"""Tests for JwtAuthProvider with in-memory UserRepository."""
from datetime import datetime, timedelta, timezone
from typing import Any

import pytest

from authentication import AccountLockedError
from authentication.implementations.jwt_provider import JwtAuthProvider
from authentication.utils import hash_password


class InMemoryUser:
    def __init__(self, id: str, email: str, password_hash: str, account_status: str = "active"):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.account_status = account_status


class InMemoryPasswordReset:
    def __init__(self, user_id: str, token: str, expires_at: datetime, user: InMemoryUser | None = None):
        self.user_id = user_id
        self.reset_token = token
        self.expires_at = expires_at
        self.used_at = None
        self.user = user


class FakeUserRepository:
    def __init__(self) -> None:
        self.users: dict[str, InMemoryUser] = {}
        self.resets: dict[str, InMemoryPasswordReset] = {}
        self.attempts: list = []

    def get_by_email(self, email: str) -> InMemoryUser | None:
        for u in self.users.values():
            if u.email == email:
                return u
        return None

    def get_by_id(self, user_id: str) -> InMemoryUser | None:
        return self.users.get(user_id)

    def create_user(self, email: str, password_hash: str, **kwargs: Any) -> InMemoryUser:
        uid = email.replace("@", "_")
        u = InMemoryUser(uid, email, password_hash)
        self.users[uid] = u
        return u

    def update_password(self, user_id: str, password_hash: str) -> None:
        if user_id in self.users:
            self.users[user_id].password_hash = password_hash

    def set_account_status(self, user_id: str, status: str) -> None:
        if user_id in self.users:
            self.users[user_id].account_status = status

    def record_login_attempt(self, email: str, success: bool, ip_address: str | None) -> None:
        self.attempts.append((email, success, ip_address))

    def create_password_reset(self, user_id: str, token: str, expires_at: datetime) -> None:
        u = self.users.get(user_id)
        pr = InMemoryPasswordReset(user_id, token, expires_at, user=u)
        self.resets[token] = pr

    def get_password_reset(self, token: str) -> InMemoryPasswordReset | None:
        return self.resets.get(token)

    def mark_password_reset_used(self, token: str) -> None:
        if token in self.resets:
            self.resets[token].used_at = datetime.now(timezone.utc)

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None


@pytest.fixture
def repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture(autouse=True)
def jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret")


def test_jwt_register_and_authenticate(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "SecureP4ss")
    out = provider.authenticate("u@example.com", "SecureP4ss")
    assert out is not None
    assert out["token"]
    assert out["user"]["email"] == "u@example.com"
    assert out["user"].get("role") == "user"


def test_jwt_authenticate_wrong_password(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "SecureP4ss")
    assert provider.authenticate("u@example.com", "wrong") is None


def test_jwt_verify(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "SecureP4ss")
    out = provider.authenticate("u@example.com", "SecureP4ss")
    payload = provider.verify(out["token"])
    assert payload is not None
    assert payload["sub"]
    assert payload["email"] == "u@example.com"


def test_jwt_lockout(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "SecureP4ss")
    for _ in range(5):
        provider.authenticate("u@example.com", "wrong")
    with pytest.raises(AccountLockedError):
        provider.authenticate("u@example.com", "SecureP4ss")


def test_jwt_lock_and_unlock_account(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "SecureP4ss")
    provider.lock_account("u@example.com")
    with pytest.raises(AccountLockedError):
        provider.authenticate("u@example.com", "SecureP4ss")
    provider.unlock_account("u@example.com")
    out = provider.authenticate("u@example.com", "SecureP4ss")
    assert out is not None


def test_jwt_refresh_token(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "SecureP4ss")
    out = provider.authenticate("u@example.com", "SecureP4ss")
    refreshed = provider.refresh_token(out["token"])
    assert refreshed is not None
    assert refreshed["token"] != out["token"]
    assert refreshed["user"]["email"] == "u@example.com"


def test_jwt_reset_password(repo: FakeUserRepository) -> None:
    provider = JwtAuthProvider(repo)
    provider.register("u@example.com", "OldPass1")
    user = repo.get_by_email("u@example.com")
    assert user is not None
    token = "reset-token-123"
    repo.create_password_reset(user.id, token, datetime.now(timezone.utc) + timedelta(hours=24))
    out = provider.reset_password(token, "NewPass1")
    assert "reset" in out["message"].lower()
    assert provider.authenticate("u@example.com", "NewPass1") is not None
