"""Server-side Binance Futures proxy — executes signed requests on
behalf of a Lumin user using their per-user credentials from
:class:`BinanceKeysStore`.

This replaces the direct ``api.binance.com`` calls the Flutter app
used to issue from ``binance_client.dart``.  All Binance traffic now
originates from the VPS's IP-allowlisted address, fixing the
"request ip: <cellular-ip> not allowlisted" error class.

Surface (mirrors ``binance_client.dart`` for drop-in replacement):

    * :meth:`get_account`      → ``GET /fapi/v2/account``
    * :meth:`get_positions`    → ``GET /fapi/v2/positionRisk``
    * :meth:`place_order`      → ``POST /fapi/v1/order``
    * :meth:`close_position`   → ``POST /fapi/v1/order`` reduce-only
    * :meth:`server_time`      → ``GET /fapi/v1/time`` (unsigned)
    * :meth:`verify`           → cheap signed probe used by the
                                 "Test connection" button on the app.

Signing
-------

Standard Binance Futures HMAC-SHA256: build a query string from the
params (alphabetical not required, but recv_window + timestamp must
be present for signed endpoints), HMAC-SHA256 it with the API secret,
append ``signature=<hex>``.  Headers: ``X-MBX-APIKEY: <api_key>``.

Errors
------

Binance returns ``{"code": <int>, "msg": "..."}`` on rejection.  Any
non-2xx response or non-empty ``code`` raises :class:`BinanceProxyError`
with the upstream code preserved for surfacing in the app's error UI.
"""

from __future__ import annotations

import hashlib
import hmac
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp

from src.auto_trade.binance_keys_store import BinanceKeys, BinanceKeysStore
from src.utils import get_logger

log = get_logger("auto_trade.binance_proxy")


_MAINNET_BASE = "https://fapi.binance.com"
_TESTNET_BASE = "https://testnet.binancefuture.com"
_DEFAULT_RECV_WINDOW_MS = 5000
_DEFAULT_TIMEOUT_S = 8.0


# ---------------------------------------------------------------------------
# Domain objects (subset of Binance response fields — only what the app needs)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AccountState:
    """Decoded subset of ``GET /fapi/v2/account``."""

    total_wallet_balance: float
    total_unrealized_profit: float
    total_margin_balance: float
    available_balance: float
    max_withdraw_amount: float
    open_position_count: int


@dataclass(frozen=True)
class Position:
    """One entry from ``GET /fapi/v2/positionRisk`` (non-zero positions only)."""

    symbol: str
    position_amt: float            # signed; negative for SHORT
    entry_price: float
    mark_price: float
    unrealized_profit: float
    leverage: int
    isolated: bool
    side: str                      # "LONG" / "SHORT" derived from position_amt sign


@dataclass(frozen=True)
class OrderResult:
    """Decoded subset of ``POST /fapi/v1/order``."""

    order_id: int
    symbol: str
    side: str
    type: str
    status: str
    executed_qty: float
    avg_price: float
    reduce_only: bool


