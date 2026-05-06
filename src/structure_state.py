"""Per-pair structure-state tracker — bull leg / bear leg / range.

This is Phase 3 of the chartist-eye world model.  PR-5 shipped the
multi-TF Level Book; PR-6 wired confluence as a bonus; PR-7 (this
file) gives every evaluator a "what state is this pair in right now"
verdict on top of the regime label the engine already computes.

Why we need this in addition to MarketRegime
--------------------------------------------
``regime`` (TRENDING_UP / TRENDING_DOWN / RANGING / VOLATILE / QUIET)
is BB-width + directional bias from rolling EMAs.  It tells you the
volatility shape, not the **structural** leg.  A market can be:
  - regime=VOLATILE while structurally in a clean BULL_LEG  → hold longs
  - regime=TRENDING_UP while structurally LH/LL on 4h        → trend
    is fragile; fading the 4h LH might still work
  - regime=QUIET while structurally still in a BULL_LEG      → wait
    for break of HL before fading; don't short blindly

Chartists carry this distinction automatically:
"BTC is in an uptrend on 4h" = a sequence of higher-highs (HH) and
higher-lows (HL) regardless of whether the candles look "trendy" by
volatility metrics.

Algorithm
---------
For each (symbol, TF):
  1. Find swing highs / swing lows via ``chart_patterns._find_swing_highs/lows``
     using a small order (3-4 bars on each side).
  2. Walk the most-recent N pivots (default 4) in chronological order.
  3. For each pivot, classify against the previous same-type pivot:
       higher than previous high  → HH
       lower than previous high   → LH
       higher than previous low   → HL
       lower than previous low    → LL
  4. Count ``HH+HL`` vs ``LH+LL`` in the recent set:
       ≥75% HH+HL  → BULL_LEG
       ≥75% LH+LL  → BEAR_LEG
       otherwise   → RANGE

Confidence scales linearly from 0 (mixed) to 1.0 (pure HH+HL or pure
LH+LL across the full window).

Output
------
``StructureState`` carries the verdict, the last anchor pivots, the
leg age in seconds, and a confidence score.  Call sites can ask:

    state = tracker.get_state("BTCUSDT", tf="4h")
    if state and state.state == "BULL_LEG":
        ...
    if tracker.is_aligned("BTCUSDT", "LONG", tf="4h"):
        ...

Wiring (deferred — separate PR)
-------------------------------
This PR ships the tracker only.  Evaluator integration plan:

* TPE / DIV_CONT / CLS / PDC — bonus for entries aligned with bull/bear
  structure on 4h (bonus +3 pts).
* LSR / FAR — counter-trend by design; **no penalty** for opposing
  structure (we already use a soft HTF penalty for regime).  Optionally
  stamp ``state.confidence`` for telemetry only.
* SR_FLIP / QCB — neutral (their thesis is structural break, not leg
  alignment).
* WHALE / FUNDING / LIQ_REVERSAL — no use of structure state (direction
  is internally driven from tape / cascade).

Cost
----
~50 candle reads + O(N) pivot scan per refresh.  TTL'd at 30 minutes
per (symbol, tf) so total cost is < 1 ms/cycle amortised.  Refresh on
demand from the scanner, just like LevelBook in PR-6.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np

from src.chart_patterns import _find_swing_highs, _find_swing_lows
from src.utils import get_logger

log = get_logger(__name__)


# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------

#: How many bars on each side of a pivot to require.  Smaller for higher TFs
#: where each candle is heavier.
SWING_ORDER_BY_TF: Dict[str, int] = {
    "5m": 5,
    "15m": 4,
    "1h": 3,
    "4h": 3,
    "1d": 2,
}

#: How many of the most-recent pivots to use for the leg classification.
PIVOT_WINDOW: int = 4

#: Minimum fraction of the window that must agree on a direction to call
#: BULL_LEG / BEAR_LEG.  Below this → RANGE.
LEG_DOMINANCE_THRESHOLD: float = 0.75

#: Minimum candles on a TF before we'll attempt classification.
MIN_CANDLES_BY_TF: Dict[str, int] = {
    "5m": 60,
    "15m": 40,
    "1h": 30,
    "4h": 20,
    "1d": 15,
}

#: Per-(symbol, tf) refresh TTL.  Structure shifts slowly; 30 min is plenty.
STRUCTURE_REFRESH_SEC: float = 1800.0


# ---------------------------------------------------------------------------
# StructureState
# ---------------------------------------------------------------------------


@dataclass
class StructureState:
    """The structural verdict for a (symbol, tf) pair at the time of refresh."""

    symbol: str
    tf: str
    state: str  # "BULL_LEG" | "BEAR_LEG" | "RANGE"
    confidence: float = 0.0
    pivots_in_window: int = 0
    bull_count: int = 0  # HH + HL in window
    bear_count: int = 0  # LH + LL in window
    last_HH: Optional[float] = None
    last_HL: Optional[float] = None
    last_LH: Optional[float] = None
    last_LL: Optional[float] = None
    leg_age_seconds: float = 0.0
    last_update_ts: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# Pivot classification helpers
# ---------------------------------------------------------------------------


def _candle_ts(candles: dict, idx: int) -> Optional[float]:
    """Best-effort extraction of a unix timestamp for candle *idx*."""
    ts_arr = candles.get("timestamp")
    if ts_arr is None:
        ts_arr = candles.get("time")
    if ts_arr is None:
        ts_arr = candles.get("open_time")
    if ts_arr is None:
        return None
    try:
        v = float(ts_arr[idx])
    except (TypeError, ValueError, IndexError):
        return None
    if v > 1e12:
        v /= 1000.0
    return v


def _ordered_pivots(
    highs: np.ndarray,
    lows: np.ndarray,
    order: int,
) -> List[Tuple[int, float, str]]:
    """Return ``(index, price, 'H'|'L')`` chronological pivot list."""
    h_idx = _find_swing_highs(highs, order)
    l_idx = _find_swing_lows(lows, order)
    out: List[Tuple[int, float, str]] = []
    for i in h_idx:
        out.append((i, float(highs[i]), "H"))
    for i in l_idx:
        out.append((i, float(lows[i]), "L"))
    out.sort(key=lambda t: t[0])
    return out


def _classify_recent(
    pivots: List[Tuple[int, float, str]],
    window: int = PIVOT_WINDOW,
) -> Tuple[List[str], Dict[str, Optional[float]]]:
    """Classify the last *window* pivots into HH/HL/LH/LL labels.

    Returns ``(labels, anchors)`` where anchors maps each kind to the most
    recent matching price.  Each pivot needs a previous same-type pivot
    to be classified — pivots without a comparator are skipped.
    """
    labels: List[str] = []
    anchors: Dict[str, Optional[float]] = {
        "HH": None, "HL": None, "LH": None, "LL": None,
    }

    last_high: Optional[float] = None
    last_low: Optional[float] = None
    for _idx, price, kind in pivots:
        if kind == "H":
            if last_high is not None:
                if price > last_high:
                    labels.append("HH")
                    anchors["HH"] = price
                else:
                    labels.append("LH")
                    anchors["LH"] = price
            last_high = price
        else:  # "L"
            if last_low is not None:
                if price > last_low:
                    labels.append("HL")
                    anchors["HL"] = price
                else:
                    labels.append("LL")
                    anchors["LL"] = price
            last_low = price

    # Keep only the last *window* labels (chronological tail).
    return labels[-window:], anchors


def _classify_state(labels: List[str]) -> Tuple[str, float, int, int]:
    """From the recent label list, pick BULL_LEG / BEAR_LEG / RANGE.

    Returns ``(state, confidence, bull_count, bear_count)``.
    """
    if not labels:
        return "RANGE", 0.0, 0, 0
    bull = sum(1 for l in labels if l in ("HH", "HL"))
    bear = sum(1 for l in labels if l in ("LH", "LL"))
    total = bull + bear
    if total == 0:
        return "RANGE", 0.0, 0, 0
    bull_frac = bull / total
    bear_frac = bear / total
    if bull_frac >= LEG_DOMINANCE_THRESHOLD:
        return "BULL_LEG", round(bull_frac, 3), bull, bear
    if bear_frac >= LEG_DOMINANCE_THRESHOLD:
        return "BEAR_LEG", round(bear_frac, 3), bull, bear
    # Mixed → RANGE.  Confidence is proximity-to-the-stronger-side.
    dominant = max(bull_frac, bear_frac)
    return "RANGE", round(dominant, 3), bull, bear


# ---------------------------------------------------------------------------
# StructureTracker
# ---------------------------------------------------------------------------


class StructureTracker:
    """Per-(symbol, tf) structure-state cache."""

    def __init__(self) -> None:
        self._state: Dict[Tuple[str, str], StructureState] = {}
        self._refresh_ts: Dict[Tuple[str, str], float] = {}

    def refresh(
        self, symbol: str, tf: str, candles: dict,
    ) -> Optional[StructureState]:
        """Compute and cache the structure state for (symbol, tf).

        Returns ``None`` if the candle set is too small or malformed.
        """
        min_n = MIN_CANDLES_BY_TF.get(tf, 30)
        highs_arr = candles.get("high") if isinstance(candles, dict) else None
        lows_arr = candles.get("low") if isinstance(candles, dict) else None
        if highs_arr is None or lows_arr is None:
            return None
        try:
            highs = np.asarray(highs_arr, dtype=np.float64).ravel()
            lows = np.asarray(lows_arr, dtype=np.float64).ravel()
        except (TypeError, ValueError):
            return None
        if len(highs) < min_n or len(lows) < min_n:
            return None

        order = SWING_ORDER_BY_TF.get(tf, 3)
        pivots = _ordered_pivots(highs, lows, order)
        labels, anchors = _classify_recent(pivots)
        state, confidence, bull_count, bear_count = _classify_state(labels)

        # Determine the "leg start" pivot: the earliest pivot in the window
        # that already agrees with the current state (so leg_age is the time
        # since the leg's first confirmed agreement).
        leg_age_s = 0.0
        if state in ("BULL_LEG", "BEAR_LEG"):
            target = ("HH", "HL") if state == "BULL_LEG" else ("LH", "LL")
            # Walk pivots backwards to find the last pivot WHERE the leg started
            # — i.e. the first pivot in the window that matches `target`.
            window_pivots = pivots[-PIVOT_WINDOW * 2:]  # generous slice
            agree_indices: List[int] = []
            for idx, label in zip(
                [p[0] for p in window_pivots[-len(labels):]], labels,
            ):
                if label in target:
                    agree_indices.append(idx)
            if agree_indices:
                first_idx = min(agree_indices)
                first_ts = _candle_ts(candles, first_idx)
                if first_ts is not None:
                    leg_age_s = max(0.0, time.time() - first_ts)

        st = StructureState(
            symbol=symbol,
            tf=tf,
            state=state,
            confidence=confidence,
            pivots_in_window=len(labels),
            bull_count=bull_count,
            bear_count=bear_count,
            last_HH=anchors.get("HH"),
            last_HL=anchors.get("HL"),
            last_LH=anchors.get("LH"),
            last_LL=anchors.get("LL"),
            leg_age_seconds=leg_age_s,
        )
        key = (symbol, tf)
        self._state[key] = st
        self._refresh_ts[key] = time.time()
        log.debug(
            "StructureTracker.refresh symbol={} tf={} state={} conf={:.2f} bull={} bear={}",
            symbol, tf, state, confidence, bull_count, bear_count,
        )
        return st

    def refresh_if_stale(
        self, symbol: str, tf: str, candles: dict,
        *, ttl_sec: float = STRUCTURE_REFRESH_SEC,
    ) -> Optional[StructureState]:
        """Refresh only if last update is older than ``ttl_sec`` for this key."""
        key = (symbol, tf)
        last = self._refresh_ts.get(key)
        if last is not None and (time.time() - last) < ttl_sec:
            return self._state.get(key)
        return self.refresh(symbol, tf, candles)

    def get_state(
        self, symbol: str, tf: str = "4h",
    ) -> Optional[StructureState]:
        return self._state.get((symbol, tf))

    def is_aligned(
        self, symbol: str, direction: str, tf: str = "4h",
        *, min_confidence: float = LEG_DOMINANCE_THRESHOLD,
    ) -> bool:
        """Return True iff the structure leg agrees with *direction*.

        ``direction`` is "LONG" or "SHORT".  RANGE is never aligned.
        """
        state = self._state.get((symbol, tf))
        if state is None:
            return False
        if state.confidence < min_confidence:
            return False
        d = direction.upper()
        if state.state == "BULL_LEG":
            return d == "LONG"
        if state.state == "BEAR_LEG":
            return d == "SHORT"
        return False

    def stats(self, symbol: str) -> Dict[str, str]:
        """Telemetry helper — returns a flat snapshot per TF for *symbol*."""
        out: Dict[str, str] = {}
        for (sym, tf), st in self._state.items():
            if sym == symbol:
                out[tf] = (
                    f"{st.state}@conf={st.confidence:.2f} "
                    f"bull={st.bull_count}/bear={st.bear_count}"
                )
        return out


__all__ = [
    "PIVOT_WINDOW",
    "LEG_DOMINANCE_THRESHOLD",
    "STRUCTURE_REFRESH_SEC",
    "StructureState",
    "StructureTracker",
]
