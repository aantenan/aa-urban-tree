"""County model for dropdown options (e.g. contact information)."""
from peewee import CharField

from database.models.base import BaseModel


class County(BaseModel):
    """County option for forms. Seed with county names for the program area."""

    name = CharField(max_length=128, index=True)
    state_code = CharField(max_length=2, default="", index=True)  # e.g. NY

    class Meta:
        table_name = "counties"
        indexes = ((("name", "state_code"), False),)
