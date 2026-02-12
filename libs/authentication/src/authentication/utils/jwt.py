"""JWT token generation, validation, and expiration handling."""
import os
from datetime import datetime, timezone, timedelta
from typing import Any

import jwt

DEFAULT_ALGORITHM = "HS256"
DEFAULT_EXPIRE_SECONDS = 7200  # 2 hours


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if not secret:
        raise ValueError("JWT_SECRET must be set for JWT authentication")
    return secret


def _get_algorithm() -> str:
    return os.getenv("JWT_ALGORITHM", DEFAULT_ALGORITHM)


def get_token_expire_seconds() -> int:
    """Token expiry in seconds (JWT_EXPIRE_SECONDS). Default 2 hours."""
    raw = os.getenv("JWT_EXPIRE_SECONDS", str(DEFAULT_EXPIRE_SECONDS))
    try:
        return max(60, int(raw))
    except ValueError:
        return DEFAULT_EXPIRE_SECONDS


def create_token(
    payload: dict[str, Any],
    *,
    expire_seconds: int | None = None,
) -> str:
    """Encode a JWT with exp and iat. payload should include sub (user id) and any user claims."""
    expire = expire_seconds or get_token_expire_seconds()
    now = datetime.now(timezone.utc)
    claims = {
        "iat": now,
        "exp": now + timedelta(seconds=expire),
        **payload,
    }
    return jwt.encode(
        claims,
        _get_secret(),
        algorithm=_get_algorithm(),
    )


def decode_token(token: str) -> dict[str, Any]:
    """Decode and return payload. Raises jwt.InvalidTokenError if invalid or expired."""
    return jwt.decode(
        token,
        _get_secret(),
        algorithms=[_get_algorithm()],
    )


def validate_token(token: str) -> dict[str, Any] | None:
    """Validate token (signature and expiration). Returns payload or None if invalid."""
    try:
        return decode_token(token)
    except jwt.InvalidTokenError:
        return None
