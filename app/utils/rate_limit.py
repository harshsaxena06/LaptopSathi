"""
Lightweight in-memory IP-based rate limiter.

The per-account lockout in app.auth.service handles repeated bad passwords
against ONE known account, but does nothing to stop registration spam,
password-reset email spam, or credential stuffing spread across many
different email addresses — all of which are realistic abuse patterns the
moment this API is reachable from the public internet. This closes that gap
cheaply, without adding a new infrastructure dependency.

Good enough for a single-instance deployment (the default here — sqlite,
one backend container). If you scale to multiple backend replicas behind a
load balancer, swap this for a shared store (Redis, e.g. via `slowapi` or
similar) — an in-memory counter only sees requests that land on the same
process.
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque, Dict, Tuple

from fastapi import Request

from app.utils.exceptions import LaptopSathiError


class RateLimitedError(LaptopSathiError):
    status_code = 429
    code = "RATE_LIMITED"


_hits: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)


def rate_limit(key: str, limit: int, window_seconds: int = 60):
    """FastAPI dependency factory: allow at most `limit` requests per
    `window_seconds` per (key, client IP) pair, e.g.
    `Depends(rate_limit("login", limit=10, window_seconds=60))`.
    """
    def _dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        bucket = _hits[(key, ip)]
        now = time.monotonic()
        while bucket and now - bucket[0] > window_seconds:
            bucket.popleft()
        if len(bucket) >= limit:
            raise RateLimitedError(
                "Too many attempts from this address. Please wait a minute and try again."
            )
        bucket.append(now)

    return _dependency
