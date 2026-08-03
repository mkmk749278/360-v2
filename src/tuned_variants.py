"""Tuned-recipe shadow arms for the measured-loser evaluators (2026-07-16).

MOVER_AVWAP_SCALP and VOLUME_SURGE_BREAKOUT are three-consecutive-windows
measured losers (edge matrix −0.78R n=141 / −0.74R n=95; profit-tab capture
−17% / −4% — they reach profit and still lose).  Owner directive 2026-07-16:
*"disabling paths is never a good idea, need to tune it for better
performance for best signals."*  So instead of pruning, every live candidate
from these paths also stamps a ``SETUP@TUNED`` counterfactual arm into the
geometry ledger, attacking each path's measured failure mode:

* **MOVER_AVWAP_SCALP** gives back 100% of its runners (avg 2.18% MFE,
  realized −0.38%): the tuned arm banks TP1 at the measured median MFE
  (``TUNED_MAS_TP1_PCT``) behind an ATR/structure stop, instead of riding
  the give-back to the stop.
* **VOLUME_SURGE_BREAKOUT** chases late entries: the tuned arm only takes
  candidates within ``TUNED_VSB_MAX_EXTENSION_ATR`` of the 20-bar mean and
  banks at the MFE-derived TP1 (``TUNED_VSB_TP1_PCT``).
* **MOVER_TREND_PULLBACK** (added 2026-07-23 — the perfect-entry study):
  the live path enters at the *close of the reclaim bar*, a full 15m bar off
  the pullback low, and its realized R runs −0.37R below its own
  counterfactual (the ``edge_reconciliation`` alert).  The tuned arm rests a
  **limit at the fast MA the pullback tagged** (SMA-``MOVER_TP_MA_FAST`` of
  15m closes) with the live arm's absolute SL/TP1 kept — same thesis, paid
  retest price.  Honesty requires fill-awareness: the arm stamps with
  ``entry_type="limit"`` so ``suppression_audit.classify_limit_record`` walks
  candles for the touch first, and a retest that never comes scores
  ``WOULD_NOT_FILL`` = 0R — the cost of patience is measured, not assumed.

Observe-only end to end: nothing here can reach the signal queue, the arm
rows are ``source="shadow"`` edge-matrix variants excluded from the
allocator and from per-strategy rollups (``geometry_ab.is_geometry_variant``
covers ``@TUNED``), and *applying* a winning recipe live remains a separate
dark-first + owner-signed change.

Cost discipline: O(1) in-memory stamps on suppression/emission events only,
candles from the already-warm store, classification batched on the existing
5-min loop — no new network or Firestore reads.
"""
from __future__ import annotations

import threading
import time
from typing import Dict, Optional, Sequence, Tuple

from src.geometry_ab import (
    TUNED_SUFFIX,
    compute_atr_structure_stop,
    is_geometry_variant,
)
from src.shadow_strategies import _simple_atr
from src.suppression_audit import (
    ENTRY_IMMEDIATE,
    ENTRY_LIMIT,
    SuppressedCandidateStore,
    stamp_candidate,
)
from src.utils import get_logger

log = get_logger("tuned_variants")

GATE_PREFIX = "tuned_variant:"

# 20-bar mean window for the VSB extension filter — matches the geometry
# A/B's structure lookback so "extended" means the same thing in both arms.
_VSB_MEAN_LOOKBACK = 20

# Per-(symbol, setup, side) monotonic cooldown, same shape as geometry_ab's.
_last_stamp: Dict[Tuple[str, str, str], float] = {}

# Pipeline-health counters for the tuned_variants liveness probe:
#   seen    — candidates from a tuned setup that reached the stamp hook
#   stamped — @TUNED arms actually recorded
#   skipped — by-design non-stamps (cooldown, VSB extension filter,
#             degenerate input geometry)
# seen − stamped − skipped is the unexplained residue: sustained growth means
# the pipeline is silently failing (uncomputable ATR arms, store rejects).
#
# "Unexplained" was literal, and that was the defect (2026-08-03): the probe
# paged with `66 unexplained non-stamps` and there are FOUR ways to produce one
# — an uncomputable MTP retest arm, an uncomputable ATR arm, a store that
# refused the candidate, and an exception — needing four different responses.
# Each now increments its own `residue:*` counter at the point it returns, so
# the alert names the cause instead of stating that it has none. Same fix the
# cohort-edge gate got days earlier: a probe that cannot say which of its
# silences it is in cannot be acted on.
RESIDUE_MTP_ARM = "residue:mtp_arm_uncomputable"
RESIDUE_ATR_ARM = "residue:atr_arm_uncomputable"
#: `stamp_candidate` returning None. NOT "the store rejected it" — the store's
#: `stamp` is fire-and-forget and its return is never read. The two real causes
#: are that writer's own degenerate-geometry guard (sl_distance <= 0) and an
#: exception inside it, which it has already recorded to `fail_open` under its
#: own site name. Named for what it is, because a counter called `store_reject`
#: sends the next reader to a module that never refused anything.
RESIDUE_STAMP_REFUSED = "residue:stamp_refused"
RESIDUE_EXCEPTION = "residue:exception"
RESIDUE_KEYS: Tuple[str, ...] = (
    RESIDUE_MTP_ARM,
    RESIDUE_ATR_ARM,
    RESIDUE_STAMP_REFUSED,
    RESIDUE_EXCEPTION,
)

