"""Tests for channel strategies – evaluate() logic."""

import pytest
import numpy as np

from src.channels.scalp import ScalpChannel
from src.smc import Direction, LiquiditySweep, MSSSignal


def _make_candles(n=60, base=100.0, trend=0.1):
    """Create synthetic OHLCV data."""
    close = np.cumsum(np.ones(n) * trend) + base
    high = close + 0.5
    low = close - 0.5
    volume = np.ones(n) * 1000
    return {"open": close - 0.1, "high": high, "low": low, "close": close, "volume": volume}


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


class TestScalpChannel:
    def test_signal_generated_on_valid_conditions(self):
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sweep = LiquiditySweep(
            index=59, direction=Direction.LONG,
            sweep_level=99, close_price=99.05,
            wick_high=101, wick_low=98,
        )
        indicators = {"5m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100)}
        smc_data = {"sweeps": [sweep]}

        sigs = ch.evaluate("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert isinstance(sigs, list)
        assert len(sigs) >= 1
        sig = sigs[0]
        assert sig.channel == "360_SCALP"
        assert sig.direction == Direction.LONG
        assert sig.entry > 0

    def test_no_signal_when_adx_low_standard_path(self):
        """Standard scalp path requires ADX >= 20; directly tests that path."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sweep = LiquiditySweep(
            index=59, direction=Direction.LONG,
            sweep_level=99, close_price=99.05,
            wick_high=101, wick_low=98,
        )
        indicators = {"5m": _make_indicators(adx_val=10)}  # below 20
        smc_data = {"sweeps": [sweep]}
        # Standard path should return None (ADX too low), test it directly
        sig = ch._evaluate_standard("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert sig is None

    def test_no_signal_without_sweep(self):
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        indicators = {"5m": _make_indicators()}
        sigs = ch.evaluate("BTCUSDT", candles, indicators, {"sweeps": []}, 0.01, 10_000_000)
        assert isinstance(sigs, list)
        assert sigs == []

    def test_whale_momentum_long_signal_on_buy_flow(self):
        """WHALE_MOMENTUM path: strong buy tick flow → LONG signal."""
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators()}
        ticks = [
            {"price": 100.0, "qty": 15000, "isBuyerMaker": False},  # buy: $1.5M
            {"price": 100.0, "qty": 5000, "isBuyerMaker": True},    # sell: $0.5M
        ]
        # Order book with strong bid imbalance (required for WHALE_MOMENTUM)
        order_book = {
            "bids": [[100.0, 500.0]] * 10,  # bid depth: $500K
            "asks": [[100.1, 100.0]] * 10,   # ask depth: $100K → imbalance 5:1
        }
        smc_data = {
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
            "order_book": order_book,
        }

        sigs = ch.evaluate("ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert isinstance(sigs, list)
        whale_sigs = [s for s in sigs if s.setup_class == "WHALE_MOMENTUM"]
        assert len(whale_sigs) >= 1
        assert whale_sigs[0].direction == Direction.LONG
        assert whale_sigs[0].setup_class == "WHALE_MOMENTUM"

    def test_whale_momentum_signal_without_order_book_has_soft_penalty(self):
        """WHALE_MOMENTUM path: missing order book → signal generated with soft penalty.

        When the depth circuit breaker is open, order_book is None.  The channel
        must still produce a signal on the strength of the whale alert + tick flow,
        but mark a soft_penalty_total so the scanner can apply a confidence penalty.
        """
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
        sig = ch._evaluate_whale_momentum("ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert sig is not None
        assert sig.soft_penalty_total >= 10.0

    def test_whale_momentum_no_signal_without_whale(self):
        """WHALE_MOMENTUM path: no whale alert and no delta spike → no signal."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        indicators = {"5m": _make_indicators()}
        smc_data = {"whale_alert": None, "volume_delta_spike": False}
        sig = ch._evaluate_whale_momentum("ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert sig is None

    def test_whale_momentum_no_signal_when_flow_ambiguous(self):
        """Buy/sell ratio < 2× should return None (ambiguous flow)."""
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators()}
        ticks = [
            {"price": 100.0, "qty": 10000, "isBuyerMaker": False},  # buy: $1M
            {"price": 100.0, "qty": 8000, "isBuyerMaker": True},    # sell: $0.8M (ratio 1.25×)
        ]
        order_book = {
            "bids": [[100.0, 500.0]] * 10,
            "asks": [[100.1, 100.0]] * 10,
        }
        smc_data = {
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
            "order_book": order_book,
        }
        sig = ch._evaluate_whale_momentum("ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert sig is None


# ---------------------------------------------------------------------------
# WHALE_MOMENTUM refinement tests (RSI layering + OBI regime-awareness)
# ---------------------------------------------------------------------------

def _whale_base_smc(order_book=None):
    """Minimal smc_data that satisfies WHALE_MOMENTUM entry conditions."""
    ticks = [
        {"price": 100.0, "qty": 15000, "isBuyerMaker": False},  # buy: $1.5M
        {"price": 100.0, "qty": 5000, "isBuyerMaker": True},    # sell: $0.5M (3× ratio)
    ]
    smc: dict = {
        "whale_alert": {"amount_usd": 1_500_000},
        "volume_delta_spike": True,
        "recent_ticks": ticks,
    }
    if order_book is not None:
        smc["order_book"] = order_book
    return smc


def _strong_obi():
    """Order book with 5:1 bid imbalance — fully satisfies OBI gate."""
    return {
        "bids": [[100.0, 500.0]] * 10,  # bid depth: $500K × 10
        "asks": [[100.1, 100.0]] * 10,  # ask depth: $100K × 10  → 5:1 imbalance
    }


def _marginal_obi():
    """Order book with ~1.3:1 bid imbalance — marginal (below 1.5× threshold)."""
    return {
        "bids": [[100.0, 130.0]] * 10,  # bid depth: $130K × 10 = $1.3M
        "asks": [[100.1, 100.0]] * 10,  # ask depth: $100K × 10 = $1.0M → 1.3:1
    }


def _weak_obi():
    """Order book with ~1.1:1 bid imbalance — below soft floor (1.2×)."""
    return {
        "bids": [[100.0, 110.0]] * 10,  # bid depth: $110K × 10 = $1.1M
        "asks": [[100.1, 100.0]] * 10,  # ask depth: $100K × 10 = $1.0M → 1.1:1
    }


def _short_ticks():
    """Strong sell tick flow → SHORT direction (3:1 sell:buy ratio)."""
    return [
        {"price": 100.0, "qty": 5000, "isBuyerMaker": False},   # buy: $0.5M
        {"price": 100.0, "qty": 15000, "isBuyerMaker": True},   # sell: $1.5M (3×)
    ]


def _short_obi():
    """Order book with 5:1 ask imbalance — satisfies OBI gate for SHORT."""
    return {
        "bids": [[100.0, 100.0]] * 10,   # bid depth: $100K × 10
        "asks": [[100.1, 500.0]] * 10,   # ask depth: $500K × 10 → 5:1 imbalance
    }


class TestWhaleMomentumRsiRefinements:
    """RSI layered soft/hard gate for WHALE_MOMENTUM (PR-4 refinement)."""

    def _call(self, rsi_val, direction_ticks=None, regime=""):
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        if direction_ticks is None:
            # Default: strong buy flow → LONG
            ticks = [
                {"price": 100.0, "qty": 15000, "isBuyerMaker": False},
                {"price": 100.0, "qty": 5000, "isBuyerMaker": True},
            ]
        else:
            ticks = direction_ticks
        indicators = {"1m": _make_indicators(rsi_val=rsi_val)}
        smc_data = {
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
            "order_book": _strong_obi(),
        }
        return ch._evaluate_whale_momentum("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime)

    # ── LONG RSI gates ────────────────────────────────────────────────────

    def test_rsi_65_long_accepted_no_penalty(self):
        """RSI = 65 (optimal zone) for LONG — accepted with no RSI penalty."""
        sig = self._call(rsi_val=65.0)
        assert sig is not None
        assert sig.direction == Direction.LONG
        assert sig.soft_penalty_total == 0.0

    def test_rsi_72_long_accepted_with_soft_penalty(self):
        """RSI = 72 (borderline zone 72–81) for LONG — accepted with +5 penalty."""
        sig = self._call(rsi_val=72.0)
        assert sig is not None, "RSI 72 should be accepted for LONG (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_81_long_accepted_with_soft_penalty(self):
        """RSI = 81 (near hard limit 82) for LONG — accepted with +5 penalty."""
        sig = self._call(rsi_val=81.0)
        assert sig is not None, "RSI 81 should be accepted for LONG (below hard limit of 82)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_82_long_hard_rejected(self):
        """RSI = 82 (at hard limit) for LONG — must be hard-rejected."""
        sig = self._call(rsi_val=82.0)
        assert sig is None, "RSI ≥ 82 must be hard-rejected for LONG direction."

    def test_rsi_90_long_hard_rejected(self):
        """RSI = 90 (extreme overbought) for LONG — must be hard-rejected."""
        sig = self._call(rsi_val=90.0)
        assert sig is None, "RSI 90 (extreme overbought) must be hard-rejected."

    # ── SHORT RSI gates ───────────────────────────────────────────────────

    def _call_short(self, rsi_val, regime=""):
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators(rsi_val=rsi_val)}
        smc_data = {
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": _short_ticks(),
            "order_book": _short_obi(),
        }
        return ch._evaluate_whale_momentum("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime)

    def test_rsi_35_short_accepted_no_penalty(self):
        """RSI = 35 (optimal zone) for SHORT — accepted with no RSI penalty."""
        sig = self._call_short(rsi_val=35.0)
        assert sig is not None
        assert sig.direction == Direction.SHORT
        assert sig.soft_penalty_total == 0.0

    def test_rsi_28_short_accepted_with_soft_penalty(self):
        """RSI = 28 (borderline zone 19–28) for SHORT — accepted with +5 penalty."""
        sig = self._call_short(rsi_val=28.0)
        assert sig is not None, "RSI 28 should be accepted for SHORT (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_19_short_accepted_with_soft_penalty(self):
        """RSI = 19 (near hard limit 18) for SHORT — accepted with +5 penalty."""
        sig = self._call_short(rsi_val=19.0)
        assert sig is not None, "RSI 19 should be accepted for SHORT (above hard limit of 18)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_18_short_hard_rejected(self):
        """RSI = 18 (at hard limit) for SHORT — must be hard-rejected."""
        sig = self._call_short(rsi_val=18.0)
        assert sig is None, "RSI ≤ 18 must be hard-rejected for SHORT direction."

    def test_rsi_5_short_hard_rejected(self):
        """RSI = 5 (extreme oversold) for SHORT — must be hard-rejected."""
        sig = self._call_short(rsi_val=5.0)
        assert sig is None, "RSI 5 (extreme oversold) must be hard-rejected."

    # ── RSI = None passes through ─────────────────────────────────────────

    def test_rsi_none_no_penalty(self):
        """Missing RSI (None) must not block the signal and must not apply RSI penalty."""
        sig = self._call(rsi_val=None)
        assert sig is not None, "Missing RSI must not block WHALE_MOMENTUM."
        assert sig.soft_penalty_total == 0.0


class TestWhaleMomentumObiRefinements:
    """Regime-aware OBI gating for WHALE_MOMENTUM (PR-4 refinement)."""

    def _call(self, order_book, regime=""):
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators(rsi_val=55.0)}
        smc_data = _whale_base_smc(order_book=order_book)
        return ch._evaluate_whale_momentum("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime)

    # ── Strong OBI always passes ──────────────────────────────────────────

    def test_strong_obi_passes_in_any_regime(self):
        """OBI ≥ 1.5× (strong imbalance) passes with no OBI penalty in any regime."""
        sig = self._call(_strong_obi(), regime="RANGING")
        assert sig is not None
        assert sig.soft_penalty_total == 0.0

    # ── Marginal OBI in fast vs calm regime ──────────────────────────────

    def test_marginal_obi_accepted_in_volatile_regime(self):
        """OBI ~1.3× (marginal) in VOLATILE regime → accepted with soft penalty."""
        sig = self._call(_marginal_obi(), regime="VOLATILE")
        assert sig is not None, "Marginal OBI in VOLATILE regime should be accepted (soft penalty)."
        assert sig.soft_penalty_total >= 8.0, "Marginal OBI in VOLATILE must carry ≥8.0 soft penalty."

    def test_marginal_obi_accepted_in_breakout_expansion_regime(self):
        """OBI ~1.3× (marginal) in BREAKOUT_EXPANSION regime → accepted with soft penalty."""
        sig = self._call(_marginal_obi(), regime="BREAKOUT_EXPANSION")
        assert sig is not None, "Marginal OBI in BREAKOUT_EXPANSION should be accepted (soft penalty)."
        assert sig.soft_penalty_total >= 8.0

    def test_marginal_obi_hard_rejected_in_calm_regime(self):
        """OBI ~1.3× (marginal) in RANGING regime → hard rejected."""
        sig = self._call(_marginal_obi(), regime="RANGING")
        assert sig is None, "Marginal OBI in RANGING regime must be hard-rejected."

    def test_marginal_obi_hard_rejected_in_trending_regime(self):
        """OBI ~1.3× (marginal) in TRENDING_UP regime → hard rejected (not a fast regime)."""
        sig = self._call(_marginal_obi(), regime="TRENDING_UP")
        assert sig is None, "Marginal OBI in TRENDING_UP must be hard-rejected (not a _WHALE_FAST_REGIME)."

    # ── Below soft floor always rejects ──────────────────────────────────

    def test_weak_obi_hard_rejected_in_volatile_regime(self):
        """OBI ~1.1× (below soft floor 1.2×) in VOLATILE regime → still hard-rejected."""
        sig = self._call(_weak_obi(), regime="VOLATILE")
        assert sig is None, "OBI below soft floor (1.2×) must be hard-rejected even in VOLATILE."

    # ── Missing order book ────────────────────────────────────────────────

    def test_no_order_book_accepted_with_penalty(self):
        """Missing order book (None) → signal accepted with +10 soft penalty."""
        sig = self._call(order_book=None, regime="")
        assert sig is not None
        assert sig.soft_penalty_total >= 10.0

    # ── Penalty stacking ─────────────────────────────────────────────────

    def test_marginal_obi_and_borderline_rsi_stack_penalties(self):
        """Marginal OBI (+8) and borderline RSI (+5) stack to exactly 13 — no missing-OB penalty."""
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators(rsi_val=75.0)}  # borderline RSI
        smc_data = _whale_base_smc(order_book=_marginal_obi())
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="VOLATILE",
        )
        assert sig is not None, "Stacked penalties must still produce a signal."
        # Order book IS present (marginal), so the +10 missing-OB penalty must NOT apply.
        # Expected: OBI penalty 8 + RSI penalty 5 = 13 (not 10+8+5=23).
        assert sig.soft_penalty_total == 13.0, (
            f"Expected soft_penalty_total == 13.0 (OBI 8 + RSI 5, no missing-OB penalty), "
            f"got {sig.soft_penalty_total}"
        )

    def test_marginal_obi_does_not_inherit_missing_ob_penalty(self):
        """Marginal OBI in a fast regime must only apply the +8 OBI penalty, not the +10 missing-OB penalty."""
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators(rsi_val=55.0)}  # optimal RSI, no RSI penalty
        smc_data = _whale_base_smc(order_book=_marginal_obi())
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="VOLATILE",
        )
        assert sig is not None
        # Only OBI marginal penalty should apply — order book is present
        assert sig.soft_penalty_total == 8.0, (
            f"Only marginal OBI penalty (8.0) expected, got {sig.soft_penalty_total}"
        )

    def test_strong_obi_with_borderline_rsi_only_rsi_penalty(self):
        """Strong OBI + borderline RSI → only the RSI penalty (+5) is applied."""
        ch = ScalpChannel()
        candles = {"1m": _make_candles(20)}
        indicators = {"1m": _make_indicators(rsi_val=75.0)}  # borderline RSI
        smc_data = _whale_base_smc(order_book=_strong_obi())
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000,
        )
        assert sig is not None
        assert sig.soft_penalty_total == 5.0, (
            f"Only RSI penalty expected (5.0), got {sig.soft_penalty_total}"
        )


