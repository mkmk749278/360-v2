"""Per-pair rolling-window soft penalty — doctrine-aligned replacement for
the hard-blacklist Tier 4 in the 2026-05-17 654-signal audit.

Doctrine reminder (CLAUDE.md §Scalping Doctrine #5): *Soft penalties over
hard blocks. Reserve hard blocks for structural-impossibility checkpoints
only.*  A pair that's net-negative over a rolling window is a SCORING
problem (the regime is wrong for this pair right now), not a STRUCTURAL
one (the pair can't physically be traded).  The right tool is a confidence
deduction that decays as the pair recovers, not a permanent exclusion.

Mechanics
---------

1. ``set_tracker(tracker)`` is called once at bootstrap with the engine's
   :class:`PerformanceTracker`.  Without a tracker the module is a no-op
   (``get(symbol)`` returns 0.0 for every symbol — safe fallback for
   tests / dry-run modes).
2. ``get(symbol)`` returns the current penalty (positive float; callers
   subtract it from confidence via the existing ``soft_penalty``
   accumulator in ``scanner/__init__.py``).
3. The cache refreshes lazily on ``get()`` calls — first call after the
   refresh interval expires re-aggregates the tracker.  No background
   thread needed; the scan loop drives refresh naturally.
4. Aggregation: group :class:`SignalRecord` entries by ``symbol`` for the
   trailing ``PAIR_PENALTY_WINDOW_DAYS``, require >=
   ``PAIR_PENALTY_MIN_SAMPLE`` records to apply (small-sample noise
   guard), compute mean ``pnl_pct``.  Negative mean → penalty.

Formula
-------

::

    raw_penalty = max(0, -mean_pnl_pct * PAIR_PENALTY_SCALE)
    penalty     = min(raw_penalty, PAIR_PENALTY_CAP_PTS)

Default calibration (env-overridable):

* ``PAIR_PENALTY_SCALE = 23.0``  — pair with mean raw pnl of −0.65%
  (matches ENA in the 2026-05-17 audit at 10× margin = −6.5% NET) gets
  ~15 confidence pts subtracted.
* ``PAIR_PENALTY_CAP_PTS = 20.0``  — hard ceiling so a catastrophic
  pair can't single-handedly push a 75-confidence signal to 50 — the
  six-dimension scoring + other soft penalties still drive the
  decision.
* ``PAIR_PENALTY_MIN_SAMPLE = 5``  — under this many records in the
  window the noise dominates the signal; pair gets no penalty
  (default behaviour).
* ``PAIR_PENALTY_WINDOW_DAYS = 28``  — matches the audit window.  A
  pair that's been bad for 4 weeks gets penalised; if it turns
  positive over the next 4 weeks the penalty decays naturally.

All thresholds are env-overridable per B8.

Telemetry hook
--------------

The scanner caller tags the contribution as ``pair_perf`` in
``_soft_penalty_by_type`` so the truth report's soft-penalty breakdown
shows how much of the cumulative confidence reduction came from
per-pair vs other gates.
"""
from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("pair_penalty")

# ---------------------------------------------------------------------------
# Tunables — all env-overridable per B8.
# ---------------------------------------------------------------------------

# Rolling window for per-pair PnL aggregation.  Matches the 2026-05-17
# 654-signal audit window (2026-04-21 → 2026-05-17 = ~26 days).
_WINDOW_DAYS: float = float(os.getenv("PAIR_PENALTY_WINDOW_DAYS", "28"))

# Minimum classified records a pair must have in the window before any
# penalty applies.  Below this, mean PnL is noise.
_MIN_SAMPLE: int = int(os.getenv("PAIR_PENALTY_MIN_SAMPLE", "5"))

# Confidence-points-per-raw-percent-PnL multiplier.  Calibrated so that
# the audit's worst pair (ENA, raw mean ≈ −0.65%) gets ~15 pts penalty.
_SCALE: float = float(os.getenv("PAIR_PENALTY_SCALE", "23.0"))

# Hard cap on the penalty.  A pair with catastrophic recent history
# shouldn't single-handedly tank a high-confluence signal — the
# six-dimension scoring + family thesis + HTF penalty still drive the
# main decision.
_CAP: float = float(os.getenv("PAIR_PENALTY_CAP_PTS", "20.0"))

# Lazy-refresh TTL (seconds).  300s = 5 min — well below the audit
# window's resolution and well above the per-scan-tick cost of
# re-aggregating ~500 records.
_REFRESH_TTL_SEC: float = float(os.getenv("PAIR_PENALTY_REFRESH_SEC", "300"))


# ---------------------------------------------------------------------------
# Module state.  Single-process engine; module-level state is fine.
# ---------------------------------------------------------------------------

_TRACKER: Any = None  # PerformanceTracker; typed Any to avoid import cycle
_CACHE: Dict[str, float] = {}
_CACHE_REFRESHED_AT: float = 0.0


