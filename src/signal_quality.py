"""Signal-quality helpers for scanner funnel classification and scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

from src.regime import MarketRegime
from src.smc import Direction
from src.utils import get_logger, price_decimal_fmt

log = get_logger("signal_quality")


class SetupClass(str, Enum):
    TREND_PULLBACK_CONTINUATION = "TREND_PULLBACK_CONTINUATION"
    TREND_PULLBACK_EMA = "TREND_PULLBACK_EMA"
    BREAKOUT_RETEST = "BREAKOUT_RETEST"
    LIQUIDITY_SWEEP_REVERSAL = "LIQUIDITY_SWEEP_REVERSAL"
    LIQUIDATION_REVERSAL = "LIQUIDATION_REVERSAL"
    RANGE_REJECTION = "RANGE_REJECTION"
    MOMENTUM_EXPANSION = "MOMENTUM_EXPANSION"
    EXHAUSTION_FADE = "EXHAUSTION_FADE"
    RANGE_FADE = "RANGE_FADE"
    WHALE_MOMENTUM = "WHALE_MOMENTUM"
    MULTI_STRATEGY_CONFLUENCE = "MULTI_STRATEGY_CONFLUENCE"
    VOLUME_SURGE_BREAKOUT = "VOLUME_SURGE_BREAKOUT"
    BREAKDOWN_SHORT = "BREAKDOWN_SHORT"
    OPENING_RANGE_BREAKOUT = "OPENING_RANGE_BREAKOUT"
    SR_FLIP_RETEST = "SR_FLIP_RETEST"
    FUNDING_EXTREME_SIGNAL = "FUNDING_EXTREME_SIGNAL"
    QUIET_COMPRESSION_BREAK = "QUIET_COMPRESSION_BREAK"
    DIVERGENCE_CONTINUATION = "DIVERGENCE_CONTINUATION"
    CONTINUATION_LIQUIDITY_SWEEP = "CONTINUATION_LIQUIDITY_SWEEP"
    POST_DISPLACEMENT_CONTINUATION = "POST_DISPLACEMENT_CONTINUATION"
    FAILED_AUCTION_RECLAIM = "FAILED_AUCTION_RECLAIM"
    # PR-01: auxiliary-channel evaluator identities — preserved as distinct setup classes
    # so that downstream scoring and suppression diagnostics reflect true channel intent.
    FVG_RETEST = "FVG_RETEST"
    FVG_RETEST_HTF_CONFLUENCE = "FVG_RETEST_HTF_CONFLUENCE"
    RSI_MACD_DIVERGENCE = "RSI_MACD_DIVERGENCE"
    SMC_ORDERBLOCK = "SMC_ORDERBLOCK"


class PortfolioRole(str, Enum):
    """Explicit portfolio role assigned to each active signal path.

    Roles formalise the intentional business-grade structure of the signal
    portfolio (roadmap step 8).  Every active evaluator must appear in
    ACTIVE_PATH_PORTFOLIO_ROLES with exactly one of these roles.

    core       — primary business signal generators; broad-regime applicability,
                 highest expected contribution to live signal output.
    support    — meaningful situational contributors; fire reliably in specific
                 but commonly-occurring market conditions.
    specialist — low-frequency or narrow-context paths; high-selectivity, only
                 valid in precise conditions, rarely fires in normal operation.
    """

    CORE = "core"
    SUPPORT = "support"
    SPECIALIST = "specialist"


# Approved portfolio-role taxonomy — exactly the three roles above.
APPROVED_PORTFOLIO_ROLES: frozenset[PortfolioRole] = frozenset(PortfolioRole)

# Explicit portfolio-role assignment for every active signal path produced by
# live evaluators (ScalpChannel._evaluate_* methods, roadmap steps 1–7).
# This mapping is the canonical record of portfolio intent for the engine.
# Any new evaluator added to ScalpChannel.evaluate() must also be added here.
ACTIVE_PATH_PORTFOLIO_ROLES: Dict[SetupClass, PortfolioRole] = {
    # ── core ──────────────────────────────────────────────────────────────
    # Primary business signal generators.  Wide regime applicability and the
    # highest expected share of live signal output.
    SetupClass.LIQUIDITY_SWEEP_REVERSAL: PortfolioRole.CORE,
    SetupClass.TREND_PULLBACK_EMA: PortfolioRole.CORE,
    SetupClass.VOLUME_SURGE_BREAKOUT: PortfolioRole.CORE,
    SetupClass.BREAKDOWN_SHORT: PortfolioRole.CORE,
    SetupClass.SR_FLIP_RETEST: PortfolioRole.CORE,
    SetupClass.CONTINUATION_LIQUIDITY_SWEEP: PortfolioRole.CORE,
    SetupClass.POST_DISPLACEMENT_CONTINUATION: PortfolioRole.CORE,
    # ── support ───────────────────────────────────────────────────────────
    # Situational contributors.  Fire in specific but commonly-occurring
    # conditions and provide meaningful signal diversity.
    SetupClass.LIQUIDATION_REVERSAL: PortfolioRole.SUPPORT,
    SetupClass.DIVERGENCE_CONTINUATION: PortfolioRole.SUPPORT,
    SetupClass.OPENING_RANGE_BREAKOUT: PortfolioRole.SUPPORT,  # disabled by default (PR-06); role preserved pending proper rebuild
    SetupClass.FAILED_AUCTION_RECLAIM: PortfolioRole.SUPPORT,
    # ── specialist ────────────────────────────────────────────────────────
    # Low-frequency, narrow-context, high-selectivity paths.  Valid only
    # under precise market conditions and expected to fire rarely.
    SetupClass.WHALE_MOMENTUM: PortfolioRole.SPECIALIST,
    SetupClass.FUNDING_EXTREME_SIGNAL: PortfolioRole.SPECIALIST,
    SetupClass.QUIET_COMPRESSION_BREAK: PortfolioRole.SPECIALIST,
    # NOTE: Auxiliary channel identities (FVG_RETEST, FVG_RETEST_HTF_CONFLUENCE,
    # RSI_MACD_DIVERGENCE, SMC_ORDERBLOCK) are registered as SetupClass values and
    # preserved through the pipeline (PR-01) but are intentionally absent from this
    # mapping.  They are sub-evaluators of auxiliary channels (360_SCALP_FVG,
    # 360_SCALP_DIVERGENCE, 360_SCALP_ORDERBLOCK) whose portfolio role is expressed
    # through their parent channel's enabled/disabled state, not via a standalone
    # path-portfolio-role entry.
}

# PR-02: Setup classes whose evaluator-authored structural SL/TP geometry must be
# preserved through downstream risk-plan handling.  For these paths the evaluator
# already computed method-specific, structurally-anchored SL and measured-move or
# band-width TPs; generic ATR/structure recomputation must not overwrite them.
# Universal hard controls (max SL %, near-zero SL guard, directional sanity,
# minimum R:R) are still enforced after the evaluator geometry is applied.
# FAILED_AUCTION_RECLAIM is handled by its own dedicated block and is NOT
# included here to avoid duplicating its structure override logic.
# SR_FLIP_RETEST is included because its SL is anchored to the flipped structural
# level (not a generic swing) and its TP1/TP2 are swing-high/4h structural targets.
STRUCTURAL_SLTP_PROTECTED_SETUPS: frozenset[SetupClass] = frozenset({
    SetupClass.POST_DISPLACEMENT_CONTINUATION,
    SetupClass.VOLUME_SURGE_BREAKOUT,
    SetupClass.BREAKDOWN_SHORT,
    SetupClass.QUIET_COMPRESSION_BREAK,
    SetupClass.TREND_PULLBACK_EMA,
    SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
    SetupClass.SR_FLIP_RETEST,
    SetupClass.LIQUIDATION_REVERSAL,    # Fibonacci retrace TPs (Type D — Reversion)
    SetupClass.DIVERGENCE_CONTINUATION, # swing-based TPs from divergence detection window
    SetupClass.FUNDING_EXTREME_SIGNAL,  # liquidation-cluster SL + structural FVG/OB TP1
})


class MarketState(str, Enum):
    STRONG_TREND = "STRONG_TREND"
    WEAK_TREND = "WEAK_TREND"
    CLEAN_RANGE = "CLEAN_RANGE"
    DIRTY_RANGE = "DIRTY_RANGE"
    BREAKOUT_EXPANSION = "BREAKOUT_EXPANSION"
    VOLATILE_UNSUITABLE = "VOLATILE_UNSUITABLE"


class QualityTier(str, Enum):
    A_PLUS = "A+"
    A = "A"
    B = "B"
    C = "C"


CHANNEL_SETUP_COMPATIBILITY: Dict[str, set[SetupClass]] = {
    "360_SCALP": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.MOMENTUM_EXPANSION,
        SetupClass.WHALE_MOMENTUM,
        SetupClass.RANGE_FADE,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.DIVERGENCE_CONTINUATION,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        SetupClass.FAILED_AUCTION_RECLAIM,
    },
    "360_SCALP_FVG": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.RANGE_REJECTION,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        # PR-01: preserve evaluator-authored FVG identities as distinct setup classes
        SetupClass.FVG_RETEST,
        SetupClass.FVG_RETEST_HTF_CONFLUENCE,
    },
    "360_SCALP_CVD": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.RANGE_REJECTION,
        SetupClass.RANGE_FADE,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
    },
    "360_SCALP_VWAP": {
        SetupClass.RANGE_REJECTION,
        SetupClass.RANGE_FADE,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
    },
    "360_SCALP_DIVERGENCE": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.RANGE_REJECTION,
        SetupClass.RANGE_FADE,
        SetupClass.EXHAUSTION_FADE,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        # PR-01: preserve evaluator-authored divergence identity
        SetupClass.RSI_MACD_DIVERGENCE,
    },
    "360_SCALP_SUPERTREND": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.MOMENTUM_EXPANSION,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
    },
    "360_SCALP_ICHIMOKU": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
    },
    "360_SCALP_ORDERBLOCK": {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.RANGE_REJECTION,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        # PR-01: preserve evaluator-authored orderblock identity
        SetupClass.SMC_ORDERBLOCK,
    },
}


REGIME_SETUP_COMPATIBILITY: Dict[MarketState, set[SetupClass]] = {
    MarketState.STRONG_TREND: {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.MOMENTUM_EXPANSION,
        SetupClass.WHALE_MOMENTUM,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.DIVERGENCE_CONTINUATION,
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        # PR-01: aux channel identities valid in strong trend
        SetupClass.FVG_RETEST,
        SetupClass.FVG_RETEST_HTF_CONFLUENCE,
        SetupClass.RSI_MACD_DIVERGENCE,
        SetupClass.SMC_ORDERBLOCK,
    },
    MarketState.WEAK_TREND: {
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.WHALE_MOMENTUM,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.DIVERGENCE_CONTINUATION,
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        # FAR: valid in weak trend — breakouts often fail when trend conviction is low
        SetupClass.FAILED_AUCTION_RECLAIM,
        # PR-01: aux channel identities valid in weak trend
        SetupClass.FVG_RETEST,
        SetupClass.FVG_RETEST_HTF_CONFLUENCE,
        SetupClass.RSI_MACD_DIVERGENCE,
        SetupClass.SMC_ORDERBLOCK,
    },
    MarketState.CLEAN_RANGE: {
        SetupClass.RANGE_REJECTION,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.EXHAUSTION_FADE,
        SetupClass.RANGE_FADE,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.LIQUIDATION_REVERSAL,
        # FAR: prime regime — failed breakouts at range extremes are the canonical setup
        SetupClass.FAILED_AUCTION_RECLAIM,
        # PR-01: divergence and orderblock are valid at range boundaries
        SetupClass.RSI_MACD_DIVERGENCE,
        SetupClass.SMC_ORDERBLOCK,
    },
    MarketState.DIRTY_RANGE: {
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.RANGE_FADE,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        SetupClass.SR_FLIP_RETEST,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.QUIET_COMPRESSION_BREAK,
        SetupClass.LIQUIDATION_REVERSAL,
        # FAR: valid in dirty range — structure still exists despite noise
        SetupClass.FAILED_AUCTION_RECLAIM,
        # PR-01: divergence valid in dirty range (trend exhaustion detection)
        SetupClass.RSI_MACD_DIVERGENCE,
    },
    MarketState.BREAKOUT_EXPANSION: {
        SetupClass.BREAKOUT_RETEST,
        SetupClass.MOMENTUM_EXPANSION,
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.TREND_PULLBACK_EMA,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        SetupClass.WHALE_MOMENTUM,
        SetupClass.MULTI_STRATEGY_CONFLUENCE,
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        SetupClass.LIQUIDATION_REVERSAL,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP,
        SetupClass.POST_DISPLACEMENT_CONTINUATION,
        # FAR: false breakouts at expansion boundaries are structurally valid
        SetupClass.FAILED_AUCTION_RECLAIM,
        # PR-01: FVG and orderblock frequently form at expansion boundaries
        SetupClass.FVG_RETEST,
        SetupClass.FVG_RETEST_HTF_CONFLUENCE,
        SetupClass.SMC_ORDERBLOCK,
    },
    MarketState.VOLATILE_UNSUITABLE: {
        # Whale-driven and liquidity-sweep signals are valid precisely in
        # volatile conditions — large actor moves and sweep-driven reversals
        # are market events that occur during volatility spikes.  All other
        # setup classes require more orderly price action.
        SetupClass.WHALE_MOMENTUM,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
        # Volume surge breakout/breakdown are designed for volatile conditions
        SetupClass.VOLUME_SURGE_BREAKOUT,
        SetupClass.BREAKDOWN_SHORT,
        SetupClass.OPENING_RANGE_BREAKOUT,
        SetupClass.FUNDING_EXTREME_SIGNAL,
        # PR-ARCH-7B: liquidation-reversal setups are specifically designed for
        # cascade / panic / volatile conditions — suppressing them in
        # VOLATILE_UNSUITABLE is architecturally wrong.
        SetupClass.LIQUIDATION_REVERSAL,
    },
}

# Maximum SL distance (as a percentage of entry) allowed per channel.
# Signals whose structure-based SL would exceed this cap are clamped.
_MAX_SL_PCT_BY_CHANNEL: Dict[str, float] = {
    "360_SCALP": 1.5,
    "360_SCALP_FVG": 1.0,
    "360_SCALP_CVD": 1.0,
    "360_SCALP_VWAP": 1.0,
    "360_SCALP_DIVERGENCE": 1.0,
    "360_SCALP_SUPERTREND": 1.2,
    "360_SCALP_ICHIMOKU": 1.2,
    "360_SCALP_ORDERBLOCK": 1.0,
}

# Family-aware minimum R:R thresholds used in build_risk_plan().
# Quick-exit families accept a lower first target because their trade thesis
# resolves faster; trend / breakout families require a larger reward cushion.
_MIN_RR_RANGE: float = 0.8           # Range rejection / range fade — BB or extreme fade
_MIN_RR_MEAN_REVERSION: float = 0.9  # Snap-back / funding extreme — fast thesis resolution
_MIN_RR_STRUCTURED: float = 1.0      # S/R flip retest — structural confirmation at level
_MIN_RR_DEFAULT: float = 1.2         # All other families — standard minimum R:R


def _min_rr_for_setup(setup: SetupClass) -> float:
    """Return canonical minimum R:R (reward/risk) by setup family policy."""
    if setup in (SetupClass.RANGE_REJECTION, SetupClass.RANGE_FADE):
        return _MIN_RR_RANGE
    if setup in (SetupClass.LIQUIDATION_REVERSAL, SetupClass.FUNDING_EXTREME_SIGNAL):
        return _MIN_RR_MEAN_REVERSION
    if setup in (SetupClass.SR_FLIP_RETEST, SetupClass.FAILED_AUCTION_RECLAIM):
        return _MIN_RR_STRUCTURED
    return _MIN_RR_DEFAULT


def _channel_max_sl_pct(channel: str) -> float:
    """Return channel max-SL decimal; unknown channels fall back to 5.0%."""
    return _MAX_SL_PCT_BY_CHANNEL.get(channel, 5.0) / 100.0


def validate_geometry_against_policy(
    signal: Any,
    setup: SetupClass,
    channel: str,
    *,
    max_sl_distance: Optional[float] = None,
) -> tuple[bool, str]:
    """Validate signal geometry against canonical SL/TP policy.

    This is shared by scanner post-predictive revalidation to avoid duplicating
    risk-policy constants or setup RR doctrine outside this module.
    """
    entry = _safe_float(getattr(signal, "entry", None), 0.0)
    stop = _safe_float(getattr(signal, "stop_loss", None), 0.0)
    tp1 = _safe_float(getattr(signal, "tp1", None), 0.0)
    tp2 = _safe_float(getattr(signal, "tp2", None), 0.0)
    tp3_raw = getattr(signal, "tp3", None)
    tp3 = _safe_float(tp3_raw, 0.0) if tp3_raw is not None else None

    if entry <= 0:
        return False, "invalid_entry"
    if any(not np.isfinite(v) for v in (entry, stop, tp1, tp2)):
        return False, "non_finite_geometry"
    if tp3 is not None and not np.isfinite(tp3):
        return False, "non_finite_geometry"
    if stop <= 0 or tp1 <= 0 or tp2 <= 0 or (tp3 is not None and tp3 <= 0):
        return False, "non_positive_geometry"

    direction = getattr(signal, "direction", None)
    if direction == Direction.LONG:
        if stop >= entry:
            return False, "sl_wrong_side"
        if tp1 <= entry or tp2 <= entry or (tp3 is not None and tp3 <= entry):
            return False, "tp_wrong_side"
        if not (tp1 < tp2 and (tp3 is None or tp2 < tp3)):
            return False, "tp_order_invalid"
    elif direction == Direction.SHORT:
        if stop <= entry:
            return False, "sl_wrong_side"
        if tp1 >= entry or tp2 >= entry or (tp3 is not None and tp3 >= entry):
            return False, "tp_wrong_side"
        if not (tp1 > tp2 and (tp3 is None or tp2 > tp3)):
            return False, "tp_order_invalid"

    risk = abs(entry - stop)
    if risk < entry * 0.0005:
        return False, "near_zero_sl"

    if (risk / entry) > _channel_max_sl_pct(channel):
        return False, "sl_cap_exceeded"

    if max_sl_distance is not None and risk > max_sl_distance + (entry * 1e-8):
        return False, "sl_distance_widened"

    rr = abs(tp1 - entry) / risk if risk > 0 else 0.0
    if rr < _min_rr_for_setup(setup):
        return False, "rr_below_min"
    return True, ""


def is_sl_distance_capped(
    *,
    entry: float,
    original_stop_loss: float,
    final_stop_loss: float,
    channel: str,
    tol: float = 1e-6,
) -> bool:
    """Return True when post-cap SL equals channel cap while pre-cap exceeded it.

    `original_stop_loss` is the pre-cap/reference SL; `final_stop_loss` is the
    downstream SL to evaluate for effective cap application.
    """
    if entry <= 0 or original_stop_loss <= 0 or final_stop_loss <= 0:
        return False
    original_sl_pct = abs(entry - original_stop_loss) / entry
    final_sl_pct = abs(entry - final_stop_loss) / entry
    cap_pct = _channel_max_sl_pct(channel)
    return original_sl_pct > cap_pct and abs(final_sl_pct - cap_pct) <= tol


@dataclass
class PairQualityAssessment:
    passed: bool
    score: float
    label: str
    volume_tier: str
    spread_score: float
    volatility_score: float
    noise_score: float
    reason: str = ""


@dataclass
class SetupAssessment:
    setup_class: SetupClass
    thesis: str
    channel_compatible: bool
    regime_compatible: bool
    reason: str = ""


@dataclass
class ExecutionAssessment:
    passed: bool
    trigger_confirmed: bool
    extension_ratio: float
    anchor_price: float
    entry_zone: str
    execution_note: str
    reason: str = ""


@dataclass
class RiskAssessment:
    passed: bool
    stop_loss: float
    tp1: float
    tp2: float
    tp3: Optional[float]
    r_multiple: float
    invalidation_summary: str
    reason: str = ""


@dataclass
class ComponentScore:
    components: Dict[str, float] = field(default_factory=dict)
    total: float = 0.0
    quality_tier: QualityTier = QualityTier.C


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _last(values: Any, default: float = 0.0) -> float:
    try:
        if values is None or len(values) == 0:
            return default
        return float(values[-1])
    except (TypeError, ValueError):
        return default


def _wickiness(candles: Optional[dict], lookback: int = 12) -> float:
    if not candles:
        return 1.0
    highs = candles.get("high", [])
    lows = candles.get("low", [])
    closes = candles.get("close", [])
    if len(highs) < 2 or len(lows) < 2 or len(closes) < 2:
        return 1.0
    start = max(1, len(closes) - lookback)
    ratios = []
    for idx in range(start, len(closes)):
        high = _safe_float(highs[idx], _safe_float(closes[idx]))
        low = _safe_float(lows[idx], _safe_float(closes[idx]))
        close = _safe_float(closes[idx], 0.0)
        prev_close = _safe_float(closes[idx - 1], close)
        candle_range = max(high - low, max(abs(close), 1.0) * 0.0001)
        body = max(abs(close - prev_close), candle_range * 0.35, max(abs(close), 1.0) * 0.0001)
        wick = max(high - max(close, prev_close), 0.0) + max(min(close, prev_close) - low, 0.0)
        ratios.append(wick / body)
    if not ratios:
        return 1.0
    return round(sum(ratios) / len(ratios), 3)


def _recent_structure(candles: Optional[dict], direction: Direction, lookback: int = 12) -> float:
    if not candles:
        return 0.0
    highs = candles.get("high", [])
    lows = candles.get("low", [])
    if direction == Direction.LONG and len(lows) > 0:
        segment = lows[-lookback:]
        return float(np.min(segment))
    if direction == Direction.SHORT and len(highs) > 0:
        segment = highs[-lookback:]
        return float(np.max(segment))
    return 0.0


def classify_market_state(
    regime_result: Any,
    indicators: Dict[str, Any],
    candles: Optional[dict],
    spread_pct: float,
) -> MarketState:
    adx_val = _safe_float(indicators.get("adx_last"))
    momentum = abs(_safe_float(indicators.get("momentum_last")))
    bb_width = _safe_float(getattr(regime_result, "bb_width_pct", indicators.get("bb_width_pct")))
    atr_val = _safe_float(indicators.get("atr_last"))
    close = _last(candles.get("close", []) if candles else [], 1.0)
    atr_pct = (atr_val / close * 100.0) if close else 0.0
    wickiness = _wickiness(candles)
    regime = getattr(regime_result, "regime", MarketRegime.RANGING)
    if isinstance(regime, str):
        try:
            regime = MarketRegime(regime)
        except ValueError:
            regime = MarketRegime.RANGING

    if spread_pct >= 0.03 or wickiness >= 3.0 or atr_pct >= 4.5:
        return MarketState.VOLATILE_UNSUITABLE
    if regime == MarketRegime.VOLATILE:
        return (
            MarketState.BREAKOUT_EXPANSION
            if adx_val >= 24.0 and momentum >= 0.45 and wickiness <= 2.2
            else MarketState.VOLATILE_UNSUITABLE
        )
    if regime in (MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN):
        return MarketState.STRONG_TREND if adx_val >= 30.0 and momentum >= 0.15 else MarketState.WEAK_TREND
    if regime == MarketRegime.QUIET:
        return MarketState.CLEAN_RANGE if wickiness <= 1.5 else MarketState.DIRTY_RANGE
    if regime == MarketRegime.RANGING:
        if adx_val <= 18.0 and wickiness <= 3.1 and (bb_width == 0.0 or bb_width <= 3.2):
            return MarketState.CLEAN_RANGE
        return MarketState.DIRTY_RANGE
    if adx_val >= 24.0 and momentum >= 0.45:
        return MarketState.BREAKOUT_EXPANSION
    return MarketState.DIRTY_RANGE


def assess_pair_quality(
    volume_24h: float,
    spread_pct: float,
    indicators: Dict[str, Any],
    candles: Optional[dict],
) -> PairQualityAssessment:
    atr_val = _safe_float(indicators.get("atr_last"))
    close = _last(candles.get("close", []) if candles else [], 1.0)
    atr_pct = (atr_val / close * 100.0) if close else 0.0
    wickiness = _wickiness(candles)

    spread_score = max(0.0, min(100.0, 100.0 - (spread_pct / 0.02) * 100.0))
    volume_score = max(0.0, min(100.0, (volume_24h / 15_000_000.0) * 100.0))
    if 0.15 <= atr_pct <= 3.5:
        volatility_score = 100.0
    elif atr_pct < 0.15:
        volatility_score = max(20.0, atr_pct / 0.15 * 100.0)
    else:
        volatility_score = max(0.0, 100.0 - ((atr_pct - 3.5) / 3.0) * 100.0)
    noise_score = max(0.0, min(100.0, 100.0 - max(wickiness - 1.0, 0.0) * 35.0))
    total = round(
        spread_score * 0.3 + volume_score * 0.3 + volatility_score * 0.2 + noise_score * 0.2,
        2,
    )

    volume_tier = "ELITE" if volume_24h >= 20_000_000 else "HIGH" if volume_24h >= 10_000_000 else "NORMAL"
    label = "ELITE" if total >= 85 else "GOOD" if total >= 72 else "WEAK"
    passed = total >= 58 and spread_pct <= 0.05 and volume_24h >= 1_000_000
    reason = ""
    if not passed:
        if spread_pct > 0.05:
            reason = "spread too wide"
        elif volume_24h < 1_000_000:
            reason = "liquidity too thin"
        else:
            reason = "pair quality below threshold"

    return PairQualityAssessment(
        passed=passed,
        score=total,
        label=label,
        volume_tier=volume_tier,
        spread_score=round(spread_score, 2),
        volatility_score=round(volatility_score, 2),
        noise_score=round(noise_score, 2),
        reason=reason,
    )


# Per-channel spread limits for `assess_pair_quality_for_channel()`.
# Tighter limits for execution-sensitive scalp channels, wider for longer-hold
# strategies that can absorb higher spread costs over extended holding periods.
_SPREAD_LIMIT_BY_CHANNEL: Dict[str, float] = {
    "360_SCALP":      0.025,  # Tightest — execution-sensitive
    "360_SCALP_FVG":  0.03,
    "360_SCALP_CVD":  0.03,
    "360_SCALP_VWAP": 0.03,
}

# Minimum 24h volume (USD) for non-SCALP channels.  Scalp channels keep the
# higher $1M floor to ensure adequate liquidity for tight execution.
_MIN_VOLUME_NON_SCALP: float = 500_000.0

# Per-channel minimum composite score thresholds.
_MIN_COMPOSITE_SCORE_BY_CHANNEL: Dict[str, float] = {
    "360_SCALP":      58.0,
    "360_SCALP_FVG":  58.0,
    "360_SCALP_CVD":  58.0,
    "360_SCALP_VWAP": 58.0,
}

# Per-channel minimum 24h volume floors (USD).
_MIN_VOLUME_BY_CHANNEL: Dict[str, float] = {
    "360_SCALP":      1_000_000.0,
    "360_SCALP_FVG":  1_000_000.0,
    "360_SCALP_CVD":  1_000_000.0,
    "360_SCALP_VWAP": 1_000_000.0,
}


def assess_pair_quality_for_channel(
    volume_24h: float,
    spread_pct: float,
    indicators: Dict[str, Any],
    candles: Optional[dict],
    channel_name: str,
    current_regime: str = "RANGING",
) -> PairQualityAssessment:
    """Assess pair quality with per-channel spread and volume thresholds.

    Applies channel-specific spread limits from :data:`_SPREAD_LIMIT_BY_CHANNEL`
    instead of the global hard gate.  Non-SCALP channels also use a lower
    minimum volume floor (:data:`_MIN_VOLUME_NON_SCALP`) to avoid excluding
    valid lower-cap futures pairs.

    The composite scoring (spread/volume/volatility/noise) and pass/fail
    reason string are identical to :func:`assess_pair_quality`; only the
    final hard-gate thresholds differ.

    Parameters
    ----------
    volume_24h:
        24-hour traded volume in USD.
    spread_pct:
        Current bid-ask spread as a fraction (e.g. ``0.002`` = 0.2 %).
    indicators:
        Indicator dict for the primary timeframe (must contain ``atr_last``).
    candles:
        Candle OHLCV dict for the primary timeframe.
    channel_name:
        Name of the trading channel (e.g. ``"360_SCALP"``).

    Returns
    -------
    :class:`PairQualityAssessment`
    """
    atr_val = _safe_float(indicators.get("atr_last"))
    close = _last(candles.get("close", []) if candles else [], 1.0)
    atr_pct = (atr_val / close * 100.0) if close else 0.0
    wickiness = _wickiness(candles)

    spread_score = max(0.0, min(100.0, 100.0 - (spread_pct / 0.02) * 100.0))
    volume_score = max(0.0, min(100.0, (volume_24h / 15_000_000.0) * 100.0))
    if 0.15 <= atr_pct <= 3.5:
        volatility_score = 100.0
    elif atr_pct < 0.15:
        volatility_score = max(20.0, atr_pct / 0.15 * 100.0)
    else:
        volatility_score = max(0.0, 100.0 - ((atr_pct - 3.5) / 3.0) * 100.0)
    noise_score = max(0.0, min(100.0, 100.0 - max(wickiness - 1.0, 0.0) * 35.0))
    total = round(
        spread_score * 0.3 + volume_score * 0.3 + volatility_score * 0.2 + noise_score * 0.2,
        2,
    )

    volume_tier = "ELITE" if volume_24h >= 20_000_000 else "HIGH" if volume_24h >= 10_000_000 else "NORMAL"
    label = "ELITE" if total >= 85 else "GOOD" if total >= 72 else "WEAK"

    # Per-channel thresholds
    spread_limit = _SPREAD_LIMIT_BY_CHANNEL.get(channel_name, 0.05)
    min_composite = _MIN_COMPOSITE_SCORE_BY_CHANNEL.get(channel_name, 58.0)
    min_volume = _MIN_VOLUME_BY_CHANNEL.get(channel_name, 500_000.0)

    # Regime-aware spread relaxation: widen spread tolerance by 30% in VOLATILE regime
    effective_spread_limit = spread_limit * 1.3 if current_regime == "VOLATILE" else spread_limit

    passed = (
        total >= min_composite
        and spread_pct <= effective_spread_limit
        and volume_24h >= min_volume
    )
    reason = ""
    if not passed:
        if spread_pct > effective_spread_limit:
            reason = "spread too wide"
        elif volume_24h < min_volume:
            reason = "liquidity too thin"
        else:
            reason = "pair quality below threshold"

    return PairQualityAssessment(
        passed=passed,
        score=total,
        label=label,
        volume_tier=volume_tier,
        spread_score=round(spread_score, 2),
        volatility_score=round(volatility_score, 2),
        noise_score=round(noise_score, 2),
        reason=reason,
    )


def classify_setup(
    channel_name: str,
    signal: Any,
    indicators: Dict[str, Dict[str, Any]],
    smc_data: Dict[str, Any],
    market_state: MarketState,
) -> SetupAssessment:
    primary_tf = "5m"
    primary = indicators.get(primary_tf, indicators.get("5m", indicators.get("1m", {})))
    sweeps = smc_data.get("sweeps", [])
    mss = smc_data.get("mss")
    fvg = smc_data.get("fvg", [])
    whale = smc_data.get("whale_alert")
    delta_spike = bool(smc_data.get("volume_delta_spike"))
    momentum = _safe_float(primary.get("momentum_last"))

    # Bypass methods self-identify via signal.setup_class.  Honor that
    # classification directly so that the regime-compatibility gate uses the
    # correct SetupClass entry (e.g. VOLUME_SURGE_BREAKOUT is in
    # REGIME_SETUP_COMPATIBILITY[VOLATILE_UNSUITABLE] and must not be
    # re-classified as MOMENTUM_EXPANSION which is not).
    _SELF_CLASSIFYING = frozenset({
        "VOLUME_SURGE_BREAKOUT",
        "BREAKDOWN_SHORT",
        "OPENING_RANGE_BREAKOUT",
        "FUNDING_EXTREME_SIGNAL",
        "LIQUIDITY_SWEEP_REVERSAL",
        "QUIET_COMPRESSION_BREAK",
        # PR-ARCH-7A: preserve evaluator-assigned setup identities
        "LIQUIDATION_REVERSAL",
        "TREND_PULLBACK_EMA",
        "WHALE_MOMENTUM",
        "DIVERGENCE_CONTINUATION",
        "SR_FLIP_RETEST",
        "CONTINUATION_LIQUIDITY_SWEEP",
        "POST_DISPLACEMENT_CONTINUATION",
        # Roadmap step 7: failed auction / failed acceptance reversal
        "FAILED_AUCTION_RECLAIM",
        # PR-01: active auxiliary channel evaluator identities — these channels
        # self-classify their output; downstream must not reclassify to a generic class.
        "FVG_RETEST",
        "FVG_RETEST_HTF_CONFLUENCE",
        "RSI_MACD_DIVERGENCE",
        "SMC_ORDERBLOCK",
    })
    _sig_setup_class = getattr(signal, "setup_class", "")
    if _sig_setup_class in _SELF_CLASSIFYING:
        try:
            setup = SetupClass(_sig_setup_class)
        except ValueError:
            import logging as _logging
            _logging.warning(
                "classify_setup: unrecognised self-classifying setup_class %r "
                "— falling back to TREND_PULLBACK_CONTINUATION",
                _sig_setup_class,
            )
            setup = SetupClass.TREND_PULLBACK_CONTINUATION
    # Check for WHALE_MOMENTUM / RANGE_FADE setups (SCALP sub-paths)
    elif channel_name == "360_SCALP" and (whale or delta_spike) and abs(momentum) >= 0.3:
        setup = SetupClass.WHALE_MOMENTUM
    elif channel_name == "360_SCALP" and market_state in (MarketState.CLEAN_RANGE, MarketState.DIRTY_RANGE):
        setup = SetupClass.RANGE_FADE
    elif sweeps and signal.direction == sweeps[0].direction and (mss is not None or abs(momentum) >= 0.2):
        setup = SetupClass.LIQUIDITY_SWEEP_REVERSAL
    elif mss is not None and signal.direction == mss.direction:
        setup = SetupClass.BREAKOUT_RETEST
    elif fvg and market_state in (MarketState.STRONG_TREND, MarketState.WEAK_TREND, MarketState.BREAKOUT_EXPANSION):
        setup = SetupClass.TREND_PULLBACK_CONTINUATION
    elif market_state in (MarketState.CLEAN_RANGE, MarketState.DIRTY_RANGE):
        setup = SetupClass.RANGE_REJECTION
    elif abs(momentum) >= 0.45:
        setup = SetupClass.MOMENTUM_EXPANSION
    else:
        setup = SetupClass.TREND_PULLBACK_CONTINUATION

    channel_ok = setup in CHANNEL_SETUP_COMPATIBILITY.get(channel_name, set())
    regime_ok = setup in REGIME_SETUP_COMPATIBILITY.get(market_state, set())
    thesis = setup.value.replace("_", " ").title()
    reason = ""
    if not channel_ok:
        reason = f"{setup.value} not allowed in {channel_name}"
    elif not regime_ok:
        reason = f"{setup.value} conflicts with {market_state.value}"

    return SetupAssessment(
        setup_class=setup,
        thesis=thesis,
        channel_compatible=channel_ok,
        regime_compatible=regime_ok,
        reason=reason,
    )


def execution_quality_check(
    signal: Any,
    indicators: Dict[str, Dict[str, Any]],
    smc_data: Dict[str, Any],
    setup: SetupClass,
    market_state: MarketState,
) -> ExecutionAssessment:
    primary_tf = "5m"
    primary = indicators.get(primary_tf, indicators.get("5m", indicators.get("1m", {})))
    atr_val = max(_safe_float(primary.get("atr_last")), signal.entry * 0.01)  # 1% floor
    ema_anchor = _safe_float(primary.get("ema21_last"), signal.entry)
    bb_mid = _safe_float(primary.get("bb_mid_last"), signal.entry)
    sweep = smc_data.get("sweeps", [None])[0] if smc_data.get("sweeps") else None
    sweep_level = _safe_float(sweep.sweep_level if sweep else None, signal.entry)
    mss = smc_data.get("mss")
    anchor = ema_anchor
    trigger_confirmed = False
    note = ""

    if setup == SetupClass.RANGE_REJECTION:
        anchor = _safe_float(primary.get("bb_lower_last") if signal.direction == Direction.LONG else primary.get("bb_upper_last"), signal.entry)
        trigger_confirmed = market_state == MarketState.CLEAN_RANGE and abs(signal.entry - anchor) <= atr_val * 0.7
        note = "Fade only at range edge; avoid mid-range entries."
    elif setup == SetupClass.LIQUIDITY_SWEEP_REVERSAL:
        anchor = sweep_level or signal.entry
        trigger_confirmed = bool(smc_data.get("sweeps")) and (
            signal.entry >= anchor if signal.direction == Direction.LONG else signal.entry <= anchor
        )
        note = "Need reclaim after sweep; do not front-run the reversal."
    elif setup == SetupClass.BREAKOUT_RETEST:
        anchor = _safe_float(mss.midpoint if mss is not None else None, ema_anchor)
        trigger_confirmed = mss is not None and (
            signal.entry >= anchor if signal.direction == Direction.LONG else signal.entry <= anchor
        )
        note = "Enter on retest hold, not on the first expansion candle."
    elif setup == SetupClass.MOMENTUM_EXPANSION:
        anchor = _safe_float(primary.get("ema9_last"), ema_anchor)
        trigger_confirmed = abs(_safe_float(primary.get("momentum_last"))) >= 0.45
        note = "Momentum is valid only while flow stays one-sided; do not chase extensions."
    elif setup == SetupClass.EXHAUSTION_FADE:
        anchor = bb_mid or sweep_level or signal.entry
        trigger_confirmed = market_state == MarketState.CLEAN_RANGE and bool(smc_data.get("sweeps"))
        note = "Fade only after exhaustion is obvious and reclaim begins."
    elif setup == SetupClass.RANGE_FADE:
        anchor = _safe_float(primary.get("bb_lower_last") if signal.direction == Direction.LONG else primary.get("bb_upper_last"), signal.entry)
        trigger_confirmed = market_state in (MarketState.CLEAN_RANGE, MarketState.DIRTY_RANGE) and abs(signal.entry - anchor) <= atr_val * 0.8
        note = "Fade at band edge only; avoid mid-range entries."
    elif setup == SetupClass.WHALE_MOMENTUM:
        anchor = _safe_float(primary.get("ema9_last"), ema_anchor)
        trigger_confirmed = abs(_safe_float(primary.get("momentum_last"))) >= 0.3
        note = "Whale flow active; keep trailing stops tight and do not chase extensions."
    elif setup == SetupClass.CONTINUATION_LIQUIDITY_SWEEP:
        anchor = sweep_level or signal.entry
        trigger_confirmed = bool(smc_data.get("sweeps")) and (
            signal.entry > anchor if signal.direction == Direction.LONG else signal.entry < anchor
        )
        note = "Enter on continuation after sweep reclaim; structural invalidation is a return below swept level."
    elif setup == SetupClass.POST_DISPLACEMENT_CONTINUATION:
        # Anchor is the consolidation breakout level (consol_high for LONG,
        # consol_low for SHORT).  Stored on the signal by the evaluator to avoid
        # EMA21 anchoring which has no relationship to the PDC thesis.
        anchor = getattr(signal, "pdc_breakout_level", signal.entry)
        trigger_confirmed = (
            signal.entry > anchor if signal.direction == Direction.LONG
            else signal.entry < anchor
        )
        note = (
            "Enter on re-acceleration breakout above consolidation; "
            "structural invalidation is a return into the consolidation range."
        )
    elif setup == SetupClass.FAILED_AUCTION_RECLAIM:
        # Anchor is the reclaim level — the structural boundary that was broken
        # and then reclaimed.  Stored on the signal by the evaluator as
        # far_reclaim_level.  Trigger is confirmed when the current entry is
        # beyond that level in the reclaim direction (price is already inside
        # prior structure, not still below/above the tested level).
        anchor = getattr(signal, "far_reclaim_level", signal.entry)
        trigger_confirmed = (
            signal.entry > anchor if signal.direction == Direction.LONG
            else signal.entry < anchor
        )
        note = (
            "Enter after failed auction reclaim is confirmed; "
            "structural invalidation is a return to or below the failed-auction wick extreme."
        )
    else:
        anchor = ema_anchor
        trigger_confirmed = (
            (_safe_float(primary.get("ema9_last")) >= ema_anchor and signal.direction == Direction.LONG)
            or (_safe_float(primary.get("ema9_last")) <= ema_anchor and signal.direction == Direction.SHORT)
        )
        note = "Wait for pullback confirmation around value; avoid late continuation entries."

    extension_ratio = round(abs(signal.entry - anchor) / max(atr_val, signal.entry * 0.0005), 2)
    max_extension = {
        SetupClass.TREND_PULLBACK_CONTINUATION: 1.5,
        SetupClass.BREAKOUT_RETEST: 1.3,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL: 1.1,
        SetupClass.RANGE_REJECTION: 1.2,
        SetupClass.MOMENTUM_EXPANSION: 1.0,
        SetupClass.EXHAUSTION_FADE: 1.0,
        SetupClass.RANGE_FADE: 1.3,
        SetupClass.WHALE_MOMENTUM: 1.2,
        SetupClass.VOLUME_SURGE_BREAKOUT: 1.5,
        SetupClass.BREAKDOWN_SHORT: 1.5,
        SetupClass.CONTINUATION_LIQUIDITY_SWEEP: 1.3,
        # PDC fires on the re-acceleration breakout immediately after tight consolidation.
        # The entry should be very close to the breakout level; cap at 1.0 ATR to reject
        # stale entries taken too far into the re-acceleration move.
        SetupClass.POST_DISPLACEMENT_CONTINUATION: 1.0,
        # FAR: entry follows the reclaim of the structural level.  Allow slightly
        # more room than PDC because the reclaim move itself creates separation from
        # the anchor; cap at 1.2 ATR to reject stale entries chasing the reversal.
        SetupClass.FAILED_AUCTION_RECLAIM: 1.2,
    }.get(setup, 1.5)
    passed = trigger_confirmed and extension_ratio <= max_extension
    zone_low = min(anchor, signal.entry)
    zone_high = max(anchor, signal.entry)
    # Use dynamic decimal places based on price magnitude for micro-cap tokens
    _zone_fmt = price_decimal_fmt(max(zone_low, zone_high, 1e-12))
    entry_zone = f"{zone_low:{_zone_fmt}} – {zone_high:{_zone_fmt}}"
    reason = ""
    if not trigger_confirmed:
        reason = "entry trigger not confirmed"
    elif extension_ratio > max_extension:
        reason = f"entry overextended ({extension_ratio:.2f} ATR)"

    return ExecutionAssessment(
        passed=passed,
        trigger_confirmed=trigger_confirmed,
        extension_ratio=extension_ratio,
        anchor_price=anchor,
        entry_zone=entry_zone,
        execution_note=note,
        reason=reason,
    )


def build_risk_plan(
    signal: Any,
    indicators: Dict[str, Dict[str, Any]],
    candles: Dict[str, dict],
    smc_data: Dict[str, Any],
    setup: SetupClass,
    spread_pct: float,
    channel: Optional[str] = None,
) -> RiskAssessment:
    primary_tf = "5m"
    primary = indicators.get(primary_tf, indicators.get("5m", indicators.get("1m", {})))
    candle_bucket = candles.get(primary_tf, candles.get("5m", candles.get("1m", {})))
    atr_val = max(_safe_float(primary.get("atr_last")), signal.entry * 0.01)  # 1% of price as minimum ATR
    buffer = max(atr_val * 0.35, signal.entry * (spread_pct / 100.0) * 1.5)
    structure = _recent_structure(candle_bucket, signal.direction)

    if smc_data.get("sweeps"):
        sweep_level = _safe_float(smc_data["sweeps"][0].sweep_level)
        if signal.direction == Direction.LONG and 0 < sweep_level < signal.entry:
            structure = max(structure, sweep_level) if structure else sweep_level
        elif signal.direction == Direction.SHORT and sweep_level > signal.entry:
            structure = min(structure, sweep_level) if structure else sweep_level

    if signal.direction == Direction.LONG:
        structure = structure if 0 < structure < signal.entry else signal.entry - atr_val
        stop_loss = round(structure - buffer, 8)
    else:
        structure = structure if structure > signal.entry else signal.entry + atr_val
        stop_loss = round(structure + buffer, 8)

    # FAILED_AUCTION_RECLAIM is not a generic recent-structure stop.  Its
    # invalidation is the failed-auction wick extreme (with buffer), and the
    # reclaim level is the structural boundary that was recovered.  Re-use the
    # evaluator-computed stop when available so downstream risk handling stays
    # aligned with the path thesis rather than drifting into the generic branch.
    far_reclaim_level = _safe_float(getattr(signal, "far_reclaim_level", None), 0.0)
    if setup == SetupClass.FAILED_AUCTION_RECLAIM:
        far_structural_sl = _safe_float(getattr(signal, "stop_loss", None), 0.0)
        if signal.direction == Direction.LONG and 0 < far_structural_sl < signal.entry:
            stop_loss = round(far_structural_sl, 8)
        elif signal.direction == Direction.SHORT and far_structural_sl > signal.entry:
            stop_loss = round(far_structural_sl, 8)

        # Use the reclaim level as the named structure for FAR invalidation
        # summaries when it sits on the correct side of the entry.
        if signal.direction == Direction.LONG and 0 < far_reclaim_level < signal.entry:
            structure = far_reclaim_level
        elif signal.direction == Direction.SHORT and far_reclaim_level > signal.entry:
            structure = far_reclaim_level

    # PR-02: For structurally-protected paths (other than FAILED_AUCTION_RECLAIM
    # which is handled above), re-use the evaluator-authored stop when it is
    # directionally valid.  This preserves the method-specific structural
    # invalidation level (e.g. 0.8% below swing-high for VOLUME_SURGE_BREAKOUT,
    # beyond consolidation range for POST_DISPLACEMENT_CONTINUATION, beyond band
    # for QUIET_COMPRESSION_BREAK) rather than drifting to the generic
    # ATR/recent-structure SL which has no knowledge of the evaluator thesis.
    # Universal hard controls (max SL %, near-zero guard, directional sanity)
    # are applied below and remain intact.
    elif setup in STRUCTURAL_SLTP_PROTECTED_SETUPS:
        _eval_sl = _safe_float(getattr(signal, "stop_loss", None), 0.0)
        if signal.direction == Direction.LONG and 0 < _eval_sl < signal.entry:
            stop_loss = round(_eval_sl, 8)
        elif signal.direction == Direction.SHORT and _eval_sl > signal.entry:
            stop_loss = round(_eval_sl, 8)

    # Channel-aware hard cap on SL distance – clamp oversized stops before
    # they inflate risk and produce trades that hit SL within seconds.
    _chan = channel or getattr(signal, "channel", None) or ""
    _max_sl_pct = _MAX_SL_PCT_BY_CHANNEL.get(_chan, 5.0) / 100.0
    if signal.entry > 0:
        _sl_dist_pct = abs(signal.entry - stop_loss) / signal.entry
        if _sl_dist_pct > _max_sl_pct:
            _capped_dist = signal.entry * _max_sl_pct
            if signal.direction == Direction.LONG:
                stop_loss = round(signal.entry - _capped_dist, 8)
            else:
                stop_loss = round(signal.entry + _capped_dist, 8)
            log.warning(
                "SL capped for %s %s: %.2f%% > %.2f%% max (capped to %.8f)",
                _chan,
                signal.direction.value,
                _sl_dist_pct * 100,
                _max_sl_pct * 100,
                stop_loss,
            )

    # Near-zero SL guard — reject signals where the capped SL is so close to
    # entry that it offers no real protection.  This catches edge cases on
    # sub-penny tokens (e.g. BULLAUSDT) where ATR-based SL exceeds the channel
    # cap by a large margin and the resulting capped price rounds near zero.
    # Threshold: SL must be at least 0.05% away from entry.
    _MIN_SL_DISTANCE_PCT = 0.0005  # 0.05% of entry price
    if signal.entry > 0:
        _sl_dist_abs = abs(signal.entry - stop_loss)
        _sl_min_required = signal.entry * _MIN_SL_DISTANCE_PCT
        if _sl_dist_abs < _sl_min_required:
            log.warning(
                "SL near-zero rejection for %s %s: SL=%.8f is only %.4f%% from entry=%.8f (min=%.4f%%)",
                _chan,
                signal.direction.value,
                stop_loss,
                (_sl_dist_abs / signal.entry * 100),
                signal.entry,
                _MIN_SL_DISTANCE_PCT * 100,
            )
            return RiskAssessment(
                passed=False,
                stop_loss=stop_loss,
                tp1=signal.tp1,
                tp2=signal.tp2,
                tp3=signal.tp3,
                r_multiple=0.0,
                invalidation_summary=f"SL distance {_sl_dist_abs:.8f} below minimum {_sl_min_required:.8f} — near-zero SL rejected.",
                reason="SL distance below minimum threshold (near-zero SL rejected)",
            )

    # Directional sanity check – reject immediately if the computed SL is on
    # the wrong side of the entry price (can happen with unusual price action
    # or very thin markets where ATR/structure estimates are unreliable).
    if signal.direction == Direction.LONG and stop_loss >= signal.entry:
        return RiskAssessment(
            passed=False,
            stop_loss=stop_loss,
            tp1=signal.tp1,
            tp2=signal.tp2,
            tp3=signal.tp3,
            r_multiple=0.0,
            invalidation_summary="SL computed above entry for LONG – risk plan rejected.",
            reason="SL above entry for LONG",
        )
    if signal.direction == Direction.SHORT and stop_loss <= signal.entry:
        return RiskAssessment(
            passed=False,
            stop_loss=stop_loss,
            tp1=signal.tp1,
            tp2=signal.tp2,
            tp3=signal.tp3,
            r_multiple=0.0,
            invalidation_summary="SL computed below entry for SHORT – risk plan rejected.",
            reason="SL below entry for SHORT",
        )

    risk = abs(signal.entry - stop_loss)
    if risk <= max(signal.entry * 0.0003, buffer * 0.5):
        return RiskAssessment(
            passed=False,
            stop_loss=signal.stop_loss,
            tp1=signal.tp1,
            tp2=signal.tp2,
            tp3=signal.tp3,
            r_multiple=0.0,
            invalidation_summary="Risk distance too tight for structural invalidation.",
            reason="risk distance too tight",
        )

    bb_mid = _safe_float(primary.get("bb_mid_last"), signal.entry)
    bb_upper = _safe_float(primary.get("bb_upper_last"), signal.entry + risk)
    bb_lower = _safe_float(primary.get("bb_lower_last"), signal.entry - risk)

    _is_long = signal.direction == Direction.LONG

    # PR-02: Protected structural paths use evaluator-authored TP geometry.
    # Each target is validated (must be on the correct side of entry); only
    # valid levels are kept — invalid ones fall back to conservative risk
    # multiples so the signal is not rejected on an edge-case geometry failure.
    # The existing FAILED_AUCTION_RECLAIM branch (below) handles its own TP
    # logic and is excluded from this set.
    if setup in STRUCTURAL_SLTP_PROTECTED_SETUPS:
        _e_tp1 = _safe_float(getattr(signal, "tp1", None), 0.0)
        _e_tp2 = _safe_float(getattr(signal, "tp2", None), 0.0)
        _e_tp3_raw = getattr(signal, "tp3", None)
        _e_tp3 = _safe_float(_e_tp3_raw, 0.0) if _e_tp3_raw is not None else None
        if _is_long:
            tp1 = _e_tp1 if _e_tp1 > signal.entry else signal.entry + risk * 1.5
            tp2 = _e_tp2 if _e_tp2 > signal.entry else signal.entry + risk * 2.5
            tp3 = _e_tp3 if (_e_tp3 is not None and _e_tp3 > signal.entry) else signal.entry + risk * 4.0
        else:
            tp1 = _e_tp1 if (0 < _e_tp1 < signal.entry) else signal.entry - risk * 1.5
            tp2 = _e_tp2 if (0 < _e_tp2 < signal.entry) else signal.entry - risk * 2.5
            tp3 = _e_tp3 if (_e_tp3 is not None and 0 < _e_tp3 < signal.entry) else signal.entry - risk * 4.0
        log.debug(
            "PR-02 structural TP preserved for %s %s: tp1=%.6f tp2=%.6f tp3=%s",
            getattr(signal, "symbol", "?"),
            setup.value,
            tp1,
            tp2,
            f"{tp3:.6f}" if tp3 is not None else "None",
        )
    elif setup == SetupClass.RANGE_REJECTION:
        # Tight Bollinger-band-anchored exits — exits at mid and upper/lower band.
        if _is_long:
            tp1 = max(signal.entry + risk * 0.9, bb_mid)
            tp2 = max(tp1 + risk * 0.4, bb_upper)
        else:
            tp1 = min(signal.entry - risk * 0.9, bb_mid)
            tp2 = min(tp1 - risk * 0.4, bb_lower)
        tp3 = None
    elif setup == SetupClass.FUNDING_EXTREME_SIGNAL:
        # Mean-reversion / snap-back: take profit quickly before the reversal fades.
        # Tighter TP ratios reflect a short-lived, aggressive counter-trend move.
        # LIQUIDATION_REVERSAL is handled above by STRUCTURAL_SLTP_PROTECTED_SETUPS
        # using evaluator-authored Fibonacci retrace TPs (B13 compliance).
        tp1 = signal.entry + risk * 1.0 if _is_long else signal.entry - risk * 1.0
        tp2 = signal.entry + risk * 1.8 if _is_long else signal.entry - risk * 1.8
        tp3 = signal.entry + risk * 2.5 if _is_long else signal.entry - risk * 2.5
    elif setup in (SetupClass.LIQUIDITY_SWEEP_REVERSAL, SetupClass.EXHAUSTION_FADE):
        # Sweep + structural reversal: moderate 1.2/2.1/3.0 R cadence.
        tp1 = signal.entry + risk * 1.2 if _is_long else signal.entry - risk * 1.2
        tp2 = signal.entry + risk * 2.1 if _is_long else signal.entry - risk * 2.1
        tp3 = signal.entry + risk * 3.0 if _is_long else signal.entry - risk * 3.0
    elif setup == SetupClass.RANGE_FADE:
        # Conservative fade at range extremes: quick first partial, short
        # extension.  Mirrors RANGE_REJECTION philosophy but on rate-of-change.
        tp1 = signal.entry + risk * 0.9 if _is_long else signal.entry - risk * 0.9
        tp2 = signal.entry + risk * 1.5 if _is_long else signal.entry - risk * 1.5
        tp3 = signal.entry + risk * 2.2 if _is_long else signal.entry - risk * 2.2
    elif setup == SetupClass.TREND_PULLBACK_CONTINUATION:
        # Clean trend pullback: ride the trend with moderate extension targets.
        tp1 = signal.entry + risk * 1.4 if _is_long else signal.entry - risk * 1.4
        tp2 = signal.entry + risk * 2.4 if _is_long else signal.entry - risk * 2.4
        tp3 = signal.entry + risk * 3.5 if _is_long else signal.entry - risk * 3.5
    elif setup == SetupClass.DIVERGENCE_CONTINUATION:
        # RSI/MACD divergence continuation swing: divergence resolves into
        # an extended swing — targets run past normal ATR cadence.
        tp1 = signal.entry + risk * 1.3 if _is_long else signal.entry - risk * 1.3
        tp2 = signal.entry + risk * 2.5 if _is_long else signal.entry - risk * 2.5
        tp3 = signal.entry + risk * 3.8 if _is_long else signal.entry - risk * 3.8
    elif setup in (
        SetupClass.BREAKOUT_RETEST,
        SetupClass.OPENING_RANGE_BREAKOUT,
    ):
        # Non-protected measured-move breakout families: breakout should travel a
        # full measured move — allow larger extensions than continuation plays.
        tp1 = signal.entry + risk * 1.5 if _is_long else signal.entry - risk * 1.5
        tp2 = signal.entry + risk * 2.8 if _is_long else signal.entry - risk * 2.8
        tp3 = signal.entry + risk * 4.0 if _is_long else signal.entry - risk * 4.0
    elif setup == SetupClass.WHALE_MOMENTUM:
        # Large-block momentum: institutional order drives price impulsively;
        # allow aggressive extension targets to ride the move.
        tp1 = signal.entry + risk * 1.5 if _is_long else signal.entry - risk * 1.5
        tp2 = signal.entry + risk * 2.5 if _is_long else signal.entry - risk * 2.5
        tp3 = signal.entry + risk * 3.8 if _is_long else signal.entry - risk * 3.8
    elif setup == SetupClass.MOMENTUM_EXPANSION:
        # Broad momentum expansion: strong directional move confirmed by ATR.
        tp1 = signal.entry + risk * 1.4 if _is_long else signal.entry - risk * 1.4
        tp2 = signal.entry + risk * 2.2 if _is_long else signal.entry - risk * 2.2
        tp3 = signal.entry + risk * 3.2 if _is_long else signal.entry - risk * 3.2
    elif setup == SetupClass.FAILED_AUCTION_RECLAIM:
        # PR-02: Prefer evaluator-authored TP geometry (measured-move from tail)
        # when the values are directionally valid.  The evaluator computes TPs
        # from `tail` = distance the auction probed beyond the reference level,
        # which is the most precise structural anchor for this path.  Only fall
        # back to the reclaim-span measured-move formula when evaluator TPs are
        # absent or invalid.
        _far_e_tp1 = _safe_float(getattr(signal, "tp1", None), 0.0)
        _far_e_tp2 = _safe_float(getattr(signal, "tp2", None), 0.0)
        _far_e_tp3_raw = getattr(signal, "tp3", None)
        _far_e_tp3 = _safe_float(_far_e_tp3_raw, 0.0) if _far_e_tp3_raw is not None else None
        _far_tp1_valid = _far_e_tp1 > signal.entry if _is_long else (0 < _far_e_tp1 < signal.entry)
        _far_tp2_valid = _far_e_tp2 > signal.entry if _is_long else (0 < _far_e_tp2 < signal.entry)
        _far_tp3_valid = (
            (_far_e_tp3 is not None and _far_e_tp3 > signal.entry)
            if _is_long
            else (_far_e_tp3 is not None and 0 < _far_e_tp3 < signal.entry)
        )
        if _far_tp1_valid and _far_tp2_valid:
            # Evaluator-authored structural TPs are valid — preserve them.
            tp1 = _far_e_tp1
            tp2 = _far_e_tp2
            tp3 = _far_e_tp3 if _far_tp3_valid else (
                signal.entry + risk * 3.0 if _is_long else signal.entry - risk * 3.0
            )
            log.debug(
                "PR-02 FAR structural TP preserved for %s: tp1=%.6f tp2=%.6f",
                getattr(signal, "symbol", "?"),
                tp1,
                tp2,
            )
        else:
            # Evaluator TPs missing or invalid — recompute from reclaim-span geometry.
            # Failed-auction reclaim: price rejected acceptance beyond a structural
            # level, reclaimed back through that level, and should now travel away
            # from the reclaim in a measured-move style continuation.
            reclaim_to_invalidation_span = abs(structure - stop_loss)
            reclaim_clearance = abs(signal.entry - structure)
            measured_move = (
                reclaim_to_invalidation_span + reclaim_clearance
                if reclaim_to_invalidation_span > 0
                else risk
            )
            tp1 = signal.entry + measured_move * 1.2 if _is_long else signal.entry - measured_move * 1.2
            tp2 = signal.entry + measured_move * 1.9 if _is_long else signal.entry - measured_move * 1.9
            tp3 = signal.entry + measured_move * 3.0 if _is_long else signal.entry - measured_move * 3.0
    else:
        # Fallback for remaining families (MULTI_STRATEGY_CONFLUENCE,
        # BREAKDOWN_SHORT, and any future setups not yet classified).
        tp1 = signal.entry + risk * 1.3 if _is_long else signal.entry - risk * 1.3
        tp2 = signal.entry + risk * 2.3 if _is_long else signal.entry - risk * 2.3
        tp3 = signal.entry + risk * 3.4 if _is_long else signal.entry - risk * 3.4

    r_multiple = round(abs(tp1 - signal.entry) / risk, 2) if risk else 0.0
    # Family-aware minimum R:R threshold — quick-exit families accept a lower
    # first target because the trade thesis resolves faster.
    if setup in (SetupClass.RANGE_REJECTION, SetupClass.RANGE_FADE):
        min_rr = _MIN_RR_RANGE
    elif setup in (SetupClass.LIQUIDATION_REVERSAL, SetupClass.FUNDING_EXTREME_SIGNAL):
        min_rr = _MIN_RR_MEAN_REVERSION
    elif setup in (SetupClass.SR_FLIP_RETEST, SetupClass.FAILED_AUCTION_RECLAIM):
        min_rr = _MIN_RR_STRUCTURED
    else:
        min_rr = _MIN_RR_DEFAULT
    passed = r_multiple >= min_rr
    reason = "" if passed else f"rr {r_multiple:.2f} below {min_rr:.2f}"
    # Sanity check: reject if SL or any TP is negative, or SL distance > 5% of entry
    sl_pct = risk / signal.entry if signal.entry > 0 else 0.0
    if stop_loss <= 0 or tp1 <= 0 or tp2 <= 0 or (tp3 is not None and tp3 <= 0):
        passed = False
        reason = "SL or TP computed as non-positive (micro-cap price precision issue)"
    elif sl_pct > 0.05:
        passed = False
        reason = f"SL distance {sl_pct:.1%} exceeds 5% of entry (risk plan rejected)"
    # Dynamic decimal places for invalidation message (micro-cap tokens)
    _struct_fmt = price_decimal_fmt(structure)
    invalidation = f"{'Below' if signal.direction == Direction.LONG else 'Above'} {structure:{_struct_fmt}} structure + volatility buffer"
    if setup == SetupClass.FAILED_AUCTION_RECLAIM:
        # Use a tiny positive floor so price_decimal_fmt() never receives zero
        # (which would otherwise choose an unusably coarse precision bucket).
        min_fmt_price = 1e-12
        _sl_fmt = price_decimal_fmt(max(abs(stop_loss), min_fmt_price))
        if far_reclaim_level > 0:
            invalidation = (
                f"{'Back below' if signal.direction == Direction.LONG else 'Back above'} "
                f"reclaimed level {structure:{_struct_fmt}} and through failed-auction "
                f"wick/buffer {stop_loss:{_sl_fmt}}"
            )
        else:
            invalidation = (
                f"{'Below' if signal.direction == Direction.LONG else 'Above'} "
                f"failed-auction wick/buffer {stop_loss:{_sl_fmt}} after reclaim failure"
            )

    return RiskAssessment(
        passed=passed,
        stop_loss=stop_loss,
        tp1=round(tp1, 8),
        tp2=round(tp2, 8),
        tp3=round(tp3, 8) if tp3 is not None else None,
        r_multiple=r_multiple,
        invalidation_summary=invalidation,
        reason=reason,
    )


def score_signal_components(
    *,
    pair_quality: PairQualityAssessment,
    setup: SetupAssessment,
    execution: ExecutionAssessment,
    risk: RiskAssessment,
    legacy_confidence: float,
    cross_verified: Optional[bool],
) -> ComponentScore:
    market_score = round(pair_quality.score * 0.25, 2)
    setup_score = 11.0
    if setup.setup_class in (
        SetupClass.TREND_PULLBACK_CONTINUATION,
        SetupClass.BREAKOUT_RETEST,
        SetupClass.LIQUIDITY_SWEEP_REVERSAL,
    ):
        setup_score += 6.0
    if setup.channel_compatible:
        setup_score += 4.0
    if setup.regime_compatible:
        setup_score += 4.0

    execution_score = round(
        8.0
        + (6.0 if execution.trigger_confirmed else 0.0)
        + max(0.0, 6.0 - max(execution.extension_ratio - 0.4, 0.0) * 4.0),
        2,
    )
    risk_score = round(8.0 + min(risk.r_multiple, 2.5) * 4.8, 2)
    context_score = round(min(max(legacy_confidence, 0.0), 100.0) * 0.1, 2)
    if cross_verified is True:
        context_score = min(10.0, context_score + 1.0)
    elif cross_verified is False:
        context_score = max(0.0, context_score - 2.0)

    components = {
        "market": round(min(market_score, 25.0), 2),
        "setup": round(min(setup_score, 25.0), 2),
        "execution": round(min(execution_score, 20.0), 2),
        "risk": round(min(risk_score, 20.0), 2),
        "context": round(min(context_score, 10.0), 2),
    }
    total = round(sum(components.values()), 2)
    tier = QualityTier.C
    if total >= 90.0:
        tier = QualityTier.A_PLUS
    elif total >= 82.0:
        tier = QualityTier.A
    elif total >= 74.0:
        tier = QualityTier.B
    return ComponentScore(components=components, total=total, quality_tier=tier)


# ---------------------------------------------------------------------------
# PR_09 — Composite Signal Scoring Engine
# ---------------------------------------------------------------------------


@dataclass
class ScoringInput:
    """All data needed to score a signal."""
    # SMC
    sweeps: Optional[List] = None            # List of LiquiditySweep objects
    mss: Optional[Any] = None               # MSSSignal or None
    fvg_zones: Optional[List] = None        # List of FVGZone objects
    # Regime
    regime: str = ""
    setup_class: str = ""
    atr_percentile: float = 50.0
    # Volume
    volume_last_usd: float = 0.0            # Last candle USD volume
    volume_avg_usd: float = 0.0             # 20-period average USD volume
    # Indicators
    macd_histogram_last: Optional[float] = None
    macd_histogram_prev: Optional[float] = None
    rsi_last: Optional[float] = None
    ema_fast: Optional[float] = None
    ema_slow: Optional[float] = None
    adx_last: Optional[float] = None
    direction: str = "LONG"
    # Pattern + MTF
    chart_patterns: Optional[List] = None   # List of PatternResult objects
    mtf_score: float = 0.0                  # 0.0–1.0 from MTF gate
    # Order-flow (used for family-aware thesis scoring)
    cvd_divergence: Optional[str] = None    # "BULLISH", "BEARISH", or None
    cvd_divergence_strength: float = 0.0    # 0.0–1.0 normalised divergence magnitude
    oi_trend: str = "NEUTRAL"               # "RISING", "FALLING", or "NEUTRAL"
    liq_vol_usd: float = 0.0               # Recent USD liquidation volume
    funding_rate: Optional[float] = None    # Latest funding rate (decimal)


class SignalScoringEngine:
    """Scores a candidate signal across six dimensions plus a family thesis layer.

    Produces a deterministic, auditable 0–100 score composed of:
    - SMC confluence (max 25 pts)
    - Regime alignment (max 20 pts)
    - Volume confirmation (max 15 pts)
    - Indicator confluence (max 20 pts)
    - Candlestick patterns (max 10 pts)
    - MTF confirmation (max 10 pts)
    - Family thesis adjustment (variable; see _apply_family_thesis_adjustment)

    The first six dimensions form the shared base model.  The family thesis
    layer adds a family-aware modifier for setups whose primary signal thesis
    is not well captured by the globally uniform base dimensions.
    """

    # Setup classes that strongly align with each regime
    _REGIME_SETUP_AFFINITY: Dict[str, List[str]] = {
        "TRENDING_UP": ["LIQUIDITY_SWEEP_REVERSAL", "BREAKOUT_INITIAL", "BREAKOUT_RETEST",
                        "THREE_WHITE_SOLDIERS", "WHALE_MOMENTUM", "VOLUME_SURGE_BREAKOUT",
                        "CONTINUATION_LIQUIDITY_SWEEP"],
        "TRENDING_DOWN": ["LIQUIDITY_SWEEP_REVERSAL", "BREAKOUT_INITIAL", "BREAKOUT_RETEST",
                          "THREE_BLACK_CROWS", "WHALE_MOMENTUM", "BREAKDOWN_SHORT",
                          "CONTINUATION_LIQUIDITY_SWEEP"],
        "RANGING": ["RANGE_FADE", "SWING_STANDARD"],
        "QUIET": ["RANGE_FADE"],
        "VOLATILE": ["WHALE_MOMENTUM", "LIQUIDITY_SWEEP_REVERSAL",
                     "VOLUME_SURGE_BREAKOUT", "BREAKDOWN_SHORT"],
    }

    # ── Family classification sets ─────────────────────────────────────────
    # Reversal / liquidation / funding-extreme: primary thesis is an
    # order-flow event (OI squeeze, mass liquidations, contrarian funding,
    # CVD reversal).  EMA is typically counter-trend at entry.
    _FAMILY_REVERSAL_LIQUIDATION: frozenset = frozenset({
        "LIQUIDATION_REVERSAL",
        "LIQUIDITY_SWEEP_REVERSAL",
        "FUNDING_EXTREME_SIGNAL",
        "EXHAUSTION_FADE",
    })

    # Order-flow / divergence: thesis is CVD or OI divergence confirming
    # a directional move before price follows.  WHALE_MOMENTUM is intentionally
    # excluded: its primary thesis (large-participant impulse) differs from
    # divergence confirmation and its OI behaviour is not universally "FALLING"
    # — falling OI is not an obviously positive signal for a momentum burst.
    # WHALE_MOMENTUM stays on shared base scoring until code-level evidence
    # supports a justified standalone family treatment.
    _FAMILY_ORDER_FLOW_DIVERGENCE: frozenset = frozenset({
        "DIVERGENCE_CONTINUATION",
    })

    # Sweep-confirmed continuation: primary thesis is a trending move where a
    # local pullback sweeps short-term liquidity (stop hunt) and price then
    # re-accelerates in the trend direction.  CVD aligning with the trend
    # direction and rising OI both confirm the continuation thesis.
    _FAMILY_SWEEP_CONTINUATION: frozenset = frozenset({
        "CONTINUATION_LIQUIDITY_SWEEP",
    })

    # Trend / continuation, breakout / measured-move, quiet-specialist, and
    # WHALE_MOMENTUM are well-served by the shared base scoring; no thesis
    # adjustment is applied to them.

    # Liquidation cap used for scaling liq-volume bonus (in USD)
    _LIQ_VOL_THESIS_CAP_USD: float = 5_000_000.0

    def score(self, inp: ScoringInput) -> Dict[str, float]:
        """Return a dict with per-dimension scores and a 'total' key.

        All scores are in [0, max_for_dimension].  The 'thesis_adj' key
        carries the family-aware thesis adjustment (may be negative, zero,
        or positive).  'total' is capped at 100.
        """
        smc = self._score_smc(inp)
        regime = self._score_regime(inp)
        volume = self._score_volume(inp)
        indicators = self._score_indicators(inp)
        patterns = self._score_patterns(inp)
        mtf = self._score_mtf(inp)
        thesis_adj = self._apply_family_thesis_adjustment(inp)
        total = smc + regime + volume + indicators + patterns + mtf + thesis_adj
        return {
            "smc": round(smc, 2),
            "regime": round(regime, 2),
            "volume": round(volume, 2),
            "indicators": round(indicators, 2),
            "patterns": round(patterns, 2),
            "mtf": round(mtf, 2),
            "thesis_adj": round(thesis_adj, 2),
            "total": round(min(100.0, total), 2),
        }

    # ------------------------------------------------------------------
    def _score_smc(self, inp: ScoringInput) -> float:
        """SMC confluence score, max 25 pts."""
        score = 0.0
        sweeps = inp.sweeps or []
        if sweeps:
            score += 10.0   # Base for any sweep
            # Quality bonus: if sweep is recent (index >= -3, i.e. within the last 3 candles) add 5 pts
            if sweeps[0].index >= -3:
                score += 5.0
        if inp.mss is not None:
            score += 8.0    # MSS confirmation adds weight
        fvg = inp.fvg_zones or []
        if fvg:
            score += 2.0    # FVG presence (minor confluence)
        return min(25.0, score)

    # ------------------------------------------------------------------
    def _score_regime(self, inp: ScoringInput) -> float:
        """Regime alignment score, max 20 pts."""
        if not inp.regime:
            return 10.0   # Neutral when no regime data
        affinity = self._REGIME_SETUP_AFFINITY.get(inp.regime.upper(), [])
        if inp.setup_class in affinity:
            base = 18.0   # Strong alignment
        elif affinity:
            base = 8.0    # Regime known but setup not optimal
        else:
            base = 10.0   # Unknown regime
        # Bonus for high ATR percentile in VOLATILE regime (energy behind the move)
        if inp.regime.upper() == "VOLATILE" and inp.atr_percentile >= 75:
            base = min(20.0, base + 2.0)
        return min(20.0, base)

    # ------------------------------------------------------------------
    def _score_volume(self, inp: ScoringInput) -> float:
        """Volume confirmation score, max 15 pts."""
        if inp.volume_avg_usd <= 0 or inp.volume_last_usd <= 0:
            return 7.5    # Neutral
        ratio = inp.volume_last_usd / inp.volume_avg_usd
        if ratio >= 3.0:
            return 15.0
        if ratio >= 2.0:
            return 12.0
        if ratio >= 1.5:
            return 9.0
        if ratio >= 1.0:
            return 6.0
        return 3.0   # Below-average volume

    # ------------------------------------------------------------------
    def _score_indicators(self, inp: ScoringInput) -> float:
        """Indicator confluence score, max 20 pts."""
        score = 0.0

        # MACD (max 7 pts)
        if inp.macd_histogram_last is not None and inp.macd_histogram_prev is not None:
            rising = inp.macd_histogram_last > inp.macd_histogram_prev
            positive = inp.macd_histogram_last > 0
            if inp.direction == "LONG":
                if rising and positive:
                    score += 7.0
                elif rising or positive:
                    score += 4.0
            else:
                falling = not rising
                negative = inp.macd_histogram_last < 0
                if falling and negative:
                    score += 7.0
                elif falling or negative:
                    score += 4.0

        # RSI (max 7 pts)
        if inp.rsi_last is not None:
            if inp.direction == "LONG":
                if inp.rsi_last <= 45:
                    score += 7.0    # Oversold or neutral — good for LONG
                elif inp.rsi_last <= 60:
                    score += 4.0
                else:
                    score += 1.0    # Overbought — risky
            else:
                if inp.rsi_last >= 55:
                    score += 7.0
                elif inp.rsi_last >= 40:
                    score += 4.0
                else:
                    score += 1.0

        # EMA alignment (max 6 pts)
        if inp.ema_fast is not None and inp.ema_slow is not None:
            aligned = (inp.ema_fast > inp.ema_slow if inp.direction == "LONG"
                       else inp.ema_fast < inp.ema_slow)
            score += 6.0 if aligned else 1.0

        return min(20.0, score)

    # ------------------------------------------------------------------
    def _score_patterns(self, inp: ScoringInput) -> float:
        """Candlestick pattern score, max 10 pts."""
        patterns = inp.chart_patterns or []
        if not patterns:
            return 5.0   # Neutral (no patterns detected either way)
        aligned = [p for p in patterns
                   if getattr(p, "direction", "") == inp.direction or
                      getattr(p, "direction", "") == "NEUTRAL"]
        bonus = sum(getattr(p, "confidence_bonus", 0.0) for p in aligned)
        return max(0.0, min(10.0, 5.0 + bonus * 0.5))

    # ------------------------------------------------------------------
    def _score_mtf(self, inp: ScoringInput) -> float:
        """MTF confirmation score, max 10 pts."""
        return round(inp.mtf_score * 10.0, 2)

    # ------------------------------------------------------------------
    def _apply_family_thesis_adjustment(self, inp: ScoringInput) -> float:
        """Return a family-specific thesis adjustment to add to the base total.

        The six shared dimensions score every setup uniformly.  This method
        adds a small family-aware modifier for setup families whose primary
        signal thesis is not adequately captured by the global dimensions:

        **Reversal / Liquidation / Funding-Extreme family**
        (LIQUIDATION_REVERSAL, LIQUIDITY_SWEEP_REVERSAL, FUNDING_EXTREME_SIGNAL,
        EXHAUSTION_FADE):
        - EMA counter-trend correction: reversal entries naturally have EMA
          misaligned (price hasn't crossed yet), so the uniform 1/6-pt EMA
          score creates a structural deficit.  When EMA is counter-trend for
          a reversal setup, +3 pts are added to partially neutralise this bias.
        - Order-flow thesis bonus (max +5 pts): falling OI + liquidation
          volume, CVD divergence aligned with direction, and contrarian
          funding rate are the primary thesis signals for this family.

        **Order-Flow / Divergence family** (DIVERGENCE_CONTINUATION):
        - CVD/OI divergence bonus (max +6 pts): confirmed divergence in the
          trade direction earns a positive thesis bonus; contra divergence
          applies a small penalty.
        - Divergence magnitude bonus (max +2 pts on top, total cap +8): when
          the evaluator confirms divergence and propagates its strength
          (cvd_divergence_strength > 0), a magnitude-weighted bonus rewards
          stronger absorption evidence.  This makes the score faithful to the
          evaluator's actual detected evidence rather than a binary check.

        **Sweep-Continuation family** (CONTINUATION_LIQUIDITY_SWEEP):
        - CVD trend-alignment bonus (+2 pts): CVD aligned with the trend
          direction confirms the continuation; not contra divergence like
          reversal setups.
        - OI rising bonus (+2 pts): rising OI during a sweep-driven pullback
          signals accumulation, confirming the continuation thesis.
        - Total: up to +4 pts, uncapped at zero (contra signals not penalised
          because the sweep itself carries the structural thesis).

        **All other families** (trend/continuation, breakout/measured-move,
        quiet-specialist, WHALE_MOMENTUM): 0 adjustment — the shared base
        scoring is appropriate for these paths.

        Returns
        -------
        float
            Adjustment in roughly [-2, +8].  Added to base total before the
            100-pt cap is applied in score().
        """
        setup = inp.setup_class

        if setup in self._FAMILY_REVERSAL_LIQUIDATION:
            adj = 0.0

            # EMA counter-trend correction: add +3 when EMA is naturally
            # misaligned for a reversal entry (does not double-count when
            # EMA happens to be aligned for the reversal direction).
            if inp.ema_fast is not None and inp.ema_slow is not None:
                ema_counter_trend = (
                    (inp.direction == "LONG" and inp.ema_fast < inp.ema_slow) or
                    (inp.direction == "SHORT" and inp.ema_fast > inp.ema_slow)
                )
                if ema_counter_trend:
                    adj += 3.0

            # Order-flow thesis bonus (max +5 pts combined)
            of_bonus = 0.0
            if inp.oi_trend == "FALLING":
                of_bonus += 2.0
                if inp.liq_vol_usd > 0:
                    liq_bonus = min(inp.liq_vol_usd / self._LIQ_VOL_THESIS_CAP_USD, 1.0) * 1.5
                    of_bonus += liq_bonus
            if inp.cvd_divergence is not None:
                cvd_aligned = (
                    (inp.direction == "LONG" and inp.cvd_divergence == "BULLISH") or
                    (inp.direction == "SHORT" and inp.cvd_divergence == "BEARISH")
                )
                # Reversal setups have an independent order-flow thesis (OI, liq,
                # funding); CVD is supplementary.  Penalty for contra CVD is
                # intentionally smaller (-1) than in the order-flow family (-2)
                # where CVD is the primary thesis signal.
                of_bonus += 2.0 if cvd_aligned else -1.0
            if inp.funding_rate is not None and abs(inp.funding_rate) >= 0.01:
                # Contrarian extreme funding confirms reversal thesis
                contrarian = (
                    (inp.direction == "LONG" and inp.funding_rate < -0.01) or
                    (inp.direction == "SHORT" and inp.funding_rate > 0.01)
                )
                if contrarian:
                    of_bonus += 1.5
            adj += max(0.0, min(5.0, of_bonus))
            return min(8.0, adj)

        if setup in self._FAMILY_ORDER_FLOW_DIVERGENCE:
            # CVD/OI divergence thesis bonus.
            # When cvd_divergence is confirmed (evaluator propagates its local
            # detection into smc_data["cvd_divergence"]), the aligned bonus is
            # +4 pts.  A magnitude bonus of up to +2 pts further rewards strong
            # absorption evidence (cvd_divergence_strength, normalised 0–1).
            # Combined cap is +8 pts when divergence is strong and OI is falling.
            of_bonus = 0.0
            if inp.cvd_divergence is not None:
                cvd_aligned = (
                    (inp.direction == "LONG" and inp.cvd_divergence == "BULLISH") or
                    (inp.direction == "SHORT" and inp.cvd_divergence == "BEARISH")
                )
                if cvd_aligned:
                    of_bonus += 4.0
                    # Magnitude bonus: stronger absorption = higher conviction.
                    of_bonus += min(2.0, inp.cvd_divergence_strength * 2.0)
                else:
                    of_bonus += -2.0
            if inp.oi_trend == "FALLING":
                of_bonus += 2.0
            return max(-2.0, min(8.0, of_bonus))

        if setup in self._FAMILY_SWEEP_CONTINUATION:
            # Continuation thesis: CVD aligned with trend + rising OI signal
            # accumulation during the sweep pullback (max +4 pts, floor 0).
            cont_bonus = 0.0
            if inp.cvd_divergence is not None:
                cvd_aligned = (
                    (inp.direction == "LONG" and inp.cvd_divergence == "BULLISH") or
                    (inp.direction == "SHORT" and inp.cvd_divergence == "BEARISH")
                )
                if cvd_aligned:
                    cont_bonus += 2.0
            if inp.oi_trend == "RISING":
                # Rising OI with directional momentum confirms trend accumulation
                cont_bonus += 2.0
            return min(4.0, cont_bonus)

        # Trend / continuation, breakout / measured-move, quiet-specialist:
        # shared base scoring is appropriate; no family thesis adjustment.
        return 0.0
