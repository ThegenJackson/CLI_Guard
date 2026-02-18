"""
Unit tests for CLI Guard CLI (argument parser and password resolution)

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

    def test_get_password_flag(self):
        """get --password passes the master password explicitly"""
        args = self.parser.parse_args([
            "get", "--user", "admin", "--account", "prod-db", "--password", "secret123"
        ])
        self.assertEqual(args.password, "secret123")

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

    # --- no subcommand ---

    def test_no_command_sets_none(self):
        """Running with no subcommand sets command to None"""
        args = self.parser.parse_args([])
        self.assertIsNone(args.command)


class TestResolvePassword(unittest.TestCase):
    """Test the 3-tier password resolution: flag → env var → stdin"""

    def test_flag_takes_priority(self):
        """--password flag should be returned first, even if env var is set"""
        with patch.dict(os.environ, {"CLIGUARD_PASSWORD": "env_pass"}):
            result = CLI_Guard_CLI._resolve_password("flag_pass")
            self.assertEqual(result, "flag_pass")

    def test_env_var_used_when_no_flag(self):
        """CLIGUARD_PASSWORD env var should be used when flag is None"""
        with patch.dict(os.environ, {"CLIGUARD_PASSWORD": "env_pass"}):
            result = CLI_Guard_CLI._resolve_password(None)
            self.assertEqual(result, "env_pass")

    def test_stdin_used_when_no_flag_or_env(self):
        """stdin should be read when no flag and no env var"""
        with patch.dict(os.environ, {}, clear=True):
            # Remove CLIGUARD_PASSWORD if it exists
            os.environ.pop("CLIGUARD_PASSWORD", None)
            with patch("sys.stdin", StringIO("piped_pass\n")):
                with patch("sys.stdin.isatty", return_value=False):
                    # StringIO doesn't have isatty, so we need to patch it
                    result = CLI_Guard_CLI._resolve_password(None)
                    self.assertEqual(result, "piped_pass")

    def test_returns_none_when_nothing_available(self):
        """Should return None when no flag, no env var, and stdin is a TTY"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("CLIGUARD_PASSWORD", None)
            with patch("sys.stdin.isatty", return_value=True):
                result = CLI_Guard_CLI._resolve_password(None)
                self.assertIsNone(result)

    def test_empty_flag_falls_through(self):
        """Empty string flag should fall through to env var"""
        with patch.dict(os.environ, {"CLIGUARD_PASSWORD": "env_pass"}):
            result = CLI_Guard_CLI._resolve_password("")
            self.assertEqual(result, "env_pass")

    def test_empty_env_var_falls_through(self):
        """Empty env var should fall through to stdin"""
        with patch.dict(os.environ, {"CLIGUARD_PASSWORD": ""}):
            with patch("sys.stdin.isatty", return_value=True):
                result = CLI_Guard_CLI._resolve_password(None)
                self.assertIsNone(result)


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


if __name__ == '__main__':
    unittest.main()
