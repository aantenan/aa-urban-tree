"""Public data query: natural language to safe predefined queries (read-only aggregates)."""
import re
from typing import Any

from database.models import Application, County
from utils.responses import error_response, success_response


# Predefined query types: NL keywords -> (description, handler)
QUERY_HANDLERS: list[tuple[list[str], str, callable]] = []


def _register(*keywords: str, description: str):
    def decorator(fn):
        QUERY_HANDLERS.append((list(keywords), description, fn))
        return fn
    return decorator


@_register("application", "count", "how many", "total", description="Total application count")
def _query_total_applications() -> list[dict[str, Any]]:
    total = Application.select().count()
    return [{"total_applications": total}]


@_register("by county", "county", "per county", "each county", description="Applications per county")
def _query_by_county() -> list[dict[str, Any]]:
    from database.models import ContactInformation
    from peewee import fn
    rows = (
        ContactInformation.select(ContactInformation.county, fn.COUNT(ContactInformation.id).alias("count"))
        .group_by(ContactInformation.county)
    )
    return [{"county": r.county or "(blank)", "count": r.count} for r in rows]


@_register("by status", "status", "draft", "submitted", description="Applications by status")
def _query_by_status() -> list[dict[str, Any]]:
    from peewee import fn
    rows = (
        Application.select(Application.status, fn.COUNT(Application.id).alias("count"))
        .group_by(Application.status)
    )
    return [{"status": r.status, "count": r.count} for r in rows]


@_register("counties", "list county", "all counties", description="List of counties")
def _query_list_counties() -> list[dict[str, Any]]:
    rows = County.select(County.name, County.state_code).order_by(County.state_code, County.name)
    return [{"name": r.name, "state_code": r.state_code} for r in rows]


def _normalize(q: str) -> str:
    return " ".join(re.split(r"\s+", q.lower().strip()))


class PublicDataQueryService:
    """Map natural language to safe read-only queries and return JSON results."""

    def __init__(self) -> None:
        pass

    def list_suggestions(self) -> dict[str, Any]:
        """Return example questions and available query descriptions."""
        examples = [
            "How many applications are there?",
            "Applications by status",
            "List all counties",
            "Applications per county",
        ]
        return success_response(
            data={
                "suggestions": examples,
                "description": "Ask about application counts, status, and counties (public data only).",
            }
        )

    def query(self, natural_language: str) -> dict[str, Any]:
        """Run a safe query based on natural language input. Returns rows as list of dicts."""
        q = _normalize(natural_language or "")
        if not q:
            return error_response("Please enter a question.", data={"code": "empty"})
        for keywords, _desc, handler in QUERY_HANDLERS:
            if any(kw in q for kw in keywords):
                try:
                    rows = handler()
                    return success_response(data={"rows": rows, "query": natural_language})
                except Exception as e:
                    return error_response(f"Query failed: {e}", data={"code": "query_error"})
        return error_response(
            "No matching public dataset. Try: 'How many applications?', 'Applications by status', or 'List counties'.",
            data={"code": "no_match", "suggestions": ["How many applications are there?", "Applications by status", "List all counties"]},
        )
