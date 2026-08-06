"""Structural veto — do not take a signal straight into a level.

Phase 4 of ``docs/PRICE_ACTION_PROGRAM.md``, and the application with leverage.

Why this one first
------------------
§5 of the program lists six places price action can apply and finds we use it
at one and a half. Application 2 — structure *generates* the signal — is the one
everybody reaches for, and it is **0.62%** of the enqueued book: 15 rows in the
2026-08-05 window, **zero of them delivered**. It takes weeks to reach a sample
worth reading, with the 54-variant null result hanging over it.

Application 6 — the **veto** — needs no new signal, no new delivery surface and
no user-visible change, and it can be measured against **97% of the book from
the day it ships**. It answers "does structure carry information on this book"
in days, and that answer is a precondition for application 2 being worth
building at all. A negative answer is a successful outcome of this phase.

The mechanism, and the features that follow from it
----------------------------------------------------
The claim being tested is narrow: **a signal fired into an opposing level is
worse than the same signal with clear air ahead.** ~82% of the enqueued book is
MA/indicator-triggered, and none of those triggers consults a level — an MA
crossing says nothing about whether the next 0.4% of price is empty or is a
1d resistance that has held four times.

So the features are what that mechanism turns on, and nothing else. A path
stamping twelve features invites twelve thresholds, and twelve cells against a
book this size guarantees a spurious winner:

* ``opposing_dist_atr`` / ``opposing_dist_pct`` — entry to the nearest opposing
  level. Both units, because ATR normalises across symbols while percent is what
  the money reads, and #855 is the standing lesson about trusting one normaliser.
* ``opposing_inside_tp1`` — is that level **between entry and TP1**? This is the
  sharpest form of the question and the only one that needs no threshold at all:
  the target cannot be reached without breaking the level. It is a structural
  contradiction, not a tuned cutoff.
* ``opposing_score`` — the LevelBook's own score for it. A level touched four
  times on the daily and a round number nobody has tested are not the same
  obstacle, and treating them alike is how a real effect gets averaged into noise.
* ``opposing_age_s`` — how long since it was last tested. A level swept minutes
  ago has had its liquidity taken and is *weaker*; the naive reading has this
  backwards, which is exactly the kind of sign error the CVD lane already paid
  for.
* ``value_area_pos`` — inside value is rotational, outside is trending, and
  "long at VAH" and "long inside value" are different trades. Auction-theory
  context for a trigger that has none.

"Opposing" is signed toward the trade throughout: resistance **above** entry for
a long, support **below** entry for a short. A feature that is not signed toward
the trade scores half the book backwards, and the delivered book is ~50/50 by
side, so the error would not show as an empty column — it would just make the
feature look like noise.

No resolver
-----------
None, deliberately. Rows are keyed by ``signal_id`` and joined to
``signal_performance.json``, which ``trade_monitor`` already writes at the
terminal transition. Every arm in this repo that grew its own forward-resolution
machinery cost a session; this one inherits a correct outcome instead of
re-deriving one, including #848's denominator.

Retention is Phase 6's shared ring, so a delivered row can never be evicted by
the flood of undelivered ones. A lane gets that by constructing one.

What ships enforcing, and what does not
----------------------------------------
The gate is real, wired into the post-scoring chain and suppression-stamped —
no scaffolds. It enforces **exactly one** rule, and only when the owner turns it
on:

``target_behind_level`` — TP1 sits beyond an opposing level.

That rule is chosen because **its threshold comes from no window**: it is not "a
level within 0.4 ATR", it is "the target is unreachable without breaking a
level", which is arithmetic on values the signal already carries. Every
*distance* rule — "veto when the level is closer than N ATR" — needs an N, and N
can only come from this window, which is the thing §2 warns about and the thing
`tpe_smc_zone` was retired for. Those ship as stamps and their thresholds get
picked from the distribution on the ops page, not here.

Enforcement is off by default and gated per setup class, the same shape as
``structural_snap``: one flip must not move nineteen paths on evidence from the
one that is most of the book.
"""
from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src import fail_open
from src.delivery_retention import DeliveryRetainedRing
from src.utils import get_logger

