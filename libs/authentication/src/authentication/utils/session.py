"""Session management constants: expiration and warning before expiry."""
import os

# 2 hours of inactivity (blueprint)
SESSION_EXPIRE_SECONDS = int(os.getenv("SESSION_EXPIRE_SECONDS", "7200"))
# Warn 5 minutes before expiration (blueprint)
WARNING_BEFORE_EXPIRE_SECONDS = int(os.getenv("WARNING_BEFORE_EXPIRE_SECONDS", "300"))


def seconds_until_expiry(exp_claim: int) -> int:
    """Seconds until token expires (from exp claim). <= 0 if already expired."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).timestamp()
    return max(0, int(exp_claim - now))


def should_warn_expiry(exp_claim: int) -> bool:
    """True if token expires within WARNING_BEFORE_EXPIRE_SECONDS."""
    return seconds_until_expiry(exp_claim) <= WARNING_BEFORE_EXPIRE_SECONDS
