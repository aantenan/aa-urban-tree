"""
Auth dependency for protected routes: accepts JWT (when AUTH_PROVIDER=jwt)
or mock provider tokens (when AUTH_PROVIDER=mock) so Dashboard works in both modes.
"""
import os
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any]:
    """
    Validate Bearer token and return user payload. Uses JWT when AUTH_PROVIDER=jwt,
    otherwise uses mock provider verify() so mock login tokens work on protected routes.
    """
    if not credentials or credentials.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    use_jwt = (os.getenv("AUTH_PROVIDER") or "mock").lower() == "jwt"
    if use_jwt:
        from authentication.utils.jwt import validate_token
        payload = validate_token(token)
    else:
        from authentication import get_provider
        payload = get_provider().verify(token)
        # If mock verify missed (e.g. new process after reload), try JWT when token looks like one
        if not payload and token.count(".") == 2:
            try:
                from authentication.utils.jwt import validate_token
                payload = validate_token(token)
            except Exception:
                pass
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any] | None:
    """Return user payload if valid Bearer token present; otherwise None (for optional-auth routes)."""
    if not credentials or credentials.credentials is None:
        return None
    token = credentials.credentials
    use_jwt = (os.getenv("AUTH_PROVIDER") or "mock").lower() == "jwt"
    if use_jwt:
        try:
            from authentication.utils.jwt import validate_token
            return validate_token(token)
        except Exception:
            return None
    from authentication import get_provider
    payload = get_provider().verify(token)
    if not payload and token.count(".") == 2:
        try:
            from authentication.utils.jwt import validate_token
            return validate_token(token)
        except Exception:
            pass
    return payload
