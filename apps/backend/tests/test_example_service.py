"""Example service tests: mocking dependencies (WO-20 unit testing utilities)."""
import pytest

from utils.testing import MockEmailService, mock_email_service
from services.example_service import ExampleService


def test_example_service_success_without_email() -> None:
    """Service works without optional email dependency."""
    svc = ExampleService()
    result = svc.do_something("user-1", "hello")
    assert result["success"] is True
    assert result["data"]["user_id"] == "user-1"
    assert result["data"]["message"] == "hello"
    assert result["message"] == "Done"


def test_example_service_sends_email_when_provided() -> None:
    """Constructor injection: pass mock email, assert it was used."""
    mock_email = mock_email_service()
    svc = ExampleService(email_service=mock_email)
    result = svc.do_something("user-2", "test message")
    assert result["success"] is True
    assert len(mock_email.sent) == 1
    assert mock_email.sent[0]["to"] == "admin@example.com"
    assert "user-2" in mock_email.sent[0]["body_text"]
    assert "test message" in mock_email.sent[0]["body_text"]


def test_example_service_validation_error() -> None:
    """Service returns consistent error response shape."""
    svc = ExampleService()
    result = svc.do_something("", "x")
    assert result["success"] is False
    assert "user_id" in result["message"]
    assert result["data"]["code"] == "validation_error"
