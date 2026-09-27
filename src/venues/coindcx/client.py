"""CoinDCX futures calls for one user, through the signing service.

Engine-side.  The secret never reaches this process: every call is a
``coindcx_signed_*`` request to the signing service, which holds the key,
enforces the endpoint allow-list and signs the body.

Errors are subclasses of :mod:`src.execution.order_placer`'s typed errors on
purpose — the circuit breakers (``tripwires.record_order_placement_failure``)
classify by those classes, so a CoinDCX rejection trips exactly what a Binance
rejection of the same kind would, with no second breaker to keep in step.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from src.execution import order_placer as _op
from src.security.signing_service import client as _signing_client
from src.security.signing_service import protocol as _proto
from src.utils import get_logger

log = get_logger("venues.coindcx.client")

P_ORDERS_CREATE = "/exchange/v1/derivatives/futures/orders/create"
P_ORDERS_CANCEL = "/exchange/v1/derivatives/futures/orders/cancel"
P_ORDERS_LIST = "/exchange/v1/derivatives/futures/orders"
P_POSITIONS = "/exchange/v1/derivatives/futures/positions"
P_TPSL = "/exchange/v1/derivatives/futures/positions/create_tpsl"
P_EXIT = "/exchange/v1/derivatives/futures/positions/exit"
P_LEVERAGE = "/exchange/v1/derivatives/futures/positions/update_leverage"
P_CANCEL_FOR_POSITION = (
    "/exchange/v1/derivatives/futures/positions/cancel_all_open_orders_for_position"
)
P_WALLETS = "/exchange/v1/derivatives/futures/wallets"

_KEY_ERRORS = frozenset({
    _proto.ERR_KEY_BLOB_NOT_FOUND,
    _proto.ERR_KEY_NOT_ATTESTED,
    _proto.ERR_CRYPTO_DECRYPT_FAILED,
})
_TRANSIENT_ERRORS = frozenset({
    _proto.ERR_BINANCE_UNREACHABLE,
    _proto.ERR_KMS_DECRYPT_FAILED,
    _proto.ERR_INTERNAL_ERROR,
})

#: Rejections that describe the USER's account (funds, size), not a fault.
#: Like Binance's -2019 they reach the user's Recent Activity and never count
#: toward a circuit breaker: one under-funded user must not walk the global
#: breaker toward halting everyone.
_USER_SETUP_MARKERS = (
    "insufficient",
    "minimum order value",
    "quantity should be greater",
    "max allowed leverage",
)


class CoinDCXRejected(_op.OrderRejectedByBinance):
    """CoinDCX answered 4xx — the request did not execute."""

    def __init__(self, message: str, *, status: int, body: Any) -> None:
        super().__init__(message)
        self.status = status
        self.body = body

    @property
    def exchange_message(self) -> str:
        b = self.body
        if isinstance(b, dict):
            return str(b.get("message") or b.get("error") or b.get("msg") or "")
        return ""

    @property
    def user_setup(self) -> bool:
        text = (self.exchange_message or str(self)).lower()
        return any(m in text for m in _USER_SETUP_MARKERS)


class CoinDCXUnreachable(_op.OrderPlacementUnreachable):
    """Network, timeout, KMS or signing-service failure — outcome unknown."""


class CoinDCXKeyError(_op.OrderPlacementKeyError):
    """No key, no attestation, or an undecryptable key — the user must act."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code


def definitely_not_executed(exc: BaseException) -> bool:
    """True when the exchange cannot have acted on the request."""
    return isinstance(exc, (CoinDCXRejected, CoinDCXKeyError))


