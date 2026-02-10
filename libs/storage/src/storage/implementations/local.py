"""Local filesystem storage implementation."""
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO

from storage.interfaces.base import FileMetadata, StorageBackend


class LocalStorageBackend(StorageBackend):
    """Store files on local disk, organized by date/type."""

    def __init__(self, root_path: str | Path) -> None:
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.root / key

    def upload(
        self,
        file_obj: BinaryIO,
        *,
        key: str,
        content_type: str,
        original_filename: str,
    ) -> FileMetadata:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = file_obj.read()
        path.write_bytes(data)
        return FileMetadata(
            storage_key=key,
            original_filename=original_filename,
            size=len(data),
            content_type=content_type,
            uploaded_at=datetime.now(timezone.utc).isoformat(),
        )

    def download(self, key: str) -> bytes:
        path = self._path(key)
        if not path.exists():
            raise FileNotFoundError(key)
        return path.read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def get_metadata(self, key: str) -> FileMetadata | None:
        path = self._path(key)
        if not path.exists():
            return None
        stat = path.stat()
        return FileMetadata(
            storage_key=key,
            original_filename=path.name,
            size=stat.st_size,
            content_type="application/octet-stream",
            uploaded_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        )

    def get_url(self, key: str) -> str:
        return str(self._path(key).resolve())
