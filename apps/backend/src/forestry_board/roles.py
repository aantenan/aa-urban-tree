"""Board member role and permission definitions for county-based access control."""

from enum import Enum


class BoardMemberRole(str, Enum):
    """
    Board member role for county-based access control.
    Users with a ForestryBoard record for a county have this role for that jurisdiction.
    """

    FORESTRY_BOARD_MEMBER = "forestry_board_member"

    @classmethod
    def has_county_access(cls, role: "BoardMemberRole", user_county: str | None, app_county: str | None) -> bool:
        """Check if role grants access to applications from app_county."""
        if not user_county or not app_county:
            return False
        if role != cls.FORESTRY_BOARD_MEMBER:
            return False
        return _counties_match(user_county, app_county)


def _counties_match(a: str, b: str) -> bool:
    """Compare county strings case-insensitively; normalize whitespace."""
    return (a or "").strip().lower() == (b or "").strip().lower()
