"""
Unit tests for password_generator module (scramble, random, passphrase)

Tests verify cryptographic randomness properties, character pool constraints,
word list integrity, and edge case handling.
"""

import unittest
import string
import sys
import os

# Add parent directory to path so we can import password_generator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import password_generator


class TestScramblePassword(unittest.TestCase):
    """Test leet-speak substitution + case randomization"""

    def test_returns_string(self):
        """scramble_password should return a string"""
        result = password_generator.scramble_password("TestPassword")
        self.assertIsInstance(result, str)

    def test_preserves_length(self):
        """Output length should equal input length"""
        password = "MyPassword123!"
        result = password_generator.scramble_password(password)
        self.assertEqual(len(result), len(password))

    def test_empty_input(self):
        """Empty string should return empty string"""
        self.assertEqual(password_generator.scramble_password(""), "")

    def test_no_alpha_chars(self):
        """Non-alphabetic input should be returned unchanged"""
        password = "12345!@#$%"
        result = password_generator.scramble_password(password)
        self.assertEqual(result, password)

    def test_preserves_non_alpha_chars(self):
        """Digits and symbols should not be modified"""
        password = "a1b2c3!"
        result = password_generator.scramble_password(password)
        # Extract non-alpha chars from result — they should match original positions
        for i, ch in enumerate(password):
            if not ch.isalpha():
                self.assertEqual(result[i], ch, f"Non-alpha char at position {i} was modified")

    def test_produces_varied_output(self):
        """Multiple scrambles should produce different results (probabilistic)"""
        password = "TestPassword"
        results = set()
        for _ in range(20):
            results.add(password_generator.scramble_password(password))
        self.assertGreater(len(results), 1, "Scramble should produce varied output")

    def test_contains_substitutions(self):
        """Scrambling a password with substitutable chars should eventually produce substitutions"""
        password = "aeiost"  # All have leet-speak mappings
        substitution_chars = set("@43!105$7+2|89")
        found_sub = False
        for _ in range(50):
            result = password_generator.scramble_password(password)
            if any(ch in substitution_chars for ch in result):
                found_sub = True
                break
        self.assertTrue(found_sub, "Should eventually produce leet-speak substitutions")

    def test_case_variation(self):
        """Scrambled output should have mixed case (probabilistic)"""
        password = "abcdefghijklmnop"  # All lowercase, no leet-speak mapping for most
        has_upper = False
        has_lower = False
        for _ in range(20):
            result = password_generator.scramble_password(password)
            alpha_chars = [ch for ch in result if ch.isalpha()]
            if any(ch.isupper() for ch in alpha_chars):
                has_upper = True
            if any(ch.islower() for ch in alpha_chars):
                has_lower = True
            if has_upper and has_lower:
                break
        self.assertTrue(has_upper and has_lower, "Should produce both upper and lower case")

    def test_single_char(self):
        """Single character input should work"""
        result = password_generator.scramble_password("a")
        self.assertEqual(len(result), 1)


