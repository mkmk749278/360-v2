"""Every book table in docs/LONGS_RESEARCH_2026_09_26.md.

    python book.py            # all sections
    python book.py sides paths   # or pick sections
"""
import bisect
import collections as C
import datetime as dt
import sys

from common import END, MVRTP, fmt, load_rows, summ, window

rows = load_rows()
LONG = [r for r in rows if r["direction"] == "LONG"]
M = sorted([r for r in LONG if r["setup"] == MVRTP], key=lambda r: r["t"])
OTHER = [r for r in LONG if r["setup"] != MVRTP]


def group(rs, keyf, title):
    print(f"\n== {title}")
    g = C.defaultdict(list)
    for r in rs:
        g[keyf(r)].append(r)
    for k in sorted(g, key=str):
        print(f"  {str(k):22s} {fmt(summ(g[k]))}")


def sides():
    print("== LONG vs SHORT by window")
    for name, d in (("all", None), ("60d", 60), ("30d", 30), ("14d", 14)):
        for side in ("LONG", "SHORT"):
            rs = [r for r in window(rows, d) if r["direction"] == side]
            print(f"  {name:4s} {side:5s} {fmt(summ(rs))}")


def paths():
    print("\n== per path x side (all / 30d), with first/last close and last-7d count")
    keys = C.Counter((r["setup"], r["direction"]) for r in rows)
    for side in ("LONG", "SHORT"):
        print(f"--- {side}")
        for (s, dr), _ in sorted(keys.items(), key=lambda x: -x[1]):
            if dr != side:
                continue
            a = [r for r in rows if r["setup"] == s and r["direction"] == dr]
            ts = [r["t"] for r in a]
            n7 = sum(1 for t in ts if t >= END - dt.timedelta(days=7))
            print(f"  {s:32s} ALL {fmt(summ(a))}  "
                  f"{min(ts):%m-%d}..{max(ts):%m-%d} last7d={n7}")
            b = window(a, 30)
            if b:
                print(f"  {'':32s} 30d {fmt(summ(b))}")
    print("\n  non-MVRTP longs, all:", fmt(summ(OTHER)))
    print("  non-MVRTP longs, 30d:", fmt(summ(window(OTHER, 30))))
    print("  MVRTP longs, 30d:    ", fmt(summ(window(M, 30))))


def mvrtp():
    group(M, lambda r: r["t"].strftime("%Y-%m"), "MVRTP LONG by close month")
    group(M, lambda r: r["regime"], "MVRTP LONG by entry regime (UNPLACED = before #817)")
    print("\n== MVRTP LONG regime x month (mean, n)")
    for m in ("2026-07", "2026-08", "2026-09"):
        cells = []
        for rg in ("UNPLACED", "RANGING", "TRENDING_UP", "VOLATILE"):
            rs = [r for r in M if r["t"].strftime("%Y-%m") == m and r["regime"] == rg]
            if rs:
                cells.append(f"{rg}:{sum(r['net_pct'] for r in rs)/len(rs):+.2f}({len(rs)})")
        print(f"  {m} " + " ".join(cells))
    group(M, lambda r: r["outcome"], "MVRTP LONG by outcome")
    print("\n== MVRTP LONG outcome mix by month")
    for m in ("2026-07", "2026-08", "2026-09"):
        rs = [r for r in M if r["t"].strftime("%Y-%m") == m]
        c = C.Counter(r["outcome"] for r in rs)
        print(f"  {m} n={len(rs)} " + ", ".join(f"{k} {v/len(rs):.0%}" for k, v in c.most_common()))

    def pb(p):
        return ("<0.01" if p < 0.01 else "<0.1" if p < 0.1 else "<1" if p < 1
                else "<10" if p < 10 else ">=10")
    group(M, lambda r: pb(r["entry"]), "MVRTP LONG by entry price bucket")
    group(M, lambda r: r["t"].strftime("%a"), "MVRTP LONG by close weekday")

    net = sorted((r["net_pct"] for r in M), reverse=True)
    tot = sum(net)
    print("\n== MVRTP LONG tail dependence")
    for k in (10, 20, 50):
        print(f"  total {tot:+.1f}; without the best {k}: {tot - sum(net[:k]):+.1f}")
    q = lambda a, p: a[int(p * (len(a) - 1))]  # noqa: E731
    sl = sorted(r["pnl_pct"] for r in M if r["outcome"] == "SL_HIT")
    tp = sorted(r["pnl_pct"] for r in M if r["outcome"] in ("TP1_HIT", "PROFIT_LOCKED"))
    print("  SL_HIT gross p5/25/50/75/95:", [round(q(sl, p), 2) for p in (.05, .25, .5, .75, .95)],
          f" share at <= -2.9%: {sum(1 for x in sl if x <= -2.9)/len(sl):.0%}")
    print("  TP1/LOCKED gross p5/25/50/75/95:", [round(q(tp, p), 2) for p in (.05, .25, .5, .75, .95)])


