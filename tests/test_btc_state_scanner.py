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


def _wk_series(closes):
    import numpy as np
    c = np.asarray(closes, dtype=np.float64)
    return {"close": c, "high": c, "low": c, "open": c, "volume": np.ones_like(c)}


class TestGetBtcMacroDirCached:
    def test_macro_downtrend_suppresses_longs(self):
        scanner = _make_scanner()
        falling = _wk_series([300.0 - i for i in range(80)])
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: falling if (sym == "BTCUSDT" and tf == "1w") else None
        )
        res = scanner._get_btc_macro_dir_cached()
        assert res["longs_suppressed"] is True and res["regime"] == "DECLINE"

    def test_macro_uptrend_allows_longs(self):
        scanner = _make_scanner()
        rising = _wk_series([100.0 + i for i in range(80)])
        scanner.data_store.get_candles = MagicMock(
            side_effect=lambda sym, tf: rising if (sym == "BTCUSDT" and tf == "1w") else None
        )
        assert scanner._get_btc_macro_dir_cached()["longs_suppressed"] is False

    def test_cache_reused_within_ttl(self):
        scanner = _make_scanner()
        falling = _wk_series([300.0 - i for i in range(80)])
        gc = MagicMock(side_effect=lambda sym, tf: falling if (sym == "BTCUSDT" and tf == "1w") else None)
        scanner.data_store.get_candles = gc
        first = scanner._get_btc_macro_dir_cached()
        n = gc.call_count
        second = scanner._get_btc_macro_dir_cached()
        assert gc.call_count == n and second is first

    def test_fail_open_not_suppressed_when_store_raises(self):
        scanner = _make_scanner()

        def _raise(sym, tf):
            raise RuntimeError("store down")

        scanner.data_store.get_candles = MagicMock(side_effect=_raise)
        assert scanner._get_btc_macro_dir_cached()["longs_suppressed"] is False


class TestCtLongMacroSuppressed:
    """The scalp-first gate decision: narrow scope, both layers, auto-restore."""

    def _scanner_with(self, btc_close, coin_close):
        scanner = _make_scanner()

        def _gc(sym, tf):
            if sym == "BTCUSDT" and tf == "1w":
                return _wk_series(btc_close)
            if sym == "ALTUSDT" and tf == "1d":
                return _wk_series(coin_close)
            return None

        scanner.data_store.get_candles = MagicMock(side_effect=_gc)
        return scanner

    def test_gated_long_suppressed_when_btc_macro_declines(self):
        s = self._scanner_with([300.0 - i for i in range(80)], [100.0 + i for i in range(80)])
        sup, why = s._ct_long_macro_suppressed("ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "LONG")
        assert sup is True and why.startswith("btc_")

    def test_gated_long_suppressed_when_coin_declines_even_if_btc_ok(self):
        # BTC fine, but the coin's own trend is down → "needs both to permit it".
        s = self._scanner_with([100.0 + i for i in range(80)], [300.0 - i for i in range(80)])
        sup, why = s._ct_long_macro_suppressed("ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "LONG")
        assert sup is True and why.startswith("coin_")

    def test_mover_trend_pullback_never_gated_trend_following(self):
        # MOVER is trend-continuation (rides the coin's own move) — must NOT be
        # suppressed even in a full BTC + coin decline.  Owner's live feed showed
        # MOVER longs winning (+4–6%) while BTC was macro-bear.
        s = self._scanner_with([300.0 - i for i in range(80)], [300.0 - i for i in range(80)])
        sup, _ = s._ct_long_macro_suppressed("ALTUSDT", "MOVER_TREND_PULLBACK", "LONG")
        assert sup is False

    def test_gated_long_allowed_when_both_up(self):
        s = self._scanner_with([100.0 + i for i in range(80)], [100.0 + i for i in range(80)])
        sup, _ = s._ct_long_macro_suppressed("ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "LONG")
        assert sup is False  # auto-restored when the trend is up

    def test_shorts_never_touched(self):
        s = self._scanner_with([300.0 - i for i in range(80)], [300.0 - i for i in range(80)])
        sup, _ = s._ct_long_macro_suppressed("ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "SHORT")
        assert sup is False  # scalp doctrine: direction-agnostic, shorts work in a downtrend

    def test_non_gated_setup_never_touched(self):
        s = self._scanner_with([300.0 - i for i in range(80)], [300.0 - i for i in range(80)])
        sup, _ = s._ct_long_macro_suppressed("ALTUSDT", "VOLUME_SURGE_BREAKOUT", "LONG")
        assert sup is False  # only the proven-bleeding counter-trend setups are in scope

    def test_disabled_layers_no_suppression(self):
        s = self._scanner_with([300.0 - i for i in range(80)], [300.0 - i for i in range(80)])
        # With the per-coin layer the only one on but disabled too, nothing suppresses.
        from unittest.mock import patch
        with patch("src.scanner.CT_LONG_MACRO_USE_BTC", False), \
             patch("src.scanner.CT_LONG_MACRO_USE_PER_COIN", False):
            sup, _ = s._ct_long_macro_suppressed("ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "LONG")
        assert sup is False
