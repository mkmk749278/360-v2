"""WHALE_MOMENTUM regime-gate behaviour.

Originally added in PR-16 to verify that WHALE_MOMENTUM was *blocked* in
QUIET regime.  The block was removed in the app-era doctrine reset
(OWNER_BRIEF §3.4: "WHALE / FUNDING / LIQ_REVERSAL — direction comes from
tape / funding / cascade — None [HTF/regime treatment]").  These tests
now assert the *new* contract:

1. WHALE_MOMENTUM produces a Signal in QUIET regime when its thesis
   gates (whale_alert + volume_delta_spike + order_book_imbalance) pass.
2. WHALE_MOMENTUM still produces a Signal when regime is anything else
   and thesis gates pass.
3. VSB / BDS regime-gate removal is verified separately — they still
   reject in QUIET candles when the breakout/volume thesis gates fail
   (so the "regression-guard" tests pass for the right reason).
"""

from __future__ import annotations

import numpy as np

from src.channels.scalp import ScalpChannel


# ---------------------------------------------------------------------------
# Shared helpers
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
        {"price": 100.0, "qty": 15000, "isBuyerMaker": False},
        {"price": 100.0, "qty": 5000,  "isBuyerMaker": True},
    ]
    order_book = {
        "bids": [[100.0, 500.0]] * 10,
        "asks": [[100.1, 100.0]] * 10,
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
        {"price": 100.0, "qty": 5000,  "isBuyerMaker": False},
        {"price": 100.0, "qty": 15000, "isBuyerMaker": True},
    ]
    order_book = {
        "bids": [[100.0, 100.0]] * 10,
        "asks": [[100.1, 500.0]] * 10,
    }
    return {
        "whale_alert": {"amount_usd": 1_500_000},
        "volume_delta_spike": True,
        "recent_ticks": ticks,
        "order_book": order_book,
    }


# ---------------------------------------------------------------------------
# WHALE_MOMENTUM — regime gate removed (app-era doctrine reset)
# ---------------------------------------------------------------------------


class TestWhaleMomentumRegimeGateRemoved:
    """WHALE_MOMENTUM must now fire in any regime when thesis gates pass.

    Previously (PR-16) WHALE returned None in QUIET regime via a hard
    `regime_blocked` rejection.  That regime block contradicted
    OWNER_BRIEF §3.4 which states WHALE is "internally direction-driven
    from tape" with no HTF/regime treatment.  The thesis gates
    (whale_alert + volume_delta_spike + order_book_imbalance) already
    ensure no signal fires without genuine flow, so the regime block
    was redundant.
    """

    def test_whale_momentum_fires_in_quiet_long(self):
        """LONG WHALE candidate now passes through QUIET regime when
        thesis gates are satisfied (whale_alert, delta_spike, OB imbalance)."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="QUIET"
        )
        assert sig is not None, (
            "WHALE_MOMENTUM regime gate was removed; LONG candidate with "
            "passing thesis gates must produce a Signal even in QUIET."
        )
        assert sig.setup_class == "WHALE_MOMENTUM"

    def test_whale_momentum_fires_in_quiet_short(self):
        """SHORT WHALE candidate fires in QUIET — symmetric to the LONG case."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles_short(n=15, base=101.0)}
        ind = _indicators_1m(rsi_last=45.0, atr=0.3)
        smc = _short_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="QUIET"
        )
        assert sig is not None
        assert sig.setup_class == "WHALE_MOMENTUM"

    def test_whale_momentum_thesis_gates_still_apply_in_quiet(self):
        """The regime gate is gone but thesis gates remain — a candidate
        with NO whale_alert / delta_spike must still reject."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles()}
        ind = _indicators_1m()
        # Empty smc — no whale alert, no flow
        smc = {"recent_ticks": [], "order_book": None}

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="QUIET"
        )
        assert sig is None, (
            "Thesis gates must still apply — no whale flow → no signal."
        )

    def test_whale_momentum_fires_in_strong_trend(self):
        """Sanity: WHALE still produces a Signal in non-QUIET regimes
        (no regression from the gate removal)."""
        ch = ScalpChannel()
        candles = {"1m": _make_1m_candles(n=15, base=99.8, trend=0.05)}
        ind = _indicators_1m(rsi_last=55.0, atr=0.3)
        smc = _long_smc()

        sig = ch._evaluate_whale_momentum(
            "BTCUSDT", candles, ind, smc, 0.01, 10_000_000, regime="STRONG_TREND"
        )
        assert sig is not None


# ---------------------------------------------------------------------------
# VSB / BDS — regime gate also removed
# ---------------------------------------------------------------------------


class TestVsbBdsRegimeGateRemoved:
    """VOLUME_SURGE_BREAKOUT and BREAKDOWN_SHORT regime gates were also
    removed per OWNER_BRIEF §3.4 ("Breakout (VSB / BDS / ORB) — fires in
    any HTF context").  Thesis gates (breakout_not_found,
    volume_spike_missing) still reject candidates that don't meet the
    structural setup, so signals only fire when the thesis is real.
    """

    @staticmethod
    def _make_5m_candles(n: int = 35, base: float = 100.0) -> dict:
        close = np.array([base + i * 0.01 for i in range(n)])
        high = close + 0.5
        low = close - 0.5
        volume = np.ones(n) * 200.0
        volume[-1] = 2000.0
        return {
            "open": close - 0.05,
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

    def test_vsb_in_quiet_rejects_for_thesis_not_regime(self):
        """VSB in QUIET still returns None on these candles, but the
        rejection reason is now thesis-driven (breakout_not_found /
        volume / EMA), not 'regime_blocked'."""
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
        # Signal still likely None due to thesis gates, but rejection
        # reason is no longer regime_blocked.
        assert ch._active_no_signal_reason != "regime_blocked", (
            "VSB regime gate was removed; rejection in QUIET must be "
            "thesis-driven, not regime-driven."
        )

    def test_bds_in_quiet_rejects_for_thesis_not_regime(self):
        """BDS in QUIET — symmetric to VSB."""
        ch = ScalpChannel()
        candles = {
            "1m": _make_1m_candles_short(),
            "5m": self._make_5m_candles(),
        }
        ind = self._full_indicators()
        smc = self._fvg_smc()

        sig = ch._evaluate_breakdown_short(
            "ETHUSDT", candles, ind, smc, 0.01, 5_000_000, regime="QUIET"
        )
        assert ch._active_no_signal_reason != "regime_blocked", (
            "BDS regime gate was removed; rejection in QUIET must be "
            "thesis-driven, not regime-driven."
        )