_counter_lock = threading.Lock()
_counters: Dict[str, int] = {
    "seen": 0,
    "stamped": 0,
    "skipped": 0,
    **{k: 0 for k in RESIDUE_KEYS},
}


def tuned_setups() -> Tuple[str, ...]:
    return ("MOVER_AVWAP_SCALP", "VOLUME_SURGE_BREAKOUT", "MOVER_TREND_PULLBACK")


def compute_mtp_retest_arm(
    *,
    side: str,
    entry: float,
    closes: Sequence[float],
    live_stop_loss: float,
    live_tp1: float,
) -> Optional[Tuple[float, str]]:
    """Perfect-entry recipe for MOVER_TREND_PULLBACK: → ``(limit_entry, reason)``.

    The limit rests at the fast MA the pullback tagged (the price the live
    arm's reclaim bar closed *away from*).  Skips, with reason:

    * ``no_improvement`` — the MA is not a better price than the live entry
      (nothing to study; stamping it would duplicate the live arm), and
    * ``through_stop`` — the MA sits at/beyond the live SL, so the resting
      order's geometry would be degenerate.
    """
    from config import MOVER_TP_MA_FAST

    side_u = str(side or "").upper()
    entry_f = float(entry or 0.0)
    sl = float(live_stop_loss or 0.0)
    tp1 = float(live_tp1 or 0.0)
    if entry_f <= 0 or sl <= 0 or tp1 <= 0 or side_u not in ("LONG", "SHORT"):
        return None
    if closes is None or len(closes) < MOVER_TP_MA_FAST:
        return None
    window = [float(c) for c in closes[-MOVER_TP_MA_FAST:]]
    limit = sum(window) / len(window)
    if limit <= 0:
        return None
    if side_u == "LONG":
        if limit >= entry_f:
            return (0.0, "no_improvement")
        if limit <= sl:
            return (0.0, "through_stop")
    else:
        if limit <= entry_f:
            return (0.0, "no_improvement")
        if limit >= sl:
            return (0.0, "through_stop")
    return (limit, "ok")


def counters() -> Dict[str, int]:
    with _counter_lock:
        return dict(_counters)


def _bump(key: str) -> None:
    with _counter_lock:
        _counters[key] = _counters.get(key, 0) + 1


def residue_breakdown() -> Dict[str, int]:
    """``{cause: n}`` for the non-zero residue causes, cause name unprefixed.

    The named causes should sum to ``seen − stamped − skipped``. Where they do
    not, a path returns without accounting for itself and the probe says so —
    one count is an assertion, two are a detector.
    """
    c = counters()
    return {
        k.split(":", 1)[1]: c.get(k, 0) for k in RESIDUE_KEYS if c.get(k, 0)
    }


def compute_tuned_arm(
    *,
    setup: str,
    side: str,
    entry: float,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
) -> Optional[Tuple[float, float, str]]:
    """Pure recipe math: → ``(stop, tp1, reason)`` or ``None``.

    ``None`` with reason semantics is split by the caller: a ``None`` from
    the VSB extension filter is a by-design skip; a ``None`` from the ATR
    stop computation is a pipeline failure worth counting.
    """
    from config import (
        TUNED_MAS_TP1_PCT,
        TUNED_VSB_MAX_EXTENSION_ATR,
        TUNED_VSB_TP1_PCT,
    )

    setup_u = str(setup or "").upper()
    side_u = str(side or "").upper()
    entry = float(entry or 0.0)
    if entry <= 0 or side_u not in ("LONG", "SHORT"):
        return None

    if setup_u == "VOLUME_SURGE_BREAKOUT":
        tp1_pct = TUNED_VSB_TP1_PCT
        # Entry-quality tightening: skip late chases.  The live path's
        # round-trips-to-−1R cohort is exactly the entries already stretched
        # far from value when the surge fires.
        if len(closes) >= _VSB_MEAN_LOOKBACK:
            atr = _simple_atr(highs, lows, closes)
            if atr > 0:
                window = [float(x) for x in closes[-_VSB_MEAN_LOOKBACK:]]
                mean = sum(window) / len(window)
                if abs(entry - mean) / atr > TUNED_VSB_MAX_EXTENSION_ATR:
                    return (0.0, 0.0, "extension_filter")
    elif setup_u == "MOVER_AVWAP_SCALP":
        tp1_pct = TUNED_MAS_TP1_PCT
    else:
        return None

    tp1 = entry * (1.0 + tp1_pct / 100.0) if side_u == "LONG" else entry * (
        1.0 - tp1_pct / 100.0
    )
    stop = compute_atr_structure_stop(
        side=side_u, entry=entry, highs=highs, lows=lows, closes=closes
    )
    if stop is None or tp1 <= 0:
        return None
    return (float(stop), float(tp1), "ok")


