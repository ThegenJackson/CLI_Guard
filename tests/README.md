# CLI_Guard Unit Tests

## Overview

This directory contains unit tests for CLI_Guard's critical security functions.

## What's Tested

### Security Functions (`test_cli_guard.py`)
- **Password Hashing** - Bcrypt hash generation and verification
- **Key Derivation** - PBKDF2 encryption key derivation
- **Encryption/Decryption** - Fernet symmetric encryption
- **Session Management** - Session lifecycle and key storage

### Input Validation (`test_validation.py`)
- **Username Validation** - Format and character restrictions
- **Password Validation** - Strength requirements
- **Text Field Validation** - Generic input validation
- **Password Strength** - Scoring algorithm
- **Input Sanitization** - Cleaning user inputs

## Running Tests

### Option 1: Using unittest (built-in)
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests/test_cli_guard.py

# Run specific test class
python -m unittest tests.test_cli_guard.TestEncryptionDecryption

# Run specific test method
python -m unittest tests.test_cli_guard.TestEncryptionDecryption.test_encrypt_password

# Run with verbose output
python -m unittest discover tests/ -v
```

### Option 2: Using pytest (if installed)
```bash
# Install pytest
pip install pytest

# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_validation.py

# Run tests matching pattern
pytest tests/ -k "encrypt"
```

## Test Coverage

Current coverage focuses on:
- ✅ Cryptographic operations (encryption, hashing, key derivation)
- ✅ Input validation (usernames, passwords, text fields)
- ✅ Session management
- ✅ Password strength calculation

## Why These Tests Matter

For a password manager, comprehensive testing is critical:

1. **Encryption bugs could expose all passwords** - Tests verify encryption/decryption work correctly
2. **Authentication bugs could allow unauthorized access** - Tests verify hashing and verification
3. **Key derivation bugs could make data unrecoverable** - Tests verify key derivation is deterministic
4. **Validation bugs could allow injection attacks** - Tests verify input sanitization

## Adding New Tests

When adding new features:

1. Add tests BEFORE implementing features (Test-Driven Development)
2. Test both success and failure cases
3. Test edge cases (empty strings, max lengths, special characters)
4. Test error handling
5. Aim for >80% code coverage on security-critical functions

## Continuous Integration

To run tests automatically on every commit:

```bash
# Add to .git/hooks/pre-commit
#!/bin/bash
echo "Running unit tests..."
python -m unittest discover tests/ -v
if [ $? -ne 0 ]; then
    echo "Tests failed! Commit aborted."
    exit 1
fi
```

## Test Dependencies

- Python 3.8+
- bcrypt
- cryptography
- Optional: pytest (for advanced features)