def others():
    group(OTHER, lambda r: r["regime"], "non-MVRTP LONG by entry regime")
    print("\n== SR_FLIP_RETEST LONG, every row")
    for r in sorted((r for r in LONG if r["setup"] == "SR_FLIP_RETEST"), key=lambda r: r["t"]):
        print(f"  {r['t']:%m-%d %H:%M} {r['symbol']:14s} {r['outcome']:15s} {r['net_pct']:+.2f}")


def days():
    def reds(rs):
        d = C.defaultdict(float)
        for r in rs:
            d[r["day"]] += r["net_pct"]
        neg = [v for v in d.values() if v < 0]
        return f"days={len(d)} red={len(neg)} red_total={sum(neg):+.1f} worst={min(d.values()):+.1f}"
    print("\n== red days")
    for n in (30, 60):
        rs = window(rows, n)
        print(f"  {n}d whole book: {reds(rs)}")
        print(f"  {n}d longs only: {reds([r for r in rs if r['direction'] == 'LONG'])}")
    L60 = window(LONG, 60)
    d = C.defaultdict(list)
    for r in L60:
        d[r["day"]].append(r)
    print("  worst long days (60d):")
    for k in sorted(d, key=lambda k: sum(r["net_pct"] for r in d[k]))[:8]:
        rs = d[k]
        sl = sum(1 for r in rs if r["outcome"] == "SL_HIT")
        mv = sum(1 for r in rs if r["setup"] == MVRTP)
        print(f"    {k} n={len(rs):3d} total={sum(r['net_pct'] for r in rs):+6.1f} "
              f"SL={sl/len(rs):.0%} MVRTP={mv}")


def activity():
    ts = [r["t"] for r in M]
    for r in M:
        a = bisect.bisect_left(ts, r["t"] - dt.timedelta(hours=30))
        b = bisect.bisect_left(ts, r["t"] - dt.timedelta(hours=6))
        r["trail"] = b - a
        xs = [x["net_pct"] for x in M[a:b]]
        r["trail_mean"] = sum(xs) / len(xs) if xs else None
    R = window(M, 60)
    print("\n== MVRTP LONG 60d by LAGGED activity: MVRTP long closes in [t-30h, t-6h]")
    for lo, hi in ((0, 10), (10, 20), (20, 35), (35, 10**6)):
        print(f"  {lo:3d}-{hi if hi < 10**6 else '':3}: {fmt(summ([r for r in R if lo <= r['trail'] < hi]))}")
    print("== MVRTP LONG 60d by LAGGED book quality: mean net of those closes")
    for lo, hi in ((-99, -0.5), (-0.5, 0), (0, 0.5), (0.5, 99)):
        xs = [r for r in R if r["trail_mean"] is not None and lo <= r["trail_mean"] < hi]
        print(f"  [{lo:+.1f},{hi:+.1f}): {fmt(summ(xs))}")
    print("== MVRTP LONG by nth entry on the same symbol within 24h (close order)")
    bys = C.defaultdict(list)
    for r in M:
        bys[r["symbol"]].append(r)
    nth, aft = C.defaultdict(list), C.defaultdict(list)
    for rs in bys.values():
        chain, prev = 0, None
        for r in rs:
            chain = chain + 1 if prev and r["t"] - prev["t"] <= dt.timedelta(hours=24) else 1
            nth[min(chain, 4)].append(r)
            if prev and r["t"] - prev["t"] <= dt.timedelta(hours=24):
                key = ("after_SL" if prev["outcome"] == "SL_HIT"
                       else "after_win" if prev["net_pct"] > 0 else "after_BE/other")
                aft[key].append(r)
            prev = r
    for k in sorted(nth):
        print(f"  nth={k}{'+' if k == 4 else ' '} {fmt(summ(nth[k]))}")
    for k, v in sorted(aft.items()):
        print(f"  {k:15s} {fmt(summ(v))}")


def shorts():
    S = [r for r in rows if r["direction"] == "SHORT"
         and r["t"] >= END - dt.timedelta(days=7)]
    group(S, lambda r: r["setup"], "SHORT paths, last 7 days")
    R30 = window(rows, 30)
    print("\n  book 30d:               ", fmt(summ(R30)))
    print("  book 30d w/o LSR SHORT: ", fmt(summ([r for r in R30 if not (
        r["setup"] == "LIQUIDITY_SWEEP_REVERSAL" and r["direction"] == "SHORT")])))


SECTIONS = dict(sides=sides, paths=paths, mvrtp=mvrtp, others=others,
                days=days, activity=activity, shorts=shorts)
if __name__ == "__main__":
    for name in (sys.argv[1:] or SECTIONS):
        SECTIONS[name]()
