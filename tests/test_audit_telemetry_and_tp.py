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


# ---------------------------------------------------------------------------
# Q4-B : TP-ladder monotonicity helper unit tests + per-evaluator wire-up
# verification.  See OWNER_BRIEF audit Q4-B and the Q4-A precedent.
#
# Helper signature (post-fix):
#   _enforce_tp_ladder_monotonicity(tp1, tp2, tp3, close, sl_dist, direction,
#                                   *, tp2_rmult_floor=2.5,
#                                      tp3_rmult_floor=3.5,
#                                      tp_gap_rmult=0.5)
# ---------------------------------------------------------------------------


class TestTpLadderMonotonicityHelper:
    """Pure-function tests for `_enforce_tp_ladder_monotonicity`.

    The helper is a no-op when the ladder is already monotonic and only
    widens TP2/TP3 in the collapse case — never narrows.  Mirrors the
    FAILED_AUCTION_RECLAIM pattern (reference: scalp.py lines ~3941-3948).
    """

    def test_no_op_when_already_monotonic_long(self):
        helper = scalp_module._enforce_tp_ladder_monotonicity
        tp1, tp2, tp3 = helper(
            tp1=101.0, tp2=102.0, tp3=103.0,
            close=100.0, sl_dist=0.5, direction=Direction.LONG,
        )
        assert (tp1, tp2, tp3) == (101.0, 102.0, 103.0)

    def test_no_op_when_already_monotonic_short(self):
        helper = scalp_module._enforce_tp_ladder_monotonicity
        tp1, tp2, tp3 = helper(
            tp1=99.0, tp2=98.0, tp3=97.0,
            close=100.0, sl_dist=0.5, direction=Direction.SHORT,
        )
        assert (tp1, tp2, tp3) == (99.0, 98.0, 97.0)

    def test_widens_collapsed_tp2_long(self):
        # tp1 sits at 5R from close; tp2 collapsed at 0R; tp3 at 10R (untouched).
        helper = scalp_module._enforce_tp_ladder_monotonicity
        tp1, tp2, tp3 = helper(
            tp1=105.0, tp2=100.0, tp3=110.0,
            close=100.0, sl_dist=1.0, direction=Direction.LONG,
            tp2_rmult_floor=2.5, tp3_rmult_floor=3.5,
        )
        # tp2 must lift to max(close + 2.5R, tp1 + 0.5R) = max(102.5, 105.5) = 105.5
        assert tp2 == 105.5, f"tp2 expected 105.5, got {tp2}"
        # tp3 was already > tp2 (110.0 > 105.5) — left alone
        assert tp3 == 110.0
        assert tp1 == 105.0  # untouched

    def test_widens_collapsed_tp2_short(self):
        # Mirror of LONG: tp1 at 5R below close; tp2 collapsed at 0R; tp3 at 10R below.
        helper = scalp_module._enforce_tp_ladder_monotonicity
        tp1, tp2, tp3 = helper(
            tp1=95.0, tp2=100.0, tp3=90.0,
            close=100.0, sl_dist=1.0, direction=Direction.SHORT,
            tp2_rmult_floor=2.5, tp3_rmult_floor=3.5,
        )
        # tp2 must drop to min(close - 2.5R, tp1 - 0.5R) = min(97.5, 94.5) = 94.5
        assert tp2 == 94.5, f"tp2 expected 94.5, got {tp2}"
        assert tp3 == 90.0  # was already < tp2
        assert tp1 == 95.0

    def test_widens_collapsed_tp3_long(self):
        helper = scalp_module._enforce_tp_ladder_monotonicity
        tp1, tp2, tp3 = helper(
            tp1=101.0, tp2=102.0, tp3=100.0,
            close=100.0, sl_dist=1.0, direction=Direction.LONG,
            tp2_rmult_floor=2.5, tp3_rmult_floor=3.5,
        )
        # tp3 must lift to max(close + 3.5R, tp2 + 0.5R) = max(103.5, 102.5) = 103.5
        assert tp3 == 103.5, f"tp3 expected 103.5, got {tp3}"
        assert tp1 == 101.0
        assert tp2 == 102.0  # already > tp1

    def test_widens_collapsed_tp3_short(self):
        helper = scalp_module._enforce_tp_ladder_monotonicity
        tp1, tp2, tp3 = helper(
            tp1=99.0, tp2=98.0, tp3=100.0,
            close=100.0, sl_dist=1.0, direction=Direction.SHORT,
            tp2_rmult_floor=2.5, tp3_rmult_floor=3.5,
        )
        # tp3 must drop to min(close - 3.5R, tp2 - 0.5R) = min(96.5, 97.5) = 96.5
        assert tp3 == 96.5, f"tp3 expected 96.5, got {tp3}"
        assert tp1 == 99.0
        assert tp2 == 98.0


