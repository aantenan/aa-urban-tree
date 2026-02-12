"""User model for authentication."""
from peewee import CharField, ForeignKeyField

from database.models.base import BaseModel


class User(BaseModel):
    """User account: email (unique), password_hash, account_status."""

    email = CharField(unique=True, index=True, max_length=255)
    password_hash = CharField(max_length=255)
    account_status = CharField(max_length=32, default="active")  # active, locked, pending_confirmation

    class Meta:
        table_name = "users"
