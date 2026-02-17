"""Document upload and management: validation, categories, error handling."""
from documents.categories import (
    DOCUMENT_CATEGORIES,
    DOCUMENT_CATEGORY_SITE_PHOTOS,
    DOCUMENT_CATEGORY_SITE_PLAN,
    DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS,
    is_valid_category,
    normalize_category,
)
from documents.errors import (
    CategoryValidationError,
    DocumentError,
    FileUploadError,
    FileValidationError,
    MalwareScanError,
)
from documents.validation import validate_document_upload, validate_document_upload_and_scan

__all__ = [
    "DOCUMENT_CATEGORIES",
    "DOCUMENT_CATEGORY_SITE_PLAN",
    "DOCUMENT_CATEGORY_SITE_PHOTOS",
    "DOCUMENT_CATEGORY_SUPPORTING_DOCUMENTS",
    "DocumentError",
    "FileValidationError",
    "FileUploadError",
    "CategoryValidationError",
    "MalwareScanError",
    "is_valid_category",
    "normalize_category",
    "validate_document_upload",
    "validate_document_upload_and_scan",
]
