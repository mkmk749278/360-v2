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




# ---------------------------------------------------------------------------
# Per-user visibility — Trade-tab header + open-positions + Pulse
# (PR #503, 2026-05-26 — extends 2026-05-23's /api/trades coverage)
# ---------------------------------------------------------------------------


class TestPerUserAutoModeAndPositions:
    """A fresh user enabling paper mode for the first time must see:

    * ``GET /api/auto-mode`` → equity = ``PAPER_STARTING_EQUITY`` ($1000),
      open_positions=0, daily/weekly/monthly/total = $0
    * ``GET /api/positions`` → empty list
    * ``GET /api/pulse``     → today_pnl_usd=0, open_positions=0

    Pre-PR-#503 the Trade-tab header inherited the engine-wide paper
    book — the operator's $963.97 equity + 4 open positions + −$36.03
    monthly PnL leaked onto a brand-new install (owner-reported via
    screenshot 2026-05-26).  These tests pin the bug fix.
    """

    def _build_paper_engine(self) -> "_PaperEngineWithRouter":
        """Build a per-test engine with a persistent router + paper
        order-manager wired so the per-user filter sees real state.

        The shared ``_StubEngine`` in this module exposes ``router``
        as a property that returns a fresh empty dict each call —
        that's fine for endpoints that read but never mutate, but
        the new paper-visibility tests need to seed
        ``active_signals`` and have those rows survive subsequent
        reads. Use a dedicated, mutation-friendly engine here.
        """
        return _PaperEngineWithRouter()

    def _seed_engine_wide_book(
        self, engine: "_PaperEngineWithRouter",
    ) -> None:
        """Operator-side book the engine has been running before our
        fresh user signed up. Closed trades + an open router signal."""
        from datetime import datetime as _dt, timedelta as _td, timezone as _tz
        from src.auto_trade import trade_records
        # Closed trade — engine-wide ledger
        trade_records.open_trade(
            signal_id="OP-PRE-1", symbol="ETHUSDT", side="long",
            entry=2300.0, qty=0.05, leverage=10.0, position_size_pct=2.0,
        )
        trade_records.close_trade(
            signal_id="OP-PRE-1", close_reason="sl",
            close_price=2280.0, gross_pnl_usd=-1.0, fees_usd=0.05,
            net_pnl_usd=-1.05,
        )
        # Open router signal pre-dating our fresh user — must NOT show
        # in their /api/positions response.
        from tests.api.test_api_smoke import _Direction, _StubSignal
        old_open = _StubSignal(
            signal_id="OP-OPEN-1",
            symbol="BTCUSDT",
            direction=_Direction("LONG"),
            entry=78000.0,
            stop_loss=77500.0,
            tp1=78400.0,
            tp2=78700.0,
            current_price=78100.0,
            pnl_pct=0.13,
            timestamp=_dt.now(_tz.utc) - _td(hours=2),
            dispatch_timestamp=_dt.now(_tz.utc) - _td(hours=2),
            qty=0.01,
        )
        engine.router.active_signals[old_open.signal_id] = old_open

    def _enable_paper_for_fresh_user(self, phone: str) -> int:
        """Wire a brand-new user (uid>=2) and flip their mode → paper.
        Returns the user_id.  The window opens at 'now', AFTER the
        engine-wide pre-existing trades + router signals."""
        from src.api import user_overrides as _uo, users as _users
        store = _uo.get_singleton()
        us = _users.get_singleton()
        user = us.get_or_create_by_phone(phone)
        store.update_auto_trade(user.user_id, {"mode": "paper"})
        return user.user_id

    def _client_for(self, app, user_id: int) -> TestClient:
        from src.api.auth import mint_token
        token = mint_token(secret=_TEST_SECRET, sub=f"user-{user_id}")
        return TestClient(app, headers={"Authorization": f"Bearer {token}"})

    def test_fresh_user_auto_mode_shows_starting_equity_and_zero_pnl(
        self, engine: _StubEngine,
    ) -> None:
        """The headline screenshot bug: brand-new install + paper mode
        must show equity=$1000 + zero PnL across every window, NOT the
        operator's accumulated −$36.03 / $963.97."""
        engine = self._build_paper_engine()
        self._seed_engine_wide_book(engine)
        fresh_uid = self._enable_paper_for_fresh_user("+15558880001")
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        client = self._client_for(app, fresh_uid)

        body = client.get("/api/auto-mode").json()
        assert body["mode"] == "paper"
        assert body["current_equity_usd"] == pytest.approx(1000.0), (
            f"fresh user must see baseline equity, got {body['current_equity_usd']}"
        )
        assert body["daily_pnl_usd"] == 0.0
        assert body["weekly_pnl_usd"] == 0.0
        assert body["monthly_pnl_usd"] == 0.0
        # simulated_pnl_usd = total within user's windows = 0 for fresh
        assert body.get("simulated_pnl_usd", 0.0) == 0.0
        assert body["open_positions"] == 0, (
            "fresh user must see 0 open positions — the operator's "
            "pre-signup router signal must be filtered out"
        )

    def test_fresh_user_positions_empty_despite_engine_wide_open(
        self, engine: _StubEngine,
    ) -> None:
        """Open positions opened before the user's window opened are
        invisible to that user — even though the router still tracks
        them and the engine-wide /api/positions list has rows."""
        engine = self._build_paper_engine()
        self._seed_engine_wide_book(engine)
        fresh_uid = self._enable_paper_for_fresh_user("+15558880002")
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        client = self._client_for(app, fresh_uid)
        body = client.get("/api/positions").json()
        assert body == {"items": [], "total": 0}, (
            "fresh user must see no open positions — the engine has "
            "OP-OPEN-1 active but its dispatch is pre-window"
        )

    def test_fresh_user_pulse_shows_zero_today_pnl_and_zero_open(
        self, engine: _StubEngine,
    ) -> None:
        """Pulse header counters must agree with Trade tab — both per-user."""
        engine = self._build_paper_engine()
        self._seed_engine_wide_book(engine)
        fresh_uid = self._enable_paper_for_fresh_user("+15558880003")
        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        client = self._client_for(app, fresh_uid)
        body = client.get("/api/pulse").json()
        assert body["mode"] == "paper"
        assert body["today_pnl_usd"] == 0.0
        assert body["open_positions"] == 0

    def test_post_window_position_is_visible(
        self, engine: _StubEngine,
    ) -> None:
        """Positivity test: a position opened AFTER the user's window
        opens DOES show up — confirms the filter isn't accidentally
        hiding legitimate post-signup activity."""
        from datetime import datetime as _dt, timezone as _tz
        from tests.api.test_api_smoke import _Direction, _StubSignal
        engine = self._build_paper_engine()
        # Fresh user enables paper FIRST.
        fresh_uid = self._enable_paper_for_fresh_user("+15558880004")
        # Then a post-window signal lands in the router AND in the
        # broker's positions dict (so the broker-cross-reference
        # filter doesn't drop it).
        post = _StubSignal(
            signal_id="POST-OPEN-1",
            symbol="ETHUSDT",
            direction=_Direction("LONG"),
            entry=2300.0,
            stop_loss=2280.0,
            tp1=2330.0,
            tp2=2360.0,
            current_price=2310.0,
            pnl_pct=0.43,
            timestamp=_dt.now(_tz.utc),
            dispatch_timestamp=_dt.now(_tz.utc),
            qty=0.05,
        )
        engine.router.active_signals[post.signal_id] = post

        # Ensure the stub broker's _positions dict has the same id so
        # the broker-state filter admits the row.
        class _StubBPos:
            quantity = 0.05
            closed_quantity = 0.0
        engine._order_manager._positions = {post.signal_id: _StubBPos()}

        app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
        client = self._client_for(app, fresh_uid)
        body = client.get("/api/positions").json()
        ids = {item["signal_id"] for item in body["items"]}
        assert "POST-OPEN-1" in ids, (
            "post-window position must be visible to the fresh user"
        )
        # AutoMode header counts it too.
        am = client.get("/api/auto-mode").json()
        assert am["open_positions"] == 1


