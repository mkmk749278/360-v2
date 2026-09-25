"""H6 (funding settlement), H8 (weekly loser momentum), H9 (time of day),
H10 (liquidation burst) — rules as pre-registered in HYPOTHESES.md."""
import numpy as np
import pandas as pd

from load import COST_RT, END, IS_START, fmt, funding, klines, metrics, summarize, universe
from events import daily

LIQ_MIN = 10e6


def liquid_on(sym, ts):
    d = daily(sym)
    if d is None:
        return False
    q = d.quote_volume.loc[:ts - pd.Timedelta(days=1)].tail(7)
    return len(q) >= 5 and q.mean() >= LIQ_MIN


# ── H6 ────────────────────────────────────────────────────────────────────────

def h6(sym, use_prev=False):
    k = klines("k5m", sym)
    f = funding(sym)
    if k is None or f.empty:
        return [], []
    dq = daily(sym)
    qv = (dq.quote_volume.rolling(7, min_periods=5).mean().shift(1)) if dq is not None else None
    setup, ctrl = [], []
    prev = f.shift(1)
    for t, rate in f[(f.index >= IS_START) & (f.index < END)].items():
        # Post-hoc correction (see RESULTS): select on the PREVIOUS settled
        # rate, which is known at entry. The realised rate at T is set by the
        # premium during the hold itself, so selecting on it is look-ahead.
        sel = prev.loc[t] if use_prev else rate
        t_in, t_out_bar = t - pd.Timedelta(minutes=60), t
        if t_in not in k.index or t_out_bar not in k.index:
            continue
        day = t.floor("D")
        if qv is None or day not in qv.index or not (qv.loc[day] >= LIQ_MIN):
            continue
        p_in = k.loc[t_in, "open"]
        p_out = k.loc[t_out_bar, "close"]  # close of the bar opening at T = T+5m
        gross = (p_in - p_out) / p_in * 100
        row = {"sym": sym, "t_entry": t_in, "gross": gross, "fund": rate * 100,
               "net": gross + rate * 100 - COST_RT}
        if np.isnan(sel):
            continue
        if sel >= 0.0005:
            setup.append(row)
        elif -0.00005 <= sel <= 0.0001:
            ctrl.append(row)
    return setup, ctrl


# ── H8 ────────────────────────────────────────────────────────────────────────

