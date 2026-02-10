"""Error handling and consistent API error responses."""
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return a consistent error payload."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal error occurred.",
            "type": type(exc).__name__,
        },
    )


def error_response(status_code: int, detail: str, **extra: Any) -> dict[str, Any]:
    """Build a consistent error body for validation or business errors."""
    body: dict[str, Any] = {"detail": detail}
    body.update(extra)
    return body
