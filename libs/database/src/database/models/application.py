"""Application model for grant applications."""
from peewee import CharField, ForeignKeyField, TextField

from database.models.base import BaseModel
from database.models.user import User


class Application(BaseModel):
    """
    Grant application: belongs to a user, status draft or submitted.
    form_data: JSON string for section data (e.g. contact information).
    """

    user = ForeignKeyField(User, backref="applications", on_delete="CASCADE")
    status = CharField(max_length=32, default="draft", index=True)  # draft | submitted
    form_data = TextField(null=True, default=None)  # JSON string

    class Meta:
        table_name = "applications"
        indexes = (
            (("user_id",), False),
            (("created_at",), False),
        )
