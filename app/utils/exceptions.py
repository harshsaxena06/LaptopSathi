"""
Shared application exceptions.

Service modules (recommendation, comparison, budget optimizer, etc.) raise
these instead of bare ValueError/RuntimeError, so routers and the global
FastAPI exception handler can map them to consistent HTTP status codes and
a uniform JSON error shape:

    {"error": {"code": "NOT_FOUND", "message": "...", "details": null}}
"""
from __future__ import annotations


class LaptopSathiError(Exception):
    """Base class for all application-level errors."""
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str, details=None):
        super().__init__(message)
        self.message = message
        self.details = details


class NotFoundError(LaptopSathiError):
    status_code = 404
    code = "NOT_FOUND"


class UnauthorizedError(LaptopSathiError):
    """Missing, invalid, or expired credentials/tokens."""
    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(LaptopSathiError):
    """Authenticated, but lacking the required role/permission."""
    status_code = 403
    code = "FORBIDDEN"


class InvalidRequestError(LaptopSathiError):
    status_code = 400
    code = "INVALID_REQUEST"


class DependencyNotReadyError(LaptopSathiError):
    """Raised when a required artifact (e.g. the FAISS index) hasn't been built yet."""
    status_code = 503
    code = "DEPENDENCY_NOT_READY"


class EmailDeliveryError(LaptopSathiError):
    """The email provider rejected the message or couldn't be reached —
    an infrastructure/config problem, not the caller's fault."""
    status_code = 502
    code = "EMAIL_DELIVERY_FAILED"
