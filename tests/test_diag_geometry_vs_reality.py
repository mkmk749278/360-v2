"""Tests for ``scripts/diag_geometry_vs_reality``.

The script is a one-shot operator diag, but the math (signed-pct from
direction, MFE/TP1 ratio, status filter, summary stats) needs to stay
correct so the conclusions an owner draws from it are sound.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest


def _load_script_module():
    """Load ``scripts/diag_geometry_vs_reality.py`` as a module — the file
    isn't on the package path so we load it directly by location."""
    here = Path(__file__).resolve().parent.parent
    path = here / "scripts" / "diag_geometry_vs_reality.py"
    spec = importlib.util.spec_from_file_location("diag_geometry_vs_reality", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def diag():
    return _load_script_module()


def test_signed_pct_long_target_above_entry(diag):
    """LONG with target above entry → positive favorable distance."""
    assert diag._signed_pct(100.0, 102.0, "LONG") == pytest.approx(2.0)


def test_signed_pct_short_target_below_entry(diag):
    """SHORT with target below entry → positive favorable distance."""
    assert diag._signed_pct(100.0, 98.0, "SHORT") == pytest.approx(2.0)


def test_signed_pct_wrong_side_returns_negative(diag):
    """LONG with target below entry → negative (target on wrong side)."""
    assert diag._signed_pct(100.0, 98.0, "LONG") == pytest.approx(-2.0)


def test_signed_pct_returns_none_on_invalid_inputs(diag):
    assert diag._signed_pct(0.0, 100.0, "LONG") is None
    assert diag._signed_pct(100.0, 0.0, "LONG") is None


def test_is_closed_recognises_terminal_statuses(diag):
    for status in (
        "SL_HIT", "PROFIT_LOCKED", "INVALIDATED", "EXPIRED",
        "FULL_TP_HIT", "TP3_HIT", "CLOSED", "BREAKEVEN_EXIT", "CANCELLED",
    ):
        assert diag._is_closed({"status": status}) is True


def test_is_closed_excludes_active_and_partial_progress(diag):
    """Active + TP1/TP2-progressing signals are NOT terminal — the sample
    must not include trades still in flight."""
    assert diag._is_closed({"status": "ACTIVE"}) is False
    assert diag._is_closed({"status": "TP1_HIT"}) is False
    assert diag._is_closed({"status": "TP2_HIT"}) is False


def test_summarise_computes_mfe_over_tp1_ratio(diag):
    """MFE/TP1 ratio is the killer diagnostic — verify the math.

    Two records, both LONG:
      A: TP1 +1.0% from entry, MFE +0.20%  → ratio 0.20
      B: TP1 +2.0% from entry, MFE +1.00%  → ratio 0.50
    Expected mean ratio: 0.35; mean MFE 0.60; mean TP1 dist 1.5.
    """
    records = [
        {
            "entry": 100.0, "tp1": 101.0, "direction": "LONG",
            "max_favorable_excursion_pct": 0.20,
            "max_adverse_excursion_pct": -0.05, "status": "EXPIRED",
        },
        {
            "entry": 50.0, "tp1": 51.0, "direction": "LONG",
            "max_favorable_excursion_pct": 1.00,
            "max_adverse_excursion_pct": -0.10, "status": "EXPIRED",
        },
    ]
    summary = diag._summarise(records)
    assert summary["n"] == 2
    assert summary["tp1_dist_mean"] == pytest.approx(1.5)
    assert summary["mfe_mean"] == pytest.approx(0.60)
    assert summary["mfe_over_tp1_mean"] == pytest.approx(0.35)


def test_summarise_handles_short_direction_and_status_mix(diag):
    """SHORT case with mixed terminal statuses populates the status mix."""
    records = [
        {
            "entry": 100.0, "tp1": 99.0, "direction": "SHORT",
            "max_favorable_excursion_pct": 0.50,
            "max_adverse_excursion_pct": -0.05, "status": "EXPIRED",
        },
        {
            "entry": 100.0, "tp1": 99.0, "direction": "SHORT",
            "max_favorable_excursion_pct": 1.20,
            "max_adverse_excursion_pct": -0.10, "status": "FULL_TP_HIT",
        },
    ]
    summary = diag._summarise(records)
    assert summary["n"] == 2
    # TP1 distance = 1% favorable for both SHORT records.
    assert summary["tp1_dist_mean"] == pytest.approx(1.0)
    assert summary["status_mix"] == {"EXPIRED": 1, "FULL_TP_HIT": 1}


def test_summarise_skips_invalid_records_in_ratio(diag):
    """Records missing entry / tp1 must NOT pollute the ratio average."""
    records = [
        {
            "entry": 0.0, "tp1": 100.0, "direction": "LONG",
            "max_favorable_excursion_pct": 0.5,
            "max_adverse_excursion_pct": -0.1, "status": "EXPIRED",
        },
        {
            "entry": 100.0, "tp1": 101.0, "direction": "LONG",
            "max_favorable_excursion_pct": 0.5,
            "max_adverse_excursion_pct": -0.1, "status": "EXPIRED",
        },
    ]
    summary = diag._summarise(records)
    # Only the second record contributes to MFE/TP1.
    assert summary["mfe_over_tp1_mean"] == pytest.approx(0.5)


def test_load_history_round_trip(diag, tmp_path: Path):
    p = tmp_path / "history.json"
    payload = [
        {"symbol": "BTCUSDT", "status": "EXPIRED", "entry": 80000.0},
    ]
    p.write_text(json.dumps(payload), encoding="utf-8")
    assert diag._load_history(str(p)) == payload
