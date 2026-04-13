"""PR-16: WHALE_MOMENTUM QUIET regime block.

Focused tests that prove:
1. _evaluate_whale_momentum() returns None when regime is QUIET.
2. _evaluate_whale_momentum() produces a signal (or skips for unrelated
   conditions) when the regime is NOT QUIET.
3. VOLUME_SURGE_BREAKOUT and BREAKDOWN_SHORT — the two unrelated evaluators
   that also block QUIET — remain unaffected by this PR (regression guard).
4. No unrelated evaluator paths are touched by this change.
"""

from __future__ import annotations

import numpy as np

from src.channels.scalp import ScalpChannel


# ---------------------------------------------------------------------------
# Shared helpers (mirrors test_whale_momentum_tp.py to keep test isolation)
# ---------------------------------------------------------------------------

def _make_1m_candles(n: int = 15, base: float = 100.0, trend: float = 0.05) -> dict:
    """Synthetic 1m OHLCV candles with a clear upward trend."""
    close = np.array([base + i * trend for i in range(n)])
    high = close + 0.3
    low = close - 0.3
    return {
        "open": close - 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 500.0,
    }


def _make_1m_candles_short(n: int = 15, base: float = 101.0) -> dict:
    """Synthetic 1m OHLCV candles with a clear downward trend."""
    close = np.array([base - i * 0.05 for i in range(n)])
    high = close + 0.3
    low = close - 0.3
    return {
        "open": close + 0.05,
        "high": high,
        "low": low,
        "close": close,
        "volume": np.ones(n) * 500.0,
    }


def _indicators_1m(rsi_last: float = 55.0, atr: float = 0.3) -> dict:
    return {
        "1m": {
            "rsi_last": rsi_last,
            "atr_last": atr,
            "ema9_last": 99.5,
            "ema21_last": 99.0,
        }
    }


def _long_smc() -> dict:
    """smc_data that satisfies WHALE_MOMENTUM LONG entry conditions."""
    ticks = [
        {"price": 100.0, "qty": 15000, "isBuyerMaker": False},  # buy: $1.5M
        {"price": 100.0, "qty": 5000,  "isBuyerMaker": True},   # sell: $0.5M (3× ratio)
    ]
    order_book = {
        "bids": [[100.0, 500.0]] * 10,   # bid depth: $50M → dominant
        "asks": [[100.1, 100.0]] * 10,   # ask depth: $10M
    }
    return {
        "whale_alert": {"amount_usd": 1_500_000},
        "volume_delta_spike": True,
        "recent_ticks": ticks,
        "order_book": order_book,
    }


def _short_smc() -> dict:
    """smc_data that satisfies WHALE_MOMENTUM SHORT entry conditions."""
    ticks = [
        {"price": 100.0, "qty": 5000,  "isBuyerMaker": False},  # buy: $0.5M
        {"price": 100.0, "qty": 15000, "isBuyerMaker": True},   # sell: $1.5M (3× ratio)
    ]
    order_book = {
        "bids": [[100.0, 100.0]] * 10,   # bid depth: $1M
        "asks": [[100.1, 500.0]] * 10,   # ask depth: $5M → dominant
    }
    return {
        "whale_alert": {"amount_usd": 1_500_000},
        "volume_delta_spike": True,
        "recent_ticks": ticks,
        "order_book": order_book,
    }


# ---------------------------------------------------------------------------
# PR-16 core tests: WHALE_MOMENTUM QUIET block
# ---------------------------------------------------------------------------

class TestWhaleMomentumQuietBlock:
    """Verify WHALE_MOMENTUM is hard-blocked in QUIET regime (PR-16)."""

    def test_whale_momentum_blocked_in_quiet_long(self):
        """LONG candidate must be rejected when regime=QUIET."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="QUIET"
        )
        assert sig is None, (
            "WHALE_MOMENTUM must return None in QUIET regime (PR-16 requirement)."
        )

    def test_whale_momentum_blocked_in_quiet_short(self):
        """SHORT candidate must be rejected when regime=QUIET."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles_short(n=15, base=101.0)}
        ind = _indicators_1m(rsi_last=45.0, atr=0.3)
        smc = _short_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="QUIET"
        )
        assert sig is None, (
            "WHALE_MOMENTUM SHORT must return None in QUIET regime (PR-16 requirement)."
        )

    def test_whale_momentum_blocked_in_quiet_case_insensitive(self):
        """Regime string comparison must be case-insensitive."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        for variant in ("quiet", "Quiet", "QUIET"):
            sig = ch._evaluate_whale_momentum(
                "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime=variant
            )
            assert sig is None, (
                f"WHALE_MOMENTUM must return None for regime={variant!r} (case-insensitive check)."
            )

    def test_whale_momentum_not_blocked_in_strong_trend(self):
        """WHALE_MOMENTUM must produce a Signal in STRONG_TREND when all conditions pass."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        assert sig is not None, (
            "WHALE_MOMENTUM must produce a signal in STRONG_TREND when tick-flow, "
            "OBI, and RSI conditions are met — the QUIET gate must not fire here."
        )
        assert sig.setup_class == "WHALE_MOMENTUM"

    def test_whale_momentum_not_blocked_in_volatile(self):
        """WHALE_MOMENTUM must produce a Signal in VOLATILE when all conditions pass."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="VOLATILE"
        )
        assert sig is not None, (
            "WHALE_MOMENTUM must produce a signal in VOLATILE when tick-flow, "
            "OBI, and RSI conditions are met — the QUIET gate must not fire here."
        )
        assert sig.setup_class == "WHALE_MOMENTUM"

    def test_whale_momentum_not_blocked_in_ranging(self):
        """WHALE_MOMENTUM must produce a Signal in RANGING when all conditions pass."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="RANGING"
        )
        assert sig is not None, (
            "WHALE_MOMENTUM must produce a signal in RANGING when tick-flow, "
            "OBI, and RSI conditions are met — the QUIET gate must not fire here."
        )
        assert sig.setup_class == "WHALE_MOMENTUM"


