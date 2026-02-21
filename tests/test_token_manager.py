"""
Unit tests for token_manager (key wrapping, session tokens, service tokens)

Tests use mocking to avoid real database operations and temp directories
to avoid touching the real session directory.
"""

import unittest
import sys
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch

# Add parent directory to path so we can import project modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import token_manager
import CLI_Guard


class TestKeyWrapping(unittest.TestCase):
    """Test the key wrapping/unwrapping cycle — the core security mechanism"""

    def test_derive_wrapping_key_returns_bytes(self):
        """Wrapping key derivation should return bytes"""
        key = token_manager._derive_wrapping_key("test_token")
        self.assertIsInstance(key, bytes)

    def test_derive_wrapping_key_correct_length(self):
        """Wrapping key should be 44 bytes (base64-encoded 32 bytes for Fernet)"""
        key = token_manager._derive_wrapping_key("test_token")
        self.assertEqual(len(key), 44)

    def test_derive_wrapping_key_is_deterministic(self):
        """Same token should always produce same wrapping key"""
        key1 = token_manager._derive_wrapping_key("test_token")
        key2 = token_manager._derive_wrapping_key("test_token")
        self.assertEqual(key1, key2)

    def test_derive_wrapping_key_different_tokens(self):
        """Different tokens should produce different wrapping keys"""
        key1 = token_manager._derive_wrapping_key("token_a")
        key2 = token_manager._derive_wrapping_key("token_b")
        self.assertNotEqual(key1, key2)

    def test_wrap_unwrap_roundtrip(self):
        """Wrapping then unwrapping should return the original key"""
        original_key = CLI_Guard.deriveEncryptionKey("TestPassword123!")
        token = "cg_ses_test_token_12345"

        wrapped = token_manager._wrap_key(original_key, token)
        unwrapped = token_manager._unwrap_key(wrapped, token)

        self.assertEqual(unwrapped, original_key)

    def test_unwrap_with_wrong_token_raises(self):
        """Unwrapping with wrong token should raise TokenInvalidError"""
        original_key = CLI_Guard.deriveEncryptionKey("TestPassword123!")
        wrapped = token_manager._wrap_key(original_key, "correct_token")

        with self.assertRaises(token_manager.TokenInvalidError):
            token_manager._unwrap_key(wrapped, "wrong_token")

    def test_wrapped_key_differs_from_original(self):
        """Wrapped blob should not be the same as the original key"""
        original_key = CLI_Guard.deriveEncryptionKey("TestPassword123!")
        wrapped = token_manager._wrap_key(original_key, "test_token")
        self.assertNotEqual(wrapped.encode('utf-8'), original_key)


class TestSessionTokens(unittest.TestCase):
    """Test session token creation, loading, invalidation, and cleanup"""

    def setUp(self):
        """Create a temporary session directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_session_dir = token_manager.SESSION_DIR
        token_manager.SESSION_DIR = self.temp_dir

    def tearDown(self):
        """Clean up temp directory and restore original"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        token_manager.SESSION_DIR = self.original_session_dir

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_create_session_returns_prefixed_token(self, mock_auth, mock_locked):
        """create_session should return a token with cg_ses_ prefix"""
        token = token_manager.create_session("testuser", "TestPass123!")
        self.assertTrue(token.startswith("cg_ses_"))

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_create_session_creates_file(self, mock_auth, mock_locked):
        """create_session should create a session file on disk"""
        token_manager.create_session("testuser", "TestPass123!")
        session_file = os.path.join(self.temp_dir, "testuser.json")
        self.assertTrue(os.path.exists(session_file))

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_create_and_load_session_roundtrip(self, mock_auth, mock_locked):
        """Should be able to load a session token after creating it"""
        token = token_manager.create_session("testuser", "TestPass123!")
        user, key = token_manager.load_session(token)
        self.assertEqual(user, "testuser")
        self.assertIsInstance(key, bytes)

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_loaded_key_matches_derived_key(self, mock_auth, mock_locked):
        """Key unwrapped from session should match the original derived key"""
        password = "TestPass123!"
        expected_key = CLI_Guard.deriveEncryptionKey(password)

        token = token_manager.create_session("testuser", password)
        _, loaded_key = token_manager.load_session(token)

        self.assertEqual(loaded_key, expected_key)

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_expired_session_raises(self, mock_auth, mock_locked):
        """Loading an expired session should raise TokenExpiredError"""
        token = token_manager.create_session("testuser", "TestPass123!", ttl_minutes=1)

        # Manually backdate the session file
        session_file = os.path.join(self.temp_dir, "testuser.json")
        with open(session_file, 'r') as f:
            data = json.load(f)
        data["created_at"] = (datetime.now() - timedelta(hours=2)).isoformat(timespec='seconds')
        with open(session_file, 'w') as f:
            json.dump(data, f)

        with self.assertRaises(token_manager.TokenExpiredError):
            token_manager.load_session(token)

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_invalidate_session_deletes_file(self, mock_auth, mock_locked):
        """Invalidating a session should delete the file and prevent reuse"""
        token = token_manager.create_session("testuser", "TestPass123!")

        result = token_manager.invalidate_session(token)
        self.assertTrue(result)

        with self.assertRaises(token_manager.TokenInvalidError):
            token_manager.load_session(token)

    def test_load_nonexistent_token_raises(self):
        """Loading a token with no matching session file should raise"""
        with self.assertRaises(token_manager.TokenInvalidError):
            token_manager.load_session("cg_ses_nonexistent_token_12345678")

    def test_load_non_session_prefix_raises(self):
        """Loading a token without cg_ses_ prefix should raise"""
        with self.assertRaises(token_manager.TokenInvalidError):
            token_manager.load_session("not_a_session_token")

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=False)
    def test_create_session_wrong_password(self, mock_auth, mock_locked):
        """create_session should raise AuthenticationError on bad password"""
        with self.assertRaises(CLI_Guard.AuthenticationError):
            token_manager.create_session("testuser", "WrongPassword!")

    @patch('CLI_Guard.isAccountLocked', return_value=True)
    def test_create_session_locked_account(self, mock_locked):
        """create_session should raise ValueError on locked account"""
        with self.assertRaises(ValueError):
            token_manager.create_session("testuser", "TestPass123!")

    @patch('CLI_Guard.isAccountLocked', return_value=False)
    @patch('CLI_Guard.authUser', return_value=True)
    def test_cleanup_expired_sessions(self, mock_auth, mock_locked):
        """cleanup_expired_sessions should remove only expired files"""
        token_manager.create_session("testuser", "TestPass123!", ttl_minutes=1)

        # Backdate the session to make it expired
        session_file = os.path.join(self.temp_dir, "testuser.json")
        with open(session_file, 'r') as f:
            data = json.load(f)
        data["created_at"] = (datetime.now() - timedelta(hours=2)).isoformat(timespec='seconds')
        with open(session_file, 'w') as f:
            json.dump(data, f)

        removed = token_manager.cleanup_expired_sessions()
        self.assertEqual(removed, 1)
        self.assertFalse(os.path.exists(session_file))

    def test_invalidate_nonexistent_returns_false(self):
        """Invalidating a token with no session file should return False"""
        result = token_manager.invalidate_session("cg_ses_does_not_exist")
        self.assertFalse(result)


