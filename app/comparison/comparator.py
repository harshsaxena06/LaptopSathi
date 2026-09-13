"""
Laptop Comparison.

Compares 2+ laptops across specs, benchmarks, feature-store scores, AI
compatibility, battery, display, weight and price, and picks a per-category
"winner" plus an overall recommendation string.
"""
from __future__ import annotations

from typing import List, Dict

from sqlalchemy.orm import Session

from app.models.db_models import Laptop
from app.utils.exceptions import InvalidRequestError


CATEGORY_EXTRACTORS = {
    "Best for Programming": lambda lp: lp.programming_score or 0,
    "Best for AI/ML": lambda lp: lp.ai_ml_score or 0,
    "Best for Gaming": lambda lp: lp.gaming_score or 0,
    "Best for Video Editing": lambda lp: lp.video_editing_score or 0,
    "Best Battery Life": lambda lp: lp.battery_life_hours or 0,
    "Most Portable": lambda lp: -1 * (lp.weight_kg or 999),  # lighter wins
    "Best Value": lambda lp: (lp.student_score or 0),
    "Best Future-Proofing": lambda lp: lp.future_proof_score or 0,
}


def compare(db: Session, laptop_ids: List[int]) -> dict:
    laptops = db.query(Laptop).filter(Laptop.id.in_(laptop_ids)).all()
    if len(laptops) < 2:
        raise InvalidRequestError("At least 2 valid laptops are required for comparison")

    # preserve requested order
    order = {lid: i for i, lid in enumerate(laptop_ids)}
    laptops.sort(key=lambda lp: order.get(lp.id, 999))

    winner_by_category: Dict[str, str] = {}
    for category, extractor in CATEGORY_EXTRACTORS.items():
        best = max(laptops, key=extractor)
        winner_by_category[category] = f"{best.brand.name} {best.model_name}"

    # Overall recommendation: whichever laptop wins the most categories,
    # tie-broken by average of all feature-store scores.
    win_counts: Dict[int, int] = {lp.id: 0 for lp in laptops}
    for category, extractor in CATEGORY_EXTRACTORS.items():
        best = max(laptops, key=extractor)
        win_counts[best.id] += 1

    def avg_score(lp: Laptop) -> float:
        fields = [
            lp.programming_score, lp.ai_ml_score, lp.gaming_score,
            lp.video_editing_score, lp.battery_score, lp.portability_score,
            lp.business_score, lp.student_score, lp.future_proof_score,
        ]
        return sum(f or 0 for f in fields) / len(fields)

    overall_winner = max(laptops, key=lambda lp: (win_counts[lp.id], avg_score(lp)))
    overall_recommendation = (
        f"{overall_winner.brand.name} {overall_winner.model_name} offers the strongest "
        f"all-round balance, winning {win_counts[overall_winner.id]} of {len(CATEGORY_EXTRACTORS)} "
        f"comparison categories among the laptops compared."
    )

    return {
        "laptops": laptops,
        "winner_by_category": winner_by_category,
        "overall_recommendation": overall_recommendation,
    }
