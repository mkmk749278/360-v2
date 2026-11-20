"""Analyst plan: schema, validator and ledger — spec step 3 (2026-11-19).

The analyst plans; the engine executes. A plan names levels **by id** from the
engine's own menu (``analyst_snapshot.level_menu``) and never carries a price.
This module resolves those ids against the **current** menu, applies the
spec's checks in order, and records every setup — accepted or rejected, with
its reason — in a SQLite ledger.

Nothing here places, sizes, moves or cancels anything, and nothing reads this
ledger on the money path. Step 4 forward-walks the accepted setups (dark); a
limit-order executor is step 6 and needs owner sign-off.

Validator order (spec §3, step 3), first failure wins and is named:

1. ``schema``           — shape, closed sets, counts
2. ``admission``        — ``crypto_perp_admission`` (fail-closed)
3. ``not_in_universe`` / ``snapshot_unreadable`` / ``data_stale``
4. ``unknown_level``    — every id must be in the CURRENT menu
5. ``geometry``         — stop on the loss side of every entry, targets on the
                          profit side, ordered
6. ``stop_distance``    — stop (level ∓ ATR buffer) within
                          [STOP_MIN_ATR, STOP_MAX_ATR] × 1h-ATR of the
                          weighted entry
7. ``cost_floor``       — first target must clear COST_FLOOR_MULT × round trip
8. ``caps``             — one setup per symbol per plan, MAX_SETUPS per plan
9. ``unlock_veto``      — a LONG inside an insider-unlock window

Macro is **not** a veto here because no macro feed is wired; every plan is
stamped ``macro: unknown`` rather than "no events".
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

from src.utils import get_logger

log = get_logger("analyst_plan")

DEFAULT_PATH = "data/analyst_plans_v1.sqlite"
PLAN_SCHEMA = 1

ARCHETYPES = ("level_reclaim", "breakout_retest", "range_fade",
              "trend_pullback", "sweep_reversal")
SIDES = ("long", "short")
BIASES = ("risk_on", "risk_off", "neutral", "stand_aside")

MAX_SETUPS = 5
MAX_PLANS_PER_HOUR = 6
EXPIRY_HOURS = (1, 24)
#: Stop is placed this many 1h-ATRs beyond its level (beyond structure).
STOP_BUFFER_ATR = 0.1
STOP_MIN_ATR, STOP_MAX_ATR = 0.8, 2.5
#: Binance USD-M maker in + taker out, the figure /track-record uses.
ROUND_TRIP_COST_PCT = 0.07
COST_FLOOR_MULT = 3.0
#: Menu depth used to resolve ids. Wider than what the analyst is shown, so a
#: level that slid from 4th to 5th between read and submit still resolves.
MENU_DEPTH = 12
_SYMBOL_RE = re.compile(r"^[A-Z0-9]{2,20}USDT$")
_TEXT_MAX = 500

_lock = threading.Lock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS plans (
    plan_id      TEXT PRIMARY KEY,
    submitted_at REAL NOT NULL,
    source       TEXT,
    bias         TEXT,
    notes        TEXT,
    n_setups     INTEGER,
    n_accepted   INTEGER,
    macro        TEXT,
    plan_schema  INTEGER,
    raw_json     TEXT
);
CREATE TABLE IF NOT EXISTS setups (
    setup_id      TEXT PRIMARY KEY,
    plan_id       TEXT NOT NULL,
    idx           INTEGER NOT NULL,
    symbol        TEXT,
    side          TEXT,
    archetype     TEXT,
    status        TEXT NOT NULL,
    reason        TEXT,
    detail        TEXT,
    price_at_submit REAL,
    atr_1h        REAL,
    entries_json  TEXT,
    stop_level_price REAL,
    stop_price    REAL,
    targets_json  TEXT,
    stop_atr      REAL,
    tp1_pct       REAL,
    invalidation  TEXT,
    expires_at    REAL,
    submitted_at  REAL NOT NULL,
    menu_json     TEXT
);
CREATE INDEX IF NOT EXISTS setups_plan ON setups(plan_id);
CREATE INDEX IF NOT EXISTS setups_time ON setups(submitted_at);
"""


