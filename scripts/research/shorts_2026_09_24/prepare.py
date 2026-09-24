"""Derived inputs for the shorts research, built from what fetch.py downloaded.

Step 1 (needs only the 1h monthly klines, plus rows.json — the delivered-book
export — copied into SHORTS_DATA_DIR):
  k1h.pkl, alive_aug.json, tradfi_stats.json, book_symbols.json
Step 2 (needs everything):
  panel.npz, feat.pkl, funding8h.npy, p15.npz, p15y.npz, tbq15y.npy

TradFi perps are detected structurally, because the live exchangeInfo
(`contractType`) is not reachable from every network: weekend volume below
0.35x weekday volume. Every crypto major reads >= 0.40 (BTC 0.40, SOL 0.70);
equities, ETFs and metals read 0.06-0.30.
"""
import datetime as dt
import json
import os
import pickle

import numpy as np

from load import load_dir
from paths import DATA

EXCLUDE_EXTRA = ("SPYUSDT", "XAUTUSDT", "ONUSDT")


def _ms(y, m, d):
    return int(dt.datetime(y, m, d, tzinfo=dt.timezone.utc).timestamp() * 1000)


def step1_k1h():
    d = load_dir(os.path.join(DATA, "k1h"), "1h")
    pickle.dump(d, open(os.path.join(DATA, "k1h.pkl"), "wb"))
    alive = sorted(s for s, a in d.items() if a[-1, 0] >= _ms(2026, 8, 31))
    json.dump(alive, open(os.path.join(DATA, "alive_aug.json"), "w"))
    t0 = _ms(2026, 7, 1)
    res = {}
    for s, a in d.items():
        m = a[:, 0] >= t0
        if m.sum() < 24 * 30:
            continue
        t = a[m, 0] / 1000
        qv = a[m, 7]
        wd = np.array([dt.datetime.utcfromtimestamp(x).weekday() for x in t])
        hr = (t // 3600) % 24
        wk, wkd = qv[wd >= 5].mean(), qv[wd < 5].mean()
        us = qv[(wd < 5) & (hr >= 14) & (hr < 21)].mean()
        off = qv[(wd < 5) & ((hr < 12) | (hr >= 22))].mean()
        res[s] = [wk / max(wkd, 1), us / max(off, 1), float(np.median(qv) * 24)]
    json.dump(res, open(os.path.join(DATA, "tradfi_stats.json"), "w"))
    rows = json.load(open(os.path.join(DATA, "rows.json")))
    json.dump(sorted({r["symbol"] for r in rows}), open(os.path.join(DATA, "book_symbols.json"), "w"))


def _panel15(dirs, t0, t1, syms, tbq=False):
    loaded = [load_dir(os.path.join(DATA, x), "15m") for x in dirs]
    ts = np.arange(t0, t1, 900_000)
    T = len(ts)
    cols = (("O", 1), ("H", 2), ("L", 3), ("C", 4), ("QV", 7)) + ((("TBQ", 10),) if tbq else ())
    M = {k: np.full((T, len(syms)), np.nan, dtype=np.float32) for k, _ in cols}
    for j, s in enumerate(syms):
        parts = [p[s] for p in loaded if s in p]
        x = np.concatenate(parts)
        x = x[np.argsort(x[:, 0], kind="stable")]
        x = x[np.concatenate([[True], np.diff(x[:, 0]) > 0])]
        idx = ((x[:, 0] - t0) // 900_000).astype(int)
        ok = (idx >= 0) & (idx < T)
        for k, c in cols:
            M[k][idx[ok], j] = x[ok, c]
    return ts, M


def step2_rest():
    from panel import build
    build()
    import feat
    F = feat.features()
    F.pop("P")
    pickle.dump(F, open(os.path.join(DATA, "feat.pkl"), "wb"))
    from fundpanel import funding_panel
    np.save(os.path.join(DATA, "funding8h.npy"), funding_panel())

    stats = json.load(open(os.path.join(DATA, "tradfi_stats.json")))
    tradfi = {s for s, v in stats.items() if v[0] < 0.35 and s not in ("BTCUSDT", "ETHUSDT")}
    tradfi |= set(EXCLUDE_EXTRA)
    k15 = load_dir(os.path.join(DATA, "k15"), "15m")
    syms = sorted(s for s in k15 if s not in tradfi)
    ts, M = _panel15(["k15"], _ms(2026, 7, 1), _ms(2026, 9, 24), syms)
    np.savez_compressed(os.path.join(DATA, "p15.npz"), ts=ts, syms=np.array(syms), **M)

    k15y = load_dir(os.path.join(DATA, "k15y"), "15m")
    syms = sorted(s for s in k15y if s in stats and stats[s][0] >= 0.35 and s not in EXCLUDE_EXTRA)
    ts, M = _panel15(["k15y", "k15"], _ms(2025, 9, 1), _ms(2026, 9, 24), syms, tbq=True)
    tbq = M.pop("TBQ")
    np.savez_compressed(os.path.join(DATA, "p15y.npz"), ts=ts, syms=np.array(syms), **M)
    np.save(os.path.join(DATA, "tbq15y.npy"), tbq)


if __name__ == "__main__":
    step1_k1h()
    step2_rest()
