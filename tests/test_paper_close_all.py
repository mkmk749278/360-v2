"""Tests for the user-facing close-all-paper-positions action.

Two layers:

1. ``PaperOrderManager.close_all_open_positions`` — broker-level
   contract (snapshot keys, zero-move close, summary return shape,
   logging, idempotency).
2. ``POST /api/auto-mode/paper/close-all`` — HTTP wiring (auth,
   response schema, idempotent second call).

Why this matters (follow-up to PR #401)
---------------------------------------
``POST /api/auto-mode/paper/reset`` (PR #401) zeros cumulative PnL +
equity + archives ``paper_trades``, but deliberately leaves
``PaperOrderManager._positions`` untouched: the reset doctrine
preserves in-flight signals for live-broker safety.  Users running
paper-only sessions still need a one-shot "flatten my book" action
they can fire BEFORE ``/reset`` (which otherwise refuses while open
positions exist).  ``close_all_open_positions`` is that action.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Tuple
from unittest.mock import MagicMock

import pytest

from src.paper_order_manager import PaperOrderManager
from src.smc import Direction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_signal(
    *,
    signal_id: str,
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
):
    """Mirror the pattern in ``test_paper_order_manager_close_and_dca`` so
    these tests stay legible alongside the rest of the broker suite.
    """
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    sig.entry = entry
    sig.current_price = entry
    sig.stop_loss = entry * 0.99 if direction == Direction.LONG else entry * 1.01
    return sig


# ---------------------------------------------------------------------------
# Broker-level: close_all_open_positions
# ---------------------------------------------------------------------------


class TestCloseAllOpenPositions:
    async def test_closes_three_open_positions_at_zero_move(self):
        """Open 3 positions → close-all returns ``closed_count=3`` and
        a near-zero realised PnL (only round-trip fees, no price move).

        Side-effects asserted: ``_positions`` is empty, three paper_trades
        rows exist with ``close_reason="user_close_all"`` and
        ``close_price == entry``.
        """
        from src.auto_trade import trade_records

        pm = PaperOrderManager(
            starting_equity_usd=10_000.0, max_position_usd=1000.0,
        )
        sigs = [
            _make_signal(signal_id="CA-1", symbol="BTCUSDT", entry=30000.0),
            _make_signal(signal_id="CA-2", symbol="ETHUSDT", entry=2300.0),
            _make_signal(signal_id="CA-3", symbol="SOLUSDT", entry=150.0),
        ]
        for sig in sigs:
            order_id = await pm.place_market_order(sig)
            assert order_id is not None
        assert pm.open_position_count == 3

        result = await pm.close_all_open_positions("user_close_all")

        # Return-shape contract.
        assert isinstance(result, dict)
        assert result["closed_count"] == 3
        # Zero-move close → only fee costs; realised PnL strictly negative
        # but in the ~$0 neighbourhood.  Use a generous tolerance because
        # the per-position fee burden depends on the configured
        # MAX_POSITION_USD cap and Binance fee tiers — we only care that
        # the magnitude is "tiny" (no big price-PnL booked).
        assert result["realised_pnl_total"] == pytest.approx(0.0, abs=10.0)
        # Strictly non-positive — fees never produce a profit on a flat close.
        assert result["realised_pnl_total"] <= 0.0

        # Side-effect contract: book is empty.
        assert pm.open_position_count == 0
        assert pm._positions == {}

        # SQLite ledger: three rows closed with the expected reason +
        # close_price == entry (zero-move flatten).
        for sig in sigs:
            row = trade_records.get_trade(sig.signal_id)
            assert row is not None, f"missing row for {sig.signal_id}"
            assert row["close_reason"] == "user_close_all"
            assert row["close_price"] == pytest.approx(sig.entry, rel=1e-9)
            assert row["closed_at"] is not None

    async def test_empty_book_is_idempotent_no_op(self):
        """Calling on a flat book returns zero counts without side effects."""
        pm = PaperOrderManager(starting_equity_usd=10_000.0)
        result = await pm.close_all_open_positions("user_close_all")
        assert result == {"closed_count": 0, "realised_pnl_total": 0.0}
        assert pm.open_position_count == 0

    async def test_second_call_is_idempotent(self):
        """Calling close-all twice in a row: first drains the book, second
        is a no-op.  Matches the HTTP-level idempotency contract."""
        pm = PaperOrderManager(
            starting_equity_usd=10_000.0, max_position_usd=1000.0,
        )
        sig = _make_signal(signal_id="CA-X", entry=30000.0)
        await pm.place_market_order(sig)
        first = await pm.close_all_open_positions("user_close_all")
        assert first["closed_count"] == 1
        second = await pm.close_all_open_positions("user_close_all")
        assert second == {"closed_count": 0, "realised_pnl_total": 0.0}

    async def test_does_not_raise_when_positions_mutate_during_iteration(self):
        """Snapshot semantics: we iterate a *copy* of the keys so concurrent
        close_full calls (which pop from self._positions) can't trip
        ``RuntimeError: dictionary changed size during iteration``."""
        pm = PaperOrderManager(
            starting_equity_usd=10_000.0, max_position_usd=1000.0,
        )
        for i in range(5):
            sig = _make_signal(signal_id=f"CA-S-{i}", entry=30000.0 + i)
            await pm.place_market_order(sig)
        # If the implementation iterated self._positions directly this
        # would raise; the snapshot+pop pattern keeps us safe.
        result = await pm.close_all_open_positions("user_close_all")
        assert result["closed_count"] == 5

    async def test_custom_reason_propagates_to_trade_records(self):
        """The reason string lands in the paper_trades ledger — useful for
        future audit/UX work (e.g. "user_panic_close")."""
        from src.auto_trade import trade_records

        pm = PaperOrderManager(
            starting_equity_usd=10_000.0, max_position_usd=1000.0,
        )
        sig = _make_signal(signal_id="CA-R", entry=30000.0)
        await pm.place_market_order(sig)
        await pm.close_all_open_positions("user_panic_close")
        row = trade_records.get_trade("CA-R")
        assert row is not None
        assert row["close_reason"] == "user_panic_close"


# ---------------------------------------------------------------------------
# HTTP wiring: POST /api/auto-mode/paper/close-all
# ---------------------------------------------------------------------------


pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.server import build_app  # noqa: E402


class _StubRiskManager:
    open_position_count = 0
    daily_realised_pnl_usd = 0.0
    daily_loss_pct = 0.0
    daily_kill_tripped = False
    manual_paused = False
    current_equity_usd = 1000.0


@dataclass
class _StubEngine:
    """Mirror ``tests/test_api_trades.py``'s engine stub, but with a real
    :class:`PaperOrderManager` so the close-all endpoint exercises the
    actual broker code path instead of a recorded-call mock."""

    _risk_manager: _StubRiskManager = field(default_factory=_StubRiskManager)
    _order_manager: PaperOrderManager = field(
        default_factory=lambda: PaperOrderManager(
            starting_equity_usd=10_000.0, max_position_usd=1000.0,
        )
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
def owner_client(engine: _StubEngine) -> TestClient:
    from src.api.auth import mint_token, OWNER_TIER
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET, tier=OWNER_TIER)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def non_owner_client(engine: _StubEngine) -> TestClient:
    from src.api.auth import mint_token
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


class TestPaperCloseAllEndpoint:
    def test_requires_owner(self, non_owner_client: TestClient) -> None:
        """Non-owner JWT is rejected (mirrors ``/reset`` auth)."""
        resp = non_owner_client.post("/api/auto-mode/paper/close-all")
        assert resp.status_code == 403

    async def test_happy_path_returns_expected_shape(
        self, owner_client: TestClient, engine: _StubEngine,
    ) -> None:
        """Open three positions on the real broker, then hit the endpoint —
        response should report ``closed_count=3`` and ``ok=true``.

        Note: TestClient is sync-only; we await ``place_market_order``
        directly on the broker before invoking the HTTP call (the
        endpoint handler is async and TestClient drives the event loop
        for it internally).
        """
        pm = engine._order_manager
        for i, (sid, sym, ent) in enumerate(
            [
                ("HTTP-CA-1", "BTCUSDT", 30000.0),
                ("HTTP-CA-2", "ETHUSDT", 2300.0),
                ("HTTP-CA-3", "SOLUSDT", 150.0),
            ]
        ):
            await pm.place_market_order(
                _make_signal(signal_id=sid, symbol=sym, entry=ent)
            )
        assert pm.open_position_count == 3

        resp = owner_client.post("/api/auto-mode/paper/close-all")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ok"] is True
        assert body["closed_count"] == 3
        # Zero-move flatten → small (fee-only) PnL, strictly non-positive.
        assert body["realised_pnl_total"] <= 0.0
        assert body["realised_pnl_total"] == pytest.approx(0.0, abs=10.0)
        # Broker book is empty post-call.
        assert pm.open_position_count == 0

    def test_empty_book_returns_zero(
        self, owner_client: TestClient, engine: _StubEngine,
    ) -> None:
        """Fresh engine, no positions opened — endpoint reports zero counts
        without raising."""
        assert engine._order_manager.open_position_count == 0
        resp = owner_client.post("/api/auto-mode/paper/close-all")
        assert resp.status_code == 200
        body = resp.json()
        assert body == {
            "ok": True,
            "closed_count": 0,
            "realised_pnl_total": 0.0,
        }

    async def test_idempotent_second_call_returns_zero(
        self, owner_client: TestClient, engine: _StubEngine,
    ) -> None:
        """Two consecutive HTTP calls: first drains the book, second is a
        no-op.  This is the user-facing idempotency the app's "Close all
        positions" button relies on so double-taps don't error."""
        pm = engine._order_manager
        await pm.place_market_order(
            _make_signal(signal_id="HTTP-IDEM", entry=30000.0)
        )

        first = owner_client.post("/api/auto-mode/paper/close-all").json()
        assert first["closed_count"] == 1

        second = owner_client.post("/api/auto-mode/paper/close-all").json()
        assert second["closed_count"] == 0
        assert second["realised_pnl_total"] == 0.0
        assert second["ok"] is True
