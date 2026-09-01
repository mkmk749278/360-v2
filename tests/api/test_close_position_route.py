"""``POST /api/auto-trade/close`` — a user closing their OWN position.

Owner, 2026-09-01: *"user can close that trade from our app to without
visiting binance to close signals manually"*.

Until now the app could open a position server-side and could not close one.
Every exit belonged to the engine — a TP, a stop, an invalidation, or the
reconciler's 2h backstop — so a subscriber wanting out early had to leave the
app, and the engine then inferred the close a reconciler cycle later from a
flat positionRisk read.

What is pinned, and each of these is a decision rather than an implementation
detail:

* the blast radius is ONE user's position.  The signal stays in the book for
  everyone else, and the response says so, because the app renders an ACTIVE
  signal card directly beside this;
* business refusals answer **200** with ``outcome="rejected"`` — nothing open,
  already closed, Binance said no.  They are outcomes the Recent Activity card
  already renders, not transport errors;
* a position that is already terminal names WHY it closed.  "Already closed"
  with no cause reads as the button being broken;
* there is no tier gate.  Every other gate on this engine decides whether a
  user may ENTER; refusing to let someone out of a live position because their
  plan lapsed would strand real money behind a paywall;
* a poll timeout answers ``queued``, never a failure — a second tap on a flat
  position is how a user opens the opposite side by accident.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.execution import position_state

NOW = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _reset():
    position_state.reset_for_test()
    yield
    position_state.reset_for_test()


def _client(engine, uid: str = "fb-o") -> TestClient:
    from src.api import close_position_route

    app = FastAPI()
    close_position_route.register(
        app,
        engine=engine,
        auth=lambda: None,
        identity_dep=lambda: SimpleNamespace(firebase_uid=uid, user_id=7),
    )
    return TestClient(app)


class _DirectEngine:
    """Single-process mode: the engine is in this process."""

    def __init__(self, result):
        self.result = result
        self.calls: list = []

    async def close_position_for_user(self, uid, signal_id):
        self.calls.append((uid, signal_id))
        return self.result


class RedisEngineFacade:  # noqa: N801 — the route routes on the class NAME
    """Isolated mode stand-in: named to match what the route checks."""

    def __init__(self, *, enqueue=True, result=None):
        self._enqueue = enqueue
        self._result = result
        self.enqueued: list = []

    async def enqueue_close_position(self, *, request_id, uid, signal_id):
        self.enqueued.append((request_id, uid, signal_id))
        return self._enqueue

    async def read_manual_take_result(self, request_id):
        return self._result


# ---------------------------------------------------------------------------
# Transport vs outcome
# ---------------------------------------------------------------------------


def test_a_close_reaches_the_engine_with_the_callers_own_uid():
    engine = _DirectEngine({"outcome": "closed", "signal_id": "sig-1"})
    resp = _client(engine).post(
        "/api/auto-trade/close", json={"signal_id": "sig-1"}
    )
    assert resp.status_code == 200
    assert resp.json()["outcome"] == "closed"
    # The uid comes from the verified identity, never from the body — a user
    # can only ever address their own position.
    assert engine.calls == [("fb-o", "sig-1")]


def test_a_business_refusal_is_200_not_an_error():
    """The Recent Activity card renders these; an HTTP error would surface as
    "something went wrong" and lose the reason."""
    engine = _DirectEngine({
        "outcome": "rejected",
        "reject_class": "PositionNotFound",
        "reject_detail": "No position of yours is open on this signal.",
        "signal_id": "sig-1",
    })
    resp = _client(engine).post(
        "/api/auto-trade/close", json={"signal_id": "sig-1"}
    )
    assert resp.status_code == 200
    assert resp.json()["reject_class"] == "PositionNotFound"


def test_a_dead_bridge_is_503_and_says_the_position_is_untouched():
    engine = RedisEngineFacade(enqueue=False)
    resp = _client(engine).post(
        "/api/auto-trade/close", json={"signal_id": "sig-1"}
    )
    assert resp.status_code == 503
    assert "untouched" in resp.json()["detail"]


def test_an_unauthenticated_caller_is_refused():
    engine = _DirectEngine({"outcome": "closed"})
    from src.api import close_position_route

    app = FastAPI()
    close_position_route.register(
        app, engine=engine, auth=lambda: None, identity_dep=lambda: None,
    )
    assert TestClient(app).post(
        "/api/auto-trade/close", json={"signal_id": "s"}
    ).status_code == 401


def test_a_slow_engine_answers_queued_never_failed():
    """A close that has not answered yet is in flight.  Telling the user it
    failed invites a second tap, and a second close on a flat position is how
    somebody opens the opposite side by accident."""
    from src.api import close_position_route

    engine = RedisEngineFacade(result=None)
    close_position_route._RESULT_POLL_TIMEOUT_S = 0.4
    body = _client(engine).post(
        "/api/auto-trade/close", json={"signal_id": "sig-1"}
    ).json()
    assert body["outcome"] == "queued"
    assert "do not tap again" in body["detail"]
    assert engine.enqueued and engine.enqueued[0][1:] == ("fb-o", "sig-1")


# ---------------------------------------------------------------------------
# The engine method — blast radius and refusal copy
# ---------------------------------------------------------------------------


def _position(state, **kw):
    base = dict(
        signal_id="sig-1", firebase_uid="fb-o", symbol="BTCUSDT", side="LONG",
        state=state, entry_price_target=29000.0, entry_price_filled=29005.5,
        sl_price=28500.0, tp1_price=29500.0, tp2_price=30000.0,
        tp3_price=30500.0, total_qty=1.0, tp1_qty=0.3, tp2_qty=0.4,
        tp3_qty=0.3, filled_qty=1.0, created_at=NOW,
    )
    base.update(kw)
    return position_state.Position(**base)


def _engine():
    from src.main import CryptoSignalEngine

    # __new__ rather than __init__: the method under test touches nothing the
    # constructor builds, and standing up a whole engine to exercise a
    # Firestore read and one dispatch call would be testing the fixture.
    return CryptoSignalEngine.__new__(CryptoSignalEngine)


@pytest.mark.asyncio
async def test_closing_scopes_the_fanout_to_one_uid(monkeypatch):
    """The signal stays live for every other subscriber.  One person taking
    money off the table is not the setup being invalidated."""
    from src.execution import signal_dispatch

    position_state._db = MagicMock()
    monkeypatch.setattr(
        position_state, "get_position",
        lambda uid, sid: _position(position_state.PositionState.OPEN),
    )
    seen: dict = {}

    async def _close(signal_id, **kw):
        seen.update(kw, signal_id=signal_id)
        return 1

    monkeypatch.setattr(
        signal_dispatch, "close_fsm_positions_for_signal", _close
    )

    out = await _engine().close_position_for_user("fb-o", "sig-1")

    assert out["outcome"] == "closed"
    assert seen["only_uid"] == "fb-o"
    assert seen["reason"] == "USER_CLOSE"
    # Said on the wire, because the app renders the ACTIVE signal card right
    # beside this answer.
    assert out["signal_still_active"] is True


@pytest.mark.asyncio
async def test_an_already_closed_position_names_its_cause(monkeypatch):
    """"Already closed" with no cause reads as the button being broken.  It
    is also the single commonest case, because the 2h reconciler backstop
    closes positions the signal feed still shows as ACTIVE."""
    position_state._db = MagicMock()
    monkeypatch.setattr(
        position_state, "get_position",
        lambda uid, sid: _position(
            position_state.PositionState.CLOSED, close_reason="STALE_EXPIRY",
        ),
    )
    out = await _engine().close_position_for_user("fb-o", "sig-1")
    assert out["reject_class"] == "PositionAlreadyClosed"
    assert "STALE_EXPIRY" in out["reject_detail"]


@pytest.mark.asyncio
async def test_a_refused_close_says_the_stop_is_still_in_place(monkeypatch):
    """The one thing a user must know after a failed close: they are not
    naked.  ``close_fsm_positions_for_signal`` cancels the bracket only on a
    path that then closes, so a zero return means nothing was touched."""
    from src.execution import signal_dispatch

    position_state._db = MagicMock()
    monkeypatch.setattr(
        position_state, "get_position",
        lambda uid, sid: _position(position_state.PositionState.OPEN),
    )
    monkeypatch.setattr(
        signal_dispatch, "close_fsm_positions_for_signal",
        AsyncMock(return_value=0),
    )
    out = await _engine().close_position_for_user("fb-o", "sig-1")
    assert out["reject_class"] == "CloseFailed"
    assert "stop is still in place" in out["reject_detail"]


@pytest.mark.asyncio
async def test_a_missing_position_is_refused_not_crashed(monkeypatch):
    position_state._db = MagicMock()

    def _raise(uid, sid):
        raise position_state.PositionNotFoundError("nope")

    monkeypatch.setattr(position_state, "get_position", _raise)
    out = await _engine().close_position_for_user("fb-o", "sig-1")
    assert out["reject_class"] == "PositionNotFound"
