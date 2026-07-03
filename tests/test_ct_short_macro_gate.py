"""Counter-trend SHORT macro mirror (S40) — dark predicate + gate semantics.

Mirror of the CT-long gate (test_btc_state_scanner.py::TestCtLongMacroSuppressed):
only SHORT + a gated reversal setup is in scope; suppress while EITHER the BTC
macro leg OR the coin's own higher-TF trend reads UP; fail open on errors.
The predicate is flag-independent (the #597 shadow pattern) — these tests pin
the decision itself; the enabled flag only decides reject-vs-[SHADOW]-log.
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


def _series(closes):
    c = np.asarray(closes, dtype=np.float64)
    return {"close": c, "high": c, "low": c, "open": c, "volume": np.ones_like(c)}


RISING = [100.0 + i for i in range(80)]
FALLING = [300.0 - i for i in range(80)]


def _scanner_with(btc_close, coin_close):
    scanner = _make_scanner()

    def _gc(sym, tf):
        if sym == "BTCUSDT" and tf == "1w":
            return _series(btc_close)
        if sym == "ALTUSDT" and tf == "1d":
            return _series(coin_close)
        return None

    scanner.data_store.get_candles = MagicMock(side_effect=_gc)
    return scanner


class TestCtShortMacroWouldSuppress:
    def test_gated_short_suppressed_when_btc_macro_up(self):
        s = _scanner_with(RISING, FALLING)
        sup, why = s._ct_short_macro_would_suppress(
            "ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "SHORT"
        )
        assert sup is True
        assert why.startswith("btc_")

    def test_gated_short_suppressed_when_coin_up_even_if_btc_down(self):
        s = _scanner_with(FALLING, RISING)
        sup, why = s._ct_short_macro_would_suppress(
            "ALTUSDT", "FAILED_AUCTION_RECLAIM", "SHORT"
        )
        assert sup is True
        assert why.startswith("coin_")

    def test_gated_short_allowed_when_both_down(self):
        s = _scanner_with(FALLING, FALLING)
        sup, _ = s._ct_short_macro_would_suppress(
            "ALTUSDT", "BREAKDOWN_SHORT", "SHORT"
        )
        assert sup is False

    def test_longs_never_touched(self):
        s = _scanner_with(RISING, RISING)
        sup, _ = s._ct_short_macro_would_suppress(
            "ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "LONG"
        )
        assert sup is False

    def test_non_gated_setup_never_touched(self):
        # QUIET_COMPRESSION_BREAK shorts were the WINNING short cohort in the
        # 2026-07 window (67% win) — they must stay out of scope by default.
        s = _scanner_with(RISING, RISING)
        sup, _ = s._ct_short_macro_would_suppress(
            "ALTUSDT", "QUIET_COMPRESSION_BREAK", "SHORT"
        )
        assert sup is False

    def test_sr_flip_short_not_in_default_scope(self):
        # SR_FLIP shorts ran ~breakeven at 50% win — not part of the bleed.
        s = _scanner_with(RISING, RISING)
        sup, _ = s._ct_short_macro_would_suppress(
            "ALTUSDT", "SR_FLIP_RETEST", "SHORT"
        )
        assert sup is False

    def test_fail_open_when_store_raises(self):
        s = _make_scanner()
        s.data_store.get_candles = MagicMock(side_effect=RuntimeError("boom"))
        sup, _ = s._ct_short_macro_would_suppress(
            "ALTUSDT", "LIQUIDITY_SWEEP_REVERSAL", "SHORT"
        )
        assert sup is False

    def test_gate_is_dark_by_default(self):
        from config import CT_SHORT_MACRO_GATE_ENABLED

        assert CT_SHORT_MACRO_GATE_ENABLED is False
