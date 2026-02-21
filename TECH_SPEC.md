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
│         DONE            │ │         DONE            │
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

### CLI Usage — Interactive (session tokens)
```bash
# Sign in once — password prompt appears interactively (never in process list)
export CLIGUARD_SESSION=$(python3 CLI_Guard_CLI.py signin --user admin)

# Use freely for 1 hour — no password needed
DB_PASS=$(python3 CLI_Guard_CLI.py get --user admin --account "production-db")
python3 CLI_Guard_CLI.py list --user admin --json

# Add a new secret
python3 CLI_Guard_CLI.py add --user admin --category DB --account prod-db \
    --secret-username dbadmin --secret "P@ssw0rd!"

# Update a secret
python3 CLI_Guard_CLI.py update --user admin --account prod-db --new-secret "NewP@ss!"

# Delete a secret (--force required)
python3 CLI_Guard_CLI.py delete --user admin --account prod-db --force

# Sign out when done
python3 CLI_Guard_CLI.py signout
unset CLIGUARD_SESSION
```

### CLI Usage — Automation (service tokens)
```bash
# One-time setup by admin (token shown once — save it in CI/CD secrets)
python3 CLI_Guard_CLI.py token create --user admin --name "ci-pipeline" --expires-days 365

# In CI/CD pipeline — no password, no interactive prompt
export CLIGUARD_SERVICE_TOKEN="cg_svc_Xk9mQ2a8b7..."
DB_PASS=$(python3 CLI_Guard_CLI.py get --user admin --account prod-db)

# List and revoke tokens
python3 CLI_Guard_CLI.py token list --user admin --json
python3 CLI_Guard_CLI.py token revoke --user admin --token-id cg_svc_abc123def456

# Check exit codes in scripts
python3 CLI_Guard_CLI.py get --user admin --account nonexistent
echo $?  # prints 3 (EXIT_NOT_FOUND)
```

### Python Import Usage
```python
import CLI_Guard

CLI_Guard.startSession("admin", master_password)
secret = CLI_Guard.getSecret("admin", "production-db")  # returns dict with decrypted password
secrets = CLI_Guard.getSecrets("admin")                  # returns list of dicts
CLI_Guard.endSession()
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

### Token-Based Authentication (Key Wrapping)
```
SIGNIN (create session token):
  password → PBKDF2 → encryption_key
  token = secrets.token_urlsafe(32)
  wrapping_key = PBKDF2(token, wrapping_salt)       ← different salt from main key
  wrapped_blob = Fernet(wrapping_key).encrypt(encryption_key)
  Store wrapped_blob in ~/.cli-guard/sessions/{user}.json
  Return token to user (for CLIGUARD_SESSION env var)

SUBSEQUENT COMMAND (use session/service token):
  token (from env var) → PBKDF2 → wrapping_key
  encryption_key = Fernet(wrapping_key).decrypt(wrapped_blob)
  startSessionFromKey(user, encryption_key) → can decrypt secrets
```

**Key design decision:** The encryption key is encrypted ("wrapped") using a second key derived from the token itself. Neither the token alone (held by the user) nor the wrapped blob alone (stored on disk/DB) is useful — you need both. This is the same principle behind LUKS disk encryption.

### Auth Priority Order (data commands)
```
1. CLIGUARD_SERVICE_TOKEN env var   → service account (automation)
2. CLIGUARD_SESSION env var         → session token (interactive)
3. No auth found                    → error with helpful message
```

No `--password` flag on data commands. Passwords are only used during `signin` and `token` commands.

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

CREATE TABLE service_tokens (
    token_id        TEXT PRIMARY KEY,       -- cg_svc_ + first 12 chars of SHA-256
    user            TEXT NOT NULL,
    name            TEXT NOT NULL,           -- human label (e.g. "ci-pipeline")
    token_hash      BLOB NOT NULL,          -- bcrypt hash of full token
    wrapped_key     TEXT NOT NULL,           -- encryption key wrapped by token-derived key
    created_at      TEXT NOT NULL,
    expires_at      TEXT,                    -- NULL = never expires
    last_used       TEXT,
    revoked         INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user) REFERENCES users(user)
);
```

### Views
```sql
CREATE VIEW vw_users AS SELECT * FROM users;
CREATE VIEW vw_passwords AS SELECT * FROM passwords;
CREATE VIEW vw_service_tokens AS SELECT * FROM service_tokens;
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
