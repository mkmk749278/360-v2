"""H3–H10: intraday hypotheses on 1h (and 5m) bars.

Common trade rules (pre-registered in HYPOTHESES.md):
  * decision at a bar close, entry at the NEXT bar's open;
  * a stop, where the hypothesis has one, is checked on every bar's high
    before any other exit (a bar touching the stop is booked as a stop, at the
    stop, or at the open if it gapped through);
  * one open position per symbol: triggers while a position is open are
    skipped, so overlapping entries into one move are not counted twice;
  * point-in-time liquidity: trailing-7d mean daily quote volume >= $10M;
  * costs: COST_RT round trip + actual funding while open.
"""
import numpy as np
import pandas as pd

from load import COST_RT, END, IS_START, funding, klines, metrics, universe

LIQ_MIN = 10e6


def hourly(sym, with_metrics=True):
    """1h futures bars + spot taker flow + premium + metrics, aligned on the hour."""
    f = klines("k1h", sym)
    if f is None or len(f) < 24 * 40:
        return None
    df = f.copy()
    df["qv_d"] = df.quote_volume.rolling(24 * 7, min_periods=24 * 5).sum() / 7
    sp = klines("spot1h", sym)
    if sp is not None:
        df["spot_qv"] = sp.quote_volume.reindex(df.index)
        df["spot_tb"] = sp.taker_buy_quote.reindex(df.index)
    pr = klines("prem1h", sym)
    if pr is not None:
        df["prem"] = pr.close.reindex(df.index)
    m = metrics(sym) if with_metrics else None
    if m is not None and len(m):
        # Metrics are stamped at the end of each 5m bucket; the value known at
        # an hour's CLOSE is the one stamped at or before open + 1h.
        mh = m.resample("1h", label="left", closed="right").last()
        df = df.join(mh, how="left")
    return df


def simulate_short(df, sym, entries, hold_bars, stop_price=None):
    """entries: list of integer positions (decision bars). Entry at open[i+1].
    stop_price: callable(i, entry_price) -> stop level, or None."""
    o, h, c = df.open.values, df.high.values, df.close.values
    idx = df.index
    fund = funding(sym)
    trades, busy_until = [], -1
    n = len(df)
    for i in entries:
        if i <= busy_until or i + 1 >= n:
            continue
        e = i + 1
        t_in = idx[e]
        if t_in < IS_START or t_in >= END:
            continue
        p_in = o[e]
        if not p_in or np.isnan(p_in):
            continue
        stop = stop_price(i, p_in) if stop_price else None
        last = min(e + hold_bars - 1, n - 1)
        exit_p, exit_i, why = c[last], last, "time"
        for j in range(e, last + 1):
            if stop is not None and h[j] >= stop:
                exit_p = max(stop, o[j]) if j > e else max(stop, p_in)
                exit_i, why = j, "stop"
                break
        t_out = idx[exit_i] + pd.Timedelta(hours=1)
        if t_out > END:
            continue
        f = fund[(fund.index > t_in) & (fund.index <= t_out)].sum() * 100 if len(fund) else np.nan
        if np.isnan(f):
            continue
        gross = (p_in - exit_p) / p_in * 100
        trades.append({"sym": sym, "t_entry": t_in, "t_exit": t_out, "gross": gross, "fund": f,
                       "net": gross + f - COST_RT, "exit": why})
        busy_until = exit_i
    return trades


def atr(df, n=24):
    tr = np.maximum(df.high - df.low, np.maximum((df.high - df.close.shift()).abs(),
                                                 (df.low - df.close.shift()).abs()))
    return tr.rolling(n).mean()


# ── H3 leverage without progress, then breakdown ──────────────────────────────

def h3(df, sym):
    if "oi" not in df or df.oi.isna().mean() > 0.5:
        return [], []
    oi_chg = df.oi / df.oi.shift(24) - 1
    oi_p80 = oi_chg.rolling(24 * 30, min_periods=24 * 20).quantile(0.8)
    oi_p50 = oi_chg.rolling(24 * 30, min_periods=24 * 20).quantile(0.5)
    px24 = df.close / df.close.shift(24) - 1
    low24 = df.low.rolling(24).min().shift(1)
    fund = funding(sym)
    last_fund = fund.reindex(df.index, method="ffill") if len(fund) else pd.Series(np.nan, index=df.index)
    trig = (df.close < low24) & (df.qv_d >= LIQ_MIN)
    flat = px24.abs() <= 0.03
    setup = trig & flat & (oi_chg >= oi_p80) & (oi_chg >= 0.05) & (last_fund >= 0)
    ctrl = trig & flat & (oi_chg <= oi_p50)
    a = atr(df)
    stop = lambda i, p: p + 1.0 * a.iloc[i]
    pos = lambda m: list(np.flatnonzero(m.fillna(False).values))
    return (simulate_short(df, sym, pos(setup), 12, stop),
            simulate_short(df, sym, pos(ctrl), 12, stop))


