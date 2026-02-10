"""Auth routes: login (and future logout, refresh)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: dict


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest) -> LoginResponse:
    """Authenticate with email/password; returns token and user info (mock or JWT)."""
    from authentication import get_provider
    provider = get_provider()
    result = provider.authenticate(body.email, body.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return LoginResponse(token=result["token"], user=result["user"])
