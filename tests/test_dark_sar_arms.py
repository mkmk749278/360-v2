"""SAR exit arms on the dark feed — the second outcome per dark row.

Owner, 2026-07-31: *"observe this dark feed too with SAR exit mechanism along
with regular"*. Each dark row already resolves against its own SL/TP1 geometry;
these arms answer the other half — what a SAR handover would have done with the
same entry.

Two properties carry the design, and both are about **populations**:

* **The dark arms live in their own ledger.** ``sar_live_arms_v1.json`` is what
  ``/signals/sar-live`` presents as the evidence for adopting SAR on the money
  path, and every row in it reached a subscriber. A dark row reached nobody.
  Pooling them would inflate that evidence with signals that were never sent —
  and silently, since a consumer that has never heard of the dark lane cannot
  filter for it, while a consumer pointed at a file it does not open cannot see
  it at all.
* **Health is per lane.** The counters were module-global; a second sweep would
  have made a dark-lane stall page as though the delivered-signal arms had
  frozen, and a busy live lane hide a quiet dark failure. That is the same
  "two populations in one number" error the ledgers themselves are split to
  avoid.
"""
from __future__ import annotations

import pytest

from src import sar_live_shadow as sar


class _Sig:
    signal_id = "SIG-DARK-SAR-1"
    symbol = "AAAUSDT"
    setup_class = "MEAN_REVERT"
    entry = 100.0
    stop_loss = 97.0
    tp1 = 106.0

    class direction:
        value = "LONG"


@pytest.fixture()
def timestamped_store():
    """A real ``HistoricalDataStore`` driven through ``update_candle`` with real
    bar timestamps — the SAR arm decides *when* something happened, so a bucket
    with no ``open_time`` is refused by ``_series`` and no arm would open.

    Returns the store with ``now_ts`` set to just after its newest closed bar,
    so the anchor is current unless a test deliberately moves the clock.
    """
    from src.historical_data import HistoricalDataStore

    store = HistoricalDataStore.__new__(HistoricalDataStore)
    store.candles, store.ticks = {}, {}
    store._last_kline_update_ts = {}

    start_ms = 1_700_000_000_000.0
    n, step_ms = 120, 300_000.0            # 5m bars
    price = 100.0
    for i in range(n):
        store.update_candle("AAAUSDT", "5m", {
            "open": price, "high": price + 0.5, "low": price - 0.5,
            "close": price, "volume": 1.0,
            "open_time": start_ms + i * step_ms,
        })
    store.now_ts = (start_ms + (n - 1) * step_ms) / 1000.0 + 60.0
    return store


@pytest.fixture(autouse=True)
def _clean():
    sar.reset_ledger(sar.SarLiveLedger(path=""))
    sar.reset_dark_ledger(sar.SarLiveLedger(path=""))
    sar.reset_health()
    sar.reset_sar_cache()
    yield
    sar.reset_ledger(None)
    sar.reset_dark_ledger(None)
    sar.reset_health()


# --------------------------------------------------------------------------- #
# The ledgers are separate
# --------------------------------------------------------------------------- #


def test_the_dark_ledger_is_a_different_file():
    assert sar.DARK_PATH != sar.SarLiveLedger.DEFAULT_PATH
    assert "dark" in sar.DARK_PATH


def test_a_dark_arm_never_lands_in_the_live_ledger(timestamped_store):
    """The live ledger is the SAR adoption evidence and every row in it reached
    a subscriber. A dark row reached nobody."""
    dark = sar.get_dark_ledger()
    sar.observe_signal(
        _Sig(), timestamped_store, ledger=dark, lane=sar.LANE_DARK,
        timeframes=["5m"], now_ts=timestamped_store.now_ts,
    )
    assert sar.get_ledger().open_arms() == [], (
        "a dark arm in the live ledger inflates the population an adoption "
        "decision reads"
    )


def test_a_dark_arm_says_which_lane_it_belongs_to(timestamped_store):
    """Stamped on the row, not merely implied by which file it landed in — a
    row that cannot name its own population becomes unattributable the moment
    it is exported or read beside rows from the other lane."""
    dark = sar.get_dark_ledger()
    sar.observe_signal(
        _Sig(), timestamped_store, ledger=dark, lane=sar.LANE_DARK,
        timeframes=["5m"], now_ts=timestamped_store.now_ts,
    )
    arms = dark.open_arms()
    assert arms, "no arm opened — the fixture's series is not being read"
    assert arms[0]["lane"] == sar.LANE_DARK


