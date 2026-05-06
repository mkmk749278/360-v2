"""One-shot backfill of `_signal_history` from the engine's pre-existing
durable record sources.

Why this exists
---------------
PR #299 added persistence for the API-facing `_signal_history` list, but
the file `data/signal_history.json` only starts populating from the next
terminal-state transition after that PR shipped.  Every signal the engine
posted to Telegram in the months prior is gone from the app's view —
they were held in-memory only and got wiped on every redeploy.

Owner-visible problem (confirmed via `/api/signals?status=all` returning
`{"items":[],"total":0}` immediately after the PR #299 / #301 / #302 /
#303 deploy): the Lumin app shows "No signals yet" + "Stats last 24h
all zero / Last fired: never" across every agent.  Subscriber-honest
state, but it omits months of real activity.

Two existing structured sources hold most of what we need:

* ``data/signal_performance.json`` — :class:`PerformanceTracker` records
  every closed signal with: signal_id, channel, symbol, direction, entry,
  stop_loss, tp1, hit_tp / hit_sl, pnl_pct, confidence, setup_class,
  quality_tier, and timestamps.  Persisted across restarts pre-PR-299.

* ``data/invalidation_records.json`` — :class:`InvalidationAudit` records
  every kill: signal_id, entry, stop_loss, tp1, kill_price, kill_reason,
  pnl_pct_at_kill, plus post-kill PROTECTIVE/PREMATURE/NEUTRAL labelling.

Combined, these cover essentially every terminal-state outcome the engine
has produced.  They lack some fields (TP2, TP3, full ATR context) but
the API surface only needs the displayed bits anyway.

Usage
-----
:meth:`backfill_from_legacy_sources` returns a list of :class:`Signal`
objects ready to extend ``_signal_history``.  No-op when both source
files are absent.  Best-effort — malformed records are skipped with a
warning, never crash boot.

The boot path in ``main.py`` invokes this iff ``load_history()`` returned
empty AND legacy sources have data — so once a real `signal_history.json`
exists, this never runs again.  Idempotent within a single boot but not
re-applied across boots.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .channels.base import Signal
from .signal_history_store import HISTORY_CAP
from .smc import Direction
from .utils import get_logger

log = get_logger(__name__)


_DEFAULT_PERF_PATH = "data/signal_performance.json"
_DEFAULT_INVAL_PATH = "data/invalidation_records.json"
_DEFAULT_DISPATCH_PATH = "data/dispatch_log.json"


def _build_dispatch_index(
    path: str = _DEFAULT_DISPATCH_PATH,
) -> Dict[str, Dict[str, float]]:
    """Build a {signal_id: {entry, sl, tp1, tp2, tp3}} index from dispatch_log.

    The dispatch log is the only store that captures the **full** original
    geometry of every signal at the moment it was sent to Telegram.
    PerformanceTracker only stores entry+SL (TP prices are aggregated as hit
    counts, not preserved per-record); InvalidationAudit stores entry+SL+TP1
    only.  As a result, app history rows for older signals show TP1=0 / TP2=0
    / TP3=null even though the original signal had real TPs.

    This index is used in two ways:
    1. During first-boot backfill — fill TPs that the perf/invalidation
       record didn't carry.
    2. During reconciliation on every boot — repair already-archived
       Signal objects in `_signal_history` whose TPs are 0/None but whose
       signal_id matches a dispatch_log entry.

    Returns an empty dict when the file is absent or unreadable.
    """
    raw = _load_json_array(Path(path))
    index: Dict[str, Dict[str, float]] = {}
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        sid = (entry.get("signal_id") or "").strip()
        if not sid:
            continue
        try:
            geometry: Dict[str, float] = {}
            if entry.get("entry") is not None:
                geometry["entry"] = float(entry["entry"])
            if entry.get("sl") is not None:
                geometry["sl"] = float(entry["sl"])
            for k in ("tp1", "tp2", "tp3"):
                v = entry.get(k)
                if v is not None:
                    geometry[k] = float(v)
        except (TypeError, ValueError):
            continue
        if geometry:
            index[sid] = geometry
    return index


def _to_datetime(value: Any) -> Optional[datetime]:
    """Coerce a unix-float, ISO string, or None into a tz-aware datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)) and value > 0:
        return datetime.fromtimestamp(float(value), tz=timezone.utc)
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    return None


def _to_direction(value: Any) -> Direction:
    if isinstance(value, Direction):
        return value
    s = (value or "LONG")
    s = s if isinstance(s, str) else str(s)
    return Direction.SHORT if s.upper() == "SHORT" else Direction.LONG


