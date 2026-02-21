"""
Token management for CLI Guard authentication

Handles two authentication models:
1. Session tokens (interactive, short-lived) — human signs in once, gets a 1-hour token
2. Service account tokens (automation, long-lived) — created once, used by scripts

Uses key wrapping to persist encryption keys without storing them in plaintext.
The encryption key is encrypted ("wrapped") with a key derived from the token itself.
Neither the token alone nor the wrapped blob alone is useful — you need both.

Usage:
    from token_manager import create_session, load_session, invalidate_session
    from token_manager import create_service_token, load_service_token

    # Interactive session
    token = create_session("admin", "master_password", ttl_minutes=60)
    user, key = load_session(token)

    # Service account
    token = create_service_token("admin", "master_password", "ci-pipeline")
    user, key = load_service_token(token)
"""

import base64
import hashlib
import json
import os
import secrets
import stat
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from cryptography.fernet import Fernet, InvalidToken

import CLI_Guard
import CLI_SQL.CLI_Guard_SQL as sqlite
from logger import log

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Session files live in ~/.cli-guard/sessions/
SESSION_DIR = os.path.join(os.path.expanduser("~"), ".cli-guard", "sessions")

# Wrapping salt — distinct from the main PBKDF2 salt in CLI_Guard.py
# This ensures the wrapping key is independent of the encryption key
WRAPPING_SALT = b'CLI_Guard_Wrap_v1_2026'
WRAPPING_ITERATIONS = 100_000

# Default session lifetime
DEFAULT_SESSION_TTL_MINUTES = 60

# Token prefixes for identification
SESSION_PREFIX = "cg_ses_"
SERVICE_PREFIX = "cg_svc_"


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class TokenError(Exception):
    """Base exception for token operations"""


class TokenExpiredError(TokenError):
    """Raised when a session or service token has expired"""


class TokenInvalidError(TokenError):
    """Raised when a token is invalid, not found, or doesn't match"""


class TokenRevokedError(TokenError):
    """Raised when a revoked service token is used"""


# ---------------------------------------------------------------------------
# Internal utilities — key wrapping
# ---------------------------------------------------------------------------

def _derive_wrapping_key(token: str) -> bytes:
    """
    Derive a Fernet-compatible wrapping key from a token string using PBKDF2

    This wrapping key is used to encrypt/decrypt the real encryption key.
    It uses a different salt than the main key derivation in CLI_Guard.py
    to ensure the wrapping key is cryptographically independent.

    Args:
        token: The raw token string

    Returns:
        44-byte base64-encoded key suitable for Fernet
    """
    kdf = hashlib.pbkdf2_hmac(
        'sha256',
        token.encode('utf-8'),
        WRAPPING_SALT,
        WRAPPING_ITERATIONS,
        dklen=32
    )
    return base64.urlsafe_b64encode(kdf)


def _wrap_key(encryption_key: bytes, token: str) -> str:
    """
    Encrypt the real encryption key using a key derived from the token

    Args:
        encryption_key: The Fernet encryption key to wrap (44 bytes, base64)
        token: The raw token string used to derive the wrapping key

    Returns:
        Fernet ciphertext string (the wrapped blob)
    """
    wrapping_key = _derive_wrapping_key(token)
    fernet = Fernet(wrapping_key)
    wrapped = fernet.encrypt(encryption_key)
    return wrapped.decode('utf-8')


def _unwrap_key(wrapped_blob: str, token: str) -> bytes:
    """
    Decrypt the real encryption key using the token

    Args:
        wrapped_blob: Fernet ciphertext from _wrap_key()
        token: The raw token string

    Returns:
        The original encryption key (44 bytes, base64)

    Raises:
        TokenInvalidError: If the token doesn't match (wrong wrapping key)
    """
    wrapping_key = _derive_wrapping_key(token)
    fernet = Fernet(wrapping_key)
    try:
        return fernet.decrypt(wrapped_blob.encode('utf-8'))
    except InvalidToken:
        raise TokenInvalidError("Token does not match — cannot unwrap encryption key")


