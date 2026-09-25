"""Insider cliff-unlock calendar — DefiLlama's emissions dataset, reduced.

The unlock-short lane (``src/unlock_shorts.py``) needs one thing from the
outside world that Binance does not publish: **when team and investor tokens
unlock, and how many.** DefiLlama publishes every tracked token's vesting
schedule in one public file (``emissionsIndex``, no key, no quota); this module
fetches it and keeps only what the lane reads.

Why this runs in a child process
--------------------------------
Measured 2026-09-25: the file is **22.2 MB**, ``json.loads`` takes **1.12 s**
and peaks at **99 MB**. Inside the engine that parse holds the GIL for over a
second — a thread would move *where* it runs and not *whether* it blocks the
event loop (the `json.dumps`-in-a-thread lesson in CLAUDE.md). So the engine
runs ``python -m src.unlock_calendar`` as a fresh interpreter (:func:`main`):
the download, the parse and the 99 MB never enter the engine, which reads back
only the few hundred events that qualify. That is also why this module imports
nothing but the standard library — and why it is not a multiprocessing pool,
which would re-import the engine's whole ``__main__`` in the child.

What qualifies (the research rule, `docs/SHORTS_MARKET_RESEARCH_2026_09_25.md`)
-------------------------------------------------------------------------------
* a **cliff** allocation (a linear stream has no date to trade);
* to **insiders**: DefiLlama category ``insiders`` / ``privateSale``, or a
  recipient naming team, investors, advisors, contributors, backers, seed,
  series, private, strategic, founders or core;
* summed per token per UTC day, at least ``min_fraction`` of max supply.

Max supply falls back to circulating + locked when DefiLlama carries none —
the same definition the backtest used, so live rows and research rows measure
the same quantity.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import time
import urllib.request
from typing import Any, Dict, List, Optional

SOURCE_URL = "https://defillama-datasets.llama.fi/emissionsIndex"

INSIDER_CATEGORIES = frozenset({"insiders", "privateSale"})
INSIDER_RECIPIENT = re.compile(
    r"team|investor|advisor|contributor|backer|seed|series|private|strategic|founder|core",
    re.I,
)

#: Hard cap on the download. The file was 22.2 MB on 2026-09-25; a response ten
#: times that is not the dataset we know how to read, and reading it anyway
#: would spend memory in a container we share with nothing but ourselves.
MAX_BYTES = 250_000_000


def is_insider(alloc: Dict[str, Any]) -> bool:
    if str(alloc.get("category") or "") in INSIDER_CATEGORIES:
        return True
    return bool(INSIDER_RECIPIENT.search(str(alloc.get("recipient") or "")))


def _max_supply(token: Dict[str, Any]) -> Optional[float]:
    for value in (
        token.get("maxSupply"),
        (token.get("circSupply") or 0) + (token.get("totalLocked") or 0),
    ):
        try:
            v = float(value or 0)
        except (TypeError, ValueError):
            continue
        if v > 0:
            return v
    return None


def _token_symbol_and_price(token: Dict[str, Any]) -> tuple:
    prices = token.get("tokenPrice") or []
    if not prices or not isinstance(prices, list) or not isinstance(prices[0], dict):
        return "", None
    sym = str(prices[0].get("symbol") or "").upper().strip()
    try:
        price = float(prices[0].get("price")) if prices[0].get("price") is not None else None
    except (TypeError, ValueError):
        price = None
    return sym, price


def reduce_emissions(
    data: Any,
    *,
    now_ts: float,
    min_fraction: float,
    lookback_days: float,
    horizon_days: float,
) -> Dict[str, Any]:
    """Qualifying insider cliffs whose date lies in [now - lookback, now + horizon].

    Returns ``{"events": [...], "tokens_total", "tokens_with_symbol",
    "tokens_unreadable", "cliffs_seen"}``. Each event::

        {"token_name", "token_symbol", "gecko_id", "unlock_ts", "unlock_date",
         "fraction", "max_supply", "price_usd", "allocations": [...]}

    ``unlock_ts`` is the earliest cliff timestamp that day; ``unlock_date`` is
    its UTC date, which is what the lane keys and schedules on.
    """
    tokens = (data or {}).get("data") if isinstance(data, dict) else None
    if not isinstance(tokens, list):
        raise ValueError("emissionsIndex: no 'data' list")
    lo = now_ts - lookback_days * 86400.0
    hi = now_ts + horizon_days * 86400.0
    out: Dict[tuple, Dict[str, Any]] = {}
    unreadable = with_symbol = cliffs = 0
    for token in tokens:
        if not isinstance(token, dict):
            unreadable += 1
            continue
        sym, price = _token_symbol_and_price(token)
        if not sym:
            continue
        with_symbol += 1
        supply = _max_supply(token)
        if not supply:
            continue
        for ev in token.get("unlockEvents") or []:
            if not isinstance(ev, dict):
                continue
            try:
                ts = float(ev.get("timestamp"))
            except (TypeError, ValueError):
                continue
            if not (lo <= ts <= hi):
                continue
            for alloc in ev.get("cliffAllocations") or []:
                if not isinstance(alloc, dict):
                    continue
                cliffs += 1
                if not is_insider(alloc):
                    continue
                try:
                    amount = float(alloc.get("amount") or 0)
                except (TypeError, ValueError):
                    continue
                if amount <= 0:
                    continue
                day = _dt.datetime.fromtimestamp(ts, tz=_dt.timezone.utc).date().isoformat()
                key = (sym, str(token.get("gecko_id") or token.get("name") or ""), day)
                row = out.get(key)
                if row is None:
                    row = out[key] = {
                        "token_name": str(token.get("name") or ""),
                        "token_symbol": sym,
                        "gecko_id": str(token.get("gecko_id") or ""),
                        "unlock_ts": ts,
                        "unlock_date": day,
                        "fraction": 0.0,
                        "max_supply": supply,
                        "price_usd": price,
                        "allocations": [],
                    }
                row["unlock_ts"] = min(row["unlock_ts"], ts)
                row["fraction"] += amount / supply
                row["allocations"].append({
                    "recipient": str(alloc.get("recipient") or ""),
                    "category": str(alloc.get("category") or ""),
                    "amount": amount,
                })
    events = [e for e in out.values() if e["fraction"] >= min_fraction]
    events.sort(key=lambda e: (e["unlock_ts"], e["token_symbol"]))
    return {
        "events": events,
        "tokens_total": len(tokens),
        "tokens_with_symbol": with_symbol,
        "tokens_unreadable": unreadable,
        "cliffs_seen": cliffs,
    }


def fetch_and_reduce(
    url: str = SOURCE_URL,
    *,
    timeout: float = 60.0,
    min_fraction: float,
    lookback_days: float,
    horizon_days: float,
    now_ts: Optional[float] = None,
) -> Dict[str, Any]:
    """Download, parse and reduce. Never raises: a failure is returned with
    its cause, because the lane renders "calendar unreadable: <why>" and a
    blank error is the one caption this repo has paid for more than any other.
    """
    started = time.time()
    now_ts = started if now_ts is None else now_ts
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "360ce-engine/unlock-shorts"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            return {"ok": False, "error": f"payload over {MAX_BYTES} bytes; refused"}
        fetched = time.time()
        data = json.loads(raw)
        parsed = time.time()
        reduced = reduce_emissions(
            data, now_ts=now_ts, min_fraction=min_fraction,
            lookback_days=lookback_days, horizon_days=horizon_days,
        )
        return {
            "ok": True,
            "bytes": len(raw),
            "fetch_sec": round(fetched - started, 3),
            "parse_sec": round(parsed - fetched, 3),
            **reduced,
        }
    except Exception as exc:  # noqa: BLE001 — returned, never swallowed
        # `str(TimeoutError())` is "" — name the type so the cause is never blank.
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}".rstrip(": ")}


def main(argv: Optional[List[str]] = None) -> int:
    """``python -m src.unlock_calendar --min-fraction … --now …`` → JSON on stdout.

    The engine runs this as a fresh interpreter rather than through a
    multiprocessing pool: a spawned pool re-imports the parent's ``__main__``
    (all of ``src.main``) in the child, which is the opposite of the point.
    A plain ``-m`` run imports this module and the standard library, nothing
    else. It always prints one JSON object and exits 0 — a failure is data.
    """
    import argparse
    import sys

    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=SOURCE_URL)
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--min-fraction", type=float, required=True)
    ap.add_argument("--lookback-days", type=float, required=True)
    ap.add_argument("--horizon-days", type=float, required=True)
    ap.add_argument("--now", type=float, default=None)
    args = ap.parse_args(argv)
    result = fetch_and_reduce(
        args.url, timeout=args.timeout, min_fraction=args.min_fraction,
        lookback_days=args.lookback_days, horizon_days=args.horizon_days, now_ts=args.now,
    )
    result["source_url"] = args.url
    sys.stdout.write(json.dumps(result))
    sys.stdout.flush()
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess
    raise SystemExit(main())