log = get_logger("structural_veto")

SCHEMA = 1
_DEFAULT_PATH = os.path.join("data", "structural_veto_v1.json")
_MAX_ROWS = 4000

# ── Refusal reasons ─────────────────────────────────────────────────────────
# Each is its own state, never pooled into "no data": the reader's next move
# differs for each, and a pooled bucket reports a fault that is not happening.
REFUSE_NO_GEOMETRY = "no_geometry"      # entry/tp1 unusable
REFUSE_NO_LEVELS = "no_levels"          # LevelBook empty or absent for the symbol
REFUSE_NO_OPPOSING = "no_opposing"      # book has levels, none ahead of the trade
REFUSE_NO_ATR = "no_atr"                # ATR column only; pct still computed
REFUSE_NO_VALUE_AREA = "no_value_area"  # volume profile absent for the symbol

#: Keys that describe the row rather than measure the setup. Named explicitly so
#: that where a line sits in a function can never reclassify a feature — the
#: `stack_sep_pct` lesson.
ROW_METADATA_KEYS = frozenset({
    "signal_id", "symbol", "side", "setup_class", "stamped_at",
    "entry", "tp1", "sl_dist_pct", "atr",
    "opposing_price", "opposing_type", "opposing_source_tf",
    "levels_seen", "refusals", "veto_mode", "veto_would_reject",
    "delivered", "delivered_at",
})


@dataclass
class VetoCounters:
    """In-process counters. Read from a counter the engine increments — never
    from a tunable lookup in a side process, which returns the boot default and
    has already misled one diagnosis (2026-08-02)."""

    evaluated: int = 0
    stamped: int = 0
    would_reject: int = 0
    enforced_reject: int = 0
    refused_no_levels: int = 0
    refused_no_opposing: int = 0
    refused_no_geometry: int = 0
    refused_no_value_area: int = 0

    def as_dict(self) -> Dict[str, int]:
        return dict(self.__dict__)


_counters = VetoCounters()


def counters() -> Dict[str, int]:
    return _counters.as_dict()


def _f(v: Any) -> Optional[float]:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f and abs(f) != float("inf") else None


def nearest_opposing(
    levels: Any,
    entry: float,
    is_long: bool,
) -> Tuple[Optional[Any], int]:
    """The nearest level *ahead of the trade*, and how many levels were readable.

    Signed toward the trade: resistance above entry for a long, support below
    for a short. A level behind the entry is not an obstacle and is skipped.

    ``levels`` is ``LevelBook.get_levels`` output — ``Level`` dataclasses with
    ``price`` / ``type``. Those fields are read **by name off the real
    producer**, not guessed across a set of plausible shapes: a flexible reader
    that accepts several shapes cannot fail loudly, because skipping an
    unreadable level is indistinguishable from having no levels. That is exactly
    how ``zone_distance_atr`` returned ``None`` on 57 of 57 rows for its whole
    life while its tests passed on a shape nothing had ever produced.

    The mapping branch exists only for the ledger's own JSON round trip.
    """
    want = "resistance" if is_long else "support"
    best = None
    best_gap: Optional[float] = None
    readable = 0
    for lvl in levels or []:
        if isinstance(lvl, dict):
            price = _f(lvl.get("price"))
            ltype = str(lvl.get("type") or "")
        else:
            price = _f(getattr(lvl, "price", None))
            ltype = str(getattr(lvl, "type", "") or "")
        if price is None or price <= 0:
            continue
        readable += 1
        if ltype != want:
            continue
        gap = (price - entry) if is_long else (entry - price)
        if gap <= 0:
            continue                       # behind us: not an obstacle
        if best_gap is None or gap < best_gap:
            best, best_gap = lvl, gap
    return best, readable


def _attr(lvl: Any, name: str, default: Any = None) -> Any:
    if isinstance(lvl, dict):
        return lvl.get(name, default)
    return getattr(lvl, name, default)


