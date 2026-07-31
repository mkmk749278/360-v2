"""Dark emission lane — the silent paths, actually emitting, owner-only.

The question this exists for, owner 2026-07-31: *"we have 75 pairs and almost 15
paths but only MOVER_TREND_PULLBACK is our volume — what happened to the
others?"*  The measurement answer (``suppression_audit``) is a counterfactual:
it stamps a killed candidate and scores it later, which is optimistic (~0.38R
measured) and cannot say what the **feed** would look like.  The owner asked for
the other thing: loosen the gates per path, let those paths **emit for real**,
and show the result to the owner only.

Why this is a separate lane and not a flag on the live one
----------------------------------------------------------
A signal that reaches ``SignalRouter`` reaches, in order: the paid Telegram
channel, ``signal_dispatch.dispatch_signal_to_active_users`` (**real capital on
real users' keys**), the FCM ``signals`` topic, the free channel, the app feed,
and ``_position_lock`` — that last one being the subtle one, because a dark
signal taking the correlation lock would **block a real signal** on that symbol
and change what subscribers receive without ever appearing to.

Six places, six correct skips, and one missed skip places an order.  So the
divergence is structural instead: the scanner **marks** a candidate at the
loosened gate and keeps going — every other gate still applies, which is the
whole point, we want to know what else would have killed it — and diverts at the
**single** ``signal_queue.put`` site.  A dark signal is never put on the queue,
so the router, the dispatcher, Telegram, FCM, the app feed and the position lock
are unreachable by construction rather than skipped by convention.

What this lane does NOT yet do, stated because the count would mislead
----------------------------------------------------------------------
``SignalRouter._process`` applies a second layer — correlation lock, per-symbol
and per-channel cooldown, per-channel concurrency cap, correlation-group limit,
global same-direction throttle — and **drops most of what it dequeues**.  This
lane does not apply it.

So a dark row means *"the scanner was willing to send this"*, **not** *"a user
would have seen this"*, and the count over-reports a feed size accordingly.
Every surface that renders these rows has to say so; a number labelled as a feed
when it is a pre-router population is the #816 error (``emitted`` stamped at the
enqueue site inflated the only population allowed to justify a live change by
~30x, non-randomly, and the ops page read "Emitted to live (98)" for a window
with 3 real signals).

The fix is to **extract** the router's throttle predicates so both lanes call one
implementation with different state — not to reimplement them here, which would
be the mirror this repo keeps paying for.  That is a change to
``SignalRouter._process``, i.e. **paid-channel routing**, which is an
owner-sign-off item, so it ships as its own reviewed change rather than riding
in on a measurement PR.

Enrolment (owner, 2026-07-31)
-----------------------------
* Loosened: ``setup_compat`` (the regime confinement that idles 14 paths —
  MEAN_REVERT dies here on 98% of its rejects, RANGE_FADE 89%,
  TREND_PULLBACK_EMA 97%) and ``execution`` (overextended /
  trigger_not_confirmed).
* **Not** loosened: ``min_confidence`` and the context floors.  Those already
  carry KEEP/TUNE/DROP verdicts in the audit, so they add least, and they are
  the last thing between a scored candidate and a feed.
* **MOVER_TREND_PULLBACK is excluded.**  It contributes 24,327 pre-scoring
  rejects in one window against ~18,000 from every other path combined, it
  already owns 64% of the delivered book, and admitting it here would make the
  dark feed a second MTP feed.  The owner set no per-path budget precisely
  because excluding MTP removes the need for one.
* Detector-level thresholds (``WHALE_MOMENTUM`` 0 of 118,642 on
  ``momentum_reject``) are a **separate** change: they live inside the
  evaluators, not the gate chain, and they need this lane to exist first.

Nothing here places an order, posts to any channel, or is visible to a user.
"""
from __future__ import annotations

import os
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from src import fail_open
from src.utils import get_logger

log = get_logger("dark_emission")

#: Attribute the scanner sets on a marked candidate. Read by the enqueue site.
DARK_ATTR = "dark_gate"

#: Gates whose rejection this lane overrides. Kept as prefixes because the token
#: carries the reason (``setup_compat:regime_STRONG_TREND``), and the reason is
#: what the owner reads.
LOOSENED_GATE_PREFIXES = ("setup_compat:", "execution:")

