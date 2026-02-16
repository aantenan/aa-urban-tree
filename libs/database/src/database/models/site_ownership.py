"""Site ownership option for project information dropdown."""
from peewee import CharField

from database.models.base import BaseModel


class SiteOwnership(BaseModel):
    """Site ownership option (e.g. Municipal, Non-profit)."""

    code = CharField(max_length=64, unique=True, index=True)
    label = CharField(max_length=128)

    class Meta:
        table_name = "site_ownership_options"
