"""Persistence + hot-path read for the Layer-G emission controller.

Holds the live ``ControllerState`` (per-strategy overrides + verdict history) and
a bounded ledger of recent adjustments. Mirrors ``strategy_edge``'s module-global
singleton + best-effort JSON persistence (``data/emission_controller_store.json``,
which the vps-monitor workflow already collects for the analysis dead-drop) —
deliberately **not** Firestore: the controller writes only when an override
actually changes (≥ K cycles apart), so a file write is far cheaper than a
Firestore round-trip and adds nothing to any hot loop.

The **hot-path contract**: ``override_for(strategy)`` is an O(1) in-memory dict
read (the scanner calls the emission policy per post-scoring candidate). It never
touches disk or network — the in-memory state is authoritative; persistence is a
side effect on write and a one-shot load on boot.
"""
from __future__ import annotations

import json
import os
import threading
from collections import deque
from typing import Any, Deque, Dict, Iterable, List, Optional

from src.emission_controller import (
    STATUS_PRUNED,
    Adjustment,
    ControllerState,
    StrategyOverride,
)
from src.utils import get_logger

log = get_logger("emission_controller_store")

_DEFAULT_PATH = os.getenv("EMISSION_CONTROLLER_STORE_PATH", "data/emission_controller_store.json")
_LEDGER_MAX = 200


