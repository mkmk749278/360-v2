"""H10 robustness. Each check answers one way the pass could be false.

  delay    entry one bar later (+5m): rules out look-ahead in the OI stamp
  control  same price drop with OI flat/up: is the OI (liquidation) part the edge?
  slippage 0.10 / 0.15 % per fill: bursts are exactly when spreads widen
  hold     15m / 30m / 1h / 2h
  days     drop the 5 biggest days; per month
  liquidity tiers
"""
import pickle
import sys
import numpy as np
import pandas as pd
from events import daily
from load import END, IS_START, DATA, FEE_RT, fmt, funding, klines, metrics, summarize, universe


def rows_for(sym):
    k = klines("k5m", sym)
    m = metrics(sym)
    if k is None or m is None or len(m) < 1000:
        return []
    oi = m.oi.reindex(k.index + pd.Timedelta(minutes=5), method="ffill")
    oi.index = k.index
    d_oi = oi / oi.shift(3) - 1
    d_px = k.close / k.close.shift(3) - 1
    dq = daily(sym)
    qv7 = pd.Series(dq.quote_volume.rolling(7, min_periods=5).mean().shift(1)
                    .reindex(k.index.floor("D")).values, index=k.index)
    burst = (d_oi <= -0.015) & (d_px <= -0.02) & (qv7 >= 10e6)
    ctrl = (d_oi >= 0) & (d_px <= -0.02) & (qv7 >= 10e6)
    o, c = k.open.values, k.close.values
    idx = k.index
    fund = funding(sym)
    out = []
    for kind, mask in (("burst", burst), ("ctrl", ctrl)):
        busy = -1
        for i in np.flatnonzero(mask.fillna(False).values):
            if i <= busy or i + 26 >= len(k):
                continue
            row = {"sym": sym, "kind": kind, "qv7": qv7.iloc[i], "d_oi": d_oi.iloc[i], "d_px": d_px.iloc[i]}
            for delay in (1, 2):
                e = i + delay
                t_in = idx[e]
                if t_in < IS_START or t_in >= END:
                    row = None
                    break
                for hold in (3, 6, 12, 24):
                    x = e + hold - 1
                    t_out = idx[x] + pd.Timedelta(minutes=5)
                    fr = fund[(fund.index > t_in) & (fund.index <= t_out)].sum() * 100 if len(fund) else 0.0
                    row[f"g_d{delay}_h{hold}"] = (o[e] - c[x]) / o[e] * 100 + fr
                row[f"t_d{delay}"] = t_in
            if row is None:
                continue
            row["t_entry"] = row["t_d1"]
            out.append(row)
            busy = i + 12
    return out


if __name__ == "__main__":
    path = f"{DATA}/h10_rows.pkl"
    if "--load" in sys.argv:
        df = pickle.load(open(path, "rb"))
    else:
        from multiprocessing import Pool
        rows = []
        with Pool(4) as pool:
            for n, r in enumerate(pool.imap_unordered(rows_for, universe(), chunksize=4)):
                rows += r
                if n % 100 == 0:
                    print(n, len(rows), flush=True)
        df = pd.DataFrame(rows)
        pickle.dump(df, open(path, "wb"))
    b, c = df[df.kind == "burst"].copy(), df[df.kind == "ctrl"].copy()

    def net(x, col, slip_per_fill=0.05):
        y = x.copy()
        y["net"] = y[col] - FEE_RT - 2 * slip_per_fill
        return y

    print(fmt(summarize(net(b, "g_d1_h12"), "burst, entry +5m, hold 1h (as registered)")))
    print(fmt(summarize(net(b, "g_d2_h12"), "burst, entry +10m (one bar later), hold 1h")))
    print(fmt(summarize(net(c, "g_d1_h12"), "control: same drop, OI flat/up, hold 1h")))
    for s in (0.10, 0.15):
        print(fmt(summarize(net(b, "g_d1_h12", s), f"burst, slippage {s:.2f}%/fill")))
    for h, lab in ((3, "15m"), (6, "30m"), (24, "2h")):
        print(fmt(summarize(net(b, f"g_d1_h{h}"), f"burst, hold {lab}")))
    x = net(b, "g_d1_h12")
    x["day"] = x.t_entry.dt.floor("D")
    top = x.groupby("day").net.sum().sort_values(ascending=False)
    print("top 5 days:", [(str(d.date()), round(v, 1), int((x.day == d).sum())) for d, v in top.head(5).items()])
    print(fmt(summarize(x[~x.day.isin(top.index[:5])], "burst, excluding 5 best days")))
    print(fmt(summarize(x, "burst, symbol-clustered", cluster="sym")))
    x["m"] = x.t_entry.dt.strftime("%Y-%m")
    print(x.groupby("m").net.agg(["size", "mean"]).round(3).T.to_string())
    for lo, hi in ((10e6, 30e6), (30e6, 100e6), (100e6, 1e13)):
        print(fmt(summarize(x[(x.qv7 >= lo) & (x.qv7 < hi)], f"liquidity ${lo/1e6:.0f}M-${hi/1e6:.0f}M/day")))
    for lo, hi in ((-0.03, -0.015), (-0.06, -0.03), (-1, -0.06)):
        print(fmt(summarize(x[(x.d_oi > lo) & (x.d_oi <= hi)] if lo > -1 else x[x.d_oi <= hi],
                            f"OI drop {hi:.1%}..{lo:.1%}")))
