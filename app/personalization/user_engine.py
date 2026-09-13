"""
Personalization.

Stores per-user preferences (brands, budget, use case, saved laptops) and
interaction history (searches, views, compares, saves) against the
authenticated user's integer id (from the `users` table) — no more
client-supplied string identifiers. Recommendation/search endpoints use
`get_current_user_optional` so personalization only kicks in when the
caller is actually logged in.
"""
from __future__ import annotations

from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.db_models import UserPreference, UserHistory


def get_or_create_preferences(db: Session, user_id: int) -> UserPreference:
    pref = db.query(UserPreference).filter_by(user_id=user_id).first()
    if pref is None:
        pref = UserPreference(user_id=user_id, preferred_brands=[], saved_laptop_ids=[])
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref


def update_preferences(
    db: Session,
    user_id: int,
    preferred_brands: Optional[List[str]] = None,
    budget_min: Optional[float] = None,
    budget_max: Optional[float] = None,
    primary_use_case: Optional[str] = None,
) -> UserPreference:
    pref = get_or_create_preferences(db, user_id)
    if preferred_brands is not None:
        pref.preferred_brands = preferred_brands
    if budget_min is not None:
        pref.budget_min = budget_min
    if budget_max is not None:
        pref.budget_max = budget_max
    if primary_use_case is not None:
        pref.primary_use_case = primary_use_case
    db.commit()
    db.refresh(pref)
    return pref


def save_laptop(db: Session, user_id: int, laptop_id: int) -> UserPreference:
    pref = get_or_create_preferences(db, user_id)
    saved = set(pref.saved_laptop_ids or [])
    saved.add(laptop_id)
    pref.saved_laptop_ids = list(saved)
    db.commit()
    db.refresh(pref)
    log_event(db, user_id, "save", {"laptop_id": laptop_id})
    return pref


def unsave_laptop(db: Session, user_id: int, laptop_id: int) -> UserPreference:
    pref = get_or_create_preferences(db, user_id)
    saved = set(pref.saved_laptop_ids or [])
    saved.discard(laptop_id)
    pref.saved_laptop_ids = list(saved)
    db.commit()
    db.refresh(pref)
    return pref


def log_event(db: Session, user_id: int, event_type: str, payload: dict) -> None:
    """Records a user interaction (search / view / compare / save) for future
    personalization and analytics."""
    entry = UserHistory(user_id=user_id, event_type=event_type, payload=payload)
    db.add(entry)
    db.commit()


def infer_brand_affinity(db: Session, user_id: int, top_n: int = 3) -> List[str]:
    """Very simple recency/frequency based brand affinity from view/save history,
    used to enrich recommendations when the user hasn't explicitly set preferred_brands."""
    from collections import Counter

    events = (
        db.query(UserHistory)
        .filter(UserHistory.user_id == user_id, UserHistory.event_type.in_(["view", "save"]))
        .order_by(UserHistory.created_at.desc())
        .limit(50)
        .all()
    )
    brand_counter = Counter()
    for e in events:
        brand = (e.payload or {}).get("brand")
        if brand:
            brand_counter[brand] += 1
    return [b for b, _ in brand_counter.most_common(top_n)]
