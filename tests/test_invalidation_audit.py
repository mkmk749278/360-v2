"""Tests for src/invalidation_audit.py — the classifier that decides whether
trade-monitor kills are PROTECTIVE / PREMATURE / NEUTRAL.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from src.invalidation_audit import (
    InvalidationRecord,
    categorise_kill_reason,
    classify_pending_records,
    classify_record,
    compute_rule_ablation_metrics,
    load_classified_records,
    prune_old_records,
    record_invalidation,
)


# ────────────────────────────────────────────────────────────────────────
# categorise_kill_reason — must hold the contract used by the truth-report
# parser (low-cardinality reason families).
# ────────────────────────────────────────────────────────────────────────


def test_categorise_kill_reason_recognises_momentum_loss():
    text = "momentum loss (|momentum|=0.000 < 0.1, 2 consecutive readings) – signal thesis exhausted"
    assert categorise_kill_reason(text) == "momentum_loss"


def test_categorise_kill_reason_recognises_regime_shift():
    text = "regime shift to TRENDING_DOWN – LONG thesis no longer valid"
    assert categorise_kill_reason(text) == "regime_shift"


def test_categorise_kill_reason_recognises_ema_crossover():
    text = "EMA bearish crossover (EMA9 < EMA21) – LONG thesis invalidated"
    assert categorise_kill_reason(text) == "ema_crossover"


def test_categorise_kill_reason_falls_through_to_other():
    assert categorise_kill_reason("some unfamiliar reason") == "other"
    assert categorise_kill_reason("") == "other"
    assert categorise_kill_reason(None) == "other"  # type: ignore[arg-type]


# ────────────────────────────────────────────────────────────────────────
# classify_record — pure function, the heart of the audit.
# ────────────────────────────────────────────────────────────────────────


def _record(direction: str, entry: float, sl: float, tp1: float):
    return {
        "direction": direction,
        "entry": entry,
        "stop_loss": sl,
        "tp1": tp1,
        "sl_distance": abs(entry - sl),
    }


def test_classify_record_long_premature_when_post_kill_high_reaches_tp1():
    """LONG signal killed at +0.0%, post-kill price would have hit TP1."""
    rec = _record("LONG", entry=100.0, sl=99.0, tp1=101.0)  # SL distance = 1.0
    label = classify_record(rec, post_kill_high=101.5, post_kill_low=99.8, post_kill_close=101.2)
    assert label == "PREMATURE"


def test_classify_record_long_protective_when_post_kill_low_drops_beyond_threshold():
    """LONG killed near entry, then price drops 0.5R further — kill saved money."""
    # SL distance = 1.0, protective threshold = 0.3R below entry = 99.7
    rec = _record("LONG", entry=100.0, sl=99.0, tp1=101.0)
    label = classify_record(rec, post_kill_high=100.1, post_kill_low=99.4, post_kill_close=99.6)
    assert label == "PROTECTIVE"


def test_classify_record_long_neutral_when_price_stays_in_band():
    """LONG kill, price never reached TP1 nor dropped beyond -0.3R."""
    rec = _record("LONG", entry=100.0, sl=99.0, tp1=101.0)
    label = classify_record(rec, post_kill_high=100.4, post_kill_low=99.8, post_kill_close=100.1)
    assert label == "NEUTRAL"


def test_classify_record_short_premature_when_post_kill_low_reaches_tp1():
    """SHORT signal killed, post-kill low would have hit TP1 (which is below entry)."""
    rec = _record("SHORT", entry=100.0, sl=101.0, tp1=99.0)  # SL distance = 1.0
    label = classify_record(rec, post_kill_high=100.2, post_kill_low=98.5, post_kill_close=98.8)
    assert label == "PREMATURE"


def test_classify_record_short_protective_when_post_kill_high_rises_beyond_threshold():
    """SHORT kill, then price rises 0.5R further (against position) — kill protective."""
    rec = _record("SHORT", entry=100.0, sl=101.0, tp1=99.0)
    label = classify_record(rec, post_kill_high=100.5, post_kill_low=99.9, post_kill_close=100.4)
    assert label == "PROTECTIVE"


def test_classify_record_handles_zero_entry_or_sl_distance():
    """Defensive: bad input data returns INSUFFICIENT_DATA, never crashes."""
    rec_zero_entry = {"direction": "LONG", "entry": 0.0, "stop_loss": 99.0, "tp1": 101.0, "sl_distance": 1.0}
    assert classify_record(rec_zero_entry, 1, 1, 1) == "INSUFFICIENT_DATA"
    rec_zero_sl_dist = {"direction": "LONG", "entry": 100.0, "stop_loss": 99.0, "tp1": 101.0, "sl_distance": 0.0}
    assert classify_record(rec_zero_sl_dist, 1, 1, 1) == "INSUFFICIENT_DATA"


# ────────────────────────────────────────────────────────────────────────
# record_invalidation — persistence + asdict round-trip.
# ────────────────────────────────────────────────────────────────────────


def test_record_invalidation_writes_record_to_storage(tmp_path):
    storage = tmp_path / "audit.json"
    rec = record_invalidation(
        signal_id="SIG-1",
        symbol="BTCUSDT",
        channel="360_SCALP",
        setup_class="SR_FLIP_RETEST",
        direction="LONG",
        entry=100.0,
        stop_loss=99.0,
        tp1=101.0,
        kill_price=100.05,
        kill_reason="momentum loss (|momentum|=0.000 < 0.1, 2 consecutive readings) – signal thesis exhausted",
        pnl_pct_at_kill=0.05,
        storage_path=str(storage),
    )
    assert isinstance(rec, InvalidationRecord)
    assert rec.kill_reason_family == "momentum_loss"
    assert rec.sl_distance == pytest.approx(1.0)

    payload = json.loads(storage.read_text(encoding="utf-8"))
    assert len(payload) == 1
    assert payload[0]["signal_id"] == "SIG-1"
    assert payload[0]["classification"] is None  # awaiting classification


def test_record_invalidation_returns_none_on_invalid_input(tmp_path):
    """Defensive: 0-entry signals shouldn't poison the audit store."""
    storage = tmp_path / "audit.json"
    result = record_invalidation(
        signal_id="SIG-BAD", symbol="BTC", channel="360_SCALP",
        setup_class="X", direction="LONG",
        entry=0.0, stop_loss=99.0, tp1=101.0,
        kill_price=100.0, kill_reason="x", pnl_pct_at_kill=0.0,
        storage_path=str(storage),
    )
    assert result is None
    assert not storage.exists()


