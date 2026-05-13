"""Tests for the server-side Binance Futures proxy + API endpoints.

The proxy is fully covered without making real Binance calls.  We
intercept ``aiohttp.ClientSession.request`` with a fake that records
the URL/signature/headers and returns canned responses — exactly what
Binance would send for each documented response shape.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

import pytest

import aiohttp

from src.auto_trade.binance_keys_store import BinanceKeysStore
from src.auto_trade.binance_proxy import (
    BinanceProxyClient,
    BinanceProxyError,
    _parse_request_ip,
)


# ---------------------------------------------------------------------------
# Test harness — fake aiohttp session that intercepts every request
# ---------------------------------------------------------------------------


@dataclass
class _FakeResponse:
    status: int
    body: Any

    async def text(self) -> str:
        if isinstance(self.body, (dict, list)):
            return json.dumps(self.body)
        return str(self.body)

    async def json(self, content_type=None) -> Any:  # noqa: ARG002 — aiohttp signature
        return self.body


class _CallRecord:
    """One captured outbound HTTP request."""

    def __init__(self, method: str, url: str, headers: Dict[str, str]) -> None:
        self.method = method
        self.url = url
        self.headers = headers


class _FakeSession:
    """aiohttp.ClientSession stand-in.  Returns the next queued response
    per method/path; records every call for assertion."""

    def __init__(self) -> None:
        self.calls: List[_CallRecord] = []
        # Map of (method, path) → list of canned responses (popped FIFO).
        self.responses: Dict[tuple, List[_FakeResponse]] = {}
        self.closed = False

    def queue(self, method: str, path: str, status: int, body: Any) -> None:
        self.responses.setdefault((method.upper(), path), []).append(
            _FakeResponse(status=status, body=body)
        )

    @asynccontextmanager
    async def request(self, method: str, url: str, *, headers=None):
        from urllib.parse import urlparse
        path = urlparse(url).path
        self.calls.append(_CallRecord(method.upper(), url, dict(headers or {})))
        responses = self.responses.get((method.upper(), path), [])
        if not responses:
            raise AssertionError(
                f"no canned response queued for {method} {path}"
            )
        yield responses.pop(0)

    @asynccontextmanager
    async def get(self, url: str, **_):
        from urllib.parse import urlparse
        path = urlparse(url).path
        self.calls.append(_CallRecord("GET", url, {}))
        responses = self.responses.get(("GET", path), [])
        if not responses:
            raise AssertionError(f"no canned response queued for GET {path}")
        yield responses.pop(0)

    async def close(self) -> None:
        self.closed = True


@pytest.fixture
def store(tmp_path: Path) -> BinanceKeysStore:
    db = tmp_path / "lumin.sqlite"
    s = BinanceKeysStore(str(db), encryption_secret="proxy-test-secret-aaaaaaaa")
    # Drop the FK on test schema so we don't have to bootstrap users.
    s._conn.execute("DROP TABLE user_binance_keys")
    s._conn.execute(
        """
        CREATE TABLE user_binance_keys (
            user_id INTEGER PRIMARY KEY,
            api_key_enc BLOB NOT NULL,
            api_secret_enc BLOB NOT NULL,
            testnet INTEGER NOT NULL DEFAULT 0,
            last_verified_at TEXT, last_used_at TEXT,
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        )
        """
    )
    return s


@pytest.fixture
def proxy(store: BinanceKeysStore):
    session = _FakeSession()
    client = BinanceProxyClient(store, session=session)  # type: ignore[arg-type]
    yield client, session, store


# ---------------------------------------------------------------------------
# Signing + transport
# ---------------------------------------------------------------------------


class TestSigning:
    @pytest.mark.asyncio
    async def test_signed_request_includes_signature_and_apikey_header(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 200, _account_body(balance=1000.0))
        await client.get_account(1)
        call = session.calls[0]
        # API key in header
        assert call.headers["X-MBX-APIKEY"] == "ak"
        # signature= present in query string
        assert "signature=" in call.url
        # timestamp + recvWindow present (mandatory for signed endpoints)
        assert "timestamp=" in call.url
        assert "recvWindow=" in call.url

    @pytest.mark.asyncio
    async def test_missing_keys_raises_with_synthetic_code(self, proxy):
        client, _session, _store = proxy
        with pytest.raises(BinanceProxyError) as ei:
            await client.get_account(99)
        assert ei.value.code == -9001  # our synthetic "no keys stored"

    @pytest.mark.asyncio
    async def test_testnet_routes_to_testnet_base(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk", testnet=True)
        session.queue("GET", "/fapi/v2/account", 200, _account_body())
        await client.get_account(1)
        assert "testnet.binancefuture.com" in session.calls[0].url

    @pytest.mark.asyncio
    async def test_mainnet_routes_to_fapi_base(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk", testnet=False)
        session.queue("GET", "/fapi/v2/account", 200, _account_body())
        await client.get_account(1)
        assert "fapi.binance.com" in session.calls[0].url


# ---------------------------------------------------------------------------
# get_account / verify
# ---------------------------------------------------------------------------


class TestGetAccount:
    @pytest.mark.asyncio
    async def test_decodes_account_fields(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 200, _account_body(
            balance=12345.67, unrealized=89.0, margin=500.0,
            available=11000.0, positions=[
                {"symbol": "ETHUSDT", "positionAmt": "0.5"},
                {"symbol": "BTCUSDT", "positionAmt": "0"},
                {"symbol": "BNBUSDT", "positionAmt": "-1.0"},
            ],
        ))
        acc = await client.get_account(1)
        assert acc.total_wallet_balance == 12345.67
        assert acc.total_unrealized_profit == 89.0
        assert acc.total_margin_balance == 500.0
        assert acc.available_balance == 11000.0
        assert acc.open_position_count == 2  # non-zero positions only

    @pytest.mark.asyncio
    async def test_verify_marks_keys_verified(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        assert store.get(1).last_verified_at is None  # type: ignore[union-attr]
        session.queue("GET", "/fapi/v2/account", 200, _account_body())
        await client.verify(1)
        assert store.get(1).last_verified_at is not None  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_get_account_stamps_last_used(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 200, _account_body())
        await client.get_account(1)
        assert store.get(1).last_used_at is not None  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_ip_restriction_error_parsed(self, proxy):
        """The classic -2015 IP-not-whitelisted error must extract the
        request IP from the message so the app can show a useful hint."""
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue(
            "GET", "/fapi/v2/account", 401,
            {"code": -2015, "msg": "Invalid API-key, IP, or permissions for action, request ip: 106.208.102.133"},
        )
        with pytest.raises(BinanceProxyError) as ei:
            await client.get_account(1)
        assert ei.value.code == -2015
        assert ei.value.http_status == 401
        assert ei.value.request_ip == "106.208.102.133"

    @pytest.mark.asyncio
    async def test_clock_skew_error_preserves_code(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue(
            "GET", "/fapi/v2/account", 400,
            {"code": -1021, "msg": "Timestamp for this request is outside of the recvWindow"},
        )
        with pytest.raises(BinanceProxyError) as ei:
            await client.get_account(1)
        assert ei.value.code == -1021

    @pytest.mark.asyncio
    async def test_non_json_response_raises_proxy_error(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 502, "<html>bad gateway</html>")
        with pytest.raises(BinanceProxyError, match="non-JSON|html"):
            await client.get_account(1)


class TestParseRequestIp:
    def test_extracts_ipv4(self):
        msg = "Invalid API-key, IP, or permissions for action, request ip: 106.208.102.133"
        assert _parse_request_ip(msg) == "106.208.102.133"

    def test_missing_returns_none(self):
        assert _parse_request_ip("some other error") is None


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


class TestGetPositions:
    @pytest.mark.asyncio
    async def test_filters_to_nonzero_and_assigns_side(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/positionRisk", 200, [
            {"symbol": "ETHUSDT", "positionAmt": "0.5", "entryPrice": "2300",
             "markPrice": "2310", "unRealizedProfit": "5.0", "leverage": "10",
             "marginType": "isolated"},
            {"symbol": "BTCUSDT", "positionAmt": "0", "entryPrice": "0",
             "markPrice": "0", "unRealizedProfit": "0", "leverage": "1",
             "marginType": "cross"},
            {"symbol": "BNBUSDT", "positionAmt": "-1.0", "entryPrice": "600",
             "markPrice": "595", "unRealizedProfit": "5.0", "leverage": "5",
             "marginType": "cross"},
        ])
        positions = await client.get_positions(1)
        assert len(positions) == 2
        eth, bnb = positions[0], positions[1]
        assert eth.symbol == "ETHUSDT" and eth.side == "LONG"
        assert bnb.symbol == "BNBUSDT" and bnb.side == "SHORT"
        assert eth.isolated is True
        assert bnb.isolated is False
        assert eth.position_amt == 0.5
        assert bnb.position_amt == -1.0


# ---------------------------------------------------------------------------
# Place / close orders
# ---------------------------------------------------------------------------


class TestPlaceOrder:
    @pytest.mark.asyncio
    async def test_market_order_omits_price_and_tif(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("POST", "/fapi/v1/order", 200, {
            "orderId": 1, "symbol": "ETHUSDT", "side": "BUY", "type": "MARKET",
            "status": "FILLED", "executedQty": "0.5", "avgPrice": "2300",
            "reduceOnly": False,
        })
        await client.place_order(
            1, symbol="ETHUSDT", side="BUY", type="MARKET", quantity=0.5,
        )
        url = session.calls[0].url
        assert "price=" not in url
        assert "timeInForce=" not in url

    @pytest.mark.asyncio
    async def test_limit_order_requires_price(self, proxy):
        client, _session, store = proxy
        store.set(1, "ak", "sk")
        with pytest.raises(BinanceProxyError, match="require a price"):
            await client.place_order(
                1, symbol="ETHUSDT", side="BUY", type="LIMIT", quantity=0.5,
            )

    @pytest.mark.asyncio
    async def test_limit_order_defaults_to_gtc(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("POST", "/fapi/v1/order", 200, _order_body())
        await client.place_order(
            1, symbol="ETHUSDT", side="BUY", type="LIMIT",
            quantity=0.5, price=2300.0,
        )
        assert "timeInForce=GTC" in session.calls[0].url

    @pytest.mark.asyncio
    async def test_reduce_only_flag_serialised(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("POST", "/fapi/v1/order", 200, _order_body())
        await client.place_order(
            1, symbol="ETHUSDT", side="SELL", type="MARKET",
            quantity=0.5, reduce_only=True,
        )
        assert "reduceOnly=true" in session.calls[0].url


class TestClosePosition:
    @pytest.mark.asyncio
    async def test_close_returns_none_when_no_position(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/positionRisk", 200, [])
        result = await client.close_position(1, symbol="ETHUSDT")
        assert result is None

    @pytest.mark.asyncio
    async def test_close_long_position_sells_reduce_only(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/positionRisk", 200, [
            {"symbol": "ETHUSDT", "positionAmt": "0.5", "entryPrice": "2300",
             "markPrice": "2310", "unRealizedProfit": "5.0", "leverage": "10",
             "marginType": "cross"},
        ])
        session.queue("POST", "/fapi/v1/order", 200, _order_body(
            side="SELL", executed_qty=0.5, reduce_only=True,
        ))
        result = await client.close_position(1, symbol="ETHUSDT")
        assert result is not None
        # Find the order POST call and verify side+reduceOnly were set.
        order_call = next(c for c in session.calls if c.method == "POST")
        assert "side=SELL" in order_call.url
        assert "reduceOnly=true" in order_call.url

    @pytest.mark.asyncio
    async def test_close_short_position_buys(self, proxy):
        client, session, store = proxy
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/positionRisk", 200, [
            {"symbol": "BNBUSDT", "positionAmt": "-1.0", "entryPrice": "600",
             "markPrice": "595", "unRealizedProfit": "5.0", "leverage": "5",
             "marginType": "cross"},
        ])
        session.queue("POST", "/fapi/v1/order", 200, _order_body(
            symbol="BNBUSDT", side="BUY", executed_qty=1.0, reduce_only=True,
        ))
        await client.close_position(1, symbol="BNBUSDT")
        order_call = next(c for c in session.calls if c.method == "POST")
        assert "side=BUY" in order_call.url


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _account_body(
    *,
    balance: float = 1000.0,
    unrealized: float = 0.0,
    margin: float = 0.0,
    available: float = 1000.0,
    positions: Optional[list] = None,
) -> dict:
    return {
        "totalWalletBalance": str(balance),
        "totalUnrealizedProfit": str(unrealized),
        "totalMarginBalance": str(margin),
        "availableBalance": str(available),
        "maxWithdrawAmount": str(available),
        "positions": positions or [],
    }


def _order_body(
    *,
    order_id: int = 12345,
    symbol: str = "ETHUSDT",
    side: str = "BUY",
    order_type: str = "MARKET",
    executed_qty: float = 0.5,
    avg_price: float = 2300.0,
    reduce_only: bool = False,
) -> dict:
    return {
        "orderId": order_id,
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "status": "FILLED",
        "executedQty": str(executed_qty),
        "avgPrice": str(avg_price),
        "reduceOnly": reduce_only,
    }