def build_row(
    *,
    signal_id: str,
    symbol: str,
    side: str,
    setup_class: str,
    entry: Optional[float],
    tp1: Optional[float],
    sl_dist_pct: Optional[float],
    atr: Optional[float],
    levels: Any,
    value_area: Any = None,
    now_ts: Optional[float] = None,
) -> Dict[str, Any]:
    """One candidate's structural context. Pure — no I/O, mutates nothing.

    Every feature degrades to ``None`` with a **named** reason rather than to a
    zero. A missing level book is not a clear path, and rendering it as one is
    the class of error that makes a broken measurement look like agreement.
    """
    now = float(now_ts if now_ts is not None else time.time())
    is_long = str(side or "").upper() in ("LONG", "BUY")
    refusals: List[str] = []

    e = _f(entry)
    t = _f(tp1)
    a = _f(atr)

    row: Dict[str, Any] = {
        "signal_id": str(signal_id or ""),
        "symbol": str(symbol or ""),
        "side": "LONG" if is_long else "SHORT",
        "setup_class": str(setup_class or ""),
        "stamped_at": now,
        "entry": e,
        "tp1": t,
        "sl_dist_pct": _f(sl_dist_pct),
        "atr": a,
        # Features
        "opposing_dist_atr": None,
        "opposing_dist_pct": None,
        "opposing_inside_tp1": None,
        "opposing_score": None,
        "opposing_age_s": None,
        "value_area_pos": None,
        # Provenance of the level itself — a 1d swing and an untested round
        # number are different obstacles and the column says which.
        "opposing_price": None,
        "opposing_type": None,
        "opposing_source_tf": None,
        "levels_seen": 0,
        "refusals": refusals,
    }

    if e is None or e <= 0:
        refusals.append(REFUSE_NO_GEOMETRY)
        _counters.refused_no_geometry += 1
        return row

    lvl, readable = nearest_opposing(levels, e, is_long)
    row["levels_seen"] = readable
    if readable == 0:
        # Absent and empty are indistinguishable through `dict.get`, which is
        # precisely why `level_book_levels` went missing for four evaluators
        # without anything being able to observe it. Named here.
        refusals.append(REFUSE_NO_LEVELS)
        _counters.refused_no_levels += 1
    elif lvl is None:
        # The book is populated and nothing sits ahead of the trade. That is a
        # *finding* — clear air — not a data fault, and pooling it with an empty
        # book would report a fault that is not happening.
        refusals.append(REFUSE_NO_OPPOSING)
        _counters.refused_no_opposing += 1

    if lvl is not None:
        price = _f(_attr(lvl, "price"))
        gap = abs(price - e) if price is not None else None
        row["opposing_price"] = price
        row["opposing_type"] = str(_attr(lvl, "type", "") or "")
        row["opposing_source_tf"] = str(_attr(lvl, "source_tf", "") or "")
        row["opposing_score"] = _f(_attr(lvl, "score"))
        if gap is not None:
            row["opposing_dist_pct"] = gap / e * 100.0
            if a is not None and a > 0:
                row["opposing_dist_atr"] = gap / a
            else:
                refusals.append(REFUSE_NO_ATR)
        # The sharpest question, and the only one needing no threshold: is the
        # target unreachable without breaking this level?
        if t is not None and price is not None:
            row["opposing_inside_tp1"] = bool(
                (e < price < t) if is_long else (t < price < e)
            )
        last_test = _f(_attr(lvl, "last_test_ts"))
        if last_test is not None and last_test > 0:
            # Recency, not "freshness". A level tested minutes ago has had its
            # liquidity taken and is WEAKER — the naive reading has this
            # backwards, and an unsigned directional feature is how the CVD
            # column spent a schema looking like noise.
            row["opposing_age_s"] = max(0.0, now - last_test)

    va = _value_area_pos(value_area, e)
    if va is None:
        refusals.append(REFUSE_NO_VALUE_AREA)
        _counters.refused_no_value_area += 1
    else:
        row["value_area_pos"] = va

    return row


