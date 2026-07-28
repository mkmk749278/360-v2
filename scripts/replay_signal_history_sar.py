#!/usr/bin/env python3
"""Replay a ``signal_history`` export under the SAR exit arm, on real candles.

Why this exists (2026-07-28, owner ask). The SAR ledger cannot answer whether a
SAR exit beats ours *for users*: in an 8.6h window it held 467 rows of which
**5** were delivered, 2 closed, and ``delta_r`` was empty on all 467 — the A/B
had n=0. Meanwhile ``signal_history`` holds hundreds of signals the router
actually delivered, every one closed and tracked forward in real time. That is
the population an adoption decision needs, and it already exists.

So: take delivered signals, keep entry / SL / TP1 / direction / dispatch time,
and replay them through the engine's **own** ``simulate_sar_exit``. Not a
re-derivation — this imports the live function, so a divergence between what
this reports and what the arm stamps is impossible by construction.

**This is reconstruction, not record.** Every caveat that applies to the Profit
tab applies here: counterfactuals are optimistic (~0.38R measured on MTP), a
replayed exit never paid a real spread, and nothing here belongs on
``/track-record``. It informs an adoption decision; it does not make one.

Two honesty features worth knowing about:

* ``--compare-old-fill`` re-runs each signal with the pre-2026-07-28 fill (the
  published SAR level, which on a reversal bar is the prior trend's extreme, so
  the exit filled at the bar's open). That bug flattered each trail exit by a
  mean +0.222% over 820 real flips. The flag exists to show the correction's
  size on *your* signals rather than on a synthetic.
* Coverage is reported, always. A symbol whose candles cannot be fetched, or a
  dispatch that lands outside the returned bars, is **refused and counted** —
  never clamped to a nearby bar. A replay that silently drops a third of the
  population and prints a mean is the failure mode this script is built against.

Usage
-----
    # On the VPS (futures — the venue the signals actually traded on):
    python scripts/replay_signal_history_sar.py history.json

    # Anywhere futures is geo-blocked, spot mirror as a labelled proxy:
    python scripts/replay_signal_history_sar.py history.json \\
        --klines-base https://data-api.binance.vision --market spot

Spot is a **proxy**: different venue, different wicks, no funding — and a
trailing-stop replay is decided by wicks. Prefer futures whenever reachable; the
output labels which one it used.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, ".")

from src import sar_exit_shadow as sar  # noqa: E402

_MIN_MS = 60_000
_BAR_MIN = 15
_BAR_MS = _BAR_MIN * _MIN_MS
_ACTIVE = {"ACTIVE", "OPEN", "RUNNING", ""}


# --------------------------------------------------------------------------- #
# Candles
# --------------------------------------------------------------------------- #
def _klines(base: str, market: str, symbol: str, start_ms: int, end_ms: int,
            retries: int = 3) -> Optional[List[Sequence[Any]]]:
    path = "/fapi/v1/klines" if market == "futures" else "/api/v3/klines"
    url = (f"{base}{path}?symbol={symbol}&interval={_BAR_MIN}m"
           f"&startTime={start_ms}&endTime={end_ms}&limit=1000")
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as exc:
            if exc.code in (418, 429):          # rate limited — back off
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            time.sleep(0.5 * (attempt + 1))
    return None


def _dispatch_ms(row: Dict[str, Any]) -> Optional[int]:
    raw = row.get("timestamp") or row.get("dispatch_timestamp")
    if not raw:
        return None
    try:
        ts = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return int(ts.timestamp() * 1000)


def _f(v: Any) -> Optional[float]:
    try:
        f = float(v)
        return f if f == f else None          # reject NaN
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# Replay
# --------------------------------------------------------------------------- #
def replay_one(row: Dict[str, Any], base: str, market: str, *, warmup: int,
               window: int, old_fill: bool) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Replay one delivered signal. Returns ``(status, result_or_None)``.

    ``status`` is one of ``ok`` / ``no-candles`` / ``no-entry-bar`` /
    ``bad-row`` / ``refused``. Every non-``ok`` is counted and reported — the
    point is that the shortfall is visible, not that the mean looks tidy.
    """
    symbol = str(row.get("symbol") or "")
    side = str(row.get("direction") or row.get("side") or "").upper()
    entry = _f(row.get("entry"))
    sl = _f(row.get("stop_loss"))
    tp1 = _f(row.get("tp1"))
    d_ms = _dispatch_ms(row)
    if not symbol or side not in ("LONG", "SHORT") or not entry or not d_ms:
        return "bad-row", None

    start = d_ms - warmup * _BAR_MS
    end = d_ms + window * _BAR_MS
    raw = _klines(base, market, symbol, start, end)
    if not raw:
        return "no-candles", None

    opens = [float(k[1]) for k in raw]
    highs = [float(k[2]) for k in raw]
    lows = [float(k[3]) for k in raw]
    closes = [float(k[4]) for k in raw]
    open_ms = [int(k[0]) for k in raw]

    # Entry bar located by TIMESTAMP, never by counting elapsed time — the #800
    # bug class. No covering bar means we do not know which bar to replay, so we
    # refuse rather than clamp to the nearest.
    entry_idx = None
    for i, ms in enumerate(open_ms):
        if ms <= d_ms < ms + _BAR_MS:
            entry_idx = i
            break
    if entry_idx is None or entry_idx < 2:
        return "no-entry-bar", None

    if old_fill:
        # Reproduce the pre-fix behaviour by feeding the published series where
        # the stop series is read. Kept as a monkeypatch of the levels function
        # so the walk itself is byte-identical to production.
        real = sar.parabolic_sar_levels

        def _published_as_stops(h, low, st, mx):
            pub, _ = real(h, low, st, mx)
            return pub, pub
        sar.parabolic_sar_levels = _published_as_stops   # type: ignore[assignment]
    try:
        res = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=entry_idx, entry=entry, side=side,
            step=0.02, max_step=0.2, max_bars=window, bar_minutes=float(_BAR_MIN),
            stop_loss=sl or 0.0, tp1=tp1 or 0.0,
        )
    finally:
        if old_fill:
            sar.parabolic_sar_levels = real                # type: ignore[assignment]
    if res is None:
        return "refused", None

    exit_price = float(res["exit_price"])
    gross = ((exit_price - entry) / entry * 100.0) if side == "LONG" \
        else ((entry - exit_price) / entry * 100.0)
    sl_dist_pct = (abs(entry - sl) / entry * 100.0) if sl else 0.0
    return "ok", {
        "symbol": symbol,
        "side": side,
        "gross_pct": gross,
        "sl_dist_pct": sl_dist_pct,
        "r": (gross / sl_dist_pct) if sl_dist_pct > 0 else None,
        "exit_reason": res["exit_reason"],
        "hold_min": res["hold_min"],
        "aligned": res.get("sar_aligned_at_resolve"),
        "handover_bars": res.get("handover_bars"),
        "real_pnl_pct": _f(row.get("pnl_pct")),
        "real_r": ((_f(row.get("pnl_pct")) or 0.0) / sl_dist_pct)
                  if sl_dist_pct > 0 and _f(row.get("pnl_pct")) is not None else None,
        "regime": str(row.get("entry_regime") or "UNPLACED"),
        "setup": str(row.get("setup_class") or "UNKNOWN"),
    }


