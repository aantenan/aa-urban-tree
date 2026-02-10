"""Tests for storage interface and local implementation."""
import io
import tempfile
from pathlib import Path

import pytest

from storage.factory import get_storage
from storage.implementations.local import LocalStorageBackend
from storage.interfaces.base import FileMetadata, StorageBackend
from storage.validation import allowed_extension, allowed_size, validate_file


def test_local_upload_download_delete() -> None:
    with tempfile.TemporaryDirectory() as d:
        backend: StorageBackend = LocalStorageBackend(Path(d))
        key = "test/file.bin"
        data = b"hello"
        meta = backend.upload(
            io.BytesIO(data),
            key=key,
            content_type="application/octet-stream",
            original_filename="file.bin",
        )
        assert meta.storage_key == key
        assert meta.original_filename == "file.bin"
        assert meta.size == len(data)
        assert backend.download(key) == data
        backend.delete(key)
        assert backend.get_metadata(key) is None


def test_validation_allowed() -> None:
    ok, msg = validate_file(
        filename="x.pdf",
        content_type="application/pdf",
        size=1024,
    )
    assert ok is True
    assert msg == ""


def test_validation_size_over() -> None:
    ok, msg = validate_file(
        filename="x.pdf",
        content_type="application/pdf",
        size=11 * 1024 * 1024,
    )
    assert ok is False
    assert "10" in msg


def test_validation_extension() -> None:
    assert allowed_extension("a.pdf") is True
    assert allowed_extension("a.exe") is False
