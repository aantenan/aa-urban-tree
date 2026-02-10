"""JWT-based authentication implementation (production)."""
from typing import Any

from authentication.interfaces.auth_provider import AuthProvider


class JwtAuthProvider(AuthProvider):
    """JWT auth: not implemented in this stub; use mock for local dev."""

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        raise NotImplementedError("Configure a real JWT/auth backend for production")
