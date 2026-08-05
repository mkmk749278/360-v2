"""360_SCALP – M1/M5 High-Frequency Scalping ⚡

Trigger : M5 Liquidity Sweep + Momentum > 0.15 % over 3 candles
          TREND_PULLBACK path: EMA pullback in trend direction
          LIQUIDATION_REVERSAL path: cascade exhaustion + CVD divergence
          WHALE_MOMENTUM path: large volume spike + OBI imbalance
Filters : EMA alignment, ADX > 20, ATR-based volatility, spread < 0.02 %, liquidity
Risk    : SL 0.05–0.1 %, TP1 0.5–1R, TP2 1–1.5R, TP3 optional 20 %, Trailing 1.5–2×ATR
"""

from __future__ import annotations

import os
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


from config import (
    CHANNEL_SCALP,
    FUNDING_RATE_EXTREME_THRESHOLD,
    SCALP_ORB_ENABLED,
    SR_FLIP_LONG_ENABLED,
    SR_FLIP_LONG_BREAK_VOL_MULT,
    SR_FLIP_LONG_MIN_HOLD_CLOSES,
    MOVER_TREND_PULLBACK_ENABLED,
    MOVER_AVWAP_SCALP_ENABLED,
    MOVER_AVWAP_TF,
    MOVER_AVWAP_ANCHOR_LOOKBACK,
    MOVER_AVWAP_MIN_MOVE_PCT,
    MOVER_AVWAP_SLOPE_MIN_PCT,
    MOVER_AVWAP_SLOPE_LOOKBACK,
    MOVER_AVWAP_PULLBACK_BAND_PCT,
    MOVER_AVWAP_VOL_MULT,
    MOVER_AVWAP_SL_BUFFER_ATR,
    MOVER_TP_MA_FAST,
    MOVER_TP_MA_MID,
    MOVER_TP_MA_SLOW,
    MOVER_TP_PULLBACK_BAND_PCT,
    MOVER_TP_SL_BUFFER_ATR,
    MOVER_TP_MIN_STACK_SEP_PCT,
    MOVER_TP_TRIGGER_DEEP_ENABLED,
    MOVER_TP_TRIGGER_CONSOL_ENABLED,
    MOVER_TP_CONSOL_LOOKBACK,
    MOVER_TP_CONSOL_RANGE_ATR,
    MOVER_TP_BREAKOUT_EXT_ATR,
    MOVER_TP_BREAKOUT_VOL_MULT,
    MEAN_REVERT_LIVE,
    RANGE_FADE_LIVE,
)
from src import dark_emission, fail_open
from src.channels.base import BaseChannel, Signal, build_channel_signal
from src.filters import (
    check_adx,
    check_macd_confirmation,
    check_rsi_regime,
    check_ema_alignment_adaptive,
    check_spread_adaptive,
    check_volume,
)
from src.mtf import mtf_gate_scalp_standard
from src.shadow_strategies import (
    _ATR_PERIOD as _MEANREV_ATR_PERIOD,
    _MEANREV_LOOKBACK,
    _RANGE_LOOKBACK,
    evaluate_mean_revert as shadow_mean_revert,
    evaluate_range_fade as shadow_range_fade,
)
from src.smc import Direction
from src.vwap import compute_vwap
from src.utils import get_logger

log = get_logger("scalp")

# HTF EMA rejection threshold: only reject if price is within this % of EMA200
# AND moving toward it. 0.15% is more permissive than the old 0.05% — valid
# EMA tests that bounce are no longer rejected.
_HTF_EMA_REJECTION_PCT: float = float(os.getenv("HTF_EMA_REJECTION_PCT", "0.0015"))

# LSR HTF POI anchor — multiplier applied to ATR for the band-width check
# that anchors the swept level to a multi-TF LevelBook entry.  Per
# OWNER_BRIEF §3.4a "HTF Structure, LTF Entry" — LSR sweeps must occur at
# structurally significant HTF levels (CLUSTERED in LevelBook or
# VP_ANCHORED), not at arbitrary 5m local extrema.  ATR×2 is wider than
# chartist-eye confluence (~0.3%) because the sweep candle itself can
# wick 1-2 ATR past the level before reclaiming — we anchor on the swept
# level, not the close.  Env-overridable per B8.
_LSR_POI_ANCHOR_ATR_MULT: float = float(os.getenv("LSR_POI_ANCHOR_ATR_MULT", "2.0"))

# TPE 1H pullback proximity multiplier (OWNER_BRIEF §3.4a row 2, 2026-05-17).
# At least one of the last 4 closed 1H bars must have approached the 1H
# EMA21 within ATR_1h × this multiplier.  Defines what "pulled back to
# EMA21" means structurally — too tight (e.g. 0.10) and ordinary trending
# bars never qualify; too loose (e.g. 2.0) and the gate is a no-op since
# almost every bar is within 2×ATR of any EMA.  0.50 is the sweet spot
# per industry pullback-trading literature.  Env-overridable per B8.
_TPE_H1_PULLBACK_ATR_MULT: float = float(
    os.getenv("TPE_H1_PULLBACK_ATR_MULT", "0.50")
)

# DIVERGENCE_CONTINUATION — 15m CVD divergence detection windows
# (OWNER_BRIEF §3.4a: HTF Structure, LTF Entry).  Pre-2026-05-17 DIV_CONT
# read CVD divergence off 5m bars where the signal is dominated by
# microstructure noise (664 sigs, 63% MFE=0 in the forensic — second-worst
# path after TPE).  15m series carries enough trade-flow integration to
# express genuine accumulation/distribution divergence vs price.
# Default 12 bars = 3 hours of 15m candles — matches the natural unwind
# window for an HTF continuation divergence.  Fallback 6-bar window
# (1.5h) catches shorter-form divergences when the 12-bar absent.
_DIV_CONT_15M_LOOKBACK: int = int(os.getenv("DIV_CONT_15M_LOOKBACK", "12"))
_DIV_CONT_15M_LOOKBACK_MIN: int = int(os.getenv("DIV_CONT_15M_LOOKBACK_MIN", "6"))

# WHALE_MOMENTUM thresholds (absorbed from former TapeChannel).  Env-overridable
# per B8 so operators can tune for current market conditions without redeploy.
#
# WHALE_DELTA_MIN_RATIO stays at 2.0 — this is the direction-conviction gate
# (buy_vol must be 2× sell_vol or vice versa).  Loosening direction conviction
# would degrade signal quality.
#
# WHALE_MIN_TICK_VOLUME_USD lowered 500k → 200k on 2026-05-27 after truth report
# showed WHALE_MOMENTUM at 0 signals from 308k attempts.  21% of rejections were
# at this gate (`recent_ticks_insufficient`).  $500k of cumulative tick volume in
# the last 100 trades was achievable only on the top 5-10 pairs at peak hours;
# $200k captures the broader top-75 alt universe while still requiring real
# continuous flow (avg $2k/tick × 100 ticks).
_WHALE_DELTA_MIN_RATIO: float = float(os.getenv("WHALE_DELTA_MIN_RATIO", "2.0"))
_WHALE_MIN_TICK_VOLUME_USD: float = float(os.getenv("WHALE_MIN_TICK_VOLUME_USD", "200000"))
_WHALE_OBI_MIN: float = float(os.getenv("WHALE_OBI_MIN", "1.5"))

# VSB / BREAKDOWN_SHORT breakout-candle volume threshold (was hardcoded 2.0).
# Env-overridable per B8.  This is the surge-confirmation gate on the closed
# breakout candle itself — distinct from the (now-removed) current-candle
# volume gate.
_VSB_BREAKOUT_VOL_MULT: float = float(os.getenv("VSB_BREAKOUT_VOL_MULT", "2.0"))

# VSB / BDS breakout-detection geometry (calibrated 2026-05-11).
# Truth report showed VSB at 998k/1.89M (53%) and BDS at 1.19M/1.89M (63%)
# rejecting on ``breakout_not_found`` — the engine missed every 10%+ pump
# and dump on the 75-pair universe across the entire window.  The original
# 5-candle search window (= 25 min on 5m candles) is too narrow for fast
# vertical moves where the breakout candle slips past index [-6] before
# the next scan cycle catches the pullback.  The original
# ``highs[-26:-6]`` swing reference includes early-rally candles, biasing
# swing_high upward and rejecting genuine pullback retests against the
# real prior structure.  Calibration:
#
# * ``BREAKOUT_SEARCH_WINDOW``: 5 → 12 candles (60 min instead of 25 min).
# * ``SWING_LOOKBACK_START`` / ``SWING_LOOKBACK_END``: ``[-26:-6]`` →
#   ``[-50:-15]``.  Pushes the reference 75-250 min back so the rally
#   itself doesn't bias the level.
# * ``PULLBACK_MAX_PCT``: 0.75% → 1.5%.  Catches the deeper retests
#   common in strong moves.  Extended-zone (0.6%-1.5%) keeps the
#   existing +3.0 soft penalty so quality stays gated.
#
# All env-overridable per B8.  VSB / BDS share the same shape — separate
# knobs so each can be tuned independently from observation data.
_VSB_BREAKOUT_SEARCH_WINDOW: int = int(os.getenv("VSB_BREAKOUT_SEARCH_WINDOW", "12"))
_VSB_SWING_LOOKBACK_START: int = int(os.getenv("VSB_SWING_LOOKBACK_START", "-50"))
_VSB_SWING_LOOKBACK_END: int = int(os.getenv("VSB_SWING_LOOKBACK_END", "-15"))
_VSB_PULLBACK_MAX_PCT: float = float(os.getenv("VSB_PULLBACK_MAX_PCT", "1.5"))
_BDS_BREAKOUT_SEARCH_WINDOW: int = int(os.getenv("BDS_BREAKOUT_SEARCH_WINDOW", "12"))
_BDS_SWING_LOOKBACK_START: int = int(os.getenv("BDS_SWING_LOOKBACK_START", "-50"))
_BDS_SWING_LOOKBACK_END: int = int(os.getenv("BDS_SWING_LOOKBACK_END", "-15"))
_BDS_PULLBACK_MAX_PCT: float = float(os.getenv("BDS_PULLBACK_MAX_PCT", "1.5"))

# ── Mover-freshness gate (VSB / BDS) ──────────────────────────────────────
# The mover universe is promoted off a LAGGING 24h |%change|
# (pair_manager.volatility_24h = abs(priceChangePercent)), so by the time
# VSB/BDS evaluate, the move is often already mature — the "promote after the
# move, then fight the exhaustion" failure mode. This gate, applied once the
# breakout/breakdown candle is found, requires:
#   (1) RECENCY — the breakout candle is within MAX_BREAKOUT_AGE candles
#       (default 4 = 20 min on 5m), not a stale ~60-min-old break.
#   (2) IMPULSE BAND — the recent move INTO the broken level (over LOOKBACK
#       candles) sits in [MIN_PCT, MAX_PCT]:
#         • below MIN  → no live momentum: the 24h move is old/stale.
#         • above MAX  → blow-off / exhausted: entering late into the
#                        mean-reversion (the BDS oversold-bounce trap; the
#                        ceiling is the symmetric exhaustion guard for shorts).
# Applies to VSB/BDS on every pair — a stale or exhausted continuation
# breakout is a poor entry regardless of how the pair was scanned. Reversible
# via MOVER_FRESHNESS_ENABLED; reject reasons surface in suppression telemetry.
# Env-overridable per B8.
_MOVER_FRESHNESS_ENABLED: bool = os.getenv(
    "MOVER_FRESHNESS_ENABLED", "true"
).lower() in ("1", "true", "yes")
_MOVER_FRESHNESS_LOOKBACK: int = int(os.getenv("MOVER_FRESHNESS_LOOKBACK", "12"))
_MOVER_FRESHNESS_MIN_PCT: float = float(os.getenv("MOVER_FRESHNESS_MIN_PCT", "1.5"))
_MOVER_FRESHNESS_MAX_PCT: float = float(os.getenv("MOVER_FRESHNESS_MAX_PCT", "10.0"))
_MOVER_FRESHNESS_MAX_BREAKOUT_AGE: int = int(
    os.getenv("MOVER_FRESHNESS_MAX_BREAKOUT_AGE", "4")
)
# In fast/volatile regimes the order book can be temporarily thin or skewed by
# market-maker spread widening.  When the OBI ratio is marginal — present but
# below the full confirmation threshold — apply a soft penalty rather than
# hard-rejecting.  Below this floor the check is still a hard reject.
_WHALE_OBI_SOFT_MIN: float = 1.2
# Regimes where OBI imbalance is treated as a soft confidence contributor (via
# penalty) rather than a hard gate when the ratio falls in the marginal band
# [_WHALE_OBI_SOFT_MIN, _WHALE_OBI_MIN).  Outside these regimes any ratio below
# _WHALE_OBI_MIN remains a hard reject.
_WHALE_FAST_REGIMES: frozenset = frozenset({
    "VOLATILE", "VOLATILE_UNSUITABLE", "BREAKOUT_EXPANSION",
})
# RSI thresholds for the layered soft/hard gate.  Hard limits reject extreme
# exhaustion that invalidates the momentum thesis; soft limits penalise
# borderline readings that may still resolve in the signal's favour.
_WHALE_RSI_LONG_HARD_MAX: float = 82.0   # ≥ this → hard reject (overbought)
_WHALE_RSI_LONG_SOFT_MIN: float = 72.0   # ≥ this (< hard) → +5 soft penalty
_WHALE_RSI_SHORT_HARD_MIN: float = 18.0  # ≤ this → hard reject (oversold)
_WHALE_RSI_SHORT_SOFT_MAX: float = 28.0  # ≤ this (> hard) → +5 soft penalty

# Regime-adaptive ADX floor for the standard scalp path.  In RANGING/QUIET
# markets ADX hovers at 15-20 and blocks most liquidity-sweep setups.
# Absolute minimum prevents the gate from becoming too permissive.
_ADX_RANGING_FLOOR: float = 12.0
# Multiplier applied to the pair-specific adx_min in RANGING/QUIET regimes.
_ADX_RANGING_MULTIPLIER: float = 0.75

# Regimes where fast momentum makes FVG/OB detection lag — the VOLUME_SURGE_BREAKOUT
# path treats the FVG/OB requirement as a soft confidence contributor rather than a
# hard gate in these regimes.
_FAST_MOMENTUM_REGIMES: frozenset = frozenset({
    "VOLATILE", "VOLATILE_UNSUITABLE", "BREAKOUT_EXPANSION", "STRONG_TREND",
})

# Regimes where fast bearish momentum makes FVG/OB detection lag — the BREAKDOWN_SHORT
# path treats the FVG/OB requirement as a soft confidence contributor rather than a
# hard gate in these regimes.  Superset of _FAST_MOMENTUM_REGIMES with TRENDING_DOWN
# added because that regime is the primary fast bearish continuation environment.
_FAST_BEARISH_REGIMES: frozenset = frozenset({
    "VOLATILE", "VOLATILE_UNSUITABLE", "BREAKOUT_EXPANSION", "STRONG_TREND", "TRENDING_DOWN",
})

# Regimes where trending / expanding momentum makes FVG/OB detection lag — the
# SR_FLIP_RETEST path treats the FVG/OB requirement as a soft confidence contributor
# rather than a hard gate in these regimes.  Covers both directional trending contexts
# (TRENDING_UP / TRENDING_DOWN) and expansion phases.  VOLATILE is excluded because
# SR_FLIP_RETEST already hard-blocks that regime at entry.
_FAST_STRUCTURAL_REGIMES: frozenset = frozenset({
    "BREAKOUT_EXPANSION", "STRONG_TREND", "TRENDING_UP", "TRENDING_DOWN",
})

# CONTINUATION_LIQUIDITY_SWEEP path constants.
# Regimes where the sweep-continuation setup is valid.  VOLATILE,
# VOLATILE_UNSUITABLE, RANGING, and QUIET are all hard-blocked:
# VOLATILE/VOLATILE_UNSUITABLE — chaotic orderflow invalidates continuation;
# RANGING/QUIET — no directional trend to continue into.
_CLS_VALID_REGIMES: frozenset = frozenset({
    "TRENDING_UP", "TRENDING_DOWN", "STRONG_TREND", "WEAK_TREND",
    "BREAKOUT_EXPANSION",
})
# OWNER_BRIEF §3.4a — CLS disabled 2026-05-17, merged into LSR via the
# HTF POI anchor.  Default True (disabled); flip to False via env to
# re-enable if LSR's HTF anchor proves to under-catch trend-aligned
# sweeps in the observation window.
_CLS_DISABLED_2026_05_17: bool = (
    os.getenv("CLS_DISABLED_2026_05_17", "true").lower()
    not in {"0", "false", "no", "off"}
)
# Max candle offset (back from current) where a sweep is still considered
# "recent enough" to anchor a continuation entry.
_CLS_SWEEP_WINDOW: int = 10
# Sweep is "very recent" (strong recency bonus) when within this many candles.
_CLS_SWEEP_RECENT: int = 5
# RSI hard/soft thresholds for the layered gate.
_CLS_RSI_LONG_HARD_MAX: float = 80.0   # ≥ this → hard reject (overbought)
_CLS_RSI_LONG_SOFT_MIN: float = 70.0   # ≥ this (< hard) → +6 soft penalty
_CLS_RSI_SHORT_HARD_MIN: float = 20.0  # ≤ this → hard reject (oversold)
_CLS_RSI_SHORT_SOFT_MAX: float = 30.0  # ≤ this (> hard) → +6 soft penalty

# POST_DISPLACEMENT_CONTINUATION path constants.
# Regimes where a displacement + consolidation + re-acceleration setup is valid.
# VOLATILE/VOLATILE_UNSUITABLE: chaotic orderflow — displacement can't be reliably
# identified as institutional (too much noise).  RANGING/QUIET: no directional
# context means the "displacement" is really just a spike, not a sustained move.
_PDC_VALID_REGIMES: frozenset = frozenset({
    "TRENDING_UP", "TRENDING_DOWN", "STRONG_TREND", "WEAK_TREND",
    "BREAKOUT_EXPANSION",
})
# Consolidation phase length: candles between the displacement candle and current.
_PDC_CONSOL_MIN: int = 2   # Minimum — shorter = not yet consolidated
_PDC_CONSOL_MAX: int = 5   # Maximum — longer = structure has dissipated
# Displacement candle body must fill at least this fraction of the candle range.
# Ensures only genuine directional displacement candles qualify (not wicky,
# indecisive candles with a coincidental volume spike).
_PDC_DISP_BODY_RATIO_MIN: float = 0.60
# Displacement candle volume must be at least this multiple of the rolling average.
# Ensures the displacement was driven by genuine institutional participation.
_PDC_DISP_VOLUME_MULT: float = 2.5
# Consolidation range as a fraction of the displacement body.
# Tight consolidation = genuine absorption. Wide consolidation = continuation move
# or chop, not absorption.
_PDC_CONSOL_RANGE_MAX_RATIO: float = 0.50
# RSI hard/soft thresholds for the layered gate (same pattern as WHALE_MOMENTUM
# and CLS: hard reject only at true extremes; soft penalty in borderline zone).
_PDC_RSI_LONG_HARD_MAX: float = 82.0   # ≥ this → hard reject (overbought)
_PDC_RSI_LONG_SOFT_MIN: float = 72.0   # ≥ this (< hard) → +6 soft penalty
_PDC_RSI_SHORT_HARD_MIN: float = 18.0  # ≤ this → hard reject (oversold)
_PDC_RSI_SHORT_SOFT_MAX: float = 28.0  # ≤ this (> hard) → +6 soft penalty

# FAILED_AUCTION_RECLAIM path constants.
# Regimes where a failed breakout / failed breakdown reclaim setup is valid.
# VOLATILE/VOLATILE_UNSUITABLE: chaotic orderflow makes level identification
# unreliable — false-auction candles are indistinguishable from genuine breakouts.
# STRONG_TREND: genuine breakouts succeed in strong trends; FAR has very low
# edge when directional momentum is overwhelming (false-breakouts rarely hold).
_FAR_BLOCKED_REGIMES: frozenset = frozenset({
    "VOLATILE", "VOLATILE_UNSUITABLE", "STRONG_TREND",
})
# Lookback for computing the reference structural level (prior swing high/low).
# Excludes the auction window so the failed-auction candle doesn't contaminate
# the reference level used to measure the breakout.
_FAR_STRUCT_LOOKBACK: int = 20
# Window within which to search for the failed-auction candle (positions back
# from the current bar, not counting current bar itself).
_FAR_AUCTION_WINDOW_MIN: int = 1  # Nearest candle that can be the auction bar
_FAR_AUCTION_WINDOW_MAX: int = 7  # Furthest candle; beyond this the signal is stale
# A breakout is "failed" when the candle closed within this fraction of the
# reference level (close was at or near the level, not convincingly beyond it).
# A value of 0.002 means the close must be within 0.2% of the level to count.
_FAR_ACCEPTANCE_THRESHOLD: float = 0.001
# Minimum reclaim distance (as a multiple of ATR) required from the reference
# level to the current close.  Ensures a genuine reclaim, not a marginal tick.
# Tightened 2026-05-17 (0.10 → 0.25) per OWNER_BRIEF §3.4a row 4 — a 0.10×ATR
# reclaim is within noise on a 5m bar; 0.25×ATR is meaningful rejection.
_FAR_MIN_RECLAIM_ATR: float = float(os.getenv("FAR_MIN_RECLAIM_ATR", "0.25"))
# Minimum auction-candle tail length (as a multiple of ATR).  Real SFP wicks
# are substantial — the rejection IS the signature.  Tightened 2026-05-17
# (0.30 → 0.50).
_FAR_MIN_TAIL_ATR: float = float(os.getenv("FAR_MIN_TAIL_ATR", "0.50"))
# R:R floor for TP1.  Raised 2026-05-17 (1.0 → 2.0) per OWNER_BRIEF §3.2 /
# B11 — at 10x leverage and ~0.7% round-trip fees, R:R 1.0 requires > 70%
# win rate to break even net; truth report had FAR at ~6% win rate.  R:R
# 2.0 brings the breakeven win rate down to ~40%, which is in scalp range.
_FAR_MIN_RR: float = float(os.getenv("FAR_MIN_RR", "2.0"))
# RSI hard/soft thresholds.  More conservative than PDC because FAR is a
# reversal-of-failure setup (counter to the initial failed breakout direction).
_FAR_RSI_LONG_HARD_MAX: float = 75.0   # ≥ this → hard reject (overbought)
_FAR_RSI_LONG_SOFT_MIN: float = 65.0   # ≥ this (< hard) → +6 soft penalty
_FAR_RSI_SHORT_HARD_MIN: float = 25.0  # ≤ this → hard reject (oversold)
_FAR_RSI_SHORT_SOFT_MAX: float = 35.0  # ≤ this (> hard) → +6 soft penalty

# SR_FLIP_RETEST HTF policy — soft penalty for HTF mismatch.
# Aligned with the scalping doctrine codified in OWNER_BRIEF §2.1a.
# Counter-trend SR_FLIP setups (e.g., resistance held during an uptrend
# pullback → SHORT scalp) are legitimate scalp products; hard-blocking
# them eliminates ~half the path's edge in correlated trending markets.
# Soft penalty (default 6.0 confidence pts) when BOTH 1H AND 4H oppose
# direction lets scoring decide.  Env-overridable per B8.
_SR_FLIP_HTF_MISMATCH_PENALTY: float = float(os.getenv("SR_FLIP_HTF_MISMATCH_PENALTY", "6.0"))
# Additional penalty when only 4H (not 1H) opposes SR_FLIP direction.
# BOTH opposing = full _SR_FLIP_HTF_MISMATCH_PENALTY; 4H-only opposing = this.
# Truth-report: 17/175 SR_FLIP invalidation kills were PREMATURE but 129/175
# were PROTECTIVE — adding a 4H-weight haircut reduces directional noise.
_SR_FLIP_H4_ONLY_PENALTY: float = float(os.getenv("SR_FLIP_H4_ONLY_PENALTY", "3.5"))
# RANGING quality re-tighten (2026-06-16).  SR_FLIP bleeds specifically in
# RANGING (live: -3.97 over 32 sigs, all ATR buckets) while it is flat-to-
# positive in trends (+0.21 TRENDING_DOWN) — so the fix is to GENERATE only
# the cleanest retests in range, not to disable the setup.  When enabled, two
# loosened gates revert to hard *only in RANGING*: (1) the extended retest zone
# (premium-zone retest required), and (2) the 70-79 / 21-30 RSI soft band
# (no chasing overbought/oversold retests).  Trending + premium-zone signals
# are untouched.  Ships dark with [SHADOW] telemetry so the would-be-rejected
# volume and its outcomes are measurable before activation.  Evaluator-path /
# paid-channel routing change — owner sign-off to set
# SR_FLIP_RANGING_STRICT_ENABLED=true on the VPS.
_SR_FLIP_RANGING_STRICT_ENABLED: bool = (
    os.getenv("SR_FLIP_RANGING_STRICT_ENABLED", "false").strip().lower()
    in ("1", "true", "yes", "on")
)
# DIVERGENCE_CONTINUATION 4H conflict penalty.
# When the 4H EMA21/50 trend opposes the 1H-determined direction, CVD
# divergence is fighting two-TF structure — the setup is weaker.
# BEATUSDT SHORT at -6.52% ACTIVE: 1H barely aligned (EMA21 < EMA50) but
# 4H was still bullish.  Soft penalty keeps correct multi-TF aligned signals
# while downgrading borderline 1H-only ones.  Env-overridable per B8.
_DIV_CONT_H4_CONFLICT_PENALTY: float = float(os.getenv("DIV_CONT_H4_CONFLICT_PENALTY", "6.0"))

# QUIET_COMPRESSION_BREAK HTF policy — soft penalty.  QCB lives in
# QUIET/RANGING regimes where HTF trends are typically weak; the soft
# penalty rarely fires but adds a conservative confidence haircut on the
# rare occasions when a compression break does fight an unambiguous HTF.
# Same env-overridable pattern.
_QCB_HTF_MISMATCH_PENALTY: float = float(os.getenv("QCB_HTF_MISMATCH_PENALTY", "6.0"))

# QCB volume confirmation multiplier (OWNER_BRIEF §3.4a row 5, 2026-05-17).
# The closed prior 5m candle's volume must be at least this multiple of the
# 20-bar rolling average for the breakout to be considered volume-confirmed.
# Literature on BB squeeze breakouts is consistent that breakouts without
# volume are 40-50% false; the 1.5× threshold is conservative since QCB
# fires in QUIET regime where absolute volumes are already below cross-
# regime averages.  Env-overridable per B8.
_QCB_VOLUME_CONFIRMATION_MULT: float = float(
    os.getenv("QCB_VOLUME_CONFIRMATION_MULT", "1.5")
)

# FAILED_AUCTION_RECLAIM HTF policy — soft penalty for HTF mismatch.
# We are a SCALPING system (per OWNER_BRIEF Part II): direction-agnostic,
# fast in/out, profitable signals matter more than directional alignment.
# Counter-trend FAR setups are *legitimate* scalp opportunities — a failed
# auction at resistance during an uptrend is exactly the kind of brief
# retracement scalp we want to capture.  Hard-blocking these would
# eliminate ~half the path's edge in trending markets where top-75 pairs
# move correlated to BTC.
#
# Soft penalty (default 6.0 confidence pts) when BOTH 1H AND 4H oppose
# direction — lets scoring decide whether the signal still clears the
# tier threshold.  Env-overridable per B8.  Set to 0 to disable entirely.
_FAR_HTF_MISMATCH_PENALTY: float = float(os.getenv("FAR_HTF_MISMATCH_PENALTY", "6.0"))

# WHALE_MOMENTUM SL: look at this many closed 1m candles (before the current bar)
# to find the recent swing low/high as the order-flow invalidation point.
# A 5-bar window captures the impulse origin without going too far back.
_WHALE_SWING_LOOKBACK: int = 5
# Buffer below swing low / above swing high for the invalidation SL (0.1%).
# Prevents the stop from sitting exactly on a round swing level.
_WHALE_SWING_BUFFER: float = 0.001


def _funding_extreme_structure_tp1(
    fvgs: list,
    orderblocks: list,
    close: float,
    direction: Direction,
    sl_dist: float,
) -> float:
    """Nearest FVG/OB structure level as thesis-aligned TP1 for FUNDING_EXTREME_SIGNAL.

    The path already requires FVG or OB confluence at entry, so the nearest
    qualifying structure level in the direction of travel is the natural first
    normalization target.  Requires at least 1.0R separation so the TP is
    meaningful rather than trivially close.  Falls back to 1.5R when no
    qualifying level is found.
    """
    candidates: list[float] = []
    min_dist = sl_dist  # must be at least 1.0R away from entry

    for zone in list(fvgs) + list(orderblocks):
        level: Optional[float] = None
        if isinstance(zone, dict):
            # Prefer the far edge of the FVG in the direction of travel;
            # fall through to generic 'level' or 'price' if specific keys absent.
            if direction == Direction.LONG:
                raw = (
                    zone.get("gap_high")
                    or zone.get("top")
                    or zone.get("level")
                    or zone.get("high")
                )
            else:
                raw = (
                    zone.get("gap_low")
                    or zone.get("bottom")
                    or zone.get("level")
                    or zone.get("low")
                )
            if raw is not None:
                level = float(raw)
        else:
            # Object-style FVG / OB
            attr_order = (
                ("gap_high", "top", "level", "price")
                if direction == Direction.LONG
                else ("gap_low", "bottom", "level", "price")
            )
            for attr in attr_order:
                v = getattr(zone, attr, None)
                if v is not None:
                    level = float(v)
                    break

        if level is None or level <= 0:
            continue
        if direction == Direction.LONG and level >= close + min_dist:
            candidates.append(level)
        elif direction == Direction.SHORT and level <= close - min_dist:
            candidates.append(level)

    if candidates:
        # Return the nearest qualifying level in the direction of travel.
        return min(candidates) if direction == Direction.LONG else max(candidates)

    # Fallback: 1.5R — better than the previous flat 0.5% placeholder.
    return (
        close + sl_dist * 1.5
        if direction == Direction.LONG
        else close - sl_dist * 1.5
    )


def _enforce_tp_ladder_monotonicity(
    tp1: float,
    tp2: float,
    tp3: float,
    close: float,
    sl_dist: float,
    direction: Direction,
    *,
    tp2_rmult_floor: float = 2.5,
    tp3_rmult_floor: float = 3.5,
    tp_gap_rmult: float = 0.5,
) -> tuple[float, float, float]:
    """Enforce TP-ladder monotonicity post-fallback (Q4-B audit fix).

    Mirrors the FAILED_AUCTION_RECLAIM pattern (canonical reference at the
    end of `_evaluate_failed_auction_reclaim`): when the geometry-derived
    tp2 (or tp3) collapses to-or-past tp1 (or tp2) for LONG / SHORT, set
    it to a value that is BOTH ≥ R-multiple-from-close AND prior-tp plus
    a gap of ``tp_gap_rmult × sl_dist``.

    Defaults (``tp2_rmult_floor=2.5``, ``tp3_rmult_floor=3.5``,
    ``tp_gap_rmult=0.5``) match FAR's deployed values.  Each evaluator
    overrides via kwargs to preserve its own R-multiple intent (e.g. TPE
    uses 2.0 / 4.0; FUNDING_EXTREME uses 2.0 / 3.5).

    No-op when the ladder is already monotonic — the helper only widens,
    never narrows.  Pure arithmetic; no IO, no logging.
    """
    if direction == Direction.LONG:
        if tp2 <= tp1:
            tp2 = max(close + sl_dist * tp2_rmult_floor, tp1 + sl_dist * tp_gap_rmult)
        if tp3 <= tp2:
            tp3 = max(close + sl_dist * tp3_rmult_floor, tp2 + sl_dist * tp_gap_rmult)
    else:
        if tp2 >= tp1:
            tp2 = min(close - sl_dist * tp2_rmult_floor, tp1 - sl_dist * tp_gap_rmult)
        if tp3 >= tp2:
            tp3 = min(close - sl_dist * tp3_rmult_floor, tp2 - sl_dist * tp_gap_rmult)
    return tp1, tp2, tp3


# ═══════════════════════════════════════════════════════════════════════════
# SR_FLIP structural-level detection (Item #7 audit fix)
# ───────────────────────────────────────────────────────────────────────────
# Prior implementation used `max(prior_highs)` / `min(prior_lows)` as the
# flipped S/R level — a single 41-bar scalar extremum, which is not a
# structural level (no multi-touch history, no volume anchoring).  That
# caused two failure modes: (1) SL placed against a random past wick that
# had no reason to hold, and (2) when the scalar-max high sat above a
# lower level that actually got broken, the evaluator rejected valid
# retests because it was looking for a breakout of the wrong price.
#
# This helper produces a ranked list of structurally-validated resistance
# and support candidates:
#   • CLUSTERED      — ≥2 swing-pivot touches within an ATR band
#   • VP_ANCHORED    — volume-profile POC / VAH / VAL
#   • SCALAR_FALLBACK — legacy max(highs)/min(lows) (always emitted so the
#                      path never loses a setup it would have caught before)
#
# Selection prefers candidates that were actually broken+closed past in the
# 8-bar recent window.  All downstream evaluator logic is unchanged.
# See: audit 2026-04-24, Item #7 design spec.
# ═══════════════════════════════════════════════════════════════════════════

from dataclasses import dataclass as _dataclass  # noqa: E402


@_dataclass(frozen=True)
class _StructuralLevel:
    price: float
    side: str                    # "RESISTANCE" | "SUPPORT"
    quality: str                 # "CLUSTERED" | "VP_ANCHORED" | "SCALAR_FALLBACK"
    touch_count: int             # 1 for fallback, >=2 for CLUSTERED
    atr_normalized_width: float  # 0.0 for non-clustered
    was_broken: bool             # did a recent-window candle break+close past it?


def _sr_extract_pivots(values: List[float], kind: str) -> List[tuple]:
    """1-bar fractal pivots: v[i] ≷ v[i-1] AND v[i] ≷ v[i+1]."""
    pivots: List[tuple] = []
    n = len(values)
    if n < 3:
        return pivots
    for i in range(1, n - 1):
        v = values[i]
        if kind == "high" and v > values[i - 1] and v > values[i + 1]:
            pivots.append((v, i))
        elif kind == "low" and v < values[i - 1] and v < values[i + 1]:
            pivots.append((v, i))
    return pivots


def _sr_cluster_pivots(
    pivots: List[tuple],
    atr: float,
    band_atr: float,
    min_touches: int,
) -> List[Dict[str, Any]]:
    """Greedy band-clustering; returns clusters with >= min_touches."""
    if atr <= 0 or len(pivots) < min_touches:
        return []
    band = atr * band_atr
    sorted_pivots = sorted(pivots, key=lambda x: x[0])

    clusters: List[List[tuple]] = []
    current: List[tuple] = [sorted_pivots[0]]
    cluster_min = sorted_pivots[0][0]
    for p in sorted_pivots[1:]:
        if p[0] - cluster_min <= band:
            current.append(p)
        else:
            clusters.append(current)
            current = [p]
            cluster_min = p[0]
    clusters.append(current)

    results: List[Dict[str, Any]] = []
    for cl in clusters:
        if len(cl) < min_touches:
            continue
        prices = [p[0] for p in cl]
        price_mean = sum(prices) / len(prices)
        width = max(prices) - min(prices)
        results.append({
            "price": price_mean,
            "touch_count": len(cl),
            "atr_normalized_width": width / atr if atr > 0 else 0.0,
        })
    return results


def _sr_was_broken_up(
    level: float, recent_highs: List[float], recent_closes: List[float],
    recent_opens: List[float], prev_closes: List[float],
) -> bool:
    """Mirrors the break-check used by _evaluate_sr_flip_retest."""
    for h, c, o, pc in zip(recent_highs, recent_closes, recent_opens, prev_closes):
        if h > level and c > level and (o <= level or pc <= level):
            return True
    return False


def _sr_was_broken_down(
    level: float, recent_lows: List[float], recent_closes: List[float],
    recent_opens: List[float], prev_closes: List[float],
) -> bool:
    for low_val, c, o, pc in zip(recent_lows, recent_closes, recent_opens, prev_closes):
        if low_val < level and c < level and (o >= level or pc >= level):
            return True
    return False


def _sr_quality_rank(quality: str) -> int:
    return {"CLUSTERED": 3, "VP_ANCHORED": 2, "SCALAR_FALLBACK": 1}.get(quality, 0)


