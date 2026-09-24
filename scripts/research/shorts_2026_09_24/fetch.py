"""Download everything the shorts research reads, from the public Binance
archive (data.binance.vision). The live REST API is not used, so this works
from networks where fapi.binance.com answers 451.

    SHORTS_DATA_DIR=~/shorts_research_data python fetch.py

Idempotent: a file already on disk is skipped. Missing archive files (a symbol
not yet listed, or delisted) are expected and silently skipped.
"""
import json
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from paths import DATA

ARCHIVE = "https://data.binance.vision/data/futures/um"
LISTING = ("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
           "?delimiter=/&prefix=data/futures/um/monthly/klines/")
MONTHS_1H = [f"2025-{m:02d}" for m in range(9, 13)] + [f"2026-{m:02d}" for m in range(1, 9)]
MONTHS_15Y = [f"2025-{m:02d}" for m in range(9, 13)] + [f"2026-{m:02d}" for m in range(1, 7)]
SEP_DAYS = [f"2026-09-{d:02d}" for d in range(1, 24)]


def _get(url, dst):
    if os.path.exists(dst):
        return
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            data = r.read()
    except Exception:
        return
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst + ".part", "wb") as f:
        f.write(data)
    os.replace(dst + ".part", dst)


def _pull(pairs, workers=48):
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(lambda p: _get(*p), pairs))


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


def main():
    syms = all_usdt_symbols()
    json.dump(syms, open(os.path.join(DATA, "all_usdt.json"), "w"))
    print(len(syms), "USDT symbols")
    _pull([(f"{ARCHIVE}/monthly/klines/{s}/1h/{s}-1h-{m}.zip", f"{DATA}/k1h/{s}-1h-{m}.zip")
           for s in syms for m in MONTHS_1H])
    # prepare.py step 1 decides which symbols are alive / liquid / crypto; the
    # remaining downloads depend on it.
    import prepare
    prepare.step1_k1h()
    alive = json.load(open(os.path.join(DATA, "alive_aug.json")))
    stats = json.load(open(os.path.join(DATA, "tradfi_stats.json")))
    _pull([(f"{ARCHIVE}/daily/klines/{s}/1h/{s}-1h-{d}.zip", f"{DATA}/k1h_sep/{s}-1h-{d}.zip")
           for s in alive for d in SEP_DAYS])
    liq_fund = [s for s in alive if s in stats and stats[s][2] >= 2e6 and stats[s][0] >= 0.35]
    _pull([(f"{ARCHIVE}/monthly/fundingRate/{s}/{s}-fundingRate-{m}.zip", f"{DATA}/fund/{s}-fundingRate-{m}.zip")
           for s in liq_fund for m in MONTHS_1H])
    book = set(json.load(open(os.path.join(DATA, "book_symbols.json"))))
    liq3 = {s for s, v in stats.items() if v[2] >= 3e6 and v[0] >= 0.35}
    s15 = sorted((liq3 | book) & set(alive))
    _pull([(f"{ARCHIVE}/monthly/klines/{s}/15m/{s}-15m-{m}.zip", f"{DATA}/k15/{s}-15m-{m}.zip")
           for s in s15 for m in ("2026-07", "2026-08")])
    _pull([(f"{ARCHIVE}/daily/klines/{s}/15m/{s}-15m-{d}.zip", f"{DATA}/k15/{s}-15m-{d}.zip")
           for s in s15 for d in SEP_DAYS])
    s15y = sorted(s for s, v in stats.items() if v[2] >= 10e6 and v[0] >= 0.35
                  and s not in ("SPYUSDT", "XAUTUSDT", "ONUSDT"))
    _pull([(f"{ARCHIVE}/monthly/klines/{s}/15m/{s}-15m-{m}.zip", f"{DATA}/k15y/{s}-15m-{m}.zip")
           for s in s15y for m in MONTHS_15Y])
    prepare.step2_rest()


if __name__ == "__main__":
    main()
