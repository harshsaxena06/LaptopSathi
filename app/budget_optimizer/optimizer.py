"""
Budget Optimizer.

Given a base laptop the user is considering, suggests nearby upgrade and
downgrade options from the knowledge base with a plain-language trade-off
summary, e.g.:
  "Spending ₹4,000 more gives you RTX 4060 instead of integrated graphics."
  "You can save ₹7,000 with only a small performance trade-off."
"""
from __future__ import annotations

from typing import List

from sqlalchemy.orm import Session

from app.models.db_models import Laptop
from app.utils.exceptions import NotFoundError


SCORE_FIELDS = [
    "programming_score", "ai_ml_score", "gaming_score", "video_editing_score",
    "battery_score", "portability_score",
]


def _overall_score(laptop: Laptop) -> float:
    return sum(getattr(laptop, f, 0.0) or 0.0 for f in SCORE_FIELDS) / len(SCORE_FIELDS)


def _tradeoff_summary(base: Laptop, candidate: Laptop) -> str:
    delta_price = candidate.price_inr - base.price_inr
    delta_score = _overall_score(candidate) - _overall_score(base)

    notes = []
    if candidate.gpu_bench and base.gpu_bench and candidate.gpu_bench.gpu_name != base.gpu_bench.gpu_name:
        notes.append(f"{candidate.gpu_bench.gpu_name} instead of {base.gpu_bench.gpu_name}")
    if candidate.ram_gb != base.ram_gb:
        notes.append(f"{candidate.ram_gb}GB RAM instead of {base.ram_gb}GB")
    if candidate.storage_gb != base.storage_gb:
        notes.append(f"{candidate.storage_gb}GB storage instead of {base.storage_gb}GB")

    detail = f" — {', '.join(notes)}" if notes else ""

    if delta_price > 0:
        verdict = "notable performance gain" if delta_score > 8 else "modest improvement"
        return f"Spending ₹{int(delta_price):,} more gives you a {verdict}{detail}."
    else:
        verdict = "with only a small performance trade-off" if delta_score > -8 else "with a noticeable performance drop"
        return f"You can save ₹{int(-delta_price):,} {verdict}{detail}."


def optimize(db: Session, laptop_id: int, flexibility_inr: float = 10000) -> dict:
    base = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if base is None:
        raise NotFoundError(f"Laptop {laptop_id} not found")

    low = base.price_inr - flexibility_inr
    high = base.price_inr + flexibility_inr

    nearby = (
        db.query(Laptop)
        .filter(Laptop.is_active.is_(True))
        .filter(Laptop.id != base.id)
        .filter(Laptop.price_inr.between(low, high))
        .all()
    )

    upgrades: List[dict] = []
    downgrades: List[dict] = []

    for candidate in nearby:
        delta = candidate.price_inr - base.price_inr
        entry = {
            "laptop": candidate,
            "price_delta_inr": round(delta, 2),
            "tradeoff_summary": _tradeoff_summary(base, candidate),
        }
        if delta >= 0 and _overall_score(candidate) > _overall_score(base):
            upgrades.append(entry)
        elif delta < 0:
            downgrades.append(entry)

    upgrades.sort(key=lambda e: _overall_score(e["laptop"]), reverse=True)
    # Biggest savings first (price_delta_inr is negative for downgrades)
    downgrades.sort(key=lambda e: e["price_delta_inr"])

    return {
        "base_laptop": base,
        "upgrades": upgrades[:5],
        "downgrades": downgrades[:5],
    }
