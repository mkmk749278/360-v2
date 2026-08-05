"""Retention by DELIVERY, not by recency.

Phase 6 of ``docs/PRICE_ACTION_PROGRAM.md``, and it exists because of an
arithmetic problem in every measurement ledger we have:

* the rings hold **4,000 rows** and evict oldest-first;
* they are filled by **enqueues**, of which roughly **0.5%** ever deliver;
* the delivered rows are the **only** population allowed to justify changing
  what a subscriber receives.

So the ring reaches capacity roughly **32 hours** after a deploy, and from that
moment every re-detection of a high-volume path evicts a row that might have
carried a verdict — preferentially destroying the rare, valuable population to
make room for the common, cheap one. Nothing about that is visible: the ledger
stays exactly 4,000 rows, the ops page keeps rendering, and the only symptom is
that the delivered sample quietly stops growing.

This is the same shape as the dark lane's row budget being consumed by the two
highest-volume paths, which "starves exactly the rare paths it exists to
measure" — one layer down, in the storage rather than the stamping.

The policy
----------
Two rings, not one.

* **pending** — every stamped row. Bounded, evicts oldest-first, and that
  eviction is *correct*: an enqueued candidate that never delivered is cheap
  evidence and there is always more of it.
* **delivered** — a row the **router confirmed**. A pending row can never evict
  one of these, which is the whole point.

Delivered rows are still bounded, because unbounded growth is a cost defect
whatever it is holding. But an eviction from *that* ring is a different event
with a different meaning — the retention policy itself is now losing verdicts —
so it is counted under its own name and never pooled with ordinary eviction. A
single ``evicted`` figure covering both would move with enqueue volume and say
nothing about the thing worth knowing.

Why a field on the row, and not state in the ring
--------------------------------------------------
``delivered`` is written **onto the row**, so it survives the JSON round trip
and the ring rebuilds its two halves from it on load. A serializer that drops a
field is invisible at both ends and nothing is missing while the process lives
(#842: ``open_time`` was added to the candle store and never written to the
snapshot, so bar timestamps did not survive a restart and every open dark row
read ``no candles``). Retention state kept only in the ring would have exactly
that defect: correct until the first restart, then silently back to
evict-by-recency with a full-looking ledger.

It also makes the fact readable. ``delivered`` on the row is a column ops can
render and an export can carry, rather than a property only the ring knows.

One policy, not one per lane
-----------------------------
``structural_snap`` and ``entry_features`` had **identical** rings — same cap,
same key, same eviction, same 0.5% delivery rate — and the program document
says the rule applies "to the Phase 5 lane from the start". Three copies of a
retention policy is three things to keep in sync, and the fix for a drifting
mirror is not a second mirror. A lane gets this by constructing one of these.
"""
from __future__ import annotations

import threading
import time
import weakref
from collections import deque
from typing import Any, Deque, Dict, Iterable, List, Optional

from src.utils import get_logger

log = get_logger("delivery_retention")

#: Field written onto a row once the router confirms delivery. Persisted with
#: the row deliberately — see the module docstring.
DELIVERED_KEY = "delivered"
DELIVERED_AT_KEY = "delivered_at"

#: Default caps. Pending matches what the lanes already used, so this change
#: does not silently alter how much cheap evidence they hold.
DEFAULT_MAX_PENDING = 4_000
#: The delivered feed runs ~16/day, so 2,000 rows is ~4 months. Bounded because
#: unbounded is a cost defect, generous because evicting one of these is the
#: event this module exists to prevent.
DEFAULT_MAX_DELIVERED = 2_000

#: Every live ring, so one router call can notify all of them without the
#: router importing each lane. Weak, so a ring built in a test does not outlive
#: it and start absorbing another test's promotions.
_RINGS: "weakref.WeakSet[DeliveryRetainedRing]" = weakref.WeakSet()


