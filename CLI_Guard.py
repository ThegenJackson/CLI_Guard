# CLI Guard SQL
import CLI_SQL.CLI_Guard_SQL as sqlite

import bcrypt
from cryptography.fernet import Fernet
import base64
import hashlib
from typing import Optional

from logger import log


# Session management - stores the current user's encryption key and username
_session_encryption_key: Optional[bytes] = None
_session_user: Optional[str] = None


def getUsers() -> list[list[str]]:
    """
    Retrieve list of all users from database

    Returns:
        List of lists, each containing [username]
    """
    # Create empty list to insert data into
    users_list: list[list[str]] = []

    # Query Users table
    data: list[tuple] = sqlite.queryData(user=None, table="users")

    if not data:
        return users_list

    # Loop through query data and insert relevant data to users_list
    for user_record in data:
        users_list.append([user_record[0]])  # Just the username

    return users_list


def hashPassword(password: str) -> bytes:
    """
    Hash a password using bcrypt for storage

    Args:
        password: Plaintext password to hash

    Returns:
        Bcrypt hashed password as bytes
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def deriveEncryptionKey(password: str) -> bytes:
    """
    Derive a Fernet encryption key from a password using PBKDF2

    This function derives the same key from the same password every time,
    allowing passwords to be encrypted/decrypted across different sessions
    without storing the encryption key.

    Args:
        password: Plaintext password to derive key from

    Returns:
        32-byte Fernet-compatible encryption key (base64 encoded)
    """
    # Fixed salt for consistent key derivation
    # NOTE: This could be made per-user for additional security
    salt = b'CLI_Guard_Salt_v1_2025'

    # Use PBKDF2 to derive 32 bytes from the password
    # 100,000 iterations for good security without being too slow
    kdf = hashlib.pbkdf2_hmac(
        'sha256',           # Hash algorithm
        password.encode('utf-8'),  # Password as bytes
        salt,               # Salt
        100000,             # Iterations
        dklen=32            # Desired key length in bytes
    )

    # Encode to base64 for Fernet compatibility
    return base64.urlsafe_b64encode(kdf)


def authUser(user: str, attempted_password: str) -> bool:
    """
    Authenticate a user by checking their password against stored bcrypt hash

    Args:
        user: Username to authenticate
        attempted_password: Plaintext password attempt

    Returns:
        True if authentication successful, False otherwise
    """
    # Query Users table for user data
    user_data: list[tuple] = sqlite.queryData(user=user, table="users")

    if not user_data or len(user_data) == 0:
        log("AUTH", f"Authentication failed for '{user}' - user not found")
        return False

    # Get the stored password hash
    # Assuming structure: (username, password_hash, ...)
    stored_hash = user_data[0][1]

    # Handle if stored_hash is string (convert to bytes)
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')

    # Verify the password using bcrypt
    try:
        result = bcrypt.checkpw(attempted_password.encode('utf-8'), stored_hash)
        if result:
            log("AUTH", f"Authentication successful for '{user}'")
        else:
            log("AUTH", f"Authentication failed for '{user}' - incorrect password")
        return result
    except Exception:
        log("AUTH", f"Authentication error for '{user}'", exc_info=True)
        return False


def startSession(user: str, password: str) -> None:
    """
    Initialize a session by deriving and storing the encryption key

    This function should be called after successful authentication.
    It derives the encryption key from the user's password and stores
    it in memory for the duration of the session.

    Args:
        user: Username for the session
        password: Plaintext password (used to derive encryption key)
    """
    global _session_encryption_key, _session_user

    _session_user = user
    _session_encryption_key = deriveEncryptionKey(password)
    log("AUTH", f"Session started for '{user}'")


def endSession() -> None:
    """
    Clear the session by removing stored encryption key and user

    This should be called when the user signs out to ensure
    sensitive data is removed from memory.
    """
    global _session_encryption_key, _session_user

    log("AUTH", f"Session ended for '{_session_user}'")
    _session_encryption_key = None
    _session_user = None


def getSessionEncryptionKey() -> Optional[bytes]:
    """
    Get the current session's encryption key

    Returns:
        Encryption key as bytes, or None if no active session
    """
    return _session_encryption_key


def getSessionUser() -> Optional[str]:
    """
    Get the current session's username

    Returns:
        Username as string, or None if no active session
    """
    return _session_user


def encryptPassword(password: str) -> str:
    """
    Encrypt a password using the session's encryption key

    Args:
        password: Plaintext password to encrypt

    Returns:
        Encrypted password as string

    Raises:
        RuntimeError: If no active session exists
    """
    if _session_encryption_key is None:
        log("ERROR", "Encryption attempted with no active session")
        raise RuntimeError("No active session - cannot encrypt password")

    fernet = Fernet(_session_encryption_key)
    encrypted = fernet.encrypt(password.encode('utf-8'))
    log("AUTH", "Password encrypted successfully")
    return encrypted.decode('utf-8')


def decryptPassword(encrypted_password: str) -> str:
    """
    Decrypt a password using the session's encryption key

    Args:
        encrypted_password: Encrypted password as string

    Returns:
        Decrypted plaintext password

    Raises:
        RuntimeError: If no active session exists
    """
    if _session_encryption_key is None:
        log("ERROR", "Decryption attempted with no active session")
        raise RuntimeError("No active session - cannot decrypt password")

    fernet = Fernet(_session_encryption_key)
    decrypted = fernet.decrypt(encrypted_password.encode('utf-8'))
    log("AUTH", "Password decrypted successfully")
    return decrypted.decode('utf-8')


# ---------------------------------------------------------------------------
# Convenience functions for CLI / scripting interface
# These wrap SQL + encryption calls so interface layers never import SQL directly
# ---------------------------------------------------------------------------

def isAccountLocked(user: str) -> bool:
    """
    Check if a user account is currently locked out

    Args:
        user: Username to check

    Returns:
        True if account is locked, False otherwise
    """
    return sqlite.isUserLocked(user)


def getSecrets(user: str, category: str = None, text: str = None,
               sort_by: str = None, sort_column: str = None) -> list[dict]:
    """
    Query all secrets for a user, returning structured dicts

    Passwords are left encrypted in the returned dicts. Call decryptPassword()
    on individual values when you need plaintext.

    Args:
        user: Username to query secrets for
        category: Column to filter on (must be in ALLOWED_COLUMNS)
        text: Search text for LIKE filtering
        sort_by: Sort order ('ascending' or 'descending')
        sort_column: Column to sort by (must be in ALLOWED_COLUMNS, defaults to category if None)

    Returns:
        List of dicts with keys: category, account, username, password (encrypted), last_modified

    Raises:
        RuntimeError: If no active session
    """
    if _session_encryption_key is None:
        raise RuntimeError("No active session - cannot query secrets")

    data = sqlite.queryData(user=user, table="passwords", category=category,
                            text=text, sort_by=sort_by, sort_column=sort_column)
    results = []
    for row in (data or []):
        # row tuple: (user, category, account, username, encrypted_password, last_modified)
        results.append({
            "category": row[1],
            "account": row[2],
            "username": row[3],
            "password": row[4],
            "last_modified": str(row[5]),
        })
    return results


def getSecret(user: str, account: str, username: str = None) -> Optional[dict]:
    """
    Get a specific secret by account name, with password decrypted

    Uses queryData with LIKE search, then filters for an exact account match.
    If multiple secrets share an account name, pass username to disambiguate.

    Args:
        user: Username who owns the secrets
        account: Account name to look up
        username: Optional username to disambiguate multiple matches

    Returns:
        Dict with keys: category, account, username, password (decrypted), last_modified
        None if no matching secret found

    Raises:
        RuntimeError: If no active session
    """
    if _session_encryption_key is None:
        raise RuntimeError("No active session - cannot retrieve secret")

    # queryData uses LIKE with %text%, so we post-filter for exact match
    data = sqlite.queryData(user=user, table="passwords",
                            category="account", text=account)
    if not data:
        return None

    # Filter for exact account match
    matches = [row for row in data if row[2] == account]
    if not matches:
        return None

    # Narrow by username if provided
    if username:
        matches = [row for row in matches if row[3] == username]
        if not matches:
            return None

    row = matches[0]
    try:
        decrypted = decryptPassword(row[4])
    except Exception:
        decrypted = None

    return {
        "category": row[1],
        "account": row[2],
        "username": row[3],
        "password": decrypted,
        "last_modified": str(row[5]),
    }


def addSecret(user: str, category: str, account: str,
              username: str, password: str) -> bool:
    """
    Encrypt a password and store it as a new secret entry

    Args:
        user: Username who owns this secret
        category: Category for the secret
        account: Account name
        username: Username for the account
        password: Plaintext password to encrypt and store

    Returns:
        True if successful

    Raises:
        RuntimeError: If no active session
    """
    if _session_encryption_key is None:
        raise RuntimeError("No active session - cannot add secret")

    encrypted = encryptPassword(password)
    sqlite.insertData(user, category, account, username, encrypted)
    log("AUTH", f"Secret added for account '{account}' by user '{user}'")
    return True


def updateSecret(user: str, account: str, username: str,
                 old_encrypted_password: str, new_password: str) -> bool:
    """
    Encrypt a new password and update an existing secret entry

    Args:
        user: Username who owns this secret
        account: Account name
        username: Username for the account
        old_encrypted_password: Current encrypted password (identifies the row)
        new_password: New plaintext password to encrypt and store

    Returns:
        True if successful

    Raises:
        RuntimeError: If no active session
    """
    if _session_encryption_key is None:
        raise RuntimeError("No active session - cannot update secret")

    new_encrypted = encryptPassword(new_password)
    sqlite.updateData(user, new_encrypted, account, username, old_encrypted_password)
    log("AUTH", f"Secret updated for account '{account}' by user '{user}'")
    return True


def deleteSecret(user: str, account: str, username: str,
                 encrypted_password: str) -> bool:
    """
    Delete a specific secret entry

    Args:
        user: Username who owns this secret
        account: Account name
        username: Username for the account
        encrypted_password: The encrypted password value (identifies the exact row)

    Returns:
        True if successful

    Raises:
        RuntimeError: If no active session
    """
    if _session_encryption_key is None:
        raise RuntimeError("No active session - cannot delete secret")

    sqlite.deleteData(user, account, username, encrypted_password)
    log("AUTH", f"Secret deleted for account '{account}' by user '{user}'")
    return True
