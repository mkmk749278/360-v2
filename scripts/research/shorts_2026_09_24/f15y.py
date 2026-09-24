import numpy as np, collections
import m15y as M
T, N = M.C.shape
def roll(x, w, fn):
    out = np.full_like(x, np.nan)
    for t in range(w, x.shape[0]): out[t] = fn(x[t - w:t], axis=0)
    return out
LO16 = roll(M.L, 16, np.nanmin); HI8 = roll(M.H, 8, np.nanmax); HI4 = roll(M.H, 4, np.nanmax)
ALT1H = np.convolve(np.nan_to_num(M.ALT), np.ones(4), 'full')[:T]     # sum of last 4 15m alt returns
BTC1H = np.convolve(np.nan_to_num(M.BTC), np.ones(4), 'full')[:T]
band = 0.0035

def short_run(cond, slf, tp_r=1.5, hold=16, entry='open', t0=None, t1=None, per_bar=None, rank=None):
    trades = []; busy = {}
    a, b = (t0 or M.BOOK[0]), (t1 or M.BOOK[1])
    for t in range(max(a, 110), b):
        js = np.where(np.nan_to_num(cond(t)).astype(bool))[0]
        if per_bar and len(js) > per_bar: js = js[np.argsort(rank(t)[js])[:per_bar]]
        for j in js:
            if busy.get(j, -1) >= t or t + 1 >= T: continue
            e = M.O[t + 1, j] if entry == 'open' else M.C[t, j]
            sl = slf(t, j)
            if not (np.isfinite(e) and np.isfinite(sl)) or sl <= e * 1.002: continue
            if (sl - e) / e * 100 > 6: continue
            r = sl - e; tps = [e - tp_r * r, e - tp_r * r]
            pct, k, why = M.walk(-1, t, j, e, sl, tps, hold, 'tp1')
            trades.append(dict(t=t, j=j, net=pct - 0.07 - 0.10, risk_pct=r / e * 100, why=why, exit_t=k)); busy[j] = k
    return trades

def mvrtp_long(guard=None, t0=None, t1=None, hold=192):
    trades = []; busy = {}
    a, b = (t0 or M.BOOK[0]), (t1 or M.BOOK[1])
    for t in range(max(a, 110), b):
        s7, s25, s99, c, pl, pc = M.S7[t], M.S25[t], M.S99[t], M.C[t], M.L[t - 1], M.C[t - 1]
        sep = np.abs(s7 - s99) / s99 >= 0.03
        fast = (pl <= s7 * (1 + band)) & (c > s7) & (c > pc); deep = (pl <= s25 * (1 + band)) & (c > s25) & (c > pc)
        js = np.where(np.nan_to_num(M.LIQ[t] & sep & (s25 > s99) & (fast | deep)).astype(bool))[0]
        for j in js:
            if busy.get(j, -1) >= t: continue
            sl = (min(s25[j], pl[j]) if fast[j] else min(s99[j], pl[j])) - 0.5 * M.ATR[t, j]
            e = c[j]
            if not (np.isfinite(e) and np.isfinite(sl)) or sl >= e: continue
            blocked = guard is not None and not guard(t)
            r = e - sl; pct, k, why = M.walk(1, t, j, e, sl, [e + r, e + 1.6 * r], hold, 'ladder')
            trades.append(dict(t=t, j=j, net=pct - 0.07, risk_pct=r / e * 100, why=why, exit_t=k, blocked=blocked)); busy[j] = k
    return trades

def daily(tr):
    d = collections.defaultdict(float)
    for x in tr: d[int(M.ts[x['exit_t']] // 86400000)] += x['net']
    return d
