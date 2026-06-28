"""All-market array streams (!ticker@arr) must be exempt from per-symbol
staleness, or the watchdog force-closes the mover-ignition connection forever.

Regression for the live 2026-06-28 bug: `!ticker@arr` → head `!ticker` →
`last_kline_age_seconds("!TICKER", "1m")` returns None → counted permanently
stale → `_check_per_symbol_staleness` force-closes every cycle, starving the
ignition detector (zero mover promotions).
"""
from __future__ import annotations

from src.websocket_manager import WSConnection, WebSocketManager

# Fixed monotonic-style stamps: connection opened at t=1000, checked at t=1200
# → 200 s old, past the 120 s min-conn-age guard, and positive so the
# ``connected_ts > 0`` filter keeps it in scope.
_CONNECTED_TS = 1000.0
_NOW = 1200.0


class _Store:
    """last_kline_age_seconds: None for unknown symbols, huge for known-stale."""

    def __init__(self, ages):
        self._ages = ages

    def last_kline_age_seconds(self, symbol, tf):
        return self._ages.get(symbol.upper())


class _WS:
    def __init__(self):
        self.closed = False
        self.close_calls = 0

    async def close(self):
        self.close_calls += 1
        self.closed = True


def _mgr_with_streams(store, streams, ws):
    m = WebSocketManager(lambda *_: None, market="futures", data_store=store)
    m._connections = [
        WSConnection(streams=streams, last_pong=_CONNECTED_TS, ws=ws, connected_ts=_CONNECTED_TS)
    ]
    return m


async def test_array_stream_not_force_closed_when_only_stream():
    # Only !ticker@arr subscribed; its head has no candle (age None). With the
    # fix it is excluded → no symbols → early return → connection untouched.
    ws = _WS()
    m = _mgr_with_streams(_Store({}), ["!ticker@arr"], ws)
    await m._check_per_symbol_staleness(_NOW)
    assert ws.close_calls == 0


async def test_real_stale_kline_symbol_still_force_closes():
    # Control: a genuine per-symbol kline stream that is stale must still trip
    # (proves the test harness can observe a force-close at all).
    ws = _WS()
    m = _mgr_with_streams(_Store({"BTCUSDT": 9_999.0}), ["btcusdt@kline_1m"], ws)
    await m._check_per_symbol_staleness(_NOW)
    assert ws.close_calls == 1


async def test_array_stream_mixed_with_klines_only_klines_counted():
    # A mover stream alongside a FRESH kline: the array stream is ignored, the
    # fresh kline keeps the connection alive (not force-closed).
    ws = _WS()
    m = _mgr_with_streams(_Store({"BTCUSDT": 1.0}), ["btcusdt@kline_1m", "!ticker@arr"], ws)
    await m._check_per_symbol_staleness(_NOW)
    assert ws.close_calls == 0
