"""Unlock-short dark lane (``src/unlock_shorts.py``, ``src/unlock_calendar.py``).

Every test here drives the lane's real code. The market is faked at the four
coroutines the lane reads (tickers, klines, funding, calendar) and nowhere
else, so the walk, the stops, the funding sign, the refusals and the ledger
round trip are the production paths.
"""
from __future__ import annotations

import ast
import datetime as dt
import json
import pathlib
import subprocess
import sys

import pytest

from src import unlock_calendar as uc
from src import unlock_shorts as us

ROOT = pathlib.Path(__file__).resolve().parents[1]
H = us.HOUR_MS
DAY = us.DAY_SEC


def _ts(s: str) -> float:
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp()


def _admit_all(symbol: str):
    return (symbol in {"FOOUSDT", "1000BARUSDT", "BTCUSDT"}), ("" if symbol in {"FOOUSDT", "1000BARUSDT", "BTCUSDT"} else "unknown_to_exchange_info")


def _event(sym="FOO", date="2026-10-15", fraction=0.02, price=1.0):
    return {
        "token_name": sym.title(), "token_symbol": sym, "gecko_id": sym.lower(),
        "unlock_ts": _ts(f"{date} 12:00"), "unlock_date": date, "fraction": fraction,
        "max_supply": 1e9, "price_usd": price,
        "allocations": [{"recipient": "Team", "category": "insiders", "amount": fraction * 1e9}],
    }


class FakeMarket:
    """The four reads, answered from in-memory series."""

    def __init__(self):
        self.hourly = {}      # symbol -> list[(open_ms, o, h, l, c)]
        self.daily = {}       # symbol -> list[(open_ms, o, h, l, c)]
        self.funding_ev = {}  # symbol -> list[(ts_ms, rate)]
        self.board = {}       # symbol -> (last, quote_vol)
        self.calls = []
        self.fail_klines = False
        self.fail_funding = False

    async def tickers(self):
        self.calls.append(("tickers",))
        return [{"symbol": s, "lastPrice": str(p), "quoteVolume": str(v)} for s, (p, v) in self.board.items()]

    async def klines(self, symbol, interval, start_ms, limit=99):
        self.calls.append(("klines", symbol, interval))
        if self.fail_klines:
            return None
        src = self.hourly if interval == "1h" else self.daily
        rows = [b for b in src.get(symbol, []) if b[0] >= start_ms][:limit]
        return [[b[0], str(b[1]), str(b[2]), str(b[3]), str(b[4]), "0"] for b in rows]

    async def funding(self, symbol, start_ms):
        self.calls.append(("funding", symbol))
        if self.fail_funding:
            return None
        return [{"fundingTime": t, "fundingRate": str(r)} for t, r in self.funding_ev.get(symbol, []) if t >= start_ms]


def _calendar(events):
    async def fetch(now):
        return {"ok": True, "events": events, "bytes": 1, "tokens_total": len(events)}
    return fetch


def _board(m, foo=1.0, btc=60000.0, n_alts=30):
    m.board = {"FOOUSDT": (foo, 50e6), "BTCUSDT": (btc, 5e9)}
    for i in range(n_alts):
        m.board[f"ALT{i}USDT"] = (10.0, 20e6)


def _daily_history(m, symbol, entry_due, ref_close, close_14):
    bars = []
    for d in range(16, 0, -1):
        o = int((entry_due - d * DAY) * 1000)
        c = close_14 if d == 15 else (ref_close if d == 1 else (ref_close + close_14) / 2)
        bars.append((o, c, c, c, c))
    m.daily[symbol] = bars


# --------------------------------------------------------------------------- #
# Calendar reduction
# --------------------------------------------------------------------------- #


def _emissions(events, *, max_supply=1e9, symbol="FOO", price=1.0):
    return {"data": [{
        "name": "Foo", "gecko_id": "foo", "maxSupply": max_supply,
        "tokenPrice": [{"symbol": symbol, "price": price}],
        "unlockEvents": events,
    }]}


