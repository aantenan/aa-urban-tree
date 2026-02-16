"""Tests for ProjectInformationService: get, put, validation, section completion."""
import pytest

from database.connection import database_proxy
from database.models import (
    User,
    Application,
    ProjectInformation,
    SiteOwnership,
    ProjectType,
)
from services.project_information_service import (
    ProjectInformationService,
    is_project_section_complete,
    _validate_project_payload,
)


@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import database.connection as conn
    conn._db = None
    db = conn.get_db()
    database_proxy.initialize(db)
    db.create_tables([User, Application, ProjectInformation, SiteOwnership, ProjectType])
    # Seed options so validation passes
    SiteOwnership.get_or_create(code="municipal", defaults={"label": "Municipal"})
    SiteOwnership.get_or_create(code="nonprofit", defaults={"label": "Non-profit"})
    ProjectType.get_or_create(code="park", defaults={"label": "Park"})
    ProjectType.get_or_create(code="street", defaults={"label": "Street tree"})
    yield
    database_proxy.initialize(None)
    db.close()
    conn._db = None


@pytest.fixture
def service() -> ProjectInformationService:
    return ProjectInformationService()


@pytest.fixture
def user_id() -> str:
    user = User.create(email="p@example.com", password_hash="hash", account_status="active")
    return str(user.id)


@pytest.fixture
def application_id(user_id: str) -> str:
    app = Application.create(user_id=user_id, status="draft")
    return str(app.id)


VALID_PAYLOAD = {
    "project_name": "Riverside Park Trees",
    "site_address_line1": "100 River Rd",
    "site_address_line2": "",
    "site_city": "Albany",
    "site_state_code": "NY",
    "site_zip_code": "12207",
    "site_ownership": "municipal",
    "project_type": "park",
    "acreage": 2.5,
    "tree_count": 50,
    "start_date": "2025-03-01",
    "completion_date": "2025-11-30",
    "description": "Plant 50 trees along the river trail.",
}


def test_get_project_empty(service: ProjectInformationService, application_id: str, user_id: str) -> None:
    result = service.get_project(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["project_information"] is None
    assert result["data"]["section_complete"] is False


def test_put_project_creates_and_returns_section_complete(
    service: ProjectInformationService, application_id: str, user_id: str
) -> None:
    result = service.put_project(application_id, user_id, VALID_PAYLOAD)
    assert result["success"] is True
    assert result["data"]["section_complete"] is True
    assert result["data"]["project_information"]["project_name"] == "Riverside Park Trees"
    assert result["data"]["project_information"]["acreage"] == 2.5
    assert result["data"]["project_information"]["tree_count"] == 50


def test_get_project_after_put(
    service: ProjectInformationService, application_id: str, user_id: str
) -> None:
    service.put_project(application_id, user_id, VALID_PAYLOAD)
    result = service.get_project(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["project_information"] is not None
    assert result["data"]["section_complete"] is True
    assert result["data"]["project_information"]["start_date"] == "2025-03-01"
    assert result["data"]["project_information"]["completion_date"] == "2025-11-30"


def test_validate_timeline_start_after_completion() -> None:
    payload = {**VALID_PAYLOAD, "start_date": "2025-12-01", "completion_date": "2025-06-01"}
    errors = _validate_project_payload(payload)
    assert "completion_date" in errors


def test_validate_acreage_range() -> None:
    payload = {**VALID_PAYLOAD, "acreage": 0.001}
    errors = _validate_project_payload(payload)
    assert "acreage" in errors
    payload2 = {**VALID_PAYLOAD, "acreage": 15000}
    errors2 = _validate_project_payload(payload2)
    assert "acreage" in errors2


def test_validate_tree_count_range() -> None:
    payload = {**VALID_PAYLOAD, "tree_count": 0}
    errors = _validate_project_payload(payload)
    assert "tree_count" in errors


def test_validate_project_type_invalid() -> None:
    payload = {**VALID_PAYLOAD, "project_type": "invalid_type"}
    errors = _validate_project_payload(payload)
    assert "project_type" in errors


def test_validate_site_ownership_invalid() -> None:
    payload = {**VALID_PAYLOAD, "site_ownership": "invalid_ownership"}
    errors = _validate_project_payload(payload)
    assert "site_ownership" in errors


def test_put_project_application_not_found(service: ProjectInformationService, user_id: str) -> None:
    import uuid
    result = service.put_project(str(uuid.uuid4()), user_id, VALID_PAYLOAD)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_put_project_wrong_user(
    service: ProjectInformationService, application_id: str, user_id: str
) -> None:
    other = User.create(email="other@example.com", password_hash="x", account_status="active")
    result = service.put_project(application_id, str(other.id), VALID_PAYLOAD)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_is_project_section_complete_none() -> None:
    assert is_project_section_complete(None) is False


def test_put_project_updates_existing(
    service: ProjectInformationService, application_id: str, user_id: str
) -> None:
    service.put_project(application_id, user_id, VALID_PAYLOAD)
    updated = {**VALID_PAYLOAD, "project_name": "Updated Project Name", "tree_count": 75}
    result = service.put_project(application_id, user_id, updated)
    assert result["success"] is True
    assert result["data"]["project_information"]["project_name"] == "Updated Project Name"
    assert result["data"]["project_information"]["tree_count"] == 75
