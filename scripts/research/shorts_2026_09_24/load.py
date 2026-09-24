"""Load Binance USDT-M kline zips into numpy arrays, one dict per symbol."""
import glob, os, zipfile, numpy as np, pickle
COLS = ("open_time","open","high","low","close","volume","close_time","quote_volume","count","tbv","tbqv","ignore")

def read_zip(path):
    try:
        with zipfile.ZipFile(path) as z:
            name = z.namelist()[0]
            raw = z.read(name).decode()
    except Exception:
        return None
    lines = raw.strip().splitlines()
    if not lines:
        return None
    if lines[0].startswith("open_time"):
        lines = lines[1:]
    arr = np.array([l.split(",")[:11] for l in lines], dtype=float)
    return arr

def load_dir(d, tf):
    out = {}
    files = sorted(glob.glob(f"{d}/*-{tf}-*.zip"))
    by = {}
    for f in files:
        sym = os.path.basename(f).split(f"-{tf}-")[0]
        by.setdefault(sym, []).append(f)
    for sym, fs in by.items():
        parts = [a for a in (read_zip(f) for f in sorted(fs)) if a is not None and len(a)]
        if not parts:
            continue
        a = np.concatenate(parts)
        # ms timestamps; some archives use microseconds from 2025 on
        t = a[:, 0]
        t = np.where(t > 1e14, t / 1000.0, t)
        a[:, 0] = t
        order = np.argsort(a[:, 0], kind="stable")
        a = a[order]
        keep = np.concatenate([[True], np.diff(a[:, 0]) > 0])
        out[sym] = a[keep]
    return out

if __name__ == "__main__":
    import sys
    d, tf, dst = sys.argv[1], sys.argv[2], sys.argv[3]
    data = load_dir(d, tf)
    pickle.dump(data, open(dst, "wb"))
    print(len(data), "symbols")