class DeliveryRetainedRing:
    """Rows evict by delivery, not by recency.

    Not a drop-in for ``deque(maxlen=…)`` and deliberately not shaped like one:
    ``add`` can evict a row that is not the oldest, which is the entire
    behaviour being bought.
    """

    def __init__(
        self,
        *,
        name: str,
        max_pending: int = DEFAULT_MAX_PENDING,
        max_delivered: int = DEFAULT_MAX_DELIVERED,
        id_key: str = "signal_id",
        time_key: str = "stamped_at",
    ) -> None:
        self.name = name
        self.id_key = id_key
        self.time_key = time_key
        self._pending: Deque[dict] = deque(maxlen=max_pending)
        self._delivered: Deque[dict] = deque(maxlen=max_delivered)
        self._by_id: Dict[str, dict] = {}
        self._lock = threading.RLock()

        # Counters, each naming a distinct event. Pooling any two of these
        # would produce a number that moves with enqueue volume rather than
        # with anything a reader wants to know.
        self.evicted_pending = 0
        self.evicted_delivered = 0
        self.duplicate_skips = 0
        #: A promotion arriving for an id the ring no longer holds. This is the
        #: measurement of whether `max_pending` is adequate: it can only happen
        #: when a row was evicted between its stamp and the router confirming
        #: delivery, which is precisely the harm this module prevents — so a
        #: non-zero value here means the pending cap is too small for the
        #: current enqueue rate, not that something is broken.
        self.promote_misses = 0
        self.promoted = 0
        #: Drained by `drain_evicted_ids`. Bounded by the drain, not by a cap:
        #: a lane that never drains would grow this forever, so the two lanes
        #: that keep their own index drain it on every add.
        self._evicted_ids: List[str] = []

        _RINGS.add(self)

    # ── writes ────────────────────────────────────────────────────────────
    def add(self, row: dict) -> bool:
        """Stamp a new row. ``False`` when the id is already held."""
        sid = str(row.get(self.id_key) or "")
        if not sid:
            return False
        with self._lock:
            if sid in self._by_id:
                self.duplicate_skips += 1
                return False
            evicted = (
                self._pending[0]
                if len(self._pending) == self._pending.maxlen
                else None
            )
            self._pending.append(row)
            self._by_id[sid] = row
            if evicted is not None:
                self.evicted_pending += 1
                lost_id = str(evicted.get(self.id_key) or "")
                self._by_id.pop(lost_id, None)
                if lost_id:
                    self._evicted_ids.append(lost_id)
            return True

    def mark_delivered(self, signal_id: str, *, now: Optional[float] = None) -> bool:
        """Promote a row after the router confirmed delivery.

        Idempotent: the router calls this once, but a re-delivery or a replayed
        event must not double-count or move the row twice.
        """
        sid = str(signal_id or "")
        if not sid:
            return False
        with self._lock:
            row = self._by_id.get(sid)
            if row is None:
                self.promote_misses += 1
                return False
            if row.get(DELIVERED_KEY):
                return True          # already promoted; not a miss, not a move
            row[DELIVERED_KEY] = True
            row[DELIVERED_AT_KEY] = float(now if now is not None else time.time())
            try:
                self._pending.remove(row)
            except ValueError:
                # Not in pending — it was restored straight into delivered, or
                # evicted between the lookup and here. Either way the row
                # object is the one the map holds, so the move below is still
                # correct.
                pass
            self._push_delivered(row)
            self.promoted += 1
            return True

    def restore(self, row: dict) -> bool:
        """Load path: route a row by the delivered flag it carries.

        The flag is on the row rather than in the ring precisely so this works
        — a restart must not silently revert the lane to evict-by-recency.
        """
        sid = str(row.get(self.id_key) or "")
        if not sid:
            return False
        with self._lock:
            if sid in self._by_id:
                return False
            if row.get(DELIVERED_KEY):
                self._by_id[sid] = row
                self._push_delivered(row)
                return True
        return self.add(row)

    def _push_delivered(self, row: dict) -> None:
        """Append to the delivered ring, counting an overflow under its own
        name. Caller holds the lock."""
        lost = (
            self._delivered[0]
            if len(self._delivered) == self._delivered.maxlen
            else None
        )
        self._delivered.append(row)
        if lost is not None:
            self.evicted_delivered += 1
            lost_id = str(lost.get(self.id_key) or "")
            self._by_id.pop(lost_id, None)
            if lost_id:
                self._evicted_ids.append(lost_id)
            # Loud, because this is the one eviction that destroys evidence
            # nothing else can regenerate: the candidate delivered, and only a
            # delivered candidate can justify changing what subscribers get.
            log.error(
                "{}: delivered-row ring is FULL ({}) — evicting a CONFIRMED "
                "row. The retention policy is now losing exactly the "
                "population it exists to keep. Raise max_delivered.",
                self.name, self._delivered.maxlen,
            )

    def note_duplicate(self) -> None:
        """Record a duplicate the CALLER rejected before reaching `add`.

        A lane that must run its own fault check before another guard (so the
        fault is not filed under the guard's expected-condition bucket) still
        needs the count to land in one place. Without this the caller reaches
        into the counter directly and the two drift.
        """
        with self._lock:
            self.duplicate_skips += 1

    def drain_evicted_ids(self) -> List[str]:
        """Ids evicted since the last call, so a caller keeping its own index
        can stay in step.

        Drained rather than exposed as a growing list: a lane that never reads
        it would otherwise accumulate every id the ring ever dropped, which is
        the unbounded growth this module is supposed to be preventing.
        """
        with self._lock:
            out = self._evicted_ids
            self._evicted_ids = []
            return out

    # ── reads ─────────────────────────────────────────────────────────────
    def row_for(self, signal_id: str) -> Optional[dict]:
        with self._lock:
            return self._by_id.get(str(signal_id or ""))

    def __contains__(self, signal_id: object) -> bool:
        with self._lock:
            return str(signal_id or "") in self._by_id

    def __len__(self) -> int:
        with self._lock:
            return len(self._pending) + len(self._delivered)

    def rows(self) -> List[dict]:
        """Every held row, oldest first.

        Sorted on the row's own timestamp when every row carries one, so a
        consumer sees one chronological ledger rather than two rings bolted
        together. Falls back to delivered-then-pending rather than to an
        arbitrary order, because a partial sort would reorder some rows and not
        others and read as corruption.
        """
        with self._lock:
            merged = list(self._delivered) + list(self._pending)
        if self.time_key and all(
            isinstance(r.get(self.time_key), (int, float)) for r in merged
        ):
            merged.sort(key=lambda r: float(r.get(self.time_key) or 0.0))
        return merged

    def delivered_rows(self) -> List[dict]:
        with self._lock:
            return list(self._delivered)

    def stats(self) -> Dict[str, Any]:
        """Every count with its own name and its own denominator."""
        with self._lock:
            n_pending = len(self._pending)
            n_delivered = len(self._delivered)
            return {
                "name": self.name,
                "n_pending": n_pending,
                "n_delivered": n_delivered,
                "max_pending": self._pending.maxlen,
                "max_delivered": self._delivered.maxlen,
                "pending_full": n_pending == self._pending.maxlen,
                "delivered_full": n_delivered == self._delivered.maxlen,
                # Ordinary and expected — cheap evidence rotating out.
                "evicted_pending": self.evicted_pending,
                # NOT ordinary. Named apart because the fixes differ and one of
                # them is "this lane is losing verdicts right now".
                "evicted_delivered": self.evicted_delivered,
                "promoted": self.promoted,
                # Non-zero means a row was evicted between its stamp and the
                # router confirming delivery — i.e. max_pending is too small
                # for the current enqueue rate.
                "promote_misses": self.promote_misses,
                "duplicate_skips": self.duplicate_skips,
            }


