"""Every governed exit that has actually happened, kept across restarts.

Owner, 2026-08-11: *"also keep traded history Trail governor (LIVE) tab not only
opened positions"*.

`/signals/trail-governor` renders the positions the governor is holding **right
now**, which is the whole book on a quiet day and nothing at all on most of them.
#916 added a realized-exit ring so the page could finally say what the canary
earned — and that ring lives in `trail_governor._health`, which means it is
**in memory, capped at 40, and destroyed by every deploy**. On a mechanism that
re-deploys several times a session, "history" written that way is a list of the
last few minutes.

This module is the record. It is deliberately **not** a measurement lane.

What that distinction changes
-----------------------------
Every other ledger in this repo stamps a *counterfactual* — where a stop would
have been, what a rule would have dropped — and can be re-derived by waiting for
a fresh window. These rows are **real fills on a real account**. They cannot be
re-derived at all: the position is closed, the bars have moved on, and nothing
in the engine will ever produce that fill again. A destroyed measurement window
is recoverable by waiting; a destroyed trade record is gone.

Three consequences, each a rule this repo already carries arriving at a record
rather than at a measurement:

* **There is no measure switch.** `measure_enabled()` is unconditionally True.
  Gating it on `TRAIL_GOVERNOR_ENABLED` would mean that turning the governor off
  — the *first* thing anyone does when a mechanism misbehaves — silently stops
  persisting the exits that explain why. A record of money has no off switch.
* **The cap is large and its eviction count is published.** A bounded buffer
  feeding a statistic must persist the eviction count with the data, or a
  reader in another process sees a sample and reads it as the population. At
  ~5 governed exits a day this holds years; `evicted` says so rather than
  implying it.
* **Nothing here is ever reconstructed.** `/track-record`'s rule — a
  reconstructed number wearing a recorded one's name is the most dangerous
  artifact this system can produce — applies with full force, because this is
  the surface an adoption decision for a live money mechanism reads.

Why `src/` and not `src/execution/`
------------------------------------
`tests/test_ledger_flush_wiring.py` derives its requirements by globbing
`src/*.py` for a module exposing `get_ledger()` whose ledger defines `flush` —
so a ledger written beside its producer in `src/execution/` gets **none** of the
guards that exist precisely because this repo has shipped flush-without-load,
load-without-caller and an additive bump that erased its own window. Putting it
where the checks can see it is not tidiness; it is the difference between being
covered by them and quietly opting out.
"""
from __future__ import annotations

import json
import os
import threading
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional

from src import fail_open, ledger_schema
from src.utils import get_logger

log = get_logger(__name__)

#: 1 (2026-08-11) — realized governed exits: one row per closed governed
#: position, carrying which fill closed it and at what price.
SCHEMA = 1

#: Which older schemas this build reads unchanged.  Required by
#: `ledger_schema.accepts`, and empty is a valid answer somebody chose: there is
#: no older schema, because this is the first.  A future ADDITIVE bump adds its
#: predecessor here — omitting it silently destroys the window on deploy, which
#: is exactly what #904 cost.
ADDITIVE_FROM_SCHEMAS: frozenset = frozenset()

_DEFAULT_PATH = os.path.join("data", "trail_exits_v1.json")

#: Years of history at the canary's rate, and small on disk — a row is ~250
#: bytes, so the cap is well under a megabyte.  Bounded anyway, because an
#: unbounded file read by an ops page every request is the hot-path shape the
#: cost rules forbid.
_MAX_ROWS = 5000

#: The two fills, never pooled.  Their difference is the cost of confirmation
#: and it is the single number the mechanism's design turns on, so a blended
#: average is not offered here any more than it is on `/signals/sar-live`.
FILL_TRAIL_STOP = "trail_stop"   # the parked level was touched  (@level)
FILL_FLIP_CLOSE = "flip_close"   # the mechanism came offside    (@confirm)


