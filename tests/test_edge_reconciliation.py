"""W2 — realized-vs-counterfactual reconciliation + always-net observability.

The net R that feeds the reconciliation is computed *independently of* the cost-model
flag, so the optimism tax is visible whether or not the live path is netting.  And
``reconcile_matrix`` pools per-source net R into the realized (emitted) vs
counterfactual (suppressed) split the watchdog and truth report read.
"""
from __future__ import annotations

import config
import pytest
from src import suppression_audit as sa
from src.strategy_edge import (
    SOURCE_EMITTED,
    SOURCE_SUPPRESSED,
    StrategyEdgeStore,
    StrategyOutcome,
    reconcile_matrix,
)


def _pin_costs(monkeypatch, *, enabled: bool) -> None:
    monkeypatch.setattr(config, "EDGE_COST_MODEL_ENABLED", enabled, raising=False)
    monkeypatch.setattr(config, "EDGE_TAKER_FEE_PCT_ROUND_TRIP", 0.10, raising=False)
    monkeypatch.setattr(config, "EDGE_SLIPPAGE_PCT_PER_SIDE", 0.02, raising=False)
    monkeypatch.setattr(config, "EDGE_FUNDING_PCT_ESTIMATE", 0.01, raising=False)


def _win_record():
    return {
        "classification": "WOULD_WIN",
        "side": "LONG",
        "entry": 100.0,
        "tp1": 102.0,
        "stop_loss": 99.0,
        "sl_distance": 1.0,
    }


def test_net_r_multiple_is_computed_even_when_flag_off(monkeypatch):
    # Flag OFF: the LIVE r_multiple stays gross, but net_r_multiple is still the
    # cost-netted value — so the optimism tax is observable without going live.
    _pin_costs(monkeypatch, enabled=False)
    out = sa.candidate_outcome(_win_record())
    assert out["r_multiple"] == 2.0                       # live value = gross
    assert out["gross_r_multiple"] == 2.0
    assert out["net_r_multiple"] == pytest.approx(1.85)   # always netted


def test_net_r_multiple_matches_live_when_flag_on(monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    out = sa.candidate_outcome(_win_record())
    assert out["r_multiple"] == pytest.approx(1.85)
    assert out["net_r_multiple"] == pytest.approx(1.85)   # live == always-net


def test_edge_store_persists_and_reads_net_r(tmp_path, monkeypatch):
    _pin_costs(monkeypatch, enabled=True)
    store = StrategyEdgeStore(persist_path="", min_samples=1)
    store.record(StrategyOutcome(
        strategy="MEAN_REVERT", context_key="NY/RANGE", side="LONG",
        won=True, pnl_pct=1.0, r_multiple=1.5, gross_r_multiple=1.7, net_r_multiple=1.5,
        source=SOURCE_SUPPRESSED,
    ))
    cell = next(iter(store.matrix().values()))
    assert cell["avg_gross_r"] == pytest.approx(1.7)
    assert cell["avg_net_r"] == pytest.approx(1.5)
    assert cell["net_r_by_source"][SOURCE_SUPPRESSED] == pytest.approx(1.5)


def test_reconcile_matrix_splits_realized_vs_counterfactual():
    # Emitted (realized) underperforms the suppressed (counterfactual) — the tax.
    matrix = {
        "MEAN_REVERT|NY/RANGE": {
            "strategy": "MEAN_REVERT",
            "n_emitted": 30, "n_suppressed": 50,
            "net_r_by_source": {SOURCE_EMITTED: 0.10, SOURCE_SUPPRESSED: 0.45},
        },
    }
    recon = reconcile_matrix(matrix)["MEAN_REVERT"]
    assert recon["realized_net_r"] == pytest.approx(0.10)
    assert recon["counterfactual_net_r"] == pytest.approx(0.45)
    assert recon["delta_r"] == pytest.approx(-0.35)   # realized − counterfactual
    assert recon["realized_n"] == 30
    assert recon["counterfactual_n"] == 50


def test_reconcile_matrix_pools_across_cells_by_source_n():
    # Two contexts for the same strategy pool by each source's n (weighted mean).
    matrix = {
        "SR_FLIP_RETEST|A": {
            "strategy": "SR_FLIP_RETEST", "n_emitted": 10, "n_suppressed": 0,
            "net_r_by_source": {SOURCE_EMITTED: 0.0},
        },
        "SR_FLIP_RETEST|B": {
            "strategy": "SR_FLIP_RETEST", "n_emitted": 30, "n_suppressed": 0,
            "net_r_by_source": {SOURCE_EMITTED: 0.4},
        },
    }
    recon = reconcile_matrix(matrix)["SR_FLIP_RETEST"]
    # (10*0.0 + 30*0.4) / 40 = 0.30
    assert recon["realized_net_r"] == pytest.approx(0.30)
    assert recon["realized_n"] == 40
    assert recon["counterfactual_net_r"] is None
    assert recon["delta_r"] is None


def test_reconcile_matrix_skips_geometry_variants():
    matrix = {
        "MEAN_REVERT@ATR|NY/RANGE": {
            "strategy": "MEAN_REVERT@ATR", "n_emitted": 40, "n_suppressed": 40,
            "net_r_by_source": {SOURCE_EMITTED: 0.1, SOURCE_SUPPRESSED: 0.2},
        },
    }
    assert reconcile_matrix(matrix) == {}