def _ensure_session_dir() -> None:
    """Create ~/.cli-guard/sessions/ with restricted permissions if needed"""
    cli_guard_dir = os.path.dirname(SESSION_DIR)

    if not os.path.exists(cli_guard_dir):
        os.makedirs(cli_guard_dir, mode=0o700)

    if not os.path.exists(SESSION_DIR):
        os.makedirs(SESSION_DIR, mode=0o700)


def _get_service_token_id(token: str) -> str:
    """
    Derive the token_id (DB lookup key) from a full service token

    Takes the first 12 chars of the SHA-256 hash of the full token,
    prefixed with 'cg_svc_'. This is NOT a security credential — it's
    a fast lookup key. The bcrypt hash in the DB provides the actual
    cryptographic verification.

    Args:
        token: The full service token string

    Returns:
        Token ID string like 'cg_svc_a3f8c1b2d4e6'
    """
    raw = token.removeprefix(SERVICE_PREFIX)
    hash_hex = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    return SERVICE_PREFIX + hash_hex[:12]


# ---------------------------------------------------------------------------
# Session tokens (interactive, short-lived)
# ---------------------------------------------------------------------------

def create_session(user: str, password: str,
                   ttl_minutes: int = DEFAULT_SESSION_TTL_MINUTES) -> str:
    """
    Create a new session token after password authentication

    Authenticates the user, derives the encryption key, generates a random
    token, wraps the key with the token, and stores the wrapped blob in a
    session file at ~/.cli-guard/sessions/{user}.json.

    Args:
        user: Username to authenticate
        password: Master password
        ttl_minutes: Session lifetime in minutes (default 60)

    Returns:
        Session token string (prefixed with cg_ses_)

    Raises:
        ValueError: If account is locked
        CLI_Guard.AuthenticationError: If password verification fails
    """
    # Check lockout
    if CLI_Guard.isAccountLocked(user):
        raise ValueError(f"Account '{user}' is locked until tomorrow")

    # Verify password
    if not CLI_Guard.authUser(user, password):
        raise CLI_Guard.AuthenticationError(f"Authentication failed for user '{user}'")

    # Derive the real encryption key
    encryption_key = CLI_Guard.deriveEncryptionKey(password)

    # Generate random token
    raw_token = secrets.token_urlsafe(32)
    token = SESSION_PREFIX + raw_token

    # Wrap the encryption key
    wrapped = _wrap_key(encryption_key, token)

    # Build session data
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    now = datetime.now().isoformat(timespec='seconds')
    session_data = {
        "user": user,
        "wrapped_key": wrapped,
        "token_hash": token_hash,
        "created_at": now,
        "ttl_minutes": ttl_minutes,
    }

    # Write session file
    _ensure_session_dir()
    session_path = os.path.join(SESSION_DIR, f"{user}.json")
    with open(session_path, 'w') as f:
        json.dump(session_data, f, indent=2)
    os.chmod(session_path, stat.S_IRUSR | stat.S_IWUSR)  # 0o600

    # Clean up expired sessions from other users while we're here
    cleanup_expired_sessions()

    log("AUTH", f"Session token created for user '{user}' (TTL: {ttl_minutes}min)")
    return token


