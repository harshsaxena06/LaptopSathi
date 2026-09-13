"""
Knowledge Database schema (SQLAlchemy ORM).

Tables: brands, laptops, cpu_benchmarks, gpu_benchmarks, price_history,
compatibility_scores, embeddings_metadata, user_preferences, user_history,
kb_versions, users, roles, permissions, refresh_tokens, password_resets,
user_sessions.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text, JSON, Table
)
from sqlalchemy.orm import relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Authentication / RBAC
# ---------------------------------------------------------------------------

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False, index=True)  # "user" / "admin"
    description = Column(String(255), nullable=True)

    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", back_populates="role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    code = Column(String(64), unique=True, nullable=False, index=True)  # e.g. "kb:upload"
    description = Column(String(255), nullable=True)

    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # bcrypt hash — never plaintext
    full_name = Column(String(120), nullable=True)

    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    last_login_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    registration_otp = relationship("RegistrationOtp", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserSession(Base):
    """One row per login (device/browser). A refresh token belongs to a session
    so 'logout' and future 'log out other devices' can target a specific one."""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    user_agent = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)
    remember_me = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="sessions")


class RefreshToken(Base):
    """Refresh tokens are stored as a SHA-256 hash (never the raw token) so a
    database leak alone can't be used to mint new access tokens. Rotated on
    every use: refreshing revokes the old row and issues a new one."""
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("user_sessions.id"), nullable=True)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="refresh_tokens")


class PasswordReset(Base):
    """Password-reset requests. Tokens are single-use and stored hashed, same
    rationale as refresh tokens."""
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token_hash = Column(String(128), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RegistrationOtp(Base):
    """One row per pending (unverified) registration. The OTP proves the
    signup email is real and reachable, not just well-formed — the account
    stays unusable (User.is_verified=False) until it's confirmed.

    Stored as a SHA-256 hash only (see app.auth.security.hash_otp), same
    rationale as RefreshToken/PasswordReset — the raw code only ever exists
    in the "sent" email and briefly in memory server-side while checking it.
    """
    __tablename__ = "registration_otps"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    otp_hash = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="registration_otp")


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False, index=True)
    country = Column(String(64), nullable=True)
    reliability_score = Column(Float, default=3.5)  # 0-5, curated

    laptops = relationship("Laptop", back_populates="brand")


class CPUBenchmark(Base):
    __tablename__ = "cpu_benchmarks"

    id = Column(Integer, primary_key=True)
    cpu_name = Column(String(128), unique=True, nullable=False, index=True)
    cores = Column(Integer, nullable=True)
    threads = Column(Integer, nullable=True)
    base_clock_ghz = Column(Float, nullable=True)
    boost_clock_ghz = Column(Float, nullable=True)
    single_core_score = Column(Integer, nullable=True)   # Geekbench-like
    multi_core_score = Column(Integer, nullable=True)
    tdp_watts = Column(Integer, nullable=True)
    generation = Column(String(32), nullable=True)

    laptops = relationship("Laptop", back_populates="cpu_bench")


class GPUBenchmark(Base):
    __tablename__ = "gpu_benchmarks"

    id = Column(Integer, primary_key=True)
    gpu_name = Column(String(128), unique=True, nullable=False, index=True)
    vram_gb = Column(Float, nullable=True)
    is_dedicated = Column(Boolean, default=False)
    supports_cuda = Column(Boolean, default=False)
    benchmark_score = Column(Integer, nullable=True)  # 3DMark-like relative score

    laptops = relationship("Laptop", back_populates="gpu_bench")


class Laptop(Base):
    __tablename__ = "laptops"

    id = Column(Integer, primary_key=True)
    model_name = Column(String(200), nullable=False, index=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)

    cpu_bench_id = Column(Integer, ForeignKey("cpu_benchmarks.id"), nullable=True)
    gpu_bench_id = Column(Integer, ForeignKey("gpu_benchmarks.id"), nullable=True)

    ram_gb = Column(Integer, nullable=False)
    ram_upgradeable = Column(Boolean, default=False)
    storage_gb = Column(Integer, nullable=False)
    storage_type = Column(String(16), default="SSD")  # SSD / HDD / Hybrid
    storage_upgradeable = Column(Boolean, default=False)

    display_size_inch = Column(Float, nullable=True)
    display_resolution = Column(String(32), nullable=True)  # e.g. "1920x1080"
    refresh_rate_hz = Column(Integer, default=60)

    battery_whr = Column(Float, nullable=True)
    battery_life_hours = Column(Float, nullable=True)

    weight_kg = Column(Float, nullable=True)

    price_inr = Column(Float, nullable=False)

    release_year = Column(Integer, nullable=True)

    # Derived/engineered fields (populated by the data engineering pipeline)
    programming_score = Column(Float, default=0.0)
    ai_ml_score = Column(Float, default=0.0)
    gaming_score = Column(Float, default=0.0)
    video_editing_score = Column(Float, default=0.0)
    battery_score = Column(Float, default=0.0)
    portability_score = Column(Float, default=0.0)
    business_score = Column(Float, default=0.0)
    student_score = Column(Float, default=0.0)
    future_proof_score = Column(Float, default=0.0)

    description_text = Column(Text, nullable=True)  # used to build embeddings

    is_active = Column(Boolean, default=True)
    kb_version = Column(String(32), default="v1")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    brand = relationship("Brand", back_populates="laptops")
    cpu_bench = relationship("CPUBenchmark", back_populates="laptops")
    gpu_bench = relationship("GPUBenchmark", back_populates="laptops")
    price_history = relationship("PriceHistory", back_populates="laptop", cascade="all, delete-orphan")
    compatibility = relationship("CompatibilityScore", back_populates="laptop", uselist=False, cascade="all, delete-orphan")
    embedding_meta = relationship("EmbeddingMetadata", back_populates="laptop", uselist=False, cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(Integer, ForeignKey("laptops.id"), nullable=False)
    price_inr = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(64), default="knowledge_base")

    laptop = relationship("Laptop", back_populates="price_history")


class CompatibilityScore(Base):
    """Pre-computed compatibility flags/scores used by the recommendation engine."""
    __tablename__ = "compatibility_scores"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(Integer, ForeignKey("laptops.id"), unique=True, nullable=False)

    supports_cuda_workloads = Column(Boolean, default=False)
    supports_android_dev = Column(Boolean, default=True)
    supports_ios_dev = Column(Boolean, default=False)  # requires macOS
    supports_heavy_multitasking = Column(Boolean, default=False)
    supports_4k_editing = Column(Boolean, default=False)
    thermal_headroom_score = Column(Float, default=0.5)  # 0-1

    laptop = relationship("Laptop", back_populates="compatibility")


class EmbeddingMetadata(Base):
    """Tracks which FAISS index / vector row corresponds to which laptop."""
    __tablename__ = "embeddings_metadata"

    id = Column(Integer, primary_key=True)
    laptop_id = Column(Integer, ForeignKey("laptops.id"), unique=True, nullable=False)
    faiss_index_position = Column(Integer, nullable=False)
    embedding_model = Column(String(64), nullable=False)
    text_hash = Column(String(64), nullable=False)  # to detect stale embeddings
    updated_at = Column(DateTime, default=datetime.utcnow)

    laptop = relationship("Laptop", back_populates="embedding_meta")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    preferred_brands = Column(JSON, default=list)
    budget_min = Column(Float, default=0)
    budget_max = Column(Float, default=1000000)
    primary_use_case = Column(String(64), nullable=True)  # gaming/programming/etc.
    saved_laptop_ids = Column(JSON, default=list)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="preferences")


class UserHistory(Base):
    __tablename__ = "user_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_type = Column(String(32), nullable=False)  # "search" / "view" / "compare" / "save"
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class KBVersion(Base):
    """Knowledge-base versioning for rollback / change tracking / reproducibility."""
    __tablename__ = "kb_versions"

    id = Column(Integer, primary_key=True)
    version_tag = Column(String(32), unique=True, nullable=False)
    source_file = Column(String(256), nullable=True)
    record_count = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