class TestServiceTokens(unittest.TestCase):
    """Test service token creation, loading, listing, and revocation"""

    def setUp(self):
        """Mock database operations so tests don't touch real DB"""
        self.stored_tokens = {}

        def mock_insert(**kwargs):
            self.stored_tokens[kwargs['token_id']] = (
                kwargs['token_id'], kwargs['user'], kwargs['name'],
                kwargs['token_hash'], kwargs['wrapped_key'],
                kwargs['created_at'], kwargs.get('expires_at'),
                None, 0
            )

        def mock_query(token_id):
            return self.stored_tokens.get(token_id)

        def mock_query_by_user(user):
            return [row for row in self.stored_tokens.values() if row[1] == user]

        def mock_revoke(token_id):
            if token_id in self.stored_tokens:
                row = list(self.stored_tokens[token_id])
                row[8] = 1
                self.stored_tokens[token_id] = tuple(row)

        def mock_update_last_used(token_id, timestamp):
            if token_id in self.stored_tokens:
                row = list(self.stored_tokens[token_id])
                row[7] = timestamp
                self.stored_tokens[token_id] = tuple(row)

        self.patches = [
            patch('token_manager.sqlite.insertServiceToken', side_effect=mock_insert),
            patch('token_manager.sqlite.queryServiceToken', side_effect=mock_query),
            patch('token_manager.sqlite.queryServiceTokensByUser', side_effect=mock_query_by_user),
            patch('token_manager.sqlite.revokeServiceToken', side_effect=mock_revoke),
            patch('token_manager.sqlite.updateServiceTokenLastUsed', side_effect=mock_update_last_used),
            patch('CLI_Guard.isAccountLocked', return_value=False),
            patch('CLI_Guard.authUser', return_value=True),
        ]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_create_returns_prefixed_token(self):
        """create_service_token should return a token with cg_svc_ prefix"""
        token = token_manager.create_service_token("testuser", "TestPass123!", "ci")
        self.assertTrue(token.startswith("cg_svc_"))

    def test_create_and_load_roundtrip(self):
        """Should be able to load a service token after creating it"""
        token = token_manager.create_service_token("testuser", "TestPass123!", "ci")
        user, key = token_manager.load_service_token(token)
        self.assertEqual(user, "testuser")
        self.assertIsInstance(key, bytes)

    def test_loaded_key_matches_derived_key(self):
        """Key from service token should match the original derived key"""
        password = "TestPass123!"
        expected_key = CLI_Guard.deriveEncryptionKey(password)

        token = token_manager.create_service_token("testuser", password, "ci")
        _, loaded_key = token_manager.load_service_token(token)

        self.assertEqual(loaded_key, expected_key)

    def test_revoke_prevents_loading(self):
        """Revoking a token should prevent it from being loaded"""
        token = token_manager.create_service_token("testuser", "TestPass123!", "ci")
        token_id = token_manager._get_service_token_id(token)

        result = token_manager.revoke_service_token("testuser", token_id)
        self.assertTrue(result)

        with self.assertRaises(token_manager.TokenRevokedError):
            token_manager.load_service_token(token)

    def test_expired_service_token_raises(self):
        """Loading an expired service token should raise TokenExpiredError"""
        token = token_manager.create_service_token(
            "testuser", "TestPass123!", "ci", expires_days=1
        )

        # Manually backdate the expiry
        token_id = token_manager._get_service_token_id(token)
        row = list(self.stored_tokens[token_id])
        row[6] = (datetime.now() - timedelta(days=1)).isoformat(timespec='seconds')
        self.stored_tokens[token_id] = tuple(row)

        with self.assertRaises(token_manager.TokenExpiredError):
            token_manager.load_service_token(token)

    def test_load_nonexistent_raises(self):
        """Loading a token not in DB should raise TokenInvalidError"""
        with self.assertRaises(token_manager.TokenInvalidError):
            token_manager.load_service_token("cg_svc_nonexistent_token_12345678")

    def test_load_wrong_prefix_raises(self):
        """Loading a token without cg_svc_ prefix should raise"""
        with self.assertRaises(token_manager.TokenInvalidError):
            token_manager.load_service_token("not_a_service_token")

    def test_list_service_tokens(self):
        """list_service_tokens should return metadata for all user tokens"""
        token_manager.create_service_token("testuser", "TestPass123!", "ci-pipeline")
        token_manager.create_service_token("testuser", "TestPass123!", "deploy-bot")

        tokens = token_manager.list_service_tokens("testuser")
        self.assertEqual(len(tokens), 2)

        names = {t["name"] for t in tokens}
        self.assertIn("ci-pipeline", names)
        self.assertIn("deploy-bot", names)

    def test_list_service_tokens_dict_keys(self):
        """list_service_tokens results should have expected dict keys"""
        token_manager.create_service_token("testuser", "TestPass123!", "ci")
        tokens = token_manager.list_service_tokens("testuser")

        expected_keys = {"token_id", "name", "created_at", "expires_at", "last_used", "revoked"}
        self.assertEqual(set(tokens[0].keys()), expected_keys)

    def test_revoke_nonexistent_returns_false(self):
        """Revoking a nonexistent token should return False"""
        result = token_manager.revoke_service_token("testuser", "cg_svc_nonexistent")
        self.assertFalse(result)

    def test_revoke_wrong_user_raises(self):
        """Revoking another user's token should raise ValueError"""
        token = token_manager.create_service_token("testuser", "TestPass123!", "ci")
        token_id = token_manager._get_service_token_id(token)

        with self.assertRaises(ValueError):
            token_manager.revoke_service_token("other_user", token_id)

    @patch('CLI_Guard.authUser', return_value=False)
    def test_create_auth_failure(self, mock_auth):
        """create_service_token should raise AuthenticationError on bad password"""
        with self.assertRaises(CLI_Guard.AuthenticationError):
            token_manager.create_service_token("testuser", "WrongPass!", "ci")

    def test_service_token_no_expiry(self):
        """Service token with no expiry should load indefinitely"""
        token = token_manager.create_service_token(
            "testuser", "TestPass123!", "ci", expires_days=None
        )
        # Should load fine — no expiry to check
        user, key = token_manager.load_service_token(token)
        self.assertEqual(user, "testuser")


