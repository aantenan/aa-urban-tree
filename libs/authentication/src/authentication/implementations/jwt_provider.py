"""JWT authentication implementation: signing, validation, refresh, lockout, password rules."""
from datetime import datetime, timezone, timedelta
from typing import Any

from authentication.errors import AccountLockedError, InvalidCredentialsError
from authentication.interfaces.auth_provider import AuthProvider, UserRepository
from authentication.utils import (
    LockoutTracker,
    create_token,
    hash_password,
    validate_password_complexity,
    validate_token,
    verify_password,
)
from authentication.utils.email_validator import validate_email_format

LOCKOUT_ATTEMPTS = 5
LOCKOUT_SECONDS = 900
RESET_TOKEN_HOURS = 24


def _user_payload(user: Any, role: str = "user") -> dict[str, Any]:
    """Build user dict for response (id, email, name, role)."""
    uid = getattr(user, "id", None)
    email = getattr(user, "email", "")
    return {
        "id": str(uid) if uid is not None else email,
        "email": email,
        "name": email.split("@")[0] if email else "",
        "role": getattr(user, "role", None) or role,
    }


class JwtAuthProvider(AuthProvider):
    """Full JWT auth: authenticate, verify, register, refresh, reset_password, lockout, session (2h)."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._repo = user_repository
        self._lockout = LockoutTracker(max_attempts=LOCKOUT_ATTEMPTS, lockout_seconds=LOCKOUT_SECONDS)

    def authenticate(self, email: str, password: str) -> dict[str, Any] | None:
        email = (email or "").strip().lower()
        if self._lockout.is_locked(email):
            raise AccountLockedError()
        user = self._repo.get_by_email(email)
        if not user:
            self._lockout.record_failure(email)
            self._repo.record_login_attempt(email, False, None)
            return None
        if getattr(user, "account_status", "active") == "locked":
            raise AccountLockedError()
        if not verify_password(password, getattr(user, "password_hash", "")):
            self._lockout.record_failure(email)
            self._repo.record_login_attempt(email, False, None)
            return None
        self._lockout.reset(email)
        self._repo.record_login_attempt(email, True, None)
        payload = {"sub": str(getattr(user, "id", user)), "email": getattr(user, "email", email)}
        token = create_token(payload)
        return {"token": token, "user": _user_payload(user)}

    def verify(self, token: str) -> dict[str, Any] | None:
        return validate_token(token)

    def register(self, email: str, password: str, **kwargs: Any) -> dict[str, Any]:
        ok, msg = validate_email_format(email)
        if not ok:
            raise ValueError(msg)
        email = email.strip().lower()
        ok, msg = validate_password_complexity(password)
        if not ok:
            raise ValueError(msg)
        if self._repo.email_exists(email):
            raise ValueError("This email is already registered.")
        password_hash = hash_password(password)
        user = self._repo.create_user(email, password_hash, **kwargs)
        return {"user": _user_payload(user), "message": "Registration successful."}

    def logout(self, token: str) -> None:
        pass  # Stateless JWT; client clears token

    def refresh_token(self, token: str) -> dict[str, Any] | None:
        payload = validate_token(token)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = self._repo.get_by_id(str(user_id))
        if not user:
            return None
        new_token = create_token({"sub": str(getattr(user, "id", user_id)), "email": getattr(user, "email", "")})
        return {"token": new_token, "user": _user_payload(user)}

    def reset_password(self, token: str, new_password: str) -> dict[str, Any]:
        ok, msg = validate_password_complexity(new_password)
        if not ok:
            raise ValueError(msg)
        pr = self._repo.get_password_reset(token)
        if not pr:
            raise ValueError("Invalid or expired reset token.")
        if getattr(pr, "used_at", None) is not None:
            raise ValueError("Reset token already used.")
        expires_at = getattr(pr, "expires_at", None)
        if expires_at is not None and expires_at < datetime.now(timezone.utc):
            raise ValueError("Reset token has expired.")
        user_id = str(getattr(pr, "user_id", getattr(pr, "user", None)))
        if hasattr(pr, "user") and pr.user is not None:
            user_id = str(getattr(pr.user, "id", user_id))
        self._repo.update_password(user_id, hash_password(new_password))
        self._repo.mark_password_reset_used(token)
        return {"message": "Password has been reset."}

    def lock_account(self, identifier: str) -> None:
        user = self._repo.get_by_email(identifier.strip().lower()) or self._repo.get_by_id(identifier)
        if user:
            self._repo.set_account_status(str(getattr(user, "id", identifier)), "locked")

    def unlock_account(self, identifier: str) -> None:
        user = self._repo.get_by_email(identifier.strip().lower()) or self._repo.get_by_id(identifier)
        if user:
            self._repo.set_account_status(str(getattr(user, "id", identifier)), "active")
