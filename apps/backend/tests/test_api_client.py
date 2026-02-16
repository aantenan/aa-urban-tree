"""Smoke tests for API client fixture: auth override and protected endpoints."""
import pytest


def test_health_public_no_auth(api_client_no_auth) -> None:
    """Public health endpoint works without auth."""
    client = api_client_no_auth
    r = client.get("/api/health")
    assert r.status_code == 200


def test_applications_list_requires_auth(api_client_no_auth) -> None:
    """Listing applications without auth returns 401."""
    r = api_client_no_auth.get("/api/v1/applications")
    assert r.status_code == 401


def test_applications_list_with_auth(api_client) -> None:
    """With auth override, listing applications returns 200 and array."""
    r = api_client.get("/api/v1/applications")
    assert r.status_code == 200
    data = r.json()
    assert "data" in data or isinstance(data, list)
    apps = data.get("data", data) if isinstance(data, dict) else data
    assert isinstance(apps, list)
