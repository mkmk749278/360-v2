"""Shadow-only strategy units (Phase 3 of the Autonomous Portfolio).

Four candidate strategy families the live engine does NOT trade — range-fade,
mean-reversion, funding-fade, cascade-reversal (Crypto Market Doctrine §3, §5,
§6: the families that pay in the ~70% ranging/quiet tape where our trend
evaluators sit idle).  Each unit is a **pure function over primitives** the
scanner already holds in memory (15m candle arrays + the funding rate) and
returns a would-be trade with full geometry.

They have **no path to the signal queue**: the scanner routes their candidates
straight into the suppression-audit shadow ledger (``gate_name="shadow_unit:*"``),
where the 5-min audit loop forward-measures TP1-before-SL on real candles and
feeds the Strategy×Context edge matrix (``source="shadow"``).  The matrix is
where these units earn — or fail to earn — a case for ever going live.

Design notes:
* Stops are **ATR-sized, beyond the trigger extreme** (doctrine §4: fixed-%
  stops sit inside crypto's noise band; these units A/B that geometry against
  the live evaluators' in the same matrix).
* Pure + fail-neutral: bad/short inputs return no candidate, never raise.
* O(small-N list scans) per call — no I/O, no indicators engine, hot-path safe.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence

from src.strategy_portfolio import (
    SHADOW_CASCADE_REVERSAL,
    SHADOW_FUNDING_FADE,
    SHADOW_MEAN_REVERT,
    SHADOW_RANGE_FADE,
)

# Tunable thresholds (env-overridable at boot, invalidation_audit pattern).
import os

_RANGE_LOOKBACK = int(os.getenv("SHADOW_RANGE_LOOKBACK_BARS", "48"))          # 12h of 15m
_RANGE_MIN_WIDTH_ATR = float(os.getenv("SHADOW_RANGE_MIN_WIDTH_ATR", "4.0"))
_RANGE_EDGE_PROXIMITY_ATR = float(os.getenv("SHADOW_RANGE_EDGE_PROXIMITY_ATR", "0.35"))
_RANGE_MIN_EDGE_TOUCHES = int(os.getenv("SHADOW_RANGE_MIN_EDGE_TOUCHES", "2"))
_MEANREV_LOOKBACK = int(os.getenv("SHADOW_MEANREV_LOOKBACK_BARS", "20"))
_MEANREV_Z_TRIGGER = float(os.getenv("SHADOW_MEANREV_Z_TRIGGER", "2.5"))
_FUNDING_EXTREME_ABS = float(os.getenv("SHADOW_FUNDING_EXTREME_ABS", "0.001"))
_CASCADE_MIN_RANGE_ATR = float(os.getenv("SHADOW_CASCADE_MIN_RANGE_ATR", "3.0"))
_CASCADE_MIN_RECOVERY = float(os.getenv("SHADOW_CASCADE_MIN_RECOVERY", "0.5"))
_ATR_PERIOD = int(os.getenv("SHADOW_ATR_PERIOD", "14"))


@dataclass(frozen=True)
class ShadowCandidate:
    """A shadow unit's would-be trade.  Geometry only — never dispatched."""

    strategy: str
    side: str                # LONG | SHORT
    entry: float
    stop_loss: float
    tp1: float
    valid_for_minutes: float
    reason: str


def _simple_atr(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
    period: int = _ATR_PERIOD,
) -> float:
    """Plain true-range ATR over the last ``period`` closed bars.  0.0 on bad input."""
    n = min(len(highs), len(lows), len(closes))
    if n < period + 1:
        return 0.0
    trs = []
    for i in range(n - period, n):
        h, low, prev_c = float(highs[i]), float(lows[i]), float(closes[i - 1])
        trs.append(max(h - low, abs(h - prev_c), abs(low - prev_c)))
    return sum(trs) / len(trs) if trs else 0.0


