"""Tuned-variant shadow arms (2026-07-16 — owner: "tune, don't disable").

MOVER_AVWAP_SCALP / VOLUME_SURGE_BREAKOUT measured-loser recipes are
forward-measured as @TUNED counterfactual arms.  These tests pin:

1. The recipe math (MAS: TP1 at median MFE + ATR/structure stop; VSB:
   extension filter + MFE TP1) on production-shape numpy arrays.
2. Observe-only plumbing: @TUNED is a variant (allocator/rollup exclusion),
   never pollutes the stop-geometry A/B rollup, and stamps into the
   geometry ledger with its own gate name.
3. Cooldown + health counters (liveness probe contract).
"""
from __future__ import annotations

import numpy as np
import pytest

from src import tuned_variants as tv
from src.geometry_ab import TUNED_SUFFIX, is_geometry_variant, summarize_geometry_ab
from src.suppression_audit import SuppressedCandidateStore


@pytest.fixture(autouse=True)
def _fresh_state(monkeypatch):
    monkeypatch.setattr(tv, "_last_stamp", {})
    # Zeroed from the module's OWN key set, not a hand-written copy of it. The
    # literal that used to sit here drifted the moment the residue counters
    # were added — a fixture asserting the author's idea of a collaborator's
    # shape back at them is the mock problem one layer down.
    monkeypatch.setattr(tv, "_counters", {k: 0 for k in tv._counters})


def _lifecycle(counters: dict) -> dict:
    """The three counters the residue is computed from, without the causes."""
    return {k: counters[k] for k in ("seen", "stamped", "skipped")}


def _candles(n: int = 40, base: float = 100.0):
    rng = np.random.default_rng(3)
    close = base + rng.normal(0.0, 0.1, n)
    return close + 0.2, close - 0.2, close  # highs, lows, closes


class TestRecipeMath:
    def test_mas_long_arm_geometry(self):
        highs, lows, closes = _candles()
        entry = float(closes[-1])
        arm = tv.compute_tuned_arm(
            setup="MOVER_AVWAP_SCALP", side="LONG", entry=entry,
            highs=highs, lows=lows, closes=closes,
        )
        assert arm is not None
        stop, tp1, reason = arm
        assert reason == "ok"
        from config import TUNED_MAS_TP1_PCT
        assert tp1 == pytest.approx(entry * (1 + TUNED_MAS_TP1_PCT / 100.0))
        assert stop < entry  # LONG stop below entry, beyond structure

    def test_mas_short_arm_geometry(self):
        highs, lows, closes = _candles()
        entry = float(closes[-1])
        arm = tv.compute_tuned_arm(
            setup="MOVER_AVWAP_SCALP", side="SHORT", entry=entry,
            highs=highs, lows=lows, closes=closes,
        )
        assert arm is not None
        stop, tp1, reason = arm
        assert tp1 < entry
        assert stop > entry

    def test_vsb_extended_entry_filtered(self):
        """VSB tuned arm refuses late chases — entry >1 ATR from the mean."""
        highs, lows, closes = _candles()
        arm = tv.compute_tuned_arm(
            setup="VOLUME_SURGE_BREAKOUT", side="LONG",
            entry=float(closes[-1]) * 1.05,   # 5% above a 0.1σ band = way >1 ATR
            highs=highs, lows=lows, closes=closes,
        )
        assert arm == (0.0, 0.0, "extension_filter")

    def test_vsb_near_value_entry_passes(self):
        highs, lows, closes = _candles()
        arm = tv.compute_tuned_arm(
            setup="VOLUME_SURGE_BREAKOUT", side="LONG",
            entry=float(closes[-1]),
            highs=highs, lows=lows, closes=closes,
        )
        assert arm is not None and arm[2] == "ok"

    def test_non_tuned_setup_returns_none(self):
        highs, lows, closes = _candles()
        assert tv.compute_tuned_arm(
            setup="SR_FLIP_RETEST", side="LONG", entry=100.0,
            highs=highs, lows=lows, closes=closes,
        ) is None


