"""Tests for src/btc_direction.py — BTC direction soft-penalty gate.

OWNER_BRIEF §2.1 doctrine: top-75 USDT-M futures are heavily BTC-correlated;
signals fighting BTC's macro 1H+4H trend tend to get swept.  Soft penalty
(not a hard block, per scalping doctrine) when both 1H and 4H oppose
the signal direction.

Test surface:

* Bullish-BTC + LONG signal → no penalty (aligned).
* Bullish-BTC + SHORT signal → penalty fires.
* Bearish-BTC + LONG signal → penalty fires (production-data trigger).
* Bearish-BTC + SHORT signal → no penalty (aligned).
* Mixed 1H/4H → no penalty (require BOTH).
* Neutral BTC (flat alignment) → no penalty.
* Missing BTC data → fail-open (no penalty).
* Tape-driven exempt setups (WHALE / FUNDING / LIQ_REVERSAL) bypass entirely.
"""
from __future__ import annotations

from src.btc_direction import (
    _BTC_DIR_EXEMPT_SETUPS,
    _ema_fan_pct,
    check_btc_direction_gate,
    check_countertrend_mover_block,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ind_bullish(ema21=100.0, ema50=98.0, ema21_prev=99.7):
    """BTC indicator dict for a bullish trend (ema21>ema50, slope up)."""
    return {
        "ema21_last": ema21,
        "ema50_last": ema50,
        "ema21_prev": ema21_prev,
    }


def _ind_bearish(ema21=100.0, ema50=102.0, ema21_prev=100.3):
    """BTC indicator dict for a bearish trend (ema21<ema50, slope down)."""
    return {
        "ema21_last": ema21,
        "ema50_last": ema50,
        "ema21_prev": ema21_prev,
    }


def _ind_neutral():
    """BTC indicator dict for a flat alignment (ema21 == ema50)."""
    return {"ema21_last": 100.0, "ema50_last": 100.0, "ema21_prev": 100.0}


def _candles_close_above(price=101.0, n=5):
    return {"close": [price] * n}


def _candles_close_below(price=99.0, n=5):
    return {"close": [price] * n}


# ---------------------------------------------------------------------------
# Aligned cases — no penalty
# ---------------------------------------------------------------------------


class TestAlignedNoPenalty:
    def test_btc_bullish_long_aligned(self):
        allowed, reason = check_btc_direction_gate(
            "LONG", _ind_bullish(), _ind_bullish(),
            _candles_close_above(),
        )
        assert allowed is True
        assert reason == ""

    def test_btc_bearish_short_aligned(self):
        allowed, reason = check_btc_direction_gate(
            "SHORT", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
        )
        assert allowed is True
        assert reason == ""


# ---------------------------------------------------------------------------
# Counter-direction — penalty fires
# ---------------------------------------------------------------------------


class TestCounterDirectionPenalty:
    def test_btc_bearish_long_penalty(self):
        """Production-data trigger: bearish BTC, LONG alt signal."""
        allowed, reason = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
        )
        assert allowed is False
        assert "btc_1h_4h_both_bearish_long" in reason

    def test_btc_bullish_short_penalty(self):
        allowed, reason = check_btc_direction_gate(
            "SHORT", _ind_bullish(), _ind_bullish(),
            _candles_close_above(),
        )
        assert allowed is False
        assert "btc_1h_4h_both_bullish_short" in reason

    def test_direction_case_insensitive(self):
        """``long`` / ``LONG`` / ``Long`` all coerce to the same path."""
        for d in ("long", "LONG", "Long"):
            allowed, _ = check_btc_direction_gate(
                d, _ind_bearish(), _ind_bearish(),
                _candles_close_below(),
            )
            assert allowed is False


# ---------------------------------------------------------------------------
# Mixed timeframes — both required
# ---------------------------------------------------------------------------


class TestBothTimeframesRequired:
    def test_1h_bearish_4h_bullish_no_penalty(self):
        """1H opposes but 4H aligns → no penalty (avoid noisy 1H signals)."""
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bullish(),
            _candles_close_above(),
        )
        assert allowed is True

    def test_1h_bullish_4h_bearish_no_penalty(self):
        allowed, _ = check_btc_direction_gate(
            "SHORT", _ind_bullish(), _ind_bearish(),
            _candles_close_below(),
        )
        assert allowed is True

    def test_neutral_1h_no_penalty(self):
        """Flat 1H alignment → no clear macro trend, no penalty."""
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_neutral(), _ind_bearish(),
            _candles_close_below(),
        )
        assert allowed is True

    def test_neutral_4h_no_penalty(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_neutral(),
            None,
        )
        assert allowed is True


# ---------------------------------------------------------------------------
# Fail-open on missing data
# ---------------------------------------------------------------------------


