"""Structural level detection for SL/TP placement.

Identifies key price levels from market structure (swing highs/lows,
round numbers, and VPOC/volume clusters) to place SL and TP at
meaningful levels where price is likely to react.

``find_structural_sl`` / ``find_structural_tp`` return a price and nothing
else, which is all the money path needs and strictly less than a measurement
needs: an all-"unchanged" column is a claim about the *reader* before it is a
claim about the market, and with a bare price there is no way to tell "no level
was in the band" from "a level was in the band and it happened to sit where the
arithmetic already put it".  The ``*_detail`` siblings answer that — they are
the implementation, and the two price-only functions are thin wrappers over
them, so there is one selection rule rather than a copy that drifts.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np


@dataclass(frozen=True)
class LevelPick:
    """One structural-level selection, with the provenance of the pick.

    ``price`` is what the caller should use (buffered, for SL).  ``level`` is
    the raw structural level before any buffer — the two differ by the 0.1%
    SL buffer and are identical for TP.  ``source`` names which generator
    supplied it, because they do not have the same standing: a swing low is
    something the market actually traded at and rejected, a round number is a
    psychological level we injected ourselves, and on a sub-$1 pair the round
    grid is 20% wide (see ``find_round_numbers``) and therefore contributes
    nothing at all.  Pooling the two and reporting "snapped" would hide that.
    """

    price: float
    source: str          # "swing" | "round" | "both" | "none"
    level: float
    n_candidates: int


def _classify_source(level: float, swings: List[float], rounds: List[float]) -> str:
    in_swing = any(abs(level - s) <= 1e-12 for s in swings)
    in_round = any(abs(level - r) <= 1e-12 for r in rounds)
    if in_swing and in_round:
        return "both"
    if in_swing:
        return "swing"
    if in_round:
        return "round"
    return "none"


# ---------------------------------------------------------------------------
# Swing highs / lows
# ---------------------------------------------------------------------------

def find_swing_levels(
    highs: np.ndarray,
    lows: np.ndarray,
    closes: np.ndarray,
    lookback: int = 20,
) -> Dict[str, List[float]]:
    """Return recent swing highs and swing lows.

    A swing high is a candle whose high is the local maximum within ±3 candles.
    A swing low is a candle whose low is the local minimum within ±3 candles.

    Only the last *lookback* candles are scanned (the most recent structure).
    """
    swing_highs: List[float] = []
    swing_lows: List[float] = []
    window = 3

    n = len(highs)
    if n < 2 * window + 1:
        return {"swing_highs": swing_highs, "swing_lows": swing_lows}

    start = max(window, n - lookback)
    end = n - window

    for i in range(start, end):
        # Swing high: highs[i] >= all highs in [i-window .. i+window]
        if highs[i] == np.max(highs[i - window : i + window + 1]):
            swing_highs.append(float(highs[i]))
        # Swing low: lows[i] <= all lows in [i-window .. i+window]
        if lows[i] == np.min(lows[i - window : i + window + 1]):
            swing_lows.append(float(lows[i]))

    return {"swing_highs": swing_highs, "swing_lows": swing_lows}


# ---------------------------------------------------------------------------
# Round numbers
# ---------------------------------------------------------------------------

def round_step_for(price: float) -> float:
    """The round-number grid spacing at *price*.

    Exposed separately because the grid is **absolute** while everything that
    consumes it is relative, so its usefulness varies by orders of magnitude
    across the same book: at $50,000 the grid is 0.2% wide and lands several
    levels inside any plausible stop band; at $0.05 it is 20% wide and no round
    number can ever fall inside one.  A large part of the delivered book is
    sub-$1 movers, where this generator is therefore **inert** rather than
    wrong — it contributes no candidates at all.

    That is stamped (``round_step_pct``) rather than fixed.  Making the grid
    scale-relative would change which levels exist, and the threshold for
    "meaningful round number on a sub-cent alt" is not derivable from the code
    that already exists — it would be a number invented to fit this window,
    which is the move this repo has paid for before.  Measure first.
    """
    if price > 1000:
        return 100.0
    if price > 100:
        return 10.0
    if price > 10:
        return 1.0
    if price > 1:
        return 0.1
    return 0.01


def find_round_numbers(price: float, count: int = 5) -> List[float]:
    """Return the *count* nearest round numbers above and below *price*.

    The rounding step depends on the price magnitude:
    * price > 1000  →  step = 100
    * price > 100   →  step = 10
    * price > 10    →  step = 1
    * price > 1     →  step = 0.1
    * price <= 1    →  step = 0.01
    """
    step = round_step_for(price)
    base = (price // step) * step
    levels: List[float] = []
    for offset in range(-count, count + 1):
        levels.append(round(base + offset * step, 8))
    return sorted(set(levels))


# ---------------------------------------------------------------------------
# Structural SL adjustment
# ---------------------------------------------------------------------------

def find_structural_sl_detail(
    direction: str,
    entry: float,
    atr_sl: float,
    swing_levels: Dict[str, List[float]],
    round_numbers: List[float],
    atr_val: float,
    min_atr_mult: float = 0.7,
    max_atr_mult: float = 1.3,
) -> LevelPick:
    """Adjust the ATR-based SL to a nearby structural level, with provenance.

    For LONG trades the SL must sit below *entry*.  We look for the nearest
    swing low or round number between ``entry - atr_val * max_atr_mult`` and
    ``entry - atr_val * min_atr_mult`` and place the SL just below it (0.1 %
    buffer).

    For SHORT trades, mirror logic using swing highs above entry.

    If no structural level is found within the acceptable range the original
    *atr_sl* is returned unchanged, with ``source="none"``.

    Note on ``atr_val``: every caller passes the signal's own **SL distance**,
    not an ATR, so the search band is 0.7–1.3× the risk the evaluator designed.
    That bound is the whole safety property of this function — the snap can
    tighten a stop by at most 30% and widen it by at most 30%, so it can never
    turn a 3% stop into a 0.5% one.  The parameter name is kept for
    backwards-compatibility with the existing signature.
    """
    direction_str = str(direction).upper()
    buffer_pct = 0.001  # 0.1 %

    if "LONG" in direction_str:
        lower_bound = entry - atr_val * max_atr_mult
        upper_bound = entry - atr_val * min_atr_mult
        swings = list(swing_levels.get("swing_lows", []))
        candidates = swings + list(round_numbers)
        valid = [lvl for lvl in candidates if lower_bound <= lvl <= upper_bound]
        if valid:
            best = max(valid)  # closest to entry → tightest SL
            return LevelPick(
                price=round(best * (1.0 - buffer_pct), 8),
                source=_classify_source(best, swings, list(round_numbers)),
                level=float(best),
                n_candidates=len(valid),
            )
    else:
        lower_bound = entry + atr_val * min_atr_mult
        upper_bound = entry + atr_val * max_atr_mult
        swings = list(swing_levels.get("swing_highs", []))
        candidates = swings + list(round_numbers)
        valid = [lvl for lvl in candidates if lower_bound <= lvl <= upper_bound]
        if valid:
            best = min(valid)  # closest to entry → tightest SL
            return LevelPick(
                price=round(best * (1.0 + buffer_pct), 8),
                source=_classify_source(best, swings, list(round_numbers)),
                level=float(best),
                n_candidates=len(valid),
            )

    return LevelPick(price=atr_sl, source="none", level=atr_sl, n_candidates=0)


def find_structural_sl(
    direction: str,
    entry: float,
    atr_sl: float,
    swing_levels: Dict[str, List[float]],
    round_numbers: List[float],
    atr_val: float,
    min_atr_mult: float = 0.7,
    max_atr_mult: float = 1.3,
) -> float:
    """Price-only view of :func:`find_structural_sl_detail`."""
    return find_structural_sl_detail(
        direction, entry, atr_sl, swing_levels, round_numbers, atr_val,
        min_atr_mult, max_atr_mult,
    ).price


# ---------------------------------------------------------------------------
# Structural TP adjustment
# ---------------------------------------------------------------------------

def find_structural_tp_detail(
    direction: str,
    entry: float,
    atr_tp: float,
    swing_levels: Dict[str, List[float]],
    round_numbers: List[float],
    atr_val: float = 0.0,
) -> LevelPick:
    """Adjust TP1 to a nearby structural level, with provenance.

    For LONG trades, look for the nearest resistance (swing high or round
    number) within 0.8–1.2 × the ATR TP distance.  If a structural level is
    *closer* than the ATR-based TP we take profit early (before resistance).
    If it is farther we keep the ATR-based TP to avoid reducing the target
    unnecessarily.

    For SHORT trades, mirror logic with swing lows as support.

    **This function only ever moves TP1 nearer**, never further, and by at most
    20%.  That direction is deliberate and it is the one the evidence supports:
    on 2026-08-01 the opposite move — flooring `TREND_PULLBACK_EMA`'s TP1 at
    1.0R — was simulated on the dark window and took the book from −0.081R to
    as low as −0.836R, because the winners barely clear their current targets
    (median hit 0.59R against a 0.89R peak).  A structural cap harvests a small
    move in front of resistance; a structural *extension* would be the change
    that measurement already argues against.

    ``atr_val`` is unused — it is accepted so the signature matches the SL
    sibling and the existing call sites.
    """
    direction_str = str(direction).upper()
    tp_dist = abs(atr_tp - entry)

    if "LONG" in direction_str:
        lower_bound = entry + tp_dist * 0.8
        upper_bound = entry + tp_dist * 1.2
        swings = list(swing_levels.get("swing_highs", []))
        candidates = swings + list(round_numbers)
        valid = [lvl for lvl in candidates if lower_bound <= lvl <= upper_bound]
        if valid:
            best = min(valid)  # closest resistance → take profit before it
            if best <= atr_tp:
                return LevelPick(
                    price=round(best, 8),
                    source=_classify_source(best, swings, list(round_numbers)),
                    level=float(best),
                    n_candidates=len(valid),
                )
    else:
        lower_bound = entry - tp_dist * 1.2
        upper_bound = entry - tp_dist * 0.8
        swings = list(swing_levels.get("swing_lows", []))
        candidates = swings + list(round_numbers)
        valid = [lvl for lvl in candidates if lower_bound <= lvl <= upper_bound]
        if valid:
            best = max(valid)  # closest support → take profit before it
            if best >= atr_tp:
                return LevelPick(
                    price=round(best, 8),
                    source=_classify_source(best, swings, list(round_numbers)),
                    level=float(best),
                    n_candidates=len(valid),
                )

    return LevelPick(price=atr_tp, source="none", level=atr_tp, n_candidates=0)


def find_structural_tp(
    direction: str,
    entry: float,
    atr_tp: float,
    swing_levels: Dict[str, List[float]],
    round_numbers: List[float],
    atr_val: float,
) -> float:
    """Price-only view of :func:`find_structural_tp_detail`."""
    return find_structural_tp_detail(
        direction, entry, atr_tp, swing_levels, round_numbers, atr_val,
    ).price
