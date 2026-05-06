"""Tests for the MA_CROSS_TREND_SHIFT evaluator (PR-8 — 15th evaluator).

Contract:
* Triggers on EMA50/EMA200 cross on 4h, OR EMA21/EMA50 cross on 1h
  (4h preferred — checked first)
* Direction = LONG on golden cross, SHORT on death cross
* SL anchored to opposite-side 1h swing in last 30 bars (or ATR×1.0
  fallback)
* TP ladder = 1.5R / 2.5R / 3.5R (fixed)
* Cooldown = 24h per (symbol, direction); persisted to disk for
  redeploy survival
* 4h cross gets +10 confidence; 1h cross gets +5
* Setup class: "MA_CROSS_TREND_SHIFT"

Each test stages indicator arrays so the cross condition is explicit
and replays exactly what production code sees.

Note: each test isolates the cooldown JSON to a per-test tmp path so
fires from one test don't leak into another.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

from src.channels.scalp import ScalpChannel
from src.smc import Direction


@pytest.fixture(autouse=True)
def _isolated_ma_cross_cooldown(tmp_path, monkeypatch):
    """Per-test cooldown JSON path so fires don't leak across tests."""
    monkeypatch.setattr(
        ScalpChannel,
        "_MA_CROSS_COOLDOWN_PATH",
        str(tmp_path / "ma_cross_cooldown.json"),
    )
    yield


# ---------------------------------------------------------------------------
# Fixture builders
# ---------------------------------------------------------------------------


def _candles_1m(n: int = 10, base: float = 100.0) -> dict:
    """Trivial 1m candle series — only the last close is read."""
    closes = np.array([base] * n, dtype=np.float64)
    return {
        "open": closes,
        "high": closes + 0.1,
        "low": closes - 0.1,
        "close": closes,
        "volume": np.full(n, 500.0),
    }


def _candles_1h(n: int = 50, sl_anchor_low: float = 95.0, sl_anchor_high: float = 105.0) -> dict:
    """1h candles — provides swing low/high for structural SL anchor."""
    highs = np.array([sl_anchor_high - 1.0] * n, dtype=np.float64)
    lows = np.array([sl_anchor_low + 1.0] * n, dtype=np.float64)
    # Force one bar to actually hit the anchors.
    highs[5] = sl_anchor_high
    lows[5] = sl_anchor_low
    return {
        "open": (highs + lows) / 2,
        "high": highs,
        "low": lows,
        "close": (highs + lows) / 2,
        "volume": np.full(n, 500.0),
    }


def _make_indicators_with_4h_golden_cross() -> dict:
    """Stage indicator arrays so 4h EMA50 just crossed above EMA200."""
    return {
        "1m": {"rsi_last": 60.0, "ema9_last": 100.5, "ema21_last": 100.0, "atr_last": 0.5},
        "1h": {
            "rsi_last": 60.0, "atr_last": 0.5,
            "ema21": [99.5, 99.7], "ema50": [99.0, 99.5],
            "ema21_last": 99.7, "ema50_last": 99.5,
        },
        "4h": {
            # ema50 was below ema200 last bar, now above → golden cross
            "ema50": [99.0, 100.5],
            "ema200": [99.5, 100.0],
            "ema50_last": 100.5,
            "ema200_last": 100.0,
        },
    }


def _make_indicators_with_4h_death_cross() -> dict:
    return {
        "1m": {"rsi_last": 40.0, "ema9_last": 99.5, "ema21_last": 100.0, "atr_last": 0.5},
        "1h": {
            "rsi_last": 40.0, "atr_last": 0.5,
            "ema21_last": 100.3, "ema50_last": 100.5,
        },
        "4h": {
            "ema50": [100.5, 99.5],
            "ema200": [100.0, 100.0],
            "ema50_last": 99.5,
            "ema200_last": 100.0,
        },
    }


