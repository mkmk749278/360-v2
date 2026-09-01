"""``GET /api/auto-trade/positions`` — priced the way Binance prices a position.

Owner, 2026-09-01, holding the Binance app beside the Trade tab: *"there we
have to show exactly how live open traded position shows in binance"*.

The endpoint returned the entry price and the geometry and nothing about what
the position is worth NOW, so the card could not answer the one question a
position card exists to answer, and the user left the app to find out.

The interesting part is where the price comes from.  The api container has no
mark-price feed and no signing socket, so it has three options and two of them
are wrong: fetching a price in the CLIENT puts a live number beside engine
state on a clock the page supplies (the defect ops paid for on 2026-07-30 —
a page reporting "LIVE" over arms that had consumed zero bars in 2h19m), and a
signed positionRisk call per poll is a vendor round trip on a path every
subscriber hits.  So the engine publishes the marks it is ALREADY holding and
this reads them.

Pinned here:

* the mark and the position state come from the same side, and the read's own
  age rides the envelope — a mark with no age beside it is a claim;
* an unmarked symbol is ``null``, never ``0.0``.  "The feed dropped this
  symbol" and "this is worth nothing" are different facts;
* PnL % is the move on the entry price — what Binance shows and what the
  signal card beside it shows — and is never divided by the stop distance,
  because this engine sizes at a fixed notional so R equalises nothing here;
* a partially-closed position is priced on what is still OPEN, not on what was
  originally placed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

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


class _Facade:
    """Isolated mode: marks arrive over Redis, not from a local feed."""

    def __init__(self, payload):
        self._payload = payload

    async def read_position_marks(self):
        return self._payload


def _client(positions, engine=None, uid="fb-o", monkeypatch=None):
    from src.api import auto_trade_status_routes

    position_state._db = MagicMock()
    monkeypatch.setattr(
        position_state, "list_positions_for_user", lambda u, **k: list(positions)
    )
    # No in-process feed in the api container — force the snapshot path.
    from src.execution import mark_price_feed as _mpf
    monkeypatch.setattr(_mpf, "get_instance", lambda: None)

    app = FastAPI()
    auto_trade_status_routes.register(
        app,
        auth=lambda: None,
        identity_dep=lambda: SimpleNamespace(firebase_uid=uid, user_id=7),
        get_engine=lambda: engine,
    )
    return TestClient(app)


def _position(**kw):
    base = dict(
        signal_id="sig-1", firebase_uid="fb-o", symbol="BTCUSDT", side="LONG",
        state=position_state.PositionState.OPEN, entry_price_target=29000.0,
        entry_price_filled=100.0, sl_price=95.0, tp1_price=110.0,
        tp2_price=115.0, tp3_price=120.0, total_qty=2.0, tp1_qty=0.6,
        tp2_qty=0.8, tp3_qty=0.6, filled_qty=2.0, created_at=NOW,
    )
    base.update(kw)
    return position_state.Position(**base)


def test_an_open_position_carries_its_live_mark_and_unrealized_pnl(monkeypatch):
    facade = _Facade({"BTCUSDT": 110.0, "__stamped_at__": 1_600_000_000.0})
    body = _client([_position()], facade, monkeypatch=monkeypatch).get(
        "/api/auto-trade/positions"
    ).json()

    row = body["positions"][0]
    assert row["mark_price"] == 110.0
    assert row["unrealized_pnl_pct"] == 10.0          # 100 → 110 long
    assert row["unrealized_pnl"] == 20.0              # 10 × 2 units
    assert row["notional"] == 220.0
    assert row["closeable"] is True
    # About the read, not the row.
    assert body["marks_stamped_at"] == 1_600_000_000.0
    assert body["marks_age_sec"] is not None


def test_a_short_makes_money_when_price_falls(monkeypatch):
    """Signed toward the TRADE, not toward price.  Half the book is short and
    an unsigned percentage would score every one of them backwards."""
    facade = _Facade({"BTCUSDT": 90.0, "__stamped_at__": 1.0})
    body = _client(
        [_position(side="SHORT")], facade, monkeypatch=monkeypatch
    ).get("/api/auto-trade/positions").json()
    assert body["positions"][0]["unrealized_pnl_pct"] == 10.0
    assert body["positions"][0]["unrealized_pnl"] == 20.0


def test_an_unmarked_symbol_is_null_never_zero(monkeypatch):
    """A dash means "the engine is not marking this"; 0.0 would read as a
    position worth nothing, which is a claim nobody made."""
    facade = _Facade({"ETHUSDT": 1800.0, "__stamped_at__": 1.0})
    row = _client([_position()], facade, monkeypatch=monkeypatch).get(
        "/api/auto-trade/positions"
    ).json()["positions"][0]
    assert row["mark_price"] is None
    assert row["unrealized_pnl"] is None
    assert row["unrealized_pnl_pct"] is None
    assert row["notional"] is None


def test_an_unreadable_snapshot_is_not_an_empty_one(monkeypatch):
    """``None`` from the reader means the engine stopped publishing or Redis
    is down.  The rows still render — the position is real — but nothing
    claims a price, and the missing stamp is what says so."""
    body = _client([_position()], _Facade(None), monkeypatch=monkeypatch).get(
        "/api/auto-trade/positions"
    ).json()
    assert body["positions"][0]["mark_price"] is None
    assert body["marks_stamped_at"] is None
    assert body["marks_age_sec"] is None


def test_a_partially_closed_position_is_priced_on_what_is_still_open(monkeypatch):
    """TP1 banked 0.6 of 2.0.  Pricing the original size would overstate what
    the user is actually holding."""
    facade = _Facade({"BTCUSDT": 110.0, "__stamped_at__": 1.0})
    row = _client(
        [_position(closed_qty=0.6, state=position_state.PositionState.TP1_HIT)],
        facade, monkeypatch=monkeypatch,
    ).get("/api/auto-trade/positions").json()["positions"][0]
    assert row["open_qty"] == pytest.approx(1.4)
    assert row["unrealized_pnl"] == pytest.approx(14.0)


def test_a_position_with_no_size_yet_is_not_closeable(monkeypatch):
    """The Close button and the engine agree on one rule, sent as a fact
    rather than inferred client-side from `state`."""
    facade = _Facade({"BTCUSDT": 110.0, "__stamped_at__": 1.0})
    row = _client(
        [_position(state=position_state.PositionState.PENDING)],
        facade, monkeypatch=monkeypatch,
    ).get("/api/auto-trade/positions").json()["positions"][0]
    assert row["closeable"] is False
