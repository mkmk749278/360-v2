"""Integration tests for the ``/api/auto-trade/*`` endpoint surface.

These exercise the FastAPI handlers end-to-end with the static admin
token bypass — the proxy itself is mocked at the aiohttp layer so no
real Binance traffic flies.

Why static-token bypass + TestClient: the JWT path is already covered
by ``tests/test_api_smoke.py``; here we focus on the new endpoint
shapes (request bodies, response models, error→HTTP mapping) without
re-validating the auth dependency for every test.
"""

from __future__ import annotations

import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import pytest
from fastapi.testclient import TestClient

from src.api.server import build_app
from src.auto_trade.binance_keys_store import BinanceKeysStore
from src.auto_trade.binance_proxy import BinanceProxyClient


_ADMIN = "admin-token"
_AUTH = {"Authorization": f"Bearer {_ADMIN}"}


# ---------------------------------------------------------------------------
# Test harness — identical pattern to test_binance_proxy.py
# ---------------------------------------------------------------------------


@dataclass
class _FakeResponse:
    status: int
    body: Any

    async def text(self) -> str:
        if isinstance(self.body, (dict, list)):
            return json.dumps(self.body)
        return str(self.body)

    async def json(self, content_type=None) -> Any:  # noqa: ARG002
        return self.body


class _FakeSession:
    def __init__(self) -> None:
        self.calls: List[tuple] = []
        self.responses: Dict[tuple, List[_FakeResponse]] = {}
        self.closed = False

    def queue(self, method: str, path: str, status: int, body: Any) -> None:
        self.responses.setdefault((method.upper(), path), []).append(
            _FakeResponse(status=status, body=body)
        )

    @asynccontextmanager
    async def request(self, method: str, url: str, *, headers=None):
        from urllib.parse import urlparse
        self.calls.append((method.upper(), urlparse(url).path, dict(headers or {})))
        responses = self.responses.get((method.upper(), urlparse(url).path), [])
        if not responses:
            raise AssertionError(f"no queued response for {method} {urlparse(url).path}")
        yield responses.pop(0)

    @asynccontextmanager
    async def get(self, url: str, **_):
        from urllib.parse import urlparse
        self.calls.append(("GET", urlparse(url).path, {}))
        responses = self.responses.get(("GET", urlparse(url).path), [])
        if not responses:
            raise AssertionError(f"no queued response for GET {urlparse(url).path}")
        yield responses.pop(0)

    async def close(self) -> None:
        self.closed = True


