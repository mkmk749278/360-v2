"""Per-pair chart context (Charts redesign part 3, 2026-09-25).

Pins the three things the app's chart screen relies on:

* ``build_one`` reads the engine's real store shapes (``Level``,
  ``VolumeProfileResult``, ``StructureState``) — driven with the real
  dataclasses, not dicts of keys chosen here;
* the checklist is symmetric and never scores;
* the route's three states (covered / not_tracked / not_reported), the
  checklist following live access, and past signals being the pair's own
  closed record only.
"""

from __future__ import annotations

import json
import time

import numpy as np
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src import pair_context as pc  # noqa: E402
from src import track_record  # noqa: E402
from src.api import firebase_auth  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import UserStore  # noqa: E402
from src.level_book import Level  # noqa: E402
from src.structure_state import StructureState  # noqa: E402
from src.volume_profile import VolumeProfileResult  # noqa: E402

from tests.api.test_api_smoke import _StubEngine  # noqa: E402


class _Book:
    def __init__(self, levels):
        self._levels = levels

    def get_levels(self, symbol):
        return list(self._levels)

    def last_refresh_ts(self, symbol):
        return 1_790_000_000.0


class _VP:
    def __init__(self, res):
        self._res = res

    def get(self, symbol):
        return self._res


class _Tracker:
    def __init__(self, st):
        self._st = st

    def get_state(self, symbol, tf="4h"):
        return self._st


class _Store:
    def __init__(self, close):
        self._c = {"close": np.array([close * 0.99, close])}

    def get_candles(self, symbol, tf):
        return self._c


class _Scanner:
    def __init__(self, *, levels, vp, st):
        self.level_book = _Book(levels)
        self.volume_profile_store = _VP(vp)
        self.structure_tracker = _Tracker(st)


def _scanner(price=100.0, state="BULL_LEG"):
    levels = [
        Level(price=99.2, type="support", source_tf="4h", touches=4),
        Level(price=95.0, type="support", source_tf="1d", touches=2),
        Level(price=104.0, type="resistance", source_tf="1d", touches=3),
        Level(price=150.0, type="resistance", source_tf="1w", touches=9),  # too far
    ]
    vp = VolumeProfileResult(symbol="SOLUSDT", bins=40, lookback=200, poc=98.0, vah=99.0, val=96.0,
                             total_volume=1.0, bin_edges=[], bin_volumes=[])
    st = StructureState(symbol="SOLUSDT", tf="4h", state=state, confidence=0.8, last_HH=101.0, last_HL=97.5)
    return _Scanner(levels=levels, vp=vp, st=st)


def test_build_one_reads_the_real_store_shapes():
    ctx = pc.build_one(_scanner(), _Store(100.0), "SOLUSDT", now=1.0)
    assert ctx["price"] == 100.0
    assert [r["price"] for r in ctx["supports"]] == [99.2, 95.0]  # nearest below first
    assert [r["price"] for r in ctx["resistances"]] == [104.0]  # 150 is beyond 12%
    assert ctx["supports"][0]["dist_pct"] == pytest.approx(-0.8)
    assert ctx["volume_profile"]["position"] == "above_value"
    assert ctx["structure_4h"]["state"] == "BULL_LEG"
    assert ctx["structure_4h"]["last_hh"] == 101.0


def test_no_price_means_no_context():
    class _Empty:
        def get_candles(self, s, tf):
            return None

    assert pc.build_one(_scanner(), _Empty(), "SOLUSDT") is None


def test_checklist_lists_both_sides_and_never_scores():
    ctx = pc.build_one(_scanner(), _Store(100.0), "SOLUSDT")
    c = pc.checklist(ctx)
    assert set(c) == {"long", "short", "neutral"}
    joined = " ".join(c["long"] + c["short"] + c["neutral"]).lower()
    for word in ("buy", "sell", "score", "%)", "confidence", "bullish", "bearish"):
        assert word not in joined
    assert any("higher highs" in x for x in c["long"])
    assert any("Support 0.8% below" in x for x in c["long"])
    assert any("Room to the next resistance: 4.0%" in x for x in c["long"])
    assert not any("Room to the next support" in x for x in c["short"])  # support is near


def test_checklist_is_mirror_symmetric():
    up = pc.checklist(pc.build_one(_scanner(state="BULL_LEG"), _Store(100.0), "S"))
    down = pc.checklist(pc.build_one(_scanner(state="BEAR_LEG"), _Store(100.0), "S"))
    assert any("higher highs" in x for x in up["long"])
    assert any("lower highs" in x for x in down["short"])
    assert not any("higher highs" in x for x in down["long"])


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

