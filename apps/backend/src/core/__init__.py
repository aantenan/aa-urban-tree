"""Core framework: DI container, email abstraction, file upload validation."""
from core.container import get_email_service, get_malware_scanner, get_storage, init_container
from core.email import ConsoleEmailService, EmailService, SmtpEmailService
from core.upload import scan_for_malware, validate_and_scan, validate_upload

__all__ = [
    "EmailService",
    "ConsoleEmailService",
    "SmtpEmailService",
    "get_email_service",
    "get_storage",
    "get_malware_scanner",
    "init_container",
    "validate_upload",
    "scan_for_malware",
    "validate_and_scan",
]
