"""Tests for cumulative paper-PnL persistence across PaperOrderManager
instances.

Doctrine: paper mode is the dashboard data source for free-tier
subscribers.  The "Paper total since boot" surface in the Lumin app
(v0.0.13 ``_ModePnlCard``) only makes sense if the cumulative number
SURVIVES engine restarts and paper↔live mode toggles.

Pre-fix, every redeploy zeroed paper PnL because
``main.set_auto_execution_mode`` rebuilds ``PaperOrderManager`` (and so
loses the in-memory ``_realised_pnl_total``) — same outcome on a regular
process restart.

Persistence design (deliberately narrow):
* Only ``_realised_pnl_total`` is written to disk
* Open positions stay ephemeral — TradeMonitor + signal-history are the
  right layer for in-flight lifecycle state
* On boot with persisted PnL, the broker initialises
  ``_available_equity = starting_equity + persisted_pnl`` so subsequent
  position sizing reflects the true paper-account balance

Tests run with ``PAPER_PNL_STATE_PATH`` pointing at a per-test temp file
so they don't pollute the production ``data/paper_pnl_state.json`` ledger.
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from src.smc import Direction


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_pnl_path(tmp_path):
    """The on-disk ledger path for the current test.

    The autouse conftest fixture (``_isolate_disk_backed_registries``) sets
    ``PAPER_PNL_STATE_PATH`` to ``tmp_path / "paper_pnl_state.json"`` for
    every test — this fixture just returns that same path so the test can
    assert directly against the file on disk.
    """
    return tmp_path / "paper_pnl_state.json"


def _make_signal(
    *,
    signal_id: str = "PAPER-001",
    symbol: str = "BTCUSDT",
    direction: Direction = Direction.LONG,
    entry: float = 30000.0,
    current_price: float = 30000.0,
):
    sig = MagicMock()
    sig.signal_id = signal_id
    sig.symbol = symbol
    sig.direction = direction
    sig.entry = entry
    sig.current_price = current_price
    return sig


# ---------------------------------------------------------------------------
# Load contract
# ---------------------------------------------------------------------------


class TestLedgerLoad:
    def test_load_returns_zero_when_file_missing(self, tmp_pnl_path):
        """Clean-slate paper sessions return $0.00 — no exceptions."""
        from src.paper_order_manager import _load_paper_pnl_state
        assert not tmp_pnl_path.exists()
        assert _load_paper_pnl_state(tmp_pnl_path) == 0.0

    def test_load_returns_persisted_value(self, tmp_pnl_path):
        from src.paper_order_manager import _load_paper_pnl_state
        tmp_pnl_path.write_text(json.dumps({"realised_pnl_usd": 84.30}))
        assert _load_paper_pnl_state(tmp_pnl_path) == pytest.approx(84.30)

    def test_load_returns_zero_when_file_corrupt(self, tmp_pnl_path):
        """Malformed JSON must not crash the broker boot — fail-soft."""
        from src.paper_order_manager import _load_paper_pnl_state
        tmp_pnl_path.write_text("not valid json {{{")
        assert _load_paper_pnl_state(tmp_pnl_path) == 0.0

    def test_load_returns_zero_when_value_non_numeric(self, tmp_pnl_path):
        from src.paper_order_manager import _load_paper_pnl_state
        tmp_pnl_path.write_text(json.dumps({"realised_pnl_usd": "oops"}))
        assert _load_paper_pnl_state(tmp_pnl_path) == 0.0

    def test_load_returns_zero_when_missing_key(self, tmp_pnl_path):
        from src.paper_order_manager import _load_paper_pnl_state
        tmp_pnl_path.write_text(json.dumps({"some_other_key": 12.0}))
        assert _load_paper_pnl_state(tmp_pnl_path) == 0.0


# ---------------------------------------------------------------------------
# Persist contract
# ---------------------------------------------------------------------------


class TestLedgerPersist:
    def test_persist_writes_value_to_disk(self, tmp_pnl_path):
        from src.paper_order_manager import _persist_paper_pnl_state
        _persist_paper_pnl_state(42.50, tmp_pnl_path)
        assert tmp_pnl_path.exists()
        data = json.loads(tmp_pnl_path.read_text())
        assert data["realised_pnl_usd"] == pytest.approx(42.50)

    def test_persist_creates_parent_dir_if_missing(self, tmp_path):
        from src.paper_order_manager import _persist_paper_pnl_state
        nested = tmp_path / "nested" / "deeper" / "paper.json"
        _persist_paper_pnl_state(7.25, nested)
        assert nested.exists()
        assert json.loads(nested.read_text())["realised_pnl_usd"] == 7.25

    def test_persist_uses_atomic_replace(self, tmp_pnl_path):
        """Tmp-then-rename so a crash mid-write doesn't leave a torn file."""
        from src.paper_order_manager import _persist_paper_pnl_state
        # Pre-existing valid file.
        tmp_pnl_path.write_text(json.dumps({"realised_pnl_usd": 1.0}))
        _persist_paper_pnl_state(99.0, tmp_pnl_path)
        # Final value present, no .tmp leftover.
        assert json.loads(tmp_pnl_path.read_text())["realised_pnl_usd"] == 99.0
        leftover = tmp_pnl_path.with_suffix(tmp_pnl_path.suffix + ".tmp")
        assert not leftover.exists()


