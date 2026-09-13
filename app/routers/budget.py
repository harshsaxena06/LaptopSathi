from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import BudgetOptimizeRequest, BudgetOptimizeResponse, BudgetSuggestion
from app.budget_optimizer import optimizer
from app.utils.serializers import laptop_to_out
from app.auth.dependencies import get_current_user
from app.models.db_models import User

router = APIRouter(prefix="/api/budget-optimizer", tags=["Budget Optimizer"])


@router.post("", response_model=BudgetOptimizeResponse)
def optimize_budget(
    payload: BudgetOptimizeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = optimizer.optimize(db, payload.laptop_id, payload.flexibility_inr)

    def to_suggestion(e):
        return BudgetSuggestion(
            laptop=laptop_to_out(e["laptop"]),
            price_delta_inr=e["price_delta_inr"],
            tradeoff_summary=e["tradeoff_summary"],
        )

    return BudgetOptimizeResponse(
        base_laptop=laptop_to_out(result["base_laptop"]),
        upgrades=[to_suggestion(e) for e in result["upgrades"]],
        downgrades=[to_suggestion(e) for e in result["downgrades"]],
    )
