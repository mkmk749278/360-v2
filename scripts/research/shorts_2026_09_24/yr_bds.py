import numpy as np, sys
from sim import stats, fmt
from feat import ema
which = sys.argv[1] if __name__ == "__main__" and len(sys.argv) > 1 else "y"
M = __import__("m15y" if which == "y" else "m15")
T, N = M.C.shape; liq = M.LIQ
E9 = ema(M.C, 9); E21 = ema(M.C, 21)
def bds(a, b, tp_r=1.5, hold=16, max_bounce=1.5, sl_pct=0.8):
    tr = []; busy = {}
    for t in range(max(a, 200), b):
        lvl = np.nanmin(M.L[t - 17:t - 5], axis=0)            # prior support, ~75-255 min back
        brk = np.zeros(N, bool)
        for i in range(1, 5):                                   # breakdown bar in the last hour
            brk |= np.nan_to_num((M.L[t - i] < lvl) & (M.C[t - i] < lvl)).astype(bool)
        c = M.C[t]
        d = (c - lvl) / lvl * 100
        fresh = np.nanmin(M.L[t - 4:t + 1], axis=0) >= lvl * 0.96    # not already dumped >4% below
        m = liq[t] & brk & (d >= 0.1) & (d <= max_bounce) & (E9[t] < E21[t]) & fresh
        for j in np.where(np.nan_to_num(m).astype(bool))[0]:
            if busy.get(j, -1) >= t or t + 1 >= T: continue
            e = float(M.O[t + 1, j])
            sl = max(lvl[j] * (1 + sl_pct / 100), M.H[t, j]) + 0.1 * M.ATR[t, j]
            if not (np.isfinite(e) and np.isfinite(sl)) or sl <= e * 1.002 or (sl - e) / e * 100 > 5: continue
            r = sl - e; pct, k, why = M.walk(-1, t, j, e, sl, [e - tp_r * r, e - tp_r * r], hold, 'tp1')
            tr.append(dict(t=t, j=j, net=pct - 0.07 - 0.10, risk_pct=r / e * 100, why=why, exit_t=k)); busy[j] = k
    return tr
if __name__ == "__main__":
    if which == "y":
        for lab, (a, b) in (("IS", M.IS), ("OOS", M.OOS)):
            print(fmt(stats(bds(a, b), M.ts, f"BDS-replica 15m core [{lab}]")))
    else:
        print(fmt(stats(bds(*M.BOOK), M.ts, "BDS-replica 15m book-window movers")))
