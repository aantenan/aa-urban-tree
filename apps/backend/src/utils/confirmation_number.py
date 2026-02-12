"""Confirmation number generation: UTP-YYYY-NNNN format."""
from datetime import datetime
from typing import Callable

# Optional: inject a sequence resolver (e.g. from DB) for NNNN
_default_sequence: int = 0


def generate_confirmation_number(
    *,
    prefix: str = "UTP",
    year: int | None = None,
    next_sequence: Callable[[], int] | None = None,
) -> str:
    """
    Generate confirmation number in format PREFIX-YYYY-NNNN (e.g. UTP-2025-0001).
    next_sequence() can be provided to get NNNN from DB; otherwise in-process counter.
    """
    global _default_sequence
    y = year or datetime.now().year
    if next_sequence is not None:
        n = next_sequence()
    else:
        _default_sequence += 1
        n = _default_sequence
    return f"{prefix}-{y}-{n:04d}"
