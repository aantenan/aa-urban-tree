"""Tests for PublicListingService and program config API."""
import pytest

from services.public_listing_service import PublicListingService


def test_get_program_config_api_response() -> None:
    """API response includes program, grantCycle, eligibility, resources."""
    svc = PublicListingService()
    data = svc.get_program_config_api_response()
    assert "program" in data
    assert "grantCycle" in data
    assert "eligibility" in data
    assert "resources" in data
    assert data["program"]["name"]
    assert "applicationDeadline" in data["grantCycle"] or data["grantCycle"] == {}
    assert "applicantTypes" in data["eligibility"] or data["eligibility"] == {}
    assert isinstance(data["resources"], list)


def test_program_config_caching() -> None:
    """Repeated calls return same config (cached)."""
    svc = PublicListingService()
    c1, e1 = svc.get_program_config()
    c2, e2 = svc.get_program_config()
    assert c1.title == c2.title
    assert e1 == e2
