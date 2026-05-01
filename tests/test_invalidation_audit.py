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
