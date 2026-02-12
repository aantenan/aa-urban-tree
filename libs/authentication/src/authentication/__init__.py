"""Authentication library: pluggable provider, JWT, password, session, lockout, errors."""
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from authentication.interfaces.auth_provider import AuthProvider, UserRepository


def get_provider(user_repository: "UserRepository | None" = None) -> "AuthProvider":
    """Return the configured auth provider (AUTH_PROVIDER=mock|jwt). For jwt, pass user_repository."""
    kind = (os.getenv("AUTH_PROVIDER") or "mock").lower()
    if kind == "jwt":
        from authentication.implementations.jwt_provider import JwtAuthProvider
        if user_repository is None:
            return _StubJwtProvider()
        return JwtAuthProvider(user_repository)
    from authentication.implementations.mock_provider import MockAuthProvider
    return MockAuthProvider()


class _StubJwtProvider:
    """Stub when AUTH_PROVIDER=jwt but no user_repository given (backend may use its own service)."""

    def authenticate(self, email: str, password: str) -> Any:
        raise NotImplementedError("JWT auth requires user_repository; use get_provider(user_repository=...) or backend auth service.")

    def verify(self, token: str) -> Any:
        from authentication.utils.jwt import validate_token
        return validate_token(token)

    def register(self, email: str, password: str, **kwargs: Any) -> Any:
        raise NotImplementedError("JWT auth requires user_repository.")

    def refresh_token(self, token: str) -> Any:
        raise NotImplementedError("JWT auth requires user_repository.")

    def reset_password(self, token: str, new_password: str) -> Any:
        raise NotImplementedError("JWT auth requires user_repository.")

    def lock_account(self, identifier: str) -> None:
        raise NotImplementedError("JWT auth requires user_repository.")

    def unlock_account(self, identifier: str) -> None:
        raise NotImplementedError("JWT auth requires user_repository.")


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
    "AuthProvider",
    "UserRepository",
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
