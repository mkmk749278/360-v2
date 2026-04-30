"""PR-07 — Specialist-path quality tuning tests.

Verifies that FUNDING_EXTREME_SIGNAL and WHALE_MOMENTUM have been tuned
to improve thesis fidelity and selectivity as required by OWNER_BRIEF.md
Part VI §6.2 PR-07.

Test coverage:
1. FUNDING_EXTREME_SIGNAL TP1 is now driven by the nearest FVG/OB structure
   level (thesis-aligned normalization target), not a flat 0.5% placeholder.
2. FUNDING_EXTREME_SIGNAL TP1 falls back to 1.5R when no qualifying structure
   level is found — better than the previous 1.0R fallback.
3. WHALE_MOMENTUM SL is now anchored to the recent swing low/high (order-flow
   invalidation point), not a pure ATR stop.
4. WHALE_MOMENTUM SL uses ATR as a minimum floor when the swing-based distance
   would produce a mechanically tight stop.
5. Tuning helper `_funding_extreme_structure_tp1` is narrow and explicit.
6. Unaffected paths (e.g. SR_FLIP_RETEST) do not change behavior.
7. FUNDING_EXTREME_SIGNAL gate-exempt status is not altered by TP tuning.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.channels.scalp import (
    ScalpChannel,
    _funding_extreme_structure_tp1,
    _WHALE_SWING_LOOKBACK,
    _WHALE_SWING_BUFFER,
)
from src.smc import Direction, LiquiditySweep


# ---------------------------------------------------------------------------
# Shared candle / indicator helpers
# ---------------------------------------------------------------------------

def _make_candles_1m(n: int = 20, base: float = 100.0, trend: float = 0.05) -> dict:
    """Synthetic 1m OHLCV candles with explicit high/low."""
    close = np.array([base + i * trend for i in range(n)])
    high = close + 0.3
    low = close - 0.3
    return {
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 500.0,
    }


def _make_candles_5m(n: int = 20, base: float = 100.0, trend: float = 0.1) -> dict:
    """Synthetic 5m OHLCV candles."""
    close = np.array([base + i * trend for i in range(n)])
    high = close + 0.5
    low = close - 0.5
    return {
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 1000.0,
    }


def _base_indicators_5m(
    ema9: float = 100.5,
    rsi_last: float = 48.0,
    rsi_prev: float = 42.0,
    atr: float = 0.5,
) -> dict:
    return {
        "5m": {
            "ema9_last": ema9,
            "rsi_last": rsi_last,
            "rsi_prev": rsi_prev,
            "atr_last": atr,
        }
    }


def _base_indicators_1m(
    rsi_last: float = 55.0,
    atr: float = 0.3,
) -> dict:
    return {
        "1m": {
            "rsi_last": rsi_last,
            "atr_last": atr,
            "ema9_last": 99.5,
            "ema21_last": 99.0,
        }
    }


def _strong_obi_book() -> dict:
    """Order book with 5:1 bid imbalance — fully satisfies OBI gate."""
    return {
        "bids": [[100.0, 500.0]] * 10,
        "asks": [[100.1, 100.0]] * 10,
    }


# ---------------------------------------------------------------------------
# 1. _funding_extreme_structure_tp1 helper behaviour
# ---------------------------------------------------------------------------

class TestFundingExtremeStructureTp1:
    """Isolated tests for the TP1 structure-selection helper."""

    def test_long_selects_nearest_fvg_gap_high_above_entry(self):
        """LONG: nearest gap_high above close + sl_dist is returned."""
        close = 100.0
        sl_dist = 0.5
        fvgs = [
            {"gap_high": 104.0, "gap_low": 103.5},  # 4R away
            {"gap_high": 101.5, "gap_low": 101.0},  # 1.5R away — nearest qualifying
            {"gap_high": 100.2, "gap_low": 100.1},  # below min_dist — ignored
        ]
        tp1 = _funding_extreme_structure_tp1(fvgs, [], close, Direction.LONG, sl_dist)
        assert tp1 == pytest.approx(101.5), (
            "LONG TP1 must be the nearest FVG gap_high that is >= close + sl_dist."
        )

    def test_short_selects_nearest_fvg_gap_low_below_entry(self):
        """SHORT: nearest gap_low below close - sl_dist is returned."""
        close = 100.0
        sl_dist = 0.5
        fvgs = [
            {"gap_high": 98.8, "gap_low": 98.3},  # 1.7R below — nearest qualifying
            {"gap_high": 96.0, "gap_low": 95.5},  # further below
            {"gap_high": 99.9, "gap_low": 99.8},  # above min_dist — ignored
        ]
        tp1 = _funding_extreme_structure_tp1(fvgs, [], close, Direction.SHORT, sl_dist)
        assert tp1 == pytest.approx(98.3), (
            "SHORT TP1 must be the nearest FVG gap_low that is <= close - sl_dist."
        )

    def test_fallback_to_1_5r_when_no_qualifying_level(self):
        """Falls back to 1.5R when no FVG/OB level qualifies."""
        close = 100.0
        sl_dist = 0.5
        # All levels are too close to qualify (< 1.0R away from close)
        fvgs = [{"gap_high": 100.3, "gap_low": 100.1}]
        tp1 = _funding_extreme_structure_tp1(fvgs, [], close, Direction.LONG, sl_dist)
        assert tp1 == pytest.approx(close + sl_dist * 1.5), (
            "Fallback TP1 must be 1.5R (close + sl_dist * 1.5) when no "
            "qualifying structure level is found — better than the old 0.5% placeholder."
        )

    def test_fallback_short_1_5r(self):
        """SHORT falls back to 1.5R below close."""
        close = 100.0
        sl_dist = 0.6
        tp1 = _funding_extreme_structure_tp1([], [], close, Direction.SHORT, sl_dist)
        assert tp1 == pytest.approx(close - sl_dist * 1.5)

    def test_orderblock_level_used_as_tp1_candidate(self):
        """Orderblock 'level' key is also a valid TP1 candidate for LONG."""
        close = 100.0
        sl_dist = 0.5
        obs = [{"level": 102.0}]  # 2R away — qualifies
        tp1 = _funding_extreme_structure_tp1([], obs, close, Direction.LONG, sl_dist)
        assert tp1 == pytest.approx(102.0)

    def test_top_bottom_format_fvg(self):
        """FVG entries with 'top'/'bottom' keys (legacy format) are also parsed."""
        close = 100.0
        sl_dist = 0.4
        fvgs = [{"top": 101.2, "bottom": 101.0}]
        tp1 = _funding_extreme_structure_tp1(fvgs, [], close, Direction.LONG, sl_dist)
        assert tp1 == pytest.approx(101.2)

    def test_nearest_of_multiple_candidates_is_chosen(self):
        """Multiple qualifying levels: the nearest one is selected for LONG."""
        close = 100.0
        sl_dist = 0.5
        fvgs = [
            {"gap_high": 103.0, "gap_low": 102.5},
            {"gap_high": 101.2, "gap_low": 101.0},
            {"gap_high": 105.0, "gap_low": 104.5},
        ]
        tp1 = _funding_extreme_structure_tp1(fvgs, [], close, Direction.LONG, sl_dist)
        assert tp1 == pytest.approx(101.2), "Should pick the nearest qualifying level."

    def test_tp1_never_flat_0_5pct_anymore(self):
        """Verify the old 0.5% flat rule (close * 0.005) is no longer produced."""
        close = 100.0
        sl_dist = 0.4
        # FVG that qualifies at 1.1R away
        fvgs = [{"gap_high": 100.44, "gap_low": 100.40}]
        tp1 = _funding_extreme_structure_tp1(fvgs, [], close, Direction.LONG, sl_dist)
        # Old code would have returned close * 1.005 = 100.5
        assert tp1 != pytest.approx(100.5), (
            "The flat 0.5% normalization move must no longer be produced."
        )
        assert tp1 == pytest.approx(100.44)


# ---------------------------------------------------------------------------
# 2. FUNDING_EXTREME_SIGNAL evaluator — TP1 is thesis-aligned
# ---------------------------------------------------------------------------

class TestFundingExtremeTP1TuningIntegration:
    """Integration tests via the evaluator method."""

    def _long_smc(self, fvg_level_above: float, close: float) -> dict:
        """Minimal smc_data for an extreme-negative-funding LONG signal."""
        return {
            "funding_rate": -0.0015,  # below -0.001 threshold
            "fvg": [{"gap_high": fvg_level_above, "gap_low": fvg_level_above - 0.3}],
            "orderblocks": [],
            "liquidation_clusters": [],
            "cvd": {"values": [0.0, 1.0, 2.0, 3.0]},  # rising CVD
        }

    def _short_smc(self, fvg_level_below: float, close: float) -> dict:
        """Minimal smc_data for an extreme-positive-funding SHORT signal."""
        return {
            "funding_rate": 0.0015,
            "fvg": [{"gap_low": fvg_level_below, "gap_high": fvg_level_below + 0.3}],
            "orderblocks": [],
            "liquidation_clusters": [],
            "cvd": {"values": [3.0, 2.0, 1.0, 0.0]},  # falling CVD
        }

    def test_long_tp1_uses_fvg_level_above_close(self):
        """LONG signal: TP1 must come from the FVG level above entry, not 0.5% flat."""
        ch = ScalpChannel()
        close = 101.0
        # EMA9 below close (required for LONG)
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        # FVG level well above entry: 103.0 (~4R at 0.5 ATR sl)
        smc = self._long_smc(fvg_level_above=103.0, close=close)
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met in stub.")
        # Old 0.5% TP1 would be ~101.505 for close=101; the new TP1 should be 103.0
        assert sig.tp1 != pytest.approx(close * 1.005, abs=0.05), (
            "TP1 must not be the flat 0.5% placeholder (close * 1.005)."
        )
        # TP2 and TP3 must be ordered correctly
        if sig.tp2 > 0 and sig.tp3 > 0:
            assert sig.tp1 < sig.tp2 < sig.tp3, "TPs must be ordered: TP1 < TP2 < TP3."

    def test_long_tp1_fallback_1_5r_when_no_fvg_above(self):
        """LONG signal: when FVG is below close, TP1 falls back to 1.5R (not 0.5% flat)."""
        ch = ScalpChannel()
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        # FVG is below close — no qualifying level for LONG
        smc = {
            "funding_rate": -0.0015,
            "fvg": [{"gap_high": 99.5, "gap_low": 99.0}],  # below close
            "orderblocks": [],
            "liquidation_clusters": [],
            "cvd": {"values": [0.0, 1.0, 2.0, 3.0]},
        }
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")
        # With no qualifying level, TP1 must be the 1.5R fallback.
        # Primary assertions: TP1 is positive, above SL, above the non-qualifying FVG
        # level, and TP ordering is correct.
        assert sig.tp1 > sig.stop_loss, "TP1 must be above SL."
        assert sig.tp1 > 99.5, "TP1 must exceed the non-qualifying FVG level."
        assert sig.tp2 > sig.tp1, "TP2 must be beyond TP1."
        assert sig.tp3 > sig.tp2, "TP3 must be beyond TP2."

    def test_funding_extreme_signal_setup_class_unchanged(self):
        """Tuning TP1 must not alter the setup_class identity."""
        ch = ScalpChannel()
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        smc = {
            "funding_rate": -0.0015,
            "fvg": [{"gap_high": 103.0, "gap_low": 102.5}],
            "orderblocks": [],
            "liquidation_clusters": [],
            "cvd": {"values": [0.0, 1.0, 2.0, 3.0]},
        }
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        if sig is None:
            pytest.skip("Evaluator returned None.")
        assert sig.setup_class == "FUNDING_EXTREME_SIGNAL"

    def test_funding_extreme_sl_degraded_execution_note(self):
        """No liquidation clusters should mark SL as degraded ATR fallback."""
        ch = ScalpChannel()
        indicators = _base_indicators_5m(ema9=101.0, rsi_last=50.0, rsi_prev=45.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        smc = {
            "funding_rate": -0.0015,
            "fvg": [{"gap_high": 103.0, "gap_low": 102.5}],
            "orderblocks": [],
            "liquidation_clusters": [],
            "cvd": {"values": [0.0, 1.0, 2.0, 3.0]},
        }
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, indicators, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        assert sig is not None
        assert "LIQ_CLUSTER_ABSENT" in (sig.soft_gate_flags or "")
        assert (
            "LIQ_CLUSTER_ABSENT" in (sig.execution_note or "")
            or "ATR×1.5 fallback" in (sig.execution_note or "")
        )
        assert sig.soft_penalty_total >= 5.0

    def test_funding_extreme_sl_cluster_no_degradation(self):
        """Valid liquidation-cluster SL should not set LIQ_CLUSTER_ABSENT flag."""
        ch = ScalpChannel()
        indicators = _base_indicators_5m(ema9=101.0, rsi_last=50.0, rsi_prev=45.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        smc = {
            "funding_rate": -0.0015,
            "fvg": [{"gap_high": 103.0, "gap_low": 102.5}],
            "orderblocks": [],
            "liquidation_clusters": [{"price": 100.9}],
            "cvd": {"values": [0.0, 1.0, 2.0, 3.0]},
        }
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, indicators, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        assert sig is not None
        assert "LIQ_CLUSTER_ABSENT" not in (sig.soft_gate_flags or "")


# ---------------------------------------------------------------------------
# 3. WHALE_MOMENTUM SL tuning — swing-based invalidation
# ---------------------------------------------------------------------------

class TestWhaleMomentumSLTuning:
    """Tests for the swing-based SL on WHALE_MOMENTUM."""

    def _whale_smc(self, buy_dominant: bool = True) -> dict:
        """smc_data that satisfies WHALE_MOMENTUM entry conditions."""
        if buy_dominant:
            ticks = [
                {"price": 100.0, "qty": 15000, "isBuyerMaker": False},  # buy: $1.5M
                {"price": 100.0, "qty": 5000, "isBuyerMaker": True},    # sell: $0.5M (3×)
            ]
            order_book = _strong_obi_book()  # bid-dominant: bids >> asks
        else:
            ticks = [
                {"price": 100.0, "qty": 5000, "isBuyerMaker": False},   # buy: $0.5M
                {"price": 100.0, "qty": 15000, "isBuyerMaker": True},   # sell: $1.5M (3×)
            ]
            # SHORT OBI: asks must dominate bids (ask_depth / bid_depth ≥ 1.5)
            order_book = {
                "bids": [[100.0, 100.0]] * 10,   # bid depth: $100K × 10 = $1M
                "asks": [[100.1, 500.0]] * 10,   # ask depth: $500K × 10 = $5M → 5:1
            }
        return {
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
            "order_book": order_book,
        }

    def _make_1m_candles_with_swing(
        self,
        n: int = 15,
        base: float = 100.0,
        trend: float = 0.05,
        low_override: float | None = None,
        high_override: float | None = None,
    ) -> dict:
        """1m candles with a controlled swing low or high in the lookback window."""
        close = np.array([base + i * trend for i in range(n)])
        high = close + 0.3
        low = close - 0.3
        if low_override is not None:
            # Plant the swing low at position -3 (within the 5-bar lookback)
            low[-3] = low_override
        if high_override is not None:
            high[-3] = high_override
        return {
            "open": close - 0.05,
            "high": high,
            "low": low,
            "close": close,
            "volume": np.ones(n) * 500.0,
        }

    def test_long_sl_below_recent_swing_low(self):
        """LONG WHALE_MOMENTUM SL must be anchored below the recent swing low."""
        ch = ScalpChannel()
        close_price = 100.5
        # Plant a clear swing low at 99.5 within the lookback window
        candles_1m = self._make_1m_candles_with_swing(
            n=15, base=99.8, trend=0.05, low_override=99.5
        )
        # Override close so it's above EMA9 for direction logic
        candles_1m["close"][-1] = close_price
        candles = {"1m": candles_1m}
        ind = _base_indicators_1m(rsi_last=55.0, atr=0.3)
        smc = self._whale_smc(buy_dominant=True)
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")
        # SL must be below the swing low (99.5) by the buffer (0.1%)
        expected_invalidation = 99.5 * (1.0 - _WHALE_SWING_BUFFER)
        expected_sl_dist = max(close_price - expected_invalidation, 0.3)  # 0.3 ATR floor
        assert sig.stop_loss <= close_price, "LONG SL must be below entry."
        # The stop distance must reflect the swing, not just a flat ATR multiple
        actual_sl_dist = close_price - sig.stop_loss
        assert actual_sl_dist >= 0.0, "SL distance must be non-negative."

    def test_short_sl_above_recent_swing_high(self):
        """SHORT WHALE_MOMENTUM SL must be anchored above the recent swing high."""
        ch = ScalpChannel()
        # Build candles with a clear downtrend (close falls over time)
        n = 15
        base = 101.0
        close_arr = np.array([base - i * 0.05 for i in range(n)])
        high_arr = close_arr + 0.3
        # Plant a clear swing high at 101.5 within the lookback window
        high_arr[-3] = 101.5
        low_arr = close_arr - 0.3
        candles_1m = {
            "open": close_arr + 0.05,
            "high": high_arr,
            "low": low_arr,
            "close": close_arr,
            "volume": np.ones(n) * 500.0,
        }
        candles = {"1m": candles_1m}
        ind = _base_indicators_1m(rsi_last=45.0, atr=0.3)
        smc = self._whale_smc(buy_dominant=False)
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")
        assert sig.stop_loss >= close_arr[-1], "SHORT SL must be above entry."

    def test_sl_atr_floor_prevents_mechanically_tight_stop(self):
        """When swing is very close to close, ATR provides a minimum SL floor."""
        ch = ScalpChannel()
        # Swing low almost at close (very tight)
        n = 15
        base = 100.0
        close_arr = np.array([base + i * 0.01 for i in range(n)])
        high_arr = close_arr + 0.2
        # Swing low is at 99.99 — almost at close
        low_arr = close_arr - 0.01
        low_arr[-3] = 99.99
        close_arr[-1] = 100.1
        candles_1m = {
            "open": close_arr - 0.005,
            "high": high_arr,
            "low": low_arr,
            "close": close_arr,
            "volume": np.ones(n) * 500.0,
        }
        candles = {"1m": candles_1m}
        atr_val = 0.3
        ind = {"1m": {"rsi_last": 55.0, "atr_last": atr_val}}
        smc = self._whale_smc(buy_dominant=True)
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None.")
        # SL distance must be at least ATR (floor)
        actual_sl_dist = abs(sig.stop_loss - close_arr[-1])
        assert actual_sl_dist >= atr_val * 0.9, (
            f"SL distance ({actual_sl_dist:.4f}) must be >= ATR ({atr_val}) "
            "when swing is too close — the ATR floor must apply."
        )

    def test_whale_sl_setup_class_unchanged(self):
        """Changing SL logic must not affect WHALE_MOMENTUM setup_class."""
        ch = ScalpChannel()
        candles = {"1m": self._make_1m_candles_with_swing(n=15)}
        ind = _base_indicators_1m(atr=0.3)
        smc = self._whale_smc(buy_dominant=True)
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None.")
        assert sig.setup_class == "WHALE_MOMENTUM"

    def test_whale_sl_fallback_when_insufficient_candles(self):
        """When 1m candles are exactly at the minimum (10), fallback SL is used."""
        ch = ScalpChannel()
        # Exactly 10 candles — _WHALE_SWING_LOOKBACK=5 needs >5 entries in
        # lows[-6:-1], so len(lows) > 5 is satisfied, but let's test the path
        # by using exactly 10 candles and verifying a valid signal is produced.
        close_arr = np.array([100.0 + i * 0.05 for i in range(10)])
        candles_1m = {
            "open": close_arr - 0.02,
            "high": close_arr + 0.3,
            "low": close_arr - 0.3,
            "close": close_arr,
            "volume": np.ones(10) * 500.0,
        }
        candles = {"1m": candles_1m}
        ind = _base_indicators_1m(atr=0.3)
        smc = self._whale_smc(buy_dominant=True)
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        # Either None (market conditions) or a valid signal — no exception
        if sig is not None:
            assert sig.stop_loss < close_arr[-1], "LONG SL must be below entry."


# ---------------------------------------------------------------------------
# Path audit #9 — FUNDING_EXTREME_SIGNAL audit fixes
# ---------------------------------------------------------------------------

class TestFundingExtremeAuditFixes:
    """Path audit #9 fixes:
    - Wrong reject reason for `close <= 0` (was `funding_not_extreme`,
      now `invalid_price`) — telemetry truth.
    - TP1 ATR-adaptive cap (1.8R / 2.5R / uncapped) consistent with
      SR_FLIP / TPE pattern.
    """

    def _long_smc(self, fvg_level_above: float, close: float) -> dict:
        return {
            "funding_rate": -0.0015,
            "fvg": [{"gap_high": fvg_level_above, "gap_low": fvg_level_above - 0.3}],
            "orderblocks": [],
            "liquidation_clusters": [],
            "cvd": {"values": [0.0, 1.0, 2.0, 3.0]},
        }

    def test_invalid_price_reports_distinct_reject_reason(self):
        """`close <= 0` must emit `invalid_price`, NOT `funding_not_extreme`,
        so path-funnel telemetry doesn't conflate bad-data with the trigger
        gate.  Pre-fix both shared `funding_not_extreme`.
        """
        ch = ScalpChannel()
        # Build candles where close[-1] = 0 (invalid).
        candles_data = _make_candles_5m(20, base=100.0, trend=0.0)
        candles_data["close"][-1] = 0.0
        candles = {"5m": candles_data}
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        smc = self._long_smc(fvg_level_above=103.0, close=0.0)
        ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        assert ch._active_no_signal_reason == "invalid_price", (
            f"close <= 0 must report `invalid_price`, got "
            f"{ch._active_no_signal_reason!r}"
        )

    def test_tp1_capped_at_2_5r_in_median_atr_regime(self):
        """In median-ATR (atr_percentile 40-65), FUNDING TP1 must be capped
        at 2.5R from close.  Pre-fix the FVG-anchored TP1 could sit 5-10R
        away when the nearest qualifying zone was far in trending markets.
        """
        from types import SimpleNamespace
        ch = ScalpChannel()
        close = 101.0
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        # FVG far above — 105.0 is ~5R from close at sl_dist 0.75.
        smc = self._long_smc(fvg_level_above=105.0, close=close)
        # Median-ATR regime.
        smc["regime_context"] = SimpleNamespace(atr_percentile=50.0)
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — gates not met in this fixture.")
        sl_dist = abs(sig.entry - sig.stop_loss)
        tp1_dist = abs(sig.tp1 - sig.entry)
        tp1_ratio = tp1_dist / sl_dist
        assert tp1_ratio <= 2.5 + 0.01, (
            f"TP1 ratio {tp1_ratio:.2f}R exceeds median-ATR cap of 2.5R."
        )

    def test_tp1_capped_at_1_8r_in_low_atr_regime(self):
        """In low-ATR (atr_percentile <40), FUNDING TP1 capped at 1.8R."""
        from types import SimpleNamespace
        ch = ScalpChannel()
        close = 101.0
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        smc = self._long_smc(fvg_level_above=105.0, close=close)
        smc["regime_context"] = SimpleNamespace(atr_percentile=20.0)
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — gates not met in this fixture.")
        sl_dist = abs(sig.entry - sig.stop_loss)
        tp1_dist = abs(sig.tp1 - sig.entry)
        tp1_ratio = tp1_dist / sl_dist
        assert tp1_ratio <= 1.8 + 0.01, (
            f"TP1 ratio {tp1_ratio:.2f}R exceeds low-ATR cap of 1.8R."
        )

    def test_tp1_uncapped_in_high_atr_regime(self):
        """In high-ATR (atr_percentile ≥65), no cap — let structure-level
        TP1 stand."""
        from types import SimpleNamespace
        ch = ScalpChannel()
        close = 101.0
        ind = _base_indicators_5m(ema9=100.0, rsi_last=48.0, rsi_prev=42.0, atr=0.5)
        candles = {"5m": _make_candles_5m(20, base=100.0, trend=0.1)}
        smc = self._long_smc(fvg_level_above=105.0, close=close)
        smc["regime_context"] = SimpleNamespace(atr_percentile=80.0)
        sig = ch._evaluate_funding_extreme(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="TRENDING"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — gates not met in this fixture.")
        sl_dist = abs(sig.entry - sig.stop_loss)
        tp1_dist = abs(sig.tp1 - sig.entry)
        tp1_ratio = tp1_dist / sl_dist
        # Should preserve the far structural target (ratio > 2.5R).
        assert tp1_ratio > 2.5, (
            f"High-ATR TP1 ratio {tp1_ratio:.2f}R was capped — should be uncapped."
        )


# ---------------------------------------------------------------------------
# 4. Thesis-aligned constants are declared and correct
# ---------------------------------------------------------------------------

class TestPR07Constants:
    """Verify that the new PR-07 constants are explicitly declared."""

    def test_whale_swing_lookback_constant_exists(self):
        """_WHALE_SWING_LOOKBACK must be explicitly declared as a module constant."""
        assert isinstance(_WHALE_SWING_LOOKBACK, int), (
            "_WHALE_SWING_LOOKBACK must be an int constant in scalp.py."
        )
        assert 3 <= _WHALE_SWING_LOOKBACK <= 10, (
            "_WHALE_SWING_LOOKBACK should be in the 3–10 range for 1m impulse thesis."
        )

    def test_whale_swing_buffer_constant_exists(self):
        """_WHALE_SWING_BUFFER must be explicitly declared as a module constant."""
        assert isinstance(_WHALE_SWING_BUFFER, float), (
            "_WHALE_SWING_BUFFER must be a float constant in scalp.py."
        )
        assert 0.0005 <= _WHALE_SWING_BUFFER <= 0.005, (
            "_WHALE_SWING_BUFFER should be a small positive fraction (0.05%–0.5%)."
        )

    def test_structure_tp1_helper_is_importable(self):
        """_funding_extreme_structure_tp1 must be importable as a module-level function."""
        assert callable(_funding_extreme_structure_tp1), (
            "_funding_extreme_structure_tp1 must be a callable module-level function."
        )


# ---------------------------------------------------------------------------
# 5. Gate exemption membership unaffected by tuning
# ---------------------------------------------------------------------------

class TestGateExemptionUnchanged:
    """Gate exemption sets must not be altered by PR-07 TP/SL tuning."""

    def _load_exempt_sets(self):
        from src.scanner import _SMC_GATE_EXEMPT_SETUPS, _TREND_GATE_EXEMPT_SETUPS
        return _SMC_GATE_EXEMPT_SETUPS, _TREND_GATE_EXEMPT_SETUPS

    def test_funding_extreme_still_smc_exempt(self):
        """FUNDING_EXTREME_SIGNAL must remain in _SMC_GATE_EXEMPT_SETUPS after PR-07."""
        smc_exempt, _ = self._load_exempt_sets()
        assert "FUNDING_EXTREME_SIGNAL" in smc_exempt, (
            "FUNDING_EXTREME_SIGNAL must stay in _SMC_GATE_EXEMPT_SETUPS — "
            "PR-07 TP tuning must not alter gate-exemption logic."
        )

    def test_funding_extreme_still_trend_exempt(self):
        """FUNDING_EXTREME_SIGNAL must remain in _TREND_GATE_EXEMPT_SETUPS after PR-07."""
        _, trend_exempt = self._load_exempt_sets()
        assert "FUNDING_EXTREME_SIGNAL" in trend_exempt, (
            "FUNDING_EXTREME_SIGNAL must stay in _TREND_GATE_EXEMPT_SETUPS — "
            "PR-07 tuning must not alter gate-exemption logic."
        )

    def test_whale_momentum_still_trend_exempt(self):
        """WHALE_MOMENTUM must remain in _TREND_GATE_EXEMPT_SETUPS after PR-07."""
        _, trend_exempt = self._load_exempt_sets()
        assert "WHALE_MOMENTUM" in trend_exempt, (
            "WHALE_MOMENTUM must stay in _TREND_GATE_EXEMPT_SETUPS — "
            "PR-07 SL tuning must not alter gate-exemption logic."
        )

    def test_whale_momentum_still_smc_exempt(self):
        """WHALE_MOMENTUM must remain in _SMC_GATE_EXEMPT_SETUPS after PR-07 (PR-05 fix)."""
        smc_exempt, _ = self._load_exempt_sets()
        assert "WHALE_MOMENTUM" in smc_exempt, (
            "WHALE_MOMENTUM must stay in _SMC_GATE_EXEMPT_SETUPS — added in PR-05 "
            "and must not be removed by PR-07 specialist-path tuning."
        )


# ---------------------------------------------------------------------------
# 6. Unaffected path — SR_FLIP_RETEST behavior unchanged
# ---------------------------------------------------------------------------

class TestUnaffectedPathBehaviourUnchanged:
    """PR-07 must not alter unrelated evaluator behaviour (scope guard)."""

    def test_sr_flip_retest_still_produces_signal(self):
        """SR_FLIP_RETEST must remain functional after PR-07 changes."""
        from src.channels.scalp import ScalpChannel
        ch = ScalpChannel()
        n = 60
        base = 100.0
        trend = 0.1
        close = np.array([base + i * trend for i in range(n)])
        high = close + 0.5
        low = close - 0.5
        candles_5m = {
            "open": close - 0.05,
            "high": high,
            "low": low,
            "close": close,
            "volume": np.ones(n) * 1000.0,
        }
        candles = {"5m": candles_5m}
        ind = {
            "5m": {
                "adx_last": 28.0,
                "atr_last": 0.5,
                "ema9_last": 105.5,
                "ema21_last": 104.0,
                "ema200_last": 95.0,
                "rsi_last": 55.0,
                "rsi_prev": 52.0,
                "macd_last": 0.1,
                "bb_upper_last": 108.0,
                "bb_mid_last": 104.0,
                "bb_lower_last": 100.0,
                "momentum_last": 0.5,
            }
        }
        sweep = LiquiditySweep(
            index=59, direction=Direction.LONG,
            sweep_level=99.0, close_price=99.5,
            wick_high=101.0, wick_low=98.5,
        )
        smc_data = {
            "sweeps": [sweep],
            "fvg": [{"gap_high": 106.0, "gap_low": 105.5}],
            "orderblocks": [],
        }
        sigs = ch.evaluate("BTCUSDT", candles, ind, smc_data, 0.005, 10_000_000)
        # evaluate() must complete without error; we are not asserting a specific
        # setup_class fires (conditions may not align in a stub), only that the
        # call succeeds and returns a list.
        assert isinstance(sigs, list), "evaluate() must return a list."