def _sr_detect_levels(
    highs: List[float],
    lows: List[float],
    closes: List[float],
    opens: List[float],
    atr: float,
    volume_poc: Optional[float] = None,
    volume_vah: Optional[float] = None,
    volume_val: Optional[float] = None,
    min_touches: int = 2,
    cluster_band_atr: float = 0.3,
) -> Dict[str, Optional[_StructuralLevel]]:
    """Best broken-and-structural resistance/support for SR_FLIP retest.

    Windows match _evaluate_sr_flip_retest exactly:
      prior window:  [-50:-9]  (41 bars for pivot extraction)
      recent window: [-9:-2]   (7 closed candles for break search)
      prev_closes:   [-10:-3]  (for gap-up / gap-down confirmation)

    Returns {"resistance": _StructuralLevel|None, "support": _StructuralLevel|None}
    """
    if len(highs) < 55 or len(lows) < 55 or len(closes) < 55 or len(opens) < 1:
        return {"resistance": None, "support": None}

    prior_highs = [float(h) for h in highs[-50:-9]]
    prior_lows = [float(low_val) for low_val in lows[-50:-9]]
    recent_highs = [float(h) for h in highs[-9:-2]]
    recent_lows = [float(low_val) for low_val in lows[-9:-2]]
    recent_closes = [float(c) for c in closes[-9:-2]]
    recent_opens = [float(o) for o in opens[-9:-2]]
    recent_prev_closes = [float(c) for c in closes[-10:-3]]
    current_close = float(closes[-1])

    # Pivots + clustering
    high_pivots = _sr_extract_pivots(prior_highs, "high")
    low_pivots = _sr_extract_pivots(prior_lows, "low")
    high_clusters = _sr_cluster_pivots(high_pivots, atr, cluster_band_atr, min_touches)
    low_clusters = _sr_cluster_pivots(low_pivots, atr, cluster_band_atr, min_touches)

    resistance_cands: List[_StructuralLevel] = []
    support_cands: List[_StructuralLevel] = []

    for cl in high_clusters:
        resistance_cands.append(_StructuralLevel(
            price=cl["price"], side="RESISTANCE", quality="CLUSTERED",
            touch_count=cl["touch_count"],
            atr_normalized_width=cl["atr_normalized_width"],
            was_broken=False,
        ))
    for cl in low_clusters:
        support_cands.append(_StructuralLevel(
            price=cl["price"], side="SUPPORT", quality="CLUSTERED",
            touch_count=cl["touch_count"],
            atr_normalized_width=cl["atr_normalized_width"],
            was_broken=False,
        ))

    # VP anchoring (additive)
    if volume_vah is not None and float(volume_vah) > 0:
        resistance_cands.append(_StructuralLevel(
            price=float(volume_vah), side="RESISTANCE", quality="VP_ANCHORED",
            touch_count=1, atr_normalized_width=0.0, was_broken=False,
        ))
    if volume_val is not None and float(volume_val) > 0:
        support_cands.append(_StructuralLevel(
            price=float(volume_val), side="SUPPORT", quality="VP_ANCHORED",
            touch_count=1, atr_normalized_width=0.0, was_broken=False,
        ))
    if volume_poc is not None and float(volume_poc) > 0:
        poc = float(volume_poc)
        resistance_cands.append(_StructuralLevel(
            price=poc, side="RESISTANCE", quality="VP_ANCHORED",
            touch_count=1, atr_normalized_width=0.0, was_broken=False,
        ))
        support_cands.append(_StructuralLevel(
            price=poc, side="SUPPORT", quality="VP_ANCHORED",
            touch_count=1, atr_normalized_width=0.0, was_broken=False,
        ))

    # Scalar fallback — always emitted (guarantees non-empty output, preserving
    # legacy behaviour when no structural level exists).
    if prior_highs:
        resistance_cands.append(_StructuralLevel(
            price=max(prior_highs), side="RESISTANCE", quality="SCALAR_FALLBACK",
            touch_count=1, atr_normalized_width=0.0, was_broken=False,
        ))
    if prior_lows:
        support_cands.append(_StructuralLevel(
            price=min(prior_lows), side="SUPPORT", quality="SCALAR_FALLBACK",
            touch_count=1, atr_normalized_width=0.0, was_broken=False,
        ))

    # Filter degenerate prices (e.g. VP data from a pair with no volume)
    resistance_cands = [c for c in resistance_cands if c.price > 0]
    support_cands = [c for c in support_cands if c.price > 0]

    # Annotate with break detection
    resistance_with_break = [
        _StructuralLevel(
            price=c.price, side=c.side, quality=c.quality,
            touch_count=c.touch_count,
            atr_normalized_width=c.atr_normalized_width,
            was_broken=_sr_was_broken_up(
                c.price, recent_highs, recent_closes, recent_opens, recent_prev_closes,
            ),
        )
        for c in resistance_cands
    ]
    support_with_break = [
        _StructuralLevel(
            price=c.price, side=c.side, quality=c.quality,
            touch_count=c.touch_count,
            atr_normalized_width=c.atr_normalized_width,
            was_broken=_sr_was_broken_down(
                c.price, recent_lows, recent_closes, recent_opens, recent_prev_closes,
            ),
        )
        for c in support_cands
    ]

    # Rank: was_broken DESC, quality DESC, touches DESC, width ASC, proximity ASC
    resistance_with_break.sort(key=lambda lv: (
        -int(lv.was_broken),
        -_sr_quality_rank(lv.quality),
        -lv.touch_count,
        lv.atr_normalized_width,
        abs(lv.price - current_close),
    ))
    support_with_break.sort(key=lambda lv: (
        -int(lv.was_broken),
        -_sr_quality_rank(lv.quality),
        -lv.touch_count,
        lv.atr_normalized_width,
        abs(lv.price - current_close),
    ))

    return {
        "resistance": resistance_with_break[0] if resistance_with_break else None,
        "support": support_with_break[0] if support_with_break else None,
    }


# Generation-path tokens for the two mover continuation paths. Used to capture
# a per-symbol "why didn't this mover fire" reason for the ops Pairs page.
_MOVER_PATH_TOKENS: frozenset = frozenset({"MOVER_TREND_PULLBACK", "MOVER_AVWAP_SCALP"})
# Drop a symbol's captured mover reason once it's older than this — keeps the
# dict bounded to pairs the scanner has touched recently (a synthetic mover that
# expires out of the universe stops being evaluated and ages out).
_MOVER_REASON_TTL_SEC: float = 1800.0


