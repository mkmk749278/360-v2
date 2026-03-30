"""Regime transition detector.

Detects transitions between market regimes and provides confidence
adjustments during the transition window. Breakouts from QUIET to
TRENDING get boosted; exhaustion from TRENDING to RANGING gets penalized.
"""
from __future__ import annotations

import time
from typing import Dict, Optional, Tuple


# Transition adjustment table: (from_regime, to_regime) → pts
_TRANSITION_ADJUSTMENTS: Dict[Tuple[str, str], float] = {
    ("QUIET", "TRENDING_UP"): 5.0,
    ("QUIET", "TRENDING_DOWN"): 5.0,
    ("RANGING", "TRENDING_UP"): 3.0,
    ("RANGING", "TRENDING_DOWN"): 3.0,
    ("TRENDING_UP", "RANGING"): -5.0,
    ("TRENDING_DOWN", "RANGING"): -5.0,
    ("TRENDING_UP", "VOLATILE"): -3.0,
    ("TRENDING_DOWN", "VOLATILE"): -3.0,
    ("VOLATILE", "QUIET"): -3.0,
}


class RegimeTransitionDetector:
    """Tracks per-symbol regime changes and returns confidence adjustments."""

    def __init__(self, transition_window_seconds: float = 300.0) -> None:
        self._window = transition_window_seconds
        # symbol → (regime, timestamp_mono)
        self._last_regime: Dict[str, Tuple[str, float]] = {}

    def record_regime(self, symbol: str, regime: str) -> None:
        """Record the current regime for *symbol* with a monotonic timestamp."""
        self._last_regime[symbol] = (regime, time.monotonic())

    def get_transition_adjustment(self, symbol: str, current_regime: str) -> float:
        """Return a confidence adjustment for a recent regime transition.

        Returns 0.0 when there is no prior regime, the regime has not
        changed, or the transition happened outside the window.
        """
        prev = self._last_regime.get(symbol)
        if prev is None:
            return 0.0

        prev_regime, prev_ts = prev
        if prev_regime == current_regime:
            return 0.0

        elapsed = time.monotonic() - prev_ts
        if elapsed > self._window:
            return 0.0

        return _TRANSITION_ADJUSTMENTS.get((prev_regime, current_regime), 0.0)

    def get_last_transition(self, symbol: str) -> Optional[Dict]:
        """Return details of the last recorded regime or ``None``.

        The returned dict contains ``from_regime``, ``to_regime``, and
        ``seconds_ago``.  If only one regime has been recorded (no
        transition yet), returns ``None``.
        """
        prev = self._last_regime.get(symbol)
        if prev is None:
            return None

        prev_regime, prev_ts = prev
        seconds_ago = time.monotonic() - prev_ts
        return {
            "from_regime": prev_regime,
            "to_regime": prev_regime,  # same until next record
            "seconds_ago": seconds_ago,
        }
