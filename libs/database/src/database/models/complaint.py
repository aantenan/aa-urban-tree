"""Complaint model for citizen complaint processing."""
from peewee import CharField, ForeignKeyField, TextField

from database.models.base import BaseModel
from database.models.user import User


# Categories and departments used for routing and reporting
COMPLAINT_CATEGORIES = (
    "infrastructure",
    "environment",
    "safety",
    "noise",
    "parks",
    "housing",
    "other",
)

COMPLAINT_STATUSES = (
    "submitted",
    "acknowledged",
    "assigned",
    "in_progress",
    "resolved",
    "closed",
)


class Complaint(BaseModel):
    """
    Citizen complaint: submitted via conversational interface, routed by department,
    with status tracking and optional assignee.
    """

    # Submitter: optional FK for logged-in users; null for anonymous
    submitted_by = ForeignKeyField(User, backref="complaints", on_delete="SET NULL", null=True, default=None)
    category = CharField(max_length=64, index=True)  # e.g. infrastructure, environment
    department = CharField(max_length=128, index=True, null=True)  # responsible department (assigned)
    status = CharField(max_length=32, default="submitted", index=True)
    priority = CharField(max_length=16, default="normal")  # low, normal, high, urgent
    subject = CharField(max_length=255)
    description = TextField()
    location_or_reference = TextField(null=True, default=None)
    # Admin assignment and resolution
    assigned_to = ForeignKeyField(User, backref="assigned_complaints", on_delete="SET NULL", null=True, default=None)
    resolution_notes = TextField(null=True, default=None)
    # Optional external reference (e.g. legacy system id)
    external_id = CharField(max_length=128, null=True, default=None, index=True)

    class Meta:
        table_name = "complaints"
        indexes = (
            (("status",), False),
            (("category",), False),
            (("created_at",), False),
        )
