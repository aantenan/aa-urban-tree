"""Public API routes: program configuration (no authentication)."""
from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse

from config import PROGRAM_CONFIG_CACHE_MAX_AGE
from services.program_config import get_cached_program_config

router = APIRouter(prefix="/public", tags=["public"])


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
