"""Tests for src.execution.events.

Pure-Python parser — no IO, no mocks needed.  Pins the Binance wire-
format → typed-dataclass mapping that the FSM (PR-6) + reconciler
(PR-9) will lean on.

What we pin:

* Each known event type parses into the correct dataclass.
* Two-letter Binance field names (``s``, ``S``, ``X``, ...) translate
  to readable Python attribute names — typos in the translation table
  would be silent corruption far from the bug.
* Numeric string fields (Binance's precision-preserving wire format)
  parse to float; empty / missing fields default to 0.0.
* Unknown event types raise :class:`UnknownEventType` — consumer
  catches + skips.
* Critical FSM fields on ORDER_TRADE_UPDATE are extracted correctly:
  ``order_status``, ``execution_type``, ``reduce_only``,
  ``client_order_id``, ``last_filled_qty``, ``last_filled_price``.
"""
from __future__ import annotations

import pytest

from src.execution import events


# ---------------------------------------------------------------------------
# Realistic ORDER_TRADE_UPDATE sample (per Binance docs)
# ---------------------------------------------------------------------------


_OTU_SAMPLE = {
    "e": "ORDER_TRADE_UPDATE",
    "E": 1568879465651,
    "T": 1568879465650,
    "o": {
        "s": "BTCUSDT",
        "c": "signal_xyz_entry",
        "S": "BUY",
        "o": "MARKET",
        "f": "GTC",
        "q": "1.000",
        "p": "0",
        "ap": "29200.5",
        "sp": "0",
        "x": "TRADE",
        "X": "FILLED",
        "i": 123456,
        "l": "1.000",
        "z": "1.000",
        "L": "29200.5",
        "n": "0.029",
        "N": "USDT",
        "T": 1568879465650,
        "t": 789,
        "b": "0",
        "a": "0",
        "m": False,
        "R": False,
        "wt": "CONTRACT_PRICE",
        "ot": "MARKET",
        "ps": "BOTH",
        "cp": False,
        "AP": "0",
        "cr": "0",
        "rp": "0.5",
    },
}


def test_order_trade_update_parses_critical_fsm_fields() -> None:
    """The FSM lives on these fields — verify every one maps correctly."""
    event = events.parse_event(_OTU_SAMPLE)
    assert isinstance(event, events.OrderTradeUpdate)
    assert event.symbol == "BTCUSDT"
    assert event.client_order_id == "signal_xyz_entry"
    assert event.side == "BUY"
    assert event.order_type == "MARKET"
    assert event.execution_type == "TRADE"
    assert event.order_status == "FILLED"
    assert event.reduce_only is False
    assert event.order_id == 123456
    assert event.last_filled_qty == 1.0
    assert event.cumulative_filled_qty == 1.0
    assert event.last_filled_price == 29200.5
    assert event.average_price == 29200.5
    assert event.commission == 0.029
    assert event.commission_asset == "USDT"
    assert event.trade_time_ms == 1568879465650
    assert event.is_maker is False
    assert event.realized_pnl == 0.5


def test_reduce_only_pretp_partial_close_parses() -> None:
    """Pre-TP partial close orders are placed with reduceOnly=true.
    The FSM uses this flag to distinguish 'pre-TP just fired' from
    'a separate take-profit hit'."""
    msg = {**_OTU_SAMPLE, "o": {**_OTU_SAMPLE["o"], "R": True}}
    event = events.parse_event(msg)
    assert isinstance(event, events.OrderTradeUpdate)
    assert event.reduce_only is True


def test_partial_fill_parses_correctly() -> None:
    """PARTIALLY_FILLED is the state the FSM enters when an entry
    order partially fills.  ``last_filled_qty`` < ``original_qty``
    distinguishes from FILLED."""
    msg = {
        **_OTU_SAMPLE,
        "o": {
            **_OTU_SAMPLE["o"],
            "X": "PARTIALLY_FILLED",
            "l": "0.3",
            "z": "0.3",
            "q": "1.000",
        },
    }
    event = events.parse_event(msg)
    assert isinstance(event, events.OrderTradeUpdate)
    assert event.order_status == "PARTIALLY_FILLED"
    assert event.last_filled_qty == 0.3
    assert event.cumulative_filled_qty == 0.3
    assert event.original_qty == 1.0


# ---------------------------------------------------------------------------
# Numeric-string-to-float handling — Binance's precision convention
# ---------------------------------------------------------------------------


def test_empty_numeric_fields_default_to_zero() -> None:
    """Binance sends ``""`` for unused numeric fields (e.g. ``sp`` for
    a MARKET order).  Default to 0.0 rather than raising — caller
    interprets 0 as 'unset' for these optional fields."""
    msg = {
        "e": "ORDER_TRADE_UPDATE",
        "E": 0,
        "o": {
            "s": "BTCUSDT",
            "X": "NEW",
            "q": "",
            "p": "",
            "sp": "",
        },
    }
    event = events.parse_event(msg)
    assert isinstance(event, events.OrderTradeUpdate)
    assert event.original_qty == 0.0
    assert event.original_price == 0.0
    assert event.stop_price == 0.0


