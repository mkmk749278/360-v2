"""Fail-open exception telemetry — silent failure is banned (2026-07-14).

The numpy-truthiness incident (PRs #726/#727): EIGHT features were dead in
production because their fail-open ``except Exception`` handlers logged at
DEBUG — invisible in prod logs — and nothing counted the failures.  The
stop-geometry A/B raised on *every single call* for 25 hours and no one knew.

This module is the fix for the *silent* half of that failure mode.  Every
fail-open handler in a data/measurement path calls :func:`record` instead of
(or in addition to) a bare debug log:

- **Counted**: a thread-safe, O(1), in-memory counter per call site, exposed
  via :func:`snapshot` to the feature-liveness manifest → monitor pager.
- **Visible**: logged at WARNING (never DEBUG), rate-limited per site so a
  hot loop failing every tick cannot flood the log.
- **Behaviour-preserving**: the caller still fails open exactly as before —
  the failure is just no longer invisible.

Hot-path safe: no I/O, one dict update under a lock.
"""
from __future__ import annotations

import threading
import time
from typing import Any, Dict, Optional

from src.utils import get_logger

log = get_logger("fail_open")

# One WARNING per site per this interval; every occurrence still counts.
_LOG_INTERVAL_SEC = 600.0

_lock = threading.Lock()
_sites: Dict[str, Dict[str, Any]] = {}
_last_logged: Dict[str, float] = {}


def record(site: str, exc: BaseException, *, now: Optional[float] = None) -> None:
    """Count one fail-open occurrence at *site* (never raises).

    ``site`` is a stable dotted name for the call site, e.g.
    ``"scanner.stamp_geometry_ab"`` — it is the key the liveness manifest,
    the truth report, and the pager all display, so keep it greppable.
    """
    try:
        ts = time.time() if now is None else float(now)
        with _lock:
            entry = _sites.setdefault(
                site, {"count": 0, "last_error": "", "last_ts": 0.0}
            )
            entry["count"] = int(entry["count"]) + 1
            entry["last_error"] = f"{type(exc).__name__}: {exc}"[:300]
            entry["last_ts"] = ts
            do_log = ts - _last_logged.get(site, 0.0) >= _LOG_INTERVAL_SEC
            if do_log:
                _last_logged[site] = ts
            count = entry["count"]
        if do_log:
            log.warning(
                "fail-open at {} (count={}): {}: {}",
                site, count, type(exc).__name__, exc,
            )
    except Exception:  # telemetry must never break the caller
        pass


def snapshot() -> Dict[str, Dict[str, Any]]:
    """Copy of all site counters (for the liveness manifest / truth report)."""
    with _lock:
        return {site: dict(entry) for site, entry in _sites.items()}


def reset() -> None:
    """Test helper — clear all counters."""
    with _lock:
        _sites.clear()
        _last_logged.clear()
