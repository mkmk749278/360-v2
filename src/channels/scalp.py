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
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


from config import CHANNEL_SCALP, SURGE_VOLUME_MULTIPLIER, FUNDING_RATE_EXTREME_THRESHOLD, SCALP_ORB_ENABLED
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
from src.smc import Direction

# HTF EMA rejection threshold: only reject if price is within this % of EMA200
# AND moving toward it. 0.15% is more permissive than the old 0.05% — valid
# EMA tests that bounce are no longer rejected.
_HTF_EMA_REJECTION_PCT: float = float(os.getenv("HTF_EMA_REJECTION_PCT", "0.0015"))

# WHALE_MOMENTUM thresholds (absorbed from former TapeChannel)
_WHALE_DELTA_MIN_RATIO: float = 2.0
_WHALE_MIN_TICK_VOLUME_USD: float = 500_000.0
_WHALE_OBI_MIN: float = 1.5
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
_FAR_ACCEPTANCE_THRESHOLD: float = 0.002
# Minimum reclaim distance (as a multiple of ATR) required from the reference
# level to the current close.  Ensures a genuine reclaim, not a marginal tick.
_FAR_MIN_RECLAIM_ATR: float = 0.10
# RSI hard/soft thresholds.  More conservative than PDC because FAR is a
# reversal-of-failure setup (counter to the initial failed breakout direction).
_FAR_RSI_LONG_HARD_MAX: float = 75.0   # ≥ this → hard reject (overbought)
_FAR_RSI_LONG_SOFT_MIN: float = 65.0   # ≥ this (< hard) → +6 soft penalty
_FAR_RSI_SHORT_HARD_MIN: float = 25.0  # ≤ this → hard reject (oversold)
_FAR_RSI_SHORT_SOFT_MAX: float = 35.0  # ≤ this (> hard) → +6 soft penalty

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


