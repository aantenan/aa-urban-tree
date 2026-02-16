"""Financial information section: validation, calculations, get/put, section completion."""
import json
from typing import Any
from uuid import UUID

from database.models import Application, BudgetCategory, FinancialInformation, User
from utils.responses import error_response, success_response

CURRENCY_DECIMALS = 2
MIN_MATCH_PERCENT = 20.0
FLOAT_TOLERANCE = 0.01


def _round_currency(value: float) -> float:
    return round(float(value), CURRENCY_DECIMALS)


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _allowed_budget_categories() -> set[str]:
    return {r.code for r in BudgetCategory.select(BudgetCategory.code)}


def _sum_matching_funds(matching_funds: list[dict]) -> float:
    total = 0.0
    for item in matching_funds:
        amount = _parse_float(item.get("amount"))
        if amount is not None and amount >= 0:
            total += amount
    return _round_currency(total)


def _sum_line_items(line_items: list[dict]) -> float:
    total = 0.0
    for item in line_items:
        amount = _parse_float(item.get("amount"))
        if amount is not None and amount >= 0:
            total += amount
    return _round_currency(total)


def compute_cost_match_percentage(total_cost: float, matching_total: float) -> float | None:
    """Server-side cost-match percentage. Returns None if total_cost <= 0."""
    if total_cost is None or total_cost <= 0:
        return None
    if matching_total is None or matching_total < 0:
        return None
    return _round_currency((matching_total / total_cost) * 100.0)


def _validate_matching_funds(matching_funds: list[Any]) -> tuple[list[dict], dict[str, str]]:
    """Normalize and validate matching funds. Returns (normalized_list, errors)."""
    errors: dict[str, str] = {}
    if not isinstance(matching_funds, list):
        return [], {"matching_funds": "Matching funds must be a list"}
    normalized = []
    for i, item in enumerate(matching_funds):
        if not isinstance(item, dict):
            errors[f"matching_funds[{i}]"] = "Invalid item"
            continue
        source = (item.get("source_name") or "").strip()
        amount = _parse_float(item.get("amount"))
        typ = (item.get("type") or "").strip().lower()
        if not source:
            errors[f"matching_funds[{i}].source_name"] = "Source name is required"
        if amount is None or amount < 0:
            errors[f"matching_funds[{i}].amount"] = "Valid amount is required"
        if typ not in ("cash", "in_kind"):
            errors[f"matching_funds[{i}].type"] = "Type must be cash or in_kind"
        if not errors.get(f"matching_funds[{i}].source_name") and amount is not None and amount >= 0 and typ in ("cash", "in_kind"):
            normalized.append({
                "source_name": source,
                "amount": _round_currency(amount),
                "type": typ,
            })
    return normalized, errors


def _validate_line_items(line_items: list[Any], allowed_categories: set[str]) -> tuple[list[dict], dict[str, str]]:
    """Normalize and validate line item budget. Returns (normalized_list, errors)."""
    errors: dict[str, str] = {}
    if not isinstance(line_items, list):
        return [], {"line_item_budget": "Line item budget must be a list"}
    normalized = []
    for i, item in enumerate(line_items):
        if not isinstance(item, dict):
            errors[f"line_item_budget[{i}]"] = "Invalid item"
            continue
        category = (item.get("category") or "").strip().lower()
        description = (item.get("description") or "").strip()
        amount = _parse_float(item.get("amount"))
        if not category:
            errors[f"line_item_budget[{i}].category"] = "Category is required"
        elif allowed_categories and category not in allowed_categories:
            errors[f"line_item_budget[{i}].category"] = "Select a valid budget category"
        if amount is None or amount < 0:
            errors[f"line_item_budget[{i}].amount"] = "Valid amount is required"
        if not errors.get(f"line_item_budget[{i}].category") and amount is not None and amount >= 0:
            normalized.append({
                "category": category,
                "description": description,
                "amount": _round_currency(amount),
            })
    return normalized, errors


def _validate_financial_payload(data: dict[str, Any]) -> dict[str, str]:
    """Validate financial payload. Returns errors dict. Performs server-side cost-match logic."""
    errors: dict[str, str] = {}

    total_cost = _parse_float(data.get("total_project_cost"))
    if total_cost is None:
        if data.get("total_project_cost") not in (None, ""):
            errors["total_project_cost"] = "Enter a valid amount"
        else:
            errors["total_project_cost"] = "Total project cost is required"
    elif total_cost < 0:
        errors["total_project_cost"] = "Total project cost must be zero or greater"
    else:
        total_cost = _round_currency(total_cost)

    grant = _parse_float(data.get("grant_amount_requested"))
    if grant is None:
        if data.get("grant_amount_requested") not in (None, ""):
            errors["grant_amount_requested"] = "Enter a valid amount"
        else:
            errors["grant_amount_requested"] = "Grant amount is required"
    elif grant < 0:
        errors["grant_amount_requested"] = "Grant amount must be zero or greater"
    else:
        grant = _round_currency(grant)

    matching_list, matching_errors = _validate_matching_funds(data.get("matching_funds") or [])
    errors.update(matching_errors)

    matching_total = _sum_matching_funds(matching_list) if not matching_errors else 0.0

    if total_cost is not None and total_cost >= 0 and grant is not None and grant >= 0:
        if grant > total_cost:
            errors["grant_amount_requested"] = "Grant amount cannot exceed total project cost"
        expected_matching = _round_currency(total_cost - grant)
        if abs(matching_total - expected_matching) > FLOAT_TOLERANCE:
            errors["matching_funds"] = (
                f"Matching funds total (${matching_total:,.2f}) must equal total cost minus grant "
                f"(${expected_matching:,.2f})"
            )
        elif total_cost > 0:
            match_pct = compute_cost_match_percentage(total_cost, matching_total)
            if match_pct is not None and match_pct < MIN_MATCH_PERCENT:
                errors["matching_funds"] = (
                    f"Cost-match percentage ({match_pct:.1f}%) must be at least {MIN_MATCH_PERCENT}%"
                )

    allowed_cats = _allowed_budget_categories()
    line_list, line_errors = _validate_line_items(data.get("line_item_budget") or [], allowed_cats)
    errors.update(line_errors)

    line_total = _sum_line_items(line_list) if not line_errors else 0.0
    if total_cost is not None and total_cost >= 0 and not line_errors and line_list:
        if abs(line_total - total_cost) > FLOAT_TOLERANCE:
            errors["line_item_budget"] = (
                f"Line items must sum to total project cost (${total_cost:,.2f}); current sum ${line_total:,.2f}"
            )

    return errors


