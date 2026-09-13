"""
LaptopSathi AI — FastAPI backend entrypoint.

Run with:
    uvicorn app.main:app --reload

All business logic lives in app/<module>/*.py; routers are thin adapters
that validate input (Pydantic), call the relevant service module, and
serialize the ORM result to a response schema. The frontend contains no
business logic and only talks to these endpoints.

This module also centralizes cross-cutting concerns: CORS, request logging,
and a uniform JSON error envelope for every failure mode (validation errors,
domain errors like "laptop not found", and unexpected exceptions).
"""
import logging
import time

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import init_db, get_db, SessionLocal
from app.utils.exceptions import LaptopSathiError
from app.routers import (
    laptops, search, recommend, compare, budget, price, users, analytics, similar, admin,
)
from app.auth.router import router as auth_router
from app.admin.log_buffer import RingBufferHandler
from app.admin.kb_admin import auto_bootstrap

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("laptopsathi")
logging.getLogger().addHandler(RingBufferHandler())  # feeds GET /api/admin/logs

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered laptop recommendation & decision support platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method, request.url.path, response.status_code, duration_ms,
    )
    return response


# ---------------------------------------------------------------------------
# Uniform error envelope for every failure mode
# ---------------------------------------------------------------------------
def _error_body(code: str, message: str, details=None) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


@app.exception_handler(LaptopSathiError)
async def domain_error_handler(request: Request, exc: LaptopSathiError):
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body(exc.code, exc.message, exc.details),
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=_error_body("VALIDATION_ERROR", "The request payload is invalid.", exc.errors()),
    )


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_body("HTTP_ERROR", str(exc.detail)),
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=_error_body("INTERNAL_ERROR", "Something went wrong on our end. Please try again."),
    )


_DEFAULT_JWT_SECRET = "dev-only-change-me-in-production-6f8a9c2e1b7d4f0a"


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("%s started (env=%s, db=%s)", settings.APP_NAME, settings.ENV, settings.DATABASE_URL)

    if settings.ENV.lower() in ("production", "prod"):
        if settings.JWT_SECRET_KEY == _DEFAULT_JWT_SECRET:
            logger.error(
                "SECURITY: ENV=%s but JWT_SECRET_KEY is still the development default. "
                "Set a unique, secret JWT_SECRET_KEY in the environment before exposing "
                "this server publicly — anyone can forge access tokens otherwise.",
                settings.ENV,
            )
        if settings.CORS_ORIGINS == ["*"]:
            logger.warning(
                "ENV=%s but CORS_ORIGINS is still '*'. Set it to your real frontend "
                "origin(s) (comma-separated) for a public deployment.", settings.ENV,
            )
        if not settings.email_delivery_enabled:
            logger.error(
                "ENV=%s but SMTP_HOST is not set — registration OTPs and password-reset "
                "links will NOT be emailed to users, only logged server-side. Set "
                "SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD (see .env.example) before "
                "exposing this server publicly.", settings.ENV,
            )
    elif not settings.email_delivery_enabled:
        logger.info(
            "SMTP_HOST is not set — registration OTPs and password-reset links will be "
            "logged instead of emailed (fine for local development). See .env.example."
        )

    if settings.AUTO_BOOTSTRAP_KB:
        db = SessionLocal()
        try:
            auto_bootstrap(db, settings.RAW_DATA_DIR)
        finally:
            db.close()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "app": settings.APP_NAME}


@app.get("/health", tags=["Health"])
def health():
    """Reports overall health plus live DB connectivity and semantic-search
    index readiness, so the frontend can distinguish 'server down' from
    'server up but index not built yet'."""
    db_ok = True
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_ok = False

    index_ready = settings.FAISS_INDEX_PATH.exists()

    status = "healthy" if db_ok else "degraded"
    return {
        "status": status,
        "database": "connected" if db_ok else "unreachable",
        "semantic_search_index": "ready" if index_ready else "not_built",
    }


app.include_router(auth_router)
app.include_router(admin.router)
app.include_router(laptops.router)
app.include_router(search.router)
app.include_router(recommend.router)
app.include_router(compare.router)
app.include_router(budget.router)
app.include_router(price.router)
app.include_router(users.router)
app.include_router(analytics.router)
app.include_router(similar.router)
