"""Tests for WHALE_MOMENTUM evaluator-level TP targets (B13 compliance).

Verifies that _evaluate_whale_momentum() now computes Type A — Fixed Ratio TP
targets at the evaluator level (1.5R, 2.5R, 4.0R) instead of deferring with
zero values, per OWNER_BRIEF.md and B13.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.channels.scalp import ScalpChannel


# ---------------------------------------------------------------------------
# Shared helpers (mirror the pattern used in test_pr07_specialist_path_quality)
# ---------------------------------------------------------------------------

def _make_1m_candles(n: int = 15, base: float = 100.0, trend: float = 0.05) -> dict:
    """Synthetic 1m OHLCV candles with a clear trend direction."""
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
    """Candles falling over time — suitable for a SHORT signal."""
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
    """smc_data that drives a LONG WHALE_MOMENTUM signal."""
    ticks = [
        {"price": 100.0, "qty": 15000, "isBuyerMaker": False},  # buy: $1.5M
        {"price": 100.0, "qty": 5000, "isBuyerMaker": True},    # sell: $0.5M (3×)
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
    """smc_data that drives a SHORT WHALE_MOMENTUM signal."""
    ticks = [
        {"price": 100.0, "qty": 5000, "isBuyerMaker": False},   # buy: $0.5M
        {"price": 100.0, "qty": 15000, "isBuyerMaker": True},   # sell: $1.5M (3×)
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
# Tests
# ---------------------------------------------------------------------------

class TestWhaleMomentumTP:
    """Verify WHALE_MOMENTUM now sets evaluator-level TP targets (B13 fix)."""

    def test_whale_momentum_tp_long(self):
        """LONG signal: TP1/2/3 must equal entry + risk * 1.5/2.5/4.0."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")

        entry = sig.entry
        sl = sig.stop_loss
        # Risk is derived from the actual SL in the built signal (same basis the
        # evaluator uses when computing its R-multiple TPs).
        risk = abs(entry - sl)

        assert risk > 0, "Risk must be positive for a valid LONG signal."
        assert sig.tp1 == pytest.approx(entry + risk * 1.5, rel=1e-4)
        assert sig.tp2 == pytest.approx(entry + risk * 2.5, rel=1e-4)
        assert sig.tp3 == pytest.approx(entry + risk * 4.0, rel=1e-4)

        # All TPs must be above entry for LONG
        assert sig.tp1 > entry, "TP1 must be above entry for LONG."
        assert sig.tp2 > entry, "TP2 must be above entry for LONG."
        assert sig.tp3 > entry, "TP3 must be above entry for LONG."

    def test_whale_momentum_tp_short(self):
        """SHORT signal: TP1/2/3 must equal entry - risk * 1.5/2.5/4.0."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles_short(n=15, base=101.0)}
        ind = _indicators_1m(rsi_last=45.0, atr=0.3)
        smc = _short_smc()
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")

        entry = sig.entry
        sl = sig.stop_loss
        # Risk is derived from the actual SL in the built signal.
        risk = abs(sl - entry)

        assert risk > 0, "Risk must be positive for a valid SHORT signal."
        assert sig.tp1 == pytest.approx(entry - risk * 1.5, rel=1e-4)
        assert sig.tp2 == pytest.approx(entry - risk * 2.5, rel=1e-4)
        assert sig.tp3 == pytest.approx(entry - risk * 4.0, rel=1e-4)

        # All TPs must be below entry for SHORT
        assert sig.tp1 < entry, "TP1 must be below entry for SHORT."
        assert sig.tp2 < entry, "TP2 must be below entry for SHORT."
        assert sig.tp3 < entry, "TP3 must be below entry for SHORT."

        # All TPs must be positive (prices > 0)
        assert sig.tp1 > 0, "TP1 must be > 0."
        assert sig.tp2 > 0, "TP2 must be > 0."
        assert sig.tp3 > 0, "TP3 must be > 0."

    def test_whale_momentum_tp_not_zero(self):
        """After evaluation, tp1/tp2/tp3 must all be non-zero (B13 compliance)."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")

        assert sig.tp1 != 0.0, "tp1 must not be 0.0 — evaluator must set real TP."
        assert sig.tp2 != 0.0, "tp2 must not be 0.0 — evaluator must set real TP."
        assert sig.tp3 != 0.0, "tp3 must not be 0.0 — evaluator must set real TP."

    def test_whale_momentum_tp_degenerate_risk(self):
        """When entry ≈ stop_loss (near-zero risk), fallback to ATR produces valid TPs."""
        ch = ScalpChannel()
        # Use exactly 10 candles (minimum) so swing lookback fails → fallback SL path.
        # Craft very flat candles so any computed SL distance might approach ATR floor.
        n = 10
        base = 100.0
        close_arr = np.array([base] * n)  # completely flat — sl_dist dominated by ATR floor
        candles_1m = {
            "open": close_arr - 0.001,
            "high": close_arr + 0.001,
            "low": close_arr - 0.001,
            "close": close_arr,
            "volume": np.ones(n) * 500.0,
        }
        candles = {"1m": candles_1m}
        atr_val = 0.5
        ind = {"1m": {"rsi_last": 55.0, "atr_last": atr_val}}
        smc = _long_smc()
        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        if sig is None:
            pytest.skip("Evaluator returned None — market-condition filters not met.")

        # TPs must all be positive and above entry for LONG
        entry = sig.entry
        assert sig.tp1 > 0, "TP1 must be > 0 even with degenerate risk."
        assert sig.tp2 > 0, "TP2 must be > 0 even with degenerate risk."
        assert sig.tp3 > 0, "TP3 must be > 0 even with degenerate risk."
        assert sig.tp1 > entry, "TP1 must be above entry for LONG (degenerate risk)."
        assert sig.tp2 > entry, "TP2 must be above entry for LONG (degenerate risk)."
        assert sig.tp3 > entry, "TP3 must be above entry for LONG (degenerate risk)."
