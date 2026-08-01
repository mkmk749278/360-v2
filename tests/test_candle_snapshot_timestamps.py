"""The disk snapshot has to carry bar timestamps across a restart.

Owner-caught 2026-07-31, from a printed ops page: every open row on the dark
feed read ``no candles``, on core pairs whose candles were plainly arriving.

The chain, and every link in it was individually reasonable:

1. ``_save_snapshot_sync`` wrote five arrays — open/high/low/close/volume — and
   ``load_snapshot`` read back the same five.  ``open_time`` had been added to
   the store without being added here, so it did not survive a restart.
2. ``_merge_candles`` then **correctly** refused to merge the gap-fetch's
   timestamps onto a bucket that had none: concatenating a present side onto a
   missing one yields a short array whose index *i* no longer names bar *i*, and
   a silently misaligned timestamp is worse than an absent one.
3. So after every restart the entire store was undatable, and any consumer that
   locates a bar by wall clock — the dark resolver, the SAR 15m walker — could
   place nothing.

The lesson is #817's, one layer down: **a field one writer populates and one
serializer drops is invisible at both ends.** The store had timestamps, the
loader had a bucket, neither was empty, and nothing anywhere was in an error
state. These tests pin the round trip so the next field added to a candle
bucket cannot silently fail to survive a restart.
"""
from __future__ import annotations

import numpy as np
import pytest

from src import historical_data as hd


