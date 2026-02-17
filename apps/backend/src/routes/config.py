"""Public configuration API: program config (no authentication)."""
from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from config import PROGRAM_CONFIG_CACHE_MAX_AGE
from services.public_listing_service import PublicListingService


router = APIRouter(prefix="/config", tags=["config"])


def _config_service() -> PublicListingService:
    return PublicListingService()


@router.get("/program")
def get_program_config(
    response: Response,
    svc: PublicListingService = Depends(_config_service),
) -> JSONResponse:
    """
    Return complete program configuration for public listing.
    No authentication. Cached with appropriate cache headers.
    """
    try:
        config, etag = svc.get_program_config()
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"message": "Program configuration is not available."},
        )
    response.headers["Cache-Control"] = f"public, max-age={PROGRAM_CONFIG_CACHE_MAX_AGE}"
    response.headers["ETag"] = etag
    data = svc.get_program_config_api_response()
    return JSONResponse(content=data)
