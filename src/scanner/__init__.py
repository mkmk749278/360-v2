"""Scanner – periodic evaluation of all pairs across channel strategies.

Extracted from :class:`src.main.CryptoSignalEngine` for modularity.
Supports signal cooldown de-duplication, market-regime-aware gating,
and optional circuit-breaker integration.
"""

from __future__ import annotations

import asyncio
import dataclasses as _dc
import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

import uuid

from config import (
    CHANNEL_ENABLE_DEFAULTS,
    CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS,
    CHANNEL_RADAR_ROLE_DEFAULTS,
    CHANNEL_ROLLOUT_STATE_DEFAULTS,
    CHANNEL_ROLLOUT_STATES_ALLOWED,
    CHANNEL_VOLATILE_FAMILY_GOVERNED,
    CHANNEL_SCALP_CVD_ENABLED,
    CHANNEL_SCALP_DIVERGENCE_ENABLED,
    CHANNEL_SCALP_ENABLED,
    CHANNEL_SCALP_FVG_ENABLED,
    CHANNEL_SCALP_ICHIMOKU_ENABLED,
    CHANNEL_SCALP_ORDERBLOCK_ENABLED,
    CHANNEL_SCALP_SUPERTREND_ENABLED,
    CHANNEL_SCALP_VWAP_ENABLED,
    FUNDING_RATE_BOOST,
    FUNDING_RATE_BOOST_THRESHOLD,
    FUNDING_RATE_PENALTY,
    FUNDING_RATE_PENALTY_THRESHOLD,
    GLOBAL_SYMBOL_COOLDOWN_SECONDS,
    MAX_CORRELATED_SCALP_SIGNALS,
    MTF_HARD_BLOCK,
    MTF_MIN_SCORE_TRENDING_SHORT,
    QUIET_SCALP_MIN_CONFIDENCE,
    RADAR_ALERT_MIN_CONFIDENCE,
    REGIME_MIN_VOLUME_USD,
    SCAN_MIN_VOLUME_USD,
    SCAN_SYMBOL_BLACKLIST,
    SEED_TIMEFRAMES,
    SIGNAL_SCAN_COOLDOWN_SECONDS,
    SIGNAL_VALID_FOR_MINUTES,
    SMC_HARD_GATE_MIN,
    SMC_SCALP_LOOKBACK,
    SMC_SCALP_TOLERANCE_PCT,
    SMC_SCORE_MIN_TRENDING_SHORT,
    SURGE_PROMOTION_MAX_PAIRS,
    SURGE_PROMOTION_VOLUME_MULTIPLIER,
    TIER2_SCAN_EVERY_N_CYCLES,
    TIER3_SCAN_EVERY_N_CYCLES,
    TIER3_SCAN_INTERVAL_MINUTES,
    TOP50_FUTURES_COUNT,
    TOP50_FUTURES_ONLY,
    TREND_HARD_GATE_MIN,
    WS_DEGRADED_CYCLES_ALERT,
    WS_DEGRADED_MAX_CYCLES,
    WS_DEGRADED_MAX_PAIRS,
    WS_PARTIAL_HEALTH_THRESHOLD,
)
from src.binance import BinanceClient
from src.channels.base import Signal as _Signal
from src.smc import Direction
from src.rate_limiter import rate_limiter, futures_rate_limiter
from src.confidence import (
    ConfidenceInput,
    compute_confidence,
    score_data_sufficiency,
    score_liquidity,
    score_multi_exchange,
    score_order_flow,
    score_smc,
    score_spread,
    score_trend,
)
from src.indicators import adx, atr, bollinger_bands, ema, macd, momentum, rsi  # noqa: F401
from src.scanner.data_fetcher import DataFetcher
from src.scanner.indicator_compute import compute_indicators_for_candle_dict
from src.onchain import score_onchain
from src.regime import MarketRegime
from src.signal_quality import (
    ExecutionAssessment,
    MarketState,
    PairQualityAssessment,
    RiskAssessment,
    SetupAssessment,
    SignalScoringEngine,
    ScoringInput,
    assess_pair_quality,
    assess_pair_quality_for_channel,
    build_risk_plan,
    classify_market_state,
    classify_setup,
    execution_quality_check,
    is_sl_distance_capped,
    score_signal_components,
    validate_geometry_against_policy,
)
from src.cluster_suppression import ClusterSuppressor
from src.confidence_decay import apply_confidence_decay
from src.cross_asset import AssetState, check_cross_asset_gate
from src.feedback_loop import FeedbackLoop
from src.kill_zone import check_kill_zone_gate
from src.mtf import check_mtf_gate, compute_mtf_confluence, _TF_WEIGHTS as _MTF_TF_WEIGHTS
from src.oi_filter import analyse_oi, check_oi_gate
from src.pair_manager import PairTier, classify_pair_tier
from src.confluence_detector import ConfluenceDetector
from src.spoof_detect import check_spoof_gate
from src.tier_manager import TierManager
from src.utils import get_logger, price_decimal_fmt, utcnow
from src.volume_divergence import check_volume_divergence_gate
from src.vwap import check_vwap_extension, compute_vwap
from src.ai_engine import get_ai_insight
from src.chart_patterns import detect_patterns, pattern_confidence_bonus, detect_all_patterns
from src.stat_filter import StatisticalFilter
from src.pair_analyzer import compute_pair_signal_quality
from src.suppression_telemetry import (
    SuppressionTracker,
    SuppressionEvent,
    REASON_QUIET_REGIME,
    REASON_SPREAD_GATE,
    REASON_VOLUME_GATE,
    REASON_OI_INVALIDATION,
    REASON_CLUSTER,
    REASON_STAT_FILTER,
    REASON_LIFESPAN,
    REASON_CONFIDENCE,
    REASON_PAIR_ANALYSIS,
)

# --- PR 01-08 new module imports ------------------------------------------
from src.scanner.filter_module import check_pair_probability, get_pair_probability
from src.volatility_metrics import calculate_dynamic_sl_tp
from src.scanner.ws_optimizer import LatencyTracker, score_shard_health, select_priority_pairs
from src.api_limits import APIWeightTracker, BatchScheduler
from src.scanner.common_gates import run_common_gates, GateCheckResult
from src.logging_utils import SuppressionLogger, LatencyMonitor
from src.scanner.regime_manager import RegimeManager
# --------------------------------------------------------------------------

log = get_logger("scanner")

# Composite signal scoring engine — instantiated once at module level.
_scoring_engine = SignalScoringEngine()

# Statistical filter — tracks rolling win rates per (channel, pair, regime)
# and suppresses or penalises signals from historically poor combinations.
_stat_filter = StatisticalFilter()

# Order book spread cache TTL
_SPREAD_CACHE_TTL: float = 30.0

# Timeout for the global bookTicker pre-fetch issued every scan cycle.
_BOOK_TICKER_PREFETCH_TIMEOUT_S: float = 3.0

# TTL for spread entries seeded from the global bookTicker endpoint.
# bookTicker returns only bid/ask (no depth), so we keep the TTL shorter
# than the standard depth-based entry to encourage fresher polling.
_BOOK_TICKER_CACHE_TTL: float = 20.0

# ADX threshold below which SCALP signals are suppressed during RANGING regime
_RANGING_ADX_SUPPRESS_THRESHOLD: float = 15.0

# Chart pattern direction sets (used by scanner for chart_pattern_names population)
_CHART_BULLISH_PATTERNS: frozenset = frozenset({"DOUBLE_BOTTOM", "ASCENDING_TRIANGLE"})
_CHART_BEARISH_PATTERNS: frozenset = frozenset({"DOUBLE_TOP", "DESCENDING_TRIANGLE"})

# SCALP channel names — used for fast-path logic (correlated-exposure cap,
# cross-exchange verification skip, and WATCHLIST short-circuit).  All eight
# scalp-family channels are included so that these policies are applied
# consistently across the full family.
_SCALP_CHANNELS: frozenset = frozenset({
    "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD", "360_SCALP_VWAP",
    "360_SCALP_DIVERGENCE", "360_SCALP_SUPERTREND",
    "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
})

# Symbols permanently excluded from scanning — loaded from config to allow
# runtime override via the SCAN_SYMBOL_BLACKLIST env var.
_SYMBOL_BLACKLIST: frozenset = frozenset(SCAN_SYMBOL_BLACKLIST)

# Channel enable/disable map — sourced from config flags so operators can
# soft-disable noisy channels via env vars without touching code.
_CHANNEL_ENABLED_FLAGS: Dict[str, bool] = {
    "360_SCALP":            CHANNEL_SCALP_ENABLED,
    "360_SCALP_FVG":        CHANNEL_SCALP_FVG_ENABLED,
    "360_SCALP_ORDERBLOCK": CHANNEL_SCALP_ORDERBLOCK_ENABLED,
    "360_SCALP_DIVERGENCE": CHANNEL_SCALP_DIVERGENCE_ENABLED,
    "360_SCALP_CVD":        CHANNEL_SCALP_CVD_ENABLED,
    "360_SCALP_VWAP":       CHANNEL_SCALP_VWAP_ENABLED,
    "360_SCALP_SUPERTREND": CHANNEL_SCALP_SUPERTREND_ENABLED,
    "360_SCALP_ICHIMOKU":   CHANNEL_SCALP_ICHIMOKU_ENABLED,
}

# Product role intent (what the channel is for), independent from runtime
# activation state (what is currently enabled via env/runtime governance).
# Naming contract:
# - "paid" means core paid production role.
# - "specialist" means specialist strategy role that may be runtime-enabled
#   later without changing its product role label.
# Runtime role strings below combine this product role with enablement state.
_CHANNEL_PRODUCT_ROLES: Dict[str, str] = {
    "360_SCALP": "paid",
    "360_SCALP_FVG": "specialist",
    "360_SCALP_ORDERBLOCK": "specialist",
    "360_SCALP_DIVERGENCE": "specialist",
    "360_SCALP_CVD": "specialist",
    "360_SCALP_VWAP": "specialist",
    "360_SCALP_SUPERTREND": "specialist",
    "360_SCALP_ICHIMOKU": "specialist",
}

# Maximum number of symbols scanned concurrently
_MAX_CONCURRENT_SCANS: int = 20

# Protective mode thresholds — trigger when market is too volatile to trade
_PROTECTIVE_MODE_VOLATILE_THRESHOLD: int = 10   # volatile_unsuitable count across all channels
_PROTECTIVE_MODE_SPREAD_THRESHOLD: int = 20     # spread too wide count
_PROTECTIVE_MODE_COOLDOWN_S: float = 7200.0     # 2 hours between broadcasts

# Failed-detection cooldown — if a symbol/channel fails the confidence gate
# this many times consecutively, suppress it for _CONF_FAIL_COOLDOWN_S seconds.
_CONF_FAIL_MAX_CONSECUTIVE: int = 3
_CONF_FAIL_COOLDOWN_S: float = 60.0

# Regime-channel compatibility matrix.
# Maps channel name → list of regimes where that channel is blocked.
# SCALP channels (except VWAP) are no longer hard-blocked in QUIET — they
# instead receive a higher soft-gate penalty (_SCALP_QUIET_REGIME_PENALTY)
# and must meet a minimum confidence threshold (QUIET_SCALP_MIN_CONFIDENCE).
# VWAP remains blocked in QUIET because VWAP signals are meaningless without
# sufficient trading volume to anchor the indicator.
# SWING needs sustained trend: block in VOLATILE (chaotic, stops get swept).
_REGIME_CHANNEL_INCOMPATIBLE: Dict[str, List[str]] = {
    "360_SCALP_VWAP": ["QUIET"],
}

# Setup classes that do not require a liquidity sweep or SMC structural basis.
# These evaluators fire on session range, volume, or structure events that are
# valid without a sweep score >= SMC_HARD_GATE_MIN.
#
# PR-ARCH-6 additions:
#   LIQUIDATION_REVERSAL     — thesis: cascade + CVD divergence + RSI extreme +
#                              volume spike.  No sweep required.
#   FUNDING_EXTREME_SIGNAL   — thesis: funding-rate extremity + RSI + CVD divergence.
#                              Funding is the primary edge; sweep is not required.
#   DIVERGENCE_CONTINUATION  — thesis: order-flow / CVD divergence continuation.
#                              SMC score is structurally 0–2 for this path.
_SMC_GATE_EXEMPT_SETUPS: frozenset = frozenset({
    "OPENING_RANGE_BREAKOUT",
    "QUIET_COMPRESSION_BREAK",
    "VOLUME_SURGE_BREAKOUT",
    "BREAKDOWN_SHORT",
    "SR_FLIP_RETEST",
    # PR-ARCH-6: non-sweep setup families whose SMC score is structurally low
    "LIQUIDATION_REVERSAL",
    "FUNDING_EXTREME_SIGNAL",
    "DIVERGENCE_CONTINUATION",
    # Phase 2 — new path: displacement-based, not sweep-based; SMC score is
    # structurally low for this path.
    "POST_DISPLACEMENT_CONTINUATION",
    # Phase 2 roadmap step 7: structural price-level rejection, not sweep-based.
    # FAR uses its own structural gates (auction wick + reclaim); SMC sweep
    # score does not measure the failed-acceptance thesis.
    "FAILED_AUCTION_RECLAIM",
    # PR-05 gate-policy alignment:
    #   TREND_PULLBACK_EMA  — thesis: pullback to EMA9/EMA21 in a trending regime.
    #                         Entry signal is EMA structure + candle touch, not a
    #                         sweep event.  SMC sweep score is structurally low and
    #                         does not measure the trend-pullback thesis correctly.
    "TREND_PULLBACK_EMA",
    #   WHALE_MOMENTUM      — thesis: large-actor order-flow impulse confirmed by
    #                         OBI / tick delta.  No liquidity sweep required; sweep
    #                         score does not reflect the order-flow thesis.
    "WHALE_MOMENTUM",
})

# Setup classes whose signal thesis is NOT based on EMA alignment.
# Applying the trend hard gate (EMA alignment score) to these is incorrect.
_TREND_GATE_EXEMPT_SETUPS: frozenset = frozenset({
    "LIQUIDATION_REVERSAL",
    "FUNDING_EXTREME_SIGNAL",
    "WHALE_MOMENTUM",
    # PR-05 gate-policy alignment:
    #   FAILED_AUCTION_RECLAIM — thesis: price reclaims a failed auction / wick
    #                            rejection level.  The entry is anchored to the
    #                            auction structure, not EMA trend alignment.
    #                            Applying the trend hard gate (EMA score) is a
    #                            mismatch for this structural-rejection path.
    "FAILED_AUCTION_RECLAIM",
})

# Penalty multiplier applied to scalp-channel soft gates when the regime is
# QUIET.  Higher than the default QUIET multiplier (0.8) to ensure only
# top-tier signals — genuine mean-reversion setups — pass through.
_SCALP_QUIET_REGIME_PENALTY: float = 1.8

# Path-specific QUIET confidence floor for DIVERGENCE_CONTINUATION.
# Live evidence (PR-ARCH-5) shows this evaluator produces structurally valid
# candidates near 64.3 that are blocked by the global 65.0 floor.  A narrow
# override of 64.0 captures these genuine near-threshold setups without opening
# the gate to weaker quiet-market noise (53–58 range).
_QUIET_DIVERGENCE_MIN_CONFIDENCE: float = 64.0

# Penalty multiplier applied to soft-gate base penalties depending on live market regime.
# Trending markets → lenient (clear direction, fewer false signals).
# Volatile markets → strict (high chaos, amplify quality gates).
_REGIME_PENALTY_MULTIPLIER: Dict[str, float] = {
    "TRENDING_UP":   0.6,   # Strong trend = clear direction, lenient penalties
    "TRENDING_DOWN": 0.6,   # Same — sustained trend, gates matter less
    "RANGING":       1.0,   # Mean-reversion market, all quality gates at full weight
    "VOLATILE":      1.5,   # High chaos = more false signals, amplify penalties
    "QUIET":         0.8,   # Low volume but stable, gates fire often on thin data
}

# Regime-specific MTF confluence configuration.
# min_score   — the minimum passing score for the hard MTF gate.
# higher_tf_weight — multiplier applied to 4h/1d weights (trend confirmation).
# lower_tf_weight  — multiplier applied to 1m/5m weights (entry precision).
# In TRENDING regimes the higher-TF alignment is critical; in RANGING the
# lower-TF precision matters more; in VOLATILE, MTF is relaxed because
# timeframes often diverge during volatile markets.
_MTF_REGIME_CONFIG: Dict[str, Dict[str, float]] = {
    "TRENDING_UP":   {"min_score": 0.6, "higher_tf_weight": 1.5, "lower_tf_weight": 0.8},
    "TRENDING_DOWN": {"min_score": 0.6, "higher_tf_weight": 1.5, "lower_tf_weight": 0.8},
    "RANGING":       {"min_score": 0.3, "higher_tf_weight": 0.7, "lower_tf_weight": 1.4},
    "VOLATILE":      {"min_score": 0.2, "higher_tf_weight": 1.0, "lower_tf_weight": 1.0},
    "QUIET":         {"min_score": 0.4, "higher_tf_weight": 0.8, "lower_tf_weight": 1.2},
}

# PR-1: first-stage family-aware MTF threshold policy for active 360_SCALP.
# This is intentionally a policy-table layer (family-specific min-score caps),
# not a full family-specific MTF semantic rewrite yet.
_SCALP_SETUP_TO_FAMILY: Dict[str, str] = {
    "TREND_PULLBACK_EMA": "trend_following",
    "VOLUME_SURGE_BREAKOUT": "breakout_momentum",
    "BREAKDOWN_SHORT": "breakout_momentum",
    "OPENING_RANGE_BREAKOUT": "breakout_momentum",
    "POST_DISPLACEMENT_CONTINUATION": "continuation",
    "CONTINUATION_LIQUIDITY_SWEEP": "continuation",
    "WHALE_MOMENTUM": "orderflow_momentum",
    "LIQUIDITY_SWEEP_REVERSAL": "reversal",
    "LIQUIDATION_REVERSAL": "reversal",
    "SR_FLIP_RETEST": "reclaim_retest",
    "FAILED_AUCTION_RECLAIM": "reclaim_retest",
    "FUNDING_EXTREME_SIGNAL": "mean_reversion",
    "QUIET_COMPRESSION_BREAK": "compression",
    "DIVERGENCE_CONTINUATION": "divergence",
}

_SCALP_MTF_POLICY_BY_FAMILY: Dict[str, Dict[str, Optional[float]]] = {
    # Explicitly intentional: TREND_PULLBACK_EMA stays on generic regime-driven
    # strictness (no PR-1 cap override for trend-following family).
    "trend_following": {"min_score_cap": None},
    "breakout_momentum": {"min_score_cap": None},
    "continuation": {"min_score_cap": 0.45},
    "orderflow_momentum": {"min_score_cap": 0.45},
    "reversal": {"min_score_cap": 0.35},
    "reclaim_retest": {"min_score_cap": 0.35},
    "mean_reversion": {"min_score_cap": 0.30},
    "divergence": {"min_score_cap": 0.30},
    "compression": {"min_score_cap": 0.25},
}

# Per-channel SMC timeframe preference order.
# SCALP → low-TF sweeps are valid entry triggers.
# Channels not listed here use the detector's default order.
_CHANNEL_SMC_TIMEFRAMES: Dict[str, tuple[str, ...]] = {
    "360_SCALP":              ("1m", "5m", "15m"),
    "360_SCALP_FVG":          ("5m", "15m"),
    "360_SCALP_CVD":          ("5m", "15m"),
    "360_SCALP_VWAP":         ("5m", "15m"),
    "360_SCALP_DIVERGENCE":   ("5m", "15m"),
    "360_SCALP_SUPERTREND":   ("5m", "15m"),
    "360_SCALP_ICHIMOKU":     ("5m", "15m"),
    "360_SCALP_ORDERBLOCK":   ("5m", "15m"),
}

