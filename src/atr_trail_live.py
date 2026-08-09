"""ATR-trail (Chandelier) exit — measured forward, in real time, like SAR.

Owner, 2026-08-09: *"look SAR live in signals tab — exactly implement same for
ATR-trail (Chandelier), and also implement ATR-trail (Chandelier) and SAR on the
dark feed too, then we can see which actually makes a good setup, then we decide
the exit mechanism. Live feed is mostly MVRTP only; in the dark feed we at least
have some other paths, so we can decide on regular pairs too."*

**This module is deliberately thin, and that is the whole design.** Every guard
the SAR arm bought over six sessions — the stale-anchor refusal (#836), the
per-advance replay guard (#846), the regressed-vs-rolled-off split, the stall
stamps (#835), the timestamp-monotonicity refusal (#842/#844), the two fills,
the two denominators, the held-to-stop arm and the stop-management rules (#869)
— lives in ``sar_live_shadow``, which is the *arm engine* rather than the SAR
mechanism. This file adds a mechanism and two ledgers and nothing else. A
second copy of that engine would be the sixth instance of the one defect shape
this repo keeps naming, and "exactly the same" is an argument for one
implementation, not two.

Four populations, four files
----------------------------
======================  ===========================  =========================
                        SAR                          ATR-trail (Chandelier)
======================  ===========================  =========================
Delivered signals       ``sar_live_arms_v1.json``    ``atr_trail_arms_v1.json``
Dark-feed rows          ``dark_sar_arms_v1.json``    ``dark_atr_trail_arms_v1.json``
======================  ===========================  =========================

Never one file with a ``mechanism`` column. The delivered ledgers are the
evidence for changing what subscribers receive and every row in them reached a
subscriber; a dark row reached nobody. Pooling either axis would inflate that
evidence silently — a consumer that has not heard of the second population
cannot filter it out, whereas a consumer pointed at a file it does not open
cannot see it at all. That is the reasoning that already split the dark SAR
lane off, applied a second time on the mechanism axis.

Why the dark lane is the one the owner actually asked about
------------------------------------------------------------
The delivered book is ~59% ``MOVER_TREND_PULLBACK``, so a delivered-only verdict
on an exit mechanism is close to a verdict on one path's geometry. The dark feed
carries the paths the gates normally silence, which is the only population in
this system where "does this exit suit *this* setup" is answerable per path. The
answer will still be thin per cell — read n before any average, and
``FAILED_AUCTION_RECLAIM``'s +0.846R on three rows is the standing reminder of
what a thin cell costs.

What this measures and what it cannot
-------------------------------------
The chandelier governs from the anchor bar whenever its level is not already
breached, which — unlike SAR, whose direction genuinely opposes the trade about
a fifth of the time — is nearly always. So the arm mostly **cancels the
evaluator's stop from bar one** and replaces it with a level 3 ATRs behind the
running extreme. That stop is frequently **wider** than the one the trade was
sized for, which is the ``r_level`` / ``r_level_risk`` split the SAR page
already publishes and the reason a chandelier verdict must never be read in R
alone. PnL % leads; R is the bridge.
"""
from __future__ import annotations

import os
import threading
from typing import Any, Dict, List, Optional

from src import sar_live_shadow as arms
from src.trail_mechanisms import MECH_CHANDELIER

#: Ledger paths. ``_v1`` is this lane's own schema in the filename, independent
#: of the SAR files' ``_v1`` — the two lanes were created at different times and
#: a shared version number would tie their futures together for no reason.
#:
#: **These filenames are a cross-repo contract.** ops mounts the engine's
#: ``data/`` read-only at ``/engine-data`` and opens them by name;
#: ``tests/test_atr_trail_live.py`` pins them on this, the producing, side —
#: #817's ``entry_regime`` was read by ops for months while nothing wrote it and
#: the page looked full the whole time.
LIVE_PATH = os.getenv("ATR_TRAIL_LIVE_PATH", "data/atr_trail_arms_v1.json")
DARK_PATH = os.getenv("ATR_TRAIL_DARK_PATH", "data/dark_atr_trail_arms_v1.json")