class TestVariantPlumbing:
    def test_tuned_suffix_is_variant(self):
        assert is_geometry_variant("MOVER_AVWAP_SCALP@TUNED")
        assert is_geometry_variant("VOLUME_SURGE_BREAKOUT@TUNED")

    def test_tuned_rows_never_pollute_stop_ab_rollup(self):
        """@TUNED is a variant, but it must not be pooled into the FIXED arm
        of the stop-geometry A/B (explicit-suffix regression)."""
        matrix = {
            "a": {"strategy": "MOVER_AVWAP_SCALP@FIXED", "n": 20, "win_rate": 0.5, "avg_r": 0.1},
            "b": {"strategy": "MOVER_AVWAP_SCALP@ATR", "n": 20, "win_rate": 0.5, "avg_r": 0.2},
            "c": {"strategy": "MOVER_AVWAP_SCALP@TUNED", "n": 99, "win_rate": 1.0, "avg_r": 9.9},
        }
        rows = summarize_geometry_ab(matrix)
        row = next(r for r in rows if r["strategy"] == "MOVER_AVWAP_SCALP")
        assert row["fixed"]["n"] == 20, "@TUNED leaked into the FIXED arm"
        assert row["atr"]["n"] == 20

    def test_stamp_lands_in_store_with_gate_and_suffix(self):
        highs, lows, closes = _candles()
        store = SuppressedCandidateStore(persist_path="", maxlen=50)
        stop = tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=float(closes[-1]), highs=highs, lows=lows, closes=closes,
            store=store,
        )
        assert stop is not None
        recs = store.records()
        assert len(recs) == 1
        rec = recs[0]
        assert rec["setup_class"] == f"MOVER_AVWAP_SCALP{TUNED_SUFFIX}"
        assert rec["gate_name"] == "tuned_variant:MOVER_AVWAP_SCALP"
        c = tv.counters()
        assert _lifecycle(c) == {"seen": 1, "stamped": 1, "skipped": 0}

    def test_cooldown_skips_and_counts(self):
        highs, lows, closes = _candles()
        store = SuppressedCandidateStore(persist_path="", maxlen=50)
        kw = dict(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=float(closes[-1]), highs=highs, lows=lows, closes=closes,
            store=store,
        )
        assert tv.stamp_tuned_variant(now_mono=1000.0, **kw) is not None
        assert tv.stamp_tuned_variant(now_mono=1030.0, **kw) is None
        assert len(store.records()) == 1
        assert _lifecycle(tv.counters()) == {"seen": 2, "stamped": 1, "skipped": 1}

    def test_vsb_extension_filter_counts_as_skipped(self):
        highs, lows, closes = _candles()
        store = SuppressedCandidateStore(persist_path="", maxlen=50)
        out = tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="VOLUME_SURGE_BREAKOUT", side="LONG",
            entry=float(closes[-1]) * 1.05,
            highs=highs, lows=lows, closes=closes,
            store=store,
        )
        assert out is None
        assert store.records() == []
        assert _lifecycle(tv.counters()) == {"seen": 1, "stamped": 0, "skipped": 1}

    def test_non_tuned_setup_not_counted(self):
        highs, lows, closes = _candles()
        assert tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="SR_FLIP_RETEST", side="LONG",
            entry=100.0, highs=highs, lows=lows, closes=closes,
        ) is None
        assert _lifecycle(tv.counters()) == {"seen": 0, "stamped": 0, "skipped": 0}


class TestScannerHook:
    def test_stamp_geometry_ab_stamps_tuned_arm(self, monkeypatch, numpy_seeded_store):
        """The scanner's per-candidate stamp hook routes MAS/VSB candidates
        into the tuned pipeline (production numpy candle shape)."""
        from types import SimpleNamespace

        from src import runtime_tunables
        from src.scanner import Scanner
        from src.smc import Direction

        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        store = numpy_seeded_store("ABCUSDT", ("15m",), n=40)
        ledger = SuppressedCandidateStore(persist_path="", maxlen=50)
        monkeypatch.setattr(
            "src.geometry_ab.get_geometry_store", lambda: ledger
        )
        sc = Scanner.__new__(Scanner)
        sc.data_store = store
        c15 = store.get_candles("ABCUSDT", "15m")
        sig = SimpleNamespace(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", direction=Direction.LONG,
            entry=float(c15["close"][-1]), stop_loss=float(c15["close"][-1]) * 0.99,
            tp1=float(c15["close"][-1]) * 1.02, confidence=70.0,
            mc_context_key="", entry_regime="RANGING", valid_for_minutes=60.0,
        )
        sc._stamp_geometry_ab(sig)
        setups = {r["setup_class"] for r in ledger.records()}
        assert f"MOVER_AVWAP_SCALP{TUNED_SUFFIX}" in setups


