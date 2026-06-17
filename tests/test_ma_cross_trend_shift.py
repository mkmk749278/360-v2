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


# ---------------------------------------------------------------------------
# Live-API contract (2026-05-11 fix): scalar ``*_prev`` / ``*_last`` pairs
# from ``compute_indicators_for_candle_dict``.  Bug: until this fix the
# 15th evaluator never fired because the live indicator API only stored
# ``*_last`` scalars and the evaluator read full arrays.
# ---------------------------------------------------------------------------


class TestScalarPrevApiPath:
    """Confirms the evaluator fires when fed the live indicator API
    (scalar pairs, no arrays).  Mirrors what production looks like."""

    def test_compute_indicators_populates_ema_prev_scalars(self):
        """Live compute_indicators_for_candle_dict produces ``*_prev`` for
        ema21 / ema50 / ema200 when enough candles exist."""
        from src.scanner.indicator_compute import compute_indicators_for_candle_dict
        import numpy as np

        # Need >= 200 closes so all three EMAs get computed.
        n = 250
        closes = list(np.linspace(1.0, 2.0, n))
        result = compute_indicators_for_candle_dict({
            "1h": {
                "high": [c * 1.01 for c in closes],
                "low": [c * 0.99 for c in closes],
                "close": closes,
                "volume": [100.0] * n,
            }
        })
        ind = result["1h"]
        for key in (
            "ema21_prev", "ema21_last",
            "ema50_prev", "ema50_last",
            "ema200_prev", "ema200_last",
        ):
            assert key in ind, f"{key} missing from live indicator dict"
            assert isinstance(ind[key], float), f"{key} not a float"

    def test_4h_golden_cross_fires_via_scalar_api(self):
        """Same trigger contract as the array-fed tests, but feeds the
        evaluator the live scalar API ``ema*_prev`` / ``ema*_last``."""
        from src.channels.scalp import ScalpChannel
        from src.smc import Direction

        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        indicators = {
            "1m": {"rsi_last": 60.0, "ema9_last": 100.5,
                   "ema21_last": 100.0, "atr_last": 0.5},
            "1h": {"rsi_last": 60.0, "atr_last": 0.5,
                   "ema21_last": 100.3, "ema50_last": 100.5},
            "4h": {
                # ema50 was below ema200 last bar, now above → golden cross
                "ema50_prev": 99.0, "ema50_last": 100.5,
                "ema200_prev": 99.5, "ema200_last": 100.0,
            },
        }
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, indicators, {}, 0.01, 10_000_000,
            regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
        assert sig.setup_class == "MA_CROSS_TREND_SHIFT"

    def test_no_cross_when_prev_missing(self):
        """Without ``*_prev`` AND without arrays, evaluator can't see the
        transition — returns no_ma_cross.  Protects against silent
        false-positives on incomplete data."""
        from src.channels.scalp import ScalpChannel

        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        # ``*_last`` only, no ``*_prev``, no arrays.  Evaluator should
        # fail closed (no detection).
        indicators = {
            "1m": {"rsi_last": 60.0, "ema9_last": 100.5,
                   "ema21_last": 100.0, "atr_last": 0.5},
            "1h": {"rsi_last": 60.0, "atr_last": 0.5,
                   "ema21_last": 100.3, "ema50_last": 100.5},
            "4h": {"ema50_last": 100.5, "ema200_last": 100.0},
        }
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, indicators, {}, 0.01, 10_000_000,
            regime="TRENDING_UP",
        )
        assert sig is None


# ---------------------------------------------------------------------------
# Higher-timeframe trend-alignment gate
#
# Research consensus on crypto MA crosses: the FILTER, not the period choice,
# is the edge — a raw cross whipsaws because crypto ranges ~60% of the time.
# The lower-conviction 1h 21/50 cross must agree with the 4h structural trend;
# the 4h 50/200 cross is confirmed by price vs the 4h EMA200.
# ---------------------------------------------------------------------------


def _make_1h_golden_cross_with_4h(ema50_4h: float, ema200_4h: float) -> dict:
    """1h golden cross (21>50), with caller-controlled 4h EMA50/200 stack."""
    return {
        "1m": {"rsi_last": 60.0, "ema9_last": 100.5, "ema21_last": 100.0, "atr_last": 0.5},
        "1h": {
            "rsi_last": 60.0, "atr_last": 0.5,
            "ema21": [99.0, 100.5], "ema50": [99.5, 100.0],
            "ema21_last": 100.5, "ema50_last": 100.0,
        },
        "4h": {"ema50_last": ema50_4h, "ema200_last": ema200_4h},
    }


class TestHtfAlignmentGate:
    def test_1h_long_fires_when_4h_bullish(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        # 4h bullish: ema50 > ema200 → confirms the 1h golden cross LONG.
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_1h_golden_cross_with_4h(101.0, 99.0),
            _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
        assert "1h" in (sig.execution_note or "")

    def test_1h_long_rejected_when_4h_bearish(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        # 4h bearish: ema50 < ema200 → 1h golden cross is counter-HTF → reject.
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, _make_1h_golden_cross_with_4h(99.0, 101.0),
            _smc(), 0.01, 10_000_000, regime="RANGING",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "ma_cross_htf_misaligned"

    def test_1h_cross_rejected_when_4h_trend_unavailable(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(), "1h": _candles_1h()}
        ind = _make_1h_golden_cross_with_4h(101.0, 99.0)
        ind["4h"] = {}  # no 4h EMAs → cannot confirm → fail closed
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "ma_cross_htf_unconfirmed"

    def test_4h_long_rejected_when_price_below_ema200(self):
        ch = ScalpChannel()
        # Price (1m close=100) below the 4h EMA200 → failing golden cross.
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h()}
        ind = _make_indicators_with_4h_golden_cross()
        # EMA200 between price (100) and EMA50 (100.5): cross stays valid
        # (ema50 > ema200) but price sits below EMA200 → failing cross.
        ind["4h"]["ema200"] = [99.5, 100.3]
        ind["4h"]["ema200_last"] = 100.3
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None
        assert ch._active_no_signal_reason == "ma_cross_4h_price_below_ema200"

    def test_4h_long_fires_when_price_above_ema200(self):
        ch = ScalpChannel()
        candles = {"1m": _candles_1m(base=100.0), "1h": _candles_1h()}
        ind = _make_indicators_with_4h_golden_cross()
        ind["4h"]["ema200_last"] = 98.0  # price 100 > 98 → confirmed
        sig = ch._evaluate_ma_cross_trend_shift(
            "BTCUSDT", candles, ind, _smc(), 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