class CoinDCXClient:
    """Typed CoinDCX futures calls for one Firebase uid."""

    def __init__(
        self,
        firebase_uid: str,
        *,
        signing: Optional[_signing_client.SigningClient] = None,
    ) -> None:
        self.uid = firebase_uid
        self._signing = signing or _signing_client.SigningClient()

    async def _call(self, method: str, path: str, body: Optional[dict] = None) -> Any:
        fn = (
            self._signing.coindcx_signed_post if method == "POST"
            else self._signing.coindcx_signed_get
        )
        try:
            resp = await fn(firebase_uid=self.uid, path=path, body=body or {})
        except (asyncio.TimeoutError, OSError) as exc:
            raise CoinDCXUnreachable(
                f"signing service transport failed: {type(exc).__name__}"
            ) from exc
        if resp.ok:
            return resp.binance_body
        if resp.error_code in _KEY_ERRORS:
            raise CoinDCXKeyError(resp.error_message, code=resp.error_code)
        if resp.error_code == _proto.ERR_BINANCE_HTTP_ERROR:
            if resp.binance_status and resp.binance_status >= 500:
                raise CoinDCXUnreachable(resp.error_message)
            raise CoinDCXRejected(
                resp.error_message, status=resp.binance_status, body=resp.binance_body,
            )
        if resp.error_code in _TRANSIENT_ERRORS:
            raise CoinDCXUnreachable(resp.error_message)
        raise CoinDCXUnreachable(f"{resp.error_code}: {resp.error_message}")

    # -- Reads ------------------------------------------------------------

    async def positions(
        self, *, pairs: Optional[List[str]] = None, margin_currencies: tuple = ("USDT", "INR"),
        size: int = 100,
    ) -> List[Dict[str, Any]]:
        """Positions (flat ones included) for ``pairs`` or for the account."""
        body: Dict[str, Any] = {
            "page": "1", "size": str(size),
            "margin_currency_short_name": list(margin_currencies),
        }
        if pairs:
            body["pairs"] = ",".join(pairs)
        data = await self._call("POST", P_POSITIONS, body)
        return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []

    async def orders(
        self, *, statuses: str, side: str, margin_currencies: tuple = ("USDT", "INR"),
        size: int = 50,
    ) -> List[Dict[str, Any]]:
        data = await self._call("POST", P_ORDERS_LIST, {
            "status": statuses, "side": side, "page": "1", "size": str(size),
            "margin_currency_short_name": list(margin_currencies),
        })
        return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []

    async def wallets(self) -> List[Dict[str, Any]]:
        data = await self._call("GET", P_WALLETS, {})
        return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []

    # -- Writes -----------------------------------------------------------

    async def update_leverage(self, *, pair: str, leverage: int, margin_currency: str) -> None:
        await self._call("POST", P_LEVERAGE, {
            "pair": pair, "leverage": str(int(leverage)),
            "margin_currency_short_name": margin_currency,
        })

    async def market_order(
        self, *, pair: str, side: str, quantity: str, leverage: int, margin_currency: str,
    ) -> Dict[str, Any]:
        """One market order.  ``side`` is ``buy``/``sell``; returns the order."""
        data = await self._call("POST", P_ORDERS_CREATE, {
            "order": {
                "side": side,
                "pair": pair,
                "order_type": "market_order",
                "total_quantity": float(quantity),
                "leverage": int(leverage),
                "notification": "no_notification",
                "margin_currency_short_name": margin_currency,
                "position_margin_type": "isolated",
            }
        })
        rows = data if isinstance(data, list) else [data]
        order = next((r for r in rows if isinstance(r, dict) and r.get("id")), None)
        if order is None:
            raise CoinDCXUnreachable(f"order create returned no order id: {type(data).__name__}")
        return order

    async def cancel_order(self, *, order_id: str) -> None:
        await self._call("POST", P_ORDERS_CANCEL, {"id": order_id})

    async def create_tpsl(
        self, *, position_id: str, stop_price: str, take_profit_price: Optional[str],
    ) -> Dict[str, Any]:
        """Position-level TP/SL — both close the ENTIRE position."""
        body: Dict[str, Any] = {
            "id": position_id,
            "stop_loss": {"stop_price": stop_price, "order_type": "stop_market"},
        }
        if take_profit_price:
            body["take_profit"] = {
                "stop_price": take_profit_price, "order_type": "take_profit_market",
            }
        data = await self._call("POST", P_TPSL, body)
        return data if isinstance(data, dict) else {}

    async def exit_position(self, *, position_id: str) -> Dict[str, Any]:
        data = await self._call("POST", P_EXIT, {"id": position_id})
        return data if isinstance(data, dict) else {}

    async def cancel_all_for_position(self, *, position_id: str) -> None:
        await self._call("POST", P_CANCEL_FOR_POSITION, {"id": position_id})


def tpsl_leg(result: Dict[str, Any], leg: str) -> tuple[bool, str, str]:
    """``(ok, order_id, error)`` for ``stop_loss`` / ``take_profit`` in a
    ``create_tpsl`` answer.  A leg is placed only if it came back as an order
    with an id; ``{"success": false, "error": ...}`` and absence both fail."""
    part = result.get(leg) if isinstance(result, dict) else None
    if not isinstance(part, dict):
        return False, "", "missing"
    if part.get("success") is False:
        return False, "", str(part.get("error") or "refused")
    oid = str(part.get("id") or "")
    return (bool(oid), oid, "" if oid else "no id")
