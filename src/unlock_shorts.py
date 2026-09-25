"""Unlock-short dark lane — short the run-up to large insider token unlocks.

Research: ``docs/SHORTS_MARKET_RESEARCH_2026_09_25.md``. Of ten short
mechanisms pre-registered from market structure, this is the one that survived:
team and investor tokens vest on a **published** date, the holders' cost basis
is near zero, and the market leans on the price for the two weeks before. On
twelve months of Binance data the rule made +5.66% per trade after costs
(+3.83% BTC-hedged), both halves positive — and every stop tight enough for a
normal trade killed it, because the typical short first went 10.6% against.
Two squeeze filters, declared before they were run, rescued a 20% stop.

Those filters are **exploratory**. This lane exists to measure them forward, on
real prices, from the moment each fact becomes knowable — before anyone is
allowed to trade them.

What "dark" means here
----------------------
**Nothing in this module can reach a subscriber or an order.** It never touches
``signal_queue``, the router, dispatch, push, or any signed endpoint; it reads
public market data and writes one ledger file that ops renders. A test walks
this module's imports and fails if that ever changes. There is no promotion
path and no effect flag, because there is no effect: the measurement switch
(``unlock_short_lane_enabled``) is the only switch, and it defaults ON.

The row lifecycle
-----------------
``SCHEDULED``
    A qualifying unlock (insider cliff ≥ 0.5% of max supply, mapped to an
    admitted Binance USDT perp) whose entry has not come due.
``OPEN``
    Stamped at the close of T−14 (00:00 UTC of T−13): the executable price at
    stamp time, the daily close it refers to, the last settled funding, the
    14-day return into entry, BTC, and an equal-weight basket of liquid alts.
    Both filters are **stamped, never applied** — every row is walked, so ops
    can show the unfiltered rule beside the filtered one and the filters are
    measured too.
``CLOSED``
    At the close of T+2 (00:00 UTC of T+3). Results for every variant: no stop,
    20% stop, 40% stop, BTC-hedged, alt-basket-hedged — fees, slippage and the
    funding actually settled while the row was open, all charged.

Refusals are terminal and named, never folded into a result:

* ``MISSED`` — the entry came due while the lane could not stamp it (engine
  down, lane off). **No backfill.** A number reconstructed after the fact and
  filed beside recorded ones is the single most dangerous artefact this repo
  could produce (``/track-record``'s rule).
* ``LATE`` — the calendar first showed the unlock after its entry had passed.
  Counted, because how often the calendar is late is itself a fact about
  whether the rule is tradeable.
* ``REFUSED`` — the entry could not be priced honestly: no Binance price, or
  DefiLlama's price disagrees with Binance's by more than 3x (two tokens
  sharing a ticker — ``price_mismatch``).
* ``CANCELLED`` — the unlock left the calendar (moved or withdrawn) before
  entry.
* ``INSUFFICIENT`` — an open row whose bars stopped (delisting): the walk
  cannot finish, and a verdict on bars nobody saw would be invented.

Vendor budget
-------------
Public endpoints only, on the engine's shared futures rate limiter. Per 5-min
cycle the lane spends at most :data:`MAX_CALLS_PER_CYCLE` REST calls, charged at
the TOP of each item before the request — a budget that only decrements on
success is a retry storm on the path production actually takes (2026-09-01).
Typical spend: one 1h-kline call and one funding call per open row per hour,
and one all-symbol ticker (weight 40) on a cycle where an entry or exit is due.
"""
from __future__ import annotations

import asyncio
import collections
import datetime as _dt
import math
import os
import threading
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from src import fail_open, ledger_schema
from src.utils import get_logger

log = get_logger("unlock_shorts")

# --------------------------------------------------------------------------- #
# The rule (a change to any of these redefines every row: bump the schema)
# --------------------------------------------------------------------------- #

LEDGER_SCHEMA = 1
#: Older schemas whose rows this build reads unchanged. None yet.
ADDITIVE_FROM_SCHEMAS: frozenset = frozenset()

RESEARCH_DOC = "docs/SHORTS_MARKET_RESEARCH_2026_09_25.md"

MIN_FRACTION = 0.005            # insider cliff, fraction of max supply
ENTRY_DAYS_BEFORE = 14          # entry at the close of T-14
EXIT_DAYS_AFTER = 2             # exit at the close of T+2
CROWDED_FUNDING = -0.0003       # E1: skip if last settled funding <= this
RUNNING_RET_14D = 0.20          # E2: skip if the 14d return into entry > this
STOP_PCTS: Tuple[int, ...] = (20, 40)
FEE_RT_PCT = 0.07               # Binance USD-M maker in + taker out
SLIP_RT_PCT = 0.10              # 0.05% adverse per fill
COST_RT_PCT = FEE_RT_PCT + SLIP_RT_PCT
PRICE_SANITY_RATIO = 3.0        # DefiLlama vs Binance, beyond this = another token
BASKET_MIN_QUOTE_VOL = 10e6     # alt-basket constituents: 24h quote volume
BASKET_EXCLUDE = frozenset({"BTCUSDT", "ETHUSDT"})

# --------------------------------------------------------------------------- #
# Cadence and bounds
# --------------------------------------------------------------------------- #

CALENDAR_REFRESH_SEC = 20 * 3600.0
CALENDAR_RETRY_SEC = 3600.0
CALENDAR_TIMEOUT_SEC = 180.0
CALENDAR_LOOKBACK_DAYS = EXIT_DAYS_AFTER + 2
CALENDAR_HORIZON_DAYS = 60.0
WALK_EVERY_SEC = 55 * 60.0
WALK_MAX_PAGES = 5              # 99 bars each: ~20 days of catch-up per cycle
FUNDING_EVERY_SEC = 3600.0
ENTRY_GRACE_SEC = 6 * 3600.0     # an entry not stamped within this is MISSED
EXIT_PRICE_GRACE_SEC = 6 * 3600.0  # beyond this the exit uses the bar close
EXIT_WALK_GRACE_SEC = 48 * 3600.0  # bars still missing after this: INSUFFICIENT
MAX_CALLS_PER_CYCLE = 150
MAX_FUNDING_CALLS_PER_CYCLE = 60  # the funding endpoint's own limit is 500/5min/IP
STALL_BARS = 3
KEEP_TERMINAL = 3000
HOUR_MS = 3_600_000
DAY_SEC = 86400.0