def _value_area_pos(value_area: Any, price: float) -> Optional[str]:
    """``"inside"`` / ``"above"`` / ``"below"``, or ``None`` with no guess.

    Reads ``vah`` / ``val`` off the real ``VolumeProfileResult`` by name.
    """
    if value_area is None:
        return None
    vah = _f(_attr(value_area, "vah"))
    val = _f(_attr(value_area, "val"))
    if vah is None or val is None or vah <= 0 or val <= 0 or val > vah:
        return None
    if price > vah:
        return "above"
    if price < val:
        return "below"
    return "inside"


# ── The rule ────────────────────────────────────────────────────────────────

def would_reject(row: Dict[str, Any]) -> bool:
    """``target_behind_level`` — TP1 sits beyond an opposing level.

    The **only** enforcing rule, and it is chosen because its threshold comes
    from nowhere: this is not "closer than N ATR", it is "the target cannot be
    reached without breaking a level", which is arithmetic on values the signal
    already carries. Every distance rule needs an N, and an N taken from the
    window it is evaluated on is the thing §2 of the program warns about and the
    thing `tpe_smc_zone` was retired for the same day it shipped.

    Fail-open on unknown: ``None`` abstains. The input is a measurement lane, and
    a fail-closed rule here would kill the feed the moment the LevelBook went
    dark — indistinguishable from a quiet market. The cost is that an inert rule
    reads exactly like a working one, which is why `unknown` is its own bucket
    on the panel and the liveness probe fails on total blindness.
    """
    return row.get("opposing_inside_tp1") is True


def enforcing_for(setup_class: str) -> bool:
    """Is the veto enforcing for this setup?

    Gated per setup class for the same reason ``structural_snap`` is: one flip
    must not move nineteen paths on evidence from the one that is 59% of the
    book. An empty allow-list means enforcing nowhere, which is what "off"
    means even if the master switch is flipped.
    """
    try:
        from config import STRUCTURAL_VETO_ENFORCE, STRUCTURAL_VETO_ENFORCE_PATHS
    except Exception:  # noqa: BLE001
        return False
    if not STRUCTURAL_VETO_ENFORCE:
        return False
    allow = {
        s.strip().upper()
        for s in str(STRUCTURAL_VETO_ENFORCE_PATHS or "").split(",")
        if s.strip()
    }
    return bool(allow) and str(setup_class or "").upper() in allow


# ── Ledger ──────────────────────────────────────────────────────────────────

class VetoLedger:
    """Rows keyed by ``signal_id``, retained by delivery (Phase 6)."""

    def __init__(self, path: Optional[str] = None, max_rows: Optional[int] = None) -> None:
        self._path = _DEFAULT_PATH if path is None else path
        self._ring = DeliveryRetainedRing(
            name="structural_veto", max_pending=max_rows or _MAX_ROWS,
        )
        self._lock = threading.RLock()
        self._dirty = False

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
            if int(payload.get("schema") or 0) != SCHEMA:
                log.info(
                    "{}: ledger schema {} != {}, starting fresh",
                    "structural_veto", payload.get("schema"), SCHEMA,
                )
                return
            with self._lock:
                for row in payload.get("rows") or []:
                    if str(row.get("signal_id") or ""):
                        self._ring.restore(row)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("structural_veto.load", exc)

    def mark_delivered(self, signal_id: str) -> bool:
        if self._ring.mark_delivered(signal_id):
            with self._lock:
                self._dirty = True
            return True
        return False

    def rows(self) -> List[dict]:
        return self._ring.rows()

    def retention(self) -> Dict[str, Any]:
        return self._ring.stats()

    def flush(self, force: bool = False) -> bool:
        """Persist. ``force`` writes even when unchanged — an idle lane must
        still prove it is alive, and a heartbeat that only fires on change is
        not a heartbeat."""
        with self._lock:
            if not (self._dirty or force):
                return False
            # ``path=""`` means in-memory (what tests construct with). Return
            # BEFORE the side effect: a no-op that touches the disk wrote stray
            # .tmp files into the repo root for two months and raised a
            # non-failure into fail_open on every test run.
            if not self._path:
                self._dirty = False
                return False
            self._dirty = False
        rows = self._ring.rows()
        ret = self._ring.stats()
        payload = {
            "schema": SCHEMA,
            "written_at": time.time(),
            "counters": counters(),
            # The ring is capped, so every rate computed on it is a sample.
            # Persisted WITH the data: a reader in another process cannot see
            # the cap, and a verdict without its denominator reads as if it
            # covered everything.
            "retention": ret,
            "rows": rows,
        }
        try:
            tmp = f"{self._path}.tmp"
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:  # noqa: BLE001
            fail_open.record("structural_veto.flush", exc)
            return False


