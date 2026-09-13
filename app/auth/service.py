"""
Authentication service — all the auth business logic lives here; the router
in app.auth.router is a thin adapter, consistent with the rest of the app.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models.db_models import User, Role, RefreshToken, UserSession, PasswordReset, RegistrationOtp
from app.auth.security import (
    hash_password, verify_password, create_access_token,
    generate_raw_token, hash_token, generate_otp, hash_otp,
)
from app.utils.exceptions import InvalidRequestError, UnauthorizedError, NotFoundError


# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------

def get_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter_by(name=name).first()
    if role is None:
        raise InvalidRequestError(
            f"Role '{name}' is not configured. Run `python scripts/seed_auth.py` first."
        )
    return role


# ---------------------------------------------------------------------------
# Registration (two steps: create + OTP-verify) — see schemas_auth.py docstring
# ---------------------------------------------------------------------------

def _issue_registration_otp(db: Session, user: User) -> str:
    """(Re)issues a fresh OTP for a pending (unverified) registration.
    Returns the raw code — the caller must email it and never log it."""
    db.query(RegistrationOtp).filter_by(user_id=user.id).delete()
    raw_otp = generate_otp(settings.REGISTRATION_OTP_LENGTH)
    db.add(RegistrationOtp(
        user_id=user.id,
        otp_hash=hash_otp(raw_otp),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.REGISTRATION_OTP_EXPIRE_MINUTES),
    ))
    db.commit()
    return raw_otp


def start_registration(db: Session, email: str, password: str, full_name: Optional[str]) -> tuple[User, str]:
    """Creates an unverified account and issues a fresh registration OTP.
    The account can't log in (see `authenticate`) until the OTP is
    confirmed via `verify_registration_otp`.

    If an unverified registration already exists for this email (e.g. the
    person never entered the code, or it expired), its details are updated
    and a new OTP is issued rather than erroring — this also lets someone
    fix a typoed name/password before verifying. A *verified* account with
    this email is a hard conflict.

    Returns (user, raw_otp).
    """
    email = email.lower().strip()
    existing = db.query(User).filter_by(email=email).first()

    if existing is not None:
        if existing.is_verified:
            raise InvalidRequestError("An account with this email already exists.")
        existing.hashed_password = hash_password(password)
        existing.full_name = full_name
        db.commit()
        db.refresh(existing)
        return existing, _issue_registration_otp(db, existing)

    role = get_role(db, "user")
    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role_id=role.id,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, _issue_registration_otp(db, user)


def resend_registration_otp(db: Session, email: str) -> Optional[str]:
    """Returns a fresh raw OTP if there's a pending (unverified) registration
    for this email, else None. The caller (router) must return the SAME
    response either way, to avoid leaking which emails are registered."""
    user = db.query(User).filter_by(email=email.lower().strip()).first()
    if user is None or user.is_verified:
        return None
    return _issue_registration_otp(db, user)


def verify_registration_otp(db: Session, email: str, otp: str) -> User:
    """Confirms the OTP, marks the account verified (making it usable), and
    consumes the code so it can't be reused."""
    email = email.lower().strip()
    user = db.query(User).filter_by(email=email).first()

    # Deliberately generic below: don't reveal whether the email exists.
    generic_failure = "That code is incorrect or has expired. Please request a new one."

    if user is None or user.is_verified:
        raise InvalidRequestError(generic_failure)

    record = db.query(RegistrationOtp).filter_by(user_id=user.id).first()
    if record is None:
        raise InvalidRequestError(
            "No verification code is pending for this email. Please register again or request a new code."
        )

    if record.expires_at < datetime.utcnow():
        raise InvalidRequestError(generic_failure)

    if record.attempts >= settings.MAX_REGISTRATION_OTP_ATTEMPTS:
        raise UnauthorizedError("Too many incorrect attempts. Please request a new code.")

    if hash_otp(otp) != record.otp_hash:
        record.attempts += 1
        db.commit()
        raise InvalidRequestError(generic_failure)

    user.is_verified = True
    db.delete(record)
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# Token issuance (shared by register-verify / login / admin-login / refresh)
# ---------------------------------------------------------------------------

