"""Per-mode daily-bucketed PnL history ledger.

Doctrine: the daily/weekly/monthly P&L surfaces in the Lumin app
(``_ModePnlCard``, the new dashboard chart) need state that survives
engine restarts and paper↔live mode switches.  Pre-fix, ``RiskManager._daily``
was in-memory only and got rebuilt on every mode switch (per
``main.set_auto_execution_mode``) and every process restart, so:

* Yesterday's P&L vanished on restart — owner reported "we are loosing
  previous day PnL"
* Weekly / monthly P&L couldn't be shown at all
* Restart at 23:55 UTC orphaned the day's loss-budget tracking

This store is the persistent source of truth for closed-trade realised
P&L.  Integration:

  PaperOrderManager.close_*  → pnl_history.record_close("paper", pnl)
  OrderManager.close_*       → pnl_history.record_close("live", pnl)
  build_pulse                → weekly / monthly aggregations from the
                               store
  /api/pnl/history           → daily series for the chart widget

Storage schema (``data/pnl_history.json``)::

    {
      "paper": {"2026-05-08": 12.84, "2026-05-07": -3.20, ...},
      "live":  {"2026-05-08": 0.0, ...}
    }

Atomic write (tmp + rename).  Fail-soft load: any IO / JSON / numeric
error returns an empty store with a warning log.

The store is intentionally thin — no caching, no async — because writes
fire on close-trade events (~15-30/day) and reads fire on snapshot
requests (~1/min).  Re-reading the file on every call is fine at this
cadence and avoids cache-coherency bugs across the
PaperOrderManager / OrderManager / RiskManager / API surfaces.
"""
from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("pnl_history")


_HISTORY_PATH_DEFAULT = "data/pnl_history.json"


def _resolve_history_path() -> Path:
    """Lazy env-var lookup so test fixtures can isolate per-tmp ledger.

    Same pattern used by ``paper_pnl_state.json`` and the active-router
    state file.
    """
    return Path(os.getenv("PNL_HISTORY_PATH", _HISTORY_PATH_DEFAULT))


