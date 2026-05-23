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
