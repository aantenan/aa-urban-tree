"""Tests for database connection and configuration."""
import os
import pytest


def test_get_database_url_default() -> None:
    """Without DATABASE_URL, default is SQLite."""
    from database.connection import get_database_url
    assert "sqlite" in get_database_url().lower()


def test_get_database_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """DATABASE_URL from environment is returned."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
    from database.connection import get_database_url
    assert "postgresql" in get_database_url()
