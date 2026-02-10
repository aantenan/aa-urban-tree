"""Storage backend factory from environment."""
import os
from pathlib import Path

from storage.implementations.local import LocalStorageBackend
from storage.implementations.s3 import S3StorageBackend
from storage.interfaces.base import StorageBackend


def get_storage() -> StorageBackend:
    """
    Return the configured storage backend.
    STORAGE_PROVIDER=local|s3 (default: local).
    For local: LOCAL_STORAGE_PATH. For s3: S3_BUCKET, AWS_REGION, optional S3_PREFIX.
    """
    provider = (os.getenv("STORAGE_PROVIDER") or os.getenv("STORAGE_BACKEND") or "local").lower()
    if provider == "s3":
        bucket = os.getenv("S3_BUCKET", "")
        if not bucket:
            raise ValueError("S3_BUCKET is required when STORAGE_PROVIDER=s3")
        return S3StorageBackend(
            bucket=bucket,
            region=os.getenv("AWS_REGION"),
            prefix=os.getenv("S3_PREFIX", ""),
        )
    path = os.getenv("LOCAL_STORAGE_PATH", "./uploads")
    return LocalStorageBackend(Path(path))
