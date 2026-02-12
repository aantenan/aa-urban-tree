"""Tests for email validation."""
import pytest

from authentication.utils.email_validator import validate_email_format


def test_valid_email() -> None:
    ok, msg = validate_email_format("user@example.com")
    assert ok is True
    assert msg == ""


def test_invalid_format() -> None:
    ok, msg = validate_email_format("not-an-email")
    assert ok is False
    assert "valid" in msg.lower()


def test_empty() -> None:
    ok, msg = validate_email_format("")
    assert ok is False


def test_normalized_lowercase() -> None:
    ok, msg = validate_email_format("  User@Example.COM  ")
    assert ok is True