class Reject(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason, self.detail = reason, detail


# ── schema ────────────────────────────────────────────────────────────────


def _text(v: Any) -> str:
    return str(v or "")[:_TEXT_MAX]


def parse_plan(raw: Any) -> Dict[str, Any]:
    """Whole-plan shape. A bad plan is rejected entirely; a bad SETUP is
    rejected alone (see ``_parse_setup``)."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError as exc:
            raise Reject("schema", f"plan is not JSON: {exc}") from None
    if not isinstance(raw, dict):
        raise Reject("schema", "plan must be an object")
    bias = raw.get("bias")
    if bias not in BIASES:
        raise Reject("schema", f"bias must be one of {BIASES}")
    setups = raw.get("setups", [])
    if not isinstance(setups, list):
        raise Reject("schema", "setups must be a list")
    if len(setups) > MAX_SETUPS:
        raise Reject("caps", f"{len(setups)} setups > MAX_SETUPS {MAX_SETUPS}")
    return {"bias": bias, "notes": _text(raw.get("notes")), "setups": setups}


def _parse_setup(s: Any) -> Dict[str, Any]:
    if not isinstance(s, dict):
        raise Reject("schema", "setup must be an object")
    sym = str(s.get("symbol") or "").upper()
    if not _SYMBOL_RE.match(sym):
        raise Reject("schema", "symbol must look like XXXUSDT")
    if s.get("side") not in SIDES:
        raise Reject("schema", f"side must be one of {SIDES}")
    if s.get("archetype") not in ARCHETYPES:
        raise Reject("schema", f"archetype must be one of {ARCHETYPES}")
    entries = s.get("entry_level_ids")
    if not isinstance(entries, list) or not 1 <= len(entries) <= 2:
        raise Reject("schema", "entry_level_ids: one or two level ids")
    weights = s.get("tranche_weights") or ([1.0] if len(entries) == 1 else [0.4, 0.6])
    if (not isinstance(weights, list) or len(weights) != len(entries)
            or any(not isinstance(w, (int, float)) or w <= 0 for w in weights)
            or abs(sum(weights) - 1.0) > 1e-6):
        raise Reject("schema", "tranche_weights: positive, one per entry, sum to 1")
    targets = s.get("target_level_ids")
    if not isinstance(targets, list) or not 1 <= len(targets) <= 3:
        raise Reject("schema", "target_level_ids: one to three level ids")
    stop = s.get("stop_level_id")
    if not isinstance(stop, str) or not stop:
        raise Reject("schema", "stop_level_id is required")
    exp = s.get("expiry_hours", 4)
    if not isinstance(exp, (int, float)) or not EXPIRY_HOURS[0] <= exp <= EXPIRY_HOURS[1]:
        raise Reject("schema", f"expiry_hours must be in {EXPIRY_HOURS}")
    if not str(s.get("invalidation") or "").strip():
        raise Reject("schema", "invalidation is required (what would prove it wrong)")
    return {"symbol": sym, "side": s["side"], "archetype": s["archetype"],
            "entry_ids": [str(x) for x in entries], "weights": [float(w) for w in weights],
            "stop_id": stop, "target_ids": [str(x) for x in targets],
            "expiry_hours": float(exp), "invalidation": _text(s.get("invalidation"))}


# ── validation against the live engine ────────────────────────────────────


def _default_admission(symbol: str) -> Tuple[bool, str]:
    from src.execution.symbol_filters import crypto_perp_admission
    return crypto_perp_admission(symbol)


def validate_setup(raw: Any, engine: Any, *, now: float,
                   admission=_default_admission) -> Dict[str, Any]:
    """One setup → a ledger row. Never raises; a failure is a named status."""
    row: Dict[str, Any] = {"status": "rejected", "submitted_at": now}
    try:
        s = _parse_setup(raw)
        row.update(symbol=s["symbol"], side=s["side"], archetype=s["archetype"],
                   invalidation=s["invalidation"],
                   expires_at=now + s["expiry_hours"] * 3600.0)
        _check(s, engine, now, admission, row)
        row["status"] = "accepted"
    except Reject as rj:
        row.update(reason=rj.reason, detail=rj.detail)
    except Exception as exc:  # noqa: BLE001 — a defect is a named rejection
        from src import fail_open
        fail_open.record("analyst_plan.validate_setup", exc)
        row.update(reason="internal_error", detail=f"{type(exc).__name__}: {exc}")
    return row


def _check(s: Dict[str, Any], engine: Any, now: float, admission, row: Dict[str, Any]) -> None:
    from src import analyst_snapshot as A

    ok, why = admission(s["symbol"])
    if not ok:
        raise Reject("admission", why)
    universe = set(getattr(getattr(engine, "pair_mgr", None), "pairs", None) or {})
    if s["symbol"] not in universe:
        raise Reject("not_in_universe", s["symbol"])
    snap = A.pair_snapshot(engine, s["symbol"], now=now, per_side=MENU_DEPTH)
    if not snap.get("readable", True):
        raise Reject("snapshot_unreadable", str(snap.get("reason")))
    if snap.get("any_stale"):
        stale = [tf for tf, f in (snap.get("bar_freshness") or {}).items() if f.get("stale")]
        raise Reject("data_stale", ",".join(stale))
    price, atr = snap.get("price"), (snap.get("atr") or {}).get("1h")
    if not price or not atr:
        raise Reject("snapshot_unreadable", "no price or 1h ATR")
    row.update(price_at_submit=price, atr_1h=atr)
    menu = snap.get("levels") or {}
    if menu.get("refused"):
        raise Reject("snapshot_unreadable", f"menu refused: {menu['refused']}")
    by_id = {lv["id"]: lv for lv in menu.get("levels") or []}
    # The menu as it stood at submit — the fixed-rule arm (analyst_walk) picks
    # from exactly this, so the comparison is on the same opportunity.
    row["menu_json"] = json.dumps([
        {"id": lv["id"], "price": lv["price"], "side": lv["side"],
         "distance_atr": lv["distance_atr"], "score": lv["score"]}
        for lv in menu.get("levels") or []])

    def resolve(lid: str) -> float:
        lv = by_id.get(lid)
        if lv is None:
            raise Reject("unknown_level", f"{lid} is not in the current menu")
        return float(lv["price"])

    entries = [resolve(i) for i in s["entry_ids"]]
    stop_level = resolve(s["stop_id"])
    targets = [resolve(i) for i in s["target_ids"]]
    long = s["side"] == "long"
    entry = sum(p * w for p, w in zip(entries, s["weights"]))
    stop = stop_level - STOP_BUFFER_ATR * atr if long else stop_level + STOP_BUFFER_ATR * atr
    row.update(entries_json=json.dumps([{"id": i, "price": p, "weight": w} for i, p, w
                                        in zip(s["entry_ids"], entries, s["weights"])]),
               stop_level_price=stop_level, stop_price=round(stop, 10),
               targets_json=json.dumps([{"id": i, "price": p}
                                        for i, p in zip(s["target_ids"], targets)]))

    sign = 1.0 if long else -1.0
    if any(sign * (e - stop_level) <= 0 for e in entries):
        raise Reject("geometry", "stop level is not on the loss side of every entry")
    edge = max(entries) if long else min(entries)
    if any(sign * (t - edge) <= 0 for t in targets):
        raise Reject("geometry", "every target must be on the profit side of every entry")
    if [sign * t for t in targets] != sorted(sign * t for t in targets):
        raise Reject("geometry", "targets must be ordered nearest first")

    stop_atr = abs(entry - stop) / atr
    row["stop_atr"] = round(stop_atr, 4)
    if not STOP_MIN_ATR <= stop_atr <= STOP_MAX_ATR:
        raise Reject("stop_distance",
                     f"{stop_atr:.2f} x 1h-ATR outside [{STOP_MIN_ATR}, {STOP_MAX_ATR}]")
    tp1_pct = abs(targets[0] - entry) / entry * 100.0
    row["tp1_pct"] = round(tp1_pct, 4)
    floor = COST_FLOOR_MULT * ROUND_TRIP_COST_PCT
    if tp1_pct < floor:
        raise Reject("cost_floor", f"TP1 {tp1_pct:.3f}% < {floor:.3f}%")

    unl = snap.get("unlocks") or {}
    if long and unl.get("events"):
        raise Reject("unlock_veto", json.dumps(unl["events"][:3]))


def validate_plan(raw: Any, engine: Any, *, now: Optional[float] = None,
                  admission=_default_admission) -> Dict[str, Any]:
    now = time.time() if now is None else now
    plan = parse_plan(raw)  # raises Reject for a malformed plan
    rows: List[Dict[str, Any]] = []
    seen: set = set()
    for i, raw_s in enumerate(plan["setups"]):
        row = validate_setup(raw_s, engine, now=now, admission=admission)
        sym = row.get("symbol")
        if row["status"] == "accepted" and sym in seen:
            row.update(status="rejected", reason="caps", detail="one setup per symbol per plan")
        if sym:
            seen.add(sym)
        row["idx"] = i
        rows.append(row)
    return {"plan": plan, "setups": rows}


# ── ledger ────────────────────────────────────────────────────────────────


class Ledger:
    def __init__(self, path: str = DEFAULT_PATH) -> None:
        self.path = path

    def _connect(self) -> sqlite3.Connection:
        d = os.path.dirname(self.path)
        if d:
            os.makedirs(d, exist_ok=True)
        con = sqlite3.connect(self.path, timeout=10)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode=WAL")
        con.executescript(_SCHEMA)
        # Additive migration: a ledger created before menu_json existed gains
        # the column; its old rows read NULL ("no_menu_stamped"), never a guess.
        cols = {r[1] for r in con.execute("PRAGMA table_info(setups)")}
        if "menu_json" not in cols:
            con.execute("ALTER TABLE setups ADD COLUMN menu_json TEXT")
        return con

    def plans_since(self, since: float) -> int:
        if not os.path.exists(self.path):
            return 0
        con = self._connect()
        try:
            return int(con.execute("SELECT COUNT(*) FROM plans WHERE submitted_at >= ?",
                                   (since,)).fetchone()[0])
        finally:
            con.close()

    def record(self, plan_id: str, now: float, source: str, result: Dict[str, Any],
               raw: Any) -> None:
        plan, rows = result["plan"], result["setups"]
        con = self._connect()
        try:
            with con:
                con.execute(
                    "INSERT INTO plans VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (plan_id, now, source, plan["bias"], plan["notes"], len(rows),
                     sum(r["status"] == "accepted" for r in rows), "unknown",
                     PLAN_SCHEMA, json.dumps(raw, default=str)[:20000]))
                for r in rows:
                    con.execute(
                        "INSERT INTO setups VALUES "
                        "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                        (f"{plan_id}:{r['idx']}", plan_id, r["idx"], r.get("symbol"),
                         r.get("side"), r.get("archetype"), r["status"], r.get("reason"),
                         r.get("detail"), r.get("price_at_submit"), r.get("atr_1h"),
                         r.get("entries_json"), r.get("stop_level_price"),
                         r.get("stop_price"), r.get("targets_json"), r.get("stop_atr"),
                         r.get("tp1_pct"), r.get("invalidation"), r.get("expires_at"),
                         r["submitted_at"], r.get("menu_json")))
        finally:
            con.close()

    def recent(self, limit: int = 5) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"readable": False, "reason": "no_file_yet", "plans": []}
        con = self._connect()
        try:
            plans = [dict(r) for r in con.execute(
                "SELECT plan_id, submitted_at, source, bias, notes, n_setups, n_accepted, "
                "macro FROM plans ORDER BY submitted_at DESC LIMIT ?", (int(limit),))]
            for p in plans:
                p["setups"] = [dict(r) for r in con.execute(
                    "SELECT idx, symbol, side, archetype, status, reason, detail, "
                    "price_at_submit, stop_price, stop_atr, tp1_pct, entries_json, "
                    "targets_json, expires_at FROM setups WHERE plan_id = ? ORDER BY idx",
                    (p["plan_id"],))]
            totals = dict(con.execute(
                "SELECT COUNT(*) AS setups, SUM(status='accepted') AS accepted "
                "FROM setups").fetchone())
            reasons = {r[0]: r[1] for r in con.execute(
                "SELECT reason, COUNT(*) FROM setups WHERE status='rejected' "
                "GROUP BY reason")}
        finally:
            con.close()
        return {"readable": True, "plans": plans, "totals": totals,
                "rejections_by_reason": reasons}


_ledger: Optional[Ledger] = None


def get_ledger() -> Ledger:
    global _ledger
    if _ledger is None:
        _ledger = Ledger()
    return _ledger


def submit(raw: Any, engine: Any, *, source: str = "unknown",
           now: Optional[float] = None, admission=_default_admission) -> Dict[str, Any]:
    """Validate and record one plan. The return is what the analyst reads back."""
    now = time.time() if now is None else now
    led = get_ledger()
    with _lock:
        if led.plans_since(now - 3600.0) >= MAX_PLANS_PER_HOUR:
            return {"accepted": False, "reason": "rate_limited",
                    "detail": f"more than {MAX_PLANS_PER_HOUR} plans in the last hour"}
        try:
            result = validate_plan(raw, engine, now=now, admission=admission)
        except Reject as rj:
            return {"accepted": False, "reason": rj.reason, "detail": rj.detail}
        plan_id = f"p_{int(now)}_{uuid.uuid4().hex[:6]}"
        led.record(plan_id, now, _text(source)[:40], result, raw)
    rows = result["setups"]
    return {
        "accepted": True, "plan_id": plan_id, "macro": "unknown — no macro feed is wired",
        "setups": [{k: r.get(k) for k in ("idx", "symbol", "side", "status", "reason",
                                           "detail", "stop_price", "stop_atr", "tp1_pct")}
                   for r in rows],
        "n_accepted": sum(r["status"] == "accepted" for r in rows),
        "note": "Recorded and measured dark. Nothing here reaches a subscriber or an order.",
    }
