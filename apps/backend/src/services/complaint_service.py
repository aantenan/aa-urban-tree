"""Complaint service: citizen complaint intake, categorization, routing, and admin workflow."""
from uuid import UUID
from typing import Any

from database.models import Complaint, User, COMPLAINT_CATEGORIES, COMPLAINT_STATUSES
from utils.responses import error_response, success_response


# Simple department routing by category (configurable / extendable)
CATEGORY_TO_DEPARTMENT: dict[str, str] = {
    "infrastructure": "Public Works",
    "environment": "Environmental Services",
    "safety": "Public Safety",
    "noise": "Code Enforcement",
    "parks": "Parks & Recreation",
    "housing": "Housing",
    "other": "General Inquiries",
}


class ComplaintService:
    """Citizen complaint processing: create, list, update status, assign."""

    def __init__(self) -> None:
        pass

    def submit_complaint(
        self,
        subject: str,
        description: str,
        category: str,
        user_id: str | None = None,
        location_or_reference: str | None = None,
    ) -> dict[str, Any]:
        """Submit a new complaint. Auto-assigns category, department, priority."""
        category = (category or "other").strip().lower()
        if category not in COMPLAINT_CATEGORIES:
            category = "other"
        department = CATEGORY_TO_DEPARTMENT.get(category, "General Inquiries")
        priority = "high" if any(kw in (subject + " " + description).lower() for kw in ("urgent", "emergency", "danger")) else "normal"

        submitted_by_id = None
        if user_id:
            try:
                submitted_by_id = UUID(user_id)
                if not User.select().where(User.id == submitted_by_id).exists():
                    submitted_by_id = None
            except (ValueError, TypeError):
                pass

        complaint = Complaint.create(
            subject=subject[:255],
            description=description,
            category=category,
            department=department,
            status="submitted",
            priority=priority,
            submitted_by_id=submitted_by_id,
            location_or_reference=location_or_reference,
        )
        return success_response(
            data=_complaint_to_dict(complaint),
            message="Complaint submitted. You can track status with your complaint ID.",
        )

    def get_complaint(self, complaint_id: str, user_id: str | None, admin: bool = False) -> dict[str, Any]:
        """Get a single complaint. Citizens see own; admins see any."""
        try:
            cid = UUID(complaint_id)
        except (ValueError, TypeError):
            return error_response("Invalid complaint ID", data={"code": "invalid_id"})
        try:
            complaint = Complaint.get_by_id(cid)
        except Complaint.DoesNotExist:
            return error_response("Complaint not found", data={"code": "not_found"})
        if not admin and complaint.submitted_by_id and user_id:
            try:
                uid = UUID(user_id)
                if complaint.submitted_by_id != uid:
                    return error_response("Complaint not found", data={"code": "not_found"})
            except (ValueError, TypeError):
                return error_response("Complaint not found", data={"code": "not_found"})
        if not admin and complaint.submitted_by_id and not user_id:
            return error_response("Complaint not found", data={"code": "not_found"})
        return success_response(data=_complaint_to_dict(complaint))

    def list_citizen_complaints(self, user_id: str) -> dict[str, Any]:
        """List complaints submitted by this user."""
        try:
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid user", data={"code": "invalid_user"})
        complaints = (
            Complaint.select()
            .where(Complaint.submitted_by_id == uid)
            .order_by(Complaint.created_at.desc())
        )
        return success_response(data=[_complaint_to_dict(c) for c in complaints])

    def list_admin_complaints(
        self,
        status: str | None = None,
        category: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> dict[str, Any]:
        """List all complaints for admin dashboard with optional filters."""
        q = Complaint.select().order_by(Complaint.created_at.desc())
        if status:
            q = q.where(Complaint.status == status)
        if category:
            q = q.where(Complaint.category == category)
        total = q.count()
        complaints = list(q.offset(offset).limit(limit))
        return success_response(
            data={
                "items": [_complaint_to_dict(c) for c in complaints],
                "total": total,
                "limit": limit,
                "offset": offset,
            }
        )

    def update_status(
        self,
        complaint_id: str,
        status: str,
        resolution_notes: str | None = None,
    ) -> dict[str, Any]:
        """Update complaint status (admin workflow)."""
        if status not in COMPLAINT_STATUSES:
            return error_response("Invalid status", data={"code": "invalid_status"})
        try:
            cid = UUID(complaint_id)
        except (ValueError, TypeError):
            return error_response("Invalid complaint ID", data={"code": "invalid_id"})
        try:
            complaint = Complaint.get_by_id(cid)
        except Complaint.DoesNotExist:
            return error_response("Complaint not found", data={"code": "not_found"})
        complaint.status = status
        if resolution_notes is not None:
            complaint.resolution_notes = resolution_notes
        complaint.save()
        return success_response(data=_complaint_to_dict(complaint), message="Status updated")

    def assign_complaint(self, complaint_id: str, assignee_id: str | None) -> dict[str, Any]:
        """Assign complaint to an admin user (or unassign)."""
        try:
            cid = UUID(complaint_id)
        except (ValueError, TypeError):
            return error_response("Invalid complaint ID", data={"code": "invalid_id"})
        if assignee_id:
            try:
                aid = UUID(assignee_id)
                if not User.select().where(User.id == aid).exists():
                    return error_response("Assignee not found", data={"code": "assignee_not_found"})
            except (ValueError, TypeError):
                return error_response("Invalid assignee", data={"code": "invalid_assignee"})
        try:
            complaint = Complaint.get_by_id(cid)
        except Complaint.DoesNotExist:
            return error_response("Complaint not found", data={"code": "not_found"})
        complaint.assigned_to_id = UUID(assignee_id) if assignee_id else None
        complaint.save()
        return success_response(data=_complaint_to_dict(complaint), message="Assignment updated")

    def get_categories(self) -> dict[str, Any]:
        """Return allowed complaint categories and departments for UI."""
        return success_response(
            data={
                "categories": list(COMPLAINT_CATEGORIES),
                "statuses": list(COMPLAINT_STATUSES),
                "category_departments": CATEGORY_TO_DEPARTMENT,
            }
        )


def _complaint_to_dict(c: Complaint) -> dict[str, Any]:
    return {
        "id": str(c.id),
        "subject": c.subject,
        "description": c.description,
        "category": c.category,
        "department": c.department,
        "status": c.status,
        "priority": c.priority,
        "location_or_reference": c.location_or_reference,
        "submitted_by_id": str(c.submitted_by_id) if c.submitted_by_id else None,
        "assigned_to_id": str(c.assigned_to_id) if c.assigned_to_id else None,
        "resolution_notes": c.resolution_notes,
        "external_id": c.external_id,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "updated_at": c.updated_at.isoformat() if c.updated_at else None,
    }
