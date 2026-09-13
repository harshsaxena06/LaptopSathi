from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import CompareRequest, CompareResponse
from app.comparison import comparator
from app.utils.exceptions import InvalidRequestError
from app.utils.serializers import laptop_to_out
from app.auth.dependencies import get_current_user
from app.models.db_models import User

router = APIRouter(prefix="/api/compare", tags=["Comparison"])


@router.post("", response_model=CompareResponse)
def compare_laptops(
    payload: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if len(payload.laptop_ids) < 2:
        raise InvalidRequestError("Provide at least 2 laptop_ids to compare")

    result = comparator.compare(db, payload.laptop_ids)

    return CompareResponse(
        laptops=[laptop_to_out(lp) for lp in result["laptops"]],
        winner_by_category=result["winner_by_category"],
        overall_recommendation=result["overall_recommendation"],
    )
