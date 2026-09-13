from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import PriceIntelligenceResponse
from app.price_intelligence import price_engine
from app.auth.dependencies import get_current_user
from app.models.db_models import User

router = APIRouter(prefix="/api/price-intelligence", tags=["Price Intelligence"])


@router.get("/{laptop_id}", response_model=PriceIntelligenceResponse)
def get_price_intel(
    laptop_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = price_engine.get_price_intelligence(db, laptop_id)
    return PriceIntelligenceResponse(**result)
