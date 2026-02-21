"""
Database seeder for CLI Guard — generates realistic test data using Faker

Creates a test user and populates ~30-35 encrypted secret entries across
6 categories. All data flows through the business logic layer (startSession →
encryptPassword → insertData) so secrets are properly encrypted and decryptable
by both the TUI and CLI.

Usage:
    python3 seed_database.py           # Seed with fake data
    python3 seed_database.py --clean   # Wipe test user's data and re-seed

Test credentials:
    Username: testuser
    Password: TestPass123!
"""

import sys
import os
import argparse

# Add project root to path so imports work from any directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from faker import Faker
import CLI_Guard
import CLI_SQL.CLI_Guard_SQL as sqlite

# ---------- Constants ----------

TEST_USER = "testuser"
TEST_PASSWORD = "TestPass123!"

# Faker with fixed seed for reproducible data
fake = Faker()
Faker.seed(42)

# Secret definitions — each tuple is (category, account, username_generator)
# We define templates, then Faker fills in realistic values
SECRET_TEMPLATES = [
    # Database secrets (6)
    ("Database", "production-mysql", "db_admin"),
    ("Database", "staging-postgres", "readonly_user"),
    ("Database", "dev-mongodb", "app_service"),
    ("Database", "analytics-redshift", "etl_pipeline"),
    ("Database", "cache-redis-prod", "cache_manager"),
    ("Database", "reporting-mariadb", "report_viewer"),

    # API Keys (6)
    ("API Keys", "aws-prod-iam", "service-account"),
    ("API Keys", "stripe-live", "payment-api"),
    ("API Keys", "github-actions-ci", "ci-bot"),
    ("API Keys", "sendgrid-transactional", "mailer-service"),
    ("API Keys", "twilio-sms-prod", "notification-svc"),
    ("API Keys", "datadog-monitoring", "observability"),

    # Cloud Services (5)
    ("Cloud Services", "azure-portal", None),  # None = generate email
    ("Cloud Services", "gcp-console", None),
    ("Cloud Services", "heroku-staging", None),
    ("Cloud Services", "digitalocean-prod", None),
    ("Cloud Services", "cloudflare-dns", None),

    # Email (5)
    ("Email", "gmail-work", None),
    ("Email", "outlook-corporate", None),
    ("Email", "protonmail-secure", None),
    ("Email", "fastmail-personal", None),
    ("Email", "zoho-team", None),

    # SSH / VPN (4)
    ("SSH / VPN", "prod-server-01", "root"),
    ("SSH / VPN", "prod-server-02", "deploy"),
    ("SSH / VPN", "vpn-office-gateway", "vpn_user"),
    ("SSH / VPN", "bastion-host", "jump_admin"),

    # Internal Tools (5)
    ("Internal Tools", "jira-corp", None),
    ("Internal Tools", "confluence-wiki", None),
    ("Internal Tools", "grafana-dashboards", "admin"),
    ("Internal Tools", "jenkins-ci", "build_agent"),
    ("Internal Tools", "vault-transit", "operator"),
]


def generate_password() -> str:
    """Generate a realistic password that meets validation rules (8+ chars, mixed case, digit, special)"""
    return fake.password(length=16, special_chars=True, digits=True, upper_case=True, lower_case=True)


def generate_username(template_username: str | None) -> str:
    """Return the fixed username or generate a realistic one"""
    if template_username is not None:
        return template_username
    return fake.user_name()


def user_exists(username: str) -> bool:
    """Check if a user already exists in the database"""
    data = sqlite.queryData(user=username, table="users")
    return len(data) > 0


def count_secrets(username: str) -> int:
    """Count how many secrets a user has"""
    data = sqlite.queryData(user=username, table="passwords")
    return len(data)


def clean_test_data() -> int:
    """Delete all secrets belonging to the test user. Returns count deleted."""
    secrets = sqlite.queryData(user=TEST_USER, table="passwords")
    for row in secrets:
        # row structure: (user, category, account, username, encrypted_password, last_modified)
        sqlite.deleteData(user=row[0], account=row[2], username=row[3], password=row[4])
    return len(secrets)


def seed() -> int:
    """
    Create test user (if needed) and populate with fake secrets.

    Returns:
        Number of secrets created
    """
    # Step 1: Create user if they don't exist
    if not user_exists(TEST_USER):
        hashed = CLI_Guard.hashPassword(TEST_PASSWORD)
        salt = CLI_Guard.generateSalt()
        sqlite.insertUser(user=TEST_USER, password=hashed, encryption_salt=salt.hex())
        print(f"  Created user '{TEST_USER}'")
    else:
        print(f"  User '{TEST_USER}' already exists — skipping creation")

    # Step 2: Start a session so encryption works
    CLI_Guard.startSession(TEST_USER, TEST_PASSWORD)

    try:
        # Step 3: Generate and insert secrets
        count = 0
        for category, account, username_template in SECRET_TEMPLATES:
            username = generate_username(username_template)
            password = generate_password()
            CLI_Guard.addSecret(
                user=TEST_USER,
                category=category,
                account=account,
                username=username,
                password=password,
            )
            count += 1

        return count
    finally:
        # Step 4: Always clean up the session
        CLI_Guard.endSession()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed CLI Guard database with realistic test data"
    )
    parser.add_argument(
        "--clean", action="store_true",
        help="Wipe existing test user data before seeding"
    )
    args = parser.parse_args()

    print("CLI Guard — Database Seeder")
    print("=" * 40)

    # Handle --clean flag
    if args.clean:
        deleted = clean_test_data()
        print(f"  Cleaned {deleted} existing secrets for '{TEST_USER}'")

    # Check for existing data (warn if re-seeding without --clean)
    existing = count_secrets(TEST_USER)
    if existing > 0 and not args.clean:
        print(f"\n  WARNING: '{TEST_USER}' already has {existing} secrets.")
        print(f"  Run with --clean to wipe and re-seed, or secrets will be added on top.")
        response = input("  Continue anyway? (y/N): ").strip().lower()
        if response != "y":
            print("  Aborted.")
            sys.exit(0)

    # Seed the database
    print("\n  Seeding database...")
    created = seed()

    # Print summary
    total = count_secrets(TEST_USER)
    print(f"\n  Done! Created {created} secrets ({total} total for '{TEST_USER}')")
    print(f"\n  Test credentials:")
    print(f"    Username: {TEST_USER}")
    print(f"    Password: {TEST_PASSWORD}")
    print(f"\n  Try it out:")
    print(f"    TUI:  python3 CLI_Guard_TUI.py")
    print(f"    CLI:  python3 CLI_Guard_CLI.py list --user {TEST_USER} --password '{TEST_PASSWORD}' --json")


if __name__ == "__main__":
    main()