# ────────────────────────────────────────────────────────────────────────
# classify_pending_records — periodic worker integration.
# ────────────────────────────────────────────────────────────────────────


def _seed_pending_record(path: Path, *, kill_ts: float, **kwargs):
    base = {
        "signal_id": "SIG-X", "symbol": "BTCUSDT", "channel": "360_SCALP",
        "setup_class": "SR_FLIP_RETEST", "direction": "LONG",
        "entry": 100.0, "stop_loss": 99.0, "tp1": 101.0, "sl_distance": 1.0,
        "kill_price": 100.0, "kill_reason": "momentum loss",
        "kill_reason_family": "momentum_loss", "kill_timestamp": kill_ts,
        "pnl_pct_at_kill": 0.0, "classified_at": None, "classification": None,
    }
    base.update(kwargs)
    existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    existing.append(base)
    path.write_text(json.dumps(existing), encoding="utf-8")


def test_classify_pending_records_skips_records_inside_window(tmp_path):
    """A kill that happened 5 min ago is too fresh — skip until the window elapses."""
    storage = tmp_path / "audit.json"
    now = 1_000_000.0
    _seed_pending_record(storage, kill_ts=now - 300)  # 5 min ago

    counters = classify_pending_records(
        fetch_ohlc_since=lambda sym, ts: {"high": [101.5], "low": [99.8], "close": [101.2]},
        now_ts=now,
        storage_path=str(storage),
    )
    assert counters == {}
    payload = json.loads(storage.read_text(encoding="utf-8"))
    assert payload[0]["classification"] is None


def test_classify_pending_records_classifies_premature_long(tmp_path):
    """A kill 30+ min old where post-kill high reached TP1 → PREMATURE."""
    storage = tmp_path / "audit.json"
    now = 1_000_000.0
    _seed_pending_record(storage, kill_ts=now - 2000)  # >30 min ago

    counters = classify_pending_records(
        fetch_ohlc_since=lambda sym, ts: {"high": [101.5], "low": [99.8], "close": [101.2]},
        now_ts=now,
        storage_path=str(storage),
    )
    assert counters == {"PREMATURE": 1}
    payload = json.loads(storage.read_text(encoding="utf-8"))
    assert payload[0]["classification"] == "PREMATURE"
    assert payload[0]["post_kill_price_max"] == 101.5
    assert payload[0]["post_kill_price_min"] == 99.8


def test_classify_pending_records_marks_insufficient_data_when_ohlc_unavailable(tmp_path):
    """Symbol with no candle data yet → INSUFFICIENT_DATA, will never be retried."""
    storage = tmp_path / "audit.json"
    now = 1_000_000.0
    _seed_pending_record(storage, kill_ts=now - 2000)
    counters = classify_pending_records(
        fetch_ohlc_since=lambda sym, ts: None,
        now_ts=now,
        storage_path=str(storage),
    )
    assert counters == {"INSUFFICIENT_DATA": 1}