# ---------------------------------------------------------------------------
# Mutation-friendly engine stub for the per-user paper visibility tests.
# Distinct from the module-level ``_StubEngine`` (which has a property-
# returning-fresh-dict ``router``) — these tests need to seed the router
# with operator-pre-existing signals and have them stick.
# ---------------------------------------------------------------------------


class _PaperEngineWithRouter:
    """Minimal engine surface for the PR #503 tests.

    * Persistent ``router.active_signals`` dict (mutable across calls).
    * ``_order_manager`` mirrors ``PaperOrderManager`` enough for
      ``build_auto_mode``'s ``_starting_equity`` + ``current_equity_usd``
      lookups.  Tests overlay ``_positions`` per-test when the
      broker-cross-reference filter needs to be exercised.
    * ``_current_auto_mode = "paper"`` so the per-user filter activates.
    """

    def __init__(self) -> None:
        from tests.api.test_api_smoke import _StubRouter
        self.router = _StubRouter({})
        self._risk_manager = _StubRiskManager()
        self._signal_history: list = []
        self._current_auto_mode = "paper"
        self._boot_time = time.monotonic()

        class _PaperOM:
            _starting_equity = 1000.0
            current_equity_usd = 1000.0
            simulated_pnl_total = 0.0
            open_position_count = 0
            # _positions deliberately absent — tests opt in by setting
            # ``engine._order_manager._positions = {...}`` per-case.

        self._order_manager = _PaperOM()

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
            "simulated_pnl_usd": getattr(
                self._order_manager, "simulated_pnl_total", 0.0,
            ),
        }

    def set_auto_execution_mode(self, new_mode: str) -> Tuple[bool, str]:
        self._current_auto_mode = new_mode
        return True, f"mode → {new_mode}"
