# Backend Service Framework (WO-20)

This document describes the service framework: dependency injection, responses, error handling, file upload validation, and how to create new services. For detailed API reference, see [SERVICES.md](SERVICES.md).

## Acceptance Criteria Summary

- **Service patterns**: Constructor dependency injection for testability; thin route handlers calling service methods.
- **Email**: Protocol + Console (dev) and SMTP (production); switch via `SMTP_HOST`.
- **File storage**: Interface with local and S3 (see `storage` lib); resolved via `get_storage()`.
- **DI container**: `core.container` — `init_container()` at startup; `get_email_service()`, `get_storage()`, `get_malware_scanner()`.
- **API responses**: `success`, `message`, `data` — use `utils.responses.success_response` / `error_response`.
- **Error handling**: Global handler (500), validation handler (422) with formatted errors.
- **File upload**: PDF, JPG, PNG, 10MB — `core.upload.validate_upload`; malware scan via `get_malware_scanner()` (NoOp in dev).
- **Confirmation numbers**: `UTP-YYYY-NNNN` via `utils.confirmation_number.generate_confirmation_number`.
- **Testing**: Mock factories in `utils.testing` (MockEmailService, MockStorageBackend, MockMalwareScanner).
- **Documentation**: This file and [SERVICES.md](SERVICES.md); example service below.

## Example Service

See `services/example_service.py` and `tests/test_example_service.py` for a minimal service that:

1. Accepts dependencies via constructor (`email_service`).
2. Returns `success_response` / `error_response` from `utils.responses`.
3. Is tested by passing `MockEmailService()` from `utils.testing`.

```python
# services/example_service.py (simplified)
from utils.responses import error_response, success_response

class ExampleService:
    def __init__(self, email_service=None):
        self.email_service = email_service

    def do_something(self, user_id: str, message: str):
        if not (user_id or "").strip():
            return error_response("user_id is required", data={"code": "validation_error"})
        if self.email_service:
            self.email_service.send(to="admin@example.com", subject="...", body_text=f"...")
        return success_response(data={"user_id": user_id, "message": message}, message="Done")
```

```python
# tests/test_example_service.py
from utils.testing import mock_email_service
from services.example_service import ExampleService

def test_example_sends_email_when_provided():
    mock_email = mock_email_service()
    svc = ExampleService(email_service=mock_email)
    result = svc.do_something("user-1", "hello")
    assert result["success"] is True
    assert len(mock_email.sent) == 1
```

## Service Registry

For advanced registration and discovery, use `utils.service_registry`:

- `register(name, factory)` — register a callable that returns the service.
- `get(name)` — resolve by name (raises `KeyError` if not registered).
- `clear()` — clear all (e.g. in test teardown).

## Configuration

- **Email**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` for production.
- **Storage**: `STORAGE_PROVIDER` / `STORAGE_BACKEND` (local | s3), `LOCAL_STORAGE_PATH`, S3 vars.
- **Malware**: `MALWARE_SCAN_DISABLED` (true in dev), `DEBUG` — when set, NoOpScanner is used.

Container initialization is called in `main.py` lifespan; failures are logged and defaults (e.g. console email, NoOp scanner) are used where possible.
