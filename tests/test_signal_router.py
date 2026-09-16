"""Tests for src.signal_router – queue-based signal routing."""

import asyncio
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

import src.signal_router as signal_router_module
from src.channels.base import Signal
from src.signal_router import (
    SignalRouter,
    _signal_from_dict,
    _signal_to_dict,
    _REDIS_KEY_SIGNALS,
    _REDIS_KEY_POSITION_LOCK,
    _REDIS_KEY_COOLDOWNS,
)
from src.smc import Direction
from src.utils import utcnow


@pytest.fixture
def sent_messages():
    """Collects (chat_id, text) tuples sent by the router."""
    return []


@pytest.fixture
def queue():
    return asyncio.Queue()


@pytest.fixture
def router(queue, sent_messages, monkeypatch):

    async def mock_send(chat_id: str, text: str):
        sent_messages.append((chat_id, text))
        return True

    def mock_format(sig: Signal) -> str:
        return f"Signal: {sig.channel} {sig.symbol} {sig.direction.value}"

    return SignalRouter(queue=queue, )



def _telegram_channels_on(monkeypatch):
    """Pin the Telegram broadcast flag ON for a test about that machinery.

    `TELEGRAM_SIGNALS_ENABLED` defaults to False from 2026-09-15: the
    broadcast channels no longer sit in front of the dispatch log, the order
    fan-out or the app feed. The retry-and-lose path below is unchanged and
    still runs when channels are on, so the tests that exercise it say which
    world they are in rather than inheriting a default that has now moved.
    Verified by reverting: every one of them fails without this line.
    """

def _make_signal(channel="360_SCALP", symbol="BTCUSDT", direction=Direction.LONG, confidence=85):
    return Signal(
        channel=channel,
        symbol=symbol,
        direction=direction,
        entry=32000,
        stop_loss=31900,
        tp1=32130,  # sl_dist=100, tp_dist=130 → R:R=1.3 ≥ 1.3 floor
        tp2=32200,
        confidence=confidence,
        signal_id=f"TEST-{symbol}-001",
        timestamp=utcnow(),
    )