def evaluate_range_fade(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
) -> Optional[ShadowCandidate]:
    """Fade at the edge of an established range, target the mid (doctrine §3:
    range tactics in accumulation/distribution; §5: the Asia-session trade)."""
    n = min(len(highs), len(lows), len(closes))
    if n < _RANGE_LOOKBACK + _ATR_PERIOD:
        return None
    atr = _simple_atr(highs, lows, closes)
    if atr <= 0:
        return None
    win_h = [float(x) for x in highs[-_RANGE_LOOKBACK:]]
    win_l = [float(x) for x in lows[-_RANGE_LOOKBACK:]]
    rng_hi, rng_lo = max(win_h), min(win_l)
    width = rng_hi - rng_lo
    price = float(closes[-1])
    if width < _RANGE_MIN_WIDTH_ATR * atr or price <= 0:
        return None  # not a tradeable range — just noise-width chop
    # A range needs *tested* edges, not one wick: count distinct bars near each.
    hi_touches = sum(1 for h in win_h if rng_hi - h <= _RANGE_EDGE_PROXIMITY_ATR * atr)
    lo_touches = sum(1 for lo in win_l if lo - rng_lo <= _RANGE_EDGE_PROXIMITY_ATR * atr)
    if hi_touches < _RANGE_MIN_EDGE_TOUCHES or lo_touches < _RANGE_MIN_EDGE_TOUCHES:
        return None
    mid = (rng_hi + rng_lo) / 2.0
    if rng_hi - price <= _RANGE_EDGE_PROXIMITY_ATR * atr:
        return ShadowCandidate(
            strategy=SHADOW_RANGE_FADE, side="SHORT", entry=price,
            stop_loss=rng_hi + atr, tp1=mid, valid_for_minutes=240.0,
            reason=f"fade range-high {rng_hi:.6g} (touches={hi_touches})",
        )
    if price - rng_lo <= _RANGE_EDGE_PROXIMITY_ATR * atr:
        return ShadowCandidate(
            strategy=SHADOW_RANGE_FADE, side="LONG", entry=price,
            stop_loss=rng_lo - atr, tp1=mid, valid_for_minutes=240.0,
            reason=f"fade range-low {rng_lo:.6g} (touches={lo_touches})",
        )
    return None


def evaluate_mean_revert(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
) -> Optional[ShadowCandidate]:
    """Fade a statistical over-extension back to the rolling mean."""
    n = len(closes)
    if n < _MEANREV_LOOKBACK + _ATR_PERIOD:
        return None
    atr = _simple_atr(highs, lows, closes)
    if atr <= 0:
        return None
    window = [float(x) for x in closes[-_MEANREV_LOOKBACK:]]
    mean = sum(window) / len(window)
    var = sum((x - mean) ** 2 for x in window) / len(window)
    sd = var ** 0.5
    price = float(closes[-1])
    if sd <= 0 or price <= 0:
        return None
    z = (price - mean) / sd
    if z >= _MEANREV_Z_TRIGGER:
        return ShadowCandidate(
            strategy=SHADOW_MEAN_REVERT, side="SHORT", entry=price,
            stop_loss=price + 1.5 * atr, tp1=mean, valid_for_minutes=180.0,
            reason=f"z={z:.2f} above {_MEANREV_LOOKBACK}-bar mean",
        )
    if z <= -_MEANREV_Z_TRIGGER:
        return ShadowCandidate(
            strategy=SHADOW_MEAN_REVERT, side="LONG", entry=price,
            stop_loss=price - 1.5 * atr, tp1=mean, valid_for_minutes=180.0,
            reason=f"z={z:.2f} below {_MEANREV_LOOKBACK}-bar mean",
        )
    return None


