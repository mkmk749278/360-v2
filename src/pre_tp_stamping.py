"""Pre-TP threshold + trigger-price stamping.

Pre-TP fires when an active signal moves favourably by an ATR-adaptive
threshold within the first 30 minutes of dispatch.  Without stamping at
dispatch, the threshold drifts with ATR between dispatch and fire — so
the "+0.20%+ raw" line in the Telegram signal post becomes a moving
target instead of a promise.

This module computes the threshold ONCE, at dispatch, using the ATR
that was relevant when the signal was generated.  The trigger price is
derived from entry and direction.  Both are stamped on the Signal so:

  - The Telegram post shows a real, locked-in trigger price.
  - Auto-trade fires deterministically against the stamped target,
    not whatever ATR is doing 25 minutes later.
  - History persistence (signal_history_store) round-trips the
    promise — restart-safe.
  - The trade-monitor's pre-TP check prefers stamped values; legacy
    in-flight signals from before this code shipped backfill on first
    check (defensive).

The doctrine sits under B11: every price-move tunable must be fee-aware.
Stamping converts the tunable into a per-signal commitment.
"""

from __future__ import annotations

from typing import Optional, Tuple

import config
from src.channels.base import Signal
from src.smc import Direction


def resolve_pre_tp_threshold(
    entry: float,
    atr_val: Optional[float],
) -> Tuple[float, str]:
    """Return ``(threshold_pct, source)`` using the ATR-adaptive rule.

    Mirrors the inline logic in :py:meth:`TradeMonitor._check_pre_tp_grab`
    so dispatch-time stamping and any in-monitor backfill produce the
    same result for the same inputs.

    ``source`` is one of:
      - ``"static"``  — ATR unavailable; static fallback used
      - ``"atr_floored"`` — ATR×mult was below fee floor; floor used
      - ``"atr"`` — ATR×mult won
    """
    if entry <= 0:
        return config.PRE_TP_THRESHOLD_PCT, "static"
    if atr_val is None or atr_val <= 0:
        return config.PRE_TP_THRESHOLD_PCT, "static"
    atr_pct = (atr_val / entry) * 100.0
    atr_threshold = atr_pct * config.PRE_TP_ATR_MULTIPLIER
    if atr_threshold < config.PRE_TP_FEE_FLOOR_PCT:
        return config.PRE_TP_FEE_FLOOR_PCT, "atr_floored"
    return atr_threshold, "atr"


def is_eligible(sig: Signal) -> bool:
    """Pre-TP only fires for paid-tier setups outside the breakout family.

    The trade-monitor enforces the same gates at fire-time, but stamping
    earlier-out lets the Telegram post conditionally include the line.
    """
    if not config.PRE_TP_ENABLED:
        return False
    setup_class = str(getattr(sig, "setup_class", "") or "")
    if setup_class and setup_class in config.PRE_TP_SETUP_BLACKLIST:
        return False
    return True


def stamp_pre_tp(sig: Signal) -> None:
    """Stamp ``pre_tp_threshold_pct`` and ``pre_tp_trigger_price`` in place.

    No-op when pre-TP is disabled, the setup is blacklisted, or the
    signal lacks a usable entry / direction.  Idempotent — re-running
    overwrites with the same values for the same inputs.
    """
    if not is_eligible(sig):
        return
    entry = float(getattr(sig, "entry", 0.0) or 0.0)
    if entry <= 0:
        return
    direction = getattr(sig, "direction", None)
    if direction is None:
        return
    atr_val = float(getattr(sig, "atr_val", 0.0) or 0.0)
    threshold_pct, _source = resolve_pre_tp_threshold(entry, atr_val)
    is_long = direction == Direction.LONG
    if is_long:
        trigger_price = entry * (1.0 + threshold_pct / 100.0)
    else:
        trigger_price = entry * (1.0 - threshold_pct / 100.0)
    sig.pre_tp_threshold_pct = round(threshold_pct, 4)
    sig.pre_tp_trigger_price = round(trigger_price, 8)


def is_stamped(sig: Signal) -> bool:
    """True when both ``pre_tp_threshold_pct`` and ``pre_tp_trigger_price``
    look usable.  Used by the trade-monitor to decide between stamped-
    fire and the legacy on-the-fly compute path.
    """
    return (
        getattr(sig, "pre_tp_threshold_pct", 0.0) > 0.0
        and getattr(sig, "pre_tp_trigger_price", 0.0) > 0.0
    )


__all__ = [
    "is_eligible",
    "is_stamped",
    "resolve_pre_tp_threshold",
    "stamp_pre_tp",
]