def _financial_to_dict(f: FinancialInformation) -> dict[str, Any]:
    data = {
        "total_project_cost": round(f.total_project_cost, CURRENCY_DECIMALS) if f.total_project_cost is not None else None,
        "grant_amount_requested": round(f.grant_amount_requested, CURRENCY_DECIMALS) if f.grant_amount_requested is not None else None,
        "matching_funds": [],
        "line_item_budget": [],
    }
    if f.matching_funds:
        try:
            data["matching_funds"] = json.loads(f.matching_funds)
        except (TypeError, ValueError):
            pass
    if f.line_item_budget:
        try:
            data["line_item_budget"] = json.loads(f.line_item_budget)
        except (TypeError, ValueError):
            pass
    matching_total = _sum_matching_funds(data["matching_funds"])
    if f.total_project_cost and f.total_project_cost > 0:
        data["cost_match_percentage"] = compute_cost_match_percentage(f.total_project_cost, matching_total)
    else:
        data["cost_match_percentage"] = None
    return data


def is_financial_section_complete(f: FinancialInformation | None) -> bool:
    """Return True if financial section has valid data and passes all checks."""
    if not f:
        return False
    data = _financial_to_dict(f)
    data["total_project_cost"] = f.total_project_cost
    data["grant_amount_requested"] = f.grant_amount_requested
    errors = _validate_financial_payload(data)
    return len(errors) == 0


class FinancialInformationService:
    """Get and update financial information; server-side calculations and validation."""

    def __init__(self) -> None:
        pass

    def get_financial(self, application_id: str, user_id: str) -> dict[str, Any]:
        """Get financial information for application if it belongs to user."""
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        if app.status != "draft":
            return error_response("Application is not a draft", data={"code": "not_draft"})
        try:
            fin = FinancialInformation.get(FinancialInformation.application_id == app.id)
        except FinancialInformation.DoesNotExist:
            return success_response(
                data={"financial_information": None, "section_complete": False},
                message="No financial information yet",
            )
        payload = _financial_to_dict(fin)
        return success_response(
            data={
                "financial_information": payload,
                "section_complete": is_financial_section_complete(fin),
            },
        )

    def put_financial(
        self, application_id: str, user_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Update financial information (auto-save). Validates and computes cost-match server-side."""
        try:
            aid = UUID(application_id)
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid id", data={"code": "invalid_id"})
        try:
            app = Application.get((Application.id == aid) & (Application.user_id == uid))
        except Application.DoesNotExist:
            return error_response("Application not found", data={"code": "not_found"})
        if app.status != "draft":
            return error_response("Only draft applications can be updated", data={"code": "not_draft"})

        total_cost = _parse_float(payload.get("total_project_cost"))
        total_cost = _round_currency(total_cost) if total_cost is not None and total_cost >= 0 else None
        grant = _parse_float(payload.get("grant_amount_requested"))
        grant = _round_currency(grant) if grant is not None and grant >= 0 else None
        matching_list, _ = _validate_matching_funds(payload.get("matching_funds") or [])
        line_list, _ = _validate_line_items(
            payload.get("line_item_budget") or [], _allowed_budget_categories()
        )
        errors = _validate_financial_payload({
            **payload,
            "total_project_cost": total_cost,
            "grant_amount_requested": grant,
            "matching_funds": [{"source_name": m["source_name"], "amount": m["amount"], "type": m["type"]} for m in matching_list],
            "line_item_budget": [{"category": l["category"], "description": l["description"], "amount": l["amount"]} for l in line_list],
        })

        fin, created = FinancialInformation.get_or_create(
            application_id=app.id,
            defaults={
                "total_project_cost": total_cost,
                "grant_amount_requested": grant,
                "matching_funds": json.dumps(matching_list) if matching_list else None,
                "line_item_budget": json.dumps(line_list) if line_list else None,
            },
        )
        if not created:
            fin.total_project_cost = total_cost
            fin.grant_amount_requested = grant
            fin.matching_funds = json.dumps(matching_list) if matching_list else None
            fin.line_item_budget = json.dumps(line_list) if line_list else None
            fin.save()

        out_data = _financial_to_dict(fin)
        return success_response(
            data={
                "financial_information": out_data,
                "section_complete": len(errors) == 0,
                "errors": errors if errors else None,
            },
            message="Financial information saved",
        )
