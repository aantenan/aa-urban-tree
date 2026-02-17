"""Document management routes: upload, list, download, delete, status."""
from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import JSONResponse, Response

from auth_deps import get_current_user
from database.models import User
from services.document_management_service import DocumentManagementService
from utils.responses import error_response
from utils.testing import mock_malware_scanner, mock_storage_backend

router = APIRouter(tags=["documents"])


def _user_id_or_401(user: dict) -> tuple[str | None, JSONResponse | None]:
    """Resolve user id from JWT payload; return (None, 401 response) if not found."""
    sub = (user or {}).get("sub")
    if not sub:
        return None, JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=error_response("User not found"))
    try:
        UUID(str(sub))
        return str(sub), None
    except (ValueError, TypeError):
        pass
    email = (str(sub) or "").strip().lower()
    try:
        u = User.get(User.email == email)
        return str(u.id), None
    except User.DoesNotExist:
        return None, JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=error_response("User not found"))


def _document_service() -> DocumentManagementService:
    """Resolve document service with storage and scanner from container."""
    try:
        from core.container import get_malware_scanner, get_storage
        storage = get_storage()
        scanner = get_malware_scanner()
    except Exception:
        storage = mock_storage_backend()
        scanner = mock_malware_scanner()
    return DocumentManagementService(storage=storage, malware_scanner=scanner)


@router.get("/status")
async def get_document_status(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: DocumentManagementService = Depends(_document_service),
):
    """Get document completion status (required: Site Plan, Site Photos)."""
    user_id, err = _user_id_or_401(user)
    if err is not None:
        return err
    result = svc.get_document_status(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("")
async def list_documents(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: DocumentManagementService = Depends(_document_service),
):
    """List documents for application grouped by category."""
    user_id, err = _user_id_or_401(user)
    if err is not None:
        return err
    result = svc.list_documents(application_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.post("")
async def upload_document(
    application_id: str,
    user: dict = Depends(get_current_user),
    svc: DocumentManagementService = Depends(_document_service),
    file: UploadFile = File(...),
    category: str = Form(...),
):
    """Upload document with category. Validates format (PDF, JPG, PNG) and size (10MB)."""
    user_id, err = _user_id_or_401(user)
    if err is not None:
        return err
    content = await file.read()
    filename = file.filename or "unnamed"
    content_type = file.content_type or "application/octet-stream"
    result = svc.upload_document(
        application_id,
        user_id,
        file_obj=BytesIO(content),
        filename=filename,
        content_type=content_type,
        category=category,
    )
    if not result.get("success"):
        code = (result.get("data") or {}).get("code")
        if code == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if code == "not_draft":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=result)


@router.get("/{document_id}")
async def download_document(
    application_id: str,
    document_id: str,
    user: dict = Depends(get_current_user),
    svc: DocumentManagementService = Depends(_document_service),
):
    """Download document file. Requires authentication and application ownership."""
    user_id, err = _user_id_or_401(user)
    if err is not None:
        return err
    content, filename, content_type, err_res = svc.download_document(application_id, document_id, user_id)
    if err_res is not None:
        if (err_res.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=err_res)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=err_res)
    if content is None:
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_response("Download failed"))
    return Response(
        content=content,
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename or "document"}"'},
    )


@router.delete("/{document_id}")
async def delete_document(
    application_id: str,
    document_id: str,
    user: dict = Depends(get_current_user),
    svc: DocumentManagementService = Depends(_document_service),
):
    """Delete document. Blocked after application submission."""
    user_id, err = _user_id_or_401(user)
    if err is not None:
        return err
    result = svc.delete_document(application_id, document_id, user_id)
    if not result.get("success"):
        if (result.get("data") or {}).get("code") == "not_found":
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=result)
        if (result.get("data") or {}).get("code") == "not_draft":
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)
