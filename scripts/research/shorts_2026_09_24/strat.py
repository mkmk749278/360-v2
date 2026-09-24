import os
from paths import DATA
import numpy as np, pickle, datetime as dt, collections
from panel import build
from sim import simulate, stats, fmt

P = build(); F = pickle.load(open(os.path.join(DATA, "feat.pkl"), "rb"))
ts = P["ts"]; C, H, L, O, QV = P["C"], P["H"], P["L"], P["O"], P["QV"]
T, N = C.shape
def tix(y, m, d): return int((dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000 - ts[0]) // 3600000)
IS = (tix(2025, 9, 8), tix(2026, 5, 1)); OOS = (tix(2026, 5, 1), T - 30)
BOOK = (tix(2026, 7, 26), tix(2026, 9, 24) - 1)

def gate_weak(t):
    return F["altidx"][t] < F["alt_e24"][t] and F["breadth"][t] < 0.45

def sl_hi6(buf=0.25, cap=8.0, floor=0.6):
    def f(t, j, e):
        s = F["hi6"][t, j] + buf * F["atr"][t, j]
        if not np.isfinite(s): return None
        r = (s - e) / e * 100
        if r > cap: return None
        if r < floor: s = e * (1 + floor / 100)
        return s
    return f

def gen(cond, t0, t1, per_bar=None, rank=None):
    out = []
    for t in range(max(t0, 80), t1):
        js = np.where(cond(t))[0]
        if per_bar and len(js) > per_bar:
            js = js[np.argsort(rank(t)[js])[:per_bar]]
        out += [(t, int(j)) for j in js]
    return out

liq = F["liq"]
def c_breakdown(gated):
    def c(t):
        m = liq[t] & (C[t] < F["lo24"][t]) & (QV[t] >= 2 * F["qv_avg24"][t]) & (F["r24"][t] > -0.15)
        if gated and not gate_weak(t): return np.zeros(N, bool)
        return np.nan_to_num(m).astype(bool)
    return c

def c_failed_mover(t):
    ran = F["hi48"][t] / C[max(0, t - 72)] - 1 >= 0.25
    m = liq[t] & ran & (C[t] <= 0.92 * F["hi48"][t]) & (C[t] < F["lo6"][t]) & (C[t] < F["e20"][t])
    return np.nan_to_num(m).astype(bool)

def c_relweak(t):
    if not gate_weak(t): return np.zeros(N, bool)
    r = F["r24"][t]
    ok = liq[t] & np.isfinite(r)
    if ok.sum() < 20: return np.zeros(N, bool)
    thr = np.nanpercentile(r[ok], 10)
    m = ok & (r <= thr) & (r >= -0.25) & (r <= -0.05) & (C[t] < F["lo6"][t]) & (C[t] < F["e20"][t])
    return np.nan_to_num(m).astype(bool)

def c_pumpfade(t):
    rng = H[t] - L[t]
    wick = H[t] - np.maximum(O[t], C[t])
    m = liq[t] & (F["r24"][t] >= 0.30) & (wick >= 0.5 * rng) & (C[t] < O[t]) & (C[t] < C[t - 1])
    return np.nan_to_num(m).astype(bool)

def sl_bar_high(buf=0.005, cap=8.0):
    def f(t, j, e):
        s = H[t, j] * (1 + buf); r = (s - e) / e * 100
        return None if r > cap or r <= 0.3 else s
    return f

# 1h approximation of MVRTP (SMA7/25/99 on 1h, pullback-to-SMA7 reclaim) — calibration only
S7 = None
def smas():
    global S7
    if S7 is None:
        cs = np.nancumsum(np.nan_to_num(C), axis=0)
        def sma(n):
            o = np.full_like(C, np.nan); o[n:] = (cs[n:] - cs[:-n]) / n; return o
        S7 = (sma(7), sma(25), sma(99))
    return S7
def c_tpb(side):
    def c(t):
        a, b, d = smas()
        sep = np.abs(a[t] - d[t]) / d[t] >= 0.03
        if side == "L":
            m = liq[t] & sep & (b[t] > d[t]) & (L[t - 1] <= a[t] * 1.0035) & (C[t] > a[t]) & (C[t] > C[t - 1])
        else:
            m = liq[t] & sep & (b[t] < d[t]) & (H[t - 1] >= a[t] * 0.9965) & (C[t] < a[t]) & (C[t] < C[t - 1])
        return np.nan_to_num(m).astype(bool)
    return c

def simulate_long(signals, tp_r=1.0, hold=24):
    # mirror by negating prices is awkward; implement directly
    trades = []; busy = {}
    a, b, d = smas()
    for t, j in signals:
        if t + 1 >= T or busy.get(j, -1) >= t: continue
        e = O[t + 1, j]
        sl = min(b[t, j], L[t - 1, j]) - 0.5 * F["atr"][t, j] / 4
        if not (np.isfinite(e) and np.isfinite(sl)) or sl >= e: continue
        risk = e - sl; tp = e + tp_r * risk; px = None
        for k in range(t + 1, min(T, t + 1 + hold)):
            if L[k, j] <= sl: px = sl; break
            if H[k, j] >= tp: px = tp; break
        if px is None:
            k = min(T - 1, t + hold); px = C[k, j]
        if not np.isfinite(px): continue
        net = (px - e) / e * 100 - 0.07 - 0.10
        trades.append(dict(t=t, j=j, net=net, risk_pct=risk / e * 100, why="", exit_t=k)); busy[j] = k
    return trades

def daily(trades):
    d = collections.defaultdict(float)
    for tr in trades: d[int(ts[tr["exit_t"]] // 86400000)] += tr["net"]
    return d

def report(name, cond, slf, tp_r=1.5, hold=24, per_bar=None, rank=None, be=None):
    res = {}
    for lab, (a, b) in (("IS", IS), ("OOS", OOS)):
        sig = gen(cond, a, b, per_bar, rank)
        tr = simulate(P, sig, slf, tp_r=tp_r, hold=hold, be_at_r=be)
        res[lab] = tr
        print(fmt(stats(tr, ts, f"{name} [{lab}]")))
    return res
