"""Audit service: record security-relevant actions without PII."""
from uuid import UUID
from typing import Any

from database.models import AuditLog, User


def record_audit(
    action: str,
    user_id: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details_redacted: str | None = None,
    request: Any = None,
) -> None:
    """
    Record an audit log entry. Do not pass PII in details_redacted.
    request can be a Starlette Request for IP and User-Agent.
    """
    try:
        uid = UUID(user_id) if user_id else None
        if uid and not User.select().where(User.id == uid).exists():
            uid = None
    except (ValueError, TypeError):
        uid = None
    ip = None
    ua = None
    if request:
        ip = request.client.host if getattr(request, "client", None) else None
        ua = (request.headers.get("user-agent") or "")[:512]
    AuditLog.create(
        user_id=uid,
        action=action[:64],
        resource_type=resource_type[:64] if resource_type else None,
        resource_id=resource_id[:255] if resource_id else None,
        details_redacted=details_redacted,
        ip_address=ip,
        user_agent=ua,
    )
