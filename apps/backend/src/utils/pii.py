"""PII detection and redaction for logs and audit trails."""
import re
from typing import Any


# Patterns for common PII (simplified; extend as needed)
EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
)
# SSN-like: 3-2-4 digits (allow optional dashes)
SSN_PATTERN = re.compile(r"\b[0-9]{3}-?[0-9]{2}-?[0-9]{4}\b")


def redact_email(s: str) -> str:
    """Replace email with [EMAIL_REDACTED]."""
    return EMAIL_PATTERN.sub("[EMAIL_REDACTED]", s)


def redact_phone(s: str) -> str:
    """Replace phone numbers with [PHONE_REDACTED]."""
    return PHONE_PATTERN.sub("[PHONE_REDACTED]", s)


def redact_ssn(s: str) -> str:
    """Replace SSN-like sequences with [SSN_REDACTED]."""
    return SSN_PATTERN.sub("[SSN_REDACTED]", s)


def redact_pii(text: str | None) -> str:
    """Redact common PII from a string for safe logging. Returns empty string if input is None."""
    if text is None:
        return ""
    s = str(text)
    s = redact_email(s)
    s = redact_phone(s)
    s = redact_ssn(s)
    return s


def redact_dict_pii(obj: dict[str, Any] | None, keys_to_redact: set[str] | None = None) -> dict[str, Any]:
    """Return a copy of the dict with PII keys redacted. keys_to_redact defaults to email, phone, ssn, password."""
    if obj is None:
        return {}
    default_keys = {"email", "phone", "primary_contact_phone", "alternate_contact_phone", "password", "password_hash", "ssn"}
    keys = keys_to_redact or default_keys
    out = {}
    for k, v in obj.items():
        key_lower = k.lower()
        if any(red in key_lower for red in default_keys) or (keys and key_lower in keys):
            out[k] = "[REDACTED]"
        elif isinstance(v, dict):
            out[k] = redact_dict_pii(v, keys)
        elif isinstance(v, str):
            out[k] = redact_pii(v)
        else:
            out[k] = v
    return out