class TestSignalRouter:
    @pytest.mark.asyncio
    async def test_signal_processed_and_sent(self, queue, router, sent_messages):
        sig = _make_signal(confidence=90)
        await queue.put(sig)
        # Run router briefly
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert sig.signal_id in router.active_signals


    @pytest.mark.asyncio
    async def test_low_confidence_filtered(self, queue, router, sent_messages):
        sig = _make_signal(confidence=30)  # below min 70
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert sig.signal_id not in router.active_signals

    @pytest.mark.asyncio
    async def test_correlation_lock(self, queue, router, sent_messages):
        sig1 = _make_signal(symbol="BTCUSDT", direction=Direction.LONG, confidence=90)
        sig1.signal_id = "TEST-BTC-001"
        sig2 = _make_signal(symbol="BTCUSDT", direction=Direction.SHORT, confidence=90)
        sig2.signal_id = "TEST-BTC-002"

        await queue.put(sig1)
        await queue.put(sig2)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.3)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # Only the first should be active (second blocked by correlation lock)
        assert "TEST-BTC-001" in router.active_signals
        assert "TEST-BTC-002" not in router.active_signals

    @pytest.mark.asyncio
    async def test_remove_signal(self, router):
        sig = _make_signal()
        router._active_signals[sig.signal_id] = sig
        router._position_lock[sig.symbol] = sig.direction

        router.remove_signal(sig.signal_id)
        assert sig.signal_id not in router.active_signals
        assert sig.symbol not in router._position_lock

    @pytest.mark.asyncio
    async def test_correlation_lock_blocks_same_direction(self, queue, router, sent_messages):
        """A second LONG for the same symbol must be blocked while the first is active."""
        sig1 = _make_signal(symbol="ETHUSDT", direction=Direction.LONG, confidence=90)
        sig1.signal_id = "TEST-ETH-001"
        sig2 = _make_signal(symbol="ETHUSDT", direction=Direction.LONG, confidence=90)
        sig2.signal_id = "TEST-ETH-002"

        await queue.put(sig1)
        await queue.put(sig2)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.3)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-ETH-001" in router.active_signals
        assert "TEST-ETH-002" not in router.active_signals

    @pytest.mark.asyncio
    async def test_cooldown_prevents_reentry(self, queue, router, sent_messages):
        """After a signal is removed, a new signal for the same (symbol, channel)
        within the cooldown window must be blocked."""
        sig1 = _make_signal(symbol="SOLUSDT", channel="360_SCALP", confidence=90)
        sig1.signal_id = "TEST-SOL-001"

        # Process first signal
        await queue.put(sig1)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        assert "TEST-SOL-001" in router.active_signals

        # Remove the signal (simulates SL hit) – cooldown clock starts now
        router.remove_signal("TEST-SOL-001")
        assert "TEST-SOL-001" not in router.active_signals
        assert ("SOLUSDT", "360_SCALP") in router._cooldown_timestamps

        # Immediately try a second signal for same (symbol, channel)
        sig2 = _make_signal(symbol="SOLUSDT", channel="360_SCALP", confidence=90)
        sig2.signal_id = "TEST-SOL-002"

        queue2 = asyncio.Queue()
        await queue2.put(sig2)
        router2 = SignalRouter(
            queue=queue2,
                                )
        # Copy the cooldown state over so router2 sees the active cooldown
        router2._cooldown_timestamps = dict(router._cooldown_timestamps)

        task2 = asyncio.create_task(router2.start())
        await asyncio.sleep(0.2)
        await router2.stop()
        task2.cancel()
        try:
            await task2
        except asyncio.CancelledError:
            pass

        # Second signal should be blocked by cooldown
        assert "TEST-SOL-002" not in router2.active_signals

    @pytest.mark.asyncio
    async def test_cooldown_allows_reentry_after_expiry(self, queue, router, sent_messages):
        """After the cooldown window expires, a new signal for (symbol, channel)
        must be accepted."""
        # Manually set an expired cooldown timestamp
        router._cooldown_timestamps[("ADAUSDT", "360_SCALP")] = (
            datetime.now(timezone.utc) - timedelta(seconds=120)  # 120s ago ensures 60s SCALP cooldown has expired
        )

        sig = _make_signal(symbol="ADAUSDT", channel="360_SCALP", confidence=90)
        sig.signal_id = "TEST-ADA-001"

        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-ADA-001" in router.active_signals

    @pytest.mark.asyncio
    async def test_tp_direction_rejected_long(self, queue, router, sent_messages):
        """LONG signal where TP1 <= entry must be rejected."""
        sig = Signal(
            channel="360_SCALP",
            symbol="DOTUSDT",
            direction=Direction.LONG,
            entry=1.5100,
            stop_loss=1.5000,
            tp1=1.5100,  # TP1 == entry → invalid
            tp2=1.5200,
            confidence=85,
            signal_id="TEST-DOT-TP-LONG",
            timestamp=utcnow(),
        )
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-DOT-TP-LONG" not in router.active_signals

    @pytest.mark.asyncio
    async def test_tp_direction_rejected_short(self, queue, router, sent_messages):
        """SHORT signal where TP1 >= entry must be rejected."""
        sig = Signal(
            channel="360_SCALP",
            symbol="AVNTUSDT",
            direction=Direction.SHORT,
            entry=0.175700,
            stop_loss=0.176500,
            tp1=0.177899,  # TP1 > entry for SHORT → invalid
            tp2=0.177522,
            confidence=85,
            signal_id="TEST-AVNT-TP-SHORT",
            timestamp=utcnow(),
        )
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-AVNT-TP-SHORT" not in router.active_signals

    @pytest.mark.asyncio
    async def test_sl_direction_rejected_long(self, queue, router, sent_messages):
        """LONG signal where SL >= entry must be rejected."""
        sig = Signal(
            channel="360_SCALP",
            symbol="XYZUSDT",
            direction=Direction.LONG,
            entry=1.0000,
            stop_loss=1.0050,  # SL > entry for LONG → invalid
            tp1=1.0200,
            tp2=1.0300,
            confidence=85,
            signal_id="TEST-XYZ-SL-LONG",
            timestamp=utcnow(),
        )
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-XYZ-SL-LONG" not in router.active_signals

    @pytest.mark.asyncio
    async def test_sl_direction_rejected_short(self, queue, router, sent_messages):
        """SHORT signal where SL <= entry must be rejected."""
        sig = Signal(
            channel="360_SCALP",
            symbol="PIPUSDT",
            direction=Direction.SHORT,
            entry=0.355990,
            stop_loss=0.354000,  # SL < entry for SHORT → invalid
            tp1=0.353000,
            tp2=0.351000,
            confidence=85,
            signal_id="TEST-PIP-SL-SHORT",
            timestamp=utcnow(),
        )
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-PIP-SL-SHORT" not in router.active_signals

    @pytest.mark.asyncio
    async def test_per_channel_cap_blocks_excess_within_same_channel(self, queue, router, sent_messages, monkeypatch):
        """When a channel is full AND the cap is armed, further signals are blocked.

        Pinned to ``enforce`` because the shipped default is ``off`` (owner,
        2026-09-04).  Without the pin this test would go green over a router
        that never checks the cap at all — its own sentence becoming false at
        the moment somebody changes the premise, which is the rot case this
        repo has paid for.  The cap is retained and re-armable from ops, so the
        behaviour it asserts is still real and still needs a guard.

        It asserts the drop REASON, not merely the outcome.  Verified by
        reverting the pin: without it this test STILL PASSED, because five held
        LONGs trip ``same_direction_throttle`` and the candidate dies at a
        different gate — an assertion outliving its premise while staying
        green, which is the rot case this repo has already paid for once.  The
        direction cap is lifted so the channel cap is the only bound that can
        fire, and the reason is checked so no future gate can satisfy this test
        by accident.
        """
        import src.signal_router as sr_mod
        from config import MAX_CONCURRENT_SIGNALS_PER_CHANNEL

        # Pin the TUNABLE, not the module global. `runtime_tunables.get`
        # returns the registered DEFAULT when no Firestore client is wired —
        # not None — so `setattr(sr_mod, "CHANNEL_CAP_MODE", ...)` is inert
        # here. That inert pin was written first and both tests still passed,
        # because a different gate happened to block the candidate; lifting
        # the direction cap is what exposed it.
        monkeypatch.setattr(
            "src.runtime_tunables.get",
            lambda key, *a, **k: "enforce" if key == "channel_cap_mode" else None,
        )
        monkeypatch.setattr(sr_mod, "MAX_SAME_DIRECTION_GLOBAL", 50)
        channel = "360_SCALP"
        cap = MAX_CONCURRENT_SIGNALS_PER_CHANNEL.get(channel, 5)

        # Pre-fill the channel to its cap using distinct symbols
        for i in range(cap):
            dummy = _make_signal(symbol=f"DUMMY{i}USDT", channel=channel, confidence=90)
            dummy.signal_id = f"DUMMY-{i}"
            router._active_signals[dummy.signal_id] = dummy
            router._position_lock[dummy.symbol] = dummy.direction

        # Now try to add one more signal for the same channel (brand-new symbol)
        sig = Signal(
            channel=channel,
            symbol="NEWUSDT",
            direction=Direction.LONG,
            entry=1.0000,
            stop_loss=0.9900,
            tp1=1.0200,
            tp2=1.0300,
            confidence=90,
            signal_id="TEST-NEW-CAP",
            timestamp=utcnow(),
        )
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # The new signal must be blocked BY THIS GATE; channel cap not exceeded
        assert "TEST-NEW-CAP" not in router.active_signals
        assert router.delivery_stats()["drops_by_reason"].get("per_channel_cap") == 1
        channel_count = sum(
            1 for s in router.active_signals.values() if s.channel == channel
        )
        assert channel_count == cap

    @pytest.mark.asyncio
    async def test_per_channel_cap_does_not_block_other_channels(self, queue, router, sent_messages, monkeypatch):
        """When one channel is full, signals from other channels are still accepted.

        Pinned to ``enforce`` for the same reason as the test above, and here
        the pin matters more: with the cap off nothing blocks anything, so an
        "the other channel got through" assertion alone would pass
        **vacuously** — green for a reason that has nothing to do with
        per-channel isolation.  So a SAME-channel candidate is enqueued beside
        the cross-channel one and asserted blocked on ``per_channel_cap``: the
        test now needs the cap to be both armed and channel-scoped, and fails
        against a router that is not enforcing it at all.
        """
        import src.signal_router as sr_mod
        from config import MAX_CONCURRENT_SIGNALS_PER_CHANNEL

        # Pin the TUNABLE, not the module global. `runtime_tunables.get`
        # returns the registered DEFAULT when no Firestore client is wired —
        # not None — so `setattr(sr_mod, "CHANNEL_CAP_MODE", ...)` is inert
        # here. That inert pin was written first and both tests still passed,
        # because a different gate happened to block the candidate; lifting
        # the direction cap is what exposed it.
        monkeypatch.setattr(
            "src.runtime_tunables.get",
            lambda key, *a, **k: "enforce" if key == "channel_cap_mode" else None,
        )
        # Raise global same-direction cap so this test can focus purely on
        # per-channel isolation without the global throttle interfering.
        monkeypatch.setattr(sr_mod, "MAX_SAME_DIRECTION_GLOBAL", 50)

        scalp_channel = "360_SCALP"
        scalp_cap = MAX_CONCURRENT_SIGNALS_PER_CHANNEL.get(scalp_channel, 5)

        # Pre-fill the SCALP channel to its cap
        for i in range(scalp_cap):
            dummy = _make_signal(symbol=f"SCALP{i}USDT", channel=scalp_channel, confidence=90)
            dummy.signal_id = f"SCALP-DUMMY-{i}"
            router._active_signals[dummy.signal_id] = dummy
            router._position_lock[dummy.symbol] = dummy.direction

        # Now try to add a signal for a DIFFERENT channel (360_SCALP_FVG)
        sig = Signal(
            channel="360_SCALP_FVG",
            symbol="FVGUSDT",
            direction=Direction.LONG,
            entry=1.0000,
            stop_loss=0.9900,
            tp1=1.0200,
            tp2=1.0300,
            confidence=90,
            signal_id="TEST-FVG-CROSS",
            timestamp=utcnow(),
        )
        # …and a SAME-channel candidate, which must NOT get through. Without
        # this second half the test is satisfied by a router that enforces
        # nothing.
        same_channel = Signal(
            channel=scalp_channel,
            symbol="SCALPOVERFLOWUSDT",
            direction=Direction.LONG,
            entry=1.0000,
            stop_loss=0.9900,
            tp1=1.0200,
            tp2=1.0300,
            confidence=90,
            signal_id="TEST-SCALP-OVERFLOW",
            timestamp=utcnow(),
        )
        await queue.put(sig)
        await queue.put(same_channel)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # The FVG signal must be accepted even though SCALP is full …
        assert "TEST-FVG-CROSS" in router.active_signals
        # … and the cap must still be channel-scoped and actually enforcing.
        assert "TEST-SCALP-OVERFLOW" not in router.active_signals
        assert router.delivery_stats()["drops_by_reason"].get("per_channel_cap") == 1







