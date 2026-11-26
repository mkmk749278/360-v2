"""The Desk read model and GET /api/desk (Lumin 2.0 Phase 1a, 2026-11-26)."""
from __future__ import annotations

import json

import pytest

from src import desk as D
from src.historical_data import HistoricalDataStore

T0 = 1_700_000_000.0
NOW = T0 + 900


def _ledger(tmp_path, monkeypatch, *, plan_at=T0, bias="risk_off", setups=True):
    from src import analyst_plan as P
    led = P.Ledger(str(tmp_path / "plans.sqlite"))
    monkeypatch.setattr(P, "_ledger", led)
    con = led._connect()
    with con:
        con.execute("INSERT INTO plans (plan_id, submitted_at, bias, notes, n_setups, "
                    "n_accepted) VALUES ('p', ?, ?, 'BTC printed a fresh 4h low.', 2, 1)",
                    (plan_at, bias))
        if setups:
            con.execute(
                "INSERT INTO setups (setup_id, plan_id, idx, symbol, side, archetype,"
                " status, entries_json, stop_price, targets_json, expires_at, submitted_at,"
                " scenario, invalidation, p_target, price_at_submit, atr_1h)"
                " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                ("p:0", "p", 0, "X", "long", "breakout_retest", "accepted",
                 json.dumps([{"id": "e", "price": 99.0, "weight": 0.4},
                             {"id": "e2", "price": 98.5, "weight": 0.6}]),
                 97.0, json.dumps([{"id": "t", "price": 103.0}, {"id": "t2", "price": 105.0}]),
                 plan_at + 4 * 3600, plan_at, "Retest of the broken shelf.",
                 "1h close below 97", 0.4, 100.0, 1.0))
            con.execute(
                "INSERT INTO setups (setup_id, plan_id, idx, symbol, side, status, reason,"
                " submitted_at) VALUES ('p:1','p',1,'X','short','rejected','geometry',?)",
                (plan_at,))
    con.close()
    return led


def _engine():
    st = HistoricalDataStore()
    for i, b in enumerate([(100, 100.5, 99.5, 100), (100, 100, 98.8, 99.2),
                           (99.5, 103.5, 99.4, 103)]):
        st.update_candle("X", "5m", {"open": b[0], "high": b[1], "low": b[2], "close": b[3],
                                     "volume": 1, "open_time": (T0 + 300 * i) * 1000})
    return type("E", (), {"data_store": st})()


def test_build_reads_the_brief_setups_and_record(tmp_path, monkeypatch):
    from src import analyst_walk as W
    _ledger(tmp_path, monkeypatch)
    eng = _engine()
    W.step(eng, now=NOW)
    out = D.build(eng, now=NOW)

    assert out["schema"] == D.DESK_SCHEMA and out["ledger"] == "ok"
    plan = out["brief"]["plan"]
    assert plan["bias"] == "risk_off" and plan["notes"].startswith("BTC printed")
    assert plan["n_accepted"] == 1 and plan["accepted"][0]["archetype"] == "breakout_retest"
    assert out["brief"]["freshness"]["state"] == "current"

    # Only accepted setups are setups; the app's keys and nothing else.
    assert [s["setup_id"] for s in out["setups"]] == ["p:0"]
    s = out["setups"][0]
    assert set(s) == set(D._SETUP_KEYS)
    assert s["entries"] == [{"price": 99.0, "weight": 0.4}, {"price": 98.5, "weight": 0.6}]
    assert s["targets"] == [103.0, 105.0] and s["state"] == "tp_hit"
    assert s["scenario"] and s["invalidation"] and s["p_target"] == 0.4

    rec = out["record"]
    assert rec["readable"] and rec["basis"] == "forward_walk"
    assert "not fills" in rec["basis_note"]
    assert rec["analyst"]["n"] == 1
    assert set(out["labels"]) == {"archetype", "bias", "state"}


def test_unreadable_market_says_so_and_macro_is_never_no_events(tmp_path, monkeypatch):
    _ledger(tmp_path, monkeypatch)
    out = D.build(_engine(), now=NOW)
    mk = out["brief"]["market"]
    assert mk["readable"] is False and mk["reason"]
    assert mk["macro"] == {"readable": False, "state": "unknown"}


def test_an_old_plan_is_stale_never_this_hours_brief(tmp_path, monkeypatch):
    _ledger(tmp_path, monkeypatch, plan_at=NOW - D.BRIEF_FRESH_SEC - 60, setups=False)
    out = D.build(_engine(), now=NOW)
    assert out["brief"]["freshness"]["state"] == "stale"
    assert out["brief"]["plan"]["bias"] == "risk_off"


