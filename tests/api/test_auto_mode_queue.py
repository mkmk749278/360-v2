"""The engine-wide mode change is QUEUED in isolated mode — make that observable.

Owner, 2026-09-26: *"There is some problem with auto execution mode toggle,
not showing correctly."* In production the api container cannot change the
mode itself: it queues a command in Redis and the engine applies it at the end
of its next ~15s writer cycle, and the api re-reads the engine state every 10s.
So ops said "Auto-mode set to PAPER" beside a toggle still reading LIVE, for up
to ~40s — or forever, when the engine REFUSED the change (open positions, no
exchange keys), because that answer lived only in the engine log.

And the stale read was worse than a display problem: "already in LIVE" was
judged against a state up to ~40s old and blind to the queue, so LIVE → PAPER
→ LIVE inside that window answered "nothing to do" to the undo and left PAPER
queued. These tests pin the repairs.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api import snapshot_store as store
from src.api.redis_engine import RedisEngineFacade
from src.api.snapshot_writer import SnapshotWriter


class _FakeRedis:
    def __init__(self) -> None:
        self._store: dict = {}
        self.available = True
        self.client = self
        self.fail_set = False

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        if self.fail_set:
            raise ConnectionError("boom")
        self._store[key] = value

    async def delete(self, key):
        self._store.pop(key, None)


def _facade(mode: str = "live", *, cached: str | None = None, pending: str | None = None):
    redis = _FakeRedis()
    redis._store[store.KEY_ENGINE_STATE] = store.encode(
        {"current_auto_mode": mode, "boot_auto_mode": "paper"}
    )
    if pending:
        redis._store[store.KEY_CMD_SET_MODE] = pending
    f = RedisEngineFacade(redis)
    # The 10s-refreshed copy — deliberately allowed to disagree with Redis.
    f._state = {"current_auto_mode": cached or mode}
    return f, redis

# Async tests, never asyncio.run: pytest-asyncio owns the loop here, and a test
# that closes its own leaves the session with no current loop (CLAUDE.md).


# ---- the facade answers against the QUEUE, not a stale copy ---------------


async def test_an_undo_inside_the_window_is_queued_not_swallowed():
    """LIVE, PAPER queued, then LIVE again: the old code said 'already in
    LIVE — nothing to do' and the engine switched to PAPER anyway."""
    f, redis = _facade("live", pending="paper")
    ok, msg, code = await f.aset_auto_execution_mode("live")
    assert (ok, code) == (True, 200)
    assert redis._store[store.KEY_CMD_SET_MODE] == "live"
    assert "replacing the pending change to PAPER" in msg


async def test_asking_for_what_is_already_queued_says_so():
    f, redis = _facade("live", pending="paper")
    ok, msg, code = await f.aset_auto_execution_mode("paper")
    assert (ok, code) == (False, 409)
    assert "already queued" in msg


async def test_already_there_with_nothing_queued_is_409():
    f, _ = _facade("paper")
    ok, msg, code = await f.aset_auto_execution_mode("paper")
    assert (ok, code) == (False, 409)
    assert "already in PAPER" in msg


async def test_current_is_read_from_redis_not_the_ten_second_copy():
    """The writer republishes state the moment a change applies; the 10s copy
    may still say LIVE. Judging against the copy is how an undo got lost."""
    f, redis = _facade("paper", cached="live")
    assert (await f.aset_auto_execution_mode("paper"))[2] == 409
    ok, _, code = await f.aset_auto_execution_mode("live")
    assert (ok, code) == (True, 200)
    assert redis._store[store.KEY_CMD_SET_MODE] == "live"


async def test_the_write_is_awaited_and_a_failure_is_reported():
    """The old path fired the write and forgot it: a lost command was a log
    line here while the caller was told 'queued'."""
    f, redis = _facade("live")
    redis.fail_set = True
    ok, msg, code = await f.aset_auto_execution_mode("paper")
    assert (ok, code) == (False, 503)
    assert "NOT queued" in msg
    assert store.KEY_CMD_SET_MODE not in redis._store


async def test_redis_down_is_503_not_queued():
    f, redis = _facade("live")
    redis.available = False
    ok, msg, code = await f.aset_auto_execution_mode("paper")
    assert (ok, code) == (False, 503)
    assert "NOT queued" in msg


async def test_status_reports_pending_result_and_boot_mode():
    f, redis = _facade("live", pending="paper")
    redis._store[store.KEY_CMD_SET_MODE_RESULT] = store.encode(
        {"requested": "off", "outcome": "refused", "message": "refused: 2 open position(s)"}
    )
    st = await f.mode_command_status()
    assert st["mode_queue"] == "queued"
    assert (st["mode"], st["pending_mode"], st["boot_mode"]) == ("live", "paper", "paper")
    assert st["last_mode_command"]["outcome"] == "refused"


async def test_an_unreadable_queue_is_not_an_empty_one():
    f, redis = _facade("live")
    redis.available = False
    st = await f.mode_command_status()
    assert st["mode_queue"] == "unreadable"
    assert "pending_mode" not in st


# ---- the writer publishes the engine's answer ------------------------------


