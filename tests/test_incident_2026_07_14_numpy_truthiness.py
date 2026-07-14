"""2026-07-14 incident regressions — the numpy-truthiness fail-open class.

``HistoricalDataStore.get_candles`` returns ``Dict[str, np.ndarray]``, and
``arr or []`` / ``if not arr`` on a multi-element numpy array raises
``ValueError``.  Three call sites read the data store directly (bypassing the
scanner's ``_normalize_candle_dict`` list boundary) and swallowed that raise
in a fail-open ``except`` — so each feature silently did nothing in
production while every list-fixture test stayed green:

1. ``Scanner._stamp_geometry_ab`` — the stop-geometry A/B (#722) stamped
   ZERO pairs in its first ~25h live (Strategy Lab + truth report both
   empty while the suppression audit classified hundreds of candidates).
2. ``CryptoSignalEngine._build_global_market_context`` — the published
   global context's ATR-percentile / HTF-prior inputs degraded to None
   every cycle since #721.
3. ``check_btc_direction_gate`` (OWNER_BRIEF §2.1 soft penalty) — never
   fired: truth-report BTC_Dir column all-zero across ~2.8k scored samples
   while the structurally identical list-fed Sym_Dir gate did fire.

Every test here drives the REAL production array shape (a
``HistoricalDataStore`` seeded via ``update_candle``, or explicit numpy
arrays) — the exact input class the original fixtures missed.

The §2.1 penalty's *application* is a live-scoring change, so it ships
dark (owner decision 2026-07-14): ``btc_dir_penalty_apply`` defaults OFF
and the registry default is pinned here.
"""
from __future__ import annotations

import numpy as np
import pytest

from src import geometry_ab as gab
from src.btc_direction import check_btc_direction_gate
from src.historical_data import HistoricalDataStore
from src.suppression_audit import SuppressedCandidateStore


def _seeded_store(
    symbol: str = "ETHUSDT",
    intervals: tuple = ("15m",),
    n: int = 120,
    close: float = 100.0,
    spread: float = 0.5,
) -> HistoricalDataStore:
    """A real data store filled through ``update_candle`` → numpy buckets,
    exactly the shape the engine hands to every consumer."""
    store = HistoricalDataStore()
    for interval in intervals:
        for _ in range(n):
            store.update_candle(
                symbol,
                interval,
                {
                    "open": close,
                    "high": close + spread,
                    "low": close - spread,
                    "close": close,
                    "volume": 1.0,
                },
            )
    return store


@pytest.fixture()
def fresh_geometry_store(monkeypatch):
    store = SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(gab, "_geometry_store", store)
    monkeypatch.setattr(gab, "_last_pair_stamp", {})
    return store


class TestGeometryAbStampsOnNumpy:
    def test_scanner_hook_stamps_pair_from_real_data_store(
        self, fresh_geometry_store, monkeypatch
    ):
        from types import SimpleNamespace

        from src import runtime_tunables
        from src.scanner import Scanner
        from src.smc import Direction

        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        scanner = SimpleNamespace(data_store=_seeded_store())
        sig = SimpleNamespace(
            symbol="ETHUSDT",
            channel="360_SCALP",
            setup_class="SR_FLIP_RETEST",
            direction=Direction.LONG,
            entry=100.0,
            stop_loss=99.0,
            tp1=101.5,
            confidence=70.0,
            mc_context_key="OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL",
            entry_regime="TRENDING_UP",
            valid_for_minutes=45.0,
            geo_atr_stop=0.0,
        )
        Scanner._stamp_geometry_ab(scanner, sig)
        recs = fresh_geometry_store.records()
        assert len(recs) == 2, (
            "geometry pair must stamp from numpy data-store candles — "
            "zero records is the 2026-07-14 production failure"
        )
        # Flat tape spread=0.5 → ATR=1.0, ×1.5 mult beats pool 0.5+buffer.
        assert sig.geo_atr_stop == pytest.approx(98.5)

    def test_stamp_geometry_pair_accepts_numpy_arrays(self, fresh_geometry_store):
        highs = np.full(40, 100.5)
        lows = np.full(40, 99.5)
        closes = np.full(40, 100.0)
        alt = gab.stamp_geometry_pair(
            symbol="BTCUSDT",
            channel="360_SCALP",
            setup_class="SR_FLIP_RETEST",
            side="LONG",
            entry=100.0,
            stop_loss=99.0,
            tp1=101.5,
            highs=highs,
            lows=lows,
            closes=closes,
        )
        assert alt == pytest.approx(98.5)
        assert len(fresh_geometry_store.records()) == 2


class TestGlobalMarketContextOnNumpy:
    def test_atr_percentile_and_htf_prior_reach_the_builder(self, monkeypatch):
        from types import SimpleNamespace

        from src import market_context as mc_mod
        from src.main import CryptoSignalEngine

        captured: dict = {}
        real_build = mc_mod.build_market_context

        def _capture(**kwargs):
            captured.update(kwargs)
            return real_build(**kwargs)

        monkeypatch.setattr(mc_mod, "build_market_context", _capture)
        stub = SimpleNamespace(
            data_store=_seeded_store("BTCUSDT", intervals=("15m", "1h"))
        )
        ctx = CryptoSignalEngine._build_global_market_context(stub)
        assert ctx is not None
        assert captured.get("atr_percentile") is not None, (
            "numpy truthiness silently dropped the ATR-percentile input "
            "of the published global context (since #721)"
        )


class TestBtcDirectionGateOnNumpy:
    _IND_1H = {"ema21_last": 95.0, "ema50_last": 100.0, "ema21_prev": 96.0}
    _IND_4H = {"ema21_last": 95.0, "ema50_last": 100.0}

    def test_gate_fires_on_numpy_close_series(self):
        cd = {"close": np.full(50, 94.0)}
        allowed, reason = check_btc_direction_gate(
            "LONG", self._IND_1H, self._IND_4H, cd
        )
        assert (allowed, reason) == (False, "btc_1h_4h_both_bearish_long"), (
            "the §2.1 penalty must evaluate on production numpy candles — "
            "fail-open here is the all-zero BTC_Dir truth-report column"
        )

    def test_gate_matches_list_fed_result(self):
        list_cd = {"close": [94.0] * 50}
        numpy_cd = {"close": np.asarray(list_cd["close"])}
        assert check_btc_direction_gate(
            "LONG", self._IND_1H, self._IND_4H, list_cd
        ) == check_btc_direction_gate("LONG", self._IND_1H, self._IND_4H, numpy_cd)

    def test_empty_numpy_close_uses_alignment_fallback(self):
        cd = {"close": np.empty(0)}
        allowed, reason = check_btc_direction_gate(
            "LONG", self._IND_1H, self._IND_4H, cd
        )
        assert (allowed, reason) == (False, "btc_1h_4h_both_bearish_long")


class TestBtcDirPenaltyShipsDark:
    def test_registry_default_is_off(self):
        from src.runtime_tunables import _build_registry

        tunable = _build_registry()["btc_dir_penalty_apply"]
        assert tunable.type == "bool"
        assert tunable.default is False, (
            "re-arming the §2.1 penalty changes live scoring — it must "
            "ship dark (default OFF) per the 2026-07-14 owner decision"
        )
        assert tunable.category == "Signal gating"
