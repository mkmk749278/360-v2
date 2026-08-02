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
_MAX_RECORDS: int = int(os.getenv("SUPPRESSION_AUDIT_MAX_RECORDS", "16000"))
# Per-gate ring size.
#
# This store was ONE count-bounded deque, and a single shared ring makes the
# LOUDEST gate the only measured one: on 2026-07-31 it sat at exactly its 5000
# cap with ``level_still_in_play`` (1331) and ``min_confidence`` (1237) holding
# half of it, while ``cohort_edge`` — whose missing stamp #834 had just fixed —
# still had no row at all.  A quiet gate's rows are evicted by a loud gate's
# before their measurement window elapses, so the gate that suppresses least is
# the one we can say least about.  That is backwards: a gate earns its place by
# being measured, and the rare ones are exactly the ones nobody has checked.
#
# Partitioning per gate makes fairness structural rather than a tuning exercise,
# and it is what makes stamping the two high-volume pre-scoring gates safe —
# MOVER_TREND_PULLBACK's 24,327 execution rejects can no longer evict anyone
# else's evidence.  A verdict on every gate beats a precise verdict on two.
_PER_GATE_MAX: int = int(os.getenv("SUPPRESSION_AUDIT_PER_GATE_MAX", "400"))
# Bounded cardinality guard.  Gate tokens are a closed vocabulary (six
# MarketState values, two execution reasons, a fixed gate list), so a store
# growing past this means a caller is minting unbounded gate names — counted
# and refused rather than allowed to grow the footprint without bound.
_MAX_GATES: int = int(os.getenv("SUPPRESSION_AUDIT_MAX_GATES", "64"))
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

# Exit models for stamped candidates.  ``static`` (default, all historical
# records): the stamped SL/TP1 are fixed levels and the outcome is the TP1-vs-SL
# race — the only model this ledger had until 2026-07-25.  ``trailing``: the
# exit level MOVES bar by bar, so the outcome is a continuous exit price rather
# than a ±1R/TP1 binary, and it can only be resolved by walking candles in
# order.  The walk itself is NOT implemented here: a trailing record is resolved
# by the ``trail_classifier`` its own ledger supplies to ``classify_pending``,
# which writes back the ``trail_*`` fields this module then scores.  That keeps
# each trailing method (SAR, ATR, SuperTrend, …) in its own module and leaves
# this one method-agnostic.
EXIT_STATIC = "static"
EXIT_TRAILING = "trailing"

# Why a trailing arm stopped.  Canonical here rather than in the individual
# trailing modules: ``classify_pending`` has to distinguish them to resolve a
# trade early (a real trail exit is final; a "window" mark on partial candles is
# just the walker running out of bars), and this module must not import
# ``sar_exit_shadow`` — that dependency runs the other way.
REASON_TRAIL = "trail"      # the moving stop caught price
REASON_WINDOW = "window"    # never stopped out — marked to the window's close
# A conditional-handover arm runs the live geometry until the indicator comes
# onside, so it can also finish on the static levels it started behind
# (owner design, 2026-07-27).  These are *final* the moment the candles cover
# them — a stop that was hit cannot be un-hit by a later bar — so they resolve
# early exactly like REASON_TRAIL.  Leaving them out of ``_FINAL_REASONS`` would
# park every never-handed-over trade at RUNNING for the full 48h window, which
# is the failure #798 already paid for once.
REASON_STATIC_SL = "static_sl"    # the live stop-loss closed it before handover
REASON_STATIC_TP1 = "static_tp1"  # the live TP1 closed it before handover
#: Exit reasons that are decided, not merely "as far as the candles go".
_FINAL_REASONS = frozenset({REASON_TRAIL, REASON_STATIC_SL, REASON_STATIC_TP1})

#: Counter key for a mid-window record that HAD candles and still produced no
#: verdict — the walker ran out of bars before the trade's exit.
#:
#: This is not an error and the ``continue`` below is correct: mid-window, "not
#: yet" is the honest answer.  But it was silent, and silence here is how a
#: ledger that resolves *nothing* reads as healthy.  ``sar_ledger_candles``
#: measures whether the fetch returned a window, and a frozen or too-short
#: window is still a window — so a record that can never resolve is counted as
#: a successful fetch and then dropped without a trace.  On 2026-07-29 that
#: combination held 395 of 401 rows at RUNNING for trades that had already
#: closed, with every watchdog green (see #825).
#:
#: A fail-open ``continue`` with no counter is how the harm stays invisible
#: (#815, and the same lesson again here).  So the cycle counts it, and
#: ``main`` pages on the *rate*: stalling is normal, stalling for everything
#: across many cycles is the freeze.
STALLED = "STALLED_NO_VERDICT"