def test_calendar_keeps_insider_cliffs_and_drops_everything_else():
    t = _ts("2026-10-15 08:00")
    data = _emissions([
        {"timestamp": t, "cliffAllocations": [
            {"recipient": "Team", "category": "insiders", "amount": 1e7},
            {"recipient": "Seed Round", "category": "Uncategorized", "amount": 5e6},  # recipient match
            {"recipient": "Ecosystem Fund", "category": "ecosystem", "amount": 9e7},  # not insider
        ], "linearAllocations": [{"recipient": "Team", "category": "insiders"}]},
    ])
    out = uc.reduce_emissions(data, now_ts=_ts("2026-10-01 00:00"), min_fraction=0.005,
                              lookback_days=4, horizon_days=60)
    assert len(out["events"]) == 1
    ev = out["events"][0]
    assert ev["unlock_date"] == "2026-10-15"
    assert ev["fraction"] == pytest.approx(0.015)  # team + seed, never the ecosystem fund
    assert {a["recipient"] for a in ev["allocations"]} == {"Team", "Seed Round"}


def test_calendar_sums_one_day_and_applies_the_size_floor_after_summing():
    t = _ts("2026-10-15 00:00")
    data = _emissions([
        {"timestamp": t, "cliffAllocations": [{"recipient": "Team", "category": "insiders", "amount": 3e6}]},
        {"timestamp": t + 3600, "cliffAllocations": [{"recipient": "Investors", "category": "privateSale", "amount": 3e6}]},
    ])
    out = uc.reduce_emissions(data, now_ts=_ts("2026-10-01 00:00"), min_fraction=0.005,
                              lookback_days=4, horizon_days=60)
    # 0.3% + 0.3% = 0.6%: each alone is under the floor, the day is over it.
    assert [e["fraction"] for e in out["events"]] == [pytest.approx(0.006)]


def test_calendar_falls_back_to_circulating_plus_locked_for_supply():
    data = {"data": [{"name": "Foo", "gecko_id": "foo", "maxSupply": None,
                      "circSupply": 4e8, "totalLocked": 6e8,
                      "tokenPrice": [{"symbol": "FOO", "price": 1}],
                      "unlockEvents": [{"timestamp": _ts("2026-10-15 00:00"), "cliffAllocations": [
                          {"recipient": "Team", "category": "insiders", "amount": 1e7}]}]}]}
    out = uc.reduce_emissions(data, now_ts=_ts("2026-10-01 00:00"), min_fraction=0.005,
                              lookback_days=4, horizon_days=60)
    assert out["events"][0]["fraction"] == pytest.approx(0.01)


def test_calendar_window_is_bounded_both_ways():
    data = _emissions([
        {"timestamp": _ts("2026-08-01 00:00"), "cliffAllocations": [{"recipient": "Team", "category": "insiders", "amount": 1e8}]},
        {"timestamp": _ts("2027-06-01 00:00"), "cliffAllocations": [{"recipient": "Team", "category": "insiders", "amount": 1e8}]},
    ])
    out = uc.reduce_emissions(data, now_ts=_ts("2026-10-01 00:00"), min_fraction=0.005,
                              lookback_days=4, horizon_days=60)
    assert out["events"] == []


def test_calendar_failure_is_named_never_blank():
    out = uc.fetch_and_reduce("file:///nonexistent/emissions.json", timeout=5,
                              min_fraction=0.005, lookback_days=4, horizon_days=60)
    assert out["ok"] is False
    assert out["error"] and out["error"].split(":")[0]


