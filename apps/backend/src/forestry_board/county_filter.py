"""County-based data filtering utilities for board member access restrictions."""

from database.models import Application, ContactInformation


def get_application_county(application: Application) -> str | None:
    """Extract county from application's contact information."""
    try:
        ci = ContactInformation.get(ContactInformation.application == application)
        return ci.county
    except ContactInformation.DoesNotExist:
        return None


def filter_applications_by_county(
    applications: list[Application],
    board_county: str | None,
) -> list[Application]:
    """
    Filter applications to only those from the board member's county.
    Returns empty list if board_county is None.
    """
    if not board_county:
        return []
    board_county_norm = board_county.strip().lower()
    result: list[Application] = []
    for app in applications:
        county = get_application_county(app)
        if county and county.strip().lower() == board_county_norm:
            result.append(app)
    return result
