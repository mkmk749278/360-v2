"""Reconcile every recorded SAR arm against Binance's own bars.

**The gap this closes.** ``sar_live_shadow`` computes a stop inside the monitor
loop, off the engine's in-process candle store, and writes it to
``sar_live_arms_v1.json``. Three things had been verified about that number and
one had not:

* the indicator arithmetic — ``parabolic_sar`` is bit-exact against an
  independent Wilder implementation (``tests/test_sar_chart_contract.py`` pins
  it across three repos);
* the recorded fills — ``pnl_level_pct`` reconciles from ``entry``/``fill_level``
  on every row, and no fill has ever been *better* than the parked level;
* the width — the levels sit inside the range real SAR produces on these
  instruments.

None of that answers **"is the level this arm parked the level SAR actually had
on those bars"**. That question needs the exchange's bars for the arm's own
symbol and window, which is exactly what the engine's store is a *cache* of. A
stale bucket, a gap-fill that over-fetched, a re-seed that replaced a bucket
mid-walk — every one of those produces an arithmetically perfect SAR over the
wrong inputs, and every check above passes while it happens. That is the seam
this script stands on.

**Why it lives here and not in ops.** It needs `fapi.binance.com`, which
answers the VPS and 451s a datacenter IP, and it needs the ledger. Run it as::

    docker compose exec engine python /app/scripts/reconcile_sar_arms.py
    docker compose exec engine python /app/scripts/reconcile_sar_arms.py \
        --symbol BICOUSDT --limit 40 --verbose

**The one hard problem, and why the answer is a refusal rather than a number.**
Parabolic SAR is path-dependent: it carries an acceleration factor and an
extreme point forward, so its level at bar *k* depends on where the walk
*started*. The engine walks a bounded window; this script fetches its own. Two
different start points can produce two different levels at the same bar, and
neither is wrong. So a naive diff would report mismatches that are artefacts of
the seed.

The script therefore recomputes each level from several independent start
offsets (``--seeds``) and asks whether they agree *with each other* first:

* they agree → the level at that bar is seed-independent, the comparison is
  meaningful, and a disagreement with the ledger is a real finding;
* they disagree → the bar sits too close to its own warmup for any
  reconstruction to be authoritative, and the row is refused as
  ``seed_sensitive`` and counted. It is **not** scored as a mismatch, and it is
  **not** scored as a pass.

That is this repo's ``a clamp is not a guard`` rule applied to a diagnostic:
where the input cannot support the claim, refuse the claim and name why, rather
than emit a confident number describing nothing. Every refusal reason below is
counted separately because each one has a different next move.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.sar_exit_shadow import parabolic_sar_live  # noqa: E402

# Wilder's defaults, and the values `sar_live_shadow` is configured with. Read
# from config so this script cannot drift from the engine it is auditing.
try:
    from config import (  # noqa: E402
        BINANCE_FUTURES_REST_BASE,
        SAR_EXIT_SHADOW_STEP,
        SAR_EXIT_SHADOW_MAX_STEP,
    )
except Exception:  # pragma: no cover - config import is not worth failing on
    BINANCE_FUTURES_REST_BASE = "https://fapi.binance.com"
    SAR_EXIT_SHADOW_STEP, SAR_EXIT_SHADOW_MAX_STEP = 0.02, 0.2

DEFAULT_LEDGER = os.getenv("SAR_LIVE_SHADOW_PATH", "data/sar_live_arms_v1.json")

#: Bar width in milliseconds, per timeframe the arms are measured on.
_TF_MS = {"1m": 60_000, "5m": 300_000, "15m": 900_000, "1h": 3_600_000}

#: A level is "the same" if it agrees to this many percent of its own value.
#: Float noise across two independent walks is ~1e-10; 1e-6 is four orders of
#: magnitude of headroom and still far tighter than any tick size in the book.
TOL_PCT = 1e-6

#: Bars of history fetched before the arm's own window, so the reconstruction
#: has a real warmup rather than starting on the entry bar.
LEAD_BARS = 400

#: Start offsets (in bars, from the front of the fetched window) used to test
#: whether a level is seed-independent. Spread deliberately wide: two nearby
#: seeds agree trivially and would prove nothing.
DEFAULT_SEEDS = (0, 60, 120, 200)

#: Bars a seed must have ahead of the target before its level is comparable.
#:
#: **Measured, not guessed** (2026-08-09). Sweeping this constant over a noisy
#: random-walk series and counting target bars where three independent seeds
#: disagree: 13/177 at 3 bars, 11/175 at 5, 6/170 at 10, and **0/160 at 20, 25
#: and 30**. Smooth trending and V-shaped series never disagreed at any depth.
#: The reason is structural rather than lucky — every SAR flip resets both the
#: extreme point and the acceleration factor, so a walk forgets its seed
#: entirely at the first reversal, and reversals arrive every few tens of bars.
#:
#: 30 is therefore well inside the converged region rather than at its edge. The
#: practical consequence is that ``seed_sensitive`` should be **rare to absent**
#: in a real run: it is insurance against a pathological window, not an expected
#: outcome, and a run reporting many of them is itself the finding.
MIN_SEED_WARMUP_BARS = 30

# Refusal reasons. Each is counted separately because the next move differs:
# a feed problem, a window problem and a warmup problem are three different
# things and pooling them into "could not check" is how a real fault hides.
R_NO_KLINES = "no_klines"                  # Binance returned nothing usable
R_BAR_MISSING = "bar_not_in_window"        # the arm's bar is not on the exchange grid we pulled
R_SHORT_WARMUP = "insufficient_warmup"     # not enough bars before the arm's bar to seed a walk
R_SEED_SENSITIVE = "seed_sensitive"        # reconstructions disagree with each other
R_NO_STOP = "no_parked_stop"               # arm never parked a SAR stop (geometry-governed, no handover)
R_NO_BAR_MS = "no_bar_timestamp"           # arm carries no last_bar_ms to anchor on


class _Refusal(Exception):
    """Raised with a named reason when a row cannot be checked at all."""

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.detail = detail


# --------------------------------------------------------------------------- #
# Binance
# --------------------------------------------------------------------------- #


def fetch_klines(
    symbol: str, interval: str, start_ms: int, end_ms: int, *, base: str, pause: float
) -> List[Tuple[int, float, float, float, float]]:
    """(open_time, open, high, low, close) for one symbol/timeframe window.

    Pages through Binance's 1500-bar limit. Returns [] on any transport error —
    the caller turns that into a named refusal rather than a mismatch, because
    "we could not ask" and "the answer differs" are different findings.
    """
    out: List[Tuple[int, float, float, float, float]] = []
    cursor = start_ms
    while cursor < end_ms:
        q = urllib.parse.urlencode(
            {
                "symbol": symbol,
                "interval": interval,
                "startTime": cursor,
                "endTime": end_ms,
                "limit": 1500,
            }
        )
        url = f"{base.rstrip('/')}/fapi/v1/klines?{q}"
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                rows = json.load(resp)
        except (urllib.error.URLError, ValueError, TimeoutError, OSError):
            return []
        if not rows:
            break
        for k in rows:
            out.append(
                (int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4]))
            )
        if len(rows) < 1500:
            break
        cursor = int(rows[-1][0]) + 1
        time.sleep(pause)
    # De-duplicate and sort. An unsorted or duplicated series silently corrupts
    # every SAR level after the offending bar — the same invariant
    # `_series_with_reason` refuses on engine-side, enforced here too because
    # this script is a second walker of the same kind of data.
    seen: Dict[int, Tuple[int, float, float, float, float]] = {}
    for row in out:
        seen[row[0]] = row
    return [seen[t] for t in sorted(seen)]


# --------------------------------------------------------------------------- #
# Reconstruction
# --------------------------------------------------------------------------- #


def _level_at(
    highs: Sequence[float], lows: Sequence[float], upto: int, step: float, max_step: float
) -> Optional[Tuple[bool, float]]:
    """SAR direction + the stop parked for the bar AFTER ``upto``.

    ``parabolic_sar_live`` projects one step past the end of the arrays it is
    given, which is precisely what the arm parks: the stop that the *next* bar
    could breach. Slicing to ``upto + 1`` and reading ``next_stop`` reproduces
    the arm's own call exactly, which is the point — this is a check of the
    inputs, not a second opinion on the arithmetic.
    """
    live = parabolic_sar_live(
        list(highs[: upto + 1]), list(lows[: upto + 1]), step, max_step
    )
    if live is None:
        return None
    return bool(live.up), float(live.next_stop)


def reconstruct(
    bars: Sequence[Tuple[int, float, float, float, float]],
    bar_ms: int,
    *,
    seeds: Sequence[int],
    step: float,
    max_step: float,
    min_warmup: int = MIN_SEED_WARMUP_BARS,
) -> Tuple[bool, float, int]:
    """The seed-independent SAR level parked after ``bar_ms``.

    Raises :class:`_Refusal` when the window cannot support the claim. Returns
    ``(up, level, n_seeds_agreeing)`` when every seed that could run agreed.

    ``min_warmup`` is a parameter rather than a constant read inline so the
    convergence claim behind :data:`MIN_SEED_WARMUP_BARS` stays falsifiable: the
    tests drive real SAR output below the threshold, where seeds genuinely
    disagree, and assert the refusal fires. A guard that cannot be made to
    trigger has not been tested, it has only been asserted.
    """
    times = [b[0] for b in bars]
    try:
        idx = times.index(int(bar_ms))
    except ValueError:
        raise _Refusal(R_BAR_MISSING, f"bar {bar_ms} not in the {len(bars)}-bar window")

    results: List[Tuple[bool, float]] = []
    for seed in seeds:
        if idx - seed < min_warmup:
            # Too little warmup ahead of the target for this seed's level to be
            # comparable. Skipped, and deliberately not counted as agreement.
            continue
        highs = [b[2] for b in bars[seed:]]
        lows = [b[3] for b in bars[seed:]]
        got = _level_at(highs, lows, idx - seed, step, max_step)
        if got is not None:
            results.append(got)
    if not results:
        raise _Refusal(R_SHORT_WARMUP, f"only {idx} bars precede the arm's bar")

    base_up, base_lvl = results[0]
    for up, lvl in results[1:]:
        if up != base_up or _pct_gap(lvl, base_lvl) > TOL_PCT:
            raise _Refusal(
                R_SEED_SENSITIVE,
                f"{len(results)} reconstructions disagree (spread "
                f"{max(_pct_gap(l, base_lvl) for _, l in results):.6f}%)",
            )
    return base_up, base_lvl, len(results)


def _pct_gap(a: float, b: float) -> float:
    if not b:
        return abs(a - b)
    return abs(a - b) / abs(b) * 100.0


# --------------------------------------------------------------------------- #
# Per-arm check
# --------------------------------------------------------------------------- #


def check_arm(
    arm: Dict[str, Any],
    bars: Sequence[Tuple[int, float, float, float, float]],
    *,
    seeds: Sequence[int],
    step: float,
    max_step: float,
) -> Dict[str, Any]:
    """Compare one arm's recorded stop against the exchange's own bars.

    **Which bar to project from depends on whether the arm is still open**, and
    getting this wrong would manufacture a mismatch on every closed row.
    ``step_arm`` parks ``live(0..i).next_stop`` after processing bar *i* without
    a breach; when bar *i* *does* breach, it closes and leaves the stop parked
    from bar *i-1* — the comment in the step loop says it outright, "the stop
    parked at the previous bar's close is what this bar could breach". So a
    running arm reconciles against its own ``last_bar_ms`` and a closed one
    against the bar before it.
    """
    recorded = arm.get("sar_stop")
    if recorded is None:
        raise _Refusal(R_NO_STOP, "arm parked no SAR stop")
    bar_ms = arm.get("last_bar_ms")
    if not bar_ms:
        raise _Refusal(R_NO_BAR_MS, "arm carries no last_bar_ms")

    closed = str(arm.get("status") or "") != "RUNNING"
    times = [b[0] for b in bars]
    target = int(bar_ms)
    if closed:
        try:
            i = times.index(target)
        except ValueError:
            raise _Refusal(R_BAR_MISSING, f"bar {target} not in window")
        if i == 0:
            raise _Refusal(R_SHORT_WARMUP, "closing bar is the first in the window")
        target = times[i - 1]

    up, level, n_seeds = reconstruct(
        bars, target, seeds=seeds, step=step, max_step=max_step
    )
    gap = _pct_gap(float(recorded), level)
    out: Dict[str, Any] = {
        "arm_id": arm.get("arm_id"),
        "symbol": arm.get("symbol"),
        "timeframe": arm.get("timeframe"),
        "status": arm.get("status"),
        "recorded": float(recorded),
        "rebuilt": level,
        "gap_pct": gap,
        "match": gap <= TOL_PCT,
        "dir_recorded": arm.get("sar_up"),
        "dir_rebuilt": up,
        "seeds": n_seeds,
    }
    # Direction is compared only when the arm recorded one. It is stamped on
    # every advance, so a blank here means the arm never advanced — an absence,
    # not a disagreement, and it must not be scored as either.
    rec_dir = arm.get("sar_up")
    out["dir_match"] = None if rec_dir is None else (bool(rec_dir) == up)

    # For a closed SAR-flip arm the exchange's bars can also settle the FILL:
    # the arm books the parked level, or the bar's open when price gapped
    # through it. Anything else is a fill the market did not offer.
    out["fill_verdict"] = None
    if arm.get("exit_reason") == "sar_flip" and arm.get("fill_level") is not None:
        try:
            j = times.index(int(bar_ms))
        except ValueError:
            j = -1
        if j >= 0:
            op = bars[j][1]
            is_long = str(arm.get("side") or "").upper() == "LONG"
            gapped = (op <= level) if is_long else (op >= level)
            expected = op if gapped else level
            out["fill_verdict"] = (
                "ok" if _pct_gap(float(arm["fill_level"]), expected) <= 1e-4 else "differs"
            )
            out["fill_expected"] = expected
    return out


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #


def load_arms(path: str) -> List[Dict[str, Any]]:
    """Every arm in the ledger, open and resolved, whatever envelope it uses.

    The store gained a schema envelope on 2026-08-02 and a reader that knew only
    the bare-list shape read two ops pages as UNAVAILABLE for four days. Both
    shapes are accepted here for the same reason.
    """
    with open(path, "r", encoding="utf-8") as fh:
        blob = json.load(fh)
    if isinstance(blob, list):
        return [a for a in blob if isinstance(a, dict)]
    if isinstance(blob, dict):
        out: List[Dict[str, Any]] = []
        for key in ("open", "arms", "resolved", "records"):
            v = blob.get(key)
            if isinstance(v, list):
                out += [a for a in v if isinstance(a, dict)]
            elif isinstance(v, dict):
                out += [a for a in v.values() if isinstance(a, dict)]
        return out
    return []


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--ledger", default=DEFAULT_LEDGER)
    ap.add_argument("--symbol", default="", help="only this symbol")
    ap.add_argument("--timeframe", default="", help="only this timeframe (5m/15m)")
    ap.add_argument("--limit", type=int, default=0, help="check at most N arms")
    ap.add_argument("--seeds", default=",".join(str(s) for s in DEFAULT_SEEDS))
    ap.add_argument("--base", default=BINANCE_FUTURES_REST_BASE)
    ap.add_argument("--pause", type=float, default=0.15, help="seconds between kline pages")
    ap.add_argument("--verbose", action="store_true", help="print every checked arm")
    ap.add_argument("--json", default="", help="also write the full result set here")
    args = ap.parse_args(argv)

    seeds = tuple(int(s) for s in str(args.seeds).split(",") if str(s).strip())
    step, max_step = SAR_EXIT_SHADOW_STEP, SAR_EXIT_SHADOW_MAX_STEP

    try:
        arms = load_arms(args.ledger)
    except FileNotFoundError:
        print(f"ledger not found: {args.ledger}", file=sys.stderr)
        return 2
    if args.symbol:
        arms = [a for a in arms if a.get("symbol") == args.symbol]
    if args.timeframe:
        arms = [a for a in arms if a.get("timeframe") == args.timeframe]
    arms = [a for a in arms if a.get("sar_stop") is not None and a.get("last_bar_ms")]
    arms.sort(key=lambda a: float(a.get("last_bar_ms") or 0), reverse=True)
    if args.limit:
        arms = arms[: args.limit]

    print(f"SAR arm reconciliation — {len(arms)} arm(s) with a parked stop")
    print(f"  ledger {args.ledger}")
    print(f"  source {args.base}  step={step} max_step={max_step}  seeds={list(seeds)}")
    print(f"  tolerance {TOL_PCT}% of the level\n")

    # One kline fetch per (symbol, timeframe), covering every arm that needs it.
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for a in arms:
        groups.setdefault((str(a.get("symbol")), str(a.get("timeframe"))), []).append(a)

    results: List[Dict[str, Any]] = []
    refusals: Counter = Counter()
    refusal_rows: List[Tuple[str, str, str]] = []

    for (symbol, tf), rows in sorted(groups.items()):
        width = _TF_MS.get(tf)
        if width is None:
            for r in rows:
                refusals[R_NO_KLINES] += 1
                refusal_rows.append((str(r.get("arm_id")), R_NO_KLINES, f"unknown tf {tf}"))
            continue
        lo = min(int(r["last_bar_ms"]) for r in rows) - LEAD_BARS * width
        hi = max(int(r["last_bar_ms"]) for r in rows) + 2 * width
        bars = fetch_klines(symbol, tf, lo, hi, base=args.base, pause=args.pause)
        if len(bars) < 40:
            for r in rows:
                refusals[R_NO_KLINES] += 1
                refusal_rows.append(
                    (str(r.get("arm_id")), R_NO_KLINES, f"{len(bars)} bars returned")
                )
            continue
        for r in rows:
            try:
                results.append(
                    check_arm(r, bars, seeds=seeds, step=step, max_step=max_step)
                )
            except _Refusal as exc:
                refusals[exc.reason] += 1
                refusal_rows.append((str(r.get("arm_id")), exc.reason, exc.detail))

    checked = len(results)
    matched = sum(1 for r in results if r["match"])
    dir_scored = [r for r in results if r["dir_match"] is not None]
    dir_ok = sum(1 for r in dir_scored if r["dir_match"])
    fills = [r for r in results if r["fill_verdict"] is not None]
    fills_ok = sum(1 for r in fills if r["fill_verdict"] == "ok")

    if args.verbose and results:
        print(f"{'arm':38s}{'tf':5s}{'recorded':>14s}{'rebuilt':>14s}{'gap%':>12s}  dir fill")
        for r in sorted(results, key=lambda x: -x["gap_pct"]):
            d = {True: "ok ", False: "BAD", None: "—  "}[r["dir_match"]]
            print(
                f"{str(r['arm_id'])[:37]:38s}{r['timeframe']:5s}"
                f"{r['recorded']:14.8f}{r['rebuilt']:14.8f}{r['gap_pct']:12.8f}  {d} "
                f"{r['fill_verdict'] or '—'}"
            )
        print()

    print("=== levels ===")
    print(f"  checked            {checked}")
    if checked:
        print(f"  match              {matched} ({matched / checked * 100:.1f}%)")
        print(f"  differ             {checked - matched}")
        gaps = sorted(r["gap_pct"] for r in results)
        print(
            f"  gap: median {statistics.median(gaps):.10f}%  "
            f"p90 {gaps[int(0.9 * (len(gaps) - 1))]:.10f}%  max {gaps[-1]:.10f}%"
        )
    print("\n=== direction ===")
    print(f"  comparable         {len(dir_scored)}")
    if dir_scored:
        print(f"  agree              {dir_ok} ({dir_ok / len(dir_scored) * 100:.1f}%)")
    print("\n=== sar_flip fills (was the booked price on offer?) ===")
    print(f"  comparable         {len(fills)}")
    if fills:
        print(f"  on offer           {fills_ok} ({fills_ok / len(fills) * 100:.1f}%)")

    total_refused = sum(refusals.values())
    print(f"\n=== refused ({total_refused}) — not scored either way ===")
    if not refusals:
        print("  none")
    for reason, n in refusals.most_common():
        print(f"  {reason:22s} {n}")
    if args.verbose and refusal_rows:
        print()
        for arm_id, reason, detail in refusal_rows[:40]:
            print(f"  {arm_id[:40]:41s}{reason:22s}{detail}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "checked": results,
                    "refusals": dict(refusals),
                    "refusal_rows": refusal_rows,
                    "tolerance_pct": TOL_PCT,
                    "seeds": list(seeds),
                },
                fh,
                indent=2,
            )
        print(f"\nwrote {args.json}")

    # Exit non-zero only on a real disagreement. A refusal is not a failure —
    # it is the script declining to answer, which is the whole point of naming
    # them, and a CI-ish caller must be able to tell the two apart.
    bad = (checked - matched) + (len(dir_scored) - dir_ok) + (len(fills) - fills_ok)
    return 1 if bad else 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
