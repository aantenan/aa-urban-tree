"""Public API routes: program configuration and public data query (no authentication)."""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import PROGRAM_CONFIG_CACHE_MAX_AGE
from services.program_config import get_cached_program_config
from services.public_data_query_service import PublicDataQueryService

router = APIRouter(prefix="/public", tags=["public"])


class DataQueryBody(BaseModel):
    query: str


@router.get("/config")
def get_program_config(response: Response) -> JSONResponse:
    """
    Serve program information for the public listing page.
    No authentication. Response is cacheable.
    """
    config, etag = get_cached_program_config()
    response.headers["Cache-Control"] = f"public, max-age={PROGRAM_CONFIG_CACHE_MAX_AGE}"
    response.headers["ETag"] = etag
    return JSONResponse(content=config.model_dump(mode="json"))


def _public_data_service() -> PublicDataQueryService:
    return PublicDataQueryService()


@router.get("/data/suggestions")
def get_data_query_suggestions() -> JSONResponse:
    """Return example natural language questions for public data (no auth)."""
    svc = _public_data_service()
    return JSONResponse(content=svc.list_suggestions())


@router.post("/data/query")
def post_data_query(body: DataQueryBody) -> JSONResponse:
    """Run a natural language public data query (read-only, no auth)."""
    svc = _public_data_service()
    result = svc.query(body.query)
    if not result.get("success"):
        return JSONResponse(status_code=400, content=result)
    return JSONResponse(content=result)


@router.get("/resources/{key:path}")
def get_public_resource(key: str) -> Response:
    """Serve a static resource (PDF, etc.) by storage key. No authentication."""
    try:
        from storage import get_storage
        backend = get_storage()
        data = backend.download(key)
        meta = backend.get_metadata(key)
        content_type = (meta and meta.content_type) or "application/octet-stream"
        return Response(content=data, media_type=content_type)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Resource not found")
