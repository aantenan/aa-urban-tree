"""Consistent API response formatting: success, message, data."""
from typing import Any


def api_response(
    *,
    success: bool = True,
    message: str | None = None,
    data: Any = None,
) -> dict[str, Any]:
    """Standard API response: success, message, data."""
    out: dict[str, Any] = {"success": success}
    if message is not None:
        out["message"] = message
    if data is not None:
        out["data"] = data
    return out


def success_response(data: Any = None, message: str | None = None) -> dict[str, Any]:
    """Success response with optional data and message."""
    return api_response(success=True, message=message, data=data)


def error_response(message: str, data: Any = None) -> dict[str, Any]:
    """Error response with message and optional extra data."""
    return api_response(success=False, message=message, data=data)