class TrailExitLedger:
    """Closed governed positions, newest last."""

    def __init__(self, path: Optional[str] = None, max_rows: Optional[int] = None) -> None:
        self._path = _DEFAULT_PATH if path is None else path
        self._max = int(max_rows or _MAX_ROWS)
        self._rows: Deque[dict] = deque(maxlen=self._max)
        self._evicted = 0
        self._lock = threading.RLock()
        self._dirty = False

    def add(self, row: dict) -> bool:
        """Record one realized exit.

        Deduplicated on ``(signal_id, uid, seq, exit_kind)``: the same fill can
        arrive twice — the FSM books it from the user-data stream while the
        sweep's own `-2022` branch books it when it finds the book already flat
        — and those are one exit seen by two observers, not two trades.  Counted
        as a duplicate rather than dropped silently, because a rising duplicate
        count means the two paths are racing more often than expected.
        """
        if not isinstance(row, dict):
            return False
        key = self._key(row)
        with self._lock:
            for existing in reversed(self._rows):
                if self._key(existing) == key:
                    return False
            if len(self._rows) == self._max:
                self._evicted += 1
            self._rows.append(dict(row))
            self._dirty = True
        return True

    @staticmethod
    def _key(row: dict) -> tuple:
        return (
            str(row.get("signal_id") or ""),
            str(row.get("uid") or ""),
            int(row.get("seq") or 0),
            str(row.get("exit_kind") or ""),
        )

    def rows(self) -> List[dict]:
        with self._lock:
            return [dict(r) for r in self._rows]

    def recent(self, n: int) -> List[dict]:
        """The newest ``n``, newest LAST — the ring's own order, so a caller
        that reverses for display does it once and visibly."""
        with self._lock:
            return [dict(r) for r in list(self._rows)[-int(n):]]

    def stats(self) -> Dict[str, Any]:
        """Held, evicted and the cap — published together.

        A verdict computed on a capped buffer is a verdict on a sample, and a
        reader in another process cannot see the cap.  `evicted` is the
        difference between "this is the book" and "this is the newest 5,000 of
        it", which are different claims.
        """
        with self._lock:
            return {
                "rows": len(self._rows),
                "evicted": self._evicted,
                "max_rows": self._max,
                "complete": self._evicted == 0,
            }

    def load(self) -> None:
        """Read the record back at boot.

        Flush without load is worse than neither: the ring starts empty and the
        first flush after the deploy **overwrites** the file with whatever has
        accumulated since. That destroyed the structural ledgers four times in
        an afternoon while their panels read "nothing evicted" — nothing was;
        the window had been erased rather than rotated. On a measurement lane
        that costs a window. Here it would cost the trade record itself, which
        nothing can regenerate.
        """
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            ok, why = ledger_schema.accepts(
                payload.get("schema"), SCHEMA, ADDITIVE_FROM_SCHEMAS
            )
            if not ok:
                log.warning(
                    "trail_history: refusing stored ledger schema={} ({}) — "
                    "starting fresh, and the previous file is NOT overwritten "
                    "until the next flush",
                    payload.get("schema"), why,
                )
                return
            with self._lock:
                for row in payload.get("rows") or []:
                    if isinstance(row, dict) and row.get("signal_id"):
                        self._rows.append(dict(row))
                self._evicted = int(payload.get("evicted") or 0)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("trail_history.load", exc)

    def flush(self, force: bool = False) -> bool:
        """Persist. ``force`` writes even when unchanged — an idle governor must
        still prove the writer is alive, and a heartbeat that only fires on
        change is not a heartbeat."""
        with self._lock:
            if not (self._dirty or force):
                return False
            # ``path=""`` is in-memory, which is what every test constructs
            # with. Return BEFORE the side effect: a no-op that touches the disk
            # wrote stray .tmp files into the repo root for two months and
            # raised a non-failure into fail_open on every test run.
            if not self._path:
                self._dirty = False
                return False
            self._dirty = False
            rows = [dict(r) for r in self._rows]
            stats = {
                "rows": len(self._rows),
                "evicted": self._evicted,
                "max_rows": self._max,
            }
        payload = {
            "schema": SCHEMA,
            "written_at": time.time(),
            "evicted": stats["evicted"],
            "max_rows": stats["max_rows"],
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
            fail_open.record("trail_history.flush", exc)
            return False


_ledger: Optional[TrailExitLedger] = None
_ledger_lock = threading.Lock()


def measure_enabled() -> bool:
    """Always True, and that is the point.

    The maintenance loop gates every ledger flush on a `measure_enabled()`, and
    every other lane wires that to its own measurement switch. This one is a
    **record of real fills**, so gating it on `TRAIL_GOVERNOR_ENABLED` would
    stop persisting exits the moment somebody switches the governor off — which
    is the first thing anyone does when a live mechanism misbehaves, i.e.
    exactly when the last few exits are the evidence.

    Kept as a function rather than removed so the derived wiring guard still
    recognises this module as a lane it must find a flush caller for.
    """
    return True


def get_ledger() -> TrailExitLedger:
    global _ledger
    if _ledger is None:
        with _ledger_lock:
            if _ledger is None:
                _ledger = TrailExitLedger()
                # Defining `load` is not calling it — pin the call site, not
                # the method. The structural ledgers each had one and neither
                # ran.
                _ledger.load()
    return _ledger


def reset_ledger(ledger: Optional[TrailExitLedger] = None) -> None:
    """Test hook. Never called in production."""
    global _ledger
    _ledger = ledger


def record(row: dict) -> bool:
    """Append one realized governed exit. Fail-open, but counted."""
    try:
        return get_ledger().add(row)
    except Exception as exc:  # noqa: BLE001
        fail_open.record("trail_history.record", exc)
        return False


def summary(rows: Optional[List[dict]] = None) -> Dict[str, Any]:
    """Per-fill totals over the record — never a blended figure.

    The two fills are reported side by side and there is deliberately no pooled
    average, exactly as on `/signals/sar-live`: their difference *is* the cost
    of confirmation, and collapsing them before it is known picks the answer.

    A row whose fill price never arrived carries ``pnl_pct = None`` and is
    counted in ``unpriced`` rather than averaged as a flat trade. `None` and
    `0.0` are different facts and a zero here is a claim.
    """
    src = get_ledger().rows() if rows is None else list(rows)
    out: Dict[str, Any] = {"n": len(src), "unpriced": 0, "by_fill": {}}
    buckets: Dict[str, List[float]] = {}
    for r in src:
        kind = str(r.get("exit_kind") or "unknown")
        pnl = r.get("pnl_pct")
        if pnl is None:
            out["unpriced"] += 1
            buckets.setdefault(kind, [])
            continue
        try:
            buckets.setdefault(kind, []).append(float(pnl))
        except (TypeError, ValueError):
            out["unpriced"] += 1
    for kind, vals in sorted(buckets.items()):
        n = len(vals)
        out["by_fill"][kind] = {
            "n": n,
            "wins": sum(1 for v in vals if v > 0),
            "avg_pnl_pct": (sum(vals) / n) if n else None,
            "total_pnl_pct": sum(vals) if n else None,
            "best_pnl_pct": max(vals) if n else None,
            "worst_pnl_pct": min(vals) if n else None,
        }
    return out
