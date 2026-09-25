"""Loaders and the shared trade/statistics helpers.

Everything is read from the archive files `fetch.py` wrote. Timestamps are
UTC milliseconds throughout. Some archive files carry microsecond timestamps
(2025+ spot); `_ms` normalises them.
"""
import glob
import json
import os
import zipfile
from functools import lru_cache

import numpy as np
import pandas as pd

DATA = os.environ.get("SHORTS_MKT_DIR", os.path.expanduser("~/shorts_data"))

IS_START = pd.Timestamp("2025-09-08", tz="UTC")
OOS_START = pd.Timestamp("2026-05-01", tz="UTC")
END = pd.Timestamp("2026-09-01", tz="UTC")  # exclusive; funding ends 2026-08-31

FEE_RT = 0.07      # % round trip
SLIP_RT = 0.10     # % round trip (0.05 per fill)
COST_RT = FEE_RT + SLIP_RT

KCOLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
         "quote_volume", "count", "taker_buy_volume", "taker_buy_quote", "ignore"]


def _ms(x):
    x = np.asarray(x, dtype="int64")
    return np.where(x > 1e14, x // 1000, x)


def _csv(path, names=None):
    with zipfile.ZipFile(path) as z:
        with z.open(z.namelist()[0]) as f:
            df = pd.read_csv(f, header=None, names=names, low_memory=False)
    first = str(df.iloc[0, 0])
    if not first.lstrip("-").replace(".", "").isdigit():
        df = df.iloc[1:].reset_index(drop=True)
    return df


def klines(sub, sym):
    """OHLCV frame indexed by UTC open time, from every file of one symbol."""
    files = sorted(glob.glob(f"{DATA}/{sub}/{sym}-*.zip"))
    if not files:
        return None
    df = pd.concat([_csv(f, KCOLS) for f in files], ignore_index=True)
    for c in KCOLS[:11]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["t"] = pd.to_datetime(_ms(df.open_time), unit="ms", utc=True)
    df = df.drop_duplicates("t").set_index("t").sort_index()
    return df[["open", "high", "low", "close", "volume", "quote_volume", "taker_buy_volume", "taker_buy_quote"]]


@lru_cache(maxsize=None)
def funding(sym):
    """Series of settled funding rates (fraction per interval) at settlement time."""
    files = sorted(glob.glob(f"{DATA}/fund/{sym}-fundingRate-*.zip"))
    if not files:
        return pd.Series(dtype=float)
    df = pd.concat([_csv(f, ["calc_time", "interval_h", "rate"]) for f in files], ignore_index=True)
    df["calc_time"] = pd.to_numeric(df.calc_time)
    # Settlement stamps drift a few ms; round to the minute.
    t = pd.to_datetime(_ms(df.calc_time), unit="ms", utc=True).round("min")
    s = pd.Series(pd.to_numeric(df.rate).values, index=t)
    return s[~s.index.duplicated()].sort_index()


def funding_between(sym, t_in, t_out):
    """Sum of funding rates settling in (t_in, t_out]. A short RECEIVES this sum."""
    f = funding(sym)
    if f.empty:
        return np.nan
    return float(f[(f.index > t_in) & (f.index <= t_out)].sum())


def metrics(sym, raw=False):
    """5-minute metrics, RE-TIMED to when each value is actually true.

    Measured (`oi_stamp_check.py`): the OI change stamped at s correlates with
    the price bar STARTING at s (mean 0.093 over 16 symbols, highest for every
    one of them), not the bar ending at s (0.024). So a row stamped s reports
    the state at s + 5m. Read at its stamp, it leaks five minutes of the
    future. The first H10 run did exactly that and "passed". Every consumer
    therefore sees the index shifted +5m.
    """
    files = sorted(glob.glob(f"{DATA}/metrics/{sym}/*.zip"))
    if not files:
        return None
    names = ["create_time", "symbol", "oi", "oi_value", "top_acct_ratio", "top_pos_ratio",
             "global_acct_ratio", "taker_ratio"]
    parts = []
    for f in files:
        try:
            parts.append(_csv(f, names))
        except Exception:
            continue
    df = pd.concat(parts, ignore_index=True)
    df["t"] = pd.to_datetime(df.create_time, utc=True, errors="coerce")
    df = df.dropna(subset=["t"]).drop_duplicates("t").set_index("t").sort_index()
    if not raw:
        df.index = df.index + pd.Timedelta(minutes=5)
    for c in names[2:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df[names[2:]]


def universe():
    return json.load(open(f"{DATA}/liquid.json"))


def half(ts):
    return "IS" if ts < OOS_START else "OOS"


# ── statistics ────────────────────────────────────────────────────────────────

def cluster_ci(values, clusters, n_boot=4000, seed=20260925):
    """95% CI of the mean, bootstrapping whole clusters (days or symbols)."""
    v = np.asarray(values, float)
    c = np.asarray(clusters)
    if len(v) < 5:
        return (np.nan, np.nan)
    keys, inv = np.unique(c, return_inverse=True)
    sums = np.bincount(inv, weights=v)
    cnts = np.bincount(inv)
    rng = np.random.default_rng(seed)
    k = len(keys)
    idx = rng.integers(0, k, size=(n_boot, k))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return tuple(np.percentile(means, [2.5, 97.5]))


def summarize(trades, label, pnl="net", cluster="day"):
    """One line per half and overall. `trades` needs columns: t_entry, sym, and
    the pnl column (short PnL in %, positive = the short made money)."""
    if trades is None or len(trades) == 0:
        return {"label": label, "n": 0}
    t = trades.copy()
    t["day"] = t.t_entry.dt.floor("D")
    t["half"] = [half(x) for x in t.t_entry]
    lo, hi = cluster_ci(t[pnl], t[cluster])
    out = {
        "label": label, "n": len(t), "syms": t.sym.nunique(),
        "mean": round(t[pnl].mean(), 3), "ci": (round(lo, 3), round(hi, 3)),
        "win": round((t[pnl] > 0).mean(), 3),
        "IS": round(t.loc[t.half == "IS", pnl].mean(), 3), "n_IS": int((t.half == "IS").sum()),
        "OOS": round(t.loc[t.half == "OOS", pnl].mean(), 3), "n_OOS": int((t.half == "OOS").sum()),
    }
    if "gross" in t:
        out["gross"] = round(t.gross.mean(), 3)
    if "fund" in t:
        out["fund"] = round(t.fund.mean(), 3)
    out["passes"] = bool(out["IS"] > 0 and out["OOS"] > 0 and lo > 0)
    return out


def fmt(r):
    if r.get("n", 0) == 0:
        return f"{r['label']:<48} n=0"
    extra = ""
    if "gross" in r:
        extra = f" gross {r['gross']:+.3f} fund {r.get('fund', 0):+.3f}"
    return (f"{r['label']:<48} n={r['n']:>5} syms={r['syms']:>4} net {r['mean']:+.3f}% "
            f"CI[{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}] win {r['win']:.2f} "
            f"IS {r['IS']:+.3f} (n={r['n_IS']}) OOS {r['OOS']:+.3f} (n={r['n_OOS']}){extra}"
            f"{'  PASS' if r['passes'] else ''}")
