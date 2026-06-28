"""Per-symbol mover-path reason capture for the ops Pairs page.

When a promoted mover sits in the universe for hours but never fires, the ops
Pairs page needs to answer *why this cycle* (no_reclaim / mover_run_too_small /
fired) rather than leaving us to infer it from cumulative truth-report counters.
``ScalpChannel`` captures the last outcome of the two mover continuation paths
per symbol; these tests drive that capture directly.
"""
from __future__ import annotations

import time

import src.channels.scalp as scalp_mod
from src.channels.scalp import ScalpChannel


def test_records_and_summarises_primary_path_reject():
    ch = ScalpChannel()
    ch._record_mover_reason("GUAUSDT", "MOVER_TREND_PULLBACK", "no_reclaim")
    ch._record_mover_reason("GUAUSDT", "MOVER_AVWAP_SCALP", "no_pullback_tag")
    out = ch.mover_last_reasons()
    # MOVER_TREND_PULLBACK is the primary path → its reason wins the summary.
    assert out["GUAUSDT"]["reason"] == "no_reclaim"
    assert out["GUAUSDT"]["path"] == "MOVER_TREND_PULLBACK"
    assert out["GUAUSDT"]["age_sec"] >= 0.0


def test_fired_beats_a_reject_either_path():
    ch = ScalpChannel()
    ch._record_mover_reason("MUSDT", "MOVER_TREND_PULLBACK", "mover_run_too_small")
    ch._record_mover_reason("MUSDT", "MOVER_AVWAP_SCALP", "fired")
    out = ch.mover_last_reasons()
    assert out["MUSDT"]["reason"] == "fired"
    assert out["MUSDT"]["path"] == "MOVER_AVWAP_SCALP"


def test_avwap_used_when_no_primary_path_reason():
    ch = ScalpChannel()
    ch._record_mover_reason("ZROUSDT", "MOVER_AVWAP_SCALP", "slope_too_flat")
    out = ch.mover_last_reasons()
    assert out["ZROUSDT"]["reason"] == "slope_too_flat"
    assert out["ZROUSDT"]["path"] == "MOVER_AVWAP_SCALP"


def test_scanner_skip_is_surfaced():
    ch = ScalpChannel()
    ch.note_mover_skip("GUAUSDT", "spread_too_wide")
    out = ch.mover_last_reasons()
    assert out["GUAUSDT"]["reason"] == "spread_too_wide"
    assert out["GUAUSDT"]["path"] == "SCAN_SKIP"


def test_latest_outcome_wins_skip_then_eval():
    ch = ScalpChannel()
    # Cycle 1: skipped by the spread gate (never evaluated).
    ch.note_mover_skip("GUAUSDT", "spread_too_wide")
    # Cycle 2: spread tightened, the pair was evaluated and rejected for structure.
    ch._record_mover_reason("GUAUSDT", "MOVER_TREND_PULLBACK", "no_reclaim")
    out = ch.mover_last_reasons()
    assert out["GUAUSDT"]["reason"] == "no_reclaim"        # eval is newer → wins
    assert out["GUAUSDT"]["path"] == "MOVER_TREND_PULLBACK"


def test_latest_outcome_wins_eval_then_skip():
    ch = ScalpChannel()
    ch._record_mover_reason("GUAUSDT", "MOVER_TREND_PULLBACK", "no_reclaim")
    # Next cycle the spread blew out → skipped before evaluation.
    ch.note_mover_skip("GUAUSDT", "spread_too_wide")
    out = ch.mover_last_reasons()
    assert out["GUAUSDT"]["reason"] == "spread_too_wide"   # skip is newer → wins


def test_stale_entries_are_dropped(monkeypatch):
    ch = ScalpChannel()
    ch._record_mover_reason("OLDUSDT", "MOVER_TREND_PULLBACK", "no_ma_stack")
    # Age the entry past the TTL by rewinding its stored timestamp.
    ch._mover_last_reason["OLDUSDT"]["ts"] = (
        time.monotonic() - scalp_mod._MOVER_REASON_TTL_SEC - 1.0
    )
    assert "OLDUSDT" not in ch.mover_last_reasons()


def test_prune_keeps_dict_bounded():
    ch = ScalpChannel()
    old = time.monotonic() - scalp_mod._MOVER_REASON_TTL_SEC - 10.0
    # Seed >256 stale entries, then one fresh write triggers the prune path.
    for i in range(300):
        ch._mover_last_reason[f"S{i}USDT"] = {
            "MOVER_TREND_PULLBACK": "no_reclaim", "ts": old,
        }
    ch._record_mover_reason("FRESHUSDT", "MOVER_TREND_PULLBACK", "fired")
    # Stale entries pruned; the fresh one survives.
    assert "FRESHUSDT" in ch._mover_last_reason
    assert len(ch._mover_last_reason) < 300
