"""
Test data factories: create User, Application, and related records for tests.
Caller must ensure database is initialized and tables exist (e.g. use memory_db fixture).
"""
from uuid import uuid4

from database.models import Application, User


def create_user(
    email: str | None = None,
    password_hash: str = "hash",
    account_status: str = "active",
    **kwargs,
) -> User:
    """Create a User. Default email is unique per call."""
    email = email or f"user-{uuid4().hex[:8]}@example.com"
    return User.create(
        email=email,
        password_hash=password_hash,
        account_status=account_status,
        **kwargs,
    )


def create_application(
    user_id: str | None = None,
    user: User | None = None,
    status: str = "draft",
    **kwargs,
) -> Application:
    """Create a draft Application. Provide either user_id or user."""
    if user is not None:
        user_id = str(user.id)
    if user_id is None:
        user = create_user()
        user_id = str(user.id)
    return Application.create(user_id=user_id, status=status, **kwargs)
