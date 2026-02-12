"""Error handling and consistent API error responses (success, message, data)."""
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from utils.responses import api_response


def format_validation_errors(errors: list[Any]) -> list[dict[str, Any]]:
    """Format Pydantic validation errors for API response data."""
    out = []
    for e in errors:
        loc = getattr(e, "loc", None) or (e.get("loc") if isinstance(e, dict) else [])
        msg = getattr(e, "msg", None) or (e.get("msg") if isinstance(e, dict) else "Validation error")
        typ = getattr(e, "type", None) or (e.get("type") if isinstance(e, dict) else None)
        out.append({"loc": list(loc), "msg": msg, "type": typ})
    return out


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation failures with consistent success/message/data format."""
    errors = format_validation_errors(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=api_response(
            success=False,
            message="Validation failed",
            data={"errors": errors},
        ),
    )


async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch unhandled exceptions and return a consistent error payload."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=api_response(
            success=False,
            message="An internal error occurred.",
            data={"type": type(exc).__name__} if __debug__ else None,
        ),
    )


def error_response(status_code: int, detail: str, **extra: Any) -> dict[str, Any]:
    """Build a consistent error body for validation or business errors (legacy shape)."""
    body: dict[str, Any] = {"detail": detail}
    body.update(extra)
    return body
