"""Service registration and dependency injection container."""
import logging
import os
from typing import Any

from config import DEBUG

logger = logging.getLogger(__name__)


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
    # Email: SMTP in production, console in development
    try:
        from core.email import ConsoleEmailService, SmtpEmailService
        _email_service = SmtpEmailService() if _use_production_email() else ConsoleEmailService()
        logger.info("Email service initialized: %s", "SMTP" if _use_production_email() else "console")
    except Exception as e:
        logger.warning("Email service initialization failed: %s", e)
        from core.email import ConsoleEmailService
        _email_service = ConsoleEmailService()

    # Storage: local or S3 from storage lib factory
    try:
        from storage.factory import get_storage as _create_storage
        _storage_backend = _create_storage()
        logger.info("Storage backend initialized")
    except Exception as e:
        logger.warning("Storage backend initialization failed: %s", e)
        _storage_backend = None

    # Malware scanner: NoOp in dev, pluggable in prod
    try:
        if DEBUG or os.getenv("MALWARE_SCAN_DISABLED", "true").lower() in ("true", "1", "yes"):
            from storage.scanning import NoOpScanner
            _malware_scanner = NoOpScanner()
            logger.info("Malware scanner: disabled (NoOp)")
        else:
            from storage.scanning import NoOpScanner
            _malware_scanner = NoOpScanner()
            logger.info("Malware scanner: NoOp (configure production scanner as needed)")
    except Exception as e:
        logger.warning("Malware scanner initialization failed: %s", e)
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
    if _storage_backend is None:
        raise RuntimeError("Storage backend not available; check initialization logs.")
    return _storage_backend


def get_malware_scanner() -> Any:
    """Return the registered malware scanner (NoOp in dev, pluggable in prod)."""
    if _malware_scanner is None:
        init_container()
    return _malware_scanner
