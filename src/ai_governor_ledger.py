"""Every verdict the governor issued, including the ones that changed nothing.

`docs/PLAN_AI_TRADE_GOVERNOR.md` §10. This ledger is what an adoption decision
reads over the months §11.1 says the shadow window takes, so it is built around
the four defects that cost this repo a session each:

* **`load()` exists and `get_ledger()` calls it.** Flush without load is worse
  than neither: it *deletes* the window on every deploy while the page reports a
  healthy ledger. Two structural lanes shipped without one and erased four
  windows before anyone noticed the row count going down.
* **`flush(force=True)` has a real caller.** A heartbeat that only fires on
  change is not a heartbeat — an idle lane stops writing and ops renders STALE,
  a fault that is not happening.
* **The schema gate goes through `ledger_schema.accepts`**, which takes the
  additive set as a *required* argument. A bare `!=` overwrote 371 SAR rows on
  the day the rule was written down.
* **`path=""` returns BEFORE the side effect.** Both structural ledgers took it
  to mean "in memory" and ran their atomic write anyway, which created `.tmp`
  files in the repo root under pytest and raised into `fail_open` on every test
  run for two months — filling the counter whose whole purpose is making a real
  failure stand out.

MAINTAIN rows are recorded
--------------------------
A lane that logs only its interventions cannot compute a baseline and will look
brilliant. Every verdict lands here, and the ops page reads the mix.

There is deliberately no combined figure
----------------------------------------
Three of the four arms are decidable from the closed-signal record and one is
not (§8): a *wider* stop on a loser asks whether price would have come back and
the walk ended at the stop; a *tighter* stop on a winner asks whether MAE
preceded TP1, and MFE/MAE carry no ordering between them. Those remove opposite
ends of the distribution, so one number over all four arms would move with the
SL arm's refusal rate rather than with the mechanism. `tests/` asserts no such
key exists.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

from src import fail_open, ledger_schema
from src.utils import get_logger

log = get_logger("ai_governor_ledger")

SCHEMA = 1

#: Older schemas this build reads unchanged. Empty because there are none yet —
#: stated out loud rather than defaulted, so the next bump has to decide.
#: Before bumping SCHEMA, ask whether the change only ADDS fields: if so, put
#: the old number here, or the first flush after deploy destroys the window.
ADDITIVE_FROM_SCHEMAS: frozenset = frozenset()

_DEFAULT_PATH = os.path.join("data", "ai_governor_v1.json")

#: Rows retained. One verdict per signal per bar with a per-signal lifetime cap
#: of ~8, so at ~16 delivered signals/day this is months of window — which is
#: what §11.1's evidence bar needs.
_MAX_ROWS = 4000


class GovernorLedger:
    """Bounded ring of verdict rows, newest last."""

    def __init__(self, path: Optional[str] = None, max_rows: Optional[int] = None) -> None:
        self._path = _DEFAULT_PATH if path is None else path
        self._max = int(max_rows or _MAX_ROWS)
        self._rows: List[Dict[str, Any]] = []
        self._evicted = 0
        self._lock = threading.RLock()
        self._dirty = False

    @property
    def evicted(self) -> int:
        """Rows rotated out by the cap.

        Persisted WITH the data and rendered beside every verdict, because a
        reader in another process cannot see the cap and a rate computed on a
        bounded ring is a sample. `dispatch_cooldown` read `n=396` for months
        with nothing on screen distinguishing that from 396 of 24,000.
        """
        return self._evicted

    def add(self, row: Dict[str, Any]) -> bool:
        with self._lock:
            self._rows.append(dict(row))
            while len(self._rows) > self._max:
                self._rows.pop(0)
                self._evicted += 1
            self._dirty = True
        return True

    def rows(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._rows)

    def count(self) -> int:
        with self._lock:
            return len(self._rows)

    def load(self) -> None:
        """Read the ledger back at boot. Called by :func:`get_ledger`."""
        if not self._path or not os.path.exists(self._path):
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            ok, why = ledger_schema.accepts(
                payload.get("schema"), SCHEMA, ADDITIVE_FROM_SCHEMAS
            )
            if not ok:
                log.info(
                    "ai_governor: ledger schema {} refused ({}), starting fresh",
                    payload.get("schema"), why,
                )
                return
            with self._lock:
                self._rows = [
                    dict(r) for r in (payload.get("rows") or [])
                    if isinstance(r, dict) and str(r.get("signal_id") or "")
                ][-self._max:]
                self._evicted = int(payload.get("evicted") or 0)
        except Exception as exc:  # noqa: BLE001
            fail_open.record("ai_governor_ledger.load", exc)

    def flush(self, force: bool = False, extra: Optional[Dict[str, Any]] = None) -> bool:
        """Persist. ``force`` writes even when unchanged, so an idle lane still
        proves it is alive."""
        with self._lock:
            if not (self._dirty or force):
                return False
            if not self._path:
                # In-memory (what tests construct with). Return BEFORE the
                # side effect — a no-op that touches the disk is the defect
                # that filled fail_open with non-failures for two months.
                self._dirty = False
                return False
            self._dirty = False
            rows = list(self._rows)
            evicted = self._evicted

        payload: Dict[str, Any] = {
            "schema": SCHEMA,
            "written_at": time.time(),
            "max_rows": self._max,
            "evicted": evicted,
            "rows": rows,
        }
        if extra:
            payload.update(extra)
        tmp = f"{self._path}.tmp"
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            os.replace(tmp, self._path)
            return True
        except Exception as exc:  # noqa: BLE001
            fail_open.record("ai_governor_ledger.flush", exc)
            return False


_ledger: Optional[GovernorLedger] = None
_ledger_lock = threading.Lock()


def get_ledger() -> GovernorLedger:
    global _ledger
    with _ledger_lock:
        if _ledger is None:
            _ledger = GovernorLedger()
            # Defining `load` is not calling it — the guard this repo derives
            # from the tree checks for exactly this line.
            _ledger.load()
        return _ledger


def reset_ledger(ledger: Optional[GovernorLedger] = None) -> None:
    global _ledger
    with _ledger_lock:
        _ledger = ledger
