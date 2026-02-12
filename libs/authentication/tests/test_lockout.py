"""Tests for account lockout (brute-force prevention)."""
import pytest

from authentication.utils.lockout import LockoutTracker


def test_lockout_after_max_attempts() -> None:
    t = LockoutTracker(max_attempts=3, lockout_seconds=60)
    assert t.is_locked("u@x.com") is False
    assert t.remaining_attempts("u@x.com") == 3
    t.record_failure("u@x.com")
    t.record_failure("u@x.com")
    assert t.remaining_attempts("u@x.com") == 1
    assert t.is_locked("u@x.com") is False
    t.record_failure("u@x.com")
    assert t.is_locked("u@x.com") is True
    assert t.remaining_attempts("u@x.com") == 0


def test_reset_clears_lockout() -> None:
    t = LockoutTracker(max_attempts=2, lockout_seconds=60)
    t.record_failure("a@b.com")
    t.record_failure("a@b.com")
    assert t.is_locked("a@b.com") is True
    t.reset("a@b.com")
    assert t.is_locked("a@b.com") is False
    assert t.remaining_attempts("a@b.com") == 2


def test_case_insensitive() -> None:
    t = LockoutTracker(max_attempts=2, lockout_seconds=60)
    t.record_failure("User@Example.com")
    t.record_failure("user@example.com")
    assert t.is_locked("USER@EXAMPLE.COM") is True