#: Paths never admitted to this lane. MOVER_TREND_PULLBACK owns 64% of the
#: delivered book and 24,327 of the 37,782 pre-scoring rejects in one window —
#: it does not need a dark feed to be understood, and it would drown the paths
#: that do.
EXCLUDED_SETUPS = frozenset(
    s.strip().upper()
    for s in os.getenv("DARK_EMISSION_EXCLUDED_SETUPS", "MOVER_TREND_PULLBACK").split(",")
    if s.strip()
)

#: Per-path ring size. The owner set no emission budget; this is a **storage**
#: bound, not a cap on what emits, and it is per path for the reason the
#: suppression store just learned the hard way — one shared ring makes the
#: loudest path the only readable one.
_PER_PATH_MAX: int = int(os.getenv("DARK_EMISSION_PER_PATH_MAX", "500"))
_MAX_PATHS: int = int(os.getenv("DARK_EMISSION_MAX_PATHS", "32"))

#: Ledger schema. Readers gate on this, never on a date (#802).
LEDGER_SCHEMA = 1

STATUS_OPEN = "OPEN"
STATUS_TP1 = "CLOSED_TP1"
STATUS_SL = "CLOSED_SL"
STATUS_EXPIRED = "EXPIRED"
#: Emitted by the scanner, then refused by the dark lane's own throttle. Not a
#: failure — it is the router layer doing what it does to live signals, and
#: counting it is how the feed's real size becomes knowable.
STATUS_THROTTLED = "THROTTLED"


def is_excluded(setup_class: Any) -> bool:
    """Is this path barred from the dark lane?"""
    return str(setup_class or "").upper() in EXCLUDED_SETUPS


def is_loosened_gate(gate_name: str) -> bool:
    return str(gate_name or "").startswith(LOOSENED_GATE_PREFIXES)


def enabled() -> bool:
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("dark_emission_enabled"))
    except Exception as exc:
        fail_open.record("dark_emission.enabled", exc)
        return False


def should_mark(sig: Any, gate_name: str) -> bool:
    """May this candidate continue past ``gate_name`` as a dark signal?

    Deliberately *not* "would it have been good" — that is what the forward
    measure is for.  This is admission only: the lane is on, the gate is one we
    loosen, the path is enrolled, and the candidate is not already dark (a
    candidate can be caught by both loosened gates, and the first one is the one
    that would have killed it live).
    """
    try:
        if not enabled():
            return False
        if not is_loosened_gate(gate_name):
            return False
        if is_excluded(getattr(sig, "setup_class", "")):
            return False
        return getattr(sig, DARK_ATTR, None) is None
    except Exception as exc:
        fail_open.record("dark_emission.should_mark", exc)
        return False


def mark(sig: Any, gate_name: str) -> None:
    """Record which gate this candidate is being carried past.

    Set on the signal rather than held here because the value has to survive
    the rest of the gate chain, and because the enqueue site — the one place
    that must never confuse a dark candidate for a live one — reads it directly.
    """
    try:
        setattr(sig, DARK_ATTR, str(gate_name))
    except Exception as exc:
        fail_open.record("dark_emission.mark", exc)


def is_dark(sig: Any) -> bool:
    """The single predicate the enqueue site branches on.

    Anything True here must never be handed to ``signal_queue.put``.
    """
    return getattr(sig, DARK_ATTR, None) is not None


# --------------------------------------------------------------------------- #
# Ledger
# --------------------------------------------------------------------------- #


