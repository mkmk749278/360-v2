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

    def test_a_suppressed_stamp_can_never_swallow_a_queued_one(self, tmp_path):
        """Owner-caught 2026-07-25: one shared cooldown budget per
        (symbol, setup, side) let a suppressed candidate block a REAL queued
        signal minutes later. Suppressed outnumber emissions by orders of
        magnitude, so the sample that can lead to a live change was silently,
        non-randomly thinned. The cooldown stays keyed by provenance.
        """
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(
            store, now_mono=1000.0, provenance=sa.PROVENANCE_SUPPRESSED
        ) is True
        # Same symbol/setup/side, 10s later, but this one passed every gate.
        assert self._stamp(
            store, now_mono=1010.0, provenance=sa.PROVENANCE_ENQUEUED
        ) is True, "a queued candidate must never be dropped from the measurement"
        queued = [r for r in store.records() if r["provenance"] == sa.PROVENANCE_ENQUEUED]
        assert len(queued) == 2      # both arms of the queued pair

    def test_stamping_can_never_write_emitted(self, tmp_path):
        """The stamp site does not know whether a signal was delivered.

        It fires when ``signal_queue.put`` accepts a candidate; the router then
        applies its own gate layer and drops most of what it dequeues. EMITTED
        is written ONLY by ``promote_to_emitted`` after confirmed delivery, so
        no stamp may produce it — that conflation was a ~30x inflation of the
        one population allowed to justify changing live output.
        """
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        for prov in (sa.PROVENANCE_SUPPRESSED, sa.PROVENANCE_ENQUEUED, ""):
            self._stamp(store, now_mono=1000.0, provenance=prov, symbol=f"X{prov}USDT")
        assert not [
            r for r in store.records() if r["provenance"] == sa.PROVENANCE_EMITTED
        ]

    def test_a_persisting_queued_candidate_is_throttled_not_re_stamped(self, tmp_path):
        """The bug this replaces: EMITTED used to bypass the cooldown on the
        premise that "an emission is a discrete dispatch event". It was not —
        it was an enqueue, so every 15s re-detection of one persisting setup
        stamped again. Real data: one WLFIUSDT setup produced 5 'emitted' rows
        at an identical entry inside 6.7h.
        """
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, now_mono=1000.0, provenance=sa.PROVENANCE_ENQUEUED) is True
        for t in (1005.0, 1010.0):
            assert self._stamp(
                store, now_mono=t, provenance=sa.PROVENANCE_ENQUEUED
            ) is False, "a re-detected persisting candidate must not re-stamp"
        assert len(store.records()) == 2

    def test_a_queued_stamp_does_not_consume_the_suppressed_budget(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, now_mono=1000.0, provenance=sa.PROVENANCE_ENQUEUED) is True
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
        assert self._stamp(store, provenance=sa.PROVENANCE_ENQUEUED) is True
        recs = store.records()
        assert len(recs) == 2
        # Both arms are ONE candidate — they must agree, or a pair could be
        # split across the emitted/queued/suppressed filter.
        assert {r["provenance"] for r in recs} == {sa.PROVENANCE_ENQUEUED}

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
        # Both halves of the sample must be represented. The enqueue site
        # stamps ENQUEUED, never EMITTED — only the router, after confirmed
        # delivery, may promote a record to EMITTED.
        joined = " ".join(invocations)
        assert "PROVENANCE_ENQUEUED" in joined
        assert "PROVENANCE_EMITTED" not in joined, (
            "the scanner cannot know a signal was delivered — the router does"
        )
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


