"""User preference capture: record interactions and return simple recommendations."""
from uuid import UUID
from collections import Counter
from typing import Any

from database.models import User, UserInteraction
from utils.responses import error_response, success_response


class PreferenceService:
    """Record user interactions and provide personalized recommendations."""

    def __init__(self) -> None:
        pass

    def record_interaction(
        self,
        user_id: str,
        interaction_type: str,
        target_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Record a single interaction (e.g. page_view, form_section_used)."""
        try:
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid user", data={"code": "invalid_user"})
        if not User.select().where(User.id == uid).exists():
            return error_response("User not found", data={"code": "user_not_found"})
        import json
        meta_json = json.dumps(metadata) if metadata else None
        UserInteraction.create(
            user_id=uid,
            interaction_type=(interaction_type or "unknown")[:64],
            target_id=target_id[:255] if target_id else None,
            metadata_json=meta_json,
        )
        return success_response(message="Recorded")

    def get_recommendations(self, user_id: str, limit: int = 5) -> dict[str, Any]:
        """Return personalized recommendations based on interaction history."""
        try:
            uid = UUID(user_id)
        except (ValueError, TypeError):
            return error_response("Invalid user", data={"code": "invalid_user"})
        interactions = (
            UserInteraction.select(UserInteraction.interaction_type, UserInteraction.target_id)
            .where(UserInteraction.user_id == uid)
            .order_by(UserInteraction.created_at.desc())
            .limit(500)
        )
        type_counts: Counter = Counter()
        target_counts: Counter = Counter()
        for i in interactions:
            type_counts[i.interaction_type] += 1
            if i.target_id:
                target_counts[i.target_id] += 1
        # Simple recommendations: suggest services/pages they haven't used much
        suggestions = []
        if type_counts.get("page_view", 0) > 2 and type_counts.get("form_section", 0) == 0:
            suggestions.append({"type": "service", "title": "Complete an application", "reason": "You’ve been browsing; consider starting an application.", "link": "/dashboard/application"})
        if type_counts.get("page_view", 0) > 0 and "complaints" not in str(target_counts.keys()).lower():
            suggestions.append({"type": "service", "title": "File or track a complaint", "reason": "Based on your activity.", "link": "/complaints"})
        if type_counts.get("page_view", 0) > 0:
            suggestions.append({"type": "data", "title": "Explore public data", "reason": "See program statistics.", "link": "/data"})
        return success_response(data={"recommendations": suggestions[:limit]})
