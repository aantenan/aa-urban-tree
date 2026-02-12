"""Abstract authentication provider interface."""
from abc import ABC, abstractmethod
from typing import Any, Protocol


class AuthProvider(ABC):
    """Pluggable authentication: authenticate, verify token, register, logout, refresh, reset, lock/unlock."""

    @abstractmethod
    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        """
        Authenticate user by email and password.
        Returns dict with 'token' and 'user' (id, email, name, role?), or None if invalid.
        """
        ...

    @abstractmethod
    def verify(self, token: str) -> dict[str, Any] | None:
        """Verify token; return payload (e.g. sub, email, role) or None if invalid/expired."""
        ...

    def register(self, email: str, password: str, **kwargs: Any) -> dict[str, Any]:
        """Register user; email uniqueness and password complexity enforced. Returns user info."""
        raise NotImplementedError("register")

    def logout(self, token: str) -> None:
        """Invalidate token (client-side cleanup; server may blacklist)."""
        pass  # Optional

    def refresh_token(self, token: str) -> dict[str, Any] | None:
        """Issue new token from valid current token. Returns new token + user or None."""
        raise NotImplementedError("refresh_token")

    def reset_password(self, token: str, new_password: str) -> dict[str, Any]:
        """Reset password with token. Returns message."""
        raise NotImplementedError("reset_password")

    def lock_account(self, identifier: str) -> None:
        """Lock account (e.g. by email or user id)."""
        raise NotImplementedError("lock_account")

    def unlock_account(self, identifier: str) -> None:
        """Unlock account."""
        raise NotImplementedError("unlock_account")


class UserRepository(Protocol):
    """Protocol for user persistence (used by JwtAuthProvider)."""

    def get_by_email(self, email: str) -> Any | None: ...
    def get_by_id(self, user_id: str) -> Any | None: ...
    def create_user(self, email: str, password_hash: str, **kwargs: Any) -> Any: ...
    def update_password(self, user_id: str, password_hash: str) -> None: ...
    def set_account_status(self, user_id: str, status: str) -> None: ...
    def record_login_attempt(self, email: str, success: bool, ip_address: str | None) -> None: ...
    def create_password_reset(self, user_id: str, token: str, expires_at: Any) -> None: ...
    def get_password_reset(self, token: str) -> Any | None: ...
    def mark_password_reset_used(self, token: str) -> None: ...
    def email_exists(self, email: str) -> bool: ...
