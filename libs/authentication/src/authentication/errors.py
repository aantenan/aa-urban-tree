"""Authentication errors with security-conscious messaging (avoid leaking info)."""


class AuthError(Exception):
    """Base for auth-related errors. Use specific subclasses for API responses."""

    def __init__(self, message: str = "Authentication error", public_message: str | None = None):
        super().__init__(message)
        self.public_message = public_message or "Invalid request."


class InvalidCredentialsError(AuthError):
    """Invalid email or password. Public message is generic to avoid user enumeration."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid credentials",
            public_message="Invalid email or password.",
        )


class AccountLockedError(AuthError):
    """Account temporarily locked after too many failed attempts."""

    def __init__(self, lockout_seconds: int = 900) -> None:
        super().__init__(
            message="Account locked",
            public_message=f"Account temporarily locked. Try again in {lockout_seconds // 60} minutes.",
        )


class TokenInvalidError(AuthError):
    """Invalid or expired token."""

    def __init__(self) -> None:
        super().__init__(
            message="Invalid token",
            public_message="Invalid or expired session. Please sign in again.",
        )


class PasswordComplexityError(AuthError):
    """Password does not meet complexity requirements."""

    def __init__(self, detail: str) -> None:
        super().__init__(message=detail, public_message=detail)
