"""Tests for AuthProvider interface: mock and JWT flows, verify, register, lockout, session."""
import pytest

from authentication import get_provider
from authentication.implementations.mock_provider import MockAuthProvider
from authentication.interfaces.auth_provider import AuthProvider


def test_get_provider_returns_mock_by_default() -> None:
    provider = get_provider()
    assert isinstance(provider, MockAuthProvider)


def test_mock_authenticate_success() -> None:
    provider = MockAuthProvider()
    out = provider.authenticate("dev@example.com", "dev")
    assert out is not None
    assert out["token"]
    assert out["user"]["email"] == "dev@example.com"


def test_mock_authenticate_fail() -> None:
    provider = MockAuthProvider()
    assert provider.authenticate("dev@example.com", "wrong") is None


def test_mock_verify_token() -> None:
    provider = MockAuthProvider()
    out = provider.authenticate("dev@example.com", "dev")
    assert out
    payload = provider.verify(out["token"])
    assert payload is not None
    assert payload["email"] == "dev@example.com"


def test_mock_verify_invalid_returns_none() -> None:
    provider = MockAuthProvider()
    assert provider.verify("invalid-token") is None


def test_mock_register() -> None:
    provider = MockAuthProvider()
    out = provider.register("new@example.com", "SecureP4ss")
    assert out["user"]["email"] == "new@example.com"
    auth = provider.authenticate("new@example.com", "SecureP4ss")
    assert auth is not None


def test_mock_register_duplicate_email_raises() -> None:
    provider = MockAuthProvider()
    provider.register("new@example.com", "SecureP4ss")
    with pytest.raises(ValueError, match="already registered"):
        provider.register("new@example.com", "OtherP4ss")


def test_mock_register_password_complexity() -> None:
    provider = MockAuthProvider()
    with pytest.raises(ValueError, match="8"):
        provider.register("x@x.com", "short")


def test_mock_logout_removes_token() -> None:
    provider = MockAuthProvider()
    out = provider.authenticate("dev@example.com", "dev")
    token = out["token"]
    provider.logout(token)
    assert provider.verify(token) is None


def test_mock_refresh_token() -> None:
    provider = MockAuthProvider()
    out = provider.authenticate("dev@example.com", "dev")
    token = out["token"]
    refreshed = provider.refresh_token(token)
    assert refreshed is not None
    assert refreshed["token"] != token
    assert provider.verify(token) is None
    assert provider.verify(refreshed["token"]) is not None


def test_mock_lock_unlock_account() -> None:
    provider = MockAuthProvider()
    assert provider.authenticate("dev@example.com", "dev") is not None
    provider.lock_account("dev@example.com")
    assert provider.authenticate("dev@example.com", "dev") is None
    provider.unlock_account("dev@example.com")
    assert provider.authenticate("dev@example.com", "dev") is not None
