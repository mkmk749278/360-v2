"""The pair book: what the analyst knows about each coin, kept between runs.

Plan: ``docs/ANALYST_DESK_PLAN_2026_11_28.md`` Phases 1d and 1e. The analyst
starts every hour from zero. A trader does not: they remember the levels they
marked on a coin and what price did there, and what they were waiting for.

Four parts, all in the analyst's SQLite ledger:

* **Level marks** (engine-recorded facts). Every entry, stop and target of
  an accepted setup becomes a mark. :func:`classify_marks` walks closed 5m
  bars after the mark and classifies how price treated it:
  * ``respected`` — touched and held;
  * ``broke`` — closed beyond it and stayed;
  * ``swept_reclaimed`` — traded through, then closed back;
  * ``untested`` — not reached within the horizon.
* **Notes** (the analyst's hypotheses). An optional ``pair_notes`` block in a
  plan: thesis, levels, what it is waiting for. Stored labelled as
  hypothesis, never as fact.
* **Reads** (Phase 1e). Which per-coin reads (image, flow, profile, book) the
  analyst made before a setup, so the split can later say whether looking
  helped.
* **Profile stamps** (Phase 1e). The coin's beta, decoupling, wick share and
  behaviour at submit, so a later split can ask whether e.g. high-beta
  shorts paid.

Read-only toward the money path: nothing here reaches a subscriber, signal or
order.
"""
from __future__ import annotations

