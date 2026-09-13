"""
Price Intelligence.

Maintains and reports on historical price information: current, lowest,
highest, average price, full history, and a simple trend classification
(rising / falling / stable) based on recent movement.
"""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import asc

from app.models.db_models import Laptop, PriceHistory
from app.utils.exceptions import NotFoundError


def get_price_intelligence(db: Session, laptop_id: int) -> dict:
    laptop = db.query(Laptop).filter(Laptop.id == laptop_id).first()
    if laptop is None:
        raise NotFoundError(f"Laptop {laptop_id} not found")

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.laptop_id == laptop_id)
        .order_by(asc(PriceHistory.recorded_at))
        .all()
    )

    if not history:
        # Fall back to the laptop's current listed price as the only data point
        prices = [laptop.price_inr]
        trend = "stable"
        history_points = []
    else:
        prices = [h.price_inr for h in history]
        history_points = [
            {"price_inr": h.price_inr, "recorded_at": h.recorded_at.isoformat(), "source": h.source}
            for h in history
        ]
        if len(prices) >= 2:
            recent_change = prices[-1] - prices[-2]
            if recent_change > prices[-2] * 0.02:
                trend = "rising"
            elif recent_change < -prices[-2] * 0.02:
                trend = "falling"
            else:
                trend = "stable"
        else:
            trend = "stable"

    return {
        "laptop_id": laptop_id,
        "current_price": prices[-1],
        "lowest_price": min(prices),
        "highest_price": max(prices),
        "average_price": round(sum(prices) / len(prices), 2),
        "trend": trend,
        "history": history_points,
    }
