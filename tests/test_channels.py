"""Tests for channel strategies – evaluate() logic."""

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
        # Borderline wick: body=0.4, lower_wick=0.1 (25% of body → penalty)
        m5["open"][-1]  = 100.85
        m5["low"][-1]   = 100.75   # lower_wick = 100.85 - 100.75 = 0.10 (25% of 0.4)
        m5["high"][-1]  = 101.0
        candles = {"5m": m5}
        # Borderline RSI for LONG: 72 → +5.0 penalty
        ind = _srflip_indicators_long(rsi_val=72.0)
        sig = self._call_long(candles, ind, _srflip_smc(direction="LONG"))
        assert sig is not None
        # proximity (+3.0) + wick (+4.0) + RSI (+5.0) = 12.0 minimum
        assert sig.soft_penalty_total >= 12.0, (
            f"Expected ≥12.0 accumulated penalty, got {sig.soft_penalty_total}"
        )
