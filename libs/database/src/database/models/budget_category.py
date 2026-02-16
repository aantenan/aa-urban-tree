"""Budget category for line item validation (e.g. Labor, Materials)."""
from peewee import CharField

from database.models.base import BaseModel


class BudgetCategory(BaseModel):
    """Allowed category code for line item budget."""

    code = CharField(max_length=64, unique=True, index=True)
    label = CharField(max_length=128)

    class Meta:
        table_name = "budget_category_options"
