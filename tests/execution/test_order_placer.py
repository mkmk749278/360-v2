"""Tests for src.execution.order_placer.

The signing client is mocked at the OrderPlacer constructor.  What
we pin:

* Each verb (entry / SL / TP / cancel) sends the right Binance
  parameters: symbol, side, algoType/type, quantity, triggerPrice,
  closePosition, reduceOnly, workingType, clientAlgoId/newClientOrderId.
* Entry/close/pretp orders use /fapi/v1/order with newClientOrderId.
* SL and TP orders use /fapi/v1/algoOrder with algoType=CONDITIONAL
  and clientAlgoId (Binance mandatory migration, Dec 9 2025).
* clientAlgoId follows the lumin_<signal_id>_<phase> convention so
  the FSM can map fills back to phases via parse_coid.
* Direction → side mapping is correct: LONG entry = BUY,
  LONG exit (SL/TP) = SELL.  Inverted for SHORT.
* Each signing-service error code maps to the right typed
  OrderPlacementError subclass — caller (FSM) only needs to handle
  three exception types.
* cancel_order swallows -2011 "Unknown order sent" (order already
  filled/cancelled) — that's not a real error from the caller's POV.
* cancel_algo_order swallows -2011 and -20121 (algo order already gone).
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
    """Mock client returning a regular order response (for MARKET/LIMIT orders)."""
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


def _algo_mock_client(post_response=None, delete_response=None) -> MagicMock:
    """Mock client returning an algoOrder response (for SL / TP orders)."""
    mock = MagicMock()
    mock.binance_signed_post = AsyncMock(
        return_value=post_response
        or _ok_resp(
            {
                "algoId": 7654321,
                "clientAlgoId": "lumin_sig-1_sl",
                "success": True,
                "code": 0,
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
    """LONG SL is a SELL CONDITIONAL algoOrder with closePosition=true.
    workingType=MARK_PRICE (less wick-prone than CONTRACT_PRICE).
    Uses /fapi/v1/algoOrder with algoType=CONDITIONAL per the Binance
    mandatory migration effective Dec 9 2025."""
    client = _algo_mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_stop_loss(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        stop_price=28500.0,
    )
    params = client.binance_signed_post.call_args.kwargs["params"]
    assert params["side"] == "SELL"
    assert params["algoType"] == "CONDITIONAL"
    # The algo endpoint requires BOTH algoType AND type — omitting type
    # returns -1102 "Mandatory parameter 'type' was not sent".
    assert params["type"] == "STOP_MARKET"
    # The algo endpoint names the trigger level ``triggerPrice`` — NOT
    # ``stopPrice`` (the legacy /fapi/v1/order name).  Sending stopPrice
    # here returns -1102 "Mandatory parameter 'triggerprice' was not sent".
    assert params["triggerPrice"] == "28500"
    assert "stopPrice" not in params
    assert params["closePosition"] == "true"
    assert params["workingType"] == "MARK_PRICE"
    assert params["clientAlgoId"] == position_state.coid_sl("sig-1")
    assert "newClientOrderId" not in params
    # Posts to the algo endpoint, not the legacy order endpoint.
    assert client.binance_signed_post.call_args.kwargs["path"] == "/fapi/v1/algoOrder"


@pytest.mark.asyncio
async def test_stop_loss_short_sends_buy() -> None:
    """SHORT SL is a BUY CONDITIONAL algoOrder."""
    client = _algo_mock_client()
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
async def test_stop_loss_returns_algo_id_as_order_id() -> None:
    """algoId from the response is surfaced as order_id so callers
    can store it and pass to cancel_algo_order."""
    client = _algo_mock_client(
        post_response=_ok_resp({"algoId": 99001, "clientAlgoId": "lumin_sig-1_sl"})
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    result = await placer.place_stop_loss(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        stop_price=28500.0,
    )
    assert result.order_id == 99001
    assert result.client_order_id == "lumin_sig-1_sl"


@pytest.mark.asyncio
async def test_stop_loss_accepts_coid_override() -> None:
    """BE shift will cancel the original SL + place a new one
    with a distinct clientAlgoId.  Verify the override is plumbed through."""
    client = _algo_mock_client()
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.place_stop_loss(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        stop_price=29000.0,
        coid_override="lumin_sig-1_sl_be",
    )
    params = client.binance_signed_post.call_args.kwargs["params"]
    assert params["clientAlgoId"] == "lumin_sig-1_sl_be"
    assert "newClientOrderId" not in params


# ---------------------------------------------------------------------------
# place_take_profit
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_take_profit_uses_reduce_only_and_explicit_quantity() -> None:
    """TPs are partial closes — reduceOnly prevents accidentally opening
    a reverse position if fill arithmetic is off.  Uses algoType=CONDITIONAL
    on /fapi/v1/algoOrder per the Binance mandatory migration Dec 9 2025."""
    client = _algo_mock_client()
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
    assert params["algoType"] == "CONDITIONAL"
    # The algo endpoint requires BOTH algoType AND type (-1102 otherwise).
    assert params["type"] == "TAKE_PROFIT_MARKET"
    assert params["side"] == "SELL"  # LONG exit
    assert params["quantity"] == "0.3"
    assert params["reduceOnly"] == "true"
    # Trigger level is triggerPrice, not stopPrice — see place_stop_loss
    # test for the -1102 rationale.
    assert params["triggerPrice"] == "29500"
    assert "stopPrice" not in params
    assert params["clientAlgoId"] == position_state.coid_tp1("sig-1")
    assert "newClientOrderId" not in params
    assert client.binance_signed_post.call_args.kwargs["path"] == "/fapi/v1/algoOrder"


@pytest.mark.asyncio
async def test_take_profit_phase_routes_to_correct_coid() -> None:
    client = _algo_mock_client()
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
        client.binance_signed_post.call_args.kwargs["params"]["clientAlgoId"]
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


# ---------------------------------------------------------------------------
# cancel_algo_order  (SL / TP orders placed via /fapi/v1/algoOrder)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cancel_algo_order_swallows_not_found_2011() -> None:
    """Binance -2011 on algo cancel = order already filled/cancelled.
    Treat as success — we wanted it gone, it's gone."""
    client = _algo_mock_client(
        delete_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -2011, "msg": "Unknown order sent"},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    # Must not raise.
    await placer.cancel_algo_order(symbol="BTCUSDT", algo_id=99001)


