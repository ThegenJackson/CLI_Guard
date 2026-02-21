"""
Input validation utilities for CLI_Guard

This module provides validation functions to ensure user inputs
are safe, reasonable, and won't cause database or security issues.
"""

import re
from typing import Tuple


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username meets security and format requirements

    Rules:
    - Length: 3-50 characters
    - Allowed: letters, numbers, underscore, hyphen, period
    - Must start with a letter or number

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)
        - If valid: (True, "")
        - If invalid: (False, "explanation of why")
    """
    if not username:
        return (False, "Username cannot be empty")

    if len(username) < 3:
        return (False, "Username must be at least 3 characters")

    if len(username) > 50:
        return (False, "Username must be 50 characters or less")

    # Check for valid characters (alphanumeric, underscore, hyphen, period)
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$', username):
        return (False, "Username must start with letter/number and contain only letters, numbers, ._-")

    return (True, "")


def validate_password(password: str) -> Tuple[bool, str]:
    """
    Validate password meets minimum security requirements

    Rules:
    - Length: 8-128 characters
    - Must contain at least:
      - 1 uppercase letter
      - 1 lowercase letter
      - 1 number
      - 1 special character

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return (False, "Password cannot be empty")

    if len(password) < 8:
        return (False, "Password must be at least 8 characters")

    if len(password) > 128:
        return (False, "Password must be 128 characters or less")

    # Check for required character types
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?/' for c in password)

    if not has_upper:
        return (False, "Password must contain at least one uppercase letter")
    if not has_lower:
        return (False, "Password must contain at least one lowercase letter")
    if not has_digit:
        return (False, "Password must contain at least one number")
    if not has_special:
        return (False, "Password must contain at least one special character")

    return (True, "")


def validate_text_field(text: str, field_name: str, min_len: int = 1, max_len: int = 100) -> Tuple[bool, str]:
    """
    Validate generic text field (category, account, username for passwords)

    Rules:
    - Length: min_len to max_len characters
    - No control characters (tabs, newlines, etc.)
    - Trimmed of leading/trailing whitespace

    Args:
        text: Text to validate
        field_name: Name of field (for error messages)
        min_len: Minimum length (default: 1)
        max_len: Maximum length (default: 100)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return (False, f"{field_name} cannot be empty")

    # Trim whitespace
    text = text.strip()

    if len(text) < min_len:
        return (False, f"{field_name} must be at least {min_len} character(s)")

    if len(text) > max_len:
        return (False, f"{field_name} must be {max_len} characters or less")

    # Check for control characters
    if any(ord(c) < 32 for c in text):
        return (False, f"{field_name} cannot contain control characters")

    return (True, "")


def validate_token_name(name: str) -> Tuple[bool, str]:
    """
    Validate a service token name meets format requirements

    Rules:
    - Length: 1-50 characters
    - Allowed: letters, numbers, hyphens, underscores
    - Must start with a letter or number

    Args:
        name: Token name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return (False, "Token name cannot be empty")

    if len(name) > 50:
        return (False, "Token name must be 50 characters or less")

    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_-]*$', name):
        return (False, "Token name must start with letter/number and contain only letters, numbers, hyphens, underscores")

    return (True, "")


def calculate_password_strength(password: str) -> Tuple[str, int]:
    """
    Calculate password strength score

    Scoring factors:
    - Length (up to 20 points)
    - Character variety (up to 40 points)
    - Entropy estimate (up to 40 points)

    Args:
        password: Password to analyze

    Returns:
        Tuple of (strength_label, score)
        - strength_label: "Weak", "Fair", "Good", "Strong", "Very Strong"
        - score: 0-100
    """
    if not password:
        return ("Weak", 0)

    score = 0

    # Length scoring (up to 20 points)
    length_score = min(len(password) * 2, 20)
    score += length_score

    # Character variety scoring (up to 40 points)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    variety_score = sum([has_lower, has_upper, has_digit, has_special]) * 10
    score += variety_score

    # Entropy estimate (up to 40 points)
    charset_size = 0
    if has_lower:
        charset_size += 26
    if has_upper:
        charset_size += 26
    if has_digit:
        charset_size += 10
    if has_special:
        charset_size += 32

    if charset_size > 0:
        import math
        entropy = len(password) * math.log2(charset_size)
        entropy_score = min(entropy / 2, 40)  # Normalize to 40 points
        score += entropy_score

    # Determine label
    if score < 40:
        label = "Weak"
    elif score < 60:
        label = "Fair"
    elif score < 75:
        label = "Good"
    elif score < 90:
        label = "Strong"
    else:
        label = "Very Strong"

    return (label, int(score))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing/replacing problematic characters

    This is a defensive measure that should be used AFTER validation,
    not instead of it.

    Args:
        text: Text to sanitize

    Returns:
        Sanitized text
    """
    # Trim whitespace
    text = text.strip()

    # Remove control characters (except space)
    text = ''.join(c for c in text if ord(c) >= 32 or c == '\n')

    # Normalize multiple spaces to single space
    text = ' '.join(text.split())

    return text
