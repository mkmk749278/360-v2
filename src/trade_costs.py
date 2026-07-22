"""Trade-cost model — the missing cost term in every measured R (W1 keystone).

The autonomous stack measured edge **gross**: the suppression counterfactual booked
a win at the full R-to-TP1 and a loss at exactly -1.0R, and the realized arm divided
raw PnL% by risk% — none of them subtracted fees, funding, or slippage.  On a scalp
whose 1R stop is ~1% and whose round-trip cost is ~0.15%, that discards ~0.15R of
drag *per trade* — larger than the gross edge itself.  This module is the single,
pure place that turns a gross R into a **net** R, so every consumer (edge matrix,
suppression verdicts, controller) can steer by money instead of a cost-free proxy.

**Pure + fail-toward-gross.**  No I/O.  Any un-computable input (missing entry / stop
distance) returns the gross value unchanged — the cost model never fabricates a worse
number than it can justify, and never raises on the measurement path.

**Leverage-independent by construction.**  R normalises to risk, and both the risk
(stop distance) and the cost scale with notional, so the cost-in-R ratio is the same
at any leverage — no leverage assumption is needed here (unlike the pre-TP margin
math in ``config``).

**DARK by default.**  ``EDGE_COST_MODEL_ENABLED`` defaults False; while off,
``net_r`` returns the gross value byte-for-byte, so shipping this changes nothing
until it is shadow-enabled and owner-signed-off (production dark-first doctrine).
"""
from __future__ import annotations

from typing import Optional


def is_enabled(override: Optional[bool] = None) -> bool:
    """Master dark flag.  ``override`` lets tests pin the state without env."""
    if override is not None:
        return bool(override)
    try:
        from config import EDGE_COST_MODEL_ENABLED
        return bool(EDGE_COST_MODEL_ENABLED)
    except Exception:
        return False


def round_trip_cost_pct(
    *,
    taker_fee_round_trip_pct: Optional[float] = None,
    slippage_pct_per_side: Optional[float] = None,
    funding_pct_estimate: Optional[float] = None,
) -> float:
    """Total round-trip cost as a percent of notional price.

    = taker entry+exit fee + slippage on both sides + a per-trade funding allowance.
    Each term is config-sourced (env-overridable) but injectable for tests.
    """
    try:
        from config import (
            EDGE_FUNDING_PCT_ESTIMATE,
            EDGE_SLIPPAGE_PCT_PER_SIDE,
            EDGE_TAKER_FEE_PCT_ROUND_TRIP,
        )
        taker = EDGE_TAKER_FEE_PCT_ROUND_TRIP if taker_fee_round_trip_pct is None else taker_fee_round_trip_pct
        slip = EDGE_SLIPPAGE_PCT_PER_SIDE if slippage_pct_per_side is None else slippage_pct_per_side
        fund = EDGE_FUNDING_PCT_ESTIMATE if funding_pct_estimate is None else funding_pct_estimate
    except Exception:
        # Config not importable (bare unit test) — fall back to explicit args or 0.
        taker = taker_fee_round_trip_pct or 0.0
        slip = slippage_pct_per_side or 0.0
        fund = funding_pct_estimate or 0.0
    return float(taker) + 2.0 * float(slip) + float(fund)


def cost_in_r(entry: float, sl_distance: float, cost_pct: Optional[float] = None) -> float:
    """Round-trip cost expressed in R, where 1R = ``sl_distance`` in price terms.

    ``cost_in_r = round_trip_cost_pct / sl_distance_pct``.  Returns 0.0 when the
    geometry can't be resolved (fail-toward-gross: no phantom cost).
    """
    try:
        entry = float(entry or 0.0)
        sl_distance = float(sl_distance or 0.0)
        if entry <= 0.0 or sl_distance <= 0.0:
            return 0.0
        sl_distance_pct = sl_distance / entry * 100.0
        if sl_distance_pct <= 0.0:
            return 0.0
        c = round_trip_cost_pct() if cost_pct is None else float(cost_pct)
        return c / sl_distance_pct
    except Exception:
        return 0.0


def net_r(
    gross_r: float,
    *,
    entry: float,
    sl_distance: float,
    enabled: Optional[bool] = None,
    cost_pct: Optional[float] = None,
) -> float:
    """Gross R minus the round-trip cost in R.  Returns gross unchanged when the
    cost model is disabled or the geometry is un-computable (fail-toward-gross).

    Cost is paid regardless of outcome, so it shifts *both* a winning R and a
    losing R down by the same amount (a +2R win nets +2R-c; a -1R loss nets
    -1R-c).
    """
    try:
        gross_r = float(gross_r or 0.0)
    except (TypeError, ValueError):
        return 0.0
    if not is_enabled(enabled):
        return gross_r
    return gross_r - cost_in_r(entry, sl_distance, cost_pct=cost_pct)
