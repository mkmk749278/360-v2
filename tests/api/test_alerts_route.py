"""/api/alerts route + snapshot plumbing (writer → Redis → facade)."""
from __future__ import annotations

from typing import Optional

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.alerts.models import AlertType, make_alert  # noqa: E402
from src.api.server import build_app  # noqa: E402

_TEST_SECRET = "alerts-route-test-secret"


class _FakeAlertService:
    def __init__(self, alerts) -> None:
        self._items = alerts

    def recent(self, limit=100, alert_type=None, symbol=None):
        return self._items[:limit]


class _StubEngine:
    """Bare-minimum engine: /api/alerts only touches _alert_service."""

    def __init__(self, alerts) -> None:
        self._alert_service = _FakeAlertService(alerts)


def _alerts_fixture():
    return [
        make_alert(
            AlertType.RSI_OVERBOUGHT, "BTCUSDT", "1h", 64000.0,
            "RSI(14) at 83.2 — extremely overbought", {"rsi": 83.2},
        ).to_dict(),
        make_alert(
            AlertType.NEAR_RESISTANCE, "ETHUSDT", "1h", 1800.0,
            "Price 0.15% from resistance at 1803", {"level_price": 1803.0},
        ).to_dict(),
    ]


def _client(engine) -> TestClient:
    from src.api.auth import mint_token

    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


def test_alerts_served_from_live_service():
    client = _client(_StubEngine(_alerts_fixture()))
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    first = body["items"][0]
    assert first["alert_type"] == "RSI_OVERBOUGHT"
    assert first["timeframe"] == "1h"
    assert first["bias"] == "BEARISH"
    assert first["title"] == "RSI Extremely Overbought"


def test_alerts_filters():
    client = _client(_StubEngine(_alerts_fixture()))
    resp = client.get("/api/alerts", params={"symbol": "ethusdt"})
    assert [i["symbol"] for i in resp.json()["items"]] == ["ETHUSDT"]
    resp = client.get("/api/alerts", params={"alert_type": "RSI_OVERBOUGHT"})
    assert [i["alert_type"] for i in resp.json()["items"]] == ["RSI_OVERBOUGHT"]
    resp = client.get("/api/alerts", params={"limit": 1})
    assert resp.json()["total"] == 1


def test_alerts_requires_auth():
    app = build_app(_StubEngine(_alerts_fixture()), jwt_secret=_TEST_SECRET, allow_static=False)
    resp = TestClient(app).get("/api/alerts")
    assert resp.status_code in (401, 403)


def test_alerts_prefers_published_snapshot_in_isolated_mode():
    """A facade exposing ``published_alerts`` (isolated mode) wins over the
    live service — mirrors positions_diag serving."""

    class _Facade(_StubEngine):
        def published_alerts(self) -> Optional[list]:
            return _alerts_fixture()[:1]

    engine = _Facade([])  # live service intentionally empty
    client = _client(engine)
    body = client.get("/api/alerts").json()
    assert body["total"] == 1
    assert body["items"][0]["symbol"] == "BTCUSDT"


def test_alerts_tolerates_shape_drift():
    """Corrupt / legacy entries are skipped, not 500s."""
    alerts = _alerts_fixture() + [{"garbage": True}]
    client = _client(_StubEngine(alerts))
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_alerts_empty_when_no_service():
    class _Bare:
        pass

    client = _client(_Bare())
    body = client.get("/api/alerts").json()
    assert body == {"items": [], "total": 0}


async def test_snapshot_writer_publishes_alerts():
    from src.api import snapshot_store as _store
    from src.api.snapshot_writer import SnapshotWriter

    class _Redis:
        def __init__(self):
            self.available = True
            self.writes = {}
            self.client = self

        async def set(self, key, value, ex=None):
            self.writes[key] = (value, ex)

    redis = _Redis()
    writer = SnapshotWriter(_StubEngine(_alerts_fixture()), redis)
    await writer._write_alerts()
    value, ttl = redis.writes[_store.KEY_ALERTS]
    assert ttl == _store.TTL_ALERTS
    assert "RSI_OVERBOUGHT" in value


async def test_redis_facade_exposes_published_alerts():
    from src.api import snapshot_store as _store
    from src.api.redis_engine import RedisEngineFacade

    payload = {
        _store.KEY_ENGINE_STATE: _store.encode({"current_auto_mode": "off"}),
        _store.KEY_ALERTS: _store.encode(_alerts_fixture()),
    }

    class _Redis:
        available = True

        def __init__(self):
            self.client = self

        async def get(self, key):
            return payload.get(key)

    facade = RedisEngineFacade(_Redis())
    await facade.refresh_state()
    published = facade.published_alerts()
    assert published is not None and len(published) == 2
    assert published[0]["alert_type"] == "RSI_OVERBOUGHT"
