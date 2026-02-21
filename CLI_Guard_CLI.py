"""
CLI Guard - Command Line Interface for scripting and automation

Non-interactive interface for retrieving, listing, and managing secrets.
Designed for use in shell scripts, CI/CD pipelines, and automation workflows.

Authentication uses tokens — no plaintext passwords on data commands:

    Interactive (human):
        export CLIGUARD_SESSION=$(python3 CLI_Guard_CLI.py signin --user admin)
        python3 CLI_Guard_CLI.py get --user admin --account prod-db
        python3 CLI_Guard_CLI.py signout

    Automation (CI/CD):
        export CLIGUARD_SERVICE_TOKEN=<your-service-token>
        DB_PASS=$(python3 CLI_Guard_CLI.py get --user admin --account prod-db)

    Create a service token:
        python3 CLI_Guard_CLI.py token create --user admin --name "ci-pipeline"
"""

import argparse
import getpass
import json
import os
import sys
from typing import Optional

import CLI_Guard
import token_manager
import validation
from logger import log


# Exit codes — scripts can check $? to determine what went wrong
EXIT_SUCCESS = 0
EXIT_ERROR = 1           # General error (bad arguments, validation failure)
EXIT_AUTH_FAILURE = 2    # Authentication failed (bad password, locked account)
EXIT_NOT_FOUND = 3       # Requested secret does not exist
EXIT_DB_ERROR = 4        # Database unreachable or missing
EXIT_TOKEN_EXPIRED = 5   # Session or service token has expired

VERSION = "0.2.0"


# ---------------------------------------------------------------------------
# Authentication helpers
# ---------------------------------------------------------------------------

def _resolve_password_for_auth() -> str:
    """
    Resolve master password for auth commands (signin, token create/list/revoke)

    Only used on commands that require the master password directly.
    Data commands (get, list, add, update, delete) use token-based auth instead.

    Priority:
        1. CLIGUARD_PASSWORD env var (for testing and non-interactive contexts)
        2. getpass.getpass() interactive prompt (if running in a terminal)
        3. stdin pipe (if not a terminal)

    Returns:
        The resolved password string

    Raises:
        SystemExit: If no password can be resolved
    """
    # Environment variable (works in any context — useful for testing and CI)
    env_password = os.environ.get("CLIGUARD_PASSWORD")
    if env_password:
        return env_password

    # Interactive prompt (most secure — password never in process list)
    if sys.stdin.isatty():
        try:
            password = getpass.getpass("Master password: ")
            if password:
                return password
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.", file=sys.stderr)
            sys.exit(EXIT_ERROR)

    # Stdin pipe (for scripting one-offs: echo "pass" | cli-guard signin ...)
    if not sys.stdin.isatty():
        password = sys.stdin.readline().strip()
        if password:
            return password

    print(
        "Error: No password provided.\n"
        "  Enter interactively, set CLIGUARD_PASSWORD env var, or pipe via stdin.",
        file=sys.stderr
    )
    sys.exit(EXIT_ERROR)


