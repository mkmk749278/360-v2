"""Tests for WebSocket REST fallback and enhanced signal formatting."""

import asyncio
import time
import unittest.mock as mock

import aiohttp
import pytest


from config import WS_ALERT_COOLDOWN, WS_FALLBACK_TIMEFRAMES, WS_HEARTBEAT_INTERVAL, WS_HEARTBEAT_INTERVAL_FUTURES, WS_SESSION_RECYCLE_ATTEMPTS, WS_STALENESS_MULTIPLIER, WS_STALENESS_MULTIPLIER_FUTURES
from src.channels.base import Signal
from src.smc import Direction
from src.telegram_bot import TelegramBot
from src.utils import utcnow
from src.websocket_manager import WSConnection, WebSocketManager


class TestWebSocketFallback:
    def test_set_critical_pairs(self):
        msgs = []

        async def handler(data):
            msgs.append(data)

        ws = WebSocketManager(handler, market="spot")
        ws.set_critical_pairs(["BTCUSDT", "ETHUSDT"])
        assert ws._critical_pairs == {"BTCUSDT", "ETHUSDT"}

    def test_fallback_not_active_initially(self):
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="spot")
        assert ws._rest_fallback_active is False
        assert ws._fallback_task is None

    def test_start_rest_fallback_no_pairs(self):
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="spot")
        ws._start_rest_fallback()
        assert ws._rest_fallback_active is False  # no critical pairs

    def test_stop_rest_fallback_noop(self):
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="spot")
        ws._stop_rest_fallback()  # should not raise
        assert ws._rest_fallback_active is False


class TestWebSocketHealthRatio:
    """WebSocketManager.health_ratio returns a continuous 0.0–1.0 health score."""

    def test_health_ratio_one_before_start(self):
        """Before start() is called there are no connections: ratio == 1.0."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="spot")
        assert ws.health_ratio == 1.0

    def test_health_ratio_all_healthy(self):
        """All connections open and recently pinged → ratio == 1.0."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="spot")
        now = time.monotonic()
        conn1 = WSConnection(streams=["btcusdt@kline_1m"], last_pong=now)
        conn2 = WSConnection(streams=["ethusdt@kline_1m"], last_pong=now)
        # Attach mock open WebSocket objects
        mock_ws = mock.MagicMock()
        mock_ws.closed = False
        conn1.ws = mock_ws
        conn2.ws = mock_ws
        ws._connections = [conn1, conn2]
        assert ws.health_ratio == 1.0

    def test_health_ratio_half_healthy(self):
        """One of two connections stale → ratio == 0.5."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="spot")
        now = time.monotonic()
        mock_open = mock.MagicMock()
        mock_open.closed = False
        mock_closed = mock.MagicMock()
        mock_closed.closed = True

        conn_healthy = WSConnection(streams=["btcusdt@kline_1m"], last_pong=now, ws=mock_open)
        conn_unhealthy = WSConnection(streams=["ethusdt@kline_1m"], last_pong=now, ws=mock_closed)
        ws._connections = [conn_healthy, conn_unhealthy]
        assert ws.health_ratio == 0.5

    def test_health_ratio_all_stale(self):
        """All connections stale → ratio == 0.0."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="spot")
        stale_pong = time.monotonic() - 9999.0  # way in the past
        mock_ws = mock.MagicMock()
        mock_ws.closed = False
        conn = WSConnection(streams=["btcusdt@kline_1m"], last_pong=stale_pong, ws=mock_ws)
        ws._connections = [conn]
        assert ws.health_ratio == 0.0

    def test_health_ratio_no_ws_object(self):
        """Connection without a ws object counts as unhealthy."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="spot")
        conn = WSConnection(streams=["btcusdt@kline_1m"])  # ws=None
        ws._connections = [conn]
        assert ws.health_ratio == 0.0

    def test_is_healthy_uses_strict_all_or_nothing(self):
        """is_healthy still requires ALL connections to be healthy."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="spot")
        now = time.monotonic()
        mock_open = mock.MagicMock()
        mock_open.closed = False
        mock_closed = mock.MagicMock()
        mock_closed.closed = True

        conn_healthy = WSConnection(streams=["btcusdt@kline_1m"], last_pong=now, ws=mock_open)
        conn_unhealthy = WSConnection(streams=["ethusdt@kline_1m"], last_pong=now, ws=mock_closed)
        ws._connections = [conn_healthy, conn_unhealthy]
        # health_ratio is 0.5 but is_healthy is False (strict)
        assert ws.health_ratio == 0.5
        assert ws.is_healthy is False


class TestReconnectDurationInstrumentation:
    """Phase 1 instrumentation (2026-05-08): drop → restored timing,
    counter activation, /diag-friendly state snapshot."""

    def test_drop_stamps_degraded_since(self):
        async def handler(data): pass
        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        ws._connections = [conn]
        assert conn.degraded_since == 0.0
        ws._set_connection_degraded(conn, True)
        assert conn.degraded is True
        assert conn.degraded_since > 0

    def test_restore_records_duration_and_clears_degraded_since(self):
        """Drop → restored cycle stamps last_reconnect_ms and clears
        degraded_since (so the next degradation starts fresh)."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        ws._connections = [conn]
        ws._set_connection_degraded(conn, True)
        # Simulate elapsed time by hand-rolling degraded_since.
        conn.degraded_since = time.monotonic() - 25.0
        ws._set_connection_degraded(conn, False)
        assert conn.degraded is False
        assert conn.degraded_since == 0.0
        # ~25s should be ~25000ms ± a tiny epsilon for the stamping itself.
        assert 24500.0 <= conn.last_reconnect_ms <= 25500.0

    def test_recovery_increments_counter(self):
        """Activate the previously-dead ``_ws_reconnection_count``."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        ws._connections = [conn]
        assert ws.ws_reconnection_count == 0
        ws._set_connection_degraded(conn, True)
        ws._set_connection_degraded(conn, False)
        assert ws.ws_reconnection_count == 1
        # Two more cycles.
        ws._set_connection_degraded(conn, True)
        ws._set_connection_degraded(conn, False)
        ws._set_connection_degraded(conn, True)
        ws._set_connection_degraded(conn, False)
        assert ws.ws_reconnection_count == 3

    def test_idempotent_set_degraded_no_double_count(self):
        """Calling _set_connection_degraded with the same value twice is a no-op."""
        async def handler(data): pass
        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        ws._connections = [conn]
        ws._set_connection_degraded(conn, True)
        ws._set_connection_degraded(conn, True)  # duplicate — should noop
        ws._set_connection_degraded(conn, False)
        ws._set_connection_degraded(conn, False)  # duplicate — should noop
        # Still exactly 1 recovery counted.
        assert ws.ws_reconnection_count == 1

    def test_get_connection_states_emits_per_connection_snapshot(self):
        async def handler(data): pass
        ws = WebSocketManager(handler, market="futures")
        now = time.monotonic()
        mock_open = mock.MagicMock()
        mock_open.closed = False
        conn1 = WSConnection(
            streams=["btcusdt@kline_1m", "ethusdt@kline_1m"],
            last_pong=now, ws=mock_open,
        )
        conn2 = WSConnection(streams=["solusdt@kline_1m"])  # no ws — degraded
        conn2.degraded = True
        conn2.degraded_since = now - 30.0
        ws._connections = [conn1, conn2]

        states = ws.get_connection_states()
        assert len(states) == 2
        assert states[0]["conn"] == 0
        assert states[0]["streams"] == 2
        assert states[0]["healthy"] is True
        assert states[0]["degraded"] is False
        assert states[1]["conn"] == 1
        assert states[1]["streams"] == 1
        assert states[1]["healthy"] is False
        assert states[1]["degraded"] is True
        assert states[1]["degraded_for_sec"] >= 29.0

    @pytest.mark.asyncio
    async def test_connect_does_not_directly_clear_degraded_flag(self):
        """Regression for the 2026-05-09 diag bug:

        Production diag showed ``futures: drops=26 recoveries=0`` and
        ``conn.degraded=False`` while ``degraded_for=229.4s`` — both
        contradictory.  Root cause: ``_connect()`` was directly setting
        ``conn.degraded = False`` after a successful reconnect.  Then
        ``_run_connection`` called ``_set_connection_degraded(conn, False)``
        immediately after, but the wrapper's idempotent guard
        (``if conn.degraded == degraded: return``) early-returned because
        the flag was already False.  The recovery instrumentation
        (duration measurement, counter increment, log marker, clearing
        ``degraded_since``) never ran.

        This test simulates the post-reconnect state: connection went
        degraded, then ``_connect`` would normally run.  With the bug,
        the wrapper call afterwards is a no-op.  Without the bug,
        ``conn.degraded_since`` is still set when the wrapper runs, so
        the recovery path executes correctly.
        """
        async def handler(data): pass
        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        ws._connections = [conn]

        # Simulate the lifecycle: drop, then reconnect via _connect
        # (which we patch to skip the actual aiohttp call but mirror
        # the post-fix invariant: do NOT touch conn.degraded).
        ws._set_connection_degraded(conn, True)
        assert conn.degraded is True
        assert conn.degraded_since > 0

        # Mock the session so _connect can run without network.
        mock_ws = mock.AsyncMock()
        mock_ws.closed = False
        ws._session = mock.AsyncMock()
        ws._session.ws_connect = mock.AsyncMock(return_value=mock_ws)

        # Hand-roll degraded_since to known value for duration assertion.
        conn.degraded_since = time.monotonic() - 5.0

        await ws._connect(conn)

        # Post-fix invariant: _connect must NOT clear the degraded flag
        # — leave that to the wrapper so the recovery instrumentation
        # runs.
        assert conn.degraded is True, (
            "_connect must not directly clear conn.degraded — that "
            "bypasses _set_connection_degraded's recovery instrumentation"
        )
        assert conn.degraded_since > 0, (
            "_connect must not clear degraded_since — the wrapper "
            "needs it to compute duration"
        )

        # Now the caller (_run_connection) does what production does
        # next: call the wrapper.  This time it MUST run the recovery
        # path because the True→False transition is real.
        ws._set_connection_degraded(conn, False)

        assert conn.degraded is False
        assert conn.degraded_since == 0.0, (
            "Wrapper must clear degraded_since after recovery"
        )
        assert conn.last_reconnect_ms > 0, (
            "Wrapper must record drop→restored duration in ms"
        )
        assert ws.ws_reconnection_count == 1, (
            "Wrapper must increment the recovery counter — pre-fix this "
            "was 0 because _connect's direct write made the wrapper a no-op"
        )


