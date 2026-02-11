# CLI Guard - Project Status

> Last updated: 2026-02-12

## Quick Summary
CLI Guard is a locally-hosted secret manager for scripting and automation workflows (like a lightweight Azure Key Vault). The foundation is built: database layer, business logic (encryption/auth), and a TUI for manual management. Next milestone is the CLI/scripting interface so scripts can retrieve secrets non-interactively.

## Development Phases

| Phase | Description | Status |
|-------|------------|--------|
| A | Database layer, business logic, encryption/hashing | Done |
| B | TUI for manual secret management + visual testing | Done |
| C | CLI/scripting interface (non-interactive secret retrieval) | **Next** |
| D | Polish (password generation, clipboard, session timeout) | Planned |

## What's Done

### Phase A: Foundation
- [x] SQLite database with users and passwords tables + views
- [x] Bcrypt password hashing for authentication
- [x] Fernet encryption (AES-128-CBC) for stored secrets
- [x] PBKDF2-HMAC-SHA256 key derivation (100k iterations)
- [x] Session management (encryption key in memory only)
- [x] Database connection management with auto-reconnect
- [x] Input validation module (username, password, text fields)
- [x] SQL injection prevention (column name whitelists)
- [x] Shared logging module (AUTH, DATABASE, TUI, ERROR)

### Phase B: TUI
- [x] User creation with bcrypt-hashed master passwords
- [x] Sign in / sign out with session management
- [x] Account lockout after 3 failed attempts
- [x] Create encrypted secret entries
- [x] View all secrets in scrollable table
- [x] View decrypted secret details in popup
- [x] Update secret entries (pre-filled form)
- [x] Delete secret entries (with Y/N confirmation)
- [x] Search secrets by category/account/username
- [x] Sort secrets by any column (ascending/descending)
- [x] Clear filters with ESC

### Infrastructure
- [x] 55 unit tests passing (business logic + validation)
- [x] Project documentation (CLAUDE.md, PRD.md, TECH_SPEC.md, STATUS.md)
- [x] Claude Code hooks (branch protection, dangerous command blocking, pre-commit tests)
- [x] Dynamic timestamp generation (no stale dates)
- [x] Popup panel rendering fix (touchwin/refresh pattern)

## What's Not Done

### Phase C: CLI/Scripting Interface (Next Priority)
- [ ] `cli-guard get` — retrieve a secret by account/username (non-interactive)
- [ ] `cli-guard list` — list available secrets for a user
- [ ] Authentication via argument or stdin (for piping)
- [ ] Output to stdout for script consumption
- [ ] Python importable interface

### Phase D: Polish
- [ ] Secret generation (scramble, random, passphrase) — buttons exist but are placeholders
- [ ] User management — change master password, delete account
- [ ] Database export/import — backup and restore
- [ ] Clipboard auto-clear after timeout
- [ ] Session timeout for security
- [ ] Password strength indicator in create/update forms

## Known Bugs
- Keyboard shortcuts for U/D in viewPasswordDetails still use old noutrefresh pattern (lines 1069-1084)
- `createUser()` does not refresh menu_window when hiding popup (uses older code pattern)
- Secret generation buttons in create/update forms are hardcoded placeholders

## File Sizes (for context)
| File | Lines | Role |
|------|-------|------|
| CLI_Guard_TUI.py | ~2100 | TUI interface |
| CLI_Guard_SQL.py | ~460 | Data access |
| validation.py | 216 | Input validation |
| CLI_Guard.py | ~210 | Business logic |
| logger.py | ~40 | Shared logging |
| test_validation.py | 237 | Validation tests |
| test_cli_guard.py | 191 | Business logic tests |

## Current Branch
Working on `main`. Feature branches should be used for future work.
