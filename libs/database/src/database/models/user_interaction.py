"""User interaction model for preference capture and personalization."""
from peewee import CharField, ForeignKeyField, TextField

from database.models.base import BaseModel
from database.models.user import User


class UserInteraction(BaseModel):
    """
    Records user interactions (page views, form sections, service usage)
    for learning preferences and powering personalized recommendations.
    """

    user = ForeignKeyField(User, backref="interactions", on_delete="CASCADE")
    interaction_type = CharField(max_length=64, index=True)  # e.g. page_view, form_section, service_used
    target_id = CharField(max_length=255, null=True, default=None)  # e.g. page path, section id, service id
    metadata_json = TextField(null=True, default=None)  # optional JSON for extra context

    class Meta:
        table_name = "user_interactions"
        indexes = (
            (("user_id", "interaction_type"), False),
            (("created_at",), False),
        )
