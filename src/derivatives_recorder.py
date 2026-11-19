"""Hourly derivatives recorder — step 2 of the AI analyst spec (2026-11-19).

Binance keeps only ~30 days of open-interest, long/short and taker-ratio
history, so the analyst's crowding context cannot be back-filled later. This
records our own copy, one row per (hour, Tier-1 symbol), to SQLite:

* **open interest, coin-denominated** — read from the in-process
  ``OrderFlowStore`` that ``OIPoller`` already fills every 60s from
  ``/fapi/v1/openInterest`` (contracts = base-coin units). No new call.
* **funding, mark, index, premium** — ONE all-symbol ``/fapi/v1/premiumIndex``
  call per hour (weight 10).
* **taker buy/sell volume** — ``/futures/data/takerlongshortRatio`` per symbol
  (0 IP weight, separate 1000/5min limit; declared 1). The newest row Binance
  returns is stored with ITS OWN timestamp; we do not reinterpret it.

Request weight per cycle (once an hour): 10 + N, N = Tier-1 count (~75),
capped by ``DERIV_RECORDER_MAX_SYMBOLS``. The budget is spent at the top of
each symbol, before its call.

Off the money path: nothing here is read by scoring, dispatch or any order.
**Default OFF** (background-loop rule): the owner arms it from ops Control →
Tunables → Measurement after one watched cycle; the counter to watch is
``read.deriv_history`` → ``last_cycle``.

Every field that could not be recorded is NULL with a named reason column —
an unknown is never written as a value.
"""
from __future__ import annotations

import asyncio
import os
import sqlite3
import time
from collections import Counter
from typing import Any, Dict, Iterable, List, Optional

from src.utils import get_logger

log = get_logger("derivatives_recorder")

DEFAULT_PATH = "data/derivatives_v1.sqlite"
HOUR_MS = 3_600_000
#: Minutes past the hour before a cycle runs, so the hour's taker bar exists.
RUN_AFTER_SEC = 120
#: An OI reading older than this is not "this hour's" OI.
OI_MAX_AGE_SEC = 300.0

_SCHEMA = """
CREATE TABLE IF NOT EXISTS deriv_hourly (
    hour_ms        INTEGER NOT NULL,
    symbol         TEXT    NOT NULL,
    oi_coin        REAL,
    oi_age_s       REAL,
    oi_reason      TEXT,
    funding_rate   REAL,
    next_funding_ms INTEGER,
    mark           REAL,
    index_price    REAL,
    premium_pct    REAL,
    premium_reason TEXT,
    taker_buy_vol  REAL,
    taker_sell_vol REAL,
    taker_ratio    REAL,
    taker_bar_ms   INTEGER,
    taker_reason   TEXT,
    recorded_at    REAL    NOT NULL,
    PRIMARY KEY (hour_ms, symbol)
)
"""
_COLS = ("hour_ms", "symbol", "oi_coin", "oi_age_s", "oi_reason", "funding_rate",
         "next_funding_ms", "mark", "index_price", "premium_pct", "premium_reason",
         "taker_buy_vol", "taker_sell_vol", "taker_ratio", "taker_bar_ms",
         "taker_reason", "recorded_at")


def enabled() -> bool:
    """The arming switch — ops Control → Tunables → Measurement. Default OFF."""
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("deriv_recorder_enabled"))
    except Exception:  # noqa: BLE001
        try:
            from config import DERIV_RECORDER_ENABLED
            return bool(DERIV_RECORDER_ENABLED)
        except Exception:  # noqa: BLE001
            return False


def hour_of(now: float) -> int:
    return int(now * 1000) // HOUR_MS * HOUR_MS


def _f(v: Any) -> Optional[float]:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if x == x else None