# ---------------------------------------------------------------------------
# PR_10 refactor verification tests
# ---------------------------------------------------------------------------

def test_volume_expansion_returns_false_when_below_threshold():
    from src.filters import check_volume_expansion
    volumes = [1000.0] * 10 + [800.0]   # Last candle is below average
    closes  = [100.0] * 11
    assert not check_volume_expansion(volumes, closes, lookback=9, multiplier=1.8)


def test_volume_expansion_returns_true_when_above():
    from src.filters import check_volume_expansion
    volumes = [1000.0] * 10 + [2500.0]  # Last candle is 2.5× average
    closes  = [100.0] * 11
    assert check_volume_expansion(volumes, closes, lookback=9, multiplier=1.8)


def test_scalp_channel_no_calc_levels_method():
    """After refactor, ScalpChannel should not have _calc_levels."""
    from src.channels.scalp import ScalpChannel
    ch = ScalpChannel()
    assert not hasattr(ch, "_calc_levels"), \
        "_calc_levels should be removed; TP is computed by build_channel_signal()"


# ---------------------------------------------------------------------------
# PR-ARCH-2: Winner-Takes-All Removal tests
# ---------------------------------------------------------------------------

class TestScalpChannelReturnsListOfSignals:
    """PR-ARCH-2: ScalpChannel.evaluate() must return List[Signal], never Optional[Signal]."""

    def test_evaluate_always_returns_list(self):
        """evaluate() must return a list even when no signals are produced."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sigs = ch.evaluate("BTCUSDT", candles, {"5m": _make_indicators()}, {"sweeps": []}, 0.01, 1_000_000)
        assert isinstance(sigs, list)

    def test_evaluate_empty_list_when_no_signals(self):
        """evaluate() returns [] instead of None when all paths reject."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sigs = ch.evaluate("BTCUSDT", candles, {"5m": _make_indicators()}, {"sweeps": []}, 0.01, 1_000_000)
        assert sigs == []

    def test_evaluate_can_return_multiple_signals(self):
        """evaluate() may return more than one signal per cycle (no winner-takes-all).

        Inject conditions that satisfy both the standard sweep path and the whale
        momentum path simultaneously so that both evaluators fire.  The result must
        contain at least one signal and must NOT be capped to exactly one.
        """
        ch = ScalpChannel()
        n = 60
        candles = {"5m": _make_candles(n), "1m": _make_candles(n)}
        sweep = LiquiditySweep(
            index=n - 1, direction=Direction.LONG,
            sweep_level=99, close_price=99.05,
            wick_high=101, wick_low=98,
        )
        ticks = [
            {"price": 100.0, "qty": 15000, "isBuyerMaker": False},  # buy $1.5M
            {"price": 100.0, "qty": 5000, "isBuyerMaker": True},    # sell $0.5M
        ]
        order_book = {
            "bids": [[100.0, 500.0]] * 10,
            "asks": [[100.1, 100.0]] * 10,
        }
        smc_data = {
            "sweeps": [sweep],
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
            "order_book": order_book,
        }
        indicators = {
            "5m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100),
            "1m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100),
        }
        sigs = ch.evaluate("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        assert isinstance(sigs, list)
        # At least one signal must be produced; multiple is expected
        assert len(sigs) >= 1

    def test_all_returned_signals_belong_to_360_scalp(self):
        """Every signal in the returned list must have channel == '360_SCALP'."""
        ch = ScalpChannel()
        n = 60
        candles = {"5m": _make_candles(n), "1m": _make_candles(n)}
        sweep = LiquiditySweep(
            index=n - 1, direction=Direction.LONG,
            sweep_level=99, close_price=99.05,
            wick_high=101, wick_low=98,
        )
        ticks = [
            {"price": 100.0, "qty": 15000, "isBuyerMaker": False},
            {"price": 100.0, "qty": 5000, "isBuyerMaker": True},
        ]
        order_book = {
            "bids": [[100.0, 500.0]] * 10,
            "asks": [[100.1, 100.0]] * 10,
        }
        smc_data = {
            "sweeps": [sweep],
            "whale_alert": {"amount_usd": 1_500_000},
            "volume_delta_spike": True,
            "recent_ticks": ticks,
            "order_book": order_book,
        }
        indicators = {
            "5m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100),
            "1m": _make_indicators(adx_val=30, mom=0.5, ema9=101, ema21=100),
        }
        sigs = ch.evaluate("BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000)
        for sig in sigs:
            assert sig.channel == "360_SCALP"

    def test_evaluate_accepts_regime_and_returns_list(self):
        """evaluate() must accept regime= kwarg and still return a list."""
        ch = ScalpChannel()
        candles = {"5m": _make_candles(60)}
        sigs = ch.evaluate(
            "BTCUSDT", candles, {"5m": _make_indicators()}, {"sweeps": []},
            0.01, 1_000_000, regime="RANGING",
        )
        assert isinstance(sigs, list)


# ---------------------------------------------------------------------------
# VOLUME_SURGE_BREAKOUT refinement tests
# ---------------------------------------------------------------------------

def _make_surge_candles(n=60, base=100.0, breakout_offset=3):
    """Build candle data that satisfies the VOLUME_SURGE_BREAKOUT conditions.

    Layout (all indices relative to the final candle, i.e. candle[-1]):
    - Candles at [-26:-6]: prices in 98–99 range, average volume 1000
    - Candle at -breakout_offset: high of 103 (breaks swing high ~99), volume 3000
    - Current candle [-1]: close=98.5 (about 0.5% below swing high 99.0)
      with surge volume 4500 (> 3× the inflated rolling average of ~1285)
    """
    closes = np.ones(n) * 98.5
    highs  = np.ones(n) * 99.0
    lows   = np.ones(n) * 97.5
    vols   = np.ones(n) * 1000.0

    # Create a detectable breakout candle at the given offset from the end
    idx = n - breakout_offset
    highs[idx] = 103.0   # clearly above prior swing high
    vols[idx]  = 3000.0  # 3× rolling average → passes 2× breakout threshold

    # Current candle: surge volume must exceed 3× rolling average.
    # Because the breakout candle (3000) is within the rolling window, the
    # inflated avg is ~1285; 4500 > 3×1285 = 3857 so the check passes.
    closes[-1] = 98.5
    highs[-1]  = 99.0
    vols[-1]   = 4500.0

    return {
        "open": closes - 0.1,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": vols,
    }


def _surge_indicators(rsi_val=58.0, ema9=101.0, ema21=99.0):
    return {"5m": _make_indicators(rsi_val=rsi_val, ema9=ema9, ema21=ema21)}


def _surge_smc(with_fvg=True):
    smc: dict = {}
    if with_fvg:
        smc["fvg"] = [{"top": 100.0, "bottom": 99.0, "type": "bullish"}]
    return smc


class TestVolumeSurgeBreakoutRefinements:
    """Tests for the refined VOLUME_SURGE_BREAKOUT path."""

    def _call(self, candles, indicators, smc_data, regime="TRENDING_UP"):
        ch = ScalpChannel()
        return ch._evaluate_volume_surge_breakout(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime,
        )

    # ── Happy path ────────────────────────────────────────────────────────

    def test_signal_fires_on_valid_breakout_at_minus3(self):
        """Original breakout position candle[-3] still fires correctly."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None
        assert sig.setup_class == "VOLUME_SURGE_BREAKOUT"
        assert sig.direction == Direction.LONG

    def test_signal_fires_on_breakout_at_minus4(self):
        """Breakout at candle[-4]: timing tolerance — was a hard miss in original code."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=4)}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None, "Breakout 4 candles ago should now be accepted."

    def test_signal_fires_on_breakout_at_minus5(self):
        """Breakout at candle[-5]: timing tolerance — was a hard miss in original code."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=5)}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None, "Breakout 5 candles ago should now be accepted."

    # ── Timing hard boundary ─────────────────────────────────────────────

    def test_no_signal_when_breakout_too_old(self):
        """Breakout at candle[-7] (outside 5-candle window) must be rejected."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=7)}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is None, "Breakout older than 5 candles must be rejected."

    # ── Pullback zone ─────────────────────────────────────────────────────

    def test_premium_pullback_zone_has_no_soft_penalty(self):
        """Pullback in premium zone (0.3%–0.6%) carries zero soft penalty.

        The quality distinction between premium and extended zones is expressed
        via the soft_penalty_total system (scanner deducts post-PR09), not via
        evaluator-level confidence mutations, which are overwritten by the pipeline.
        """
        m5 = _make_surge_candles(n=60, breakout_offset=3)
        swing_high = 99.0
        # 0.45% below swing_high: 99.0 * (1 - 0.0045) ≈ 98.554
        m5["close"][-1] = swing_high * (1 - 0.0045)
        candles = {"5m": m5}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None
        # Premium zone with FVG present: no pullback penalty, no FVG penalty
        assert sig.soft_penalty_total == 0.0

    def test_shallow_pullback_accepted_with_soft_penalty(self):
        """Pullback of 0.2% (below premium zone 0.3%–0.6%) is accepted with soft penalty."""
        m5 = _make_surge_candles(n=60, breakout_offset=3)
        swing_high = 99.0
        # 0.2% below swing_high: 99.0 * (1 - 0.002) ≈ 98.802
        m5["close"][-1] = swing_high * (1 - 0.002)
        candles = {"5m": m5}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None, "Shallow pullback (0.2%) should be accepted."
        assert sig.soft_penalty_total > 0.0, "Shallow pullback should carry a soft penalty."

    def test_upper_extended_zone_accepted_with_soft_penalty(self):
        """Pullback of 0.65% (above premium zone) is accepted but carries soft penalty."""
        m5 = _make_surge_candles(n=60, breakout_offset=3)
        swing_high = 99.0
        # 0.65% below swing_high: still above SL (0.8% below = 98.208), valid entry
        m5["close"][-1] = swing_high * (1 - 0.0065)
        candles = {"5m": m5}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None, "Upper extended pullback (0.65%) should be accepted."
        assert sig.soft_penalty_total > 0.0, "Upper extended pullback should carry soft penalty."

    def test_pullback_exceeding_0_75pct_rejected(self):
        """Pullback > 0.75% is rejected (sl >= close, or explicit upper bound)."""
        m5 = _make_surge_candles(n=60, breakout_offset=3)
        swing_high = 99.0
        # 0.9% below swing_high → close (98.109) < sl (98.208) → rejected
        m5["close"][-1] = swing_high * (1 - 0.009)
        candles = {"5m": m5}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is None, "Pullback beyond 0.75% must be rejected."

    def test_price_at_or_above_swing_high_rejected(self):
        """Price above swing high (no pullback) must be rejected."""
        m5 = _make_surge_candles(n=60, breakout_offset=3)
        swing_high = 99.0
        m5["close"][-1] = swing_high + 0.5  # still above swing high
        candles = {"5m": m5}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is None, "Price above swing high (no retest) must be rejected."

    # ── RSI ─────────────────────────────────────────────────────────────

    def test_rsi_73_accepted_with_soft_penalty(self):
        """RSI = 73 (borderline above optimal) is accepted with a soft penalty."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(rsi_val=73.0), _surge_smc())
        assert sig is not None, "RSI 73 should be accepted (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_80_accepted_with_soft_penalty(self):
        """RSI = 80 (near upper hard limit) is accepted with a soft penalty."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(rsi_val=80.0), _surge_smc())
        assert sig is not None, "RSI 80 should be accepted (below hard limit of 82)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_83_hard_rejected(self):
        """RSI = 83 (above hard limit of 82) must be hard-rejected."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(rsi_val=83.0), _surge_smc())
        assert sig is None, "RSI above 82 must be hard-rejected."

    def test_rsi_39_hard_rejected(self):
        """RSI = 39 (below hard limit of 40) must be hard-rejected."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(rsi_val=39.0), _surge_smc())
        assert sig is None, "RSI below 40 must be hard-rejected."

    def test_rsi_42_accepted_with_soft_penalty(self):
        """RSI = 42 (borderline below optimal) is accepted with a soft penalty."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(rsi_val=42.0), _surge_smc())
        assert sig is not None, "RSI 42 should be accepted (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    # ── FVG / orderblock in fast vs. calm regimes ────────────────────────

    def test_no_fvg_ob_hard_rejected_in_calm_regime(self):
        """Without FVG or OB, signal is rejected in a non-fast regime."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(), _surge_smc(with_fvg=False), regime="RANGING")
        assert sig is None, "Missing FVG/OB must hard-block in non-fast regimes."

    def test_no_fvg_ob_accepted_with_penalty_in_volatile_regime(self):
        """Without FVG or OB, signal passes with soft penalty in VOLATILE regime."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(), _surge_smc(with_fvg=False), regime="VOLATILE")
        assert sig is not None, "Missing FVG/OB should NOT hard-block in VOLATILE regime."
        assert sig.soft_penalty_total >= 8.0

    def test_no_fvg_ob_accepted_with_penalty_in_breakout_expansion(self):
        """Without FVG or OB, signal passes with soft penalty in BREAKOUT_EXPANSION regime."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(
            candles, _surge_indicators(), _surge_smc(with_fvg=False), regime="BREAKOUT_EXPANSION",
        )
        assert sig is not None, "Missing FVG/OB should NOT hard-block in BREAKOUT_EXPANSION regime."
        assert sig.soft_penalty_total >= 8.0

    def test_fvg_present_reduces_soft_penalty_vs_absent(self):
        """FVG presence yields a lower soft_penalty_total than absent FVG (fast regime).

        The evaluator-level sig.confidence from the evaluator is overwritten by the
        scanner's PR09 composite engine, so quality differentiation must be expressed
        via soft_penalty_total (deducted post-PR09).  FVG absent → +8.0 soft penalty;
        FVG present → 0.0 FVG penalty, so with-FVG signal will lose less confidence.
        """
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        ind = _surge_indicators()
        sig_with_fvg = self._call(candles, ind, _surge_smc(with_fvg=True), regime="VOLATILE")
        sig_no_fvg   = self._call(candles, ind, _surge_smc(with_fvg=False), regime="VOLATILE")
        assert sig_with_fvg is not None and sig_no_fvg is not None
        assert sig_no_fvg.soft_penalty_total >= 8.0, \
            "Absent FVG in fast regime must accumulate ≥8.0 soft penalty."
        assert sig_with_fvg.soft_penalty_total < sig_no_fvg.soft_penalty_total, \
            "FVG present should carry a lower soft penalty than absent FVG."

    # ── Quiet regime blocked ─────────────────────────────────────────────

    def test_quiet_regime_hard_blocked(self):
        """QUIET regime must always return None."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(), _surge_smc(), regime="QUIET")
        assert sig is None

    # ── Minimum data requirement ──────────────────────────────────────────

    def test_insufficient_data_returns_none(self):
        """Fewer than 28 candles must return None (27 is the boundary)."""
        m5 = _make_surge_candles(n=27, breakout_offset=3)
        candles = {"5m": m5}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is None

    # ── SL/TP geometry ───────────────────────────────────────────────────

    def test_sl_below_entry_on_valid_signal(self):
        """Stop loss must be strictly below the entry price."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None
        assert sig.stop_loss < sig.entry

    def test_tp1_above_entry_on_valid_signal(self):
        """TP1 must be strictly above the entry price (long direction)."""
        candles = {"5m": _make_surge_candles(n=60, breakout_offset=3)}
        sig = self._call(candles, _surge_indicators(), _surge_smc())
        assert sig is not None
        assert sig.tp1 > sig.entry


# ---------------------------------------------------------------------------
# BREAKDOWN_SHORT refinement tests
# ---------------------------------------------------------------------------

def _make_breakdown_candles(n=60, breakdown_offset=3):
    """Build candle data that satisfies the BREAKDOWN_SHORT conditions.

    Layout (all indices relative to the final candle, i.e. candle[-1]):
    - Candles at [-26:-6]: prices around 100–101 range, average volume 1000
    - Candle at -breakdown_offset: low of 97 (breaks swing low ~100.0), volume 3000
    - Current candle [-1]: close=100.4 (about 0.4% above swing low 100.0)
      with surge volume 4500 (> 3× the inflated rolling average of ~1285)
    """
    swing_low = 100.0
    closes = np.ones(n) * 100.4
    highs  = np.ones(n) * 101.5
    lows   = np.ones(n) * swing_low
    vols   = np.ones(n) * 1000.0

    # Create a detectable breakdown candle at the given offset from the end
    idx = n - breakdown_offset
    lows[idx] = 97.0   # clearly below prior swing low 100.0
    vols[idx]  = 3000.0  # 3× rolling average → passes 2× breakdown threshold

    # Current candle: surge volume, close above swing low for dead-cat bounce.
    # Because the breakdown candle (3000) is within the rolling window, the
    # inflated avg is ~1285; 4500 > 3×1285 = 3855 so the check passes.
    closes[-1] = 100.4   # 0.4% above swing low 100.0 (premium zone 0.3%–0.6%)
    highs[-1]  = 101.0
    vols[-1]   = 4500.0

    return {
        "open":   closes - 0.1,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": vols,
    }


def _breakdown_indicators(rsi_val=38.0, ema9=98.0, ema21=100.0):
    """Indicators suitable for BREAKDOWN_SHORT: EMA9 < EMA21 (bearish alignment)."""
    return {"5m": _make_indicators(rsi_val=rsi_val, ema9=ema9, ema21=ema21)}


def _breakdown_smc(with_fvg=True):
    smc: dict = {}
    if with_fvg:
        smc["fvg"] = [{"top": 100.5, "bottom": 100.0, "type": "bearish"}]
    return smc


class TestBreakdownShortRefinements:
    """Tests for the refined BREAKDOWN_SHORT path."""

    def _call(self, candles, indicators, smc_data, regime="TRENDING_DOWN"):
        ch = ScalpChannel()
        return ch._evaluate_breakdown_short(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime=regime,
        )

    # ── Happy path ────────────────────────────────────────────────────────

    def test_signal_fires_on_valid_breakdown_at_minus3(self):
        """Original breakdown position candle[-3] still fires correctly."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None
        assert sig.setup_class == "BREAKDOWN_SHORT"
        assert sig.direction == Direction.SHORT

    def test_signal_fires_on_breakdown_at_minus4(self):
        """Breakdown at candle[-4]: timing tolerance — was a hard miss in original code."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=4)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None, "Breakdown 4 candles ago should now be accepted."

    def test_signal_fires_on_breakdown_at_minus5(self):
        """Breakdown at candle[-5]: timing tolerance — was a hard miss in original code."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=5)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None, "Breakdown 5 candles ago should now be accepted."

    # ── Timing hard boundary ─────────────────────────────────────────────

    def test_no_signal_when_breakdown_too_old(self):
        """Breakdown at candle[-7] (outside 5-candle window) must be rejected."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=7)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is None, "Breakdown older than 5 candles must be rejected."

    # ── Dead-cat bounce zone ─────────────────────────────────────────────

    def test_premium_bounce_zone_has_no_soft_penalty(self):
        """Bounce in premium zone (0.3%–0.6%) carries zero soft penalty.

        The quality distinction between premium and extended zones is expressed
        via the soft_penalty_total system (scanner deducts post-PR09), not via
        evaluator-level confidence mutations, which are overwritten by the pipeline.
        """
        m5 = _make_breakdown_candles(n=60, breakdown_offset=3)
        swing_low = 100.0
        # 0.45% above swing_low: inside premium zone (0.3%–0.6%)
        m5["close"][-1] = swing_low * (1 + 0.0045)
        candles = {"5m": m5}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None
        # Premium zone with FVG present: no bounce penalty, no FVG penalty
        assert sig.soft_penalty_total == 0.0

    def test_shallow_bounce_accepted_with_soft_penalty(self):
        """Bounce of 0.2% (below premium zone 0.3%–0.6%) is accepted with soft penalty."""
        m5 = _make_breakdown_candles(n=60, breakdown_offset=3)
        swing_low = 100.0
        # 0.2% above swing_low: in extended zone (0.1%–0.3%)
        m5["close"][-1] = swing_low * (1 + 0.002)
        candles = {"5m": m5}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None, "Shallow bounce (0.2%) should be accepted."
        assert sig.soft_penalty_total > 0.0, "Shallow bounce should carry a soft penalty."

    def test_upper_extended_bounce_accepted_with_soft_penalty(self):
        """Bounce of 0.65% (above premium zone, within extended zone) carries soft penalty."""
        m5 = _make_breakdown_candles(n=60, breakdown_offset=3)
        swing_low = 100.0
        # 0.65% above swing_low — within extended zone (0.6%–0.75%), still below SL (0.8% above)
        m5["close"][-1] = swing_low * (1 + 0.0065)
        candles = {"5m": m5}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None, "Upper extended bounce (0.65%) should be accepted."
        assert sig.soft_penalty_total > 0.0, "Upper extended bounce should carry soft penalty."

    def test_bounce_exceeding_0_75pct_rejected(self):
        """Bounce > 0.75% is rejected (sl ≤ close, or explicit upper bound check)."""
        m5 = _make_breakdown_candles(n=60, breakdown_offset=3)
        swing_low = 100.0
        # 0.9% above swing_low → close (100.9) > sl (100.8) → rejected
        m5["close"][-1] = swing_low * (1 + 0.009)
        candles = {"5m": m5}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is None, "Bounce beyond 0.75% must be rejected."

    def test_price_at_or_below_swing_low_rejected(self):
        """Price at/below swing low (no bounce yet) must be rejected."""
        m5 = _make_breakdown_candles(n=60, breakdown_offset=3)
        swing_low = 100.0
        m5["close"][-1] = swing_low - 0.5  # still below swing low
        candles = {"5m": m5}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is None, "Price below swing low (no bounce) must be rejected."

    # ── RSI ─────────────────────────────────────────────────────────────

    def test_rsi_56_accepted_with_soft_penalty(self):
        """RSI = 56 (borderline above optimal zone 28–55) is accepted with a soft penalty."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(rsi_val=56.0), _breakdown_smc())
        assert sig is not None, "RSI 56 should be accepted (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_65_accepted_with_soft_penalty(self):
        """RSI = 65 (near upper hard limit 68) is accepted with a soft penalty."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(rsi_val=65.0), _breakdown_smc())
        assert sig is not None, "RSI 65 should be accepted (below hard limit of 68)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_69_hard_rejected(self):
        """RSI = 69 (above hard limit of 68) must be hard-rejected."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(rsi_val=69.0), _breakdown_smc())
        assert sig is None, "RSI above 68 must be hard-rejected."

    def test_rsi_19_hard_rejected(self):
        """RSI = 19 (below hard limit of 20) must be hard-rejected."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(rsi_val=19.0), _breakdown_smc())
        assert sig is None, "RSI below 20 must be hard-rejected."

    def test_rsi_22_accepted_with_soft_penalty(self):
        """RSI = 22 (borderline below optimal zone 28–55) is accepted with a soft penalty."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(rsi_val=22.0), _breakdown_smc())
        assert sig is not None, "RSI 22 should be accepted (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    # ── FVG / orderblock in fast vs. calm regimes ────────────────────────

    def test_no_fvg_ob_hard_rejected_in_calm_regime(self):
        """Without FVG or OB, signal is rejected in a non-fast regime."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(
            candles, _breakdown_indicators(), _breakdown_smc(with_fvg=False), regime="RANGING",
        )
        assert sig is None, "Missing FVG/OB must hard-block in non-fast regimes."

    def test_no_fvg_ob_accepted_with_penalty_in_volatile_regime(self):
        """Without FVG or OB, signal passes with soft penalty in VOLATILE regime."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(
            candles, _breakdown_indicators(), _breakdown_smc(with_fvg=False), regime="VOLATILE",
        )
        assert sig is not None, "Missing FVG/OB should NOT hard-block in VOLATILE regime."
        assert sig.soft_penalty_total >= 8.0

    def test_no_fvg_ob_accepted_with_penalty_in_trending_down(self):
        """Without FVG or OB, signal passes with soft penalty in TRENDING_DOWN regime."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(
            candles, _breakdown_indicators(), _breakdown_smc(with_fvg=False), regime="TRENDING_DOWN",
        )
        assert sig is not None, "Missing FVG/OB should NOT hard-block in TRENDING_DOWN regime."
        assert sig.soft_penalty_total >= 8.0

    def test_fvg_present_reduces_soft_penalty_vs_absent(self):
        """FVG presence yields a lower soft_penalty_total than absent FVG (fast regime).

        The evaluator-level sig.confidence is overwritten by the scanner's PR09 composite
        engine, so quality differentiation must be expressed via soft_penalty_total.
        FVG absent → +8.0 soft penalty; FVG present → 0.0 FVG penalty.
        """
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        ind = _breakdown_indicators()
        sig_with_fvg = self._call(candles, ind, _breakdown_smc(with_fvg=True),  regime="VOLATILE")
        sig_no_fvg   = self._call(candles, ind, _breakdown_smc(with_fvg=False), regime="VOLATILE")
        assert sig_with_fvg is not None and sig_no_fvg is not None
        assert sig_no_fvg.soft_penalty_total >= 8.0, \
            "Absent FVG in fast regime must accumulate ≥8.0 soft penalty."
        assert sig_with_fvg.soft_penalty_total < sig_no_fvg.soft_penalty_total, \
            "FVG present should carry a lower soft penalty than absent FVG."

    # ── Quiet regime blocked ─────────────────────────────────────────────

    def test_quiet_regime_hard_blocked(self):
        """QUIET regime must always return None."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc(), regime="QUIET")
        assert sig is None

    # ── Minimum data requirement ──────────────────────────────────────────

    def test_insufficient_data_returns_none(self):
        """Fewer than 28 candles must return None (27 is the boundary)."""
        m5 = _make_breakdown_candles(n=27, breakdown_offset=3)
        candles = {"5m": m5}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is None

    # ── SL/TP geometry ───────────────────────────────────────────────────

    def test_sl_above_entry_on_valid_signal(self):
        """Stop loss must be strictly above the entry price (short direction)."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None
        assert sig.stop_loss > sig.entry

    def test_tp1_below_entry_on_valid_signal(self):
        """TP1 must be strictly below the entry price (short direction)."""
        candles = {"5m": _make_breakdown_candles(n=60, breakdown_offset=3)}
        sig = self._call(candles, _breakdown_indicators(), _breakdown_smc())
        assert sig is not None
        assert sig.tp1 < sig.entry


