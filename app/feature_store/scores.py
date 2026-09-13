"""
Feature Store.

Computes reusable engineered scores (0-100 scale) for every laptop:
Programming, AI & ML, Gaming, Video Editing, Battery, Portability,
Business, Student, Future-Proof.

These scores are pre-computed once per knowledge-base update and stored on
the `laptops` table so that recommendation, comparison, and analytics
modules can all read them without recomputation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _minmax(series: pd.Series, invert: bool = False) -> pd.Series:
    lo, hi = series.min(), series.max()
    if hi == lo:
        norm = pd.Series(0.5, index=series.index)
    else:
        norm = (series - lo) / (hi - lo)
    return (1 - norm) if invert else norm


def compute_all_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Adds *_score columns (0-100) to the dataframe. Assumes engineering.pipeline
    has already run (needs is_dedicated_gpu, supports_cuda, res columns etc.)."""
    df = df.copy()

    ram_norm = _minmax(df["ram_gb"])
    storage_norm = _minmax(df["storage_gb"])
    weight_norm = _minmax(df["weight_kg"], invert=True)  # lighter = better
    battery_norm = _minmax(df["battery_life_hours"])
    price_norm = _minmax(df["price_inr"], invert=True)  # cheaper = better (for value scores)
    pixels_norm = _minmax(df["total_pixels"])
    refresh_norm = _minmax(df["refresh_rate_hz"])
    dedicated_gpu = df["is_dedicated_gpu"].astype(float)
    cuda = df["supports_cuda"].astype(float)

    # --- Programming Score: CPU + RAM + multitasking headroom, GPU barely matters
    df["programming_score"] = (
        0.45 * ram_norm + 0.35 * storage_norm + 0.20 * battery_norm
    ) * 100

    # --- AI & ML Score: heavily GPU/CUDA + RAM + VRAM-proxy dependent
    df["ai_ml_score"] = (
        0.40 * cuda + 0.30 * dedicated_gpu + 0.30 * ram_norm
    ) * 100

    # --- Gaming Score: dedicated GPU + refresh rate + resolution + cooling proxy (weight as inverse thermal proxy ignored)
    df["gaming_score"] = (
        0.45 * dedicated_gpu + 0.30 * refresh_norm + 0.25 * pixels_norm
    ) * 100

    # --- Video Editing Score: resolution + storage + RAM + dedicated GPU
    df["video_editing_score"] = (
        0.35 * pixels_norm + 0.30 * ram_norm + 0.20 * storage_norm + 0.15 * dedicated_gpu
    ) * 100

    # --- Battery Score: pure battery life, lightly adjusted by weight (portability correlate)
    df["battery_score"] = (0.85 * battery_norm + 0.15 * weight_norm) * 100

    # --- Portability Score: weight + battery, size implicitly via weight
    df["portability_score"] = (0.65 * weight_norm + 0.35 * battery_norm) * 100

    # --- Business Score: portability + battery + reliability (brand-level, applied later) + moderate specs
    df["business_score"] = (
        0.35 * weight_norm + 0.35 * battery_norm + 0.30 * ram_norm
    ) * 100

    # --- Student Score: value for money + portability + adequate (not extreme) specs
    df["student_score"] = (
        0.45 * price_norm + 0.30 * weight_norm + 0.25 * battery_norm
    ) * 100

    # --- Future-Proof Score: RAM headroom + upgradeability + storage + recency
    year_norm = _minmax(df["release_year"].astype(float))
    upgrade_bonus = (df["ram_upgradeable"].astype(float) + df["storage_upgradeable"].astype(float)) / 2
    df["future_proof_score"] = (
        0.30 * ram_norm + 0.25 * storage_norm + 0.25 * upgrade_bonus + 0.20 * year_norm
    ) * 100

    score_cols = [
        "programming_score", "ai_ml_score", "gaming_score", "video_editing_score",
        "battery_score", "portability_score", "business_score", "student_score",
        "future_proof_score",
    ]
    df[score_cols] = df[score_cols].round(2)
    return df
