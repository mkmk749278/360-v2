"""Tests for the MOVER_TREND_PULLBACK evaluator (Session 29).

The path catches the *continuation* pullbacks on a confirmed top-mover — price
rides the MA stack and offers repeated pullback-to-MA re-entries — which VSB/BDS
(ignition-only) structurally cannot. Ships DARK behind
``MOVER_TREND_PULLBACK_ENABLED``; mover-only via ``smc_data['is_mover_promoted']``.
"""

import src.channels.scalp as scalp_mod
from src.channels.scalp import ScalpChannel
from src.smc import Direction


def _trend_candles(*, up: bool, n: int = 115, base: float = 100.0, step: float = 0.1):
    """Monotonic 15m series → MA7>MA25>MA99 (up) or inverse (down).

    Default high/low wicks (±0.5) make the prior candle's wick tag the fast MA
    while the latest candle closes in the trend direction (pullback + reclaim).
    """
    closes = [base + (step if up else -step) * i for i in range(n)]
    highs = [c + 0.5 for c in closes]
    lows = [c - 0.5 for c in closes]
    return {
        "15m": {
            "open": list(closes),
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": [1000.0] * n,
        }
    }


def _inputs(*, up: bool, step: float = 0.1):
    # default step → ~4% MA7↔MA99 separation, clears the mover gate (>= 3%).
    candles = _trend_candles(up=up, step=step)
    indicators = {"15m": {"atr_last": 0.3}}
    smc_data = {"pair_profile": None, "regime_context": None}
    return candles, indicators, smc_data


