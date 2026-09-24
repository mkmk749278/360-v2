import os
from paths import DATA
import numpy as np, collections
import strat as S
from sim import stats, fmt
Fr = np.load(os.path.join(DATA, 'funding8h.npy')) * 100   # % per 8h
C, O, H, L = S.C, S.O, S.H, S.L; T, N = C.shape
F = S.F; liq = F['liq']; ts = S.ts

def run(thr=-0.05, need_down=True, below_ema=True, hold=72, stop_atr=3.0, stop_cap=12.0,
        tp_pct=None, t0=None, t1=None, fee=0.07, slip=0.05, every=1):
    """Short when funding <= thr. Entry next open. Stop = entry + stop_atr*ATR(1h), capped.
    Exit: stop, optional fixed % target, or time. Funding carry charged hourly (Fr/8)."""
    t0 = t0 or 200; t1 = t1 or T - 2
    busy = {}; trades = []
    for t in range(t0, t1, every):
        m = liq[t] & (Fr[t] <= thr)
        if need_down: m &= F['r24'][t] < 0
        if below_ema: m &= C[t] < F['e20'][t]
        for j in np.where(np.nan_to_num(m).astype(bool))[0]:
            if busy.get(j, -1) >= t or t + 1 >= T: continue
            e = O[t + 1, j]; a = F['atr'][t, j]
            if not (np.isfinite(e) and np.isfinite(a)) or e <= 0: continue
            sl = e + stop_atr * a
            if (sl - e) / e * 100 > stop_cap: sl = e * (1 + stop_cap / 100)
            tp = e * (1 - tp_pct / 100) if tp_pct else -np.inf
            px = None; carry = 0.0; k = t + 1
            for k in range(t + 1, min(T, t + 1 + hold)):
                if not np.isfinite(H[k, j]): continue
                carry += (Fr[k, j] / 8.0) if np.isfinite(Fr[k, j]) else 0.0   # + = short receives
                if H[k, j] >= sl: px = max(sl, O[k, j]) if k > t + 1 else sl; why = 'SL'; break
                if L[k, j] <= tp: px = tp; why = 'TP'; break
            if px is None:
                k = min(T - 1, t + hold); px = C[k, j]; why = 'TIME'
            if not np.isfinite(px): continue
            gross = (e - px) / e * 100
            net = gross + carry - fee - 2 * slip
            trades.append(dict(t=t, j=j, net=net, gross=gross, carry=carry, why=why, exit_t=k,
                               risk_pct=(sl - e) / e * 100, sym=S.F['syms'][j]))
            busy[j] = k
    return trades

def summary(tr, label):
    s = stats(tr, ts, label)
    if tr:
        c = np.mean([x['carry'] for x in tr]); g = np.mean([x['gross'] for x in tr])
        w = collections.Counter(x['why'] for x in tr)
        sym = collections.Counter(x['sym'] for x in tr)
        top = sym.most_common(1)[0]
        return fmt(s) + f" | gross {g:+.2f} carry {c:+.2f} | {dict(w)} | syms={len(sym)} top={top[0]}:{top[1]}"
    return fmt(s)
