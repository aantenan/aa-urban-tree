"""Project type option for project information dropdown."""
from peewee import CharField

from database.models.base import BaseModel


class ProjectType(BaseModel):
    """Project type option (e.g. Park, Street tree)."""

    code = CharField(max_length=64, unique=True, index=True)
    label = CharField(max_length=128)

    class Meta:
        table_name = "project_type_options"
