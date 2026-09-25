"""Download everything this research reads, from the public Binance archive
(data.binance.vision). No engine artifact is read.

    SHORTS_MKT_DIR=~/shorts_data python fetch.py

Idempotent: files already on disk are skipped; archive 404s (a symbol not yet
listed or already delisted) are expected and skipped.

Stage A  daily klines, every USDT perp          -> universe, listings, unlock tokens
Stage B  liquid crypto perps only:
         1h + 5m futures klines, 1h premium index, 1h spot klines,
         5-minute metrics (OI, long/short ratios, taker ratio)
Stage C  funding history, every USDT perp
"""
import json
import os
import re
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor

import requests

DATA = os.environ.get("SHORTS_MKT_DIR", os.path.expanduser("~/shorts_data"))
FUT = "https://data.binance.vision/data/futures/um"
SPOT = "https://data.binance.vision/data/spot"
LISTING = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
           "?delimiter=/&prefix=data/futures/um/monthly/klines/")
MONTHS = [f"2025-{m:02d}" for m in range(9, 13)] + [f"2026-{m:02d}" for m in range(1, 9)]
# Listings need a tail before the window so a symbol listed in Aug 2025 is not
# read as new in Sep 2025.
PRE_MONTHS = [f"2025-{m:02d}" for m in range(3, 9)]
# Intraday series need ~30 days before the window for trailing percentiles.
B_MONTHS = ["2025-08"] + MONTHS

_tl = threading.local()


def _session():
    if not hasattr(_tl, "s"):
        _tl.s = requests.Session()
    return _tl.s


def get(url, dst):
    if os.path.exists(dst) or os.path.exists(dst + ".404"):
        return
    try:
        r = _session().get(url, timeout=90)
    except Exception:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if r.status_code == 404:
        open(dst + ".404", "w").close()
        return
    if r.status_code != 200:
        return
    with open(dst + ".part", "wb") as f:
        f.write(r.content)
    os.replace(dst + ".part", dst)


def pull(pairs, workers=48, label=""):
    pairs = list(pairs)
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda p: get(*p), pairs))
    print(f"{label}: {len(pairs)} requested", flush=True)


def all_usdt_symbols():
    syms, marker = [], ""
    while True:
        x = requests.get(LISTING + (f"&marker={marker}" if marker else ""), timeout=60).text
        syms += re.findall(r"<Prefix>data/futures/um/monthly/klines/([^/<]+)/</Prefix>", x)
        m = re.search(r"<NextMarker>([^<]+)</NextMarker>", x)
        if not m or "<IsTruncated>true" not in x:
            break
        marker = m.group(1)
    return [s for s in syms if s.endswith("USDT")]


def read_zip_csv(path, header_first="open_time"):
    """Rows of the single CSV in an archive zip, header row dropped if present."""
    with zipfile.ZipFile(path) as z:
        raw = z.read(z.namelist()[0]).decode()
    rows = [r.split(",") for r in raw.strip().splitlines()]
    if rows and not rows[0][0].strip().lstrip("-").isdigit():
        rows = rows[1:]
    return rows


def liquid_crypto_universe(syms, min_quote=10e6, weekend_ratio=0.35):
    """Symbols that were ever liquid (trailing-7d mean quote volume >= min_quote)
    inside the window, and that trade like crypto rather than a TradFi perp
    (weekend volume / weekday volume >= weekend_ratio). The point-in-time
    liquidity filter is re-applied at every decision; this only bounds the
    download."""
    import datetime as dt
    out, stats = [], {}
    for s in syms:
        rows = []
        for m in MONTHS:
            p = f"{DATA}/k1d/{s}-1d-{m}.zip"
            if os.path.exists(p):
                rows += read_zip_csv(p)
        if len(rows) < 14:
            continue
        qv = [float(r[7]) for r in rows]
        dow = [dt.datetime.utcfromtimestamp(int(r[0]) / 1000).weekday() for r in rows]
        we = [q for q, d in zip(qv, dow) if d >= 5]
        wd = [q for q, d in zip(qv, dow) if d < 5]
        ratio = (sum(we) / len(we)) / (sum(wd) / len(wd)) if we and wd and sum(wd) > 0 else 0
        best7 = max(sum(qv[i:i + 7]) / 7 for i in range(len(qv) - 6))
        stats[s] = (ratio, best7, len(rows))
        if best7 >= min_quote and ratio >= weekend_ratio:
            out.append(s)
    return out, stats


def spot_symbol(perp):
    for pre in ("1000000", "1000", "1M"):
        if perp.startswith(pre) and not perp.startswith("1000SATS"):
            return perp[len(pre):]
    return perp


def main():
    os.makedirs(DATA, exist_ok=True)
    syms = all_usdt_symbols()
    json.dump(syms, open(f"{DATA}/all_usdt.json", "w"))
    print(len(syms), "USDT perps", flush=True)

    pull([(f"{FUT}/monthly/klines/{s}/1d/{s}-1d-{m}.zip", f"{DATA}/k1d/{s}-1d-{m}.zip")
          for s in syms for m in PRE_MONTHS + MONTHS], label="A 1d klines")

    liq, stats = liquid_crypto_universe(syms)
    json.dump(liq, open(f"{DATA}/liquid.json", "w"))
    json.dump(stats, open(f"{DATA}/universe_stats.json", "w"))
    print(len(liq), "liquid crypto perps", flush=True)

    pull([(f"{FUT}/monthly/klines/{s}/1h/{s}-1h-{m}.zip", f"{DATA}/k1h/{s}-1h-{m}.zip")
          for s in liq for m in B_MONTHS], label="B 1h klines")
    pull([(f"{FUT}/monthly/premiumIndexKlines/{s}/1h/{s}-1h-{m}.zip", f"{DATA}/prem1h/{s}-1h-{m}.zip")
          for s in liq for m in B_MONTHS], label="B premium")
    pull([(f"{SPOT}/monthly/klines/{spot_symbol(s)}/1h/{spot_symbol(s)}-1h-{m}.zip",
           f"{DATA}/spot1h/{s}-1h-{m}.zip") for s in liq for m in B_MONTHS], label="B spot 1h")
    pull([(f"{FUT}/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip", f"{DATA}/fund/{s}-fundingRate-{m}.zip")
          for s in syms for m in PRE_MONTHS + MONTHS], label="C funding")
    pull([(f"{FUT}/monthly/klines/{s}/5m/{s}-5m-{m}.zip", f"{DATA}/k5m/{s}-5m-{m}.zip")
          for s in liq for m in MONTHS], label="B 5m klines")
    import datetime as dt
    d0 = dt.date(2025, 8, 1)
    days = [(d0 + dt.timedelta(days=i)).isoformat() for i in range((dt.date(2026, 8, 31) - d0).days + 1)]
    pull([(f"{FUT}/daily/metrics/{s}/{s}-metrics-{d}.zip", f"{DATA}/metrics/{s}/{s}-metrics-{d}.zip")
          for s in liq for d in days], workers=64, label="B metrics")
    print("done", flush=True)


if __name__ == "__main__":
    main()
