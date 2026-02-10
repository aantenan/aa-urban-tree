"""Base model with UUID primary key and timestamps."""
import uuid
from datetime import datetime
from typing import Any

from peewee import DateTimeField, Model, UUIDField

from database.connection import database_proxy


class BaseModel(Model):
    """Base for all models: UUID primary key, created_at, updated_at."""

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = database_proxy
        table_settings = []

    def save(self, *args: Any, **kwargs: Any) -> int:
        """Override to set updated_at on every save."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