# Provenance of a stamped candidate: did this candidate actually reach
# subscribers, or did a gate kill it?  Shadow ledgers stamp from BOTH points in
# the scanner, which doubles the sample but mixes two different questions —
# "would this exit have improved the signals we SENT" vs "…every candidate we
# considered".  Only the first can justify changing what users receive, so the
# provenance has to travel with the record or the two can never be separated.
# Empty string = unknown (every record stamped before 2026-07-25).
#
# There are THREE states, not two, and conflating the middle one with EMITTED
# was a real measurement bug (owner-caught 2026-07-25, ~30x inflation):
#
#   SUPPRESSED — a gate in the SCANNER killed the candidate.
#   ENQUEUED   — it passed every scanner gate and ``signal_queue.put`` accepted
#                it.  This is NOT dispatch.  ``SignalRouter._process`` then
#                applies a whole second layer (correlation lock, per-symbol and
#                per-channel cooldown, per-channel concurrent cap, correlation
#                group limit, global same-direction throttle, TP/SL sanity,
#                staleness) and drops most of what it dequeues.
#   EMITTED     — the router confirmed delivery.  A subscriber really saw it.
#
# Only EMITTED can justify changing what users receive.  Measured over one
# 6.7h window: 90 distinct candidates reached the queue, 3 reached the feed —
# and the surplus is not a random sample of the rest (it is dominated by
# candidates arriving while the book was full or correlation-locked, which
# skewed the old "emitted" set to 81% SHORT against a 52% SHORT real feed).
PROVENANCE_EMITTED = "emitted"
PROVENANCE_SUPPRESSED = "suppressed"
PROVENANCE_ENQUEUED = "enqueued"

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
    # Exit model (EXIT_STATIC | EXIT_TRAILING).  Defaulted for the same reason:
    # every record written before 2026-07-25 is a static SL/TP1 race and must
    # keep scoring as one after a reload.
    exit_model: str = EXIT_STATIC
    # PROVENANCE_EMITTED | PROVENANCE_SUPPRESSED | "" (unknown, pre-2026-07-25).
    # Defaulted so persisted records reload unchanged.
    provenance: str = ""
    # Which generation of the provenance contract wrote this record.  0 = written
    # before the enqueue-vs-dispatch fix, when ``emitted`` was stamped at the
    # enqueue site and therefore cannot be trusted.  See PROVENANCE_SCHEMA.
    prov_schema: int = 0
    # Which generation of the *stamp* rule wrote this record.  0 = written when
    # the only throttle was a per-(symbol, setup, side, provenance) cooldown, so
    # one persisting setup on one move could contribute many rows — SLXUSDT
    # produced 10 inside 2h10m at a 0.37% entry spread, 36% of a whole resolved
    # population (owner-caught 2026-07-28).  Rows either side of a bump are
    # sampled differently and must not be pooled silently; see
    # ``sar_exit_shadow.STAMP_SCHEMA``.
    stamp_schema: int = 0
    # True when the gate that killed this candidate fired BEFORE the scoring
    # engine ran (``setup_compat`` / ``execution``).  Such a row carries the
    # evaluator's geometry and its evaluator confidence, but never a scored
    # one — so it can be audited (did the gate save or cost us?) and must NOT
    # reach the Strategy×Context edge matrix, which Layer C consumes live to
    # set per-context emission floors.  Measurement ON, money path untouched.
    pre_scoring: bool = False
    # Filled by classify_pending once the window elapses.
    classified_at: Optional[float] = None
    classification: Optional[str] = None
    post_price_max: Optional[float] = None
    post_price_min: Optional[float] = None
    post_price_final: Optional[float] = None
    # Trailing-exit results, written back by the ledger's own trail_classifier
    # (EXIT_TRAILING records only).  ``trail_exit_price`` is where the moving
    # stop actually took the trade out; ``trail_mfe_pct`` is the best excursion
    # reached before that.  ``candidate_outcome`` scores from these instead of
    # the TP1/SL levels.
    trail_exit_price: Optional[float] = None
    trail_mfe_pct: Optional[float] = None
    trail_hold_min: Optional[float] = None
    trail_exit_reason: Optional[str] = None
    # Was the trailing indicator on our side when the signal fired?  Written at
    # STAMP time (2026-07-27), not at resolution: it compares the indicator
    # level on the last closed bar against the entry, and both numbers exist the
    # instant the candidate is stamped.  Computing it in the resolve path meant
    # 261 of 277 rows carried no verdict for up to 48h purely because of where
    # the line sat, and the agreement mix on screen always described a two-day-old
    # population.  ``None`` means "we could not decide", never "opposed" —
    # the caller refuses rather than defaulting.
    sar_aligned_at_entry: Optional[bool] = None
    # The resolve-path recomputation of the same quantity, kept as a CROSS-CHECK
    # and never as the authority.  The two must agree; a disagreement means the
    # walker's replay window is not reconstructing the bar the scanner actually
    # saw, which is exactly the #800 failure mode made self-reporting.
    sar_aligned_at_resolve: Optional[bool] = None


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

    if str(record.get("exit_model") or EXIT_STATIC) == EXIT_TRAILING:
        # A moving stop has no TP1-vs-SL binary: it exits wherever the trail
        # caught price, so R is continuous.  The R *denominator* is still the
        # live geometry's sl_distance — that is precisely what makes a trailing
        # arm comparable in R against the static control arm stamped from the
        # same candidate.
        exit_price = float(record.get("trail_exit_price") or 0.0)
        if exit_price <= 0 or sl_distance <= 0:
            return {"won": False, "pnl_pct": 0.0, "r_multiple": 0.0,
                    "gross_r_multiple": 0.0, "net_r_multiple": 0.0, "mfe_pct": 0.0}
        side = str(record.get("side") or "").upper()
        move = (exit_price - entry) if side == "LONG" else (entry - exit_price)
        gross_r = move / sl_distance
        won = move > 0
        pnl = move / entry * 100.0
        mfe = float(record.get("trail_mfe_pct") or 0.0)
        live_r = trade_costs.net_r(gross_r, entry=entry, sl_distance=sl_distance)
        always_net_r = trade_costs.net_r(
            gross_r, entry=entry, sl_distance=sl_distance, enabled=True
        )
        cost_pct = trade_costs.round_trip_cost_pct() if trade_costs.is_enabled() else 0.0
        return {
            "won": won,
            "pnl_pct": pnl - cost_pct,
            "r_multiple": live_r,
            "gross_r_multiple": gross_r,
            "net_r_multiple": always_net_r,
            "mfe_pct": mfe,
        }

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


