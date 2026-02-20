"""Revision request model: board member comments and history for applicant feedback."""
from peewee import ForeignKeyField, IntegerField, TextField

from database.models.application import Application
from database.models.base import BaseModel
from database.models.forestry_board import ForestryBoard


class RevisionRequest(BaseModel):
    """
    Revision request: application, board member, comments, request date, revision number.
    Tracks history of board feedback for applicant visibility.
    """

    application = ForeignKeyField(Application, backref="revision_requests", on_delete="CASCADE")
    board_member = ForeignKeyField(ForestryBoard, backref="revision_requests", on_delete="CASCADE")
    comments = TextField()
    revision_number = IntegerField(default=1)  # increment per application

    class Meta:
        table_name = "revision_request"
        indexes = (
            (("application_id",), False),
            (("board_member_id",), False),
        )
