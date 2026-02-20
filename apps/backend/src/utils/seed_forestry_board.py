"""Seed Forestry Board members for development/testing."""
from database.models import ForestryBoard, User


def seed_forestry_board() -> None:
    """Create forestry board members linked to existing users (e.g. admin@example.com for Baltimore)."""
    for email, county, name, title in [
        ("admin@example.com", "Baltimore", "Jane Boardmember", "Forestry Board Chair"),
        ("dev@example.com", "Montgomery", "Dev Reviewer", "Board Member"),
    ]:
        try:
            user = User.get(User.email == email)
        except User.DoesNotExist:
            continue
        if not ForestryBoard.select().where(ForestryBoard.user_id == user.id).exists():
            ForestryBoard.create(
                user=user,
                county=county,
                board_member_name=name,
                title=title,
                email=user.email,
            )
