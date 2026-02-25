"""Complaint routes: citizen submission and status, admin management."""
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth_deps import get_current_user, get_current_user_optional
from config import ADMIN_EMAILS
from database.models import User
from services.complaint_service import ComplaintService
from utils.responses import error_response

router = APIRouter(prefix="/complaints", tags=["complaints"])


class SubmitComplaintBody(BaseModel):
    subject: str
    description: str
    category: str = "other"
    location_or_reference: str | None = None


class UpdateStatusBody(BaseModel):
    status: str
    resolution_notes: str | None = None


class AssignBody(BaseModel):
    assignee_id: str | None = None


def _resolve_user_id(payload: dict) -> str | None:
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


def _complaint_service() -> ComplaintService:
    return ComplaintService()


def _user_or_401(user: dict):
    user_id = _resolve_user_id(user)
    if not user_id:
        return None, JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response("User not found"),
        )
    return user_id, None


def _is_admin(user: dict) -> bool:
    email = (user.get("email") or "").strip().lower()
    if "@" in email:
        return email in ADMIN_EMAILS
    sub = user.get("sub")
    if not sub:
        return False
    try:
        u = User.get_by_id(UUID(str(sub)))
        return ((u.email or "").strip().lower()) in ADMIN_EMAILS
    except Exception:
        return False


# ---- Public / optional-auth: submit complaint ----
@router.post("/submit")
async def submit_complaint(
    body: SubmitComplaintBody,
    request: Request,
    user: dict | None = Depends(get_current_user_optional),
    svc: ComplaintService = Depends(_complaint_service),
):
    """Submit a complaint. Optional auth links complaint to user for tracking."""
    user_id = _resolve_user_id(user) if user else None
    result = svc.submit_complaint(
        subject=body.subject,
        description=body.description,
        category=body.category,
        user_id=user_id,
        location_or_reference=body.location_or_reference,
    )
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    try:
        from services.audit_service import record_audit
        complaint_id = (result.get("data") or {}).get("id")
        record_audit("complaint_submit", user_id=user_id, resource_type="complaint", resource_id=complaint_id, request=request)
    except Exception:
        pass
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)


# ---- Citizen: list my complaints, get one ----
@router.get("")
async def list_my_complaints(
    user: dict = Depends(get_current_user),
    svc: ComplaintService = Depends(_complaint_service),
):
    """List complaints submitted by the current user."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.list_citizen_complaints(user_id)
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/categories")
async def get_categories(svc: ComplaintService = Depends(_complaint_service)):
    """Return complaint categories and statuses for UI (public)."""
    return JSONResponse(content=svc.get_categories())


@router.get("/{complaint_id}")
async def get_complaint(
    complaint_id: str,
    user: dict = Depends(get_current_user),
    svc: ComplaintService = Depends(_complaint_service),
):
    """Get a complaint by ID (own only, unless admin)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    admin = _is_admin(user)
    result = svc.get_complaint(complaint_id, user_id, admin=admin)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


# ---- Admin: list all, update status, assign ----
@router.get("/admin/all")
async def list_all_complaints(
    status_filter: str | None = None,
    category: str | None = None,
    limit: int = 100,
    offset: int = 0,
    user: dict = Depends(get_current_user),
    svc: ComplaintService = Depends(_complaint_service),
):
    """List all complaints (admin only)."""
    _, err = _user_or_401(user)
    if err is not None:
        return err
    if not _is_admin(user):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Admin access required"),
        )
    result = svc.list_admin_complaints(status=status_filter, category=category, limit=limit, offset=offset)
    return JSONResponse(content=result)


@router.patch("/admin/{complaint_id}/status")
async def update_complaint_status(
    complaint_id: str,
    body: UpdateStatusBody,
    user: dict = Depends(get_current_user),
    svc: ComplaintService = Depends(_complaint_service),
):
    """Update complaint status (admin only)."""
    _, err = _user_or_401(user)
    if err is not None:
        return err
    if not _is_admin(user):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Admin access required"),
        )
    result = svc.update_status(complaint_id, body.status, resolution_notes=body.resolution_notes)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.patch("/admin/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: str,
    body: AssignBody,
    user: dict = Depends(get_current_user),
    svc: ComplaintService = Depends(_complaint_service),
):
    """Assign complaint to a user (admin only)."""
    _, err = _user_or_401(user)
    if err is not None:
        return err
    if not _is_admin(user):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Admin access required"),
        )
    result = svc.assign_complaint(complaint_id, body.assignee_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)
