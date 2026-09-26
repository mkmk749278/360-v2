"""Exit counterfactuals for MVRTP LONG, last 60 days, on Binance 1m tape.

Each test starts at the trade's ACTUAL exit and walks forward, because at that
moment the alternative exit rule is in a known state:

* BREAKEVEN_EXIT -> "no BE move". Price is back at entry, the original stop
  was never touched (the BE stop sat above it) and TP1 was never touched (or
  the row would read TP1). So the no-BE trade is simply still open at entry
  with its original stop and target. Walk: +TP first -> +TP; stop first -> -S.
* SL_HIT -> "wider stop". Price is at the old stop. Walk with the stop
  `extra` points further away, the current BE rule (arm at +2%, park at
  entry) and the same target.
* TP1 / PROFIT_LOCKED -> "runner". Half closes at TP1 (as now); the other half
  walks on with its stop at entry (or at half the TP1 gain) toward 2x TP1.

Levels the public record does not carry are fixed from the book's own
medians: stop 3.0% (62% of MVRTP stops sit at the 3% cap) and TP1 4.0%
(median TP1 gain 3.98%); the BE test is repeated at TP 3.0%. A bar touching
both levels is booked at the stop. Horizon 24h, then marked to the close.
Deltas are gross and the fee cancels: both arms are one round trip.
"""
import collections as C
import datetime as dt
import glob
import os
import random
import zipfile

import numpy as np

from common import DATA, END, MVRTP, load_rows

H = 24 * 60
_cache = {}


def klines(sym):
    if sym in _cache:
        return _cache[sym]
    parts = []
    for f in sorted(glob.glob(os.path.join(DATA, "kl", f"{sym}__*.zip"))):
        try:
            z = zipfile.ZipFile(f)
            raw = z.read(z.namelist()[0]).decode().strip().splitlines()
        except Exception:  # noqa: BLE001 — a missing day is reported as no coverage
            continue
        if raw and raw[0].startswith("open_time"):
            raw = raw[1:]
        if raw:
            parts.append(np.array([ln.split(",")[:5] for ln in raw], dtype=float))
    a = None
    if parts:
        a = np.concatenate(parts)
        a[:, 0] = np.where(a[:, 0] > 1e14, a[:, 0] / 1000, a[:, 0])
        a = a[np.argsort(a[:, 0])]
    _cache[sym] = a
    return a


def walk(a, i0, entry, stop, tp, be_arm=None, be_level=None):
    st = stop
    end = min(len(a), i0 + H)
    for i in range(i0, end):
        if a[i, 3] <= st:
            return (st / entry - 1) * 100, "be" if be_arm and st >= entry * 0.999 else "stop"
        if a[i, 2] >= tp:
            return (tp / entry - 1) * 100, "tp"
        if be_arm is not None and a[i, 2] >= be_arm and st < be_level:
            st = be_level
    if end <= i0:
        return None, "nodata"
    return (a[end - 1, 4] / entry - 1) * 100, "mtm" if end == i0 + H else "mtm_partial"


def ci(items, n=2000):
    by = C.defaultdict(list)
    for d, _, sym in items:
        by[sym].append(d)
    g = list(by.values())
    rnd = random.Random(3)
    ms = sorted(sum(map(sum, s)) / sum(map(len, s))
                for s in ([rnd.choice(g) for _ in g] for _ in range(n)))
    return ms[int(.025 * n)], ms[int(.975 * n)]


def main():
    res = C.defaultdict(list)
    nocov = 0
    for r in load_rows():
        if r["direction"] != "LONG" or r["setup"] != MVRTP:
            continue
        if r["t"] < END - dt.timedelta(days=60):
            continue
        a = klines(r["symbol"])
        tms = r["t"].timestamp() * 1000
        i0 = int(np.searchsorted(a[:, 0], tms, side="right")) if a is not None else 0
        if a is None or i0 >= len(a) or a[i0, 0] - tms > 5 * 60 * 1000:
            nocov += 1
            continue
        E, g, o, sym = r["entry"], r["pnl_pct"], r["outcome"], r["symbol"]
        if o == "BREAKEVEN_EXIT":
            for s, tp in ((3.0, 4.0), (3.0, 3.0)):
                v, how = walk(a, i0, E, E * (1 - s / 100), E * (1 + tp / 100))
                if v is not None:
                    res[f"BE -> no BE (stop {s}, TP {tp})"].append((v - g, how, sym))
        elif o == "SL_HIT":
            s = -g
            for extra in (1.0, 2.0, 3.0):
                v, how = walk(a, i0, E, E * (1 - (s + extra) / 100), E * 1.04,
                              be_arm=E * 1.02, be_level=E)
                if v is not None:
                    res[f"SL -> stop wider by {extra:.0f}pt"].append((v - g, how, sym))
            end = min(len(a), i0 + H)
            res["SL -> traded back to entry in 24h (share)"].append(
                (1.0 if (a[i0:end, 2] >= E).any() else 0.0, "", sym))
        elif o in ("TP1_HIT", "PROFIT_LOCKED", "FULL_TP_HIT"):
            v, how = walk(a, i0, E, E, E * (1 + 2 * g / 100))
            if v is not None:
                res["TP1 -> 50% runner, stop at entry, 2x TP1"].append((0.5 * (v - g), how, sym))
            v, how = walk(a, i0, E, E * (1 + g / 200), E * (1 + 2 * g / 100))
            if v is not None:
                res["TP1 -> 50% runner, stop at +TP1/2, 2x TP1"].append((0.5 * (v - g), how, sym))
    print(f"no 1m coverage: {nocov} trades")
    for k, v in res.items():
        ds = [d for d, _, _ in v]
        lo, hi = ci(v)
        hows = dict(C.Counter(h for _, h, _ in v))
        print(f"{k:44s} n={len(v):4d} mean={np.mean(ds):+.3f} CI[{lo:+.2f},{hi:+.2f}] "
              f"total={np.sum(ds):+7.1f}  {hows if '' not in hows else ''}")


if __name__ == "__main__":
    main()