def test_classify_pending_records_skips_already_classified(tmp_path):
    """Idempotent: re-running over an already-classified record is a no-op."""
    storage = tmp_path / "audit.json"
    now = 1_000_000.0
    _seed_pending_record(storage, kill_ts=now - 2000, classification="PREMATURE", classified_at=now - 100)

    sentinel_calls = []

    def fetcher(sym, ts):
        sentinel_calls.append((sym, ts))
        return {"high": [99.0], "low": [98.0], "close": [98.5]}

    counters = classify_pending_records(
        fetch_ohlc_since=fetcher,
        now_ts=now,
        storage_path=str(storage),
    )
    assert counters == {}
    assert sentinel_calls == []  # fetcher not invoked


# ────────────────────────────────────────────────────────────────────────
# load_classified_records / prune_old_records.
# ────────────────────────────────────────────────────────────────────────


def test_load_classified_records_returns_only_classified(tmp_path):
    storage = tmp_path / "audit.json"
    now = 1_000_000.0
    _seed_pending_record(storage, kill_ts=now - 100, classification="PROTECTIVE", classified_at=now)
    _seed_pending_record(storage, kill_ts=now - 50)  # still pending

    classified = load_classified_records(str(storage))
    assert len(classified) == 1
    assert classified[0]["classification"] == "PROTECTIVE"


def test_prune_old_records_drops_records_older_than_retention(tmp_path):
    storage = tmp_path / "audit.json"
    now = 1_000_000.0
    # 8 days old — should be pruned
    _seed_pending_record(storage, kill_ts=now - 8 * 24 * 3600)
    # 1 hour old — should be kept
    _seed_pending_record(storage, kill_ts=now - 3600)

    pruned = prune_old_records(retention_sec=7 * 24 * 3600, now_ts=now, storage_path=str(storage))
    assert pruned == 1
    payload = json.loads(storage.read_text(encoding="utf-8"))
    assert len(payload) == 1


# ────────────────────────────────────────────────────────────────────────
# compute_rule_ablation_metrics — per-rule EV in R-units → DROP/TUNE/KEEP.
# OWNER_BRIEF B17 ablation question: "If we drop rule X, does the cohort's
# MFE-give-back get worse?"  EV/kill in R units is the only honest answer.
# ────────────────────────────────────────────────────────────────────────


def _ablation_record(
    *,
    family: str,
    classification: str,
    direction: str = "LONG",
    entry: float = 100.0,
    sl_distance: float = 1.0,
    tp1: float = 102.0,
    kill_price: float = 99.7,
    post_kill_min: float = 99.5,
    post_kill_max: float = 100.5,
):
    return {
        "kill_reason_family": family,
        "classification": classification,
        "direction": direction,
        "entry": entry,
        "sl_distance": sl_distance,
        "tp1": tp1,
        "kill_price": kill_price,
        "post_kill_price_min": post_kill_min,
        "post_kill_price_max": post_kill_max,
    }


def test_ablation_empty_records_returns_empty():
    result = compute_rule_ablation_metrics([])
    assert result["by_family"] == {}
    assert result["drop_candidates"] == []


def test_ablation_drop_when_premature_destroys_more_R_than_protective_saves():
    """Rule with 5 PROTECTIVE (each saves ~0.3R) vs 20 PREMATURE (each misses ~2R)
    is silently destroying edge: EV/kill = (5*0.3 - 20*2) / 25 = -1.54R/kill → DROP.
    Min sample = 5 (override) so the 25-record cohort qualifies.
    """
    records = []
    # 5 PROTECTIVE LONG kills: killed at -0.3R, would have dropped to -0.6R only
    # → saved 0.3R per kill (not full SL — counterfactual_R = -0.6).
    for _ in range(5):
        records.append(_ablation_record(
            family="momentum_loss",
            classification="PROTECTIVE",
            kill_price=99.7,        # R_at_kill = -0.3
            post_kill_min=99.4,     # counterfactual_R = -0.6
        ))
    # 20 PREMATURE LONG kills: killed at -0.0R, TP1 at +2R → missed 2R each.
    for _ in range(20):
        records.append(_ablation_record(
            family="momentum_loss",
            classification="PREMATURE",
            kill_price=100.0,       # R_at_kill = 0
            tp1=102.0,              # R_to_tp1 = +2
        ))
    result = compute_rule_ablation_metrics(records, min_sample_per_family=5)
    fam = result["by_family"]["momentum_loss"]
    assert fam["protective_n"] == 5
    assert fam["premature_n"] == 20
    assert fam["total"] == 25
    assert fam["saved_R_total"] == pytest.approx(5 * 0.3, abs=1e-6)
    assert fam["missed_R_total"] == pytest.approx(20 * 2.0, abs=1e-6)
    assert fam["ev_per_kill_R"] < -0.20
    assert fam["recommendation"] == "DROP"
    assert "momentum_loss" in result["drop_candidates"]


