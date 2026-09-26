"""The two engine-side queue consumers, driven through their real drain loops.

``ManualTakeConsumer`` (a user's take / close / manual trade from the app) and
``SafetySwitchConsumer`` (the kill switch when the api container is blind)
both had ``_process`` covered and ``start()`` never run — so the part that
actually pulls an envelope off Redis, survives a Redis error, and keeps
going after a timeout was untested on both. ``manual_take`` also had three
envelope kinds with no test at all: a user closing their own position, the
owner closing a signal, and the manual trade builder with its stale refusal
(2026-09-26 audit; module coverage 46%).

The loops are run for real against a scripted fake: each ``brpop`` returns the
next item, ``None`` is a server-side timeout, an exception is a Redis fault,
and an exhausted script cancels the loop the way shutdown does.
"""
from __future__ import annotations

import asyncio
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from src.api import snapshot_store as store
from src.execution import manual_take
from src.execution import safety_switch_bridge as bridge


class _ScriptedRedis:
    """``brpop`` replays a script; ``set`` records results."""

    def __init__(self, script, *, unavailable_polls: int = 0) -> None:
        self.client = self
        self._script = list(script)
        self._unavailable = unavailable_polls
        self.brpop_keys: list[str] = []
        self.written: dict[str, str] = {}

    @property
    def available(self) -> bool:
        if self._unavailable > 0:
            self._unavailable -= 1
            return False
        return True

    async def brpop(self, key, timeout=None):
        self.brpop_keys.append(key)
        if not self._script:
            raise asyncio.CancelledError  # shutdown
        item = self._script.pop(0)
        if isinstance(item, BaseException):
            raise item
        if item is None:
            return None  # BRPOP timed out with nothing queued
        return (key, item)

    async def set(self, key, value, ex=None):
        self.written[key] = value


def _result(redis: _ScriptedRedis, prefix: str, request_id: str) -> dict:
    return json.loads(redis.written[prefix + request_id])


@pytest.fixture(autouse=True)
def _no_backoff(monkeypatch):
    monkeypatch.setattr(manual_take, "_ERROR_BACKOFF_S", 0.0)
    monkeypatch.setattr(bridge, "_ERROR_BACKOFF_S", 0.0)


# ---------------------------------------------------------------------------
# ManualTakeConsumer.start
# ---------------------------------------------------------------------------


def _take(request_id: str, *, ts: float | None = None) -> str:
    return json.dumps({
        "request_id": request_id, "uid": "fb-U", "signal_id": f"sig-{request_id}",
        "ts": time.time() if ts is None else ts,
    })


async def test_take_drain_processes_in_order_through_timeouts_and_faults() -> None:
    engine = SimpleNamespace(take_signal_for_user=AsyncMock(
        side_effect=lambda uid, sid: {"outcome": "placed", "signal_id": sid},
    ))
    redis = _ScriptedRedis([
        _take("a"),
        None,                              # idle timeout — must not stop the loop
        ConnectionError("redis blip"),     # fault — logged, backed off, loop continues
        _take("b"),
    ])
    consumer = manual_take.ManualTakeConsumer(engine, redis)
    with pytest.raises(asyncio.CancelledError):
        await consumer.start()
    assert [c.args[1] for c in engine.take_signal_for_user.await_args_list] == ["sig-a", "sig-b"]
    assert set(redis.brpop_keys) == {store.KEY_CMD_TAKE}
    assert _result(redis, store.KEY_TAKE_RESULT_PREFIX, "a")["outcome"] == "placed"
    assert _result(redis, store.KEY_TAKE_RESULT_PREFIX, "b")["outcome"] == "placed"


async def test_take_drain_waits_out_an_unavailable_redis() -> None:
    engine = SimpleNamespace(take_signal_for_user=AsyncMock(return_value={"outcome": "placed"}))
    redis = _ScriptedRedis([_take("a")], unavailable_polls=3)
    consumer = manual_take.ManualTakeConsumer(engine, redis)
    with pytest.raises(asyncio.CancelledError):
        await consumer.start()
    engine.take_signal_for_user.assert_awaited_once()


async def test_a_stale_take_in_the_queue_never_reaches_the_engine() -> None:
    engine = SimpleNamespace(take_signal_for_user=AsyncMock())
    old = time.time() - store.TAKE_CMD_STALE_S - 5
    redis = _ScriptedRedis([_take("old", ts=old)])
    consumer = manual_take.ManualTakeConsumer(engine, redis)
    with pytest.raises(asyncio.CancelledError):
        await consumer.start()
    engine.take_signal_for_user.assert_not_awaited()
    assert _result(redis, store.KEY_TAKE_RESULT_PREFIX, "old")["reject_class"] == "TakeRequestStale"


# ---------------------------------------------------------------------------
# kind="close_position" — a user closing their OWN position
# ---------------------------------------------------------------------------


