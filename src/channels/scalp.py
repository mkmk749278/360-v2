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


from config import CHANNEL_SCALP
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

# Regime-adaptive ADX floor for the standard scalp path.  In RANGING/QUIET
# markets ADX hovers at 15-20 and blocks most liquidity-sweep setups.
# Absolute minimum prevents the gate from becoming too permissive.
_ADX_RANGING_FLOOR: float = 12.0
# Multiplier applied to the pair-specific adx_min in RANGING/QUIET regimes.
_ADX_RANGING_MULTIPLIER: float = 0.75


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
            return {"order_flow": 1.5, "trend": 0.7, "volume": 1.3}
        if regime_upper in ("QUIET", "RANGING"):
            return {"order_flow": 0.8, "trend": 0.75, "volume": 0.9}
        if regime_upper in ("TRENDING_UP", "TRENDING_DOWN"):
            # Trend-following signals preferred in trending markets
            return {"order_flow": 1.0, "trend": 1.5, "volume": 1.0}
        return {"order_flow": 1.0, "trend": 1.0, "volume": 1.0}

    def evaluate(
        self,
        symbol: str,
        candles: Dict[str, dict],
        indicators: Dict[str, dict],
        smc_data: dict,
        spread_pct: float,
        volume_24h_usd: float,
        regime: str = "",
    ) -> Optional[Signal]:
        # Evaluate all signal paths and return the one with the best R-multiple,
        # adjusted by regime-specific indicator weight multipliers so that the
        # most appropriate signal type is preferred for the current market regime.
        weights = self._select_indicator_weights(regime)
        # Each tuple is (signal, adjusted_r_multiple) for regime-aware selection.
        scored: List[tuple] = []
        for evaluator, weight_key in (
            (self._evaluate_standard,              "trend"),
            (self._evaluate_trend_pullback,        "trend"),
            (self._evaluate_liquidation_reversal,  "order_flow"),
            (self._evaluate_whale_momentum,        "order_flow"),
        ):
            sig = evaluator(symbol, candles, indicators, smc_data, spread_pct, volume_24h_usd, regime)
            if sig is not None:
                # Boost the effective R-multiple by the regime weight so that
                # regime-preferred signal types rank higher in the selection.
                adjusted_r = sig.r_multiple * weights[weight_key]
                scored.append((sig, adjusted_r))
        if not scored:
            return None
        # Return the candidate with the best regime-adjusted risk-reward
        best, _ = max(scored, key=lambda t: t[1])
        # Apply kill zone check and mark reduced-conviction signals
        profile = smc_data.get("pair_profile") if smc_data else None
        result = self._apply_kill_zone_note(best, profile=profile)
        return result

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

        _regime_ctx = smc_data.get("regime_context")
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
            id_prefix="SCALP",
            atr_val=atr_val,
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return None

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

        _regime_ctx = smc_data.get("regime_context")
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
            id_prefix="TPULLBACK",
            atr_val=atr_val,
            setup_class="TREND_PULLBACK_EMA",
            regime=regime,
            atr_percentile=_regime_ctx.atr_percentile if _regime_ctx else 50.0,
            pair_tier=profile.tier if profile else "MIDCAP",
        )
        if sig is None:
            return None

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
        if reversal_direction == Direction.LONG:
            cascade_low = min(float(closes[-4:]))
            sl = cascade_low - sl_buffer
        else:
            cascade_high = max(float(closes[-4:]))
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

        sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
        sig.trailing_stage = 0
        sig.partial_close_pct = 0.0
        # High-conviction setup: multiple confirming factors required
        sig.confidence = min(100.0, sig.confidence + 10.0)
        return sig

    # ------------------------------------------------------------------
    # WHALE_MOMENTUM path (absorbed from former TapeChannel)
    # Large volume spike + OBI imbalance
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

        # RSI extreme gate: don't chase overbought LONGs or fade oversold SHORTs
        if not check_rsi_regime(indicators.get("1m", {}).get("rsi_last"), direction=direction.value, regime=regime):
            return None

        # Order book imbalance check — confirms the dominant side matches the
        # whale direction.  When order_book is unavailable (e.g. depth circuit
        # breaker open) the check is skipped rather than hard-rejecting: the
        # primary whale signals (alert, delta spike, tick flow) are sufficient
        # to identify the setup; OBI is a confirmation layer.  Missing OBI is
        # flagged via obi_confirmed=False so the scanner can apply a penalty.
        order_book = smc_data.get("order_book")
        obi_confirmed = False
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
            if imbalance_ratio < _WHALE_OBI_MIN:
                return None
            obi_confirmed = True

        atr_val = indicators.get("1m", {}).get("atr_last", close * 0.002)
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
            sig.trailing_atr_mult_effective = self.config.trailing_atr_mult
            sig.trailing_stage = 0
            sig.partial_close_pct = 0.0
            if not obi_confirmed:
                # No order book available — signal is valid on tick-flow alone
                # but carries lower certainty; apply a soft confidence penalty
                # so only very strong whale setups pass the min_confidence gate.
                sig.soft_penalty_total = getattr(sig, "soft_penalty_total", 0.0) + 10.0
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
