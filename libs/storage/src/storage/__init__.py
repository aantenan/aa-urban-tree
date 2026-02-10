"""Pluggable file storage library."""
from storage.factory import get_storage
from storage.interfaces.base import FileMetadata, StorageBackend

__all__ = ["get_storage", "StorageBackend", "FileMetadata"]