def _close_position(request_id="c1", *, ts=None, **drop):
    env = {"kind": "close_position", "request_id": request_id, "uid": "fb-U",
           "signal_id": "sig-9", "ts": time.time() if ts is None else ts}
    for k in drop:
        env.pop(k)
    return json.dumps(env)


async def test_close_position_calls_the_users_own_close_and_answers() -> None:
    engine = SimpleNamespace(
        close_position_for_user=AsyncMock(return_value={"outcome": "closed", "signal_id": "sig-9"}),
        take_signal_for_user=AsyncMock(),
    )
    redis = _ScriptedRedis([])
    await manual_take.ManualTakeConsumer(engine, redis)._process(_close_position())
    engine.close_position_for_user.assert_awaited_once_with("fb-U", "sig-9")
    engine.take_signal_for_user.assert_not_awaited()
    assert _result(redis, store.KEY_TAKE_RESULT_PREFIX, "c1")["outcome"] == "closed"


async def test_a_late_close_still_closes() -> None:
    """No staleness gate on a close, by design: getting out late still does
    what the user asked, and a queued close is when they most want out."""
    engine = SimpleNamespace(close_position_for_user=AsyncMock(return_value={"outcome": "closed"}))
    redis = _ScriptedRedis([])
    ancient = time.time() - store.TAKE_CMD_STALE_S * 20
    await manual_take.ManualTakeConsumer(engine, redis)._process(_close_position(ts=ancient))
    engine.close_position_for_user.assert_awaited_once()


async def test_a_crashing_close_still_answers_with_a_rejection() -> None:
    engine = SimpleNamespace(close_position_for_user=AsyncMock(side_effect=RuntimeError("signing down")))
    redis = _ScriptedRedis([])
    await manual_take.ManualTakeConsumer(engine, redis)._process(_close_position())
    out = _result(redis, store.KEY_TAKE_RESULT_PREFIX, "c1")
    assert out["outcome"] == "rejected"
    assert out["reject_class"] == "RuntimeError"
    assert out["signal_id"] == "sig-9"


@pytest.mark.parametrize("missing", ["request_id", "uid", "signal_id"])
async def test_an_incomplete_close_is_dropped_without_acting(missing) -> None:
    engine = SimpleNamespace(close_position_for_user=AsyncMock())
    redis = _ScriptedRedis([])
    await manual_take.ManualTakeConsumer(engine, redis)._process(
        _close_position(**{missing: None}),
    )
    engine.close_position_for_user.assert_not_awaited()
    assert redis.written == {}


async def test_a_lost_result_write_does_not_raise_into_the_loop() -> None:
    engine = SimpleNamespace(close_position_for_user=AsyncMock(return_value={"outcome": "closed"}))
    redis = _ScriptedRedis([])

    async def _boom(*a, **k):
        raise ConnectionError("redis gone")

    redis.set = _boom
    await manual_take.ManualTakeConsumer(engine, redis)._process(_close_position())
    engine.close_position_for_user.assert_awaited_once()


# ---------------------------------------------------------------------------
# kind="close" — the owner closing a signal for everybody
# ---------------------------------------------------------------------------


async def test_owner_close_routes_to_the_admin_close_not_the_users() -> None:
    engine = SimpleNamespace(
        close_signal_admin=AsyncMock(return_value={"closed": True, "signal_id": "sig-7"}),
        close_position_for_user=AsyncMock(),
    )
    redis = _ScriptedRedis([])
    env = json.dumps({"kind": "close", "request_id": "o1", "signal_id": "sig-7"})
    await manual_take.ManualTakeConsumer(engine, redis)._process(env)
    engine.close_signal_admin.assert_awaited_once_with("sig-7")
    engine.close_position_for_user.assert_not_awaited()
    assert _result(redis, store.KEY_TAKE_RESULT_PREFIX, "o1")["closed"] is True


async def test_owner_close_crash_reports_not_closed() -> None:
    engine = SimpleNamespace(close_signal_admin=AsyncMock(side_effect=RuntimeError("x")))
    redis = _ScriptedRedis([])
    env = json.dumps({"kind": "close", "request_id": "o1", "signal_id": "sig-7"})
    await manual_take.ManualTakeConsumer(engine, redis)._process(env)
    out = _result(redis, store.KEY_TAKE_RESULT_PREFIX, "o1")
    assert out["closed"] is False and out["reason"] == "x"


# ---------------------------------------------------------------------------
# kind="manual_trade" — the chart trade builder
# ---------------------------------------------------------------------------


def _manual(request_id="m1", *, ts=None, payload=None):
    return json.dumps({
        "kind": "manual_trade", "request_id": request_id, "uid": "fb-U",
        "ts": time.time() if ts is None else ts,
        "payload": {"ref_id": "ref-1", "symbol": "BTCUSDT"} if payload is None else payload,
    })


