"""Stop-geometry A/B measurement (Phase 3 item 8) — math, pairing, wiring.

The doctrine scenario under test throughout: a fixed-% stop sitting inside the
15m noise band gets clipped by a wick the ATR/structure stop survives, and the
pair ledger measures exactly that difference per (strategy, context).
"""
from __future__ import annotations

import time
from types import SimpleNamespace

import pytest

from src import geometry_ab as gab
from src.geometry_ab import (
    ATR_SUFFIX,
    FIXED_SUFFIX,
    GATE_ATR,
    GATE_FIXED,
    base_strategy,
    compute_atr_structure_stop,
    is_geometry_variant,
    stamp_geometry_pair,
    summarize_geometry_ab,
)
from src.scanner import Scanner
from src.smc import Direction
from src.strategy_allocator import recommend
from src.suppression_audit import SuppressedCandidateStore

CTX = "OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL"


def _candles(n: int = 40, close: float = 100.0, spread: float = 0.5, **over):
    """Flat tape: TR = 2*spread every bar → ATR = 2*spread exactly."""
    highs = [close + spread] * n
    lows = [close - spread] * n
    closes = [close] * n
    for idx, v in (over.get("low_overrides") or {}).items():
        lows[idx] = v
    for idx, v in (over.get("high_overrides") or {}).items():
        highs[idx] = v
    return highs, lows, closes


@pytest.fixture()
def fresh_geometry_store(monkeypatch):
    store = SuppressedCandidateStore(persist_path="")
    monkeypatch.setattr(gab, "_geometry_store", store)
    monkeypatch.setattr(gab, "_last_pair_stamp", {})
    return store


class TestComputeAtrStructureStop:
    def test_long_atr_dominant(self):
        highs, lows, closes = _candles()  # ATR = 1.0, pool = 99.5
        stop = compute_atr_structure_stop(
            side="LONG", entry=100.0, highs=highs, lows=lows, closes=closes
        )
        # atr_dist 1.5 > pool_dist 0.5 + buffer 0.05 → 100 − 1.5
        assert stop == pytest.approx(98.5)

    def test_long_structure_dominant(self):
        highs, lows, closes = _candles(low_overrides={30: 97.0})
        stop = compute_atr_structure_stop(
            side="LONG", entry=100.0, highs=highs, lows=lows, closes=closes
        )
        # pool 97.0 → dist 3.0 + 0.05 buffer beats atr_dist ~1.5ish
        assert stop == pytest.approx(96.95, abs=0.02)

    def test_short_mirror(self):
        highs, lows, closes = _candles(high_overrides={35: 103.0})
        stop = compute_atr_structure_stop(
            side="SHORT", entry=100.0, highs=highs, lows=lows, closes=closes
        )
        assert stop == pytest.approx(103.05, abs=0.02)

    def test_sanity_clamp_returns_none(self):
        highs, lows, closes = _candles(low_overrides={30: 92.0})  # 8% pool
        assert (
            compute_atr_structure_stop(
                side="LONG", entry=100.0, highs=highs, lows=lows, closes=closes
            )
            is None
        )

    def test_no_atr_returns_none(self):
        highs, lows, closes = _candles(spread=0.0)  # zero true range
        assert (
            compute_atr_structure_stop(
                side="LONG", entry=100.0, highs=highs, lows=lows, closes=closes
            )
            is None
        )

    def test_insufficient_bars_and_bad_inputs(self):
        highs, lows, closes = _candles(n=5)
        assert (
            compute_atr_structure_stop(
                side="LONG", entry=100.0, highs=highs, lows=lows, closes=closes
            )
            is None
        )
        highs, lows, closes = _candles()
        assert (
            compute_atr_structure_stop(
                side="SIDEWAYS", entry=100.0, highs=highs, lows=lows, closes=closes
            )
            is None
        )
        assert (
            compute_atr_structure_stop(
                side="LONG", entry=0.0, highs=highs, lows=lows, closes=closes
            )
            is None
        )


