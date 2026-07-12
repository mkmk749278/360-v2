"""Truth-report sections for the shadow ledger + edge matrix (Layer C/F)."""
from __future__ import annotations

import time

from src.runtime_truth_report import (
    build_snapshot,
    format_truth_report_markdown,
    summarize_strategy_edge,
    summarize_suppression_audit,
)

CTX = "OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL"


def _suppressed_record(cls: str = "WOULD_WIN", gate: str = "quiet_scalp_block") -> dict:
    return {
        "gate_name": gate,
        "setup_class": "BREAKOUT_RETEST",
        "symbol": "ETHUSDT",
        "channel": "360_SCALP",
        "side": "LONG",
        "entry": 100.0,
        "stop_loss": 99.0,
        "tp1": 101.5,
        "sl_distance": 1.0,
        "confidence": 70.0,
        "context_key": CTX,
        "regime": "TRENDING_UP",
        "valid_for_minutes": 45.0,
        "suppress_timestamp": time.time() - 7200,
        "classification": cls,
        "post_price_max": 102.0 if cls == "WOULD_WIN" else 100.2,
        "post_price_min": 99.8 if cls == "WOULD_WIN" else 98.5,
        "post_price_final": 101.9 if cls == "WOULD_WIN" else 98.6,
    }


def test_summarize_suppression_audit_counts_and_gates() -> None:
    records = [
        _suppressed_record("WOULD_WIN"),
        _suppressed_record("WOULD_LOSE", gate="regime_kill"),
        {**_suppressed_record(), "classification": None},  # pending
        "not-a-dict",
    ]
    out = summarize_suppression_audit(records)
    assert out["totals"]["WOULD_WIN"] == 1
    assert out["totals"]["WOULD_LOSE"] == 1
    assert out["pending"] == 1
    assert "quiet_scalp_block" in out["by_gate"]
    assert "regime_kill" in out["by_gate"]
    assert out["by_setup"]["BREAKOUT_RETEST"]["WOULD_WIN"] == 1


def test_summarize_suppression_audit_empty() -> None:
    out = summarize_suppression_audit([])
    assert out["totals"]["WOULD_WIN"] == 0
    assert out["by_gate"] == {}


def _matrix_cell(strategy: str, edge_r, n: int = 20, ctx: str = CTX) -> dict:
    return {
        "strategy": strategy,
        "context_key": ctx,
        "n": n,
        "n_emitted": 5,
        "n_suppressed": 10,
        "n_shadow": n - 15,
        "win_rate": 0.6,
        "avg_pnl_pct": 0.4,
        "avg_r": 0.3,
        "mfe_capture": 0.5,
        "edge_r": edge_r,
        "verdict": "POSITIVE" if (edge_r or 0) > 0 else "NEGATIVE",
        "last_updated": "2026-07-12T00:00:00+00:00",
    }


def test_summarize_strategy_edge_rollup() -> None:
    matrix = {
        f"A|{CTX}": _matrix_cell("A", 0.2),
        "A|ASIA/RANGE/NORMAL/BTC_NEUTRAL": _matrix_cell(
            "A", -0.1, ctx="ASIA/RANGE/NORMAL/BTC_NEUTRAL"
        ),
        f"B|{CTX}": _matrix_cell("B", None, n=3),
    }
    out = summarize_strategy_edge(matrix)
    a = out["per_strategy"]["A"]
    assert a["n"] == 40 and a["cells"] == 2
    assert a["best_cell"]["edge_r"] == 0.2
    assert a["worst_cell"]["edge_r"] == -0.1
    assert out["total_outcomes"] == 43
    assert out["scored_cells"] == 2
    assert out["top_cells"][0]["edge_r"] == 0.2
    assert out["bottom_cells"][0]["edge_r"] == -0.1


def test_summarize_strategy_edge_empty() -> None:
    out = summarize_strategy_edge({})
    assert out["per_strategy"] == {} and out["total_outcomes"] == 0


def _minimal_snapshot(**extra) -> tuple:
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
        **extra,
    )


def test_markdown_renders_populated_sections() -> None:
    suppression = summarize_suppression_audit(
        [_suppressed_record("WOULD_WIN") for _ in range(25)]
    )
    edge = summarize_strategy_edge({f"A|{CTX}": _matrix_cell("A", 0.2)})
    snapshot, comparison = _minimal_snapshot(
        suppression_audit=suppression, strategy_edge=edge
    )
    md = format_truth_report_markdown(snapshot, comparison)
    assert "## Suppression Quality Audit" in md
    assert "## Strategy × Context Edge Matrix" in md
    assert "quiet_scalp_block" in md
    assert "WOULD_WIN=25" in md
    assert "| A | 20 | 5/10/5 |" in md


def test_markdown_renders_cold_state_hints() -> None:
    snapshot, comparison = _minimal_snapshot()
    md = format_truth_report_markdown(snapshot, comparison)
    assert "## Suppression Quality Audit" in md
    assert "no classified suppressed candidates yet" in md
    assert "matrix is cold" in md


def test_tunables_registry_has_measurement_flags() -> None:
    from src.runtime_tunables import _build_registry

    reg = _build_registry()
    for key in (
        "market_context_enabled",
        "suppression_audit_enabled",
        "shadow_strategies_enabled",
        "allocator_recommend_enabled",
    ):
        assert key in reg, f"{key} not registered"
        assert reg[key].type == "bool"
        assert reg[key].category == "Measurement"
