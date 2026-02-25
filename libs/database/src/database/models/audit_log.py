"""Audit log for sensitive actions (no PII stored in action_details)."""
from peewee import CharField, DateTimeField, ForeignKeyField, TextField

from database.models.base import BaseModel
from database.models.user import User


class AuditLog(BaseModel):
    """
    Audit trail for security-relevant actions. Stores action type and
    optional non-PII context (e.g. resource type and id). Do not store
    PII or full request bodies here.
    """

    user = ForeignKeyField(User, backref="audit_logs", on_delete="SET NULL", null=True, default=None)
    action = CharField(max_length=64, index=True)  # e.g. login, application_submit, complaint_submit
    resource_type = CharField(max_length=64, null=True, default=None)  # e.g. application, complaint
    resource_id = CharField(max_length=255, null=True, default=None)  # UUID or reference, no PII
    details_redacted = TextField(null=True, default=None)  # optional non-PII context (JSON or text)
    ip_address = CharField(max_length=45, null=True, default=None)
    user_agent = CharField(max_length=512, null=True, default=None)

    class Meta:
        table_name = "audit_logs"
        indexes = (
            (("action",), False),
            (("created_at",), False),
        )