def gate_metrics_by_setup(
    records: List[Dict[str, Any]],
    *,
    setup_class: str = "",
    min_sample: int = 1,
) -> Dict[str, Dict[str, Any]]:
    """Which gates kill a given setup, and what that costs — per (setup, gate).

    The per-gate table answers "is this gate net-helping?" but pools every
    setup into one row, so it cannot answer the question the emission probes
    actually tell you to ask: *"this path emits nothing — which gate is
    stopping it?"*  Both fields were already on every stamped record; nothing
    cross-tabbed them, so #781 said "check gate rejections" for days with no
    view that could.

    Keyed ``"SETUP|gate"``.  Pass ``setup_class`` to scope to one path.
    """
    from src import trade_costs  # noqa: F401  (parity with the per-gate table)

    by_key: Dict[str, Dict[str, Any]] = {}
    want = str(setup_class or "").strip().upper()
    for rec in records or []:
        cls = rec.get("classification")
        if cls in (None, INSUFFICIENT):
            continue
        setup = str(rec.get("setup_class") or "UNKNOWN")
        if want and setup.upper() != want:
            continue
        gate = str(rec.get("gate_name") or "unknown")
        agg = by_key.setdefault(
            f"{setup}|{gate}",
            {
                "setup_class": setup, "gate_name": gate, "n": 0,
                "would_win": 0, "would_lose": 0, "would_expire": 0,
                "_ev_sum": 0.0,
            },
        )
        agg["n"] += 1
        if cls == WOULD_WIN:
            agg["would_win"] += 1
        elif cls == WOULD_LOSE:
            agg["would_lose"] += 1
        elif cls == WOULD_EXPIRE:
            agg["would_expire"] += 1
        ev = suppression_value_delta_r(rec)
        if ev is not None:
            agg["_ev_sum"] += ev

    out: Dict[str, Dict[str, Any]] = {}
    for key, agg in by_key.items():
        n = agg["n"]
        if n < min_sample:
            continue
        ev_per = agg.pop("_ev_sum") / n if n else 0.0
        agg["would_win_pct"] = (agg["would_win"] / n) if n else 0.0
        # EV from the SUPPRESSION's perspective: positive = the gate helped.
        # Negative means this gate is destroying value on this specific path,
        # which is the actionable form of "why does this path never emit".
        agg["ev_per_suppression_r"] = ev_per
        agg["verdict"] = (
            VERDICT_KEEP if ev_per >= _KEEP_EV_R
            else VERDICT_DROP if ev_per <= _DROP_EV_R
            else VERDICT_TUNE
        ) if n >= _MIN_SAMPLE else VERDICT_INSUFFICIENT
        out[key] = agg
    return out


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