class TestMtpRetestArm:
    """MOVER_TREND_PULLBACK perfect-entry recipe (2026-07-23): limit at the
    fast MA the pullback tagged, live SL/TP1 kept, fill-aware measurement."""

    def test_long_limit_rests_at_fast_ma_below_entry(self):
        # Closes flat at 100, live entry (reclaim-bar close) above at 100.8:
        # the limit improves to the SMA7 ≈ 100.
        closes = [100.0] * 40
        arm = tv.compute_mtp_retest_arm(
            side="LONG", entry=100.8, closes=closes,
            live_stop_loss=98.5, live_tp1=102.4,
        )
        assert arm is not None
        limit, reason = arm
        assert reason == "ok"
        assert abs(limit - 100.0) < 1e-9

    def test_short_limit_rests_at_fast_ma_above_entry(self):
        closes = [100.0] * 40
        arm = tv.compute_mtp_retest_arm(
            side="SHORT", entry=99.2, closes=closes,
            live_stop_loss=101.5, live_tp1=97.6,
        )
        assert arm is not None
        limit, reason = arm
        assert reason == "ok"
        assert abs(limit - 100.0) < 1e-9

    def test_no_improvement_skipped(self):
        # Live entry already below the MA (LONG): the limit would be a WORSE
        # price — nothing to study.
        closes = [100.0] * 40
        arm = tv.compute_mtp_retest_arm(
            side="LONG", entry=99.5, closes=closes,
            live_stop_loss=98.0, live_tp1=101.5,
        )
        assert arm == (0.0, "no_improvement")

    def test_through_stop_skipped(self):
        # MA sits below the live stop: resting there is degenerate geometry.
        closes = [97.0] * 40
        arm = tv.compute_mtp_retest_arm(
            side="LONG", entry=100.0, closes=closes,
            live_stop_loss=98.0, live_tp1=102.0,
        )
        assert arm == (0.0, "through_stop")

    def test_degenerate_inputs_return_none(self):
        assert tv.compute_mtp_retest_arm(
            side="LONG", entry=100.0, closes=[100.0] * 3,
            live_stop_loss=98.0, live_tp1=102.0,
        ) is None  # too few closes for the fast MA
        assert tv.compute_mtp_retest_arm(
            side="LONG", entry=100.0, closes=[100.0] * 40,
            live_stop_loss=0.0, live_tp1=102.0,
        ) is None  # missing live SL

    def test_stamp_mtp_lands_as_limit_entry_variant(self):
        from src.suppression_audit import ENTRY_LIMIT

        store = SuppressedCandidateStore(persist_path="")
        highs, lows, closes = _candles()
        stop = tv.stamp_tuned_variant(
            symbol="MOVUSDT", channel="360_SCALP",
            setup_class="MOVER_TREND_PULLBACK", side="LONG",
            entry=float(closes[-1]) + 0.8,
            highs=highs, lows=lows, closes=closes,
            live_stop_loss=float(closes[-1]) - 2.0,
            live_tp1=float(closes[-1]) + 2.8,
            store=store,
        )
        assert stop is not None
        recs = store.records()
        assert len(recs) == 1
        rec = recs[0]
        assert rec["setup_class"] == f"MOVER_TREND_PULLBACK{TUNED_SUFFIX}"
        assert rec["entry_type"] == ENTRY_LIMIT
        # Entry re-rests at the fast MA; SL/TP1 are the live arm's levels.
        assert rec["entry"] < float(closes[-1]) + 0.8
        assert rec["stop_loss"] == pytest.approx(float(closes[-1]) - 2.0)
        assert rec["tp1"] == pytest.approx(float(closes[-1]) + 2.8)
        assert tv.counters()["stamped"] == 1

    def test_stamp_mtp_no_improvement_counts_skipped(self):
        store = SuppressedCandidateStore(persist_path="")
        highs, lows, closes = _candles()
        stop = tv.stamp_tuned_variant(
            symbol="MOVUSDT", channel="360_SCALP",
            setup_class="MOVER_TREND_PULLBACK", side="LONG",
            entry=float(closes[-1]) - 5.0,  # live entry already below the MA
            highs=highs, lows=lows, closes=closes,
            live_stop_loss=float(closes[-1]) - 8.0,
            live_tp1=float(closes[-1]) + 2.0,
            store=store,
        )
        assert stop is None
        assert store.records() == []
        assert tv.counters()["skipped"] == 1