class TestCorrelationThrottle:
    """Global same-direction cap (MAX_SAME_DIRECTION_GLOBAL).

    The group-based check_correlation_limit only covers ~25 named pairs.
    The global cap prevents more than N same-direction active signals
    regardless of symbol, guarding against BTC-dump simultaneous SL scenario.

    **These pin ``global`` mode specifically** (2026-08-22).  The gate now has
    two, and this class asserts the behaviour of one of them: without pinning
    the mode these tests would silently start describing whichever mode the
    environment happened to select, which is an assertion outliving its
    premise at the moment somebody changes the premise.  ``per_path`` has its
    own file, ``tests/test_direction_cap.py``.
    """

    def _make_router_with_cap(self, cap: int, queue, sent_messages, monkeypatch):
        import src.signal_router as sr_mod
        monkeypatch.setattr(sr_mod, "DIRECTION_CAP_MODE", "global")
        monkeypatch.setattr(sr_mod, "MAX_SAME_DIRECTION_GLOBAL", cap)

        async def mock_send(chat_id: str, text: str):
            sent_messages.append((chat_id, text))
            return True

        return SignalRouter(
            queue=queue,
                                )

    @pytest.mark.asyncio
    async def test_below_cap_allows_signal(self, monkeypatch):
        """2 LONGs active with cap=3 — a third LONG is allowed."""
        msgs = []
        q = asyncio.Queue()
        router = self._make_router_with_cap(3, q, msgs, monkeypatch)

        # Inject 2 active LONGs directly (bypass queue routing)
        for sym in ("ETHUSDT", "SOLUSDT"):
            s = _make_signal(symbol=sym, direction=Direction.LONG, confidence=90)
            s.signal_id = f"PREFILL-{sym}"
            router._active_signals[s.signal_id] = s
            router._position_lock[s.symbol] = s.direction

        # Route a third LONG on a different symbol
        third = _make_signal(symbol="BNBUSDT", direction=Direction.LONG, confidence=90)
        third.signal_id = "TEST-THIRD-LONG"
        await q.put(third)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.3)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-THIRD-LONG" in router.active_signals

    @pytest.mark.asyncio
    async def test_at_cap_blocks_same_direction(self, monkeypatch):
        """3 LONGs active with cap=3 — a 4th LONG is blocked."""
        msgs = []
        q = asyncio.Queue()
        router = self._make_router_with_cap(3, q, msgs, monkeypatch)

        for sym in ("ETHUSDT", "SOLUSDT", "ADAUSDT"):
            s = _make_signal(symbol=sym, direction=Direction.LONG, confidence=90)
            s.signal_id = f"PREFILL-{sym}"
            router._active_signals[s.signal_id] = s
            router._position_lock[s.symbol] = s.direction

        fourth = _make_signal(symbol="BNBUSDT", direction=Direction.LONG, confidence=90)
        fourth.signal_id = "TEST-FOURTH-LONG"
        await q.put(fourth)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.3)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-FOURTH-LONG" not in router.active_signals

    @pytest.mark.asyncio
    async def test_opposite_direction_not_throttled(self, monkeypatch):
        """3 LONGs active with cap=3 — a SHORT on a new symbol is still allowed."""
        msgs = []
        q = asyncio.Queue()
        router = self._make_router_with_cap(3, q, msgs, monkeypatch)

        for sym in ("ETHUSDT", "SOLUSDT", "ADAUSDT"):
            s = _make_signal(symbol=sym, direction=Direction.LONG, confidence=90)
            s.signal_id = f"PREFILL-{sym}"
            router._active_signals[s.signal_id] = s
            router._position_lock[s.symbol] = s.direction

        short_sig = _make_signal(symbol="BNBUSDT", direction=Direction.SHORT, confidence=90)
        short_sig.signal_id = "TEST-SHORT-OK"
        short_sig.entry = 32000
        short_sig.stop_loss = 32100
        short_sig.tp1 = 31870
        short_sig.tp2 = 31700
        await q.put(short_sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.3)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-SHORT-OK" in router.active_signals

    @pytest.mark.asyncio
    async def test_cap_zero_blocks_all(self, monkeypatch):
        """cap=0 means no same-direction signals can ever be routed."""
        msgs = []
        q = asyncio.Queue()
        router = self._make_router_with_cap(0, q, msgs, monkeypatch)

        sig = _make_signal(symbol="ETHUSDT", direction=Direction.LONG, confidence=90)
        sig.signal_id = "TEST-CAP-ZERO"
        await q.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.3)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        assert "TEST-CAP-ZERO" not in router.active_signals