class DarkLedger:
    """Bounded, per-path ring of dark-emitted signals and their outcomes."""

    DEFAULT_PATH = "data/dark_signals_live_v1.json"

    def __init__(
        self, path: Optional[str] = None, per_path_max: Optional[int] = None
    ) -> None:
        self._lock = threading.Lock()
        self._path = self.DEFAULT_PATH if path is None else path
        self._per_path_max = int(
            per_path_max if per_path_max is not None else _PER_PATH_MAX
        )
        self._paths: Dict[str, Deque[dict]] = {}
        self.emitted_total: int = 0
        self.throttled_total: int = 0
        self.paths_refused: int = 0
        self._dirty = False

    def add(self, row: dict) -> bool:
        with self._lock:
            setup = str(row.get("setup_class") or "UNKNOWN")
            ring = self._paths.get(setup)
            if ring is None:
                if len(self._paths) >= _MAX_PATHS:
                    self.paths_refused += 1
                    return False
                ring = deque(maxlen=self._per_path_max)
                self._paths[setup] = ring
            ring.append(row)
            if row.get("status") == STATUS_THROTTLED:
                self.throttled_total += 1
            else:
                self.emitted_total += 1
            self._dirty = True
            return True

    def rows(self) -> List[dict]:
        with self._lock:
            out: List[dict] = []
            for ring in self._paths.values():
                out.extend(ring)
        out.sort(key=lambda r: float(r.get("emitted_at") or 0.0), reverse=True)
        return out

    def open_rows(self) -> List[dict]:
        return [r for r in self.rows() if r.get("status") == STATUS_OPEN]

    def mark_dirty(self) -> None:
        with self._lock:
            self._dirty = True

    def flush(self, force: bool = False) -> bool:
        """Persist. Writes on a heartbeat even with nothing to say.

        An idle engine that writes nothing produces no file, and a missing file
        reads to ops as "the lane is not running" — a fault that is not
        happening.  #832 shipped exactly that bug and the owner caught it
        minutes after deploy.
        """
        import json

        with self._lock:
            if not (self._dirty or force):
                return False
            payload = {
                "schema": LEDGER_SCHEMA,
                "written_at": time.time(),
                "emitted_total": self.emitted_total,
                "throttled_total": self.throttled_total,
                "rows": [r for ring in self._paths.values() for r in ring],
            }
            self._dirty = False
        try:
            dirname = os.path.dirname(self._path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            tmp = self._path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:
            fail_open.record("dark_emission.flush", exc)
            return False

    def load(self) -> None:
        import json

        try:
            if not os.path.exists(self._path):
                return
            with open(self._path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            if not isinstance(raw, dict) or int(raw.get("schema") or 0) != LEDGER_SCHEMA:
                # A schema bump drops rows rather than reinterpreting them.
                return
            for row in raw.get("rows") or []:
                if isinstance(row, dict):
                    self.add(row)
            self.emitted_total = int(raw.get("emitted_total") or self.emitted_total)
            self.throttled_total = int(
                raw.get("throttled_total") or self.throttled_total
            )
        except Exception as exc:
            fail_open.record("dark_emission.load", exc)


_ledger: Optional[DarkLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> DarkLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = DarkLedger()
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[DarkLedger] = None) -> None:
    global _ledger
    with _ledger_lock:
        _ledger = ledger


# --------------------------------------------------------------------------- #
# Publish
# --------------------------------------------------------------------------- #


def _row_from_signal(sig: Any, now: float) -> dict:
    _direction = getattr(sig, "direction", None)
    return {
        "schema": LEDGER_SCHEMA,
        "signal_id": str(getattr(sig, "signal_id", "") or ""),
        "symbol": str(getattr(sig, "symbol", "") or ""),
        "channel": str(getattr(sig, "channel", "") or ""),
        "setup_class": str(getattr(sig, "setup_class", "") or "UNKNOWN"),
        "side": str(getattr(_direction, "value", None) or _direction or ""),
        "entry": float(getattr(sig, "entry", 0.0) or 0.0),
        "stop_loss": float(getattr(sig, "stop_loss", 0.0) or 0.0),
        "tp1": float(getattr(sig, "tp1", 0.0) or 0.0),
        # Which gate carried it here. The whole point of the lane: this row
        # exists because THIS gate said no, so the gate's name is the finding.
        "dark_gate": str(getattr(sig, DARK_ATTR, "") or ""),
        # Scored confidence, not the evaluator's — a dark signal has been
        # through the full scoring engine and every gate except the loosened
        # one, which is exactly what makes it different from a suppression stamp.
        "confidence": float(getattr(sig, "confidence", 0.0) or 0.0),
        "regime": str(getattr(sig, "entry_regime", "") or ""),
        "context_key": str(getattr(sig, "mc_context_key", "") or ""),
        "valid_for_minutes": float(getattr(sig, "valid_for_minutes", 0.0) or 0.0),
        "pair_admission": str(getattr(sig, "pair_admission", "") or ""),
        "emitted_at": now,
        "status": STATUS_OPEN,
        "closed_at": None,
        "exit_price": None,
        "pnl_pct": None,
        "r_multiple": None,
        "mfe_pct": 0.0,
        "bars_seen": 0,
        "last_bar_ms": None,
    }


def publish(sig: Any, now_ts: Optional[float] = None) -> bool:
    """Record a dark signal. Returns True when it entered the ledger.

    Called from the **one** site that would otherwise enqueue, so reaching here
    means the candidate cleared every gate except the loosened one — scoring,
    MTF, min_confidence, the context floors, level_still_in_play, dispatch
    cooldown and staleness all still said yes.  That is what makes these rows
    different in kind from a suppression stamp: a stamp is a candidate, this is
    a signal the engine was willing to send.

    It is still **not** what a subscriber would have received, and the ledger
    says so: ``SignalRouter`` applies a second layer this lane does not yet
    share (correlation lock, cooldowns, concurrency caps, same-direction
    throttle) and drops most of what it dequeues.  Until those predicates are
    extracted for both lanes to call, a dark row means *"the scanner would have
    sent this"*, not *"a user would have seen this"* — and the page must say the
    difference rather than let the count read as a feed size.
    """
    now = time.time() if now_ts is None else float(now_ts)
    try:
        row = _row_from_signal(sig, now)
        if row["entry"] <= 0 or row["stop_loss"] <= 0 or row["tp1"] <= 0:
            # No tradeable geometry, nothing to forward-measure. Refuse rather
            # than store a row that can never resolve.
            return False
        ledger = get_ledger()
        ok = ledger.add(row)
        if ok:
            log.info(
                "[DARK] {} {} {} past {} conf={:.1f} — owner-only, no user, no order",
                row["symbol"], row["side"], row["setup_class"],
                row["dark_gate"], row["confidence"],
            )
        return ok
    except Exception as exc:
        fail_open.record("dark_emission.publish", exc)
        return False


# --------------------------------------------------------------------------- #
# Forward resolution — on the money-path clock, not a replay
# --------------------------------------------------------------------------- #


def _walk(row: dict, ohlc: Dict[str, List[float]]) -> Optional[dict]:
    """Resolve one dark signal by walking bars in order.

    Bars in order, never window extremes: a bar that touches both TP1 and SL
    cannot be ordered from OHLC, and taking the max/min of the whole window
    silently books whichever the reader prefers. Ambiguity is resolved
    pessimistically **and flagged**, so the row is visibly a judgement rather
    than quietly averaged in as a fact.
    """
    highs, lows = ohlc.get("high"), ohlc.get("low")
    if highs is None or lows is None or len(highs) == 0:
        return None
    entry = float(row["entry"])
    sl = float(row["stop_loss"])
    tp1 = float(row["tp1"])
    if entry <= 0:
        return None
    is_long = str(row.get("side") or "").upper() == "LONG"
    sl_dist_pct = abs(entry - sl) / entry * 100.0
    mfe = float(row.get("mfe_pct") or 0.0)
    for i in range(len(highs)):
        hi, lo = float(highs[i]), float(lows[i])
        fav = (hi - entry) if is_long else (entry - lo)
        mfe = max(mfe, fav / entry * 100.0)
        sl_hit = (lo <= sl) if is_long else (hi >= sl)
        tp_hit = (hi >= tp1) if is_long else (lo <= tp1)
        if sl_hit or tp_hit:
            ambiguous = bool(sl_hit and tp_hit)
            # Pessimistic on a same-bar tie.
            exit_price = sl if sl_hit else tp1
            status = STATUS_SL if sl_hit else STATUS_TP1
            pnl = ((exit_price - entry) if is_long else (entry - exit_price)) / entry * 100.0
            return {
                "status": status,
                "exit_price": exit_price,
                "pnl_pct": pnl,
                "r_multiple": (pnl / sl_dist_pct) if sl_dist_pct > 0 else None,
                "mfe_pct": mfe,
                "ambiguous_bar": ambiguous,
                "bars_seen": i + 1,
            }
    return {"mfe_pct": mfe, "bars_seen": len(highs)}


def resolve_open(
    fetch_ohlc_since: Any,
    *,
    now_ts: Optional[float] = None,
    horizon_sec: float = 6 * 3600.0,
    ledger: Optional[DarkLedger] = None,
) -> Dict[str, int]:
    """Advance every open dark row. Returns a per-cycle tally.

    Keyed on **the rows owed a verdict** (#815/#835), not on the live universe
    or the current scan set — a dark signal on a symbol that has since rotated
    out is exactly the row most at risk of never resolving, and it stays in this
    population whether or not its symbol does.

    A row past ``horizon_sec`` with no touch is EXPIRED, which is a real outcome
    for a scalp and is counted apart from a loss: the mechanism did nothing, it
    did not lose. Rows whose candles cannot be fetched are left OPEN and counted
    as ``no_candles`` — an unresolved row must never be scored, because a
    loss-selected sample is worse than no sample.
    """
    now = time.time() if now_ts is None else float(now_ts)
    book = ledger if ledger is not None else get_ledger()
    tally = {"resolved": 0, "still_open": 0, "expired": 0, "no_candles": 0}
    try:
        for row in book.open_rows():
            ts = float(row.get("emitted_at") or 0.0)
            if ts <= 0:
                continue
            try:
                ohlc = fetch_ohlc_since(str(row.get("symbol") or ""), ts)
            except Exception as exc:
                fail_open.record("dark_emission.fetch_ohlc", exc)
                ohlc = None
            # None/len checks, never truthiness: the data store holds numpy
            # arrays and `not ohlc` raises on them, which is the class that
            # killed 8 features silently on 2026-07-14.
            if ohlc is None or len(ohlc) == 0:
                tally["no_candles"] += 1
                continue
            out = _walk(row, ohlc)
            if out is None:
                tally["no_candles"] += 1
                continue
            row.update(out)
            if out.get("status"):
                row["closed_at"] = now
                tally["resolved"] += 1
            elif (now - ts) >= horizon_sec:
                row["status"] = STATUS_EXPIRED
                row["closed_at"] = now
                # No fill, no loss. Scored 0R deliberately: the honest cost of a
                # setup that never resolved is nothing happening, not a stop.
                row["pnl_pct"] = 0.0
                row["r_multiple"] = 0.0
                tally["expired"] += 1
            else:
                tally["still_open"] += 1
            book.mark_dirty()
        book.flush()
    except Exception as exc:
        fail_open.record("dark_emission.resolve_open", exc)
    return tally


def summary(ledger: Optional[DarkLedger] = None) -> Dict[str, Any]:
    """Per-path rollup. Resolved rows only — an open row has no outcome, and
    pooling it as a zero would drag every path toward flat."""
    book = ledger if ledger is not None else get_ledger()
    out: Dict[str, Any] = {}
    for row in book.rows():
        setup = str(row.get("setup_class") or "UNKNOWN")
        agg = out.setdefault(setup, {
            "setup_class": setup, "n": 0, "open": 0, "resolved": 0,
            "tp1": 0, "sl": 0, "expired": 0, "sum_r": 0.0, "n_r": 0,
            "gates": {},
        })
        agg["n"] += 1
        gate = str(row.get("dark_gate") or "")
        agg["gates"][gate] = agg["gates"].get(gate, 0) + 1
        status = row.get("status")
        if status == STATUS_OPEN:
            agg["open"] += 1
            continue
        agg["resolved"] += 1
        if status == STATUS_TP1:
            agg["tp1"] += 1
        elif status == STATUS_SL:
            agg["sl"] += 1
        elif status == STATUS_EXPIRED:
            agg["expired"] += 1
        r = row.get("r_multiple")
        if r is not None:
            agg["sum_r"] += float(r)
            agg["n_r"] += 1
    for agg in out.values():
        agg["avg_r"] = (agg["sum_r"] / agg["n_r"]) if agg["n_r"] else None
        decided = agg["tp1"] + agg["sl"]
        # Win rate over DECIDED rows: an expiry is neither a win nor a loss, and
        # counting it as a loss is the #685 fabrication class.
        agg["win_rate"] = (agg["tp1"] / decided) if decided else None
    return out
