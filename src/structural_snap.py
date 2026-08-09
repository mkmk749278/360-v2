"""Structural SL/TP1 snap — the level-aware half of signal geometry.

What this is
------------
Every live evaluator computes its stop and its targets **arithmetically**: a
buffer off a moving average or a prior bar for the stop, then fixed R-multiples
off that distance for TP1/TP2/TP3.  ``MOVER_TREND_PULLBACK`` — 59% of the
enqueued book on the 2026-08-04 truth report — is the clearest case:
``sl = min(ma_mid, prev_low) - atr*buf``, then ``tp1/tp2/tp3 = sl_dist ×
1.0/1.6/2.5``.  Nothing in that chain asks where price has actually traded, so
TP1 lands wherever the multiplication puts it, which may be a hair beyond a
swing high that has rejected four times, and the stop may sit a hair inside one.

``structural_levels.py`` has held the repair since it was written — snap the
stop to the nearest swing low / round number inside 0.7–1.3× the designed risk,
and pull TP1 back to resistance when resistance is inside 0.8–1.2× the designed
target.  ``channels/base.build_channel_signal`` even called it.

It has never run.  The call was guarded on ``candle_highs is not None`` and
**no caller in the engine has ever passed that argument** (``grep -rn
candle_highs src/`` matched only the parameter's own definition), while the
function's own comment read *"this snap is shared by EVERY evaluator that
passes candle arrays"*.  It was dead twice over: every evaluator overwrites
``sig.stop_loss`` / ``sig.tp1`` immediately after ``build_channel_signal``
returns, so the snapped values would have been discarded even had the arrays
arrived.  Same class as #817 (a field one repo reads and no repo writes), one
layer down — a parameter one function reads and no caller writes.

What ships here
---------------
The mechanism, wired end to end, at the one place the geometry is final.

**Measurement is ON** (``structural_snap_measure``, default true) and **effect
is OFF** (``structural_snap_apply``, default false) — the two flags the
production dark-first rule requires, and they are not the same flag.  From the
moment this deploys every enqueued signal carries a row saying what the snap
*would* have done; nothing a subscriber receives changes until the owner flips
the second flag, per path, on the measured result.

Why the seam is ``_enqueue_signal`` and not the evaluator
---------------------------------------------------------
"Record a fact where it becomes true" is a point in the call graph.  A signal's
geometry is rewritten **four** times after the evaluator sets it: the
noise-floor widener, ``predictive.adjust_tp_sl``, the min-distance clamp at the
top of ``_enqueue_signal``, and the TP rescale that clamp performs.  Snapping
any earlier measures a stop that is not the stop, and #848 is exactly the bill
for a denominator that moved after it was stamped.  ``_enqueue_signal`` is the
single choke point every path passes through, and this runs *after* its clamp.

No resolver
-----------
There is deliberately none.  Rows are keyed by ``signal_id`` and joined to
``signal_performance.json``, which ``trade_monitor`` already writes correctly at
the terminal transition — including ``max_favorable_excursion_pct`` and
``max_adverse_excursion_pct``, which is what makes most of the counterfactual
decidable without walking a single bar.  Every measurement arm in this repo
that grew its own forward-resolution machinery cost a session to unresolvable
rows; this one needs none.

What the join can and cannot decide (stated here because it bounds the verdict)
-------------------------------------------------------------------------------
The TP1 arm snaps **nearer only**, so it is fully decidable from MFE: a trade
that reached its own TP1 necessarily passed a nearer one, and a trade that
stopped out reached the nearer target iff ``MFE ≥ snapped TP1 distance`` — all
excursion is recorded before the close, so there is no ordering ambiguity.

The SL arm is **not** fully decidable and the undecidable part is
direction-biased, which is the trap.  A *wider* snapped stop on a trade that
stopped out asks whether price would have come back, and the walk ended at the
stop — unknowable.  A *tighter* snapped stop on a winner asks whether MAE was
reached before TP1 or after, and MFE/MAE carry no ordering between them.  Ops
therefore publishes the two arms separately with their decidable fractions on
screen and never blends them into one "would the snap have helped" number.  A
loss-selected sample is worse than no sample because it looks like an answer.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np

from src import ledger_schema
from src import fail_open
from src.setup_timeframes import TF_BY_SETUP as _TF_BY_SETUP
from src.structural_levels import (
    find_round_numbers,
    find_structural_sl_detail,
    find_structural_tp_detail,
    find_swing_levels,
    round_step_for,
)
from src.delivery_retention import DeliveryRetainedRing
from src.utils import get_logger

log = get_logger("structural_snap")

SCHEMA = 1

#: Older schemas this build reads unchanged. EMPTY on purpose: no bump here has
#: been declared additive, so every one drops its window — which is safe but is
#: a *decision*, not an accident. Before bumping SCHEMA, ask whether the change
#: only ADDS fields; if so add the old number here, or the first flush after
#: deploy silently destroys the ledger (`ledger_schema`, and the 371 SAR rows
#: lost on 2026-08-09).
ADDITIVE_FROM_SCHEMAS: frozenset = frozenset()


_DEFAULT_PATH = os.path.join("data", "structural_snap_v1.json")
_MAX_ROWS = 4000

#: Search-band bounds, mirrored from ``structural_levels`` so the ledger ships
#: them and ops renders the contract rather than keeping its own copy.  The fix
#: for a drifting mirror is one writer and one reader, not a second mirror.
SL_BAND = (0.7, 1.3)
TP1_BAND = (0.8, 1.2)
SWING_LOOKBACK = 20
SWING_WINDOW = 3

#: The evaluator's own trigger timeframe, per setup class.
#:
#: **Not a copy** — this is the same object as ``setup_timeframes.TF_BY_SETUP``,
#: re-exported under the name this module already used.  The map was written
#: here first, for the snap (a 5m swing and a 15m swing are different levels);
#: it turned out the scanner needs exactly the same answer for scoring, because
#: ``_get_primary_timeframe`` returned the literal ``"5m"`` for every channel.
#: A second consumer means a second copy, and a second copy is the drift that
#: silently inflated the Strategy Lab rollup for a week — so the declaration
#: moved to one module and both subsystems import it.
#:
#: A setup absent from the map is **refused and named** (``tf_unknown``), never
#: defaulted to 5m.  A hand-maintained map is a floor, silent by construction on
#: the next evaluator; making the miss a counted refusal is what stops a new
#: path from being quietly snapped against the wrong timeframe's structure.
SNAP_TF_BY_SETUP: Dict[str, str] = _TF_BY_SETUP

# ── Refusal reasons ─────────────────────────────────────────────────────────
# Each is its own state because the reader's next move differs for each, and
# pooling them is how a page reports a fault that is not happening.
REFUSE_TF_UNKNOWN = "tf_unknown"            # setup not in SNAP_TF_BY_SETUP
REFUSE_NO_CANDLES = "no_candles"            # store has no series for that TF
REFUSE_SHORT_SERIES = "short_series"        # fewer bars than swing detection needs
REFUSE_BAD_PRICES = "bad_prices"            # non-finite / non-positive input
REFUSE_NO_GEOMETRY = "no_geometry"          # signal carries no usable SL or TP1
REFUSE_MIN_DISTANCE = "would_breach_min_distance"   # apply-only
REFUSE_WRONG_SIDE = "would_cross_entry"             # apply-only
REFUSE_REDETECT = "redetect_cooldown"               # same move, already stamped


@dataclass
class SnapCounters:
    """In-process counters.  Read by the liveness probe and the ops panel.

    Read from a counter the engine itself increments — never from a tunable
    lookup in a side process, which returns the boot default and has already
    misled one diagnosis (2026-08-02).
    """

    evaluated: int = 0
    stamped: int = 0
    applied_sl: int = 0
    applied_tp1: int = 0
    refused: Dict[str, int] = field(default_factory=dict)

    def refuse(self, reason: str) -> None:
        self.refused[reason] = self.refused.get(reason, 0) + 1

    def as_dict(self) -> Dict[str, Any]:
        return {
            "evaluated": self.evaluated,
            "stamped": self.stamped,
            "applied_sl": self.applied_sl,
            "applied_tp1": self.applied_tp1,
            "refused": dict(self.refused),
        }


_counters = SnapCounters()

#: (symbol, direction, setup_class) -> last stamp time.
#:
#: A THROTTLE ON EVIDENCE, not on rate. A setup persists across many scans, so
#: without this one move contributes a row per scan and the ledger's verdict
#: becomes an artefact of re-detection rather than of the mechanism. Owner
#: export 2026-08-05: **51 rows from 6 distinct setups**, EPICUSDT SHORT alone
#: 30 of them (59%) — every one carrying the *identical* `shift_pct`, i.e. the
#: same level and the same geometry counted thirty times. The same shape had
#: already filled this ledger with 211 re-detections of one RIFUSDT setup, and
#: SLXUSDT's 10 rows in 2h10m inside a 0.37% spread inverted a whole
#: population's sign (32% win per row against 55% per move).
#:
#: The key is deliberately MINIMAL — symbol, direction, setup. Nothing in it can
#: oscillate within a move, because a key that splits a budget multiplies it:
#: the SAR cooldown carried provenance and a candidate flipping across a gate
#: boundary therefore held two budgets.
_last_stamp: Dict[str, float] = {}

#: Matched to `price_action_lane.EMIT_COOLDOWN_S`. One number for "how long is
#: one move" across every lane that needs the answer.
REDETECT_COOLDOWN_S = 1800.0


def _redetect_key(symbol: str, direction: str, setup_class: str) -> str:
    return f"{symbol}|{direction}|{setup_class}"


def reset_redetect_state() -> None:
    """Test hook. Never called in production."""
    _last_stamp.clear()


def get_counters() -> SnapCounters:
    return _counters


def reset_counters() -> None:
    global _counters
    _counters = SnapCounters()



# ── Flags ───────────────────────────────────────────────────────────────────

def measure_enabled() -> bool:
    """Stamping.  Default **ON** — a measurement shipped OFF produces an empty
    panel and a decision that keeps being deferred."""
    try:
        from src import runtime_tunables as _rt
        return bool(_rt.get("structural_snap_measure"))
    except Exception:  # noqa: BLE001 — a tunable read must never block emission
        return True


def apply_enabled(setup_class: str) -> bool:
    """Whether the snap actually moves this path's geometry.

    Default **OFF**, and gated twice: a global switch plus an explicit
    per-setup allow-list.  A single global flag would flip 19 paths at once on
    evidence gathered from the one path that is most of the book — the shape
    that put nine dead Layer-G overrides into Firestore (#806).
    """
    try:
        from src import runtime_tunables as _rt
        if not bool(_rt.get("structural_snap_apply")):
            return False
        allowed = str(_rt.get("structural_snap_apply_paths") or "")
    except Exception:  # noqa: BLE001
        return False
    if not allowed.strip():
        return False
    wanted = {p.strip().upper() for p in allowed.split(",") if p.strip()}
    return str(setup_class or "").upper() in wanted


def snap_timeframe(setup_class: str) -> Optional[str]:
    return SNAP_TF_BY_SETUP.get(str(setup_class or "").upper())


# ── Computation ─────────────────────────────────────────────────────────────

def _finite(*values: Any) -> bool:
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            return False
        if not np.isfinite(f) or f <= 0:
            return False
    return True


def compute(
    *,
    direction: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    highs: Any,
    lows: Any,
    closes: Any,
    tf: str = "",
) -> Dict[str, Any]:
    """What the snap would do to one signal's geometry.

    Pure compute, no I/O, no mutation.  Returns a row dict; ``refused`` is
    non-empty exactly when no verdict is possible, and is never blank with a
    caption invented for it.

    Refuses rather than clamps on an input that cannot support the work: a
    series too short for ±3-bar swing confirmation yields no swings, and
    reporting "no structural level nearby" for it would be a claim about the
    market made from a fact about the buffer.
    """
    row: Dict[str, Any] = {
        "tf": tf,
        "refused": "",
        "sl_arith": None,
        "sl_snapped": None,
        "sl_source": None,
        "sl_shift_pct": None,
        "tp1_arith": None,
        "tp1_snapped": None,
        "tp1_source": None,
        "tp1_shift_pct": None,
        "n_swing_highs": None,
        "n_swing_lows": None,
        "round_step_pct": None,
        "bars": None,
    }

    if not _finite(entry, stop_loss, tp1):
        row["refused"] = REFUSE_NO_GEOMETRY
        return row

    is_long = "LONG" in str(direction).upper()
    # The evaluator's designed risk — the quantity both bands are relative to.
    sl_dist = abs(float(entry) - float(stop_loss))
    if sl_dist <= 0:
        row["refused"] = REFUSE_NO_GEOMETRY
        return row

    # Never boolean-test a candle array: the store holds numpy arrays and
    # truthiness raises.
    if highs is None or lows is None or closes is None:
        row["refused"] = REFUSE_NO_CANDLES
        return row
    h = np.asarray(highs, dtype=np.float64).ravel()
    lo = np.asarray(lows, dtype=np.float64).ravel()
    c = np.asarray(closes, dtype=np.float64).ravel()
    n = int(min(len(h), len(lo), len(c)))
    row["bars"] = n
    if n == 0:
        row["refused"] = REFUSE_NO_CANDLES
        return row
    if n < 2 * SWING_WINDOW + 1:
        row["refused"] = REFUSE_SHORT_SERIES
        return row
    if not (np.all(np.isfinite(h[-SWING_LOOKBACK:])) and np.all(np.isfinite(lo[-SWING_LOOKBACK:]))):
        row["refused"] = REFUSE_BAD_PRICES
        return row

    swings = find_swing_levels(h[:n], lo[:n], c[:n], lookback=SWING_LOOKBACK)
    rounds = find_round_numbers(float(entry))

    sl_pick = find_structural_sl_detail(
        "LONG" if is_long else "SHORT",
        float(entry), float(stop_loss), swings, rounds, sl_dist,
        SL_BAND[0], SL_BAND[1],
    )
    tp1_pick = find_structural_tp_detail(
        "LONG" if is_long else "SHORT",
        float(entry), float(tp1), swings, rounds,
    )

    row.update({
        "sl_arith": round(float(stop_loss), 8),
        "sl_snapped": round(float(sl_pick.price), 8),
        "sl_source": sl_pick.source,
        "tp1_arith": round(float(tp1), 8),
        "tp1_snapped": round(float(tp1_pick.price), 8),
        "tp1_source": tp1_pick.source,
        "n_swing_highs": len(swings.get("swing_highs", [])),
        "n_swing_lows": len(swings.get("swing_lows", [])),
        # The round grid's granularity at this price, as a percentage. It is an
        # absolute ladder against a relative consumer, so it is fine-grained on
        # BTC and 20%-wide on a sub-cent alt, where it contributes nothing.
        # Stamped so an all-"swing" source column reads as the grid being inert
        # rather than as round numbers being unhelpful.
        "round_step_pct": round(round_step_for(float(entry)) / float(entry) * 100.0, 4),
    })

    # Signed toward risk/reward, not toward price: positive SL shift = the stop
    # moved FURTHER from entry (more risk), positive TP1 shift = the target
    # moved FURTHER (more reward). Without that convention every SHORT reads
    # backwards, which is how two entry features spent a schema version looking
    # like noise.
    new_sl_dist = abs(float(entry) - float(sl_pick.price))
    new_tp1_dist = abs(float(tp1_pick.price) - float(entry))
    tp1_dist = abs(float(tp1) - float(entry))
    row["sl_shift_pct"] = round((new_sl_dist - sl_dist) / float(entry) * 100.0, 6)
    row["tp1_shift_pct"] = round((new_tp1_dist - tp1_dist) / float(entry) * 100.0, 6)
    return row


def describe_spec() -> Dict[str, Any]:
    """The contract, as data, shipped inside the ledger.

    Ops renders bands, timeframes and refusal reasons from this rather than
    keeping its own copy — ``MEASUREMENT_SUFFIXES`` drifted for a week and the
    lesson was one writer, one reader.
    """
    return {
        "schema": SCHEMA,
        "sl_band": list(SL_BAND),
        "tp1_band": list(TP1_BAND),
        "swing_lookback": SWING_LOOKBACK,
        "swing_window": SWING_WINDOW,
        "tf_by_setup": dict(SNAP_TF_BY_SETUP),
        "refusals": [
            REFUSE_TF_UNKNOWN, REFUSE_NO_CANDLES, REFUSE_SHORT_SERIES,
            REFUSE_BAD_PRICES, REFUSE_NO_GEOMETRY, REFUSE_MIN_DISTANCE,
            REFUSE_WRONG_SIDE,
        ],
        # TP1 only ever tightens; SL may move either way inside its band. Ops
        # needs this to know which arm is decidable from MFE alone.
        "tp1_direction": "nearer_only",
        "sl_direction": "both",
    }


# ── Ledger ──────────────────────────────────────────────────────────────────

class SnapLedger:
    """Append-only ring of snap stamps, keyed by ``signal_id``."""

    def __init__(self, path: Optional[str] = None, max_rows: Optional[int] = None) -> None:
        self._path = _DEFAULT_PATH if path is None else path
        # Retention by DELIVERY, not by recency (Phase 6). This ring is filled
        # by enqueues of which ~0.5% deliver, so oldest-first eviction spends
        # the cap destroying the rare population to make room for the common
        # one — and does it silently, because the ledger stays exactly full.
        self._ring = DeliveryRetainedRing(
            name="structural_snap",
            max_pending=max_rows or _MAX_ROWS,
        )
        self._lock = threading.RLock()
        self._dirty = False

    # `duplicate_skips` / `evicted` stay readable at their old names: the
    # truth report and the ops payload both read them, and a rename would be a
    # cross-process contract break for no gain.
    @property
    def duplicate_skips(self) -> int:
        return self._ring.duplicate_skips

    @property
    def evicted(self) -> int:
        """Pending-row evictions only.

        Deliberately NOT the sum with `evicted_delivered`: one is cheap
        evidence rotating out as designed, the other is the retention policy
        losing a confirmed row, and a single figure covering both would move
        with enqueue volume rather than with the thing worth knowing.
        """
        return self._ring.evicted_pending

    def add(self, row: dict) -> bool:
        if self._ring.add(row):
            with self._lock:
                self._dirty = True
            return True
        return False


    def load(self) -> None:
        """Read the ledger back at boot.

        **This was missing, and flush without load is worse than neither.** The
        lane persisted every cycle and started from an empty ring on every
        restart, so the first flush after boot OVERWROTE the file with what had
        accumulated since — the snap ledger went 12 rows to 8 across one
        afternoon's deploys while its own panel read "nothing evicted", because
        nothing was: the previous window had been destroyed, not rotated
        (owner data, 2026-08-06).

        #842's class, the other half. That entry says a round trip is a
        contract and to follow a field all the way to disk AND BACK; here the
        return leg did not exist at all. Restores through `ring.restore` rather
        than `add` so a row that was DELIVERED comes back protected — retention
        rebuilt as evict-by-recency would be correct until the first restart
        and silently wrong after it.
        """
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            _ok, _why = ledger_schema.accepts(
                payload.get("schema"), SCHEMA, ADDITIVE_FROM_SCHEMAS
            )
            if not _ok:
                log.info(
                    "{}: ledger schema {} != {}, starting fresh",
                    "structural_snap", payload.get("schema"), SCHEMA,
                )
                return
            with self._lock:
                for row in payload.get("rows") or []:
                    if str(row.get("signal_id") or ""):
                        self._ring.restore(row)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("structural_snap.load", exc)

    def mark_delivered(self, signal_id: str) -> bool:
        """Promote after the router confirmed delivery."""
        if self._ring.mark_delivered(signal_id):
            with self._lock:
                self._dirty = True
            return True
        return False

    def note_duplicate(self) -> None:
        """Count a duplicate the caller rejected before it reached the ring."""
        self._ring.note_duplicate()

    def has(self, signal_id: str) -> bool:
        """Is this signal already stamped?

        Exposed so the re-detect throttle can run AFTER the duplicate check: a
        second stamp of ONE signal_id is a fault (the choke point ran twice),
        while two signals on one move is expected. Letting the throttle
        pre-empt the fault detector would file a real bug in the bucket that
        exists for an expected condition — which is how a fault stops standing
        out.
        """
        return signal_id in self._ring

    def rows(self) -> List[dict]:
        return self._ring.rows()

    def retention(self) -> Dict[str, Any]:
        return self._ring.stats()

    def flush(self, force: bool = False) -> bool:
        """Persist.  ``force`` writes even when unchanged, so an idle lane still
        proves it is alive — an ops page cannot tell "quiet" from "stopped"
        without a heartbeat, and a heartbeat that only fires on change is not
        one."""
        with self._lock:
            if not (self._dirty or force):
                return False
            # ``path=""`` means in-memory (what tests construct with). Return
            # BEFORE the side effect: a no-op that touches the disk wrote stray
            # .tmp files into the repo root for two months and raised into
            # fail_open on every test run.
            if not self._path:
                self._dirty = False
                return False
            self._dirty = False
        rows = self._ring.rows()
        _ret = self._ring.stats()
        evicted = _ret["evicted_pending"]
        payload = {
            "schema": SCHEMA,
            "written_at": time.time(),
            # The ring is capped, so every rate computed on it is a sample.
            # Persist the eviction count WITH the data: a reader in another
            # process cannot see the cap, and a verdict without its denominator
            # reads as if it covered everything.
            "max_rows": _ret["max_pending"],
            "evicted": evicted,
            # Phase 6. Named apart from `evicted` because they are different
            # events: one is designed rotation, the other is a lost verdict.
            "retention": _ret,
            "counters": _counters.as_dict(),
            # Resolver liveness only. NOT a book fraction — six consumers call
            # resolve() per candidate, so this denominator is ~6x the signal
            # count. The per-signal truth is `score_tf_mismatch` on each row.
            "tf_census": _tf_census(),
            "rows": rows,
            "spec": describe_spec(),
        }
        tmp = f"{self._path}.tmp"
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:  # noqa: BLE001
            fail_open.record("structural_snap.flush", exc)
            return False



def _tf_census() -> Dict[str, Any]:
    """The scoring-timeframe resolver's own counters, for liveness.

    Fail-soft: this rides in the ledger payload, and a census that cannot be
    read must not stop the rows being written.
    """
    try:
        from src import setup_timeframes as _stf
        return _stf.summary()
    except Exception as exc:  # noqa: BLE001
        fail_open.record("structural_snap.tf_census", exc)
        return {}


def stamp_and_apply(
    sig: Any,
    *,
    candles: Any,
    min_sl_distance: float = 0.0,
) -> Optional[Dict[str, Any]]:
    """Stamp what the snap would do, and — only when its path is switched on —
    do it.

    Called from ``Scanner._enqueue_signal`` **after** the min-distance clamp,
    which is the first moment ``sig.stop_loss`` / ``sig.tp1`` are the numbers
    that will actually be parked.

    Returns the stamped row, or ``None`` when measurement is disabled.

    The apply half re-validates against the same invariants the clamp above it
    enforces and **refuses** rather than clamping when it cannot satisfy them:
    the snap band bottoms out at 0.7× the designed risk, which can land inside
    the ``max(0.8%, 1×ATR)`` floor, and quietly widening back to the floor
    would book a stop nobody chose.  A refusal is counted and named apart from
    a measurement refusal, because the measurement is fine and only the action
    was declined.
    """
    if not measure_enabled():
        return None

    _counters.evaluated += 1
    setup_class = str(getattr(sig, "setup_class", "") or getattr(sig, "channel", "") or "")
    direction: Any = getattr(sig, "direction", None)
    dir_str = str(getattr(direction, "value", direction) or "")
    entry = float(getattr(sig, "entry", 0) or 0)
    symbol = str(getattr(sig, "symbol", "") or "")

    # The duplicate check runs FIRST. A second stamp of one signal_id means the
    # choke point ran twice — a fault — while two signal_ids on one move is
    # expected. If the throttle pre-empted this, a real bug would be filed under
    # the bucket that exists for an expected condition.
    _sid = str(getattr(sig, "signal_id", "") or "")
    if _sid and get_ledger().has(_sid):
        get_ledger().note_duplicate()
        return None

    # One move, one row. Counted and named, never silent — a suppressed
    # re-detection and a setup that never fired are different facts, and the
    # panel divides by this to show how concentrated the ledger really is.
    _now = time.time()
    _key = _redetect_key(symbol, dir_str, setup_class)
    _prev = _last_stamp.get(_key, 0.0)
    if _prev and (_now - _prev) < REDETECT_COOLDOWN_S:
        _counters.refuse(REFUSE_REDETECT)
        return None
    _last_stamp[_key] = _now

    base: Dict[str, Any] = {
        "signal_id": str(getattr(sig, "signal_id", "") or ""),
        "symbol": str(getattr(sig, "symbol", "") or ""),
        "setup_class": setup_class,
        "direction": dir_str,
        "entry": entry,
        "stamped_at": time.time(),
        # Whether the row's own path was live at stamp time. A row measured
        # while the path was dark and one measured while it was applying are
        # different populations; pooling them would average a counterfactual
        # with a realised outcome.
        "apply_mode": bool(apply_enabled(setup_class)),
        "applied_sl": False,
        "applied_tp1": False,
        "apply_refused": "",
    }

    # Per-setup scoring-timeframe census, stamped ONCE per signal.
    #
    # `Scanner._get_primary_timeframe` was `return "5m"` for every channel, and
    # six money-path consumers read it — continuation-sweep evidence, the
    # VWAP / OI / volume-divergence gates, the chart-pattern confidence bonus,
    # and the volume inputs to the composite score. It is corrected behind
    # `setup_tf_correction_live` (default off).
    #
    # It lives on this row rather than in `setup_timeframes`' own counters
    # because those count *resolutions* — six per candidate — so a book
    # fraction computed from them would be inflated ~6x while looking entirely
    # plausible. One row per signal is the denominator the ops panel needs.
    try:
        from src import setup_timeframes as _stf
        _declared = _stf.declared_for(setup_class)
        _tf_live = _stf.correction_live()
        _used = _declared if (_tf_live and _declared) else _stf.LEGACY_TF
        base["score_tf_declared"] = _declared
        base["score_tf_used"] = _used
        base["score_tf_correction_live"] = bool(_tf_live)
        # None (unmapped) is not a mismatch and not an agreement — a setup with
        # no declared timeframe is its own state, or a new evaluator silently
        # inherits 5m and reads as healthy.
        base["score_tf_mismatch"] = (
            None if _declared is None else bool(_declared != _stf.LEGACY_TF)
        )
    except Exception as _tf_exc:  # noqa: BLE001
        fail_open.record("structural_snap.score_tf_census", _tf_exc)

    tf = snap_timeframe(setup_class)
    if tf is None:
        base.update(compute(
            direction=dir_str, entry=entry, stop_loss=0.0, tp1=0.0,
            highs=None, lows=None, closes=None, tf="",
        ))
        base["refused"] = REFUSE_TF_UNKNOWN
        _counters.refuse(REFUSE_TF_UNKNOWN)
        _record(base)
        return base

    highs = lows = closes = None
    if candles is not None:
        highs = candles.get("high")
        lows = candles.get("low")
        closes = candles.get("close")

    row = compute(
        direction=dir_str,
        entry=entry,
        stop_loss=float(getattr(sig, "stop_loss", 0) or 0),
        tp1=float(getattr(sig, "tp1", 0) or 0),
        highs=highs, lows=lows, closes=closes, tf=tf,
    )
    base.update(row)
    if base["refused"]:
        _counters.refuse(str(base["refused"]))
        _record(base)
        return base

    if not base["apply_mode"]:
        _record(base)
        return base

    is_long = "LONG" in dir_str.upper()
    new_sl = float(base["sl_snapped"])
    new_tp1 = float(base["tp1_snapped"])

    # ── Apply: SL ────────────────────────────────────────────────────────
    sl_ok = (new_sl < entry) if is_long else (new_sl > entry)
    if not sl_ok:
        base["apply_refused"] = REFUSE_WRONG_SIDE
        _counters.refuse(REFUSE_WRONG_SIDE)
    elif abs(entry - new_sl) < float(min_sl_distance):
        base["apply_refused"] = REFUSE_MIN_DISTANCE
        _counters.refuse(REFUSE_MIN_DISTANCE)
    elif abs(new_sl - float(base["sl_arith"])) > 0:
        sig.stop_loss = round(new_sl, 8)
        # The R denominator moved, so restamp it here. #848 is the bill for a
        # ratio whose denominator changed after it was recorded: ops divides
        # pnl_pct by sl_distance_pct_at_entry, and leaving the arithmetic stop
        # in it would score every snapped trade against risk it never carried.
        new_dist = abs(entry - new_sl)
        sig.original_sl_distance = new_dist
        if entry > 0:
            sig.sl_distance_pct_at_entry = new_dist / entry * 100.0
        base["applied_sl"] = True
        _counters.applied_sl += 1

    # ── Apply: TP1 ───────────────────────────────────────────────────────
    # Only ever nearer, so it cannot cross entry or break ladder monotonicity
    # against an unchanged tp2/tp3 — but assert the side rather than assume it.
    tp1_ok = (new_tp1 > entry) if is_long else (new_tp1 < entry)
    if tp1_ok and abs(new_tp1 - float(base["tp1_arith"])) > 0:
        sig.tp1 = round(new_tp1, 8)
        base["applied_tp1"] = True
        _counters.applied_tp1 += 1

    _record(base)
    return base


def _record(row: Dict[str, Any]) -> None:
    if get_ledger().add(row):
        _counters.stamped += 1


_ledger: Optional[SnapLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> SnapLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = SnapLedger()
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[SnapLedger] = None) -> None:
    """Replace the ledger, and clear the re-detect state with it.

    The throttle belongs to the ledger's lifetime, not to the process's. A
    fresh ledger carrying stale `_last_stamp` entries would refuse to stamp
    setups the (empty) ledger has never seen — a silent, self-inflicted blind
    spot, and exactly the kind of leak that makes one test's state decide
    another's result.
    """
    global _ledger
    with _ledger_lock:
        _ledger = ledger
    reset_redetect_state()


def summary() -> Dict[str, Any]:
    """In-process state for the liveness probe and the truth report."""
    led = get_ledger()
    rows = led.rows()
    computed = [r for r in rows if not r.get("refused")]
    return {
        "rows": len(rows),
        "computed": len(computed),
        "refused": len(rows) - len(computed),
        "evicted": led.evicted,
        "duplicate_skips": led.duplicate_skips,
        "counters": _counters.as_dict(),
        "measure_enabled": measure_enabled(),
    }
