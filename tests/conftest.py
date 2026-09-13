"""
Shared pytest fixtures for the FastAPI test suite.

Each test gets a fresh, isolated SQLite database (a temp file) with
roles/permissions seeded, and a TestClient wired to it via FastAPI's
dependency override — never the real dev/prod database.

Environment variables MUST be set before `app.config`/`app.main` are ever
imported (Settings() reads them once, at import time), so this happens at
module scope before any `from app...` import below. In particular
AUTO_BOOTSTRAP_KB=false keeps the test suite independent of the ML stack
(sentence-transformers/faiss) used by the knowledge-base ingestion
pipeline, which isn't needed to test authentication/2FA.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP_DB_DIR = tempfile.mkdtemp(prefix="laptopsathi-test-")
os.environ.setdefault("ENV", "test")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP_DB_DIR}/app.db")
os.environ.setdefault("AUTO_BOOTSTRAP_KB", "false")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-jwt-secret-do-not-use-in-prod")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models import db_models  # noqa: F401 — registers all models on Base
from app.main import app as fastapi_app


@pytest.fixture()
def db_session(tmp_path):
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    from scripts.seed_auth import upsert_role, upsert_permission, USER_PERMISSIONS, ADMIN_ONLY_PERMISSIONS

    session = TestingSessionLocal()
    try:
        all_perm_codes = [c for c, _ in USER_PERMISSIONS]
        admin_perm_codes = all_perm_codes + [c for c, _ in ADMIN_ONLY_PERMISSIONS]
        for code, desc in USER_PERMISSIONS + ADMIN_ONLY_PERMISSIONS:
            upsert_permission(session, code, desc)
        upsert_role(session, "user", "Standard end user", all_perm_codes)
        upsert_role(session, "admin", "Administrator — full access", admin_perm_codes)
        session.commit()
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """The in-memory rate limiter (app.utils.rate_limit) is a module-level
    dict shared by the whole process — reset it before every test so one
    test's requests can't trip another test's rate limit."""
    from app.utils import rate_limit
    rate_limit._hits.clear()
    yield
    rate_limit._hits.clear()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    from fastapi.testclient import TestClient
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.pop(get_db, None)
