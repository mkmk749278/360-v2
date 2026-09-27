"""CoinDCX private event stream — latency, never safety.

One socket per user **holding a live CoinDCX record** (zero sockets otherwise).
Each ``df-order-update`` / ``df-position-update`` only nudges the reconciler
for that user; the reconciler reads the exchange and decides.  So a dropped
socket, a missed event or a malformed payload costs seconds of latency and
nothing else: the stop and target rest on CoinDCX, and the reconciler still
runs every cycle.

Transport, measured against the live endpoint on 2026-09-27: Socket.IO v2 over
Engine.IO v3 — handshake ``0{...pingInterval...}``, then ``40``; client pings
``2``, server answers ``3``; events arrive as ``42["<event>", {...}]``.  That
is small enough to speak directly on the ``aiohttp`` client the engine already
uses, so no Socket.IO dependency is added.

The join signature (``authSignature``) comes from the signing service; it can
read this user's futures events and do nothing else, and is never logged.
"""

from __future__ import annotations

import asyncio
import json
import random
from typing import Any, Callable, Dict, Optional

import aiohttp

from src.utils import get_logger

log = get_logger("venues.coindcx.stream")

_URL = "wss://stream.coindcx.com/socket.io/?EIO=3&transport=websocket"
_EVENTS = frozenset({"df-order-update", "df-position-update"})
_MANAGE_EVERY_S = 10.0


def parse_frame(frame: str) -> Optional[tuple[str, Any]]:
    """``'42["event", payload]'`` → ``("event", payload)``; anything else →
    ``None``.  Tolerates payloads that are JSON strings inside JSON."""
    if not frame.startswith("42"):
        return None
    try:
        data = json.loads(frame[2:])
    except ValueError:
        return None
    if not (isinstance(data, list) and data and isinstance(data[0], str)):
        return None
    payload = data[1] if len(data) > 1 else None
    if isinstance(payload, dict) and isinstance(payload.get("data"), str):
        try:
            payload = dict(payload, data=json.loads(payload["data"]))
        except ValueError:
            pass
    return data[0], payload


class _UserStream:
    def __init__(self, uid: str, on_event: Callable[[str, str], None]) -> None:
        self.uid = uid
        self._on_event = on_event
        self.task: Optional[asyncio.Task] = None
        self.connects = 0
        self.events = 0
        self.last_error = ""

    async def run(self) -> None:
        from src.security.signing_service import client as _sc

        backoff = 2.0
        while True:
            try:
                resp = await _sc.SigningClient().coindcx_stream_auth(firebase_uid=self.uid)
                if not resp.ok or not isinstance(resp.binance_body, dict):
                    self.last_error = f"auth: {resp.error_code}"
                    raise RuntimeError(self.last_error)
                api_key = str(resp.binance_body.get("api_key") or "")
                sig = str(resp.binance_body.get("auth_signature") or "")
                await self._session(api_key, sig)
                backoff = 2.0
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 — reconnect with backoff
                self.last_error = f"{type(exc).__name__}"
                log.info("coindcx stream uid={} dropped: {}", self.uid, type(exc).__name__)
            await asyncio.sleep(backoff + random.uniform(0, 1))
            backoff = min(backoff * 2, 60.0)

    async def _session(self, api_key: str, auth_signature: str) -> None:
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.ws_connect(_URL, heartbeat=None) as ws:
                self.connects += 1
                ping_interval = 25.0
                pinger: Optional[asyncio.Task] = None
                try:
                    async for msg in ws:
                        if msg.type != aiohttp.WSMsgType.TEXT:
                            if msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                break
                            continue
                        frame = msg.data
                        if frame.startswith("0{"):
                            try:
                                ping_interval = float(json.loads(frame[1:]).get("pingInterval", 25000)) / 1000.0
                            except ValueError:
                                pass
                        elif frame == "40":
                            await ws.send_str("42" + json.dumps(["join", {
                                "channelName": "coindcx",
                                "authSignature": auth_signature,
                                "apiKey": api_key,
                            }]))
                            if pinger is None:
                                pinger = asyncio.create_task(self._ping(ws, ping_interval))
                            # A fresh connection may have missed events.
                            self._on_event(self.uid, "connected")
                        else:
                            parsed = parse_frame(frame)
                            if parsed and parsed[0] in _EVENTS:
                                self.events += 1
                                self._on_event(self.uid, parsed[0])
                finally:
                    if pinger is not None:
                        pinger.cancel()

    @staticmethod
    async def _ping(ws: Any, interval: float) -> None:
        while True:
            await asyncio.sleep(max(5.0, interval * 0.8))
            await ws.send_str("2")


class CoinDCXStreamManager:
    """Keeps one stream per user with a live CoinDCX record."""

    def __init__(self, reconciler: Any, store_getter: Callable[[], Any]) -> None:
        self._reconciler = reconciler
        self._store_getter = store_getter
        self._streams: Dict[str, _UserStream] = {}

    def _on_event(self, uid: str, event: str) -> None:
        self._reconciler.nudge(uid)

    async def run(self) -> None:
        log.info("CoinDCX stream manager started")
        try:
            while True:
                try:
                    await self.manage_once()
                except Exception as exc:  # noqa: BLE001
                    log.warning("coindcx stream manage failed: {}", exc)
                await asyncio.sleep(_MANAGE_EVERY_S)
        finally:
            for s in self._streams.values():
                if s.task:
                    s.task.cancel()

    async def manage_once(self) -> None:
        live = await asyncio.to_thread(self._store_getter().live_positions)
        wanted = {p.uid for p in live}
        for uid in list(self._streams):
            if uid not in wanted:
                s = self._streams.pop(uid)
                if s.task:
                    s.task.cancel()
        for uid in wanted:
            if uid not in self._streams:
                s = _UserStream(uid, self._on_event)
                s.task = asyncio.create_task(s.run(), name=f"coindcx_stream:{uid[:8]}")
                self._streams[uid] = s

    def snapshot(self) -> Dict[str, Any]:
        return {
            "streams": len(self._streams),
            "connects": sum(s.connects for s in self._streams.values()),
            "events": sum(s.events for s in self._streams.values()),
            "errors": sorted({s.last_error for s in self._streams.values() if s.last_error}),
        }