class Market:
    """The two reads the recorder makes, through the shared futures client."""

    def __init__(self, client: Any = None) -> None:
        self._client = client

    def _c(self) -> Any:
        if self._client is None:
            from src.binance import BinanceClient
            self._client = BinanceClient("futures")
        return self._client

    async def premium_all(self) -> Optional[List[dict]]:
        return await self._c().fetch_premium_index_all()

    async def taker(self, symbol: str) -> Optional[List[dict]]:
        return await self._c().fetch_taker_ratio(symbol, "1h", 1)


class Recorder:
    def __init__(self, path: str = DEFAULT_PATH, market: Optional[Market] = None) -> None:
        self.path = path
        self.market = market or Market()
        self.counters: Counter = Counter()
        self.last_cycle: Optional[Dict[str, Any]] = None
        self.last_hour: Optional[int] = None
        self.last_error: Optional[str] = None

    # ── storage ───────────────────────────────────────────────────────────
    def _connect(self) -> sqlite3.Connection:
        d = os.path.dirname(self.path)
        if d:
            os.makedirs(d, exist_ok=True)
        con = sqlite3.connect(self.path, timeout=10)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute(_SCHEMA)
        return con

    def write_rows(self, rows: List[Dict[str, Any]]) -> int:
        if not rows:
            return 0
        con = self._connect()
        try:
            with con:
                con.executemany(
                    f"INSERT OR REPLACE INTO deriv_hourly ({','.join(_COLS)}) "
                    f"VALUES ({','.join('?' * len(_COLS))})",
                    [tuple(r.get(c) for c in _COLS) for r in rows],
                )
        finally:
            con.close()
        return len(rows)

    def stored_summary(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"readable": False, "reason": "no_file_yet"}
        con = self._connect()
        try:
            n, hours, newest = con.execute(
                "SELECT COUNT(*), COUNT(DISTINCT hour_ms), MAX(hour_ms) FROM deriv_hourly"
            ).fetchone()
            nulls = con.execute(
                "SELECT SUM(oi_coin IS NULL), SUM(premium_pct IS NULL), "
                "SUM(taker_ratio IS NULL) FROM deriv_hourly WHERE hour_ms = ?",
                (newest,),
            ).fetchone() if newest is not None else (None, None, None)
        finally:
            con.close()
        return {"readable": True, "rows": n, "hours": hours, "newest_hour_ms": newest,
                "newest_hour_nulls": {"oi": nulls[0], "premium": nulls[1],
                                      "taker": nulls[2]}}

    # ── one cycle ─────────────────────────────────────────────────────────
    async def run_cycle(self, symbols: Iterable[str], oi_store: Any, *,
                        now: Optional[float] = None,
                        max_symbols: Optional[int] = None) -> Dict[str, Any]:
        now = time.time() if now is None else now
        t0 = time.monotonic()
        hour = hour_of(now)
        syms = list(dict.fromkeys(symbols))
        if max_symbols is None:
            from config import DERIV_RECORDER_MAX_SYMBOLS as max_symbols  # type: ignore[no-redef]
        cyc: Counter = Counter()

        prem_rows = await self.market.premium_all()
        prem: Dict[str, dict] = {}
        if prem_rows is None:
            cyc["premium_call_failed"] += 1
        else:
            prem = {str(r.get("symbol")): r for r in prem_rows if isinstance(r, dict)}

        rows: List[Dict[str, Any]] = []
        budget = int(max_symbols)
        for sym in syms:
            # Budget at the TOP, before any call (hard limit).
            if budget <= 0:
                cyc["over_budget"] += 1
                continue
            budget -= 1
            row: Dict[str, Any] = {"hour_ms": hour, "symbol": sym, "recorded_at": now}

            oi, age, reason = _oi_from_store(oi_store, sym)
            row.update(oi_coin=oi, oi_age_s=age, oi_reason=reason)
            if reason:
                cyc[f"oi_{reason}"] += 1

            p = prem.get(sym)
            if p is None:
                row["premium_reason"] = ("call_failed" if prem_rows is None
                                         else "symbol_absent")
                cyc["premium_missing"] += 1
            else:
                mark, idx = _f(p.get("markPrice")), _f(p.get("indexPrice"))
                row.update(mark=mark, index_price=idx,
                           funding_rate=_f(p.get("lastFundingRate")),
                           next_funding_ms=int(_f(p.get("nextFundingTime")) or 0) or None)
                if mark and idx:
                    row["premium_pct"] = round((mark / idx - 1.0) * 100.0, 6)
                else:
                    row["premium_reason"] = "unparseable"
                    cyc["premium_missing"] += 1

            try:
                t = await self.market.taker(sym)
            except Exception as exc:  # noqa: BLE001 — one symbol must not end the cycle
                from src import fail_open
                fail_open.record("derivatives_recorder.taker", exc)
                t = None
            last = t[-1] if t else None
            if not isinstance(last, dict):
                row["taker_reason"] = "call_failed" if t is None else "empty"
                cyc["taker_missing"] += 1
            else:
                row.update(taker_buy_vol=_f(last.get("buyVol")),
                           taker_sell_vol=_f(last.get("sellVol")),
                           taker_ratio=_f(last.get("buySellRatio")),
                           taker_bar_ms=int(_f(last.get("timestamp")) or 0) or None)
            rows.append(row)

        written = await asyncio.to_thread(self.write_rows, rows)
        cyc["rows_written"] += written
        self.counters.update(cyc)
        self.counters["cycles"] += 1
        self.last_hour = hour
        self.last_cycle = {"hour_ms": hour, "at": now, "symbols": len(syms),
                           "duration_s": round(time.monotonic() - t0, 2),
                           # 10 for the all-symbol premium call + 1 per taker call
                           "weight_declared": 10 + len(rows),
                           **dict(cyc)}
        return self.last_cycle

    def due(self, now: float) -> bool:
        hour = hour_of(now)
        return self.last_hour != hour and (now * 1000 - hour) >= RUN_AFTER_SEC * 1000


