"""Tests for ``src/pair_penalty.py`` — the doctrine-aligned rolling-window
per-pair soft penalty that replaces the closed Tier-4 hard blacklist.

What we pin:

* No-op behaviour when ``set_tracker`` hasn't been called.
* Pair with mean PnL >= 0 gets 0 penalty.
* Pair with mean PnL < 0 gets penalty = -mean_pnl * SCALE.
* Penalty capped at ``PAIR_PENALTY_CAP_PTS``.
* Records below ``PAIR_PENALTY_MIN_SAMPLE`` get no penalty.
* Records outside the rolling window are excluded from aggregation.
* Lazy refresh respects TTL — second call within TTL returns cached value
  even if records changed underneath.
* ``force_refresh`` bypasses TTL.
* Malformed records don't poison aggregation for healthy pairs.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List

import pytest

from src import pair_penalty


@dataclass
class _FakeRecord:
    """Subset of :class:`SignalRecord` fields ``pair_penalty`` reads."""
    symbol: str
    pnl_pct: float
    timestamp: float = field(default_factory=time.time)


class _FakeTracker:
    """Drop-in stand-in for :class:`PerformanceTracker`.  ``pair_penalty``
    only reads ``_records`` (a list of objects with .symbol / .pnl_pct /
    .timestamp attributes) — match that shape."""
    def __init__(self, records: List[_FakeRecord]):
        self._records = records


@pytest.fixture(autouse=True)
def _reset():
    """Wipe module state between each test so cache + tracker installs
    don't leak across cases."""
    pair_penalty._reset_state_for_tests()
    yield
    pair_penalty._reset_state_for_tests()


def test_no_tracker_installed_returns_zero():
    # set_tracker was never called → safe no-op fallback.
    assert pair_penalty.get("BTCUSDT") == 0.0
    assert pair_penalty.snapshot() == {}


def test_net_positive_pair_gets_zero_penalty():
    now = time.time()
    records = [
        _FakeRecord("BTCUSDT", pnl_pct=0.5, timestamp=now - 1000)
        for _ in range(10)
    ]
    pair_penalty.set_tracker(_FakeTracker(records))
    assert pair_penalty.get("BTCUSDT") == 0.0


def test_breakeven_pair_gets_zero_penalty():
    now = time.time()
    records = [
        _FakeRecord("BTCUSDT", pnl_pct=0.0, timestamp=now - 1000)
        for _ in range(10)
    ]
    pair_penalty.set_tracker(_FakeTracker(records))
    assert pair_penalty.get("BTCUSDT") == 0.0


def test_net_negative_pair_gets_proportional_penalty():
    # mean pnl = -0.5%; SCALE=23 → 11.5 pts (below the 20-pt cap).
    now = time.time()
    records = [
        _FakeRecord("BNBUSDT", pnl_pct=-0.5, timestamp=now - 1000)
        for _ in range(10)
    ]
    pair_penalty.set_tracker(_FakeTracker(records))
    penalty = pair_penalty.get("BNBUSDT")
    assert penalty == pytest.approx(11.5, abs=0.01)


def test_penalty_capped_at_max():
    # Catastrophic pair: mean pnl = -5.0% × 23 = 115 → should clamp to
    # PAIR_PENALTY_CAP_PTS (default 20.0).
    now = time.time()
    records = [
        _FakeRecord("BADUSDT", pnl_pct=-5.0, timestamp=now - 1000)
        for _ in range(10)
    ]
    pair_penalty.set_tracker(_FakeTracker(records))
    assert pair_penalty.get("BADUSDT") == 20.0


def test_below_min_sample_gets_zero_penalty():
    # Default min sample is 5 — a pair with 3 records (even all losing)
    # is below the noise floor and gets no penalty.
    now = time.time()
    records = [
        _FakeRecord("LOWVOLUSDT", pnl_pct=-2.0, timestamp=now - 1000)
        for _ in range(3)
    ]
    pair_penalty.set_tracker(_FakeTracker(records))
    assert pair_penalty.get("LOWVOLUSDT") == 0.0


def test_records_outside_window_excluded():
    # Default window is 28 days = 2_419_200 sec.  Mix recent losing
    # records with old positive records; only the recent ones should
    # drive the penalty calculation.
    now = time.time()
    recent = [
        _FakeRecord("FOOUSDT", pnl_pct=-1.0, timestamp=now - 1000)
        for _ in range(6)
    ]
    too_old = [
        _FakeRecord("FOOUSDT", pnl_pct=+5.0, timestamp=now - (40 * 86400))
        for _ in range(20)
    ]
    pair_penalty.set_tracker(_FakeTracker(recent + too_old))
    penalty = pair_penalty.get("FOOUSDT")
    # Only the 6 recent records aggregate: mean = -1.0 → -1.0 * 23 = 23
    # → capped to 20.
    assert penalty == 20.0


