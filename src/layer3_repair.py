"""Layer 3 repair — the order-block detector that never existed, and the
twelve-bar FVG window.

Phase 3 of ``docs/PRICE_ACTION_PROGRAM.md``. Two hollow primitives sit behind
gates that read as though they check two things:

* **``orderblocks`` has never had a writer.** ``SMCResult`` declares the field
  and ``orderblocks_detector_status: "not_implemented"``, and nothing in
  ``detector.py`` has ever assigned it — the VPS truth report counts 474,467
  observations, **100% empty**. So every
  ``bool(fvgs) or bool(orderblocks)`` gate in ``channels/scalp.py`` has always
  been ``bool(fvgs)`` alone, at **eight** call sites.
* **``detect_fvg`` sees twelve bars** (``lookback=10`` plus the 2-bar pattern).
  On 15m that is three hours. A gap from yesterday's structure does not exist as
  far as any evaluator is concerned — and that narrow window is what makes a
  deliberately loose gate behave like a strict one: measured on the first 89 TPE
  signals, zone distance ran a median of **0.13 ATR**, p90 0.42, max 0.52, with
  no tail. Any gap it can find is near price by construction.

Dark means the measurement runs, not that the change is off
------------------------------------------------------------
Both of these **widen a rejecting gate** when activated, so they are money-path
and ship dark-first. What that means precisely (§ Project Phase):

* the detector **actually runs**, from the moment this deploys, producing real
  output that ops renders the same day;
* ``smc_data["orderblocks"]`` stays **empty** and the live FVG list stays the
  narrow one, so every gate behaves **byte-identically**;
* the flip is the owner's, on the measured result.

Assigning the detector's output straight to ``SMCResult.orderblocks`` would ship
the *effect*, not the measurement: eight gates would immediately start passing
candidates they reject today, with nothing measured behind it. That is the
distinction the two flags exist to hold, and it is why the measured output lands
under its own key.

What the census can and cannot answer
--------------------------------------
These gates run **pre-scoring and reject**. A candidate the FVG gate kills today
has no row, no outcome and no ledger entry, so widening the window would *admit*
candidates that are currently invisible. The census therefore answers **"how much
of the book would change"** and is **structurally incapable** of answering **"how
much better it would be"** — the same survivorship bound the
``_get_primary_timeframe`` census carries. Pricing the correction needs a shadow
gate chain; saying so is cheaper than a number that looks like an answer.

One computation, not two
-------------------------
A wide lookback **subsumes** a narrow one: ``detect_fvg`` scans
``range(max(0, n - lookback - 2), n - 2)``, so the narrow result is exactly the
wide result filtered by index. Detection runs once at the wide window and the
live list is derived from it — no doubled cost on a path that runs per scan, per
symbol, per channel.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Sequence

import numpy as np

from src.smc import FVGZone, Direction
from src.utils import get_logger

log = get_logger("layer3_repair")

#: Bars of displacement to look for after a candidate order block.
OB_DISPLACEMENT_BARS = 3

#: How far the move after the block must travel, as a multiple of the block's
#: own range. Not tuned on this window — it is the definitional content of
#: "displacement" (the move must be large relative to the candle it came from),
#: and the *distribution* of the ratio rides on every row so a real threshold
#: can be picked from data rather than from this docstring.
OB_MIN_DISPLACEMENT_RATIO = 1.5


@dataclass
class Layer3Census:
    """Counters, read from the engine's own process.

    A ``docker exec`` one-shot reads the boot default, not the live tunable —
    that has already misled one diagnosis (2026-08-02).
    """

    detections: int = 0
    #: Symbols where the wide window found a gap and the narrow one did not.
    #: This is the FVG gate's would-change population.
    fvg_narrow_empty_wide_found: int = 0
    fvg_narrow_found: int = 0
    fvg_both_empty: int = 0
    fvg_wide_total: int = 0
    fvg_narrow_total: int = 0
    #: Order blocks found where the narrow FVG list was empty — i.e. where
    #: `bool(fvgs) or bool(orderblocks)` would flip from False to True.
    ob_found_when_fvg_empty: int = 0
    ob_found: int = 0
    ob_total: int = 0

    def as_dict(self) -> Dict[str, int]:
        return dict(self.__dict__)


_census = Layer3Census()


def census() -> Dict[str, int]:
    return _census.as_dict()


def reset_census() -> None:
    """Test hook."""
    global _census
    _census = Layer3Census()


def narrow_from_wide(
    wide: Sequence[FVGZone], n_bars: int, narrow_lookback: int,
) -> List[FVGZone]:
    """The exact list ``detect_fvg(..., lookback=narrow_lookback)`` would return.

    ``detect_fvg`` iterates ``i`` over ``range(max(0, n - lookback - 2), n - 2)``
    and stamps ``index = i + 1``, applying the same width filter at every ``i``.
    So the narrow result is the wide result restricted to ``i >= start``, in the
    same order — this is a filter, not a re-derivation, and that is what makes
    the live path byte-identical rather than merely equivalent.
    """
    start = max(0, n_bars - narrow_lookback - 2)
    return [z for z in wide if (z.index - 1) >= start]


def detect_orderblocks(
    high: Any,
    low: Any,
    close: Any,
    open_: Any = None,
    *,
    lookback: int = 40,
    displacement_bars: int = OB_DISPLACEMENT_BARS,
    min_displacement_ratio: float = OB_MIN_DISPLACEMENT_RATIO,
) -> List[Dict[str, Any]]:
    """The last opposing candle before a displacement move.

    An order block is the final down-candle before an impulsive move up (bullish)
    or the final up-candle before an impulsive move down (bearish). The
    displacement requirement is what separates it from "any candle": without it,
    every second bar qualifies and the output is noise wearing a name.

    Returns plain dicts using **``gap_high`` / ``gap_low``** — the same
    vocabulary ``FVGZone`` uses — because ``_funding_extreme_structure_tp1``
    consumes ``list(fvgs) + list(orderblocks)`` through one reader and prices a
    zone by those keys first. A producer inventing its own field names there is
    the ``zone_distance_atr`` failure exactly: the reader skips every zone it
    cannot price, and skipping is indistinguishable from having none.

    ``§2`` of the program is blunt that order blocks have **no validation
    distinct from support/resistance**. This exists to be measured and deleted
    if it does not discriminate, not because the construct is believed.
    """
    h = np.asarray(high, dtype=np.float64).ravel()
    l = np.asarray(low, dtype=np.float64).ravel()
    c = np.asarray(close, dtype=np.float64).ravel()
    o = (
        np.asarray(open_, dtype=np.float64).ravel()
        if open_ is not None else None
    )
    n = len(c)
    if n < displacement_bars + 2 or len(h) != n or len(l) != n:
        return []
    if o is not None and len(o) != n:
        o = None

    out: List[Dict[str, Any]] = []
    start = max(0, n - lookback - displacement_bars)
    for i in range(start, n - displacement_bars):
        body_high, body_low = h[i], l[i]
        rng = body_high - body_low
        if rng <= 0:
            continue
        # Direction of candle i. Without an open array, fall back to the
        # previous close — stated rather than silently assumed, because the
        # store does carry `open` and a caller that omits it gets a slightly
        # different (not wrong) classification.
        if o is not None:
            bullish_candle = c[i] > o[i]
        elif i > 0:
            bullish_candle = c[i] > c[i - 1]
        else:
            continue

        window_hi = float(np.max(h[i + 1: i + 1 + displacement_bars]))
        window_lo = float(np.min(l[i + 1: i + 1 + displacement_bars]))

        # Bullish OB: a DOWN candle, then an impulsive move up away from it.
        if not bullish_candle:
            move = window_hi - body_high
            if move >= rng * min_displacement_ratio:
                out.append({
                    "index": i,
                    "direction": Direction.LONG,
                    "gap_high": float(body_high),
                    "gap_low": float(body_low),
                    "displacement_ratio": float(move / rng),
                    "kind": "orderblock",
                })
        # Bearish OB: an UP candle, then an impulsive move down away from it.
        else:
            move = body_low - window_lo
            if move >= rng * min_displacement_ratio:
                out.append({
                    "index": i,
                    "direction": Direction.SHORT,
                    "gap_high": float(body_high),
                    "gap_low": float(body_low),
                    "displacement_ratio": float(move / rng),
                    "kind": "orderblock",
                })
    return out


def observe(
    *,
    fvg_narrow: Sequence[Any],
    fvg_wide: Sequence[Any],
    orderblocks: Sequence[Any],
) -> None:
    """Fold one detection into the census.

    Counted per **detection**, not per zone, because the gate asks a yes/no
    question (``bool(fvgs)``) and a rate over zones would move with how many
    gaps a volatile symbol happens to carry rather than with how often the gate
    would change its answer.
    """
    _census.detections += 1
    _census.fvg_wide_total += len(fvg_wide)
    _census.fvg_narrow_total += len(fvg_narrow)
    _census.ob_total += len(orderblocks)
    if fvg_narrow:
        _census.fvg_narrow_found += 1
    elif fvg_wide:
        # The FVG gate rejects today and would pass on the wider window.
        _census.fvg_narrow_empty_wide_found += 1
    else:
        _census.fvg_both_empty += 1
    if orderblocks:
        _census.ob_found += 1
        if not fvg_narrow:
            # `bool(fvgs) or bool(orderblocks)` flips False -> True here, which
            # is the whole of what implementing the detector would change.
            _census.ob_found_when_fvg_empty += 1


def orderblocks_live() -> bool:
    """Should the detector's output reach ``SMCResult.orderblocks``?

    Default False. While False, eight gates behave byte-identically and the
    detector is a measurement — which is what dark means.
    """
    try:
        from config import ORDERBLOCKS_LIVE
        return bool(ORDERBLOCKS_LIVE)
    except Exception:  # noqa: BLE001
        return False


def fvg_wide_live() -> bool:
    """Should the wide FVG list be the one the gates read? Default False."""
    try:
        from config import FVG_WIDE_LIVE
        return bool(FVG_WIDE_LIVE)
    except Exception:  # noqa: BLE001
        return False


def lookbacks() -> tuple[int, int]:
    """``(live_narrow, measured_wide)``."""
    try:
        from config import FVG_LOOKBACK, FVG_LOOKBACK_WIDE
        return int(FVG_LOOKBACK), int(FVG_LOOKBACK_WIDE)
    except Exception:  # noqa: BLE001
        return 10, 60


def orderblocks_enabled() -> bool:
    try:
        from config import ORDERBLOCKS_MEASURE
        return bool(ORDERBLOCKS_MEASURE)
    except Exception:  # noqa: BLE001
        return True


def detector_status() -> str:
    """What ``orderblocks_detector_status`` should say now.

    A named state, never a boolean: ``not_implemented`` was true for years and
    the whole reason the hollow gate survived is that a dead primitive behind a
    passing gate looks identical to a working one.
    """
    if not orderblocks_enabled():
        return "measure_disabled"
    return "measured_live" if orderblocks_live() else "measured_dark"