def _make_app(tmp_path: Path) -> tuple[TestClient, _FakeSession, BinanceKeysStore]:
    """Build a FastAPI app with the proxy wired to a fake aiohttp session."""
    db = tmp_path / "lumin.sqlite"
    store = BinanceKeysStore(str(db), encryption_secret="endpoint-test-secret-aaaaa")
    # Drop FK clause (no users table in test scope)
    store._conn.execute("DROP TABLE user_binance_keys")
    store._conn.execute(
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
    session = _FakeSession()
    proxy = BinanceProxyClient(store, session=session)  # type: ignore[arg-type]
    engine = SimpleNamespace(
        _boot_time=0.0, telegram=None,
        router=SimpleNamespace(active_signals={}),
    )
    app = build_app(
        engine,
        jwt_secret="",
        static_token=_ADMIN,
        allow_static=True,
        binance_keys_store=store,
        binance_proxy=proxy,
    )
    return TestClient(app), session, store


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestKeysUploadVerifyFlow:
    def test_upload_with_successful_verify_returns_verified_true(self, tmp_path):
        client, session, store = _make_app(tmp_path)
        session.queue("GET", "/fapi/v2/account", 200, {
            "totalWalletBalance": "1000", "totalUnrealizedProfit": "0",
            "totalMarginBalance": "0", "availableBalance": "1000",
            "maxWithdrawAmount": "1000", "positions": [],
        })
        r = client.post(
            "/api/auto-trade/keys",
            json={"api_key": "abcdefgh-key", "api_secret": "xyz12345-secret", "testnet": False},
            headers=_AUTH,
        )
        assert r.status_code == 200, r.json()
        body = r.json()
        assert body["verified"] is True
        assert body["last_verified_at"] is not None
        # Key stored — store.has() proves persistence.
        assert store.has(1) is True

    def test_upload_with_ip_error_persists_but_reports_unverified(self, tmp_path):
        """Cellular-IP case: keys saved, but Binance returns -2015.  App
        UI shows "Verification failed: IP not whitelisted" with the
        offending IP — user knows exactly what to fix."""
        client, session, store = _make_app(tmp_path)
        session.queue("GET", "/fapi/v2/account", 401, {
            "code": -2015,
            "msg": "Invalid API-key, IP, or permissions for action, request ip: 106.208.102.133",
        })
        r = client.post(
            "/api/auto-trade/keys",
            json={"api_key": "abcdefgh-key", "api_secret": "xyz12345-secret"},
            headers=_AUTH,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["verified"] is False
        assert body["error_code"] == -2015
        assert body["request_ip_seen_by_binance"] == "106.208.102.133"
        # Keys are still stored — user can retry verify after fixing.
        assert store.has(1) is True

    def test_upload_rejects_too_short_inputs(self, tmp_path):
        client, _session, _store = _make_app(tmp_path)
        r = client.post(
            "/api/auto-trade/keys",
            json={"api_key": "x", "api_secret": "y"},
            headers=_AUTH,
        )
        assert r.status_code == 422  # Pydantic min_length

    def test_status_when_no_keys_stored(self, tmp_path):
        client, _session, _store = _make_app(tmp_path)
        r = client.get("/api/auto-trade/keys/status", headers=_AUTH)
        assert r.status_code == 200
        assert r.json() == {
            "stored": False,
            "testnet": False,
            "last_verified_at": None,
            "last_used_at": None,
            "created_at": None,
            "updated_at": None,
        }

    def test_status_after_upload_shows_stored_true(self, tmp_path):
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk", testnet=True)
        r = client.get("/api/auto-trade/keys/status", headers=_AUTH)
        assert r.status_code == 200
        body = r.json()
        assert body["stored"] is True
        assert body["testnet"] is True
        # Critical: status NEVER returns key material
        assert "api_key" not in body
        assert "api_secret" not in body

    def test_delete_removes_keys(self, tmp_path):
        client, _session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        assert store.has(1)
        r = client.delete("/api/auto-trade/keys", headers=_AUTH)
        assert r.status_code == 200
        assert r.json() == {"cleared": True}
        assert not store.has(1)

    def test_verify_endpoint_independent_of_upload(self, tmp_path):
        """``POST /api/auto-trade/keys/verify`` re-tests stored keys.
        Useful after the user fixes Binance allowlist."""
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 200, {
            "totalWalletBalance": "5000", "totalUnrealizedProfit": "0",
            "totalMarginBalance": "0", "availableBalance": "5000",
            "maxWithdrawAmount": "5000", "positions": [],
        })
        r = client.post("/api/auto-trade/keys/verify", headers=_AUTH)
        assert r.status_code == 200
        assert r.json()["verified"] is True


class TestEquityAndPositions:
    def test_equity_returns_account_fields(self, tmp_path):
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 200, {
            "totalWalletBalance": "1234.56", "totalUnrealizedProfit": "10.0",
            "totalMarginBalance": "100.0", "availableBalance": "1100.0",
            "maxWithdrawAmount": "1000.0", "positions": [
                {"symbol": "ETHUSDT", "positionAmt": "0.5"},
            ],
        })
        r = client.get("/api/auto-trade/equity", headers=_AUTH)
        assert r.status_code == 200
        body = r.json()
        assert body["total_wallet_balance"] == 1234.56
        assert body["open_position_count"] == 1

    def test_equity_returns_404_when_no_keys(self, tmp_path):
        """Per the -9001 → 404 mapping in _proxy_error_to_http."""
        client, _session, _store = _make_app(tmp_path)
        r = client.get("/api/auto-trade/equity", headers=_AUTH)
        assert r.status_code == 404
        body = r.json()["detail"]
        assert body["code"] == -9001

    def test_equity_returns_401_on_binance_ip_error(self, tmp_path):
        """-2015 → 401 with full error payload preserved."""
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/account", 401, {
            "code": -2015,
            "msg": "Invalid API-key, IP, or permissions for action, request ip: 1.2.3.4",
        })
        r = client.get("/api/auto-trade/equity", headers=_AUTH)
        assert r.status_code == 401
        body = r.json()["detail"]
        assert body["code"] == -2015
        assert body["request_ip"] == "1.2.3.4"

    def test_positions_returns_nonzero_only(self, tmp_path):
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/positionRisk", 200, [
            {"symbol": "ETHUSDT", "positionAmt": "0.5", "entryPrice": "2300",
             "markPrice": "2310", "unRealizedProfit": "5.0", "leverage": "10",
             "marginType": "isolated"},
            {"symbol": "BTCUSDT", "positionAmt": "0", "entryPrice": "0",
             "markPrice": "0", "unRealizedProfit": "0", "leverage": "1",
             "marginType": "cross"},
        ])
        r = client.get("/api/auto-trade/positions", headers=_AUTH)
        assert r.status_code == 200
        body = r.json()
        assert len(body["positions"]) == 1
        assert body["positions"][0]["symbol"] == "ETHUSDT"
        assert body["positions"][0]["side"] == "LONG"


