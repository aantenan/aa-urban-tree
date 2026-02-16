# Backend Testing Guide

This document describes the backend unit testing infrastructure, mocking patterns, and how to run tests.

## Running Tests

```bash
# From apps/backend (with dev deps installed)
uv run pytest

# With coverage
uv run pytest --cov=src --cov-report=term-missing

# Single file or test
uv run pytest tests/test_contact_information_service.py -v
uv run pytest tests/test_contact_information_service.py::test_get_contact_empty -v
```

## Configuration

- **pytest**: Configured in `pyproject.toml` under `[tool.pytest.ini_options]`. Test discovery uses `tests/` and `test_*.py` / `test_*` names.
- **Coverage**: `[tool.coverage.run]` sources `src/`; report options in `[tool.coverage.report]`. Run with `pytest --cov=src`.

## Test Database

Tests use **in-memory SQLite** (`sqlite:///:memory:`) so no external DB is required.

- **Per-test DB**: Many tests use an `autouse` fixture that sets `DATABASE_URL` and creates only the tables that test needs (e.g. `User`, `Application`, `ContactInformation`, `County`).
- **Shared full schema**: The `memory_db` fixture in `tests/conftest.py` creates **all** app tables. Use it when you need the full schema without listing models.
- **TESTING=1**: When set, the app’s lifespan skips migrations and seeds so API tests share the same in-memory DB as the test process.

## Fixtures (conftest.py)

| Fixture | Purpose |
|--------|---------|
| `all_models` | List of all Peewee models for `create_tables`. |
| `memory_db` | In-memory DB with all tables; resets proxy on teardown. |
| `make_user` | Factory fixture: `make_user(email=...)` creates a `User`. |
| `make_application` | Factory fixture: `make_application(user=...)` creates an `Application`. |
| `auth_user_payload` | Creates a user and returns `(user_id, payload_dict)` for auth override. |
| `api_client` | FastAPI `TestClient` with `get_current_user` overridden to `auth_user_payload`. |
| `api_client_no_auth` | `TestClient` with no auth (for public endpoints or 401 checks). |

## Test Data Factories

- **Fixture factories**: Use `make_user` and `make_application` in tests that need DB records.
- **Standalone**: `tests/factories.py` provides `create_user()` and `create_application()`. Caller must ensure DB and tables exist (e.g. use `memory_db` in the same test).

```python
# In a test that uses memory_db
from tests.factories import create_user, create_application
user = create_user(email="test@example.com")
app = create_application(user=user, status="draft")
```

## Service Tests (no HTTP)

Test service classes in isolation with an in-memory DB and optional mocks:

1. Use `autouse` fixture to set `DATABASE_URL` and create only the tables you need.
2. Create test data (User, Application, etc.) and call the service directly.
3. Assert on return values and DB state.

Example (see `tests/test_contact_information_service.py`):

```python
@pytest.fixture(autouse=True)
def use_memory_db(monkeypatch, ...):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    # ... init db, create_tables([User, Application, ContactInformation, County])
    yield
    # ... teardown

def test_get_contact_empty(service, application_id, user_id):
    result = service.get_contact(application_id, user_id)
    assert result["success"] is True
    assert result["data"]["contact_information"] is None
```

## API / Route Tests (HTTP client)

Use `api_client` or `api_client_no_auth` to hit real routes with mocked auth:

- **Authenticated**: `api_client` overrides `get_current_user` so the request is treated as the user from `auth_user_payload`. Use for GET/PUT/POST to protected routes.
- **Unauthenticated**: `api_client_no_auth` for public endpoints or to assert 401.

Example (see `tests/test_api_client.py`):

```python
def test_applications_list_with_auth(api_client):
    r = api_client.get("/api/v1/applications")
    assert r.status_code == 200
```

## Mocking Dependencies

### Email

Use `utils.testing.MockEmailService`. Inspect `.sent` to assert emails:

```python
from utils.testing import MockEmailService
mock_email = MockEmailService()
# Inject into service or patch get_email_service
# ... trigger action that sends email ...
assert len(mock_email.sent) == 1
assert mock_email.sent[0]["to"] == "user@example.com"
```

### Storage / file upload

Use `utils.testing.MockStorageBackend`. Files are stored in memory by key; use `.upload()`, `.download()`, `.get_metadata()`, `.delete()`.

### Malware scanner

Use `utils.testing.MockMalwareScanner(safe=True)` or `(safe=False)`. Inspect `.scanned` for scan calls.

### Authentication (routes)

Use the `api_client` fixture; it overrides `get_current_user` so no real JWT is required. For custom user, create the user (e.g. with `make_user`) and build a payload `{"sub": str(user.id), "email": user.email}`, then override the dependency with a callable returning that payload.

## Performance / load testing

Use `tests/performance.run_load_test()` to run a callable N times and get latency stats:

```python
from tests.performance import run_load_test, print_load_report

def test_health_latency(api_client_no_auth):
    stats = run_load_test(lambda: api_client_no_auth.get("/api/health"), n=100)
    print_load_report(stats, "GET /api/health")
    assert stats["p95_ms"] < 100  # optional threshold
```

## Standards

- **Isolation**: Each test should not depend on another test’s side effects. Use fixtures to create data.
- **Naming**: `test_<behavior>_<scenario>` (e.g. `test_get_contact_empty`, `test_put_contact_wrong_user`).
- **Service logic**: Prefer testing service methods with a real in-memory DB and mocked external deps (email, storage) rather than only mocking the service.
- **Coverage**: Run `pytest --cov=src --cov-report=term-missing` and add tests for uncovered branches when touching code.
