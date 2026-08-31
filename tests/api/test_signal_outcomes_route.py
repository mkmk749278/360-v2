"""``GET /api/auto-trade/signal-outcomes`` — the join the app never had.

Owner, 2026-08-31: *"why don't we show actually same like signal it's
outcome, actually what traded in binance ... with that user can
understand what actually engine produced and what's traded in binance"*.

Both halves already existed and had never been joined.  The position
document has carried ``entry_price_filled`` / ``filled_qty`` /
``realized_pnl_total`` / ``close_reason`` / ``closed_at`` since the FSM
shipped; ``GET /api/auto-trade/positions`` excludes terminal states by
design and pointed at a trade-records endpoint still marked ``TBD``.  So
the app's only per-signal record of an order was the dispatch *event* —
a record of an ATTEMPT with no outcome on it — which is why a placed row
asserts "Position is open" in the present tense forever and can sit
directly beneath "YOUR OPEN POSITIONS 0".

Pinned here:

* open and closed positions both surface, with the money fields Binance
  actually produced;
* "not traded" splits into ``rejected`` (something refused) and
  ``preference`` (the user's own filter declined it) — two states with
  two different next moves, and pooling them makes a working account
  read as a broken one;
* where a position and an event describe the same signal the POSITION
  wins on every money field, and the event contributes only ``source``;
* a ``placed`` event with no position inside the window is omitted
  rather than invented as an outcome;
* the window sizes and truncation flags ride the payload, because
  "absent from this response" and "not traded" are different facts.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.execution import dispatch_log, position_state

NOW = datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def _reset():
    position_state.reset_for_test()
    dispatch_log.reset_for_test()
    yield
    position_state.reset_for_test()
    dispatch_log.reset_for_test()


def _build_app(uid: str = "fb-o") -> FastAPI:
    from src.api import auto_trade_status_routes

    app = FastAPI()
    auto_trade_status_routes.register(
        app,
        auth=lambda: None,
        identity_dep=lambda: SimpleNamespace(firebase_uid=uid, user_id=7),
    )
    return app


def _position(signal_id: str, *, state, closed_at=None, **kw):
    base = dict(
        signal_id=signal_id,
        firebase_uid="fb-o",
        symbol="BTCUSDT",
        side="LONG",
        state=state,
        entry_price_target=29000.0,
        entry_price_filled=29005.5,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        filled_qty=1.0,
        created_at=NOW,
        closed_at=closed_at,
    )
    base.update(kw)
    return position_state.Position(**base)


def _event(signal_id: str, outcome: str, **kw):
    base = dict(
        event_id=f"e-{signal_id}",
        firebase_uid="fb-o",
        signal_id=signal_id,
        symbol="ETHUSDT",
        direction="SHORT",
        outcome=outcome,
        timestamp=NOW - timedelta(minutes=5),
        entry_price=1800.0,
    )
    base.update(kw)
    return dispatch_log.DispatchEvent(**base)


def _wire(monkeypatch, *, open_=(), closed=(), events=()):
    position_state._db = MagicMock()
    monkeypatch.setattr(
        position_state, "list_positions_for_user",
        lambda uid, **kw: list(open_),
    )
    monkeypatch.setattr(
        position_state, "list_recent_closed_positions_for_user",
        lambda uid, **kw: list(closed),
    )
    monkeypatch.setattr(
        dispatch_log, "list_recent_events", lambda uid, **kw: list(events),
    )


def _get(monkeypatch, **wiring) -> dict:
    _wire(monkeypatch, **wiring)
    r = TestClient(_build_app()).get("/api/auto-trade/signal-outcomes")
    assert r.status_code == 200, r.text
    return r.json()


def _by_id(body: dict) -> dict:
    return {row["signal_id"]: row for row in body["outcomes"]}


# ---------------------------------------------------------------------------
# The traded half — what Binance actually did
# ---------------------------------------------------------------------------


def test_open_position_reports_the_fill_not_the_signal_price(monkeypatch) -> None:
    body = _get(
        monkeypatch,
        open_=[_position("sig-open", state=position_state.PositionState.OPEN)],
    )
    row = _by_id(body)["sig-open"]
    assert row["status"] == "open"
    assert row["state"] == "OPEN"
    # 29005.5 is the fill; 29000.0 is what the signal asked for.  The
    # whole point of the endpoint is that these are different numbers.
    assert row["entry_price_filled"] == 29005.5
    assert row["closed_at"] is None


def test_closed_position_reports_realized_pnl_and_close_reason(monkeypatch) -> None:
    closed_at = NOW + timedelta(hours=2)
    body = _get(
        monkeypatch,
        closed=[
            _position(
                "sig-done",
                state=position_state.PositionState.CLOSED,
                closed_at=closed_at,
                close_reason="TP1",
                realized_pnl_total=12.34,
            )
        ],
    )
    row = _by_id(body)["sig-done"]
    assert row["status"] == "closed"
    assert row["close_reason"] == "TP1"
    assert row["realized_pnl_usd"] == 12.34
    assert row["closed_at"] == closed_at.isoformat()
    assert body["closed_window"] == 1


# ---------------------------------------------------------------------------
# The not-traded half — two classes, two next moves
# ---------------------------------------------------------------------------


def test_rejection_and_preference_are_different_classes(monkeypatch) -> None:
    body = _get(
        monkeypatch,
        events=[
            _event(
                "sig-rej", "rejected",
                reject_class="OrderRejectedByBinance",
                reject_detail="code=-2019 Margin is insufficient",
                reject_binance_code=-2019,
            ),
            _event(
                "sig-pref", "skipped",
                skip_reason="path_preference",
                reject_detail="RANGE_FADE is not in your auto-trade setup list.",
            ),
        ],
    )
    rows = _by_id(body)
    assert rows["sig-rej"]["status"] == "not_traded"
    assert rows["sig-rej"]["not_traded_class"] == "rejected"
    assert rows["sig-rej"]["binance_code"] == -2019
    assert rows["sig-pref"]["not_traded_class"] == "preference"
    assert rows["sig-pref"]["not_traded_reason"] == "path_preference"
    # Nothing the user must act on: their own filter declined it.
    assert rows["sig-pref"]["binance_code"] is None


def test_placed_event_without_a_position_is_omitted_not_invented(
    monkeypatch,
) -> None:
    """The position is older than the closed window reached.  Recording
    it as ``not_traded`` would be a fabricated outcome on the one surface
    a subscriber reads to decide whether the product works."""
    body = _get(monkeypatch, events=[_event("sig-old", "placed")])
    assert body["outcomes"] == []


# ---------------------------------------------------------------------------
# Precedence + honesty of the windows
# ---------------------------------------------------------------------------


def test_position_wins_over_the_event_but_event_supplies_source(
    monkeypatch,
) -> None:
    body = _get(
        monkeypatch,
        open_=[_position("sig-both", state=position_state.PositionState.OPEN)],
        events=[
            _event(
                "sig-both", "rejected", symbol="ETHUSDT",
                reject_class="ShouldNotWin", source="manual_take",
            )
        ],
    )
    row = _by_id(body)["sig-both"]
    assert row["status"] == "open"
    assert row["symbol"] == "BTCUSDT"          # the position's, not the event's
    assert row["not_traded_reason"] is None
    assert row["source"] == "manual_take"      # the only field the event owns
    assert len(body["outcomes"]) == 1


def test_windows_and_truncation_are_published(monkeypatch) -> None:
    """"Absent from this response" and "not traded on this account" are
    different facts, and only the window counts let the caller tell them
    apart."""
    _wire(
        monkeypatch,
        closed=[
            _position(
                f"c{i}", state=position_state.PositionState.CLOSED,
                closed_at=NOW,
            )
            for i in range(3)
        ],
    )
    body = TestClient(_build_app()).get(
        "/api/auto-trade/signal-outcomes?limit=3"
    ).json()
    assert body["closed_window"] == 3
    assert body["closed_truncated"] is True
    assert body["events_truncated"] is False


def test_requires_firebase_sign_in() -> None:
    from src.api import auto_trade_status_routes

    app = FastAPI()
    auto_trade_status_routes.register(
        app, auth=lambda: None, identity_dep=lambda: None,
    )
    assert TestClient(app).get(
        "/api/auto-trade/signal-outcomes"
    ).status_code == 401
