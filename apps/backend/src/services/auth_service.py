"""User authentication service: register, login, logout, forgot/reset password, refresh token."""
import secrets
from datetime import datetime, timezone, timedelta
from typing import Any

from authentication import (
    InvalidCredentialsError,
    AccountLockedError,
    hash_password,
    verify_password,
    validate_password_complexity,
    create_token,
    validate_token,
    LockoutTracker,
    validate_email_format,
)
from database.models import User, PasswordReset, LoginAttempt

try:
    from email_svc import send_email
except ImportError:
    send_email = None  # type: ignore

# Lockout: 5 attempts, 15 min window
_lockout = LockoutTracker(max_attempts=5, lockout_seconds=900)
RESET_TOKEN_EXPIRE_HOURS = 24


def _user_to_dict(user: User) -> dict[str, Any]:
    return {"id": str(user.id), "email": user.email, "name": user.email.split("@")[0]}


class UserAuthenticationService:
    """Authentication with constructor dependency injection (DB, email optional)."""

    def __init__(self) -> None:
        pass

    def register(self, email: str, password: str, name: str | None = None) -> dict[str, Any]:
        """Register user: validate email and password, create user, send confirmation email."""
        ok, msg = validate_email_format(email)
        if not ok:
            raise ValueError(msg)
        email = email.strip().lower()
        ok, msg = validate_password_complexity(password)
        if not ok:
            raise ValueError(msg)
        if User.select().where(User.email == email).exists():
            raise ValueError("This email is already registered.")
        password_hash = hash_password(password)
        user = User.create(email=email, password_hash=password_hash, account_status="active")
        if name:
            pass  # User model has no name field; could add later
        if send_email:
            send_email(
                to=email,
                subject="Welcome – Urban Tree Grant",
                body_text=f"Your account has been created. You can sign in at the application site.",
            )
        return {"user": _user_to_dict(user), "message": "Registration successful."}

    def login(self, email: str, password: str, ip_address: str | None = None) -> dict[str, Any]:
        """Authenticate user; record attempt; enforce lockout; return JWT and user."""
        email = (email or "").strip().lower()
        if _lockout.is_locked(email):
            raise AccountLockedError()
        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            _record_attempt(email, False, ip_address)
            _lockout.record_failure(email)
            raise InvalidCredentialsError()
        if user.account_status == "locked":
            raise AccountLockedError()
        if not verify_password(password, user.password_hash):
            _record_attempt(email, False, ip_address)
            _lockout.record_failure(email)
            raise InvalidCredentialsError()
        _record_attempt(email, True, ip_address)
        _lockout.reset(email)
        payload = {"sub": str(user.id), "email": user.email}
        token = create_token(payload)
        return {"token": token, "user": _user_to_dict(user)}

    def logout(self, token: str | None) -> None:
        """Client-side cleanup; server-side JWT invalidation optional (e.g. blacklist). No-op for stateless JWT."""
        pass

    def forgot_password(self, email: str) -> dict[str, Any]:
        """Create reset token (24h), send email. Always return same message to avoid enumeration."""
        email = email.strip().lower()
        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            return {"message": "If an account exists for that email, you will receive a reset link."}
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_EXPIRE_HOURS)
        PasswordReset.create(user=user, reset_token=reset_token, expires_at=expires_at)
        reset_link = f"/reset-password?token={reset_token}"  # Frontend URL
        if send_email:
            send_email(
                to=email,
                subject="Password reset – Urban Tree Grant",
                body_text=f"Use this link to reset your password (valid 24 hours): {reset_link}",
            )
        return {"message": "If an account exists for that email, you will receive a reset link."}

    def reset_password(self, token: str, new_password: str) -> dict[str, Any]:
        """Validate token, check password complexity, update password, mark token used."""
        ok, msg = validate_password_complexity(new_password)
        if not ok:
            raise ValueError(msg)
        try:
            pr = PasswordReset.get(
                (PasswordReset.reset_token == token) & (PasswordReset.used_at >> None),
            )
        except PasswordReset.DoesNotExist:
            raise ValueError("Invalid or expired reset token.")
        if pr.expires_at < datetime.now(timezone.utc):
            raise ValueError("Reset token has expired.")
        user = pr.user
        user.password_hash = hash_password(new_password)
        user.save()
        pr.used_at = datetime.now(timezone.utc)
        pr.save()
        return {"message": "Password has been reset. You can sign in with your new password."}

    def refresh_token(self, current_token: str) -> dict[str, Any]:
        """Issue new JWT if current token is valid (session extension)."""
        payload = validate_token(current_token)
        if not payload:
            raise InvalidCredentialsError()
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidCredentialsError()
        try:
            user = User.get(User.id == user_id)
        except User.DoesNotExist:
            raise InvalidCredentialsError()
        new_token = create_token({"sub": str(user.id), "email": user.email})
        return {"token": new_token, "user": _user_to_dict(user)}


def _record_attempt(email: str, success: bool, ip_address: str | None) -> None:
    LoginAttempt.create(email=email, success=success, ip_address=ip_address)
