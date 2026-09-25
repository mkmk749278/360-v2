"""H1 robustness: distribution, tails, size and recipient splits, adverse
excursion during the hold, and the event-minus-control difference."""
import numpy as np
import pandas as pd
from events import h1, daily
from load import fmt, summarize

res = h1()
ev = res["primary [T-14, T+2]"].copy()
ctl = res["control (same tokens, >=45d from unlocks)"].copy()
print("event net: median %.2f  p5 %.2f  p95 %.2f  min %.2f  max %.2f" % tuple(
    np.percentile(ev.net, [50, 5, 95, 0, 100])))
print("worst 5:\n", ev.nsmallest(5, "net")[["sym", "t_entry", "net", "fund"]].to_string(index=False))
# Adverse excursion: highest daily high during the hold vs entry.
def mae(r):
    d = daily(r.sym)
    w = d.loc[r.t_entry: r.t_exit - pd.Timedelta(days=1)]
    p_in = d.close.loc[r.t_entry - pd.Timedelta(days=1)]
    return (w.high.max() - p_in) / p_in * 100
ev["mae"] = ev.apply(mae, axis=1)
print("adverse excursion pct: median %.1f p75 %.1f p90 %.1f p95 %.1f" % tuple(np.percentile(ev.mae, [50, 75, 90, 95])))
for stop in (10, 15, 20):
    capped = np.where(ev.mae >= stop, -stop - 0.17 + ev.fund, ev.net)
    ev[f"s{stop}"] = capped
    print(fmt(summarize(ev, f"with a {stop}% hard stop (booked at stop)", pnl=f"s{stop}")))
# size buckets
for lo, hi in [(0.005, 0.01), (0.01, 0.02), (0.02, 1)]:
    print(fmt(summarize(ev[(ev.frac >= lo) & (ev.frac < hi)], f"size {lo:.1%}-{hi:.0%} of max supply")))
# first unlock of a token vs repeats in the window
ev = ev.sort_values("t_entry")
ev["nth"] = ev.groupby("sym").cumcount()
print(fmt(summarize(ev[ev.nth == 0], "first event per token in window")))
print(fmt(summarize(ev[ev.nth > 0], "repeat events")))
# difference vs control, bootstrapping days across both samples
def diff_ci(a, b, col, n=4000, seed=1):
    rng = np.random.default_rng(seed)
    da = a.groupby(a.t_entry.dt.floor("D"))[col].apply(list)
    db = b.groupby(b.t_entry.dt.floor("D"))[col].apply(list)
    out = []
    A, B = list(da.values), list(db.values)
    for _ in range(n):
        xa = np.concatenate([A[i] for i in rng.integers(0, len(A), len(A))])
        xb = np.concatenate([B[i] for i in rng.integers(0, len(B), len(B))])
        out.append(xa.mean() - xb.mean())
    return np.percentile(out, [2.5, 97.5])
for col in ("net", "hedged"):
    lo, hi = diff_ci(ev, ctl, col)
    print(f"event - control ({col}): {ev[col].mean() - ctl[col].mean():+.2f}pp  CI[{lo:+.2f}, {hi:+.2f}]")
