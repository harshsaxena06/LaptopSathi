"""
SQLAlchemy engine / session management.
Uses SQLite by default (DATABASE_URL in config.py); switching to Postgres
in production requires only an env var change, no code change.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called on startup / by scripts/init_db.py."""
    from app.models import db_models  # noqa: F401  (ensures models are registered)
    Base.metadata.create_all(bind=engine)