def _make_mock_redis(stored: dict):
    """Build a fake RedisClient that stores/retrieves from `stored` dict."""
    mock_redis = MagicMock()
    mock_redis.available = True

    async def fake_get(key):
        return stored.get(key)

    async def fake_set(key, value):
        stored[key] = value

    mock_client = MagicMock()
    mock_client.get = fake_get
    mock_client.set = fake_set
    mock_redis.client = mock_client
    return mock_redis


class TestSignalToDict:
    """_signal_to_dict must produce a JSON-serializable, reversible dict."""

    def test_direction_is_string(self):
        sig = _make_signal()
        d = _signal_to_dict(sig)
        assert isinstance(d["direction"], str)
        assert d["direction"] == "LONG"

    def test_timestamp_is_isoformat(self):
        sig = _make_signal()
        d = _signal_to_dict(sig)
        assert isinstance(d["timestamp"], str)
        # Must be valid ISO format
        datetime.fromisoformat(d["timestamp"])

    def test_roundtrip_via_signal_from_dict(self):
        sig = _make_signal(symbol="ETHUSDT", confidence=88)
        d = _signal_to_dict(sig)
        restored = _signal_from_dict(d)
        assert restored is not None
        assert restored.symbol == sig.symbol
        assert restored.confidence == sig.confidence
        assert restored.direction == sig.direction

    def test_json_serializable(self):
        sig = _make_signal()
        d = _signal_to_dict(sig)
        # Must not raise
        json.dumps(d)

    def test_lifecycle_datetime_fields_serialized(self):
        """last_lifecycle_check and dca_timestamp must be ISO strings, not datetime objects."""
        sig = _make_signal()
        sig.last_lifecycle_check = utcnow()
        sig.dca_timestamp = utcnow()
        d = _signal_to_dict(sig)
        # Both datetime fields must be ISO strings
        assert isinstance(d["last_lifecycle_check"], str)
        assert isinstance(d["dca_timestamp"], str)
        datetime.fromisoformat(d["last_lifecycle_check"])
        datetime.fromisoformat(d["dca_timestamp"])
        # Must not raise
        json.dumps(d)

    def test_lifecycle_datetime_fields_roundtrip(self):
        """last_lifecycle_check and dca_timestamp must survive a serialize→deserialize round-trip."""
        now = utcnow()
        sig = _make_signal()
        sig.last_lifecycle_check = now
        sig.dca_timestamp = now
        d = _signal_to_dict(sig)
        restored = _signal_from_dict(d)
        assert restored is not None
        assert restored.last_lifecycle_check == now
        assert restored.dca_timestamp == now


class TestRedisPersistence:
    """SignalRouter must persist and restore state via RedisClient."""

    def _make_router(self, redis_store: dict):
        mock_redis = _make_mock_redis(redis_store)

        async def mock_send(chat_id: str, text: str):
            return True

        router = SignalRouter(
            queue=asyncio.Queue(),
                                    redis_client=mock_redis,
        )
        return router

    @pytest.mark.asyncio
    async def test_persist_state_saves_active_signals(self):
        """_persist_state must write active signals, position lock, and cooldowns to Redis."""
        store: dict = {}
        router = self._make_router(store)

        sig = _make_signal(symbol="BTCUSDT", confidence=90)
        router._active_signals[sig.signal_id] = sig
        router._position_lock[sig.symbol] = sig.direction

        await router._persist_state()

        assert _REDIS_KEY_SIGNALS in store
        saved = json.loads(store[_REDIS_KEY_SIGNALS])
        assert sig.signal_id in saved
        assert _REDIS_KEY_POSITION_LOCK in store
        lock = json.loads(store[_REDIS_KEY_POSITION_LOCK])
        assert lock.get("BTCUSDT") == "LONG"

    @pytest.mark.asyncio
    async def test_restore_reloads_active_signals(self):
        """restore() must load previously persisted signals back into memory."""
        sig = _make_signal(symbol="SOLUSDT", confidence=82)
        store: dict = {
            _REDIS_KEY_SIGNALS: json.dumps({sig.signal_id: _signal_to_dict(sig)}),
            _REDIS_KEY_POSITION_LOCK: json.dumps({"SOLUSDT": "LONG"}),
            _REDIS_KEY_COOLDOWNS: json.dumps({}),
        }
        router = self._make_router(store)
        await router.restore()

        assert sig.signal_id in router._active_signals
        assert router._position_lock.get("SOLUSDT") == Direction.LONG

    @pytest.mark.asyncio
    async def test_restore_reloads_cooldown_timestamps(self):
        """restore() must reload cooldown timestamps with proper tuple keys."""
        ts = datetime.now(timezone.utc)
        store: dict = {
            _REDIS_KEY_SIGNALS: json.dumps({}),
            _REDIS_KEY_POSITION_LOCK: json.dumps({}),
            _REDIS_KEY_COOLDOWNS: json.dumps({"ADAUSDT|360_SCALP": ts.isoformat()}),
        }
        router = self._make_router(store)
        await router.restore()

        assert ("ADAUSDT", "360_SCALP") in router._cooldown_timestamps

    @pytest.mark.asyncio
    async def test_persist_called_on_remove_signal(self):
        """remove_signal() must schedule a Redis persist."""
        store: dict = {}
        router = self._make_router(store)

        sig = _make_signal()
        router._active_signals[sig.signal_id] = sig
        router._position_lock[sig.symbol] = sig.direction

        router.remove_signal(sig.signal_id)
        # Flush pending tasks
        await asyncio.sleep(0)

        assert sig.signal_id not in router._active_signals
        # Persistence must have fired (signals key updated)
        assert _REDIS_KEY_SIGNALS in store

    @pytest.mark.asyncio
    async def test_persist_called_on_update_signal(self):
        """update_signal() must schedule a Redis persist."""
        store: dict = {}
        router = self._make_router(store)

        sig = _make_signal()
        router._active_signals[sig.signal_id] = sig

        router.update_signal(sig.signal_id, status="TP1_HIT")
        # Flush pending tasks
        await asyncio.sleep(0)

        assert router._active_signals[sig.signal_id].status == "TP1_HIT"
        assert _REDIS_KEY_SIGNALS in store

    @pytest.mark.asyncio
    async def test_no_redis_skips_persist(self):
        """When no redis_client is provided, _persist_state must be a no-op."""
        async def mock_send(chat_id: str, text: str):
            return True

        router = SignalRouter(
            queue=asyncio.Queue(),
                                    redis_client=None,
        )
        # Must not raise
        await router._persist_state()

    @pytest.mark.asyncio
    async def test_no_redis_skips_restore(self):
        """When no redis_client is provided, restore() must be a no-op."""
        async def mock_send(chat_id: str, text: str):
            return True

        router = SignalRouter(
            queue=asyncio.Queue(),
                                    redis_client=None,
        )
        # Must not raise and must leave state empty
        await router.restore()
        assert router._active_signals == {}


