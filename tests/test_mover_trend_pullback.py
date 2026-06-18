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


def _inputs(*, up: bool, is_mover: bool = True):
    candles = _trend_candles(up=up)
    indicators = {"15m": {"atr_last": 0.3}}
    smc_data = {"is_mover_promoted": is_mover, "pair_profile": None, "regime_context": None}
    return candles, indicators, smc_data


class TestMoverTrendPullback:
    def test_dark_by_default_returns_no_signal(self):
        """Flag off (default): a valid setup emits NO live signal (shadow only)."""
        assert scalp_mod.MOVER_TREND_PULLBACK_ENABLED is False
        candles, indicators, smc_data = _inputs(up=True)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "AGTUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None, "ships dark — must not emit until the flag is activated"

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

    def test_rejects_non_mover(self, monkeypatch):
        """Even with the flag on, a non-mover (flag absent) never fires."""
        monkeypatch.setattr(scalp_mod, "MOVER_TREND_PULLBACK_ENABLED", True)
        candles, indicators, smc_data = _inputs(up=True, is_mover=False)
        sig = ScalpChannel()._evaluate_mover_trend_pullback(
            "ETHUSDT", candles, indicators, smc_data, 0.01, 10_000_000, regime="TRENDING_UP",
        )
        assert sig is None, "path is mover-only — must reject when not a promoted mover"

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
