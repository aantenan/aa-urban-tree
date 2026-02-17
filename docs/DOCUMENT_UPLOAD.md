# Document Upload Workflow and Security

This document describes the document management project structure, upload workflow, validation, and security considerations.

## Overview

Document Management handles uploads of supporting documents for grant applications. Applicants upload site plans, photographs, and optional supporting materials, organized by category. Files are validated before storage; thumbnails are generated for images; malware scanning is applied in production.

## Project Structure

```
apps/backend/src/
├── documents/
│   ├── __init__.py      # Exports
│   ├── categories.py    # Document category definitions and validation
│   ├── errors.py        # Error handling for upload failures
│   ├── validation.py    # File format, size, category validation
│   └── thumbnail.py     # Thumbnail generation (Pillow; logic TBD)
├── core/
│   ├── upload.py        # File validation, malware scan integration
│   └── container.py     # Storage, malware scanner DI
└── config.py            # STORAGE_BACKEND, LOCAL_STORAGE_PATH, etc.
```

## Document Categories

- **Site Plan** (`site_plan`)
- **Site Photos** (`site_photos`)
- **Supporting Documents** (`supporting_documents`)

Category validation: `documents.categories.validate_category()` and `documents.validation.validate_document_upload()`.

## File Validation

- **Formats**: PDF, JPG, PNG only
- **Size**: Maximum 10MB per file
- **Content-Type**: Must match extension (`application/pdf`, `image/jpeg`, `image/png`)

Use `documents.validation.validate_document_upload()` for format, size, and category. Use `validate_document_upload_and_scan()` when malware scanning is required.

## Multipart Form Data

FastAPI handles `multipart/form-data` natively. Use `File()` and `Form()` for upload endpoints:

```python
from fastapi import File, Form, UploadFile

@router.post("/documents")
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form(...),
):
    contents = await file.read()
    ok, msg = validate_document_upload(
        filename=file.filename or "",
        content_type=file.content_type or "",
        size=len(contents),
        category=category,
    )
    if not ok:
        raise HTTPException(400, msg)
    # ... store and return
```

## Security Considerations

### File Access

- **Authentication**: All document endpoints require authentication
- **Ownership**: Applicants can only upload/delete documents for their own applications
- **Reviewers**: Can view documents for applications they are reviewing
- **Post-submission**: Applicants cannot modify documents after submission; only admins can

### Malware Scanning

- **Development**: `MALWARE_SCAN_DISABLED=true` (default)—NoOpScanner, no scan
- **Production**: Set `MALWARE_SCAN_DISABLED=false` and configure a malware scanner (e.g. ClamAV) via `storage.scanning`

Files are scanned before being written to storage. If the scan fails or detects malware, the upload is rejected.

### Storage Configuration

- **Development**: `STORAGE_BACKEND=local`, `LOCAL_STORAGE_PATH=./uploads`
- **Production**: `STORAGE_BACKEND=s3` with `S3_BUCKET`, `AWS_REGION`, etc.

File paths stored in the database are system-generated unique identifiers. Original filenames are stored separately for display. Do not serve files directly from user-provided paths; always resolve through the database record.

### Thumbnail Generation

Pillow (PIL) is used for image thumbnail generation. Thumbnails are stored separately; only image types (JPG, PNG) receive thumbnails. PDF thumbnails require additional tooling (out of scope for initial implementation).

## Error Handling

Document-specific errors:

- `FileValidationError`: Invalid format, size, or content type
- `CategoryValidationError`: Invalid document category
- `FileUploadError`: Storage or permission failure
- `MalwareScanError`: Scan failed or threat detected

Use `documents.errors` and return appropriate HTTP status codes (400 for validation, 403 for access, 500 for server errors).

## Dependencies

- **Pillow**: Image processing for thumbnail generation
- **storage**: Pluggable backend (local/S3), validation, malware scanning interface
- **FastAPI**: Built-in multipart support; no extra package for `multipart/form-data`

## Testing

Unit tests use `tempfile` for temporary files and `BytesIO` for in-memory file objects. See `tests/test_document_validation.py` for patterns. Mock the storage backend and malware scanner in service tests.
