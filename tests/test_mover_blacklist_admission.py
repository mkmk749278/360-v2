"""Mover promotion must honour the universe-hygiene blacklists.

#666 admits outside-top-75 movers straight off the ``!ticker@arr`` board —
which covers the WHOLE exchange, including tokenized stocks / commodities
that pair_manager's fetch paths exclude by design (Class-C misfits).  In the
2026-07-01..03 window SAMSUNG/HOOD/COIN/QCOM/PLTR-style equity perps were
promoted, scanned, and emitted to the paid channel through this hole.
``_ensure_mover_pair`` is the single admission funnel for both promotion
sources, so the gate lives there.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

from src.scanner import Scanner


# The mover-admission funnel is now fail-CLOSED on exchangeInfo metadata
# (2026-07-30): "we do not know what this instrument is" rejects.  Seed the
# REAL symbol_filters cache through its own test seams so these tests exercise
# the production collaborator rather than a shape we invented.
import pytest as _pytest  # noqa: E402

from src.execution import symbol_filters as _sf  # noqa: E402


@_pytest.fixture(autouse=True)
def _seed_exchange_metadata():
    _sf.reset_for_test()
    _known = (
        "BTCUSDT", "ETHUSDT", "GUAUSDT", "SKYAIUSDT", "AAAUSDT", "BBBUSDT",
        "CCCUSDT", "DDDUSDT", "EEEUSDT", "FFFUSDT", "PEPEUSDT", "WIFUSDT",
        "SAMSUNGUSDT", "HOODUSDT", "COINUSDT", "QCOMUSDT", "PLTRUSDT",
    )
    _sf._set_cache_for_test({
        s: _sf.SymbolFilters(symbol=s, step_size=0.001, tick_size=0.01,
                             min_qty=0.001, min_notional=5.0)
        for s in _known
    })
    _sf._set_tradfi_perps_for_test(
        {"SAMSUNGUSDT", "HOODUSDT", "COINUSDT", "QCOMUSDT", "PLTRUSDT"}
    )
    yield
    _sf.reset_for_test()


def _info(vol, vola):
    return SimpleNamespace(volume_24h_usd=vol, volatility_24h=vola)


def _make_scanner(pairs):
    pair_mgr = MagicMock()
    pair_mgr.pairs = pairs
    router = MagicMock(active_signals={})
    router.cleanup_expired.return_value = 0
    sq = MagicMock()
    sq.put = AsyncMock(return_value=True)
    sc = Scanner(
        pair_mgr=pair_mgr, data_store=MagicMock(), channels=[],
        smc_detector=MagicMock(), regime_detector=MagicMock(), predictive=MagicMock(),
        exchange_mgr=MagicMock(), spot_client=None, telemetry=MagicMock(),
        signal_queue=sq, router=router,
    )
    sc._seed_mover_pair = AsyncMock(return_value=True)
    return sc


class _FakeDetector:
    def __init__(self, movers, meta):
        self._movers = movers
        self._meta = meta

    def universe_movers(self, min_pct, min_vol):
        return [m for m in self._movers if abs(m[1]) >= min_pct and m[2] >= min_vol]

    def meta(self, sym):
        return self._meta.get(sym.upper())


def test_ensure_mover_pair_rejects_blacklisted_symbol():
    sc = _make_scanner({})
    # SAMSUNGUSDT is on the pair_manager _NON_CRYPTO_BLACKLIST (2026-07-03
    # sweep) — the admission funnel must refuse to synthesise it.
    info = sc._ensure_mover_pair("SAMSUNGUSDT", change_pct=-12.0, vol=50_000_000.0)
    assert info is None
    assert "SAMSUNGUSDT" not in sc.pair_mgr.pairs


def test_ensure_mover_pair_admits_normal_crypto():
    sc = _make_scanner({})
    info = sc._ensure_mover_pair("GUAUSDT", change_pct=-40.0, vol=18_000_000.0)
    assert info is not None
    assert "GUAUSDT" in sc.pair_mgr.pairs


async def test_promotion_source2_skips_tokenized_stock():
    sc = _make_scanner({"BTCUSDT": _info(5e9, 1.0)})
    sc.mover_ignition_pending = {}
    sc.mover_ignition_detector = _FakeDetector(
        movers=[
            ("HOODUSDT", -25.0, 60_000_000.0),   # Robinhood — blacklisted
            ("GUAUSDT", -40.0, 18_000_000.0),    # real crypto mover
        ],
        meta={
            "HOODUSDT": (-25.0, 60_000_000.0),
            "GUAUSDT": (-40.0, 18_000_000.0),
        },
    )
    await sc._update_movers_promotion(set())
    assert "HOODUSDT" not in sc.pair_mgr.pairs
    assert "GUAUSDT" in sc.pair_mgr.pairs


async def test_ignition_source_skips_tokenized_stock():
    sc = _make_scanner({"BTCUSDT": _info(5e9, 1.0)})
    sc.mover_ignition_pending = {"COINUSDT": "SHORT", "GUAUSDT": "SHORT"}
    sc.mover_ignition_detector = _FakeDetector(
        movers=[],
        meta={
            "COINUSDT": (-15.0, 90_000_000.0),   # Coinbase — blacklisted
            "GUAUSDT": (-40.0, 18_000_000.0),
        },
    )
    await sc._update_movers_promotion(set())
    assert "COINUSDT" not in sc.pair_mgr.pairs
    assert "GUAUSDT" in sc.pair_mgr.pairs


def test_scan_time_blacklist_mirrors_new_equities():
    # Defense in depth: the SCAN_SYMBOL_BLACKLIST default must carry the
    # same 2026-07-03 additions so an already-admitted pair is still
    # skipped by the scan loop after a config-only deploy.
    from config import SCAN_SYMBOL_BLACKLIST

    for sym in (
        "SAMSUNGUSDT", "HOODUSDT", "COINUSDT", "QCOMUSDT", "PLTRUSDT",
        "SNDKUSDT", "RKLBUSDT", "ASTSUSDT", "AXTIUSDT", "LITEUSDT",
        "ARMUSDT", "MRVLUSDT", "XPTUSDT",
    ):
        assert sym in SCAN_SYMBOL_BLACKLIST, sym
