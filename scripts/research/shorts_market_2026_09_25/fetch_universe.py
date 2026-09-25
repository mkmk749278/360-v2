"""Step 1: list every USDT-M perp in the public archive and pull its daily
klines, so the liquid-crypto universe is chosen from the market, not from any
engine artifact.

    SHORTS_MKT_DIR=~/shorts_data python fetch_universe.py
"""
import json, os, re, urllib.request
from concurrent.futures import ThreadPoolExecutor

DATA = os.environ.get("SHORTS_MKT_DIR", os.path.expanduser("~/shorts_data"))
ARCHIVE = "https://data.binance.vision/data/futures/um"
LISTING = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
           "?delimiter=/&prefix=data/futures/um/monthly/klines/")
MONTHS = [f"2025-{m:02d}" for m in range(9, 13)] + [f"2026-{m:02d}" for m in range(1, 9)]


def get(url, dst):
    if os.path.exists(dst):
        return True
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            data = r.read()
    except Exception:
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst + ".part", "wb") as f:
        f.write(data)
    os.replace(dst + ".part", dst)
    return True


def pull(pairs, workers=48):
    with ThreadPoolExecutor(workers) as ex:
        return list(ex.map(lambda p: get(*p), pairs))


def all_usdt_symbols():
    syms, marker = [], ""
    while True:
        x = urllib.request.urlopen(LISTING + (f"&marker={marker}" if marker else ""), timeout=60).read().decode()
        syms += re.findall(r"<Prefix>data/futures/um/monthly/klines/([^/<]+)/</Prefix>", x)
        m = re.search(r"<NextMarker>([^<]+)</NextMarker>", x)
        if not m or "<IsTruncated>true" not in x:
            break
        marker = m.group(1)
    return [s for s in syms if s.endswith("USDT")]


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    syms = all_usdt_symbols()
    json.dump(syms, open(f"{DATA}/all_usdt.json", "w"))
    print(len(syms), "USDT perps")
    pull([(f"{ARCHIVE}/monthly/klines/{s}/1d/{s}-1d-{m}.zip", f"{DATA}/k1d/{s}-1d-{m}.zip")
          for s in syms for m in MONTHS])
    days = [f"2026-09-{d:02d}" for d in range(1, 25)]
    pull([(f"{ARCHIVE}/daily/klines/{s}/1d/{s}-1d-{d}.zip", f"{DATA}/k1d/{s}-1d-{d}.zip")
          for s in syms for d in days])
    print("done")