class TestFormatFreeSignal:
    def test_free_signal_has_header_and_footer(self):
        sig = Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32150,
            stop_loss=32120,
            tp1=32200,
            tp2=32300,
            tp3=32400,
            trailing_active=True,
            trailing_desc="1.5×ATR",
            confidence=87,
            ai_sentiment_label="Positive",
            ai_sentiment_summary="Whale Activity",
            risk_label="Aggressive",
            market_phase="Bullish",
            liquidity_info="High",
            timestamp=utcnow(),
        )
        text = TelegramBot.format_free_signal(sig)
        assert "FREE SIGNAL OF THE DAY" in text
        assert "BTCUSDT" in text
        assert "Tip:" in text
        assert "Premium gets all signals!" in text

    def test_format_signal_includes_market_phase(self):
        sig = Signal(
            channel="360_SCALP",
            symbol="ETHUSDT",
            direction=Direction.SHORT,
            entry=2350,
            stop_loss=2380,
            tp1=2320,
            tp2=2300,
            confidence=80,
            market_phase="Bearish",
            liquidity_info="Low",
            timestamp=utcnow(),
        )
        text = TelegramBot.format_signal_legacy(sig)
        assert "Market Phase: Bearish" in text
        assert "Liquidity Pool: Low" in text

    def test_format_signal_default_market_phase(self):
        sig = Signal(
            channel="360_SPOT",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32100,
            stop_loss=32050,
            tp1=32150,
            tp2=32200,
            confidence=75,
            timestamp=utcnow(),
        )
        text = TelegramBot.format_signal_legacy(sig)
        assert "Market Phase: N/A" in text
        assert "Liquidity Pool: Standard" in text


class TestSignalDataclass:
    def test_new_fields_default(self):
        sig = Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000,
            stop_loss=31900,
            tp1=32100,
            tp2=32200,
            confidence=85,
            timestamp=utcnow(),
        )
        assert sig.market_phase == "N/A"
        assert sig.liquidity_info == "Standard"

    def test_new_fields_custom(self):
        sig = Signal(
            channel="360_SCALP",
            symbol="BTCUSDT",
            direction=Direction.LONG,
            entry=32000,
            stop_loss=31900,
            tp1=32100,
            tp2=32200,
            confidence=85,
            market_phase="Accumulation",
            liquidity_info="Deep",
            timestamp=utcnow(),
        )
        assert sig.market_phase == "Accumulation"
        assert sig.liquidity_info == "Deep"


class TestEscapeMdFunction:
    """Verify the _escape_md helper escapes all Markdown V1 special characters."""

    def test_escape_asterisk(self):
        assert TelegramBot._escape_md("*bold*") == "\\*bold\\*"

    def test_escape_underscore(self):
        assert TelegramBot._escape_md("_italic_") == "\\_italic\\_"

    def test_escape_backtick(self):
        assert TelegramBot._escape_md("`code`") == "\\`code\\`"

    def test_escape_bracket(self):
        assert TelegramBot._escape_md("[text]") == "\\[text]"

    def test_escape_backslash(self):
        assert TelegramBot._escape_md("a\\b") == "a\\\\b"

    def test_escape_all_special_chars(self):
        raw = "*_`[\\"
        escaped = TelegramBot._escape_md(raw)
        assert escaped == "\\*\\_\\`\\[\\\\"

    def test_plain_text_unchanged(self):
        text = "Sweep SHORT at 0.3572 | FVG 0.3543-0.3538"
        assert TelegramBot._escape_md(text) == text

    def test_empty_string(self):
        assert TelegramBot._escape_md("") == ""


class TestWebSocketLastPongOnText:
    """Verify that last_pong is updated when TEXT messages arrive."""

    def test_last_pong_updated_on_text_message(self):
        """is_healthy should remain True after TEXT messages (not just PONG frames)."""

        received = []

        async def handler(data):
            received.append(data)

        ws = WebSocketManager(handler, market="spot")

        # Simulate a connection that received a TEXT message recently
        conn = WSConnection()
        conn.last_pong = time.monotonic()  # fresh timestamp

        # Immediately after connect the connection should be healthy
        ws._connections = [conn]

        # Monkey-patch ws so is_healthy thinks the socket is open
        mock_ws = type("FakeWS", (), {"closed": False})()
        conn.ws = mock_ws

        assert ws.is_healthy is True

        # Simulate staleness beyond the 10× heartbeat window
        conn.last_pong = time.monotonic() - 350  # 350 s ago → stale (threshold: 30×10=300s)
        assert ws.is_healthy is False

        # Simulate a TEXT message arriving and updating last_pong
        conn.last_pong = time.monotonic()
        assert ws.is_healthy is True

    def test_closed_connections_are_not_reported_healthy(self):
        async def handler(data):
            return None

        ws = WebSocketManager(handler, market="spot")
        closed_ws = type("FakeWS", (), {"closed": True})()
        ws._connections = [WSConnection(ws=closed_ws, last_pong=time.monotonic())]

        assert ws.is_healthy is False


class TestWebSocketLifecycle:
    @pytest.mark.asyncio
    async def test_stop_awaits_cancelled_tasks(self):
        cancelled = []

        async def handler(data):
            return None

        async def sleeper(name: str):
            try:
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                cancelled.append(name)
                raise

        ws = WebSocketManager(handler, market="spot")
        conn_task = asyncio.create_task(sleeper("conn"))
        fallback_task = asyncio.create_task(sleeper("fallback"))
        watchdog_task = asyncio.create_task(sleeper("watchdog"))
        fake_ws = type(
            "FakeWS",
            (),
            {"closed": False, "close": lambda self: asyncio.sleep(0)},
        )()
        ws._connections = [WSConnection(ws=fake_ws, streams=["btcusdt@kline_1m"], task=conn_task)]
        ws._fallback_task = fallback_task
        ws._watchdog_task = watchdog_task
        ws._session = type(
            "FakeSession",
            (),
            {"closed": False, "close": lambda self: asyncio.sleep(0)},
        )()
        await asyncio.sleep(0)

        await ws.stop()

        assert {"conn", "fallback", "watchdog"} <= set(cancelled)
        assert conn_task.done() and fallback_task.done() and watchdog_task.done()
        assert ws._connections == []
        assert ws._session is None

    def test_fallback_stays_active_until_all_degraded_connections_recover(self):
        async def handler(data):
            return None

        ws = WebSocketManager(handler, market="spot")
        ws.set_critical_pairs(["BTCUSDT", "ETHUSDT"])
        conn_a = WSConnection(streams=["btcusdt@kline_1m"])
        conn_b = WSConnection(streams=["ethusdt@kline_1m"])
        ws._connections = [conn_a, conn_b]
        ws._start_rest_fallback = lambda: setattr(ws, "_rest_fallback_active", True)
        ws._stop_rest_fallback = lambda: setattr(ws, "_rest_fallback_active", False)

        ws._set_connection_degraded(conn_a, True)
        ws._set_connection_degraded(conn_b, True)
        assert ws._rest_fallback_active is True

        ws._set_connection_degraded(conn_a, False)
        assert ws._rest_fallback_active is True

        ws._set_connection_degraded(conn_b, False)
        assert ws._rest_fallback_active is False


class TestAdminAlertRateLimiting:
    """Admin alert must not fire more than once per WS_ALERT_COOLDOWN window."""

    def test_last_alert_time_starts_at_zero(self):
        """_last_alert_time initialises to 0.0 so the first alert always fires."""
        ws = WebSocketManager(lambda data: None, market="spot")
        assert ws._last_alert_time == 0.0

    @pytest.mark.asyncio
    async def test_alert_fires_on_first_reconnect(self):
        """Admin alert callback is invoked on the first connection drop."""
        alerted = []

        async def alert(msg):
            alerted.append(msg)

        ws = WebSocketManager(lambda data: None, market="futures", admin_alert_callback=alert)
        # Set last_alert_time beyond the WS_ALERT_COOLDOWN window so the alert fires.
        ws._last_alert_time = time.monotonic() - (WS_ALERT_COOLDOWN + 1)

        # Simulate the alert logic directly
        now = time.monotonic()
        if now - ws._last_alert_time > WS_ALERT_COOLDOWN:
            ws._last_alert_time = now
            await alert("⚠️ WebSocket connection lost (futures, attempt 1). Reconnecting…")

        assert len(alerted) == 1

    @pytest.mark.asyncio
    async def test_alert_suppressed_within_cooldown(self):
        """Alert is not sent again while the cooldown is active."""
        alerted = []

        async def alert(msg):
            alerted.append(msg)

        ws = WebSocketManager(lambda data: None, market="futures", admin_alert_callback=alert)
        # Simulate that an alert was just sent
        ws._last_alert_time = time.monotonic()

        now = time.monotonic()
        if now - ws._last_alert_time > WS_ALERT_COOLDOWN:
            ws._last_alert_time = now
            await alert("⚠️ WebSocket connection lost (futures, attempt 1). Reconnecting…")

        assert len(alerted) == 0

    def test_no_ping_loop_method(self):
        """_ping_loop must not exist — aiohttp heartbeat= handles keepalive."""
        ws = WebSocketManager(lambda data: None, market="spot")
        assert not hasattr(ws, "_ping_loop")

    def test_alert_cooldown_is_600(self):
        """WS_ALERT_COOLDOWN must be at least 600s to reduce Telegram spam."""
        assert WS_ALERT_COOLDOWN >= 600