_live_ledger: Optional[arms.SarLiveLedger] = None
_dark_ledger: Optional[arms.SarLiveLedger] = None
_lock = threading.Lock()


def enabled() -> bool:
    """Is the ATR-trail measurement running.

    Read at call time, never captured at import: a module-level snapshot of a
    config flag is how a restart becomes the only way to change a measurement.
    """
    try:
        from config import ATR_TRAIL_LIVE_ENABLED

        return bool(ATR_TRAIL_LIVE_ENABLED)
    except Exception:
        return False


def _build(path: str) -> arms.SarLiveLedger:
    from config import SAR_LIVE_SHADOW_MAX_RESOLVED

    ledger = arms.SarLiveLedger(
        path=path,
        max_resolved=SAR_LIVE_SHADOW_MAX_RESOLVED,
        mechanism=MECH_CHANDELIER,
    )
    # `load()` here rather than at the first flush: flush without load is how
    # two structural ledgers erased their own window on every deploy while the
    # page reported a healthy one. `get_ledger()` must CALL load, not merely
    # have one — defining a method is not calling it, and there is a derived
    # test in this repo that checks exactly that.
    ledger.load()
    return ledger


def get_ledger() -> arms.SarLiveLedger:
    """Arms on **delivered** signals."""
    global _live_ledger
    with _lock:
        if _live_ledger is None:
            _live_ledger = _build(LIVE_PATH)
        return _live_ledger


def get_dark_ledger() -> arms.SarLiveLedger:
    """Arms on **dark-feed** rows — signals diverted before the queue."""
    global _dark_ledger
    with _lock:
        if _dark_ledger is None:
            _dark_ledger = _build(DARK_PATH)
        return _dark_ledger


def reset_ledgers(
    live: Optional[arms.SarLiveLedger] = None,
    dark: Optional[arms.SarLiveLedger] = None,
) -> None:
    """Test hook."""
    global _live_ledger, _dark_ledger
    with _lock:
        _live_ledger, _dark_ledger = live, dark


# --------------------------------------------------------------------------- #
# Orchestration — the same two entry points, for the same reason (#835)
# --------------------------------------------------------------------------- #


def observe_signal(
    sig: Any,
    store: Any,
    *,
    price: Optional[float] = None,
    dark: bool = False,
    ledger: Optional[arms.SarLiveLedger] = None,
    timeframes: Optional[List[str]] = None,
    now_ts: Optional[float] = None,
) -> None:
    """Open this signal's chandelier arms on first sight.

    ``dark`` selects the ledger and the health lane together, because those two
    must never disagree: a row filed in the dark ledger whose health rolled into
    the live lane would let a dark stall page as a live failure, and the whole
    point of per-lane health is that a number is only readable when its
    population is nameable.
    """
    if not enabled():
        return
    book = ledger if ledger is not None else (
        get_dark_ledger() if dark else get_ledger()
    )
    arms.observe_signal(
        sig,
        store,
        price=price,
        timeframes=timeframes,
        ledger=book,
        lane=arms.lane_of(MECH_CHANDELIER, dark),
        mechanism=MECH_CHANDELIER,
        now_ts=now_ts,
    )


def sweep(
    store: Any,
    *,
    price_fn: Optional[Any] = None,
    dark: bool = False,
    ledger: Optional[arms.SarLiveLedger] = None,
    now_ts: Optional[float] = None,
) -> Dict[str, int]:
    """Advance every open chandelier arm in one lane's ledger."""
    if not enabled():
        return {
            "advanced": 0, "current": 0, "stalled": 0,
            "no_series": 0, "series_corrupt": 0, "retired": 0,
        }
    book = ledger if ledger is not None else (
        get_dark_ledger() if dark else get_ledger()
    )
    return arms.sweep(
        store,
        price_fn=price_fn,
        ledger=book,
        lane=arms.lane_of(MECH_CHANDELIER, dark),
        now_ts=now_ts,
    )
