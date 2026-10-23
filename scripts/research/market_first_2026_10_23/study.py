#!/usr/bin/env python3
"""Phase-0 market study behind docs/MARKET_FIRST_METHODOLOGY_2026_10_23.md.

    python scripts/research/market_first_2026_10_23/study.py --data /tmp/mf

Prints, from the candles fetch.py wrote:
  1. BTC regime mix and run lengths (BTC daily close vs its 20-day SMA + slope)
  2. alt correlation and up/down beta to BTC (hourly, daily)
  3. does a move continue or reverse (pooled across coins, 1h..7d)
  4. event -> next-12h price move, by BTC regime, split into two halves
  5. hour-of-day and weekday volatility

Every regime label is YESTERDAY's, so nothing here reads the future. Returns are
price moves only: no stop, no fee. That is what makes them hypotheses for the
Phase-1 replay rather than results.
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np
import pandas as pd


def load(path: str) -> pd.DataFrame:
    px = {}
    for f in sorted(os.listdir(path)):
        r = pd.DataFrame(json.load(open(os.path.join(path, f))))
        r["t"] = pd.to_datetime(r.t, unit="s", utc=True)
        px[f[:-5]] = r.drop_duplicates("t").set_index("t").c.astype(float).sort_index()
    return pd.DataFrame(px).sort_index()


def btc_regime(btc: pd.Series) -> pd.Series:
    d = btc.resample("1D").last()
    sma = d.rolling(20).mean()
    up = (d > sma) & (sma > sma.shift(5))
    dn = (d < sma) & (sma < sma.shift(5))
    reg = pd.Series(np.where(up, "UP", np.where(dn, "DOWN", "RANGE")), index=d.index)
    reg[sma.isna()] = None
    return reg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    a = ap.parse_args()
    pd.set_option("display.width", 200)
    P = load(a.data)
    lp = np.log(P)
    r = lp.diff()
    alts = [c for c in P.columns if c != "BTC"]
    reg = btc_regime(P.BTC)
    regh = reg.shift(1).reindex(P.index, method="ffill").values  # known at the hour

    print("== 1. BTC regime mix", P.index.min(), "->", P.index.max())
    print(reg.value_counts().to_dict())
    runs = (reg != reg.shift()).cumsum()
    rl = reg.groupby(runs).agg(["first", "size"])
    print("median run (days):", rl.groupby("first")["size"].median().to_dict())
    alt = r[alts].mean(axis=1)
    dd = pd.DataFrame({"btc": r.BTC.resample("1D").sum(),
                       "alts": alt.resample("1D").sum(), "reg": reg})
    print((dd.groupby("reg")[["btc", "alts"]].mean() * 100).round(3), "(avg % per day)")

    print("\n== 2. alts vs BTC")
    for freq in ["1h", "1D"]:
        rb = r.BTC if freq == "1h" else r.BTC.resample(freq).sum()
        ra = r[alts] if freq == "1h" else r[alts].resample(freq).sum()
        up, dn = rb > 0, rb < 0
        bu = np.median([ra[c][up].cov(rb[up]) / rb[up].var() for c in alts])
        bd = np.median([ra[c][dn].cov(rb[dn]) / rb[dn].var() for c in alts])
        co = np.median([ra[c].corr(rb) for c in alts])
        print(f"{freq}: corr {co:.2f}  beta BTC-up {bu:.2f}  beta BTC-down {bd:.2f}")

    print("\n== 3. corr(past move, next move), pooled")
    for H in [1, 4, 24, 72, 168]:
        idx = P.index[::H]
        x = lp.diff(H).loc[idx].stack()
        y = (lp.shift(-H) - lp).loc[idx].stack()
        ok = x.notna() & y.notna()
        print(f"{H:>4}h {np.corrcoef(x[ok], y[ok])[0, 1]:+.3f}")

    print("\n== 4. event -> next-12h move (%), by yesterday's BTC regime")
    A = lp[alts]
    f12 = A.shift(-12) - A
    p4, u3 = A.diff(4), A.diff(72)
    lo24, hi24 = A.rolling(24).min().shift(1), A.rolling(24).max().shift(1)
    events = {
        "pullback in strong coin (-3%/4h, +10%/3d)": (p4 < -0.03) & (u3 > 0.10),
        "oversold dip in weak coin (-3%/4h, <=0/3d)": (p4 < -0.03) & (u3 <= 0),
        "bounce +3%/4h": p4 > 0.03,
        "break below 24h low": A < lo24,
        "break above 24h high": A > hi24,
    }
    mid = P.index[len(P) // 2]
    for name, c in events.items():
        for half, sl in [("H1", P.index < mid), ("H2", P.index >= mid)]:
            out = []
            for rg in ["UP", "RANGE", "DOWN"]:
                m = c.values & (regh == rg)[:, None] & sl[:, None]
                v = f12.values[m]
                v = v[~np.isnan(v)]
                out.append(f"{rg} {v.mean() * 100:+.2f} (n{len(v)})")
            print(f"{half} {name:<44} " + "  ".join(out))

    print("\n== 5. volatility by UTC hour and weekday (BTC |1h move|, relative)")
    v = r.BTC.abs()
    hr = v.groupby(v.index.hour).mean()
    print((hr / hr.mean()).round(2).to_dict())
    wd = v.groupby(v.index.dayofweek).mean()
    print(dict(zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                   (wd / wd.mean()).round(2))))


if __name__ == "__main__":
    main()
