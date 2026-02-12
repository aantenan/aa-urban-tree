# Backend Service Framework

This document describes the service-based architecture: dependency injection, API responses, error handling, and how to add new services.

## Patterns

- **Thin route handlers**: Routes parse request, call a service method, return a formatted response.
- **Constructor injection**: Services receive dependencies (email, storage, DB) in `__init__` so tests can pass mocks.
- **Pure service methods**: Input parameters and return values; avoid reaching for globals inside methods.

## API Response Format

All JSON responses use a consistent shape:

```json
{
  "success": true,
  "message": "Optional message",
  "data": { ... }
}
```

- **Success**: use `utils.responses.success_response(data=..., message=...)`.
- **Error**: use `utils.responses.error_response(message="...", data=...)`.
- Validation errors return `success: false`, `message: "Validation failed"`, and `data.errors` as a list of `{ loc, msg, type }`.

## Error Handling

- **Validation (422)**: Pydantic validation failures are caught and returned in the standard format via `utils.errors.validation_exception_handler`.
- **Unhandled (500)**: `utils.errors.error_handler` returns a generic message and optional debug `type` in data.

## Dependency Injection

- **Container**: `core.container` holds the email service, storage backend, and malware scanner. Call `init_container()` once at startup (done in `main.py` lifespan).
- **Resolve in routes or services**: `get_email_service()`, `get_storage()`, `get_malware_scanner()`.
- **Configuration**: Email uses SMTP when `SMTP_HOST` is set, otherwise `ConsoleEmailService` (logs only). Storage uses `storage` lib factory (env: `STORAGE_PROVIDER`/`STORAGE_BACKEND`, `LOCAL_STORAGE_PATH`, or S3 vars). Malware scanning uses `NoOpScanner` when `DEBUG` or `MALWARE_SCAN_DISABLED` is set.

## Email

- **Interface**: `core.email.EmailService` (Protocol): `send(to, subject, body_text, body_html=None, **kwargs)`.
- **Implementations**: `ConsoleEmailService` (dev), `SmtpEmailService` (production; env: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`).

## File Storage and Upload

- **Storage**: Use `get_storage()` for the configured backend (local or S3). Interface: `storage.interfaces.base.StorageBackend`.
- **Validation**: `core.upload.validate_upload(filename, content_type, size)` enforces PDF/JPG/PNG and 10MB. Returns `(ok, error_message)`.
- **Malware**: `core.upload.scan_for_malware(file_obj, filename, scanner)` or `validate_and_scan(...)` with `get_malware_scanner()`. In development the scanner is a no-op.

## Confirmation Numbers

- **Format**: `UTP-YYYY-NNNN` (e.g. `UTP-2025-0001`).
- **Utility**: `utils.confirmation_number.generate_confirmation_number(prefix="UTP", year=..., next_sequence=...)`. Optionally pass `next_sequence` (callable returning int) for DB-backed sequences.

## Creating a New Service

1. Add a class under `services/` (optionally subclass `services.base.BaseService`).
2. Inject dependencies in `__init__` (e.g. `email_service`, `storage`, or resolved via `get_*()` when not testing).
3. Implement methods with clear inputs and return values.
4. In routes, call `success_response(data=svc.do_something(...))` or `error_response(message=...)` and return `JSONResponse(content=..., status_code=...)`.
5. In tests, construct the service with mocks: `MyService(email_service=mock_email, storage=mock_storage)`.

## Unit Testing

- **Mock factories**: Use `utils.testing.MockEmailService`, `MockStorageBackend`, `MockMalwareScanner`, or the factory helpers `mock_email_service()`, `mock_storage_backend()`, `mock_malware_scanner()`. Pass these into service constructors in tests.
- Use `utils.responses.api_response` / `success_response` / `error_response` in tests to assert response shape.
- See `services/example_service.py` and `tests/test_example_service.py` for a full example; see also [SERVICE_FRAMEWORK.md](SERVICE_FRAMEWORK.md).
- For route-level tests, override `app.dependency_overrides` or the container if you need to inject a test double.