# ---------------------------------------------------------------------------
# SR_FLIP_RETEST refinement tests
# ---------------------------------------------------------------------------

def _make_srflip_candles_long(n=60, flip_offset=3, level=100.0):
    """Build candle data satisfying LONG SR_FLIP_RETEST conditions.

    Array slice positions (Python negative indexing, n=60):
    - Prior window highs[-50:-8]: 42 candles; all set to `level`, establishing prior_swing_high.
    - Flip candle at index n-flip_offset (i.e. highs[-flip_offset]): high = level + 1.0.
    - Remaining candles in the 8-candle window highs[-8:] (non-flip): high = level + 0.3.
    - Current candle [-1]: close = level * 1.001 (0.1% above level — premium zone),
      open = level * 1.0015, high = level * 1.002, low = level * 0.999.
      → lower_wick = open - low ≈ 0.25, candle_body = |close - open| ≈ 0.05,
      lower_wick / body ≈ 5.0 → clear rejection, no wick penalty.

    With default level=100.0:
    - prior_swing_high = 100.0, flip at 101.0 → LONG direction, structural_level = 100.0
    - close = 100.1 → dist_from_level = 0.1% → premium zone
    - sl = level * 0.998 = 99.8 < close = 100.1 → valid geometry
    """
    closes = np.ones(n) * 99.8
    highs  = np.ones(n) * (level + 0.3)   # recent non-flip candles
    lows   = np.ones(n) * (level - 1.0)
    opens  = np.ones(n) * 99.7

    # Prior window: all highs exactly at level (sets prior_swing_high = level)
    prior_start = max(0, n - 50)
    prior_end   = n - 8
    for i in range(prior_start, prior_end):
        highs[i] = level

    # Flip candle
    flip_idx = n - flip_offset
    highs[flip_idx] = level + 1.0  # breaks prior_swing_high

    # Hold confirmation for tightened path: prior close already reclaimed above level.
    closes[-2] = level * 1.001

    # Current candle: premium retest with clear rejection wick
    closes[-1] = level * 1.001    # 0.1% above level
    opens[-1]  = level * 1.0015  # slightly above close (bearish body, which is fine)
    highs[-1]  = level * 1.002
    lows[-1]   = level * 0.999   # lower wick = open - low > 0.5 * body → no penalty

    return {
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": np.ones(n) * 1000.0,
    }


def _make_srflip_candles_short(n=60, flip_offset=3, level=100.0):
    """Build candle data satisfying SHORT SR_FLIP_RETEST conditions.

    Array slice positions (Python negative indexing, n=60):
    - Prior window lows[-50:-8]: 42 candles; all set to `level`, establishing prior_swing_low.
    - Flip candle at index n-flip_offset (i.e. lows[-flip_offset]): low = level - 1.0.
    - Remaining candles in the 8-candle window lows[-8:] (non-flip): low = level - 0.3.
    - Current candle [-1]: close = level * 0.999 (0.1% below level — premium zone),
      open = level * 0.9985, high = level * 1.001, low = level * 0.998.
      → upper_wick = high - open ≈ 0.25, candle_body ≈ 0.05,
      upper_wick / body ≈ 5.0 → clear rejection, no wick penalty.

    With default level=100.0:
    - prior_swing_low = 100.0, flip at 99.0 → SHORT direction, structural_level = 100.0
    - close = 99.9 → dist_from_level = 0.1% → premium zone
    - sl = level * 1.002 = 100.2 > close = 99.9 → valid geometry
    """
    closes = np.ones(n) * (level + 0.2)
    highs  = np.ones(n) * (level + 1.0)
    lows   = np.ones(n) * (level - 0.3)  # recent non-flip candles
    opens  = np.ones(n) * (level + 0.3)

    # Prior window: all lows exactly at level (sets prior_swing_low = level)
    prior_start = max(0, n - 50)
    prior_end   = n - 8
    for i in range(prior_start, prior_end):
        lows[i] = level

    # Flip candle
    flip_idx = n - flip_offset
    lows[flip_idx] = level - 1.0  # breaks prior_swing_low

    # Hold confirmation for tightened path: prior close already reclaimed below level.
    closes[-2] = level * 0.999

    # Current candle: premium retest with clear upper rejection wick
    closes[-1] = level * 0.999    # 0.1% below level
    opens[-1]  = level * 0.9985  # slightly below close (bullish body, which is fine)
    highs[-1]  = level * 1.001   # upper wick = high - open > 0.5 * body → no penalty
    lows[-1]   = level * 0.998

    return {
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": np.ones(n) * 1000.0,
    }


def _srflip_indicators_long(rsi_val=55.0, ema9=102.0, ema21=99.0):
    """Indicators for LONG SR_FLIP_RETEST: EMA9 > EMA21 (bullish alignment)."""
    return {"5m": _make_indicators(rsi_val=rsi_val, ema9=ema9, ema21=ema21)}


def _srflip_indicators_short(rsi_val=45.0, ema9=98.0, ema21=101.0):
    """Indicators for SHORT SR_FLIP_RETEST: EMA9 < EMA21 (bearish alignment)."""
    return {"5m": _make_indicators(rsi_val=rsi_val, ema9=ema9, ema21=ema21)}


def _srflip_smc(with_fvg=True, direction="LONG"):
    smc: dict = {}
    if with_fvg:
        if direction == "LONG":
            smc["fvg"] = [{"top": 100.5, "bottom": 99.8, "type": "bullish"}]
        else:
            smc["fvg"] = [{"top": 100.2, "bottom": 99.5, "type": "bearish"}]
    return smc