def evaluate_funding_fade(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
    funding_rate: Optional[float],
) -> Optional[ShadowCandidate]:
    """Fade the crowded side on a funding extreme (doctrine §6: extreme funding
    marks positioning that is about to be punished)."""
    if funding_rate is None:
        return None
    try:
        f = float(funding_rate)
    except (TypeError, ValueError):
        return None
    if abs(f) < _FUNDING_EXTREME_ABS or closes is None or len(closes) == 0:
        return None
    atr = _simple_atr(highs, lows, closes)
    price = float(closes[-1])
    if atr <= 0 or price <= 0:
        return None
    if f > 0:  # longs crowded and paying — fade long positioning
        return ShadowCandidate(
            strategy=SHADOW_FUNDING_FADE, side="SHORT", entry=price,
            stop_loss=price + 2.0 * atr, tp1=price - 1.5 * atr,
            valid_for_minutes=480.0, reason=f"funding {f:+.4%} crowded-long",
        )
    return ShadowCandidate(
        strategy=SHADOW_FUNDING_FADE, side="LONG", entry=price,
        stop_loss=price - 2.0 * atr, tp1=price + 1.5 * atr,
        valid_for_minutes=480.0, reason=f"funding {f:+.4%} crowded-short",
    )


def evaluate_cascade_reversal(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
) -> Optional[ShadowCandidate]:
    """Enter the recovery after a liquidation-cascade wick (doctrine §6): a bar
    whose range dwarfs ATR, breaks the recent extreme, and closes back
    reclaiming most of the wick — forced-flow exhaustion, not new information."""
    n = min(len(highs), len(lows), len(closes))
    if n < _ATR_PERIOD + 22:
        return None
    # Use the last CLOSED bar (index -2); -1 is still forming on live feeds.
    h, low, c = float(highs[-2]), float(lows[-2]), float(closes[-2])
    atr = _simple_atr(highs[:-1], lows[:-1], closes[:-1])
    rng = h - low
    price = float(closes[-1])
    if atr <= 0 or rng < _CASCADE_MIN_RANGE_ATR * atr or price <= 0:
        return None
    prior_lo = min(float(x) for x in lows[-22:-2])
    prior_hi = max(float(x) for x in highs[-22:-2])
    # The break of the prior extreme must itself be meaningful (≥ half an
    # ATR), otherwise a huge two-sided bar that ticks 0.1 past the prior
    # high/low would count as a "cascade through" that side.
    break_min = 0.5 * atr
    # Down-cascade: broke the prior low, then reclaimed ≥ half the bar.
    if low < prior_lo - break_min and (c - low) >= _CASCADE_MIN_RECOVERY * rng:
        return ShadowCandidate(
            strategy=SHADOW_CASCADE_REVERSAL, side="LONG", entry=price,
            stop_loss=low - 0.25 * atr, tp1=price + 0.5 * rng,
            valid_for_minutes=120.0,
            reason=f"down-cascade wick {rng / atr:.1f}×ATR reclaimed",
        )
    # Up-cascade (short squeeze): broke the prior high, then gave back ≥ half.
    if h > prior_hi + break_min and (h - c) >= _CASCADE_MIN_RECOVERY * rng:
        return ShadowCandidate(
            strategy=SHADOW_CASCADE_REVERSAL, side="SHORT", entry=price,
            stop_loss=h + 0.25 * atr, tp1=price - 0.5 * rng,
            valid_for_minutes=120.0,
            reason=f"up-cascade wick {rng / atr:.1f}×ATR rejected",
        )
    return None


def evaluate_all(
    highs: Sequence[float], lows: Sequence[float], closes: Sequence[float],
    funding_rate: Optional[float] = None,
) -> List[ShadowCandidate]:
    """Run every unit; a unit error never blocks its siblings (fail-neutral)."""
    out: List[ShadowCandidate] = []
    for fn in (
        lambda: evaluate_range_fade(highs, lows, closes),
        lambda: evaluate_mean_revert(highs, lows, closes),
        lambda: evaluate_funding_fade(highs, lows, closes, funding_rate),
        lambda: evaluate_cascade_reversal(highs, lows, closes),
    ):
        try:
            cand = fn()
            if cand is not None and cand.entry > 0 and cand.stop_loss > 0 and cand.tp1 > 0:
                out.append(cand)
        except Exception:
            continue
    return out
