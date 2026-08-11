"""Delivered-signal track record — the recorded book, reduced for subscribers.

The owner's problem, restated from the ops page this ports (2026-07-28): a
per-user paper book **starts empty**, so a new subscriber waits a week to a
month before anything in the app can tell them whether the signals work. The
engine has recorded every closed signal since it was built. This module reduces
that record into a daily series the Lumin app's Pulse tab can render on a user's
first day, before they have taken a single trade.

**Recorded, not reconstructed.** Every row behind these numbers is a signal the
router confirmed, tracked forward in real time by ``trade_monitor`` and written
to ``data/signal_performance.json`` at its terminal transition. Nothing here
replays a candle or rebuilds an outcome after the fact. That line is the whole
reason this module exists rather than pointing the app at ``free_run`` /
``dark_signals`` / ``exit_backtest``, which are counterfactuals, measure ~0.38R
optimistic, and must never wear a track record's name.

**This is NOT the user's own book, and the two must never be reconciled.** The
app's "YOUR PAPER P&L" card reads ``execution/paper_book_registry.py`` — a
per-user ledger that starts empty at enrolment, applies that user's symbol /
path / regime preferences and their own RiskManager on top of router delivery,
sizes at ``min(equity x 2%, $100)`` **compounding**, and books each TP-ladder
partial on its own day. This is every delivered closed signal, pooled, at one
fixed notional, one blended ``pnl_pct`` per row. Different population, different
sizing, different exit accounting. A disagreement between them is not a bug.

Rules carried across from the ops page, each one paid for there:

* **PnL leads and nothing here divides by a stop.** ``signal_dispatch`` sizes at
  a fixed notional (``raw_qty = notional / entry_price``), so the stop distance
  is absent from the sizing and R equalises nothing: a 0.80% loss and a 6.14%
  loss both read -1.00R at $4.00 and $30.70 of the same $500. R also silently
  shrinks its own population — 421 of 448 rows in the owner's 30d window carry
  no ``sl_distance_pct_at_entry``. There is deliberately no R in this payload.
* **The size is an INPUT, never an assumption.** Every dollar figure is
  ``amount * pnl_pct / 100`` — fixed size, no compounding — and ``amount_usdt``
  rides in the response so the reader can never see a dollar without the size
  that produced it.
* **Charge the fee and say what it is.** The owner's 30d window is roughly ten
  times more fee than edge; a gross-only figure answers the wrong question.
  Gross, fee and net all ship, so the split is readable rather than implied.
* **Bucket by CLOSE time.** A day's PnL is the PnL realised that day. Bucketing
  by entry credits Monday with a trade that closed Thursday.
* **A window boundary is not a bucket boundary.** The range start snaps to
  midnight UTC, so the oldest day of a rolling window is a whole day and not a
  fragment rendering as one. Today is still partial by construction, so it is
  stamped ``in_progress`` rather than left to read as finished.
* **Refuse, don't clamp.** A row with no readable ``pnl_pct`` is counted in the
  trade count and excluded from every money figure, and the shortfall is
  reported. Neither is scored zero.
* **Disclose concentration.** Overlapping entries into one move resolve at the
  same exit and are not independent evidence, so the distinct-move count ships
  beside the trade count. Nothing is de-duplicated — that judgement is the
  reader's, and counting them silently is what this discloses against.

``tests/test_track_record.py`` pins the reducers against a shared vector that is
byte-identical to 360ce-ops' ``tests/test_track_record_contract.py``. Ops has
rendered these same numbers since 2026-07-28; two surfaces under one name
computing two different books already cost this system a session, and a shared
vector is what stops the app and the owner's dashboard drifting apart.
"""
from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("track_record")

#: Where ``PerformanceTracker`` persists the closed-signal record. Both the
#: engine and the isolated ``api`` container mount ``/app/data``, so this one
#: path works in single-process and isolated mode alike — which is why this
#: module reads the file rather than reaching through the engine facade.
DEFAULT_RECORD_PATH = "data/signal_performance.json"

#: Same clustering threshold as ``sar_exit_shadow`` and the ops page. Two
#: entries into one move within this percentage of each other are one move.
SAME_MOVE_PCT = 0.5