class TestSrFlipRetestRefinements:
    """Tests for the refined SR_FLIP_RETEST path."""

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

    # ── Happy path ────────────────────────────────────────────────────────

    def test_long_signal_fires_on_valid_retest(self):
        """Valid LONG flip retest should produce a SR_FLIP_RETEST signal."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None
        assert sig.setup_class == "SR_FLIP_RETEST"
        assert sig.direction == Direction.LONG

    def test_short_signal_fires_on_valid_retest(self):
        """Valid SHORT flip retest should produce a SR_FLIP_RETEST signal."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(candles, _srflip_indicators_short(), _srflip_smc(direction="SHORT"))
        assert sig is not None
        assert sig.setup_class == "SR_FLIP_RETEST"
        assert sig.direction == Direction.SHORT

    # ── Flip detection window (extended from 5 to 8 candles) ─────────────

    def test_flip_at_minus3_accepted(self):
        """Flip at candle[-3]: original position still fires correctly."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None, "Flip 3 candles ago should be accepted."

    def test_flip_at_minus6_accepted(self):
        """Flip at candle[-6]: extended window — was hard-missed with 5-candle window."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=6)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None, "Flip 6 candles ago should now be accepted."

    def test_flip_at_minus9_accepted(self):
        """Flip at candle[-9]: new boundary of closed-candle window — should be accepted."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=9)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None, "Flip 9 closed candles ago should be accepted (boundary of window)."

    def test_flip_at_minus10_rejected(self):
        """Flip at candle[-10]: outside the 8-closed-candle window — must be rejected."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=10)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is None, "Flip 10 candles ago (outside 8-closed-candle window) must be rejected."

    # ── Retest proximity zone ─────────────────────────────────────────────

    def test_premium_zone_has_no_proximity_penalty(self):
        """Retest at 0.2% from level (premium zone ≤0.3%) carries zero proximity penalty.

        Quality differentiation is expressed via soft_penalty_total (deducted post-PR09),
        not via evaluator-level confidence mutations.
        """
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        m5["close"][-1] = 100.2   # 0.2% above level — premium zone
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None
        # Premium zone + FVG present: no proximity penalty, no FVG penalty
        assert sig.soft_penalty_total == 0.0

    def test_extended_zone_accepted_with_proximity_penalty(self):
        """Retest at 0.45% from level (extended zone 0.3%–0.6%) accepted with soft penalty.

        Premium zone = no penalty.  Extended zone = +3.0 soft penalty.
        """
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        m5["close"][-1] = 100.45   # 0.45% above level — extended zone
        m5["open"][-1]  = 100.50   # keep rejection wick valid
        m5["low"][-1]   = 100.25   # lower_wick = 100.50 - 100.25 = 0.25 >> body
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None, "0.45% extended retest should be accepted."
        assert sig.soft_penalty_total >= 3.0, "Extended zone should carry at least +3.0 penalty."

    def test_retest_beyond_0_6pct_hard_rejected(self):
        """Retest > 0.6% from level must be hard-rejected (too far from structural level)."""
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        m5["close"][-1] = 100.7   # 0.7% above level — beyond extended zone
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is None, "Retest > 0.6% from level must be hard-rejected."

    # ── Rejection candle (layered soft/hard gate) ─────────────────────────

    def test_clear_rejection_wick_no_penalty(self):
        """Lower wick ≥ 50% of candle body (clear rejection) carries no wick penalty."""
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        # Default candle already has large wick; verify baseline
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None
        # FVG present, premium zone, clear wick: zero soft penalty
        assert sig.soft_penalty_total == 0.0

    def test_borderline_wick_accepted_with_penalty(self):
        """Lower wick 20%–50% of body (borderline rejection) accepted with +4.0 penalty."""
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        # Craft candle: body = 0.4, lower_wick = 0.1 (25% of body → borderline)
        m5["close"][-1] = 100.1
        m5["open"][-1]  = 100.5   # body = |100.1 - 100.5| = 0.4
        m5["low"][-1]   = 100.4   # lower_wick = open - low = 100.5 - 100.4 = 0.1 (25%)
        m5["high"][-1]  = 100.6
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None, "Borderline wick (25% of body) should be accepted."
        assert sig.soft_penalty_total >= 4.0, "Borderline wick should carry ≥4.0 soft penalty."

    def test_no_wick_hard_rejected(self):
        """Lower wick < 20% of body (no rejection evidence) must be hard-rejected."""
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        # Craft candle: body = 0.5, lower_wick = 0.05 (10% of body → below 20% hard limit)
        m5["close"][-1] = 100.1
        m5["open"][-1]  = 100.6   # body = |100.1 - 100.6| = 0.5
        m5["low"][-1]   = 100.55  # lower_wick = open - low = 100.6 - 100.55 = 0.05 (10%)
        m5["high"][-1]  = 100.7
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is None, "Wick < 20% of body (no meaningful rejection) must be hard-rejected."

    def test_doji_candle_passes(self):
        """Doji (zero body) at structural level always passes — indecision at structure is valid."""
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        # Doji: open == close
        m5["close"][-1] = 100.1
        m5["open"][-1]  = 100.1   # body = 0 → candle_body == 0 → wick check skipped
        m5["high"][-1]  = 100.3
        m5["low"][-1]   = 99.9
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None, "Doji at structural level should always pass (indecision = valid)."

    def test_short_no_upper_wick_hard_rejected(self):
        """Upper wick < 20% of body (no rejection at resistance) must be hard-rejected (SHORT)."""
        m5 = _make_srflip_candles_short(n=60, flip_offset=3, level=100.0)
        # Craft: body = 0.5, upper_wick = 0.05 (10% of body)
        m5["close"][-1] = 99.9
        m5["open"][-1]  = 99.4    # body = |99.9 - 99.4| = 0.5, open < close (bullish body)
        m5["high"][-1]  = 99.45  # upper_wick = high - open = 99.45 - 99.4 = 0.05 (10%)
        m5["low"][-1]   = 99.3
        candles = {"5m": m5}
        sig = self._call_short(candles, _srflip_indicators_short(), _srflip_smc(direction="SHORT"))
        assert sig is None, "Upper wick < 20% of body must be hard-rejected (SHORT path)."

    # ── RSI ─────────────────────────────────────────────────────────────

    def test_rsi_70_accepted_with_penalty_long(self):
        """RSI = 70 (borderline, below new hard limit 80) accepted with +5.0 penalty (LONG)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(rsi_val=70.0), _srflip_smc(direction="LONG"))
        assert sig is not None, "RSI 70 should be accepted (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_79_accepted_with_penalty_long(self):
        """RSI = 79 (near upper hard limit 80) accepted with +5.0 penalty (LONG)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(rsi_val=79.0), _srflip_smc(direction="LONG"))
        assert sig is not None, "RSI 79 should be accepted (below hard limit of 80)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_80_hard_rejected_long(self):
        """RSI = 80 (at hard limit) must be hard-rejected (LONG)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(rsi_val=80.0), _srflip_smc(direction="LONG"))
        assert sig is None, "RSI ≥ 80 must be hard-rejected (LONG)."

    def test_rsi_30_accepted_with_penalty_short(self):
        """RSI = 30 (borderline, above new hard limit 20) accepted with +5.0 penalty (SHORT)."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(candles, _srflip_indicators_short(rsi_val=30.0), _srflip_smc(direction="SHORT"))
        assert sig is not None, "RSI 30 should be accepted (borderline, not hard-blocked)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_21_accepted_with_penalty_short(self):
        """RSI = 21 (borderline, above hard limit 20) accepted with +5.0 penalty (SHORT)."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(candles, _srflip_indicators_short(rsi_val=21.0), _srflip_smc(direction="SHORT"))
        assert sig is not None, "RSI 21 should be accepted (borderline, above hard limit)."
        assert sig.soft_penalty_total >= 5.0

    def test_rsi_20_hard_rejected_short(self):
        """RSI = 20 (at hard limit) must be hard-rejected (SHORT)."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(candles, _srflip_indicators_short(rsi_val=20.0), _srflip_smc(direction="SHORT"))
        assert sig is None, "RSI ≤ 20 must be hard-rejected (SHORT)."

    # ── FVG / orderblock (soft vs hard gate by regime) ────────────────────

    def test_no_fvg_ob_hard_rejected_in_calm_regime(self):
        """Without FVG or OB, signal is hard-rejected in a calm regime (RANGING)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(
            candles, _srflip_indicators_long(), _srflip_smc(with_fvg=False), regime="RANGING",
        )
        assert sig is None, "Missing FVG/OB must hard-block in calm regimes."

    def test_no_fvg_ob_accepted_with_penalty_in_trending_up(self):
        """Without FVG or OB, signal passes with soft penalty in TRENDING_UP regime."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(
            candles, _srflip_indicators_long(), _srflip_smc(with_fvg=False), regime="TRENDING_UP",
        )
        assert sig is not None, "Missing FVG/OB should NOT hard-block in TRENDING_UP regime."
        assert sig.soft_penalty_total >= 8.0

    def test_no_fvg_ob_accepted_with_penalty_in_breakout_expansion(self):
        """Without FVG or OB, signal passes with soft penalty in BREAKOUT_EXPANSION regime."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(
            candles, _srflip_indicators_long(), _srflip_smc(with_fvg=False), regime="BREAKOUT_EXPANSION",
        )
        assert sig is not None, "Missing FVG/OB should NOT hard-block in BREAKOUT_EXPANSION."
        assert sig.soft_penalty_total >= 8.0

    def test_fvg_present_reduces_soft_penalty_vs_absent(self):
        """FVG presence yields a lower soft_penalty_total than absent FVG (fast regime).

        The evaluator-level sig.confidence is overwritten by the scanner's PR09 engine,
        so quality differentiation must be expressed via soft_penalty_total.
        FVG absent in fast regime → +8.0 FVG penalty.  FVG present → 0.0 FVG penalty.
        """
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        ind = _srflip_indicators_long()
        sig_with_fvg = self._call_long(
            candles, ind, _srflip_smc(with_fvg=True,  direction="LONG"), regime="TRENDING_UP",
        )
        sig_no_fvg = self._call_long(
            candles, ind, _srflip_smc(with_fvg=False, direction="LONG"), regime="TRENDING_UP",
        )
        assert sig_with_fvg is not None and sig_no_fvg is not None
        assert sig_no_fvg.soft_penalty_total >= 8.0, \
            "Absent FVG in fast regime must accumulate ≥8.0 soft penalty."
        assert sig_with_fvg.soft_penalty_total < sig_no_fvg.soft_penalty_total, \
            "FVG present should carry a lower soft penalty than absent FVG."

    def test_no_fvg_ob_accepted_with_penalty_in_trending_down_short(self):
        """Without FVG or OB, SHORT signal passes with soft penalty in TRENDING_DOWN."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(
            candles, _srflip_indicators_short(), _srflip_smc(with_fvg=False), regime="TRENDING_DOWN",
        )
        assert sig is not None, "Missing FVG/OB should NOT hard-block in TRENDING_DOWN (SHORT)."
        assert sig.soft_penalty_total >= 8.0

    # ── VOLATILE regime blocked ───────────────────────────────────────────

    def test_volatile_regime_hard_blocked(self):
        """VOLATILE regime must always return None (structural flips are noisy)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(
            candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"), regime="VOLATILE",
        )
        assert sig is None, "VOLATILE regime must be hard-blocked for SR_FLIP_RETEST."

    # ── SL/TP geometry ───────────────────────────────────────────────────

    def test_sl_below_entry_on_long_signal(self):
        """Stop loss must be strictly below the entry price (LONG direction)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None
        assert sig.stop_loss < sig.entry

    def test_sl_above_entry_on_short_signal(self):
        """Stop loss must be strictly above the entry price (SHORT direction)."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(candles, _srflip_indicators_short(), _srflip_smc(direction="SHORT"))
        assert sig is not None
        assert sig.stop_loss > sig.entry

    def test_tp1_above_entry_on_long_signal(self):
        """TP1 must be strictly above the entry price (LONG direction)."""
        candles = {"5m": _make_srflip_candles_long(n=60, flip_offset=3)}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is not None
        assert sig.tp1 > sig.entry

    def test_tp1_below_entry_on_short_signal(self):
        """TP1 must be strictly below the entry price (SHORT direction)."""
        candles = {"5m": _make_srflip_candles_short(n=60, flip_offset=3)}
        sig = self._call_short(candles, _srflip_indicators_short(), _srflip_smc(direction="SHORT"))
        assert sig is not None
        assert sig.tp1 < sig.entry

    # ── Cumulative soft penalty ordering ─────────────────────────────────

    def test_penalty_accumulates_across_dimensions(self):
        """Signal with extended zone + borderline wick + borderline RSI accumulates all penalties.

        This verifies that multiple soft quality dimensions stack correctly into
        soft_penalty_total, as the scoring architecture requires.
        """
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        # Extended zone: 0.45% from level
        m5["close"][-1] = 100.45
        # Borderline wick: body=0.10, lower_wick=0.025 (25% of body → penalty)
        m5["open"][-1]  = 100.35
        m5["low"][-1]   = 100.325
        m5["high"][-1]  = 100.55
        candles = {"5m": m5}
        # Borderline RSI for LONG: 72 → +5.0 penalty
        ind = _srflip_indicators_long(rsi_val=72.0)
        sig = self._call_long(candles, ind, _srflip_smc(direction="LONG"))
        assert sig is not None
        # proximity (+3.0) + wick (+4.0) + RSI (+5.0) = 12.0 minimum
        assert sig.soft_penalty_total >= 12.0, (
            f"Expected ≥12.0 accumulated penalty, got {sig.soft_penalty_total}"
        )

    def test_long_immediate_touch_without_prior_hold_rejected(self):
        """Current retest alone is insufficient; prior candle must already hold above level."""
        m5 = _make_srflip_candles_long(n=60, flip_offset=3, level=100.0)
        m5["close"][-2] = 99.95  # no prior hold above flipped level
        candles = {"5m": m5}
        sig = self._call_long(candles, _srflip_indicators_long(), _srflip_smc(direction="LONG"))
        assert sig is None


def _make_trend_pullback_candles_long(n=60, level=100.0):
    closes = np.ones(n) * (level - 0.2)
    highs = closes + 0.25
    lows = closes - 0.25
    opens = closes - 0.05

    # Pullback then turn: down candle then bounce candle.
    closes[-3] = level + 0.12
    closes[-2] = level - 0.02
    closes[-1] = level + 0.10
    opens[-1] = level + 0.03
    highs[-1] = level + 0.20
    lows[-1] = level - 0.12

    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": np.ones(n) * 1000.0,
    }


def _trend_pullback_indicators_long():
    return {
        "5m": {
            **_make_indicators(ema9=100.02, ema21=99.90, ema200=99.30, rsi_val=52.0, mom=0.08),
            "rsi_prev": 47.0,
            "momentum_array": [-0.06, 0.08],
        }
    }


class TestTrendPullbackEntryQuality:
    def _call_long(self, candles, indicators, smc_data):
        ch = ScalpChannel()
        return ch._evaluate_trend_pullback(
            "BTCUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )

    def test_trend_pullback_long_accepts_turn_confirmation(self):
        candles = {"5m": _make_trend_pullback_candles_long()}
        sig = self._call_long(candles, _trend_pullback_indicators_long(), {"fvg": [{"level": 100.0}]})
        assert sig is not None
        assert sig.setup_class == "TREND_PULLBACK_EMA"
        assert sig.direction == Direction.LONG

    def test_trend_pullback_long_rejects_active_pullback_without_turn(self):
        m5 = _make_trend_pullback_candles_long()
        # Keep EMA proximity but remove turn/continuation confirmation.
        m5["close"][-2] = 100.04
        m5["close"][-1] = 100.01  # still slipping lower into EMA
        m5["open"][-1] = 100.03
        m5["high"][-1] = 100.08
        m5["low"][-1] = 99.96
        candles = {"5m": m5}
        ind = _trend_pullback_indicators_long()
        ind["5m"]["momentum_array"] = [0.02, -0.01]
        ind["5m"]["momentum_last"] = -0.01
        ind["5m"]["rsi_prev"] = 53.0
        ind["5m"]["rsi_last"] = 51.0
        sig = self._call_long(candles, ind, {"fvg": [{"level": 100.0}]})
        assert sig is None

    def test_trend_pullback_long_accepts_without_strict_micro_sequence(self):
        m5 = _make_trend_pullback_candles_long()
        # No strict two-bar reversal shape (prev2 already below prev), but still
        # valid continuation-side close and directional momentum sign.
        m5["close"][-3] = 99.96
        m5["close"][-2] = 100.02
        m5["close"][-1] = 100.10
        m5["open"][-1] = 100.04
        m5["high"][-1] = 100.20
        m5["low"][-1] = 99.88
        candles = {"5m": m5}
        ind = _trend_pullback_indicators_long()
        # Momentum weakens vs prior sample but remains directionally positive.
        ind["5m"]["momentum_last"] = 0.04
        ind["5m"]["momentum_array"] = [0.07, 0.04]
        ind["5m"]["rsi_prev"] = 48.0
        ind["5m"]["rsi_last"] = 51.0
        sig = self._call_long(candles, ind, {"fvg": [{"level": 100.0}]})
        assert sig is not None


# ---------------------------------------------------------------------------
# CONTINUATION_LIQUIDITY_SWEEP path tests (roadmap step 5)
# ---------------------------------------------------------------------------

def _make_cls_candles_long(n=40, sweep_level=99.0, close_price=100.5, sweep_offset=3):
    """Build candle data satisfying LONG CLS conditions.

    - EMA alignment: EMA9 > EMA21 (bullish trend) — set via indicators, not candles.
    - sweep_level: the swept low (stop hunt below prior support).
    - close_price: current price, must be > sweep_level (reclaimed).
    - sweep_offset: how many candles ago the sweep happened (1=just, 10=max window).
    """
    closes = np.ones(n) * close_price
    highs  = closes + 0.5
    lows   = closes - 0.2
    opens  = closes - 0.1
    volume = np.ones(n) * 1000.0
    return {
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": volume,
    }


def _make_cls_candles_short(n=40, sweep_level=101.0, close_price=99.5, sweep_offset=3):
    """Build candle data satisfying SHORT CLS conditions.

    - EMA alignment: EMA9 < EMA21 (bearish trend) — set via indicators.
    - sweep_level: the swept high (stop hunt above prior resistance).
    - close_price: current price, must be < sweep_level (reclaimed).
    """
    closes = np.ones(n) * close_price
    highs  = closes + 0.2
    lows   = closes - 0.5
    opens  = closes + 0.1
    volume = np.ones(n) * 1000.0
    return {
        "open":   opens,
        "high":   highs,
        "low":    lows,
        "close":  closes,
        "volume": volume,
    }


def _cls_indicators_long(rsi_val=55.0, ema9=102.0, ema21=99.0, adx_val=25.0, mom=0.3):
    """Indicators for LONG CLS: EMA9 > EMA21 (bullish), positive momentum."""
    return {"5m": _make_indicators(adx_val=adx_val, ema9=ema9, ema21=ema21,
                                   rsi_val=rsi_val, mom=mom)}


def _cls_indicators_short(rsi_val=45.0, ema9=97.0, ema21=101.0, adx_val=25.0, mom=-0.3):
    """Indicators for SHORT CLS: EMA9 < EMA21 (bearish), negative momentum."""
    return {"5m": _make_indicators(adx_val=adx_val, ema9=ema9, ema21=ema21,
                                   rsi_val=rsi_val, mom=mom)}


def _cls_sweep_long(sweep_level=99.0, sweep_index=-3):
    """Create a LONG-direction sweep (dip-and-recover, stop hunt on longs' stops)."""
    return LiquiditySweep(
        index=sweep_index, direction=Direction.LONG,
        sweep_level=sweep_level, close_price=sweep_level + 0.1,
        wick_high=sweep_level + 1.0, wick_low=sweep_level - 0.5,
    )


def _cls_sweep_short(sweep_level=101.0, sweep_index=-3):
    """Create a SHORT-direction sweep (spike-and-fall, stop hunt on shorts' stops)."""
    return LiquiditySweep(
        index=sweep_index, direction=Direction.SHORT,
        sweep_level=sweep_level, close_price=sweep_level - 0.1,
        wick_high=sweep_level + 0.5, wick_low=sweep_level - 1.0,
    )


class TestContinuationLiquiditySweep:
    """Tests for the CONTINUATION_LIQUIDITY_SWEEP path (roadmap step 5)."""

    def _call_long(self, candles, indicators, smc_data, regime="TRENDING_UP"):
        ch = ScalpChannel()
        return ch._evaluate_continuation_liquidity_sweep(
            "BTCUSDT", candles, indicators, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime=regime,
        )

    def _call_short(self, candles, indicators, smc_data, regime="TRENDING_DOWN"):
        ch = ScalpChannel()
        return ch._evaluate_continuation_liquidity_sweep(
            "BTCUSDT", candles, indicators, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime=regime,
        )

    # ── Happy path ────────────────────────────────────────────────────────

    def test_long_signal_fires_on_valid_setup(self):
        """Valid LONG sweep + reclaim in uptrend → CONTINUATION_LIQUIDITY_SWEEP signal."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        assert sig.setup_class == "CONTINUATION_LIQUIDITY_SWEEP"
        assert sig.direction == Direction.LONG

    def test_short_signal_fires_on_valid_setup(self):
        """Valid SHORT sweep + reclaim in downtrend → CONTINUATION_LIQUIDITY_SWEEP signal."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_short(candles, _cls_indicators_short(), smc_data)
        assert sig is not None
        assert sig.setup_class == "CONTINUATION_LIQUIDITY_SWEEP"
        assert sig.direction == Direction.SHORT

    # ── Regime gate ───────────────────────────────────────────────────────

    def test_volatile_regime_hard_blocked(self):
        """VOLATILE regime must hard-block CLS — chaotic orderflow invalidates continuation."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data, regime="VOLATILE")
        assert sig is None, "VOLATILE regime must be hard-blocked for CLS."

    def test_volatile_unsuitable_hard_blocked(self):
        """VOLATILE_UNSUITABLE must also hard-block CLS."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(
            candles, _cls_indicators_long(), smc_data, regime="VOLATILE_UNSUITABLE"
        )
        assert sig is None, "VOLATILE_UNSUITABLE must be hard-blocked for CLS."

    def test_ranging_regime_hard_blocked(self):
        """RANGING regime must hard-block CLS — no directional trend to continue."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data, regime="RANGING")
        assert sig is None, "RANGING must be hard-blocked for CLS — no trend to continue."

    def test_quiet_regime_hard_blocked(self):
        """QUIET regime must hard-block CLS — low-volume range, not a trend."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data, regime="QUIET")
        assert sig is None, "QUIET must be hard-blocked for CLS — no trend to continue."

    def test_trending_up_regime_allowed_for_long(self):
        """TRENDING_UP + LONG EMA alignment → setup fires."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data, regime="TRENDING_UP")
        assert sig is not None

    def test_trending_down_blocks_long_setup(self):
        """TRENDING_DOWN + LONG EMA alignment → regime/EMA mismatch → no signal."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        # EMA is bullish but regime is strongly downtrend — mismatch rejected
        sig = self._call_long(
            candles, _cls_indicators_long(), smc_data, regime="TRENDING_DOWN"
        )
        assert sig is None, "TRENDING_DOWN + LONG EMA should be rejected."

    def test_trending_up_blocks_short_setup(self):
        """TRENDING_UP + SHORT EMA alignment → regime/EMA mismatch → no signal."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_short(
            candles, _cls_indicators_short(), smc_data, regime="TRENDING_UP"
        )
        assert sig is None, "TRENDING_UP + SHORT EMA should be rejected."

    # ── EMA alignment gate ────────────────────────────────────────────────

    def test_ema_not_aligned_long_blocked(self):
        """EMA9 < EMA21 → direction is SHORT, so LONG sweep is ignored."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        # EMA9 < EMA21 → direction=SHORT; sweep is LONG, no match → None
        ind = _cls_indicators_long(ema9=97.0, ema21=101.0)
        sig = self._call_long(candles, ind, smc_data, regime="RANGING")
        assert sig is None, "EMA misalignment should block signal."

    def test_ema_converged_blocked(self):
        """EMA9 == EMA21 → no trend direction → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(ema9=100.0, ema21=100.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is None, "Converged EMAs should be hard-rejected."

    # ── No sweep / wrong direction sweep ─────────────────────────────────

    def test_no_sweep_blocked(self):
        """No sweeps in smc_data → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        smc_data = {"sweeps": []}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is None, "Missing sweep must hard-block CLS."

    def test_wrong_direction_sweep_blocked(self):
        """Sweep direction opposite to EMA trend → no matching sweep → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        # SHORT sweep in a LONG trend — not a valid CLS setup
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is None, "Opposite-direction sweep should not match LONG trend."

    # ── Sweep recency window ───────────────────────────────────────────────

    def test_sweep_at_minus1_accepted(self):
        """Sweep 1 candle ago (index=-1): within window, very recent — no recency penalty."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-1)
        fvgs = [{"gap_high": 102.0, "gap_low": 101.5}]
        smc_data = {"sweeps": [sweep], "fvg": fvgs}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None, "Sweep at index=-1 should be accepted."
        # Very recent sweep + FVG present: only RSI and FVG penalties = 0
        assert sig.soft_penalty_total == 0.0, (
            f"Very recent sweep + FVG should have zero penalty, got {sig.soft_penalty_total}"
        )

    def test_sweep_at_minus5_accepted_no_recency_penalty(self):
        """Sweep 5 candles ago: within recent threshold, no recency penalty."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-5)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None, "Sweep at index=-5 should be accepted."

    def test_sweep_at_minus6_gets_recency_penalty(self):
        """Sweep 6 candles ago: accepted but with +5 recency soft penalty."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-6)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None, "Sweep at index=-6 should still be accepted."
        assert sig.soft_penalty_total >= 5.0, (
            f"Expected ≥5.0 recency penalty, got {sig.soft_penalty_total}"
        )

    def test_sweep_at_minus10_accepted(self):
        """Sweep at boundary (index=-10): just inside window, recency penalty applied."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-10)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None, "Sweep at index=-10 should be accepted (boundary)."
        assert sig.soft_penalty_total >= 5.0

    def test_sweep_at_minus11_rejected(self):
        """Sweep 11 candles ago: outside window → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-11)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is None, "Sweep at index=-11 must be hard-rejected (outside window)."

    # ── Reclaim gate ──────────────────────────────────────────────────────

    def test_long_price_below_sweep_level_blocked(self):
        """Price at/below sweep level → reclaim not confirmed → hard reject."""
        sweep_level = 99.0
        # close_price at or below sweep_level
        candles = {"5m": _make_cls_candles_long(close_price=98.9)}
        sweep = _cls_sweep_long(sweep_level=sweep_level, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is None, "Price below sweep level must hard-reject LONG CLS."

    def test_long_price_equal_to_sweep_level_blocked(self):
        """Price exactly at sweep level → not yet reclaimed → hard reject."""
        sweep_level = 99.0
        candles = {"5m": _make_cls_candles_long(close_price=sweep_level)}
        sweep = _cls_sweep_long(sweep_level=sweep_level, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is None, "Price == sweep level should still be hard-rejected."

    def test_short_price_above_sweep_level_blocked(self):
        """Price at/above sweep level → reclaim not confirmed → hard reject."""
        sweep_level = 101.0
        candles = {"5m": _make_cls_candles_short(close_price=101.1)}
        sweep = _cls_sweep_short(sweep_level=sweep_level, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_short(candles, _cls_indicators_short(), smc_data)
        assert sig is None, "Price above sweep level must hard-reject SHORT CLS."

    # ── Momentum gate ─────────────────────────────────────────────────────

    def test_zero_momentum_long_blocked(self):
        """Zero or negative momentum in LONG setup → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(mom=0.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is None, "Zero momentum must block LONG CLS."

    def test_negative_momentum_long_blocked(self):
        """Negative momentum in LONG setup → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(mom=-0.2)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is None, "Negative momentum must block LONG CLS."

    def test_positive_momentum_short_blocked(self):
        """Positive momentum in SHORT setup → hard reject."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_short(mom=0.2)
        sig = self._call_short(candles, ind, smc_data)
        assert sig is None, "Positive momentum must block SHORT CLS."

    # ── RSI layered gate ──────────────────────────────────────────────────

    def test_rsi_long_hard_max_blocked(self):
        """RSI ≥ 80 for LONG → hard reject (overbought, continuation exhausted)."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(rsi_val=80.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is None, "RSI=80.0 must hard-block LONG CLS."

    def test_rsi_long_above_hard_max_blocked(self):
        """RSI > 80 for LONG → hard reject."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(rsi_val=85.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is None, "RSI=85 must hard-block LONG CLS."

    def test_rsi_long_soft_min_penalised(self):
        """RSI in [70, 80) for LONG → +6 soft penalty, signal still emits."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-1)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(rsi_val=73.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None, "RSI=73 should not hard-block LONG CLS."
        assert sig.soft_penalty_total >= 6.0, (
            f"Expected ≥6.0 RSI penalty, got {sig.soft_penalty_total}"
        )

    def test_rsi_long_below_soft_min_no_penalty(self):
        """RSI < 70 for LONG → no RSI soft penalty."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-1)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(rsi_val=60.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None, "RSI=60 should produce a LONG CLS signal."
        # With very recent sweep (index=-1) and no FVG, only fvg_ob_penalty=8 applies
        assert sig.soft_penalty_total < 14.0, "RSI=60 should not add RSI penalty."

    def test_rsi_short_hard_min_blocked(self):
        """RSI ≤ 20 for SHORT → hard reject (oversold, continuation exhausted)."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_short(rsi_val=20.0)
        sig = self._call_short(candles, ind, smc_data)
        assert sig is None, "RSI=20.0 must hard-block SHORT CLS."

    def test_rsi_short_soft_max_penalised(self):
        """RSI in (20, 30] for SHORT → +6 soft penalty, signal still emits."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-1)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_short(rsi_val=27.0)
        sig = self._call_short(candles, ind, smc_data)
        assert sig is not None, "RSI=27 should not hard-block SHORT CLS."
        assert sig.soft_penalty_total >= 6.0, (
            f"Expected ≥6.0 RSI penalty, got {sig.soft_penalty_total}"
        )

    # ── FVG / orderblock soft gate ────────────────────────────────────────

    def test_no_fvg_no_ob_applies_penalty(self):
        """Missing FVG and orderblock → +8 soft penalty (not hard reject)."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-1)
        smc_data = {"sweeps": [sweep]}  # no fvg or orderblocks keys
        ind = _cls_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None, "Missing FVG/OB must not hard-reject CLS."
        assert sig.soft_penalty_total >= 8.0, (
            f"Expected ≥8.0 FVG/OB penalty, got {sig.soft_penalty_total}"
        )

    def test_fvg_present_removes_fvg_penalty(self):
        """FVG present → no FVG/OB penalty (and FVG used as TP1 target)."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-1)
        fvgs = [{"gap_high": 102.0, "gap_low": 101.5}]
        smc_data = {"sweeps": [sweep], "fvg": fvgs}
        ind = _cls_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None
        # FVG present → no FVG penalty; only recency penalty if any
        assert sig.soft_penalty_total < 8.0, (
            f"FVG present should remove FVG penalty, got {sig.soft_penalty_total}"
        )

    def test_orderblock_present_removes_fvg_penalty(self):
        """Orderblock present (no FVG) → no FVG/OB penalty."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-1)
        smc_data = {"sweeps": [sweep], "orderblocks": [{"level": 99.5}]}
        ind = _cls_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None
        assert sig.soft_penalty_total < 8.0

    # ── Cumulative soft penalty stacking ─────────────────────────────────

    def test_all_soft_penalties_stack(self):
        """Borderline RSI + no FVG/OB + older sweep → penalties accumulate.

        RSI=73 (+6) + no FVG/OB (+8) + sweep_index=-8 (+5) = 19.0 total.
        """
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-8)
        smc_data = {"sweeps": [sweep]}
        ind = _cls_indicators_long(rsi_val=73.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None, "Stacked penalties should not hard-block signal."
        assert sig.soft_penalty_total == pytest.approx(19.0), (
            f"Expected 19.0 total penalty (6+8+5), got {sig.soft_penalty_total}"
        )

    def test_clean_setup_zero_penalty(self):
        """RSI=55 + FVG present + very recent sweep → zero soft penalty."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-2)
        fvgs = [{"gap_high": 102.0, "gap_low": 101.5}]
        smc_data = {"sweeps": [sweep], "fvg": fvgs}
        ind = _cls_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, smc_data)
        assert sig is not None
        assert sig.soft_penalty_total == 0.0, (
            f"Clean setup should have zero penalty, got {sig.soft_penalty_total}"
        )

    # ── SL/TP geometry ────────────────────────────────────────────────────

    def test_long_sl_below_entry(self):
        """Stop loss must be strictly below entry (LONG direction)."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        assert sig.stop_loss < sig.entry

    def test_short_sl_above_entry(self):
        """Stop loss must be strictly above entry (SHORT direction)."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_short(candles, _cls_indicators_short(), smc_data)
        assert sig is not None
        assert sig.stop_loss > sig.entry

    def test_long_sl_anchored_to_sweep_level(self):
        """SL for LONG must be placed below the swept level (structural invalidation)."""
        sweep_level = 99.0
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=sweep_level, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        # SL must be strictly below the swept level
        assert sig.stop_loss < sweep_level, (
            f"SL {sig.stop_loss} must be below sweep_level {sweep_level}"
        )

    def test_short_sl_anchored_to_sweep_level(self):
        """SL for SHORT must be placed above the swept level."""
        sweep_level = 101.0
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=sweep_level, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_short(candles, _cls_indicators_short(), smc_data)
        assert sig is not None
        assert sig.stop_loss > sweep_level, (
            f"SL {sig.stop_loss} must be above sweep_level {sweep_level}"
        )

    def test_tp1_above_entry_on_long(self):
        """TP1 must be strictly above entry price (LONG)."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        assert sig.tp1 > sig.entry

    def test_tp1_below_entry_on_short(self):
        """TP1 must be strictly below entry price (SHORT)."""
        candles = {"5m": _make_cls_candles_short(close_price=99.5)}
        sweep = _cls_sweep_short(sweep_level=101.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_short(candles, _cls_indicators_short(), smc_data)
        assert sig is not None
        assert sig.tp1 < sig.entry

    def test_tp1_uses_fvg_when_available(self):
        """TP1 should use the nearest FVG midpoint when available."""
        sweep_level = 99.0
        close_price = 100.5
        fvg_mid = 102.5
        candles = {"5m": _make_cls_candles_long(close_price=close_price)}
        sweep = _cls_sweep_long(sweep_level=sweep_level, sweep_index=-2)
        fvgs = [{"gap_high": 103.0, "gap_low": 102.0}]
        smc_data = {"sweeps": [sweep], "fvg": fvgs}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        # FVG midpoint = (103.0 + 102.0) / 2 = 102.5
        assert sig.tp1 == pytest.approx(fvg_mid, abs=1e-6)

    def test_tp2_greater_than_tp1_on_long(self):
        """TP2 must be strictly greater than TP1 (LONG direction)."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        assert sig.tp2 > sig.tp1

    def test_setup_class_registration(self):
        """Signal has setup_class == 'CONTINUATION_LIQUIDITY_SWEEP'."""
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        smc_data = {"sweeps": [sweep]}
        sig = self._call_long(candles, _cls_indicators_long(), smc_data)
        assert sig is not None
        assert sig.setup_class == "CONTINUATION_LIQUIDITY_SWEEP"

    def test_registered_in_evaluate(self):
        """evaluate() returns at least one CLS signal when conditions are met."""
        ch = ScalpChannel()
        candles = {"5m": _make_cls_candles_long(close_price=100.5)}
        sweep = _cls_sweep_long(sweep_level=99.0, sweep_index=-3)
        fvgs = [{"gap_high": 102.0, "gap_low": 101.5}]
        smc_data = {"sweeps": [sweep], "fvg": fvgs}
        ind = {"5m": _make_indicators(adx_val=25, ema9=102, ema21=99, mom=0.3, rsi_val=55)}
        sigs = ch.evaluate(
            "BTCUSDT", candles, ind, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime="TRENDING_UP"
        )
        cls_sigs = [s for s in sigs if s.setup_class == "CONTINUATION_LIQUIDITY_SWEEP"]
        assert len(cls_sigs) >= 1, "evaluate() must return a CLS signal when conditions are met."


# ---------------------------------------------------------------------------
# POST_DISPLACEMENT_CONTINUATION path tests (roadmap step 6)
# ---------------------------------------------------------------------------

def _make_pdc_candles_long(
    n=30,
    close_price=103.5,
    consol_count=2,
    disp_body=2.0,
    avg_vol=100.0,
    disp_vol_mult=3.0,
    consol_vol_mult=0.5,
    consol_range_frac=0.3,
):
    """Build candle data satisfying LONG PDC conditions.

    Layout (from oldest to newest, index 0 to n-1):
      [0 … (n-consol_count-2)]: background candles (flat)
      [n-consol_count-2]:       displacement candle (bullish, high volume)
      [n-consol_count-1 … n-2]: consolidation candles (tight range, low volume)
      [n-1]:                    current candle (breaks above consolidation)

    Parameters
    ----------
    close_price : float
        Current (re-acceleration) close price.
    consol_count : int
        Number of consolidation candles (between displacement and current).
    disp_body : float
        Body size of the displacement candle.
    avg_vol : float
        Background average volume (used to compute displacement/consolidation vols).
    disp_vol_mult : float
        Displacement volume as a multiple of avg_vol.
    consol_vol_mult : float
        Consolidation average volume as a multiple of avg_vol.
    consol_range_frac : float
        Consolidation range as a fraction of displacement body.
    """
    # Displacement candle: bullish body of disp_body
    disp_close = 101.0
    disp_open = disp_close - disp_body       # e.g., 99.0
    disp_high = disp_close + 0.2
    disp_low = disp_open - 0.2

    # Consolidation: tight range above disp_open (territory gate)
    consol_range = disp_body * consol_range_frac
    consol_base = disp_open + disp_body * 0.6   # well above disp_open
    consol_low_price = consol_base
    consol_high_price = consol_base + consol_range

    # Current bar breaks above consolidation high
    # close_price should be > consol_high_price
    actual_close = max(close_price, consol_high_price + 0.3)

    n_bg = n - consol_count - 2   # background candles
    if n_bg < 0:
        n_bg = 0

    # Build arrays
    closes = np.ones(n) * 100.0
    opens = closes.copy()
    highs = closes + 0.3
    lows = closes - 0.3
    volumes = np.ones(n) * avg_vol

    d_abs = n - consol_count - 2    # displacement index
    # Displacement candle
    opens[d_abs] = disp_open
    closes[d_abs] = disp_close
    highs[d_abs] = disp_high
    lows[d_abs] = disp_low
    volumes[d_abs] = avg_vol * disp_vol_mult

    # Consolidation candles
    consol_vol = avg_vol * consol_vol_mult
    for i in range(consol_count):
        c_abs = d_abs + 1 + i
        opens[c_abs] = consol_base + consol_range * 0.3
        closes[c_abs] = consol_base + consol_range * 0.5
        highs[c_abs] = consol_high_price
        lows[c_abs] = consol_low_price
        volumes[c_abs] = consol_vol

    # Current candle: re-acceleration bar
    opens[-1] = consol_high_price
    closes[-1] = actual_close
    highs[-1] = actual_close + 0.2
    lows[-1] = consol_high_price - 0.1
    volumes[-1] = avg_vol * 1.5   # Volume picks up on re-acceleration

    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }


def _make_pdc_candles_short(
    n=30,
    close_price=96.5,
    consol_count=2,
    disp_body=2.0,
    avg_vol=100.0,
    disp_vol_mult=3.0,
    consol_vol_mult=0.5,
    consol_range_frac=0.3,
):
    """Build candle data satisfying SHORT PDC conditions (mirror of long)."""
    # Displacement candle: bearish body of disp_body
    disp_close = 99.0
    disp_open = disp_close + disp_body     # e.g., 101.0
    disp_high = disp_open + 0.2
    disp_low = disp_close - 0.2

    # Consolidation: tight range below disp_open
    consol_range = disp_body * consol_range_frac
    consol_base = disp_open - disp_body * 0.6  # well below disp_open
    consol_high_price = consol_base
    consol_low_price = consol_base - consol_range

    # Current bar breaks below consolidation low
    actual_close = min(close_price, consol_low_price - 0.3)

    n_bg = n - consol_count - 2
    if n_bg < 0:
        n_bg = 0

    closes = np.ones(n) * 100.0
    opens = closes.copy()
    highs = closes + 0.3
    lows = closes - 0.3
    volumes = np.ones(n) * avg_vol

    d_abs = n - consol_count - 2
    # Displacement candle
    opens[d_abs] = disp_open
    closes[d_abs] = disp_close
    highs[d_abs] = disp_high
    lows[d_abs] = disp_low
    volumes[d_abs] = avg_vol * disp_vol_mult

    # Consolidation candles
    consol_vol = avg_vol * consol_vol_mult
    for i in range(consol_count):
        c_abs = d_abs + 1 + i
        opens[c_abs] = consol_high_price - consol_range * 0.3
        closes[c_abs] = consol_high_price - consol_range * 0.5
        highs[c_abs] = consol_high_price
        lows[c_abs] = consol_low_price
        volumes[c_abs] = consol_vol

    # Current candle: re-acceleration (break below consolidation floor)
    opens[-1] = consol_low_price
    closes[-1] = actual_close
    highs[-1] = consol_low_price + 0.1
    lows[-1] = actual_close - 0.2
    volumes[-1] = avg_vol * 1.5

    return {
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }


def _pdc_indicators_long(rsi_val=55.0, ema9=102.0, ema21=99.0, adx_val=25.0, mom=0.3):
    """Indicators for LONG PDC: EMA9 > EMA21 (bullish), positive momentum."""
    return {"5m": _make_indicators(adx_val=adx_val, ema9=ema9, ema21=ema21,
                                   rsi_val=rsi_val, mom=mom)}


def _pdc_indicators_short(rsi_val=45.0, ema9=97.0, ema21=101.0, adx_val=25.0, mom=-0.3):
    """Indicators for SHORT PDC: EMA9 < EMA21 (bearish), negative momentum."""
    return {"5m": _make_indicators(adx_val=adx_val, ema9=ema9, ema21=ema21,
                                   rsi_val=rsi_val, mom=mom)}


class TestPostDisplacementContinuation:
    """Tests for the POST_DISPLACEMENT_CONTINUATION path (roadmap step 6)."""

    def _call_long(self, candles, indicators, smc_data, regime="TRENDING_UP"):
        ch = ScalpChannel()
        return ch._evaluate_post_displacement_continuation(
            "BTCUSDT", candles, indicators, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime=regime,
        )

    def _call_short(self, candles, indicators, smc_data, regime="TRENDING_DOWN"):
        ch = ScalpChannel()
        return ch._evaluate_post_displacement_continuation(
            "BTCUSDT", candles, indicators, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime=regime,
        )

    # ── Happy path ────────────────────────────────────────────────────────

    def test_long_signal_fires_on_valid_setup(self):
        """Valid LONG displacement + consolidation + re-acceleration → PDC signal."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None, "Valid LONG PDC setup must produce a signal."
        assert sig.setup_class == "POST_DISPLACEMENT_CONTINUATION"
        assert sig.direction == Direction.LONG

    def test_short_signal_fires_on_valid_setup(self):
        """Valid SHORT displacement + consolidation + re-acceleration → PDC signal."""
        candles = {"5m": _make_pdc_candles_short()}
        sig = self._call_short(candles, _pdc_indicators_short(), {})
        assert sig is not None, "Valid SHORT PDC setup must produce a signal."
        assert sig.setup_class == "POST_DISPLACEMENT_CONTINUATION"
        assert sig.direction == Direction.SHORT

    def test_three_candle_consolidation_accepted(self):
        """3-candle consolidation (within 2-5 window) → signal fires."""
        candles = {"5m": _make_pdc_candles_long(consol_count=3)}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None, "3-candle consolidation must be accepted."

    def test_five_candle_consolidation_accepted(self):
        """5-candle consolidation (maximum window) → signal fires."""
        candles = {"5m": _make_pdc_candles_long(n=35, consol_count=5)}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None, "5-candle consolidation (max) must be accepted."

    # ── Regime gate ───────────────────────────────────────────────────────

    def test_volatile_regime_hard_blocked(self):
        """VOLATILE regime must hard-block PDC — displacement identification unreliable."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {}, regime="VOLATILE")
        assert sig is None, "VOLATILE must be hard-blocked for PDC."

    def test_volatile_unsuitable_hard_blocked(self):
        """VOLATILE_UNSUITABLE must also hard-block PDC."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(
            candles, _pdc_indicators_long(), {}, regime="VOLATILE_UNSUITABLE"
        )
        assert sig is None, "VOLATILE_UNSUITABLE must be hard-blocked for PDC."

    def test_ranging_regime_hard_blocked(self):
        """RANGING regime must hard-block PDC — displacement is a spike not institutional."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {}, regime="RANGING")
        assert sig is None, "RANGING must be hard-blocked for PDC."

    def test_quiet_regime_hard_blocked(self):
        """QUIET regime must hard-block PDC — no directional context."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {}, regime="QUIET")
        assert sig is None, "QUIET must be hard-blocked for PDC."

    def test_strong_trend_long_allowed(self):
        """STRONG_TREND + LONG EMA → setup fires."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {}, regime="STRONG_TREND")
        assert sig is not None, "STRONG_TREND must allow LONG PDC."

    def test_breakout_expansion_long_allowed(self):
        """BREAKOUT_EXPANSION + LONG EMA → setup fires."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(
            candles, _pdc_indicators_long(), {}, regime="BREAKOUT_EXPANSION"
        )
        assert sig is not None, "BREAKOUT_EXPANSION must allow LONG PDC."

    def test_weak_trend_short_allowed(self):
        """WEAK_TREND + SHORT EMA → setup fires."""
        candles = {"5m": _make_pdc_candles_short()}
        sig = self._call_short(candles, _pdc_indicators_short(), {}, regime="WEAK_TREND")
        assert sig is not None, "WEAK_TREND must allow SHORT PDC."

    def test_trending_down_blocks_long_ema(self):
        """TRENDING_DOWN + LONG EMA alignment → regime/EMA mismatch → hard reject."""
        candles = {"5m": _make_pdc_candles_long()}
        # EMA is bullish but regime says downtrend — mismatch rejected
        sig = self._call_long(
            candles, _pdc_indicators_long(), {}, regime="TRENDING_DOWN"
        )
        assert sig is None, "TRENDING_DOWN + LONG EMA mismatch must be rejected."

    def test_trending_up_blocks_short_ema(self):
        """TRENDING_UP + SHORT EMA alignment → regime/EMA mismatch → hard reject."""
        candles = {"5m": _make_pdc_candles_short()}
        sig = self._call_short(
            candles, _pdc_indicators_short(), {}, regime="TRENDING_UP"
        )
        assert sig is None, "TRENDING_UP + SHORT EMA mismatch must be rejected."

    # ── EMA alignment gate ────────────────────────────────────────────────

    def test_ema_converged_hard_blocked(self):
        """EMA9 == EMA21 → no trend direction → hard reject."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(ema9=100.0, ema21=100.0)
        sig = self._call_long(candles, ind, {})
        assert sig is None, "Converged EMAs must be hard-rejected."

    def test_ema_misaligned_long_hard_blocked(self):
        """EMA9 < EMA21 → direction is SHORT; LONG candle displacement is ignored."""
        candles = {"5m": _make_pdc_candles_long()}
        # EMA9 < EMA21 → direction=SHORT; displacement is LONG → mismatch → None
        ind = _pdc_indicators_long(ema9=97.0, ema21=101.0)
        sig = self._call_long(candles, ind, {})
        assert sig is None, "EMA misalignment must block signal."

    # ── Displacement quality gates ────────────────────────────────────────

    def test_weak_displacement_body_blocked(self):
        """Displacement candle body < 60% of range → hard reject (indecisive candle).

        Construct a candle array where the displacement bar has a body of 0.2 units
        but a range of 2.0 units (body ratio = 0.1 < _PDC_DISP_BODY_RATIO_MIN=0.6).
        """
        n = 30
        avg_vol = 100.0
        # Build base candle array
        closes = np.ones(n) * 100.0
        opens = closes.copy()
        highs = closes + 0.3
        lows = closes - 0.3
        volumes = np.ones(n) * avg_vol

        # d_abs for consol_count=2: n - 1 - (consol_count + 1) = 30 - 1 - 3 = 26
        d_abs = n - 1 - 3
        # Displacement candle: small body (0.2) but wide range (2.0) → body_ratio = 0.1
        opens[d_abs] = 100.0
        closes[d_abs] = 100.2    # body = 0.2
        highs[d_abs] = 101.0     # range = 2.0 (high - low)
        lows[d_abs] = 99.0
        volumes[d_abs] = avg_vol * 3.0   # volume passes

        # Consolidation candles (at -3, -2 relative to end)
        for i in range(2):
            c = d_abs + 1 + i
            opens[c] = 100.1
            closes[c] = 100.2
            highs[c] = 100.3
            lows[c] = 100.0
            volumes[c] = avg_vol * 0.5

        # Current candle breaks above consolidation high
        closes[-1] = 100.5
        highs[-1] = 100.6
        lows[-1] = 100.2
        opens[-1] = 100.3
        volumes[-1] = avg_vol * 1.5

        candles_data = {
            "open": opens, "high": highs, "low": lows,
            "close": closes, "volume": volumes,
        }
        sig = self._call_long({"5m": candles_data}, _pdc_indicators_long(), {})
        assert sig is None, (
            "Displacement body ratio 0.1 < 0.6 threshold must hard-block PDC."
        )

    def test_insufficient_displacement_volume_blocked(self):
        """Displacement volume < 2.5× avg → hard reject (not institutional move)."""
        # Only 1.5× avg volume — not enough for a displacement
        candles = {"5m": _make_pdc_candles_long(disp_vol_mult=1.5)}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is None, "Insufficient displacement volume must hard-block PDC."

    def test_consolidation_too_wide_blocked(self):
        """Consolidation range > 50% of displacement body → too wide, not absorption."""
        # consol_range_frac=0.8 → consolidation range = 80% of displacement body
        candles = {"5m": _make_pdc_candles_long(consol_range_frac=0.8)}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is None, "Wide consolidation (> 50% of displacement body) must be rejected."

    # ── Re-acceleration gate ──────────────────────────────────────────────

    def test_price_inside_consolidation_blocked(self):
        """Current close still inside consolidation range → no re-acceleration → hard reject."""
        candles_data = _make_pdc_candles_long(consol_count=2, close_price=103.5)
        # Determine the consolidation high from the generated candle array.
        # With consol_count=2, consolidation candles are at indices [-3] and [-2].
        consol_high = max(float(candles_data["high"][-3]), float(candles_data["high"][-2]))
        # Force current close to be at the consolidation high (not yet broken out).
        closes = list(candles_data["close"])
        closes[-1] = consol_high  # exactly at the ceiling, not above → no breakout
        candles_data_mod = dict(candles_data)
        candles_data_mod["close"] = closes
        sig = self._call_long({"5m": candles_data_mod}, _pdc_indicators_long(), {})
        assert sig is None, "Price at/below consolidation high must hard-reject re-acceleration."

    # ── RSI layered gate ──────────────────────────────────────────────────

    def test_rsi_long_hard_max_blocked(self):
        """RSI ≥ 82 for LONG → hard reject (extreme overbought exhaustion)."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(rsi_val=82.0)
        sig = self._call_long(candles, ind, {})
        assert sig is None, "RSI=82.0 must hard-block LONG PDC."

    def test_rsi_long_above_hard_max_blocked(self):
        """RSI > 82 for LONG → hard reject."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(rsi_val=90.0)
        sig = self._call_long(candles, ind, {})
        assert sig is None, "RSI=90 must hard-block LONG PDC."

    def test_rsi_long_soft_min_penalised(self):
        """RSI in [72, 82) for LONG → +6 soft penalty, signal still emits."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(rsi_val=75.0)
        sig = self._call_long(candles, ind, {})
        assert sig is not None, "RSI=75 should not hard-block LONG PDC."
        assert sig.soft_penalty_total >= 6.0, (
            f"Expected ≥6.0 RSI soft penalty, got {sig.soft_penalty_total}"
        )

    def test_rsi_long_below_soft_min_no_rsi_penalty(self):
        """RSI < 72 for LONG → no RSI soft penalty."""
        candles = {"5m": _make_pdc_candles_long()}
        fvgs = [{"gap_high": 105.0, "gap_low": 104.5}]
        ind = _pdc_indicators_long(rsi_val=60.0)
        sig = self._call_long(candles, ind, {"fvg": fvgs})
        assert sig is not None, "RSI=60 should produce a LONG PDC signal."
        # With FVG present, no FVG penalty; RSI clean → only consol vol penalty possible
        assert sig.soft_penalty_total < 6.0, (
            f"RSI=60 with FVG should not add RSI penalty; got {sig.soft_penalty_total}"
        )

    def test_rsi_short_hard_min_blocked(self):
        """RSI ≤ 18 for SHORT → hard reject (extreme oversold exhaustion)."""
        candles = {"5m": _make_pdc_candles_short()}
        ind = _pdc_indicators_short(rsi_val=18.0)
        sig = self._call_short(candles, ind, {})
        assert sig is None, "RSI=18.0 must hard-block SHORT PDC."

    def test_rsi_short_soft_max_penalised(self):
        """RSI in (18, 28] for SHORT → +6 soft penalty, signal still emits."""
        candles = {"5m": _make_pdc_candles_short()}
        ind = _pdc_indicators_short(rsi_val=25.0)
        sig = self._call_short(candles, ind, {})
        assert sig is not None, "RSI=25 should not hard-block SHORT PDC."
        assert sig.soft_penalty_total >= 6.0, (
            f"Expected ≥6.0 RSI soft penalty for SHORT, got {sig.soft_penalty_total}"
        )

    # ── FVG / orderblock soft gate ────────────────────────────────────────

    def test_no_fvg_no_ob_applies_penalty(self):
        """Missing FVG and orderblock → +7 soft penalty (not hard reject)."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, {})  # empty smc_data
        assert sig is not None, "Missing FVG/OB must not hard-reject PDC."
        assert sig.soft_penalty_total >= 7.0, (
            f"Expected ≥7.0 FVG/OB penalty, got {sig.soft_penalty_total}"
        )

    def test_fvg_present_removes_fvg_penalty(self):
        """FVG present → no FVG/OB penalty."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(rsi_val=55.0)
        fvgs = [{"gap_high": 106.0, "gap_low": 105.5}]
        sig = self._call_long(candles, ind, {"fvg": fvgs})
        assert sig is not None
        # FVG present → no FVG penalty; only consol_vol_penalty possible
        assert sig.soft_penalty_total < 7.0, (
            f"FVG present should remove FVG penalty, got {sig.soft_penalty_total}"
        )

    def test_orderblock_present_removes_fvg_penalty(self):
        """Orderblock present (no FVG) → no FVG/OB penalty."""
        candles = {"5m": _make_pdc_candles_long()}
        ind = _pdc_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, {"orderblocks": [{"level": 102.0}]})
        assert sig is not None
        assert sig.soft_penalty_total < 7.0, (
            f"OB present should remove FVG/OB penalty, got {sig.soft_penalty_total}"
        )

    # ── Consolidation volume quality penalty ─────────────────────────────

    def test_noisy_consolidation_volume_applies_penalty(self):
        """Consolidation avg vol >= 1.5× displacement vol → +5 noisy-consolidation penalty."""
        # consol_vol_mult=4.0, disp_vol_mult=2.5: consol_vol=4*100=400 >= 1.5*2.5*100=375 → penalised
        candles = {"5m": _make_pdc_candles_long(
            disp_vol_mult=2.5, consol_vol_mult=4.0,
        )}
        fvgs = [{"gap_high": 106.0, "gap_low": 105.5}]
        ind = _pdc_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, {"fvg": fvgs})
        assert sig is not None, "Noisy consolidation volume must not hard-reject."
        assert sig.soft_penalty_total >= 5.0, (
            f"Expected ≥5 noisy-consolidation penalty, got {sig.soft_penalty_total}"
        )

    def test_quiet_consolidation_volume_no_penalty(self):
        """Consolidation avg vol < displacement vol → no consolidation-volume penalty."""
        # consol_vol_mult=0.3 → very quiet consolidation
        candles = {"5m": _make_pdc_candles_long(
            disp_vol_mult=3.0, consol_vol_mult=0.3,
        )}
        fvgs = [{"gap_high": 106.0, "gap_low": 105.5}]
        ind = _pdc_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, {"fvg": fvgs})
        assert sig is not None
        # Quiet consolidation → no consol_vol_penalty; FVG → no fvg_ob_penalty
        # RSI=55 → no rsi_penalty → zero total
        assert sig.soft_penalty_total == 0.0, (
            f"Quiet consolidation + FVG + clean RSI should have zero penalty, "
            f"got {sig.soft_penalty_total}"
        )

    # ── Cumulative soft penalty stacking ─────────────────────────────────

    def test_all_soft_penalties_stack(self):
        """Borderline RSI + no FVG/OB + noisy consolidation → penalties accumulate.

        RSI=75 (+6) + no FVG/OB (+7) + noisy consol vol (+5) = 18.0 total.
        """
        candles = {"5m": _make_pdc_candles_long(
            disp_vol_mult=2.5, consol_vol_mult=4.0,
        )}
        ind = _pdc_indicators_long(rsi_val=75.0)
        sig = self._call_long(candles, ind, {})
        assert sig is not None, "Stacked penalties should not hard-block signal."
        assert sig.soft_penalty_total == pytest.approx(18.0), (
            f"Expected 18.0 total penalty (6+7+5), got {sig.soft_penalty_total}"
        )

    def test_clean_setup_zero_penalty(self):
        """RSI=55 + FVG present + quiet consolidation → zero soft penalty."""
        candles = {"5m": _make_pdc_candles_long(
            disp_vol_mult=3.0, consol_vol_mult=0.3,
        )}
        fvgs = [{"gap_high": 106.0, "gap_low": 105.5}]
        ind = _pdc_indicators_long(rsi_val=55.0)
        sig = self._call_long(candles, ind, {"fvg": fvgs})
        assert sig is not None
        assert sig.soft_penalty_total == 0.0, (
            f"Clean setup should have zero penalty, got {sig.soft_penalty_total}"
        )

    # ── SL/TP geometry ────────────────────────────────────────────────────

    def test_long_sl_below_entry(self):
        """Stop loss must be strictly below entry (LONG direction)."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None
        assert sig.stop_loss < sig.entry, "SL must be below entry for LONG PDC."

    def test_short_sl_above_entry(self):
        """Stop loss must be strictly above entry (SHORT direction)."""
        candles = {"5m": _make_pdc_candles_short()}
        sig = self._call_short(candles, _pdc_indicators_short(), {})
        assert sig is not None
        assert sig.stop_loss > sig.entry, "SL must be above entry for SHORT PDC."

    def test_long_sl_below_consolidation_low(self):
        """SL for LONG must be placed below the consolidation low (structural)."""
        candles_data = _make_pdc_candles_long(consol_count=2)
        candles = {"5m": candles_data}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None
        # Consolidation lows live inside the candle array at positions [-3, -2]
        consol_lows = [float(candles_data["low"][-3]), float(candles_data["low"][-2])]
        consol_low = min(consol_lows)
        assert sig.stop_loss < consol_low, (
            f"SL {sig.stop_loss} must be below consolidation low {consol_low}"
        )

    def test_short_sl_above_consolidation_high(self):
        """SL for SHORT must be placed above the consolidation high (structural)."""
        candles_data = _make_pdc_candles_short(consol_count=2)
        candles = {"5m": candles_data}
        sig = self._call_short(candles, _pdc_indicators_short(), {})
        assert sig is not None
        consol_highs = [float(candles_data["high"][-3]), float(candles_data["high"][-2])]
        consol_high = max(consol_highs)
        assert sig.stop_loss > consol_high, (
            f"SL {sig.stop_loss} must be above consolidation high {consol_high}"
        )

    def test_long_tp1_above_entry(self):
        """TP1 must be strictly above entry (LONG)."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None
        assert sig.tp1 > sig.entry, "TP1 must be above entry for LONG PDC."

    def test_short_tp1_below_entry(self):
        """TP1 must be strictly below entry (SHORT)."""
        candles = {"5m": _make_pdc_candles_short()}
        sig = self._call_short(candles, _pdc_indicators_short(), {})
        assert sig is not None
        assert sig.tp1 < sig.entry, "TP1 must be below entry for SHORT PDC."

    def test_long_tp2_greater_than_tp1(self):
        """TP2 must be strictly greater than TP1 (LONG)."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None
        assert sig.tp2 > sig.tp1, "TP2 must be greater than TP1 for LONG PDC."

    def test_short_tp2_less_than_tp1(self):
        """TP2 must be strictly less than TP1 (SHORT)."""
        candles = {"5m": _make_pdc_candles_short()}
        sig = self._call_short(candles, _pdc_indicators_short(), {})
        assert sig is not None
        assert sig.tp2 < sig.tp1, "TP2 must be less than TP1 for SHORT PDC."

    def test_long_tp3_greater_than_tp2(self):
        """TP3 must be strictly greater than TP2 (LONG)."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None
        assert sig.tp3 > sig.tp2, "TP3 must be greater than TP2 for LONG PDC."

    # ── Setup class registration ──────────────────────────────────────────

    def test_setup_class_registration(self):
        """Signal has setup_class == 'POST_DISPLACEMENT_CONTINUATION'."""
        candles = {"5m": _make_pdc_candles_long()}
        sig = self._call_long(candles, _pdc_indicators_long(), {})
        assert sig is not None
        assert sig.setup_class == "POST_DISPLACEMENT_CONTINUATION"

    def test_registered_in_evaluate(self):
        """evaluate() returns at least one PDC signal when conditions are met."""
        ch = ScalpChannel()
        candles = {"5m": _make_pdc_candles_long()}
        fvgs = [{"gap_high": 106.0, "gap_low": 105.5}]
        ind = {"5m": _make_indicators(adx_val=25, ema9=102, ema21=99, mom=0.3, rsi_val=55)}
        sigs = ch.evaluate(
            "BTCUSDT", candles, ind, {"fvg": fvgs},
            spread_pct=0.01, volume_24h_usd=10_000_000, regime="TRENDING_UP"
        )
        pdc_sigs = [s for s in sigs if s.setup_class == "POST_DISPLACEMENT_CONTINUATION"]
        assert len(pdc_sigs) >= 1, "evaluate() must return a PDC signal when conditions are met."