def stamp_tuned_variant(
    *,
    symbol: str,
    channel: str,
    setup_class: str,
    side: str,
    entry: float,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    confidence: float = 0.0,
    context_key: str = "",
    regime: str = "",
    valid_for_minutes: float = 0.0,
    live_stop_loss: float = 0.0,
    live_tp1: float = 0.0,
    store: Optional[SuppressedCandidateStore] = None,
    now_mono: Optional[float] = None,
) -> Optional[float]:
    """Stamp the ``@TUNED`` arm for one MAS/VSB/MTP candidate (fail-open).

    Returns the tuned stop price on stamp, else ``None``.  MTP arms need the
    live candidate's SL/TP1 (``live_stop_loss`` / ``live_tp1``) — the recipe
    changes the *entry*, not the exit levels.
    """
    _bumped_seen = False
    try:
        setup = str(setup_class or "").strip().upper()
        if setup not in tuned_setups() or is_geometry_variant(setup):
            return None
        _bump("seen")
        _bumped_seen = True
        side_u = str(side or "").upper()
        entry_f = float(entry or 0.0)
        if entry_f <= 0 or side_u not in ("LONG", "SHORT"):
            _bump("skipped")
            return None
        from config import TUNED_VARIANT_STAMP_COOLDOWN_SEC

        cd_key = (str(symbol or ""), setup, side_u)
        mono = time.monotonic() if now_mono is None else float(now_mono)
        last = _last_stamp.get(cd_key)
        if last is not None and mono - last < TUNED_VARIANT_STAMP_COOLDOWN_SEC:
            _bump("skipped")
            return None

        if setup == "MOVER_TREND_PULLBACK":
            mtp = compute_mtp_retest_arm(
                side=side_u, entry=entry_f, closes=closes,
                live_stop_loss=live_stop_loss, live_tp1=live_tp1,
            )
            if mtp is None:
                # Pipeline failure (degenerate live geometry / short candles)
                # — NOT counted as skipped so the liveness residue grows, and
                # named so the probe can say which failure it was.
                _bump(RESIDUE_MTP_ARM)
                return None
            limit_entry, mtp_reason = mtp
            if mtp_reason != "ok":
                _bump("skipped")
                return None
            arm_entry, stop, tp1 = limit_entry, float(live_stop_loss), float(live_tp1)
            entry_model = ENTRY_LIMIT
        else:
            arm = compute_tuned_arm(
                setup=setup, side=side_u, entry=entry_f,
                highs=highs, lows=lows, closes=closes,
            )
            if arm is None:
                # Pipeline failure (no ATR arm / degenerate inputs) — deliberately
                # NOT counted as skipped so the liveness residue grows, and named
                # so the probe can say which failure it was.
                _bump(RESIDUE_ATR_ARM)
                return None
            stop, tp1, reason = arm
            if reason == "extension_filter":
                _bump("skipped")
                return None
            arm_entry = entry_f
            entry_model = ENTRY_IMMEDIATE
        # Late-bound store lookup (mirrors stamp_geometry_pair) — the tuned
        # arms live in the same dedicated variants ledger as @FIXED/@ATR.
        from src import geometry_ab as _gab

        rec = stamp_candidate(
            gate_name=f"{GATE_PREFIX}{setup}",
            symbol=str(symbol or ""),
            channel=str(channel or ""),
            setup_class=f"{setup}{TUNED_SUFFIX}",
            side=side_u,
            entry=arm_entry,
            stop_loss=stop,
            tp1=tp1,
            confidence=float(confidence or 0.0),
            context_key=context_key or "",
            regime=regime or "",
            valid_for_minutes=float(valid_for_minutes or 0.0),
            entry_type=entry_model,
            store=store or _gab.get_geometry_store(),
        )
        if rec is None:
            # The ledger writer declined this candidate — degenerate geometry
            # by its own guard, or an exception it already recorded. A
            # different fault from an uncomputable arm, and it lives in
            # suppression_audit rather than here.
            _bump(RESIDUE_STAMP_REFUSED)
            return None
        _last_stamp[cd_key] = mono
        _bump("stamped")
        return stop
    except Exception as exc:
        from src import fail_open

        fail_open.record("tuned_variants.stamp", exc)
        # Only counted as residue when `seen` was already incremented — an
        # exception raised before that point never entered the denominator, so
        # counting it here would make the reconciliation report a gap that is
        # not there.
        if _bumped_seen:
            _bump(RESIDUE_EXCEPTION)
        return None