def test_no_ledger_yet_is_a_state_not_a_crash(tmp_path, monkeypatch):
    from src import analyst_plan as P
    monkeypatch.setattr(P, "_ledger", P.Ledger(str(tmp_path / "absent.sqlite")))
    out = D.build(_engine(), now=NOW)
    assert out["ledger"] != "ok"
    assert out["brief"]["plan"] is None and out["brief"]["freshness"]["state"] == "none"
    assert out["setups"] == [] and out["record"]["readable"] is False


def test_every_analyst_archetype_and_feed_state_has_a_label():
    from src import analyst_plan, analyst_walk
    assert set(D.ARCHETYPE_LABELS) == set(analyst_plan.ARCHETYPES)
    assert set(D.BIAS_LABELS) == set(analyst_plan.BIASES)
    assert set(D.STATE_LABELS) == set(analyst_walk.FEED_STATES)


def test_desk_is_on_the_diag_catalog(tmp_path, monkeypatch):
    from src import diag_catalog
    _ledger(tmp_path, monkeypatch)
    out = diag_catalog.run("read.desk", _engine(), {})
    assert out["ok"], out
    assert out["result"]["schema"] == D.DESK_SCHEMA


# ── the route ────────────────────────────────────────────────────────────

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

_SECRET = "desk-test-secret"


class _Facade:
    def __init__(self, payload):
        self._p = payload

    def published_desk(self):
        return self._p


def _client(engine):
    from src.api.auth import mint_token
    from src.api.server import build_app
    app = build_app(engine, jwt_secret=_SECRET, allow_static=False)
    return TestClient(app, headers={
        "Authorization": f"Bearer {mint_token(secret=_SECRET, sub='user-1')}"})


def test_route_states(tmp_path, monkeypatch):
    _ledger(tmp_path, monkeypatch)
    payload = D.build(_engine(), now=NOW)

    c = _client(_Facade(payload))
    r = c.get("/api/desk").json()
    assert r["state"] == "ok" and r["desk"]["brief"]["plan"]["bias"] == "risk_off"

    one = c.get("/api/desk/setups/p:0").json()
    assert one["state"] == "ok" and one["setup"]["symbol"] == "X"
    assert one["record"]["basis"] == "forward_walk"
    assert c.get("/api/desk/setups/nope").json()["state"] == "not_in_window"

    # Nothing published is "not reported", never an empty desk.
    assert _client(_Facade(None)).get("/api/desk").json() == {
        "state": "not_reported", "desk": None}

    from src import runtime_tunables
    real = runtime_tunables.get
    monkeypatch.setattr(runtime_tunables, "get",
                        lambda k: False if k == "desk_api_enabled" else real(k))
    assert c.get("/api/desk").json()["state"] == "disabled"


def test_route_needs_a_signed_in_caller(tmp_path, monkeypatch):
    from src.api.server import build_app
    app = build_app(_Facade({}), jwt_secret=_SECRET, allow_static=False)
    assert TestClient(app).get("/api/desk").status_code in (401, 403)


def _keys(obj, prefix=""):
    """Every dict key path in obj (lists contribute their first element)."""
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            out.add(p)
            out |= _keys(v, p)
    elif isinstance(obj, list) and obj and isinstance(obj[0], (dict, list)):
        out |= _keys(obj[0], prefix + "[]")
    return out


def test_payload_matches_the_app_contract_fixture(tmp_path, monkeypatch):
    """lumin-app reads tests/fixtures/desk_app_contract.json (a byte-identical
    copy at test/data/fixtures/desk_engine_schema1.json there). A key renamed
    or dropped here fails this test instead of quietly emptying the app's Desk.
    Additive keys are fine; regenerate both copies when DESK_SCHEMA bumps."""
    import pathlib
    from src import analyst_walk as W
    _ledger(tmp_path, monkeypatch)
    eng = _engine()
    W.step(eng, now=NOW)
    live = {"state": "ok", "desk": D.build(eng, now=NOW)}
    pinned = json.loads(pathlib.Path("tests/fixtures/desk_app_contract.json").read_text())
    assert pinned["desk"]["schema"] == D.DESK_SCHEMA
    missing = _keys(pinned) - _keys(live)
    assert not missing, f"keys the app reads are gone: {sorted(missing)}"