# ── H4 perp-led rally with no spot buying, then failure ───────────────────────

def h4(df, sym):
    if "spot_tb" not in df or df.spot_tb.isna().mean() > 0.5 or "oi" not in df:
        return [], []
    r24 = df.close / df.close.shift(24) - 1
    fut_net = (2 * df.taker_buy_quote - df.quote_volume).rolling(24).sum() / df.quote_volume.rolling(24).sum()
    spot_net = (2 * df.spot_tb - df.spot_qv).rolling(24).sum() / df.spot_qv.rolling(24).sum()
    oi_up = df.oi / df.oi.shift(24) - 1 > 0
    base = (r24 >= 0.08) & (df.qv_d >= LIQ_MIN) & oi_up
    setup = base & (fut_net >= 0.04) & (spot_net <= 0)
    ctrl = base & (spot_net >= 0.04)
    lo, hi = df.low.values, df.high.values
    c = df.close.values

    def triggers(mask):
        out, m = [], mask.fillna(False).values
        for s in np.flatnonzero(m):
            peak = hi[s]
            for k in range(s + 1, min(s + 13, len(c))):
                peak = max(peak, hi[k])
                if c[k] < lo[k - 1]:
                    out.append((k, peak))
                    break
        return out

    def run(mask):
        tr = triggers(mask)
        peaks = dict(tr)
        return simulate_short(df, sym, [k for k, _ in tr], 24, lambda i, p: max(peaks[i] * 1.002, p * 1.002))
    return run(setup), run(ctrl)


# ── H5 perp premium dislocation ───────────────────────────────────────────────

def h5(df, sym):
    if "prem" not in df or df.prem.isna().mean() > 0.5:
        return [], []
    q99 = df.prem.rolling(24 * 30, min_periods=24 * 20).quantile(0.99)
    q40 = df.prem.rolling(24 * 30, min_periods=24 * 20).quantile(0.40)
    q60 = df.prem.rolling(24 * 30, min_periods=24 * 20).quantile(0.60)
    liq = df.qv_d >= LIQ_MIN
    setup = liq & (df.prem >= 0.0025) & (df.prem >= q99)
    ctrl = liq & (df.prem >= q40) & (df.prem <= q60)
    pos = lambda m: list(np.flatnonzero(m.fillna(False).values))
    return simulate_short(df, sym, pos(setup), 8), simulate_short(df, sym, pos(ctrl)[::24], 8)


# ── H7 retail crowding vs top traders ─────────────────────────────────────────

def h7(df, sym):
    if "global_acct_ratio" not in df or df.global_acct_ratio.isna().mean() > 0.5:
        return [], []
    g = df.global_acct_ratio
    q90 = g.rolling(24 * 30, min_periods=24 * 20).quantile(0.9)
    q40 = g.rolling(24 * 30, min_periods=24 * 20).quantile(0.4)
    q60 = g.rolling(24 * 30, min_periods=24 * 20).quantile(0.6)
    top_fell = df.top_pos_ratio < df.top_pos_ratio.shift(24)
    liq = df.qv_d >= LIQ_MIN
    setup = liq & (g >= q90) & top_fell
    ctrl = liq & (g >= q40) & (g <= q60)
    pos = lambda m: list(np.flatnonzero(m.fillna(False).values))
    return simulate_short(df, sym, pos(setup), 24), simulate_short(df, sym, pos(ctrl)[::6], 24)


HYPS = {"H3": h3, "H4": h4, "H5": h5, "H7": h7}


def run_all(syms=None, which=None):
    syms = syms or universe()
    hyps = {k: v for k, v in HYPS.items() if not which or k in which}
    need_m = any(k in hyps for k in ("H3", "H4", "H7"))
    out = {k: ([], []) for k in hyps}
    for n, sym in enumerate(syms):
        try:
            df = hourly(sym, with_metrics=need_m)
        except Exception as exc:  # a malformed archive file: skip the symbol, say so
            print("skip", sym, exc)
            continue
        if df is None:
            continue
        for k, fn in hyps.items():
            a, b = fn(df, sym)
            out[k][0].extend(a)
            out[k][1].extend(b)
        if n % 50 == 0:
            print(n, sym, {k: (len(v[0]), len(v[1])) for k, v in out.items()}, flush=True)
    return {k: (pd.DataFrame(a), pd.DataFrame(b)) for k, (a, b) in out.items()}


if __name__ == "__main__":
    import pickle
    import sys
    from load import DATA, fmt, summarize
    which = sys.argv[1:] or list(HYPS)
    res = run_all(which=which)
    pickle.dump(res, open(f"{DATA}/intraday_{'_'.join(which)}.pkl", "wb"))
    for k, (a, b) in res.items():
        print(fmt(summarize(a, f"{k} setup")))
        print(fmt(summarize(b, f"{k} control")))
