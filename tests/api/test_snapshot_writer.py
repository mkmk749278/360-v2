"""Unit tests for SnapshotWriter helper methods.

Tests focus on the pure ``_build_*`` methods and the engine-state builder —
these are synchronous and don't require a running asyncio loop or real Redis.
The async ``_write_*`` and ``_apply_pending_mode_cmd`` paths are integration
concerns validated by docker-compose smoke tests on the VPS.
"""
import pytest
from unittest.mock import MagicMock, patch

_SAMPLE_TASKS = [
    "trade_monitor", "reconciler", "mark_price_feed",
    "funding_exit_watcher", "snapshot_writer",
]


def _make_engine():
    """Minimal engine stub sufficient for _build_engine_state."""
    engine = MagicMock()
    engine._current_auto_mode = "paper"

    rm = MagicMock()
    rm.open_position_count = 2
    rm.daily_realised_pnl_usd = 45.67
    rm.current_equity_usd = 1045.67
    rm.daily_kill_tripped = False
    engine._risk_manager = rm

    om = MagicMock()
    om._positions = {}
    om.current_equity_usd = 1045.67
    engine._order_manager = om

    router = MagicMock()
    router.active_signals = {}
    engine.router = router

    regime_mock = MagicMock()
    regime_mock.regime.value = "RANGING"
    engine._regime_detector.get_regime.return_value = regime_mock

    engine._boot_time = 0.0
    engine.pair_mgr.symbols = ["BTCUSDT", "ETHUSDT"]
    engine._signal_history = []

    status = {
        "mode": "paper",
        "open_positions": 2,
        "daily_pnl_usd": 45.67,
        "daily_loss_pct": 0.0,
        "daily_kill_tripped": False,
        "manual_paused": False,
        "current_equity_usd": 1045.67,
    }
    engine.get_auto_execution_status.return_value = status

    return engine


def test_build_engine_state_shape():
    from src.api.snapshot_writer import SnapshotWriter

    engine = _make_engine()
    sw = SnapshotWriter(engine, redis_client=MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)

    assert state["current_auto_mode"] == "paper"
    assert state["regime_btcusdt"] == "RANGING"
    assert isinstance(state["uptime_seconds"], float)
    assert state["scanning_pairs_count"] == 2
    assert "risk_manager" in state
    assert "broker_positions" in state
    assert "active_signal_dispatch" in state
    assert "auto_execution_status" in state
    assert "background_tasks" in state


def test_build_engine_state_background_tasks_published():
    """The live task census captured on the loop must round-trip into the
    snapshot so the isolated API can answer /internal/diag/tasks."""
    from src.api.snapshot_writer import SnapshotWriter

    engine = _make_engine()
    sw = SnapshotWriter(engine, MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)

    assert state["background_tasks"] == _SAMPLE_TASKS
    # Must be a plain list (JSON-serialisable), not a generator/set
    assert isinstance(state["background_tasks"], list)


def test_build_engine_state_risk_manager_fields():
    from src.api.snapshot_writer import SnapshotWriter

    engine = _make_engine()
    sw = SnapshotWriter(engine, MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)
    rm = state["risk_manager"]

    assert rm["open_position_count"] == 2
    assert abs(rm["daily_realised_pnl_usd"] - 45.67) < 0.01
    assert rm["daily_kill_tripped"] is False


def test_build_engine_state_no_risk_manager():
    from src.api.snapshot_writer import SnapshotWriter

    engine = _make_engine()
    engine._risk_manager = None
    sw = SnapshotWriter(engine, MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)

    rm = state["risk_manager"]
    assert rm["open_position_count"] == 0
    assert rm["current_equity_usd"] == 0.0


def test_build_engine_state_broker_positions_serialized():
    from src.api.snapshot_writer import SnapshotWriter

    engine = _make_engine()
    pos = MagicMock()
    pos.quantity = 0.002
    pos.closed_quantity = 0.001
    engine._order_manager._positions = {"sig_xyz": pos}

    sw = SnapshotWriter(engine, MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)

    bp = state["broker_positions"]
    assert "sig_xyz" in bp
    assert abs(bp["sig_xyz"]["quantity"] - 0.002) < 1e-9
    assert abs(bp["sig_xyz"]["closed_quantity"] - 0.001) < 1e-9


def test_build_engine_state_active_signal_dispatch():
    from src.api.snapshot_writer import SnapshotWriter
    from datetime import datetime, timezone

    engine = _make_engine()
    ts = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)
    sig = MagicMock()
    sig.dispatch_timestamp = ts
    sig.timestamp = ts
    engine.router.active_signals = {"sig_abc": sig}

    sw = SnapshotWriter(engine, MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)

    assert "sig_abc" in state["active_signal_dispatch"]
    assert state["active_signal_dispatch"]["sig_abc"] is not None


def test_build_engine_state_serialisable_via_json():
    """encode(state) must not raise — all values must be JSON-serialisable."""
    from src.api.snapshot_writer import SnapshotWriter
    from src.api.snapshot_store import encode

    engine = _make_engine()
    sw = SnapshotWriter(engine, MagicMock())
    state = sw._build_engine_state(_SAMPLE_TASKS)
    # Should not raise
    encoded = encode(state)
    assert len(encoded) > 0


def test_build_positions_diag_serialisable():
    """The engine-side positions-diag X-ray must build into a JSON-serialisable
    dict so the isolated API can publish and re-hydrate it."""
    from src.api.snapshot_writer import SnapshotWriter
    from src.api.snapshot_store import encode

    engine = _make_engine()
    sw = SnapshotWriter(engine, MagicMock())
    diag = sw._build_positions_diag()

    assert isinstance(diag, dict)
    assert "items" in diag
    assert "total" in diag
    assert "monitor_running" in diag
    assert "generated_at" in diag
    # Must not raise — all values JSON-serialisable.
    assert len(encode(diag)) > 0
