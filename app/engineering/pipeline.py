"""
Data Engineering Pipeline.

Transforms a validated raw dataframe (from the ingestion pipeline) into a
model-ready dataset: cleaning, missing-value handling, CPU/GPU/storage/display
normalization, and derived-feature generation (compatibility flags, a text
description used for embeddings, etc).

This module does NOT compute the feature-store "scores" (Programming Score,
Gaming Score, ...) — that lives in app/feature_store/scores.py, which is run
after this pipeline on the cleaned dataframe.
"""
from __future__ import annotations

import re
import logging
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger("laptopsathi.engineering")


# ---------- Normalization helpers ----------

def normalize_brand(brand: str) -> str:
    return brand.strip().title().replace("Hp", "HP").replace("Msi", "MSI").replace("Lg", "LG")


def normalize_storage_type(storage_type: str) -> str:
    s = storage_type.strip().upper()
    if "NVME" in s or "SSD" in s:
        return "SSD"
    if "HDD" in s:
        return "HDD"
    if "HYBRID" in s or "EMMC" in s:
        return "Hybrid"
    return "SSD"  # sane default for modern laptops


def normalize_cpu_name(cpu_name: str) -> str:
    """Collapse marketing variants to a canonical CPU key, e.g.
    'Intel(R) Core(TM) i7-13700H' -> 'Intel Core i7-13700H'."""
    s = cpu_name.replace("(R)", "").replace("(TM)", "").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_gpu_name(gpu_name: str) -> str:
    s = gpu_name.strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace("Nvidia", "NVIDIA").replace("GEFORCE", "GeForce")
    return s


def is_dedicated_gpu(gpu_name: str) -> bool:
    integrated_markers = ["integrated", "iris", "vega", "radeon graphics", "uhd graphics"]
    return not any(m in gpu_name.lower() for m in integrated_markers)


def supports_cuda(gpu_name: str) -> bool:
    return "nvidia" in gpu_name.lower() or "rtx" in gpu_name.lower() or "gtx" in gpu_name.lower()


def parse_resolution(res: str) -> tuple[int, int]:
    try:
        w, h = res.lower().replace(" ", "").split("x")
        return int(w), int(h)
    except Exception:
        return 1920, 1080  # default FHD


# ---------- Missing value handling ----------

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["battery_whr"] = df["battery_whr"].fillna(df["battery_whr"].median())
    df["battery_life_hours"] = df["battery_life_hours"].fillna(df["battery_life_hours"].median())
    df["weight_kg"] = df["weight_kg"].fillna(df["weight_kg"].median())
    df["release_year"] = df["release_year"].fillna(int(df["release_year"].mode().iloc[0]) if not df["release_year"].mode().empty else 2023)
    df["refresh_rate_hz"] = df["refresh_rate_hz"].fillna(60)
    return df


# ---------- Main pipeline ----------

def clean_and_transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full data-engineering pass. Input: validated raw dataframe.
    Output: cleaned, normalized dataframe with derived columns ready for the
    feature store and for DB insertion.
    """
    df = handle_missing_values(df)

    df["brand"] = df["brand"].apply(normalize_brand)
    df["storage_type"] = df["storage_type"].apply(normalize_storage_type)
    df["cpu_name"] = df["cpu_name"].apply(normalize_cpu_name)
    df["gpu_name"] = df["gpu_name"].apply(normalize_gpu_name)

    df["is_dedicated_gpu"] = df["gpu_name"].apply(is_dedicated_gpu)
    df["supports_cuda"] = df["gpu_name"].apply(supports_cuda)

    res_parsed = df["display_resolution"].apply(parse_resolution)
    df["res_width"] = res_parsed.apply(lambda t: t[0])
    df["res_height"] = res_parsed.apply(lambda t: t[1])
    df["total_pixels"] = df["res_width"] * df["res_height"]

    # Upgradeability heuristics (derived, since raw data rarely states this explicitly)
    df["ram_upgradeable"] = df["ram_gb"] <= 16
    df["storage_upgradeable"] = df["storage_type"] != "Hybrid"

    # Natural-language description used to build sentence embeddings for semantic search
    df["description_text"] = df.apply(_build_description, axis=1)

    # Basic outlier clipping so a single bad price doesn't skew downstream scoring
    price_cap = df["price_inr"].quantile(0.995)
    df["price_inr"] = df["price_inr"].clip(upper=price_cap)

    logger.info("Engineering pipeline transformed %d rows", len(df))
    return df


def _build_description(row) -> str:
    dedicated = "dedicated" if row.get("is_dedicated_gpu") else "integrated"
    return (
        f"{row['brand']} {row['model_name']} featuring {row['cpu_name']} processor, "
        f"{row['gpu_name']} ({dedicated} graphics), {row['ram_gb']}GB RAM, "
        f"{row['storage_gb']}GB {row['storage_type']} storage, "
        f"{row['display_size_inch']}-inch {row['display_resolution']} display "
        f"at {row.get('refresh_rate_hz', 60)}Hz, "
        f"priced around {int(row['price_inr'])} INR, released in {int(row.get('release_year', 2023))}."
    )
