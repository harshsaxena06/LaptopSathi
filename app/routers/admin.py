"""
Admin-only API. Everything here requires the `admin` role (see
app.auth.dependencies.require_role). Covers the ADMIN-tier permissions from
the product spec: Knowledge Base Upload, Dataset Versioning, User
Management, System Settings, Logs. (Analytics is admin-only too, but lives
in app.routers.analytics since it's dataset-analytics, not account admin.)
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings
from app.models.db_models import User, Role
from app.auth.dependencies import require_role
from app.admin import kb_admin
from app.admin.log_buffer import get_recent_logs
from app.utils.exceptions import InvalidRequestError, NotFoundError
from app.search import semantic_search

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class IndexRebuildResponse(BaseModel):
    vectors_indexed: int


# ---------------------------------------------------------------------------
# Knowledge Base upload & versioning
# ---------------------------------------------------------------------------

class KBUploadResponse(BaseModel):
    version_tag: str
    record_count: int
    invalid_rows: int
    duplicate_rows: int
    index_rebuilt: bool
    index_error: Optional[str] = None


class KBVersionOut(BaseModel):
    version_tag: str
    source_file: Optional[str]
    record_count: int
    notes: Optional[str]
    created_at: str


@router.post("/knowledge-base/upload", response_model=KBUploadResponse)
async def upload_knowledge_base(
    file: UploadFile = File(...),
    notes: str = "",
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    if file.filename is None or not file.filename.lower().endswith((".csv", ".json")):
        raise InvalidRequestError("Only .csv or .json files are accepted.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = kb_admin.run_ingestion_pipeline(db, tmp_path, notes=notes or f"Uploaded by {current_user.email}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    report = result["ingestion_report"]
    return KBUploadResponse(
        version_tag=result["version_tag"],
        record_count=result["record_count"],
        invalid_rows=report["invalid_rows"],
        duplicate_rows=report["duplicate_rows"],
        index_rebuilt=result["index_rebuilt"],
        index_error=result["index_error"],
    )


@router.post("/knowledge-base/rebuild-index", response_model=IndexRebuildResponse)
def rebuild_index(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Manual safety valve: force a full FAISS rebuild without re-uploading a
    file. Useful after data edits made another way, or to recover if the
    automatic rebuild on upload ever fails (e.g. transient OOM)."""
    count = semantic_search.build_index(db)
    return IndexRebuildResponse(vectors_indexed=count)


@router.get("/knowledge-base/versions", response_model=list[KBVersionOut])
def list_kb_versions(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    versions = kb_admin.list_kb_versions(db)
    return [
        KBVersionOut(
            version_tag=v.version_tag, source_file=v.source_file,
            record_count=v.record_count, notes=v.notes, created_at=v.created_at.isoformat(),
        )
        for v in versions
    ]


# ---------------------------------------------------------------------------
# User management
# ---------------------------------------------------------------------------

class AdminUserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: str
    last_login_at: Optional[str]


class UpdateUserRequest(BaseModel):
    role: Optional[str] = None       # "user" | "admin"
    is_active: Optional[bool] = None


def _to_admin_user_out(u: User) -> AdminUserOut:
    return AdminUserOut(
        id=u.id, email=u.email, full_name=u.full_name, role=u.role.name,
        is_active=u.is_active, is_verified=u.is_verified,
        created_at=u.created_at.isoformat(),
        last_login_at=u.last_login_at.isoformat() if u.last_login_at else None,
    )


@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    limit: int = Query(default=100, le=500),
    offset: int = 0,
):
    users = db.query(User).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    return [_to_admin_user_out(u) for u in users]


@router.patch("/users/{user_id}", response_model=AdminUserOut)
def update_user(
    user_id: int,
    payload: UpdateUserRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter_by(id=user_id).first()
    if user is None:
        raise NotFoundError("User not found")

    if payload.role is not None:
        role = db.query(Role).filter_by(name=payload.role).first()
        if role is None:
            raise InvalidRequestError(f"Unknown role: {payload.role}")
        if user.id == current_user.id and payload.role != "admin":
            raise InvalidRequestError("You cannot demote your own account.")
        user.role_id = role.id

    if payload.is_active is not None:
        if user.id == current_user.id and not payload.is_active:
            raise InvalidRequestError("You cannot deactivate your own account.")
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return _to_admin_user_out(user)


# ---------------------------------------------------------------------------
# System settings (read-only snapshot — no secrets)
# ---------------------------------------------------------------------------

class SystemSettingsOut(BaseModel):
    app_name: str
    env: str
    embedding_model: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    max_failed_login_attempts: int
    account_lock_minutes: int
    recommendation_weights: dict


@router.get("/settings", response_model=SystemSettingsOut)
def get_settings(current_user: User = Depends(require_role("admin"))):
    return SystemSettingsOut(
        app_name=settings.APP_NAME,
        env=settings.ENV,
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
        max_failed_login_attempts=settings.MAX_FAILED_LOGIN_ATTEMPTS,
        account_lock_minutes=settings.ACCOUNT_LOCK_MINUTES,
        recommendation_weights={
            "semantic": settings.WEIGHT_SEMANTIC,
            "budget": settings.WEIGHT_BUDGET,
            "compatibility": settings.WEIGHT_COMPATIBILITY,
            "benchmark": settings.WEIGHT_BENCHMARK,
            "brand_preference": settings.WEIGHT_BRAND_PREF,
            "future_proof": settings.WEIGHT_FUTURE_PROOF,
        },
    )


# ---------------------------------------------------------------------------
# Logs
# ---------------------------------------------------------------------------

class LogEntryOut(BaseModel):
    timestamp: str
    level: str
    logger: str
    message: str


@router.get("/logs", response_model=list[LogEntryOut])
def get_logs(current_user: User = Depends(require_role("admin")), limit: int = 200):
    return get_recent_logs(limit=limit)
