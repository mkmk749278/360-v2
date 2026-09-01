"""``GET /api/auto-trade/positions`` as a JOIN — what the engine set up
against what Binance actually holds.

Owner, 2026-09-01: *"there we have to show exactly how live open traded
position shows in binance"*, over a Signals tab showing five ACTIVE signals
and a Trade tab showing nothing.

The first cut of this endpoint answered from the engine's own position
document and marked it with a price.  That is what the engine INTENDED, and
after a partial fill, a manual close, or the two-hour reconciler backstop
(39 of 140 positions in the owner's window) it is not what the account holds.
The exchange was describing the position the whole time and nothing read it:
``ACCOUNT_UPDATE`` was parsed and dropped, and ``positionRisk`` was fetched
every cycle with everything but ``positionAmt`` discarded.

What is pinned here is the reading, and mostly the distinctions that would
otherwise collapse into a number that looks right:

* the exchange supplies size and entry when it has spoken, and every row says
  WHICH source answered;
* a stale REST snapshot never overrides a live push (that is asserted in
  ``test_exchange_positions``; here we assert the endpoint honours the result);
* ``exchange_state`` has THREE values — an engine that has said nothing must
  never render as a flat account;
* the divergence the owner saw is NAMED, not left to be inferred from nulls;
* a position Binance holds that the engine has no record of is surfaced, in
  its own list, never merged into the managed rows and never dropped;
* the Close button follows the exchange, because a close against a flat
  position is a -2022 and a confusing snackbar.
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
    from src.execution import exchange_positions as xp
    xp.reset_for_test()
    yield
    position_state.reset_for_test()
    xp.reset_for_test()


class _Facade:
    def __init__(self, payload):
        self._payload = payload

    async def read_position_marks(self):
        return {"BTCUSDT": 110.0, "ETHUSDT": 2000.0, "__stamped_at__": 1.0}

    async def read_exchange_positions(self):
        return self._payload


def _ex(symbol="BTCUSDT", amount=1.4, entry=100.0, is_open=True, **kw):
    row = {
        "symbol": symbol,
        "side": "LONG" if amount > 0 else ("SHORT" if amount < 0 else "FLAT"),
        "position_amount": amount,
        "entry_price": entry or None,
        "exchange_unrealized_pnl": 14.0,
        "liquidation_price": 82.5,
        "leverage": 10.0,
        "margin_type": "cross",
        "push_age_sec": 2.0,
        "flat_since_epoch": None,
        "is_open": is_open,
    }
    row.update(kw)
    return row


def _client(positions, payload, monkeypatch, uid="fb-o"):
    from src.api import auto_trade_status_routes
    from src.execution import mark_price_feed as _mpf

    position_state._db = MagicMock()
    monkeypatch.setattr(
        position_state, "list_positions_for_user", lambda u, **k: list(positions)
    )
    monkeypatch.setattr(_mpf, "get_instance", lambda: None)

    app = FastAPI()
    auto_trade_status_routes.register(
        app,
        auth=lambda: None,
        identity_dep=lambda: SimpleNamespace(firebase_uid=uid, user_id=7),
        get_engine=lambda: _Facade(payload),
    )
    return TestClient(app)


def _position(**kw):
    base = dict(
        signal_id="sig-1", firebase_uid="fb-o", symbol="BTCUSDT", side="LONG",
        state=position_state.PositionState.OPEN, entry_price_target=99.0,
        entry_price_filled=100.0, sl_price=95.0, tp1_price=110.0,
        tp2_price=115.0, tp3_price=120.0, total_qty=2.0, tp1_qty=0.6,
        tp2_qty=0.8, tp3_qty=0.6, filled_qty=2.0, created_at=NOW,
    )
    base.update(kw)
    return position_state.Position(**base)


def _body(client):
    return client.get("/api/auto-trade/positions").json()


# ---------------------------------------------------------------------------
# The exchange answers first
# ---------------------------------------------------------------------------


def test_size_and_entry_come_from_the_exchange_and_say_so(monkeypatch):
    """The engine's document says total_qty 2.0; Binance says 1.4 is actually
    on the account.  Rendering 2.0 overstates what the user is holding — and
    a reader cannot check a number whose origin is invisible."""
    payload = {"users": {"fb-o": {"BTCUSDT": _ex(amount=1.4, entry=101.5)}},
               "stamped_at": 1.0}
    row = _body(_client([_position()], payload, monkeypatch))["positions"][0]

    assert row["open_qty"] == 1.4
    assert row["qty_source"] == "exchange"
    assert row["entry_price"] == 101.5
    assert row["entry_source"] == "exchange"


def test_the_exchanges_own_columns_are_carried(monkeypatch):
    """Liquidation price and leverage exist NOWHERE except positionRisk — the
    push does not carry them — and that response was being fetched every
    cycle and thrown away."""
    payload = {"users": {"fb-o": {"BTCUSDT": _ex()}}, "stamped_at": 1.0}
    row = _body(_client([_position()], payload, monkeypatch))["positions"][0]

    assert row["liquidation_price"] == 82.5
    assert row["leverage"] == 10.0
    assert row["margin_type"] == "cross"
    assert row["exchange_push_age_sec"] == 2.0


def test_the_engine_answers_only_when_the_exchange_has_not(monkeypatch):
    """An engine that predates the index, or a user whose worker is not
    running.  The row still renders — the position is real — and says the
    engine supplied it."""
    body = _body(_client([_position()], None, monkeypatch))
    row = body["positions"][0]

    assert row["qty_source"] == "engine"
    assert row["entry_source"] == "engine"
    assert row["open_qty"] == 2.0
    assert row["liquidation_price"] is None
    # The state rides the ENVELOPE, not the row: it describes the read rather
    # than any one position.
    assert body["exchange_state"] == "unavailable"


# ---------------------------------------------------------------------------
# Three states, never two
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "payload,expected",
    [
        (None, "unavailable"),
        ({"users": {}, "stamped_at": 1.0}, "not_reported"),
        ({"users": {"fb-o": {}}, "stamped_at": 1.0}, "reporting"),
    ],
)
def test_an_empty_book_has_three_causes(payload, expected, monkeypatch):
    """"We could not ask", "the engine has never heard of this user" and "the
    engine is reporting and this account is flat" have three different next
    moves.  Collapsing them renders a cold engine as a flat account."""
    body = _body(_client([], payload, monkeypatch))
    assert body["exchange_state"] == expected


def test_a_silent_exchange_never_asserts_a_divergence(monkeypatch):
    """An engine that has said nothing is not evidence that a position
    closed.  Claiming otherwise is the alarming-caption failure: it sends the
    owner to debug a position that is fine."""
    row = _body(_client([_position()], None, monkeypatch))["positions"][0]
    assert row["divergence"] is None
    assert row["closeable"] is True


# ---------------------------------------------------------------------------
# The divergence the owner actually saw
# ---------------------------------------------------------------------------


def test_engine_open_over_an_exchange_that_is_flat_is_named(monkeypatch):
    """The two-hour backstop closes the position while the signal runs on.
    39 of 140 positions in the owner's window.  This is that state, named."""
    payload = {
        "users": {"fb-o": {"BTCUSDT": _ex(amount=0.0, is_open=False,
                                          flat_since_epoch=1_700_000_000.0)}},
        "stamped_at": 1.0,
    }
    row = _body(_client([_position()], payload, monkeypatch))["positions"][0]

    assert row["divergence"] == "exchange_flat"
    assert row["exchange_flat_since_epoch"] == 1_700_000_000.0
    # And the Close button is withheld: closing a flat position is a -2022.
    assert row["closeable"] is False


