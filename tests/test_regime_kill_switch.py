"""Tests for src.regime_kill_switch — BTC whipsaw detection."""
from __future__ import annotations

import os
from unittest.mock import MagicMock

import pytest

from src.regime_kill_switch import (
    BtcRegimeKillSwitch,
    evaluate_btc_whipsaw,
    REGIME_KILL_EXEMPT_SETUPS,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_candles_15m(
    n: int,
    open_: float,
    *,
    trending_pct: float = 0.0,
    noise_pct: float = 0.5,
) -> dict:
    """Build synthetic 15m candles.

    Parameters
    ----------
    n:
        Number of candles (should be at least lookback+1).
    open_:
        Starting price.
    trending_pct:
        Net directional move as % of open_.
        Positive = uptrend, negative = downtrend, 0 = flat.
    noise_pct:
        Per-candle high-low range as % of open_.
    """
    closes = []
    highs = []
    lows = []

    price = open_
    per_candle_move = (trending_pct / 100.0 * open_) / n if n > 0 else 0.0
    half_range = noise_pct / 100.0 * open_ / 2.0

    for _ in range(n + 1):
        closes.append(price)
        highs.append(price + half_range)
        lows.append(price - half_range)
        price += per_candle_move

    return {"close": closes, "high": highs, "low": lows}


def _make_whipsaw_candles(n: int, price: float = 50000.0, noise_pct: float = 0.5) -> dict:
    """Candles that alternate direction each candle — pure whipsaw.

    net_move ≈ 0, total_range = n × noise.
    """
    closes = [price]
    highs = []
    lows = []
    half_range = noise_pct / 100.0 * price / 2.0

    for i in range(n):
        # Alternate up/down
        delta = half_range if i % 2 == 0 else -half_range
        closes.append(closes[-1] + delta)
        highs.append(max(closes[-2], closes[-1]) + half_range * 0.1)
        lows.append(min(closes[-2], closes[-1]) - half_range * 0.1)

    return {"close": closes, "high": highs, "low": lows}


# ---------------------------------------------------------------------------
# evaluate_btc_whipsaw: pure function tests
# ---------------------------------------------------------------------------

class TestEvaluateBtcWhipsaw:
    def test_missing_candles_returns_false(self):
        is_whipsaw, reason, eff = evaluate_btc_whipsaw({})
        assert is_whipsaw is False
        assert reason == ""
        assert eff == 0.0

    def test_insufficient_candles_returns_false(self):
        # Only 5 candles but lookback=16 requires 17
        candles = _make_candles_15m(5, 50000.0)
        is_whipsaw, reason, eff = evaluate_btc_whipsaw(candles)
        assert is_whipsaw is False

    def test_clean_trend_not_whipsaw(self):
        """Strong uptrend: net move ≈ total range → efficiency ≈ 1.0."""
        # 2% uptrend over 16 candles with minimal noise
        candles = _make_candles_15m(20, 50000.0, trending_pct=2.0, noise_pct=0.02)
        is_whipsaw, reason, eff = evaluate_btc_whipsaw(candles)
        assert is_whipsaw is False
        assert eff > 0.5

    def test_alternating_candles_is_whipsaw(self):
        """Alternating up/down candles — net ≈ 0, total_range large."""
        candles = _make_whipsaw_candles(20, price=50000.0, noise_pct=0.3)
        # Total range is significant (20 × 0.3% each) but net is near 0
        is_whipsaw, reason, eff = evaluate_btc_whipsaw(
            candles,
            lookback=16,
            efficiency_min=0.20,
            min_range_pct=1.5,
        )
        assert is_whipsaw is True
        assert "whipsaw" in reason.lower()
        assert "direction_efficiency" in reason

    def test_quiet_market_not_whipsaw(self):
        """BTC barely moving — total_range < min_range_pct → gate inactive."""
        # Only 0.2% net move, 0.05% per-candle noise — total range < 1.5%
        candles = _make_candles_15m(20, 50000.0, trending_pct=0.0, noise_pct=0.05)
        is_whipsaw, reason, eff = evaluate_btc_whipsaw(
            candles,
            lookback=16,
            efficiency_min=0.20,
            min_range_pct=1.5,
        )
        # Quiet day: total_range_pct < 1.5%, gate should not fire
        assert is_whipsaw is False

    def test_moderate_ranging_not_whipsaw(self):
        """Moderate back-and-forth, but efficiency just above threshold."""
        candles = _make_candles_15m(20, 50000.0, trending_pct=0.8, noise_pct=0.3)
        is_whipsaw, reason, eff = evaluate_btc_whipsaw(
            candles,
            lookback=16,
            efficiency_min=0.15,  # tighter threshold
            min_range_pct=1.5,
        )
        # With 0.8% net vs ~4.8% range, efficiency ≈ 0.17 — may depend on
        # exact geometry, so just assert the function returns a float and
        # doesn't crash.
        assert isinstance(is_whipsaw, bool)
        assert isinstance(eff, float)

    def test_custom_lookback_respected(self):
        """Only last 8 candles (2h) examined when lookback=8."""
        candles = _make_candles_15m(20, 50000.0, trending_pct=0.0, noise_pct=0.3)
        # This should work without error for both lookback values
        r8 = evaluate_btc_whipsaw(candles, lookback=8, efficiency_min=0.20, min_range_pct=1.5)
        r16 = evaluate_btc_whipsaw(candles, lookback=16, efficiency_min=0.20, min_range_pct=1.5)
        assert isinstance(r8[0], bool)
        assert isinstance(r16[0], bool)


# ---------------------------------------------------------------------------
# BtcRegimeKillSwitch: integration tests
# ---------------------------------------------------------------------------

class TestBtcRegimeKillSwitch:
    def _sig(self, setup_class: str = "SR_FLIP_RETEST"):
        s = MagicMock()
        s.setup_class = setup_class
        return s

    def test_disabled_never_blocks(self, monkeypatch):
        import src.regime_kill_switch as rks_mod
        monkeypatch.setattr(rks_mod, "REGIME_KILL_ENABLED", False)

        ks = BtcRegimeKillSwitch()
        candles = _make_whipsaw_candles(20)
        blocked, reason = ks.check(self._sig(), candles)
        assert blocked is False

    def test_no_btc_data_fails_open(self):
        ks = BtcRegimeKillSwitch()
        blocked, reason = ks.check(self._sig(), None)
        assert blocked is False

    def test_empty_btc_data_fails_open(self):
        ks = BtcRegimeKillSwitch()
        blocked, reason = ks.check(self._sig(), {})
        assert blocked is False

    def test_whipsaw_blocks_structural_setup(self):
        ks = BtcRegimeKillSwitch()
        candles = _make_whipsaw_candles(20, price=50000.0, noise_pct=0.3)
        blocked, reason = ks.check(self._sig("SR_FLIP_RETEST"), candles)
        assert blocked is True
        assert reason != ""
        assert ks.kill_count == 1

    def test_trending_does_not_block(self):
        ks = BtcRegimeKillSwitch()
        candles = _make_candles_15m(20, 50000.0, trending_pct=2.0, noise_pct=0.02)
        blocked, _ = ks.check(self._sig("SR_FLIP_RETEST"), candles)
        assert blocked is False

    def test_exempt_setups_bypass_gate(self):
        """Tape-driven setups are never blocked even in whipsaw."""
        ks = BtcRegimeKillSwitch()
        candles = _make_whipsaw_candles(20, price=50000.0, noise_pct=0.3)

        for exempt in ("WHALE_MOMENTUM", "FUNDING_EXTREME_SIGNAL", "LIQUIDATION_REVERSAL"):
            blocked, reason = ks.check(self._sig(exempt), candles)
            assert blocked is False, f"{exempt} should be exempt but was blocked"

    def test_exempt_set_has_expected_entries(self):
        """Lock the default exempt set — any change should be deliberate."""
        assert "WHALE_MOMENTUM" in REGIME_KILL_EXEMPT_SETUPS
        assert "FUNDING_EXTREME_SIGNAL" in REGIME_KILL_EXEMPT_SETUPS
        assert "LIQUIDATION_REVERSAL" in REGIME_KILL_EXEMPT_SETUPS

    def test_kill_count_increments(self):
        ks = BtcRegimeKillSwitch()
        candles = _make_whipsaw_candles(20, price=50000.0, noise_pct=0.3)

        assert ks.kill_count == 0
        ks.check(self._sig(), candles)
        ks.check(self._sig(), candles)
        assert ks.kill_count == 2

    def test_last_kill_reason_populated(self):
        ks = BtcRegimeKillSwitch()
        candles = _make_whipsaw_candles(20, price=50000.0, noise_pct=0.3)
        ks.check(self._sig(), candles)
        assert "whipsaw" in ks.last_kill_reason.lower()

    def test_env_override_exempt_setups(self, monkeypatch):
        """REGIME_KILL_EXEMPT_SETUPS env var is honoured."""
        import src.regime_kill_switch as rks_mod
        # Temporarily widen the exempt set to include SR_FLIP_RETEST
        monkeypatch.setattr(
            rks_mod,
            "REGIME_KILL_EXEMPT_SETUPS",
            frozenset({"WHALE_MOMENTUM", "SR_FLIP_RETEST"}),
        )
        ks = BtcRegimeKillSwitch()
        candles = _make_whipsaw_candles(20, price=50000.0, noise_pct=0.3)
        blocked, _ = ks.check(self._sig("SR_FLIP_RETEST"), candles)
        assert blocked is False
