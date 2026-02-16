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
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