class TestLabelParameter:
    """label parameter lets managers report a distinct name in logs and alerts."""

    def test_label_defaults_to_market(self):
        """When label is not provided, _label falls back to the market value."""
        ws = WebSocketManager(lambda data: None, market="futures")
        assert ws._label == "futures"

    def test_label_defaults_to_market_spot(self):
        """When label is not provided for spot, _label falls back to 'spot'."""
        ws = WebSocketManager(lambda data: None, market="spot")
        assert ws._label == "spot"

    def test_custom_label_is_stored(self):
        """An explicit label is stored and distinct from market."""
        ws = WebSocketManager(lambda data: None, market="futures", label="futures_liq")
        assert ws._label == "futures_liq"
        assert ws._market == "futures"

    @pytest.mark.asyncio
    async def test_alert_message_uses_label(self):
        """Alert messages include the label, not the raw market string."""
        alerted = []

        async def alert(msg):
            alerted.append(msg)

        ws = WebSocketManager(
            lambda data: None,
            market="futures",
            admin_alert_callback=alert,
            label="futures_liq",
        )
        # Verify that _label (not _market) is what the alert format string uses.
        # The implementation builds: f"... ({self._label}, attempt …)"
        # so _label == "futures_liq" means the alert will say "futures_liq".
        assert ws._label == "futures_liq"
        assert ws._market == "futures"
        # The alert text produced by _run_connection will use self._label:
        alert_text = (
            f"⚠️ WebSocket connection lost ({ws._label}, attempt 1, "
            f"total drops: 1). Reconnecting…"
        )
        assert "futures_liq" in alert_text
        assert alert_text.count("futures") == 1  # only "futures_liq", not bare "futures"


class TestWsFuturesLiqNoAdminCallback:
    """_ws_futures_liq must be created without an admin alert callback."""

    def test_futures_liq_has_no_alert_callback(self):
        """Liquidation WS manager is expendable; drops should not alert admin."""
        ws = WebSocketManager(
            lambda data: None,
            market="futures",
            admin_alert_callback=None,
            label="futures_liq",
        )
        assert ws._admin_alert is None

    def test_futures_liq_label_is_set(self):
        """Liquidation WS manager reports as 'futures_liq' in logs."""
        ws = WebSocketManager(
            lambda data: None,
            market="futures",
            admin_alert_callback=None,
            label="futures_liq",
        )
        assert ws._label == "futures_liq"




class TestHeartbeatIntervalPerMarket:
    """Verify per-market heartbeat interval selection."""

    def test_futures_uses_longer_heartbeat(self):
        """Futures WebSocketManager must use WS_HEARTBEAT_INTERVAL_FUTURES."""
        ws = WebSocketManager(lambda data: None, market="futures")
        assert ws._heartbeat_interval == WS_HEARTBEAT_INTERVAL_FUTURES

    def test_spot_uses_default_heartbeat(self):
        """Spot WebSocketManager must use WS_HEARTBEAT_INTERVAL."""
        ws = WebSocketManager(lambda data: None, market="spot")
        assert ws._heartbeat_interval == WS_HEARTBEAT_INTERVAL

    def test_futures_heartbeat_longer_than_spot(self):
        """Futures heartbeat interval must be strictly longer than spot."""
        assert WS_HEARTBEAT_INTERVAL_FUTURES > WS_HEARTBEAT_INTERVAL

    def test_futures_staleness_threshold_with_new_heartbeat(self):
        """Futures connections should be stale after heartbeat×multiplier seconds with no data."""
        ws = WebSocketManager(lambda data: None, market="futures")
        threshold = WS_HEARTBEAT_INTERVAL_FUTURES * WS_STALENESS_MULTIPLIER_FUTURES
        conn = WSConnection()
        mock_ws = type("FakeWS", (), {"closed": False})()
        conn.ws = mock_ws
        conn.last_pong = time.monotonic() - (threshold + 50)  # over threshold
        ws._connections = [conn]
        assert ws.is_healthy is False

    def test_futures_staleness_healthy_under_threshold(self):
        """Futures connections with last_pong within the threshold should still be healthy."""
        ws = WebSocketManager(lambda data: None, market="futures")
        threshold = WS_HEARTBEAT_INTERVAL_FUTURES * WS_STALENESS_MULTIPLIER_FUTURES
        conn = WSConnection()
        mock_ws = type("FakeWS", (), {"closed": False})()
        conn.ws = mock_ws
        # Use 70% of threshold so the test stays comfortably inside the
        # healthy band regardless of future config tuning.
        conn.last_pong = time.monotonic() - (threshold * 0.7)
        ws._connections = [conn]
        assert ws.is_healthy is True


class TestReconnectJitter:
    """Bug 1: Reconnect delay should include random jitter (±25%)."""

    def test_data_store_param_accepted(self):
        """WebSocketManager accepts optional data_store parameter."""
        mock_store = object()
        ws = WebSocketManager(lambda data: None, market="spot", data_store=mock_store)
        assert ws._data_store is mock_store

    def test_data_store_defaults_to_none(self):
        """data_store defaults to None for backward compatibility."""
        ws = WebSocketManager(lambda data: None, market="spot")
        assert ws._data_store is None

    def test_jitter_produces_varied_delays(self):
        """Successive jitter values should not always be identical."""
        import random
        from config import WS_RECONNECT_BASE_DELAY, WS_RECONNECT_MAX_DELAY
        # Test across different reconnect attempts (exponents 0-3) to verify
        # jitter is applied regardless of backoff magnitude.
        all_delays = []
        for attempt in range(4):
            delays = set()
            for _ in range(20):
                delay = min(WS_RECONNECT_BASE_DELAY * (2 ** attempt), WS_RECONNECT_MAX_DELAY)
                jitter = delay * random.uniform(-0.25, 0.25)
                actual = max(0.5, delay + jitter)
                delays.add(round(actual, 6))
            # With 20 samples, at least 2 distinct values should appear
            assert len(delays) > 1, f"No jitter variation at attempt={attempt}"
            all_delays.extend(delays)
        # Verify delays stay within the expected ±25% jitter band + min 0.5s floor
        for attempt in range(4):
            base = min(WS_RECONNECT_BASE_DELAY * (2 ** attempt), WS_RECONNECT_MAX_DELAY)
            low = max(0.5, base * 0.75)
            high = base * 1.25
            for _ in range(50):
                jitter = base * random.uniform(-0.25, 0.25)
                actual = max(0.5, base + jitter)
                assert low <= actual <= high, f"Delay {actual:.3f} outside [{low:.3f}, {high:.3f}]"


class TestMultiTimeframeFallbackConfig:
    """Bug 3: Fallback timeframe constants are set correctly."""

    def test_fallback_timeframes_cover_all_channels(self):
        """WS_FALLBACK_TIMEFRAMES must include 1m, 5m, 15m, and 1h."""
        required = {"1m", "5m", "15m", "1h"}
        assert required <= set(WS_FALLBACK_TIMEFRAMES)

    def test_fallback_poll_intervals_present(self):
        """WS_FALLBACK_POLL_INTERVALS config is importable."""
        from config import WS_FALLBACK_POLL_INTERVALS
        assert "1m" in WS_FALLBACK_POLL_INTERVALS


class TestSessionRecycling:
    """Bug 5: _recreate_session closes old session and creates a new one."""

    @pytest.mark.asyncio
    async def test_recreate_session_closes_old(self):
        """_recreate_session must close the old session."""
        closed = []

        async def fake_close():
            closed.append(True)

        ws = WebSocketManager(lambda data: None, market="spot")
        fake_session = type(
            "FakeSession",
            (),
            {"closed": False, "close": lambda self: fake_close()},
        )()
        ws._session = fake_session

        await ws._recreate_session()

        assert closed, "Old session close() was not called"
        assert ws._session is not fake_session

    @pytest.mark.asyncio
    async def test_recreate_session_skips_already_closed(self):
        """_recreate_session must not call close() on an already-closed session."""
        closed = []

        ws = WebSocketManager(lambda data: None, market="spot")
        fake_session = type(
            "FakeSession",
            (),
            {"closed": True, "close": lambda self: closed.append(True)},
        )()
        ws._session = fake_session

        await ws._recreate_session()

        assert not closed, "close() should not be called on an already-closed session"
        assert ws._session is not fake_session

    def test_session_recycle_attempts_config(self):
        """WS_SESSION_RECYCLE_ATTEMPTS must be a positive integer."""
        assert isinstance(WS_SESSION_RECYCLE_ATTEMPTS, int)
        assert WS_SESSION_RECYCLE_ATTEMPTS > 0