def mark_delivered(signal_id: str, *, now: Optional[float] = None) -> int:
    """Promote ``signal_id`` in every live lane. Returns how many promoted.

    Called from the router at the confirmed-delivery point — the same place
    that already writes ``PROVENANCE_EMITTED``, and for the same reason: enqueue
    is not delivery, and only the router knows the difference.

    A return of 0 is **not** an error. A lane may legitimately not hold the row
    (its gate never stamped this candidate); each ring counts its own misses,
    which is where "the cap is too small" would show up.
    """
    sid = str(signal_id or "")
    if not sid:
        return 0
    n = 0
    for ring in list(_RINGS):
        try:
            if ring.mark_delivered(sid, now=now):
                n += 1
        except Exception as exc:  # noqa: BLE001
            from src import fail_open
            fail_open.record(f"delivery_retention.mark_delivered:{ring.name}", exc)
    return n


def all_stats() -> List[Dict[str, Any]]:
    """Every live ring's counters, for the ops surface."""
    out: List[Dict[str, Any]] = []
    for ring in list(_RINGS):
        try:
            out.append(ring.stats())
        except Exception:  # noqa: BLE001
            continue
    out.sort(key=lambda s: str(s.get("name") or ""))
    return out


def _registered_names() -> Iterable[str]:
    """Test/diagnostic helper."""
    return sorted(r.name for r in list(_RINGS))
