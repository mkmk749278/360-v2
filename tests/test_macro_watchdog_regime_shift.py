"""Tests for src/macro_watchdog._check_regime_shift — Phase-2b regime shift alert.

Verifies:
* First observation records baseline silently (no alert)
* Same direction next cycle → silent
* Direction flip → HIGH-severity alert routed to admin + free
* Cooldown is per-symbol — BTC flip does not silence ETH
* Cooldown blocks repeat alerts on rapid re-flips within window
* HTTP / parse errors degrade silently
"""
from __future__ import annotations

import asyncio
import time as _time
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from src.macro_watchdog import MacroWatchdog


def _kline(close_price: float) -> list:
    """Minimal Binance kline: [open_time, o, h, l, c, v, close_time, ...]."""
    return [0, "0", "0", "0", str(close_price), "0", 0, "0", 0, "0", "0", "0"]


def _klines_with_last_close(last_close: float, n: int = 22, base: float = 100.0) -> list:
    """Build n-candle kline payload where the first n-1 closes are `base`
    (so EMA21 ≈ base) and the last close is `last_close`."""
    return [_kline(base) for _ in range(n - 1)] + [_kline(last_close)]


def _make_session_response(klines: list, status: int = 200):
    response = MagicMock()
    response.status = status
    response.json = AsyncMock(return_value=klines)
    response_cm = MagicMock()
    response_cm.__aenter__ = AsyncMock(return_value=response)
    response_cm.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=response_cm)
    return session


def _make_watchdog():
    admin = AsyncMock(return_value=True)
    free = AsyncMock(return_value=True)
    return MacroWatchdog(send_alert=admin, send_to_free=free), admin, free


# ---------------------------------------------------------------------------
# Baseline + direction tracking
# ---------------------------------------------------------------------------


async def test_first_observation_records_baseline_silently():
    """First cycle for a symbol records direction without alerting."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response(_klines_with_last_close(105.0))  # UP
    await watchdog._check_regime_shift("BTCUSDT", session)
    admin.assert_not_awaited()
    free.assert_not_awaited()
    assert watchdog._regime_last_direction["BTCUSDT"] == "UP"


async def test_same_direction_next_cycle_silent():
    """Two consecutive UP observations → no alert (no flip)."""
    watchdog, admin, free = _make_watchdog()
    session_up = _make_session_response(_klines_with_last_close(105.0))
    await watchdog._check_regime_shift("BTCUSDT", session_up)  # baseline
    admin.reset_mock()
    free.reset_mock()
    await watchdog._check_regime_shift("BTCUSDT", session_up)  # same direction
    admin.assert_not_awaited()
    free.assert_not_awaited()


# ---------------------------------------------------------------------------
# Flip → alert
# ---------------------------------------------------------------------------


async def test_up_to_down_flip_alerts_high_severity():
    """UP → DOWN flip emits HIGH-severity alert to admin and free."""
    watchdog, admin, free = _make_watchdog()
    session_up = _make_session_response(_klines_with_last_close(105.0))
    session_down = _make_session_response(_klines_with_last_close(95.0))
    await watchdog._check_regime_shift("BTCUSDT", session_up)  # baseline UP
    await watchdog._check_regime_shift("BTCUSDT", session_down)  # flip DOWN
    admin.assert_awaited_once()
    free.assert_awaited_once()
    msg = admin.call_args.args[0]
    assert "BTC regime shift" in msg
    assert "UP → DOWN" in msg
    assert "*Severity:* HIGH" in msg
    assert "📉" in msg


async def test_down_to_up_flip_uses_up_emoji():
    """DOWN → UP flip uses the up emoji and label."""
    watchdog, admin, free = _make_watchdog()
    session_down = _make_session_response(_klines_with_last_close(95.0))
    session_up = _make_session_response(_klines_with_last_close(105.0))
    await watchdog._check_regime_shift("ETHUSDT", session_down)  # baseline
    await watchdog._check_regime_shift("ETHUSDT", session_up)
    admin.assert_awaited_once()
    msg = admin.call_args.args[0]
    assert "ETH regime shift" in msg
    assert "DOWN → UP" in msg
    assert "📈" in msg


# ---------------------------------------------------------------------------
# Cooldown
# ---------------------------------------------------------------------------


async def test_per_symbol_cooldown_isolates_btc_and_eth():
    """A flip on BTC must not silence a flip on ETH."""
    watchdog, admin, free = _make_watchdog()
    sess_up = _make_session_response(_klines_with_last_close(105.0))
    sess_down = _make_session_response(_klines_with_last_close(95.0))
    # BTC flip
    await watchdog._check_regime_shift("BTCUSDT", sess_up)
    await watchdog._check_regime_shift("BTCUSDT", sess_down)
    assert admin.await_count == 1
    # ETH flip — independent symbol → independent cooldown
    await watchdog._check_regime_shift("ETHUSDT", sess_up)
    await watchdog._check_regime_shift("ETHUSDT", sess_down)
    assert admin.await_count == 2


async def test_cooldown_blocks_rapid_re_flip():
    """A second flip within the cooldown window is suppressed."""
    watchdog, admin, free = _make_watchdog()
    sess_up = _make_session_response(_klines_with_last_close(105.0))
    sess_down = _make_session_response(_klines_with_last_close(95.0))
    await watchdog._check_regime_shift("BTCUSDT", sess_up)  # baseline
    await watchdog._check_regime_shift("BTCUSDT", sess_down)  # flip 1 → alert
    assert admin.await_count == 1
    # Re-flip back UP within cooldown window → suppressed
    await watchdog._check_regime_shift("BTCUSDT", sess_up)
    assert admin.await_count == 1


# ---------------------------------------------------------------------------
# Resilience
# ---------------------------------------------------------------------------


async def test_http_non_200_silent():
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([], status=503)
    await watchdog._check_regime_shift("BTCUSDT", session)  # must not raise
    admin.assert_not_awaited()
    assert "BTCUSDT" not in watchdog._regime_last_direction


async def test_short_payload_silent():
    """<22 candles → silent skip (insufficient data for EMA21)."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(100.0) for _ in range(10)])
    await watchdog._check_regime_shift("BTCUSDT", session)
    admin.assert_not_awaited()
    assert "BTCUSDT" not in watchdog._regime_last_direction


