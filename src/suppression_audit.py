"""Suppression Quality Audit + shadow ledger (Layer C).

Answers the owner's question — *"is our low signal volume killing GOOD setups, or
correctly suppressing bad ones?"* — with forward-measured data instead of opinion.

At each post-scoring suppression point the scanner **stamps** the killed candidate's
geometry (entry / SL / TP1) into a bounded in-memory buffer.  A periodic loop then
**forward-measures** each stamped candidate against real candles — did price reach TP1
before SL from the stamped entry? — and classifies it WOULD_WIN / WOULD_LOSE /
WOULD_EXPIRE.  Per gate we then get % would-have-won and EV in R-units, yielding a
KEEP / TUNE / DROP verdict per gate.

It also doubles as the **continuous shadow ledger** for the Strategy×Context edge
matrix: every classified candidate is a real-data outcome for its strategy in its
market context, fed to the edge store via an ``on_classified`` callback.

Design (mirrors ``src/invalidation_audit.py`` + ``CohortEdgeStore``):
  * **Hot-path stamp is O(1)** — a ``deque.append`` into a capped buffer, **no file
    or network I/O** (Cost Discipline).  Persistence is batched onto the periodic loop
    (one write / cycle), never per-stamp.
  * **Pure classifier** — independently unit-testable.
  * **Fail-open everywhere** — a stamp/classify error never changes control flow.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any, Callable, Deque, Dict, List, Optional

from src.utils import get_logger

log = get_logger("suppression_audit")

# How long after a suppression to wait before judging the counterfactual.  Matches
# the invalidation audit's 60-min window (scalps run 5-60 min, OWNER_BRIEF §3.2).
_WINDOW_SEC: float = float(os.getenv("SUPPRESSION_AUDIT_WINDOW_SEC", "3600"))
# Bounded rolling sample - this is a measurement, not a complete ledger.
_MAX_RECORDS: int = int(os.getenv("SUPPRESSION_AUDIT_MAX_RECORDS", "5000"))
# Drop classified records older than this so the buffer stays a fresh window.
_RETENTION_SEC: float = float(os.getenv("SUPPRESSION_AUDIT_RETENTION_SEC", str(7 * 24 * 3600)))
_DEFAULT_PATH: str = os.getenv("SUPPRESSION_AUDIT_PATH", "data/suppressed_candidates.json")

# Per-gate ablation verdict thresholds (EV in R per suppression, from the
# suppression's perspective: positive = suppression net-helped).
_KEEP_EV_R: float = float(os.getenv("SUPPRESSION_AUDIT_KEEP_EV_R", "0.10"))
_DROP_EV_R: float = float(os.getenv("SUPPRESSION_AUDIT_DROP_EV_R", "-0.20"))
_MIN_SAMPLE: int = int(os.getenv("SUPPRESSION_AUDIT_MIN_SAMPLE", "20"))

WOULD_WIN = "WOULD_WIN"
WOULD_LOSE = "WOULD_LOSE"
WOULD_EXPIRE = "WOULD_EXPIRE"
# Limit-entry arms only: price never came back to the resting entry, so no
# trade happened.  Scored as 0R in ``candidate_outcome`` — the cost of a
# patient entry IS the fills it misses, and 0R is that cost stated honestly.
WOULD_NOT_FILL = "WOULD_NOT_FILL"
INSUFFICIENT = "INSUFFICIENT_DATA"

# Entry-fill models for stamped candidates.  ``immediate`` (default, all
# historical records): assume entered at the stamped entry the moment of the
# stamp — correct for market-style dispatch.  ``limit``: a resting order at
# ``entry`` that must be TOUCHED by price before TP/SL race — requires the
# candle-walk classifier (``classify_limit_record``) because window extremes
# cannot order fill-vs-target events.
ENTRY_IMMEDIATE = "immediate"
ENTRY_LIMIT = "limit"

VERDICT_KEEP = "KEEP"           # gate correctly suppresses losers
VERDICT_DROP = "DROP"           # gate is killing winners
VERDICT_TUNE = "TUNE"
VERDICT_INSUFFICIENT = "INSUFFICIENT_SAMPLE"


@dataclass
class SuppressedCandidateRecord:
    """A single post-scoring candidate a gate killed, with its would-be geometry.

    Only candidates with tradeable geometry (entry/SL/TP1 all set) are stamped - a
    candidate killed at basic_filters has nothing to counterfactually measure.
    """

    gate_name: str
    setup_class: str
    symbol: str
    channel: str
    side: str                    # LONG | SHORT
    entry: float
    stop_loss: float
    tp1: float
    sl_distance: float
    confidence: float
    context_key: str             # MarketContext.context_key() at suppression
    regime: str
    valid_for_minutes: float
    suppress_timestamp: float
    # Pair-cohort (liquidity tier) for the Phase-5 cohort-refined edge cell —
    # dual-written alongside the base cell so cohort matrices accumulate without
    # fragmenting the base one.
    pair_cohort: str = ""
    # Entry-fill model (ENTRY_IMMEDIATE | ENTRY_LIMIT).  Defaulted so every
    # pre-existing persisted record keeps its original semantics on reload.
    entry_type: str = ENTRY_IMMEDIATE
    # Filled by classify_pending once the window elapses.
    classified_at: Optional[float] = None
    classification: Optional[str] = None
    post_price_max: Optional[float] = None
    post_price_min: Optional[float] = None
    post_price_final: Optional[float] = None


# ---------------------------------------------------------------------------
# Pure classification + R math
# ---------------------------------------------------------------------------


def classify_suppressed_record(
    record: Dict[str, Any],
    post_high: float,
    post_low: float,
    post_final: float = 0.0,
) -> str:
    """Would this suppressed candidate have won (TP1 before SL), lost, or expired?

    Two-sided and conservative: if the post-window extremes breach *both* TP1 and SL
    (OHLC can't resolve intrabar ordering), assume SL-first -> WOULD_LOSE, the same
    defensive bias the live money path uses.  Pure - unit-testable.
    """
    side = str(record.get("side") or "").upper()
    entry = float(record.get("entry") or 0.0)
    tp1 = float(record.get("tp1") or 0.0)
    sl = float(record.get("stop_loss") or 0.0)
    sl_distance = float(record.get("sl_distance") or abs(entry - sl))
    if entry <= 0 or sl_distance <= 0 or tp1 <= 0 or sl <= 0:
        return INSUFFICIENT

    if side == "LONG":
        hit_tp = post_high >= tp1
        hit_sl = post_low <= sl
        if hit_sl:                        # SL-first on ambiguity (conservative)
            return WOULD_LOSE
        if hit_tp:
            return WOULD_WIN
        return WOULD_EXPIRE
    elif side == "SHORT":
        hit_tp = post_low <= tp1
        hit_sl = post_high >= sl
        if hit_sl:
            return WOULD_LOSE
        if hit_tp:
            return WOULD_WIN
        return WOULD_EXPIRE
    return INSUFFICIENT


def classify_limit_record(
    record: Dict[str, Any],
    highs: List[float],
    lows: List[float],
) -> str:
    """Fill-aware counterfactual for a resting-limit entry arm.

    Walks candles in time order: the order fills on the first candle whose
    range touches ``entry``; only from that candle on may TP1/SL count.
    Conservative on every intrabar ambiguity (same bias as
    ``classify_suppressed_record``): a candle that fills AND breaches the stop
    is a loss, regardless of whether it also reached TP1 — OHLC cannot order
    intrabar events and the money path must not be flattered.  Never filled →
    ``WOULD_NOT_FILL``.  Pure — unit-testable.
    """
    side = str(record.get("side") or "").upper()
    entry = float(record.get("entry") or 0.0)
    tp1 = float(record.get("tp1") or 0.0)
    sl = float(record.get("stop_loss") or 0.0)
    sl_distance = float(record.get("sl_distance") or abs(entry - sl))
    if entry <= 0 or sl_distance <= 0 or tp1 <= 0 or sl <= 0:
        return INSUFFICIENT
    if side not in ("LONG", "SHORT") or highs is None or lows is None:
        return INSUFFICIENT
    n = min(len(highs), len(lows))
    if n == 0:
        return INSUFFICIENT

    filled = False
    for i in range(n):
        high = float(highs[i])
        low = float(lows[i])
        if side == "LONG":
            touched = low <= entry
            hit_sl = low <= sl
            hit_tp = high >= tp1
        else:
            touched = high >= entry
            hit_sl = high >= sl
            hit_tp = low <= tp1
        if not filled:
            if not touched:
                continue
            filled = True
            # Touching the limit already implies price traded through toward
            # the stop side; a same-candle stop breach is a fill-then-stop.
            if hit_sl:
                return WOULD_LOSE
            if hit_tp:
                # Range spans entry AND target with the stop intact: the fill
                # is certain and the stop never traded — credit the win (same
                # tp-with-stop-intact rule the immediate classifier applies).
                return WOULD_WIN
            continue
        if hit_sl:
            return WOULD_LOSE
        if hit_tp:
            return WOULD_WIN
    return WOULD_EXPIRE if filled else WOULD_NOT_FILL


def _r_to_tp1(record: Dict[str, Any]) -> float:
    entry = float(record.get("entry") or 0.0)
    tp1 = float(record.get("tp1") or 0.0)
    sl_distance = float(record.get("sl_distance") or 0.0)
    if sl_distance <= 0:
        return 0.0
    return abs(tp1 - entry) / sl_distance


def suppression_value_delta_r(record: Dict[str, Any]) -> Optional[float]:
    """EV of the *suppression* in R (positive = suppressing helped).

    Gross: WOULD_LOSE -> +1.0R saved (stop avoided); WOULD_WIN -> -R_to_TP1 (profit
    forgone); WOULD_EXPIRE -> 0.0.  ``None`` until classified.

    Net (when the cost model is enabled): suppressing also avoids the round-trip
    cost, so a saved loss is worth +(1.0 + cost_R), a forgone win only
    -(R_to_TP1 - cost_R), and a would-expire trade saves its cost (+cost_R).  With
    the model disabled these collapse to the gross values byte-for-byte.
    """
    from src import trade_costs

    cls = record.get("classification")
    if cls not in (WOULD_LOSE, WOULD_WIN, WOULD_EXPIRE):
        return None
    entry = float(record.get("entry") or 0.0)
    sl_distance = float(record.get("sl_distance") or 0.0)
    cost_r = trade_costs.cost_in_r(entry, sl_distance) if trade_costs.is_enabled() else 0.0
    if cls == WOULD_LOSE:
        return 1.0 + cost_r
    if cls == WOULD_WIN:
        return -(_r_to_tp1(record) - cost_r)
    return cost_r  # WOULD_EXPIRE


def candidate_outcome(record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The candidate's own would-be outcome (for the Strategy x Context edge matrix).

    Returns ``{won, pnl_pct, r_multiple, gross_r_multiple, mfe_pct}`` or ``None`` if
    unclassified.  ``r_multiple`` / ``pnl_pct`` are **net of costs** when the cost
    model is enabled; ``gross_r_multiple`` always carries the pre-cost R so the
    W2 reconciliation can show the optimism tax.  ``won`` stays outcome-based
    (reached TP1 before SL) — profitability lives in the netted R, not the flag.
    """
    from src import trade_costs

    cls = record.get("classification")
    entry = float(record.get("entry") or 0.0)
    if not cls or cls == INSUFFICIENT or entry <= 0:
        return None
    if cls == WOULD_NOT_FILL:
        # No fill, no fees, no PnL — the limit recipe's outcome for this
        # candidate is exactly zero, and that zero belongs in its average.
        return {"won": False, "pnl_pct": 0.0, "r_multiple": 0.0,
                "gross_r_multiple": 0.0, "net_r_multiple": 0.0, "mfe_pct": 0.0}
    sl_distance = float(record.get("sl_distance") or 0.0)
    r_tp1 = _r_to_tp1(record)

    if cls == WOULD_WIN:
        gross_r = r_tp1
        won = True
        pnl = abs(float(record.get("tp1", 0.0)) - entry) / entry * 100.0
        mfe = pnl
    elif cls == WOULD_LOSE:
        gross_r = -1.0
        won = False
        pnl = -sl_distance / entry * 100.0
        mfe = 0.0
    else:  # WOULD_EXPIRE — mark to the final close from the candidate's side.
        final = float(record.get("post_price_final") or 0.0)
        if final <= 0 or sl_distance <= 0:
            return {"won": False, "pnl_pct": 0.0, "r_multiple": 0.0,
                    "gross_r_multiple": 0.0, "net_r_multiple": 0.0, "mfe_pct": 0.0}
        side = str(record.get("side") or "").upper()
        move = (final - entry) if side == "LONG" else (entry - final)
        gross_r = move / sl_distance
        won = move > 0
        pnl = move / entry * 100.0
        mfe = max(0.0, move / entry * 100.0)

    # ``r_multiple`` is flag-gated (the value the LIVE edge_r / controller reads):
    # gross while the cost model is dark, net once it's signed on.  ``net_r_multiple``
    # is ALWAYS netted regardless of the flag, so the reconciliation (W2) can show the
    # optimism tax without flipping the live-affecting flag.
    live_r = trade_costs.net_r(gross_r, entry=entry, sl_distance=sl_distance)
    always_net_r = trade_costs.net_r(gross_r, entry=entry, sl_distance=sl_distance, enabled=True)
    cost_pct = trade_costs.round_trip_cost_pct() if trade_costs.is_enabled() else 0.0
    return {
        "won": won,
        "pnl_pct": pnl - cost_pct,
        "r_multiple": live_r,
        "gross_r_multiple": gross_r,
        "net_r_multiple": always_net_r,
        "mfe_pct": mfe,
    }


def compute_gate_suppression_metrics(
    records: List[Dict[str, Any]],
    *,
    min_sample: int = _MIN_SAMPLE,
) -> Dict[str, Dict[str, Any]]:
    """Per-gate ablation: counts + saved/missed R + EV/suppression + KEEP/TUNE/DROP.

    Structural clone of ``invalidation_audit``'s per-rule ablation, keyed by gate.
    """
    by_gate: Dict[str, Dict[str, Any]] = {}
    for rec in records:
        cls = rec.get("classification")
        if cls in (None, INSUFFICIENT):
            continue
        gate = rec.get("gate_name") or "unknown"
        g = by_gate.setdefault(
            gate,
            {"WOULD_WIN": 0, "WOULD_LOSE": 0, "WOULD_EXPIRE": 0,
             "saved_r": 0.0, "missed_r": 0.0},
        )
        g[cls] = g.get(cls, 0) + 1
        ev = suppression_value_delta_r(rec)
        if ev is None:
            continue
        if ev > 0:
            g["saved_r"] += ev
        elif ev < 0:
            g["missed_r"] += -ev

    for gate, g in by_gate.items():
        n = g["WOULD_WIN"] + g["WOULD_LOSE"] + g["WOULD_EXPIRE"]
        g["n"] = n
        g["would_win_pct"] = (g["WOULD_WIN"] / n * 100.0) if n else 0.0
        ev_per = ((g["saved_r"] - g["missed_r"]) / n) if n else 0.0
        g["ev_per_suppression_r"] = ev_per
        if n < min_sample:
            g["verdict"] = VERDICT_INSUFFICIENT
        elif ev_per >= _KEEP_EV_R:
            g["verdict"] = VERDICT_KEEP
        elif ev_per <= _DROP_EV_R:
            g["verdict"] = VERDICT_DROP
        else:
            g["verdict"] = VERDICT_TUNE
    return by_gate


# ---------------------------------------------------------------------------
# Store - bounded in-memory buffer + batched persistence
# ---------------------------------------------------------------------------


class SuppressedCandidateStore:
    def __init__(self, persist_path: Optional[str] = None, maxlen: Optional[int] = None) -> None:
        self._lock = threading.Lock()
        self._buffer: Deque[dict] = deque(maxlen=maxlen if maxlen is not None else _MAX_RECORDS)
        # Monotonic since-boot stamp counter — the ring buffer evicts, so the
        # feature-liveness probes need a counter that can't go backwards.
        self.stamped_total: int = 0
        self._persist_path: str = _DEFAULT_PATH if persist_path is None else persist_path
        if self._persist_path:
            self._load()

    # ---- hot path: O(1), no I/O ----
    def stamp(self, record: SuppressedCandidateRecord) -> None:
        with self._lock:
            self._buffer.append(asdict(record))
            self.stamped_total += 1

    def records(self) -> List[dict]:
        with self._lock:
            return list(self._buffer)

    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for r in self._buffer if r.get("classification") is None)

    # ---- periodic loop: classify + persist + prune ----
    def classify_pending(
        self,
        *,
        fetch_ohlc_since: Callable[[str, float], Optional[Dict[str, List[float]]]],
        now_ts: Optional[float] = None,
        window_sec: float = _WINDOW_SEC,
        on_classified: Optional[Callable[[dict], None]] = None,
    ) -> Dict[str, int]:
        now = now_ts if now_ts is not None else time.time()
        counters: Dict[str, int] = {}
        with self._lock:
            snapshot = list(self._buffer)
        for rec in snapshot:
            if rec.get("classification") is not None:
                continue
            ts = float(rec.get("suppress_timestamp") or 0.0)
            if ts <= 0:
                _mark(rec, INSUFFICIENT, now)
                counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                continue
            # Respect the candidate's own validity window, floored at the default.
            vfm = float(rec.get("valid_for_minutes") or 0.0)
            eff_window = max(window_sec, vfm * 60.0) if vfm > 0 else window_sec
            if now - ts < eff_window:
                continue
            symbol = str(rec.get("symbol") or "")
            ohlc = fetch_ohlc_since(symbol, ts) if symbol else None
            if not ohlc:
                _mark(rec, INSUFFICIENT, now)
                counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                continue
            # None/len checks, not truthiness — a fetcher returning numpy
            # arrays would raise here and kill the whole classify batch
            # (numpy-truthiness class, 2026-07-14).
            _highs = ohlc.get("high")
            _lows = ohlc.get("low")
            if _highs is None or _lows is None or len(_highs) == 0 or len(_lows) == 0:
                _mark(rec, INSUFFICIENT, now)
                counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                continue
            high = max(_highs)
            low = min(_lows)
            close = ohlc.get("close")
            final = float(close[-1]) if close is not None and len(close) > 0 else 0.0
            if str(rec.get("entry_type") or ENTRY_IMMEDIATE) == ENTRY_LIMIT:
                label = classify_limit_record(
                    rec, [float(h) for h in _highs], [float(low_) for low_ in _lows]
                )
            else:
                label = classify_suppressed_record(rec, high, low, final)
            rec["post_price_max"] = high
            rec["post_price_min"] = low
            rec["post_price_final"] = final
            _mark(rec, label, now)
            counters[label] = counters.get(label, 0) + 1
            if on_classified is not None and label != INSUFFICIENT:
                try:
                    on_classified(rec)
                except Exception as exc:  # never let a consumer break the loop
                    log.debug("on_classified hook failed (fail-open): {}", exc)
        self._prune(now)
        self._save()
        return counters

    def _prune(self, now: float) -> None:
        with self._lock:
            keep = deque(
                (
                    r for r in self._buffer
                    if r.get("classification") is None
                    or (now - float(r.get("suppress_timestamp") or now)) < _RETENTION_SEC
                ),
                maxlen=self._buffer.maxlen,
            )
            self._buffer = keep

    # ---- persistence (batched, off the hot path) ----
    def _load(self) -> None:
        try:
            if not os.path.exists(self._persist_path):
                return
            with open(self._persist_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            if isinstance(raw, list):
                with self._lock:
                    for r in raw[-(self._buffer.maxlen or _MAX_RECORDS):]:
                        if isinstance(r, dict):
                            self._buffer.append(r)
        except Exception:
            pass  # fail-open on a bad store file

    def _save(self) -> None:
        if not self._persist_path:
            return
        try:
            with self._lock:
                payload = list(self._buffer)
            dirname = os.path.dirname(self._persist_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._persist_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._persist_path)
        except Exception:
            pass  # best-effort


def _mark(rec: dict, label: str, now: float) -> None:
    rec["classification"] = label
    rec["classified_at"] = now


# ---------------------------------------------------------------------------
# Module singleton + hot-path stamp helper
# ---------------------------------------------------------------------------

_store: Optional[SuppressedCandidateStore] = None


def get_store() -> SuppressedCandidateStore:
    global _store
    if _store is None:
        _store = SuppressedCandidateStore()
    return _store


def stamp_candidate(
    *,
    gate_name: str,
    symbol: str,
    channel: str,
    setup_class: str,
    side: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    confidence: float = 0.0,
    context_key: str = "",
    regime: str = "",
    valid_for_minutes: float = 0.0,
    pair_cohort: str = "",
    entry_type: str = ENTRY_IMMEDIATE,
    store: Optional[SuppressedCandidateStore] = None,
) -> Optional[SuppressedCandidateRecord]:
    """Stamp a suppressed candidate (fail-open).  Scopes to tradeable geometry only."""
    try:
        entry = float(entry or 0.0)
        stop_loss = float(stop_loss or 0.0)
        tp1 = float(tp1 or 0.0)
        sl_distance = abs(entry - stop_loss)
        if entry <= 0 or stop_loss <= 0 or tp1 <= 0 or sl_distance <= 0:
            return None
        rec = SuppressedCandidateRecord(
            gate_name=gate_name,
            setup_class=str(setup_class or "UNKNOWN"),
            symbol=symbol,
            channel=channel,
            side=str(side or "").upper(),
            entry=entry,
            stop_loss=stop_loss,
            tp1=tp1,
            sl_distance=sl_distance,
            confidence=float(confidence or 0.0),
            context_key=context_key or "",
            regime=regime or "",
            valid_for_minutes=float(valid_for_minutes or 0.0),
            pair_cohort=str(pair_cohort or ""),
            entry_type=str(entry_type or ENTRY_IMMEDIATE),
            suppress_timestamp=time.time(),
        )
        (store or get_store()).stamp(rec)
        return rec
    except Exception as exc:
        from src import fail_open
        fail_open.record("suppression_audit.stamp_candidate", exc)
        return None
