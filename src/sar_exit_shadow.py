"""Parabolic-SAR exit shadow arm (``@SAREXIT``) — forward-measuring the
2026-07-25 bake-off's verdict on live signals, dark and observe-only.

The large-sample exit-method bake-off (``scripts/exit_method_backtest.py``,
102,496 klines-derived entries over 6 months) ranked four exits and only one
was profitable: **Parabolic SAR trailing on 15m bars**, PF 1.60, positive in
7/7 months, all 4 regimes, both directions, 20/20 symbols, and not
outlier-driven (dropping the top 3 trades leaves PF at 1.60).  The other two
trails lost on the identical window (SuperTrend 0.93, ATR 0.72).

**Nothing here changes an exit.**  Per the production dark-first doctrine a
backtest verdict is not a promotion: the next step is forward measurement on
*real live signals* in *real market context*, and that is all this module does.
For every post-scoring candidate the scanner already stamps geometry arms for,
this stamps a second counterfactual **pair** into its own ledger:

    ``SETUP@SARBASE``  — the live evaluator geometry (entry / SL / TP1), static
    ``SETUP@SAREXIT``  — the same entry, exited by a trailing 15m Parabolic SAR

Both arms are forward-measured over the **identical window**, which is the
point of the pair.  The bake-off's headline "SAR beats our current exit" was
confounded: the engine baseline got a 100-minute lookahead while the trails got
48 hours — 29× longer.  The trail-vs-trail ranking was clean, the
trail-vs-baseline comparison was not.  Here the control arm gets exactly the
window the trail gets, so the comparison the owner actually has to sign off on
is measured honestly from the first record.

Why the math is a verbatim port:  ``parabolic_sar`` and the trail walk below
are copied from the bake-off script rather than re-derived.  If the shadow arm
and the backtest ever disagreed, we would not know which one was lying — and
the entire value of this arm is that it either confirms or kills a number we
already have.  ``tests/test_sar_exit_shadow.py`` locks the two implementations
together on shared fixtures, so a future edit to either side fails CI.

R normalization: both arms divide by the **live** ``sl_distance``, so the trail
is scored in the same risk units as the stop it would replace.  A trail that
rides further must still pay more R per unit of risk taken to win the A/B.

Cost discipline: stamps are O(1) in-memory appends on suppression/emission
events only (never per scanned symbol); candles are the already-warm in-memory
15m arrays; classification batches on the existing 5-min audit loop.  No
network read, no Firestore read, nothing on a hot path.

Observe-only end to end: evaluator geometry ownership (B7) is untouched, no
record here can reach the signal queue or the position FSM, and *activating* a
SAR exit live remains a separate dark-first, owner-signed change.
"""
from __future__ import annotations

import os
import threading
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple

from src.suppression_audit import (
    EXIT_STATIC,
    EXIT_TRAILING,
    WOULD_EXPIRE,
    WOULD_LOSE,
    WOULD_WIN,
    SuppressedCandidateStore,
    stamp_candidate,
)
from src.utils import get_logger

log = get_logger("sar_exit_shadow")

# Arm suffixes.  The edge matrix keys on the suffixed strategy name, so each arm
# appears as its own row per context cell.  Registered in
# ``geometry_ab._VARIANT_SUFFIXES`` so the allocator can never *recommend* one —
# a measurement arm is evidence about how to exit a strategy, not an
# activatable strategy.
SARBASE_SUFFIX = "@SARBASE"
SAREXIT_SUFFIX = "@SAREXIT"

GATE_SARBASE = "sar_exit_shadow:base"
GATE_SAREXIT = "sar_exit_shadow:trail"

_DEFAULT_PATH: str = os.getenv("SAR_EXIT_SHADOW_PATH", "data/sar_exit_candidates.json")
_MAX_RECORDS: int = int(os.getenv("SAR_EXIT_SHADOW_MAX_RECORDS", "4000"))

# Exit reasons recorded on the trail arm (diagnostic only).
REASON_TRAIL = "trail"      # the moving stop caught price
REASON_WINDOW = "window"    # never stopped out — marked to the window's close


# ---------------------------------------------------------------------------
# Pure SAR math — ported verbatim from scripts/exit_method_backtest.py
# ---------------------------------------------------------------------------