async def test_zero_close_silent():
    """Any close ≤ 0 in payload → silent skip (corrupt data)."""
    watchdog, admin, free = _make_watchdog()
    bad = _klines_with_last_close(105.0)
    bad[5] = _kline(0.0)  # corrupt one candle
    session = _make_session_response(bad)
    await watchdog._check_regime_shift("BTCUSDT", session)
    admin.assert_not_awaited()


async def test_timeout_silent():
    watchdog, admin, free = _make_watchdog()
    response_cm = MagicMock()
    response_cm.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError())
    response_cm.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=response_cm)
    await watchdog._check_regime_shift("BTCUSDT", session)  # must not raise
    admin.assert_not_awaited()


# ---------------------------------------------------------------------------
# Wiring — feature flag
# ---------------------------------------------------------------------------


async def test_disabled_skips_check_in_cycle():
    """When MACRO_REGIME_SHIFT_ENABLED is False, _check_macro_events skips it."""
    watchdog, admin, free = _make_watchdog()
    # Stub all the inner checks so we only observe whether _check_regime_shift fires
    watchdog._get_session = AsyncMock(return_value=MagicMock(spec=aiohttp.ClientSession))
    watchdog._check_fear_greed = AsyncMock()
    watchdog._check_btc_price_move = AsyncMock()
    watchdog._check_news = AsyncMock()
    watchdog._check_regime_shift = AsyncMock()

    with patch("src.macro_watchdog.MACRO_REGIME_SHIFT_ENABLED", False):
        await watchdog._check_macro_events()
    watchdog._check_regime_shift.assert_not_awaited()


async def test_enabled_fires_for_btc_and_eth_in_cycle():
    """When enabled, the cycle calls _check_regime_shift once per BTC and ETH."""
    watchdog, admin, free = _make_watchdog()
    watchdog._get_session = AsyncMock(return_value=MagicMock(spec=aiohttp.ClientSession))
    watchdog._check_fear_greed = AsyncMock()
    watchdog._check_btc_price_move = AsyncMock()
    watchdog._check_news = AsyncMock()
    watchdog._check_regime_shift = AsyncMock()

    with patch("src.macro_watchdog.MACRO_REGIME_SHIFT_ENABLED", True):
        await watchdog._check_macro_events()
    symbols_called = [c.args[0] for c in watchdog._check_regime_shift.await_args_list]
    assert "BTCUSDT" in symbols_called
    assert "ETHUSDT" in symbols_called
