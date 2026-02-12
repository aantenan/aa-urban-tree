"""Tests for ContactInformationService: get, put, validation, section completion."""
import pytest

from database.connection import database_proxy
from database.models import User, Application, ContactInformation, County
from services.contact_information_service import (
    ContactInformationService,
    is_contact_section_complete,
    _validate_contact_payload,
)


@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import database.connection as conn
    conn._db = None
    db = conn.get_db()
    database_proxy.initialize(db)
    db.create_tables([User, Application, ContactInformation, County])
    yield
    database_proxy.initialize(None)
    db.close()
    conn._db = None


@pytest.fixture
def service() -> ContactInformationService:
    return ContactInformationService()


@pytest.fixture
def user_id() -> str:
    user = User.create(email="c@example.com", password_hash="hash", account_status="active")
    return str(user.id)


@pytest.fixture
def application_id(user_id: str) -> str:
    app = Application.create(user_id=user_id, status="draft")
    return str(app.id)


VALID_PAYLOAD = {
    "organization_name": "Org Inc",
    "address_line1": "123 Main St",
    "address_line2": "",
    "city": "Albany",
    "state_code": "NY",
    "zip_code": "12207",
    "county": "Albany",
    "primary_contact_name": "Jane Doe",
    "primary_contact_title": "Director",
    "primary_contact_email": "jane@example.com",
    "primary_contact_phone": "518-555-1234",
    "alternate_contact_name": "",
    "alternate_contact_email": "",
    "alternate_contact_phone": "",
}


def test_get_contact_empty(service: ContactInformationService, application_id: str, user_id: str) -> None:
    result = service.get_contact(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["contact_information"] is None
    assert result["data"]["section_complete"] is False


def test_put_contact_creates_and_returns_section_complete(
    service: ContactInformationService, application_id: str, user_id: str
) -> None:
    result = service.put_contact(application_id, user_id, VALID_PAYLOAD)
    assert result["success"] is True
    assert result["data"]["section_complete"] is True
    assert result["data"]["contact_information"]["organization_name"] == "Org Inc"
    assert result["data"]["contact_information"]["primary_contact_email"] == "jane@example.com"


def test_get_contact_after_put(
    service: ContactInformationService, application_id: str, user_id: str
) -> None:
    service.put_contact(application_id, user_id, VALID_PAYLOAD)
    result = service.get_contact(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["contact_information"] is not None
    assert result["data"]["section_complete"] is True
    assert result["data"]["contact_information"]["county"] == "Albany"


def test_put_contact_validation_errors_returned(
    service: ContactInformationService, application_id: str, user_id: str
) -> None:
    payload = {"organization_name": "Only org", "primary_contact_email": "bad-email"}
    result = service.put_contact(application_id, user_id, payload)
    assert result["success"] is True
    assert result["data"]["section_complete"] is False
    errors = result["data"].get("errors") or {}
    assert "primary_contact_email" in errors or "address_line1" in errors or "primary_contact_name" in errors


def test_validate_contact_payload_valid() -> None:
    errors = _validate_contact_payload(VALID_PAYLOAD)
    assert len(errors) == 0


def test_validate_contact_payload_invalid_email() -> None:
    payload = {**VALID_PAYLOAD, "primary_contact_email": "not-an-email"}
    errors = _validate_contact_payload(payload)
    assert "primary_contact_email" in errors


def test_validate_contact_payload_invalid_phone() -> None:
    payload = {**VALID_PAYLOAD, "primary_contact_phone": "123"}
    errors = _validate_contact_payload(payload)
    assert "primary_contact_phone" in errors


def test_put_contact_application_not_found(service: ContactInformationService, user_id: str) -> None:
    import uuid
    result = service.put_contact(str(uuid.uuid4()), user_id, VALID_PAYLOAD)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_put_contact_wrong_user(
    service: ContactInformationService, application_id: str, user_id: str
) -> None:
    other = User.create(email="other@example.com", password_hash="x", account_status="active")
    result = service.put_contact(application_id, str(other.id), VALID_PAYLOAD)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_is_contact_section_complete_none() -> None:
    assert is_contact_section_complete(None) is False


def test_put_contact_updates_existing(
    service: ContactInformationService, application_id: str, user_id: str
) -> None:
    service.put_contact(application_id, user_id, VALID_PAYLOAD)
    updated = {**VALID_PAYLOAD, "organization_name": "Updated Org"}
    result = service.put_contact(application_id, user_id, updated)
    assert result["success"] is True
    assert result["data"]["contact_information"]["organization_name"] == "Updated Org"
