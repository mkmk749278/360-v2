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
from typing import Any, Deque, Dict, List, Optional

from src.emission_controller import Adjustment, ControllerState, StrategyOverride
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

    def commit(self, new_state: ControllerState, adjustments: List[Adjustment]) -> None:
        """Replace state with the controller's new state and append *applied*
        adjustments to the ledger; persist best-effort only when something
        actually changed."""
        applied = [a for a in adjustments if a.applied]
        with self._lock:
            self._state = new_state
            for a in adjustments:
                self._ledger.append(a.to_dict())
            if applied:
                self._persist_locked()

    def ledger(self, limit: int = 50) -> List[dict]:
        with self._lock:
            items = list(self._ledger)
        return items[-max(1, limit):]

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
            payload = {"state": self._state.to_dict(), "ledger": list(self._ledger)}
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
        except Exception as exc:
            log.warning("emission_controller_store load failed: {}", exc)


_store: Optional[EmissionControllerStore] = None


def get_emission_controller_store() -> EmissionControllerStore:
    global _store
    if _store is None:
        _store = EmissionControllerStore()
    return _store
