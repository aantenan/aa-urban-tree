"""Example service demonstrating WO-20 patterns: constructor injection, responses, testing."""
from typing import Any

from utils.responses import error_response, success_response


class ExampleService:
    """
    Example feature service with constructor-injected dependencies.
    Use this as a template for new services; test with mocks from utils.testing.
    """

    def __init__(self, email_service: Any = None) -> None:
        self.email_service = email_service

    def do_something(self, user_id: str, message: str) -> dict[str, Any]:
        """
        Pure method: inputs and return dict. Returns consistent success/error response shape.
        """
        if not (user_id or "").strip():
            return error_response("user_id is required", data={"code": "validation_error"})
        if self.email_service:
            self.email_service.send(
                to="admin@example.com",
                subject="Example notification",
                body_text=f"User {user_id}: {message}",
            )
        return success_response(
            data={"user_id": user_id, "message": message},
            message="Done",
        )