def parabolic_sar(
    highs: Sequence[float], lows: Sequence[float], step: float, max_step: float
) -> List[Optional[float]]:
    """Parabolic SAR (Wilder). Returns the stop-and-reverse level per bar.

    Verbatim port of the bake-off script's implementation — see the module
    docstring for why this is a copy and not a re-derivation.
    """
    n = len(highs)
    out: List[Optional[float]] = [None] * n
    if n < 2:
        return out
    up = highs[1] >= highs[0]
    af = step
    ep = highs[1] if up else lows[1]
    sar = lows[0] if up else highs[0]
    out[1] = sar
    for i in range(2, n):
        sar = sar + af * (ep - sar)
        if up:
            sar = min(sar, lows[i - 1], lows[i - 2])
            if lows[i] < sar:
                up = False
                sar = ep
                ep = lows[i]
                af = step
            else:
                if highs[i] > ep:
                    ep = highs[i]
                    af = min(af + step, max_step)
        else:
            sar = max(sar, highs[i - 1], highs[i - 2])
            if highs[i] > sar:
                up = True
                sar = ep
                ep = highs[i]
                af = step
            else:
                if lows[i] < ep:
                    ep = lows[i]
                    af = min(af + step, max_step)
        out[i] = sar
    return out


def simulate_sar_exit(
    *,
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    opens: Optional[Sequence[float]],
    entry_idx: int,
    entry: float,
    side: str,
    step: float,
    max_step: float,
    max_bars: int,
    bar_minutes: float,
) -> Optional[Dict[str, Any]]:
    """Replay one signal from ``entry_idx`` under a SAR-trailing-only exit.

    Pure.  Returns ``{exit_price, exit_reason, mfe_pct, hold_min, exit_idx}``
    or ``None`` when the inputs can't support an honest replay (no SAR level at
    entry, degenerate entry, bad side).  A pair that cannot compute its trail
    arm is skipped entirely, never guessed.

    The exit-fill model is the bake-off's: when a bar *gaps through* the stop,
    the fill is the bar's open (worse than the stop), not the stop itself.
    Without opens the stop price is used, which is the optimistic read — hence
    the caller supplies opens whenever the data store has them.
    """
    try:
        is_long = str(side or "").upper() == "LONG"
        if str(side or "").upper() not in ("LONG", "SHORT"):
            return None
        entry = float(entry or 0.0)
        n = min(len(highs), len(lows), len(closes))
        if entry <= 0 or n < 3 or entry_idx < 0 or entry_idx >= n:
            return None
        series = parabolic_sar(highs, lows, step, max_step)
        if series[entry_idx] is None:
            return None

        # The walk is bounded to the measurement window; `end` is exclusive.
        end = n if max_bars <= 0 else min(n, entry_idx + 1 + int(max_bars))
        best_fav = entry
        exit_price: Optional[float] = None
        exit_idx: Optional[int] = None
        reason = REASON_WINDOW

        for i in range(entry_idx, end):
            stop_level = series[i]
            if stop_level is None:
                continue
            # No same-bar exit: the entry bar's SAR is the level the trade
            # starts behind, not a level it can already have breached.
            if i > entry_idx:
                bar_open = (
                    float(opens[i])
                    if opens is not None and i < len(opens) and float(opens[i] or 0.0) > 0
                    else None
                )
                if is_long and float(lows[i]) <= stop_level:
                    exit_price = (
                        bar_open
                        if bar_open is not None and bar_open < stop_level
                        else stop_level
                    )
                    exit_idx = i
                    reason = REASON_TRAIL
                    break
                if (not is_long) and float(highs[i]) >= stop_level:
                    exit_price = (
                        bar_open
                        if bar_open is not None and bar_open > stop_level
                        else stop_level
                    )
                    exit_idx = i
                    reason = REASON_TRAIL
                    break
            if is_long:
                best_fav = max(best_fav, float(highs[i]))
            else:
                best_fav = min(best_fav, float(lows[i]))

        if exit_price is None:
            exit_idx = end - 1
            exit_price = float(closes[exit_idx])
            reason = REASON_WINDOW
        if exit_price <= 0:
            return None

        if is_long:
            mfe = max(0.0, (best_fav - entry) / entry * 100.0)
        else:
            mfe = max(0.0, (entry - best_fav) / entry * 100.0)
        hold_min = max(0.0, float((exit_idx or entry_idx) - entry_idx) * float(bar_minutes))
        return {
            "exit_price": float(exit_price),
            "exit_reason": reason,
            "mfe_pct": float(mfe),
            "hold_min": hold_min,
            "exit_idx": int(exit_idx if exit_idx is not None else entry_idx),
        }
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.simulate", exc)
        return None


