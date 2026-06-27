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
    """Authenticated client — mints an all-access JWT (default tier).

    Used for READ endpoints.  Write endpoints (settings PUT, auto-mode
    POST) now require ``OWNER_TIER`` and will 403 with this client; use
    ``owner_client`` for those.
    """
    from src.api.auth import mint_token  # local import — pyjwt optional

    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def owner_client(engine: _StubEngine) -> TestClient:
    """Owner-tier client — mints a JWT with ``tier=OWNER_TIER``.

    Used for write endpoints (settings PUT, auto-mode POST) added
    2026-05-10 ahead of multi-tester invites.  Anon / all-access JWTs
    can READ but only owner-tier can mutate engine state.
    """
    from src.api.auth import mint_token, OWNER_TIER  # local import — pyjwt optional

    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    token = mint_token(secret=_TEST_SECRET, tier=OWNER_TIER)
    return TestClient(app, headers={"Authorization": f"Bearer {token}"})


@pytest.fixture
def auth_client(engine: _StubEngine) -> TestClient:
    """Static-token client — admin escape hatch, used by static-token tests below.

    Static token bypass is treated as OWNER (highest privilege), so this
    client also passes ``owner_required`` checks.
    """
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
# Request-latency observability middleware
# ---------------------------------------------------------------------------


def test_response_carries_server_timing_header(client: TestClient) -> None:
    """Every response exposes the server-measured duration so it can be
    correlated with Cloudflare/edge logs without log access on both sides.
    This is the outermost-middleware contract — it must hold for a plain
    200 like /api/health."""
    r = client.get("/api/health")
    assert r.status_code == 200
    assert "X-Response-Time-Ms" in r.headers
    # Header is a non-negative integer-ms string.
    val = float(r.headers["X-Response-Time-Ms"])
    assert val >= 0.0


def test_timing_header_present_on_error_responses(auth_client: TestClient) -> None:
    """The timing layer wraps failures too — a 401 still carries the header,
    proving the middleware is outermost (it sees the response the auth
    dependency short-circuited)."""
    # No bearer token → 401 from the auth dependency.
    r = auth_client.get("/api/pulse")
    assert r.status_code == 401
    assert "X-Response-Time-Ms" in r.headers


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


# ---------------------------------------------------------------------------
# /internal/diag/positions — operator-facing position state X-ray
# ---------------------------------------------------------------------------
#
# Owner-tier endpoint shipped to resolve a 2026-05-13 incident: positions
# closed on Binance (SL filled) showed ACTIVE in the Lumin app.  The diag
# endpoint surfaces what TradeMonitor._evaluate_signal compares against
# (stored SL + 1m candle wick + candle-feed age), letting the operator tell
# stale-feed, monitor-bug, and state-sync gaps apart from one X-ray.


class _StubMonitorStore:
    """Stub of HistoricalDataStore.get_candles + last_kline_age_seconds.

    Maps (symbol, interval) → {high: [...], low: [...]}.  Age map is parallel.
    """

    def __init__(self) -> None:
        self._buckets: Dict[Tuple[str, str], Dict[str, List[float]]] = {}
        self._ages: Dict[Tuple[str, str], Optional[float]] = {}

    def set(
        self,
        symbol: str,
        interval: str,
        *,
        high: float,
        low: float,
        age_sec: Optional[float],
    ) -> None:
        self._buckets[(symbol, interval)] = {"high": [high], "low": [low]}
        self._ages[(symbol, interval)] = age_sec

    def get_candles(self, symbol: str, interval: str):
        return self._buckets.get((symbol, interval))

    def last_kline_age_seconds(self, symbol: str, interval: str) -> Optional[float]:
        return self._ages.get((symbol, interval))


class _StubMonitor:
    def __init__(self, store: _StubMonitorStore, running: bool = True) -> None:
        self._store = store
        self._running = running


def _attach_monitor(engine: _StubEngine, **store_kwargs) -> _StubMonitorStore:
    """Helper: attach a _StubMonitor + populate its 1m candle for ETHUSDT."""
    store = _StubMonitorStore()
    # Default: fresh candle that does NOT breach the active sig's SL=2310.
    defaults = dict(symbol="ETHUSDT", interval="1m", high=2342.0, low=2334.0, age_sec=4.0)
    defaults.update(store_kwargs)
    store.set(**defaults)
    engine.monitor = _StubMonitor(store)  # type: ignore[attr-defined]
    return store


def test_positions_diag_requires_owner_tier(
    client: TestClient, owner_client: TestClient, engine: _StubEngine,
) -> None:
    """All-access JWT must 403; owner-tier must 200.

    Diag exposes internal monitor state — keep it behind the owner gate so
    a tester-tier JWT can't fan out the SL geometry of every active signal.
    """
    _attach_monitor(engine)
    assert client.get("/internal/diag/positions").status_code == 403
    assert owner_client.get("/internal/diag/positions").status_code == 200


def test_positions_diag_empty_when_no_signals(
    owner_client: TestClient, engine: _StubEngine,
) -> None:
    engine.router.active_signals.clear()
    _attach_monitor(engine)
    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["monitor_running"] is True
    assert "generated_at" in body


def test_positions_diag_surfaces_candle_extremes_and_age(
    owner_client: TestClient, engine: _StubEngine,
) -> None:
    _attach_monitor(engine, high=2342.0, low=2334.0, age_sec=4.0)
    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["symbol"] == "ETHUSDT"
    assert item["status"] == "ACTIVE"
    assert item["stop_loss"] == 2310.0
    assert item["candle_1m_high"] == 2342.0
    assert item["candle_1m_low"] == 2334.0
    assert item["candle_1m_age_sec"] == 4.0
    # LONG, candle_low (2334) > stop_loss (2310) → positive distance
    assert item["sl_breach_distance_pct"] is not None
    assert item["sl_breach_distance_pct"] > 0


def test_positions_diag_long_sl_breach_distance_negative_when_wick_past_sl(
    owner_client: TestClient, engine: _StubEngine,
) -> None:
    """Smoking-gun case the endpoint exists to detect.

    ETH active LONG with SL=2310; candle low wicks to 2305 (5 below SL) but
    signal status is still ACTIVE.  sl_breach_distance_pct must be negative
    so the operator sees the monitor failed to mark SL_HIT.
    """
    _attach_monitor(engine, high=2340.0, low=2305.0, age_sec=2.0)
    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    item = r.json()["items"][0]
    assert item["status"] == "ACTIVE"  # engine has NOT marked it terminal
    assert item["sl_breach_distance_pct"] is not None
    assert item["sl_breach_distance_pct"] < 0  # but the wick already broke SL


def test_positions_diag_short_sl_breach_distance_negative_when_wick_past_sl(
    owner_client: TestClient, engine: _StubEngine,
) -> None:
    """Same smoking-gun for SHORT — candle high wicks above stop_loss."""
    # Replace the seeded LONG with a SHORT, SL=2400, wick to 2410 → breached.
    engine.router.active_signals.clear()
    short_sig = _StubSignal(
        signal_id="sig-short-1",
        symbol="ETHUSDT",
        direction=_Direction("SHORT"),
        entry=2380.0,
        stop_loss=2400.0,
        tp1=2350.0,
        tp2=2330.0,
        status="ACTIVE",
        current_price=2410.0,
    )
    engine.router.active_signals[short_sig.signal_id] = short_sig
    _attach_monitor(engine, high=2410.0, low=2370.0, age_sec=3.0)

    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    item = r.json()["items"][0]
    assert item["direction"] == "SHORT"
    assert item["status"] == "ACTIVE"
    assert item["sl_breach_distance_pct"] is not None
    assert item["sl_breach_distance_pct"] < 0