class TestResidueNamesItsCause:
    """``66 unexplained non-stamps`` was literal, and that was the defect.

    Four paths produce a residue — an uncomputable MTP retest arm, an
    uncomputable ATR arm, a store that refused the candidate, and an exception
    — and they need four different responses. The probe paged for 15 straight
    audit cycles on 2026-08-03 without being able to say which.
    """

    def test_an_uncomputable_atr_arm_is_named(self):
        store = SuppressedCandidateStore(persist_path="", maxlen=50)
        # Too few closes for the arm's window: `compute_tuned_arm` returns None.
        out = tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=100.0, highs=[100.0], lows=[100.0], closes=[100.0],
            store=store,
        )
        assert out is None
        assert tv.residue_breakdown() == {"atr_arm_uncomputable": 1}

    def test_an_uncomputable_mtp_arm_is_named_separately(self):
        store = SuppressedCandidateStore(persist_path="", maxlen=50)
        out = tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_TREND_PULLBACK", side="LONG",
            entry=100.0, highs=[100.0], lows=[100.0], closes=[100.0],
            store=store, live_stop_loss=95.0, live_tp1=110.0,
        )
        assert out is None
        assert tv.residue_breakdown() == {"mtp_arm_uncomputable": 1}

    def test_a_refusal_by_the_ledger_writer_is_its_own_cause(self, monkeypatch):
        """Driven through the REAL ``stamp_candidate``, not a fake store.

        The first cut of this test handed in a stub whose ``add`` returned
        None. It went green — and for the wrong reason: ``stamp_candidate``
        never reads its store's return, it calls ``stamp``, so the stub raised
        ``AttributeError``, was swallowed, and wrote a fabricated entry into
        ``fail_open`` — the counter whose whole job is making a real failure
        stand out. Here the writer's own degenerate-geometry guard fires, which
        is a way it genuinely returns None.
        """
        highs, lows, closes = _candles()
        entry = float(closes[-1])
        # A zero-width stop: `stamp_candidate` refuses on sl_distance <= 0.
        monkeypatch.setattr(
            tv, "compute_tuned_arm", lambda **k: (entry, entry * 1.02, "ok")
        )
        store = SuppressedCandidateStore(persist_path="", maxlen=50)

        out = tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=entry, highs=highs, lows=lows, closes=closes, store=store,
        )

        assert out is None
        assert store.records() == []
        assert tv.residue_breakdown() == {"stamp_refused": 1}

    def test_an_exception_after_seen_is_counted_as_residue(self, monkeypatch):
        highs, lows, closes = _candles()
        monkeypatch.setattr(
            tv, "compute_tuned_arm",
            lambda **k: (_ for _ in ()).throw(RuntimeError("boom")),
        )
        out = tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=float(closes[-1]), highs=highs, lows=lows, closes=closes,
            store=SuppressedCandidateStore(persist_path="", maxlen=50),
        )
        assert out is None
        assert tv.residue_breakdown() == {"exception": 1}

    def test_the_named_causes_reconcile_with_the_arithmetic_residue(self):
        """One count is an assertion, two are a detector: a gap between them
        means a path returns without accounting for itself."""
        store = SuppressedCandidateStore(persist_path="", maxlen=50)
        for i in range(3):
            tv.stamp_tuned_variant(
                symbol=f"A{i}USDT", channel="360_SCALP",
                setup_class="MOVER_AVWAP_SCALP", side="LONG",
                entry=100.0, highs=[100.0], lows=[100.0], closes=[100.0],
                store=store,
            )
        # ...and one healthy stamp, which must not land in the residue.
        highs, lows, closes = _candles()
        tv.stamp_tuned_variant(
            symbol="OKUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=float(closes[-1]), highs=highs, lows=lows, closes=closes,
            store=store,
        )

        c = tv.counters()
        residue = c["seen"] - c["stamped"] - c["skipped"]

        assert residue == 3
        assert sum(tv.residue_breakdown().values()) == residue

    def test_a_healthy_pipeline_reports_no_causes(self):
        highs, lows, closes = _candles()
        tv.stamp_tuned_variant(
            symbol="ABCUSDT", channel="360_SCALP",
            setup_class="MOVER_AVWAP_SCALP", side="LONG",
            entry=float(closes[-1]), highs=highs, lows=lows, closes=closes,
            store=SuppressedCandidateStore(persist_path="", maxlen=50),
        )
        assert tv.residue_breakdown() == {}
