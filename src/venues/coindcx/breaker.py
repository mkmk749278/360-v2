"""CoinDCX venue breaker — a CoinDCX outage pauses CoinDCX, not Binance.

Until 2026-10-01 every CoinDCX placement failure fed the engine's shared
global breaker (``tripwires.global_breaker``), whose trip engages the global
kill switch.  So a CoinDCX-only outage, or one CoinDCX-specific rejection
repeated across CoinDCX users on one signal, halted auto-trade for every
**Binance** subscriber too.  Users choose their exchange; one exchange's
failure must not take the other one down (owner, 2026-10-01: *"some choose
binance some choose coin dcx — we should give the best for both"*).

This breaker has the same threshold and window as the global one, so it is
exactly as sensitive.  Only what it stops is narrower:

* **Trip** → the CoinDCX master switch (runtime tunable
  ``coindcx_execution_enabled``) is written OFF, and an admin alert is sent.
  New CoinDCX orders stop for everyone; positions already open keep their
  exchange-resident stop, and the reconciler keeps running.
* **Reset** is the owner turning that same switch back ON from
  ``/control/coindcx``.  There is no second switch to find, and the write
  survives a restart.
* **If the write fails** (no Firestore in this process), the trip is held in
  memory, so CoinDCX still refuses orders until the engine restarts.  It is
  never silently forgotten.

Still shared, deliberately: the per-user breaker (a user is on one exchange,
so disabling them stops nobody else), and the kill switch and global breaker
that *gate* CoinDCX orders.  A signing-service or KMS outage reaches both
exchanges, and the Binance breaker that catches it still stops CoinDCX.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any, Callable, Deque, Dict, Optional

from src.utils import get_logger

log = get_logger("venues.coindcx.breaker")


class CoinDCXVenueBreaker:
    def __init__(
        self,
        *,
        threshold: Optional[int] = None,
        window_s: Optional[float] = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        from src.execution import tripwires as _tw

        self.threshold = int(threshold or _tw.DEFAULT_GLOBAL_REJECTION_THRESHOLD)
        self.window_s = float(window_s or _tw.DEFAULT_GLOBAL_REJECTION_WINDOW_S)
        self._clock = clock
        self._lock = threading.RLock()
        self._times: Deque[float] = deque()
        self._held_in_memory = False
        self.trips = 0
        self.failures_total = 0
        self.last_trip_at: Optional[float] = None
        self.last_trip_reason = ""
        self.last_trip_persisted: Optional[bool] = None

    def tripped_in_memory(self) -> bool:
        """True only when a trip could not be written to the master switch."""
        with self._lock:
            return self._held_in_memory

    def record_failure(self, exc: BaseException) -> bool:
        """Count one CoinDCX placement failure.  True if this one tripped."""
        now = self._clock()
        with self._lock:
            self.failures_total += 1
            cutoff = now - self.window_s
            while self._times and self._times[0] < cutoff:
                self._times.popleft()
            self._times.append(now)
            if len(self._times) < self.threshold:
                return False
            count = len(self._times)
            self._times.clear()  # one trip per burst
            self.trips += 1
            self.last_trip_at = time.time()
            self.last_trip_reason = (
                f"{count} CoinDCX placement failures in {self.window_s:.0f}s "
                f"(last: {type(exc).__name__}: {str(exc)[:160]})"
            )
        log.error("CoinDCX venue breaker tripped — {}", self.last_trip_reason)
        persisted = _switch_off()
        with self._lock:
            self.last_trip_persisted = persisted
            if not persisted:
                self._held_in_memory = True
        _alert(self.last_trip_reason, persisted)
        return True

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "threshold": self.threshold,
                "window_s": self.window_s,
                "failures_total": self.failures_total,
                "failures_in_window": len(self._times),
                "trips": self.trips,
                "last_trip_at": self.last_trip_at,
                "last_trip_reason": self.last_trip_reason,
                "last_trip_persisted": self.last_trip_persisted,
                "held_in_memory": self._held_in_memory,
            }


def _switch_off() -> bool:
    """Write the CoinDCX master switch OFF.  False when it could not be."""
    try:
        from src import runtime_tunables as _rt

        _rt.set_values({"coindcx_execution_enabled": False})
        return True
    except Exception as exc:  # noqa: BLE001 — held in memory instead
        log.error("CoinDCX breaker could not switch the venue off: {}", exc)
        try:
            from src import fail_open as _fo

            _fo.record("coindcx.breaker.switch_off", exc)
        except Exception:  # pragma: no cover
            pass
        return False


def _alert(reason: str, persisted: bool) -> None:
    text = (
        "🚨 *CoinDCX auto-trade paused — venue breaker tripped*\n"
        f"{reason}\n"
        + ("The CoinDCX master switch is now OFF. Binance auto-trade is unaffected.\n"
           "Turn it back on from ops → Control → CoinDCX once the cause is understood."
           if persisted else
           "Could NOT write the master switch — CoinDCX is refused in memory until "
           "the engine restarts. Binance auto-trade is unaffected.")
    )
    try:
        from src.execution import telegram_alerts as _ta
        from src.execution import tripwires as _tw

        _tw._spawn_alert(lambda: _ta._send(text))
    except Exception:  # pragma: no cover — the log line above is the record
        log.exception("CoinDCX breaker alert failed")


_BREAKER: Optional[CoinDCXVenueBreaker] = None


def get_breaker() -> CoinDCXVenueBreaker:
    global _BREAKER
    if _BREAKER is None:
        _BREAKER = CoinDCXVenueBreaker()
    return _BREAKER


def set_breaker_for_test(b: Optional[CoinDCXVenueBreaker]) -> None:
    global _BREAKER
    _BREAKER = b
