"""Precise-entry *arming* stage — separate the setup from the trigger.

## Why this exists (2026-07-23, owner-validated on real data)

A momentum evaluator (MOVER_TREND_PULLBACK and the mover family) is good at
*direction* — it identifies "this mover will resume its trend" — but it emits at
*detection*, which is mid-pullback.  A no-look-ahead replay of 26 live MVRTP
signals against real Gate.io klines showed the cost of that: entries ate a
**−15 % to −60 % adverse excursion** before (often) turning the signalled way, so
a 1–3 % stop is noise-width and the trade is stopped/liquidated before the
direction it called ever pays.  In 20 of 23 stopped trades price *did* go on to
move favourably — the thesis is right, the **entry timing** is wrong.

Splitting *setup* (detection) from *trigger* (precise entry) rescued it in the
replay: waiting for the turn lifted win rate **8 % → 41 %** and average R
**−0.50 → −0.09** on the same signals.  It reaches breakeven with a first-pass
trigger; the remaining edge is trigger *quality* (a real momentum turn, not a
green candle) plus letting winners run — tuned forward, not guessed.

## What this module is

A **pure, I/O-free** state resolver (mirrors ``mover_ignition`` — no engine refs,
no network, fully unit-testable with synthetic candles).  Given a detected
candidate's side and the candles that arrive *after* detection, it runs the
precise-entry state machine:

    DETECTED → (watch for the turn) → TRIGGERED(entry, structural stop) | EXPIRED

The trigger, per the validated replay, requires all of:
  * **floor / level** — the pullback's swing extreme anchors a *structural* stop;
  * **momentum turn** — the candle reclaims the prior candle's extreme in the
    signal's direction and closes with the move (a hook, not mere presence);
  * **volume confirm** — the trigger candle carries above-baseline volume.

The stop is anchored to the turn structure (``swing_lookback`` extreme ± buffer),
and a trigger whose resulting stop is *wider* than ``max_sl_pct`` is rejected —
we keep watching for a tighter turn, and expire if none comes.  That enforces the
owner's rule: *"at that entry the SL is not wider."*

## How it is consumed (no scaffold)

The resolver's output is **measurement from day one**: the scanner arms every
mover-family candidate and feeds the post-detection candles here; the resulting
``ArmOutcome`` is stamped as the ``@ARMED`` arm in the strategy-edge ledger
alongside the live (emit-on-detect) arm, forward-measured net-of-cost.  When
``ARMED_ENTRY_LIVE_APPLY`` is on, a TRIGGERED outcome *becomes* the emitted
signal's entry/stop and an EXPIRED candidate is not emitted; when off, the live
path is unchanged and only the ledger sees it.  Live-apply flips on the measured
edge (dark-first graduation), guarded by the ``armed_entry`` kill switch and the
edge-reconciliation watchdog.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence, Tuple

from src import fail_open
from src.utils import get_logger

log = get_logger("armed_signal")

LONG = "LONG"
SHORT = "SHORT"


class ArmStatus(str, Enum):
    PENDING = "PENDING"       # still watching for the turn
    TRIGGERED = "TRIGGERED"   # precise entry found
    EXPIRED = "EXPIRED"       # no qualifying turn within the window


@dataclass(frozen=True)
class ArmConfig:
    """Trigger calibration.  All values env-overridable via config/ helpers.

    Defaults are the first-pass replay config (breakeven); the forward ledger
    tunes them toward positive.  Kept here as a value object so tests and the
    shadow measurement use exactly the same numbers as live.
    """
    expire_bars: int = 24          # give up if no turn within this many candles
    vol_mult: float = 1.2          # trigger candle volume vs trailing mean
    vol_lookback: int = 6          # trailing window for the volume baseline
    swing_lookback: int = 8        # candles back to anchor the structural stop
    max_sl_pct: float = 3.0        # reject a turn whose stop is wider than this (%)
    buffer_pct: float = 0.15       # stop buffer beyond the swing extreme (%)


# A candle is (open, high, low, close, volume).  Time is positional (index).
Candle = Tuple[float, float, float, float, float]


@dataclass(frozen=True)
class ArmOutcome:
    status: ArmStatus
    trigger_index: Optional[int] = None   # index into the post-detection candles
    entry: Optional[float] = None         # precise entry (trigger candle close)
    stop: Optional[float] = None          # structural tight stop
    sl_pct: Optional[float] = None        # |entry-stop|/entry * 100
    reason: str = ""

    @property
    def triggered(self) -> bool:
        return self.status is ArmStatus.TRIGGERED


def arm_config_from_settings() -> ArmConfig:
    """Build an :class:`ArmConfig` from ``config`` so shadow, live, and tests
    share one calibration.  Imported lazily to keep this module config-light."""
    try:
        import config
        return ArmConfig(
            expire_bars=int(config.ARMED_ENTRY_EXPIRE_BARS),
            vol_mult=float(config.ARMED_ENTRY_VOL_MULT),
            swing_lookback=int(config.ARMED_ENTRY_SWING_LOOKBACK),
            max_sl_pct=float(config.ARMED_ENTRY_MAX_SL_PCT),
            buffer_pct=float(config.ARMED_ENTRY_BUFFER_PCT),
        )
    except Exception as exc:
        fail_open.record("armed_signal.arm_config_from_settings", exc)
        return ArmConfig()


def _mean(vals: Sequence[float]) -> float:
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else 0.0


def resolve_arm(
    side: str,
    candles: Sequence[Candle],
    cfg: Optional[ArmConfig] = None,
) -> ArmOutcome:
    """Resolve the precise-entry state machine over post-detection candles.

    ``candles`` are the OHLCV candles that *closed after* the setup was detected,
    in chronological order.  Pure and side-effect-free: the same call serves the
    shadow measurement (whole window) and a live incremental poll (candles so far,
    which returns PENDING until the turn arrives or the window expires).

    Never raises — malformed input fails toward EXPIRED (no trade), the safe
    direction for a money-path resolver, and records the failure to fail_open.
    """
    cfg = cfg or ArmConfig()
    try:
        long = side.upper() == LONG
        n = len(candles)
        if n < 2:
            return ArmOutcome(ArmStatus.PENDING, reason="insufficient_candles")

        horizon = min(cfg.expire_bars, n)
        for i in range(1, horizon):
            o, h, l, c, v = candles[i]
            po, ph, pl, pc, pv = candles[i - 1]

            # --- momentum turn (a hook, not mere presence) --------------------
            if long:
                reclaim = c > ph and c > o          # takes prior high, closes up
            else:
                reclaim = c < pl and c < o          # takes prior low, closes down
            if not reclaim:
                continue

            # --- volume confirm ----------------------------------------------
            base = _mean([candles[j][4] for j in range(max(0, i - cfg.vol_lookback), i)])
            vol_ok = (v > cfg.vol_mult * base) if base > 0 else True
            if not vol_ok:
                continue

            # --- structural (tight) stop anchored to the pullback extreme -----
            lo = max(0, i - cfg.swing_lookback)
            if long:
                swing = min(candles[j][2] for j in range(lo, i + 1))   # swing low
                stop = swing * (1.0 - cfg.buffer_pct / 100.0)
                sl_pct = (c - stop) / c * 100.0 if c > 0 else 999.0
            else:
                swing = max(candles[j][1] for j in range(lo, i + 1))   # swing high
                stop = swing * (1.0 + cfg.buffer_pct / 100.0)
                sl_pct = (stop - c) / c * 100.0 if c > 0 else 999.0

            # Enforce "the SL is not wider": a turn that only offers a wide stop
            # is not a precise entry — keep watching for a tighter one.
            if sl_pct <= 0 or sl_pct > cfg.max_sl_pct:
                continue

            return ArmOutcome(
                status=ArmStatus.TRIGGERED,
                trigger_index=i,
                entry=c,
                stop=stop,
                sl_pct=round(sl_pct, 4),
                reason="turn_confirmed",
            )

        # Window exhausted with no qualifying turn.
        if n >= cfg.expire_bars:
            return ArmOutcome(ArmStatus.EXPIRED, reason="no_turn_in_window")
        return ArmOutcome(ArmStatus.PENDING, reason="watching")
    except Exception as exc:  # never break the money path on a resolver bug
        fail_open.record("armed_signal.resolve_arm", exc)
        return ArmOutcome(ArmStatus.EXPIRED, reason="resolver_error")
