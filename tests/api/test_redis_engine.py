"""Unit tests for RedisEngineFacade property accessors.

Validates that the facade correctly exposes engine-state dict keys as the
attribute interface that the snapshot builder functions (build_pulse,
build_auto_mode, build_positions) expect.  Redis reads are replaced with
a direct state injection so no running Redis is required.
"""
import pytest
from src.api.redis_engine import (
    RedisEngineFacade,
    _MockRiskManager,
    _MockOrderManager,
    _MockRouter,
    _MockSignal,
    _MockPosition,
)
from unittest.mock import MagicMock


def _facade_with_state(state: dict) -> RedisEngineFacade:
    facade = RedisEngineFacade(redis_client=MagicMock())
    facade._state = state
    return facade


def test_current_auto_mode():
    f = _facade_with_state({"current_auto_mode": "paper"})
    assert f._current_auto_mode == "paper"


def test_current_auto_mode_defaults_to_off():
    f = _facade_with_state({})
    assert f._current_auto_mode == "off"


def test_risk_manager_returns_none_when_absent():
    f = _facade_with_state({})
    assert f._risk_manager is None


def test_risk_manager_fields():
    f = _facade_with_state({
        "risk_manager": {
            "open_position_count": 3,
            "daily_realised_pnl_usd": 22.5,
            "current_equity_usd": 1022.5,
            "daily_kill_tripped": True,
        }
    })
    rm = f._risk_manager
    assert rm is not None
    assert rm.open_position_count == 3
    assert abs(rm.daily_realised_pnl_usd - 22.5) < 0.001
    assert rm.daily_kill_tripped is True


def test_order_manager_positions_populated():
    f = _facade_with_state({
        "broker_positions": {
            "sig1": {"quantity": 0.005, "closed_quantity": 0.002}
        }
    })
    om = f._order_manager
    assert "sig1" in om._positions
    assert abs(om._positions["sig1"].quantity - 0.005) < 1e-9
    assert abs(om._positions["sig1"].closed_quantity - 0.002) < 1e-9


def test_order_manager_paper_equity():
    f = _facade_with_state({"paper_equity_usd": 987.65})
    assert abs(f._order_manager.current_equity_usd - 987.65) < 0.001


def test_router_active_signals_populated():
    f = _facade_with_state({
        "active_signal_dispatch": {
            "sig_abc": "2026-06-02T12:00:00+00:00",
        }
    })
    router = f.router
    assert "sig_abc" in router.active_signals
    sig = router.active_signals["sig_abc"]
    assert sig.signal_id == "sig_abc"
    assert sig.dispatch_timestamp is not None


def test_router_empty_when_no_state():
    f = _facade_with_state({})
    assert f.router.active_signals == {}


def test_regime_detector():
    f = _facade_with_state({"regime_btcusdt": "TRENDING_UP"})
    result = f._regime_detector.get_regime("BTCUSDT")
    assert result.regime.value == "TRENDING_UP"


def test_regime_defaults_to_ranging():
    f = _facade_with_state({})
    result = f._regime_detector.get_regime("BTCUSDT")
    assert result.regime.value == "RANGING"


def test_get_auto_execution_status_returns_dict():
    state = {
        "auto_execution_status": {
            "mode": "paper",
            "open_positions": 1,
            "daily_pnl_usd": 5.0,
            "daily_loss_pct": 0.5,
            "daily_kill_tripped": False,
            "manual_paused": False,
            "current_equity_usd": 1005.0,
        }
    }
    f = _facade_with_state(state)
    status = f.get_auto_execution_status()
    assert status["mode"] == "paper"
    assert status["open_positions"] == 1


def test_get_background_task_census_from_state():
    tasks = ["trade_monitor", "reconciler", "mark_price_feed",
             "funding_exit_watcher", "snapshot_writer"]
    f = _facade_with_state({"background_tasks": tasks})
    assert f.get_background_task_census() == tasks


def test_get_background_task_census_empty_when_absent():
    f = _facade_with_state({})
    assert f.get_background_task_census() == []


def test_get_background_task_census_ignores_non_list():
    f = _facade_with_state({"background_tasks": "not-a-list"})
    assert f.get_background_task_census() == []


def test_set_auto_execution_mode_invalid_mode():
    f = _facade_with_state({"current_auto_mode": "paper"})
    ok, msg = f.set_auto_execution_mode("invalid")
    assert ok is False
    assert "invalid" in msg


def test_set_auto_execution_mode_same_mode():
    f = _facade_with_state({"current_auto_mode": "paper"})
    ok, msg = f.set_auto_execution_mode("paper")
    assert ok is False
    assert "already" in msg.lower()


def test_pair_mgr_count():
    f = _facade_with_state({"scanning_pairs_count": 75})
    assert len(list(f.pair_mgr.symbols)) == 75


def test_signal_history_is_empty_list():
    f = _facade_with_state({})
    assert f._signal_history == []


def test_channels_is_empty_list():
    f = _facade_with_state({})
    assert f._channels == []


def test_state_age_infinite_when_not_refreshed():
    f = RedisEngineFacade(redis_client=MagicMock())
    assert f.state_age_seconds == float("inf")


# ---------------------------------------------------------------------------
# Positions-diag X-ray published by the engine (isolated mode)
# ---------------------------------------------------------------------------


def test_published_positions_diag_none_by_default():
    f = RedisEngineFacade(redis_client=MagicMock())
    assert f.published_positions_diag() is None


@pytest.mark.asyncio
async def test_refresh_state_loads_positions_diag():
    """refresh_state must pull both engine_state and the positions_diag key,
    surfacing the latter via published_positions_diag()."""
    import json
    from unittest.mock import AsyncMock
    from src.api import snapshot_store as _store

    engine_state = {"current_auto_mode": "live"}
    diag = {
        "items": [], "total": 0, "monitor_running": True,
        "generated_at": "2026-06-04T16:00:00+00:00",
    }

    async def _get(key):
        if key == _store.KEY_ENGINE_STATE:
            return json.dumps(engine_state)
        if key == _store.KEY_POSITIONS_DIAG:
            return json.dumps(diag)
        return None

    redis_client = MagicMock()
    redis_client.available = True
    redis_client.client = MagicMock()
    redis_client.client.get = AsyncMock(side_effect=_get)

    f = RedisEngineFacade(redis_client=redis_client)
    await f.refresh_state()

    assert f._current_auto_mode == "live"
    assert f.published_positions_diag() == diag


@pytest.mark.asyncio
async def test_refresh_state_positions_diag_absent_is_none():
    """When the engine hasn't published a diag (key expired/absent), the
    facade reports None so the endpoint can fall back gracefully."""
    from unittest.mock import AsyncMock
    import json
    from src.api import snapshot_store as _store

    async def _get(key):
        if key == _store.KEY_ENGINE_STATE:
            return json.dumps({"current_auto_mode": "off"})
        return None  # positions_diag absent

    redis_client = MagicMock()
    redis_client.available = True
    redis_client.client = MagicMock()
    redis_client.client.get = AsyncMock(side_effect=_get)

    f = RedisEngineFacade(redis_client=redis_client)
    await f.refresh_state()
    assert f.published_positions_diag() is None
