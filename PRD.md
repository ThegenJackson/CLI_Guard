# CLI Guard - Product Requirements Document (PRD)

## Background
CLI Guard is a lightweight, locally-hosted secret manager designed primarily for scripting and automation workflows. Think of it as a self-hosted alternative to Azure Key Vault — but instead of making API calls to a cloud service, scripts and automations query a local encrypted SQLite database to retrieve secrets at runtime.

CLI Guard also provides a TUI (Terminal User Interface) for convenient manual management of secrets — creating, updating, deleting, and browsing entries. But the TUI is a convenience layer, not the primary purpose. The core value is enabling scripts to securely retrieve secrets without hardcoding them.

## Business Problem
Secrets management in scripting and automation workflows is a common pain point:

- **Hardcoded secrets** — API keys, database passwords, and tokens embedded directly in scripts. Insecure, hard to rotate, and a security incident waiting to happen.
- **Cloud key vaults (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault)** — Powerful, but require network access, subscriptions, and configuration overhead. Not suitable for airgapped environments, offline systems, or internal networks that prefer self-hosted tools.
- **Environment variables / .env files** — Better than hardcoding, but still plaintext on disk with no access control, encryption, or audit logging.
- **Existing CLI password managers (pass, gopass)** — Designed for personal password management, not for programmatic secret retrieval in automation pipelines.

CLI Guard fills the gap for environments that need:
- **Encrypted secret storage** with proper key derivation (not plaintext files)
- **Programmatic access** for scripts (bash, Python, etc.) to retrieve secrets at runtime
- **Zero network dependency** — works on airgapped systems, offline clusters, internal networks
- **No subscription fees** or cloud accounts required
- **A convenient TUI** for human operators to manage the secret store manually

## Target Environments
- Container clusters and orchestration systems without cloud access
- Airgapped or offline distributed systems
- Internal networks that prefer self-hosted tools over cloud services
- Development environments that need local secret management
- CI/CD pipelines running on self-hosted infrastructure

## Target Users
- DevOps engineers and system administrators managing automation workflows
- Developers writing scripts that need to consume secrets securely
- Security-conscious teams that don't trust cloud-hosted secret stores
- Hobbyist developers learning about encryption, security, and secret management

## User Stories

### Scripting & Automation (Primary Use Case)
- **US-1:** As a script, I can authenticate and retrieve a specific secret by account/username so I don't hardcode credentials
- **US-2:** As a script, I can retrieve secrets non-interactively (no TUI, no prompts) for use in automation pipelines
- **US-3:** As an operator, I can use CLI Guard from bash/Python scripts the same way I'd use `az keyvault secret show`
- **US-4:** As an operator, I can rotate a secret in CLI Guard and all scripts automatically pick up the new value on next retrieval

### Authentication
- **US-5:** As a user, I can create a new account with a username and master password
- **US-6:** As a user, I can sign in with my username and master password
- **US-7:** As a user, my account locks after 3 failed login attempts (until the next day)
- **US-8:** As a user, I can sign out to clear my session and encryption keys from memory

### Secret Management (via TUI)
- **US-9:** As a user, I can create a new secret entry with category, account, username, and password/secret
- **US-10:** As a user, I can view all my stored secrets in a scrollable table
- **US-11:** As a user, I can select a secret to view its full decrypted details in a popup
- **US-12:** As a user, I can update an existing secret entry
- **US-13:** As a user, I can delete a secret entry with confirmation
- **US-14:** As a user, I can search my secrets by category, account, or username
- **US-15:** As a user, I can sort my secrets by any column in ascending or descending order
- **US-16:** As a user, I can clear active search/sort filters with ESC

### Secret Generation (Planned)
- **US-17:** As a user, I can generate a scrambled password from text I provide
- **US-18:** As a user, I can generate a random password with configurable length
- **US-19:** As a user, I can generate a passphrase (multiple random words)

### User Management (Planned)
- **US-20:** As a user, I can change my master password
- **US-21:** As a user, I can delete my account and all associated secrets

### Data Management (Planned)
- **US-22:** As a user, I can export my database to a backup file
- **US-23:** As a user, I can import a database backup

### Security (Planned)
- **US-24:** As a user, my clipboard is automatically cleared after copying a secret (timeout)
- **US-25:** As a user, my session times out after inactivity for security

## Requirements

### Functional Requirements
| ID | Requirement | Status |
|----|------------|--------|
| **Scripting Interface** | | |
| FR-1 | CLI mode: retrieve secret by account/username (non-interactive) | Done |
| FR-2 | CLI mode: authenticate via session tokens or service account tokens | Done |
| FR-3 | CLI mode: output secret to stdout for script consumption | Done |
| FR-4 | CLI mode: list available secrets (non-interactive) | Done |
| FR-5 | Python module: importable interface for Python scripts | Done |
| **Core (Done)** | | |
| FR-6 | User authentication with bcrypt-hashed master password | Done |
| FR-7 | Account lockout after 3 failed attempts | Done |
| FR-8 | AES-encrypted secret storage using Fernet | Done |
| FR-9 | PBKDF2 key derivation (encryption key never stored on disk) | Done |
| FR-10 | Full CRUD operations for secret entries | Done |
| FR-11 | Search by category/account/username with LIKE queries | Done |
| FR-12 | Sort by any column in ascending/descending order | Done |
| FR-13 | Input validation on all user-provided data | Done |
| FR-14 | SQL injection prevention via column whitelists | Done |
| FR-20a | Session tokens for interactive CLI use (signin/signout, 1-hour TTL) | Done |
| FR-20b | Service account tokens for automation (long-lived, revocable) | Done |
| FR-20c | Key wrapping — encryption key encrypted by token-derived key | Done |
| FR-20d | `--password` flag removed from data commands (passwords only on auth commands) | Done |
| **Remaining Features** | | |
| FR-15 | Secret generation (scramble, random, passphrase) | Planned |
| FR-16 | User management (change password, delete account) | Planned |
| FR-17 | Database export/import | Planned |
| FR-18 | Clipboard auto-clear after timeout | Planned |
| FR-19 | Session timeout after inactivity | Planned |

### Non-Functional Requirements
| ID | Requirement | Status |
|----|------------|--------|
| NFR-1 | Runs in any terminal with minimum 65x20 characters (TUI mode) | Done |
| NFR-2 | All encryption/decryption happens in memory only | Done |
| NFR-3 | Zero network calls — fully offline application | Done |
| NFR-4 | Python 3.12+ with minimal dependencies (bcrypt, cryptography) | Done |
| NFR-5 | Unit test coverage for business logic, validation, CLI, and tokens | Done (163 tests) |
| NFR-6 | Works on airgapped systems with no internet access | Done |
| NFR-7 | Scriptable: can be invoked non-interactively from bash/Python | Done |

## Development Strategy
The project is being built foundation-up:

1. **Phase A (Done):** Database layer, business logic, encryption/hashing — the functions that actually do the work
2. **Phase B (Done):** TUI for manual secret management — lets us visually verify everything works, test without ambiguity
3. **Phase C (Done):** CLI/scripting interface — expose the existing business logic functions for non-interactive use
4. **Phase C.1 (Done):** Token-based authentication — session tokens for humans, service tokens for automation, key wrapping for secure key persistence
5. **Phase D (Next):** Polish — password generation, clipboard management, session timeout

This approach means the TUI was built first not because it's more important, but because it provides an unambiguous way to test the underlying functions before building the "headless" scripting interface on top of them. All the hard work (encryption, auth, CRUD) is already done in `CLI_Guard.py` — the scripting interface just needs to call those same functions.