class TestFailOpen:
    def test_no_btc_1h_no_penalty(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", None, _ind_bearish(),
            _candles_close_below(),
        )
        assert allowed is True

    def test_no_btc_4h_no_penalty(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), None,
            None,
        )
        assert allowed is True

    def test_empty_indicator_dict_no_penalty(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", {}, {},
            None,
        )
        assert allowed is True

    def test_missing_ema21_no_penalty(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", {"ema50_last": 100.0}, _ind_bearish(),
            None,
        )
        assert allowed is True

    def test_ema_non_numeric_no_penalty(self):
        """Defensive: non-numeric indicator values don't crash the gate."""
        allowed, _ = check_btc_direction_gate(
            "LONG", {"ema21_last": "x", "ema50_last": 100.0}, _ind_bearish(),
            None,
        )
        assert allowed is True


# ---------------------------------------------------------------------------
# Slope handling
# ---------------------------------------------------------------------------


class TestSlopeHandling:
    def test_alignment_only_when_ema21_prev_missing(self):
        """``ema21_prev`` absent (warmup) → accept alignment-only.
        This is the soft-penalty fail-open doctrine: never block on
        missing data."""
        ind_1h = {"ema21_last": 100.0, "ema50_last": 98.0}  # bullish, no prev
        allowed, _ = check_btc_direction_gate(
            "SHORT", ind_1h, ind_1h, _candles_close_above(),
        )
        assert allowed is False  # alignment-only still triggers penalty

    def test_against_slope_breaks_classification(self):
        """ema21>ema50 (bullish alignment) but ema21_prev>ema21 (falling
        slope) → not classified as BULLISH; no penalty."""
        contradicting = {
            "ema21_last": 100.0,
            "ema50_last": 98.0,
            "ema21_prev": 101.0,  # slope is falling despite bullish alignment
        }
        allowed, _ = check_btc_direction_gate(
            "SHORT", contradicting, contradicting,
            _candles_close_above(),
        )
        assert allowed is True


# ---------------------------------------------------------------------------
# Setup exemptions — tape-driven counter-tape paths
# ---------------------------------------------------------------------------


class TestSetupExemptions:
    def test_whale_momentum_exempt(self):
        """WHALE_MOMENTUM's thesis IS fading the tape; bypass entirely."""
        allowed, reason = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
            setup_class="WHALE_MOMENTUM",
        )
        assert allowed is True
        assert reason == ""

    def test_funding_extreme_exempt(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
            setup_class="FUNDING_EXTREME_SIGNAL",
        )
        assert allowed is True

    def test_liquidation_reversal_exempt(self):
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
            setup_class="LIQUIDATION_REVERSAL",
        )
        assert allowed is True

    def test_setup_class_case_insensitive(self):
        """``whale_momentum`` / ``WHALE_MOMENTUM`` both treated as exempt."""
        for s in ("whale_momentum", "Whale_Momentum", "WHALE_MOMENTUM"):
            allowed, _ = check_btc_direction_gate(
                "LONG", _ind_bearish(), _ind_bearish(),
                _candles_close_below(), setup_class=s,
            )
            assert allowed is True

    def test_non_exempt_setup_still_penalised(self):
        """SR_FLIP_RETEST is NOT exempt — should still get the penalty."""
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
            setup_class="SR_FLIP_RETEST",
        )
        assert allowed is False

    def test_unknown_setup_not_exempt(self):
        """Setup name not in the exempt set should be penalised normally."""
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(),
            _candles_close_below(),
            setup_class="MADE_UP_SETUP",
        )
        assert allowed is False


# ---------------------------------------------------------------------------
# 4H close-vs-EMA confirmation
# ---------------------------------------------------------------------------


class TestFourHourCloseConfirmation:
    def test_4h_bearish_alignment_but_close_above_ema21_neutral(self):
        """4H ema21<ema50 (bearish alignment) but close > ema21 →
        treated as NEUTRAL per ``_classify_btc_4h`` contract (mirrors
        ``ScalpChannel._classify_htf_trend``).  No penalty."""
        ind_4h_bearish = _ind_bearish()  # ema21=100, ema50=102
        candles_above_ema = _candles_close_above(price=101.0)  # close>ema21
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), ind_4h_bearish, candles_above_ema,
        )
        assert allowed is True  # 4H neutral by close-side rule

    def test_4h_close_below_ema21_confirms_bearish(self):
        ind_4h_bearish = _ind_bearish()  # ema21=100
        candles_below = _candles_close_below(price=99.0)
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), ind_4h_bearish, candles_below,
        )
        assert allowed is False  # 4H bearish confirmed, penalty fires

    def test_4h_alignment_only_fallback_when_candles_missing(self):
        """No 4H candles → alignment-only fallback (no close-side check)."""
        allowed, _ = check_btc_direction_gate(
            "LONG", _ind_bearish(), _ind_bearish(), None,
        )
        assert allowed is False


# ---------------------------------------------------------------------------
# Exempt setup list invariant
# ---------------------------------------------------------------------------


