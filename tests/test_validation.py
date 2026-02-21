"""
Unit tests for input validation

These tests ensure validation logic correctly identifies valid/invalid inputs.
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import validation


class TestUsernameValidation(unittest.TestCase):
    """Test username validation rules"""

    def test_valid_username_alphanumeric(self):
        """Valid alphanumeric username should pass"""
        valid, error = validation.validate_username("john123")
        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_valid_username_with_underscore(self):
        """Username with underscore should be valid"""
        valid, error = validation.validate_username("john_doe")
        self.assertTrue(valid)

    def test_valid_username_with_hyphen(self):
        """Username with hyphen should be valid"""
        valid, error = validation.validate_username("john-doe")
        self.assertTrue(valid)

    def test_valid_username_with_period(self):
        """Username with period should be valid"""
        valid, error = validation.validate_username("john.doe")
        self.assertTrue(valid)

    def test_invalid_username_too_short(self):
        """Username less than 3 characters should fail"""
        valid, error = validation.validate_username("ab")
        self.assertFalse(valid)
        self.assertIn("3 characters", error)

    def test_invalid_username_too_long(self):
        """Username over 50 characters should fail"""
        valid, error = validation.validate_username("a" * 51)
        self.assertFalse(valid)
        self.assertIn("50 characters", error)

    def test_invalid_username_empty(self):
        """Empty username should fail"""
        valid, error = validation.validate_username("")
        self.assertFalse(valid)
        self.assertIn("empty", error.lower())

    def test_invalid_username_starts_with_special_char(self):
        """Username starting with special character should fail"""
        valid, error = validation.validate_username("_john")
        self.assertFalse(valid)

    def test_invalid_username_with_space(self):
        """Username with space should fail"""
        valid, error = validation.validate_username("john doe")
        self.assertFalse(valid)

    def test_invalid_username_with_special_chars(self):
        """Username with disallowed special characters should fail"""
        for username in ["john@doe", "john#doe", "john$doe", "john%doe"]:
            valid, error = validation.validate_username(username)
            self.assertFalse(valid, f"{username} should be invalid")


class TestPasswordValidation(unittest.TestCase):
    """Test password validation rules"""

    def test_valid_strong_password(self):
        """Strong password meeting all requirements should pass"""
        valid, error = validation.validate_password("MyP@ssw0rd!")
        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_invalid_password_too_short(self):
        """Password less than 8 characters should fail"""
        valid, error = validation.validate_password("Sh0rt!")
        self.assertFalse(valid)
        self.assertIn("8 characters", error)

    def test_invalid_password_too_long(self):
        """Password over 128 characters should fail"""
        valid, error = validation.validate_password("A1!" + "a" * 126)
        self.assertFalse(valid)
        self.assertIn("128 characters", error)

    def test_invalid_password_no_uppercase(self):
        """Password without uppercase should fail"""
        valid, error = validation.validate_password("myp@ssw0rd!")
        self.assertFalse(valid)
        self.assertIn("uppercase", error.lower())

    def test_invalid_password_no_lowercase(self):
        """Password without lowercase should fail"""
        valid, error = validation.validate_password("MYP@SSW0RD!")
        self.assertFalse(valid)
        self.assertIn("lowercase", error.lower())

    def test_invalid_password_no_digit(self):
        """Password without digit should fail"""
        valid, error = validation.validate_password("MyP@ssword!")
        self.assertFalse(valid)
        self.assertIn("number", error.lower())

    def test_invalid_password_no_special(self):
        """Password without special character should fail"""
        valid, error = validation.validate_password("MyPassw0rd")
        self.assertFalse(valid)
        self.assertIn("special", error.lower())

    def test_invalid_password_empty(self):
        """Empty password should fail"""
        valid, error = validation.validate_password("")
        self.assertFalse(valid)


class TestTextFieldValidation(unittest.TestCase):
    """Test generic text field validation"""

    def test_valid_text_field(self):
        """Valid text should pass"""
        valid, error = validation.validate_text_field("My Category", "Category")
        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_invalid_text_field_empty(self):
        """Empty text should fail"""
        valid, error = validation.validate_text_field("", "Category")
        self.assertFalse(valid)
        self.assertIn("empty", error.lower())

    def test_invalid_text_field_whitespace_only(self):
        """Whitespace-only text should fail"""
        valid, error = validation.validate_text_field("   ", "Category")
        self.assertFalse(valid)

    def test_valid_text_field_with_leading_trailing_spaces(self):
        """Text with spaces should be trimmed and validated"""
        valid, error = validation.validate_text_field("  Test  ", "Field", min_len=1, max_len=10)
        self.assertTrue(valid)

    def test_invalid_text_field_too_long(self):
        """Text exceeding max length should fail"""
        valid, error = validation.validate_text_field("a" * 101, "Category", max_len=100)
        self.assertFalse(valid)
        self.assertIn("100", error)

    def test_invalid_text_field_too_short(self):
        """Text below min length should fail"""
        valid, error = validation.validate_text_field("ab", "Category", min_len=3)
        self.assertFalse(valid)
        self.assertIn("3", error)

    def test_invalid_text_field_control_characters(self):
        """Text with control characters should fail"""
        valid, error = validation.validate_text_field("Test\x00\x01\x02", "Category")
        self.assertFalse(valid)
        self.assertIn("control", error.lower())


class TestTokenNameValidation(unittest.TestCase):
    """Test service token name validation rules"""

    def test_valid_token_name(self):
        """Valid alphanumeric token name should pass"""
        valid, error = validation.validate_token_name("ci-pipeline")
        self.assertTrue(valid)
        self.assertEqual(error, "")

    def test_valid_name_with_underscores(self):
        """Token name with underscores should pass"""
        valid, error = validation.validate_token_name("deploy_bot_v2")
        self.assertTrue(valid)

    def test_valid_name_with_hyphens(self):
        """Token name with hyphens should pass"""
        valid, error = validation.validate_token_name("github-actions-ci")
        self.assertTrue(valid)

    def test_valid_single_char_name(self):
        """Single character token name should pass"""
        valid, error = validation.validate_token_name("x")
        self.assertTrue(valid)

    def test_invalid_empty_name(self):
        """Empty token name should fail"""
        valid, error = validation.validate_token_name("")
        self.assertFalse(valid)
        self.assertIn("empty", error.lower())

    def test_invalid_name_too_long(self):
        """Token name over 50 characters should fail"""
        valid, error = validation.validate_token_name("a" * 51)
        self.assertFalse(valid)
        self.assertIn("50", error)

    def test_invalid_name_starts_with_hyphen(self):
        """Token name starting with hyphen should fail"""
        valid, error = validation.validate_token_name("-bad-name")
        self.assertFalse(valid)

    def test_invalid_name_with_spaces(self):
        """Token name with spaces should fail"""
        valid, error = validation.validate_token_name("bad name")
        self.assertFalse(valid)

    def test_invalid_name_with_special_chars(self):
        """Token name with special characters should fail"""
        for name in ["bad@name", "bad.name", "bad/name", "bad!name"]:
            valid, error = validation.validate_token_name(name)
            self.assertFalse(valid, f"'{name}' should be invalid")


class TestPasswordStrength(unittest.TestCase):
    """Test password strength calculation"""

    def test_weak_password(self):
        """Simple password should be weak"""
        label, score = validation.calculate_password_strength("pass")
        self.assertEqual(label, "Weak")
        self.assertLess(score, 40)

    def test_fair_password(self):
        """Moderate password should be fair or better"""
        label, score = validation.calculate_password_strength("Password1")
        self.assertIn(label, ["Weak", "Fair", "Good"])
        self.assertGreater(score, 0)

    def test_good_password(self):
        """Good password should score appropriately"""
        label, score = validation.calculate_password_strength("MyP@ssw0rd")
        self.assertIn(label, ["Fair", "Good", "Strong", "Very Strong"])
        self.assertGreater(score, 40)

    def test_strong_password(self):
        """Strong password should score high"""
        label, score = validation.calculate_password_strength("MyVery$tr0ng!P@ssw0rd#2024")
        self.assertIn(label, ["Strong", "Very Strong"])
        self.assertGreater(score, 75)

    def test_empty_password_strength(self):
        """Empty password should be weak with 0 score"""
        label, score = validation.calculate_password_strength("")
        self.assertEqual(label, "Weak")
        self.assertEqual(score, 0)

    def test_password_strength_increases_with_length(self):
        """Longer passwords should score higher"""
        short_label, short_score = validation.calculate_password_strength("Pass1!")
        long_label, long_score = validation.calculate_password_strength("Pass1!aaaaaaaaaaaaa")
        self.assertGreater(long_score, short_score)


class TestInputSanitization(unittest.TestCase):
    """Test input sanitization"""

    def test_sanitize_trims_whitespace(self):
        """Sanitization should trim leading/trailing whitespace"""
        result = validation.sanitize_input("  test  ")
        self.assertEqual(result, "test")

    def test_sanitize_removes_control_characters(self):
        """Sanitization should remove control characters"""
        result = validation.sanitize_input("test\x00\x01\x02string")
        self.assertNotIn("\x00", result)
        self.assertNotIn("\x01", result)

    def test_sanitize_normalizes_spaces(self):
        """Sanitization should normalize multiple spaces"""
        result = validation.sanitize_input("test    multiple    spaces")
        self.assertEqual(result, "test multiple spaces")

    def test_sanitize_empty_string(self):
        """Sanitization of empty string should return empty"""
        result = validation.sanitize_input("")
        self.assertEqual(result, "")


if __name__ == '__main__':
    unittest.main()