class _Engine:
    def __init__(self, mode: str, answer: tuple) -> None:
        self._current_auto_mode = mode
        self._answer = answer
        self.calls: list = []

    def set_auto_execution_mode(self, new_mode):
        self.calls.append(new_mode)
        ok, msg = self._answer
        if ok:
            self._current_auto_mode = new_mode
        return ok, msg


def _writer(engine, pending: str):
    redis = _FakeRedis()
    redis._store[store.KEY_CMD_SET_MODE] = pending
    w = SnapshotWriter(engine, redis)
    republished: list = []

    async def _fake_state():
        republished.append(True)

    w._write_engine_state = _fake_state
    return w, redis, republished


def _result(redis) -> dict:
    return store.decode(redis._store[store.KEY_CMD_SET_MODE_RESULT])


async def test_a_refusal_is_published_not_just_logged():
    engine = _Engine("live", (False, "refused: 2 open position(s) — close them first"))
    w, redis, republished = _writer(engine, "paper")
    await w._apply_pending_mode_cmd()
    r = _result(redis)
    assert r["outcome"] == "refused"
    assert "2 open position" in r["message"]
    assert (r["requested"], r["mode"]) == ("paper", "live")
    assert republished == []  # nothing changed, nothing to republish
    assert store.KEY_CMD_SET_MODE not in redis._store


async def test_an_applied_change_republishes_state_at_once():
    engine = _Engine("live", (True, "mode changed"))
    w, redis, republished = _writer(engine, "paper")
    await w._apply_pending_mode_cmd()
    r = _result(redis)
    assert (r["outcome"], r["mode"]) == ("applied", "paper")
    assert republished == [True]


async def test_a_repeat_is_a_no_op_not_a_refusal():
    """An undo that raced the apply re-sends the current mode. Reporting that
    as 'refused' would tell the owner the engine declined something it had
    already done."""
    engine = _Engine("paper", (False, "should not be called"))
    w, redis, _ = _writer(engine, "paper")
    await w._apply_pending_mode_cmd()
    assert _result(redis)["outcome"] == "no_op"
    assert engine.calls == []


async def test_an_invalid_command_is_published_too():
    engine = _Engine("live", (True, ""))
    w, redis, _ = _writer(engine, "sideways")
    await w._apply_pending_mode_cmd()
    assert _result(redis)["outcome"] == "invalid"
    assert engine.calls == []


def test_boot_mode_is_published_from_the_engine_process():
    from src.api.snapshot_writer import _boot_auto_mode
    from config import AUTO_EXECUTION_MODE

    assert _boot_auto_mode() == AUTO_EXECUTION_MODE


# ---- the routes ------------------------------------------------------------


@pytest.fixture
def isolated():
    from src.api.server import build_app

    f, redis = _facade("live")
    app = build_app(f, jwt_secret="test-secret", static_token="test-token", allow_static=True)
    with TestClient(app) as client:
        yield client, redis


_AUTH = {"Authorization": "Bearer test-token"}


def test_post_says_the_change_was_queued(isolated):
    client, redis = isolated
    r = client.post("/api/auto-mode", json={"mode": "paper"}, headers=_AUTH)
    assert r.status_code == 200
    assert r.json()["queued"] is True
    assert redis._store[store.KEY_CMD_SET_MODE] == "paper"


def test_post_carries_the_facade_status_code(isolated):
    client, redis = isolated
    redis.available = False
    r = client.post("/api/auto-mode", json={"mode": "paper"}, headers=_AUTH)
    assert r.status_code == 503
    assert "NOT queued" in r.json()["detail"]


def test_command_endpoint_reads_the_queue(isolated):
    client, redis = isolated
    client.post("/api/auto-mode", json={"mode": "paper"}, headers=_AUTH)
    body = client.get("/api/auto-mode/command", headers=_AUTH).json()
    assert body["mode_queue"] == "queued"
    assert (body["mode"], body["pending_mode"], body["boot_mode"]) == ("live", "paper", "paper")


def test_command_endpoint_is_owner_only(isolated):
    """Same guard as the POST that changes the mode — derived from that
    route rather than from a name, which is a closure called ``_verify``."""
    client, _ = isolated
    assert client.get("/api/auto-mode/command").status_code in (401, 403)

    def _guards(path, method):
        route = next(
            r for r in client.app.routes
            if getattr(r, "path", "") == path and method in getattr(r, "methods", set())
        )
        return {d.call for d in route.dependant.dependencies}

    owner = _guards("/api/auto-mode", "POST")
    assert owner and owner <= _guards("/api/auto-mode/command", "GET")


def test_a_direct_engine_reports_direct():
    """Single-process: the change applies inside the POST, nothing is pending,
    and the page must not wait on a queue that does not exist."""
    from unittest.mock import MagicMock

    from src.api.server import build_app

    engine = MagicMock()
    engine._current_auto_mode = "paper"
    engine.set_auto_execution_mode.return_value = (True, "changed")
    app = build_app(engine, jwt_secret="test-secret", static_token="test-token", allow_static=True)
    with TestClient(app) as client:
        body = client.get("/api/auto-mode/command", headers=_AUTH).json()
        assert (body["mode_queue"], body["mode"]) == ("direct", "paper")
        r = client.post("/api/auto-mode", json={"mode": "live"}, headers=_AUTH)
        assert r.json()["queued"] is False
