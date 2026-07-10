"""Break-even ratchet policy — noise-aware arm + park (ACTIVE, 2026-07-07).

Single source of truth for WHEN the break-even shift arms and WHERE the
armed stop parks, shared by the two BE consumers so the engine's signal
book (``trade_monitor``) and users' real positions (``pretp_dispatcher``)
behave identically:

Why this exists (7d study, 38 BREAKEVEN_EXIT scratches vs real 1m klines):

- 84% of BE scratches reached ≥1% profit within 3h of the scratch (74%
  within 1h) — the flat 1% arm triggered inside ordinary wick territory on
  fast movers, and the stop parked at the EXACT entry price got tagged by
  wicks that then resumed in our favour.

Policy:

- **Arm** at the LARGEST of: the legacy flat trigger (``be_arm_trigger_pct``),
  ``be_arm_r_mult`` × the trade's own stop distance (1R by default), and
  ``be_arm_noise_mult`` × the pair's 1h-ATR noise floor when known.
- **Park** the armed stop ``be_park_tolerance_pct`` on the LOSS side of
  entry — an exact-entry wick no longer scratches; worst case the exit is
  −tolerance% instead of 0%.

All knobs are runtime tunables (ops panel), read via the 5s-cached
accessor — no Firestore reads per tick beyond the shared doc cache.
"""
from __future__ import annotations

from src import runtime_tunables as _rt


def be_enabled(default: bool) -> bool:
    """Live BE-ratchet master switch (falls back to env boot default)."""
    try:
        return bool(_rt.get("be_shift_enabled"))
    except Exception:
        return default


def arm_threshold_pct(
    sl_distance_pct: float,
    noise_floor_pct: float = 0.0,
    tp1_distance_pct: float = 0.0,
) -> float:
    """Return the MFE % (of entry) required before the BE ratchet arms.

    TP1 cap (2026-07-10): the noise-aware arm double-counted the #702
    noise-floor stop widening — 1R of an already-widened 2.4-2.7% stop put
    the arm at ≈ the stop distance, at or ABOVE TP1 for tighter setups.
    Under the TP1-full-close default that arm is unreachable: the trade
    either closes at TP1 or round-trips its full stop with the ratchet
    never engaging (owner-reported +2% → −2.5% full-SL swings).  When the
    caller supplies the trade's TP1 distance, the arm is capped at
    ``be_arm_tp1_cap_fraction`` of it — a trade that has covered that
    fraction of the way to its own target always arms — floored at the
    flat trigger so the cap can never make the arm hair-trigger.
    """
    try:
        arm = float(_rt.get("be_arm_trigger_pct"))
        r_mult = float(_rt.get("be_arm_r_mult"))
        noise_mult = float(_rt.get("be_arm_noise_mult"))
    except Exception:
        # Registry unavailable (partial boot) — legacy flat behaviour.
        from config import BE_SHIFT_TRIGGER_PCT
        return float(BE_SHIFT_TRIGGER_PCT)
    flat_trigger = arm
    if sl_distance_pct and sl_distance_pct > 0:
        arm = max(arm, r_mult * float(sl_distance_pct))
    if noise_floor_pct and noise_floor_pct > 0:
        arm = max(arm, noise_mult * float(noise_floor_pct))
    if tp1_distance_pct and tp1_distance_pct > 0:
        try:
            cap_fraction = float(_rt.get("be_arm_tp1_cap_fraction"))
        except Exception:
            from config import BE_ARM_TP1_CAP_FRACTION
            cap_fraction = BE_ARM_TP1_CAP_FRACTION
        if cap_fraction > 0:
            cap = max(cap_fraction * float(tp1_distance_pct), flat_trigger)
            arm = min(arm, cap)
    return arm


def park_price(entry: float, is_long: bool) -> float:
    """Stop price for the armed ratchet: entry offset to the loss side by
    the park tolerance so an exact-entry wick doesn't scratch the trade."""
    try:
        tol = float(_rt.get("be_park_tolerance_pct"))
    except Exception:
        tol = 0.0
    if tol <= 0:
        return entry
    return entry * (1.0 - tol / 100.0) if is_long else entry * (1.0 + tol / 100.0)
