"""Tests for src/macro_watchdog._check_btc_price_move — the Phase-2 BTC big-move alert.

Verifies:
* Threshold respected (below → silent, at/above → alert)
* Severity classification (HIGH vs CRITICAL)
* Cooldown is per-direction (UP doesn't suppress DOWN and vice versa)
* HTTP errors degrade silently (do not raise)
* Routes via `_broadcast` (admin + free for HIGH/CRITICAL)
"""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from src.macro_watchdog import MacroWatchdog


def _kline(close_price: float) -> list:
    """Minimal Binance kline shape: [open_time, o, h, l, c, v, close_time, ...]."""
    return [0, "0", "0", "0", str(close_price), "0", 0, "0", 0, "0", "0", "0"]


def _make_session_response(klines: list, status: int = 200):
    """Build a mock aiohttp session whose `.get(...).__aenter__` yields a
    response with `.status` and `.json()` returning the kline payload."""
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
    watchdog = MacroWatchdog(send_alert=admin, send_to_free=free)
    return watchdog, admin, free


# ---------------------------------------------------------------------------
# Threshold + severity classification
# ---------------------------------------------------------------------------


async def test_below_threshold_no_alert():
    """BTC move under ±3% must produce zero alerts."""
    watchdog, admin, free = _make_watchdog()
    # 100 → 102 = +2.0% (below 3.0 threshold)
    session = _make_session_response([_kline(100.0), _kline(102.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_not_awaited()
    free.assert_not_awaited()


async def test_at_threshold_high_severity_routes_to_both():
    """+3.0% (exactly at threshold) → HIGH severity → admin AND free."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(100.0), _kline(103.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_awaited_once()
    free.assert_awaited_once()
    msg = admin.call_args.args[0]
    assert "🚀" in msg
    assert "UP 3.00%" in msg
    assert "*Severity:* HIGH" in msg


async def test_strong_move_classified_critical():
    """+6.0% → CRITICAL severity (≥5% threshold)."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(100.0), _kline(106.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_awaited_once()
    free.assert_awaited_once()
    msg = admin.call_args.args[0]
    assert "*Severity:* CRITICAL" in msg


async def test_down_move_uses_down_emoji_and_label():
    """-4.0% → 📉 emoji, DOWN label, HIGH severity."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(100.0), _kline(96.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_awaited_once()
    msg = admin.call_args.args[0]
    assert "📉" in msg
    assert "DOWN 4.00%" in msg
    assert "*Severity:* HIGH" in msg


# ---------------------------------------------------------------------------
# Cooldown — per-direction
# ---------------------------------------------------------------------------


async def test_same_direction_within_cooldown_suppressed():
    """A second UP alert within the cooldown window is suppressed."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(100.0), _kline(104.0)])
    await watchdog._check_btc_price_move(session)
    assert admin.await_count == 1
    # Second call immediately after — should be suppressed
    await watchdog._check_btc_price_move(session)
    assert admin.await_count == 1


async def test_opposite_direction_alerts_independently():
    """An UP alert does NOT suppress a subsequent DOWN alert (legitimate
    reversals deserve their own announcement)."""
    watchdog, admin, free = _make_watchdog()
    # First: UP alert
    up_session = _make_session_response([_kline(100.0), _kline(104.0)])
    await watchdog._check_btc_price_move(up_session)
    assert admin.await_count == 1
    # Then: DOWN alert (different direction → no cooldown)
    down_session = _make_session_response([_kline(100.0), _kline(96.0)])
    await watchdog._check_btc_price_move(down_session)
    assert admin.await_count == 2


# ---------------------------------------------------------------------------
# Network resilience
# ---------------------------------------------------------------------------


async def test_http_non_200_silent():
    """Non-200 status → silent skip (no alert, no exception)."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([], status=503)
    await watchdog._check_btc_price_move(session)  # must not raise
    admin.assert_not_awaited()


async def test_short_payload_silent():
    """Klines payload with <2 candles → silent skip."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(100.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_not_awaited()


async def test_zero_prev_close_silent():
    """prev_close of 0 → silent skip (avoids division by zero)."""
    watchdog, admin, free = _make_watchdog()
    session = _make_session_response([_kline(0.0), _kline(100.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_not_awaited()


async def test_timeout_silent():
    """aiohttp timeout → caught + logged + silent skip."""
    watchdog, admin, free = _make_watchdog()
    response_cm = MagicMock()
    import asyncio as _asyncio
    response_cm.__aenter__ = AsyncMock(side_effect=_asyncio.TimeoutError())
    response_cm.__aexit__ = AsyncMock(return_value=False)
    session = MagicMock(spec=aiohttp.ClientSession)
    session.get = MagicMock(return_value=response_cm)
    await watchdog._check_btc_price_move(session)  # must not raise
    admin.assert_not_awaited()


# ---------------------------------------------------------------------------
# Free-channel routing (relies on _broadcast — already tested in
# test_macro_watchdog_routing.py — but verify integration here)
# ---------------------------------------------------------------------------


async def test_btc_move_alert_skips_free_when_no_callable():
    """Backwards compat: legacy `send_to_free=None` still alerts admin only."""
    admin = AsyncMock(return_value=True)
    watchdog = MacroWatchdog(send_alert=admin, send_to_free=None)
    session = _make_session_response([_kline(100.0), _kline(105.0)])
    await watchdog._check_btc_price_move(session)
    admin.assert_awaited_once()
