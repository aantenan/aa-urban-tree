"""Tests for FinancialInformationService: get, put, validation, cost-match %, section completion."""
import uuid

import pytest

from database.connection import database_proxy
from database.models import (
    User,
    Application,
    FinancialInformation,
    BudgetCategory,
)
from services.financial_information_service import (
    FinancialInformationService,
    compute_cost_match_percentage,
    is_financial_section_complete,
    _validate_financial_payload,
    _validate_matching_funds,
    _validate_line_items,
)


def _seed_budget_categories() -> None:
    for code, label in [
        ("labor", "Labor"),
        ("materials", "Materials"),
        ("equipment", "Equipment"),
        ("contractors", "Contractors"),
        ("other", "Other"),
    ]:
        BudgetCategory.get_or_create(code=code, defaults={"label": label})


@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    import database.connection as conn
    conn._db = None
    db = conn.get_db()
    database_proxy.initialize(db)
    db.create_tables([User, Application, FinancialInformation, BudgetCategory])
    _seed_budget_categories()
    yield
    database_proxy.initialize(None)
    db.close()
    conn._db = None


@pytest.fixture
def service() -> FinancialInformationService:
    return FinancialInformationService()


@pytest.fixture
def user_id() -> str:
    user = User.create(email="p@example.com", password_hash="hash", account_status="active")
    return str(user.id)


@pytest.fixture
def application_id(user_id: str) -> str:
    app = Application.create(user_id=user_id, status="draft")
    return str(app.id)


# total 100k, grant 75k -> matching 25k -> 25% cost-match (>= 20%)
VALID_PAYLOAD = {
    "total_project_cost": 100_000.0,
    "grant_amount_requested": 75_000.0,
    "matching_funds": [
        {"source_name": "City match", "amount": 15_000.0, "type": "cash"},
        {"source_name": "Donated labor", "amount": 10_000.0, "type": "in_kind"},
    ],
    "line_item_budget": [
        {"category": "labor", "description": "Staff", "amount": 40_000.0},
        {"category": "materials", "description": "Trees and supplies", "amount": 35_000.0},
        {"category": "equipment", "description": "Tools", "amount": 25_000.0},
    ],
}


def test_compute_cost_match_percentage() -> None:
    assert compute_cost_match_percentage(100.0, 25.0) == 25.0
    assert compute_cost_match_percentage(100.0, 20.0) == 20.0
    assert compute_cost_match_percentage(100.0, 0.0) == 0.0
    assert compute_cost_match_percentage(0.0, 10.0) is None
    assert compute_cost_match_percentage(100.0, 100.0) == 100.0