def test_exempt_setups_contains_tape_driven_paths():
    """OWNER_BRIEF §3.4a doctrine: tape-driven paths (WHALE / FUNDING /
    LIQ_REVERSAL) are exempt from HTF-correlation penalties.  Pin the
    exempt set so a refactor can't silently widen / narrow it."""
    assert "WHALE_MOMENTUM" in _BTC_DIR_EXEMPT_SETUPS
    assert "FUNDING_EXTREME_SIGNAL" in _BTC_DIR_EXEMPT_SETUPS
    assert "LIQUIDATION_REVERSAL" in _BTC_DIR_EXEMPT_SETUPS
    # Structure paths must NOT be exempt — they need the gate.
    assert "SR_FLIP_RETEST" not in _BTC_DIR_EXEMPT_SETUPS
    assert "FAILED_AUCTION_RECLAIM" not in _BTC_DIR_EXEMPT_SETUPS
    assert "QUIET_COMPRESSION_BREAK" not in _BTC_DIR_EXEMPT_SETUPS
    assert "TREND_PULLBACK_EMA" not in _BTC_DIR_EXEMPT_SETUPS
    assert "DIVERGENCE_CONTINUATION" not in _BTC_DIR_EXEMPT_SETUPS
    assert "LIQUIDITY_SWEEP_REVERSAL" not in _BTC_DIR_EXEMPT_SETUPS


# ---------------------------------------------------------------------------
# Counter-trend mover HARD block (Session 30) — check_countertrend_mover_block
# ---------------------------------------------------------------------------

_CT_BLOCKED = frozenset({"LIQUIDITY_SWEEP_REVERSAL", "SR_FLIP_RETEST"})


def _wide_bullish(ema21=110.0, ema50=100.0, ema21_prev=109.0):
    """Mover-grade bullish: 10% EMA fan, slope up."""
    return {"ema21_last": ema21, "ema50_last": ema50, "ema21_prev": ema21_prev}


def _wide_bearish(ema21=90.0, ema50=100.0, ema21_prev=91.0):
    """Mover-grade bearish: 10% EMA fan, slope down."""
    return {"ema21_last": ema21, "ema50_last": ema50, "ema21_prev": ema21_prev}


def _wide_bull_4h_candles():
    return {"close": [115.0] * 5}  # above ema21=110 → 4h BULLISH confirmed


def _wide_bear_4h_candles():
    return {"close": [85.0] * 5}   # below ema21=90 → 4h BEARISH confirmed


class TestCountertrendMoverBlock:
    """Hard-block a reversal that fades a confirmed strong mover (the SYNUSDT case)."""

    def test_ema_fan_pct(self):
        assert _ema_fan_pct({"ema21_last": 110.0, "ema50_last": 100.0}) == 10.0
        assert _ema_fan_pct({"ema21_last": 90.0, "ema50_last": 100.0}) == 10.0
        assert _ema_fan_pct(None) is None
        assert _ema_fan_pct({"ema21_last": 100.0}) is None          # missing ema50
        assert _ema_fan_pct({"ema21_last": 100.0, "ema50_last": 0.0}) is None  # div-guard

    def test_short_fading_strong_bullish_mover_is_blocked(self):
        # The SYNUSDT case: LSR SHORT into a +parabolic, 1h+4h stacked-up mover.
        allowed, reason = check_countertrend_mover_block(
            "SHORT", _wide_bullish(), _wide_bullish(), _wide_bull_4h_candles(),
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is False
        assert "bullish" in reason

    def test_long_fading_strong_bearish_mover_is_blocked(self):
        allowed, reason = check_countertrend_mover_block(
            "LONG", _wide_bearish(), _wide_bearish(), _wide_bear_4h_candles(),
            setup_class="SR_FLIP_RETEST",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is False
        assert "bearish" in reason

    def test_trend_aligned_short_into_bearish_mover_passes(self):
        # A trend-ALIGNED reversal (SHORT into a down mover) must NOT be blocked.
        allowed, _ = check_countertrend_mover_block(
            "SHORT", _wide_bearish(), _wide_bearish(), _wide_bear_4h_candles(),
            setup_class="SR_FLIP_RETEST",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is True

    def test_narrow_fan_not_blocked_left_to_soft_penalty(self):
        # ema21=100, ema50=98 → 2.04% fan < 3% → ordinary trend, keep soft penalty.
        allowed, _ = check_countertrend_mover_block(
            "SHORT", _ind_bullish(), _ind_bullish(), _candles_close_above(101.0),
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is True

    def test_only_one_htf_opposing_not_blocked(self):
        # 1h bullish-wide, 4h neutral → not BOTH oppose → fail-open.
        allowed, _ = check_countertrend_mover_block(
            "SHORT", _wide_bullish(), _ind_neutral(), {},
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is True

    def test_setup_not_in_blocked_set_passes(self):
        allowed, _ = check_countertrend_mover_block(
            "SHORT", _wide_bullish(), _wide_bullish(), _wide_bull_4h_candles(),
            setup_class="FAILED_AUCTION_RECLAIM",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is True

    def test_missing_data_fail_open(self):
        allowed, _ = check_countertrend_mover_block(
            "SHORT", None, None, None,
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            blocked_setups=_CT_BLOCKED, min_fan_pct=3.0,
        )
        assert allowed is True
