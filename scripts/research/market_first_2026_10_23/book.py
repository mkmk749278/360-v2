#!/usr/bin/env python3
"""Apply the live book's admission rules to the replayed candidates.

    python scripts/research/market_first_2026_10_23/book.py --replay DIR --out book.csv

replay.py records every candidate an evaluator produced on every bar. Live,
most of those never reach a subscriber, for reasons that depend on the whole
book rather than one symbol. In time order, a candidate is kept only if:

  * the symbol has no active signal (the router's correlation lock);
  * the symbol has not enqueued in the last 600 s (SIGNAL_SCAN_COOLDOWN_SECONDS);
  * its (setup, direction) holds fewer than 3 active signals across the book
    (same-direction throttle, PER_PATH mode, budget 3);
  * its pre-penalty composite score is at least --min-score (default 65, the
    scanner's floor; replay.py mirrors the scorer).

Same-bar candidates on one symbol keep the evaluator dispatch order, so the
first one wins, as it does in the scanner. Not applied: the scoring floor, the
post-evaluator gates and the staleness checks, which the replay cannot see.
"""
from __future__ import annotations

import argparse
import glob
import os

import pandas as pd

SCAN_COOLDOWN_MS = 600_000
PER_PATH_BUDGET = 3
FEE_PCT = 0.07
RESOLVED = {"SL_HIT", "TP1_HIT", "BREAKEVEN_EXIT", "TIMEOUT"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--replay", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-score", type=float, default=65.0)
    a = ap.parse_args()
    frames = []
    for p in sorted(glob.glob(os.path.join(a.replay, "*.csv"))):
        d = pd.read_csv(p)
        if len(d):
            d["seq"] = range(len(d))
            frames.append(d)
    c = pd.concat(frames, ignore_index=True)
    c = c[c.outcome.isin(RESOLVED) & (c.score >= a.min_score)].sort_values(["t_ms", "symbol", "seq"], kind="stable")

    active_until: dict = {}   # symbol -> exit_ms of its active signal
    last_enq: dict = {}       # symbol -> t_ms of last enqueue
    path_active: dict = {}    # (setup, direction) -> list of exit_ms
    keep = []
    for r in c.itertuples(index=False):
        t = r.t_ms
        if active_until.get(r.symbol, 0) > t:
            continue
        if t - last_enq.get(r.symbol, -10**15) < SCAN_COOLDOWN_MS:
            continue
        key = (r.setup, r.direction)
        live = [e for e in path_active.get(key, []) if e > t]
        if len(live) >= PER_PATH_BUDGET:
            path_active[key] = live
            continue
        live.append(r.exit_ms)
        path_active[key] = live
        active_until[r.symbol] = r.exit_ms
        last_enq[r.symbol] = t
        keep.append(r)
    b = pd.DataFrame(keep)
    b["net_pct"] = b.pnl_pct - FEE_PCT
    b["entry_time"] = pd.to_datetime(b.t_ms, unit="ms", utc=True)
    b.to_csv(a.out, index=False)
    print(f"candidates {len(c)}  kept {len(b)}")


if __name__ == "__main__":
    main()
