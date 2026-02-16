"""Seed site ownership and project type options if tables are empty."""
import logging

logger = logging.getLogger(__name__)


def seed_project_options() -> None:
    """Insert default site ownership and project type options if empty."""
    try:
        from database.models import SiteOwnership, ProjectType
        from data.project_seed import DEFAULT_SITE_OWNERSHIP, DEFAULT_PROJECT_TYPES
    except ImportError as e:
        logger.warning("Project options seed skipped: %s", e)
        return
    if SiteOwnership.select().count() == 0:
        for row in DEFAULT_SITE_OWNERSHIP:
            SiteOwnership.get_or_create(code=row["code"], defaults={"label": row["label"]})
        logger.info("Seeded %d site ownership options", len(DEFAULT_SITE_OWNERSHIP))
    if ProjectType.select().count() == 0:
        for row in DEFAULT_PROJECT_TYPES:
            ProjectType.get_or_create(code=row["code"], defaults={"label": row["label"]})
        logger.info("Seeded %d project type options", len(DEFAULT_PROJECT_TYPES))
