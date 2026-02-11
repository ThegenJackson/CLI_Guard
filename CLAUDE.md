# CLI Guard - Project Instructions for Claude

## Project Overview
CLI Guard is a lightweight, locally-hosted secret manager for scripting and automation workflows.
Think Azure Key Vault, but self-hosted and offline — for airgapped systems, container clusters, and internal networks.

**Primary purpose:** Scripts and automations retrieve encrypted secrets at runtime (CLI/scripting interface — being built next).
**Secondary purpose:** TUI for human operators to manually manage the secret store.

**Repository:** CLI_Guard
**Language:** Python 3.12+
**TUI entry point:** `CLI_Guard_TUI.py` (run with `python3 CLI_Guard_TUI.py`)
**CLI entry point:** Planned — will call the same `CLI_Guard.py` business logic functions

## Architecture
Three-tier architecture — each layer only talks to the one below it.
Multiple interfaces (TUI, CLI, Python import) all share the same business logic and data layers:

```
CLI_Guard_TUI.py      (TUI Interface)    → curses windows, panels, user input
CLI_Guard_CLI.py      (CLI Interface)    → non-interactive scripting access (planned)
        ↓                    ↓
CLI_Guard.py          (Business Logic)   → encryption, hashing, session management
validation.py         (Shared)           → input validation
        ↓
CLI_SQL/CLI_Guard_SQL.py (Data Access)   → SQLite queries, connection management
```

**Do not** let interfaces call SQL functions directly. Always go through CLI_Guard.py for business logic.

## File Structure
```
CLI_Guard/
├── CLI_Guard_TUI.py          # TUI interface (curses) - for human operators
├── CLI_Guard.py               # Business logic (encryption, auth, sessions)
├── validation.py              # Input validation utilities
├── logger.py                  # Shared logging (AUTH, DATABASE, TUI, ERROR)
├── CLI_SQL/
│   ├── CLI_Guard_SQL.py       # Database access layer
│   └── CLI_Guard_DB.db        # SQLite database (DO NOT commit test data)
├── tests/
│   ├── test_cli_guard.py      # Tests for business logic
│   └── test_validation.py     # Tests for validation
├── Deprecated/                # Old code kept for reference only
├── Logs.txt                   # Runtime debug log
├── STATUS.md                  # Current project state (read this first each session)
├── PRD.md                     # Product requirements
└── TECH_SPEC.md               # Technical specification
```

## Code Style Rules
- Use type hints on all function signatures
- Use docstrings on all public functions (Args, Returns, Raises)
- Follow existing naming conventions: `snake_case` for functions/variables, `UPPER_CASE` for constants
- Keep functions focused — one function, one responsibility
- Never use bare `except:` — always catch specific exceptions
- Delete dead code rather than commenting it out
- Do not add features, refactor code, or make improvements beyond what was asked

## Security Rules (Critical)
- **Never** store encryption keys on disk — keys exist only in memory during a session
- **Never** log plaintext passwords or encryption keys
- **Always** use parameterized queries (?) for SQL — never f-strings for user data
- **Always** validate column names against `ALLOWED_COLUMNS` whitelist before use in SQL
- **Always** validate user input before passing to database or encryption functions
- Encryption: Fernet (AES-128-CBC + HMAC-SHA256) via `cryptography` library
- Auth hashing: bcrypt via `bcrypt` library
- Key derivation: PBKDF2-HMAC-SHA256 with 100,000 iterations

## Curses/TUI Patterns
- All popup panels must call this pattern when hiding to prevent rendering artifacts:
  ```python
  popup_panel.hide()
  curses.panel.update_panels()
  menu_window.touchwin()
  menu_window.refresh()
  content_window.touchwin()
  content_window.refresh()
  ```
- Never use `noutrefresh()` alone when hiding popups — it doesn't force a full redraw
- All popup functions receive the full `windows` dict and access `menu_window` + `content_window` for cleanup
- Password fields must be masked with `*` characters in the TUI

## Testing
- Run tests: `python3 -m pytest tests/ -v` or `python3 -m unittest discover tests/`
- 55 tests currently passing (20 business logic, 35 validation)
- Write tests for any new business logic or validation functions
- TUI functions are not unit-tested (curses is hard to mock) — test manually

## Git Workflow
- Work on feature branches, not directly on `main`
- Commit frequently — after each logical unit of work
- Write descriptive commit messages explaining *why*, not just *what*
- Never commit `.env`, credentials, or the database file with real user data

## Common Pitfalls (Learned from Experience)
- Using `break` in the passwordManagement while loop exits the entire function — use `continue` or let the loop naturally re-iterate to refresh the password list
- The `table` parameter in SQL queries builds view names as `vw_{table}` — this is by design for the database views
- Timestamps must be generated dynamically via `get_today()` / `get_now_timestamp()` — never cache them at module level
- The popup_panel is shared across all popup functions — always hide it before returning