# ---------------------------------------------------------------------------
# Fix 7: Position lock cleanup via cleanup_expired()
# ---------------------------------------------------------------------------


class TestCleanupExpired:
    """cleanup_expired() must remove stale signals and their position locks."""

    @pytest.fixture(autouse=True)
    def _enable_expiry(self, monkeypatch):
        # cleanup_expired now honours the signal-expiry toggle (2026-07-08 fix:
        # it previously force-closed at the 1h max-hold regardless of the
        # owner's OFF setting). These behaviour tests exercise the ON path.
        monkeypatch.setattr("src.signal_router.SIGNAL_EXPIRY_ENABLED", True)

    def test_cleanup_noop_when_expiry_disabled(self, router, monkeypatch):
        """With signal-expiry OFF, an over-age signal must NOT be force-closed —
        it runs to TP/SL. Regression lock for the 2026-07-08 bug where this
        sweep ignored the toggle."""
        monkeypatch.setattr("src.signal_router.SIGNAL_EXPIRY_ENABLED", False)
        sig = _make_signal(channel="360_SCALP", symbol="XRPUSDT")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig
        router._position_lock["XRPUSDT"] = sig.direction

        removed = router.cleanup_expired()
        assert removed == 0
        assert sig.signal_id in router._active_signals

    def test_cleanup_removes_expired_signal(self, router):
        """A signal older than its channel max hold must be removed."""
        sig = _make_signal(channel="360_SCALP")
        # Age the signal far beyond its 1-hour hold
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig
        router._position_lock[sig.symbol] = sig.direction

        removed = router.cleanup_expired()
        assert removed == 1
        assert sig.signal_id not in router._active_signals

    def test_cleanup_clears_position_lock(self, router):
        """After cleanup, the position lock for the expired symbol is released."""
        sig = _make_signal(channel="360_SCALP", symbol="ETHUSDT")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig
        router._position_lock["ETHUSDT"] = sig.direction

        router.cleanup_expired()
        assert "ETHUSDT" not in router._position_lock

    def test_cleanup_sets_cooldown_on_expiry(self, router):
        """Expired signals must record a cooldown timestamp for re-entry suppression."""
        sig = _make_signal(channel="360_SCALP", symbol="SOLUSDT")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig
        router._position_lock["SOLUSDT"] = sig.direction

        router.cleanup_expired()
        assert ("SOLUSDT", "360_SCALP") in router._cooldown_timestamps

    def test_cleanup_does_not_remove_active_signal(self, router):
        """A fresh signal must not be removed by cleanup_expired."""
        sig = _make_signal(channel="360_SCALP", symbol="BNBUSDT")
        sig.timestamp = datetime.now(timezone.utc)  # just created
        router._active_signals[sig.signal_id] = sig
        router._position_lock["BNBUSDT"] = sig.direction

        removed = router.cleanup_expired()
        assert removed == 0
        assert sig.signal_id in router._active_signals

    def test_cleanup_returns_zero_on_empty_router(self, router):
        """cleanup_expired with no active signals must return 0."""
        assert router.cleanup_expired() == 0

    def test_cleanup_invokes_on_signal_expired_callback(self, router):
        """Engine hook must fire BEFORE the signal is popped from
        _active_signals so the engine can compute P&L, archive, close
        broker, and stamp a perf record.  Without this hook the signal
        silently disappears with no record anywhere.
        """
        sig = _make_signal(channel="360_SCALP", symbol="SOLUSDT")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig

        captured = []

        def _capture(s, now):
            captured.append((s.signal_id, s.symbol, s in router._active_signals.values()))

        router.on_signal_expired = _capture
        router.cleanup_expired()

        assert len(captured) == 1
        sid, sym, was_in_active_at_callback_time = captured[0]
        assert sid == sig.signal_id
        assert sym == "SOLUSDT"
        # Hook must fire while signal is still in active dict — engine relies
        # on that for any logic that touches router state mid-archive.
        assert was_in_active_at_callback_time is True

    def test_cleanup_swallows_callback_exception(self, router):
        """A failing on_signal_expired callback must not break cleanup —
        the cooldown / position-lock release must still happen."""
        sig = _make_signal(channel="360_SCALP", symbol="SOLUSDT")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig
        router._position_lock["SOLUSDT"] = sig.direction

        def _boom(s, now):
            raise RuntimeError("simulated callback failure")

        router.on_signal_expired = _boom
        # Should not raise.
        router.cleanup_expired()
        # Cleanup still ran — signal popped, lock cleared.
        assert sig.signal_id not in router._active_signals
        assert "SOLUSDT" not in router._position_lock

    def test_cleanup_works_when_callback_is_none(self, router):
        """Default state (engine never wired the hook) must not crash."""
        sig = _make_signal(channel="360_SCALP")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=3)
        router._active_signals[sig.signal_id] = sig

        # router.on_signal_expired is None by default.
        removed = router.cleanup_expired()
        assert removed == 1


# ---------------------------------------------------------------------------
# Telegram expiry message — uses sig.current_price + pnl_pct when stamped
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# BUG 4: cleanup_expired is wired into start() loop
# ---------------------------------------------------------------------------