class BinanceProxyError(Exception):
    """Raised when Binance returns a non-success response or transport fails.

    Carries the upstream ``code`` (Binance error code, or ``None`` for
    transport / decode errors) so the app can surface a precise message.
    """

    def __init__(
        self,
        message: str,
        *,
        code: Optional[int] = None,
        http_status: Optional[int] = None,
        request_ip: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.http_status = http_status
        self.request_ip = request_ip

    def __str__(self) -> str:  # pragma: no cover — trivial
        bits = [super().__str__()]
        if self.code is not None:
            bits.append(f"code={self.code}")
        if self.http_status is not None:
            bits.append(f"http={self.http_status}")
        if self.request_ip is not None:
            bits.append(f"request_ip={self.request_ip}")
        return " | ".join(bits)


# ---------------------------------------------------------------------------
# Proxy client
# ---------------------------------------------------------------------------


class BinanceProxyClient:
    """Per-user Binance Futures client.  One instance is shared across
    requests; per-call we look up credentials from the keys store.

    The client owns an :class:`aiohttp.ClientSession` for connection
    pooling.  Call :meth:`close` on shutdown.
    """

    def __init__(
        self,
        keys_store: BinanceKeysStore,
        *,
        session: Optional[aiohttp.ClientSession] = None,
        timeout_s: float = _DEFAULT_TIMEOUT_S,
    ) -> None:
        self._keys_store = keys_store
        self._owns_session = session is None
        self._session = session or aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout_s),
        )

    async def close(self) -> None:
        if self._owns_session and not self._session.closed:
            await self._session.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_keys(self, user_id: int) -> BinanceKeys:
        keys = self._keys_store.get(user_id)
        if keys is None:
            raise BinanceProxyError(
                "no Binance keys stored for this user — upload them via "
                "POST /api/auto-trade/keys before calling this endpoint",
                code=-9001,  # synthetic; our domain
            )
        return keys

    @staticmethod
    def _base_url(testnet: bool) -> str:
        return _TESTNET_BASE if testnet else _MAINNET_BASE

    @staticmethod
    def _sign(query: str, secret: str) -> str:
        return hmac.new(
            secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    @staticmethod
    def _timestamp_ms() -> int:
        return int(time.time() * 1000)

    async def _signed_request(
        self,
        keys: BinanceKeys,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Issue a signed Binance Futures request and return decoded JSON."""
        all_params = dict(params or {})
        all_params["timestamp"] = self._timestamp_ms()
        all_params["recvWindow"] = _DEFAULT_RECV_WINDOW_MS
        # urlencode with stable ordering (insertion order in dict).
        query_str = urllib.parse.urlencode(all_params, doseq=True)
        signature = self._sign(query_str, keys.api_secret)
        signed_query = f"{query_str}&signature={signature}"
        url = f"{self._base_url(keys.testnet)}{path}?{signed_query}"
        headers = {"X-MBX-APIKEY": keys.api_key}

        try:
            async with self._session.request(method, url, headers=headers) as resp:
                body_text = await resp.text()
                status = resp.status
        except aiohttp.ClientError as exc:
            raise BinanceProxyError(
                f"transport error talking to Binance: {exc}",
                code=None,
            ) from exc

        # Best-effort JSON decode.
        try:
            body = _safe_json_loads(body_text)
        except ValueError as exc:
            raise BinanceProxyError(
                f"non-JSON response from Binance ({status}): {body_text[:200]}",
                http_status=status,
            ) from exc

        if status >= 400 or (isinstance(body, dict) and isinstance(body.get("code"), int) and body["code"] < 0):
            code = None
            msg = body_text
            request_ip = None
            if isinstance(body, dict):
                code = body.get("code")
                msg = str(body.get("msg") or body_text)
                # Binance includes "request ip: <ip>" inside `msg` for IP errors.
                # Parse it out for clean surfacing on the app.
                if "request ip" in msg.lower():
                    request_ip = _parse_request_ip(msg)
            raise BinanceProxyError(
                msg, code=code, http_status=status, request_ip=request_ip,
            )
        return body

    async def _public_get(self, base_url: str, path: str) -> Any:
        url = f"{base_url}{path}"
        try:
            async with self._session.get(url) as resp:
                return await resp.json(content_type=None)
        except aiohttp.ClientError as exc:
            raise BinanceProxyError(f"transport error: {exc}") from exc

    # ------------------------------------------------------------------
    # Public surface
    # ------------------------------------------------------------------

    async def server_time(self, *, testnet: bool = False) -> int:
        """Return Binance server epoch-ms.  Used for clock sanity-check
        before signing — large clock skew causes ``-1021`` errors."""
        body = await self._public_get(self._base_url(testnet), "/fapi/v1/time")
        if not isinstance(body, dict) or "serverTime" not in body:
            raise BinanceProxyError(f"unexpected /fapi/v1/time response: {body!r}")
        return int(body["serverTime"])

    async def verify(self, user_id: int) -> AccountState:
        """Probe ``/fapi/v2/account`` with the stored keys.  On success
        the store's ``last_verified_at`` is stamped and the decoded
        :class:`AccountState` is returned.  Raises :class:`BinanceProxyError`
        on any failure — caller decides how to surface."""
        account = await self.get_account(user_id)
        self._keys_store.mark_verified(user_id)
        return account

    async def get_account(self, user_id: int) -> AccountState:
        keys = self._load_keys(user_id)
        body = await self._signed_request(keys, "GET", "/fapi/v2/account")
        if not isinstance(body, dict):
            raise BinanceProxyError(f"unexpected /fapi/v2/account shape: {body!r}")
        self._keys_store.mark_used(user_id)
        positions = body.get("positions") or []
        open_count = sum(
            1 for p in positions
            if isinstance(p, dict) and _safe_float(p.get("positionAmt"), 0.0) != 0.0
        )
        return AccountState(
            total_wallet_balance=_safe_float(body.get("totalWalletBalance")),
            total_unrealized_profit=_safe_float(body.get("totalUnrealizedProfit")),
            total_margin_balance=_safe_float(body.get("totalMarginBalance")),
            available_balance=_safe_float(body.get("availableBalance")),
            max_withdraw_amount=_safe_float(body.get("maxWithdrawAmount")),
            open_position_count=open_count,
        )

    async def get_positions(self, user_id: int) -> List[Position]:
        """Return all non-zero open positions.  ``/fapi/v2/positionRisk``
        returns every tradeable symbol; we filter to ``positionAmt != 0``."""
        keys = self._load_keys(user_id)
        body = await self._signed_request(keys, "GET", "/fapi/v2/positionRisk")
        if not isinstance(body, list):
            raise BinanceProxyError(f"unexpected /fapi/v2/positionRisk shape: {body!r}")
        self._keys_store.mark_used(user_id)
        out: List[Position] = []
        for entry in body:
            if not isinstance(entry, dict):
                continue
            amt = _safe_float(entry.get("positionAmt"), 0.0)
            if amt == 0.0:
                continue
            out.append(
                Position(
                    symbol=str(entry.get("symbol") or ""),
                    position_amt=amt,
                    entry_price=_safe_float(entry.get("entryPrice")),
                    mark_price=_safe_float(entry.get("markPrice")),
                    unrealized_profit=_safe_float(entry.get("unRealizedProfit")),
                    leverage=int(_safe_float(entry.get("leverage"), 1.0)),
                    isolated=str(entry.get("marginType") or "").lower() == "isolated",
                    side="LONG" if amt > 0 else "SHORT",
                )
            )
        return out

    async def place_order(
        self,
        user_id: int,
        *,
        symbol: str,
        side: str,             # "BUY" / "SELL"
        type: str,             # "MARKET" / "LIMIT"
        quantity: float,
        price: Optional[float] = None,
        reduce_only: bool = False,
        time_in_force: Optional[str] = None,  # "GTC" / "IOC" / "FOK" — required for LIMIT
        client_order_id: Optional[str] = None,
    ) -> OrderResult:
        """Place a Futures order.  Quantity must already be rounded to
        the symbol's ``stepSize``; caller is responsible for filter
        compliance (handled by the engine's order_executor today)."""
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": type.upper(),
            "quantity": f"{quantity:.8f}".rstrip("0").rstrip("."),
        }
        if reduce_only:
            params["reduceOnly"] = "true"
        if type.upper() == "LIMIT":
            if price is None:
                raise BinanceProxyError("LIMIT orders require a price")
            params["price"] = f"{price:.8f}".rstrip("0").rstrip(".")
            params["timeInForce"] = (time_in_force or "GTC").upper()
        if client_order_id:
            params["newClientOrderId"] = client_order_id

        keys = self._load_keys(user_id)
        body = await self._signed_request(keys, "POST", "/fapi/v1/order", params=params)
        if not isinstance(body, dict):
            raise BinanceProxyError(f"unexpected /fapi/v1/order shape: {body!r}")
        self._keys_store.mark_used(user_id)
        return OrderResult(
            order_id=int(body.get("orderId", 0)),
            symbol=str(body.get("symbol") or ""),
            side=str(body.get("side") or ""),
            type=str(body.get("type") or ""),
            status=str(body.get("status") or ""),
            executed_qty=_safe_float(body.get("executedQty")),
            avg_price=_safe_float(body.get("avgPrice")),
            reduce_only=bool(body.get("reduceOnly", False)),
        )

    async def close_position(
        self,
        user_id: int,
        *,
        symbol: str,
    ) -> Optional[OrderResult]:
        """Close any open position on ``symbol`` with a reduce-only
        MARKET order.  Returns ``None`` when no position is open."""
        positions = await self.get_positions(user_id)
        match = next((p for p in positions if p.symbol == symbol.upper()), None)
        if match is None:
            return None
        # Closing side is the opposite of the position side.
        side = "SELL" if match.position_amt > 0 else "BUY"
        return await self.place_order(
            user_id,
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=abs(match.position_amt),
            reduce_only=True,
        )


# ---------------------------------------------------------------------------
# Module helpers
# ---------------------------------------------------------------------------


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def _safe_json_loads(text: str) -> Any:
    """``json.loads`` with a friendlier error type — kept here so we
    don't pull ``json`` into every caller's import block."""
    import json
    return json.loads(text)


def _parse_request_ip(msg: str) -> Optional[str]:
    """Extract the ``request ip: 1.2.3.4`` IP that Binance includes in
    IP-restriction error messages so the app can show a useful hint
    ('this IP isn't whitelisted — check Binance API key settings')."""
    import re
    match = re.search(r"request ip:\s*([0-9a-fA-F:.]+)", msg)
    return match.group(1) if match else None
