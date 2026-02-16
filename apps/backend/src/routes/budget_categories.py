"""Reference data: budget categories for line item validation."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from database.models import BudgetCategory
from utils.responses import success_response

router = APIRouter(prefix="/budget-categories", tags=["reference"])


@router.get("")
async def list_budget_categories():
    """List budget categories for financial line item dropdown."""
    options = BudgetCategory.select().order_by(BudgetCategory.label)
    data = [{"id": str(o.id), "code": o.code, "label": o.label} for o in options]
    return JSONResponse(content=success_response(data=data))
