"""
Data Ingestion Pipeline.

Responsibilities:
 - Load raw data from CSV/JSON (Kaggle exports, manufacturer sheets, manual updates)
 - Schema validation
 - Duplicate detection
 - Data merging (new + existing knowledge base)
 - Version tracking (delegates to app.versioning.kb_version)
 - Basic data quality checks / reporting
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List

import pandas as pd
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

logger = logging.getLogger("laptopsathi.ingestion")

REQUIRED_COLUMNS = [
    "model_name", "brand", "cpu_name", "gpu_name", "ram_gb",
    "storage_gb", "storage_type", "display_size_inch", "display_resolution",
    "refresh_rate_hz", "battery_whr", "battery_life_hours", "weight_kg",
    "price_inr", "release_year",
]


class RawLaptopRecord(BaseModel):
    """Schema-validation model for a single incoming laptop record."""
    model_config = ConfigDict(protected_namespaces=())  # "model_name" is our field, not pydantic's

    model_name: str
    brand: str
    cpu_name: str
    gpu_name: str
    ram_gb: int
    storage_gb: int
    storage_type: str
    display_size_inch: float
    display_resolution: str
    refresh_rate_hz: int = 60
    battery_whr: float | None = None
    battery_life_hours: float | None = None
    weight_kg: float | None = None
    price_inr: float
    release_year: int | None = None

    @field_validator("ram_gb", "storage_gb")
    @classmethod
    def must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("must be a positive integer")
        return v

    @field_validator("price_inr")
    @classmethod
    def price_reasonable(cls, v):
        if v <= 0 or v > 1_000_000:
            raise ValueError("price out of expected range for a consumer laptop")
        return v


class IngestionReport(BaseModel):
    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int
    errors: List[str]


def _load_raw_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        # utf-8-sig instead of utf-8: transparently strips a UTF-8 BOM if present
        # (a no-op if there isn't one). Without this, a BOM-prefixed file — common
        # when a CSV has been touched by Excel/Notepad on Windows, or written by
        # some locale/tooling configurations — silently renames only the FIRST
        # column to "\ufeffmodel_name", which then fails the exact-match schema
        # check below. .str.strip() on the column names guards the same class of
        # issue for accidental leading/trailing whitespace.
        df = pd.read_csv(path, encoding="utf-8-sig")
        df.columns = df.columns.str.strip()
        return df
    elif path.suffix.lower() == ".json":
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df.columns = df.columns.str.strip()
        return df
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def _check_schema(df: pd.DataFrame) -> list[str]:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        detected = ", ".join(df.columns.astype(str)) or "(no columns parsed at all)"
        return [f"Missing required column: {c}" for c in missing] + [
            f"Columns actually detected in the file ({len(df.columns)}): {detected}",
        ]
    return []


def _detect_duplicates(df: pd.DataFrame) -> pd.Series:
    """A duplicate = same brand + model_name + ram + storage (common re-listing pattern)."""
    key_cols = ["brand", "model_name", "ram_gb", "storage_gb"]
    return df.duplicated(subset=key_cols, keep="first")


def ingest_file(path: str | Path) -> tuple[pd.DataFrame, IngestionReport]:
    """
    Main entrypoint. Loads a raw CSV/JSON file, validates schema + row-level data,
    flags duplicates, and returns (clean_dataframe, report).
    """
    path = Path(path)
    df = _load_raw_file(path)

    errors = _check_schema(df)
    if errors:
        logger.error("Schema validation failed: %s", errors)
        return pd.DataFrame(), IngestionReport(
            total_rows=len(df), valid_rows=0, invalid_rows=len(df),
            duplicate_rows=0, errors=errors,
        )

    dup_mask = _detect_duplicates(df)
    duplicate_rows = int(dup_mask.sum())
    df = df[~dup_mask].copy()

    valid_indices = []
    row_errors: list[str] = []
    for idx, row in df.iterrows():
        try:
            RawLaptopRecord(**row.to_dict())  # validation only; raises on bad data
            valid_indices.append(idx)
        except ValidationError as e:
            row_errors.append(f"Row {idx} ({row.get('model_name', '?')}): {e.errors()[0]['msg']}")

    # Keep ALL original columns (not just the slim validation schema's fields) for
    # rows that passed validation, so downstream pipelines (e.g. CPU/GPU benchmark
    # extraction) still have access to source-specific extra columns.
    clean_df = df.loc[valid_indices].reset_index(drop=True)
    report = IngestionReport(
        total_rows=len(df) + duplicate_rows,
        valid_rows=len(clean_df),
        invalid_rows=len(row_errors),
        duplicate_rows=duplicate_rows,
        errors=row_errors,
    )
    logger.info("Ingestion complete: %s", report.model_dump())
    return clean_df, report


def merge_with_existing(new_df: pd.DataFrame, existing_path: Path) -> pd.DataFrame:
    """Merge freshly ingested records with the existing processed knowledge base, deduping."""
    if not existing_path.exists():
        return new_df

    existing_df = pd.read_csv(existing_path)
    combined = pd.concat([existing_df, new_df], ignore_index=True)
    key_cols = ["brand", "model_name", "ram_gb", "storage_gb"]
    combined = combined.drop_duplicates(subset=key_cols, keep="last")
    return combined