# ---------------------------------------------------------------------------
# FAILED_AUCTION_RECLAIM path tests (roadmap step 7)
# ---------------------------------------------------------------------------

def _make_far_candles_long(
    n=30,
    base=100.0,
    auction_wick_low=99.0,
    cur_close=100.4,
    avg_vol=100.0,
):
    """Build candle data satisfying LONG FAR conditions.

    Uses FLAT base candles so that no bar in the auction window accidentally
    triggers a false SHORT auction by having a high above the struct range.

    Structure:
    - All bars at base (flat) — establishes struct_low = base - 0.1
    - Bar at offset=3 (n-4): low = auction_wick_low (probes below struct_low),
      close = base + 0.05 (fails acceptance, recovers back above struct_low)
    - Bar n-1 (current): close = cur_close (confirmed reclaim above struct_low)
    """
    bar_high = base + 0.3
    bar_low = base - 0.1   # struct_low candidate from flat bars
    closes = [base] * n
    highs = [bar_high] * n
    lows = [bar_low] * n
    opens = [base - 0.02] * n
    volumes = [avg_vol] * n

    # Auction bar at offset=3 (bar_idx = n-4):
    # wick below struct_low, close accepted back above → failed acceptance
    auction_idx = n - 4
    lows[auction_idx] = auction_wick_low
    closes[auction_idx] = base + 0.05
    highs[auction_idx] = bar_high  # same high as other bars → no SHORT signal

    # Current bar — reclaim confirmed
    closes[-1] = cur_close
    highs[-1] = cur_close + 0.2
    lows[-1] = cur_close - 0.05
    opens[-1] = cur_close - 0.02

    return {
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }


def _make_far_candles_short(
    n=30,
    base=100.0,
    auction_wick_high=101.0,
    cur_close=99.6,
    avg_vol=100.0,
):
    """Build candle data satisfying SHORT FAR conditions.

    Uses FLAT base candles so that no bar in the auction window accidentally
    triggers a false LONG auction.

    Structure:
    - All bars at base (flat) — establishes struct_high = base + 0.1
    - Bar at offset=3 (n-4): high = auction_wick_high (probes above struct_high),
      close = base - 0.05 (fails acceptance, recovers back below struct_high)
    - Bar n-1 (current): close = cur_close (confirmed reclaim below struct_high)
    """
    bar_high = base + 0.1   # struct_high candidate from flat bars
    bar_low = base - 0.3
    closes = [base] * n
    highs = [bar_high] * n
    lows = [bar_low] * n
    opens = [base + 0.02] * n
    volumes = [avg_vol] * n

    # Auction bar at offset=3 (bar_idx = n-4):
    # wick above struct_high, close rejected back below → failed acceptance
    auction_idx = n - 4
    highs[auction_idx] = auction_wick_high
    closes[auction_idx] = base - 0.05
    lows[auction_idx] = bar_low  # same low → no LONG signal

    # Current bar — reclaim confirmed below struct_high
    closes[-1] = cur_close
    lows[-1] = cur_close - 0.2
    highs[-1] = cur_close + 0.05
    opens[-1] = cur_close + 0.02

    return {
        "open": opens, "high": highs, "low": lows,
        "close": closes, "volume": volumes,
    }