def _today_str() -> str:
    """Current UTC date as ISO-8601 (``YYYY-MM-DD``)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Load / persist
# ---------------------------------------------------------------------------


def _load_history() -> Dict[str, Dict[str, float]]:
    """Read the per-mode history ledger from disk.

    Returns ``{}`` on any failure (missing file, malformed JSON,
    permission error).  Per-mode dicts are normalised to
    ``Dict[str (date), float (pnl)]`` — entries with non-string dates
    or non-numeric PnL are silently dropped.
    """
    path = _resolve_history_path()
    try:
        with path.open("r") as fp:
            raw = json.load(fp)
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError) as exc:
        log.warning(
            "PnL history ledger corrupt at %s — starting fresh (%s)",
            path, exc,
        )
        return {}
    if not isinstance(raw, dict):
        return {}
    cleaned: Dict[str, Dict[str, float]] = {}
    for mode, buckets in raw.items():
        if not isinstance(mode, str) or not isinstance(buckets, dict):
            continue
        normalised: Dict[str, float] = {}
        for d, pnl in buckets.items():
            if not isinstance(d, str):
                continue
            try:
                normalised[d] = float(pnl)
            except (TypeError, ValueError):
                continue
        cleaned[mode] = normalised
    return cleaned


def _persist_history(state: Dict[str, Dict[str, float]]) -> None:
    """Atomic write (tmp + rename).  Best-effort — IO failures logged
    at WARNING and swallowed; persistence is a UX nicety, not a
    safety-critical invariant."""
    path = _resolve_history_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("w") as fp:
            json.dump(state, fp)
        tmp.replace(path)
    except OSError as exc:
        log.warning(
            "PnL history persist failed at %s: %s — continuing in-memory",
            path, exc,
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def record_close(mode: str, pnl_usd: float, *, when: Optional[date] = None) -> None:
    """Append the realised PnL of a closed trade to today's bucket
    for ``mode``.  Persists synchronously.

    Parameters
    ----------
    mode:
        ``"paper"`` or ``"live"``.  Anything else is accepted but
        creates a bespoke bucket — useful for future modes.
    pnl_usd:
        The realised PnL in USD (positive for win, negative for loss).
    when:
        Override for the date bucket.  Default = current UTC date.
        Used by tests; engine code always uses today.
    """
    if not isinstance(mode, str) or not mode:
        return
    bucket_date = (when or datetime.now(timezone.utc).date()).strftime("%Y-%m-%d")
    state = _load_history()
    mode_bucket = state.setdefault(mode, {})
    mode_bucket[bucket_date] = round(
        float(mode_bucket.get(bucket_date, 0.0)) + float(pnl_usd), 4,
    )
    _persist_history(state)


def get_daily(mode: str, *, on_date: Optional[date] = None) -> float:
    """Realised PnL for a specific UTC date in ``mode`` (default: today)."""
    bucket_date = (on_date or datetime.now(timezone.utc).date()).strftime("%Y-%m-%d")
    state = _load_history()
    return float(state.get(mode, {}).get(bucket_date, 0.0))


def get_rolling_window(mode: str, *, days: int) -> float:
    """Sum of PnL across the last ``days`` UTC days (inclusive of today)."""
    if days <= 0:
        return 0.0
    state = _load_history().get(mode, {})
    today = datetime.now(timezone.utc).date()
    total = 0.0
    for offset in range(days):
        d = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        total += float(state.get(d, 0.0))
    return round(total, 4)


def get_weekly(mode: str) -> float:
    """Last 7 days rolling (inclusive of today)."""
    return get_rolling_window(mode, days=7)


def get_monthly(mode: str) -> float:
    """Last 30 days rolling (inclusive of today).

    Rolling-30 chosen over calendar-month because the engine runs 24/7 —
    "this month so far" misleads on May 2nd.  The chart UI on the app
    side can build calendar-month aggregates from the daily series if a
    future product decision flips that."""
    return get_rolling_window(mode, days=30)


def get_history(
    mode: str, *, days: int = 30
) -> List[Tuple[str, float]]:
    """Daily PnL series for charting, oldest → newest, including zero days.

    Returns a list of ``(date_str, pnl_usd)`` tuples spanning the last
    ``days`` UTC days.  Days with no closed trades are filled with 0.0
    so the chart x-axis is contiguous (gaps would look like data loss).
    """
    if days <= 0:
        return []
    state = _load_history().get(mode, {})
    today = datetime.now(timezone.utc).date()
    series: List[Tuple[str, float]] = []
    for offset in range(days - 1, -1, -1):
        d = today - timedelta(days=offset)
        key = d.strftime("%Y-%m-%d")
        series.append((key, float(state.get(key, 0.0))))
    return series


# ---------------------------------------------------------------------------
# Per-user aggregate readers (2026-06-20) — engine-wide paper view is the SUM
# across every per-user bucket (``paper:<uid>``).  The app reads a single
# user's bucket via the single-mode readers above with mode=``paper:<uid>``;
# the truth report + ops + engine snapshot read the aggregate here.
# ---------------------------------------------------------------------------


def _modes_matching(prefix: str) -> "List[str]":
    state = _load_history()
    return [m for m in state if m == prefix or m.startswith(prefix + ":")]


def _aggregate_buckets(prefix: str) -> Dict[str, float]:
    """Merge every ``<prefix>`` / ``<prefix>:<uid>`` mode into one date→PnL
    bucket dict (engine-wide view of a per-user-namespaced mode)."""
    state = _load_history()
    merged: Dict[str, float] = {}
    for mode, buckets in state.items():
        if mode == prefix or mode.startswith(prefix + ":"):
            for d, v in buckets.items():
                merged[d] = round(merged.get(d, 0.0) + float(v), 4)
    return merged


def get_daily_aggregate(prefix: str, *, on_date: Optional[date] = None) -> float:
    bucket_date = (on_date or datetime.now(timezone.utc).date()).strftime("%Y-%m-%d")
    return float(_aggregate_buckets(prefix).get(bucket_date, 0.0))


def get_rolling_window_aggregate(prefix: str, *, days: int) -> float:
    if days <= 0:
        return 0.0
    merged = _aggregate_buckets(prefix)
    today = datetime.now(timezone.utc).date()
    total = 0.0
    for offset in range(days):
        d = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        total += float(merged.get(d, 0.0))
    return round(total, 4)


def get_weekly_aggregate(prefix: str) -> float:
    return get_rolling_window_aggregate(prefix, days=7)


def get_monthly_aggregate(prefix: str) -> float:
    return get_rolling_window_aggregate(prefix, days=30)


def get_history_aggregate(
    prefix: str, *, days: int = 30
) -> List[Tuple[str, float]]:
    if days <= 0:
        return []
    merged = _aggregate_buckets(prefix)
    today = datetime.now(timezone.utc).date()
    series: List[Tuple[str, float]] = []
    for offset in range(days - 1, -1, -1):
        key = (today - timedelta(days=offset)).strftime("%Y-%m-%d")
        series.append((key, float(merged.get(key, 0.0))))
    return series


def reset_aggregate(prefix: str) -> int:
    """Wipe every per-user bucket for ``prefix`` (``paper`` + ``paper:*``)."""
    state = _load_history()
    cleared = 0
    for mode in [m for m in state if m == prefix or m.startswith(prefix + ":")]:
        cleared += len(state.get(mode) or {})
        state[mode] = {}
    _persist_history(state)
    log.info(
        "pnl_history.reset_aggregate: cleared {} buckets across prefix={}",
        cleared, prefix,
    )
    return cleared


def reset_mode(mode: str) -> int:
    """Wipe every daily bucket for ``mode`` and persist atomically.

    Returns the number of buckets that were cleared — telemetry for the
    ``POST /api/auto-mode/paper/reset`` log line so the operator can
    confirm the reset actually had work to do.

    Other modes' ledgers are untouched: a paper reset never touches
    ``live`` history, so the operator can flip back to live and see
    the pre-reset live performance intact.

    Idempotent — calling on an already-empty mode is a no-op that
    returns 0.
    """
    if not isinstance(mode, str) or not mode:
        return 0
    state = _load_history()
    bucket = state.get(mode) or {}
    cleared = len(bucket)
    state[mode] = {}
    _persist_history(state)
    log.info(
        "pnl_history.reset_mode: cleared {} daily buckets for mode={}",
        cleared, mode,
    )
    return cleared