def _stats(vals: List[float]) -> str:
    if not vals:
        return "n=0"
    w = sum(1 for v in vals if v > 0)
    return ("n=%3d  win %5.1f%%  mean %+.3f  median %+.3f"
            % (len(vals), 100.0 * w / len(vals), sum(vals) / len(vals),
               sorted(vals)[len(vals) // 2]))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("history", help="signal_history JSON export")
    ap.add_argument("--klines-base", default="https://fapi.binance.com")
    ap.add_argument("--market", choices=("futures", "spot"), default="futures")
    ap.add_argument("--warmup", type=int, default=50,
                    help="bars before dispatch (SAR_EXIT_SHADOW_WARMUP_BARS)")
    ap.add_argument("--window", type=int, default=192,
                    help="bars after dispatch (SAR_EXIT_SHADOW_WINDOW_BARS)")
    ap.add_argument("--limit", type=int, default=0, help="cap rows (0 = all)")
    ap.add_argument("--compare-old-fill", action="store_true",
                    help="also replay with the pre-2026-07-28 fill and report the delta")
    ap.add_argument("--cost-pct", type=float, default=0.10,
                    help="round-trip taker cost deducted from gross (default 0.10%%)")
    args = ap.parse_args()

    rows = json.load(open(args.history))
    if not isinstance(rows, list):
        rows = rows.get("signals") or rows.get("records") or []
    # Delivered AND closed only: an open signal has no real outcome to compare
    # the counterfactual against, so including it would compare a finished
    # replay with an unfinished fact.
    rows = [r for r in rows
            if str(r.get("status") or "").upper() not in _ACTIVE]
    if args.limit:
        rows = rows[: args.limit]

    print(f"replaying {len(rows)} delivered+closed signals "
          f"({args.market} candles from {args.klines_base})")
    if args.market == "spot":
        print("  !! SPOT PROXY — these signals traded on perps. Different venue, "
              "different wicks, no funding. Treat as indicative only.")
    print()

    ok: List[Dict[str, Any]] = []
    old_ok: Dict[int, float] = {}
    status = Counter()
    for n, row in enumerate(rows):
        st, res = replay_one(row, args.klines_base, args.market,
                             warmup=args.warmup, window=args.window, old_fill=False)
        status[st] += 1
        if st == "ok" and res:
            ok.append(res)
            if args.compare_old_fill:
                st2, res2 = replay_one(row, args.klines_base, args.market,
                                       warmup=args.warmup, window=args.window,
                                       old_fill=True)
                if st2 == "ok" and res2:
                    old_ok[len(ok) - 1] = res2["gross_pct"]
        if (n + 1) % 25 == 0:
            print(f"  ... {n+1}/{len(rows)}  replayed={len(ok)}", file=sys.stderr)

    total = sum(status.values())
    print("COVERAGE")
    for k, v in status.most_common():
        print("  %-14s %4d  (%.0f%%)" % (k, v, 100.0 * v / total if total else 0))
    if not ok:
        print("\nnothing replayed — no result to report.")
        return 1
    print()

    net = [r["gross_pct"] - args.cost_pct for r in ok]
    real = [r["real_pnl_pct"] for r in ok if r["real_pnl_pct"] is not None]
    print("SAR ARM vs THE ENGINE'S REAL EXIT  (net of %.2f%% round-trip)" % args.cost_pct)
    print("  SAR replay   %s" % _stats(net))
    print("  engine real  %s" % _stats([p for p in real]))
    rs = [r["r"] for r in ok if r["r"] is not None]
    rr = [r["real_r"] for r in ok if r["real_r"] is not None]
    print("  SAR replay R %s" % _stats(rs))
    print("  engine  R    %s" % _stats(rr))
    print()

    if args.compare_old_fill and old_ok:
        deltas = [ok[i]["gross_pct"] - old for i, old in old_ok.items()]
        trail = [ok[i]["gross_pct"] - old for i, old in old_ok.items()
                 if ok[i]["exit_reason"] == sar.REASON_TRAIL]
        print("FILL CORRECTION (new minus old; negative = the old fill flattered)")
        print("  all replayed exits  %s" % _stats(deltas))
        print("  trail exits only    %s" % _stats(trail))
        print()

    print("BY SAR ALIGNMENT AT ENTRY")
    by = defaultdict(list)
    for r in ok:
        by[{True: "agreed", False: "opposed"}.get(r["aligned"], "undecided")].append(
            r["gross_pct"] - args.cost_pct)
    for k in ("agreed", "opposed", "undecided"):
        if by[k]:
            print("  %-10s %s" % (k, _stats(by[k])))
    print()

    print("BY EXIT REASON")
    byr = defaultdict(list)
    for r in ok:
        byr[r["exit_reason"]].append(r["gross_pct"] - args.cost_pct)
    for k in sorted(byr, key=lambda x: -len(byr[x])):
        print("  %-12s %s" % (k, _stats(byr[k])))
    print()

    # Concentration: overlapping entries into one move are not independent
    # evidence. Disclose it rather than silently averaging it.
    per_sym = Counter((r["symbol"], r["side"]) for r in ok)
    dupes = sum(v - 1 for v in per_sym.values() if v > 1)
    print("CONCENTRATION")
    print("  %d rows across %d symbol+side pairs; %d are repeats of a pair (%.0f%%)"
          % (len(ok), len(per_sym), dupes, 100.0 * dupes / len(ok)))
    top = per_sym.most_common(3)
    if top:
        print("  heaviest: " + ", ".join("%s %s ×%d" % (s, d, n) for (s, d), n in top))
    print()
    print("Reconstruction, not record. Counterfactuals are optimistic; this "
          "informs an adoption decision, it does not make one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
