"""The exchange's own picture of the account — the data that was already
arriving and being thrown away.

Owner, 2026-09-01: *"there we have to show exactly how live open traded
position shows in binance"*.

Two sources existed and neither had a reader:

* ``ACCOUNT_UPDATE`` — Binance PUSHING signed size, entry price, unrealized
  PnL, margin type on every change.  ``events.parse_event`` has decoded it
  into a typed dataclass since the user-data stream shipped; ``PositionFSM``
  no-ops it and its docstring pointed at the reconciler, which has never seen
  a stream event.
* ``positionRisk`` — the reconciler fetched the whole row every cycle and kept
  ``positionAmt``, discarding ``liquidationPrice`` and ``leverage``, which
  exist nowhere else at all.

So the first cut of the position card inferred a position the exchange was
describing for free.  What is pinned here is the reading, and mostly the
distinctions that would otherwise collapse into a plausible wrong number:

* the push wins over REST for the fields both carry, because it is fresher by
  construction and letting a ~5-minute snapshot overwrite a live size walks
  the number backwards;
* REST-only fields are applied unconditionally, since the push cannot supply
  them;
* freshness is per SOURCE, never one "as of" over two clocks;
* a FLAT frame is recorded, not dropped — it is the exchange saying "you are
  out", which is the fact the Trade tab could not distinguish from "nothing
  was ever placed";
* an absent reading is ``None``, never ``0.0``: a liquidation price of zero
  renders as "you cannot be liquidated";
* a hedge-mode frame is skipped rather than merged, and the whole-exchange
  flat rows in a positionRisk response are not recorded.
"""
from __future__ import annotations

import pytest

from src.execution import events as events_mod
from src.execution import exchange_positions as xp


@pytest.fixture(autouse=True)
def _reset():
    xp.reset_for_test()
    yield
    xp.reset_for_test()


def _account_update(*positions) -> events_mod.AccountUpdate:
    return events_mod.AccountUpdate(
        event_time_ms=0, transaction_time_ms=0, event_reason="ORDER",
        balances=[], positions=list(positions),
    )


def _frame(
    symbol="BTCUSDT", amount=0.5, entry=29000.0, upnl=12.5,
    realized=0.0, margin="cross", isolated=0.0, side="BOTH",
) -> events_mod.AccountUpdatePosition:
    return events_mod.AccountUpdatePosition(
        symbol=symbol, position_amount=amount, entry_price=entry,
        accumulated_realized_pnl=realized, unrealized_pnl=upnl,
        margin_type=margin, isolated_wallet=isolated, position_side=side,
    )


def _risk(symbol="BTCUSDT", amt="0.5", liq="24500.0", lev="10",
          mark="29180.0", entry="29000.0", notional="14590.0"):
    return {
        "symbol": symbol, "positionAmt": amt, "liquidationPrice": liq,
        "leverage": lev, "markPrice": mark, "entryPrice": entry,
        "notional": notional, "marginType": "cross",
    }


# ---------------------------------------------------------------------------
# The push
# ---------------------------------------------------------------------------


def test_the_exchange_push_is_recorded_with_its_own_numbers():
    xp.apply_account_update("fb-o", _account_update(_frame()))
    row = xp.for_user("fb-o")["BTCUSDT"]

    assert row["side"] == "LONG"
    assert row["position_amount"] == 0.5
    assert row["entry_price"] == 29000.0
    assert row["exchange_unrealized_pnl"] == 12.5
    assert row["is_open"] is True
    assert row["push_age_sec"] is not None
    # REST has not run: those fields are unknown, not zero.
    assert row["liquidation_price"] is None
    assert row["leverage"] is None
    assert row["rest_age_sec"] is None


def test_a_short_is_signed_not_guessed():
    xp.apply_account_update("fb-o", _account_update(_frame(amount=-0.5)))
    assert xp.for_user("fb-o")["BTCUSDT"]["side"] == "SHORT"


def test_going_flat_is_recorded_as_a_fact_not_a_deletion():
    """The most useful frame this module receives: the exchange saying "you
    are out".  Dropping it renders the same blank as "nothing was ever
    placed", which is exactly the confusion the Trade tab had."""
    xp.apply_account_update("fb-o", _account_update(_frame()))
    xp.apply_account_update(
        "fb-o", _account_update(_frame(amount=0.0, upnl=0.0, realized=3.2))
    )
    row = xp.for_user("fb-o")["BTCUSDT"]

    assert row["is_open"] is False
    assert row["side"] == "FLAT"
    assert row["flat_since_epoch"] is not None
    assert row["accumulated_realized_pnl"] == 3.2
    assert xp.counters()["went_flat"] == 1


def test_a_balance_only_update_asserts_nothing_about_positions():
    """Funding and deposits arrive with no position frames.  Reading that as
    "the account is flat" would close every card on a funding tick."""
    xp.apply_account_update("fb-o", _account_update(_frame()))
    xp.apply_account_update("fb-o", _account_update())  # no frames
    assert xp.for_user("fb-o")["BTCUSDT"]["is_open"] is True


