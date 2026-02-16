"""Financial information for an application: costs, grant, matching funds, line item budget."""
from peewee import FloatField, ForeignKeyField, TextField

from database.models.application import Application
from database.models.base import BaseModel


class FinancialInformation(BaseModel):
    """
    Financial information section: one-to-one with Application.
    total_project_cost, grant_amount_requested; matching_funds and line_item_budget stored as JSON.
    Cost-match percentage is computed server-side from matching funds and total cost.
    """

    application = ForeignKeyField(
        Application, backref="financial_information", on_delete="CASCADE", unique=True
    )
    total_project_cost = FloatField(null=True)   # currency, 2 decimal precision
    grant_amount_requested = FloatField(null=True)
    # JSON: [ {"source_name": str, "amount": float, "type": "cash"|"in_kind"}, ... ]
    matching_funds = TextField(null=True, default=None)
    # JSON: [ {"category": str, "description": str, "amount": float}, ... ]
    line_item_budget = TextField(null=True, default=None)

    class Meta:
        table_name = "financial_information"
