"""The Trade tab's positions in ISOLATED mode — driven across the real seam.

Until 2026-09-23 ``GET /api/auto-trade/positions`` and the position half of
``/api/auto-trade/signal-outcomes`` read ``position_state`` in the api
container, which in isolated mode (production) never initialises it.  Both
took their ``_db is None`` branch on every request: "YOUR OPEN POSITIONS 0"
whatever the user held, and no signal card ever showed its own outcome.  The
existing tests passed because each one patched ``position_state._db`` into the
api process — the one thing production never does.

These tests do not patch it.  They drive the engine's real publisher
(``SnapshotWriter._write_user_positions``) into a Redis double, read it back
through the real ``RedisEngineFacade``, and serve the real endpoints from a
process where ``position_state._db`` is None — exactly production's shape.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import snapshot_store as _store
from src.api.redis_engine import RedisEngineFacade
from src.api.snapshot_writer import SnapshotWriter
from src.execution import position_state as ps


class _FakeRedisClient:
    """The handful of redis-py asyncio calls the book path uses."""

    def __init__(self) -> None:
        self.kv: dict = {}
        self.hashes: dict = {}
        self.sets: dict = {}

    async def get(self, key):
        return self.kv.get(key)

    async def set(self, key, value, ex=None):
        self.kv[key] = value

    async def delete(self, key):
        self.kv.pop(key, None)

    async def hset(self, key, mapping):
        self.hashes.setdefault(key, {}).update(mapping)

    async def hget(self, key, field):
        return self.hashes.get(key, {}).get(field)

    async def exists(self, key):
        return int(key in self.kv or bool(self.hashes.get(key)))

    async def hgetall(self, key):
        return dict(self.hashes.get(key, {}))

    async def sadd(self, key, member):
        self.sets.setdefault(key, set()).add(member)

    async def spop(self, key):
        members = self.sets.get(key)
        return members.pop() if members else None


class _FakeRedis:
    def __init__(self, client: _FakeRedisClient) -> None:
        self.client = client
        self.available = True


class _WriteDb:
    """Firestore double for ``put_position``: accepts writes, counts none."""

    def collection(self, _name):
        return self

    def document(self, _id):
        return self

    def set(self, _data):
        return None


def _position(uid: str, sid: str, state: ps.PositionState, **kw) -> ps.Position:
    now = datetime.now(timezone.utc)
    base = dict(
        signal_id=sid,
        firebase_uid=uid,
        symbol=kw.pop("symbol", "BTCUSDT"),
        side="LONG",
        state=state,
        entry_price_target=100.0,
        entry_price_filled=100.5,
        sl_price=98.0,
        tp1_price=103.0,
        tp2_price=105.0,
        tp3_price=108.0,
        total_qty=1.0,
        tp1_qty=0.5,
        tp2_qty=0.3,
        tp3_qty=0.2,
        filled_qty=1.0,
        created_at=now - timedelta(minutes=30),
        last_event_at=now,
    )
    base.update(kw)
    return ps.Position(**base)


@pytest.fixture(autouse=True)
def _engine_process():
    """Engine side: a live index serving, as ``bootstrap`` leaves it."""
    ps.reset_for_test()
    ps._db = _WriteDb()
    ps._index_active = True
    yield
    ps.reset_for_test()


async def _publish(writer: SnapshotWriter) -> None:
    await writer._write_user_positions()


def _as_api_process():
    """Flip this process into the api container's shape: no position store."""
    ps._db = None


def _app(facade: RedisEngineFacade, uid: str) -> FastAPI:
    from src.api import auto_trade_status_routes

    app = FastAPI()
    auto_trade_status_routes.register(
        app,
        auth=lambda: None,
        identity_dep=lambda: SimpleNamespace(firebase_uid=uid, user_id=1),
        get_engine=lambda: facade,
    )
    return app