def test_only_records_outside_window_returns_zero():
    # All records are older than the window → pair fails the min_sample
    # check on the in-window subset → no penalty.
    now = time.time()
    old = [
        _FakeRecord("STALEUSDT", pnl_pct=-2.0, timestamp=now - (40 * 86400))
        for _ in range(20)
    ]
    pair_penalty.set_tracker(_FakeTracker(old))
    assert pair_penalty.get("STALEUSDT") == 0.0


def test_lazy_refresh_respects_ttl():
    # Install a tracker, get a snapshot, then mutate the underlying
    # records.  Within the TTL the cache should NOT reflect the
    # mutation.
    now = time.time()
    records = [
        _FakeRecord("ABCUSDT", pnl_pct=-1.0, timestamp=now - 1000)
        for _ in range(6)
    ]
    tracker = _FakeTracker(records)
    pair_penalty.set_tracker(tracker)

    first = pair_penalty.get("ABCUSDT", now=now)
    assert first > 0.0

    # Mutate the records — pair now looks great.
    tracker._records = [
        _FakeRecord("ABCUSDT", pnl_pct=+5.0, timestamp=now - 500)
        for _ in range(6)
    ]
    # Within TTL → still see the old (penalised) value.
    second = pair_penalty.get("ABCUSDT", now=now + 60)
    assert second == first

    # Past TTL → re-aggregates and the pair flips to no penalty.
    third = pair_penalty.get("ABCUSDT", now=now + 600)
    assert third == 0.0


def test_force_refresh_bypasses_ttl():
    now = time.time()
    tracker = _FakeTracker([
        _FakeRecord("XYZUSDT", pnl_pct=-1.0, timestamp=now - 100)
        for _ in range(6)
    ])
    pair_penalty.set_tracker(tracker)
    initial = pair_penalty.get("XYZUSDT", now=now)
    assert initial > 0.0

    # Drop all the bad records, force refresh.
    tracker._records = []
    snapshot = pair_penalty.force_refresh(now=now + 1)
    assert snapshot == {}
    assert pair_penalty.get("XYZUSDT", now=now + 1) == 0.0


def test_set_tracker_resets_cache():
    # Switching trackers (e.g. in a test harness) must drop the cache
    # — otherwise the second tracker would see stale state from the
    # first.
    now = time.time()
    bad_tracker = _FakeTracker([
        _FakeRecord("ABCUSDT", pnl_pct=-1.0, timestamp=now - 100)
        for _ in range(6)
    ])
    pair_penalty.set_tracker(bad_tracker)
    assert pair_penalty.get("ABCUSDT", now=now) > 0.0

    fresh_tracker = _FakeTracker([])
    pair_penalty.set_tracker(fresh_tracker)
    # Fresh tracker has no records → no penalty for any pair.
    assert pair_penalty.get("ABCUSDT", now=now) == 0.0


def test_malformed_records_dont_poison_healthy_pairs():
    # A record with a None symbol or a non-numeric pnl shouldn't
    # cascade-fail the whole aggregation.  The healthy pair next to
    # it must still get its correct penalty.
    now = time.time()
    healthy = [
        _FakeRecord("GOODUSDT", pnl_pct=-0.5, timestamp=now - 100)
        for _ in range(6)
    ]
    # Bad records — None symbol and one with NaN-ish pnl.
    class _BrokenRecord:
        symbol = None
        pnl_pct = -1.0
        timestamp = now - 100
    broken = [_BrokenRecord() for _ in range(3)]

    pair_penalty.set_tracker(_FakeTracker(healthy + broken))
    # GOODUSDT: mean -0.5 × 23 = 11.5.
    assert pair_penalty.get("GOODUSDT", now=now) == pytest.approx(11.5, abs=0.01)


def test_snapshot_returns_all_penalised_pairs():
    now = time.time()
    pair_penalty.set_tracker(_FakeTracker([
        # Two losing pairs.
        *[_FakeRecord("AUSDT", pnl_pct=-1.0, timestamp=now - 100) for _ in range(6)],
        *[_FakeRecord("BUSDT", pnl_pct=-0.3, timestamp=now - 100) for _ in range(6)],
        # One winning pair — excluded from snapshot.
        *[_FakeRecord("CUSDT", pnl_pct=+1.0, timestamp=now - 100) for _ in range(6)],
    ]))
    snap = pair_penalty.snapshot()
    assert set(snap.keys()) == {"AUSDT", "BUSDT"}
    assert snap["AUSDT"] == 20.0  # capped
    assert snap["BUSDT"] == pytest.approx(6.9, abs=0.01)  # -0.3 * 23