class TestOrderPlacement:
    def test_place_market_order_round_trips(self, tmp_path):
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        session.queue("POST", "/fapi/v1/order", 200, {
            "orderId": 999, "symbol": "ETHUSDT", "side": "BUY",
            "type": "MARKET", "status": "FILLED",
            "executedQty": "0.5", "avgPrice": "2300", "reduceOnly": False,
        })
        r = client.post(
            "/api/auto-trade/order",
            json={
                "symbol": "ETHUSDT", "side": "BUY", "type": "MARKET",
                "quantity": 0.5,
            },
            headers=_AUTH,
        )
        assert r.status_code == 200, r.json()
        body = r.json()
        assert body["order_id"] == 999
        assert body["status"] == "FILLED"
        assert body["executed_qty"] == 0.5

    def test_close_returns_closed_false_when_no_position(self, tmp_path):
        client, session, store = _make_app(tmp_path)
        store.set(1, "ak", "sk")
        session.queue("GET", "/fapi/v2/positionRisk", 200, [])
        r = client.post(
            "/api/auto-trade/close",
            json={"symbol": "ETHUSDT"},
            headers=_AUTH,
        )
        assert r.status_code == 200
        assert r.json() == {"closed": False, "symbol": "ETHUSDT", "order": None}


class TestUnconfiguredProxy:
    def test_endpoints_503_when_keys_store_not_wired(self, tmp_path):
        """No BINANCE_KEY_ENCRYPTION_SECRET → every proxy endpoint
        returns 503 with a clear actionable message."""
        engine = SimpleNamespace(
            _boot_time=0.0, telegram=None,
            router=SimpleNamespace(active_signals={}),
        )
        app = build_app(
            engine,
            jwt_secret="",
            static_token=_ADMIN,
            allow_static=True,
            binance_keys_store=None,
            binance_proxy=None,
        )
        client = TestClient(app)
        for method, path, payload in (
            ("POST", "/api/auto-trade/keys",
             {"api_key": "abcdefghij", "api_secret": "abcdefghij"}),
            ("GET", "/api/auto-trade/keys/status", None),
            ("POST", "/api/auto-trade/keys/verify", None),
            ("GET", "/api/auto-trade/equity", None),
            ("GET", "/api/auto-trade/positions", None),
        ):
            if method == "GET":
                r = client.get(path, headers=_AUTH)
            else:
                r = client.post(path, json=payload, headers=_AUTH)
            assert r.status_code == 503, (path, r.status_code, r.json())
            assert "BINANCE_KEY_ENCRYPTION_SECRET" in r.json()["detail"]