def _authenticate(user: str, password: str) -> None:
    """
    Authenticate user with password and start encryption session

    Used by auth commands (token list, token revoke) that need to verify
    the user owns the account. Data commands use _resolve_auth() instead.

    Args:
        user: Username to authenticate
        password: Master password
    """
    # Check account lockout
    if CLI_Guard.isAccountLocked(user):
        print(f"Error: Account '{user}' is locked until tomorrow.", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)

    # Validate username format
    valid, error = validation.validate_username(user)
    if not valid:
        print(f"Error: Invalid username — {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # Authenticate against stored bcrypt hash
    if not CLI_Guard.authUser(user, password):
        print(f"Error: Authentication failed for user '{user}'.", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)

    # Derive encryption key and store in memory
    CLI_Guard.startSession(user, password)


def _resolve_auth(user: str) -> None:
    """
    Authenticate via token for data commands (no password accepted)

    Checks tokens in priority order:
        1. CLIGUARD_SERVICE_TOKEN env var → long-lived service account
        2. CLIGUARD_SESSION env var       → short-lived interactive session

    On success, calls startSessionFromKey() so the encryption session is active.
    On failure, prints a helpful error message and exits.

    Args:
        user: Expected username (must match the token's user)

    Raises:
        SystemExit: If no token found, token invalid/expired/revoked, or user mismatch
    """
    # Validate username format
    valid, error = validation.validate_username(user)
    if not valid:
        print(f"Error: Invalid username — {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # 1. Service account token (automation/CI)
    service_token = os.environ.get("CLIGUARD_SERVICE_TOKEN")
    if service_token:
        try:
            token_user, encryption_key = token_manager.load_service_token(service_token)
            if token_user != user:
                print(
                    f"Error: Service token belongs to user '{token_user}', "
                    f"but --user specifies '{user}'.",
                    file=sys.stderr
                )
                sys.exit(EXIT_AUTH_FAILURE)
            CLI_Guard.startSessionFromKey(user, encryption_key)
            return
        except token_manager.TokenRevokedError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(EXIT_AUTH_FAILURE)
        except token_manager.TokenExpiredError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(EXIT_TOKEN_EXPIRED)
        except token_manager.TokenInvalidError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(EXIT_AUTH_FAILURE)

    # 2. Session token (interactive)
    session_token = os.environ.get("CLIGUARD_SESSION")
    if session_token:
        try:
            token_user, encryption_key = token_manager.load_session(session_token)
            if token_user != user:
                print(
                    f"Error: Session belongs to user '{token_user}', "
                    f"but --user specifies '{user}'.",
                    file=sys.stderr
                )
                sys.exit(EXIT_AUTH_FAILURE)
            CLI_Guard.startSessionFromKey(user, encryption_key)
            return
        except token_manager.TokenExpiredError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(EXIT_TOKEN_EXPIRED)
        except token_manager.TokenInvalidError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(EXIT_AUTH_FAILURE)

    # 3. No authentication token found
    print(
        "Error: No authentication token found.\n"
        "\n"
        "  For interactive use:\n"
        "    export CLIGUARD_SESSION=$(python3 CLI_Guard_CLI.py signin --user USER)\n"
        "\n"
        "  For automation/CI:\n"
        "    export CLIGUARD_SERVICE_TOKEN=<your-service-token>\n"
        "\n"
        "  Run 'cli-guard signin --help' or 'cli-guard token --help' for details.",
        file=sys.stderr
    )
    sys.exit(EXIT_AUTH_FAILURE)


# ---------------------------------------------------------------------------
# Auth subcommand handlers (signin, signout)
# ---------------------------------------------------------------------------

def cmd_signin(args: argparse.Namespace) -> None:
    """Create a session token and print it to stdout for capture"""
    password = _resolve_password_for_auth()

    # Validate username
    valid, error = validation.validate_username(args.user)
    if not valid:
        print(f"Error: Invalid username — {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    try:
        session_token = token_manager.create_session(
            args.user, password, ttl_minutes=args.ttl
        )
        # Token goes to stdout (for capture via $())
        print(session_token)
        # Help text goes to stderr (visible to user, not captured)
        print(
            f"Session created for '{args.user}' (expires in {args.ttl} minutes).",
            file=sys.stderr
        )
        print(f"Export it:  export CLIGUARD_SESSION={session_token}", file=sys.stderr)

    except CLI_Guard.AuthenticationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)


def cmd_signout(args: argparse.Namespace) -> None:
    """Invalidate the current session token"""
    session_token = os.environ.get("CLIGUARD_SESSION")
    if not session_token:
        print(
            "Error: No session token found (CLIGUARD_SESSION not set).\n"
            "  Nothing to sign out from.",
            file=sys.stderr
        )
        sys.exit(EXIT_ERROR)

    if token_manager.invalidate_session(session_token):
        print("Session invalidated.", file=sys.stderr)
        print("Run:  unset CLIGUARD_SESSION", file=sys.stderr)
    else:
        print(
            "Warning: Session token not found (may have already expired).",
            file=sys.stderr
        )


# ---------------------------------------------------------------------------
# Token subcommand handlers (token create, token list, token revoke)
# ---------------------------------------------------------------------------

def cmd_token_create(args: argparse.Namespace) -> None:
    """Create a new long-lived service account token"""
    password = _resolve_password_for_auth()

    # Validate username
    valid, error = validation.validate_username(args.user)
    if not valid:
        print(f"Error: Invalid username — {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    # Validate token name
    valid, error = validation.validate_token_name(args.name)
    if not valid:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    try:
        service_token = token_manager.create_service_token(
            args.user, password, args.name,
            expires_days=args.expires_days
        )
        # Token goes to stdout (for capture)
        print(service_token)
        # Info goes to stderr
        print(
            f"Service token '{args.name}' created for user '{args.user}'.",
            file=sys.stderr
        )
        if args.expires_days:
            print(f"Expires in {args.expires_days} days.", file=sys.stderr)
        else:
            print("No expiry set.", file=sys.stderr)
        print(
            "IMPORTANT: Save this token now — it cannot be retrieved later.",
            file=sys.stderr
        )

    except CLI_Guard.AuthenticationError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)


def cmd_token_list(args: argparse.Namespace) -> None:
    """List all service tokens for a user"""
    password = _resolve_password_for_auth()
    _authenticate(args.user, password)

    try:
        tokens = token_manager.list_service_tokens(args.user)

        if not tokens:
            print("No service tokens found.", file=sys.stderr)
            sys.exit(EXIT_SUCCESS)

        if args.json:
            print(json.dumps(tokens, indent=2))
        else:
            print("Token ID\tName\tCreated\tExpires\tLast Used\tRevoked")
            for t in tokens:
                print(
                    f"{t['token_id']}\t{t['name']}\t{t['created_at']}\t"
                    f"{t['expires_at'] or 'never'}\t{t['last_used'] or 'never'}\t"
                    f"{'yes' if t['revoked'] else 'no'}"
                )

    finally:
        CLI_Guard.endSession()


def cmd_token_revoke(args: argparse.Namespace) -> None:
    """Revoke a service token by its token ID"""
    password = _resolve_password_for_auth()
    _authenticate(args.user, password)

    try:
        revoked = token_manager.revoke_service_token(args.user, args.token_id)
        if revoked:
            print(
                f"Service token '{args.token_id}' has been revoked.",
                file=sys.stderr
            )
        else:
            print(
                f"Error: Token '{args.token_id}' not found.",
                file=sys.stderr
            )
            sys.exit(EXIT_NOT_FOUND)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_AUTH_FAILURE)
    finally:
        CLI_Guard.endSession()


# ---------------------------------------------------------------------------
# Data subcommand handlers (get, list, add, update, delete)
# ---------------------------------------------------------------------------

def cmd_get(args: argparse.Namespace) -> None:
    """Retrieve a single secret by account name"""
    _resolve_auth(args.user)

    try:
        secret = CLI_Guard.getSecret(
            args.user, args.account,
            username=getattr(args, "username", None)
        )

        if secret is None:
            print(f"Error: No secret found for account '{args.account}'.", file=sys.stderr)
            sys.exit(EXIT_NOT_FOUND)

        field = getattr(args, "field", "password")

        if args.json:
            if field == "all":
                print(json.dumps(secret, indent=2))
            else:
                print(json.dumps({field: secret.get(field)}))
        else:
            if field == "all":
                for key, value in secret.items():
                    print(f"{key}\t{value}")
            else:
                value = secret.get(field)
                if value is None:
                    print(f"Error: Field '{field}' not found.", file=sys.stderr)
                    sys.exit(EXIT_ERROR)
                print(value)

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    finally:
        CLI_Guard.endSession()


def cmd_list(args: argparse.Namespace) -> None:
    """List all secrets for a user (no passwords shown)"""
    _resolve_auth(args.user)

    try:
        secrets = CLI_Guard.getSecrets(args.user)

        if not secrets:
            print("No secrets found.", file=sys.stderr)
            sys.exit(EXIT_SUCCESS)

        if args.json:
            # Strip encrypted passwords from output
            safe = [{k: v for k, v in s.items() if k != "password"} for s in secrets]
            print(json.dumps(safe, indent=2))
        else:
            # Tab-separated table for easy parsing with cut/awk
            print("Category\tAccount\tUsername\tLast Modified")
            for s in secrets:
                print(f"{s['category']}\t{s['account']}\t{s['username']}\t{s['last_modified']}")

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    finally:
        CLI_Guard.endSession()


def cmd_add(args: argparse.Namespace) -> None:
    """Add a new secret entry"""
    _resolve_auth(args.user)

    try:
        # Validate all fields before touching the database
        for field_name, value, max_len in [
            ("Category", args.category, 50),
            ("Account", args.account, 100),
            ("Username", args.secret_username, 100),
            ("Secret value", args.secret, 500),
        ]:
            valid, error = validation.validate_text_field(value, field_name, max_len=max_len)
            if not valid:
                print(f"Error: {error}", file=sys.stderr)
                sys.exit(EXIT_ERROR)

        CLI_Guard.addSecret(
            args.user, args.category, args.account,
            args.secret_username, args.secret
        )
        print(f"Secret added for account '{args.account}'.", file=sys.stderr)

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    finally:
        CLI_Guard.endSession()


def cmd_update(args: argparse.Namespace) -> None:
    """Update an existing secret's password"""
    _resolve_auth(args.user)

    try:
        # Find the existing secret to get its encrypted password (needed as row identifier)
        secrets = CLI_Guard.getSecrets(args.user)
        target = None
        for s in (secrets or []):
            if s["account"] == args.account:
                if args.secret_username and s["username"] != args.secret_username:
                    continue
                target = s
                break

        if not target:
            print(f"Error: No secret found for account '{args.account}'.", file=sys.stderr)
            sys.exit(EXIT_NOT_FOUND)

        # Validate the new secret value
        valid, error = validation.validate_text_field(args.new_secret, "Secret value", max_len=500)
        if not valid:
            print(f"Error: {error}", file=sys.stderr)
            sys.exit(EXIT_ERROR)

        CLI_Guard.updateSecret(
            args.user, target["account"], target["username"],
            target["password"], args.new_secret
        )
        print(f"Secret updated for account '{args.account}'.", file=sys.stderr)

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    finally:
        CLI_Guard.endSession()


def cmd_delete(args: argparse.Namespace) -> None:
    """Delete a secret entry"""
    _resolve_auth(args.user)

    try:
        # Find the secret to get its encrypted password (needed for exact row deletion)
        secrets = CLI_Guard.getSecrets(args.user)
        target = None
        for s in (secrets or []):
            if s["account"] == args.account:
                if args.secret_username and s["username"] != args.secret_username:
                    continue
                target = s
                break

        if not target:
            print(f"Error: No secret found for account '{args.account}'.", file=sys.stderr)
            sys.exit(EXIT_NOT_FOUND)

        if not args.force:
            print(
                f"Error: Use --force to confirm deletion of secret for '{args.account}'.",
                file=sys.stderr
            )
            sys.exit(EXIT_ERROR)

        CLI_Guard.deleteSecret(
            args.user, target["account"],
            target["username"], target["password"]
        )
        print(f"Secret deleted for account '{args.account}'.", file=sys.stderr)

    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(EXIT_ERROR)
    finally:
        CLI_Guard.endSession()


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands"""
    parser = argparse.ArgumentParser(
        prog="cli-guard",
        description="CLI Guard — Locally-hosted secret manager for scripting and automation",
        epilog=(
            "Auth: Use 'signin' for interactive sessions, "
            "'token create' for automation. See each command's --help."
        )
    )
    parser.add_argument("--version", action="version", version=f"CLI Guard {VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- signin ---
    signin_p = subparsers.add_parser(
        "signin",
        help="Create a session token (interactive auth)"
    )
    signin_p.add_argument("--user", required=True, help="CLI Guard username")
    signin_p.add_argument(
        "--ttl", type=int, default=60,
        help="Session lifetime in minutes (default: 60)"
    )
    signin_p.set_defaults(func=cmd_signin)

    # --- signout ---
    signout_p = subparsers.add_parser(
        "signout",
        help="Invalidate the current session token"
    )
    signout_p.set_defaults(func=cmd_signout)

    # --- token (with subcommands: create, list, revoke) ---
    token_p = subparsers.add_parser(
        "token",
        help="Manage service account tokens"
    )
    token_sub = token_p.add_subparsers(dest="token_command", help="Token commands")

    # token create
    tc_p = token_sub.add_parser("create", help="Create a new service token")
    tc_p.add_argument("--user", required=True, help="CLI Guard username")
    tc_p.add_argument("--name", required=True, help="Human label for this token (e.g. 'ci-pipeline')")
    tc_p.add_argument(
        "--expires-days", type=int, default=None,
        help="Token expiry in days from now (default: never expires)"
    )
    tc_p.set_defaults(func=cmd_token_create)

    # token list
    tl_p = token_sub.add_parser("list", help="List service tokens for a user")
    tl_p.add_argument("--user", required=True, help="CLI Guard username")
    tl_p.add_argument("--json", action="store_true", help="Output as JSON")
    tl_p.set_defaults(func=cmd_token_list)

    # token revoke
    tr_p = token_sub.add_parser("revoke", help="Revoke a service token")
    tr_p.add_argument("--user", required=True, help="CLI Guard username")
    tr_p.add_argument(
        "--token-id", required=True,
        help="Token ID to revoke (e.g. cg_svc_a3f8c1b2d4e6)"
    )
    tr_p.set_defaults(func=cmd_token_revoke)

    # --- get ---
    get_p = subparsers.add_parser("get", help="Retrieve a secret by account name")
    get_p.add_argument("--user", required=True, help="CLI Guard username")
    get_p.add_argument("--account", required=True, help="Account name to retrieve")
    get_p.add_argument("--username", default=None,
                       help="Username to disambiguate if multiple secrets share an account")
    get_p.add_argument("--field", default="password",
                       choices=["password", "username", "category", "last_modified", "all"],
                       help="Which field to return (default: password)")
    get_p.add_argument("--json", action="store_true", help="Output as JSON")
    get_p.set_defaults(func=cmd_get)

    # --- list ---
    list_p = subparsers.add_parser("list", help="List all secrets for a user")
    list_p.add_argument("--user", required=True, help="CLI Guard username")
    list_p.add_argument("--json", action="store_true", help="Output as JSON")
    list_p.set_defaults(func=cmd_list)

    # --- add ---
    add_p = subparsers.add_parser("add", help="Add a new secret")
    add_p.add_argument("--user", required=True, help="CLI Guard username")
    add_p.add_argument("--category", required=True, help="Secret category")
    add_p.add_argument("--account", required=True, help="Account name")
    add_p.add_argument("--secret-username", required=True, help="Username for the secret")
    add_p.add_argument("--secret", required=True, help="Secret value (password/API key/token)")
    add_p.set_defaults(func=cmd_add)

    # --- update ---
    upd_p = subparsers.add_parser("update", help="Update an existing secret")
    upd_p.add_argument("--user", required=True, help="CLI Guard username")
    upd_p.add_argument("--account", required=True, help="Account to update")
    upd_p.add_argument("--secret-username", default=None, help="Username to disambiguate")
    upd_p.add_argument("--new-secret", required=True, help="New secret value")
    upd_p.set_defaults(func=cmd_update)

    # --- delete ---
    del_p = subparsers.add_parser("delete", help="Delete a secret")
    del_p.add_argument("--user", required=True, help="CLI Guard username")
    del_p.add_argument("--account", required=True, help="Account to delete")
    del_p.add_argument("--secret-username", default=None, help="Username to disambiguate")
    del_p.add_argument("--force", action="store_true",
                       help="Skip confirmation (required for scripting)")
    del_p.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    """Main entry point for CLI Guard CLI"""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help(sys.stderr)
        sys.exit(EXIT_ERROR)

    # Handle subcommand groups with no action (e.g. 'cli-guard token' with no subcommand)
    if not hasattr(args, 'func'):
        print(f"Error: '{args.command}' requires a subcommand. Use --help for details.", file=sys.stderr)
        sys.exit(EXIT_ERROR)

    log("CLI", f"Command: {args.command}")
    args.func(args)


if __name__ == "__main__":
    main()