class ScalpChannel(BaseChannel):
    def __init__(self) -> None:
        super().__init__(CHANNEL_SCALP)
        self._generation_telemetry: Dict[str, Dict[str, int]] = {
            "attempts": defaultdict(int),
            "no_signal": defaultdict(int),
            "no_signal_reason": defaultdict(int),
            "generated": defaultdict(int),
        }
        self._active_generation_path: Optional[str] = None
        self._active_no_signal_reason: Optional[str] = None
        # Per-symbol last outcome of the two mover paths (MOVER_TREND_PULLBACK,
        # MOVER_AVWAP_SCALP), keyed by symbol → {path_token: reason, "ts": mono}.
        # Surfaced on the ops Pairs page so a promoted mover that isn't firing
        # shows *why* this cycle (e.g. ``no_reclaim``, ``mover_run_too_small``)
        # instead of leaving us to infer it from cumulative truth-report counters.
        # Bounded to the live scan universe and pruned on write.
        self._mover_last_reason: Dict[str, Dict[str, Any]] = {}
        # PR-8: per-(symbol, direction) cooldown for MA_CROSS_TREND_SHIFT.
        # MA crossovers are infrequent — once per pair per direction every
        # ~24h is the realistic cadence.  Without a cooldown, EMA50/EMA200
        # straddling each other on a sideways 4h would emit a fresh signal
        # every cycle.
        #
        # Persisted to ``data/ma_cross_cooldown.json`` (chartist-eye seeding
        # fix, 2026-05-06).  Without persistence, every redeploy resets the
        # registry, so a recent MA_CROSS could double-fire if the engine
        # restarts within the 24h window.  Loaded on init; written on every
        # successful signal via ``_persist_ma_cross_cooldown``.
        self._ma_cross_last_fire_ts: Dict[tuple, float] = {}
        self._load_ma_cross_cooldown()
        # MEAN_REVERT liveness: monotonic count of shared-detection hits
        # (incremented pre-gate, so it moves whether live or shadowed).
        # Compared against the shadow unit's stamp rate by the liveness probe.
        self._mean_revert_detections: int = 0
        # RANGE_FADE liveness: same contract as _mean_revert_detections —
        # incremented pre-gate (moves whether live, shadowed, or
        # context-blocked downstream), compared against the shadow unit's
        # stamp rate by the range_fade_path liveness probe.
        self._range_fade_detections: int = 0

    def _reset_generation_telemetry(self) -> None:
        self._generation_telemetry = {
            "attempts": defaultdict(int),
            "no_signal": defaultdict(int),
            "no_signal_reason": defaultdict(int),
            "generated": defaultdict(int),
        }

    @staticmethod
    def _generation_path_token(evaluator_name: str) -> str:
        token = evaluator_name.replace("_evaluate_", "").upper()
        return token or "UNKNOWN"

    @staticmethod
    def _no_signal_reason_token(reason: str) -> str:
        token = str(reason or "none").strip().lower()
        token = token.replace("-", "_").replace(" ", "_")
        token = "".join(ch for ch in token if ch.isalnum() or ch == "_")
        return token or "none"

    def _reject(self, reason: str) -> Optional[Signal]:
        self._active_no_signal_reason = self._no_signal_reason_token(reason)
        return None

    @staticmethod
    def _mover_path_live(tunable_key: str, boot_default: bool) -> bool:
        """Live/shadow switch for a mover path, read from the ops-controlled
        runtime tunables (2026-07-09).  The env flags
        (MOVER_TREND_PULLBACK_ENABLED / MOVER_AVWAP_SCALP_ENABLED) required a
        VPS .env edit + redeploy to flip a path into shadow; per the #702
        owner directive every such knob lives on the ops panel.  The tunable's
        default IS the env flag, so behaviour is unchanged until the owner
        flips it.  Read via the 5s-cached whole-doc accessor — no per-scan
        Firestore reads (Cost Discipline).
        """
        try:
            from src import runtime_tunables as _rt
            return bool(_rt.get(tunable_key))
        except Exception as exc:
            # A typo'd/unregistered tunable key raises KeyError and would
            # silently pin the path to its boot default forever — count it.
            fail_open.record("scalp.path_live_tunable", exc)
            return boot_default

    def _prune_mover_reasons(self, now: float) -> None:
        """Drop stale per-symbol mover-reason entries (cheap, bounded)."""
        if len(self._mover_last_reason) > 256:
            stale = [
                s for s, r in self._mover_last_reason.items()
                if now - float(r.get("ts", 0.0)) > _MOVER_REASON_TTL_SEC
            ]
            for s in stale:
                self._mover_last_reason.pop(s, None)

    def _record_mover_reason(self, symbol: str, path: str, reason: str) -> None:
        """Capture this cycle's outcome for one mover path on *symbol*.

        Records the reason an evaluator (MOVER_TREND_PULLBACK / MOVER_AVWAP_SCALP)
        gave — ``fired`` or a reject token. Marks this cycle as ``eval`` so the
        summary prefers it over any earlier scanner-side skip. Read back by
        :meth:`mover_last_reasons` for the ops Pairs page.
        """
        now = time.monotonic()
        rec = self._mover_last_reason.get(symbol)
        if rec is None:
            rec = {}
            self._mover_last_reason[symbol] = rec
        rec[path] = reason
        rec["ts"] = now
        rec["last_kind"] = "eval"
        self._prune_mover_reasons(now)

    def note_mover_skip(self, symbol: str, reason: str) -> None:
        """Record a scanner-side pre-evaluation skip for a promoted mover.

        A mover dropped before :meth:`evaluate` runs (spread gate, rollout
        exclusion, channel skip) never reaches :meth:`_record_mover_reason`, so
        without this the ops Pairs page would show a blank ``—`` and hide the
        real wall. Marks the cycle as ``skip`` so the summary surfaces this
        reason when it's the latest outcome.
        """
        now = time.monotonic()
        rec = self._mover_last_reason.get(symbol)
        if rec is None:
            rec = {}
            self._mover_last_reason[symbol] = rec
        rec["scan_skip"] = self._no_signal_reason_token(reason)
        rec["ts"] = now
        rec["last_kind"] = "skip"
        self._prune_mover_reasons(now)

    def mover_last_reasons(self) -> Dict[str, Dict[str, Any]]:
        """Per-symbol last mover outcome for the ops Pairs page.

        Returns ``{symbol: {"reason": str, "path": str, "age_sec": float}}``.
        When the latest cycle was a scanner-side skip (spread gate / rollout),
        the skip reason wins — the pair was never evaluated. Otherwise ``reason``
        is ``fired`` if either mover path produced a signal, else the
        MOVER_TREND_PULLBACK reject (primary path), falling back to AVWAP.
        Entries older than the TTL are dropped.
        """
        now = time.monotonic()
        out: Dict[str, Dict[str, Any]] = {}
        for sym, rec in self._mover_last_reason.items():
            ts = float(rec.get("ts", 0.0))
            if now - ts > _MOVER_REASON_TTL_SEC:
                continue
            if rec.get("last_kind") == "skip":
                reason = rec.get("scan_skip")
                if reason is None:
                    continue
                path = "SCAN_SKIP"
            else:
                mtp = rec.get("MOVER_TREND_PULLBACK")
                avwap = rec.get("MOVER_AVWAP_SCALP")
                if mtp == "fired" or avwap == "fired":
                    reason, path = "fired", (
                        "MOVER_TREND_PULLBACK" if mtp == "fired" else "MOVER_AVWAP_SCALP"
                    )
                elif mtp is not None:
                    reason, path = mtp, "MOVER_TREND_PULLBACK"
                elif avwap is not None:
                    reason, path = avwap, "MOVER_AVWAP_SCALP"
                else:
                    continue
            out[sym] = {"reason": reason, "path": path, "age_sec": round(now - ts, 1)}
        return out

    # ------------------------------------------------------------------
    # MA-cross cooldown persistence (chartist-eye seeding fix, 2026-05-06)
    # ------------------------------------------------------------------
    #
    # ``_ma_cross_last_fire_ts`` is in-memory.  Without a disk-backed
    # mirror, every GitHub-Actions redeploy resets the cooldown registry
    # — so a recent MA_CROSS_TREND_SHIFT signal can double-fire if the
    # engine restarts within the 24h window.  Persistence makes the
    # cooldown survive restarts.

    _MA_CROSS_COOLDOWN_PATH = "data/ma_cross_cooldown.json"

    def _load_ma_cross_cooldown(self) -> None:
        """Load the cooldown registry from disk on init.  Best-effort."""
        import json
        from pathlib import Path
        path = Path(self._MA_CROSS_COOLDOWN_PATH)
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
            try:
                symbol, direction = key.split("|", 1)
                self._ma_cross_last_fire_ts[(symbol, direction)] = float(ts)
            except (ValueError, TypeError):
                continue

    def _persist_ma_cross_cooldown(self) -> None:
        """Atomically write the cooldown registry to disk."""
        import json
        from pathlib import Path
        path = Path(self._MA_CROSS_COOLDOWN_PATH)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            payload = {
                f"{symbol}|{direction}": ts
                for (symbol, direction), ts in self._ma_cross_last_fire_ts.items()
            }
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload), encoding="utf-8")
            tmp.replace(path)
        except OSError as exc:
            # Don't crash the engine over a persistence write failure.
            from src.utils import get_logger
            get_logger("scalp").debug(
                "MA-cross cooldown persist failed: %s", exc,
            )

    @staticmethod
    def _dependency_state(smc_data: dict, name: str) -> str:
        state_map = smc_data.get("__dependency_source_state")
        if isinstance(state_map, dict):
            state = str(state_map.get(name) or "").strip().lower()
            if state in {"unavailable", "empty", "populated"}:
                return state
        return "unknown"

    @staticmethod
    def _classify_htf_trend(
        indicators: Dict[str, dict],
        candles: Dict[str, dict],
        tf_label: str,
    ) -> Optional[str]:
        """Return 'BULLISH' / 'BEARISH' / 'NEUTRAL' / None for the given timeframe.

        Mirrors the contract used by `src.mtf._classify_trend`: a TF is BULLISH
        when ema_fast > ema_slow AND close > ema_fast (and BEARISH when both
        inverted).  Returns None when indicator/candle data for the TF is
        unavailable so the caller can choose how to handle missing data.
        """
        ind_tf = indicators.get(tf_label, {})
        ema_fast = ind_tf.get("ema9_last")
        ema_slow = ind_tf.get("ema21_last")
        cd = candles.get(tf_label, {})
        closes = cd.get("close", [])
        if ema_fast is None or ema_slow is None or len(closes) == 0:
            return None
        try:
            ema_fast_f = float(ema_fast)
            ema_slow_f = float(ema_slow)
            close_f = float(closes[-1])
        except (TypeError, ValueError):
            return None
        if ema_fast_f > ema_slow_f and close_f > ema_fast_f:
            return "BULLISH"
        if ema_fast_f < ema_slow_f and close_f < ema_fast_f:
            return "BEARISH"
        return "NEUTRAL"

    def consume_generation_telemetry(self) -> Dict[str, Dict[str, int]]:
        snapshot = {
            stage: dict(counts)
            for stage, counts in self._generation_telemetry.items()
        }
        self._reset_generation_telemetry()
        return snapshot

    def _pass_basic_filters(
        self,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
        profile=None,
    ) -> bool:
        """Return True if basic spread/volume filters pass (regime-adaptive, pair-aware)."""
        thresholds = self._get_pair_adjusted_thresholds(profile)
        vol_min = thresholds["min_volume"]
        spread_max = thresholds["spread_max"]

        # Wire PairProfile.liquidity_tier for volume gate (item 17)
        if profile is not None:
            _tier = getattr(profile, "liquidity_tier", 2)
            if _tier == 1:
                vol_min *= 1.5  # Tier 1 needs higher volume confirmation
            elif _tier == 3:
                vol_min *= 0.8  # Smaller pairs, lower absolute volume
            # Wire PairProfile.avg_spread_bps for spread gate (item 17)
            _avg_bps = getattr(profile, "avg_spread_bps", 3.0)
            if _avg_bps > 5:
                spread_max *= 0.85  # Historically wide-spread pair: extra margin needed

        return (
            check_spread_adaptive(spread_pct, spread_max, regime=regime)
            and check_volume(volume_24h_usd, vol_min)
        )

    def _select_indicator_weights(self, regime: str) -> dict:
        """Return indicator weight multipliers for the current regime.

        The weights are applied as a confidence boost multiplier to each
        candidate signal so that regime-appropriate setups are preferred
        when multiple candidates are available.

        Parameters
        ----------
        regime:
            Current market regime string (e.g. ``"VOLATILE"``, ``"QUIET"``).

        Returns
        -------
        dict
            Keys: ``"order_flow"``, ``"trend"``, ``"mean_reversion"``,
            ``"volume"``.  Values are float multipliers (>1 boosts,
            <1 suppresses).
        """
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "VOLATILE":
            # Order flow signals more reliable in volatile markets
            return {"order_flow": 1.5, "trend": 0.7, "mean_reversion": 0.8, "volume": 1.3}
        if regime_upper in ("QUIET", "RANGING"):
            # Mean-reversion setups are preferred in ranging markets while trend
            # signals have lower edge.
            return {"order_flow": 0.8, "trend": 0.75, "mean_reversion": 1.2, "volume": 0.9}
        if regime_upper in ("TRENDING_UP", "TRENDING_DOWN"):
            # Trend-following signals preferred in trending markets
            return {"order_flow": 1.0, "trend": 1.5, "mean_reversion": 0.7, "volume": 1.0}
        return {"order_flow": 1.0, "trend": 1.0, "mean_reversion": 1.0, "volume": 1.0}

    def evaluate(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
        allowed_evaluators: Optional[frozenset] = None,
    ) -> List[Signal]:
        # Evaluate all signal paths and return every valid candidate so that the
        # scanner can process each one independently through the gate chain.
        # Previously only the winner-takes-all best signal was returned, which
        # silently discarded all other valid setups.
        #
        # allowed_evaluators: when provided (not None), only run evaluators whose
        # name is in this frozenset. Used by movers-promotion scan to restrict
        # mover-promoted pairs to VSB + BREAKDOWN_SHORT only.
        profile = smc_data.get("pair_profile") if smc_data else None
        self._reset_generation_telemetry()
        results: List[Signal] = []
        for evaluator_name, evaluator in (
            ("_evaluate_standard", self._evaluate_standard),
            ("_evaluate_trend_pullback", self._evaluate_trend_pullback),
            ("_evaluate_liquidation_reversal", self._evaluate_liquidation_reversal),
            ("_evaluate_whale_momentum", self._evaluate_whale_momentum),
            ("_evaluate_volume_surge_breakout", self._evaluate_volume_surge_breakout),
            ("_evaluate_breakdown_short", self._evaluate_breakdown_short),
            ("_evaluate_mover_trend_pullback", self._evaluate_mover_trend_pullback),
            ("_evaluate_mover_avwap_scalp", self._evaluate_mover_avwap_scalp),
            ("_evaluate_opening_range_breakout", self._evaluate_opening_range_breakout),
            ("_evaluate_sr_flip_retest", self._evaluate_sr_flip_retest),
            ("_evaluate_funding_extreme", self._evaluate_funding_extreme),
            ("_evaluate_quiet_compression_break", self._evaluate_quiet_compression_break),
            ("_evaluate_divergence_continuation", self._evaluate_divergence_continuation),
            ("_evaluate_continuation_liquidity_sweep", self._evaluate_continuation_liquidity_sweep),
            ("_evaluate_post_displacement_continuation", self._evaluate_post_displacement_continuation),
            ("_evaluate_failed_auction_reclaim", self._evaluate_failed_auction_reclaim),
            ("_evaluate_ma_cross_trend_shift", self._evaluate_ma_cross_trend_shift),
            ("_evaluate_mean_revert", self._evaluate_mean_revert),
            ("_evaluate_range_fade", self._evaluate_range_fade),
        ):
            if allowed_evaluators is not None and evaluator_name not in allowed_evaluators:
                continue  # restricted scan context — skip evaluators not in allowlist
            _path = self._generation_path_token(evaluator_name)
            self._generation_telemetry["attempts"][_path] += 1
            self._active_generation_path = _path
            self._active_no_signal_reason = None
            try:
                try:
                    sig = evaluator(symbol, candles, indicators, smc_data, spread_pct, volume_24h_usd, regime)
                except Exception as exc:
                    self._generation_telemetry["no_signal"][_path] += 1
                    self._generation_telemetry["no_signal_reason"][f"{_path}:exception"] += 1
                    log.error(
                        "ScalpChannel evaluator {} raised for {}: {}\n{}",
                        _path,
                        symbol,
                        exc,
                        traceback.format_exc(),
                    )
                    continue
                if sig is not None:
                    self._generation_telemetry["generated"][_path] += 1
                    if _path in _MOVER_PATH_TOKENS:
                        self._record_mover_reason(symbol, _path, "fired")
                    # Apply kill zone check and mark reduced-conviction signals
                    sig_with_kz = self._apply_kill_zone_note(sig, profile=profile)
                    results.append(sig_with_kz)
                else:
                    self._generation_telemetry["no_signal"][_path] += 1
                    _reason = self._active_no_signal_reason or "none"
                    self._generation_telemetry["no_signal_reason"][f"{_path}:{_reason}"] += 1
                    if _path in _MOVER_PATH_TOKENS:
                        self._record_mover_reason(symbol, _path, _reason)
            finally:
                self._active_generation_path = None
                self._active_no_signal_reason = None
        return results

    # ------------------------------------------------------------------
    # Standard scalp path (TREND_PULLBACK / BREAKOUT / LIQUIDITY_SWEEP)
    # ------------------------------------------------------------------

    def _evaluate_standard(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 50:
            return self._reject("insufficient_candles")

        ind = indicators.get("5m", {})
        profile = smc_data.get("pair_profile")
        thresholds = self._get_pair_adjusted_thresholds(profile)
        # Regime-adaptive ADX minimum: in RANGING/QUIET markets ADX hovers at
        # 15-20 and consistently blocks the standard scalp path.  Lower the
        # floor so well-formed liquidity-sweep setups can still compete.
        adx_min_effective = thresholds["adx_min"]
        if regime and regime.upper() in ("RANGING", "QUIET"):
            adx_min_effective = max(_ADX_RANGING_FLOOR, thresholds["adx_min"] * _ADX_RANGING_MULTIPLIER)
        if not check_adx(ind.get("adx_last"), adx_min_effective):
            return self._reject("adx_reject")
        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime, profile=profile):
            return self._reject("basic_filters_failed")

        ema_fast = ind.get("ema9_last")
        ema_slow = ind.get("ema21_last")
        if ema_fast is None or ema_slow is None:
            return self._reject("ema_alignment_reject")

        sweeps = smc_data.get("sweeps", [])
        if not sweeps:
            return self._reject("sweeps_not_detected")
        sweep = sweeps[0]

        close = float(m5["close"][-1])
        atr_val = ind.get("atr_last", close * 0.002)

        mom = ind.get("momentum_last")
        if mom is None:
            return self._reject("momentum_reject")
        # ATR-adaptive momentum threshold: scales with each pair's volatility
        # BTC (ATR ~0.3%) → threshold ~0.15%, DOGE (ATR ~0.8%) → threshold ~0.30%
        atr_pct = (atr_val / close) * 100.0 if close > 0 else 0.15
        profile = smc_data.get("pair_profile")
        base_momentum = max(0.10, min(0.30, atr_pct * 0.5))
        if profile is not None:
            base_momentum *= profile.momentum_threshold_mult
        momentum_threshold = base_momentum
        if abs(mom) < momentum_threshold:
            return self._reject("momentum_reject")

        # Momentum persistence: require momentum above threshold for consecutive
        # candles to avoid whipsaws where a single candle briefly spikes momentum.
        # In QUIET/RANGING, the sweep itself is the trigger — reduce to 1 candle.
        mom_arr = ind.get("momentum_array")
        persist = profile.momentum_persist_candles if profile else 2
        if regime and regime.upper() in ("QUIET", "RANGING"):
            persist = min(persist, 1)
        if mom_arr is not None and len(mom_arr) >= persist:
            if not all(abs(float(mom_arr[-i])) >= momentum_threshold for i in range(1, persist + 1)):
                return self._reject("momentum_reject")  # Momentum not persistent — likely whipsaw

        direction = sweep.direction

        # MSS (Market Structure Shift) confirmation — SMC doctrine pairs every
        # sweep with a lower-TF MSS to confirm the reversal has structurally
        # taken hold.  `detect_mss` is computed upstream by SMCDetector and
        # reaches us via `smc_data["mss"]`.  Three cases:
        #   - present + direction matches sweep  → canonical pattern, no penalty
        #   - present + direction mismatches     → hard reject (LTF moved
        #                                          against the sweep — the
        #                                          reversal already failed)
        #   - missing                            → soft penalty (sweep alone
        #                                          is still tradeable, but
        #                                          lower confidence)
        mss_obj = smc_data.get("mss")
        mss_adj = 0.0
        mss_reason = ""
        if mss_obj is not None:
            _mss_dir = getattr(mss_obj, "direction", None)
            if _mss_dir is not None and _mss_dir != direction:
                return self._reject("mss_direction_mismatch")
        else:
            mss_adj = -8.0
            mss_reason = "MSS_MISSING"

        # RSI extreme gate: use pair-specific OB/OS levels when available
        rsi_val = ind.get("rsi_last")
        if rsi_val is not None and profile is not None:
            from src.filters import check_rsi
            if not check_rsi(rsi_val, thresholds["rsi_ob"], thresholds["rsi_os"], direction.value):
                return self._reject("rsi_reject")
        elif not check_rsi_regime(rsi_val, direction=direction.value, regime=regime):
            return self._reject("rsi_reject")

        # NOTE: a 5m 3-candle momentum-sign check used to live here.  It was
        # structurally inverted: by definition, the 2-3 candles BEFORE a sweep
        # drift in the direction OPPOSITE to the reversal we want, so demanding
        # the post-sweep mom sign already match `direction` rejects the very
        # setups LSR is meant to fire on.  Magnitude (line ~799) and persistence
        # (line ~809) checks are retained — both are sign-agnostic.  The MSS
        # gate above is the structurally truthful direction confirmation.

        pair_tier = profile.tier if profile else "MIDCAP"
        if not check_ema_alignment_adaptive(
            ema_fast, ema_slow, direction.value,
            atr_val=atr_val, close=close,
            regime=regime, pair_tier=pair_tier,
        ):
            return self._reject("ema_alignment_reject")

        # MACD confirmation gate (PR_04)
        ind_macd_last = ind.get("macd_histogram_last")
        ind_macd_prev = ind.get("macd_histogram_prev")
        strict_macd = regime.upper() in ("RANGING", "QUIET") if regime else False
        macd_ok, macd_adj = check_macd_confirmation(
            ind_macd_last, ind_macd_prev, direction.value, regime=regime, strict=strict_macd
        )
        if not macd_ok:
            return self._reject("macd_reject")  # Hard reject in strict mode

        # MTF gate — 1h EMA/RSI must support the 5m signal direction (PR_06)
        indicators_1h = indicators.get("1h", {})
        mtf_ok, mtf_reason, mtf_adj = mtf_gate_scalp_standard(indicators_1h, direction.value, regime)
        if not mtf_ok:
            return self._reject("mtf_reject")

        # HTF POI anchor (OWNER_BRIEF §3.4a — "HTF Structure, LTF Entry").
        #
        # The 2026-05-17 audit on 654 closed signals found LSR was the only
        # path with passable direction-call quality (24% MFE=0 vs 39-78% on
        # other paths) but still net-negative at -1.13% NET/sig.  Root cause:
        # SMCDetector finds sweeps wherever it can — 5m local lows, micro
        # supports, intra-range noise — not just sweeps of structurally
        # significant HTF levels.  Many of the LSR signals were "real
        # sweeps of nothing-levels."
        #
        # Fix: anchor the sweep to a multi-TF LevelBook entry.  Quality
        # criteria mirror the §3.5 chartist-eye stack: a level qualifies
        # if it's CLUSTERED (>=2 source TFs converged on the same band) or
        # VP_ANCHORED (POC / VAH / VAL from the volume-profile feed).
        # Single-TF round-number-only levels do NOT qualify — they're
        # psychological noise without institutional defence.
        #
        # Distance criterion: ATR * 2.  Wider than chartist-eye confluence
        # query (CONFLUENCE_TOLERANCE_PCT ≈ 0.3%) because a sweep candle
        # can wick 1-2 ATR past the level before reclaiming.
        _sweep = sweeps[0] if sweeps else None
        _sweep_level = None
        if _sweep is not None:
            # Try multiple attribute names used by different SMC implementations
            _sweep_level = getattr(_sweep, "level", None) or getattr(_sweep, "price", None) or getattr(_sweep, "sweep_level", None)
        if _sweep_level is not None and float(_sweep_level) > 0:
            _sweep_level_f = float(_sweep_level)
            # Sentinel distinction: ``None`` / key-absent means "LevelBook has
            # not been refreshed for this scan cycle" — happens in unit tests
            # that build a synthetic ``smc_data`` without the scanner's
            # assembly pass.  Empty list means "refreshed, but no levels
            # found for this symbol" — that IS a hard-block per §3.4a.  The
            # production path in ``Scanner._build_scan_context`` always sets
            # this key (to at least ``[]``) when the refresh succeeds, so
            # this fail-open branch only triggers in test or pre-warm-up
            # scenarios where the LevelBook is genuinely uninitialised.
            _lb_levels_raw = smc_data.get("level_book_levels")
            if _lb_levels_raw is not None:
                _anchor_band = atr_val * _LSR_POI_ANCHOR_ATR_MULT
                _anchored = False
                for _lv in _lb_levels_raw:
                    # Quality gate — CLUSTERED (multi-TF cluster, len(source_tfs) >= 2)
                    # or VP_ANCHORED (volume-profile-sourced).  Skip everything else
                    # (single-TF pivots, round numbers in isolation).
                    _src_tfs = getattr(_lv, "source_tfs", None) or [getattr(_lv, "source_tf", "")]
                    _is_clustered = isinstance(_src_tfs, list) and len(_src_tfs) >= 2
                    _is_vp_anchored = getattr(_lv, "source_tf", "") == "vp" or "vp" in (_src_tfs or [])
                    if not (_is_clustered or _is_vp_anchored):
                        continue
                    _lv_price = float(getattr(_lv, "price", 0.0) or 0.0)
                    if _lv_price <= 0:
                        continue
                    if abs(_lv_price - _sweep_level_f) <= _anchor_band:
                        _anchored = True
                        break
                if not _anchored:
                    # Doctrine-correct rejection: the sweep wasn't anchored to a
                    # structurally significant HTF level.  This is the LSR path's
                    # primary quality filter; pre-2026-05-17 it didn't exist and
                    # the path fired on any detected sweep.
                    return self._reject("htf_poi_unanchored")
        if _sweep_level is not None and float(_sweep_level) > 0:
            _sweep_level = float(_sweep_level)
            if direction == Direction.LONG:
                sl = _sweep_level * (1 - 0.001)  # SL just below swept level
            else:
                sl = _sweep_level * (1 + 0.001)  # SL just above swept level
            sl_dist = abs(close - sl)
            # Ensure minimum SL distance (at least 0.5×ATR)
            if sl_dist < atr_val * 0.5:
                sl_dist = atr_val * 0.5
                sl = close - sl_dist if direction == Direction.LONG else close + sl_dist
        else:
            # ATR-based fallback
            sl_dist = max(close * self.config.sl_pct_range[0] / 100, atr_val * 0.5)
            # Wire PairProfile.volatility_class for SL sizing (item 17)
            if profile is not None:
                _vol_class = getattr(profile, "volatility_class", "medium")
                if _vol_class == "high":
                    sl_dist *= 1.3  # Wider SL for volatile pairs
            sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # Structure-based TP: FVG above/below entry for TP1, swing high/low for TP2
        m5_highs = m5.get("high", [])
        m5_lows = m5.get("low", [])
        tp1 = 0.0
        tp2 = 0.0
        tp3 = 0.0

        # TP1: nearest FVG in signal direction
        fvgs = smc_data.get("fvg", [])
        for fvg_zone in fvgs:
            fvg_mid = None
            if hasattr(fvg_zone, "gap_high") and hasattr(fvg_zone, "gap_low"):
                fvg_mid = (float(fvg_zone.gap_high) + float(fvg_zone.gap_low)) / 2.0
            elif isinstance(fvg_zone, dict):
                _gh = fvg_zone.get("gap_high", 0)
                _gl = fvg_zone.get("gap_low", 0)
                if _gh and _gl:
                    fvg_mid = (float(_gh) + float(_gl)) / 2.0
            if fvg_mid is not None:
                if direction == Direction.LONG and fvg_mid > close:
                    tp1 = fvg_mid
                    break
                elif direction == Direction.SHORT and fvg_mid < close:
                    tp1 = fvg_mid
                    break

        # TP2: 20-candle swing high (LONG) / swing low (SHORT)
        if direction == Direction.LONG and len(m5_highs) >= 21:
            tp2 = max(float(h) for h in m5_highs[-21:-1])
            if tp2 <= close:
                tp2 = 0.0
        elif direction == Direction.SHORT and len(m5_lows) >= 21:
            tp2 = min(float(l) for l in m5_lows[-21:-1])
            if tp2 >= close:
                tp2 = 0.0

        # Fall back to ATR-ratio approach for any missing TP levels
        if tp1 <= 0 or (direction == Direction.LONG and tp1 <= close) or (direction == Direction.SHORT and tp1 >= close):
            tp1 = close + sl_dist * 1.5 if direction == Direction.LONG else close - sl_dist * 1.5
        if tp2 <= 0:
            tp2 = close + sl_dist * 2.5 if direction == Direction.LONG else close - sl_dist * 2.5
        tp3 = close + sl_dist * 4.0 if direction == Direction.LONG else close - sl_dist * 4.0
        # Q4-B: enforce ladder monotonicity post-fallback.  Prior code's
        # `tp2 <= tp1: tp2 = close ± sl_dist*2.5` could leave tp2 ≤ tp1 when
        # tp1 came from an FVG sitting > 2.5R past close.
        tp1, tp2, tp3 = _enforce_tp_ladder_monotonicity(
            tp1, tp2, tp3, close, sl_dist, direction,
            tp2_rmult_floor=2.5, tp3_rmult_floor=4.0,
        )

        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="SCALP",
            atr_val=atr_val,
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # Override with structure-based SL and TP targets
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Apply MACD soft penalty if applicable
        if macd_adj != 0.0:
            sig.confidence += macd_adj
            if sig.soft_gate_flags:
                sig.soft_gate_flags += ",MACD_WEAK"
            else:
                sig.soft_gate_flags = "MACD_WEAK"

        # Apply MTF soft penalty if applicable
        if mtf_adj != 0.0:
            sig.confidence += mtf_adj
            sig.soft_gate_flags = (sig.soft_gate_flags + f",MTF:{mtf_reason}").lstrip(",")

        # Apply MSS soft penalty when LTF confirmation is missing
        if mss_adj != 0.0:
            sig.confidence += mss_adj
            sig.soft_gate_flags = (sig.soft_gate_flags + f",{mss_reason}").lstrip(",")

        return sig

    # ------------------------------------------------------------------
    # TREND_PULLBACK path
    # EMA pullback in trend direction — fires in TRENDING regimes only.
    # ------------------------------------------------------------------

    def _evaluate_trend_pullback(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """TREND_PULLBACK_EMA: pullback to EMA in trend direction.

        Detection on 1H trend (OWNER_BRIEF §3.4a row 2 — "Detect on 1H
        EMA21/50 slope + structure state; Confirm on 1H pullback to
        EMA21 within ATR; Enter on 5m EMA9 reclaim + momentum candle").

        Pre-2026-05-17 TPE gated on 5m regime label + 5m EMA9/EMA21/EMA50
        alignment.  Truth-report data: 36 signals, 78% MFE=0 — the worst
        direction-call quality in the portfolio.  Root cause: a 5m
        "TRENDING_UP regime" is often noise inside a 1H/4h ranging
        market — circular reasoning (confirming "trend exists" on the
        same timeframe we're entering on).  EMAs are also lagging; by
        the time 5m EMA9 > 21 > 50 aligns and price returns to EMA21,
        the move is exhausted.

        Post-2026-05-17 doctrine: source the trend identification from
        1H EMA21/50 alignment + slope, and require a recent 1H bar to
        have approached 1H EMA21 (the pullback structure).  5m entry
        gates remain unchanged — they ARE the LTF timing.

        HTF path activates when ``indicators["1h"]`` carries ema21/ema50
        (production scanner populates).  Fallback to legacy 5m-regime
        path preserves existing test fixtures that don't seed 1H data.
        """
        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 50:
            return self._reject("insufficient_candles")

        # ── HTF trend identification (production path) ────────────────────
        # 1H EMA21 / EMA50 alignment + slope + recent-pullback check.
        # When 1H indicators are unavailable (test/pre-warm), fall back
        # to the legacy 5m regime gate so existing TPE test fixtures
        # continue to exercise the path.
        ind_1h = indicators.get("1h", {})
        ema21_1h = ind_1h.get("ema21_last")
        ema50_1h = ind_1h.get("ema50_last")
        ema21_1h_prev = ind_1h.get("ema21_prev")
        _uses_1h_trend = (
            ema21_1h is not None
            and ema50_1h is not None
        )

        direction: Optional[Direction] = None
        if _uses_1h_trend:
            # 1H alignment + slope tells us direction and that we're in a
            # genuine multi-hour trend, not a 5m wiggle.
            ema21_1h_f = float(ema21_1h)
            ema50_1h_f = float(ema50_1h)
            # Slope: when ema21_prev is unavailable (warmup), accept the
            # alignment-only signal — soft-penalty doctrine on missing data.
            slope_pos = (
                ema21_1h_prev is None
                or float(ema21_1h_prev) < ema21_1h_f
            )
            slope_neg = (
                ema21_1h_prev is None
                or float(ema21_1h_prev) > ema21_1h_f
            )
            if ema21_1h_f > ema50_1h_f and slope_pos:
                direction = Direction.LONG
            elif ema21_1h_f < ema50_1h_f and slope_neg:
                direction = Direction.SHORT
            else:
                return self._reject("h1_trend_not_aligned")

            # 1H pullback confirmation — at least one of the last few
            # closed 1H bars must have approached EMA21 (the pullback
            # structure that TPE is named for).  Threshold: low (LONG) /
            # high (SHORT) within ATR_1h × ``_TPE_H1_PULLBACK_ATR_MULT``
            # of EMA21.  When 1H ATR or candle history is unavailable,
            # skip this check (fail-open per soft-penalty doctrine —
            # never block on missing data).
            atr_1h = ind_1h.get("atr_last")
            cd_1h = candles.get("1h") or {}
            h1_highs = cd_1h.get("high") or []
            h1_lows = cd_1h.get("low") or []
            if atr_1h is not None and len(h1_highs) >= 2 and len(h1_lows) >= 2:
                _pullback_band = float(atr_1h) * _TPE_H1_PULLBACK_ATR_MULT
                # Look at last 4 CLOSED 1H bars (exclude index -1 which is
                # the still-forming current bar).  Window matches the ~4-hour
                # window during which a pullback would typically resolve.
                _h1_lookback = min(len(h1_highs) - 1, 4)
                if direction == Direction.LONG:
                    _h1_recent_lows = [
                        float(low_v) for low_v in h1_lows[-1 - _h1_lookback:-1]
                    ]
                    _pulled_back = any(
                        abs(low_v - ema21_1h_f) <= _pullback_band
                        for low_v in _h1_recent_lows
                    )
                else:
                    _h1_recent_highs = [
                        float(h) for h in h1_highs[-1 - _h1_lookback:-1]
                    ]
                    _pulled_back = any(
                        abs(h - ema21_1h_f) <= _pullback_band
                        for h in _h1_recent_highs
                    )
                if not _pulled_back:
                    return self._reject("h1_pullback_not_confirmed")
        else:
            # Legacy 5m-regime fallback path (test / pre-warm).  Allowed
            # regimes match pre-2026-05-17: TRENDING_UP/DOWN (direction
            # from label) and WEAK_TREND (direction from 5m EMA alignment).
            regime_upper = regime.upper() if regime else ""
            if regime_upper == "TRENDING_UP":
                direction = Direction.LONG
            elif regime_upper == "TRENDING_DOWN":
                direction = Direction.SHORT
            elif regime_upper == "WEAK_TREND":
                ind_for_dir = indicators.get("5m", {})
                ema9_for_dir = ind_for_dir.get("ema9_last")
                ema21_for_dir = ind_for_dir.get("ema21_last")
                if ema9_for_dir is None or ema21_for_dir is None:
                    return self._reject("ema_alignment_reject")
                if ema9_for_dir > ema21_for_dir:
                    direction = Direction.LONG
                elif ema9_for_dir < ema21_for_dir:
                    direction = Direction.SHORT
                else:
                    return self._reject("ema_alignment_reject")
            else:
                return self._reject("regime_blocked")

        ind = indicators.get("5m", {})
        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        ema50 = ind.get("ema50_last")
        rsi_val = ind.get("rsi_last")

        if ema9 is None or ema21 is None:
            return self._reject("ema_alignment_reject")

        close = float(m5["close"][-1])
        closes = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        opens = m5.get("open", [])
        if len(opens) < 1 or len(closes) < 3 or len(highs) < 2 or len(lows) < 2:
            return self._reject("insufficient_candles")
        last_open = float(opens[-1])
        prev_close = float(closes[-2])
        prev_high = float(highs[-2])
        prev_low = float(lows[-2])
        last_low = float(lows[-1])
        last_high = float(highs[-1])

        # 5m EMA alignment check.  Pre-2026-05-17 this required
        # EMA9 > EMA21 > EMA50 (LONG) — but the 5m EMA50 ordering is
        # redundant once 1H trend is the source of truth (HTF path).
        # On the legacy fallback path the EMA50 check stays in place
        # to preserve the existing pre-2026-05-17 selectivity.
        if _uses_1h_trend:
            # HTF path: only require EMA9 vs EMA21 ordering on 5m.  The
            # 5m EMA50 ordering would add nothing the 1H trend filter
            # hasn't already enforced at HTF — and would routinely
            # reject valid pullbacks during the lower-low / higher-high
            # phase of a healthy 1H trend.
            if direction == Direction.LONG and not (ema9 > ema21):
                return self._reject("ema_alignment_reject")
            if direction == Direction.SHORT and not (ema9 < ema21):
                return self._reject("ema_alignment_reject")
        else:
            if direction == Direction.LONG:
                if ema50 is not None and not (ema9 > ema21 > ema50):
                    return self._reject("ema_alignment_reject")
                elif ema50 is None and not (ema9 > ema21):
                    return self._reject("ema_alignment_reject")
            else:
                if ema50 is not None and not (ema9 < ema21 < ema50):
                    return self._reject("ema_alignment_reject")
                elif ema50 is None and not (ema9 < ema21):
                    return self._reject("ema_alignment_reject")

        # BUG FIX 7: Require CONFIRMED bounce, not just proximity.
        # Old: fired when price TOUCHED EMA (82.6% SL rate — entering on liquidity hunt)
        # New: require prev candle tested EMA + current candle CLOSES above EMA21
        if direction == Direction.LONG:
            if not (prev_low <= ema21 * 1.003):
                return self._reject("ema_not_tested_prev")
            if close <= ema21 or close <= ema9:
                return self._reject("no_ema_reclaim_close")
        else:
            if not (prev_high >= ema21 * 0.997):
                return self._reject("ema_not_tested_prev")
            if close >= ema21 or close >= ema9:
                return self._reject("no_ema_reclaim_close")
        # Close-position-in-range: the canonical TPE entry is a hammer-like
        # reclaim — large lower wick (testing EMA21) with close near the high
        # for LONG, or large upper wick with close near the low for SHORT.
        # The previous `body_size / range >= 0.50` gate was structurally
        # backward: it punishes the very wick that identifies a valid pullback
        # test, mistaking hammers for dojis.  Truth-aligned check: close must
        # be in the trend-direction half of the candle's range.
        candle_range = last_high - last_low
        if candle_range > 0:
            if direction == Direction.LONG:
                close_position = (close - last_low) / candle_range
                if close_position < 0.50:
                    return self._reject("body_conviction_fail")
            else:
                close_position = (last_high - close) / candle_range
                if close_position < 0.50:
                    return self._reject("body_conviction_fail")
        # Body must agree with direction (no opposite-coloured close)
        if direction == Direction.LONG and close < last_open:
            return self._reject("body_conviction_fail")
        if direction == Direction.SHORT and close > last_open:
            return self._reject("body_conviction_fail")

        # RSI pullback zone: 40–60
        if rsi_val is not None and not (40 <= rsi_val <= 60):
            return self._reject("rsi_reject")
        rsi_prev = ind.get("rsi_prev")
        if rsi_val is not None and rsi_prev is not None:
            if direction == Direction.LONG and float(rsi_val) <= float(rsi_prev):
                return self._reject("rsi_reject")
            if direction == Direction.SHORT and float(rsi_val) >= float(rsi_prev):
                return self._reject("rsi_reject")

        # Last candle rejection: close > open for LONG, close < open for SHORT
        if direction == Direction.LONG and close <= last_open:
            return self._reject("momentum_reject")
        if direction == Direction.SHORT and close >= last_open:
            return self._reject("momentum_reject")

        # Entry-quality tightening: require a genuine turn/continuation confirmation,
        # not just EMA proximity while pullback is still moving against direction.
        momentum_last = ind.get("momentum_last")
        if momentum_last is None:
            return self._reject("momentum_reject")
        momentum_last = float(momentum_last)
        if direction == Direction.LONG:
            if prev_close > ema9 and prev_close > ema21:
                return self._reject("prev_already_above_emas")
            if close <= ema9 or close <= ema21:
                return self._reject("close_below_emas")
            if close <= prev_close:
                return self._reject("no_close_progression")
            if close <= prev_high:
                return self._reject("no_prev_high_break")
            if last_low > ema21 * 1.001:
                return self._reject("ema21_not_tagged")
            if momentum_last <= 0:
                return self._reject("momentum_flat")
        else:
            if prev_close < ema9 and prev_close < ema21:
                return self._reject("prev_already_below_emas")
            if close >= ema9 or close >= ema21:
                return self._reject("close_above_emas")
            if close >= prev_close:
                return self._reject("no_close_progression")
            if close >= prev_low:
                return self._reject("no_prev_low_break")
            if last_high < ema21 * 0.999:
                return self._reject("ema21_not_tagged")
            if momentum_last >= 0:
                return self._reject("momentum_flat")

        # SMC support. NOTE what this actually checks (Phase 3): `orderblocks`
        # has had no writer for the life of this gate, so `bool(fvgs) or
        # bool(orderblocks)` has always been `bool(fvgs)` alone. The detector
        # now exists but is DARK — its output is on `orderblocks_measured` and
        # this line is unchanged until ORDERBLOCKS_LIVE flips.
        #
        # Nor is this the "in the pullback zone" test the old comment claimed:
        # it is a global existence test. What makes it behave like a zone test
        # is `detect_fvg`'s 12-bar window — any gap it can find is near price by
        # construction (median 0.13 ATR, max 0.52 over the first 89 TPE
        # signals). Widening that window is the other half of Phase 3, also
        # dark: `fvg` stays the narrow list until FVG_WIDE_LIVE flips.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        has_smc_support = bool(fvgs) or bool(orderblocks)
        if not has_smc_support:
            return self._reject("missing_fvg_or_orderblock")

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close * 0.002)
        # BUG FIX 7b: Structural SL at candle low/high, not just EMA distance
        if direction == Direction.LONG:
            sl = min(last_low - atr_val * 0.1, close - atr_val * 1.0,
                     close - close * self.config.sl_pct_range[0] / 100)
        else:
            sl = max(last_high + atr_val * 0.1, close + atr_val * 1.0,
                     close + close * self.config.sl_pct_range[0] / 100)
        sl_dist = abs(close - sl)

        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # BUG FIX: Enforce minimum SL distance (1×ATR or 0.50%)
        min_sl_atr = max(atr_val * 1.0, close * self.config.sl_pct_range[0] / 100)
        if sl_dist < min_sl_atr:
            sl_dist = min_sl_atr
            sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        # Structure-based TP targets
        m5_highs = m5.get("high", [])
        m5_lows = m5.get("low", [])
        # TP1: nearest swing high (LONG) or swing low (SHORT) from last 20 candles
        if direction == Direction.LONG:
            tp1 = max(float(h) for h in m5_highs[-21:-1]) if len(m5_highs) >= 21 else close + sl_dist * 1.5
        else:
            tp1 = min(float(l) for l in m5_lows[-21:-1]) if len(m5_lows) >= 21 else close - sl_dist * 1.5
        # Ensure TP1 is beyond entry in the right direction
        if direction == Direction.LONG and tp1 <= close:
            tp1 = close + sl_dist * 1.5
        if direction == Direction.SHORT and tp1 >= close:
            tp1 = close - sl_dist * 1.5

        # TP2: 4h swing high/low if available, else 2.0 × sl_dist
        candles_4h = candles.get("4h")
        if candles_4h and len(candles_4h.get("high", [])) >= 5:
            _4h_highs = candles_4h.get("high", [])
            _4h_lows = candles_4h.get("low", [])
            if direction == Direction.LONG:
                tp2 = max(float(h) for h in _4h_highs[-10:]) if _4h_highs else close + sl_dist * 2.0
            else:
                tp2 = min(float(l) for l in _4h_lows[-10:]) if _4h_lows else close - sl_dist * 2.0
        else:
            tp2 = close + sl_dist * 2.0 if direction == Direction.LONG else close - sl_dist * 2.0

        # TP3: ratio fallback
        tp3 = close + 4.0 * sl_dist if direction == Direction.LONG else close - 4.0 * sl_dist
        # ATR-adaptive TP1 cap: swing-high TP1 can be 3-5% away in low-ATR accumulation
        _rc_tpe = smc_data.get("regime_context")
        _atr_pct_tpe = _rc_tpe.atr_percentile if _rc_tpe else 50.0
        if _atr_pct_tpe < 40.0:
            _tp1_cap_tpe = sl_dist * 1.8
        elif _atr_pct_tpe < 65.0:
            _tp1_cap_tpe = sl_dist * 2.5
        else:
            _tp1_cap_tpe = None
        if _tp1_cap_tpe is not None:
            tp1 = (min(tp1, close + _tp1_cap_tpe) if direction == Direction.LONG
                   else max(tp1, close - _tp1_cap_tpe))
        # Q4-B: enforce ladder monotonicity.  Prior code's no-4h branch
        # had no tp1-relative floor; the 4h branch fell back to 2.0R which
        # could still be ≤ tp1 when tp1 sat at the 5m swing-high extreme.
        tp1, tp2, tp3 = _enforce_tp_ladder_monotonicity(
            tp1, tp2, tp3, close, sl_dist, direction,
            tp2_rmult_floor=2.0, tp3_rmult_floor=4.0,
        )

        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="TPULLBACK",
            atr_val=atr_val,
            setup_class="TREND_PULLBACK_EMA",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # Trend was sourced from the 1H (EMA21/50 alignment + slope + pullback
        # structure) on the HTF path — record it so the scorer credits the
        # higher-timeframe trend instead of penalising the 5m pullback label.
        sig.htf_trend_aligned = bool(_uses_1h_trend)

        # Override with structure-based TP targets
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # High-probability setup: trend pullback to EMA in trend direction
        sig.confidence = min(100.0, sig.confidence + 8.0)
        # Entry-time feature stamp (2026-08-01, owner: "on which bases entry is
        # confirming especially on Trend pullback EMA").
        #
        # What this path actually confirms on: 1H EMA21-vs-EMA50 for direction,
        # then on 5m an EMA21 tag by the previous bar, a close back above both
        # EMAs, close > prev_close, close > prev_high, RSI inside 40-60 and
        # rising, close in the trend-direction half of its own range, and one
        # momentum sign.  Every one of those is a *boolean* — the evaluator
        # records that each threshold was crossed and never how far.
        #
        # So the extras below are the magnitudes behind its own gates, not a
        # wishlist of new indicators: how mature the 1H trend is, how much of
        # the leg the pullback gave back, where in the RSI band it fired, how
        # decisively prev_high broke, and the distance to the SMC zone its
        # `missing_fvg_or_orderblock` gate claims to require but does not check.
        # `uses_1h_trend` records which of the two direction mechanisms ran —
        # the 1H path and the legacy 5m-regime fallback are different strategies
        # sharing one setup_class, and no artifact has ever distinguished them.
        try:
            from src import entry_features as _ef

            # Only meaningful on the 1H path: on the legacy 5m-regime fallback
            # there is no 1H trend to measure the separation of. Resolved here
            # rather than inline so the None-ness is settled once — the two EMAs
            # are non-None exactly when `_uses_1h_trend` is true, which is that
            # flag's definition.
            _atr_1h = ind_1h.get("atr_last")
            _h1_sep: Optional[float] = None
            if (
                _uses_1h_trend
                and _atr_1h is not None
                and ema21_1h is not None
                and ema50_1h is not None
                and float(_atr_1h) > 0
            ):
                _h1_sep = abs(float(ema21_1h) - float(ema50_1h)) / float(_atr_1h)
            _prev_extreme = prev_high if direction == Direction.LONG else prev_low
            _ef.stamp(
                sig,
                # sig.entry_regime is still "" here — the scanner writes it in
                # _populate_signal_context, after this returns (#850).
                regime=regime,
                features=_ef.capture(
                    symbol=symbol,
                    direction_is_long=(direction == Direction.LONG),
                    entry=close,
                    sl_dist=sl_dist,
                    tp1=tp1,
                    trigger="ema21_tag_reclaim",
                    tf=m5,
                    tf_name="5m",
                    atr=atr_val,
                    smc_data=smc_data,
                    # The level the trigger is literally defined against.
                    entry_ref=ema21,
                    entry_ref_name="ema21_5m",
                    ma_slow=ema50,
                    profile_would_reject=(
                        not self._pass_basic_filters(
                            spread_pct, volume_24h_usd, regime=regime, profile=profile
                        )
                        if profile is not None
                        else None
                    ),
                    extras={
                        "retrace_frac_of_leg": _ef.retrace_fraction(
                            [float(h) for h in highs],
                            [float(low_v) for low_v in lows],
                            close,
                            direction == Direction.LONG,
                        ),
                        "h1_trend_sep_atr": _h1_sep,
                        "smc_zone_dist_atr": _ef.zone_distance_atr(
                            list(fvgs or []) + list(orderblocks or []),
                            close,
                            atr_val,
                        ),
                        "rsi_at_entry": (
                            float(rsi_val) if rsi_val is not None else None
                        ),
                        "prev_extreme_break_atr": (
                            abs(close - _prev_extreme) / float(atr_val)
                            if atr_val and float(atr_val) > 0
                            else None
                        ),
                        # Stamped as a number so it splits like every other
                        # feature; a bool would need its own rendering path.
                        "uses_1h_trend": 1.0 if _uses_1h_trend else 0.0,
                    },
                ),
            )
        except Exception as _exc:  # noqa: BLE001 — never let a stamp kill a scan
            from src import fail_open as _fo

            _fo.record("scalp.tpe_entry_features", _exc)
        return sig

    # ------------------------------------------------------------------
    # LIQUIDATION_REVERSAL path
    # Cascade exhaustion + CVD divergence — fires when liquidity sweep
    # overshoots a key level and CVD confirms absorption.
    # ------------------------------------------------------------------

    def _evaluate_liquidation_reversal(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """LIQUIDATION_REVERSAL path: cascade exhaustion + CVD divergence."""
        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        volumes = m5.get("volume", [])
        if len(closes) < 4 or len(volumes) < 21:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        # 1. Cascade detection: ATR-relative threshold (floor 1.5%, cap 3.5%)
        # Fixed 2.0% never triggered in low-ATR accumulation (cascade_threshold_not_met=162k).
        close_now = float(closes[-1])
        close_3ago = float(closes[-4])
        if close_3ago <= 0:
            return self._reject("cascade_threshold_not_met")
        cascade_pct = (close_now - close_3ago) / close_3ago * 100.0
        _atr_raw = float(indicators.get("5m", {}).get("atr_last", close_now * 0.002))
        _cascade_threshold = max(1.5, min(3.5, _atr_raw / close_now * 100.0 * 3.0))

        if cascade_pct <= -_cascade_threshold:
            reversal_direction = Direction.LONG   # Price fell — potential LONG reversal
        elif cascade_pct >= _cascade_threshold:
            reversal_direction = Direction.SHORT  # Price rose — potential SHORT reversal
        else:
            return self._reject("cascade_threshold_not_met")

        # 2. CVD divergence: price moving one way, CVD moving opposite
        cvd_data = smc_data.get("cvd")
        if cvd_data is None:
            # CVD unavailable — skip this path gracefully
            return self._reject("missing_cvd")
        cvd_values = cvd_data if isinstance(cvd_data, list) else cvd_data.get("values", [])
        if len(cvd_values) < 4:
            return self._reject("cvd_insufficient")
        cvd_now = float(cvd_values[-1])
        cvd_3ago = float(cvd_values[-4])
        cvd_change = cvd_now - cvd_3ago

        # For LONG reversal: price fell but CVD is rising (buyers absorbing)
        if reversal_direction == Direction.LONG and cvd_change <= 0:
            return self._reject("cvd_divergence_failed")
        # For SHORT reversal: price rose but CVD is falling (sellers absorbing)
        if reversal_direction == Direction.SHORT and cvd_change >= 0:
            return self._reject("cvd_divergence_failed")

        ind = indicators.get("5m", {})
        rsi_val = ind.get("rsi_last")
        rsi_prev = ind.get("rsi_prev")

        # Pre-compute cascade extrema (needed by gate 4 below as well as the
        # SL block below the RSI gate).
        _cascade_slice = [float(c) for c in closes[-4:]]
        cascade_low = min(_cascade_slice)
        cascade_high = max(_cascade_slice)
        cascade_range = cascade_high - cascade_low

        # 3. RSI extreme gate
        # A 5m cascade reversal needs OVERSOLD context WITH reversal under way,
        # not "RSI must be exhausted."  Pre-fix used <25 / >75 thresholds which
        # 5m RSI rarely hits during a normal 1.5-3% cascade — the gate killed
        # valid reversal setups at the structural moment they form (RSI in
        # 28-35 with RSI rising is the canonical bullish-reversal context;
        # demanding <25 means waiting until the cascade has already exhausted).
        # New rule: oversold zone (LONG <35 / SHORT >65) AND RSI direction
        # confirms the reversal is actually under way (rising for LONG, falling
        # for SHORT) when rsi_prev is available.
        if reversal_direction == Direction.LONG:
            if rsi_val is not None and rsi_val >= 35:
                return self._reject("rsi_reject")
            if (rsi_val is not None and rsi_prev is not None
                    and float(rsi_val) <= float(rsi_prev)):
                return self._reject("rsi_reject")
        else:
            if rsi_val is not None and rsi_val <= 65:
                return self._reject("rsi_reject")
            if (rsi_val is not None and rsi_prev is not None
                    and float(rsi_val) >= float(rsi_prev)):
                return self._reject("rsi_reject")

        # 4. Price within 0.5% of a known orderblock or FVG zone.
        # Pre-fix only checked close_now — but a cascade by definition
        # OVERSHOOTS supply/demand zones, then bounces.  By the time we
        # evaluate, close_now is past the zone (in recovery).  Truth-aligned
        # check: either close_now or the cascade extremum (low for LONG,
        # high for SHORT) within the proximity window — the extremum is what
        # actually tested the zone.
        cascade_extremum = cascade_low if reversal_direction == Direction.LONG else cascade_high
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        near_zone = False
        for zone in list(fvgs) + list(orderblocks):
            zone_level = zone.gap_low if hasattr(zone, "gap_low") else (
                zone.get("level") if isinstance(zone, dict) else None
            )
            if zone_level is None and hasattr(zone, "price"):
                zone_level = zone.price
            if zone_level is not None and float(zone_level) > 0:
                _zl = float(zone_level)
                _close_proximity = abs(close_now - _zl) / _zl
                _extremum_proximity = abs(cascade_extremum - _zl) / _zl
                if _close_proximity <= 0.005 or _extremum_proximity <= 0.005:
                    near_zone = True
                    break
        if not near_zone:
            return self._reject("missing_fvg_or_orderblock")

        # 5. Volume spike: last candle volume > 2.5x 20-candle average
        avg_vol = sum(float(v) for v in volumes[-21:-1]) / 20.0 if len(volumes) >= 21 else 0.0
        last_vol = float(volumes[-1])
        if avg_vol <= 0 or last_vol < 2.5 * avg_vol:
            return self._reject("volume_spike_missing")

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close_now * 0.002)

        # SL: beyond cascade extremum + 0.3% buffer (cascade_low/high computed earlier).
        sl_buffer = close_now * 0.003
        if reversal_direction == Direction.LONG:
            sl = cascade_low - sl_buffer
        else:
            sl = cascade_high + sl_buffer

        sl_dist = abs(close_now - sl)
        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")

        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=reversal_direction,
            close=close_now,
            sl=sl,
            tp1=0.0,
            tp2=0.0,
            tp3=0.0,
            sl_dist=sl_dist,
            id_prefix="LIQ-REV",
            atr_val=atr_val,
            setup_class="LIQUIDATION_REVERSAL",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # B13: Fibonacci retrace TP targets (Type D — Reversion, OWNER_BRIEF)
        # 38.2%, 61.8%, 100% retrace of the cascade range back toward pre-cascade level.
        # Fall back to ATR R-multiples when cascade_range is degenerate (< ATR * 0.5).
        _risk = sl_dist
        if cascade_range >= atr_val * 0.5:
            if reversal_direction == Direction.LONG:
                _tp1_fib = cascade_low + cascade_range * 0.382
                _tp2_fib = cascade_low + cascade_range * 0.618
                _tp3_fib = cascade_low + cascade_range * 1.0
                sig.tp1 = _tp1_fib if _tp1_fib > close_now else close_now + _risk * 1.5
                sig.tp2 = _tp2_fib if _tp2_fib > close_now else close_now + _risk * 2.5
                sig.tp3 = _tp3_fib if _tp3_fib > close_now else close_now + _risk * 4.0
            else:
                _tp1_fib = cascade_high - cascade_range * 0.382
                _tp2_fib = cascade_high - cascade_range * 0.618
                _tp3_fib = cascade_high - cascade_range * 1.0
                sig.tp1 = _tp1_fib if _tp1_fib < close_now else close_now - _risk * 1.5
                sig.tp2 = _tp2_fib if _tp2_fib < close_now else close_now - _risk * 2.5
                sig.tp3 = _tp3_fib if _tp3_fib < close_now else close_now - _risk * 4.0
        else:
            # Degenerate cascade range — fall back to ATR-based R-multiples
            if reversal_direction == Direction.LONG:
                sig.tp1 = close_now + _risk * 1.5
                sig.tp2 = close_now + _risk * 2.5
                sig.tp3 = close_now + _risk * 4.0
            else:
                sig.tp1 = close_now - _risk * 1.5
                sig.tp2 = close_now - _risk * 2.5
                sig.tp3 = close_now - _risk * 4.0

        # Q4-B: enforce ladder monotonicity.  The fib branch picks each TP
        # independently against close (not against the prior TP), so a
        # pathological geometry (small bounce + large cascade) can produce
        # tp1=fib but tp2=ATR-fallback < tp1.
        sig.tp1, sig.tp2, sig.tp3 = _enforce_tp_ladder_monotonicity(
            sig.tp1, sig.tp2, sig.tp3, close_now, _risk, reversal_direction,
            tp2_rmult_floor=2.5, tp3_rmult_floor=4.0,
        )

        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # High-conviction setup: multiple confirming factors required
        sig.confidence = min(100.0, sig.confidence + 10.0)
        return sig

    # ------------------------------------------------------------------
    # WHALE_MOMENTUM path (absorbed from former TapeChannel)
    # Whale alert or delta spike + dominant tick flow + OBI confirmation
    # ------------------------------------------------------------------

    def _evaluate_whale_momentum(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        # Regime gate removed per OWNER_BRIEF §3.4: WHALE_MOMENTUM is
        # "internally direction-driven (direction comes from tape)" and
        # explicitly NOT regime-gated.  The thesis gates below
        # (whale_alert + volume_delta_spike + order_book_imbalance) already
        # ensure no signal fires without genuine flow — making the regime
        # block redundant.  In QUIET cycles those thesis gates simply
        # reject for the right reason instead of "regime_blocked".
        # `regime_upper` is still used by the OBI marginal-acceptance branch
        # to allow looser depth confirmation in fast/volatile regimes.
        regime_upper = regime.upper() if regime else ""
        whale = smc_data.get("whale_alert")
        delta_spike = smc_data.get("volume_delta_spike", False)
        if whale is None and not delta_spike:
            return self._reject("momentum_reject")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        m1 = candles.get("1m")
        if m1 is None or len(m1.get("close", [])) < 10:
            return self._reject("insufficient_candles")

        close = float(m1["close"][-1])

        ticks: List[Dict[str, Any]] = smc_data.get("recent_ticks", [])
        if not ticks:
            tick_state = self._dependency_state(smc_data, "recent_ticks")
            if tick_state == "unavailable":
                return self._reject("missing_recent_ticks")
            return self._reject("recent_ticks_empty")
        buy_vol = sum(
            t.get("qty", 0) * t.get("price", 0)
            for t in ticks if not t.get("isBuyerMaker", True)
        )
        sell_vol = sum(
            t.get("qty", 0) * t.get("price", 0)
            for t in ticks if t.get("isBuyerMaker", True)
        )

        total_vol = buy_vol + sell_vol
        if total_vol < _WHALE_MIN_TICK_VOLUME_USD:
            return self._reject("recent_ticks_insufficient")

        if buy_vol >= sell_vol * _WHALE_DELTA_MIN_RATIO:
            direction = Direction.LONG
        elif sell_vol >= buy_vol * _WHALE_DELTA_MIN_RATIO:
            direction = Direction.SHORT
        else:
            return self._reject("momentum_reject")

        # RSI gate — layered soft/hard replacing the prior binary check_rsi_regime
        # call.  Whale buying/selling routinely pushes RSI into borderline zones
        # without exhausting the move; hard-blocking at those levels loses valid
        # setups.  Architecture is consistent with VOLUME_SURGE_BREAKOUT and
        # BREAKDOWN_SHORT:
        #   LONG : hard block ≥ 82 (extreme overbought); soft +5 for 72–81
        #   SHORT: hard block ≤ 18 (extreme oversold);   soft +5 for 19–28
        rsi_val_1m = indicators.get("1m", {}).get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val_1m is not None:
            if direction == Direction.LONG:
                if rsi_val_1m >= _WHALE_RSI_LONG_HARD_MAX:
                    return self._reject("rsi_reject")
                if _WHALE_RSI_LONG_SOFT_MIN <= rsi_val_1m < _WHALE_RSI_LONG_HARD_MAX:
                    rsi_penalty = 5.0  # Borderline: penalise but still allow
            else:
                if rsi_val_1m <= _WHALE_RSI_SHORT_HARD_MIN:
                    return self._reject("rsi_reject")
                if _WHALE_RSI_SHORT_HARD_MIN < rsi_val_1m <= _WHALE_RSI_SHORT_SOFT_MAX:
                    rsi_penalty = 5.0  # Borderline: penalise but still allow

        # Order book imbalance — confirms the dominant side matches the whale
        # direction.
        #
        # Three-tier behaviour:
        #   1. order_book is None (circuit breaker open): skip OBI entirely.
        #      NOTE: no penalty is applied in this case today — obi_penalty stays
        #      0.0 when order_book is None. The prior `obi_confirmed=False -> +10`
        #      design was never wired up; flagged for signal-quality review.
        #   2. order_book source=book_ticker (top-of-book only): treat as
        #      partial/degraded evidence, never as full depth confirmation.
        #   3. order_book present, ratio ≥ _WHALE_OBI_MIN (1.5×): full
        #      confirmation, no OBI penalty.
        #   4. order_book present, ratio in [_WHALE_OBI_SOFT_MIN, _WHALE_OBI_MIN)
        #      AND regime is a fast/volatile regime: marginal OBI treated as a
        #      soft contributor (+8 penalty) rather than hard rejection.  In fast
        #      regimes depth books are routinely thin due to market-maker spread
        #      widening; tick flow and whale alert carry more weight.
        #   5. order_book present, ratio < _WHALE_OBI_MIN in a calm regime, or
        #      ratio < _WHALE_OBI_SOFT_MIN in any regime: hard reject — the order
        #      book actively contradicts the assumed whale direction.
        order_book = smc_data.get("order_book")
        obi_penalty = 0.0
        if order_book is not None:
            ob_source = str(order_book.get("source") or "").strip().lower() if isinstance(order_book, dict) else ""
            ob_quality = (
                str(order_book.get("depth_quality") or "").strip().lower()
                if isinstance(order_book, dict)
                else ""
            )
            if ob_source == "book_ticker" or ob_quality == "top_of_book_only":
                obi_penalty = max(obi_penalty, 10.0)
            else:
                bids = order_book.get("bids", [])
                asks = order_book.get("asks", [])
                bid_depth = sum(float(b[1]) * float(b[0]) for b in bids[:10])
                ask_depth = sum(float(a[1]) * float(a[0]) for a in asks[:10])
                if bid_depth <= 0 or ask_depth <= 0:
                    return self._reject("order_book_insufficient")
                imbalance_ratio = (
                    bid_depth / ask_depth if direction == Direction.LONG else ask_depth / bid_depth
                )
                if imbalance_ratio >= _WHALE_OBI_MIN:
                    pass  # strong OBI (ratio >= _WHALE_OBI_MIN) — full confirmation, no penalty
                elif regime_upper in _WHALE_FAST_REGIMES and imbalance_ratio >= _WHALE_OBI_SOFT_MIN:
                    # Marginal OBI in a fast regime: soft penalty, not hard reject
                    obi_penalty = 8.0
                else:
                    return self._reject("order_book_imbalance_failed")

        atr_val = indicators.get("1m", {}).get("atr_last", close * 0.002)

        # SL: use the recent swing low (LONG) or swing high (SHORT) as the
        # order-flow invalidation point.  If the whale impulse was genuine,
        # price should not retrace through the swing that preceded the impulse.
        # ATR acts as a minimum floor to avoid mechanically tight stops when the
        # swing is extremely recent.  Falls back to the previous % / ATR logic
        # when the lookback window contains insufficient data.
        m1_highs = m1.get("high", [])
        m1_lows = m1.get("low", [])
        if direction == Direction.LONG and len(m1_lows) > _WHALE_SWING_LOOKBACK:
            swing_low = min(
                float(l) for l in m1_lows[-_WHALE_SWING_LOOKBACK - 1 : -1]
            )
            invalidation = swing_low * (1.0 - _WHALE_SWING_BUFFER)
            sl_dist = max(close - invalidation, atr_val)
        elif direction == Direction.SHORT and len(m1_highs) > _WHALE_SWING_LOOKBACK:
            swing_high = max(
                float(h) for h in m1_highs[-_WHALE_SWING_LOOKBACK - 1 : -1]
            )
            invalidation = swing_high * (1.0 + _WHALE_SWING_BUFFER)
            sl_dist = max(invalidation - close, atr_val)
        else:
            sl_dist = max(close * self.config.sl_pct_range[0] / 100, atr_val)

        sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        _regime_ctx = smc_data.get("regime_context")
        _pair_profile = smc_data.get("pair_profile")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=0.0,
            tp2=0.0,
            tp3=0.0,
            sl_dist=sl_dist,
            id_prefix="WHALE",
            atr_val=atr_val,
            setup_class="WHALE_MOMENTUM",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=_pair_profile.tier if _pair_profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # Override TPs with evaluator-authored R-multiple targets (B13 compliance:
        # Type A — Fixed Ratio per OWNER_BRIEF.md: 1.5R, 2.5R, 4.0R).
        # Use the actual SL from the built signal as the risk basis so the
        # multipliers are consistent with whatever sl_dist adjustments
        # build_channel_signal applied.  Fall back to ATR when risk is
        # degenerate (entry ≈ stop_loss).
        entry = sig.entry
        risk = abs(entry - sig.stop_loss)
        if risk < atr_val * 0.01:  # degenerate: SL essentially at entry — fall back to 1× ATR
            risk = atr_val
        if direction == Direction.LONG:
            sig.tp1 = round(entry + risk * 1.5, 8)
            sig.tp2 = round(entry + risk * 2.5, 8)
            sig.tp3 = round(entry + risk * 4.0, 8)
        else:
            sig.tp1 = round(entry - risk * 1.5, 8)
            sig.tp2 = round(entry - risk * 2.5, 8)
            sig.tp3 = round(entry - risk * 4.0, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # Accumulate soft penalties then assign once.
        _penalty = getattr(sig, "soft_penalty_total", 0.0)
        if order_book is None:
            # No order book available — signal is valid on tick-flow alone
            # but carries lower certainty.
            _penalty += 10.0
        if obi_penalty > 0:
            # Marginal OBI in fast regime: weaker confirmation layer.
            _penalty += obi_penalty
        if rsi_penalty > 0:
            # Borderline RSI: signal may still be valid but with lower certainty.
            _penalty += rsi_penalty
        sig.soft_penalty_total = _penalty
        return sig

    def _check_mover_freshness(
        self,
        *,
        closes: Any,
        swing_level: float,
        breakout_idx: int,
        is_long: bool,
    ) -> Tuple[bool, str]:
        """Reject stale or exhausted continuation breakouts (VSB/BDS).

        The mover universe is promoted off a lagging 24h |%change|, so these
        continuation paths often fire on a move that has already played out.
        This gate keeps entries fresh:

          * breakout recency — the broken-level candle must be within
            ``_MOVER_FRESHNESS_MAX_BREAKOUT_AGE`` candles, not a ~60-min-old break.
          * impulse band — the recent move INTO the broken level (over
            ``_MOVER_FRESHNESS_LOOKBACK`` candles) must sit in
            [``MIN_PCT``, ``MAX_PCT``]: below MIN = no live momentum (stale
            24h mover); above MAX = blow-off/exhausted (late entry into the
            reversal — the short-side oversold-bounce trap).

        Returns ``(ok, reason)``. Fail-open (``True, ""``) when the gate is
        disabled or there isn't enough history to judge — never blocks on
        missing data. ``reason`` is a suppression-telemetry tag on rejection.
        """
        if not _MOVER_FRESHNESS_ENABLED:
            return True, ""
        if abs(int(breakout_idx)) > _MOVER_FRESHNESS_MAX_BREAKOUT_AGE:
            return False, "breakout_stale"
        lookback = _MOVER_FRESHNESS_LOOKBACK
        if closes is None or len(closes) < lookback + 1 or swing_level <= 0:
            return True, ""  # insufficient history → fail-open
        past_close = float(closes[-(lookback + 1)])
        if past_close <= 0:
            return True, ""
        if is_long:
            impulse_pct = (swing_level - past_close) / past_close * 100.0
        else:
            impulse_pct = (past_close - swing_level) / past_close * 100.0
        if impulse_pct < _MOVER_FRESHNESS_MIN_PCT:
            return False, "move_not_fresh"
        if impulse_pct > _MOVER_FRESHNESS_MAX_PCT:
            return False, "move_exhausted"
        return True, ""

    # ------------------------------------------------------------------
    # VOLUME_SURGE_BREAKOUT path
    # Volume surge + pullback to breakout level — fires in volatile/trending markets.
    # ------------------------------------------------------------------

    def _evaluate_volume_surge_breakout(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """VOLUME_SURGE_BREAKOUT path: price breaks swing high on surge volume then pulls back.

        Refinements vs. original:
        - Breakout search window extended from exactly candle[-3] to the last 5 closed
          candles, accommodating 1–4 candle timing variation common in live crypto.
        - Pullback zone corrected from 0.5%–2.0% (which was effectively 0.5%–0.8% due
          to the structural SL constraint) to 0.1%–0.75%.  This adds shallow-sprint
          entries (0.1%–0.5%) that the original wrongly rejected while making the upper
          bound explicit.  Premium zone 0.3%–0.6% earns a confidence bonus; extended
          zone (0.1%–0.3% and 0.6%–0.75%) applies a soft penalty.
        - RSI hard gate relaxed from 45–72 to 40–82.  Borderline values (40–44 or
          73–82) attract a soft penalty rather than a hard block, because strong
          breakout momentum routinely pushes RSI above 72 without invalidating the setup.
        - FVG / orderblock requirement converted to a soft confidence contributor in
          fast-momentum regimes (VOLATILE, BREAKOUT_EXPANSION, STRONG_TREND) where SMC
          detection may lag the price action.  Remains a hard gate in calmer regimes.
        - Breakout-candle volume check now uses the actual breakout candle's volume
          rather than always checking volumes[-3].
        """
        # Regime gate removed per OWNER_BRIEF §3.4: breakout setups
        # (VSB/BDS/ORB) "fire in any HTF context" — the volume_spike_missing
        # and breakout_not_found thesis gates below already catch any
        # QUIET-period candidate that lacks the structural setup, so the
        # regime block was redundant.  `regime_upper` is still used by the
        # fast-momentum FVG-soft branch below.
        regime_upper = regime.upper() if regime else ""
        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 28:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        highs = m5.get("high", [])
        volumes = m5.get("volume", [])
        if len(closes) < 28 or len(highs) < 28 or len(volumes) < 10:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        # Rolling 7-candle average (last 7 complete candles, not current)
        rolling_vols = [float(v) for v in volumes[-8:-1]]
        if len(rolling_vols) < 7 or sum(rolling_vols) <= 0:
            return self._reject("volume_spike_missing")
        rolling_avg = sum(rolling_vols) / len(rolling_vols)

        # NOTE: a current-candle volume gate (volumes[-1] ≥ SURGE_VOLUME_MULTIPLIER ×
        # rolling_avg) used to live here.  It was structurally broken: volumes[-1]
        # is a STILL-FORMING 5m candle whose volume is necessarily a fraction of a
        # complete candle's, so demanding it exceed multiples of complete-candle
        # averages is a unit mismatch that rejects valid setups.  Worse, the path's
        # thesis is "surge breakout + pullback" — pullbacks by definition have
        # REDUCED volume, so the gate contradicts the very pattern it's meant to
        # validate.  The breakout-candle volume check below (≥ 2× rolling avg on the
        # actual closed breakout candle) properly validates the surge.  In the
        # latest 18,423-cycle zip, `volume_spike_missing` was 62.7% of all VSB
        # rejections — by far the dominant suppressor — and the bulk of it was
        # this gate firing on partial current-candle volume.  Existing test
        # fixtures set `vols[-1] = 4500.0` artificially to bypass this gate;
        # that's a strong tell the gate was already known broken inside the
        # test infrastructure.

        # Swing high: configurable lookback window pushed further back from
        # the search window to isolate real prior resistance from in-rally
        # peaks.  Original ``highs[-26:-6]`` was vulnerable to fast vertical
        # moves contaminating the reference; ``[-50:-15]`` (default) places
        # the reference 75-250 min back where it represents structure that
        # PRE-DATES the move under test.  Env-overridable per B8.
        # Layout: [...swing_high window│gap│breakout search│current]
        #          highs[start:end]    [-15:-WINDOW]  [-WINDOW:-1]  [-1]
        _swing_window = highs[_VSB_SWING_LOOKBACK_START:_VSB_SWING_LOOKBACK_END]
        if len(_swing_window) < 5:
            return self._reject("breakout_not_found")
        swing_high_level = max(float(h) for h in _swing_window)
        if swing_high_level <= 0:
            return self._reject("breakout_not_found")

        # Find the most recent breakout candle within the configurable
        # search window.  Default 12 candles (60 min on 5m) — captures
        # breakouts that the original 25-min window missed in fast moves
        # where the breakout candle has already slipped past index [-6]
        # by the time the next scan cycle catches the pullback geometry.
        # Scans newest-first to prefer the candle closest to current.
        # A genuine breakout requires the candle to CLOSE above the
        # level — a wick that pierces then closes back below is a sweep
        # (LSR), not a breakout.
        breakout_candle_idx: Optional[int] = None
        breakout_vol = 0.0
        closes_arr = closes
        for i in range(-2, -(_VSB_BREAKOUT_SEARCH_WINDOW + 1), -1):
            if (float(highs[i]) > swing_high_level
                    and float(closes_arr[i]) > swing_high_level):
                breakout_candle_idx = i
                breakout_vol = float(volumes[i])
                break

        if breakout_candle_idx is None:
            return self._reject("breakout_not_found")

        # Freshness gate — reject stale or exhausted breakouts (movers are
        # promoted off a lagging 24h move, so the breakout we're catching may
        # already be old or blown-off). See _check_mover_freshness.
        _fresh_ok, _fresh_reason = self._check_mover_freshness(
            closes=closes,
            swing_level=swing_high_level,
            breakout_idx=breakout_candle_idx,
            is_long=True,
        )
        if not _fresh_ok:
            return self._reject(_fresh_reason)

        # Pullback zone: current close is below the swing high (breakout retest).
        # Lower bound 0.1% ensures a genuine pullback below the broken level.
        # Upper bound expanded 2026-05-11 from 0.75% → ``_VSB_PULLBACK_MAX_PCT``
        # (default 1.5%) to catch the deeper retests common in strong trending
        # moves — was responsible for 315k retest_proximity_failed rejections
        # (17% of VSB attempts).  Premium zone (0.3%-0.6%) keeps the textbook
        # geometry; extended zone (0.1%-0.3% and 0.6%-max) earns the existing
        # +3.0 soft penalty so quality stays gated.
        close = float(closes[-1])
        if close <= 0:
            return self._reject("breakout_not_found")
        dist_from_swing_pct = (swing_high_level - close) / swing_high_level * 100.0
        if not (0.1 <= dist_from_swing_pct <= _VSB_PULLBACK_MAX_PCT):
            return self._reject("retest_proximity_failed")
        pullback_in_premium_zone = (0.3 <= dist_from_swing_pct <= 0.6)
        pullback_penalty = 0.0 if pullback_in_premium_zone else 3.0

        # Condition 4: EMA9 > EMA21 (trend alignment, hard gate unchanged)
        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None or ema9 <= ema21:
            return self._reject("ema_alignment_reject")

        # RSI — layered soft/hard gate replacing the previous hard gate of 45–72.
        # Hard block below 40 (momentum failure) or above 82 (extreme overbought
        # exhaustion at entry).  Borderline 40–44 or 73–82 attracts a soft penalty;
        # optimal zone 45–72 passes with no adjustment.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if rsi_val < 40.0 or rsi_val > 82.0:
                return self._reject("rsi_reject")
            elif not (45.0 <= rsi_val <= 72.0):
                rsi_penalty = 5.0

        # FVG / orderblock — soft confidence contributor in fast-momentum regimes where
        # SMC detection may lag price.  Hard gate in calmer regimes preserves structural
        # quality requirements without globally softening the path.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        has_smc_context = bool(fvgs or orderblocks)
        fvg_penalty = 0.0
        if not has_smc_context:
            if regime_upper not in _FAST_MOMENTUM_REGIMES:
                return self._reject("missing_fvg_or_orderblock")
            fvg_penalty = 8.0  # Soft penalty in fast regimes instead of hard block

        # Breakout candle volume ≥ _VSB_BREAKOUT_VOL_MULT × rolling average
        # (env-overridable per B8; was hardcoded 2.0).  Validates surge on the
        # actual closed breakout candle.
        if breakout_vol < _VSB_BREAKOUT_VOL_MULT * rolling_avg:
            return self._reject("volume_spike_missing")

        # Method-specific SL/TP.
        # Pre-fix anchored SL purely to swing_high (`swing_high * 0.992`), which
        # creates absurdly tight stops when close is in deep pullback:
        #   close at 0.50% below swing_high → sl_dist = 0.30%
        #   close at 0.60% below swing_high → sl_dist = 0.20%
        #   close at 0.75% below swing_high → sl_dist = 0.05% (< spread on most pairs!)
        # The structural intent ("SL just below the broken resistance") is right,
        # but the geometry must also respect (a) ATR-based volatility and (b) a
        # close-relative minimum.  Take the tightest-acceptable SL across:
        #   - structural floor: 0.8% below swing_high (anti-bull-trap)
        #   - close-relative floor: max(0.8% of close, 1.0×ATR)
        # Final SL is the LOWER of these (further from close → wider, never tighter).
        atr_val = ind.get("atr_last", close * 0.002)
        structural_sl = swing_high_level * (1 - 0.008)
        close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
        sl = min(structural_sl, close_rel_floor)
        sl_dist = abs(close - sl)
        if sl_dist <= 0 or sl >= close:
            return self._reject("invalid_sl_geometry")

        # TP: measured move from base of range (window aligned with swing high window)
        lows = m5.get("low", [])
        base_of_range = min(float(l) for l in lows[-26:-6]) if len(lows) >= 26 else close * 0.98
        measured_move = swing_high_level - base_of_range
        if measured_move <= 0:
            measured_move = sl_dist * 2.0

        tp1 = close + measured_move
        tp2 = close + measured_move * 1.5
        tp3 = close + measured_move * 2.0

        profile = smc_data.get("pair_profile")
        # atr_val already computed above for SL.
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=Direction.LONG,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="SURGE",
            atr_val=atr_val,
            setup_class="VOLUME_SURGE_BREAKOUT",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # Override with method-specific structural SL and measured-move TPs
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Stamp the validated breakout-candle surge ratio so the scoring engine
        # scores the volume dimension off the surge, not the low-volume pullback
        # entry candle.  rolling_avg > 0 is guaranteed by the volume gate above.
        sig.breakout_volume_ratio = breakout_vol / rolling_avg if rolling_avg > 0 else 0.0

        # Pre-score confidence annotation (established pattern for all evaluators).
        # All evaluators in this family add a path-specific base boost to sig.confidence
        # before returning.  The scanner's _prepare_signal() pipeline overwrites this
        # value three times (legacy confidence → score_signal_components →
        # composite scoring engine) so this mutation does NOT affect the final signal
        # confidence and does NOT bypass or double-count the family-aware scoring engine.
        # Quality differentiation (premium pullback zone, SMC context) is expressed
        # correctly via the soft_penalty_total system below, which the scanner deducts
        # post-scoring, and via the scoring engine's own _score_smc(fvg_zones=...) and
        # _score_volume() dimensions that already capture these signals independently.
        sig.confidence = min(100.0, sig.confidence + 8.0)

        # Accumulate soft penalties — the scanner deducts these from confidence after
        # the composite scoring pass, preserving the separation between hard gates and
        # soft quality adjustments.
        total_penalty = pullback_penalty + rsi_penalty + fvg_penalty
        if total_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

        return sig

    # ------------------------------------------------------------------
    # BREAKDOWN_SHORT path
    # Mirror of VOLUME_SURGE_BREAKOUT for the short side.
    # ------------------------------------------------------------------

    def _evaluate_breakdown_short(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """BREAKDOWN_SHORT path: price breaks swing low on surge volume then dead-cat bounces.

        Refinements vs. original:
        - Breakdown search window extended from exactly candle[-3] to the last 5 closed
          candles, accommodating 1–4 candle timing variation common in live crypto.
        - Dead-cat bounce zone corrected from 0.5%–2.0% to 0.1%–0.75%.  The original
          2.0% upper bound was internally impossible: the structural SL sits 0.8% above
          the swing low, so any bounce > 0.8% fails the sl > close constraint silently.
          The new explicit upper bound of 0.75% makes the valid window clear.  The lower
          bound is widened from 0.5% to 0.1% to accept shallow-sprint entries that the
          original wrongly rejected.  Premium zone 0.3%–0.6% passes with no soft penalty;
          extended zone (0.1%–0.3% and 0.6%–0.75%) accumulates a +3.0 soft penalty via
          soft_penalty_total (deducted post-scoring by the scanner).
        - RSI hard gate relaxed from 28–55 to 20–68.  Borderline values (20–27 or 56–68)
          accumulate a +5.0 soft penalty rather than a hard block, because dead-cat
          bounces routinely push RSI to 55–68 before bearish continuation resumes.
        - FVG / orderblock requirement converted to a soft penalty contributor in
          fast-bearish regimes (VOLATILE, TRENDING_DOWN, BREAKOUT_EXPANSION, STRONG_TREND)
          where SMC detection may lag fast price action: missing FVG/OB accumulates a
          +8.0 soft penalty instead of hard-blocking.  Remains a hard gate in calmer
          regimes.
        - Breakdown-candle volume check now uses the actual breakdown candle's volume
          rather than always checking volumes[-3].
        """
        # Regime gate removed per OWNER_BRIEF §3.4: breakout setups
        # (VSB/BDS/ORB) "fire in any HTF context".  The breakout_not_found
        # and volume_spike_missing thesis gates below already enforce
        # structural validity in any regime.  `regime_upper` is still used
        # by the fast-bearish FVG-soft branch below.
        regime_upper = regime.upper() if regime else ""
        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 28:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        lows = m5.get("low", [])
        highs = m5.get("high", [])
        volumes = m5.get("volume", [])
        if len(closes) < 28 or len(lows) < 28 or len(volumes) < 10:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        # Rolling 7-candle average (last 7 complete candles, not current)
        rolling_vols = [float(v) for v in volumes[-8:-1]]
        if len(rolling_vols) < 7 or sum(rolling_vols) <= 0:
            return self._reject("volume_spike_missing")
        rolling_avg = sum(rolling_vols) / len(rolling_vols)

        # NOTE: a current-candle volume gate (volumes[-1] ≥ SURGE_VOLUME_MULTIPLIER ×
        # rolling_avg) used to live here.  Removed in path audit #6 for the same
        # reasons it was removed from VSB in #250: volumes[-1] is a STILL-FORMING
        # candle (unit mismatch with complete-candle averages), and BDS's thesis
        # is "breakdown + DEAD-CAT BOUNCE" — bounces have REDUCED volume by
        # definition, so the gate contradicted the very pattern it was meant to
        # validate.  The breakdown-candle volume check below validates the actual
        # surge on the closed breakdown candle.

        # Swing low: configurable lookback window pushed further back from
        # the search window to isolate real prior support from in-drop troughs.
        # Same calibration as VSB swing-high reference (2026-05-11).  Default
        # ``[-50:-15]`` places reference 75-250 min back where it represents
        # structure that pre-dates the breakdown under test.
        _swing_window = lows[_BDS_SWING_LOOKBACK_START:_BDS_SWING_LOOKBACK_END]
        if len(_swing_window) < 5:
            return self._reject("breakout_not_found")
        swing_low_level = min(float(l) for l in _swing_window)
        if swing_low_level <= 0:
            return self._reject("breakout_not_found")

        # Find the most recent breakdown candle within the configurable
        # search window.  Default 12 candles (60 min on 5m) — captures
        # breakdowns that the original 25-min window missed in fast drops
        # where the breakdown candle has already slipped past index [-6]
        # by the time the next scan cycle catches the bounce geometry.
        # A genuine breakdown requires the candle to CLOSE below the
        # level — a wick that pierces then closes back above is a
        # bullish sweep (LSR LONG), not a breakdown.
        breakdown_candle_idx: Optional[int] = None
        breakdown_vol = 0.0
        for i in range(-2, -(_BDS_BREAKOUT_SEARCH_WINDOW + 1), -1):
            if (float(lows[i]) < swing_low_level
                    and float(closes[i]) < swing_low_level):
                breakdown_candle_idx = i
                breakdown_vol = float(volumes[i])
                break

        if breakdown_candle_idx is None:
            return self._reject("breakout_not_found")

        # Freshness gate — reject stale or exhausted breakdowns. The MAX-impulse
        # ceiling is the symmetric oversold-exhaustion guard: don't short a
        # dump that has already fallen too far (the dead-cat-bounce trap).
        _fresh_ok, _fresh_reason = self._check_mover_freshness(
            closes=closes,
            swing_level=swing_low_level,
            breakout_idx=breakdown_candle_idx,
            is_long=False,
        )
        if not _fresh_ok:
            return self._reject(_fresh_reason)

        # Dead-cat bounce zone: current close is above the swing low (bounce from breakdown).
        # Lower bound: 0.1% ensures a genuine micro-bounce has occurred above the broken
        # support level rather than price still pressing at the low.
        # Upper bound: 0.75% — the structural SL is 0.8% above swing_low, so bounces
        # beyond 0.75% leave sl ≤ close (checked explicitly below), making this bound
        # consistent with the SL placement.
        # Premium zone (0.3%–0.6%) captures textbook dead-cat geometry; earns no penalty.
        # Extended zone (0.1%–0.3% and 0.6%–0.75%) applies a soft penalty.
        close = float(closes[-1])
        if close <= 0:
            return self._reject("retest_proximity_failed")
        dist_from_swing_pct = (close - swing_low_level) / swing_low_level * 100.0
        # Upper bound expanded 2026-05-11 from 0.75% → ``_BDS_PULLBACK_MAX_PCT``
        # (default 1.5%) to catch the deeper dead-cat bounces common in strong
        # downtrends.  Premium zone (0.3%-0.6%) keeps the textbook geometry;
        # extended zone earns +3.0 soft penalty so quality stays gated.
        if not (0.1 <= dist_from_swing_pct <= _BDS_PULLBACK_MAX_PCT):
            return self._reject("retest_proximity_failed")
        bounce_in_premium_zone = (0.3 <= dist_from_swing_pct <= 0.6)
        bounce_penalty = 0.0 if bounce_in_premium_zone else 3.0

        # EMA9 < EMA21 (trend alignment, hard gate unchanged)
        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None or ema9 >= ema21:
            return self._reject("ema_alignment_reject")

        # RSI — layered soft/hard gate replacing the previous hard gate of 28–55.
        # Hard block below 20 (full capitulation, no tradeable dead-cat bounce) or
        # above 68 (too bullish, bearish continuation thesis breaks down).
        # Borderline 20–27 or 56–68 attracts a soft penalty; optimal 28–55 passes
        # with no adjustment.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if rsi_val < 20.0 or rsi_val > 68.0:
                return self._reject("rsi_reject")
            elif not (28.0 <= rsi_val <= 55.0):
                rsi_penalty = 5.0

        # FVG / orderblock — soft penalty contributor in fast-bearish regimes where
        # SMC detection may lag price.  Hard gate in calmer regimes preserves structural
        # quality requirements without globally softening the path.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        has_smc_context = bool(fvgs or orderblocks)
        fvg_penalty = 0.0
        if not has_smc_context:
            if regime_upper not in _FAST_BEARISH_REGIMES:
                return self._reject("missing_fvg_or_orderblock")  # Hard gate in non-fast regimes (behaviour unchanged)
            fvg_penalty = 8.0  # Soft penalty in fast regimes instead of hard block

        # Breakdown candle volume ≥ _VSB_BREAKOUT_VOL_MULT × rolling average
        # (env-overridable per B8; was hardcoded 2.0).  Validates the surge on
        # the actual closed breakdown candle.  Shares the constant with VSB
        # since both paths are surge-confirmation gates of the same shape.
        if breakdown_vol < _VSB_BREAKOUT_VOL_MULT * rolling_avg:
            return self._reject("volume_spike_missing")

        # Method-specific SL/TP.
        # Pre-fix anchored SL purely to swing_low (`swing_low * 1.008`), which
        # creates absurdly tight stops when close has bounced deep:
        #   close at 0.30% above swing_low → sl_dist = 0.50% (tight)
        #   close at 0.60% above swing_low → sl_dist = 0.20% (dangerous)
        #   close at 0.75% above swing_low → sl_dist = 0.05% (< spread!)
        # The structural intent ("SL just above the broken support") is right,
        # but the geometry must respect (a) ATR-based volatility and (b) a
        # close-relative minimum.  Take the HIGHER (further-from-close, since
        # this is a SHORT) of two anchors:
        #   - structural ceiling: 0.8% above swing_low (anti-bear-trap)
        #   - close-relative ceiling: max(0.8% of close, 1.0×ATR) above close
        # Final SL is the HIGHER of these (further from close → wider, never
        # tighter).  Mirrors the VSB fix in #250.
        atr_val = ind.get("atr_last", close * 0.002)
        structural_sl = swing_low_level * (1 + 0.008)
        close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
        sl = max(structural_sl, close_rel_ceiling)
        sl_dist = abs(close - sl)
        if sl_dist <= 0 or sl <= close:
            return self._reject("invalid_sl_geometry")

        # TP: measured move downward projection (window aligned with swing low window)
        base_of_range = max(float(h) for h in highs[-26:-6]) if len(highs) >= 26 else close * 1.02
        measured_move = base_of_range - swing_low_level
        if measured_move <= 0:
            measured_move = sl_dist * 2.0

        tp1 = close - measured_move
        tp2 = close - measured_move * 1.5
        tp3 = close - measured_move * 2.0

        profile = smc_data.get("pair_profile")
        # atr_val already computed above for SL.
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=Direction.SHORT,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="BRKDN",
            atr_val=atr_val,
            setup_class="BREAKDOWN_SHORT",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # Override with method-specific structural SL and measured-move TPs
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Stamp the validated breakdown-candle surge ratio so the scoring engine
        # scores the volume dimension off the surge, not the low-volume dead-cat
        # bounce entry candle.  rolling_avg > 0 is guaranteed by the gate above.
        sig.breakout_volume_ratio = breakdown_vol / rolling_avg if rolling_avg > 0 else 0.0

        # Pre-score confidence annotation (established pattern for all evaluators).
        # All evaluators in this family add a path-specific base boost to sig.confidence
        # before returning.  The scanner's _prepare_signal() pipeline overwrites this
        # value three times (legacy confidence → score_signal_components →
        # composite scoring engine) so this mutation does NOT affect the final signal
        # confidence and does NOT bypass or double-count the family-aware scoring engine.
        # Quality differentiation (premium bounce zone, SMC context) is expressed
        # correctly via the soft_penalty_total system below, which the scanner deducts
        # post-scoring, and via the scoring engine's own _score_smc(fvg_zones=...) and
        # _score_volume() dimensions that already capture these signals independently.
        sig.confidence = min(100.0, sig.confidence + 8.0)

        # Accumulate soft penalties — the scanner deducts these from confidence after
        # the composite scoring pass, preserving the separation between hard gates and
        # soft quality adjustments.
        total_penalty = bounce_penalty + rsi_penalty + fvg_penalty
        if total_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

        return sig

    # ------------------------------------------------------------------
    # MOVER_TREND_PULLBACK path
    # ------------------------------------------------------------------
    @staticmethod
    def _mover_htf_aligned_fan_pct(
        indicators_1h: Optional[dict], direction: "Direction"
    ) -> float:
        """1H EMA21/50 fan width (%) when it AGREES with ``direction``, else 0.0.

        A multi-day mover's strength shows on the higher timeframe (15m×99 ≈ 24h
        is too short).  The fan is only credited when the 1H trend points the same
        way as the entry — a bearish 1H fan must not count as "strength" for a
        LONG.  Returns 0.0 on missing/invalid data so the caller falls back to the
        15m separation alone (fail-safe: never inflates strength)."""
        if not indicators_1h:
            return 0.0
        ema21 = indicators_1h.get("ema21_last")
        ema50 = indicators_1h.get("ema50_last")
        if ema21 is None or ema50 is None:
            return 0.0
        try:
            e21 = float(ema21)
            e50 = float(ema50)
        except (TypeError, ValueError):
            return 0.0
        if e50 <= 0:
            return 0.0
        aligned = (
            (direction == Direction.LONG and e21 > e50)
            or (direction == Direction.SHORT and e21 < e50)
        )
        if not aligned:
            return 0.0
        return abs(e21 - e50) / e50 * 100.0

    def _evaluate_mover_trend_pullback(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """MOVER_TREND_PULLBACK: on a confirmed top-mover, enter each pullback that
        tags the fast MA and reclaims in the trend direction.

        Rationale (Session 29, owner-driven from live mover charts): VSB/BDS catch
        only the *ignition* breakout+retest and go silent once a mover is trending,
        but the recurring edge on a strong mover is the *continuation* — price rides
        the MA stack (MA7>MA25>MA99 up, inverse down) and offers repeated
        pullback-to-MA re-entries.  This path catches those.  Direction comes from
        the MA stack itself (the move decides direction), so no aged HTF structure is
        required — which is exactly why TPE (1H-structure gated) cannot serve movers.

        "Mover" is defined by the MA-stack *separation* (MA7 vs MA99 >=
        ``MOVER_TP_MIN_STACK_SEP_PCT``), NOT by the mover-promotion bookkeeping:
        real movers (BTW, ESPORTS) enter the scan as universe/young pairs rather
        than via promotion, so the old ``is_mover_promoted`` gate locked the path
        out of its own targets.  The separation gate captures a genuine strong run
        wherever the pair sits, while rejecting gently-trending blue chips (TPE's
        domain).  Live by default in the testing phase
        (``MOVER_TREND_PULLBACK_ENABLED=true``); set the flag false to fall back to
        shadow-only (``[SHADOW] MOVER_TREND_PULLBACK_WOULD_FIRE`` log, no signal).
        """
        tf = candles.get("15m")
        need = MOVER_TP_MA_SLOW + 2
        if tf is None or len(tf.get("close", [])) < need:
            return self._reject("insufficient_candles")
        closes = [float(c) for c in tf.get("close", [])]
        highs = [float(h) for h in tf.get("high", [])]
        lows = [float(low) for low in tf.get("low", [])]
        if len(closes) < need or len(highs) < need or len(lows) < need:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        def _sma(vals: list, n: int) -> float:
            return sum(vals[-n:]) / n

        ma_fast = _sma(closes, MOVER_TP_MA_FAST)
        ma_mid = _sma(closes, MOVER_TP_MA_MID)
        ma_slow = _sma(closes, MOVER_TP_MA_SLOW)
        close = closes[-1]
        if min(close, ma_fast, ma_mid, ma_slow) <= 0:
            return self._reject("insufficient_candles")

        # Trend from the MID/SLOW MAs (MA25 vs MA99) — NOT the full three-MA stack.
        # This path enters on a pullback that, by design, tags the FAST MA — and a
        # pullback routinely dips MA7 toward/below MA25, so demanding a clean
        # ma_fast>ma_mid>ma_slow stack on the pullback bar contradicted the buy-the-
        # dip thesis and was the path's #1 generation reject (no_ma_stack ~45%).
        # The mid/slow pair holds the established trend through a fast-MA pullback
        # (§3.3: trend on the slower context, entry timing on the fast MA below).
        if ma_mid > ma_slow:
            direction = Direction.LONG
        elif ma_mid < ma_slow:
            direction = Direction.SHORT
        else:
            return self._reject("no_ma_stack")

        # Mover gate: require a strong run.  Measure strength on the WIDER of the
        # 15m MA7↔MA99 separation and the direction-aligned 1H EMA21/50 fan.  A
        # multi-day mover (SYNUSDT: +300%/7d) compresses its 15m stack on a pullback
        # (MA7↔MA99 ~1.5%) while the 1H/4H fan stays wide — reading strength off the
        # 15m alone tripped mover_run_too_small and locked the path out of exactly
        # the movers it targets.  15m×99 ≈ 24h is too short to size a multi-day run;
        # the 1H fan captures it (§3.3).  Still self-contained — no promotion
        # bookkeeping — so it catches universe/young movers (BTW/ESPORTS).
        sep_15m_pct = abs(ma_fast - ma_slow) / ma_slow * 100.0
        htf_fan_pct = self._mover_htf_aligned_fan_pct(indicators.get("1h"), direction)
        stack_sep_pct = max(sep_15m_pct, htf_fan_pct)
        if stack_sep_pct < MOVER_TP_MIN_STACK_SEP_PCT:
            return self._reject("mover_run_too_small")

        # ── Entry triggers ──────────────────────────────────────────────────
        # A strong mover offers several continuation re-entries; fire on the first
        # that matches in priority order (cleanest / best-R shape first) and stamp
        # which one fired (`entry_trigger`) so per-trigger win-rate is measurable.
        #   1) fast_pullback — shallow dip tags SMA7, this bar reclaims it.
        #   2) deep_pullback — deeper dip tags SMA25, this bar reclaims the mid MA
        #      (better price; SL drops below the slow MA, the trend anchor).
        #   3) consol_break  — no pullback: a tight micro-range breaks in-trend,
        #      guarded against chasing (holds fast MA, not over-extended, volume).
        band = MOVER_TP_PULLBACK_BAND_PCT / 100.0
        prev_high = highs[-2]
        prev_low = lows[-2]
        atr_val = (
            indicators.get("15m", {}).get("atr_last")
            or indicators.get("5m", {}).get("atr_last")
            or close * 0.004
        )
        buf = atr_val * MOVER_TP_SL_BUFFER_ATR
        vols = [float(v) for v in tf.get("volume", [])]

        trigger = ""
        sl = 0.0
        if direction == Direction.LONG:
            if prev_low <= ma_fast * (1.0 + band) and close > ma_fast and close > closes[-2]:
                trigger = "fast_pullback"
                sl = min(ma_mid, prev_low) - buf
            elif (
                MOVER_TP_TRIGGER_DEEP_ENABLED
                and prev_low <= ma_mid * (1.0 + band)
                and close > ma_mid
                and close > closes[-2]
            ):
                trigger = "deep_pullback"
                sl = min(ma_slow, prev_low) - buf
            elif MOVER_TP_TRIGGER_CONSOL_ENABLED:
                cb = self._mover_consol_break(
                    Direction.LONG, close, closes, highs, lows, vols, ma_fast, atr_val
                )
                if cb is not None:
                    trigger = "consol_break"
                    sl = cb - buf
            if not trigger:
                if prev_low > ma_fast * (1.0 + band) and prev_low > ma_mid * (1.0 + band):
                    return self._reject("no_pullback_tag")
                return self._reject("no_reclaim")
            if sl >= close:
                return self._reject("invalid_sl_geometry")
            sl_dist = close - sl
            tp1 = close + sl_dist * 1.0
            tp2 = close + sl_dist * 1.6
            tp3 = close + sl_dist * 2.5
        else:
            if prev_high >= ma_fast * (1.0 - band) and close < ma_fast and close < closes[-2]:
                trigger = "fast_pullback"
                sl = max(ma_mid, prev_high) + buf
            elif (
                MOVER_TP_TRIGGER_DEEP_ENABLED
                and prev_high >= ma_mid * (1.0 - band)
                and close < ma_mid
                and close < closes[-2]
            ):
                trigger = "deep_pullback"
                sl = max(ma_slow, prev_high) + buf
            elif MOVER_TP_TRIGGER_CONSOL_ENABLED:
                cb = self._mover_consol_break(
                    Direction.SHORT, close, closes, highs, lows, vols, ma_fast, atr_val
                )
                if cb is not None:
                    trigger = "consol_break"
                    sl = cb + buf
            if not trigger:
                if prev_high < ma_fast * (1.0 - band) and prev_high < ma_mid * (1.0 - band):
                    return self._reject("no_pullback_tag")
                return self._reject("no_reclaim")
            if sl <= close:
                return self._reject("invalid_sl_geometry")
            sl_dist = sl - close
            tp1 = close - sl_dist * 1.0
            tp2 = close - sl_dist * 1.6
            tp3 = close - sl_dist * 2.5

        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")

        # Live/shadow is ops-controlled (runtime tunable; boot default = the
        # env flag).  When shadowed, log a [SHADOW] line to size the
        # opportunity instead of emitting a live signal.
        if not self._mover_path_live(
            "mover_trend_pullback_live", MOVER_TREND_PULLBACK_ENABLED
        ):
            log.info(
                "[SHADOW] MOVER_TREND_PULLBACK_WOULD_FIRE: symbol={} dir={} "
                "trigger={} close={:.6f} ma_fast={:.6f} ma_mid={:.6f} ma_slow={:.6f} "
                "sl={:.6f} sl_dist_pct={:.3f}",
                symbol,
                "LONG" if direction == Direction.LONG else "SHORT",
                trigger, close, ma_fast, ma_mid, ma_slow, sl, sl_dist / close * 100.0,
            )
            return self._reject("shadow_mode")

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="MVRTP",
            atr_val=atr_val,
            setup_class="MOVER_TREND_PULLBACK",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # Method-specific structural SL + R-multiple TP ladder.
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # The mover MA-stack IS the higher-context trend, so credit full regime
        # affinity via the trend-pullback family scoring path (§3.6a); the volume
        # dimension floors at neutral (a pullback entry is low-volume by design).
        sig.htf_trend_aligned = True
        sig.entry_trigger = trigger
        sig.confidence = min(100.0, sig.confidence + 8.0)
        # Entry-time feature stamp (2026-08-01, owner: "taking entry is matter…
        # what if we add some more data to that").  This path decides on price
        # against three SMAs and one ATR; smc_data has been carrying CVD, book
        # depth, funding, liquidation clusters and the level book past it all
        # along.  Record what they said here — where the facts become true and
        # nowhere else can recover them — and apply none of it.  Nothing below
        # reads these values; the signal returned is byte-identical either way.
        try:
            from src import entry_features as _ef

            _ef.stamp(
                sig,
                # sig.entry_regime is still "" here — the scanner writes it in
                # _populate_signal_context, which runs after this returns. Pass
                # the label the evaluator was given (2026-08-01).
                regime=regime,
                features=_ef.capture(
                    symbol=symbol,
                    direction_is_long=(direction == Direction.LONG),
                    entry=close,
                    sl_dist=sl_dist,
                    tp1=tp1,
                    trigger=trigger,
                    tf=tf,
                    # The literal this evaluator opens with: candles.get("15m").
                    tf_name="15m",
                    atr=atr_val,
                    smc_data=smc_data,
                    # The MA the trigger is defined against on this path.
                    entry_ref=ma_fast,
                    entry_ref_name="sma7_15m",
                    ma_slow=ma_slow,
                    stack_sep_pct=stack_sep_pct,
                    # The 15m term of the mover gate on its own. `stack_sep_pct`
                    # above is `max(this, the 1H fan)`, so on its own it cannot
                    # say which of the two cleared the floor — and a candidate
                    # carried entirely by the 1H fan is a run that has stopped
                    # moving on the timeframe this path trades.
                    extras={"sep_15m_pct": float(sep_15m_pct)},
                    # The argument 19 of 20 call sites omit: this path calls
                    # _pass_basic_filters WITHOUT `profile`, so the pair-tier
                    # liquidity/spread adjustment is inert for 94% of the book.
                    # Stamp what it *would* have said; changing the live call
                    # changes what emits, which is dark-first + sign-off.
                    profile_would_reject=(
                        not self._pass_basic_filters(
                            spread_pct, volume_24h_usd, regime=regime, profile=profile
                        )
                        if profile is not None
                        else None
                    ),
                ),
            )
        except Exception as _exc:  # noqa: BLE001 — never let a stamp kill a scan
            from src import fail_open as _fo

            _fo.record("scalp.mvrtp_entry_features", _exc)
        log.info(
            "MOVER_TP_FIRED: symbol={} dir={} trigger={} close={:.6f} "
            "sl_dist_pct={:.3f} conf={:.1f}",
            symbol,
            "LONG" if direction == Direction.LONG else "SHORT",
            trigger, close, sl_dist / close * 100.0, sig.confidence,
        )
        return sig

    # ────────────────────────────────────────────────────────────────────────
    # MOVER_AVWAP_SCALP — anchored-VWAP continuation scalp (2026-06-28)
    # ────────────────────────────────────────────────────────────────────────
    def _evaluate_mover_avwap_scalp(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """MOVER_AVWAP_SCALP: scalp a confirmed mover via the VWAP anchored at the
        move's origin, entered WITH the AVWAP slope on a pullback to it.

        The professional mover-scalp standard (snappchart / TrendSpider /
        trademomentum VWAP-momentum playbooks): the anchored VWAP is the average
        price every participant in the move paid, so a pullback to it is where the
        trend reloads. Direction is set by the AVWAP slope ("rising VWAP = long
        only, falling = short only" — don't fight the tape) and a close decisively
        through the AVWAP against the trend ends the thesis. Anchor = the swing
        extreme over ``MOVER_AVWAP_ANCHOR_LOOKBACK`` bars (the leg's origin); the
        AVWAP is ``compute_vwap`` over ``candles[anchor:]``. Live by default;
        ``MOVER_AVWAP_SCALP_ENABLED=false`` → shadow-only log.
        """
        tf = candles.get(MOVER_AVWAP_TF)
        lookback = MOVER_AVWAP_ANCHOR_LOOKBACK
        need = lookback + 2
        if tf is None or len(tf.get("close", [])) < need:
            return self._reject("insufficient_candles")
        closes = [float(c) for c in tf.get("close", [])]
        highs = [float(h) for h in tf.get("high", [])]
        lows = [float(low) for low in tf.get("low", [])]
        vols = [float(v) for v in tf.get("volume", [])]
        if min(len(closes), len(highs), len(lows), len(vols)) < need:
            return self._reject("insufficient_candles")
        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")
        close = closes[-1]
        if close <= 0:
            return self._reject("insufficient_candles")

        # ── Direction from the recent leg; anchor at its origin swing ──────────
        win_h = highs[-lookback:]
        win_l = lows[-lookback:]
        anchor_high_off = max(range(lookback), key=lambda i: win_h[i])
        anchor_low_off = min(range(lookback), key=lambda i: win_l[i])
        swing_high = win_h[anchor_high_off]
        swing_low = win_l[anchor_low_off]
        if swing_low <= 0 or swing_high <= 0:
            return self._reject("insufficient_candles")
        # Down-leg: a swing high earlier, price far below it now → SHORT, anchor at
        # the high. Up-leg: a swing low earlier, price far above it now → LONG.
        down_move = (swing_high - close) / swing_high * 100.0
        up_move = (close - swing_low) / swing_low * 100.0
        if (down_move >= up_move and down_move >= MOVER_AVWAP_MIN_MOVE_PCT
                and anchor_high_off < anchor_low_off):
            direction = Direction.SHORT
            anchor_off = anchor_high_off
        elif (up_move > down_move and up_move >= MOVER_AVWAP_MIN_MOVE_PCT
                and anchor_low_off < anchor_high_off):
            direction = Direction.LONG
            anchor_off = anchor_low_off
        else:
            return self._reject("no_mover_leg")

        anchor_idx = len(closes) - lookback + anchor_off
        seg_h, seg_l, seg_c, seg_v = (
            highs[anchor_idx:], lows[anchor_idx:], closes[anchor_idx:], vols[anchor_idx:],
        )
        k = MOVER_AVWAP_SLOPE_LOOKBACK
        if len(seg_c) < k + 2:
            return self._reject("anchor_too_recent")

        avwap_res = compute_vwap(seg_h, seg_l, seg_c, seg_v)
        avwap_prev_res = compute_vwap(seg_h[:-k], seg_l[:-k], seg_c[:-k], seg_v[:-k])
        if avwap_res is None or avwap_prev_res is None:
            return self._reject("avwap_unavailable")
        avwap = avwap_res.vwap
        slope_pct = (avwap - avwap_prev_res.vwap) / close * 100.0

        # ── Slope filter: trade WITH the AVWAP slope only ──────────────────────
        if direction == Direction.LONG and slope_pct < MOVER_AVWAP_SLOPE_MIN_PCT:
            return self._reject("avwap_slope_against")
        if direction == Direction.SHORT and slope_pct > -MOVER_AVWAP_SLOPE_MIN_PCT:
            return self._reject("avwap_slope_against")

        # ── Pullback-to-AVWAP entry (continuation), volume-confirmed ───────────
        band = MOVER_AVWAP_PULLBACK_BAND_PCT / 100.0
        prev_high = highs[-2]
        prev_low = lows[-2]
        atr_val = (
            indicators.get(MOVER_AVWAP_TF, {}).get("atr_last")
            or indicators.get("5m", {}).get("atr_last")
            or close * 0.004
        )
        buf = atr_val * MOVER_AVWAP_SL_BUFFER_ATR
        recent_vols = seg_v[-20:] if len(seg_v) >= 20 else seg_v
        avg_vol = (sum(recent_vols[:-1]) / (len(recent_vols) - 1)) if len(recent_vols) > 1 else 0.0
        vol_ok = avg_vol <= 0 or vols[-1] >= avg_vol * MOVER_AVWAP_VOL_MULT

        trigger = ""
        sl = 0.0
        if direction == Direction.LONG:
            if prev_low <= avwap * (1.0 + band) and close > avwap and close > closes[-2]:
                if not vol_ok:
                    return self._reject("avwap_reclaim_no_volume")
                trigger = "avwap_reclaim"
                sl = min(avwap, prev_low) - buf
            if not trigger:
                if prev_low > avwap * (1.0 + band):
                    return self._reject("no_avwap_tag")
                return self._reject("no_avwap_reclaim")
            if sl >= close:
                return self._reject("invalid_sl_geometry")
            sl_dist = close - sl
            tp1, tp2, tp3 = close + sl_dist, close + sl_dist * 1.6, close + sl_dist * 2.5
        else:
            if prev_high >= avwap * (1.0 - band) and close < avwap and close < closes[-2]:
                if not vol_ok:
                    return self._reject("avwap_reclaim_no_volume")
                trigger = "avwap_reclaim"
                sl = max(avwap, prev_high) + buf
            if not trigger:
                if prev_high < avwap * (1.0 - band):
                    return self._reject("no_avwap_tag")
                return self._reject("no_avwap_reclaim")
            if sl <= close:
                return self._reject("invalid_sl_geometry")
            sl_dist = sl - close
            tp1, tp2, tp3 = close - sl_dist, close - sl_dist * 1.6, close - sl_dist * 2.5

        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")

        # Live/shadow is ops-controlled (runtime tunable; boot default = the
        # env flag).
        if not self._mover_path_live(
            "mover_avwap_scalp_live", MOVER_AVWAP_SCALP_ENABLED
        ):
            log.info(
                "[SHADOW] MOVER_AVWAP_SCALP_WOULD_FIRE: symbol={} dir={} close={:.6f} "
                "avwap={:.6f} slope_pct={:.3f} sl={:.6f} sl_dist_pct={:.3f}",
                symbol, "LONG" if direction == Direction.LONG else "SHORT",
                close, avwap, slope_pct, sl, sl_dist / close * 100.0,
            )
            return self._reject("shadow_mode")

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="MVAVW",
            atr_val=atr_val,
            setup_class="MOVER_AVWAP_SCALP",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("signal_build_failed")
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # The AVWAP slope IS the higher-context trend confirmation.
        sig.htf_trend_aligned = True
        sig.entry_trigger = trigger
        sig.confidence = min(100.0, sig.confidence + 8.0)
        # Entry-time feature stamp (2026-08-01, owner: "…especially on Trend
        # pullback EMA and mover AVWAP").
        #
        # This path is not blind the way MVRTP is — it already gates on volume
        # (`vol_ok`) and on AVWAP slope.  What it does not have is any sense of
        # *where in the move it is*.  The anchor is computed and then used only
        # to produce a VWAP: how many bars ago the leg started, how far it has
        # already travelled, and how many times price has already returned to
        # the anchor are all available at this point and none of them is
        # consulted or recorded.  A first pullback into a 6-bar-old leg and a
        # fourth pullback into a 90-bar-old one are the same object here.
        #
        # That matters for this data specifically: `execution:overextended` is
        # the gate carried past on 21 of the 65 dark rows, and `leg_move_pct` is
        # the quantity that gate is about.
        #
        # `vol_ratio_at_trigger` and `avwap_slope_pct` are the exact values the
        # live gates threshold on, so recording them makes those thresholds
        # checkable instead of trusted.  `tp1_r_multiple` will read 1.000 on
        # every row here (tp1 = close +/- sl_dist) — stamped anyway, so the
        # constant is visible in the data rather than being something a reader
        # has to know from the source.
        try:
            from src import entry_features as _ef

            _ef.stamp(
                sig,
                regime=regime,
                features=_ef.capture(
                    symbol=symbol,
                    direction_is_long=(direction == Direction.LONG),
                    entry=close,
                    sl_dist=sl_dist,
                    tp1=tp1,
                    trigger=trigger,
                    tf=tf,
                    tf_name=MOVER_AVWAP_TF,
                    atr=atr_val,
                    smc_data=smc_data,
                    entry_ref=avwap,
                    entry_ref_name="avwap_anchored",
                    profile_would_reject=(
                        not self._pass_basic_filters(
                            spread_pct, volume_24h_usd, regime=regime, profile=profile
                        )
                        if profile is not None
                        else None
                    ),
                    extras={
                        # Bars since the leg's origin swing — the anchor's age,
                        # which is what makes an anchored VWAP mean anything.
                        "anchor_age_bars": float(len(closes) - anchor_idx),
                        # How far the move has already run, the same number the
                        # MIN_MOVE_PCT floor is applied to and nothing caps.
                        "leg_move_pct": float(
                            up_move if direction == Direction.LONG else down_move
                        ),
                        "avwap_touches_in_leg": _ef.anchor_touch_count(
                            seg_h, seg_l, avwap,
                            band_pct=MOVER_AVWAP_PULLBACK_BAND_PCT,
                        ),
                        "avwap_slope_pct": float(slope_pct),
                        "vol_ratio_at_trigger": (
                            float(vols[-1]) / avg_vol if avg_vol > 0 else None
                        ),
                    },
                ),
            )
        except Exception as _exc:  # noqa: BLE001 — never let a stamp kill a scan
            from src import fail_open as _fo

            _fo.record("scalp.mvavw_entry_features", _exc)
        log.info(
            "MOVER_AVWAP_FIRED: symbol={} dir={} close={:.6f} avwap={:.6f} "
            "slope_pct={:.3f} sl_dist_pct={:.3f} conf={:.1f}",
            symbol, "LONG" if direction == Direction.LONG else "SHORT",
            close, avwap, slope_pct, sl_dist / close * 100.0, sig.confidence,
        )
        return sig

    @staticmethod
    def _mover_consol_break(
        direction: "Direction",
        close: float,
        closes: list,
        highs: list,
        lows: list,
        vols: list,
        ma_fast: float,
        atr_val: float,
    ) -> Optional[float]:
        """Guarded consolidation-break trigger for a mover that grinds without
        pulling back to the MA.  Returns the structural SL anchor (consolidation
        low for LONG / high for SHORT) when ALL guards pass, else None.

        The continuation-pattern literature is explicit that a naive "chase the
        breakout" entry is the classic mistake; this fires only when it is NOT
        extended.  Guards:
          • tight K-bar micro-range (height <= MOVER_TP_CONSOL_RANGE_ATR × ATR) —
            a wide range is the move itself, not a base;
          • this bar breaks the range extreme in the trend direction;
          • price holds the fast MA and is not over-extended beyond it
            (<= MOVER_TP_BREAKOUT_EXT_ATR × ATR) — keeps us off parabolic chases;
          • breakout-bar volume >= MOVER_TP_BREAKOUT_VOL_MULT × the window average
            (a break on weak volume "is almost certainly a fake-out").
        """
        k = MOVER_TP_CONSOL_LOOKBACK
        if atr_val <= 0 or k < 2 or len(closes) < k + 1:
            return None
        win_highs = highs[-(k + 1):-1]
        win_lows = lows[-(k + 1):-1]
        if not win_highs or not win_lows:
            return None
        consol_high = max(win_highs)
        consol_low = min(win_lows)
        if (consol_high - consol_low) > MOVER_TP_CONSOL_RANGE_ATR * atr_val:
            return None  # range too wide to be a flag/base
        # Volume confirmation on the breakout bar vs the consolidation-window avg.
        if len(vols) >= k + 1:
            win_vols = vols[-(k + 1):-1]
            avg_vol = sum(win_vols) / len(win_vols) if win_vols else 0.0
            if avg_vol > 0 and vols[-1] < MOVER_TP_BREAKOUT_VOL_MULT * avg_vol:
                return None
        ext = MOVER_TP_BREAKOUT_EXT_ATR * atr_val
        if direction == Direction.LONG:
            if close <= consol_high:        # must break the range up
                return None
            if close < ma_fast:             # must hold the fast MA (continuation)
                return None
            if (close - ma_fast) > ext:     # anti-extension: not a parabolic chase
                return None
            return consol_low
        if close >= consol_low:             # SHORT: must break the range down
            return None
        if close > ma_fast:
            return None
        if (ma_fast - close) > ext:
            return None
        return consol_high

    # ------------------------------------------------------------------
    # OPENING_RANGE_BREAKOUT path
    # First 4 candles of London/NY session form a range; breakout fires on
    # close beyond range_high/low with volume + EMA alignment + SMC basis.
    # ------------------------------------------------------------------

    def _evaluate_opening_range_breakout(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """OPENING_RANGE_BREAKOUT: session opening-range breakout with SMC basis."""
        # PR-06: disabled by default until rebuilt with true session-opening-range
        # logic.  The current proxy (last-8-bar window) is not institutional-grade.
        # Re-enable explicitly via SCALP_ORB_ENABLED=true in .env.
        # Telemetry: report `feature_disabled` (truthful) rather than the
        # misleading `regime_blocked` token which conflated two distinct
        # rejection causes — the dormant flag check vs. an actual regime gate.
        if not SCALP_ORB_ENABLED:
            return self._reject("feature_disabled")
        now_hour = datetime.now(timezone.utc).hour
        # Only active during London (07:00–08:59 UTC) or NY (12:00–13:59 UTC)
        in_london = 7 <= now_hour < 9
        in_ny = 12 <= now_hour < 14
        if not (in_london or in_ny):
            return self._reject("regime_blocked")

        regime_upper = regime.upper() if regime else ""
        if regime_upper in ("QUIET", "RANGING"):
            return self._reject("regime_blocked")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        volumes = m5.get("volume", [])
        if len(closes) < 20 or len(highs) < 20 or len(lows) < 20 or len(volumes) < 21:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        # Opening range = the 4 candles immediately before the most recent 4,
        # acting as a proxy for the first 4 candles of the session window.
        range_highs = [float(h) for h in highs[-8:-4]]
        range_lows = [float(l) for l in lows[-8:-4]]
        if not range_highs or not range_lows:
            return self._reject("breakout_not_found")
        range_high = max(range_highs)
        range_low = min(range_lows)
        range_height = range_high - range_low
        if range_height <= 0:
            return self._reject("breakout_not_found")

        close = float(closes[-1])
        if close <= 0:
            return self._reject("breakout_not_found")

        # Entry direction
        if close > range_high:
            direction = Direction.LONG
        elif close < range_low:
            direction = Direction.SHORT
        else:
            return self._reject("breakout_not_found")

        # Volume: rolling average must be non-degenerate.
        # Pre-fix this also demanded `volumes[-1] >= 1.5 × avg_vol` — but
        # volumes[-1] is the STILL-FORMING current 5m candle whose volume is
        # necessarily a fraction of a complete candle's eventual volume.
        # Demanding partial-candle volume exceed multiples of complete-candle
        # averages is the same unit-mismatch bug that was removed from
        # VSB / BDS (PRs #250 / #251).  Drop the partial-candle multiplier
        # check; the closed-candle activity is implicitly validated by the
        # `_pass_basic_filters` 24h-volume gate above and by the EMA-alignment
        # gate below.  When ORB is rebuilt with true session-anchored range
        # logic, re-introduce a closed-candle volume confirmation against the
        # actual breakout candle (whichever 5m candle first crossed the range).
        avg_vol = sum(float(v) for v in volumes[-21:-1]) / 20.0 if len(volumes) >= 21 else 0.0
        if avg_vol <= 0:
            return self._reject("volume_spike_missing")

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return self._reject("ema_alignment_reject")

        # EMA9 aligned in signal direction
        if direction == Direction.LONG and ema9 <= ema21:
            return self._reject("ema_alignment_reject")
        if direction == Direction.SHORT and ema9 >= ema21:
            return self._reject("ema_alignment_reject")

        # SMC basis: at least one FVG or orderblock
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return self._reject("missing_fvg_or_orderblock")

        # SL and TP — same close-relative+ATR floor pattern as VSB / BDS.
        # Pre-fix anchored SL purely to the opposite end of the opening range
        # with a 0.1% buffer (`range_low × 0.999` for LONG).  Two ways wrong:
        #   (1) On low-volatility pairs the 0.1% buffer is sub-spread.
        #   (2) When the breakout extends close past the opposite range edge,
        #       sl_dist could collapse arbitrarily — the 0.80% universal floor
        #       at `_enqueue_signal` would then clamp it, defeating the
        #       structural anchor.
        # Take the LOWER (further-from-close, since LONG) of:
        #   - structural floor: range_low − 0.1% (anti-bull-trap intent)
        #   - close-relative floor: max(0.8% of close, 1.0×ATR)
        # Mirror for SHORT: HIGHER of structural ceiling and close-relative ceiling.
        atr_val = ind.get("atr_last", close * 0.002)
        if direction == Direction.LONG:
            structural_sl = range_low * (1 - 0.001)
            close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
            sl = min(structural_sl, close_rel_floor)
            tp1 = close + range_height * 1.0
            tp2 = close + range_height * 1.5
            tp3 = close + range_height * 2.0
        else:
            structural_sl = range_high * (1 + 0.001)
            close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
            sl = max(structural_sl, close_rel_ceiling)
            tp1 = close - range_height * 1.0
            tp2 = close - range_height * 1.5
            tp3 = close - range_height * 2.0

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        profile = smc_data.get("pair_profile")
        # atr_val already computed above for SL.
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="ORB",
            atr_val=atr_val,
            setup_class="OPENING_RANGE_BREAKOUT",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        sig.confidence = min(100.0, sig.confidence + 5.0)
        return sig

    # ------------------------------------------------------------------
    # SR_FLIP_RETEST path
    # Prior swing high/low flipped; price retests with rejection candle.
    # ------------------------------------------------------------------

    @staticmethod
    def _sr_flip_ranging_shadow(reason: str, symbol: str, value: float) -> None:
        """Dark-mode telemetry for the RANGING SR_FLIP quality re-tighten.

        Logs what ``_SR_FLIP_RANGING_STRICT_ENABLED`` *would* additionally
        reject (and on which symbol/value) so the suppressed volume and its
        realized outcomes are measurable before the flag is flipped.  No-op on
        signal behaviour — it only emits a log line.
        """
        log.info(
            "[SHADOW] SR_FLIP_RANGING_STRICT: symbol={} reason={} value={:.4f} "
            "— would reject if enabled",
            symbol,
            reason,
            value,
        )

    def _evaluate_sr_flip_retest(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """SR_FLIP_RETEST: support/resistance flip retest with rejection candle.

        Refinements vs. original:
        - Flip detection window extended from 5 to 8 closed prior candles.  The current
          (still-forming) candle is excluded from the flip search, preserving true
          structural-retest semantics: the flip must be confirmed on a prior closed
          candle before the current candle can serve as the retest signal.  This
          accommodates retests that arrive 6–7 bars after the structural break — common
          in live crypto where the retest candle does not always immediately follow the
          breakout candle.
        - Retest proximity expanded from a 0.3% hard gate to a layered zone system.
          Premium zone (0–0.3% from flipped level) passes with no soft penalty.
          Extended zone (0.3%–0.6%) accumulates a +3.0 soft penalty, reflecting a
          messier but still-valid structural retest where price hasn't cleanly returned
          to the exact level.  Hard block beyond 0.6%.
        - Flip confirmation requires breakout-close acceptance, not wick-only breach:
          LONG needs a recent closed candle that breaks and closes above prior swing
          high; SHORT needs a recent closed candle that breaks and closes below prior
          swing low.
        - Rejection candle strictness remains layered soft/hard, but doji-style
          indecision candles are rejected.  The reclaim candle must show a minimum
          body-vs-range footprint before wick-quality is evaluated.
        - RSI hard gate relaxed from 70/30 to 80/20.  Borderline 70–79 (LONG) or
          21–30 (SHORT) attracts a +5.0 soft penalty instead of a hard block, because
          the initial flip move routinely pushes RSI to these levels without invalidating
          the structural retest thesis.
        - FVG / orderblock requirement converted to a +8.0 soft penalty in fast
          structural regimes (TRENDING_UP, TRENDING_DOWN, BREAKOUT_EXPANSION,
          STRONG_TREND) where SMC detection may lag fast price action.  Remains a hard
          gate in calm regimes (RANGING, etc.) to preserve structural quality.
        """
        regime_upper = regime.upper() if regime else ""
        # SR_FLIP_RETEST is structurally invalid in chaotic regimes — the
        # role-flip thesis depends on orderly price action around a structural
        # level.  Pre-fix only blocked "VOLATILE"; "VOLATILE_UNSUITABLE" slipped
        # through to rely on the scanner's regime gate, which works but is a
        # defence-in-depth gap.  REGIME_SETUP_COMPATIBILITY in
        # `signal_quality.py` already excludes SR_FLIP from VOLATILE_UNSUITABLE
        # — mirror that doctrine here.
        if regime_upper in ("VOLATILE", "VOLATILE_UNSUITABLE"):
            return self._reject("regime_blocked")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 55:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        opens = m5.get("open", [])
        if len(closes) < 55 or len(highs) < 55 or len(lows) < 55 or len(opens) < 1:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        close = float(closes[-1])
        if close <= 0:
            return self._reject("invalid_price")
        prev_close = float(closes[-2])

        # Structural level identification.
        # Prior window ([-50:-9]) provides 41 candles of genuine prior structure.
        # Flip search window ([-9:-1]) covers the 8 most recent *closed* candles,
        # explicitly excluding the current (still-forming) candle at [-1].  This
        # preserves true structural-retest semantics: the flip must be confirmed on a
        # prior closed candle before the current candle can be treated as the retest.
        # Layout: [...prior (41) │ closed flip search (8) │ current (1)]
        #          highs[-50:-9]   highs[-9:-1]              highs[-1]
        # The 8-candle closed search window (up from 5) accommodates retests that
        # arrive 6–7 bars after the structural break.
        # Breakout confirmation is evaluated on the closed-candle window before the
        # immediate prior candle. The immediate prior candle is reserved for hold/reclaim
        # evidence in the retest sequence.
        recent_highs = [float(h) for h in highs[-9:-2]]
        recent_lows = [float(l) for l in lows[-9:-2]]
        recent_closes = [float(c) for c in closes[-9:-2]]
        recent_opens = [float(o) for o in opens[-9:-2]]
        recent_prev_closes = [float(c) for c in closes[-10:-3]]

        # ──────────────────────────────────────────────────────────────
        # HTF level sourcing (OWNER_BRIEF §3.4a — "HTF Structure, LTF Entry")
        # ──────────────────────────────────────────────────────────────
        # Pre-2026-05-17 SR_FLIP detected the swing level via ``_sr_detect_levels``
        # over the prior 41 5m candles (= ~3.4 hours of local extrema).  Truth-
        # report data showed 43% of SR_FLIP signals had MFE=0 — engine-called
        # direction; price never moved that way.  Root cause: the "level" was
        # a 5m local extremum, not a structurally significant HTF S/R.
        #
        # Post-2026-05-17 doctrine: source the level from the chartist-eye
        # LevelBook (1H/4h/1d swing pivots + VP zones, injected into smc_data
        # by the scanner per PR #410 / OWNER_BRIEF §3.4a).  Quality criterion
        # mirrors LSR's HTF POI anchor — accept CLUSTERED (multi-TF cluster,
        # len(source_tfs) >= 2) or VP_ANCHORED (source_tf == "vp") only;
        # single-TF and round-number-only levels are too noisy.
        #
        # Production scanner always sets ``level_book_levels`` to at least
        # ``[]`` after refresh.  The key-absent / None sentinel only triggers
        # in tests that build a synthetic ``smc_data`` without the scanner's
        # assembly pass — fall through to the legacy 5m pivot detector so
        # existing fixtures continue to pass.

        ind_early = indicators.get("5m", {})
        atr_for_levels = float(ind_early.get("atr_last") or close * 0.002)

        _lb_levels_raw = smc_data.get("level_book_levels")
        _htf_resistance: Optional[float] = None
        _htf_support: Optional[float] = None
        if _lb_levels_raw is not None:
            # Production path — LevelBook refreshed.  Pick the highest-scoring
            # qualifying RESISTANCE-type and SUPPORT-type level.  Doesn't
            # filter on above/below close — once a level is broken, current
            # price may be on either side of it, and the 5m break detection
            # below decides which direction the flip is.  ``_lb_levels_raw``
            # is sorted by descending score per LevelBook.get_levels(), so
            # we walk and take the first match per side.
            for _lv in _lb_levels_raw:
                _src_tfs = getattr(_lv, "source_tfs", None) or [
                    getattr(_lv, "source_tf", "")
                ]
                _is_clustered = (
                    isinstance(_src_tfs, list) and len(_src_tfs) >= 2
                )
                _is_vp_anchored = (
                    getattr(_lv, "source_tf", "") == "vp"
                    or "vp" in (_src_tfs or [])
                )
                if not (_is_clustered or _is_vp_anchored):
                    continue
                _lv_price = float(getattr(_lv, "price", 0.0) or 0.0)
                if _lv_price <= 0:
                    continue
                _lv_type = (getattr(_lv, "type", "") or "").lower()
                if _htf_resistance is None and _lv_type == "resistance":
                    _htf_resistance = _lv_price
                elif _htf_support is None and _lv_type == "support":
                    _htf_support = _lv_price
                if _htf_resistance is not None and _htf_support is not None:
                    break

        if _lb_levels_raw is not None and _htf_resistance is None and _htf_support is None:
            # LevelBook refreshed but no qualifying CLUSTERED / VP_ANCHORED
            # level on either side — strict doctrinal rejection.  Avoids the
            # pre-fix behaviour where the path fired on any 5m local extremum.
            return self._reject("no_htf_structural_level")

        if _lb_levels_raw is None:
            # Test / pre-warm fallback — preserve legacy 5m pivot detector so
            # the considerable existing test surface for SR_FLIP continues
            # to exercise the path.
            _sr_levels = _sr_detect_levels(
                highs=list(highs),
                lows=list(lows),
                closes=list(closes),
                opens=list(opens),
                atr=atr_for_levels,
                volume_poc=ind_early.get("volume_poc"),
                volume_vah=ind_early.get("volume_vah"),
                volume_val=ind_early.get("volume_val"),
            )
            _resistance_lv = _sr_levels["resistance"]
            _support_lv = _sr_levels["support"]
            prior_swing_high = _resistance_lv.price if _resistance_lv is not None else float("inf")
            prior_swing_low = _support_lv.price if _support_lv is not None else float("-inf")
        else:
            # HTF path — _resistance_lv / _support_lv stay None (level-quality
            # soft-penalty branch below treats this as "external HTF source").
            _resistance_lv = None
            _support_lv = None
            prior_swing_high = (
                _htf_resistance if _htf_resistance is not None else float("inf")
            )
            prior_swing_low = (
                _htf_support if _htf_support is not None else float("-inf")
            )

        # Bullish flip: require breakout-close acceptance above prior swing high.
        # The FIRST qualifying candle in the closed window is the break candle —
        # its index feeds the V2 volume/acceptance evidence checks below.
        _long_break_rel: Optional[int] = None
        for _bi, (h, c, o, prev_c) in enumerate(
            zip(recent_highs, recent_closes, recent_opens, recent_prev_closes)
        ):
            if (
                h > prior_swing_high
                and c > prior_swing_high
                and (o <= prior_swing_high or prev_c <= prior_swing_high)
            ):
                _long_break_rel = _bi
                break
        long_breakout_close_confirmed = _long_break_rel is not None
        # Bearish flip: require breakout-close acceptance below prior swing low.
        short_breakout_close_confirmed = any(
            l < prior_swing_low
            and c < prior_swing_low
            and (o >= prior_swing_low or prev_c >= prior_swing_low)
            for l, c, o, prev_c in zip(
                recent_lows,
                recent_closes,
                recent_opens,
                recent_prev_closes,
            )
        )

        # Whipsaw guard (long V2, S40): both directions confirming inside the
        # same 8-candle window means price whipped through BOTH structural
        # levels — that's chop around structure, not a flip.  V1 silently
        # resolved these LONG (the if-priority), feeding the bull-trap bleed.
        if long_breakout_close_confirmed and short_breakout_close_confirmed:
            return self._reject("whipsaw_flip")

        if long_breakout_close_confirmed:
            direction = Direction.LONG
            level = prior_swing_high
        elif short_breakout_close_confirmed:
            direction = Direction.SHORT
            level = prior_swing_low
        else:
            return self._reject("flip_close_not_confirmed")

        # Set only on the long side, read at the single return below. Declared
        # here so the short path — which never enters the block — still has it.
        _carry_long_dark = False

        # ── SR_FLIP long V2 (S40, issue #674) — trap-discriminating evidence ──
        # The long/short code is symmetric; the LONG side bled (19% win, every
        # regime) because a break above resistance in leveraged crypto is
        # disproportionately a bull trap, and V1 confirmed flips on pure price.
        # V2 demands what a trap can't fake: real volume on the break and real
        # acceptance above the level.  Both evidence checks run regardless of
        # the enable flag so the [SHADOW] line measures exactly the candidates
        # a re-enable would emit (stamp-and-shadow doctrine).
        if direction == Direction.LONG:
            # 1. Volume-backed break: breakout candle vs prior-20 mean.
            #    Fail-open when volume data is unavailable (warmup) — the
            #    acceptance-hold check below still applies.
            _break_abs = len(closes) - 9 + int(_long_break_rel or 0)
            _vols = m5.get("volume", [])
            _v2_vol_ok: Optional[bool] = None
            if len(_vols) > _break_abs and _break_abs >= 20:
                _base = [float(v) for v in _vols[_break_abs - 20 : _break_abs]]
                _base_mean = sum(_base) / len(_base) if _base else 0.0
                if _base_mean > 0:
                    _v2_vol_ok = (
                        float(_vols[_break_abs])
                        >= SR_FLIP_LONG_BREAK_VOL_MULT * _base_mean
                    )
            if _v2_vol_ok is False:
                return self._reject("long_break_volume_thin")
            # 2. Acceptance hold: closed candles above the level from the
            #    break through the last closed candle (break close counts).
            #    One poke above the level is not a flip.
            _closes_above = sum(
                1 for _c in closes[_break_abs:-1] if float(_c) > prior_swing_high
            )
            if _closes_above < SR_FLIP_LONG_MIN_HOLD_CLOSES:
                return self._reject("long_acceptance_not_held")
            # 3. Enable gate — while off, a V2-passing candidate is either
            #    carried into the dark lane (measured forward to a real TP1/SL
            #    with an R) or rejected outright, and the shadow line records
            #    which. Owner directive 2026-07-31: route these to the dark
            #    feed.
            #
            #    The carry deliberately does NOT publish here. This point sits
            #    before the 1H break confirmation and before the entire scanner
            #    chain — scoring, MTF, min_confidence, the context floors,
            #    level_still_in_play, staleness. The dark feed's central claim
            #    is that every row cleared all of that with one gate overridden;
            #    a row published from inside an evaluator would not have, and
            #    would quietly make that sentence false for the whole page. So
            #    the candidate keeps building and is diverted at the same single
            #    `signal_queue.put` site as every other dark row.
            if not SR_FLIP_LONG_ENABLED:
                _long_dark = dark_emission.will_admit(
                    "SR_FLIP_RETEST", dark_emission.GATE_SR_FLIP_LONG
                )
                log.info(
                    "[SHADOW] SR_FLIP_LONG_V2_WOULD_FIRE symbol={} level={:.6g} "
                    "vol_ok={} closes_above={} — long side disabled, {}",
                    symbol, level, _v2_vol_ok, _closes_above,
                    "carried dark" if _long_dark else "rejected",
                )
                if not _long_dark:
                    return self._reject("long_disabled")
                _carry_long_dark = True

        # 1H break confirmation (OWNER_BRIEF §3.4a — "HTF Structure, LTF
        # Entry").  Only enforced when the level came from LevelBook (HTF
        # path); the 5m-pivot fallback for test fixtures skips this check
        # since those fixtures already encode the break-and-retest on 5m.
        #
        # A genuine break-and-flip on a multi-TF S/R must show on the 1H
        # close — otherwise the 5m "break" is just an intra-1H wick that
        # gives the level back within the same hour.  Walk the last ~8
        # closed 1H candles; require at least one closed beyond the level
        # in the flip direction.
        if _lb_levels_raw is not None:
            _h1 = candles.get("1h") or {}
            _h1_closes = _h1.get("close") or []
            _h1_highs = _h1.get("high") or []
            _h1_lows = _h1.get("low") or []
            # Need at least one bar history beyond the current still-forming
            # bar (index -1) — skip the check when 1H data is unavailable
            # (early warmup window) to fail-open per soft-penalty doctrine.
            if len(_h1_closes) >= 2 and len(_h1_highs) >= 2 and len(_h1_lows) >= 2:
                _h1_lookback = min(len(_h1_closes) - 1, 8)
                _h1_closed_closes = [float(c) for c in _h1_closes[-1 - _h1_lookback:-1]]
                _h1_closed_highs = [float(h) for h in _h1_highs[-1 - _h1_lookback:-1]]
                _h1_closed_lows = [float(low_v) for low_v in _h1_lows[-1 - _h1_lookback:-1]]
                if direction == Direction.LONG:
                    _broke_on_1h = any(
                        h > level and c > level
                        for h, c in zip(_h1_closed_highs, _h1_closed_closes)
                    )
                else:
                    _broke_on_1h = any(
                        low_v < level and c < level
                        for low_v, c in zip(_h1_closed_lows, _h1_closed_closes)
                    )
                if not _broke_on_1h:
                    return self._reject("h1_break_not_confirmed")

        # HTF mismatch soft penalty — aligned with scalping doctrine
        # (OWNER_BRIEF §2.1a).  Counter-trend SR_FLIP setups are legitimate
        # scalp products: resistance held during an uptrend pullback is a
        # valid SHORT scalp, support held during a downtrend bounce is a
        # valid LONG scalp.  Hard-blocking these would eliminate ~half the
        # path's edge in correlated trending markets where top-75 USDT-M
        # pairs follow BTC.  Soft penalty (default 6.0 pts) when BOTH 1H
        # AND 4H oppose direction lets scoring decide whether the signal
        # clears the confidence-tier threshold.  Replaces the prior hard
        # `htf_direction_veto` reject (PR #266 → corrected by PR #269).
        sr_flip_htf_penalty = 0.0
        if _SR_FLIP_HTF_MISMATCH_PENALTY > 0:
            trend_1h = self._classify_htf_trend(indicators, candles, "1h")
            trend_4h = self._classify_htf_trend(indicators, candles, "4h")
            opposite = "BEARISH" if direction == Direction.LONG else "BULLISH"
            if trend_1h == opposite and trend_4h == opposite:
                sr_flip_htf_penalty = _SR_FLIP_HTF_MISMATCH_PENALTY  # both TFs oppose
            elif trend_4h == opposite:
                sr_flip_htf_penalty = _SR_FLIP_H4_ONLY_PENALTY  # 4H opposes, 1H aligned

        # Retest proximity gate — tier-dependent per §3.4a doctrine.
        # HTF LevelBook source (production path): tighter zones since
        # institutional levels deserve precise retest.  5m local-extremum
        # fallback (test path / pre-warm): keeps the legacy looser zones
        # so existing test fixtures continue exercising the path.
        #
        # HTF tier:
        #   premium <= 0.15% from level → no penalty
        #   extended 0.15% – 0.30%      → +3.0 soft penalty
        #   beyond  > 0.30%             → hard reject
        # 5m-fallback tier (legacy, pre-2026-05-17 values):
        #   premium <= 0.30%            → no penalty
        #   extended 0.30% – 0.60%      → +3.0 soft penalty
        #   beyond  > 0.60%             → hard reject
        if level <= 0:
            return self._reject("retest_out_of_zone")
        dist_from_level_pct = abs(close - level) / level
        _proximity_hard_max = 0.003 if _lb_levels_raw is not None else 0.006
        _proximity_premium = 0.0015 if _lb_levels_raw is not None else 0.003
        if dist_from_level_pct > _proximity_hard_max:
            return self._reject("retest_out_of_zone")
        retest_in_premium_zone = dist_from_level_pct <= _proximity_premium
        proximity_penalty = 0.0 if retest_in_premium_zone else 3.0

        # RANGING quality re-tighten: in dead-range chop an extended-zone retest
        # (price hasn't returned cleanly to the level) is the low-probability
        # variant driving the RANGING bleed.  Require a premium-zone retest in
        # RANGING; trending signals keep the wider zone.  Dark + [SHADOW].
        if regime_upper == "RANGING" and not retest_in_premium_zone:
            if _SR_FLIP_RANGING_STRICT_ENABLED:
                return self._reject("ranging_strict_extended_zone")
            self._sr_flip_ranging_shadow("extended_zone", symbol, dist_from_level_pct)

        # Rejection candle check — layered soft/hard gate replacing the original hard-50% rule.
        # A clear rejection wick (≥50% of candle body) is the ideal structural signal.
        # Borderline wicks (20%–50%) are weaker but still pass with a +4.0 soft penalty.
        # No meaningful wick (<20% of body) is hard-rejected — the candle shows no
        # structural push-back at the level.  Doji (zero body) always passes — indecision
        # at structure is a valid retest signature.
        last_open = float(opens[-1])
        last_high = float(highs[-1])
        last_low = float(lows[-1])

        # Entry-quality tightening: require reclaim/hold evidence across candles so
        # weak immediate-touch entries do not pass on a single tap.
        if direction == Direction.LONG:
            if prev_close <= level:
                return self._reject("reclaim_hold_failed")
            if close <= level * 1.0005:
                return self._reject("reclaim_hold_failed")
            if last_low > level * 1.0045:
                return self._reject("reclaim_hold_failed")
        else:
            if prev_close >= level:
                return self._reject("reclaim_hold_failed")
            if close >= level * 0.9995:
                return self._reject("reclaim_hold_failed")
            if last_high < level * 0.9955:
                return self._reject("reclaim_hold_failed")

        candle_body = abs(close - last_open)
        candle_range = max(last_high - last_low, 0.0)
        if candle_range <= 0:
            return self._reject("wick_quality_failed")
        if candle_body / candle_range < 0.12:
            return self._reject("wick_quality_failed")
        wick_penalty = 0.0
        if direction == Direction.LONG:
            lower_wick = last_open - last_low if last_open > last_low else close - last_low
            if lower_wick < 0.2 * candle_body:
                return self._reject("wick_quality_failed")
            if lower_wick < 0.5 * candle_body:
                wick_penalty = 4.0  # Borderline rejection — apply soft penalty
        else:
            upper_wick = last_high - last_open if last_high > last_open else last_high - close
            if upper_wick < 0.2 * candle_body:
                return self._reject("wick_quality_failed")
            if upper_wick < 0.5 * candle_body:
                wick_penalty = 4.0  # Borderline rejection — apply soft penalty

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return self._reject("ema_alignment_reject")

        if direction == Direction.LONG and ema9 <= ema21:
            return self._reject("ema_alignment_reject")
        if direction == Direction.SHORT and ema9 >= ema21:
            return self._reject("ema_alignment_reject")

        # RSI — layered soft/hard gate replacing the previous hard gate of 70/30.
        # Hard block at ≥80 (LONG) or ≤20 (SHORT): extreme exhaustion invalidates the
        # retest thesis regardless of structural clarity.
        # Borderline 70–79 (LONG) or 21–30 (SHORT): +5.0 soft penalty.  Initial flip
        # moves routinely push RSI to these levels without breaking the retest setup.
        # Optimal zones pass with no adjustment.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= 80.0:
                    return self._reject("rsi_reject")
                if rsi_val >= 70.0:
                    # RANGING quality re-tighten: don't chase an overbought
                    # retest in chop — revert the 70-79 soft band to a hard
                    # gate in RANGING only.  Dark + [SHADOW].
                    if regime_upper == "RANGING":
                        if _SR_FLIP_RANGING_STRICT_ENABLED:
                            return self._reject("ranging_strict_rsi")
                        self._sr_flip_ranging_shadow("rsi_band", symbol, rsi_val)
                    rsi_penalty = 5.0
            else:
                if rsi_val <= 20.0:
                    return self._reject("rsi_reject")
                if rsi_val <= 30.0:
                    if regime_upper == "RANGING":
                        if _SR_FLIP_RANGING_STRICT_ENABLED:
                            return self._reject("ranging_strict_rsi")
                        self._sr_flip_ranging_shadow("rsi_band", symbol, rsi_val)
                    rsi_penalty = 5.0

        # FVG / orderblock — soft penalty contributor in fast structural regimes where
        # SMC detection may lag fast price action.  Hard gate in calmer regimes preserves
        # structural quality requirements without globally softening the path.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        has_smc_context = bool(fvgs or orderblocks)
        fvg_penalty = 0.0
        if not has_smc_context:
            if regime_upper not in _FAST_STRUCTURAL_REGIMES:
                return self._reject("missing_fvg_or_orderblock")
            fvg_penalty = 8.0  # Soft penalty in fast structural regimes

        # SR_FLIP_RETEST invalidation must sit beyond reclaim failure structure, not a
        # flat percent from the flip level.
        atr_val = float(ind.get("atr_last", close * 0.002))
        atr_buffer = atr_val * 0.35
        level_buffer = level * 0.0015
        wick_overshoot = 0.0
        if direction == Direction.LONG:
            wick_overshoot = max(level - last_low, 0.0)
        else:
            wick_overshoot = max(last_high - level, 0.0)
        structural_failure_buffer = wick_overshoot + atr_val * 0.15
        invalidation_buffer = max(level_buffer, atr_buffer, structural_failure_buffer)
        if direction == Direction.LONG:
            invalidation_anchor = min(level, last_low)
            sl = invalidation_anchor - invalidation_buffer
        else:
            invalidation_anchor = max(level, last_high)
            sl = invalidation_anchor + invalidation_buffer

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # BUG FIX: Enforce minimum SL = max(1.0×ATR, 0.50% of close)
        # Structural SL from wick+buffer can be too tight (0.3-0.4%)
        # causing correct-direction signals to be wiped by normal noise
        min_sl_dist = max(
            atr_val * 1.0,                          # 1×ATR minimum
            close * self.config.sl_pct_range[0] / 100  # 0.50% minimum
        )
        if sl_dist < min_sl_dist:
            if direction == Direction.LONG:
                sl = close - min_sl_dist
            else:
                sl = close + min_sl_dist
            sl_dist = min_sl_dist

        # TP1: 20-candle swing high/low with floor at 1.2R.
        if direction == Direction.LONG:
            tp1 = max(float(h) for h in highs[-21:-1]) if len(highs) >= 21 else 0.0
            if tp1 <= close:
                tp1 = close + sl_dist * 1.5
            tp1 = max(tp1, close + sl_dist * 1.2)
        else:
            tp1 = min(float(low_val) for low_val in lows[-21:-1]) if len(lows) >= 21 else 0.0
            if tp1 >= close:
                tp1 = close - sl_dist * 1.5
            tp1 = min(tp1, close - sl_dist * 1.2)

        # ATR-adaptive TP1 cap (mirror of TPE pattern at line ~1264).
        # OWNER_BRIEF Audit-3 claimed this was deployed for SR_FLIP but the code
        # had only the 1.2R floor — no upper cap.  In trending markets the
        # 20-candle swing high can sit 5-10R from close, producing TP1 targets
        # that rarely get hit before the structural SL fires (a documented
        # contributor to the 100% SL rate in early-window monitoring).
        # Cap by ATR percentile:
        #   <40 (low ATR / accumulation):  TP1 ≤ 1.8R
        #   40-65 (median ATR):            TP1 ≤ 2.5R
        #   ≥65 (high ATR):                no cap (room to run)
        _rc_srflip = smc_data.get("regime_context")
        _atr_pct_srflip = _rc_srflip.atr_percentile if _rc_srflip else 50.0
        if _atr_pct_srflip < 40.0:
            _tp1_cap_srflip = sl_dist * 1.8
        elif _atr_pct_srflip < 65.0:
            _tp1_cap_srflip = sl_dist * 2.5
        else:
            _tp1_cap_srflip = None
        if _tp1_cap_srflip is not None:
            tp1 = (min(tp1, close + _tp1_cap_srflip) if direction == Direction.LONG
                   else max(tp1, close - _tp1_cap_srflip))

        # TP2: 4h target or fallback.  When the 4h max/min fails the
        # tp2-vs-tp1 monotonicity check, the fallback must enforce a real gap
        # above (LONG) / below (SHORT) tp1 — mirroring the FAILED_AUCTION_RECLAIM
        # pattern.  Pre-fix this branch could leave tp2 ≤ tp1 (collapse when
        # tp1 came from the same close + sl_dist*1.5 fallback, or inversion
        # when tp1 sat above the 1.5R fallback).
        candles_4h = candles.get("4h")
        if candles_4h and len(candles_4h.get("high", [])) >= 5:
            _4h_highs = candles_4h.get("high", [])
            _4h_lows = candles_4h.get("low", [])
            if direction == Direction.LONG:
                tp2 = max(float(h) for h in _4h_highs[-10:]) if _4h_highs else close + sl_dist * 1.5
                if tp2 <= tp1:
                    tp2 = max(close + sl_dist * 1.5, tp1 + sl_dist * 0.5)
            else:
                tp2 = min(float(low_val) for low_val in _4h_lows[-10:]) if _4h_lows else close - sl_dist * 1.5
                if tp2 >= tp1:
                    tp2 = min(close - sl_dist * 1.5, tp1 - sl_dist * 0.5)
        else:
            tp2 = close + sl_dist * 1.5 if direction == Direction.LONG else close - sl_dist * 1.5
            if direction == Direction.LONG and tp2 <= tp1:
                tp2 = tp1 + sl_dist
            if direction == Direction.SHORT and tp2 >= tp1:
                tp2 = tp1 - sl_dist

        tp3 = close + sl_dist * 3.5 if direction == Direction.LONG else close - sl_dist * 3.5

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="SRFLIP",
            atr_val=atr_val,
            setup_class="SR_FLIP_RETEST",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.sr_flip_level = round(level, 8)
        # Item #7 — level quality telemetry.  The fired-direction side of the
        # structural detector is the one that defines `level`.  Stored on the
        # Signal for performance tracking so we can measure per-quality SL rate
        # post-deploy and iterate on the algorithm based on real data.
        _lv_for_direction = _resistance_lv if direction == Direction.LONG else _support_lv
        sig.sr_flip_level_quality = _lv_for_direction.quality if _lv_for_direction else None
        sig.sr_flip_level_touches = _lv_for_direction.touch_count if _lv_for_direction else 0
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Pre-score confidence annotation (established pattern for all evaluators).
        # All evaluators in this family add a path-specific base boost to sig.confidence
        # before returning.  The scanner's _prepare_signal() pipeline overwrites this
        # value (legacy confidence → score_signal_components → composite scoring engine)
        # so this mutation does NOT affect the final signal confidence and does NOT
        # bypass or double-count the family-aware scoring engine.
        # Quality differentiation (proximity zone, wick quality, RSI, SMC context) is
        # expressed correctly via the soft_penalty_total system below, which the scanner
        # deducts post-scoring.
        sig.confidence = min(100.0, sig.confidence + 8.0)

        # Item #7 — level-quality soft penalty.  Biases scoring toward signals
        # backed by structurally-validated levels without introducing a hard gate.
        # Magnitudes are intentionally modest (A+ tier threshold is 80).
        #   CLUSTERED + >=3 touches  → -3.0 (bonus: strongest structural evidence)
        #   CLUSTERED + 2 touches    →  0.0 (neutral)
        #   VP_ANCHORED              →  0.0 (neutral)
        #   SCALAR_FALLBACK          → +5.0 (penalty: level is a guess)
        level_quality_penalty = 0.0
        if _lv_for_direction is not None:
            if _lv_for_direction.quality == "CLUSTERED" and _lv_for_direction.touch_count >= 3:
                level_quality_penalty = -3.0
            elif _lv_for_direction.quality == "SCALAR_FALLBACK":
                level_quality_penalty = 5.0

        # Accumulate soft penalties — the scanner deducts these from confidence after
        # the composite scoring pass, preserving the separation between hard gates and
        # soft quality adjustments.
        total_penalty = (
            proximity_penalty + wick_penalty + rsi_penalty + fvg_penalty
            + level_quality_penalty + sr_flip_htf_penalty
        )
        if total_penalty != 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

        # A long carried past the disable must leave here dark or not at all.
        # `will_admit` answered sixty lines ago and is not permission: the lane
        # can be toggled off mid-evaluation, and `mark` records a failure rather
        # than raising. So the mark is verified, not assumed — an unmarked
        # candidate would reach `signal_queue.put` and put a path measured at
        # −21.8% back in front of paid subscribers with no owner sign-off. This
        # branch is the safety property for the long side; it fails closed.
        if _carry_long_dark:
            dark_emission.mark(sig, dark_emission.GATE_SR_FLIP_LONG)
            if not dark_emission.is_dark(sig):
                return self._reject("long_disabled")

        return sig

    # ------------------------------------------------------------------
    # FUNDING_EXTREME_SIGNAL path
    # Extreme funding rate with price + RSI + CVD confluence.
    # ------------------------------------------------------------------

    def _evaluate_funding_extreme(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """FUNDING_EXTREME_SIGNAL: contrarian signal when funding rate is extreme."""
        # QUIET block removed: extreme funding is the quality gate, not regime.
        # Market spends ~78% of time in QUIET, which was starving this path.

        funding_rate = smc_data.get("funding_rate")
        if funding_rate is None:
            return self._reject("missing_funding_rate")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 5:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        if len(closes) < 5:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        close = float(closes[-1])
        if close <= 0:
            # Telemetry-truth: this is invalid candle data, NOT a "funding not
            # extreme" condition.  Pre-fix conflated the two reasons in the
            # path-funnel, polluting the headline `funding_not_extreme` count
            # with a small number of bad-price rows.
            return self._reject("invalid_price")

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        rsi_last = ind.get("rsi_last")
        rsi_prev = ind.get("rsi_prev")

        # CVD
        cvd_data = smc_data.get("cvd")
        cvd_change: Optional[float] = None
        if cvd_data is not None:
            cvd_values = cvd_data if isinstance(cvd_data, list) else cvd_data.get("values", [])
            if len(cvd_values) >= 4:
                cvd_change = float(cvd_values[-1]) - float(cvd_values[-4])

        # LONG signal: deeply negative funding → longs being discounted
        if funding_rate < -FUNDING_RATE_EXTREME_THRESHOLD:
            if ema9 is None or close <= ema9:
                return self._reject("ema_alignment_reject")
            if rsi_last is not None and rsi_last >= 55:
                return self._reject("rsi_reject")
            if rsi_prev is not None and rsi_last is not None and rsi_last <= rsi_prev:
                return self._reject("momentum_reject")
            if cvd_change is not None and cvd_change <= 0:
                return self._reject("cvd_divergence_failed")
            direction = Direction.LONG
        # SHORT signal: deeply positive funding → shorts being discounted
        elif funding_rate > FUNDING_RATE_EXTREME_THRESHOLD:
            if ema9 is None or close >= ema9:
                return self._reject("ema_alignment_reject")
            if rsi_last is not None and rsi_last <= 45:
                return self._reject("rsi_reject")
            if rsi_prev is not None and rsi_last is not None and rsi_last >= rsi_prev:
                return self._reject("momentum_reject")
            if cvd_change is not None and cvd_change >= 0:
                return self._reject("cvd_divergence_failed")
            direction = Direction.SHORT
        else:
            return self._reject("funding_not_extreme")

        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return self._reject("missing_fvg_or_orderblock")

        atr_val = ind.get("atr_last", close * 0.002)

        # SL: nearest liquidation cluster in SL direction, fallback atr*1.5
        liq_clusters = smc_data.get("liquidation_clusters", [])
        sl_dist: Optional[float] = None
        for cluster in liq_clusters:
            cluster_price = cluster.get("price") if isinstance(cluster, dict) else getattr(cluster, "price", None)
            if cluster_price is None:
                continue
            cluster_price = float(cluster_price)
            if direction == Direction.LONG and cluster_price < close:
                liq_dist = abs(close - cluster_price) * 1.1
                if sl_dist is None or liq_dist < sl_dist:
                    sl_dist = liq_dist
            elif direction == Direction.SHORT and cluster_price > close:
                liq_dist = abs(close - cluster_price) * 1.1
                if sl_dist is None or liq_dist < sl_dist:
                    sl_dist = liq_dist

        _sl_degraded = False
        if sl_dist is None or sl_dist <= 0:
            sl_dist = atr_val * 1.5
            _sl_degraded = True

        sl = close - sl_dist if direction == Direction.LONG else close + sl_dist
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # TP1: nearest FVG/OB structure level in the direction of travel.
        # The path already requires FVG/OB confluence at entry, so the nearest
        # qualifying structure level is the natural first normalization target.
        # Falls back to 1.5R when no qualifying level is found — better than
        # the previous flat 0.5% placeholder which was not thesis-aligned.
        tp1 = _funding_extreme_structure_tp1(fvgs, orderblocks, close, direction, sl_dist)

        # ATR-adaptive TP1 cap (mirror of SR_FLIP / TPE pattern).
        # When the nearest qualifying FVG/OB is far from close (e.g., 5-10R in
        # trending markets), the structural target sits well past where a
        # mean-reversion contrarian setup can realistically reach before SL.
        # Cap by ATR percentile so the structure-level target is preserved
        # only when within reach:
        #   <40 (low ATR / accumulation):  TP1 ≤ 1.8R
        #   40-65 (median ATR):            TP1 ≤ 2.5R
        #   ≥65 (high ATR):                no cap (room to run)
        # FUNDING is mean-reversion (`min_rr` 0.9 per signal_quality) so the
        # cap matters more here than for trend-following paths.
        _rc_funding = smc_data.get("regime_context")
        _atr_pct_funding = _rc_funding.atr_percentile if _rc_funding else 50.0
        if _atr_pct_funding < 40.0:
            _tp1_cap_funding = sl_dist * 1.8
        elif _atr_pct_funding < 65.0:
            _tp1_cap_funding = sl_dist * 2.5
        else:
            _tp1_cap_funding = None
        if _tp1_cap_funding is not None:
            tp1 = (min(tp1, close + _tp1_cap_funding) if direction == Direction.LONG
                   else max(tp1, close - _tp1_cap_funding))

        tp2 = close + sl_dist * 2.0 if direction == Direction.LONG else close - sl_dist * 2.0
        tp3 = close + sl_dist * 3.5 if direction == Direction.LONG else close - sl_dist * 3.5
        # Q4-B: enforce ladder monotonicity.  tp1 from `_funding_extreme_structure_tp1`
        # can sit > 2R from close when the nearest qualifying FVG/OB is far,
        # which would invert the flat tp2 = close ± 2R fallback below it.
        tp1, tp2, tp3 = _enforce_tp_ladder_monotonicity(
            tp1, tp2, tp3, close, sl_dist, direction,
            tp2_rmult_floor=2.0, tp3_rmult_floor=3.5,
        )

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="FUND",
            atr_val=atr_val,
            setup_class="FUNDING_EXTREME_SIGNAL",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        if _sl_degraded:
            _note = "SL: ATR×1.5 fallback (liquidation clusters absent — thesis-aligned SL unavailable)"
            sig.execution_note = (getattr(sig, "execution_note", "") + "; " + _note).lstrip("; ")
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + 5.0
            sig.soft_gate_flags = (getattr(sig, "soft_gate_flags", "") + ",LIQ_CLUSTER_ABSENT").lstrip(",")
        sig.confidence = min(100.0, sig.confidence + 6.0)
        return sig

    # ------------------------------------------------------------------
    # QUIET_COMPRESSION_BREAK path
    # Bollinger Band squeeze breakout with MACD + volume + RSI.
    # ------------------------------------------------------------------

    def _evaluate_quiet_compression_break(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """QUIET_COMPRESSION_BREAK: 15m Bollinger Band squeeze breakout.

        Detection on 15m (OWNER_BRIEF §3.4a row 5 — HTF Structure, LTF
        Entry); entry timing on 5m breakout candle.  Pre-2026-05-17 the
        compression was detected on 5m which fires dozens of times per
        day per pair on noise — truth-report data showed 39% MFE=0 on
        QCB signals with the path running structurally negative
        (-1.11% NET/sig).

        Three coupled changes vs the pre-fix path:

          1. **15m compression** — band width / close < 1.5% on 15m
             (vs 5m width < 2.5%).  Real accumulation squeezes show
             on 15m; 5m wiggles within larger bands aren't the same
             setup.  Per literature: 15m squeezes are the signature
             retail traders + market makers actually defend.
          2. **Real volume confirmation** — the closed PRIOR 5m candle
             must show ≥ 1.5× the 20-candle volume average.  The pre-
             fix code removed the volume check entirely citing a
             still-forming-candle unit-mismatch (correctly); this PR
             puts the gate back on the *closed* prior candle which
             has no such unit problem.  Per literature: BB breakouts
             without volume are 40-50% noise.
          3. **TP1 widened** — band_width × 1.5 (vs band_width × 0.5).
             At R:R 1.30 the path mathematically can't profit at
             realistic 40-50% breakout win rates; the literature
             requires R:R ≥ 3:1 for positive EV.  TP1 × 1.5 brings
             the geometry into ~3:1 territory at typical 15m bands.
        """
        regime_upper = regime.upper() if regime else ""
        if regime_upper not in ("QUIET", "RANGING"):
            return self._reject("regime_blocked")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 25:
            return self._reject("insufficient_candles")

        closes = m5.get("close", [])
        volumes = m5.get("volume", [])
        if len(closes) < 25 or len(volumes) < 21:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        close = float(closes[-1])
        if close <= 0:
            return self._reject("invalid_price")

        # 15m compression check (OWNER_BRIEF §3.4a row 5).  Production
        # scanner populates indicators["15m"] via PR #408's 15m pipeline.
        # When 15m indicators are absent (test fixtures / pre-warm window),
        # fall through to the legacy 5m check to preserve backward-compat
        # with existing QCB test fixtures that don't seed 15m data.
        ind_5m = indicators.get("5m", {})
        ind_15m = indicators.get("15m", {})

        bb_upper_15m = ind_15m.get("bb_upper_last")
        bb_lower_15m = ind_15m.get("bb_lower_last")
        use_15m_compression = (
            bb_upper_15m is not None and bb_lower_15m is not None
        )

        # 5m bands are ALWAYS used for the breakout-direction trigger —
        # this is the "LTF entry" half of the HTF Structure / LTF Entry
        # doctrine.  The HTF (15m) bands govern compression + SL/TP
        # geometry but the trigger is a 5m close stepping outside the
        # 5m bands.
        bb_upper_5m = ind_5m.get("bb_upper_last")
        bb_lower_5m = ind_5m.get("bb_lower_last")
        if bb_upper_5m is None or bb_lower_5m is None:
            return self._reject("missing_bollinger_bands")
        bb_upper_5m = float(bb_upper_5m)
        bb_lower_5m = float(bb_lower_5m)

        if use_15m_compression:
            bb_upper = float(bb_upper_15m)
            bb_lower = float(bb_lower_15m)
            # Tighter 15m squeeze threshold — real accumulation bands on
            # 15m are <1.5% wide.  Pre-2026-05-17 the 5m threshold was
            # 2.5% (widened from 1.5% specifically because 5m bands
            # rarely tighten that much in QUIET; the 15m equivalent IS
            # the tight version).
            _compression_threshold = 0.015
        else:
            # Legacy 5m-only path for test fixtures that don't seed 15m
            # data.  Compression + breakout + geometry all use the 5m
            # bands — identical to the pre-2026-05-17 behaviour.
            bb_upper = bb_upper_5m
            bb_lower = bb_lower_5m
            _compression_threshold = 0.025

        if (bb_upper - bb_lower) / close >= _compression_threshold:
            return self._reject("compression_not_detected")

        # Entry direction — 5m breakout, regardless of which TF the
        # compression was measured on.  The 15m bands are the structural
        # context; the 5m close-vs-5m-band tells us the trigger fired.
        # When the HTF path is active, this lets a 5m breakout fire even
        # if the close is still inside the wider 15m envelope — which is
        # exactly the early-entry doctrine §3.4a calls for.
        if close > bb_upper_5m:
            direction = Direction.LONG
        elif close < bb_lower_5m:
            direction = Direction.SHORT
        else:
            return self._reject("breakout_not_detected")

        # HTF mismatch soft penalty — aligned with scalping doctrine
        # (OWNER_BRIEF §2.1a).  QCB lives in QUIET/RANGING regimes where
        # HTF trends are typically weak, so the penalty rarely fires —
        # but when 1H AND 4H both clearly oppose direction it adds a
        # conservative confidence haircut without hard-blocking the
        # signal.  Replaces the prior hard `htf_direction_veto` reject
        # (PR #267 → corrected by PR #269).
        qcb_htf_penalty = 0.0
        if _QCB_HTF_MISMATCH_PENALTY > 0:
            trend_1h = self._classify_htf_trend(indicators, candles, "1h")
            trend_4h = self._classify_htf_trend(indicators, candles, "4h")
            opposite = "BEARISH" if direction == Direction.LONG else "BULLISH"
            if trend_1h == opposite and trend_4h == opposite:
                qcb_htf_penalty = _QCB_HTF_MISMATCH_PENALTY

        # MACD momentum confirmation: histogram must be trending in breakout direction.
        # Zero-cross requirement was too timing-sensitive — breakout candle rarely
        # lands on the exact zero-cross tick in low-vol accumulation.
        ind = ind_5m  # Preserve the legacy local name for the rest of the function
        macd_hist_last = ind.get("macd_histogram_last")
        macd_hist_prev = ind.get("macd_histogram_prev")
        if macd_hist_last is not None and macd_hist_prev is not None:
            if direction == Direction.LONG and not (macd_hist_last > macd_hist_prev):
                return self._reject("macd_reject")
            if direction == Direction.SHORT and not (macd_hist_last < macd_hist_prev):
                return self._reject("macd_reject")

        # Volume confirmation — REAL gate (2026-05-17 doctrine reset).
        # The pre-fix path removed the volume check entirely citing a
        # unit-mismatch on the still-forming current 5m candle.  That
        # critique was correct as written but the doctrinal need for
        # volume confirmation wasn't replaced.  Literature on BB squeeze
        # breakouts (pi42.com / Gate.io Web3 Research) is consistent:
        # without volume confirmation, 40-50% of breakouts are false.
        #
        # This implementation checks the CLOSED PRIOR 5m candle's volume
        # vs the 20-bar rolling average (using closed bars only) so there's
        # no unit-mismatch.  The threshold (1.5× avg) is conservative —
        # lower than the literature's 2× suggestion to account for QCB
        # firing in QUIET regime where absolute volumes are by definition
        # below their cross-regime averages.
        avg_vol = sum(float(v) for v in volumes[-21:-1]) / 20.0
        if avg_vol <= 0:
            return self._reject("volume_reject")
        # ``volumes[-2]`` is the prior closed bar (volumes[-1] is the
        # still-forming current bar, which is the partial-candle source
        # the pre-fix removed).  No unit-mismatch here.
        prior_closed_volume = float(volumes[-2])
        if prior_closed_volume < avg_vol * _QCB_VOLUME_CONFIRMATION_MULT:
            return self._reject("volume_confirmation_failed")

        # RSI
        rsi_val = ind.get("rsi_last")
        if rsi_val is not None:
            # Widened from [50,70]/[30,50] — breakout candles can push RSI to 72-75.
            if direction == Direction.LONG and not (48 <= rsi_val <= 75):
                return self._reject("rsi_reject")
            if direction == Direction.SHORT and not (25 <= rsi_val <= 52):
                return self._reject("rsi_reject")

        # SMC: FVG preferred, fallback to orderblocks
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return self._reject("missing_fvg_or_orderblock")

        atr_val = ind.get("atr_last", close * 0.002)

        # SL and TP — same close-relative + ATR floor pattern as VSB / BDS / ORB.
        # Pre-fix anchored SL to the opposite Bollinger band with a tiny 0.5×ATR
        # buffer, OR to a flat 0.3% close-relative — whichever was further.
        # The 0.3% floor was sub-spread on most pairs and ignored ATR; the
        # bb-anchored stop was tight in compressed-band conditions (QCB by
        # definition fires when bb width <2.5%).  Result: the 0.80% universal
        # floor at `_enqueue_signal` clamped most stops, defeating the
        # structural anchor.  Apply close-relative floor: max(0.8% × close,
        # 1×ATR) below close (LONG) / above close (SHORT).  Take the
        # further-from-close of structural and close-relative anchors so
        # the stop respects both the band geometry AND minimum room.
        if direction == Direction.LONG:
            structural_sl = bb_lower - atr_val * 0.5
            close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
            sl = min(structural_sl, close_rel_floor)
        else:
            structural_sl = bb_upper + atr_val * 0.5
            close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
            sl = max(structural_sl, close_rel_ceiling)

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # TP ladder — TP1 widened to ``band_width × 1.5`` (was 0.5).
        # OWNER_BRIEF §3.2 / B11 economics: at R:R 1.30 the path requires
        # >50% win rate (taker fees, 10× leverage) to break even net.
        # Truth report shows QCB at ~1.5% win rate — the geometry was
        # mathematically incapable of profit.  TP1 × 1.5 produces typical
        # R:R ≈ 2.5-3.0 at our SL geometry, which the literature says
        # is the minimum for BB-squeeze breakouts.  TP2 / TP3 widened
        # proportionally to preserve the ladder structure.
        band_width = bb_upper - bb_lower
        if band_width > 0:
            if direction == Direction.LONG:
                tp1 = close + band_width * 1.5
                tp2 = close + band_width * 2.5
                tp3 = close + band_width * 4.0
            else:
                tp1 = close - band_width * 1.5
                tp2 = close - band_width * 2.5
                tp3 = close - band_width * 4.0
        else:
            tp1 = close + sl_dist * 3.0 if direction == Direction.LONG else close - sl_dist * 3.0
            tp2 = close + sl_dist * 4.5 if direction == Direction.LONG else close - sl_dist * 4.5
            tp3 = close + sl_dist * 6.0 if direction == Direction.LONG else close - sl_dist * 6.0

        # R:R floor — TP1 must be at least 2.5× SL distance from entry
        # (was 1.3×).  Same doctrinal reason as above; preserves the
        # ladder when band_width was unusually small relative to SL.
        if direction == Direction.LONG:
            tp1 = max(tp1, close + sl_dist * 2.5)
            tp2 = max(tp2, close + sl_dist * 3.5)
            tp3 = max(tp3, close + sl_dist * 5.0)
        else:
            tp1 = min(tp1, close - sl_dist * 2.5)
            tp2 = min(tp2, close - sl_dist * 3.5)
            tp3 = min(tp3, close - sl_dist * 5.0)

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="QBREAK",
            atr_val=atr_val,
            setup_class="QUIET_COMPRESSION_BREAK",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # Stamp the validated closed-bar breakout volume ratio so the scorer
        # scores volume off the squeeze-break candle, not the quiet entry
        # candle (QUIET-regime entry volume is low by design). Pairs with
        # QUIET_COMPRESSION_BREAK's membership in _BREAKOUT_SURGE_SETUPS.
        sig.breakout_volume_ratio = (
            prior_closed_volume / avg_vol if avg_vol > 0 else 0.0
        )
        sig.confidence = min(100.0, sig.confidence + 4.0)
        if qcb_htf_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + qcb_htf_penalty
        return sig

    # ------------------------------------------------------------------
    # DIVERGENCE_CONTINUATION path
    # Hidden CVD divergence confirms trend continuation.
    # ------------------------------------------------------------------

    def _evaluate_divergence_continuation(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """DIVERGENCE_CONTINUATION: hidden CVD divergence in trending regime.

        Detection on **15m CVD + 15m close divergence** (OWNER_BRIEF §3.4a
        row 3 — "Detect on 15m CVD divergence vs 15m HH/LL; Confirm on
        5m EMA21 retest in trend direction; Enter on 5m EMA9 reclaim").

        Pre-2026-05-17 DIV_CONT detected divergence on 5m CVD/5m close
        (forensic: 19 signals, 63% MFE=0 — second-worst direction-call
        quality after TPE).  5m CVD is dominated by HFT noise so the
        signal-to-noise of a "divergence" read is poor.  The 15m series
        carries enough trade-flow integration to express genuine
        accumulation/distribution structure.

        Direction comes from **1H EMA21/50 alignment + slope** (HTF
        trend identification).  Pre-2026-05-17 direction was sourced
        from the 5m regime label — circular for an evaluator entering
        on 5m.

        Legacy 5m-divergence + 5m-regime fallback preserved when 15m
        CVD or 1H indicators absent (warmup / test fixtures) so soft
        penalty doctrine holds and existing test fixtures still
        exercise the path.
        """
        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return self._reject("insufficient_candles")

        closes_raw = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        if len(closes_raw) < 20:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        # ── HTF direction (1H EMA21/50 alignment + slope) ────────────
        # Mirrors TPE PR #418 doctrine.  When 1H indicators absent,
        # fall back to legacy 5m-regime label path (preserves test
        # fixtures that don't seed 1H data).
        ind_1h = indicators.get("1h", {})
        ema21_1h = ind_1h.get("ema21_last")
        ema50_1h = ind_1h.get("ema50_last")
        ema21_1h_prev = ind_1h.get("ema21_prev")
        _uses_1h_trend = ema21_1h is not None and ema50_1h is not None

        direction: Optional[Direction] = None
        if _uses_1h_trend:
            ema21_1h_f = float(ema21_1h)
            ema50_1h_f = float(ema50_1h)
            # Slope: when ema21_prev absent (warmup), accept alignment-only.
            slope_pos = (
                ema21_1h_prev is None or float(ema21_1h_prev) < ema21_1h_f
            )
            slope_neg = (
                ema21_1h_prev is None or float(ema21_1h_prev) > ema21_1h_f
            )
            if ema21_1h_f > ema50_1h_f and slope_pos:
                direction = Direction.LONG
            elif ema21_1h_f < ema50_1h_f and slope_neg:
                direction = Direction.SHORT
            else:
                return self._reject("h1_trend_not_aligned")
        else:
            # Legacy 5m-regime fallback (test / pre-warm).
            regime_upper = regime.upper() if regime else ""
            if regime_upper == "TRENDING_UP":
                direction = Direction.LONG
            elif regime_upper == "TRENDING_DOWN":
                direction = Direction.SHORT
            elif regime_upper == "WEAK_TREND":
                ind_for_dir = indicators.get("5m", {})
                ema9_for_dir = ind_for_dir.get("ema9_last")
                ema21_for_dir = ind_for_dir.get("ema21_last")
                if ema9_for_dir is None or ema21_for_dir is None:
                    return self._reject("ema_alignment_reject")
                if ema9_for_dir > ema21_for_dir:
                    direction = Direction.LONG
                elif ema9_for_dir < ema21_for_dir:
                    direction = Direction.SHORT
                else:
                    return self._reject("ema_alignment_reject")
            else:
                return self._reject("regime_blocked")

        # 4H conflict penalty: when the 4H EMA21/50 trend opposes the
        # 1H-determined direction, the CVD divergence is fighting two-TF
        # structure.  The 1H gate above already hard-rejects if the 1H trend
        # is absent; this catches the case where 1H is barely aligned but 4H
        # still says the opposite (BEATUSDT SHORT: 1H EMA21 < EMA50 by a
        # sliver, 4H EMA21 > EMA50 = firmly bullish → direction call weak).
        # Only applied on the 1H path (_uses_1h_trend) — legacy 5m fallback
        # doesn't have 4H context and isn't used in prod.
        _h4_conflict_penalty = 0.0
        if _DIV_CONT_H4_CONFLICT_PENALTY > 0 and _uses_1h_trend:
            _ind_4h = indicators.get("4h", {})
            _ema21_4h = _ind_4h.get("ema21_last")
            _ema50_4h = _ind_4h.get("ema50_last")
            if _ema21_4h is not None and _ema50_4h is not None:
                _ema21_4h_f, _ema50_4h_f = float(_ema21_4h), float(_ema50_4h)
                if direction == Direction.SHORT and _ema21_4h_f > _ema50_4h_f:
                    _h4_conflict_penalty = _DIV_CONT_H4_CONFLICT_PENALTY
                elif direction == Direction.LONG and _ema21_4h_f < _ema50_4h_f:
                    _h4_conflict_penalty = _DIV_CONT_H4_CONFLICT_PENALTY

        closes = [float(c) for c in closes_raw]
        close = closes[-1]
        if close <= 0:
            # Telemetry-truth: invalid candle data, NOT a momentum reject.
            return self._reject("invalid_price")

        # ── Divergence detection: HTF 15m path ───────────────────────
        # 15m CVD + 15m close divergence is the structurally-correct
        # read.  Fall back to legacy 5m series when 15m unavailable
        # (warmup / test fixtures that don't seed 15m data).
        cvd_15m_data = smc_data.get("cvd_15m")
        candles_15m = candles.get("15m") or {}
        closes_15m = candles_15m.get("close") or []
        _uses_15m_cvd = (
            cvd_15m_data is not None
            and isinstance(cvd_15m_data, list)
            and len(cvd_15m_data) >= _DIV_CONT_15M_LOOKBACK_MIN
            and len(closes_15m) >= _DIV_CONT_15M_LOOKBACK_MIN
        )

        _div_detected = False
        _div_strength = 0.0
        if _uses_15m_cvd:
            cvd_15m_f = [float(v) for v in cvd_15m_data]
            closes_15m_f = [float(c) for c in closes_15m]
            _aligned_len = min(len(cvd_15m_f), len(closes_15m_f))
            cvd_15m_f = cvd_15m_f[-_aligned_len:]
            closes_15m_f = closes_15m_f[-_aligned_len:]

            for _win in (_DIV_CONT_15M_LOOKBACK, _DIV_CONT_15M_LOOKBACK_MIN):
                if _aligned_len < _win or _win < 4:
                    continue
                _half = _win // 2
                _early_price = closes_15m_f[-_win:-_half]
                _late_price = closes_15m_f[-_half:]
                _early_cvd = cvd_15m_f[-_win:-_half]
                _late_cvd = cvd_15m_f[-_half:]
                if not _early_price or not _late_price:
                    continue
                if direction == Direction.LONG:
                    _ep, _lp = min(_early_price), min(_late_price)
                    _ec, _lc = min(_early_cvd), min(_late_cvd)
                    if _lp < _ep and _lc > _ec:
                        _div_detected = True
                        _drop = (_ep - _lp) / _ep if _ep > 0 else 0.0
                        _div_strength = min(1.0, _drop / 0.03)
                        break
                else:
                    _ep, _lp = max(_early_price), max(_late_price)
                    _ec, _lc = max(_early_cvd), max(_late_cvd)
                    if _lp > _ep and _lc < _ec:
                        _div_detected = True
                        _rise = (_lp - _ep) / _ep if _ep > 0 else 0.0
                        _div_strength = min(1.0, _rise / 0.03)
                        break
            if not _div_detected:
                return self._reject("cvd_divergence_failed")
            _div_label: str = "BULLISH" if direction == Direction.LONG else "BEARISH"
        else:
            # ── Legacy 5m-divergence fallback ─────────────────────────
            cvd_data = smc_data.get("cvd")
            if cvd_data is None:
                return self._reject("missing_cvd")
            cvd_values = cvd_data if isinstance(cvd_data, list) else cvd_data.get("values", [])
            if len(cvd_values) < 10:
                return self._reject("cvd_insufficient")
            cvd_floats = [float(v) for v in cvd_values]

            _has_20 = len(cvd_floats) >= 20 and len(closes) >= 20
            if direction == Direction.LONG:
                if _has_20:
                    price_low_early = min(closes[-20:-10])
                    price_low_late = min(closes[-10:])
                    cvd_low_early = min(cvd_floats[-20:-10])
                    cvd_low_late = min(cvd_floats[-10:])
                    if price_low_late < price_low_early and cvd_low_late > cvd_low_early:
                        _div_detected = True
                        _drop = (price_low_early - price_low_late) / price_low_early if price_low_early > 0 else 0.0
                        _div_strength = min(1.0, _drop / 0.03)
                if not _div_detected and len(cvd_floats) >= 10 and len(closes) >= 10:
                    price_low_early = min(closes[-10:-5])
                    price_low_late = min(closes[-5:])
                    cvd_low_early = min(cvd_floats[-10:-5])
                    cvd_low_late = min(cvd_floats[-5:])
                    if price_low_late < price_low_early and cvd_low_late > cvd_low_early:
                        _div_detected = True
                        _drop = (price_low_early - price_low_late) / price_low_early if price_low_early > 0 else 0.0
                        _div_strength = min(1.0, _drop / 0.02)
                if not _div_detected:
                    return self._reject("cvd_divergence_failed")
                _div_label = "BULLISH"
            else:
                if _has_20:
                    price_high_early = max(closes[-20:-10])
                    price_high_late = max(closes[-10:])
                    cvd_high_early = max(cvd_floats[-20:-10])
                    cvd_high_late = max(cvd_floats[-10:])
                    if price_high_late > price_high_early and cvd_high_late < cvd_high_early:
                        _div_detected = True
                        _rise = (price_high_late - price_high_early) / price_high_early if price_high_early > 0 else 0.0
                        _div_strength = min(1.0, _rise / 0.03)
                if not _div_detected and len(cvd_floats) >= 10 and len(closes) >= 10:
                    price_high_early = max(closes[-10:-5])
                    price_high_late = max(closes[-5:])
                    cvd_high_early = max(cvd_floats[-10:-5])
                    cvd_high_late = max(cvd_floats[-5:])
                    if price_high_late > price_high_early and cvd_high_late < cvd_high_early:
                        _div_detected = True
                        _rise = (price_high_late - price_high_early) / price_high_early if price_high_early > 0 else 0.0
                        _div_strength = min(1.0, _rise / 0.02)
                if not _div_detected:
                    return self._reject("cvd_divergence_failed")
                _div_label = "BEARISH"

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return self._reject("ema_alignment_reject")

        # Price within 1.5% of EMA21
        if ema21 <= 0 or abs(close - ema21) / ema21 > 0.015:
            return self._reject("retest_proximity_failed")

        # EMA alignment
        if direction == Direction.LONG and ema9 <= ema21:
            return self._reject("ema_alignment_reject")
        if direction == Direction.SHORT and ema9 >= ema21:
            return self._reject("ema_alignment_reject")

        # SMC basis
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return self._reject("missing_fvg_or_orderblock")

        # SL geometry — same close-relative + ATR floor pattern as VSB / BDS /
        # ORB / QCB.  Pre-fix anchored SL purely to EMA21 ± 0.5% which could
        # produce sub-spread stops when close is very near EMA21:
        #   close=100, ema21=99.9 → sl=99.40 → sl_dist 0.60% (< 0.80% universal floor)
        # The 0.80% universal floor at `_enqueue_signal` would clamp it,
        # defeating the structural anchor.  Take the LOWER (further-from-close,
        # since LONG) of structural floor and close-relative floor:
        #   - structural floor: ema21 − 0.5% (anti-EMA21-flip-back invalidation)
        #   - close-relative floor: max(0.8% × close, 1.0×ATR)
        atr_val = ind.get("atr_last", close * 0.002)
        if direction == Direction.LONG:
            structural_sl = ema21 * (1 - 0.005)
            close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
            sl = min(structural_sl, close_rel_floor)
        else:
            structural_sl = ema21 * (1 + 0.005)
            close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
            sl = max(structural_sl, close_rel_ceiling)

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # TP1: nearer 10-candle swing — natural first target from the recent
        # divergence resolution.  Using a 10-bar window (vs the original 20-bar)
        # prevents TP1 from collapsing onto TP2 when the 20-bar extreme sits in
        # the last 10 bars.
        if direction == Direction.LONG:
            _tp1_win = [float(h) for h in highs[-10:]] if len(highs) >= 10 else []
            tp1 = max(_tp1_win) if _tp1_win else 0.0
            if tp1 <= close:
                tp1 = close + sl_dist * 1.5
        else:
            _tp1_win = [float(low_val) for low_val in lows[-10:]] if len(lows) >= 10 else []
            tp1 = min(_tp1_win) if _tp1_win else close
            if tp1 >= close:
                tp1 = close - sl_dist * 1.5

        # ATR-adaptive TP1 cap (mirror of SR_FLIP / TPE / FUNDING).
        # The 10-candle swing extremum can sit several R from close in
        # trending markets — DIV_CONT is a continuation setup so it sits
        # in TRENDING regimes by definition.  Cap by ATR percentile so
        # the structural target survives only when within reach.
        # 10-candle window (vs SR_FLIP's 20) is naturally more contained,
        # but the cap still matters on strong-trend pairs where 50min of
        # one-direction price action can produce 4-5R extrema.
        _rc_divcont = smc_data.get("regime_context")
        _atr_pct_divcont = _rc_divcont.atr_percentile if _rc_divcont else 50.0
        if _atr_pct_divcont < 40.0:
            _tp1_cap_divcont = sl_dist * 1.8
        elif _atr_pct_divcont < 65.0:
            _tp1_cap_divcont = sl_dist * 2.5
        else:
            _tp1_cap_divcont = None
        if _tp1_cap_divcont is not None:
            tp1 = (min(tp1, close + _tp1_cap_divcont) if direction == Direction.LONG
                   else max(tp1, close - _tp1_cap_divcont))

        # TP2: 20-candle structural swing — confirmation target.  Must always
        # sit at least 1R beyond TP1 to preserve two-stage TP progression.
        if direction == Direction.LONG:
            _tp2_win = [float(h) for h in highs[-20:]] if len(highs) >= 20 else []
            tp2_struct = max(_tp2_win) if _tp2_win else 0.0
            tp2_rmult = close + sl_dist * 2.5
            tp2 = max(tp2_struct, tp2_rmult, tp1 + sl_dist * 1.0)
        else:
            _tp2_win = [float(low_val) for low_val in lows[-20:]] if len(lows) >= 20 else []
            tp2_struct = min(_tp2_win) if _tp2_win else close
            tp2_rmult = close - sl_dist * 2.5
            tp2 = min(tp2_struct, tp2_rmult, tp1 - sl_dist * 1.0)

        # TP3: HTF (4h/15m) swing high/low — extended target.
        # Prefer 4h data; fall back to 15m if 4h is not available; then R-multiple.
        candles_4h = candles.get("4h")
        candles_15m = candles.get("15m")
        if candles_4h and len(candles_4h.get("high", [])) >= 5:
            _4h_highs = candles_4h.get("high", [])
            _4h_lows = candles_4h.get("low", [])
            if direction == Direction.LONG:
                tp3 = max(float(h) for h in _4h_highs[-10:]) if _4h_highs else close + sl_dist * 4.0
                if tp3 <= close:
                    tp3 = close + sl_dist * 4.0
            else:
                tp3 = min(float(l) for l in _4h_lows[-10:]) if _4h_lows else close - sl_dist * 4.0
                if tp3 >= close:
                    tp3 = close - sl_dist * 4.0
        elif candles_15m and len(candles_15m.get("high", [])) >= 5:
            _15m_highs = candles_15m.get("high", [])
            _15m_lows = candles_15m.get("low", [])
            if direction == Direction.LONG:
                tp3 = max(float(h) for h in _15m_highs[-20:]) if _15m_highs else close + sl_dist * 4.0
                if tp3 <= close:
                    tp3 = close + sl_dist * 4.0
            else:
                tp3 = min(float(l) for l in _15m_lows[-20:]) if _15m_lows else close - sl_dist * 4.0
                if tp3 >= close:
                    tp3 = close - sl_dist * 4.0
        else:
            tp3 = close + sl_dist * 4.0 if direction == Direction.LONG else close - sl_dist * 4.0

        profile = smc_data.get("pair_profile")
        # atr_val already computed above for SL.
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="DIVCON",
            atr_val=atr_val,
            setup_class="DIVERGENCE_CONTINUATION",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        sig.analyst_reason = f"Hidden {_div_label} CVD divergence (strength={_div_strength:.2f})"
        if _h4_conflict_penalty != 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + _h4_conflict_penalty
        return sig

    # ------------------------------------------------------------------
    # CONTINUATION_LIQUIDITY_SWEEP path (Phase 2, roadmap step 5)
    # Trend-present sweep of local liquidity → continuation entry.
    # ------------------------------------------------------------------

    def _evaluate_continuation_liquidity_sweep(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """CONTINUATION_LIQUIDITY_SWEEP — DISABLED 2026-05-17 per OWNER_BRIEF §3.4a.

        After PR #5's HTF POI anchor lands on LSR (_evaluate_standard), any sweep
        at a real HTF support during an uptrend automatically falls into LSR's
        catchment — the trend-aligned subset of LSR signals IS the continuation
        case.  Maintaining a separate evaluator with an additional trend-alignment
        constraint shrinks the sample without adding edge: 2026-05-17 audit on
        654 closed signals showed CLS at -2.36% NET/sig vs LSR at -1.13% NET/sig,
        which the doctrine attributes to CLS firing on micro stop-runs at
        nothing-levels (the same root cause LSR's HTF POI anchor addresses, but
        without HTF anchoring CLS still suffers).

        Disablement, not deletion: returning ``None`` here keeps the enum,
        telemetry constants, and historical-record compatibility intact (so
        old signal records remain readable).  Reversible via
        ``CLS_DISABLED_2026_05_17=false`` env override if the LSR HTF POI
        anchor proves to under-catch trend-aligned sweeps in the
        observation window.

        Original pre-disablement docstring follows for archival reference:

        Setup logic:
        1. Trend is established via EMA9/EMA21 alignment (hard gate).
        2. A recent local pullback swept short-term liquidity (stop hunt) in the
           trend direction — e.g. a dip below prior lows in an uptrend that
           quickly recovers.
        3. Price has already reclaimed the swept level — distinguishing this from
           an ongoing reversal or breakdown.
        4. Momentum agrees with the trend direction (hard gate).
        5. RSI is not at exhaustion extremes (layered hard/soft gate).

        Structural SL is placed beyond the swept level (+ ATR buffer).  If price
        returns below the sweep level the continuation thesis is invalidated.

        Soft penalty contributors (do not hard-reject):
        - RSI borderline (70-79 LONG / 21-30 SHORT): +6 pts
        - No FVG or orderblock in target zone: +8 pts
        - Sweep is older (6–10 candles back, not 1–5): +5 pts
        """
        # 2026-05-17 disablement (OWNER_BRIEF §3.4a).  Returns the rejection
        # tag ``cls_disabled_merged_into_lsr`` so the truth report still
        # surfaces non-zero suppression telemetry for this path during the
        # observation window — distinguishes "disabled by doctrine" from
        # "no candidates" cleanly.  Reversible per ``CLS_DISABLED_2026_05_17``.
        if _CLS_DISABLED_2026_05_17:
            return self._reject("cls_disabled_merged_into_lsr")

        # Hard block regimes where the continuation thesis does not apply:
        # - VOLATILE/VOLATILE_UNSUITABLE: chaotic orderflow invalidates structure
        # - RANGING/QUIET: no directional trend exists to continue
        regime_upper = regime.upper() if regime else ""
        if regime_upper not in _CLS_VALID_REGIMES:
            return self._reject("regime_blocked")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return self._reject("ema_alignment_reject")

        # Direction determined by EMA alignment — this is a trend-following path
        if ema9 > ema21:
            direction = Direction.LONG
        elif ema9 < ema21:
            direction = Direction.SHORT
        else:
            return self._reject("ema_alignment_reject")

        # Cross-validate direction against strongly-stated directional regimes
        if regime_upper == "TRENDING_DOWN" and direction == Direction.LONG:
            return self._reject("ema_alignment_reject")
        if regime_upper == "TRENDING_UP" and direction == Direction.SHORT:
            return self._reject("ema_alignment_reject")

        closes_raw = m5.get("close", [])
        close = float(closes_raw[-1])
        if close <= 0:
            # Telemetry-truth: this is invalid candle data, NOT a "momentum
            # reject" condition.  Pre-fix conflated bad-data telemetry with
            # the actual momentum gate count (same family as DIV_CONT /
            # FUNDING fixes in #256 / #254).
            return self._reject("invalid_price")

        # ADX gate: trend continuation requires meaningful trend strength
        profile = smc_data.get("pair_profile")
        thresholds = self._get_pair_adjusted_thresholds(profile)
        adx_val = ind.get("adx_last")
        if adx_val is not None and adx_val < thresholds["adx_min"]:
            return self._reject("adx_reject")

        # Sweep detection: must have a recent sweep in the trend continuation
        # direction (i.e. swept the stops of participants against the trend,
        # then recovered — confirming a liquidity grab rather than a break).
        sweeps = smc_data.get("sweeps", [])
        if not sweeps:
            return self._reject("sweeps_not_detected")

        trend_sweep = None
        for sweep in sweeps:
            if sweep.direction == direction:
                trend_sweep = sweep
                break
        if trend_sweep is None:
            return self._reject("sweeps_not_detected")

        # Sweep recency gate: sweep must be within the last _CLS_SWEEP_WINDOW
        # closed candles.  Staler sweeps lose their structural relevance.
        sweep_index = getattr(trend_sweep, "index", None)
        if sweep_index is None:
            return self._reject("sweep_index_missing")
        if sweep_index < -_CLS_SWEEP_WINDOW:
            return self._reject("sweep_too_old")

        # Sweep level extraction
        sweep_level: Optional[float] = None
        for attr in ("level", "price", "sweep_level"):
            v = getattr(trend_sweep, attr, None)
            if v is not None:
                sweep_level = float(v)
                break
        if sweep_level is None or sweep_level <= 0:
            return self._reject("sweeps_not_detected")

        # Reclaim confirmation: current price must already be beyond the swept
        # level in the trend direction.  This is the defining gate that separates
        # CLS from a still-in-progress LIQUIDITY_SWEEP_REVERSAL — the sweep must
        # already be resolved before this path fires.
        if direction == Direction.LONG and close <= sweep_level:
            return self._reject("reclaim_confirmation_failed")
        if direction == Direction.SHORT and close >= sweep_level:
            return self._reject("reclaim_confirmation_failed")

        # Momentum agreement: must confirm trend direction (hard gate)
        mom = ind.get("momentum_last")
        if mom is None:
            return self._reject("momentum_reject")
        if direction == Direction.LONG and mom <= 0:
            return self._reject("momentum_reject")
        if direction == Direction.SHORT and mom >= 0:
            return self._reject("momentum_reject")

        # RSI layered gate: hard reject only at true exhaustion extremes;
        # soft penalty in the borderline zone — same pattern as WHALE_MOMENTUM.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= _CLS_RSI_LONG_HARD_MAX:
                    return self._reject("rsi_reject")
                if rsi_val >= _CLS_RSI_LONG_SOFT_MIN:
                    rsi_penalty = 6.0
            else:
                if rsi_val <= _CLS_RSI_SHORT_HARD_MIN:
                    return self._reject("rsi_reject")
                if rsi_val <= _CLS_RSI_SHORT_SOFT_MAX:
                    rsi_penalty = 6.0

        # FVG / orderblock soft quality gate: absence is penalised, not hard-rejected.
        # In fast trending/expansion regimes, FVG detection can lag the actual
        # structural move; the sweep reclaim is the primary confirmation.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        fvg_ob_penalty = 0.0 if (fvgs or orderblocks) else 8.0

        # Sweep recency bonus: very recent sweeps (≤ _CLS_SWEEP_RECENT candles)
        # are the cleanest setups.  Older sweeps (within window) get a penalty.
        sweep_recency_penalty = 0.0 if sweep_index >= -_CLS_SWEEP_RECENT else 5.0

        # ── SL: placed beyond the swept level (structural invalidation) ────
        # Same close-relative + 1×ATR floor pattern as VSB / BDS / ORB / QCB /
        # DIV_CONT.  Pre-fix used `sweep_level ± 0.3×ATR` with a `0.5×ATR`
        # minimum.  When sweep_level was very close to close (e.g., 5bp gap),
        # the structural sl_dist could be 0.15% — well under the 0.80%
        # universal floor at `_enqueue_signal`, defeating the structural
        # anchor when clamped.  Now take the further-from-close of:
        #   - structural floor: sweep_level − 0.3×ATR (anti-sweep-recovery)
        #   - close-relative floor: max(0.8% × close, 1×ATR)
        atr_val = ind.get("atr_last", close * 0.002)
        atr_buffer = atr_val * 0.3
        if direction == Direction.LONG:
            structural_sl = sweep_level - atr_buffer
            close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
            sl = min(structural_sl, close_rel_floor)
        else:
            structural_sl = sweep_level + atr_buffer
            close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
            sl = max(structural_sl, close_rel_ceiling)

        sl_dist = abs(close - sl)
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # ── TP targets: FVG → swing target → ATR fallback ──────────────────
        m5_highs = m5.get("high", [])
        m5_lows = m5.get("low", [])
        tp1 = 0.0
        tp2 = 0.0

        # TP1: nearest FVG midpoint in the continuation direction
        for fvg_zone in fvgs:
            fvg_mid = None
            if hasattr(fvg_zone, "gap_high") and hasattr(fvg_zone, "gap_low"):
                fvg_mid = (float(fvg_zone.gap_high) + float(fvg_zone.gap_low)) / 2.0
            elif isinstance(fvg_zone, dict):
                gh = fvg_zone.get("gap_high", 0)
                gl = fvg_zone.get("gap_low", 0)
                if gh and gl:
                    fvg_mid = (float(gh) + float(gl)) / 2.0
            if fvg_mid is not None:
                if direction == Direction.LONG and fvg_mid > close:
                    tp1 = fvg_mid
                    break
                elif direction == Direction.SHORT and fvg_mid < close:
                    tp1 = fvg_mid
                    break

        # TP2: 20-candle swing high (LONG) or swing low (SHORT)
        if direction == Direction.LONG and len(m5_highs) >= 21:
            tp2 = max(float(h) for h in m5_highs[-21:-1])
            if tp2 <= close:
                tp2 = 0.0
        elif direction == Direction.SHORT and len(m5_lows) >= 21:
            tp2 = min(float(lv) for lv in m5_lows[-21:-1])
            if tp2 >= close:
                tp2 = 0.0

        # ATR-ratio fallback for any missing targets
        if tp1 <= 0 or (direction == Direction.LONG and tp1 <= close) or (direction == Direction.SHORT and tp1 >= close):
            tp1 = close + sl_dist * 1.5 if direction == Direction.LONG else close - sl_dist * 1.5
        if tp2 <= 0:
            tp2 = close + sl_dist * 2.5 if direction == Direction.LONG else close - sl_dist * 2.5
        tp3 = close + sl_dist * 4.0 if direction == Direction.LONG else close - sl_dist * 4.0

        # ATR-adaptive TP1 cap (mirror of SR_FLIP / TPE / FUNDING / DIV_CONT).
        # The FVG-anchored TP1 can sit several R from close in trending
        # markets; CLS is a continuation setup so by definition fires in
        # trends.  Cap by ATR percentile so the structural target survives
        # only when within reach.
        _rc_cls = smc_data.get("regime_context")
        _atr_pct_cls = _rc_cls.atr_percentile if _rc_cls else 50.0
        if _atr_pct_cls < 40.0:
            _tp1_cap_cls = sl_dist * 1.8
        elif _atr_pct_cls < 65.0:
            _tp1_cap_cls = sl_dist * 2.5
        else:
            _tp1_cap_cls = None
        if _tp1_cap_cls is not None:
            tp1 = (min(tp1, close + _tp1_cap_cls) if direction == Direction.LONG
                   else max(tp1, close - _tp1_cap_cls))

        # Q4-B: enforce ladder monotonicity (same pattern as LSR).
        tp1, tp2, tp3 = _enforce_tp_ladder_monotonicity(
            tp1, tp2, tp3, close, sl_dist, direction,
            tp2_rmult_floor=2.5, tp3_rmult_floor=4.0,
        )

        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="CLSWEEP",
            atr_val=atr_val,
            setup_class="CONTINUATION_LIQUIDITY_SWEEP",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Accumulate soft penalties — deducted from confidence post-scoring by scanner
        total_penalty = rsi_penalty + fvg_ob_penalty + sweep_recency_penalty
        if total_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

        return sig

    # ------------------------------------------------------------------
    # POST_DISPLACEMENT_CONTINUATION path (Phase 2, roadmap step 6)
    # Strong displacement → tight absorption consolidation → re-acceleration.
    # ------------------------------------------------------------------

    def _evaluate_post_displacement_continuation(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """POST_DISPLACEMENT_CONTINUATION: re-acceleration after institutional displacement.

        Setup logic:
        1. A genuine displacement candle (high volume + strong directional body)
           occurred 2–5 consolidation candles before the current bar.
        2. Following the displacement, 2–5 tight-range candles formed a
           consolidation (absorption phase): price holds within the displacement
           territory while volume contracts — institutions absorbing retail orders.
        3. Current close breaks beyond the consolidation range in the displacement
           direction — the re-acceleration that confirms institutional continuation.
        4. EMA9/EMA21 alignment must agree with the displacement direction (hard gate).
        5. Regime must be a continuation/expansion context (hard gate).
        6. RSI is not at exhaustion extremes (layered hard/soft gate).

        This is distinct from VOLUME_SURGE_BREAKOUT (which fires on the initial
        breakout + pullback) and CONTINUATION_LIQUIDITY_SWEEP (which requires a
        stop-hunt sweep).  PDC fires specifically on the re-acceleration leg of a
        two-phase institutional displacement move.

        Structural SL is placed just beyond the consolidation range.  If price
        re-enters the consolidation the re-acceleration thesis is invalidated.

        Soft penalty contributors (do not hard-reject):
        - RSI borderline (72-81 LONG / 19-28 SHORT): +6 pts
        - No FVG or orderblock present: +7 pts
        - Consolidation volume noisy (avg >= 1.5× displacement volume): +5 pts
        """
        # Hard block regimes where displacement + consolidation structure is not
        # architecturally sound:
        # - VOLATILE/VOLATILE_UNSUITABLE: chaotic orderflow makes displacement
        #   identification unreliable (spikes vs. genuine institutional moves blur)
        # - RANGING/QUIET: no directional context means "displacement" is just a
        #   spike into noise, not a sustained institutional commitment
        regime_upper = regime.upper() if regime else ""
        if regime_upper not in _PDC_VALID_REGIMES:
            return self._reject("regime_blocked")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return self._reject("insufficient_candles")

        closes_raw = m5.get("close", [])
        opens_raw = m5.get("open", [])
        highs_raw = m5.get("high", [])
        lows_raw = m5.get("low", [])
        volumes_raw = m5.get("volume", [])

        n = len(closes_raw)
        if (n < 20 or len(opens_raw) < n
                or len(highs_raw) < n or len(lows_raw) < n or len(volumes_raw) < n):
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return self._reject("ema_alignment_reject")

        # Direction from EMA alignment — displacement must agree with the trend
        if ema9 > ema21:
            direction = Direction.LONG
        elif ema9 < ema21:
            direction = Direction.SHORT
        else:
            return self._reject("ema_alignment_reject")

        # Cross-validate direction against strongly stated directional regimes
        if regime_upper == "TRENDING_DOWN" and direction == Direction.LONG:
            return self._reject("ema_alignment_reject")
        if regime_upper == "TRENDING_UP" and direction == Direction.SHORT:
            return self._reject("ema_alignment_reject")

        close = float(closes_raw[-1])
        if close <= 0:
            # Telemetry-truth: this is invalid candle data, NOT an auction-
            # not-detected condition.  Pre-fix conflated bad-data with the
            # actual auction-detection gate count (same family as DIV_CONT /
            # FUNDING / CLS fixes).
            return self._reject("invalid_price")

        # ADX gate: trend strength required for displacement to be valid
        profile = smc_data.get("pair_profile")
        thresholds = self._get_pair_adjusted_thresholds(profile)
        adx_val = ind.get("adx_last")
        if adx_val is not None and adx_val < thresholds["adx_min"]:
            return self._reject("adx_reject")

        # Rolling background volume average: computed from candles BEFORE the
        # displacement + consolidation window.  Excluding the recent event candles
        # prevents high consolidation volume from inflating the baseline and making
        # the displacement look insufficiently strong.
        # The worst case is a 5-candle consolidation + 1 displacement = 6 candles,
        # so we exclude the last (_PDC_CONSOL_MAX + 2) candles from the average.
        vol_bg_end = max(1, n - _PDC_CONSOL_MAX - 2)
        vol_bg_start = max(0, vol_bg_end - 15)
        vol_window = [float(v) for v in volumes_raw[vol_bg_start:vol_bg_end]]
        if not vol_window or sum(vol_window) <= 0:
            return self._reject("volume_spike_missing")
        avg_vol = sum(vol_window) / len(vol_window)

        # ── Displacement + consolidation structure search ────────────────
        # Iterate from shortest valid consolidation window to longest.
        # For each consol_count, the displacement candle is exactly
        # (consol_count + 1) positions back from current:
        #   closes[-1]                    = current (re-acceleration bar)
        #   closes[-2] … closes[-consol_count-1]  = consolidation phase
        #   closes[-(consol_count+2)]     = displacement candle
        displacement_found = None
        for consol_count in range(_PDC_CONSOL_MIN, _PDC_CONSOL_MAX + 1):
            d_back = consol_count + 1  # positions back from current to displacement
            if d_back + 1 >= n:
                continue  # Not enough history

            # Absolute index of the displacement candle
            d_abs = n - 1 - d_back

            disp_open = float(opens_raw[d_abs])
            disp_close_val = float(closes_raw[d_abs])
            disp_high = float(highs_raw[d_abs])
            disp_low = float(lows_raw[d_abs])
            disp_vol = float(volumes_raw[d_abs])

            disp_body = abs(disp_close_val - disp_open)
            disp_range = disp_high - disp_low
            if disp_range <= 0 or disp_body <= 0:
                continue

            # Displacement quality gates:
            # 1. Strong directional body (≥ 60% of range) — no wicky indecisive candle
            if disp_body / disp_range < _PDC_DISP_BODY_RATIO_MIN:
                continue

            # 2. Volume surge — institutional participation required
            if disp_vol < avg_vol * _PDC_DISP_VOLUME_MULT:
                continue

            # 3. Direction agreement — displacement must be in the EMA/regime direction
            disp_dir = Direction.LONG if disp_close_val > disp_open else Direction.SHORT
            if disp_dir != direction:
                continue

            # ── Consolidation phase validation ───────────────────────────
            # Consolidation candles occupy absolute indices [d_abs+1, d_abs+consol_count]
            # (i.e., between displacement and current, exclusive of both).
            consol_highs = [float(highs_raw[d_abs + 1 + i]) for i in range(consol_count)]
            consol_lows = [float(lows_raw[d_abs + 1 + i]) for i in range(consol_count)]
            consol_vols = [float(volumes_raw[d_abs + 1 + i]) for i in range(consol_count)]

            consol_high = max(consol_highs)
            consol_low = min(consol_lows)
            consol_range = consol_high - consol_low

            # Tight consolidation gate: range must be narrow relative to displacement body.
            # Wide consolidation means the move has reversed or extended — not absorption.
            if consol_range > disp_body * _PDC_CONSOL_RANGE_MAX_RATIO:
                continue

            # Territory gate: consolidation must remain within the displacement territory.
            # For LONG: consolidation lows stay above the displacement open (price hasn't
            # fully retraced the displacement body — still holding institutional gains).
            # For SHORT: consolidation highs stay below the displacement open (price hasn't
            # fully recovered — institutional sellers still in control).
            if direction == Direction.LONG and consol_low < disp_open:
                continue  # Consolidation gave back the full displacement body
            if direction == Direction.SHORT and consol_high > disp_open:
                continue  # Consolidation recovered the full displacement body

            consol_avg_vol = sum(consol_vols) / len(consol_vols)
            displacement_found = (
                disp_high, disp_low, disp_body,
                consol_high, consol_low, consol_avg_vol, disp_vol,
            )
            break

        if displacement_found is None:
            return self._reject("breakout_not_found")

        disp_high, disp_low, disp_body, consol_high, consol_low, consol_avg_vol, disp_vol = (
            displacement_found
        )

        # ── Re-acceleration breakout gate ───────────────────────────────
        # Current close must have broken beyond the consolidation range in the
        # displacement direction.  This is the defining moment of the setup.
        if direction == Direction.LONG and close <= consol_high:
            return self._reject("breakout_not_found")
        if direction == Direction.SHORT and close >= consol_low:
            return self._reject("breakout_not_found")

        # ── RSI layered gate ─────────────────────────────────────────────
        # Hard reject at true exhaustion extremes; soft penalty in borderline zone.
        # Same layered pattern as WHALE_MOMENTUM and CLS.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= _PDC_RSI_LONG_HARD_MAX:
                    return self._reject("rsi_reject")
                if rsi_val >= _PDC_RSI_LONG_SOFT_MIN:
                    rsi_penalty = 6.0
            else:
                if rsi_val <= _PDC_RSI_SHORT_HARD_MIN:
                    return self._reject("rsi_reject")
                if rsi_val <= _PDC_RSI_SHORT_SOFT_MAX:
                    rsi_penalty = 6.0

        # ── FVG / orderblock soft quality gate ───────────────────────────
        # Absence is penalised, not hard-rejected.  In fast regimes SMC detection
        # may lag; the displacement + consolidation structure is the primary
        # confirmation and stands alone when structural context is absent.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        fvg_ob_penalty = 0.0 if (fvgs or orderblocks) else 7.0

        # ── Consolidation volume quality penalty ─────────────────────────
        # Clean absorption: consolidation average volume should be below the
        # displacement candle volume.  If consolidation average >= 1.5× displacement
        # volume, the "absorption" is actually active trading (chop or continuation),
        # not the quiet institutional accumulation/distribution this path requires.
        consol_vol_penalty = 0.0
        if disp_vol > 0 and consol_avg_vol >= disp_vol * 1.5:
            consol_vol_penalty = 5.0

        # ── SL: just beyond the consolidation range (structural Type 1) ──
        # If price returns into the consolidation the re-acceleration is failed.
        # Same close-relative + 1×ATR floor pattern as VSB / BDS / ORB / QCB /
        # DIV_CONT / CLS.  Pre-fix used `consol_low ± 0.3×ATR` with `0.5×ATR`
        # min — when consolidation was tight (which is the path's whole
        # design — narrow consolidation = strong absorption), structural
        # sl_dist could be 0.2-0.4% — defeated by the 0.80% universal floor
        # at `_enqueue_signal`, structural anchor lost.
        atr_val = ind.get("atr_last", close * 0.002)
        atr_buffer = atr_val * 0.3
        if direction == Direction.LONG:
            structural_sl = consol_low - atr_buffer
            close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
            sl = min(structural_sl, close_rel_floor)
        else:
            structural_sl = consol_high + atr_buffer
            close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
            sl = max(structural_sl, close_rel_ceiling)

        sl_dist = abs(close - sl)
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # ── TP: Measured move from displacement height (Type C) ───────────
        # The displacement height captures the institutional move magnitude and
        # projects the expected continuation.  Projected from the current close
        # (re-acceleration entry point).
        disp_height = disp_high - disp_low
        if disp_height <= 0:
            disp_height = sl_dist * 2.0

        if direction == Direction.LONG:
            tp1 = close + disp_height * 1.0
            tp2 = close + disp_height * 1.5
            tp3 = close + disp_height * 2.5
        else:
            tp1 = close - disp_height * 1.0
            tp2 = close - disp_height * 1.5
            tp3 = close - disp_height * 2.5

        # Ensure minimum R:R geometry
        if direction == Direction.LONG and tp1 <= close:
            tp1 = close + sl_dist * 1.5
        if direction == Direction.SHORT and tp1 >= close:
            tp1 = close - sl_dist * 1.5
        if direction == Direction.LONG and tp2 <= tp1:
            tp2 = close + sl_dist * 2.5
        if direction == Direction.SHORT and tp2 >= tp1:
            tp2 = close - sl_dist * 2.5

        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="PDC",
            atr_val=atr_val,
            setup_class="POST_DISPLACEMENT_CONTINUATION",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # Stamp the validated displacement volume ratio so the scorer scores
        # volume off the institutional displacement leg (the defining 2.5×
        # surge), not the modest-volume re-acceleration entry candle. Pairs
        # with POST_DISPLACEMENT_CONTINUATION's membership in
        # _BREAKOUT_SURGE_SETUPS.
        sig.breakout_volume_ratio = disp_vol / avg_vol if avg_vol > 0 else 0.0

        # Store the consolidation breakout level so that execution_quality_check()
        # can use it as the structural anchor (rather than falling back to EMA21,
        # which is irrelevant to the displacement/consolidation thesis).
        # For LONG: the breakout level is consol_high (price broke above this).
        # For SHORT: the breakout level is consol_low (price broke below this).
        sig.pdc_breakout_level = round(
            consol_high if direction == Direction.LONG else consol_low, 8
        )

        # Accumulate soft penalties — deducted from confidence post-scoring by scanner
        total_penalty = rsi_penalty + fvg_ob_penalty + consol_vol_penalty
        if total_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

        return sig

    # ------------------------------------------------------------------
    # FAILED_AUCTION_RECLAIM path (Phase 2, roadmap step 7)
    # Failed breakout/breakdown → acceptance failure → reclaim.
    # ------------------------------------------------------------------

    def _evaluate_failed_auction_reclaim(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """FAILED_AUCTION_RECLAIM: failed-acceptance level reclaim entry.

        Setup logic:
        1. A structural reference level (prior swing high/low) is identified
           from recent history (excluding the auction window).
        2. Within the auction window (1–7 bars back from current), a candle
           probed beyond that level — the "failed auction": it broke the obvious
           level but its close stayed at or near the level rather than convincingly
           accepting beyond it.
        3. The current close has reclaimed back inside the prior range by at least
           _FAR_MIN_RECLAIM_ATR × ATR — the reclaim confirmation that entries the
           thesis.
        4. RSI is not at exhaustion extremes (layered hard/soft gate).

        This is distinct from:
        - LIQUIDITY_SWEEP_REVERSAL: LSR requires an SMC sweep structure (wick
          through prior lows/highs with SMC context).  FAR captures the price-
          structure rejection without requiring a sweep detection event.
        - CONTINUATION_LIQUIDITY_SWEEP: CLS enters continuation after a sweep in
          the trend direction.  FAR enters reclaim after a failed directional probe.
        - SR_FLIP_RETEST: SFR fires on a confirmed support/resistance role-change.
          FAR fires when a level holds by rejecting an auction attempt.

        Structural SL is placed just beyond the failed-auction wick extreme.  If
        price moves past that point the rejection was not genuine and the thesis
        is fully invalidated.

        Soft penalty contributors (do not hard-reject):
        - RSI in borderline zone (65-75 LONG / 25-35 SHORT): +6 pts
        - No FVG or orderblock context present: +5 pts
        """
        # Hard block regimes where false-auction detection is unreliable or where
        # genuine breakouts dominate, making FAR structurally incorrect.
        regime_upper = regime.upper() if regime else ""
        if regime_upper in _FAR_BLOCKED_REGIMES:
            return self._reject("regime_blocked")

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return self._reject("insufficient_candles")

        closes_raw = m5.get("close", [])
        highs_raw = m5.get("high", [])
        lows_raw = m5.get("low", [])

        n = len(closes_raw)
        if n < 20 or len(highs_raw) < n or len(lows_raw) < n:
            return self._reject("insufficient_candles")

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        ind = indicators.get("5m", {})
        atr_val = ind.get("atr_last")
        if atr_val is None or atr_val <= 0:
            return self._reject("atr_invalid")

        close = float(closes_raw[-1])
        if close <= 0:
            return self._reject("invalid_price")

        # ── Reference structure levels ───────────────────────────────────
        # HTF anchor (OWNER_BRIEF §3.4a row 4 — "Detect on 1H structural
        # level; Confirm on 1H probe-and-reclaim; Enter on 5m reclaim
        # candle").  Pre-2026-05-17 FAR computed struct_high / struct_low
        # purely from the prior 20 5m candles' high/low extremes — a
        # ~100-minute window that produced "swing failure" detections on
        # ordinary intra-trend wicks rather than real structural rejections.
        # Truth-report data: 115 FAR signals, 39% MFE=0, -0.72% NET/sig.
        #
        # When the scanner-injected ``smc_data["level_book_levels"]`` is
        # available (production path), prefer the highest-scoring
        # CLUSTERED (>= 2 source_tfs) or VP_ANCHORED level per side.
        # This is the same HTF anchor pattern used by LSR (PR #410) and
        # SR_FLIP (PR #414); the FAR thesis applies it to the "swing
        # failure pattern" reading — a probe of a multi-TF level that
        # closes back inside is institutional rejection, not just a
        # short-window 5m wick.
        #
        # Fallback to the 5m struct-scan when LevelBook is unavailable
        # (test fixtures / pre-warm) so the existing FAR test surface
        # continues exercising the path.
        _lb_levels_raw = smc_data.get("level_book_levels")
        struct_high: Optional[float] = None
        struct_low: Optional[float] = None
        if _lb_levels_raw is not None:
            for _lv in _lb_levels_raw:
                _src_tfs = getattr(_lv, "source_tfs", None) or [
                    getattr(_lv, "source_tf", "")
                ]
                _is_clustered = (
                    isinstance(_src_tfs, list) and len(_src_tfs) >= 2
                )
                _is_vp_anchored = (
                    getattr(_lv, "source_tf", "") == "vp"
                    or "vp" in (_src_tfs or [])
                )
                if not (_is_clustered or _is_vp_anchored):
                    continue
                _lv_price = float(getattr(_lv, "price", 0.0) or 0.0)
                if _lv_price <= 0:
                    continue
                _lv_type = (getattr(_lv, "type", "") or "").lower()
                if struct_high is None and _lv_type == "resistance":
                    struct_high = _lv_price
                elif struct_low is None and _lv_type == "support":
                    struct_low = _lv_price
                if struct_high is not None and struct_low is not None:
                    break
            if struct_high is None and struct_low is None:
                # LevelBook refreshed but no qualifying multi-TF level
                # on either side → strict doctrinal rejection (no SFP
                # without a real swing to fail at).
                return self._reject("no_htf_structural_level")
        else:
            # Test / pre-warm fallback — preserve the legacy 5m-window
            # struct-scan so existing FAR test fixtures continue to
            # exercise the path without needing LevelBook seeding.
            struct_end = n - 1 - _FAR_AUCTION_WINDOW_MAX   # exclusive end
            struct_start = max(0, struct_end - _FAR_STRUCT_LOOKBACK)
            if struct_end <= struct_start:
                return self._reject("auction_not_detected")
            struct_highs = [float(highs_raw[i]) for i in range(struct_start, struct_end)]
            struct_lows = [float(lows_raw[i]) for i in range(struct_start, struct_end)]
            if not struct_highs or not struct_lows:
                return self._reject("auction_not_detected")
            struct_high = max(struct_highs)
            struct_low = min(struct_lows)

        # Sanity: when both sides came from the same source, they must
        # straddle current price for the SFP thesis to apply.  In the
        # HTF path one side may be absent (LevelBook returned only a
        # resistance OR only a support nearby); set the missing side to
        # a sentinel that trivially fails its branch of the auction
        # search so we don't fire SFP in a direction with no anchor.
        if struct_high is not None and struct_low is not None and struct_high <= struct_low:
            return self._reject("auction_not_detected")
        if struct_high is None:
            struct_high = float("inf")    # No upper anchor → no SHORT detection
        if struct_low is None:
            struct_low = float("-inf")    # No lower anchor → no LONG detection

        # ── Failed-auction candle search ─────────────────────────────────
        # Scan the auction window (1 to _FAR_AUCTION_WINDOW_MAX bars back).
        # For a LONG setup: look for a candle whose LOW was below struct_low but
        # whose CLOSE was at or above struct_low (failed acceptance below).
        # For a SHORT setup: look for a candle whose HIGH was above struct_high
        # but whose CLOSE was at or below struct_high (failed acceptance above).
        long_auction: Optional[tuple] = None   # (auction_wick_low, struct_low)
        short_auction: Optional[tuple] = None  # (auction_wick_high, struct_high)

        for offset in range(_FAR_AUCTION_WINDOW_MIN, _FAR_AUCTION_WINDOW_MAX + 1):
            bar_idx = n - 1 - offset
            if bar_idx < 0:
                break
            bar_low = float(lows_raw[bar_idx])
            bar_high = float(highs_raw[bar_idx])
            bar_close = float(closes_raw[bar_idx])

            # LONG candidate: low below struct_low but close accepted back above
            # (close >= struct_low is "at or above", indicating rejection of the break)
            if (
                long_auction is None
                and bar_low < struct_low
                and bar_close >= struct_low * (1.0 - _FAR_ACCEPTANCE_THRESHOLD)
            ):
                long_auction = (bar_low, struct_low)

            # SHORT candidate: high above struct_high but close rejected back below
            if (
                short_auction is None
                and bar_high > struct_high
                and bar_close <= struct_high * (1.0 + _FAR_ACCEPTANCE_THRESHOLD)
            ):
                short_auction = (bar_high, struct_high)

            # Stop early if both found (shouldn't happen in normal markets but
            # prevents unnecessary iteration)
            if long_auction and short_auction:
                break

        # Determine which direction (if any) has a valid auction
        if long_auction is None and short_auction is None:
            return self._reject("auction_not_detected")

        # Prefer the auction whose reference level is currently reclaimed.
        # If both fire simultaneously (rare) prefer whichever reclaim is larger.
        direction = None
        auction_wick_extreme = 0.0
        reclaim_level = 0.0

        if long_auction is not None:
            awk_low, ref_low = long_auction
            reclaim_dist = close - ref_low
            min_reclaim = atr_val * _FAR_MIN_RECLAIM_ATR
            if close > ref_low and reclaim_dist >= min_reclaim:
                direction = Direction.LONG
                auction_wick_extreme = awk_low
                reclaim_level = ref_low

        if short_auction is not None:
            awk_high, ref_high = short_auction
            reclaim_dist_s = ref_high - close
            min_reclaim = atr_val * _FAR_MIN_RECLAIM_ATR
            if close < ref_high and reclaim_dist_s >= min_reclaim:
                # If long direction already set, compare reclaim distances
                if direction == Direction.LONG:
                    long_dist = close - reclaim_level
                    if reclaim_dist_s > long_dist:
                        direction = Direction.SHORT
                        auction_wick_extreme = awk_high
                        reclaim_level = ref_high
                else:
                    direction = Direction.SHORT
                    auction_wick_extreme = awk_high
                    reclaim_level = ref_high

        if direction is None:
            return self._reject("reclaim_hold_failed")

        # HTF mismatch soft penalty — we are SCALPING, not trend-following.
        # Counter-trend FAR setups (e.g., failed auction at resistance during
        # an uptrend) are legitimate brief-retracement scalps; hard-blocking
        # them would eliminate roughly half the path's edge in trending
        # markets where top-75 pairs move correlated.  Soft penalty when
        # BOTH 1H AND 4H oppose direction lets scoring decide whether the
        # signal still clears the confidence-tier threshold.
        htf_penalty = 0.0
        if _FAR_HTF_MISMATCH_PENALTY > 0:
            trend_1h = self._classify_htf_trend(indicators, candles, "1h")
            trend_4h = self._classify_htf_trend(indicators, candles, "4h")
            opposite = "BEARISH" if direction == Direction.LONG else "BULLISH"
            if trend_1h == opposite and trend_4h == opposite:
                htf_penalty = _FAR_HTF_MISMATCH_PENALTY

        if direction == Direction.LONG:
            tail = reclaim_level - auction_wick_extreme
        else:
            tail = auction_wick_extreme - reclaim_level
        if tail < atr_val * _FAR_MIN_TAIL_ATR:
            return self._reject("tail_too_small")

        # ── RSI layered gate ─────────────────────────────────────────────
        # More conservative thresholds than PDC because FAR is a reversal-of-
        # failure structure: entering when RSI is near exhaustion contradicts
        # the thesis that price is genuinely rejecting and reclaiming.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= _FAR_RSI_LONG_HARD_MAX:
                    return self._reject("rsi_reject")
                if rsi_val >= _FAR_RSI_LONG_SOFT_MIN:
                    rsi_penalty = 6.0
            else:
                if rsi_val <= _FAR_RSI_SHORT_HARD_MIN:
                    return self._reject("rsi_reject")
                if rsi_val <= _FAR_RSI_SHORT_SOFT_MAX:
                    rsi_penalty = 6.0

        # ── FVG / orderblock soft quality gate ───────────────────────────
        # SMC context strengthens the reclaim thesis but is not required:
        # FAR is defined as NOT oscillator-dependent and the structural candle
        # pattern is primary evidence.  Absence gets a soft penalty only.
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        fvg_ob_penalty = 0.0 if (fvgs or orderblocks) else 5.0

        # ── SL: below / above the failed-auction wick extreme ────────────
        # This is the hard structural invalidation: if price reaches the wick
        # extreme the rejection was not genuine — the auction was accepted
        # and the thesis is fully wrong.
        atr_buffer = atr_val * 0.3
        if direction == Direction.LONG:
            structural_sl = auction_wick_extreme - atr_buffer
            close_rel_floor = close - max(close * 0.008, atr_val * 1.0)
            sl = min(structural_sl, close_rel_floor)
        else:
            structural_sl = auction_wick_extreme + atr_buffer
            close_rel_ceiling = close + max(close * 0.008, atr_val * 1.0)
            sl = max(structural_sl, close_rel_ceiling)

        sl_dist = abs(close - sl)

        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        if direction == Direction.LONG:
            tp1 = max(close + tail, close + sl_dist * _FAR_MIN_RR)
            tp2 = close + tail * 1.5
            tp3 = close + tail * 2.5
        else:
            tp1 = min(close - tail, close - sl_dist * _FAR_MIN_RR)
            tp2 = close - tail * 1.5
            tp3 = close - tail * 2.5

        # Ensure minimum R:R geometry
        if direction == Direction.LONG and tp1 <= close:
            tp1 = close + sl_dist * _FAR_MIN_RR
        if direction == Direction.SHORT and tp1 >= close:
            tp1 = close - sl_dist * _FAR_MIN_RR
        if direction == Direction.LONG and tp2 <= tp1:
            tp2 = max(close + sl_dist * 2.5, tp1 + sl_dist * 0.5)
        if direction == Direction.SHORT and tp2 >= tp1:
            tp2 = min(close - sl_dist * 2.5, tp1 - sl_dist * 0.5)
        if direction == Direction.LONG and tp3 <= tp2:
            tp3 = max(close + sl_dist * 3.5, tp2 + sl_dist * 0.5)
        if direction == Direction.SHORT and tp3 >= tp2:
            tp3 = min(close - sl_dist * 3.5, tp2 - sl_dist * 0.5)

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="FAR",
            atr_val=atr_val,
            setup_class="FAILED_AUCTION_RECLAIM",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Store the reclaim level so that execution_quality_check() can use it
        # as the structural anchor (the level that was broken and reclaimed).
        # For LONG: reclaim_level is the struct_low that was broken-then-recovered.
        # For SHORT: reclaim_level is the struct_high that was broken-then-recovered.
        sig.far_reclaim_level = round(reclaim_level, 8)

        total_penalty = rsi_penalty + fvg_ob_penalty + htf_penalty
        if total_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

        return sig

    # ------------------------------------------------------------------
    # Kill zone integration (P2-13)
    # ------------------------------------------------------------------

    def _is_kill_zone_active(self, now: Optional[datetime] = None) -> bool:
        """Return True if the current UTC time falls within a high-liquidity kill zone.

        Kill zones are defined as:
        * London session     : 07:00–10:00 UTC
        * NY session         : 12:00–16:00 UTC
        * London/NY overlap  : 12:00–14:00 UTC (already covered by NY range above)
        """
        if now is None:
            now = datetime.now(timezone.utc)
        hour = now.hour
        return (7 <= hour < 10) or (12 <= hour < 16)

    def _apply_kill_zone_note(self, sig: Signal, profile=None, now: Optional[datetime] = None) -> Optional[Signal]:
        """Annotate the signal with a reduced-conviction note when outside kill zones.

        For ALTCOIN tier (kill_zone_hard_gate=True), applies a soft confidence
        penalty instead of hard-rejecting.  For other tiers, sets execution_note
        but still emits the signal.
        """
        if not self._is_kill_zone_active(now):
            if profile is not None and profile.kill_zone_hard_gate:
                # Soft penalty instead of hard reject for better setup capture
                sig.confidence = max(0.0, sig.confidence - 8.0)
                if sig.execution_note:
                    sig.execution_note += "; Kill zone penalty: -8 pts (ALTCOIN outside session)"
                else:
                    sig.execution_note = "Kill zone penalty: -8 pts (ALTCOIN outside session)"
            elif sig.execution_note:
                sig.execution_note += "; Outside kill zone — reduced conviction"
            else:
                sig.execution_note = "Outside kill zone — reduced conviction"
        return sig

    # ------------------------------------------------------------------
    # MA_CROSS_TREND_SHIFT — discrete EMA crossover event
    # ------------------------------------------------------------------
    #
    # The 15th evaluator (added 2026-05-06).  Catches the *moment* a
    # 4h EMA50 / EMA200 (golden / death cross) or a 1h EMA21 / EMA50
    # crosses, rather than confirming an existing trend via stack
    # alignment (the way other evaluators consume EMAs).
    #
    # Rationale: textbook trend-shift signal that no current path
    # captures cleanly.  Low-frequency / high-conviction (cooldown 24h
    # per (symbol, direction)) — fits app-era doctrine where Pre-TP
    # grab + invalidation audit cap downside on additional volume.
    #
    # Trigger logic
    #   golden cross  (LONG):  ema_fast crosses above ema_slow on the most
    #                          recent closed candle (prev fast ≤ prev slow,
    #                          last fast > last slow)
    #   death cross   (SHORT): mirror — fast crosses below slow
    #
    # Two trigger sources searched in order:
    #   1. 4h EMA50/EMA200 (slow / structural) — preferred; high conviction
    #   2. 1h EMA21/EMA50 (faster / responsive) — secondary trigger
    #
    # SL geometry
    #   Anchored to the most recent 1h swing low (LONG) or swing high (SHORT)
    #   over the last 30 bars, with a 0.10% buffer.  ATR×1.0 fallback when no
    #   qualifying swing is found.  Capped by _MAX_SL_PCT_BY_SETUP entry
    #   "MA_CROSS_TREND_SHIFT": 3.0.
    #
    # TP geometry
    #   TP1 = 1.5R  (conservative scalp first target)
    #   TP2 = 2.5R
    #   TP3 = 3.5R  (trailing past this)

    _MA_CROSS_COOLDOWN_SEC: float = 24 * 3600.0  # 24h per (symbol, direction)
    _MA_CROSS_SL_BUFFER_PCT: float = 0.10        # buffer beyond structural swing
    _MA_CROSS_SL_LOOKBACK: int = 30              # 1h candles for swing-anchor
    _MA_CROSS_TP_R_MULT: tuple = (1.5, 2.5, 3.5)

    def _evaluate_ma_cross_trend_shift(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """MA_CROSS_TREND_SHIFT — fires on EMA50/200 (4h) or EMA21/50 (1h) cross."""
        import time as _time

        # Basic spread / volume gates always run.
        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return self._reject("basic_filters_failed")

        # Detect cross on a TF.  Returns (direction, label) on hit, None on miss.
        # `label` is a short string for telemetry / setup_class subtype.
        # Reads scalar ``*_prev`` / ``*_last`` pairs (e.g. ``ema21_prev`` +
        # ``ema21_last``) populated by ``compute_indicators_for_candle_dict``.
        # Bug 2026-05-11: this used to read full ``ind["ema21"]`` arrays,
        # which the live indicator API never populated — every call
        # returned None, producing 100% no_ma_cross reject for the
        # 15th evaluator since PR #318 shipped.
        def _detect_cross(
            ind: Dict[str, Any], fast_key: str, slow_key: str,
        ) -> Optional[tuple]:
            fast_name = fast_key.replace("_last", "")
            slow_name = slow_key.replace("_last", "")
            # Live path: scalar ``*_prev`` / ``*_last`` pairs (added by
            # compute_indicators_for_candle_dict 2026-05-11).
            f_prev = ind.get(f"{fast_name}_prev")
            f_last = ind.get(fast_key)
            s_prev = ind.get(f"{slow_name}_prev")
            s_last = ind.get(slow_key)
            # Fallback for legacy callers (test fixtures, ``diagnose_pair``)
            # that pass full EMA arrays under the bare name.  Extract the
            # last two elements to honour the scalar contract above.
            if f_prev is None or s_prev is None:
                fast_arr = ind.get(fast_name)
                slow_arr = ind.get(slow_name)
                try:
                    if fast_arr is not None and slow_arr is not None:
                        fast = list(fast_arr)
                        slow = list(slow_arr)
                        if len(fast) >= 2 and len(slow) >= 2:
                            f_prev = fast[-2] if f_prev is None else f_prev
                            f_last = fast[-1] if f_last is None else f_last
                            s_prev = slow[-2] if s_prev is None else s_prev
                            s_last = slow[-1] if s_last is None else s_last
                except (TypeError, ValueError):
                    pass
            # Missing any of the four scalars (typically at boot before two
            # candles have closed) → not detectable; fail open quietly.
            if any(v is None for v in (f_prev, f_last, s_prev, s_last)):
                return None
            f_prev = float(f_prev)
            f_last = float(f_last)
            s_prev = float(s_prev)
            s_last = float(s_last)
            # Skip if any value is NaN-ish or non-positive.
            if not (f_prev > 0 and f_last > 0 and s_prev > 0 and s_last > 0):
                return None
            # Golden cross: prev fast ≤ prev slow AND last fast > last slow.
            if f_prev <= s_prev and f_last > s_last:
                return (Direction.LONG, f"{fast_name}/{slow_name}")
            # Death cross.
            if f_prev >= s_prev and f_last < s_last:
                return (Direction.SHORT, f"{fast_name}/{slow_name}")
            return None

        ind_4h = indicators.get("4h", {})
        ind_1h = indicators.get("1h", {})

        # Try 4h EMA50/EMA200 first (high-conviction structural cross).
        result = _detect_cross(ind_4h, "ema50_last", "ema200_last")
        cross_tf = "4h"
        # Fall back to 1h EMA21/EMA50.
        if result is None:
            result = _detect_cross(ind_1h, "ema21_last", "ema50_last")
            cross_tf = "1h"
        if result is None:
            return self._reject("no_ma_cross")

        direction, cross_label = result

        # --- Higher-timeframe trend-alignment gate -------------------------
        # Research consensus across crypto MA-cross backtests: the EMA
        # *periods* are second-order — the FILTER is the edge.  A raw cross
        # whipsaws because crypto ranges ~60% of the time, so an unfiltered
        # crossover loses money; gating on higher-timeframe trend agreement is
        # what turns it positive.  The 4h 50/200 cross IS the structural trend
        # (confirmed by price below), so only the lower-conviction 1h 21/50
        # cross needs the 4h to vouch for it.
        ema50_4h = ind_4h.get("ema50_last")
        ema200_4h = ind_4h.get("ema200_last")
        if cross_tf == "1h":
            if (
                ema50_4h is None or ema200_4h is None
                or float(ema50_4h) <= 0 or float(ema200_4h) <= 0
            ):
                # No 4h trend reference → can't confirm a 1h cross → fail closed.
                return self._reject("ma_cross_htf_unconfirmed")
            htf_bull = float(ema50_4h) > float(ema200_4h)
            if (direction == Direction.LONG) != htf_bull:
                return self._reject("ma_cross_htf_misaligned")

        # Cooldown — at most one signal per (symbol, direction) per 24h.
        cd_key = (symbol, direction.value)
        last_fire = self._ma_cross_last_fire_ts.get(cd_key)
        if last_fire is not None and (_time.time() - last_fire) < self._MA_CROSS_COOLDOWN_SEC:
            return self._reject("ma_cross_cooldown")

        # Need 1m close for entry price + 1h candles for swing-anchor SL.
        m1 = candles.get("1m")
        if m1 is None or len(m1.get("close", [])) < 5:
            return self._reject("insufficient_candles")
        close = float(m1["close"][-1])
        if close <= 0:
            return self._reject("invalid_price")

        # 4h structural cross: light price-vs-EMA200 confirmation.  Only act
        # when current price sits on the cross's side of the 4h slow line —
        # filters failing / already-reverted crosses where price has snapped
        # back through EMA200.  Fail-open if the 4h EMA200 is unavailable.
        if cross_tf == "4h" and ema200_4h is not None and float(ema200_4h) > 0:
            if direction == Direction.LONG and close < float(ema200_4h):
                return self._reject("ma_cross_4h_price_below_ema200")
            if direction == Direction.SHORT and close > float(ema200_4h):
                return self._reject("ma_cross_4h_price_above_ema200")

        # Structural SL: most recent opposite-side swing on 1h within lookback.
        h1 = candles.get("1h", {})
        h1_highs = h1.get("high")
        h1_lows = h1.get("low")
        atr_1h = ind_1h.get("atr_last") if ind_1h else None
        atr_val = float(atr_1h) if atr_1h else close * 0.005

        sl_dist: Optional[float] = None
        if h1_highs is not None and h1_lows is not None:
            try:
                highs_list = list(h1_highs)[-self._MA_CROSS_SL_LOOKBACK:]
                lows_list = list(h1_lows)[-self._MA_CROSS_SL_LOOKBACK:]
                if direction == Direction.LONG and lows_list:
                    structural_low = min(float(x) for x in lows_list)
                    if structural_low < close:
                        sl_dist = (close - structural_low) * (1 + self._MA_CROSS_SL_BUFFER_PCT / 100.0)
                elif direction == Direction.SHORT and highs_list:
                    structural_high = max(float(x) for x in highs_list)
                    if structural_high > close:
                        sl_dist = (structural_high - close) * (1 + self._MA_CROSS_SL_BUFFER_PCT / 100.0)
            except (TypeError, ValueError):
                sl_dist = None

        if sl_dist is None or sl_dist <= 0:
            sl_dist = atr_val  # ATR×1.0 fallback

        if sl_dist <= 0:
            return self._reject("invalid_sl_geometry")

        sl = close - sl_dist if direction == Direction.LONG else close + sl_dist
        if direction == Direction.LONG and sl >= close:
            return self._reject("invalid_sl_geometry")
        if direction == Direction.SHORT and sl <= close:
            return self._reject("invalid_sl_geometry")

        # TP ladder — fixed R-multiples (1.5R / 2.5R / 3.5R).
        r1, r2, r3 = self._MA_CROSS_TP_R_MULT
        if direction == Direction.LONG:
            tp1 = close + sl_dist * r1
            tp2 = close + sl_dist * r2
            tp3 = close + sl_dist * r3
        else:
            tp1 = close - sl_dist * r1
            tp2 = close - sl_dist * r2
            tp3 = close - sl_dist * r3

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="MAX",
            atr_val=atr_val,
            setup_class="MA_CROSS_TREND_SHIFT",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0

        # Conviction lift: 4h cross is structurally stronger than 1h cross.
        if cross_tf == "4h":
            sig.confidence = min(100.0, sig.confidence + 10.0)
            sig.execution_note = (getattr(sig, "execution_note", "") + f"; MA cross {cross_label} on 4h").lstrip("; ")
        else:
            sig.confidence = min(100.0, sig.confidence + 5.0)
            sig.execution_note = (getattr(sig, "execution_note", "") + f"; MA cross {cross_label} on 1h").lstrip("; ")

        # Stamp cooldown — only on success so cooldown doesn't trip on rejects.
        # Persisted to disk so the cooldown survives engine restarts (without
        # this, a redeploy within 24h could let the same cross double-fire).
        self._ma_cross_last_fire_ts[cd_key] = _time.time()
        self._persist_ma_cross_cooldown()
        return sig

    # ────────────────────────────────────────────────────────────────────────
    # MEAN_REVERT — statistical mean-reversion (2026-07-15)
    # ────────────────────────────────────────────────────────────────────────
    def _evaluate_mean_revert(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """MEAN_REVERT: fade a 2.5σ over-extension on 15m closes back to the
        20-bar rolling mean, stop ±1.5·ATR beyond entry.

        Graduated from the shadow unit SHADOW_MEAN_REVERT (Autonomous
        Portfolio Phase 3) after the suppression-audit ledger forward-measured
        **+0.67R avg / 59% win over n=550** candidates across two data windows
        — the strongest strategy in the Strategy×Context edge matrix, in
        exactly the ~70% ranging/quiet tape where the trend evaluators idle.

        Detection and geometry are ``shadow_strategies.evaluate_mean_revert``
        — the SAME pure function the shadow unit stamps with, so the live path
        and its shadow control arm can never drift.  Entry/SL/TP1 are the
        measured geometry verbatim; TP2/TP3 are R-multiple extensions past the
        mean (default exit is TP1-full, matching the shadow forward-measure).
        The shadow unit keeps stamping unconditionally as the ungated control.

        Live per owner directive 2026-07-15; ``mean_revert_live`` runtime
        tunable is the instant ops off-switch (OFF → ``[SHADOW]
        MEAN_REVERT_WOULD_FIRE`` log, no signal).
        """
        tf = candles.get("15m")
        if tf is None:
            return self._reject("insufficient_candles")
        closes = tf.get("close")
        highs = tf.get("high")
        lows = tf.get("low")
        need = _MEANREV_LOOKBACK + _MEANREV_ATR_PERIOD
        if (
            closes is None or highs is None or lows is None
            or len(closes) < need or len(highs) < need or len(lows) < need
        ):
            return self._reject("insufficient_candles")

        profile = smc_data.get("pair_profile")
        if not self._pass_basic_filters(
            spread_pct, volume_24h_usd, regime=regime, profile=profile
        ):
            return self._reject("basic_filters_failed")

        cand = shadow_mean_revert(highs, lows, closes)
        if cand is None:
            return self._reject("no_extension")
        # Detection counter for the feature-liveness probe: shadow stamps
        # flowing while this stays flat = dead live wiring.
        self._mean_revert_detections += 1

        direction = Direction.LONG if cand.side == "LONG" else Direction.SHORT
        close = float(cand.entry)
        sl = float(cand.stop_loss)
        tp1 = float(cand.tp1)
        sl_dist = abs(close - sl)
        if sl_dist <= 0 or close <= 0:
            return self._reject("invalid_sl_geometry")
        # By construction tp1 (the mean) sits on the profit side of a ±2.5σ
        # extension; guard anyway so degenerate inputs can't invert the ladder.
        if (direction == Direction.LONG and tp1 <= close) or (
            direction == Direction.SHORT and tp1 >= close
        ):
            return self._reject("invalid_sl_geometry")
        # TP2/TP3: R-multiple extensions past the mean.  Exit policy is
        # TP1-full, so these only shape the residual runner if policy changes.
        if direction == Direction.LONG:
            tp2 = tp1 + sl_dist * 0.5
            tp3 = tp1 + sl_dist * 1.0
        else:
            tp2 = tp1 - sl_dist * 0.5
            tp3 = tp1 - sl_dist * 1.0

        atr_val = float(indicators.get("15m", {}).get("atr_last", 0.0) or 0.0)

        # Live/ops off-switch (runtime tunable; boot default = MEAN_REVERT_LIVE).
        if not self._mover_path_live("mean_revert_live", MEAN_REVERT_LIVE):
            log.info(
                "[SHADOW] MEAN_REVERT_WOULD_FIRE: symbol={} dir={} close={:.6f} "
                "sl={:.6f} tp1={:.6f} sl_dist_pct={:.3f} ({})",
                symbol, cand.side, close, sl, tp1,
                sl_dist / close * 100.0, cand.reason,
            )
            return self._reject("shadow_mode")

        profile = smc_data.get("pair_profile")
        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="MNRVT",
            atr_val=atr_val,
            setup_class="MEAN_REVERT",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # The measured geometry IS the edge (STRUCTURAL_SLTP_PROTECTED) —
        # re-stamp it verbatim over anything generic construction adjusted.
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        # Structural anchor for execution_quality_check's MEAN_REVERT branch:
        # the fade is judged against the mean it targets, not the generic
        # 5m-EMA trend anchor (which is structurally opposed for a fade).
        sig.mean_revert_mean = sig.tp1
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # The shadow unit measured 180-minute validity; sentinel-0 would
        # collapse it to the 15-minute channel default at dispatch.
        sig.valid_for_minutes = 180
        sig.entry_trigger = "mean_revert_z"
        # Entry-time feature stamp (2026-08-01).  Thin path — 9 dark rows, 5
        # decided — so this accumulates, it is not readable yet.
        #
        # The entry here *is* an extension measurement, so unlike the pullback
        # paths there is no hidden variable to go looking for: the z-score the
        # detector fired on is the whole thesis, and the 2.5-sigma trigger has
        # never been checked against outcomes. It comes off `cand.metrics`
        # rather than being recomputed — the detector already holds it exactly,
        # and a second computation of the same quantity is only a detector when
        # it is kept beside the first, never when it silently replaces it.
        # The reference is the 20-bar mean, which is also TP1.
        try:
            from src import entry_features as _ef

            _ef.stamp(
                sig,
                regime=regime,
                features=_ef.capture(
                    symbol=symbol,
                    direction_is_long=(direction == Direction.LONG),
                    entry=close,
                    sl_dist=sl_dist,
                    tp1=tp1,
                    trigger="mean_revert_z",
                    tf=tf,
                    tf_name="15m",
                    atr=atr_val,
                    smc_data=smc_data,
                    entry_ref=tp1,
                    entry_ref_name="rolling_mean_20",
                    extras={
                        "sigma_at_entry": cand.metrics.get("sigma_at_entry"),
                        "retrace_frac_of_leg": _ef.retrace_fraction(
                            [float(h) for h in highs],
                            [float(low_v) for low_v in lows],
                            close,
                            direction == Direction.LONG,
                        ),
                    },
                ),
            )
        except Exception as _exc:  # noqa: BLE001 — never let a stamp kill a scan
            from src import fail_open as _fo

            _fo.record("scalp.mean_revert_entry_features", _exc)
        log.info(
            "MEAN_REVERT_FIRED: symbol={} dir={} close={:.6f} sl_dist_pct={:.3f} "
            "conf={:.1f} ({})",
            symbol, cand.side, close, sl_dist / close * 100.0,
            sig.confidence, cand.reason,
        )
        return sig

    # ────────────────────────────────────────────────────────────────────────
    # RANGE_FADE — range-edge fade to mid (2026-07-18, dark + context-gated)
    # ────────────────────────────────────────────────────────────────────────
    def _evaluate_range_fade(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        """RANGE_FADE: fade a tested range edge back to the mid.  Range = 48
        closed 15m bars, width ≥ 4·ATR, ≥ 2 distinct touches per edge; stop =
        1·ATR beyond the faded edge, TP1 = the range mid, 240-min validity.

        Graduated from the shadow unit SHADOW_RANGE_FADE (Autonomous Portfolio
        Phase 3).  Strategy Lab 2026-07-18: the allocator's TOP recommendation
        in the live context (+0.841R over n=24 in ASIA/QUIET/NORMAL), with
        STRONG cells across the range/quiet contexts — but the gate audit
        measures BLANKET activation net-negative (+0.20R saved per suppressed
        candidate, n=223: NEGATIVE-cell losses outweigh STRONG-cell wins), so
        the scanner's context-edge gate additionally restricts emission to
        contexts whose SHADOW_RANGE_FADE cell carries a measured
        POSITIVE/STRONG verdict.

        Detection and geometry are ``shadow_strategies.evaluate_range_fade``
        — the SAME pure function the shadow unit stamps with, so the live path
        and its shadow control arm can never drift.  Entry/SL/TP1 are the
        measured geometry verbatim; TP2/TP3 are R-multiple extensions past the
        mid (default exit is TP1-full, matching the shadow forward-measure).
        The shadow unit keeps stamping unconditionally as the ungated control.

        DARK per production doctrine (default OFF); ``range_fade_live`` is the
        ops activation switch (OFF → ``[SHADOW] RANGE_FADE_WOULD_FIRE`` log,
        no signal).
        """
        tf = candles.get("15m")
        if tf is None:
            return self._reject("insufficient_candles")
        closes = tf.get("close")
        highs = tf.get("high")
        lows = tf.get("low")
        need = _RANGE_LOOKBACK + _MEANREV_ATR_PERIOD
        if (
            closes is None or highs is None or lows is None
            or len(closes) < need or len(highs) < need or len(lows) < need
        ):
            return self._reject("insufficient_candles")

        profile = smc_data.get("pair_profile")
        if not self._pass_basic_filters(
            spread_pct, volume_24h_usd, regime=regime, profile=profile
        ):
            return self._reject("basic_filters_failed")

        cand = shadow_range_fade(highs, lows, closes)
        if cand is None:
            return self._reject("no_range_edge")
        # Detection counter for the feature-liveness probe: shadow stamps
        # flowing while this stays flat = dead live wiring.
        self._range_fade_detections += 1

        direction = Direction.LONG if cand.side == "LONG" else Direction.SHORT
        close = float(cand.entry)
        sl = float(cand.stop_loss)
        tp1 = float(cand.tp1)
        sl_dist = abs(close - sl)
        if sl_dist <= 0 or close <= 0:
            return self._reject("invalid_sl_geometry")
        # By construction the mid sits on the profit side of an edge entry;
        # guard anyway so degenerate inputs can't invert the ladder.
        if (direction == Direction.LONG and tp1 <= close) or (
            direction == Direction.SHORT and tp1 >= close
        ):
            return self._reject("invalid_sl_geometry")
        # TP2/TP3: R-multiple extensions past the mid, toward the far edge.
        # Exit policy is TP1-full, so these only shape a residual runner if
        # policy ever changes.
        if direction == Direction.LONG:
            tp2 = tp1 + sl_dist * 0.5
            tp3 = tp1 + sl_dist * 1.0
        else:
            tp2 = tp1 - sl_dist * 0.5
            tp3 = tp1 - sl_dist * 1.0

        atr_val = float(indicators.get("15m", {}).get("atr_last", 0.0) or 0.0)

        # Live/ops activation switch (runtime tunable; boot default =
        # RANGE_FADE_LIVE, which ships false — dark-first).
        if not self._mover_path_live("range_fade_live", RANGE_FADE_LIVE):
            log.info(
                "[SHADOW] RANGE_FADE_WOULD_FIRE: symbol={} dir={} close={:.6f} "
                "sl={:.6f} tp1={:.6f} sl_dist_pct={:.3f} ({})",
                symbol, cand.side, close, sl, tp1,
                sl_dist / close * 100.0, cand.reason,
            )
            return self._reject("shadow_mode")

        _regime_ctx = smc_data.get("regime_context")
        sig = build_channel_signal(
            config=self.config,
            symbol=symbol,
            direction=direction,
            close=close,
            sl=sl,
            tp1=tp1,
            tp2=tp2,
            tp3=tp3,
            sl_dist=sl_dist,
            id_prefix="RNGFD",
            atr_val=atr_val,
            setup_class="RANGE_FADE",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return self._reject("build_signal_failed")

        # The measured geometry IS the edge (STRUCTURAL_SLTP_PROTECTED) —
        # re-stamp it verbatim over anything generic construction adjusted.
        sig.stop_loss = round(sl, 8)
        sig.tp1 = round(tp1, 8)
        sig.tp2 = round(tp2, 8)
        sig.tp3 = round(tp3, 8)
        sig.original_tp1 = sig.tp1
        sig.original_tp2 = sig.tp2
        sig.original_tp3 = sig.tp3
        sig.original_sl_distance = sl_dist
        # Structural anchor for execution_quality_check's RANGE_FADE branch:
        # the fade is judged against the mid it targets, not the generic
        # 5m-EMA trend anchor (which is structurally opposed for a fade).
        sig.range_fade_mid = sig.tp1
        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # The shadow unit measured 240-minute validity; sentinel-0 would
        # collapse it to the 15-minute channel default at dispatch.
        sig.valid_for_minutes = 240
        sig.entry_trigger = "range_fade_edge"
        # Entry-time feature stamp (2026-08-01).  One dark row in the window, so
        # purely accumulative.
        #
        # A range edge is only an edge while it holds, so the number that
        # matters is how many times it has already been tested — the detector
        # counts exactly that to qualify the range and then discards it into a
        # reason string. Range width in ATR sits beside it because a 4-ATR range
        # and a 12-ATR range are different trades with the same geometry.
        # Reference is the range mid (also TP1).
        try:
            from src import entry_features as _ef

            _ef.stamp(
                sig,
                regime=regime,
                features=_ef.capture(
                    symbol=symbol,
                    direction_is_long=(direction == Direction.LONG),
                    entry=close,
                    sl_dist=sl_dist,
                    tp1=tp1,
                    trigger="range_fade_edge",
                    tf=tf,
                    tf_name="15m",
                    atr=atr_val,
                    smc_data=smc_data,
                    entry_ref=tp1,
                    entry_ref_name="range_mid",
                    extras={
                        "edge_touches": cand.metrics.get("edge_touches"),
                        "range_width_atr": cand.metrics.get("range_width_atr"),
                    },
                ),
            )
        except Exception as _exc:  # noqa: BLE001 — never let a stamp kill a scan
            from src import fail_open as _fo

            _fo.record("scalp.range_fade_entry_features", _exc)
        log.info(
            "RANGE_FADE_FIRED: symbol={} dir={} close={:.6f} sl_dist_pct={:.3f} "
            "conf={:.1f} ({})",
            symbol, cand.side, close, sl_dist / close * 100.0,
            sig.confidence, cand.reason,
        )
        return sig