class TestGenerateRandom(unittest.TestCase):
    """Test cryptographically random password generation"""

    def test_returns_string(self):
        """generate_random should return a string"""
        result = password_generator.generate_random()
        self.assertIsInstance(result, str)

    def test_default_length(self):
        """Default length should be 20"""
        result = password_generator.generate_random()
        self.assertEqual(len(result), 20)

    def test_custom_length(self):
        """Custom length should be respected"""
        result = password_generator.generate_random(length=30)
        self.assertEqual(len(result), 30)

    def test_min_length_clamping(self):
        """Length below minimum should be clamped to 12"""
        result = password_generator.generate_random(length=4)
        self.assertEqual(len(result), 12)

    def test_max_length_clamping(self):
        """Length above maximum should be clamped to 128"""
        result = password_generator.generate_random(length=500)
        self.assertEqual(len(result), 128)

    def test_has_uppercase(self):
        """Generated password must contain uppercase"""
        result = password_generator.generate_random()
        self.assertTrue(any(c in string.ascii_uppercase for c in result))

    def test_has_lowercase(self):
        """Generated password must contain lowercase"""
        result = password_generator.generate_random()
        self.assertTrue(any(c in string.ascii_lowercase for c in result))

    def test_has_digit(self):
        """Generated password must contain a digit"""
        result = password_generator.generate_random()
        self.assertTrue(any(c in string.digits for c in result))

    def test_has_special_char(self):
        """Generated password must contain a special character"""
        result = password_generator.generate_random()
        self.assertTrue(any(c in password_generator.SPECIAL_CHARS for c in result))

    def test_all_chars_from_pool(self):
        """All characters must come from the defined charset"""
        for _ in range(10):
            result = password_generator.generate_random()
            for ch in result:
                self.assertIn(ch, password_generator.CHARSET,
                              f"Character '{ch}' not in allowed charset")

    def test_no_shell_dangerous_chars(self):
        """Generated passwords must not contain shell-hostile characters"""
        dangerous = set("|;'\"`\\{}<>~()[]?/")
        for _ in range(20):
            result = password_generator.generate_random()
            for ch in result:
                self.assertNotIn(ch, dangerous,
                                 f"Shell-dangerous character '{ch}' found in password")

    def test_unique_outputs(self):
        """Multiple calls should produce different passwords"""
        results = set()
        for _ in range(10):
            results.add(password_generator.generate_random())
        self.assertEqual(len(results), 10, "All 10 passwords should be unique")

    def test_guarantee_at_min_length(self):
        """Even at minimum length (12), all character categories should be present"""
        for _ in range(20):
            result = password_generator.generate_random(length=12)
            self.assertTrue(any(c in string.ascii_uppercase for c in result))
            self.assertTrue(any(c in string.ascii_lowercase for c in result))
            self.assertTrue(any(c in string.digits for c in result))
            self.assertTrue(any(c in password_generator.SPECIAL_CHARS for c in result))


class TestGeneratePassphrase(unittest.TestCase):
    """Test passphrase generation from word list"""

    @staticmethod
    def _extract_words(passphrase: str) -> list[str]:
        """Extract words from passphrase by splitting on separator characters."""
        import re
        # Split on any character from the SEPARATORS pool
        sep_pattern = '[' + re.escape(password_generator.SEPARATORS) + ']'
        return re.split(sep_pattern, passphrase)

    def test_returns_string(self):
        """generate_passphrase should return a string"""
        result = password_generator.generate_passphrase()
        self.assertIsInstance(result, str)

    def test_default_word_count(self):
        """Default should produce 4 words"""
        result = password_generator.generate_passphrase()
        words = self._extract_words(result)
        self.assertEqual(len(words), 4)

    def test_custom_word_count(self):
        """Custom word count should be respected"""
        result = password_generator.generate_passphrase(word_count=6)
        words = self._extract_words(result)
        self.assertEqual(len(words), 6)

    def test_min_word_count_clamping(self):
        """Word count below minimum should be clamped to 3"""
        result = password_generator.generate_passphrase(word_count=1)
        words = self._extract_words(result)
        self.assertEqual(len(words), 3)

    def test_max_word_count_clamping(self):
        """Word count above maximum should be clamped to 10"""
        result = password_generator.generate_passphrase(word_count=50)
        words = self._extract_words(result)
        self.assertEqual(len(words), 10)

    def test_words_from_list(self):
        """All words (lowercased) must come from the WORD_LIST"""
        for _ in range(10):
            result = password_generator.generate_passphrase()
            for word in self._extract_words(result):
                self.assertIn(word.lower(), password_generator.WORD_LIST,
                              f"Word '{word}' not in WORD_LIST")

    def test_separators_from_pool(self):
        """All separator characters must come from the SEPARATORS pool"""
        for _ in range(20):
            result = password_generator.generate_passphrase()
            for ch in result:
                if not ch.isalpha():
                    self.assertIn(ch, password_generator.SEPARATORS,
                                  f"Separator '{ch}' not in SEPARATORS pool")

    def test_has_separators(self):
        """Passphrase should contain separator characters between words"""
        result = password_generator.generate_passphrase()
        sep_count = sum(1 for ch in result if ch in password_generator.SEPARATORS)
        self.assertEqual(sep_count, 3, "4 words should have 3 separators")

    def test_varied_separators(self):
        """Multiple passphrases should eventually use different separators (probabilistic)"""
        all_seps = set()
        for _ in range(30):
            result = password_generator.generate_passphrase()
            for ch in result:
                if not ch.isalpha():
                    all_seps.add(ch)
        self.assertGreater(len(all_seps), 3,
                           "Should use varied separator characters across passphrases")

    def test_capitalization_variation(self):
        """Some words should be capitalized, some not (probabilistic ~27%)"""
        has_capitalized = False
        has_lowercase = False
        for _ in range(30):
            result = password_generator.generate_passphrase()
            words = self._extract_words(result)
            for word in words:
                if word[0].isupper():
                    has_capitalized = True
                else:
                    has_lowercase = True
            if has_capitalized and has_lowercase:
                break
        self.assertTrue(has_capitalized and has_lowercase,
                        "Should produce both capitalized and lowercase words")

    def test_unique_outputs(self):
        """Multiple calls should produce different passphrases"""
        results = set()
        for _ in range(10):
            results.add(password_generator.generate_passphrase())
        self.assertGreater(len(results), 5,
                           "Most passphrases should be unique (4 words from 4096)")


