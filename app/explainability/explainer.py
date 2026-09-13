"""
Explainable AI.

Every recommendation must ship with a human-readable explanation: reasons,
pros, cons, a confidence score, and pointers to better alternatives / budget
trade-offs. This module is pure logic (no ML black-box) — it inspects the
same signals the hybrid recommendation engine used and turns them into
natural-language justification, which is what makes the system auditable.
"""
from __future__ import annotations

from typing import List, Dict, Optional

from app.models.db_models import Laptop


USE_CASE_SCORE_FIELD = {
    "programming": "programming_score",
    "ai_ml": "ai_ml_score",
    "gaming": "gaming_score",
    "video_editing": "video_editing_score",
    "business": "business_score",
    "student": "student_score",
}


def _score_of(laptop: Laptop, field: str) -> float:
    return float(getattr(laptop, field, 0.0) or 0.0)


def build_explanation(
    laptop: Laptop,
    use_case: Optional[str],
    budget_max: float,
    score_breakdown: Dict[str, float],
    alternatives: List[Laptop] | None = None,
) -> dict:
    reasons: List[str] = []
    pros: List[str] = []
    cons: List[str] = []

    # --- Budget reasoning
    if laptop.price_inr <= budget_max:
        headroom = budget_max - laptop.price_inr
        reasons.append(f"Fits your budget with ₹{int(headroom):,} to spare" if headroom > 0 else "Fits exactly within your budget")
    else:
        cons.append(f"Exceeds your stated budget by ₹{int(laptop.price_inr - budget_max):,}")

    # --- CPU / use-case reasoning
    if use_case and use_case in USE_CASE_SCORE_FIELD:
        field = USE_CASE_SCORE_FIELD[use_case]
        score = _score_of(laptop, field)
        cpu_name = laptop.cpu_bench.cpu_name if laptop.cpu_bench else "The processor"
        if score >= 70:
            reasons.append(f"{cpu_name} performs strongly for {use_case.replace('_', ' ')} workloads")
        elif score >= 45:
            reasons.append(f"{cpu_name} handles {use_case.replace('_', ' ')} workloads adequately")
        else:
            cons.append(f"Hardware is under-powered for demanding {use_case.replace('_', ' ')} workloads")

    # --- GPU / compatibility reasoning
    if laptop.compatibility and laptop.compatibility.supports_cuda_workloads:
        reasons.append(f"{laptop.gpu_bench.gpu_name if laptop.gpu_bench else 'GPU'} supports CUDA workloads for AI/ML")
        pros.append("CUDA-capable GPU")
    elif use_case == "ai_ml":
        cons.append("No CUDA-capable GPU — training will rely on CPU or cloud")

    # --- RAM reasoning
    if laptop.ram_gb >= 16:
        reasons.append(f"{laptop.ram_gb}GB RAM comfortably satisfies multitasking/AI development needs")
        pros.append(f"{laptop.ram_gb}GB RAM")
    elif laptop.ram_gb < 8:
        cons.append(f"Only {laptop.ram_gb}GB RAM may bottleneck heavier workloads")

    # --- Upgradeability
    if laptop.storage_upgradeable:
        reasons.append("Storage is upgradeable for future expansion")
        pros.append("Upgradeable storage")
    if laptop.ram_upgradeable:
        pros.append("Upgradeable RAM")

    # --- Battery / portability
    if laptop.battery_life_hours and laptop.battery_life_hours >= 8:
        pros.append(f"Long battery life (~{laptop.battery_life_hours:.1f}h)")
    elif laptop.battery_life_hours and laptop.battery_life_hours < 5:
        cons.append("Below-average battery life")

    if laptop.weight_kg and laptop.weight_kg <= 1.5:
        pros.append(f"Lightweight at {laptop.weight_kg}kg")
    elif laptop.weight_kg and laptop.weight_kg >= 2.3:
        cons.append(f"Relatively heavy at {laptop.weight_kg}kg")

    if not pros:
        pros.append("Balanced overall specification for the price")
    if not cons:
        cons.append("No significant drawbacks identified for the stated use case")

    # --- Confidence score: derived from how many strong signals align
    signal_strength = sum(score_breakdown.values()) / max(len(score_breakdown), 1)
    confidence_score = round(min(0.99, max(0.35, signal_strength)), 2)

    # --- Budget trade-offs
    budget_tradeoffs: List[str] = []
    if alternatives:
        for alt in alternatives:
            delta = alt.price_inr - laptop.price_inr
            if delta > 0 and alt.gaming_score > laptop.gaming_score + 10:
                budget_tradeoffs.append(
                    f"Spending ₹{int(delta):,} more gets you {alt.brand.name} {alt.model_name} with notably better graphics performance"
                )
            elif delta < 0:
                budget_tradeoffs.append(
                    f"You could save ₹{int(-delta):,} with {alt.brand.name} {alt.model_name} at a modest performance trade-off"
                )

    better_alt_ids = [a.id for a in alternatives] if alternatives else []

    return {
        "reasons": reasons,
        "pros": pros,
        "cons": cons,
        "confidence_score": confidence_score,
        "better_alternatives": better_alt_ids,
        "budget_tradeoffs": budget_tradeoffs[:3],
    }
