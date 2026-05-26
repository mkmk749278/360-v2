"""Per-user paper-mode view via subscription windows (2026-05-23).

The engine runs a single :class:`PaperOrderManager` writing one shared
ledger (``data/paper_trades.sqlite`` + ``data/pnl_history.json``). Per-user
visibility is derived by filtering that ledger to trades closed within
the user's paper-subscription windows (see ``user_paper_subscriptions`` in
``user_overrides``).

Why subscription-windows rather than per-user duplicated rows:

* The engine fires one signal stream — the same paper trade either
  happened or it didn't. Writing N rows per signal (one per active paper
  user) would scale storage as O(signals × users) without changing the
  underlying simulation.
* Subscription windows let multiple users see overlapping engine activity
  while each user's "first enable" cleanly bounds what they ever see.
  Fresh users see nothing (empty windows → nothing matches).
* The pattern composes cleanly with Phase 3 per-user FSM workers: when
  each user gets their own PaperOrderManager instance, the subscription
  windows are simply the per-user instance's lifetime.

Doctrine alignment: per CLAUDE.md "Server-side execution doctrine",
true per-user simulation lands with Phase 3. This module is the
Phase-2.5 bridge so the visibility bug doesn't wait on the full
multi-user execution stack.

Coverage history:

* PR #478 (2026-05-23) — windowed ``/api/trades`` + ``/api/pnl/history``.
* PR #503 (2026-05-26, this module) — extends the same window filter to
  ``/api/auto-mode`` (Trade-tab header + rolling counters), ``/api/positions``
  (open-position list), and ``/api/pulse`` (header today_pnl_usd +
  open_positions count). A fresh user enabling paper mode for the first
  time now sees equity=$1000, 0 open, 0 PnL across every window (matching
  ``/api/trades`` empty list) instead of inheriting the engine-wide
  operator's paper book at signup.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("api.paper_user_view")


SubscriptionWindow = Tuple[str, Optional[str]]


def _coerce_iso(value: Optional[str]) -> Optional[datetime]:
    """Parse a stored ISO-8601 UTC stamp into a tz-aware datetime.

    Returns None on falsy input or malformed payloads. The store writes
    via ``datetime.now(timezone.utc).isoformat()`` so values are always
    tz-aware in normal operation; the defensive coercion is here so a
    hand-edited row can't 500 the API.
    """
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def trade_closed_within_any_window(
    closed_at: Optional[str],
    windows: Iterable[SubscriptionWindow],
) -> bool:
    """Return True when ``closed_at`` falls within any subscription window.

    Open windows (``ended_at`` is None) are treated as open-ended through
    the present moment. Open trades (``closed_at`` is None) are not
    visible — by definition the user can't see PnL until the trade has
    closed.
    """
    closed_dt = _coerce_iso(closed_at)
    if closed_dt is None:
        return False
    for started, ended in windows:
        started_dt = _coerce_iso(started)
        if started_dt is None or closed_dt < started_dt:
            continue
        if ended is None:
            return True
        ended_dt = _coerce_iso(ended)
        if ended_dt is None or closed_dt <= ended_dt:
            return True
    return False


def filter_trades_for_user(
    rows: List[Dict[str, Any]],
    windows: List[SubscriptionWindow],
    *,
    include_open: bool = False,
) -> List[Dict[str, Any]]:
    """Filter engine-ledger trade rows down to those visible to a user.

    ``include_open=True`` lets dashboards mix in still-open positions —
    we admit them when their ``created_at`` (open time) falls within an
    active subscription window. This matches the engine's
    ``trade_records.list_trades(include_open=True)`` semantics: open
    positions sort after closed trades, but are still per-user.
    """
    if not windows:
        return []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if row.get("closed_at"):
            if trade_closed_within_any_window(row.get("closed_at"), windows):
                out.append(row)
        elif include_open:
            # Open trades are visible if their open time fell inside any
            # of the user's windows. Use ``created_at`` as the proxy.
            if trade_closed_within_any_window(row.get("created_at"), windows):
                out.append(row)
    return out


def pnl_history_for_user(
    trade_rows: List[Dict[str, Any]],
    windows: List[SubscriptionWindow],
    *,
    days: int,
) -> Tuple[List[Tuple[str, float]], float, float]:
    """Build the per-user daily PnL series + weekly/monthly aggregates.

    Sums ``net_pnl_usd`` over user-visible closed trades, bucketed by the
    UTC date of ``closed_at``. Days with no visible trades are filled with
    0.0 so the chart x-axis stays contiguous (matches the global
    ``pnl_history.get_history`` shape).

    Returns ``(series, weekly_usd, monthly_usd)`` — the second and third
    are rolling 7/30-day sums from the same source so the per-user view
    is internally consistent.
    """
    days = max(1, int(days))
    visible = filter_trades_for_user(trade_rows, windows, include_open=False)
    buckets: Dict[str, float] = {}
    for row in visible:
        closed_dt = _coerce_iso(row.get("closed_at"))
        if closed_dt is None:
            continue
        date_key = closed_dt.astimezone(timezone.utc).strftime("%Y-%m-%d")
        try:
            pnl = float(row.get("net_pnl_usd") or 0.0)
        except (TypeError, ValueError):
            pnl = 0.0
        buckets[date_key] = round(buckets.get(date_key, 0.0) + pnl, 4)

    today = datetime.now(timezone.utc).date()
    series: List[Tuple[str, float]] = []
    for offset in range(days - 1, -1, -1):
        d = today - timedelta(days=offset)
        key = d.strftime("%Y-%m-%d")
        series.append((key, float(buckets.get(key, 0.0))))

    def _rolling(window_days: int) -> float:
        total = 0.0
        for offset in range(window_days):
            d = today - timedelta(days=offset)
            total += float(buckets.get(d.strftime("%Y-%m-%d"), 0.0))
        return round(total, 4)

    return series, _rolling(7), _rolling(30)



# ---------------------------------------------------------------------------
# Snapshot-builder helpers (PR #503, 2026-05-26)
#
# The ``/api/trades`` + ``/api/pnl/history`` filters above operate on the
# closed-trade row set. The Trade-tab header + open-positions list +
# Pulse header pull from different shapes (engine state dicts, router
# active_signals, AutoModeStatus rolling counters), so they need their
# own thin helpers that route through the same window-filter primitives.
# ---------------------------------------------------------------------------


def _datetime_to_iso(value: Any) -> Optional[str]:
    """Coerce a ``datetime | str | None`` into the ISO-8601 string shape
    the existing ``trade_closed_within_any_window`` helper expects.

    The router's ``Signal`` carries ``dispatch_timestamp`` and
    ``timestamp`` as tz-aware ``datetime`` objects (see
    ``src/channels/base.py:Signal``); the trade-records ledger stores
    ISO strings. This adapter lets both feed into the same window-check
    without duplicating the parse-and-compare logic.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    if isinstance(value, str):
        return value
    return None