def _make_indicators_with_1h_golden_cross() -> dict:
    """4h has no cross; 1h EMA21 crosses EMA50."""
    return {
        "1m": {"rsi_last": 60.0, "ema9_last": 100.5, "ema21_last": 100.0, "atr_last": 0.5},
        "1h": {
            "rsi_last": 60.0, "atr_last": 0.5,
            # ema21 just crossed above ema50
            "ema21": [99.0, 100.5],
            "ema50": [99.5, 100.0],
            "ema21_last": 100.5,
            "ema50_last": 100.0,
        },
        "4h": {
            # No cross — ema50 stable above ema200 throughout
            "ema50": [101.0, 101.0],
            "ema200": [99.0, 99.0],
            "ema50_last": 101.0,
            "ema200_last": 99.0,
        },
    }


def _make_indicators_no_cross() -> dict:
    """Stack aligned, but no recent cross on either TF."""
    return {
        "1m": {"rsi_last": 60.0, "ema9_last": 100.5, "ema21_last": 100.0, "atr_last": 0.5},
        "1h": {
            "rsi_last": 60.0, "atr_last": 0.5,
            "ema21": [101.0, 101.5], "ema50": [99.0, 99.5],
            "ema21_last": 101.5, "ema50_last": 99.5,
        },
        "4h": {
            "ema50": [101.0, 101.5], "ema200": [99.0, 99.5],
            "ema50_last": 101.5, "ema200_last": 99.5,
        },
    }


def _smc() -> dict:
    return {}


# ---------------------------------------------------------------------------
# Trigger detection
# ---------------------------------------------------------------------------


class TestTriggerDetection:
    def test_4h_golden_cross_fires_long(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
        assert sig.setup_class == "MA_CROSS_TREND_SHIFT"

    def test_4h_death_cross_fires_short(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h(sl_anchor_high=105.0)}
        sig = ch._evaluate_ma_cross_trend_shift(
            "ETHUSDT", candles, _make_indicators_with_4h_death_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_DOWN",
        )
        assert sig is not None
        assert sig.direction == Direction.SHORT
        assert sig.setup_class == "MA_CROSS_TREND_SHIFT"

    def test_1h_cross_fires_when_no_4h_cross(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_1h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
        # 1h cross gets the smaller +5 lift; 4h gets +10
        # We just assert the note differentiates them.
        assert "1h" in (sig.execution_note or "")

    def test_no_cross_returns_none(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_no_cross(),
            _smc(), 0.01, 10_000_000, regime="RANGING",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "no_ma_cross"

    def test_4h_takes_precedence_over_1h(self):
        """When both 4h and 1h cross simultaneously, 4h wins (higher conviction)."""
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        ind = _make_indicators_with_4h_golden_cross()
        # Also stage a 1h cross of opposite direction to make sure 4h wins.
        ind["1h"]["ema21"] = [101.0, 99.5]   # crossing DOWN
        ind["1h"]["ema50"] = [100.0, 100.0]
        ind["1h"]["ema21_last"] = 99.5
        ind["1h"]["ema50_last"] = 100.0
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG  # 4h golden, not 1h death
        assert "4h" in (sig.execution_note or "")


# ---------------------------------------------------------------------------
# SL / TP geometry
# ---------------------------------------------------------------------------


class TestSlTpGeometry:
    def test_long_sl_below_entry_short_sl_above(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0)}
        sig_long = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig_long is not None
        assert sig_long.stop_loss < sig_long.entry

        ch2 = ScalpChannel()
        candles2 = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_high=105.0)}
        sig_short = ch2._evaluate_ma_cross_trend_shift(
            "ETHUSDT", candles2, _make_indicators_with_4h_death_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_DOWN",
        )
        assert sig_short is not None
        assert sig_short.stop_loss > sig_short.entry

    def test_tp_ladder_at_fixed_r_multiples(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0)}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        sl_dist = sig.entry - sig.stop_loss
        assert sl_dist > 0
        # 1.5R / 2.5R / 3.5R, allowing rounding tolerance.
        assert abs((sig.tp1 - sig.entry) - 1.5 * sl_dist) < 0.01
        assert abs((sig.tp2 - sig.entry) - 2.5 * sl_dist) < 0.01
        assert abs((sig.tp3 - sig.entry) - 3.5 * sl_dist) < 0.01

    def test_atr_fallback_when_no_1h_swings(self):
        """No 1h candles → ATR×1.0 SL distance."""
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0)}  # no 1h
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None  # should still fire
        sl_dist = sig.entry - sig.stop_loss
        assert sl_dist > 0


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------


