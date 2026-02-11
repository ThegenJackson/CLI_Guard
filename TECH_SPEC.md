# CLI Guard - Technical Specification

## System Architecture

CLI Guard uses a multi-interface architecture. Multiple consumers (TUI, CLI, Python import)
share the same business logic and data access layers:

```
┌─────────────────────────┐ ┌─────────────────────────┐
│   CLI_Guard_TUI.py      │ │   CLI_Guard_CLI.py      │
│  (TUI - curses)         │ │  (CLI - argparse)       │
│  For human operators    │ │  For scripts/automation  │
│                         │ │                         │
│ ┌───────┐ ┌──────────┐ │ │ ┌───────┐ ┌──────────┐ │
│ │ Login │ │ Password │ │ │ │ get   │ │ list     │ │
│ │Screen │ │  Table   │ │ │ │secret │ │secrets   │ │
│ └───────┘ └──────────┘ │ │ └───────┘ └──────────┘ │
│         DONE            │ │        PLANNED          │
├─────────────────────────┴─┴─────────────────────────┤
│               validation.py                          │
│          (Input Validation - shared)                 │
├──────────────────────────────────────────────────────┤
│                CLI_Guard.py                          │
│            (Business Logic Layer)                    │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │  Auth    │ │Encryption│ │ Session  │            │
│  │ (bcrypt) │ │ (Fernet) │ │  Mgmt    │            │
│  └──────────┘ └──────────┘ └──────────┘            │
├──────────────────────────────────────────────────────┤
│           CLI_SQL/CLI_Guard_SQL.py                   │
│             (Data Access Layer)                      │
│                                                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐            │
│  │Connection│ │  CRUD    │ │  Query   │            │
│  │  Mgmt    │ │Operations│ │ Builder  │            │
│  └──────────┘ └──────────┘ └──────────┘            │
├──────────────────────────────────────────────────────┤
│              SQLite Database                         │
│           CLI_SQL/CLI_Guard_DB.db                    │
└──────────────────────────────────────────────────────┘
```

### Planned CLI Usage (scripting interface)
```bash
# Retrieve a secret for use in a script (like az keyvault secret show)
DB_PASS=$(cli-guard get --user admin --account "production-db" --field password)

# List all secrets for a user
cli-guard list --user admin

# Use in a pipeline
cli-guard get --user deploy --account "api-key" | curl -H "Authorization: Bearer $(cat -)"
```

```python
# Python import usage
import CLI_Guard
CLI_Guard.startSession("admin", master_password)
secret = CLI_Guard.decryptPassword(encrypted_value)
```

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.12+ | Core language |
| TUI Framework | curses (stdlib) | — | Terminal user interface |
| Database | SQLite3 (stdlib) | — | Local data storage |
| Auth Hashing | bcrypt | 3.2.2 | Master password hashing |
| Encryption | cryptography (Fernet) | 41.0.7 | Password encryption (AES-128-CBC) |
| Key Derivation | hashlib.pbkdf2_hmac (stdlib) | — | Derive encryption key from master password |
| Testing | unittest/pytest | — | Unit tests |

## Cryptography Design

### Authentication Flow
```
User enters password
        │
        ▼
password.encode('utf-8')
        │
        ▼
bcrypt.hashpw(password, salt)  →  stored in DB as BLOB
        │
        ▼
bcrypt.checkpw(attempt, stored_hash)  →  True/False
```

### Encryption Flow
```
User's master password
        │
        ▼
PBKDF2-HMAC-SHA256 (100,000 iterations, fixed salt)
        │
        ▼
32-byte derived key  →  base64 encoded  →  Fernet key
        │                                       │
        │   (key lives in memory only)          │
        ▼                                       ▼
Fernet(key).encrypt(plaintext)    Fernet(key).decrypt(ciphertext)
        │                                       │
        ▼                                       ▼
Stored in DB as TEXT              Displayed in TUI popup
```

**Key design decision:** The encryption key is derived deterministically from the master password using PBKDF2. This means the same password always produces the same key, allowing decryption across sessions without ever storing the key. The key only exists in the `_session_encryption_key` global variable while the user is logged in.

### Security Note on Salt
The current PBKDF2 salt is fixed (`CLI_Guard_Salt_v1_2025`). This is acceptable for a single-user local application, but if multi-device sync is ever added, per-user salts stored in the database would be required.

## Database Schema

### Tables
```sql
CREATE TABLE users (
    user            TEXT PRIMARY KEY,
    user_pw         BLOB NOT NULL,        -- bcrypt hash
    user_last_modified DATE,
    last_locked     DATE                   -- NULL if not locked
);

CREATE TABLE passwords (
    user            TEXT NOT NULL,
    category        TEXT NOT NULL,
    account         TEXT NOT NULL,
    username        TEXT NOT NULL,
    password        TEXT NOT NULL,          -- Fernet-encrypted string
    last_modified   DATE,
    FOREIGN KEY (user) REFERENCES users(user)
);
```

### Views
```sql
CREATE VIEW vw_users AS SELECT * FROM users;
CREATE VIEW vw_passwords AS SELECT * FROM passwords;
```

The data access layer queries views (`vw_passwords`, `vw_users`) rather than tables directly. This allows future flexibility (e.g., adding computed columns or filtering) without changing application code.

## TUI Window Layout

```
┌─────────────────────────────────────────────┐
│              answer_window (h=5)             │
├────────────┬────────────────────────────────┤
│            │                                │
│ menu_window│      content_window            │
│  (w=21)    │    (remaining width)           │
│            │                                │
│ MAIN MENU  │  [Create] [Search] [Sort]      │
│ Passwords  │  ┌─────────────────────────┐   │
│ User Mgmt  │  │ Idx Category Account .. │   │
│ Migrate DB │  │  1  Social   Twitter .. │   │
│ Settings   │  │  2  Email    Gmail   .. │   │
│ Sign Out   │  └─────────────────────────┘   │
│ Quit       │                                │
│            │                                │
│ User: john │                                │
├────────────┴────────────────────────────────┤
│           message_window (h=5)              │
└─────────────────────────────────────────────┘

Popup panels (centered overlay, 60x12):
┌──────────────────────────────────────┐
│ | Create New Password |              │
│                                      │
│ Category:    [____________]          │
│ Account:     [____________]          │
│ Username:    [____________]          │
│ Password:    [************]          │
│                                      │
│ [Scramble] [Random] [Passphrase]     │
│                                      │
│        [Create]  [Cancel]            │
└──────────────────────────────────────┘
```

## Session Management

```
Sign In  →  authUser() verifies bcrypt hash
         →  startSession() derives Fernet key, stores in memory
         →  _session_encryption_key = derived key
         →  _session_user = username

Sign Out →  endSession() clears both globals to None
         →  Encryption key no longer in memory
```

## Input Validation Rules

| Field | Min | Max | Rules |
|-------|-----|-----|-------|
| Username (auth) | 3 | 50 | Alphanumeric + `._-`, starts with letter/number |
| Master Password | 8 | 128 | Must have upper + lower + digit + special |
| Category | 1 | 50 | No control characters |
| Account | 1 | 100 | No control characters |
| Username (password) | 1 | 100 | No control characters |
| Password (stored) | 1 | 500 | No control characters |
| Search term | 1 | 100 | No control characters |

## SQL Injection Prevention
Column names in dynamic queries are validated against a whitelist:
```python
ALLOWED_COLUMNS = {'category', 'account', 'username', 'last_modified'}
ALLOWED_SORT_ORDERS = {'ascending', 'descending'}
```
Any column name not in this set raises a `ValueError` before reaching the database.
