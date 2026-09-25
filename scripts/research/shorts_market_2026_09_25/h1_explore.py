"""H1 exploratory filters E1-E4, declared in HYPOTHESES.md before running."""
import numpy as np
import pandas as pd
from events import h1, daily
from load import COST_RT, fmt, funding, summarize, universe

res = h1()
ev = res["primary [T-14, T+2]"].copy()


def last_funding(sym, t):
    f = funding(sym)
    f = f[f.index <= t]
    return f.iloc[-1] if len(f) else np.nan


def ret_into(sym, t, days=14):
    d = daily(sym).close
    t_close = t - pd.Timedelta(days=1)  # entry is at this bar's close
    t0 = t_close - pd.Timedelta(days=days)
    if t0 not in d.index or t_close not in d.index:
        return np.nan
    return d.loc[t_close] / d.loc[t0] - 1


def mae(r):
    d = daily(r.sym)
    w = d.loc[r.t_entry: r.t_exit - pd.Timedelta(days=1)]
    p_in = d.close.loc[r.t_entry - pd.Timedelta(days=1)]
    return (w.high.max() - p_in) / p_in * 100


# Equal-weight liquid-alt basket (BTC/ETH excluded), point-in-time liquidity.
closes, qv = {}, {}
for s in universe():
    if s in ("BTCUSDT", "ETHUSDT"):
        continue
    d = daily(s)
    if d is not None:
        closes[s], qv[s] = d.close, d.quote_volume
PX = pd.DataFrame(closes).sort_index()
QV = pd.DataFrame(qv).sort_index().rolling(7, min_periods=5).mean().shift(1)


def basket_ret(t_in, t_out):
    a, b = t_in - pd.Timedelta(days=1), t_out - pd.Timedelta(days=1)
    if a not in PX.index or b not in PX.index:
        return np.nan
    elig = QV.columns[(QV.loc[a] >= 10e6).values]
    r = (PX.loc[b, elig] / PX.loc[a, elig] - 1).dropna()
    return r.mean() if len(r) >= 20 else np.nan


ev["f_in"] = [last_funding(s, t) for s, t in zip(ev.sym, ev.t_entry)]
ev["r14"] = [ret_into(s, t) for s, t in zip(ev.sym, ev.t_entry)]
ev["mae"] = ev.apply(mae, axis=1)
ev["bask"] = [basket_ret(a, b) for a, b in zip(ev.t_entry, ev.t_exit)]
ev["alt_hedged"] = ev.net + ev.bask * 100 - COST_RT  # basket funding not charged (small; see report)


def report(df, label):
    print(fmt(summarize(df, label)))
    for stop in (20, 40):
        x = df.copy()
        x["s"] = np.where(x.mae >= stop, -stop - COST_RT + x.fund, x.net)
        print(fmt(summarize(x, f"   {stop}% hard stop", pnl="s")))


report(ev, "H1 primary (reference)")
e1 = ev[~(ev.f_in <= -0.0003)]
report(e1, "E1 skip crowded (funding <= -0.03%)")
e2 = ev[~(ev.r14 > 0.20)]
report(e2, "E2 skip squeeze in progress (14d > +20%)")
e3 = ev[~(ev.f_in <= -0.0003) & ~(ev.r14 > 0.20)]
report(e3, "E3 = E1 + E2")
print(fmt(summarize(ev.dropna(subset=["alt_hedged"]), "E4 alt-basket hedged", pnl="alt_hedged")))
print(fmt(summarize(e3.dropna(subset=["alt_hedged"]), "E3 + E4 alt-basket hedged", pnl="alt_hedged")))
print("removed by E1:", int((ev.f_in <= -0.0003).sum()), " by E2:", int((ev.r14 > 0.20).sum()))
print("E3 rows' worst 3:\n", e3.nsmallest(3, "net")[["sym", "t_entry", "net", "mae"]].to_string(index=False))
