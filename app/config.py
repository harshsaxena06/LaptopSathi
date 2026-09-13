"""
Central configuration for LaptopSathi AI.
Reads from environment variables (.env) with sensible defaults so the
system runs out-of-the-box in development (SQLite) and can be pointed
at PostgreSQL in production by changing DATABASE_URL.
"""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "LaptopSathi AI"
    ENV: str = "development"

    # Database: SQLite for dev, swap to postgresql+psycopg2://... for prod
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'laptopsathi.db'}"

    # Paths
    RAW_DATA_DIR: Path = BASE_DIR / "data" / "raw"
    PROCESSED_DATA_DIR: Path = BASE_DIR / "data" / "processed"
    EMBEDDINGS_DIR: Path = BASE_DIR / "data" / "embeddings"
    KB_VERSIONS_DIR: Path = BASE_DIR / "data" / "kb_versions"

    # Semantic search
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    FAISS_INDEX_PATH: Path = BASE_DIR / "data" / "embeddings" / "laptops.index"
    EMBEDDING_DIM: int = 384  # dim of all-MiniLM-L6-v2

    # Hybrid recommendation weights (must sum to ~1.0, tunable without code changes)
    WEIGHT_SEMANTIC: float = 0.30
    WEIGHT_BUDGET: float = 0.20
    WEIGHT_COMPATIBILITY: float = 0.20
    WEIGHT_BENCHMARK: float = 0.15
    WEIGHT_BRAND_PREF: float = 0.05
    WEIGHT_FUTURE_PROOF: float = 0.10

    # Stored as a plain string (never a list) specifically so pydantic-settings
    # never tries to JSON-decode this env var — that decoding step is what
    # raises a JSONDecodeError on a plain `CORS_ORIGINS=*` in .env, and its
    # exact behavior/availability (e.g. the NoDecode escape hatch) varies
    # across pydantic-settings versions. A plain str field sidesteps that
    # entirely, so this works the same on every version.
    #   CORS_ORIGINS=*
    #   CORS_ORIGINS=https://laptopsathi.ai,https://www.laptopsathi.ai
    CORS_ORIGINS_RAW: str = Field(default="*", alias="CORS_ORIGINS")

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    # If the DB has no laptops yet, ingest the newest file in data/raw/ (and
    # build the FAISS index) automatically on startup instead of requiring a
    # manual `run_ingestion.py` / `build_embeddings.py` step. Safe to disable
    # once you manage the knowledge base entirely through the admin API.
    AUTO_BOOTSTRAP_KB: bool = True

    # ---- Authentication / JWT ----
    # SECURITY: override JWT_SECRET_KEY via environment variable in any real
    # deployment. The default below is only safe for local development.
    JWT_SECRET_KEY: str = "dev-only-change-me-in-production-6f8a9c2e1b7d4f0a"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7          # default "not remembered" session
    REMEMBER_ME_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30

    # ---- Account lockout ----
    MAX_FAILED_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCK_MINUTES: int = 15

    # ---- Bcrypt ----
    BCRYPT_ROUNDS: int = 12

    # ---- Registration email OTP verification ----
    # A new account is created in an unverified state and cannot log in
    # until this code (sent to the email address given at signup) is
    # confirmed — this is what proves the email is real and reachable,
    # rather than just well-formed.
    REGISTRATION_OTP_LENGTH: int = 6
    REGISTRATION_OTP_EXPIRE_MINUTES: int = 10
    MAX_REGISTRATION_OTP_ATTEMPTS: int = 5

    # Where the SPA lives, used only to build placeholder email links in logs
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    # ---- Outgoing email (SMTP) ----
    # If SMTP_HOST is empty (the default), no real email is sent — the app
    # falls back to logging the message instead, which is fine for local
    # development but means registration OTPs / reset links never leave the
    # server. Set these to send real email via any SMTP provider (Gmail,
    # SendGrid, Mailgun, Amazon SES, Postmark, your own mail server, etc.):
    #   SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_USE_TLS
    # See .env.example for provider-specific notes.
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True  # STARTTLS on the given port (587 is standard)
    SMTP_FROM_EMAIL: str = "no-reply@laptopsathi.ai"
    SMTP_FROM_NAME: str = "LaptopSathi AI"
    # Fail fast instead of hanging if the SMTP server is unreachable.
    SMTP_TIMEOUT_SECONDS: int = 10

    @property
    def email_delivery_enabled(self) -> bool:
        return bool(self.SMTP_HOST)

    model_config = SettingsConfigDict(env_file=".env", arbitrary_types_allowed=True, extra="ignore")


settings = Settings()

# Ensure directories exist at import time
for _dir in [settings.RAW_DATA_DIR, settings.PROCESSED_DATA_DIR,
             settings.EMBEDDINGS_DIR, settings.KB_VERSIONS_DIR]:
    _dir.mkdir(parents=True, exist_ok=True)
