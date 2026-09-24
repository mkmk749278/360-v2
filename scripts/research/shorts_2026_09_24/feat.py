import numpy as np
from panel import build, rolling_sum

def ema(x, n):
    a = 2.0 / (n + 1)
    out = np.full_like(x, np.nan)
    prev = np.full(x.shape[1], np.nan)
    for t in range(x.shape[0]):
        v = x[t]
        prev = np.where(np.isnan(prev), v, np.where(np.isnan(v), prev, a * v + (1 - a) * prev))
        out[t] = prev
    return out

def roll_max(x, w):
    out = np.full_like(x, np.nan)
    for t in range(w, x.shape[0]):
        out[t] = np.nanmax(x[t - w:t], axis=0)
    return out

def roll_min(x, w):
    out = np.full_like(x, np.nan)
    for t in range(w, x.shape[0]):
        out[t] = np.nanmin(x[t - w:t], axis=0)
    return out

def features():
    P = build()
    C, H, L, QV = P["C"], P["H"], P["L"], P["QV"]
    syms = list(P["syms"]); ib = syms.index("BTCUSDT")
    QV24 = rolling_sum(QV, 24)
    liq = QV24 >= 10e6
    r1 = np.clip(C / np.roll(C, 1, axis=0) - 1, -0.3, 0.3); r1[0] = np.nan
    alt = np.where(liq, r1, np.nan); alt[:, ib] = np.nan
    with np.errstate(all="ignore"):
        altr = np.nanmean(alt, axis=1)
    altidx = np.cumprod(1 + np.nan_to_num(altr))
    r24 = C / np.roll(C, 24, axis=0) - 1
    r72 = C / np.roll(C, 72, axis=0) - 1
    with np.errstate(all="ignore"):
        breadth = np.nanmean(np.where(liq, (r24 > 0).astype(float), np.nan), axis=1)
    prevC = np.roll(C, 1, axis=0)
    tr = np.nanmax(np.stack([H - L, np.abs(H - prevC), np.abs(L - prevC)]), axis=0)
    atr = ema(tr, 14)
    e20 = ema(C, 20)
    lo24 = roll_min(L, 24); hi24 = roll_max(H, 24); hi48 = roll_max(H, 48)
    hi6 = roll_max(H, 6); lo6 = roll_min(L, 6)
    qv_avg24 = rolling_sum(QV, 24) / 24.0
    F = dict(P=P, syms=syms, ib=ib, liq=liq, r1=r1, altr=altr, altidx=altidx,
             alt_e24=ema(altidx[:, None], 24)[:, 0], alt_e72=ema(altidx[:, None], 72)[:, 0],
             r24=r24, r72=r72, breadth=breadth, atr=atr, e20=e20, lo24=lo24, hi24=hi24,
             hi48=hi48, hi6=hi6, lo6=lo6, qv_avg24=qv_avg24)
    return F
