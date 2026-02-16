"""Reference data: site ownership options for dropdowns."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database.models import SiteOwnership
from utils.responses import success_response

router = APIRouter(prefix="/site-ownership", tags=["reference"])


@router.get("")
async def list_site_ownership():
    """List site ownership options for project information dropdown."""
    options = SiteOwnership.select().order_by(SiteOwnership.label)
    data = [{"id": str(o.id), "code": o.code, "label": o.label} for o in options]
    return JSONResponse(content=success_response(data=data))