TOKENS = {
    "anon": {"uid": "anon-1", "iat": 1, "exp": 2, "firebase": {"sign_in_provider": "anonymous"}},
}


class _Engine(_StubEngine):
    def __init__(self, snap):
        super().__init__()
        self._snap = snap

    def published_pair_context(self):
        return self._snap


def _client(tmp_path, monkeypatch, snap):
    monkeypatch.setenv("FIREBASE_AUTH_ENABLED", "true")
    monkeypatch.delenv("GUEST_ACCESS_ENABLED", raising=False)
    monkeypatch.setattr(firebase_auth, "is_initialised", lambda: True)
    monkeypatch.setattr(firebase_auth, "verify_id_token", lambda t: dict(TOKENS[t]))
    now = time.time()
    record = [
        {"signal_id": "a", "symbol": "SOLUSDT", "direction": "LONG", "entry": 99.0, "pnl_pct": 1.2,
         "outcome_label": "TP1_HIT", "terminal_outcome_timestamp": now - 3600, "dispatch_timestamp": now - 7200},
        {"signal_id": "b", "symbol": "SOLUSDT", "direction": "SHORT", "entry": 101.0, "pnl_pct": -0.9,
         "outcome_label": "SL_HIT", "terminal_outcome_timestamp": now - 86400},
        {"signal_id": "c", "symbol": "ETHUSDT", "direction": "LONG", "entry": 3000, "pnl_pct": 0.5,
         "outcome_label": "TP1_HIT", "terminal_outcome_timestamp": now - 3600},
        {"signal_id": "d", "symbol": "SOLUSDT", "direction": "LONG", "entry": 90, "pnl_pct": 2.0,
         "outcome_label": "TP1_HIT", "terminal_outcome_timestamp": now - 40 * 86400},
    ]
    path = tmp_path / "signal_performance.json"
    path.write_text(json.dumps(record))
    monkeypatch.setattr(track_record, "DEFAULT_RECORD_PATH", str(path))
    track_record.reset_cache()
    store = UserStore(tmp_path / "lumin.sqlite")
    app = build_app(_Engine(snap), jwt_secret="x" * 40, allow_static=False, user_store=store)
    return TestClient(app), store


def _snap():
    ctx = pc.build_one(_scanner(), _Store(100.0), "SOLUSDT")
    return {"schema": 1, "generated_at": 123.0, "pairs": {"SOLUSDT": ctx}}


def test_route_covered_for_a_guest_gives_levels_but_locks_the_checklist(tmp_path, monkeypatch):
    client, store = _client(tmp_path, monkeypatch, _snap())
    try:
        r = client.get("/api/pairs/solusdt/context", headers={"Authorization": "Bearer anon"})
        assert r.status_code == 200
        body = r.json()
        assert body["state"] == "covered"
        assert body["context"]["supports"][0]["price"] == 99.2
        assert body["checklist"] is None and body["checklist_locked"] is True
        assert "private" in r.headers["cache-control"]
        # Only this pair's closed signals, only the last 30 days, newest first.
        assert [p["signal_id"] for p in body["past_signals"]] == ["a", "b"]
        assert body["past_signals"][0]["opened_at_ts"] is not None
    finally:
        store.close()


def test_route_owner_gets_the_checklist(tmp_path, monkeypatch):
    client, store = _client(tmp_path, monkeypatch, _snap())
    try:
        from src.api import signal_access

        monkeypatch.setattr(signal_access, "live_access",
                            lambda identity, **k: signal_access.LiveAccess(True, "owner"))
        body = client.get("/api/pairs/SOLUSDT/context", headers={"Authorization": "Bearer anon"}).json()
        assert body["checklist_locked"] is False
        assert body["checklist"]["long"]
    finally:
        store.close()


def test_route_three_states_never_two(tmp_path, monkeypatch):
    client, store = _client(tmp_path, monkeypatch, _snap())
    try:
        body = client.get("/api/pairs/PEPEUSDT/context", headers={"Authorization": "Bearer anon"}).json()
        assert body["state"] == "not_tracked" and body["context"] is None
    finally:
        store.close()
    client, store = _client(tmp_path, monkeypatch, None)
    try:
        body = client.get("/api/pairs/SOLUSDT/context", headers={"Authorization": "Bearer anon"}).json()
        assert body["state"] == "not_reported"
        assert [p["signal_id"] for p in body["past_signals"]] == ["a", "b"]  # the record still answers
    finally:
        store.close()


def test_route_refuses_a_malformed_symbol(tmp_path, monkeypatch):
    client, store = _client(tmp_path, monkeypatch, _snap())
    try:
        r = client.get("/api/pairs/SOL-USDT/context", headers={"Authorization": "Bearer anon"})
        assert r.status_code == 400
    finally:
        store.close()