def test_missing_numeric_fields_default_to_zero() -> None:
    """Fields absent entirely default to 0.0 — defence against Binance
    silently dropping a field in a future API revision."""
    msg = {"e": "ORDER_TRADE_UPDATE", "o": {"s": "BTCUSDT", "X": "NEW"}}
    event = events.parse_event(msg)
    assert isinstance(event, events.OrderTradeUpdate)
    assert event.original_qty == 0.0
    assert event.realized_pnl == 0.0


# ---------------------------------------------------------------------------
# ACCOUNT_UPDATE — for reconciliation in PR-9
# ---------------------------------------------------------------------------


def test_account_update_parses_balances_and_positions() -> None:
    msg = {
        "e": "ACCOUNT_UPDATE",
        "E": 1564745798939,
        "T": 1564745798938,
        "a": {
            "m": "ORDER",
            "B": [
                {"a": "USDT", "wb": "122624.0", "cw": "100.0", "bc": "0.1"},
            ],
            "P": [
                {
                    "s": "BTCUSDT",
                    "pa": "20",
                    "ep": "27499.5",
                    "cr": "-1.2",
                    "up": "30.5",
                    "mt": "isolated",
                    "iw": "500.0",
                    "ps": "LONG",
                },
            ],
        },
    }
    event = events.parse_event(msg)
    assert isinstance(event, events.AccountUpdate)
    assert event.event_reason == "ORDER"
    assert len(event.balances) == 1
    assert event.balances[0].asset == "USDT"
    assert event.balances[0].wallet_balance == 122624.0
    assert len(event.positions) == 1
    pos = event.positions[0]
    assert pos.symbol == "BTCUSDT"
    assert pos.position_amount == 20.0  # signed; +20 = LONG
    assert pos.entry_price == 27499.5
    assert pos.unrealized_pnl == 30.5
    assert pos.margin_type == "isolated"
    assert pos.position_side == "LONG"


def test_account_update_negative_position_amount_means_short() -> None:
    """Binance uses signed quantity in position updates: positive =
    LONG, negative = SHORT.  Verify parser preserves sign so the
    FSM can directionally classify."""
    msg = {
        "e": "ACCOUNT_UPDATE",
        "E": 0,
        "T": 0,
        "a": {
            "m": "ORDER",
            "B": [],
            "P": [{"s": "BTCUSDT", "pa": "-5.0", "ps": "SHORT"}],
        },
    }
    event = events.parse_event(msg)
    assert isinstance(event, events.AccountUpdate)
    assert event.positions[0].position_amount == -5.0


# ---------------------------------------------------------------------------
# MARGIN_CALL — anomaly trigger
# ---------------------------------------------------------------------------


def test_margin_call_parses_at_risk_positions() -> None:
    msg = {
        "e": "MARGIN_CALL",
        "E": 1587727187525,
        "cw": "3.16812045",
        "p": [
            {
                "s": "ETHUSDT",
                "ps": "LONG",
                "pa": "1.0",
                "mt": "CROSSED",
                "iw": "0.0",
                "mp": "200.5",
                "up": "-50.0",
                "mm": "20.0",
            },
        ],
    }
    event = events.parse_event(msg)
    assert isinstance(event, events.MarginCall)
    assert event.cross_wallet_balance == 3.16812045
    assert len(event.positions) == 1
    p = event.positions[0]
    assert p.symbol == "ETHUSDT"
    assert p.mark_price == 200.5
    assert p.maintenance_margin_required == 20.0


# ---------------------------------------------------------------------------
# listenKeyExpired — worker reconnect trigger
# ---------------------------------------------------------------------------


def test_listen_key_expired_parses() -> None:
    msg = {"e": "listenKeyExpired", "E": 1612847600000}
    event = events.parse_event(msg)
    assert isinstance(event, events.ListenKeyExpired)
    assert event.event_time_ms == 1612847600000


# ---------------------------------------------------------------------------
# Unknown event types — caller catches + skips
# ---------------------------------------------------------------------------


def test_unknown_event_type_raises_typed_exception() -> None:
    """Binance sends event types we don't care about (ACCOUNT_CONFIG_UPDATE,
    STRATEGY_UPDATE, etc.).  Consumer treats this as 'log + skip',
    so the parser raises a typed exception that's easy to catch."""
    msg = {"e": "ACCOUNT_CONFIG_UPDATE", "E": 0}
    with pytest.raises(events.UnknownEventType):
        events.parse_event(msg)


def test_missing_event_type_field_raises() -> None:
    """Messages without ``e`` are malformed — Binance would have to
    ship a breaking change to produce this; surface loudly."""
    with pytest.raises(events.UnknownEventType):
        events.parse_event({})