import json
import re
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_SYMBOL_RE = re.compile(r"^[A-Z0-9]{2,20}USDT$")
MAX_NOTES_PER_PLAN = 6
NOTE_MAX = 300
#: How long a mark is watched before it is called untested.
MARK_HORIZON_S = 48 * 3600
#: Bars after a touch in which a close back on the original side counts as a
#: sweep-and-reclaim rather than a break.
RECLAIM_BARS = 3
#: A wick beyond the level by less than this (fraction of the 1h ATR) is a
#: touch, not a trade-through.
TOUCH_TOL_ATR = 0.1
MARK_TF = "5m"
MARK_TF_MS = 300_000
CLASSIFY_PER_STEP = 400
#: A read made this long before a submit counts as informing it.
READ_WINDOW_S = 1800
READ_KINDS = ("image", "flow", "profile", "book", "chart")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS level_marks (
    mark_id     TEXT PRIMARY KEY,
    setup_id    TEXT NOT NULL,
    symbol      TEXT NOT NULL,
    side        TEXT,
    kind        TEXT NOT NULL,
    price       REAL NOT NULL,
    above       INTEGER NOT NULL,
    tol         REAL NOT NULL,
    marked_at   REAL NOT NULL,
    status      TEXT NOT NULL DEFAULT 'pending',
    touched_at  REAL,
    resolved_at REAL,
    max_beyond_pct REAL
);
CREATE INDEX IF NOT EXISTS level_marks_symbol ON level_marks(symbol, marked_at);
CREATE INDEX IF NOT EXISTS level_marks_open ON level_marks(status);
CREATE TABLE IF NOT EXISTS pair_notes (
    plan_id      TEXT NOT NULL,
    symbol       TEXT NOT NULL,
    submitted_at REAL NOT NULL,
    note         TEXT NOT NULL,
    price_at_note REAL,
    PRIMARY KEY (plan_id, symbol)
);
CREATE INDEX IF NOT EXISTS pair_notes_symbol ON pair_notes(symbol, submitted_at);
"""

MARK_STATES = ("pending", "respected", "broke", "swept_reclaimed", "untested",
               "insufficient")

# ── reads (Phase 1e) ────────────────────────────────────────────────────────

_reads: Dict[Tuple[str, str], float] = {}
_reads_lock = threading.Lock()


def note_read(symbol: str, kind: str, *, now: Optional[float] = None) -> None:
    """Record that the analyst read *kind* for *symbol*. In-memory, bounded."""
    if kind not in READ_KINDS or not symbol:
        return
    with _reads_lock:
        if len(_reads) > 5000:
            _reads.clear()
        _reads[(symbol.upper(), kind)] = time.time() if now is None else now


def reads_for(symbol: str, now: float) -> Dict[str, bool]:
    with _reads_lock:
        return {k: (now - _reads.get((symbol.upper(), k), -1e18)) <= READ_WINDOW_S
                for k in READ_KINDS}


def profile_stamp(engine: Any, symbol: str) -> Dict[str, Any]:
    """The profile values a later split will ask about, frozen at submit."""
    from src import analyst_profile

    p = analyst_profile.pair_profile(engine, symbol)
    if not p.get("readable"):
        return {"readable": False, "reason": p.get("reason")}
    btc = p.get("btc") or {}
    vol = p.get("volatility") or {}
    ch = p.get("character") or {}
    return {
        "readable": True,
        "beta_1h": (btc.get("1h") or {}).get("beta"),
        "beta_4h_btc_down": (btc.get("4h_btc_down_bars") or {}).get("beta"),
        "beta_4h_btc_up": (btc.get("4h_btc_up_bars") or {}).get("beta"),
        "corr_48h": (btc.get("now_48h") or {}).get("corr"),
        "decoupled_now": btc.get("decoupled_now"),
        "wick_share_1h": vol.get("wick_share_median_1h"),
        "daily_range_pctl_90d": vol.get("daily_range_percentile_90d"),
        "behaviour": ch.get("behaviour"),
        "variance_ratio_4": ch.get("variance_ratio_4"),
    }


# ── notes ───────────────────────────────────────────────────────────────────


def parse_notes(raw: Any) -> Tuple[Dict[str, str], List[str]]:
    """``{SYMBOL: note}`` and the keys dropped, by name. Never rejects a plan."""
    if raw is None:
        return {}, []
    if not isinstance(raw, dict):
        return {}, ["pair_notes must be an object of SYMBOL: text"]
    kept: Dict[str, str] = {}
    dropped: List[str] = []
    for k, v in raw.items():
        sym = str(k).upper()
        if not _SYMBOL_RE.match(sym):
            dropped.append(f"{k}: not a USDT symbol")
            continue
        if not isinstance(v, str) or not v.strip():
            dropped.append(f"{k}: empty note")
            continue
        if len(kept) >= MAX_NOTES_PER_PLAN:
            dropped.append(f"{k}: more than {MAX_NOTES_PER_PLAN} notes")
            continue
        kept[sym] = " ".join(v.split())[:NOTE_MAX]
    return kept, dropped


def ensure_schema(con: sqlite3.Connection) -> None:
    con.executescript(_SCHEMA)


def record_notes(con: sqlite3.Connection, plan_id: str, now: float,
                 notes: Dict[str, str], prices: Dict[str, Optional[float]]) -> int:
    ensure_schema(con)
    for sym, text in notes.items():
        con.execute("INSERT OR REPLACE INTO pair_notes (plan_id, symbol, submitted_at, "
                    "note, price_at_note) VALUES (?,?,?,?,?)",
                    (plan_id, sym, now, text, prices.get(sym)))
    return len(notes)


# ── level marks ─────────────────────────────────────────────────────────────


def sync_marks(con: sqlite3.Connection, limit: int = 500) -> int:
    """Create marks for accepted setups that have none yet. Idempotent."""
    ensure_schema(con)
    rows = [dict(r) for r in con.execute(
        "SELECT s.setup_id, s.symbol, s.side, s.entries_json, s.stop_price, "
        "s.targets_json, s.price_at_submit, s.atr_1h, s.submitted_at FROM setups s "
        "WHERE s.status='accepted' AND NOT EXISTS (SELECT 1 FROM level_marks m "
        "WHERE m.setup_id = s.setup_id) ORDER BY s.submitted_at LIMIT ?", (int(limit),))]
    n = 0
    for s in rows:
        px = s.get("price_at_submit")
        if not px or px <= 0:
            continue
        atr = s.get("atr_1h") or 0.0
        tol = max(float(atr) * TOUCH_TOL_ATR, float(px) * 0.0005)
        levels: List[Tuple[str, float]] = []
        try:
            levels += [(f"entry{i}", float(e["price"]))
                       for i, e in enumerate(json.loads(s.get("entries_json") or "[]"))]
            levels += [(f"target{i}", float(t["price"]))
                       for i, t in enumerate(json.loads(s.get("targets_json") or "[]"))]
        except (ValueError, KeyError, TypeError):
            pass
        if s.get("stop_price"):
            levels.append(("stop", float(s["stop_price"])))
        for kind, price in levels:
            if price <= 0:
                continue
            con.execute(
                "INSERT OR IGNORE INTO level_marks (mark_id, setup_id, symbol, side, kind, "
                "price, above, tol, marked_at) VALUES (?,?,?,?,?,?,?,?,?)",
                (f"{s['setup_id']}:{kind}", s["setup_id"], s["symbol"], s["side"], kind,
                 price, int(price > px), tol, float(s["submitted_at"])))
            n += 1
    return n


def classify(above: bool, price: float, tol: float, times: np.ndarray, high: np.ndarray,
             low: np.ndarray, close: np.ndarray) -> Optional[Dict[str, Any]]:
    """How price treated one level, from closed bars after the mark. Pure.

    ``above``: the level sat above price when marked (resistance). Returns
    None while undecided: not yet touched, or touched with fewer than
    ``RECLAIM_BARS`` closed bars after the touch.
    """
    if len(close) == 0:
        return None
    reach = high >= price - tol if above else low <= price + tol
    idx = np.flatnonzero(reach)
    if len(idx) == 0:
        return None
    i = int(idx[0])
    after = close[i:i + 1 + RECLAIM_BARS]
    if len(after) < 1 + RECLAIM_BARS:
        return None
    window_h, window_l = high[i:i + 1 + RECLAIM_BARS], low[i:i + 1 + RECLAIM_BARS]
    if above:
        beyond = float(window_h.max() - price)
        closed_beyond = after > price + tol
    else:
        beyond = float(price - window_l.min())
        closed_beyond = after < price - tol
    out = {"touched_at": float(times[i]) / 1000.0,
           "max_beyond_pct": round(max(beyond, 0.0) / price * 100, 4)}
    if closed_beyond[-1]:
        status = "broke"
    elif beyond > tol:
        status = "swept_reclaimed"
    else:
        status = "respected"
    out["status"] = status
    out["resolved_at"] = float(times[i + RECLAIM_BARS]) / 1000.0
    return out


def classify_marks(con: sqlite3.Connection, buckets: Dict[str, Any], now: float,
                   limit: int = CLASSIFY_PER_STEP) -> Dict[str, int]:
    """Advance pending marks on closed 5m bars. Bounded per call."""
    ensure_schema(con)
    counts = {k: 0 for k in MARK_STATES}
    marks = [dict(r) for r in con.execute(
        "SELECT * FROM level_marks WHERE status='pending' ORDER BY marked_at LIMIT ?",
        (int(limit),))]
    for m in marks:
        cd = (buckets.get(m["symbol"]) or {}).get(MARK_TF)
        t = cd.get("open_time") if isinstance(cd, dict) else None
        if t is None or len(t) == 0:
            if now - m["marked_at"] > MARK_HORIZON_S:
                con.execute("UPDATE level_marks SET status='insufficient', resolved_at=? "
                            "WHERE mark_id=?", (now, m["mark_id"]))
                counts["insufficient"] += 1
            continue
        t = np.asarray(t, dtype=float)
        start_ms = m["marked_at"] * 1000.0
        end_ms = min(now, m["marked_at"] + MARK_HORIZON_S) * 1000.0
        sel = (t >= start_ms) & (t + MARK_TF_MS <= end_ms)
        if sel.any() and not np.all(np.diff(t[sel]) > 0):
            continue    # unsorted window: refuse rather than read bars out of order
        res = classify(bool(m["above"]), m["price"], m["tol"], t[sel],
                       np.asarray(cd["high"], float)[sel], np.asarray(cd["low"], float)[sel],
                       np.asarray(cd["close"], float)[sel])
        if res is not None:
            con.execute("UPDATE level_marks SET status=?, touched_at=?, resolved_at=?, "
                        "max_beyond_pct=? WHERE mark_id=?",
                        (res["status"], res["touched_at"], res["resolved_at"],
                         res["max_beyond_pct"], m["mark_id"]))
            counts[res["status"]] += 1
        elif now - m["marked_at"] > MARK_HORIZON_S:
            first = t[t >= start_ms]
            # Untested only if the bars actually cover the horizon; a series
            # that stopped is not evidence that price never came.
            covered = len(first) and first.max() + MARK_TF_MS >= end_ms - 2 * MARK_TF_MS
            status = "untested" if covered else "insufficient"
            con.execute("UPDATE level_marks SET status=?, resolved_at=? WHERE mark_id=?",
                        (status, now, m["mark_id"]))
            counts[status] += 1
    return counts


# ── the read ────────────────────────────────────────────────────────────────


def pair_book(symbol: str, *, path: Optional[str] = None, now: Optional[float] = None,
              limit: int = 30) -> Dict[str, Any]:
    import os

    from src import analyst_plan, analyst_walk

    now = time.time() if now is None else now
    path = path or analyst_plan.get_ledger().path
    if not os.path.exists(path):
        return {"symbol": symbol, "readable": False, "reason": "no_ledger_yet"}
    con = analyst_plan.Ledger(path)._connect()
    try:
        ensure_schema(con)
        notes = [dict(r) for r in con.execute(
            "SELECT plan_id, submitted_at, note, price_at_note FROM pair_notes "
            "WHERE symbol=? ORDER BY submitted_at DESC LIMIT 10", (symbol,))]
        marks = [dict(r) for r in con.execute(
            "SELECT setup_id, side, kind, price, above, status, marked_at, touched_at, "
            "max_beyond_pct FROM level_marks WHERE symbol=? ORDER BY marked_at DESC "
            "LIMIT ?", (symbol, int(limit)))]
        summary = {r[0]: r[1] for r in con.execute(
            "SELECT status, COUNT(*) FROM level_marks WHERE symbol=? GROUP BY status",
            (symbol,))}
    finally:
        con.close()
    for m in marks:
        m["role"] = "resistance" if m.pop("above") else "support"
    setups = [r for r in analyst_walk.feed(limit=analyst_walk.FEED_MAX, path=path,
                                           now=now).get("rows", [])
              if r.get("symbol") == symbol][:10]
    return {
        "symbol": symbol, "readable": True,
        "notes": [{**n, "label": "your earlier hypothesis, not a fact"} for n in notes],
        "level_marks": marks, "level_summary": summary,
        "setups": [{k: r.get(k) for k in ("submitted_at", "side", "archetype", "state",
                                          "p_target", "rr_tp1")}
                   | {"realized_net_pct": (0.0 if r.get("state") == "not_filled"
                                           else (r.get("analyst") or {}).get("net_pct"))}
                   for r in setups],
        "note": ("level_marks are engine-recorded facts: how price treated each level you "
                 "marked (respected / broke / swept_reclaimed / untested / pending). "
                 "notes are your own earlier hypotheses. setups are your last 10 on this "
                 "coin; a handful of trades is not evidence about the coin, so never "
                 "rule a coin in or out on them."),
    }
