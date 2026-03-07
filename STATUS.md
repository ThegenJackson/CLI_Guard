# CLI Guard - Project Status

> Last updated: 2026-03-07

## Quick Summary
CLI Guard is a locally-hosted secret manager for scripting and automation workflows (like a lightweight Azure Key Vault). The foundation is complete: database layer, business logic (encryption/auth), TUI for manual management, CLI for scripting, and token-based authentication. Password generation is implemented. However, **major feature blades are not yet built** — User Management, Database Migration/Export, and Settings are all still needed before the application is production-ready.

## Development Phases

| Phase | Description | Status |
|-------|------------|--------|
| A | Database layer, business logic, encryption/hashing | Done |
| B | TUI for manual secret management + visual testing | Done |
| C | CLI/scripting interface (non-interactive secret retrieval) | Done |
| C.1 | Token-based CLI authentication (session + service tokens) | Done |
| D | Polish (password generation, clipboard, session timeout) | **In Progress** |
| E | Feature blades (user management, database tools, settings) | Not Started |

## What's Done

### Phase A: Foundation
- [x] SQLite database with users and passwords tables + views
- [x] Bcrypt password hashing for authentication
- [x] Fernet encryption (AES-128-CBC) for stored secrets
- [x] PBKDF2-HMAC-SHA256 key derivation (100k iterations, per-user salts)
- [x] Session management (encryption key in memory only)
- [x] Database connection management with auto-reconnect
- [x] Input validation module (username, password, text fields, token names)
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
- [x] Composable search+sort (search to reduce scope, then sort on top)
- [x] Clear filters with ESC
- [x] Contextual help tips in message_window

### Phase C: CLI/Scripting Interface
- [x] `cli-guard get` — retrieve a secret by account/username (non-interactive)
- [x] `cli-guard list` — list available secrets for a user
- [x] `cli-guard add` / `update` / `delete` — full CRUD via CLI
- [x] Output to stdout for `$()` capture, `--json` for structured output
- [x] Convenience functions in CLI_Guard.py (Python importable interface)
- [x] Exit codes: 0=success, 1=error, 2=auth failure, 3=not found, 4=db error, 5=token expired
- [x] `delete --force` safety flag to prevent accidental deletions
- [x] Input validation on all CLI fields
- [x] DB_PATH fix — works when invoked from any working directory
- [x] Database seeder (`seed_database.py`) with Faker for test data

### Phase C.1: Token-Based Authentication
- [x] `cli-guard signin` — create session token (1-hour TTL, password via getpass/env/stdin)
- [x] `cli-guard signout` — invalidate session token
- [x] `cli-guard token create` — create long-lived service account token
- [x] `cli-guard token list` — list service tokens (metadata only)
- [x] `cli-guard token revoke` — revoke a service token by ID
- [x] Key wrapping — encryption key encrypted by token-derived key (neither alone is useful)
- [x] Session tokens stored in `~/.cli-guard/sessions/` with 0o600 permissions
- [x] Service tokens stored in DB (bcrypt-hashed, wrapped key, revocation flag)
- [x] `--password` flag removed from all data commands (get, list, add, update, delete)
- [x] Auth via `CLIGUARD_SESSION` or `CLIGUARD_SERVICE_TOKEN` env vars
- [x] Token expiry and revocation checks
- [x] `startSessionFromKey()` for token-based session initialization

### Phase D: Polish (In Progress)
- [x] Password scramble — leet-speak substitution + case randomization (`password_generator.scramble_password`)
- [x] Random password generation — cryptographically random from shell-safe pool (`password_generator.generate_random`)
- [x] Passphrase generation — 4 random words from 4,096-word dictionary, random capitalization (~27%), random separators (~61.8 bits entropy)
- [x] TUI integration — all three generators wired into Create Password and Update Password popups
- [ ] Clipboard auto-clear after timeout
- [ ] Session timeout for security
- [ ] Password strength indicator in create/update forms

### Infrastructure
- [x] 213 unit tests passing (business logic + validation + CLI parser + token manager + password generator)
- [x] Project documentation (CLAUDE.md, PRD.md, TECH_SPEC.md, STATUS.md)
- [x] Claude Code hooks (branch protection, dangerous command blocking, pre-commit tests)
- [x] Dynamic timestamp generation (no stale dates)
- [x] Popup panel rendering fix (touchwin/refresh pattern)

## What's Not Done

### Phase D: Polish (Remaining)
- [ ] Clipboard auto-clear after timeout
- [ ] Session timeout for security
- [ ] Password strength indicator in create/update forms

### Phase E: Feature Blades (Full Development Needed)
These are entire feature areas that have **not been started**. Each requires UI, business logic, and potentially database changes.

#### User Management (Not Started)
- [ ] Change master password — re-encrypt all secrets with new derived key
- [ ] Delete account — cascade delete all secrets, tokens, and user record
- [ ] View/edit user profile (username display, creation date, etc.)
- [ ] TUI menu integration for user management options

#### Database Tools (Not Started)
- [ ] Database export — backup secrets to encrypted file
- [ ] Database import — restore from backup file
- [ ] Database migration tooling — schema versioning for upgrades
- [ ] Data integrity checks

#### Settings (Not Started)
- [ ] Configurable session timeout duration
- [ ] Configurable clipboard clear timeout
- [ ] Default password generation preferences (length, type)
- [ ] TUI settings screen
- [ ] Settings persistence (config file or database)

#### Logging (Not Started)
Currently logs to a plaintext file on disk (`Logs.txt`). Planned enhancements:
- [ ] Configurable log destination — plaintext file (current default) or remote Syslog server
- [ ] Syslog support — forward logs to a specified Syslog server via UDP (514/udp) or TCP (514/tcp)
- [ ] Log level configuration (e.g., AUTH only vs. all categories)
- [ ] Log rotation / size management for disk-based logging

## Known Bugs
- Keyboard shortcuts for U/D in viewPasswordDetails still use old noutrefresh pattern (lines 1069-1084)
- `createUser()` does not refresh menu_window when hiding popup (uses older code pattern)

## File Sizes (for context)
| File | Lines | Role |
|------|-------|------|
| CLI_Guard_TUI.py | ~2100 | TUI interface |
| CLI_Guard_CLI.py | ~470 | CLI interface |
| CLI_Guard.py | ~440 | Business logic |
| password_generator.py | ~600 | Password generation (scramble, random, passphrase) |
| token_manager.py | ~570 | Token lifecycle (session + service tokens) |
| CLI_Guard_SQL.py | ~530 | Data access |
| validation.py | ~240 | Input validation |
| seed_database.py | ~200 | Database seeder (Faker) |
| logger.py | ~48 | Shared logging |
| test_cli_guard.py | ~290 | Business logic tests |
| test_cli_guard_cli.py | ~270 | CLI parser + auth tests |
| test_password_generator.py | ~200 | Password generator tests |
| test_token_manager.py | ~340 | Token manager tests |
| test_validation.py | ~280 | Validation tests |

## Current Branch
Working on feature branches. PRs merged to `main`.
