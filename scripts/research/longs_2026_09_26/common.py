"""Shared loading and statistics for the longs research. Research code: not
imported by the engine, changes nothing on the money path."""
import collections as C
import datetime as dt
import json
import os
import random

DATA = os.environ.get("LONGS_DATA_DIR", os.path.expanduser("~/longs_research_data"))
#: The export was taken 2026-09-26 ~06:00 UTC. Every window is measured back
#: from here, never from "now", so a rerun on the same rows.json reproduces.
END = dt.datetime(2026, 9, 26, 6, 0, tzinfo=dt.timezone.utc)
MVRTP = "MOVER_TREND_PULLBACK"


def load_rows():
    rows = json.load(open(os.path.join(DATA, "rows.json")))
    for r in rows:
        r["t"] = dt.datetime.fromisoformat(r["closed_at"])
        r["day"] = r["t"].date()
    return rows


def window(rows, days):
    if days is None:
        return rows
    return [r for r in rows if r["t"] >= END - dt.timedelta(days=days)]


def boot_ci(items, value=lambda r: r["net_pct"], group=lambda r: r["symbol"],
            n=2000, seed=1):
    """Symbol-clustered bootstrap 95% CI of the per-trade mean.

    One symbol's repeated entries into one move are not independent evidence,
    so the resampling unit is the symbol, not the trade."""
    by = C.defaultdict(list)
    for r in items:
        by[group(r)].append(value(r))
    groups = list(by.values())
    if len(groups) < 3:
        return float("nan"), float("nan")
    rnd = random.Random(seed)
    ms = []
    for _ in range(n):
        s = [rnd.choice(groups) for _ in groups]
        ms.append(sum(map(sum, s)) / sum(map(len, s)))
    ms.sort()
    return ms[int(0.025 * n)], ms[int(0.975 * n)]


def summ(rs):
    if not rs:
        return None
    net = [r["net_pct"] for r in rs]
    w = [x for x in net if x > 0]
    lo_ = [x for x in net if x <= 0]
    lo, hi = boot_ci(rs)
    return dict(n=len(rs), mean=sum(net) / len(rs), tot=sum(net),
                win=len(w) / len(rs), lo=lo, hi=hi,
                avgw=(sum(w) / len(w) if w else 0.0),
                avgl=(sum(lo_) / len(lo_) if lo_ else 0.0),
                syms=len({r["symbol"] for r in rs}))


def fmt(s):
    if not s:
        return "-"
    return (f"n={s['n']:4d} sym={s['syms']:3d} mean={s['mean']:+.3f}% "
            f"CI[{s['lo']:+.2f},{s['hi']:+.2f}] tot={s['tot']:+8.1f}% "
            f"win={s['win']*100:4.1f}% avgW={s['avgw']:+.2f} avgL={s['avgl']:+.2f}")