def test_a_reporting_exchange_with_no_row_for_the_symbol_is_named_apart(
    monkeypatch
):
    """Different from "flat": the exchange is reporting this account and has
    never mentioned this symbol at all.  Same blank on screen, different
    cause, different fix."""
    payload = {"users": {"fb-o": {"ETHUSDT": _ex(symbol="ETHUSDT")}},
               "stamped_at": 1.0}
    row = _body(_client([_position()], payload, monkeypatch))["positions"][0]
    assert row["divergence"] == "exchange_silent"


# ---------------------------------------------------------------------------
# Positions the engine does not manage
# ---------------------------------------------------------------------------


def test_a_position_binance_holds_that_the_engine_does_not_know_is_surfaced(
    monkeypatch
):
    """The most important thing this endpoint can say, and it was invisible on
    every surface we have."""
    payload = {
        "users": {"fb-o": {
            "BTCUSDT": _ex(),
            "ETHUSDT": _ex(symbol="ETHUSDT", amount=-0.5, entry=2100.0),
        }},
        "stamped_at": 1.0,
    }
    body = _body(_client([_position()], payload, monkeypatch))

    assert [r["symbol"] for r in body["positions"]] == ["BTCUSDT"]
    assert len(body["unmanaged"]) == 1
    un = body["unmanaged"][0]
    assert un["symbol"] == "ETHUSDT"
    assert un["side"] == "SHORT"
    assert un["open_qty"] == 0.5
    # Signed toward the trade: a short is up when price falls.
    assert un["unrealized_pnl_pct"] > 0


def test_an_unmanaged_row_is_never_merged_into_the_managed_ones(monkeypatch):
    """They carry no signal, no stop and no target, so every field a managed
    row renders is absent.  One list would make the app render blanks it
    cannot explain."""
    payload = {"users": {"fb-o": {"ETHUSDT": _ex(symbol="ETHUSDT")}},
               "stamped_at": 1.0}
    body = _body(_client([], payload, monkeypatch))
    assert body["positions"] == []
    assert len(body["unmanaged"]) == 1
    assert "signal_id" not in body["unmanaged"][0]


def test_a_flat_exchange_row_is_not_an_unmanaged_position(monkeypatch):
    """The flat frame is retained so a card can say "Binance closed this".
    It is not a holding and must never be listed as one."""
    payload = {
        "users": {"fb-o": {"ETHUSDT": _ex(symbol="ETHUSDT", amount=0.0,
                                          is_open=False)}},
        "stamped_at": 1.0,
    }
    assert _body(_client([], payload, monkeypatch))["unmanaged"] == []
