from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.schemas import UserPreferenceUpdate, UserPreferenceOut, SaveLaptopRequest
from app.personalization import user_engine
from app.auth.dependencies import get_current_user
from app.models.db_models import User

router = APIRouter(prefix="/api/users", tags=["Users / Personalization"])


@router.get("/me/preferences", response_model=UserPreferenceOut)
def get_my_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_engine.get_or_create_preferences(db, current_user.id)


@router.put("/me/preferences", response_model=UserPreferenceOut)
def update_my_preferences(
    payload: UserPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_engine.update_preferences(db, current_user.id, **payload.model_dump(exclude_unset=True))


@router.post("/me/save-laptop", response_model=UserPreferenceOut)
def save_laptop(
    payload: SaveLaptopRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_engine.save_laptop(db, current_user.id, payload.laptop_id)


@router.post("/me/unsave-laptop", response_model=UserPreferenceOut)
def unsave_laptop(
    payload: SaveLaptopRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_engine.unsave_laptop(db, current_user.id, payload.laptop_id)
