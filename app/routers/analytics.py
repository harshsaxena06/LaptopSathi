from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import AnalyticsResponse
from app.analytics import dashboard
from app.auth.dependencies import require_role
from app.models.db_models import User

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return dashboard.get_analytics(db)
