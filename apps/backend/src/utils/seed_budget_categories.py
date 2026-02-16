"""Seed budget category options if table is empty."""
import logging

logger = logging.getLogger(__name__)


def seed_budget_categories() -> None:
    """Insert default budget categories if empty."""
    try:
        from database.models import BudgetCategory
        from data.budget_categories_seed import DEFAULT_BUDGET_CATEGORIES
    except ImportError as e:
        logger.warning("Budget categories seed skipped: %s", e)
        return
    if BudgetCategory.select().count() == 0:
        for row in DEFAULT_BUDGET_CATEGORIES:
            BudgetCategory.get_or_create(code=row["code"], defaults={"label": row["label"]})
        logger.info("Seeded %d budget categories", len(DEFAULT_BUDGET_CATEGORIES))
