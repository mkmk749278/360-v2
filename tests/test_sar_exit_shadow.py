"""Tests for the Parabolic-SAR exit shadow arm (``src/sar_exit_shadow.py``).

Two things these tests exist to prevent, both learned the hard way on
2026-07-25:

1. **Drift between the shadow arm and the bake-off.** The whole value of this
   arm is that it confirms or kills a number we already have (PF 1.60 over
   102,496 entries). If the live SAR walk and the script's SAR walk ever
   disagree, neither number means anything. ``TestParityWithTheBakeOff`` locks
   them together on shared fixtures, so editing either side alone fails CI.

2. **Guarded assertions hiding a dead path.** Every ``Backtester`` test was
   ``if total_signals > 0: assert ...``, so a backtester that emitted nothing
   passed the entire suite for two weeks. Nothing here is guarded: the tests
   assert the stamp actually stamps, the classifier actually classifies, and
   both arms actually reach the outcome scorer.
"""
from __future__ import annotations

import numpy as np
import pytest

import scripts.exit_method_backtest as eb
from src import sar_exit_shadow as sar
from src import suppression_audit as sa
from src.geometry_ab import is_geometry_variant
from src.suppression_audit import SuppressedCandidateStore


def _walk(n: int, *, seed: int, drift: float = 0.0, start: float = 100.0):
    """Deterministic OHLC random walk — highs/lows bracket each close."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(drift, 0.6, size=n)
    closes = start + np.cumsum(steps)
    closes = np.maximum(closes, 1.0)
    opens = np.concatenate([[start], closes[:-1]])
    spread = np.abs(rng.normal(0.0, 0.3, size=n)) + 0.05
    highs = np.maximum(opens, closes) + spread
    lows = np.minimum(opens, closes) - spread
    lows = np.maximum(lows, 0.5)
    return (
        [float(v) for v in opens],
        [float(v) for v in highs],
        [float(v) for v in lows],
        [float(v) for v in closes],
    )


def _bars(opens, highs, lows, closes):
    return [
        eb.Bar(open_time_ms=i * 900_000, open=o, high=h, low=low_, close=c)
        for i, (o, h, low_, c) in enumerate(zip(opens, highs, lows, closes))
    ]


@pytest.fixture(autouse=True)
def _clear_cooldown():
    """The pair cooldown is module-global; a leaked entry silently kills the
    next test's stamp (and a silently-skipped stamp is exactly the failure
    mode this arm is built to detect)."""
    sar._last_pair_stamp.clear()
    yield
    sar._last_pair_stamp.clear()


class TestParityWithTheBakeOff:
    """The shadow arm and scripts/exit_method_backtest.py must not drift."""

    @pytest.mark.parametrize("seed", [1, 7, 42, 1234])
    def test_sar_series_is_bit_identical(self, seed):
        _, highs, lows, _ = _walk(300, seed=seed)
        mine = sar.parabolic_sar(highs, lows, 0.02, 0.2)
        theirs = eb.parabolic_sar(highs, lows, 0.02, 0.2)
        assert len(mine) == len(theirs) == 300
        assert mine == theirs
        # Not vacuous: the series must actually carry levels.
        assert sum(1 for v in mine if v is not None) >= 290

    @pytest.mark.parametrize("seed,side", [(3, "LONG"), (5, "SHORT"), (11, "LONG"), (19, "SHORT")])
    def test_exit_price_and_mfe_match_the_script(self, seed, side):
        opens, highs, lows, closes = _walk(400, seed=seed)
        bars = _bars(opens, highs, lows, closes)
        entry_idx = 60
        entry = closes[entry_idx]

        theirs = eb.simulate_trailing_exit(
            bars, entry_idx, entry, side, "sar",
            period=14, mult=1.5, sar_step=0.02, sar_max=0.2,
            tf_min=15, fee_pct=0.0, funding_bps_per_8h=0.0,
        )
        mine = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=entry_idx, entry=entry, side=side,
            step=0.02, max_step=0.2,
            max_bars=len(bars),          # unbounded, to match the script
            bar_minutes=15,
        )

        assert mine is not None, "the trail walk must resolve on clean data"
        assert theirs.exit_price is not None
        assert mine["exit_price"] == pytest.approx(theirs.exit_price, rel=1e-12)
        assert mine["mfe_pct"] == pytest.approx(theirs.mfe_pct, rel=1e-12)
        assert mine["hold_min"] == pytest.approx(float(theirs.hold_mins), rel=1e-12)


class TestTrailWalk:
    def test_a_long_that_reverses_is_stopped_by_the_trail(self):
        # Rally then collapse: the SAR must catch the turn, not ride to the end.
        opens, highs, lows, closes = _walk(120, seed=2, drift=0.5)
        o2, h2, l2, c2 = _walk(120, seed=3, drift=-0.9, start=closes[-1])
        opens, highs, lows, closes = opens + o2, highs + h2, lows + l2, closes + c2
        res = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=100, entry=closes[100], side="LONG",
            step=0.02, max_step=0.2, max_bars=192, bar_minutes=15,
        )
        assert res is not None
        assert res["exit_reason"] == sar.REASON_TRAIL
        assert res["exit_idx"] > 100

    def test_window_bound_marks_to_the_close_instead_of_running_forever(self):
        opens, highs, lows, closes = _walk(500, seed=9, drift=0.4)
        res = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=10, entry=closes[10], side="LONG",
            step=0.02, max_step=0.2, max_bars=5, bar_minutes=15,
        )
        assert res is not None
        # Either the trail fired inside 5 bars or we marked to the window close;
        # in both cases the walk must not have run past the bound.
        assert res["exit_idx"] <= 15
        assert res["hold_min"] <= 5 * 15

    def test_a_gap_through_the_stop_fills_at_the_open_not_the_stop(self):
        """The pessimistic fill model — a gap must not be scored as if the
        stop held. Getting this backwards flatters every trailing arm."""
        highs = [100.0, 101.0, 102.0, 103.0, 104.0, 90.0]
        lows = [99.0, 100.0, 101.0, 102.0, 103.0, 88.0]
        closes = [100.0, 101.0, 102.0, 103.0, 104.0, 89.0]
        opens = [100.0, 100.0, 101.0, 102.0, 103.0, 91.0]
        res = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=2, entry=102.0, side="LONG",
            step=0.02, max_step=0.2, max_bars=10, bar_minutes=15,
        )
        assert res is not None
        assert res["exit_reason"] == sar.REASON_TRAIL
        # The bar opened at 91 having gapped below the SAR level; the fill is
        # the open, which is strictly worse than the stop.
        assert res["exit_price"] == pytest.approx(91.0)


class TestPairStamping:
    def _stamp(self, store, **kw):
        base = dict(
            symbol="BTCUSDT", channel="scalp", setup_class="SR_FLIP_RETEST",
            side="LONG", entry=100.0, stop_loss=99.0, tp1=102.0, store=store,
        )
        base.update(kw)
        return sar.stamp_sar_pair(**base)

    def test_both_arms_stamp_together_with_the_right_exit_models(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True

        recs = store.records()
        assert len(recs) == 2, "a lone arm biases the A/B — both or neither"
        by_setup = {r["setup_class"]: r for r in recs}
        assert set(by_setup) == {"SR_FLIP_RETEST@SARBASE", "SR_FLIP_RETEST@SAREXIT"}
        assert by_setup["SR_FLIP_RETEST@SARBASE"]["exit_model"] == sa.EXIT_STATIC
        assert by_setup["SR_FLIP_RETEST@SAREXIT"]["exit_model"] == sa.EXIT_TRAILING
        # Both arms share the R denominator — that is what makes them comparable.
        assert (
            by_setup["SR_FLIP_RETEST@SARBASE"]["sl_distance"]
            == by_setup["SR_FLIP_RETEST@SAREXIT"]["sl_distance"]
        )

    def test_cooldown_blocks_the_near_duplicate_rescan(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, now_mono=1000.0, provenance=sa.PROVENANCE_SUPPRESSED) is True
        assert self._stamp(store, now_mono=1010.0, provenance=sa.PROVENANCE_SUPPRESSED) is False
        assert len(store.records()) == 2

    def test_a_suppressed_stamp_can_never_swallow_an_emitted_one(self, tmp_path):
        """Owner-caught 2026-07-25: one shared cooldown budget per
        (symbol, setup, side) let a suppressed candidate block a REAL emitted
        signal minutes later. Suppressed outnumber emissions by orders of
        magnitude, so the emitted sample — the only population that can justify
        changing what subscribers receive — was silently, non-randomly thinned.
        """
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(
            store, now_mono=1000.0, provenance=sa.PROVENANCE_SUPPRESSED
        ) is True
        # Same symbol/setup/side, 10s later, but this one actually went out.
        assert self._stamp(
            store, now_mono=1010.0, provenance=sa.PROVENANCE_EMITTED
        ) is True, "an emitted signal must never be dropped from the measurement"
        emitted = [r for r in store.records() if r["provenance"] == sa.PROVENANCE_EMITTED]
        assert len(emitted) == 2      # both arms of the emitted pair

    def test_emitted_stamps_are_never_throttled_against_each_other(self, tmp_path):
        """Duplicate emissions are already prevented upstream by
        dispatch_cooldown, so this arm must not second-guess them."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        for t in (1000.0, 1005.0, 1010.0):
            assert self._stamp(store, now_mono=t, provenance=sa.PROVENANCE_EMITTED) is True
        assert len(store.records()) == 6

    def test_an_emitted_stamp_does_not_consume_the_suppressed_budget(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, now_mono=1000.0, provenance=sa.PROVENANCE_EMITTED) is True
        assert self._stamp(
            store, now_mono=1001.0, provenance=sa.PROVENANCE_SUPPRESSED
        ) is True, "the suppressed arm has its own cooldown keyspace"

    def test_bad_geometry_stamps_nothing(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, stop_loss=100.0) is False   # zero SL distance
        assert self._stamp(store, entry=0.0, symbol="ETHUSDT") is False
        assert self._stamp(store, side="SIDEWAYS", symbol="SOLUSDT") is False
        assert store.records() == []

    def test_provenance_travels_with_both_arms(self, tmp_path):
        """Emitted vs gate-suppressed must be recorded AT the stamp.

        The two scanner call sites are the only place that distinction exists;
        nothing downstream can recover it. Without it the ledger silently mixes
        "would this exit improve the signals we SENT" with "…every candidate we
        considered" — and only the first can justify changing live output.
        """
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, provenance=sa.PROVENANCE_EMITTED) is True
        recs = store.records()
        assert len(recs) == 2
        # Both arms are ONE candidate — they must agree, or a pair could be
        # split across the emitted/suppressed filter.
        assert {r["provenance"] for r in recs} == {sa.PROVENANCE_EMITTED}

    def test_suppressed_provenance_is_recorded_too(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, provenance=sa.PROVENANCE_SUPPRESSED) is True
        assert {r["provenance"] for r in store.records()} == {sa.PROVENANCE_SUPPRESSED}

    def test_provenance_defaults_to_unknown_not_to_emitted(self, tmp_path):
        """Records stamped before this shipped have no provenance. They must
        read as unknown — counting them as emitted would inflate the only
        population that can justify a live change."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True
        assert {r["provenance"] for r in store.records()} == {""}

    def test_measurement_arms_are_never_activatable_strategies(self):
        """The allocator must not be able to recommend a measurement row."""
        assert is_geometry_variant("SR_FLIP_RETEST@SAREXIT")
        assert is_geometry_variant("SR_FLIP_RETEST@SARBASE")
        assert not is_geometry_variant("SR_FLIP_RETEST")


class TestScannerWiringCarriesProvenance:
    """The two scanner call sites are the ONLY place emitted-vs-suppressed
    exists. If a site stops passing it, every record silently becomes
    'unknown' and the emitted-only view goes quietly empty — a failure that
    looks exactly like 'no signals yet'."""

    def test_the_suppressed_call_site_marks_records_suppressed(self):
        from types import SimpleNamespace

        from src.scanner import Scanner

        seen: list = []

        class _Stub:
            def _stamp_geometry_ab(self, sig, provenance=""):
                seen.append(provenance)

        sig = SimpleNamespace(
            symbol="ETHUSDT", channel="360_SCALP", setup_class="BREAKOUT_RETEST",
            entry=100.0, stop_loss=99.0, tp1=101.5,
        )
        Scanner._stamp_suppressed(_Stub(), sig, "quiet_scalp_block")
        assert seen == [sa.PROVENANCE_SUPPRESSED]

    def test_every_stamp_call_site_passes_provenance_explicitly(self):
        """A new call site must not be able to default to unknown."""
        import inspect
        import re

        import src.scanner as scanner_mod

        src_text = inspect.getsource(scanner_mod)
        calls = re.findall(r"_stamp_geometry_ab\((?!self,?\s*sig:)[^)]*\)", src_text)
        # Drop the definition itself; what remains are invocations.
        invocations = [c for c in calls if not c.startswith("_stamp_geometry_ab(self")]
        assert invocations, "expected to find the stamp call sites"
        for call in invocations:
            assert "provenance=" in call, f"call site without provenance: {call}"
        # Both halves of the sample must be represented.
        joined = " ".join(invocations)
        assert "PROVENANCE_EMITTED" in joined
        assert "PROVENANCE_SUPPRESSED" in joined


class TestOutcomeScoring:
    def test_trailing_records_score_continuous_r_not_a_tp1_binary(self):
        rec = {
            "classification": sa.WOULD_WIN, "exit_model": sa.EXIT_TRAILING,
            "side": "LONG", "entry": 100.0, "stop_loss": 99.0, "tp1": 102.0,
            "sl_distance": 1.0, "trail_exit_price": 103.5, "trail_mfe_pct": 4.0,
        }
        out = sa.candidate_outcome(rec)
        assert out is not None
        # 3.5 / 1.0 — the trail rode past TP1 and the R says so. A static
        # record would have been capped at r_to_tp1 = 2.0.
        assert out["gross_r_multiple"] == pytest.approx(3.5)
        assert out["won"] is True
        assert out["mfe_pct"] == pytest.approx(4.0)

    def test_a_trail_stopped_below_entry_is_a_fractional_loss(self):
        rec = {
            "classification": sa.WOULD_LOSE, "exit_model": sa.EXIT_TRAILING,
            "side": "SHORT", "entry": 100.0, "stop_loss": 101.0, "tp1": 98.0,
            "sl_distance": 1.0, "trail_exit_price": 100.4, "trail_mfe_pct": 0.5,
        }
        out = sa.candidate_outcome(rec)
        assert out is not None
        assert out["gross_r_multiple"] == pytest.approx(-0.4)
        assert out["won"] is False

    def test_static_records_are_unchanged_by_the_trailing_branch(self):
        """Regression: every pre-2026-07-25 record must score exactly as before."""
        rec = {
            "classification": sa.WOULD_WIN, "side": "LONG", "entry": 100.0,
            "stop_loss": 99.0, "tp1": 102.0, "sl_distance": 1.0,
        }
        out = sa.candidate_outcome(rec)
        assert out is not None
        assert out["gross_r_multiple"] == pytest.approx(2.0)   # r_to_tp1, capped
        assert out["won"] is True

    def test_a_trail_with_no_exit_price_scores_zero_not_a_crash(self):
        rec = {
            "classification": sa.WOULD_EXPIRE, "exit_model": sa.EXIT_TRAILING,
            "side": "LONG", "entry": 100.0, "stop_loss": 99.0, "tp1": 102.0,
            "sl_distance": 1.0,
        }
        out = sa.candidate_outcome(rec)
        assert out is not None
        assert out["gross_r_multiple"] == 0.0


class TestClassifyEndToEnd:
    """The whole path: stamp → classify → outcome, both arms, one window."""

    def _fetcher(self, opens, highs, lows, closes, entry_index):
        def _fetch(symbol, since_ts):
            return {
                "open": list(opens), "high": list(highs),
                "low": list(lows), "close": list(closes),
                "entry_index": entry_index,
            }
        return _fetch

    def test_both_arms_classify_and_reach_the_edge_feed(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert sar.stamp_sar_pair(
            symbol="BTCUSDT", channel="scalp", setup_class="SR_FLIP_RETEST",
            side="LONG", entry=100.0, stop_loss=99.0, tp1=102.0, store=store,
        ) is True

        warmup = 40
        opens, highs, lows, closes = _walk(warmup + 100, seed=21, drift=0.3)
        fed: list = []
        counters = store.classify_pending(
            fetch_ohlc_since=self._fetcher(opens, highs, lows, closes, warmup),
            now_ts=__import__("time").time() + 3600,
            window_sec=1.0,
            on_classified=fed.append,
            trail_classifier=sar.classify_sar_record,
        )

        # Unguarded: the path must be ALIVE. A classifier that resolves nothing
        # is the exact failure this suite exists to catch.
        assert sum(counters.values()) == 2, counters
        assert counters.get(sa.INSUFFICIENT, 0) == 0
        assert len(fed) == 2

        by_setup = {r["setup_class"]: r for r in store.records()}
        trail = by_setup["SR_FLIP_RETEST@SAREXIT"]
        base = by_setup["SR_FLIP_RETEST@SARBASE"]
        assert trail["classification"] is not None
        assert base["classification"] is not None
        assert trail["trail_exit_price"] is not None
        assert trail["trail_exit_reason"] in (sar.REASON_TRAIL, sar.REASON_WINDOW)
        # Both arms scored — the pair is comparable, which is the point.
        assert sa.candidate_outcome(trail) is not None
        assert sa.candidate_outcome(base) is not None

    def test_the_static_arm_does_not_see_the_warmup_prefix(self, tmp_path):
        """The control arm shares the trail's fetcher, warmup and all. If it
        scored the pre-entry bars it would count price action that happened
        BEFORE the signal as the signal's own outcome."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert sar.stamp_sar_pair(
            symbol="BTCUSDT", channel="scalp", setup_class="SR_FLIP_RETEST",
            side="LONG", entry=100.0, stop_loss=99.0, tp1=102.0, store=store,
        ) is True

        # Warmup spikes through TP1 (110); post-entry never leaves 99.5–100.5.
        warmup = 5
        opens = [100.0] * warmup + [100.0] * 20
        highs = [110.0] * warmup + [100.5] * 20
        lows = [99.5] * warmup + [99.5] * 20
        closes = [100.0] * warmup + [100.0] * 20

        store.classify_pending(
            fetch_ohlc_since=self._fetcher(opens, highs, lows, closes, warmup),
            now_ts=__import__("time").time() + 3600,
            window_sec=1.0,
            trail_classifier=sar.classify_sar_record,
        )
        base = {r["setup_class"]: r for r in store.records()}["SR_FLIP_RETEST@SARBASE"]
        assert base["classification"] == sa.WOULD_EXPIRE, (
            "TP1 was only touched in the warmup prefix — scoring it a win means "
            "the prefix leaked into the measurement window"
        )
        assert base["post_price_max"] == pytest.approx(100.5)


