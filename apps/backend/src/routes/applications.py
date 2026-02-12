"""Application form routes: create draft, get, list, update."""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from authentication.middleware.deps import get_current_user
from database.models import User
from services.application_form_service import ApplicationFormService
from utils.responses import error_response

router = APIRouter(prefix="/applications", tags=["applications"])


class UpdateApplicationBody(BaseModel):
    form_data: dict | None = None


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