_ledger: Optional[VetoLedger] = None
_ledger_lock = threading.Lock()


def measure_enabled() -> bool:
    """Whether the lane is stamping. Mirrors `structural_snap.measure_enabled`
    because the maintenance loop gates every ledger flush on one — and this
    module not having one is how it got left out of that loop entirely."""
    try:
        from config import STRUCTURAL_VETO_MEASURE
        return bool(STRUCTURAL_VETO_MEASURE)
    except Exception:  # noqa: BLE001
        return False


def get_ledger() -> VetoLedger:
    global _ledger
    if _ledger is None:
        with _ledger_lock:
            if _ledger is None:
                _ledger = VetoLedger()
                _ledger.load()
    return _ledger


def reset_ledger() -> None:
    """Test hook. Never called in production."""
    global _ledger
    _ledger = None


# ── The seam ────────────────────────────────────────────────────────────────

def stamp(
    sig: Any,
    *,
    levels: Any,
    value_area: Any = None,
    now_ts: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """Stamp one candidate and return its row. Returns ``None`` if unusable.

    Called from ``_enqueue_signal`` **after** the min-distance clamp, because
    that is where the geometry becomes true: between the evaluator and the queue
    ``sig.tp1`` is rewritten by the noise-floor widener, ``adjust_tp_sl``, the
    clamp, and the clamp's proportional TP rescale. ``opposing_inside_tp1``
    measured any earlier describes a target that is not the target.
    """
    _counters.evaluated += 1
    try:
        from config import STRUCTURAL_VETO_MEASURE
        if not STRUCTURAL_VETO_MEASURE:
            return None
        sid = str(getattr(sig, "signal_id", "") or "")
        if not sid:
            return None
        setup = str(
            getattr(sig, "setup_class", "") or getattr(sig, "channel", "") or ""
        )
        direction = getattr(sig, "direction", None)
        side = str(getattr(direction, "value", direction) or "")
        entry = _f(getattr(sig, "entry", None))
        sl = _f(getattr(sig, "stop_loss", None))
        sl_pct = (
            abs(entry - sl) / entry * 100.0
            if entry and sl and entry > 0 else None
        )
        row = build_row(
            signal_id=sid,
            symbol=str(getattr(sig, "symbol", "") or ""),
            side=side,
            setup_class=setup,
            entry=entry,
            tp1=_f(getattr(sig, "tp1", None)),
            sl_dist_pct=sl_pct,
            atr=_f(getattr(sig, "atr_val", None)),
            levels=levels,
            value_area=value_area,
            now_ts=now_ts,
        )
        reject = would_reject(row)
        enforcing = enforcing_for(setup)
        row["veto_would_reject"] = reject
        # Read off the row, never mirrored from a copy of the flag registry.
        row["veto_mode"] = "enforce" if enforcing else "measure"
        if reject:
            _counters.would_reject += 1
        get_ledger().add(row)
        _counters.stamped += 1
        return row
    except Exception as exc:  # noqa: BLE001
        fail_open.record("structural_veto.stamp", exc)
        return None


def should_suppress(row: Optional[Dict[str, Any]]) -> bool:
    """Does the enforcing veto reject this candidate?

    Separate from :func:`stamp` so the measurement cannot be skipped by the
    gate short-circuiting, and so the gate's decision reads off the row the
    ledger holds rather than recomputing it — two computations of one quantity
    that can disagree is how a panel and a gate end up describing different
    books.
    """
    if not row:
        return False
    if row.get("veto_mode") != "enforce":
        return False
    if not row.get("veto_would_reject"):
        return False
    _counters.enforced_reject += 1
    return True