def test_get_financial_empty(service: FinancialInformationService, application_id: str, user_id: str) -> None:
    result = service.get_financial(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["financial_information"] is None
    assert result["data"]["section_complete"] is False


def test_put_financial_creates_and_returns_section_complete(
    service: FinancialInformationService, application_id: str, user_id: str
) -> None:
    result = service.put_financial(application_id, user_id, VALID_PAYLOAD)
    assert result["success"] is True
    assert result["data"]["section_complete"] is True
    assert result["data"]["errors"] is None
    fi = result["data"]["financial_information"]
    assert fi["total_project_cost"] == 100_000.0
    assert fi["grant_amount_requested"] == 75_000.0
    assert fi["cost_match_percentage"] == 25.0
    assert len(fi["matching_funds"]) == 2
    assert len(fi["line_item_budget"]) == 3


def test_get_financial_after_put(
    service: FinancialInformationService, application_id: str, user_id: str
) -> None:
    service.put_financial(application_id, user_id, VALID_PAYLOAD)
    result = service.get_financial(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["financial_information"] is not None
    assert result["data"]["section_complete"] is True
    assert result["data"]["financial_information"]["cost_match_percentage"] == 25.0


def test_validate_grant_exceeds_total() -> None:
    payload = {
        **VALID_PAYLOAD,
        "total_project_cost": 50_000.0,
        "grant_amount_requested": 60_000.0,
        "matching_funds": [],
        "line_item_budget": [{"category": "labor", "description": "X", "amount": 50_000.0}],
    }
    errors = _validate_financial_payload(payload)
    assert "grant_amount_requested" in errors


def test_validate_matching_sum_must_equal_total_minus_grant() -> None:
    payload = {
        **VALID_PAYLOAD,
        "matching_funds": [{"source_name": "A", "amount": 10_000.0, "type": "cash"}],
        # total 100k, grant 75k -> need 25k matching; we sent 10k
    }
    errors = _validate_financial_payload(payload)
    assert "matching_funds" in errors
    assert "25,000" in errors["matching_funds"] or "25000" in errors["matching_funds"]


def test_validate_min_cost_match_percentage() -> None:
    # total 100k, grant 95k -> matching 5k -> 5% < 20%
    payload = {
        "total_project_cost": 100_000.0,
        "grant_amount_requested": 95_000.0,
        "matching_funds": [{"source_name": "Small match", "amount": 5_000.0, "type": "cash"}],
        "line_item_budget": [{"category": "labor", "description": "X", "amount": 100_000.0}],
    }
    errors = _validate_financial_payload(payload)
    assert "matching_funds" in errors
    assert "20" in errors["matching_funds"]


def test_validate_line_items_sum_to_total() -> None:
    payload = {
        **VALID_PAYLOAD,
        "line_item_budget": [
            {"category": "labor", "description": "X", "amount": 30_000.0},
            {"category": "materials", "description": "Y", "amount": 20_000.0},
        ],
        # sum 50k != total 100k
    }
    errors = _validate_financial_payload(payload)
    assert "line_item_budget" in errors


def test_validate_line_item_category_invalid() -> None:
    payload = {
        **VALID_PAYLOAD,
        "line_item_budget": [
            {"category": "invalid_category", "description": "X", "amount": 100_000.0},
        ],
    }
    errors = _validate_financial_payload(payload)
    assert any("category" in k for k in errors)


def test_validate_matching_funds_type() -> None:
    _, errors = _validate_matching_funds([
        {"source_name": "A", "amount": 100.0, "type": "invalid"},
    ])
    assert any("type" in k for k in errors)


def test_put_financial_application_not_found(service: FinancialInformationService, user_id: str) -> None:
    result = service.put_financial(str(uuid.uuid4()), user_id, VALID_PAYLOAD)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_put_financial_wrong_user(
    service: FinancialInformationService, application_id: str, user_id: str
) -> None:
    other = User.create(email="other@example.com", password_hash="x", account_status="active")
    result = service.put_financial(application_id, str(other.id), VALID_PAYLOAD)
    assert result["success"] is False
    assert result["data"]["code"] == "not_found"


def test_is_financial_section_complete_none() -> None:
    assert is_financial_section_complete(None) is False


def test_put_financial_updates_existing(
    service: FinancialInformationService, application_id: str, user_id: str
) -> None:
    service.put_financial(application_id, user_id, VALID_PAYLOAD)
    updated = {
        **VALID_PAYLOAD,
        "total_project_cost": 120_000.0,
        "grant_amount_requested": 90_000.0,
        "matching_funds": [
            {"source_name": "Match A", "amount": 20_000.0, "type": "cash"},
            {"source_name": "Match B", "amount": 10_000.0, "type": "in_kind"},
        ],
        "line_item_budget": [
            {"category": "labor", "description": "Staff", "amount": 50_000.0},
            {"category": "materials", "description": "Supplies", "amount": 45_000.0},
            {"category": "equipment", "description": "Tools", "amount": 25_000.0},
        ],
    }
    result = service.put_financial(application_id, user_id, updated)
    assert result["success"] is True
    assert result["data"]["financial_information"]["total_project_cost"] == 120_000.0
    assert result["data"]["financial_information"]["grant_amount_requested"] == 90_000.0
    assert result["data"]["financial_information"]["cost_match_percentage"] == 25.0  # 30/120


def test_put_financial_with_validation_errors_still_saves(
    service: FinancialInformationService, application_id: str, user_id: str
) -> None:
    bad_payload = {
        **VALID_PAYLOAD,
        "matching_funds": [{"source_name": "Only", "amount": 5_000.0, "type": "cash"}],
    }
    result = service.put_financial(application_id, user_id, bad_payload)
    assert result["success"] is True
    assert result["data"]["section_complete"] is False
    assert result["data"]["errors"] is not None
    assert "matching_funds" in result["data"]["errors"]
    # Data was still persisted
    get_result = service.get_financial(application_id, user_id)
    assert get_result["data"]["financial_information"] is not None
    assert get_result["data"]["financial_information"]["total_project_cost"] == 100_000.0


def test_validate_line_items_allowed_categories() -> None:
    allowed = {"labor", "materials"}
    list_ok, err_ok = _validate_line_items(
        [{"category": "labor", "description": "D", "amount": 100.0}],
        allowed,
    )
    assert len(list_ok) == 1 and not err_ok
    list_bad, err_bad = _validate_line_items(
        [{"category": "equipment", "description": "D", "amount": 100.0}],
        allowed,
    )
    assert len(err_bad) > 0
    assert any("category" in k for k in err_bad)
