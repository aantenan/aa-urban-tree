"""Database connection pool and initialization."""
import os
from typing import Optional

from peewee import Database
from peewee import DatabaseProxy
from playhouse.db_url import connect

_db: Optional[Database] = None

# Proxy allows models to be defined before the database is initialized.
database_proxy: DatabaseProxy = DatabaseProxy()


def get_database_url() -> str:
    """Return DATABASE_URL from environment (default SQLite for development)."""
    return os.getenv("DATABASE_URL", "sqlite:///./local.db")


def get_db() -> Database:
    """Return the global database instance; initializes on first call."""
    global _db
    if _db is None:
        url = get_database_url()
        _db = connect(url)
    return _db


def init_db() -> Database:
    """Initialize database connection and bind proxy. Idempotent."""
    db = get_db()
    database_proxy.initialize(db)
    return db


def close_db() -> None:
    """Close the global database connection."""
    global _db
    if _db is not None:
        _db.close()
        _db = None
        database_proxy.initialize(None)