class TestWordList(unittest.TestCase):
    """Test the embedded word list integrity"""

    def test_word_count(self):
        """WORD_LIST should have exactly 4,096 entries"""
        self.assertEqual(len(password_generator.WORD_LIST), 4096)

    def test_no_duplicates(self):
        """WORD_LIST should have no duplicate entries"""
        self.assertEqual(len(password_generator.WORD_LIST),
                         len(set(password_generator.WORD_LIST)))

    def test_all_lowercase(self):
        """All words should be lowercase"""
        for word in password_generator.WORD_LIST:
            self.assertEqual(word, word.lower(),
                             f"Word '{word}' is not lowercase")

    def test_all_alpha(self):
        """All words should be alphabetic only (no digits, spaces, hyphens)"""
        for word in password_generator.WORD_LIST:
            self.assertTrue(word.isalpha(),
                            f"Word '{word}' contains non-alpha characters")

    def test_all_correct_length(self):
        """All words should be 4-8 characters"""
        for word in password_generator.WORD_LIST:
            self.assertTrue(4 <= len(word) <= 8,
                            f"Word '{word}' has length {len(word)}, expected 4-8")

    def test_is_tuple(self):
        """WORD_LIST should be a tuple (immutable)"""
        self.assertIsInstance(password_generator.WORD_LIST, tuple)


class TestConstants(unittest.TestCase):
    """Test module constants are correctly defined"""

    def test_charset_length(self):
        """CHARSET should have 74 characters"""
        self.assertEqual(len(password_generator.CHARSET), 74)

    def test_charset_no_duplicates(self):
        """CHARSET should have no duplicate characters"""
        self.assertEqual(len(password_generator.CHARSET),
                         len(set(password_generator.CHARSET)))

    def test_substitution_map_keys_lowercase(self):
        """All SUBSTITUTION_MAP keys should be lowercase letters"""
        for key in password_generator.SUBSTITUTION_MAP:
            self.assertTrue(key.islower() and key.isalpha(),
                            f"Key '{key}' should be a lowercase letter")

    def test_substitution_map_values_non_empty(self):
        """All SUBSTITUTION_MAP values should be non-empty lists"""
        for key, values in password_generator.SUBSTITUTION_MAP.items():
            self.assertIsInstance(values, list)
            self.assertGreater(len(values), 0,
                               f"Substitutions for '{key}' should not be empty")

    def test_separators_defined(self):
        """SEPARATORS should be a non-empty string"""
        self.assertIsInstance(password_generator.SEPARATORS, str)
        self.assertGreater(len(password_generator.SEPARATORS), 0)

    def test_separators_no_duplicates(self):
        """SEPARATORS should have no duplicate characters"""
        self.assertEqual(len(password_generator.SEPARATORS),
                         len(set(password_generator.SEPARATORS)))

    def test_default_length(self):
        """DEFAULT_LENGTH should be 20"""
        self.assertEqual(password_generator.DEFAULT_LENGTH, 20)

    def test_default_words(self):
        """DEFAULT_WORDS should be 4"""
        self.assertEqual(password_generator.DEFAULT_WORDS, 4)


if __name__ == '__main__':
    unittest.main()
