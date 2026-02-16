"""Reference data: project type options for dropdowns."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database.models import ProjectType
from utils.responses import success_response

router = APIRouter(prefix="/project-types", tags=["reference"])


@router.get("")
async def list_project_types():
    """List project type options for project information dropdown."""
    options = ProjectType.select().order_by(ProjectType.label)
    data = [{"id": str(o.id), "code": o.code, "label": o.label} for o in options]
    return JSONResponse(content=success_response(data=data))
