"""Seed counties table from default list if empty."""
import logging

logger = logging.getLogger(__name__)


def seed_counties() -> None:
    """Insert default counties if the table is empty."""
    try:
        from database.models import County
        from data.counties_seed import DEFAULT_COUNTIES
    except ImportError as e:
        logger.warning("County seed skipped: %s", e)
        return
    if County.select().count() > 0:
        return
    for row in DEFAULT_COUNTIES:
        County.get_or_create(
            name=row["name"],
            state_code=row.get("state_code", ""),
        )
    logger.info("Seeded %d counties", len(DEFAULT_COUNTIES))