# ---------------------------------------------------------------------------
# Pair ledger — dedicated store so trail volume can't evict gate records
# ---------------------------------------------------------------------------

_sar_store: Optional[SuppressedCandidateStore] = None
_store_lock = threading.Lock()

# Per-(symbol, setup, side) pair cooldown.  ``None`` sentinel, never 0.0 — a
# 0.0 default swallows every stamp for the first COOLDOWN seconds after boot,
# because monotonic() starts near zero on a fresh host (bug class caught in S53
# and re-checked here).
_last_pair_stamp: Dict[Tuple[str, str, str], float] = {}


def get_sar_store() -> SuppressedCandidateStore:
    global _sar_store
    with _store_lock:
        if _sar_store is None:
            _sar_store = SuppressedCandidateStore(
                persist_path=_DEFAULT_PATH, maxlen=_MAX_RECORDS
            )
        return _sar_store


def is_sar_variant(strategy: str) -> bool:
    """True for ``X@SARBASE`` / ``X@SAREXIT`` measurement rows."""
    s = str(strategy or "")
    return s.endswith(SARBASE_SUFFIX) or s.endswith(SAREXIT_SUFFIX)


def stamp_sar_pair(
    *,
    symbol: str,
    channel: str,
    setup_class: str,
    side: str,
    entry: float,
    stop_loss: float,
    tp1: float,
    confidence: float = 0.0,
    context_key: str = "",
    regime: str = "",
    valid_for_minutes: float = 0.0,
    provenance: str = "",
    store: Optional[SuppressedCandidateStore] = None,
    now_mono: Optional[float] = None,
) -> bool:
    """Stamp the SARBASE/SAREXIT counterfactual pair for one candidate (fail-open).

    Returns ``True`` when the pair was stamped, else ``False`` (cooldown or bad
    geometry).  Both arms always stamp together — a lone arm biases the A/B.

    ``provenance`` records where the candidate stood at stamp time —
    ``SUPPRESSED`` (a scanner gate killed it) or ``ENQUEUED`` (it passed every
    scanner gate and the queue accepted it).  Both arms of a pair carry the
    same value (they are one candidate).

    **This function never writes EMITTED.**  Whether a queued candidate is
    actually delivered is not known here: the router applies its own gate
    layer afterwards and drops most of what it dequeues.  ``EMITTED`` is
    written only by :func:`promote_to_emitted`, from the router, after
    confirmed delivery — which is what lets the measurement answer "would this
    exit have improved the signals we SENT" separately from "…every candidate
    we considered".  Only the former can justify changing what users receive.

    Note the trail arm carries the live SL/TP1 **as levels it never consults**:
    they are stored so ``sl_distance`` (the shared R denominator) and the
    control arm's geometry travel with the record.  The trail's own exit comes
    entirely from the SAR walk at classification time.
    """
    try:
        setup = str(setup_class or "").strip()
        if not setup or is_sar_variant(setup):
            return False
        entry = float(entry or 0.0)
        stop_loss = float(stop_loss or 0.0)
        tp1 = float(tp1 or 0.0)
        if entry <= 0 or stop_loss <= 0 or tp1 <= 0 or abs(entry - stop_loss) <= 0:
            return False
        side_u = str(side or "").upper()
        if side_u not in ("LONG", "SHORT"):
            return False
        prov = str(provenance or "")
        # The cooldown is keyed by provenance so a *suppressed* stamp cannot
        # swallow a real signal's stamp minutes later (2026-07-25, owner-caught):
        # suppressed candidates outnumber emissions by orders of magnitude, so
        # one shared (symbol, setup, side) budget thinned the emitted sample
        # silently and non-randomly.
        #
        # The EMITTED cooldown bypass that shipped alongside that fix has been
        # REMOVED, because its premise was false. It reasoned that "an emission
        # is a discrete dispatch event, and duplicates are already prevented
        # upstream by dispatch_cooldown" — but this stamp never fired on a
        # dispatch. It fired when ``signal_queue.put`` accepted the candidate,
        # which the router then usually rejected. So the bypass let every
        # re-detection of a persisting setup stamp as EMITTED and *amplified*
        # the very mismatch it was meant to fix (one WLFIUSDT setup produced 5
        # "emitted" rows at an identical entry inside 6.7h).
        #
        # EMITTED now arrives only via :func:`promote_to_emitted`, called by the
        # router after confirmed delivery — at which point the "discrete
        # dispatch event" premise is finally true. The stamp path handles
        # SUPPRESSED and ENQUEUED, and both take the cooldown: both are
        # scan-cycle events on a candidate that may persist for many cycles.
        cd_key = (str(symbol or ""), setup, side_u, prov)
        mono = time.monotonic() if now_mono is None else float(now_mono)
        from config import SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC

        last = _last_pair_stamp.get(cd_key)
        if last is not None and mono - last < SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC:
            return False
        target = store or get_sar_store()

        def _stamp_arm(gate: str, suffix: str, exit_model: str):
            return stamp_candidate(
                gate_name=gate,
                symbol=str(symbol or ""),
                channel=str(channel or ""),
                setup_class=f"{setup}{suffix}",
                side=side_u,
                entry=entry,
                stop_loss=stop_loss,
                tp1=tp1,
                confidence=float(confidence or 0.0),
                context_key=context_key or "",
                regime=regime or "",
                valid_for_minutes=float(valid_for_minutes or 0.0),
                exit_model=exit_model,
                provenance=str(provenance or ""),
                store=target,
            )

        # Both arms stamp together or not at all — a lone arm biases the A/B.
        if _stamp_arm(GATE_SARBASE, SARBASE_SUFFIX, EXIT_STATIC) is None:
            return False
        if _stamp_arm(GATE_SAREXIT, SAREXIT_SUFFIX, EXIT_TRAILING) is None:
            return False
        _last_pair_stamp[cd_key] = mono
        return True
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.stamp_pair", exc)
        return False