# ---------------------------------------------------------------------------
# Init contract
# ---------------------------------------------------------------------------


class TestPaperOrderManagerInitLoadsPersistedPnl:
    def test_fresh_init_starts_at_zero(self, tmp_pnl_path):
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        assert pm.simulated_pnl_total == 0.0

    def test_init_loads_persisted_pnl(self, tmp_pnl_path):
        """Restart scenario — broker starts up with PnL from prior session."""
        tmp_pnl_path.write_text(json.dumps({"realised_pnl_usd": 25.50}))
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        assert pm.simulated_pnl_total == pytest.approx(25.50)

    def test_init_seeds_available_equity_from_persisted_pnl(self, tmp_pnl_path):
        """Position sizing must reflect the paper account's true balance."""
        tmp_pnl_path.write_text(json.dumps({"realised_pnl_usd": 50.0}))
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        # _available_equity should be starting + persisted = 1050.
        assert pm._available_equity == pytest.approx(1050.0)


# ---------------------------------------------------------------------------
# End-to-end: close path persists, next instance picks it up
# ---------------------------------------------------------------------------


class TestEndToEndPersistenceCycle:
    async def test_partial_close_persists_to_disk(self, tmp_pnl_path):
        """Every TP1/TP2/TP3 close path must write to disk."""
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        sig = _make_signal(direction=Direction.LONG, entry=100.0)
        await pm.place_market_order(sig)
        # Move favourably, partial close at TP1.
        sig.current_price = 105.0
        await pm.close_partial(sig, fraction=0.33, tp_level=1, current_price=105.0)
        assert tmp_pnl_path.exists()
        data = json.loads(tmp_pnl_path.read_text())
        # Compare against the raw cumulative — ``simulated_pnl_total`` rounds
        # to 4dp which doesn't match the unrounded float persisted to disk
        # once Binance fees enter the math (sub-cent precision matters).
        assert data["realised_pnl_usd"] == pytest.approx(pm._realised_pnl_total, abs=1e-9)
        assert data["realised_pnl_usd"] > 0  # actually banked something

    async def test_full_close_persists_to_disk(self, tmp_pnl_path):
        """SL/INVALIDATED full closes also persist."""
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        sig = _make_signal(direction=Direction.LONG, entry=100.0)
        await pm.place_market_order(sig)
        sig.current_price = 99.0
        await pm.close_full(sig, current_price=99.0, reason="SL_HIT")
        assert tmp_pnl_path.exists()
        data = json.loads(tmp_pnl_path.read_text())
        # Compare against the raw cumulative — ``simulated_pnl_total`` rounds
        # to 4dp which doesn't match the unrounded float persisted to disk
        # once Binance fees enter the math (sub-cent precision matters).
        assert data["realised_pnl_usd"] == pytest.approx(pm._realised_pnl_total, abs=1e-9)
        assert data["realised_pnl_usd"] < 0  # actually lost money

    async def test_persistence_survives_broker_rebuild(self, tmp_pnl_path):
        """The mode-switch scenario: paper → live → paper.

        Simulated by destroying the first PaperOrderManager and creating
        a new one against the same ledger path.  The new instance must
        pick up the prior PnL exactly — that's what survives the
        ``main.set_auto_execution_mode`` teardown / rebuild.
        """
        from src.paper_order_manager import PaperOrderManager
        # Session 1: trade, partial close, full close.
        pm1 = PaperOrderManager(starting_equity_usd=1000.0)
        sig = _make_signal(direction=Direction.LONG, entry=100.0)
        await pm1.place_market_order(sig)
        sig.current_price = 105.0
        await pm1.close_partial(sig, fraction=0.33, tp_level=1, current_price=105.0)
        session1_pnl = pm1.simulated_pnl_total
        assert session1_pnl > 0

        # Session 2: rebuild broker (mimics paper after a paper→live→paper toggle).
        pm2 = PaperOrderManager(starting_equity_usd=1000.0)
        assert pm2.simulated_pnl_total == pytest.approx(session1_pnl)
        # And its available equity reflects the persisted PnL.
        assert pm2._available_equity == pytest.approx(
            1000.0 + session1_pnl
        )

    async def test_two_close_cycles_accumulate_on_disk(self, tmp_pnl_path):
        """Sequential closes update the same ledger key — no silent drops."""
        from src.paper_order_manager import PaperOrderManager
        pm = PaperOrderManager(starting_equity_usd=1000.0)
        # Two independent winning trades.
        for i, entry in enumerate([100.0, 200.0], start=1):
            sig = _make_signal(
                signal_id=f"PAPER-00{i}", entry=entry,
                current_price=entry * 1.05,
            )
            await pm.place_market_order(sig)
            await pm.close_full(sig, current_price=entry * 1.05, reason="TP1_HIT")
        data = json.loads(tmp_pnl_path.read_text())
        # Compare against the raw cumulative — ``simulated_pnl_total`` rounds
        # to 4dp which doesn't match the unrounded float persisted to disk
        # once Binance fees enter the math (sub-cent precision matters).
        assert data["realised_pnl_usd"] == pytest.approx(pm._realised_pnl_total, abs=1e-9)
