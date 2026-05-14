"""WebSocket manager – multi-connection, heartbeat, auto-reconnect.

Supports up to ``WS_MAX_STREAMS_PER_CONN`` streams per connection,
exponential-backoff reconnect, auto-resubscribe, REST fallback,
and admin Telegram alerts.

Message buffering during reconnection gaps is handled by the upstream
:class:`src.signal_queue.SignalQueue` layer (Redis + asyncio.Queue fallback),
not at the WebSocket manager level.
"""

from __future__ import annotations

import asyncio
import json
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set

import aiohttp

from config import (
    BINANCE_FUTURES_REST_BASE,
    BINANCE_FUTURES_WS_BASE,
    BINANCE_REST_BASE,
    BINANCE_WS_BASE,
    WS_ALERT_COOLDOWN,
    WS_FALLBACK_BULK_LIMIT,
    WS_FALLBACK_POLL_INTERVALS,
    WS_FALLBACK_TIMEFRAMES,
    WS_HEALTH_CHECK_INTERVAL,
    WS_HEALTH_CHECK_MIN_CONN_AGE_SEC,
    WS_HEARTBEAT_INTERVAL,
    WS_HEARTBEAT_INTERVAL_FUTURES,
    WS_LOW_MSGRATE_FORCE_CLOSE_AFTER_SEC,
    WS_MAX_STREAMS_PER_CONN,
    WS_MIN_MESSAGE_RATE,
    WS_PER_SYMBOL_STALENESS_RATIO,
    WS_PER_SYMBOL_STALENESS_THRESHOLD_SEC,
    WS_PING_TIMEOUT_MS,
    WS_RECONNECT_BASE_DELAY,
    WS_RECONNECT_FAIL_ALERT_THRESHOLD,
    WS_RECONNECT_MAX_DELAY,
    WS_REST_FALLBACK_ALERT_GRACE_SEC,
    WS_SESSION_RECYCLE_ATTEMPTS,
    WS_STALENESS_MULTIPLIER,
    WS_STALENESS_MULTIPLIER_FUTURES,
    WS_TRACE_SAMPLE_FIRST_N,
    WS_TRACE_SUMMARY_INTERVAL_SEC,
    WS_TRACE_SUMMARY_STALENESS_SEC,
)
from src.utils import get_logger, get_ws_trace_logger

log = get_logger("ws_manager")
# Dedicated logger for ``<WS:LABEL>`` events that the operator pulls via
# ``/ws_log``.  Routes only to ``logs/ws_trace.log`` (configured in
# ``src/utils.py``) so stderr and the engine rolling log stay quiet of
# the per-event noise we need for incident replay.
ws_trace = get_ws_trace_logger()

MessageHandler = Callable[[dict], Coroutine[Any, Any, None]]


@dataclass
class WSConnection:
    """Tracks one WebSocket connection and its streams."""
    ws: Optional[aiohttp.ClientWebSocketResponse] = None
    streams: List[str] = field(default_factory=list)
    last_pong: float = 0.0
    reconnect_attempts: int = 0
    task: Optional[asyncio.Task] = None
    degraded: bool = False
    # Ping/pong latency tracking
    last_ping_time: float = 0.0   # monotonic time when last manual ping was sent
    ping_latency_ms: float = 0.0  # RTT (ms) of the most recent completed ping/pong
    # Health monitoring fields (used by _health_check_loop)
    health_check_ts: float = 0.0   # last time a health check snapshot was taken
    health_msg_count: int = 0      # TEXT messages received since last health check
    # Wall-clock monotonic timestamp set when this connection's WS handshake
    # completed.  Used by the health-check loop's min-conn-age guard so a
    # freshly-reconnected connection doesn't get force-closed during its
    # 30-60 s resubscribe window (200 streams take that long to begin
    # delivering kline frames after the WS handshake).
    connected_ts: float = 0.0
    # Monotonic timestamp at which the connection first dropped below
    # ``WS_MIN_MESSAGE_RATE``.  Cleared as soon as rate recovers.  When this
    # remains set for ``WS_LOW_MSGRATE_FORCE_CLOSE_AFTER_SEC`` seconds the
    # health-check loop force-closes the connection.  Pattern matches
    # ``degraded_since`` so it composes cleanly with /diag reporting.
    low_msgrate_since: float = 0.0
    # Per-stream "last data arrived" timestamps (monotonic).  Populated from
    # ``_listen`` when a combined-stream wrapper arrives ({"stream":..., "data":...}).
    # The trace summary loop reads this to report ``active/silent`` counts per
    # connection — the diagnostic that distinguishes "Binance dropped a subset
    # of subscriptions silently" from "all streams down".
    stream_data_ts: Dict[str, float] = field(default_factory=dict)
    # Monotonic timestamp the trace summary loop last emitted a
    # ``stream_summary`` event for this connection.  Throttles the summary
    # cadence to ``WS_TRACE_SUMMARY_INTERVAL_SEC`` even though the
    # ``_health_check_loop`` ticks every ``WS_HEALTH_CHECK_INTERVAL``.
    trace_summary_last_ts: float = 0.0
    # Number of first-N raw messages already logged via ``raw_sample``.
    # Trace data 2026-05-14 showed connect_success on /stream?streams=...
    # then ZERO ``first_data`` events, ``health_msg_count=0``, and NO
    # close_received frames.  Hypothesis: Binance is sending BINARY
    # frames (gzip-compressed JSON, used elsewhere in their stack)
    # which the original ``_listen`` silently ignored.  Per-connection
    # sample counter lets us log the first ``WS_TRACE_SAMPLE_FIRST_N``
    # raw messages (any type) so we can see exactly what comes over
    # the wire without flooding the log on a healthy connection.
    samples_logged: int = 0
    # Per-msg-type counters for the periodic ``stream_summary`` line.
    # Lets us distinguish "BINARY frames arrived but ignored" from
    # "absolutely nothing arrived" by visual inspection of the trace.
    msg_type_counts: Dict[str, int] = field(default_factory=dict)
    # Reconnect-duration instrumentation (Phase 1, 2026-05-08).
    # ``degraded_since`` stamps monotonic time when the connection went
    # degraded; cleared when it goes healthy again.  ``last_reconnect_ms``
    # is the duration of the most recent recovery (drop → restored), in
    # milliseconds.  Both feed /diag + the truth-report parser to give us
    # data for tuning the REST-fallback grace window.
    degraded_since: float = 0.0
    last_reconnect_ms: float = 0.0


