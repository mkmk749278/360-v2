"""Audit F2 (2026-07-18): the setup-compat and execution-quality hard gates
were the last reasonless rejects in the pre-scoring funnel.

A path 100%-killed at either showed only ``Gated == Generated,
classification (none)`` in the truth report — which is how MEAN_REVERT's
zero-emission (#739) stayed indistinguishable from the execution-gate bug
that #732 had already fixed.  These tests pin the new reason-tagged
``gate_reject:*`` funnel stages end-to-end: counter key contract →
snapshot parse → rendered report section.
"""
from __future__ import annotations

from collections import defaultdict

from src.runtime_truth_report import (
    build_snapshot,
    format_truth_report_markdown,
)


def _scanner_stub():
    from src.scanner import Scanner

    sc = Scanner.__new__(Scanner)
    sc._path_funnel_counters = defaultdict(int)
    sc._mean_revert_emitted_total = 0
    return sc


def _snapshot(funnel: dict):
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
        current_funnel=funnel,
        previous_funnel={},
        now_ts=1_000_000.0,
    )


class TestCounterKeyContract:
    def test_compat_and_execution_stages_land_under_setup(self):
        sc = _scanner_stub()
        sc._increment_path_funnel(
            "gate_reject:setup_compat:regime_BREAKOUT_EXPANSION",
            "360_SCALP",
            "MEAN_REVERT",
        )
        sc._increment_path_funnel(
            "gate_reject:execution:trigger_not_confirmed",
            "360_SCALP",
            "MEAN_REVERT",
        )
        keys = set(sc._path_funnel_counters)
        assert (
            "gate_reject:setup_compat:regime_BREAKOUT_EXPANSION:360_SCALP:"
            "mean_reversion:MEAN_REVERT" in keys
        )
        assert (
            "gate_reject:execution:trigger_not_confirmed:360_SCALP:"
            "mean_reversion:MEAN_REVERT" in keys
        )

    def test_gate_reject_stage_never_feeds_emission_probe(self):
        # The mean_revert_emission liveness probe counts ONLY 'emitted'.
        sc = _scanner_stub()
        sc._increment_path_funnel(
            "gate_reject:setup_compat:regime_CLEAN_RANGE",
            "360_SCALP",
            "MEAN_REVERT",
        )
        assert sc._mean_revert_emitted_total == 0


class TestTruthReportSection:
    def test_reasons_render_per_setup(self):
        funnel = {
            "generated:360_SCALP:mean_reversion:MEAN_REVERT": 100,
            "scanner_preparation:360_SCALP:mean_reversion:MEAN_REVERT": 100,
            "gated:360_SCALP:mean_reversion:MEAN_REVERT": 100,
            (
                "gate_reject:setup_compat:regime_BREAKOUT_EXPANSION:"
                "360_SCALP:mean_reversion:MEAN_REVERT"
            ): 70,
            (
                "gate_reject:setup_compat:regime_VOLATILE_UNSUITABLE:"
                "360_SCALP:mean_reversion:MEAN_REVERT"
            ): 25,
            (
                "gate_reject:execution:overextended:"
                "360_SCALP:mean_reversion:MEAN_REVERT"
            ): 5,
        }
        snapshot, comparison = _snapshot(funnel)
        path_truth = snapshot["path_funnel_truth"]["MEAN_REVERT"]
        assert path_truth["gate_reject_reasons"] == {
            "setup_compat:regime_BREAKOUT_EXPANSION": 70,
            "setup_compat:regime_VOLATILE_UNSUITABLE": 25,
            "execution:overextended": 5,
        }
        md = format_truth_report_markdown(snapshot, comparison)
        assert "## Pre-scoring gate rejects" in md
        # Sorted by count descending, the dominant MarketState is named —
        # the read that answers "which gate holds this path" directly.
        assert (
            "**MEAN_REVERT** (total=100): "
            "setup_compat:regime_BREAKOUT_EXPANSION=70, "
            "setup_compat:regime_VOLATILE_UNSUITABLE=25, "
            "execution:overextended=5"
        ) in md

    def test_cold_window_renders_placeholder(self):
        snapshot, comparison = _snapshot({})
        md = format_truth_report_markdown(snapshot, comparison)
        assert "## Pre-scoring gate rejects" in md
        assert "no pre-scoring gate rejects recorded in this window" in md
