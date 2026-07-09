"""Mover runner-exit policy — ACTIVE (owner sign-off in-session, 2026-07-09).

Single source of truth for WHICH setup classes get the runner exit and the
partial-bank ladder it uses, consumed by ``trade_monitor`` (the engine's
signal book).

Why this exists (3d post-#702 window vs the Jun-01→Jul-05 range, ops Profit
CSVs): the mover continuation paths FIND their moves — MOVER_TREND_PULLBACK
averaged +3.38% MFE per signal — but the engine-default BE_THEN_TP1 exit
banks at most TP1 = 1R, and the BE park realises ~0 on anything that arms
and retraces.  42% of mover signals reached ≥1% MFE yet realised ≤0,
forfeiting 68% of MFE in three days (HMSTRUSDT ran +31.3% and banked 0;
TRIAUSDT +12.3% → 0).  A momentum-continuation thesis needs the tail; the
1R full-close inverts its payoff profile.

Policy (when the ``mover_runner_exit_enabled`` tunable is ON, mover setup
classes only — every other path keeps the BE_THEN_TP1 full close untouched):

- **TP1** — bank ``RUNNER_TP1_BANK_FRACTION`` (40%) of the position, lift the
  stop to the small profit-side buffer (existing TP1 handling), keep running.
- **TP2** — bank up to a cumulative ``RUNNER_TP2_CUM_FRACTION`` (70%), stop
  lifts to TP1 (existing TP2 handling — 1R now locked on the remainder).
- **NO fixed TP3 cap** (owner directive 2026-07-09: the 4-5% movers in the
  screenshots — TAIKO/NBIS/WDC, HMSTR +31% — are the thesis; a 2.5R cap
  cuts exactly them).  Crossing TP3 stamps best_tp_hit=3 and posts, but the
  last slice stays open: the phase-tightened ATR trail (0.35× after TP2,
  floored at TP1) IS the exit for the remainder.
- A trail-out after TP1 classifies as PROFIT_LOCKED with the banked slices
  credited honestly (``TradeMonitor._set_realized_pnl``).

The tunable ships ON (owner directive 2026-07-09: "make it live, no dark
flags" — the Profit tracker's measured MFE / give-back columns over the
3d/35d windows are the counterfactual evidence).  If turned OFF from ops,
the monitor resumes logging ``[SHADOW] MOVER_RUNNER_WOULD_HOLD`` at every
mover TP1 full-close so the off-state keeps measuring the fork.

All reads go through the 5s-cached runtime-tunables accessor — no Firestore
reads per monitor tick beyond the shared doc cache (Cost Discipline).
"""
from __future__ import annotations

from src import runtime_tunables as _rt

#: The two mover continuation paths.  Deliberately a fixed set, not a
#: tunable: the runner thesis is specific to momentum continuation, and
#: widening it to other paths is a scoring/exit design decision that goes
#: through its own owner sign-off.
MOVER_SETUP_CLASSES: frozenset = frozenset({
    "MOVER_TREND_PULLBACK",
    "MOVER_AVWAP_SCALP",
})

#: Fraction of the original position banked at TP1 (1R).
RUNNER_TP1_BANK_FRACTION: float = 0.40
#: Cumulative fraction banked once TP2 (1.6R) is reached.
RUNNER_TP2_CUM_FRACTION: float = 0.70


def is_mover_setup(setup_class: str) -> bool:
    """True when *setup_class* is one of the mover continuation paths."""
    return (setup_class or "").upper() in MOVER_SETUP_CLASSES


def _flag_enabled() -> bool:
    try:
        return bool(_rt.get("mover_runner_exit_enabled"))
    except Exception:
        # Registry unavailable (partial boot) — dark default.
        from config import MOVER_RUNNER_EXIT_ENABLED
        return MOVER_RUNNER_EXIT_ENABLED


def runner_exit_active(setup_class: str) -> bool:
    """True when the runner exit governs this signal's TP handling."""
    return is_mover_setup(setup_class) and _flag_enabled()


def runner_exit_shadow(setup_class: str) -> bool:
    """True when this signal WOULD run the runner exit but the flag is dark —
    the caller stamps the would-be fork instead of changing behaviour."""
    return is_mover_setup(setup_class) and not _flag_enabled()
