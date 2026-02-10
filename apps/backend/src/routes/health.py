"""Health check endpoint for monitoring."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Return service health status."""
    return {"status": "ok"}
