"""Service registration and dependency injection container."""
import os
from typing import Any

from config import DEBUG


def _use_production_email() -> bool:
    return bool(os.getenv("SMTP_HOST"))


def _use_local_storage() -> bool:
    return os.getenv("STORAGE_BACKEND", "local").lower() == "local"


_email_service: Any = None
_storage_backend: Any = None
_malware_scanner: Any = None


def init_container() -> None:
    """Initialize services from config. Call once at app startup (e.g. in lifespan)."""
    global _email_service, _storage_backend, _malware_scanner
    from core.email import ConsoleEmailService, SmtpEmailService
    _email_service = SmtpEmailService() if _use_production_email() else ConsoleEmailService()

    from storage.factory import get_storage as _create_storage
    _storage_backend = _create_storage()

    if DEBUG or os.getenv("MALWARE_SCAN_DISABLED", "true").lower() in ("true", "1", "yes"):
        from storage.scanning import NoOpScanner
        _malware_scanner = NoOpScanner()
    else:
        from storage.scanning import NoOpScanner
        _malware_scanner = NoOpScanner()


def get_email_service() -> Any:
    """Return the registered email service (Console or SMTP)."""
    if _email_service is None:
        init_container()
    return _email_service


def get_storage() -> Any:
    """Return the registered storage backend (local or S3)."""
    if _storage_backend is None:
        init_container()
    return _storage_backend


def get_malware_scanner() -> Any:
    """Return the registered malware scanner (NoOp in dev, pluggable in prod)."""
    if _malware_scanner is None:
        init_container()
    return _malware_scanner