class TestDarkFirst:
    def test_the_arm_ships_default_off(self):
        from config import SAR_EXIT_SHADOW_ENABLED
        assert SAR_EXIT_SHADOW_ENABLED is False, (
            "the app is live on the Play Store; a money-path-adjacent "
            "measurement ships dark and is switched on deliberately"
        )

    def test_the_runtime_tunable_defaults_off_too(self):
        from src import runtime_tunables as rt
        spec = rt.registry()["sar_exit_shadow_enabled"]
        assert spec.default is False
        assert spec.type == "bool"

    def test_the_window_matches_the_bake_off_that_produced_the_verdict(self):
        from config import (
            SAR_EXIT_SHADOW_BAR_MINUTES,
            SAR_EXIT_SHADOW_MAX_STEP,
            SAR_EXIT_SHADOW_STEP,
            SAR_EXIT_SHADOW_WINDOW_BARS,
        )
        # Drifting any of these makes the shadow measure a different thing
        # than the 6-month result it is supposed to confirm or kill.
        assert SAR_EXIT_SHADOW_WINDOW_BARS == 192
        assert SAR_EXIT_SHADOW_BAR_MINUTES == 15
        assert SAR_EXIT_SHADOW_STEP == 0.02
        assert SAR_EXIT_SHADOW_MAX_STEP == 0.2


