"""
FastAPI dependencies for authentication and role/permission-based access
control (RBAC). These are the server-side counterpart to the frontend's
`ProtectedRoute` / `RoleGuard` components — the frontend guard is a UX nicety,
these dependencies are the actual enforcement boundary.
"""
from __future__ import annotations

from typing import Optional

import jwt
from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.auth.security import decode_token
from app.utils.exceptions import UnauthorizedError, ForbiddenError


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")
    return authorization.split(" ", 1)[1].strip()


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    token = _extract_bearer_token(authorization)
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Your session has expired. Please log in again.")
    except jwt.PyJWTError:
        raise UnauthorizedError("Invalid access token.")

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type.")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found or inactive.")
    return user


def get_current_user_optional(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Like get_current_user, but returns None instead of raising when no
    (or an invalid) token is present — used by endpoints that work for both
    guests and logged-in users (e.g. personalization is 'best effort')."""
    if not authorization:
        return None
    try:
        return get_current_user(authorization, db)
    except Exception:
        return None


def require_role(*allowed_roles: str):
    """Dependency factory: require_role('admin') protects admin-only routes."""
    def _dependency(user: User = Depends(get_current_user)) -> User:
        if user.role.name not in allowed_roles:
            raise ForbiddenError("You do not have permission to perform this action.")
        return user
    return _dependency


def require_permission(permission_code: str):
    """Dependency factory keyed on the fine-grained `permissions` table rather
    than the role name directly, e.g. require_permission('kb:upload')."""
    def _dependency(user: User = Depends(get_current_user)) -> User:
        codes = {p.code for p in user.role.permissions}
        if permission_code not in codes:
            raise ForbiddenError(f"Missing required permission: {permission_code}")
        return user
    return _dependency