def issue_tokens(
    db: Session, user: User, remember_me: bool,
    user_agent: Optional[str] = None, ip_address: Optional[str] = None,
    session_id: Optional[int] = None,
) -> tuple[str, str, int]:
    if session_id is None:
        session = UserSession(
            user_id=user.id, user_agent=user_agent, ip_address=ip_address, remember_me=remember_me,
        )
        db.add(session)
        db.flush()
        session_id = session.id

    access_token = create_access_token(user.id, user.role.name)

    raw_refresh = generate_raw_token()
    days = (
        settings.REMEMBER_ME_REFRESH_TOKEN_EXPIRE_DAYS if remember_me
        else settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    refresh_row = RefreshToken(
        user_id=user.id,
        session_id=session_id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.utcnow() + timedelta(days=days),
    )
    db.add(refresh_row)
    db.commit()

    return access_token, raw_refresh, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


# ---------------------------------------------------------------------------
# Login / lockout
# ---------------------------------------------------------------------------

def _assert_not_locked(user: User) -> None:
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining_minutes = max(1, int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1)
        raise UnauthorizedError(
            f"This account is temporarily locked after repeated failed sign-in attempts. "
            f"Try again in {remaining_minutes} minute(s)."
        )


def _register_failed_attempt(db: Session, user: User) -> None:
    user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
    if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
        user.locked_until = datetime.utcnow() + timedelta(minutes=settings.ACCOUNT_LOCK_MINUTES)
        user.failed_login_attempts = 0
    db.commit()


def authenticate(
    db: Session, email: str, password: str, remember_me: bool,
    required_role: Optional[str] = None,
    user_agent: Optional[str] = None, ip_address: Optional[str] = None,
) -> tuple[User, str, str, int]:
    email = email.lower().strip()
    user = db.query(User).filter_by(email=email).first()

    # Deliberately generic message below: never reveal whether the email
    # exists, whether the role mismatched, or which check failed.
    generic_failure = "Invalid email or password"

    if user is None:
        raise UnauthorizedError(generic_failure)

    _assert_not_locked(user)

    if not user.is_active:
        raise UnauthorizedError("This account has been deactivated. Contact an administrator.")

    if required_role and user.role.name != required_role:
        raise UnauthorizedError(generic_failure)

    if not verify_password(password, user.hashed_password):
        _register_failed_attempt(db, user)
        raise UnauthorizedError(generic_failure)

    if not user.is_verified:
        raise UnauthorizedError(
            "Please verify your email address before signing in. Check your inbox for the verification code, "
            "or register again to request a new one."
        )

    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    db.commit()

    access_token, refresh_token, expires_in = issue_tokens(db, user, remember_me, user_agent, ip_address)
    return user, access_token, refresh_token, expires_in


# ---------------------------------------------------------------------------
# Refresh / logout
# ---------------------------------------------------------------------------

def refresh_access_token(db: Session, raw_refresh_token: str) -> tuple[User, str, str, int]:
    token_hash = hash_token(raw_refresh_token)
    existing = db.query(RefreshToken).filter_by(token_hash=token_hash).first()

    if existing is None or existing.revoked or existing.expires_at < datetime.utcnow():
        raise UnauthorizedError("Your session has expired. Please log in again.")

    user = db.query(User).filter_by(id=existing.user_id).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    remember_me = False
    if existing.session_id is not None:
        session = db.query(UserSession).filter_by(id=existing.session_id).first()
        if session is not None:
            remember_me = bool(session.remember_me)

    # Rotation: revoke the used token, mint a fresh access+refresh pair on the same session.
    existing.revoked = True
    db.commit()

    access_token, new_refresh_token, expires_in = issue_tokens(
        db, user, remember_me, session_id=existing.session_id,
    )
    return user, access_token, new_refresh_token, expires_in


def logout(db: Session, raw_refresh_token: str) -> None:
    token_hash = hash_token(raw_refresh_token)
    row = db.query(RefreshToken).filter_by(token_hash=token_hash).first()
    if row is None:
        return  # already logged out / invalid — logout is idempotent, no error
    row.revoked = True
    if row.session_id:
        session = db.query(UserSession).filter_by(id=row.session_id).first()
        if session:
            session.revoked_at = datetime.utcnow()
    db.commit()


# ---------------------------------------------------------------------------
# Password reset
# ---------------------------------------------------------------------------

def request_password_reset(db: Session, email: str) -> Optional[str]:
    """Returns the raw reset token if the account exists, else None. The
    caller (router) must return the SAME response either way to avoid leaking
    which emails are registered (user enumeration)."""
    user = db.query(User).filter_by(email=email.lower().strip()).first()
    if user is None:
        return None

    raw_token = generate_raw_token()
    db.add(PasswordReset(
        user_id=user.id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
    ))
    db.commit()
    return raw_token


def reset_password(db: Session, raw_token: str, new_password: str) -> None:
    token_hash = hash_token(raw_token)
    reset_row = db.query(PasswordReset).filter_by(token_hash=token_hash, used_at=None).first()

    if reset_row is None or reset_row.expires_at < datetime.utcnow():
        raise InvalidRequestError("This password reset link is invalid or has expired.")

    user = db.query(User).filter_by(id=reset_row.user_id).first()
    if user is None:
        raise NotFoundError("User not found")

    user.hashed_password = hash_password(new_password)
    user.failed_login_attempts = 0
    user.locked_until = None
    reset_row.used_at = datetime.utcnow()

    # Resetting a password invalidates every existing session as a safety measure.
    db.query(RefreshToken).filter_by(user_id=user.id, revoked=False).update({"revoked": True})
    db.commit()
