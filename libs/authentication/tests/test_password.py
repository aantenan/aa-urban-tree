"""Tests for password hashing and complexity."""
import pytest

from authentication.utils.password import (
    hash_password,
    verify_password,
    validate_password_complexity,
    get_salt_rounds,
)


def test_hash_and_verify() -> None:
    pwd = "SecureP4ss"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_verify_invalid_hash() -> None:
    assert verify_password("any", "not-a-valid-bcrypt-hash") is False


def test_complexity_valid() -> None:
    ok, msg = validate_password_complexity("Abcd1234")
    assert ok is True
    assert msg == ""


def test_complexity_too_short() -> None:
    ok, msg = validate_password_complexity("Ab1")
    assert ok is False
    assert "8" in msg


def test_complexity_no_upper() -> None:
    ok, msg = validate_password_complexity("abcd1234")
    assert ok is False
    assert "uppercase" in msg.lower()


def test_complexity_no_lower() -> None:
    ok, msg = validate_password_complexity("ABCD1234")
    assert ok is False
    assert "lowercase" in msg.lower()


def test_complexity_no_digit() -> None:
    ok, msg = validate_password_complexity("Abcdefgh")
    assert ok is False
    assert "number" in msg.lower()
