"""Scanner – periodic evaluation of all pairs across channel strategies.

Extracted from :class:`src.main.CryptoSignalEngine` for modularity.
Supports signal cooldown de-duplication, market-regime-aware gating,
and optional circuit-breaker integration.
"""

from __future__ import annotations

import asyncio
import dataclasses as _dc
import functools
import os
import re
import json
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
    BTC_STATE_ENABLED,
    BTC_STATE_HAIRCUT_ENABLED,
    BTC_STATE_K,
    BTC_STATE_FLOOR,
    BTC_STATE_CT_LONG_MULT,
    BTC_STATE_CT_SHORT_MULT,
    BTC_STATE_SEVERE_SETUP_WEIGHT,
    BTC_STATE_MILD_SETUP_WEIGHT,
    BTC_STATE_CACHE_TTL_SEC,
    BTC_STATE_COUPLING_TF,
    BTC_STATE_COUPLING_LOOKBACK,
    CT_LONG_MACRO_GATE_ENABLED,
    CT_LONG_MACRO_GATE_SETUPS,
    CT_LONG_MACRO_USE_BTC,
    CT_LONG_MACRO_USE_PER_COIN,
    CT_SHORT_MACRO_GATE_ENABLED,
    CT_SHORT_MACRO_GATE_SETUPS,
    CT_SHORT_MACRO_USE_BTC,
    CT_SHORT_MACRO_USE_PER_COIN,
    BTC_MACRO_TF,
    BTC_MACRO_FAST_PERIOD,
    BTC_MACRO_RECOVER_PERIOD,
    BTC_MACRO_SLOW_PERIOD,
    BTC_MACRO_CACHE_TTL_SEC,
    COIN_MACRO_TF,
    COIN_MACRO_FAST_PERIOD,
    COIN_MACRO_RECOVER_PERIOD,
    COIN_MACRO_SLOW_PERIOD,
    DARK_FLAG_SHADOW_TELEMETRY,
    FEEDBACK_LOOP_ENABLED,
    NARRATIVE_PAIR_BONUS,
    NARRATIVE_PAIR_LIST,
    FUNDING_RATE_BOOST,
    FUNDING_RATE_BOOST_THRESHOLD,
    FUNDING_RATE_PENALTY,
    FUNDING_RATE_PENALTY_THRESHOLD,
    GLOBAL_SYMBOL_COOLDOWN_SECONDS,
    LEVEL_REARM_BUCKET_BPS,
    LEVEL_REARM_CEILING_PCT,
    LEVEL_REARM_FALLBACK_PCT,
    LEVEL_REARM_FLOOR_PCT,
    LEVEL_REARM_SL_MULTIPLIER,
    LEVEL_REARM_TTL_SEC,
    LIFECYCLE_COOLDOWN_EXPIRED_SEC,
    LIFECYCLE_COOLDOWN_INVALIDATION_SEC,
    LIFECYCLE_COOLDOWN_SL_SEC,
    LOSS_STREAK_LOSS_PCT,
    LOSS_STREAK_RESET_PCT,
    MAX_CORRELATED_SCALP_SIGNALS,
    MAX_KLINE_STALENESS_SEC,
    MTF_HARD_BLOCK,
    MTF_MIN_SCORE_TRENDING_SHORT,
    QUIET_SCALP_MIN_CONFIDENCE,
    RADAR_ALERT_MIN_CONFIDENCE,
    RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED,
    RANGING_LOW_ATR_SUPPRESS_PCTILE,
    RANGING_LOW_ATR_SUPPRESS_SETUPS,
    REGIME_MIN_VOLUME_USD,
    SCAN_MIN_VOLUME_USD,
    SCAN_SYMBOL_BLACKLIST,
    SEED_TIMEFRAMES,
    SHADOW_STRATEGY_COOLDOWN_SEC,
    SIGNAL_SCAN_COOLDOWN_SECONDS,
    SIGNAL_VALID_FOR_MINUTES,
    SMC_HARD_GATE_MIN,
    SMC_SCALP_LOOKBACK,
    SMC_SCALP_TOLERANCE_PCT,
    SMC_SCORE_MIN_TRENDING_SHORT,
    MOVER_PROMOTION_MAX_PAIRS,
    MOVER_PROMOTION_TTL_SEC,
    MOVER_PROMOTION_MIN_PCT,
    MOVER_PROMOTION_MIN_VOLUME_USD,
    MOVER_MAX_SPREAD_PCT,
    COUNTERTREND_MOVER_HARD_BLOCK_ENABLED,
    COUNTERTREND_MOVER_MIN_FAN_PCT,
    RANGE_FADE_CONTEXT_GATE_ENABLED,
    RANGE_FADE_CONTEXT_MIN_VERDICT,
    SURGE_PROMOTION_MAX_PAIRS,
    SURGE_PROMOTION_VOLUME_MULTIPLIER,
    TIER2_SCAN_EVERY_N_CYCLES,
    SCAN_EXECUTOR_WORKERS,
    SCAN_STAGE_TIMING_ENABLED,
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
from src.pre_tp_stamping import stamp_pre_tp
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
from src.regime import MarketRegime, detect_regime_from_arrays
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
from src import fail_open
from src import pair_penalty as _pair_penalty
from src.feedback_loop import FeedbackLoop
from src.kill_zone import check_kill_zone_gate
from src.mtf import check_mtf_gate, compute_mtf_confluence, _TF_WEIGHTS as _MTF_TF_WEIGHTS
from src.oi_filter import analyse_oi, check_oi_gate
from src.pair_manager import (
    PairInfo,
    PairTier,
    _PAIR_BLACKLIST,
    classify_pair_tier,
)
from src.confluence_detector import ConfluenceDetector
from src.level_book import LevelBook
from src.structure_state import LEG_DOMINANCE_THRESHOLD, StructureTracker
from src.volume_profile import VolumeProfileStore
from src.spoof_detect import check_spoof_gate
from src.tier_manager import TierManager
from src.utils import get_logger, price_decimal_fmt, utcnow
from src.btc_direction import (
    check_btc_direction_gate,
    check_countertrend_mover_block,
    check_symbol_direction_gate,
)
from src.btc_state import (
    DEFAULT_TF_WEIGHTS as _BTC_STATE_TF_WEIGHTS,
    compute_btc_state,
    compute_downside_coupling,
    compute_haircut_factor,
    macro_direction,
)
from src.market_context import build_market_context
from src.volume_divergence import check_volume_divergence_gate
from src.vwap import check_vwap_extension, compute_vwap
from src.ai_engine import get_ai_insight
from src.chart_patterns import detect_patterns, pattern_confidence_bonus, detect_all_patterns
from src.stat_filter import CohortEdgeStore, StatisticalFilter
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
    REASON_COHORT_EDGE,
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

# Cohort edge store — STEP 1 observe-only data collection layer.
# Tracks outcomes keyed by (setup_class, side, regime_family, btc_macro_dir).
# Shadow-logs would-emit / would-suppress verdicts; no live decisions yet.
_cohort_edge_store = CohortEdgeStore()

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

# Universe-hygiene blacklist shared with pair_manager (stablecoins +
# tokenized stocks / commodities / FX).  The mover-admission path
# (`_ensure_mover_pair`) synthesises pairs straight off the `!ticker@arr`
# board and must honour the same exclusions as every pair_manager fetch
# path — otherwise Class-C non-crypto perps re-enter through promotion.
_MOVER_UNIVERSE_BLACKLIST: frozenset = _PAIR_BLACKLIST

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

# Higher-TF keys whose closed-candle counts fingerprint the SMC result cache.
# Excludes 1m: the in-progress partial candle's last_close changes every tick,
# while structural sweeps/FVGs/orderblocks are determined by completed 5m+
# candles and remain stable across ~20 consecutive 15s scan cycles.
_SMC_CACHE_TFS: tuple = ("4h", "1h", "15m", "5m")

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
    # 2026-05-13 diag (post-#379 deploy) showed 1 B-tier LSR candidate /h
    # killed by trend_hard_gate.  LSR is counter-trend by design: it sells
    # into long sweeps and buys into short sweeps — EMA alignment with the
    # entry direction is *bearish* for the LSR thesis (price has already
    # moved too far), not bullish.  Requiring trend alignment for LSR
    # contradicts the path's setup_class doctrine and was the bottleneck
    # blocking the second-most-active path in the funnel.
    "LIQUIDITY_SWEEP_REVERSAL",
})

# Penalty multiplier applied to scalp-channel soft gates when the regime is
# QUIET.  Higher than the default QUIET multiplier (0.8) to ensure only
# top-tier signals — genuine mean-reversion setups — pass through.
_SCALP_QUIET_REGIME_PENALTY: float = 1.8

# Path-specific QUIET confidence floors — REMOVED 2026-05-04 to align with
# OWNER_BRIEF §2.1a scalping doctrine: "only the final paid signal matters,
# watchlist is scrap."  Previous exempts (DIV_CONT ≥ 64, FUNDING ≥ 60, QCB
# fully exempt) were lowering the QUIET-block threshold to enable signals
# below the 65 paid-tier minimum.  Those sub-65 signals routed to watchlist
# tier → free channel (scrap by doctrine), generating no business value.
# The global QUIET_SCALP_MIN_CONFIDENCE (65) now applies uniformly to all
# 360_SCALP setups in QUIET regime.  No paid signals are affected — every
# 65+ signal still passes through unchanged.

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
    "MOVER_TREND_PULLBACK": "trend_following",
    "MOVER_AVWAP_SCALP": "trend_following",
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
    # 2026-07-15: MEAN_REVERT must map to mean_reversion — an unmapped setup
    # falls into family "other", which is BLOCKED in RANGING-low-ADX, i.e.
    # exactly this path's home regime (fail-closed comment below).
    "MEAN_REVERT": "mean_reversion",
    # 2026-07-18: RANGE_FADE fades a range edge back to the mid — reversion to
    # value, same family; unmapped would fall to "other" (blocked in
    # RANGING-low-ADX, its home regime — same fail-closed trap MEAN_REVERT hit).
    "RANGE_FADE": "mean_reversion",
    "QUIET_COMPRESSION_BREAK": "compression",
    "DIVERGENCE_CONTINUATION": "divergence",
}

# OWNER_BRIEF §3.4 + §3.2 #4 doctrine alignment — MTF hard-block exempt setups.
#
# §3.4 explicitly assigns these setup classes "None" HTF treatment:
#   - Tape-driven: WHALE / LIQUIDATION_REVERSAL / FUNDING_EXTREME — direction
#     comes from realtime order flow (tick imbalance / cascade / funding sign),
#     not from candle-EMA structure.  An EMA-alignment hard veto is
#     structurally orthogonal to the thesis.
#   - Breakout: VSB / BDS / ORB — "fires in any HTF context."  The breakout
#     event is the thesis; whether 1H/4H EMAs happen to align is a separate
#     statistical property the confidence score already consumes via
#     `mtf_aligned_count`.
#
# Per §3.2 #4 ("soft penalties over hard blocks; reserve hard blocks for
# structural-impossibility checkpoints"), these paths must not be hard-
# vetoed by the MTF gate.  Their structural quality is enforced upstream
# by their own thesis gates inside the evaluator (whale_alert + OBI +
# delta-imbalance for WHALE; cascade detection for LIQ_REVERSAL; funding
# extreme for FUNDING; breakout_not_found + volume_spike + ema_alignment
# for VSB/BDS/ORB) and downstream by confidence scoring + the 65 paid-tier
# floor.  The MTF score is still computed — it just stops being a veto.
#
# Setups NOT exempt:
#   - LSR / FAR (counter-trend by design): family cap 0.35 already provides
#     the doctrine-faithful relaxation; their evaluators already apply the
#     1H+4H-both-oppose soft penalty internally.
#   - SR_FLIP / QCB (structure with optional counter-trend): same — family
#     cap + evaluator-side soft penalty already aligned.
#   - TPE / DIV_CONT / CLS / PDC (trend-aligned): regime gate is the
#     operative HTF check; an EMA-alignment threshold inside a TRENDING
#     regime is consistent with their thesis.
#
# Set MTF_DOCTRINE_BYPASS_ENABLED=false to restore the legacy hard-block
# behaviour engine-wide (kill switch for diagnosis / rollback).
_SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS: frozenset[str] = frozenset({
    # Tape-driven (§3.4 row 2)
    "WHALE_MOMENTUM",
    "LIQUIDATION_REVERSAL",
    "FUNDING_EXTREME_SIGNAL",
    # Breakout — fires in any HTF context (§3.4 row 5)
    "VOLUME_SURGE_BREAKOUT",
    "BREAKDOWN_SHORT",
    "OPENING_RANGE_BREAKOUT",
    # Mover continuation — like the breakout family, it fires in any HTF context
    # (§3.4 row 5): the move itself (MA7↔MA99 stack separation ≥ MOVER_TP_MIN_
    # STACK_SEP_PCT) defines direction and regime, so the HTF confluence / longs-
    # regime gates must not veto it.  Its own mover-separation + reclaim gates are
    # the filter.  Family stays trend_following for SCORING affinity only (#621).
    "MOVER_TREND_PULLBACK",
    # AVWAP mover scalp — same: the AVWAP slope defines direction/regime, so the
    # HTF confluence / longs-regime gates must not veto it.
    "MOVER_AVWAP_SCALP",
})

_MTF_DOCTRINE_BYPASS_ENABLED: bool = os.getenv(
    "MTF_DOCTRINE_BYPASS_ENABLED", "true"
).lower() not in ("0", "false", "no", "off")

# Longs higher-timeframe regime gate.  A LONG fired while the 15m regime is
# trending DOWN fights the larger tide — the losing bucket in the 496-signal
# audit (removing it flipped the realised book from -14.1 to +3.0).  Gated on
# the unified, tier-aware 15m regime label (see regime.detect_regime_from_arrays)
# so "trend" means the same thing as the 5m entry regime.  Shorts are not gated.
_MTF_LONGS_REGIME_GATE_ENABLED: bool = os.getenv(
    "MTF_LONGS_REGIME_GATE_ENABLED", "true"
).lower() not in ("0", "false", "no", "off")
# Dark mode: evaluate and count what WOULD be blocked without rejecting, so the
# suppressed volume can be measured before the gate is trusted to hard-block.
_MTF_LONGS_REGIME_GATE_DARK: bool = os.getenv(
    "MTF_LONGS_REGIME_GATE_DARK", "false"
).lower() not in ("0", "false", "no", "off")

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

# Families whose thesis is structural reclaim/reversal and therefore require
# family-semantic downstream MTF evaluation (not plain trend-alignment only).
_SCALP_MTF_SEMANTIC_FAMILIES: frozenset[str] = frozenset({
    "reclaim_retest",
    "reversal",
})
_SCALP_MTF_SEMANTIC_NEAR_MISS_MAX_DELTA: float = 0.10

# Families intentionally blocked when the market is explicitly RANGING with
# weak directional strength (ADX below _RANGING_ADX_SUPPRESS_THRESHOLD).
# This replaces the previous channel-wide hard pre-skip for 360_SCALP so that
# structurally valid reclaim/retest and reversal families can still express
# evaluator-local truth in low-ADX range conditions.
_SCALP_RANGING_LOW_ADX_BLOCKED_FAMILIES: frozenset[str] = frozenset({
    "trend_following",
    "breakout_momentum",
    "continuation",
    "orderflow_momentum",
    # "divergence" removed: DIV_CONT sources direction from 1H EMA21/50 and
    # detects on 15m CVD — not from 5m momentum.  The evaluator's own
    # h1_trend_not_aligned hard-reject is the correct gate for this family.
    # Blocking on low-ADX ranging is redundant and incorrect post-HTF-refactor.
    # Fail closed for unmapped/new setup classes until explicitly classified.
    "other",
})

