"""File validation: format restrictions and size limits."""
from typing import Set

ALLOWED_EXTENSIONS: Set[str] = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_CONTENT_TYPES: Set[str] = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}
MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10MB


def allowed_content_type(content_type: str) -> bool:
    """Return True if content type is allowed."""
    return content_type.strip().lower() in ALLOWED_CONTENT_TYPES


def allowed_extension(filename: str) -> bool:
    """Return True if file extension is allowed."""
    ext = ""
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
    return f".{ext}" in ALLOWED_EXTENSIONS


def allowed_size(size: int) -> bool:
    """Return True if size is within limit."""
    return 0 <= size <= MAX_FILE_SIZE_BYTES


def validate_file(
    *,
    filename: str,
    content_type: str,
    size: int,
) -> tuple[bool, str]:
    """
    Validate file. Returns (ok, error_message).
    error_message is empty when ok is True.
    """
    if not allowed_extension(filename):
        return False, f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    if not allowed_content_type(content_type):
        return False, f"Content type not allowed: {content_type}"
    if not allowed_size(size):
        return False, f"File size exceeds {MAX_FILE_SIZE_BYTES // (1024*1024)}MB limit"
    return True, ""
