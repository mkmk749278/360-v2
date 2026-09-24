import os
from paths import DATA
import numpy as np, datetime as dt
z = np.load(os.path.join(DATA, 'p15.npz'), allow_pickle=True)
ts, syms = z['ts'], list(z['syms']); O, H, L, C, QV = (z[k].astype(float) for k in ('O','H','L','C','QV'))
T, N = C.shape
def sma(x, n):
    cs = np.nancumsum(np.nan_to_num(x), axis=0); o = np.full_like(x, np.nan); o[n:] = (cs[n:] - cs[:-n]) / n
    cnt = np.cumsum(np.isfinite(x), axis=0); c2 = np.full_like(x, np.nan); c2[n:] = cnt[n:] - cnt[:-n]
    o[c2 < n] = np.nan; return o
S7, S25, S99 = sma(C, 7), sma(C, 25), sma(C, 99)
prevC = np.roll(C, 1, axis=0)
TR = np.nanmax(np.stack([H - L, np.abs(H - prevC), np.abs(L - prevC)]), axis=0)
def ema(x, n):
    a = 2 / (n + 1); out = np.full_like(x, np.nan); p = np.full(x.shape[1], np.nan)
    for t in range(x.shape[0]):
        v = x[t]; p = np.where(np.isnan(p), v, np.where(np.isnan(v), p, a * v + (1 - a) * p)); out[t] = p
    return out
ATR = ema(TR, 14)
cs = np.cumsum(np.nan_to_num(QV), axis=0); QV24 = np.full_like(QV, np.nan); QV24[96:] = cs[96:] - cs[:-96]
LIQ = QV24 >= 5e6
ib = syms.index('BTCUSDT')
r1 = np.clip(C / prevC - 1, -0.3, 0.3); r1[0] = np.nan
alt = np.where(QV24 >= 10e6, r1, np.nan); alt[:, ib] = np.nan
with np.errstate(all='ignore'):
    ALT = np.nanmean(alt, axis=1) * 100          # alt index 15m return, %
BTC = r1[:, ib] * 100
def tix(y, m, d): return int((dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000 - ts[0]) // 900000)
BOOK = (tix(2026, 7, 26), T - 2)

def walk(side, t, j, e, sl, tps, hold, fsm):
    """side +1 long / -1 short. tps list of prices. fsm: 'tp1' full exit at TP1;
    'ladder' = 50% at TP1 then stop to BE, rest to TP2 or BE. Returns (pct, exit_k, why)."""
    stop = sl; filled = 0.0; realized = 0.0; why = 'TIME'; k = t + 1
    for k in range(t + 1, min(T, t + 1 + hold)):
        h, l = H[k, j], L[k, j]
        if not np.isfinite(h): continue
        hit_sl = (l <= stop) if side > 0 else (h >= stop)
        if hit_sl:
            px = stop
            realized += (1 - filled) * side * (px - e) / e * 100
            return realized, k, ('SL' if filled == 0 else 'BE')
        tp = tps[0] if filled == 0 else tps[1]
        hit_tp = (h >= tp) if side > 0 else (l <= tp)
        if hit_tp:
            if fsm == 'tp1' or filled > 0:
                realized += (1 - filled) * side * (tp - e) / e * 100
                return realized, k, 'TP'
            realized += 0.5 * side * (tp - e) / e * 100; filled = 0.5; stop = e
    k = min(T - 1, t + hold); px = C[k, j]
    realized += (1 - filled) * side * (px - e) / e * 100
    return realized, k, why
