"""
Analytics Dashboard (backend logic).

Aggregates dataset-level statistics: brand/CPU/GPU/price distributions,
overall dataset stats, and current knowledge-base version. The frontend
Admin Analytics Dashboard renders this data — no business logic on the
client side.
"""
from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from app.models.db_models import Laptop, KBVersion


PRICE_BUCKETS = [
    (0, 40000, "Under ₹40k"),
    (40000, 70000, "₹40k–70k"),
    (70000, 100000, "₹70k–100k"),
    (100000, 150000, "₹100k–150k"),
    (150000, 250000, "₹150k–250k"),
    (250000, float("inf"), "Above ₹250k"),
]


def _bucket_label(price: float) -> str:
    for lo, hi, label in PRICE_BUCKETS:
        if lo <= price < hi:
            return label
    return "Unknown"


def get_analytics(db: Session) -> dict:
    laptops = db.query(Laptop).filter(Laptop.is_active.is_(True)).all()

    brand_dist = Counter(lp.brand.name for lp in laptops)
    cpu_dist = Counter(lp.cpu_bench.cpu_name if lp.cpu_bench else "Unknown" for lp in laptops)
    gpu_dist = Counter(lp.gpu_bench.gpu_name if lp.gpu_bench else "Unknown" for lp in laptops)
    price_dist = Counter(_bucket_label(lp.price_inr) for lp in laptops)

    avg_price = round(sum(lp.price_inr for lp in laptops) / len(laptops), 2) if laptops else 0.0

    latest_version = (
        db.query(KBVersion).order_by(KBVersion.created_at.desc()).first()
    )

    return {
        "total_laptops": len(laptops),
        "brand_distribution": dict(brand_dist),
        "cpu_distribution": dict(cpu_dist.most_common(15)),
        "gpu_distribution": dict(gpu_dist.most_common(15)),
        "price_distribution": dict(price_dist),
        "avg_price": avg_price,
        "kb_version": latest_version.version_tag if latest_version else None,
    }
