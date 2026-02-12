"""Tests for auth error types and public messages."""
from authentication.errors import (
    AuthError,
    InvalidCredentialsError,
    AccountLockedError,
    TokenInvalidError,
    PasswordComplexityError,
)


def test_invalid_credentials_public_message() -> None:
    e = InvalidCredentialsError()
    assert "email" in e.public_message.lower() or "password" in e.public_message.lower()
    assert "invalid" in e.public_message.lower()


def test_account_locked_public_message() -> None:
    e = AccountLockedError(lockout_seconds=900)
    assert "lock" in e.public_message.lower()
    assert "15" in e.public_message  # 900/60


def test_token_invalid_public_message() -> None:
    e = TokenInvalidError()
    assert "sign in" in e.public_message.lower() or "session" in e.public_message.lower()


def test_password_complexity_uses_detail() -> None:
    e = PasswordComplexityError("Must include a number.")
    assert e.public_message == "Must include a number."
