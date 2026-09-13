"""
Basic tests for the data engineering + feature store logic (pure pandas/numpy,
no DB/FastAPI/ML dependencies needed — safe to run in any environment with
just pandas/numpy/scikit-learn installed).

Run:
    python -m pytest tests/test_basic.py -v
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from app.engineering.pipeline import (
    clean_and_transform, normalize_storage_type, is_dedicated_gpu, supports_cuda, parse_resolution,
)
from app.feature_store.scores import compute_all_scores


def _sample_df():
    return pd.DataFrame([
        {
            "model_name": "TestBook Pro", "brand": "dell", "cpu_name": "Intel(R) Core(TM) i7-13700H",
            "gpu_name": "NVIDIA GeForce RTX 4060", "ram_gb": 16, "storage_gb": 512,
            "storage_type": "NVMe SSD", "display_size_inch": 15.6, "display_resolution": "1920x1080",
            "refresh_rate_hz": 144, "battery_whr": 80, "battery_life_hours": 7.5, "weight_kg": 1.9,
            "price_inr": 95000, "release_year": 2024,
        },
        {
            "model_name": "TestBook Air", "brand": "asus", "cpu_name": "AMD Ryzen 5 7530U",
            "gpu_name": "AMD Radeon Graphics (Integrated)", "ram_gb": 8, "storage_gb": 256,
            "storage_type": "SSD", "display_size_inch": 14.0, "display_resolution": "1920x1080",
            "refresh_rate_hz": 60, "battery_whr": 55, "battery_life_hours": 10.5, "weight_kg": 1.3,
            "price_inr": 45000, "release_year": 2023,
        },
    ])


def test_storage_normalization():
    assert normalize_storage_type("NVMe SSD") == "SSD"
    assert normalize_storage_type("hdd") == "HDD"
    assert normalize_storage_type("eMMC") == "Hybrid"


def test_gpu_helpers():
    assert is_dedicated_gpu("NVIDIA GeForce RTX 4060") is True
    assert is_dedicated_gpu("Intel Iris Xe Graphics") is False
    assert supports_cuda("NVIDIA GeForce RTX 4060") is True
    assert supports_cuda("AMD Radeon Graphics (Integrated)") is False


def test_resolution_parsing():
    assert parse_resolution("1920x1080") == (1920, 1080)
    assert parse_resolution("garbage") == (1920, 1080)  # safe default


def test_engineering_pipeline_adds_expected_columns():
    df = clean_and_transform(_sample_df())
    for col in ["is_dedicated_gpu", "supports_cuda", "total_pixels", "description_text"]:
        assert col in df.columns
    assert df.loc[0, "is_dedicated_gpu"] == True
    assert df.loc[1, "is_dedicated_gpu"] == False


def test_feature_scores_are_bounded():
    df = compute_all_scores(clean_and_transform(_sample_df()))
    score_cols = [
        "programming_score", "ai_ml_score", "gaming_score", "video_editing_score",
        "battery_score", "portability_score", "business_score", "student_score",
        "future_proof_score",
    ]
    for col in score_cols:
        assert (df[col] >= 0).all() and (df[col] <= 100).all(), f"{col} out of [0,100] bounds"

    # The gaming rig should clearly outscore the ultrabook on gaming, and vice versa on portability
    assert df.loc[0, "gaming_score"] > df.loc[1, "gaming_score"]
    assert df.loc[1, "portability_score"] > df.loc[0, "portability_score"]


if __name__ == "__main__":
    test_storage_normalization()
    test_gpu_helpers()
    test_resolution_parsing()
    test_engineering_pipeline_adds_expected_columns()
    test_feature_scores_are_bounded()
    print("All tests passed.")