# Backstop exempt set for the RANGING-low-ADX family block.  The PRIMARY
# exemption is the htf_trend_aligned flag (see _is_scalp_family_blocked_in_ranging
# _low_adx) — it covers the whole trend-pullback family (TREND_PULLBACK_EMA on its
# 1H-trend path + MOVER_TREND_PULLBACK on the MA stack), which fires AT a pullback
# that reads RANGING/low-ADX on the entry TF by design while a higher timeframe IS
# trending.  This explicit set is a belt-and-suspenders backstop for a path that
# self-proves the move (the mover's MA7↔MA99 stack-separation gate) even if its
# htf_trend_aligned stamp is ever dropped in a refactor.  Family stays trend_
# following for SCORING affinity (#621); only the gate is exempt — §3.6a split.
_SCALP_RANGING_LOW_ADX_EXEMPT_SETUPS: frozenset[str] = frozenset({
    "MOVER_TREND_PULLBACK",
    "MOVER_AVWAP_SCALP",
})

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
#
# 2026-05-04 — KZ DISABLED ON 360_SCALP (B10 owner-approved).
# Truth-report soft-penalty breakdown showed KZ accounts for 80–100% of
# the aggregate `gate=` penalty across every filtered SCALP setup
# (LSR 96%, FAR 100%, SR_FLIP 94%, QCB 80%, DIV_CONT 100%).  KZ was
# inherited from session-traded asset doctrine; it deducts ~5–13 pts of
# confidence during "low-liquidity" hours that don't exist in 24/7
# crypto futures (Asia trading hours are very active, US-EU overlap is
# busy, every clock is someone's session).  Per OWNER_BRIEF §3.2 we are
# 24/7 scalpers — penalising signals for the time-of-day was doctrinally
# wrong.  Removing KZ from 360_SCALP is expected to lift LSR avg final
# 49.42 → 62.58 and unblock several-fold paid signal volume.  Other
# SCALP_* auxiliary channels keep KZ pending data on their behaviour.
# Reversible: flip back to True if quality degrades.
_CHANNEL_GATE_PROFILE: Dict[str, Dict[str, bool]] = {
    # SCALP channels: KZ disabled across the family — 24/7 crypto, no
    # session windows. Doctrine §3.2 ("we are 24/7 scalpers") means a
    # session-time penalty is structurally wrong for any of our scalp
    # variants. Originally only the main channel was flipped (2026-05-04)
    # because we wanted per-channel truth-report data first; aux channels
    # turned out to be too low-volume to ever produce that data, so we
    # apply the same doctrinal call uniformly.
    "360_SCALP":      {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_FVG":  {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_CVD":  {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_VWAP": {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_DIVERGENCE":  {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_SUPERTREND":  {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_ICHIMOKU":    {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
    "360_SCALP_ORDERBLOCK":  {"mtf": True,  "vwap": True,  "kill_zone": False, "oi": True,  "cross_asset": True,  "spoof": True,  "volume_div": True,  "cluster": True},
}

# Per-channel soft penalty base weights.
# These override the hard-coded defaults in _prepare_signal().
# Gates not listed use the original fallback values.
_CHANNEL_PENALTY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "360_SCALP":      {"vwap": 15.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 12.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_FVG":  {"vwap": 15.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 12.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_CVD":  {"vwap": 12.0, "kill_zone": 8.0,  "oi": 10.0, "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_VWAP": {"vwap": 18.0, "kill_zone": 8.0,  "oi": 6.0,  "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_DIVERGENCE":  {"vwap": 12.0, "kill_zone": 8.0,  "oi": 8.0,  "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_SUPERTREND":  {"vwap": 12.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 10.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_ICHIMOKU":    {"vwap": 10.0, "kill_zone": 8.0,  "oi": 8.0,  "volume_div": 10.0, "cluster": 10.0, "spoof": 10.0, "btc_dir": 6.0, "sym_dir": 6.0},
    "360_SCALP_ORDERBLOCK":  {"vwap": 12.0, "kill_zone": 10.0, "oi": 8.0,  "volume_div": 12.0, "cluster": 10.0, "spoof": 12.0, "btc_dir": 6.0, "sym_dir": 6.0},
}

# OWNER_BRIEF §2.1 — BTC direction soft penalty.  Top-75 USDT-M futures
# are heavily BTC-correlated; signals fighting BTC's macro 1H/4H trend
# get swept on the next BTC impulse.  Production data 2026-05-18 last-100
# window: 27% full-SL rate on LONG vs 7% on SHORT during a
# TRENDING_DOWN-skewed market.  Default base 6.0 pts mirrors the per-pair
# HTF mismatch pattern (``_SR_FLIP_HTF_MISMATCH_PENALTY`` and friends).
# Env-overridable per B8.
_BTC_DIRECTION_GATE_ENABLED: bool = os.getenv(
    "BTC_DIRECTION_GATE_ENABLED", "true"
).lower() in ("1", "true", "yes", "on")
_BTC_DIRECTION_PENALTY_BASE: float = float(
    os.getenv("BTC_DIRECTION_PENALTY_BASE", "6.0")
)
# Per-symbol direction gate: penalises signals that go against the pair's own
# 1H + 4H EMA trend.  Catches counter-trend trades on altcoins that are in a
# clear local downtrend/uptrend while BTC is range-bound (QUIET regime), which
# the BTC direction gate misses because BTC's own EMAs are flat in those periods.
# LSR and FAR are exempt — their thesis IS to trade against local structure.
_SYM_DIRECTION_GATE_ENABLED: bool = os.getenv(
    "SYM_DIRECTION_GATE_ENABLED", "true"
).lower() in ("1", "true", "yes", "on")
_SYM_DIRECTION_PENALTY_BASE: float = float(
    os.getenv("SYM_DIRECTION_PENALTY_BASE", "6.0")
)

# Counter-trend reversal / structure setups that fade trend — the paths that
# short a parabolic mover (SYNUSDT: LIQUIDITY_SWEEP_REVERSAL shorted +300%, full
# SL).  Only an instance whose DIRECTION opposes both the pair's 1H and 4H trend
# AND on a mover-grade move (wide EMA fan) is hard-blocked (Filter 1c); a trend-
# ALIGNED SR_FLIP/LSR, or a gently-trending pair, is untouched.  FAILED_AUCTION_
# RECLAIM is intentionally excluded — it is profitable in aggregate and rarely
# fires on a parabolic move; add it only if data shows it fading movers.
_COUNTERTREND_MOVER_BLOCKED_SETUPS: frozenset[str] = frozenset({
    "LIQUIDITY_SWEEP_REVERSAL",
    "SR_FLIP_RETEST",
})

# PR-7B: Path-aware modulation of soft-penalty base weights.
# Doctrine guardrails:
# - penalties are preserved (scale > 0)
# - hard gates are unchanged
# - modulation is narrow and explicit (path-targeted only)
_PENALTY_MODULATION_BY_SETUP: Dict[str, Dict[str, float]] = {
    # Top-emitter softening (PR-4, 2026-05-06).  Truth-report showed OI gate
    # contributed 91–100% of the soft-penalty stack on these three paths.
    # OI base=15 × 1.8 (QUIET regime mult) = 27 points — enough to push a
    # B-tier candidate (65) below threshold.  Doctrinal rationale per path:
    #   - LIQUIDITY_SWEEP_REVERSAL: counter-trend by design (§3.4).  When
    #     OI flips against direction, that's the crowd we're trading
    #     against — exactly the signal we want, not a penalty.  0.30
    #     keeps a small contributor for genuine outliers.
    #   - FAILED_AUCTION_RECLAIM: counter-trend / reclaim.  Same logic
    #     as LSR — OI mismatch confirms the auction failed against
    #     positioning.  0.30.
    #   - SR_FLIP_RETEST: structure / continuation.  Less aggressive than
    #     the counter-trend pair (OI agreement is more meaningful here),
    #     but the 27-point penalty still over-suppresses the dominant
    #     emitter.  0.50.
    "LIQUIDITY_SWEEP_REVERSAL": {"oi": 0.30},
    "SR_FLIP_RETEST": {"vwap": 0.60, "oi": 0.50},
    "FAILED_AUCTION_RECLAIM": {"vwap": 0.60, "oi": 0.30},
    "VOLUME_SURGE_BREAKOUT": {"volume_div": 0.60},
    "POST_DISPLACEMENT_CONTINUATION": {"volume_div": 0.65, "vwap": 0.80},
    "TREND_PULLBACK_EMA": {"kill_zone": 0.70},
    "CONTINUATION_LIQUIDITY_SWEEP": {"volume_div": 0.75},
    # QCB thesis = primary-TF compression breakout volume during a QUIET window
    # (higher-TF volume declining). That's the exact pattern volume_div is
    # designed to flag as manipulation, so the gate is structurally backward
    # for this path. Compression IS volume divergence — penalising it punishes
    # the setup for matching its own thesis.  At 0.60 the effective weight in
    # QUIET (1.8× regime mult) is ~1.08× base, i.e. essentially unchanged.
    # 0.20 brings effective QUIET weight to ~0.36× base, which preserves a
    # small contributor (so genuine outlier divergence still costs something)
    # while removing the structural penalty.
    "QUIET_COMPRESSION_BREAK": {"volume_div": 0.20},
}
_PENALTY_MODULATION_MIN_SCALE: float = 0.1
_PENALTY_MODULATION_MAX_SCALE: float = 1.0

# PR-6: Confluence-bonus tunables.
#
# When an entry price sits in a band where the multi-TF Level Book reports
# multiple distinct levels (≥0.30% tolerance — see level_book.CONFLUENCE_TOLERANCE_PCT),
# subtract a bonus from soft_penalty (= raise final confidence).  Magnitudes
# are calibrated against existing soft penalties:
#   - OI base (15) × 1.8 (QUIET) = 27 — single dominant gate
#   - Confluence-2 bonus (3 pts) ≈ 11% of that — a modest lift
#   - Confluence-4+ bonus (9 pts) ≈ 33% — meaningful, never enough to
#     unilaterally lift a sub-50 candidate to paid tier
#
# Refresh cadence: per-symbol TTL.  The LevelBook is rebuilt at most once
# per LEVEL_BOOK_REFRESH_SEC (default 1 hour) per symbol.  Discovery cost
# is < 100ms × 75 pairs = ~7.5s/hr amortised.
_CONFLUENCE_BONUS_BY_COUNT: Dict[int, float] = {
    2: 3.0,
    3: 6.0,
    4: 9.0,
}
_CONFLUENCE_BONUS_MAX: float = 9.0  # 4+ levels saturate at this bonus
_CONFLUENCE_QUERY_TOLERANCE_PCT: float = 0.30
LEVEL_BOOK_REFRESH_SEC: float = 3600.0  # rebuild per-symbol levels at most hourly

# PR-Wire: Structure-alignment bonus (PR-7 wiring).
# When a structure-aware path fires with its entry direction matching the
# 4h structure leg (HH/HL bull or LH/LL bear), award a small soft-penalty
# bonus.
#
# Allowlist widened 2026-05-08: diag + truth-report analysis showed 0% TP
# rate across the top-emitting setups (SR_FLIP_RETEST 28/28 closed at 0%
# wins, QUIET_COMPRESSION_BREAK 29/29 same).  The chartist-eye bonus was
# structurally barred from these paths so the lift never reached the
# signals carrying actual business volume — STRUCT_ALIGN fired on 0/3
# recent terminal samples in the diag.
#
# Eligibility:
# * Pure trend-following (TPE / DIV_CONT / CLS / PDC) — original allowlist.
# * Structure-aware with optional counter-trend (SR_FLIP / QCB) — these
#   already TAKE a soft penalty when fighting 4h structure (per the HTF
#   policy table); the symmetric counterpart is a small bonus when
#   aligned.  An SR_FLIP that flips a level and pushes WITH the structural
#   leg is the strongest version of that setup; same logic for a QCB
#   whose compression break direction matches the leg.
#
# Still excluded — counter-trend / tape-driven / break-event paths whose
# thesis is either deliberately counter-trend, internally direction-driven,
# or fires on structural break events where alignment is irrelevant:
# LSR / FAR / WHALE / FUNDING / LIQ_REVERSAL / VSB / BDS / ORB / MA_CROSS.
#
# Bonus value (3 pts) kept smaller than the max confluence bonus (9 pts)
# so the chartist-eye stack doesn't overweight either input.
_STRUCTURE_ALIGN_BONUS: float = 3.0
_STRUCTURE_ALIGN_PATHS: frozenset = frozenset({
    "TREND_PULLBACK_EMA",
    "DIVERGENCE_CONTINUATION",
    "CONTINUATION_LIQUIDITY_SWEEP",
    "POST_DISPLACEMENT_CONTINUATION",
    "SR_FLIP_RETEST",
    "QUIET_COMPRESSION_BREAK",
})

# Structure-MISALIGNMENT penalty (PR 2026-05-20).  The existing
# ``_STRUCTURE_ALIGN_BONUS`` is asymmetric — alignment gets rewarded,
# misalignment gets nothing.  Truth-report 2026-05-20 found
# DIVERGENCE_CONTINUATION has the highest SL rate (30% on n=10) AND
# the most-degraded avg-PnL window-over-window (-0.30) of all active
# paths.  DIV_CONT's eval-stage funnel filters 98% of attempts but
# the confidence gate then passes 95% of the residual — the gate
# does almost no work.  Hypothesis: marginal kept-signals are
# DIV_CONTs entering against the 4h structural leg, fighting the
# higher-TF trend with no HTF-structure penalty to suppress them.
#
# This penalty is the symmetric counterpart to the bonus.  When the
# 4h structure exists with sufficient confidence AND opposes signal
# direction (BULL_LEG + SHORT or BEAR_LEG + LONG), apply a small
# soft penalty.  ``RANGE`` and below-confidence states are exempt
# (the structural read is too weak to penalise on).
#
# Per-path enrolment via ``_STRUCTURE_MISALIGN_PATHS`` so the
# blast-radius stays narrow — only DIV_CONT enrols at first.  Other
# paths can be added once a window's worth of telemetry validates
# the penalty's behaviour.
#
# Magnitude 5.0 calibration: with DIV_CONT avg-final 72.11 on KEPT
# signals and 65.0 threshold, +5 brings the marginal kept-signals
# (final 65-70, ~30% of KEPTs based on the dispersion in the truth
# report) below threshold while leaving high-conviction signals
# (final 70+) safely above.  Env-overridable per B8.
_STRUCTURE_MISALIGN_PENALTY: float = float(
    os.getenv("STRUCTURE_MISALIGN_PENALTY", "5.0")
)
_STRUCTURE_MISALIGN_PATHS: frozenset = frozenset({
    "DIVERGENCE_CONTINUATION",
})

# Per-(symbol, setup_class, direction) dispatch cooldown.  Default 30 min
# is short enough to allow re-fires when conditions materially change but
# long enough to prevent the exact same setup from re-detecting every
# 15s scan cycle.  Bug observed 2026-05-07: 5 identical
# FAILED_AUCTION_RECLAIM signals dispatched on BNBUSDT in 5h, all
# immediately invalidating at SL.  Cooldown persisted to disk so a
# redeploy doesn't let duplicates through.
# Gate audit (2026-07-19) read dispatch_cooldown DROP: 312 blocked, 100%
# would-win, 235.1R missed, EV −0.75 — the 30-min window blocked profitable
# re-entries on continuing moves.  Default lowered to 15 min and made a live
# ops tunable (dispatch_cooldown_sec / dispatch_cooldown_enabled) so the owner
# tunes it off the audit with no redeploy; still guards against 15s
# bit-identical re-emission spam.  Env default kept env-overridable per B8.
from config import (  # noqa: E402
    DISPATCH_COOLDOWN_ENABLED,
    DISPATCH_COOLDOWN_SEC,
)
DISPATCH_COOLDOWN_PATH: str = "data/signal_dispatch_cooldown.json"


def _dispatch_cooldown_enabled() -> bool:
    """Cooldown off-switch: an explicit ops override wins; otherwise the module
    global (env/config default, and monkeypatch-compatible for tests)."""
    try:
        from src import runtime_tunables as _rt
        _v = _rt.get("dispatch_cooldown_enabled")
        _reg = _rt.registry().get("dispatch_cooldown_enabled")
        if _v is not None and _reg is not None and bool(_v) != bool(_reg.default):
            return bool(_v)  # genuine ops override
    except Exception:
        # Tunable-read fallback (not a data path) — use the module global.
        return bool(DISPATCH_COOLDOWN_ENABLED)
    return bool(DISPATCH_COOLDOWN_ENABLED)


def _dispatch_cooldown_sec() -> float:
    """Re-emission window (s): an explicit ops override wins; otherwise the module
    global (env/config default, and monkeypatch-compatible for tests)."""
    try:
        from src import runtime_tunables as _rt
        _v = _rt.get("dispatch_cooldown_sec")
        _reg = _rt.registry().get("dispatch_cooldown_sec")
        if _v is not None and _reg is not None and float(_v) != float(_reg.default):
            return float(_v)  # genuine ops override
    except Exception:
        # Tunable-read fallback (not a data path) — use the module global.
        return float(DISPATCH_COOLDOWN_SEC)
    return float(DISPATCH_COOLDOWN_SEC)

# Consecutive-loss streak registry (2026-07-09, dark-flagged escalation).
# Mirrors DISPATCH_COOLDOWN_PATH's atomic-write persistence pattern.
LOSS_STREAK_PATH: str = "data/loss_streaks.json"

# Level-rearm state-machine persistence path.  See LEVEL_REARM_* knobs in
# config/__init__.py.  Mirrors DISPATCH_COOLDOWN_PATH atomic-write pattern.
LEVEL_IN_PLAY_PATH: str = "data/level_in_play.json"

# Pre-dispatch staleness check.  Reject if real-time price has drifted
# more than this percentage from the entry price between setup detection
# and dispatch.  At 0.5% the check is gentle — allows normal mid-candle
# drift but catches the "entry says 626.85 but current price is already
# at 631.86 (SL)" pathology from the 2026-05-07 bug.  Env-overridable
# per B8 if we need to tune.
DISPATCH_STALENESS_MAX_DRIFT_PCT: float = 0.5

# Structure-readiness gate (2026-05-11): structure-based evaluators
# require an aged multi-TF level foundation.  Pairs whose LevelBook
# entry has fewer than this many 1d-anchored levels are deemed
# "structurally young" and get restricted to the breakout-/event-family
# allowlist (see _YOUNG_PAIR_EVALUATORS below).  Default 5 is calibrated
# against the LevelBook config: 1d swing-pivot detection needs ~3 weeks
# of 1d candles to produce 5+ distinct levels reliably; a 2-day-old
# listing won't reach this threshold and shouldn't be running SR_FLIP /
# FAR / QCB / TPE etc. on nascent structure.
MIN_1D_LEVELS_FOR_STRUCTURE_PATHS: int = int(
    os.getenv("MIN_1D_LEVELS_FOR_STRUCTURE_PATHS", "5")
)

# Evaluators whose thesis does NOT require aged multi-TF structure:
# breakout family (price-driven), tape/order-flow family (cascade- and
# whale-driven), funding family (rate-driven).  These can safely fire
# on freshly-promoted pairs.  Anything not in this set is structure-
# based and falls under the structure-readiness gate.
_YOUNG_PAIR_EVALUATORS: frozenset[str] = frozenset({
    "_evaluate_volume_surge_breakout",
    "_evaluate_breakdown_short",
    "_evaluate_opening_range_breakout",
    "_evaluate_whale_momentum",
    "_evaluate_liquidation_reversal",
    "_evaluate_funding_extreme",
    # Mover continuation — price-driven (MA stack), no aged structure needed.
    # Real movers (BTW/ESPORTS) arrive as young/universe pairs, so the path
    # MUST be young-pair-safe to reach them.
    "_evaluate_mover_trend_pullback",
    # AVWAP mover scalp — same: anchored-VWAP reference, no aged HTF structure.
    "_evaluate_mover_avwap_scalp",
    # _evaluate_mean_revert is DELIBERATELY absent: the z-score needs a stable
    # 20-bar statistical mean, and a fresh listing's distribution is a
    # one-sided ramp — the "extension" would just be the listing move itself.
    # _evaluate_range_fade is DELIBERATELY absent for the same reason: a
    # "range" on a fresh listing is 12h of listing ramp, not tested structure.
})

def _range_fade_context_allowed(verdict: str) -> bool:
    """Pure eligibility rule for the RANGE_FADE context-edge gate.

    Mirrors the allocator's own promotion rule (``strategy_allocator``):
    a context cell must carry a measured Wilson-bound verdict to emit —
    STRONG always qualifies; POSITIVE only when the operator relaxed
    ``RANGE_FADE_CONTEXT_MIN_VERDICT`` to "positive".  Everything else
    (NEGATIVE / FLAT / INSUFFICIENT_DATA / unknown) blocks: an unverified
    edge is not an edge, and the shadow arm keeps measuring the cell so a
    context that turns STRONG self-unlocks without a deploy.
    """
    from src.strategy_edge import VERDICT_POSITIVE, VERDICT_STRONG

    if verdict == VERDICT_STRONG:
        return True
    return (
        RANGE_FADE_CONTEXT_MIN_VERDICT == "positive"
        and verdict == VERDICT_POSITIVE
    )


# PR-7C: runtime validation focus paths for concise operator summaries.
_PR7C_TARGET_SETUPS: frozenset[str] = frozenset({
    "SR_FLIP_RETEST",
    "FAILED_AUCTION_RECLAIM",
    "TREND_PULLBACK_EMA",
    "VOLUME_SURGE_BREAKOUT",
    "POST_DISPLACEMENT_CONTINUATION",
    "CONTINUATION_LIQUIDITY_SWEEP",
})
# PR-13: Evidence-gated specialist/internal reactivation review scope.
# These paths are reviewed explicitly from runtime funnel truth only; no
# automatic promotion is allowed from this summary.
_PR13_SPECIALIST_REVIEW_SETUPS: frozenset[str] = frozenset({
    "WHALE_MOMENTUM",
    "FUNDING_EXTREME_SIGNAL",
    "QUIET_COMPRESSION_BREAK",
})
_PR13_GOVERNANCE_DISABLED_REVIEW_SETUPS: frozenset[str] = frozenset({
    "OPENING_RANGE_BREAKOUT",
})
_EVAL_PATH_PREFIX = "EVAL::"
_DEPENDENCY_ABSENCE_REASON_TOKENS: frozenset[str] = frozenset({
    "missing_funding_rate",
    "missing_cvd",
    "missing_recent_ticks",
    "missing_order_book",
    "missing_liquidation_clusters",
})


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
    A signal-tier classifier returning ``"A+"`` (≥80) / ``"B"`` (65-79) /
    ``"FILTERED"`` (< 65).

    The WATCHLIST tier (50-64 → free channel preview) was removed in the
    app-era doctrine reset: subscribers consume signals via the Lumin app,
    not the Telegram free channel, and watchlist previews were producing
    spammy free-channel volume with negligible paid-conversion value.
    Sub-65 confidence now drops cleanly.
    """
    if confidence >= 80:
        return "A+"
    elif confidence >= 65:
        return "B"
    return "FILTERED"


@dataclass
class LevelInPlayState:
    """Per-(symbol, direction, level_bucket) state for the level-rearm
    state machine — see ``Scanner._check_and_record_level_in_play``.

    Frozen at dispatch; only ``max_excursion_pct`` mutates over time as
    live price walks away from the level.  When ``max_excursion_pct``
    crosses ``threshold_pct``, the entry is dropped and the level is
    re-armed for the next genuine retest.
    """
    level_price: float          # exact entry/level at dispatch
    dispatched_at: float        # time.time() at dispatch
    threshold_pct: float        # SL-distance-derived, clamped to floor/ceiling
    max_excursion_pct: float = 0.0  # max |price - level| / level since dispatch


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

        # Multi-TF Level Book (PR-5).  Auto-discovers and scores S/R levels
        # per symbol from 1d/4h/1h candles plus round numbers.  Refreshed
        # lazily per symbol with a TTL so we don't re-scan every cycle.
        # PR-6 wires confluence_count() into the soft-penalty stack as a bonus.
        self.level_book: LevelBook = LevelBook()
        self._level_book_refresh_ts: Dict[str, float] = {}

        # Per-(symbol, setup_class, direction) dispatch cooldown.  Same
        # signal shouldn't re-fire within COOLDOWN_SEC after a successful
        # dispatch — bug observed 2026-05-07: identical FAILED_AUCTION_RECLAIM
        # signal dispatched 5x on BNBUSDT in 5 hours, all instant-SL'd.
        # Persisted to data/signal_dispatch_cooldown.json so a redeploy
        # within the cooldown window doesn't let duplicates through.
        self._dispatch_cooldown: Dict[tuple, float] = {}
        self._load_dispatch_cooldown()

        # Per-(symbol, setup_class, direction) consecutive-loss streaks
        # (2026-07-09, dark-flagged).  Fed by on_signal_lifecycle_outcome;
        # when the loss_streak_escalation_enabled tunable is ON, the
        # lifecycle cooldown extension doubles per consecutive losing
        # outcome (capped) so the scanner stops re-entering the same
        # failing setup every time the flat cooldown lapses (MONUSDT
        # MVRTP LONG: 6 dispatches / −3.7% in 3 days).  Persisted next to
        # the dispatch cooldown so restarts don't reset streaks.
        self._loss_streaks: Dict[tuple, int] = {}
        self._load_loss_streaks()

        # Per-symbol throttle for the promoted-mover candle re-seed
        # (``_refresh_stale_mover_candles``, 2026-07-10) — monotonic ts of
        # the last refresh ATTEMPT per symbol.
        self._mover_last_reseed: Dict[str, float] = {}

        # Per-(symbol, direction, level_bucket) "level in play" registry —
        # see _check_and_record_level_in_play.  Blocks stuck-level repeat-
        # fires from level-anchored evaluators (SR_FLIP_RETEST / VSB /
        # BDS / FAR) until price has decisively travelled away from the
        # level.  Bug observed 2026-05-13: ETHUSDT SR_FLIP SHORT
        # dispatched 13× over 26h at identical entry 2305.32 while price
        # chopped ±0.3% around the level (68% of paid emission was
        # duplicates of 4 stuck levels).  Persisted to
        # data/level_in_play.json so the suppression survives redeploys.
        # NOTE: setup_class is intentionally omitted from the key —
        # different evaluators may detect the same level (e.g. VSB and
        # SR_FLIP both anchoring on the same swing high); one being
        # in-play should suppress the other, because chop is chop
        # regardless of which detector spotted it.
        self._level_in_play: Dict[Tuple[str, str, float], LevelInPlayState] = {}
        self._load_level_in_play()

        # Volume Profile (PR-9) — POC/VAH/VAL per symbol.  Same TTL pattern
        # as LevelBook.  POC/VAH/VAL injected into LevelBook on each
        # refresh so confluence scoring picks them up automatically.
        # Two scopes:
        #   - "micro": 1h candles, last 200 bars (~8 days) — short-window POC
        #   - "macro": 1d candles, last 200 bars (~6 months) — multi-week
        #     accumulation zones a chartist sees on the daily chart
        # Both contribute their POC/VAH/VAL into LevelBook on refresh.
        self.volume_profile_store: VolumeProfileStore = VolumeProfileStore()
        self.volume_profile_store_macro: VolumeProfileStore = VolumeProfileStore()

        # Structure Tracker (PR-7) — bull leg / bear leg / range per (symbol, tf).
        # Used by trend-aligned paths (TPE / DIV_CONT / CLS / PDC) to award
        # a small soft-penalty bonus when entry direction aligns with the
        # 4h structure leg.
        self.structure_tracker: StructureTracker = StructureTracker()

        # Mutable state shared with the engine / command handler
        self.paused_channels: Set[str] = set()
        self.confidence_overrides: Dict[str, float] = {}
        self.force_scan: bool = False

        # WebSocket manager (set after boot)
        # 2026-05-14: ws_spot removed — engine is futures-only per CLAUDE.md.
        self.ws_futures: Optional[Any] = None

        # Real-time mover-ignition queue (set after boot) — a shared
        # ``{symbol: direction}`` dict the WS handler fills and
        # ``_update_movers_promotion`` drains each cycle. ``None`` ⇒ the
        # ignition path is not wired (falls back to the 24h-%change trigger).
        self.mover_ignition_pending: Optional[Dict[str, str]] = None
        # The ignition detector itself (set after boot) — its !ticker@arr feed is
        # the ONLY source that sees the full ~600-pair futures universe, so both
        # promotion sources (ignition + top-24h movers) read it to reach pairs
        # outside the engine's top-75 pair_mgr scan set.
        self.mover_ignition_detector: Optional[Any] = None
        # Symbols we synthetically admitted into pair_mgr.pairs to scan a mover
        # from outside the top-75 universe; removed when their promotion expires.
        self._synthetic_mover_pairs: set = set()

        # Optional circuit breaker (set after construction)
        self.circuit_breaker: Optional[Any] = None

        # Optional gem scanner (set after construction)
        self.gem_scanner: Optional[Any] = None

        # Order book spread cache: symbol → (spread_pct, expiry_monotonic_time)
        # expiry_monotonic_time is an absolute time.monotonic() value; the entry
        # is valid while time.monotonic() < expiry_monotonic_time.
        self._order_book_cache: Dict[str, Tuple[float, float]] = {}
        # Lightweight order-book snapshot cache sourced from global bookTicker:
        # symbol → ({"bids": [[price, qty]], "asks": [[price, qty]]}, expiry).
        # This is not full depth, but it provides a truthful top-of-book snapshot
        # for evaluator paths that consume order_book.
        self._order_book_snapshot_cache: Dict[str, Tuple[Dict[str, Any], float]] = {}
        # Timestamp of the last successful bookTicker pre-fetch.  Used to gate
        # the API call: we only re-fetch when the cache is actually stale, not
        # every 1-second scan cycle.  0.0 = never fetched → fetch immediately.
        self._last_book_ticker_fetch_at: float = 0.0

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
        # Per-cycle regime classification counts, cleared and emitted every 100
        # scan cycles. Surfaces the regime distribution to the runtime truth
        # report so operators can confirm e.g. "market is 99.7% QUIET" from
        # structured data instead of grepping debug logs.
        self._regime_cycle_counts: Dict[str, int] = defaultdict(int)
        # Per-symbol regime classification counts (2026-05-23 telemetry).
        # Answers: does a given symbol live in QUIET vs TRENDING vs VOLATILE
        # over the window? Needed to validate the symbol-class bonus: narrative
        # pairs should spend more cycles in TRENDING; tokenized stocks should
        # spend more in QUIET. Cleared and re-emitted every 100 cycles.
        self._regime_cycle_by_symbol: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        # Semaphore to limit concurrent symbol scans
        self._scan_semaphore: asyncio.Semaphore = asyncio.Semaphore(_MAX_CONCURRENT_SCANS)

        # Per-cycle stage-timing accumulator (diagnostic). Summed wall-time per
        # stage across all concurrent symbol scans in a cycle; cleared at the
        # start of each cycle and logged at the end when SCAN_STAGE_TIMING_ENABLED.
        # Mutated only from coroutine steps on the single event loop, so the
        # plain += needs no lock.
        self._stage_timing: Dict[str, float] = defaultdict(float)

        # Dedicated thread pool for all CPU-bound scan work: _compute_indicators,
        # smc_detector.detect, and chan.evaluate calls.  Isolated from the default
        # asyncio executor so that saturating it never starves auth/DB threads.
        # Running these synchronous operations in threads keeps the event loop
        # free so HTTP request handlers are never blocked by scan work.
        #
        # Thread count: governed by SCAN_EXECUTOR_WORKERS (env-overridable,
        # default 2× cpu_count). Capped at _MAX_CONCURRENT_SCANS.  With the
        # SMC+indicator caches warm, most cycles submit few executor tasks
        # (only pairs whose candle counts changed), so the default is sufficient.
        # Raise via .env if profiling shows sustained executor queue depth.
        from concurrent.futures import ThreadPoolExecutor as _TPE
        self._scan_executor = _TPE(
            max_workers=SCAN_EXECUTOR_WORKERS,
            thread_name_prefix="scanner-compute",
        )

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
        # Monotonic (never cleared) MEAN_REVERT emission counter feeding the
        # mean_revert_emission liveness probe — the rolling funnel counters
        # above are flushed periodically so they can't drive a probe.
        self._mean_revert_emitted_total: int = 0
        # RANGE_FADE monotonic counters (same probe contract): emissions, and
        # context-edge-gate blocks.  The emission probe treats a context block
        # as proof the path is alive — a RANGE_FADE candidate legitimately
        # dies here whenever the current context cell isn't measured
        # POSITIVE/STRONG, which can hold for many hours.
        self._range_fade_emitted_total: int = 0
        self._range_fade_context_blocked_total: int = 0
        # Context-adaptive emission policy (Layer C consumer) monotonic counters:
        # every candidate the policy evaluated, and the four divergence outcomes
        # vs the global floor (would-emit = relax opportunity, would-suppress =
        # measured-losing cell, applied = live floor actually moved/suppressed).
        # Drive the context_emission liveness probe + Strategy Lab telemetry.
        self._context_floor_evaluated_total: int = 0
        self._context_floor_would_emit_total: int = 0
        self._context_floor_would_suppress_total: int = 0
        self._context_floor_applied_total: int = 0

        # Scoring tier telemetry: accumulates candidate counts per setup_class
        # and score tier across cycles; logged every 100 scan cycles to diagnose
        # funnel distribution across paths.
        self._scoring_tier_counters: Dict[str, int] = defaultdict(int)
        # Scoring distribution telemetry: pre-penalty vs post-penalty score
        # bands and tiers by channel/family/path for PR-7A runtime validation.
        self._scoring_distribution_counters: Dict[str, int] = defaultdict(int)
        # PR-7B telemetry: explicit penalty modulation usage by gate/path/family.
        self._penalty_modulation_counters: Dict[str, int] = defaultdict(int)
        # PR-7C telemetry: concise target-path migration and penalty-hit summaries.
        self._target_path_tier_migration_counters: Dict[str, int] = defaultdict(int)
        self._target_path_penalty_gate_counters: Dict[str, int] = defaultdict(int)

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

        # Shadow-strategy stamp cooldown: last stamp (monotonic) per
        # (unit, symbol) so a persisting condition (e.g. price parked at a
        # range edge) yields one ledger entry per window, not one per 15s scan.
        self._shadow_last_stamp: Dict[Tuple[str, str], float] = {}

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

        # Regime Kill Switch: blocks new signals when BTC is in whipsaw.
        # See src/regime_kill_switch.py for detection algorithm and tuning.
        from src.regime_kill_switch import BtcRegimeKillSwitch
        self._regime_kill_switch: BtcRegimeKillSwitch = BtcRegimeKillSwitch()

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

        # Indicator result cache, keyed PER TIMEFRAME: symbol → {tf: (len, ind_dict)}.
        # Per-timeframe so a new 1m candle (every ~cycle) doesn't invalidate the
        # higher-timeframe indicators that haven't changed.  Each tf entry hits
        # until that tf's candle count changes (i.e. its bar closes).
        self._indicator_cache: Dict[str, Dict[str, tuple]] = {}
        # SMC result cache: symbol → (fingerprint, SMCResult).
        # Fingerprint: closed-candle counts for 5m+ timeframes only.
        # Structural sweeps/FVGs/orderblocks are deterministic on completed
        # candles → cache stable for ~20 cycles between 5m candle closes.
        self._smc_cache: Dict[str, tuple] = {}

        # PR8: Dynamic pair promotion — volume baseline tracker and promoted pairs
        # symbol → last known 24h volume (used to detect surge events)
        self._volume_baseline: Dict[str, float] = {}
        # symbol → cycles remaining (non-scan pairs temporarily added to universe)
        self._promoted_pairs: Dict[str, int] = {}
        # Movers promotion: symbol → cycles remaining for pairs promoted by 24h % change.
        # These are scanned with a RESTRICTED evaluator set (VSB + BREAKDOWN_SHORT only).
        self._mover_promoted_pairs: Dict[str, int] = {}

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
            # len() not truthiness — these are numpy arrays, and `not arr`
            # raised on every symbol WITH data (numpy-truthiness class,
            # 2026-07-14), breaking pair diagnosis entirely.
            if len(closes_5m) == 0:
                results["error"] = f"No 5m candle data for {symbol}"
                return results

            _candle_dict_for_ind: dict = {
                tf: candles[tf] for tf in ("1m", "5m", "15m", "1h") if tf in candles
            }
            indicators: dict = compute_indicators_for_candle_dict(_candle_dict_for_ind)

            ind5 = indicators.get("5m", {})

            # Use the same data sources as the live scan path.  The previous
            # implementation called data_store.get_spread/get_volume/get_regime/
            # get_smc — none of which exist on HistoricalDataStore — so the whole
            # diagnostic returned an AttributeError string instead of gate data.
            info = self.pair_mgr.pairs.get(symbol)
            market = info.market if info is not None else "spot"
            volume_24h = float(getattr(info, "volume_24h_usd", 0.0) or 0.0)
            spread_pct = await self._get_spread_pct(symbol, market=market) or 0.0

            # Regime via the per-symbol RegimeService.  Prefer the cached result
            # from the last scan cycle; fall back to a fresh classification so a
            # pair that has not been scanned this run still reports a real regime.
            regime_result = None
            get_regime = getattr(self.regime_detector, "get_regime", None)
            if get_regime is not None:
                regime_result = get_regime(symbol)
            if regime_result is None:
                _pair_tier = getattr(
                    classify_pair_tier(symbol, volume_24h_usd=volume_24h), "tier", "MIDCAP"
                )
                regime_result = self.regime_detector.classify(
                    ind5, candles.get("5m"), timeframe="5m",
                    symbol=symbol, pair_tier=_pair_tier,
                )
            _regime_enum = getattr(regime_result, "regime", None)
            regime = getattr(_regime_enum, "value", "RANGING") if _regime_enum else "RANGING"

            # SMC via the detector, mirroring _build_scan_context.
            ticks = self.data_store.ticks.get(symbol, [])
            smc_result = self.smc_detector.detect(
                symbol, candles, ticks, self.order_flow_store,
                lookback=SMC_SCALP_LOOKBACK,
                tolerance_pct=SMC_SCALP_TOLERANCE_PCT,
            )
            smc_data = smc_result.as_dict() if smc_result is not None else {}

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

    async def _seed_mover_pair(self, symbol: str, info: Any) -> bool:
        """Backfill candles + CVD for a freshly-promoted mover pair.

        Mover pairs sit outside the boot-time `seed_all()` universe and outside
        the WS subscription set, so without an on-promotion REST seed every
        evaluator fails on insufficient_candles for the entire 5-cycle TTL.

        Pulls the standard 6-timeframe candle backfill (mirrors
        `main.py:708` new-pair seed pattern) and the historical CVD seed
        (mirrors `bootstrap.py:177`). Returns True on success — caller must
        skip promotion if False so we don't burn telemetry on a dead pair.
        """
        try:
            await self.data_store.seed_symbol(symbol, info.market)
        except Exception as exc:
            log.warning("mover seed failed for {}: {}", symbol, exc)
            return False

        sym_candles = self.data_store.candles.get(symbol, {})
        c5 = sym_candles.get("5m", {})
        if not c5 or len(c5.get("close", [])) < 28:
            log.warning(
                "mover seed insufficient for {}: 5m={} candles — skip promotion",
                symbol, len(c5.get("close", [])) if c5 else 0,
            )
            return False

        for tf_name, data in sym_candles.items():
            self.pair_mgr.record_candles(symbol, tf_name, len(data.get("close", [])))

        if self.order_flow_store is not None:
            kl_1m = sym_candles.get("1m", {})
            tbv = kl_1m.get("taker_buy_vol_usd")
            vusd = kl_1m.get("volume_usd")
            if tbv is not None and vusd is not None and len(tbv) > 0:
                try:
                    self.order_flow_store.seed_cvd_from_klines(symbol, tbv, vusd)
                except Exception as exc:
                    log.debug("mover CVD seed failed for {}: {}", symbol, exc)

        return True

    def _ensure_mover_pair(
        self, symbol: str, change_pct: Optional[float] = None, vol: Optional[float] = None,
    ) -> Optional["PairInfo"]:
        """Return the ``pair_mgr`` entry for *symbol*, admitting it if absent.

        Movers worth scalping (a −40% alt) usually sit OUTSIDE the engine's
        top-75 ``pair_mgr`` universe (``TOP50_FUTURES_ONLY``), so the old
        ``pair_mgr.pairs.get`` gate silently dropped every one. The detector's
        ``!ticker@arr`` meta carries the 24h %change + volume for the whole
        universe; use it to synthesise a TIER3 ``PairInfo`` so the pair can be
        seeded + scanned. Removed again when its promotion expires.
        """
        info = self.pair_mgr.pairs.get(symbol)
        if info is not None:
            return info
        # Blacklist gate — the ``!ticker@arr`` feed covers the WHOLE board,
        # including tokenized stocks / commodities / stablecoins that
        # pair_manager's fetch paths exclude by design (Class-C misfits,
        # docs/SYMBOL_CLASS_RESEARCH_2026_05_23.md).  Without this check the
        # mover path re-admits them around every filter: SAMSUNG/HOOD/COIN/
        # QCOM/PLTR-style equity perps were promoted, scanned, and emitted
        # to the paid channel in the 2026-07-01..03 window.
        if symbol in _SYMBOL_BLACKLIST or symbol in _MOVER_UNIVERSE_BLACKLIST:
            log.debug("mover admission blocked (blacklist): {}", symbol)
            return None
        if (change_pct is None or vol is None) and self.mover_ignition_detector is not None:
            m = self.mover_ignition_detector.meta(symbol)
            if m is not None:
                change_pct = m[0] if change_pct is None else change_pct
                vol = m[1] if vol is None else vol
        if change_pct is None or vol is None or vol <= 0:
            return None
        info = PairInfo(
            symbol=symbol,
            market="futures",
            volume_24h_usd=float(vol),
            tier=PairTier.TIER3,
            volatility_24h=abs(float(change_pct)),
        )
        self.pair_mgr.pairs[symbol] = info
        self._synthetic_mover_pairs.add(symbol)
        return info

    async def _update_movers_promotion(self, sorted_pairs_set: set) -> List[str]:
        """Promote non-scanned movers into the scan universe — TWO sources.

        Mover capture has two complementary triggers, both feeding the same 6 h
        hold so VSB/BDS/MOVER_TREND_PULLBACK get repeated chances to scalp:

        1. **Ignition** (``mover_ignition_pending`` wired ⇒ ``MOVER_IGNITION_ENABLED``)
           — real-time bursts off ``!ticker@arr``: a pair accelerating *now*,
           caught at minute-zero of a sudden move.
        2. **Top 24h movers** (``volatility_24h >= MOVER_PROMOTION_MIN_PCT``) —
           sustained directional trends (e.g. a pair −40 % on the day, grinding
           down its MA stack) that have no single 30 s burst but are clearly
           movers. The detector alone misses these; the three paths exist to
           scalp exactly this kind of trend.

        Promotion is deliberately *inclusive* — the evaluators' own gates
        (freshness ceiling, MA-stack alignment, exhaustion guard) decide entry
        quality, so an exhausted mover gets promoted but never traded. Newly-
        promoted symbols are REST-seeded (candles + CVD) before being added.

        Returns the list of currently mover-promoted symbols.
        """
        now_mono = time.monotonic()
        candidates: List[tuple[str, Any]] = []
        ignition_dirs: Dict[str, str] = {}
        seen: set = set()
        det = self.mover_ignition_detector
        # Bound seeding cost: stop collecting candidates once promoted+pending
        # would exceed the concurrent-mover cap (each new candidate costs one
        # REST seed). universe_movers is sorted |%| desc, so we take the biggest.
        _budget = max(0, MOVER_PROMOTION_MAX_PAIRS - len(self._mover_promoted_pairs))

        # Source 1 — real-time ignition (sudden bursts), if wired.
        pending = self.mover_ignition_pending
        if pending is not None:
            drained = dict(pending)
            pending.clear()
            for symbol, direction in drained.items():
                if symbol in sorted_pairs_set:
                    self._mover_promoted_pairs.pop(symbol, None)
                    continue
                if symbol in self._mover_promoted_pairs:
                    continue
                # Admit the pair even if it's outside the top-75 pair_mgr set —
                # an igniting mover is exactly the pair we don't already scan.
                info = self._ensure_mover_pair(symbol)
                if info is None or info.volume_24h_usd < MOVER_PROMOTION_MIN_VOLUME_USD:
                    continue
                ignition_dirs[symbol] = direction
                candidates.append((symbol, info))
                seen.add(symbol)

        # Source 2 — top 24h movers across the FULL universe. The detector's
        # !ticker@arr feed sees ~600 pairs; pair_mgr only tracks the top 75, so
        # reading from pair_mgr alone (the old behaviour) could never reach a
        # low-volume / high-%move pair like a −40% alt — the whole point.
        if det is not None:
            movers = det.universe_movers(MOVER_PROMOTION_MIN_PCT, MOVER_PROMOTION_MIN_VOLUME_USD)
        else:
            movers = [
                (s, i.volatility_24h, i.volume_24h_usd)
                for s, i in self.pair_mgr.pairs.items()
                if i.volatility_24h >= MOVER_PROMOTION_MIN_PCT
                and i.volume_24h_usd >= MOVER_PROMOTION_MIN_VOLUME_USD
            ]
        for symbol, change_pct, vol in movers:
            if len(candidates) >= _budget:
                break
            if symbol in sorted_pairs_set:
                self._mover_promoted_pairs.pop(symbol, None)
                continue
            if symbol in self._mover_promoted_pairs or symbol in seen:
                continue
            info = self._ensure_mover_pair(symbol, change_pct, vol)
            if info is None or info.volume_24h_usd < MOVER_PROMOTION_MIN_VOLUME_USD:
                continue
            candidates.append((symbol, info))
            seen.add(symbol)

        if candidates:
            seed_results = await asyncio.gather(
                *[self._seed_mover_pair(sym, info) for sym, info in candidates],
                return_exceptions=False,
            )
            _hold_h = MOVER_PROMOTION_TTL_SEC / 3600.0
            for (symbol, info), seeded in zip(candidates, seed_results):
                if not seeded:
                    continue
                if symbol in ignition_dirs:
                    log.info(
                        "🔥 MOVER IGNITION: {} {} vol={:.0f} — VSB/BREAKDOWN scan for {:.1f}h",
                        symbol, ignition_dirs[symbol], info.volume_24h_usd, _hold_h,
                    )
                else:
                    log.info(
                        "📈 MOVER PROMOTION: {} {:.1f}% vol={:.0f} — VSB/BREAKDOWN scan for {:.1f}h",
                        symbol, info.volatility_24h, info.volume_24h_usd, _hold_h,
                    )
                # Store the monotonic EXPIRY time (now + TTL). The pair stays in
                # the scan universe until this elapses (default 6 h) so the mover
                # evaluators get repeated chances to find an entry as the move
                # develops — not a ~25 s cycle-count window. Re-igniting an
                # already-promoted pair refreshes its expiry (handled by the
                # ``symbol in self._mover_promoted_pairs`` skip above keeping the
                # original; a fresh ignition after expiry restamps it).
                self._mover_promoted_pairs[symbol] = now_mono + MOVER_PROMOTION_TTL_SEC

        # Evict pairs that entered the main scan, or whose promotion TTL elapsed.
        # A synthetically-admitted pair (one we added to pair_mgr to scan it) is
        # also removed from pair_mgr so the tracked universe doesn't grow unbounded.
        for sym in list(self._mover_promoted_pairs.keys()):
            if sym in sorted_pairs_set or now_mono >= self._mover_promoted_pairs[sym]:
                del self._mover_promoted_pairs[sym]
                if sym in self._synthetic_mover_pairs:
                    self.pair_mgr.pairs.pop(sym, None)
                    self._synthetic_mover_pairs.discard(sym)

        # Cap concurrently-scanned movers, freshest first (largest expiry =
        # most-recently promoted) so new ignitions are never starved by stale holds.
        active = sorted(
            (s for s in self._mover_promoted_pairs if s not in sorted_pairs_set),
            key=lambda s: self._mover_promoted_pairs[s], reverse=True,
        )
        active = active[:MOVER_PROMOTION_MAX_PAIRS]

        # Keep the scanned movers' candles LIVE for the rest of their hold
        # (2026-07-10).  Promoted pairs have no WS kline subscription — the
        # one-time promotion seed was the only candle write, so minutes into
        # the 6 h TTL every evaluator read frozen data, entries were computed
        # off stale closes, and once REST seeds started stamping freshness the
        # dispatch staleness gate would (rightly) block them.  Re-seed any
        # active mover whose 1m candle age exceeds MOVER_CANDLE_REFRESH_SEC,
        # throttled per symbol and bounded per cycle (REST weight budget).
        await self._refresh_stale_mover_candles(active)

        return active

    async def _refresh_stale_mover_candles(self, active: List[str]) -> None:
        """Re-seed candles for actively-scanned promoted movers whose 1m data
        has gone stale (no WS subscription → REST seed is their only source).

        Bounded work: at most ``MOVER_CANDLE_REFRESH_MAX_PER_CYCLE`` re-seeds
        per scan cycle, each throttled to one attempt per
        ``MOVER_CANDLE_REFRESH_SEC`` per symbol regardless of outcome, so a
        dead symbol can't burn the budget every cycle.  Fail-soft — a refresh
        error leaves the stale data in place (the dispatch staleness gate and
        trade_monitor's mark-feed fallback own the protection downstream).
        """
        from config import (
            MOVER_CANDLE_REFRESH_MAX_PER_CYCLE,
            MOVER_CANDLE_REFRESH_SEC,
        )
        if MOVER_CANDLE_REFRESH_SEC <= 0 or not active:
            return
        data_store = getattr(self, "data_store", None)
        if data_store is None or not hasattr(data_store, "last_kline_age_seconds"):
            return
        now_mono = time.monotonic()
        to_refresh: List[str] = []
        for sym in active:
            try:
                age = data_store.last_kline_age_seconds(sym, "1m")
                age = None if age is None else float(age)
            except (TypeError, ValueError):
                # Non-numeric store stub (tests) / unexpected shape — skip:
                # the downstream staleness protections own the safety net.
                continue
            # ``age is None`` = pre-stamp data (restored snapshot / legacy
            # seed) — refresh it too so the pair gets a real freshness stamp.
            if age is not None and age <= MOVER_CANDLE_REFRESH_SEC:
                continue
            last_attempt = self._mover_last_reseed.get(sym, 0.0)
            if now_mono - last_attempt < MOVER_CANDLE_REFRESH_SEC:
                continue
            to_refresh.append(sym)
            if len(to_refresh) >= MOVER_CANDLE_REFRESH_MAX_PER_CYCLE:
                break
        if not to_refresh:
            return
        for sym in to_refresh:
            self._mover_last_reseed[sym] = now_mono
        # Drop throttle entries for symbols no longer scanned (bounded map).
        if len(self._mover_last_reseed) > 128:
            keep = set(active)
            self._mover_last_reseed = {
                s: t for s, t in self._mover_last_reseed.items() if s in keep
            }

        async def _reseed(sym: str) -> None:
            info = self.pair_mgr.pairs.get(sym)
            if info is None:
                return
            try:
                await self.data_store.seed_symbol(sym, info.market)
                log.debug("mover candle refresh: re-seeded {}", sym)
            except Exception as exc:
                log.warning("mover candle refresh failed for {}: {}", sym, exc)

        await asyncio.gather(*[_reseed(s) for s in to_refresh])

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
                # The loop IS alive during a protective halt — keep the
                # heartbeat fresh so a stale heartbeat unambiguously means a
                # real hang, and publish the breaker state so the external
                # monitor can report "halted by breaker" instead of "unhealthy".
                # (2026-07-06: a 6h halt read as a crash because the skip
                # bypassed the end-of-cycle heartbeat touch.)
                self._touch_heartbeat()
                self._write_breaker_status()
                await asyncio.sleep(5)
                continue

            # WS health-aware scan gating: when the futures WS manager is
            # unhealthy (or not set) there is no live kline data, so a full
            # scan over the pair universe burns API weight on stale candles
            # and produces no signals.  Skip the full scan and track
            # degraded-cycle count.
            # 2026-05-14: spot WS removed; this gate now only consults futures.
            ws_futures_ok = self.ws_futures.is_healthy if self.ws_futures else True
            ws_both_unhealthy = not ws_futures_ok
            # Partial degradation: futures manager has below-threshold health.
            # Used to tighten REST fetch limits for the remainder of the cycle.
            ws_futures_ratio = self.ws_futures.health_ratio if self.ws_futures else 1.0
            self._ws_any_degraded_this_cycle = (
                ws_futures_ratio < WS_PARTIAL_HEALTH_THRESHOLD
            )
            if ws_both_unhealthy:
                self._consecutive_ws_degraded_cycles += 1
                # After WS_DEGRADED_MAX_CYCLES, stop blocking and fall through
                # to REST-only scanning so the engine is not stuck forever.
                if self._consecutive_ws_degraded_cycles < WS_DEGRADED_MAX_CYCLES:
                    log.warning(
                        "WS health degraded (futures={}) — skipping full scan "
                        "(degraded cycle #{})",
                        ws_futures_ok, self._consecutive_ws_degraded_cycles,
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
                    ws_conns = (self.ws_futures.stream_count if self.ws_futures else 0)
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
                        "WS partially degraded (futures_ratio={:.0%}) "
                        "— limiting scan to top {} pairs to protect REST rate limit",
                        ws_futures_ratio, WS_DEGRADED_MAX_PAIRS,
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
                # Movers promotion: pairs with extreme 24h % change — restricted to VSB+BREAKDOWN
                _mover_promoted = await self._update_movers_promotion(_sorted_pairs_set)
                _all_promoted = list(dict.fromkeys(_promoted + _mover_promoted))  # dedup, order-stable
                if _all_promoted:
                    _added = 0
                    _promoted_syms = {sym for sym, _ in filtered_pairs}
                    filtered_pairs = list(filtered_pairs)
                    for _promo_sym in _all_promoted:
                        if _promo_sym not in _promoted_syms:
                            _promo_info = self.pair_mgr.pairs.get(_promo_sym)
                            if _promo_info is not None:
                                filtered_pairs.append((_promo_sym, _promo_info))
                                _added += 1
                    if _added:
                        log.info(
                            "Added {} dynamically promoted pair(s) to scan cycle "
                            "(vol-surge={} movers={})",
                            _added, len(_promoted), len(_mover_promoted),
                        )

                sem = self._scan_semaphore
                self._stage_timing.clear()  # reset per-cycle stage accumulators
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

            # Per-stage timing diagnostic: sums are wall-time accumulated across
            # all concurrent symbol scans this cycle, so they can exceed the
            # cycle wall-time — the RATIO between stages locates the bottleneck.
            if SCAN_STAGE_TIMING_ENABLED and self._stage_timing:
                _stages = {
                    k: round(v, 2)
                    for k, v in sorted(
                        self._stage_timing.items(), key=lambda kv: -kv[1]
                    )
                }
                log.info(
                    "Scan stage timing (summed across concurrent scans, cycle={:.1f}s): {}",
                    elapsed_ms / 1000.0, _stages,
                )

            self.telemetry.set_pairs_monitored(len(self.pair_mgr.pairs))
            self.telemetry.set_mover_pairs(len(self._mover_promoted_pairs))
            self.telemetry.set_active_signals(len(self.router.active_signals))
            try:
                qsize = await self.signal_queue.qsize()
            except Exception as exc:
                log.warning("Failed to read signal queue size: {}", exc)
                qsize = 0
            self.telemetry.set_queue_size(qsize)
            ws_conns = (self.ws_futures.stream_count if self.ws_futures else 0)
            ws_ok = (self.ws_futures.is_healthy if self.ws_futures else True)
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
            if self._scan_cycle_count % 100 == 0 and self._penalty_modulation_counters:
                log.info(
                    "Penalty modulation distribution (last 100 cycles): {}",
                    dict(self._penalty_modulation_counters),
                )
                self._penalty_modulation_counters.clear()
            if self._scan_cycle_count % 100 == 0:
                _target_tier_summary = self._build_target_path_tier_migration_summary()
                _target_penalty_summary = self._build_target_path_penalty_summary()
                _target_funnel_summary, _target_outcome_summary = self._build_target_path_funnel_summary()
                _pr13_specialist_summary = self._build_pr13_specialist_reactivation_summary()
                if (
                    _target_tier_summary
                    or _target_penalty_summary
                    or _target_funnel_summary
                    or _target_outcome_summary
                ):
                    log.info(
                        "PR-7C target-path runtime summary (last 100 cycles): tier_migration={} penalty_hits={} funnel={} outcomes={}",
                        _target_tier_summary,
                        _target_penalty_summary,
                        _target_funnel_summary,
                        _target_outcome_summary,
                    )
                if _pr13_specialist_summary:
                    log.info(
                        "PR-13 specialist evidence-gate summary (last 100 cycles): {}",
                        _pr13_specialist_summary,
                    )
                self._target_path_tier_migration_counters.clear()
                self._target_path_penalty_gate_counters.clear()
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
            if self._scan_cycle_count % 100 == 0 and self._regime_cycle_counts:
                log.info(
                    "Regime distribution (last 100 cycles): {}",
                    dict(self._regime_cycle_counts),
                )
                self._regime_cycle_counts.clear()
            if self._scan_cycle_count % 100 == 0 and self._regime_cycle_by_symbol:
                # Compact: drop symbols with no classifications and convert
                # nested defaultdicts to plain dicts so the log line is
                # parseable by ast.literal_eval in the truth-report parser.
                compact = {
                    sym: dict(buckets)
                    for sym, buckets in self._regime_cycle_by_symbol.items()
                    if buckets
                }
                if compact:
                    log.info(
                        "Per-symbol regime distribution (last 100 cycles): {}",
                        compact,
                    )
                self._regime_cycle_by_symbol.clear()

            # Touch heartbeat file so healthcheck knows the scanner is alive
            # (FINDING-024).
            self._touch_heartbeat()
            self._write_breaker_status()

            if not self.force_scan:
                await asyncio.sleep(1)
            self.force_scan = False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    _HEARTBEAT_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "scanner_heartbeat"
    )

    _BREAKER_STATUS_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data", "circuit_breaker_status.json",
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

    def _write_breaker_status(self) -> None:
        """Publish a small circuit-breaker snapshot to the data volume so the
        external monitor can distinguish a *protective halt* from a *hung loop*.

        Local file write only — no network — so it is safe on the scan hot path
        (cost-discipline compliant). Best-effort; never blocks or crashes the
        loop. Added after the 2026-07-06 incident where a 6h breaker halt was
        indistinguishable from a crash to the monitor.
        """
        if not self.circuit_breaker:
            return
        try:
            snap = self.circuit_breaker.status_snapshot()
            snap["updated_at"] = time.time()
            os.makedirs(os.path.dirname(self._BREAKER_STATUS_PATH), exist_ok=True)
            with open(self._BREAKER_STATUS_PATH, "w") as fh:
                json.dump(snap, fh)
        except (OSError, TypeError, ValueError):
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
        # Gate on last-fetch time: only call the API when the cache is actually
        # stale.  Fetching every 1-second scan cycle costs Weight 2 × 60 = 120
        # weight/min but discards all 629 results when TTL hasn't expired.
        # Fetch at 90% of TTL so entries never expire between refreshes.
        now = time.monotonic()
        if now - self._last_book_ticker_fetch_at < _BOOK_TICKER_CACHE_TTL * 0.9:
            return

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
                bid_qty = entry.get("bidQty")
                ask_qty = entry.get("askQty")
                try:
                    bid_qty_f = float(bid_qty)
                    ask_qty_f = float(ask_qty)
                except (TypeError, ValueError):
                    bid_qty_f = 0.0
                    ask_qty_f = 0.0
                if bid_qty_f > 0 and ask_qty_f > 0:
                    self._order_book_snapshot_cache[symbol] = (
                        {
                            "bids": [[best_bid, bid_qty_f]],
                            "asks": [[best_ask, ask_qty_f]],
                            "source": "book_ticker",
                            "depth_quality": "top_of_book_only",
                        },
                        now + _BOOK_TICKER_CACHE_TTL,
                    )
                populated += 1

            self._last_book_ticker_fetch_at = now
            log.debug(
                "Global bookTicker pre-fetch refreshed {} spread cache entries (market={})",
                populated, market,
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
        _t0 = time.monotonic()
        try:
            if self.onchain_client is not None:
                return await asyncio.wait_for(
                    self.onchain_client.get_exchange_flow(symbol),
                    timeout=3,
                )
            return None
        except Exception as exc:
            log.debug("On-chain fetch error for {}: {}", symbol, exc)
            return None
        finally:
            self._stage_timing["onchain"] += time.monotonic() - _t0

    async def _verify_cross_exchange(
        self, symbol: str, direction: str, entry: float
    ) -> Optional[bool]:
        _t0 = time.monotonic()
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
        finally:
            self._stage_timing["cross_exchange"] += time.monotonic() - _t0
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
        # ------------------------------------------------------------------
        # Per-timeframe indicator cache.
        #
        # The whole-dict fingerprint approach was wrong: a new 1m candle closes
        # roughly every scan cycle, which changed the combined fingerprint and
        # invalidated indicators for ALL timeframes every cycle — so 5m/15m/1h/
        # 4h/1d/1w were recomputed needlessly even though their bars hadn't
        # closed.  Cache each timeframe independently keyed on that timeframe's
        # own candle count.  1m recomputes every cycle (scalping needs the live
        # bar); the higher timeframes hit ~95% of cycles.
        # ------------------------------------------------------------------
        loop = asyncio.get_running_loop()
        ticks = self.data_store.ticks.get(symbol, [])

        _sym_ind_cache = self._indicator_cache.setdefault(symbol, {})
        _tfs_to_compute: Dict[str, dict] = {}
        indicators: Dict[str, dict] = {}
        for _tf, _cd in candles.items():
            _n = len(_cd.get("close", []))
            _hit = _sym_ind_cache.get(_tf)
            if _hit is not None and _hit[0] == _n:
                indicators[_tf] = _hit[1]
            else:
                _tfs_to_compute[_tf] = _cd

        # SMC cache: structural sweeps / FVGs / orderblocks are deterministic on
        # completed candles.  Fingerprint on closed 5m+ candle counts only — the
        # in-progress 1m partial candle is excluded because its last_close changes
        # every tick while the structures are unchanged.  Cache stays warm for the
        # ~5 cycles between 5m candle closes (~80-95% hit rate).
        _smc_fp = tuple(
            len(candles.get(tf, {}).get("close", []))
            for tf in _SMC_CACHE_TFS
        )
        _cached_smc = self._smc_cache.get(symbol)
        _smc_cache_hit = _cached_smc is not None and _cached_smc[0] == _smc_fp

        # ── Indicator compute (only timeframes whose candle count changed) ──
        _t_ind = time.monotonic()
        if _tfs_to_compute:
            _fresh = await loop.run_in_executor(
                self._scan_executor,
                self._compute_indicators,
                _tfs_to_compute,
            )
            for _tf, _ind in _fresh.items():
                _sym_ind_cache[_tf] = (len(_tfs_to_compute[_tf].get("close", [])), _ind)
                indicators[_tf] = _ind
        self._stage_timing["indicators"] += time.monotonic() - _t_ind

        # ── SMC detect (skipped entirely on cache hit) ──
        _t_smc = time.monotonic()
        if _smc_cache_hit:
            smc_result = _cached_smc[1]
        else:
            smc_result = await loop.run_in_executor(
                self._scan_executor,
                functools.partial(
                    self.smc_detector.detect,
                    symbol, candles, ticks, self.order_flow_store,
                    lookback=SMC_SCALP_LOOKBACK,
                    tolerance_pct=SMC_SCALP_TOLERANCE_PCT,
                ),
            )
            self._smc_cache[symbol] = (_smc_fp, smc_result)
        self._stage_timing["smc"] += time.monotonic() - _t_smc

        smc_data = smc_result.as_dict()
        dependency_source_state: Dict[str, str] = {}
        _recent_ticks = smc_data.get("recent_ticks")
        if _recent_ticks is None:
            _recent_ticks = self.data_store.ticks.get(symbol, [])[-100:]
            dependency_source_state["recent_ticks"] = "unavailable" if not _recent_ticks else "populated"
        else:
            dependency_source_state["recent_ticks"] = "populated" if _recent_ticks else "empty"
        smc_data["recent_ticks"] = _recent_ticks

        _orderblocks_key_present = "orderblocks" in smc_data
        _raw_detector_orderblocks = smc_data.get("orderblocks")
        _detector_orderblocks_count = (
            len(_raw_detector_orderblocks)
            if isinstance(_raw_detector_orderblocks, list)
            else 0
        )
        _orderblocks = _raw_detector_orderblocks
        _orderblocks_detector_status = str(
            smc_data.get("orderblocks_detector_status") or "not_implemented"
        ).strip().lower()
        if _orderblocks is None:
            dependency_source_state["orderblocks"] = "unavailable"
            _orderblocks = []
        else:
            dependency_source_state["orderblocks"] = "populated" if _orderblocks else "empty"
        _scanner_orderblocks_count = len(_orderblocks)
        smc_data["orderblocks"] = _orderblocks
        smc_data["__orderblocks_trace"] = {
            "detector_key_present": _orderblocks_key_present,
            "detector_status": _orderblocks_detector_status,
            "detector_count": _detector_orderblocks_count,
            "scanner_source_state": dependency_source_state["orderblocks"],
            "scanner_final_count": _scanner_orderblocks_count,
        }
        log.debug(
            "{} orderblocks trace: detector_key_present={}, detector_status={}, detector_count={}, scanner_state={}, scanner_count={}",
            symbol,
            _orderblocks_key_present,
            _orderblocks_detector_status,
            _detector_orderblocks_count,
            dependency_source_state["orderblocks"],
            _scanner_orderblocks_count,
        )

        _order_book = smc_data.get("order_book")
        if _order_book is None:
            _book_snapshot = self._order_book_snapshot_cache.get(symbol)
            if _book_snapshot and time.monotonic() < float(_book_snapshot[1]):
                _order_book = _book_snapshot[0]
            if _order_book is None:
                dependency_source_state["order_book"] = "unavailable"
            elif isinstance(_order_book, dict) and ((_order_book.get("bids") or []) and (_order_book.get("asks") or [])):
                dependency_source_state["order_book"] = "populated"
            else:
                dependency_source_state["order_book"] = "empty"
        elif isinstance(_order_book, dict) and ((_order_book.get("bids") or []) and (_order_book.get("asks") or [])):
            dependency_source_state["order_book"] = "populated"
        else:
            dependency_source_state["order_book"] = "empty"
        smc_data["order_book"] = _order_book

        _liq_clusters = smc_data.get("liquidation_clusters")
        if _liq_clusters is None:
            if self.order_flow_store is not None:
                _cluster_fn = getattr(self.order_flow_store, "get_liquidation_clusters", None)
                if callable(_cluster_fn):
                    try:
                        _cluster_candidates = _cluster_fn(symbol)
                    except Exception:
                        _cluster_candidates = []
                    _liq_clusters = _cluster_candidates if isinstance(_cluster_candidates, list) else []
                    dependency_source_state["liquidation_clusters"] = "populated" if _liq_clusters else "empty"
                else:
                    dependency_source_state["liquidation_clusters"] = "unavailable"
                    _liq_clusters = []
            else:
                dependency_source_state["liquidation_clusters"] = "unavailable"
                _liq_clusters = []
        else:
            dependency_source_state["liquidation_clusters"] = "populated" if _liq_clusters else "empty"
        smc_data["liquidation_clusters"] = _liq_clusters
        # Attach per-pair profile so channel evaluators can consume it via
        # smc_data.get("pair_profile") without any signature changes.
        smc_data["pair_profile"] = classify_pair_tier(symbol, volume_24h_usd=volume_24h)

        regime_tf = "5m" if "5m" in indicators else "1m"
        regime_ind = indicators.get("5m", indicators.get("1m", {}))
        regime_candles = candles.get("5m", candles.get("1m"))
        _pair_tier = getattr(smc_data.get("pair_profile"), "tier", "MIDCAP")
        regime_result = self.regime_detector.classify(
            regime_ind,
            regime_candles,
            timeframe=regime_tf,
            symbol=symbol,
            pair_tier=_pair_tier,
        )
        await asyncio.sleep(0)
        log.debug("{} regime: {}", symbol, regime_result.regime.value)
        self._regime_cycle_counts[regime_result.regime.value] += 1
        self._regime_cycle_by_symbol[symbol][regime_result.regime.value] += 1
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
            symbol=symbol, pair_tier=_pair_tier,
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
            # 15m CVD (OWNER_BRIEF §3.4a — HTF Structure, LTF Entry).  Separate
            # 15m-aligned series for divergence detection on 15m bars; consumed
            # by DIVERGENCE_CONTINUATION after its per-path criteria fix.  None
            # when uninitialised so consumers can fail-open per soft-penalty doctrine.
            _cvd_15m_arr = self.order_flow_store.get_cvd_15m_history(symbol)
            smc_data["cvd_15m"] = (
                _cvd_15m_arr.tolist() if len(_cvd_15m_arr) > 0 else None
            )
            dependency_source_state["funding_rate"] = "populated" if _fr is not None else "empty"
            dependency_source_state["cvd"] = "populated" if len(_cvd_arr) > 0 else "empty"
            dependency_source_state["cvd_15m"] = (
                "populated" if len(_cvd_15m_arr) > 0 else "empty"
            )
            log.debug(
                "{} smc_data: funding_rate={}, cvd_candles={}, cvd_15m_candles={}",
                symbol,
                _fr,
                len(_cvd_arr),
                len(_cvd_15m_arr),
            )
        else:
            dependency_source_state["funding_rate"] = "unavailable"
            dependency_source_state["cvd"] = "unavailable"
            dependency_source_state["cvd_15m"] = "unavailable"
        dependency_source_state["oi_snapshot"] = (
            "unavailable" if self.order_flow_store is None else "empty"
        )
        smc_data["__dependency_source_state"] = dependency_source_state
        smc_data["__dependency_state"] = self._build_dependency_readiness(symbol, smc_data)

        # HTF level lookup for evaluators that need to anchor signals to
        # structural HTF levels (OWNER_BRIEF §3.4a — "HTF Structure, LTF
        # Entry").  LSR consumes this in the HTF POI anchor check.  Other
        # evaluators (SR_FLIP / FAR per upcoming PRs) will consume the same
        # list once their per-path criteria fixes land.
        #
        # ``_refresh_level_book_if_stale`` is idempotent (per-symbol TTL),
        # so calling it here AND from ``_prepare_signal`` (where the
        # confluence bonus consumes the same data post-evaluator) is safe.
        # The duplicate call costs at most one extra dict lookup per cycle
        # in the steady state where the TTL hasn't elapsed.
        try:
            self._refresh_level_book_if_stale(symbol, candles)
            smc_data["level_book_levels"] = self.level_book.get_levels(symbol)
        except Exception as _lb_exc:
            log.debug(
                "LevelBook refresh/lookup failed at smc_data assembly for {}: {}",
                symbol, _lb_exc,
            )
            smc_data["level_book_levels"] = []

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

    def _should_skip_channel(self, symbol: str, chan_name: str, ctx: ScanContext) -> Optional[str]:
        """Return a short skip-reason token if *chan_name* should not scan *symbol*
        this cycle, else ``None``. The token feeds the mover "why not firing"
        diagnostic (and is truthy, so existing ``if`` call sites keep working)."""
        # Tier-based channel gating: Tier 2 pairs skip SCALP (REST-only, no
        # order book depth for tight scalp execution).
        pair_info = self.pair_mgr.pairs.get(symbol)
        if pair_info is not None and pair_info.tier == PairTier.TIER2 and chan_name == "360_SCALP":
            log.debug("Skipping {} {} – Tier 2 pair excluded from SCALP", symbol, chan_name)
            self._suppression_counters[f"tier2_scalp_excluded:{chan_name}"] += 1
            return "tier2_scalp_excluded"
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
                    return (
                        "pair_quality_spread" if "spread" in chan_quality.reason
                        else "pair_quality_volume"
                    )
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
                return "pair_quality_no_volume"
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
                return "volatile_unsuitable"
        if chan_name in self.paused_channels:
            self._suppression_counters[f"paused_channel:{chan_name}"] += 1
            return "channel_paused"
        if self._is_in_cooldown(symbol, chan_name):
            log.debug("Cooldown active: skipping {} {}", symbol, chan_name)
            self._suppression_counters[f"cooldown:{chan_name}"] += 1
            return "cooldown"
        # Per-symbol circuit breaker: suppress the symbol across all channels
        # when it has accumulated too many consecutive SL hits.
        if self.circuit_breaker is not None and self.circuit_breaker.is_symbol_tripped(symbol):
            log.debug(
                "Per-symbol circuit breaker active: skipping {} {}", symbol, chan_name
            )
            self._suppression_counters[f"circuit_breaker:{chan_name}"] += 1
            return "circuit_breaker"
        if any(
            s.symbol == symbol and s.channel == chan_name
            for s in self.router.active_signals.values()
        ):
            log.debug("Skipping {} {} – active signal already exists", symbol, chan_name)
            self._suppression_counters[f"active_signal:{chan_name}"] += 1
            return "active_signal_exists"
        if (
            chan_name == "360_SCALP"
            and ctx.is_ranging
            and ctx.adx_val < _RANGING_ADX_SUPPRESS_THRESHOLD
        ):
            # Family-aware doctrine routing: do not hard-block the whole channel
            # pre-evaluator; defer to setup-family logic in _prepare_signal().
            self._suppression_counters[
                f"ranging_low_adx:channel_preskip_bypassed:{chan_name}"
            ] += 1
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
            return f"regime_{current_regime}".lower()
        return None

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
    def _is_scalp_family_blocked_in_ranging_low_adx(
        setup_family: str, setup_class: str = "", htf_trend_aligned: bool = False
    ) -> bool:
        # Only families in the blocked set are ever gated here.
        if setup_family not in _SCALP_RANGING_LOW_ADX_BLOCKED_FAMILIES:
            return False
        # Exemption — the whole trend-pullback family, scoped by htf_trend_aligned:
        # a HTF-aligned pullback fires AT a dip that reads RANGING/low-ADX on the
        # entry TF BY DESIGN, but a higher timeframe IS trending — the exact
        # opposite of the dead chop this gate targets.  The flag is stamped only by
        # the trend-pullback family (TREND_PULLBACK_EMA on its 1H-trend path;
        # MOVER_TREND_PULLBACK on the MA stack), so it scopes the exemption to
        # exactly the EMA-riding continuation paths and leaves TPE's 5m-fallback
        # path (no HTF confirmation) blocked.  The explicit setup set is a belt-and-
        # suspenders backstop for a path that self-proves the move even if the flag
        # is ever dropped.  Family stays in the blocked set for SCORING; only the
        # gate is exempt — the §3.6a split, at the gate.  setup_class/htf default so
        # existing family-only callers are unchanged.
        if htf_trend_aligned:
            return False
        if setup_class and setup_class in _SCALP_RANGING_LOW_ADX_EXEMPT_SETUPS:
            return False
        return True

    @staticmethod
    def _should_block_ranging_low_atr_loser(
        setup_class_name: str,
        is_ranging: bool,
        atr_pctile: Optional[float],
    ) -> bool:
        """Pure predicate for the RANGING low-ATR loser-setup gate.

        True when a configured loser setup (SR_FLIP_RETEST / LSR) fires into a
        low-ATR range — the dead chop where mean-reversion scalping bleeds net
        of fees.  Kept side-effect-free so it is directly unit-testable; the
        ENABLED-vs-shadow decision stays at the call site.
        """
        if not is_ranging:
            return False
        if setup_class_name not in RANGING_LOW_ATR_SUPPRESS_SETUPS:
            return False
        if atr_pctile is None:
            return False
        return atr_pctile <= RANGING_LOW_ATR_SUPPRESS_PCTILE

    @staticmethod
    def _regime_name_from_ctx(ctx: ScanContext, default: str = "RANGING") -> str:
        regime_obj = getattr(getattr(ctx, "regime_result", None), "regime", None)
        if regime_obj is not None and hasattr(regime_obj, "value"):
            return str(regime_obj.value)
        return default

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
        if stage == "emitted":
            _emitted_setup = self._normalize_setup_class(setup_class_name)
            if _emitted_setup == "MEAN_REVERT":
                self._mean_revert_emitted_total += 1
            elif _emitted_setup == "RANGE_FADE":
                self._range_fade_emitted_total += 1

    @staticmethod
    def _dependency_count_bucket(value: int) -> str:
        if value <= 0:
            return "none"
        if value <= 3:
            return "few"
        if value <= 20:
            return "some"
        return "many"

    def _build_dependency_readiness(self, symbol: str, smc_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        source_state_map = smc_data.get("__dependency_source_state")
        if not isinstance(source_state_map, dict):
            source_state_map = {}

        def _state(name: str, count: int, unavailable: bool = False) -> str:
            if unavailable:
                return "unavailable"
            if count <= 0:
                return "empty"
            return "populated"

        funding_rate = smc_data.get("funding_rate")
        cvd_data = smc_data.get("cvd")
        cvd_count = len(cvd_data) if isinstance(cvd_data, list) else 0
        recent_ticks = smc_data.get("recent_ticks") or []
        orderblocks = smc_data.get("orderblocks") or []
        orderblock_trace = smc_data.get("__orderblocks_trace")
        orderblocks_source = "unknown"
        if isinstance(orderblock_trace, dict):
            _trace_status = str(orderblock_trace.get("detector_status") or "not_set").strip().lower()
            if _trace_status:
                orderblocks_source = _trace_status
        order_book = smc_data.get("order_book")
        liq_clusters = smc_data.get("liquidation_clusters") or []
        oi_points = 0
        if self.order_flow_store is not None:
            oi_points = len(getattr(self.order_flow_store, "_oi", {}).get(symbol, []))
        order_book_levels = 0
        order_book_source = "unavailable"
        order_book_quality = "none"
        if isinstance(order_book, dict):
            bids = order_book.get("bids") or []
            asks = order_book.get("asks") or []
            order_book_levels = min(len(bids), len(asks))
            _raw_source = str(order_book.get("source") or "").strip().lower()
            if _raw_source:
                order_book_source = _raw_source
            else:
                order_book_source = "unknown"
            _raw_quality = str(order_book.get("depth_quality") or "").strip().lower()
            if _raw_quality:
                order_book_quality = _raw_quality
            elif order_book_levels >= 2:
                order_book_quality = "multi_level"
            elif order_book_levels == 1:
                order_book_quality = "single_level"
            else:
                order_book_quality = "empty"
        oi_state = _state("oi_snapshot", oi_points, unavailable=self.order_flow_store is None)
        return {
            "funding_rate": {
                "state": source_state_map.get("funding_rate", _state("funding_rate", 1 if funding_rate is not None else 0)),
                "present": funding_rate is not None,  # BUG FIX: was != unavailable
                "bucket": self._dependency_count_bucket(1 if funding_rate is not None else 0),
            },
            "cvd": {
                "state": source_state_map.get("cvd", _state("cvd", cvd_count)),
                "present": cvd_count > 0,  # BUG FIX: was != unavailable
                "count": cvd_count,
                "bucket": self._dependency_count_bucket(cvd_count),
            },
            "recent_ticks": {
                "state": source_state_map.get("recent_ticks", _state("recent_ticks", len(recent_ticks))),
                "present": len(recent_ticks) > 0,  # BUG FIX
                "count": len(recent_ticks),
                "bucket": self._dependency_count_bucket(len(recent_ticks)),
            },
            "orderblocks": {
                "state": source_state_map.get("orderblocks", _state("orderblocks", len(orderblocks))),
                "present": len(orderblocks) > 0,  # BUG FIX
                "count": len(orderblocks),
                "bucket": self._dependency_count_bucket(len(orderblocks)),
                "source": orderblocks_source,
            },
            "order_book": {
                "state": source_state_map.get("order_book", _state("order_book", order_book_levels)),
                "present": order_book_levels > 0,  # BUG FIX
                "count": order_book_levels,
                "bucket": self._dependency_count_bucket(order_book_levels),
                "source": order_book_source,
                "quality": order_book_quality,
            },
            "liquidation_clusters": {
                "state": source_state_map.get("liquidation_clusters", _state("liquidation_clusters", len(liq_clusters))),
                "present": len(liq_clusters) > 0,  # BUG FIX
                "count": len(liq_clusters),
                "bucket": self._dependency_count_bucket(len(liq_clusters)),
            },
            "oi_snapshot": {
                "state": "populated" if oi_points > 0 else oi_state,
                "present": oi_points > 0,  # BUG FIX: was != unavailable
                "count": oi_points,
                "bucket": self._dependency_count_bucket(oi_points),
            },
        }

    def _record_dependency_readiness(self, chan_name: str, smc_data: Dict[str, Any]) -> None:
        _dep_state = smc_data.get("__dependency_state")
        if not isinstance(_dep_state, dict):
            return
        for _dep_name, _details in _dep_state.items():
            if not isinstance(_details, dict):
                continue
            _present = bool(_details.get("present"))
            _presence = "present" if _present else "absent"
            self._channel_funnel_counters[f"dependency_presence:{chan_name}:{_dep_name}:{_presence}"] += 1
            _state = str(_details.get("state") or "").strip()
            if _state in {"unavailable", "empty", "populated"}:
                self._channel_funnel_counters[f"dependency_state:{chan_name}:{_dep_name}:{_state}"] += 1
            _bucket = str(_details.get("bucket") or "").strip()
            if _bucket:
                self._channel_funnel_counters[f"dependency_bucket:{chan_name}:{_dep_name}:{_bucket}"] += 1
            _source = str(_details.get("source") or "").strip()
            if _source:
                self._channel_funnel_counters[f"dependency_source:{chan_name}:{_dep_name}:{_source}"] += 1
            _quality = str(_details.get("quality") or "").strip()
            if _quality:
                self._channel_funnel_counters[f"dependency_quality:{chan_name}:{_dep_name}:{_quality}"] += 1

    def _record_scalp_generation_telemetry(self, chan: Any, chan_name: str) -> None:
        if chan_name != "360_SCALP":
            return
        _consume = getattr(chan, "consume_generation_telemetry", None)
        if not callable(_consume):
            return
        _snapshot = _consume() or {}
        _stage_map = {
            "attempts": "evaluator_attempted",
            "no_signal": "evaluator_no_signal",
            "generated": "evaluator_generated",
        }
        for _source_stage, _funnel_stage in _stage_map.items():
            _counts = _snapshot.get(_source_stage, {})
            if not isinstance(_counts, dict):
                continue
            for _path_name, _count in _counts.items():
                _n = int(_count or 0)
                if _n <= 0:
                    continue
                _eval_path_key = f"{_EVAL_PATH_PREFIX}{self._normalize_setup_class(_path_name)}"
                self._path_funnel_counters[self._path_funnel_key(_funnel_stage, chan_name, _eval_path_key)] += _n
        _reason_counts = _snapshot.get("no_signal_reason", {})
        if isinstance(_reason_counts, dict):
            for _reason_key, _count in _reason_counts.items():
                _n = int(_count or 0)
                if _n <= 0:
                    continue
                try:
                    _path_name, _reason = str(_reason_key).rsplit(":", 1)
                except ValueError:
                    _path_name, _reason = str(_reason_key), "unknown"
                _normalized_path = self._normalize_setup_class(_path_name)
                _normalized_reason = self._metric_token(_reason)
                _eval_path_key = f"{_EVAL_PATH_PREFIX}{_normalized_path}"
                self._path_funnel_counters[
                    self._path_funnel_key(
                        f"evaluator_no_signal_reason:{_normalized_reason}",
                        chan_name,
                        _eval_path_key,
                    )
                ] += _n
                if _normalized_reason in _DEPENDENCY_ABSENCE_REASON_TOKENS:
                    self._path_funnel_counters[
                        self._path_funnel_key(
                            f"dependency_missing:{_normalized_reason}",
                            chan_name,
                            _eval_path_key,
                        )
                    ] += _n
                self._channel_funnel_counters[
                    f"evaluator_no_signal_reason:{chan_name}:{_normalized_path}:{_normalized_reason}"
                ] += _n

    @staticmethod
    def _evaluate_family_semantic_mtf(
        *,
        setup_family: str,
        signal_direction: str,
        mtf_data: Dict[str, Dict[str, float]],
        min_score: float,
        tf_weight_overrides: Optional[Dict[str, float]] = None,
    ) -> Tuple[bool, str]:
        """Evaluate family-semantic MTF pass/fail for structural scalp families.

        This is intentionally scoped to reclaim/retest and reversal families:
        preserve higher-TF context while avoiding a pure trend-alignment doctrine.
        """
        if setup_family not in _SCALP_MTF_SEMANTIC_FAMILIES:
            return False, "not_semantic_family"
        if not mtf_data:
            return False, "semantic_fail_no_data"

        result = compute_mtf_confluence(
            signal_direction,
            mtf_data,
            min_score=min_score,
            tf_weight_overrides=tf_weight_overrides,
        )
        if result.total_count == 0:
            return False, "semantic_fail_no_valid_tf"

        wanted = "BULLISH" if signal_direction.upper() == "LONG" else "BEARISH"
        opposed = "BEARISH" if wanted == "BULLISH" else "BULLISH"
        lower_tfs = {"1m", "5m", "15m"}
        higher_tfs = {"1h", "4h", "1d"}
        lower_states = [s for s in result.timeframe_states if s.timeframe in lower_tfs]
        higher_states = [s for s in result.timeframe_states if s.timeframe in higher_tfs]

        score_deficit = max(0.0, min_score - float(result.score))
        if score_deficit > _SCALP_MTF_SEMANTIC_NEAR_MISS_MAX_DELTA:
            return False, "semantic_fail_deep_misalignment"

        lower_aligned = sum(1 for s in lower_states if s.trend == wanted)
        lower_opposed = sum(1 for s in lower_states if s.trend == opposed)
        if not (lower_aligned >= 2 and lower_opposed == 0):
            return False, "semantic_fail_lower_tf_weak"

        higher_aligned = sum(1 for s in higher_states if s.trend == wanted)
        higher_opposed = sum(1 for s in higher_states if s.trend == opposed)
        if not (higher_aligned >= 1 and higher_opposed == 0):
            return False, "semantic_fail_higher_tf_weak"

        return True, "family_semantic_mtf_pass"

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

    @staticmethod
    def _is_pr7c_target_setup(setup_class: Any) -> bool:
        _setup = Scanner._normalize_setup_class(setup_class)
        return _setup in _PR7C_TARGET_SETUPS

    @staticmethod
    def _target_path_summary_token(setup_class: str, setup_family: str) -> str:
        return f"{setup_class}[{setup_family}]"

    def _record_target_path_tier_migration(
        self,
        *,
        setup_family: str,
        setup_class: str,
        pre_tier: str,
        post_tier: str,
    ) -> None:
        """Record pre→post tier migration for PR-7C target paths."""
        if not self._is_pr7c_target_setup(setup_class):
            return
        self._target_path_tier_migration_counters[
            f"{setup_family}:{setup_class}:{pre_tier}->{post_tier}"
        ] += 1

    def _build_target_path_tier_migration_summary(self) -> Dict[str, Dict[str, int]]:
        """Build operator-facing tier migration summary for PR-7C target paths."""
        _summary: Dict[str, Dict[str, int]] = {}
        for _key, _count in self._target_path_tier_migration_counters.items():
            _segments = _key.split(":")
            if len(_segments) != 3:
                continue
            _family, _setup, _transition = _segments
            _tiers = _transition.split("->")
            if len(_tiers) != 2:
                continue
            _pre_tier, _post_tier = _tiers
            _token = self._target_path_summary_token(_setup, _family)
            _bucket = _summary.setdefault(_token, {})
            _bucket[_transition] = _bucket.get(_transition, 0) + _count
            if self._is_tier_compressed(_pre_tier, _post_tier):
                _bucket["pre_B_or_A+_compressed"] = _bucket.get("pre_B_or_A+_compressed", 0) + _count
        return _summary

    @staticmethod
    def _is_tier_compressed(pre_tier: str, post_tier: str) -> bool:
        return pre_tier in {"A+", "B"} and post_tier not in {"A+", "B"}

    def _build_target_path_penalty_summary(self) -> Dict[str, Dict[str, int]]:
        """Build operator-facing per-path penalty gate hit counts for PR-7C."""
        _summary: Dict[str, Dict[str, int]] = {}
        for _key, _count in self._target_path_penalty_gate_counters.items():
            try:
                _family, _setup, _gate = _key.split(":", 2)
            except ValueError:
                continue
            _token = self._target_path_summary_token(_setup, _family)
            _bucket = _summary.setdefault(_token, {})
            _bucket[_gate] = _bucket.get(_gate, 0) + _count
        return _summary

    def _build_target_path_funnel_summary(self) -> Tuple[Dict[str, Dict[str, int]], Dict[str, Dict[str, int]]]:
        """Build target-path stage funnel and lifecycle outcome summaries."""
        _funnel_summary: Dict[str, Dict[str, int]] = {}
        _outcome_summary: Dict[str, Dict[str, int]] = {}
        for _key, _count in self._path_funnel_counters.items():
            _parts = _key.split(":")
            if not _parts:
                continue
            if _parts[0] == "lifecycle":
                if len(_parts) != 5:
                    continue
                _, _outcome, _, _family, _setup = _parts
                if not self._is_pr7c_target_setup(_setup):
                    continue
                _token = self._target_path_summary_token(_setup, _family)
                _bucket = _outcome_summary.setdefault(_token, {})
                _bucket[_outcome] = _bucket.get(_outcome, 0) + _count
                continue
            if len(_parts) != 4:
                continue
            _stage, _, _family, _setup = _parts
            if not self._is_pr7c_target_setup(_setup):
                continue
            _token = self._target_path_summary_token(_setup, _family)
            _bucket = _funnel_summary.setdefault(_token, {})
            _bucket[_stage] = _bucket.get(_stage, 0) + _count
        return _funnel_summary, _outcome_summary

    def _build_pr13_specialist_reactivation_summary(self) -> Dict[str, Dict[str, Any]]:
        """Build evidence-gated specialist/internal path retention summary for PR-13."""
        _tracked_setups = _PR13_SPECIALIST_REVIEW_SETUPS | _PR13_GOVERNANCE_DISABLED_REVIEW_SETUPS
        _counts: Dict[str, Dict[str, int]] = {
            _setup: {"attempted": 0, "generated": 0, "scanner_preparation": 0, "emitted": 0}
            for _setup in _tracked_setups
        }

        for _key, _count in self._path_funnel_counters.items():
            _parts = _key.split(":", 3)
            if len(_parts) != 4:
                continue
            _stage, _chan_name, _, _setup_raw = _parts
            if _chan_name != "360_SCALP":
                continue

            _setup_name = self._normalize_setup_class(_setup_raw)
            if _stage in {"evaluator_attempted", "evaluator_generated"}:
                if not _setup_name.startswith(_EVAL_PATH_PREFIX):
                    continue
                _setup_name = self._normalize_setup_class(_setup_name[len(_EVAL_PATH_PREFIX):])
            if _setup_name not in _tracked_setups:
                continue

            if _stage == "evaluator_attempted":
                _counts[_setup_name]["attempted"] += _count
            elif _stage == "evaluator_generated":
                _counts[_setup_name]["generated"] += _count
            elif _stage == "scanner_preparation":
                _counts[_setup_name]["scanner_preparation"] += _count
            elif _stage == "emitted":
                _counts[_setup_name]["emitted"] += _count

        _summary: Dict[str, Dict[str, Any]] = {}
        for _setup_name in sorted(_tracked_setups):
            _bucket = _counts[_setup_name]
            if not any(_bucket.values()):
                continue
            _evidence_ready = (
                _bucket["generated"] > 0
                and _bucket["scanner_preparation"] > 0
                and _bucket["emitted"] > 0
            )
            if _setup_name in _PR13_GOVERNANCE_DISABLED_REVIEW_SETUPS:
                _decision = "retained_inactive_governance_disabled"
            elif _evidence_ready:
                _decision = "retain_current_activation_no_auto_promotion"
            else:
                _decision = "retained_conservative_insufficient_post_pr_evidence"
            _summary[_setup_name] = {
                "attempted": _bucket["attempted"],
                "generated": _bucket["generated"],
                "scanner_preparation": _bucket["scanner_preparation"],
                "emitted": _bucket["emitted"],
                "evidence_ready_for_reactivation": _evidence_ready,
                "decision": _decision,
            }
        return _summary

    def _resolve_penalty_modulation_scale(
        self,
        *,
        setup_class: str,
        setup_family: str,
        penalty_key: str,
    ) -> Tuple[float, str]:
        _path_scale = _PENALTY_MODULATION_BY_SETUP.get(setup_class, {}).get(penalty_key)
        if _path_scale is not None:
            return self._clamp_penalty_modulation_scale(_path_scale), "path"
        return 1.0, "none"

    @staticmethod
    def _clamp_penalty_modulation_scale(scale: float) -> float:
        return min(
            _PENALTY_MODULATION_MAX_SCALE,
            max(_PENALTY_MODULATION_MIN_SCALE, float(scale)),
        )

    def _modulate_penalty_base(
        self,
        *,
        base: float,
        penalty_key: str,
        chan_name: str,
        setup_family: str,
        setup_class: str,
    ) -> float:
        _scale, _source = self._resolve_penalty_modulation_scale(
            setup_class=setup_class,
            setup_family=setup_family,
            penalty_key=penalty_key,
        )
        if _scale >= 0.999:
            return base
        _modulated = round(base * _scale, 1)
        self._penalty_modulation_counters[
            f"modulated:{penalty_key}:{chan_name}:{setup_family}:{setup_class}:{_source}:{_scale:.2f}"
        ] += 1
        if self._is_pr7c_target_setup(setup_class):
            self._target_path_penalty_gate_counters[f"{setup_family}:{setup_class}:{penalty_key}"] += 1
        return _modulated

    # Outcome → dispatch-cooldown extension duration (seconds).  Owner-
    # flagged 2026-05-09: same DOGEUSDT SR_FLIP_RETEST SHORT signal
    # dispatched 4× in 7h, all EXPIRED — the 30-min dispatch cooldown
    # elapsed mid-trade and nothing prevented re-emission on the same
    # level.  Outcomes not in this map keep the default 30-min cooldown
    # set at dispatch time (TP* hits, BREAKEVEN_EXIT, PROFIT_LOCKED,
    # FULL_TP_HIT, CLOSED).
    _LIFECYCLE_COOLDOWN_BY_OUTCOME: Dict[str, int] = {
        "EXPIRED": LIFECYCLE_COOLDOWN_EXPIRED_SEC,
        "SL_HIT": LIFECYCLE_COOLDOWN_SL_SEC,
        "INVALIDATED": LIFECYCLE_COOLDOWN_INVALIDATION_SEC,
    }

    def on_signal_lifecycle_outcome(self, sig: Any, outcome_label: str) -> None:
        """Record final lifecycle outcome against origin setup family/path,
        and extend the (symbol, setup_class, direction) dispatch cooldown
        when the outcome indicates the thesis didn't pan out."""
        _chan_name = getattr(sig, "channel", "") or "UNKNOWN"
        _setup_class_name = self._resolve_origin_setup_class(sig)
        _setup_family = getattr(sig, "origin_setup_family", "") or self._setup_family_for_channel(
            _chan_name, _setup_class_name
        )
        self._path_funnel_counters[
            f"lifecycle:{outcome_label}:{_chan_name}:{_setup_family}:{_setup_class_name}"
        ] += 1

        extension_sec = self._LIFECYCLE_COOLDOWN_BY_OUTCOME.get(outcome_label)
        try:
            streak = self._update_loss_streak(sig, outcome_label)
        except Exception as exc:
            log.debug("loss-streak update failed (non-fatal): {}", exc)
            streak = 0
        if extension_sec is None or extension_sec <= 0:
            return
        try:
            cd_key = self._cooldown_key_for(sig)
            if cd_key is None:
                return
            # Loss-streak escalation (2026-07-09, dark-flagged): double the
            # extension per consecutive losing outcome on this key, capped,
            # so the flat 1h/2h cooldown stops metronoming re-entries into
            # a setup that keeps failing.  Shadow-logged while the tunable
            # is OFF so activation is decided on measured would-block data.
            if streak >= 2:
                try:
                    from src import runtime_tunables as _rt
                    _cap_sec = float(_rt.get("loss_streak_cap_hours")) * 3600.0
                    _escalated = min(
                        extension_sec * (2 ** (streak - 1)), _cap_sec
                    )
                    if bool(_rt.get("loss_streak_escalation_enabled")):
                        self._path_funnel_counters[
                            f"loss_streak_escalated:{cd_key[1]}"
                        ] += 1
                        log.info(
                            "loss_streak escalate {} {} {} (streak={} → "
                            "cooldown {}s instead of {}s)",
                            cd_key[0], cd_key[1], cd_key[2],
                            streak, int(_escalated), extension_sec,
                        )
                        extension_sec = _escalated
                    else:
                        self._path_funnel_counters[
                            f"loss_streak_shadow:{cd_key[1]}"
                        ] += 1
                        log.info(
                            "[SHADOW] LOSS_STREAK_WOULD_EXTEND: {} {} {} "
                            "(streak={} — would set {}s cooldown instead "
                            "of {}s)",
                            cd_key[0], cd_key[1], cd_key[2],
                            streak, int(_escalated), extension_sec,
                        )
                except Exception as exc:
                    log.debug("loss-streak escalation failed (fail-open): {}", exc)
            new_expiry = time.time() + extension_sec
            existing = self._dispatch_cooldown.get(cd_key, 0.0)
            # Ratchet only — never shorten an already-longer cooldown.
            if new_expiry > existing:
                self._dispatch_cooldown[cd_key] = new_expiry
                self._persist_dispatch_cooldown()
                log.info(
                    "dispatch_cooldown extend {} {} {} ({} → +{}s after {})",
                    cd_key[0], cd_key[1], cd_key[2],
                    outcome_label, extension_sec, outcome_label,
                )
        except Exception as exc:
            log.debug("lifecycle cooldown extension failed (non-fatal): {}", exc)

    def _update_loss_streak(self, sig: Any, outcome_label: str) -> int:
        """Maintain the consecutive-loss streak for this signal's
        (symbol, setup_class, direction) key and return the current streak.

        A losing outcome (realised PnL at or below LOSS_STREAK_LOSS_PCT on a
        stop / expiry / invalidation / plain close) increments the streak; a
        profitable one (PnL at or above LOSS_STREAK_RESET_PCT, or any TP /
        PROFIT_LOCKED completion) resets it.  Breakeven-ish scratches in
        between leave the streak unchanged — a BE park is not evidence the
        thesis failed, nor that it worked.
        """
        cd_key = self._cooldown_key_for(sig)
        if cd_key is None:
            return 0
        pnl = float(getattr(sig, "pnl_pct", 0.0) or 0.0)
        winning_labels = ("TP1_HIT", "TP2_HIT", "TP3_HIT", "FULL_TP_HIT", "PROFIT_LOCKED")
        losing_labels = ("SL_HIT", "EXPIRED", "INVALIDATED", "CLOSED")
        if outcome_label in winning_labels or pnl >= LOSS_STREAK_RESET_PCT:
            if self._loss_streaks.pop(cd_key, None) is not None:
                self._persist_loss_streaks()
            return 0
        if outcome_label in losing_labels and pnl <= LOSS_STREAK_LOSS_PCT:
            streak = self._loss_streaks.get(cd_key, 0) + 1
            self._loss_streaks[cd_key] = streak
            self._persist_loss_streaks()
            return streak
        return self._loss_streaks.get(cd_key, 0)

    @staticmethod
    def _get_primary_timeframe(chan_name: str) -> str:
        """Return the primary timeframe interval string for a given channel name."""
        return "5m"

    @staticmethod
    def _resolve_candles(candles: Dict[str, dict], primary_tf: str) -> dict:
        """Return the best available candle dict for *primary_tf*, falling back to 5m/1m."""
        return candles.get(primary_tf) or candles.get("5m") or candles.get("1m") or {}

    def _get_btc_state_cached(self) -> Dict[str, object]:
        """Composite BTC-State (pair-independent), cached per cycle.

        The multi-TF EMA/RSI/ATR compute is identical for every signal in a scan
        cycle, so it runs at most once per ``BTC_STATE_CACHE_TTL_SEC`` and is reused
        across all pairs — keeping it off the per-signal hot path (Cost Discipline:
        no new network/Firestore read; ``get_candles`` is an in-memory lookup).
        Fails toward the neutral b=0 read on any error.
        """
        now = time.monotonic()
        cached = getattr(self, "_btc_state_cache", None)
        if cached is not None and (now - cached[0]) < BTC_STATE_CACHE_TTL_SEC:
            return cached[1]
        try:
            btc_by_tf: Dict[str, Dict[str, Any]] = {}
            for _tf in _BTC_STATE_TF_WEIGHTS:
                _cd = self.data_store.get_candles("BTCUSDT", _tf)
                if _cd:
                    btc_by_tf[_tf] = _cd
            state = compute_btc_state(btc_by_tf)
        except Exception as _bs_exc:
            log.debug("BTC-State compute error (fail open, b=0): {}", _bs_exc)
            state = {"b": 0.0, "per_tf": {}, "status": "error"}
        self._btc_state_cache = (now, state)
        return state

    def _get_btc_macro_dir_cached(self) -> Dict[str, object]:
        """BTC macro DIRECTION (weekly slope + price-vs-fast-MA + structure), cached.

        The pair-independent cycle backdrop for the counter-trend-long scalp filter.
        Slow-moving, so it runs at most once per ``BTC_MACRO_CACHE_TTL_SEC`` and is
        reused across all pairs (Cost Discipline: ``get_candles`` is an in-memory
        lookup, no new I/O).  Fails to NEUTRAL / not-suppressed on any error — a
        suppression gate never fires on missing data.
        """
        now = time.monotonic()
        cached = getattr(self, "_btc_macro_dir_cache", None)
        if cached is not None and (now - cached[0]) < BTC_MACRO_CACHE_TTL_SEC:
            return cached[1]
        try:
            _cd = self.data_store.get_candles("BTCUSDT", BTC_MACRO_TF) or {}
            state = macro_direction(
                _cd.get("close", []),
                fast_period=BTC_MACRO_FAST_PERIOD,
                recover_period=BTC_MACRO_RECOVER_PERIOD,
                slow_period=BTC_MACRO_SLOW_PERIOD,
            )
        except Exception as _bm_exc:
            log.debug("BTC-macro-direction compute error (fail open): {}", _bm_exc)
            state = {"regime": "NEUTRAL", "longs_suppressed": False, "status": "error"}
        self._btc_macro_dir_cache = (now, state)
        return state

    def _ct_long_macro_suppressed(
        self, symbol: str, setup_class_name: str, direction: str,
    ) -> Tuple[bool, str]:
        """Should this counter-trend LONG scalp be suppressed by macro direction?

        Scalp-first guardrails: only LONG + a gated reversal setup is ever in scope;
        everything else returns ``(False, "")`` immediately.  Suppress if EITHER the
        BTC macro leg OR the coin's own trend reads DOWN ("a long needs both to
        permit it").  Auto-restores when either turns up.  Fails open (no
        suppression) on any error or missing data.
        """
        if not (
            CT_LONG_MACRO_GATE_ENABLED
            and (direction or "").upper() == "LONG"
            and (setup_class_name or "").upper() in CT_LONG_MACRO_GATE_SETUPS
        ):
            return False, ""
        try:
            if CT_LONG_MACRO_USE_BTC:
                _btc = self._get_btc_macro_dir_cached()
                if _btc.get("longs_suppressed"):
                    return True, f"btc_{_btc.get('regime')}"
            if CT_LONG_MACRO_USE_PER_COIN:
                _cd = self.data_store.get_candles(symbol, COIN_MACRO_TF) or {}
                _coin = macro_direction(
                    _cd.get("close", []),
                    fast_period=COIN_MACRO_FAST_PERIOD,
                    recover_period=COIN_MACRO_RECOVER_PERIOD,
                    slow_period=COIN_MACRO_SLOW_PERIOD,
                )
                if _coin.get("longs_suppressed"):
                    return True, f"coin_{_coin.get('regime')}"
        except Exception as _ctm_exc:
            log.debug(
                "CT-long macro gate error for {} (fail open): {}", symbol, _ctm_exc,
            )
        return False, ""

    def _ct_short_macro_would_suppress(
        self, symbol: str, setup_class_name: str, direction: str,
    ) -> Tuple[bool, str]:
        """Would the counter-trend-SHORT macro mirror suppress this scalp?

        Flag-INDEPENDENT predicate (the #597 shadow pattern): the gate and the
        [SHADOW] telemetry share this exact decision, so the shadow count can't
        drift from what activation would do.  Mirror of the CT-long gate:
        only SHORT + a gated reversal setup is in scope; suppress while EITHER
        the BTC macro leg OR the coin's own higher-TF trend reads UP ("a short
        needs both to permit it").  Auto-restores when the trend turns down.
        Fails open (no suppression) on any error or missing data.
        """
        if not (
            (direction or "").upper() == "SHORT"
            and (setup_class_name or "").upper() in CT_SHORT_MACRO_GATE_SETUPS
        ):
            return False, ""
        try:
            if CT_SHORT_MACRO_USE_BTC:
                _btc = self._get_btc_macro_dir_cached()
                if str(_btc.get("direction")) == "up":
                    return True, f"btc_{_btc.get('regime')}"
            if CT_SHORT_MACRO_USE_PER_COIN:
                _cd = self.data_store.get_candles(symbol, COIN_MACRO_TF) or {}
                _coin = macro_direction(
                    _cd.get("close", []),
                    fast_period=COIN_MACRO_FAST_PERIOD,
                    recover_period=COIN_MACRO_RECOVER_PERIOD,
                    slow_period=COIN_MACRO_SLOW_PERIOD,
                )
                if str(_coin.get("direction")) == "up":
                    return True, f"coin_{_coin.get('regime')}"
        except Exception as _cts_exc:
            log.debug(
                "CT-short macro predicate error for {} (fail open): {}",
                symbol, _cts_exc,
            )
        return False, ""

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
            except Exception as _cs_exc:
                fail_open.record("scanner.continuation_sweep_evidence", _cs_exc)

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
        _t_predict = time.monotonic()
        try:
            prediction = await self.predictive.predict(
                symbol, ctx.candles, ctx.ind_for_predict
            )
            self.predictive.adjust_tp_sl(sig, prediction)
            self.predictive.update_confidence(sig, prediction)
        except Exception as exc:
            log.debug("Predictive AI error for {}: {}", symbol, exc)
            self._stage_timing["predictive"] += time.monotonic() - _t_predict
            self._suppression_counters[
                f"predictive_revalidation_bypassed:{chan_name}:predictive_error"
            ] += 1
            self._suppression_counters[
                f"geometry_preserved_final:{chan_name}:{_setup_family}"
            ] += 1
            self._increment_path_funnel("geometry:final_live:preserved", chan_name, _setup_class_name)
            return
        self._stage_timing["predictive"] += time.monotonic() - _t_predict

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
        valid, reason, policy_scope = validate_geometry_against_policy(
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
        if policy_scope is not None:
            self._suppression_counters[
                f"geometry_rejected_final_policy:{chan_name}:{_setup_family}:{policy_scope}"
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
        if policy_scope is not None:
            self._increment_path_funnel(
                f"geometry:final_live:rejected_policy:{policy_scope}",
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

    def _refresh_level_book_if_stale(
        self, symbol: str, candles_by_tf: Dict[str, dict],
    ) -> None:
        """Rebuild the LevelBook for *symbol* when the per-symbol TTL elapsed.

        Discovery cost is < 100ms.  TTL of 1h means the budget per symbol is
        ~3600× cheaper than per-cycle refresh.  No-op when *symbol* has been
        refreshed recently or when no usable TF candles are present.

        Also refreshes the Volume Profile for *symbol* and injects
        POC/VAH/VAL into the LevelBook so confluence scoring picks them up.
        """
        now = time.time()
        last = self._level_book_refresh_ts.get(symbol)
        if last is not None and (now - last) < LEVEL_BOOK_REFRESH_SEC:
            return
        # Pick whichever of 1w / 1d / 4h / 1h candles are present.  1w added
        # 2026-05-06 to seed cycle-level S/R into the LevelBook (chartist-eye
        # seeding-gap fix).  ``LevelBook.refresh`` skips any TF whose data
        # is missing or has fewer than 20 bars.
        tf_inputs: Dict[str, dict] = {}
        for tf in ("1w", "1d", "4h", "1h"):
            cd = candles_by_tf.get(tf) if isinstance(candles_by_tf, dict) else None
            if isinstance(cd, dict) and cd.get("high") is not None:
                tf_inputs[tf] = cd
        if not tf_inputs:
            return

        # Refresh Volume Profile twice — micro (1h × 200 ≈ 8 days) and
        # macro (1d × 200 ≈ 6 months) — and pass both into LevelBook.refresh
        # so POC/VAH/VAL from each scope participate in clustering and
        # confluence scoring as additional zones.
        vp_results: list = []
        try:
            micro_candles = candles_by_tf.get("1h") or candles_by_tf.get("4h")
            if micro_candles is not None and micro_candles.get("volume") is not None:
                micro_vp = self.volume_profile_store.refresh_if_stale(
                    symbol, micro_candles,
                )
                if micro_vp is not None:
                    vp_results.append(micro_vp)
        except Exception as exc:
            log.debug("Micro VolumeProfile refresh failed for {}: {}", symbol, exc)

        try:
            macro_candles = candles_by_tf.get("1d")
            if macro_candles is not None and macro_candles.get("volume") is not None:
                macro_vp = self.volume_profile_store_macro.refresh_if_stale(
                    symbol, macro_candles,
                )
                if macro_vp is not None:
                    vp_results.append(macro_vp)
        except Exception as exc:
            log.debug("Macro VolumeProfile refresh failed for {}: {}", symbol, exc)

        try:
            self.level_book.refresh(symbol, tf_inputs, volume_profile=vp_results or None)
            self._level_book_refresh_ts[symbol] = now
        except Exception as exc:
            log.debug("LevelBook refresh failed for {}: {}", symbol, exc)

        # Structure tracker on 4h.  Same TTL semantics; cheap.
        try:
            cd_4h = candles_by_tf.get("4h")
            if isinstance(cd_4h, dict) and cd_4h.get("high") is not None:
                self.structure_tracker.refresh_if_stale(symbol, "4h", cd_4h)
        except Exception as exc:
            log.debug("StructureTracker refresh failed for {}: {}", symbol, exc)

    def _populate_signal_context(self, sig: Any, volume_24h: float, ctx: ScanContext) -> None:
        sig.market_phase = ctx.market_state.value
        if ctx.regime_context is None:
            # No regime context = the classifier had nothing to classify with.
            # Previously this left entry_regime/market_phase EMPTY, which the
            # ops Profit page rendered as "UNKNOWN" — hiding our single most
            # profitable cohort (7d study: empty-regime signals +26.3% vs
            # −26.1% for stamped ones). Almost always this is a fresh listing
            # / newly-promoted pair whose candle history is too short, so name
            # it: NEW_LISTING when the 1h history is thin, UNCLASSIFIED for
            # the rare established pair the classifier skipped.
            try:
                _c1h = ctx.candles.get("1h") if ctx.candles else None
                _closes_1h = (_c1h or {}).get("close")
                _hist_1h = len(_closes_1h) if _closes_1h is not None else 0
                _label = "NEW_LISTING" if _hist_1h < 30 else "UNCLASSIFIED"
            except (TypeError, AttributeError):
                _label = "UNCLASSIFIED"
            sig.entry_regime = _label
            sig.market_phase = _label
        if ctx.regime_context is not None:
            rc = ctx.regime_context
            sig.entry_regime = rc.label  # string assignment, cannot raise — set before float() calls
            try:
                sig.market_phase = (
                    f"{rc.label} | ATR%ile={float(rc.atr_percentile):.0f} | "
                    f"Vol={rc.volume_profile}"
                )
                sig.regime_context = (
                    f"ADXslope={float(rc.adx_slope):.2f} strengthen={rc.is_regime_strengthening}"
                )
                sig.atr_percentile_at_entry = float(rc.atr_percentile)
                sig.atr_value_at_entry = float(rc.atr_value)
            except (TypeError, ValueError):
                pass  # Keep market_state.value when context is not a real RegimeContext

        # Multi-timeframe regime stamp (Fix C): record the 15m regime at entry so
        # the exit logic only keeps TP2/TP3 runners when the higher timeframe
        # agrees with the trade direction — a 5m trend that is a pullback inside a
        # 15m range should not spawn a runner.  Uses the stateless array detector
        # so it never perturbs the per-symbol 5m hysteresis state.
        try:
            c15 = ctx.candles.get("15m") if ctx.candles else None
            if c15 and len(c15.get("close", [])) >= 30:
                closes = np.asarray(c15["close"], dtype=np.float64)
                highs = np.asarray(c15.get("high", closes), dtype=np.float64)
                lows = np.asarray(c15.get("low", closes), dtype=np.float64)
                vols = np.asarray(
                    c15.get("volume", np.zeros(len(closes))), dtype=np.float64
                )
                _tier_15m = getattr(
                    classify_pair_tier(
                        getattr(sig, "symbol", ""), volume_24h_usd=volume_24h
                    ),
                    "tier",
                    "MIDCAP",
                )
                sig.entry_regime_15m = detect_regime_from_arrays(
                    closes, highs, lows, vols, idx=len(closes) - 1,
                    pair_tier=_tier_15m,
                )
        except Exception as exc:
            log.debug(
                "15m regime stamp failed for {}: {}",
                getattr(sig, "symbol", "?"), exc,
            )
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
        # Pair-cohort (liquidity tier) for the edge matrix's Phase-5 cohort
        # dimension — stamped on every candidate so the dual-write feeders and
        # the cohort-aware emission policy can key on it.  Pure, fail-safe.
        try:
            from src.pair_cohort import classify_cohort as _classify_cohort
            sig.mc_pair_cohort = _classify_cohort(
                getattr(sig, "symbol", "") or "", volume_24h_usd=volume_24h
            )
        except Exception as _coh_exc:
            sig.mc_pair_cohort = ""
            fail_open.record("scanner.pair_cohort_stamp", _coh_exc)
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

    def _evaluate_shadow_strategies(self, symbol: str, ctx: ScanContext) -> None:
        """Run the shadow-only strategy units for one scanned symbol.

        Observe-only (Phase 3): each unit's would-be trade is stamped into the
        suppression-audit shadow ledger (``gate_name="shadow_unit:<name>"``)
        with the symbol's market-context key, then forward-measured by the
        5-min audit loop into the edge matrix (``source="shadow"``).  There is
        deliberately NO code path from here to the signal queue.

        Cost: pure list scans over in-memory 15m arrays + the cached funding
        read; a per-(unit, symbol) cooldown bounds ledger growth.  Fail-open.
        """
        try:
            from src import runtime_tunables as _rt
            if not bool(_rt.get("shadow_strategies_enabled")):
                return
            from src import shadow_strategies as _ss
            c15 = self._resolve_candles(ctx.candles, "15m") or {}
            highs = c15.get("high") or []
            lows = c15.get("low") or []
            closes = c15.get("close") or []
            if len(closes) < 60:
                return
            _funding = None
            if self.order_flow_store is not None:
                try:
                    _funding = self.order_flow_store.get_funding_rate(symbol)
                except Exception:
                    _funding = None
            candidates = _ss.evaluate_all(highs, lows, closes, funding_rate=_funding)
            if not candidates:
                return
            # One context build per symbol with a triggering unit (rare).
            _context_key = ""
            _regime_label = ""
            try:
                _regime_name = getattr(ctx.regime_result, "regime", None)
                _regime_label = str(
                    getattr(_regime_name, "value", _regime_name or "") or ""
                )
                _btc_b: Optional[float] = None
                if BTC_STATE_ENABLED:
                    _b_raw: Any = self._get_btc_state_cached().get("b", 0.0)
                    _btc_b = float(_b_raw or 0.0)
                _mc = build_market_context(
                    regime_label=_regime_label or None,
                    atr_percentile=getattr(ctx.regime_context, "atr_percentile", None),
                    funding_rate=_funding,
                    btc_state=_btc_b,
                )
                _context_key = _mc.context_key()
            except Exception as _mc_exc:
                fail_open.record("scanner.market_context_key", _mc_exc)
            from src import suppression_audit as _sa
            now_mono = time.monotonic()
            for cand in candidates:
                cd_key = (cand.strategy, symbol)
                # None = never stamped.  A 0.0 sentinel would silently swallow
                # every stamp for the first COOLDOWN seconds after boot,
                # because monotonic() starts near zero on a fresh host.
                last = self._shadow_last_stamp.get(cd_key)
                if last is not None and now_mono - last < SHADOW_STRATEGY_COOLDOWN_SEC:
                    continue
                self._shadow_last_stamp[cd_key] = now_mono
                _sa.stamp_candidate(
                    gate_name=f"shadow_unit:{cand.strategy}",
                    symbol=symbol,
                    channel="SHADOW",
                    setup_class=cand.strategy,
                    side=cand.side,
                    entry=cand.entry,
                    stop_loss=cand.stop_loss,
                    tp1=cand.tp1,
                    confidence=0.0,
                    context_key=_context_key,
                    regime=_regime_label,
                    valid_for_minutes=cand.valid_for_minutes,
                )
                log.debug(
                    "[SHADOW_UNIT] {} {} {} entry={:.6g} sl={:.6g} tp1={:.6g} — {}",
                    cand.strategy, symbol, cand.side,
                    cand.entry, cand.stop_loss, cand.tp1, cand.reason,
                )
        except Exception as exc:
            fail_open.record("scanner.shadow_strategies", exc)

    def _stamp_geometry_ab(self, sig: Any) -> None:
        """Stop-geometry A/B pair stamp for a post-scoring candidate.

        Observe-only + fail-open (Phase 3 item 8): stamps this candidate's
        fixed-% stop and its would-be ATR/structure stop as a counterfactual
        pair into the dedicated geometry ledger (own store — can't evict gate
        records), so the edge matrix measures which geometry wins per
        (strategy, context).  Candles are the already-warm in-memory 15m
        arrays; runs only on suppression/emission events, never per scanned
        symbol.  Never alters live geometry (B7).
        """
        try:
            from src import runtime_tunables as _rt
            from src import geometry_ab as _gab
            symbol = str(getattr(sig, "symbol", "") or "")
            if not symbol:
                return
            c15 = self.data_store.get_candles(symbol, "15m") or {}
            # The data store holds numpy arrays — `arr or []` raises ValueError
            # on multi-element arrays, and the fail-open except below would
            # swallow every stamp (the 2026-07-13→14 zero-pairs incident).
            highs = c15.get("high")
            lows = c15.get("low")
            closes = c15.get("close")
            if highs is None or lows is None or closes is None:
                return
            _direction = getattr(sig, "direction", None)
            _side = getattr(_direction, "value", None) or str(_direction or "")
            # Tuned-recipe arm for the measured-loser paths (own tunable —
            # keeps measuring even if the stop A/B is toggled off; owner
            # 2026-07-16: "tune, don't disable").  Fail-open in its own site.
            try:
                from src import tuned_variants as _tv
                if (
                    str(getattr(sig, "setup_class", "") or "").upper() in _tv.tuned_setups()
                    and bool(_rt.get("tuned_variants_enabled"))
                ):
                    _tv.stamp_tuned_variant(
                        symbol=symbol,
                        channel=str(getattr(sig, "channel", "") or ""),
                        setup_class=str(getattr(sig, "setup_class", "") or ""),
                        side=_side,
                        entry=float(getattr(sig, "entry", 0.0) or 0.0),
                        highs=highs,
                        lows=lows,
                        closes=closes,
                        confidence=float(getattr(sig, "confidence", 0.0) or 0.0),
                        context_key=str(getattr(sig, "mc_context_key", "") or ""),
                        regime=str(getattr(sig, "entry_regime", "") or ""),
                        valid_for_minutes=float(getattr(sig, "valid_for_minutes", 0.0) or 0.0),
                    )
            except Exception as _tv_exc:
                fail_open.record("scanner.stamp_tuned_variant", _tv_exc)
            if not bool(_rt.get("geometry_ab_enabled")):
                return
            alt_stop = _gab.stamp_geometry_pair(
                symbol=symbol,
                channel=str(getattr(sig, "channel", "") or ""),
                setup_class=str(getattr(sig, "setup_class", "") or ""),
                side=_side,
                entry=float(getattr(sig, "entry", 0.0) or 0.0),
                stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
                tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
                highs=highs,
                lows=lows,
                closes=closes,
                confidence=float(getattr(sig, "confidence", 0.0) or 0.0),
                context_key=str(getattr(sig, "mc_context_key", "") or ""),
                regime=str(getattr(sig, "entry_regime", "") or ""),
                valid_for_minutes=float(getattr(sig, "valid_for_minutes", 0.0) or 0.0),
            )
            if alt_stop is not None:
                # Stamp the would-be effect on the signal itself
                # (stamp-and-shadow doctrine) — consumed by nothing.
                sig.geo_atr_stop = float(alt_stop)
        except Exception as exc:
            fail_open.record("scanner.stamp_geometry_ab", exc)

    def _stamp_suppressed(self, sig: Any, gate_name: str) -> None:
        """Shadow-ledger stamp for a post-scoring suppressed candidate.

        Observe-only + fail-open (Layer C): records the candidate's tradeable
        geometry into the in-memory suppression audit (O(1) deque append, no
        I/O) so the 5-min audit loop can forward-measure on real candles
        whether this gate saved or cost us.  Never alters the suppression
        decision itself — callers stamp immediately before their existing
        suppress return, which stays byte-identical.
        """
        # Suppressed candidates are half the geometry A/B's sample — stamp the
        # pair regardless of whether the suppression audit itself is enabled
        # (each measurement has its own tunable).
        try:
            self._stamp_geometry_ab(sig)
        except Exception as exc:
            # _stamp_geometry_ab records its own failures internally; this
            # outer guard is effectively unreachable, counted for completeness.
            fail_open.record("scanner.stamp_suppressed_geo", exc)
        try:
            from src import runtime_tunables as _rt
            if not bool(_rt.get("suppression_audit_enabled")):
                return
            from src import suppression_audit as _sa
            _direction = getattr(sig, "direction", None)
            _side = getattr(_direction, "value", None) or str(_direction or "")
            _sa.stamp_candidate(
                gate_name=gate_name,
                symbol=str(getattr(sig, "symbol", "") or ""),
                channel=str(getattr(sig, "channel", "") or ""),
                setup_class=str(getattr(sig, "setup_class", "") or ""),
                side=_side,
                entry=float(getattr(sig, "entry", 0.0) or 0.0),
                stop_loss=float(getattr(sig, "stop_loss", 0.0) or 0.0),
                tp1=float(getattr(sig, "tp1", 0.0) or 0.0),
                confidence=float(getattr(sig, "confidence", 0.0) or 0.0),
                context_key=str(getattr(sig, "mc_context_key", "") or ""),
                regime=str(getattr(sig, "entry_regime", "") or ""),
                valid_for_minutes=float(getattr(sig, "valid_for_minutes", 0.0) or 0.0),
                pair_cohort=str(getattr(sig, "mc_pair_cohort", "") or ""),
            )
        except Exception as exc:
            fail_open.record("scanner.stamp_suppressed", exc)

    async def _enqueue_signal(self, sig: Any) -> bool:
        self._stamp_origin_setup_identity(sig, getattr(sig, "channel", "") or "UNKNOWN")
        try:
            entry = float(getattr(sig, "entry", 0) or 0)
            sl    = float(getattr(sig, "stop_loss", 0) or 0)
            atr   = float(getattr(sig, "atr_val", 0) or 0)
            direction = getattr(sig, "direction", None)
            if entry > 0 and sl > 0 and direction is not None:
                sl_dist = abs(entry - sl)
                min_dist = max(entry * 0.0080, atr * 1.0 if atr > 0 else 0.0)
                if sl_dist < min_dist:
                    is_long = direction.value == "LONG" if hasattr(direction, "value") else str(direction).upper() == "LONG"
                    new_sl = entry - min_dist if is_long else entry + min_dist
                    ratio  = min_dist / sl_dist if sl_dist > 0 else 1.0
                    sig.stop_loss = round(new_sl, 8)
                    sig.original_sl_distance = min_dist
                    for tp_attr in ("tp1", "tp2", "tp3"):
                        tp_val = float(getattr(sig, tp_attr, 0) or 0)
                        if tp_val > 0:
                            new_tp = entry + abs(entry - tp_val) * ratio if is_long else entry - abs(entry - tp_val) * ratio
                            setattr(sig, tp_attr, round(new_tp, 8))
        except Exception as _mind_exc:
            # This block MUTATES sig.stop_loss then rescales the TPs — an
            # exception mid-loop leaves half-rescaled geometry, which is
            # exactly the kind of failure that must page, not vanish.
            fail_open.record("scanner.min_distance_geometry", _mind_exc)

        # ── Active-duplicate guard (2026-07-09, dark-flagged) ────────────
        # The dispatch cooldown below intends "never two live copies of the
        # same setup", but it does not survive every restart path — SPCXUSDT
        # MOVER_TREND_PULLBACK SHORT emitted twice 7 minutes apart at an
        # identical entry/SL on 2026-07-08 while the first copy was still
        # open.  Checking the live signal book is restart-proof: if an open
        # signal with the same (symbol, setup_class, direction) exists,
        # block (or shadow-log, while the tunable is OFF) this dispatch.
        # O(active book) per dispatch attempt — dispatches are rare and the
        # book is small; no reads, no I/O.
        try:
            dup_key = self._cooldown_key_for(sig)
            if dup_key is not None:
                _dup = next(
                    (
                        s for s in self.router.active_signals.values()
                        if self._cooldown_key_for(s) == dup_key
                    ),
                    None,
                )
                if _dup is not None:
                    from src import runtime_tunables as _rt
                    if bool(_rt.get("active_dup_guard_enabled")):
                        self._suppression_counters[
                            f"active_dup:{dup_key[1]}"
                        ] += 1
                        self._suppression_counters[
                            f"enqueue_stage:active_dup:{dup_key[1]}"
                        ] += 1
                        log.info(
                            "active_dup skip {} {} {} (open signal_id={})",
                            dup_key[0], dup_key[1], dup_key[2],
                            getattr(_dup, "signal_id", "?"),
                        )
                        # Real-suppress branch only — the shadow branch below
                        # falls through to emission and is measured as emitted.
                        self._stamp_suppressed(sig, "active_dup")
                        return False
                    self._suppression_counters[
                        f"active_dup_shadow:{dup_key[1]}"
                    ] += 1
                    log.info(
                        "[SHADOW] ACTIVE_DUP_WOULD_BLOCK: {} {} {} "
                        "(open signal_id={})",
                        dup_key[0], dup_key[1], dup_key[2],
                        getattr(_dup, "signal_id", "?"),
                    )
        except Exception as exc:
            log.debug("active-dup guard error (fail-open): {}", exc)

        # ── Per-(symbol, setup, direction) dispatch cooldown ─────────────
        # Prevents the same setup from re-firing within DISPATCH_COOLDOWN_SEC
        # after a successful dispatch.  Without this, the same FAILED_AUCTION
        # _RECLAIM pattern keeps re-detecting every cycle (15s) and dispatches
        # bit-identical signals to Telegram (bug 2026-05-07: 5 identical
        # BNBUSDT FAR signals in 5 h).
        try:
            cd_key = self._cooldown_key_for(sig)
            if (
                cd_key is not None
                and _dispatch_cooldown_enabled()
                and self._is_cooldown_active(cd_key)
            ):
                remaining_s = self._dispatch_cooldown[cd_key] - time.time()
                self._suppression_counters[
                    f"dispatch_cooldown:{cd_key[1]}"
                ] += 1
                self._suppression_counters[
                    f"enqueue_stage:dispatch_cooldown:{cd_key[1]}"
                ] += 1
                log.info(
                    "dispatch_cooldown skip {} {} {} ({:.0f}s remaining)",
                    cd_key[0], cd_key[1], cd_key[2], max(0.0, remaining_s),
                )
                self._stamp_suppressed(sig, "dispatch_cooldown")
                return False
        except Exception as exc:
            log.debug("dispatch cooldown check error (fail-open): {}", exc)

        # ── Pre-dispatch data-staleness check ────────────────────────────
        # Reject dispatch when the most-recent 1m kline for the symbol is
        # older than MAX_KLINE_STALENESS_SEC.  Defends against frozen feeds
        # (e.g. promoted pairs whose WS subscription hasn't caught up,
        # dropped streams without recovery) that would otherwise dispatch
        # signals against stale candle data and report deterministic
        # micro-loss closes.  Bug 2026-05-11: QUSDT was promoted into the
        # universe but its 1m kline stream was silent for 30+ minutes;
        # 5+ SR_FLIP signals dispatched at identical entry/SL/exit,
        # all closing at the same frozen -0.10358%.  This check catches
        # the symptom regardless of WHY the feed is stale (subscription
        # gap / stream death / REST-fallback misalignment).
        try:
            if not self._is_kline_data_fresh(sig):
                _sc = getattr(sig, "setup_class", "UNKNOWN")
                self._suppression_counters[f"data_stale:{_sc}"] += 1
                self._suppression_counters[f"enqueue_stage:data_stale:{_sc}"] += 1
                log.info(
                    "data_stale skip {} {} entry={:.6f}",
                    getattr(sig, "symbol", "?"),
                    _sc,
                    float(getattr(sig, "entry", 0.0) or 0.0),
                )
                self._stamp_suppressed(sig, "data_stale")
                return False
        except Exception as exc:
            log.debug("data-staleness check error (fail-open): {}", exc)

        # ── Pre-dispatch staleness check ─────────────────────────────────
        # If real-time price has drifted >DISPATCH_STALENESS_MAX_DRIFT_PCT from
        # the proposed entry, the signal is stale — by the time the subscriber
        # reads it, price is too far away for the limit order to fill at sane
        # levels.  Worst case (bug 2026-05-07): current_price already at SL,
        # signal dispatches and immediately invalidates.
        try:
            if not self._is_entry_fresh(sig):
                _sc = getattr(sig, "setup_class", "UNKNOWN")
                self._suppression_counters[f"dispatch_staleness:{_sc}"] += 1
                self._suppression_counters[f"enqueue_stage:dispatch_staleness:{_sc}"] += 1
                log.info(
                    "dispatch_staleness skip {} {} entry={:.6f} drifted",
                    getattr(sig, "symbol", "?"),
                    _sc,
                    float(getattr(sig, "entry", 0.0) or 0.0),
                )
                self._stamp_suppressed(sig, "dispatch_staleness")
                return False
        except Exception as exc:
            log.debug("staleness check error (fail-open): {}", exc)

        # ── Level-rearm gate ─────────────────────────────────────────────
        # Block stuck-level repeat-fires from level-anchored evaluators
        # (SR_FLIP_RETEST / VSB / BDS / FAR all anchor `entry` to a
        # historical structural level).  After a successful dispatch at a
        # level, additional dispatches at the same level (within
        # LEVEL_REARM_BUCKET_BPS) are blocked until price has travelled
        # the SL-distance-derived excursion threshold away from the level
        # — see LevelInPlayState / _is_level_in_play / _record_level_in_play.
        # Bug observed 2026-05-13: ETHUSDT SR_FLIP SHORT dispatched 13×
        # over 26h at identical entry while price chopped within 0.3%.
        try:
            if self._is_level_in_play(sig):
                _sc = getattr(sig, "setup_class", "UNKNOWN")
                self._suppression_counters[f"level_still_in_play:{_sc}"] += 1
                self._suppression_counters[f"enqueue_stage:level_still_in_play:{_sc}"] += 1
                log.info(
                    "level_still_in_play skip {} {} entry={:.8f} — awaiting genuine excursion",
                    getattr(sig, "symbol", "?"),
                    _sc,
                    float(getattr(sig, "entry", 0.0) or 0.0),
                )
                self._stamp_suppressed(sig, "level_still_in_play")
                return False
        except Exception as exc:
            log.debug("level-in-play check error (fail-open): {}", exc)

        # ── Regime Kill Switch ────────────────────────────────────────────
        # Block dispatch when BTC is in a whipsaw regime (direction efficiency
        # < threshold over the last 4h of 15m candles).  Tape-driven setups
        # (WHALE_MOMENTUM / FUNDING_EXTREME_SIGNAL / LIQUIDATION_REVERSAL)
        # are exempt — their thesis is to trade the chaos, not avoid it.
        # Fails-open when BTC data is unavailable (warmup, feed drop).
        try:
            _btc_15m = self.data_store.get_candles("BTCUSDT", "15m") or {}
            _rks_blocked, _rks_reason = self._regime_kill_switch.check(sig, _btc_15m)
            if _rks_blocked:
                _sc_rks = getattr(sig, "setup_class", "UNKNOWN")
                self._suppression_counters[f"regime_kill:{_sc_rks}"] += 1
                self._suppression_counters["enqueue_stage:regime_kill"] += 1
                log.info(
                    "regime_kill skip {} {} — {}",
                    getattr(sig, "symbol", "?"),
                    _sc_rks,
                    _rks_reason,
                )
                self._stamp_suppressed(sig, "regime_kill")
                return False
        except Exception as exc:
            log.debug("regime-kill check error (fail-open): {}", exc)

        # Stamp pre-TP threshold + trigger price using the ATR observed at
        # dispatch.  Locks the promise shown in the Telegram post; trade-
        # monitor and persistence both round-trip the stamped values.  No-op
        # when pre-TP is disabled or the setup is in the breakout blacklist.
        try:
            stamp_pre_tp(sig)
        except Exception as exc:
            log.debug("pre-TP stamp failed for %s: %s", getattr(sig, "symbol", "?"), exc)

        # Stamp cooldown on success.  Only persist after queue.put succeeds
        # (so a queue overflow doesn't lock out future legitimate signals).
        ok = await self.signal_queue.put(sig)
        _sc_final = getattr(sig, "setup_class", "UNKNOWN")
        if ok:
            self._suppression_counters[f"enqueue_stage:emitted:{_sc_final}"] += 1
            # Emitted candidates are the other half of the stop-geometry A/B
            # sample (observe-only; stamps the pair + sig.geo_atr_stop).
            self._stamp_geometry_ab(sig)
            try:
                cd_key = self._cooldown_key_for(sig)
                if cd_key is not None and _dispatch_cooldown_enabled():
                    self._dispatch_cooldown[cd_key] = time.time() + _dispatch_cooldown_sec()
                    self._persist_dispatch_cooldown()
            except Exception as exc:
                log.debug("cooldown stamp error (non-fatal): {}", exc)
            # Stamp the dispatched level into the registry so the next
            # candidate at the same level is blocked until price excursion.
            try:
                self._record_level_in_play(sig)
            except Exception as exc:
                log.debug("level-in-play stamp error (non-fatal): {}", exc)
        else:
            self._suppression_counters[f"enqueue_stage:queue_put_failed:{_sc_final}"] += 1
            log.warning(
                "signal_queue.put returned False for {} {} — queue full or backend unavailable",
                getattr(sig, "symbol", "?"), _sc_final,
            )
        return ok

    @staticmethod
    def _cooldown_key_for(sig: Any) -> Optional[tuple]:
        """Build the ``(symbol, setup_class, direction)`` cooldown key."""
        symbol = getattr(sig, "symbol", "") or ""
        setup_class = getattr(sig, "setup_class", "") or ""
        direction_obj = getattr(sig, "direction", None)
        direction = (
            direction_obj.value
            if direction_obj is not None and hasattr(direction_obj, "value")
            else str(direction_obj or "")
        ).upper()
        if not symbol or not setup_class or not direction:
            return None
        return (symbol, setup_class, direction)

    def _is_cooldown_active(self, key: tuple) -> bool:
        # Stored value is the EXPIRY timestamp (``time.time() + duration``);
        # active iff now < expiry.  Migration: legacy entries persisted as
        # last-dispatch timestamps appear in the past, so the comparison
        # below naturally treats them as expired (no spurious lockout).
        expiry = self._dispatch_cooldown.get(key)
        if expiry is None:
            return False
        return time.time() < expiry

    def _is_entry_fresh(self, sig: Any) -> bool:
        """Return True if the proposed entry is within tolerance of current price.

        ``current_price`` is the last close on the most-granular available
        candle TF for this signal's channel.  Drift > 0.5% (default) means
        the setup-detection candles are stale relative to live ticks — the
        signal would dispatch into a price level price has already left.
        """
        try:
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
            if entry <= 0:
                return True
            symbol = getattr(sig, "symbol", "")
            if not symbol:
                return True
            data_store = getattr(self, "data_store", None)
            if data_store is None:
                return True
            # Look up the most-granular candle for this symbol.
            symbol_candles = (
                data_store.candles.get(symbol)
                if hasattr(data_store, "candles") else None
            )
            if not symbol_candles:
                return True
            # Prefer 1m, fall back to 5m / 15m / 1h.
            for tf in ("1m", "5m", "15m", "1h"):
                cd = symbol_candles.get(tf)
                if not cd or "close" not in cd:
                    continue
                closes = cd["close"]
                if closes is None or len(closes) == 0:
                    continue
                current_price = float(closes[-1])
                if current_price <= 0:
                    continue
                drift_pct = abs(current_price - entry) / entry * 100.0
                return drift_pct <= DISPATCH_STALENESS_MAX_DRIFT_PCT
        except Exception:
            return True  # Fail-open
        return True

    def _is_kline_data_fresh(self, sig: Any) -> bool:
        """Return True if the symbol's most-recent 1m kline is fresh enough
        to dispatch a signal against.

        Reads ``HistoricalDataStore.last_kline_age_seconds(symbol, "1m")``.
        Two cases are distinguished:

        * ``age is None`` — no timestamp has been stamped yet.  Engine just
          booted and seed-loaded candles via REST/bulk-seed (which writes
          OHLC into the candle store without stamping
          ``_last_kline_update_ts``; only live ``update_candle`` calls
          from WS frames stamp it).  Fail-OPEN here: blocking dispatch
          until the first WS frame arrives caused a 15-min signal
          blackout after every restart (2026-05-12 — WS watchdog took
          903s to detect a silent post-boot subscription, and the
          data-staleness gate killed every dispatch attempt in the
          meantime).  Matches the fail-open doctrine used by
          ``_is_pair_structurally_aged`` on missing accessor.
        * ``age > MAX_KLINE_STALENESS_SEC`` — pair *has* been observed
          but the feed has gone silent.  This is the QUSDT-class
          pathology PR #359 was designed to catch: frozen feed,
          deterministic-loss carbon-copy emissions.  Hard-block.

        Fail-open on any unexpected store shape (missing accessor) to
        avoid suppressing legitimate signals on harness / test contexts.
        """
        try:
            symbol = getattr(sig, "symbol", "")
            if not symbol:
                return True
            data_store = getattr(self, "data_store", None)
            if data_store is None or not hasattr(data_store, "last_kline_age_seconds"):
                return True
            age = data_store.last_kline_age_seconds(symbol, "1m")
            if age is None:
                # No live kline observed yet (post-boot, pre-first-WS-frame).
                # Fail-OPEN — see docstring for rationale.
                return True
            return age <= MAX_KLINE_STALENESS_SEC
        except Exception:
            return True  # Fail-open

    def _is_pair_structurally_aged(self, symbol: str) -> bool:
        """Return True if the pair has enough 1d-anchored LevelBook levels
        for structure-based evaluators to evaluate honestly.

        Structure paths (SR_FLIP / FAR / QCB / TPE / DIV_CONT / CLS /
        PDC / MA_CROSS / STANDARD) need the multi-TF level book to
        contain at least ``MIN_1D_LEVELS_FOR_STRUCTURE_PATHS`` levels
        anchored on 1d swing pivots before their thesis is statistically
        sound.  Newly-promoted pairs typically take days to build that
        history.

        Fail-open on missing accessor / store so unit tests that don't
        wire LevelBook don't lose legitimate signals.  The cost of a
        false-negative here is one carbon-copy emission slipping through
        until the next scan cycle; the data-staleness gate (PR #359) is
        the second line of defence.
        """
        try:
            level_book = getattr(self, "level_book", None)
            if level_book is None or not hasattr(level_book, "stats"):
                return True
            stats = level_book.stats(symbol)
            if not isinstance(stats, dict):
                return True
            from_1d = int(stats.get("from_1d", 0) or 0)
            return from_1d >= MIN_1D_LEVELS_FOR_STRUCTURE_PATHS
        except Exception:
            return True  # Fail-open

    def _load_dispatch_cooldown(self) -> None:
        """Load the cooldown registry from disk on init.  Best-effort."""
        from pathlib import Path
        path = Path(DISPATCH_COOLDOWN_PATH)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        for key, ts in data.items():
            if not isinstance(key, str) or "|" not in key:
                continue
            parts = key.split("|", 2)
            if len(parts) != 3:
                continue
            try:
                self._dispatch_cooldown[(parts[0], parts[1], parts[2])] = float(ts)
            except (ValueError, TypeError):
                continue

    def _persist_dispatch_cooldown(self) -> None:
        """Atomically write the cooldown registry to disk."""
        from pathlib import Path
        path = Path(DISPATCH_COOLDOWN_PATH)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                f"{symbol}|{setup}|{direction}": ts
                for (symbol, setup, direction), ts in self._dispatch_cooldown.items()
            }
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            tmp.replace(path)
        except OSError as exc:
            log.debug("dispatch cooldown persist failed: %s", exc)

    def _load_loss_streaks(self) -> None:
        """Load the consecutive-loss streak registry from disk.  Best-effort."""
        from pathlib import Path
        path = Path(LOSS_STREAK_PATH)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        for key, streak in data.items():
            if not isinstance(key, str) or "|" not in key:
                continue
            parts = key.split("|", 2)
            if len(parts) != 3:
                continue
            try:
                self._loss_streaks[(parts[0], parts[1], parts[2])] = int(streak)
            except (ValueError, TypeError):
                continue

    def _persist_loss_streaks(self) -> None:
        """Atomically write the loss-streak registry to disk.  Writes happen
        only on outcome resolution (~dozens/day) — never on the scan path."""
        from pathlib import Path
        path = Path(LOSS_STREAK_PATH)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                f"{symbol}|{setup}|{direction}": streak
                for (symbol, setup, direction), streak in self._loss_streaks.items()
            }
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            tmp.replace(path)
        except OSError as exc:
            log.debug("loss streak persist failed: %s", exc)

    # ------------------------------------------------------------------
    # Level-rearm state machine — see LevelInPlayState dataclass and the
    # LEVEL_REARM_* knobs in config/__init__.py.
    # ------------------------------------------------------------------

    @staticmethod
    def _level_bucket(price: float) -> float:
        """Round ``price`` to ``LEVEL_REARM_BUCKET_BPS`` granularity so
        clustering noise (2305.32 vs 2305.33 on different cycles) keys to
        the same bucket.  Multiplier = 10000 / BUCKET_BPS gives 2000 for
        the default 5 bps.
        """
        if price <= 0:
            return 0.0
        multiplier = max(1, 10_000 // max(1, LEVEL_REARM_BUCKET_BPS))
        return round(price * multiplier) / multiplier

    @staticmethod
    def _compute_rearm_threshold_pct(entry: float, stop_loss: float) -> float:
        """Return the |move from level| % required to re-arm.

        Derived from SL distance (which is ATR-calibrated per evaluator at
        signal creation, so it tracks pair volatility automatically) —
        ``LEVEL_REARM_SL_MULTIPLIER × sl_distance`` is the "decisive move
        past thesis" benchmark.  Clamped to env-tunable floor / ceiling so
        very tight or very wide SLs don't produce pathological gates.
        """
        if entry <= 0 or stop_loss <= 0:
            return LEVEL_REARM_FALLBACK_PCT
        sl_distance_pct = abs(stop_loss - entry) / entry
        raw = LEVEL_REARM_SL_MULTIPLIER * sl_distance_pct
        return max(LEVEL_REARM_FLOOR_PCT, min(LEVEL_REARM_CEILING_PCT, raw))

    def _level_in_play_key(self, sig: Any) -> Optional[Tuple[str, str, float]]:
        """Compose ``(symbol, direction, level_bucket)`` from a Signal.
        Returns ``None`` when any component is missing — caller should
        treat that as fail-open (no gating)."""
        symbol = getattr(sig, "symbol", "") or ""
        direction_obj = getattr(sig, "direction", None)
        direction = (
            direction_obj.value
            if direction_obj is not None and hasattr(direction_obj, "value")
            else str(direction_obj or "")
        ).upper()
        try:
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
        except (TypeError, ValueError):
            return None
        if not symbol or not direction or entry <= 0:
            return None
        return (symbol, direction, self._level_bucket(entry))

    def _find_matching_level(
        self, sig: Any
    ) -> Tuple[Optional[Tuple[str, str, float]], Optional[LevelInPlayState]]:
        """Return ``(key, state)`` for an in-play level matching ``sig``.

        Membership uses both the bucket key (cheap O(1) lookup) AND a
        tolerance check against the stored level_price (defense against
        boundary-spanning levels: 2305.314 buckets to 2305.31 while
        2305.318 buckets to 2305.32, but both sit inside the 5 bps zone
        around either).  Iteration is O(N) where N is small (level
        registry is typically <50 entries total).
        """
        key = self._level_in_play_key(sig)
        if key is None:
            return None, None
        # Fast path: exact bucket match.
        state = self._level_in_play.get(key)
        if state is not None:
            return key, state
        # Slow path: tolerance check for boundary-spanning buckets.
        try:
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
        except (TypeError, ValueError):
            return None, None
        symbol, direction, _ = key
        tolerance = LEVEL_REARM_BUCKET_BPS / 10_000.0
        for (s, d, _b), st in self._level_in_play.items():
            if s != symbol or d != direction or st.level_price <= 0:
                continue
            if abs(entry - st.level_price) / st.level_price <= tolerance:
                return (s, d, _b), st
        return None, None

    def _is_level_in_play(self, sig: Any) -> bool:
        """True if a level matching ``sig`` is currently in play (blocked).

        Side effect: opportunistically updates the matched entry's
        ``max_excursion_pct`` against current price, and drops it if the
        threshold or TTL has been crossed (so a stale level doesn't
        falsely block a fresh dispatch).

        Fail-OPEN when the data store has no 1m close data for the
        symbol — we can't measure excursion, so we can't honestly say
        the level is still in play.  Mirrors the fail-open doctrine
        used by ``_is_kline_data_fresh`` (missing accessor) and
        ``_is_entry_fresh`` (no candles).  Also makes the gate
        naturally inert in unit-test harnesses that mock ``data_store``
        without seeding 1m candle data.
        """
        key, state = self._find_matching_level(sig)
        if key is None or state is None:
            return False
        # Fail-OPEN when we can't read current price.
        try:
            symbol = key[0]
            data_store = getattr(self, "data_store", None)
            if data_store is None or not hasattr(data_store, "candles"):
                return False
            candles_for_symbol = data_store.candles
            if not isinstance(candles_for_symbol, dict):
                return False
            tf_data = candles_for_symbol.get(symbol, {})
            if not isinstance(tf_data, dict):
                return False
            tf = tf_data.get("1m") or tf_data.get("5m")
            if not tf or "close" not in tf:
                return False
            closes = tf["close"]
            if closes is None or len(closes) == 0:
                return False
        except (TypeError, AttributeError):
            return False
        # We have price data — tick the excursion update and re-check.
        try:
            self._tick_level_state(key, state)
        except Exception as exc:
            log.debug("level excursion tick failed for %s: %s", key, exc)
        # If the tick removed the entry (threshold or TTL crossed), it's
        # no longer in play.
        return key in self._level_in_play

    def _tick_level_state(
        self, key: Tuple[str, str, float], state: LevelInPlayState
    ) -> None:
        """Update ``max_excursion_pct`` against current 1m close, and drop
        the entry when it crosses the threshold or TTL."""
        symbol = key[0]
        # TTL drop — regime has likely shifted; let detector re-discover.
        if time.time() - state.dispatched_at > LEVEL_REARM_TTL_SEC:
            self._level_in_play.pop(key, None)
            self._persist_level_in_play()
            return
        # Excursion update — read most-recent 1m close (mirrors the
        # pattern used by _is_entry_fresh).
        data_store = getattr(self, "data_store", None)
        if data_store is None:
            return
        try:
            symbol_candles = (
                data_store.candles.get(symbol, {})
                if hasattr(data_store, "candles")
                else {}
            )
            tf = symbol_candles.get("1m") or symbol_candles.get("5m")
            if not tf or "close" not in tf or tf["close"] is None or len(tf["close"]) == 0:
                return
            current = float(tf["close"][-1])
            if current <= 0 or state.level_price <= 0:
                return
            excursion = abs(current - state.level_price) / state.level_price
        except (TypeError, ValueError, IndexError):
            return
        if excursion > state.max_excursion_pct:
            state.max_excursion_pct = excursion
        if state.max_excursion_pct >= state.threshold_pct:
            # Real move observed → re-arm.
            self._level_in_play.pop(key, None)
            self._persist_level_in_play()
            log.info(
                "level rearm: {} {} level={:.8f} excursion={:.4%} threshold={:.4%}",
                key[0], key[1], state.level_price,
                state.max_excursion_pct, state.threshold_pct,
            )

    def _update_level_excursions(self, symbol: str) -> None:
        """Walk the registry for ``symbol`` and tick every matching entry.
        Called once per ``_scan_symbol`` cycle so excursions stay current
        even when no candidate is being dispatched.
        """
        # Snapshot keys so deletes inside _tick_level_state don't break iteration.
        for key in [k for k in self._level_in_play.keys() if k[0] == symbol]:
            state = self._level_in_play.get(key)
            if state is None:
                continue
            try:
                self._tick_level_state(key, state)
            except Exception as exc:
                log.debug("level excursion update failed for {}: {}", key, exc)

    def _record_level_in_play(self, sig: Any) -> None:
        """Stamp a successfully-dispatched level into the registry.
        Idempotent — overwrites any existing entry at the same bucket
        with a fresh state (zero excursion, current timestamp)."""
        key = self._level_in_play_key(sig)
        if key is None:
            return
        try:
            entry = float(getattr(sig, "entry", 0.0) or 0.0)
            stop_loss = float(getattr(sig, "stop_loss", 0.0) or 0.0)
        except (TypeError, ValueError):
            return
        threshold = self._compute_rearm_threshold_pct(entry, stop_loss)
        self._level_in_play[key] = LevelInPlayState(
            level_price=entry,
            dispatched_at=time.time(),
            threshold_pct=threshold,
            max_excursion_pct=0.0,
        )
        self._persist_level_in_play()

    def _load_level_in_play(self) -> None:
        """Load the level-in-play registry from disk on init.  Best-effort."""
        from pathlib import Path
        path = Path(LEVEL_IN_PLAY_PATH)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return
        for key, payload in data.items():
            if not isinstance(key, str) or "|" not in key:
                continue
            parts = key.split("|", 2)
            if len(parts) != 3:
                continue
            try:
                bucket = float(parts[2])
                state = LevelInPlayState(
                    level_price=float(payload.get("level_price", 0.0)),
                    dispatched_at=float(payload.get("dispatched_at", 0.0)),
                    threshold_pct=float(payload.get("threshold_pct", LEVEL_REARM_FALLBACK_PCT)),
                    max_excursion_pct=float(payload.get("max_excursion_pct", 0.0)),
                )
            except (ValueError, TypeError, AttributeError):
                continue
            if state.level_price <= 0 or state.dispatched_at <= 0:
                continue
            self._level_in_play[(parts[0], parts[1], bucket)] = state

    def _persist_level_in_play(self) -> None:
        """Atomically write the level-in-play registry to disk."""
        from pathlib import Path
        path = Path(LEVEL_IN_PLAY_PATH)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                f"{symbol}|{direction}|{bucket}": {
                    "level_price": state.level_price,
                    "dispatched_at": state.dispatched_at,
                    "threshold_pct": state.threshold_pct,
                    "max_excursion_pct": state.max_excursion_pct,
                }
                for (symbol, direction, bucket), state in self._level_in_play.items()
            }
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            tmp.replace(path)
        except OSError as exc:
            log.debug("level-in-play persist failed: %s", exc)

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
        # Per-type soft-penalty breakdown for the confidence_gate log line.
        # Truth-report parser surfaces this as a `soft_penalties(...)` group
        # so we can attribute which gate is dragging confidence down.  Without
        # this, the aggregate "penalty" number masks WHICH penalty fired —
        # e.g. is it HTF mismatch, OI flip, VWAP overextension, or a cluster
        # gate?  Each soft-gate accumulator below appends to this dict.
        _soft_penalty_by_type: Dict[str, float] = {}
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
        if (
            chan_name == "360_SCALP"
            and ctx.is_ranging
            and ctx.adx_val < _RANGING_ADX_SUPPRESS_THRESHOLD
        ):
            _regime_name = self._regime_name_from_ctx(ctx, default="RANGING")
            _htf_aligned = bool(getattr(sig, "htf_trend_aligned", False))
            if self._is_scalp_family_blocked_in_ranging_low_adx(
                _setup_family, _setup_class_name, _htf_aligned
            ):
                self._suppression_counters[f"ranging_low_adx:{chan_name}"] += 1
                self._suppression_counters[
                    f"ranging_low_adx:family_block:{chan_name}:{_setup_family}"
                ] += 1
                self._suppression_counters[
                    f"ranging_low_adx:setup_block:{chan_name}:{_setup_class_name}"
                ] += 1
                self.suppression_tracker.record(SuppressionEvent(
                    symbol=symbol,
                    channel=chan_name,
                    reason="ranging_low_adx_family_block",
                    regime=_regime_name,
                    would_be_confidence=getattr(sig, "confidence", None),
                ))
                log.debug(
                    "Rejected {} {} setup={} family={} (RANGING low ADX {:.1f})",
                    symbol,
                    chan_name,
                    _setup_class_name,
                    _setup_family,
                    ctx.adx_val,
                )
                return _reject("gated", None)
            # Not blocked.  When the family WOULD block but the signal was exempted,
            # record it distinctly (with the reason) so the exemption's live volume
            # is measurable via /suppressed, separate from genuinely-allowed families.
            if _setup_family in _SCALP_RANGING_LOW_ADX_BLOCKED_FAMILIES:
                _exempt_reason = (
                    "htf_aligned" if _htf_aligned
                    else "setup" if _setup_class_name in _SCALP_RANGING_LOW_ADX_EXEMPT_SETUPS
                    else None
                )
                if _exempt_reason is not None:
                    self._suppression_counters[
                        f"ranging_low_adx:exempt:{chan_name}:{_setup_class_name}:{_exempt_reason}"
                    ] += 1
            self._suppression_counters[
                f"ranging_low_adx:family_allowed:{chan_name}:{_setup_family}"
            ] += 1

        # RANGING low-ATR loser-setup suppression (surgical, setup-specific).
        # SR_FLIP_RETEST and LIQUIDITY_SWEEP_REVERSAL bleed in dead-range chop
        # (live last-100: −4.36% / −3.77%); they are allowed by the family gate
        # above, so suppress just those two when RANGING *and* ATR percentile is
        # very low.  Ships dark with [SHADOW] telemetry until owner activates
        # RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED (paid-channel routing change).
        if (
            chan_name == "360_SCALP"
            and ctx.is_ranging
            and _setup_class_name in RANGING_LOW_ATR_SUPPRESS_SETUPS
            and ctx.regime_context is not None
        ):
            try:
                _atr_pctile = float(ctx.regime_context.atr_percentile)
            except (TypeError, ValueError):
                _atr_pctile = None
            if self._should_block_ranging_low_atr_loser(
                _setup_class_name, ctx.is_ranging, _atr_pctile
            ):
                if RANGING_LOW_ATR_LOSER_SUPPRESS_ENABLED:
                    self._suppression_counters[
                        f"ranging_low_atr:setup_block:{chan_name}:{_setup_class_name}"
                    ] += 1
                    self.suppression_tracker.record(SuppressionEvent(
                        symbol=symbol,
                        channel=chan_name,
                        reason="ranging_low_atr_loser_block",
                        regime=self._regime_name_from_ctx(ctx, default="RANGING"),
                        would_be_confidence=getattr(sig, "confidence", None),
                    ))
                    log.debug(
                        "Rejected {} {} setup={} (RANGING low ATR%ile {:.0f} <= {:.0f})",
                        symbol,
                        chan_name,
                        _setup_class_name,
                        _atr_pctile,
                        RANGING_LOW_ATR_SUPPRESS_PCTILE,
                    )
                    return _reject("gated", None)
                # Dark: count + log what we WOULD suppress so the volume and
                # would-be PnL impact is measurable before the flag is flipped.
                self._suppression_counters[
                    f"shadow:ranging_low_atr:{chan_name}:{_setup_class_name}"
                ] += 1
                log.info(
                    "[SHADOW] RANGING_LOW_ATR_LOSER_SUPPRESS: symbol={} setup={} "
                    "atr_pctile={:.0f} conf={} — would suppress if enabled",
                    symbol,
                    _setup_class_name,
                    _atr_pctile,
                    getattr(sig, "confidence", None),
                )

        if not setup.channel_compatible or not setup.regime_compatible:
            if (
                not setup.regime_compatible
                and ctx.market_state == MarketState.VOLATILE_UNSUITABLE
                and chan_name in CHANNEL_VOLATILE_FAMILY_GOVERNED
            ):
                self._suppression_counters[f"volatile_unsuitable:family_block:{chan_name}"] += 1
            # 2026-07-18 audit F2: this and the execution reject below were the
            # last two reasonless kills in the funnel — a path 100%-blocked here
            # showed only "Gated == Generated, classification (none)" in the
            # truth report (how MEAN_REVERT's zero-emission hid behind the
            # already-fixed execution gate, #739).  Bounded cardinality: the
            # regime token is one of six MarketState values.
            _ms_token = getattr(ctx.market_state, "value", str(ctx.market_state))
            _compat_token = (
                "channel" if not setup.channel_compatible else f"regime_{_ms_token}"
            )
            self._increment_path_funnel(
                f"gate_reject:setup_compat:{_compat_token}",
                chan_name,
                _setup_class_name,
            )
            log.debug("Rejected {} {} setup: {}", symbol, chan_name, setup.reason)
            return _reject("gated", None)

        execution = self._evaluate_execution(sig, ctx, setup)
        if not execution.passed:
            _exec_token = (
                "trigger_not_confirmed"
                if not execution.trigger_confirmed
                else "overextended"
            )
            self._increment_path_funnel(
                f"gate_reject:execution:{_exec_token}",
                chan_name,
                _setup_class_name,
            )
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
            _mtf_semantic_allowed = False
            if chan_name == "360_SCALP" and _setup_family in _SCALP_MTF_SEMANTIC_FAMILIES:
                self._suppression_counters[f"mtf_semantic_eval:360_SCALP:{_setup_family}"] += 1
                _mtf_semantic_allowed, _mtf_semantic_reason = self._evaluate_family_semantic_mtf(
                    setup_family=_setup_family,
                    signal_direction=sig.direction.value,
                    mtf_data=mtf_data,
                    min_score=_mtf_min_score,
                    tf_weight_overrides=_tf_weight_overrides or None,
                )
                if _mtf_semantic_allowed:
                    self._suppression_counters[f"mtf_semantic_pass:360_SCALP:{_setup_family}"] += 1
                else:
                    self._suppression_counters[f"mtf_semantic_fail:360_SCALP:{_setup_family}"] += 1
                    self._suppression_counters[
                        f"mtf_semantic_fail_setup:360_SCALP:{_setup_class_name}"
                    ] += 1
            if not mtf_allowed and _mtf_semantic_allowed:
                self._suppression_counters[f"mtf_semantic_saved:360_SCALP:{_setup_family}"] += 1
                self._suppression_counters[f"mtf_semantic_saved_setup:360_SCALP:{_setup_class_name}"] += 1
                mtf_allowed = True
                mtf_reason = _mtf_semantic_reason
            if not mtf_allowed:
                log.debug("MTF gate blocked {} {}: {}", symbol, chan_name, mtf_reason)
                self._suppression_counters[f"mtf_gate:{chan_name}"] += 1
                if chan_name == "360_SCALP":
                    self._suppression_counters[f"mtf_gate_family:360_SCALP:{_setup_family}"] += 1
                    self._suppression_counters[f"mtf_gate_setup:360_SCALP:{_setup_class_name}"] += 1
                # OWNER_BRIEF §3.4 + §3.2 #4 doctrine bypass: tape-driven and
                # breakout setups are explicitly assigned "None" HTF treatment
                # by §3.4.  Hard-vetoing them here contradicts doctrine and
                # discards signals the evaluator's own thesis gates and the
                # confidence floor would correctly classify.  The MTF score
                # remains in the confidence calc; we just stop using it as a
                # veto.  Non-exempt setups (counter-trend / structure / trend-
                # aligned) keep the existing hard-block behaviour.
                _doctrine_bypass = (
                    chan_name == "360_SCALP"
                    and _MTF_DOCTRINE_BYPASS_ENABLED
                    and _setup_class_name in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
                )
                if _doctrine_bypass:
                    self._suppression_counters[
                        f"mtf_doctrine_bypass:360_SCALP:{_setup_class_name}"
                    ] += 1
                    self._suppression_counters[
                        f"mtf_doctrine_bypass_family:360_SCALP:{_setup_family}"
                    ] += 1
                    log.debug(
                        "MTF doctrine-bypass {} {} setup={} ({}): "
                        "OWNER_BRIEF §3.4 — no HTF gate for this path",
                        symbol, chan_name, _setup_class_name, mtf_reason,
                    )
                    # Fall through to subsequent gates (VWAP / KZ / OI /
                    # confidence floor / dispatch staleness etc.).  The
                    # doctrine-faithful position is that MTF *score* is a
                    # soft input to confidence (already wired) but never a
                    # hard veto for these setup classes.
                    mtf_allowed = True
                else:
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

        # ── Filter 1b: Longs higher-timeframe regime gate ──────────────────
        # Drop a LONG when the 15m (higher-timeframe) regime is trending DOWN:
        # the trade is fighting the larger tide.  Independent of the MTF
        # confluence gate above (that scores EMA alignment; this reads the
        # unified regime label).  Shorts are intentionally exempt, as are the
        # §3.4 doctrine-bypass setups (breakout / tape-driven) handled below.
        if _MTF_LONGS_REGIME_GATE_ENABLED and sig.direction.value == "LONG":
            _c15 = ctx.candles.get("15m") if ctx.candles else None
            _c15_closes = _c15.get("close", []) if _c15 else []
            if len(_c15_closes) >= 30:
                self._suppression_counters[f"mtf_longs_regime_eval:{chan_name}"] += 1
                _closes15 = np.asarray(_c15_closes, dtype=np.float64)
                _highs15 = np.asarray(_c15.get("high", _c15_closes), dtype=np.float64)
                _lows15 = np.asarray(_c15.get("low", _c15_closes), dtype=np.float64)
                _vols15 = np.asarray(
                    _c15.get("volume", np.zeros(len(_closes15))), dtype=np.float64
                )
                _tier15 = getattr(
                    classify_pair_tier(symbol, volume_24h_usd=volume_24h),
                    "tier", "MIDCAP",
                )
                _regime15 = detect_regime_from_arrays(
                    _closes15, _highs15, _lows15, _vols15,
                    idx=len(_closes15) - 1, pair_tier=_tier15,
                )
                if _regime15 == MarketRegime.TRENDING_DOWN.value:
                    # OWNER_BRIEF §3.4 doctrine bypass: tape-driven and breakout
                    # setups fire "in any HTF context" — a breakout or post-
                    # liquidation reversal long IS the regime change igniting,
                    # not a counter-trend mistake.  Mirror the MTF confluence
                    # gate's exemption so we don't HTF-veto the very setups
                    # doctrine says must not be HTF-gated.
                    _doctrine_exempt = (
                        chan_name == "360_SCALP"
                        and _MTF_DOCTRINE_BYPASS_ENABLED
                        and _setup_class_name in _SCALP_MTF_HARD_BLOCK_EXEMPT_SETUPS
                    )
                    if _doctrine_exempt:
                        self._suppression_counters[
                            f"mtf_longs_regime_doctrine_bypass:360_SCALP:{_setup_class_name}"
                        ] += 1
                        log.debug(
                            "Longs HTF-regime gate doctrine-bypass {} {} setup={}: "
                            "OWNER_BRIEF §3.4 — no HTF veto (15m={})",
                            symbol, chan_name, _setup_class_name, _regime15,
                        )
                        # Fall through: the long is allowed despite a down 15m.
                    elif _MTF_LONGS_REGIME_GATE_DARK:
                        # Measure-only: count what we WOULD block, don't reject.
                        self._suppression_counters[
                            f"mtf_longs_regime_would_block:{chan_name}"
                        ] += 1
                    else:
                        self._suppression_counters[
                            f"mtf_longs_regime_block:{chan_name}"
                        ] += 1
                        self.suppression_tracker.record(SuppressionEvent(
                            symbol=symbol,
                            channel=chan_name,
                            reason="mtf_longs_regime_down",
                            regime=_regime15,
                            would_be_confidence=sig.confidence,
                        ))
                        log.debug(
                            "Longs HTF-regime gate blocked {} {}: 15m={}",
                            symbol, chan_name, _regime15,
                        )
                        return _reject("gated", None)

        # ── Filter 1c: Counter-trend reversal HARD-block on a confirmed mover ──
        # The per-symbol direction gate (Filter 10) only SOFT-penalises and EXEMPTS
        # LSR/FAR, so a reversal fading a parabolic mover got no penalty at all
        # (SYNUSDT: LSR shorted +300%/7d, 4h+1h stacked up → full SL).  Fading a
        # confirmed strong mover is structural impossibility — the one case §3.2 #5
        # reserves a hard block for.  Hard-reject a blocked-set reversal/structure
        # entry that opposes BOTH the pair's 1H and 4H EMA trend on a mover-grade
        # move (wide EMA fan).  Trend-aligned instances and gently-trending pairs
        # are untouched.  Fail-open on any error.  Reversible env off-switch.
        if (
            chan_name == "360_SCALP"
            and COUNTERTREND_MOVER_HARD_BLOCK_ENABLED
            and _setup_class_name in _COUNTERTREND_MOVER_BLOCKED_SETUPS
        ):
            try:
                _ct_allowed, _ct_reason = check_countertrend_mover_block(
                    sig.direction.value,
                    ctx.indicators.get("1h", {}),
                    ctx.indicators.get("4h", {}),
                    ctx.candles.get("4h", {}),
                    setup_class=_setup_class_name,
                    blocked_setups=_COUNTERTREND_MOVER_BLOCKED_SETUPS,
                    min_fan_pct=COUNTERTREND_MOVER_MIN_FAN_PCT,
                )
                if not _ct_allowed:
                    self._suppression_counters[
                        f"countertrend_mover_block:{chan_name}:{_setup_class_name}"
                    ] += 1
                    self.suppression_tracker.record(SuppressionEvent(
                        symbol=symbol,
                        channel=chan_name,
                        reason="countertrend_mover_block",
                        regime=_regime_key,
                        would_be_confidence=getattr(sig, "confidence", None),
                    ))
                    log.debug(
                        "Counter-trend mover hard-block {} {} {} {}: {}",
                        symbol, chan_name, _setup_class_name, sig.direction.value, _ct_reason,
                    )
                    return _reject("gated", None)
            except Exception as _ct_exc:
                log.debug(
                    "Counter-trend mover block error for {} {} (fail open): {}",
                    symbol, chan_name, _ct_exc,
                )

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
                    _base = self._modulate_penalty_base(
                        base=_base,
                        penalty_key="vwap",
                        chan_name=chan_name,
                        setup_family=_setup_family,
                        setup_class=_setup_class_name,
                    )
                    _scaled = round(_base * regime_mult, 1)
                    soft_penalty += _scaled
                    _soft_penalty_by_type["vwap"] = _soft_penalty_by_type.get("vwap", 0.0) + _scaled
                    _fired_gates.append("VWAP")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.1f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, vwap_reason,
                    )
            except Exception as _vwap_exc:
                fail_open.record("scanner.vwap_gate", _vwap_exc)

        # ── Filter 3: Kill Zone / Session Filter ────────────────────────────
        if _gate_profile.get("kill_zone", True):
            # Relaxed minimum multiplier for scalp signals (scalps can trade lower-liquidity windows)
            _kz_min_mult = 0.40 if chan_name == "360_SCALP" else 0.50
            kz_allowed, kz_reason = check_kill_zone_gate(minimum_multiplier=_kz_min_mult)
            if not kz_allowed:
                _base = _penalty_weights.get("kill_zone", 10.0)
                _base = self._modulate_penalty_base(
                    base=_base,
                    penalty_key="kill_zone",
                    chan_name=chan_name,
                    setup_family=_setup_family,
                    setup_class=_setup_class_name,
                )
                _scaled = round(_base * regime_mult, 1)
                soft_penalty += _scaled
                _soft_penalty_by_type["kz"] = _soft_penalty_by_type.get("kz", 0.0) + _scaled
                _fired_gates.append("KZ")
                log.debug(
                    "SOFT_PENALTY {} {} {:+.1f} (base={:.1f} × regime={:.1f}) total={:.1f}: {}",
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
                        _soft_penalty_by_type["oi"] = _soft_penalty_by_type.get("oi", 0.0) + _scaled
                        _fired_gates.append("OI")
                        log.debug(
                            "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                            symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, oi_reason,
                        )
            except Exception as _oi_exc:
                fail_open.record("scanner.oi_gate", _oi_exc)

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
                        # Route through _fired_gates so the join at the end
                        # of the gate chain (sig.soft_gate_flags assignment
                        # below) preserves it.  Pre-fix, this wrote directly
                        # to sig.soft_gate_flags before the join, so the
                        # join silently overwrote the flag.
                        _fired_gates.append(_fr_flag)
                    log.debug(
                        "Funding gate {} {} fr={:.4f} {:+.1f}",
                        symbol, chan_name, _fr, _fr_adj,
                    )
            except Exception as _fr_exc:
                fail_open.record("scanner.funding_gate", _fr_exc)


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
                            # Route through _fired_gates (see Funding gate
                            # comment above) so the join at the end of the
                            # gate chain doesn't silently drop the flag.
                            _fired_gates.append(
                                f"CROSS_ASSET:{ca_conf_adj:+.0f}"
                            )
                        log.debug(
                            "Cross-asset gate {} {} {:+.1f}: {}",
                            symbol, chan_name, ca_conf_adj, ca_reason,
                        )
            except Exception as _ca_exc:
                fail_open.record("scanner.cross_asset_gate", _ca_exc)

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
                    _soft_penalty_by_type["spoof"] = _soft_penalty_by_type.get("spoof", 0.0) + _scaled
                    _fired_gates.append("SPOOF")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, spoof_reason,
                    )
            except Exception as _spoof_exc:
                fail_open.record("scanner.spoof_gate", _spoof_exc)

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
                    _base = self._modulate_penalty_base(
                        base=_base,
                        penalty_key="volume_div",
                        chan_name=chan_name,
                        setup_family=_setup_family,
                        setup_class=_setup_class_name,
                    )
                    _scaled = round(_base * regime_mult, 1)
                    soft_penalty += _scaled
                    _soft_penalty_by_type["vol_div"] = _soft_penalty_by_type.get("vol_div", 0.0) + _scaled
                    _fired_gates.append("VOL_DIV")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.1f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, vol_div_reason,
                    )
            except Exception as _vol_div_exc:
                fail_open.record("scanner.volume_div_gate", _vol_div_exc)

        # ── Filter 8: Signal Clustering Suppression ───────────────────────
        if _gate_profile.get("cluster", True):
            cluster_allowed, cluster_reason = self.cluster_suppressor.check_cluster_gate(
                symbol, sig.direction.value
            )
            if not cluster_allowed:
                _base = _penalty_weights.get("cluster", 8.0)
                _scaled = round(_base * regime_mult, 1)
                soft_penalty += _scaled
                _soft_penalty_by_type["cluster"] = _soft_penalty_by_type.get("cluster", 0.0) + _scaled
                _fired_gates.append("CLUSTER")
                log.debug(
                    "SOFT_PENALTY {} {} {:+.1f} (base={:.0f} × regime={:.1f}) total={:.1f}: {}",
                    symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, cluster_reason,
                )

        # ── Filter 9: BTC direction soft penalty (OWNER_BRIEF §2.1) ──────
        # Production data 2026-05-18: LONG signals hit full SL at 27% vs
        # SHORT at 7% during a TRENDING_DOWN-skewed market — the asymmetry
        # tracks BTC's 1H/4H trend.  Top-75 USDT-M futures are heavily
        # BTC-correlated; signals fighting BTC's macro direction get swept
        # on the next BTC impulse.  Soft penalty (default 6.0 pts) when
        # BOTH BTC 1H AND 4H oppose the signal direction — matches the
        # per-pair HTF mismatch pattern (SR_FLIP / QCB / FAR).  Tape-driven
        # paths (WHALE / FUNDING / LIQ_REVERSAL) are exempt: their thesis
        # IS fading the tape.  Fail-open on missing BTC data.
        if _gate_profile.get("btc_dir", True) and _BTC_DIRECTION_GATE_ENABLED:
            try:
                _btc_cd_1h = self.data_store.get_candles("BTCUSDT", "1h") or {}
                _btc_cd_4h = self.data_store.get_candles("BTCUSDT", "4h") or {}
                _btc_inds_raw = compute_indicators_for_candle_dict(
                    {k: v for k, v in {"1h": _btc_cd_1h, "4h": _btc_cd_4h}.items() if v}
                )
                _btc_ind_1h = _btc_inds_raw.get("1h", {})
                _btc_ind_4h = _btc_inds_raw.get("4h", {})
                btc_dir_allowed, btc_dir_reason = check_btc_direction_gate(
                    sig.direction.value,
                    _btc_ind_1h,
                    _btc_ind_4h,
                    _btc_cd_4h,
                    setup_class=_setup_class_name,
                )
                if not btc_dir_allowed:
                    _base = _penalty_weights.get("btc_dir", _BTC_DIRECTION_PENALTY_BASE)
                    _base = self._modulate_penalty_base(
                        base=_base,
                        penalty_key="btc_dir",
                        chan_name=chan_name,
                        setup_family=_setup_family,
                        setup_class=_setup_class_name,
                    )
                    _scaled = round(_base * regime_mult, 1)
                    # Dark-first restore (2026-07-14): the gate never actually
                    # fired in production (numpy truthiness ate every call in
                    # this except handler), so re-arming it changes live
                    # scoring.  Apply only when the owner flips the tunable;
                    # while OFF, shadow-log every would-fire so a real window
                    # shows exactly which signals it touches.
                    from src import runtime_tunables as _rt
                    if bool(_rt.get("btc_dir_penalty_apply")):
                        soft_penalty += _scaled
                        _soft_penalty_by_type["btc_dir"] = (
                            _soft_penalty_by_type.get("btc_dir", 0.0) + _scaled
                        )
                        _fired_gates.append("BTC_DIR")
                        log.debug(
                            "SOFT_PENALTY {} {} {:+.1f} (base={:.1f} × regime={:.1f}) total={:.1f}: {}",
                            symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, btc_dir_reason,
                        )
                    else:
                        self._suppression_counters[
                            f"btc_dir_shadow:{chan_name}:{_setup_class_name}"
                        ] += 1
                        log.info(
                            "BTC_DIR_SHADOW would-penalise {} {} {:+.1f} (base={:.1f} × regime={:.1f}): {}",
                            symbol, chan_name, _scaled, _base, regime_mult, btc_dir_reason,
                        )
            except Exception as _btc_dir_exc:
                fail_open.record("scanner.btc_direction_gate", _btc_dir_exc)

        # ── Filter 10: Per-symbol 1H/4H direction soft penalty ────────────
        # BTC direction gate (Filter 9) fires only when BTC's OWN EMAs are
        # aligned — which is ~30% of the time.  The remaining 70% (QUIET
        # regime) an altcoin can be in a clear local downtrend while BTC
        # is flat, and the BTC gate passes the signal through.  This filter
        # applies the same soft-penalty logic against the signal symbol's
        # OWN 1H + 4H EMA alignment, catching exactly those cases.
        # LSR and FAR are exempt — their thesis IS to trade against the
        # pair's recent local structure.  Fail-open on missing data.
        if _gate_profile.get("sym_dir", True) and _SYM_DIRECTION_GATE_ENABLED:
            try:
                _sym_ind_1h = ctx.indicators.get("1h", {})
                _sym_ind_4h = ctx.indicators.get("4h", {})
                _sym_cd_4h = ctx.candles.get("4h", {})
                sym_dir_allowed, sym_dir_reason = check_symbol_direction_gate(
                    sig.direction.value,
                    _sym_ind_1h,
                    _sym_ind_4h,
                    _sym_cd_4h,
                    setup_class=_setup_class_name,
                )
                if not sym_dir_allowed:
                    _base = _penalty_weights.get("sym_dir", _SYM_DIRECTION_PENALTY_BASE)
                    _base = self._modulate_penalty_base(
                        base=_base,
                        penalty_key="sym_dir",
                        chan_name=chan_name,
                        setup_family=_setup_family,
                        setup_class=_setup_class_name,
                    )
                    _scaled = round(_base * regime_mult, 1)
                    soft_penalty += _scaled
                    _soft_penalty_by_type["sym_dir"] = (
                        _soft_penalty_by_type.get("sym_dir", 0.0) + _scaled
                    )
                    _fired_gates.append("SYM_DIR")
                    log.debug(
                        "SOFT_PENALTY {} {} {:+.1f} (base={:.1f} × regime={:.1f}) total={:.1f}: {}",
                        symbol, chan_name, _scaled, _base, regime_mult, soft_penalty, sym_dir_reason,
                    )
            except Exception as _sym_dir_exc:
                fail_open.record("scanner.sym_direction_gate", _sym_dir_exc)

        # ── Counter-trend-LONG macro-direction suppression (S39, scalp filter) ──
        # SCALP-FIRST: a thin context filter on genuine counter-trend REVERSAL long
        # scalps (LIQUIDITY_SWEEP_REVERSAL; SR_FLIP-long already off) — NOT a macro
        # trade, and NOT trend-following longs.  MOVER_TREND_PULLBACK is deliberately
        # excluded: it rides the coin's own momentum (trend-aligned by construction),
        # and blocking it on BTC weakness kills working scalps (owner's live feed).
        # SHORTs and every non-reversal setup are untouched; exits stay pure scalp.
        # Suppress these reversal longs only while the big trend is heading DOWN —
        # BTC's macro leg AND/OR the coin's own — and AUTO-RESTORE when it turns up.
        # Hard reject before scoring; env-reversible; fail-open on missing data.
        _ct_sup, _ct_why = self._ct_long_macro_suppressed(
            symbol, _setup_class_name, sig.direction.value,
        )
        if _ct_sup:
            self._suppression_counters[
                f"ct_long_macro_suppress:{chan_name}:{_setup_class_name}"
            ] += 1
            log.info(
                "CT_LONG_MACRO_SUPPRESS {} {} LONG [{}] ({})",
                symbol, chan_name, _setup_class_name, _ct_why,
            )
            return _reject("gated", None)

        # ── Counter-trend-SHORT macro mirror (S40, DARK — default OFF) ──
        # The 2026-07-01..03 clean window put the whole short bleed in
        # reversal shorts fading a weekly-BULL BTC.  One regime state is not
        # a validated gate, so while CT_SHORT_MACRO_GATE_ENABLED is false the
        # shared predicate only [SHADOW]-logs what it WOULD have suppressed;
        # activation is an owner decision on a shadow window spanning more
        # than one regime.  Same fail-open, same auto-restore as the long gate.
        _cts_sup, _cts_why = self._ct_short_macro_would_suppress(
            symbol, _setup_class_name, sig.direction.value,
        )
        if _cts_sup:
            if CT_SHORT_MACRO_GATE_ENABLED:
                self._suppression_counters[
                    f"ct_short_macro_suppress:{chan_name}:{_setup_class_name}"
                ] += 1
                log.info(
                    "CT_SHORT_MACRO_SUPPRESS {} {} SHORT [{}] ({})",
                    symbol, chan_name, _setup_class_name, _cts_why,
                )
                return _reject("gated", None)
            if DARK_FLAG_SHADOW_TELEMETRY:
                log.info(
                    "[SHADOW] CT_SHORT_MACRO_SUPPRESSED {} {} SHORT [{}] ({})",
                    symbol, chan_name, _setup_class_name, _cts_why,
                )

        risk = self._evaluate_risk(sig, ctx, setup, chan_name=chan_name)
        if not risk.passed:
            log.debug("Rejected {} {} risk: {}", symbol, chan_name, risk.reason)
            self._suppression_counters[
                f"geometry_rejected_risk_plan:{chan_name}:{_setup_family}"
            ] += 1
            _reason_token = self._metric_token(risk.reason)
            self._suppression_counters[
                f"geometry_rejected_risk_plan_reason:{chan_name}:{_setup_family}:{_reason_token}"
            ] += 1
            if risk.reason == "protected_structural_sl_cap_exceeded_reject_not_compress":
                _policy_scope = str(getattr(risk, "sl_cap_policy_scope", "channel") or "channel")
                self._suppression_counters[
                    f"geometry_rejected_risk_plan_policy:{chan_name}:{_setup_family}:{_policy_scope}"
                ] += 1
            self._increment_path_funnel("geometry:risk_plan:rejected", chan_name, _setup_class_name)
            self._increment_path_funnel(
                f"geometry:risk_plan:rejected_reason:{_reason_token}",
                chan_name,
                _setup_class_name,
            )
            if risk.reason == "protected_structural_sl_cap_exceeded_reject_not_compress":
                _policy_scope = str(getattr(risk, "sl_cap_policy_scope", "channel") or "channel")
                self._increment_path_funnel(
                    f"geometry:risk_plan:rejected_policy:{_policy_scope}",
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
                    setup=setup.setup_class,
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
        _composite_score_before_penalty: Optional[float] = None
        _confidence_before_soft_penalty: Optional[float] = None
        _feedback_adjustment: float = 0.0
        _stat_filter_delta: float = 0.0
        _pair_analysis_penalty: float = 0.0
        _regime_transition_boost: float = 0.0
        # Decay applied by ``apply_confidence_decay`` later — captured here
        # so the confidence_gate INFO log can surface a ``decay={:+.1f}``
        # term.  Negative-or-zero (decay never boosts).  Initialised early
        # so early-reject log paths (MTF gate, etc.) still have a safe value.
        _decay_delta: float = 0.0
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
        # ML feedback adjustment based on historical outcomes for this
        # channel / setup combination. Disabled by default since 2026-05-23
        # (per FEEDBACK_LOOP_ENABLED env-flag doctrine in config/__init__.py).
        if FEEDBACK_LOOP_ENABLED:
            fb_adj = self.feedback_loop.get_confidence_adjustment(
                setup_score.components, chan_name, setup.setup_class.value
            )
            if fb_adj != 0.0:
                _feedback_adjustment = fb_adj
                sig.confidence += fb_adj
                log.debug(
                    "Feedback adjustment for {} {} {}: {:+.1f} → {:.1f}",
                    symbol, chan_name, setup.setup_class.value, fb_adj, sig.confidence,
                )

        # Narrative-pair bonus — lift candidates on the curated narrative
        # list (FARTCOIN, JTO, FIL, ENA, PLAY by default). Top-5 winners
        # carried +12.19% of net PnL on 43 signals per the 2026-05-23
        # per-signal audit. Set NARRATIVE_PAIR_BONUS=0 to disable.
        if NARRATIVE_PAIR_BONUS != 0.0 and symbol in NARRATIVE_PAIR_LIST:
            sig.confidence += NARRATIVE_PAIR_BONUS
            log.debug(
                "Narrative-pair bonus for {} {}: {:+.1f} → {:.1f}",
                symbol, chan_name, NARRATIVE_PAIR_BONUS, sig.confidence,
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
                fail_open.record("scanner.chart_patterns", _exc)

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
                        np.asarray(_vol_arr) if len(_vol_arr) else None,
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
                fail_open.record("scanner.candlestick_patterns", _exc)

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
            fail_open.record("scanner.mtf_conf_modifier", _mtf_exc)

        # Hard MTF block: signal was vetoed — return immediately.
        if sig is None:
            return _reject("gated", cross_verified)

        # Apply adaptive confidence decay based on signal freshness.
        # apply_confidence_decay clamps the final value to [0, 100].
        # We capture the delta into the outer-scope ``_decay_delta`` so the
        # confidence_gate INFO log can surface a ``decay={:+.1f}`` term —
        # without this the composite→final drop has been invisible in
        # telemetry (the bug surfaced 2026-05-06 in production logs where
        # ~15-point drops appeared with no per-type explanation).
        _confidence_pre_decay = float(sig.confidence)
        sig.confidence = apply_confidence_decay(
            confidence=sig.confidence,
            signal_generated_at=t0_signal,
            current_time=time.monotonic(),
            channel=chan_name,
        )
        sig.confidence = self._clamp_confidence(sig.confidence)
        _decay_delta = float(sig.confidence) - _confidence_pre_decay  # ≤ 0
        sig.post_ai_confidence = sig.confidence

        # ── PR-6: Multi-TF Level Book Confluence Bonus ────────────────────
        # When the entry sits in a band where ≥2 distinct multi-TF S/R levels
        # cluster (level + round number + multi-TF swing all count), give a
        # negative soft_penalty (= bonus).  This is the chartist-confluence
        # signal: humans treat 100K + a 4h swing high + a 1d resistance at the
        # same price as one strong wall.  The bonus magnitude is bounded
        # (max 9 pts) so it can't unilaterally lift a sub-50 candidate to
        # paid tier — it only nudges borderline B-tier candidates over the
        # 65 paid threshold.
        try:
            self._refresh_level_book_if_stale(symbol, ctx.candles)
            _confluence_n = self.level_book.confluence_count(
                symbol, sig.entry, tolerance_pct=_CONFLUENCE_QUERY_TOLERANCE_PCT,
            )
            if _confluence_n >= 2:
                _bonus = _CONFLUENCE_BONUS_BY_COUNT.get(
                    min(_confluence_n, 4), _CONFLUENCE_BONUS_MAX,
                )
                soft_penalty -= _bonus
                _soft_penalty_by_type["confluence"] = (
                    _soft_penalty_by_type.get("confluence", 0.0) - _bonus
                )
                _fired_gates.append(f"CONFLUENCE×{_confluence_n}")
                log.debug(
                    "CONFLUENCE_BONUS {} {} -{:+.1f} (count={}) total_penalty={:.1f}",
                    symbol, chan_name, _bonus, _confluence_n, soft_penalty,
                )
            # Always stash the count on the signal for telemetry / app surface,
            # even if it didn't earn a bonus (count<2).
            sig.confluence_count = _confluence_n
        except Exception as _conf_exc:
            fail_open.record("scanner.levelbook_confluence", _conf_exc)

        # ── PR-Wire: Structure-alignment bonus ───────────────────────────
        # When a trend-following path (TPE / DIV_CONT / CLS / PDC) fires
        # with its entry direction matching the 4h structure leg, award a
        # small bonus.  Counter-trend paths and break-event paths
        # deliberately do not consume this — see _STRUCTURE_ALIGN_PATHS
        # comment for the doctrine reasoning.
        try:
            _setup_class_str = str(getattr(sig, "setup_class", "") or "")
            if _setup_class_str in _STRUCTURE_ALIGN_PATHS:
                _struct_state = self.structure_tracker.get_state(symbol, tf="4h")
                _aligned = self.structure_tracker.is_aligned(
                    symbol, sig.direction.value, tf="4h",
                )
                if _aligned:
                    soft_penalty -= _STRUCTURE_ALIGN_BONUS
                    _soft_penalty_by_type["structure_align"] = (
                        _soft_penalty_by_type.get("structure_align", 0.0)
                        - _STRUCTURE_ALIGN_BONUS
                    )
                    _state_label = (
                        _struct_state.state if _struct_state is not None else "ALIGNED"
                    )
                    _fired_gates.append(f"STRUCT_ALIGN:{_state_label}")
                    log.debug(
                        "STRUCTURE_ALIGN_BONUS {} {} -{:+.1f} ({}) total_penalty={:.1f}",
                        symbol, chan_name, _STRUCTURE_ALIGN_BONUS,
                        _state_label, soft_penalty,
                    )
        except Exception as _sa_exc:
            fail_open.record("scanner.structure_align_bonus", _sa_exc)

        # ── Structure-MISALIGN penalty (DIV_CONT only at first) ────────
        # Symmetric counterpart to the align-bonus block above.  See
        # ``_STRUCTURE_MISALIGN_PENALTY`` constant docstring for the
        # truth-report data + magnitude rationale.  Only paths in
        # ``_STRUCTURE_MISALIGN_PATHS`` participate (currently
        # DIVERGENCE_CONTINUATION only); other paths can enrol once a
        # telemetry window validates behaviour.
        #
        # No penalty when:
        #   - structure not yet detected (warmup / new pair)
        #   - state is RANGE (no directional structure to oppose)
        #   - confidence below LEG_DOMINANCE_THRESHOLD (weak read)
        #   - direction matches structure (already got the bonus)
        try:
            if _setup_class_str in _STRUCTURE_MISALIGN_PATHS:
                _struct_state_mis = self.structure_tracker.get_state(
                    symbol, tf="4h",
                )
                if (
                    _struct_state_mis is not None
                    and _struct_state_mis.state in ("BULL_LEG", "BEAR_LEG")
                    and _struct_state_mis.confidence >= LEG_DOMINANCE_THRESHOLD
                ):
                    _dir_upper = sig.direction.value.upper()
                    _opposes = (
                        (_struct_state_mis.state == "BEAR_LEG"
                         and _dir_upper == "LONG")
                        or (_struct_state_mis.state == "BULL_LEG"
                            and _dir_upper == "SHORT")
                    )
                    if _opposes:
                        soft_penalty += _STRUCTURE_MISALIGN_PENALTY
                        # Reuse the existing structure_align telemetry
                        # bucket — the truth report already surfaces it
                        # per-path so the penalty + bonus delta net out
                        # naturally in the soft-penalty-per-type table.
                        _soft_penalty_by_type["structure_align"] = (
                            _soft_penalty_by_type.get(
                                "structure_align", 0.0,
                            )
                            + _STRUCTURE_MISALIGN_PENALTY
                        )
                        _fired_gates.append(
                            f"STRUCT_MISALIGN:{_struct_state_mis.state}"
                        )
                        log.debug(
                            "STRUCTURE_MISALIGN_PENALTY {} {} +{:.1f} "
                            "({} conf={:.2f}) total_penalty={:.1f}",
                            symbol, chan_name, _STRUCTURE_MISALIGN_PENALTY,
                            _struct_state_mis.state,
                            _struct_state_mis.confidence,
                            soft_penalty,
                        )
        except Exception as _sm_exc:
            fail_open.record("scanner.structure_misalign_penalty", _sm_exc)

        # ── Per-pair rolling-window soft penalty ─────────────────────────
        # Doctrine-aligned replacement for the closed-without-merge hard
        # blacklist (PR #424).  Pairs that have been net-negative over
        # the trailing 28-day window get a confidence deduction
        # proportional to mean raw PnL × scale, capped at 20 pts.
        # Pair recovers → penalty decays naturally on the next refresh.
        # See ``src/pair_penalty.py`` for calibration + env-overrides.
        try:
            _pair_pen = _pair_penalty.get(symbol)
            if _pair_pen > 0.0:
                soft_penalty += _pair_pen
                _soft_penalty_by_type["pair_perf"] = (
                    _soft_penalty_by_type.get("pair_perf", 0.0) + _pair_pen
                )
                _fired_gates.append("PAIR_PERF")
                log.debug(
                    "SOFT_PENALTY {} {} {:+.1f} pair_perf total={:.1f}",
                    symbol, chan_name, _pair_pen, soft_penalty,
                )
        except Exception as _pp_exc:
            # Fail-open: a bug in the penalty lookup must never block
            # signal scoring.  Worst case we miss the deduction for one
            # signal; the next scan tick catches it.
            fail_open.record("scanner.pair_penalty_lookup", _pp_exc)
            log.debug(
                "pair_penalty lookup error for {} {} (fail open): {}",
                symbol, chan_name, _pp_exc,
            )

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
        _pre_penalty_tier_for_migration = classify_signal_tier(sig.confidence)
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
            if len(_closes_arr) and len(_vol_arr):
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
                except Exception as _of_exc:
                    fail_open.record("scanner.orderflow_thesis_inputs", _of_exc)
            _scoring_inp = ScoringInput(
                sweeps=ctx.smc_result.sweeps,
                mss=ctx.smc_result.mss,
                fvg_zones=ctx.smc_result.fvg,
                regime=_regime_key,
                setup_class=sig.setup_class,
                htf_trend_aligned=getattr(sig, "htf_trend_aligned", False),
                atr_percentile=_atr_pct,
                volume_last_usd=_volume_last_usd,
                volume_avg_usd=_volume_avg_usd,
                breakout_volume_ratio=getattr(sig, "breakout_volume_ratio", 0.0) or 0.0,
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
            _composite_score_before_penalty = _score_result["total"]
            _pre_penalty_tier_for_migration = classify_signal_tier(sig.confidence)
            self._record_scoring_distribution(
                phase="pre_penalty",
                chan_name=chan_name,
                setup_family=_sf,
                setup_class=_sc,
                score=sig.confidence,
                tier=_pre_penalty_tier_for_migration,
            )
            if _score_result["total"] >= 80:
                sig.signal_tier = "A+"
                self._suppression_counters[f"score_80plus:{_sc}"] += 1
                self._scoring_tier_counters[f"score_80plus:{_sc}"] += 1
            elif _score_result["total"] >= 65:
                sig.signal_tier = "B"
                self._suppression_counters[f"score_65to79:{_sc}"] += 1
                self._scoring_tier_counters[f"score_65to79:{_sc}"] += 1
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
                self._record_target_path_tier_migration(
                    setup_family=_sf,
                    setup_class=_sc,
                    pre_tier=_pre_penalty_tier_for_migration,
                    post_tier=_below_tier,
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
            fail_open.record("scanner.composite_scoring", _score_exc)

        # PR-15: Apply the full accumulated soft-penalty (evaluator-authored + scanner-gate)
        # after composite score assignment so that the penalties are not overwritten by the
        # scoring engine.  sig.soft_penalty_total holds evaluator-level quality penalties
        # plus scanner-gate penalties; previously only the scanner portion (soft_penalty)
        # was deducted, leaving evaluator-authored penalties un-applied and allowing signals
        # with inflated pre-penalty confidence to pass downstream floor and tier gates.
        _total_soft_penalty = sig.soft_penalty_total  # evaluator-authored + scanner-gate combined
        _confidence_before_soft_penalty = sig.confidence
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
        self._record_target_path_tier_migration(
            setup_family=_sf,
            setup_class=_sc,
            pre_tier=_pre_penalty_tier_for_migration,
            post_tier=sig.signal_tier,
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
            _stat_filter_delta = _sf_conf - sig.confidence
            sig.confidence = _sf_conf
            if "penalty" in _sf_reason:
                _existing_flags = sig.soft_gate_flags or ""
                sig.soft_gate_flags = (_existing_flags + f",{_sf_reason}").lstrip(",")
        except Exception as _sf_exc:
            log.debug("stat_filter error for {} {} (fail open): {}", symbol, chan_name, _sf_exc)

        # ── COHORT_EDGE gate — STEP 2 ACTIVE (owner-approved 2026-07-07) ──
        # Compute the cohort key (setup × side × regime_family × BTC-macro-dir),
        # stamp it for perf attribution, then SUPPRESS when the cohort's
        # measured live expectancy is negative with enough samples.  This is
        # the fix for the score-band inversion (75+ confidence band ran
        # −0.107%/trade vs +0.088% for 65–70 in the 7d study): the composite
        # score measures pattern conformity; this gate measures whether the
        # cohort has actually been making money.  Fail-open on no history and
        # on any error.  Thresholds are ops-panel runtime tunables.
        try:
            from src import runtime_tunables as _rt
            _btc_macro = self._get_btc_macro_dir_cached()
            _macro_dir_str = str(_btc_macro.get("regime", "NEUTRAL"))
            _c_key_tuple = _cohort_edge_store.cohort_key(
                sig.setup_class, sig.direction.value, _regime_key, _macro_dir_str,
            )
            sig.cohort_edge_key = "/".join(_c_key_tuple)
            _c_samples = _cohort_edge_store.sample_count(
                sig.setup_class, sig.direction.value, _regime_key, _macro_dir_str,
            )
            sig.cohort_edge_samples = _c_samples
            _c_exp = _cohort_edge_store.expectancy(
                sig.setup_class, sig.direction.value, _regime_key, _macro_dir_str,
            )
            if _c_exp is not None:
                sig.cohort_edge_expectancy = _c_exp
            if (
                _rt.get("cohort_edge_gate_enabled")
                and _c_exp is not None
                and _c_samples >= int(_rt.get("cohort_edge_gate_min_n"))
                and _c_exp <= float(_rt.get("cohort_edge_suppress_below"))
            ):
                log.info(
                    "COHORT_EDGE suppressed {}/{}: edge={:.3f}%/trade n={} "
                    "key={} (measured negative expectancy)",
                    symbol, chan_name, _c_exp, _c_samples, sig.cohort_edge_key,
                )
                self.suppression_tracker.record(SuppressionEvent(
                    symbol=symbol,
                    channel=chan_name,
                    reason=REASON_COHORT_EDGE,
                    regime=_regime_key,
                    would_be_confidence=sig.confidence,
                ))
                return _reject("filtered", cross_verified)
        except Exception as _ce_exc:
            log.debug("cohort_edge gate error for {} {} (fail open): {}", symbol, chan_name, _ce_exc)

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
                    _pair_analysis_penalty = _pa_penalty
                    sig.confidence = max(0.0, sig.confidence - _pa_penalty)
                    _existing_flags = sig.soft_gate_flags or ""
                    sig.soft_gate_flags = (
                        _existing_flags + ",pair_analysis:weak_penalty"
                    ).lstrip(",")
                    self._suppression_counters[f"pair_analysis:weak_penalty:{chan_name}"] += 1
                    log.debug(
                        "pair_analysis weak penalty {}/{}: -{}pts → {:.1f}",
                        symbol, chan_name, _pa_penalty, sig.confidence,
                    )
        except Exception as _pa_exc:
            log.debug("pair_analysis gate error for {} {} (fail open): {}", symbol, chan_name, _pa_exc)

        # DISTRIBUTION soft gate: LONG signals in distribution volume profile carry
        # higher failure risk (market is offloading into retail buyers).
        try:
            _rc_dist = ctx.regime_context if ctx is not None else None
            if (_rc_dist is not None
                    and getattr(_rc_dist, "volume_profile", None) == "DISTRIBUTION"
                    and hasattr(sig, "direction")
                    and sig.direction.value == "LONG"):
                _dist_penalty = 15.0
                sig.confidence = max(0.0, sig.confidence - _dist_penalty)
                _existing_flags = sig.soft_gate_flags or ""
                sig.soft_gate_flags = (_existing_flags + ",distribution_long_penalty").lstrip(",")
                self._suppression_counters[f"distribution_long_penalty:{chan_name}"] += 1
                log.debug(
                    "distribution soft gate {} {}: LONG in DISTRIBUTION -{}pts → {:.1f}",
                    symbol, chan_name, _dist_penalty, sig.confidence,
                )
        except Exception as _dist_exc:
            log.debug("distribution gate error for {} {} (fail open): {}", symbol, chan_name, _dist_exc)

        # Meme coin low-volume penalty: thin meme coins (<$150M 24h vol) behave
        # erratically — SMC patterns are noise-driven, not institutional.
        _MEME_SYMBOLS = frozenset({"PEPEUSDT", "SHIBUSDT", "BONKUSDT", "FLOKIUSDT"})
        try:
            if symbol in _MEME_SYMBOLS and volume_24h < 150_000_000.0:
                _meme_penalty = sig.confidence * (1.0 - 0.85)
                sig.confidence = max(0.0, sig.confidence * 0.85)
                _existing_flags = sig.soft_gate_flags or ""
                sig.soft_gate_flags = (_existing_flags + ",meme_low_vol_penalty").lstrip(",")
                self._suppression_counters[f"meme_low_vol_penalty:{chan_name}"] += 1
                log.debug(
                    "meme low-vol gate {} {}: vol={:.0f} -{}% → {:.1f}",
                    symbol, chan_name, volume_24h, 15, sig.confidence,
                )
        except Exception as _meme_exc:
            log.debug("meme gate error for {} {} (fail open): {}", symbol, chan_name, _meme_exc)

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

        def _record_confidence_gate_decision(
            *,
            decision: str,
            reason: str,
            threshold: float,
        ) -> None:
            """Emit confidence-gate telemetry counters and structured decision logs."""
            self._suppression_counters[
                f"confidence_gate:{decision}:{chan_name}:{_setup_family}:{reason}"
            ] += 1
            _raw_conf_src = getattr(sig, "pre_ai_confidence", None)
            _raw_conf = float(_raw_conf_src) if _raw_conf_src is not None else float("nan")
            _composite_conf = (
                float(_composite_score_before_penalty)
                if _composite_score_before_penalty is not None
                else float(sig.confidence)
            )
            _pre_soft_conf = (
                float(_confidence_before_soft_penalty)
                if _confidence_before_soft_penalty is not None
                else float(sig.confidence)
            )
            log.info(
                "confidence_gate {} {} [{}]: decision={} reason={} raw={:.1f} "
                "composite={:.1f} pre_soft={:.1f} final={:.1f} threshold={:.1f} "
                "penalties(eval={:.1f},gate={:.1f},total={:.1f},pair_analysis={:.1f}) "
                "adjustments(feedback={:+.1f},stat_filter={:+.1f},regime_transition={:+.1f},"
                "decay={:+.1f}) "
                "components(market={:.1f},execution={:.1f},risk={:.1f},thesis_adj={:.1f}) "
                "engine(smc={:.1f},regime={:.1f},volume={:.1f},indicators={:.1f},"
                "patterns={:.1f},mtf={:.1f}) "
                "soft_penalties(vwap={:.1f},kz={:.1f},oi={:.1f},spoof={:.1f},vol_div={:.1f},cluster={:.1f},"
                "confluence={:+.1f},struct_align={:+.1f},btc_dir={:.1f},sym_dir={:.1f}) "
                "flags=[{}]",
                symbol,
                chan_name,
                _setup_class_name,
                decision,
                reason,
                _raw_conf,
                _composite_conf,
                _pre_soft_conf,
                sig.confidence,
                threshold,
                _evaluator_penalty,
                soft_penalty,
                _total_soft_penalty,
                _pair_analysis_penalty,
                _feedback_adjustment,
                _stat_filter_delta,
                _regime_transition_boost,
                _decay_delta,
                float(sig.component_scores.get("market", 0.0)),
                float(sig.component_scores.get("execution", 0.0)),
                float(sig.component_scores.get("risk", 0.0)),
                float(sig.component_scores.get("thesis_adj", 0.0)),
                float(sig.component_scores.get("smc", 0.0)),
                float(sig.component_scores.get("regime", 0.0)),
                float(sig.component_scores.get("volume", 0.0)),
                float(sig.component_scores.get("indicators", 0.0)),
                float(sig.component_scores.get("patterns", 0.0)),
                float(sig.component_scores.get("mtf", 0.0)),
                float(_soft_penalty_by_type.get("vwap", 0.0)),
                float(_soft_penalty_by_type.get("kz", 0.0)),
                float(_soft_penalty_by_type.get("oi", 0.0)),
                float(_soft_penalty_by_type.get("spoof", 0.0)),
                float(_soft_penalty_by_type.get("vol_div", 0.0)),
                float(_soft_penalty_by_type.get("cluster", 0.0)),
                # PR-Diag: surface chartist-eye contributions (negative = bonus).
                float(_soft_penalty_by_type.get("confluence", 0.0)),
                float(_soft_penalty_by_type.get("structure_align", 0.0)),
                # OWNER_BRIEF §2.1 — BTC-direction soft penalty, captured
                # by truth-report parser as ``sp_btc_dir`` to surface in the
                # per-setup soft-penalty table.
                float(_soft_penalty_by_type.get("btc_dir", 0.0)),
                # Per-symbol 1H/4H direction soft penalty (Filter 10).
                float(_soft_penalty_by_type.get("sym_dir", 0.0)),
                # Full flag string so any new gate name appears in INFO logs
                # without needing a code change to the format string.
                getattr(sig, "soft_gate_flags", "") or "",
            )

        # Regime transition boost (item 15): if regime just changed in the direction
        # of this signal, apply a confidence boost (high-probability entry window).
        try:
            _trans_boost = self.regime_detector.get_transition_boost(
                sig.direction.value, symbol=symbol
            )
            if _trans_boost > 0.0:
                _regime_transition_boost = _trans_boost
                sig.confidence = min(100.0, sig.confidence + _trans_boost)
                sig.soft_gate_flags = (
                    sig.soft_gate_flags + f",REGIME_TRANSITION:+{_trans_boost:.0f}"
                ).lstrip(",")
                log.debug(
                    "Regime transition boost {} {}: +{:.1f} → {:.1f}",
                    symbol, chan_name, _trans_boost, sig.confidence,
                )
        except Exception as _trans_exc:
            fail_open.record("scanner.regime_transition_boost", _trans_exc)

        # Populate regime/context display fields BEFORE the remaining gates so
        # (a) the market-context stamp below reads the real entry regime — it
        # previously ran with these fields still empty, so the Wyckoff phase
        # always classified AMBIGUOUS — and (b) suppressed candidates carry
        # their regime into the shadow ledger.  Pure stamping, no gating.
        self._populate_signal_context(sig, volume_24h, ctx)

        # ── Market-Context vector (Layer A) — observe-only stamp ─────────────
        # Compute + stamp the "what regime is it now" vector on every signal.
        # All inputs are already warm here (entry_regime, ATR percentile,
        # cached BTC-State, funding_rate), so this adds no new reads (Cost
        # Discipline).  Placed ABOVE the QUIET gate so every post-scoring
        # suppression records the candidate's context into the shadow ledger.
        # Off the money path: nothing consumes these fields to change live
        # output — they feed the ops edge matrix + the allocator.
        try:
            from src import runtime_tunables as _rt
            if bool(_rt.get("market_context_enabled")):
                _mc_btc_b: Optional[float] = None
                if BTC_STATE_ENABLED:
                    _mc_b_raw: Any = self._get_btc_state_cached().get("b", 0.0)
                    _mc_btc_b = float(_mc_b_raw or 0.0)
                _mc = build_market_context(
                    regime_label=getattr(sig, "entry_regime", "") or None,
                    htf_trend_prior=getattr(sig, "entry_regime_15m", "") or None,
                    atr_percentile=getattr(sig, "atr_percentile_at_entry", None),
                    funding_rate=_funding_rate,
                    btc_state=_mc_btc_b,
                )
                for _k, _v in _mc.as_signal_fields().items():
                    setattr(sig, _k, _v)
        except Exception as _mc_exc:
            log.debug(
                "Market-context stamp error for {} {} (fail open): {}",
                symbol, chan_name, _mc_exc,
            )

        # ── RANGE_FADE context-edge gate (2026-07-18, the path's activation
        # contract) ──────────────────────────────────────────────────────────
        # The shadow ledger measured SHADOW_RANGE_FADE blanket activation
        # net-negative (+0.20R saved per suppressed candidate, n=223) while
        # specific context cells are STRONG (+0.841R ASIA/QUIET/NORMAL,
        # +0.885R OVERLAP/RANGE/NORMAL, …).  So RANGE_FADE emits ONLY when the
        # current context cell for its shadow control arm carries a measured
        # POSITIVE/STRONG Wilson-bound verdict — the allocator's own
        # eligibility rule, consumed live for the first time.  Cold matrix /
        # thin cell / NEGATIVE cell / store error → suppress (fail-CLOSED: an
        # unverifiable edge is not an edge; the shadow arm keeps measuring the
        # cell either way, so a cell that turns STRONG self-unlocks).  Cost:
        # in-memory dict lookup, no I/O (Cost Discipline).  Every rejection is
        # tagged (funnel + suppression tracker + shadow ledger stamp), so this
        # gate's own save/miss balance lands in the gate audit as
        # ``context_edge:RANGE_FADE``.
        if (
            RANGE_FADE_CONTEXT_GATE_ENABLED
            and str(getattr(sig, "setup_class", "") or "") == "RANGE_FADE"
        ):
            _rf_allowed = False
            _rf_verdict = "UNKNOWN"
            _rf_ctx_key = str(getattr(sig, "mc_context_key", "") or "")
            try:
                from src.strategy_edge import (
                    get_strategy_edge_store as _get_edge_store,
                )
                from src.strategy_portfolio import SHADOW_RANGE_FADE as _RF_SHADOW
                if _rf_ctx_key:
                    _rf_verdict = _get_edge_store().verdict(_RF_SHADOW, _rf_ctx_key)
                    _rf_allowed = _range_fade_context_allowed(_rf_verdict)
            except Exception as _rf_exc:
                # Fail-closed by leaving _rf_allowed False — but never
                # silently: a broken edge store must page, not just suppress.
                fail_open.record("scanner.range_fade_context_gate", _rf_exc)
            if not _rf_allowed:
                self._range_fade_context_blocked_total += 1
                self._suppression_counters[
                    f"context_edge:RANGE_FADE:{_rf_verdict}"
                ] += 1
                log.info(
                    "CONTEXT_EDGE suppressed {} RANGE_FADE: context={} "
                    "verdict={} (needs {}+)",
                    symbol, _rf_ctx_key or "(unknown)", _rf_verdict,
                    RANGE_FADE_CONTEXT_MIN_VERDICT.upper(),
                )
                self.suppression_tracker.record(SuppressionEvent(
                    symbol=symbol,
                    channel=chan_name,
                    reason=REASON_COHORT_EDGE,
                    regime=_regime_key,
                    would_be_confidence=sig.confidence,
                ))
                self._increment_path_funnel(
                    "gate_reject:context_edge", chan_name, "RANGE_FADE"
                )
                self._stamp_suppressed(sig, "context_edge:RANGE_FADE")
                return _reject("filtered", cross_verified)

        # QUIET regime safety net for scalp channels: signals must clear the
        # global 65.0 confidence floor (the paid B-tier minimum) when market
        # is compressed.  Per OWNER_BRIEF §2.1a "only the final paid signal
        # matters, watchlist is scrap" — applies uniformly across all setups
        # including QCB, DIV_CONT, FUNDING.  Previous per-setup exempts (QCB
        # fully, DIV_CONT ≥64, FUNDING ≥60) were shipped 2026-05-02 to fix
        # apparent "bottlenecks" but were lowering the bar to enable scrap
        # routing — sub-65 signals reaching watchlist tier and free channel
        # generated zero business value.  Removed 2026-05-04 in PR #270.
        if _regime_key == "QUIET" and chan_name.startswith("360_SCALP"):
            if sig.confidence < QUIET_SCALP_MIN_CONFIDENCE:
                _record_confidence_gate_decision(
                    decision="filtered",
                    reason="quiet_scalp_min_confidence",
                    threshold=QUIET_SCALP_MIN_CONFIDENCE,
                )
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
                self._stamp_suppressed(sig, "quiet_scalp_block")
                return _reject("filtered", cross_verified)
        # ── Graded BTC-State soft-confirmation (src/btc_state.py) ──────────
        # Counter-trend-long fix (ACTIVE_CONTEXT S38): alts couple to BTC harder
        # on the downside, so a LONG fighting a BTC downtrend on a BTC-led pair
        # bleeds.  Stamp the BTC-State b, the per-pair downside coupling w_pair,
        # and the would-be confidence multiplier on EVERY signal.  Recomputed each
        # scan ⇒ auto-restores longs the moment BTC turns up.
        #
        # DARK-FIRST (CLAUDE.md § Project Phase): the haircut is APPLIED only when
        # BTC_STATE_HAIRCUT_ENABLED (default OFF) — otherwise this is stamp +
        # shadow-log only and changes no live output.  Placed as the LAST
        # confidence adjustment so the floor gate below re-evaluates after it:
        # activation is a pure flag flip, no further code change (no scaffold).
        if BTC_STATE_ENABLED:
            try:
                _bstate = self._get_btc_state_cached()
                _b = float(_bstate.get("b", 0.0))
                _pair_cd = self._resolve_candles(ctx.candles, BTC_STATE_COUPLING_TF)
                _pair_closes = _pair_cd.get("close", []) if _pair_cd else []
                _btc_cpl_cd = self.data_store.get_candles("BTCUSDT", BTC_STATE_COUPLING_TF) or {}
                _cpl = compute_downside_coupling(
                    _pair_closes,
                    _btc_cpl_cd.get("close", []),
                    lookback=BTC_STATE_COUPLING_LOOKBACK,
                )
                _w_pair = float(_cpl.get("w_pair", 0.0))
                _hc = compute_haircut_factor(
                    _b, _w_pair, sig.direction.value,
                    str(getattr(sig, "setup_class", "") or ""),
                    k=BTC_STATE_K, floor=BTC_STATE_FLOOR,
                    ct_long_mult=BTC_STATE_CT_LONG_MULT,
                    ct_short_mult=BTC_STATE_CT_SHORT_MULT,
                    severe_setup_weight=BTC_STATE_SEVERE_SETUP_WEIGHT,
                    mild_setup_weight=BTC_STATE_MILD_SETUP_WEIGHT,
                )
                _factor = float(_hc.get("factor", 1.0))
                sig.btc_state = _b
                sig.btc_downside_coupling = _w_pair
                sig.btc_state_factor = _factor
                if _hc.get("applied") and _factor < 1.0:
                    _would_be = sig.confidence * _factor
                    if BTC_STATE_HAIRCUT_ENABLED:
                        _before = sig.confidence
                        sig.confidence = self._clamp_confidence(_would_be)
                        sig.soft_gate_flags = (
                            (sig.soft_gate_flags or "") + ",btc_state_haircut"
                        ).lstrip(",")
                        log.debug(
                            "BTC_STATE haircut {} {} {}: conf {:.1f}→{:.1f} "
                            "(×{:.2f} b={:+.2f} w={:.2f})",
                            symbol, chan_name, sig.direction.value,
                            _before, sig.confidence, _factor, _b, _w_pair,
                        )
                    elif DARK_FLAG_SHADOW_TELEMETRY:
                        log.info(
                            "[BTC_STATE_SHADOW] {} {} {} [{}]: would ×{:.2f} → "
                            "conf {:.1f}→{:.1f} (b={:+.2f} w={:.2f} {})",
                            symbol, chan_name, sig.direction.value,
                            getattr(sig, "setup_class", ""), _factor,
                            sig.confidence, _would_be, _b, _w_pair,
                            _hc.get("reason", ""),
                        )
            except Exception as _bs_exc:
                log.debug(
                    "BTC-State stamp error for {} {} (fail open): {}",
                    symbol, chan_name, _bs_exc,
                )

        # Reclassify after all post-score confidence adjustments (stat filter, pair-analysis
        # penalties, transition boost) so paid-tier decisions use current confidence.
        sig.signal_tier = classify_signal_tier(sig.confidence)
        # WATCHLIST tier removed (app-era doctrine reset).  Sub-65 confidence
        # signals drop cleanly — no free-channel preview, no router routing,
        # no monitor management.  Lumin app's per-agent + signals views show
        # only paid-tier (≥65) outcomes; the free Telegram channel keeps macro
        # / regime-shift / signal-close storytelling but no preview signals.
        _market_component_floor = 12.0
        _execution_component_floor = 10.0
        _risk_component_floor = 10.0
        # ── Context-adaptive emission floor (Layer C → emission consumer) ──
        # The measured Strategy×Context edge matrix sets a per-(strategy,
        # context) confidence floor: RELAX toward the quality anchor in cells
        # measured STRONG/POSITIVE (so a path emits its best setups where it is
        # measured to win), HARD-SUPPRESS NEGATIVE cells (stay silent where it
        # loses), leave the global floor untouched on cold/thin/FLAT cells.  The
        # two-sided generalisation of the S67 RANGE_FADE gate to every strategy.
        # LIVE by owner directive (2026-07-19) with full ops control — the
        # context_emission_* runtime tunables enable/disable, toggle apply-vs-
        # measure-only, and shape anchor/relax/samples with no redeploy.  Fail
        # open to the global floor on any edge-store error (recorded, never
        # silent).  O(1) in-memory lookup against the already-warm edge store —
        # no hot-path Firestore/network read (Cost Discipline).
        _emission_floor = float(min_conf)
        _components_ok = (
            sig.component_scores.get("market", 0.0) >= _market_component_floor
            and sig.component_scores.get("execution", 0.0) >= _execution_component_floor
            and sig.component_scores.get("risk", 0.0) >= _risk_component_floor
        )
        _cep_ctx_key = str(getattr(sig, "mc_context_key", "") or "")
        _cep_setup = str(getattr(sig, "setup_class", "") or "")
        _cep_params = None
        try:
            from src import context_emission_policy as _cep
            _cep_params = _cep.PolicyParams.from_config()
        except Exception as _cep_pexc:
            fail_open.record("scanner.context_emission_params", _cep_pexc)
        if _cep_params is not None and _cep_params.enabled and _cep_ctx_key and _cep_setup:
            _cep_decision = None
            try:
                _cep_decision = _cep.effective_floor(
                    _cep_setup, _cep_ctx_key, float(min_conf),
                    cohort=str(getattr(sig, "mc_pair_cohort", "") or ""),
                    params=_cep_params,
                )
            except Exception as _cep_exc:
                # Unverifiable edge → fall back to the global floor, and page.
                fail_open.record("scanner.context_emission_policy", _cep_exc)
            if _cep_decision is not None:
                self._context_floor_evaluated_total += 1
                _cep_div = _cep.classify_divergence(
                    float(sig.confidence), float(min_conf), _cep_decision,
                    components_ok=_components_ok,
                )
                self._suppression_counters[
                    f"context_floor:{_cep_decision.verdict}:{_cep_div}"
                ] += 1
                if _cep_div == _cep.DIV_RELAX:
                    self._context_floor_would_emit_total += 1
                elif _cep_div == _cep.DIV_TIGHTEN:
                    self._context_floor_would_suppress_total += 1
                if _cep_div in (_cep.DIV_RELAX, _cep.DIV_TIGHTEN):
                    log.info(
                        "[CONTEXT_FLOOR_SHADOW] {} {} {} ctx={} verdict={} "
                        "floor {:.1f}->{:.1f} conf={:.1f} div={} live={} ({})",
                        symbol, chan_name, _cep_setup, _cep_ctx_key,
                        _cep_decision.verdict, float(min_conf),
                        _cep_decision.effective_floor, float(sig.confidence),
                        _cep_div, _cep_params.live, _cep_decision.reason,
                    )
                # LIVE application — instant off via the context_emission_live /
                # context_emission_enabled ops tunables.
                if _cep_params.live:
                    if _cep_decision.suppressed:
                        self._context_floor_applied_total += 1
                        self._suppression_counters[
                            f"context_floor_suppress:{_cep_setup}"
                        ] += 1
                        log.info(
                            "CONTEXT_FLOOR suppressed {} {} {}: NEGATIVE cell {} ({})",
                            symbol, chan_name, _cep_setup, _cep_ctx_key,
                            _cep_decision.reason,
                        )
                        self.suppression_tracker.record(SuppressionEvent(
                            symbol=symbol,
                            channel=chan_name,
                            reason=REASON_COHORT_EDGE,
                            regime=_regime_key,
                            would_be_confidence=sig.confidence,
                        ))
                        self._increment_path_funnel(
                            "gate_reject:context_floor", chan_name, _cep_setup
                        )
                        self._stamp_suppressed(sig, f"context_floor:{_cep_setup}")
                        return _reject("filtered", cross_verified)
                    if _cep_decision.effective_floor < _emission_floor:
                        self._context_floor_applied_total += 1
                        _emission_floor = float(_cep_decision.effective_floor)
        if (
            sig.confidence < _emission_floor
            or sig.component_scores.get("market", 0.0) < _market_component_floor
            or sig.component_scores.get("execution", 0.0) < _execution_component_floor
            or sig.component_scores.get("risk", 0.0) < _risk_component_floor
        ):
            _reason = "min_confidence"
            _threshold = float(_emission_floor)
            if sig.component_scores.get("market", 0.0) < _market_component_floor:
                _reason = "market_component_floor"
                _threshold = _market_component_floor
            elif sig.component_scores.get("execution", 0.0) < _execution_component_floor:
                _reason = "execution_component_floor"
                _threshold = _execution_component_floor
            elif sig.component_scores.get("risk", 0.0) < _risk_component_floor:
                _reason = "risk_component_floor"
                _threshold = _risk_component_floor
            _record_confidence_gate_decision(
                decision="filtered",
                reason=_reason,
                threshold=_threshold,
            )
            self.suppression_tracker.record(SuppressionEvent(
                symbol=symbol,
                channel=chan_name,
                reason=REASON_CONFIDENCE,
                regime=_regime_key,
                would_be_confidence=sig.confidence,
            ))
            self._stamp_suppressed(sig, _reason)
            return _reject("filtered", cross_verified)
        # Reset failed-detection counter — this symbol+channel produced a valid signal
        self._conf_fail_tracker.pop((symbol, chan_name), None)
        _record_confidence_gate_decision(
            decision="kept",
            reason="min_confidence_pass",
            threshold=float(min_conf),
        )
        # (_populate_signal_context now runs before the QUIET gate above.)
        self._apply_noise_floor_stop(sig, ctx)
        return sig, cross_verified

    # ------------------------------------------------------------------
    # Noise-floor stops (owner-approved ACTIVE, 2026-07-07)
    # ------------------------------------------------------------------
    # 7d study vs real 1m klines: 52% of SL hits crossed back through entry
    # within 1h (75% within 3h) with a 1.80% average post-SL favourable move
    # against a 1.00% median stop — stops sat inside the pairs' hourly noise.
    # Fix: the shipped stop must clear ≥ noise_floor_atr_mult × ATR(1h)% of
    # entry.  Widen-only (never tightens evaluator geometry), capped at
    # noise_floor_max_sl_pct, TPs untouched.  Dispatch scales the auto-trade
    # notional down by the widen factor so per-trade capital risk is constant
    # (see signal_dispatch._compute_qty_split callers).  Runtime-tunable from
    # the ops panel — no env changes needed.

    @staticmethod
    def _atr_pct_from_candles(cd: Optional[dict], entry: float, period: int = 14) -> float:
        """Simple ATR over the last ``period`` closed candles, as % of entry.
        Returns 0.0 when the data is insufficient or malformed."""
        try:
            if not cd or entry <= 0:
                return 0.0
            highs = cd.get("high") or []
            lows = cd.get("low") or []
            closes = cd.get("close") or []
            n = min(len(highs), len(lows), len(closes))
            if n < period + 1:
                return 0.0
            trs = []
            for i in range(n - period, n):
                h, l_, pc = float(highs[i]), float(lows[i]), float(closes[i - 1])
                trs.append(max(h - l_, abs(h - pc), abs(l_ - pc)))
            atr = sum(trs) / len(trs)
            return (atr / entry) * 100.0 if atr > 0 else 0.0
        except (TypeError, ValueError, IndexError):
            return 0.0

    def _measure_noise_floor_pct(self, sig: Any, ctx: ScanContext) -> float:
        """The pair's 1h noise band as % of entry: ATR(1h) preferred, with
        timescale-adjusted fallbacks so fresh pairs (short history — the
        NEW_LISTING cohort) still get a floor from whatever candles exist."""
        entry = float(getattr(sig, "entry", 0) or 0)
        candles = ctx.candles or {}
        pct = self._atr_pct_from_candles(candles.get("1h"), entry)
        if pct > 0:
            return pct
        # 15m ATR ×2 ≈ 1h-equivalent (sqrt(4) diffusion scaling)
        pct = self._atr_pct_from_candles(candles.get("15m"), entry)
        if pct > 0:
            return pct * 2.0
        # 5m ATR ×3.46 ≈ 1h-equivalent (sqrt(12))
        pct = self._atr_pct_from_candles(candles.get("5m"), entry)
        if pct > 0:
            return pct * 3.46
        atr_5m = float(getattr(sig, "atr_value_at_entry", 0) or 0)
        if atr_5m > 0 and entry > 0:
            return (atr_5m / entry) * 100.0 * 3.46
        return 0.0

    def _apply_noise_floor_stop(self, sig: Any, ctx: ScanContext) -> None:
        """Widen ``sig.stop_loss`` to the pair's noise floor.  Fail-open:
        any error leaves the evaluator's geometry untouched."""
        try:
            from src import runtime_tunables as _rt

            entry = float(getattr(sig, "entry", 0) or 0)
            sl = float(getattr(sig, "stop_loss", 0) or 0)
            if entry <= 0 or sl <= 0:
                return
            structural_dist_pct = abs(sl - entry) / entry * 100.0
            sig.sl_distance_pct_at_entry = structural_dist_pct
            noise_pct = self._measure_noise_floor_pct(sig, ctx)
            sig.noise_floor_pct = noise_pct
            if not _rt.get("noise_floor_stops_enabled") or noise_pct <= 0:
                return
            floor_pct = min(
                noise_pct * float(_rt.get("noise_floor_atr_mult")),
                float(_rt.get("noise_floor_max_sl_pct")),
            )
            if floor_pct <= structural_dist_pct or structural_dist_pct <= 0:
                return  # evaluator geometry already clears the floor
            is_long = sig.direction == Direction.LONG
            new_sl = (
                entry * (1.0 - floor_pct / 100.0)
                if is_long
                else entry * (1.0 + floor_pct / 100.0)
            )
            sig.stop_loss = round(new_sl, 8)
            sig.noise_floor_widen_factor = floor_pct / structural_dist_pct
            sig.sl_distance_pct_at_entry = floor_pct
            log.info(
                "NOISE_FLOOR widened {} {} {} stop {:.3f}%→{:.3f}% "
                "(1h-noise={:.3f}%, size ÷{:.2f} keeps risk constant)",
                sig.symbol, getattr(sig, "setup_class", ""), sig.direction.value,
                structural_dist_pct, floor_pct, noise_pct,
                sig.noise_floor_widen_factor,
            )
        except Exception as _nf_exc:  # fail-open — never block emission
            log.debug(
                "noise_floor error for {} (fail open): {}",
                getattr(sig, "symbol", "?"), _nf_exc,
            )

    def _get_channel_candidate(
        self,
        *,
        chan: Any,
        chan_name: str,
        symbol: str,
        ctx_for_chan: ScanContext,
        volume_24h: float,
        allowed_evaluators: Optional[frozenset] = None,
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
                allowed_evaluators=allowed_evaluators,
            )
        except Exception as _exc:
            log.debug("Channel {} eval error for {}: {}", chan_name, symbol, _exc)
            return None

    async def _scan_symbol(self, symbol: str, volume_24h: float) -> None:
        """Run all channel evaluations for one symbol."""
        ctx = await self._build_scan_context(symbol, volume_24h)
        if ctx is None:
            return
        # Populate the chartist-eye world model (LevelBook +
        # VolumeProfile + StructureTracker) eagerly per scanned symbol.
        # Without this, state only populated lazily inside
        # ``_prepare_signal``, which meant symbols whose candidates
        # filtered out upstream never got LevelBook entries — depriving
        # them of the CONFLUENCE / STRUCT_ALIGN bonuses PRs #314–#321
        # were designed to give them.  Truth report 2026-05-10 showed
        # 13/75 pairs populated; emissions concentrated to 2 symbols/day
        # as a result.  TTL-gated (``LEVEL_BOOK_REFRESH_SEC`` = 1 h) so
        # steady-state cost is a dict-lookup early-return.
        self._refresh_level_book_if_stale(symbol, ctx.candles)

        # Update per-cycle excursion for any in-play levels on this symbol
        # (level-rearm state machine).  Cheap dict walk filtered by symbol;
        # registry is typically <50 entries total system-wide.  Keeps the
        # gate honest even when no candidate is being dispatched this cycle.
        try:
            self._update_level_excursions(symbol)
        except Exception as exc:
            log.debug("level excursion sweep failed for {}: {}", symbol, exc)

        ticks = self.data_store.ticks.get(symbol, [])
        loop = asyncio.get_running_loop()

        # Compute rolling BTC correlation for this symbol (once per scan cycle)
        self._update_btc_correlation(symbol)

        # Shadow-only strategy units (Phase 3, observe-only): would-be trades
        # go straight into the shadow ledger, never the signal queue.
        try:
            self._evaluate_shadow_strategies(symbol, ctx)
        except Exception as exc:
            log.debug("shadow-strategy pass failed for {} (fail-open): {}", symbol, exc)

        # Collect all signals before deciding what to emit (confluence check)
        _pending_signals: list = []

        # SMC re-detect cache: deduplicate detections across channels sharing the same TF set.
        # Key: tuple of timeframes. Value: (SMCResult, smc_data_dict)
        _smc_cache: Dict[tuple, tuple] = {}

        # A promoted mover skipped *before* ScalpChannel.evaluate() runs (rollout
        # gate, channel skip, spread gate) never reaches the in-evaluator reason
        # capture — surface the scanner-side skip so the ops Pairs page shows the
        # real wall instead of a blank "—".
        _promoted_mover = symbol in self._mover_promoted_pairs

        def _note_mover_skip(_chan: Any, _reason: str) -> None:
            if _promoted_mover and _chan.config.name == "360_SCALP":
                _noter = getattr(_chan, "note_mover_skip", None)
                if _noter is not None:
                    _noter(symbol, _reason)

        for chan in self.channels:
            chan_name = chan.config.name
            # Controlled rollout gating (PR-5): explicit per-channel state
            # decides live eligibility with fail-closed semantics.
            if not self._is_live_rollout_enabled_for_symbol(chan_name, symbol):
                self._record_rollout_live_exclusion(chan_name, symbol)
                _note_mover_skip(chan, "rollout_excluded")
                continue
            _skip_reason = self._should_skip_channel(symbol, chan_name, ctx)
            if _skip_reason:
                _note_mover_skip(chan, _skip_reason)
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
                        _smc_r = await loop.run_in_executor(
                            self._scan_executor,
                            functools.partial(
                                self.smc_detector.detect,
                                symbol, ctx.candles, ticks, self.order_flow_store,
                                lookback=SMC_SCALP_LOOKBACK,
                                tolerance_pct=SMC_SCALP_TOLERANCE_PCT,
                                smc_timeframes=_ch_tfs,
                            ),
                        )
                        _new_smc_data = _smc_r.as_dict()
                        _redetect_orderblocks = _new_smc_data.get("orderblocks")
                        _redetect_count = (
                            len(_redetect_orderblocks)
                            if isinstance(_redetect_orderblocks, list)
                            else 0
                        )
                        # Carry over metadata fields added by _build_scan_context()
                        # that are not part of the SMCResult dataclass.
                        _new_smc_data["pair_profile"] = ctx.smc_data.get("pair_profile")
                        _new_smc_data["regime_context"] = ctx.smc_data.get("regime_context")
                        # Carry over order-flow fields wired in _build_scan_context()
                        # so evaluators see funding_rate and cvd regardless of which
                        # channel-specific SMC re-detect path is taken.
                        # Only carry over when the key was set (i.e. order_flow_store present).
                        for _of_key in (
                            "funding_rate",
                            "cvd",
                            "recent_ticks",
                            "orderblocks",
                            "orderblocks_detector_status",
                            "__orderblocks_trace",
                            "order_book",
                            "liquidation_clusters",
                            "__dependency_source_state",
                            "__dependency_state",
                        ):
                            if _of_key in ctx.smc_data:
                                _new_smc_data[_of_key] = ctx.smc_data[_of_key]
                        _handoff_orderblocks = _new_smc_data.get("orderblocks")
                        _handoff_count = (
                            len(_handoff_orderblocks)
                            if isinstance(_handoff_orderblocks, list)
                            else 0
                        )
                        if _handoff_count != _redetect_count:
                            log.debug(
                                "{} {} orderblocks handoff override: redetect_count={}, handoff_count={}",
                                symbol,
                                chan_name,
                                _redetect_count,
                                _handoff_count,
                            )
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

            self._record_dependency_readiness(chan_name, ctx_for_chan.smc_data)
            if chan_name == "360_SCALP":
                # ScalpChannel.evaluate() returns List[Signal] — every valid candidate
                # is processed independently through the gate chain.  Same-direction
                # signals from the same symbol are deduplicated here so that only one
                # setup per direction can enter _pending_signals per cycle.

                # Movers promotion: restrict to VSB + BREAKDOWN_SHORT only.
                # Spread pre-check: thin mover pairs with >0.5% spread are skipped.
                _mover_evaluators = frozenset({
                    "_evaluate_volume_surge_breakout",
                    "_evaluate_breakdown_short",
                    # Continuation pullback on a confirmed mover (Session 29).
                    # VSB/BDS catch the ignition; this catches the repeated
                    # MA-pullback re-entries that follow.  Ships dark.
                    "_evaluate_mover_trend_pullback",
                    # Anchored-VWAP mover scalp — the participant-cost reload, the
                    # primary continuation entry for a confirmed mover (2026-06-28).
                    "_evaluate_mover_avwap_scalp",
                    # _evaluate_mean_revert is DELIBERATELY absent: a mover
                    # promotion is a trending/ignition context — the anti-thesis
                    # of fading an extension back to the mean.
                    # _evaluate_range_fade is DELIBERATELY absent for the same
                    # reason: an igniting mover has no tested two-sided range
                    # to fade — the "edge" would be the launchpad.
                })
                _is_mover = symbol in self._mover_promoted_pairs
                # spread_pct is a PERCENT of mid (0.5 == 0.5%), same unit as the
                # config threshold. The prior gate compared against 0.005 — i.e.
                # 0.005% — which rejected every promoted mover before evaluation.
                if _is_mover and ctx_for_chan.spread_pct > MOVER_MAX_SPREAD_PCT:
                    self._suppression_counters[f"mover_spread_rejected:{chan_name}"] += 1
                    _note_mover_skip(chan, "spread_too_wide")
                    log.debug(
                        "mover spread gate {} {}: spread={:.3f}% > {:.3f}% — skip",
                        symbol, chan_name, ctx_for_chan.spread_pct, MOVER_MAX_SPREAD_PCT,
                    )
                    continue

                # Structure-readiness gate: structure-based evaluators
                # (SR_FLIP / FAR / QCB / TPE / DIV_CONT / CLS / PDC /
                # MA_CROSS / STANDARD) require an aged multi-TF level
                # foundation to evaluate their thesis honestly.  Pairs
                # promoted into the active universe in the last few days
                # don't have enough 1d swing-pivot history for those
                # evaluators yet — they'd dispatch low-quality signals on
                # nascent levels (bug 2026-05-11: QUSDT carbon-copy
                # SR_FLIP emissions on a 2-day-old listing).
                #
                # When the LevelBook's 1d-anchored level count for this
                # symbol is below ``MIN_1D_LEVELS_FOR_STRUCTURE_PATHS``,
                # restrict to the breakout-/event-family allowlist
                # (price-driven and tape-driven paths whose thesis does
                # NOT require aged structure).  This is broader than the
                # mover restriction (which is 2 paths) because more
                # young-pair-safe paths exist; the two restrictions
                # compose — both must allow the evaluator for it to run.
                _is_structurally_aged = self._is_pair_structurally_aged(symbol)
                _allowed_evals: Optional[frozenset] = None
                if not _is_structurally_aged:
                    _allowed_evals = _YOUNG_PAIR_EVALUATORS
                    self._suppression_counters[
                        f"young_pair_restriction:{symbol}"
                    ] += 1
                if _is_mover:
                    # Mover restriction is the stricter of the two — it
                    # always supersedes when both apply (intersection).
                    _allowed_evals = _mover_evaluators

                _raw_result = await loop.run_in_executor(
                    self._scan_executor,
                    functools.partial(
                        self._get_channel_candidate,
                        chan=chan,
                        chan_name=chan_name,
                        symbol=symbol,
                        ctx_for_chan=ctx_for_chan,
                        volume_24h=volume_24h,
                        allowed_evaluators=_allowed_evals,
                    ),
                )
                self._record_scalp_generation_telemetry(chan, chan_name)
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
                    self._increment_path_funnel("scanner_preparation", chan_name, _raw_setup)
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
                _raw_result = await loop.run_in_executor(
                    self._scan_executor,
                    functools.partial(
                        self._get_channel_candidate,
                        chan=chan,
                        chan_name=chan_name,
                        symbol=symbol,
                        ctx_for_chan=ctx_for_chan,
                        volume_24h=volume_24h,
                    ),
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
                    _sc_for_cd = getattr(sig, "setup_class", chan_name) or chan_name
                    self._suppression_counters[
                        f"enqueue_stage:global_cooldown:{_sc_for_cd}"
                    ] += 1
                    log.info(
                        "global_cooldown skip {} {} {} (setup={})",
                        symbol, _sig_dir, chan_name, _sc_for_cd,
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
                _radar_result = await loop.run_in_executor(
                    self._scan_executor,
                    functools.partial(
                        chan.evaluate,
                        symbol=symbol,
                        candles=ctx.candles,
                        indicators=ctx.indicators,
                        smc_data=ctx.smc_data,
                        spread_pct=ctx.spread_pct,
                        volume_24h_usd=volume_24h,
                        regime=_regime_str,
                    ),
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
                        # Radar/WATCHLIST free-channel alerts disabled — too spammy
                        pass  # _radar_cb disabled
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