class TestStartLoopCallsCleanup:
    """start() must call cleanup_expired() periodically via the timeout path."""

    @pytest.mark.asyncio
    async def test_cleanup_called_on_timeout_counter_overflow(self, queue):
        """Simulate 60 timeout ticks – cleanup_expired must be called exactly once."""
        cleanup_calls = []

        async def mock_send(chat_id: str, text: str):
            return True

        router = SignalRouter(
            queue=queue,
                                )
        # Monkey-patch cleanup_expired to record calls
        original = router.cleanup_expired

        def tracking_cleanup():
            result = original()
            cleanup_calls.append(True)
            return result

        router.cleanup_expired = tracking_cleanup

        # Seed one expired signal so cleanup has something to do
        sig = _make_signal(channel="360_SCALP")
        sig.timestamp = datetime.now(timezone.utc) - timedelta(hours=5)
        router._active_signals[sig.signal_id] = sig
        router._position_lock[sig.symbol] = sig.direction

        # Drive the start() loop with a very short timeout so it fires quickly.
        # We put None in the queue to create a fast timeout-style loop.
        # Instead, run the loop just long enough for at least 60 iterations.
        # We do this by draining timeouts: with timeout=1.0 that would need 60s.
        # Instead, we test the counter logic directly by patching asyncio.wait_for
        # to always raise TimeoutError — simulating 60 rapid timeout ticks.

        timeout_count = 0

        async def fast_wait_for(coro, timeout):
            nonlocal timeout_count
            timeout_count += 1
            # On the 60th tick, stop the router so the test finishes
            if timeout_count >= 60:
                router._running = False
            coro.close()
            raise asyncio.TimeoutError

        router._queue_has_timeout = False  # force the asyncio.wait_for code path
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(asyncio, "wait_for", fast_wait_for)
        # cleanup_expired now honours the signal-expiry toggle (2026-07-08 fix).
        # This test asserts the loop drives cleanup to remove the seeded over-age
        # signal, so it must exercise the expiry-ON path.
        monkeypatch.setattr("src.signal_router.SIGNAL_EXPIRY_ENABLED", True)

        try:
            await router.start()
        finally:
            monkeypatch.undo()

        # After 60 simulated timeout ticks, cleanup must have been called
        assert len(cleanup_calls) >= 1, "cleanup_expired was never called from the start() loop"
        # The expired signal must have been removed
        assert sig.signal_id not in router._active_signals






class TestRouterDropTelemetry:
    """The router drops most of what it dequeues, and used to say nothing.

    Every rejection in ``_process`` was a bare ``return`` after a ``log.info``:
    no counter, no suppression stamp, no funnel stage, and no truth-report
    section parsing those lines. Twelve live gates with no row in the
    Suppression Quality Audit, on the one hop that decides what a subscriber
    receives — while the path funnel's ``emitted`` column, incremented straight
    after ``_enqueue_signal``, counts *enqueues* and stops one layer above.

    These drive the real router through the real ``_process``; a mock whose keys
    we chose could not tell us a drop went uncounted.
    """

    @pytest.mark.asyncio
    async def test_a_delivered_signal_is_counted_as_delivered(self, router):
        await router._process(_make_signal(confidence=90))
        stats = router.delivery_stats()
        assert stats["processed"] == 1
        assert stats["delivered"] == 1
        assert stats["dropped"] == 0
        assert stats["delivery_rate"] == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_the_correlation_lock_drop_is_counted_and_named(self, router):
        """The second signal on a symbol with an open position. Previously this
        left no trace anywhere."""
        await router._process(_make_signal(symbol="BTCUSDT"))
        second = _make_signal(symbol="BTCUSDT")
        second.signal_id = "TEST-BTCUSDT-002"
        await router._process(second)

        stats = router.delivery_stats()
        assert stats["delivered"] == 1
        assert stats["dropped"] == 1
        assert stats["drops_by_reason"]["correlation_lock"] == 1
        assert stats["delivery_rate"] == pytest.approx(0.5)

    @pytest.mark.asyncio
    async def test_tp_sanity_rejection_is_counted(self, router):
        bad = _make_signal(symbol="ETHUSDT")
        bad.tp1 = bad.entry - 10          # LONG with TP1 below entry
        await router._process(bad)
        assert router.delivery_stats()["drops_by_reason"]["tp_sanity"] == 1

    @pytest.mark.asyncio
    async def test_drops_are_keyed_by_setup_so_a_starved_path_is_visible(self, router):
        """'This path never reaches a user' and 'the market was quiet' produce
        the same total otherwise."""
        first = _make_signal(symbol="SOLUSDT")
        first.setup_class = "MOVER_TREND_PULLBACK"
        await router._process(first)
        second = _make_signal(symbol="SOLUSDT")
        second.signal_id = "TEST-SOLUSDT-002"
        second.setup_class = "MOVER_TREND_PULLBACK"
        await router._process(second)

        by_setup = router.delivery_stats()["drops_by_reason_setup"]
        assert by_setup["correlation_lock:MOVER_TREND_PULLBACK"] == 1

    @pytest.mark.asyncio
    async def test_a_drop_stamps_the_suppression_audit_under_its_own_gate_name(
        self, router, monkeypatch
    ):
        """The counter says how much volume a gate costs; only the audit says
        whether it cost money. A gate that cannot be measured cannot earn its
        place — and none of these could."""
        stamped = []
        import src.suppression_audit as sa

        monkeypatch.setattr(
            sa, "stamp_candidate", lambda **kw: stamped.append(kw) or None
        )
        monkeypatch.setattr(
            "src.runtime_tunables.get", lambda key, *a, **k: True
        )
        await router._process(_make_signal(symbol="XRPUSDT"))
        second = _make_signal(symbol="XRPUSDT")
        second.signal_id = "TEST-XRPUSDT-002"
        await router._process(second)

        assert [s["gate_name"] for s in stamped] == ["router:correlation_lock"]
        assert stamped[0]["symbol"] == "XRPUSDT"
        assert stamped[0]["entry"] > 0 and stamped[0]["tp1"] > 0

    @pytest.mark.asyncio
    async def test_a_failing_stamp_never_costs_the_drop_decision(self, router, monkeypatch):
        """A measurement must never change what the router does."""
        import src.suppression_audit as sa

        def _boom(**kw):
            raise RuntimeError("audit down")

        monkeypatch.setattr(sa, "stamp_candidate", _boom)
        monkeypatch.setattr("src.runtime_tunables.get", lambda key, *a, **k: True)

        await router._process(_make_signal(symbol="ADAUSDT"))
        second = _make_signal(symbol="ADAUSDT")
        second.signal_id = "TEST-ADAUSDT-002"
        await router._process(second)

        assert router.delivery_stats()["drops_by_reason"]["correlation_lock"] == 1
        assert router.delivery_stats()["delivered"] == 1

    def test_an_idle_router_logs_nothing(self, router, caplog):
        """A row of zeros every minute is how a real drop-off stops standing
        out."""
        router._log_delivery_stats()
        assert "ROUTER_DELIVERY" not in caplog.text


# ── the drop census must reach a reader ───────────────────────────────────

