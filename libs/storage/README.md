# Storage library

Pluggable file storage: local filesystem (development) and Amazon S3 (production).

## Configuration

- `STORAGE_PROVIDER` or `STORAGE_BACKEND`: `local` (default) or `s3`
- Local: `LOCAL_STORAGE_PATH` (default `./uploads`)
- S3: `S3_BUCKET`, `AWS_REGION`, optional `S3_PREFIX`. Install optional deps: `pip install storage[s3]` (boto3)

## Usage

```python
from storage import get_storage
from storage.validation import validate_file

backend = get_storage()
ok, err = validate_file(filename="doc.pdf", content_type="application/pdf", size=1024)
if ok:
    meta = backend.upload(file_obj, key="path/to/key", content_type="...", original_filename="doc.pdf")
    url = backend.get_url(meta.storage_key)
```

## Validation

- Allowed types: PDF, JPG, PNG (10MB max). Use `storage.validation.validate_file()`.

## Malware scanning

- Use `storage.scanning.MalwareScanner` in production; `NoOpScanner` for development.

## Adding a new backend

Implement `StorageBackend` (see `storage.interfaces.base`) and register it in `storage.factory.get_storage()`.
