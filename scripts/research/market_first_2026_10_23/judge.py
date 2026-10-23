#!/usr/bin/env python3
"""Phase-1 judgement: calibrate the replay, pick the regime, score every cell.

    python scripts/research/market_first_2026_10_23/judge.py \\
        --book book.csv --zips bn/zip --live trades.csv --out report_dir

`--live` is the ops /track-record per-trade export (window=all).

Everything here follows §3-§4 of docs/MARKET_FIRST_METHODOLOGY_2026_10_23.md,
which fixed the criteria before this script was run:

  1. Calibration (Jun 1 - Oct 21 2026, core pairs only): per (setup, side),
     replay vs the recorded book - trades per day, net per trade, win rate - and
     a trade-level match on MOVER_TREND_PULLBACK LONG (same symbol and side,
     entry within 15 min).
  2. Regime candidates R1-R4, each judged on (a) next-24h alt-basket return
     UP vs DOWN with the same sign in both halves, (b) median run >= 3 days and
     <= 6 flips a month, (c) computable live.
  3. Cells (setup, side, state) for the chosen regime and for the time window:
     n >= 200, net > 0 in both halves, 95% bootstrap CI, profit factor, max DD.
     The number of cells tested is printed.

All market-state labels use information available before the trade: daily
labels from the previous UTC day, hourly labels from the previous closed hour.
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
sys.path.insert(0, os.path.dirname(__file__))

from replay import load_tf  # noqa: E402
from src.btc_state import compute_btc_state, macro_direction  # noqa: E402

SPLIT = pd.Timestamp("2026-04-06", tz="UTC")  # same split as study.py
CAL_START = pd.Timestamp("2026-06-01", tz="UTC")
MIN_N = 200
RNG = np.random.default_rng(7)  # seeded so the CI is reproducible


def daily_closes(zips: str, symbols: list) -> pd.DataFrame:
    out = {}
    for s in symbols:
        d = load_tf(zips, s, "1d")
        if d:
            out[s] = pd.Series(d["close"], index=pd.to_datetime(d["open_time"], unit="ms", utc=True))
    return pd.DataFrame(out).sort_index()


def r1(btc: pd.Series) -> pd.Series:
    sma = btc.rolling(20).mean()
    up = (btc > sma) & (sma > sma.shift(5))
    dn = (btc < sma) & (sma < sma.shift(5))
    lab = pd.Series(np.where(up, "UP", np.where(dn, "DOWN", "RANGE")), index=btc.index)
    lab[sma.isna()] = None
    return lab


def r2(btc: pd.Series) -> pd.Series:
    """Engine macro_direction on BTC daily closes (live runs it on weekly)."""
    vals = btc.values
    out = []
    for i in range(len(vals)):
        m = macro_direction(vals[: i + 1])
        reg = m["regime"]
        out.append(None if m["status"] == "insufficient_data" else
                   "UP" if reg in ("BULL", "RECOVERY") else "DOWN" if reg == "DECLINE" else "RANGE")
    return pd.Series(out, index=btc.index)


def r4(closes: pd.DataFrame) -> pd.Series:
    sma = closes.rolling(20).mean()
    valid = sma.notna()
    above = ((closes > sma) & valid).sum(1).astype(float)
    share = above / valid.sum(1).replace(0, np.nan)
    lab = pd.Series(np.where(share > 0.6, "UP", np.where(share < 0.4, "DOWN", "RANGE")), index=closes.index)
    lab[valid.sum(1) < 20] = None
    return lab


def r3_hourly(zips: str) -> pd.Series:
    """btc_state b on BTC 5m/15m/1h, read every closed hour, bucketed at +/-0.33."""
    tf = {k: load_tf(zips, "BTCUSDT", k) for k in ("5m", "15m", "1h")}
    h = tf["1h"]
    labs, idx = [], []
    for n in range(200, len(h["close"])):
        t = h["close_time"][n - 1]
        win = {}
        for k, s in tf.items():
            m = int(np.searchsorted(s["close_time"], t, side="right"))
            win[k] = {f: np.asarray(s[f][max(0, m - 300):m]) for f in ("open", "high", "low", "close")}
        b = float(compute_btc_state(win)["b"])
        labs.append("UP" if b > 0.33 else "DOWN" if b < -0.33 else "RANGE")
        idx.append(pd.Timestamp(int(t) + 1, unit="ms", tz="UTC"))
    return pd.Series(labs, index=idx)


def regime_quality(lab: pd.Series, basket_fwd: pd.Series, freq_days: float) -> dict:
    """Criteria (a) and (b). `basket_fwd` is the next-24h basket return aligned to lab."""
    df = pd.DataFrame({"lab": lab, "fwd": basket_fwd}).dropna()
    res = {}
    for half, part in (("H1", df[df.index < SPLIT]), ("H2", df[df.index >= SPLIT])):
        g = part.groupby("lab").fwd.mean()
        res[half] = round(float(g.get("UP", np.nan) - g.get("DOWN", np.nan)) * 100, 3)
    runs = (lab != lab.shift()).cumsum()
    run_len = lab.groupby(runs).size() * freq_days
    months = (lab.index.max() - lab.index.min()).days / 30.4
    res["median_run_days"] = round(float(run_len.median()), 2)
    res["flips_per_month"] = round(float((lab != lab.shift()).sum() / months), 1)
    res["a_pass"] = bool(res["H1"] > 0 and res["H2"] > 0)
    res["b_pass"] = bool(res["median_run_days"] >= 3 and res["flips_per_month"] <= 6)
    return res


def cell_stats(x: pd.Series) -> dict:
    v = x.values
    boot = RNG.choice(v, size=(2000, len(v))).mean(1)
    cum = np.cumsum(v)
    gains, losses = v[v > 0].sum(), -v[v < 0].sum()
    return {"n": len(v), "avg": round(v.mean(), 3), "ci_lo": round(np.percentile(boot, 2.5), 3),
            "ci_hi": round(np.percentile(boot, 97.5), 3), "win": round((v > 0).mean(), 3),
            "pf": round(gains / losses, 2) if losses > 0 else np.inf,
            "max_dd": round(float(np.max(np.maximum.accumulate(cum) - cum)), 1)}


def judge_cells(b: pd.DataFrame, col: str) -> pd.DataFrame:
    rows = []
    for (setup, side, st), g in b.groupby(["setup", "direction", col]):
        s = cell_stats(g.net_pct)
        h1 = g[g.entry_time < SPLIT].net_pct
        h2 = g[g.entry_time >= SPLIT].net_pct
        s.update(setup=setup, side=side, state=st, h1_n=len(h1), h1_avg=round(h1.mean(), 3) if len(h1) else np.nan,
                 h2_n=len(h2), h2_avg=round(h2.mean(), 3) if len(h2) else np.nan)
        s["pass"] = bool(s["n"] >= MIN_N and len(h1) and len(h2) and h1.mean() > 0 and h2.mean() > 0)
        rows.append(s)
    cols = ["setup", "side", "state", "n", "avg", "ci_lo", "ci_hi", "win", "pf", "max_dd",
            "h1_n", "h1_avg", "h2_n", "h2_avg", "pass"]
    if not rows:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(rows)[cols].sort_values(["setup", "side", "state"])


def time_window(ts: pd.Series) -> pd.Series:
    h, wd = ts.dt.hour, ts.dt.dayofweek
    return np.where(wd >= 5, "WEEKEND",
                    np.where((h >= 8) & (h < 21), "ACTIVE",
                             np.where((h >= 4) & (h < 8), "QUIET", "OFF_HOURS")))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", required=True)
    ap.add_argument("--zips", required=True)
    ap.add_argument("--live", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    pd.set_option("display.width", 220)
    pd.set_option("display.max_rows", 400)

    b = pd.read_csv(a.book)
    b["entry_time"] = pd.to_datetime(b.entry_time, utc=True)
    symbols = sorted(b.symbol.unique().tolist() + ["BTCUSDT"])

    # ---- 1. calibration ---------------------------------------------------
    live = pd.read_csv(a.live, parse_dates=["entry_iso"])
    live = live[(live.entry_iso >= CAL_START) & (live.pair_admission == "CORE")
                & live.symbol.isin(b.symbol.unique())]
    rep = b[b.entry_time >= CAL_START]
    days = (rep.entry_time.max() - CAL_START).days or 1
    cal = pd.DataFrame({
        "live_n": live.groupby(["setup", "direction"]).size(),
        "live_avg": live.groupby(["setup", "direction"]).net_pct.mean().round(3),
        "live_win": live.groupby(["setup", "direction"]).pnl_pct.apply(lambda s: (s > 0).mean()).round(3),
        "rep_n": rep.groupby(["setup", "direction"]).size(),
        "rep_avg": rep.groupby(["setup", "direction"]).net_pct.mean().round(3),
        "rep_win": rep.groupby(["setup", "direction"]).pnl_pct.apply(lambda s: (s > 0).mean()).round(3),
    }).fillna(0)
    cal["rep_per_live"] = (cal.rep_n / cal.live_n.replace(0, np.nan)).round(1)
    cal["sign_match"] = np.sign(cal.live_avg) == np.sign(cal.rep_avg)
    print(f"== 1. CALIBRATION {CAL_START.date()} -> {rep.entry_time.max().date()} ({days} d), core pairs")
    print(cal.to_string())
    cal.to_csv(os.path.join(a.out, "calibration.csv"))

    # trade-level match on the path that is 60% of the book
    lm = live[(live.setup == "MOVER_TREND_PULLBACK") & (live.direction == "LONG")]
    rm = rep[(rep.setup == "MOVER_TREND_PULLBACK") & (rep.direction == "LONG")]
    cand = b[(b.setup == "MOVER_TREND_PULLBACK") & (b.direction == "LONG")]
    matched, out_agree = 0, 0
    for r in lm.itertuples():
        m = cand[(cand.symbol == r.symbol) & ((cand.entry_time - r.entry_iso).abs() <= pd.Timedelta(minutes=15))]
        if len(m):
            matched += 1
            out_agree += int(np.sign(m.pnl_pct.iloc[0]) == np.sign(r.pnl_pct))
    print(f"MVRTP LONG trade match: {matched}/{len(lm)} live signals found in the replay book "
          f"({matched / max(1, len(lm)):.0%}); same win/loss sign on {out_agree}/{max(1, matched)}; "
          f"replay book has {len(rm)} in the window")

    # ---- 2. regime candidates ---------------------------------------------
    closes = daily_closes(a.zips, symbols)
    rets = np.log(closes).diff()
    basket_next = rets.drop(columns=["BTCUSDT"]).mean(1).shift(-1)  # day d+1, labelled at d
    btc = closes.BTCUSDT
    # daily labels computed on day d's close are used on day d+1 -> shift(1)
    lab = {"R1": r1(btc), "R2": r2(btc), "R4": r4(closes.drop(columns=["BTCUSDT"]))}
    lab["R1+R4"] = pd.Series(np.where(lab["R1"] == lab["R4"], lab["R1"], "RANGE"), index=btc.index)
    lab["R1+R4"][lab["R1"].isna() | lab["R4"].isna()] = None
    window_lo = b.entry_time.min().normalize() - pd.Timedelta(days=1)
    qual = {}
    for k, v in lab.items():
        v = v[v.index >= window_lo]
        qual[k] = regime_quality(v, basket_next.reindex(v.index), 1.0)
    h3 = r3_hourly(a.zips)
    hourly_basket = None  # R3 judged on the same daily basket, using the label at each day's open
    d3 = h3[h3.index.hour == 0]
    d3.index = d3.index.normalize()
    qual["R3"] = regime_quality(d3[d3.index >= window_lo], basket_next.reindex(d3.index), 1.0)
    q = pd.DataFrame(qual).T
    print("\n== 2. REGIME CANDIDATES (UP-DOWN next-day basket spread %, by half)")
    print(q.to_string())
    q.to_csv(os.path.join(a.out, "regimes.csv"))
    del hourly_basket

    # stamp every trade with every candidate (yesterday's daily label; R3 = last closed hour)
    day_prev = b.entry_time.dt.floor("D") - pd.Timedelta(days=1)
    for k, v in lab.items():
        b[k] = day_prev.map(v)
    b["R3"] = pd.merge_asof(b[["entry_time"]].sort_values("entry_time"),
                            h3.rename("R3").to_frame().reset_index().rename(columns={"index": "t"}),
                            left_on="entry_time", right_on="t", direction="backward").set_index(
        b.sort_values("entry_time").index).R3
    b["window"] = time_window(b.entry_time)
    b.to_csv(os.path.join(a.out, "book_stamped.csv"), index=False)

    # ---- 3. cells --------------------------------------------------------
    print("\n== 3. CELLS (net % per trade after 0.07% fee)")
    for col in ["R1", "R2", "R3", "R4", "R1+R4", "window"]:
        c = judge_cells(b.dropna(subset=[col]), col)
        c.to_csv(os.path.join(a.out, f"cells_{col}.csv"), index=False)
        big = c[c.n >= MIN_N]
        print(f"\n-- by {col}: {len(c)} cells, {len(big)} with n>={MIN_N}, {int(c['pass'].sum())} pass")
        print(big.to_string(index=False))
    print("\n-- whole book by path (no state)")
    print(judge_cells(b.assign(all="ALL"), "all").to_string(index=False))


if __name__ == "__main__":
    main()
