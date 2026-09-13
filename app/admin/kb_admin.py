"""
Knowledge Base admin operations, shared by:
 - scripts/run_ingestion.py (CLI)
 - app.routers.admin (POST /api/admin/knowledge-base/upload, admin-only)

This is the same upsert logic previously inline in scripts/run_ingestion.py,
extracted so both entry points share one implementation.
"""
from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.ingestion.pipeline import ingest_file, IngestionReport
from app.engineering.pipeline import clean_and_transform
from app.feature_store.scores import compute_all_scores
from app.versioning import kb_version
from app.models.db_models import (
    Brand, CPUBenchmark, GPUBenchmark, Laptop, PriceHistory, CompatibilityScore, KBVersion,
)
from app.utils.exceptions import InvalidRequestError
from app.search import semantic_search

logger = logging.getLogger("laptopsathi.admin.kb")

# Columns compute_all_scores() reads from the dataframe it's given.
_SCORE_INPUT_COLUMNS = [
    "ram_gb", "storage_gb", "weight_kg", "battery_life_hours", "price_inr",
    "total_pixels", "refresh_rate_hz", "is_dedicated_gpu", "supports_cuda",
    "ram_upgradeable", "storage_upgradeable", "release_year",
]


def _existing_catalog_frame(db: Session, exclude_keys: set[tuple]) -> pd.DataFrame:
    """Reconstructs the *_score input columns for every currently active
    laptop NOT being touched by this ingestion run, so an incremental
    upload (a handful of rows) gets normalized against the whole catalog
    instead of just itself — a min-max score computed over 2 rows is
    meaningless (see feature_store/scores.py::_minmax).
    """
    rows = []
    for lp in db.query(Laptop).filter(Laptop.is_active.is_(True)).all():
        key = (lp.brand.name, lp.model_name, lp.ram_gb, lp.storage_gb)
        if key in exclude_keys:
            continue
        width, height = 1920, 1080
        if lp.display_resolution:
            try:
                w, h = lp.display_resolution.lower().replace(" ", "").split("x")
                width, height = int(w), int(h)
            except Exception:
                pass
        rows.append({
            "ram_gb": lp.ram_gb,
            "storage_gb": lp.storage_gb,
            "weight_kg": lp.weight_kg,
            "battery_life_hours": lp.battery_life_hours,
            "price_inr": lp.price_inr,
            "total_pixels": width * height,
            "refresh_rate_hz": lp.refresh_rate_hz,
            "is_dedicated_gpu": bool(lp.gpu_bench.is_dedicated) if lp.gpu_bench else False,
            "supports_cuda": bool(lp.gpu_bench.supports_cuda) if lp.gpu_bench else False,
            "ram_upgradeable": lp.ram_upgradeable,
            "storage_upgradeable": lp.storage_upgradeable,
            "release_year": lp.release_year,
        })
    return pd.DataFrame(rows, columns=_SCORE_INPUT_COLUMNS)


def _get_or_create_brand(db: Session, name: str) -> Brand:
    brand = db.query(Brand).filter_by(name=name).first()
    if brand is None:
        brand = Brand(name=name)
        db.add(brand)
        db.flush()
    return brand


def _get_or_create_cpu(db: Session, row) -> CPUBenchmark:
    cpu = db.query(CPUBenchmark).filter_by(cpu_name=row["cpu_name"]).first()
    if cpu is None:
        cpu = CPUBenchmark(
            cpu_name=row["cpu_name"],
            cores=row.get("cpu_cores"),
            threads=row.get("cpu_threads"),
            base_clock_ghz=row.get("cpu_base_clock_ghz"),
            boost_clock_ghz=row.get("cpu_boost_clock_ghz"),
            single_core_score=row.get("cpu_single_core_score"),
            multi_core_score=row.get("cpu_multi_core_score"),
            tdp_watts=row.get("cpu_tdp_watts"),
        )
        db.add(cpu)
        db.flush()
    return cpu


def _get_or_create_gpu(db: Session, row) -> GPUBenchmark:
    gpu = db.query(GPUBenchmark).filter_by(gpu_name=row["gpu_name"]).first()
    if gpu is None:
        gpu = GPUBenchmark(
            gpu_name=row["gpu_name"],
            vram_gb=row.get("gpu_vram_gb"),
            is_dedicated=bool(row.get("gpu_is_dedicated", False)),
            supports_cuda=bool(row.get("gpu_supports_cuda", False)),
            benchmark_score=row.get("gpu_benchmark_score"),
        )
        db.add(gpu)
        db.flush()
    return gpu


