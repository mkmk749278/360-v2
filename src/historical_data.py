"""Historical data seeding – fetch OHLCV and recent trades on boot.

Uses public Binance REST endpoints with rate-limit-compliant delays.
Supports disk-based caching so restarts only fetch the data that is
missing since the last snapshot (gap-fill), cutting boot times from
3-5 minutes down to ~15 seconds after a brief outage.
"""

from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from config import (
    BATCH_REQUEST_DELAY,
    GEM_SEED_TIMEFRAMES,
    SEED_TICK_LIMIT,
    SEED_TIMEFRAMES,
    TimeframeSeed,
)
from src.binance import BinanceClient
from src.pair_manager import PairManager
from src.utils import get_logger

log = get_logger("historical")

# ---------------------------------------------------------------------------
# Disk-cache paths
# ---------------------------------------------------------------------------
CACHE_DIR = Path("data/cache")
_TICKS_DIR = CACHE_DIR / "ticks"
_META_FILE = CACHE_DIR / "metadata.json"

# Maximum candles to retain per symbol-timeframe bucket.
# 1,000 provides headroom for 365 daily gem candles + buffer, and the
# existing 750-candle 1m/5m seeds used by SCALP/SWING channels.
_MAX_CANDLES_PER_BUCKET: int = 1_000
# Seconds per candle interval — used to estimate how many candles are missing
_INTERVAL_SECONDS: Dict[str, int] = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3_600,
    "4h": 14_400,
    "1d": 86_400,
    "1w": 604_800,
}

# If the cache is older than this many seconds, do a full re-seed for that
# symbol/timeframe rather than trying to gap-fill (avoids huge limit requests)
_MAX_GAP_FILL_SECONDS = 24 * 3_600  # 24 hours

# Sentinel returned by _estimate_gap_candles to signal "cache too stale, do full fetch"
_FULL_FETCH_SENTINEL = 9_999

# Extra candles fetched on top of the estimated gap to cover partial candles and clock skew
_GAP_BUFFER_CANDLES = 5

# Gap-fill concurrency settings
_GAP_FILL_DELAY: float = 0.1          # shorter per-call sleep during gap-fill
_GAP_FILL_CONCURRENT_SYMBOLS: int = 10  # symbols processed in parallel (safe with 5,000/min budget)
_TICK_REFRESH_AGE_SECS: int = 300      # skip tick refresh if cache is fresher than this


