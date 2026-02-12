"""Password hashing (bcrypt) and complexity validation."""
import os
import re
from typing import Any

import bcrypt

DEFAULT_SALT_ROUNDS = 12


def get_salt_rounds() -> int:
    """Salt rounds from env (BCRYPT_SALT_ROUNDS) or default."""
    raw = os.getenv("BCRYPT_SALT_ROUNDS", str(DEFAULT_SALT_ROUNDS))
    try:
        return max(10, min(16, int(raw)))
    except ValueError:
        return DEFAULT_SALT_ROUNDS


def hash_password(password: str) -> str:
    """Hash password with bcrypt. Returns encoded hash string."""
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=get_salt_rounds()),
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Return True if password matches hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def validate_password_complexity(
    password: str,
    *,
    min_length: int = 8,
    require_upper: bool = True,
    require_lower: bool = True,
    require_digit: bool = True,
) -> tuple[bool, str]:
    """
    Validate password complexity. Returns (valid, error_message).
    error_message is empty when valid is True.
    """
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters."
    if require_upper and not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if require_lower and not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if require_digit and not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    return True, ""