class TestProvenancePromotionOnDispatch:
    """The enqueue-vs-dispatch fix (owner-caught 2026-07-25).

    The scanner stamped ``emitted`` the moment ``signal_queue.put`` accepted a
    candidate, and its comment claimed "the signal really did go out". It had
    not. ``SignalRouter._process`` consumes that queue and applies a second
    gate layer — correlation lock, per-symbol/per-channel cooldown, per-channel
    concurrent cap, correlation group limit, global same-direction throttle,
    TP/SL sanity, staleness — dropping most of what it dequeues.

    Measured over one 6.7h window: 90 distinct candidates reached the queue, 3
    reached the feed. The surplus was not a random sample either — it skewed to
    81% SHORT against a 52% SHORT real feed, because the same-direction
    throttle rejected the short pile-up *after* it had been stamped emitted.

    So EMITTED must be written at delivery, by the router, and nowhere else.
    """

    def _stamp(self, store, **kw):
        base = dict(
            symbol="BTCUSDT", channel="scalp", setup_class="SR_FLIP_RETEST",
            side="LONG", entry=100.0, stop_loss=99.0, tp1=102.0, store=store,
            provenance=sa.PROVENANCE_ENQUEUED,
        )
        base.update(kw)
        return sar.stamp_sar_pair(**base)

    def _promote(self, store, **kw):
        base = dict(
            symbol="BTCUSDT", setup_class="SR_FLIP_RETEST", side="LONG",
            entry=100.0, store=store,
        )
        base.update(kw)
        return sar.promote_to_emitted(**base)

    def test_promotion_flips_both_arms_of_the_delivered_candidate(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True

        assert self._promote(store) == 2, "a half-promoted pair biases the A/B"
        assert {r["provenance"] for r in store.records()} == {sa.PROVENANCE_EMITTED}

    def test_a_queued_candidate_the_router_drops_stays_queued(self, tmp_path):
        """The whole point: no promotion call ⇒ it is not in the emitted set."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True

        assert not [
            r for r in store.records() if r["provenance"] == sa.PROVENANCE_EMITTED
        ]
        assert {r["provenance"] for r in store.records()} == {sa.PROVENANCE_ENQUEUED}

    def test_promotion_never_touches_a_suppressed_record(self, tmp_path):
        """A gate-killed candidate must never become emitted — that would put
        a signal users never saw into the population that justifies changes."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store, provenance=sa.PROVENANCE_SUPPRESSED) is True

        assert self._promote(store) == 0
        assert {r["provenance"] for r in store.records()} == {sa.PROVENANCE_SUPPRESSED}

    def test_promotion_matches_on_entry_so_a_different_candidate_is_untouched(
        self, tmp_path,
    ):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True

        # Same symbol/setup/side, different price ⇒ a different candidate.
        assert self._promote(store, entry=123.0) == 0
        assert {r["provenance"] for r in store.records()} == {sa.PROVENANCE_ENQUEUED}

    def test_one_dispatch_promotes_one_candidate_not_the_whole_history(
        self, tmp_path,
    ):
        """A setup that persists across scan cycles accumulates rows. A single
        dispatch must promote the newest candidate only — relabelling the
        history would re-inflate exactly what this fix removes."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        # Two distinct detections, far enough apart to clear the cooldown.
        assert self._stamp(store, now_mono=1000.0) is True
        # ``now_mono`` drives only the cooldown; ``suppress_timestamp`` is wall
        # clock, and the test body runs in microseconds. Age the first pair so
        # the two detections are separated in wall time as they are in prod.
        with store._lock:
            for rec in store._buffer:
                rec["suppress_timestamp"] -= 600.0
        assert self._stamp(store, now_mono=100000.0) is True
        assert len(store.records()) == 4

        assert self._promote(store) == 2
        provs = [r["provenance"] for r in store.records()]
        assert provs.count(sa.PROVENANCE_EMITTED) == 2
        assert provs.count(sa.PROVENANCE_ENQUEUED) == 2

    def test_promotion_cannot_rewrite_an_already_measured_record(self, tmp_path):
        """Once a record is classified its outcome is in the edge matrix.
        Re-labelling it would retroactively move a measured result between
        populations."""
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True
        with store._lock:
            for rec in store._buffer:
                rec["classification"] = "TP1_FIRST"

        assert self._promote(store) == 0

    def test_promotion_ignores_a_stamp_older_than_the_window(self, tmp_path):
        store = SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"), maxlen=100)
        assert self._stamp(store) is True

        assert self._promote(store, max_age_sec=0.0) == 0

    def test_promotion_is_fail_open(self, tmp_path):
        """A measurement re-label must never break dispatch."""
        class _Boom:
            def promote_provenance(self, **_kw):
                raise RuntimeError("ledger down")

        assert sar.promote_to_emitted(
            symbol="BTCUSDT", setup_class="SR_FLIP_RETEST", side="LONG",
            entry=100.0, store=_Boom(),
        ) == 0


class TestPreFixRecordsAreRelabelledOnLoad:
    """Records persisted before the fix carry ``emitted`` written at the
    enqueue site, so ~97% were never delivered. They load as ``enqueued``:
    the truthful label, and it fails safe by removing them from the emitted
    sample rather than inventing membership in it."""

    def _write(self, path, provenance, *, schema=None, ts=None):
        import json
        import time as _t
        rec = {
            "gate_name": "sar_exit_shadow:base",
            "setup_class": "SR_FLIP_RETEST@SARBASE",
            "symbol": "BTCUSDT", "channel": "scalp", "side": "LONG",
            "entry": 100.0, "stop_loss": 99.0, "tp1": 102.0, "sl_distance": 1.0,
            "confidence": 70.0, "context_key": "", "regime": "",
            "valid_for_minutes": 0.0,
            "suppress_timestamp": _t.time() if ts is None else ts,
            "provenance": provenance, "classification": None,
        }
        if schema is not None:
            rec["prov_schema"] = schema
        path.write_text(json.dumps([rec]))

    def test_a_pre_fix_emitted_record_loads_as_enqueued(self, tmp_path):
        """No schema marker ⇒ written by the enqueue-site stamp ⇒ not delivery."""
        p = tmp_path / "s.json"
        self._write(p, sa.PROVENANCE_EMITTED)  # no prov_schema at all

        store = SuppressedCandidateStore(persist_path=str(p), maxlen=100)
        assert [r["provenance"] for r in store.records()] == [sa.PROVENANCE_ENQUEUED]

    def test_a_post_fix_emitted_record_is_trusted(self, tmp_path):
        p = tmp_path / "s.json"
        self._write(p, sa.PROVENANCE_EMITTED, schema=sa.PROVENANCE_SCHEMA)

        store = SuppressedCandidateStore(persist_path=str(p), maxlen=100)
        assert [r["provenance"] for r in store.records()] == [sa.PROVENANCE_EMITTED]

    def test_suppressed_records_are_left_alone(self, tmp_path):
        p = tmp_path / "s.json"
        self._write(p, sa.PROVENANCE_SUPPRESSED)

        store = SuppressedCandidateStore(persist_path=str(p), maxlen=100)
        assert [r["provenance"] for r in store.records()] == [sa.PROVENANCE_SUPPRESSED]

    def test_a_recent_pre_fix_record_is_not_trusted_by_being_recent(self, tmp_path):
        """The bug this replaced: a wall-clock cutoff set to when the fix was
        *written* trusted everything stamped after it, including eight hours of
        old-code stamps written before the fix actually deployed. 88 rows of
        enqueue-site data rendered as "Delivered to users" for a window whose
        real feed was one signal. Recency is not provenance."""
        p = tmp_path / "s.json"
        import time as _t
        self._write(p, sa.PROVENANCE_EMITTED, ts=_t.time())  # stamped seconds ago

        store = SuppressedCandidateStore(persist_path=str(p), maxlen=100)
        assert [r["provenance"] for r in store.records()] == [sa.PROVENANCE_ENQUEUED]

    def test_a_promoted_record_survives_a_reload(self, tmp_path):
        """Promotion is what makes EMITTED true, so it must mark the record —
        otherwise the load-time migration downgrades a genuine delivery."""
        p = tmp_path / "s.json"
        self._write(p, sa.PROVENANCE_ENQUEUED, schema=sa.PROVENANCE_SCHEMA)
        store = SuppressedCandidateStore(persist_path=str(p), maxlen=100)

        assert store.promote_provenance(
            symbol="BTCUSDT", side="LONG", setup_prefix="SR_FLIP_RETEST",
            entry=100.0, from_provenance=sa.PROVENANCE_ENQUEUED,
            to_provenance=sa.PROVENANCE_EMITTED, max_age_sec=3600.0,
        ) == 1
        rec = store.records()[0]
        assert rec["provenance"] == sa.PROVENANCE_EMITTED
        assert sa._migrate_provenance(dict(rec))["provenance"] == sa.PROVENANCE_EMITTED

    def test_a_stamped_record_carries_the_schema_marker(self):
        """The marker has to be written at the stamp site or every fresh record
        loads as pre-fix."""
        store = SuppressedCandidateStore(persist_path="", maxlen=10)
        sa.stamp_candidate(
            gate_name="g", symbol="BTCUSDT", channel="scalp",
            setup_class="SR_FLIP_RETEST", side="LONG",
            entry=100.0, stop_loss=99.0, tp1=102.0,
            provenance=sa.PROVENANCE_ENQUEUED, store=store,
        )
        assert store.records()[0]["prov_schema"] == sa.PROVENANCE_SCHEMA


class TestRouterPromotesOnConfirmedDelivery:
    """The promotion must be wired at the router's confirmed-delivery point,
    after every drop gate. Wiring it anywhere earlier reintroduces the bug."""

    def test_the_router_promotes_after_registering_the_delivered_signal(self):
        import inspect

        from src import signal_router

        src_text = inspect.getsource(signal_router)
        assert "promote_to_emitted" in src_text, (
            "the router is the only component that knows a signal was delivered"
        )
        # It must sit after the confirmed-delivery registration, not before it.
        register = src_text.index("Register only after confirmed delivery")
        promote = src_text.index("promote_to_emitted")
        assert promote > register, (
            "promotion before confirmed delivery is the bug being fixed"
        )


class TestATrailingTradeResolvesWhenItActuallyCloses:
    """A trailing arm's exit is knowable the moment the forward candles cover
    it. Holding every row at RUNNING until the full 48h window elapsed made the
    tab read "0 resolved, 88 still running" for trades that had closed hours
    earlier (owner-caught 2026-07-26)."""

    WINDOW = 48 * 3600.0

    def _store_with_pending(self, ts):
        store = SuppressedCandidateStore(persist_path="", maxlen=10)
        rec = sa.SuppressedCandidateRecord(
            gate_name="sar_exit_shadow:base",
            setup_class="SR_FLIP_RETEST@SARBASE",
            symbol="BTCUSDT", channel="scalp", side="LONG",
            entry=100.0, stop_loss=99.0, tp1=102.0, sl_distance=1.0,
            confidence=70.0, context_key="", regime="",
            valid_for_minutes=0.0, suppress_timestamp=ts,
            exit_model=sa.EXIT_TRAILING,
        )
        store.stamp(rec)
        return store

    @staticmethod
    def _ohlc(_symbol, _since):
        return {"high": [1.0, 1.0], "low": [1.0, 1.0], "close": [1.0, 1.0]}

    def test_a_trail_exit_resolves_immediately_not_in_48h(self):
        import time as _t
        store = self._store_with_pending(_t.time() - 600.0)  # 10 min old

        counters = store.classify_pending(
            fetch_ohlc_since=self._ohlc,
            window_sec=self.WINDOW,
            trail_classifier=lambda rec, ohlc: {
                "classification": "WIN",
                "exit_reason": sa.REASON_TRAIL,
                "trail_exit_price": 101.0,
            },
        )
        assert counters.get("WIN") == 1
        assert store.records()[0]["classification"] == "WIN"

    def test_an_unexited_trade_stays_running_and_is_not_marked_to_close(self):
        """A "window" verdict mid-window is the walker running out of bars, not
        the trade closing. Booking it would record an arbitrary price as a
        realized result."""
        import time as _t
        store = self._store_with_pending(_t.time() - 600.0)

        counters = store.classify_pending(
            fetch_ohlc_since=self._ohlc,
            window_sec=self.WINDOW,
            trail_classifier=lambda rec, ohlc: {
                "classification": "LOSS",
                "exit_reason": sa.REASON_WINDOW,
                "trail_exit_price": 99.5,
            },
        )
        assert counters == {}
        assert store.records()[0]["classification"] is None

    def test_a_window_verdict_is_accepted_once_the_window_has_elapsed(self):
        import time as _t
        store = self._store_with_pending(_t.time() - self.WINDOW - 60.0)

        counters = store.classify_pending(
            fetch_ohlc_since=self._ohlc,
            window_sec=self.WINDOW,
            trail_classifier=lambda rec, ohlc: {
                "classification": "LOSS",
                "exit_reason": sa.REASON_WINDOW,
                "trail_exit_price": 99.5,
            },
        )
        assert counters.get("LOSS") == 1

    def test_missing_candles_mid_window_are_not_a_verdict(self):
        """Mid-window the candles may simply not exist yet; only a record whose
        full window passed without data is genuinely INSUFFICIENT."""
        import time as _t
        store = self._store_with_pending(_t.time() - 600.0)

        counters = store.classify_pending(
            fetch_ohlc_since=lambda *_a: None,
            window_sec=self.WINDOW,
            trail_classifier=lambda rec, ohlc: None,
        )
        assert counters == {}
        assert store.records()[0]["classification"] is None

    def test_a_static_arm_still_waits_for_its_full_window(self):
        """Static outcomes are a TP/SL race decided by window extremes — they
        cannot be resolved from a partial window."""
        import time as _t
        store = SuppressedCandidateStore(persist_path="", maxlen=10)
        store.stamp(sa.SuppressedCandidateRecord(
            gate_name="g", setup_class="SR_FLIP_RETEST", symbol="BTCUSDT",
            channel="scalp", side="LONG", entry=100.0, stop_loss=99.0,
            tp1=102.0, sl_distance=1.0, confidence=70.0,
            context_key="", regime="", valid_for_minutes=0.0,
            suppress_timestamp=_t.time() - 600.0, exit_model=sa.EXIT_STATIC,
        ))

        counters = store.classify_pending(
            fetch_ohlc_since=self._ohlc, window_sec=self.WINDOW,
        )
        assert counters == {}
        assert store.records()[0]["classification"] is None


class TestEarlyResolutionIsResultIdentical:
    """Resolving early must not change the answer, only when we learn it.

    The SAR level at bar i depends only on bars <= i, and the ledger's fetch
    anchors the series so entry always sits `warmup` bars in. So a trail exit
    found at T+1h is the same exit the full 48h walk would have found. If that
    were not true, early resolution would be silently rewriting outcomes that
    feed the Strategy x Context edge matrix.
    """

    @pytest.mark.parametrize("seed,side", [(2, "LONG"), (5, "SHORT"), (13, "LONG"), (21, "SHORT")])
    def test_a_trail_exit_is_the_same_whenever_it_is_computed(self, seed, side):
        drift = 0.5 if side == "LONG" else -0.5
        opens, highs, lows, closes = _walk(60, seed=seed, drift=drift)
        o2, h2, l2, c2 = _walk(140, seed=seed + 100, drift=-drift, start=closes[-1])
        opens, highs, lows, closes = opens + o2, highs + h2, lows + l2, closes + c2
        entry_idx, entry = 55, closes[55]

        full = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=entry_idx, entry=entry, side=side,
            step=0.02, max_step=0.2, max_bars=192, bar_minutes=15,
        )
        assert full is not None and full["exit_reason"] == sar.REASON_TRAIL, (
            "fixture must actually produce a trail exit or it proves nothing"
        )
        exit_bar = full["exit_idx"]

        # Every truncation that still contains the exit bar must agree exactly.
        agreed = 0
        for n in range(exit_bar + 1, len(closes) + 1):
            early = sar.simulate_sar_exit(
                highs=highs[:n], lows=lows[:n], closes=closes[:n], opens=opens[:n],
                entry_idx=entry_idx, entry=entry, side=side,
                step=0.02, max_step=0.2, max_bars=192, bar_minutes=15,
            )
            assert early is not None
            assert early["exit_reason"] == sar.REASON_TRAIL
            assert early["exit_price"] == pytest.approx(full["exit_price"], rel=1e-12)
            assert early["exit_idx"] == full["exit_idx"]
            assert early["hold_min"] == pytest.approx(full["hold_min"], rel=1e-12)
            agreed += 1
        assert agreed > 0

    @pytest.mark.parametrize("seed,side", [(2, "LONG"), (5, "SHORT")])
    def test_before_the_exit_bar_the_walk_reports_window_not_a_trail(self, seed, side):
        """Which is exactly what classify_pending refuses to book mid-window."""
        drift = 0.5 if side == "LONG" else -0.5
        opens, highs, lows, closes = _walk(60, seed=seed, drift=drift)
        o2, h2, l2, c2 = _walk(140, seed=seed + 100, drift=-drift, start=closes[-1])
        opens, highs, lows, closes = opens + o2, highs + h2, lows + l2, closes + c2
        entry_idx, entry = 55, closes[55]

        full = sar.simulate_sar_exit(
            highs=highs, lows=lows, closes=closes, opens=opens,
            entry_idx=entry_idx, entry=entry, side=side,
            step=0.02, max_step=0.2, max_bars=192, bar_minutes=15,
        )
        assert full is not None and full["exit_reason"] == sar.REASON_TRAIL

        truncated = sar.simulate_sar_exit(
            highs=highs[:full["exit_idx"]], lows=lows[:full["exit_idx"]],
            closes=closes[:full["exit_idx"]], opens=opens[:full["exit_idx"]],
            entry_idx=entry_idx, entry=entry, side=side,
            step=0.02, max_step=0.2, max_bars=192, bar_minutes=15,
        )
        assert truncated is not None
        assert truncated["exit_reason"] == sar.REASON_WINDOW
