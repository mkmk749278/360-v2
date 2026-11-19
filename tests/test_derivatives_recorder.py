"""Hourly derivatives recorder (analyst spec step 2, 2026-11-19)."""
from __future__ import annotations

import sqlite3
import time
from collections import deque
from types import SimpleNamespace

from src import derivatives_recorder as D
from src import diag_catalog

NOW = 1_800_000_150.0  # 150s past an hour boundary


class FakeMarket:
    def __init__(self, premium=None, taker=None, fail=()):
        self.premium = premium
        self.taker_rows = taker or {}
        self.fail = set(fail)
        self.calls = []

    async def premium_all(self):
        self.calls.append("premium")
        return self.premium

    async def taker(self, symbol):
        self.calls.append(symbol)
        if symbol in self.fail:
            return None
        return self.taker_rows.get(symbol, [])


def _store(readings):
    oi = {s: deque([SimpleNamespace(timestamp=time.monotonic() - age, open_interest=v)])
          for s, (v, age) in readings.items()}
    return SimpleNamespace(_oi=oi)


PREM = [{"symbol": "BTCUSDT", "markPrice": "101.0", "indexPrice": "100.0",
         "lastFundingRate": "0.0001", "nextFundingTime": 1_800_028_800_000}]
TAKER = {"BTCUSDT": [{"buySellRatio": "1.2", "buyVol": "60", "sellVol": "50",
                      "timestamp": 1_799_996_400_000}]}


async def test_cycle_records_every_field_with_its_own_timestamp(tmp_path):
    rec = D.Recorder(str(tmp_path / "d.sqlite"), FakeMarket(PREM, TAKER))
    out = await rec.run_cycle(["BTCUSDT"], _store({"BTCUSDT": (5000.0, 10)}),
                              now=NOW, max_symbols=10)
    assert out["rows_written"] == 1 and out["weight_declared"] == 11
    con = sqlite3.connect(rec.path)
    con.row_factory = sqlite3.Row
    r = dict(con.execute("SELECT * FROM deriv_hourly").fetchone())
    assert r["hour_ms"] == D.hour_of(NOW) and r["oi_coin"] == 5000.0
    assert abs(r["premium_pct"] - 1.0) < 1e-9 and r["funding_rate"] == 0.0001
    assert r["taker_ratio"] == 1.2 and r["taker_bar_ms"] == 1_799_996_400_000
    assert r["oi_reason"] is None and r["premium_reason"] is None and r["taker_reason"] is None


async def test_unknowns_are_null_with_a_named_reason_never_a_value(tmp_path):
    rec = D.Recorder(str(tmp_path / "d.sqlite"), FakeMarket(None, {}, fail={"ETHUSDT"}))
    out = await rec.run_cycle(["BTCUSDT", "ETHUSDT"],
                              _store({"BTCUSDT": (5000.0, 9999)}), now=NOW, max_symbols=10)
    con = sqlite3.connect(rec.path)
    rows = {r[0]: r[1:] for r in con.execute(
        "SELECT symbol, oi_coin, oi_reason, premium_pct, premium_reason, "
        "taker_ratio, taker_reason FROM deriv_hourly")}
    assert rows["BTCUSDT"] == (None, "stale", None, "call_failed", None, "empty")
    assert rows["ETHUSDT"] == (None, "no_reading", None, "call_failed", None, "call_failed")
    assert out["premium_call_failed"] == 1 and out["taker_missing"] == 2


async def test_budget_is_spent_before_the_call_and_bounds_it(tmp_path):
    m = FakeMarket(PREM, TAKER)
    rec = D.Recorder(str(tmp_path / "d.sqlite"), m)
    out = await rec.run_cycle([f"S{i}USDT" for i in range(5)], _store({}),
                              now=NOW, max_symbols=2)
    assert m.calls == ["premium", "S0USDT", "S1USDT"]
    assert out["over_budget"] == 3 and out["rows_written"] == 2


async def test_same_hour_rewrites_rather_than_duplicates(tmp_path):
    rec = D.Recorder(str(tmp_path / "d.sqlite"), FakeMarket(PREM, TAKER))
    for _ in range(2):
        await rec.run_cycle(["BTCUSDT"], _store({"BTCUSDT": (1.0, 1)}), now=NOW, max_symbols=5)
    assert rec.stored_summary()["rows"] == 1


def test_due_waits_for_the_hour_to_settle_and_runs_once():
    rec = D.Recorder("unused")
    hour_start = D.hour_of(NOW) / 1000
    assert not rec.due(hour_start + 30)
    assert rec.due(hour_start + D.RUN_AFTER_SEC)
    rec.last_hour = D.hour_of(NOW)
    assert not rec.due(hour_start + 1800)


def test_default_off_and_off_is_healthy(monkeypatch):
    from config import DERIV_RECORDER_ENABLED
    assert DERIV_RECORDER_ENABLED is False
    monkeypatch.setattr(D, "enabled", lambda: False)
    assert D.health()[0] is True


def test_armed_but_two_hours_behind_pages(monkeypatch):
    monkeypatch.setattr(D, "enabled", lambda: True)
    rec = D.Recorder("unused")
    rec.last_hour = D.hour_of(NOW) - 2 * D.HOUR_MS
    monkeypatch.setattr(D, "_recorder", rec)
    ok, msg = D.health(now=NOW)
    assert not ok and "2 hours" in msg


def test_catalog_entry_reports_no_file_rather_than_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(D, "_recorder", D.Recorder(str(tmp_path / "none.sqlite")))
    out = diag_catalog.run("read.deriv_history", SimpleNamespace(), {})
    assert out["ok"], out
    assert out["result"]["stored"] == {"readable": False, "reason": "no_file_yet"}


def test_loop_is_launched_and_tunable_registered():
    import inspect

    from src import bootstrap, runtime_tunables
    assert "_deriv_recorder_loop()" in inspect.getsource(bootstrap)
    assert "deriv_recorder_enabled" in runtime_tunables._build_registry()
