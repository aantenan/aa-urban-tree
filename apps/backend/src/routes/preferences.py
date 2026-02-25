"""User preference capture: record interactions and get recommendations."""
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from auth_deps import get_current_user
from database.models import User
from services.preference_service import PreferenceService
from utils.responses import error_response

router = APIRouter(prefix="/preferences", tags=["preferences"])


class RecordInteractionBody(BaseModel):
    interaction_type: str
    target_id: str | None = None
    metadata: dict | None = None


def _resolve_user_id(payload: dict) -> str | None:
    from uuid import UUID
    sub = payload.get("sub")
    if not sub:
        return None
    try:
        UUID(str(sub))
        return str(sub)
    except (ValueError, TypeError):
        pass
    email = (sub or "").strip().lower()
    try:
        user = User.get(User.email == email)
        return str(user.id)
    except User.DoesNotExist:
        return None


def _preference_service() -> PreferenceService:
    return PreferenceService()


def _user_or_401(user: dict):
    user_id = _resolve_user_id(user)
    if not user_id:
        return None, JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response("User not found"),
        )
    return user_id, None


@router.post("/interaction")
async def record_interaction(
    body: RecordInteractionBody,
    user: dict = Depends(get_current_user),
    svc: PreferenceService = Depends(_preference_service),
):
    """Record a user interaction for preference learning (authenticated)."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.record_interaction(
        user_id,
        body.interaction_type,
        target_id=body.target_id,
        metadata=body.metadata,
    )
    if not result.get("success"):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=result)
    return JSONResponse(content=result)


@router.get("/recommendations")
async def get_recommendations(
    user: dict = Depends(get_current_user),
    svc: PreferenceService = Depends(_preference_service),
    limit: int = 5,
):
    """Get personalized recommendations based on interaction history."""
    user_id, err = _user_or_401(user)
    if err is not None:
        return err
    result = svc.get_recommendations(user_id, limit=limit)
    return JSONResponse(content=result)
