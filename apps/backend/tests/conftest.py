"""
Shared pytest fixtures and test configuration.

- memory_db: in-memory SQLite with all app tables (optional autouse per module).
- auth_user / api_client: for testing protected endpoints with mocked authentication.
- Factories: make_user, make_application for consistent test data.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

if TYPE_CHECKING:
    from fastapi.testclient import TestClient

# All Peewee models used by the backend (for create_tables in one place).
def _get_all_models():
    from database.models import (
        User,
        Application,
        County,
        ContactInformation,
        SiteOwnership,
        ProjectType,
        ProjectInformation,
        FinancialInformation,
        BudgetCategory,
        PasswordReset,
        LoginAttempt,
    )
    return [
        User,
        PasswordReset,
        LoginAttempt,
        Application,
        County,
        ContactInformation,
        SiteOwnership,
        ProjectType,
        ProjectInformation,
        FinancialInformation,
        BudgetCategory,
    ]


@pytest.fixture
def all_models():
    """Return list of all database models for create_tables. Use in custom db fixtures."""
    return _get_all_models()


@pytest.fixture
def memory_db(monkeypatch: pytest.MonkeyPatch, all_models):
    """
    In-memory SQLite DB with all tables created. Use when you need the full schema
    without per-test table list. Resets database_proxy and connection on teardown.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import database.connection as conn
    conn._db = None
    from database.connection import database_proxy, get_db
    db = get_db()
    database_proxy.initialize(db)
    for model in all_models:
        db.create_tables([model], safe=True)
    yield db
    database_proxy.initialize(None)
    db.close()
    conn._db = None


# ---- Test data factories (return model instances; use in fixtures or tests) ----

@pytest.fixture
def make_user(all_models):
    """Factory: create a User and return the instance. Requires DB with User table."""
    from database.models import User
    def _create(email: str = None, password_hash: str = "hash", account_status: str = "active", **kwargs):
        email = email or f"user-{uuid4().hex[:8]}@example.com"
        return User.create(email=email, password_hash=password_hash, account_status=account_status, **kwargs)
    return _create


@pytest.fixture
def make_application(make_user):
    """Factory: create a draft Application for a user. Returns (application, user)."""
    from database.models import Application
    def _create(user=None, status: str = "draft", **kwargs):
        if user is None:
            user = make_user()
        app = Application.create(user_id=user.id, status=status, **kwargs)
        return app, user
    return _create


# ---- Authentication mocking for protected routes ----

@pytest.fixture
def auth_user_payload(make_user):
    """
    Create a user and return (user_id, payload_dict) for use as get_current_user override.
    payload_dict has 'sub' = user_id (UUID string) so routes that resolve by sub work.
    """
    user = make_user()
    return str(user.id), {"sub": str(user.id), "email": user.email}


@pytest.fixture
def api_client(auth_user_payload, memory_db, monkeypatch: pytest.MonkeyPatch):
    """
    FastAPI TestClient with get_current_user overridden to return auth_user_payload.
    Requires memory_db so the app's lifespan uses the same in-memory DB. TESTING=1
    skips migrations and seeds in lifespan so the test-controlled schema is used.
    """
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    user_id, payload = auth_user_payload
    from fastapi.testclient import TestClient
    from authentication.middleware.deps import get_current_user

    def mock_get_current_user():
        return payload

    from main import app
    app.dependency_overrides[get_current_user] = mock_get_current_user
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture
def api_client_no_auth(memory_db, monkeypatch: pytest.MonkeyPatch):
    """TestClient without auth override; for public endpoints or 401 tests."""
    monkeypatch.setenv("TESTING", "1")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as client:
        yield client
