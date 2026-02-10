"""Run migrations to apply schema updates on startup."""


def _concrete_subclasses(cls: type) -> list[type]:
    """Recursively collect all non-abstract subclasses."""
    result: list[type] = []
    for c in cls.__subclasses__():
        if getattr(c, "__abstract__", False):
            result.extend(_concrete_subclasses(c))
        else:
            result.append(c)
            result.extend(_concrete_subclasses(c))
    return result


def run_migrations() -> None:
    """Create tables for all concrete models (subclasses of BaseModel)."""
    from database.connection import get_db
    from database.models import BaseModel

    db = get_db()
    models = _concrete_subclasses(BaseModel)
    if models:
        db.create_tables(models, safe=True)