def _status_from_perf(record: Dict[str, Any]) -> str:
    """Mirror ``classify_trade_outcome`` → SignalDetail.status semantics."""
    label = (record.get("outcome_label") or "").strip()
    if label:
        # Already classified by performance_tracker.  Trust it.
        return label
    hit_tp = int(record.get("hit_tp", 0) or 0)
    hit_sl = bool(record.get("hit_sl", False))
    if hit_tp >= 3 and not hit_sl:
        return "FULL_TP_HIT"
    if hit_sl:
        return "SL_HIT"
    if hit_tp > 0:
        return f"TP{hit_tp}_HIT"
    return "CLOSED"


def _signal_from_perf_dict(
    record: Dict[str, Any],
    *,
    dispatch_index: Optional[Dict[str, Dict[str, float]]] = None,
) -> Optional[Signal]:
    """Build a Signal from a PerformanceTracker JSON record.

    Defensive: missing required fields → return None rather than crash.

    When ``dispatch_index`` is supplied, missing tp2/tp3 (and tp1 if absent
    from the perf record) are filled from the dispatch log, which is the
    only store that captures the full original geometry of every signal.
    """
    signal_id = (record.get("signal_id") or "").strip()
    symbol = (record.get("symbol") or "").strip()
    if not signal_id or not symbol:
        return None
    try:
        entry = float(record.get("entry", 0.0) or 0.0)
        sl = float(record.get("stop_loss", 0.0) or 0.0)
        tp1 = float(record.get("tp1", 0.0) or 0.0)
    except (TypeError, ValueError):
        return None
    if entry <= 0:
        return None

    tp2 = 0.0
    tp3: Optional[float] = None
    if dispatch_index is not None:
        geom = dispatch_index.get(signal_id)
        if geom:
            if tp1 <= 0 and "tp1" in geom:
                tp1 = geom["tp1"]
            if "tp2" in geom:
                tp2 = geom["tp2"]
            if "tp3" in geom:
                tp3 = geom["tp3"]

    create_ts = _to_datetime(record.get("create_timestamp"))
    dispatch_ts = _to_datetime(record.get("dispatch_timestamp"))
    terminal_ts = _to_datetime(record.get("terminal_outcome_timestamp"))
    timestamp = create_ts or dispatch_ts or terminal_ts or datetime.now(timezone.utc)

    return Signal(
        channel=record.get("channel", "") or "",
        symbol=symbol,
        direction=_to_direction(record.get("direction")),
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        signal_id=signal_id,
        setup_class=record.get("setup_class", "") or "",
        confidence=float(record.get("confidence", 0.0) or 0.0),
        quality_tier=record.get("quality_tier", "B") or "B",
        status=_status_from_perf(record),
        pnl_pct=float(record.get("pnl_pct", 0.0) or 0.0),
        timestamp=timestamp,
        dispatch_timestamp=dispatch_ts,
        terminal_outcome_timestamp=terminal_ts,
        first_sl_touch_timestamp=_to_datetime(
            record.get("first_sl_touch_timestamp")
        ),
        first_tp_touch_timestamp=_to_datetime(
            record.get("first_tp_touch_timestamp")
        ),
    )


def _signal_from_invalidation_dict(
    record: Dict[str, Any],
    *,
    dispatch_index: Optional[Dict[str, Dict[str, float]]] = None,
) -> Optional[Signal]:
    """Build a Signal from an InvalidationRecord JSON record.

    ``dispatch_index`` lookup fills tp2/tp3 (and tp1 if absent), since
    InvalidationAudit only stores entry/SL/TP1.
    """
    signal_id = (record.get("signal_id") or "").strip()
    symbol = (record.get("symbol") or "").strip()
    if not signal_id or not symbol:
        return None
    try:
        entry = float(record.get("entry", 0.0) or 0.0)
        sl = float(record.get("stop_loss", 0.0) or 0.0)
        tp1 = float(record.get("tp1", 0.0) or 0.0)
        kill_price = float(record.get("kill_price", entry) or entry)
        pnl_pct = float(record.get("pnl_pct_at_kill", 0.0) or 0.0)
    except (TypeError, ValueError):
        return None
    if entry <= 0:
        return None

    tp2 = 0.0
    tp3: Optional[float] = None
    if dispatch_index is not None:
        geom = dispatch_index.get(signal_id)
        if geom:
            if tp1 <= 0 and "tp1" in geom:
                tp1 = geom["tp1"]
            if "tp2" in geom:
                tp2 = geom["tp2"]
            if "tp3" in geom:
                tp3 = geom["tp3"]

    kill_ts = _to_datetime(record.get("kill_timestamp"))
    timestamp = kill_ts or datetime.now(timezone.utc)
    return Signal(
        channel=record.get("channel", "") or "",
        symbol=symbol,
        direction=_to_direction(record.get("direction")),
        entry=entry,
        stop_loss=sl,
        tp1=tp1,
        tp2=tp2,
        tp3=tp3,
        signal_id=signal_id,
        setup_class=record.get("setup_class", "") or "",
        status="INVALIDATED",
        current_price=kill_price,
        pnl_pct=pnl_pct,
        # Use kill_timestamp as both timestamp and terminal_outcome_timestamp
        # so the app's "minutes since terminal" math works correctly and the
        # 24h lifecycle counters in build_agents see the kill.
        timestamp=timestamp,
        terminal_outcome_timestamp=kill_ts,
    )