class TestMoverTrendPullback:
    def test_live_by_default_in_testing_phase(self):
        """Default-on (no subscribers yet — we ship live): a valid setup fires."""
        assert scalp_mod.MOVER_TREND_PULLBACK_ENABLED is True
        candles, indicators, smc_data = _inputs(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None, "live by default — a valid mover pullback must emit"

    def test_disabled_falls_back_to_shadow(self, monkeypatch):
        """Explicitly disabled: emits NO live signal (shadow-only fallback)."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", False)
        candles, indicators, smc_data = _inputs(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None, "disabled flag must suppress the live signal"

    def test_fires_long_when_enabled(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.direction == Direction.LONG
        assert sig.setup_class == "MOVER_TREND_PULLBACK"
        assert sig.stop_loss < sig.entry, "LONG stop must sit below entry"
        assert sig.htf_trend_aligned is True, "mover stack IS the higher-context trend"

    def test_fires_short_when_enabled(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=False)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "BTWUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_DOWN",
        )
        assert sig is not None
        assert sig.direction == Direction.SHORT
        assert sig.stop_loss > sig.entry, "SHORT stop must sit above entry"

    def test_rejects_weak_run(self, monkeypatch):
        """A gently-trending pair (small MA7↔MA99 separation) is NOT a mover —
        that's TPE's domain, this path must reject it."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=True, step=0.02)  # ~0.9% sep < 3%
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None, "weak run must reject (mover_run_too_small)"

    def test_registered_in_all_canonical_setup_maps(self):
        """MOVER_TREND_PULLBACK must be registered everywhere the other setups
        are, or classify_setup re-labels it and it never scores/dispatches as
        itself (the 0-emit bug). Locks the stringly-coupled registration."""
        from src.signal_quality import SetupClass, ACTIVE_PATH_PORTFOLIO_ROLES
        from src.scanner import _SCALP_SETUP_TO_FAMILY

        assert SetupClass("MOVER_TREND_PULLBACK") is SetupClass.MOVER_TREND_PULLBACK
        assert SetupClass.MOVER_TREND_PULLBACK in ACTIVE_PATH_PORTFOLIO_ROLES
        assert _SCALP_SETUP_TO_FAMILY.get("MOVER_TREND_PULLBACK") == "trend_following"

    def test_registered_in_channel_and_regime_compatibility_maps(self):
        """classify_setup sets channel_compatible / regime_compatible from these two
        maps; _prepare_signal hard-rejects a setup absent from EITHER (the real
        cause of 0 emissions). MOVER must sit wherever its VSB/BDS mover peers do:
        the 360_SCALP channel set + every market state."""
        from src.signal_quality import (
            CHANNEL_SETUP_COMPATIBILITY,
            REGIME_SETUP_COMPATIBILITY,
            SetupClass,
        )

        assert SetupClass.MOVER_TREND_PULLBACK in CHANNEL_SETUP_COMPATIBILITY["360_SCALP"]
        # Present in every regime the compat map defines — like VOLUME_SURGE_BREAKOUT.
        for state, setups in REGIME_SETUP_COMPATIBILITY.items():
            assert SetupClass.MOVER_TREND_PULLBACK in setups, (
                f"MOVER_TREND_PULLBACK missing from REGIME_SETUP_COMPATIBILITY[{state}] "
                "→ regime_compatible=False → hard-rejected before scoring"
            )

    def test_setup_class_preserved_through_classify(self):
        """A stamped MOVER signal keeps its identity through classify_setup
        (it is in _SELF_CLASSIFYING), rather than being re-labelled by heuristic."""
        from src.signal_quality import classify_setup, SetupClass, MarketState
        from types import SimpleNamespace
        sig = SimpleNamespace(setup_class="MOVER_TREND_PULLBACK", direction=Direction.LONG)
        assessment = classify_setup(
            channel_name="360_SCALP", signal=sig, indicators={}, smc_data={},
            market_state=MarketState.STRONG_TREND,
        )
        assert assessment.setup_class == SetupClass.MOVER_TREND_PULLBACK

    def test_htf_fan_rescues_compressed_15m_mover(self, monkeypatch):
        """A multi-day mover whose 15m stack has compressed (<3% sep) still fires
        when the 1H EMA fan confirms the run — the SYNUSDT case (15m ~1.5%, 1H wide).
        Same weak-15m inputs that reject in test_rejects_weak_run, now rescued by 1H."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=True, step=0.02)  # ~0.9% 15m sep
        indicators["1h"] = {"ema21_last": 110.0, "ema50_last": 100.0}  # 10% bullish fan
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "SYNUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None, "wide aligned 1H fan must rescue a compressed 15m mover"
        assert sig.direction == Direction.LONG

    def test_htf_fan_not_credited_when_misaligned(self, monkeypatch):
        """A bearish 1H fan must NOT count as strength for a LONG — the path falls
        back to the (weak) 15m separation and rejects."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=True, step=0.02)
        indicators["1h"] = {"ema21_last": 100.0, "ema50_last": 110.0}  # bearish — opposes LONG
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "SYNUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None, "misaligned 1H fan must not rescue a weak 15m run"

    def test_htf_aligned_fan_pct_helper(self):
        """Unit: the 1H fan is credited only when it agrees with the entry side."""
        f = ScalpChannel._mover_htf_aligned_fan_pct
        assert f({"ema21_last": 110.0, "ema50_last": 100.0}, Direction.LONG) == 10.0
        assert f({"ema21_last": 90.0, "ema50_last": 100.0}, Direction.SHORT) == 10.0
        # Misaligned → 0.0
        assert f({"ema21_last": 110.0, "ema50_last": 100.0}, Direction.SHORT) == 0.0
        assert f({"ema21_last": 90.0, "ema50_last": 100.0}, Direction.LONG) == 0.0
        # Missing / invalid → 0.0 (fail-safe, never inflates strength)
        assert f(None, Direction.LONG) == 0.0
        assert f({"ema21_last": 110.0}, Direction.LONG) == 0.0
        assert f({"ema21_last": 110.0, "ema50_last": 0.0}, Direction.LONG) == 0.0

    def test_fires_on_pullback_that_compresses_fast_ma(self, monkeypatch):
        """The core fix: an uptrend whose recent pullback has dipped MA7 BELOW MA25
        (so the old strict ma_fast>ma_mid>ma_slow stack failed → no_ma_stack) still
        fires, because trend is now read on the mid/slow pair which holds."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        n = 115
        # Strong rise for 100 bars, then a 14-bar pullback, then a reclaim bar.
        closes = [100.0 + 0.4 * i for i in range(n - 15)]          # 100 → ~139.6
        peak = closes[-1]
        closes += [peak - 0.6 * (j + 1) for j in range(14)]        # pull back ~8.4
        closes.append(peak - 4.0)                                  # strong reclaim back above MA7
        ma_fast = sum(closes[-7:]) / 7
        ma_mid = sum(closes[-25:]) / 25
        ma_slow = sum(closes[-99:]) / 99
        # Precondition the test asserts the fix for: MA7 dipped below MA25, but the
        # mid/slow pair still holds the uptrend (and MA7↔MA99 sep is still wide).
        assert ma_fast < ma_mid, "pullback must have compressed MA7 below MA25"
        assert ma_mid > ma_slow, "mid/slow must still hold the uptrend"
        highs = [c + 0.5 for c in closes]
        lows = [c - 0.5 for c in closes]
        candles = {"15m": {"open": list(closes), "high": highs, "low": lows,
                           "close": closes, "volume": [1000.0] * n}}
        indicators = {"15m": {"atr_last": 0.3}}
        smc_data = {"pair_profile": None, "regime_context": None}
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None, "compressed-fast-MA pullback must fire under the fix"
        assert sig.direction == Direction.LONG

    # ── Multi-trigger continuation entries (Session 31) ──────────────────────

    def test_fast_pullback_stamps_trigger(self, monkeypatch):
        """The original shallow-pullback shape stamps entry_trigger=fast_pullback."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.entry_trigger == "fast_pullback"

    def _deep_candles(self):
        """Strong ramp, then a sharp 1-bar drop to ~the mid MA, then a reclaim bar
        that closes ABOVE the mid MA but still BELOW the (lagging-high) fast MA —
        the deep-dip shape the shallow trigger misses (close < fast MA)."""
        n = 115
        closes = [100.0 + 0.4 * i for i in range(n - 2)]
        peak = closes[-1]
        closes.append(peak - 5.0)   # sharp drop toward the mid MA
        closes.append(peak - 2.4)   # reclaim: above mid, below fast
        highs = [c + 0.1 for c in closes]
        lows = [c - 0.1 for c in closes]
        candles = {"15m": {"open": list(closes), "high": highs, "low": lows,
                           "close": closes, "volume": [1000.0] * n}}
        return candles, {"15m": {"atr_last": 0.3}}, {"pair_profile": None, "regime_context": None}

    def test_deep_pullback_fires_and_stamps(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = self._deep_candles()
        closes = candles["15m"]["close"]
        ma_fast = sum(closes[-7:]) / 7
        ma_mid = sum(closes[-25:]) / 25
        assert closes[-1] < ma_fast, "reclaim must stay below the fast MA (else it's a fast_pullback)"
        assert closes[-1] > ma_mid, "reclaim must close above the mid MA"
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None
        assert sig.entry_trigger == "deep_pullback"
        assert sig.stop_loss < sig.entry

    def test_deep_pullback_off_switch(self, monkeypatch):
        """With the deep trigger disabled, the same deep-dip shape no longer fires
        as deep (the shallow trigger can't claim it — close is below the fast MA)."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        monkeypatch.setattr(scalp_mod, "MOVER_TP_TRIGGER_DEEP_ENABLED", False)
        monkeypatch.setattr(scalp_mod, "MOVER_TP_TRIGGER_CONSOL_ENABLED", False)
        candles, indicators, smc_data = self._deep_candles()
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None

    def _consol_candles(self, *, up=True, atr=1.5, breakout_vol=2000.0):
        """A hard ramp that never dips to the MA (prev bar low stays clear of the
        fast-MA band) → only the guarded consolidation-break trigger can fire."""
        n = 115
        s = 0.4 if up else -0.4
        closes = [100.0 + s * i for i in range(n)]
        highs = [c + 0.1 for c in closes]
        lows = [c - 0.1 for c in closes]
        vols = [1000.0] * n
        vols[-1] = breakout_vol
        candles = {"15m": {"open": list(closes), "high": highs, "low": lows,
                           "close": closes, "volume": vols}}
        return candles, {"15m": {"atr_last": atr}}, {"pair_profile": None, "regime_context": None}

    def test_consol_break_fires_and_stamps(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = self._consol_candles(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is not None, "a hard ramp with volume must fire the consolidation-break trigger"
        assert sig.entry_trigger == "consol_break"
        assert sig.direction == Direction.LONG
        assert sig.stop_loss < sig.entry

    def test_consol_break_off_switch(self, monkeypatch):
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        monkeypatch.setattr(scalp_mod, "MOVER_TP_TRIGGER_CONSOL_ENABLED", False)
        candles, indicators, smc_data = self._consol_candles(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None, "disabling the consol trigger removes the only shape this ramp matches"

    # ── consolidation-break guards (helper-level, isolated) ──────────────────

    def _consol_helper_arrays(self):
        # 6-bar window (indices -7..-2) is tight; index -1 is the breakout slot.
        highs = [10.10, 10.08, 10.11, 10.09, 10.10, 10.07, 99.0]
        lows = [9.90, 9.92, 9.91, 9.93, 9.90, 9.94, 0.0]
        vols = [1000.0] * 6 + [2000.0]
        closes = [10.0] * 7
        return closes, highs, lows, vols

    def test_consol_helper_fires_when_clean(self):
        closes, highs, lows, vols = self._consol_helper_arrays()
        anchor = ScalpChannel._mover_consol_break(
            Direction.LONG, 10.2, closes, highs, lows, vols, ma_fast=10.0, atr_val=1.0,
        )
        assert anchor == min(lows[-7:-1]), "clean break returns the consolidation low as SL anchor"

    def test_consol_helper_rejects_overextension(self):
        closes, highs, lows, vols = self._consol_helper_arrays()
        # Tight range + volume still pass, but close sits 1.5 > 1.0×ATR beyond the fast MA.
        anchor = ScalpChannel._mover_consol_break(
            Direction.LONG, 11.5, closes, highs, lows, vols, ma_fast=10.0, atr_val=1.0,
        )
        assert anchor is None, "over-extended breakout must be rejected (anti-chase guard)"

    def test_consol_helper_rejects_low_volume(self):
        closes, highs, lows, vols = self._consol_helper_arrays()
        vols[-1] = 1000.0  # equal to window avg → below the 1.5× confirmation
        anchor = ScalpChannel._mover_consol_break(
            Direction.LONG, 10.2, closes, highs, lows, vols, ma_fast=10.0, atr_val=1.0,
        )
        assert anchor is None, "a break without volume confirmation must be rejected"

    def test_consol_helper_rejects_wide_range(self):
        closes, highs, lows, vols = self._consol_helper_arrays()
        highs[2] = 13.0  # blow out the window range past 1.5×ATR
        anchor = ScalpChannel._mover_consol_break(
            Direction.LONG, 13.5, closes, highs, lows, vols, ma_fast=10.0, atr_val=1.0,
        )
        assert anchor is None, "a wide window is the move itself, not a base — reject"

    def test_rejects_without_ma_stack(self, monkeypatch):
        """A flat/choppy mover (no clean MA stack) does not fire."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        n = 115
        flat = [100.0] * n  # constant — MA7 == MA25 == MA99, no strict stack
        candles = {
            "15m": {
                "open": list(flat),
                "high": [c + 0.5 for c in flat],
                "low": [c - 0.5 for c in flat],
                "close": flat,
                "volume": [1000.0] * n,
            }
        }
        indicators = {"15m": {"atr_last": 0.3}}
        smc_data = {"is_mover_promoted": True, "pair_profile": None, "regime_context": None}
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="RANGING",
        )
        assert sig is None
