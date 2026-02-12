"""Tests for session expiry and warning."""
from unittest.mock import patch
import time

from authentication.utils.session import (
    SESSION_EXPIRE_SECONDS,
    WARNING_BEFORE_EXPIRE_SECONDS,
    seconds_until_expiry,
    should_warn_expiry,
)


def test_seconds_until_expiry_future() -> None:
    exp = int(time.time()) + 3600
    assert seconds_until_expiry(exp) > 0


def test_seconds_until_expiry_past() -> None:
    exp = int(time.time()) - 10
    assert seconds_until_expiry(exp) == 0


def test_should_warn_expiry_soon() -> None:
    # Expires in 2 minutes (120 sec); warning is 300 sec by default
    exp = int(time.time()) + 120
    assert should_warn_expiry(exp) is True


def test_should_warn_expiry_not_soon() -> None:
    # Expires in 1 hour
    exp = int(time.time()) + 3600
    assert should_warn_expiry(exp) is False