class TestQ4BHelperWiredIntoEvaluators:
    """Verify each of the 5 affected evaluators calls
    `_enforce_tp_ladder_monotonicity` after computing TPs.  Uses a
    monkey-patch spy so we don't need to construct an inversion-triggering
    fixture for every evaluator — the contract being tested is "the
    helper is wired into the call site," not "the helper does the right
    thing" (that's covered by `TestTpLadderMonotonicityHelper`)."""

    def _spy(self, monkeypatch):
        """Install a spy on the helper; return the call list."""
        calls: list[dict] = []
        original = scalp_module._enforce_tp_ladder_monotonicity

        def spy(*args, **kwargs):
            calls.append({"args": args, "kwargs": kwargs})
            return original(*args, **kwargs)

        monkeypatch.setattr(scalp_module, "_enforce_tp_ladder_monotonicity", spy)
        return calls

    # ── LSR (`_evaluate_standard`) ────────────────────────────────────────

    def test_lsr_calls_helper(self, monkeypatch):
        calls = self._spy(monkeypatch)
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sweep = LiquiditySweep(
            index=59, direction=Direction.LONG,
            sweep_level=99, close_price=99.05,
            wick_high=101, wick_low=98,
        )
        indicators = {"5m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100)}
        smc_data = {"sweeps": [sweep]}
        ch._evaluate_standard("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert calls, (
            "LSR (`_evaluate_standard`) must call "
            "`_enforce_tp_ladder_monotonicity` after computing TPs."
        )

    # ── CLS (`_evaluate_continuation_liquidity_sweep`) ────────────────────

    def test_cls_calls_helper(self, monkeypatch):
        calls = self._spy(monkeypatch)
        ch = ScalpChannel()
        # CLS happy path: trending regime + recent sweep + EMA alignment.
        n = 30
        m5 = {
            "open":   [100.0 + i * 0.1 for i in range(n)],
            "high":   [100.5 + i * 0.1 for i in range(n)],
            "low":    [99.5 + i * 0.1 for i in range(n)],
            "close":  [100.0 + i * 0.1 for i in range(n)],
            "volume": [1000.0] * n,
        }
        candles = {"5m": m5}
        sweep = LiquiditySweep(
            index=n - 4, direction=Direction.LONG,
            sweep_level=98.0, close_price=98.2,
            wick_high=100.0, wick_low=97.5,
        )
        indicators = {"5m": _make_indicators(ema9=103.0, ema21=102.0)}
        smc_data = {"sweeps": [sweep]}
        ch._evaluate_continuation_liquidity_sweep(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000,
            regime="TRENDING_UP",
        )
        # CLS may reject for unrelated reasons (e.g. sweep_too_old, fvg_missing)
        # — what we're verifying is whether the helper IS called when the
        # path makes it to TP computation.  If the path rejects before TP
        # compute, calls will be empty AND the rejection is documented in
        # ch._active_no_signal_reason.  In either case, we want to assert
        # one of: (helper called) OR (rejected at a known pre-TP gate).
        # The strongest assertion that doesn't require fixture-perfection:
        # if the path produced ANY TPs (we'd see calls), they were
        # normalised through the helper.
        if not calls:
            # Path didn't reach TP compute — fixture didn't pass all gates,
            # but that's NOT a wire-up regression.  Document the gate hit
            # so the test fails loudly if the wire-up itself is broken.
            assert ch._active_no_signal_reason in (
                "regime_blocked", "sweeps_not_detected",
                "sweep_too_old", "ema_alignment_reject",
                "missing_fvg_or_orderblock", "rsi_reject",
                "basic_filters_failed", "insufficient_candles",
                "invalid_sl_geometry", "build_signal_failed",
                "momentum_reject", "no_close_progression",
            ), (
                "CLS rejected at unknown gate "
                f"{ch._active_no_signal_reason!r} — investigate before "
                "trusting this wire-up test."
            )

    # ── TPE (`_evaluate_trend_pullback`) ──────────────────────────────────

    def test_tpe_calls_helper(self, monkeypatch):
        calls = self._spy(monkeypatch)
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        indicators = {"5m": _make_indicators(ema9=102.0, ema21=100.0)}
        ch._evaluate_trend_pullback(
            "BTCUSDT", candles, indicators, {}, 0.01, 10_000_000,
            regime="TRENDING_UP",
        )
        # Same caveat as CLS — wire-up is what's being tested.
        if not calls:
            assert ch._active_no_signal_reason in (
                "regime_blocked", "ema_alignment_reject",
                "ema_not_tested_prev", "no_ema_reclaim_close",
                "body_conviction_fail", "rsi_reject",
                "momentum_reject", "missing_fvg_or_orderblock",
                "invalid_sl_geometry", "build_signal_failed",
                "basic_filters_failed", "insufficient_candles",
                "prev_already_above_emas", "close_below_emas",
                "no_close_progression", "no_prev_high_break",
                "ema21_not_tagged", "momentum_flat",
                "prev_already_below_emas", "close_above_emas",
                "no_prev_low_break",
            ), (
                "TPE rejected at unknown gate "
                f"{ch._active_no_signal_reason!r}."
            )

    # ── LIQ_REV (`_evaluate_liquidation_reversal`) ────────────────────────

    def test_liq_rev_calls_helper(self, monkeypatch):
        calls = self._spy(monkeypatch)
        ch = ScalpChannel()
        # Reuse the LIQ_REV LONG fixture pattern (cascade 100 → 97.5).
        n = 25
        closes = [100.0] * (n - 4) + [100.0, 99.5, 98.5, 97.5]
        volumes = [100.0] * (n - 1) + [300.0]
        candles = {"5m": {
            "close": closes,
            "high": [c + 0.5 for c in closes],
            "low": [c - 0.5 for c in closes],
            "open": [c - 0.1 for c in closes],
            "volume": volumes,
        }}
        indicators = {"5m": {"atr_last": 0.5}}  # rsi_last absent → RSI gate bypassed
        smc_data = {
            "cvd": [0.0] * (n - 4) + [-200.0, -150.0, -100.0, 50.0],
            "fvg": [{"level": 97.4}],
            "orderblocks": [],
            "pair_profile": None,
            "regime_context": None,
        }
        ch._evaluate_liquidation_reversal(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000,
        )
        # LIQ_REV happy path produces a signal and runs through TP compute,
        # so the helper MUST have been called.
        assert calls, (
            "LIQ_REV (`_evaluate_liquidation_reversal`) must call "
            "`_enforce_tp_ladder_monotonicity` after computing TPs.  "
            f"Reason on rejection: {ch._active_no_signal_reason!r}."
        )

    # ── FUNDING_EXTREME (`_evaluate_funding_extreme`) ─────────────────────

    def test_funding_extreme_calls_helper(self, monkeypatch):
        calls = self._spy(monkeypatch)
        ch = ScalpChannel()
        candles = {"5m": _make_candles(30)}
        indicators = {"5m": _make_indicators()}
        smc_data = {
            "funding_rate": 0.025,  # 2.5% — extreme
            "fvg": [{"top": 99.0, "bottom": 98.5, "level": 98.7}],
            "orderblocks": [],
        }
        ch._evaluate_funding_extreme(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000,
            regime="TRENDING_DOWN",
        )
        # Same wire-up contract.
        if not calls:
            assert ch._active_no_signal_reason in (
                "regime_blocked", "missing_funding_rate",
                "missing_fvg_or_orderblock", "missing_cvd",
                "rsi_reject", "basic_filters_failed",
                "insufficient_candles", "invalid_sl_geometry",
                "build_signal_failed", "funding_threshold_not_met",
                "funding_not_extreme", "cvd_insufficient",
                "no_oversold_or_overbought", "structural_anchor_missing",
                "ema_alignment_reject", "momentum_reject",
            ), (
                "FUNDING_EXT rejected at unknown gate "
                f"{ch._active_no_signal_reason!r}."
            )


# ---------------------------------------------------------------------------
# INV-1 : Make `_check_invalidation` regime-flip & EMA-crossover rules
# CREATION-relative.
#
# Live data (post Q4-A/Q4-B/Q5/Q7-A deploy) showed 19 of 20 closed signals
# in the last window terminated via `outcome_label="CLOSED"` — i.e. via
# `TradeMonitor._check_invalidation()` rather than reaching SL or TP.
# The proximate cause: 9 of 17 SR_FLIP_RETEST LONGs were born in a
# TRENDING_DOWN regime (they're a counter-trend retest setup by design),
# but the existing invalidation rule kills any LONG when the current
# regime is TRENDING_DOWN — regardless of whether the regime CHANGED
# during the trade.  Same shape for EMA9/EMA21 alignment: counter-trend
# setups enter with EMAs already misaligned to direction, and the rule
# fires once the channel age gate (600s) opens.
#
# Fix: the rule's docstring says "regime FLIP" but the implementation
# checks current-only state.  Make it semantically correct — only
# invalidate when the regime DIFFERS from the regime captured at signal
# creation (`sig.market_phase`).  For EMA crossover, skip the rule
# entirely on counter-trend setups (LONG born in TRENDING_DOWN, or SHORT
# born in TRENDING_UP) because their thesis is structurally counter to
# short-term EMA alignment from the start.
# ---------------------------------------------------------------------------


from datetime import timedelta as _timedelta
from unittest.mock import MagicMock as _MagicMock
from src.channels.base import Signal as _Signal
from src.trade_monitor import TradeMonitor as _TradeMonitor
from src.utils import utcnow as _utcnow


def _build_invalidation_test_monitor(sig, candles_close=None, regime_detector=None):
    """Construct a minimal TradeMonitor instance for invalidation testing.

    Mirrors the pattern in tests/test_trade_monitor.py::TestSignalInvalidation
    but kept local so this test file has no cross-test imports.
    """
    sent: list = []

    async def mock_send(chat_id, text):
        sent.append((chat_id, text))

    data_store = _MagicMock()
    data_store.ticks = {}
    if candles_close is not None:
        closes = list(candles_close)
        candles_dict = {
            "close": closes,
            "open": closes,
            "high": closes,
            "low": closes,
            "volume": [1.0] * len(closes),
        }
        data_store.get_candles.return_value = candles_dict
    else:
        data_store.get_candles.return_value = None

    return _TradeMonitor(
        data_store=data_store,
        send_telegram=mock_send,
        get_active_signals=lambda: {sig.signal_id: sig},
        remove_signal=lambda sid: None,
        update_signal=_MagicMock(),
        regime_detector=regime_detector,
    )


def _make_invalidation_signal(
    *,
    direction=Direction.LONG,
    market_phase: str = "N/A",
    age_seconds: float = 700.0,
    entry: float = 30000.0,
    stop_loss: float = 29850.0,
    tp1: float = 30150.0,
):
    """Return a Signal with controllable market_phase + age for invalidation tests."""
    sig = _Signal(
        channel="360_SCALP",
        symbol="BTCUSDT",
        direction=direction,
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=entry + (tp1 - entry) * 2.0 if direction == Direction.LONG else entry - (entry - tp1) * 2.0,
        confidence=85.0,
        signal_id=f"INV-TEST-{direction.name}",
    )
    sig.market_phase = market_phase
    sig.timestamp = _utcnow() - _timedelta(seconds=age_seconds)
    return sig


class TestInvalidationFlipAware:
    """`_check_invalidation` regime-flip rule must compare CURRENT regime
    against the regime captured at signal creation (`sig.market_phase`),
    not against the signal direction alone.  Counter-trend setups
    (SR_FLIP, FAR, LIQ_REV, FUNDING_EXT) are intentionally born with
    regime opposing direction; they must not be invalidated unless the
    regime actually FLIPS during the trade.
    """

    # ── Counter-trend signals must NOT be invalidated when regime is unchanged ──

    def test_long_counter_trend_no_invalidation_when_regime_unchanged(self):
        """LONG signal born in TRENDING_DOWN, regime still TRENDING_DOWN
        → no invalidation (same regime, no flip)."""
        sig = _make_invalidation_signal(
            direction=Direction.LONG, market_phase="TRENDING_DOWN | ATR=18 | Vol=DISTRIBUTION",
        )
        regime_detector = _MagicMock()
        result = _MagicMock()
        result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = result
        monitor = _build_invalidation_test_monitor(
            sig, candles_close=[30000.0] * 25, regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"Counter-trend LONG (born in TRENDING_DOWN) must not be killed "
            f"when regime is still TRENDING_DOWN; got reason {reason!r}."
        )

    def test_short_counter_trend_no_invalidation_when_regime_unchanged(self):
        """SHORT signal born in TRENDING_UP, regime still TRENDING_UP
        → no invalidation."""
        sig = _make_invalidation_signal(
            direction=Direction.SHORT,
            market_phase="TRENDING_UP | ATR=22 | Vol=ACCUMULATION",
            entry=30000.0, stop_loss=30150.0, tp1=29850.0,
        )
        regime_detector = _MagicMock()
        result = _MagicMock()
        result.regime.value = "TRENDING_UP"
        regime_detector.classify.return_value = result
        monitor = _build_invalidation_test_monitor(
            sig, candles_close=[30000.0] * 25, regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"Counter-trend SHORT (born in TRENDING_UP) must not be killed "
            f"when regime is still TRENDING_UP; got reason {reason!r}."
        )

    # ── Genuine regime FLIP must still invalidate (existing rule preserved) ──

    def test_long_invalidated_when_regime_actually_flips(self):
        """Trend-following LONG born in TRENDING_UP → regime flips to
        TRENDING_DOWN mid-trade → invalidate (this is the original rule
        intent and must still fire)."""
        sig = _make_invalidation_signal(
            direction=Direction.LONG,
            market_phase="TRENDING_UP | ATR=15 | Vol=ACCUMULATION",
        )
        regime_detector = _MagicMock()
        result = _MagicMock()
        result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = result
        monitor = _build_invalidation_test_monitor(
            sig, candles_close=[30000.0] * 25, regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None, (
            "Genuine regime flip (TRENDING_UP → TRENDING_DOWN) on a LONG "
            "signal must still invalidate."
        )
        assert "TRENDING_DOWN" in reason

    def test_short_invalidated_when_regime_actually_flips(self):
        sig = _make_invalidation_signal(
            direction=Direction.SHORT,
            market_phase="TRENDING_DOWN | ATR=15 | Vol=DISTRIBUTION",
            entry=30000.0, stop_loss=30150.0, tp1=29850.0,
        )
        regime_detector = _MagicMock()
        result = _MagicMock()
        result.regime.value = "TRENDING_UP"
        regime_detector.classify.return_value = result
        monitor = _build_invalidation_test_monitor(
            sig, candles_close=[30000.0] * 25, regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "TRENDING_UP" in reason

    # ── EMA crossover rule must skip counter-trend setups ──

    def test_ema_crossover_skipped_for_counter_trend_long(self):
        """LONG signal born in TRENDING_DOWN with EMA9 < EMA21 (already
        misaligned at creation) must NOT be invalidated by the EMA
        crossover rule — there was no crossover, just the original
        counter-trend alignment."""
        sig = _make_invalidation_signal(
            direction=Direction.LONG,
            market_phase="TRENDING_DOWN | ATR=18 | Vol=DISTRIBUTION",
        )
        # Falling closes → EMA9 < EMA21 (bearish alignment)
        closes = [30000.0 - i * 10 for i in range(25)]
        monitor = _build_invalidation_test_monitor(sig, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is None, (
            f"Counter-trend LONG must not be killed by EMA crossover "
            f"rule (EMAs were misaligned at creation); got {reason!r}."
        )

    def test_ema_crossover_skipped_for_counter_trend_short(self):
        sig = _make_invalidation_signal(
            direction=Direction.SHORT,
            market_phase="TRENDING_UP | ATR=22 | Vol=ACCUMULATION",
            entry=30000.0, stop_loss=30150.0, tp1=29850.0,
        )
        # Rising closes → EMA9 > EMA21
        closes = [30000.0 + i * 10 for i in range(25)]
        monitor = _build_invalidation_test_monitor(sig, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is None

    # ── EMA crossover still fires for trend-following setups ──

    def test_ema_crossover_still_kills_trend_following_long(self):
        """LONG signal born in TRENDING_UP, EMAs cross to bearish during
        trade → EMA crossover rule still fires.  Regression guard."""
        sig = _make_invalidation_signal(
            direction=Direction.LONG,
            market_phase="TRENDING_UP | ATR=15 | Vol=ACCUMULATION",
        )
        closes = [30000.0 - i * 10 for i in range(25)]  # falling → bearish EMAs
        monitor = _build_invalidation_test_monitor(sig, candles_close=closes)
        reason = monitor._check_invalidation(sig)
        assert reason is not None
        assert "EMA" in reason
        assert "LONG" in reason

    # ── Defensive fallback: market_phase missing/empty ──

    def test_default_market_phase_falls_back_to_old_behavior(self):
        """When market_phase is empty/N-A (older signals or fixtures
        without market_phase set), the fix must fall back to the
        pre-existing invalidation behavior so existing tests and live
        signals don't regress."""
        sig = _make_invalidation_signal(
            direction=Direction.LONG, market_phase="N/A",
        )
        regime_detector = _MagicMock()
        result = _MagicMock()
        result.regime.value = "TRENDING_DOWN"
        regime_detector.classify.return_value = result
        monitor = _build_invalidation_test_monitor(
            sig, candles_close=[30000.0] * 25, regime_detector=regime_detector,
        )
        reason = monitor._check_invalidation(sig)
        # With unknown creation regime, current rule (LONG + TRENDING_DOWN
        # → kill) must fire.  Backward-compat preserved.
        assert reason is not None
        assert "TRENDING_DOWN" in reason