class TestVariantHelpers:
    def test_round_trip(self):
        assert is_geometry_variant("SR_FLIP_RETEST@ATR")
        assert is_geometry_variant("SR_FLIP_RETEST@FIXED")
        assert not is_geometry_variant("SR_FLIP_RETEST")
        assert not is_geometry_variant("")
        assert base_strategy("MOVER_TREND_PULLBACK@ATR") == "MOVER_TREND_PULLBACK"
        assert base_strategy("MOVER_TREND_PULLBACK@FIXED") == "MOVER_TREND_PULLBACK"
        assert base_strategy("MOVER_TREND_PULLBACK") == "MOVER_TREND_PULLBACK"


def _stamp(store, **over):
    highs, lows, closes = _candles()
    kwargs = dict(
        symbol="ETHUSDT",
        channel="360_SCALP",
        setup_class="SR_FLIP_RETEST",
        side="LONG",
        entry=100.0,
        stop_loss=99.0,
        tp1=101.5,
        highs=highs,
        lows=lows,
        closes=closes,
        confidence=70.0,
        context_key=CTX,
        regime="TRENDING_UP",
        valid_for_minutes=45.0,
        store=store,
    )
    kwargs.update(over)
    return stamp_geometry_pair(**kwargs)


class TestStampGeometryPair:
    def test_stamps_both_arms(self, fresh_geometry_store):
        alt = _stamp(fresh_geometry_store)
        assert alt == pytest.approx(98.5)
        recs = fresh_geometry_store.records()
        assert len(recs) == 2
        fixed = next(r for r in recs if r["gate_name"] == GATE_FIXED)
        atr = next(r for r in recs if r["gate_name"] == GATE_ATR)
        assert fixed["setup_class"] == f"SR_FLIP_RETEST{FIXED_SUFFIX}"
        assert atr["setup_class"] == f"SR_FLIP_RETEST{ATR_SUFFIX}"
        # Same thesis on both arms — only the stop differs.
        assert fixed["entry"] == atr["entry"] == 100.0
        assert fixed["tp1"] == atr["tp1"] == 101.5
        assert fixed["stop_loss"] == 99.0
        assert atr["stop_loss"] == pytest.approx(98.5)
        assert fixed["context_key"] == atr["context_key"] == CTX

    def test_cooldown_blocks_repeat_pair(self, fresh_geometry_store):
        assert _stamp(fresh_geometry_store, now_mono=1000.0) is not None
        assert _stamp(fresh_geometry_store, now_mono=1030.0) is None
        assert len(fresh_geometry_store.records()) == 2
        # Different symbol is its own cooldown key.
        assert _stamp(fresh_geometry_store, symbol="SOLUSDT", now_mono=1030.0) is not None
        assert len(fresh_geometry_store.records()) == 4

    def test_no_pair_when_atr_arm_uncomputable(self, fresh_geometry_store):
        highs, lows, closes = _candles(spread=0.0)
        assert (
            _stamp(fresh_geometry_store, highs=highs, lows=lows, closes=closes) is None
        )
        assert fresh_geometry_store.records() == []

    def test_refuses_variant_setup_and_bad_geometry(self, fresh_geometry_store):
        assert _stamp(fresh_geometry_store, setup_class="X@ATR") is None
        assert _stamp(fresh_geometry_store, tp1=0.0) is None
        assert _stamp(fresh_geometry_store, entry=0.0) is None
        assert fresh_geometry_store.records() == []


class _FakeScanner:
    """Just enough Scanner surface for the two stamp entry points."""

    _stamp_geometry_ab = Scanner._stamp_geometry_ab
    _stamp_suppressed = Scanner._stamp_suppressed

    def __init__(self, candles):
        self.data_store = SimpleNamespace(get_candles=lambda sym, tf: candles)


def _sig(**over):
    base = dict(
        symbol="ETHUSDT",
        channel="360_SCALP",
        setup_class="SR_FLIP_RETEST",
        direction=Direction.LONG,
        entry=100.0,
        stop_loss=99.0,
        tp1=101.5,
        confidence=70.0,
        mc_context_key=CTX,
        entry_regime="TRENDING_UP",
        valid_for_minutes=45.0,
        geo_atr_stop=0.0,
    )
    base.update(over)
    return SimpleNamespace(**base)