def test_the_calendar_cli_runs_as_a_fresh_interpreter(tmp_path):
    """Drive the exact command the engine runs: `python -m src.unlock_calendar`."""
    path = tmp_path / "emissions.json"
    path.write_text(json.dumps(_emissions([
        {"timestamp": _ts("2026-10-15 00:00"), "cliffAllocations": [{"recipient": "Team", "category": "insiders", "amount": 1e8}]},
    ])))
    proc = subprocess.run(
        [sys.executable, "-m", "src.unlock_calendar", "--url", path.as_uri(),
         "--min-fraction", "0.005", "--lookback-days", "4", "--horizon-days", "60",
         "--now", str(_ts("2026-10-01 00:00"))],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert out["ok"] is True and len(out["events"]) == 1
    assert out["source_url"] == path.as_uri()


def test_the_calendar_module_imports_only_the_standard_library():
    """It runs in a fresh interpreter precisely so the engine's imports stay out."""
    tree = ast.parse((ROOT / "src" / "unlock_calendar.py").read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module.split(".")[0])
    assert mods <= {"__future__", "datetime", "json", "re", "time", "urllib", "typing", "argparse", "sys"}, mods


# --------------------------------------------------------------------------- #
# Mapping and schedule arithmetic
# --------------------------------------------------------------------------- #


def test_mapping_uses_admission_and_the_multiplier_prefix():
    assert us.map_symbol("FOO", _admit_all) == ("FOOUSDT", 1.0, "")
    assert us.map_symbol("BAR", _admit_all) == ("1000BARUSDT", 1000.0, "")
    assert us.map_symbol("NOPE", _admit_all) == (None, 1.0, us.MAP_NO_PERP)


def test_mapping_names_blindness_apart_from_not_listed():
    blind = lambda s: (False, "metadata_unavailable")  # noqa: E731
    assert us.map_symbol("FOO", blind)[2] == us.MAP_ADMIT_PREFIX + "metadata_unavailable"
    tradfi = lambda s: (False, "tradfi_perp") if s == "FOOUSDT" else (False, "unknown_to_exchange_info")  # noqa: E731
    assert us.map_symbol("FOO", tradfi)[2] == us.MAP_ADMIT_PREFIX + "tradfi_perp"


def test_schedule_matches_the_research_instants():
    """Entry at the close of T-14, exit at the close of T+2."""
    day, entry_due, exit_due = us.schedule_for("2026-10-15")
    assert entry_due == _ts("2026-10-02 00:00")  # close of Oct 1 = T-14
    assert exit_due == _ts("2026-10-18 00:00")   # close of Oct 17 = T+2


# --------------------------------------------------------------------------- #
# Scheduling from the calendar
# --------------------------------------------------------------------------- #


def test_first_read_marks_already_passed_entries_as_the_lanes_start():
    led = us.UnlockLedger(path="")
    now = _ts("2026-10-05 00:00")
    us.schedule_from_calendar(led, [_event(date="2026-10-15"), _event(sym="BAR", date="2026-10-30")],
                              now=now, admission=_admit_all, first_read=True)
    late = led.rows["FOOUSDT:2026-10-15"]
    assert late["status"] == us.S_LATE and late["late_cause"] == "lane_start"
    assert led.rows["1000BARUSDT:2026-10-30"]["status"] == us.S_SCHEDULED


def test_after_the_first_read_a_late_row_blames_the_calendar():
    led = us.UnlockLedger(path="")
    us.schedule_from_calendar(led, [_event(date="2026-10-15")], now=_ts("2026-10-05 00:00"),
                              admission=_admit_all, first_read=False)
    assert led.rows["FOOUSDT:2026-10-15"]["late_cause"] == "calendar_late"


def test_a_removed_unlock_cancels_only_while_it_is_still_scheduled():
    led = us.UnlockLedger(path="")
    now = _ts("2026-09-20 00:00")
    us.schedule_from_calendar(led, [_event(date="2026-10-15"), _event(sym="BAR", date="2026-10-20")],
                              now=now, admission=_admit_all)
    led.rows["1000BARUSDT:2026-10-20"]["status"] = us.S_OPEN  # already entered
    changes = us.schedule_from_calendar(led, [], now=now, admission=_admit_all)
    assert led.rows["FOOUSDT:2026-10-15"]["status"] == us.S_CANCELLED
    assert led.rows["1000BARUSDT:2026-10-20"]["status"] == us.S_OPEN  # a recorded row is never rewritten
    assert changes["cancelled"] == 1


def test_no_cancellation_when_the_exchange_metadata_was_missing():
    led = us.UnlockLedger(path="")
    now = _ts("2026-09-20 00:00")
    us.schedule_from_calendar(led, [_event(date="2026-10-15")], now=now, admission=_admit_all)
    blind = lambda s: (False, "metadata_unavailable")  # noqa: E731
    us.schedule_from_calendar(led, [_event(date="2026-10-15")], now=now, admission=blind)
    assert led.rows["FOOUSDT:2026-10-15"]["status"] == us.S_SCHEDULED


async def test_a_blind_calendar_read_retries_on_the_short_clock():
    led = us.UnlockLedger(path="")
    blind = lambda s: (False, "metadata_unavailable")  # noqa: E731
    now = _ts("2026-09-20 00:00")
    await us.step(now=now, ledger=led, market=FakeMarket(), fetch_calendar=_calendar([_event()]), admission=blind)
    assert led.calendar.get("last_ok_at") is None
    assert "metadata unavailable" in led.calendar["last_error"]


# --------------------------------------------------------------------------- #
# The full lifecycle, checked by hand
# --------------------------------------------------------------------------- #


async def _open_row(m, led, *, foo_now=1.0, funding_last=0.0001, ref_close=1.0, close_14=1.0):
    ev = _event(date="2026-10-15", price=1.0)
    _, entry_due, exit_due = us.schedule_for("2026-10-15")
    await us.step(now=entry_due - 10 * DAY, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    _board(m, foo=foo_now)
    _daily_history(m, "FOOUSDT", entry_due, ref_close, close_14)
    m.funding_ev["FOOUSDT"] = [(int((entry_due - 8 * 3600) * 1000), funding_last)]
    await us.step(now=entry_due + 300, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    return led.rows["FOOUSDT:2026-10-15"], entry_due, exit_due


async def test_entry_stamps_executable_price_filters_and_basket():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    row, entry_due, _ = await _open_row(m, led, foo_now=1.02, funding_last=-0.0005, ref_close=1.0, close_14=0.8)
    assert row["status"] == us.S_OPEN
    assert row["entry_price"] == pytest.approx(1.02)      # what could be traded at stamp time
    assert row["entry_ref_close"] == pytest.approx(1.0)   # the close it refers to
    assert row["entry_drift_pct"] == pytest.approx(2.0)
    assert row["ret_14d"] == pytest.approx(0.25)
    assert row["crowded"] is True and row["running"] is True and row["selected"] is False
    assert row["btc_entry"] == 60000.0
    assert row["basket_n"] == 30  # liquid alts; BTC, ETH and the token itself excluded


async def test_the_walk_stops_and_results_match_hand_arithmetic():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    row, entry_due, exit_due = await _open_row(m, led)
    e_ms = int(entry_due * 1000)
    bars = []
    n_hours = int((exit_due - entry_due) // 3600)
    for i in range(n_hours):
        o = e_ms + i * H
        if i == 30:
            bars.append((o, 1.10, 1.25, 1.05, 1.20))   # touches the 20% stop at 1.20 (not gapped)
        elif i == 31:
            bars.append((o, 1.45, 1.46, 1.30, 1.35))   # gaps through the 40% stop: fill at the open 1.45
        else:
            bars.append((o, 0.95, 0.96, 0.94, 0.95))
    bars[-1] = (bars[-1][0], 0.90, 0.91, 0.89, 0.90)
    m.hourly["FOOUSDT"] = bars
    # Funding while open: +0.01% twice (the short receives it); one after the 20% stop.
    m.funding_ev["FOOUSDT"] += [(e_ms + 8 * H, 0.0001), (e_ms + 40 * H, 0.0001)]
    m.funding_ev["BTCUSDT"] = [(e_ms + 8 * H, 0.0002)]
    # Walk hour by hour, then exit a few minutes after the close of T+2.
    t = entry_due + 300
    while t < exit_due:
        t += 3600
        await us.step(now=min(t, exit_due - 60), ledger=led, market=m, fetch_calendar=_calendar([_event()]), admission=_admit_all)
    _board(m, foo=0.90, btc=61200.0)
    for s in list(m.board):
        if s.startswith("ALT"):
            m.board[s] = (10.5, 20e6)   # basket +5%
    await us.step(now=exit_due + 300, ledger=led, market=m, fetch_calendar=_calendar([_event()]), admission=_admit_all)
    row = led.rows["FOOUSDT:2026-10-15"]
    assert row["status"] == us.S_CLOSED and row["exit_basis"] == "executable"
    r = row["results"]
    assert r["gross_pct"] == pytest.approx(10.0)                 # (1.00 - 0.90) / 1.00
    assert r["funding_pct"] == pytest.approx(0.02)               # two +0.01% settlements received
    assert r["net_pct"] == pytest.approx(10.0 + 0.02 - 0.17)
    s20 = r["stop20"]
    assert s20["hit"] and s20["gross_pct"] == pytest.approx(-20.0)
    assert s20["funding_pct"] == pytest.approx(0.01)             # only the settlement before the stop
    s40 = r["stop40"]
    assert s40["hit"] and s40["gross_pct"] == pytest.approx(-45.0)  # gapped: fill at 1.45, not 1.40
    assert r["btc_ret_pct"] == pytest.approx(2.0)
    assert r["btc_hedged_pct"] == pytest.approx(r["net_pct"] + 2.0 - 0.02 - 0.17)
    assert r["alt_hedged_pct"] == pytest.approx(r["net_pct"] + 5.0 - 0.17)
    assert "basket_entry" not in row  # dropped once it has priced the exit


async def test_an_entry_the_lane_could_not_stamp_is_missed_never_backfilled():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    ev = _event(date="2026-10-15")
    _, entry_due, _ = us.schedule_for("2026-10-15")
    await us.step(now=entry_due - 10 * DAY, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    _board(m)
    await us.step(now=entry_due + us.ENTRY_GRACE_SEC + 60, ledger=led, market=m,
                  fetch_calendar=_calendar([ev]), admission=_admit_all)
    row = led.rows["FOOUSDT:2026-10-15"]
    assert row["status"] == us.S_MISSED
    assert "entry_price" not in row


async def test_a_transient_fetch_error_defers_the_entry_instead_of_stamping_unknown():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    ev = _event(date="2026-10-15")
    _, entry_due, _ = us.schedule_for("2026-10-15")
    await us.step(now=entry_due - 10 * DAY, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    _board(m)
    _daily_history(m, "FOOUSDT", entry_due, 1.0, 1.0)
    m.fail_klines = True
    c = await us.step(now=entry_due + 300, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    assert led.rows["FOOUSDT:2026-10-15"]["status"] == us.S_SCHEDULED
    assert c["entry_deferred:fetch_error"] == 1
    # Past half the grace window it stamps with what it has — and names the gap.
    c = await us.step(now=entry_due + us.ENTRY_GRACE_SEC * 0.6, ledger=led, market=m,
                      fetch_calendar=_calendar([ev]), admission=_admit_all)
    row = led.rows["FOOUSDT:2026-10-15"]
    assert row["status"] == us.S_OPEN and row["running"] is None and row["selected"] is None
    assert row["filter_inputs"]["daily"] == "fetch_error"


async def test_a_price_from_another_token_is_refused():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    row, _, _ = await _open_row(m, led, foo_now=10.0)  # DefiLlama says ~1.0
    assert row["status"] == us.S_REFUSED and row["reason"] == us.R_PRICE_MISMATCH


async def test_a_symbol_with_no_binance_price_is_refused():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    ev = _event(date="2026-10-15")
    _, entry_due, _ = us.schedule_for("2026-10-15")
    await us.step(now=entry_due - 10 * DAY, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    m.board = {"BTCUSDT": (60000.0, 5e9)}
    await us.step(now=entry_due + 300, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    assert led.rows["FOOUSDT:2026-10-15"]["reason"] == us.R_NO_PRICE


async def test_an_exit_waits_for_the_board_then_falls_back_to_the_bar_close():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    row, entry_due, exit_due = await _open_row(m, led)
    e_ms = int(entry_due * 1000)
    m.hourly["FOOUSDT"] = [(e_ms + i * H, 0.95, 0.96, 0.94, 0.95) for i in range(int((exit_due - entry_due) // 3600))]

    async def no_board():
        return None
    m.tickers = no_board
    c = await us.step(now=exit_due + 300, ledger=led, market=m, fetch_calendar=_calendar([_event()]), admission=_admit_all)
    assert led.rows["FOOUSDT:2026-10-15"]["status"] == us.S_OPEN
    assert c["exit_deferred:no_ticker"] == 1
    await us.step(now=exit_due + us.EXIT_PRICE_GRACE_SEC + 600, ledger=led, market=m,
                  fetch_calendar=_calendar([_event()]), admission=_admit_all)
    row = led.rows["FOOUSDT:2026-10-15"]
    assert row["status"] == us.S_CLOSED and row["exit_basis"] == "bar_close"
    assert row["exit_price"] == pytest.approx(0.95)
    assert row["results"]["btc_hedged_pct"] is None  # no board, no hedge — never a guess


async def test_bars_that_never_arrive_end_insufficient_not_scored():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    row, entry_due, exit_due = await _open_row(m, led)
    m.hourly["FOOUSDT"] = []  # delisted
    await us.step(now=exit_due + us.EXIT_WALK_GRACE_SEC + 600, ledger=led, market=m,
                  fetch_calendar=_calendar([_event()]), admission=_admit_all)
    row = led.rows["FOOUSDT:2026-10-15"]
    assert row["status"] == us.S_INSUFFICIENT and "results" not in row


async def test_freshness_is_graded_on_the_rows_own_walk():
    m, led = FakeMarket(), us.UnlockLedger(path="")
    row, entry_due, _ = await _open_row(m, led)
    m.hourly["FOOUSDT"] = []
    await us.step(now=entry_due + 6 * 3600, ledger=led, market=m, fetch_calendar=_calendar([_event()]), admission=_admit_all)
    row = led.rows["FOOUSDT:2026-10-15"]
    assert row["bars_behind"] >= us.STALL_BARS and row["stalled"] is True
    ok, detail = us.health(now=entry_due + 6 * 3600, ledger=led)
    assert not ok and "stalled" in detail


# --------------------------------------------------------------------------- #
# Budget
# --------------------------------------------------------------------------- #


def test_the_budget_is_spent_before_the_call_and_counts_refusals():
    b = us.Budget(calls=2, funding=1)
    assert b.take(funding=True) and b.take()
    assert not b.take() and not b.take(funding=True)
    assert b.exhausted == 2


async def test_a_starved_budget_defers_an_entry_rather_than_stamping_unknown(monkeypatch):
    m, led = FakeMarket(), us.UnlockLedger(path="")
    ev = _event(date="2026-10-15")
    _, entry_due, _ = us.schedule_for("2026-10-15")
    await us.step(now=entry_due - 10 * DAY, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    _board(m)
    monkeypatch.setattr(us, "MAX_CALLS_PER_CYCLE", 1)  # the board call spends it
    monkeypatch.setattr(us.Budget.__init__, "__defaults__", (1, us.MAX_FUNDING_CALLS_PER_CYCLE))
    c = await us.step(now=entry_due + 300, ledger=led, market=m, fetch_calendar=_calendar([ev]), admission=_admit_all)
    assert led.rows["FOOUSDT:2026-10-15"]["status"] == us.S_SCHEDULED
    assert c["entry_deferred:budget"] == 1


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #


async def test_the_ledger_round_trips_through_the_real_serializer(tmp_path):
    path = tmp_path / "unlock_shorts_v1.json"
    m, led = FakeMarket(), us.UnlockLedger(path=str(path))
    await _open_row(m, led)
    assert led.flush(force=True, enabled_now=True)
    raw = json.loads(path.read_text())
    assert raw["schema"] == us.LEDGER_SCHEMA and raw["enabled"] is True
    assert raw["rule"]["min_fraction"] == us.MIN_FRACTION
    back = us.UnlockLedger(path=str(path))
    back.load()
    assert back.rows["FOOUSDT:2026-10-15"] == led.rows["FOOUSDT:2026-10-15"]
    assert back.calendar == led.calendar


def test_a_newer_schema_is_refused_and_named(tmp_path):
    path = tmp_path / "unlock_shorts_v1.json"
    path.write_text(json.dumps({"schema": us.LEDGER_SCHEMA + 1, "rows": [{"row_id": "X:2026-01-01"}]}))
    led = us.UnlockLedger(path=str(path))
    led.load()
    assert led.rows == {} and led.load_refused == "newer_schema"


def test_terminal_rows_are_bounded_and_the_eviction_is_counted(monkeypatch):
    monkeypatch.setattr(us, "KEEP_TERMINAL", 3)
    led = us.UnlockLedger(path="")
    for i in range(5):
        led.upsert({"row_id": f"R{i}", "status": us.S_CLOSED, "entry_due_ts": float(i)})
    led.upsert({"row_id": "OPEN", "status": us.S_OPEN, "entry_due_ts": -1.0})
    led.flush(force=True)
    assert "OPEN" in led.rows and len(led.rows) == 4 and led.evicted == 2


def test_the_in_memory_path_never_touches_the_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    us.UnlockLedger(path="").flush(force=True)
    assert list(tmp_path.iterdir()) == []


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #


def test_health_names_a_calendar_that_never_arrived(monkeypatch):
    monkeypatch.setattr(us, "enabled", lambda: True)
    led = us.UnlockLedger(path="")
    led.calendar = {"last_attempt_at": 1.0, "last_error": "HTTPError: 503"}
    ok, detail = us.health(now=10.0, ledger=led)
    assert not ok and "503" in detail


def test_health_treats_off_as_a_decision_not_a_fault(monkeypatch):
    monkeypatch.setattr(us, "enabled", lambda: False)
    assert us.health(ledger=us.UnlockLedger(path=""))[0] is True


# --------------------------------------------------------------------------- #
# Dark means dark
# --------------------------------------------------------------------------- #

MONEY_PATH = {
    "signal_queue", "signal_router", "signal_dispatch", "push_notifications",
    "telegram_bot", "order_placer", "position_fsm", "position_worker",
    "trade_monitor", "manual_take", "dark_promotion", "signing_service",
}


@pytest.mark.parametrize("module", ["unlock_shorts.py", "unlock_calendar.py"])
def test_the_lane_cannot_reach_a_subscriber_or_an_order(module):
    """Nothing here may import the money path, directly or by name."""
    tree = ast.parse((ROOT / "src" / module).read_text())
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {p for a in node.names for p in a.name.split(".")}
        elif isinstance(node, ast.ImportFrom):
            names |= set((node.module or "").split("."))
            names |= {a.name for a in node.names}
    assert not (names & MONEY_PATH), names & MONEY_PATH


def test_the_loop_is_launched_and_flushes_every_cycle():
    """A lane with no caller is the defect this repo has paid for most."""
    boot = (ROOT / "src" / "bootstrap.py").read_text()
    assert "engine._unlock_shorts_loop()" in boot
    main_src = (ROOT / "src" / "main.py").read_text()
    tree = ast.parse(main_src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == "_unlock_shorts_loop")
    body = ast.unparse(fn)
    assert "_uls.step()" in body
    assert "get_ledger().flush(force=True)" in body
    # The flush sits OUTSIDE the enabled() branch so a switched-off lane still
    # writes its heartbeat and renders OFF rather than STALE.
    loop = next(n for n in ast.walk(fn) if isinstance(n, ast.While))
    try_node = next(n for n in loop.body if isinstance(n, ast.Try))
    top_level = [ast.unparse(s) for s in try_node.body]
    assert any("flush(force=True)" in s and not s.startswith("if") for s in top_level)


def test_get_ledger_loads_before_anything_can_flush(tmp_path, monkeypatch):
    path = tmp_path / "unlock_shorts_v1.json"
    path.write_text(json.dumps({"schema": us.LEDGER_SCHEMA, "rows": [{"row_id": "KEEP:2026-01-01", "status": us.S_CLOSED}]}))
    monkeypatch.setattr(us, "DEFAULT_PATH", str(path))
    us.reset_ledger(None)
    try:
        assert "KEEP:2026-01-01" in us.get_ledger().rows
    finally:
        us.reset_ledger(None)


def test_the_new_endpoints_are_declared_before_they_can_be_called():
    from src.binance_weights import weight_for
    assert weight_for("/fapi/v1/fundingRate") == 1
    assert weight_for("/fapi/v1/klines", limit=99) == 1
    assert weight_for("/fapi/v1/ticker/24hr") == 40