class TestSummary:
    def test_a_thin_arm_reads_measuring_never_a_winner(self):
        matrix = {
            "a": {"strategy": "SR_FLIP_RETEST@SAREXIT", "n": 80, "win_rate": 0.4, "avg_r": 0.30},
            "b": {"strategy": "SR_FLIP_RETEST@SARBASE", "n": 3, "win_rate": 0.5, "avg_r": -0.10},
        }
        rows = sar.summarize_sar_exit(matrix, min_sample=15)
        assert len(rows) == 1
        assert rows[0]["leader"] == "MEASURING"
        assert rows[0]["delta_r"] is None

    def test_a_measured_pair_names_its_leader_and_delta(self):
        matrix = {
            "a": {"strategy": "SR_FLIP_RETEST@SAREXIT", "n": 100, "win_rate": 0.40, "avg_r": 0.30},
            "b": {"strategy": "SR_FLIP_RETEST@SARBASE", "n": 100, "win_rate": 0.55, "avg_r": -0.10},
        }
        rows = sar.summarize_sar_exit(matrix, min_sample=15)
        assert rows[0]["strategy"] == "SR_FLIP_RETEST"
        assert rows[0]["leader"] == "SAR"
        assert rows[0]["delta_r"] == pytest.approx(0.40)
        # The lower win rate must not decide it — a trend-following exit wins
        # small-often-lose / big-rarely-win, which is the whole open question.
        assert rows[0]["sar"]["win_rate"] < rows[0]["base"]["win_rate"]

    def test_non_sar_rows_are_ignored(self):
        matrix = {
            "a": {"strategy": "SR_FLIP_RETEST@ATR", "n": 100, "win_rate": 0.5, "avg_r": 0.2},
            "b": {"strategy": "SR_FLIP_RETEST@FIXED", "n": 100, "win_rate": 0.5, "avg_r": 0.1},
            "c": {"strategy": "SR_FLIP_RETEST", "n": 100, "win_rate": 0.5, "avg_r": 0.1},
        }
        assert sar.summarize_sar_exit(matrix) == []