class TestScannerWiring:
    def _candle_dict(self):
        highs, lows, closes = _candles()
        return {"high": highs, "low": lows, "close": closes}

    def test_stamps_and_marks_signal_when_enabled(
        self, fresh_geometry_store, monkeypatch
    ):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        scanner = _FakeScanner(self._candle_dict())
        sig = _sig()
        scanner._stamp_geometry_ab(sig)
        assert len(fresh_geometry_store.records()) == 2
        assert sig.geo_atr_stop == pytest.approx(98.5)

    def test_no_stamp_when_tunable_off(self, fresh_geometry_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(
            runtime_tunables,
            "get",
            lambda key: key != "geometry_ab_enabled",
        )
        scanner = _FakeScanner(self._candle_dict())
        sig = _sig()
        scanner._stamp_geometry_ab(sig)
        assert fresh_geometry_store.records() == []
        assert sig.geo_atr_stop == 0.0

    def test_suppressed_path_stamps_pair_even_with_audit_off(
        self, fresh_geometry_store, monkeypatch
    ):
        # geometry_ab has its own tunable — suppression_audit OFF must not
        # starve the A/B of its suppressed-candidate half.
        from src import runtime_tunables
        monkeypatch.setattr(
            runtime_tunables,
            "get",
            lambda key: key == "geometry_ab_enabled",
        )
        scanner = _FakeScanner(self._candle_dict())
        scanner._stamp_suppressed(_sig(), "dispatch_staleness")
        assert len(fresh_geometry_store.records()) == 2

    def test_fail_open_on_garbage(self, fresh_geometry_store, monkeypatch):
        from src import runtime_tunables
        monkeypatch.setattr(runtime_tunables, "get", lambda key: True)
        scanner = _FakeScanner(None)  # data store returns None
        scanner._stamp_geometry_ab(_sig())
        scanner._stamp_geometry_ab(object())
        # And the legacy bare-object self path must stay safe too.
        Scanner._stamp_suppressed(object(), _sig(), "regime_kill")


class TestClassifyDoctrineScenario:
    def test_noise_clips_fixed_arm_but_not_atr_arm(self, fresh_geometry_store):
        """The wick dips to 98.7 then price runs to TP: fixed (99.0) stops out,
        ATR/structure (98.5) survives and wins — the doctrine's exact claim,
        measured by the same classifier the suppression audit uses."""
        _stamp(fresh_geometry_store)

        def fetch_ohlc_since(symbol, since_ts):
            return {"high": [102.0], "low": [98.7], "close": [101.9]}

        fresh_geometry_store.classify_pending(
            fetch_ohlc_since=fetch_ohlc_since,
            now_ts=time.time() + 7200,
        )
        recs = fresh_geometry_store.records()
        by_gate = {r["gate_name"]: r for r in recs}
        assert by_gate[GATE_FIXED]["classification"] == "WOULD_LOSE"
        assert by_gate[GATE_ATR]["classification"] == "WOULD_WIN"


class TestAllocatorExclusion:
    def test_variant_rows_never_recommended(self):
        cell = {
            "strategy": "SR_FLIP_RETEST@ATR",
            "context_key": CTX,
            "n": 50,
            "n_emitted": 0,
            "win_rate": 0.9,
            "avg_r": 1.0,
            "edge_r": 0.8,
            "verdict": "STRONG",
        }
        out = recommend(CTX, {f"SR_FLIP_RETEST@ATR|{CTX}": cell})
        assert out["activate"] == []
        assert out["demote"] == []

    def test_base_rows_still_recommended(self):
        cell = {
            "strategy": "SR_FLIP_RETEST",
            "context_key": CTX,
            "n": 50,
            "n_emitted": 5,
            "win_rate": 0.9,
            "avg_r": 1.0,
            "edge_r": 0.8,
            "verdict": "STRONG",
        }
        out = recommend(CTX, {f"SR_FLIP_RETEST|{CTX}": cell})
        assert [r["strategy"] for r in out["activate"]] == ["SR_FLIP_RETEST"]


def _matrix_cell(strategy: str, n: int, win_rate: float, avg_r: float, ctx: str = CTX):
    return {
        "strategy": strategy,
        "context_key": ctx,
        "n": n,
        "n_emitted": 0,
        "n_suppressed": 0,
        "n_shadow": n,
        "win_rate": win_rate,
        "avg_pnl_pct": 0.0,
        "avg_r": avg_r,
        "mfe_capture": 0.0,
        "edge_r": None,
        "verdict": "INSUFFICIENT_DATA",
        "last_updated": "2026-07-13T00:00:00+00:00",
    }


class TestSummarizeGeometryAb:
    def test_pools_arms_and_names_leader(self):
        matrix = {
            f"A@FIXED|{CTX}": _matrix_cell("A@FIXED", 20, 0.40, -0.20),
            "A@FIXED|X2": _matrix_cell("A@FIXED", 10, 0.40, -0.20, ctx="X2"),
            f"A@ATR|{CTX}": _matrix_cell("A@ATR", 20, 0.60, 0.30),
            "A@ATR|X2": _matrix_cell("A@ATR", 10, 0.60, 0.30, ctx="X2"),
            # Thin arm → MEASURING, no leader named.
            f"B@FIXED|{CTX}": _matrix_cell("B@FIXED", 30, 0.5, 0.1),
            f"B@ATR|{CTX}": _matrix_cell("B@ATR", 3, 1.0, 2.0),
            # Non-variant rows are ignored here.
            f"A|{CTX}": _matrix_cell("A", 99, 0.5, 0.5),
        }
        rows = summarize_geometry_ab(matrix, min_sample=15)
        by_name = {r["strategy"]: r for r in rows}
        a = by_name["A"]
        assert a["fixed"]["n"] == 30 and a["atr"]["n"] == 30
        assert a["delta_r"] == pytest.approx(0.5)
        assert a["leader"] == "ATR"
        b = by_name["B"]
        assert b["leader"] == "MEASURING" and b["delta_r"] is None
        # Sorted by |ΔR|: the measured A/B outranks the unmeasured one.
        assert rows[0]["strategy"] == "A"

    def test_empty_matrix(self):
        assert summarize_geometry_ab({}) == []


class TestTruthReportSection:
    def test_variants_excluded_from_strategy_rollup_and_section_renders(self):
        from src.runtime_truth_report import summarize_strategy_edge

        matrix = {
            f"A|{CTX}": _matrix_cell("A", 20, 0.6, 0.3),
            f"A@FIXED|{CTX}": _matrix_cell("A@FIXED", 20, 0.4, -0.2),
            f"A@ATR|{CTX}": _matrix_cell("A@ATR", 20, 0.6, 0.3),
        }
        out = summarize_strategy_edge(matrix)
        assert set(out["per_strategy"].keys()) == {"A"}
        assert out["total_outcomes"] == 20  # variants not double-counted
        ab = out["geometry_ab"]
        assert len(ab) == 1 and ab[0]["strategy"] == "A"

    def test_markdown_renders_populated_and_cold(self):
        from src.runtime_truth_report import (
            build_snapshot,
            format_truth_report_markdown,
            summarize_strategy_edge,
        )

        def snap(edge):
            return build_snapshot(
                channel="360_SCALP",
                lookback_hours=24,
                compare_previous_window=False,
                include_raw_json=False,
                symbol_filter="",
                setup_filter="",
                runtime_health={"running": True, "status": "running", "health": "healthy"},
                heartbeat_text="Heartbeat age: 30s",
                records=[],
                current_funnel={},
                previous_funnel={},
                now_ts=1_000_000.0,
                strategy_edge=edge,
            )

        edge = summarize_strategy_edge(
            {
                f"A@FIXED|{CTX}": _matrix_cell("A@FIXED", 30, 0.4, -0.2),
                f"A@ATR|{CTX}": _matrix_cell("A@ATR", 30, 0.6, 0.3),
            }
        )
        snapshot, comparison = snap(edge)
        md = format_truth_report_markdown(snapshot, comparison)
        assert "## Stop-Geometry A/B" in md
        assert "**ATR**" in md

        snapshot, comparison = snap(summarize_strategy_edge({}))
        md = format_truth_report_markdown(snapshot, comparison)
        assert "## Stop-Geometry A/B" in md
        assert "no geometry pairs classified yet" in md
