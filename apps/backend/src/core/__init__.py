"""Core framework: DI container, email abstraction, file upload validation."""
from core.container import get_email_service, get_malware_scanner, get_storage, init_container
from core.email import ConsoleEmailService, EmailService, SmtpEmailService

__all__ = [
    "EmailService",
    "ConsoleEmailService",
    "SmtpEmailService",
    "get_email_service",
    "get_storage",
    "get_malware_scanner",
    "init_container",
]