def test_positions_diag_handles_missing_monitor_gracefully(
    owner_client: TestClient, engine: _StubEngine,
) -> None:
    """No monitor wired → candle fields zero, age None, sl_breach None.

    The builder must not 500; the dashboard renders 'monitor not running'
    instead and the operator knows to investigate the engine boot path.
    """
    # Make sure no monitor attribute is set on this engine.
    if hasattr(engine, "monitor"):
        delattr(engine, "monitor")
    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    body = r.json()
    assert body["monitor_running"] is False
    item = body["items"][0]
    assert item["candle_1m_high"] == 0.0
    assert item["candle_1m_low"] == 0.0
    assert item["candle_1m_age_sec"] is None
    assert item["sl_breach_distance_pct"] is None


def test_positions_diag_monitor_running_from_census_isolated_mode() -> None:
    """Isolated mode: no .monitor object, so liveness comes from the published
    task census. trade_monitor present → monitor_running True."""
    from types import SimpleNamespace

    from src.api.snapshot import build_positions_diag

    facade = SimpleNamespace(
        router=SimpleNamespace(active_signals={}),
        get_background_task_census=lambda: [
            "trade_monitor", "reconciler", "mark_price_feed",
        ],
    )
    # No .monitor attribute on the facade (matches RedisEngineFacade).
    assert not hasattr(facade, "monitor")
    resp = build_positions_diag(facade)
    assert resp.monitor_running is True
    assert resp.total == 0


def test_positions_diag_monitor_running_false_when_census_lacks_monitor() -> None:
    """Isolated mode: census present but trade_monitor absent → monitor_running
    False (a genuine dead-monitor signal, not masked by the reporting bug)."""
    from types import SimpleNamespace

    from src.api.snapshot import build_positions_diag

    facade = SimpleNamespace(
        router=SimpleNamespace(active_signals={}),
        get_background_task_census=lambda: ["reconciler", "mark_price_feed"],
    )
    resp = build_positions_diag(facade)
    assert resp.monitor_running is False


def test_positions_diag_skips_malformed_signal(
    owner_client: TestClient, engine: _StubEngine,
) -> None:
    """A corrupted signal in active_signals must not 500 the whole diag."""
    bad = _StubSignal(
        signal_id="BAD-DIAG-001",
        symbol="ZECUSDT",
        direction=_Direction("CORRUPTED"),
        entry=100.0,
        stop_loss=99.0,
        tp1=101.0,
        tp2=102.0,
    )
    engine.router.active_signals[bad.signal_id] = bad
    _attach_monitor(engine)
    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    body = r.json()
    # Either bad is sanitized (still appears) or skipped — both are valid.
    # Contract: no 500, and the legit signal is still in the response.
    ids = [it["signal_id"] for it in body["items"]]
    assert "sig-001" in ids


def test_positions_diag_returns_empty_on_builder_crash(
    owner_client: TestClient, engine: _StubEngine, monkeypatch,
) -> None:
    """If build_positions_diag itself raises, the endpoint returns a
    degraded empty response rather than 500."""
    from src.api import server as _server_mod

    def _broken(_engine):
        raise RuntimeError("simulated crash inside build_positions_diag")

    monkeypatch.setattr(_server_mod, "build_positions_diag", _broken)
    r = owner_client.get("/internal/diag/positions")
    assert r.status_code == 200
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["monitor_running"] is False


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


def test_auto_mode_post_switches(owner_client: TestClient, engine: _StubEngine) -> None:
    r = owner_client.post("/api/auto-mode", json={"mode": "off"})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["mode"] == "off"
    assert engine.last_mode_change == "off"


def test_auto_mode_post_same_mode_returns_409(
    owner_client: TestClient,
) -> None:
    r = owner_client.post("/api/auto-mode", json={"mode": "paper"})
    assert r.status_code == 409


def test_auto_mode_post_invalid_payload_returns_422(
    owner_client: TestClient,
) -> None:
    r = owner_client.post("/api/auto-mode", json={"mode": "yolo"})
    # Pydantic validation rejects literal mismatch with 422
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# Global kill switch — ops control plane HTTP surface (2026-06-20)
# ---------------------------------------------------------------------------


def test_kill_switch_get_uninitialised_reports_unavailable(
    client: TestClient,
) -> None:
    """With no Firestore/GCP creds (the test env), the kill switch never
    boots — GET must report ``initialised=false`` rather than a misleading
    ``engaged=false`` that looks like a live, safe state."""
    r = client.get("/api/kill-switch")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["initialised"] is False
    assert body["engaged"] is False


def test_kill_switch_post_uninitialised_returns_503(
    owner_client: TestClient,
) -> None:
    r = owner_client.post("/api/kill-switch", json={"engaged": True})
    assert r.status_code == 503


def test_kill_switch_post_requires_owner(client: TestClient) -> None:
    """Non-owner callers cannot flip the global halt."""
    r = client.post("/api/kill-switch", json={"engaged": True})
    assert r.status_code in (401, 403)


