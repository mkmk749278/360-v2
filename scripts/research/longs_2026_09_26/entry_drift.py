"""§11.1–11.2 of the report: entry drift on the engine's own record.

Drift = first price the monitor observed after dispatch vs the stamped entry,
signed toward the trade. Three prices of the same trade are compared:

* recorded  — `pnl_pct` from the stamped entry (what every page publishes);
* rebased   — the same exit priced from the observed fill (ops' rebased book);
* BE@fill   — rebased, except a BREAKEVEN_EXIT scratches at the fill. A live
  user's break-even stop parks at THEIR fill (`pretp_dispatcher`:
  `entry_price_filled`), while the book parks it at the stamped entry, so the
  rebased figure books every drifted scratch as a loss of the drift.
"""
import collections as C
import datetime as dt
import json
import os
import random
import statistics as st

from common import DATA

FEE = 0.07


def load():
    rows = json.load(open(os.path.join(DATA, "sigperf.json")))
    out = []
    for r in rows:
        e, o = r.get("entry") or 0, r.get("first_observed_price") or 0
        if e <= 0 or o <= 0 or r.get("first_observed_stale"):
            continue
        lng = r["direction"] == "LONG"
        x = e * (1 + r["pnl_pct"] / 100) if lng else e * (1 - r["pnl_pct"] / 100)
        r["drift"] = ((o / e - 1) if lng else (1 - o / e)) * 100
        r["book"] = r["pnl_pct"] - FEE
        r["reb"] = ((x / o - 1) if lng else (1 - x / o)) * 100 - FEE
        r["be_fill"] = -FEE if r["outcome_label"] == "BREAKEVEN_EXIT" else r["reb"]
        r["bar_age15"] = r["create_timestamp"] % 900
        out.append(r)
    return rows, out


def ci(rs, key, n=2000):
    by = C.defaultdict(list)
    for r in rs:
        by[r["symbol"]].append(r[key])
    g = list(by.values())
    if len(g) < 3:
        return float("nan"), float("nan")
    rnd = random.Random(5)
    ms = sorted(sum(map(sum, s)) / sum(map(len, s))
                for s in ([rnd.choice(g) for _ in g] for _ in range(n)))
    return ms[int(.025 * n)], ms[int(.975 * n)]


def line(rs):
    lo, hi = ci(rs, "be_fill")
    return (f"n={len(rs):4d} drift mean={st.mean(r['drift'] for r in rs):+.3f} "
            f"med={st.median(r['drift'] for r in rs):+.3f} | recorded {st.mean(r['book'] for r in rs):+.3f} "
            f"rebased {st.mean(r['reb'] for r in rs):+.3f} BE@fill {st.mean(r['be_fill'] for r in rs):+.3f} "
            f"CI[{lo:+.2f},{hi:+.2f}]")


def group(rs, key, title, minn=8):
    print(f"\n== {title}")
    g = C.defaultdict(list)
    for r in rs:
        g[key(r)].append(r)
    for k in sorted(g, key=str):
        if len(g[k]) >= minn:
            print(f"  {str(k):40s} {line(g[k])}")


def main():
    allrows, P = load()
    print(f"priced rows {len(P)} of {len(allrows)}, first dispatch "
          f"{dt.datetime.utcfromtimestamp(min(r['dispatch_timestamp'] for r in P)):%Y-%m-%d %H:%M} UTC")
    group(P, lambda r: r["direction"], "by side", 1)
    group(P, lambda r: (r["setup_class"], r["direction"]), "by path x side")
    M = [r for r in P if r["setup_class"] == "MOVER_TREND_PULLBACK" and r["direction"] == "LONG"]
    group(M, lambda r: "created <5m after 15m close" if r["bar_age15"] < 300
          else "created 5-15m after 15m close", "MVRTP LONG by signal age vs its 15m bar")
    group(M, lambda r: "drift < 0.5%" if r["drift"] < 0.5 else "drift >= 0.5%",
          "MVRTP LONG by drift at fill")
    mid = dt.datetime(2026, 9, 16, tzinfo=dt.timezone.utc).timestamp()
    group(M, lambda r: ("Sep05-15 " if r["dispatch_timestamp"] < mid else "Sep16-26 ")
          + ("drift<0.5" if r["drift"] < 0.5 else "drift>=0.5"), "MVRTP LONG, drift split by half")
    group(M, lambda r: r["pair_admission"] or "(none)", "MVRTP LONG by pair admission (priced)")
    print("\n== MVRTP LONG by pair admission, whole record (recorded prices)")
    g = C.defaultdict(list)
    for r in allrows:
        if r["setup_class"] == "MOVER_TREND_PULLBACK" and r["direction"] == "LONG":
            r["book"] = r["pnl_pct"] - FEE
            g[r["pair_admission"] or "(unstamped)"].append(r)
    for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
        lo, hi = ci(v, "book")
        print(f"  {k:16s} n={len(v):4d} recorded {st.mean(r['book'] for r in v):+.3f} CI[{lo:+.2f},{hi:+.2f}]")


if __name__ == "__main__":
    main()