def set_tracker(tracker: Any) -> None:
    """Install the engine's :class:`PerformanceTracker` so this module can
    aggregate per-pair PnL on demand.  Called once at bootstrap (see
    :func:`src.main.run`).

    Resetting via this function (e.g. in tests) drops the cache so a
    stale tracker doesn't leak penalty values across instances.
    """
    global _TRACKER, _CACHE, _CACHE_REFRESHED_AT
    _TRACKER = tracker
    _CACHE = {}
    _CACHE_REFRESHED_AT = 0.0


def get(symbol: str, *, now: Optional[float] = None) -> float:
    """Return the current per-pair penalty (positive float) for ``symbol``.

    Returns 0.0 when the module hasn't been wired with a tracker yet
    (e.g. during boot before bootstrap completes), the pair has fewer
    than ``PAIR_PENALTY_MIN_SAMPLE`` records in the window, or the pair
    is net-positive / breakeven.

    The cache refreshes lazily on the first call after
    ``PAIR_PENALTY_REFRESH_SEC`` has elapsed since the last refresh.
    """
    _ensure_fresh(now=now)
    return _CACHE.get(symbol, 0.0)


def snapshot() -> Dict[str, float]:
    """Test / diagnostic helper — returns a shallow copy of the current
    per-pair penalty map."""
    _ensure_fresh()
    return dict(_CACHE)


def force_refresh(*, now: Optional[float] = None) -> Dict[str, float]:
    """Drop the lazy-refresh TTL and re-aggregate immediately.  Used by
    tests + diagnostic endpoints that want a fresh snapshot regardless
    of cache age.
    """
    global _CACHE_REFRESHED_AT
    _CACHE_REFRESHED_AT = 0.0
    _ensure_fresh(now=now)
    return dict(_CACHE)


def _ensure_fresh(*, now: Optional[float] = None) -> None:
    global _CACHE_REFRESHED_AT
    if _TRACKER is None:
        return
    ts = now if now is not None else time.time()
    if ts - _CACHE_REFRESHED_AT < _REFRESH_TTL_SEC:
        return
    _CACHE_REFRESHED_AT = ts
    _refresh(now=ts)


def _refresh(*, now: float) -> None:
    """Aggregate the tracker into a fresh per-pair penalty map and swap
    it into the module-level cache.  Called from ``_ensure_fresh`` on
    TTL expiry — never run synchronously inside the hot scoring path
    on every signal.
    """
    global _CACHE
    if _TRACKER is None:
        return
    cutoff = now - (_WINDOW_DAYS * 86400.0)
    # PerformanceTracker's ``_records`` is module-private but stable
    # across versions per the design notes — we accept the coupling
    # here because adding a public ``records_since(ts)`` method would
    # be a wider refactor.  Tests pin the access pattern.
    records: List[Any] = getattr(_TRACKER, "_records", []) or []
    by_symbol: Dict[str, List[float]] = {}
    for r in records:
        try:
            if float(r.timestamp) < cutoff:
                continue
            sym = str(r.symbol or "")
            if not sym:
                continue
            by_symbol.setdefault(sym, []).append(float(r.pnl_pct))
        except (AttributeError, TypeError, ValueError):
            # Defensive — a malformed record shouldn't break aggregation
            # for the rest.  ``_refresh`` is called from the scoring
            # hot-path; we never want it to raise.
            continue

    new_cache: Dict[str, float] = {}
    for sym, pnls in by_symbol.items():
        if len(pnls) < _MIN_SAMPLE:
            continue
        mean_pnl = sum(pnls) / len(pnls)
        if mean_pnl >= 0.0:
            continue
        raw_penalty = -mean_pnl * _SCALE
        new_cache[sym] = min(_CAP, raw_penalty)

    _CACHE = new_cache
    if new_cache:
        log.info(
            "pair_penalty refresh: {} pairs penalised; worst="
            "{} ({:.2f} pts)",
            len(new_cache),
            *_worst(new_cache),
        )


def _worst(cache: Dict[str, float]) -> tuple:
    """Return ``(symbol, penalty)`` of the worst-penalised pair."""
    if not cache:
        return ("", 0.0)
    worst_sym = max(cache, key=lambda k: cache[k])
    return (worst_sym, cache[worst_sym])


# ---------------------------------------------------------------------------
# Test-only helpers.
# ---------------------------------------------------------------------------

def _reset_state_for_tests() -> None:
    """Wipe module state.  Tests call this between cases so module-level
    caches don't leak across test boundaries.  Not part of the public
    runtime API.
    """
    global _TRACKER, _CACHE, _CACHE_REFRESHED_AT
    _TRACKER = None
    _CACHE = {}
    _CACHE_REFRESHED_AT = 0.0