def test_kill_switch_engage_disengage_happy_path(
    owner_client: TestClient, monkeypatch,
) -> None:
    """Engage/disengage round-trip against a fake in-memory kill-switch
    client (the real one needs Firestore).  Pins that the endpoint calls
    engage_global with the reason and reflects the new state back."""
    from src.execution import kill_switch as ks

    class _FakeKS:
        def __init__(self) -> None:
            self.engaged = False
            self.reason: str | None = None

        def is_global_engaged(self) -> bool:
            return self.engaged

        def global_reason(self) -> str | None:
            return self.reason

        def engage_global(self, reason: str = "") -> None:
            self.engaged = True
            self.reason = reason

        def disengage_global(self) -> None:
            self.engaged = False
            self.reason = None

    fake = _FakeKS()
    monkeypatch.setattr(ks, "is_initialised", lambda: True)
    monkeypatch.setattr(ks, "get_client", lambda: fake)

    r = owner_client.post(
        "/api/kill-switch", json={"engaged": True, "reason": "manual halt"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["engaged"] is True
    assert body["initialised"] is True
    assert body["reason"] == "manual halt"
    assert fake.engaged is True

    r2 = owner_client.post("/api/kill-switch", json={"engaged": False})
    assert r2.status_code == 200
    assert r2.json()["engaged"] is False
    assert fake.engaged is False


def test_auto_trade_global_get_uninitialised(client: TestClient) -> None:
    r = client.get("/api/auto-trade-global")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["initialised"] is False
    assert body["enabled"] is False


def test_auto_trade_global_post_requires_owner(client: TestClient) -> None:
    r = client.post("/api/auto-trade-global", json={"enabled": True})
    assert r.status_code in (401, 403)


def test_auto_trade_global_enable_disable_happy_path(
    owner_client: TestClient, monkeypatch,
) -> None:
    from src.execution import kill_switch as ks

    class _FakeKS:
        def __init__(self) -> None:
            self.enabled = False

        def is_globally_enabled(self) -> bool:
            return self.enabled

        def enable_global_auto_trade(self) -> None:
            self.enabled = True

        def disable_global_auto_trade(self) -> None:
            self.enabled = False

    fake = _FakeKS()
    monkeypatch.setattr(ks, "is_initialised", lambda: True)
    monkeypatch.setattr(ks, "get_client", lambda: fake)

    r = owner_client.post("/api/auto-trade-global", json={"enabled": True})
    assert r.status_code == 200, r.text
    assert r.json()["enabled"] is True
    assert fake.enabled is True

    r2 = owner_client.post("/api/auto-trade-global", json={"enabled": False})
    assert r2.status_code == 200
    assert r2.json()["enabled"] is False
    assert fake.enabled is False


# ---------------------------------------------------------------------------
# Agents
# ---------------------------------------------------------------------------


def test_agents_returns_16_evaluators(client: TestClient) -> None:
    """API surface includes one entry per evaluator.  Session 29 added the
    16th evaluator (MOVER_TREND_PULLBACK; PR #318 added the 15th, MA_CROSS_TREND_SHIFT)."""
    r = client.get("/api/agents")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 16
    by_setup = {a["setup_class"]: a for a in body["items"]}
    assert "TREND_PULLBACK_EMA" in by_setup
    assert by_setup["TREND_PULLBACK_EMA"]["display_name"] == "The Pullback Sniper"
    assert by_setup["MOVER_TREND_PULLBACK"]["display_name"] == "The Momentum Rider"
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
    owner_client: TestClient, client: TestClient, tmp_path, monkeypatch,
) -> None:
    """PUT (owner) with one field must persist that field and leave others
    on default; subsequent GET (any tier) reflects the persisted state."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )

    r = owner_client.put(
        "/api/settings/pretp",
        json={"regime_allowlist": ["TRENDING_UP", "TRENDING_DOWN", "RANGING"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body["regime_allowlist"]) == {"TRENDING_UP", "TRENDING_DOWN", "RANGING"}
    # threshold_pct unchanged from default — was NOT in the PUT payload.
    from config import PRE_TP_THRESHOLD_PCT
    assert body["threshold_pct"] == PRE_TP_THRESHOLD_PCT

    # Re-GET (anon all-access tier) reflects the persisted state — read is open.
    r2 = client.get("/api/settings/pretp")
    assert set(r2.json()["regime_allowlist"]) == {
        "TRENDING_UP", "TRENDING_DOWN", "RANGING",
    }


def test_settings_pretp_put_accepts_ui_tokens(
    owner_client: TestClient, tmp_path, monkeypatch,
) -> None:
    """The app sends UI-friendly tokens (TRENDING / RANGING / CHOPPY); the
    server normalises to backend tokens on read so the engine sees the
    expanded set."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )

    r = owner_client.put(
        "/api/settings/pretp",
        json={"regime_allowlist": ["TRENDING", "RANGING"]},
    )
    assert r.status_code == 200
    body = r.json()
    assert set(body["regime_allowlist"]) == {
        "TRENDING_UP", "TRENDING_DOWN", "RANGING",
    }


def test_settings_pretp_put_rejects_negative_numeric(owner_client: TestClient) -> None:
    """Pydantic ``ge=0.0`` enforces non-negative thresholds at the API boundary."""
    r = owner_client.put(
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


# ---------------------------------------------------------------------------
# /api/settings/auto-trade — owner-flagged 2026-05-10 (Auto-trade page mock).
# ---------------------------------------------------------------------------


def test_settings_auto_trade_get_returns_resolved_view(
    client: TestClient, tmp_path, monkeypatch,
) -> None:
    """GET resolves the page state: mode + sizing knobs.  Defaults come from
    config when no user override exists."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    r = client.get("/api/settings/auto-trade")
    assert r.status_code == 200
    body = r.json()
    from config import POSITION_SIZE_PCT
    assert body["position_size_pct"] == pytest.approx(POSITION_SIZE_PCT)
    assert body["leverage_cap"] is not None
    assert body["max_concurrent_positions"] == 5


def test_settings_auto_trade_put_partial_payload_merges(
    owner_client: TestClient, client: TestClient, tmp_path, monkeypatch,
) -> None:
    """One-field PUT (owner) must persist; subsequent GET (any tier)
    reflects the persisted state and still has defaults for the rest."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    r = owner_client.put(
        "/api/settings/auto-trade",
        json={"position_size_pct": 4.5},
    )
    assert r.status_code == 200
    assert r.json()["position_size_pct"] == pytest.approx(4.5)

    r2 = client.get("/api/settings/auto-trade")
    assert r2.json()["position_size_pct"] == pytest.approx(4.5)
    assert r2.json()["max_concurrent_positions"] == 5  # untouched


def test_settings_auto_trade_put_clamps_leverage_to_hard_cap(
    owner_client: TestClient, tmp_path, monkeypatch,
) -> None:
    """B12: server clamps leverage_cap to ≤ 30.  Pydantic ``le=30.0``
    enforces this at the boundary; a legitimate-looking 30 must round-trip
    while >30 must 422."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    r = owner_client.put("/api/settings/auto-trade", json={"leverage_cap": 30.0})
    assert r.status_code == 200
    assert r.json()["leverage_cap"] == pytest.approx(30.0)

    r2 = owner_client.put("/api/settings/auto-trade", json={"leverage_cap": 50.0})
    assert r2.status_code == 422


def test_settings_auto_trade_put_routes_mode_through_engine(
    owner_client: TestClient, engine: _StubEngine, tmp_path, monkeypatch,
) -> None:
    """Mode change in the bundled PUT must invoke
    ``engine.set_auto_execution_mode`` so live state actually changes —
    not just the persisted preference."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    # Stub engine starts in "paper".  Switching to "live" exercises the
    # routing path; the stub records the attempt on ``last_mode_change``.
    r = owner_client.put(
        "/api/settings/auto-trade",
        json={"mode": "live", "position_size_pct": 3.0},
    )
    assert r.status_code == 200
    # Stub recorded the mode change.
    assert engine.last_mode_change == "live"
    # Sizing knob was still persisted alongside.
    assert user_settings.get_auto_trade()["position_size_pct"] == pytest.approx(3.0)


def test_settings_auto_trade_put_rejects_invalid_size(owner_client: TestClient) -> None:
    """Pydantic enforces ``gt=0`` and ``le=100`` on position_size_pct."""
    r = owner_client.put("/api/settings/auto-trade", json={"position_size_pct": 0.0})
    assert r.status_code == 422
    r = owner_client.put("/api/settings/auto-trade", json={"position_size_pct": 150.0})
    assert r.status_code == 422


def test_settings_auto_trade_requires_auth(engine: _StubEngine) -> None:
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    unauth_client = TestClient(app)
    r = unauth_client.get("/api/settings/auto-trade")
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# Owner-tier gate on write endpoints (added 2026-05-10 ahead of multi-tester
# invites).  Anon / all-access JWTs can READ all state but only owner-tier
# credentials can mutate engine config — without this gate, any tester
# could flip the engine into Live mode or change position size.
# ---------------------------------------------------------------------------


def test_anon_jwt_can_read_settings(client: TestClient) -> None:
    """Anon (default all-access) JWTs can still GET /api/settings/* —
    testers see the configured state, just can't write."""
    r1 = client.get("/api/settings/pretp")
    assert r1.status_code == 200
    r2 = client.get("/api/settings/auto-trade")
    assert r2.status_code == 200


def test_anon_jwt_cannot_put_pretp_settings(client: TestClient) -> None:
    """Anon JWT (default all-access tier) hitting PUT must 403 — owner-only."""
    r = client.put("/api/settings/pretp", json={"threshold_pct": 0.4})
    assert r.status_code == 403
    assert "owner" in r.json()["detail"].lower()


def test_anon_jwt_cannot_put_auto_trade_settings(client: TestClient) -> None:
    """Anon JWT hitting auto-trade PUT must 403."""
    r = client.put("/api/settings/auto-trade", json={"position_size_pct": 5.0})
    assert r.status_code == 403


def test_anon_jwt_cannot_post_auto_mode(client: TestClient) -> None:
    """Anon JWT cannot flip the engine's execution mode."""
    r = client.post("/api/auto-mode", json={"mode": "live"})
    assert r.status_code == 403


def test_owner_jwt_can_write_all_endpoints(
    owner_client: TestClient, engine: _StubEngine, tmp_path, monkeypatch,
) -> None:
    """Owner-tier JWT passes the gate on every write endpoint."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    assert owner_client.put(
        "/api/settings/pretp", json={"threshold_pct": 0.4}
    ).status_code == 200
    assert owner_client.put(
        "/api/settings/auto-trade", json={"position_size_pct": 5.0}
    ).status_code == 200
    assert owner_client.post(
        "/api/auto-mode", json={"mode": "off"}
    ).status_code == 200


def test_static_admin_token_treated_as_owner(
    auth_client: TestClient, tmp_path, monkeypatch,
) -> None:
    """The static admin token bypass passes ``owner_required`` so admin
    tooling (curl, scripts) can hit write endpoints without minting a JWT."""
    from src import user_settings
    monkeypatch.setattr(
        user_settings, "_STORE",
        user_settings._Store(path=str(tmp_path / "user_settings.json")),
    )
    r = auth_client.put(
        "/api/settings/auto-trade",
        json={"position_size_pct": 5.0},
        headers={"Authorization": "Bearer secret"},
    )
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Phase 2 — phone OTP auth + billing webhook
#
# These exercise the full /api/auth/request-otp -> /api/auth/verify-otp
# flow and the bot-side /internal/billing/grant webhook end-to-end.  The
# delivery provider is a stub that captures the issued code so the test
# can submit it back without scraping logs.
# ---------------------------------------------------------------------------


import hashlib as _hashlib  # noqa: E402
import hmac as _hmac  # noqa: E402
import json as _json  # noqa: E402
from datetime import datetime as _datetime, timedelta as _timedelta, timezone as _tz  # noqa: E402

_BILLING_SECRET = "phase2-billing-test-secret-x" * 2


class _CapturingDelivery:
    """Records every (phone, code) pair sent.  Returns OK / log channel."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send(self, phone_e164: str, code: str):
        from src.api.otp_delivery import DeliveryResult, DeliveryStatus

        self.sent.append((phone_e164, code))
        return DeliveryResult(
            status=DeliveryStatus.OK, channel_used="log", detail="captured",
        )


def _phase2_app(engine, tmp_path, *, billing_secret: str = _BILLING_SECRET):
    """Build a TestClient with the full Phase 2 stack wired in."""
    from src.api.billing_callback import BillingWebhookVerifier
    from src.api.otp import OtpStore
    from src.api.user_overrides import UserOverridesStore
    from src.api.users import UserStore

    db = tmp_path / "lumin.sqlite"
    user_store = UserStore(db)
    user_overrides = UserOverridesStore(db)
    otp_store = OtpStore(max_issues_per_hour=2, max_attempts_per_code=3)
    delivery = _CapturingDelivery()
    verifier = BillingWebhookVerifier(billing_secret)
    app = build_app(
        engine,
        jwt_secret=_TEST_SECRET,
        allow_static=False,
        user_store=user_store,
        user_overrides=user_overrides,
        otp_store=otp_store,
        otp_delivery=delivery,
        billing_verifier=verifier,
    )
    return TestClient(app), user_store, delivery


def _hmac_sig(body: bytes, secret: str = _BILLING_SECRET) -> str:
    return _hmac.new(secret.encode("utf-8"), body, _hashlib.sha256).hexdigest()


# ---- request-otp -----------------------------------------------------------


def test_request_otp_returns_503_when_unconfigured(engine: _StubEngine) -> None:
    """When the app is built without a UserStore, the endpoint should
    fail closed — phone-auth not configured."""
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    client = TestClient(app)
    r = client.post("/api/auth/request-otp", json={"phone": "+15551110000"})
    assert r.status_code == 503


def test_request_otp_sends_via_delivery_provider(engine: _StubEngine, tmp_path) -> None:
    client, _store, delivery = _phase2_app(engine, tmp_path)
    r = client.post("/api/auth/request-otp", json={"phone": "+15551110000"})
    assert r.status_code == 200
    assert r.json()["channel_used"] == "log"
    assert r.json()["expires_in_seconds"] == 300
    assert len(delivery.sent) == 1
    assert delivery.sent[0][0] == "+15551110000"
    assert len(delivery.sent[0][1]) == 6  # 6-digit code


def test_request_otp_rate_limited_returns_429(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    # Test fixture's max_issues_per_hour=2 — 3rd request gets 429.
    assert client.post("/api/auth/request-otp", json={"phone": "+15551110000"}).status_code == 200
    assert client.post("/api/auth/request-otp", json={"phone": "+15551110000"}).status_code == 200
    r = client.post("/api/auth/request-otp", json={"phone": "+15551110000"})
    assert r.status_code == 429
    assert "Retry-After" in r.headers


def test_request_otp_validates_phone_length(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    # Pydantic min_length=8 — too short.
    r = client.post("/api/auth/request-otp", json={"phone": "+1"})
    assert r.status_code == 422


# ---- verify-otp ------------------------------------------------------------


def test_verify_otp_creates_user_and_mints_user_token(
    engine: _StubEngine, tmp_path,
) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    client.post("/api/auth/request-otp", json={"phone": "+15551110000"})
    code = delivery.sent[-1][1]

    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110000", "code": code},
    )
    assert r.status_code == 200
    body = r.json()
    # New user → free tier by default; sub is user-<id>.
    assert body["tier"] == "free"
    assert body["sub"].startswith("user-")
    user = store.get_by_phone("+15551110000")
    assert user is not None
    assert body["sub"] == f"user-{user.user_id}"


def test_verify_otp_returning_user_keeps_tier(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    # Pre-existing paid user.
    user = store.get_or_create_by_phone("+15551110000")
    expiry = _datetime.now(_tz.utc) + _timedelta(days=30)
    store.set_tier(user.user_id, tier="paid", paid_until=expiry)

    client.post("/api/auth/request-otp", json={"phone": "+15551110000"})
    code = delivery.sent[-1][1]
    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110000", "code": code},
    )
    assert r.status_code == 200
    assert r.json()["tier"] == "paid"
    # paid_until must round-trip via the JWT payload.
    from src.api.auth import decode_token

    claims = decode_token(r.json()["token"], secret=_TEST_SECRET)
    assert claims.paid_until is not None
    # Truncate to seconds — JWT timestamps are int-seconds.
    assert int(claims.paid_until.timestamp()) == int(expiry.timestamp())


def test_verify_otp_no_record_returns_401(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    # Never issued — no record.
    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110000", "code": "123456"},
    )
    assert r.status_code == 401


def test_verify_otp_wrong_code_returns_401(engine: _StubEngine, tmp_path) -> None:
    client, _store, delivery = _phase2_app(engine, tmp_path)
    client.post("/api/auth/request-otp", json={"phone": "+15551110000"})
    real_code = delivery.sent[-1][1]
    wrong = "000000" if real_code != "000000" else "999999"
    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110000", "code": wrong},
    )
    assert r.status_code == 401


def test_verify_otp_validates_six_digit_code(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    # Pydantic enforces \d{6} pattern.
    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110000", "code": "abcdef"},
    )
    assert r.status_code == 422


# ---- /internal/billing/grant ----------------------------------------------


def test_billing_grant_503_when_unconfigured(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path, billing_secret="")
    body = _json.dumps(
        {"phone": "+15551110000", "tier": "paid", "paid_until_iso": None}
    ).encode()
    r = client.post(
        "/internal/billing/grant",
        content=body,
        headers={"X-Lumin-Sig": "deadbeef"},
    )
    assert r.status_code == 503


def test_billing_grant_invalid_signature_401(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    body = _json.dumps(
        {"phone": "+15551110000", "tier": "paid", "paid_until_iso": None}
    ).encode()
    # Sign with the wrong secret.
    bad_sig = _hmac.new(b"wrong-secret", body, _hashlib.sha256).hexdigest()
    r = client.post(
        "/internal/billing/grant",
        content=body,
        headers={"X-Lumin-Sig": bad_sig},
    )
    assert r.status_code == 401


def test_billing_grant_missing_signature_header_401(
    engine: _StubEngine, tmp_path,
) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    body = _json.dumps(
        {"phone": "+15551110000", "tier": "paid", "paid_until_iso": None}
    ).encode()
    r = client.post("/internal/billing/grant", content=body)
    assert r.status_code == 401


def test_billing_grant_creates_user_and_sets_tier(
    engine: _StubEngine, tmp_path,
) -> None:
    """First grant for an unseen phone — bot pre-pays a tier on behalf of
    a new tester before they've done OTP signin."""
    client, store, _delivery = _phase2_app(engine, tmp_path)
    expiry = (_datetime.now(_tz.utc) + _timedelta(days=30)).replace(microsecond=0)
    body = _json.dumps(
        {
            "phone": "+15551110000",
            "tier": "paid",
            "paid_until_iso": expiry.isoformat(),
        }
    ).encode()
    r = client.post(
        "/internal/billing/grant",
        content=body,
        headers={"X-Lumin-Sig": _hmac_sig(body)},
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True
    user = store.get_by_phone("+15551110000")
    assert user is not None
    assert user.tier == "paid"
    assert user.paid_until == expiry


def test_billing_grant_revokes_to_free(engine: _StubEngine, tmp_path) -> None:
    """paid_until_iso=null = downgrade.  Used when subscription expires
    or is cancelled."""
    client, store, _delivery = _phase2_app(engine, tmp_path)
    # First, grant paid.
    user = store.get_or_create_by_phone("+15551110000")
    store.set_tier(
        user.user_id, tier="paid",
        paid_until=_datetime.now(_tz.utc) + _timedelta(days=30),
    )
    # Now revoke.
    body = _json.dumps(
        {"phone": "+15551110000", "tier": "free", "paid_until_iso": None}
    ).encode()
    r = client.post(
        "/internal/billing/grant",
        content=body,
        headers={"X-Lumin-Sig": _hmac_sig(body)},
    )
    assert r.status_code == 200
    user_after = store.get_by_phone("+15551110000")
    assert user_after.tier == "free"
    assert user_after.paid_until is None


def test_billing_grant_rejects_invalid_iso(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    body = _json.dumps(
        {
            "phone": "+15551110000",
            "tier": "paid",
            "paid_until_iso": "not-a-real-date",
        }
    ).encode()
    r = client.post(
        "/internal/billing/grant",
        content=body,
        headers={"X-Lumin-Sig": _hmac_sig(body)},
    )
    assert r.status_code == 422


def test_billing_grant_rejects_unknown_tier(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    body = _json.dumps(
        {"phone": "+15551110000", "tier": "platinum", "paid_until_iso": None}
    ).encode()
    r = client.post(
        "/internal/billing/grant",
        content=body,
        headers={"X-Lumin-Sig": _hmac_sig(body)},
    )
    # Pydantic Literal["free","paid","owner"] rejects "platinum".
    assert r.status_code == 422


# =============================================================================
# Phase 3 — needs_onboarding + /api/profile
# =============================================================================


def _verify_and_get_token(client, store, delivery, phone: str) -> str:
    """Issue + verify an OTP for ``phone``.  Returns the minted JWT."""
    client.post("/api/auth/request-otp", json={"phone": phone})
    code = delivery.sent[-1][1]
    r = client.post("/api/auth/verify-otp", json={"phone": phone, "code": code})
    assert r.status_code == 200, r.text
    return r.json()["token"]


# ---- needs_onboarding in token responses -----------------------------------


def test_verify_otp_new_user_needs_onboarding_true(engine: _StubEngine, tmp_path) -> None:
    client, _store, delivery = _phase2_app(engine, tmp_path)
    client.post("/api/auth/request-otp", json={"phone": "+15551110001"})
    code = delivery.sent[-1][1]
    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110001", "code": code},
    )
    body = r.json()
    assert body["needs_onboarding"] is True


def test_verify_otp_onboarded_user_needs_onboarding_false(
    engine: _StubEngine, tmp_path,
) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    # Pre-onboard.
    user = store.get_or_create_by_phone("+15551110002")
    store.update_profile(
        user.user_id, display_name="Eve", accept_terms=True,
    )
    # Verify OTP — token should report onboarded.
    client.post("/api/auth/request-otp", json={"phone": "+15551110002"})
    code = delivery.sent[-1][1]
    r = client.post(
        "/api/auth/verify-otp",
        json={"phone": "+15551110002", "code": code},
    )
    assert r.json()["needs_onboarding"] is False


def test_anonymous_token_needs_onboarding_true(engine: _StubEngine, tmp_path) -> None:
    """/api/auth/anonymous is retired (Firebase Phone Auth replaced it) → 410 Gone."""
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    r = client.post("/api/auth/anonymous")
    assert r.status_code == 410


def test_refresh_carries_onboarding_state(engine: _StubEngine, tmp_path) -> None:
    """/api/auth/refresh is retired (Firebase Phone Auth replaced it) → 410 Gone."""
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15551110003")
    r = client.post("/api/auth/refresh", json={"token": token})
    assert r.status_code == 410


# ---- /api/profile GET ------------------------------------------------------


def test_profile_get_returns_user_row(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15551110010")
    r = client.get(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["phone_e164"] == "+15551110010"
    assert body["tier"] == "free"
    assert body["needs_onboarding"] is True
    assert body["display_name"] is None
    assert body["onboarded_at"] is None


def test_profile_get_requires_auth(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    r = client.get("/api/profile")
    assert r.status_code == 401


def test_profile_get_rejects_anonymous_device_token(
    engine: _StubEngine, tmp_path,
) -> None:
    """/api/auth/anonymous is retired → 410 Gone (can't mint device-id token)."""
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    r = client.post("/api/auth/anonymous")
    assert r.status_code == 410


# ---- /api/profile PUT ------------------------------------------------------


def test_profile_put_completes_onboarding(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15551110020")
    r = client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "display_name": "Grace",
            "country_code": "SG",
            "timezone": "Asia/Singapore",
            "currency": "USD",
            "accept_terms": True,
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["display_name"] == "Grace"
    assert body["country_code"] == "SG"
    assert body["timezone"] == "Asia/Singapore"
    assert body["currency"] == "USD"
    assert body["needs_onboarding"] is False
    assert body["onboarded_at"] is not None


def test_profile_put_partial_does_not_clobber_fields(
    engine: _StubEngine, tmp_path,
) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15551110021")
    # Initial fill.
    client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "display_name": "Henry",
            "country_code": "AE",
            "timezone": "Asia/Dubai",
            "currency": "AED",
            "accept_terms": True,
        },
    )
    # Partial — only change display_name.
    r = client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Henry K."},
    )
    body = r.json()
    assert body["display_name"] == "Henry K."
    assert body["country_code"] == "AE"
    assert body["timezone"] == "Asia/Dubai"
    assert body["currency"] == "AED"
    assert body["needs_onboarding"] is False  # latched on


def test_profile_put_without_terms_stays_unonboarded(
    engine: _StubEngine, tmp_path,
) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15551110022")
    r = client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"display_name": "Ivy", "accept_terms": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["display_name"] == "Ivy"
    assert body["needs_onboarding"] is True  # terms not accepted yet
    assert body["onboarded_at"] is None


def test_profile_put_validates_country_code_length(
    engine: _StubEngine, tmp_path,
) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15551110023")
    r = client.put(
        "/api/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"country_code": "USA"},  # 3 chars; pydantic min/max=2
    )
    assert r.status_code == 422


# =============================================================================
# Phase 2 — per-user settings overrides
# =============================================================================


# ---- /api/settings/user/pretp ----------------------------------------------


def test_user_pretp_get_returns_defaults_for_fresh_user(
    engine: _StubEngine, tmp_path,
) -> None:
    """A user with no overrides sees the engine's effective defaults
    + ``using_defaults=true``."""
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330001")
    r = client.get(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["using_defaults"] is True
    # Engine defaults (config) are exposed via the same schema.
    assert "threshold_pct" in body
    assert "atr_multiplier" in body
    # OWNER_BRIEF B17 (2026-05-17) — manual-entry protection defaults ON
    # so manual operators get capital preservation without an opt-in step.
    assert body.get("protect_manual_entries") is True


def test_user_pretp_protect_manual_entries_round_trip(
    engine: _StubEngine, tmp_path,
) -> None:
    """User-set False survives the GET→PUT→GET cycle and flips
    ``using_defaults`` to False even when it's the only field touched."""
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330099")
    r = client.put(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token}"},
        json={"protect_manual_entries": False},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["protect_manual_entries"] is False
    assert body["using_defaults"] is False

    # Re-read confirms persistence.
    r2 = client.get(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token}"},
    )
    body2 = r2.json()
    assert body2["protect_manual_entries"] is False
    assert body2["using_defaults"] is False


def test_user_pretp_put_persists_override(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330002")
    r = client.put(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token}"},
        json={"threshold_pct": 0.50, "enabled": True},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["using_defaults"] is False
    assert body["threshold_pct"] == 0.50
    assert body["enabled"] is True


def test_user_pretp_partial_put_merges(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330003")
    client.put(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token}"},
        json={"threshold_pct": 0.50},
    )
    # Second PUT touches a different field — first override survives.
    r = client.put(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token}"},
        json={"atr_multiplier": 0.75},
    )
    body = r.json()
    assert body["threshold_pct"] == 0.50
    assert body["atr_multiplier"] == 0.75


def test_user_pretp_isolated_per_user(engine: _StubEngine, tmp_path) -> None:
    """User A's overrides don't leak into User B's view."""
    client, store, delivery = _phase2_app(engine, tmp_path)
    token_a = _verify_and_get_token(client, store, delivery, "+15553330010")
    token_b = _verify_and_get_token(client, store, delivery, "+15553330011")
    client.put(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"threshold_pct": 0.99},
    )
    # User B should still see engine default.
    r = client.get(
        "/api/settings/user/pretp",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    body = r.json()
    assert body["using_defaults"] is True
    assert body["threshold_pct"] != 0.99


def test_user_pretp_requires_auth(engine: _StubEngine, tmp_path) -> None:
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    r = client.get("/api/settings/user/pretp")
    assert r.status_code == 401


def test_user_pretp_rejects_anonymous_token(engine: _StubEngine, tmp_path) -> None:
    """/api/auth/anonymous is retired → 410 Gone (device-id token path removed)."""
    client, _store, _delivery = _phase2_app(engine, tmp_path)
    r = client.post("/api/auth/anonymous")
    assert r.status_code == 410


# ---- /api/settings/user/auto-trade -----------------------------------------


def test_user_auto_trade_get_returns_defaults(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330020")
    r = client.get(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["using_defaults"] is True
    assert "position_size_pct" in body


def test_user_auto_trade_mode_does_not_inherit_engine_default(
    engine: _StubEngine, tmp_path,
) -> None:
    """**Per-user isolation pin.**  ``mode`` must be ``None`` for a user
    who has never written their own row, regardless of what the
    engine's running ``auto_execution_mode`` is.

    Owner-reported 2026-05-23: "trade > paper there it's still showing
    default on" + "many owner changes are applying to all users".
    The pre-fix endpoint inherited ``mode`` from the engine-wide
    ``_build_auto_trade_view()`` baseline, so the Lumin app's Paper
    tab toggle (which reads ``userSettings.mode == "paper"``) lit up
    "on" for every signed-in user as long as the engine ran in paper.

    Other override fields (``position_size_pct``, ``leverage_cap``,
    ``max_concurrent_positions``) legitimately inherit engine
    defaults — they're operator-set baselines, not per-user state.
    Only ``mode`` is the per-user opt-in bit.
    """
    # Pin the engine into 'paper' (the typical operator default).
    engine.auto_execution_mode = "paper"

    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330022")
    body = client.get(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    # The headline regression: ``mode`` must NOT carry the engine's
    # 'paper' over to a fresh user.
    assert body["mode"] is None, (
        f"Fresh user should see mode=None, got {body['mode']!r}.  "
        "The pre-fix endpoint leaked the engine's running mode here."
    )
    # Other engine-default fields still come through as before.
    assert body["using_defaults"] is True
    assert "position_size_pct" in body
    assert "leverage_cap" in body


def test_user_auto_trade_put_persists_override(
    engine: _StubEngine, tmp_path,
) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330021")
    r = client.put(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
        json={"position_size_pct": 1.0, "leverage_cap": 10.0},
    )
    body = r.json()
    assert body["using_defaults"] is False
    assert body["position_size_pct"] == 1.0
    assert body["leverage_cap"] == 10.0


def test_user_auto_trade_mode_does_not_flip_engine_global(
    engine: _StubEngine, tmp_path,
) -> None:
    """Per-user mode is stored but does NOT call set_auto_execution_mode.

    The engine global mode stays unchanged — Phase 3 wires per-user
    execution on the app side; until then the engine still operates in
    whatever mode the operator picked.
    """
    client, store, delivery = _phase2_app(engine, tmp_path)
    # Sanity: stub engine starts in some mode (off / paper / live).
    initial_mode = getattr(engine, "auto_execution_mode", None)
    token = _verify_and_get_token(client, store, delivery, "+15553330030")
    client.put(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
        json={"mode": "live"},
    )
    # Engine's own mode is untouched.
    assert getattr(engine, "auto_execution_mode", None) == initial_mode
    # But the user's stored override reflects the change.
    body = client.get(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    assert body["mode"] == "live"


def test_user_auto_trade_clamps_leverage(engine: _StubEngine, tmp_path) -> None:
    """B12: leverage_cap > 30 must be clamped to 30 at the store layer."""
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330031")
    # Pydantic le=30 on the schema rejects 100 with 422 — verify the
    # write path's coercion isn't reachable for over-cap values.
    r = client.put(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
        json={"leverage_cap": 100.0},
    )
    assert r.status_code == 422


def test_user_auto_trade_isolated_per_user(engine: _StubEngine, tmp_path) -> None:
    client, store, delivery = _phase2_app(engine, tmp_path)
    a = _verify_and_get_token(client, store, delivery, "+15553330040")
    b = _verify_and_get_token(client, store, delivery, "+15553330041")
    client.put(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {a}"},
        json={"position_size_pct": 5.0},
    )
    body = client.get(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {b}"},
    ).json()
    assert body["using_defaults"] is True
    assert body["position_size_pct"] != 5.0


def test_user_auto_trade_paper_preferences_round_trip(
    engine: _StubEngine, tmp_path,
) -> None:
    """The PAPER eligibility triple must survive the HTTP boundary.

    Regression guard: the ``paper_symbol/path/regime_preference`` columns
    and their per-user-paper-book consumer (``PaperBookFanout._eligible``)
    shipped in #636, but the ``AutoTradeSettings`` Pydantic schema did not
    declare the fields — so a PUT carrying them was silently dropped by
    Pydantic (extra-ignore) and the app had nothing to write to.  This
    pins that the keys now PUT, persist, and GET back, independently of
    the LIVE triple (a user paper-tests one set while live-trading
    another)."""
    client, store, delivery = _phase2_app(engine, tmp_path)
    token = _verify_and_get_token(client, store, delivery, "+15553330050")
    r = client.put(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "path_preference": ["MOMENTUM_BREAKOUT"],
            "paper_symbol_preference": ["BTCUSDT", "ETHUSDT"],
            "paper_path_preference": ["DIVERGENCE_CONTINUATION"],
            "paper_regime_preference": ["TRENDING"],
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    # Paper triple persisted and is returned by the same view.
    assert body["paper_symbol_preference"] == ["BTCUSDT", "ETHUSDT"]
    assert body["paper_path_preference"] == ["DIVERGENCE_CONTINUATION"]
    # Regime gets the same UI-token→backend-label normalisation as the
    # live triple (TRENDING → TRENDING_UP / TRENDING_DOWN).
    assert set(body["paper_regime_preference"]) == {
        "TRENDING_UP",
        "TRENDING_DOWN",
    }
    # Independent of the LIVE triple set in the same payload.
    assert body["path_preference"] == ["MOMENTUM_BREAKOUT"]
    # Survives a fresh GET (not just the PUT echo).
    got = client.get(
        "/api/settings/user/auto-trade",
        headers={"Authorization": f"Bearer {token}"},
    ).json()
    assert got["paper_symbol_preference"] == ["BTCUSDT", "ETHUSDT"]
    assert got["paper_path_preference"] == ["DIVERGENCE_CONTINUATION"]
    assert set(got["paper_regime_preference"]) == {
        "TRENDING_UP",
        "TRENDING_DOWN",
    }


# ============================================================================
# Build-positions broker-state filter (fix/positions-skip-broker-rejected)
# ============================================================================
# Owner-reported 2026-05-17: Lumin OPEN POSITIONS card showed 4-5 phantom
# rows at qty=0 alongside 1 real broker-active position visible in the
# trade_records list.  Root cause: ``sig.qty`` was never set anywhere in
# the engine; it always defaulted to 0.  ``build_positions`` rendered
# every router signal as a position regardless of whether the paper
# broker had actually opened one (qty_zero_guard from PR #401 would
# return None and skip the open, but the signal lived on in the router).


class _StubPaperPosition:
    """Minimal stand-in for ``PaperOrderManager._PaperPosition`` — only
    the two fields ``build_positions`` reads when enriching qty from
    the broker (quantity + closed_quantity)."""
    def __init__(self, quantity: float, closed_quantity: float = 0.0):
        self.quantity = quantity
        self.closed_quantity = closed_quantity


class _StubPaperBroker:
    """Minimal duck-type of ``PaperOrderManager`` — ``build_positions``
    only inspects ``_positions`` (the dict signal_id → _PaperPosition).
    Other broker methods aren't called from build_positions; we keep
    the surface intentionally small."""
    def __init__(self, positions: Dict[str, _StubPaperPosition]):
        self._positions = positions


def test_positions_filters_signals_without_broker_position(
    client: TestClient, engine: _StubEngine,
) -> None:
    """When a paper broker is wired AND lacks a position for a given
    signal_id, ``/api/positions`` must skip that signal — it's a phantom
    from the router's signal-tracking machinery (e.g. broker rejected
    via qty_zero_guard / notional_floor / risk gate).

    Without this filter the OPEN POSITIONS card showed 4-5 ghost rows
    at qty=0 (2026-05-17 owner-reported bug).
    """
    # Wire a paper broker with EMPTY positions — broker has no record of
    # any signal_id, even though the router has sig-001 active.
    engine._order_manager = _StubPaperBroker(positions={})

    r = client.get("/api/positions")
    assert r.status_code == 200, r.text
    body = r.json()
    # Pre-fix: returns the active router signal (sig-001) at qty=0.
    # Post-fix: returns empty — the broker filter scrubs out phantoms.
    assert body["total"] == 0, (
        "Phantom positions slipping through broker-state filter — "
        f"got {body['total']} rows when broker has no positions"
    )


def test_positions_returns_only_broker_active(
    client: TestClient, engine: _StubEngine,
) -> None:
    """When the broker has SOME positions, ``/api/positions`` must
    return ONLY those, scrubbing router signals the broker doesn't
    have entries for.
    """
    # Add a second signal to the router; only the first is "in" the
    # broker's positions.  Both directions valid for the Pydantic schema.
    now = datetime.now(timezone.utc)
    sig_2 = _StubSignal(
        signal_id="sig-002-broker-rejected",
        symbol="DOGEUSDT",
        direction=_Direction("SHORT"),
        entry=0.12,
        stop_loss=0.13,
        tp1=0.11,
        tp2=0.10,
        current_price=0.12,
        pnl_pct=0.0,
        timestamp=now - timedelta(minutes=5),
        dispatch_timestamp=now - timedelta(minutes=5),
    )
    engine.router.active_signals[sig_2.signal_id] = sig_2

    # Broker has the first signal (sig-001 / ETHUSDT) but NOT sig-002.
    engine._order_manager = _StubPaperBroker(positions={
        "sig-001": _StubPaperPosition(quantity=0.0429),
    })

    r = client.get("/api/positions")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1
    p = body["items"][0]
    assert p["signal_id"] == "sig-001"
    # Quantity sourced from broker (0.0429 — not the always-zero sig.qty
    # the pre-fix path used).
    assert p["qty"] == pytest.approx(0.0429, rel=1e-6)


def test_positions_uses_broker_residual_after_partial_close(
    client: TestClient, engine: _StubEngine,
) -> None:
    """The broker tracks ``quantity`` (original) and ``closed_quantity``
    (already-closed partials).  The OPEN-positions display should show
    the RESIDUAL (quantity − closed_quantity) — the still-riding slice.

    Example: pre-TP banked 50%, residual rides → broker has
    quantity=100, closed_quantity=50 → display shows qty=50.
    """
    engine._order_manager = _StubPaperBroker(positions={
        "sig-001": _StubPaperPosition(quantity=100.0, closed_quantity=50.0),
    })

    r = client.get("/api/positions")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["qty"] == pytest.approx(50.0, rel=1e-6)


def test_positions_no_broker_falls_back_to_router_signals(
    client: TestClient, engine: _StubEngine,
) -> None:
    """When no order_manager is wired (signal-only mode / live mode where
    Binance is the position source, queried app-side), the broker-state
    filter is skipped and every router signal renders.  Backward-compat
    with the pre-2026-05-17 behaviour.
    """
    # No _order_manager on the engine.
    assert not hasattr(engine, "_order_manager") or engine._order_manager is None

    r = client.get("/api/positions")
    assert r.status_code == 200, r.text
    body = r.json()
    # The default fixture has one active router signal — it should render
    # even though there's no broker tracking it.
    assert body["total"] == 1
    assert body["items"][0]["symbol"] == "ETHUSDT"


# ---------------------------------------------------------------------------
# Auto-pause resume endpoint (2026-05-24 — consecutive -2019 fix)
# ---------------------------------------------------------------------------


def _auth_user_token(user_id: int = 1) -> str:
    from src.api.auth import mint_token
    return mint_token(secret=_TEST_SECRET, sub=f"user-{user_id}")


def test_auto_mode_resume_mine_returns_false_when_not_paused(
    engine, tmp_path,
) -> None:
    """Idempotent on a non-paused user — no-op, returns resumed=False."""
    client, user_store, _ = _phase2_app(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")  # uid=1
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    r = client.post("/api/auto-mode/resume-mine")
    assert r.status_code == 200
    assert r.json() == {"resumed": False}


def _phase2_app_with_overrides(engine, tmp_path):
    """Variant of _phase2_app that also returns the UserOverridesStore.

    _phase2_app encapsulates the build but doesn't expose the overrides
    store; rebuilding the same surface here so tests can drive the
    pause-state directly. Matches the production wiring in
    src/bootstrap.py which constructs the store and passes it to
    build_app.
    """
    from src.api.billing_callback import BillingWebhookVerifier
    from src.api.otp import OtpStore
    from src.api.user_overrides import UserOverridesStore
    from src.api.users import UserStore

    db = tmp_path / "lumin.sqlite"
    user_store = UserStore(db)
    user_overrides = UserOverridesStore(db)
    otp_store = OtpStore(max_issues_per_hour=2, max_attempts_per_code=3)
    delivery = _CapturingDelivery()
    verifier = BillingWebhookVerifier(_BILLING_SECRET)
    app = build_app(
        engine,
        jwt_secret=_TEST_SECRET,
        allow_static=False,
        user_store=user_store,
        user_overrides=user_overrides,
        otp_store=otp_store,
        otp_delivery=delivery,
        billing_verifier=verifier,
    )
    return TestClient(app), user_store, user_overrides


def test_auto_mode_resume_mine_clears_pause(
    engine, tmp_path,
) -> None:
    """When the user is paused, the endpoint clears the pause and
    returns resumed=True; a second call returns False (idempotent)."""
    client, user_store, store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")  # uid=1
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    store.update_auto_trade(1, {"mode": "live"})
    store.pause_user_auto_trade(1, "insufficient_margin")
    assert store.is_user_auto_paused(1) is True
    r1 = client.post("/api/auto-mode/resume-mine")
    assert r1.status_code == 200
    assert r1.json() == {"resumed": True}
    assert store.is_user_auto_paused(1) is False
    # Idempotent.
    r2 = client.post("/api/auto-mode/resume-mine")
    assert r2.status_code == 200
    assert r2.json() == {"resumed": False}


def test_user_auto_trade_get_surfaces_pause_state(
    engine, tmp_path,
) -> None:
    """The user's auto-trade view includes paused_reason + paused_at
    when paused so the app can render a banner."""
    client, user_store, store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    store.update_auto_trade(1, {"mode": "live"})
    store.pause_user_auto_trade(1, "insufficient_margin")
    r = client.get("/api/settings/user/auto-trade")
    assert r.status_code == 200
    body = r.json()
    assert body["paused_reason"] == "insufficient_margin"
    assert body["paused_at"]


# ---------------------------------------------------------------------------
# /api/pnl/history per-user filter (2026-05-24 — paper "confusion" follow-up)
# ---------------------------------------------------------------------------


def test_pnl_history_paper_falls_back_to_engine_when_no_user(
    engine, tmp_path,
) -> None:
    """Anonymous device-token callers (sub like ``device-X``) get the
    engine-wide paper ledger — pre-2026-05-24 behaviour, preserved as
    fallback so OTP / landing-page flows don't 404."""
    from src.api.auth import mint_token
    from src.auto_trade import pnl_history
    pnl_history.record_close("paper", 5.50)
    client, _user_store, _store = _phase2_app_with_overrides(engine, tmp_path)
    client.headers["Authorization"] = (
        f"Bearer {mint_token(secret=_TEST_SECRET)}"
    )
    r = client.get("/api/pnl/history?mode=paper&days=7")
    assert r.status_code == 200
    assert r.json()["weekly_pnl_usd"] == 5.50


def test_pnl_history_paper_excludes_trades_before_user_subscribed(
    engine, tmp_path,
) -> None:
    """Trades closed BEFORE the user opened their paper subscription
    are NOT visible to them — the whole point of the filter."""
    from src.auto_trade import pnl_history, trade_records
    pnl_history.record_close("paper", 99.0)
    trade_records.open_trade(
        signal_id="USR-A", symbol="BTCUSDT", side="long",
        entry=30000.0, qty=0.01, leverage=10.0, position_size_pct=2.0,
    )
    trade_records.close_trade(
        signal_id="USR-A", close_reason="tp1",
        close_price=30300.0, gross_pnl_usd=3.0, fees_usd=0.18,
        net_pnl_usd=2.82,
    )
    client, user_store, store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    store.update_auto_trade(1, {"mode": "paper"})
    r = client.get("/api/pnl/history?mode=paper&days=7")
    assert r.status_code == 200
    assert r.json()["weekly_pnl_usd"] == 0.0


def test_pnl_history_paper_includes_trades_inside_user_window(
    engine, tmp_path,
) -> None:
    """Trades closed AFTER the user opens their paper subscription
    DO appear in their per-user pnl_history view."""
    from src.auto_trade import trade_records
    client, user_store, store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    store.update_auto_trade(1, {"mode": "paper"})
    trade_records.open_trade(
        signal_id="USR-AFTER", symbol="ETHUSDT", side="long",
        entry=3000.0, qty=0.1, leverage=10.0, position_size_pct=2.0,
    )
    trade_records.close_trade(
        signal_id="USR-AFTER", close_reason="tp1",
        close_price=3030.0, gross_pnl_usd=3.0, fees_usd=0.18,
        net_pnl_usd=2.82,
    )
    r = client.get("/api/pnl/history?mode=paper&days=7")
    assert r.status_code == 200
    assert r.json()["weekly_pnl_usd"] == 2.82


def test_pnl_history_live_mode_stays_engine_wide(
    engine, tmp_path,
) -> None:
    """Live-mode PnL stays engine-wide — per-user live PnL is Phase 4
    work (each user has their own Binance ledger; per-user
    reconciliation against dispatch_log ships then)."""
    from src.auto_trade import pnl_history
    pnl_history.record_close("live", 3.30)
    client, user_store, store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    store.update_auto_trade(1, {"mode": "paper"})
    r = client.get("/api/pnl/history?mode=live&days=7")
    assert r.status_code == 200
    assert r.json()["weekly_pnl_usd"] == 3.30


# ---------------------------------------------------------------------------
# /api/referral (Phase 1: free invite/share tracking, no reward — 2026-06-27)
# ---------------------------------------------------------------------------


def test_referral_me_returns_503_when_unconfigured(engine: _StubEngine) -> None:
    app = build_app(engine, jwt_secret=_TEST_SECRET, allow_static=False)
    client = TestClient(app)
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    r = client.get("/api/referral/me")
    assert r.status_code == 503


def test_referral_me_generates_code_and_starts_at_zero(
    engine, tmp_path,
) -> None:
    client, user_store, _store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    r = client.get("/api/referral/me")
    assert r.status_code == 200
    body = r.json()
    assert len(body["code"]) == 7
    assert body["referred_count"] == 0
    # Stable across repeated calls.
    r2 = client.get("/api/referral/me")
    assert r2.json()["code"] == body["code"]


def test_referral_claim_success_via_endpoint(engine, tmp_path) -> None:
    client, user_store, _store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")  # uid=1, referrer
    user_store.get_or_create_by_phone("+15550000002")  # uid=2, referee
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    code = client.get("/api/referral/me").json()["code"]

    client.headers["Authorization"] = f"Bearer {_auth_user_token(2)}"
    r = client.post("/api/referral/claim", json={"code": code})
    assert r.status_code == 200
    assert r.json() == {"ok": True, "reason": None}

    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    assert client.get("/api/referral/me").json()["referred_count"] == 1


def test_referral_claim_self_referral_rejected_via_endpoint(
    engine, tmp_path,
) -> None:
    client, user_store, _store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    code = client.get("/api/referral/me").json()["code"]
    r = client.post("/api/referral/claim", json={"code": code})
    assert r.status_code == 200
    assert r.json() == {"ok": False, "reason": "self_referral"}


def test_referral_claim_unknown_code_rejected_via_endpoint(
    engine, tmp_path,
) -> None:
    client, user_store, _store = _phase2_app_with_overrides(engine, tmp_path)
    user_store.get_or_create_by_phone("+15550000001")
    client.headers["Authorization"] = f"Bearer {_auth_user_token(1)}"
    r = client.post("/api/referral/claim", json={"code": "NOSUCH1"})
    assert r.status_code == 200
    assert r.json() == {"ok": False, "reason": "invalid_code"}
