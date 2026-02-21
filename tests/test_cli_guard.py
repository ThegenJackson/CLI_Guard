"""
Unit tests for CLI_Guard business logic (encryption, hashing, authentication)

These tests verify the core security functions work correctly.
"""

import unittest
import sys
import os

# Add parent directory to path so we can import CLI_Guard
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import CLI_Guard
from unittest.mock import patch

# Fixed 32-byte salt for testing — avoids database dependency in unit tests
TEST_SALT = b'\x01' * 32


class TestPasswordHashing(unittest.TestCase):
    """Test bcrypt password hashing and verification"""

    def test_hash_password_returns_bytes(self):
        """hashPassword should return bytes (bcrypt hash)"""
        password = "TestPassword123!"
        hashed = CLI_Guard.hashPassword(password)
        self.assertIsInstance(hashed, bytes)
        self.assertTrue(len(hashed) > 0)

    def test_hash_password_produces_different_hashes(self):
        """Same password should produce different hashes (due to random salt)"""
        password = "TestPassword123!"
        hash1 = CLI_Guard.hashPassword(password)
        hash2 = CLI_Guard.hashPassword(password)
        self.assertNotEqual(hash1, hash2, "Hashes should differ due to salt")

    def test_hash_password_with_special_characters(self):
        """hashPassword should handle special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = CLI_Guard.hashPassword(password)
        self.assertIsInstance(hashed, bytes)

    def test_hash_password_with_unicode(self):
        """hashPassword should handle unicode characters"""
        password = "Pàsswörd™"
        hashed = CLI_Guard.hashPassword(password)
        self.assertIsInstance(hashed, bytes)


class TestEncryptionKeyDerivation(unittest.TestCase):
    """Test PBKDF2 encryption key derivation"""

    def test_derive_encryption_key_returns_bytes(self):
        """deriveEncryptionKey should return bytes"""
        password = "TestPassword123!"
        key = CLI_Guard.deriveEncryptionKey(password, TEST_SALT)
        self.assertIsInstance(key, bytes)

    def test_derive_encryption_key_correct_length(self):
        """Derived key should be 44 bytes (32 bytes base64-encoded)"""
        password = "TestPassword123!"
        key = CLI_Guard.deriveEncryptionKey(password, TEST_SALT)
        # Base64-encoded 32 bytes = 44 characters
        self.assertEqual(len(key), 44)

    def test_derive_encryption_key_is_deterministic(self):
        """Same password + salt should always produce same key (for decryption)"""
        password = "TestPassword123!"
        key1 = CLI_Guard.deriveEncryptionKey(password, TEST_SALT)
        key2 = CLI_Guard.deriveEncryptionKey(password, TEST_SALT)
        self.assertEqual(key1, key2, "Key derivation must be deterministic")

    def test_derive_encryption_key_different_passwords(self):
        """Different passwords should produce different keys"""
        key1 = CLI_Guard.deriveEncryptionKey("Password1", TEST_SALT)
        key2 = CLI_Guard.deriveEncryptionKey("Password2", TEST_SALT)
        self.assertNotEqual(key1, key2)

    def test_derive_encryption_key_different_salts(self):
        """Same password with different salts should produce different keys"""
        password = "TestPassword123!"
        salt_a = b'\x01' * 32
        salt_b = b'\x02' * 32
        key_a = CLI_Guard.deriveEncryptionKey(password, salt_a)
        key_b = CLI_Guard.deriveEncryptionKey(password, salt_b)
        self.assertNotEqual(key_a, key_b)

    def test_generate_salt_returns_32_bytes(self):
        """generateSalt should return 32 random bytes"""
        salt = CLI_Guard.generateSalt()
        self.assertIsInstance(salt, bytes)
        self.assertEqual(len(salt), 32)

    def test_generate_salt_is_random(self):
        """generateSalt should produce different values each time"""
        salt1 = CLI_Guard.generateSalt()
        salt2 = CLI_Guard.generateSalt()
        self.assertNotEqual(salt1, salt2)


class TestEncryptionDecryption(unittest.TestCase):
    """Test Fernet encryption and decryption"""

    def setUp(self):
        """Start a test session before each test"""
        self.salt_patcher = patch('CLI_Guard.sqlite.queryUserSalt', return_value=TEST_SALT.hex())
        self.salt_patcher.start()
        test_user = "test_user"
        test_password = "TestPassword123!"
        CLI_Guard.startSession(test_user, test_password)

    def tearDown(self):
        """End session after each test"""
        CLI_Guard.endSession()
        self.salt_patcher.stop()

    def test_encrypt_password(self):
        """encryptPassword should return an encrypted string"""
        plaintext = "MySecretPassword123!"
        encrypted = CLI_Guard.encryptPassword(plaintext)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, plaintext)

    def test_decrypt_password(self):
        """decryptPassword should recover original plaintext"""
        plaintext = "MySecretPassword123!"
        encrypted = CLI_Guard.encryptPassword(plaintext)
        decrypted = CLI_Guard.decryptPassword(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_decrypt_with_special_characters(self):
        """Encryption should handle special characters"""
        plaintext = "P@ssw0rd!#$%^&*()_+-=[]{}|;:,.<>?"
        encrypted = CLI_Guard.encryptPassword(plaintext)
        decrypted = CLI_Guard.decryptPassword(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_decrypt_with_unicode(self):
        """Encryption should handle unicode"""
        plaintext = "Pàsswörd™€"
        encrypted = CLI_Guard.encryptPassword(plaintext)
        decrypted = CLI_Guard.decryptPassword(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_decrypt_empty_string(self):
        """Encryption should handle empty strings"""
        plaintext = ""
        encrypted = CLI_Guard.encryptPassword(plaintext)
        decrypted = CLI_Guard.decryptPassword(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_encrypt_without_session_raises_error(self):
        """encryptPassword should raise error if no session"""
        CLI_Guard.endSession()  # End the session from setUp
        with self.assertRaises(RuntimeError):
            CLI_Guard.encryptPassword("test")

    def test_decrypt_without_session_raises_error(self):
        """decryptPassword should raise error if no session"""
        encrypted = CLI_Guard.encryptPassword("test")
        CLI_Guard.endSession()
        with self.assertRaises(RuntimeError):
            CLI_Guard.decryptPassword(encrypted)

    def test_decrypt_with_wrong_key_raises_error(self):
        """Decryption with wrong key should fail"""
        # Encrypt with one session
        plaintext = "MySecretPassword123!"
        encrypted = CLI_Guard.encryptPassword(plaintext)

        # Start new session with different password
        CLI_Guard.endSession()
        CLI_Guard.startSession("test_user", "DifferentPassword123!")

        # Try to decrypt - should raise error
        with self.assertRaises(Exception):
            CLI_Guard.decryptPassword(encrypted)


class TestSessionManagement(unittest.TestCase):
    """Test session lifecycle management"""

    def setUp(self):
        self.salt_patcher = patch('CLI_Guard.sqlite.queryUserSalt', return_value=TEST_SALT.hex())
        self.salt_patcher.start()

    def tearDown(self):
        CLI_Guard.endSession()
        self.salt_patcher.stop()

    def test_start_session_sets_user(self):
        """startSession should set session user"""
        CLI_Guard.startSession("test_user", "TestPassword123!")
        self.assertEqual(CLI_Guard.getSessionUser(), "test_user")
        CLI_Guard.endSession()

    def test_start_session_sets_encryption_key(self):
        """startSession should set encryption key"""
        CLI_Guard.startSession("test_user", "TestPassword123!")
        key = CLI_Guard.getSessionEncryptionKey()
        self.assertIsNotNone(key)
        self.assertIsInstance(key, bytes)
        CLI_Guard.endSession()

    def test_end_session_clears_data(self):
        """endSession should clear all session data"""
        CLI_Guard.startSession("test_user", "TestPassword123!")
        CLI_Guard.endSession()
        self.assertIsNone(CLI_Guard.getSessionUser())
        self.assertIsNone(CLI_Guard.getSessionEncryptionKey())

    def test_multiple_sessions(self):
        """Should handle multiple session start/stop cycles"""
        # Session 1
        CLI_Guard.startSession("user1", "Password1")
        self.assertEqual(CLI_Guard.getSessionUser(), "user1")
        CLI_Guard.endSession()

        # Session 2
        CLI_Guard.startSession("user2", "Password2")
        self.assertEqual(CLI_Guard.getSessionUser(), "user2")
        CLI_Guard.endSession()


class TestStartSessionFromKey(unittest.TestCase):
    """Test startSessionFromKey() for token-based auth"""

    def setUp(self):
        self.salt_patcher = patch('CLI_Guard.sqlite.queryUserSalt', return_value=TEST_SALT.hex())
        self.salt_patcher.start()

    def tearDown(self):
        """Ensure session is ended"""
        CLI_Guard.endSession()
        self.salt_patcher.stop()

    def test_valid_key_starts_session(self):
        """startSessionFromKey should set user and key when given a valid Fernet key"""
        key = CLI_Guard.deriveEncryptionKey("TestPassword123!", TEST_SALT)
        CLI_Guard.startSessionFromKey("test_user", key)
        self.assertEqual(CLI_Guard.getSessionUser(), "test_user")
        self.assertEqual(CLI_Guard.getSessionEncryptionKey(), key)

    def test_invalid_key_raises_value_error(self):
        """startSessionFromKey should raise ValueError for invalid keys"""
        with self.assertRaises(ValueError):
            CLI_Guard.startSessionFromKey("test_user", b"not_a_valid_key")

    def test_encrypt_decrypt_with_key_session(self):
        """Encryption/decryption should work after startSessionFromKey"""
        key = CLI_Guard.deriveEncryptionKey("TestPassword123!", TEST_SALT)
        CLI_Guard.startSessionFromKey("test_user", key)

        plaintext = "MySecret123!"
        encrypted = CLI_Guard.encryptPassword(plaintext)
        decrypted = CLI_Guard.decryptPassword(encrypted)
        self.assertEqual(decrypted, plaintext)

    def test_key_session_matches_password_session(self):
        """startSessionFromKey and startSession with same password should produce same key"""
        password = "TestPassword123!"
        key = CLI_Guard.deriveEncryptionKey(password, TEST_SALT)

        # Encrypt with password-based session
        CLI_Guard.startSession("test_user", password)
        encrypted = CLI_Guard.encryptPassword("test_secret")
        CLI_Guard.endSession()

        # Decrypt with key-based session
        CLI_Guard.startSessionFromKey("test_user", key)
        decrypted = CLI_Guard.decryptPassword(encrypted)
        self.assertEqual(decrypted, "test_secret")


class TestAuthenticationError(unittest.TestCase):
    """Test AuthenticationError exception"""

    def test_exception_exists(self):
        """AuthenticationError should be defined on CLI_Guard module"""
        self.assertTrue(hasattr(CLI_Guard, 'AuthenticationError'))

    def test_exception_is_exception_subclass(self):
        """AuthenticationError should be a subclass of Exception"""
        self.assertTrue(issubclass(CLI_Guard.AuthenticationError, Exception))

    def test_exception_can_be_raised_and_caught(self):
        """AuthenticationError should be raisable and catchable"""
        with self.assertRaises(CLI_Guard.AuthenticationError):
            raise CLI_Guard.AuthenticationError("test message")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions used by CLI/scripting interface"""

    def setUp(self):
        """Start a test session"""
        self.salt_patcher = patch('CLI_Guard.sqlite.queryUserSalt', return_value=TEST_SALT.hex())
        self.salt_patcher.start()
        CLI_Guard.startSession("test_user", "TestPassword123!")

    def tearDown(self):
        """End session"""
        CLI_Guard.endSession()
        self.salt_patcher.stop()

    def test_get_secrets_no_session_raises(self):
        """getSecrets should raise RuntimeError if no session"""
        CLI_Guard.endSession()
        with self.assertRaises(RuntimeError):
            CLI_Guard.getSecrets("test_user")

    def test_get_secret_no_session_raises(self):
        """getSecret should raise RuntimeError if no session"""
        CLI_Guard.endSession()
        with self.assertRaises(RuntimeError):
            CLI_Guard.getSecret("test_user", "some-account")

    def test_add_secret_no_session_raises(self):
        """addSecret should raise RuntimeError if no session"""
        CLI_Guard.endSession()
        with self.assertRaises(RuntimeError):
            CLI_Guard.addSecret("test_user", "cat", "acct", "user", "pass")

    def test_update_secret_no_session_raises(self):
        """updateSecret should raise RuntimeError if no session"""
        CLI_Guard.endSession()
        with self.assertRaises(RuntimeError):
            CLI_Guard.updateSecret("test_user", "acct", "user", "old", "new")

    def test_delete_secret_no_session_raises(self):
        """deleteSecret should raise RuntimeError if no session"""
        CLI_Guard.endSession()
        with self.assertRaises(RuntimeError):
            CLI_Guard.deleteSecret("test_user", "acct", "user", "encrypted")

    def test_is_account_locked_returns_bool(self):
        """isAccountLocked should return a boolean"""
        result = CLI_Guard.isAccountLocked("nonexistent_user_xyz")
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_get_secrets_returns_list(self):
        """getSecrets should return a list (even if empty)"""
        result = CLI_Guard.getSecrets("nonexistent_user_xyz")
        self.assertIsInstance(result, list)

    def test_get_secret_returns_none_for_missing(self):
        """getSecret should return None for nonexistent account"""
        result = CLI_Guard.getSecret("test_user", "nonexistent_account_xyz")
        self.assertIsNone(result)

    def test_get_secrets_dict_structure(self):
        """getSecrets results should have expected dict keys"""
        expected_keys = {"category", "account", "username", "password", "last_modified"}
        results = CLI_Guard.getSecrets("test_user")
        for secret in results:
            self.assertEqual(set(secret.keys()), expected_keys)


if __name__ == '__main__':
    unittest.main()
