"""FastAPI dependencies for route protection and user context from JWT."""
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from authentication.errors import TokenInvalidError
from authentication.utils.jwt import validate_token
from authentication.utils.session import should_warn_expiry

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict[str, Any]:
    """
    Extract and validate Bearer token; return decoded payload (user context).
    Raises 401 if missing or invalid. Use as Depends() for protected routes.
    """
    if not credentials or credentials.credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = validate_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Optional: add X-Session-Warning if expiring soon
    exp = payload.get("exp")
    if exp and should_warn_expiry(int(exp)):
        pass  # Caller can set response header; or set in middleware
    return payload


def require_auth(
    user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Alias for get_current_user when you just need the user context."""
    return user
