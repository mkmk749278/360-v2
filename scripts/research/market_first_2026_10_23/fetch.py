#!/usr/bin/env python3
"""Fetch ~400 days of 1h candles for BTC + 29 large alts from Gate.io USDT perps.

Gate.io, not Binance, because Binance answers 451 from cloud containers. The
series are close enough for regime and beta research; the Phase-1 replay in
docs/MARKET_FIRST_METHODOLOGY_2026_10_23.md is meant to run on Binance klines
from the VPS.

    python scripts/research/market_first_2026_10_23/fetch.py --out /tmp/mf

Writes one JSON file per coin (Gate's raw candle rows) into --out.
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.request

COINS = [
    "BTC", "ETH", "SOL", "XRP", "BNB", "DOGE", "ADA", "LINK", "AVAX", "SUI",
    "LTC", "DOT", "NEAR", "APT", "ARB", "OP", "INJ", "TIA", "SEI", "WIF",
    "PEPE", "FET", "RENDER", "AAVE", "UNI", "HYPE", "ENA", "TAO", "ONDO", "JUP",
]
URL = ("https://api.gateio.ws/api/v4/futures/usdt/candlesticks"
       "?contract={c}_USDT&interval=1h&from={fr}&to={to}")
STEP = 1999 * 3600  # Gate caps a request at 2,000 points


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--days", type=int, default=400)
    ap.add_argument("--end", type=int, default=int(time.time()) // 3600 * 3600)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    start = a.end - a.days * 86400
    for coin in COINS:
        rows, fr = [], start
        while fr < a.end:
            to = min(fr + STEP, a.end)
            with urllib.request.urlopen(URL.format(c=coin, fr=fr, to=to), timeout=30) as r:
                rows += json.load(r)
            fr = to + 3600
            time.sleep(0.15)
        with open(os.path.join(a.out, f"{coin}.json"), "w") as f:
            json.dump(rows, f)
        print(coin, len(rows))


if __name__ == "__main__":
    main()
