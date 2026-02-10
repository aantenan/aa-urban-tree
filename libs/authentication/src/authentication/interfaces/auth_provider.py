"""Abstract authentication provider interface."""
from abc import ABC, abstractmethod
from typing import Any


class AuthProvider(ABC):
    """Interface for authentication (login, verify, etc.)."""

    @abstractmethod
    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        """
        Authenticate user by email and password.
        Returns dict with at least 'token' and 'user' (e.g. id, email, name), or None if invalid.
        """
        ...
