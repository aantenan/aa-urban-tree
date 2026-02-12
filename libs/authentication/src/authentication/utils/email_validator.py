"""Email format validation and uniqueness checking utility."""
import re
from typing import Callable, Awaitable

# Simple format check
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_email_format(email: str) -> tuple[bool, str]:
    """
    Validate email format. Returns (valid, error_message).
    error_message is empty when valid is True.
    """
    email = (email or "").strip().lower()
    if not email:
        return False, "Email is required."
    if not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    return True, ""


async def check_email_unique(
    email: str,
    is_taken: Callable[[str], Awaitable[bool]],
) -> tuple[bool, str]:
    """
    Check that email is not already taken (e.g. in DB).
    is_taken(email) should return True if the email exists.
    Returns (unique, error_message).
    """
    ok, msg = validate_email_format(email)
    if not ok:
        return False, msg
    if await is_taken(email):
        return False, "This email is already registered."
    return True, ""
