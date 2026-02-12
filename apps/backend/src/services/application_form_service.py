"""Application form service: create and retrieve applications (MVP)."""
import json
from typing import Any
from uuid import UUID

from database.models import Application, User
from utils.responses import error_response, success_response


class ApplicationFormService:
    """Create and retrieve applications; constructor injection for testability."""

    def __init__(self) -> None:
        pass

    def create_draft(self, user_id: str) -> dict[str, Any]:
        """
        Create a new draft application for the user.
        Returns consistent response: success, message, data.
        """
        try:
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid user", data={"code": "invalid_user"})
        if not User.select().where(User.id == uid).exists():
            return error_response("User not found", data={"code": "user_not_found"})
        app = Application.create(user_id=uid, status="draft")
        return success_response(
            data=_application_to_dict(app),
            message="Application created",
        )

    def get_application(self, application_id: str, user_id: str) -> dict[str, Any]:
        """
        Retrieve application by id if it belongs to the user.
        Returns consistent response with data or error.
        """
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        return success_response(data=_application_to_dict(app))

    def list_applications(self, user_id: str) -> dict[str, Any]:
        """List applications for the user (newest first)."""
        try:
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid user", data={"code": "invalid_user"})
        apps = Application.select().where(Application.user_id == uid).order_by(Application.created_at.desc())
        return success_response(data=[_application_to_dict(a) for a in apps])

    def update_application(
        self, application_id: str, user_id: str, form_data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Update draft application form_data. Returns updated application."""
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        if app.status != "draft":
            return error_response("Only draft applications can be updated", data={"code": "not_draft"})
        if form_data is not None:
            app.form_data = json.dumps(form_data) if form_data else None
            app.save()
        return success_response(data=_application_to_dict(app), message="Application updated")


def _application_to_dict(app: Application) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": str(app.id),
        "user_id": str(app.user_id),
        "status": app.status,
        "created_at": app.created_at.isoformat() + "Z" if app.created_at else None,
        "last_modified": app.updated_at.isoformat() + "Z" if app.updated_at else None,
    }
    if app.form_data:
        try:
            data["form_data"] = json.loads(app.form_data)
        except (TypeError, ValueError):
            data["form_data"] = None
    else:
        data["form_data"] = None
    return data