class ScalpChannel(BaseChannel):
    def __init__(self) -> None:
        super().__init__(CHANNEL_SCALP)

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
    ) -> List[Signal]:
        # Evaluate all signal paths and return every valid candidate so that the
        # scanner can process each one independently through the gate chain.
        # Previously only the winner-takes-all best signal was returned, which
        # silently discarded all other valid setups.
        profile = smc_data.get("pair_profile") if smc_data else None
        results: List[Signal] = []
        for evaluator in (
            self._evaluate_standard,
            self._evaluate_trend_pullback,
            self._evaluate_liquidation_reversal,
            self._evaluate_whale_momentum,
            self._evaluate_volume_surge_breakout,
            self._evaluate_breakdown_short,
            self._evaluate_opening_range_breakout,
            self._evaluate_sr_flip_retest,
            self._evaluate_funding_extreme,
            self._evaluate_quiet_compression_break,
            self._evaluate_divergence_continuation,
            self._evaluate_continuation_liquidity_sweep,
            self._evaluate_post_displacement_continuation,
            self._evaluate_failed_auction_reclaim,
        ):
            sig = evaluator(symbol, candles, indicators, smc_data, spread_pct, volume_24h_usd, regime)
            if sig is not None:
                # Apply kill zone check and mark reduced-conviction signals
                sig_with_kz = self._apply_kill_zone_note(sig, profile=profile)
                results.append(sig_with_kz)
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
            return None

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
            return None
        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime, profile=profile):
            return None

        ema_fast = ind.get("ema9_last")
        ema_slow = ind.get("ema21_last")
        if ema_fast is None or ema_slow is None:
            return None

        sweeps = smc_data.get("sweeps", [])
        if not sweeps:
            return None
        sweep = sweeps[0]

        close = float(m5["close"][-1])
        atr_val = ind.get("atr_last", close * 0.002)

        mom = ind.get("momentum_last")
        if mom is None:
            return None
        # ATR-adaptive momentum threshold: scales with each pair's volatility
        # BTC (ATR ~0.3%) → threshold ~0.15%, DOGE (ATR ~0.8%) → threshold ~0.30%
        atr_pct = (atr_val / close) * 100.0 if close > 0 else 0.15
        profile = smc_data.get("pair_profile")
        base_momentum = max(0.10, min(0.30, atr_pct * 0.5))
        if profile is not None:
            base_momentum *= profile.momentum_threshold_mult
        momentum_threshold = base_momentum
        if abs(mom) < momentum_threshold:
            return None

        # Momentum persistence: require momentum above threshold for consecutive
        # candles to avoid whipsaws where a single candle briefly spikes momentum.
        mom_arr = ind.get("momentum_array")
        persist = profile.momentum_persist_candles if profile else 2
        if mom_arr is not None and len(mom_arr) >= persist:
            if not all(abs(float(mom_arr[-i])) >= momentum_threshold for i in range(1, persist + 1)):
                return None  # Momentum not persistent — likely whipsaw

        direction = sweep.direction

        # RSI extreme gate: use pair-specific OB/OS levels when available
        rsi_val = ind.get("rsi_last")
        if rsi_val is not None and profile is not None:
            from src.filters import check_rsi
            if not check_rsi(rsi_val, thresholds["rsi_ob"], thresholds["rsi_os"], direction.value):
                return None
        elif not check_rsi_regime(rsi_val, direction=direction.value, regime=regime):
            return None

        # Momentum must agree with sweep direction
        if direction == Direction.LONG and mom < 0:
            return None
        if direction == Direction.SHORT and mom > 0:
            return None

        pair_tier = profile.tier if profile else "MIDCAP"
        if not check_ema_alignment_adaptive(
            ema_fast, ema_slow, direction.value,
            atr_val=atr_val, close=close,
            regime=regime, pair_tier=pair_tier,
        ):
            return None

        # MACD confirmation gate (PR_04)
        ind_macd_last = ind.get("macd_histogram_last")
        ind_macd_prev = ind.get("macd_histogram_prev")
        strict_macd = regime.upper() in ("RANGING", "QUIET") if regime else False
        macd_ok, macd_adj = check_macd_confirmation(
            ind_macd_last, ind_macd_prev, direction.value, regime=regime, strict=strict_macd
        )
        if not macd_ok:
            return None  # Hard reject in strict mode

        # MTF gate — 1h EMA/RSI must support the 5m signal direction (PR_06)
        indicators_1h = indicators.get("1h", {})
        mtf_ok, mtf_reason, mtf_adj = mtf_gate_scalp_standard(indicators_1h, direction.value, regime)
        if not mtf_ok:
            return None

        # HTF EMA200 rejection gate: reject entry if price is within 0.15% of EMA200
        # AND moving toward it (not if it just touched and bounced).
        # Use 1h indicators for HTF EMA200 if available, else 5m.
        _htf_ema200 = indicators_1h.get("ema200_last") or ind.get("ema200_last")
        if _htf_ema200 is not None and _htf_ema200 > 0:
            _ema200_diff_pct = abs(close - _htf_ema200) / _htf_ema200
            if _ema200_diff_pct < _HTF_EMA_REJECTION_PCT:
                # Only reject if price is moving TOWARD the EMA200 (not bouncing away)
                _prev_close = float(m5["close"][-2]) if len(m5["close"]) >= 2 else close
                _moving_toward = (
                    (direction == Direction.LONG and close < _htf_ema200 and close < _prev_close)
                    or (direction == Direction.SHORT and close > _htf_ema200 and close > _prev_close)
                )
                if _moving_toward:
                    return None

        # Structure-based SL: use swept level ± buffer if available, else ATR fallback
        _sweep = sweeps[0] if sweeps else None
        _sweep_level = None
        if _sweep is not None:
            # Try multiple attribute names used by different SMC implementations
            _sweep_level = getattr(_sweep, "level", None) or getattr(_sweep, "price", None) or getattr(_sweep, "sweep_level", None)
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
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

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
        if tp2 <= 0 or (direction == Direction.LONG and tp2 <= tp1) or (direction == Direction.SHORT and tp2 >= tp1):
            tp2 = close + sl_dist * 2.5 if direction == Direction.LONG else close - sl_dist * 2.5
        tp3 = close + sl_dist * 4.0 if direction == Direction.LONG else close - sl_dist * 4.0

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
            return None

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
        """TREND_PULLBACK_EMA path: price pulls back to EMA9/EMA21 in trend direction."""
        # Only fire in trending regimes
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "TRENDING_UP":
            direction = Direction.LONG
        elif regime_upper == "TRENDING_DOWN":
            direction = Direction.SHORT
        else:
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 50:
            return None

        ind = indicators.get("5m", {})
        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        ema50 = ind.get("ema50_last")
        rsi_val = ind.get("rsi_last")

        if ema9 is None or ema21 is None:
            return None

        close = float(m5["close"][-1])
        opens = m5.get("open", [])
        if len(opens) < 1:
            return None
        last_open = float(opens[-1])

        # EMA alignment check
        if direction == Direction.LONG:
            if ema50 is not None and not (ema9 > ema21 > ema50):
                return None
            elif ema50 is None and not (ema9 > ema21):
                return None
        else:
            if ema50 is not None and not (ema9 < ema21 < ema50):
                return None
            elif ema50 is None and not (ema9 < ema21):
                return None

        # Price proximity to EMA9 (0.3%) or EMA21 (0.5%)
        near_ema9 = abs(close - ema9) / ema9 <= 0.003 if ema9 > 0 else False
        near_ema21 = abs(close - ema21) / ema21 <= 0.005 if ema21 > 0 else False
        if not (near_ema9 or near_ema21):
            return None

        # RSI pullback zone: 40–60
        if rsi_val is not None and not (40 <= rsi_val <= 60):
            return None

        # Last candle rejection: close > open for LONG, close < open for SHORT
        if direction == Direction.LONG and close <= last_open:
            return None
        if direction == Direction.SHORT and close >= last_open:
            return None

        # SMC: require at least one FVG or orderblock in the pullback zone
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        has_smc_support = bool(fvgs) or bool(orderblocks)
        if not has_smc_support:
            return None

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close * 0.002)
        # SL: beyond EMA21 for both directions
        sl_dist = max(close * self.config.sl_pct_range[0] / 100, abs(close - ema21) * 1.1)
        sl_dist = max(sl_dist, atr_val * 0.5)
        sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

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
            if direction == Direction.LONG and tp2 <= tp1:
                tp2 = close + sl_dist * 2.0
            if direction == Direction.SHORT and tp2 >= tp1:
                tp2 = close - sl_dist * 2.0
        else:
            tp2 = close + sl_dist * 2.0 if direction == Direction.LONG else close - sl_dist * 2.0

        # TP3: ratio fallback
        tp3 = close + 4.0 * sl_dist if direction == Direction.LONG else close - 4.0 * sl_dist

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
            return None

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
            return None

        closes = m5.get("close", [])
        volumes = m5.get("volume", [])
        if len(closes) < 4 or len(volumes) < 21:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        # 1. Cascade detection: last 3 candles moved > 2.0% in one direction
        close_now = float(closes[-1])
        close_3ago = float(closes[-4])
        if close_3ago <= 0:
            return None
        cascade_pct = (close_now - close_3ago) / close_3ago * 100.0

        if cascade_pct <= -2.0:
            cascade_direction = Direction.SHORT  # Price fell — potential LONG reversal
            reversal_direction = Direction.LONG
        elif cascade_pct >= 2.0:
            cascade_direction = Direction.LONG   # Price rose — potential SHORT reversal
            reversal_direction = Direction.SHORT
        else:
            return None

        # 2. CVD divergence: price moving one way, CVD moving opposite
        cvd_data = smc_data.get("cvd")
        if cvd_data is None:
            # CVD unavailable — skip this path gracefully
            return None
        cvd_values = cvd_data if isinstance(cvd_data, list) else cvd_data.get("values", [])
        if len(cvd_values) < 4:
            return None
        cvd_now = float(cvd_values[-1])
        cvd_3ago = float(cvd_values[-4])
        cvd_change = cvd_now - cvd_3ago

        # For LONG reversal: price fell but CVD is rising (buyers absorbing)
        if reversal_direction == Direction.LONG and cvd_change <= 0:
            return None
        # For SHORT reversal: price rose but CVD is falling (sellers absorbing)
        if reversal_direction == Direction.SHORT and cvd_change >= 0:
            return None

        ind = indicators.get("5m", {})
        rsi_val = ind.get("rsi_last")

        # 3. RSI extreme gate
        if reversal_direction == Direction.LONG:
            if rsi_val is not None and rsi_val >= 25:
                return None  # Not oversold enough after cascade
        else:
            if rsi_val is not None and rsi_val <= 75:
                return None  # Not overbought enough after cascade

        # 4. Price within 0.5% of a known orderblock or FVG zone
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        near_zone = False
        for zone in list(fvgs) + list(orderblocks):
            zone_level = zone.gap_low if hasattr(zone, "gap_low") else (
                zone.get("level") if isinstance(zone, dict) else None
            )
            if zone_level is None and hasattr(zone, "price"):
                zone_level = zone.price
            if zone_level is not None and zone_level > 0:
                if abs(close_now - float(zone_level)) / float(zone_level) <= 0.005:
                    near_zone = True
                    break
        if not near_zone:
            return None

        # 5. Volume spike: last candle volume > 2.5x 20-candle average
        avg_vol = sum(float(v) for v in volumes[-21:-1]) / 20.0 if len(volumes) >= 21 else 0.0
        last_vol = float(volumes[-1])
        if avg_vol <= 0 or last_vol < 2.5 * avg_vol:
            return None

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close_now * 0.002)

        # SL: beyond cascade extremum + 0.3% buffer
        sl_buffer = close_now * 0.003
        _cascade_slice = [float(c) for c in closes[-4:]]
        cascade_low = min(_cascade_slice)
        cascade_high = max(_cascade_slice)
        cascade_range = cascade_high - cascade_low
        if reversal_direction == Direction.LONG:
            sl = cascade_low - sl_buffer
        else:
            sl = cascade_high + sl_buffer

        sl_dist = abs(close_now - sl)
        if sl_dist <= 0:
            return None

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
            return None

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
        # Block in QUIET regime — whale momentum setups require directional flow and
        # volume that QUIET markets structurally lack.  This is a setup-specific gate
        # that mirrors the same pattern used by VOLUME_SURGE_BREAKOUT and
        # BREAKDOWN_SHORT.  It does not affect any other evaluator path.
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "QUIET":
            return None

        whale = smc_data.get("whale_alert")
        delta_spike = smc_data.get("volume_delta_spike", False)
        if whale is None and not delta_spike:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        m1 = candles.get("1m")
        if m1 is None or len(m1.get("close", [])) < 10:
            return None

        close = float(m1["close"][-1])

        ticks: List[Dict[str, Any]] = smc_data.get("recent_ticks", [])
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
            return None

        if buy_vol >= sell_vol * _WHALE_DELTA_MIN_RATIO:
            direction = Direction.LONG
        elif sell_vol >= buy_vol * _WHALE_DELTA_MIN_RATIO:
            direction = Direction.SHORT
        else:
            return None

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
                    return None  # Hard reject: extreme overbought invalidates momentum thesis
                if _WHALE_RSI_LONG_SOFT_MIN <= rsi_val_1m < _WHALE_RSI_LONG_HARD_MAX:
                    rsi_penalty = 5.0  # Borderline: penalise but still allow
            else:
                if rsi_val_1m <= _WHALE_RSI_SHORT_HARD_MIN:
                    return None  # Hard reject: extreme oversold invalidates momentum thesis
                if _WHALE_RSI_SHORT_HARD_MIN < rsi_val_1m <= _WHALE_RSI_SHORT_SOFT_MAX:
                    rsi_penalty = 5.0  # Borderline: penalise but still allow

        # Order book imbalance — confirms the dominant side matches the whale
        # direction.
        #
        # Three-tier behaviour:
        #   1. order_book is None (circuit breaker open): skip OBI entirely;
        #      flag obi_confirmed=False so a +10 soft penalty is applied.
        #   2. order_book present, ratio ≥ _WHALE_OBI_MIN (1.5×): full
        #      confirmation, no OBI penalty.
        #   3. order_book present, ratio in [_WHALE_OBI_SOFT_MIN, _WHALE_OBI_MIN)
        #      AND regime is a fast/volatile regime: marginal OBI treated as a
        #      soft contributor (+8 penalty) rather than hard rejection.  In fast
        #      regimes depth books are routinely thin due to market-maker spread
        #      widening; tick flow and whale alert carry more weight.
        #   4. order_book present, ratio < _WHALE_OBI_MIN in a calm regime, or
        #      ratio < _WHALE_OBI_SOFT_MIN in any regime: hard reject — the order
        #      book actively contradicts the assumed whale direction.
        order_book = smc_data.get("order_book")
        obi_confirmed = False
        obi_penalty = 0.0
        if order_book is not None:
            bids = order_book.get("bids", [])
            asks = order_book.get("asks", [])
            bid_depth = sum(float(b[1]) * float(b[0]) for b in bids[:10])
            ask_depth = sum(float(a[1]) * float(a[0]) for a in asks[:10])
            if bid_depth <= 0 or ask_depth <= 0:
                return None
            imbalance_ratio = (
                bid_depth / ask_depth if direction == Direction.LONG else ask_depth / bid_depth
            )
            if imbalance_ratio >= _WHALE_OBI_MIN:
                obi_confirmed = True
            elif regime_upper in _WHALE_FAST_REGIMES and imbalance_ratio >= _WHALE_OBI_SOFT_MIN:
                # Marginal OBI in a fast regime: soft penalty, not hard reject
                obi_penalty = 8.0
            else:
                return None

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
        if sig is not None:
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
        # Block only in QUIET — surge setups need volume, which QUIET lacks.
        # VOLATILE/VOLATILE_UNSUITABLE are explicitly allowed here.
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "QUIET":
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 28:
            return None

        closes = m5.get("close", [])
        highs = m5.get("high", [])
        volumes = m5.get("volume", [])
        if len(closes) < 28 or len(highs) < 28 or len(volumes) < 10:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        # Rolling 7-candle average (last 7 complete candles, not current)
        rolling_vols = [float(v) for v in volumes[-8:-1]]
        if len(rolling_vols) < 7 or sum(rolling_vols) <= 0:
            return None
        rolling_avg = sum(rolling_vols) / len(rolling_vols)

        # Current 5m candle volume ≥ SURGE_VOLUME_MULTIPLIER × rolling average
        # (use current candle volume to confirm active surge, same units as rolling_avg)
        current_vol = float(volumes[-1]) if len(volumes) >= 1 else 0.0
        if current_vol < SURGE_VOLUME_MULTIPLIER * rolling_avg:
            return None

        # Swing high: 20-candle lookback from before the 5-candle breakout search window.
        # Excluding the search window ensures swing_high is set by genuine prior resistance,
        # not by the candles we are testing as the breakout event itself.
        # Layout: [...swing_high window (20)│breakout search (5)│current (1)]
        #          highs[-26:-6]              highs[-6:-1]         highs[-1]
        swing_high_level = max(float(h) for h in highs[-26:-6])
        if swing_high_level <= 0:
            return None

        # Find the most recent breakout candle within the last 5 closed candles.
        # Scans newest-first (i = -2, -3, -4, -5, -6) to prefer the candle
        # closest to the current bar. Candle at -1 is still forming.
        breakout_candle_idx: Optional[int] = None
        breakout_vol = 0.0
        for i in range(-2, -7, -1):  # iterates -2, -3, -4, -5, -6
            if float(highs[i]) > swing_high_level:
                breakout_candle_idx = i
                breakout_vol = float(volumes[i])
                break

        if breakout_candle_idx is None:
            return None

        # Pullback zone: current close is below the swing high (breakout retest).
        # Lower bound: 0.1% ensures the price has made a genuine pullback below the
        # broken resistance level rather than entering right at the top.
        # Upper bound: 0.75% is a practical limit given the 0.8% structural SL
        # placement — pullbacks deeper than the SL distance are rejected by the
        # sl>=close check below, so this bound makes the logic explicit.
        # Premium zone (0.3%–0.6%) captures textbook breakout-retest geometry and
        # earns a confidence bonus.  The extended zone (0.1%–0.3% and 0.6%–0.75%)
        # represents shallow sprints or near-SL entries; a soft penalty is applied.
        close = float(closes[-1])
        if close <= 0:
            return None
        dist_from_swing_pct = (swing_high_level - close) / swing_high_level * 100.0
        if not (0.1 <= dist_from_swing_pct <= 0.75):
            return None
        pullback_in_premium_zone = (0.3 <= dist_from_swing_pct <= 0.6)
        pullback_penalty = 0.0 if pullback_in_premium_zone else 3.0

        # Condition 4: EMA9 > EMA21 (trend alignment, hard gate unchanged)
        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None or ema9 <= ema21:
            return None

        # RSI — layered soft/hard gate replacing the previous hard gate of 45–72.
        # Hard block below 40 (momentum failure) or above 82 (extreme overbought
        # exhaustion at entry).  Borderline 40–44 or 73–82 attracts a soft penalty;
        # optimal zone 45–72 passes with no adjustment.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if rsi_val < 40.0 or rsi_val > 82.0:
                return None
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
                return None  # Hard gate in non-fast regimes (behaviour unchanged)
            fvg_penalty = 8.0  # Soft penalty in fast regimes instead of hard block

        # Breakout candle volume ≥ 2.0 × rolling average (unchanged quality threshold;
        # now checks the actual breakout candle's volume rather than always volumes[-3]).
        if breakout_vol < 2.0 * rolling_avg:
            return None

        # Method-specific SL/TP
        sl = swing_high_level * (1 - 0.008)  # 0.8% below breakout level
        sl_dist = abs(close - sl)
        if sl_dist <= 0 or sl >= close:
            return None

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
        atr_val = ind.get("atr_last", close * 0.002)
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
            return None

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
        # Block only in QUIET — breakdown setups need volume, which QUIET lacks.
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "QUIET":
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 28:
            return None

        closes = m5.get("close", [])
        lows = m5.get("low", [])
        highs = m5.get("high", [])
        volumes = m5.get("volume", [])
        if len(closes) < 28 or len(lows) < 28 or len(volumes) < 10:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        # Rolling 7-candle average (last 7 complete candles, not current)
        rolling_vols = [float(v) for v in volumes[-8:-1]]
        if len(rolling_vols) < 7 or sum(rolling_vols) <= 0:
            return None
        rolling_avg = sum(rolling_vols) / len(rolling_vols)

        # Current 5m candle volume ≥ SURGE_VOLUME_MULTIPLIER × rolling average
        # (use current candle volume to confirm active surge, same units as rolling_avg)
        current_vol = float(volumes[-1]) if len(volumes) >= 1 else 0.0
        if current_vol < SURGE_VOLUME_MULTIPLIER * rolling_avg:
            return None

        # Swing low: 20-candle lookback from before the 5-candle breakdown search window.
        # Excluding the search window ensures swing_low is set by genuine prior support,
        # not by the candles we are testing as the breakdown event itself.
        # Layout: [...swing_low window (20)│breakdown search (5)│current (1)]
        #          lows[-26:-6]             lows[-6:-1]           lows[-1]
        # The search iterates indices -2, -3, -4, -5, -6 (newest-first within the window).
        swing_low_level = min(float(l) for l in lows[-26:-6])
        if swing_low_level <= 0:
            return None

        # Find the most recent breakdown candle within the last 5 closed candles.
        # Scans newest-first (i = -2, -3, -4, -5, -6) to prefer the candle
        # closest to the current bar. Candle at -1 is still forming.
        breakdown_candle_idx: Optional[int] = None
        breakdown_vol = 0.0
        for i in range(-2, -7, -1):  # iterates -2, -3, -4, -5, -6
            if float(lows[i]) < swing_low_level:
                breakdown_candle_idx = i
                breakdown_vol = float(volumes[i])
                break

        if breakdown_candle_idx is None:
            return None

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
            return None
        dist_from_swing_pct = (close - swing_low_level) / swing_low_level * 100.0
        if not (0.1 <= dist_from_swing_pct <= 0.75):
            return None
        bounce_in_premium_zone = (0.3 <= dist_from_swing_pct <= 0.6)
        bounce_penalty = 0.0 if bounce_in_premium_zone else 3.0

        # EMA9 < EMA21 (trend alignment, hard gate unchanged)
        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None or ema9 >= ema21:
            return None

        # RSI — layered soft/hard gate replacing the previous hard gate of 28–55.
        # Hard block below 20 (full capitulation, no tradeable dead-cat bounce) or
        # above 68 (too bullish, bearish continuation thesis breaks down).
        # Borderline 20–27 or 56–68 attracts a soft penalty; optimal 28–55 passes
        # with no adjustment.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if rsi_val < 20.0 or rsi_val > 68.0:
                return None
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
                return None  # Hard gate in non-fast regimes (behaviour unchanged)
            fvg_penalty = 8.0  # Soft penalty in fast regimes instead of hard block

        # Breakdown candle volume ≥ 2.0 × rolling average (unchanged quality threshold;
        # now checks the actual breakdown candle's volume rather than always volumes[-3]).
        if breakdown_vol < 2.0 * rolling_avg:
            return None

        # Method-specific SL/TP
        sl = swing_low_level * (1 + 0.008)  # 0.8% above breakdown level
        sl_dist = abs(close - sl)
        if sl_dist <= 0 or sl <= close:
            return None

        # TP: measured move downward projection (window aligned with swing low window)
        base_of_range = max(float(h) for h in highs[-26:-6]) if len(highs) >= 26 else close * 1.02
        measured_move = base_of_range - swing_low_level
        if measured_move <= 0:
            measured_move = sl_dist * 2.0

        tp1 = close - measured_move
        tp2 = close - measured_move * 1.5
        tp3 = close - measured_move * 2.0

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close * 0.002)
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
            return None

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
        if not SCALP_ORB_ENABLED:
            return None
        now_hour = datetime.now(timezone.utc).hour
        # Only active during London (07:00–08:59 UTC) or NY (12:00–13:59 UTC)
        in_london = 7 <= now_hour < 9
        in_ny = 12 <= now_hour < 14
        if not (in_london or in_ny):
            return None

        regime_upper = regime.upper() if regime else ""
        if regime_upper in ("QUIET", "RANGING"):
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return None

        closes = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        volumes = m5.get("volume", [])
        if len(closes) < 20 or len(highs) < 20 or len(lows) < 20 or len(volumes) < 21:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        # Opening range = the 4 candles immediately before the most recent 4,
        # acting as a proxy for the first 4 candles of the session window.
        range_highs = [float(h) for h in highs[-8:-4]]
        range_lows = [float(l) for l in lows[-8:-4]]
        if not range_highs or not range_lows:
            return None
        range_high = max(range_highs)
        range_low = min(range_lows)
        range_height = range_high - range_low
        if range_height <= 0:
            return None

        close = float(closes[-1])
        if close <= 0:
            return None

        # Entry direction
        if close > range_high:
            direction = Direction.LONG
        elif close < range_low:
            direction = Direction.SHORT
        else:
            return None

        # Volume: current candle >= 1.5x 20-candle avg
        avg_vol = sum(float(v) for v in volumes[-21:-1]) / 20.0 if len(volumes) >= 21 else 0.0
        current_vol = float(volumes[-1])
        if avg_vol <= 0 or current_vol < 1.5 * avg_vol:
            return None

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return None

        # EMA9 aligned in signal direction
        if direction == Direction.LONG and ema9 <= ema21:
            return None
        if direction == Direction.SHORT and ema9 >= ema21:
            return None

        # SMC basis: at least one FVG or orderblock
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return None

        # SL and TP
        if direction == Direction.LONG:
            sl = range_low * (1 - 0.001)
            tp1 = close + range_height * 1.0
            tp2 = close + range_height * 1.5
            tp3 = close + range_height * 2.0
        else:
            sl = range_high * (1 + 0.001)
            tp1 = close - range_height * 1.0
            tp2 = close - range_height * 1.5
            tp3 = close - range_height * 2.0

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return None
        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close * 0.002)
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
            return None

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
        - Rejection candle strictness reduced from a hard-50% wick rule to a layered
          soft/hard gate: wick < 20% of body is a hard reject (no rejection evidence
          at the structural level).  Wick 20%–50% of body accumulates a +4.0 soft
          penalty (borderline rejection — valid but weaker structural push-back).
          Wick ≥ 50% of body passes with no penalty (clear hammer / shooting star).
          Doji (zero body) always passes — indecision at structure is inherently valid.
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
        if regime_upper == "VOLATILE":
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 55:
            return None

        closes = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        opens = m5.get("open", [])
        if len(closes) < 55 or len(highs) < 55 or len(lows) < 55 or len(opens) < 1:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        close = float(closes[-1])
        if close <= 0:
            return None

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
        prior_highs = [float(h) for h in highs[-50:-9]]
        prior_lows = [float(l) for l in lows[-50:-9]]
        recent_highs = [float(h) for h in highs[-9:-1]]
        recent_lows = [float(l) for l in lows[-9:-1]]

        prior_swing_high = max(prior_highs)
        prior_swing_low = min(prior_lows)

        # Bullish flip: any candle in the 8-candle window broke prior swing high → LONG
        if max(recent_highs) > prior_swing_high:
            direction = Direction.LONG
            level = prior_swing_high
        # Bearish flip: any candle in the 8-candle window broke prior swing low → SHORT
        elif min(recent_lows) < prior_swing_low:
            direction = Direction.SHORT
            level = prior_swing_low
        else:
            return None

        # Retest proximity gate — layered zone system replacing the original hard-0.3% gate.
        # Premium zone (0–0.3% from flipped level) → no soft penalty.
        # Extended zone (0.3%–0.6%) → +3.0 soft penalty (messier but valid retest).
        # Hard block beyond 0.6% — price has not genuinely returned to the structural level.
        if level <= 0:
            return None
        dist_from_level_pct = abs(close - level) / level
        if dist_from_level_pct > 0.006:
            return None
        retest_in_premium_zone = dist_from_level_pct <= 0.003
        proximity_penalty = 0.0 if retest_in_premium_zone else 3.0

        # Rejection candle check — layered soft/hard gate replacing the original hard-50% rule.
        # A clear rejection wick (≥50% of candle body) is the ideal structural signal.
        # Borderline wicks (20%–50%) are weaker but still pass with a +4.0 soft penalty.
        # No meaningful wick (<20% of body) is hard-rejected — the candle shows no
        # structural push-back at the level.  Doji (zero body) always passes — indecision
        # at structure is a valid retest signature.
        last_open = float(opens[-1])
        last_high = float(highs[-1])
        last_low = float(lows[-1])
        candle_body = abs(close - last_open)
        wick_penalty = 0.0
        if candle_body > 0:
            if direction == Direction.LONG:
                lower_wick = last_open - last_low if last_open > last_low else close - last_low
                if lower_wick < 0.2 * candle_body:
                    return None  # No meaningful rejection at support
                if lower_wick < 0.5 * candle_body:
                    wick_penalty = 4.0  # Borderline rejection — apply soft penalty
            else:
                upper_wick = last_high - last_open if last_high > last_open else last_high - close
                if upper_wick < 0.2 * candle_body:
                    return None  # No meaningful rejection at resistance
                if upper_wick < 0.5 * candle_body:
                    wick_penalty = 4.0  # Borderline rejection — apply soft penalty

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return None

        if direction == Direction.LONG and ema9 <= ema21:
            return None
        if direction == Direction.SHORT and ema9 >= ema21:
            return None

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
                    return None
                if rsi_val >= 70.0:
                    rsi_penalty = 5.0
            else:
                if rsi_val <= 20.0:
                    return None
                if rsi_val <= 30.0:
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
                return None  # Hard gate in calm regimes (behaviour unchanged)
            fvg_penalty = 8.0  # Soft penalty in fast structural regimes

        # SL beyond flipped level (structural invalidation point — unchanged)
        if direction == Direction.LONG:
            sl = level * (1 - 0.002)
        else:
            sl = level * (1 + 0.002)

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return None
        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

        # TP1: 20-candle swing high/low
        if direction == Direction.LONG:
            tp1 = max(float(h) for h in highs[-21:-1]) if len(highs) >= 21 else 0.0
            if tp1 <= close:
                tp1 = close + sl_dist * 1.5
        else:
            tp1 = min(float(low_val) for low_val in lows[-21:-1]) if len(lows) >= 21 else 0.0
            if tp1 >= close:
                tp1 = close - sl_dist * 1.5

        # TP2: 4h target or fallback
        candles_4h = candles.get("4h")
        if candles_4h and len(candles_4h.get("high", [])) >= 5:
            _4h_highs = candles_4h.get("high", [])
            _4h_lows = candles_4h.get("low", [])
            if direction == Direction.LONG:
                tp2 = max(float(h) for h in _4h_highs[-10:]) if _4h_highs else close + sl_dist * 1.5
                if tp2 <= tp1:
                    tp2 = close + sl_dist * 1.5
            else:
                tp2 = min(float(low_val) for low_val in _4h_lows[-10:]) if _4h_lows else close - sl_dist * 1.5
                if tp2 >= tp1:
                    tp2 = close - sl_dist * 1.5
        else:
            tp2 = close + sl_dist * 1.5 if direction == Direction.LONG else close - sl_dist * 1.5
            if direction == Direction.LONG and tp2 <= tp1:
                tp2 = tp1 + sl_dist
            if direction == Direction.SHORT and tp2 >= tp1:
                tp2 = tp1 - sl_dist

        tp3 = close + sl_dist * 3.5 if direction == Direction.LONG else close - sl_dist * 3.5

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close * 0.002)
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
            return None

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

        # Accumulate soft penalties — the scanner deducts these from confidence after
        # the composite scoring pass, preserving the separation between hard gates and
        # soft quality adjustments.
        total_penalty = proximity_penalty + wick_penalty + rsi_penalty + fvg_penalty
        if total_penalty > 0.0:
            sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + total_penalty

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
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "QUIET":
            return None

        funding_rate = smc_data.get("funding_rate")
        if funding_rate is None:
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 5:
            return None

        closes = m5.get("close", [])
        if len(closes) < 5:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        close = float(closes[-1])
        if close <= 0:
            return None

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
                return None
            if rsi_last is not None and rsi_last >= 55:
                return None
            if rsi_prev is not None and rsi_last is not None and rsi_last <= rsi_prev:
                return None
            if cvd_change is not None and cvd_change <= 0:
                return None
            direction = Direction.LONG
        # SHORT signal: deeply positive funding → shorts being discounted
        elif funding_rate > FUNDING_RATE_EXTREME_THRESHOLD:
            if ema9 is None or close >= ema9:
                return None
            if rsi_last is not None and rsi_last <= 45:
                return None
            if rsi_prev is not None and rsi_last is not None and rsi_last >= rsi_prev:
                return None
            if cvd_change is not None and cvd_change >= 0:
                return None
            direction = Direction.SHORT
        else:
            return None

        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return None

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

        if sl_dist is None or sl_dist <= 0:
            sl_dist = atr_val * 1.5

        sl = close - sl_dist if direction == Direction.LONG else close + sl_dist
        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

        # TP1: nearest FVG/OB structure level in the direction of travel.
        # The path already requires FVG/OB confluence at entry, so the nearest
        # qualifying structure level is the natural first normalization target.
        # Falls back to 1.5R when no qualifying level is found — better than
        # the previous flat 0.5% placeholder which was not thesis-aligned.
        tp1 = _funding_extreme_structure_tp1(fvgs, orderblocks, close, direction, sl_dist)

        tp2 = close + sl_dist * 2.0 if direction == Direction.LONG else close - sl_dist * 2.0
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
            id_prefix="FUND",
            atr_val=atr_val,
            setup_class="FUNDING_EXTREME_SIGNAL",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return None

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
        """QUIET_COMPRESSION_BREAK: Bollinger Band squeeze breakout."""
        regime_upper = regime.upper() if regime else ""
        if regime_upper not in ("QUIET", "RANGING"):
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 25:
            return None

        closes = m5.get("close", [])
        volumes = m5.get("volume", [])
        if len(closes) < 25 or len(volumes) < 21:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        close = float(closes[-1])
        if close <= 0:
            return None

        ind = indicators.get("5m", {})
        bb_upper = ind.get("bb_upper_last")
        bb_lower = ind.get("bb_lower_last")
        if bb_upper is None or bb_lower is None:
            return None

        bb_upper = float(bb_upper)
        bb_lower = float(bb_lower)

        # Compression check: band width / close < 1.5%
        if (bb_upper - bb_lower) / close >= 0.015:
            return None

        # Entry direction
        if close > bb_upper:
            direction = Direction.LONG
        elif close < bb_lower:
            direction = Direction.SHORT
        else:
            return None

        # MACD histogram zero-cross
        macd_hist_last = ind.get("macd_histogram_last")
        macd_hist_prev = ind.get("macd_histogram_prev")
        if macd_hist_last is not None and macd_hist_prev is not None:
            if direction == Direction.LONG and not (macd_hist_last > 0 and macd_hist_prev < 0):
                return None
            if direction == Direction.SHORT and not (macd_hist_last < 0 and macd_hist_prev > 0):
                return None

        # Volume: current >= 2.0x 20-candle avg
        avg_vol = sum(float(v) for v in volumes[-21:-1]) / 20.0
        current_vol = float(volumes[-1])
        if avg_vol <= 0 or current_vol < 2.0 * avg_vol:
            return None

        # RSI
        rsi_val = ind.get("rsi_last")
        if rsi_val is not None:
            if direction == Direction.LONG and not (50 <= rsi_val <= 70):
                return None
            if direction == Direction.SHORT and not (30 <= rsi_val <= 50):
                return None

        # SMC: FVG preferred, fallback to orderblocks
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return None

        # SL and TP
        if direction == Direction.LONG:
            sl = bb_lower * (1 - 0.001)
        else:
            sl = bb_upper * (1 + 0.001)

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return None
        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

        band_width = bb_upper - bb_lower
        if band_width > 0:
            if direction == Direction.LONG:
                tp1 = close + band_width * 0.5
                tp2 = close + band_width * 1.0
                tp3 = close + band_width * 1.5
            else:
                tp1 = close - band_width * 0.5
                tp2 = close - band_width * 1.0
                tp3 = close - band_width * 1.5
        else:
            tp1 = close + sl_dist * 1.5 if direction == Direction.LONG else close - sl_dist * 1.5
            tp2 = close + sl_dist * 2.5 if direction == Direction.LONG else close - sl_dist * 2.5
            tp3 = close + sl_dist * 4.0 if direction == Direction.LONG else close - sl_dist * 4.0

        profile = smc_data.get("pair_profile")
        atr_val = ind.get("atr_last", close * 0.002)
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
            return None

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
        sig.confidence = min(100.0, sig.confidence + 4.0)
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
        """DIVERGENCE_CONTINUATION: hidden CVD divergence in trending regime."""
        regime_upper = regime.upper() if regime else ""
        if regime_upper == "TRENDING_UP":
            direction = Direction.LONG
        elif regime_upper == "TRENDING_DOWN":
            direction = Direction.SHORT
        else:
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return None

        closes_raw = m5.get("close", [])
        highs = m5.get("high", [])
        lows = m5.get("low", [])
        if len(closes_raw) < 20:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        cvd_data = smc_data.get("cvd")
        if cvd_data is None:
            return None

        cvd_values = cvd_data if isinstance(cvd_data, list) else cvd_data.get("values", [])
        if len(cvd_values) < 20:
            return None

        closes = [float(c) for c in closes_raw]
        cvd_floats = [float(v) for v in cvd_values]

        close = closes[-1]
        if close <= 0:
            return None

        # CVD divergence detection (price vs CVD divergence signals absorption)
        if direction == Direction.LONG:
            price_low_early = min(closes[-20:-10])
            price_low_late = min(closes[-10:])
            cvd_low_early = min(cvd_floats[-20:-10])
            cvd_low_late = min(cvd_floats[-10:])
            # Bullish CVD divergence: price makes lower low but CVD makes higher low
            # (buyers absorbing selling pressure — continuation signal in uptrend)
            if not (price_low_late < price_low_early and cvd_low_late > cvd_low_early):
                return None
            # Divergence magnitude: how far price pulled back that CVD absorbed.
            # Normalised so a 3 % price drop = strength 1.0; capped at 1.0.
            _price_drop_pct = (price_low_early - price_low_late) / price_low_early if price_low_early > 0 else 0.0
            _div_strength = min(1.0, _price_drop_pct / 0.03)
            _div_label: str = "BULLISH"
        else:
            price_high_early = max(closes[-20:-10])
            price_high_late = max(closes[-10:])
            cvd_high_early = max(cvd_floats[-20:-10])
            cvd_high_late = max(cvd_floats[-10:])
            # Bearish CVD divergence: price makes higher high but CVD makes lower high
            # (sellers absorbing buying pressure — continuation signal in downtrend)
            if not (price_high_late > price_high_early and cvd_high_late < cvd_high_early):
                return None
            _price_rise_pct = (price_high_late - price_high_early) / price_high_early if price_high_early > 0 else 0.0
            _div_strength = min(1.0, _price_rise_pct / 0.03)
            _div_label = "BEARISH"

        # Propagate confirmed divergence evidence to smc_data so the downstream
        # composite scorer (PR-09) sees the evaluator's actual thesis signal.
        # Only overwrite when the evaluator's local detection is definitive — the
        # evaluator passes all checks above only when divergence is confirmed.
        smc_data["cvd_divergence"] = _div_label
        smc_data["cvd_divergence_strength"] = _div_strength

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return None

        # Price within 1.5% of EMA21
        if ema21 <= 0 or abs(close - ema21) / ema21 > 0.015:
            return None

        # EMA alignment
        if direction == Direction.LONG and ema9 <= ema21:
            return None
        if direction == Direction.SHORT and ema9 >= ema21:
            return None

        # SMC basis
        fvgs = smc_data.get("fvg", [])
        orderblocks = smc_data.get("orderblocks", [])
        if not (fvgs or orderblocks):
            return None

        # SL: beyond EMA21
        if direction == Direction.LONG:
            sl = ema21 * (1 - 0.005)
        else:
            sl = ema21 * (1 + 0.005)

        sl_dist = abs(close - sl)
        if sl_dist <= 0:
            return None
        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

        # TP1: previous swing high/low from the divergence detection window.
        # The divergence pattern is detected over closes[-20:]; the highest high
        # (lowest low for SHORT) in that same window is the natural first target —
        # the swing from which price diverged and where divergence resolves.
        if direction == Direction.LONG:
            _div_win_highs = [float(h) for h in highs[-20:]] if len(highs) >= 20 else []
            tp1 = max(_div_win_highs) if _div_win_highs else 0.0
            if tp1 <= close:
                tp1 = close + sl_dist * 1.5
        else:
            _div_win_lows = [float(low_val) for low_val in lows[-20:]] if len(lows) >= 20 else []
            tp1 = min(_div_win_lows) if _div_win_lows else close  # close triggers fallback below
            if tp1 >= close:
                tp1 = close - sl_dist * 1.5

        # TP2: 20-candle 5m swing high/low — structural confirmation level.
        if direction == Direction.LONG:
            tp2 = max(float(h) for h in highs[-20:]) if len(highs) >= 20 else 0.0
            if tp2 <= close:
                tp2 = close + sl_dist * 2.5
        else:
            tp2 = min(float(low_val) for low_val in lows[-20:]) if len(lows) >= 20 else close
            if tp2 >= close:
                tp2 = close - sl_dist * 2.5

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
        atr_val = ind.get("atr_last", close * 0.002)
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
            return None

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
        """CONTINUATION_LIQUIDITY_SWEEP: sweep-confirmed trend continuation.

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
        # Hard block regimes where the continuation thesis does not apply:
        # - VOLATILE/VOLATILE_UNSUITABLE: chaotic orderflow invalidates structure
        # - RANGING/QUIET: no directional trend exists to continue
        regime_upper = regime.upper() if regime else ""
        if regime_upper not in _CLS_VALID_REGIMES:
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return None

        # Direction determined by EMA alignment — this is a trend-following path
        if ema9 > ema21:
            direction = Direction.LONG
        elif ema9 < ema21:
            direction = Direction.SHORT
        else:
            return None  # EMAs converged — no trend direction

        # Cross-validate direction against strongly-stated directional regimes
        if regime_upper == "TRENDING_DOWN" and direction == Direction.LONG:
            return None  # EMA not aligned with the established downtrend
        if regime_upper == "TRENDING_UP" and direction == Direction.SHORT:
            return None  # EMA not aligned with the established uptrend

        closes_raw = m5.get("close", [])
        close = float(closes_raw[-1])
        if close <= 0:
            return None

        # ADX gate: trend continuation requires meaningful trend strength
        profile = smc_data.get("pair_profile")
        thresholds = self._get_pair_adjusted_thresholds(profile)
        adx_val = ind.get("adx_last")
        if adx_val is not None and adx_val < thresholds["adx_min"]:
            return None

        # Sweep detection: must have a recent sweep in the trend continuation
        # direction (i.e. swept the stops of participants against the trend,
        # then recovered — confirming a liquidity grab rather than a break).
        sweeps = smc_data.get("sweeps", [])
        if not sweeps:
            return None

        trend_sweep = None
        for sweep in sweeps:
            if sweep.direction == direction:
                trend_sweep = sweep
                break
        if trend_sweep is None:
            return None

        # Sweep recency gate: sweep must be within the last _CLS_SWEEP_WINDOW
        # closed candles.  Staleer sweeps lose their structural relevance.
        sweep_index = getattr(trend_sweep, "index", None)
        if sweep_index is None or sweep_index < -_CLS_SWEEP_WINDOW:
            return None

        # Sweep level extraction
        sweep_level: Optional[float] = None
        for attr in ("level", "price", "sweep_level"):
            v = getattr(trend_sweep, attr, None)
            if v is not None:
                sweep_level = float(v)
                break
        if sweep_level is None or sweep_level <= 0:
            return None

        # Reclaim confirmation: current price must already be beyond the swept
        # level in the trend direction.  This is the defining gate that separates
        # CLS from a still-in-progress LIQUIDITY_SWEEP_REVERSAL — the sweep must
        # already be resolved before this path fires.
        if direction == Direction.LONG and close <= sweep_level:
            return None  # Price hasn't reclaimed above sweep level yet
        if direction == Direction.SHORT and close >= sweep_level:
            return None  # Price hasn't reclaimed below sweep level yet

        # Momentum agreement: must confirm trend direction (hard gate)
        mom = ind.get("momentum_last")
        if mom is None:
            return None
        if direction == Direction.LONG and mom <= 0:
            return None
        if direction == Direction.SHORT and mom >= 0:
            return None

        # RSI layered gate: hard reject only at true exhaustion extremes;
        # soft penalty in the borderline zone — same pattern as WHALE_MOMENTUM.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= _CLS_RSI_LONG_HARD_MAX:
                    return None  # Hard reject: overbought — continuation exhausted
                if rsi_val >= _CLS_RSI_LONG_SOFT_MIN:
                    rsi_penalty = 6.0
            else:
                if rsi_val <= _CLS_RSI_SHORT_HARD_MIN:
                    return None  # Hard reject: oversold — continuation exhausted
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
        atr_val = ind.get("atr_last", close * 0.002)
        atr_buffer = atr_val * 0.3
        if direction == Direction.LONG:
            sl = sweep_level - atr_buffer
        else:
            sl = sweep_level + atr_buffer

        sl_dist = abs(close - sl)
        min_sl_dist = atr_val * 0.5
        if sl_dist < min_sl_dist:
            sl_dist = min_sl_dist
            sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

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
        if tp2 <= 0 or (direction == Direction.LONG and tp2 <= tp1) or (direction == Direction.SHORT and tp2 >= tp1):
            tp2 = close + sl_dist * 2.5 if direction == Direction.LONG else close - sl_dist * 2.5
        tp3 = close + sl_dist * 4.0 if direction == Direction.LONG else close - sl_dist * 4.0

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
            return None

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
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return None

        closes_raw = m5.get("close", [])
        opens_raw = m5.get("open", [])
        highs_raw = m5.get("high", [])
        lows_raw = m5.get("low", [])
        volumes_raw = m5.get("volume", [])

        n = len(closes_raw)
        if (n < 20 or len(opens_raw) < n
                or len(highs_raw) < n or len(lows_raw) < n or len(volumes_raw) < n):
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        ind = indicators.get("5m", {})
        ema9 = ind.get("ema9_last")
        ema21 = ind.get("ema21_last")
        if ema9 is None or ema21 is None:
            return None

        # Direction from EMA alignment — displacement must agree with the trend
        if ema9 > ema21:
            direction = Direction.LONG
        elif ema9 < ema21:
            direction = Direction.SHORT
        else:
            return None  # EMAs converged — no trend direction

        # Cross-validate direction against strongly stated directional regimes
        if regime_upper == "TRENDING_DOWN" and direction == Direction.LONG:
            return None  # EMA not aligned with the established downtrend
        if regime_upper == "TRENDING_UP" and direction == Direction.SHORT:
            return None  # EMA not aligned with the established uptrend

        close = float(closes_raw[-1])
        if close <= 0:
            return None

        # ADX gate: trend strength required for displacement to be valid
        profile = smc_data.get("pair_profile")
        thresholds = self._get_pair_adjusted_thresholds(profile)
        adx_val = ind.get("adx_last")
        if adx_val is not None and adx_val < thresholds["adx_min"]:
            return None

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
            return None
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
            return None

        disp_high, disp_low, disp_body, consol_high, consol_low, consol_avg_vol, disp_vol = (
            displacement_found
        )

        # ── Re-acceleration breakout gate ───────────────────────────────
        # Current close must have broken beyond the consolidation range in the
        # displacement direction.  This is the defining moment of the setup.
        if direction == Direction.LONG and close <= consol_high:
            return None  # Not yet broken above consolidation ceiling
        if direction == Direction.SHORT and close >= consol_low:
            return None  # Not yet broken below consolidation floor

        # ── RSI layered gate ─────────────────────────────────────────────
        # Hard reject at true exhaustion extremes; soft penalty in borderline zone.
        # Same layered pattern as WHALE_MOMENTUM and CLS.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= _PDC_RSI_LONG_HARD_MAX:
                    return None  # Hard reject: extreme overbought exhaustion
                if rsi_val >= _PDC_RSI_LONG_SOFT_MIN:
                    rsi_penalty = 6.0
            else:
                if rsi_val <= _PDC_RSI_SHORT_HARD_MIN:
                    return None  # Hard reject: extreme oversold exhaustion
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
        atr_val = ind.get("atr_last", close * 0.002)
        atr_buffer = atr_val * 0.3
        if direction == Direction.LONG:
            sl = consol_low - atr_buffer
        else:
            sl = consol_high + atr_buffer

        sl_dist = abs(close - sl)
        min_sl_dist = atr_val * 0.5
        if sl_dist < min_sl_dist:
            sl_dist = min_sl_dist
            sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

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
            return None

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
            return None

        m5 = candles.get("5m")
        if m5 is None or len(m5.get("close", [])) < 20:
            return None

        closes_raw = m5.get("close", [])
        highs_raw = m5.get("high", [])
        lows_raw = m5.get("low", [])

        n = len(closes_raw)
        if n < 20 or len(highs_raw) < n or len(lows_raw) < n:
            return None

        if not self._pass_basic_filters(spread_pct, volume_24h_usd, regime=regime):
            return None

        ind = indicators.get("5m", {})
        atr_val = ind.get("atr_last")
        if atr_val is None or atr_val <= 0:
            return None

        close = float(closes_raw[-1])
        if close <= 0:
            return None

        # ── Reference structure levels ───────────────────────────────────
        # Compute prior swing high and low from history BEFORE the auction
        # window.  This prevents the auction candle itself from shifting the
        # reference (a candle that probed far below/above the prior range
        # would lower/raise the reference, negating the breakout detection).
        # Exclude the full auction window (_FAR_AUCTION_WINDOW_MAX bars) so that
        # no auction-window candle contaminates the struct reference level.
        struct_end = n - 1 - _FAR_AUCTION_WINDOW_MAX   # exclusive end
        struct_start = max(0, struct_end - _FAR_STRUCT_LOOKBACK)
        if struct_end <= struct_start:
            return None

        struct_highs = [float(highs_raw[i]) for i in range(struct_start, struct_end)]
        struct_lows = [float(lows_raw[i]) for i in range(struct_start, struct_end)]
        if not struct_highs or not struct_lows:
            return None
        struct_high = max(struct_highs)
        struct_low = min(struct_lows)
        if struct_high <= struct_low:
            return None

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
            return None

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
            return None

        # ── RSI layered gate ─────────────────────────────────────────────
        # More conservative thresholds than PDC because FAR is a reversal-of-
        # failure structure: entering when RSI is near exhaustion contradicts
        # the thesis that price is genuinely rejecting and reclaiming.
        rsi_val = ind.get("rsi_last")
        rsi_penalty = 0.0
        if rsi_val is not None:
            if direction == Direction.LONG:
                if rsi_val >= _FAR_RSI_LONG_HARD_MAX:
                    return None  # Hard reject: overbought — reclaim won't hold
                if rsi_val >= _FAR_RSI_LONG_SOFT_MIN:
                    rsi_penalty = 6.0
            else:
                if rsi_val <= _FAR_RSI_SHORT_HARD_MIN:
                    return None  # Hard reject: oversold — reclaim won't hold
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
            sl = auction_wick_extreme - atr_buffer
        else:
            sl = auction_wick_extreme + atr_buffer

        sl_dist = abs(close - sl)
        min_sl_dist = atr_val * 0.5
        if sl_dist < min_sl_dist:
            sl_dist = min_sl_dist
            sl = close - sl_dist if direction == Direction.LONG else close + sl_dist

        if direction == Direction.LONG and sl >= close:
            return None
        if direction == Direction.SHORT and sl <= close:
            return None

        # ── TP: measured move from failed-auction tail (Type C) ───────────
        # The "tail" is the distance the auction probed beyond the reference
        # level before being rejected.  Projecting an equal move from the
        # current entry in the reclaim direction gives a measured-move target
        # that is directly calibrated to the strength of the rejection.
        if direction == Direction.LONG:
            tail = reclaim_level - auction_wick_extreme  # how far below level it went
        else:
            tail = auction_wick_extreme - reclaim_level  # how far above level it went

        if tail <= 0:
            tail = sl_dist  # fallback: use SL distance as proxy

        if direction == Direction.LONG:
            tp1 = close + tail * 1.0
            tp2 = close + tail * 1.5
            tp3 = close + tail * 2.5
        else:
            tp1 = close - tail * 1.0
            tp2 = close - tail * 1.5
            tp3 = close - tail * 2.5

        # Ensure minimum R:R geometry
        if direction == Direction.LONG and tp1 <= close:
            tp1 = close + sl_dist * 1.5
        if direction == Direction.SHORT and tp1 >= close:
            tp1 = close - sl_dist * 1.5
        if direction == Direction.LONG and tp2 <= tp1:
            tp2 = close + sl_dist * 2.5
        if direction == Direction.SHORT and tp2 >= tp1:
            tp2 = close - sl_dist * 2.5

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
            return None

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

        total_penalty = rsi_penalty + fvg_ob_penalty
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
