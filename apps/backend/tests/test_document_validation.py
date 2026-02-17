"""Tests for document validation and file operations with temporary file handling."""
import os
import tempfile
from io import BytesIO

import pytest

from documents.categories import is_valid_category, normalize_category, validate_category
from documents.validation import validate_document_upload


class TestDocumentCategories:
    """Tests for document category validation."""

    def test_valid_categories(self) -> None:
        """All valid categories are accepted."""
        for cat in ("site_plan", "site_photos", "supporting_documents"):
            assert is_valid_category(cat) is True
            ok, msg = validate_category(cat)
            assert ok is True
            assert msg == ""

    def test_category_normalization(self) -> None:
        """Category aliases normalize to DB format."""
        assert normalize_category("Site Plan") == "site_plan"
        assert normalize_category("site photos") == "site_photos"
        assert normalize_category("supporting_documents") == "supporting_documents"

    def test_invalid_category_rejected(self) -> None:
        """Invalid categories are rejected."""
        ok, msg = validate_category("invalid")
        assert ok is False
        assert "Invalid category" in msg

    def test_empty_category_rejected(self) -> None:
        """Empty category is rejected."""
        ok, msg = validate_category("")
        assert ok is False
        assert "required" in msg.lower()


class TestDocumentUploadValidation:
    """Tests for document upload validation with temp files."""

    def test_valid_pdf_passes(self) -> None:
        """Valid PDF upload passes validation."""
        ok, msg = validate_document_upload(
            filename="plan.pdf",
            content_type="application/pdf",
            size=1024,
            category="site_plan",
        )
        assert ok is True
        assert msg == ""

    def test_valid_jpeg_passes(self) -> None:
        """Valid JPEG upload passes validation."""
        ok, msg = validate_document_upload(
            filename="photo.jpg",
            content_type="image/jpeg",
            size=50000,
            category="site_photos",
        )
        assert ok is True
        assert msg == ""

    def test_valid_png_passes(self) -> None:
        """Valid PNG upload passes validation."""
        ok, msg = validate_document_upload(
            filename="image.png",
            content_type="image/png",
            size=100000,
            category="supporting_documents",
        )
        assert ok is True
        assert msg == ""

    def test_invalid_extension_rejected(self) -> None:
        """Invalid file extension is rejected."""
        ok, msg = validate_document_upload(
            filename="doc.exe",
            content_type="application/octet-stream",
            size=1024,
            category="site_plan",
        )
        assert ok is False
        assert "allowed" in msg.lower() or "type" in msg.lower()

    def test_oversized_file_rejected(self) -> None:
        """File exceeding 10MB is rejected."""
        ok, msg = validate_document_upload(
            filename="large.pdf",
            content_type="application/pdf",
            size=11 * 1024 * 1024,
            category="site_plan",
        )
        assert ok is False
        assert "size" in msg.lower() or "limit" in msg.lower()

    def test_invalid_category_fails_upload_validation(self) -> None:
        """Invalid category fails document upload validation."""
        ok, msg = validate_document_upload(
            filename="plan.pdf",
            content_type="application/pdf",
            size=1024,
            category="invalid_category",
        )
        assert ok is False
        assert "category" in msg.lower()


class TestTempFileOperations:
    """Tests using temporary files for file operation patterns."""

    def test_temp_file_readable(self) -> None:
        """Temporary file can be created and read."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"%PDF-1.4 fake content")
            path = f.name
        try:
            with open(path, "rb") as f:
                content = f.read()
            assert content == b"%PDF-1.4 fake content"
        finally:
            os.unlink(path)

    def test_temp_directory_cleanup(self) -> None:
        """Temporary directory is cleaned up after use."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.pdf")
            with open(filepath, "wb") as f:
                f.write(b"content")
            assert os.path.exists(filepath)
        assert not os.path.exists(tmpdir)

    def test_bytes_io_as_file_obj(self) -> None:
        """BytesIO can be used as file-like object for validation."""
        # validate_document_upload doesn't take file_obj, but validate_and_scan does
        # This tests the pattern of using in-memory file objects
        bio = BytesIO(b"%PDF-1.4 minimal")
        assert bio.readable()
        bio.seek(0)
        assert bio.read() == b"%PDF-1.4 minimal"