def load_session(token: str) -> tuple[str, bytes]:
    """
    Load and validate a session token, returning (user, encryption_key)

    Finds the session file, checks the token hash matches, verifies the
    session hasn't expired, then unwraps the encryption key.

    Args:
        token: Session token string (cg_ses_...)

    Returns:
        Tuple of (username, encryption_key)

    Raises:
        TokenInvalidError: If token doesn't match any session
        TokenExpiredError: If session has exceeded TTL
    """
    if not token.startswith(SESSION_PREFIX):
        raise TokenInvalidError("Not a valid session token (expected cg_ses_ prefix)")

    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()

    # Search session files for a matching token hash
    if not os.path.exists(SESSION_DIR):
        raise TokenInvalidError("No active sessions found")

    for filename in os.listdir(SESSION_DIR):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(SESSION_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        if session_data.get("token_hash") != token_hash:
            continue

        # Found matching session — check expiry
        created_at = datetime.fromisoformat(session_data["created_at"])
        ttl = session_data.get("ttl_minutes", DEFAULT_SESSION_TTL_MINUTES)
        expires_at = created_at + timedelta(minutes=ttl)

        if datetime.now() > expires_at:
            # Expired — delete the file
            os.remove(filepath)
            log("AUTH", f"Session expired for user '{session_data['user']}'")
            raise TokenExpiredError(
                f"Session expired (created {session_data['created_at']}, TTL {ttl}min). "
                f"Run 'cli-guard signin' to create a new session."
            )

        # Valid — unwrap the encryption key
        user = session_data["user"]
        encryption_key = _unwrap_key(session_data["wrapped_key"], token)

        log("AUTH", f"Session token validated for user '{user}'")
        return user, encryption_key

    raise TokenInvalidError("Session token not recognized — it may have expired or been invalidated")


def invalidate_session(token: str) -> bool:
    """
    Delete the session file for this token (signout)

    Args:
        token: Session token string

    Returns:
        True if session was found and deleted, False otherwise
    """
    if not token.startswith(SESSION_PREFIX):
        return False

    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()

    if not os.path.exists(SESSION_DIR):
        return False

    for filename in os.listdir(SESSION_DIR):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(SESSION_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)
            if session_data.get("token_hash") == token_hash:
                os.remove(filepath)
                log("AUTH", f"Session invalidated for user '{session_data.get('user')}'")
                return True
        except (json.JSONDecodeError, OSError):
            continue

    return False


def cleanup_expired_sessions() -> int:
    """
    Remove expired session files from ~/.cli-guard/sessions/

    Returns:
        Number of expired session files removed
    """
    if not os.path.exists(SESSION_DIR):
        return 0

    removed = 0
    for filename in os.listdir(SESSION_DIR):
        if not filename.endswith('.json'):
            continue

        filepath = os.path.join(SESSION_DIR, filename)
        try:
            with open(filepath, 'r') as f:
                session_data = json.load(f)

            created_at = datetime.fromisoformat(session_data["created_at"])
            ttl = session_data.get("ttl_minutes", DEFAULT_SESSION_TTL_MINUTES)
            expires_at = created_at + timedelta(minutes=ttl)

            if datetime.now() > expires_at:
                os.remove(filepath)
                removed += 1
        except (json.JSONDecodeError, OSError, KeyError, ValueError):
            continue

    if removed > 0:
        log("AUTH", f"Cleaned up {removed} expired session(s)")
    return removed


# ---------------------------------------------------------------------------
# Service account tokens (automation, long-lived)
# ---------------------------------------------------------------------------

def create_service_token(user: str, password: str, name: str,
                         expires_days: Optional[int] = None) -> str:
    """
    Create a long-lived service account token

    Authenticates the user, derives the encryption key, generates a random
    token, wraps the key with the token, bcrypt-hashes the token, and stores
    the metadata in the service_tokens database table.

    The full token is returned ONCE and never stored. Only its bcrypt hash
    and the wrapped encryption key are persisted.

    Args:
        user: Username this token acts as
        password: Master password (needed to derive encryption key)
        name: Human label for this token (e.g. "ci-pipeline")
        expires_days: Optional expiry in days from now (None = never expires)

    Returns:
        Service token string (prefixed with cg_svc_)

    Raises:
        ValueError: If account is locked
        CLI_Guard.AuthenticationError: If password verification fails
    """
    # Check lockout
    if CLI_Guard.isAccountLocked(user):
        raise ValueError(f"Account '{user}' is locked until tomorrow")

    # Verify password
    if not CLI_Guard.authUser(user, password):
        raise CLI_Guard.AuthenticationError(f"Authentication failed for user '{user}'")

    # Derive the real encryption key
    encryption_key = CLI_Guard.deriveEncryptionKey(password)

    # Generate random token
    raw_token = secrets.token_urlsafe(32)
    token = SERVICE_PREFIX + raw_token

    # Derive the token_id (DB lookup key)
    token_id = _get_service_token_id(token)

    # Bcrypt-hash the token for storage (never store the raw token)
    token_hash = bcrypt.hashpw(token.encode('utf-8'), bcrypt.gensalt())

    # Wrap the encryption key with the token
    wrapped = _wrap_key(encryption_key, token)

    # Calculate expiry
    now = datetime.now().isoformat(timespec='seconds')
    expires_at = None
    if expires_days is not None:
        expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat(timespec='seconds')

    # Store in database
    sqlite.insertServiceToken(
        token_id=token_id,
        user=user,
        name=name,
        token_hash=token_hash,
        wrapped_key=wrapped,
        created_at=now,
        expires_at=expires_at,
    )

    log("AUTH", f"Service token '{name}' created for user '{user}' (id: {token_id})")
    return token


def load_service_token(token: str) -> tuple[str, bytes]:
    """
    Validate a service token and return (user, encryption_key)

    Derives the token_id for DB lookup, verifies the bcrypt hash matches,
    checks the token isn't revoked or expired, then unwraps the encryption key.

    Args:
        token: Service token string (cg_svc_...)

    Returns:
        Tuple of (username, encryption_key)

    Raises:
        TokenInvalidError: If token not found or hash doesn't match
        TokenRevokedError: If token has been revoked
        TokenExpiredError: If token has expired
    """
    if not token.startswith(SERVICE_PREFIX):
        raise TokenInvalidError("Not a valid service token (expected cg_svc_ prefix)")

    # Look up token in database
    token_id = _get_service_token_id(token)
    row = sqlite.queryServiceToken(token_id)

    if row is None:
        raise TokenInvalidError("Service token not recognized")

    # Unpack row: (token_id, user, name, token_hash, wrapped_key, created_at, expires_at, last_used, revoked)
    _, user, name, stored_hash, wrapped_key, created_at, expires_at, _, revoked = row

    # Check revocation
    if revoked:
        log("AUTH", f"Rejected revoked service token '{name}' for user '{user}'")
        raise TokenRevokedError(f"Service token '{name}' has been revoked")

    # Check expiry
    if expires_at is not None:
        if datetime.now() > datetime.fromisoformat(expires_at):
            log("AUTH", f"Rejected expired service token '{name}' for user '{user}'")
            raise TokenExpiredError(
                f"Service token '{name}' expired on {expires_at}. "
                f"Create a new token with 'cli-guard token create'."
            )

    # Verify bcrypt hash
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')
    if not bcrypt.checkpw(token.encode('utf-8'), stored_hash):
        raise TokenInvalidError("Service token hash mismatch")

    # Unwrap the encryption key
    encryption_key = _unwrap_key(wrapped_key, token)

    # Update last_used timestamp
    sqlite.updateServiceTokenLastUsed(token_id, datetime.now().isoformat(timespec='seconds'))

    log("AUTH", f"Service token '{name}' validated for user '{user}'")
    return user, encryption_key


def list_service_tokens(user: str) -> list[dict]:
    """
    List all service tokens for a user (no sensitive data exposed)

    Args:
        user: Username to list tokens for

    Returns:
        List of dicts with keys: token_id, name, created_at, expires_at, last_used, revoked
    """
    rows = sqlite.queryServiceTokensByUser(user)
    results = []
    for row in rows:
        # (token_id, user, name, token_hash, wrapped_key, created_at, expires_at, last_used, revoked)
        results.append({
            "token_id": row[0],
            "name": row[2],
            "created_at": row[5],
            "expires_at": row[6],
            "last_used": row[7],
            "revoked": bool(row[8]),
        })
    return results


def revoke_service_token(user: str, token_id: str) -> bool:
    """
    Revoke a service token by its token_id

    Args:
        user: Username who owns the token (for authorization check)
        token_id: Token ID to revoke (e.g. 'cg_svc_a3f8c1b2d4e6')

    Returns:
        True if token was found and revoked, False if not found

    Raises:
        ValueError: If token doesn't belong to the specified user
    """
    row = sqlite.queryServiceToken(token_id)
    if row is None:
        return False

    # Verify the token belongs to this user
    token_user = row[1]
    if token_user != user:
        raise ValueError(f"Token '{token_id}' does not belong to user '{user}'")

    sqlite.revokeServiceToken(token_id)
    log("AUTH", f"Service token '{row[2]}' (id: {token_id}) revoked by user '{user}'")
    return True
