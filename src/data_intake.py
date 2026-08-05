"""What we are actually reading from Binance — assembled from live engine state.

Answers, without an SSH session, the question that took a source-tree audit to
answer on 2026-08-05: *which streams are we subscribed to, how current is each
series, where does each derived input actually come from, and which detectors
are hollow?*

Why this exists as a page and not a docstring
---------------------------------------------
Every finding in ``docs/PRICE_ACTION_PROGRAM.md`` §3 had the same shape: a
mechanism that looks wired, has telemetry, has consumers, and is fed by
something that is not what the consumers assume. Those are invisible in logs and
invisible in code review, because nothing about them *fails*:

* ``data_store.ticks`` is a one-shot ``/fapi/v1/trades`` snapshot taken at seed
  time. Five call sites read it as live. Nothing errors — the numbers are simply
  old.
* ``orderblocks`` has never had a writer, so every
  ``bool(fvgs) or bool(orderblocks)`` gate is ``bool(fvgs)`` alone.
* ``detect_fvg`` sees twelve bars, which is what makes a deliberately loose gate
  behave like a strict one.
* The order book is one bid and one ask, stamped ``top_of_book_only``.

**A hollow input behind a passing gate is indistinguishable from a working
one.** So each of those is a named row here, rendered whether or not it is
currently a problem — a check that appears only when it trips teaches the reader
that its absence means "fine", when it equally means the check stopped running.

Provenance beats freshness
--------------------------
Where a value could be read from more than one place, this module reports **the
place it actually came from**, not just how old it is. ``cvd_source`` says
``kline_taker_buy`` rather than implying tick data; ``order_book_quality`` says
``top_of_book_only`` rather than showing a depth count of 1 and letting the
reader assume a thin book. Age answers "is this current"; provenance answers
"is this the thing I think it is", and the 2026-08-05 audit turned entirely on
the second question.

Cost
----
Assembled from state the engine already holds. **No new vendor calls, no new
polling, no I/O.** It is built on the snapshot writer's existing cycle and
published to Redis like the positions X-ray, because in isolated mode the API
container's facade cannot see any of this.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from src.utils import get_logger

log = get_logger("data_intake")

#: Schema version of the payload. Bumped when a field's *meaning* changes, so
#: ops can refuse to render a shape it does not understand rather than showing
#: a plausible wrong number.
SCHEMA = 1

#: A series older than this is called out. Not a fault by itself — a 4h bar is
#: legitimately hours old — so the threshold is applied per timeframe below.
_STALE_MULTIPLIER = 3.0

_INTERVAL_SECONDS: Dict[str, int] = {
    "1m": 60, "3m": 180, "5m": 300, "15m": 900, "30m": 1_800,
    "1h": 3_600, "2h": 7_200, "4h": 14_400, "6h": 21_600,
    "12h": 43_200, "1d": 86_400, "3d": 259_200, "1w": 604_800,
}


def _age(ts: Optional[float], *, monotonic: bool = False) -> Optional[float]:
    """Seconds since *ts*, or None when it was never set.

    ``None`` and ``0.0`` are different states: never-set and set-at-epoch. A
    caller that renders both as "0s ago" reports a healthy clock on a field
    nothing has ever written.
    """
    if ts is None or ts == 0:
        return None
    now = time.monotonic() if monotonic else time.time()
    return max(0.0, now - ts)


# ───────────────────────────────────────────────────────────────────────────
# WebSocket pools
# ───────────────────────────────────────────────────────────────────────────

def _pool_report(label: str, mgr: Any) -> Dict[str, Any]:
    """One WebSocket manager's connections, per-connection.

    Reported per connection rather than aggregated: Binance drops *subsets* of
    subscriptions silently, so one degraded connection inside a healthy pool is
    exactly the state an aggregate hides.
    """
    out: Dict[str, Any] = {
        "label": label,
        "present": mgr is not None,
        "connections": [],
        "streams_total": 0,
        "degraded_count": 0,
    }
    if mgr is None:
        # Named absence. A pool that was never started and a pool whose
        # connections all died look identical in a stream count of zero.
        out["state"] = "not_started"
        return out

    conns = list(getattr(mgr, "_connections", []) or [])
    now = time.monotonic()
    # Default 120s; scaled by the pool's own multiplier where the engine has
    # declared one. Surfaced on the row so a reader can see WHY a pool with
    # hours of silence is not being flagged.
    mult = float(getattr(mgr, "_staleness_multiplier", 1.0) or 1.0)
    silence_budget_s = 120.0 * max(1.0, mult)
    out["silence_budget_s"] = round(silence_budget_s, 1)
    out["silence_is_expected"] = mult > 1.0
    for idx, conn in enumerate(conns):
        streams = list(getattr(conn, "streams", []) or [])
        stream_ts = dict(getattr(conn, "stream_data_ts", {}) or {})
        # Streams that have delivered nothing recently — the "Binance silently
        # dropped a subset" detector.
        #
        # The budget is per POOL, read from the manager's own staleness
        # multiplier. A @forceOrder stream fires only during liquidations and is
        # legitimately silent for hours; the engine already sets
        # ``staleness_multiplier=100`` on that pool for exactly this reason, and
        # a flat 120s budget flagged 64 of 75 of them as silent on the first
        # live read. That is this page reporting a fault that is not happening —
        # against its own rule. The engine's number is reused rather than a
        # second threshold being invented here.
        silent = [
            s for s in streams
            if (now - stream_ts.get(s, 0.0)) > silence_budget_s or s not in stream_ts
        ]
        connected_ts = float(getattr(conn, "connected_ts", 0.0) or 0.0)
        out["connections"].append({
            "index": idx,
            "streams": len(streams),
            "silent_streams": len(silent),
            # Named, capped — the whole list on a 200-stream connection is
            # noise, and zero of it is a fault you cannot act on.
            "silent_sample": sorted(silent)[:10],
            "degraded": bool(getattr(conn, "degraded", False)),
            "reconnect_attempts": int(getattr(conn, "reconnect_attempts", 0) or 0),
            "ping_latency_ms": float(getattr(conn, "ping_latency_ms", 0.0) or 0.0),
            "last_reconnect_ms": float(getattr(conn, "last_reconnect_ms", 0.0) or 0.0),
            "connected_age_s": _age(connected_ts, monotonic=True),
            # Binance force-closes every connection at 24h. Showing the time
            # remaining turns a scheduled event into an expected one instead of
            # an alarm at 03:00.
            "seconds_to_forced_cycle": (
                max(0.0, 86_400.0 - (now - connected_ts))
                if connected_ts else None
            ),
            "msgs_since_health_check": int(
                getattr(conn, "health_msg_count", 0) or 0
            ),
        })
        out["streams_total"] += len(streams)
        if getattr(conn, "degraded", False):
            out["degraded_count"] += 1

    if not conns:
        out["state"] = "no_connections"
    elif out["degraded_count"] == len(conns):
        out["state"] = "all_degraded"
    elif out["degraded_count"]:
        out["state"] = "partially_degraded"
    else:
        out["state"] = "healthy"
    return out


def _discover_pools(engine: Any) -> List[tuple]:
    """Every WebSocket pool on the engine, found by SHAPE not by name.

    The first cut hard-coded ``("_ws_futures", "_ws_futures_liq",
    "_ws_futures_mover", "_ws")`` — and Phase 2a added ``_ws_futures_aggtrade``
    the very next change. The page then reported "Aggregate trades: NOT
    SUBSCRIBED" on a running feed, because the reporter could not see the pool
    at all. That is this repo's "a deny-list is a floor" rule, committed by the
    surface built to catch exactly this class of defect: a hand-written list
    excludes precisely the things somebody already typed and is silent by
    construction on the next one.

    So: any attribute carrying ``_connections`` is a pool, and its label comes
    from the manager's own ``_label`` — one writer, one reader. A pool added
    tomorrow appears here without anyone updating a list.
    """
    found: List[tuple] = []
    for attr, value in list(vars(engine).items()):
        if not attr.startswith("_ws"):
            continue
        if value is None:
            # A declared-but-unstarted pool is still a pool, and "never
            # started" is a state worth naming — see _pool_report.
            found.append((attr.lstrip("_").replace("ws_", "") or attr, attr, None))
            continue
        if not hasattr(value, "_connections"):
            continue
        label = str(getattr(value, "_label", "") or attr.lstrip("_"))
        found.append((label, attr, value))
    found.sort(key=lambda t: t[0])
    return found


def _stream_kinds(pools: List[Dict[str, Any]], engine: Any) -> Dict[str, Any]:
    """Which *kinds* of stream we subscribe to at all.

    The 2026-08-05 audit's central finding was an absence: ``@aggTrade`` and
    ``@trade`` appear nowhere in any ``.start()`` call, while a complete trade
    handler sits in ``main.py`` waiting for messages that never arrive. An
    absence cannot be seen in a list of what *is* subscribed, so the expected
    kinds are enumerated here and each is reported present or absent by name.
    """
    # Full stream names, not suffixes. Splitting on "@" and keeping the tail
    # turns "!ticker@arr" into "@arr" and loses the only part that identifies
    # it — the whole-board ticker then reads as unsubscribed while it is
    # running. Caught by the test that asserts each kind by name, which is
    # exactly what that test is for.
    subscribed: set[str] = set()
    for _label, _attr, mgr in _discover_pools(engine):
        if mgr is None:
            continue
        for conn in getattr(mgr, "_connections", []) or []:
            for s in getattr(conn, "streams", []) or []:
                subscribed.add(str(s))

    def _has(*needles: str) -> bool:
        return any(any(n in s for s in subscribed) for n in needles)

    # Distinct kinds, for display: the symbol prefix is dropped so 75 kline
    # streams collapse to one row, but the stream's own name is preserved.
    suffixes = sorted({
        ("@" + s.split("@", 1)[1]) if "@" in s and not s.startswith("!") else s
        for s in subscribed
    })

    return {
        "distinct_stream_suffixes": suffixes,
        "kinds": {
            "klines": _has("@kline_"),
            "liquidations": _has("@forceOrder"),
            "all_market_ticker": _has("!ticker@arr"),
            # The two that decide whether layer 4 exists at all.
            "aggregate_trades": _has("@aggTrade"),
            "raw_trades": _has("@trade"),
            "depth": _has("@depth"),
        },
    }


# ───────────────────────────────────────────────────────────────────────────
# Candle series
# ───────────────────────────────────────────────────────────────────────────

def _series_report(engine: Any, *, sample_limit: int = 400) -> Dict[str, Any]:
    """Per symbol × timeframe: how many bars, and how old the newest one is.

    Rolled up per timeframe with the worst offenders named, because a
    per-symbol table across 75 symbols × 6 timeframes is 450 rows nobody reads.
    The rollup keeps both denominators — how many series exist and how many are
    stale — since a stale *fraction* over a shrinking population reads healthy
    while the population disappears.
    """
    store = getattr(engine, "data_store", None)
    out: Dict[str, Any] = {"present": store is not None, "by_timeframe": {}}
    if store is None:
        return out

    # The live scan universe. A rotated-out mover's bucket freezes by design —
    # it has no WS kline subscription and nothing re-seeds it once its 6h
    # promotion lapses — so counting it as "stale" beside a core pair pools a
    # known, harmless state with a real fault and reports the fault at ~4x its
    # true size. On the first live read this page showed 95 of 286 1m series
    # stale; the scan universe is 75, so most of that was symbols nobody scans.
    #
    # Split, never subtracted: the rotated-out count is retained because an
    # unbounded pile of frozen buckets is its own finding (286 symbols held for
    # a 75-symbol universe), just not a *staleness* finding.
    pair_mgr = getattr(engine, "pair_mgr", None)
    try:
        live_universe = {str(x).upper() for x in (getattr(pair_mgr, "pairs", {}) or {})}
    except Exception:  # noqa: BLE001
        live_universe = set()

    candles = getattr(store, "candles", {}) or {}
    now = time.time()
    per_tf: Dict[str, Dict[str, Any]] = {}

    for symbol, by_tf in list(candles.items())[:sample_limit]:
        in_universe = (not live_universe) or (str(symbol).upper() in live_universe)
        if not isinstance(by_tf, dict):
            continue
        for tf, data in by_tf.items():
            slot = per_tf.setdefault(tf, {
                "series": 0, "stale": 0, "undated": 0,
                "series_scanned": 0, "stale_scanned": 0, "undated_scanned": 0,
                "bars_min": None, "bars_max": None,
                "oldest_newest_bar_age_s": None, "stalest_symbols": [],
            })
            slot["series"] += 1
            if in_universe:
                slot["series_scanned"] += 1
            closes = data.get("close") if isinstance(data, dict) else None
            n = int(len(closes)) if closes is not None else 0
            slot["bars_min"] = n if slot["bars_min"] is None else min(slot["bars_min"], n)
            slot["bars_max"] = n if slot["bars_max"] is None else max(slot["bars_max"], n)

            open_time = data.get("open_time") if isinstance(data, dict) else None
            if open_time is None or len(open_time) == 0:
                # Undated is its own bucket, not folded into stale: a series
                # whose bars carry no timestamps cannot be aged at all, and
                # calling that "fresh" is how a restart-dropped `open_time`
                # field stayed invisible (#842).
                slot["undated"] += 1
                slot["undated_scanned"] += int(in_universe)
                continue
            try:
                newest_ms = float(open_time[-1])
            except (TypeError, ValueError, IndexError):
                slot["undated"] += 1
                slot["undated_scanned"] += int(in_universe)
                continue
            if newest_ms != newest_ms:  # NaN
                slot["undated"] += 1
                slot["undated_scanned"] += int(in_universe)
                continue
            age = max(0.0, now - newest_ms / 1000.0)
            budget = _INTERVAL_SECONDS.get(tf, 300) * _STALE_MULTIPLIER
            if age > budget:
                slot["stale"] += 1
                if in_universe:
                    slot["stale_scanned"] += 1
                    # Only a scanned symbol's staleness is actionable, so only
                    # those are named — a list headed by four-day-old rotated-out
                    # movers buries the core pair that actually broke.
                    slot["stalest_symbols"].append((symbol, round(age, 1)))
            if (slot["oldest_newest_bar_age_s"] is None
                    or age > slot["oldest_newest_bar_age_s"]):
                slot["oldest_newest_bar_age_s"] = round(age, 1)

    for tf, slot in per_tf.items():
        slot["stalest_symbols"] = [
            {"symbol": s, "age_s": a}
            for s, a in sorted(slot["stalest_symbols"], key=lambda x: -x[1])[:10]
        ]
        slot["stale_budget_s"] = _INTERVAL_SECONDS.get(tf, 300) * _STALE_MULTIPLIER
    out["by_timeframe"] = per_tf
    out["symbols_sampled"] = min(len(candles), sample_limit)
    out["symbols_total"] = len(candles)
    out["symbols_in_scan_universe"] = len(live_universe)
    # Buckets held for symbols nobody scans. Not a staleness fault — an
    # unbounded-growth one, and it has never had a number anywhere.
    out["symbols_retained_outside_universe"] = max(
        0, len(candles) - len(live_universe)
    ) if live_universe else None
    return out


# ───────────────────────────────────────────────────────────────────────────
# Derived inputs — provenance, not just freshness
# ───────────────────────────────────────────────────────────────────────────

def _live_tick_report(store: Any) -> Dict[str, Any]:
    """The live aggTrade series, and whether anything is reading it.

    Two facts that must not collapse into one:

    * **is the feed working** — `fed` / `quiet` / `subscribed_silent`, where
      the third is a subscription that did not take and is invisible in any
      count keyed on arrival;
    * **is the money path reading it** — `serving_consumers`, which is the
      `TICKS_LIVE_FOR_CONSUMERS` flag and *not* a consequence of the feed being
      healthy. A working feed is not a reason to change what a live gate sees.

    The drift panel is the measurement the handover is waiting on: the seeded
    store's age against the live one's, per symbol, which is exactly the error
    every current consumer carries.
    """
    out: Dict[str, Any] = {"present": False}
    try:
        from config import (
            AGGTRADE_MAX_SYMBOLS,
            AGGTRADE_STREAM_ENABLED,
            TICKS_LIVE_FOR_CONSUMERS,
        )
        from src.live_ticks import get_store as _live

        live = _live()
        out = dict(live.health())
        out["present"] = True
        out["stream_enabled"] = bool(AGGTRADE_STREAM_ENABLED)
        out["max_symbols"] = int(AGGTRADE_MAX_SYMBOLS)
        # The flag, read as the flag. Never inferred from feed health.
        out["serving_consumers"] = bool(TICKS_LIVE_FOR_CONSUMERS)
        seeded = getattr(store, "ticks", {}) if store is not None else {}
        out["drift_vs_seeded"] = live.compare_with_seeded(seeded or {})
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def _footprint_report() -> Dict[str, Any]:
    """Per-bar, per-price volume — health, bounds, and one real sample.

    The sample matters: a row count proves the store is filling and says
    nothing about whether the shape is usable. A rendered bar shows the bin
    granularity, the point of control, the most one-sided level and the size
    distribution — so a reader can see the measurement rather than a promise
    of one.
    """
    out: Dict[str, Any] = {"present": False}
    try:
        from src.footprint import get_store as _fp

        store = _fp()
        out = dict(store.health())
        out["present"] = True
        # Newest sealed bar from whichever symbol has one. Not "the busiest" —
        # picking by volume would show the healthiest example every time and
        # hide a store that is filling for one symbol and nothing else.
        sample = None
        for sym in sorted(getattr(store, "_by_symbol", {})):
            sample = store.sample(sym)
            if sample is not None:
                break
        out["sample"] = sample
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def _depth_report() -> Dict[str, Any]:
    """The real book: health, and what it disagrees with.

    Two things, and the second is the one the phase turns on. Health says the
    feed is arriving. The **comparison** says whether it matters — top-of-book
    imbalance against full-depth imbalance, computed from the same snapshot so
    the two differ only in depth and not in timing.

    A sign flip is counted apart from the magnitude of the disagreement,
    because a consumer testing against zero and one testing against a threshold
    are harmed by different things: the OBI gate compares a fraction to 0.65,
    while `book_imbalance` is signed toward the trade and its sign is the whole
    reading.
    """
    out: Dict[str, Any] = {"present": False}
    try:
        from config import DEPTH_LIVE_FOR_CONSUMERS, DEPTH_STREAM_ENABLED
        from src.depth_book import get_store as _db

        store = _db()
        out = dict(store.health())
        out["present"] = True
        out["measurement_enabled"] = DEPTH_STREAM_ENABLED
        # The handover state, named on the panel rather than inferred. While
        # this is False the four consumers are still reading one quote, and a
        # panel showing a healthy depth feed without saying so would read as
        # though the book were in use.
        out["live_for_consumers"] = DEPTH_LIVE_FOR_CONSUMERS
        out["comparison"] = store.comparison_census()
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)
    return out


def _derived_report(engine: Any) -> Dict[str, Any]:
    """Where each derived input actually comes from.

    Every entry here answers "is this the thing I think it is" before it
    answers "how old is it". That ordering is the whole point of the panel.
    """
    store = getattr(engine, "data_store", None)
    flow = getattr(engine, "_order_flow_store", None)
    scanner = getattr(engine, "scanner", None) or getattr(engine, "_scanner", None)

    ticks = getattr(store, "ticks", {}) if store is not None else {}
    tick_symbols = len(ticks or {})
    tick_rows = sum(len(v or []) for v in (ticks or {}).values())
    # Newest trade timestamp across the store, in ms. If the tick feed is a
    # seed-time snapshot this is hours old while the store looks populated.
    newest_trade_ms = 0.0
    for rows in (ticks or {}).values():
        if rows:
            try:
                newest_trade_ms = max(newest_trade_ms, float(rows[-1].get("time", 0) or 0))
            except (AttributeError, TypeError, ValueError):
                continue

    return {
        "cvd": {
            # Named source, not implied. This is a per-bar taker-buy split
            # from closed klines, NOT tick-derived order flow: one signed
            # number per bar, with no per-price-level volume behind it.
            "source": "kline_taker_buy",
            "detail": "closed 1m/15m kline Q/q fields — not tick data",
            "symbols_tracked": len(getattr(flow, "_running_cvd", {}) or {})
            if flow is not None else 0,
            "symbols_tracked_15m": len(getattr(flow, "_running_cvd_15m", {}) or {})
            if flow is not None else 0,
        },
        "ticks": {
            # The seeded store. `append_tick` and the `trade` handler both
            # exist and nothing has ever subscribed a trade stream, so this is
            # whatever `/fapi/v1/trades` returned when each symbol was seeded.
            "source": "rest_seed_snapshot",
            "detail": (
                "/fapi/v1/trades limit=1000 at seed time; no @trade "
                "subscription feeds it"
            ),
            "symbols": tick_symbols,
            "rows": tick_rows,
            "newest_trade_age_s": (
                round(max(0.0, time.time() - newest_trade_ms / 1000.0), 1)
                if newest_trade_ms else None
            ),
            "consumers": [
                "scanner._build_scan_context (recent_ticks)",
                "channels.scalp WHALE_MOMENTUM tick-volume gate",
                "trade_monitor",
            ],
        },
        # Phase 2a. Reported beside the seeded store rather than replacing it,
        # because the handover is a separate decision from the feed working —
        # `serving_consumers` is what says which one the money path actually
        # sees, and it is a flag, not a consequence of health.
        "live_ticks": _live_tick_report(store),
        # Phase 2b. Reported beside the tick ring, not inside it: the ring
        # answers "what just traded", the footprint answers "at which price,
        # and which side was aggressive" — and only the second can say whether
        # a level was defended.
        "footprint": _footprint_report(),
        # What the CONSUMERS read. Kept as its own entry beside `depth` below,
        # because until the handover flag flips these are two different books
        # and the panel must not let the healthier one stand for both.
        "order_book": {
            "source": "book_ticker",
            "quality": "top_of_book_only",
            "detail": (
                "one bid and one ask from /fapi/v1/ticker/bookTicker — cannot "
                "see walls, refills or absorption. Four consumers read this: "
                "the OBI execution gate (OBI_DEFAULT_LEVELS=20), "
                "entry_features.book_imbalance (bids[:10]), the WHALE OBI "
                "check, and the AI predictor's 0.25-weighted order_book score"
            ),
            "symbols_cached": len(
                getattr(scanner, "_order_book_snapshot_cache", {}) or {}
            ) if scanner is not None else 0,
        },
        # Phase 2c. The real book, and the disagreement it has with the quote
        # above. Reported separately for the same reason the footprint is
        # reported beside the tick ring rather than inside it.
        "depth": _depth_report(),
        "open_interest": {
            "source": "rest_poll",
            "symbols": len(getattr(flow, "_oi", {}) or {}) if flow is not None else 0,
        },
        "funding": {
            "source": "rest_poll",
            "symbols": len(getattr(flow, "_funding_rates", {}) or {})
            if flow is not None else 0,
        },
        "liquidations": {
            "source": "ws_force_order",
            "symbols": len(getattr(flow, "_liqs", {}) or {}) if flow is not None else 0,
        },
    }


# ───────────────────────────────────────────────────────────────────────────
# Primitive census — the hollow-detector panel
# ───────────────────────────────────────────────────────────────────────────

def _primitive_report() -> Dict[str, Any]:
    """Which structural primitives can actually produce a value.

    Read from the producing modules themselves rather than mirrored, and
    rendered **whether or not anything is wrong** — a detector that is dead
    behind a passing gate looks exactly like a working one, which is how
    ``orderblocks`` survived with no writer at all.
    """
    rows: List[Dict[str, Any]] = []

    try:
        # Read the LIVE status from the module that decides it, never the
        # dataclass default — the default still says `not_implemented`, which
        # is the honest value for a result nobody ran.
        from src import layer3_repair as _l3
        status = _l3.detector_status()
        _c = _l3.census()
        _det = max(1, _c.get("detections", 0))
        rows.append({
            "primitive": "orderblocks",
            "status": status,
            "healthy": status not in ("not_implemented", "", "measure_disabled"),
            "detail": (
                "declared on SMCResult and never assigned — every "
                "`bool(fvgs) or bool(orderblocks)` gate is `bool(fvgs)` alone"
                if status in ("not_implemented", "measure_disabled") else
                # Dark: the detector runs and the gates do not see it. The
                # number that matters is how often the gate WOULD flip, which
                # is a per-detection rate, not a count of zones.
                f"detector live (Phase 3, DARK — gates still read an empty "
                f"list). Found on {_c.get('ob_found', 0)} of {_c.get('detections', 0)} "
                f"detections; would flip `bool(fvgs) or bool(orderblocks)` "
                f"False→True on {_c.get('ob_found_when_fvg_empty', 0)} "
                f"({_c.get('ob_found_when_fvg_empty', 0) / _det * 100:.1f}%)"
            ),
        })
        _lb_live, _lb_wide = _l3.lookbacks()
        rows.append({
            "primitive": "fvg_lookback_wide",
            "status": f"live={_lb_live} measured={_lb_wide}",
            "healthy": True,
            "detail": (
                f"the wide window would admit {_c.get('fvg_narrow_empty_wide_found', 0)} "
                f"of {_c.get('detections', 0)} detections the narrow one rejects "
                f"({_c.get('fvg_narrow_empty_wide_found', 0) / _det * 100:.1f}%). "
                "DARK — the gates still read the narrow list. This says how much "
                "of the book would CHANGE and is structurally incapable of saying "
                "how much better it would be: these gates reject pre-scoring, so "
                "the candidates a wider window would admit have no row, no "
                "outcome and no ledger entry. Pricing that needs a shadow gate "
                "chain."
            ),
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"primitive": "orderblocks", "status": f"unreadable: {exc}",
                     "healthy": False, "detail": ""})

    try:
        import inspect

        from src import smc
        lookback = inspect.signature(smc.detect_fvg).parameters["lookback"].default
        rows.append({
            "primitive": "fvg",
            "status": f"lookback={lookback}",
            # Not a pass/fail: the lookback is a design choice. It is surfaced
            # because it is what makes a deliberately loose gate behave like a
            # strict one, and that is invisible from the gate's own code.
            "healthy": True,
            "detail": (
                f"sees ~{int(lookback) + 2} bars — on 15m that is "
                f"~{(int(lookback) + 2) * 15 / 60:.1f}h of structure"
            ),
        })
    except Exception as exc:  # noqa: BLE001
        rows.append({"primitive": "fvg", "status": f"unreadable: {exc}",
                     "healthy": False, "detail": ""})

    return {"rows": rows}


def _vp_report(scanner: Any) -> Dict[str, Any]:
    """Volume-profile coverage, read from the store's REAL attribute.

    The first cut guessed ``_cache``; ``VolumeProfileStore`` holds ``_results``.
    So the live page read ``micro 0 · macro 0`` on two stores that were running,
    which says "volume profile is dead" — and layers 1-2 of the price-action
    program rest on it. An all-zero column is a claim about the reader before it
    is a claim about the system, and a guessed attribute name cannot fail
    loudly: ``getattr(x, "_cache", {})`` returns ``{}`` just as convincingly for
    "empty" as for "wrong name".

    So the attribute is read by name and its absence is reported as
    ``unreadable`` rather than as zero.
    """
    def _count(store: Any) -> Any:
        if store is None:
            return {"symbols": 0, "state": "absent"}
        results = getattr(store, "_results", None)
        if results is None:
            return {"symbols": None, "state": "unreadable: no _results attribute"}
        return {"symbols": len(results), "state": "ok"}

    return {
        "micro": _count(getattr(scanner, "volume_profile_store", None)
                        if scanner is not None else None),
        "macro": _count(getattr(scanner, "volume_profile_store_macro", None)
                        if scanner is not None else None),
    }


def _levels_report(engine: Any) -> Dict[str, Any]:
    """LevelBook and volume-profile coverage — layers 1 and 2."""
    scanner = getattr(engine, "scanner", None) or getattr(engine, "_scanner", None)
    book = getattr(scanner, "level_book", None) if scanner is not None else None
    levels = getattr(book, "_levels", {}) if book is not None else {}
    refresh_ts = getattr(book, "_refresh_ts", {}) if book is not None else {}
    ages = [
        _age(ts, monotonic=False) for ts in (refresh_ts or {}).values()
    ]
    ages = [a for a in ages if a is not None]
    return {
        "level_book": {
            "present": book is not None,
            "symbols": len(levels or {}),
            "levels_total": sum(len(v or []) for v in (levels or {}).values()),
            "oldest_refresh_age_s": round(max(ages), 1) if ages else None,
        },
        "volume_profile": _vp_report(scanner),
    }


# ───────────────────────────────────────────────────────────────────────────
# Rate-limit budget
# ───────────────────────────────────────────────────────────────────────────

def _weight_report() -> Dict[str, Any]:
    """Live weight usage against budget, plus the declared-weight table.

    ``update_from_header`` has been syncing the authoritative
    ``x-mbx-used-weight-1m`` value into the limiter all along and nothing ever
    rendered it — noted as an open follow-up in ``ACTIVE_CONTEXT.md``. The
    declared table sits beside the live number deliberately: a disagreement
    between what we believe a call costs and what the exchange says we have
    spent is the early symptom of an under-declaration, and the alternative to
    seeing it here is discovering it as a ban.
    """
    out: Dict[str, Any] = {}
    try:
        from src.rate_limiter import futures_rate_limiter, spot_rate_limiter
        for name, lim in (("futures", futures_rate_limiter), ("spot", spot_rate_limiter)):
            used = int(getattr(lim, "_used", 0) or 0)
            budget = int(getattr(lim, "_budget", 0) or 0)
            out[name] = {
                "used": used,
                "budget": budget,
                "pct": round(used / budget * 100.0, 1) if budget else None,
            }
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)

    try:
        from src.binance_weights import describe
        out["declared"] = describe()
    except Exception as exc:  # noqa: BLE001
        out["declared_error"] = str(exc)
    return out


# ───────────────────────────────────────────────────────────────────────────
# Entry point
# ───────────────────────────────────────────────────────────────────────────

def build_data_intake(engine: Any) -> Dict[str, Any]:
    """Assemble the whole report from live engine state.

    Every section is independently fail-soft: a section that cannot be read
    reports its own error rather than emptying the page, because "the WS pool
    is down" and "the WS section raised" are different states and pooling them
    would report a fault that is not happening.
    """
    report: Dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at": time.time(),
    }

    sections = (
        ("pools", lambda: [
            _pool_report(label, mgr)
            for label, _attr, mgr in _discover_pools(engine)
        ]),
        ("stream_kinds", lambda: _stream_kinds([], engine)),
        ("series", lambda: _series_report(engine)),
        ("derived", lambda: _derived_report(engine)),
        ("primitives", lambda: _primitive_report()),
        ("levels", lambda: _levels_report(engine)),
        ("weight", lambda: _weight_report()),
    )
    for key, fn in sections:
        try:
            report[key] = fn()
        except Exception as exc:  # noqa: BLE001
            from src import fail_open
            fail_open.record(f"data_intake.{key}", exc)
            report[key] = {"error": str(exc)}
    return report
