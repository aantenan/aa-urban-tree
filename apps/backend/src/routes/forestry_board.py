"""Forestry Board approval routes: list, get, approve, request revision, documents (board member only)."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from auth_deps import get_current_user
from database.models import User, ForestryBoard
from services.forestry_board_service import ForestryBoardService
from services.document_management_service import DocumentManagementService
from utils.responses import error_response


router = APIRouter(prefix="/board", tags=["forestry-board"])


class ApproveBody(BaseModel):
    boardMemberName: str
    boardMemberTitle: str | None = None
    approvalDate: str  # ISO 8601


class RequestRevisionBody(BaseModel):
    comments: str


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


def _get_board_member_for_user(user_id: str) -> ForestryBoard | None:
    try:
        return ForestryBoard.get(ForestryBoard.user_id == UUID(user_id))
    except (ForestryBoard.DoesNotExist, ValueError, TypeError):
        return None


def _forestry_board_service() -> ForestryBoardService:
    return ForestryBoardService()


def _document_service() -> DocumentManagementService:
    try:
        from core.container import get_malware_scanner, get_storage
        return DocumentManagementService(storage=get_storage(), malware_scanner=get_malware_scanner())
    except Exception:
        from utils.testing import mock_malware_scanner, mock_storage_backend
        return DocumentManagementService(storage=mock_storage_backend(), malware_scanner=mock_malware_scanner())


def _user_or_401(user: dict):
    user_id = _resolve_user_id(user)
    if not user_id:
        return None, JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response("User not found"),
        )
    return user_id, None


@router.get("/board-members/me/applications")
async def list_my_board_applications(
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
):
    """List applications from board member's county (board member only)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    board = _get_board_member_for_user(user_id)
    if not board:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Not a forestry board member"),
        )
    result = svc.list_applications_for_board_member(str(board.id))
    return JSONResponse(content=result)


@router.get("/board-members/me/applications/{application_id}")
async def get_application_for_review(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
):
    """Get full application details for board review (board member only)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    board = _get_board_member_for_user(user_id)
    if not board:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Not a forestry board member"),
        )
    result = svc.get_application_for_board_member(str(board.id), application_id)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "access_denied":
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.post("/board-members/me/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    body: ApproveBody,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
):
    """Approve application with electronic signature (board member only)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    board = _get_board_member_for_user(user_id)
    if not board:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Not a forestry board member"),
        )
    try:
        approval_dt = datetime.fromisoformat(body.approvalDate.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response("Invalid approval date format"),
        )
    result = svc.approve(
        str(board.id),
        application_id,
        body.boardMemberName,
        body.boardMemberTitle,
        approval_dt,
    )
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "access_denied":
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=result)
        if code == "already_approved":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.post("/board-members/me/applications/{application_id}/request-revision")
async def request_revision(
    application_id: str,
    body: RequestRevisionBody,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
):
    """Request revisions with comments (board member only)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    board = _get_board_member_for_user(user_id)
    if not board:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Not a forestry board member"),
        )
    result = svc.request_revision(str(board.id), application_id, body.comments)
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "access_denied":
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/board-members/me/applications/{application_id}/documents")
async def list_board_application_documents(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
    doc_svc: DocumentManagementService = Depends(_document_service),
):
    """List documents for application (board member only, county access checked via get)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    board = _get_board_member_for_user(user_id)
    if not board:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Not a forestry board member"),
        )
    check = svc.get_application_for_board_member(str(board.id), application_id)
    if not check.get("success"):
        code = (check.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=check)
        if code == "access_denied":
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=check)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=check)
    result = doc_svc.list_documents_for_application(application_id)
    return JSONResponse(content=result)


@router.get("/board-members/me/applications/{application_id}/documents/{document_id}")
async def download_board_application_document(
    application_id: str,
    document_id: str,
    user: dict = Depends(get_current_user),
    svc: ForestryBoardService = Depends(_forestry_board_service),
    doc_svc: DocumentManagementService = Depends(_document_service),
):
    """Download document (board member only, county access checked)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    board = _get_board_member_for_user(user_id)
    if not board:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response("Not a forestry board member"),
        )
    check = svc.get_application_for_board_member(str(board.id), application_id)
    if not check.get("success"):
        code = (check.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=check)
        if code == "access_denied":
            return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content=check)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=check)
    content, filename, content_type, err_res = doc_svc.download_document_for_application(application_id, document_id)
    if err_res is not None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND if (err_res.get("data") or {}).get("code") == "not_found" else status.HTTP_400_BAD_REQUEST,
            content=err_res,
        )
    return Response(
        content=content,
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename or "document"}"'},
    )
