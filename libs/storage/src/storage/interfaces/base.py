"""Abstract file storage interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import BinaryIO


@dataclass
class FileMetadata:
    """Metadata for a stored file."""

    storage_key: str
    original_filename: str
    size: int
    content_type: str
    uploaded_at: str  # ISO datetime


class StorageBackend(ABC):
    """Abstract interface for file storage (upload, download, delete, metadata)."""

    @abstractmethod
    def upload(
        self,
        file_obj: BinaryIO,
        *,
        key: str,
        content_type: str,
        original_filename: str,
    ) -> FileMetadata:
        """Store a file and return its metadata."""
        ...

    @abstractmethod
    def download(self, key: str) -> bytes:
        """Retrieve file contents by key. Raises if not found."""
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        """Remove a file by key. No-op if not found."""
        ...

    @abstractmethod
    def get_metadata(self, key: str) -> FileMetadata | None:
        """Return metadata for a key, or None if not found."""
        ...

    @abstractmethod
    def get_url(self, key: str) -> str:
        """Return a URL for secure access to the file (or path for local)."""
        ...