# Generation of the provenance contract.  Bumped when the *meaning* of the
# ``provenance`` field changes, so records can be told apart by what wrote them
# rather than by when they were written.
#
#   0 — pre-fix.  ``emitted`` was stamped at the *enqueue* site, which is not
#       dispatch (see the PROVENANCE_* block at the top of this module), so
#       roughly 97% of those rows were never delivered to anyone.
#   2 — post-fix.  The scanner stamps ENQUEUED; only the router's
#       ``promote_to_emitted`` writes EMITTED, after confirmed delivery.
#
# A schema-0 ``emitted`` record is relabelled ENQUEUED on load.  That is the
# truthful label — it was queued, and which few were actually sent is not
# recoverable — and it fails in the safe direction: it removes them from the
# emitted sample rather than inventing membership in it.
#
# **This is deliberately not a timestamp.**  The first cut of this migration
# used a hardcoded wall-clock cutoff set to when the fix was *written*
# (2026-07-25T18:00Z).  The PR then sat unmerged for eight hours and shipped at
# 2026-07-26T02:10Z, so every record stamped in that gap was written by the old
# enqueue-site code yet sat *after* the cutoff and was trusted — 88 rows of
# pre-fix data rendered as "Delivered to users (88)" in ops for a window whose
# real feed was 3 signals, i.e. exactly the ~30x inflation the fix existed to
# remove (owner-caught 2026-07-26).  A marker written by the code itself cannot
# drift from its own deploy time; a guessed timestamp always can.
PROVENANCE_SCHEMA: int = 2


# Window inside which two stamps are treated as arms of the SAME candidate.
# Both arms of a measurement pair are written in one call stack (microseconds
# apart); separate detections are gated by the stamp cooldown, which is orders
# of magnitude larger.
_PAIR_EPSILON_SEC: float = 1.0


def _migrate_provenance(rec: dict) -> dict:
    """Downgrade a pre-fix ``emitted`` stamp to ``enqueued`` (in place).

    Keyed on who wrote the record, not on when.  Anything claiming EMITTED
    without the current schema marker was written by the enqueue-site stamp and
    is not evidence of delivery.
    """
    try:
        if rec.get("provenance") != PROVENANCE_EMITTED:
            return rec
        if int(rec.get("prov_schema") or 0) >= PROVENANCE_SCHEMA:
            return rec
        rec["provenance"] = PROVENANCE_ENQUEUED
    except (TypeError, ValueError):
        pass
    return rec


