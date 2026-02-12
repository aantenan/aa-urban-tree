"""File upload validation: format, size, and optional malware scan."""
from typing import BinaryIO

from storage.validation import validate_file as _validate_file


def validate_upload(
    *,
    filename: str,
    content_type: str,
    size: int,
) -> tuple[bool, str]:
    """
    Validate file (PDF, JPG, PNG; 10MB limit).
    Returns (ok, error_message). error_message is empty when ok is True.
    """
    return _validate_file(
        filename=filename,
        content_type=content_type,
        size=size,
    )


def scan_for_malware(file_obj: BinaryIO, filename: str, scanner=None) -> tuple[bool, str]:
    """
    Run malware scan if scanner is provided. Otherwise returns (True, "").
    Returns (safe, message). safe is False if malware or error.
    """
    if scanner is None:
        return True, ""
    return scanner.scan(file_obj, filename)


def validate_and_scan(
    *,
    filename: str,
    content_type: str,
    size: int,
    file_obj: BinaryIO | None = None,
    scanner=None,
) -> tuple[bool, str]:
    """
    Validate format/size then optionally scan. file_obj required only if scanner is set.
    Returns (ok, error_message).
    """
    ok, msg = validate_upload(filename=filename, content_type=content_type, size=size)
    if not ok:
        return False, msg
    if scanner and file_obj is not None:
        safe, scan_msg = scan_for_malware(file_obj, filename, scanner)
        if not safe:
            return False, scan_msg or "File scan failed."
    return True, ""