def test_ablation_keep_when_protective_dominates():
    """Rule with 20 PROTECTIVE (each saves ~0.8R via near-full-SL counterfactual)
    and 5 PREMATURE (each misses ~0.5R) → EV/kill clearly positive → KEEP.
    """
    records = []
    # 20 PROTECTIVE: killed at -0.2R, post-kill min crashed to -1.0R floor →
    # counterfactual_R = -1.0, saved_R = -0.2 - (-1.0) = +0.8 each.
    for _ in range(20):
        records.append(_ablation_record(
            family="regime_shift",
            classification="PROTECTIVE",
            kill_price=99.8,
            post_kill_min=98.5,  # post-kill below SL → floored at -1R
        ))
    # 5 PREMATURE: killed at +0.5R, TP1 at +1.0R → missed 0.5R each.
    for _ in range(5):
        records.append(_ablation_record(
            family="regime_shift",
            classification="PREMATURE",
            kill_price=100.5,
            tp1=101.0,
        ))
    result = compute_rule_ablation_metrics(records, min_sample_per_family=5)
    fam = result["by_family"]["regime_shift"]
    assert fam["saved_R_total"] == pytest.approx(20 * 0.8, abs=1e-6)
    assert fam["missed_R_total"] == pytest.approx(5 * 0.5, abs=1e-6)
    assert fam["ev_per_kill_R"] > 0.10
    assert fam["recommendation"] == "KEEP"
    assert "regime_shift" not in result["drop_candidates"]


def test_ablation_insufficient_sample_when_total_below_threshold():
    """Even a clearly-bleeding rule must not get a DROP recommendation
    when the classified cohort is too small to be confident."""
    records = [
        _ablation_record(family="ema_crossover", classification="PREMATURE",
                         kill_price=100.0, tp1=102.0)
        for _ in range(5)
    ]
    result = compute_rule_ablation_metrics(records, min_sample_per_family=20)
    fam = result["by_family"]["ema_crossover"]
    assert fam["total"] == 5
    assert fam["recommendation"] == "INSUFFICIENT_SAMPLE"
    assert result["drop_candidates"] == []


def test_ablation_tune_when_ev_is_marginal():
    """A rule sitting between -0.20 and +0.10 R/kill is not strongly bleeding
    nor strongly protecting; should surface as TUNE, not DROP/KEEP."""
    records = []
    # 10 PROTECTIVE saving ~0.4R each + 10 PREMATURE missing ~0.4R each →
    # EV ~ 0.0 → TUNE.
    for _ in range(10):
        records.append(_ablation_record(
            family="other",
            classification="PROTECTIVE",
            kill_price=99.8,
            post_kill_min=99.4,
        ))
    for _ in range(10):
        records.append(_ablation_record(
            family="other",
            classification="PREMATURE",
            kill_price=100.4,   # R_at_kill = +0.4
            tp1=100.8,          # R_to_tp1 = +0.8 → missed 0.4
        ))
    result = compute_rule_ablation_metrics(records, min_sample_per_family=20)
    fam = result["by_family"]["other"]
    assert fam["recommendation"] == "TUNE"
    assert "other" not in result["drop_candidates"]


def test_ablation_short_direction_math_mirrors_long():
    """SHORT kills must compute R-units with entry-price polarity flipped."""
    records = []
    # PREMATURE SHORT: entry=100, tp1=98 (R_to_tp1 = +2), killed at 100 (R_at_kill = 0).
    for _ in range(20):
        records.append(_ablation_record(
            family="trailing_invalidation",
            classification="PREMATURE",
            direction="SHORT",
            entry=100.0,
            sl_distance=1.0,
            tp1=98.0,
            kill_price=100.0,
        ))
    result = compute_rule_ablation_metrics(records, min_sample_per_family=20)
    fam = result["by_family"]["trailing_invalidation"]
    assert fam["missed_R_total"] == pytest.approx(20 * 2.0, abs=1e-6)
    assert fam["recommendation"] == "DROP"


def test_ablation_neutral_records_count_but_contribute_zero_ev():
    """NEUTRAL classifications still count toward sample size but their EV
    contribution is 0 (counterfactual is ambiguous when price stayed in band)."""
    records = [
        _ablation_record(family="momentum_loss", classification="NEUTRAL")
        for _ in range(25)
    ]
    result = compute_rule_ablation_metrics(records, min_sample_per_family=20)
    fam = result["by_family"]["momentum_loss"]
    assert fam["neutral_n"] == 25
    assert fam["saved_R_total"] == 0.0
    assert fam["missed_R_total"] == 0.0
    assert fam["ev_per_kill_R"] == 0.0
    assert fam["recommendation"] == "TUNE"