def test_a_hedge_mode_frame_is_skipped_rather_than_merged():
    """This engine trades one-way only.  LONG and SHORT rows for one symbol
    would overwrite each other under a single key and produce a size that is
    neither."""
    xp.apply_account_update(
        "fb-o", _account_update(_frame(side="LONG", amount=0.5))
    )
    assert xp.for_user("fb-o") == {}
    assert xp.counters()["position_frames"] == 0


# ---------------------------------------------------------------------------
# The REST row
# ---------------------------------------------------------------------------


def test_positionrisk_supplies_what_the_push_cannot():
    xp.apply_position_risk("fb-o", [_risk()])
    row = xp.for_user("fb-o")["BTCUSDT"]

    assert row["liquidation_price"] == 24500.0
    assert row["leverage"] == 10.0
    assert row["mark_price_rest"] == 29180.0
    assert row["rest_age_sec"] is not None
    # No push has landed, so Binance's own uPnL is unknown rather than 0.0.
    assert row["exchange_unrealized_pnl"] is None


def test_a_stale_rest_snapshot_never_overwrites_a_live_push():
    """positionRisk is up to a reconciler cycle old.  Letting it write size
    and entry over a push that landed a second ago walks a live number
    backwards — the position would shrink on screen and then grow again."""
    xp.apply_account_update("fb-o", _account_update(_frame(amount=0.9)))
    xp.apply_position_risk("fb-o", [_risk(amt="0.5")])
    row = xp.for_user("fb-o")["BTCUSDT"]

    assert row["position_amount"] == 0.9        # the push held
    assert row["liquidation_price"] == 24500.0  # REST-only field still applied


def test_the_exchanges_flat_rows_are_not_recorded():
    """positionRisk returns a row for every symbol on the account, nearly all
    flat.  Recording them would grow this map to the size of the exchange for
    no reader."""
    xp.apply_position_risk(
        "fb-o",
        [_risk(symbol="BTCUSDT", amt="0.5"),
         _risk(symbol="ETHUSDT", amt="0"),
         _risk(symbol="SOLUSDT", amt="0")],
    )
    assert list(xp.for_user("fb-o")) == ["BTCUSDT"]


# ---------------------------------------------------------------------------
# Freshness and lifetime
# ---------------------------------------------------------------------------


def test_freshness_is_per_source_and_never_pooled():
    """A single "as of" over two clocks is the defect /signals/sar-live and
    /truth each paid for.  A card cannot grade freshness it did not measure."""
    xp.apply_account_update("fb-o", _account_update(_frame()))
    row = xp.for_user("fb-o")["BTCUSDT"]
    assert row["push_age_sec"] is not None
    assert row["rest_age_sec"] is None

    xp.apply_position_risk("fb-o", [_risk()])
    row = xp.for_user("fb-o")["BTCUSDT"]
    assert row["push_age_sec"] is not None
    assert row["rest_age_sec"] is not None


def test_an_untracked_user_is_empty_not_flat():
    """Empty means "this process has heard nothing about this user" — before
    the first frame, after a restart, or with no worker running.  It is not
    the account being flat, and a reader that cannot tell those apart reads a
    cold engine as a closed position."""
    assert xp.for_user("nobody") == {}


def test_forgetting_a_user_drops_their_book():
    xp.apply_account_update("fb-o", _account_update(_frame()))
    assert xp.tracked_users() == 1
    xp.forget_user("fb-o")
    assert xp.for_user("fb-o") == {}
    assert xp.tracked_users() == 0


def test_a_flat_row_ages_out_but_an_open_one_never_does(monkeypatch):
    """The retain window bounds memory; an OPEN position is never evicted
    however long it is held."""
    # Born flat: the ordinary case after a restart, where the position closed
    # while the engine was down and the first frame we ever see is a zero.
    # Stamping flat_since only on an open->flat TRANSITION left this row
    # unevictable forever, which is a retain window a whole class of rows
    # never enters.
    xp.apply_account_update("fb-o", _account_update(_frame(amount=0.0)))
    assert xp.for_user("fb-o")["BTCUSDT"]["flat_since_epoch"] is not None
    xp.apply_account_update(
        "fb-o", _account_update(_frame(symbol="ETHUSDT", amount=1.0))
    )
    xp._positions["fb-o"]["BTCUSDT"].flat_since = 0.0  # past the window
    xp.apply_account_update(
        "fb-o", _account_update(_frame(symbol="ETHUSDT", amount=1.0))
    )
    assert "BTCUSDT" not in xp.for_user("fb-o")
    assert "ETHUSDT" in xp.for_user("fb-o")


def test_the_generation_advances_so_a_reader_can_skip_unchanged_work():
    g0 = xp.get_generation()
    xp.apply_account_update("fb-o", _account_update(_frame()))
    assert xp.get_generation() > g0


def test_a_malformed_frame_never_raises_into_the_socket():
    """This rides the same stream that drives the FSM. A bad frame must not
    cost a fill event."""
    xp.apply_account_update("fb-o", object())  # not an AccountUpdate at all
    assert xp.for_user("fb-o") == {}