def promote_to_emitted(
    *,
    symbol: str,
    setup_class: str,
    side: str,
    entry: float,
    store: Optional[SuppressedCandidateStore] = None,
    max_age_sec: Optional[float] = None,
) -> int:
    """Mark a candidate's arms EMITTED after the router confirmed delivery.

    This is the only writer of ``PROVENANCE_EMITTED`` (2026-07-25 fix). The
    scanner stamps ``ENQUEUED`` when the queue accepts a candidate; the router
    calls this once it has actually posted the signal. Everything that never
    gets here stays ``ENQUEUED``, which is the honest label for "we considered
    it, we queued it, and our own routing caps dropped it".

    Returns the number of arm records promoted — 2 on the normal path (both
    ``@SARBASE`` and ``@SAREXIT``), 0 when no matching stamp is in the window.
    A 0 is not an error: the stamp cooldown may legitimately have throttled a
    re-detected setup, and the earlier arms for that same candidate are already
    in the ledger.

    Fail-open: a measurement re-label must never break dispatch.
    """
    try:
        setup = str(setup_class or "").strip()
        if not setup or is_sar_variant(setup):
            return 0
        from src.suppression_audit import (
            PROVENANCE_EMITTED,
            PROVENANCE_ENQUEUED,
        )

        if max_age_sec is None:
            # Generous relative to the scanner→router hop (sub-second in
            # practice) but bounded so a promotion can never reach a candidate
            # from an earlier, unrelated detection of the same setup.
            from config import SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC
            max_age_sec = max(300.0, float(SAR_EXIT_SHADOW_STAMP_COOLDOWN_SEC))
        target = store or get_sar_store()
        return target.promote_provenance(
            symbol=str(symbol or ""),
            side=str(side or ""),
            # Both arms share the base setup as their prefix, so one call
            # promotes the pair together.
            setup_prefix=setup,
            entry=float(entry or 0.0),
            from_provenance=PROVENANCE_ENQUEUED,
            to_provenance=PROVENANCE_EMITTED,
            max_age_sec=float(max_age_sec),
        )
    except Exception as exc:
        from src import fail_open
        fail_open.record("sar_exit_shadow.promote_to_emitted", exc)
        return 0


# ---------------------------------------------------------------------------
# Trail classifier — the hook handed to SuppressedCandidateStore.classify_pending
# ---------------------------------------------------------------------------


