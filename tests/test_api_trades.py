"""FastAPI tests for the new ``/api/trades`` and
``/api/auto-mode/paper/reset`` endpoints (paper-trade visibility,
2026-05-16).

Builds the app against a stub engine mirroring the surface of
``tests/api/test_api_smoke.py`` — just enough state so the
auto-mode read-paths + the new endpoints round-trip cleanly.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.server import build_app  # noqa: E402


# ---------------------------------------------------------------------------
# Minimal stub engine — just enough surface for the endpoints under test.
# ---------------------------------------------------------------------------


class _StubRiskManager:
    open_position_count = 0
    daily_realised_pnl_usd = 0.0
    daily_loss_pct = 0.0
    daily_kill_tripped = False
    manual_paused = False
    current_equity_usd = 1000.0


class _StubPaperOrderManager:
    """Surfaces the methods the reset endpoint touches.

    The reset endpoint short-circuits on ``open_position_count > 0`` so
    tests of the happy path keep this at 0.  The ``reset_state``
    method just records the call so we can assert it was invoked.
    """

    _starting_equity = 1000.0
    open_position_count = 0
    current_equity_usd = 1000.0  # property-equivalent — real broker computes
    reset_state_calls = 0

    def reset_state(self) -> None:
        type(self).reset_state_calls += 1


@dataclass
class _StubEngine:
    _risk_manager: _StubRiskManager = field(default_factory=_StubRiskManager)
    _order_manager: _StubPaperOrderManager = field(
        default_factory=_StubPaperOrderManager
    )
    _signal_history: list = field(default_factory=list)
    _current_auto_mode: str = "paper"
    _boot_time: float = field(default_factory=time.monotonic)

    @property
    def router(self):
        class _R:
            active_signals: Dict = {}
        return _R()

    def get_auto_execution_status(self) -> Dict[str, object]:
        rm = self._risk_manager
        return {
            "mode": self._current_auto_mode,
            "open_positions": rm.open_position_count,
            "daily_pnl_usd": rm.daily_realised_pnl_usd,
            "daily_loss_pct": rm.daily_loss_pct,
            "daily_kill_tripped": rm.daily_kill_tripped,
            "manual_paused": rm.manual_paused,
            "current_equity_usd": rm.current_equity_usd,
        }

    def set_auto_execution_mode(self, new_mode: str) -> Tuple[bool, str]:
        self._current_auto_mode = new_mode
        return True, f"mode → {new_mode}"


_TEST_SECRET = "smoke-test-secret-x" * 4


@pytest.fixture
def engine() -> _StubEngine:
    return _StubEngine()


@pytest.fixture
def client(engine: _StubEngine) -> TestClient:
    from src.api.auth import mint_token
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def owner_client(engine: _StubEngine) -> TestClient:
    from src.api.auth import mint_token, OWNER_TIER
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET, tier=OWNER_TIER)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


# ---------------------------------------------------------------------------
# /api/trades
# ---------------------------------------------------------------------------


class TestListTradesEndpoint:
    def test_empty_returns_zero_total(self, client: TestClient) -> None:
        resp = client.get("/api/trades")
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"items": [], "total": 0}

    def test_returns_seeded_trades(self, client: TestClient) -> None:
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="API-1", symbol="BTCUSDT", side="long",
            entry=30000.0, qty=0.01, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="API-1", close_reason="tp1",
            close_price=30300.0, gross_pnl_usd=3.0,
            fees_usd=0.18, net_pnl_usd=2.82,
        )
        resp = client.get("/api/trades")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total"] == 1
        assert len(body["items"]) == 1
        item = body["items"][0]
        assert item["signal_id"] == "API-1"
        assert item["symbol"] == "BTCUSDT"
        assert item["close_reason"] == "tp1"
        # ROI = 2.82 / 30 (margin) * 100 = 9.4
        assert item["roi_pct_on_margin"] == pytest.approx(9.4, rel=1e-3)

    def test_pagination(self, client: TestClient) -> None:
        from src.auto_trade import trade_records
        for i in range(5):
            sid = f"P-{i}"
            trade_records.open_trade(
                signal_id=sid, symbol="BTCUSDT", side="long",
                entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
            )
            trade_records.close_trade(
                signal_id=sid, close_reason="tp1", close_price=101.0,
                gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
            )
        page1 = client.get("/api/trades?limit=2&offset=0").json()
        page2 = client.get("/api/trades?limit=2&offset=2").json()
        assert page1["total"] == 5
        assert page2["total"] == 5
        assert len(page1["items"]) == 2
        assert len(page2["items"]) == 2
        assert {it["signal_id"] for it in page1["items"]} != {
            it["signal_id"] for it in page2["items"]
        }

    def test_symbol_filter(self, client: TestClient) -> None:
        from src.auto_trade import trade_records
        for sid, sym in [("X-BTC", "BTCUSDT"), ("X-ETH", "ETHUSDT")]:
            trade_records.open_trade(
                signal_id=sid, symbol=sym, side="long",
                entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
            )
            trade_records.close_trade(
                signal_id=sid, close_reason="tp1", close_price=101.0,
                gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
            )
        eth = client.get("/api/trades?symbol=ETHUSDT").json()
        assert eth["total"] == 1
        assert eth["items"][0]["symbol"] == "ETHUSDT"

    def test_live_mode_returns_400(self, client: TestClient) -> None:
        resp = client.get("/api/trades?mode=live")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# /api/auto-mode/paper/reset
# ---------------------------------------------------------------------------


class TestPaperResetEndpoint:
    def test_requires_owner(self, client: TestClient) -> None:
        """Non-owner JWT can READ /api/trades but cannot POST reset."""
        resp = client.post("/api/auto-mode/paper/reset")
        # Owner-required dependency → 403.
        assert resp.status_code == 403

    def test_happy_path(
        self, owner_client: TestClient, engine: _StubEngine
    ) -> None:
        from src.auto_trade import pnl_history, trade_records
        # Seed daily-bucket history + a closed trade.
        pnl_history.record_close("paper", 12.84)
        trade_records.open_trade(
            signal_id="RESET-1", symbol="BTCUSDT", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="RESET-1", close_reason="tp1", close_price=101.0,
            gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
        )
        # Sanity: store starts populated.
        assert pnl_history.get_daily("paper") != 0.0
        assert trade_records.count_trades() == 1

        resp = owner_client.post("/api/auto-mode/paper/reset")
        assert resp.status_code == 200
        body = resp.json()
        assert body["pnl_buckets_cleared"] >= 1
        assert body["trades_archived"] == 1
        assert body["starting_equity_usd"] == pytest.approx(1000.0)
        # Broker.reset_state() was called.
        assert _StubPaperOrderManager.reset_state_calls >= 1
        # Live store is empty post-archive.
        assert trade_records.count_trades() == 0
        # Daily bucket cleared.
        assert pnl_history.get_daily("paper") == 0.0
        # Reset class counter so subsequent tests in the same suite
        # don't see leaked state from this assertion.
        _StubPaperOrderManager.reset_state_calls = 0

    def test_refuses_with_open_positions(
        self, owner_client: TestClient, engine: _StubEngine
    ) -> None:
        """The reset endpoint must refuse while open positions exist —
        clearing equity while in-flight trades reference it would
        orphan the engine's lifecycle state."""
        engine._order_manager.open_position_count = 1
        resp = owner_client.post("/api/auto-mode/paper/reset")
        assert resp.status_code == 409
        assert "open positions" in resp.json()["detail"].lower()
        engine._order_manager.open_position_count = 0
