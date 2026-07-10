"""Application-layer rate limiting for the public API (audit F-14).

Cloudflare absorbs volumetric floods in front of ``api.luminapp.org``, but
nothing at this layer stopped a single client from hammering expensive
endpoints (snapshot builds, OTP issue, billing verify) at line rate.  This
middleware adds a per-client sliding-window limit:

* **Client key** — the Bearer token when present (SHA-256 prefix, so a
  token never sits in memory as a dict key in the clear), else the client
  IP.  Behind nginx/Cloudflare the socket peer is the proxy, so the first
  hop of ``X-Forwarded-For`` is used when present.  Per-token keying means
  one abusive device can't consume another device's budget behind a
  shared CGNAT IP (common on Indian mobile networks).
* **Sliding window** — timestamps in a deque per client, pruned on every
  hit.  Pure in-memory, zero I/O on the hot path (Cost Discipline: no new
  reads/writes anywhere).
* **Bounded memory** — at most ``max_clients`` tracked keys; when full,
  the stalest client is evicted.  A deque per client holds at most
  ``limit_per_min`` timestamps.

Defaults are deliberately generous — the busiest legitimate client (the
app's 15s poll loop + a tab of the ops dashboard) sits far under 60
requests/min; 240/min only throttles abuse, never subscribers.  All knobs
env-overridable per B8:

* ``API_RATE_LIMIT_ENABLED``   (default ``true``)
* ``API_RATE_LIMIT_PER_MIN``   (default ``240``)
* ``API_RATE_LIMIT_MAX_CLIENTS`` (default ``10000``)

Health endpoints are exempt so container healthchecks and the liveness
watch can never be throttled into a false-down.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from collections import deque
from typing import Deque, Dict, Optional, Tuple

from src.utils import get_logger

log = get_logger("api.rate_limit")


DEFAULT_LIMIT_PER_MIN = 240
DEFAULT_MAX_CLIENTS = 10_000
_WINDOW_SEC = 60.0

# Never throttle: healthchecks (docker + liveness watch) and the auth mint
# path would brick a client that is trying to recover from a 401 storm.
EXEMPT_PATH_PREFIXES = ("/api/health", "/health", "/healthz")


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name, "")
    if not raw:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


def _env_int(name: str, default: int) -> int:
    try:
        val = int(os.environ.get(name, ""))
        return val if val > 0 else default
    except (TypeError, ValueError):
        return default


class SlidingWindowLimiter:
    """Per-client sliding-window counter.  Thread-safe, in-memory only.

    ``check(key)`` returns ``(allowed, retry_after_seconds)``.  The lock is
    uncontended in practice (uvicorn single event loop); it exists so the
    limiter is also safe from worker threads / tests.
    """

    def __init__(
        self,
        limit_per_min: int = DEFAULT_LIMIT_PER_MIN,
        max_clients: int = DEFAULT_MAX_CLIENTS,
    ) -> None:
        self.limit = max(1, limit_per_min)
        self.max_clients = max(1, max_clients)
        self._hits: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, now: Optional[float] = None) -> Tuple[bool, float]:
        ts = time.monotonic() if now is None else now
        cutoff = ts - _WINDOW_SEC
        with self._lock:
            dq = self._hits.get(key)
            if dq is None:
                if len(self._hits) >= self.max_clients:
                    self._evict_stalest_locked()
                dq = deque()
                self._hits[key] = dq
            while dq and dq[0] <= cutoff:
                dq.popleft()
            if len(dq) >= self.limit:
                # Oldest hit ages out at dq[0] + window — that's when one
                # slot frees up.
                retry_after = max(0.0, dq[0] + _WINDOW_SEC - ts)
                return False, retry_after
            dq.append(ts)
            return True, 0.0

    def _evict_stalest_locked(self) -> None:
        """Drop the client whose most-recent hit is oldest (already locked)."""
        stalest_key = None
        stalest_ts = float("inf")
        for key, dq in self._hits.items():
            last = dq[-1] if dq else 0.0
            if last < stalest_ts:
                stalest_ts = last
                stalest_key = key
        if stalest_key is not None:
            del self._hits[stalest_key]

    @property
    def tracked_clients(self) -> int:
        with self._lock:
            return len(self._hits)


def client_key(
    *,
    authorization: str,
    client_host: str,
    forwarded_for: str,
) -> str:
    """Stable rate-limit key for a request.

    Token-keyed when a Bearer credential is present (hashed — raw tokens
    must never be dict keys or appear in logs), IP-keyed otherwise.
    """
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() == "bearer" and token.strip():
        digest = hashlib.sha256(token.strip().encode("utf-8")).hexdigest()[:24]
        return f"tok:{digest}"
    if forwarded_for:
        # First hop = original client (Cloudflare/nginx append their own).
        first = forwarded_for.split(",")[0].strip()
        if first:
            return f"ip:{first}"
    return f"ip:{client_host or 'unknown'}"


def install_rate_limiting(app) -> Optional[SlidingWindowLimiter]:
    """Attach the rate-limit middleware to a FastAPI app.

    Returns the limiter (for tests/inspection) or ``None`` when disabled
    via ``API_RATE_LIMIT_ENABLED=false``.
    """
    if not _env_bool("API_RATE_LIMIT_ENABLED", True):
        log.warning("API rate limiting DISABLED via API_RATE_LIMIT_ENABLED")
        return None

    limiter = SlidingWindowLimiter(
        limit_per_min=_env_int("API_RATE_LIMIT_PER_MIN", DEFAULT_LIMIT_PER_MIN),
        max_clients=_env_int("API_RATE_LIMIT_MAX_CLIENTS", DEFAULT_MAX_CLIENTS),
    )
    app.state.rate_limiter = limiter

    from fastapi import Request  # local import keeps module importable in tools
    from fastapi.responses import JSONResponse

    @app.middleware("http")
    async def _rate_limit_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        path = request.url.path
        if path.startswith(EXEMPT_PATH_PREFIXES):
            return await call_next(request)
        key = client_key(
            authorization=request.headers.get("authorization", ""),
            client_host=(request.client.host if request.client else ""),
            forwarded_for=request.headers.get("x-forwarded-for", ""),
        )
        allowed, retry_after = limiter.check(key)
        if not allowed:
            # keys are already anonymised (hash prefix / IP) — safe to log.
            log.warning(
                "rate limit exceeded: key={} path={} retry_after={:.1f}s",
                key,
                path,
                retry_after,
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "rate limit exceeded"},
                headers={"Retry-After": str(max(1, int(retry_after + 0.999)))},
            )
        return await call_next(request)

    log.info(
        "API rate limiting active: {}/min per client, max {} tracked clients",
        limiter.limit,
        limiter.max_clients,
    )
    return limiter
