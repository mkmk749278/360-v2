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


def _wire_user_store_with_owner_subscription(tmp_path) -> None:
    """Set up a singleton UserStore + UserOverridesStore with the owner
    (uid=1) on an active paper subscription so existing /api/trades tests
    that seed trades see them via the per-user filter.

    Tests of the new fresh-account behaviour explicitly skip this wiring
    by clearing the singletons (see TestPerUserVisibility below).
    """
    from src.api import user_overrides as _uo, users as _users
    db = tmp_path / "lumin.sqlite"
    us = _users.UserStore(db)
    us.get_or_create_by_phone("+15550000001")  # owner_id=1
    _users.set_singleton(us)
    store = _uo.UserOverridesStore(db)
    _uo.set_singleton(store)
    # Open paper subscription for owner so seeded trades are visible.
    store.update_auto_trade(1, {"mode": "paper"})


@pytest.fixture(autouse=True)
def _reset_singletons(tmp_path):
    """Ensure no singleton leakage between tests; wire owner subscription
    by default so the bulk of tests don't need to repeat the dance."""
    from src.api import user_overrides as _uo, users as _users
    _uo.clear_singleton()
    _users.set_singleton(None)
    _wire_user_store_with_owner_subscription(tmp_path)
    yield
    _uo.clear_singleton()
    _users.set_singleton(None)


@pytest.fixture
def client(engine: _StubEngine) -> TestClient:
    # Use a user-id token so the per-user filter resolves to uid=1 (which
    # the autouse fixture above has opened a paper subscription for).
    # Pre-2026-05-23 these tests used anonymous device tokens, but the
    # /api/trades endpoint now requires a user_id to look up subscription
    # windows.
    from src.api.auth import mint_token
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET, sub="user-1")
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def owner_client(engine: _StubEngine) -> TestClient:
    from src.api.auth import mint_token, OWNER_TIER
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET, sub="user-1", tier=OWNER_TIER)
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


# ---------------------------------------------------------------------------
# Per-user visibility (2026-05-23 fix for fresh-account bug)
# ---------------------------------------------------------------------------