class TestRouterDeliveryCensusIsPublished:
    """`delivery_stats()` had exactly one caller — `_log_delivery_stats`, which
    logs `drops_by_reason` and **not** `drops_by_reason_setup`.

    That second key is the one that says whether a high-volume path is consuming
    the concurrency caps and starving the others, and it was computed on every
    cycle and rendered nowhere: a field one repo writes and no repo reads,
    standing directly in front of the question it was built to answer
    (owner, 2026-08-07).
    """

    @staticmethod
    def _real_router():
        """A real router, not ``__new__`` with the three attributes I happened
        to need.

        The hand-built version broke the day ``delivery_stats`` grew the
        position-lock block (2026-08-20) — it reads ``_active_signals`` and
        ``_position_lock``, which a bypassed ``__init__`` never creates.  That
        is the repo's own *"drive the real collaborator"* rule arriving at a
        constructor: a stub carrying only the fields the assertion touches
        cannot notice when the method under test starts needing more, and the
        tempting repair — making the reader ``getattr``-defensive — would have
        hidden a genuinely missing attribute in production.
        """
        from unittest.mock import MagicMock

        from src.signal_router import SignalRouter

        return SignalRouter(
            queue=MagicMock(),
                                    redis_client=None,
        )

    def test_the_stats_carry_the_per_setup_breakdown(self):
        r = self._real_router()
        r._drop_counters["same_direction_throttle"] = 7
        r._drop_counters["same_direction_throttle:MOVER_TREND_PULLBACK"] = 5
        r._drop_counters["same_direction_throttle:TREND_PULLBACK_EMA"] = 2
        s = r.delivery_stats()
        assert s["drops_by_reason"] == {"same_direction_throttle": 7}
        assert s["drops_by_reason_setup"]["same_direction_throttle:MOVER_TREND_PULLBACK"] == 5
        # The two must not pool: the un-keyed total is not a setup row.
        assert "same_direction_throttle" not in s["drops_by_reason_setup"]

    def test_the_snapshot_writer_publishes_it(self):
        """Pin the CALL SITE, not the method. Defining `_write_router_delivery`
        is not calling it — the exact distinction that left two structural
        ledgers flushed-but-never-loaded."""
        import ast
        import inspect
        import textwrap

        from src.api.snapshot_writer import SnapshotWriter

        src = textwrap.dedent(inspect.getsource(SnapshotWriter._write_cycle))
        calls = {
            n.func.attr for n in ast.walk(ast.parse(src))
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        }
        assert "_write_router_delivery" in calls, (
            "the census is built and never published — the seam this fixes"
        )

    def test_a_missing_router_names_its_cause_rather_than_returning_empty(self):
        """"The router dropped nothing" and "there is no router here" are
        different states; an empty payload renders them identically."""
        from src.api.snapshot_writer import SnapshotWriter

        w = SnapshotWriter.__new__(SnapshotWriter)
        w._engine = object()
        out = w._build_router_delivery()
        assert out["schema"] == 0
        assert "error" in out and out["error"]

    def test_a_real_router_builds_a_schema_1_payload(self):
        """Drive the real object rather than a stub whose keys I chose."""
        from src.api.snapshot_writer import SnapshotWriter

        r = self._real_router()
        r._processed_total = 3
        r._delivered_total = 1
        r._drop_counters["per_channel_cap"] = 2
        r._drop_counters["per_channel_cap:MOVER_TREND_PULLBACK"] = 2

        class _E:
            router = r

        w = SnapshotWriter.__new__(SnapshotWriter)
        w._engine = _E()
        out = w._build_router_delivery()
        assert out["schema"] == 1
        assert out["processed"] == 3 and out["delivered"] == 1 and out["dropped"] == 2
        assert out["drops_by_reason_setup"]["per_channel_cap:MOVER_TREND_PULLBACK"] == 2


