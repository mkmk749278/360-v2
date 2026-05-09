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


class _StubDataStore:
    """Minimal stub of HistoricalDataStore — covers ``get_candles`` only."""

    def __init__(self) -> None:
        # 1m closes for the live-price ticker; 1h closes for the 24h % change.
        # Just enough history to verify the change-pct math: ref vs latest.
        self._buckets: Dict[Tuple[str, str], Dict[str, List[float]]] = {
            ("BTCUSDT", "1m"): {"close": [78000.0] * 5 + [78240.0]},
            ("BTCUSDT", "1h"): {"close": [76800.0] * 24 + [78240.0]},
            ("ETHUSDT", "1m"): {"close": [2329.0]},
            ("ETHUSDT", "1h"): {"close": [2300.0] * 24 + [2329.0]},
            ("SOLUSDT", "1m"): {"close": [148.0]},
            ("SOLUSDT", "1h"): {"close": [150.0] * 24 + [148.0]},
        }

    def get_candles(self, symbol: str, interval: str):
        return self._buckets.get((symbol, interval))


class _StubEngine:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self.data_store = _StubDataStore()
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


def test_pulse_tickers_returns_top_pairs(client: TestClient) -> None:
    """Wave 2: live-price strip for the Pulse top-pair ticker.

    The stub data-store only seeds BTC / ETH / SOL — the build_tickers
    helper must skip the rest of ``_PULSE_TICKER_SYMBOLS`` rather than
    return zeroed placeholders that would mislead subscribers.
    """
    r = client.get("/api/pulse/tickers")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == len(body["items"])
    symbols = [item["symbol"] for item in body["items"]]
    assert symbols == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    btc = next(i for i in body["items"] if i["symbol"] == "BTCUSDT")
    assert btc["price"] == pytest.approx(78240.0)
    # 24h change: (78240 - 76800) / 76800 * 100 ≈ +1.875%
    assert btc["change_pct_24h"] == pytest.approx(1.875, rel=1e-3)


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


def test_signals_status_open_excludes_terminal_status_in_active_map(
    client: TestClient, engine: _StubEngine,
) -> None:
    """Owner reported INVALIDATED + SL_HIT signals appearing in the
    Lumin app's "Open" tab.  Root cause: ``router.active_signals`` can
    transiently hold signals with terminal status (post-status-change,
    pre-_remove call), and the persistence layer can capture them
    mid-shutdown so a subsequent restart resurrects them in the active
    map.

    The API contract for ``status=open`` is "currently in-flight only"
    — defensive filter must drop any signal whose ``status`` isn't
    exactly ``ACTIVE``.
    """
    # Add an INVALIDATED signal to active_signals — mimics the
    # mid-removal race window.
    invalidated = _StubSignal(
        signal_id="INV-001",
        symbol="ZECUSDT",
        direction=_Direction("LONG"),
        entry=572.92,
        stop_loss=569.14,
        tp1=578.59,
        tp2=582.38,
        status="INVALIDATED",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=45),
        dispatch_timestamp=datetime.now(timezone.utc) - timedelta(minutes=45),
    )
    sl_hit = _StubSignal(
        signal_id="SL-001",
        symbol="FLOCKUSDT",
        direction=_Direction("LONG"),
        entry=0.07797,
        stop_loss=0.07699,
        tp1=0.08055,
        tp2=0.08153,
        status="SL_HIT",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=49),
        dispatch_timestamp=datetime.now(timezone.utc) - timedelta(minutes=49),
    )
    engine.router.active_signals[invalidated.signal_id] = invalidated
    engine.router.active_signals[sl_hit.signal_id] = sl_hit

    r = client.get("/api/signals", params={"status": "open"})
    assert r.status_code == 200
    body = r.json()
    statuses = [it["status"] for it in body["items"]]
    assert "INVALIDATED" not in statuses
    assert "SL_HIT" not in statuses
    # The genuinely-active stub signal is still present.
    assert any(it["status"] == "ACTIVE" for it in body["items"])


