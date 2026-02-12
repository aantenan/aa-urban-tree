"""Contact information section: validation, get/put, section completion."""
import re
from typing import Any
from uuid import UUID

from database.models import Application, ContactInformation, User
from utils.responses import error_response, success_response

# Email: basic format
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
# Phone: digits, spaces, dashes, parens; at least 10 digits
PHONE_RE = re.compile(r"^[\d\s\-\(\)\+\.]+$")
MIN_PHONE_DIGITS = 10


def _validate_email(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    if not EMAIL_RE.match(value.strip()):
        return "Enter a valid email address"
    return None


def _validate_phone(value: str | None) -> str | None:
    if not value or not value.strip():
        return None
    s = value.strip()
    if not PHONE_RE.match(s):
        return "Enter a valid phone number"
    digits = sum(1 for c in s if c.isdigit())
    if digits < MIN_PHONE_DIGITS:
        return "Phone number must have at least 10 digits"
    return None


def _validate_contact_payload(data: dict[str, Any]) -> dict[str, str]:
    """Validate contact payload. Returns dict of field -> error message (empty if valid)."""
    errors: dict[str, str] = {}
    # Required for section completion (and for PUT we require at least primary contact)
    org = (data.get("organization_name") or "").strip()
    if not org:
        errors["organization_name"] = "Organization name is required"
    addr1 = (data.get("address_line1") or "").strip()
    if not addr1:
        errors["address_line1"] = "Address line 1 is required"
    city = (data.get("city") or "").strip()
    if not city:
        errors["city"] = "City is required"
    state = (data.get("state_code") or "").strip()
    if not state:
        errors["state_code"] = "State is required"
    zip_code = (data.get("zip_code") or "").strip()
    if not zip_code:
        errors["zip_code"] = "ZIP code is required"
    county = (data.get("county") or "").strip()
    if not county:
        errors["county"] = "County is required"
    primary_name = (data.get("primary_contact_name") or "").strip()
    if not primary_name:
        errors["primary_contact_name"] = "Primary contact name is required"
    primary_email = (data.get("primary_contact_email") or "").strip()
    if not primary_email:
        errors["primary_contact_email"] = "Primary contact email is required"
    else:
        err = _validate_email(primary_email)
        if err:
            errors["primary_contact_email"] = err
    primary_phone = (data.get("primary_contact_phone") or "").strip()
    if primary_phone:
        err = _validate_phone(primary_phone)
        if err:
            errors["primary_contact_phone"] = err
    # Alternate contact optional but if provided, validate
    alt_email = (data.get("alternate_contact_email") or "").strip()
    if alt_email:
        err = _validate_email(alt_email)
        if err:
            errors["alternate_contact_email"] = err
    alt_phone = (data.get("alternate_contact_phone") or "").strip()
    if alt_phone:
        err = _validate_phone(alt_phone)
        if err:
            errors["alternate_contact_phone"] = err
    return errors


def _contact_to_dict(c: ContactInformation) -> dict[str, Any]:
    return {
        "organization_name": c.organization_name,
        "address_line1": c.address_line1,
        "address_line2": c.address_line2,
        "city": c.city,
        "state_code": c.state_code,
        "zip_code": c.zip_code,
        "county": c.county,
        "primary_contact_name": c.primary_contact_name,
        "primary_contact_title": c.primary_contact_title,
        "primary_contact_email": c.primary_contact_email,
        "primary_contact_phone": c.primary_contact_phone,
        "alternate_contact_name": c.alternate_contact_name,
        "alternate_contact_title": c.alternate_contact_title,
        "alternate_contact_email": c.alternate_contact_email,
        "alternate_contact_phone": c.alternate_contact_phone,
    }


def is_contact_section_complete(c: ContactInformation | None) -> bool:
    """Return True if contact section has all required fields and they pass validation."""
    if not c:
        return False
    data = _contact_to_dict(c)
    errors = _validate_contact_payload(data)
    return len(errors) == 0


class ContactInformationService:
    """Get and update contact information; validation and section completion."""

    def __init__(self) -> None:
        pass

    def get_contact(self, application_id: str, user_id: str) -> dict[str, Any]:
        """Get contact information for application if it belongs to user."""
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
            contact = ContactInformation.get(ContactInformation.application_id == app.id)
        except ContactInformation.DoesNotExist:
            return success_response(
                data={"contact_information": None, "section_complete": False},
                message="No contact information yet",
            )
        payload = _contact_to_dict(contact)
        return success_response(
            data={
                "contact_information": payload,
                "section_complete": is_contact_section_complete(contact),
            },
        )

    def put_contact(
        self, application_id: str, user_id: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        """Update contact information (auto-save). Saves payload and returns validation errors + section_complete."""
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
        errors = _validate_contact_payload(payload)
        def _v(k: str) -> str | None:
            val = (payload.get(k) or "").strip()
            return val or None

        contact, created = ContactInformation.get_or_create(
            application_id=app.id,
            defaults={
                "organization_name": _v("organization_name"),
                "address_line1": _v("address_line1"),
                "address_line2": _v("address_line2"),
                "city": _v("city"),
                "state_code": _v("state_code"),
                "zip_code": _v("zip_code"),
                "county": _v("county"),
                "primary_contact_name": _v("primary_contact_name"),
                "primary_contact_title": _v("primary_contact_title"),
                "primary_contact_email": _v("primary_contact_email"),
                "primary_contact_phone": _v("primary_contact_phone"),
                "alternate_contact_name": _v("alternate_contact_name"),
                "alternate_contact_title": _v("alternate_contact_title"),
                "alternate_contact_email": _v("alternate_contact_email"),
                "alternate_contact_phone": _v("alternate_contact_phone"),
            },
        )
        if not created:
            contact.organization_name = _v("organization_name")
            contact.address_line1 = _v("address_line1")
            contact.address_line2 = _v("address_line2")
            contact.city = _v("city")
            contact.state_code = _v("state_code")
            contact.zip_code = _v("zip_code")
            contact.county = _v("county")
            contact.primary_contact_name = _v("primary_contact_name")
            contact.primary_contact_title = _v("primary_contact_title")
            contact.primary_contact_email = _v("primary_contact_email")
            contact.primary_contact_phone = _v("primary_contact_phone")
            contact.alternate_contact_name = _v("alternate_contact_name")
            contact.alternate_contact_title = _v("alternate_contact_title")
            contact.alternate_contact_email = _v("alternate_contact_email")
            contact.alternate_contact_phone = _v("alternate_contact_phone")
            contact.save()
        return success_response(
            data={
                "contact_information": _contact_to_dict(contact),
                "section_complete": len(errors) == 0,
                "errors": errors if errors else None,
            },
            message="Contact information saved",
        )