# --------------------------------------------------------------------------- #
# Statuses and reasons
# --------------------------------------------------------------------------- #

S_SCHEDULED = "SCHEDULED"
S_OPEN = "OPEN"
S_CLOSED = "CLOSED"
S_MISSED = "MISSED"
S_LATE = "LATE"
S_REFUSED = "REFUSED"
S_CANCELLED = "CANCELLED"
S_INSUFFICIENT = "INSUFFICIENT"
TERMINAL = frozenset({S_CLOSED, S_MISSED, S_LATE, S_REFUSED, S_CANCELLED, S_INSUFFICIENT})

R_NO_PRICE = "no_price"
R_PRICE_MISMATCH = "price_mismatch"
R_NOT_LISTED = "not_listed"
R_CALENDAR_REMOVED = "calendar_removed"
R_WALK_INCOMPLETE = "walk_incomplete"
R_NO_BARS = "no_bars"

#: Map-time refusals. A token DefiLlama tracks that Binance does not list is
#: the ordinary case and is only counted; an admission refusal is named.
MAP_NO_PERP = "no_perp"
MAP_ADMIT_PREFIX = "admission:"

DEFAULT_PATH = "data/unlock_shorts_v1.json"


# --------------------------------------------------------------------------- #
# Switch
# --------------------------------------------------------------------------- #


def enabled() -> bool:
    """The measurement switch — ops Control → Tunables → Measurement."""
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("unlock_short_lane_enabled"))
    except Exception:  # noqa: BLE001
        try:
            from config import UNLOCK_SHORT_LANE_ENABLED
            return bool(UNLOCK_SHORT_LANE_ENABLED)
        except Exception:  # noqa: BLE001
            return False


def measure_enabled() -> bool:
    """Alias the maintenance loop gates flushes on, like every other lane."""
    return enabled()


# --------------------------------------------------------------------------- #
# Time helpers — everything is UTC
# --------------------------------------------------------------------------- #


def _day_start(ts: float) -> float:
    return math.floor(float(ts) / DAY_SEC) * DAY_SEC


