from paths import DATA
import glob, zipfile, numpy as np
from panel import build
def funding_panel():
    P = build(); ts = P["ts"]; syms = list(P["syms"]); T, N = P["C"].shape
    Fr = np.full((T, N), np.nan)
    for j, s in enumerate(syms):
        fs = sorted(glob.glob(f"{DATA}/fund/{s}-fundingRate-*.zip"))
        if not fs: continue
        ev = []
        for f in fs:
            try:
                raw = zipfile.ZipFile(f).read(zipfile.ZipFile(f).namelist()[0]).decode().strip().splitlines()
            except Exception: continue
            for line in raw:
                if line.startswith("calc_time"): continue
                a = line.split(",")
                t = float(a[0]); iv = float(a[1]) or 8.0; r = float(a[2])
                ev.append((t, r * 8.0 / iv))
        ev.sort()
        idx = np.array([int((t - ts[0]) // 3600000) for t, _ in ev]); val = np.array([v for _, v in ev])
        ok = (idx >= 0) & (idx < T)
        col = np.full(T, np.nan); col[idx[ok]] = val[ok]
        # forward-fill the latest settled rate
        last = np.nan
        for t in range(T):
            if not np.isnan(col[t]): last = col[t]
            col[t] = last
        Fr[:, j] = col
    return Fr
