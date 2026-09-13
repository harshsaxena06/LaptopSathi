from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import SimilarLaptopResponse, SearchResultItem
from app.similar_finder import similar
from app.utils.serializers import laptop_to_out
from app.auth.dependencies import get_current_user
from app.models.db_models import User

router = APIRouter(prefix="/api/similar", tags=["Similar Laptop Finder"])


@router.get("/{laptop_id}", response_model=SimilarLaptopResponse)
def get_similar(
    laptop_id: int,
    top_k: int = Query(default=6, ge=1, le=25),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    pairs = similar.find_similar_laptops(db, laptop_id, top_k=top_k)

    return SimilarLaptopResponse(
        reference_laptop_id=laptop_id,
        similar=[
            SearchResultItem(laptop=laptop_to_out(lp), similarity_score=round(score, 4))
            for lp, score in pairs
        ],
    )