def _iso(ts: Optional[float]) -> Optional[str]:
    if ts is None:
        return None
    return _dt.datetime.fromtimestamp(float(ts), tz=_dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def schedule_for(unlock_date: str) -> Tuple[float, float, float]:
    """(unlock day start, entry due, exit due) for a UTC unlock date.

    Entry is the close of T−14 — the bar that closes at 00:00 UTC of T−13.
    Exit is the close of T+2 — 00:00 UTC of T+3. The same instants the
    backtest used, so a live row and a research row measure one quantity.
    """
    day = _dt.datetime.strptime(unlock_date, "%Y-%m-%d").replace(tzinfo=_dt.timezone.utc).timestamp()
    entry_due = day - (ENTRY_DAYS_BEFORE - 1) * DAY_SEC
    exit_due = day + (EXIT_DAYS_AFTER + 1) * DAY_SEC
    return day, entry_due, exit_due


# --------------------------------------------------------------------------- #
# Symbol mapping
# --------------------------------------------------------------------------- #

#: Binance lists low-priced tokens with a multiplier prefix (1000PEPEUSDT).
PREFIXES: Tuple[Tuple[str, float], ...] = (("", 1.0), ("1000", 1000.0), ("1000000", 1e6), ("1M", 1e6))


def map_symbol(
    token_symbol: str,
    admission: Callable[[str], Tuple[bool, str]],
) -> Tuple[Optional[str], float, str]:
    """``(perp, multiplier, reason)`` — the first candidate Binance admits.

    Admission is ``symbol_filters.crypto_perp_admission``: fail-closed on
    Binance's own ``contractType``, so a TradFi perp or an unknown symbol is
    refused structurally rather than by a name list (Hard Limits).
    """
    sym = (token_symbol or "").upper().strip()
    if not sym or not sym.isalnum():
        return None, 1.0, MAP_NO_PERP
    reasons: List[str] = []
    for prefix, mult in PREFIXES:
        cand = f"{prefix}{sym}USDT"
        ok, why = admission(cand)
        if ok:
            return cand, mult, ""
        reasons.append(why)
    # Name the most informative refusal. "metadata_unavailable" outranks the
    # rest because it means we could not ask — which must never read as "not
    # listed" (absence of knowledge is not an answer).
    for important in ("metadata_unavailable", "tradfi_perp"):
        if important in reasons:
            return None, 1.0, MAP_ADMIT_PREFIX + important
    return None, 1.0, MAP_NO_PERP


# --------------------------------------------------------------------------- #
# Ledger
# --------------------------------------------------------------------------- #


class UnlockLedger:
    """Every unlock row the lane has seen, keyed ``SYMBOL:YYYY-MM-DD``."""

    def __init__(self, path: Optional[str] = None) -> None:
        self._lock = threading.Lock()
        self._path = DEFAULT_PATH if path is None else path
        self.rows: "collections.OrderedDict[str, dict]" = collections.OrderedDict()
        self.calendar: Dict[str, Any] = {}
        self.counters: collections.Counter = collections.Counter()
        self.last_cycle: Dict[str, Any] = {}
        self.last_cycle_at: Optional[float] = None
        self.evicted = 0
        self.loaded_from: Optional[str] = None
        self.load_refused: Optional[str] = None
        self._dirty = False

    # -- mutation ------------------------------------------------------------

    def upsert(self, row: dict) -> None:
        with self._lock:
            self.rows[row["row_id"]] = row
            self._dirty = True

    def mark_dirty(self) -> None:
        with self._lock:
            self._dirty = True

    def by_status(self, *statuses: str) -> List[dict]:
        with self._lock:
            return [r for r in self.rows.values() if r.get("status") in statuses]

    def all_rows(self) -> List[dict]:
        with self._lock:
            return list(self.rows.values())

    def _bound_terminal(self) -> None:
        """Keep the newest :data:`KEEP_TERMINAL` terminal rows; count the rest.

        Open and scheduled rows are never evicted — they are owed a verdict.
        """
        terminal = [r for r in self.rows.values() if r.get("status") in TERMINAL]
        excess = len(terminal) - KEEP_TERMINAL
        if excess <= 0:
            return
        terminal.sort(key=lambda r: float(r.get("entry_due_ts") or 0.0))
        for r in terminal[:excess]:
            self.rows.pop(r["row_id"], None)
        self.evicted += excess

    # -- persistence ---------------------------------------------------------

    def flush(self, force: bool = False, *, enabled_now: Optional[bool] = None) -> bool:
        """Persist on a heartbeat, dirty or not.

        An idle lane that writes nothing produces a file ops cannot tell from a
        dead one (#832/#839). ``enabled`` rides in the payload so a switched-off
        lane renders OFF rather than STALE — they have different next moves.
        """
        import json

        with self._lock:
            if not (self._dirty or force):
                return False
            self._bound_terminal()
            payload = {
                "schema": LEDGER_SCHEMA,
                "written_at": time.time(),
                "enabled": enabled() if enabled_now is None else bool(enabled_now),
                "rule": rule_manifest(),
                "calendar": dict(self.calendar),
                "counters": dict(self.counters),
                "last_cycle": dict(self.last_cycle),
                "last_cycle_at": self.last_cycle_at,
                "evicted": self.evicted,
                "load_refused": self.load_refused,
                "rows": list(self.rows.values()),
            }
            self._dirty = False
        if not self._path:
            return True  # in-memory (tests): nothing asked to be persisted
        try:
            dirname = os.path.dirname(self._path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:  # noqa: BLE001
            fail_open.record("unlock_shorts.flush", exc)
            return False

    def load(self) -> None:
        """Restore the window. Flush without load deletes it on every deploy."""
        import json

        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            ok, why = ledger_schema.accepts(
                raw.get("schema") if isinstance(raw, dict) else None,
                LEDGER_SCHEMA, ADDITIVE_FROM_SCHEMAS,
            )
            if not isinstance(raw, dict) or not ok:
                self.load_refused = why or "unreadable"
                return
            with self._lock:
                for row in raw.get("rows") or []:
                    if isinstance(row, dict) and row.get("row_id"):
                        self.rows[row["row_id"]] = row
                self.calendar = dict(raw.get("calendar") or {})
                self.evicted = int(raw.get("evicted") or 0)
            self.loaded_from = self._path
        except Exception as exc:  # noqa: BLE001
            fail_open.record("unlock_shorts.load", exc)


_ledger: Optional[UnlockLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> UnlockLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = UnlockLedger()
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[UnlockLedger] = None) -> None:
    global _ledger
    with _ledger_lock:
        _ledger = ledger


def rule_manifest() -> Dict[str, Any]:
    """The rule travels with the data. Ops renders this block; it keeps no copy."""
    return {
        "research_doc": RESEARCH_DOC,
        "min_fraction": MIN_FRACTION,
        "entry_days_before": ENTRY_DAYS_BEFORE,
        "exit_days_after": EXIT_DAYS_AFTER,
        "crowded_funding": CROWDED_FUNDING,
        "running_ret_14d": RUNNING_RET_14D,
        "stop_pcts": list(STOP_PCTS),
        "fee_rt_pct": FEE_RT_PCT,
        "slip_rt_pct": SLIP_RT_PCT,
        "basket_min_quote_vol": BASKET_MIN_QUOTE_VOL,
        "entry_grace_sec": ENTRY_GRACE_SEC,
        "max_calls_per_cycle": MAX_CALLS_PER_CYCLE,
        "stall_bars": STALL_BARS,
        # What the research measured, so ops can print it as a reference line
        # beside the forward result — labelled backtest, never pooled with it.
        "backtest": {
            "window": "2025-09-08 → 2026-08-31",
            "all_no_stop_net_pct": 5.66,
            "all_btc_hedged_net_pct": 3.83,
            "selected_stop20_net_pct": 3.23,
            "selected_alt_hedged_net_pct": 3.70,
            "note": "Selected = both filters pass. The filters were exploratory.",
        },
    }


# --------------------------------------------------------------------------- #
# Scheduling from the calendar
# --------------------------------------------------------------------------- #


def schedule_from_calendar(
    ledger: UnlockLedger,
    events: List[dict],
    *,
    now: float,
    admission: Callable[[str], Tuple[bool, str]],
    first_read: bool = False,
) -> Dict[str, int]:
    """Create, refresh or cancel rows from one calendar read.

    Only a ``SCHEDULED`` row is ever changed by the calendar. Once a row has
    been entered its facts are the ones that were true at entry; a later edit
    to the schedule must not rewrite a recorded row.
    """
    out: collections.Counter = collections.Counter()
    seen: set = set()
    could_not_map = False
    for ev in events:
        perp, mult, reason = map_symbol(str(ev.get("token_symbol") or ""), admission)
        if not perp:
            out[f"map:{reason}"] += 1
            if reason == MAP_ADMIT_PREFIX + "metadata_unavailable":
                could_not_map = True
            continue
        try:
            unlock_day, entry_due, exit_due = schedule_for(str(ev["unlock_date"]))
        except Exception:  # noqa: BLE001
            out["map:bad_date"] += 1
            continue
        row_id = f"{perp}:{ev['unlock_date']}"
        seen.add(row_id)
        facts = {
            "token_name": ev.get("token_name"),
            "token_symbol": ev.get("token_symbol"),
            "gecko_id": ev.get("gecko_id"),
            "fraction": float(ev.get("fraction") or 0.0),
            "max_supply": ev.get("max_supply"),
            "calendar_price_usd": ev.get("price_usd"),
            "allocations": list(ev.get("allocations") or [])[:12],
        }
        existing = ledger.rows.get(row_id)
        if existing is not None:
            if existing.get("status") == S_SCHEDULED:
                existing.update(facts)
                existing["calendar_seen_at"] = now
                ledger.mark_dirty()
            continue
        if exit_due <= now:
            continue  # already over: nothing to measure, nothing to record
        row = {
            "row_id": row_id,
            "symbol": perp,
            "multiplier": mult,
            "unlock_date": ev["unlock_date"],
            "unlock_ts": ev.get("unlock_ts"),
            "unlock_day_ts": unlock_day,
            "entry_due_ts": entry_due,
            "exit_due_ts": exit_due,
            "first_seen_at": now,
            "calendar_seen_at": now,
            **facts,
        }
        if entry_due + ENTRY_GRACE_SEC < now:
            row["status"] = S_LATE
            # Two causes with different meanings: on the lane's first read every
            # unlock inside the next two weeks is past its entry because the
            # LANE is new; after that, it means the CALENDAR was late.
            row["late_cause"] = "lane_start" if first_read else "calendar_late"
            row["reason"] = (
                "the lane started after this entry had passed" if first_read
                else "calendar showed the unlock after its entry had passed"
            )
            out[f"late:{row['late_cause']}"] += 1
        else:
            row["status"] = S_SCHEDULED
            out["scheduled"] += 1
        ledger.upsert(row)
    if not could_not_map:
        for row in ledger.by_status(S_SCHEDULED):
            if row["row_id"] not in seen and float(row["entry_due_ts"]) > now:
                row["status"] = S_CANCELLED
                row["reason"] = R_CALENDAR_REMOVED
                row["closed_at"] = now
                out["cancelled"] += 1
                ledger.mark_dirty()
    return dict(out)


# --------------------------------------------------------------------------- #
# Vendor access, budgeted
# --------------------------------------------------------------------------- #


class Budget:
    """Calls this cycle may still make. Spent BEFORE each request."""

    def __init__(self, calls: int = MAX_CALLS_PER_CYCLE, funding: int = MAX_FUNDING_CALLS_PER_CYCLE) -> None:
        self.calls = int(calls)
        self.funding = int(funding)
        self.exhausted = 0

    def take(self, *, funding: bool = False) -> bool:
        if self.calls <= 0 or (funding and self.funding <= 0):
            self.exhausted += 1
            return False
        self.calls -= 1
        if funding:
            self.funding -= 1
        return True


class Market:
    """The four reads the lane makes, through the engine's shared client.

    Tests substitute a fake with the same four coroutines; the real one
    wraps :class:`src.binance.BinanceClient` so the shared futures rate
    limiter prices every call.
    """

    def __init__(self, client: Any = None) -> None:
        self._client = client

    def _c(self) -> Any:
        if self._client is None:
            from src.binance import BinanceClient
            self._client = BinanceClient("futures")
        return self._client

    async def tickers(self) -> Optional[List[dict]]:
        return await self._c().fetch_all_tickers_24h()

    async def klines(self, symbol: str, interval: str, start_ms: int, limit: int = 99) -> Optional[list]:
        return await self._c().fetch_klines_since(symbol, interval, start_ms, limit)

    async def funding(self, symbol: str, start_ms: int) -> Optional[list]:
        return await self._c().fetch_funding_history(symbol, start_ms)


_market: Optional[Market] = None


def _default_market() -> Market:
    global _market
    if _market is None:
        _market = Market()
    return _market


# --------------------------------------------------------------------------- #
# Pure arithmetic
# --------------------------------------------------------------------------- #


def short_gross_pct(entry: float, exit_price: float) -> float:
    return (float(entry) - float(exit_price)) / float(entry) * 100.0


def funding_pct(events: List[List[float]], *, until_ms: Optional[float] = None) -> float:
    """Funding a SHORT receives, in %: positive rates pay the short."""
    total = 0.0
    for ts, rate in events or []:
        if until_ms is not None and float(ts) >= float(until_ms):
            continue
        total += float(rate)
    return total * 100.0


def compute_results(row: dict) -> Dict[str, Any]:
    """Every variant, from one walk. Positive = the short made money."""
    entry = float(row["entry_price"])
    exit_price = float(row["exit_price"])
    fund_all = funding_pct(row.get("funding_events") or [])
    gross = short_gross_pct(entry, exit_price)
    out: Dict[str, Any] = {
        "gross_pct": gross,
        "funding_pct": fund_all,
        "net_pct": gross + fund_all - COST_RT_PCT,
    }
    for pct in STOP_PCTS:
        hit = (row.get("stops") or {}).get(str(pct)) or {}
        if hit.get("hit_ms") is not None:
            g = short_gross_pct(entry, float(hit["fill"]))
            f = funding_pct(row.get("funding_events") or [], until_ms=float(hit["hit_ms"]) + HOUR_MS)
            out[f"stop{pct}"] = {"hit": True, "gross_pct": g, "funding_pct": f,
                                 "net_pct": g + f - COST_RT_PCT}
        else:
            out[f"stop{pct}"] = {"hit": False, "gross_pct": gross, "funding_pct": fund_all,
                                 "net_pct": out["net_pct"]}
    btc_in, btc_out = row.get("btc_entry"), row.get("btc_exit")
    if btc_in and btc_out:
        btc_ret = (float(btc_out) / float(btc_in) - 1.0) * 100.0
        btc_fund = funding_pct(row.get("btc_funding_events") or [])
        out["btc_ret_pct"] = btc_ret
        # Long BTC leg: earns BTC's return and PAYS its funding; both legs charged.
        out["btc_hedged_pct"] = out["net_pct"] + btc_ret - btc_fund - COST_RT_PCT
    else:
        out["btc_ret_pct"] = out["btc_hedged_pct"] = None
    basket_ret = row.get("basket_ret_pct")
    if basket_ret is not None:
        # Basket funding is not charged — as in the research; stated on the page.
        out["alt_hedged_pct"] = out["net_pct"] + float(basket_ret) - COST_RT_PCT
    else:
        out["alt_hedged_pct"] = None
    return out


def _ticker_map(tickers: Optional[List[dict]]) -> Dict[str, Tuple[float, float]]:
    out: Dict[str, Tuple[float, float]] = {}
    for t in tickers or []:
        try:
            out[str(t["symbol"])] = (float(t["lastPrice"]), float(t.get("quoteVolume") or 0.0))
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _bar(k: list) -> Optional[Tuple[int, float, float, float, float]]:
    try:
        return int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])
    except (IndexError, TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# The cycle
# --------------------------------------------------------------------------- #

CalendarFetcher = Callable[[float], Awaitable[Dict[str, Any]]]


async def _fetch_calendar_in_child(now: float) -> Dict[str, Any]:
    """Download + parse in a fresh interpreter; see ``unlock_calendar`` for why.

    Always returns a dict. A child that dies, hangs or prints something that is
    not JSON is a named failure, never a blank one.
    """
    import json
    import sys

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "src.unlock_calendar",
        "--min-fraction", repr(MIN_FRACTION),
        "--lookback-days", repr(CALENDAR_LOOKBACK_DAYS),
        "--horizon-days", repr(CALENDAR_HORIZON_DAYS),
        "--timeout", repr(CALENDAR_TIMEOUT_SEC - 30.0),
        "--now", repr(now),
        cwd=root,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        out, err = await asyncio.wait_for(proc.communicate(), CALENDAR_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return {"ok": False, "error": f"calendar child exceeded {int(CALENDAR_TIMEOUT_SEC)}s; killed"}
    if proc.returncode != 0:
        tail = (err or b"").decode(errors="replace").strip().splitlines()[-1:] or ["no stderr"]
        return {"ok": False, "error": f"calendar child exited {proc.returncode}: {tail[0][:300]}"}
    try:
        return json.loads(out or b"{}")
    except ValueError as exc:
        return {"ok": False, "error": f"calendar child printed non-JSON: {exc}"}


async def _refresh_calendar(
    ledger: UnlockLedger,
    now: float,
    fetcher: CalendarFetcher,
    admission: Callable[[str], Tuple[bool, str]],
    cycle: collections.Counter,
) -> None:
    cal = ledger.calendar
    last_ok = cal.get("last_ok_at")
    last_try = cal.get("last_attempt_at")
    if last_ok is not None and now - float(last_ok) < CALENDAR_REFRESH_SEC:
        return
    if last_try is not None and now - float(last_try) < CALENDAR_RETRY_SEC:
        return
    cal["last_attempt_at"] = now
    try:
        result = await fetcher(now)
    except Exception as exc:  # noqa: BLE001
        result = {"ok": False, "error": f"{type(exc).__name__}: {exc}".rstrip(": ")}
    if not result.get("ok"):
        cal["last_error"] = str(result.get("error") or "unknown")
        cal["last_error_at"] = now
        cal["failures"] = int(cal.get("failures") or 0) + 1
        ledger.counters["calendar_fail"] += 1
        cycle["calendar_fail"] += 1
        ledger.mark_dirty()
        return
    events = list(result.get("events") or [])
    changes = schedule_from_calendar(
        ledger, events, now=now, admission=admission,
        first_read=cal.get("first_ok_at") is None,
    )
    blind = int(changes.get(f"map:{MAP_ADMIT_PREFIX}metadata_unavailable") or 0)
    if blind:
        # Binance's symbol metadata was not loaded, so these events could not
        # be mapped. Counting the read as OK would wait 20h before looking
        # again; retry on the short clock instead. Absence of knowledge is not
        # "not listed".
        cal["last_error"] = f"exchange metadata unavailable: {blind} event(s) not mapped yet"
        cal["last_error_at"] = now
        cal["last_changes"] = changes
        ledger.counters["calendar_deferred"] += 1
        cycle["calendar_deferred"] += 1
        ledger.mark_dirty()
        return
    cal.setdefault("first_ok_at", now)
    cal.update({
        "last_ok_at": now,
        "source_url": result.get("source_url") or "https://defillama-datasets.llama.fi/emissionsIndex",
        "bytes": result.get("bytes"),
        "fetch_sec": result.get("fetch_sec"),
        "parse_sec": result.get("parse_sec"),
        "tokens_total": result.get("tokens_total"),
        "tokens_with_symbol": result.get("tokens_with_symbol"),
        "cliffs_seen": result.get("cliffs_seen"),
        "qualifying_events": len(events),
        "last_changes": changes,
        "failures": 0,
        "last_error": None,
    })
    ledger.counters["calendar_ok"] += 1
    cycle["calendar_ok"] += 1
    ledger.mark_dirty()


async def _stamp_entry(
    row: dict,
    now: float,
    market: Market,
    budget: Budget,
    tick: Dict[str, Tuple[float, float]],
    cycle: collections.Counter,
) -> None:
    sym = row["symbol"]
    if sym not in tick:
        row.update(status=S_REFUSED, reason=R_NO_PRICE, closed_at=now)
        cycle[f"refused:{R_NO_PRICE}"] += 1
        return
    price_now, qv = tick[sym]
    if price_now <= 0:
        row.update(status=S_REFUSED, reason=R_NO_PRICE, closed_at=now)
        cycle[f"refused:{R_NO_PRICE}"] += 1
        return
    cal_price = row.get("calendar_price_usd")
    mult = float(row.get("multiplier") or 1.0)
    if cal_price:
        ratio = float(cal_price) / (price_now / mult)
        row["price_ratio"] = ratio
        if not (1.0 / PRICE_SANITY_RATIO <= ratio <= PRICE_SANITY_RATIO):
            row.update(status=S_REFUSED, reason=R_PRICE_MISMATCH, closed_at=now)
            cycle[f"refused:{R_PRICE_MISMATCH}"] += 1
            return
        row["price_check"] = "ok"
    else:
        row["price_check"] = "unchecked"

    entry_due = float(row["entry_due_ts"])
    # Both filter inputs are fetched before anything is stamped. If the budget
    # cannot cover them, or a fetch errors, the entry waits for the next cycle
    # rather than stamping "unknown" — a transient failure of OURS would
    # otherwise become a permanent fact about the row. Past half the grace
    # window it stamps with what it has, and the unknown is named on the row.
    patient = now - entry_due < ENTRY_GRACE_SEC / 2.0
    if budget.calls < 2 or budget.funding < 1:
        if patient:
            cycle["entry_deferred:budget"] += 1
            return
    ref_close = close_14 = None
    daily = None
    if budget.take():
        cycle["calls"] += 1
        daily = await market.klines(sym, "1d", int((entry_due - 16 * DAY_SEC) * 1000), limit=20)
    fund = None
    if budget.take(funding=True):
        cycle["calls"] += 1
        fund = await market.funding(sym, int((entry_due - 3 * DAY_SEC) * 1000))
    if (daily is None or fund is None) and patient:
        cycle["entry_deferred:fetch_error"] += 1
        return
    by_open = {}
    for k in daily or []:
        b = _bar(k)
        if b:
            by_open[b[0]] = b
    ref_bar = by_open.get(int((entry_due - DAY_SEC) * 1000))
    old_bar = by_open.get(int((entry_due - 15 * DAY_SEC) * 1000))
    ref_close = ref_bar[4] if ref_bar else None
    close_14 = old_bar[4] if old_bar else None
    funding_last = funding_last_ts = None
    settled = [f for f in fund or [] if float(f.get("fundingTime") or 0) <= now * 1000]
    if settled:
        funding_last = float(settled[-1]["fundingRate"])
        funding_last_ts = float(settled[-1]["fundingTime"]) / 1000.0
    row["filter_inputs"] = {
        "daily": "ok" if daily is not None else "fetch_error",
        "funding": "ok" if fund is not None else "fetch_error",
        "ref_bar": ref_bar is not None,
        "bar_14d_ago": old_bar is not None,
        "settled_funding": bool(settled),
    }

    ret_14d = (ref_close / close_14 - 1.0) if (ref_close and close_14) else None
    crowded = None if funding_last is None else funding_last <= CROWDED_FUNDING
    running = None if ret_14d is None else ret_14d > RUNNING_RET_14D
    selected = None if (crowded is None or running is None) else (not crowded and not running)

    basket = {
        s: p for s, (p, v) in tick.items()
        if v >= BASKET_MIN_QUOTE_VOL and s not in BASKET_EXCLUDE and s != sym and p > 0
    }
    row.update(
        status=S_OPEN,
        entry_stamped_at=now,
        entry_price=price_now,
        entry_ref_close=ref_close,
        entry_drift_pct=((price_now / ref_close - 1.0) * 100.0) if ref_close else None,
        entry_quote_vol_24h=qv,
        funding_last=funding_last,
        funding_last_ts=funding_last_ts,
        ret_14d=ret_14d,
        crowded=crowded,
        running=running,
        selected=selected,
        btc_entry=(tick.get("BTCUSDT") or (None,))[0],
        basket_entry=basket,
        basket_n=len(basket),
        last_bar_open_ms=None,
        bars_seen=0,
        gap_bars=0,
        max_high=None,
        min_low=None,
        last_close=None,
        stops={},
        funding_events=[],
        last_funding_fetch_at=None,
        last_walk_at=None,
        last_advance_at=None,
        walk_misses=0,
        last_miss_reason=None,
    )
    cycle["entered"] += 1


async def _walk(row: dict, now: float, market: Market, budget: Budget, cycle: collections.Counter) -> None:
    """Advance one open row through closed 1h bars, located by open time."""
    sym = row["symbol"]
    entry = float(row["entry_price"])
    entry_due_ms = int(float(row["entry_due_ts"]) * 1000)
    exit_due_ms = int(float(row["exit_due_ts"]) * 1000)
    now_ms = int(now * 1000)
    advanced = 0
    fetched_any = False
    # Page until caught up. After downtime a row can be hundreds of bars
    # behind; one page per cycle would make its exit wait for the walk.
    for _page in range(WALK_MAX_PAGES):
        last_open = row.get("last_bar_open_ms")
        start_ms = entry_due_ms if last_open is None else int(last_open) + HOUR_MS
        if not (start_ms < exit_due_ms and start_ms + HOUR_MS <= now_ms):
            break
        if not budget.take():
            row["last_miss_reason"] = "budget"
            cycle["walk_budget"] += 1
            break
        cycle["calls"] += 1
        bars = await market.klines(sym, "1h", start_ms, limit=99)
        if bars is None:
            row["walk_misses"] = int(row.get("walk_misses") or 0) + 1
            row["last_miss_reason"] = "fetch_error"
            cycle["walk_miss:fetch_error"] += 1
            break
        fetched_any = True
        expected = start_ms
        page_advanced = 0
        for k in bars:
            b = _bar(k)
            if b is None:
                continue
            t_open, o, h, lo, c = b
            if t_open < expected:
                continue  # a bar we already consumed; never walk backwards
            if t_open >= exit_due_ms or t_open + HOUR_MS > now_ms:
                break    # after the exit, or not closed yet
            if t_open > expected:
                row["gap_bars"] = int(row.get("gap_bars") or 0) + (t_open - expected) // HOUR_MS
            row["max_high"] = h if row.get("max_high") is None else max(float(row["max_high"]), h)
            row["min_low"] = lo if row.get("min_low") is None else min(float(row["min_low"]), lo)
            for pct in STOP_PCTS:
                key = str(pct)
                if key in row["stops"]:
                    continue
                level = entry * (1.0 + pct / 100.0)
                if h >= level:
                    # Gapped through: the fill is the open, not the level.
                    row["stops"][key] = {"hit_ms": t_open, "fill": max(level, o), "level": level}
            row["last_close"] = c
            row["last_bar_open_ms"] = t_open
            expected = t_open + HOUR_MS
            page_advanced += 1
        advanced += page_advanced
        if page_advanced == 0 or len(bars) < 99:
            break
    if advanced:
        row["bars_seen"] = int(row.get("bars_seen") or 0) + advanced
        row["last_advance_at"] = now
        cycle["walk_bars"] += advanced
    elif fetched_any:
        last_open = row.get("last_bar_open_ms")
        start_ms = entry_due_ms if last_open is None else int(last_open) + HOUR_MS
        if start_ms + HOUR_MS <= now_ms - 3 * HOUR_MS:
            row["walk_misses"] = int(row.get("walk_misses") or 0) + 1
            row["last_miss_reason"] = R_NO_BARS
            cycle["walk_miss:no_bars"] += 1
    row["last_walk_at"] = now
    # Funding the row has been exposed to since it was stamped.
    last_f = row.get("last_funding_fetch_at")
    due = now >= float(row["exit_due_ts"])
    if (last_f is None or now - float(last_f) >= FUNDING_EVERY_SEC or due) and budget.take(funding=True):
        cycle["calls"] += 1
        events = row.get("funding_events") or []
        since = int(events[-1][0]) + 1 if events else int(float(row["entry_stamped_at"]) * 1000)
        fund = await market.funding(sym, since)
        if fund is not None:
            for f in fund:
                try:
                    ts, rate = int(f["fundingTime"]), float(f["fundingRate"])
                except (KeyError, TypeError, ValueError):
                    continue
                if ts <= int(float(row["entry_stamped_at"]) * 1000) or ts > exit_due_ms or ts > now_ms:
                    continue
                if events and ts <= events[-1][0]:
                    continue
                events.append([ts, rate])
            row["funding_events"] = events
            row["last_funding_fetch_at"] = now
    stamp_freshness(row, now)


def stamp_freshness(row: dict, now: float) -> None:
    """``bars_behind`` / ``stalled``, graded on this row's own walk (#835/#108)."""
    if row.get("status") != S_OPEN:
        return
    horizon_ms = min(int(now * 1000), int(float(row["exit_due_ts"]) * 1000))
    last_open = row.get("last_bar_open_ms")
    covered = int(float(row["entry_due_ts"]) * 1000) if last_open is None else int(last_open) + HOUR_MS
    behind = max(0, (horizon_ms - covered) // HOUR_MS)
    row["bars_behind"] = int(behind)
    row["stalled"] = behind >= STALL_BARS


async def _stamp_exit(
    row: dict,
    now: float,
    market: Market,
    budget: Budget,
    tick: Optional[Dict[str, Tuple[float, float]]],
    cycle: collections.Counter,
) -> None:
    exit_due = float(row["exit_due_ts"])
    exit_due_ms = int(exit_due * 1000)
    last_open = row.get("last_bar_open_ms")
    walked_to = None if last_open is None else int(last_open) + HOUR_MS
    if walked_to is None or walked_to < exit_due_ms:
        if now - exit_due > EXIT_WALK_GRACE_SEC:
            row.update(status=S_INSUFFICIENT, closed_at=now,
                       reason=R_WALK_INCOMPLETE if walked_to else R_NO_BARS)
            cycle[f"insufficient:{row['reason']}"] += 1
        return  # wait for the bars; the row stays OPEN and stamps its lag
    if tick is None and now - exit_due <= EXIT_PRICE_GRACE_SEC:
        # No board this cycle: wait for one rather than close on half the data
        # (the hedges need BTC and the basket at the same instant as the exit).
        cycle["exit_deferred:no_ticker"] += 1
        return
    sym = row["symbol"]
    exec_price = None
    if tick is not None and now - exit_due <= EXIT_PRICE_GRACE_SEC and sym in tick:
        exec_price = tick[sym][0]
    row["exit_ref_close"] = row.get("last_close")
    if exec_price and exec_price > 0:
        row["exit_price"] = exec_price
        row["exit_basis"] = "executable"
    else:
        row["exit_price"] = row.get("last_close")
        row["exit_basis"] = "bar_close"
    btc_exit = (tick.get("BTCUSDT") or (None,))[0] if tick else None
    row["btc_exit"] = btc_exit
    btc_events: List[List[float]] = []
    if btc_exit and budget.take(funding=True):
        cycle["calls"] += 1
        fund = await market.funding("BTCUSDT", int(float(row["entry_stamped_at"]) * 1000) + 1)
        for f in fund or []:
            try:
                ts, rate = int(f["fundingTime"]), float(f["fundingRate"])
            except (KeyError, TypeError, ValueError):
                continue
            if ts <= exit_due_ms:
                btc_events.append([ts, rate])
    row["btc_funding_events"] = btc_events
    basket_in = row.get("basket_entry") or {}
    if tick is not None and basket_in:
        rets = [
            tick[s][0] / float(p) - 1.0
            for s, p in basket_in.items()
            if s in tick and float(p) > 0 and tick[s][0] > 0
        ]
        row["basket_ret_pct"] = (sum(rets) / len(rets) * 100.0) if len(rets) >= 20 else None
        row["basket_n_exit"] = len(rets)
    else:
        row["basket_ret_pct"] = None
    # The entry basket is only needed to price the exit; drop it now so the
    # ledger does not carry ~150 prices per closed row forever.
    row.pop("basket_entry", None)
    try:
        row["results"] = compute_results(row)
    except Exception as exc:  # noqa: BLE001
        fail_open.record("unlock_shorts.results", exc)
        row["results"] = None
    row["status"] = S_CLOSED
    row["exit_stamped_at"] = now
    row["closed_at"] = now
    row["stalled"] = False
    cycle["closed"] += 1


async def step(
    *,
    now: Optional[float] = None,
    ledger: Optional[UnlockLedger] = None,
    market: Optional[Market] = None,
    fetch_calendar: Optional[CalendarFetcher] = None,
    admission: Optional[Callable[[str], Tuple[bool, str]]] = None,
) -> Dict[str, int]:
    """One maintenance-loop cycle. Returns this cycle's counters."""
    now = time.time() if now is None else float(now)
    ledger = get_ledger() if ledger is None else ledger
    market = _default_market() if market is None else market
    fetch_calendar = _fetch_calendar_in_child if fetch_calendar is None else fetch_calendar
    if admission is None:
        from src.execution.symbol_filters import crypto_perp_admission as admission  # noqa: N813
    cycle: collections.Counter = collections.Counter()
    budget = Budget()

    await _refresh_calendar(ledger, now, fetch_calendar, admission, cycle)

    scheduled_due = [r for r in ledger.by_status(S_SCHEDULED) if float(r["entry_due_ts"]) <= now]
    open_rows = ledger.by_status(S_OPEN)
    exits_due = [r for r in open_rows if float(r["exit_due_ts"]) <= now]

    tick: Optional[Dict[str, Tuple[float, float]]] = None
    needs_entry = [r for r in scheduled_due if now - float(r["entry_due_ts"]) <= ENTRY_GRACE_SEC]
    if (needs_entry or exits_due) and budget.take():
        cycle["calls"] += 1
        tick = _ticker_map(await market.tickers()) or None
        if tick is None:
            cycle["ticker_fail"] += 1

    for row in scheduled_due:
        if now - float(row["entry_due_ts"]) > ENTRY_GRACE_SEC:
            row.update(status=S_MISSED, closed_at=now,
                       reason=f"entry due {_iso(row['entry_due_ts'])}, not stamped within "
                              f"{int(ENTRY_GRACE_SEC // 3600)}h")
            cycle["missed"] += 1
            ledger.mark_dirty()
            continue
        if tick is None:
            continue  # try again next cycle, still inside the grace window
        await _stamp_entry(row, now, market, budget, tick, cycle)
        ledger.mark_dirty()

    for row in ledger.by_status(S_OPEN):
        due_exit = float(row["exit_due_ts"]) <= now
        last_walk = row.get("last_walk_at")
        if due_exit or last_walk is None or now - float(last_walk) >= WALK_EVERY_SEC:
            await _walk(row, now, market, budget, cycle)
            ledger.mark_dirty()
        else:
            stamp_freshness(row, now)
        if due_exit:
            await _stamp_exit(row, now, market, budget, tick, cycle)
            ledger.mark_dirty()

    cycle["budget_exhausted"] = budget.exhausted
    for k, v in cycle.items():
        ledger.counters[k] += v
    ledger.last_cycle = dict(cycle)
    ledger.last_cycle_at = now
    ledger.mark_dirty()
    return dict(cycle)


# --------------------------------------------------------------------------- #
# Health
# --------------------------------------------------------------------------- #


def health(now: Optional[float] = None, ledger: Optional[UnlockLedger] = None) -> Tuple[bool, str]:
    """Liveness predicate for ``feature_liveness``.

    Keyed on the population that would be harmed (#815): open rows that
    stopped advancing, and a calendar that stopped arriving — the one input no
    other probe in the engine watches. "Off" is healthy; it is a decision.
    """
    if not enabled():
        return True, "lane switched off"
    now = time.time() if now is None else float(now)
    ledger = get_ledger() if ledger is None else ledger
    cal = ledger.calendar
    last_ok = cal.get("last_ok_at")
    if last_ok is None:
        if cal.get("last_attempt_at") is not None:
            return False, f"calendar never read: {cal.get('last_error') or 'no error recorded'}"
        return True, "calendar not attempted yet"
    age_h = (now - float(last_ok)) / 3600.0
    if age_h > 30:
        return False, f"calendar {age_h:.0f}h old: {cal.get('last_error') or 'no error recorded'}"
    stalled = [r["row_id"] for r in ledger.by_status(S_OPEN) if r.get("stalled")]
    if stalled:
        return False, f"{len(stalled)} open row(s) stalled: {', '.join(stalled[:3])}"
    n_open = len(ledger.by_status(S_OPEN))
    n_sched = len(ledger.by_status(S_SCHEDULED))
    return True, f"{n_open} open, {n_sched} scheduled, calendar {age_h:.1f}h old"


def summary(ledger: Optional[UnlockLedger] = None) -> Dict[str, Any]:
    """Counts for the diagnostic console — the ops page reads the ledger file."""
    ledger = get_ledger() if ledger is None else ledger
    by = collections.Counter(r.get("status") for r in ledger.all_rows())
    return {
        "enabled": enabled(),
        "statuses": dict(by),
        "calendar": dict(ledger.calendar),
        "counters": dict(ledger.counters),
        "last_cycle": dict(ledger.last_cycle),
        "last_cycle_at": ledger.last_cycle_at,
        "evicted": ledger.evicted,
        "load_refused": ledger.load_refused,
    }
