"""End-to-end smoke test for the isolated API container path.

Builds the FastAPI app with a ``RedisEngineFacade`` backed by an in-memory
fake Redis, seeds an engine-state snapshot the way ``SnapshotWriter`` would,
and verifies the read endpoints serve correctly without a live engine.

This validates the full isolation contract:
  SnapshotWriter (engine) → Redis → RedisEngineFacade → build_app → HTTP
"""
import pytest
from fastapi.testclient import TestClient


class _FakeRedisClient:
    """Minimal in-memory stand-in for src.redis_client.RedisClient."""

    def __init__(self) -> None:
        self._store: dict = {}
        self.available = True
        self.client = self  # the facade calls .client.get / .set / .delete

    async def get(self, key):
        return self._store.get(key)

    async def set(self, key, value, ex=None):
        self._store[key] = value

    async def delete(self, key):
        self._store.pop(key, None)


@pytest.fixture
def isolated_client():
    """A TestClient wired to a RedisEngineFacade over fake Redis."""
    from src.api.redis_engine import RedisEngineFacade
    from src.api.snapshot_store import KEY_ENGINE_STATE, KEY_SIGNALS_ALL, encode
    from src.api.server import build_app

    fake_redis = _FakeRedisClient()

    # Seed an engine-state snapshot (what SnapshotWriter would publish).
    engine_state = {
        "current_auto_mode": "paper",
        "regime_btcusdt": "RANGING",
        "uptime_seconds": 123.0,
        "scanning_pairs_count": 75,
        "signals_today_count": 0,
        "risk_manager": {
            "open_position_count": 0,
            "daily_realised_pnl_usd": 0.0,
            "current_equity_usd": 1000.0,
            "daily_kill_tripped": False,
        },
        "paper_equity_usd": 1000.0,
        "broker_positions": {},
        "active_signal_dispatch": {},
        "auto_execution_status": {
            "mode": "paper",
            "open_positions": 0,
            "daily_pnl_usd": 0.0,
            "daily_loss_pct": 0.0,
            "daily_kill_tripped": False,
            "manual_paused": False,
            "current_equity_usd": 1000.0,
        },
    }
    fake_redis._store[KEY_ENGINE_STATE] = encode(engine_state)
    fake_redis._store[KEY_SIGNALS_ALL] = encode([])

    facade = RedisEngineFacade(fake_redis)

    app = build_app(
        facade,
        jwt_secret="test-secret",
        static_token="test-token",
        allow_static=True,
    )
    with TestClient(app) as client:
        yield client, facade, fake_redis


def test_health_endpoint_isolated(isolated_client):
    client, _, _ = isolated_client
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert "version" in resp.json()


def test_pulse_endpoint_isolated(isolated_client):
    client, facade, _ = isolated_client
    # Refresh facade state from fake Redis (lifespan doesn't auto-loop in TestClient).
    import asyncio
    asyncio.get_event_loop().run_until_complete(facade.refresh_state())

    resp = client.get("/api/pulse", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["mode"] == "paper"
    assert body["scanning_pairs"] == 75
    assert body["regime"] == "RANGING"


def test_signals_endpoint_isolated_serves_from_cache(isolated_client):
    client, _, _ = isolated_client
    resp = client.get("/api/signals", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_set_mode_queues_redis_command(isolated_client):
    """POST /api/auto-mode in isolated mode must write a Redis command, not
    mutate engine state directly."""
    client, facade, fake_redis = isolated_client
    import asyncio
    asyncio.get_event_loop().run_until_complete(facade.refresh_state())

    from src.api.snapshot_store import KEY_CMD_SET_MODE

    # facade is in 'paper'; request a switch to 'off'.
    resp = client.post(
        "/api/auto-mode",
        json={"mode": "off"},
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    # The command must now be queued in Redis for the engine to pick up.
    assert fake_redis._store.get(KEY_CMD_SET_MODE) == "off"


def test_auto_mode_get_isolated(isolated_client):
    client, facade, _ = isolated_client
    import asyncio
    asyncio.get_event_loop().run_until_complete(facade.refresh_state())

    resp = client.get("/api/auto-mode", headers={"Authorization": "Bearer test-token"})
    assert resp.status_code == 200
    assert resp.json()["mode"] == "paper"


def test_positions_diag_isolated_serves_published_xray(isolated_client):
    """In isolated mode the endpoint serves the engine-published X-ray with full
    symbol/SL/candle data — not a blank diag built from skeletal facade stubs
    (the bug where MAGMAUSDT rendered as an all-zero, blank-symbol row)."""
    client, facade, fake_redis = isolated_client
    import asyncio
    from datetime import datetime, timezone
    from src.api.snapshot_store import KEY_POSITIONS_DIAG, encode
    from src.api.schemas import PositionsDiagResponse, PositionDiagDetail

    detail = PositionDiagDetail(
        signal_id="SIG-XYZ", symbol="MAGMAUSDT", direction="LONG",
        status="ACTIVE", setup_class="SR_FLIP_RETEST", channel="The Architect",
        entry=0.43982, stop_loss=0.43320, tp1=0.44848, tp2=0.46880,
        current_price=0.43703, pnl_pct=-0.63,
        max_favorable_excursion_pct=0.0, max_adverse_excursion_pct=-0.63,
        best_tp_hit=0, pre_tp_hit=False,
        candle_1m_high=0.4400, candle_1m_low=0.4365, candle_1m_age_sec=12.0,
        sl_breach_distance_pct=0.88, minutes_open=2,
    )
    published = PositionsDiagResponse(
        items=[detail], total=1, monitor_running=True,
        generated_at=datetime(2026, 6, 4, 16, 7, 9, tzinfo=timezone.utc),
    ).model_dump(mode="json")
    fake_redis._store[KEY_POSITIONS_DIAG] = encode(published)
    asyncio.get_event_loop().run_until_complete(facade.refresh_state())

    resp = client.get(
        "/internal/diag/positions",
        headers={"Authorization": "Bearer test-token"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["monitor_running"] is True
    assert body["total"] == 1
    item = body["items"][0]
    assert item["symbol"] == "MAGMAUSDT"
    assert abs(item["stop_loss"] - 0.43320) < 1e-9
    assert item["candle_1m_age_sec"] == 12.0
