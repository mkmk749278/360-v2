"""Tests for src.api.take_signal_route (POST /api/auto-trade/take).

Same wiring pattern as test_auto_trade_status_routes: auth stub +
identity stub + minimal FastAPI app.  The engine is a stub in direct
mode and a name-matched facade double in isolated mode (the route
branches on ``type(engine).__name__ == "RedisEngineFacade"``).
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.api import take_signal_route


def _build_app(
    *, engine: object, identity: object = None, allow_auth: bool = True
) -> FastAPI:
    app = FastAPI()

    def _auth_stub() -> None:
        if not allow_auth:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="missing token")
        return None

    def _identity_stub() -> object:
        return identity

    take_signal_route.register(
        app, engine=engine, auth=_auth_stub, identity_dep=_identity_stub,
    )
    return app


def _firebase_user(uid: str = "fb-take") -> object:
    return SimpleNamespace(firebase_uid=uid, user_id=7)


@pytest.fixture(autouse=True)
def _enable_flag_and_neutral_deps(monkeypatch):
    """Flag ON + tier gate transparent + keystore uninitialised (skips the
    key pre-check) for every test; individual tests override."""
    import config as _config

    monkeypatch.setattr(_config, "AUTO_TRADE_MANUAL_TAKE_ENABLED", True)
    monkeypatch.setattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", False)
    from src.security import firestore_keystore as _fk
    _fk.reset_for_test()
    yield
    _fk.reset_for_test()


def _direct_engine(result=None):
    """Engine stub for single-process mode (class name != facade)."""
    return SimpleNamespace(
        take_signal_for_user=AsyncMock(
            return_value=result or {"outcome": "placed", "signal_id": "sig-1"},
        ),
    )


def test_flag_off_returns_503(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_MANUAL_TAKE_ENABLED", False)
    app = _build_app(engine=_direct_engine(), identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 503


def test_requires_firebase_identity() -> None:
    app = _build_app(engine=_direct_engine(), identity=None)
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 401


def test_tier_gate_403_for_free_user(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", True)
    from src.api import users as _users

    fake_store = MagicMock()
    fake_store.aget_by_firebase_uid = AsyncMock(
        return_value=MagicMock(user_id=7, tier="free", paid_until=None),
    )
    monkeypatch.setattr(_users, "_store", fake_store, raising=False)

    app = _build_app(engine=_direct_engine(), identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 403
    assert "Assist" in r.json()["detail"]


def test_tier_gate_passes_assist_user(monkeypatch) -> None:
    import config as _config
    monkeypatch.setattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", True)
    from src.api import users as _users

    fake_store = MagicMock()
    fake_store.aget_by_firebase_uid = AsyncMock(
        return_value=MagicMock(user_id=7, tier="assist", paid_until=None),
    )
    monkeypatch.setattr(_users, "_store", fake_store, raising=False)

    app = _build_app(engine=_direct_engine(), identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 200
    assert r.json()["outcome"] == "placed"


def test_no_server_key_returns_409(monkeypatch) -> None:
    from src.security import firestore_keystore as _fk

    _fk._db = MagicMock()  # initialised
    def _no_blob(uid: str):
        raise _fk.KeyBlobNotFoundError(uid)
    monkeypatch.setattr(_fk, "get_key_blob", _no_blob)

    app = _build_app(engine=_direct_engine(), identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 409
    assert "Server-side auto-trade" in r.json()["detail"]


def test_direct_mode_relays_engine_result() -> None:
    engine = _direct_engine(
        result={
            "outcome": "rejected",
            "reject_class": "AlreadyActive",
            "reject_detail": "You already hold a position on this signal.",
            "signal_id": "sig-1",
        },
    )
    app = _build_app(engine=engine, identity=_firebase_user(uid="fb-D"))
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["outcome"] == "rejected"
    assert body["reject_class"] == "AlreadyActive"
    engine.take_signal_for_user.assert_awaited_once_with("fb-D", "sig-1")


# ---------------------------------------------------------------------------
# Isolated mode — facade double (class NAME must match the route's branch)
# ---------------------------------------------------------------------------


class RedisEngineFacade:  # noqa: N801 — name-matched test double
    """Minimal facade double: snapshot pre-validation + queue + result."""

    def __init__(
        self, *, snapshot=None, enqueue_ok=True, result=None,
        result_after_polls=1,
    ) -> None:
        self._snapshot = snapshot
        self._enqueue_ok = enqueue_ok
        self._result = result
        self._polls_needed = result_after_polls
        self._polls_seen = 0
        self.enqueued: list = []

    async def refresh_signals_all(self) -> None:
        return None

    def published_signal(self, signal_id: str):
        return self._snapshot

    async def enqueue_manual_take(self, *, request_id, uid, signal_id):
        if not self._enqueue_ok:
            return False
        self.enqueued.append((request_id, uid, signal_id))
        return True

    async def read_manual_take_result(self, request_id: str):
        self._polls_seen += 1
        if self._result is not None and self._polls_seen >= self._polls_needed:
            return self._result
        return None


@pytest.fixture(autouse=True)
def _fast_poll(monkeypatch):
    """Shrink the poll window so timeout tests run in milliseconds."""
    monkeypatch.setattr(take_signal_route, "_RESULT_POLL_TIMEOUT_S", 0.3)
    monkeypatch.setattr(take_signal_route, "_RESULT_POLL_INTERVAL_S", 0.01)


def test_isolated_mode_enqueues_and_returns_engine_result() -> None:
    facade = RedisEngineFacade(
        result={"outcome": "placed", "signal_id": "sig-1", "total_qty": 0.017},
    )
    app = _build_app(engine=facade, identity=_firebase_user(uid="fb-I"))
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 200
    assert r.json()["outcome"] == "placed"
    assert len(facade.enqueued) == 1
    _req_id, uid, sid = facade.enqueued[0]
    assert (uid, sid) == ("fb-I", "sig-1")


def test_isolated_mode_snapshot_closed_signal_short_circuits() -> None:
    facade = RedisEngineFacade(
        snapshot={"signal_id": "sig-1", "is_open": False, "status": "SL_HIT"},
        result={"outcome": "placed"},
    )
    app = _build_app(engine=facade, identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["outcome"] == "rejected"
    assert body["reject_class"] == "SignalClosed"
    assert facade.enqueued == []  # never reached the queue


def test_isolated_mode_redis_down_returns_503() -> None:
    facade = RedisEngineFacade(enqueue_ok=False)
    app = _build_app(engine=facade, identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 503


def test_isolated_mode_poll_timeout_returns_queued() -> None:
    facade = RedisEngineFacade(result=None)  # engine never answers
    app = _build_app(engine=facade, identity=_firebase_user())
    r = TestClient(app).post(
        "/api/auto-trade/take", json={"signal_id": "sig-1"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["outcome"] == "queued"
    assert "Recent Activity" in body["detail"]