def _upsert_laptop(db: Session, row, version_tag: str) -> Laptop:
    brand = _get_or_create_brand(db, row["brand"])
    cpu = _get_or_create_cpu(db, row)
    gpu = _get_or_create_gpu(db, row)

    laptop = (
        db.query(Laptop)
        .filter_by(brand_id=brand.id, model_name=row["model_name"], ram_gb=int(row["ram_gb"]), storage_gb=int(row["storage_gb"]))
        .first()
    )
    if laptop is None:
        laptop = Laptop(brand_id=brand.id, model_name=row["model_name"], ram_gb=int(row["ram_gb"]), storage_gb=int(row["storage_gb"]))
        db.add(laptop)

    laptop.cpu_bench_id = cpu.id
    laptop.gpu_bench_id = gpu.id
    laptop.storage_type = row["storage_type"]
    laptop.ram_upgradeable = bool(row["ram_upgradeable"])
    laptop.storage_upgradeable = bool(row["storage_upgradeable"])
    laptop.display_size_inch = row["display_size_inch"]
    laptop.display_resolution = row["display_resolution"]
    laptop.refresh_rate_hz = int(row.get("refresh_rate_hz", 60))
    laptop.battery_whr = row.get("battery_whr")
    laptop.battery_life_hours = row.get("battery_life_hours")
    laptop.weight_kg = row.get("weight_kg")
    laptop.price_inr = float(row["price_inr"])
    laptop.release_year = int(row.get("release_year", 2023))

    laptop.programming_score = row["programming_score"]
    laptop.ai_ml_score = row["ai_ml_score"]
    laptop.gaming_score = row["gaming_score"]
    laptop.video_editing_score = row["video_editing_score"]
    laptop.battery_score = row["battery_score"]
    laptop.portability_score = row["portability_score"]
    laptop.business_score = row["business_score"]
    laptop.student_score = row["student_score"]
    laptop.future_proof_score = row["future_proof_score"]

    laptop.description_text = row["description_text"]
    laptop.is_active = True
    laptop.kb_version = version_tag

    db.flush()

    latest = (
        db.query(PriceHistory)
        .filter_by(laptop_id=laptop.id)
        .order_by(PriceHistory.recorded_at.desc())
        .first()
    )
    if latest is None or abs(latest.price_inr - laptop.price_inr) > 0.01:
        db.add(PriceHistory(laptop_id=laptop.id, price_inr=laptop.price_inr, source="knowledge_base"))

    compat = db.query(CompatibilityScore).filter_by(laptop_id=laptop.id).first()
    if compat is None:
        compat = CompatibilityScore(laptop_id=laptop.id)
        db.add(compat)
    compat.supports_cuda_workloads = bool(row.get("gpu_supports_cuda", False))
    compat.supports_android_dev = True
    compat.supports_ios_dev = row["brand"] == "Apple"
    compat.supports_heavy_multitasking = row["ram_gb"] >= 16
    compat.supports_4k_editing = row["total_pixels"] >= 3840 * 2160 * 0.9
    compat.thermal_headroom_score = min(1.0, (row.get("cpu_tdp_watts", 15) or 15) / 45)

    db.flush()
    return laptop


