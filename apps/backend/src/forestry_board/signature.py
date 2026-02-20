"""
Electronic signature handling framework for typed name confirmations.
Validates that the typed name matches expected format and records timestamp.
"""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ElectronicSignature:
    """Electronic signature: typed name with timestamp."""

    typed_name: str
    title: str | None
    approval_date: datetime

    def to_dict(self) -> dict[str, Any]:
        return {
            "typed_name": self.typed_name,
            "title": self.title,
            "approval_date": self.approval_date.isoformat() + "Z" if self.approval_date else None,
        }


def validate_signature(
    typed_name: str,
    expected_name: str | None = None,
    min_length: int = 2,
    max_length: int = 255,
) -> tuple[bool, str | None]:
    """
    Validate electronic signature (typed name confirmation).
    Returns (is_valid, error_message).
    """
    if not typed_name or not isinstance(typed_name, str):
        return False, "Signature (typed name) is required"
    name = typed_name.strip()
    if len(name) < min_length:
        return False, f"Signature must be at least {min_length} characters"
    if len(name) > max_length:
        return False, f"Signature must be at most {max_length} characters"
    # Allow letters, spaces, hyphens, apostrophes (e.g. O'Brien, Anne Arundel)
    if not re.match(r"^[\w\s\-'.]+$", name, re.UNICODE):
        return False, "Signature contains invalid characters"
    if expected_name and _normalize(name) != _normalize(expected_name):
        return False, "Typed name does not match board member name"
    return True, None


def _normalize(s: str) -> str:
    """Normalize for comparison: lowercase, collapse spaces."""
    return " ".join((s or "").lower().split())