class WebSocketManager:
    """Manages multiple Binance WebSocket connections with resilience."""

    def __init__(self, on_message: MessageHandler, market: str = "spot", admin_alert_callback=None, data_store=None, label: str | None = None, staleness_multiplier: float | None = None) -> None:
        self._on_message = on_message
        self._market = market
        self._label = label or market
        self._base_url = BINANCE_WS_BASE if market == "spot" else BINANCE_FUTURES_WS_BASE
        self._rest_base_url = BINANCE_REST_BASE if market == "spot" else BINANCE_FUTURES_REST_BASE
        self._heartbeat_interval = WS_HEARTBEAT_INTERVAL_FUTURES if market == "futures" else WS_HEARTBEAT_INTERVAL
        default_multiplier = WS_STALENESS_MULTIPLIER_FUTURES if market == "futures" else WS_STALENESS_MULTIPLIER
        self._staleness_multiplier = staleness_multiplier if staleness_multiplier is not None else default_multiplier
        self._connections: List[WSConnection] = []
        self._session: Optional[aiohttp.ClientSession] = None
        self._running = False
        self._subscribed_streams: Set[str] = set()
        self._rest_fallback_active: bool = False
        self._critical_pairs: Set[str] = set()
        self._fallback_task: Optional[asyncio.Task] = None
        self._watchdog_task: Optional[asyncio.Task] = None
        # 2026-05-14: ``_health_check_loop`` task was never created — defined
        # but unstarted since the module existed.  PR #386 added the
        # actionable msg-rate force-close + per-symbol staleness check
        # INSIDE that loop, but the loop itself was still never scheduled.
        # PR #389 added the periodic ``stream_summary`` trace emit, also
        # inside the unstarted loop.  Result: every loop-resident feature
        # was dead in prod, only the ``_health_watchdog`` (started at
        # line 171) actually ran.  This task attribute + the create_task
        # call in start() bring the loop online.
        self._health_check_task: Optional[asyncio.Task] = None
        self._admin_alert = admin_alert_callback
        self._last_alert_time: float = 0.0
        # None = never alerted yet (so the first activation always fires);
        # subsequent activations within WS_ALERT_COOLDOWN are coalesced.
        self._last_rest_fallback_alert_time: Optional[float] = None
        self._total_drops: int = 0
        self._rest_fallback_activations_in_cooldown: int = 0
        self._data_store = data_store
        self._ws_rest_fallback_count: int = 0
        self._ws_reconnection_count: int = 0
        self._connection_message_rates: Dict[int, float] = {}  # conn_index -> msgs/min
        # Per-key alert dedup window — keyed by the alert source
        # (e.g. ``low_msgrate:<idx>``, ``per_symbol_stale``) so the
        # data-staleness paths don't compete with the REST-fallback path
        # over a single ``_last_alert_time`` slot.
        self._alert_keyed_ts: Dict[str, float] = {}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self, streams: List[str]) -> None:
        """Subscribe to *streams* distributed across connections."""
        self._running = True
        self._connections = []
        self._subscribed_streams = set()
        self._rest_fallback_active = False
        self._session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(keepalive_timeout=30)
        )
        for i in range(0, len(streams), WS_MAX_STREAMS_PER_CONN):
            chunk = streams[i: i + WS_MAX_STREAMS_PER_CONN]
            conn = WSConnection(streams=chunk)
            self._connections.append(conn)
            conn.task = asyncio.create_task(self._run_connection(conn))
        log.info(
            "WS manager started: {} streams across {} connections ({})",
            len(streams), len(self._connections), self._label,
        )
        self._watchdog_task = asyncio.create_task(self._health_watchdog())
        # Start the health-check loop too — it owns the actionable
        # msg-rate force-close, the per-symbol staleness check, AND the
        # periodic stream_summary trace emit.  This was previously never
        # started, leaving all three subsystems dead in prod.
        self._health_check_task = asyncio.create_task(self._health_check_loop())

    async def stop(self) -> None:
        self._running = False
        self._rest_fallback_active = False
        tasks: List[asyncio.Task] = []
        if self._fallback_task and not self._fallback_task.done():
            self._fallback_task.cancel()
            tasks.append(self._fallback_task)
        if self._watchdog_task and not self._watchdog_task.done():
            self._watchdog_task.cancel()
            tasks.append(self._watchdog_task)
        if self._health_check_task and not self._health_check_task.done():
            self._health_check_task.cancel()
            tasks.append(self._health_check_task)
        for conn in self._connections:
            conn.degraded = False
            if conn.task and not conn.task.done():
                conn.task.cancel()
                tasks.append(conn.task)
            if conn.ws and not conn.ws.closed:
                await conn.ws.close()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._fallback_task = None
        self._watchdog_task = None
        self._health_check_task = None
        if self._session and not self._session.closed:
            await self._session.close()
        self._session = None
        self._connections = []
        log.info("WS manager stopped ({})", self._label)

    # ------------------------------------------------------------------
    # REST fallback for critical pairs
    # ------------------------------------------------------------------

    def set_critical_pairs(self, pairs: List[str]) -> None:
        """Define which symbols receive REST fallback during WS outages."""
        self._critical_pairs = set(pairs)
        log.info("Critical pairs set ({}): {}", len(self._critical_pairs), pairs)

    def auto_populate_critical_pairs(self, symbols: List[str]) -> None:
        """Populate *_critical_pairs* from the provided symbol list.

        Call this after :meth:`start` with the top-N pairs by volume so that
        REST fallback activates automatically when WS is fully degraded even
        if :meth:`set_critical_pairs` was never called explicitly.

        Existing critical pairs are *replaced* only when the incoming list is
        non-empty; an empty list is a no-op so bootstrap ordering is flexible.
        """
        if not symbols:
            return
        self._critical_pairs = set(s.upper() for s in symbols)
        log.info(
            "Critical pairs auto-populated ({}): {}", len(self._critical_pairs), list(self._critical_pairs)[:20]
        )

    async def update_streams_for_top50(
        self,
        symbols: List[str],
        intervals: Optional[List[str]] = None,
    ) -> None:
        """Dynamically update WS streams to cover *symbols* (top-50) only.

        Computes the symmetric difference between the current subscribed kline
        streams and the desired set, then restarts the manager with the new
        stream list.  This is a full restart (stop → start) to keep the
        implementation simple; the caller should avoid calling this too
        frequently.

        This method is the entry-point for PR4 dynamic top-50 WS management:
        whenever the top-50 futures list changes, the main engine calls this
        method to shed streams for pairs that dropped out of the top-50 and
        open new streams for pairs that entered.

        Parameters
        ----------
        symbols:
            Current top-50 futures symbols (upper-case, e.g. ``"BTCUSDT"``).
        intervals:
            Kline intervals to stream for each symbol.  Defaults to
            ``["1m", "5m", "15m"]``.
        """
        if not self._running:
            log.debug("update_streams_for_top50: manager not running — skipping")
            return

        intervals = intervals or ["1m", "5m", "15m"]
        desired_streams: Set[str] = set()
        for sym in symbols:
            for tf in intervals:
                desired_streams.add(self.build_kline_stream(sym.lower(), tf))

        current_streams = set(self._subscribed_streams)
        if desired_streams == current_streams:
            log.debug("update_streams_for_top50: no stream changes required")
            return

        added = desired_streams - current_streams
        removed = current_streams - desired_streams
        log.info(
            "update_streams_for_top50: +%d / -%d streams for %d symbols (%s)",
            len(added), len(removed), len(symbols), self._label,
        )

        # Restart with the new stream list.  auto_populate_critical_pairs is
        # re-applied so the REST fallback remains aligned to the new top-50.
        await self.stop()
        await self.start(sorted(desired_streams))
        self.auto_populate_critical_pairs(symbols)

    async def _rest_fallback_loop(self) -> None:
        """Poll REST klines for critical pairs while WS is down."""
        assert self._session is not None
        if self._market == "futures":
            url_tpl = f"{self._rest_base_url}/fapi/v1/klines?symbol={{symbol}}&interval={{interval}}&limit=2"  # BUG FIX: limit=2 so raw[0] is truly closed
        else:
            url_tpl = f"{self._rest_base_url}/api/v3/klines?symbol={{symbol}}&interval={{interval}}&limit=2"  # BUG FIX: limit=2 so raw[0] is truly closed

        log.info("REST fallback loop started for {} critical pairs", len(self._critical_pairs))

        # One-time bulk backfill to warm indicator pipelines (50 candles per
        # symbol × timeframe) so scanners can produce signals immediately after
        # a WS outage rather than waiting for candle-by-candle accumulation.
        if self._data_store is not None:
            for symbol in list(self._critical_pairs):
                for interval in WS_FALLBACK_TIMEFRAMES:
                    try:
                        await self._data_store.fetch_and_store_fallback(
                            symbol, interval=interval, limit=WS_FALLBACK_BULK_LIMIT, market=self._market
                        )
                        log.info(
                            "REST fallback: bulk-seeded {} {} candles for {}",
                            WS_FALLBACK_BULK_LIMIT, interval, symbol,
                        )
                    except Exception as exc:
                        log.warning(
                            "REST fallback bulk seed failed for {} {}: {}", symbol, interval, exc
                        )
                    await asyncio.sleep(0.2)  # ~5 req/s well within Binance's 1200 req/min weight limit

        try:
            while self._running and self._rest_fallback_active:
                for symbol in list(self._critical_pairs):
                    for interval in WS_FALLBACK_POLL_INTERVALS:
                        try:
                            url = url_tpl.format(symbol=symbol, interval=interval)
                            async with self._session.get(
                                url, timeout=aiohttp.ClientTimeout(total=10),
                            ) as resp:
                                if resp.status != 200:
                                    log.debug("REST fallback {} {} status {}", symbol, interval, resp.status)
                                    continue
                                raw = await resp.json()
                            # BUG FIX: guard len>=2; raw[0]=last CLOSED candle
                            if not raw or len(raw) < 2:
                                continue
                            k = raw[0]
                            msg: dict = {
                                "e": "kline",
                                "s": symbol,
                                "k": {
                                    "i": interval,
                                    "o": str(k[1]),
                                    "h": str(k[2]),
                                    "l": str(k[3]),
                                    "c": str(k[4]),
                                    "v": str(k[5]),
                                    "x": True,
                                    "t": k[0],
                                },
                            }
                            await self._on_message(msg)
                        except asyncio.CancelledError:
                            raise
                        except Exception as exc:
                            log.debug("REST fallback error for {} {}: {}", symbol, interval, exc)
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            pass
        log.info("REST fallback loop stopped")

    def _start_rest_fallback(self) -> None:
        """Activate REST fallback if critical pairs are configured.

        The admin alert is delayed by ``WS_REST_FALLBACK_ALERT_GRACE_SEC``
        so transient drops that reconnect inside the grace window stay
        silent — they're informational only and were creating Telegram
        spam (e.g. the futures staleness watchdog force-closes every
        ``heartbeat_interval × staleness_multiplier`` ≈ 15 min and
        reconnect succeeds in <2 s, which would have alerted every cycle).

        Sustained outages (REST fallback still active after the grace
        period) still fire the alert; subsequent fires within
        ``WS_ALERT_COOLDOWN`` are coalesced into a suppressed-count
        suffix on the next post-cooldown alert so prolonged outages
        don't spam either.
        """
        if not self._critical_pairs:
            return
        if self._rest_fallback_active:
            return
        self._rest_fallback_active = True
        # Phase 1 instrumentation: bump the counter so /diag + truth report
        # can show how often this triggers.  Pre-fix this was declared but
        # never incremented.
        self._ws_rest_fallback_count += 1
        log.info(
            "ws_rest_fallback_activated label={} total={}",
            self._label, self._ws_rest_fallback_count,
        )
        self._fallback_task = asyncio.create_task(self._rest_fallback_loop())
        if self._admin_alert:
            asyncio.create_task(self._maybe_alert_after_grace())

    async def _maybe_alert_after_grace(self) -> None:
        """Wait the grace period; alert only if REST fallback is still active.

        Also enforces ``WS_ALERT_COOLDOWN`` so a sustained outage that keeps
        cycling through degraded → reconnect → degraded doesn't burst-alert
        every grace window.
        """
        await asyncio.sleep(WS_REST_FALLBACK_ALERT_GRACE_SEC)
        if not self._rest_fallback_active:
            return  # Reconnected before grace expired — transient drop, no alert.
        now = time.monotonic()
        cooldown_expired = (
            self._last_rest_fallback_alert_time is None
            or (now - self._last_rest_fallback_alert_time) > WS_ALERT_COOLDOWN
        )
        if not cooldown_expired:
            self._rest_fallback_activations_in_cooldown += 1
            return
        coalesced = self._rest_fallback_activations_in_cooldown
        self._rest_fallback_activations_in_cooldown = 0
        self._last_rest_fallback_alert_time = now
        suffix = (
            f" ({coalesced} suppressed during last {int(WS_ALERT_COOLDOWN)}s)"
            if coalesced > 0 else ""
        )
        if self._admin_alert:
            await self._admin_alert(
                f"⚠️ REST fallback activated for {self._label} critical pairs.{suffix}"
            )

    def _stop_rest_fallback(self) -> None:
        """Deactivate REST fallback once WS reconnects."""
        if not self._rest_fallback_active:
            return
        self._rest_fallback_active = False
        if self._fallback_task and not self._fallback_task.done():
            self._fallback_task.cancel()
        self._fallback_task = None

    def _connection_uses_fallback(self, conn: WSConnection) -> bool:
        return any(
            stream.split("@", 1)[0].upper() in self._critical_pairs
            for stream in conn.streams
        )

    def _sync_rest_fallback_state(self) -> None:
        # If all connections are degraded but _critical_pairs was never
        # configured, auto-extract symbols from subscribed kline streams so
        # that the REST fallback activates rather than remaining a no-op.
        all_degraded = self._connections and all(c.degraded for c in self._connections)
        if all_degraded and not self._critical_pairs and self._subscribed_streams:
            extracted: List[str] = []
            for stream in self._subscribed_streams:
                if "@kline_" in stream:
                    symbol = stream.split("@", 1)[0].upper()
                    extracted.append(symbol)
            if extracted:
                # Deduplicate while preserving insertion order for logging
                seen: set = set()
                unique: List[str] = []
                for s in extracted:
                    if s not in seen:
                        seen.add(s)
                        unique.append(s)
                self._critical_pairs = set(unique[:20])
                log.warning(
                    "WS fully degraded with empty critical_pairs — "
                    "auto-extracted {} symbols from subscribed streams",
                    len(self._critical_pairs),
                )

        should_run = any(
            conn.degraded and self._connection_uses_fallback(conn)
            for conn in self._connections
        )
        if should_run:
            self._start_rest_fallback()
        else:
            self._stop_rest_fallback()

    def _set_connection_degraded(self, conn: WSConnection, degraded: bool) -> None:
        if conn.degraded == degraded:
            return
        conn.degraded = degraded
        # Reconnect-duration instrumentation (Phase 1, 2026-05-08).
        #
        # On drop (degraded=True):  stamp ``degraded_since`` for later diff.
        # On restore (degraded=False):
        #   * compute drop → restored duration in ms
        #   * write to ``last_reconnect_ms`` for /diag exposure
        #   * emit a parseable ``ws_reconnect_duration_ms`` log marker that
        #     the truth-report parser will aggregate into a distribution
        #   * bump the recovery counter so /diag shows total recoveries
        #     since boot
        now = time.monotonic()
        if degraded:
            conn.degraded_since = now
        else:
            if conn.degraded_since > 0:
                duration_ms = (now - conn.degraded_since) * 1000.0
                conn.last_reconnect_ms = duration_ms
                self._ws_reconnection_count += 1
                # Snapshot the index for log readability — connections
                # don't carry an explicit ID, so we use the position in
                # ``_connections``.
                idx = (
                    self._connections.index(conn)
                    if conn in self._connections else -1
                )
                log.info(
                    "ws_reconnect_duration_ms label={} conn={} duration_ms={:.0f} "
                    "attempts={} streams={}",
                    self._label, idx, duration_ms,
                    conn.reconnect_attempts, len(conn.streams),
                )
                conn.degraded_since = 0.0
        self._sync_rest_fallback_state()

    # ------------------------------------------------------------------
    # Connection loop
    # ------------------------------------------------------------------

    async def _run_connection(self, conn: WSConnection) -> None:
        while self._running:
            try:
                await self._connect(conn)
                self._set_connection_degraded(conn, False)
                await self._listen(conn)
            except asyncio.CancelledError:
                return
            except Exception as exc:
                log.warning("WS connection error: {}", exc)
            if self._running:
                self._set_connection_degraded(conn, True)
                self._total_drops += 1
                # Only alert after multiple consecutive failures on the same
                # connection.  Transient drops reconnect on the first or
                # second attempt and are normal network jitter — alerting
                # starts at the third consecutive failure (reconnect_attempts
                # is 0-indexed, so >= 2 means the third attempt).
                if self._admin_alert and conn.reconnect_attempts >= 2:
                    now = time.monotonic()
                    if now - self._last_alert_time > WS_ALERT_COOLDOWN:
                        self._last_alert_time = now
                        asyncio.create_task(
                            self._admin_alert(
                                f"⚠️ WebSocket connection lost ({self._label}, "
                                f"attempt {conn.reconnect_attempts + 1}, "
                                f"total drops: {self._total_drops}). Reconnecting…"
                            )
                        )
                delay = min(
                    WS_RECONNECT_BASE_DELAY * (2 ** conn.reconnect_attempts),
                    WS_RECONNECT_MAX_DELAY,
                )
                # Add ±25% jitter to prevent thundering-herd reconnects when
                # multiple connections drop simultaneously.
                jitter = delay * random.uniform(-0.25, 0.25)
                actual_delay = max(0.5, delay + jitter)
                conn.reconnect_attempts += 1
                log.info(
                    "Reconnecting in {:.1f}s (attempt {}) …",
                    actual_delay,
                    conn.reconnect_attempts,
                )
                # Recycle the aiohttp session periodically to clear stale TCP
                # connection pools and DNS caches after extended outages.
                if conn.reconnect_attempts % WS_SESSION_RECYCLE_ATTEMPTS == 0:
                    log.warning(
                        "Recycling HTTP session after {} consecutive failures ({})",
                        conn.reconnect_attempts, self._label,
                    )
                    await self._recreate_session(force_dns_reresolution=True)
                # Escalation alert: after many consecutive failures the issue
                # may require manual intervention (e.g. IP ban, firewall change).
                if (
                    conn.reconnect_attempts == WS_RECONNECT_FAIL_ALERT_THRESHOLD
                    and self._admin_alert
                ):
                    asyncio.create_task(
                        self._admin_alert(
                            f"🚨 WebSocket unable to reconnect after "
                            f"{WS_RECONNECT_FAIL_ALERT_THRESHOLD} attempts "
                            f"({self._label}) — manual intervention may be needed."
                        )
                    )
                await asyncio.sleep(actual_delay)

    def _build_combined_stream_url(self, streams: List[str]) -> str:
        """Build a Binance combined-stream WebSocket URL.

        Per Binance docs:
          - ``/ws/<single_stream>``          single-stream raw endpoint
          - ``/stream?streams=<s1>/<s2>``    combined-stream endpoint

        This manager always uses combined-stream because we subscribe to
        many streams per connection.  The helper exists as a separate
        method (rather than inline in ``_connect``) so test code can
        exercise the URL construction without spinning up an aiohttp
        session — see ``TestBuildCombinedStreamUrl``.

        Normalisation rules (defensive against env-override drift):
          1. If ``_base_url`` ends in ``/ws`` or ``/stream``, strip it
             and log a one-time warning if the stripped suffix was
             ``/ws`` (legacy operators may still have that in .env).
          2. Always append ``/stream?streams=<joined>``.

        Result: regardless of what ``BINANCE_FUTURES_WS_BASE`` is set
        to in the env, the URL we hand to ``ws_connect`` is the
        documented combined-stream form.
        """
        base = self._base_url
        # Strip a trailing slash so the suffix-check is unambiguous.
        if base.endswith("/"):
            base = base[:-1]
        for legacy_suffix in ("/stream", "/ws"):
            if base.endswith(legacy_suffix):
                stripped = legacy_suffix
                base = base[: -len(legacy_suffix)]
                # Log once per process if we had to fix the legacy /ws
                # path — operator should update .env eventually so the
                # value matches the new config default.  Loguru
                # dedups identical messages by record signature, so
                # the warning emits at most once per reconnect cycle.
                if stripped == "/ws" and not getattr(self, "_warned_legacy_ws_base", False):
                    log.warning(
                        "BINANCE_*_WS_BASE ({}) ends in /ws — auto-correcting to /stream "
                        "(Binance combined-stream endpoint).  Update .env to silence this warning: "
                        "BINANCE_FUTURES_WS_BASE=wss://fstream.binance.com/stream",
                        self._label,
                    )
                    # Stamp the flag so subsequent reconnects don't spam.
                    self._warned_legacy_ws_base = True
                break
        stream_path = "/".join(streams)
        return f"{base}/stream?streams={stream_path}"

    async def _connect(self, conn: WSConnection) -> None:
        assert self._session is not None
        # Combined-stream URL per Binance docs.  See PR #388 for the
        # initial rationale; the short form is "/ws/<s1>/<s2>/..." was
        # unofficial and Binance Futures silently dropped subscriptions
        # beyond the first stream.  /stream?streams=... is documented.
        #
        # 2026-05-14 trace data revealed the env-override trap: prod
        # `.env` on the VPS had ``BINANCE_FUTURES_WS_BASE=
        # wss://fstream.binance.com/ws`` (the legacy value) which
        # overrode the new config default.  Resulting URLs were
        # ``/ws?streams=btcusdt@kline_1m/...`` — Binance accepted the
        # TCP+WS handshake on /ws but then ignored the ?streams= query
        # (the /ws endpoint takes the stream name as a PATH suffix, not
        # a query string), leaving the connection subscribed to
        # NOTHING.  Trace showed connect_success followed by 305 s of
        # zero frames on both connections before the watchdog tripped.
        #
        # Defensive normalisation: regardless of what ``_base_url`` is
        # set to (e.g. ``.../ws`` legacy, ``.../stream`` correct,
        # or no trailing path at all), strip any trailing ``/ws`` or
        # ``/stream`` and always re-append ``/stream``.  Output is
        # guaranteed to be the documented combined-stream form.
        url = self._build_combined_stream_url(conn.streams)

        # WS-trace: stamp the connect attempt with conn index, label,
        # stream count, and the URL prefix so the operator can correlate
        # close events to the right connection.  URL is truncated at 220
        # chars to avoid 200-stream URLs (>5 KB) bloating the trace file.
        try:
            conn_idx = self._connections.index(conn) if conn in self._connections else -1
        except ValueError:
            conn_idx = -1
        url_preview = (url if len(url) <= 220 else url[:220] + f"... ({len(url) - 220} chars truncated)")
        connect_t0 = time.monotonic()
        ws_trace.info(
            f"<WS:{self._label}> connect_start conn={conn_idx} streams={len(conn.streams)} url={url_preview}"
        )

        try:
            conn.ws = await self._session.ws_connect(url, heartbeat=self._heartbeat_interval)
        except Exception as exc:
            ws_trace.warning(
                f"<WS:{self._label}> connect_fail conn={conn_idx} duration_ms={(time.monotonic() - connect_t0) * 1000:.0f} "
                f"exc_type={type(exc).__name__} msg={str(exc)[:200]!r}"
            )
            raise
        ws_trace.info(
            f"<WS:{self._label}> connect_success conn={conn_idx} duration_ms={(time.monotonic() - connect_t0) * 1000:.0f}"
        )
        conn.last_pong = time.monotonic()
        conn.reconnect_attempts = 0
        # NOTE: do NOT set ``conn.degraded = False`` here.  The
        # ``_set_connection_degraded`` wrapper that ``_run_connection``
        # calls immediately after a successful ``_connect`` carries the
        # recovery instrumentation (duration measurement, recovery-counter
        # increment, ``ws_reconnect_duration_ms`` log marker, clearing
        # ``degraded_since``).  If we set the flag here, the wrapper's
        # ``if conn.degraded == degraded: return`` early-return hits and
        # the instrumentation never runs — that's exactly the bug
        # surfaced by the 2026-05-09 diag where futures showed
        # ``drops=26 recoveries=0`` and ``degraded_for=229.4s`` while
        # ``degraded=False`` (contradictory state).  Letting the wrapper
        # own the False→True→False state machine fixes it.
        conn.last_ping_time = 0.0
        conn.ping_latency_ms = 0.0
        # Reset the data-flow staleness state on fresh connect.  ``connected_ts``
        # protects the health-check loop from force-closing a connection in its
        # resubscribe phase; ``low_msgrate_since`` is cleared so a previous
        # connection's stale state doesn't trip the new connection on its first
        # health-check tick.
        conn.connected_ts = time.monotonic()
        conn.low_msgrate_since = 0.0
        conn.health_msg_count = 0
        # Clear per-stream timestamps — old stamps from a previous connection
        # are stale.  trace_summary_last_ts is reset so the first summary
        # after reconnect doesn't get throttled.
        conn.stream_data_ts.clear()
        conn.trace_summary_last_ts = 0.0
        # Reset the per-conn sample / msg-type counters so the FIRST
        # post-reconnect frames are captured for diagnosis (rather
        # than carrying forward the previous connection's "already
        # sampled" state).
        conn.samples_logged = 0
        conn.msg_type_counts = {}
        self._subscribed_streams.update(conn.streams)
        log.info("Connected WS: {} streams", len(conn.streams))

    async def _listen(self, conn: WSConnection) -> None:
        assert conn.ws is not None
        try:
            conn_idx = self._connections.index(conn) if conn in self._connections else -1
        except ValueError:
            conn_idx = -1
        async for msg in conn.ws:
            # ---- Diagnostic: log the first N raw messages regardless of type ----
            # Trace 2026-05-14 showed stream_summary with ``never_seen=all``
            # and ``health_msg_count=0`` despite connect_success on the
            # correct ``/stream?streams=...`` URL.  The hypothesis is
            # Binance is sending BINARY frames (or some shape our parser
            # doesn't recognise) which the previous ``_listen`` silently
            # skipped.  Per-conn sampling logs the first
            # ``WS_TRACE_SAMPLE_FIRST_N`` messages so the next /ws_log
            # pull shows what's actually on the wire.  The counter resets
            # on _connect so each reconnect gets a fresh sample window.
            type_name = getattr(msg.type, "name", str(msg.type))
            conn.msg_type_counts[type_name] = conn.msg_type_counts.get(type_name, 0) + 1
            if conn.samples_logged < WS_TRACE_SAMPLE_FIRST_N:
                conn.samples_logged += 1
                # Truncate data preview at 200 chars and tag whether it's
                # str or bytes.  Bytes => Binance is sending BINARY which
                # could be gzip-compressed JSON we need to decode.
                raw = msg.data
                kind = "bytes" if isinstance(raw, (bytes, bytearray)) else "str"
                if isinstance(raw, (bytes, bytearray)):
                    preview = repr(bytes(raw[:120]))
                elif raw is None:
                    preview = "None"
                else:
                    preview = repr(str(raw)[:200])
                ws_trace.info(
                    f"<WS:{self._label}> raw_sample conn={conn_idx} n={conn.samples_logged} "
                    f"type={type_name} kind={kind} data={preview}"
                )

            if msg.type == aiohttp.WSMsgType.TEXT:
                # Any incoming data message proves the connection is alive;
                # update last_pong so is_healthy reflects real liveness.
                now_mono = time.monotonic()
                conn.last_pong = now_mono
                # Count this towards the health-check loop's msgs-per-min
                # window.  Prior to 2026-05-14 this counter was declared on
                # WSConnection but never incremented, so ``_health_check_loop``
                # always read rate=0 and logged "low message rate" forever
                # without taking action.  Increment-on-TEXT (not on PING/PONG)
                # so the rate truly reflects kline-data flow.
                conn.health_msg_count += 1
                try:
                    data = json.loads(msg.data)
                except Exception as exc:
                    log.debug("Message parse error: {}", exc)
                    continue
                # WS-trace: capture per-stream data arrival from the
                # combined-stream wrapper.  Tracks which subscribed streams
                # are actually delivering data — distinguishes "Binance
                # silently unsubscribed a subset" from "everything's flowing".
                # First-data-per-stream gets its own trace event so the
                # operator can spot streams that connect but never deliver.
                if isinstance(data, dict):
                    stream_name = data.get("stream")
                    if isinstance(stream_name, str) and stream_name:
                        first_seen = stream_name not in conn.stream_data_ts
                        conn.stream_data_ts[stream_name] = now_mono
                        if first_seen:
                            delay_s = now_mono - conn.connected_ts if conn.connected_ts > 0 else 0.0
                            ws_trace.info(
                                f"<WS:{self._label}> first_data conn={conn_idx} stream={stream_name} delay_after_connect_s={delay_s:.2f}"
                            )
                    # Subscribe / error response from Binance:
                    #   success: {"result": null, "id": 1}
                    #   error:   {"error": {"code": -1121, "msg": "Invalid symbol"}}
                    # Detect by absence of "stream"/"e" but presence of
                    # "result" or "error".  These don't reach the engine
                    # message handler because they don't match any event
                    # type — but they're gold for diagnosing silent
                    # subscription failures.
                    if "stream" not in data and "e" not in data:
                        raw = str(msg.data)[:200]
                        if "error" in data:
                            ws_trace.warning(
                                f"<WS:{self._label}> subscribe_error conn={conn_idx} raw={raw!r}"
                            )
                        elif "result" in data:
                            ws_trace.info(
                                f"<WS:{self._label}> subscribe_ack conn={conn_idx} raw={raw!r}"
                            )
                try:
                    await self._on_message(data)
                except Exception as exc:
                    log.debug("Message handler error: {}", exc)
            elif msg.type in (aiohttp.WSMsgType.PING, aiohttp.WSMsgType.PONG):
                # Binance sends PING frames every ~3 minutes; aiohttp auto-replies
                # with PONG.  Treat both as proof that the connection is alive.
                now_mono = time.monotonic()
                conn.last_pong = now_mono
                # When a PONG arrives, measure RTT against the last manual ping
                # sent by the watchdog and reset last_ping_time so the watchdog
                # does not report a false timeout on the next iteration.
                if msg.type == aiohttp.WSMsgType.PONG and conn.last_ping_time > 0:
                    conn.ping_latency_ms = (now_mono - conn.last_ping_time) * 1000
                    conn.last_ping_time = 0.0
            elif msg.type == aiohttp.WSMsgType.BINARY:
                # Binance has been observed to send gzip-compressed JSON
                # over some WS endpoints.  We previously fell through to
                # the default branch and silently dropped these.  Attempt
                # to decompress + parse; treat data flow as alive
                # regardless so the watchdog doesn't trip on a healthy
                # but binary-encoded connection.
                now_mono = time.monotonic()
                conn.last_pong = now_mono
                conn.health_msg_count += 1
                raw = msg.data
                decoded = None
                decode_method: str = "raw"
                try:
                    import gzip
                    try:
                        decompressed = gzip.decompress(raw)
                        decoded = decompressed.decode("utf-8", errors="replace")
                        decode_method = "gzip"
                    except (OSError, EOFError):
                        # Not gzip — try raw bytes-to-str
                        decoded = raw.decode("utf-8", errors="replace")
                        decode_method = "utf8"
                except Exception as exc:
                    log.debug("BINARY decode error: {}", exc)
                if decoded is not None:
                    try:
                        data = json.loads(decoded)
                        # Same wrapper-unwrap as TEXT branch — propagates
                        # to the engine handler.
                        if isinstance(data, dict):
                            stream_name = data.get("stream")
                            if isinstance(stream_name, str) and stream_name:
                                first_seen = stream_name not in conn.stream_data_ts
                                conn.stream_data_ts[stream_name] = now_mono
                                if first_seen:
                                    delay_s = now_mono - conn.connected_ts if conn.connected_ts > 0 else 0.0
                                    ws_trace.info(
                                        f"<WS:{self._label}> first_data conn={conn_idx} "
                                        f"stream={stream_name} delay_after_connect_s={delay_s:.2f} "
                                        f"(via BINARY/{decode_method})"
                                    )
                        await self._on_message(data)
                    except Exception as exc:
                        log.debug("BINARY JSON parse error: {}", exc)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                # Capture the close code + reason — previously dropped on
                # the floor.  Binance close codes:
                #   1000 = normal closure
                #   1006 = abnormal (TCP RST)
                #   1011 = server error
                #   4xxx = Binance-specific (rate limit etc.)
                code = msg.data if isinstance(msg.data, int) else None
                reason = ""
                try:
                    if msg.extra is not None:
                        reason = str(msg.extra)[:200]
                except Exception:
                    reason = ""
                ws_trace.warning(
                    f"<WS:{self._label}> close_received conn={conn_idx} code={code} reason={reason!r}"
                )
                log.warning("WS closed/error, will reconnect")
                break
            elif msg.type == aiohttp.WSMsgType.ERROR:
                err_data = str(msg.data)[:200] if msg.data is not None else ""
                ws_trace.warning(
                    f"<WS:{self._label}> error_received conn={conn_idx} data={err_data!r}"
                )
                log.warning("WS closed/error, will reconnect")
                break

    # ------------------------------------------------------------------
    # Health watchdog
    # ------------------------------------------------------------------

    async def _health_watchdog(self) -> None:
        """Periodically force-close truly stale connections so _run_connection reconnects.

        Only one actionable check is performed:

        1. **Staleness** – no data (TEXT, PING, or PONG) for
           ``heartbeat_interval × staleness_multiplier`` seconds → connection is
           dead, force-close so ``_run_connection`` can reconnect.

        aiohttp's built-in ``heartbeat=`` keepalive already sends PING frames
        and closes the connection when the remote end stops responding, so
        additional manual ping-timeout force-closes are unnecessary and were
        causing a repeating 10-minute drop/alert cycle (manual pings sent every
        ``heartbeat_interval`` seconds, but the 5 s ``WS_PING_TIMEOUT_MS``
        threshold was always exceeded by the next tick, killing healthy
        connections).

        A manual ping is still sent for **latency measurement** purposes.  If a
        PONG comes back, ``_listen`` records the RTT in ``conn.ping_latency_ms``
        which is available to callers.  No connection is force-closed based on
        the measured latency.
        """
        try:
            while self._running:
                await asyncio.sleep(self._heartbeat_interval)
                now = time.monotonic()
                for conn in self._connections:
                    if not (conn.ws and not conn.ws.closed):
                        continue

                    # Staleness check: no data at all for an extended period
                    stale_threshold = max(1.0, self._heartbeat_interval * self._staleness_multiplier)
                    if (now - conn.last_pong) >= stale_threshold:
                        age_s = now - conn.last_pong
                        log.warning(
                            "Watchdog: stale WS connection ({:.0f}s since last data) — force-closing to trigger reconnect",
                            age_s,
                        )
                        conn_idx = -1
                        try:
                            conn_idx = self._connections.index(conn)
                        except ValueError:
                            pass
                        ws_trace.warning(
                            f"<WS:{self._label}> watchdog_force_close conn={conn_idx} age_s={age_s:.0f} threshold_s={stale_threshold:.0f}"
                        )
                        conn.last_ping_time = 0.0
                        await conn.ws.close()
                        continue

                    # Log (but do NOT force-close) if a previous manual ping
                    # never received a PONG.  This is informational only;
                    # aiohttp's built-in heartbeat handles actual keepalive.
                    if conn.last_ping_time > 0:
                        overdue_ms = (now - conn.last_ping_time) * 1000
                        if overdue_ms > WS_PING_TIMEOUT_MS:
                            log.debug(
                                "Watchdog: manual ping PONG overdue ({:.0f}ms) — "
                                "informational only, aiohttp heartbeat handles keepalive",
                                overdue_ms,
                            )
                            conn.last_ping_time = 0.0

                    # Send a fresh manual ping to probe latency on the next tick
                    try:
                        conn.last_ping_time = time.monotonic()
                        await conn.ws.ping()
                    except Exception as exc:
                        log.debug("Watchdog ping send error ({}): {}", self._label, exc)
                        conn.last_ping_time = 0.0
        except asyncio.CancelledError:
            pass

    # ------------------------------------------------------------------
    # Dynamic subscription helpers
    # ------------------------------------------------------------------

    async def _recreate_session(self, force_dns_reresolution: bool = False) -> None:
        """Close and recreate the aiohttp session to clear stale connections.

        Parameters
        ----------
        force_dns_reresolution:
            When ``True``, create the TCP connector with ``force_close=True``
            so that no connections are reused from the pool.  This forces the
            OS to resolve DNS again, which helps when the Binance endpoint IP
            changes or when a previous outage was caused by a stale ARP/DNS
            cache.
        """
        if self._session and not self._session.closed:
            try:
                await self._session.close()
            except Exception as exc:
                log.debug("Error closing stale session ({}): {}", self._label, exc)
        connector = aiohttp.TCPConnector(
            keepalive_timeout=30,
            force_close=force_dns_reresolution,
        )
        self._session = aiohttp.ClientSession(connector=connector)

    def build_kline_stream(self, symbol: str, interval: str) -> str:
        return f"{symbol.lower()}@kline_{interval}"

    def build_trade_stream(self, symbol: str) -> str:
        return f"{symbol.lower()}@trade"

    def build_depth_stream(self, symbol: str, level: int = 5) -> str:
        return f"{symbol.lower()}@depth{level}@100ms"

    def build_force_order_stream(self, symbol: str) -> str:
        """Return the Binance Futures liquidation stream name for *symbol*.

        Subscribing to this stream delivers ``forceOrder`` events whenever a
        position in *symbol* is force-liquidated.  The event payload includes
        the order side (``"BUY"`` = short liq'd, ``"SELL"`` = long liq'd),
        quantity, and average fill price.
        """
        return f"{symbol.lower()}@forceOrder"

    @property
    def stream_count(self) -> int:
        return sum(len(c.streams) for c in self._connections)

    @property
    def health_ratio(self) -> float:
        """Fraction of connections that are currently open and non-stale (0.0–1.0).

        Unlike :attr:`is_healthy` which requires *all* connections to be
        healthy, this property returns a continuous value so callers can
        make proportional decisions (e.g. reduce REST fallback intensity when
        only a minority of connections are down).

        Returns ``1.0`` when no connections have been started yet so callers
        treat the manager as fully healthy before :meth:`start` is called.
        """
        if not self._connections:
            return 1.0
        now = time.monotonic()
        healthy_count = sum(
            1 for c in self._connections
            if c.ws is not None
            and not c.ws.closed
            and (now - c.last_pong) < self._heartbeat_interval * self._staleness_multiplier
        )
        return healthy_count / len(self._connections)

    @property
    def is_healthy(self) -> bool:
        if not self._connections:
            return True
        now = time.monotonic()
        open_connections = [
            c for c in self._connections if c.ws is not None and not c.ws.closed
        ]
        if not open_connections or len(open_connections) != len(self._connections):
            return False
        return all(
            (now - c.last_pong) < self._heartbeat_interval * self._staleness_multiplier
            for c in open_connections
        )

    @property
    def ws_rest_fallback_count(self) -> int:
        return self._ws_rest_fallback_count

    @property
    def ws_reconnection_count(self) -> int:
        return self._ws_reconnection_count

    @property
    def total_drops(self) -> int:
        """Public read of the drop counter for /diag rendering."""
        return self._total_drops

    def get_connection_states(self) -> List[Dict[str, Any]]:
        """Per-connection snapshot for /diag rendering.

        Each entry: ``{conn: int, streams: int, healthy: bool, degraded: bool,
        degraded_for_sec: float, last_reconnect_ms: float,
        sec_since_last_msg: float, ping_latency_ms: float}``.

        ``degraded_for_sec`` is 0 when the connection is healthy; non-zero
        only while a drop is in-flight.  ``last_reconnect_ms`` shows the
        most recent recovery time so operators can spot trends.
        """
        now = time.monotonic()
        out: List[Dict[str, Any]] = []
        for idx, conn in enumerate(self._connections):
            stale_threshold = max(
                1.0, self._heartbeat_interval * self._staleness_multiplier
            )
            sec_since_msg = (
                (now - conn.last_pong) if conn.last_pong > 0 else -1.0
            )
            healthy = (
                conn.ws is not None
                and not conn.ws.closed
                and sec_since_msg < stale_threshold
                and sec_since_msg >= 0
            )
            degraded_for = (
                (now - conn.degraded_since) if conn.degraded_since > 0 else 0.0
            )
            out.append({
                "conn": idx,
                "streams": len(conn.streams),
                "healthy": healthy,
                "degraded": conn.degraded,
                "degraded_for_sec": round(degraded_for, 1),
                "last_reconnect_ms": round(conn.last_reconnect_ms, 0),
                "sec_since_last_msg": round(sec_since_msg, 1)
                    if sec_since_msg >= 0 else -1,
                "ping_latency_ms": round(conn.ping_latency_ms, 1),
                "reconnect_attempts": conn.reconnect_attempts,
            })
        return out

    def get_healthy_connection_ratio(self) -> float:
        """Return ratio of healthy connections (0.0–1.0)."""
        if not self._connections:
            return 1.0
        healthy = sum(
            1 for c in self._connections
            if c.ws is not None and not c.ws.closed
        )
        return healthy / len(self._connections)

    async def _health_check_loop(self) -> None:
        """Periodically assess data-flow health and force-close silent connections.

        Two independent checks run every ``WS_HEALTH_CHECK_INTERVAL`` (default
        30 s):

        1. **Per-connection low-rate check** — message rate (msgs/min) computed
           over the elapsed window.  When it stays below
           ``WS_MIN_MESSAGE_RATE`` for ``WS_LOW_MSGRATE_FORCE_CLOSE_AFTER_SEC``
           (default 90 s) continuous, force-close so ``_run_connection``
           reconnects.  This catches the silent-but-pingable failure mode:
           aiohttp's heartbeat keeps the socket alive on PING/PONG even when
           TEXT frames have stopped arriving, so the ``last_pong``-based
           ``_health_watchdog`` is fooled.  Increment-on-TEXT in ``_listen``
           gives the actionable signal.

        2. **Per-symbol staleness check** — when a ``data_store`` is wired,
           read ``last_kline_age_seconds(symbol, "1m")`` for each subscribed
           symbol and count those above
           ``WS_PER_SYMBOL_STALENESS_THRESHOLD_SEC`` (default 180 s) as stale.
           When the stale ratio exceeds ``WS_PER_SYMBOL_STALENESS_RATIO``
           (default 0.5), force-close all connections.  This catches the case
           where a connection's aggregate rate is acceptable but a majority
           of individual symbol streams have gone silent inside it — e.g.,
           Binance reusing the WS but quietly dropping a subset of streams
           after a network blip.

        Both checks honor a ``WS_HEALTH_CHECK_MIN_CONN_AGE_SEC`` (default 120 s)
        guard so a freshly-reconnected connection isn't churned during the
        30-60 s resubscribe window before kline data begins arriving.

        Admin Telegram alert fires on every force-close, throttled by
        ``WS_ALERT_COOLDOWN`` (shared with the REST-fallback alert path) so
        prolonged outages don't spam.
        """
        while self._running:
            await asyncio.sleep(WS_HEALTH_CHECK_INTERVAL)
            if not self._connections:
                continue
            now = time.monotonic()

            # ---- Per-connection low message-rate check ----
            for idx, conn in enumerate(self._connections):
                if conn.ws is None or conn.ws.closed:
                    # Connection is already dead; reset counters and skip.
                    conn.health_check_ts = now
                    conn.health_msg_count = 0
                    conn.low_msgrate_since = 0.0
                    self._connection_message_rates[idx] = 0.0
                    continue

                elapsed = now - conn.health_check_ts if conn.health_check_ts > 0 else now
                msg_count = conn.health_msg_count
                rate = (msg_count / elapsed) * 60.0 if elapsed > 0 else 0.0
                self._connection_message_rates[idx] = rate

                # Skip newly-connected connections — give them time to
                # resubscribe before judging their throughput.
                conn_age = now - conn.connected_ts if conn.connected_ts > 0 else 0.0
                under_age = conn_age < WS_HEALTH_CHECK_MIN_CONN_AGE_SEC

                if rate < WS_MIN_MESSAGE_RATE:
                    if conn.low_msgrate_since == 0.0:
                        conn.low_msgrate_since = now
                    low_for = now - conn.low_msgrate_since
                    if not under_age and low_for >= WS_LOW_MSGRATE_FORCE_CLOSE_AFTER_SEC:
                        log.warning(
                            "Health-check: WS conn[{}] ({}) silent for {:.0f}s "
                            "(rate={:.2f} msgs/min, threshold={:.2f}) — force-closing to trigger reconnect",
                            idx, self._label, low_for, rate, WS_MIN_MESSAGE_RATE,
                        )
                        ws_trace.warning(
                            f"<WS:{self._label}> health_force_close conn={idx} silent_s={low_for:.0f} rate={rate:.2f} threshold={WS_MIN_MESSAGE_RATE:.2f}"
                        )
                        await self._alert_admin_throttled(
                            f"WS {self._label} conn[{idx}] data-silent {low_for:.0f}s "
                            f"({rate:.2f} msgs/min) — forcing reconnect",
                            alert_key=f"low_msgrate:{idx}",
                        )
                        try:
                            await conn.ws.close()
                        except Exception as exc:
                            log.debug("Force-close exception (ignored): {}", exc)
                        conn.low_msgrate_since = 0.0
                else:
                    # Rate recovered — clear the timer.
                    conn.low_msgrate_since = 0.0

                # Reset rolling counters for the next window
                conn.health_check_ts = now
                conn.health_msg_count = 0

                # ---- WS-trace: periodic stream summary ----
                # Emit ``stream_summary`` for this connection every
                # ``WS_TRACE_SUMMARY_INTERVAL_SEC`` so the operator can spot
                # silent-stream subsets in real time (this is the central
                # diagnostic the URL-format / per-conn-limit hypotheses
                # need to verify).
                if (now - conn.trace_summary_last_ts) >= WS_TRACE_SUMMARY_INTERVAL_SEC:
                    conn.trace_summary_last_ts = now
                    total_subscribed = len(conn.streams)
                    silent_streams: List[str] = []
                    seen_streams = 0
                    for stream in conn.streams:
                        last_ts = conn.stream_data_ts.get(stream)
                        if last_ts is None:
                            silent_streams.append(stream)
                        else:
                            seen_streams += 1
                            if (now - last_ts) > WS_TRACE_SUMMARY_STALENESS_SEC:
                                silent_streams.append(stream)
                    active = total_subscribed - len(silent_streams)
                    sample = ",".join(silent_streams[:5])
                    # Per-msg-type counts surface "BINARY frames arrived
                    # but parser ignored them" as a distinct state from
                    # "absolutely nothing arrived".  Sorted for stability.
                    type_counts = ",".join(
                        f"{k}={v}" for k, v in sorted(conn.msg_type_counts.items())
                    ) or "(none)"
                    ws_trace.info(
                        f"<WS:{self._label}> stream_summary conn={idx} "
                        f"active={active}/{total_subscribed} silent={len(silent_streams)} "
                        f"never_seen={total_subscribed - seen_streams} "
                        f"msg_types={type_counts} "
                        f"silent_sample={sample if sample else '(none)'}"
                    )

            # ---- Per-symbol staleness check ----
            # Runs only when the manager was wired with a ``data_store``
            # (HistoricalDataStore-like) that exposes
            # ``last_kline_age_seconds(symbol, interval)``.  The check is
            # whole-manager, not per-connection, because a stale-symbol
            # majority signal usually means the upstream WS feed is dropping
            # a subset of streams across the whole session; restarting just
            # one connection doesn't help.
            await self._check_per_symbol_staleness(now)

    async def _check_per_symbol_staleness(self, now_mono: float) -> None:
        """Force-close all connections when too many symbols have stale klines.

        Separated from ``_health_check_loop`` to keep the loop body readable
        and to make this leg independently mockable in tests.
        """
        store = self._data_store
        if store is None:
            return
        age_fn = getattr(store, "last_kline_age_seconds", None)
        if not callable(age_fn):
            return

        # Symbols are the kline streams' first segment, e.g. "btcusdt@kline_1m"
        # → "BTCUSDT".  Use the union of subscribed streams across all
        # connections so a disabled connection's symbols aren't double-counted.
        symbols: Set[str] = set()
        for conn in self._connections:
            for stream in conn.streams:
                head = stream.split("@", 1)[0]
                if head:
                    symbols.add(head.upper())
        if not symbols:
            return

        threshold = WS_PER_SYMBOL_STALENESS_THRESHOLD_SEC
        stale_count = 0
        for symbol in symbols:
            try:
                age = age_fn(symbol, "1m")
            except Exception:
                continue
            if age is None:
                # Never recorded — count as stale only if the manager has been
                # alive long enough that we should have seen a frame by now.
                # Use the same min-conn-age guard so a fresh boot doesn't
                # immediately trip on never-seen-data symbols.
                stale_count += 1
                continue
            if age > threshold:
                stale_count += 1

        ratio = stale_count / len(symbols)
        if ratio < WS_PER_SYMBOL_STALENESS_RATIO:
            return

        # Skip the action if every connection is still under min-conn-age —
        # we'd just churn a fresh reconnect that hasn't had time to deliver.
        all_under_age = all(
            (now_mono - c.connected_ts) < WS_HEALTH_CHECK_MIN_CONN_AGE_SEC
            for c in self._connections
            if c.connected_ts > 0
        )
        if all_under_age:
            return

        log.warning(
            "Per-symbol staleness: {}/{} ({:.0%}) of {} symbols stale "
            "(threshold={:.0f}s, ratio_threshold={:.0%}) — force-closing all conns",
            stale_count, len(symbols), ratio, self._label,
            threshold, WS_PER_SYMBOL_STALENESS_RATIO,
        )
        ws_trace.warning(
            f"<WS:{self._label}> per_symbol_force_close stale={stale_count}/{len(symbols)} ratio={ratio:.2f} threshold_s={threshold:.0f}"
        )
        await self._alert_admin_throttled(
            f"WS {self._label} per-symbol stale: {stale_count}/{len(symbols)} "
            f"symbols silent >{threshold:.0f}s — forcing all-conn reconnect",
            alert_key="per_symbol_stale",
        )
        for conn in self._connections:
            if conn.ws is not None and not conn.ws.closed:
                try:
                    await conn.ws.close()
                except Exception as exc:
                    log.debug("Force-close exception (ignored): {}", exc)

    async def _alert_admin_throttled(self, message: str, *, alert_key: str) -> None:
        """Send an admin Telegram alert with per-key throttling.

        Uses ``self._alert_keyed_ts[alert_key]`` so the data-staleness paths
        (low_msgrate:N, per_symbol_stale) dedup independently from the
        REST-fallback path (which uses ``_last_alert_time`` /
        ``_last_rest_fallback_alert_time``).  When no callback is wired
        (tests, or admin-alerts disabled) this is a noop.
        """
        if self._admin_alert is None:
            return
        now = time.monotonic()
        last = self._alert_keyed_ts.get(alert_key)
        # ``last is None`` means never-alerted-yet for this key.  Always let
        # the first alert through — otherwise an alert that fires within the
        # first ``WS_ALERT_COOLDOWN`` seconds of process boot would compare
        # against last=0.0 with ``now`` still small from a fresh monotonic
        # clock, suppressing the very alert that mattered most (boot-time
        # WS failures).
        if last is not None and (now - last) < WS_ALERT_COOLDOWN:
            return
        self._alert_keyed_ts[alert_key] = now
        try:
            await self._admin_alert(message)
        except Exception as exc:
            log.debug("admin_alert exception (ignored): {}", exc)
