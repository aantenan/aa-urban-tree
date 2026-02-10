"""Malware scanning interface. Production can plug in a scanner; development bypasses."""
from abc import ABC, abstractmethod
from typing import BinaryIO


class MalwareScanner(ABC):
    """Interface for scanning uploads. In development, use NoOpScanner."""

    @abstractmethod
    def scan(self, file_obj: BinaryIO, filename: str) -> tuple[bool, str]:
        """
        Scan file. Returns (safe, message).
        safe is False if malware or error; message describes the result.
        """
        ...


class NoOpScanner(MalwareScanner):
    """No-op scanner for development: always reports safe."""

    def scan(self, file_obj: BinaryIO, filename: str) -> tuple[bool, str]:
        return True, ""