class TestPerUserVisibility:
    """The bug fix: fresh accounts must not see prior engine ledger data.

    These tests intentionally do NOT use the autouse owner-subscription
    wiring above — they exercise the bare per-user-filter behaviour
    directly.
    """

    def test_user_with_no_subscription_sees_empty(
        self, engine: _StubEngine, tmp_path
    ) -> None:
        """A user who has never enabled paper sees zero trades, even when
        the engine ledger has rows. This is the headline bug fix."""
        # Seed the engine ledger.
        from src.auto_trade import trade_records
        trade_records.open_trade(
            signal_id="OPERATOR-1", symbol="BTCUSDT", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="OPERATOR-1", close_reason="tp1",
            close_price=101.0, gross_pnl_usd=1.0, fees_usd=0.05,
            net_pnl_usd=0.95,
        )
        # Wire a fresh user (uid=2) who has NEVER enabled paper.
        from src.api import user_overrides as _uo, users as _users
        store = _uo.get_singleton()
        us = _users.get_singleton()
        us.get_or_create_by_phone("+15550000002")  # uid=2 — never enabled paper
        # User 1 (set up by autouse fixture) DOES have a subscription, so
        # the operator/uid=1 view should still see the trade. uid=2 must not.
        from src.api.auth import mint_token
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        token_fresh = mint_token(secret=_TEST_SECRET, sub="user-2")
        fresh_client = TestClient(
            app, headers={"Authorization": f"Bearer {token_fresh}"}
        )
        body = fresh_client.get("/api/trades").json()
        assert body == {"items": [], "total": 0}, (
            "fresh user must not see operator's prior paper trades"
        )

    def test_user_sees_only_trades_in_their_window(
        self, engine: _StubEngine
    ) -> None:
        """A user who enables paper at T sees trades closed at >= T,
        not trades that closed before they enabled."""
        from src.api import user_overrides as _uo, users as _users
        store = _uo.get_singleton()
        us = _users.get_singleton()
        us.get_or_create_by_phone("+15550000003")  # uid=2
        from src.auto_trade import trade_records
        # Seed a PRE-subscription trade.
        trade_records.open_trade(
            signal_id="PRE-1", symbol="ETHUSDT", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="PRE-1", close_reason="tp1", close_price=101.0,
            gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
        )
        # Now uid=2 enables paper.
        store.update_auto_trade(2, {"mode": "paper"})
        # Seed a POST-subscription trade.
        trade_records.open_trade(
            signal_id="POST-1", symbol="ETHUSDT", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="POST-1", close_reason="tp1", close_price=101.0,
            gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
        )
        from src.api.auth import mint_token
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        token = mint_token(secret=_TEST_SECRET, sub="user-2")
        client = TestClient(app, headers={"Authorization": f"Bearer {token}"})
        body = client.get("/api/trades").json()
        ids = {item["signal_id"] for item in body["items"]}
        assert "POST-1" in ids
        assert "PRE-1" not in ids
        assert body["total"] == 1

    def test_reset_mine_carves_fresh_window(
        self, engine: _StubEngine
    ) -> None:
        """POST /api/auto-mode/paper/reset-mine starts a fresh subscription
        window — trades closed before the reset disappear from the user's
        view (without affecting other users)."""
        from src.api.auth import mint_token
        from src.auto_trade import trade_records
        # Seed a pre-reset trade visible to uid=1 (autouse-subscribed).
        trade_records.open_trade(
            signal_id="PRE-RESET", symbol="BTCUSDT", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="PRE-RESET", close_reason="tp1", close_price=101.0,
            gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
        )
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        token = mint_token(secret=_TEST_SECRET, sub="user-1")
        client = TestClient(app, headers={"Authorization": f"Bearer {token}"})
        # Visible before reset.
        body = client.get("/api/trades").json()
        assert body["total"] == 1
        # Reset-mine.
        resp = client.post("/api/auto-mode/paper/reset-mine")
        assert resp.status_code == 200
        new_started_at = resp.json()["new_started_at"]
        assert new_started_at  # ISO stamp
        # Pre-reset trade now invisible (closed_at < new_started_at).
        body = client.get("/api/trades").json()
        assert body == {"items": [], "total": 0}, (
            "after reset-mine the user must see no prior trades"
        )

    def test_reset_mine_does_not_affect_other_users(
        self, engine: _StubEngine
    ) -> None:
        """uid=1 calling reset-mine must not affect uid=2's visibility."""
        from src.api import user_overrides as _uo, users as _users
        from src.api.auth import mint_token
        from src.auto_trade import trade_records
        store = _uo.get_singleton()
        us = _users.get_singleton()
        us.get_or_create_by_phone("+15550000004")  # uid=2
        store.update_auto_trade(2, {"mode": "paper"})
        # Both users have active subscriptions now; seed a shared trade.
        trade_records.open_trade(
            signal_id="SHARED", symbol="BTCUSDT", side="long",
            entry=100.0, qty=1.0, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="SHARED", close_reason="tp1", close_price=101.0,
            gross_pnl_usd=1.0, fees_usd=0.05, net_pnl_usd=0.95,
        )
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        token_1 = mint_token(secret=_TEST_SECRET, sub="user-1")
        token_2 = mint_token(secret=_TEST_SECRET, sub="user-2")
        client_1 = TestClient(app, headers={"Authorization": f"Bearer {token_1}"})
        client_2 = TestClient(app, headers={"Authorization": f"Bearer {token_2}"})
        assert client_1.get("/api/trades").json()["total"] == 1
        assert client_2.get("/api/trades").json()["total"] == 1
        # uid=1 resets.
        client_1.post("/api/auto-mode/paper/reset-mine")
        # uid=1 now blind; uid=2 still sees the shared trade.
        assert client_1.get("/api/trades").json() == {"items": [], "total": 0}
        assert client_2.get("/api/trades").json()["total"] == 1