def test_the_arm_carries_the_dark_rows_own_geometry(timestamped_store):
    """Entry, SL and TP1 come from the dark signal, so the two outcomes on the
    page divide by the same denominator and are comparable."""
    dark = sar.get_dark_ledger()
    sar.observe_signal(
        _Sig(), timestamped_store, ledger=dark, lane=sar.LANE_DARK,
        timeframes=["5m"], now_ts=timestamped_store.now_ts,
    )
    (arm,) = dark.open_arms()
    assert arm["entry"] == pytest.approx(100.0)
    assert arm["stop_loss"] == pytest.approx(97.0)
    assert arm["tp1"] == pytest.approx(106.0)
    assert arm["signal_id"] == "SIG-DARK-SAR-1"


# --------------------------------------------------------------------------- #
# Health is per lane
# --------------------------------------------------------------------------- #


def test_a_dark_stall_does_not_show_up_in_the_live_lanes_health():
    sar.record_step("AAAUSDT", False, f"{sar.STALL_NO_SERIES}:5m", lane=sar.LANE_DARK)
    sar.roll_health_cycle()
    assert sar.step_health(sar.LANE_DARK)["no_series"] == 1
    assert sar.step_health(sar.LANE_LIVE)["no_series"] == 0, (
        "a dark-lane stall paging as a live-arm failure sends someone looking "
        "at the trades that carry real exits"
    )


def test_a_live_stall_does_not_show_up_in_the_dark_lanes_health():
    sar.record_step("BBBUSDT", False, f"{sar.STALL_NO_SERIES}:5m")
    sar.roll_health_cycle()
    assert sar.step_health(sar.LANE_LIVE)["no_series"] == 1
    assert sar.step_health(sar.LANE_DARK)["no_series"] == 0


def test_a_lane_can_be_rolled_without_rolling_the_other():
    """The two lanes are swept on different periods — the monitor loop and the
    dark resolver — so one roll covering both would report a window neither
    lane actually ran."""
    sar.record_step("AAAUSDT", True, lane=sar.LANE_DARK)
    sar.record_step("BBBUSDT", True, lane=sar.LANE_LIVE)
    sar.roll_health_cycle(sar.LANE_DARK)
    assert sar.step_health(sar.LANE_DARK)["stepped"] == 1
    assert sar.step_health(sar.LANE_LIVE)["stepped"] == 0  # not rolled yet
    sar.roll_health_cycle(sar.LANE_LIVE)
    assert sar.step_health(sar.LANE_LIVE)["stepped"] == 1


def test_refusals_are_counted_per_lane_too():
    sar.record_open_refusal(
        "AAAUSDT", "15m", sar.OPEN_REFUSED_STALE_ANCHOR, 40.0, lane=sar.LANE_DARK,
    )
    sar.roll_health_cycle()
    assert sar.step_health(sar.LANE_DARK)["refused_open"] == 1
    assert sar.step_health(sar.LANE_LIVE)["refused_open"] == 0


def test_step_health_names_the_lane_it_describes():
    assert sar.step_health(sar.LANE_DARK)["lane"] == sar.LANE_DARK
    assert sar.step_health()["lane"] == sar.LANE_LIVE


# --------------------------------------------------------------------------- #
# The anchor guard still applies — a dark arm can be born a replay too
# --------------------------------------------------------------------------- #


def test_a_stale_anchor_is_refused_in_the_dark_lane_as_well(timestamped_store):
    """#836 was found on the live arms; the guard belongs to `observe_signal`,
    so it covers these — but the refusal has to land in THIS lane's counter or
    the dark page would report someone else's."""
    dark = sar.get_dark_ledger()
    # Ask for the arm 10 hours after the fixture's newest bar closed.
    sar.observe_signal(
        _Sig(), timestamped_store, ledger=dark, lane=sar.LANE_DARK,
        timeframes=["5m"], now_ts=timestamped_store.now_ts + 36_000.0,
    )
    assert dark.open_arms() == []
    sar.roll_health_cycle()
    assert sar.step_health(sar.LANE_DARK)["refused_open"] == 1
    assert sar.step_health(sar.LANE_LIVE)["refused_open"] == 0
