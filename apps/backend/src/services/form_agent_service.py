"""Form-filling agent: guidance and text extraction for pre-filling forms."""
import re
from typing import Any

from utils.responses import error_response, success_response


# Section definitions: required fields and suggested order for guidance
SECTION_GUIDANCE = {
    "contact_information": {
        "title": "Contact Information",
        "fields_in_order": [
            "organization_name",
            "address_line1",
            "address_line2",
            "city",
            "state_code",
            "zip_code",
            "county",
            "primary_contact_name",
            "primary_contact_title",
            "primary_contact_email",
            "primary_contact_phone",
        ],
        "required": ["organization_name", "address_line1", "city", "state_code", "primary_contact_email", "primary_contact_phone"],
        "tips": {
            "organization_name": "Enter the legal or common name of your organization.",
            "county": "Select the county where the project is located.",
            "primary_contact_email": "We'll use this for application updates and correspondence.",
        },
    },
    "project_information": {
        "title": "Project Information",
        "fields_in_order": ["project_name", "site_address_line1", "site_city", "site_state_code", "site_zip_code", "site_ownership", "project_type", "acreage", "tree_count", "start_date", "completion_date", "description"],
        "required": ["project_name", "site_address_line1", "site_city", "site_state_code", "site_zip_code", "project_type"],
        "tips": {},
    },
}


def _extract_email(text: str) -> str | None:
    m = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text, re.IGNORECASE)
    return m.group(0) if m else None


def _extract_phone(text: str) -> str | None:
    m = re.search(r"(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}", text)
    return m.group(0).strip() if m else None


def _extract_label_value(text: str, labels: list[tuple[str, list[str]]]) -> dict[str, str]:
    """Extract key-value pairs where key is one of the labels (e.g. 'county', 'County:')."""
    out = {}
    for key, aliases in labels:
        for alias in aliases:
            # Match "Label: value" or "Label value" (value until newline or next Label)
            pat = re.compile(rf"{re.escape(alias)}\s*[:\-]?\s*(.+?)(?=\n[A-Za-z]|\n\n|$)", re.IGNORECASE | re.DOTALL)
            m = pat.search(text)
            if m:
                val = m.group(1).strip().strip(".,;")
                if val and len(val) < 500:
                    out[key] = val
                break
    return out


class FormAgentService:
    """Provide form guidance and extract structured data from pasted text for pre-filling."""

    def __init__(self) -> None:
        pass

    def get_guidance(self, section: str, current_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return suggested next field, required list, and tips for a form section."""
        section = (section or "").strip().lower().replace("-", "_")
        if section not in SECTION_GUIDANCE:
            return error_response("Unknown section", data={"code": "unknown_section", "available": list(SECTION_GUIDANCE.keys())})
        g = SECTION_GUIDANCE[section]
        current_data = current_data or {}
        next_field = None
        for f in g["fields_in_order"]:
            val = current_data.get(f)
            if val is None or (isinstance(val, str) and not val.strip()):
                next_field = f
                break
        tip = g["tips"].get(next_field) if next_field else None
        return success_response(
            data={
                "section": section,
                "title": g["title"],
                "required_fields": g["required"],
                "suggested_next_field": next_field,
                "tip": tip,
                "all_fields": g["fields_in_order"],
            }
        )

    def extract_from_text(self, section: str, text: str) -> dict[str, Any]:
        """Parse pasted text and return key-value pairs for form pre-fill."""
        section = (section or "").strip().lower().replace("-", "_")
        if section not in SECTION_GUIDANCE:
            return error_response("Unknown section", data={"code": "unknown_section"})
        if not (text or text.strip()):
            return error_response("No text provided", data={"code": "empty"})
        text = text.strip()
        extracted = {}

        if section == "contact_information":
            email = _extract_email(text)
            if email:
                extracted["primary_contact_email"] = email
            phone = _extract_phone(text)
            if phone:
                extracted["primary_contact_phone"] = phone
            labels = [
                ("organization_name", ["organization", "org", "company", "name"]),
                ("address_line1", ["address", "street", "address line 1"]),
                ("address_line2", ["address line 2", "suite", "unit"]),
                ("city", ["city"]),
                ("state_code", ["state", "st"]),
                ("zip_code", ["zip", "postal", "zip code"]),
                ("county", ["county"]),
                ("primary_contact_name", ["contact", "name", "primary contact"]),
                ("primary_contact_title", ["title"]),
            ]
            extracted.update(_extract_label_value(text, labels))

        if section == "project_information":
            labels = [
                ("project_name", ["project name", "project"]),
                ("site_address_line1", ["site address", "address", "location"]),
                ("site_city", ["city"]),
                ("site_state_code", ["state"]),
                ("site_zip_code", ["zip"]),
                ("description", ["description", "summary"]),
            ]
            extracted.update(_extract_label_value(text, labels))

        return success_response(data={"extracted": extracted, "section": section})
