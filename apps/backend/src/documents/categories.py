"""Document category definitions and validation for document management."""
from database.models.document import (
    DOCUMENT_CATEGORIES,
    DOCUMENT_CATEGORY_SITE_PHOTOS,
    DOCUMENT_CATEGORY_SITE_PLAN,
    DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS,
)

# Display names for UI/API responses
CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    DOCUMENT_CATEGORY_SITE_PLAN: "Site Plan",
    DOCUMENT_CATEGORY_SITE_PHOTOS: "Site Photos",
    DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS: "Supporting Documents",
}

# API/request format (camelCase) to DB format (snake_case)
CATEGORY_ALIASES: dict[str, str] = {
    "site_plan": DOCUMENT_CATEGORY_SITE_PLAN,
    "site_photos": DOCUMENT_CATEGORY_SITE_PHOTOS,
    "supporting_documents": DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS,
    "siteplan": DOCUMENT_CATEGORY_SITE_PLAN,
    "sitephotos": DOCUMENT_CATEGORY_SITE_PHOTOS,
    "supportingdocuments": DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS,
}

__all__ = [
    "DOCUMENT_CATEGORIES",
    "DOCUMENT_CATEGORY_SITE_PLAN",
    "DOCUMENT_CATEGORY_SITE_PHOTOS",
    "DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS",
    "CATEGORY_DISPLAY_NAMES",
    "normalize_category",
    "is_valid_category",
    "validate_category",
]


def normalize_category(category: str) -> str | None:
    """Normalize category string to DB format (snake_case). Returns None if invalid."""
    raw = (category or "").strip().lower().replace(" ", "_").replace("-", "_")
    return CATEGORY_ALIASES.get(raw) or (raw if raw in DOCUMENT_CATEGORIES else None)


def is_valid_category(category: str) -> bool:
    """Return True if category is a valid document category."""
    return normalize_category(category) is not None


def validate_category(category: str) -> tuple[bool, str]:
    """
    Validate document category. Returns (ok, error_message).
    error_message is empty when ok is True.
    """
    if not (category or "").strip():
        return False, "Document category is required."
    if not is_valid_category(category):
        return (
            False,
            "Invalid category. Allowed: Site Plan, Site Photos, Supporting Documents.",
        )
    return True, ""
