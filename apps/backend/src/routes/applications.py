"""Application form routes: create draft, get, list, update, contact-information."""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth_deps import get_current_user
from database.models import User
from routes import documents as documents_routes
from services.application_form_service import ApplicationFormService
from services.forestry_board_service import ForestryBoardService
from services.contact_information_service import ContactInformationService
from services.project_information_service import ProjectInformationService
from services.financial_information_service import FinancialInformationService
from utils.responses import error_response

router = APIRouter(prefix="/applications", tags=["applications"])

# Document management: must be included so path /{application_id}/documents is under applications
router.include_router(
    documents_routes.router,
    prefix="/{application_id}/documents",
    tags=["documents"],
)


class UpdateApplicationBody(BaseModel):
    form_data: dict | None = None


class ContactInformationBody(BaseModel):
    organization_name: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_code: str | None = None
    zip_code: str | None = None
    county: str | None = None
    primary_contact_name: str | None = None
    primary_contact_title: str | None = None
    primary_contact_email: str | None = None
    primary_contact_phone: str | None = None
    alternate_contact_name: str | None = None
    alternate_contact_title: str | None = None
    alternate_contact_email: str | None = None
    alternate_contact_phone: str | None = None


class ProjectInformationBody(BaseModel):
    project_name: str | None = None
    site_address_line1: str | None = None
    site_address_line2: str | None = None
    site_city: str | None = None
    site_state_code: str | None = None
    site_zip_code: str | None = None
    site_ownership: str | None = None
    project_type: str | None = None
    acreage: float | None = None
    tree_count: int | None = None
    start_date: str | None = None
    completion_date: str | None = None
    description: str | None = None


class FinancialInformationBody(BaseModel):
    total_project_cost: float | None = None
    grant_amount_requested: float | None = None
    matching_funds: list[dict] | None = None
    line_item_budget: list[dict] | None = None


def _resolve_user_id(payload: dict) -> str | None:
    """Resolve user id from JWT payload: sub may be UUID (JWT) or email (mock)."""
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        UUID(str(sub))
        return str(sub)
    except (ValueError, TypeError):
        pass
    email = (sub or "").strip().lower()
    try:
        user = User.get(User.email == email)
        return str(user.id)
    except User.DoesNotExist:
        return None


def _application_form_service() -> ApplicationFormService:
    return ApplicationFormService()


def _contact_information_service() -> ContactInformationService:
    return ContactInformationService()


def _project_information_service() -> ProjectInformationService:
    return ProjectInformationService()


def _financial_information_service() -> FinancialInformationService:
    return FinancialInformationService()


def _forestry_board_service() -> ForestryBoardService:
    return ForestryBoardService()


def _user_or_401(user: dict):
    user_id = _resolve_user_id(user)
    if not user_id:
        return None, JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response("User not found"),
        )
    return user_id, None


@router.post("")
async def create_application(
    user: dict = Depends(get_current_user),
    svc: ApplicationFormService = Depends(_application_form_service),
):
    """Create a new draft application for the current user."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.create_draft(user_id)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "user_not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)


@router.get("")
async def list_applications(
    user: dict = Depends(get_current_user),
    svc: ApplicationFormService = Depends(_application_form_service),
):
    """List current user's applications."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.list_applications(user_id)
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/{application_id}")
async def get_application(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ApplicationFormService = Depends(_application_form_service),
):
    """Retrieve application by id if it belongs to the current user."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.get_application(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.patch("/{application_id}")
async def update_application(
    application_id: str,
    body: UpdateApplicationBody,
    user: dict = Depends(get_current_user),
    svc: ApplicationFormService = Depends(_application_form_service),
):
    """Update draft application form data."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.update_application(application_id, user_id, form_data=body.form_data)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "not_draft":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/{application_id}/contact-information")
async def get_contact_information(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ContactInformationService = Depends(_contact_information_service),
):
    """Get contact information section for the application."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.get_contact(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.put("/{application_id}/contact-information")
async def put_contact_information(
    application_id: str,
    body: ContactInformationBody,
    user: dict = Depends(get_current_user),
    svc: ContactInformationService = Depends(_contact_information_service),
):
    """Update contact information (auto-save). Returns validation errors and section_complete."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    payload = body.model_dump(exclude_none=True)
    result = svc.put_contact(application_id, user_id, payload)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "not_draft":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/{application_id}/project-information")
async def get_project_information(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ProjectInformationService = Depends(_project_information_service),
):
    """Get project information section for the application."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.get_project(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.put("/{application_id}/project-information")
async def put_project_information(
    application_id: str,
    body: ProjectInformationBody,
    user: dict = Depends(get_current_user),
    svc: ProjectInformationService = Depends(_project_information_service),
):
    """Update project information (auto-save). Returns validation errors and section_complete."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    payload = body.model_dump(exclude_none=True)
    result = svc.put_project(application_id, user_id, payload)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "not_draft":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/{application_id}/financial-information")
async def get_financial_information(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: FinancialInformationService = Depends(_financial_information_service),
):
    """Get financial information section (with server-computed cost-match percentage)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.get_financial(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.put("/{application_id}/financial-information")
async def put_financial_information(
    application_id: str,
    body: FinancialInformationBody,
    user: dict = Depends(get_current_user),
    svc: FinancialInformationService = Depends(_financial_information_service),
):
    """Update financial information (auto-save). Cost-match % computed server-side. Returns errors and section_complete."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    payload = body.model_dump(exclude_none=True)
    result = svc.put_financial(application_id, user_id, payload)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "not_draft":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.post("/{application_id}/mark-ready-for-board-review")
async def mark_ready_for_board_review(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
):
    """Mark application ready for Forestry Board review."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.mark_ready_for_board_review(application_id, user_id)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/{application_id}/forestry-board-approval-status")
async def get_forestry_board_approval_status(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
):
    """Get Forestry Board approval status for the application."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.get_approval_status(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)
