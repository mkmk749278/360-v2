"""H1 (insider cliff unlocks) and H2 (post-listing decay): daily event studies.

Entry and exit at daily closes. Short PnL in % of notional:
    gross = (P_in - P_out) / P_in
    fund  = funding settled while the position was open (a short receives it)
    net   = gross + fund - COST_RT
Hedged: the short plus an equal-notional BTC long, both legs charged.
"""
import collections
import datetime as dt
import json
import re

import numpy as np
import pandas as pd

from load import (COST_RT, DATA, END, IS_START, fmt, funding_between, klines,
                  summarize)

INSIDER = re.compile(r"team|investor|advisor|contributor|backer|seed|series|private|strategic|founder|core", re.I)
_daily = {}


def daily(sym):
    if sym not in _daily:
        _daily[sym] = klines("k1d", sym)
    return _daily[sym]


def close_on(sym, day):
    d = daily(sym)
    if d is None:
        return None, None
    ts = pd.Timestamp(day, tz="UTC")
    if ts not in d.index:
        return None, None
    # A daily bar's close is at the end of that day.
    return float(d.loc[ts, "close"]), ts + pd.Timedelta(days=1)


def short_trade(sym, day_in, day_out, hedge=True):
    p_in, t_in = close_on(sym, day_in)
    p_out, t_out = close_on(sym, day_out)
    if not p_in or not p_out:
        return None
    gross = (p_in - p_out) / p_in * 100
    fund = funding_between(sym, t_in, t_out) * 100
    if np.isnan(fund):
        return None
    row = {"sym": sym, "t_entry": t_in, "t_exit": t_out, "gross": gross, "fund": fund,
           "net": gross + fund - COST_RT}
    if hedge:
        b_in, _ = close_on("BTCUSDT", day_in)
        b_out, _ = close_on("BTCUSDT", day_out)
        bfund = funding_between("BTCUSDT", t_in, t_out) * 100
        # Long BTC leg: gains the BTC return, PAYS funding.
        row["hedged"] = row["net"] + (b_out - b_in) / b_in * 100 - bfund - COST_RT
    return row


# ── H1 ────────────────────────────────────────────────────────────────────────

def unlock_events(min_frac=0.005):
    perps = set(json.load(open(f"{DATA}/all_usdt.json")))
    idx = json.load(open(f"{DATA}/emissionsIndex.json"))["data"]
    ev = collections.defaultdict(float)
    for t in idx:
        tp = t.get("tokenPrice") or []
        sym = ((tp[0].get("symbol") if tp else "") or "").upper()
        cand = [c for c in (sym + "USDT", "1000" + sym + "USDT", "1000000" + sym + "USDT") if c in perps]
        if not cand:
            continue
        ms = t.get("maxSupply") or ((t.get("circSupply") or 0) + (t.get("totalLocked") or 0))
        if not ms:
            continue
        for e in t.get("unlockEvents", []):
            day = dt.datetime.utcfromtimestamp(e["timestamp"]).date()
            for a in e.get("cliffAllocations", []):
                if a.get("category") in ("insiders", "privateSale") or INSIDER.search(a.get("recipient") or ""):
                    ev[(cand[0], day)] += a["amount"] / ms
    return {k: v for k, v in ev.items() if v >= min_frac}, {k: v for k, v in ev.items() if v >= 0.001}


def h1():
    big, anyev = unlock_events()
    windows = {"primary [T-14, T+2]": (-14, 2), "[T-30, T]": (-30, 0),
               "[T-7, T+7]": (-7, 7), "[T, T+14]": (0, 14)}
    res = {}
    for name, (a, b) in windows.items():
        rows = []
        for (sym, day), frac in big.items():
            d_in, d_out = day + dt.timedelta(days=a), day + dt.timedelta(days=b)
            if pd.Timestamp(d_in, tz="UTC") < IS_START or pd.Timestamp(d_out, tz="UTC") >= END - pd.Timedelta(days=1):
                continue
            r = short_trade(sym, d_in, d_out)
            if r:
                r["frac"] = frac
                rows.append(r)
        res[name] = pd.DataFrame(rows)
    # Control: same tokens, entries every 7 days that sit >= 45 days from any
    # insider cliff of that token, same 16-day hold as the primary window.
    toks = {s for s, _ in big}
    near = collections.defaultdict(list)
    for (s, d) in anyev:
        near[s].append(d)
    rows = []
    day = IS_START.date()
    while pd.Timestamp(day + dt.timedelta(days=16), tz="UTC") < END - pd.Timedelta(days=1):
        for s in toks:
            mid = day + dt.timedelta(days=14)
            if all(abs((mid - e).days) >= 45 for e in near[s]):
                r = short_trade(s, day, day + dt.timedelta(days=16))
                if r:
                    rows.append(r)
        day += dt.timedelta(days=7)
    res["control (same tokens, >=45d from unlocks)"] = pd.DataFrame(rows)
    return res


# ── H2 ────────────────────────────────────────────────────────────────────────

def listings():
    """(symbol, listing day) for every USDT perp whose first archive bar is in
    the window, excluding TradFi perps by the weekend-volume rule."""
    out = []
    for sym in json.load(open(f"{DATA}/all_usdt.json")):
        d = daily(sym)
        if d is None or len(d) < 8:
            continue
        first = d.index[0]
        if not (IS_START - pd.Timedelta(days=7) <= first < END):
            continue
        head = d.iloc[:60]
        we = head[head.index.dayofweek >= 5].quote_volume.mean()
        wd = head[head.index.dayofweek < 5].quote_volume.mean()
        if not wd or np.isnan(we) or we / wd < 0.35:
            continue
        out.append((sym, first.date()))
    return out


def h2():
    lst = listings()
    grid = {"primary +7 -> +60": (7, 60), "+3 -> +30": (3, 30), "+7 -> +30": (7, 30),
            "+14 -> +90": (14, 90), "+7 -> +90": (7, 90)}
    res = {}
    for name, (a, b) in grid.items():
        rows = []
        for sym, first in lst:
            d = daily(sym)
            d_in = first + dt.timedelta(days=a)
            d_out = first + dt.timedelta(days=b)
            if pd.Timestamp(d_in, tz="UTC") < IS_START:
                continue
            if pd.Timestamp(d_out, tz="UTC") >= END - pd.Timedelta(days=1):
                continue
            # Delisted before the planned exit: exit at the last close.
            last = d.index[-1].date()
            if last < d_out:
                d_out = last
            if d_out <= d_in:
                continue
            r = short_trade(sym, d_in, d_out)
            if r:
                qv = d.loc[:pd.Timestamp(d_in, tz="UTC")].quote_volume.tail(7).mean()
                r["qv7"] = qv
                rows.append(r)
        res[name] = pd.DataFrame(rows)
    return res, lst


if __name__ == "__main__":
    print("== H1 insider cliff unlocks (>=0.5% of max supply)")
    for k, df in h1().items():
        print(fmt(summarize(df, k)))
        if len(df) and "hedged" in df:
            print(fmt(summarize(df, "   BTC-hedged", pnl="hedged")))
            print(fmt(summarize(df, "   symbol-clustered", cluster="sym")))
    print("== H2 post-listing decay")
    res, lst = h2()
    print(len(lst), "new crypto perps listed in window")
    for k, df in res.items():
        print(fmt(summarize(df, k)))
        if len(df):
            print(fmt(summarize(df, "   BTC-hedged", pnl="hedged")))
            liq = df[df.qv7 >= 10e6]
            print(fmt(summarize(liq, "   entry-liquid (7d qv >= $10M)")))
