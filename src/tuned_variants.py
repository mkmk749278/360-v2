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
from src.suppression_audit import SuppressedCandidateStore, stamp_candidate
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
_counter_lock = threading.Lock()
_counters: Dict[str, int] = {"seen": 0, "stamped": 0, "skipped": 0}


def tuned_setups() -> Tuple[str, ...]:
    return ("MOVER_AVWAP_SCALP", "VOLUME_SURGE_BREAKOUT")


def counters() -> Dict[str, int]:
    with _counter_lock:
        return dict(_counters)


def _bump(key: str) -> None:
    with _counter_lock:
        _counters[key] += 1


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
    store: Optional[SuppressedCandidateStore] = None,
    now_mono: Optional[float] = None,
) -> Optional[float]:
    """Stamp the ``@TUNED`` arm for one MAS/VSB candidate (fail-open).

    Returns the tuned stop price on stamp, else ``None``.
    """
    try:
        setup = str(setup_class or "").strip().upper()
        if setup not in tuned_setups() or is_geometry_variant(setup):
            return None
        _bump("seen")
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
        arm = compute_tuned_arm(
            setup=setup, side=side_u, entry=entry_f,
            highs=highs, lows=lows, closes=closes,
        )
        if arm is None:
            # Pipeline failure (no ATR arm / degenerate inputs) — deliberately
            # NOT counted as skipped so the liveness residue grows.
            return None
        stop, tp1, reason = arm
        if reason == "extension_filter":
            _bump("skipped")
            return None
        # Late-bound store lookup (mirrors stamp_geometry_pair) — the tuned
        # arms live in the same dedicated variants ledger as @FIXED/@ATR.
        from src import geometry_ab as _gab

        rec = stamp_candidate(
            gate_name=f"{GATE_PREFIX}{setup}",
            symbol=str(symbol or ""),
            channel=str(channel or ""),
            setup_class=f"{setup}{TUNED_SUFFIX}",
            side=side_u,
            entry=entry_f,
            stop_loss=stop,
            tp1=tp1,
            confidence=float(confidence or 0.0),
            context_key=context_key or "",
            regime=regime or "",
            valid_for_minutes=float(valid_for_minutes or 0.0),
            store=store or _gab.get_geometry_store(),
        )
        if rec is None:
            return None
        _last_stamp[cd_key] = mono
        _bump("stamped")
        return stop
    except Exception as exc:
        from src import fail_open

        fail_open.record("tuned_variants.stamp", exc)
        return None
