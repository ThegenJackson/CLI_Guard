"""
Unit tests for CLI Guard CLI (argument parser, auth resolution, exit codes)

These tests verify the non-interactive CLI interface works correctly
without touching the database or encryption layer.
"""

import unittest
import sys
import os
from unittest.mock import patch
from io import StringIO

# Add parent directory to path so we can import CLI_Guard_CLI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import CLI_Guard_CLI


class TestBuildParser(unittest.TestCase):
    """Test that the argument parser accepts valid commands and rejects invalid ones"""

    def setUp(self):
        """Build a fresh parser for each test"""
        self.parser = CLI_Guard_CLI.build_parser()

    # --- get subcommand ---

    def test_get_requires_user_and_account(self):
        """get subcommand requires --user and --account"""
        args = self.parser.parse_args(["get", "--user", "admin", "--account", "prod-db"])
        self.assertEqual(args.command, "get")
        self.assertEqual(args.user, "admin")
        self.assertEqual(args.account, "prod-db")

    def test_get_missing_user_exits(self):
        """get without --user should cause an error"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["get", "--account", "prod-db"])

    def test_get_missing_account_exits(self):
        """get without --account should cause an error"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["get", "--user", "admin"])

    def test_get_field_default_is_password(self):
        """get --field defaults to 'password'"""
        args = self.parser.parse_args(["get", "--user", "admin", "--account", "prod-db"])
        self.assertEqual(args.field, "password")

    def test_get_field_accepts_valid_choices(self):
        """get --field accepts password, username, category, last_modified, all"""
        for field in ["password", "username", "category", "last_modified", "all"]:
            args = self.parser.parse_args([
                "get", "--user", "admin", "--account", "prod-db", "--field", field
            ])
            self.assertEqual(args.field, field)

    def test_get_field_rejects_invalid_choice(self):
        """get --field rejects values not in the allowed set"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                "get", "--user", "admin", "--account", "prod-db", "--field", "bogus"
            ])

    def test_get_json_flag(self):
        """get --json sets the json attribute to True"""
        args = self.parser.parse_args([
            "get", "--user", "admin", "--account", "prod-db", "--json"
        ])
        self.assertTrue(args.json)

    def test_get_json_default_false(self):
        """get without --json defaults to False"""
        args = self.parser.parse_args(["get", "--user", "admin", "--account", "prod-db"])
        self.assertFalse(args.json)

    def test_get_optional_username(self):
        """get --username is optional and used to disambiguate"""
        args = self.parser.parse_args([
            "get", "--user", "admin", "--account", "prod-db", "--username", "dbadmin"
        ])
        self.assertEqual(args.username, "dbadmin")

    def test_get_rejects_password_flag(self):
        """get should NOT accept --password (removed in auth redesign)"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                "get", "--user", "admin", "--account", "prod-db", "--password", "secret"
            ])

    # --- list subcommand ---

    def test_list_requires_user(self):
        """list subcommand requires --user"""
        args = self.parser.parse_args(["list", "--user", "admin"])
        self.assertEqual(args.command, "list")
        self.assertEqual(args.user, "admin")

    def test_list_missing_user_exits(self):
        """list without --user should cause an error"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["list"])

    def test_list_json_flag(self):
        """list --json sets the json attribute to True"""
        args = self.parser.parse_args(["list", "--user", "admin", "--json"])
        self.assertTrue(args.json)

    def test_list_rejects_password_flag(self):
        """list should NOT accept --password"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args(["list", "--user", "admin", "--password", "secret"])

    # --- add subcommand ---

    def test_add_requires_all_fields(self):
        """add requires --user, --category, --account, --secret-username, --secret"""
        args = self.parser.parse_args([
            "add", "--user", "admin", "--category", "Database",
            "--account", "prod-db", "--secret-username", "dbadmin",
            "--secret", "P@ssw0rd!"
        ])
        self.assertEqual(args.command, "add")
        self.assertEqual(args.category, "Database")
        self.assertEqual(args.account, "prod-db")
        self.assertEqual(args.secret_username, "dbadmin")
        self.assertEqual(args.secret, "P@ssw0rd!")

    def test_add_missing_category_exits(self):
        """add without --category should cause an error"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                "add", "--user", "admin", "--account", "prod-db",
                "--secret-username", "dbadmin", "--secret", "pass"
            ])

    def test_add_missing_secret_exits(self):
        """add without --secret should cause an error"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                "add", "--user", "admin", "--category", "DB",
                "--account", "prod-db", "--secret-username", "dbadmin"
            ])

    # --- update subcommand ---

    def test_update_requires_account_and_new_secret(self):
        """update requires --user, --account, --new-secret"""
        args = self.parser.parse_args([
            "update", "--user", "admin", "--account", "prod-db",
            "--new-secret", "NewP@ss!"
        ])
        self.assertEqual(args.command, "update")
        self.assertEqual(args.account, "prod-db")
        self.assertEqual(args.new_secret, "NewP@ss!")

    def test_update_missing_new_secret_exits(self):
        """update without --new-secret should cause an error"""
        with self.assertRaises(SystemExit):
            self.parser.parse_args([
                "update", "--user", "admin", "--account", "prod-db"
            ])

    def test_update_optional_secret_username(self):
        """update --secret-username is optional for disambiguation"""
        args = self.parser.parse_args([
            "update", "--user", "admin", "--account", "prod-db",
            "--new-secret", "NewP@ss!", "--secret-username", "dbadmin"
        ])
        self.assertEqual(args.secret_username, "dbadmin")

    # --- delete subcommand ---

    def test_delete_requires_user_and_account(self):
        """delete requires --user and --account"""
        args = self.parser.parse_args([
            "delete", "--user", "admin", "--account", "prod-db"
        ])
        self.assertEqual(args.command, "delete")
        self.assertEqual(args.account, "prod-db")

    def test_delete_force_flag(self):
        """delete --force sets the force attribute to True"""
        args = self.parser.parse_args([
            "delete", "--user", "admin", "--account", "prod-db", "--force"
        ])
        self.assertTrue(args.force)

    def test_delete_force_default_false(self):
        """delete without --force defaults to False"""
        args = self.parser.parse_args([
            "delete", "--user", "admin", "--account", "prod-db"
        ])
        self.assertFalse(args.force)

    # --- signin subcommand ---

    def test_signin_requires_user(self):
        """signin subcommand requires --user"""
        args = self.parser.parse_args(["signin", "--user", "admin"])
        self.assertEqual(args.command, "signin")
        self.assertEqual(args.user, "admin")

    def test_signin_ttl_default(self):
        """signin --ttl defaults to 60 minutes"""
        args = self.parser.parse_args(["signin", "--user", "admin"])
        self.assertEqual(args.ttl, 60)

    def test_signin_custom_ttl(self):
        """signin --ttl accepts custom value"""
        args = self.parser.parse_args(["signin", "--user", "admin", "--ttl", "120"])
        self.assertEqual(args.ttl, 120)

    # --- signout subcommand ---

    def test_signout_command(self):
        """signout should be a valid subcommand"""
        args = self.parser.parse_args(["signout"])
        self.assertEqual(args.command, "signout")

    # --- token create subcommand ---

    def test_token_create_requires_user_and_name(self):
        """token create requires --user and --name"""
        args = self.parser.parse_args([
            "token", "create", "--user", "admin", "--name", "ci-pipeline"
        ])
        self.assertEqual(args.command, "token")
        self.assertEqual(args.token_command, "create")
        self.assertEqual(args.user, "admin")
        self.assertEqual(args.name, "ci-pipeline")

    def test_token_create_expires_days_default(self):
        """token create --expires-days defaults to None (no expiry)"""
        args = self.parser.parse_args([
            "token", "create", "--user", "admin", "--name", "ci"
        ])
        self.assertIsNone(args.expires_days)

    def test_token_create_custom_expires(self):
        """token create --expires-days accepts a custom value"""
        args = self.parser.parse_args([
            "token", "create", "--user", "admin", "--name", "ci",
            "--expires-days", "90"
        ])
        self.assertEqual(args.expires_days, 90)

    # --- token list subcommand ---

    def test_token_list_requires_user(self):
        """token list requires --user"""
        args = self.parser.parse_args(["token", "list", "--user", "admin"])
        self.assertEqual(args.command, "token")
        self.assertEqual(args.token_command, "list")
        self.assertEqual(args.user, "admin")

    def test_token_list_json_flag(self):
        """token list --json sets the json attribute"""
        args = self.parser.parse_args(["token", "list", "--user", "admin", "--json"])
        self.assertTrue(args.json)

    # --- token revoke subcommand ---

    def test_token_revoke_requires_user_and_id(self):
        """token revoke requires --user and --token-id"""
        args = self.parser.parse_args([
            "token", "revoke", "--user", "admin", "--token-id", "cg_svc_abc123"
        ])
        self.assertEqual(args.command, "token")
        self.assertEqual(args.token_command, "revoke")
        self.assertEqual(args.token_id, "cg_svc_abc123")

    # --- no subcommand ---

    def test_no_command_sets_none(self):
        """Running with no subcommand sets command to None"""
        args = self.parser.parse_args([])
        self.assertIsNone(args.command)