async def test_a_fresh_manual_trade_reaches_the_builder_with_its_payload() -> None:
    engine = SimpleNamespace(build_manual_trade_for_user=AsyncMock(
        return_value={"outcome": "placed", "ref_id": "ref-1"},
    ))
    redis = _ScriptedRedis([])
    await manual_take.ManualTakeConsumer(engine, redis)._process(_manual())
    engine.build_manual_trade_for_user.assert_awaited_once_with(
        "fb-U", {"ref_id": "ref-1", "symbol": "BTCUSDT"},
    )
    assert _result(redis, store.KEY_TAKE_RESULT_PREFIX, "m1")["outcome"] == "placed"


async def test_a_stale_manual_trade_is_refused_for_the_users_safety() -> None:
    """A market or limit order fired minutes after Confirm is at a price the
    user never saw — the same refusal the take path makes."""
    engine = SimpleNamespace(build_manual_trade_for_user=AsyncMock())
    redis = _ScriptedRedis([])
    old = time.time() - store.TAKE_CMD_STALE_S - 1
    await manual_take.ManualTakeConsumer(engine, redis)._process(_manual(ts=old))
    engine.build_manual_trade_for_user.assert_not_awaited()
    out = _result(redis, store.KEY_TAKE_RESULT_PREFIX, "m1")
    assert out["reject_class"] == "TradeRequestStale"
    assert out["ref_id"] == "ref-1"


async def test_a_manual_trade_without_a_payload_object_is_dropped() -> None:
    engine = SimpleNamespace(build_manual_trade_for_user=AsyncMock())
    redis = _ScriptedRedis([])
    await manual_take.ManualTakeConsumer(engine, redis)._process(_manual(payload="BTCUSDT"))
    engine.build_manual_trade_for_user.assert_not_awaited()
    assert redis.written == {}


async def test_a_crashing_manual_trade_still_answers() -> None:
    engine = SimpleNamespace(build_manual_trade_for_user=AsyncMock(side_effect=ValueError("bad sl")))
    redis = _ScriptedRedis([])
    await manual_take.ManualTakeConsumer(engine, redis)._process(_manual())
    out = _result(redis, store.KEY_TAKE_RESULT_PREFIX, "m1")
    assert out["outcome"] == "rejected" and out["reject_class"] == "ValueError"


# ---------------------------------------------------------------------------
# SafetySwitchConsumer.start — the emergency stop's transport
# ---------------------------------------------------------------------------


class _KillSwitchClient:
    def __init__(self) -> None:
        self.calls: list = []

    def engage_global(self, reason=""):
        self.calls.append(("engage", reason))

    def disengage_global(self):
        self.calls.append(("disengage", None))


def _flip(request_id: str, value: bool, *, ts: float | None = None) -> str:
    return json.dumps({"request_id": request_id, "switch": "kill_switch", "value": value,
                       "reason": "ops", "ts": time.time() if ts is None else ts})


async def test_the_switch_drain_applies_flips_in_order_through_faults() -> None:
    client = _KillSwitchClient()
    redis = _ScriptedRedis([
        None,
        _flip("r1", True),
        RuntimeError("redis blip"),
        _flip("r2", False),
    ])
    consumer = bridge.SafetySwitchConsumer(redis, get_client=lambda: client)
    with pytest.raises(asyncio.CancelledError):
        await consumer.start()
    assert client.calls == [("engage", "ops"), ("disengage", None)]
    assert set(redis.brpop_keys) == {store.KEY_CMD_SWITCH}
    assert _result(redis, store.KEY_SWITCH_RESULT_PREFIX, "r1")["ok"] is True
    assert _result(redis, store.KEY_SWITCH_RESULT_PREFIX, "r2")["ok"] is True


async def test_the_switch_drain_waits_out_an_unavailable_redis() -> None:
    client = _KillSwitchClient()
    redis = _ScriptedRedis([_flip("r1", True)], unavailable_polls=2)
    consumer = bridge.SafetySwitchConsumer(redis, get_client=lambda: client)
    with pytest.raises(asyncio.CancelledError):
        await consumer.start()
    assert client.calls == [("engage", "ops")]


async def test_a_stale_flip_in_the_queue_is_refused_not_applied() -> None:
    client = _KillSwitchClient()
    old = time.time() - store.SWITCH_CMD_STALE_S - 1
    redis = _ScriptedRedis([_flip("r1", False, ts=old)])
    consumer = bridge.SafetySwitchConsumer(redis, get_client=lambda: client)
    with pytest.raises(asyncio.CancelledError):
        await consumer.start()
    assert client.calls == []
    assert _result(redis, store.KEY_SWITCH_RESULT_PREFIX, "r1")["ok"] is False