class TestCooldown:
    def test_second_signal_within_24h_blocked(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0)}
        ind = _make_indicators_with_4h_golden_cross()

        first = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert first is not None

        # Second call same symbol/direction within 24h → cooldown.
        second = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert second is None
        assert ch._active_no_signal_reason == "ma_cross_cooldown"

    def test_different_symbol_not_blocked(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0)}
        ind = _make_indicators_with_4h_golden_cross()

        first = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert first is not None

        second = ch._evaluate_ma_cross_trend_shift(
            "ETHUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert second is not None  # different symbol → independent cooldown

    def test_different_direction_not_blocked(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0, sl_anchor_high=105.0)}

        # First a LONG.
        first = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert first is not None

        # Then a SHORT — different (symbol, direction) key.
        second = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_death_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_DOWN",
        )
        assert second is not None  # opposite direction → independent cooldown

    def test_post_cooldown_fires_again(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0)}
        ind = _make_indicators_with_4h_golden_cross()

        first = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert first is not None
        # Forge cooldown expiry.
        ch._ma_cross_last_fire_ts[("BTCUSDT", Direction.LONG.value)] = time.time() - 25 * 3600.0
        second = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert second is not None


# ---------------------------------------------------------------------------
# Defensive checks
# ---------------------------------------------------------------------------


class TestDefensive:
    def test_missing_indicators_returns_none(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, {}, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None

    def test_insufficient_1m_candles(self):
        ch = ScalpChannel()
        candles = {"1m": {"close": [100.0]}, "1h": _candles_1h()}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None

    def test_basic_filter_failure(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        # Spread too wide.
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 99.0, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "basic_filters_failed"

    def test_negative_close_rejected(self):
        ch = ScalpChannel()
        # Force a negative close in 1m fixture.
        bad_1m = _candles_1m(base=100.0)
        bad_1m["close"] = np.array([100.0, 100.0, 100.0, 100.0, -1.0], dtype=np.float64)
        candles = {"1m": bad_1m, "1h": _candles_1h()}
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "invalid_price"


# ---------------------------------------------------------------------------
# Conviction lift
# ---------------------------------------------------------------------------


class TestConvictionLift:
    def test_4h_cross_higher_conviction_than_1h(self):
        """Same setup, 4h cross should yield higher confidence than 1h cross."""
        ch_4h = ScalpChannel()
        ch_1h = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h(sl_anchor_low=95.0)}

        sig_4h = ch_4h._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_indicators_with_4h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        sig_1h = ch_1h._evaluate_ma_cross_trend_shift(
            "ETHUSDT", candles, _make_indicators_with_1h_golden_cross(),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig_4h is not None and sig_1h is not None
        assert sig_4h.confidence > sig_1h.confidence


# ---------------------------------------------------------------------------
# SetupClass enum integrity
# ---------------------------------------------------------------------------


def test_setup_class_enum_value():
    from src.signal_quality import SetupClass
    assert SetupClass.MA_CROSS_TREND_SHIFT.value == "MA_CROSS_TREND_SHIFT"


def test_max_sl_pct_entry_present():
    from src.signal_quality import _MAX_SL_PCT_BY_SETUP
    assert "MA_CROSS_TREND_SHIFT" in _MAX_SL_PCT_BY_SETUP
    assert 1.0 <= _MAX_SL_PCT_BY_SETUP["MA_CROSS_TREND_SHIFT"] <= 5.0


def test_portfolio_role_assigned():
    from src.signal_quality import ACTIVE_PATH_PORTFOLIO_ROLES, SetupClass, PortfolioRole
    assert ACTIVE_PATH_PORTFOLIO_ROLES.get(SetupClass.MA_CROSS_TREND_SHIFT) == PortfolioRole.SPECIALIST
