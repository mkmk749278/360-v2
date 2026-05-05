"""Smoke tests for the Lumin app API.

Build the FastAPI app against a stub engine and hit every endpoint.
The stub mirrors the surface that ``src.api.snapshot`` reads — just
enough state to round-trip a realistic response without booting the
full engine.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import pytest

# Skip the entire module when FastAPI / uvicorn aren't installed in the
# CI environment — they're optional engine deps.
pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.server import build_app  # noqa: E402


# ---------------------------------------------------------------------------
# Stub engine surface
# ---------------------------------------------------------------------------


class _Direction:
    def __init__(self, value: str) -> None:
        self.value = value


@dataclass
class _StubSignal:
    signal_id: str
    symbol: str
    direction: _Direction
    entry: float
    stop_loss: float
    tp1: float
    tp2: float
    tp3: Optional[float] = None
    confidence: float = 75.0
    quality_tier: str = "B"
    setup_class: str = "SR_FLIP_RETEST"
    status: str = "ACTIVE"
    current_price: float = 0.0
    pnl_pct: float = 0.0
    pre_tp_hit: bool = False
    pre_tp_pct: float = 0.0
    pre_tp_timestamp: Optional[datetime] = None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    dispatch_timestamp: Optional[datetime] = None
    terminal_outcome_timestamp: Optional[datetime] = None
    qty: float = 1.0
    pnl_usd: float = 0.0


class _StubRouter:
    def __init__(self, active: Dict[str, _StubSignal]) -> None:
        self.active_signals: Dict[str, _StubSignal] = active


class _StubRiskManager:
    def __init__(self) -> None:
        self.open_position_count = 1
        self.daily_realised_pnl_usd = 12.84
        self.daily_loss_pct = 0.0
        self.daily_kill_tripped = False
        self.manual_paused = False
        self.current_equity_usd = 1012.84


class _StubRegimeResult:
    class _Regime:
        value = "TRENDING_UP"

    regime = _Regime()


class _StubRegimeDetector:
    def get_regime(self, symbol: str) -> _StubRegimeResult:
        return _StubRegimeResult()


class _StubPairMgr:
    symbols: Tuple[str, ...] = tuple(f"PAIR{i}USDT" for i in range(75))


class ScalpChannel:
    """Named to match the production class — ``build_agents`` looks it up by name."""

    def __init__(self) -> None:
        self._generation_telemetry: Dict[str, Dict[str, int]] = {
            "attempts": {"TREND_PULLBACK": 5, "STANDARD": 3, "WHALE_MOMENTUM": 1},
            "generated": {"TREND_PULLBACK": 1, "WHALE_MOMENTUM": 1},
            "no_signal": {"TREND_PULLBACK": 4, "STANDARD": 3},
        }


class _StubEngine:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        active_sig = _StubSignal(
            signal_id="sig-001",
            symbol="ETHUSDT",
            direction=_Direction("LONG"),
            entry=2329.0,
            stop_loss=2310.0,
            tp1=2351.0,
            tp2=2378.0,
            tp3=2394.0,
            current_price=2338.80,
            pnl_pct=0.42,
            timestamp=now - timedelta(minutes=18),
            dispatch_timestamp=now - timedelta(minutes=18),
            qty=0.0429,
        )
        closed_sig = _StubSignal(
            signal_id="sig-002",
            symbol="BTCUSDT",
            direction=_Direction("SHORT"),
            entry=78240.0,
            stop_loss=78850.0,
            tp1=77800.0,
            tp2=77400.0,
            tp3=76900.0,
            setup_class="LIQUIDITY_SWEEP_REVERSAL",
            status="TP1_HIT",
            current_price=77800.0,
            pnl_pct=0.56,
            timestamp=now - timedelta(hours=2),
            dispatch_timestamp=now - timedelta(hours=2),
            terminal_outcome_timestamp=now - timedelta(minutes=90),
        )
        self.router = _StubRouter({active_sig.signal_id: active_sig})
        self._signal_history: List[_StubSignal] = [closed_sig]
        self._risk_manager = _StubRiskManager()
        self._regime_detector = _StubRegimeDetector()
        self.pair_mgr = _StubPairMgr()
        self._channels = [ScalpChannel()]
        self._current_auto_mode = "paper"
        self._boot_time = time.monotonic() - 3600.0  # 1h uptime

        self.last_mode_change: Optional[str] = None

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
        if new_mode not in {"off", "paper", "live"}:
            return False, f"invalid mode {new_mode!r}"
        if new_mode == self._current_auto_mode:
            return False, f"already in {new_mode.upper()} mode"
        previous = self._current_auto_mode
        self._current_auto_mode = new_mode
        self.last_mode_change = new_mode
        return True, f"mode changed: {previous.upper()} → {new_mode.upper()}"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def engine() -> _StubEngine:
    return _StubEngine()


_TEST_SECRET = "smoke-test-secret-x" * 4


@pytest.fixture
def client(engine: _StubEngine) -> TestClient:
    """Authenticated client — mints a JWT and applies it on every request.

    Auth is now mandatory; endpoints reject unauthenticated requests.
    The smoke tests below exercise endpoint behaviour, not auth — auth
    itself is covered exhaustively in ``tests/api/test_auth.py``.
    """
    from src.api.auth import mint_token  # local import — pyjwt optional

    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def auth_client(engine: _StubEngine) -> TestClient:
    """Static-token client — admin escape hatch, used by static-token tests below."""
    return TestClient(
        build_app(
            engine,
            jwt_secret=_TEST_SECRET,
            static_token="secret",
            allow_static=True,
        )
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


def test_health_returns_uptime(client: TestClient) -> None:
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["uptime_seconds"] > 0


# ---------------------------------------------------------------------------
# Pulse
# ---------------------------------------------------------------------------


def test_pulse_returns_engine_snapshot(client: TestClient) -> None:
    r = client.get("/api/pulse")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "paper"
    assert body["status"] == "Healthy"
    assert body["regime"] == "TRENDING_UP"
    assert body["open_positions"] == 1
    assert body["scanning_pairs"] == 75
    assert body["today_pnl_usd"] == pytest.approx(12.84)


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------


def test_signals_default_returns_active_and_closed(client: TestClient) -> None:
    r = client.get("/api/signals")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    symbols = {s["symbol"] for s in body["items"]}
    assert symbols == {"ETHUSDT", "BTCUSDT"}


def test_signals_status_open_filters_to_active(client: TestClient) -> None:
    r = client.get("/api/signals", params={"status": "open"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["symbol"] == "ETHUSDT"
    assert body["items"][0]["agent_name"] == "The Architect"


def test_signals_status_closed_filters_to_history(client: TestClient) -> None:
    r = client.get("/api/signals", params={"status": "closed"})
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["symbol"] == "BTCUSDT"
    assert body["items"][0]["agent_name"] == "The Counter-Puncher"


def test_signal_detail_lookup_by_id(client: TestClient) -> None:
    r = client.get("/api/signals/sig-001")
    assert r.status_code == 200
    body = r.json()
    assert body["signal_id"] == "sig-001"
    assert body["direction"] == "LONG"


def test_signal_detail_unknown_returns_404(client: TestClient) -> None:
    r = client.get("/api/signals/missing")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------


def test_positions_returns_active_signals(client: TestClient) -> None:
    r = client.get("/api/positions")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    p = body["items"][0]
    assert p["symbol"] == "ETHUSDT"
    assert p["direction"] == "LONG"
    assert p["minutes_open"] >= 17


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------


def test_activity_includes_open_and_terminal_events(client: TestClient) -> None:
    r = client.get("/api/activity")
    assert r.status_code == 200
    body = r.json()
    kinds = [e["kind"] for e in body["items"]]
    assert "OPEN" in kinds
    assert "TP1" in kinds  # closed BTCUSDT had TP1_HIT


# ---------------------------------------------------------------------------
# Auto-mode
# ---------------------------------------------------------------------------


def test_auto_mode_get_returns_current(client: TestClient) -> None:
    r = client.get("/api/auto-mode")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "paper"


def test_auto_mode_post_switches(client: TestClient, engine: _StubEngine) -> None:
    r = client.post("/api/auto-mode", json={"mode": "off"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["mode"] == "off"
    assert engine.last_mode_change == "off"


def test_auto_mode_post_same_mode_returns_409(
    client: TestClient,
) -> None:
    r = client.post("/api/auto-mode", json={"mode": "paper"})
    assert r.status_code == 409


def test_auto_mode_post_invalid_payload_returns_422(
    client: TestClient,
) -> None:
    r = client.post("/api/auto-mode", json={"mode": "yolo"})
    # Pydantic validation rejects literal mismatch with 422
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


def test_agents_returns_14_evaluators(client: TestClient) -> None:
    r = client.get("/api/agents")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 14
    by_setup = {a["setup_class"]: a for a in body["items"]}
    assert "TREND_PULLBACK_EMA" in by_setup
    assert by_setup["TREND_PULLBACK_EMA"]["display_name"] == "The Pullback Sniper"
    assert by_setup["TREND_PULLBACK_EMA"]["attempts"] == 5
    assert by_setup["TREND_PULLBACK_EMA"]["generated"] == 1


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_auth_required_when_token_set(auth_client: TestClient) -> None:
    r = auth_client.get("/api/pulse")
    assert r.status_code == 401


def test_auth_passes_with_correct_bearer(auth_client: TestClient) -> None:
    r = auth_client.get(
        "/api/pulse",
        headers={"Authorization": "Bearer secret"},
    )
    assert r.status_code == 200


def test_auth_rejects_wrong_bearer(auth_client: TestClient) -> None:
    r = auth_client.get(
        "/api/pulse",
        headers={"Authorization": "Bearer nope"},
    )
    assert r.status_code == 401


def test_health_does_not_require_auth(auth_client: TestClient) -> None:
    r = auth_client.get("/api/health")
    assert r.status_code == 200
