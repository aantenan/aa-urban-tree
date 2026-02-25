"""Form-filling agent: guidance and text extraction for pre-filling."""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth_deps import get_current_user
from services.form_agent_service import FormAgentService
from utils.responses import error_response

router = APIRouter(prefix="/form-agent", tags=["form-agent"])


class GuidanceQueryBody(BaseModel):
    section: str
    current_data: dict | None = None


class ExtractBody(BaseModel):
    section: str
    text: str


def _form_agent_service() -> FormAgentService:
    return FormAgentService()


@router.get("/guidance")
async def get_guidance(
    section: str,
    user: dict = Depends(get_current_user),
    svc: FormAgentService = Depends(_form_agent_service),
):
    """Get form guidance for a section: suggested next field, required fields, tips."""
    result = svc.get_guidance(section, current_data=None)
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.post("/guidance")
async def post_guidance(
    body: GuidanceQueryBody,
    user: dict = Depends(get_current_user),
    svc: FormAgentService = Depends(_form_agent_service),
):
    """Get form guidance with current form data to suggest next field."""
    result = svc.get_guidance(body.section, current_data=body.current_data)
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.post("/extract")
async def extract_from_text(
    body: ExtractBody,
    user: dict = Depends(get_current_user),
    svc: FormAgentService = Depends(_form_agent_service),
):
    """Extract form fields from pasted text for pre-filling (e.g. contact info)."""
    result = svc.extract_from_text(body.section, body.text)
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)