# Which gates are active per channel family.
# True = gate runs normally, False = gate is skipped entirely.
# Channels not listed default to all-True (fail-safe).
_CHANNEL_GATE_PROFILE: Dict[str, Dict[str, bool]] = {
    # SCALP channels: ALL gates active — microstructure matters at 1m/5m
    "360_SCALP":      {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_FVG":  {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_CVD":  {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_VWAP": {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_DIVERGENCE":  {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_SUPERTREND":  {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_ICHIMOKU":    {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_ORDERBLOCK":  {"mtf": True,  "vwap": True,  "kill_zone": True,  "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
}

# Per-channel soft penalty base weights.
# These override the hard-coded defaults in _prepare_signal().
# Gates not listed use the original fallback values.
_CHANNEL_PENALTY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "360_SCALP":      {"vwap": 15.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 12.0},
    "360_SCALP_FVG":  {"vwap": 15.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 12.0},
    "360_SCALP_CVD":  {"vwap": 12.0, "kill_zone": 8.0,  "oi": 10.0, "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0},
    "360_SCALP_VWAP": {"vwap": 18.0, "kill_zone": 8.0,  "oi": 6.0,  "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0},
    "360_SCALP_DIVERGENCE":  {"vwap": 12.0, "kill_zone": 8.0,  "oi": 8.0,  "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0},
    "360_SCALP_SUPERTREND":  {"vwap": 12.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 10.0},
    "360_SCALP_ICHIMOKU":    {"vwap": 10.0, "kill_zone": 8.0,  "oi": 8.0,  "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0},
    "360_SCALP_ORDERBLOCK":  {"vwap": 12.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 12.0},
}


def _normalize_candle_dict(cd: dict) -> dict:
    """Ensure all array-like values in a candle dict are flat 1-D Python lists.

    Candle data can occasionally arrive from the data store as 2-D numpy arrays
    of shape ``(n, 1)`` instead of the expected 1-D shape ``(n,)``.  This causes
    ``ValueError: The truth value of an array with more than one element is
    ambiguous`` in any downstream code that uses the array in a boolean context
    (e.g. ``if closes:``).  Converting everything to a plain Python list at the
    data-store boundary protects all downstream consumers.
    """
    normalized: dict = {}
    for key, val in cd.items():
        if isinstance(val, np.ndarray):
            normalized[key] = np.asarray(val, dtype=np.float64).ravel().tolist()
        elif isinstance(val, list):
            try:
                normalized[key] = np.asarray(val, dtype=np.float64).ravel().tolist()
            except (ValueError, TypeError) as exc:
                log.debug("_normalize_candle_dict: could not flatten list for key '{}': {}", key, exc)
                normalized[key] = val
        else:
            normalized[key] = val
    return normalized


def classify_signal_tier(confidence: float) -> str:
    """Classify a signal into a quality tier based on its confidence score.

    Parameters
    ----------
    confidence:
        Signal confidence (0–100 scale).

    Returns
    -------
    One of: ``"A+"`` (sniper, 80-100), ``"B"`` (setup, 65-79),
    ``"WATCHLIST"`` (50-64), ``"FILTERED"`` (< 50).
    """
    if confidence >= 80:
        return "A+"
    elif confidence >= 65:
        return "B"
    elif confidence >= 50:
        return "WATCHLIST"
    return "FILTERED"


@dataclass
class ScanContext:
    candles: Dict[str, dict]
    indicators: Dict[str, dict]
    smc_result: Any
    smc_data: dict
    regime_result: Any
    ai: Dict[str, Any]
    spread_pct: float
    ind_for_predict: Dict[str, Any]
    is_ranging: bool
    adx_val: float
    onchain_data: Any
    candle_total: int
    pair_quality: PairQualityAssessment
    market_state: MarketState
    regime_context: Any = None  # RegimeContext from regime detector


_SCORE_MIN: float = 0.0
_SCORE_MAX: float = 100.0


class Scanner:
    """Scans all pairs across channel strategies on every cycle.

    Parameters
    ----------
    pair_mgr:
        :class:`src.pair_manager.PairManager` instance.
    data_store:
        :class:`src.historical_data.HistoricalDataStore` instance.
    channels:
        List of channel strategy objects.
    smc_detector:
        :class:`src.detector.SMCDetector` instance.
    regime_detector:
        :class:`src.regime.MarketRegimeDetector` instance.
    predictive:
        :class:`src.predictive_ai.PredictiveEngine` instance.
    exchange_mgr:
        :class:`src.exchange.ExchangeManager` instance.
    spot_client:
        Optional :class:`src.binance.BinanceClient` for order book fetches.
    telemetry:
        :class:`src.telemetry.TelemetryCollector` instance.
    signal_queue:
        :class:`src.signal_queue.SignalQueue` instance.
    router:
        :class:`src.signal_router.SignalRouter` instance.
    """

    def __init__(
        self,
        pair_mgr: Any,
        data_store: Any,
        channels: List[Any],
        smc_detector: Any,
        regime_detector: Any,
        predictive: Any,
        exchange_mgr: Any,
        spot_client: Optional[Any],
        telemetry: Any,
        signal_queue: Any,
        router: Any,
        openai_evaluator: Optional[Any] = None,
        onchain_client: Optional[Any] = None,
        order_flow_store: Optional[Any] = None,
        tier_manager: Optional[TierManager] = None,
    ) -> None:
        self.pair_mgr = pair_mgr
        self.data_store = data_store
        self.channels = channels
        self.smc_detector = smc_detector
        self.regime_detector = regime_detector
        self.predictive = predictive
        self.exchange_mgr = exchange_mgr
        self.spot_client: Optional[Any] = spot_client
        self.futures_client: Optional[Any] = None
        self.telemetry = telemetry
        self.signal_queue = signal_queue
        self.router = router
        self.openai_evaluator: Optional[Any] = openai_evaluator
        self.onchain_client: Optional[Any] = onchain_client
        self.order_flow_store: Optional[Any] = order_flow_store

        # Optional dynamic tier manager (PR 2 — Market Watchdog & Dynamic Tiering).
        # When present, get_symbol_tier() delegates to TierManager.get_tier() which
        # returns a live, volume+volatility-ranked PairTier refreshed every ~5 min.
        # When absent, the scanner falls back to the PairManager's static tier
        # assignment (rank-by-volume-only, updated on pair refresh).
        self.tier_manager: Optional[TierManager] = tier_manager

        # Stateful signal-quality enhancement modules
        self.feedback_loop: FeedbackLoop = FeedbackLoop()
        self.cluster_suppressor: ClusterSuppressor = ClusterSuppressor()
        self.confluence_detector: ConfluenceDetector = ConfluenceDetector()

        # Mutable state shared with the engine / command handler
        self.paused_channels: Set[str] = set()
        self.confidence_overrides: Dict[str, float] = {}
        self.force_scan: bool = False

        # WebSocket managers (set after boot)
        self.ws_spot: Optional[Any] = None
        self.ws_futures: Optional[Any] = None

        # Optional circuit breaker (set after construction)
        self.circuit_breaker: Optional[Any] = None

        # Optional gem scanner (set after construction)
        self.gem_scanner: Optional[Any] = None

        # Order book spread cache: symbol → (spread_pct, expiry_monotonic_time)
        # expiry_monotonic_time is an absolute time.monotonic() value; the entry
        # is valid while time.monotonic() < expiry_monotonic_time.
        self._order_book_cache: Dict[str, Tuple[float, float]] = {}

        # Cooldown tracking: (symbol, channel_name) → monotonic expiry time
        self._cooldown_until: Dict[Tuple[str, str], float] = {}

        # Global cross-channel per-symbol+direction cooldown tracker.
        # Maps (symbol, direction) → monotonic timestamp when the cooldown expires.
        # Directional: a LONG signal does not block a SHORT on the same symbol.
        self._global_symbol_cooldown: Dict[Tuple[str, str], float] = {}

        # Rolling BTC correlation cache: symbol → (correlation, expiry_monotonic)
        # Recomputed once per scan cycle per symbol, cached to avoid redundant work.
        self._btc_correlation_cache: Dict[str, float] = {}
        self._btc_correlation_expiry: Dict[str, float] = {}

        # Regime history: symbol → list of (monotonic_time, regime_value) tuples
        # Used to detect oscillating / unstable regimes (too many flips in window).
        self._regime_history: Dict[str, List[Tuple[float, str]]] = {}
        # Most recent overall-market regime value (updated per scan cycle; used by
        # gem scanner for adaptive threshold adjustment — feature 7).
        self._last_market_regime: str = "RANGING"

        # Semaphore to limit concurrent symbol scans
        self._scan_semaphore: asyncio.Semaphore = asyncio.Semaphore(_MAX_CONCURRENT_SCANS)

        # Tiered scanning counters
        self._scan_cycle_count: int = 0
        self._last_tier3_scan_time: float = 0.0

        # Setup diversity telemetry: rolling count of evaluated signals per
        # setup_class, logged every 100 scan cycles for operational visibility.
        self._setup_eval_counts: Dict[str, int] = defaultdict(int)
        self._setup_emit_counts: Dict[str, int] = defaultdict(int)
        # End-to-end path observability counters (rolling 100-scan window).
        self._path_funnel_counters: Dict[str, int] = defaultdict(int)
        self._channel_funnel_counters: Dict[str, int] = defaultdict(int)

        # Scoring tier telemetry: accumulates candidate counts per setup_class
        # and score tier across cycles; logged every 100 scan cycles to diagnose
        # funnel distribution across paths.
        self._scoring_tier_counters: Dict[str, int] = defaultdict(int)
        # Scoring distribution telemetry: pre-penalty vs post-penalty score
        # bands and tiers by channel/family/path for PR-7A runtime validation.
        self._scoring_distribution_counters: Dict[str, int] = defaultdict(int)

        # WS health-aware scan gating: counts consecutive cycles where both
        # WS managers are unhealthy, used to trigger an admin alert.
        self._consecutive_ws_degraded_cycles: int = 0

        # Per-cycle WS degradation flag: True when either WS manager is
        # partially degraded.  Set at the start of each scan cycle and used
        # by _get_spread_pct to apply tighter REST fetch limits.
        self._ws_any_degraded_this_cycle: bool = False

        # Suppression telemetry: counters per suppression reason, accumulated
        # over each scan cycle and logged as a summary at cycle end.
        self._suppression_counters: Dict[str, int] = defaultdict(int)

        # Failed-detection cooldown: tracks consecutive confidence-gate failures
        # per (symbol, channel_name) to suppress re-evaluation for a short period.
        # Key: (symbol, channel_name) → (fail_count: int, suppressed_until: float)
        self._conf_fail_tracker: Dict[tuple, tuple] = {}

        # Protective mode broadcaster state
        # Tracks whether the engine is currently in protective mode (broadcasted to channels)
        self._protective_mode_active: bool = False
        self._protective_mode_broadcast_time: float = 0.0  # monotonic time of last broadcast

        # Suppression tracker — records structured suppression events for
        # Telegram digest and data-driven threshold tuning.
        self.suppression_tracker: SuppressionTracker = SuppressionTracker()

        # --- PR 01-08 new module instances --------------------------------
        # PR 01: High-probability filter (pair probability scoring)
        self.suppression_logger: SuppressionLogger = SuppressionLogger()
        # PR 03: Scan latency tracker for adaptive pair prioritisation
        self.latency_tracker: LatencyTracker = LatencyTracker()
        # PR 04: API weight tracker and batch scheduler
        self.api_weight_tracker: APIWeightTracker = APIWeightTracker()
        self.batch_scheduler: BatchScheduler = BatchScheduler()
        # PR 06: Latency monitor for pipeline component tracking
        self.latency_monitor: LatencyMonitor = LatencyMonitor()
        # PR 07: Regime-adaptive channel scheduling
        self.regime_manager: RegimeManager = RegimeManager()
        # -----------------------------------------------------------------

        # Radar scores: channel_name → {symbol, confidence, bias, ...}
        # Populated by the radar evaluation pass for soft-disabled channels.
        # Read by _get_scanner_context() → RadarChannel every 30s.
        self._radar_scores: Dict[str, Any] = {}
        self._last_channel_governance_snapshot: Dict[str, Dict[str, Any]] = {}
        self._rollout_fail_closed_logged: Set[str] = set()

        # Data fetcher — delegates kline and order-book retrieval
        self._data_fetcher = DataFetcher(
            data_store=data_store,
            exchange_mgr=exchange_mgr,
            spot_client=spot_client,
        )

        # Indicator result cache: symbol → (fingerprint, indicator_dict)
        # fingerprint is a tuple of (tf, last_close) pairs — cheap to compute,
        # invalidates automatically whenever any timeframe gets a new candle.
        self._indicator_cache: Dict[str, tuple] = {}

        # PR8: Dynamic pair promotion — volume baseline tracker and promoted pairs
        # symbol → last known 24h volume (used to detect surge events)
        self._volume_baseline: Dict[str, float] = {}
        # symbol → cycles remaining (non-scan pairs temporarily added to universe)
        self._promoted_pairs: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Dynamic tier query helper
    # ------------------------------------------------------------------

    def _classify_channel_runtime_role(self, channel_name: str) -> str:
        """Return explicit runtime role for channel governance telemetry."""
        _default_enabled = CHANNEL_ENABLE_DEFAULTS.get(channel_name, False)
        _product_role = _CHANNEL_PRODUCT_ROLES.get(channel_name, "specialist")
        _rollout_state = self._resolve_channel_rollout_state(channel_name)
        if _rollout_state == "full_live":
            if _product_role == "paid":
                return "runtime_active_paid"
            return "specialist_full_live"
        if _rollout_state == "limited_live":
            return "specialist_limited_live"
        if _rollout_state == "radar_only":
            return "radar_only"
        if not _default_enabled:
            return "intentionally_disabled"
        return "governance_disabled"

    def _resolve_channel_rollout_state(self, channel_name: str) -> str:
        """Resolve rollout state with explicit fail-closed handling."""
        _raw = str(CHANNEL_ROLLOUT_STATE_DEFAULTS.get(channel_name, "disabled")).strip().lower()
        if _raw in CHANNEL_ROLLOUT_STATES_ALLOWED:
            # Runtime flag acts as emergency kill-switch for live rollout states.
            # Missing channel entries intentionally fail-closed to disabled.
            if _raw in {"full_live", "limited_live"} and not _CHANNEL_ENABLED_FLAGS.get(channel_name, False):
                return "disabled"
            if _raw == "radar_only":
                _radar_governed = CHANNEL_RADAR_ROLE_DEFAULTS.get(channel_name, False)
                if not _radar_governed:
                    return "disabled"
            return _raw
        _key = f"{channel_name}:{_raw or 'empty'}"
        if _key not in self._rollout_fail_closed_logged:
            self._rollout_fail_closed_logged.add(_key)
            log.warning(
                "Unknown rollout state for {}: {!r} — fail-closing to disabled",
                channel_name,
                _raw,
            )
        return "disabled"

    def _is_live_rollout_enabled_for_symbol(self, channel_name: str, symbol: str) -> bool:
        """Return True when channel is allowed to evaluate on live paid path."""
        _state = self._resolve_channel_rollout_state(channel_name)
        if _state == "full_live":
            return True
        if _state != "limited_live":
            return False
        _pilot_symbols = CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS.get(channel_name, frozenset())
        return symbol in _pilot_symbols

    def _is_radar_rollout_enabled(self, channel_name: str, symbol: str) -> bool:
        """Return True when channel is allowed on observe-only radar path."""
        _state = self._resolve_channel_rollout_state(channel_name)
        if _state == "radar_only":
            return True
        if _state == "limited_live":
            # Keep observe-only visibility outside pilot scope.
            return not self._is_live_rollout_enabled_for_symbol(channel_name, symbol)
        return False

    def _record_rollout_live_exclusion(self, channel_name: str, symbol: str) -> None:
        """Emit explicit telemetry when rollout policy excludes a live-path evaluation."""
        _state = self._resolve_channel_rollout_state(channel_name)
        self._channel_funnel_counters[f"rollout_excluded:live:{_state}:{channel_name}"] += 1
        if _state == "limited_live":
            _pilot_symbols = CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS.get(channel_name, frozenset())
            if symbol not in _pilot_symbols:
                self._channel_funnel_counters[
                    f"rollout_excluded:live:limited_live_non_pilot:{channel_name}"
                ] += 1

    def _channel_governance_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """Build inspectable runtime/default governance truth for all channels."""
        _snapshot: Dict[str, Dict[str, Any]] = {}
        for _chan_name, _runtime_enabled in _CHANNEL_ENABLED_FLAGS.items():
            _rollout_state = self._resolve_channel_rollout_state(_chan_name)
            _pilot_symbols = sorted(CHANNEL_LIMITED_LIVE_PILOT_SYMBOLS.get(_chan_name, frozenset()))
            _snapshot[_chan_name] = {
                "product_role": _CHANNEL_PRODUCT_ROLES.get(_chan_name, "specialist"),
                "config_default_enabled": CHANNEL_ENABLE_DEFAULTS.get(
                    _chan_name, False,
                ),
                "runtime_enabled": _runtime_enabled,
                "runtime_role": self._classify_channel_runtime_role(_chan_name),
                "rollout_state": _rollout_state,
                "rollout_live_enabled": _rollout_state in {"limited_live", "full_live"},
                "rollout_radar_enabled": _rollout_state in {"limited_live", "radar_only"},
                "limited_live_pilot_symbols": _pilot_symbols,
            }
        return _snapshot

    def get_symbol_tier(self, symbol: str) -> PairTier:
        """Return the current :class:`~src.pair_manager.PairTier` for *symbol*.

        Resolution order
        ----------------
        1. If a :class:`~src.tier_manager.TierManager` is attached, delegate to
           its live volume+volatility-ranked tier assignment (refreshed every
           ~5 minutes by the background polling loop).
        2. Otherwise fall back to the :class:`~src.pair_manager.PairManager`
           static tier — the volume-rank assignment from the last pair refresh.
        3. If the symbol is not found in either source, return
           :attr:`~src.pair_manager.PairTier.TIER3` as a safe default.
        """
        if self.tier_manager is not None:
            return self.tier_manager.get_tier(symbol)
        info = self.pair_mgr.pairs.get(symbol)
        if info is not None:
            return info.tier
        return PairTier.TIER3

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def diagnose_pair(self, symbol: str) -> dict:
        """Run the signal pipeline in dry-run mode, returning gate-by-gate diagnostics."""
        results: dict = {"symbol": symbol, "gates": {}, "signal_paths": {}, "error": None}
        try:
            candles: dict = {}
            for tf in ("1m", "5m", "15m", "1h", "4h"):
                c = self.data_store.get_candles(symbol, tf)
                if c:
                    candles[tf] = c

            m5 = candles.get("5m", {})
            closes_5m = m5.get("close", [])
            if not closes_5m:
                results["error"] = f"No 5m candle data for {symbol}"
                return results

            close = float(closes_5m[-1])

            indicators: dict = {}
            for tf in ("1m", "5m", "15m", "1h"):
                ind = self.data_store.get_indicators(symbol, tf)
                if ind:
                    indicators[tf] = ind

            ind5 = indicators.get("5m", {})

            spread_pct = self.data_store.get_spread(symbol) or 0.0
            volume_24h = self.data_store.get_volume(symbol) or 0.0

            regime_result = self.data_store.get_regime(symbol)
            regime = str(getattr(regime_result, "regime", "RANGING")) if regime_result else "RANGING"

            smc_data = self.data_store.get_smc(symbol) or {}

            gates = results["gates"]

            gates["regime"] = {"value": regime, "pass": True}

            spread_threshold = 0.02
            gates["spread"] = {
                "value": round(spread_pct, 4),
                "threshold": spread_threshold,
                "pass": spread_pct < spread_threshold,
            }

            from config import REGIME_MIN_VOLUME_USD
            vol_floor = REGIME_MIN_VOLUME_USD.get(regime, 1_000_000.0)
            gates["volume"] = {
                "value": round(volume_24h, 0),
                "floor": vol_floor,
                "pass": volume_24h >= vol_floor,
            }

            sweeps = smc_data.get("sweeps", [])
            fvgs = smc_data.get("fvg", [])
            orderblocks = smc_data.get("orderblocks", [])
            gates["smc"] = {
                "sweeps": len(sweeps),
                "fvgs": len(fvgs),
                "orderblocks": len(orderblocks),
                "pass": bool(sweeps or fvgs or orderblocks),
            }

            ema9 = ind5.get("ema9_last")
            ema21 = ind5.get("ema21_last")
            ema50 = ind5.get("ema50_last")
            gates["ema"] = {
                "ema9": ema9,
                "ema21": ema21,
                "ema50": ema50,
                "aligned_long": bool(ema9 and ema21 and ema9 > ema21),
                "aligned_short": bool(ema9 and ema21 and ema9 < ema21),
            }

            momentum = ind5.get("momentum_last")
            gates["momentum"] = {"value": momentum, "threshold": 0.15}

            macd_hist = ind5.get("macd_histogram_last")
            gates["macd"] = {
                "histogram": macd_hist,
                "direction": "bullish" if macd_hist and macd_hist > 0 else "bearish",
            }

            rsi = ind5.get("rsi_last")
            gates["rsi"] = {"value": rsi}

            cvd_data = smc_data.get("cvd")
            funding_rate = smc_data.get("funding_rate")
            gates["order_flow"] = {
                "cvd_available": cvd_data is not None,
                "funding_rate": funding_rate,
            }

            from datetime import datetime, timezone as _tz
            now_hour = datetime.now(_tz.utc).hour
            in_kill_zone = (7 <= now_hour < 10) or (12 <= now_hour < 16)
            gates["kill_zone"] = {"hour_utc": now_hour, "active": in_kill_zone}

            from src.channels.scalp import ScalpChannel
            ch = ScalpChannel()
            for method_name in (
                "_evaluate_standard",
                "_evaluate_trend_pullback",
                "_evaluate_liquidation_reversal",
                "_evaluate_whale_momentum",
                "_evaluate_volume_surge_breakout",
                "_evaluate_breakdown_short",
                "_evaluate_opening_range_breakout",
                "_evaluate_sr_flip_retest",
                "_evaluate_funding_extreme",
                "_evaluate_quiet_compression_break",
                "_evaluate_divergence_continuation",
            ):
                method = getattr(ch, method_name, None)
                if method is None:
                    continue
                try:
                    sig = method(symbol, candles, indicators, smc_data, spread_pct, volume_24h, regime)
                    if sig is not None:
                        results["signal_paths"][method_name] = {
                            "fired": True,
                            "direction": sig.direction.value,
                            "confidence": sig.confidence,
                            "setup_class": sig.setup_class,
                        }
                    else:
                        results["signal_paths"][method_name] = {"fired": False}
                except Exception as exc:
                    results["signal_paths"][method_name] = {"fired": False, "error": str(exc)}

        except Exception as exc:
            results["error"] = str(exc)

        return results

    def _update_volume_baseline(self, sorted_pairs_set: set) -> List[str]:
        """Detect volume surge events in the full pair universe and temporarily
        promote non-scanned pairs into the scan cycle.

        Uses ``pair_mgr.pairs`` as the source of truth for current 24h volume.
        Pairs with a volume that is ``SURGE_PROMOTION_VOLUME_MULTIPLIER`` × higher
        than their previous baseline AND whose volume exceeds ``SCAN_MIN_VOLUME_USD``
        are added to ``_promoted_pairs`` for 3 scan cycles.

        Parameters
        ----------
        sorted_pairs_set:
            Set of symbol strings currently in the active scan universe.

        Returns
        -------
        List[str]
            List of currently promoted symbols (symbols NOT in sorted_pairs_set
            that have been temporarily added to the scan universe).
        """
        now_promoted: List[str] = []

        for symbol, info in list(self.pair_mgr.pairs.items()):
            current_vol = info.volume_24h_usd
            baseline = self._volume_baseline.get(symbol, 0.0)

            # Detect surge for pairs outside the active scan universe
            if symbol not in sorted_pairs_set:
                if (
                    baseline > 0
                    and current_vol > baseline * SURGE_PROMOTION_VOLUME_MULTIPLIER
                    and current_vol > SCAN_MIN_VOLUME_USD
                ):
                    ratio = current_vol / baseline
                    log.info(
                        "🚀 SURGE PROMOTION: {} volume {:.0f} is {:.1f}× baseline "
                        "— adding to scan for 3 cycles",
                        symbol, current_vol, ratio,
                    )
                    self._promoted_pairs[symbol] = 3

            # Update baseline for all known pairs
            self._volume_baseline[symbol] = current_vol

        # Decrement counters for currently promoted pairs; remove when expired
        for sym in list(self._promoted_pairs.keys()):
            if sym in sorted_pairs_set:
                # Pair re-entered the main scan universe — no longer needs promotion
                del self._promoted_pairs[sym]
            else:
                remaining = self._promoted_pairs[sym] - 1
                if remaining <= 0:
                    del self._promoted_pairs[sym]
                else:
                    self._promoted_pairs[sym] = remaining
                    now_promoted.append(sym)

        return now_promoted[:SURGE_PROMOTION_MAX_PAIRS]

    async def scan_loop(self) -> None:
        """Periodic scan over all pairs / channels."""
        log.info("Scanner loop started")
        log.info(
            "Scanner config: TOP50_FUTURES_ONLY={} TOP50_FUTURES_COUNT={} pairs",
            TOP50_FUTURES_ONLY, TOP50_FUTURES_COUNT,
        )
        while True:
            t0 = time.monotonic()
            self._scan_cycle_count += 1

            _governance_snapshot = self._channel_governance_snapshot()
            if _governance_snapshot != self._last_channel_governance_snapshot:
                self._last_channel_governance_snapshot = _governance_snapshot
                log.info(
                    "Channel governance runtime roles: {}",
                    _governance_snapshot,
                )

            # Always clean up expired signals first (safety net for stuck slots)
            expired_count = self.router.cleanup_expired()
            if expired_count > 0:
                log.info("Cleaned up {} expired signals at start of scan cycle", expired_count)

            # Skip scanning when circuit breaker is tripped
            if self.circuit_breaker and self.circuit_breaker.is_tripped():
                log.warning("Circuit breaker tripped — skipping scan cycle")
                await asyncio.sleep(5)
                continue

            # WS health-aware scan gating: when both WS managers are unhealthy
            # (or not set) there is no live kline data, so a full scan over
            # 796 pairs burns API weight on stale candles and produces no
            # signals.  Skip the full scan and track degraded-cycle count.
            ws_spot_ok = self.ws_spot.is_healthy if self.ws_spot else True
            ws_futures_ok = self.ws_futures.is_healthy if self.ws_futures else True
            ws_both_unhealthy = not ws_spot_ok and not ws_futures_ok
            # Partial degradation: either manager has below-threshold health.
            # Used to tighten REST fetch limits for the remainder of the cycle.
            ws_spot_ratio = self.ws_spot.health_ratio if self.ws_spot else 1.0
            ws_futures_ratio = self.ws_futures.health_ratio if self.ws_futures else 1.0
            self._ws_any_degraded_this_cycle = (
                ws_spot_ratio < WS_PARTIAL_HEALTH_THRESHOLD
                or ws_futures_ratio < WS_PARTIAL_HEALTH_THRESHOLD
            )
            if ws_both_unhealthy:
                self._consecutive_ws_degraded_cycles += 1
                # After WS_DEGRADED_MAX_CYCLES, stop blocking and fall through
                # to REST-only scanning so the engine is not stuck forever.
                if self._consecutive_ws_degraded_cycles < WS_DEGRADED_MAX_CYCLES:
                    log.warning(
                        "WS health degraded (spot={}, futures={}) — skipping full scan "
                        "(degraded cycle #{})",
                        ws_spot_ok, ws_futures_ok, self._consecutive_ws_degraded_cycles,
                    )
                    if self._consecutive_ws_degraded_cycles == WS_DEGRADED_CYCLES_ALERT:
                        try:
                            _alert_fn = self.telemetry.get_admin_alert_callback()
                            if _alert_fn is not None:
                                await _alert_fn(
                                    f"⚠️ WebSocket unhealthy for "
                                    f"{self._consecutive_ws_degraded_cycles} consecutive scan cycles. "
                                    "Scan is paused until WS recovers. Consider /restart."
                                )
                        except Exception:
                            pass
                    elapsed_ms = (time.monotonic() - t0) * 1000
                    self.telemetry.set_scan_latency(elapsed_ms)
                    ws_conns = (
                        (self.ws_spot.stream_count if self.ws_spot else 0)
                        + (self.ws_futures.stream_count if self.ws_futures else 0)
                    )
                    self.telemetry.set_ws_health(False, ws_conns)
                    await asyncio.sleep(5)
                    continue
                else:
                    if self._consecutive_ws_degraded_cycles == WS_DEGRADED_MAX_CYCLES:
                        log.warning(
                            "WS degraded for {} cycles — falling back to REST-only scanning",
                            self._consecutive_ws_degraded_cycles,
                        )
                        try:
                            _alert_fn = self.telemetry.get_admin_alert_callback()
                            if _alert_fn is not None:
                                await _alert_fn(
                                    f"⚠️ WebSocket degraded for {self._consecutive_ws_degraded_cycles} "
                                    "cycles — switching to REST-only scanning."
                                )
                        except Exception:
                            pass
            else:
                if self._consecutive_ws_degraded_cycles > 0:
                    log.info(
                        "WS health restored after {} degraded cycles",
                        self._consecutive_ws_degraded_cycles,
                    )
                self._consecutive_ws_degraded_cycles = 0

            try:
                # Prioritise high-volume pairs for order book fetches
                sorted_pairs = sorted(
                    self.pair_mgr.pairs.items(),
                    key=lambda kv: kv[1].volume_24h_usd,
                    reverse=True,
                )

                # Top-50 futures-only mode (PR2): restrict universe to the
                # top-50 USDT-M futures pairs; spot pairs and lower-ranked
                # futures are excluded entirely from this scan cycle.
                if TOP50_FUTURES_ONLY:
                    top50 = self.pair_mgr.get_top50_futures_pairs()
                    if top50:
                        top50_set = set(top50)
                        sorted_pairs = [
                            (sym, info) for sym, info in sorted_pairs
                            if info.market == "futures" and sym in top50_set
                        ]
                    else:
                        # Fall back to futures-only scan when cache is not yet
                        # populated (first cycle before first refresh completes).
                        sorted_pairs = [
                            (sym, info) for sym, info in sorted_pairs
                            if info.market == "futures"
                        ]

                # Tiered scanning:
                #   Tier 1 → every cycle (full scan, all channels)
                #   Tier 2 → every TIER2_SCAN_EVERY_N_CYCLES cycles (SWING+SPOT only)
                #   Tier 3 → every TIER3_SCAN_EVERY_N_CYCLES cycles (cycle-based)
                #            OR on the time-based interval (whichever fires first)
                scan_tier2 = (self._scan_cycle_count % TIER2_SCAN_EVERY_N_CYCLES == 0)
                scan_tier3 = (self._scan_cycle_count % TIER3_SCAN_EVERY_N_CYCLES == 0)
                # In top-50 futures-only mode all included pairs are treated as
                # Tier 1 (full scan every cycle); tier filtering still applies
                # in the normal multi-tier path.
                if TOP50_FUTURES_ONLY:
                    pairs_this_cycle = list(sorted_pairs)
                else:
                    pairs_this_cycle = [
                        (sym, info) for sym, info in sorted_pairs
                        if info.tier == PairTier.TIER1
                        or (info.tier == PairTier.TIER2 and scan_tier2)
                        or (info.tier == PairTier.TIER3 and scan_tier3)
                    ]

                # Apply cheap in-memory pre-filters to reduce the number of
                # symbols that reach expensive API calls (order book, klines).
                # This keeps Binance weight consumption ~400/min for 200+ pairs.
                filtered_pairs = self._prefilter_pairs(pairs_this_cycle)

                # When WS is partially degraded, cap the scan set to top-N
                # pairs by volume.  This prevents querying REST /depth for
                # hundreds of pairs that lack live kline updates, which was
                # the primary cause of the 100% rate-limit exhaustion observed
                # when the futures WS dropped (WS=300, ok=False).
                if self._ws_any_degraded_this_cycle and len(filtered_pairs) > WS_DEGRADED_MAX_PAIRS:
                    filtered_pairs = filtered_pairs[:WS_DEGRADED_MAX_PAIRS]
                    log.warning(
                        "WS partially degraded (spot_ratio={:.0%}, futures_ratio={:.0%}) "
                        "— limiting scan to top {} pairs to protect REST rate limit",
                        ws_spot_ratio, ws_futures_ratio, WS_DEGRADED_MAX_PAIRS,
                    )

                # PR 3 — Tier-aware REST fallback: issue a single weight-
                # efficient global bookTicker call (Weight 2) to pre-populate
                # the spread cache for all Tier 2 and Tier 3 pairs every cycle.
                # This replaces per-symbol /depth calls for those tiers and
                # reserves the heavier /depth endpoint strictly for Tier 1
                # (Hot) pairs.  Previously gated behind WS-degraded only, but
                # always running it eliminates 30-50 individual REST calls per
                # cycle (each Weight 1, timeout-prone) with a single call.
                await self._fetch_global_book_tickers(market="futures")

                # PR8 — Dynamic pair promotion: detect volume surges in pairs
                # outside the current scan universe and temporarily add them.
                _sorted_pairs_set = {sym for sym, _ in sorted_pairs}
                _promoted = self._update_volume_baseline(_sorted_pairs_set)
                if _promoted:
                    # Add promoted pairs to filtered_pairs (capped at SURGE_PROMOTION_MAX_PAIRS)
                    _added = 0
                    _promoted_syms = {sym for sym, _ in filtered_pairs}
                    filtered_pairs = list(filtered_pairs)  # ensure mutable list once
                    for _promo_sym in _promoted:
                        if _promo_sym not in _promoted_syms:
                            _promo_info = self.pair_mgr.pairs.get(_promo_sym)
                            if _promo_info is not None:
                                filtered_pairs.append((_promo_sym, _promo_info))
                                _added += 1
                    if _added:
                        log.info("Added {} dynamically promoted pair(s) to scan cycle", _added)

                sem = self._scan_semaphore
                tasks = [
                    self._scan_symbol_bounded(sem, sym, info.volume_24h_usd)
                    for sym, info in filtered_pairs
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for sym_info, result in zip(filtered_pairs, results):
                    if isinstance(result, Exception):
                        log.warning(
                            "Scan error for {} ({}): {}",
                            sym_info[0], type(result).__name__, result,
                        )

                # Tier 3 lightweight scan (time-gated, independent of cycle count)
                _now = time.monotonic()
                if _now - self._last_tier3_scan_time >= TIER3_SCAN_INTERVAL_MINUTES * 60:
                    self._last_tier3_scan_time = _now
                    await self._lightweight_tier3_scan()


            except asyncio.CancelledError:
                break
            except Exception as exc:
                log.error("Scan loop error: {}", exc)

            elapsed_ms = (time.monotonic() - t0) * 1000
            self.telemetry.set_scan_latency(elapsed_ms)

            self.telemetry.set_pairs_monitored(len(self.pair_mgr.pairs))
            self.telemetry.set_active_signals(len(self.router.active_signals))
            try:
                qsize = await self.signal_queue.qsize()
            except Exception as exc:
                log.warning("Failed to read signal queue size: {}", exc)
                qsize = 0
            self.telemetry.set_queue_size(qsize)
            ws_conns = (
                (self.ws_spot.stream_count if self.ws_spot else 0)
                + (self.ws_futures.stream_count if self.ws_futures else 0)
            )
            ws_ok = (
                (self.ws_spot.is_healthy if self.ws_spot else True)
                and (self.ws_futures.is_healthy if self.ws_futures else True)
            )
            self.telemetry.set_ws_health(ws_ok, ws_conns)

            # Log suppression telemetry summary for this cycle, then reset.
            if self._suppression_counters:
                log.info(
                    "Scan cycle suppression summary: {}",
                    dict(self._suppression_counters),
                )

            # ── Protective Mode Broadcaster ─────────────────────────────────────────
            # Count total volatile_unsuitable hits and spread too wide hits this cycle.
            try:
                _volatile_count = sum(
                    v for k, v in self._suppression_counters.items()
                    if k.startswith("volatile_unsuitable:")
                )
                _spread_count = sum(
                    v for k, v in self._suppression_counters.items()
                    if k.startswith("pair_quality:spread too wide")
                )
                _now_mono = time.monotonic()
                _in_protective_mode = (
                    _volatile_count >= _PROTECTIVE_MODE_VOLATILE_THRESHOLD
                    or _spread_count >= _PROTECTIVE_MODE_SPREAD_THRESHOLD
                )

                if _in_protective_mode and not self._protective_mode_active:
                    # Entering protective mode — broadcast to both free and paid channels
                    self._protective_mode_active = True
                    self._protective_mode_broadcast_time = _now_mono
                    # Build context-aware message that only mentions triggering metric(s)
                    _trigger_parts = []
                    if _spread_count >= _PROTECTIVE_MODE_SPREAD_THRESHOLD:
                        _trigger_parts.append(f"spreads widened across {_spread_count} pairs")
                    if _volatile_count >= _PROTECTIVE_MODE_VOLATILE_THRESHOLD:
                        _trigger_parts.append(f"{_volatile_count} setups suppressed due to volatility")
                    _trigger_str = " · ".join(_trigger_parts) if _trigger_parts else (
                        f"Spreads widened across {_spread_count} pairs · "
                        f"{_volatile_count} setups suppressed due to volatility"
                    )
                    _protective_msg = (
                        "⚠️ *Market Alert — Protective Mode Active*\n\n"
                        f"{_trigger_str.capitalize()}.\n\n"
                        "Scanner is running but holding entries until conditions stabilise. "
                        "This is normal during high-impact events — patience protects capital."
                    )
                    try:
                        _alert_fn = self.telemetry.get_admin_alert_callback()
                        if _alert_fn is not None:
                            await _alert_fn(_protective_msg)
                    except Exception:
                        pass
                    # Also post to free channel via router if available
                    try:
                        if hasattr(self.router, "send_free_channel_message"):
                            await self.router.send_free_channel_message(_protective_msg)
                    except Exception:
                        pass
                    log.info(
                        "Protective mode ENTERED (volatile={}, spread_wide={})",
                        _volatile_count, _spread_count,
                    )

                elif not _in_protective_mode and self._protective_mode_active:
                    # Exiting protective mode — only broadcast if cooldown has passed
                    if _now_mono - self._protective_mode_broadcast_time >= _PROTECTIVE_MODE_COOLDOWN_S:
                        self._protective_mode_active = False
                        self._protective_mode_broadcast_time = _now_mono
                        _recovery_msg = (
                            "✅ *Market Conditions Normalising*\n\n"
                            "Spreads compressing · Volatility easing. "
                            "Scanner resuming full scan — watching for high-quality setups."
                        )
                        try:
                            _alert_fn = self.telemetry.get_admin_alert_callback()
                            if _alert_fn is not None:
                                await _alert_fn(_recovery_msg)
                        except Exception:
                            pass
                        try:
                            if hasattr(self.router, "send_free_channel_message"):
                                await self.router.send_free_channel_message(_recovery_msg)
                        except Exception:
                            pass
                        log.info("Protective mode EXITED")
                    else:
                        # Cooldown not elapsed — silently reset flag without broadcasting
                        self._protective_mode_active = False
            except Exception:
                pass
            # ── End Protective Mode Broadcaster ─────────────────────────────────────

            if self._suppression_counters:
                self._suppression_counters.clear()

            # Periodic cleanup of stale failed-detection entries (every 300 cycles)
            if self._scan_cycle_count % 300 == 0 and self._conf_fail_tracker:
                _now_clean = time.monotonic()
                self._conf_fail_tracker = {
                    k: v for k, v in self._conf_fail_tracker.items()
                    if v[1] > _now_clean  # keep only active suppressions
                    or v[0] < _CONF_FAIL_MAX_CONSECUTIVE  # or not yet at threshold
                }

            # Setup diversity telemetry: log evaluated and emitted counts per
            # setup_class every 100 scan cycles for operational visibility.
            if self._scan_cycle_count % 100 == 0 and self._setup_eval_counts:
                log.info(
                    "Signal diversity (last 100 cycles): evaluated={} emitted={}",
                    dict(self._setup_eval_counts),
                    dict(self._setup_emit_counts),
                )
                self._setup_eval_counts.clear()
                self._setup_emit_counts.clear()

            # Scoring tier distribution telemetry: log per-path score tier counts
            # every 100 scan cycles to diagnose funnel bias across setup classes.
            if self._scan_cycle_count % 100 == 0 and self._scoring_tier_counters:
                log.info(
                    "Scoring tier distribution (last 100 cycles): {}",
                    dict(self._scoring_tier_counters),
                )
                self._scoring_tier_counters.clear()
            if self._scan_cycle_count % 100 == 0 and self._scoring_distribution_counters:
                log.info(
                    "Scoring pre/post distribution (last 100 cycles): {}",
                    dict(self._scoring_distribution_counters),
                )
                self._scoring_distribution_counters.clear()
            if (
                self._scan_cycle_count % 100 == 0
                and (self._path_funnel_counters or self._channel_funnel_counters)
            ):
                log.info(
                    "Path funnel (last 100 cycles): path={} channel={}",
                    dict(self._path_funnel_counters),
                    dict(self._channel_funnel_counters),
                )
                self._path_funnel_counters.clear()
                self._channel_funnel_counters.clear()

            # Touch heartbeat file so healthcheck knows the scanner is alive
            # (FINDING-024).
            self._touch_heartbeat()

            if not self.force_scan:
                await asyncio.sleep(1)
            self.force_scan = False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    _HEARTBEAT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "scanner_heartbeat"
    )

    def _touch_heartbeat(self) -> None:
        """Update the heartbeat file timestamp so the healthcheck can verify
        that the scanner loop is actively running (FINDING-024)."""
        try:
            os.makedirs(os.path.dirname(self._HEARTBEAT_PATH), exist_ok=True)
            with open(self._HEARTBEAT_PATH, "w") as fh:
                fh.write(str(time.time()))
        except OSError:
            pass  # Best-effort; don't crash the scan loop

    def _is_in_global_cooldown(self, symbol: str, direction: str) -> bool:
        """Return True if (symbol, direction) is in the global directional cooldown."""
        key = (symbol, direction)
        expiry = self._global_symbol_cooldown.get(key)
        if expiry is None:
            return False
        if time.monotonic() < expiry:
            return True
        del self._global_symbol_cooldown[key]
        return False

    def _update_btc_correlation(self, symbol: str) -> None:
        """Compute and cache 50-candle rolling Pearson correlation vs BTC.

        Recomputed once per scan cycle per symbol.  Skipped if BTC candles
        or symbol candles are unavailable.
        """
        if symbol in ("BTCUSDT", "ETHUSDT"):
            self._btc_correlation_cache[symbol] = 1.0
            return

        _now = time.monotonic()
        _expiry = self._btc_correlation_expiry.get(symbol, 0.0)
        if _now < _expiry:
            return  # Already fresh for this cycle

        try:
            _btc_candles = self.data_store.get_candles("BTCUSDT", "5m") or {}
            _sym_candles = self.data_store.get_candles(symbol, "5m") or {}
            _btc_closes = _btc_candles.get("close", [])
            _sym_closes = _sym_candles.get("close", [])
            _n = min(len(_btc_closes), len(_sym_closes), 50)
            if _n >= 10:
                _x = np.asarray(_btc_closes[-_n:], dtype=np.float64)
                _y = np.asarray(_sym_closes[-_n:], dtype=np.float64)
                _x = _x - _x.mean()
                _y = _y - _y.mean()
                _std_x = np.std(_x)
                _std_y = np.std(_y)
                if _std_x > 0 and _std_y > 0:
                    _corr = float(np.dot(_x, _y) / (_n * _std_x * _std_y))
                    _corr = max(-1.0, min(1.0, _corr))
                    self._btc_correlation_cache[symbol] = _corr
                else:
                    self._btc_correlation_cache[symbol] = 0.7
            else:
                self._btc_correlation_cache[symbol] = 0.7  # conservative default
        except Exception:
            self._btc_correlation_cache[symbol] = 0.7  # fail-safe default

        # Cache valid for the current scan cycle (expire after 30s)
        self._btc_correlation_expiry[symbol] = _now + 30.0

    def _is_in_cooldown(self, symbol: str, channel_name: str) -> bool:
        """Return True if the (symbol, channel) pair is currently in cooldown."""
        key = (symbol, channel_name)
        expiry = self._cooldown_until.get(key)
        if expiry is None:
            return False
        if time.monotonic() < expiry:
            return True
        # Expired – clean up
        del self._cooldown_until[key]
        return False

    def _set_cooldown(self, symbol: str, channel_name: str) -> None:
        """Start the cooldown timer for (symbol, channel)."""
        cooldown_s = SIGNAL_SCAN_COOLDOWN_SECONDS.get(channel_name, 60)
        self._cooldown_until[(symbol, channel_name)] = (
            time.monotonic() + cooldown_s
        )
        log.debug(
            "Cooldown set for {} {} ({:.0f}s)", symbol, channel_name, cooldown_s
        )

    def _count_regime_flips(self, symbol: str, window_minutes: int = 30) -> int:
        """Return the number of regime transitions within the rolling window."""
        history = self._regime_history.get(symbol, [])
        if len(history) < 2:
            return 0
        cutoff = time.monotonic() - window_minutes * 60
        recent = [r for t, r in history if t >= cutoff]
        if len(recent) < 2:
            return 0
        return sum(1 for i in range(1, len(recent)) if recent[i] != recent[i - 1])

    def _is_regime_unstable(
        self,
        symbol: str,
        window_minutes: int = 30,
        max_flips: int = 2,
    ) -> bool:
        """Return True if the regime for *symbol* has flipped more than *max_flips*
        times within the last *window_minutes* minutes.

        A regime "flip" is any transition between distinct regime values in the
        recorded history.  When the count of flips exceeds the threshold the
        symbol is considered too noisy for TAPE-style signals.
        """
        return self._count_regime_flips(symbol, window_minutes) > max_flips

    def _prefilter_pairs(
        self, pairs: List[Tuple[str, Any]]
    ) -> List[Tuple[str, Any]]:
        """Return a cheaply-filtered subset of pairs for expensive API scans.

        Applies three in-memory checks (zero API calls) before the main scan
        loop creates tasks and acquires the concurrency semaphore:

        1. **Volume filter** – skip symbols whose 24h USD volume is below
           ``SCAN_MIN_VOLUME_USD``.  Thin markets rarely produce valid signals
           and every API call they trigger wastes Binance weight budget.
        2. **All-channel active-signal filter** – skip symbols that already
           have an active signal on *every* channel we scan.  The per-channel
           check inside :meth:`_should_skip_channel` would catch each one
           individually, but pre-filtering avoids even building the scan context.
        3. **All-channel cooldown filter** – skip symbols where every channel
           is currently in cooldown, for the same reason as above.

        Typically reduces 200+ symbols down to ~60-80 before any order-book or
        kline fetches are triggered, keeping weight consumption ~400/min.
        """
        channel_names = [c.config.name for c in self.channels]
        active_symbols_channels = {
            (s.symbol, s.channel)
            for s in self.router.active_signals.values()
        }
        result: List[Tuple[str, Any]] = []
        skipped_volume = skipped_all_active = skipped_all_cooldown = skipped_blacklist = 0

        for sym, info in pairs:
            # 0. Blacklist filter — gold-pegged / micro-cap junk that will never signal
            if sym in _SYMBOL_BLACKLIST:
                skipped_blacklist += 1
                continue
            # 1. Volume pre-filter — regime-aware volume floor.
            # Use the current market regime to pick the right threshold;
            # falls back to SCAN_MIN_VOLUME_USD when regime is unknown/None/unset.
            _vol_floor = REGIME_MIN_VOLUME_USD.get(
                getattr(self, "_last_market_regime", None) or "",
                SCAN_MIN_VOLUME_USD,
            )
            if info.volume_24h_usd < _vol_floor:
                skipped_volume += 1
                continue
            # 2. All channels already have an active signal for this symbol
            if channel_names and all(
                (sym, ch) in active_symbols_channels for ch in channel_names
            ):
                skipped_all_active += 1
                continue
            # 3. All channels are in cooldown for this symbol
            if channel_names and all(
                self._is_in_cooldown(sym, ch) for ch in channel_names
            ):
                skipped_all_cooldown += 1
                continue
            result.append((sym, info))

        if skipped_volume or skipped_all_active or skipped_all_cooldown or skipped_blacklist:
            log.debug(
                "Pre-filter: %d/%d symbols kept "
                "(skipped %d blacklist, %d low-volume, %d all-active, %d all-cooldown)",
                len(result), len(pairs),
                skipped_blacklist, skipped_volume, skipped_all_active, skipped_all_cooldown,
            )
        return result

    async def _scan_symbol_bounded(self, sem: asyncio.Semaphore, symbol: str, volume_24h: float) -> None:
        """Acquire *sem* then delegate to :meth:`_scan_symbol`."""
        async with sem:
            await self._scan_symbol(symbol, volume_24h)

    def _load_candles(self, symbol: str) -> Dict[str, dict]:
        """Load candles — delegated to DataFetcher."""
        candles: Dict[str, dict] = {}
        for tf in SEED_TIMEFRAMES:
            c = self.data_store.get_candles(symbol, tf.interval)
            if c:
                candles[tf.interval] = _normalize_candle_dict(c)
        return candles

    def _compute_indicators(self, candles: Dict[str, dict]) -> Dict[str, dict]:
        """Compute indicators — delegated to src/scanner/indicator_compute.py."""
        return compute_indicators_for_candle_dict(candles)

    async def _fetch_global_book_tickers(self, market: str = "futures") -> None:
        """Pre-populate the spread cache for ALL pairs using a single weight-efficient
        bookTicker call.

        Called every scan cycle to seed bid/ask spreads for all 50 symbols from a
        single /fapi/v1/ticker/bookTicker request (Weight: 2). This completely
        replaces per-symbol /fapi/v1/depth REST calls for spread calculation across
        all channels.

        Parameters
        ----------
        market:
            ``"futures"`` (default) or ``"spot"``.  The appropriate
            :class:`~src.binance.BinanceClient` instance is lazily created if
            not already present.
        """
        try:
            if market == "futures":
                if self.futures_client is None:
                    self.futures_client = BinanceClient("futures")
                client = self.futures_client
            else:
                if self.spot_client is None:
                    self.spot_client = BinanceClient("spot")
                client = self.spot_client

            tickers = await asyncio.wait_for(
                client.fetch_all_book_tickers(),
                timeout=_BOOK_TICKER_PREFETCH_TIMEOUT_S,
            )
            if not tickers:
                log.warning(
                    "Global bookTicker pre-fetch returned no data (market={})", market
                )
                return

            now = time.monotonic()
            populated = 0
            for symbol, entry in tickers.items():
                # /depth is now only fetched for spread via bookTicker — accurate
                # best-bid/ask spread for all channels at zero extra cost.
                # Skip only if there is already a fresh (non-bookTicker) cache entry.
                existing = self._order_book_cache.get(symbol)
                if existing and now < existing[1]:
                    continue
                try:
                    best_bid = float(entry.get("bidPrice", 0))
                    best_ask = float(entry.get("askPrice", 0))
                except (TypeError, ValueError):
                    continue
                if best_bid <= 0 or best_ask <= 0:
                    continue
                mid = (best_bid + best_ask) / 2.0
                if mid <= 0:
                    continue
                spread_pct = (best_ask - best_bid) / mid * 100.0
                self._order_book_cache[symbol] = (spread_pct, now + _BOOK_TICKER_CACHE_TTL)
                populated += 1

            log.debug(
                "Global bookTicker pre-fetch populated {} spread cache entries (all tiers)",
                populated,
            )
        except asyncio.TimeoutError:
            log.warning("Global bookTicker pre-fetch timed out (market={})", market)
        except Exception as exc:
            log.warning("Global bookTicker pre-fetch error (market={}): {}", market, exc)

    async def _get_spread_pct(self, symbol: str, market: str = "spot") -> float:
        """Return cached spread for *symbol* from the bookTicker pre-fetch.

        Depth endpoint calls (/fapi/v1/depth) have been removed from this path.
        Spread is now sourced exclusively from the global bookTicker pre-fetch
        issued at the start of every scan cycle (_fetch_global_book_tickers).
        This eliminates 50 per-cycle /depth REST calls that were the primary
        cause of 40s+ scan latency spikes when Binance depth was degraded.
        """
        now = time.monotonic()
        cached = self._order_book_cache.get(symbol)
        if cached and now < cached[1]:
            return cached[0]
        # bookTicker pre-fetch hasn't populated this symbol yet — return fallback
        return 0.01

    async def _fetch_onchain_data(self, symbol: str) -> Any:
        try:
            if self.onchain_client is not None:
                return await asyncio.wait_for(
                    self.onchain_client.get_exchange_flow(symbol),
                    timeout=3,
                )
        except Exception as exc:
            log.debug("On-chain fetch error for {}: {}", symbol, exc)
        return None

    async def _verify_cross_exchange(
        self, symbol: str, direction: str, entry: float
    ) -> Optional[bool]:
        try:
            return await asyncio.wait_for(
                self.exchange_mgr.verify_signal_cross_exchange(
                    symbol, direction, entry
                ),
                timeout=3,
            )
        except asyncio.TimeoutError:
            log.debug("Cross-exchange verification timed out for {}", symbol)
        except Exception as exc:
            log.debug("Cross-exchange verification error for {}: {}", symbol, exc)
        return None

    def _build_smc_summary(self, smc_result: Any) -> str:
        smc_parts = []
        if smc_result.sweeps:
            sweep = smc_result.sweeps[0]
            fmt = price_decimal_fmt(sweep.sweep_level)
            smc_parts.append(
                f"Sweep {sweep.direction.value} at {sweep.sweep_level:{fmt}}"
            )
        if smc_result.fvg:
            fvg = smc_result.fvg[0]
            fmt = price_decimal_fmt(max(fvg.gap_high, fvg.gap_low))
            smc_parts.append(f"FVG {fvg.gap_high:{fmt}}-{fvg.gap_low:{fmt}}")
        return " | ".join(smc_parts) if smc_parts else "None detected"

    async def _build_scan_context(self, symbol: str, volume_24h: float) -> Optional[ScanContext]:
        candles = self._load_candles(symbol)
        if not candles:
            return None
        # Build a cheap fingerprint: tuple of (tf, last_close) for all timeframes.
        # If candles haven't changed since last cycle, reuse cached indicators.
        try:
            _fp = tuple(
                (tf, float(cd["close"][-1]) if cd.get("close") else 0.0)
                for tf, cd in sorted(candles.items())
            )
        except Exception:
            _fp = None
        _cached = self._indicator_cache.get(symbol) if _fp is not None else None
        if _cached is not None and _cached[0] == _fp:
            indicators = _cached[1]
        else:
            indicators = await asyncio.to_thread(self._compute_indicators, candles)
            if _fp is not None:
                self._indicator_cache[symbol] = (_fp, indicators)
        ticks = self.data_store.ticks.get(symbol, [])
        # Use scalp-optimised sweep detection parameters: shorter lookback catches
        # recent S/R levels; wider tolerance catches institutional sweeps that
        # reclaim $100-200 past the level.  The full post-channel quality pipeline
        # (MTF, VWAP, KillZone, OI, CrossAsset, Spoof, VolDiv, Clustering filters
        # and confidence scoring) still runs on the detected sweeps.
        smc_result = self.smc_detector.detect(
            symbol, candles, ticks, self.order_flow_store,
            lookback=SMC_SCALP_LOOKBACK,
            tolerance_pct=SMC_SCALP_TOLERANCE_PCT,
        )
        smc_data = smc_result.as_dict()
        # Attach per-pair profile so channel evaluators can consume it via
        # smc_data.get("pair_profile") without any signature changes.
        smc_data["pair_profile"] = classify_pair_tier(symbol, volume_24h_usd=volume_24h)

        regime_tf = "5m" if "5m" in indicators else "1m"
        regime_ind = indicators.get("5m", indicators.get("1m", {}))
        regime_candles = candles.get("5m", candles.get("1m"))
        regime_result = self.regime_detector.classify(regime_ind, regime_candles, timeframe=regime_tf)
        log.debug("{} regime: {}", symbol, regime_result.regime.value)
        # Keep a rolling picture of the overall market regime using BTCUSDT as
        # the representative benchmark (feature 7 – gem adaptive thresholds).
        if "BTC" in symbol.upper():
            self._last_market_regime = regime_result.regime.value

        # Record regime history for oscillation / instability detection
        _now = time.monotonic()
        history = self._regime_history.setdefault(symbol, [])
        history.append((_now, regime_result.regime.value))
        # Prune entries older than 30 minutes
        _cutoff = _now - 30 * 60
        self._regime_history[symbol] = [(t, r) for t, r in history if t >= _cutoff]

        ind_for_predict = indicators.get("5m", indicators.get("1m", {}))
        candle_total = sum(len(cd.get("close", [])) for cd in candles.values())
        market = (
            self.pair_mgr.pairs[symbol].market
            if symbol in self.pair_mgr.pairs
            else "spot"
        )
        spread_pct, onchain_data = await asyncio.gather(
            self._get_spread_pct(symbol, market=market),
            self._fetch_onchain_data(symbol),
        )
        ai: Dict[str, Any] = {}
        pair_quality = assess_pair_quality(
            volume_24h=volume_24h,
            spread_pct=spread_pct,
            indicators=regime_ind,
            candles=regime_candles,
        )
        market_state = classify_market_state(
            regime_result=regime_result,
            indicators=regime_ind,
            candles=regime_candles,
            spread_pct=spread_pct,
        )
        # Build rich regime context for signal enrichment
        from src.vwap import compute_vwap  # noqa: PLC0415
        vwap_val = 0.0
        if regime_candles is not None:
            vwap_result = compute_vwap(
                regime_candles.get("high", []),
                regime_candles.get("low", []),
                regime_candles.get("close", []),
                regime_candles.get("volume", []),
            )
            if vwap_result is not None:
                vwap_val = vwap_result.vwap
        regime_context = self.regime_detector.build_regime_context(
            regime_result, regime_candles, regime_ind, vwap=vwap_val,
        )
        # Attach regime context so channel evaluators can access atr_percentile
        # via smc_data.get("regime_context") without any signature changes.
        smc_data["regime_context"] = regime_context

        # ── Wire funding_rate and cvd into smc_data before evaluators run ────
        # Evaluators (_evaluate_funding_extreme, _evaluate_divergence_continuation,
        # _evaluate_liquidation_reversal) depend on these keys being present.
        # Fail-open: if data is unavailable, keys are set to None so evaluators
        # can degrade gracefully rather than failing on a missing key.
        if self.order_flow_store is not None:
            _fr = self.order_flow_store.get_funding_rate(symbol)
            smc_data["funding_rate"] = _fr
            _cvd_arr = self.order_flow_store.get_cvd_history(symbol)
            smc_data["cvd"] = _cvd_arr.tolist() if len(_cvd_arr) > 0 else None
            log.debug(
                "{} smc_data: funding_rate={}, cvd_candles={}",
                symbol,
                _fr,
                len(_cvd_arr),
            )

        return ScanContext(
            candles=candles,
            indicators=indicators,
            smc_result=smc_result,
            smc_data=smc_data,
            regime_result=regime_result,
            ai=ai,
            spread_pct=spread_pct,
            ind_for_predict=ind_for_predict,
            is_ranging=regime_result.regime == MarketRegime.RANGING,
            adx_val=regime_ind.get("adx_last") or 0,
            onchain_data=onchain_data,
            candle_total=candle_total,
            pair_quality=pair_quality,
            market_state=market_state,
            regime_context=regime_context,
        )

    def _should_skip_channel(self, symbol: str, chan_name: str, ctx: ScanContext) -> bool:
        # Tier-based channel gating: Tier 2 pairs skip SCALP (REST-only, no
        # order book depth for tight scalp execution).
        pair_info = self.pair_mgr.pairs.get(symbol)
        if pair_info is not None and pair_info.tier == PairTier.TIER2 and chan_name == "360_SCALP":
            log.debug("Skipping {} {} – Tier 2 pair excluded from SCALP", symbol, chan_name)
            self._suppression_counters[f"tier2_scalp_excluded:{chan_name}"] += 1
            return True
        # Per-channel pair quality gate: the generic ctx.pair_quality uses a
        # universal 5% spread limit.  When it fails, we re-evaluate with
        # channel-specific thresholds — this allows wider-spread pairs on
        # SWING/SPOT/GEM channels while keeping SCALP at a tighter limit.
        if not ctx.pair_quality.passed:
            _regime_ind = ctx.indicators.get("5m", ctx.indicators.get("1m", {}))
            _regime_candles = ctx.candles.get("5m", ctx.candles.get("1m"))
            try:
                _vol = float(pair_info.volume_24h_usd) if pair_info is not None else 0.0
            except (TypeError, ValueError):
                _vol = 0.0
            # Only attempt the channel-specific re-check when we have valid data;
            # if volume is unavailable, fail open (don't double-penalise the pair).
            if _vol > 0.0:
                chan_quality = assess_pair_quality_for_channel(
                    volume_24h=_vol,
                    spread_pct=ctx.spread_pct,
                    indicators=_regime_ind,
                    candles=_regime_candles,
                    channel_name=chan_name,
                )
                if not chan_quality.passed:
                    log.debug(
                        "Skipping {} {} – pair quality gate failed: {}",
                        symbol,
                        chan_name,
                        chan_quality.reason,
                    )
                    _supp_reason = (
                        REASON_SPREAD_GATE if "spread" in chan_quality.reason
                        else REASON_VOLUME_GATE
                    )
                    self._suppression_counters[f"pair_quality:{chan_quality.reason}"] += 1
                    self.suppression_tracker.record(SuppressionEvent(
                        symbol=symbol,
                        channel=chan_name,
                        reason=_supp_reason,
                        regime=ctx.regime_result.regime.value,
                    ))
                    return True
                # Channel-specific re-check passed — allow through despite generic failure
                log.debug(
                    "{} {} passed channel-specific quality gate (generic failed)",
                    symbol, chan_name,
                )
            else:
                log.debug(
                    "Skipping {} {} – pair quality gate failed: {}",
                    symbol,
                    chan_name,
                    ctx.pair_quality.reason,
                )
                self._suppression_counters[f"pair_quality:{ctx.pair_quality.reason}"] += 1
                return True
        if ctx.market_state == MarketState.VOLATILE_UNSUITABLE:
            if chan_name in CHANNEL_VOLATILE_FAMILY_GOVERNED:
                # PR-3 contradiction-cleanup scope: only selected channels bypass
                # channel-level pre-skip so family/setup compatibility can decide.
                self._suppression_counters[
                    f"volatile_unsuitable:channel_preskip_bypassed:{chan_name}"
                ] += 1
            else:
                log.debug(
                    "Skipping {} {} – volatile/unsuitable market state",
                    symbol,
                    chan_name,
                )
                self._suppression_counters[f"volatile_unsuitable:{chan_name}"] += 1
                return True
        if chan_name in self.paused_channels:
            self._suppression_counters[f"paused_channel:{chan_name}"] += 1
            return True
        if self._is_in_cooldown(symbol, chan_name):
            log.debug("Cooldown active: skipping {} {}", symbol, chan_name)
            self._suppression_counters[f"cooldown:{chan_name}"] += 1
            return True
        # Per-symbol circuit breaker: suppress the symbol across all channels
        # when it has accumulated too many consecutive SL hits.
        if self.circuit_breaker is not None and self.circuit_breaker.is_symbol_tripped(symbol):
            log.debug(
                "Per-symbol circuit breaker active: skipping {} {}", symbol, chan_name
            )
            self._suppression_counters[f"circuit_breaker:{chan_name}"] += 1
            return True
        if any(
            s.symbol == symbol and s.channel == chan_name
            for s in self.router.active_signals.values()
        ):
            log.debug("Skipping {} {} – active signal already exists", symbol, chan_name)
            self._suppression_counters[f"active_signal:{chan_name}"] += 1
            return True
        if (
            chan_name == "360_SCALP"
            and ctx.is_ranging
            and ctx.adx_val < _RANGING_ADX_SUPPRESS_THRESHOLD
        ):
            log.debug(
                "Suppressing SCALP signal for {} (RANGING, ADX={:.1f})",
                symbol,
                ctx.adx_val,
            )
            self._suppression_counters[f"ranging_low_adx:{chan_name}"] += 1
            return True
        # Regime-channel compatibility matrix
        current_regime = ctx.regime_result.regime.value
        incompatible_regimes = _REGIME_CHANNEL_INCOMPATIBLE.get(chan_name, [])
        if current_regime in incompatible_regimes:
            log.debug(
                "Suppressing {} signal for {} (regime {} incompatible with channel)",
                chan_name,
                symbol,
                current_regime,
            )
            self._suppression_counters[f"regime:{current_regime}:{chan_name}"] += 1
            self.suppression_tracker.record(SuppressionEvent(
                symbol=symbol,
                channel=chan_name,
                reason=REASON_QUIET_REGIME,
                regime=current_regime,
            ))
            return True
        return False

    def _evaluate_setup(
        self,
        chan_name: str,
        sig: Any,
        ctx: ScanContext,
    ) -> SetupAssessment:
        return classify_setup(
            channel_name=chan_name,
            signal=sig,
            indicators=ctx.indicators,
            smc_data=ctx.smc_data,
            market_state=ctx.market_state,
        )

    def _evaluate_execution(
        self,
        sig: Any,
        ctx: ScanContext,
        setup: SetupAssessment,
    ) -> ExecutionAssessment:
        return execution_quality_check(
            signal=sig,
            indicators=ctx.indicators,
            smc_data=ctx.smc_data,
            setup=setup.setup_class,
            market_state=ctx.market_state,
        )

    def _evaluate_risk(
        self,
        sig: Any,
        ctx: ScanContext,
        setup: SetupAssessment,
        chan_name: str = "",
    ) -> RiskAssessment:
        return build_risk_plan(
            signal=sig,
            indicators=ctx.indicators,
            candles=ctx.candles,
            smc_data=ctx.smc_data,
            setup=setup.setup_class,
            spread_pct=ctx.spread_pct,
            channel=chan_name or sig.channel,
        )

    def _apply_risk_plan_to_signal(
        self,
        sig: Any,
        risk: RiskAssessment,
    ) -> None:
        sig.stop_loss = risk.stop_loss
        sig.tp1 = risk.tp1
        sig.tp2 = risk.tp2
        sig.tp3 = risk.tp3
        sig.invalidation_summary = risk.invalidation_summary

    @staticmethod
    def _capture_geometry(sig: Any) -> Tuple[float, float, float, Optional[float]]:
        """Snapshot mutable SL/TP geometry from a signal for diff/revert logic."""
        tp3_raw = getattr(sig, "tp3", None)
        return (
            float(getattr(sig, "stop_loss", 0.0) or 0.0),
            float(getattr(sig, "tp1", 0.0) or 0.0),
            float(getattr(sig, "tp2", 0.0) or 0.0),
            float(tp3_raw) if tp3_raw is not None else None,
        )

    @staticmethod
    def _restore_geometry(sig: Any, geometry: Tuple[float, float, float, Optional[float]]) -> None:
        """Restore a previously captured SL/TP snapshot onto *sig*."""
        sig.stop_loss, sig.tp1, sig.tp2, sig.tp3 = geometry

    @staticmethod
    def _geometry_changed(
        before: Tuple[float, float, float, Optional[float]],
        after: Tuple[float, float, float, Optional[float]],
        tol: float = 1e-8,
    ) -> bool:
        """Return True when two geometry snapshots differ beyond tolerance."""
        b_sl, b_tp1, b_tp2, b_tp3 = before
        a_sl, a_tp1, a_tp2, a_tp3 = after
        if abs(a_sl - b_sl) > tol or abs(a_tp1 - b_tp1) > tol or abs(a_tp2 - b_tp2) > tol:
            return True
        if b_tp3 is None and a_tp3 is None:
            return False
        if b_tp3 is None or a_tp3 is None:
            return True
        return abs(a_tp3 - b_tp3) > tol

    @staticmethod
    def _setup_family_for_channel(chan_name: str, setup_class_name: str) -> str:
        """Resolve setup family tag used for low-cardinality geometry telemetry."""
        if chan_name == "360_SCALP":
            return _SCALP_SETUP_TO_FAMILY.get(setup_class_name, "other")
        return "other"

    @staticmethod
    def _normalize_setup_class(setup_class: Any) -> str:
        if isinstance(setup_class, str):
            return setup_class or "UNKNOWN"
        return str(getattr(setup_class, "value", setup_class) or "UNKNOWN")

    def _path_funnel_key(self, stage: str, chan_name: str, setup_class_name: Any) -> str:
        _setup_name = self._normalize_setup_class(setup_class_name)
        _family = self._setup_family_for_channel(chan_name, _setup_name)
        return f"{stage}:{chan_name}:{_family}:{_setup_name}"

    def _increment_path_funnel(self, stage: str, chan_name: str, setup_class_name: Any) -> None:
        self._path_funnel_counters[self._path_funnel_key(stage, chan_name, setup_class_name)] += 1

    def _resolve_origin_setup_class(self, sig: Any) -> str:
        _origin_setup_raw = getattr(sig, "origin_setup_class", None)
        if _origin_setup_raw in (None, ""):
            _origin_setup_raw = getattr(sig, "setup_class", None)
        return self._normalize_setup_class(_origin_setup_raw)

    def _stamp_origin_setup_identity(self, sig: Any, chan_name: str) -> None:
        """Persist immutable origin setup identity on a signal."""
        _origin_setup_class = self._resolve_origin_setup_class(sig)
        _origin_setup_family = getattr(sig, "origin_setup_family", "") or self._setup_family_for_channel(
            chan_name, _origin_setup_class
        )
        setattr(sig, "origin_setup_class", _origin_setup_class)
        setattr(sig, "origin_setup_family", _origin_setup_family)

    @staticmethod
    def _metric_token(value: Any) -> str:
        _text = str(value or "unknown")
        _token = re.sub(r"[^A-Za-z0-9]+", "_", _text).strip("_")
        return _token or "unknown"

    @staticmethod
    def _score_band(score: float) -> str:
        """Return a low-cardinality score band token for telemetry."""
        _score = max(_SCORE_MIN, min(_SCORE_MAX, float(score)))
        if _score >= _SCORE_MAX:
            return "100"
        _lower = int(_score // 10) * 10
        _upper = _lower + 9
        return f"{_lower:02d}-{_upper:02d}"

    def _record_scoring_distribution(
        self,
        *,
        phase: str,
        chan_name: str,
        setup_family: str,
        setup_class: str,
        score: float,
        tier: str,
    ) -> None:
        """Track score/tier distribution by channel/family/path and phase."""
        _band = self._score_band(score)
        self._scoring_distribution_counters[
            f"{phase}:band:{chan_name}:{setup_family}:{setup_class}:{_band}"
        ] += 1
        self._scoring_distribution_counters[
            f"{phase}:tier:{chan_name}:{setup_family}:{setup_class}:{tier}"
        ] += 1

    def on_signal_lifecycle_outcome(self, sig: Any, outcome_label: str) -> None:
        """Record final lifecycle outcome against origin setup family/path."""
        _chan_name = getattr(sig, "channel", "") or "UNKNOWN"
        _setup_class_name = self._resolve_origin_setup_class(sig)
        _setup_family = getattr(sig, "origin_setup_family", "") or self._setup_family_for_channel(
            _chan_name, _setup_class_name
        )
        self._path_funnel_counters[
            f"lifecycle:{outcome_label}:{_chan_name}:{_setup_family}:{_setup_class_name}"
        ] += 1

    @staticmethod
    def _get_primary_timeframe(chan_name: str) -> str:
        """Return the primary timeframe interval string for a given channel name."""
        return "5m"

    @staticmethod
    def _resolve_candles(candles: Dict[str, dict], primary_tf: str) -> dict:
        """Return the best available candle dict for *primary_tf*, falling back to 5m/1m."""
        return candles.get(primary_tf) or candles.get("5m") or candles.get("1m") or {}

    @staticmethod
    def _classify_macro_trend(closes: list) -> tuple[str, float]:
        """Classify the macro trend from a close price series.

        Returns ``(trend_label, pct_change)`` where *trend_label* is one of
        ``"DUMPING"``, ``"BEARISH"``, ``"BULLISH"``, or ``"NEUTRAL"``.
        """
        first = float(closes[0])
        last = float(closes[-1])
        pct = (last - first) / first if first != 0 else 0.0
        if pct < -0.02:
            trend = "DUMPING"
        elif pct < -0.005:
            trend = "BEARISH"
        elif pct > 0.005:
            trend = "BULLISH"
        else:
            trend = "NEUTRAL"
        return trend, pct

    def _compute_base_confidence(
        self,
        symbol: str,
        volume_24h: float,
        sig: Any,
        ctx: ScanContext,
        cross_verified: Optional[bool],
        chan_name: str = "",
        funding_rate: Optional[float] = None,
        sentiment_score: float = 0.0,
        regime_key: str = "",
    ) -> Optional[float]:
        # Gate: if OI is rising against the sweep direction, block the signal
        if ctx.smc_data.get("oi_invalidated", False):
            log.debug(
                "{}: signal blocked – OI rising against {} sweep direction",
                symbol, sig.direction.value,
            )
            return None

        has_sweep = bool(ctx.smc_data["sweeps"])
        has_mss = ctx.smc_data["mss"] is not None
        has_fvg = bool(ctx.smc_data["fvg"])

        # Wire continuation sweep detection for SHORT in TRENDING_DOWN (item 14)
        # A bearish continuation sweep adds to SMC conviction for trend-following entries.
        if (
            sig.direction.value == "SHORT"
            and regime_key == "TRENDING_DOWN"
            and not has_sweep
        ):
            try:
                from src.smc import detect_continuation_sweep
                _primary_tf = self._get_primary_timeframe(chan_name)
                _cont_candles = self._resolve_candles(ctx.candles, _primary_tf)
                _cont_sweep = detect_continuation_sweep(_cont_candles, "SHORT", lookback=10)
                if _cont_sweep is not None:
                    has_sweep = True  # Count continuation sweep as sweep evidence
            except Exception:
                pass  # Fail open

        ema_aligned = (
            ctx.ind_for_predict.get("ema9_last") is not None
            and ctx.ind_for_predict.get("ema21_last") is not None
            and (
                (ctx.ind_for_predict["ema9_last"] > ctx.ind_for_predict["ema21_last"])
                if sig.direction.value == "LONG"
                else (ctx.ind_for_predict["ema9_last"] < ctx.ind_for_predict["ema21_last"])
            )
        )
        adx_ok = (ctx.ind_for_predict.get("adx_last") or 0) >= 20
        mom_positive = (
            (ctx.ind_for_predict.get("momentum_last") or 0) > 0
            if sig.direction.value == "LONG"
            else (ctx.ind_for_predict.get("momentum_last") or 0) < 0
        )

        # Compute sweep depth percentage for gradient SMC scoring
        sweep_depth_pct = 0.0
        if ctx.smc_data["sweeps"]:
            sweep = ctx.smc_data["sweeps"][0]
            if hasattr(sweep, "sweep_level") and hasattr(sweep, "close_price"):
                ref_price = sweep.close_price if sweep.close_price > 0 else max(sig.entry, 1e-8)
                sweep_depth_pct = abs(sweep.sweep_level - sweep.close_price) / ref_price * 100.0

        # Compute FVG size relative to ATR for gradient SMC scoring
        fvg_atr_ratio = 0.0
        if ctx.smc_data["fvg"]:
            fvg = ctx.smc_data["fvg"][0]
            if hasattr(fvg, "gap_high") and hasattr(fvg, "gap_low"):
                fvg_size = abs(fvg.gap_high - fvg.gap_low)
                atr_val = ctx.ind_for_predict.get("atr_last")
                if atr_val and atr_val > 0:
                    fvg_atr_ratio = fvg_size / atr_val

        # Order flow score: OI trend + liquidations + CVD divergence
        of_score = 0.0
        if self.order_flow_store is not None:
            oi_trend = self.order_flow_store.get_oi_trend(symbol)
            liq_vol = self.order_flow_store.get_recent_liq_volume_usd(symbol)
            cvd_div = ctx.smc_data.get("cvd_divergence")
            of_score = score_order_flow(
                oi_trend=oi_trend.value,
                liq_vol_usd=liq_vol,
                cvd_divergence=cvd_div,
                signal_direction=sig.direction.value,
                funding_rate=funding_rate,
            )

        cinp = ConfidenceInput(
            smc_score=score_smc(
                has_sweep, has_mss, has_fvg,
                sweep_depth_pct=sweep_depth_pct,
                fvg_atr_ratio=fvg_atr_ratio,
            ),
            trend_score=score_trend(
                ema_aligned, adx_ok, mom_positive,
                adx_value=ctx.ind_for_predict.get("adx_last") or 0.0,
                momentum_strength=ctx.ind_for_predict.get("momentum_last") or 0.0,
                macd_histogram=ctx.ind_for_predict.get("macd_histogram_last"),
                macd_histogram_prev=ctx.ind_for_predict.get("macd_histogram_prev"),
                signal_direction=sig.direction.value,
            ),
            liquidity_score=score_liquidity(volume_24h, channel=chan_name),
            spread_score=score_spread(ctx.spread_pct),
            data_sufficiency=score_data_sufficiency(ctx.candle_total),
            multi_exchange=score_multi_exchange(verified=cross_verified),
            onchain_score=score_onchain(ctx.onchain_data),
            order_flow_score=of_score,
            sentiment_score=sentiment_score,
            has_enough_history=self.pair_mgr.has_enough_history(symbol),
            opposing_position_open=any(
                s.symbol == symbol and s.direction.value != sig.direction.value
                for s in self.router.active_signals.values()
            ),
        )
        result = compute_confidence(cinp, channel=chan_name)
        if result.blocked:
            return None
        return result.total

    async def _apply_predictive_adjustments(
        self,
        symbol: str,
        sig: Any,
        ctx: ScanContext,
        setup: SetupAssessment,
        chan_name: str,
    ) -> None:
        _setup_class_name = setup.setup_class.value
        _setup_family = self._setup_family_for_channel(chan_name, _setup_class_name)
        _pre_geom = self._capture_geometry(sig)
        _baseline_sl_distance = abs(float(getattr(sig, "entry", 0.0) or 0.0) - _pre_geom[0])
        try:
            prediction = await self.predictive.predict(
                symbol, ctx.candles, ctx.ind_for_predict
            )
            self.predictive.adjust_tp_sl(sig, prediction)
            self.predictive.update_confidence(sig, prediction)
        except Exception as exc:
            log.debug("Predictive AI error for {}: {}", symbol, exc)
            self._suppression_counters[
                f"predictive_revalidation_bypassed:{chan_name}:predictive_error"
            ] += 1
            self._suppression_counters[
                f"geometry_preserved_final:{chan_name}:{_setup_family}"
            ] += 1
            self._increment_path_funnel("geometry:final_live:preserved", chan_name, _setup_class_name)
            return

        _post_geom = self._capture_geometry(sig)
        if not self._geometry_changed(_pre_geom, _post_geom):
            self._suppression_counters[
                f"predictive_revalidation_bypassed:{chan_name}:unchanged"
            ] += 1
            self._suppression_counters[
                f"geometry_preserved_final:{chan_name}:{_setup_family}"
            ] += 1
            self._increment_path_funnel("geometry:final_live:preserved", chan_name, _setup_class_name)
            return

        self._suppression_counters[
            f"predictive_revalidation_triggered:{chan_name}:{_setup_family}"
        ] += 1
        valid, reason = validate_geometry_against_policy(
            signal=sig,
            setup=setup.setup_class,
            channel=chan_name,
            max_sl_distance=_baseline_sl_distance,
        )
        if valid:
            self._suppression_counters[
                f"predictive_revalidation_passed:{chan_name}:{_setup_family}"
            ] += 1
            self._suppression_counters[
                f"geometry_changed_final:{chan_name}:{_setup_family}"
            ] += 1
            self._increment_path_funnel("geometry:final_live:changed", chan_name, _setup_class_name)
            return

        self._restore_geometry(sig, _pre_geom)
        self._suppression_counters[
            f"predictive_revalidation_rejected:{chan_name}:{_setup_family}"
        ] += 1
        self._suppression_counters[
            f"geometry_rejected_final:{chan_name}:{_setup_family}:{reason}"
        ] += 1
        self._suppression_counters[
            f"geometry_preserved_final:{chan_name}:{_setup_family}"
        ] += 1
        _reason_token = self._metric_token(reason)
        self._increment_path_funnel("geometry:final_live:rejected", chan_name, _setup_class_name)
        self._increment_path_funnel(
            f"geometry:final_live:rejected_reason:{_reason_token}",
            chan_name,
            _setup_class_name,
        )
        log.warning(
            "Predictive geometry rejected for {} {} ({}): reverted to validated plan",
            symbol,
            chan_name,
            reason,
        )

    @staticmethod
    def _clamp_confidence(value: float) -> float:
        return max(0.0, min(100.0, round(value, 2)))

    def _populate_signal_context(self, sig: Any, volume_24h: float, ctx: ScanContext) -> None:
        sig.market_phase = ctx.market_state.value
        if ctx.regime_context is not None:
            rc = ctx.regime_context
            try:
                sig.market_phase = (
                    f"{rc.label} | ATR%ile={float(rc.atr_percentile):.0f} | "
                    f"Vol={rc.volume_profile}"
                )
                sig.regime_context = (
                    f"ADXslope={float(rc.adx_slope):.2f} strengthen={rc.is_regime_strengthening}"
                )
            except (TypeError, ValueError):
                pass  # Keep market_state.value when context is not a real RegimeContext
        liq_parts = []
        if ctx.smc_result.sweeps:
            sweep = ctx.smc_result.sweeps[0]
            fmt = price_decimal_fmt(sweep.sweep_level)
            liq_parts.append(
                f"Sweep {sweep.direction.value} at {sweep.sweep_level:{fmt}}"
            )
        if ctx.smc_result.fvg:
            fvg = ctx.smc_result.fvg[0]
            fmt = price_decimal_fmt(max(fvg.gap_high, fvg.gap_low))
            liq_parts.append(f"FVG {fvg.gap_high:{fmt}}-{fvg.gap_low:{fmt}}")
        if liq_parts:
            sig.liquidity_info = " | ".join(liq_parts)
        sig.spread_pct = ctx.spread_pct
        sig.volume_24h_usd = volume_24h
        sig.pair_quality_score = ctx.pair_quality.score
        sig.pair_quality_label = ctx.pair_quality.label
        # How long (minutes) the setup remains actionable — sourced from config.
        # Only apply the channel default when the evaluator has not already set
        # an explicit value (valid_for_minutes == 0 is the "not set" sentinel).
        if sig.valid_for_minutes == 0:
            sig.valid_for_minutes = SIGNAL_VALID_FOR_MINUTES.get(sig.channel, 15)

    @staticmethod
    def _has_higher_timeframe_alignment(sig: Any, indicators: Dict[str, Dict[str, Any]]) -> bool:
        for tf in ("15m", "1h", "4h"):
            ind = indicators.get(tf, {})
            ema9 = ind.get("ema9_last")
            ema21 = ind.get("ema21_last")
            if ema9 is None or ema21 is None:
                continue
            if sig.direction.value == "LONG" and ema9 < ema21:
                return False
            if sig.direction.value == "SHORT" and ema9 > ema21:
                return False
        return True

    async def _enqueue_signal(self, sig: Any) -> bool:
        self._stamp_origin_setup_identity(sig, getattr(sig, "channel", "") or "UNKNOWN")
        return await self.signal_queue.put(sig)

    async def _prepare_signal(
        self,
        symbol: str,
        volume_24h: float,
        chan: Any,
        ctx: ScanContext,
        _preseed_signal: Optional[Any] = None,
        _funnel_meta: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[Any], Optional[bool]]:
        t0_signal = time.monotonic()
        soft_penalty: float = 0.0  # Accumulated confidence deduction from soft gates
        _fired_gates: list = []
        chan_name = chan.config.name

        def _reject(stage: str, cross: Optional[bool]) -> Tuple[None, Optional[bool]]:
            if _funnel_meta is not None:
                _funnel_meta["reject_stage"] = stage
            return None, cross

        # ── Failed-detection cooldown ──────────────────────────────────────────
        # If this symbol+channel has failed the confidence gate too many times
        # in a row recently, skip re-evaluation until the cooldown expires.
        _fail_key = (symbol, chan_name)
        _fail_entry = self._conf_fail_tracker.get(_fail_key)
        if _fail_entry is not None:
            _fail_count, _suppressed_until = _fail_entry
            if _fail_count >= _CONF_FAIL_MAX_CONSECUTIVE and time.monotonic() < _suppressed_until:
                return _reject("gated", False)  # Silently skip — cooldown active
        # ── End failed-detection cooldown check ───────────────────────────────

        if _preseed_signal is not None:
            # Signal was already evaluated outside (e.g. ScalpChannel multi-signal path);
            # skip the evaluate() call and run the gate chain on the pre-built signal.
            sig = _preseed_signal
        else:
            try:
                sig = chan.evaluate(
                    symbol=symbol,
                    candles=ctx.candles,
                    indicators=ctx.indicators,
                    smc_data=ctx.smc_data,
                    spread_pct=ctx.spread_pct,
                    volume_24h_usd=volume_24h,
                    regime=ctx.regime_result.regime.value,
                )
            except Exception as exc:
                log.debug("Channel {} eval error for {}: {}", chan_name, symbol, exc)
                return _reject("gated", None)
            if sig is None:
                return _reject("gated", None)

        # Record wall-clock time of signal detection for latency tracking.
        sig.detected_at = time.time()

        setup = self._evaluate_setup(chan_name, sig, ctx)
        _setup_class_name = setup.setup_class.value
        _setup_family = self._setup_family_for_channel(chan_name, _setup_class_name)
        if not setup.channel_compatible or not setup.regime_compatible:
            if (
                not setup.regime_compatible
                and ctx.market_state == MarketState.VOLATILE_UNSUITABLE
                and chan_name in CHANNEL_VOLATILE_FAMILY_GOVERNED
            ):
                self._suppression_counters[f"volatile_unsuitable:family_block:{chan_name}"] += 1
            log.debug("Rejected {} {} setup: {}", symbol, chan_name, setup.reason)
            return _reject("gated", None)

        execution = self._evaluate_execution(sig, ctx, setup)
        if not execution.passed:
            log.debug("Rejected {} {} execution: {}", symbol, chan_name, execution.reason)
            return _reject("gated", None)

        # ── Filter 1: MTF Confluence Gate ──────────────────────────────────
        # Resolve the regime key early so regime-specific MTF config can
        # adjust the min_score and per-TF weight multipliers below.
        # (The same key is reused later for the regime penalty multiplier.)
        _regime_name = getattr(ctx.regime_result, "regime", None)
        if _regime_name is None:
            _regime_key = ""
        elif hasattr(_regime_name, "value"):
            _regime_key = _regime_name.value
        else:
            _regime_key = str(_regime_name)

        # Look up this channel's gate profile and penalty weights.
        # Unknown channels default to an empty profile (all gates on via .get(key, True))
        # and empty weights (gate-specific defaults apply via .get(key, default)).
        _gate_profile = _CHANNEL_GATE_PROFILE.get(chan_name, {})
        _penalty_weights = _CHANNEL_PENALTY_WEIGHTS.get(chan_name, {})
        if _gate_profile.get("mtf", True):
            # Base MTF min_score: relaxed for SCALP (range-fade setups need less confluence)
            _base_mtf_min_score = 0.55 if chan_name == "360_SCALP" else 0.5
            # Override with regime-specific min_score when configured
            _mtf_cfg = _MTF_REGIME_CONFIG.get(_regime_key, {})
            _mtf_min_score = _mtf_cfg.get("min_score", _base_mtf_min_score)
            # Relax MTF min_score for SHORT signals in TRENDING_DOWN regime:
            # lower timeframes are already aligned by definition in a downtrend.
            if _regime_key == "TRENDING_DOWN" and sig.direction.value == "SHORT":
                _mtf_min_score = min(_mtf_min_score, MTF_MIN_SCORE_TRENDING_SHORT)
            _generic_mtf_min_score = _mtf_min_score

            if chan_name == "360_SCALP":
                _family_policy = _SCALP_MTF_POLICY_BY_FAMILY.get(_setup_family, {})
                _family_mtf_cap = _family_policy.get("min_score_cap")
                # Track only effective relaxations (cap is tighter/equal => no behavior change).
                if _family_mtf_cap is not None and _family_mtf_cap < _mtf_min_score:
                    _mtf_min_score = _family_mtf_cap
                    self._suppression_counters[
                        f"mtf_policy_relaxed:360_SCALP:{_setup_family}"
                    ] += 1
            # Build TF weight overrides from the regime config
            _higher_tfs = {"4h", "1d"}
            _lower_tfs = {"1m", "5m", "15m"}
            _tf_weight_overrides: Dict[str, float] = {}
            if _mtf_cfg:
                _hw = _mtf_cfg.get("higher_tf_weight", 1.0)
                _lw = _mtf_cfg.get("lower_tf_weight", 1.0)
                for _tf in _higher_tfs:
                    _tf_weight_overrides[_tf] = _MTF_TF_WEIGHTS.get(_tf, 1.0) * _hw
                for _tf in _lower_tfs:
                    _tf_weight_overrides[_tf] = _MTF_TF_WEIGHTS.get(_tf, 1.0) * _lw
            mtf_data: Dict[str, Dict[str, float]] = {}
            for tf_label, ind in ctx.indicators.items():
                ema_fast = ind.get("ema9_last")
                ema_slow = ind.get("ema21_last")
                cd = ctx.candles.get(tf_label, {})
                closes = cd.get("close", [])
                if ema_fast is not None and ema_slow is not None and len(closes) > 0:
                    mtf_data[tf_label] = {
                        "ema_fast": float(ema_fast),
                        "ema_slow": float(ema_slow),
                        "close": float(closes[-1]),
                    }
            mtf_allowed, mtf_reason = check_mtf_gate(
                sig.direction.value,
                mtf_data,
                min_score=_mtf_min_score,
                tf_weight_overrides=_tf_weight_overrides or None,
            )
            if not mtf_allowed:
                log.debug("MTF gate blocked {} {}: {}", symbol, chan_name, mtf_reason)
                self._suppression_counters[f"mtf_gate:{chan_name}"] += 1
                if chan_name == "360_SCALP":
                    self._suppression_counters[f"mtf_gate_family:360_SCALP:{_setup_family}"] += 1
                    self._suppression_counters[f"mtf_gate_setup:360_SCALP:{_setup_class_name}"] += 1
                self.suppression_tracker.record(SuppressionEvent(
                    symbol=symbol,
                    channel=chan_name,
                    reason="mtf_gate",
                    regime=_regime_key,
                    would_be_confidence=sig.confidence,
                ))
                return _reject("gated", None)
            if chan_name == "360_SCALP" and _mtf_min_score < _generic_mtf_min_score:
                _generic_allowed, _ = check_mtf_gate(
                    sig.direction.value,
                    mtf_data,
                    min_score=_generic_mtf_min_score,
                    tf_weight_overrides=_tf_weight_overrides or None,
                )
                if not _generic_allowed:
                    # Survival-delta telemetry only: this counts candidates
                    # preserved by family-aware PR-1 threshold policy versus
                    # generic MTF threshold. It is not quality proof by itself.
                    self._suppression_counters[f"mtf_policy_saved:360_SCALP:{_setup_family}"] += 1

        # Resolve regime penalty multiplier for all soft gates below.
        # Scalp channels in QUIET regime use a higher multiplier to ensure
        # only top-tier mean-reversion setups pass the quality bar.
        if _regime_key == "QUIET" and chan_name.startswith("360_SCALP"):
            regime_mult = _SCALP_QUIET_REGIME_PENALTY
        else:
            regime_mult = _REGIME_PENALTY_MULTIPLIER.get(_regime_key, 1.0)

        # ── Filter 2: VWAP Extension Rejection ─────────────────────────────
        if _gate_profile.get("vwap", True):
            try:
                _primary_tf = self._get_primary_timeframe(chan_name)
                _cd = self._resolve_candles(ctx.candles, _primary_tf)
                _vwap_result = compute_vwap(
                    _cd.get("high", []),
                    _cd.get("low", []),
                    _cd.get("close", []),
                    _cd.get("volume", []),
                )
                vwap_allowed, vwap_reason = check_vwap_extension(
                    sig.direction.value, sig.entry, _vwap_result
                )
                if not vwap_allowed:
                    _base = _penalty_weights.get("vwap", 12.0)
                    _scaled = round(_base * regime_mult, 1)
                    soft_penalty += _scaled
                    _fired_gates.append("VWAP")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, vwap_reason,
                    )
            except Exception as _vwap_exc:
                log.debug("VWAP gate error for {} {} (fail open): {}", symbol, chan_name, _vwap_exc)

        # ── Filter 3: Kill Zone / Session Filter ────────────────────────────
        if _gate_profile.get("kill_zone", True):
            # Relaxed minimum multiplier for scalp signals (scalps can trade lower-liquidity windows)
            _kz_min_mult = 0.40 if chan_name == "360_SCALP" else 0.50
            kz_allowed, kz_reason = check_kill_zone_gate(minimum_multiplier=_kz_min_mult)
            if not kz_allowed:
                _base = _penalty_weights.get("kill_zone", 10.0)
                _scaled = round(_base * regime_mult, 1)
                soft_penalty += _scaled
                _fired_gates.append("KZ")
                log.debug(
                    "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                    symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, kz_reason,
                )

        # ── Filter 4: OI + Funding Rate Gate ────────────────────────────────
        _funding_rate: Optional[float] = None
        if _gate_profile.get("oi", True) and self.order_flow_store is not None:
            try:
                _oi_tf = self._get_primary_timeframe(chan_name)
                _oi_cd = self._resolve_candles(ctx.candles, _oi_tf)
                _prices = _oi_cd.get("close", [])
                _oi_snaps = list(getattr(self.order_flow_store, "_oi", {}).get(symbol, []))
                _oi_values = [s.open_interest for s in _oi_snaps]
                if _prices and _oi_values:
                    oi_analysis = analyse_oi(_prices, _oi_values)
                    _fr = oi_analysis.latest_funding_rate
                    if isinstance(_fr, (int, float)):
                        _funding_rate = float(_fr)
                    oi_allowed, oi_reason = check_oi_gate(sig.direction.value, oi_analysis)
                    if not oi_allowed:
                        _base = _penalty_weights.get("oi", 15.0)
                        _scaled = round(_base * regime_mult, 1)
                        soft_penalty += _scaled
                        _fired_gates.append("OI")
                        log.debug(
                            "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                            symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, oi_reason,
                        )
            except Exception as _oi_exc:
                log.debug("OI gate error for {} {} (fail open): {}", symbol, chan_name, _oi_exc)

        # ── Funding Rate Gate ────────────────────────────────────────────────
        # Soft penalty/boost only — never hard blocks a signal alone.
        # Extreme funding in the direction of the signal = expensive / crowded.
        # Extreme funding opposite the signal = confirmation of signal thesis.
        if _funding_rate is not None:
            try:
                _dir_upper = sig.direction.value.upper()
                _fr = _funding_rate
                _fr_flag: Optional[str] = None
                _fr_adj: float = 0.0
                if _dir_upper == "LONG":
                    if _fr > FUNDING_RATE_BOOST_THRESHOLD:
                        # Extreme short crowding confirms LONG
                        _fr_adj = FUNDING_RATE_BOOST
                        _fr_flag = f"FUNDING_BOOST:{_fr_adj:+.0f}"
                    elif _fr > FUNDING_RATE_PENALTY_THRESHOLD:
                        # Moderate long crowding — longs expensive
                        _fr_adj = FUNDING_RATE_PENALTY
                        _fr_flag = f"FUNDING_PENALTY:{_fr_adj:+.0f}"
                elif _dir_upper == "SHORT":
                    if _fr < -FUNDING_RATE_BOOST_THRESHOLD:
                        # Extreme long crowding confirms SHORT
                        _fr_adj = FUNDING_RATE_BOOST
                        _fr_flag = f"FUNDING_BOOST:{_fr_adj:+.0f}"
                    elif _fr < -FUNDING_RATE_PENALTY_THRESHOLD:
                        # Moderate short crowding — shorts expensive
                        _fr_adj = FUNDING_RATE_PENALTY
                        _fr_flag = f"FUNDING_PENALTY:{_fr_adj:+.0f}"
                if _fr_adj != 0.0:
                    sig.confidence += _fr_adj
                    if _fr_flag:
                        sig.soft_gate_flags = (
                            sig.soft_gate_flags + f",{_fr_flag}"
                        ).lstrip(",")
                    log.debug(
                        "Funding gate {} {} fr={:.4f} {:+.1f}",
                        symbol, chan_name, _fr, _fr_adj,
                    )
            except Exception as _fr_exc:
                log.debug("Funding rate gate error for {} {} (fail open): {}", symbol, chan_name, _fr_exc)


        if _gate_profile.get("cross_asset", True) and symbol not in ("BTCUSDT", "ETHUSDT"):
            try:
                _asset_states: List[AssetState] = []
                _btc_corr: Optional[float] = self._btc_correlation_cache.get(symbol)
                for _major in ("BTCUSDT", "ETHUSDT"):
                    _major_cd = self.data_store.get_candles(_major, "5m") or {}
                    _major_closes = _major_cd.get("close", [])
                    if len(_major_closes) >= 2:
                        _trend, _pct = self._classify_macro_trend(_major_closes)
                        _asset_states.append(
                            AssetState(symbol=_major, trend=_trend, price_change_pct=_pct)
                        )
                if _asset_states:
                    ca_allowed, ca_reason, ca_conf_adj = check_cross_asset_gate(
                        sig.direction.value, symbol, _asset_states,
                        btc_correlation=_btc_corr,
                    )
                    if not ca_allowed:
                        log.debug(
                            "Cross-asset gate blocked {} {}: {}", symbol, chan_name, ca_reason
                        )
                        return _reject("gated", None)
                    if ca_conf_adj != 0.0:
                        sig.confidence += ca_conf_adj
                        if ca_reason:
                            sig.soft_gate_flags = (
                                sig.soft_gate_flags + f",CROSS_ASSET:{ca_conf_adj:+.0f}"
                            ).lstrip(",")
                        log.debug(
                            "Cross-asset gate {} {} {:+.1f}: {}",
                            symbol, chan_name, ca_conf_adj, ca_reason,
                        )
            except Exception as _ca_exc:
                log.debug(
                    "Cross-asset gate error for {} {} (fail open): {}", symbol, chan_name, _ca_exc
                )

        # ── Filter 6: Spoofing / Layering Detection ───────────────────────
        if _gate_profile.get("spoof", True):
            try:
                spoof_allowed, spoof_reason = check_spoof_gate(
                    sig.direction.value, None, sig.entry
                )
                if not spoof_allowed:
                    _base = _penalty_weights.get("spoof", 10.0)
                    _scaled = round(_base * regime_mult, 1)
                    soft_penalty += _scaled
                    _fired_gates.append("SPOOF")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, spoof_reason,
                    )
            except Exception as _spoof_exc:
                log.debug(
                    "Spoof gate error for {} {} (fail open): {}", symbol, chan_name, _spoof_exc
                )

        # ── Filter 7: Cross-Timeframe Volume Divergence ───────────────────
        if _gate_profile.get("volume_div", True):
            try:
                _vol_primary_tf = self._get_primary_timeframe(chan_name)
                # Relaxed spike threshold for scalp signals (volume spikes ARE valid for scalps)
                _vol_spike_thresh = 2.5 if chan_name == "360_SCALP" else 2.0
                vol_div_allowed, vol_div_reason = check_volume_divergence_gate(
                    sig.direction.value, ctx.candles, _vol_primary_tf,
                    spike_threshold=_vol_spike_thresh,
                    regime=_regime_key if _regime_key else None,
                )
                if not vol_div_allowed:
                    _base = _penalty_weights.get("volume_div", 10.0)
                    _scaled = round(_base * regime_mult, 1)
                    soft_penalty += _scaled
                    _fired_gates.append("VOL_DIV")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, vol_div_reason,
                    )
            except Exception as _vol_div_exc:
                log.debug(
                    "Volume divergence gate error for {} {} (fail open): {}",
                    symbol, chan_name, _vol_div_exc,
                )

        # ── Filter 8: Signal Clustering Suppression ───────────────────────
        if _gate_profile.get("cluster", True):
            cluster_allowed, cluster_reason = self.cluster_suppressor.check_cluster_gate(
                symbol, sig.direction.value
            )
            if not cluster_allowed:
                _base = _penalty_weights.get("cluster", 8.0)
                _scaled = round(_base * regime_mult, 1)
                soft_penalty += _scaled
                _fired_gates.append("CLUSTER")
                log.debug(
                    "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                    symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, cluster_reason,
                )

        risk = self._evaluate_risk(sig, ctx, setup, chan_name=chan_name)
        if not risk.passed:
            log.debug("Rejected {} {} risk: {}", symbol, chan_name, risk.reason)
            self._suppression_counters[
                f"geometry_rejected_risk_plan:{chan_name}:{_setup_family}"
            ] += 1
            _reason_token = self._metric_token(risk.reason)
            self._increment_path_funnel("geometry:risk_plan:rejected", chan_name, _setup_class_name)
            self._increment_path_funnel(
                f"geometry:risk_plan:rejected_reason:{_reason_token}",
                chan_name,
                _setup_class_name,
            )
            return _reject("gated", None)
        _eval_geom = self._capture_geometry(sig)
        _risk_geom = (
            float(risk.stop_loss),
            float(risk.tp1),
            float(risk.tp2),
            float(risk.tp3) if risk.tp3 is not None else None,
        )
        if self._geometry_changed(_eval_geom, _risk_geom):
            self._suppression_counters[
                f"geometry_changed_risk_plan:{chan_name}:{_setup_family}"
            ] += 1
            self._increment_path_funnel("geometry:risk_plan:changed", chan_name, _setup_class_name)
            _entry = float(getattr(sig, "entry", 0.0) or 0.0)
            _eval_sl = _eval_geom[0]
            if _entry > 0 and _eval_sl > 0:
                if is_sl_distance_capped(
                    entry=_entry,
                    original_stop_loss=_eval_sl,
                    final_stop_loss=_risk_geom[0],
                    channel=chan_name,
                ):
                    self._suppression_counters[
                        f"geometry_capped_risk_plan:{chan_name}:{_setup_family}"
                    ] += 1
                    self._increment_path_funnel("geometry:risk_plan:capped", chan_name, _setup_class_name)
        else:
            self._suppression_counters[
                f"geometry_preserved_risk_plan:{chan_name}:{_setup_family}"
            ] += 1
            self._increment_path_funnel("geometry:risk_plan:preserved", chan_name, _setup_class_name)
        self._apply_risk_plan_to_signal(sig, risk)

        # ── Correlated position exposure cap ───────────────────────────────
        # Block new scalp signals when too many same-direction active signals
        # exist already, to limit correlated BTC-driven stop-out risk.
        if chan_name in _SCALP_CHANNELS:
            same_dir_count = sum(
                1
                for s in self.router.active_signals.values()
                if s.direction == sig.direction and s.channel in _SCALP_CHANNELS
            )
            if same_dir_count >= MAX_CORRELATED_SCALP_SIGNALS:
                log.info(
                    "Correlated exposure cap reached for {} {} (direction={}, active={}): "
                    "blocking signal",
                    symbol, chan_name, sig.direction.value, same_dir_count,
                )
                return _reject("gated", None)

        cross_verified = await self._verify_cross_exchange(
            symbol, sig.direction.value, sig.entry
        ) if chan_name not in _SCALP_CHANNELS else None

        # Fetch AI sentiment only for channels where latency is acceptable.
        # SCALP channels receive 0.0 (neutral) so the hot path has zero extra latency.
        sentiment_score = 0.0

        legacy_confidence = self._compute_base_confidence(
            symbol,
            volume_24h,
            sig,
            ctx,
            cross_verified,
            chan_name=chan_name,
            funding_rate=_funding_rate,
            sentiment_score=sentiment_score,
            regime_key=_regime_key,
        )
        if legacy_confidence is None:
            return _reject("gated", cross_verified)
        sig.confidence = legacy_confidence
        await self._apply_predictive_adjustments(
            symbol,
            sig,
            ctx,
            setup=setup,
            chan_name=chan_name,
        )
        setup_score = score_signal_components(
            pair_quality=ctx.pair_quality,
            setup=setup,
            execution=execution,
            risk=risk,
            legacy_confidence=sig.confidence,
            cross_verified=cross_verified,
        )
        sig.setup_class = setup.setup_class.value
        # PR-01: preserve evaluator-authored analyst_reason; only apply the generic
        # scored thesis when the evaluator did not set a richer path-specific reason.
        if not getattr(sig, "analyst_reason", ""):
            sig.analyst_reason = setup.thesis
        sig.execution_note = execution.execution_note
        sig.entry_zone = execution.entry_zone
        sig.component_scores = setup_score.components
        sig.quality_tier = setup_score.quality_tier.value
        sig.pre_ai_confidence = setup_score.total
        sig.confidence = setup_score.total
        # Apply ML feedback adjustment based on historical outcomes for this
        # channel / setup combination.
        fb_adj = self.feedback_loop.get_confidence_adjustment(
            setup_score.components, chan_name, setup.setup_class.value
        )
        if fb_adj != 0.0:
            sig.confidence += fb_adj
            log.debug(
                "Feedback adjustment for {} {} {}: {:+.1f} → {:.1f}",
                symbol, chan_name, setup.setup_class.value, fb_adj, sig.confidence,
            )

        # Chart pattern bonus: detect confirming patterns from primary-TF candles
        primary_tf = self._get_primary_timeframe(chan_name)
        primary_candles = self._resolve_candles(ctx.candles, primary_tf)
        if primary_candles:
            try:
                patterns = detect_patterns(primary_candles)
                pat_bonus = pattern_confidence_bonus(patterns, sig.direction.value)
                if pat_bonus != 0.0:
                    sig.confidence += pat_bonus
                    log.debug(
                        "Chart pattern bonus {} {}: {:+.2f} (patterns={})",
                        symbol, chan_name, pat_bonus,
                        [p["pattern"] for p in patterns],
                    )
                # Record confirming pattern names for downstream consumers.
                confirming_names = []
                for _p in patterns:
                    _pname = _p.get("pattern", "")
                    if sig.direction.value == "LONG":
                        if _pname in _CHART_BULLISH_PATTERNS:
                            confirming_names.append(_pname)
                        elif _pname == "BB_SQUEEZE" and _p.get("expansion_direction") == "UP":
                            confirming_names.append(_pname)
                    else:
                        if _pname in _CHART_BEARISH_PATTERNS:
                            confirming_names.append(_pname)
                        elif _pname == "BB_SQUEEZE" and _p.get("expansion_direction") == "DOWN":
                            confirming_names.append(_pname)
                if confirming_names:
                    sig.chart_pattern_names = ",".join(confirming_names)
            except Exception as _exc:
                log.debug("Chart pattern detection error for {}: {}", symbol, _exc)

            # PR_05: candlestick pattern engine — confidence modifier (not hard gate)
            try:
                _open_arr = primary_candles.get("open", [])
                _high_arr = primary_candles.get("high", [])
                _low_arr = primary_candles.get("low", [])
                _close_arr = primary_candles.get("close", [])
                _vol_arr = primary_candles.get("volume", [])
                if len(_close_arr) >= 3 and len(_open_arr) >= 3:
                    _cp_results = detect_all_patterns(
                        np.asarray(_open_arr),
                        np.asarray(_high_arr),
                        np.asarray(_low_arr),
                        np.asarray(_close_arr),
                        np.asarray(_vol_arr) if _vol_arr else None,
                    )
                    # Store in smc_data for downstream consumers
                    ctx.smc_data["chart_patterns"] = _cp_results
                    # Filter to direction-aligned patterns only
                    _aligned = [
                        p for p in _cp_results
                        if p.direction == sig.direction.value or p.direction == "NEUTRAL"
                    ]
                    if _aligned:
                        _cp_bonus = sum(p.confidence_bonus for p in _aligned)
                        sig.confidence = max(0.0, min(100.0, sig.confidence + _cp_bonus))
                        _cp_names = ", ".join(p.name for p in _aligned)
                        # Append to chart_pattern_names (may already have legacy pattern names)
                        if sig.chart_pattern_names:
                            sig.chart_pattern_names = sig.chart_pattern_names + ", " + _cp_names
                        else:
                            sig.chart_pattern_names = _cp_names
                        log.debug(
                            "Candlestick pattern bonus {} {}: {:+.2f} ({})",
                            symbol, chan_name, _cp_bonus, _cp_names,
                        )
            except Exception as _exc:
                log.debug("Candlestick pattern detection error for {}: {}", symbol, _exc)

        # This augments the hard MTF gate above with a continuous confidence signal.
        try:
            _mtf_conf_data: Dict[str, Dict[str, float]] = {}
            for _tf in ("5m", "15m", "1h", "4h"):
                _ind = ctx.indicators.get(_tf, {})
                _ema_fast = _ind.get("ema9_last")
                _ema_slow = _ind.get("ema21_last")
                _cd = ctx.candles.get(_tf, {})
                _closes = _cd.get("close", [])
                if _ema_fast is not None and _ema_slow is not None and _closes:
                    _mtf_conf_data[_tf] = {
                        "ema_fast": float(_ema_fast),
                        "ema_slow": float(_ema_slow),
                        "close": float(_closes[-1]),
                    }
            if _mtf_conf_data:
                _mtf_result = compute_mtf_confluence(sig.direction.value, _mtf_conf_data)
                sig.mtf_score = _mtf_result.score
                if _mtf_result.is_strong:
                    sig.confidence += 3.0
                    log.debug(
                        "MTF strong-confluence boost {} {}: +3.0 (score={:.2f})",
                        symbol, chan_name, _mtf_result.score,
                    )
                elif not _mtf_result.is_aligned:
                    if MTF_HARD_BLOCK:
                        log.info(
                            "Signal blocked by MTF hard gate: {} {} (score={:.2f})",
                            symbol, chan_name, _mtf_result.score,
                        )
                        sig = None
                    else:
                        sig.confidence -= 5.0
                        log.debug(
                            "MTF misalignment penalty {} {}: -5.0 (score={:.2f})",
                            symbol, chan_name, _mtf_result.score,
                        )
        except Exception as _mtf_exc:
            log.debug("MTF confidence modifier error for {} {} (fail open): {}", symbol, chan_name, _mtf_exc)

        # Hard MTF block: signal was vetoed — return immediately.
        if sig is None:
            return _reject("gated", cross_verified)

        # Apply adaptive confidence decay based on signal freshness.
        # apply_confidence_decay clamps the final value to [0, 100].
        sig.confidence = apply_confidence_decay(
            confidence=sig.confidence,
            signal_generated_at=t0_signal,
            current_time=time.monotonic(),
            channel=chan_name,
        )
        sig.confidence = self._clamp_confidence(sig.confidence)
        sig.post_ai_confidence = sig.confidence
        # PR-01: accumulate scanner-level soft-gate penalties on top of any evaluator-
        # authored soft_penalty_total — do not overwrite the evaluator's path-level
        # penalty state.  The total reflects both evaluator quality judgments and
        # scanner gate assessments, preserving evaluator intent end-to-end.
        # _evaluator_penalty: the penalty written by the evaluator before this scanner
        # pipeline ran; soft_penalty is the scanner-gate portion accumulated above.
        _evaluator_penalty = getattr(sig, "soft_penalty_total", 0.0)
        sig.soft_penalty_total = _evaluator_penalty + soft_penalty
        sig.regime_penalty_multiplier = regime_mult
        sig.soft_gate_flags = ",".join(_fired_gates)
        # Classify signal into quality tier based on final confidence.
        sig.signal_tier = classify_signal_tier(sig.confidence)
        # Per-path scoring telemetry: capture setup_class before entering the
        # scoring block so tier counters can be keyed by path (not just channel).
        _sc = getattr(sig, "setup_class", "UNKNOWN")
        _sf = self._setup_family_for_channel(chan_name, _sc)
        self._increment_path_funnel("scored", chan_name, _sc)
        self._suppression_counters[f"candidate_reached_scoring:{_sc}"] += 1
        self._scoring_tier_counters[f"candidate_reached_scoring:{_sc}"] += 1
        # ── PR_09: Composite Signal Scoring Engine ────────────────────────
        # Overwrites sig.confidence and sig.signal_tier with the structured
        # 0-100 composite score.  Merges new dimension breakdown into the
        # existing component_scores so that downstream format checks still
        # see the "market"/"execution"/"risk" keys set earlier.
        try:
            _primary_tf = self._get_primary_timeframe(chan_name)
            _primary_ind = ctx.indicators.get(_primary_tf, {})
            _primary_cd = self._resolve_candles(ctx.candles, _primary_tf)
            _closes_arr = _primary_cd.get("close", [])
            _vol_arr = _primary_cd.get("volume", [])
            if _closes_arr and _vol_arr:
                _usd_vols = [c * v for c, v in zip(_closes_arr[-20:], _vol_arr[-20:])]
                _volume_last_usd = float(_usd_vols[-1]) if _usd_vols else 0.0
                _volume_avg_usd = float(np.mean(_usd_vols)) if _usd_vols else 0.0
            else:
                _volume_last_usd = 0.0
                _volume_avg_usd = 0.0
            _atr_pct = 50.0
            if ctx.regime_context is not None:
                try:
                    _atr_pct = float(ctx.regime_context.atr_percentile)
                except (TypeError, ValueError):
                    pass
            # Gather order-flow signals for family-aware thesis scoring.
            _oi_trend = "NEUTRAL"
            _liq_vol = 0.0
            if self.order_flow_store is not None:
                try:
                    _oi_trend = self.order_flow_store.get_oi_trend(symbol).value
                    _liq_vol = self.order_flow_store.get_recent_liq_volume_usd(symbol)
                except Exception:
                    pass
            _scoring_inp = ScoringInput(
                sweeps=ctx.smc_result.sweeps,
                mss=ctx.smc_result.mss,
                fvg_zones=ctx.smc_result.fvg,
                regime=_regime_key,
                setup_class=sig.setup_class,
                atr_percentile=_atr_pct,
                volume_last_usd=_volume_last_usd,
                volume_avg_usd=_volume_avg_usd,
                macd_histogram_last=_primary_ind.get("macd_histogram_last"),
                macd_histogram_prev=_primary_ind.get("macd_histogram_prev"),
                rsi_last=_primary_ind.get("rsi_last"),
                ema_fast=_primary_ind.get("ema9_last"),
                ema_slow=_primary_ind.get("ema21_last"),
                adx_last=_primary_ind.get("adx_last"),
                direction=sig.direction.value,
                chart_patterns=ctx.smc_data.get("chart_patterns", []),
                mtf_score=getattr(sig, "mtf_score", 0.0),
                cvd_divergence=ctx.smc_data.get("cvd_divergence"),
                cvd_divergence_strength=float(ctx.smc_data.get("cvd_divergence_strength") or 0.0),
                oi_trend=_oi_trend,
                liq_vol_usd=_liq_vol,
                funding_rate=_funding_rate,
            )
            _score_result = _scoring_engine.score(_scoring_inp)
            # Merge new dimension scores into component_scores (preserves existing keys)
            sig.component_scores.update(_score_result)
            sig.confidence = _score_result["total"]
            self._record_scoring_distribution(
                phase="pre_penalty",
                chan_name=chan_name,
                setup_family=_sf,
                setup_class=_sc,
                score=sig.confidence,
                tier=classify_signal_tier(sig.confidence),
            )
            if _score_result["total"] >= 80:
                sig.signal_tier = "A+"
                self._suppression_counters[f"score_80plus:{_sc}"] += 1
                self._scoring_tier_counters[f"score_80plus:{_sc}"] += 1
            elif _score_result["total"] >= 65:
                sig.signal_tier = "B"
                self._suppression_counters[f"score_65to79:{_sc}"] += 1
                self._scoring_tier_counters[f"score_65to79:{_sc}"] += 1
            elif _score_result["total"] >= 50:
                sig.signal_tier = "WATCHLIST"
                self._suppression_counters[f"score_50to64:{_sc}"] += 1
                self._scoring_tier_counters[f"score_50to64:{_sc}"] += 1
            else:
                log.debug(
                    "scoring below-threshold {} {} [{}]: total={:.1f} smc={} regime={} vol={} ind={} pat={} mtf={} thesis_adj={}",
                    symbol, chan_name, _sc, _score_result["total"],
                    _score_result["smc"], _score_result["regime"], _score_result["volume"],
                    _score_result["indicators"], _score_result["patterns"], _score_result["mtf"],
                    _score_result["thesis_adj"],
                )
                self._suppression_counters[f"score_below50:{chan_name}"] += 1
                self._suppression_counters[f"score_below50:{_sc}"] += 1
                self._scoring_tier_counters[f"score_below50:{_sc}"] += 1
                _below_tier = classify_signal_tier(sig.confidence)
                self._record_scoring_distribution(
                    phase="post_penalty",
                    chan_name=chan_name,
                    setup_family=_sf,
                    setup_class=_sc,
                    score=sig.confidence,
                    tier=_below_tier,
                )
                return _reject("filtered", cross_verified)
            log.debug(
                "composite score {} {} → {:.1f} (tier={}) smc={} regime={} vol={} ind={} pat={} mtf={} thesis_adj={}",
                symbol, chan_name, _score_result["total"], sig.signal_tier,
                _score_result["smc"], _score_result["regime"], _score_result["volume"],
                _score_result["indicators"], _score_result["patterns"], _score_result["mtf"],
                _score_result["thesis_adj"],
            )
        except Exception as _score_exc:
            log.debug("scoring engine error for {} {} (fail open): {}", symbol, chan_name, _score_exc)

        # PR-15: Apply the full accumulated soft-penalty (evaluator-authored + scanner-gate)
        # after composite score assignment so that the penalties are not overwritten by the
        # scoring engine.  sig.soft_penalty_total holds evaluator-level quality penalties
        # plus scanner-gate penalties; previously only the scanner portion (soft_penalty)
        # was deducted, leaving evaluator-authored penalties un-applied and allowing signals
        # with inflated pre-penalty confidence to pass downstream floor and tier gates.
        _total_soft_penalty = sig.soft_penalty_total  # evaluator-authored + scanner-gate combined
        if _total_soft_penalty > 0.0:
            sig.confidence -= _total_soft_penalty
            sig.confidence = self._clamp_confidence(sig.confidence)
            log.debug(
                "Soft-gate penalty applied {} {}: -{:.1f} (eval={:.1f} gate={:.1f}) → {:.1f} (post-scoring)",
                symbol, chan_name, _total_soft_penalty,
                _evaluator_penalty, soft_penalty, sig.confidence,
            )
        # PR-15: Re-classify tier after full penalty so that WATCHLIST/floor decisions are
        # made on the true post-penalty confidence, not the stale pre-penalty scoring tier.
        sig.signal_tier = classify_signal_tier(sig.confidence)
        self._record_scoring_distribution(
            phase="post_penalty",
            chan_name=chan_name,
            setup_family=_sf,
            setup_class=_sc,
            score=sig.confidence,
            tier=sig.signal_tier,
        )

        # ── PR_12: Statistical False-Positive Filter ──────────────────────
        # Apply rolling win-rate gate after scoring. Fail-open when no history.
        try:
            _sf_allow, _sf_conf, _sf_reason = _stat_filter.check(
                channel=chan_name,
                pair=symbol,
                regime=_regime_key,
                current_confidence=sig.confidence,
            )
            if not _sf_allow:
                log.debug(
                    "stat_filter suppressed {}/{}: {}",
                    symbol, chan_name, _sf_reason,
                )
                self.suppression_tracker.record(SuppressionEvent(
                    symbol=symbol,
                    channel=chan_name,
                    reason=REASON_STAT_FILTER,
                    regime=_regime_key,
                    would_be_confidence=sig.confidence,
                ))
                return _reject("filtered", cross_verified)
            sig.confidence = _sf_conf
            if "penalty" in _sf_reason:
                _existing_flags = sig.soft_gate_flags or ""
                sig.soft_gate_flags = (_existing_flags + f",{_sf_reason}").lstrip(",")
        except Exception as _sf_exc:
            log.debug("stat_filter error for {} {} (fail open): {}", symbol, chan_name, _sf_exc)

        # ── Pair Analysis Quality Gate ─────────────────────────────────────
        # Suppress signals from pairs with CRITICAL quality label (hit rate
        # < 35% or max drawdown > 15%).  Apply confidence penalty for WEAK
        # pairs.  Fail-open when the performance tracker is unavailable or
        # there is insufficient data.
        try:
            if self.router and hasattr(self.router, "performance_tracker"):
                _pa_quality = compute_pair_signal_quality(
                    self.router.performance_tracker, symbol, window_days=30,
                )
                if _pa_quality.quality_label == "CRITICAL":
                    log.info(
                        "pair_analysis suppressed {}/{}: quality=CRITICAL "
                        "hit_rate={:.1f}% dd={:.1f}%",
                        symbol, chan_name,
                        _pa_quality.hit_rate, _pa_quality.max_drawdown,
                    )
                    self.suppression_tracker.record(SuppressionEvent(
                        symbol=symbol,
                        channel=chan_name,
                        reason=REASON_PAIR_ANALYSIS,
                        regime=_regime_key,
                        would_be_confidence=sig.confidence,
                    ))
                    self._suppression_counters[f"pair_analysis:critical:{chan_name}"] += 1
                    return _reject("filtered", cross_verified)
                if _pa_quality.quality_label == "WEAK":
                    _pa_penalty = 8.0
                    sig.confidence = max(0.0, sig.confidence - _pa_penalty)
                    _existing_flags = sig.soft_gate_flags or ""
                    sig.soft_gate_flags = (
                        _existing_flags + f",pair_analysis:weak_penalty"
                    ).lstrip(",")
                    self._suppression_counters[f"pair_analysis:weak_penalty:{chan_name}"] += 1
                    log.debug(
                        "pair_analysis weak penalty {}/{}: -{}pts → {:.1f}",
                        symbol, chan_name, _pa_penalty, sig.confidence,
                    )
        except Exception as _pa_exc:
            log.debug("pair_analysis gate error for {} {} (fail open): {}", symbol, chan_name, _pa_exc)

        # SMC hard gate: require minimum structural basis (sweep OR MSS present).
        # A signal with smc_score < SMC_HARD_GATE_MIN has no institutional
        # footprint — it is a pure momentum/liquidity play with no SMC edge.
        # Fail-open when the scoring engine did not populate "smc" (engine error).
        # Relaxed minimum for SHORT signals in TRENDING_DOWN: market is going
        # their way, so the structural requirement is slightly eased.
        # Setup classes whose entry conditions are session/volume/structure based
        # (not sweep-based) are exempt from this gate.
        if "smc" in sig.component_scores:
            _setup = getattr(sig, "setup_class", "")
            if _setup in _SMC_GATE_EXEMPT_SETUPS:
                log.debug(
                    "SMC gate exempt for {} {} setup_class={} — skipping sweep requirement",
                    symbol, chan_name, _setup,
                )
            else:
                _smc_score = sig.component_scores["smc"]
                _smc_min = (
                    SMC_SCORE_MIN_TRENDING_SHORT
                    if _regime_key == "TRENDING_DOWN" and sig.direction.value == "SHORT"
                    else SMC_HARD_GATE_MIN
                )
                if _smc_score < _smc_min:
                    log.debug(
                        "SMC hard gate: {} {} smc_score={:.1f} < {:.1f}",
                        symbol, chan_name, _smc_score, _smc_min,
                    )
                    self._suppression_counters[f"smc_hard_gate:{chan_name}"] += 1
                    self.suppression_tracker.record(SuppressionEvent(
                        symbol=symbol,
                        channel=chan_name,
                        reason="smc_hard_gate",
                        regime=_regime_key,
                        would_be_confidence=sig.confidence,
                    ))
                    return _reject("filtered", cross_verified)

        # Trend hard gate: EMA alignment is non-negotiable for scalp channels.
        # indicator_score < TREND_HARD_GATE_MIN means MACD/RSI/EMA are not
        # supporting the direction — a structural contradiction.
        # Fail-open when the scoring engine did not populate "indicators".
        # Setup classes whose thesis does not depend on EMA alignment are exempt.
        if chan_name.startswith("360_SCALP") and "indicators" in sig.component_scores:
            _setup = getattr(sig, "setup_class", "")
            if _setup in _TREND_GATE_EXEMPT_SETUPS:
                log.debug(
                    "Trend gate exempt for {} {} setup_class={} — skipping EMA alignment gate",
                    symbol, chan_name, _setup,
                )
            else:
                _ind_score = sig.component_scores["indicators"]
                if _ind_score < TREND_HARD_GATE_MIN:
                    log.debug(
                        "Trend hard gate: {} {} ind_score={:.1f} < {:.1f}",
                        symbol, chan_name, _ind_score, TREND_HARD_GATE_MIN,
                    )
                    self._suppression_counters[f"trend_hard_gate:{chan_name}"] += 1
                    self.suppression_tracker.record(SuppressionEvent(
                        symbol=symbol,
                        channel=chan_name,
                        reason="trend_hard_gate",
                        regime=_regime_key,
                        would_be_confidence=sig.confidence,
                    ))
                    return _reject("filtered", cross_verified)

        min_conf = self.confidence_overrides.get(chan_name, chan.config.min_confidence)

        # Regime transition boost (item 15): if regime just changed in the direction
        # of this signal, apply a confidence boost (high-probability entry window).
        try:
            _trans_boost = self.regime_detector.get_transition_boost(sig.direction.value)
            if _trans_boost > 0.0:
                sig.confidence = min(100.0, sig.confidence + _trans_boost)
                sig.soft_gate_flags = (
                    sig.soft_gate_flags + f",REGIME_TRANSITION:+{_trans_boost:.0f}"
                ).lstrip(",")
                log.debug(
                    "Regime transition boost {} {}: +{:.1f} → {:.1f}",
                    symbol, chan_name, _trans_boost, sig.confidence,
                )
        except Exception:
            pass  # Fail-safe

        # QUIET regime safety net for scalp channels: only the highest-quality
        # mean-reversion setups are allowed through when the market is compressed.
        # QUIET_COMPRESSION_BREAK is exempt — it is the evaluator specifically
        # designed for QUIET regime (BB squeeze release) and must not be
        # self-blocked by this gate.
        if _regime_key == "QUIET" and chan_name.startswith("360_SCALP"):
            _setup = getattr(sig, "setup_class", "")
            if _setup == "QUIET_COMPRESSION_BREAK":
                log.debug(
                    "QUIET_SCALP_BLOCK exempt for {} {} setup_class=QUIET_COMPRESSION_BREAK",
                    symbol, chan_name,
                )
            elif _setup == "DIVERGENCE_CONTINUATION" and sig.confidence >= _QUIET_DIVERGENCE_MIN_CONFIDENCE:
                log.debug(
                    "QUIET_SCALP_BLOCK exempt for {} {} setup_class=DIVERGENCE_CONTINUATION conf={:.1f} >= path_min={:.1f}",
                    symbol, chan_name, sig.confidence, _QUIET_DIVERGENCE_MIN_CONFIDENCE,
                )
            elif sig.confidence < QUIET_SCALP_MIN_CONFIDENCE:
                log.info(
                    "QUIET_SCALP_BLOCK {} {} conf={:.1f} < min={:.1f}",
                    symbol, chan_name, sig.confidence, QUIET_SCALP_MIN_CONFIDENCE,
                )
                self.suppression_tracker.record(SuppressionEvent(
                    symbol=symbol,
                    channel=chan_name,
                    reason=REASON_CONFIDENCE,
                    regime=_regime_key,
                    would_be_confidence=sig.confidence,
                ))
                # Track consecutive failures for this symbol+channel
                _fail_key = (symbol, chan_name)
                _prev = self._conf_fail_tracker.get(_fail_key, (0, 0.0))
                _new_count = _prev[0] + 1
                _until = time.monotonic() + _CONF_FAIL_COOLDOWN_S if _new_count >= _CONF_FAIL_MAX_CONSECUTIVE else _prev[1]
                self._conf_fail_tracker[_fail_key] = (_new_count, _until)
                if _new_count >= _CONF_FAIL_MAX_CONSECUTIVE:
                    log.debug(
                        "Failed-detection cooldown triggered for {} {} ({}x consecutive) — suppressing for {:.0f}s",
                        symbol, chan_name, _new_count, _CONF_FAIL_COOLDOWN_S,
                    )
                return _reject("filtered", cross_verified)
        # WATCHLIST tier: signals with confidence 50-64 are kept as WATCHLIST
        # instead of being discarded.  Only the SCALP channel family generates
        # watchlist alerts; SWING and SPOT require higher confidence.
        _watchlist_confidence = 50.0
        if (
            sig.signal_tier == "WATCHLIST"
            and chan_name in _SCALP_CHANNELS
            and sig.confidence >= _watchlist_confidence
        ):
            # Keep as WATCHLIST — the router will dispatch this to the free
            # channel only (zone-alert preview, not a paid active trade).
            self._populate_signal_context(sig, volume_24h, ctx)
            return sig, cross_verified
        if (
            sig.confidence < min_conf
            or sig.component_scores.get("market", 0.0) < 12.0
            or sig.component_scores.get("execution", 0.0) < 10.0
            or sig.component_scores.get("risk", 0.0) < 10.0
        ):
            self.suppression_tracker.record(SuppressionEvent(
                symbol=symbol,
                channel=chan_name,
                reason=REASON_CONFIDENCE,
                regime=_regime_key,
                would_be_confidence=sig.confidence,
            ))
            return _reject("filtered", cross_verified)
        # Reset failed-detection counter — this symbol+channel produced a valid signal
        self._conf_fail_tracker.pop((symbol, chan_name), None)
        self._populate_signal_context(sig, volume_24h, ctx)
        return sig, cross_verified

    def _get_channel_candidate(
        self,
        *,
        chan: Any,
        chan_name: str,
        symbol: str,
        ctx_for_chan: ScanContext,
        volume_24h: float,
    ) -> Any:
        try:
            return chan.evaluate(
                symbol=symbol,
                candles=ctx_for_chan.candles,
                indicators=ctx_for_chan.indicators,
                smc_data=ctx_for_chan.smc_data,
                spread_pct=ctx_for_chan.spread_pct,
                volume_24h_usd=volume_24h,
                regime=ctx_for_chan.regime_result.regime.value,
            )
        except Exception as _exc:
            log.debug("Channel {} eval error for {}: {}", chan_name, symbol, _exc)
            return None

    async def _scan_symbol(self, symbol: str, volume_24h: float) -> None:
        """Run all channel evaluations for one symbol."""
        ctx = await self._build_scan_context(symbol, volume_24h)
        if ctx is None:
            return
        ticks = self.data_store.ticks.get(symbol, [])

        # Compute rolling BTC correlation for this symbol (once per scan cycle)
        self._update_btc_correlation(symbol)

        # Collect all signals before deciding what to emit (confluence check)
        _pending_signals: list = []

        # SMC re-detect cache: deduplicate detections across channels sharing the same TF set.
        # Key: tuple of timeframes. Value: (SMCResult, smc_data_dict)
        _smc_cache: Dict[tuple, tuple] = {}

        for chan in self.channels:
            chan_name = chan.config.name
            # Controlled rollout gating (PR-5): explicit per-channel state
            # decides live eligibility with fail-closed semantics.
            if not self._is_live_rollout_enabled_for_symbol(chan_name, symbol):
                self._record_rollout_live_exclusion(chan_name, symbol)
                continue
            if self._should_skip_channel(symbol, chan_name, ctx):
                continue
            # Re-detect SMC with channel-specific timeframe preference when available.
            # This ensures scalp channels see low-TF sweeps first while swing/spot
            # channels only act on high-TF institutional sweeps.
            _ch_tfs = _CHANNEL_SMC_TIMEFRAMES.get(chan_name)
            if _ch_tfs is not None:
                _cache_key = tuple(_ch_tfs)
                if _cache_key in _smc_cache:
                    _smc_r, _new_smc_data = _smc_cache[_cache_key]
                    ctx_for_chan = _dc.replace(ctx, smc_result=_smc_r, smc_data=_new_smc_data)
                else:
                    try:
                        _smc_r = self.smc_detector.detect(
                            symbol, ctx.candles, ticks, self.order_flow_store,
                            lookback=SMC_SCALP_LOOKBACK,
                            tolerance_pct=SMC_SCALP_TOLERANCE_PCT,
                            smc_timeframes=_ch_tfs,
                        )
                        _new_smc_data = _smc_r.as_dict()
                        # Carry over metadata fields added by _build_scan_context()
                        # that are not part of the SMCResult dataclass.
                        _new_smc_data["pair_profile"] = ctx.smc_data.get("pair_profile")
                        _new_smc_data["regime_context"] = ctx.smc_data.get("regime_context")
                        # Carry over order-flow fields wired in _build_scan_context()
                        # so evaluators see funding_rate and cvd regardless of which
                        # channel-specific SMC re-detect path is taken.
                        # Only carry over when the key was set (i.e. order_flow_store present).
                        for _of_key in ("funding_rate", "cvd"):
                            if _of_key in ctx.smc_data:
                                _new_smc_data[_of_key] = ctx.smc_data[_of_key]
                        _smc_cache[_cache_key] = (_smc_r, _new_smc_data)
                        ctx_for_chan = _dc.replace(
                            ctx,
                            smc_result=_smc_r,
                            smc_data=_new_smc_data,
                        )
                    except Exception as _exc:
                        log.debug("Per-channel SMC re-detect failed for {} {}: {}", symbol, chan_name, _exc)
                        ctx_for_chan = ctx
            else:
                ctx_for_chan = ctx

            if chan_name == "360_SCALP":
                # ScalpChannel.evaluate() returns List[Signal] — every valid candidate
                # is processed independently through the gate chain.  Same-direction
                # signals from the same symbol are deduplicated here so that only one
                # setup per direction can enter _pending_signals per cycle.
                _raw_result = self._get_channel_candidate(
                    chan=chan,
                    chan_name=chan_name,
                    symbol=symbol,
                    ctx_for_chan=ctx_for_chan,
                    volume_24h=volume_24h,
                )
                # Normalise: real ScalpChannel returns list; legacy mocks return Signal|None
                if isinstance(_raw_result, list):
                    _raw_sigs = _raw_result
                elif _raw_result is not None:
                    _raw_sigs = [_raw_result]
                else:
                    _raw_sigs = []
                if not _raw_sigs:
                    self._channel_funnel_counters[f"no_candidate_generated:{chan_name}"] += 1
                # PR-03: Quality-ranked arbitration — evaluate ALL same-direction
                # candidates and keep the best one by final confidence score.
                # This replaces the previous first-wins dedup that allowed a
                # weaker earlier candidate to suppress a stronger later one purely
                # because of method-evaluation order.
                # Format: direction → (best_prepared_sig, chan_name)
                _scalp_dir_best: dict = {}
                for _raw_sig in _raw_sigs:
                    _raw_setup = self._normalize_setup_class(getattr(_raw_sig, "setup_class", None))
                    self._increment_path_funnel("generated", chan_name, _raw_setup)
                    _funnel_meta: Dict[str, Any] = {}
                    # cross_verified is None for all scalp channels (cross-exchange
                    # verification is skipped for 360_SCALP — see _prepare_signal).
                    sig, _cross_verified = await self._prepare_signal(
                        symbol, volume_24h, chan, ctx_for_chan,
                        _preseed_signal=_raw_sig,
                        _funnel_meta=_funnel_meta,
                    )
                    if sig is None:
                        _reject_stage = _funnel_meta.get("reject_stage")
                        if _reject_stage == "filtered":
                            self._increment_path_funnel("filtered", chan_name, _raw_setup)
                        else:
                            self._increment_path_funnel("gated", chan_name, _raw_setup)
                        continue
                    # Stamp before arbitration/confluence can rewrite setup_class.
                    self._stamp_origin_setup_identity(sig, chan_name)
                    _sig_dir = (
                        sig.direction.value if hasattr(sig.direction, "value") else str(sig.direction)
                    )
                    if self._is_in_global_cooldown(symbol, _sig_dir):
                        log.debug(
                            "Global directional cooldown: {} {} {} skipped",
                            symbol, _sig_dir, chan_name,
                        )
                        continue
                    _existing = _scalp_dir_best.get(_sig_dir)
                    if _existing is None:
                        _scalp_dir_best[_sig_dir] = (sig, chan_name)
                    elif sig.confidence > _existing[0].confidence:
                        # New candidate is strictly better — replace and log.
                        log.debug(
                            "Scalp arbitration: {} {} {} (conf={:.1f}) replaces"
                            " {} (conf={:.1f})",
                            symbol, _sig_dir,
                            getattr(sig, "setup_class", "?"), sig.confidence,
                            getattr(_existing[0], "setup_class", "?"),
                            _existing[0].confidence,
                        )
                        _scalp_dir_best[_sig_dir] = (sig, chan_name)
                    else:
                        # Existing candidate is better (or equal) — suppress new one.
                        log.debug(
                            "Scalp arbitration: {} {} {} (conf={:.1f}) suppressed;"
                            " {} (conf={:.1f}) retained",
                            symbol, _sig_dir,
                            getattr(sig, "setup_class", "?"), sig.confidence,
                            getattr(_existing[0], "setup_class", "?"),
                            _existing[0].confidence,
                        )
                # Emit arbitration winners into the pending signals queue.
                for _sig_dir, (_best_sig, _best_chan) in _scalp_dir_best.items():
                    _sc = getattr(_best_sig, "setup_class", chan_name)
                    self._setup_eval_counts[_sc] += 1
                    _pending_signals.append((_best_sig, _best_chan))
            else:
                _raw_result = self._get_channel_candidate(
                    chan=chan,
                    chan_name=chan_name,
                    symbol=symbol,
                    ctx_for_chan=ctx_for_chan,
                    volume_24h=volume_24h,
                )
                if _raw_result is None:
                    self._channel_funnel_counters[f"no_candidate_generated:{chan_name}"] += 1
                    continue
                _raw_setup = self._normalize_setup_class(getattr(_raw_result, "setup_class", None))
                self._increment_path_funnel("generated", chan_name, _raw_setup)
                _funnel_meta: Dict[str, Any] = {}
                sig, cross_verified = await self._prepare_signal(
                    symbol,
                    volume_24h,
                    chan,
                    ctx_for_chan,
                    _preseed_signal=_raw_result,
                    _funnel_meta=_funnel_meta,
                )
                if sig is None:
                    _reject_stage = _funnel_meta.get("reject_stage")
                    if _reject_stage == "filtered":
                        self._increment_path_funnel("filtered", chan_name, _raw_setup)
                    else:
                        self._increment_path_funnel("gated", chan_name, _raw_setup)
                    continue
                # Stamp before any downstream transformations; _enqueue_signal
                # performs the same call as an idempotent durability backstop.
                self._stamp_origin_setup_identity(sig, chan_name)
                # Directional global cooldown check: skip if same (symbol, direction)
                # fired recently. Opposite direction is not blocked.
                _sig_dir = sig.direction.value if hasattr(sig.direction, "value") else str(sig.direction)
                if self._is_in_global_cooldown(symbol, _sig_dir):
                    log.debug(
                        "Global directional cooldown: {} {} {} skipped",
                        symbol, _sig_dir, chan_name,
                    )
                    continue
                # Track evaluated setup class for diversity telemetry
                _sc = getattr(sig, "setup_class", chan_name)
                self._setup_eval_counts[_sc] += 1
                _pending_signals.append((sig, chan_name))

        # --- Radar evaluation pass (explicit rollout-governed observe-only paths) ---
        # Evaluates channels in radar_only state and limited_live channels outside
        # their pilot symbol scope.
        # Results are written to _radar_scores for RadarChannel to read.
        # No signals are published here — fail-safe: exceptions are debug-logged.
        _regime_str = ""
        try:
            _regime_str = ctx.regime_result.regime.value
        except Exception:
            pass
        for chan in self.channels:
            chan_name = chan.config.name
            if not self._is_radar_rollout_enabled(chan_name, symbol):
                continue
            try:
                _radar_result = chan.evaluate(
                    symbol=symbol,
                    candles=ctx.candles,
                    indicators=ctx.indicators,
                    smc_data=ctx.smc_data,
                    spread_pct=ctx.spread_pct,
                    volume_24h_usd=volume_24h,
                    regime=_regime_str,
                )
                # ScalpChannel returns List[Signal]; pick the first for radar scoring.
                if isinstance(_radar_result, list):
                    _radar_sig = _radar_result[0] if _radar_result else None
                else:
                    _radar_sig = _radar_result
                if _radar_sig is not None and _radar_sig.confidence >= RADAR_ALERT_MIN_CONFIDENCE:
                    _existing = self._radar_scores.get(chan_name)
                    if (
                        _existing is None
                        or _radar_sig.confidence > _existing.get("confidence", 0)
                    ):
                        _bias_val = getattr(_radar_sig.direction, "value", str(_radar_sig.direction))
                        _setup_val = getattr(_radar_sig, "setup_class", chan_name)
                        self._radar_scores[chan_name] = {
                            "symbol": symbol,
                            "confidence": _radar_sig.confidence,
                            "bias": _bias_val,
                            "setup_name": _setup_val,
                            "waiting_for": "confirm",
                        }
                        # Notify the free-watch service so it can post a radar
                        # alert to the free channel and create a tracked watch.
                        _radar_cb = getattr(self, "on_radar_candidate", None)
                        if _radar_cb is not None:
                            try:
                                await _radar_cb(
                                    symbol=symbol,
                                    source_channel=chan_name,
                                    bias=_bias_val,
                                    setup_name=_setup_val,
                                    waiting_for="confirm",
                                    confidence=_radar_sig.confidence,
                                )
                            except Exception as _cb_exc:
                                log.debug("on_radar_candidate callback error: {}", _cb_exc)
            except Exception as _radar_exc:
                log.debug("Radar eval error {} {}: {}", chan_name, symbol, _radar_exc)
        # ------------------------------------------------------------------

        if not _pending_signals:
            return

        # Check for multi-strategy confluence: group by direction
        _emitted_directions: set = set()
        if len(_pending_signals) >= 2:
            _by_direction: dict = defaultdict(list)
            for sig, ch_name in _pending_signals:
                _dir = sig.direction.value if hasattr(sig.direction, "value") else str(sig.direction)
                _by_direction[_dir].append((sig, ch_name))

            for direction, signals_and_channels in _by_direction.items():
                if len(signals_and_channels) < 2:
                    continue
                # Multi-strategy confluence detected – pick highest-confidence signal
                signals_and_channels.sort(key=lambda x: x[0].confidence, reverse=True)
                best_sig, best_ch = signals_and_channels[0]
                contributing = [ch for _, ch in signals_and_channels]
                count = len(contributing)
                boost = 5.0 if count == 2 else (8.0 if count == 3 else 12.0)
                best_sig.confidence = min(100.0, best_sig.confidence + boost)
                best_sig.setup_class = "MULTI_STRATEGY_CONFLUENCE"
                best_sig.analyst_reason = (
                    f"Multi-Strategy Confluence: {', '.join(contributing)} "
                    f"(+{boost:.0f} boost)"
                )
                best_sig.quality_tier = "A+" if best_sig.confidence >= 80 else "A"
                log.info(
                    "Multi-Strategy Confluence {} {}: strategies={} boost=+{:.0f} conf={:.1f}",
                    symbol, direction, contributing, boost, best_sig.confidence,
                )
                if await self._enqueue_signal(best_sig):
                    self._setup_emit_counts[best_sig.setup_class] += 1
                    self._increment_path_funnel("emitted", best_ch, best_sig.setup_class)
                    for _, ch_name in signals_and_channels:
                        self._set_cooldown(symbol, ch_name)
                    self.cluster_suppressor.record_signal(symbol, direction)
                    # Directional cooldown: key is (symbol, direction) so the
                    # same symbol can fire in the opposite direction after cooldown.
                    self._global_symbol_cooldown[(symbol, direction)] = (
                        time.monotonic() + GLOBAL_SYMBOL_COOLDOWN_SECONDS
                    )
                _emitted_directions.add(direction)

        # Emit remaining signals that weren't part of confluence
        for sig, chan_name in _pending_signals:
            _dir = sig.direction.value if hasattr(sig.direction, "value") else str(sig.direction)
            if _dir in _emitted_directions:
                continue
            if not await self._enqueue_signal(sig):
                continue
            self._setup_emit_counts[sig.setup_class] += 1
            self._increment_path_funnel("emitted", chan_name, sig.setup_class)
            self._set_cooldown(symbol, chan_name)
            self.cluster_suppressor.record_signal(symbol, _dir)
            # Directional cooldown: key is (symbol, direction) so the
            # same symbol can fire in the opposite direction after cooldown.
            self._global_symbol_cooldown[(symbol, _dir)] = (
                time.monotonic() + GLOBAL_SYMBOL_COOLDOWN_SECONDS
            )

    async def _lightweight_tier3_scan(self) -> None:
        """Lightweight volume/momentum scan for Tier 3 pairs.

        Checks whether any Tier 3 pair has experienced a volume surge exceeding
        ``TIER3_VOLUME_SURGE_MULTIPLIER`` × its previous 24h volume.  Qualifying
        pairs are promoted to Tier 2 via :meth:`PairManager.check_promotions` so
        that they receive full SWING+SPOT channel evaluation on the next cycle.

        No order book fetches, kline lookups, or indicator computation are
        performed — this is intentionally minimal to avoid Binance weight
        exhaustion.
        """
        tier3_pairs = [
            (sym, info)
            for sym, info in self.pair_mgr.pairs.items()
            if info.tier == PairTier.TIER3
        ]
        if not tier3_pairs:
            return
        log.debug("Tier 3 lightweight scan: %d pairs", len(tier3_pairs))
        promoted = self.pair_mgr.check_promotions()
        if promoted:
            log.info(
                "Tier 3 auto-promoted %d pairs to Tier 2: %s",
                len(promoted), promoted[:10],
            )
