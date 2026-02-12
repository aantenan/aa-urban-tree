"""Tests for JWT generation and validation."""
from datetime import datetime, timezone, timedelta

import pytest
import jwt as pyjwt

from authentication.utils.jwt import (
    create_token,
    decode_token,
    validate_token,
    get_token_expire_seconds,
)


@pytest.fixture(autouse=True)
def set_jwt_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "test-secret-for-unit-tests")


def test_create_and_validate() -> None:
    payload = {"sub": "user-123", "email": "u@example.com"}
    token = create_token(payload)
    assert isinstance(token, str)
    decoded = validate_token(token)
    assert decoded is not None
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "u@example.com"
    assert "exp" in decoded
    assert "iat" in decoded


def test_decode_invalid_returns_none() -> None:
    assert validate_token("invalid.token.here") is None
    assert validate_token("") is None


def test_decode_expired_returns_none() -> None:
    secret = "test-secret-for-unit-tests"
    token = pyjwt.encode(
        {"sub": "u", "iat": datetime.now(timezone.utc) - timedelta(hours=2), "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
        secret,
        algorithm="HS256",
    )
    assert validate_token(token) is None


def test_wrong_signature_returns_none() -> None:
    # Token signed with different secret will not validate
    token = create_token({"sub": "u"})
    # Tamper: replace one char in token
    bad_token = token[:-1] + ("X" if token[-1] != "X" else "Y")
    assert validate_token(bad_token) is None
