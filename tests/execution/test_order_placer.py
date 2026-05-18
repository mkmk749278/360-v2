"""Tests for src.execution.order_placer.

The signing client is mocked at the OrderPlacer constructor.  What
we pin:

* Each verb (entry / SL / TP / cancel) sends the right Binance
  parameters: symbol, side, type, quantity, stopPrice, closePosition,
  reduceOnly, workingType, newClientOrderId.
* clientOrderId follows the lumin_<signal_id>_<phase> convention so
  the FSM can map fills back to phases via parse_coid.
* Direction → side mapping is correct: LONG entry = BUY,
  LONG exit (SL/TP) = SELL.  Inverted for SHORT.
* Each signing-service error code maps to the right typed
  OrderPlacementError subclass — caller (FSM) only needs to handle
  three exception types.
* cancel_order swallows -2011 "Unknown order sent" (order already
  filled/cancelled) — that's not a real error from the caller's POV.
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import order_placer
from src.execution import position_state
from src.security.signing_service import protocol as sig_protocol


def _ok_resp(body: Any) -> sig_protocol.SignResponse:
    return sig_protocol.SignResponse.ok_reply(
        "req-x", binance_status=200, binance_body=body
    )


def _err_resp(code: str, body: Any = None) -> sig_protocol.SignResponse:
    return sig_protocol.SignResponse.error_reply(
        "req-x",
        code=code,
        message="error",
        binance_status=400,
        binance_body=body,
    )


def _mock_client(post_response=None, delete_response=None) -> MagicMock:
    mock = MagicMock()
    mock.binance_signed_post = AsyncMock(
        return_value=post_response
        or _ok_resp(
            {
                "orderId": 1234567,
                "clientOrderId": "lumin_sig-1_entry",
                "status": "NEW",
                "avgPrice": "0",
            }
        )
    )
    mock.binance_signed_delete = AsyncMock(
        return_value=delete_response or _ok_resp({})
    )
    return mock


# ---------------------------------------------------------------------------
# place_market_entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_market_entry_long_sends_buy_side() -> None:
    """LONG → BUY for entry, SHORT → SELL.  Inversion mistake here
    would open positions on the wrong side — catastrophic."""
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_market_entry(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        quantity=0.5,
    )
    params = client.binance_signed_post.call_args.kwargs["params"]
    assert params["symbol"] == "BTCUSDT"
    assert params["side"] == "BUY"
    assert params["type"] == "MARKET"
    assert params["quantity"] == "0.5"
    assert params["newClientOrderId"] == position_state.coid_entry("sig-1")


@pytest.mark.asyncio
async def test_market_entry_short_sends_sell_side() -> None:
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_market_entry(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="SHORT",
        quantity=1.0,
    )
    assert (
        client.binance_signed_post.call_args.kwargs["params"]["side"]
        == "SELL"
    )


@pytest.mark.asyncio
async def test_market_entry_returns_parsed_result() -> None:
    """The orderId / clientOrderId / status come back as typed fields
    on OrderPlacementResult — FSM persists ``order_id`` directly to
    Firestore."""
    client = _mock_client(
        post_response=_ok_resp(
            {
                "orderId": 9876543,
                "clientOrderId": "lumin_sig-1_entry",
                "status": "FILLED",
                "avgPrice": "29005.5",
            }
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    result = await placer.place_market_entry(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        quantity=0.5,
    )
    assert result.order_id == 9876543
    assert result.status == "FILLED"
    assert result.avg_price == 29005.5


# ---------------------------------------------------------------------------
# place_stop_loss
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stop_loss_long_sends_sell_with_close_position() -> None:
    """LONG SL is a SELL STOP_MARKET with closePosition=true.
    workingType=MARK_PRICE (less wick-prone than CONTRACT_PRICE)."""
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_stop_loss(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        stop_price=28500.0,
    )
    params = client.binance_signed_post.call_args.kwargs["params"]
    assert params["side"] == "SELL"
    assert params["type"] == "STOP_MARKET"
    assert params["stopPrice"] == "28500"
    assert params["closePosition"] == "true"
    assert params["workingType"] == "MARK_PRICE"
    assert params["newClientOrderId"] == position_state.coid_sl("sig-1")


@pytest.mark.asyncio
async def test_stop_loss_short_sends_buy() -> None:
    """SHORT SL is a BUY STOP_MARKET."""
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_stop_loss(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="SHORT",
        stop_price=30000.0,
    )
    assert (
        client.binance_signed_post.call_args.kwargs["params"]["side"]
        == "BUY"
    )


@pytest.mark.asyncio
async def test_stop_loss_accepts_coid_override() -> None:
    """PR-7's BE shift will cancel the original SL + place a new one
    with a distinct clientOrderId (you can't reuse the original; it's
    associated with the cancelled order).  Verify the override is
    plumbed through."""
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_stop_loss(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        stop_price=29000.0,
        coid_override="lumin_sig-1_sl_be",
    )
    params = client.binance_signed_post.call_args.kwargs["params"]
    assert params["newClientOrderId"] == "lumin_sig-1_sl_be"


# ---------------------------------------------------------------------------
# place_take_profit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_take_profit_uses_reduce_only_and_explicit_quantity() -> None:
    """TPs are partial closes — reduceOnly prevents accidentally
    opening a reverse position if fill arithmetic is off."""
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_take_profit(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        stop_price=29500.0,
        quantity=0.3,
        tp_phase="tp1",
    )
    params = client.binance_signed_post.call_args.kwargs["params"]
    assert params["type"] == "TAKE_PROFIT_MARKET"
    assert params["side"] == "SELL"  # LONG exit
    assert params["quantity"] == "0.3"
    assert params["reduceOnly"] == "true"
    assert params["newClientOrderId"] == position_state.coid_tp1("sig-1")


@pytest.mark.asyncio
async def test_take_profit_phase_routes_to_correct_coid() -> None:
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_take_profit(
        signal_id="sig-X",
        symbol="ETHUSDT",
        direction="LONG",
        stop_price=2000.0,
        quantity=0.1,
        tp_phase="tp2",
    )
    assert (
        client.binance_signed_post.call_args.kwargs["params"][
            "newClientOrderId"
        ]
        == position_state.coid_tp2("sig-X")
    )


@pytest.mark.asyncio
async def test_take_profit_rejects_unknown_phase() -> None:
    client = _mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    with pytest.raises(ValueError):
        await placer.place_take_profit(
            signal_id="sig-1",
            symbol="BTCUSDT",
            direction="LONG",
            stop_price=29500.0,
            quantity=0.3,
            tp_phase="tp99",
        )


# ---------------------------------------------------------------------------
# Error-code → typed-exception mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "error_code, expected_cls",
    [
        (
            sig_protocol.ERR_KEY_BLOB_NOT_FOUND,
            order_placer.OrderPlacementKeyError,
        ),
        (
            sig_protocol.ERR_CRYPTO_DECRYPT_FAILED,
            order_placer.OrderPlacementKeyError,
        ),
        (
            sig_protocol.ERR_BINANCE_UNREACHABLE,
            order_placer.OrderPlacementUnreachable,
        ),
        (
            sig_protocol.ERR_KMS_DECRYPT_FAILED,
            order_placer.OrderPlacementUnreachable,
        ),
        (
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            order_placer.OrderRejectedByBinance,
        ),
        (
            sig_protocol.ERR_BAD_REQUEST,
            order_placer.OrderPlacementError,
        ),
    ],
)
@pytest.mark.asyncio
async def test_signing_error_maps_to_typed_exception(
    error_code, expected_cls
) -> None:
    """Pin the error-code → exception-class table so the FSM's
    catch chain stays minimal (3 exception types instead of 7
    error code constants)."""
    client = _mock_client(post_response=_err_resp(error_code))
    placer = order_placer.OrderPlacer("fb-x", client=client)
    with pytest.raises(expected_cls):
        await placer.place_market_entry(
            signal_id="sig-1",
            symbol="BTCUSDT",
            direction="LONG",
            quantity=0.5,
        )


# ---------------------------------------------------------------------------
# cancel_order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_order_swallows_unknown_order() -> None:
    """Binance -2011 = "Unknown order sent" — typically means the
    order was already filled or cancelled.  We wanted it gone; it's
    gone.  Treat as success rather than fail."""
    client = _mock_client(
        delete_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -2011, "msg": "Unknown order sent"},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    # Must not raise.
    await placer.cancel_order(symbol="BTCUSDT", order_id=999)


@pytest.mark.asyncio
async def test_cancel_order_raises_on_other_failures() -> None:
    """Non-(-2011) failures DO raise — caller may want to retry or
    Telegram-alert."""
    client = _mock_client(
        delete_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -1021, "msg": "Timestamp out of recvWindow"},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    with pytest.raises(order_placer.OrderRejectedByBinance):
        await placer.cancel_order(symbol="BTCUSDT", order_id=999)