@pytest.fixture()
def store(tmp_path, monkeypatch):
    """A real store writing into a temp cache dir — no mocks: the bug lived in
    the serializer, and a mocked serializer would have asserted the mistake back
    at us (#798)."""
    monkeypatch.setattr(hd, "CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(hd, "_TICKS_DIR", tmp_path / "cache" / "ticks")
    monkeypatch.setattr(hd, "_META_FILE", tmp_path / "cache" / "metadata.json")
    return hd.HistoricalDataStore.__new__(hd.HistoricalDataStore)


def _bucket(store, symbol="BCHUSDT", interval="1m", n=5, start_ms=1_700_000_000_000.0):
    store.candles = {symbol: {interval: {
        "open": np.full(n, 100.0),
        "high": np.full(n, 101.0),
        "low": np.full(n, 99.0),
        "close": np.full(n, 100.5),
        "volume": np.full(n, 10.0),
        "open_time": np.arange(n, dtype=np.float64) * 60_000.0 + start_ms,
    }}}
    store.ticks = {}
    store._last_kline_update_ts = {}
    return store.candles[symbol][interval]


def test_bar_timestamps_survive_a_restart(store):
    original = _bucket(store)["open_time"].copy()
    store._save_snapshot_sync()

    reloaded = hd.HistoricalDataStore.__new__(hd.HistoricalDataStore)
    reloaded.candles, reloaded.ticks, reloaded._last_kline_update_ts = {}, {}, {}
    assert reloaded.load_snapshot() is True

    bucket = reloaded.candles["BCHUSDT"]["1m"]
    assert "open_time" in bucket, "the whole store is undatable without this"
    np.testing.assert_array_equal(bucket["open_time"], original)


def test_a_legacy_cache_without_timestamps_loads_aligned_rather_than_absent(store):
    """An npz written by the old code has no ``open_time``. Loading it as a
    NaN column — rather than leaving the key off — keeps index *i* naming bar
    *i* and lets the merge carry the fresh side's timestamps through. Absence
    does not just lose the old times, it discards the new ones too."""
    _bucket(store, n=4)
    store._save_snapshot_sync()

    # Rewrite the npz the way the pre-fix serializer did: five keys, no times.
    path = hd.CACHE_DIR / "BCHUSDT_1m.npz"
    with np.load(path, allow_pickle=False) as data:
        legacy = {k: data[k] for k in ("open", "high", "low", "close", "volume")}
    np.savez_compressed(path, **legacy)

    reloaded = hd.HistoricalDataStore.__new__(hd.HistoricalDataStore)
    reloaded.candles, reloaded.ticks, reloaded._last_kline_update_ts = {}, {}, {}
    reloaded.load_snapshot()

    bucket = reloaded.candles["BCHUSDT"]["1m"]
    assert len(bucket["open_time"]) == len(bucket["close"])
    assert np.all(np.isnan(bucket["open_time"])), "unknown, not guessed"


def test_a_gap_fetch_carries_its_timestamps_onto_a_legacy_bucket(store):
    """The merge drops timestamps unless both sides are index-aligned. With the
    loader padding, a restored bucket qualifies — so the bars fetched after the
    restart keep their real times and only the restored history is unknown.
    Before the fix this produced a bucket with no timestamps at all, and every
    dark row on the ops page reported `no candles`."""
    n_old = 4
    existing = {
        "open": np.full(n_old, 100.0), "high": np.full(n_old, 101.0),
        "low": np.full(n_old, 99.0), "close": np.full(n_old, 100.5),
        "volume": np.full(n_old, 10.0),
        "open_time": np.full(n_old, np.nan),      # restored legacy history
    }
    fresh_times = np.array([1_700_000_240_000.0, 1_700_000_300_000.0])
    new_data = {
        "open": np.full(2, 100.0), "high": np.full(2, 101.0),
        "low": np.full(2, 99.0), "close": np.full(2, 100.5),
        "volume": np.full(2, 10.0), "open_time": fresh_times,
    }
    # Instance method since 2026-08-01: the merge counts what it drops, and a
    # counter needs somewhere to live.
    merged = hd.HistoricalDataStore()._merge_candles(existing, new_data, 100)

    assert len(merged["open_time"]) == len(merged["close"]) == 6
    assert np.all(np.isnan(merged["open_time"][:4]))
    np.testing.assert_array_equal(merged["open_time"][4:], fresh_times)


def test_the_dark_resolver_can_place_a_stamp_in_the_merged_bucket():
    """The end-to-end shape the incident produced: a NaN prefix from the restore
    and a finite tail from the gap fetch. A stamp inside the tail is located
    exactly; one inside the prefix walks undated instead of blanking the row."""
    from src import dark_emission as de

    times = np.concatenate([np.full(4, np.nan),
                            np.array([1_700_000_240_000.0, 1_700_000_300_000.0])])
    candles = {
        "high": np.full(6, 101.0), "low": np.full(6, 99.0),
        "close": np.full(6, 100.5), "open_time": times,
    }
    dated = de.slice_window(candles, 1_700_000_250.0)
    assert dated["open_time"][0] == pytest.approx(1_700_000_240_000.0)

    undated = de.slice_window(candles, 1_700_000_100.0)
    assert "open_time" not in undated
    assert undated["undated_reason"] == "stamp_before_timestamps"


# --------------------------------------------------------------------------- #
# Overlap on merge (2026-08-01)
# --------------------------------------------------------------------------- #


class TestMergeDropsOverlapRatherThanAppendingIt:
    """``_merge_candles`` used to concatenate blindly, and the gap fetch
    over-fetches **on purpose**.

    ``_estimate_gap_candles`` adds ``_GAP_BUFFER_CANDLES`` to cover partial bars
    and clock skew, which is correct — a gap fill that comes up short leaves a
    hole. What was missing is that the overlap is therefore *expected*, so it has
    to be removed on the way in. Appending it had two consequences:

    * duplicate bars in the bucket, so any indicator averaging a fixed bar count
      (SMA7/25/99, ATR, SAR) double-weighted the overlap window;
    * a **non-monotonic** ``open_time``, and ``dark_emission.slice_window``
      locates its entry bar with ``np.searchsorted``, which is undefined — not
      imprecise — on an unsorted array. The walk that follows is structurally
      valid, stamps ``last_bar_ms`` and reads ``freshness: current``.

    Owner data 2026-08-01: 7 of the 9 open dark rows carried ~21 more array
    entries than there had been minutes since their entry, on a 1m bucket.
    """

    @staticmethod
    def _bucket(start_ms: int, n: int, price: float = 100.0):
        t = np.array([start_ms + i * 60_000 for i in range(n)], dtype=float)
        return {
            "open": np.full(n, price),
            "high": np.full(n, price + 1.0),
            "low": np.full(n, price - 1.0),
            "close": np.full(n, price),
            "volume": np.full(n, 10.0),
            "open_time": t,
        }

    def test_an_overlapping_gap_fetch_does_not_duplicate_bars(self):
        store = hd.HistoricalDataStore()
        existing = self._bucket(1_000_000_000_000, 30)
        # The gap fetch re-pulls the last 5 bars plus 5 genuinely new ones —
        # exactly the shape `_GAP_BUFFER_CANDLES` produces.
        incoming = self._bucket(1_000_000_000_000 + 25 * 60_000, 10, price=101.0)

        merged = store._merge_candles(existing, incoming, 500)

        assert len(merged["close"]) == 35, "5 overlapping bars should be dropped"
        assert store.merge_duplicate_bars_dropped == 5
        assert store.merge_undedupable == 0

    def test_the_merged_timestamps_are_strictly_increasing(self):
        """The property `searchsorted` needs and never had."""
        store = hd.HistoricalDataStore()
        existing = self._bucket(1_000_000_000_000, 30)
        incoming = self._bucket(1_000_000_000_000 + 25 * 60_000, 10, price=101.0)

        merged = store._merge_candles(existing, incoming, 500)

        t = merged["open_time"]
        assert np.all(np.diff(t) > 0), (
            "duplicate bars make open_time non-monotonic, which makes every "
            "searchsorted over it undefined"
        )

    def test_new_bars_survive_and_keep_their_values(self):
        """Dropping the overlap must not cost the bars that are genuinely new."""
        store = hd.HistoricalDataStore()
        existing = self._bucket(1_000_000_000_000, 30, price=100.0)
        incoming = self._bucket(1_000_000_000_000 + 25 * 60_000, 10, price=101.0)

        merged = store._merge_candles(existing, incoming, 500)

        assert merged["close"][-1] == 101.0
        assert merged["close"][29] == 100.0
        assert merged["open_time"][-1] == incoming["open_time"][-1]

    def test_a_fully_stale_fetch_adds_nothing(self):
        """Every incoming bar already held: the correct merge is a no-op, not a
        doubling of the tail."""
        store = hd.HistoricalDataStore()
        existing = self._bucket(1_000_000_000_000, 30)
        incoming = self._bucket(1_000_000_000_000, 10)

        merged = store._merge_candles(existing, incoming, 500)

        assert len(merged["close"]) == 30
        assert np.all(np.diff(merged["open_time"]) > 0)

    def test_a_disjoint_fetch_is_appended_whole(self):
        store = hd.HistoricalDataStore()
        existing = self._bucket(1_000_000_000_000, 30)
        incoming = self._bucket(1_000_000_000_000 + 100 * 60_000, 10)

        merged = store._merge_candles(existing, incoming, 500)

        assert len(merged["close"]) == 40
        assert store.merge_duplicate_bars_dropped == 0

    def test_an_undedupable_merge_is_counted_not_guessed(self):
        """One side without timestamps cannot be deduped, and dropping bars on a
        guess loses history — strictly worse than the duplicates it prevents.

        Absence of knowledge is not permission (``CLAUDE.md``): concatenate as
        before, and *count* it, because a silent degraded mode is exactly how
        the dropped ``open_time`` in #842 stayed invisible.
        """
        store = hd.HistoricalDataStore()
        existing = self._bucket(1_000_000_000_000, 30)
        del existing["open_time"]
        incoming = self._bucket(1_000_000_000_000 + 25 * 60_000, 10)

        merged = store._merge_candles(existing, incoming, 500)

        assert len(merged["close"]) == 40, "no dedupe possible, so nothing dropped"
        assert store.merge_undedupable == 1
        assert store.merge_duplicate_bars_dropped == 0


class TestSliceWindowRefusesAnUnsortedSeries:
    """``searchsorted`` on an unsorted array returns an index with no
    relationship to the bar asked for, and every downstream stamp then describes
    the wrong bar while looking healthy.

    The source is fixed above; this guard stays because it belongs where the
    assumption is made, and a store is not the only thing that can hand us a bad
    series.
    """

    @staticmethod
    def _series(times):
        n = len(times)
        return {
            "high": [101.0] * n,
            "low": [99.0] * n,
            "close": [100.0] * n,
            "open_time": [float(t) for t in times],
        }

    def test_a_duplicated_tail_is_walked_but_never_claims_to_be_dated(self):
        from src import dark_emission as de

        base = 1_000_000_000_000
        # 10 clean bars, then 3 that repeat earlier timestamps — the exact shape
        # a blind merge of an overlapping gap fetch produced.
        times = [base + i * 60_000 for i in range(10)]
        times += [base + i * 60_000 for i in range(7, 10)]

        out = de.slice_window(self._series(times), (base + 5 * 60_000) / 1000.0)

        assert out is not None, "refusing the measurement outright is the #842 mistake"
        assert out.get("undated_reason") == "timestamps_unsorted"
        assert "open_time" not in out, (
            "an undated window must not carry timestamps a reader would trust"
        )

    def test_a_clean_series_still_dates_its_window(self):
        from src import dark_emission as de

        base = 1_000_000_000_000
        times = [base + i * 60_000 for i in range(10)]

        out = de.slice_window(self._series(times), (base + 5 * 60_000) / 1000.0)

        assert out is not None
        assert out.get("undated_reason") is None
        assert out["open_time"][0] == float(base + 5 * 60_000)
