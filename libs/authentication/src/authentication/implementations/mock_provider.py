"""Mock authentication for development: configurable users, in-memory tokens and lockout."""
import os
import secrets
from typing import Any

from authentication.interfaces.auth_provider import AuthProvider
from authentication.utils import validate_password_complexity
from authentication.utils.email_validator import validate_email_format


def _parse_fake_users() -> list[tuple[str, str, str]]:
    raw = os.getenv("MOCK_AUTH_USERS", "").strip()
    if not raw:
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
    """In-memory auth: configurable users, token store, lockout, register, refresh, reset."""

    def __init__(self) -> None:
        self._users: list[tuple[str, str, str]] = _parse_fake_users()  # email, password, name
        self._tokens: dict[str, dict[str, Any]] = {}  # token -> {sub, email, name}
        self._locked: set[str] = set()  # emails

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        email = (email or "").strip().lower()
        if email in self._locked:
            return None
        for e, p, name in self._users:
            if e == email and p == password:
                token = secrets.token_urlsafe(32)
                self._tokens[token] = {"sub": e, "email": e, "name": name}
                return {"token": token, "user": {"id": e, "email": e, "name": name, "role": "user"}}
        return None

    def verify(self, token: str) -> dict[str, Any] | None:
        return self._tokens.get(token)

    def register(self, email: str, password: str, **kwargs: Any) -> dict[str, Any]:
        ok, msg = validate_email_format(email)
        if not ok:
            raise ValueError(msg)
        email = email.strip().lower()
        ok, msg = validate_password_complexity(password)
        if not ok:
            raise ValueError(msg)
        if any(e == email for e, _, _ in self._users):
            raise ValueError("This email is already registered.")
        name = kwargs.get("name", email.split("@")[0])
        self._users.append((email, password, name))
        return {"user": {"id": email, "email": email, "name": name, "role": "user"}, "message": "Registration successful."}

    def logout(self, token: str) -> None:
        self._tokens.pop(token, None)

    def refresh_token(self, token: str) -> dict[str, Any] | None:
        data = self._tokens.get(token)
        if not data:
            return None
        self._tokens.pop(token, None)
        new_token = secrets.token_urlsafe(32)
        self._tokens[new_token] = data
        return {"token": new_token, "user": {"id": data["sub"], "email": data["email"], "name": data["name"], "role": "user"}}

    def reset_password(self, token: str, new_password: str) -> dict[str, Any]:
        ok, msg = validate_password_complexity(new_password)
        if not ok:
            raise ValueError(msg)
        # Mock: accept any token; update password for first user (no real token store)
        if self._users:
            self._users[0] = (self._users[0][0], new_password, self._users[0][2])
        return {"message": "Password has been reset."}

    def lock_account(self, identifier: str) -> None:
        self._locked.add(identifier.strip().lower())

    def unlock_account(self, identifier: str) -> None:
        self._locked.discard(identifier.strip().lower())
