"""Pydantic request/response schemas for the authentication API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=120)

    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)
    remember_me: bool = False


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if not any(c.isupper() for c in v) or not any(c.islower() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Password must contain upper- and lower-case letters and a number")
        return v


class UserOut(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    is_verified: bool
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserOut


class MessageResponse(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# Registration email-OTP verification
#
# Registration is two steps: POST /register creates an unverified account
# and emails a 6-digit code (logged as a placeholder — see app.auth.router);
# POST /register/verify-otp confirms that code and only then issues real
# session tokens (the account is unusable — can't log in — until then). This
# is what proves the email address genuinely exists and is reachable by the
# person registering it, not just that it's well-formed.
# ---------------------------------------------------------------------------

class RegisterStartResponse(BaseModel):
    message: str
    email: str


class RegisterVerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=4, max_length=8)


class ResendRegistrationOtpRequest(BaseModel):
    email: EmailStr