def test_signals_status_closed_includes_terminal_signals_in_active_map(
    client: TestClient, engine: _StubEngine,
) -> None:
    """Symmetric test — terminal-status signals stuck in the active map
    must still appear in ``status=closed`` so they're not orphaned
    between the two views."""
    invalidated = _StubSignal(
        signal_id="INV-002",
        symbol="ZECUSDT",
        direction=_Direction("LONG"),
        entry=572.92,
        stop_loss=569.14,
        tp1=578.59,
        tp2=582.38,
        status="INVALIDATED",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=45),
        dispatch_timestamp=datetime.now(timezone.utc) - timedelta(minutes=45),
    )
    engine.router.active_signals[invalidated.signal_id] = invalidated

    r = client.get("/api/signals", params={"status": "closed"})
    assert r.status_code == 200
    body = r.json()
    symbols = [it["symbol"] for it in body["items"]]
    assert "ZECUSDT" in symbols  # the orphan now appears in closed


def test_signals_filter_by_setup_class(client: TestClient) -> None:
    r = client.get(
        "/api/signals",
        params={"status": "all", "setup_class": "SR_FLIP_RETEST"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["setup_class"] == "SR_FLIP_RETEST"
    assert body["items"][0]["symbol"] == "ETHUSDT"


def test_signals_filter_by_setup_class_is_case_insensitive(
    client: TestClient,
) -> None:
    r = client.get(
        "/api/signals",
        params={"setup_class": "sr_flip_retest"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_signals_filter_by_setup_class_unknown_returns_empty(
    client: TestClient,
) -> None:
    r = client.get(
        "/api/signals",
        params={"setup_class": "WHO_DAT"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 0


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


def test_activity_filter_by_setup_class(client: TestClient) -> None:
    r = client.get(
        "/api/activity",
        params={"setup_class": "LIQUIDITY_SWEEP_REVERSAL"},
    )
    assert r.status_code == 200
    body = r.json()
    # All events should reference the BTCUSDT closed signal — symbol shows
    # up in title/subtitle for both OPEN and TP1 kinds.
    for ev in body["items"]:
        assert "BTCUSDT" in ev["title"]


def test_activity_filter_by_setup_class_unknown_returns_empty(
    client: TestClient,
) -> None:
    r = client.get(
        "/api/activity",
        params={"setup_class": "NEVER_SEEN"},
    )
    assert r.status_code == 200
    assert r.json()["total"] == 0


# ---------------------------------------------------------------------------
# Trade-tab error resilience (2026-05-08)
# ---------------------------------------------------------------------------
#
# Owner reported the app showing "Could not load Trade state /
# ApiError(500): Internal Server Error" on the Trade tab.  Without
# logs we can't pin which of the three endpoints (auto-mode / positions
# / activity) is failing — and a single 500 on any of them breaks the
# entire tab.
#
# These tests verify the new defensive behaviour: when one of the
# build_* helpers raises, the endpoint returns a degraded response
# (empty list / off-mode default) and logs the traceback rather than
# 500ing.  Diagnosis happens VPS-side from logs; UX stays graceful.


def test_positions_returns_empty_on_per_signal_error(
    client: TestClient, engine: _StubEngine,
) -> None:
    """A single corrupted signal in active_signals must not fail the
    whole /api/positions response — that was breaking the Trade tab."""
    bad = _StubSignal(
        signal_id="BAD-001",
        symbol="ZECUSDT",
        # direction with corrupted Direction-style value (not LONG/SHORT)
        direction=_Direction("CORRUPTED"),
        entry=100.0,
        stop_loss=99.0,
        tp1=101.0,
        tp2=102.0,
    )
    engine.router.active_signals[bad.signal_id] = bad

    r = client.get("/api/positions")
    assert r.status_code == 200, r.text
    body = r.json()
    # Bad signal skipped; the original good signal still in the list.
    bad_in = any(it["signal_id"] == "BAD-001" for it in body["items"])
    # Either the malformed one is sanitized to LONG (so it appears) or
    # it's dropped entirely — both are acceptable degradation paths;
    # the contract is "no 500".
    if bad_in:
        bad_pos = next(it for it in body["items"] if it["signal_id"] == "BAD-001")
        assert bad_pos["direction"] in ("LONG", "SHORT")


def test_positions_returns_empty_on_router_attribute_error(
    client: TestClient, engine: _StubEngine, monkeypatch,
) -> None:
    """When the whole build_positions call raises (e.g. router state is
    None or otherwise broken), endpoint returns an empty list."""
    from src.api import server as _server_mod

    def _broken(_engine):
        raise RuntimeError("simulated crash inside build_positions")

    monkeypatch.setattr(_server_mod, "build_positions", _broken)
    r = client.get("/api/positions")
    assert r.status_code == 200
    assert r.json() == {"items": [], "total": 0}


def test_activity_returns_empty_on_build_error(
    client: TestClient, engine: _StubEngine, monkeypatch,
) -> None:
    from src.api import server as _server_mod

    def _broken(*_args, **_kwargs):
        raise RuntimeError("simulated crash inside build_activity")

    monkeypatch.setattr(_server_mod, "build_activity", _broken)
    r = client.get("/api/activity")
    assert r.status_code == 200
    assert r.json() == {"items": [], "total": 0}


def test_auto_mode_returns_off_default_on_build_error(
    client: TestClient, engine: _StubEngine, monkeypatch,
) -> None:
    from src.api import server as _server_mod

    def _broken(_engine):
        raise RuntimeError("simulated crash inside build_auto_mode")

    monkeypatch.setattr(_server_mod, "build_auto_mode", _broken)
    r = client.get("/api/auto-mode")
    assert r.status_code == 200
    body = r.json()
    # Safe off-mode default — Trade tab renders the off card cleanly
    # instead of "Could not load Trade state".
    assert body["mode"] == "off"
    assert body["open_positions"] == 0
    assert body["daily_pnl_usd"] == 0.0
    assert body["daily_kill_tripped"] is False


# ---------------------------------------------------------------------------
# Auto-mode
# ---------------------------------------------------------------------------


def test_auto_mode_get_returns_current(client: TestClient) -> None:
    r = client.get("/api/auto-mode")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "paper"
    # Weekly/monthly aggregates land alongside daily — default to 0 with no
    # history yet (clean slate), but the keys must exist so the client
    # can render zeros without conditional null handling.
    assert "weekly_pnl_usd" in body
    assert "monthly_pnl_usd" in body


def test_pnl_history_returns_30_day_series(client: TestClient) -> None:
    """The dashboard chart endpoint — daily series + rolling aggregates."""
    r = client.get("/api/pnl/history")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "paper"
    assert body["days"] == 30
    assert len(body["items"]) == 30
    # Each item: {date: YYYY-MM-DD, pnl_usd: float}
    for item in body["items"]:
        assert "date" in item
        assert "pnl_usd" in item
        assert isinstance(item["pnl_usd"], (int, float))
    # Series oldest → newest (chart left-to-right).
    dates = [it["date"] for it in body["items"]]
    assert dates == sorted(dates)


def test_pnl_history_respects_days_parameter(client: TestClient) -> None:
    r = client.get("/api/pnl/history?days=7")
    assert r.status_code == 200
    body = r.json()
    assert body["days"] == 7
    assert len(body["items"]) == 7


def test_pnl_history_clamps_invalid_days(client: TestClient) -> None:
    """Out-of-range days param is rejected at the FastAPI Query layer."""
    r = client.get("/api/pnl/history?days=0")
    assert r.status_code == 422
    r = client.get("/api/pnl/history?days=999")
    assert r.status_code == 422


def test_pnl_history_mode_override(client: TestClient) -> None:
    """Mode override lets the client view the live ledger while engine is paper."""
    r = client.get("/api/pnl/history?mode=live&days=7")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "live"


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


def test_agents_returns_15_evaluators(client: TestClient) -> None:
    """API surface includes one entry per evaluator.  PR #318 added the
    15th evaluator (MA_CROSS_TREND_SHIFT)."""
    r = client.get("/api/agents")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 15
    by_setup = {a["setup_class"]: a for a in body["items"]}
    assert "TREND_PULLBACK_EMA" in by_setup
    assert by_setup["TREND_PULLBACK_EMA"]["display_name"] == "The Pullback Sniper"
    assert by_setup["TREND_PULLBACK_EMA"]["attempts"] == 5
    assert by_setup["TREND_PULLBACK_EMA"]["generated"] == 1
    # MA_CROSS_TREND_SHIFT (PR #318) must be present + labelled.
    assert "MA_CROSS_TREND_SHIFT" in by_setup
    assert by_setup["MA_CROSS_TREND_SHIFT"]["display_name"] == "The Trend Shifter"


def test_agents_lifecycle_counts_tp_hit_in_window(client: TestClient) -> None:
    """Closed BTCUSDT signal had TP1_HIT 90 min ago → counts under LSR."""
    r = client.get("/api/agents")
    assert r.status_code == 200
    by_setup = {a["setup_class"]: a for a in r.json()["items"]}
    lsr = by_setup["LIQUIDITY_SWEEP_REVERSAL"]
    assert lsr["tp_hits"] == 1
    assert lsr["sl_hits"] == 0
    assert lsr["invalidated"] == 0
    assert lsr["closed_today"] == 1


def test_agents_last_signal_age_minutes_populated(client: TestClient) -> None:
    """Active SR_FLIP_RETEST signal opened 18m ago should populate age."""
    r = client.get("/api/agents")
    assert r.status_code == 200
    by_setup = {a["setup_class"]: a for a in r.json()["items"]}
    sr_flip = by_setup["SR_FLIP_RETEST"]
    assert sr_flip["last_signal_age_minutes"] is not None
    assert 17 <= sr_flip["last_signal_age_minutes"] <= 19


def test_agents_lifecycle_counts_zero_when_never_fired(
    client: TestClient,
) -> None:
    """Evaluators without any signal in history report zero counts."""
    r = client.get("/api/agents")
    assert r.status_code == 200
    by_setup = {a["setup_class"]: a for a in r.json()["items"]}
    far = by_setup["FAILED_AUCTION_RECLAIM"]
    assert far["tp_hits"] == 0
    assert far["sl_hits"] == 0
    assert far["invalidated"] == 0
    assert far["closed_today"] == 0
    assert far["last_signal_age_minutes"] is None


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


# ---------------------------------------------------------------------------
# /api/settings/pretp — Pre-TP grab settings page
# ---------------------------------------------------------------------------


def test_settings_pretp_get_returns_resolved_view(
    client: TestClient, tmp_path, monkeypatch,
) -> None:
    """GET returns the merged view: user overrides where set, defaults otherwise."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )

    r = client.get("/api/settings/pretp")
    assert r.status_code == 200
    body = r.json()
    # Default config has TRENDING regimes excluded from the allowlist.
    from config import PRE_TP_REGIME_ALLOWLIST, PRE_TP_THRESHOLD_PCT
    assert set(body["regime_allowlist"]) == set(PRE_TP_REGIME_ALLOWLIST)
    assert body["threshold_pct"] == PRE_TP_THRESHOLD_PCT


def test_settings_pretp_put_partial_payload_merges(
    client: TestClient, tmp_path, monkeypatch,
) -> None:
    """PUT with one field must persist that field and leave others on default."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )

    r = client.put(
        "/api/settings/pretp",
        json={"regime_allowlist": ["TRENDING_UP", "TRENDING_DOWN", "RANGING"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body["regime_allowlist"]) == {"TRENDING_UP", "TRENDING_DOWN", "RANGING"}
    # threshold_pct unchanged from default — was NOT in the PUT payload.
    from config import PRE_TP_THRESHOLD_PCT
    assert body["threshold_pct"] == PRE_TP_THRESHOLD_PCT

    # Re-GET reflects the persisted state.
    r2 = client.get("/api/settings/pretp")
    assert set(r2.json()["regime_allowlist"]) == {
        "TRENDING_UP", "TRENDING_DOWN", "RANGING",
    }


def test_settings_pretp_put_accepts_ui_tokens(
    client: TestClient, tmp_path, monkeypatch,
) -> None:
    """The app sends UI-friendly tokens (TRENDING / RANGING / CHOPPY); the
    server normalises to backend tokens on read so the engine sees the
    expanded set."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )

    r = client.put(
        "/api/settings/pretp",
        json={"regime_allowlist": ["TRENDING", "RANGING"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body["regime_allowlist"]) == {
        "TRENDING_UP", "TRENDING_DOWN", "RANGING",
    }


def test_settings_pretp_put_rejects_negative_numeric(client: TestClient) -> None:
    """Pydantic ``ge=0.0`` enforces non-negative thresholds at the API boundary."""
    r = client.put(
        "/api/settings/pretp",
        json={"threshold_pct": -1.0},
    )
    assert r.status_code == 422


def test_settings_pretp_requires_auth(engine: _StubEngine) -> None:
    """Unauthenticated GET on the settings endpoint must 401."""
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    unauth_client = TestClient(app)
    r = unauth_client.get("/api/settings/pretp")
    assert r.status_code == 401