def run_ingestion_pipeline(db: Session, file_path: str | Path, notes: str = "") -> dict:
    """Runs ingestion -> engineering -> feature store -> DB upsert -> versioning
    for a single raw CSV/JSON file. Returns a summary dict for the API/CLI to report."""
    clean_df, report = ingest_file(file_path)

    if clean_df.empty:
        raise InvalidRequestError(
            f"No valid rows to ingest ({report.invalid_rows} invalid, {report.duplicate_rows} duplicates).",
            details=report.errors[:20],
        )

    engineered_df = clean_and_transform(clean_df)

    exclude_keys = {
        (row["brand"], row["model_name"], int(row["ram_gb"]), int(row["storage_gb"]))
        for _, row in engineered_df.iterrows()
    }
    baseline_df = _existing_catalog_frame(db, exclude_keys)
    if not baseline_df.empty:
        # Score incoming rows together with the existing catalog so min-max
        # normalization spans the whole population (matters most for small
        # incremental uploads), then keep only the newly-ingested rows —
        # existing laptops' stored scores are untouched here.
        combined = pd.concat(
            [baseline_df, engineered_df[_SCORE_INPUT_COLUMNS]], ignore_index=True,
        )
        combined_scored = compute_all_scores(combined)
        new_scores = combined_scored.tail(len(engineered_df)).reset_index(drop=True)
        score_cols = [c for c in new_scores.columns if c.endswith("_score")]
        engineered_df = engineered_df.reset_index(drop=True)
        for col in score_cols:
            engineered_df[col] = new_scores[col].values
        scored_df = engineered_df
    else:
        scored_df = compute_all_scores(engineered_df)

    version_tag = kb_version.next_version_tag(db)
    for _, row in scored_df.iterrows():
        _upsert_laptop(db, row, version_tag)
    db.commit()

    version = kb_version.create_version(db, scored_df, source_file=str(file_path), notes=notes)

    # Keep semantic search in sync with the knowledge base automatically —
    # without this, laptops added/changed by an ingestion run would be
    # invisible (or worse, mismatched) to /api/search and /api/similar until
    # someone manually SSH'd in and ran build_embeddings.py, which isn't a
    # realistic option for a publicly deployed instance.
    index_rebuilt = False
    index_error = None
    try:
        semantic_search.build_index(db)
        index_rebuilt = True
    except Exception as exc:  # pragma: no cover - defensive, index rebuild must never break ingestion
        index_error = str(exc)
        logger.exception("Automatic embedding index rebuild failed after ingesting %s", file_path)

    return {
        "version_tag": version.version_tag,
        "record_count": len(scored_df),
        "ingestion_report": report.model_dump(),
        "index_rebuilt": index_rebuilt,
        "index_error": index_error,
    }


def list_kb_versions(db: Session) -> list[KBVersion]:
    return kb_version.list_versions(db)


def auto_bootstrap(db: Session, raw_data_dir: Path) -> None:
    """Best-effort, idempotent self-healing step run once at app startup.

    Fresh clones / fresh containers commonly have an empty database and no
    FAISS index because the multi-step manual setup (`init_db.py` ->
    `run_ingestion.py` -> `build_embeddings.py`) was never run — which is
    exactly what surfaces to end users as "AI Search: could not reach the
    server" even though the real cause is "the index was never built".
    This makes the app self-sufficient:
      1. If the `laptops` table is empty, ingest the newest raw file already
         sitting in data/raw/ (if any) — this also rebuilds the index, since
         run_ingestion_pipeline() does that automatically now.
      2. Otherwise, if laptops already exist but the FAISS index file is
         still missing (e.g. the DB was restored from a backup/volume but
         data/embeddings/ was not), just rebuild the index.
    Never raises — logs and leaves the app running in a degraded-but-honest
    state (reported by GET /health) if it can't complete either step, e.g.
    because there is no raw file yet or the embedding model can't be
    downloaded in a network-restricted environment.
    """
    from app.config import settings

    try:
        has_laptops = db.query(Laptop.id).first() is not None
    except Exception:
        logger.exception("Auto-bootstrap: could not query the laptops table.")
        return

    if not has_laptops:
        candidates = sorted(
            [*raw_data_dir.glob("*.csv"), *raw_data_dir.glob("*.json")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not candidates:
            logger.warning(
                "Auto-bootstrap: no laptops in the database and no raw file found in %s — "
                "run `python scripts/generate_synthetic_dataset.py` (or drop your own export "
                "there) and restart, or POST a file to /api/admin/knowledge-base/upload.",
                raw_data_dir,
            )
            return
        newest = candidates[0]
        logger.info("Auto-bootstrap: empty database detected, ingesting %s ...", newest)
        try:
            result = run_ingestion_pipeline(db, newest, notes="Auto-bootstrap on startup")
            logger.info(
                "Auto-bootstrap: ingested %d laptops (version=%s, index_rebuilt=%s).",
                result["record_count"], result["version_tag"], result["index_rebuilt"],
            )
        except Exception:
            logger.exception("Auto-bootstrap: ingestion of %s failed.", newest)
        return

    if not settings.FAISS_INDEX_PATH.exists():
        logger.info("Auto-bootstrap: laptops exist but the search index is missing — rebuilding it.")
        try:
            semantic_search.build_index(db)
        except Exception:
            logger.exception("Auto-bootstrap: index rebuild failed.")
