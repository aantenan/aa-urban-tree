"""Forestry Board model: county-based board members with contact information."""
from peewee import CharField, ForeignKeyField, TextField

from database.models.base import BaseModel
from database.models.user import User


# Valid county values match ContactInformation.county (Maryland counties).
# No explicit enum in DB; application county must match board county for access.
COUNTY_VALID_MAX_LENGTH = 128


class ForestryBoard(BaseModel):
    """
    Forestry Board member: assigned to a county for application review.
    user_id links to User for authentication; when user logs in, they are a board member for this county.
    """

    user = ForeignKeyField(User, backref="forestry_board_assignments", on_delete="CASCADE", null=True)
    county = CharField(max_length=COUNTY_VALID_MAX_LENGTH, index=True)
    board_member_name = CharField(max_length=255)
    title = CharField(max_length=128, null=True)
    email = CharField(max_length=255, index=True)
    contact_info = TextField(null=True)

    class Meta:
        table_name = "forestry_board"
        indexes = (
            (("county",), False),
        )
