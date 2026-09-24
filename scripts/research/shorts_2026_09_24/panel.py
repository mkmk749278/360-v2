import os
from paths import DATA
"""Aligned hourly panel over every crypto USDT-M perp (TradFi excluded by the
weekend-volume test), 2025-09-01 .. 2026-09-23."""
import json, pickle, numpy as np, datetime as dt
from load import load_dir

TRADFI_EXTRA = {"SPYUSDT", "XAUTUSDT", "ONUSDT", "USDCUSDT", "FDUSDUSDT", "BUSDUSDT", "TUSDUSDT", "USDPUSDT"}

def build(cache=os.path.join(DATA, "panel.npz")):
    if os.path.exists(cache):
        z = np.load(cache, allow_pickle=True)
        return {k: z[k] for k in z.files}
    base = pickle.load(open(os.path.join(DATA, "k1h.pkl"), "rb"))
    sep = load_dir(os.path.join(DATA, "k1h_sep"), "1h")
    stats = json.load(open(os.path.join(DATA, "tradfi_stats.json")))
    tradfi = {s for s, v in stats.items() if v[0] < 0.35 and s not in ("BTCUSDT", "ETHUSDT")} | TRADFI_EXTRA
    syms = sorted(s for s in set(base) | set(sep) if s not in tradfi)
    t0 = int(dt.datetime(2025, 9, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)
    t1 = int(dt.datetime(2026, 9, 24, tzinfo=dt.timezone.utc).timestamp() * 1000)
    ts = np.arange(t0, t1, 3600_000)
    T, N = len(ts), len(syms)
    O = np.full((T, N), np.nan); H = O.copy(); L = O.copy(); C = O.copy(); QV = O.copy(); TBQ = O.copy()
    for j, s in enumerate(syms):
        parts = [p for p in (base.get(s), sep.get(s)) if p is not None]
        a = np.concatenate(parts)
        a = a[np.argsort(a[:, 0], kind="stable")]
        a = a[np.concatenate([[True], np.diff(a[:, 0]) > 0])]
        idx = ((a[:, 0] - t0) // 3600_000).astype(int)
        ok = (idx >= 0) & (idx < T)
        idx = idx[ok]; a = a[ok]
        O[idx, j] = a[:, 1]; H[idx, j] = a[:, 2]; L[idx, j] = a[:, 3]; C[idx, j] = a[:, 4]
        QV[idx, j] = a[:, 7]; TBQ[idx, j] = a[:, 10]
    out = dict(ts=ts, syms=np.array(syms), O=O, H=H, L=L, C=C, QV=QV, TBQ=TBQ)
    np.savez_compressed(cache, **out)
    return out

def rolling_sum(x, w):
    x0 = np.nan_to_num(x)
    cs = np.cumsum(x0, axis=0)
    out = cs.copy()
    out[w:] = cs[w:] - cs[:-w]
    out[:w] = np.nan
    return out
