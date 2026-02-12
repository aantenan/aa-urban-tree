"""Authentication library: pluggable provider, JWT, password, session, lockout, errors."""
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from authentication.interfaces.auth_provider import AuthProvider


def get_provider() -> "AuthProvider":
    """Return the configured auth provider (AUTH_PROVIDER=mock|jwt)."""
    kind = (os.getenv("AUTH_PROVIDER") or "mock").lower()
    if kind == "jwt":
        from authentication.implementations.jwt_provider import JwtAuthProvider
        return JwtAuthProvider()
    from authentication.implementations.mock_provider import MockAuthProvider
    return MockAuthProvider()


# Re-export utilities and errors for convenience
from authentication.errors import (
    AuthError,
    InvalidCredentialsError,
    AccountLockedError,
    TokenInvalidError,
    PasswordComplexityError,
)
from authentication.utils import (
    hash_password,
    verify_password,
    validate_password_complexity,
    create_token,
    decode_token,
    validate_token,
    SESSION_EXPIRE_SECONDS,
    WARNING_BEFORE_EXPIRE_SECONDS,
    LockoutTracker,
    validate_email_format,
)

__all__ = [
    "get_provider",
    "AuthError",
    "InvalidCredentialsError",
    "AccountLockedError",
    "TokenInvalidError",
    "PasswordComplexityError",
    "hash_password",
    "verify_password",
    "validate_password_complexity",
    "create_token",
    "decode_token",
    "validate_token",
    "SESSION_EXPIRE_SECONDS",
    "WARNING_BEFORE_EXPIRE_SECONDS",
    "LockoutTracker",
    "validate_email_format",
]
