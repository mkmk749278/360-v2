"""Tests for the Strategy×Context edge matrix (src/strategy_edge.py, Layer C)."""
from __future__ import annotations

from src.strategy_edge import (
    VERDICT_INSUFFICIENT,
    VERDICT_NEGATIVE,
    VERDICT_STRONG,
    StrategyEdgeStore,
    StrategyOutcome,
)

CTX = "OVERLAP/MARKUP/EXPANDED/BTC_RISING"


def _win(r=1.5, pnl=1.2):
    return StrategyOutcome(
        strategy="S1", context_key=CTX, side="LONG", won=True,
        pnl_pct=pnl, r_multiple=r, mfe_pct=pnl,
    )


def _loss(r=-1.0, pnl=-0.8):
    return StrategyOutcome(
        strategy="S1", context_key=CTX, side="LONG", won=False,
        pnl_pct=pnl, r_multiple=r, mfe_pct=0.3,
    )


def test_insufficient_samples_return_none():
    store = StrategyEdgeStore(min_samples=15, persist_path="")
    for _ in range(5):
        store.record(_win())
    assert store.edge_r("S1", CTX) is None
    assert store.verdict("S1", CTX) == VERDICT_INSUFFICIENT
    assert store.sample_count("S1", CTX) == 5


def test_strong_positive_edge():
    store = StrategyEdgeStore(min_samples=10, persist_path="")
    for _ in range(20):
        store.record(_win(r=1.5))
    edge = store.edge_r("S1", CTX)
    assert edge is not None and edge > 0.25
    assert store.verdict("S1", CTX) == VERDICT_STRONG


def test_negative_edge_flags_losing_strategy():
    store = StrategyEdgeStore(min_samples=10, persist_path="")
    for _ in range(18):
        store.record(_loss())
    for _ in range(2):
        store.record(_win(r=1.0))
    edge = store.edge_r("S1", CTX)
    assert edge is not None and edge < 0
    assert store.verdict("S1", CTX) == VERDICT_NEGATIVE


def test_window_evicts_oldest():
    store = StrategyEdgeStore(window=10, min_samples=5, persist_path="")
    for _ in range(25):
        store.record(_win())
    assert store.sample_count("S1", CTX) == 10  # capped at window


def test_matrix_shape_and_capture():
    store = StrategyEdgeStore(min_samples=5, persist_path="")
    for _ in range(6):
        store.record(_win(r=1.0, pnl=1.0))
    m = store.matrix()
    cell = m[f"S1|{CTX}"]
    assert cell["strategy"] == "S1"
    assert cell["context_key"] == CTX
    assert cell["n"] == 6
    assert cell["win_rate"] == 1.0
    assert 0.0 < cell["mfe_capture"] <= 1.0
    assert cell["verdict"] in {VERDICT_STRONG, "POSITIVE"}


def test_persistence_round_trip(tmp_path):
    path = str(tmp_path / "edge.json")
    s1 = StrategyEdgeStore(min_samples=5, persist_path=path)
    for _ in range(8):
        s1.record(_win(r=1.2, pnl=1.1))
    # New store hydrates from disk.
    s2 = StrategyEdgeStore(min_samples=5, persist_path=path)
    assert s2.sample_count("S1", CTX) == 8
    assert s2.edge_r("S1", CTX) is not None


def test_empty_persist_path_disables_io():
    store = StrategyEdgeStore(min_samples=5, persist_path="")
    store.record(_win())
    assert store.sample_count("S1", CTX) == 1


def test_source_provenance_counts_in_matrix():
    from src.strategy_edge import SOURCE_SHADOW, SOURCE_SUPPRESSED

    store = StrategyEdgeStore(min_samples=1, persist_path="")
    store.record(_win())  # default source = emitted
    o = _win()
    o.source = SOURCE_SUPPRESSED
    store.record(o)
    o2 = _win()
    o2.source = SOURCE_SHADOW
    store.record(o2)
    cell = store.matrix()[f"S1|{CTX}"]
    assert cell["n"] == 3
    assert cell["n_emitted"] == 1
    assert cell["n_suppressed"] == 1
    assert cell["n_shadow"] == 1


def test_source_survives_persistence_round_trip(tmp_path):
    path = str(tmp_path / "edge.json")
    s1 = StrategyEdgeStore(min_samples=1, persist_path=path)
    o = _win()
    o.source = "shadow"
    s1.record(o)
    s2 = StrategyEdgeStore(min_samples=1, persist_path=path)
    assert s2.matrix()[f"S1|{CTX}"]["n_shadow"] == 1


def test_legacy_store_file_loads_as_emitted(tmp_path):
    import json

    path = tmp_path / "edge.json"
    path.write_text(json.dumps({
        f"S1|{CTX}": [
            {"won": True, "pnl_pct": 1.0, "r": 1.0, "mfe": 1.0,
             "ts": "2026-07-01T00:00:00+00:00"},
        ]
    }))
    store = StrategyEdgeStore(min_samples=1, persist_path=str(path))
    cell = store.matrix()[f"S1|{CTX}"]
    assert cell["n_emitted"] == 1 and cell["n_shadow"] == 0
