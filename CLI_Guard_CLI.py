"""
CLI Guard - Command Line Interface for scripting and automation

Non-interactive interface for retrieving, listing, and managing secrets.
Designed for use in shell scripts, CI/CD pipelines, and automation workflows.

Usage:
    python3 CLI_Guard_CLI.py get --user admin --account prod-db
    python3 CLI_Guard_CLI.py list --user admin --json
    DB_PASS=$(python3 CLI_Guard_CLI.py get --user admin --account prod-db)

Authentication (3 methods, checked in this order):
    --password FLAG         Explicit flag (visible in ps/history — use for testing only)
    CLIGUARD_PASSWORD       Environment variable (recommended for CI/CD)
    stdin pipe              echo "pass" | python3 CLI_Guard_CLI.py get ...
"""

import argparse
import json
import os
import sys
from typing import Optional

import CLI_Guard
import validation
from logger import log


# Exit codes — scripts can check $? to determine what went wrong
EXIT_SUCCESS = 0
EXIT_ERROR = 1           # General error (bad arguments, validation failure)
EXIT_AUTH_FAILURE = 2    # Authentication failed (bad password, locked account)
EXIT_NOT_FOUND = 3       # Requested secret does not exist
EXIT_DB_ERROR = 4        # Database unreachable or missing

VERSION = "0.1.0"


def _resolve_password(args_password: Optional[str]) -> Optional[str]:
    """
    Resolve the master password from flag, environment variable, or stdin

    Priority:
        1. --password flag (explicitly provided by user)
        2. CLIGUARD_PASSWORD environment variable (recommended for CI/CD)
        3. stdin (if piped, not a TTY — for one-off scripting)

    Args:
        args_password: Value from --password argument, or None

    Returns:
        The resolved password string, or None if not available
    """
    if args_password:
        return args_password

    env_password = os.environ.get("CLIGUARD_PASSWORD")
    if env_password:
        return env_password

    if not sys.stdin.isatty():
        password = sys.stdin.readline().strip()
        if password:
            return password

    return None


def _authenticate(user: str, password: str) -> None:
    """
    Authenticate user and start session

    Checks account lockout, validates username, verifies password,
    then starts the encryption session. Exits with appropriate code on failure.

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


def _require_password(args_password: Optional[str]) -> str:
    """
    Resolve password or exit with an error message

    Args:
        args_password: Value from --password argument, or None

    Returns:
        The resolved password string
    """
    password = _resolve_password(args_password)
    if not password:
        print(
            "Error: No password provided.\n"
            "  Use --password FLAG, set CLIGUARD_PASSWORD env var, or pipe via stdin.",
            file=sys.stderr
        )
        sys.exit(EXIT_ERROR)
    return password


# ---------------------------------------------------------------------------
# Subcommand handlers
# ---------------------------------------------------------------------------

def cmd_get(args: argparse.Namespace) -> None:
    """Retrieve a single secret by account name"""
    password = _require_password(args.password)
    _authenticate(args.user, password)

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
    password = _require_password(args.password)
    _authenticate(args.user, password)

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
    password = _require_password(args.password)
    _authenticate(args.user, password)

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
    password = _require_password(args.password)
    _authenticate(args.user, password)

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
    password = _require_password(args.password)
    _authenticate(args.user, password)

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
        epilog="Auth: Use --password, CLIGUARD_PASSWORD env var, or pipe via stdin."
    )
    parser.add_argument("--version", action="version", version=f"CLI Guard {VERSION}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- get ---
    get_p = subparsers.add_parser("get", help="Retrieve a secret by account name")
    get_p.add_argument("--user", required=True, help="CLI Guard username")
    get_p.add_argument("--password", default=None, help="Master password")
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
    list_p.add_argument("--password", default=None, help="Master password")
    list_p.add_argument("--json", action="store_true", help="Output as JSON")
    list_p.set_defaults(func=cmd_list)

    # --- add ---
    add_p = subparsers.add_parser("add", help="Add a new secret")
    add_p.add_argument("--user", required=True, help="CLI Guard username")
    add_p.add_argument("--password", default=None, help="Master password")
    add_p.add_argument("--category", required=True, help="Secret category")
    add_p.add_argument("--account", required=True, help="Account name")
    add_p.add_argument("--secret-username", required=True, help="Username for the secret")
    add_p.add_argument("--secret", required=True, help="Secret value (password/API key/token)")
    add_p.set_defaults(func=cmd_add)

    # --- update ---
    upd_p = subparsers.add_parser("update", help="Update an existing secret")
    upd_p.add_argument("--user", required=True, help="CLI Guard username")
    upd_p.add_argument("--password", default=None, help="Master password")
    upd_p.add_argument("--account", required=True, help="Account to update")
    upd_p.add_argument("--secret-username", default=None, help="Username to disambiguate")
    upd_p.add_argument("--new-secret", required=True, help="New secret value")
    upd_p.set_defaults(func=cmd_update)

    # --- delete ---
    del_p = subparsers.add_parser("delete", help="Delete a secret")
    del_p.add_argument("--user", required=True, help="CLI Guard username")
    del_p.add_argument("--password", default=None, help="Master password")
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

    log("CLI", f"Command: {args.command}")
    args.func(args)


if __name__ == "__main__":
    main()