class SuppressedCandidateStore:
    def __init__(
        self,
        persist_path: Optional[str] = None,
        maxlen: Optional[int] = None,
        per_gate_max: Optional[int] = None,
    ) -> None:
        self._lock = threading.Lock()
        # One bounded ring PER GATE, not one shared ring — see _PER_GATE_MAX.
        # ``maxlen`` stays honoured as a global ceiling so an operator can still
        # bound total footprint, and so existing callers keep their meaning.
        self._per_gate_max: int = int(
            per_gate_max if per_gate_max is not None else _PER_GATE_MAX
        )
        self._global_max: int = int(maxlen if maxlen is not None else _MAX_RECORDS)
        self._gates: Dict[str, Deque[dict]] = {}
        #: Gates refused because the store already holds ``_MAX_GATES`` names.
        #: Counted, never silent: a refusal here means a caller is minting gate
        #: names and some gate is going unmeasured.
        self.gates_refused: int = 0
        #: Records dropped by the per-gate ring, keyed by gate. The sampling
        #: rate belongs on screen beside the verdict — a rate measured on 400
        #: of 24,000 suppressions is a sample, and the reader must know it.
        self.evicted_by_gate: Dict[str, int] = {}
        # Monotonic since-boot stamp counter — the ring buffer evicts, so the
        # feature-liveness probes need a counter that can't go backwards.
        self.stamped_total: int = 0
        self._persist_path: str = _DEFAULT_PATH if persist_path is None else persist_path
        if self._persist_path:
            self._load()

    # ---- hot path: O(1), no I/O ----
    @property
    def _buffer(self) -> List[dict]:
        """Every record, newest last. Read-only view over the per-gate rings.

        Kept as ``_buffer`` because the eviction policy changed, not the
        contract: callers still see one chronologically ordered population.
        """
        out: List[dict] = []
        for ring in self._gates.values():
            out.extend(ring)
        out.sort(key=lambda r: float(r.get("suppress_timestamp") or 0.0))
        return out

    def stamp(self, record: SuppressedCandidateRecord) -> None:
        with self._lock:
            rec = asdict(record)
            gate = str(rec.get("gate_name") or "")
            ring = self._gates.get(gate)
            if ring is None:
                if len(self._gates) >= _MAX_GATES:
                    self.gates_refused += 1
                    return
                ring = deque(maxlen=self._per_gate_max)
                self._gates[gate] = ring
            if len(ring) == ring.maxlen:
                self.evicted_by_gate[gate] = self.evicted_by_gate.get(gate, 0) + 1
            ring.append(rec)
            self.stamped_total += 1
            self._enforce_global_ceiling()

    def _enforce_global_ceiling(self) -> None:
        """Trim the fullest gate first when the global ceiling is exceeded.

        Evicting the globally-oldest record is what made the shared ring unfair
        in the first place; taking from whichever gate holds most keeps the
        pressure on the gate that can best afford it. Caller holds the lock.
        """
        total = sum(len(r) for r in self._gates.values())
        while total > self._global_max:
            gate, ring = max(self._gates.items(), key=lambda kv: len(kv[1]))
            if not ring:
                return
            ring.popleft()
            self.evicted_by_gate[gate] = self.evicted_by_gate.get(gate, 0) + 1
            total -= 1

    def sampling(self) -> Dict[str, Dict[str, int]]:
        """Per-gate held vs evicted, so a verdict can state its denominator."""
        with self._lock:
            return {
                gate: {
                    "held": len(ring),
                    "evicted": int(self.evicted_by_gate.get(gate, 0)),
                    "cap": int(ring.maxlen or 0),
                }
                for gate, ring in self._gates.items()
            }

    def promote_provenance(
        self,
        *,
        symbol: str,
        side: str,
        setup_prefix: str,
        entry: float,
        from_provenance: str,
        to_provenance: str,
        max_age_sec: float,
        now_ts: Optional[float] = None,
    ) -> int:
        """Re-label the newest matching candidate's arms in place.

        Used when the truth about a record is only known *later* than the
        stamp: the scanner stamps ENQUEUED when the queue accepts a candidate,
        and the router — which is the actual dispatcher — promotes it to
        EMITTED once delivery is confirmed.

        Matches on ``(symbol, side, entry)`` plus a ``setup_prefix`` so both
        measurement arms of one candidate (e.g. ``FOO@SARBASE`` and
        ``FOO@SAREXIT``) are promoted together — a half-promoted pair would
        bias the A/B exactly as a lone stamp does.  Only unclassified records
        inside ``max_age_sec`` are eligible, so a promotion can never reach
        back and rewrite an already-measured outcome.

        Ties are broken by the newest stamp, and only the newest candidate is
        promoted: a persisting setup re-detected across scan cycles must not
        have all its historical rows relabelled by one dispatch.

        Returns the number of arm records promoted (0 when nothing matched).
        """
        now = time.time() if now_ts is None else float(now_ts)
        prefix = str(setup_prefix or "")
        side_u = str(side or "").upper()
        try:
            entry_f = float(entry or 0.0)
        except (TypeError, ValueError):
            return 0
        with self._lock:
            candidates: List[dict] = []
            for rec in self._buffer:
                if rec.get("provenance") != from_provenance:
                    continue
                if rec.get("classification") is not None:
                    continue
                if str(rec.get("symbol") or "") != str(symbol or ""):
                    continue
                if str(rec.get("side") or "").upper() != side_u:
                    continue
                setup = str(rec.get("setup_class") or "")
                if not setup.startswith(prefix):
                    continue
                ts = float(rec.get("suppress_timestamp") or 0.0)
                if now - ts > max_age_sec:
                    continue
                # Same underlying candidate ⇒ identical entry price. A
                # re-detection at a different price is a different candidate.
                if abs(float(rec.get("entry") or 0.0) - entry_f) > 1e-12:
                    continue
                candidates.append(rec)
            if not candidates:
                return 0
            newest = max(float(r.get("suppress_timestamp") or 0.0) for r in candidates)
            promoted = 0
            for rec in candidates:
                # Arms of ONE candidate are stamped in the same call stack, so
                # their timestamps differ by microseconds — an exact match
                # would promote a single arm and bias the A/B. Distinct
                # detections of a persisting setup are separated by the stamp
                # cooldown (tens of seconds), so this epsilon cannot merge two.
                if newest - float(rec.get("suppress_timestamp") or 0.0) > _PAIR_EPSILON_SEC:
                    continue
                rec["provenance"] = to_provenance
                # The promotion itself is what makes EMITTED trustworthy — it
                # ran under the current contract, from the router, after
                # confirmed delivery.  Mark the record accordingly so the
                # load-time migration does not downgrade it again.
                rec["prov_schema"] = PROVENANCE_SCHEMA
                promoted += 1
            return promoted

    def clear(self) -> int:
        """Drop every record and persist the empty ledger.  Returns the count.

        Owner-initiated purge: when a defect is found in how records were
        *resolved*, the rows are evidence of the bug rather than of the thing
        being measured, and leaving them in poisons every consumer that pools
        them (the edge matrix keys on the same cells).  ``stamped_total`` is
        deliberately NOT reset — the liveness probes watch it for a monotonic
        heartbeat and a reset would read as a dead feature.
        """
        with self._lock:
            n = sum(len(r) for r in self._gates.values())
            self._gates.clear()
            self.evicted_by_gate.clear()
        self._save()
        return n

    def records(self) -> List[dict]:
        with self._lock:
            return self._buffer

    def pending_count(self) -> int:
        with self._lock:
            return sum(
                1
                for ring in self._gates.values()
                for r in ring
                if r.get("classification") is None
            )

    # ---- periodic loop: classify + persist + prune ----
    def classify_pending(
        self,
        *,
        fetch_ohlc_since: Callable[[str, float], Optional[Dict[str, List[float]]]],
        now_ts: Optional[float] = None,
        window_sec: float = _WINDOW_SEC,
        on_classified: Optional[Callable[[dict], None]] = None,
        trail_classifier: Optional[
            Callable[[dict, Dict[str, List[float]]], Optional[Dict[str, Any]]]
        ] = None,
    ) -> Dict[str, int]:
        now = now_ts if now_ts is not None else time.time()
        counters: Dict[str, int] = {}
        with self._lock:
            snapshot = self._buffer
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
            window_elapsed = (now - ts) >= eff_window
            # A trailing arm's exit is knowable as soon as the forward candles
            # cover it: the trail either caught price or it didn't, and no later
            # bar can un-catch it.  Waiting the whole window would park a trade
            # that closed in 40 minutes at RUNNING for 48h — which is exactly
            # what the ops tab showed (0 of 300 resolved, every row RUNNING,
            # owner-caught 2026-07-26).  Static arms still need the full window,
            # because their outcome is a TP/SL race decided by window extremes.
            #
            # Only a *trail* exit may resolve early.  A "window" verdict on
            # partial candles is the walker marking to the last bar it can see,
            # which would book a still-open trade at an arbitrary price — so it
            # is rejected below until the window has genuinely elapsed.
            trailing = str(rec.get("exit_model") or EXIT_STATIC) == EXIT_TRAILING
            early = trailing and not window_elapsed
            if not window_elapsed and not early:
                continue
            symbol = str(rec.get("symbol") or "")
            ohlc = fetch_ohlc_since(symbol, ts) if symbol else None
            if not ohlc:
                # Mid-window the candles simply may not exist yet; that is not a
                # verdict.  Only a record whose full window has passed without
                # usable data is genuinely INSUFFICIENT.
                if early:
                    continue
                _mark(rec, INSUFFICIENT, now)
                counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                continue
            # None/len checks, not truthiness — a fetcher returning numpy
            # arrays would raise here and kill the whole classify batch
            # (numpy-truthiness class, 2026-07-14).
            _highs = ohlc.get("high")
            _lows = ohlc.get("low")
            if _highs is None or _lows is None or len(_highs) == 0 or len(_lows) == 0:
                if early:
                    continue
                _mark(rec, INSUFFICIENT, now)
                counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                continue
            # Trailing arms resolve through their own ledger's walker: the exit
            # level moves per bar, so window extremes cannot express the
            # outcome.  The walker owns post_price_* too, because its candle
            # window may carry a pre-entry warmup prefix that must not leak
            # into the recorded excursion.
            if trailing:
                detail = None
                if trail_classifier is not None:
                    try:
                        detail = trail_classifier(rec, ohlc)
                    except Exception as exc:
                        from src import fail_open
                        fail_open.record("suppression_audit.trail_classifier", exc)
                        detail = None
                if not detail or not detail.get("classification"):
                    if early:
                        counters[STALLED] = counters.get(STALLED, 0) + 1
                        continue
                    _mark(rec, INSUFFICIENT, now)
                    counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                    continue
                # Mid-window, only a real trail exit is a result.  Anything else
                # is the walker running out of candles, not the trade closing.
                #
                # The key is ``trail_exit_reason`` — the ledger's field name,
                # which is what a trail classifier returns.  The first cut of
                # this guard read ``exit_reason`` (the *walker's* internal name,
                # one layer down), so it was always None, never matched, and
                # silently discarded every early classification: the whole path
                # ran, computed the right answer, and threw it away. The tab
                # stayed at "0 resolved" and the fix shipped inert
                # (owner-caught 2026-07-26).
                if early and str(detail.get("trail_exit_reason") or "") not in _FINAL_REASONS:
                    # The walker reached the end of its candles without the
                    # trade closing.  Mid-window that is honest; sustained
                    # across every record it means the candles never advance.
                    counters[STALLED] = counters.get(STALLED, 0) + 1
                    continue
                label = str(detail["classification"])
                for key, value in detail.items():
                    if key != "classification":
                        rec[key] = value
                _mark(rec, label, now)
                counters[label] = counters.get(label, 0) + 1
                if on_classified is not None and label != INSUFFICIENT:
                    try:
                        on_classified(rec)
                    except Exception as exc:
                        log.debug("on_classified hook failed (fail-open): {}", exc)
                continue
            # A fetcher may supply a pre-entry warmup prefix (trailing ledgers
            # need one so their indicator has converged before the trade
            # starts) and mark the trade's first bar with ``entry_index``.
            # Static arms sharing that fetcher must skip the prefix, or
            # pre-entry price action gets scored as the trade's own outcome.
            _ei = int(ohlc.get("entry_index") or 0)  # type: ignore[arg-type]
            if _ei > 0:
                _highs = _highs[_ei:]
                _lows = _lows[_ei:]
                if _highs is None or _lows is None or len(_highs) == 0 or len(_lows) == 0:
                    _mark(rec, INSUFFICIENT, now)
                    counters[INSUFFICIENT] = counters.get(INSUFFICIENT, 0) + 1
                    continue
            high = max(_highs)
            low = min(_lows)
            close = ohlc.get("close")
            if close is not None and _ei > 0:
                close = close[_ei:]
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
        """Drop classified records past retention, per gate.

        Rebuilt ring by ring: pruning into one shared deque would silently
        re-pool the gates and undo the partition on the first prune cycle.
        """
        with self._lock:
            for gate, ring in list(self._gates.items()):
                kept = deque(
                    (
                        r for r in ring
                        if r.get("classification") is None
                        or (now - float(r.get("suppress_timestamp") or now))
                        < _RETENTION_SEC
                    ),
                    maxlen=self._per_gate_max,
                )
                self._gates[gate] = kept

    # ---- persistence (batched, off the hot path) ----
    def _load(self) -> None:
        try:
            if not os.path.exists(self._persist_path):
                return
            with open(self._persist_path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            # Schema 2 (2026-08-02) wraps the records so the per-gate eviction
            # counts survive the round trip. They are what turns "n=396" into
            # "396 of 24,000", and without them a reader in another process —
            # the truth report is built by a separate script — sees every gate
            # as unsampled, which is exactly wrong for the gates sitting at the
            # cap. A list is the pre-schema file and still loads.
            if isinstance(payload, dict):
                raw = payload.get("records") or []
                _ev = payload.get("evicted_by_gate")
                if isinstance(_ev, dict):
                    self.evicted_by_gate.update(
                        {str(k): int(v) for k, v in _ev.items()}
                    )
                self.stamped_total = int(payload.get("stamped_total") or 0)
            else:
                raw = payload
            if isinstance(raw, list):
                with self._lock:
                    # Bucket by gate on the way in. Truncating the raw list
                    # first would reload the same unfair sample the partition
                    # exists to end — the tail of one file is whichever gate
                    # was loudest when it was written.
                    for r in raw:
                        if not isinstance(r, dict):
                            continue
                        gate = str(r.get("gate_name") or "")
                        ring = self._gates.get(gate)
                        if ring is None:
                            if len(self._gates) >= _MAX_GATES:
                                self.gates_refused += 1
                                continue
                            ring = deque(maxlen=self._per_gate_max)
                            self._gates[gate] = ring
                        ring.append(_migrate_provenance(r))
                    self._enforce_global_ceiling()
        except Exception:
            pass  # fail-open on a bad store file

    def _save(self) -> None:
        if not self._persist_path:
            return
        try:
            with self._lock:
                payload = {
                    "schema": 2,
                    "records": self._buffer,
                    # Not decoration: a per-gate EV computed on a capped ring is
                    # a sample, and the reader has to be told the denominator.
                    "evicted_by_gate": dict(self.evicted_by_gate),
                    "stamped_total": int(self.stamped_total),
                }
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


def feeds_edge_matrix(rec: dict) -> bool:
    """May this classified record become a Strategy×Context edge-matrix cell?

    Named and exported rather than written inline at the call site, because the
    answer is a **money-path** decision: Layer C's ``context_emission_policy``
    reads those cells live to set per-context emission floors, so whatever
    returns True here can change what subscribers receive.

    False for a pre-scoring reject.  ``setup_compat`` / ``execution`` fire ahead
    of the scoring engine, so the row carries the evaluator's confidence and no
    scored one, and there are ~38k of them per window against ~4.5k
    post-scoring suppressions — admitting them would not just add rows, it
    would swamp the matrix with a differently-measured population.  They are
    still fully audited; the audit is display-and-analysis, the matrix routes.
    """
    return not bool(rec.get("pre_scoring"))


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
    exit_model: str = EXIT_STATIC,
    provenance: str = "",
    sar_aligned_at_entry: Optional[bool] = None,
    stamp_schema: int = 0,
    pre_scoring: bool = False,
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
            exit_model=str(exit_model or EXIT_STATIC),
            provenance=str(provenance or ""),
            # Tri-state on purpose: True / False / None-for-undecidable. Not
            # coerced with bool(), which would turn "we could not tell" into
            # "opposed" and silently invent half a population.
            sar_aligned_at_entry=(
                None if sar_aligned_at_entry is None else bool(sar_aligned_at_entry)
            ),
            # Stamped by the current contract, so its provenance is trustworthy
            # on reload without consulting a wall clock.
            prov_schema=PROVENANCE_SCHEMA,
            # Which stamp-rule generation produced this row.  Callers that have
            # no dedup rule of their own leave it 0 and are unaffected.
            stamp_schema=int(stamp_schema or 0),
            pre_scoring=bool(pre_scoring),
            suppress_timestamp=time.time(),
        )
        (store or get_store()).stamp(rec)
        return rec
    except Exception as exc:
        from src import fail_open
        fail_open.record("suppression_audit.stamp_candidate", exc)
        return None