def classify_sar_record(
    record: Dict[str, Any], ohlc: Dict[str, List[float]]
) -> Optional[Dict[str, Any]]:
    """Resolve one ``@SAREXIT`` record by walking its SAR trail (pure).

    ``ohlc`` carries a pre-entry **warmup prefix** so the SAR has converged by
    the time the trade starts; ``entry_index`` says where the trade begins.
    Without that prefix the first bars of every trade would be measured against
    a SAR still seeded from its own first two bars, which is not the indicator
    the bake-off measured.

    ``post_price_max`` / ``post_price_min`` are computed over the **post-entry**
    slice only, so the warmup bars never leak into the recorded excursion.
    """
    from config import (
        SAR_EXIT_SHADOW_BAR_MINUTES,
        SAR_EXIT_SHADOW_MAX_STEP,
        SAR_EXIT_SHADOW_STEP,
        SAR_EXIT_SHADOW_WINDOW_BARS,
    )

    highs = ohlc.get("high")
    lows = ohlc.get("low")
    closes = ohlc.get("close")
    opens = ohlc.get("open")
    if highs is None or lows is None or closes is None:
        return None
    if len(highs) == 0 or len(lows) == 0 or len(closes) == 0:
        return None
    entry_idx = int(ohlc.get("entry_index") or 0)  # type: ignore[arg-type]
    result = simulate_sar_exit(
        highs=highs,
        lows=lows,
        closes=closes,
        opens=opens,
        entry_idx=entry_idx,
        entry=float(record.get("entry") or 0.0),
        side=str(record.get("side") or ""),
        step=SAR_EXIT_SHADOW_STEP,
        max_step=SAR_EXIT_SHADOW_MAX_STEP,
        max_bars=SAR_EXIT_SHADOW_WINDOW_BARS,
        bar_minutes=SAR_EXIT_SHADOW_BAR_MINUTES,
    )
    if result is None:
        return None

    entry = float(record.get("entry") or 0.0)
    exit_price = float(result["exit_price"])
    is_long = str(record.get("side") or "").upper() == "LONG"
    move = (exit_price - entry) if is_long else (entry - exit_price)
    # The label stays in the ledger's shared vocabulary so the edge matrix and
    # every existing consumer read it without a special case.  For a trailing
    # arm it is the *sign* of the realized exit, not a TP1-vs-SL race:
    # WOULD_EXPIRE means the trail never fired inside the window.
    if str(result["exit_reason"]) == REASON_WINDOW:
        label = WOULD_EXPIRE
    else:
        label = WOULD_WIN if move > 0 else WOULD_LOSE

    post_high = max(float(h) for h in highs[entry_idx:]) if len(highs) > entry_idx else 0.0
    post_low = min(float(low) for low in lows[entry_idx:]) if len(lows) > entry_idx else 0.0
    return {
        "classification": label,
        "trail_exit_price": exit_price,
        "trail_mfe_pct": float(result["mfe_pct"]),
        "trail_hold_min": float(result["hold_min"]),
        "trail_exit_reason": str(result["exit_reason"]),
        "post_price_max": post_high,
        "post_price_min": post_low,
        "post_price_final": float(closes[-1]),
    }


# ---------------------------------------------------------------------------
# Rollup for ops / the truth report
# ---------------------------------------------------------------------------


def summarize_sar_exit(matrix: Dict[str, Dict], *, min_sample: int = 15) -> List[Dict]:
    """Per-strategy live-geometry-vs-SAR-trail rollup from edge-matrix cells (pure).

    Pools each arm's cells across contexts (sample-weighted) and names a leader
    only when BOTH arms clear ``min_sample`` — an A/B with one thin arm is
    MEASURING, not evidence.  This is the table the owner's activation decision
    reads, so "not enough data yet" has to be a first-class answer, never an
    accidental 0-sample "SAR wins".
    """
    pooled: Dict[str, Dict[str, Dict[str, float]]] = {}
    for cell in (matrix or {}).values():
        strategy = str(cell.get("strategy", ""))
        if strategy.endswith(SAREXIT_SUFFIX):
            arm = "sar"
        elif strategy.endswith(SARBASE_SUFFIX):
            arm = "base"
        else:
            continue
        base = strategy[: -len(SAREXIT_SUFFIX if arm == "sar" else SARBASE_SUFFIX)]
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

        base_arm = _arm("base")
        sar_arm = _arm("sar")
        measured = base_arm["n"] >= min_sample and sar_arm["n"] >= min_sample
        delta = sar_arm["avg_r"] - base_arm["avg_r"]
        rows.append(
            {
                "strategy": base,
                "base": base_arm,
                "sar": sar_arm,
                "delta_r": delta if measured else None,
                "leader": (
                    ("SAR" if delta > 0 else "LIVE" if delta < 0 else "TIE")
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