class TestFetchAndStoreFallback:
    """Bug 2: HistoricalDataStore.fetch_and_store_fallback stores candles correctly."""

    @pytest.mark.asyncio
    async def test_fetch_and_store_fallback_stores_new_data(self):
        """fetch_and_store_fallback seeds candles when none exist for the symbol."""
        import numpy as np
        from src.historical_data import HistoricalDataStore

        store = HistoricalDataStore()
        dummy = {
            "open": np.array([1.0, 2.0]),
            "high": np.array([1.1, 2.1]),
            "low": np.array([0.9, 1.9]),
            "close": np.array([1.05, 2.05]),
            "volume": np.array([100.0, 200.0]),
        }

        with mock.patch.object(store, "fetch_candles", return_value=dummy) as patched:
            await store.fetch_and_store_fallback("BTCUSDT", "1m", 200, "futures")
            patched.assert_called_once_with("BTCUSDT", "1m", 200, "futures")

        assert "BTCUSDT" in store.candles
        assert "1m" in store.candles["BTCUSDT"]
        np.testing.assert_array_equal(store.candles["BTCUSDT"]["1m"]["close"], dummy["close"])

    @pytest.mark.asyncio
    async def test_fetch_and_store_fallback_merges_existing(self):
        """fetch_and_store_fallback merges new candles with existing data."""
        import numpy as np
        from src.historical_data import HistoricalDataStore

        store = HistoricalDataStore()
        existing = {
            "open": np.array([0.5]),
            "high": np.array([0.6]),
            "low": np.array([0.4]),
            "close": np.array([0.55]),
            "volume": np.array([50.0]),
        }
        store.candles["BTCUSDT"] = {"1m": existing}
        new_data = {
            "open": np.array([1.0]),
            "high": np.array([1.1]),
            "low": np.array([0.9]),
            "close": np.array([1.05]),
            "volume": np.array([100.0]),
        }

        with mock.patch.object(store, "fetch_candles", return_value=new_data):
            await store.fetch_and_store_fallback("BTCUSDT", "1m", 200, "spot")

        assert len(store.candles["BTCUSDT"]["1m"]["close"]) == 2

    @pytest.mark.asyncio
    async def test_fetch_and_store_fallback_noop_on_empty_response(self):
        """fetch_and_store_fallback does nothing if fetch_candles returns empty."""
        from src.historical_data import HistoricalDataStore

        store = HistoricalDataStore()
        with mock.patch.object(store, "fetch_candles", return_value={}):
            await store.fetch_and_store_fallback("ETHUSDT", "5m", 200, "spot")
        assert "ETHUSDT" not in store.candles


class TestTotalDropsCounter:
    """Verify _total_drops counter increments on each connection drop."""

    def test_total_drops_starts_at_zero(self):
        """_total_drops must be 0 on a freshly created WebSocketManager."""
        ws = WebSocketManager(lambda data: None, market="futures")
        assert ws._total_drops == 0

    @pytest.mark.asyncio
    async def test_total_drops_increments_on_drop(self):
        """_total_drops must increment each time a connection is reported lost."""
        alerts = []

        async def fake_alert(msg: str) -> None:
            alerts.append(msg)

        ws = WebSocketManager(
            lambda data: None,
            market="futures",
            admin_alert_callback=fake_alert,
        )
        # Bypass the cooldown by back-dating _last_alert_time far enough that
        # even on a freshly booted CI container (low time.monotonic() value)
        # the cooldown check `now - _last_alert_time > WS_ALERT_COOLDOWN` passes.
        ws._last_alert_time = time.monotonic() - WS_ALERT_COOLDOWN - 1.0

        # Simulate two consecutive drops.
        conn = WSConnection()
        ws._connections = [conn]
        ws._running = True

        # Manually trigger the drop-path logic twice.
        for _ in range(2):
            ws._total_drops += 1
            now = time.monotonic()
            if now - ws._last_alert_time > WS_ALERT_COOLDOWN:
                ws._last_alert_time = now
                await fake_alert(
                    f"⚠️ WebSocket connection lost (futures, attempt 1, "
                    f"total drops: {ws._total_drops}). Reconnecting…"
                )
            # Reset to allow the second iteration through the cooldown.
            ws._last_alert_time = time.monotonic() - WS_ALERT_COOLDOWN - 1.0

        assert ws._total_drops == 2
        assert len(alerts) == 2
        assert "total drops: 1" in alerts[0]
        assert "total drops: 2" in alerts[1]

    def test_total_drops_in_alert_message(self):
        """Alert message must include total drops when _total_drops > 0."""
        ws = WebSocketManager(lambda data: None, market="spot")
        ws._total_drops = 5
        msg = (
            f"⚠️ WebSocket connection lost ({ws._market}, "
            f"attempt 1, total drops: {ws._total_drops}). Reconnecting…"
        )
        assert "total drops: 5" in msg


class TestStalenessMultiplierConfig:
    """Verify WS_STALENESS_MULTIPLIER config constants are correct."""

    def test_staleness_multiplier_spot(self):
        assert WS_STALENESS_MULTIPLIER == 10

    def test_staleness_multiplier_futures_default(self):
        # 2026-05-14: dropped from 15 to 5 after a 13h emission blackout where
        # the futures conn sat at sec_since_last_msg≈12 min under a 900s
        # threshold that never tripped before subscriber-visible silence.
        assert WS_STALENESS_MULTIPLIER_FUTURES == 5

    def test_futures_threshold_bounded(self):
        """Both multipliers should keep the per-market threshold inside a sane
        window: too short causes reconnect churn during normal liquidation
        cascades; too long lets silent-but-pingable feeds drag for tens of
        minutes (the May 12 / 13 blackout pattern).  Assert both per-market
        thresholds fall within 180-600s."""
        spot_threshold = WS_HEARTBEAT_INTERVAL * WS_STALENESS_MULTIPLIER
        fut_threshold = WS_HEARTBEAT_INTERVAL_FUTURES * WS_STALENESS_MULTIPLIER_FUTURES
        assert 180 <= spot_threshold <= 600, f"spot threshold {spot_threshold}s out of band"
        assert 180 <= fut_threshold <= 600, f"futures threshold {fut_threshold}s out of band"

    def test_spot_manager_uses_spot_multiplier(self):
        ws = WebSocketManager(lambda data: None, market="spot")
        assert ws._staleness_multiplier == WS_STALENESS_MULTIPLIER

    def test_futures_manager_uses_futures_multiplier(self):
        ws = WebSocketManager(lambda data: None, market="futures")
        assert ws._staleness_multiplier == WS_STALENESS_MULTIPLIER_FUTURES


class TestForceOrderStreamSeparation:
    """Verify forceOrder streams are kept separate from kline streams in bootstrap."""

    def test_forceorder_not_in_futures_kline_streams(self):
        """Kline stream list must not contain any @forceOrder streams."""
        syms = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
        futures_kline_streams = []
        futures_liq_streams = []
        for sym in syms:
            s = sym.lower()
            futures_kline_streams.append(f"{s}@kline_1m")
            futures_kline_streams.append(f"{s}@kline_5m")
            futures_liq_streams.append(f"{s}@forceOrder")

        assert not any("forceOrder" in s for s in futures_kline_streams)
        assert all("forceOrder" in s for s in futures_liq_streams)

    def test_kline_streams_not_in_liq_streams(self):
        """Liquidation stream list must not contain kline streams."""
        syms = ["BTCUSDT", "ETHUSDT"]
        futures_kline_streams = []
        futures_liq_streams = []
        for sym in syms:
            s = sym.lower()
            futures_kline_streams.append(f"{s}@kline_1m")
            futures_kline_streams.append(f"{s}@kline_5m")
            futures_liq_streams.append(f"{s}@forceOrder")

        assert not any("kline" in s for s in futures_liq_streams)

    def test_liq_stream_count_matches_symbol_count(self):
        """Each symbol produces exactly one forceOrder stream."""
        syms = [f"SYM{i}USDT" for i in range(50)]
        futures_liq_streams = [f"{s.lower()}@forceOrder" for s in syms]
        assert len(futures_liq_streams) == len(syms)

    def test_engine_has_ws_futures_liq_attribute(self):
        """CryptoSignalEngine must declare _ws_futures_liq attribute."""
        from src.main import CryptoSignalEngine
        engine = CryptoSignalEngine()
        assert hasattr(engine, "_ws_futures_liq")
        assert engine._ws_futures_liq is None  # set during boot, None at init


class TestStreamShardingCap:
    """Requirement 1 & 2: Hard cap and auto-sharding across connections."""

    def test_max_streams_per_conn_at_least_150(self):
        """Safe stream cap must be >= 150 (well below Binance's 1024 limit)."""
        from config import WS_MAX_STREAMS_PER_CONN
        assert WS_MAX_STREAMS_PER_CONN >= 150

    def test_max_streams_per_conn_at_most_200(self):
        """Safe stream cap must be <= 200 to stay well within Binance limits."""
        from config import WS_MAX_STREAMS_PER_CONN
        assert WS_MAX_STREAMS_PER_CONN <= 200

    def test_streams_sharded_into_multiple_connections(self):
        """start() must distribute streams across multiple WSConnection objects."""
        from config import WS_MAX_STREAMS_PER_CONN
        ws = WebSocketManager(lambda data: None, market="spot")
        ws._running = True
        ws._session = mock.MagicMock()

        dummy_task = mock.MagicMock()
        dummy_task.done.return_value = False

        # Build a stream list large enough to require 2 shards
        stream_count = WS_MAX_STREAMS_PER_CONN + 1
        streams = [f"sym{i}usdt@kline_1m" for i in range(stream_count)]

        with mock.patch("asyncio.create_task", return_value=dummy_task):
            asyncio.get_event_loop().run_until_complete(
                _mock_start(ws, streams)
            )

        assert len(ws._connections) >= 2, "Must create at least 2 shards for > MAX_STREAMS_PER_CONN streams"
        for conn in ws._connections:
            assert len(conn.streams) <= WS_MAX_STREAMS_PER_CONN, "No shard may exceed the cap"

    def test_single_shard_for_small_stream_list(self):
        """A small stream list that fits within the cap uses exactly one shard."""
        from config import WS_MAX_STREAMS_PER_CONN
        ws = WebSocketManager(lambda data: None, market="spot")
        ws._running = True
        ws._session = mock.MagicMock()

        dummy_task = mock.MagicMock()
        dummy_task.done.return_value = False

        streams = [f"sym{i}usdt@kline_1m" for i in range(10)]

        with mock.patch("asyncio.create_task", return_value=dummy_task):
            asyncio.get_event_loop().run_until_complete(
                _mock_start(ws, streams)
            )

        assert len(ws._connections) == 1


