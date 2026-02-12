"""Tests for ApplicationFormService."""
import pytest

from database.connection import database_proxy
from database.models import User, Application
from services.application_form_service import ApplicationFormService


@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import database.connection as conn
    conn._db = None
    db = conn.get_db()
    database_proxy.initialize(db)
    db.create_tables([User, Application])
    yield
    database_proxy.initialize(None)
    db.close()
    conn._db = None


@pytest.fixture
def service() -> ApplicationFormService:
    return ApplicationFormService()


@pytest.fixture
def user_id() -> str:
    user = User.create(email="app@example.com", password_hash="hash", account_status="active")
    return str(user.id)


def test_create_draft(service: ApplicationFormService, user_id: str) -> None:
    result = service.create_draft(user_id)
    assert result["success"] is True
    assert result["data"]["id"]
    assert result["data"]["status"] == "draft"
    assert result["data"]["user_id"] == user_id
    assert "created_at" in result["data"]
    assert "last_modified" in result["data"]


def test_create_draft_invalid_user_id(service: ApplicationFormService) -> None:
    result = service.create_draft("not-a-uuid")
    assert result["success"] is False
    assert result["data"]["code"] == "invalid_user"


def test_create_draft_user_not_found(service: ApplicationFormService) -> None:
    import uuid
    result = service.create_draft(str(uuid.uuid4()))
    assert result["success"] is False
    assert result["data"]["code"] == "user_not_found"


def test_get_application(service: ApplicationFormService, user_id: str) -> None:
    create = service.create_draft(user_id)
    app_id = create["data"]["id"]
    result = service.get_application(app_id, user_id)
    assert result["success"] is True
    assert result["data"]["id"] == app_id
    assert result["data"]["status"] == "draft"


def test_get_application_not_found(service: ApplicationFormService, user_id: str) -> None:
    import uuid
    result = service.get_application(str(uuid.uuid4()), user_id)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_get_application_wrong_user(service: ApplicationFormService, user_id: str) -> None:
    create = service.create_draft(user_id)
    app_id = create["data"]["id"]
    other = User.create(email="other@example.com", password_hash="x", account_status="active")
    result = service.get_application(app_id, str(other.id))
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_list_applications(service: ApplicationFormService, user_id: str) -> None:
    service.create_draft(user_id)
    service.create_draft(user_id)
    result = service.list_applications(user_id)
    assert result["success"] is True
    assert len(result["data"]) == 2


def test_update_application(service: ApplicationFormService, user_id: str) -> None:
    create = service.create_draft(user_id)
    app_id = create["data"]["id"]
    result = service.update_application(app_id, user_id, form_data={"contact": {"email": "a@b.com"}})
    assert result["success"] is True
    assert result["data"]["form_data"] == {"contact": {"email": "a@b.com"}}