def signal_visible_within_any_window(
    timestamp: Any,
    windows: Iterable[SubscriptionWindow],
) -> bool:
    """Return True when a signal's dispatch/open time falls within any
    subscription window.

    Mirrors :func:`trade_closed_within_any_window` but for objects that
    expose a ``datetime`` rather than a ledger row's ISO string. Open
    positions in ``router.active_signals`` are filtered through this so
    a user who enabled paper after the engine had already opened
    positions doesn't see those pre-window positions on their Trade tab.

    Window-fall semantics match the trade-row check exactly: the signal
    is visible iff its dispatch time falls between ``started_at`` and
    ``ended_at`` (inclusive of the start, inclusive of the close on a
    closed window, open-ended on an active window).
    """
    iso = _datetime_to_iso(timestamp)
    return trade_closed_within_any_window(iso, windows)


def rolling_pnl_for_user(
    rows: List[Dict[str, Any]],
    windows: List[SubscriptionWindow],
) -> Dict[str, float]:
    """Return windowed daily / weekly / monthly / total PnL counters.

    Sums ``net_pnl_usd`` over user-visible closed trades, bucketed by
    UTC close-day:

    * ``daily_pnl_usd`` — closed today (UTC).
    * ``weekly_pnl_usd`` — closed in the last 7 UTC days (inclusive).
    * ``monthly_pnl_usd`` — closed in the last 30 UTC days (inclusive).
    * ``total_pnl_usd`` — closed within ANY subscription window
      (i.e. the user's full visible-since-enable cumulative).

    A fresh user with zero subscription windows gets all zeros — the
    correct empty-state for the Trade-tab header right after they
    enable paper mode and before the first engine signal reaches their
    new window.

    Replaces three independent rolling-window sources for paper mode
    that were all engine-wide:
    * ``RiskManager.daily_realised_pnl_usd`` (today)
    * ``pnl_history.get_weekly/get_monthly("paper")`` (rolling 7/30)
    * ``PaperOrderManager.simulated_pnl_total`` (cumulative since boot)

    The returned ``total_pnl_usd`` plays the same role
    ``simulated_pnl_total`` does — but bounded to the user's
    subscription windows rather than the engine's lifetime. The Trade
    tab's "Equity" cell adds this to ``PAPER_STARTING_EQUITY`` to render
    the user's per-user equity figure ($1000 for a fresh enable, drifts
    with their visible PnL thereafter).
    """
    counters = {
        "daily_pnl_usd": 0.0,
        "weekly_pnl_usd": 0.0,
        "monthly_pnl_usd": 0.0,
        "total_pnl_usd": 0.0,
    }
    if not windows:
        return counters

    visible = filter_trades_for_user(rows, windows, include_open=False)
    today = datetime.now(timezone.utc).date()
    # Inclusive-of-today rolling cutoffs match
    # ``pnl_history.get_rolling_window``: ``days=7`` covers today + the
    # six prior days; ``days=30`` covers today + the 29 prior days. The
    # subtraction by ``days - 1`` keeps the user-windowed counters
    # numerically aligned with the engine-wide series the rest of the
    # surface still reads from for live mode.
    week_cutoff = today - timedelta(days=6)
    month_cutoff = today - timedelta(days=29)

    daily = 0.0
    weekly = 0.0
    monthly = 0.0
    total = 0.0
    for row in visible:
        closed_dt = _coerce_iso(row.get("closed_at"))
        if closed_dt is None:
            continue
        try:
            pnl = float(row.get("net_pnl_usd") or 0.0)
        except (TypeError, ValueError):
            continue
        d = closed_dt.astimezone(timezone.utc).date()
        total += pnl
        if d >= month_cutoff:
            monthly += pnl
        if d >= week_cutoff:
            weekly += pnl
        if d == today:
            daily += pnl

    counters["daily_pnl_usd"] = round(daily, 4)
    counters["weekly_pnl_usd"] = round(weekly, 4)
    counters["monthly_pnl_usd"] = round(monthly, 4)
    counters["total_pnl_usd"] = round(total, 4)
    return counters
