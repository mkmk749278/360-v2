"""Scanner-side wiring for the graded BTC-State (src/scanner _get_btc_state_cached).

Covers the per-cycle cache (Cost Discipline: the multi-TF compute runs once per TTL,
not per signal) and fail-open behaviour.  The pure scoring/coupling/haircut math is
covered in test_btc_state.py.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import numpy as np

from src.scanner import Scanner


def _make_scanner(**kwargs) -> Scanner:
    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    router_mock = MagicMock(active_signals={})
    router_mock.cleanup_expired.return_value = 0
    defaults = dict(
        pair_mgr=MagicMock(),
        data_store=MagicMock(),
        channels=[],
        smc_detector=MagicMock(),
        regime_detector=MagicMock(),
        predictive=MagicMock(),
        exchange_mgr=MagicMock(),
        spot_client=None,
        telemetry=MagicMock(),
        signal_queue=signal_queue,
        router=router_mock,
    )
    defaults.update(kwargs)
    return Scanner(**defaults)


def _btc_candles(closes):
    c = np.asarray(closes, dtype=np.float64)
    return {"close": c, "high": c * 1.001, "low": c * 0.999, "open": c, "volume": np.ones_like(c)}


def _trend(start, step, n=120):
    return _btc_candles([start + step * i for i in range(n)])


class TestGetBtcStateCached:
    def test_downtrend_yields_negative_b(self):
        scanner = _make_scanner()
        down = _trend(160.0, -0.5)
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: down if sym == "BTCUSDT" else None
        )
        res = scanner._get_btc_state_cached()
        assert res["status"] == "ok"
        assert res["b"] < 0.0  # hostile to longs

    def test_uptrend_yields_positive_b(self):
        scanner = _make_scanner()
        up = _trend(100.0, 0.5)
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: up if sym == "BTCUSDT" else None
        )
        assert scanner._get_btc_state_cached()["b"] > 0.0

    def test_cache_reused_within_ttl(self):
        """The multi-TF compute must run once per cycle, not per call (cost)."""
        scanner = _make_scanner()
        up = _trend(100.0, 0.5)
        gc = MagicMock(side_effect=lambda sym, tf: up if sym == "BTCUSDT" else None)
        scanner.data_store.get_candles = gc
        first = scanner._get_btc_state_cached()
        calls_after_first = gc.call_count
        second = scanner._get_btc_state_cached()
        # No additional candle fetches on the cached call; identical object returned.
        assert gc.call_count == calls_after_first
        assert second is first

    def test_fail_open_when_store_raises(self):
        scanner = _make_scanner()

        def _raise(sym, tf):
            raise RuntimeError("store down")

        scanner.data_store.get_candles = MagicMock(side_effect=_raise)
        res = scanner._get_btc_state_cached()
        assert res["b"] == 0.0  # neutral no-op

    def test_insufficient_data_is_neutral(self):
        scanner = _make_scanner()
        short = _trend(100.0, 0.5, n=10)
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: short if sym == "BTCUSDT" else None
        )
        res = scanner._get_btc_state_cached()
        assert res["b"] == 0.0


def _weekly(closes):
    import numpy as np
    c = np.asarray(closes, dtype=np.float64)
    return {"close": c, "high": c, "low": c, "open": c, "volume": np.ones_like(c)}


class TestGetBtcMacroCached:
    def test_weekly_below_ma_reads_bear(self):
        scanner = _make_scanner()
        wk = _weekly([100.0] * 199 + [60.0])
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: wk if (sym == "BTCUSDT" and tf == "1w") else None
        )
        res = scanner._get_btc_macro_cached()
        assert res["macro_bear"] is True and res["basis"] == "weekly"

    def test_weekly_above_ma_not_bear(self):
        scanner = _make_scanner()
        wk = _weekly([100.0] * 199 + [150.0])
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: wk if (sym == "BTCUSDT" and tf == "1w") else None
        )
        assert scanner._get_btc_macro_cached()["macro_bear"] is False

    def test_cache_reused_within_ttl(self):
        scanner = _make_scanner()
        wk = _weekly([100.0] * 199 + [60.0])
        gc = MagicMock(side_effect=lambda sym, tf: wk if (sym == "BTCUSDT" and tf == "1w") else None)
        scanner.data_store.get_candles = gc
        first = scanner._get_btc_macro_cached()
        n = gc.call_count
        second = scanner._get_btc_macro_cached()
        assert gc.call_count == n and second is first

    def test_fail_open_not_bear_when_store_raises(self):
        scanner = _make_scanner()

        def _raise(sym, tf):
            raise RuntimeError("store down")

        scanner.data_store.get_candles = MagicMock(side_effect=_raise)
        assert scanner._get_btc_macro_cached()["macro_bear"] is False
