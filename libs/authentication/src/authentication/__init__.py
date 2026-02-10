"""Authentication library: pluggable provider (mock for dev, JWT for prod)."""
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
