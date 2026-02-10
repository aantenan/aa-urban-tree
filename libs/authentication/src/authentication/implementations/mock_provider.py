"""Mock authentication implementation for local development with configurable fake users."""
import os
import secrets
from typing import Any

from authentication.interfaces.auth_provider import AuthProvider


def _parse_fake_users() -> list[tuple[str, str, str]]:
    """
    Parse MOCK_AUTH_USERS from env. Format: one user per line or comma-separated,
    each entry email:password or email:password:Display Name.
    """
    raw = os.getenv("MOCK_AUTH_USERS", "").strip()
    if not raw:
        # Default dev accounts
        return [
            ("dev@example.com", "dev", "Dev User"),
            ("admin@example.com", "admin", "Admin User"),
        ]
    users: list[tuple[str, str, str]] = []
    for part in raw.replace(",", "\n").splitlines():
        part = part.strip()
        if not part:
            continue
        segments = part.split(":", 2)
        email = (segments[0] or "").strip().lower()
        password = (segments[1] or "").strip()
        name = (segments[2] or email).strip() if len(segments) > 2 else email
        if email and password is not None:
            users.append((email, password, name))
    return users if users else [("dev@example.com", "dev", "Dev User")]


class MockAuthProvider(AuthProvider):
    """Accepts any email/password that matches the configured fake user list."""

    def __init__(self) -> None:
        self._users = _parse_fake_users()

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        email = (email or "").strip().lower()
        for e, p, name in self._users:
            if e == email and p == password:
                token = secrets.token_urlsafe(32)
                return {
                    "token": token,
                    "user": {"id": e, "email": e, "name": name},
                }
        return None
