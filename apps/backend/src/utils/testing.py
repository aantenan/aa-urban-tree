"""Unit testing utilities: mock factories for email, storage, and scanner dependencies."""
from typing import Any, BinaryIO


class MockEmailService:
    """In-memory email mock for tests. Inspect .sent for assertions."""

    def __init__(self) -> None:
        self.sent: list[dict[str, Any]] = []

    def send(
        self,
        to: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.sent.append({
            "to": to,
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
            **kwargs,
        })


class MockStorageBackend:
    """In-memory file storage mock for tests. Store/retrieve by key."""

    def __init__(self) -> None:
        self._store: dict[str, bytes] = {}
        self._meta: dict[str, dict] = {}

    def upload(
        self,
        file_obj: BinaryIO,
        *,
        key: str,
        content_type: str,
        original_filename: str,
    ) -> Any:
        data = file_obj.read()
        self._store[key] = data
        from datetime import datetime
        self._meta[key] = {
            "storage_key": key,
            "original_filename": original_filename,
            "size": len(data),
            "content_type": content_type,
            "uploaded_at": datetime.utcnow().isoformat() + "Z",
        }
        return self._meta[key]

    def download(self, key: str) -> bytes:
        if key not in self._store:
            raise FileNotFoundError(key)
        return self._store[key]

    def delete(self, key: str) -> None:
        self._store.pop(key, None)
        self._meta.pop(key, None)

    def get_metadata(self, key: str) -> Any:
        return self._meta.get(key)

    def get_url(self, key: str) -> str:
        return f"/mock/{key}"


class MockMalwareScanner:
    """Configurable scanner mock: set .safe to control scan result."""

    def __init__(self, safe: bool = True) -> None:
        self.safe = safe
        self.scanned: list[tuple[str, str]] = []

    def scan(self, file_obj: BinaryIO, filename: str) -> tuple[bool, str]:
        self.scanned.append((filename, getattr(file_obj, "name", "")))
        return (self.safe, "" if self.safe else "Mock threat")


def mock_email_service() -> MockEmailService:
    """Factory for a fresh MockEmailService."""
    return MockEmailService()


def mock_storage_backend() -> MockStorageBackend:
    """Factory for a fresh MockStorageBackend."""
    return MockStorageBackend()


def mock_malware_scanner(safe: bool = True) -> MockMalwareScanner:
    """Factory for a MockMalwareScanner."""
    return MockMalwareScanner(safe=safe)