class TestChannelCapMode:
    """The per-channel cap is switched, not deleted (owner, 2026-09-04).

    ``360_SCALP`` is the only fully-live channel, so a cap named per-channel
    was a cap on the whole book across 17 paths — it took 45 of 56 router
    drops in one measured 4.9h boot, and 32 of 101 promoted
    ``LIQUIDITY_SWEEP_REVERSAL`` rows.  It now defaults to ``off``, with the
    book ceiling beside it as the re-armable bound and the counterfactual
    published either way.

    Every test here drives the real router loop rather than calling the
    decision helper, because the property that matters is what reaches a
    subscriber and a helper asserting its own return shape is a mock agreeing
    with the author.
    """

    @staticmethod
    def _tunables(monkeypatch, **overrides):
        """Override the LIVE tunable reads, not the module globals.

        This is the trap ``_tunable_str``'s own docstring records: with no
        Firestore client ``runtime_tunables.get`` returns the tunable's
        registered DEFAULT rather than ``None``, so patching the module global
        a tunable falls back to changes nothing.  A test that patched the
        global and passed would be asserting the config default, not the
        override it thinks it set — which is how a bound goes untested.
        """
        monkeypatch.setattr(
            "src.runtime_tunables.get", lambda key, *a, **k: overrides.get(key)
        )

    @staticmethod
    async def _run(router, queue, sig):
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @staticmethod
    def _fill_channel(router, channel, n):
        for i in range(n):
            dummy = _make_signal(symbol=f"FILL{i}USDT", channel=channel, confidence=90)
            dummy.signal_id = f"FILL-{i}"
            router._active_signals[dummy.signal_id] = dummy
            router._position_lock[dummy.symbol] = dummy.direction

    @pytest.mark.asyncio
    async def test_off_admits_a_signal_a_full_channel_would_have_blocked(
        self, queue, router, sent_messages, monkeypatch
    ):
        """The shipped default. This is the behaviour the owner asked for."""
        import src.signal_router as sr_mod
        from config import MAX_CONCURRENT_SIGNALS_PER_CHANNEL

        self._tunables(monkeypatch, channel_cap_mode="off",
                       max_concurrent_signals_book=0)
        monkeypatch.setattr(sr_mod, "MAX_SAME_DIRECTION_GLOBAL", 50)

        cap = MAX_CONCURRENT_SIGNALS_PER_CHANNEL.get("360_SCALP", 5)
        self._fill_channel(router, "360_SCALP", cap)

        sig = _make_signal(symbol="NEWUSDT", confidence=90)
        sig.signal_id = "CAP-OFF-ADMITTED"
        await self._run(router, queue, sig)

        assert "CAP-OFF-ADMITTED" in router.active_signals
        assert router.delivery_stats()["drops_by_reason"].get("per_channel_cap", 0) == 0

    @pytest.mark.asyncio
    async def test_the_counterfactual_still_counts_what_the_cap_would_have_taken(
        self, queue, router, sent_messages, monkeypatch
    ):
        """Effect off, measurement on.

        A switch shipped with its measurement off produces an empty panel and a
        decision that keeps getting deferred, which is exactly how this repo
        has lost dark lanes before.  ``channel_only`` is the population that
        says what re-arming the cap would cost.
        """
        import src.signal_router as sr_mod
        from config import MAX_CONCURRENT_SIGNALS_PER_CHANNEL

        self._tunables(monkeypatch, channel_cap_mode="off",
                       max_concurrent_signals_book=0)
        monkeypatch.setattr(sr_mod, "MAX_SAME_DIRECTION_GLOBAL", 50)

        cap = MAX_CONCURRENT_SIGNALS_PER_CHANNEL.get("360_SCALP", 5)
        self._fill_channel(router, "360_SCALP", cap)

        sig = _make_signal(symbol="NEWUSDT", confidence=90)
        sig.signal_id = "CAP-OFF-COUNTED"
        sig.setup_class = "LIQUIDITY_SWEEP_REVERSAL"
        await self._run(router, queue, sig)

        report = router.delivery_stats()["channel_cap"]
        assert report["mode"] == "off"
        assert report["counterfactual"]["channel_only"] == 1
        assert report["would_have_blocked"] == 1
        # Keyed by setup as well as totalled: "this cap costs 45 drops" and
        # "this cap costs ONE path 45 drops" are different findings.
        assert (
            report["counterfactual_by_setup"]["channel_only:LIQUIDITY_SWEEP_REVERSAL"]
            == 1
        )

    @pytest.mark.asyncio
    async def test_book_ceiling_blocks_and_names_itself_apart_from_the_channel_cap(
        self, queue, router, sent_messages, monkeypatch
    ):
        """The re-armable bound, and it must not borrow the channel's name.

        A candidate refused because the whole book is full and one refused
        because a single channel is full are different findings with different
        fixes, so they never share a drop reason.
        """
        import src.signal_router as sr_mod

        self._tunables(monkeypatch, channel_cap_mode="off",
                       max_concurrent_signals_book=3)
        monkeypatch.setattr(sr_mod, "MAX_SAME_DIRECTION_GLOBAL", 50)

        self._fill_channel(router, "360_SCALP", 3)

        sig = _make_signal(symbol="NEWUSDT", confidence=90)
        sig.signal_id = "BOOK-CEILING-BLOCKED"
        await self._run(router, queue, sig)

        assert "BOOK-CEILING-BLOCKED" not in router.active_signals
        drops = router.delivery_stats()["drops_by_reason"]
        assert drops.get("book_cap") == 1
        assert drops.get("per_channel_cap", 0) == 0

    @pytest.mark.asyncio
    async def test_zero_is_off_not_block_everything(
        self, queue, router, sent_messages, monkeypatch
    ):
        """``0`` is a decision somebody made, never an unset value.

        The bound that does NOT do the work needs its own test — a ceiling read
        as ``count >= 0`` refuses every candidate on an empty book and would
        take the whole feed down silently.
        """
        import src.signal_router as sr_mod

        self._tunables(monkeypatch, channel_cap_mode="off",
                       max_concurrent_signals_book=0)

        sig = _make_signal(symbol="NEWUSDT", confidence=90)
        sig.signal_id = "EMPTY-BOOK-ADMITTED"
        await self._run(router, queue, sig)

        assert "EMPTY-BOOK-ADMITTED" in router.active_signals
        assert router.delivery_stats()["drops_by_reason"].get("book_cap", 0) == 0

    @pytest.mark.asyncio
    async def test_report_renders_before_any_candidate_is_seen(self, router):
        """A panel that appears only once it trips teaches the reader that its
        absence means "fine" when it equally means the check stopped running.
        """
        report = router.delivery_stats()["channel_cap"]
        assert report["evaluated"] == 0
        assert report["would_have_blocked"] == 0
        # None, not 0.0 — no candidate was seen, so there is no share to state.
        assert report["would_have_blocked_share"] is None
        assert report["book_limit"] == 0


class TestTheUnstampedRouterExits:
    """The three gates below the twelve counted ones.

    ``_process`` was documented as rejecting on twelve conditions and stamping
    each. Three exits below them were still bare ``return``s — the RiskManager,
    a missing Telegram channel id, and permanent delivery failure — so their
    drops appeared in no funnel, in no suppression audit, and left a promoted
    dark row reading ``promoted_enqueued`` forever, indistinguishable from one
    still in flight.

    Measured on the live box 2026-09-04: **11 of 65 dequeued candidates (17%)**
    reached neither a delivery nor a stamped drop, and **31 of 101** promoted
    ``LIQUIDITY_SWEEP_REVERSAL`` rows sat at the RiskManager — all 31 below its
    own 1.2 R:R floor, against 5 delivered rows all at 1.22 or above.
    """

    @staticmethod
    async def _run(router, queue, sig):
        await queue.put(sig)
        task = asyncio.create_task(router.start())
        await asyncio.sleep(0.2)
        await router.stop()
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_a_risk_manager_refusal_is_counted_and_named(self, queue, router):
        """It must be counted, and NOT under a single "risk manager" integer.

        An R:R floor, a per-symbol concurrency limit and an order-book
        imbalance are three different fixes; one counter for all three is the
        `place_failed` defect one subsystem over.
        """
        sig = _make_signal(symbol="RRFLOORUSDT", confidence=90)
        sig.signal_id = "RISK-RR-FLOOR"
        # TP1 nearer than the stop: designed R:R 0.5, below the 1.2 floor.
        sig.stop_loss = sig.entry - 100
        sig.tp1 = sig.entry + 50
        await self._run(router, queue, sig)

        assert "RISK-RR-FLOOR" not in router.active_signals
        drops = router.delivery_stats()["drops_by_reason"]
        assert drops.get("risk_manager_rr_floor") == 1



    def test_the_reason_classifier_buckets_by_cause_not_by_numbers(self):
        """`risk.reason` interpolates the values, so using it as a counter key
        would create one bucket per candidate and count nothing."""
        from src.signal_router import _risk_reason_class

        assert _risk_reason_class("Insufficient R:R (0.44 < 1.2)") == "rr_floor"
        assert _risk_reason_class("Insufficient R:R (0.91 < 1.2)") == "rr_floor"
        assert (
            _risk_reason_class("Max 2 concurrent signals per symbol exceeded")
            == "symbol_concurrency"
        )
        # A cause this table has never heard of is named, never dropped and
        # never forced into a neighbour.
        assert _risk_reason_class("something nobody has written yet") == "other"
        assert _risk_reason_class("") == "unspecified"
        assert _risk_reason_class(None) == "unspecified"
