"""
Security primitives: password hashing (bcrypt), JWT issuance/verification,
and registration-OTP generation/hashing.

Design notes:
 - Passwords are always hashed with bcrypt (via the `bcrypt` package directly —
   no plaintext ever touches the database).
 - Access tokens are short-lived signed JWTs (default 15 min) carrying the
   user id and role, so most requests never hit the database for auth.
 - Refresh tokens are opaque random strings; only their SHA-256 hash is
   stored server-side (in `refresh_tokens`), so a database leak alone can't
   be replayed as a valid refresh token.
 - Purpose tokens (password reset) are short-lived signed JWTs with a
   `purpose` claim, so one signing scheme covers all short-lived, single-use
   links without extra DB tables for verification.
 - Registration OTPs are short numeric codes; only their SHA-256 hash is
   stored (see app.models.db_models.RegistrationOtp), the same pattern as
   refresh tokens — a database leak alone doesn't hand over a usable code.
"""
from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# JWTs
# ---------------------------------------------------------------------------

def create_access_token(user_id: int, role: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "role": role,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_purpose_token(user_id: int, purpose: str, minutes: int, extra_claims: dict | None = None) -> str:
    """Short-lived signed token for password-reset-style flows. `extra_claims`
    lets callers embed small, non-secret bits of state that need to survive
    a multi-step flow without a server-side session store."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "purpose": purpose,
        "iat": now,
        "exp": now + timedelta(minutes=minutes),
        **(extra_claims or {}),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Raises jwt.PyJWTError (or a subclass) on any invalid/expired token —
    callers are expected to catch that broadly and translate to 401/400."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


# ---------------------------------------------------------------------------
# Opaque refresh / reset tokens
# ---------------------------------------------------------------------------

def generate_raw_token() -> str:
    """A high-entropy opaque token, e.g. for refresh tokens. Only its hash is
    ever persisted; the raw value is returned to the client exactly once."""
    return secrets.token_urlsafe(48)


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Registration OTP (email verification at signup)
# ---------------------------------------------------------------------------

def generate_otp(length: int) -> str:
    """A cryptographically random numeric code, e.g. '482913'. Uses
    `secrets` (not `random`) since this gates account creation and must not
    be predictable."""
    return "".join(secrets.choice("0123456789") for _ in range(length))


def hash_otp(raw_otp: str) -> str:
    return hashlib.sha256(raw_otp.strip().encode("utf-8")).hexdigest()
