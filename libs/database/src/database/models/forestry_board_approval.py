"""Forestry Board approval model: approval actions with electronic signature and timestamps."""
from peewee import CharField, DateTimeField, ForeignKeyField, TextField

from database.models.application import Application
from database.models.base import BaseModel
from database.models.forestry_board import ForestryBoard


class ForestryBoardApproval(BaseModel):
    """
    Approval record: one per application, tracks current status.
    Status: pending, approved, revision_requested.
    Once approved, approval is immutable (no status change allowed).
    """

    application = ForeignKeyField(
        Application,
        backref="forestry_board_approvals",
        on_delete="CASCADE",
        unique=True,
    )
    board_member = ForeignKeyField(ForestryBoard, backref="approvals", on_delete="CASCADE")
    approval_date = DateTimeField(null=True)  # set when approved
    electronic_signature = TextField(null=True)  # typed name confirmation
    status = CharField(max_length=32, default="pending", index=True)  # pending | approved | revision_requested

    class Meta:
        table_name = "forestry_board_approval"
        indexes = (
            (("application_id",), False),
            (("board_member_id",), False),
        )