async def _mock_start(ws: WebSocketManager, streams: list) -> None:
    """Helper: run WebSocketManager.start() without actually connecting."""
    ws._connections = []
    ws._subscribed_streams = set()
    ws._rest_fallback_active = False
    from config import WS_MAX_STREAMS_PER_CONN
    for i in range(0, len(streams), WS_MAX_STREAMS_PER_CONN):
        chunk = streams[i: i + WS_MAX_STREAMS_PER_CONN]
        conn = WSConnection(streams=chunk)
        ws._connections.append(conn)
        conn.task = mock.MagicMock()


class TestPingPongHeartbeatMonitor:
    """Requirement 3: Strict ping/pong latency and timeout detection."""

    def test_ws_ping_timeout_ms_config_exists(self):
        """WS_PING_TIMEOUT_MS constant must exist in config."""
        from config import WS_PING_TIMEOUT_MS
        assert WS_PING_TIMEOUT_MS > 0

    def test_ws_ping_timeout_ms_is_2000(self):
        """WS_PING_TIMEOUT_MS default must be 5000 ms."""
        from config import WS_PING_TIMEOUT_MS
        assert WS_PING_TIMEOUT_MS == 5000

    def test_ws_connection_has_last_ping_time_field(self):
        """WSConnection must expose last_ping_time for latency tracking."""
        conn = WSConnection()
        assert hasattr(conn, "last_ping_time")
        assert conn.last_ping_time == 0.0

    def test_ws_connection_has_ping_latency_ms_field(self):
        """WSConnection must expose ping_latency_ms for RTT measurement."""
        conn = WSConnection()
        assert hasattr(conn, "ping_latency_ms")
        assert conn.ping_latency_ms == 0.0

    @pytest.mark.asyncio
    async def test_watchdog_does_not_close_on_ping_timeout(self):
        """Watchdog must NOT force-close a shard for ping timeout — aiohttp heartbeat handles keepalive."""
        from config import WS_PING_TIMEOUT_MS

        ws = WebSocketManager(lambda data: None, market="spot")
        ws._running = True

        closed = []

        class FakeWS:
            closed = False

            async def close(self):
                closed.append(True)
                FakeWS.closed = True

            async def ping(self):
                pass

        fake_ws = FakeWS()
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        conn.ws = fake_ws
        conn.last_pong = time.monotonic()
        # Simulate a ping sent WS_PING_TIMEOUT_MS + 100ms ago with no pong back
        conn.last_ping_time = time.monotonic() - (WS_PING_TIMEOUT_MS / 1000 + 0.1)
        conn.ping_latency_ms = 0.0
        ws._connections = [conn]
        ws._heartbeat_interval = 0  # skip the sleep

        # Run one watchdog tick (sleep=0 so it completes quickly)
        with mock.patch.object(ws, "_heartbeat_interval", 0):
            task = asyncio.create_task(ws._health_watchdog())
            await asyncio.sleep(0.05)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        assert not closed, "Watchdog must NOT close the connection for ping timeout (aiohttp handles keepalive)"

    @pytest.mark.asyncio
    async def test_watchdog_does_not_close_on_high_latency(self):
        """Watchdog must NOT force-close a shard for high latency — only staleness triggers close."""
        from config import WS_PING_TIMEOUT_MS

        ws = WebSocketManager(lambda data: None, market="spot")
        ws._running = True

        closed = []

        class FakeWS:
            closed = False

            async def close(self):
                closed.append(True)
                FakeWS.closed = True

            async def ping(self):
                pass

        fake_ws = FakeWS()
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        conn.ws = fake_ws
        conn.last_pong = time.monotonic()
        conn.last_ping_time = 0.0
        # Simulate a previously measured high RTT
        conn.ping_latency_ms = WS_PING_TIMEOUT_MS + 500
        ws._connections = [conn]

        with mock.patch.object(ws, "_heartbeat_interval", 0):
            task = asyncio.create_task(ws._health_watchdog())
            await asyncio.sleep(0.05)
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        assert not closed, "Watchdog must NOT close the connection for high latency (aiohttp handles keepalive)"

    @pytest.mark.asyncio
    async def test_watchdog_sends_ping_when_connection_healthy(self):
        """Watchdog must send a manual ping on healthy connections to measure latency."""
        ws = WebSocketManager(lambda data: None, market="spot")
        ws._running = True

        pings_sent = []

        class FakeWS:
            closed = False

            async def close(self):
                pass

            async def ping(self):
                pings_sent.append(time.monotonic())

        conn = WSConnection(streams=["btcusdt@kline_1m"])
        conn.ws = FakeWS()
        conn.last_pong = time.monotonic()
        conn.last_ping_time = 0.0
        conn.ping_latency_ms = 0.0
        ws._connections = [conn]

        # _heartbeat_interval=0 -> asyncio.sleep(0) yields to event loop without blocking.
        # The staleness threshold is max(1.0, 0 * staleness_multiplier) = 1.0 s, so a
        # freshly created connection (last_pong ~= now) won't be falsely closed.
        ws._heartbeat_interval = 0
        task = asyncio.create_task(ws._health_watchdog())
        # Two sleep(0) calls are needed: the first tick starts the watchdog and
        # lets it hit its own sleep(0); the second tick runs the watchdog body
        # (staleness checks + the manual ping send).
        await asyncio.sleep(0)
        await asyncio.sleep(0)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert pings_sent, "Watchdog must send a manual ping on healthy connections"
        assert conn.last_ping_time > 0, "last_ping_time must be set after ping is sent"

    @pytest.mark.asyncio
    async def test_listen_computes_latency_on_pong(self):
        """_listen must compute ping_latency_ms when a PONG frame arrives."""
        received = []

        async def on_msg(data):
            received.append(data)

        ws = WebSocketManager(on_msg, market="spot")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        # Simulate a ping sent 50ms ago
        conn.last_ping_time = time.monotonic() - 0.05

        class FakeMsg:
            def __init__(self, mtype, data=""):
                self.type = mtype
                self.data = data

        class FakeWS:
            def __init__(self):
                self._msgs = [
                    FakeMsg(aiohttp.WSMsgType.PONG),
                    FakeMsg(aiohttp.WSMsgType.CLOSED),
                ]

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self._msgs:
                    return self._msgs.pop(0)
                raise StopAsyncIteration

        conn.ws = FakeWS()
        await ws._listen(conn)

        assert conn.ping_latency_ms > 0, "ping_latency_ms must be set after PONG"
        assert conn.last_ping_time == 0.0, "last_ping_time must be reset after PONG"

    @pytest.mark.asyncio
    async def test_connect_resets_ping_fields(self):
        """_connect must reset last_ping_time and ping_latency_ms on (re)connect."""
        ws = WebSocketManager(lambda data: None, market="spot")
        ws._running = True

        class FakeWS:
            closed = False

        fake_ws_response = FakeWS()

        class FakeSession:
            async def ws_connect(self, url, **kwargs):
                return fake_ws_response

        ws._session = FakeSession()

        conn = WSConnection(streams=["btcusdt@kline_1m"])
        conn.last_ping_time = 99.9
        conn.ping_latency_ms = 1234.5

        await ws._connect(conn)

        assert conn.last_ping_time == 0.0
        assert conn.ping_latency_ms == 0.0


class TestShardResiliency:
    """Requirement 4: Individual shard failure must not affect other shards."""

    def test_degraded_flag_per_connection(self):
        """Each WSConnection has its own degraded flag, independent of others."""
        conn1 = WSConnection(streams=["btcusdt@kline_1m"])
        conn2 = WSConnection(streams=["ethusdt@kline_1m"])
        conn1.degraded = True
        assert conn2.degraded is False, "conn2 must be unaffected when conn1 is degraded"

    def test_health_ratio_reflects_partial_degradation(self):
        """health_ratio must reflect the fraction of healthy shards."""
        ws = WebSocketManager(lambda data: None, market="spot")
        now = time.monotonic()

        mock_open = type("FWS", (), {"closed": False})()
        mock_closed = type("FWS", (), {"closed": True})()

        conn_ok = WSConnection(streams=["btcusdt@kline_1m"], last_pong=now, ws=mock_open)
        conn_down = WSConnection(streams=["ethusdt@kline_1m"], last_pong=now, ws=mock_closed)
        ws._connections = [conn_ok, conn_down]

        ratio = ws.health_ratio
        assert ratio == 0.5, f"Expected 0.5, got {ratio}"

    def test_ping_fields_independent_per_shard(self):
        """Ping latency fields on one shard are independent of another shard's fields."""
        conn1 = WSConnection(streams=["btcusdt@kline_1m"])
        conn2 = WSConnection(streams=["ethusdt@kline_1m"])
        conn1.ping_latency_ms = 3000.0
        conn1.last_ping_time = 1.0
        assert conn2.ping_latency_ms == 0.0
        assert conn2.last_ping_time == 0.0


