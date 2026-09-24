"""Short-only event simulator on the hourly panel.

Entry at the NEXT bar's open after the signal bar closes. Each later bar: the
stop is checked before the target (if one bar touches both, it is booked a
stop — the conservative reading). A time stop exits at that bar's close.
One open position per symbol. Costs: FEE_RT round trip plus SLIP per side.
"""
import numpy as np

FEE_RT = 0.07      # % round trip (maker in 0.02 + taker out 0.05)
SLIP = 0.05        # % per fill, adverse (movers are thin)

def simulate(P, signals, sl_fn, tp_r=1.5, hold=24, be_at_r=None):
    """signals: iterable of (t_idx, j) in time order. sl_fn(t, j, entry) -> stop price
    (above entry for a short). Returns list of trade dicts."""
    O, H, L, C = P["O"], P["H"], P["L"], P["C"]
    T = O.shape[0]
    busy_until = {}
    trades = []
    for t, j in signals:
        if t + 1 >= T or busy_until.get(j, -1) >= t:
            continue
        e = O[t + 1, j]
        if not np.isfinite(e) or e <= 0:
            continue
        sl = sl_fn(t, j, e)
        if sl is None or not np.isfinite(sl) or sl <= e:
            continue
        risk = sl - e
        tp = e - tp_r * risk if tp_r else -np.inf
        stop = sl
        exit_px, why, k = None, None, t + 1
        for k in range(t + 1, min(T, t + 1 + hold)):
            h, l, c = H[k, j], L[k, j], C[k, j]
            if not np.isfinite(h):
                continue
            if h >= stop:
                exit_px, why = max(stop, O[k, j]) if k > t + 1 else stop, "SL" if stop == sl else "BE"
                break
            if l <= tp:
                exit_px, why = tp, "TP"
                break
            if be_at_r is not None and l <= e - be_at_r * risk:
                stop = min(stop, e)
        if exit_px is None:
            k = min(T - 1, t + hold)
            c = C[k, j]
            if not np.isfinite(c):
                continue
            exit_px, why = c, "TIME"
        gross = (e - exit_px) / e * 100.0
        net = gross - FEE_RT - 2 * SLIP
        trades.append(dict(t=t, j=j, entry=e, exit=exit_px, why=why, gross=gross, net=net,
                           risk_pct=risk / e * 100.0, exit_t=k))
        busy_until[j] = k
    return trades

def stats(trades, ts=None, label=""):
    if not trades:
        return dict(label=label, n=0)
    x = np.array([tr["net"] for tr in trades])
    wins = x[x > 0].sum(); losses = -x[x < 0].sum()
    out = dict(label=label, n=len(x), mean=x.mean(), win=(x > 0).mean() * 100,
               pf=(wins / losses) if losses > 0 else np.inf, total=x.sum(),
               med_risk=np.median([tr["risk_pct"] for tr in trades]))
    if ts is not None:
        days = np.array([ts[tr["t"]] // 86_400_000 for tr in trades])
        ud = np.unique(days)
        # day-clustered bootstrap of the mean
        rng = np.random.default_rng(7)
        groups = [x[days == d] for d in ud]
        bs = []
        for _ in range(2000):
            pick = rng.integers(0, len(groups), len(groups))
            s = np.concatenate([groups[i] for i in pick])
            bs.append(s.mean())
        out["ci"] = (np.percentile(bs, 2.5), np.percentile(bs, 97.5))
        out["days"] = len(ud)
    return out

def fmt(s):
    if not s.get("n"):
        return f"{s['label']:44s} n=0"
    ci = s.get("ci")
    cis = f"[{ci[0]:+.3f},{ci[1]:+.3f}]" if ci else ""
    return (f"{s['label']:44s} n={s['n']:5d} mean={s['mean']:+.3f}% {cis:18s} win={s['win']:4.1f}% "
            f"PF={s['pf']:.2f} total={s['total']:+8.1f}% risk~{s['med_risk']:.2f}%")
