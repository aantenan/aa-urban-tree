"""Tests for base model."""
import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from peewee import SqliteDatabase

from database.connection import database_proxy
from database.models import BaseModel


@pytest.fixture
def in_memory_db() -> SqliteDatabase:
    """Use an in-memory SQLite database for tests."""
    db = SqliteDatabase(":memory:")
    database_proxy.initialize(db)
    yield db
    database_proxy.initialize(None)
    db.close()


def test_base_model_has_uuid_and_timestamps(in_memory_db: SqliteDatabase) -> None:
    """BaseModel defines id, created_at, updated_at."""
    class TestModel(BaseModel):
        class Meta:
            table_name = "test_model"
    in_memory_db.create_tables([TestModel])
    m = TestModel.create()
    assert m.id is not None
    assert isinstance(m.id, uuid.UUID)
    assert isinstance(m.created_at, datetime)
    assert isinstance(m.updated_at, datetime)
    m.save()
    assert m.updated_at >= m.created_at
