"""Error handling patterns for document upload and file operations."""


class DocumentError(Exception):
    """Base exception for document management errors."""

    def __init__(self, message: str, code: str = "document_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class FileValidationError(DocumentError):
    """Raised when file validation fails (format, size, content type)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="validation_error")


class FileUploadError(DocumentError):
    """Raised when file upload fails (storage, permissions, etc.)."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="upload_error")


class CategoryValidationError(DocumentError):
    """Raised when document category is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="category_validation_error")


class MalwareScanError(DocumentError):
    """Raised when malware scan fails or detects threat."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="malware_scan_error")
