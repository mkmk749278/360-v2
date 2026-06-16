"""Typed event dataclasses for Binance Futures User Data Stream messages.

The User Data Stream WS sends compact JSON messages with a top-level
``e`` field indicating the event type.  The four types Lumin cares
about for the Position FSM (PR-6) + reconciliation (PR-9):

* ``ORDER_TRADE_UPDATE`` — fired on every order state change.  This
  is THE event the FSM lives on: it tells us when entry filled,
  when SL/TP filled, when a partial fill happened (pre-TP), when
  an order was cancelled.
* ``ACCOUNT_UPDATE`` — fires on balance / position change.  Used by
  reconciliation to verify our FSM's view of the position size
  matches what Binance actually shows.
* ``MARGIN_CALL`` — fires when margin is dangerously low.  Logged +
  Telegram-alerted; PR-8 anomaly tripwire will auto-disable the
  user on this.
* ``listenKeyExpired`` — fires if our listenKey expires (we missed
  too many keepalives).  We close + reconnect with a fresh key.

Reference: https://binance-docs.github.io/apidocs/futures/en/#user-data-streams

Wire format note: Binance uses two-letter abbreviated field names
on the wire (``s`` for symbol, ``x`` for order status, etc.) for
bandwidth efficiency.  This module is the ONE place we translate
those into readable Python attribute names — every other consumer
should work in terms of the typed dataclasses below, not raw dicts.

Stability contract: every dataclass field is a primitive or a list/dict
of primitives.  Adding a new field is backward-compatible; renaming
or removing a field is a breaking change for downstream consumers
(PR-6's FSM + PR-9's reconciler).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Union


# ---------------------------------------------------------------------------
# ORDER_TRADE_UPDATE — the FSM's primary event
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OrderTradeUpdate:
    """One Binance ORDER_TRADE_UPDATE event, parsed into readable names.

    The most important fields for the FSM:

    * ``order_status`` — NEW / PARTIALLY_FILLED / FILLED / CANCELED /
      EXPIRED / REJECTED.  FSM transitions on FILLED.
    * ``execution_type`` — NEW / TRADE / CANCELED / EXPIRED / TRAILING_STOP_UPDATE.
      TRADE means a fill happened (full or partial); the ``last_filled_qty``
      tells us how much.
    * ``symbol`` — for the symbol allowlist check in PR-8.
    * ``side`` — BUY / SELL.
    * ``order_type`` — MARKET / LIMIT / STOP_MARKET / TAKE_PROFIT_MARKET / etc.
    * ``reduce_only`` — true for pre-TP partial-close orders.  FSM
      uses this to distinguish "TP1 filled" from "user manually placed
      a partial close."
    * ``client_order_id`` — Lumin sets this at order placement (PR-6)
      to a deterministic ``signal_<id>_<phase>`` string so we can map
      fills back to the originating signal regardless of Binance's
      ``order_id`` randomness.
    """

    symbol: str
    client_order_id: str
    side: str  # "BUY" | "SELL"
    order_type: str  # "MARKET" | "LIMIT" | "STOP_MARKET" | "TAKE_PROFIT_MARKET" | ...
    time_in_force: str  # "GTC" | "IOC" | "FOK" | ...
    original_qty: float
    original_price: float
    average_price: float
    stop_price: float
    execution_type: str  # "NEW" | "TRADE" | "CANCELED" | ...
    order_status: str  # "NEW" | "PARTIALLY_FILLED" | "FILLED" | "CANCELED" | ...
    order_id: int
    last_filled_qty: float
    cumulative_filled_qty: float
    last_filled_price: float
    commission: float
    commission_asset: str
    trade_time_ms: int
    trade_id: int
    bids_notional: float
    asks_notional: float
    is_maker: bool
    reduce_only: bool
    working_type: str  # "MARK_PRICE" | "CONTRACT_PRICE" — for STOP orders
    original_order_type: str
    position_side: str  # "BOTH" | "LONG" | "SHORT" (one-way vs hedge mode)
    close_position: bool
    activation_price: float
    callback_rate: float
    realized_pnl: float


# ---------------------------------------------------------------------------
# ACCOUNT_UPDATE — for reconciliation
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AccountUpdateBalance:
    asset: str
    wallet_balance: float
    cross_wallet_balance: float
    balance_change: float


@dataclass(frozen=True)
class AccountUpdatePosition:
    symbol: str
    position_amount: float  # signed: positive = LONG, negative = SHORT, 0 = flat
    entry_price: float
    accumulated_realized_pnl: float
    unrealized_pnl: float
    margin_type: str  # "isolated" | "cross"
    isolated_wallet: float
    position_side: str  # "BOTH" | "LONG" | "SHORT"


@dataclass(frozen=True)
class AccountUpdate:
    event_time_ms: int
    transaction_time_ms: int
    event_reason: str  # "ORDER" | "FUNDING_FEE" | "WITHDRAW" | "DEPOSIT" | ...
    balances: List[AccountUpdateBalance]
    positions: List[AccountUpdatePosition]


# ---------------------------------------------------------------------------
# MARGIN_CALL — risk warning
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MarginCallPosition:
    symbol: str
    position_side: str
    position_amount: float
    margin_type: str
    isolated_wallet: float
    mark_price: float
    unrealized_pnl: float
    maintenance_margin_required: float


@dataclass(frozen=True)
class MarginCall:
    event_time_ms: int
    cross_wallet_balance: float
    positions: List[MarginCallPosition]


# ---------------------------------------------------------------------------
# listenKeyExpired
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ListenKeyExpired:
    event_time_ms: int


# ---------------------------------------------------------------------------
# Discriminated-union type for the parser output
# ---------------------------------------------------------------------------


Event = Union[OrderTradeUpdate, AccountUpdate, MarginCall, ListenKeyExpired]


# ---------------------------------------------------------------------------
# Parser — single entry point that maps a raw dict to a typed event
# ---------------------------------------------------------------------------


class UnknownEventType(Exception):
    """Raised when ``e`` doesn't match any event type we handle.

    Production should LOG and SKIP (the WS sends event types we don't
    care about — e.g. ``ACCOUNT_CONFIG_UPDATE`` — alongside the ones
    we do).  Test code asserts on this to verify the parser doesn't
    silently accept garbage."""


def parse_event(message: Dict[str, Any]) -> Event:
    """Parse a raw Binance User Data Stream message into a typed event.

    Raises :class:`UnknownEventType` if ``e`` doesn't match a known
    event type.  Caller catches this + logs + continues — Binance
    sends event types we don't subscribe to (ACCOUNT_CONFIG_UPDATE,
    STRATEGY_UPDATE, etc.) alongside the ones we do.

    Raises :class:`ValueError` on malformed payloads (missing required
    fields, wrong types) — that's a wire-format breach Binance would
    have to ship, treat as a bug.
    """
    event_type = message.get("e")
    if event_type == "ORDER_TRADE_UPDATE":
        return _parse_order_trade_update(message)
    if event_type == "ACCOUNT_UPDATE":
        return _parse_account_update(message)
    if event_type == "MARGIN_CALL":
        return _parse_margin_call(message)
    if event_type == "listenKeyExpired":
        return _parse_listen_key_expired(message)
    raise UnknownEventType(f"unknown User Data Stream event type: {event_type!r}")


def _f(d: Dict[str, Any], key: str, default: float = 0.0) -> float:
    """Pull a numeric field that Binance encodes as a string.  Empty /
    missing values default to 0.0.  Used everywhere because Binance
    sends prices + quantities as strings to preserve precision."""
    raw = d.get(key)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def _parse_order_trade_update(message: Dict[str, Any]) -> OrderTradeUpdate:
    o = message.get("o") or {}
    return OrderTradeUpdate(
        symbol=str(o.get("s", "")),
        client_order_id=str(o.get("c", "")),
        side=str(o.get("S", "")),
        order_type=str(o.get("o", "")),
        time_in_force=str(o.get("f", "")),
        original_qty=_f(o, "q"),
        original_price=_f(o, "p"),
        average_price=_f(o, "ap"),
        stop_price=_f(o, "sp"),
        execution_type=str(o.get("x", "")),
        order_status=str(o.get("X", "")),
        order_id=int(o.get("i", 0)),
        last_filled_qty=_f(o, "l"),
        cumulative_filled_qty=_f(o, "z"),
        last_filled_price=_f(o, "L"),
        commission=_f(o, "n"),
        commission_asset=str(o.get("N", "")),
        trade_time_ms=int(o.get("T", 0)),
        trade_id=int(o.get("t", 0)),
        bids_notional=_f(o, "b"),
        asks_notional=_f(o, "a"),
        is_maker=bool(o.get("m", False)),
        reduce_only=bool(o.get("R", False)),
        working_type=str(o.get("wt", "")),
        original_order_type=str(o.get("ot", "")),
        position_side=str(o.get("ps", "")),
        close_position=bool(o.get("cp", False)),
        activation_price=_f(o, "AP"),
        callback_rate=_f(o, "cr"),
        realized_pnl=_f(o, "rp"),
    )


def _parse_account_update(message: Dict[str, Any]) -> AccountUpdate:
    a = message.get("a") or {}
    balances_raw = a.get("B") or []
    positions_raw = a.get("P") or []
    return AccountUpdate(
        event_time_ms=int(message.get("E", 0)),
        transaction_time_ms=int(message.get("T", 0)),
        event_reason=str(a.get("m", "")),
        balances=[
            AccountUpdateBalance(
                asset=str(b.get("a", "")),
                wallet_balance=_f(b, "wb"),
                cross_wallet_balance=_f(b, "cw"),
                balance_change=_f(b, "bc"),
            )
            for b in balances_raw
        ],
        positions=[
            AccountUpdatePosition(
                symbol=str(p.get("s", "")),
                position_amount=_f(p, "pa"),
                entry_price=_f(p, "ep"),
                accumulated_realized_pnl=_f(p, "cr"),
                unrealized_pnl=_f(p, "up"),
                margin_type=str(p.get("mt", "")),
                isolated_wallet=_f(p, "iw"),
                position_side=str(p.get("ps", "")),
            )
            for p in positions_raw
        ],
    )


def _parse_margin_call(message: Dict[str, Any]) -> MarginCall:
    positions_raw = message.get("p") or []
    return MarginCall(
        event_time_ms=int(message.get("E", 0)),
        cross_wallet_balance=_f(message, "cw"),
        positions=[
            MarginCallPosition(
                symbol=str(p.get("s", "")),
                position_side=str(p.get("ps", "")),
                position_amount=_f(p, "pa"),
                margin_type=str(p.get("mt", "")),
                isolated_wallet=_f(p, "iw"),
                mark_price=_f(p, "mp"),
                unrealized_pnl=_f(p, "up"),
                maintenance_margin_required=_f(p, "mm"),
            )
            for p in positions_raw
        ],
    )


def _parse_listen_key_expired(message: Dict[str, Any]) -> ListenKeyExpired:
    return ListenKeyExpired(event_time_ms=int(message.get("E", 0)))
