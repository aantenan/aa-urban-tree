"""Seed User table so mock-auth logins (by email) resolve to a DB user."""
import logging
import os

logger = logging.getLogger(__name__)


def _emails_from_mock_env() -> list[str]:
    """Parse MOCK_AUTH_USERS (email:password or email:password:name) for emails."""
    raw = os.getenv("MOCK_AUTH_USERS", "").strip()
    if not raw:
        return []
    emails = []
    for part in raw.replace(",", "\n").splitlines():
        part = part.strip()
        if not part:
            continue
        segments = part.split(":", 2)
        email = (segments[0] or "").strip().lower()
        if email:
            emails.append(email)
    return emails


def seed_users() -> None:
    """Create User rows for default seed emails + MOCK_AUTH_USERS if not present."""
    try:
        from database.models import User
        from data.seed_users_data import DEFAULT_SEED_USERS
    except ImportError as e:
        logger.warning("User seed skipped: %s", e)
        return
    emails_to_seed = {row["email"] for row in DEFAULT_SEED_USERS}
    for e in _emails_from_mock_env():
        emails_to_seed.add(e)
    by_email = {row["email"]: row for row in DEFAULT_SEED_USERS}
    created = 0
    for email in emails_to_seed:
        row = by_email.get(email)
        defaults = {
            "password_hash": row["password_hash"] if row else "seeded",
            "account_status": "active",
        }
        _, created_this = User.get_or_create(email=email, defaults=defaults)
        if created_this:
            created += 1
    if created:
        logger.info("Seeded %d users", created)