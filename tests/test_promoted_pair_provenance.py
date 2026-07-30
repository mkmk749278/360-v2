"""Promoted-pair admission gate, hold, and provenance stamp (2026-07-30).

Companion to ``test_scan_universe_admission.py``, on the scanner side of the
seam.  All three behaviours here were absent from the engine that put SMCI /
SOXS / IBM / NOK / LRCX signals into the paid book while recording nothing
about how any of those pairs got into the scan set.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import symbol_filters as _sf
from src.pair_manager import PairInfo, PairManager, PairTier
from src.scanner import Scanner


@pytest.fixture(autouse=True)
def _seed_exchange_metadata():
    """Drive the real symbol_filters cache, not a hand-written stand-in."""
    _sf.reset_for_test()
    crypto = ("BTCUSDT", "GUAUSDT", "SKYAIUSDT")
    tradfi = ("SMCIUSDT", "SOXSUSDT", "IBMUSDT", "NOKUSDT", "LRCXUSDT")
    _sf._set_cache_for_test({
        s: _sf.SymbolFilters(symbol=s, step_size=0.001, tick_size=0.01,
                             min_qty=0.001, min_notional=5.0)
        for s in (*crypto, *tradfi)
    })
    _sf._set_tradfi_perps_for_test(set(tradfi))
    yield
    _sf.reset_for_test()


def _make_scanner(pair_mgr=None):
    pair_mgr = pair_mgr if pair_mgr is not None else MagicMock(pairs={})
    router = MagicMock(active_signals={})
    router.cleanup_expired.return_value = 0
    sq = MagicMock()
    sq.put = AsyncMock(return_value=True)
    sc = Scanner(
        pair_mgr=pair_mgr, data_store=MagicMock(), channels=[],
        smc_detector=MagicMock(), regime_detector=MagicMock(),
        predictive=MagicMock(), exchange_mgr=MagicMock(), spot_client=None,
        telemetry=MagicMock(), signal_queue=sq, router=router,
    )
    sc._seed_mover_pair = AsyncMock(return_value=True)
    return sc


def _real_pm() -> PairManager:
    pm = PairManager()
    pm._spot_client = MagicMock()
    pm._futures_client = MagicMock()
    return pm


# ---------------------------------------------------------------------------
# The leak
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "symbol", ["SMCIUSDT", "SOXSUSDT", "IBMUSDT", "NOKUSDT", "LRCXUSDT"]
)
def test_mover_admission_refuses_every_ticker_that_reached_the_live_book(symbol):
    """The five stock perps found in signals_last100 must not be admissible.

    Note these are ALSO on the static floor now — so this test is asserted
    against the structural gate specifically, by removing the name from the
    blacklist for the duration.  Otherwise it would pass on the floor alone
    and tell us nothing about whether the next unlisted stock perp is stopped.
    """
    import src.scanner as _scanner_mod

    sc = _make_scanner()
    original = _scanner_mod._MOVER_UNIVERSE_BLACKLIST
    _scanner_mod._MOVER_UNIVERSE_BLACKLIST = frozenset(
        s for s in original if s != symbol
    )
    try:
        info = sc._ensure_mover_pair(symbol, change_pct=-22.0, vol=30_000_000.0)
    finally:
        _scanner_mod._MOVER_UNIVERSE_BLACKLIST = original
    assert info is None, f"{symbol} admitted by the structural gate"
    assert symbol not in sc.pair_mgr.pairs
    assert sc._suppression_counters["mover_admission_rejected:tradfi_perp"] == 1


def test_unknown_instrument_is_refused_and_counted():
    """Fail-closed: a symbol exchangeInfo has never heard of does not enter."""
    sc = _make_scanner()
    assert sc._ensure_mover_pair("MYSTERYUSDT", change_pct=-30.0, vol=2e7) is None
    assert sc._suppression_counters[
        "mover_admission_rejected:unknown_to_exchange_info"
    ] == 1


def test_metadata_outage_refuses_rather_than_admitting_the_whole_board():
    sc = _make_scanner()
    _sf.reset_for_test()
    assert sc._ensure_mover_pair("GUAUSDT", change_pct=-40.0, vol=2e7) is None
    assert sc._suppression_counters[
        "mover_admission_rejected:metadata_unavailable"
    ] == 1


def test_genuine_crypto_mover_still_admitted():
    sc = _make_scanner()
    info = sc._ensure_mover_pair("GUAUSDT", change_pct=-40.0, vol=18_000_000.0)
    assert info is not None
    assert info.tier == PairTier.TIER3


# ---------------------------------------------------------------------------
# The hold
# ---------------------------------------------------------------------------


async def test_admitted_mover_survives_a_universe_refresh():
    """End-to-end: admit a mover, rotate the top-N, mover is still scannable.

    This is the defect that cost a mean ~50% of every promotion window.  The
    two halves are wired through the REAL PairManager, because the bug lived
    exactly in the seam between them.
    """
    pm = _real_pm()
    pm.pairs["BTCUSDT"] = PairInfo(symbol="BTCUSDT", market="futures",
                                   volume_24h_usd=9e9, tier=PairTier.TIER1)
    sc = _make_scanner(pm)

    assert sc._ensure_mover_pair("GUAUSDT", change_pct=-40.0, vol=2e7) is not None
    assert "GUAUSDT" in pm.pairs

    async def _fetch(limit=None):
        return [PairInfo(symbol="BTCUSDT", market="futures", volume_24h_usd=9e9)]

    pm.fetch_top_futures_pairs = _fetch
    await pm.refresh_top50_futures(count=1, force=True)

    assert "GUAUSDT" in pm.pairs, "the 6h refresh evicted a mover mid-promotion"


async def test_expired_promotion_releases_the_hold():
    """A hold must not outlive the promotion that took it, or the universe
    grows without bound and the prune stops meaning anything."""
    pm = _real_pm()
    sc = _make_scanner(pm)
    sc._ensure_mover_pair("GUAUSDT", change_pct=-40.0, vol=2e7)
    assert "GUAUSDT" in pm.held_symbols()

    # Expire it: TTL in the past.
    sc._mover_promoted_pairs["GUAUSDT"] = 0.0
    sc.mover_ignition_pending = {}
    sc.mover_ignition_detector = None
    await sc._update_movers_promotion(set())

    assert "GUAUSDT" not in pm.held_symbols()
    assert "GUAUSDT" not in pm.pairs


# ---------------------------------------------------------------------------
# The provenance stamp
# ---------------------------------------------------------------------------


class TestPairAdmissionStamp:
    def test_core_pair(self):
        sc = _make_scanner()
        assert sc._pair_admission_for("BTCUSDT") == "CORE"

    def test_ignition_promoted_pair_names_its_source(self):
        sc = _make_scanner()
        sc._mover_promoted_pairs["GUAUSDT"] = 1e9
        sc._mover_promotion_source["GUAUSDT"] = "MOVER_IGNITION"
        assert sc._pair_admission_for("GUAUSDT") == "MOVER_IGNITION"

    def test_top24h_promoted_pair_names_its_source(self):
        sc = _make_scanner()
        sc._mover_promoted_pairs["GUAUSDT"] = 1e9
        sc._mover_promotion_source["GUAUSDT"] = "MOVER_TOP24H"
        assert sc._pair_admission_for("GUAUSDT") == "MOVER_TOP24H"

    def test_surge_promoted_pair(self):
        sc = _make_scanner()
        sc._promoted_pairs["GUAUSDT"] = 3
        assert sc._pair_admission_for("GUAUSDT") == "SURGE"

    async def test_source_is_recorded_at_promotion_time(self):
        """Not derived later — the promotion is gone before the signal closes."""
        pm = _real_pm()
        sc = _make_scanner(pm)
        sc.mover_ignition_pending = {"GUAUSDT": "short"}
        sc.mover_ignition_detector = SimpleNamespace(
            universe_movers=lambda a, b: [],
            meta=lambda s: {"GUAUSDT": (-40.0, 2e7)}.get(s.upper()),
        )
        await sc._update_movers_promotion(set())
        assert sc._pair_admission_for("GUAUSDT") == "MOVER_IGNITION"


class TestProvenanceReachesTheRecord:
    """A cross-repo field name is a contract — pin it on the producing side.

    ops reads ``pair_admission`` off the closed-signal record.  ``entry_regime``
    was read by ops for months while the engine never wrote it (#817); this
    test is what makes a rename here fail loudly instead of quietly emptying
    an ops page.
    """

    def test_signal_carries_the_field(self):
        from src.channels.base import Signal

        assert hasattr(Signal(channel="c", symbol="S", direction=None, entry=1.0,
                              stop_loss=0.9, tp1=1.1, tp2=1.2), "pair_admission")

    def test_signal_record_carries_the_field(self):
        from src.performance_tracker import SignalRecord

        rec = SignalRecord(signal_id="x", channel="c", symbol="S", direction="LONG",
                           entry=1.0, hit_tp=0, hit_sl=False, pnl_pct=0.0,
                           confidence=70.0, pair_admission="MOVER_TOP24H")
        assert rec.pair_admission == "MOVER_TOP24H"

    def test_record_outcome_persists_it(self, tmp_path):
        from src.performance_tracker import PerformanceTracker

        pt = PerformanceTracker(storage_path=str(tmp_path / "perf.json"))
        pt.record_outcome(
            signal_id="s1", channel="360_SCALP", symbol="GUAUSDT",
            direction="LONG", entry=1.0, hit_tp=0, hit_sl=True, pnl_pct=-1.0,
            confidence=70.0, pair_admission="MOVER_IGNITION",
        )
        assert pt._records[-1].pair_admission == "MOVER_IGNITION"

    def test_api_schema_exposes_it(self):
        from src.api.schemas import SignalDetail

        assert "pair_admission" in SignalDetail.model_fields

    def test_default_is_empty_not_a_guess(self):
        """Pre-fix records cannot be backfilled — the promotion is long gone."""
        from src.performance_tracker import SignalRecord

        rec = SignalRecord(signal_id="x", channel="c", symbol="S", direction="LONG",
                           entry=1.0, hit_tp=0, hit_sl=False, pnl_pct=0.0,
                           confidence=70.0)
        assert rec.pair_admission == ""
