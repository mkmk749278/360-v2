"""Generate the ops fixture for `/signals/unlock-shorts` from the REAL lane.

    python scripts/gen_ops_unlock_shorts_fixture.py > ../360ce-ops/tests/fixtures_unlock_shorts.json

A fixture written by hand chooses a shape and then agrees with you about it —
``zone_distance_atr`` and the price-action lane card both cost a session to
that. This drives ``src/unlock_shorts.step`` through a full lifecycle with a
fake market (only the four reads are fake) and prints the ledger exactly as
``UnlockLedger.flush`` would write it, so the ops tests read the engine's own
output. Re-run it whenever the ledger shape changes.

Rows it produces, one per state the page must render: CLOSED (filters pass,
20% stop hit), CLOSED (a filter rejects), OPEN, SCHEDULED, MISSED, LATE,
REFUSED (price_mismatch), CANCELLED.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import unlock_shorts as us  # noqa: E402

H, DAY = us.HOUR_MS, us.DAY_SEC
SYMS = {"AAAUSDT", "BBBUSDT", "CCCUSDT", "DDDUSDT", "EEEUSDT", "FFFUSDT", "GGGUSDT", "BTCUSDT"}


def _ts(s: str) -> float:
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M").replace(tzinfo=dt.timezone.utc).timestamp()


def admit(symbol):
    return (symbol in SYMS), ("" if symbol in SYMS else "unknown_to_exchange_info")


def event(sym, date, fraction=0.02, price=1.0):
    return {"token_name": sym.title(), "token_symbol": sym, "gecko_id": sym.lower(),
            "unlock_ts": _ts(f"{date} 12:00"), "unlock_date": date, "fraction": fraction,
            "max_supply": 1e9, "price_usd": price,
            "allocations": [{"recipient": "Team", "category": "insiders", "amount": fraction * 1e9}]}


class Market:
    def __init__(self):
        self.hourly, self.daily, self.fund, self.board = {}, {}, {}, {}

    async def tickers(self):
        return [{"symbol": s, "lastPrice": str(p), "quoteVolume": str(v)} for s, (p, v) in self.board.items()]

    async def klines(self, symbol, interval, start_ms, limit=99):
        src = self.hourly if interval == "1h" else self.daily
        return [[b[0], str(b[1]), str(b[2]), str(b[3]), str(b[4]), "0"]
                for b in src.get(symbol, []) if b[0] >= start_ms][:limit]

    async def funding(self, symbol, start_ms):
        return [{"fundingTime": t, "fundingRate": str(r)} for t, r in self.fund.get(symbol, []) if t >= start_ms]


def board(m, **prices):
    m.board = {"BTCUSDT": (60000.0, 5e9)}
    for i in range(25):
        m.board[f"ALT{i}USDT"] = (10.0, 20e6)
    for s, p in prices.items():
        m.board[s] = (p, 30e6)


def daily(m, sym, entry_due, ref, old):
    m.daily[sym] = [(int((entry_due - d * DAY) * 1000), c, c, c, c)
                    for d in range(16, 0, -1) for c in [old if d == 15 else ref]]


async def main():
    led = us.UnlockLedger(path="")
    m = Market()
    evs = [event("AAA", "2026-10-15"), event("BBB", "2026-10-15"), event("CCC", "2026-11-20"),
           event("DDD", "2026-12-20"), event("EEE", "2026-10-16"), event("GGG", "2026-10-17", price=5.0),
           event("FFF", "2026-12-25")]
    cal = {"evs": evs}

    async def fetch(now):
        return {"ok": True, "events": cal["evs"], "bytes": 22_200_000, "fetch_sec": 3.1,
                "parse_sec": 1.1, "tokens_total": 370, "tokens_with_symbol": 360, "cliffs_seen": 3200}

    async def step(now):
        return await us.step(now=now, ledger=led, market=m, fetch_calendar=fetch, admission=admit)

    _, e15, x15 = us.schedule_for("2026-10-15")
    _, e16, _ = us.schedule_for("2026-10-16")
    _, e17, _ = us.schedule_for("2026-10-17")
    await step(e15 - 5 * DAY)                                      # first calendar read: all scheduled
    board(m, AAAUSDT=1.0, BBBUSDT=1.0, GGGUSDT=1.0)
    daily(m, "AAAUSDT", e15, 1.0, 1.0)                              # AAA: filters pass
    daily(m, "BBBUSDT", e15, 1.0, 0.7)                              # BBB: running (+43% in 14d)
    for s in ("AAAUSDT", "BBBUSDT"):
        m.fund[s] = [(int((e15 - 8 * 3600) * 1000), 0.0001)]
    await step(e15 + 300)                                          # AAA, BBB enter
    # EEE's entry passes while the lane is "down"; GGG enters against a wrong price.
    daily(m, "GGGUSDT", e17, 1.0, 1.0)
    m.fund["GGGUSDT"] = [(int((e17 - 8 * 3600) * 1000), 0.0001)]
    board(m, AAAUSDT=1.0, BBBUSDT=1.0, GGGUSDT=1.0)
    await step(e16 + us.ENTRY_GRACE_SEC + 600)                      # EEE -> MISSED
    await step(e17 + 300)                                          # GGG -> REFUSED price_mismatch
    e_ms = int(e15 * 1000)
    n = int((x15 - e15) // 3600)
    m.hourly["AAAUSDT"] = [(e_ms + i * H, 0.95, 1.30 if i == 50 else 0.96, 0.90, 0.92) for i in range(n)]
    m.hourly["BBBUSDT"] = [(e_ms + i * H, 1.02, 1.05, 1.00, 1.03) for i in range(n)]
    m.fund["BTCUSDT"] = [(e_ms + 8 * H, 0.0001)]
    t = e15 + 300
    while t + 3600 < x15:
        t += 3600
        await step(t)
    board(m, AAAUSDT=0.92, BBBUSDT=1.03, GGGUSDT=1.0)
    await step(x15 + 300)                                          # AAA, BBB close
    # A later read drops FFF (cancelled) and shows HHH only after its entry passed.
    cal["evs"] = [e for e in evs if e["token_symbol"] != "FFF"] + [event("HHH", "2026-10-25")]
    SYMS.add("HHHUSDT")
    led.calendar["last_ok_at"] = None
    led.calendar["last_attempt_at"] = None
    await step(x15 + 400)
    # CCC (unlock 2026-11-20) enters on schedule and is walked a few hours.
    ccc_e = us.schedule_for("2026-11-20")[1]
    board(m, CCCUSDT=2.0)
    daily(m, "CCCUSDT", ccc_e, 2.0, 2.0)
    m.fund["CCCUSDT"] = [(int((ccc_e - 8 * 3600) * 1000), -0.0001)]
    await step(ccc_e + 300)
    m.hourly["CCCUSDT"] = [(int(ccc_e * 1000) + i * H, 2.0, 2.05, 1.95, 1.98) for i in range(6)]
    await step(ccc_e + 6 * 3600 + 120)
    led.flush(force=True, enabled_now=True)
    payload = {
        "schema": us.LEDGER_SCHEMA,
        "written_at": ccc_e + 6 * 3600 + 120,
        "enabled": True,
        "rule": us.rule_manifest(),
        "calendar": dict(led.calendar),
        "counters": dict(led.counters),
        "last_cycle": dict(led.last_cycle),
        "last_cycle_at": led.last_cycle_at,
        "evicted": led.evicted,
        "load_refused": led.load_refused,
        "rows": list(led.rows.values()),
    }
    json.dump(payload, sys.stdout, indent=1, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    asyncio.run(main())