def _oi_from_store(store: Any, symbol: str):
    """(oi_coin, age_s, reason). Reason is None when the value is usable."""
    snaps = getattr(store, "_oi", {}).get(symbol) if store is not None else None
    if not snaps:
        return None, None, "no_reading"
    last = snaps[-1]
    age = time.monotonic() - float(getattr(last, "timestamp", 0.0))
    oi = _f(getattr(last, "open_interest", None))
    if oi is None or oi <= 0:
        return None, round(age, 1), "unparseable"
    if age > OI_MAX_AGE_SEC:
        return None, round(age, 1), "stale"
    return oi, round(age, 1), None


_recorder: Optional[Recorder] = None


def get_recorder() -> Recorder:
    global _recorder
    if _recorder is None:
        _recorder = Recorder()
    return _recorder


def summary() -> Dict[str, Any]:
    """What ``read.deriv_history`` returns. Engine-process state."""
    r = get_recorder()
    try:
        stored = r.stored_summary()
    except Exception as exc:  # noqa: BLE001
        stored = {"readable": False, "reason": f"{type(exc).__name__}: {exc}"}
    return {"enabled": enabled(), "path": r.path, "counters": dict(r.counters),
            "last_cycle": r.last_cycle, "last_error": r.last_error, "stored": stored,
            "note": ("counters are since boot; armed from ops Control → Tunables → "
                     "Measurement (deriv_recorder_enabled)")}


def health(now: Optional[float] = None) -> "tuple[bool, str]":
    """Off is healthy. On: an hour must have been recorded in the last two."""
    if not enabled():
        return True, "disabled (default OFF; owner arms)"
    now = time.time() if now is None else now
    r = get_recorder()
    if r.last_hour is None:
        return True, "armed, no cycle yet this boot"
    behind = (hour_of(now) - r.last_hour) // HOUR_MS
    if behind >= 2:
        return False, f"last recorded hour is {behind} hours old"
    lc = r.last_cycle or {}
    if lc.get("symbols") and lc.get("rows_written", 0) == 0:
        return False, "last cycle wrote 0 rows"
    return True, f"hour recorded, {lc.get('rows_written', 0)} rows"