# ---------------------------------------------------------------------------
# Regression guard: unrelated evaluators retain their own QUIET behaviour
# ---------------------------------------------------------------------------

class TestUnrelatedEvaluatorsUnaffected:
    """Prove that the PR-16 change has no side-effect on other evaluator paths.

    VOLUME_SURGE_BREAKOUT and BREAKDOWN_SHORT had their own QUIET blocks
    before this PR.  Their behaviour must be unchanged.
    """

    # ------------------------------------------------------------------
    # Minimal 5m candle builder for VOLUME_SURGE_BREAKOUT / BREAKDOWN_SHORT
    # ------------------------------------------------------------------
    @staticmethod
    def _make_5m_candles(n: int = 35, base: float = 100.0) -> dict:
        close = np.array([base + i * 0.01 for i in range(n)])
        high = close + 0.5
        low = close - 0.5
        # Give the last candle a volume surge to satisfy the breakout gate.
        volume = np.ones(n) * 200.0
        volume[-1] = 2000.0  # well above 1.5× rolling avg
        return {
            "open": close - 0.05,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }

    @staticmethod
    def _make_5m_candles_down(n: int = 35, base: float = 101.0) -> dict:
        close = np.array([base - i * 0.01 for i in range(n)])
        high = close + 0.5
        low = close - 0.5
        volume = np.ones(n) * 200.0
        volume[-1] = 2000.0
        return {
            "open": close + 0.05,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }

    @staticmethod
    def _full_indicators() -> dict:
        return {
            "1m": {"rsi_last": 55.0, "atr_last": 0.3, "ema9_last": 99.5, "ema21_last": 99.0},
            "5m": {"rsi_last": 55.0, "atr_last": 0.5, "ema9_last": 99.0, "ema21_last": 98.5},
            "1h": {"rsi_last": 55.0, "ema9_last": 98.0, "ema21_last": 97.0, "ema200_last": 90.0,
                   "adx_last": 25.0, "macd_last": 0.1, "macd_signal_last": 0.05},
        }

    @staticmethod
    def _fvg_smc() -> dict:
        return {
            "fvg": {"direction": "bullish", "gap_start": 99.5, "gap_end": 100.0},
            "orderblock": {"direction": "bullish", "high": 100.5, "low": 99.5},
        }

    def test_volume_surge_breakout_still_blocked_in_quiet(self):
        """VOLUME_SURGE_BREAKOUT QUIET block (pre-PR-16) must remain unchanged."""
        ch = ScalpChannel()
        candles = {
            "1m": _make_1m_candles(),
            "5m": self._make_5m_candles(),
        }
        ind = self._full_indicators()
        smc = self._fvg_smc()

        sig = ch._evaluate_volume_surge_breakout(
            "ETHUSDT", candles, ind, smc, 0.01, 5_000_000, regime="QUIET"
        )
        assert sig is None, (
            "VOLUME_SURGE_BREAKOUT must still return None in QUIET (pre-existing gate, "
            "unaffected by PR-16)."
        )

    def test_breakdown_short_still_blocked_in_quiet(self):
        """BREAKDOWN_SHORT QUIET block (pre-PR-16) must remain unchanged."""
        ch = ScalpChannel()
        candles = {
            "1m": _make_1m_candles_short(),
            "5m": self._make_5m_candles_down(),
        }
        ind = self._full_indicators()
        smc = self._fvg_smc()

        sig = ch._evaluate_breakdown_short(
            "ETHUSDT", candles, ind, smc, 0.01, 5_000_000, regime="QUIET"
        )
        assert sig is None, (
            "BREAKDOWN_SHORT must still return None in QUIET (pre-existing gate, "
            "unaffected by PR-16)."
        )