async def test_open_position_reaches_the_trade_tab_in_isolated_mode(monkeypatch):
    client = _FakeRedisClient()
    redis = _FakeRedis(client)
    writer = SnapshotWriter(engine=SimpleNamespace(), redis_client=redis)

    ps.put_position(_position("u1", "sig-open", ps.PositionState.OPEN))
    await _publish(writer)

    _as_api_process()
    facade = RedisEngineFacade(redis)
    r = TestClient(_app(facade, "u1")).get("/api/auto-trade/positions")
    assert r.status_code == 200
    body = r.json()
    assert body["positions_state"] == "reporting"
    assert [p["signal_id"] for p in body["positions"]] == ["sig-open"]
    assert body["positions"][0]["entry_price_filled"] == 100.5


def test_a_cold_engine_is_unavailable_not_an_empty_account():
    """No meta key = the engine is not publishing.  Must not read as 0 open."""
    redis = _FakeRedis(_FakeRedisClient())
    _as_api_process()
    body = TestClient(_app(RedisEngineFacade(redis), "u1")).get(
        "/api/auto-trade/positions"
    ).json()
    assert body["positions"] == []
    assert body["positions_state"] == "unavailable"


async def test_engine_publishes_nothing_until_its_index_serves():
    ps._index_active = False
    client = _FakeRedisClient()
    writer = SnapshotWriter(engine=SimpleNamespace(), redis_client=_FakeRedis(client))
    await _publish(writer)
    assert _store.KEY_USER_POSITIONS_META not in client.kv


async def test_closed_position_reaches_signal_outcomes(monkeypatch):
    from src.execution import dispatch_log

    monkeypatch.setattr(dispatch_log, "list_recent_events", lambda uid, limit=20: [])
    client = _FakeRedisClient()
    redis = _FakeRedis(client)
    writer = SnapshotWriter(engine=SimpleNamespace(), redis_client=redis)

    ps.put_position(_position("u1", "sig-a", ps.PositionState.OPEN))
    ps.put_position(
        _position(
            "u1", "sig-a", ps.PositionState.CLOSED,
            closed_at=datetime.now(timezone.utc),
            close_reason="TP1", realized_pnl_total=1.25,
        )
    )
    await _publish(writer)

    _as_api_process()
    body = TestClient(_app(RedisEngineFacade(redis), "u1")).get(
        "/api/auto-trade/signal-outcomes"
    ).json()
    assert body["positions_state"] == "reporting"
    [row] = body["outcomes"]
    assert row["status"] == "closed"
    assert row["close_reason"] == "TP1"
    assert row["realized_pnl_usd"] == 1.25
    # Not yet seeded from history: the api asked, and says the window is partial.
    assert body["closed_complete"] is False
    assert "u1" in client.sets[_store.KEY_CMD_SEED_CLOSED]


async def test_seed_runs_once_per_user_and_is_bounded(monkeypatch):
    calls = []
    older = _position(
        "u1", "sig-old", ps.PositionState.CLOSED,
        closed_at=datetime.now(timezone.utc) - timedelta(days=2),
    )

    def _fake_history(uid, *, limit):
        calls.append((uid, limit))
        return [older]

    monkeypatch.setattr(ps, "list_recent_closed_positions_for_user", _fake_history)
    client = _FakeRedisClient()
    redis = _FakeRedis(client)
    writer = SnapshotWriter(engine=SimpleNamespace(), redis_client=redis)
    client.sets[_store.KEY_CMD_SEED_CLOSED] = {"u1"}
    await _publish(writer)
    # Asked again after seeding: no second query.
    client.sets[_store.KEY_CMD_SEED_CLOSED] = {"u1"}
    await _publish(writer)

    assert calls == [("u1", ps.CLOSED_RING)]
    book = ps.user_book("u1")
    assert book["closed_seeded"] is True
    assert [r["signal_id"] for r in book["closed"]] == ["sig-old"]


async def test_closed_history_survives_an_engine_restart():
    """The hash has no TTL and is restored at boot, so a deploy does not
    re-read every user's history from Firestore."""
    client = _FakeRedisClient()
    redis = _FakeRedis(client)
    ps.put_position(
        _position("u1", "sig-c", ps.PositionState.CLOSED,
                  closed_at=datetime.now(timezone.utc))
    )
    ps.seed_closed("u1", [])
    await _publish(SnapshotWriter(engine=SimpleNamespace(), redis_client=redis))

    # Restart: a fresh process with an empty book and a new writer.
    ps.reset_for_test()
    ps._db = _WriteDb()
    ps._index_active = True
    await _publish(SnapshotWriter(engine=SimpleNamespace(), redis_client=redis))

    book = ps.user_book("u1")
    assert book["closed_seeded"] is True
    assert [r["signal_id"] for r in book["closed"]] == ["sig-c"]


