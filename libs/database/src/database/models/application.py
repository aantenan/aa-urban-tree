"""Application model for grant applications."""
from peewee import CharField, DateTimeField, ForeignKeyField, TextField

from database.models.base import BaseModel
from database.models.user import User


class Application(BaseModel):
    """
    Grant application: belongs to a user, status draft or submitted.
    form_data: JSON string for section data (e.g. contact information).
    ready_for_board_review_at: when applicant marked ready for Forestry Board review.
    """

    user = ForeignKeyField(User, backref="applications", on_delete="CASCADE")
    status = CharField(max_length=32, default="draft", index=True)  # draft | submitted
    form_data = TextField(null=True, default=None)  # JSON string
    ready_for_board_review_at = DateTimeField(null=True, default=None)

    class Meta:
        table_name = "applications"
        indexes = (
            (("user_id",), False),
            (("created_at",), False),
        )
