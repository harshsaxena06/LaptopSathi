"""
Authentication API.

    POST /api/auth/register            -> start registration: creates an unverified account,
                                           sends a 6-digit email OTP (does NOT log the user in)
    POST /api/auth/register/verify-otp -> confirm the OTP; account becomes usable and is logged in
    POST /api/auth/register/resend-otp -> issue a fresh OTP for a pending registration
    POST /api/auth/login               -> user login (blocked until the account is OTP-verified)
    POST /api/auth/admin-login         -> admin-only login (role-checked)
    POST /api/auth/refresh             -> rotate refresh token, issue new access token
    POST /api/auth/logout              -> revoke a refresh token / session
    POST /api/auth/forgot-password     -> request a reset link (always same response)
    POST /api/auth/reset-password      -> consume a reset token, set new password
    GET  /api/auth/me                  -> current authenticated user
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.auth import service
from app.config import settings
from app.utils.email import send_email, render_registration_otp_email, render_password_reset_email
from app.auth.schemas_auth import (
    RegisterRequest, LoginRequest, AdminLoginRequest, RefreshRequest, LogoutRequest,
    ForgotPasswordRequest, ResetPasswordRequest,
    TokenResponse, UserOut, MessageResponse,
    RegisterStartResponse, RegisterVerifyOtpRequest, ResendRegistrationOtpRequest,
)
from app.auth.dependencies import get_current_user
from app.utils.rate_limit import rate_limit

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _to_user_out(user: User) -> UserOut:
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat(),
    )


def _token_response(user: User, access_token: str, refresh_token: str, expires_in: int) -> TokenResponse:
    return TokenResponse(
        access_token=access_token, refresh_token=refresh_token,
        expires_in=expires_in, user=_to_user_out(user),
    )


# ---------------------------------------------------------------------------
# Registration (create account -> email OTP -> verify -> logged in)
# ---------------------------------------------------------------------------

def _send_registration_otp_email(to_email: str, raw_otp: str) -> None:
    subject, text_body, html_body = render_registration_otp_email(raw_otp, settings.REGISTRATION_OTP_EXPIRE_MINUTES)
    send_email(to_email, subject, text_body, html_body)


@router.post(
    "/register", response_model=RegisterStartResponse, status_code=201,
    dependencies=[Depends(rate_limit("register", limit=5, window_seconds=60))],
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """Creates an unverified account and sends a 6-digit code to the email
    address given. The account cannot log in until that code is confirmed
    at /register/verify-otp — this is what proves the email genuinely
    exists and is reachable, not just well-formed."""
    user, raw_otp = service.start_registration(db, payload.email, payload.password, payload.full_name)
    _send_registration_otp_email(user.email, raw_otp)
    return RegisterStartResponse(
        message="We've sent a 6-digit verification code to your email. Enter it to finish creating your account.",
        email=user.email,
    )


@router.post(
    "/register/verify-otp", response_model=TokenResponse,
    dependencies=[Depends(rate_limit("register-verify-otp", limit=10, window_seconds=60))],
)
def register_verify_otp(payload: RegisterVerifyOtpRequest, request: Request, db: Session = Depends(get_db)):
    """Confirms the emailed code. On success the account becomes verified
    and the user is logged in immediately (real session tokens issued)."""
    user = service.verify_registration_otp(db, payload.email, payload.otp)
    access_token, refresh_token, expires_in = service.issue_tokens(
        db, user, remember_me=False,
        user_agent=request.headers.get("user-agent"), ip_address=_client_ip(request),
    )
    return _token_response(user, access_token, refresh_token, expires_in)


@router.post(
    "/register/resend-otp", response_model=MessageResponse,
    dependencies=[Depends(rate_limit("register-resend-otp", limit=5, window_seconds=60))],
)
def register_resend_otp(payload: ResendRegistrationOtpRequest, db: Session = Depends(get_db)):
    raw_otp = service.resend_registration_otp(db, payload.email)
    if raw_otp:
        _send_registration_otp_email(payload.email, raw_otp)
    # Identical response whether or not a pending registration exists, to avoid user enumeration.
    return MessageResponse(message="If that email has a pending registration, a new code has been sent.")



# ---------------------------------------------------------------------------
# Login / session
# ---------------------------------------------------------------------------

@router.post(
    "/login", response_model=TokenResponse,
    dependencies=[Depends(rate_limit("login", limit=10, window_seconds=60))],
)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user, access_token, refresh_token, expires_in = service.authenticate(
        db, payload.email, payload.password, payload.remember_me,
        user_agent=request.headers.get("user-agent"), ip_address=_client_ip(request),
    )
    return _token_response(user, access_token, refresh_token, expires_in)


@router.post(
    "/admin-login", response_model=TokenResponse,
    dependencies=[Depends(rate_limit("admin-login", limit=5, window_seconds=60))],
)
def admin_login(payload: AdminLoginRequest, request: Request, db: Session = Depends(get_db)):
    user, access_token, refresh_token, expires_in = service.authenticate(
        db, payload.email, payload.password, remember_me=False, required_role="admin",
        user_agent=request.headers.get("user-agent"), ip_address=_client_ip(request),
    )
    return _token_response(user, access_token, refresh_token, expires_in)


@router.post(
    "/refresh", response_model=TokenResponse,
    dependencies=[Depends(rate_limit("refresh", limit=30, window_seconds=60))],
)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    user, access_token, refresh_token, expires_in = service.refresh_access_token(db, payload.refresh_token)
    return _token_response(user, access_token, refresh_token, expires_in)


@router.post("/logout", response_model=MessageResponse)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    service.logout(db, payload.refresh_token)
    return MessageResponse(message="Logged out successfully.")


@router.post(
    "/forgot-password", response_model=MessageResponse,
    dependencies=[Depends(rate_limit("forgot-password", limit=5, window_seconds=60))],
)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    raw_token = service.request_password_reset(db, payload.email)
    if raw_token:
        reset_url = f"{settings.FRONTEND_BASE_URL}/reset-password?token={raw_token}"
        subject, text_body, html_body = render_password_reset_email(reset_url)
        send_email(payload.email, subject, text_body, html_body)
    # Identical response whether or not the email exists, to avoid user enumeration.
    return MessageResponse(message="If an account exists for that email, a reset link has been sent.")


@router.post(
    "/reset-password", response_model=MessageResponse,
    dependencies=[Depends(rate_limit("reset-password", limit=10, window_seconds=60))],
)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    service.reset_password(db, payload.token, payload.new_password)
    return MessageResponse(message="Your password has been reset. Please log in.")


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return _to_user_out(current_user)