def test_the_ring_is_bounded_and_newest_first():
    base = datetime.now(timezone.utc)
    for i in range(ps.CLOSED_RING + 10):
        ps.put_position(
            _position("u1", f"sig-{i}", ps.PositionState.CLOSED,
                      closed_at=base + timedelta(minutes=i))
        )
    closed = ps.user_book("u1")["closed"]
    assert len(closed) == ps.CLOSED_RING
    assert closed[0]["signal_id"] == f"sig-{ps.CLOSED_RING + 9}"


def test_wire_round_trip_preserves_every_field():
    p = _position(
        "u1", "sig-w", ps.PositionState.CLOSED,
        closed_at=datetime.now(timezone.utc), close_reason="SL",
        realized_pnl_total=-2.5, exit_mechanism="sar",
    )
    back = ps.from_wire(ps.to_wire(p))
    assert ps._to_firestore_dict(back) == ps._to_firestore_dict(p)


async def test_a_quiet_book_publishes_nothing_after_the_first_pass():
    client = _FakeRedisClient()
    writer = SnapshotWriter(engine=SimpleNamespace(), redis_client=_FakeRedis(client))
    ps.put_position(_position("u1", "sig-q", ps.PositionState.OPEN))
    await _publish(writer)
    first = writer.user_book_counters["published"]
    await _publish(writer)
    await _publish(writer)
    assert writer.user_book_counters["published"] == first


def test_api_main_still_does_not_open_the_position_store():
    """The design premise: the api reads the engine's book instead of opening
    its own store.  If a later change wires ``init_position_state`` into the
    api entry point, the per-request Firestore cost returns and this should be
    revisited deliberately rather than by accident."""
    import pathlib

    src = pathlib.Path("src/api/main.py").read_text()
    assert "init_position_state" not in src


async def test_an_evicted_book_is_unavailable_then_republished():
    """Redis runs allkeys-lru at 128 MB.  If the hash is evicted, a user with
    open positions must read "unavailable" — never "not_reported", which the
    app renders as an empty account — and the engine republishes from memory."""
    client = _FakeRedisClient()
    redis = _FakeRedis(client)
    writer = SnapshotWriter(engine=SimpleNamespace(), redis_client=redis)
    ps.put_position(_position("u1", "sig-e", ps.PositionState.OPEN))
    await _publish(writer)

    client.hashes.pop(_store.KEY_USER_POSITIONS)          # evicted
    facade = RedisEngineFacade(redis)
    book, state = await facade.read_user_positions("u1")
    assert (book, state) == (None, "unavailable")

    await _publish(writer)                                # engine's next pass
    book, state = await facade.read_user_positions("u1")
    assert state == "reporting"
    assert [r["signal_id"] for r in book["open"]] == ["sig-e"]


def test_the_published_row_is_the_slim_projection():
    """Every published row carries only BOOK_FIELDS, so the book stays small
    inside a 128 MB LRU cache shared with the feed keys."""
    ps.put_position(_position("u1", "sig-s", ps.PositionState.OPEN))
    [row] = ps.user_book("u1")["open"]
    assert set(row) == set(ps.BOOK_FIELDS)


def test_a_ring_failure_never_breaks_the_fsm_write(monkeypatch):
    """The ring is display-only and runs inside put_position: a failure there
    is counted and swallowed, and the position write still completes."""
    from src import fail_open

    def _boom(_p):
        raise RuntimeError("ring broke")

    monkeypatch.setattr(ps, "_closed_ring_push_locked", _boom)
    seen = []
    monkeypatch.setattr(fail_open, "record", lambda site, exc: seen.append(site))
    ps.put_position(_position("u1", "sig-f", ps.PositionState.CLOSED))
    assert seen == ["position_state.closed_ring"]
    assert ps.get_write_generation() == 1
