"""
Knowledge Base Versioning.

Every knowledge-base update (a new ingestion + engineering + feature-store
run) creates a new version record and snapshots the processed dataset to
disk under data/kb_versions/, enabling rollback, dataset comparison across
versions, change tracking, and reproducibility.
"""
from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.models.db_models import KBVersion


def next_version_tag(db: Session) -> str:
    count = db.query(KBVersion).count()
    return f"v{count + 1}"


def create_version(
    db: Session,
    processed_df: pd.DataFrame,
    source_file: str,
    notes: str = "",
) -> KBVersion:
    tag = next_version_tag(db)
    snapshot_path = settings.KB_VERSIONS_DIR / f"{tag}.csv"
    processed_df.to_csv(snapshot_path, index=False)

    version = KBVersion(
        version_tag=tag,
        source_file=source_file,
        record_count=len(processed_df),
        notes=notes or f"Auto-created on {datetime.utcnow().isoformat()}",
    )
    db.add(version)
    db.commit()
    db.refresh(version)
    return version


def list_versions(db: Session) -> list[KBVersion]:
    return db.query(KBVersion).order_by(KBVersion.created_at.desc()).all()


def rollback_to(db: Session, version_tag: str) -> Path:
    """Returns the path to the snapshot CSV for a given version so the caller
    (e.g. a script) can re-run ingestion against it. Rollback does not mutate
    the live DB directly — that's a deliberate safety choice; the operator
    re-runs the ingestion pipeline against the returned snapshot."""
    snapshot_path = settings.KB_VERSIONS_DIR / f"{version_tag}.csv"
    if not snapshot_path.exists():
        raise FileNotFoundError(f"No snapshot found for version {version_tag}")
    return snapshot_path


def diff_versions(version_a: str, version_b: str) -> dict:
    """Simple dataset comparison between two KB versions."""
    path_a = settings.KB_VERSIONS_DIR / f"{version_a}.csv"
    path_b = settings.KB_VERSIONS_DIR / f"{version_b}.csv"
    if not path_a.exists() or not path_b.exists():
        raise FileNotFoundError("One or both version snapshots not found")

    df_a = pd.read_csv(path_a)
    df_b = pd.read_csv(path_b)

    key_cols = ["brand", "model_name", "ram_gb", "storage_gb"]
    set_a = set(df_a[key_cols].apply(tuple, axis=1))
    set_b = set(df_b[key_cols].apply(tuple, axis=1))

    return {
        "version_a": version_a,
        "version_b": version_b,
        "count_a": len(df_a),
        "count_b": len(df_b),
        "added_in_b": len(set_b - set_a),
        "removed_in_b": len(set_a - set_b),
        "unchanged": len(set_a & set_b),
    }
