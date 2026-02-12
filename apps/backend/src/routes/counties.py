"""Reference data: counties for dropdowns."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database.models import County
from utils.responses import success_response

router = APIRouter(prefix="/counties", tags=["reference"])


@router.get("")
async def list_counties():
    """List counties for dropdown options (e.g. contact information)."""
    counties = County.select().order_by(County.state_code, County.name)
    data = [{"id": str(c.id), "name": c.name, "state_code": c.state_code} for c in counties]
    return JSONResponse(content=success_response(data=data))