def h8(syms):
    closes = {}
    for s in syms:
        d = daily(s)
        if d is not None:
            closes[s] = d.close
    px = pd.DataFrame(closes).sort_index()
    qv = pd.DataFrame({s: daily(s).quote_volume for s in closes}).sort_index()
    qv7 = qv.rolling(7, min_periods=5).mean().shift(1)
    mondays = [t for t in px.index if t.dayofweek == 0 and IS_START <= t and t + pd.Timedelta(days=7) < END]
    short_leg, spread, vs_ew = [], [], []
    for t in mondays:
        # Decision at Monday 00:00 = the close of Sunday's bar.
        t_dec = t - pd.Timedelta(days=1)
        if t_dec not in px.index:
            continue
        elig = [s for s in px.columns if qv7.loc[t_dec, s] >= LIQ_MIN and not np.isnan(px.loc[t_dec, s])
                and t_dec - pd.Timedelta(days=14) in px.index and not np.isnan(px.loc[t_dec - pd.Timedelta(days=14), s])]
        if len(elig) < 30:
            continue
        form = px.loc[t_dec, elig] / px.loc[t_dec - pd.Timedelta(days=14), elig] - 1
        t_exit = t_dec + pd.Timedelta(days=7)
        fwd = px.loc[t_exit, elig] / px.loc[t_dec, elig] - 1
        ok = fwd.dropna().index
        form, fwd = form[ok], fwd[ok]
        dec = max(1, len(ok) // 10)
        losers = form.nsmallest(dec).index
        winners = form.nlargest(dec).index
        t_in, t_out = t, t + pd.Timedelta(days=7)
        for s in losers:
            fsum = funding(s)
            fr = fsum[(fsum.index > t_in) & (fsum.index <= t_out)].sum() * 100 if len(fsum) else 0.0
            short_leg.append({"sym": s, "t_entry": t_in, "gross": -fwd[s] * 100, "fund": fr,
                              "net": -fwd[s] * 100 + fr - COST_RT})
        ew = fwd.mean() * 100
        vs_ew.append({"sym": "basket", "t_entry": t_in,
                      "net": -fwd[losers].mean() * 100 + ew - 2 * COST_RT})
        spread.append({"sym": "basket", "t_entry": t_in,
                       "net": (fwd[winners].mean() - fwd[losers].mean()) * 100 - 2 * COST_RT})
    return pd.DataFrame(short_leg), pd.DataFrame(vs_ew), pd.DataFrame(spread)


# ── H9 ────────────────────────────────────────────────────────────────────────

def h9(syms):
    """Equal-weight basket of liquid alts (BTC and ETH excluded), 5m bars."""
    rets = {}
    for s in syms:
        if s in ("BTCUSDT", "ETHUSDT"):
            continue
        k = klines("k5m", s)
        if k is None:
            continue
        r = np.log(k.close / k.open)
        dq = daily(s)
        liq = dq.quote_volume.rolling(7, min_periods=5).mean().shift(1).reindex(r.index.floor("D")).values >= LIQ_MIN
        rets[s] = r.where(liq)
    R = pd.DataFrame(rets)
    basket = R.mean(axis=1)
    basket = basket[(basket.index >= IS_START) & (basket.index < END)]
    rows_us, rows_mon = [], []
    for day, g in basket.groupby(basket.index.floor("D")):
        m = g.index.hour * 60 + g.index.minute
        if day.dayofweek < 5:
            w = g[(m >= 13 * 60 + 30) & (m < 15 * 60 + 30)]
            if len(w) >= 20:
                gross = -(np.exp(w.sum()) - 1) * 100
                rows_us.append({"sym": "basket", "t_entry": day, "gross": gross, "net": gross - COST_RT})
    for day, g in basket.groupby(basket.index.floor("D")):
        if day.dayofweek == 6:  # Sunday: window Sun 23:00 -> Mon 23:00
            w = basket[(basket.index >= day + pd.Timedelta(hours=23)) & (basket.index < day + pd.Timedelta(hours=47))]
            if len(w) >= 250:
                gross = -(np.exp(w.sum()) - 1) * 100
                rows_mon.append({"sym": "basket", "t_entry": day, "gross": gross, "net": gross - COST_RT})
    return pd.DataFrame(rows_us), pd.DataFrame(rows_mon)


# ── H10 ───────────────────────────────────────────────────────────────────────

def h10(sym):
    k = klines("k5m", sym)
    m = metrics(sym)
    if k is None or m is None or len(m) < 1000:
        return [], []
    oi = m.oi.reindex(k.index + pd.Timedelta(minutes=5), method="ffill")
    oi.index = k.index  # OI known at each bar's close
    d_oi = oi / oi.shift(3) - 1
    d_px = k.close / k.close.shift(3) - 1
    dq = daily(sym)
    liq = pd.Series(dq.quote_volume.rolling(7, min_periods=5).mean().shift(1).reindex(k.index.floor("D")).values,
                    index=k.index) >= LIQ_MIN
    ev = (d_oi <= -0.015) & (d_px <= -0.02) & liq
    o, c = k.open.values, k.close.values
    idx = k.index
    fund = funding(sym)
    shorts, longs, busy = [], [], -1
    for i in np.flatnonzero(ev.fillna(False).values):
        if i <= busy or i + 12 >= len(k):
            continue
        t_in = idx[i + 1]
        if t_in < IS_START or t_in >= END:
            continue
        p_in, p_out = o[i + 1], c[i + 12]
        t_out = idx[i + 12] + pd.Timedelta(minutes=5)
        fr = fund[(fund.index > t_in) & (fund.index <= t_out)].sum() * 100 if len(fund) else 0.0
        g = (p_in - p_out) / p_in * 100
        shorts.append({"sym": sym, "t_entry": t_in, "gross": g, "fund": fr, "net": g + fr - COST_RT})
        longs.append({"sym": sym, "t_entry": t_in, "gross": -g, "fund": -fr, "net": -g - fr - COST_RT})
        busy = i + 12
    return shorts, longs


if __name__ == "__main__":
    import sys
    syms = universe()
    which = sys.argv[1:] or ["H6", "H8", "H9", "H10"]
    if "H8" in which:
        a, b, c = h8(syms)
        print(fmt(summarize(a, "H8 short bottom decile (14d), hold 7d")))
        print(fmt(summarize(b, "H8 short losers vs long EW universe")))
        print(fmt(summarize(c, "H8 long winners / short losers")))
    if "H6" in which:
        S, C = [], []
        for s in syms:
            a, b = h6(s)
            S += a
            C += b
        print(fmt(summarize(pd.DataFrame(S), "H6 funding >= 0.05%: short T-60m -> T+5m")))
        print(fmt(summarize(pd.DataFrame(C), "H6 control funding ~0")))
    if "H6b" in which:
        S, C = [], []
        for s in syms:
            a, b = h6(s, use_prev=True)
            S += a
            C += b
        print(fmt(summarize(pd.DataFrame(S), "H6b prev funding >= 0.05%: short T-60m -> T+5m")))
        print(fmt(summarize(pd.DataFrame(C), "H6b control prev funding ~0")))
    if "H9" in which:
        us, mon = h9(syms)
        print(fmt(summarize(us, "H9 short alt basket 13:30-15:30 UTC")))
        print(fmt(summarize(mon, "H9 short alt basket Sun23-Mon23 (expect loss)")))
    if "H10" in which:
        S, L = [], []
        for s in syms:
            a, b = h10(s)
            S += a
            L += b
        print(fmt(summarize(pd.DataFrame(S), "H10 short after long-liquidation burst, 1h")))
        print(fmt(summarize(pd.DataFrame(L), "H10 long after long-liquidation burst, 1h")))
