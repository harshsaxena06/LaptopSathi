from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Laptop, User
from app.schemas.schemas import LaptopOut
from app.utils.exceptions import NotFoundError
from app.utils.serializers import laptop_to_out
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/laptops", tags=["Laptops"])


@router.get("", response_model=list[LaptopOut])
def list_laptops(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    q = db.query(Laptop).filter(Laptop.is_active.is_(True))
    if brand:
        q = q.filter(Laptop.brand.has(name=brand))
    if min_price is not None:
        q = q.filter(Laptop.price_inr >= min_price)
    if max_price is not None:
        q = q.filter(Laptop.price_inr <= max_price)
    laptops = q.offset(offset).limit(limit).all()
    return [laptop_to_out(lp) for lp in laptops]


@router.get("/{laptop_id}", response_model=LaptopOut)
def get_laptop(laptop_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lp = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if lp is None:
        raise NotFoundError(f"Laptop {laptop_id} not found")
    return laptop_to_out(lp)
