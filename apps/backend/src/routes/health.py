"""Health check endpoint for monitoring."""
from fastapi import APIRouter, Query

router = APIRouter(tags=["health"])


def _check_db() -> str:
    try:
        from database.models import Application
        Application.select().limit(1)
        return "ok"
    except Exception as e:
        return f"error: {e!s}"


@router.get("/health")
def health(detail: bool = Query(False, description="Include DB and service checks")) -> dict:
    """Return service health status. Use ?detail=true for DB and optional checks."""
    out = {"status": "ok"}
    if detail:
        out["checks"] = {
            "database": _check_db(),
        }
        try:
            from core.container import get_storage
            get_storage()
            out["checks"]["storage"] = "ok"
        except Exception as e:
            out["checks"]["storage"] = f"error: {e!s}"
    return out