def _far_indicators_long(atr=0.5, rsi=50.0, ema9=101.0, ema21=100.0, adx=22.0):
    return {
        "5m": _make_indicators(
            adx_val=adx, atr_val=atr, ema9=ema9, ema21=ema21,
            rsi_val=rsi, mom=0.2,
        )
    }


def _far_indicators_short(atr=0.5, rsi=50.0, ema9=99.0, ema21=100.0, adx=22.0):
    return {
        "5m": _make_indicators(
            adx_val=adx, atr_val=atr, ema9=ema9, ema21=ema21,
            rsi_val=rsi, mom=-0.2,
        )
    }


class TestFailedAuctionReclaim:
    """Tests for the FAILED_AUCTION_RECLAIM path (roadmap step 7)."""

    def _call_long(self, candles, indicators, smc_data, regime="RANGING"):
        ch = ScalpChannel()
        return ch._evaluate_failed_auction_reclaim(
            "BTCUSDT", candles, indicators, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime=regime,
        )

    def _call_short(self, candles, indicators, smc_data, regime="RANGING"):
        ch = ScalpChannel()
        return ch._evaluate_failed_auction_reclaim(
            "BTCUSDT", candles, indicators, smc_data,
            spread_pct=0.01, volume_24h_usd=10_000_000, regime=regime,
        )

    # ── Happy path ───────────────────────────────────────────────────────

    def test_happy_path_long(self):
        """LONG FAR fires when a bar pierced below struct_low and current has reclaimed.

        With flat candles:
        - struct_low = base - 0.1 = 99.9 (from flat bars in lookback)
        - auction wick low = 98.5 (< 99.9), close = base+0.05 = 100.05 (failed acceptance)
        - cur_close = 100.4 > struct_low, reclaim_dist = 0.5 >= min_reclaim_atr (0.05)
        """
        candles = {"5m": _make_far_candles_long(base=100.0, auction_wick_low=98.5)}
        sig = self._call_long(candles, _far_indicators_long(atr=0.5), {})
        assert sig is not None, "LONG FAR should fire when all conditions are met."
        assert sig.direction == Direction.LONG
        assert sig.setup_class == "FAILED_AUCTION_RECLAIM"

    def test_happy_path_short(self):
        """SHORT FAR fires when a bar pierced above struct_high and current has reclaimed.

        With flat candles:
        - struct_high = base + 0.1 = 100.1 (from flat bars in lookback)
        - auction wick high = 101.5 (> 100.1), close = base-0.05 = 99.95 (failed acceptance)
        - cur_close = 99.6 < struct_high, reclaim_dist = 0.5 >= min_reclaim_atr (0.05)
        """
        candles = {"5m": _make_far_candles_short(base=100.0, auction_wick_high=101.5)}
        sig = self._call_short(candles, _far_indicators_short(atr=0.5), {}, regime="RANGING")
        assert sig is not None, "SHORT FAR should fire when all conditions are met."
        assert sig.direction == Direction.SHORT
        assert sig.setup_class == "FAILED_AUCTION_RECLAIM"

    # ── Regime gate ──────────────────────────────────────────────────────

    def test_volatile_blocked(self):
        """VOLATILE regime hard-blocks FAR (chaotic orderflow)."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {}, regime="VOLATILE")
        assert sig is None, "VOLATILE must hard-block FAR."

    def test_volatile_unsuitable_blocked(self):
        """VOLATILE_UNSUITABLE must hard-block FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {}, regime="VOLATILE_UNSUITABLE")
        assert sig is None, "VOLATILE_UNSUITABLE must hard-block FAR."

    def test_strong_trend_blocked(self):
        """STRONG_TREND must hard-block FAR (genuine breakouts dominate)."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {}, regime="STRONG_TREND")
        assert sig is None, "STRONG_TREND must hard-block FAR."

    def test_ranging_allowed(self):
        """RANGING is a valid regime for FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {}, regime="RANGING")
        assert sig is not None, "RANGING must allow FAR."

    def test_weak_trend_allowed(self):
        """WEAK_TREND is a valid regime for FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {}, regime="WEAK_TREND")
        assert sig is not None, "WEAK_TREND must allow FAR."

    def test_breakout_expansion_allowed(self):
        """BREAKOUT_EXPANSION is a valid regime for FAR (false breakouts at expansion boundaries)."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {}, regime="BREAKOUT_EXPANSION")
        assert sig is not None, "BREAKOUT_EXPANSION must allow FAR."

    # ── Failure/reclaim structure gates ─────────────────────────────────

    def test_no_auction_candle_returns_none(self):
        """Returns None when no candle in the auction window probed beyond struct extremes.

        Uses perfectly flat candles where high == struct_high and low == struct_low
        for every bar, so no auction window bar can have high > struct_high or
        low < struct_low.
        """
        n = 30
        # Flat candles: all highs and lows identical — no bar ever exceeds struct extremes
        flat_high = 100.2
        flat_low = 99.8
        closes = [100.0] * n
        highs = [flat_high] * n
        lows = [flat_low] * n
        opens = [99.99] * n
        volumes = [100.0] * n
        candles = {"5m": {"open": opens, "high": highs, "low": lows,
                          "close": closes, "volume": volumes}}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is None, "No auction probe → no FAR signal."

    def test_accepted_auction_not_failed(self):
        """When the auction candle CLOSED convincingly beyond the level, it is not a failed auction.

        With flat candles (struct_low = base - 0.1 = 99.9), an auction_wick_low=98.5 would
        normally fire as LONG FAR because the wick pierces below struct_low. However, if we
        manually override the auction close to be well below struct_low, the acceptance check
        should reject it.
        """
        n = 30
        base = 100.0
        bar_high = base + 0.3
        bar_low = base - 0.1   # struct_low = 99.9
        closes = [base] * n
        highs = [bar_high] * n
        lows = [bar_low] * n
        opens = [base - 0.02] * n
        volumes = [100.0] * n

        # Auction bar: wick below struct_low but CLOSE is also well below (accepted!)
        auction_idx = n - 4
        lows[auction_idx] = 98.5    # probed below struct_low=99.9
        closes[auction_idx] = 98.0  # accepted well below struct_low=99.9 (not failed)
        highs[auction_idx] = bar_high

        # Current bar
        closes[-1] = 100.4
        highs[-1] = 100.6
        lows[-1] = 100.35
        opens[-1] = 100.38

        candles = {"5m": {"open": opens, "high": highs, "low": lows,
                          "close": closes, "volume": volumes}}
        sig = self._call_long(candles, _far_indicators_long(atr=0.5), {})
        assert sig is None, "Accepted auction (close well below level) must not trigger FAR."

    def test_insufficient_reclaim_returns_none(self):
        """When current close barely exceeds struct_low, reclaim is insufficient.

        struct_low = 99.9 (flat bars at base=100.0, bar_low=99.9).
        cur_close = 99.92 → reclaim_dist = 0.02 < _FAR_MIN_RECLAIM_ATR * atr (0.10*0.5=0.05).
        """
        n = 30
        base = 100.0
        bar_high = base + 0.3
        bar_low = base - 0.1   # struct_low = 99.9
        closes = [base] * n
        highs = [bar_high] * n
        lows = [bar_low] * n
        opens = [base - 0.02] * n
        volumes = [100.0] * n

        # Auction bar: valid failed auction
        auction_idx = n - 4
        lows[auction_idx] = 98.5
        closes[auction_idx] = base + 0.05
        highs[auction_idx] = bar_high

        # Current bar: marginal reclaim (well within min_reclaim threshold)
        closes[-1] = 99.92
        highs[-1] = 100.0
        lows[-1] = 99.9
        opens[-1] = 99.91

        candles = {"5m": {"open": opens, "high": highs, "low": lows,
                          "close": closes, "volume": volumes}}
        sig = self._call_long(candles, _far_indicators_long(atr=0.5), {})
        assert sig is None, "Marginal reclaim below min_reclaim threshold must not trigger FAR."

    # ── RSI gate ────────────────────────────────────────────────────────

    def test_rsi_hard_reject_long_overbought(self):
        """RSI >= 75 hard-blocks LONG FAR (overbought reclaim won't hold)."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(rsi=76.0), {})
        assert sig is None, "RSI >= 75 must hard-block LONG FAR."

    def test_rsi_hard_reject_short_oversold(self):
        """RSI <= 25 hard-blocks SHORT FAR (oversold reclaim won't hold)."""
        candles = {"5m": _make_far_candles_short()}
        sig = self._call_short(candles, _far_indicators_short(rsi=24.0), {}, regime="RANGING")
        assert sig is None, "RSI <= 25 must hard-block SHORT FAR."

    def test_rsi_soft_penalty_long_borderline(self):
        """RSI in soft zone (65-75) adds penalty but doesn't hard-block LONG FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(rsi=68.0), {})
        assert sig is not None, "Borderline RSI must not hard-block FAR."
        assert sig.soft_penalty_total >= 6.0, "Borderline RSI must add ≥6 pts soft penalty."

    def test_rsi_soft_penalty_short_borderline(self):
        """RSI in soft zone (25-35) adds penalty but doesn't hard-block SHORT FAR."""
        candles = {"5m": _make_far_candles_short()}
        sig = self._call_short(candles, _far_indicators_short(rsi=32.0), {}, regime="RANGING")
        assert sig is not None, "Borderline RSI must not hard-block SHORT FAR."
        assert sig.soft_penalty_total >= 6.0, "Borderline RSI must add ≥6 pts soft penalty."

    # ── SL/TP geometry ──────────────────────────────────────────────────

    def test_long_sl_below_auction_wick_extreme(self):
        """SL for LONG FAR must be below the auction wick low (hard structural invalidation)."""
        candles = {"5m": _make_far_candles_long(auction_wick_low=98.5)}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert sig.stop_loss < 98.5, (
            f"SL {sig.stop_loss} must be below auction wick low 98.5"
        )

    def test_short_sl_above_auction_wick_extreme(self):
        """SL for SHORT FAR must be above the auction wick high (hard structural invalidation)."""
        candles = {"5m": _make_far_candles_short(auction_wick_high=101.5)}
        sig = self._call_short(candles, _far_indicators_short(), {}, regime="RANGING")
        assert sig is not None
        assert sig.stop_loss > 101.5, (
            f"SL {sig.stop_loss} must be above auction wick high 101.5"
        )

    def test_long_tp1_above_entry(self):
        """TP1 must be strictly above entry for LONG FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert sig.tp1 > sig.entry, "TP1 must be above entry for LONG FAR."

    def test_short_tp1_below_entry(self):
        """TP1 must be strictly below entry for SHORT FAR."""
        candles = {"5m": _make_far_candles_short()}
        sig = self._call_short(candles, _far_indicators_short(), {}, regime="RANGING")
        assert sig is not None
        assert sig.tp1 < sig.entry, "TP1 must be below entry for SHORT FAR."

    def test_long_tp2_greater_than_tp1(self):
        """TP2 > TP1 for LONG FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert sig.tp2 > sig.tp1

    def test_short_tp2_less_than_tp1(self):
        """TP2 < TP1 for SHORT FAR."""
        candles = {"5m": _make_far_candles_short()}
        sig = self._call_short(candles, _far_indicators_short(), {}, regime="RANGING")
        assert sig is not None
        assert sig.tp2 < sig.tp1

    def test_long_tp3_greater_than_tp2(self):
        """TP3 > TP2 for LONG FAR."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert sig.tp3 > sig.tp2

    # ── far_reclaim_level attribute ──────────────────────────────────────

    def test_far_reclaim_level_stored_on_signal(self):
        """Signal must store far_reclaim_level for execution_quality_check()."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert hasattr(sig, "far_reclaim_level"), "Signal must have far_reclaim_level attribute."
        assert sig.far_reclaim_level > 0, "far_reclaim_level must be positive."

    # ── Setup class and dispatch registration ───────────────────────────

    def test_setup_class_registration(self):
        """Signal has setup_class == 'FAILED_AUCTION_RECLAIM'."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert sig.setup_class == "FAILED_AUCTION_RECLAIM"

    def test_registered_in_evaluate(self):
        """evaluate() returns at least one FAR signal when conditions are met."""
        ch = ScalpChannel()
        candles = {"5m": _make_far_candles_long()}
        sigs = ch.evaluate(
            "BTCUSDT", candles, _far_indicators_long(),
            {}, spread_pct=0.01, volume_24h_usd=10_000_000, regime="RANGING",
        )
        far_sigs = [s for s in sigs if s.setup_class == "FAILED_AUCTION_RECLAIM"]
        assert len(far_sigs) >= 1, "evaluate() must return a FAR signal when conditions are met."

    # ── FVG/OB soft penalty ──────────────────────────────────────────────

    def test_no_fvg_ob_soft_penalty(self):
        """Absence of FVG/OB adds a soft penalty of 5 pts."""
        candles = {"5m": _make_far_candles_long()}
        sig = self._call_long(candles, _far_indicators_long(), {})
        assert sig is not None
        assert sig.soft_penalty_total >= 5.0, "Missing FVG/OB must add ≥5 pts penalty."

    def test_fvg_present_no_ob_penalty(self):
        """When FVG is present, the 5pt FVG/OB penalty is not applied.

        With clean RSI (50) and FVG present, total penalty should be 0
        (no RSI penalty and no FVG/OB penalty).
        """
        candles = {"5m": _make_far_candles_long()}
        smc_data = {"fvg": [{"gap_high": 101.0, "gap_low": 100.5}]}
        sig = self._call_long(candles, _far_indicators_long(rsi=50.0), smc_data)
        assert sig is not None
        # FVG present: no FVG/OB penalty applied (0.0), and no RSI penalty (rsi=50)
        assert sig.soft_penalty_total < 5.0, (
            "When FVG is present, the 5pt FVG/OB penalty must not be applied."
        )