class TestTokenIdGeneration(unittest.TestCase):
    """Test token ID derivation from full tokens"""

    def test_token_id_has_correct_prefix(self):
        """Token ID should start with cg_svc_"""
        token_id = token_manager._get_service_token_id("cg_svc_some_random_token")
        self.assertTrue(token_id.startswith("cg_svc_"))

    def test_token_id_is_deterministic(self):
        """Same token should always produce same token_id"""
        token = "cg_svc_test_token_12345"
        id1 = token_manager._get_service_token_id(token)
        id2 = token_manager._get_service_token_id(token)
        self.assertEqual(id1, id2)

    def test_different_tokens_different_ids(self):
        """Different tokens should produce different IDs"""
        id1 = token_manager._get_service_token_id("cg_svc_token_a")
        id2 = token_manager._get_service_token_id("cg_svc_token_b")
        self.assertNotEqual(id1, id2)


class TestCustomExceptions(unittest.TestCase):
    """Test exception hierarchy"""

    def test_token_expired_is_token_error(self):
        """TokenExpiredError should be a subclass of TokenError"""
        self.assertTrue(issubclass(token_manager.TokenExpiredError, token_manager.TokenError))

    def test_token_invalid_is_token_error(self):
        """TokenInvalidError should be a subclass of TokenError"""
        self.assertTrue(issubclass(token_manager.TokenInvalidError, token_manager.TokenError))

    def test_token_revoked_is_token_error(self):
        """TokenRevokedError should be a subclass of TokenError"""
        self.assertTrue(issubclass(token_manager.TokenRevokedError, token_manager.TokenError))


if __name__ == '__main__':
    unittest.main()
