"""Project information section: validation, get/put, section completion."""
from datetime import date
from typing import Any
from uuid import UUID

from database.models import Application, ProjectInformation, ProjectType, SiteOwnership, User
from utils.responses import error_response, success_response

ACREAGE_MIN = 0.01
ACREAGE_MAX = 10000.0
TREE_COUNT_MIN = 1
TREE_COUNT_MAX = 1_000_000


def _allowed_ownership_codes() -> set[str]:
    return {r.code for r in SiteOwnership.select(SiteOwnership.code)}


def _allowed_project_type_codes() -> set[str]:
    return {r.code for r in ProjectType.select(ProjectType.code)}


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    s = (value or "").strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _validate_project_payload(data: dict[str, Any]) -> dict[str, str]:
    """Validate project payload. Returns dict of field -> error message."""
    errors: dict[str, str] = {}

    project_name = (data.get("project_name") or "").strip()
    if not project_name:
        errors["project_name"] = "Project name is required"

    site_addr1 = (data.get("site_address_line1") or "").strip()
    if not site_addr1:
        errors["site_address_line1"] = "Site address is required"
    site_city = (data.get("site_city") or "").strip()
    if not site_city:
        errors["site_city"] = "Site city is required"
    site_state = (data.get("site_state_code") or "").strip()
    if not site_state:
        errors["site_state_code"] = "Site state is required"
    site_zip = (data.get("site_zip_code") or "").strip()
    if not site_zip:
        errors["site_zip_code"] = "Site ZIP code is required"

    site_ownership = (data.get("site_ownership") or "").strip()
    if not site_ownership:
        errors["site_ownership"] = "Site ownership is required"
    elif site_ownership and site_ownership not in _allowed_ownership_codes():
        errors["site_ownership"] = "Select a valid site ownership option"

    project_type = (data.get("project_type") or "").strip()
    if not project_type:
        errors["project_type"] = "Project type is required"
    elif project_type and project_type not in _allowed_project_type_codes():
        errors["project_type"] = "Select a valid project type"

    acreage = _parse_float(data.get("acreage"))
    if acreage is not None:
        if acreage < ACREAGE_MIN or acreage > ACREAGE_MAX:
            errors["acreage"] = f"Acreage must be between {ACREAGE_MIN} and {ACREAGE_MAX}"
    else:
        # Required for completion
        if data.get("acreage") is not None and (data.get("acreage") or "").strip() != "":
            errors["acreage"] = "Enter a valid number"
        else:
            errors["acreage"] = "Acreage is required"

    tree_count = _parse_int(data.get("tree_count"))
    if tree_count is not None:
        if tree_count < TREE_COUNT_MIN or tree_count > TREE_COUNT_MAX:
            errors["tree_count"] = f"Tree count must be between {TREE_COUNT_MIN} and {TREE_COUNT_MAX}"
    else:
        if data.get("tree_count") is not None and (data.get("tree_count") or "").strip() != "":
            errors["tree_count"] = "Enter a valid whole number"
        else:
            errors["tree_count"] = "Tree count is required"

    start_date = _parse_date(data.get("start_date"))
    completion_date = _parse_date(data.get("completion_date"))
    if start_date and completion_date and start_date > completion_date:
        errors["completion_date"] = "Completion date must be on or after start date"
    if not start_date:
        errors["start_date"] = "Start date is required"
    if not completion_date:
        errors["completion_date"] = "Completion date is required"

    description = (data.get("description") or "").strip()
    if not description:
        errors["description"] = "Project description is required"

    return errors


def _project_to_dict(p: ProjectInformation) -> dict[str, Any]:
    return {
        "project_name": p.project_name,
        "site_address_line1": p.site_address_line1,
        "site_address_line2": p.site_address_line2,
        "site_city": p.site_city,
        "site_state_code": p.site_state_code,
        "site_zip_code": p.site_zip_code,
        "site_ownership": p.site_ownership,
        "project_type": p.project_type,
        "acreage": p.acreage,
        "tree_count": p.tree_count,
        "start_date": p.start_date.isoformat() if p.start_date else None,
        "completion_date": p.completion_date.isoformat() if p.completion_date else None,
        "description": p.description,
    }


def is_project_section_complete(p: ProjectInformation | None) -> bool:
    """Return True if project section has all required fields and passes validation."""
    if not p:
        return False
    data = _project_to_dict(p)
    errors = _validate_project_payload(data)
    return len(errors) == 0


class ProjectInformationService:
    """Get and update project information; validation and section completion."""

    def __init__(self) -> None:
        pass

    def get_project(self, application_id: str, user_id: str) -> dict[str, Any]:
        """Get project information for application if it belongs to user."""
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
            return error_response("Application is not a draft", data={"code": "not_draft"})
        try:
            project = ProjectInformation.get(ProjectInformation.application_id == app.id)
        except ProjectInformation.DoesNotExist:
            return success_response(
                data={"project_information": None, "section_complete": False},
                message="No project information yet",
            )
        payload = _project_to_dict(project)
        return success_response(
            data={
                "project_information": payload,
                "section_complete": is_project_section_complete(project),
            },
        )

    def put_project(
        self, application_id: str, user_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Update project information (auto-save). Saves and returns validation errors + section_complete."""
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
        errors = _validate_project_payload(payload)

        def _v(k: str) -> str | None:
            val = (payload.get(k) or "").strip()
            return val or None

        start_d = _parse_date(payload.get("start_date"))
        comp_d = _parse_date(payload.get("completion_date"))
        acreage = _parse_float(payload.get("acreage"))
        tree_count = _parse_int(payload.get("tree_count"))

        project, created = ProjectInformation.get_or_create(
            application_id=app.id,
            defaults={
                "project_name": _v("project_name"),
                "site_address_line1": _v("site_address_line1"),
                "site_address_line2": _v("site_address_line2"),
                "site_city": _v("site_city"),
                "site_state_code": _v("site_state_code"),
                "site_zip_code": _v("site_zip_code"),
                "site_ownership": _v("site_ownership") or None,
                "project_type": _v("project_type") or None,
                "acreage": acreage,
                "tree_count": tree_count,
                "start_date": start_d,
                "completion_date": comp_d,
                "description": _v("description") or None,
            },
        )
        if not created:
            project.project_name = _v("project_name")
            project.site_address_line1 = _v("site_address_line1")
            project.site_address_line2 = _v("site_address_line2")
            project.site_city = _v("site_city")
            project.site_state_code = _v("site_state_code")
            project.site_zip_code = _v("site_zip_code")
            project.site_ownership = _v("site_ownership") or None
            project.project_type = _v("project_type") or None
            project.acreage = acreage
            project.tree_count = tree_count
            project.start_date = start_d
            project.completion_date = comp_d
            project.description = _v("description") or None
            project.save()
        return success_response(
            data={
                "project_information": _project_to_dict(project),
                "section_complete": len(errors) == 0,
                "errors": errors if errors else None,
            },
            message="Project information saved",
        )