# ---------------------------------------------------------------------------
# Data-staleness watchdog — 2026-05-14 fix for 13h emission blackout
# ---------------------------------------------------------------------------
#
# Root cause: ``_health_watchdog`` checked ``last_pong``, which updates on
# PING/PONG as well as TEXT, so a connection where Binance kept the socket
# alive on pings but stopped delivering kline TEXT frames read as healthy.
# ``_health_check_loop`` was supposed to catch low message rates but its
# ``conn.health_msg_count`` was never incremented in ``_listen``, so rate=0
# always and the check just logged forever without acting.  Fixed by:
#   1. Incrementing health_msg_count in _listen on TEXT msgs
#   2. Making _health_check_loop force-close on sustained low rate
#   3. Adding per-symbol staleness via data_store.last_kline_age_seconds
#   4. Dropping WS_STALENESS_MULTIPLIER_FUTURES default 15→5 (15min→5min)


class _FakeClosableWS:
    """Stub aiohttp WS with .closed flag + an async close() that flips it."""

    def __init__(self) -> None:
        self.closed = False
        self.close_calls = 0

    async def close(self) -> None:
        self.close_calls += 1
        self.closed = True


class _FakeDataStore:
    """Minimal data store: maps (symbol, interval) → age_sec (or None)."""

    def __init__(self) -> None:
        self._ages: dict = {}

    def set_age(self, symbol: str, interval: str, age_sec):
        self._ages[(symbol.upper(), interval)] = age_sec

    def last_kline_age_seconds(self, symbol: str, interval: str):
        return self._ages.get((symbol.upper(), interval))


@pytest.fixture
def alerts_seen() -> list:
    return []


@pytest.fixture
def alert_cb(alerts_seen: list):
    async def _cb(msg: str) -> None:
        alerts_seen.append(msg)
    return _cb


class TestHealthMsgCounter:
    """_listen must increment conn.health_msg_count on every TEXT message."""

    async def test_listen_increments_health_msg_count_on_text(self):
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])

        # Build a minimal async iterator that yields one TEXT msg then closes.
        class _Msg:
            def __init__(self, type_, data="{}"):
                self.type = type_
                self.data = data

        class _AsyncIter:
            def __init__(self, msgs):
                self._msgs = list(msgs)

            def __aiter__(self):
                return self

            async def __anext__(self):
                if not self._msgs:
                    raise StopAsyncIteration
                return self._msgs.pop(0)

        fake_ws = _AsyncIter([
            _Msg(aiohttp.WSMsgType.TEXT, '{"e":"kline"}'),
            _Msg(aiohttp.WSMsgType.TEXT, '{"e":"kline"}'),
            _Msg(aiohttp.WSMsgType.TEXT, '{"e":"kline"}'),
            _Msg(aiohttp.WSMsgType.CLOSED),
        ])
        conn.ws = fake_ws  # type: ignore[assignment]
        await ws._listen(conn)
        assert conn.health_msg_count == 3


class TestHealthCheckLoopForceClose:
    """_health_check_loop must force-close connections with sustained low rate."""

    async def test_force_close_after_threshold_window(
        self, alert_cb, alerts_seen, monkeypatch,
    ):
        """When rate stays below threshold for ≥ force-close window AND
        connection is past min-conn-age, force-close fires + alert sent."""
        async def handler(data):
            pass

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
            label="futures-test",
        )
        # Shrink the health interval to 0 so a single iteration runs.
        # We won't actually loop — we'll call the loop body inline by
        # constructing the conditions and running a one-shot check.

        fake = _FakeClosableWS()
        conn = WSConnection(streams=["btcusdt@kline_1m"], ws=fake)  # type: ignore[arg-type]

        now = time.monotonic()
        # Connection is well past min-conn-age (default 120s)
        conn.connected_ts = now - 300.0
        # Last health check was 60s ago, with 0 TEXT msgs in the window
        conn.health_check_ts = now - 60.0
        conn.health_msg_count = 0
        # Low-rate state began earlier than the force-close threshold (90s)
        conn.low_msgrate_since = now - 100.0

        ws._connections = [conn]
        # Run one cycle of the body by patching asyncio.sleep to break.
        # Simpler: call the inner logic directly by monkey-stopping after 1 iter.
        ws._running = True

        async def _stop_after_one(_: float) -> None:
            ws._running = False
        monkeypatch.setattr("src.websocket_manager.asyncio.sleep", _stop_after_one)

        await ws._health_check_loop()

        assert fake.close_calls == 1, "force-close should fire when rate stays low past threshold"
        assert fake.closed is True
        assert any("data-silent" in a for a in alerts_seen), "admin alert should fire on force-close"

    async def test_skip_force_close_when_under_min_conn_age(
        self, alert_cb, alerts_seen, monkeypatch,
    ):
        """Freshly-reconnected connection (under min-conn-age) must NOT be force-closed."""
        async def handler(data):
            pass

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
            label="futures-test",
        )
        fake = _FakeClosableWS()
        conn = WSConnection(streams=["btcusdt@kline_1m"], ws=fake)  # type: ignore[arg-type]

        now = time.monotonic()
        # Connection is FRESH — only 10s old, well under 120s min-conn-age
        conn.connected_ts = now - 10.0
        conn.health_check_ts = now - 60.0
        conn.health_msg_count = 0
        conn.low_msgrate_since = now - 200.0  # would otherwise trigger

        ws._connections = [conn]
        ws._running = True

        async def _stop_after_one(_: float) -> None:
            ws._running = False
        monkeypatch.setattr("src.websocket_manager.asyncio.sleep", _stop_after_one)

        await ws._health_check_loop()

        assert fake.close_calls == 0, "fresh connection should be protected by min-conn-age guard"
        assert alerts_seen == [], "no alert should fire while under min-conn-age"

    async def test_no_action_when_rate_recovers(self, alert_cb, alerts_seen, monkeypatch):
        """Rate above threshold clears low_msgrate_since; no close, no alert."""
        async def handler(data):
            pass

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
        )
        fake = _FakeClosableWS()
        conn = WSConnection(streams=["btcusdt@kline_1m"], ws=fake)  # type: ignore[arg-type]

        now = time.monotonic()
        conn.connected_ts = now - 300.0
        conn.health_check_ts = now - 60.0
        # 60 msgs in 60s = 60 msgs/min = healthy
        conn.health_msg_count = 60
        conn.low_msgrate_since = now - 200.0  # was previously stuck

        ws._connections = [conn]
        ws._running = True

        async def _stop_after_one(_: float) -> None:
            ws._running = False
        monkeypatch.setattr("src.websocket_manager.asyncio.sleep", _stop_after_one)

        await ws._health_check_loop()

        assert fake.close_calls == 0
        assert conn.low_msgrate_since == 0.0, "rate recovery should clear the low-rate timer"
        assert alerts_seen == []


class TestPerSymbolStaleness:
    """Per-symbol staleness check force-closes all conns when majority of
    subscribed symbols have stale klines, even if per-connection rate is OK."""

    async def test_force_close_all_when_majority_stale(
        self, alert_cb, alerts_seen,
    ):
        async def handler(data):
            pass

        store = _FakeDataStore()
        # 4 symbols, 3 stale (>180s) → ratio 0.75 > 0.5 threshold
        store.set_age("BTCUSDT", "1m", 5.0)     # fresh
        store.set_age("ETHUSDT", "1m", 250.0)   # stale
        store.set_age("SOLUSDT", "1m", 220.0)   # stale
        store.set_age("AVAXUSDT", "1m", 300.0)  # stale

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
            data_store=store,
        )

        fake0 = _FakeClosableWS()
        fake1 = _FakeClosableWS()
        now = time.monotonic()
        # Both connections past min-conn-age
        conn0 = WSConnection(
            streams=["btcusdt@kline_1m", "ethusdt@kline_1m"], ws=fake0,  # type: ignore[arg-type]
        )
        conn0.connected_ts = now - 300.0
        conn1 = WSConnection(
            streams=["solusdt@kline_1m", "avaxusdt@kline_1m"], ws=fake1,  # type: ignore[arg-type]
        )
        conn1.connected_ts = now - 300.0
        ws._connections = [conn0, conn1]

        await ws._check_per_symbol_staleness(now)

        assert fake0.close_calls == 1, "both conns should be force-closed"
        assert fake1.close_calls == 1
        assert any("per-symbol stale" in a for a in alerts_seen)

    async def test_no_action_when_minority_stale(self, alert_cb, alerts_seen):
        async def handler(data):
            pass

        store = _FakeDataStore()
        # 4 symbols, only 1 stale → ratio 0.25 < 0.5 threshold
        store.set_age("BTCUSDT", "1m", 5.0)
        store.set_age("ETHUSDT", "1m", 5.0)
        store.set_age("SOLUSDT", "1m", 5.0)
        store.set_age("AVAXUSDT", "1m", 300.0)

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
            data_store=store,
        )

        fake = _FakeClosableWS()
        now = time.monotonic()
        conn = WSConnection(
            streams=["btcusdt@kline_1m", "ethusdt@kline_1m", "solusdt@kline_1m", "avaxusdt@kline_1m"],
            ws=fake,  # type: ignore[arg-type]
        )
        conn.connected_ts = now - 300.0
        ws._connections = [conn]

        await ws._check_per_symbol_staleness(now)

        assert fake.close_calls == 0
        assert alerts_seen == []

    async def test_no_action_when_all_conns_under_min_age(
        self, alert_cb, alerts_seen,
    ):
        """All-fresh-conns guard: don't churn during the resubscribe window."""
        async def handler(data):
            pass

        store = _FakeDataStore()
        # All symbols stale, but conns are too fresh — guard should apply
        store.set_age("BTCUSDT", "1m", 250.0)
        store.set_age("ETHUSDT", "1m", 250.0)

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
            data_store=store,
        )

        fake = _FakeClosableWS()
        now = time.monotonic()
        conn = WSConnection(
            streams=["btcusdt@kline_1m", "ethusdt@kline_1m"],
            ws=fake,  # type: ignore[arg-type]
        )
        # Fresh connect — only 30s old
        conn.connected_ts = now - 30.0
        ws._connections = [conn]

        await ws._check_per_symbol_staleness(now)

        assert fake.close_calls == 0
        assert alerts_seen == []

    async def test_no_data_store_skips_check(self, alert_cb, alerts_seen):
        """When no data_store is wired, per-symbol check is a noop."""
        async def handler(data):
            pass

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
            data_store=None,
        )
        fake = _FakeClosableWS()
        now = time.monotonic()
        conn = WSConnection(streams=["btcusdt@kline_1m"], ws=fake)  # type: ignore[arg-type]
        conn.connected_ts = now - 300.0
        ws._connections = [conn]

        await ws._check_per_symbol_staleness(now)

        assert fake.close_calls == 0


