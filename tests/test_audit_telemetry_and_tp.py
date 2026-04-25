"""Regression tests for the second-round CTE audit findings.

Covers:
- Q5-A : LIQUIDITY_SWEEP_REVERSAL (`_evaluate_standard`) must emit
  `_active_no_signal_reason == "build_signal_failed"` when
  `build_channel_signal` returns None.  Previously this path used a bare
  ``return None`` which silently dropped the suppression-telemetry reason.
- Q5-B : WHALE_MOMENTUM (`_evaluate_whale_momentum`) must do the same.  The
  prior implementation fell through an ``if sig is not None:`` block and
  returned None implicitly, again without setting the reason.
- Q4-A : SR_FLIP_RETEST (`_evaluate_sr_flip_retest`) 4h-data branch must
  enforce TP2 strictly above TP1 with a meaningful gap (LONG) / strictly
  below TP1 with a meaningful gap (SHORT).  Pre-fix, when the 4h max/min
  failed the `tp2 <= tp1` / `tp2 >= tp1` check the fallback set
  ``tp2 = close ± sl_dist * 1.5`` without enforcing the relationship to
  tp1, so partial-close geometry could collapse or invert.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.channels import scalp as scalp_module
from src.channels.scalp import ScalpChannel
from src.smc import Direction, LiquiditySweep


# ---------------------------------------------------------------------------
# Helpers (kept local; mirrors the patterns used in tests/test_channels.py).
# ---------------------------------------------------------------------------


def _make_candles(n=60, base=100.0, trend=0.1):
    close = np.cumsum(np.ones(n) * trend) + base
    high = close + 0.5
    low = close - 0.5
    volume = np.ones(n) * 1000
    return {
        "open": close - 0.1,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }


def _make_indicators(adx_val=30, atr_val=0.5, ema9=101, ema21=100, ema200=95,
                     rsi_val=50, bb_upper=103, bb_mid=100, bb_lower=97, mom=0.5):
    return {
        "adx_last": adx_val,
        "atr_last": atr_val,
        "ema9_last": ema9,
        "ema21_last": ema21,
        "ema200_last": ema200,
        "rsi_last": rsi_val,
        "bb_upper_last": bb_upper,
        "bb_mid_last": bb_mid,
        "bb_lower_last": bb_lower,
        "momentum_last": mom,
    }


def _make_srflip_candles_long(n=60, flip_offset=3, level=100.0):
    """Mirror of tests/test_channels.py::_make_srflip_candles_long.

    Replicated locally so this file has no cross-test imports.
    """
    closes = np.ones(n) * 99.8
    highs = np.ones(n) * (level + 0.3)
    lows = np.ones(n) * (level - 1.0)
    opens = np.ones(n) * 99.7

    prior_start = max(0, n - 50)
    prior_end = n - 8
    for i in range(prior_start, prior_end):
        highs[i] = level

    flip_idx = n - flip_offset
    highs[flip_idx] = level + 1.0
    closes[flip_idx] = level * 1.002

    closes[-2] = level * 1.001
    opens[-2] = level * 1.0012

    closes[-1] = level * 1.001
    opens[-1] = level * 1.0015
    highs[-1] = level * 1.002
    lows[-1] = level * 0.999

    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    }


def _make_srflip_candles_short(n=60, flip_offset=3, level=100.0):
    closes = np.ones(n) * (level + 0.2)
    highs = np.ones(n) * (level + 1.0)
    lows = np.ones(n) * (level - 0.3)
    opens = np.ones(n) * (level + 0.3)

    prior_start = max(0, n - 50)
    prior_end = n - 8
    for i in range(prior_start, prior_end):
        lows[i] = level

    flip_idx = n - flip_offset
    lows[flip_idx] = level - 1.0
    closes[flip_idx] = level * 0.998

    closes[-2] = level * 0.999
    opens[-2] = level * 0.9988

    closes[-1] = level * 0.999
    opens[-1] = level * 0.9985
    highs[-1] = level * 1.001
    lows[-1] = level * 0.998

    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    }


def _srflip_indicators_long(rsi_val=55.0, ema9=102.0, ema21=99.0):
    return {"5m": _make_indicators(rsi_val=rsi_val, ema9=ema9, ema21=ema21)}


def _srflip_indicators_short(rsi_val=45.0, ema9=98.0, ema21=101.0):
    return {"5m": _make_indicators(rsi_val=rsi_val, ema9=ema9, ema21=ema21)}


def _srflip_smc(direction="LONG"):
    if direction == "LONG":
        return {"fvg": [{"top": 100.5, "bottom": 99.8, "type": "bullish"}]}
    return {"fvg": [{"top": 100.2, "bottom": 99.5, "type": "bearish"}]}


# ---------------------------------------------------------------------------
# Q5-A : LIQUIDITY_SWEEP_REVERSAL build_signal_failed telemetry.
# ---------------------------------------------------------------------------


class TestLsrBuildSignalFailedTelemetry:
    """`_evaluate_standard` must publish `build_signal_failed` when the
    builder returns None — never a bare ``return None``."""

    def test_lsr_records_build_signal_failed_reason(self, monkeypatch):
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sweep = LiquiditySweep(
            index=59,
            direction=Direction.LONG,
            sweep_level=99,
            close_price=99.05,
            wick_high=101,
            wick_low=98,
        )
        indicators = {"5m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100)}
        smc_data = {
            "sweeps": [sweep],
            "fvg": [{"gap_high": 101.0, "gap_low": 100.5, "type": "bullish"}],
        }

        # Force build_channel_signal to fail at the very last gate.  Earlier
        # rejects must not fire — the fixture above is the same one used by
        # `test_signal_generated_on_valid_conditions`, which produces a
        # signal under the real builder.
        monkeypatch.setattr(scalp_module, "build_channel_signal", lambda **_: None)

        sig = ch._evaluate_standard("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000)

        assert sig is None
        assert ch._active_no_signal_reason == "build_signal_failed", (
            "LIQUIDITY_SWEEP_REVERSAL must emit 'build_signal_failed' when the "
            "signal builder returns None; got "
            f"{ch._active_no_signal_reason!r}.  Bare `return None` drops "
            "suppression telemetry — see Q5-A audit finding."
        )


# ---------------------------------------------------------------------------
# Q5-B : WHALE_MOMENTUM build_signal_failed telemetry.
# ---------------------------------------------------------------------------


class TestWhaleBuildSignalFailedTelemetry:
    """`_evaluate_whale_momentum` must publish `build_signal_failed` when the
    builder returns None.  Pre-fix the path fell through an
    ``if sig is not None`` guard and returned the None implicitly."""

    def test_whale_records_build_signal_failed_reason(self, monkeypatch):
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators()}
        ticks = [
            {"price": 100.0, "qty": 15000, "isBuyerMaker": False},
            {"price": 100.0, "qty": 5000, "isBuyerMaker": True},
        ]
        smc_data = {
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
        }

        monkeypatch.setattr(scalp_module, "build_channel_signal", lambda **_: None)

        sig = ch._evaluate_whale_momentum(
            "ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000
        )

        assert sig is None
        assert ch._active_no_signal_reason == "build_signal_failed", (
            "WHALE_MOMENTUM must emit 'build_signal_failed' when the signal "
            "builder returns None; got "
            f"{ch._active_no_signal_reason!r}.  Implicit fall-through drops "
            "suppression telemetry — see Q5-B audit finding."
        )


# ---------------------------------------------------------------------------
# Q4-A : SR_FLIP_RETEST 4h-data branch TP1/TP2 monotonicity.
# ---------------------------------------------------------------------------


def _flat_4h_candles(n: int, level: float):
    """4h candles whose entire OHLC sits at `level` (no recent extension).

    Used to force the SR_FLIP `tp2 <= tp1` (LONG) /  `tp2 >= tp1` (SHORT)
    fallback branch.

    Returned as plain Python lists (not numpy arrays) so the channel's
    ``if _4h_highs`` truthy-check doesn't blow up on multi-element ndarrays.
    Production candles arrive as lists, so this matches the real shape.
    """
    return {
        "open": [level] * n,
        "high": [level] * n,
        "low": [level] * n,
        "close": [level] * n,
        "volume": [1000.0] * n,
    }


class TestSrFlip4hBranchTpMonotonicity:
    """SR_FLIP_RETEST 4h-data branch must keep TP2 strictly beyond TP1.

    Pre-fix code path (line 2474–2475 LONG, 2478–2479 SHORT):
        if tp2 <= tp1:
            tp2 = close + sl_dist * 1.5
    fails to enforce tp2 > tp1, so when the 5m swing tp1 already exceeds
    `close + 1.5R` (e.g. tp1 sits at the flip extreme) the fallback leaves
    tp2 below tp1 (inversion) or equal to tp1 (collapse).  The fix mirrors
    the FAILED_AUCTION_RECLAIM monotonicity guard:

        tp2 = max(close + sl_dist * 1.5, tp1 + sl_dist * 0.5)

    Both LONG and SHORT must have the guard.
    """

    def _call_long(self, candles, indicators, smc_data, regime="RANGING"):
        ch = ScalpChannel()
        return ch._evaluate_sr_flip_retest(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime,
        )

    def _call_short(self, candles, indicators, smc_data, regime="RANGING"):
        ch = ScalpChannel()
        return ch._evaluate_sr_flip_retest(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime,
        )

    def test_long_4h_branch_keeps_tp2_above_tp1(self):
        # 4h candles flat at 99.5 → 4h max = 99.5 < tp1 (5m swing high = 101.0)
        # Forces the broken fallback branch on current code.
        candles = {
            "5m": _make_srflip_candles_long(n=60, flip_offset=3),
            "4h": _flat_4h_candles(20, level=99.5),
        }
        sig = self._call_long(
            candles, _srflip_indicators_long(), _srflip_smc(direction="LONG")
        )
        assert sig is not None, (
            "Fixture must produce a SR_FLIP_RETEST signal — if this fails, the "
            "test environment changed, not the fix."
        )
        sl_dist = abs(sig.entry - sig.stop_loss)
        assert sl_dist > 0
        assert sig.tp2 > sig.tp1, (
            f"TP2 must be strictly above TP1 in 4h-data fallback branch; got "
            f"tp1={sig.tp1!r}, tp2={sig.tp2!r}, sl_dist={sl_dist!r}.  "
            "See Q4-A audit finding."
        )
        assert sig.tp2 >= sig.tp1 + sl_dist * 0.4, (
            f"TP2 must clear TP1 by ≥ 0.4R; got "
            f"tp1={sig.tp1!r}, tp2={sig.tp2!r}, sl_dist={sl_dist!r}.  "
            "Mirrors the FAR-pattern monotonicity guard."
        )
        # And of course tp3 monotonic above tp2 (existing invariant; included
        # so the regression covers the full ladder).
        assert sig.tp3 > sig.tp2, (
            f"TP3 must remain above TP2; got tp2={sig.tp2!r}, tp3={sig.tp3!r}."
        )

    def test_short_4h_branch_keeps_tp2_below_tp1(self):
        # 4h candles flat at 100.5 → 4h min = 100.5 > tp1 (5m swing low = 99.0)
        # Forces the broken SHORT fallback branch on current code.
        candles = {
            "5m": _make_srflip_candles_short(n=60, flip_offset=3),
            "4h": _flat_4h_candles(20, level=100.5),
        }
        sig = self._call_short(
            candles, _srflip_indicators_short(), _srflip_smc(direction="SHORT")
        )
        assert sig is not None, (
            "Fixture must produce a SR_FLIP_RETEST SHORT signal — if this "
            "fails, the test environment changed, not the fix."
        )
        sl_dist = abs(sig.entry - sig.stop_loss)
        assert sl_dist > 0
        assert sig.tp2 < sig.tp1, (
            f"TP2 must be strictly below TP1 (SHORT) in 4h-data fallback "
            f"branch; got tp1={sig.tp1!r}, tp2={sig.tp2!r}, "
            f"sl_dist={sl_dist!r}.  See Q4-A audit finding."
        )
        assert sig.tp2 <= sig.tp1 - sl_dist * 0.4, (
            f"TP2 must clear TP1 by ≥ 0.4R below (SHORT); got "
            f"tp1={sig.tp1!r}, tp2={sig.tp2!r}, sl_dist={sl_dist!r}."
        )
        assert sig.tp3 < sig.tp2, (
            f"TP3 must remain below TP2 (SHORT); got tp2={sig.tp2!r}, "
            f"tp3={sig.tp3!r}."
        )


# ---------------------------------------------------------------------------
# Q7-A : Conservative regime widening for TREND_PULLBACK_EMA and
# DIVERGENCE_CONTINUATION.  Adds WEAK_TREND only; STRONG_TREND and
# BREAKOUT_EXPANSION must continue to reject.
#
# Tests assert reason codes only — they don't depend on the full happy-path
# fixtures (tests/test_channels.py::TestTrendPullbackEntryQuality has
# unrelated pre-existing failures).
# ---------------------------------------------------------------------------


def _tpe_indicators(ema9: float = 102.0, ema21: float = 100.0):
    """Indicators for TREND_PULLBACK_EMA: configurable EMA alignment."""
    return {"5m": _make_indicators(ema9=ema9, ema21=ema21)}


def _div_cont_indicators(ema9: float = 102.0, ema21: float = 100.0):
    """Indicators for DIVERGENCE_CONTINUATION: configurable EMA alignment."""
    return {"5m": _make_indicators(ema9=ema9, ema21=ema21)}


class TestTpeRegimeWideningWeakTrend:
    """`_evaluate_trend_pullback` (TREND_PULLBACK_EMA) must accept
    WEAK_TREND while continuing to block STRONG_TREND and
    BREAKOUT_EXPANSION (conservative widening, Q7-A)."""

    def _call(self, regime: str, indicators=None):
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sig = ch._evaluate_trend_pullback(
            "BTCUSDT",
            candles,
            indicators if indicators is not None else _tpe_indicators(),
            {},
            0.01,
            10_000_000,
            regime=regime,
        )
        return ch, sig

    def test_weak_trend_passes_regime_gate_long(self):
        ch, sig = self._call("WEAK_TREND", _tpe_indicators(ema9=102.0, ema21=100.0))
        # The regime gate must let this through.  Whether the signal then
        # builds depends on the rest of the pipeline; the regime-gate
        # contract is "reason is not 'regime_blocked'".
        assert ch._active_no_signal_reason != "regime_blocked", (
            "WEAK_TREND must clear the TPE regime gate; got reason "
            f"{ch._active_no_signal_reason!r}."
        )

    def test_weak_trend_rejects_when_emas_missing(self):
        # When EMAs are absent (None) and regime=WEAK_TREND, the new branch
        # must reject with ema_alignment_reject (direction cannot be derived).
        bad_ind = {"5m": {k: None for k in (
            "adx_last", "atr_last", "ema9_last", "ema21_last",
            "ema200_last", "rsi_last", "momentum_last",
        )}}
        ch, sig = self._call("WEAK_TREND", bad_ind)
        assert sig is None
        assert ch._active_no_signal_reason == "ema_alignment_reject", (
            "Missing EMAs in WEAK_TREND must reject with "
            "'ema_alignment_reject', not 'regime_blocked'; got "
            f"{ch._active_no_signal_reason!r}."
        )

    def test_strong_trend_still_blocked(self):
        ch, sig = self._call("STRONG_TREND")
        assert sig is None
        assert ch._active_no_signal_reason == "regime_blocked", (
            "Conservative widening: STRONG_TREND must still reject for TPE; "
            f"got {ch._active_no_signal_reason!r}."
        )

    def test_breakout_expansion_still_blocked(self):
        ch, sig = self._call("BREAKOUT_EXPANSION")
        assert sig is None
        assert ch._active_no_signal_reason == "regime_blocked", (
            "Conservative widening: BREAKOUT_EXPANSION must still reject "
            f"for TPE; got {ch._active_no_signal_reason!r}."
        )


class TestDivContRegimeWideningWeakTrend:
    """`_evaluate_divergence_continuation` (DIVERGENCE_CONTINUATION) must
    accept WEAK_TREND while continuing to block STRONG_TREND and
    BREAKOUT_EXPANSION (conservative widening, Q7-A)."""

    def _call(self, regime: str, indicators=None):
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sig = ch._evaluate_divergence_continuation(
            "BTCUSDT",
            candles,
            indicators if indicators is not None else _div_cont_indicators(),
            {},
            0.01,
            10_000_000,
            regime=regime,
        )
        return ch, sig

    def test_weak_trend_passes_regime_gate(self):
        ch, sig = self._call("WEAK_TREND", _div_cont_indicators(ema9=102.0, ema21=100.0))
        assert ch._active_no_signal_reason != "regime_blocked", (
            "WEAK_TREND must clear the DIV_CONT regime gate; got reason "
            f"{ch._active_no_signal_reason!r}."
        )

    def test_strong_trend_still_blocked(self):
        ch, sig = self._call("STRONG_TREND")
        assert sig is None
        assert ch._active_no_signal_reason == "regime_blocked", (
            "Conservative widening: STRONG_TREND must still reject for "
            f"DIV_CONT; got {ch._active_no_signal_reason!r}."
        )

    def test_breakout_expansion_still_blocked(self):
        ch, sig = self._call("BREAKOUT_EXPANSION")
        assert sig is None
        assert ch._active_no_signal_reason == "regime_blocked", (
            "Conservative widening: BREAKOUT_EXPANSION must still reject "
            f"for DIV_CONT; got {ch._active_no_signal_reason!r}."
        )