class TestResolvePasswordForAuth(unittest.TestCase):
    """Test password resolution for auth commands (signin, token create/list/revoke)"""

    def test_env_var_takes_priority(self):
        """CLIGUARD_PASSWORD env var should be used when set"""
        with patch.dict(os.environ, {"CLIGUARD_PASSWORD": "env_pass"}):
            result = CLI_Guard_CLI._resolve_password_for_auth()
            self.assertEqual(result, "env_pass")

    def test_getpass_used_when_tty_and_no_env(self):
        """Interactive prompt should be used at a TTY when env var not set"""
        env = {k: v for k, v in os.environ.items() if k != "CLIGUARD_PASSWORD"}
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stdin.isatty", return_value=True):
                with patch("CLI_Guard_CLI.getpass.getpass", return_value="prompted_pass"):
                    result = CLI_Guard_CLI._resolve_password_for_auth()
                    self.assertEqual(result, "prompted_pass")

    def test_stdin_used_when_not_tty_and_no_env(self):
        """Stdin pipe should be used when not a TTY and env var not set"""
        env = {k: v for k, v in os.environ.items() if k != "CLIGUARD_PASSWORD"}
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stdin", StringIO("piped_pass\n")):
                result = CLI_Guard_CLI._resolve_password_for_auth()
                self.assertEqual(result, "piped_pass")

    def test_exits_when_nothing_available(self):
        """Should exit with error when no password source is available"""
        env = {k: v for k, v in os.environ.items() if k != "CLIGUARD_PASSWORD"}
        with patch.dict(os.environ, env, clear=True):
            with patch("sys.stdin.isatty", return_value=True):
                with patch("CLI_Guard_CLI.getpass.getpass", return_value=""):
                    with self.assertRaises(SystemExit) as ctx:
                        CLI_Guard_CLI._resolve_password_for_auth()
                    self.assertEqual(ctx.exception.code, CLI_Guard_CLI.EXIT_ERROR)

    def test_env_var_overrides_tty(self):
        """If CLIGUARD_PASSWORD is set, getpass should not be called"""
        with patch.dict(os.environ, {"CLIGUARD_PASSWORD": "env_pass"}):
            with patch("CLI_Guard_CLI.getpass.getpass") as mock_getpass:
                result = CLI_Guard_CLI._resolve_password_for_auth()
                mock_getpass.assert_not_called()
                self.assertEqual(result, "env_pass")


