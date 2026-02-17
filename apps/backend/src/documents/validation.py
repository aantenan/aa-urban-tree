"""File validation utilities for document management: format, size, and category."""
from typing import BinaryIO

from core.upload import validate_and_scan, validate_upload
from documents.categories import validate_category
from documents.errors import FileValidationError


def validate_document_upload(
    *,
    filename: str,
    content_type: str,
    size: int,
    category: str,
) -> tuple[bool, str]:
    """
    Validate document upload: format (PDF, JPG, PNG), size (10MB max), and category.
    Returns (ok, error_message). error_message is empty when ok is True.
    """
    ok, msg = validate_upload(
        filename=filename,
        content_type=content_type,
        size=size,
    )
    if not ok:
        return False, msg

    ok, msg = validate_category(category)
    if not ok:
        return False, msg

    return True, ""


def validate_document_upload_and_scan(
    *,
    filename: str,
    content_type: str,
    size: int,
    category: str,
    file_obj: BinaryIO | None = None,
    scanner=None,
) -> tuple[bool, str]:
    """
    Validate format, size, category, then optionally run malware scan.
    Returns (ok, error_message).
    """
    ok, msg = validate_document_upload(
        filename=filename,
        content_type=content_type,
        size=size,
        category=category,
    )
    if not ok:
        return False, msg

    ok, msg = validate_and_scan(
        filename=filename,
        content_type=content_type,
        size=size,
        file_obj=file_obj,
        scanner=scanner,
    )
    if not ok:
        return False, msg

    return True, ""
