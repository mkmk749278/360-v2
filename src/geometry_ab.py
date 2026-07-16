"""Stop-geometry A/B shadow measurement (Phase 3 item 8 — the biggest edge lever).

The Crypto Market Doctrine's core mechanical finding: our fixed-% stops sit
*inside* a mid-cap's 15m noise band, exactly where liquidity-grab algorithms
feed, which is why the book bleeds expiries and stopped-in-noise losses.  The
institutional fix is volatility-first geometry — "let the stop define the size":

    stop distance = max(ATR × mult, distance beyond the structure pool)
    size          = account risk ÷ stop distance   (risk held constant)

This module measures that fix WITHOUT touching live output.  For every
post-scoring candidate — emitted or gate-suppressed — the scanner stamps a
counterfactual **pair** into a dedicated ledger:

    ``SETUP@FIXED``  — the evaluator's real stop (what we do today)
    ``SETUP@ATR``    — the ATR/structure stop beyond the liquidity pool

Both arms share the same entry/TP1 and are forward-measured identically
(TP1-before-SL on real candles) by the existing 5-min audit loop, then fed to
the Strategy×Context edge matrix as ``source="shadow"`` rows.  Because outcomes
are recorded in R-units (PnL ÷ own stop distance), constant-dollar-risk sizing
is inherent in the comparison — a wider stop that stops getting noise-clipped
must still pay more R per unit risk to win the A/B.

Observe-only end to end: evaluator geometry ownership (B7) is untouched, no
record here can reach the signal queue, and *applying* a winning geometry live
remains a dark-first + owner-sign-off change.  The pair ledger is a separate
``SuppressedCandidateStore`` instance so A/B volume can never evict real gate
records from the suppression audit, and geometry rows never pollute the
per-gate KEEP/TUNE/DROP table.

Cost discipline: stamps are O(1) in-memory appends on suppression/emission
events only (not per scanned symbol); candles come from the already-warm
in-memory store; classification + persistence batch on the existing 5-min loop.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Dict, List, Optional, Sequence, Tuple

from src.shadow_strategies import _simple_atr
from src.suppression_audit import SuppressedCandidateStore, stamp_candidate
from src.utils import get_logger

log = get_logger("geometry_ab")

# Strategy-name suffixes for the measurement arms.  The edge matrix keys on
# the suffixed name, so each arm appears as its own row per context cell.
# @TUNED (src/tuned_variants.py, 2026-07-16) rides the same variant plumbing:
# excluded from the allocator and from per-strategy rollups exactly like the
# stop-geometry arms — measurement rows are never activatable strategies.
FIXED_SUFFIX = "@FIXED"
ATR_SUFFIX = "@ATR"
TUNED_SUFFIX = "@TUNED"
_VARIANT_SUFFIXES: Tuple[str, ...] = (FIXED_SUFFIX, ATR_SUFFIX, TUNED_SUFFIX)

GATE_FIXED = "geometry_ab:fixed"
GATE_ATR = "geometry_ab:atr"

_DEFAULT_PATH: str = os.getenv("GEOMETRY_AB_PATH", "data/geometry_ab_candidates.json")
_MAX_RECORDS: int = int(os.getenv("GEOMETRY_AB_MAX_RECORDS", "4000"))


def is_geometry_variant(strategy: str) -> bool:
    """True for ``X@FIXED`` / ``X@ATR`` measurement rows.

    The allocator must never *recommend* a measurement arm — geometry variants
    are evidence about HOW to stop a strategy, not activatable strategies.
    """
    s = str(strategy or "")
    return any(s.endswith(sfx) for sfx in _VARIANT_SUFFIXES)


def base_strategy(strategy: str) -> str:
    """``X@ATR`` → ``X`` (identity for non-variant names)."""
    s = str(strategy or "")
    for sfx in _VARIANT_SUFFIXES:
        if s.endswith(sfx):
            return s[: -len(sfx)]
    return s


# ---------------------------------------------------------------------------
# Pure geometry math
# ---------------------------------------------------------------------------


def compute_atr_structure_stop(
    *,
    side: str,
    entry: float,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    atr_mult: Optional[float] = None,
    structure_lookback: Optional[int] = None,
    structure_buffer_pct: Optional[float] = None,
    max_stop_pct: Optional[float] = None,
) -> Optional[float]:
    """The doctrine stop: beyond the liquidity pool, outside the noise band.

    Distance = max(ATR14 × mult, |entry − pool|) + buffer beyond the pool,
    where the pool is the ``structure_lookback``-bar swing extreme (where
    retail stops cluster and hunts feed).  Returns the stop *price*, or
    ``None`` when the inputs can't support an honest computation (no ATR,
    not enough bars, stop degenerate or beyond the sanity clamp) — a pair
    that can't compute its ATR arm is skipped entirely, never guessed.
    """
    from config import (
        GEOMETRY_AB_ATR_MULT,
        GEOMETRY_AB_MAX_STOP_PCT,
        GEOMETRY_AB_STRUCTURE_BUFFER_PCT,
        GEOMETRY_AB_STRUCTURE_LOOKBACK_BARS,
    )

    mult = GEOMETRY_AB_ATR_MULT if atr_mult is None else float(atr_mult)
    lookback = (
        GEOMETRY_AB_STRUCTURE_LOOKBACK_BARS
        if structure_lookback is None
        else int(structure_lookback)
    )
    buffer_pct = (
        GEOMETRY_AB_STRUCTURE_BUFFER_PCT
        if structure_buffer_pct is None
        else float(structure_buffer_pct)
    )
    clamp_pct = GEOMETRY_AB_MAX_STOP_PCT if max_stop_pct is None else float(max_stop_pct)

    try:
        entry = float(entry or 0.0)
        side = str(side or "").upper()
        if entry <= 0 or side not in ("LONG", "SHORT"):
            return None
        n = min(len(highs), len(lows), len(closes))
        if n < lookback or lookback <= 0:
            return None
        atr = _simple_atr(highs, lows, closes)
        if atr <= 0:
            return None
        atr_dist = atr * max(0.0, mult)
        buffer_abs = entry * buffer_pct / 100.0
        if side == "LONG":
            pool = min(float(v) for v in lows[-lookback:])
            pool_dist = max(0.0, entry - pool)
            stop = entry - max(atr_dist, pool_dist + buffer_abs)
        else:
            pool = max(float(v) for v in highs[-lookback:])
            pool_dist = max(0.0, pool - entry)
            stop = entry + max(atr_dist, pool_dist + buffer_abs)
        dist = abs(entry - stop)
        if stop <= 0 or dist <= 0:
            return None
        if clamp_pct > 0 and dist > entry * clamp_pct / 100.0:
            return None
        return stop
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Pair ledger — a dedicated store so A/B volume can't evict gate records
# ---------------------------------------------------------------------------

_geometry_store: Optional[SuppressedCandidateStore] = None
_store_lock = threading.Lock()

# Per-(symbol, setup, side) pair cooldown.  None sentinel, never 0.0 — a 0.0
# default would swallow every stamp for the first COOLDOWN seconds after boot
# (monotonic() starts near zero on a fresh host; bug caught in S53).
_last_pair_stamp: Dict[Tuple[str, str, str], float] = {}


def get_geometry_store() -> SuppressedCandidateStore:
    global _geometry_store
    with _store_lock:
        if _geometry_store is None:
            _geometry_store = SuppressedCandidateStore(
                persist_path=_DEFAULT_PATH, maxlen=_MAX_RECORDS
            )
        return _geometry_store


def stamp_geometry_pair(
    *,
    symbol: str,
    channel: str,
    setup_class: str,
    side: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    confidence: float = 0.0,
    context_key: str = "",
    regime: str = "",
    valid_for_minutes: float = 0.0,
    store: Optional[SuppressedCandidateStore] = None,
    now_mono: Optional[float] = None,
) -> Optional[float]:
    """Stamp the FIXED/ATR counterfactual pair for one candidate (fail-open).

    Returns the computed ATR/structure stop price when the pair was stamped,
    else ``None`` (cooldown, un-computable ATR arm, or bad geometry).  Both
    arms always stamp together — a lone arm would bias the A/B.
    """
    try:
        setup = str(setup_class or "").strip()
        if not setup or is_geometry_variant(setup):
            return None
        entry = float(entry or 0.0)
        stop_loss = float(stop_loss or 0.0)
        tp1 = float(tp1 or 0.0)
        if entry <= 0 or stop_loss <= 0 or tp1 <= 0 or abs(entry - stop_loss) <= 0:
            return None
        side_u = str(side or "").upper()
        cd_key = (str(symbol or ""), setup, side_u)
        mono = time.monotonic() if now_mono is None else float(now_mono)
        from config import GEOMETRY_AB_STAMP_COOLDOWN_SEC

        last = _last_pair_stamp.get(cd_key)
        if last is not None and mono - last < GEOMETRY_AB_STAMP_COOLDOWN_SEC:
            return None
        alt_stop = compute_atr_structure_stop(
            side=side_u, entry=entry, highs=highs, lows=lows, closes=closes
        )
        if alt_stop is None:
            return None
        target = store or get_geometry_store()

        def _stamp_arm(gate: str, suffix: str, stop: float):
            return stamp_candidate(
                gate_name=gate,
                symbol=str(symbol or ""),
                channel=str(channel or ""),
                setup_class=f"{setup}{suffix}",
                side=side_u,
                entry=entry,
                stop_loss=stop,
                tp1=tp1,
                confidence=float(confidence or 0.0),
                context_key=context_key or "",
                regime=regime or "",
                valid_for_minutes=float(valid_for_minutes or 0.0),
                store=target,
            )

        # Both arms stamp together or not at all — a lone arm biases the A/B.
        # The ATR arm's inputs are pre-validated above, so once the FIXED arm
        # stamps, the pair completes.
        if _stamp_arm(GATE_FIXED, FIXED_SUFFIX, stop_loss) is None:
            return None
        if _stamp_arm(GATE_ATR, ATR_SUFFIX, alt_stop) is None:
            return None
        _last_pair_stamp[cd_key] = mono
        return alt_stop
    except Exception as exc:
        from src import fail_open
        fail_open.record("geometry_ab.stamp_pair", exc)
        return None


def summarize_geometry_ab(
    matrix: Dict[str, Dict], *, min_sample: int = 15
) -> List[Dict]:
    """Per-strategy fixed-vs-ATR rollup from edge-matrix cells (pure).

    Pools each arm's cells across contexts (sample-weighted) and names a
    leader only when BOTH arms clear ``min_sample`` — an A/B with one thin
    arm is MEASURING, not evidence.  Sorted by measured |ΔR| descending so
    the biggest geometry effects surface first.
    """
    pooled: Dict[str, Dict[str, Dict[str, float]]] = {}
    for cell in (matrix or {}).values():
        strategy = str(cell.get("strategy", ""))
        # Explicit suffix check — @TUNED is a variant too but belongs to the
        # tuned-recipe measurement, not this stop A/B; pooling it into the
        # "fixed" arm would corrupt the rollup.
        if not (strategy.endswith(ATR_SUFFIX) or strategy.endswith(FIXED_SUFFIX)):
            continue
        arm = "atr" if strategy.endswith(ATR_SUFFIX) else "fixed"
        base = base_strategy(strategy)
        n = int(cell.get("n", 0) or 0)
        if n <= 0:
            continue
        agg = pooled.setdefault(base, {}).setdefault(
            arm, {"n": 0.0, "wins": 0.0, "r_sum": 0.0, "cells": 0.0}
        )
        agg["n"] += n
        agg["wins"] += float(cell.get("win_rate", 0.0) or 0.0) * n
        agg["r_sum"] += float(cell.get("avg_r", 0.0) or 0.0) * n
        agg["cells"] += 1
    rows: List[Dict] = []
    for base, arms in pooled.items():

        def _arm(name: str) -> Dict[str, float]:
            a = arms.get(name, {"n": 0.0, "wins": 0.0, "r_sum": 0.0, "cells": 0.0})
            n = a["n"]
            return {
                "n": int(n),
                "cells": int(a["cells"]),
                "win_rate": (a["wins"] / n) if n else 0.0,
                "avg_r": (a["r_sum"] / n) if n else 0.0,
            }

        fixed = _arm("fixed")
        atr = _arm("atr")
        measured = fixed["n"] >= min_sample and atr["n"] >= min_sample
        delta = atr["avg_r"] - fixed["avg_r"]
        rows.append(
            {
                "strategy": base,
                "fixed": fixed,
                "atr": atr,
                "delta_r": delta if measured else None,
                "leader": (
                    ("ATR" if delta > 0 else "FIXED" if delta < 0 else "TIE")
                    if measured
                    else "MEASURING"
                ),
            }
        )
    rows.sort(
        key=lambda r: abs(r["delta_r"]) if r["delta_r"] is not None else -1.0,
        reverse=True,
    )
    return rows