#: The notional a dollar figure assumes when the caller does not say. Matches
#: the ops page's default and the engine's own meaning of ``notional``.
DEFAULT_AMOUNT_USDT = 100.0

#: Round trip, both legs, as a percentage of notional. Binance USD-M maker
#: 0.02% in + taker 0.05% out. ``0`` renders the gross book.
DEFAULT_FEE_PCT = 0.07

#: Bounds on the window a caller may ask for.
MIN_DAYS = 1
MAX_DAYS = 365


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _parse_ts(value: Any) -> Optional[datetime]:
    """Engine timestamps are epoch floats; tolerate ISO strings defensively."""
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if value <= 0:
            return None
        try:
            return datetime.fromtimestamp(float(value), tz=timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return None


def close_time(rec: Dict[str, Any]) -> Optional[datetime]:
    """When the PnL was realised.

    ``terminal_outcome_timestamp`` is the close. ``timestamp`` is when the
    record was written, the same moment in practice and the only field older
    rows are guaranteed to carry. ``create_timestamp`` is the **entry** and is
    deliberately last: bucketing a day's PnL by entry credits Monday with a
    trade that closed on Thursday.
    """
    return (
        _parse_ts(rec.get("terminal_outcome_timestamp"))
        or _parse_ts(rec.get("timestamp"))
        or _parse_ts(rec.get("create_timestamp"))
    )


def _f(value: Any) -> Optional[float]:
    """Float or None — never 0.0 as a stand-in for "could not read this"."""
    if value is None or isinstance(value, bool):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    if out != out or out in (float("inf"), float("-inf")):
        return None
    return out


def floor_day(when: datetime) -> datetime:
    """Midnight UTC of the day ``when`` falls in."""
    return when.replace(hour=0, minute=0, second=0, microsecond=0)


def money(pct: Optional[float], amount: float) -> Optional[float]:
    """A percentage of the entered notional, in dollars.

    The engine sizes at a fixed notional, so a percentage move on a fixed size
    is exactly linear in the amount. That linearity is what makes this a
    multiplication rather than a model.
    """
    return None if pct is None else amount * pct / 100.0


def distinct_moves(rows: List[Dict[str, Any]]) -> int:
    """How many distinct moves these rows describe.

    Greedy single-pass clustering per ``(symbol, direction)``, oldest first: a
    row opens a new move unless it sits within ``SAME_MOVE_PCT`` of the move
    currently open on that key. Anchored on the open move rather than the
    previous row, so a slow walk cannot drift arbitrarily far and still count
    as one move.

    Disclosure, not de-duplication — no row is dropped, and every average still
    covers every row.
    """
    open_move: Dict[Tuple[str, str], float] = {}
    moves = 0
    for row in sorted(rows, key=lambda r: r.get("closed_at_ts") or 0.0):
        key = (str(row.get("symbol", "")), str(row.get("direction", "")))
        entry = _f(row.get("entry"))
        if entry is None or entry <= 0:
            continue
        anchor = open_move.get(key)
        if anchor is not None and abs(entry - anchor) / anchor * 100.0 < SAME_MOVE_PCT:
            continue
        open_move[key] = entry
        moves += 1
    return moves


def reduce_records(records: Any) -> List[Dict[str, Any]]:
    """Flatten the closed-signal record into display rows (pure).

    Rows carry their own close timestamp so every downstream consumer reads one
    definition of it rather than re-deriving it. A row with no usable close
    time keeps its place here — it is counted in ``undateable`` rather than
    silently dropped — and lands in no bucket.
    """
    out: List[Dict[str, Any]] = []
    rows = records if isinstance(records, list) else []
    for rec in rows:
        if not isinstance(rec, dict):
            continue
        closed = close_time(rec)
        out.append({
            # ``signal_id`` is the JOIN KEY across every measurement lane in
            # this engine, and leaving it off an export once turned a one-line
            # coverage check into a session of matching on rounded prices.
            "signal_id": str(rec.get("signal_id", "")),
            "symbol": str(rec.get("symbol", "")),
            "direction": str(rec.get("direction", "")).upper(),
            "setup": str(rec.get("setup_class") or "UNKNOWN"),
            # The regime at ENTRY. Knowable only at entry, so records closed
            # before the engine stamped it read UNPLACED rather than being
            # handed a guess — there is no honest backfill.
            "regime": str(rec.get("entry_regime") or "").strip() or "UNPLACED",
            "outcome": str(rec.get("outcome_label") or ""),
            "entry": rec.get("entry"),
            "pnl_pct": rec.get("pnl_pct"),
            "closed_at": closed,
            "closed_at_ts": closed.timestamp() if closed else None,
        })
    out.sort(key=lambda r: r.get("closed_at_ts") or 0.0, reverse=True)
    return out


def summarize(
    rows: List[Dict[str, Any]],
    *,
    amount: float = DEFAULT_AMOUNT_USDT,
    fee_pct: float = DEFAULT_FEE_PCT,
) -> Dict[str, Any]:
    """Headline over whatever was selected, in money and in percent.

    Two denominators, kept apart on purpose:

    * ``n`` — every selected trade.
    * ``n_pnl`` — those carrying a readable ``pnl_pct``. Every figure below
      divides by **this**, and ``no_pnl`` states the gap so a caller can say on
      screen when the two differ.

    The win rate counts on the **net** money: a trade that made less than its
    own round trip did not make money, and calling it a win is how a fee-sized
    edge reads as a winning book.
    """
    gross = [p for p in (_f(r.get("pnl_pct")) for r in rows) if p is not None]
    net = [p - fee_pct for p in gross]
    wins = sum(1 for p in net if p > 0)
    moves = distinct_moves(rows)
    return {
        "n": len(rows),
        "moves": moves,
        "n_pnl": len(gross),
        "no_pnl": len(rows) - len(gross),
        "wins": wins,
        "losses": len(net) - wins,
        "win_rate": (wins / len(net)) if net else None,
        # Money, at the size the caller entered.
        "gross_usd": money(sum(gross), amount) if gross else None,
        "fee_usd": (amount * fee_pct / 100.0 * len(gross)) if gross else None,
        "net_usd": money(sum(net), amount) if net else None,
        # The same book as percentages, size-independent.
        "total_pnl_pct": sum(gross) if gross else None,
        "avg_pnl_pct": (sum(gross) / len(gross)) if gross else None,
        "total_net_pct": sum(net) if net else None,
        "avg_net_pct": (sum(net) / len(net)) if net else None,
        "best_pnl_pct": max(gross) if gross else None,
        "worst_pnl_pct": min(gross) if gross else None,
    }


def bucket_days(
    rows: List[Dict[str, Any]],
    *,
    amount: float = DEFAULT_AMOUNT_USDT,
    fee_pct: float = DEFAULT_FEE_PCT,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Group into UTC calendar days, **oldest first** (chart order).

    Each day carries the same summary shape as the headline, so a day and the
    total are never computed two different ways.

    ``partial_reason`` is ``in_progress`` on the day containing ``now`` and
    ``None`` everywhere else. A part-period rendering as a whole one already
    flipped a sign on the ops page once — a rolling window cut 8 of 11 trades
    off a day and the surviving 3, all winners, rendered as that day's result.
    The range start snaps to midnight here so the *oldest* day cannot be cut;
    today is partial by construction and says so.

    Days with no closed trade are **not** filled in. An empty day is not a
    zero-PnL day — nothing closed — and inventing a point for it would draw a
    flat segment the book never traded. The caller has the range start and can
    space the series by date.
    """
    now = now or datetime.now(tz=timezone.utc)
    today_key = floor_day(now).strftime("%Y-%m-%d")
    grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        when = row.get("closed_at")
        if when is None:
            continue
        grouped[when.strftime("%Y-%m-%d")].append(row)

    out: List[Dict[str, Any]] = []
    cum_usd = 0.0
    cum_pct = 0.0
    for key in sorted(grouped):
        bucket = summarize(grouped[key], amount=amount, fee_pct=fee_pct)
        bucket["date"] = key
        bucket["partial_reason"] = "in_progress" if key == today_key else None
        if bucket["net_usd"] is not None:
            cum_usd += bucket["net_usd"]
            cum_pct += bucket["total_net_pct"] or 0.0
        # A day with no readable move did not move the curve, and it is not a
        # gap in the curve either — carry the level forward rather than
        # emitting a null the chart would have to guess about.
        bucket["cum_net_usd"] = cum_usd
        bucket["cum_net_pct"] = cum_pct
        out.append(bucket)
    return out


# ---------------------------------------------------------------------------
# Loading — cached on the file's own identity, never on a bare TTL
# ---------------------------------------------------------------------------

_cache_stamp: Optional[Tuple[str, int, int]] = None
_cache_rows: Optional[List[Dict[str, Any]]] = None


def _stamp(path: str) -> Optional[Tuple[str, int, int]]:
    try:
        st = os.stat(path)
    except OSError:
        return None
    return (path, st.st_mtime_ns, st.st_size)


def load_rows(
    path: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    """Read and reduce the closed-signal record, cached on ``(mtime, size)``.

    ``path`` resolves to ``DEFAULT_RECORD_PATH`` **at call time**, not as a
    default argument. A default argument binds the constant at import, so a
    caller (or a test) that reassigns the module constant would be silently
    ignored — the same "read once, meant every time" shape this repo has paid
    for elsewhere. Production never changes it; the tests must be able to.

    This sits behind a per-request API endpoint every app user hits on every
    Pulse load, so an uncached parse of a multi-megabyte file would be exactly
    the per-request cost the repo's cost rules forbid. The cache is gated on an
    **invalidation signal the writer itself produces** — the file's own mtime
    and size — rather than on a TTL, so a fresh close is visible on the next
    request and a quiet hour costs one ``stat``.

    The reduced book is identical for every caller (it is pooled, not per-user),
    which is what makes one process-wide entry correct rather than a leak.

    Returns ``(rows, error)``. ``error`` is a short reason string, never a
    silent empty list: a missing file and an unreadable one have different
    fixes, and a caller that cannot tell them apart renders "no trades" for
    both.
    """
    global _cache_stamp, _cache_rows

    path = path or DEFAULT_RECORD_PATH
    stamp = _stamp(path)
    if stamp is None:
        # Not a fault on its own: an engine that has closed no signal yet has
        # never written this file. The caller says "no record", not "broken".
        _cache_stamp, _cache_rows = None, None
        return [], "missing"
    if stamp == _cache_stamp and _cache_rows is not None:
        return _cache_rows, None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
    except (OSError, ValueError) as exc:
        log.warning("track record unreadable at %s: %s", path, exc)
        return [], "unreadable"
    if not isinstance(raw, list):
        log.warning("track record at %s is not a list: %s", path, type(raw).__name__)
        return [], "unexpected_shape"
    rows = reduce_records(raw)
    _cache_stamp, _cache_rows = stamp, rows
    return rows, None


def reset_cache() -> None:
    """Drop the loader cache. Tests only — production invalidates on mtime."""
    global _cache_stamp, _cache_rows
    _cache_stamp, _cache_rows = None, None


# ---------------------------------------------------------------------------
# The payload
# ---------------------------------------------------------------------------


def build_track_record(
    *,
    days: int = 30,
    amount: float = DEFAULT_AMOUNT_USDT,
    fee_pct: float = DEFAULT_FEE_PCT,
    path: Optional[str] = None,
    now: Optional[datetime] = None,
    enabled: bool = True,
) -> Dict[str, Any]:
    """The delivered-signal record over the last ``days`` whole UTC days.

    ``enabled=False`` returns the same shape with an empty book, so a caller
    never has to distinguish "switched off" from "failed" by the absence of a
    key. The reason rides in ``unavailable_reason``.
    """
    now = now or datetime.now(tz=timezone.utc)
    days = max(MIN_DAYS, min(int(days), MAX_DAYS))
    amount = max(0.0, float(amount))
    fee_pct = max(0.0, float(fee_pct))

    # Snap to midnight UTC. A preset that started at ``now - N days`` would
    # leave the oldest bucket holding only the tail of that day while rendering
    # identically to a complete one.
    start = floor_day(now - timedelta(days=days))

    empty = {
        "enabled": enabled,
        "unavailable_reason": "",
        "days": days,
        "amount_usdt": amount,
        "fee_pct": fee_pct,
        "range_start": start.strftime("%Y-%m-%d"),
        "generated_at": now.isoformat(),
        "total_records": 0,
        "undateable": 0,
        "summary": summarize([], amount=amount, fee_pct=fee_pct),
        "items": [],
    }
    if not enabled:
        empty["unavailable_reason"] = "disabled"
        return empty

    all_rows, error = load_rows(path)
    if error:
        empty["unavailable_reason"] = error
        return empty

    rows = [
        r for r in all_rows
        if r.get("closed_at") is not None and r["closed_at"] >= start
    ]
    payload = dict(empty)
    payload["total_records"] = len(all_rows)
    payload["undateable"] = sum(1 for r in all_rows if r.get("closed_at") is None)
    payload["summary"] = summarize(rows, amount=amount, fee_pct=fee_pct)
    payload["items"] = bucket_days(rows, amount=amount, fee_pct=fee_pct, now=now)
    return payload


#: A render bound on the per-signal list, applied AFTER filtering, never inside
#: a reducer. Truncating before a filter starves the rarest population hardest
#: — ops learned that when "delivered to users" silently meant "delivered,
#: within the newest 300" of a 2,000-row ledger. The response says when it bit.
SIGNALS_LIMIT = 200


def build_signal_list(
    *,
    days: int = 30,
    date: str = "",
    amount: float = DEFAULT_AMOUNT_USDT,
    fee_pct: float = DEFAULT_FEE_PCT,
    limit: int = SIGNALS_LIMIT,
    path: Optional[str] = None,
    now: Optional[datetime] = None,
    enabled: bool = True,
) -> Dict[str, Any]:
    """The individual closed signals behind the daily buckets.

    This is the drill-down: a reader who sees a red day should be able to ask
    *which signals* made it red, and a headline nobody can open is a claim
    rather than a record.

    ``date`` (``YYYY-MM-DD``, UTC) narrows to one day; empty means the whole
    ``days`` window. The day filter is applied to the **close** time, exactly as
    the buckets are, so the list under a bar is the bar.

    Rows with no readable ``pnl_pct`` are **included** and carry ``null`` money.
    They are part of what closed that day, and omitting them would make the
    list disagree with the count above it — the shortfall is named on the
    summary rather than hidden by dropping rows.
    """
    now = now or datetime.now(tz=timezone.utc)
    days = max(MIN_DAYS, min(int(days), MAX_DAYS))
    amount = max(0.0, float(amount))
    fee_pct = max(0.0, float(fee_pct))
    limit = max(1, min(int(limit), SIGNALS_LIMIT))

    out: Dict[str, Any] = {
        "enabled": enabled,
        "unavailable_reason": "" if enabled else "disabled",
        "days": days,
        "date": date,
        "amount_usdt": amount,
        "fee_pct": fee_pct,
        "matched": 0,
        "truncated": False,
        "items": [],
    }
    if not enabled:
        return out

    all_rows, error = load_rows(path)
    if error:
        out["unavailable_reason"] = error
        return out

    if date:
        rows = [
            r for r in all_rows
            if r.get("closed_at") is not None
            and r["closed_at"].strftime("%Y-%m-%d") == date
        ]
    else:
        start = floor_day(now - timedelta(days=days))
        rows = [
            r for r in all_rows
            if r.get("closed_at") is not None and r["closed_at"] >= start
        ]

    # Newest first — ``reduce_records`` already sorts that way, and a reader
    # opening a day wants the last thing that happened at the top.
    out["matched"] = len(rows)
    out["truncated"] = len(rows) > limit
    out["items"] = [
        {
            "signal_id": r.get("signal_id", ""),
            "symbol": r.get("symbol", ""),
            "direction": r.get("direction", ""),
            "setup": r.get("setup", ""),
            "regime": r.get("regime", ""),
            "outcome": r.get("outcome", ""),
            "entry": _f(r.get("entry")),
            "closed_at": (
                r["closed_at"].isoformat() if r.get("closed_at") else ""
            ),
            "pnl_pct": _f(r.get("pnl_pct")),
            "net_pct": (
                None if _f(r.get("pnl_pct")) is None
                else _f(r.get("pnl_pct")) - fee_pct
            ),
            "net_usd": money(
                None if _f(r.get("pnl_pct")) is None
                else _f(r.get("pnl_pct")) - fee_pct,
                amount,
            ),
        }
        for r in rows[:limit]
    ]
    return out
