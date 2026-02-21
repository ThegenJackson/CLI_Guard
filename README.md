#	CLI Guard
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)

CLI Guard is a secure, terminal-based password manager with encryption and multi-user support. Built with Python and using industry-standard cryptographic practices, CLI Guard provides a modern TUI (Terminal User Interface) for managing your passwords safely.

---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Architecture Overview](#architecture-overview)
  - [Project Structure](#project-structure)
  - [Component Responsibilities](#component-responsibilities)
- [Security Architecture](#security-architecture)
  - [Authentication System](#authentication-system)
  - [Encryption Design](#encryption-design)
  - [Session Management](#session-management)
  - [Security Features](#security-features)
- [Database Schema](#database-schema)
- [Development Roadmap](#development-roadmap)
- [CLI Guard Password Generator](#cli-guard-password-generator)
- [Contributing](#contributing)
- [Database Management System](#database-management-system)

---

## Features

- 🔐 **Secure Authentication** - Bcrypt password hashing with 3-attempt lockout
- 🔒 **Strong Encryption** - Fernet symmetric encryption for stored passwords
- 👥 **Multi-user Support** - Separate encrypted password vaults per user
- 💻 **Modern TUI** - Clean curses-based terminal interface
- 🗄️ **SQLite Backend** - Reliable local database storage
- 🔑 **Session-based Keys** - Encryption keys never stored on disk
- 📊 **Password Management** - Create, view, edit, delete, search, and sort passwords

---

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/CLI_Guard.git
cd CLI_Guard
```

2. Install required dependencies:
```bash
pip install bcrypt cryptography
```

3. Run the TUI application:
```bash
python CLI_Guard_TUI.py
```

---

## Prerequisites

- **Python 3.8+** (type hints and modern features)
- **bcrypt** - Password hashing
- **cryptography** - Fernet encryption
- **curses** - TUI (included in Python standard library on Unix/Linux/macOS)
- **SQLite3** - Database (included in Python standard library)

### Windows Users
Windows requires the `windows-curses` package:
```bash
pip install windows-curses
```

---

## Quick Start

1. **First Run**: Launch the application and create a new user
2. **Sign In**: Enter your username and password
3. **Main Menu**: Access password management features
4. **Add Passwords**: Store encrypted credentials
5. **Sign Out**: Safely close your session


---

## Architecture Overview

CLI Guard follows a layered architecture separating the TUI, business logic, and data access layers.

### Project Structure

```
CLI_Guard/
├── CLI_Guard_TUI.py            # Terminal User Interface (curses-based)
├── CLI_Guard.py                # Business Logic Layer
├── CLI_SQL/
│   ├── CLI_Guard_SQL.py        # Data Access Layer
│   └── CLI_Guard_DB.db         # SQLite Database
├── CG/
│   └── CGPG/
│       └── CGPG.py             # Password Generator (AWS Lambda)
├── Deprecated/
│   ├── CLI_Guard_TUI_Deprecated.py  # Old TUI (for reference)
│   └── CLI_Guard_Deprecated.py      # Old business logic (for reference)
└── README.md
```

### Component Responsibilities

#### 1. **CLI_Guard_TUI.py** (Presentation Layer)
- Manages the terminal user interface using Python's curses library
- Handles user input and navigation
- Displays windows, panels, and forms
- Calls business logic functions for operations
- **Key Functions:**
  - `signIn()` - User selection and sign-in flow
  - `authSignIn()` - Password authentication with attempt tracking
  - `createUser()` - New user registration
  - `mainMenu()` - Main application menu
  - `passwordManagement()` - Password CRUD operations

#### 2. **CLI_Guard.py** (Business Logic Layer)
- Implements core security operations
- Manages user sessions and encryption keys
- Provides authentication and encryption services
- **Key Functions:**
  - `hashPassword()` - Bcrypt password hashing
  - `deriveEncryptionKey()` - PBKDF2 key derivation
  - `authUser()` - Authenticate user credentials
  - `startSession()` / `endSession()` - Session lifecycle management
  - `encryptPassword()` / `decryptPassword()` - Password encryption operations

#### 3. **CLI_Guard_SQL.py** (Data Access Layer)
- Handles all database operations
- Executes parameterized SQL queries (SQL injection protection)
- Manages user and password records
- **Key Functions:**
  - `insertUser()` / `updateUserPassword()` / `deleteUser()` - User management
  - `insertData()` / `updateData()` / `deleteData()` - Password management
  - `queryData()` - Flexible data retrieval
  - `lockUser()` / `isUserLocked()` - Account lockout management
  - `exportDatabase()` / `importDatabase()` - Database migration

---

## Security Architecture

CLI Guard implements a defense-in-depth security model with multiple layers of protection.

### Authentication System

#### **Dual-Key Cryptographic Approach**

CLI Guard uses a sophisticated dual-key system that separates authentication from encryption:

1. **Bcrypt Hash** (Authentication)
   - User passwords are hashed using bcrypt with automatic salt generation
   - Stored in database as BLOB for type safety
   - Used solely for verifying user identity
   - **Never used for encryption** (bcrypt output is not suitable for encryption keys)

2. **PBKDF2-Derived Fernet Key** (Encryption)
   - Derived from user's plaintext password using PBKDF2-HMAC-SHA256
   - 100,000 iterations for computational hardness
   - Per-user salt (stored in database) ensures unique keys even if passwords match
   - Generates a 32-byte key, base64-encoded for Fernet compatibility
   - **Never stored on disk** - regenerated each session from password

#### **Why This Approach?**

**Problem**: Bcrypt hashes cannot be used directly as encryption keys because:
- Bcrypt output format is incompatible with Fernet (which requires 32-byte URL-safe base64)
- Bcrypt is designed for password verification, not key derivation
- Bcrypt hashes vary in length and include metadata

**Solution**: Use bcrypt for authentication, PBKDF2 for key derivation
- ✅ Secure password storage (bcrypt's strength)
- ✅ Proper encryption key generation (PBKDF2's purpose)
- ✅ Keys never stored (derived on-demand from password)
- ✅ User cannot access data without correct password

### Encryption Design

#### **Fernet Symmetric Encryption**

- **Algorithm**: AES-128 in CBC mode with HMAC-SHA256 authentication
- **Key Source**: PBKDF2-derived from user's password
- **Implementation**: Python's `cryptography` library (Fernet)
- **Key Rotation**: Each user has a unique encryption key (derived from their password)

#### **Data Flow**

**Storing a Password:**
```
User enters password → PBKDF2 derives Fernet key → Encrypt password → Store in DB
```

**Retrieving a Password:**
```
User signs in → PBKDF2 derives Fernet key → Query DB → Decrypt password → Display
```

**Key Properties:**
- Encryption key exists only in memory during active session
- Different users = different encryption keys (even for same stored password)
- Lost master password = permanently lost data (by design)

### Session Management

#### **Session Lifecycle**

1. **Session Start** (`startSession()`)
   - Called after successful authentication
   - Derives encryption key from user's password using PBKDF2
   - Stores key in module-level variable (`_session_encryption_key`)
   - Stores username in module-level variable (`_session_user`)

2. **Active Session**
   - Encryption key available for encrypt/decrypt operations
   - All password operations use the session key
   - Key exists only in process memory (not on disk)

3. **Session End** (`endSession()`)
   - Called on sign-out or application exit
   - Clears encryption key from memory (set to `None`)
   - Clears username from memory
   - Ensures sensitive data is removed from memory

#### **Security Implications**

- **Session Isolation**: Each session is independent; keys are never reused
- **Memory-Only Storage**: Encryption keys never touch the filesystem
- **Automatic Cleanup**: Keys cleared on sign-out/exit
- **No Key Persistence**: User must re-enter password each session

### Security Features

#### **Account Lockout Protection**
- **3-Attempt Limit**: Maximum 3 failed login attempts
- **24-Hour Lockout**: Account locked until next day after 3 failures
- **Attempt Tracking**: Real-time counter displayed to user
- **Database Persistence**: Lockout status stored in `last_locked` column
- **Pre-Check**: Locked accounts cannot attempt authentication

#### **SQL Injection Protection**
- **Parameterized Queries**: All SQL uses `?` placeholders
- **No String Interpolation**: User input never directly concatenated into SQL
- **Type Safety**: Database schema enforces data types (TEXT, BLOB)

#### **Cryptographic Standards**
- **Bcrypt**: Industry-standard password hashing (adaptive cost factor)
- **PBKDF2**: NIST-recommended key derivation (100,000 iterations)
- **Fernet**: Authenticated encryption (AES-128 + HMAC-SHA256)
- **Random Salt**: Bcrypt generates unique salt per password

#### **Security Model**

CLI Guard makes every reasonable effort to be cryptographically secure — master passwords are hashed with bcrypt, secrets are encrypted with Fernet (AES-128-CBC + HMAC-SHA256), and encryption keys are derived via PBKDF2 and never stored on disk.

As a locally-hosted application, CLI Guard's security model places responsibility on the operator to secure the hosting environment. The host machine is the primary security boundary — untrusted parties should not have direct access. This is the same trust model used by tools like `pass`, `gpg-agent`, and local SSH key storage.

For a detailed discussion of threat assumptions and design trade-offs, see the [Security Model and Threat Assumptions](TECH_SPEC.md#security-model-and-threat-assumptions) section in the technical specification.

---

## Database Schema

### Tables

#### **users**
```sql
CREATE TABLE users (
    user TEXT NOT NULL UNIQUE PRIMARY KEY,
    user_pw BLOB NOT NULL,                    -- Bcrypt hash (binary data)
    user_last_modified TEXT NOT NULL,
    last_locked TEXT                          -- NULL or date (YYYY-MM-DD)
);
```

**Design Notes:**
- `user_pw` is BLOB to properly store binary bcrypt hashes
- `last_locked` tracks account lockout status
- `user` is unique to prevent duplicate accounts

#### **passwords**
```sql
CREATE TABLE passwords (
    user TEXT NOT NULL,
    category TEXT NOT NULL,
    account TEXT NOT NULL,
    username TEXT NOT NULL,
    password TEXT NOT NULL,                   -- Fernet-encrypted password
    last_modified TEXT NOT NULL,
    FOREIGN KEY (user) REFERENCES users(user) ON DELETE NO ACTION ON UPDATE NO ACTION
);
```

**Design Notes:**
- `password` column stores Fernet-encrypted passwords as base64 strings
- Foreign key ensures referential integrity with users
- No encryption key stored (derived from user's password)
- `ON DELETE NO ACTION` prevents accidental user deletion

### Views

#### **vw_users**
```sql
CREATE VIEW vw_users AS SELECT * FROM users;
```

#### **vw_passwords**
```sql
CREATE VIEW vw_passwords AS SELECT * FROM passwords;
```

**Purpose:** Views provide abstraction layer for potential future schema changes

---

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with type hints and docstrings
4. Test thoroughly with the TUI application
5. Commit with descriptive messages
6. Push to your fork and submit a pull request

### Code Standards

- **Type Hints**: Use Python type hints for all function signatures
- **Docstrings**: Google-style docstrings for all public functions
- **Security**: Never log passwords or encryption keys
- **SQL**: Always use parameterized queries
- **Error Handling**: Catch specific exceptions, log to `Logs.txt`

### Key Areas for Contribution

- Password generation features (scrambler, random, passphrase)
- Password strength analysis
- Export/import improvements
- Additional encryption algorithms
- Mobile/web interface
- Multi-factor authentication
- Password sharing features

---

## Database Management System
-	SQLite Studio \
	https://sqlitestudio.pl/ \
	https://www.sqlite.org/docs.html


### Development Roadmap

#### ✅ Completed
- [x] **Authentication System** - Bcrypt + PBKDF2 implementation
- [x] **Session Management** - Secure key handling
- [x] **Database Schema** - BLOB-based user password storage
- [x] **Account Lockout** - 3-attempt limit with 24-hour lockout
- [x] **TUI Framework** - Curses-based interface structure
- [x] **User Sign-In/Sign-Out** - Complete authentication flow
- [x] **User Creation** - New user registration

#### 🚧 In Progress
- [ ] **Password Management** - Full CRUD operations in TUI
  - [ ] Create password with encryption
  - [ ] View decrypted passwords
  - [ ] Edit existing passwords
  - [ ] Delete passwords
  - [ ] Search passwords
  - [ ] Sort passwords

#### 📋 Planned Features
- [ ] **CLI Guard Password Generator**
  - [ ] Word scrambler (2+ words with customization)
  - [ ] Random password generator
  - [ ] Passphrase generator
  - [ ] Integration with TUI
- [ ] **Password Strength Analysis**
  - [ ] Strength meter
  - [ ] Breach checking (Have I Been Pwned API)
  - [ ] Duplicate detection
- [ ] **Database Migration Tools**
  - [ ] Import from CSV/JSON
  - [ ] Export to CSV/JSON
  - [ ] Database backup automation
- [ ] **Local Web Application**
  - [ ] Flask/FastAPI backend
  - [ ] Modern web UI
  - [ ] Same security architecture
- [ ] **Advanced Features**
  - [ ] Password history tracking
  - [ ] Secure password sharing
  - [ ] Two-factor authentication (TOTP)
  - [ ] Biometric authentication support

### Process Flowchart
![Flowchart](/CG/flowchart.svg)


### CLI Guard Password Generator
:warning: :warning: Currently In Development :warning: :warning:

The CLI Guard Password Generator is a serverless web application deployed on AWS that generates secure passwords using word scrambling techniques.

#### Web Application
🔗 **Live Demo:** https://prod.d2px0taen1p9zb.amplifyapp.com/

#### Features
- Word-based password generation
- Character substitution (a→@, e→3, etc.)
- Capitalization patterns (every 3rd letter)
- AWS Lambda backend for processing
- DynamoDB logging

#### AWS Architecture
![AWS-CGPG](CG/CGPG/AWS_CGPG.svg)

**Components:**
- **AWS Amplify** - Static web hosting
- **AWS Lambda** - Serverless password generation logic
- **Amazon DynamoDB** - Usage logging
- **API Gateway** - RESTful API endpoint

---

## Libraries and Packages

### Core Dependencies

#### **bcrypt** (`pip install bcrypt`)
- **Purpose**: Secure password hashing for authentication
- **Usage**: `CLI_Guard.hashPassword()`
- **Version**: 4.0+
- **Why**: Industry-standard adaptive hashing with automatic salting

#### **cryptography** (`pip install cryptography`)
- **Purpose**: Fernet symmetric encryption for passwords
- **Usage**: `CLI_Guard.encryptPassword()` / `decryptPassword()`
- **Version**: 41.0+
- **Why**: Well-tested, NIST-approved algorithms (AES + HMAC)

#### **curses** (Python Standard Library)
- **Purpose**: Terminal User Interface (TUI)
- **Usage**: `CLI_Guard_TUI.py`
- **Platform**: Unix/Linux/macOS built-in, Windows requires `windows-curses`
- **Why**: Native terminal graphics without external dependencies

#### **sqlite3** (Python Standard Library)
- **Purpose**: Embedded database
- **Usage**: `CLI_Guard_SQL.py`
- **Why**: Zero-configuration, file-based, ACID-compliant

### Development Dependencies

```bash
# Install all required packages
pip install bcrypt cryptography

# Windows only - curses support
pip install windows-curses
```

### Optional Tools

- **SQLite Studio** - GUI database browser: https://sqlitestudio.pl/
- **DB Browser for SQLite** - Alternative GUI: https://sqlitebrowser.org/

---

## Technical Details

### File Locations

- **Database**: `CLI_SQL/CLI_Guard_DB.db`
- **Logs**: `Logs.txt` (created in project root)
- **Configuration**: None (currently hardcoded)

### Important Constants

**PBKDF2 Configuration** (`CLI_Guard.py`):
```python
salt = os.urandom(32)              # Per-user salt (generated at user creation, stored in DB)
iterations = 100000                # PBKDF2 iterations
key_length = 32                    # Fernet key size (bytes)
```

**Security Note**: Each user gets a unique cryptographically random 32-byte salt, generated at account creation and stored in the `encryption_salt` column of the users table. This ensures that even if two users choose the same master password, their derived encryption keys will be different. Existing users created before per-user salts are automatically migrated on first login — their secrets are re-encrypted under a new random salt.

### Performance Considerations

- **Bcrypt**: Intentionally slow (~100ms per hash) to resist brute-force
- **PBKDF2**: 100,000 iterations (~50-100ms) for key derivation
- **Fernet**: Fast symmetric encryption (~1ms per operation)
- **Database**: SQLite performs well for single-user scenarios

### Logging

All operations are logged to `Logs.txt` with timestamps:
- User creation/deletion
- Password operations (account names only, never passwords)
- Database operations (success/failure)
- Authentication attempts (failures only)
- Account lockouts

**Format**: `[YYYY-MM-DD HH:MM:SS] MESSAGE`

---

## License

This project is open-source. Please see LICENSE file for details.

---

## Support

For issues, questions, or contributions, please open an issue on GitHub.

**Security Issues**: If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue.
