"""Account lockout tracking for brute-force prevention (5 failed attempts = lockout)."""
import os
import time
from threading import Lock

DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_LOCKOUT_SECONDS = 900  # 15 min


class LockoutTracker:
    """
    Tracks failed login attempts per identifier (e.g. email).
    After max_attempts failures, account is locked for lockout_seconds.
    Thread-safe in-memory store; replace with Redis/DB for multi-process.
    """

    def __init__(
        self,
        max_attempts: int | None = None,
        lockout_seconds: int | None = None,
    ) -> None:
        self._max_attempts = max_attempts or int(os.getenv("LOCKOUT_MAX_ATTEMPTS", str(DEFAULT_MAX_ATTEMPTS)))
        self._lockout_seconds = lockout_seconds or int(os.getenv("LOCKOUT_SECONDS", str(DEFAULT_LOCKOUT_SECONDS)))
        self._failures: dict[str, list[float]] = {}
        self._locked_until: dict[str, float] = {}
        self._lock = Lock()

    def _key(self, identifier: str) -> str:
        return (identifier or "").strip().lower()

    def record_failure(self, identifier: str) -> None:
        """Record a failed attempt for identifier."""
        key = self._key(identifier)
        if not key:
            return
        with self._lock:
            self._failures.setdefault(key, []).append(time.time())
            # Trim to last max_attempts
            self._failures[key] = self._failures[key][-self._max_attempts :]
            if len(self._failures[key]) >= self._max_attempts:
                self._locked_until[key] = time.time() + self._lockout_seconds

    def reset(self, identifier: str) -> None:
        """Clear failure count and lockout for identifier (e.g. after successful login)."""
        key = self._key(identifier)
        with self._lock:
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)

    def is_locked(self, identifier: str) -> bool:
        """True if identifier is currently locked out."""
        key = self._key(identifier)
        with self._lock:
            until = self._locked_until.get(key, 0)
            if until and time.time() < until:
                return True
            if until:
                del self._locked_until[key]
                self._failures.pop(key, None)
            return False

    def remaining_attempts(self, identifier: str) -> int:
        """Remaining attempts before lockout (0 if already locked)."""
        if self.is_locked(identifier):
            return 0
        key = self._key(identifier)
        with self._lock:
            n = len(self._failures.get(key, []))
            return max(0, self._max_attempts - n)