@pytest.mark.asyncio
async def test_cancel_algo_order_swallows_not_found_20121() -> None:
    """Binance -20121 'Order does not exist' is the algo-API equivalent
    of -2011 — treat as success."""
    client = _algo_mock_client(
        delete_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -20121, "msg": "Order does not exist"},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    await placer.cancel_algo_order(symbol="BTCUSDT", algo_id=99001)


@pytest.mark.asyncio
async def test_cancel_algo_order_raises_on_other_failures() -> None:
    """Non-not-found failures DO raise from cancel_algo_order."""
    client = _algo_mock_client(
        delete_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -1021, "msg": "Timestamp out of recvWindow"},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    with pytest.raises(order_placer.OrderRejectedByBinance):
        await placer.cancel_algo_order(symbol="BTCUSDT", algo_id=99001)


# ---------------------------------------------------------------------------
# ensure_cross_margin (2026-06-01 — VTHOUSDT isolated-margin incident)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_ensure_cross_margin_sends_crossed() -> None:
    """Posts marginType=CROSSED to /fapi/v1/marginType for the symbol."""
    client = _mock_client(post_response=_ok_resp({"code": 200, "msg": "success"}))
    placer = order_placer.OrderPlacer("fb-x", client=client)
    ok = await placer.ensure_cross_margin(symbol="BTCUSDT")
    assert ok is True
    call = client.binance_signed_post.call_args.kwargs
    assert call["path"] == "/fapi/v1/marginType"
    assert call["params"] == {"symbol": "BTCUSDT", "marginType": "CROSSED"}


@pytest.mark.asyncio
async def test_ensure_cross_margin_tolerates_already_cross() -> None:
    """Binance -4046 'No need to change margin type.' is the desired
    end-state (already CROSSED) → treated as success, not failure."""
    client = _mock_client(
        post_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -4046, "msg": "No need to change margin type."},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    assert await placer.ensure_cross_margin(symbol="BTCUSDT") is True


@pytest.mark.asyncio
async def test_ensure_cross_margin_returns_false_on_other_error() -> None:
    """Any other Binance error → False (best-effort; caller logs +
    proceeds, never raises)."""
    client = _mock_client(
        post_response=_err_resp(
            sig_protocol.ERR_BINANCE_HTTP_ERROR,
            body={"code": -4047, "msg": "Margin type cannot be changed with open position"},
        )
    )
    placer = order_placer.OrderPlacer("fb-x", client=client)
    assert await placer.ensure_cross_margin(symbol="BTCUSDT") is False


@pytest.mark.asyncio
async def test_ensure_cross_margin_never_raises_on_transport_error() -> None:
    """A signing-service / network exception is swallowed → False."""
    client = MagicMock()
    client.binance_signed_post = AsyncMock(side_effect=RuntimeError("socket gone"))
    placer = order_placer.OrderPlacer("fb-x", client=client)
    assert await placer.ensure_cross_margin(symbol="BTCUSDT") is False