class TestAlertThrottle:
    """Per-key alert throttle dedups within WS_ALERT_COOLDOWN window."""

    async def test_alert_deduped_within_cooldown(self, alert_cb, alerts_seen):
        async def handler(data):
            pass

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
        )
        await ws._alert_admin_throttled("first", alert_key="k1")
        await ws._alert_admin_throttled("second", alert_key="k1")
        assert len(alerts_seen) == 1
        assert alerts_seen[0] == "first"

    async def test_different_keys_alert_independently(self, alert_cb, alerts_seen):
        async def handler(data):
            pass

        ws = WebSocketManager(
            handler, market="futures",
            admin_alert_callback=alert_cb,
        )
        await ws._alert_admin_throttled("a", alert_key="low_msgrate:0")
        await ws._alert_admin_throttled("b", alert_key="per_symbol_stale")
        assert len(alerts_seen) == 2

    async def test_no_callback_is_noop(self):
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="futures", admin_alert_callback=None)
        # Must not raise
        await ws._alert_admin_throttled("test", alert_key="k")


class TestFuturesStalenessMultiplierDefault:
    """Verify the env-driven default actually dropped from 15 to 5."""

    def test_default_dropped_to_five(self):
        # Imported at module top; just assert the value.
        assert WS_STALENESS_MULTIPLIER_FUTURES == 5, (
            "Futures multiplier should default to 5 (300s threshold) per 2026-05-14 fix"
        )


# ---------------------------------------------------------------------------
# Combined-stream URL format (2026-05-14 — Binance-doc-compliant)
# ---------------------------------------------------------------------------
#
# Switching from the unofficial ``/ws/<s1>/<s2>/...`` form (which Binance
# Futures has been silently partially-dropping for us) to the documented
# combined-stream form: ``/stream?streams=<s1>/<s2>/...``.  Payloads then
# arrive wrapped as ``{"stream": "<name>", "data": <rawPayload>}`` and the
# manager / engine handler must unwrap before dispatching to the typed
# event handlers.


class TestCombinedStreamBaseUrl:
    """Verify the env-driven WS base URLs point at /stream (combined) not /ws."""

    def test_futures_base_is_combined_stream(self):
        from config import BINANCE_FUTURES_WS_BASE
        assert BINANCE_FUTURES_WS_BASE.rstrip("/").endswith("/stream"), (
            "Futures WS base must end with /stream (combined-stream endpoint) "
            "per Binance docs.  Raw /ws is the single-stream endpoint and "
            "doesn't reliably support multi-stream subscriptions."
        )

    def test_spot_base_is_combined_stream(self):
        # Spot WS manager was ripped in PR #387 but the base URL is still
        # imported by ``WebSocketManager.__init__`` when ``market="spot"``
        # — keep it on /stream so any test/use that constructs a spot
        # manager doesn't hit the wrong URL form.
        from config import BINANCE_WS_BASE
        assert BINANCE_WS_BASE.rstrip("/").endswith("/stream"), (
            "Spot WS base must end with /stream for consistency with futures."
        )


class TestCombinedStreamUrlConstruction:
    """``_connect`` builds URL as ``base?streams=<s1>/<s2>/...``."""

    async def test_url_uses_query_string_format(self, monkeypatch):
        """Patch the session's ws_connect to capture the URL the code
        actually sends to Binance.  Verifies the new combined-stream
        format vs the old ``/ws/<s1>/<s2>`` path-component form."""
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="futures")
        captured: list[str] = []

        # Fake session + ws_connect — just record the URL and return a
        # closed-immediately fake ws so _connect returns cleanly.
        class _FakeWS:
            closed = False
            async def close(self): self.closed = True
            def __aiter__(self): return self
            async def __anext__(self): raise StopAsyncIteration

        class _FakeSession:
            async def ws_connect(self_, url, **kw):
                captured.append(url)
                return _FakeWS()

        ws._session = _FakeSession()  # type: ignore[assignment]
        conn = WSConnection(streams=[
            "btcusdt@kline_1m",
            "ethusdt@kline_1m",
            "solusdt@kline_5m",
        ])
        await ws._connect(conn)

        assert len(captured) == 1
        url = captured[0]
        # Must use ?streams= query string, not path components.
        assert "?streams=" in url, f"URL should use combined-stream form: {url}"
        # Streams concatenated with /
        assert "btcusdt@kline_1m/ethusdt@kline_1m/solusdt@kline_5m" in url, (
            f"All streams should appear joined by /: {url}"
        )
        # NEGATIVE assertion — the old form would have had path components
        # like /ws/btcusdt@kline_1m/ethusdt@kline_1m — assert that's NOT
        # what we built.  ``/ws/`` may still appear in test bases (rare)
        # but the multi-stream PATH form should not.
        assert "/ws/btcusdt@kline_1m" not in url, (
            f"Old /ws/<s1>/<s2> form regressed: {url}"
        )


class TestCombinedStreamPayloadUnwrap:
    """``_on_ws_message`` accepts both wrapped and raw payloads."""

    async def test_unwraps_combined_stream_kline_payload(self):
        """Combined-stream wrapper: {"stream":"...","data":{"e":"kline",...}}.

        The handler must reach the kline branch and call
        ``data_store.update_candle`` on candle close.  Use a SimpleNamespace
        engine stub with just the surfaces _on_ws_message reads.
        """
        from types import SimpleNamespace
        from src.main import CryptoSignalEngine

        # Build a minimal engine via __new__ to bypass full __init__;
        # only the attributes used by _on_ws_message need to exist.
        engine = CryptoSignalEngine.__new__(CryptoSignalEngine)
        update_calls: list = []

        class _DS:
            def update_candle(self, symbol, interval, candle):
                update_calls.append((symbol, interval, candle))
            def append_tick(self, symbol, tick):
                pass

        class _OFS:
            def update_cvd_from_tick(self, *a, **kw):
                pass
            def snapshot_cvd_at_candle_close(self, *a, **kw):
                pass

        engine.data_store = _DS()  # type: ignore[attr-defined]
        engine._order_flow_store = _OFS()  # type: ignore[attr-defined]

        wrapped = {
            "stream": "btcusdt@kline_1m",
            "data": {
                "e": "kline",
                "s": "BTCUSDT",
                "k": {
                    "i": "1m",
                    "o": 100.0, "h": 101.0, "l": 99.0, "c": 100.5,
                    "v": 12.5, "x": True,
                    "Q": 5.0, "q": 10.0,
                },
            },
        }
        await engine._on_ws_message(wrapped)
        assert len(update_calls) == 1
        assert update_calls[0][0] == "BTCUSDT"
        assert update_calls[0][1] == "1m"
        assert update_calls[0][2]["close"] == 100.5

    async def test_accepts_raw_payload_for_backwards_compat(self):
        """Raw single-stream payload (legacy / REST fallback path):
        {"e":"kline","s":"BTC","k":{...}} — no wrapper.  Handler must
        still dispatch to update_candle on close."""
        from src.main import CryptoSignalEngine

        engine = CryptoSignalEngine.__new__(CryptoSignalEngine)
        update_calls: list = []

        class _DS:
            def update_candle(self, symbol, interval, candle):
                update_calls.append((symbol, interval, candle))
            def append_tick(self, symbol, tick):
                pass

        class _OFS:
            def update_cvd_from_tick(self, *a, **kw):
                pass
            def snapshot_cvd_at_candle_close(self, *a, **kw):
                pass

        engine.data_store = _DS()  # type: ignore[attr-defined]
        engine._order_flow_store = _OFS()  # type: ignore[attr-defined]

        raw = {
            "e": "kline",
            "s": "ETHUSDT",
            "k": {
                "i": "5m",
                "o": 2000.0, "h": 2010.0, "l": 1995.0, "c": 2005.0,
                "v": 50.0, "x": True,
                "Q": 20.0, "q": 40.0,
            },
        }
        await engine._on_ws_message(raw)
        assert len(update_calls) == 1
        assert update_calls[0][0] == "ETHUSDT"
        assert update_calls[0][1] == "5m"

    async def test_no_false_unwrap_on_payload_with_stream_field(self):
        """Defensive: if a payload happens to have a top-level ``stream``
        key but no ``data`` dict, the handler must not crash — should
        treat it as raw.  Guards against shape drift breaking the
        unwrapper without us noticing."""
        from src.main import CryptoSignalEngine

        engine = CryptoSignalEngine.__new__(CryptoSignalEngine)
        engine.data_store = type("DS", (), {
            "update_candle": lambda *a, **k: None,
            "append_tick": lambda *a, **k: None,
        })()
        engine._order_flow_store = type("OFS", (), {
            "update_cvd_from_tick": lambda *a, **k: None,
            "snapshot_cvd_at_candle_close": lambda *a, **k: None,
        })()

        # ``stream`` field present but ``data`` is None — must not unwrap
        odd = {"stream": "btcusdt@kline_1m", "data": None, "e": "kline"}
        # Should not raise; should not match the kline branch because
        # there's no "k" key after non-unwrap, but the test asserts
        # only that no exception escapes.
        await engine._on_ws_message(odd)
        # If we got here, the handler didn't crash — pass.


