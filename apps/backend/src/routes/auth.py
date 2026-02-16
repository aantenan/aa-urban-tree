"""Auth routes: register, login, logout, forgot-password, reset-password, refresh-token."""
import os
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class RefreshTokenRequest(BaseModel):
    token: str


class AuthResponse(BaseModel):
    token: str | None = None
    user: dict | None = None
    message: str | None = None


def _auth_service():
    from services.auth_service import UserAuthenticationService
    return UserAuthenticationService()


def _use_jwt_backend() -> bool:
    return (os.getenv("AUTH_PROVIDER") or "mock").lower() == "jwt"


@router.post("/register", response_model=AuthResponse)
def register(body: RegisterRequest) -> AuthResponse:
    """Register with email and password; email uniqueness and password complexity enforced."""
    if not _use_jwt_backend():
        raise HTTPException(status_code=501, detail="Registration is only available with JWT auth backend.")
    svc = _auth_service()
    try:
        out = svc.register(body.email, body.password, body.name)
        return AuthResponse(user=out["user"], message=out.get("message", "Registration successful."))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, request: Request) -> AuthResponse:
    """Authenticate; returns JWT and user. Uses DB+JWT when AUTH_PROVIDER=jwt, else mock provider."""
    ip_address = request.client.host if request.client else None
    if _use_jwt_backend():
        svc = _auth_service()
        try:
            out = svc.login(body.email, body.password, ip_address)
            return AuthResponse(token=out["token"], user=out["user"])
        except Exception as e:
            from authentication.errors import InvalidCredentialsError, AccountLockedError
            if isinstance(e, AccountLockedError):
                raise HTTPException(status_code=429, detail=e.public_message)
            if isinstance(e, InvalidCredentialsError):
                raise HTTPException(status_code=401, detail=e.public_message)
            raise
    from authentication import get_provider
    provider = get_provider()
    result = provider.authenticate(body.email, body.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return AuthResponse(token=result["token"], user=result["user"])


@router.post("/logout", response_model=AuthResponse)
def logout() -> AuthResponse:
    """Client should clear token; server-side no-op for stateless JWT."""
    return AuthResponse(message="Logged out.")


@router.post("/forgot-password", response_model=AuthResponse)
def forgot_password(body: ForgotPasswordRequest) -> AuthResponse:
    """Send password reset email (24h token). Same message whether email exists or not."""
    if not _use_jwt_backend():
        raise HTTPException(status_code=501, detail="Password reset is only available with JWT auth backend.")
    svc = _auth_service()
    out = svc.forgot_password(body.email)
    return AuthResponse(message=out["message"])


@router.post("/reset-password", response_model=AuthResponse)
def reset_password(body: ResetPasswordRequest) -> AuthResponse:
    """Reset password with token; validate complexity."""
    if not _use_jwt_backend():
        raise HTTPException(status_code=501, detail="Password reset is only available with JWT auth backend.")
    svc = _auth_service()
    try:
        out = svc.reset_password(body.token, body.new_password)
        return AuthResponse(message=out["message"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh-token", response_model=AuthResponse)
def refresh_token(body: RefreshTokenRequest) -> AuthResponse:
    """Issue new JWT before expiration (session extension)."""
    if not _use_jwt_backend():
        raise HTTPException(status_code=501, detail="Token refresh is only available with JWT auth backend.")
    svc = _auth_service()
    try:
        out = svc.refresh_token(body.token)
        return AuthResponse(token=out["token"], user=out["user"])
    except Exception as e:
        from authentication.errors import InvalidCredentialsError
        if isinstance(e, InvalidCredentialsError):
            raise HTTPException(status_code=401, detail=e.public_message)
        raise