class HistoricalDataStore:
    """In-memory store for OHLCV and tick data, keyed by symbol + timeframe."""

    def __init__(self) -> None:
        # candles[symbol][timeframe] = {"open": [], "high": [], "low": [], "close": [], "volume": []}
        self.candles: Dict[str, Dict[str, Dict[str, np.ndarray]]] = {}
        # ticks[symbol] = [{"price": float, "qty": float, "isBuyerMaker": bool, "time": int}, …]
        self.ticks: Dict[str, List[Dict[str, Any]]] = {}
        # Per-symbol-per-interval timestamp of the most-recent ``update_candle``
        # call.  Used by the scanner's data-staleness gate to reject signal
        # dispatches against frozen kline feeds (e.g. recently-promoted pairs
        # whose WebSocket subscription hasn't caught up yet — bug 2026-05-11
        # QUSDT carbon-copy emissions at deterministic -0.10358%).  None /
        # absent means we've never received a kline for that (symbol, interval).
        self._last_kline_update_ts: Dict[str, Dict[str, float]] = {}
        self._client = BinanceClient("spot")
        self._futures_client = BinanceClient("futures")
        # Merge telemetry (2026-08-01).  ``_merge_candles`` used to concatenate
        # blindly, and ``_estimate_gap_candles`` over-fetches by
        # ``_GAP_BUFFER_CANDLES`` *on purpose*, so every gap fill re-appended
        # bars the bucket already had.  Dedupe is the fix; these counters are
        # how we know it is doing work and how we see the case it cannot fix
        # (a merge where one side carries no ``open_time``, which is undedupable
        # by construction rather than clean).
        self.merge_duplicate_bars_dropped: int = 0
        self.merge_undedupable: int = 0

    # ------------------------------------------------------------------
    # OHLCV fetch
    # ------------------------------------------------------------------

    async def fetch_candles(
        self, symbol: str, interval: str, limit: int, market: str = "spot",
    ) -> Dict[str, np.ndarray]:
        """Fetch OHLCV candles for one symbol/interval."""
        client = self._futures_client if market == "futures" else self._client
        try:
            raw = await client.fetch_klines(symbol, interval, limit)
        except Exception as exc:
            log.error("Candle fetch error %s %s: %s", symbol, interval, exc)
            return {}

        if not raw:
            return {}

        opens = np.array([float(c[1]) for c in raw])
        highs = np.array([float(c[2]) for c in raw])
        lows = np.array([float(c[3]) for c in raw])
        closes = np.array([float(c[4]) for c in raw])
        volumes = np.array([float(c[5]) for c in raw])
        # Binance kline columns: [0]=open_time … [7]=quote_asset_volume …
        # [10]=taker_buy_quote_asset_volume — USD buy/sell split for CVD seeding
        volume_usd = np.array([float(c[7]) for c in raw])
        taker_buy_vol_usd = np.array([float(c[10]) for c in raw])

        # Bar open time (ms).  Carried so a consumer can locate the bar covering
        # a given wall clock instead of inferring an index from elapsed time —
        # inference assumes the array is gap-free and its last bar is current,
        # and neither holds on a feed that dropped frames or froze (the
        # MVLLUSDT 11-hour freeze below is the standing counter-example).
        open_time = np.array([float(c[0]) for c in raw])

        return {
            "open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes,
            "open_time": open_time,
            "volume_usd": volume_usd, "taker_buy_vol_usd": taker_buy_vol_usd,
        }

    # ------------------------------------------------------------------
    # Recent trades fetch
    # ------------------------------------------------------------------

    async def fetch_recent_trades(
        self, symbol: str, limit: int = SEED_TICK_LIMIT, market: str = "spot",
    ) -> List[Dict[str, Any]]:
        client = self._futures_client if market == "futures" else self._client
        capped_limit = min(limit, 1000)
        try:
            if market == "futures":
                raw = await client._get(
                    "/fapi/v1/trades",
                    params={"symbol": symbol, "limit": capped_limit},
                    weight=1,
                )
            else:
                raw = await client._get(
                    "/api/v3/trades",
                    params={"symbol": symbol, "limit": capped_limit},
                    weight=1,
                )
        except Exception as exc:
            log.error("Trade fetch error %s: %s", symbol, exc)
            return []

        if not raw:
            return []

        return [
            {
                "price": float(t["price"]),
                "qty": float(t["qty"]),
                "isBuyerMaker": t.get("isBuyerMaker", False),
                "time": t.get("time", 0),
            }
            for t in raw
        ]

    # ------------------------------------------------------------------
    # Full seed for one symbol
    # ------------------------------------------------------------------

    async def seed_symbol(self, symbol: str, market: str = "spot") -> None:
        """Seed all timeframes + ticks for a single symbol.

        All timeframe fetches are dispatched concurrently via
        ``asyncio.gather`` so that a single symbol's worth of data is
        retrieved in one round-trip rather than one sequential request per
        timeframe.  Ticks are fetched in parallel with the candles.
        A single rate-limit sleep is taken afterwards (instead of one per
        request), which cuts per-symbol boot time by the number of
        timeframes.
        """
        self.candles.setdefault(symbol, {})

        async def _fetch_tf(tf: TimeframeSeed) -> None:
            data = await self.fetch_candles(symbol, tf.interval, tf.limit, market)
            if data:
                if len(data.get("close", [])) > _MAX_CANDLES_PER_BUCKET:
                    data = {k: v[-_MAX_CANDLES_PER_BUCKET:] for k, v in data.items()}
                self.candles[symbol][tf.interval] = data
                # Stamp freshness on REST writes too (2026-07-10).  Pre-fix only
                # live WS ``update_candle`` frames stamped ``_last_kline_update_ts``,
                # so a promoted MOVER pair — seeded here, never WS-subscribed —
                # reported ``last_kline_age_seconds() is None`` for its whole
                # life.  Both staleness protections (the scanner's dispatch
                # gate and trade_monitor's mark-feed fallback, #706) fail-open
                # on None, which is how MVLLUSDT's price froze at its last
                # seeded close for 11+ hours while SL/TP/trail ran blind.
                self._last_kline_update_ts.setdefault(symbol, {})[tf.interval] = time.time()
                log.debug("Seeded %s %s: %d candles", symbol, tf.interval, len(data["close"]))

        async def _fetch_ticks() -> None:
            ticks = await self.fetch_recent_trades(symbol, SEED_TICK_LIMIT, market)
            if ticks:
                self.ticks[symbol] = ticks
                log.debug("Seeded %s ticks: %d", symbol, len(ticks))

        # Fetch all timeframes and ticks simultaneously for this symbol
        await asyncio.gather(
            *[_fetch_tf(tf) for tf in SEED_TIMEFRAMES],
            _fetch_ticks(),
        )

        # One consolidated rate-limit pause after all parallel fetches
        await asyncio.sleep(BATCH_REQUEST_DELAY)

    # ------------------------------------------------------------------
    # Full boot seed
    # ------------------------------------------------------------------

    async def seed_all(self, pair_mgr: PairManager) -> int:
        """Seed historical data for every active pair.

        Up to :data:`_GAP_FILL_CONCURRENT_SYMBOLS` symbols are seeded in
        parallel.  Within each symbol, all timeframe fetches are already
        parallelised by :meth:`seed_symbol`, so the overall boot time is
        reduced from O(symbols × timeframes) sequential requests to
        O(⌈symbols / concurrency⌉) rounds.

        Returns
        -------
        int
            Number of pairs that were successfully seeded (have candle data).
        """
        total = len(pair_mgr.pairs)
        log.info("Starting historical data seed for %d pairs …", total)

        semaphore = asyncio.Semaphore(_GAP_FILL_CONCURRENT_SYMBOLS)

        async def _seed_one(sym: str, info: Any) -> None:
            async with semaphore:
                await self.seed_symbol(sym, info.market)
                for tf_name, data in self.candles.get(sym, {}).items():
                    pair_mgr.record_candles(sym, tf_name, len(data.get("close", [])))

        await asyncio.gather(*[_seed_one(sym, info) for sym, info in pair_mgr.pairs.items()])

        seeded = sum(1 for sym in pair_mgr.pairs if self.candles.get(sym))
        log.info(
            "Historical data seed complete: %d / %d pairs seeded.", seeded, total
        )
        if seeded == 0 and total > 0:
            log.critical(
                "All %d pairs failed to seed — no candle data available.", total
            )
        return seeded

    # ------------------------------------------------------------------
    # Disk-cache: save
    # ------------------------------------------------------------------

    def _save_snapshot_sync(self) -> None:
        """Blocking disk I/O for save_snapshot — runs in a thread-pool executor."""
        try:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            _TICKS_DIR.mkdir(parents=True, exist_ok=True)

            saved_at = datetime.now(timezone.utc).isoformat()
            meta: Dict[str, Any] = {}
            saved_count = 0

            for symbol, timeframes in self.candles.items():
                for interval, arrays in timeframes.items():
                    if not arrays or "close" not in arrays or len(arrays["close"]) == 0:
                        continue
                    try:
                        path = CACHE_DIR / f"{symbol}_{interval}.npz"
                        _save_kw: Dict[str, Any] = {
                            "open": arrays["open"],
                            "high": arrays["high"],
                            "low": arrays["low"],
                            "close": arrays["close"],
                            "volume": arrays["volume"],
                        }
                        # Bar timestamps survive the restart, or every consumer
                        # that locates a bar by wall clock is blind until the
                        # array rolls over. They were absent here from the day
                        # `open_time` was added (2026-07-31): the snapshot wrote
                        # five keys, the loader read the same five, and
                        # `_merge_candles` then *correctly* refused to merge a
                        # timestamped fetch onto an untimestamped cache — so
                        # after every restart the whole store was undatable.
                        # Only saved when index-aligned: a short array whose
                        # index i does not name bar i is worse than none.
                        if len(arrays.get("open_time", ())) == len(arrays["close"]):
                            _save_kw["open_time"] = arrays["open_time"]
                        for _ek in ("volume_usd", "taker_buy_vol_usd"):
                            if _ek in arrays and len(arrays[_ek]) > 0:
                                _save_kw[_ek] = arrays[_ek]
                        np.savez_compressed(path, **_save_kw)
                        key = f"{symbol}:{interval}"
                        meta[key] = {
                            "count": int(len(arrays["close"])),
                            "saved_at": saved_at,
                        }
                        saved_count += 1
                    except Exception as exc:  # pragma: no cover
                        log.warning("Snapshot save failed for %s %s: %s", symbol, interval, exc)

            for symbol, ticks in self.ticks.items():
                if not ticks:
                    continue
                try:
                    tick_path = _TICKS_DIR / f"{symbol}.json"
                    with tick_path.open("w", encoding="utf-8") as fh:
                        json.dump(ticks, fh)
                except Exception as exc:  # pragma: no cover
                    log.warning("Tick snapshot save failed for %s: %s", symbol, exc)

            with _META_FILE.open("w", encoding="utf-8") as fh:
                json.dump(meta, fh)

            log.info("Snapshot saved: %d symbol-timeframe combos (saved_at=%s)", saved_count, saved_at)
        except Exception as exc:  # pragma: no cover
            log.error("save_snapshot error: %s", exc)

    async def save_snapshot(self) -> None:
        """Persist current candle and tick data to disk for fast restarts."""
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._save_snapshot_sync)

    # ------------------------------------------------------------------
    # Disk-cache: load
    # ------------------------------------------------------------------

    def load_snapshot(self) -> bool:
        """Load cached candle and tick data from disk.

        Returns True if cache was found and loaded, False otherwise.
        """
        try:
            if not _META_FILE.exists():
                return False

            with _META_FILE.open("r", encoding="utf-8") as fh:
                meta: Dict[str, Any] = json.load(fh)

            if not meta:
                return False

            loaded_count = 0
            for key, info in meta.items():
                try:
                    symbol, interval = key.split(":", 1)
                    path = CACHE_DIR / f"{symbol}_{interval}.npz"
                    if not path.exists():
                        log.warning("Cache file missing: %s — skipping", path)
                        continue
                    with np.load(path, allow_pickle=False) as data:
                        _loaded: Dict[str, np.ndarray] = {
                            k: np.asarray(data[k], dtype=np.float64).ravel()
                            for k in ("open", "high", "low", "close", "volume")
                        }
                        for _ek in ("volume_usd", "taker_buy_vol_usd"):
                            if _ek in data.files:
                                _loaded[_ek] = np.asarray(data[_ek], dtype=np.float64).ravel()
                        # An npz written before timestamps were saved carries no
                        # `open_time`. Pad it with NaN rather than leaving the
                        # key absent: absence makes `_merge_candles` drop the
                        # timestamps of the *fresh* side too, so one legacy file
                        # keeps a bucket undatable for as long as it is merged
                        # into. NaN says "this bar's time is unknown", which a
                        # consumer can see and route around per bar.
                        if "open_time" in data.files:
                            _ot = np.asarray(data["open_time"], dtype=np.float64).ravel()
                        else:
                            _ot = np.full(len(_loaded["close"]), np.nan, dtype=np.float64)
                        if len(_ot) != len(_loaded["close"]):
                            _ot = np.full(len(_loaded["close"]), np.nan, dtype=np.float64)
                        _loaded["open_time"] = _ot
                        self.candles.setdefault(symbol, {})[interval] = _loaded
                    loaded_count += 1
                except Exception as exc:
                    log.warning("Failed to load cache for %s: %s — skipping", key, exc)

            for tick_file in _TICKS_DIR.glob("*.json"):
                symbol = tick_file.stem
                try:
                    with tick_file.open("r", encoding="utf-8") as fh:
                        self.ticks[symbol] = json.load(fh)
                except json.JSONDecodeError as exc:
                    log.warning(
                        "Failed to load ticks for %s: %s — deleting corrupted file %s",
                        symbol,
                        exc,
                        tick_file,
                    )
                    try:
                        tick_file.unlink()
                    except OSError as del_exc:
                        log.error("Could not delete corrupted tick file %s: %s", tick_file, del_exc)
                except Exception as exc:
                    log.warning("Failed to load ticks for %s: %s — skipping", symbol, exc)

            log.info("Snapshot loaded: %d symbol-timeframe combos from disk", loaded_count)
            return loaded_count > 0
        except Exception as exc:  # pragma: no cover
            log.error("load_snapshot error: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Disk-cache: gap-fill
    # ------------------------------------------------------------------

    async def gap_fill(self, pair_mgr: PairManager) -> int:
        """Fetch only the candles missing since the last snapshot.

        For each symbol+timeframe already in cache, calculates how many
        candles are needed based on the elapsed time since ``saved_at``,
        then fetches and merges them.  For symbol+timeframe combos not in
        cache, a full seed is performed.

        Uses concurrent processing (up to 4 symbols at a time) and skips
        tick refresh when the cache is fresher than 5 minutes.

        Returns
        -------
        int
            Number of pairs that have candle data after gap-fill.
        """
        try:
            if not _META_FILE.exists():
                log.info("No metadata found — falling back to full seed")
                return await self.seed_all(pair_mgr)

            with _META_FILE.open("r", encoding="utf-8") as fh:
                meta: Dict[str, Any] = json.load(fh)
        except Exception as exc:
            log.error("gap_fill: cannot read metadata (%s) — falling back to full seed", exc)
            return await self.seed_all(pair_mgr)

        total = len(pair_mgr.pairs)
        log.info("Gap-filling %d pairs …", total)

        semaphore = asyncio.Semaphore(_GAP_FILL_CONCURRENT_SYMBOLS)

        await asyncio.gather(*[
            self._gap_fill_symbol(sym, info, meta, semaphore, pair_mgr)
            for sym, info in pair_mgr.pairs.items()
        ])

        seeded = sum(1 for sym in pair_mgr.pairs if self.candles.get(sym))
        log.info("Gap-fill complete: %d / %d pairs have data.", seeded, total)
        if seeded == 0 and total > 0:
            log.critical(
                "Gap-fill produced no candle data for any of %d pairs.", total
            )
        return seeded

    async def _gap_fill_symbol(
        self,
        sym: str,
        info: Any,
        meta: Dict[str, Any],
        semaphore: asyncio.Semaphore,
        pair_mgr: PairManager,
    ) -> None:
        """Process gap-fill for a single symbol, bounded by *semaphore*."""
        async with semaphore:
            self.candles.setdefault(sym, {})

            # Collect timeframe fetch tasks
            tasks = []
            for tf in SEED_TIMEFRAMES:
                key = f"{sym}:{tf.interval}"
                if key in meta and sym in self.candles and tf.interval in self.candles[sym]:
                    saved_at_iso = meta[key].get("saved_at", "")
                    gap = self._estimate_gap_candles(saved_at_iso, tf.interval)
                    if gap <= 0:
                        log.debug("No gap needed for %s %s", sym, tf.interval)
                        continue
                    elif gap >= tf.limit:
                        log.debug(
                            "Cache stale for %s %s (gap=%d >= limit=%d) — full fetch",
                            sym, tf.interval, gap, tf.limit,
                        )
                        tasks.append(self._fetch_and_store(sym, tf.interval, tf.limit, info.market))
                    else:
                        tasks.append(self._gap_fetch_and_merge(sym, tf.interval, gap, tf.limit, info.market))
                else:
                    # Not in cache — full fetch
                    tasks.append(self._fetch_and_store(sym, tf.interval, tf.limit, info.market))

            if tasks:
                await asyncio.gather(*tasks)
                await asyncio.sleep(_GAP_FILL_DELAY)

            # Only refresh ticks if cache is older than 5 minutes
            should_refresh_ticks = True
            any_key = f"{sym}:{SEED_TIMEFRAMES[0].interval}"
            if any_key in meta:
                saved_at_iso = meta[any_key].get("saved_at", "")
                if saved_at_iso:
                    try:
                        saved_dt = datetime.fromisoformat(saved_at_iso)
                        if saved_dt.tzinfo is None:
                            saved_dt = saved_dt.replace(tzinfo=timezone.utc)
                        elapsed = (datetime.now(timezone.utc) - saved_dt).total_seconds()
                        should_refresh_ticks = elapsed > _TICK_REFRESH_AGE_SECS
                    except Exception:
                        pass

            if should_refresh_ticks:
                ticks = await self.fetch_recent_trades(sym, SEED_TICK_LIMIT, info.market)
                if ticks:
                    self.ticks[sym] = ticks
                await asyncio.sleep(_GAP_FILL_DELAY)

            for tf_name, data in self.candles.get(sym, {}).items():
                pair_mgr.record_candles(sym, tf_name, len(data.get("close", [])))

    async def _fetch_and_store(self, symbol: str, interval: str, limit: int, market: str) -> None:
        """Fetch a full set of candles and store them in the cache."""
        data = await self.fetch_candles(symbol, interval, limit, market)
        if data:
            self.candles.setdefault(symbol, {})[interval] = data
            log.debug("Full-seeded (no cache) %s %s: %d candles", symbol, interval, len(data["close"]))

    async def fetch_and_store_fallback(
        self, symbol: str, interval: str, limit: int, market: str
    ) -> None:
        """Fetch *limit* candles via REST and merge them into the store.

        Used by the WebSocket REST fallback to warm indicator pipelines after a
        WS outage so scanners can generate signals without waiting for candles to
        accumulate one-by-one.
        """
        data = await self.fetch_candles(symbol, interval, limit, market)
        if not data:
            return
        existing = self.candles.get(symbol, {}).get(interval)
        if existing and len(existing.get("close", [])) > 0:
            self.candles.setdefault(symbol, {})[interval] = self._merge_candles(
                existing, data, _MAX_CANDLES_PER_BUCKET
            )
        else:
            self.candles.setdefault(symbol, {})[interval] = data
        log.info(
            "Fallback seeded %s %s: %d candles",
            symbol, interval, len(data.get("close", [])),
        )

    async def refresh_timeframe(
        self, symbol: str, interval: str, limit: int, market: str = "futures"
    ) -> bool:
        """Re-pull ONE timeframe via REST, **replacing** the bucket, and stamp it.

        For a caller that needs a single timeframe kept alive on a symbol that may
        have left the scanned universe.  That caller is the SAR exit ledger's
        resolver (2026-07-28): it owes verdicts on trades whose symbol has since
        rotated out of the mover set, and a promoted mover has no WS subscription
        at all — ``_refresh_stale_mover_candles`` is its only writer and that runs
        only for *actively scanned* movers.  So the moment a mover rotates out its
        15m array stops advancing, the walker sees a window that ends before the
        exit, and every record on that symbol sits RUNNING until it silently ages
        into INSUFFICIENT.

        Neither existing path fits: ``seed_symbol`` pulls every timeframe plus the
        tick book, and ``fetch_and_store_fallback`` merges.

        **Replace, never merge.** ``_merge_candles`` concatenates blindly — it has
        no dedupe on ``open_time`` — so merging an overlapping REST pull duplicates
        bars, and a duplicate reads as a zero-width gap to the contiguity guard in
        ``main.fetch_ohlc_15m_since``, which then refuses the whole window.  A
        refresh written to make a record resolvable would have made it permanently
        unresolvable.  A fresh REST pull is contiguous and current by construction,
        so replacement is both simpler and the only correct write here.

        Callers pass the timeframe's own seed depth (``SEED_TIMEFRAMES``) so a
        replacement can never shorten an array another consumer is reading.

        Returns True when bars were written.  Never raises: a refresh failure
        leaves existing data untouched, and the caller records that it could not
        refresh rather than inheriting an exception mid-batch.
        """
        try:
            data = await self.fetch_candles(symbol, interval, limit, market)
            if not data:
                return False
            closes = data.get("close")
            # None/len, never truthiness — these are numpy arrays (hard limit).
            if closes is None or len(closes) == 0:
                return False
            if len(closes) > _MAX_CANDLES_PER_BUCKET:
                data = {k: v[-_MAX_CANDLES_PER_BUCKET:] for k, v in data.items()}
            self.candles.setdefault(symbol, {})[interval] = data
            # REST writes count as freshness — see ``seed_symbol`` for why.
            self._last_kline_update_ts.setdefault(symbol, {})[interval] = time.time()
            log.debug(
                "Refreshed %s %s: %d candles", symbol, interval, len(data["close"])
            )
            return True
        except Exception as exc:
            from src import fail_open
            fail_open.record("historical_data.refresh_timeframe", exc)
            return False

    async def _gap_fetch_and_merge(
        self, symbol: str, interval: str, gap: int, limit: int, market: str
    ) -> None:
        """Fetch gap candles and merge them into the existing cache."""
        new_data = await self.fetch_candles(symbol, interval, gap, market)
        if new_data:
            existing = self.candles.get(symbol, {}).get(interval, {})
            self.candles.setdefault(symbol, {})[interval] = self._merge_candles(existing, new_data, limit)
            # REST writes count as freshness — see seed_symbol for rationale.
            self._last_kline_update_ts.setdefault(symbol, {})[interval] = time.time()
            log.debug(
                "Gap-filled %s %s: fetched %d, total %d",
                symbol, interval, len(new_data["close"]),
                len(self.candles[symbol][interval]["close"]),
            )

    # ------------------------------------------------------------------
    # Disk-cache helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _estimate_gap_candles(saved_at_iso: str, interval: str) -> int:
        """Return the number of candles needed to cover the gap since *saved_at_iso*.

        A small buffer (+5) is added to account for partial candles and
        clock skew.  If the timestamp cannot be parsed, returns a large
        number so the caller falls back to a full fetch.
        """
        if not saved_at_iso:
            return _FULL_FETCH_SENTINEL
        try:
            saved_dt = datetime.fromisoformat(saved_at_iso)
            now_dt = datetime.now(timezone.utc)
            if saved_dt.tzinfo is None:
                saved_dt = saved_dt.replace(tzinfo=timezone.utc)
            elapsed = max(0.0, (now_dt - saved_dt).total_seconds())
            if elapsed > _MAX_GAP_FILL_SECONDS:
                return _FULL_FETCH_SENTINEL
            interval_secs = _INTERVAL_SECONDS.get(interval, 60)
            raw_gap = int(elapsed / interval_secs)
            if raw_gap == 0:
                return 0
            return raw_gap + _GAP_BUFFER_CANDLES
        except Exception:
            return _FULL_FETCH_SENTINEL

    @staticmethod
    def _first_new_index(
        existing: Dict[str, np.ndarray], new_data: Dict[str, np.ndarray]
    ) -> Optional[int]:
        """Index into *new_data* of the first bar newer than *existing*'s last.

        ``None`` means the question cannot be answered — one side carries no
        usable ``open_time`` — and the caller must then concatenate as before
        rather than guess.  Absence of knowledge is not permission to drop bars
        (``CLAUDE.md``); dropping the wrong ones loses history, which is strictly
        worse than the duplicates this exists to prevent.
        """
        old_t = existing.get("open_time")
        new_t = new_data.get("open_time")
        # None/len, never truthiness — numpy arrays raise on bool() (hard limit).
        if old_t is None or new_t is None:
            return None
        if len(old_t) != len(existing.get("close", ())) or len(old_t) == 0:
            return None
        if len(new_t) != len(new_data.get("close", ())) or len(new_t) == 0:
            return None
        try:
            old_arr = np.asarray(old_t, dtype=np.float64)
        except (TypeError, ValueError):
            return None
        finite_old = old_arr[np.isfinite(old_arr)]
        # An all-NaN bucket is the restored-legacy-history case (#842): there is
        # nothing to compare against, so no bar can be shown to be a duplicate.
        # Checked before nanmax rather than after, because nanmax on an all-NaN
        # slice warns — and a warning fired on an expected, handled condition is
        # how a real one stops standing out.
        if finite_old.size == 0:
            return None
        last_old = float(finite_old.max())
        arr = np.asarray(new_t, dtype=np.float64)
        if not np.all(np.isfinite(arr)):
            return None
        return int(np.searchsorted(arr, last_old, side="right"))

    def _merge_candles(
        self,
        existing: Dict[str, np.ndarray],
        new_data: Dict[str, np.ndarray],
        limit: int,
    ) -> Dict[str, np.ndarray]:
        """Append *new_data* arrays to *existing* and trim to *limit* candles.

        **Overlap is dropped, not concatenated** (2026-08-01).  This used to
        append blindly, and ``_estimate_gap_candles`` adds ``_GAP_BUFFER_CANDLES``
        deliberately — so every gap fill re-appended bars the bucket already held.
        Two consequences, and the second is the dangerous one:

        * the bucket carried duplicate bars, so any indicator averaging over a
          fixed bar count (SMA7/25/99, ATR, SAR) silently double-weighted the
          overlap window;
        * ``open_time`` came back **non-monotonic**, and
          ``dark_emission.slice_window`` locates its entry bar with
          ``np.searchsorted``, which is undefined — not merely imprecise — on an
          unsorted array.  A dark row could therefore walk from the wrong bar
          while stamping ``last_bar_ms`` and reading ``freshness: current``.

        Owner data 2026-08-01: 7 of the 9 open dark rows carried ~21 more array
        entries than there had been minutes since their entry, on a 1m bucket.

        The buffer itself is correct and stays — it protects against a genuine
        gap.  What was missing is that overlap is *expected*, so it must be
        removed on the way in rather than trusted to be absent.
        """
        start = self._first_new_index(existing, new_data)
        if start is None:
            # Undedupable: one side has no usable timestamps, so there is no way
            # to tell an overlapping bar from a new one. Concatenate as before —
            # and count it, because this is the degraded mode, not the healthy
            # one, and a silent degraded mode is how #842 stayed invisible.
            self.merge_undedupable += 1
        elif start > 0:
            # Every array in a bucket is built from the same Binance rows and is
            # index-aligned, so one offset trims them all. A key shorter than
            # the offset slices to empty, which the branches below already skip.
            self.merge_duplicate_bars_dropped += start
            new_data = {
                key: value[start:]
                for key, value in new_data.items()
                if value is not None
            }
        result: Dict[str, np.ndarray] = {}
        core_keys = ("open", "high", "low", "close", "volume")
        extended_keys = ("volume_usd", "taker_buy_vol_usd")
        for key in core_keys:
            combined = np.concatenate([existing.get(key, np.array([])), new_data.get(key, np.array([]))])
            result[key] = combined[-limit:] if len(combined) > limit else combined
        # ``open_time`` is index-aligned with the OHLC arrays, so it is merged
        # only when BOTH sides carry it.  Concatenating a present side onto a
        # missing one would yield a short array whose index i no longer names
        # bar i — a silently wrong timestamp is worse than none, because a
        # consumer can detect absence (and refuse) but not misalignment.
        if len(existing.get("open_time", ())) == len(existing.get("close", ())) and len(
            new_data.get("open_time", ())
        ) == len(new_data.get("close", ())):
            combined = np.concatenate(
                [existing.get("open_time", np.array([])), new_data.get("open_time", np.array([]))]
            )
            result["open_time"] = combined[-limit:] if len(combined) > limit else combined
        # Extended keys: only carry forward if the fresh fetch included them
        for key in extended_keys:
            if key in new_data and len(new_data[key]) > 0:
                combined = np.concatenate([existing.get(key, np.array([])), new_data[key]])
                result[key] = combined[-limit:] if len(combined) > limit else combined
        return result

    # ------------------------------------------------------------------
    # Gem scanner seeding — daily + weekly candles for macro analysis
    # ------------------------------------------------------------------

    async def seed_gem_symbol(self, symbol: str) -> None:
        """Seed daily and weekly candles for a single gem-scanner symbol.

        Fetches ~365 daily candles and ~52 weekly candles so the gem scanner
        has a full year of history for ATH detection, accumulation-base
        identification, and 90-day volume averaging.  Uses the spot client
        (daily/weekly data is available on spot endpoints for all USDT pairs).
        """
        self.candles.setdefault(symbol, {})

        async def _fetch_tf(tf: TimeframeSeed) -> None:
            data = await self.fetch_candles(symbol, tf.interval, tf.limit, "spot")
            if data:
                if len(data.get("close", [])) > _MAX_CANDLES_PER_BUCKET:
                    data = {k: v[-_MAX_CANDLES_PER_BUCKET:] for k, v in data.items()}
                self.candles[symbol][tf.interval] = data
                log.debug(
                    "Gem-seeded %s %s: %d candles", symbol, tf.interval, len(data["close"])
                )

        await asyncio.gather(*[_fetch_tf(tf) for tf in GEM_SEED_TIMEFRAMES])
        await asyncio.sleep(BATCH_REQUEST_DELAY)

    async def seed_gem_pairs(self, symbols: List[str]) -> None:
        """Seed daily/weekly historical data for all gem-scanner pairs.

        Up to :data:`_GAP_FILL_CONCURRENT_SYMBOLS` symbols are seeded in
        parallel.  This is called during boot after the standard
        :meth:`seed_all` so that the gem scanner has the ~1 year of daily
        candle history it needs for macro-reversal detection.

        Parameters
        ----------
        symbols:
            List of USDT symbol strings to seed (e.g. ``["BTCUSDT", ...]``).
        """
        if not symbols:
            return
        log.info("Starting gem scanner seed for %d pairs (daily + weekly) …", len(symbols))
        semaphore = asyncio.Semaphore(_GAP_FILL_CONCURRENT_SYMBOLS)

        async def _seed_one(sym: str) -> None:
            async with semaphore:
                await self.seed_gem_symbol(sym)

        await asyncio.gather(*[_seed_one(sym) for sym in symbols])
        log.info("Gem scanner seed complete.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_candles(self, symbol: str, interval: str) -> Optional[Dict[str, np.ndarray]]:
        return self.candles.get(symbol, {}).get(interval)

    def has_data(self) -> bool:
        """Return True if the store has any seeded candle data."""
        return bool(self.candles)

    def update_candle(self, symbol: str, interval: str, candle: Dict[str, float]) -> None:
        """Append a single candle (from WebSocket) to the store.

        ``candle["open_time"]`` (ms) is optional but strongly preferred — see
        ``fetch_candles``.  When the caller omits it, or when the bucket
        predates timestamp tracking, the slot is filled with NaN rather than a
        guess: a consumer that needs real times checks ``np.isfinite`` over the
        window it intends to use and refuses, which is recoverable, whereas an
        invented timestamp is silently wrong forever.
        """
        keys = ("open", "high", "low", "close", "volume", "open_time")
        bucket = self.candles.setdefault(symbol, {}).setdefault(
            interval,
            {k: np.empty(0, dtype=np.float64) for k in keys},
        )
        # A bucket seeded before this field existed (or by a legacy path) needs
        # its history padded so index i still names bar i.
        n_existing = len(bucket.get("close", ()))
        if len(bucket.get("open_time", ())) != n_existing:
            bucket["open_time"] = np.full(n_existing, np.nan, dtype=np.float64)
        for key in keys:
            arr = bucket[key]
            arr = np.append(arr, float(candle.get(key, np.nan if key == "open_time" else 0.0)))
            if len(arr) > _MAX_CANDLES_PER_BUCKET:
                arr = arr[-_MAX_CANDLES_PER_BUCKET:]
            bucket[key] = arr
        # Stamp the per-(symbol, interval) last-update wall clock so the
        # scanner's data-staleness gate can reject dispatch on frozen feeds.
        self._last_kline_update_ts.setdefault(symbol, {})[interval] = time.time()

    def last_kline_age_seconds(self, symbol: str, interval: str) -> Optional[float]:
        """Return seconds since the most-recent ``update_candle`` for the
        given (symbol, interval), or ``None`` if no kline has been recorded.

        Used by the scanner to gate signal dispatch against stale data.
        Returning ``None`` is treated as "stale" by callers — a pair with
        zero recorded klines is by definition not ready for trading.
        """
        last = self._last_kline_update_ts.get(symbol, {}).get(interval)
        if last is None:
            return None
        return max(0.0, time.time() - last)

    def append_tick(self, symbol: str, tick: Dict[str, Any]) -> None:
        self.ticks.setdefault(symbol, []).append(tick)
        # Keep only the last SEED_TICK_LIMIT ticks
        if len(self.ticks[symbol]) > SEED_TICK_LIMIT:
            self.ticks[symbol] = self.ticks[symbol][-SEED_TICK_LIMIT:]

    async def close(self) -> None:
        await self._client.close()
        await self._futures_client.close()