class TestResolveAuth(unittest.TestCase):
    """Test token-based auth resolution for data commands"""

    def test_no_tokens_exits_with_auth_failure(self):
        """Should exit with EXIT_AUTH_FAILURE when no tokens are set"""
        env = {k: v for k, v in os.environ.items()
               if k not in ("CLIGUARD_SERVICE_TOKEN", "CLIGUARD_SESSION")}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                CLI_Guard_CLI._resolve_auth("admin")
            self.assertEqual(ctx.exception.code, CLI_Guard_CLI.EXIT_AUTH_FAILURE)

    def test_invalid_username_exits(self):
        """Should exit with EXIT_ERROR for invalid username format"""
        with self.assertRaises(SystemExit) as ctx:
            CLI_Guard_CLI._resolve_auth("a")  # too short
        self.assertEqual(ctx.exception.code, CLI_Guard_CLI.EXIT_ERROR)


class TestExitCodes(unittest.TestCase):
    """Verify exit code constants are defined correctly"""

    def test_exit_codes_are_distinct(self):
        """All exit codes should be unique integers"""
        codes = [
            CLI_Guard_CLI.EXIT_SUCCESS,
            CLI_Guard_CLI.EXIT_ERROR,
            CLI_Guard_CLI.EXIT_AUTH_FAILURE,
            CLI_Guard_CLI.EXIT_NOT_FOUND,
            CLI_Guard_CLI.EXIT_DB_ERROR,
            CLI_Guard_CLI.EXIT_TOKEN_EXPIRED,
        ]
        self.assertEqual(len(codes), len(set(codes)), "Exit codes must be unique")

    def test_exit_success_is_zero(self):
        """EXIT_SUCCESS must be 0 (Unix convention)"""
        self.assertEqual(CLI_Guard_CLI.EXIT_SUCCESS, 0)

    def test_exit_codes_are_positive(self):
        """Error exit codes should be positive integers"""
        self.assertGreater(CLI_Guard_CLI.EXIT_ERROR, 0)
        self.assertGreater(CLI_Guard_CLI.EXIT_AUTH_FAILURE, 0)
        self.assertGreater(CLI_Guard_CLI.EXIT_NOT_FOUND, 0)
        self.assertGreater(CLI_Guard_CLI.EXIT_DB_ERROR, 0)
        self.assertGreater(CLI_Guard_CLI.EXIT_TOKEN_EXPIRED, 0)

    def test_token_expired_code_exists(self):
        """EXIT_TOKEN_EXPIRED should be defined and equal to 5"""
        self.assertEqual(CLI_Guard_CLI.EXIT_TOKEN_EXPIRED, 5)


if __name__ == '__main__':
    unittest.main()
