"""Typed Binance order-placement helpers on top of the signing-service client.

Wraps the raw :class:`SigningClient` from PR-4 with three typed
methods covering the order types the Position FSM needs:

* :meth:`OrderPlacer.place_market_entry` — MARKET order to enter the
  position with the user's configured quantity.
* :meth:`OrderPlacer.place_stop_loss` — STOP_MARKET with
  ``closePosition=true`` so the SL fires for the entire position
  regardless of partial closes that happen along the way.
* :meth:`OrderPlacer.place_take_profit` — TAKE_PROFIT_MARKET with an
  explicit quantity so we can lay multiple TP legs (TP1/TP2/TP3) on
  the same position per Binance's native split-target support.

* :meth:`OrderPlacer.cancel_order` — DELETE for use in PR-7's BE-shift
  (cancel old SL, place new SL at entry).

Each method:

* Sets ``newClientOrderId`` via :mod:`src.execution.position_state`'s
  :func:`coid_*` helpers so the FSM can map incoming
  ORDER_TRADE_UPDATE events back to the originating phase.
* Returns the parsed Binance response on success.
* Raises :class:`OrderPlacementError` (with a typed subclass) on
  signing-service errors / Binance rejections / network failures.
  The FSM catches and decides retry vs disable.

This module does NOT decide which orders to place — that's
:mod:`src.execution.position_fsm`.  This module is a typed adapter
between "intent" (place a SL at X) and "wire" (Binance HTTP body).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from src.security.signing_service import client as signing_client
from src.security.signing_service import protocol as sig_protocol
from src.utils import get_logger

from . import position_state as _position_state

log = get_logger("execution.order_placer")


_FUTURES_ORDER_PATH = "/fapi/v1/order"
# Binance mandatory migration (Dec 9 2025, -4120): conditional order types
# (STOP_MARKET, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET) no longer accepted
# at /fapi/v1/order; they must use /fapi/v1/algoOrder with algoType=CONDITIONAL.
# MARKET and LIMIT order types are unaffected and stay on /fapi/v1/order.
_FUTURES_ALGO_ORDER_PATH = "/fapi/v1/algoOrder"
_FUTURES_MARGIN_TYPE_PATH = "/fapi/v1/marginType"
_FUTURES_BASE = "futures"

# Binance returns -4046 "No need to change margin type." when the symbol
# is already on the requested margin mode.  We treat it as success — the
# desired end-state (CROSSED) already holds.
_ERR_NO_NEED_CHANGE_MARGIN = -4046


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------


class OrderPlacementError(Exception):
    """Base — caller decides retry / disable / propagate per error type."""

    def __init__(self, message: str, *, signing_response: Optional[sig_protocol.SignResponse] = None) -> None:
        super().__init__(message)
        self.signing_response = signing_response


class OrderRejectedByBinance(OrderPlacementError):
    """Binance returned a 4xx with a typed error code (e.g. -2010
    insufficient margin, -1111 precision-too-high).  Caller inspects
    ``signing_response.binance_body`` for the specific Binance code."""


class OrderPlacementUnreachable(OrderPlacementError):
    """Network / signing-service unavailable.  Caller may retry."""


class OrderPlacementKeyError(OrderPlacementError):
    """User's key state is bad — KEY_BLOB_NOT_FOUND (not connected),
    CRYPTO_DECRYPT_FAILED (corrupted blob), or signing service
    not configured.  Caller marks the user disabled."""


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OrderPlacementResult:
    """Parsed Binance response on a successful order placement.

    Only the fields the FSM needs.  Full body available via
    ``binance_body`` if downstream code needs more.
    """

    order_id: int
    client_order_id: str
    status: str  # "NEW" | "FILLED" | "PARTIALLY_FILLED" | ...
    avg_price: float
    binance_body: Any


def _parse_result(body: Any) -> OrderPlacementResult:
    """Map a Binance ``POST /fapi/v1/order`` response body to typed result."""
    if not isinstance(body, dict):
        # Unexpected shape — Binance would have to ship a breaking change.
        raise OrderPlacementError(
            f"unexpected Binance response shape: {type(body).__name__}"
        )
    return OrderPlacementResult(
        order_id=int(body.get("orderId", 0)),
        client_order_id=str(body.get("clientOrderId", "")),
        status=str(body.get("status", "")),
        avg_price=float(body.get("avgPrice", "0") or 0),
        binance_body=body,
    )


def _parse_algo_result(body: Any) -> OrderPlacementResult:
    """Map a Binance ``POST /fapi/v1/algoOrder`` response body to typed result.

    Algo orders return ``algoId`` (not ``orderId``) and ``clientAlgoId``
    (not ``clientOrderId``).  We surface ``algoId`` as ``order_id`` so the
    FSM can store it and pass it back to ``cancel_algo_order`` without
    needing a separate field type.  ``status`` is always "NEW" — the algo
    order is queued on Binance's side; fills arrive via User Data Stream.
    """
    if not isinstance(body, dict):
        raise OrderPlacementError(
            f"unexpected Binance algo response shape: {type(body).__name__}"
        )
    return OrderPlacementResult(
        order_id=int(body.get("algoId", 0)),
        client_order_id=str(body.get("clientAlgoId", "")),
        status="NEW",
        avg_price=0.0,
        binance_body=body,
    )


# ---------------------------------------------------------------------------
# Direction helpers
# ---------------------------------------------------------------------------


def _entry_side(direction: str) -> str:
    """LONG → BUY (enter), SHORT → SELL (enter)."""
    if direction == "LONG":
        return "BUY"
    if direction == "SHORT":
        return "SELL"
    raise ValueError(f"unknown direction: {direction!r}")


def _exit_side(direction: str) -> str:
    """LONG → SELL (exit), SHORT → BUY (exit).  Used for SL + TP
    orders that close the position."""
    if direction == "LONG":
        return "SELL"
    if direction == "SHORT":
        return "BUY"
    raise ValueError(f"unknown direction: {direction!r}")


# ---------------------------------------------------------------------------
# OrderPlacer — typed wrapper around SigningClient
# ---------------------------------------------------------------------------


class OrderPlacer:
    """Typed Binance Futures order placement for one user.

    Stateless — methods accept all parameters explicitly.  Constructed
    per-FSM (one per signal) so each instance carries the firebase_uid
    + signing client without a thread of context.

    ``client`` is injectable for tests (mock SigningClient).
    """

    def __init__(
        self,
        firebase_uid: str,
        *,
        client: Optional[signing_client.SigningClient] = None,
    ) -> None:
        self.firebase_uid = firebase_uid
        self._client = client or signing_client.SigningClient()

    async def ensure_cross_margin(self, *, symbol: str) -> bool:
        """Force the symbol onto CROSSED margin before the entry order.

        Owner-reported 2026-06-01: a test account showed five VTHOUSDT
        positions in ISOLATED margin (all losses) because the symbol
        defaulted to isolated on the Binance account from a prior manual
        session.  The engine places every position assuming CROSSED, but
        never asserted it — Binance silently honoured the account's
        per-symbol isolated setting.  This method closes that gap by
        issuing ``POST /fapi/v1/marginType marginType=CROSSED`` before the
        first entry on each symbol.

        Idempotent on Binance's side: -4046 ("No need to change margin
        type.") is returned when the symbol is already CROSSED, which we
        treat as success.  Callers cache the per-(uid, symbol) success so
        this only hits the wire once per symbol per process.

        Returns ``True`` when the symbol is confirmed CROSSED (either we
        switched it or it already was), ``False`` on any other failure.
        Best-effort by contract: a ``False`` return is logged but does not
        by itself block the entry — the caller decides.  It never raises.
        """
        params = {"symbol": symbol, "marginType": "CROSSED"}
        try:
            resp = await self._client.binance_signed_post(
                firebase_uid=self.firebase_uid,
                base=_FUTURES_BASE,
                path=_FUTURES_MARGIN_TYPE_PATH,
                params=params,
            )
        except Exception as exc:  # network / signing-service blip
            log.warning(
                "ensure_cross_margin: request raised uid={} symbol={} exc={}",
                self.firebase_uid, symbol, exc,
            )
            return False
        if resp.ok:
            log.info(
                "ensure_cross_margin: set CROSSED uid={} symbol={}",
                self.firebase_uid, symbol,
            )
            return True
        # Already cross → Binance -4046; that's the end-state we wanted.
        if (
            resp.error_code == sig_protocol.ERR_BINANCE_HTTP_ERROR
            and isinstance(resp.binance_body, dict)
            and resp.binance_body.get("code") == _ERR_NO_NEED_CHANGE_MARGIN
        ):
            return True
        log.warning(
            "ensure_cross_margin: failed uid={} symbol={} code={} body={}",
            self.firebase_uid, symbol, resp.error_code, resp.binance_body,
        )
        return False

    async def place_market_entry(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,  # "LONG" | "SHORT"
        quantity: float,
    ) -> OrderPlacementResult:
        """MARKET order to enter the position.

        Uses ``newClientOrderId = lumin_<signal_id>_entry`` so the
        FSM can identify fill events.  ``positionSide=BOTH`` (one-way
        mode) — hedge mode is a future option.
        """
        params = {
            "symbol": symbol,
            "side": _entry_side(direction),
            "type": "MARKET",
            "quantity": _qty_str(quantity),
            "newClientOrderId": _position_state.coid_entry(signal_id),
        }
        return await self._submit_order(
            params=params,
            phase="entry",
            signal_id=signal_id,
        )

    async def place_stop_loss(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,
        stop_price: float,
        coid_override: Optional[str] = None,
    ) -> OrderPlacementResult:
        """Conditional stop order with ``closePosition=true``.

        Uses ``/fapi/v1/algoOrder`` with ``algoType=CONDITIONAL`` per the
        Binance mandatory migration effective Dec 9 2025 (-4120).  The
        legacy ``type=STOP_MARKET`` on ``/fapi/v1/order`` is rejected by
        Binance on all accounts since that date.

        Fires for the full remaining position when ``stop_price`` is
        touched on MARK_PRICE — less wick-prone than CONTRACT_PRICE.

        ``coid_override`` lets the BE-shift re-place an SL with a new
        ``clientAlgoId`` (since you can't modify SL price in place; you
        cancel + replace).  Default uses the standard ``_sl`` suffix;
        BE-shift uses ``_sl_be`` to distinguish the new order from the
        original on User Data Stream fill events.

        Returns ``OrderPlacementResult`` with ``order_id = algoId`` so
        callers can store it and pass it to ``cancel_algo_order``.
        """
        from src.execution import symbol_filters as _sf
        coid = coid_override or _position_state.coid_sl(signal_id)
        # Round stop_price to the symbol's tickSize so Binance doesn't
        # reject with -4014 "Price not increased by tick size".
        rounded = _sf.round_price(symbol, stop_price)
        params = {
            "symbol": symbol,
            "side": _exit_side(direction),
            "algoType": "CONDITIONAL",
            "stopPrice": _price_str(rounded),
            "closePosition": "true",
            "workingType": "MARK_PRICE",
            "clientAlgoId": coid,
        }
        return await self._submit_algo_order(
            params=params,
            phase="sl",
            signal_id=signal_id,
        )

    async def place_take_profit(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,
        stop_price: float,
        quantity: float,
        tp_phase: str,  # "tp1" | "tp2" | "tp3"
    ) -> OrderPlacementResult:
        """Conditional take-profit order with explicit quantity for partial close.

        Uses ``/fapi/v1/algoOrder`` with ``algoType=CONDITIONAL`` per the
        Binance mandatory migration effective Dec 9 2025 (-4120).  The
        legacy ``type=TAKE_PROFIT_MARKET`` on ``/fapi/v1/order`` is rejected
        by Binance on all accounts since that date.

        Lumin places TP1 / TP2 / TP3 as separate orders per Binance's native
        split-target support.  ``reduceOnly=true`` so a TP can't accidentally
        open a counter-position if the fill arithmetic is off.

        Returns ``OrderPlacementResult`` with ``order_id = algoId`` so
        callers can store it and pass it to ``cancel_algo_order``.
        """
        from src.execution import symbol_filters as _sf
        if tp_phase not in ("tp1", "tp2", "tp3"):
            raise ValueError(f"tp_phase must be tp1|tp2|tp3, got {tp_phase!r}")
        coid_fn = {
            "tp1": _position_state.coid_tp1,
            "tp2": _position_state.coid_tp2,
            "tp3": _position_state.coid_tp3,
        }[tp_phase]
        rounded_price = _sf.round_price(symbol, stop_price)
        params = {
            "symbol": symbol,
            "side": _exit_side(direction),
            "algoType": "CONDITIONAL",
            "stopPrice": _price_str(rounded_price),
            "quantity": _qty_str(quantity),
            "reduceOnly": "true",
            "workingType": "MARK_PRICE",
            "clientAlgoId": coid_fn(signal_id),
        }
        return await self._submit_algo_order(
            params=params,
            phase=tp_phase,
            signal_id=signal_id,
        )

    async def place_pretp_partial(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,
        quantity: float,
    ) -> OrderPlacementResult:
        """REDUCE_ONLY MARKET order for the pre-TP partial close.

        Fired by :mod:`src.execution.pretp_controller` when the mark
        price crosses the configured pre-TP threshold.  Closes a
        ``pretp_fraction`` slice of the position immediately — banks
        the doctrine-critical §3.2a profit before the residual rides
        toward TP1 or back to the BE-shifted SL.

        REDUCE_ONLY ensures we can't accidentally open a counter-
        position if the fill arithmetic is off (defence-in-depth on
        top of the position-cap tripwire from PR-8).
        """
        params = {
            "symbol": symbol,
            "side": _exit_side(direction),
            "type": "MARKET",
            "quantity": _qty_str(quantity),
            "reduceOnly": "true",
            "newClientOrderId": _position_state.coid_pretp(signal_id),
        }
        return await self._submit_order(
            params=params,
            phase="pretp",
            signal_id=signal_id,
        )

    async def place_pretp_limit(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,
        limit_price: float,
        quantity: float,
    ) -> OrderPlacementResult:
        """REDUCE_ONLY GTC LIMIT order for the pre-TP partial close.

        Placed at dispatch time (alongside SL/TP) at the pre-TP threshold
        price so the fill is passive (maker pricing, zero poll lag).

        Uses the same ``coid_pretp`` client order id as the tick-based
        MARKET path so ``_apply_pretp_fill`` handles both fill origins
        identically.  ``pretp_order_id != 0`` on the position is the
        sentinel that tells ``should_fire_pretp`` not to MARKET-chase.
        """
        from src.execution import symbol_filters as _sf
        rounded = _sf.round_price(symbol, limit_price)
        params = {
            "symbol": symbol,
            "side": _exit_side(direction),
            "type": "LIMIT",
            "price": _price_str(rounded),
            "quantity": _qty_str(quantity),
            "reduceOnly": "true",
            "timeInForce": "GTC",
            "newClientOrderId": _position_state.coid_pretp(signal_id),
        }
        return await self._submit_order(
            params=params,
            phase="pretp_limit",
            signal_id=signal_id,
        )

    async def place_market_close(
        self,
        *,
        signal_id: str,
        symbol: str,
        direction: str,  # "LONG" | "SHORT"
        quantity: float,
    ) -> OrderPlacementResult:
        """REDUCE_ONLY MARKET order for a full close on invalidation/expiry/
        cancellation.

        Uses ``coid_close`` so the FSM can identify the fill event as a
        terminal close (not a pre-TP partial or normal fill).

        Called by :func:`signal_dispatch.close_fsm_positions_for_signal`
        when the engine's signal-lifecycle monitor decides to exit (regime
        shift, momentum-loss invalidation, max-hold expiry, or SL hit
        detected engine-side before the native Binance SL fires).

        ``reduceOnly=true`` ensures this can never accidentally open a
        counter-position if the position was already closed on Binance
        (e.g. the native SL fired a millisecond before we got here).
        """
        params = {
            "symbol": symbol,
            "side": _exit_side(direction),
            "type": "MARKET",
            "quantity": _qty_str(quantity),
            "reduceOnly": "true",
            "newClientOrderId": _position_state.coid_close(signal_id),
        }
        return await self._submit_order(
            params=params,
            phase="close",
            signal_id=signal_id,
        )

    async def cancel_order(
        self,
        *,
        symbol: str,
        order_id: int,
    ) -> None:
        """Cancel a regular (non-algo) open order by Binance ``orderId``.

        Used for LIMIT and MARKET orders on ``/fapi/v1/order`` — e.g. the
        pre-TP LIMIT resting on Binance's book.  SL and TP orders placed via
        ``place_stop_loss`` / ``place_take_profit`` are algo orders and must
        be cancelled via ``cancel_algo_order`` instead.

        Raises :class:`OrderPlacementError` subclasses on failure;
        a "no such order" rejection is logged + swallowed (the order
        was already filled or cancelled — caller doesn't care which).
        """
        params = {"symbol": symbol, "orderId": order_id}
        resp = await self._client.binance_signed_delete(
            firebase_uid=self.firebase_uid,
            base=_FUTURES_BASE,
            path=_FUTURES_ORDER_PATH,
            params=params,
        )
        if resp.ok:
            return
        # -2011 = "Unknown order sent" — order already filled/cancelled.
        if (
            resp.error_code == sig_protocol.ERR_BINANCE_HTTP_ERROR
            and isinstance(resp.binance_body, dict)
            and resp.binance_body.get("code") == -2011
        ):
            log.info(
                "cancel_order: order already gone (uid={} order_id={})",
                self.firebase_uid,
                order_id,
            )
            return
        _raise_for_signing_error(resp, phase="cancel")

    async def cancel_algo_order(
        self,
        *,
        symbol: str,
        algo_id: int,
    ) -> None:
        """Cancel an algo order by Binance ``algoId``.

        Used to cancel SL and TP orders placed via ``place_stop_loss``
        and ``place_take_profit``, which now use ``/fapi/v1/algoOrder``.
        ``algo_id`` is the ``algoId`` field from the placement response,
        surfaced as ``order_id`` in ``OrderPlacementResult``.

        Tolerant of "already gone": Binance returns -2011 or -20121 when
        the order was already filled / cancelled — both are swallowed since
        the desired end-state (order gone) is already true.
        """
        params = {"symbol": symbol, "algoId": algo_id}
        resp = await self._client.binance_signed_delete(
            firebase_uid=self.firebase_uid,
            base=_FUTURES_BASE,
            path=_FUTURES_ALGO_ORDER_PATH,
            params=params,
        )
        if resp.ok:
            return
        if (
            resp.error_code == sig_protocol.ERR_BINANCE_HTTP_ERROR
            and isinstance(resp.binance_body, dict)
            and resp.binance_body.get("code") in (-2011, -20121)
        ):
            log.info(
                "cancel_algo_order: algo order already gone (uid={} algo_id={})",
                self.firebase_uid,
                algo_id,
            )
            return
        _raise_for_signing_error(resp, phase="cancel_algo")

    async def _submit_order(
        self,
        *,
        params: dict,
        phase: str,
        signal_id: str,
    ) -> OrderPlacementResult:
        """Shared POST + error-mapping helper for MARKET/LIMIT order verbs."""
        resp = await self._client.binance_signed_post(
            firebase_uid=self.firebase_uid,
            base=_FUTURES_BASE,
            path=_FUTURES_ORDER_PATH,
            params=params,
        )
        if not resp.ok:
            _raise_for_signing_error(resp, phase=phase)
        log.info(
            "order placed: uid={} signal_id={} phase={} order_id={}",
            self.firebase_uid,
            signal_id,
            phase,
            (resp.binance_body or {}).get("orderId"),
        )
        return _parse_result(resp.binance_body)

    async def _submit_algo_order(
        self,
        *,
        params: dict,
        phase: str,
        signal_id: str,
    ) -> OrderPlacementResult:
        """POST to ``/fapi/v1/algoOrder`` + error-mapping for conditional orders.

        Returns ``OrderPlacementResult`` with ``order_id = algoId`` from the
        response, so callers can store and later pass to ``cancel_algo_order``.
        """
        resp = await self._client.binance_signed_post(
            firebase_uid=self.firebase_uid,
            base=_FUTURES_BASE,
            path=_FUTURES_ALGO_ORDER_PATH,
            params=params,
        )
        if not resp.ok:
            _raise_for_signing_error(resp, phase=phase)
        log.info(
            "algo order placed: uid={} signal_id={} phase={} algo_id={}",
            self.firebase_uid,
            signal_id,
            phase,
            (resp.binance_body or {}).get("algoId"),
        )
        return _parse_algo_result(resp.binance_body)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _qty_str(qty: float) -> str:
    """Format a quantity for Binance's wire format.

    Binance expects string-encoded decimals (precision-preserving).
    We round to 8 decimal places — well beyond any Futures symbol's
    actual precision — and strip trailing zeros so the wire form is
    minimal.  Per-symbol precision (LOT_SIZE / PRICE_FILTER) is the
    caller's responsibility; this is just lossless serialisation.
    """
    return f"{qty:.8f}".rstrip("0").rstrip(".")


def _price_str(price: float) -> str:
    """Same convention as :func:`_qty_str`, separate function for
    readability at call sites."""
    return f"{price:.8f}".rstrip("0").rstrip(".")


def _raise_for_signing_error(
    resp: sig_protocol.SignResponse, *, phase: str
) -> None:
    """Map a non-ok :class:`SignResponse` to the right typed
    :class:`OrderPlacementError` subclass.

    Centralised so every order-placing method has consistent error
    taxonomy — FSM's catch chain only deals with three exception
    types, not seven."""
    code = resp.error_code
    msg = (
        f"order placement failed (phase={phase}): "
        f"code={code} status={resp.binance_status} "
        f"message={resp.error_message}"
    )
    if code in (
        sig_protocol.ERR_KEY_BLOB_NOT_FOUND,
        sig_protocol.ERR_CRYPTO_DECRYPT_FAILED,
        sig_protocol.ERR_INTERNAL_ERROR,
    ):
        raise OrderPlacementKeyError(msg, signing_response=resp)
    if code in (
        sig_protocol.ERR_BINANCE_UNREACHABLE,
        sig_protocol.ERR_KMS_DECRYPT_FAILED,
    ):
        raise OrderPlacementUnreachable(msg, signing_response=resp)
    if code == sig_protocol.ERR_BINANCE_HTTP_ERROR:
        raise OrderRejectedByBinance(msg, signing_response=resp)
    # BAD_REQUEST / unknown — programming bug, surface loudly.
    raise OrderPlacementError(msg, signing_response=resp)