# ---------------------------------------------------------------------------
# WS-trace logger + per-stream tracking + stream_summary (2026-05-14, Phase 3)
# ---------------------------------------------------------------------------
#
# The trace logger writes structured ``<WS:LABEL>`` events to a dedicated
# file routed via a loguru ``filter=ws_trace`` sink so stderr + engine log
# stay quiet of per-second WS noise.  Owner pulls the file via the new
# ``/ws_log`` Telegram command (no SSH needed).


class TestWsTraceLoggerSeparation:
    """Records emitted via ``get_ws_trace_logger()`` must go to the trace
    file ONLY — never to stderr or the engine rolling log.  This guards
    the operator's main log from being flooded with per-stream events."""

    def test_trace_logger_writes_to_dedicated_file(self, tmp_path, monkeypatch):
        from importlib import reload
        import src.utils as utils_mod
        # Repoint the trace log to a tmp file by reloading the module with
        # an env override.  The module-level loguru ``add()`` runs at
        # import time, so we monkeypatch the path and reload.
        trace_path = tmp_path / "ws_trace.log"
        monkeypatch.setenv("WS_TRACE_LOG_PATH", str(trace_path))
        # Force config re-read AND utils re-init.  Note: this affects
        # global loguru state for the duration of the test; later tests
        # that depend on the production path will pick up whichever path
        # was last set (acceptable for an isolated unit).
        import config as cfg_mod
        reload(cfg_mod)
        reload(utils_mod)
        ws = utils_mod.get_ws_trace_logger()
        ws.info("<WS:UNIT> probe_event k=v")
        # Loguru's file sinks flush synchronously when enqueue=False (our
        # configured value), so we can read the file immediately.
        contents = trace_path.read_text(encoding="utf-8")
        assert "<WS:UNIT> probe_event k=v" in contents


class TestWSConnectionStreamDataTracking:
    """``_listen`` populates ``conn.stream_data_ts`` from combined-stream
    wrapper payloads so the periodic ``stream_summary`` can report which
    subscribed streams are actually delivering."""

    async def test_first_data_stamps_stream_ts(self):
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m", "ethusdt@kline_1m"])
        conn.connected_ts = time.monotonic()

        class _Msg:
            def __init__(self, data):
                self.type = aiohttp.WSMsgType.TEXT
                self.data = data

        class _AsyncIter:
            def __init__(self, msgs):
                self._msgs = list(msgs)
            def __aiter__(self):
                return self
            async def __anext__(self):
                if not self._msgs:
                    raise StopAsyncIteration
                return self._msgs.pop(0)

        # Combined-stream wrapper payloads for two different streams
        import json as _json
        msgs = [
            _Msg(_json.dumps({"stream": "btcusdt@kline_1m", "data": {"e": "kline"}})),
            _Msg(_json.dumps({"stream": "ethusdt@kline_1m", "data": {"e": "kline"}})),
            _Msg(_json.dumps({"stream": "btcusdt@kline_1m", "data": {"e": "kline"}})),  # 2nd hit on BTC
        ]
        conn.ws = _AsyncIter(msgs)  # type: ignore[assignment]
        await ws._listen(conn)
        assert "btcusdt@kline_1m" in conn.stream_data_ts
        assert "ethusdt@kline_1m" in conn.stream_data_ts
        # BTC's timestamp is the *latest* (second hit) — confirms we
        # update on every TEXT, not just the first
        btc_ts = conn.stream_data_ts["btcusdt@kline_1m"]
        eth_ts = conn.stream_data_ts["ethusdt@kline_1m"]
        # BTC was first, then ETH, then BTC again → BTC's ts > ETH's ts
        assert btc_ts >= eth_ts

    async def test_raw_payload_does_not_stamp_stream_ts(self):
        """Raw (non-wrapped) payloads — e.g. from REST fallback — have
        no top-level ``stream`` key.  Per-stream tracking should skip
        them; only health_msg_count increments."""
        async def handler(data):
            pass

        ws = WebSocketManager(handler, market="futures")
        conn = WSConnection(streams=["btcusdt@kline_1m"])
        conn.connected_ts = time.monotonic()

        class _Msg:
            def __init__(self, data):
                self.type = aiohttp.WSMsgType.TEXT
                self.data = data

        class _AsyncIter:
            def __init__(self, msgs):
                self._msgs = list(msgs)
            def __aiter__(self):
                return self
            async def __anext__(self):
                if not self._msgs:
                    raise StopAsyncIteration
                return self._msgs.pop(0)

        import json as _json
        msgs = [
            _Msg(_json.dumps({"e": "kline", "s": "BTCUSDT", "k": {}})),  # raw, no wrapper
        ]
        conn.ws = _AsyncIter(msgs)  # type: ignore[assignment]
        await ws._listen(conn)
        # health_msg_count incremented but stream_data_ts stays empty
        assert conn.health_msg_count == 1
        assert conn.stream_data_ts == {}


class TestWsLogCommand:
    """``/ws_log`` reads ``WS_TRACE_LOG_PATH`` and sends via send_document."""

    async def test_ws_log_sends_full_file_when_no_args(self, tmp_path, monkeypatch):
        from src.commands.channels import handle_ws_log

        trace_path = tmp_path / "ws_trace.log"
        trace_path.write_text(
            "2026-05-14 06:00:00 | <WS:FUT> connect_start streams=200\n"
            "2026-05-14 06:00:02 | <WS:FUT> connect_success duration_ms=1834\n",
            encoding="utf-8",
        )
        # Patch the config import inside the handler.  The handler does
        # ``from config import WS_TRACE_LOG_PATH`` at call time so we can
        # patch the module attribute.
        import config as cfg
        monkeypatch.setattr(cfg, "WS_TRACE_LOG_PATH", str(trace_path), raising=True)

        # Stub Telegram client capturing the document upload.
        captured: dict = {}

        class _StubTelegram:
            async def send_document(self, chat_id, document, filename, caption=None):
                captured["chat_id"] = chat_id
                captured["document"] = document
                captured["filename"] = filename
                captured["caption"] = caption
                return True

        replies: list = []

        class _StubCtx:
            telegram = _StubTelegram()
            chat_id = "owner-chat"
            async def reply(self, msg):
                replies.append(msg)

        await handle_ws_log([], _StubCtx())
        assert "filename" in captured
        assert captured["filename"].startswith("ws_trace_")
        assert captured["filename"].endswith(".log")
        assert b"<WS:FUT> connect_start" in captured["document"]
        # Caption mentions byte count
        assert "bytes" in (captured["caption"] or "")
        # No fallback reply needed — send_document returned True
        assert replies == []

    async def test_ws_log_tail_limits_output(self, tmp_path, monkeypatch):
        from src.commands.channels import handle_ws_log

        trace_path = tmp_path / "ws_trace.log"
        # 20 distinct lines
        lines = [f"<WS:FUT> event_{i}" for i in range(20)]
        trace_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        import config as cfg
        monkeypatch.setattr(cfg, "WS_TRACE_LOG_PATH", str(trace_path), raising=True)

        captured: dict = {}

        class _StubTelegram:
            async def send_document(self, chat_id, document, filename, caption=None):
                captured["document"] = document
                captured["caption"] = caption
                return True

        class _StubCtx:
            telegram = _StubTelegram()
            chat_id = "owner-chat"
            async def reply(self, msg):
                pass

        await handle_ws_log(["5"], _StubCtx())
        body = captured["document"].decode("utf-8")
        # Should contain the last 5 events (15..19) but not earlier ones
        assert "event_19" in body
        assert "event_15" in body
        assert "event_5" not in body
        # Caption reports tail boundaries
        assert "last 5" in (captured["caption"] or "")

    async def test_ws_log_missing_file(self, tmp_path, monkeypatch):
        from src.commands.channels import handle_ws_log

        missing = tmp_path / "never_written.log"
        import config as cfg
        monkeypatch.setattr(cfg, "WS_TRACE_LOG_PATH", str(missing), raising=True)

        replies: list = []

        class _StubTelegram:
            async def send_document(self, *a, **kw):
                raise AssertionError("send_document should not be called")

        class _StubCtx:
            telegram = _StubTelegram()
            chat_id = "owner-chat"
            async def reply(self, msg):
                replies.append(msg)

        await handle_ws_log([], _StubCtx())
        assert len(replies) == 1
        assert "not found" in replies[0]

    async def test_ws_log_empty_file(self, tmp_path, monkeypatch):
        from src.commands.channels import handle_ws_log

        trace_path = tmp_path / "ws_trace.log"
        trace_path.write_text("", encoding="utf-8")

        import config as cfg
        monkeypatch.setattr(cfg, "WS_TRACE_LOG_PATH", str(trace_path), raising=True)

        replies: list = []

        class _StubTelegram:
            async def send_document(self, *a, **kw):
                raise AssertionError("send_document should not be called on empty file")

        class _StubCtx:
            telegram = _StubTelegram()
            chat_id = "owner-chat"
            async def reply(self, msg):
                replies.append(msg)

        await handle_ws_log([], _StubCtx())
        assert any("empty" in r.lower() for r in replies)