class EmissionControllerStore:
    def __init__(self, persist_path: Optional[str] = None) -> None:
        self._path = persist_path if persist_path is not None else _DEFAULT_PATH
        self._lock = threading.RLock()
        self._state = ControllerState()
        self._ledger: Deque[dict] = deque(maxlen=_LEDGER_MAX)
        self._pending: List[dict] = []   # current cycle's would-be (shadow) candidates
        self._routability: Dict[str, Any] = {}   # latest RoutabilityReport (measurement)
        self._load()

    # ---- hot path (in-memory, O(1)) --------------------------------------
    def override_for(self, strategy: str) -> StrategyOverride:
        """Per-strategy override for the emission policy. In-memory only."""
        with self._lock:
            return self._state.overrides.get((strategy or "").upper(), StrategyOverride())

    def overrides_snapshot(self) -> Dict[str, Dict[str, Any]]:
        """{strategy -> {suppress_negative, min_samples}} for the policy to load once."""
        with self._lock:
            return {s: o.to_dict() for s, o in self._state.overrides.items()}

    # ---- controller loop (rare writes) -----------------------------------
    @property
    def state(self) -> ControllerState:
        with self._lock:
            return self._state

    def commit(
        self,
        new_state: ControllerState,
        adjustments: List[Adjustment],
        routability: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Replace state with the controller's new state and persist **every
        cycle** (a 30-min small-file write, not a hot path).

        The durable ``ledger`` holds only **applied** adjustments — the audit of
        what actually changed — so a real promotion is never evicted by repeated
        shadow re-stamps under the ring-buffer cap. The current cycle's **pending
        (would-be)** candidates are kept as a separate overwritten snapshot, so
        the shadow ledger is observable during the dark / boot-grace period
        (otherwise the store would sit empty until the first live change) and the
        stability history survives a restart.
        """
        with self._lock:
            self._state = new_state
            for a in adjustments:
                if a.applied:
                    self._ledger.append(a.to_dict())
            self._pending = [a.to_dict() for a in adjustments if not a.applied]
            if routability is not None:
                self._routability = dict(routability)
            self._persist_locked()

    def ledger(self, limit: int = 50) -> List[dict]:
        """The durable audit trail of *applied* adjustments (most recent last)."""
        with self._lock:
            items = list(self._ledger)
        return items[-max(1, limit):]

    def pending(self) -> List[dict]:
        """The current cycle's would-be (shadow) candidates — what the controller
        *would* do right now but hasn't promoted yet (boot-grace, thin evidence,
        below the EV bar, or blast-radius-deferred)."""
        with self._lock:
            return list(self._pending)

    def routability(self) -> Dict[str, Any]:
        """The latest cycle's ``RoutabilityReport`` — the live measurement of what
        the controller's un-closed action space is costing. Empty until the first
        cycle runs with classification on."""
        with self._lock:
            return dict(self._routability)

    def routability_summary(self, routable: Optional[Iterable[str]] = None) -> Dict[str, Any]:
        """Latest cycle report + **lifetime** promotion attribution over the ledger.

        The lifetime split is what makes the cost legible on day one rather than
        after a week of fresh cycles: rows written before classification shipped
        carry no ``routable`` stamp, so they are classified at read time against
        ``routable``. The stamped value always wins where present — a second
        computation of the same quantity is a detector, not a replacement — and
        ``classified_at_read`` reports how much of the number came from the
        read-time pass, so a blank has a cause rather than a caption.
        """
        allowed = {str(s).upper() for s in routable} if routable is not None else None
        with self._lock:
            rows = list(self._ledger)
            latest = dict(self._routability)

        counts = {"routable": 0, "unroutable": 0, "unknown": 0, "pruned": 0}
        classified_at_read = 0
        by_key: Dict[str, int] = {}
        for row in rows:
            if str(row.get("status") or "") == STATUS_PRUNED:
                counts["pruned"] += 1
                continue
            flag = row.get("routable")
            if flag is None and allowed is not None:
                flag = str(row.get("strategy") or "").upper() in allowed
                classified_at_read += 1
            if flag is None:
                counts["unknown"] += 1
            elif flag:
                counts["routable"] += 1
            else:
                counts["unroutable"] += 1
                key = str(row.get("strategy") or "?")
                by_key[key] = by_key.get(key, 0) + 1

        return {
            "latest_cycle": latest,
            "lifetime_promotions": sum(
                counts[k] for k in ("routable", "unroutable", "unknown")
            ),
            "lifetime_counts": counts,
            "lifetime_unroutable_by_key": dict(sorted(by_key.items())),
            "classified_at_read": classified_at_read,
            "ledger_rows": len(rows),
        }

    def active_overrides(self) -> Dict[str, Dict[str, Any]]:
        """Only strategies with at least one non-None override — the live footprint."""
        snap = self.overrides_snapshot()
        return {
            s: {k: v for k, v in o.items() if v is not None}
            for s, o in snap.items()
            if any(v is not None for v in o.values())
        }

    # ---- persistence (best-effort) ---------------------------------------
    def _persist_locked(self) -> None:
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            payload = {
                "state": self._state.to_dict(),
                "ledger": list(self._ledger),
                "pending": list(self._pending),
                "active_overrides": self.active_overrides(),
                # The routability measurement, for the ops Layer-G panel. Stamped
                # here by the engine so the dashboard renders it rather than
                # re-deriving the suffix list — that mirror is the drift class
                # which silently inflated the Strategy Lab rollup for a week.
                "routability": dict(self._routability),
            }
            tmp = f"{self._path}.tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False, indent=2)
            os.replace(tmp, self._path)
        except Exception as exc:  # persistence must never break the control loop
            log.warning("emission_controller_store persist failed: {}", exc)

    def _load(self) -> None:
        try:
            if not os.path.exists(self._path):
                return
            with open(self._path, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            if isinstance(payload, dict):
                self._state = ControllerState.from_dict(payload.get("state") or {})
                led = payload.get("ledger")
                if isinstance(led, list):
                    self._ledger = deque(led, maxlen=_LEDGER_MAX)
                pend = payload.get("pending")
                if isinstance(pend, list):
                    self._pending = pend
                rout = payload.get("routability")
                if isinstance(rout, dict):
                    self._routability = rout
        except Exception as exc:
            log.warning("emission_controller_store load failed: {}", exc)


_store: Optional[EmissionControllerStore] = None


def get_emission_controller_store() -> EmissionControllerStore:
    global _store
    if _store is None:
        _store = EmissionControllerStore()
    return _store
