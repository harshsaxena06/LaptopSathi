"""
Hybrid Recommendation Engine.

Combines multiple independent signals into a single weighted score:
 - Semantic similarity (from the search module, if a free-text query is given)
 - Budget suitability
 - Hardware compatibility (use-case specific feature-store score)
 - Benchmark performance (CPU/GPU raw benchmark scores)
 - Brand preference
 - Future-proof score

Weights are centrally configured in app.config.Settings so they can be tuned
without touching this module's logic.
"""
from __future__ import annotations

from typing import List, Optional, Dict

from sqlalchemy.orm import Session

from app.config import settings
from app.models.db_models import Laptop
from app.search import semantic_search
from app.explainability.explainer import build_explanation
from app.utils.exceptions import DependencyNotReadyError


USE_CASE_SCORE_FIELD = {
    "programming": "programming_score",
    "ai_ml": "ai_ml_score",
    "gaming": "gaming_score",
    "video_editing": "video_editing_score",
    "business": "business_score",
    "student": "student_score",
}


def _budget_fit_score(price: float, budget_min: float, budget_max: float) -> float:
    """1.0 if comfortably inside budget, decays outside the range."""
    if budget_min <= price <= budget_max:
        # reward being well-utilized but not maxed out
        utilization = price / budget_max if budget_max > 0 else 1
        return 1.0 - 0.15 * max(0.0, utilization - 0.85)  # tiny penalty for using every rupee
    if price > budget_max:
        overage = (price - budget_max) / budget_max
        return max(0.0, 1 - overage * 2)
    # below budget_min: usually fine, small penalty for possibly being underpowered
    return 0.85


def _benchmark_score(laptop: Laptop) -> float:
    cpu_score = (laptop.cpu_bench.multi_core_score or 0) if laptop.cpu_bench else 0
    gpu_score = (laptop.gpu_bench.benchmark_score or 0) if laptop.gpu_bench else 0
    # Normalize against rough real-world ceilings so this stays 0-1
    return min(1.0, (cpu_score / 20000) * 0.6 + (gpu_score / 25000) * 0.4)


def _compatibility_score(laptop: Laptop, use_case: Optional[str]) -> float:
    if use_case and use_case in USE_CASE_SCORE_FIELD:
        return float(getattr(laptop, USE_CASE_SCORE_FIELD[use_case], 0.0)) / 100.0
    # No use case given: average of all use-case scores as a general-purpose proxy
    fields = list(USE_CASE_SCORE_FIELD.values())
    return sum(float(getattr(laptop, f, 0.0)) for f in fields) / (100.0 * len(fields))


def _brand_pref_score(laptop: Laptop, preferred_brands: Optional[List[str]]) -> float:
    if not preferred_brands:
        return 0.5  # neutral
    return 1.0 if laptop.brand.name in preferred_brands else 0.2


def recommend(
    db: Session,
    query: Optional[str],
    budget_min: float,
    budget_max: float,
    use_case: Optional[str],
    preferred_brands: Optional[List[str]],
    top_k: int = 5,
) -> List[dict]:
    """Returns a ranked list of {laptop, hybrid_score, score_breakdown, explanation}."""

    candidates: Dict[int, Laptop] = {
        lp.id: lp
        for lp in db.query(Laptop)
        .filter(Laptop.is_active.is_(True))
        .all()
    }

    semantic_scores: Dict[int, float] = {}
    if query:
        try:
            for laptop_id, score in semantic_search.search(query, top_k=50):
                semantic_scores[laptop_id] = score
        except DependencyNotReadyError:
            # Index not built yet — degrade gracefully to non-semantic ranking
            semantic_scores = {}

    scored: List[tuple[Laptop, float, dict]] = []
    for laptop_id, laptop in candidates.items():
        sem = semantic_scores.get(laptop_id, 0.5 if not query else 0.0)
        budget = _budget_fit_score(laptop.price_inr, budget_min, budget_max)
        compat = _compatibility_score(laptop, use_case)
        bench = _benchmark_score(laptop)
        brand = _brand_pref_score(laptop, preferred_brands)
        future = float(laptop.future_proof_score or 0.0) / 100.0

        breakdown = {
            "semantic": round(sem, 3),
            "budget_fit": round(budget, 3),
            "compatibility": round(compat, 3),
            "benchmark": round(bench, 3),
            "brand_preference": round(brand, 3),
            "future_proof": round(future, 3),
        }

        hybrid = (
            settings.WEIGHT_SEMANTIC * sem
            + settings.WEIGHT_BUDGET * budget
            + settings.WEIGHT_COMPATIBILITY * compat
            + settings.WEIGHT_BENCHMARK * bench
            + settings.WEIGHT_BRAND_PREF * brand
            + settings.WEIGHT_FUTURE_PROOF * future
        )
        scored.append((laptop, hybrid, breakdown))

    scored.sort(key=lambda t: t[1], reverse=True)
    top = scored[:top_k]
    remaining_pool = [lp for lp, _, _ in scored[top_k:top_k + 10]]

    results = []
    for laptop, hybrid_score, breakdown in top:
        alt_candidates = [
            a for a in remaining_pool
            if abs(a.price_inr - laptop.price_inr) <= 0.25 * laptop.price_inr
        ][:2]
        explanation = build_explanation(laptop, use_case, budget_max, breakdown, alt_candidates)
        results.append({
            "laptop": laptop,
            "hybrid_score": round(hybrid_score, 4),
            "score_breakdown": breakdown,
            "explanation": explanation,
        })
    return results