def _load_json_array(path: Path) -> List[Dict[str, Any]]:
    """Best-effort load of a JSON array file.  Empty list on any failure."""
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        log.warning("signal_history_backfill: load %s failed (%s)", path, e)
        return []
    if not isinstance(data, list):
        log.warning("signal_history_backfill: %s is not a list", path)
        return []
    return [r for r in data if isinstance(r, dict)]


def backfill_from_legacy_sources(
    *,
    perf_path: str = _DEFAULT_PERF_PATH,
    invalidation_path: str = _DEFAULT_INVAL_PATH,
    dispatch_path: str = _DEFAULT_DISPATCH_PATH,
) -> List[Signal]:
    """Reconstruct a `_signal_history`-shaped list from legacy sources.

    Records are de-duplicated by ``signal_id``.  When the same signal_id
    appears in both files we keep the **performance_tracker** record
    because it carries the richer field set (timestamps, tier, etc.).
    Sorted by ``timestamp`` descending, capped at :data:`HISTORY_CAP`
    to mirror the in-memory cap.

    ``dispatch_path`` is consulted to fill TP2/TP3 (and TP1 if absent)
    that the perf/invalidation records don't store — without this the
    app shows TP1=0/TP2=0/TP3=null on every backfilled row.

    Returns an empty list when both source files are absent or unreadable
    — the caller can use that as a "nothing to backfill" signal.
    """
    perf_records = _load_json_array(Path(perf_path))
    inval_records = _load_json_array(Path(invalidation_path))
    dispatch_index = _build_dispatch_index(dispatch_path)

    by_id: Dict[str, Signal] = {}

    # Invalidation first so performance overwrites on collision.
    for r in inval_records:
        sig = _signal_from_invalidation_dict(r, dispatch_index=dispatch_index)
        if sig is None:
            continue
        by_id[sig.signal_id] = sig

    perf_overrides = 0
    for r in perf_records:
        sig = _signal_from_perf_dict(r, dispatch_index=dispatch_index)
        if sig is None:
            continue
        if sig.signal_id in by_id:
            perf_overrides += 1
        by_id[sig.signal_id] = sig

    if not by_id:
        return []

    merged = list(by_id.values())
    # Most-recent-first; cap to mirror save_history()'s behaviour.
    merged.sort(
        key=lambda s: s.timestamp or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    capped = merged[:HISTORY_CAP]

    log.info(
        "signal_history_backfill: reconstructed %d signals "
        "(perf=%d, invalidation=%d, perf_overrides=%d, capped_to=%d)",
        len(capped), len(perf_records), len(inval_records),
        perf_overrides, HISTORY_CAP,
    )
    return capped


def reconcile_invalidation_status(
    history: List[Signal],
    *,
    invalidation_path: str = _DEFAULT_INVAL_PATH,
) -> int:
    """Repair ``Signal.status`` against ``invalidation_records.json``.

    Background — bug compounded across two layers:

    1. ``trade_monitor._record_outcome`` historically derived
       ``outcome_label`` purely from ``(hit_tp, hit_sl, expired)`` via
       ``classify_trade_outcome``.  Invalidations call it with
       ``hit_tp=0, hit_sl=False, expired=False`` → label ``"CLOSED"``,
       even though ``sig.status`` was set to ``"INVALIDATED"`` two lines
       earlier.  Result: every historical perf record for an
       invalidation says ``outcome_label="CLOSED"``.
    2. The backfill (PR #304) prefers perf record over invalidation
       record on collision (richer fields), so the wrong ``"CLOSED"``
       label overwrites the correct ``"INVALIDATED"`` from the
       audit log.  Subscribers see "CLOSED" in the Lumin app's All
       view but nothing in the Invalidated sub-filter.

    This reconciliation reads ``invalidation_records.json`` (the
    authoritative truth source for invalidations — written by
    ``trade_monitor`` directly with the kill semantics) and forces
    every matching ``signal_id`` in *history* to ``status="INVALIDATED"``,
    syncing ``current_price`` to ``kill_price``, ``pnl_pct`` to
    ``pnl_pct_at_kill``, and ``terminal_outcome_timestamp`` to
    ``kill_timestamp``.

    Idempotent — runs every boot, only mutates when something is wrong.
    Safe to call after ``load_history()`` and after
    ``backfill_from_legacy_sources``.

    Returns the count of records mutated so the caller can decide
    whether to re-flush via ``save_history``.
    """
    inval_records = _load_json_array(Path(invalidation_path))
    inval_by_id: Dict[str, Dict[str, Any]] = {
        r["signal_id"]: r
        for r in inval_records
        if isinstance(r, dict) and r.get("signal_id")
    }
    if not inval_by_id:
        return 0

    fixed = 0
    for sig in history:
        sid = getattr(sig, "signal_id", "") or ""
        if not sid or sid not in inval_by_id:
            continue
        if (getattr(sig, "status", "") or "").upper() == "INVALIDATED":
            continue

        inval = inval_by_id[sid]
        sig.status = "INVALIDATED"

        kill_price = inval.get("kill_price")
        if kill_price is not None:
            try:
                sig.current_price = float(kill_price)
            except (TypeError, ValueError):
                pass

        pnl = inval.get("pnl_pct_at_kill")
        if pnl is not None:
            try:
                sig.pnl_pct = float(pnl)
            except (TypeError, ValueError):
                pass

        kill_ts = _to_datetime(inval.get("kill_timestamp"))
        if kill_ts is not None:
            sig.terminal_outcome_timestamp = kill_ts

        fixed += 1

    if fixed:
        log.info(
            "signal_history reconciliation: corrected %d records to status=INVALIDATED",
            fixed,
        )
    return fixed


def reconcile_missing_tps(
    history: List[Signal],
    *,
    dispatch_path: str = _DEFAULT_DISPATCH_PATH,
) -> int:
    """Patch missing TP prices on already-archived signals.

    Walks ``history`` and, for any signal whose ``tp1``/``tp2``/``tp3``
    are unset (0.0 / None) but whose ``signal_id`` matches a
    ``dispatch_log.json`` entry, fills in the original geometry from
    that dispatch log.

    Why: PerformanceTracker only stores entry+SL.  InvalidationAudit
    stores entry+SL+TP1.  Neither stores TP2 or TP3.  Signals archived
    into ``_signal_history`` before PR #299 (in-memory only) were
    backfilled from these two stores and so came in with TP2=0 / TP3=null
    — the app shows "TP1 0.00 / TP3 0.00" on those rows.  The dispatch
    log keeps the full original geometry indexed by signal_id and is
    the only source of truth for those missing values.

    Idempotent: a signal whose TPs are already populated is left alone.
    Returns the number of signals mutated so the caller can decide
    whether to re-flush via ``save_history``.
    """
    dispatch_index = _build_dispatch_index(dispatch_path)
    if not dispatch_index:
        return 0

    fixed = 0
    for sig in history:
        sid = getattr(sig, "signal_id", "") or ""
        if not sid or sid not in dispatch_index:
            continue
        geom = dispatch_index[sid]

        mutated = False
        if (getattr(sig, "tp1", 0.0) or 0.0) <= 0 and "tp1" in geom:
            sig.tp1 = geom["tp1"]
            mutated = True
        if (getattr(sig, "tp2", 0.0) or 0.0) <= 0 and "tp2" in geom:
            sig.tp2 = geom["tp2"]
            mutated = True
        if getattr(sig, "tp3", None) in (None, 0, 0.0) and "tp3" in geom:
            sig.tp3 = geom["tp3"]
            mutated = True
        if mutated:
            fixed += 1

    if fixed:
        log.info(
            "signal_history_backfill: reconcile_missing_tps patched %d signals",
            fixed,
        )
    return fixed


__all__ = [
    "backfill_from_legacy_sources",
    "reconcile_invalidation_status",
    "reconcile_missing_tps",
]
