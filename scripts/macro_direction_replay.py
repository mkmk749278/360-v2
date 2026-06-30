#!/usr/bin/env python3
"""Replay the directional macro-regime gate over BTC's real weekly history.

THE PROOF (owner-requested, S39).  Before the directional counter-trend-long gate
touches the live engine, show it would have flipped the right way at the real cycle
turns — DECLINE on the 2022 fall, RECOVERY/BULL on the 2023 climb — and that it does
so EARLIER than the static "200-week MA" line did, on both ends.  That is the whole
fix: direction (slope + price-vs-fast-MA + structure), not which side of a fence.

This walks BTC weekly closes from 2018 to now; at each week it computes:
  * the directional regime via the SAME engine function the scanner will use
    (``src.btc_state.macro_direction``) — single source of truth, no drift, and
  * the static signal (price vs its 200-week SMA) for contrast.

Then it prints the regime-run timeline and a head-to-head on the two cycle turns.

Read-only diagnostic: one public Binance GET for BTC weekly klines, no engine state.
Run where Binance is reachable (the VPS):

    docker exec 360scalp-v2-engine python scripts/macro_direction_replay.py
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from typing import List, Optional, Tuple

# Single source of truth — the exact classifier the engine gate will call.
sys.path.insert(0, ".")
from src.btc_state import _sma, macro_direction  # noqa: E402

_SPOT = "https://api.binance.com/api/v3/klines"
_WEEK_MS = 7 * 24 * 3600 * 1000


def _get(url: str, timeout: float = 30.0):
    req = urllib.request.Request(url, headers={"User-Agent": "macro-replay/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_weekly(symbol: str, start_ms: int) -> Tuple[List[int], List[float]]:
    """All weekly (open_ms, close) for symbol from start_ms to now (paginated)."""
    out_ms: List[int] = []
    out_close: List[float] = []
    cur = start_ms
    now = int(time.time() * 1000)
    while cur <= now:
        url = f"{_SPOT}?symbol={symbol}&interval=1w&startTime={cur}&limit=1000"
        rows = _get(url)
        if not rows:
            break
        for r in rows:
            out_ms.append(int(r[0]))
            out_close.append(float(r[4]))
        last = int(rows[-1][0])
        if last + _WEEK_MS <= cur:
            break
        cur = last + _WEEK_MS
        if len(rows) < 1000:
            break
        time.sleep(0.15)
    return out_ms, out_close


def _ymd(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="BTCUSDT")
    ap.add_argument("--fast", type=int, default=50, help="fast MA period (weeks)")
    ap.add_argument("--slow", type=int, default=200, help="slow MA period (weeks)")
    ap.add_argument("--start", default="2018-01-01", help="history start (YYYY-MM-DD)")
    args = ap.parse_args()

    start_ms = int(datetime.strptime(args.start, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
    print(f"Fetching {args.symbol} weekly from {args.start} …")
    ms, closes = fetch_weekly(args.symbol, start_ms)
    if len(closes) < args.fast + 25:
        print(f"Not enough weekly history ({len(closes)} candles). Aborting.", file=sys.stderr)
        return 1
    print(f"  {len(closes)} weekly candles ({_ymd(ms[0])} → {_ymd(ms[-1])})\n")

    # Walk each week point-in-time (no look-ahead): regime on closes[:i+1].
    rows = []  # (date, regime, suppressed, price_vs_slow)
    for i in range(len(closes)):
        window = closes[: i + 1]
        res = macro_direction(window, fast_period=args.fast, slow_period=args.slow)
        slow = _sma(window, args.slow)
        if slow is None:
            pvs = "—"
        else:
            pvs = "above200w" if closes[i] >= slow else "below200w"
        rows.append((ms[i], res["regime"], bool(res["longs_suppressed"]), pvs))

    # ---- Regime-run timeline (collapse consecutive same-regime weeks) ----
    print("=== REGIME TIMELINE (directional gate) ===")
    print(f"{'from':12} {'to':12} {'regime':10} {'weeks':>5}  longs")
    run_start = 0
    for i in range(1, len(rows) + 1):
        if i == len(rows) or rows[i][1] != rows[run_start][1]:
            d0, d1 = _ymd(rows[run_start][0]), _ymd(rows[i - 1][0])
            reg = rows[run_start][1]
            longs = "OFF" if rows[run_start][2] else "on"
            print(f"{d0:12} {d1:12} {reg:10} {i - run_start:>5}  {longs}")
            run_start = i

    # ---- Head-to-head on the two cycle turns ----
    def first_where(pred, lo_ms, hi_ms) -> Optional[str]:
        lo = int(datetime.strptime(lo_ms, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
        hi = int(datetime.strptime(hi_ms, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1000)
        for (m, reg, sup, pvs) in rows:
            if lo <= m <= hi and pred(reg, sup, pvs):
                return _ymd(m)
        return None

    print("\n=== THE TWO CYCLE TURNS — directional gate vs the static 200-line ===")
    fall_gate = first_where(lambda reg, sup, pvs: sup, "2021-11-01", "2023-01-01")
    fall_line = first_where(lambda reg, sup, pvs: pvs == "below200w", "2021-11-01", "2023-06-01")
    print(f"① FALL  — gate first switched longs OFF : {fall_gate or 'n/a'}")
    print(f"         price first closed below 200w   : {fall_line or 'n/a'}")
    rec_gate = first_where(lambda reg, sup, pvs: not sup and reg in ("RECOVERY", "BULL"), "2022-11-01", "2024-06-01")
    rec_line = first_where(lambda reg, sup, pvs: pvs == "above200w", "2022-11-01", "2024-06-01")
    print(f"② RECOVERY — gate first switched longs ON: {rec_gate or 'n/a'}")
    print(f"           price first reclaimed 200w    : {rec_line or 'n/a'}")

    print("\n--- ACCEPTANCE ---")
    print("Pass iff: the gate switched longs OFF during the 2022 fall and back ON during the")
    print("2023 recovery, and did each at least as early as the static 200-week line.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
