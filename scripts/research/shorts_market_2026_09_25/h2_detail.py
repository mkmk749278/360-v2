"""H2 robustness: tails, adverse excursion, stops, funding drag."""
import numpy as np
import pandas as pd
from events import h2, daily
from load import fmt, summarize

res, lst = h2()
ev = res["primary +7 -> +60"].copy()
print("net: median %.2f p5 %.2f p95 %.2f min %.2f max %.2f" % tuple(np.percentile(ev.net, [50, 5, 95, 0, 100])))
print("funding paid by the short: median %.2f p10 %.2f min %.2f" % tuple(np.percentile(ev.fund, [50, 10, 0])))
print("worst 5:\n", ev.nsmallest(5, "net")[["sym", "t_entry", "gross", "fund", "net"]].to_string(index=False))
def mae(r):
    d = daily(r.sym)
    w = d.loc[r.t_entry: r.t_exit - pd.Timedelta(days=1)]
    p_in = d.close.loc[r.t_entry - pd.Timedelta(days=1)]
    return (w.high.max() - p_in) / p_in * 100
ev["mae"] = ev.apply(mae, axis=1)
print("adverse excursion pct: median %.1f p75 %.1f p90 %.1f" % tuple(np.percentile(ev.mae, [50, 75, 90])))
for stop in (15, 25, 40):
    ev[f"s{stop}"] = np.where(ev.mae >= stop, -stop - 0.17 + ev.fund, ev.net)
    print(fmt(summarize(ev, f"with a {stop}% hard stop", pnl=f"s{stop}")))
