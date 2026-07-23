"""Tests for the Suppression Quality Audit / shadow ledger (src/suppression_audit.py)."""
from __future__ import annotations

import config
import pytest

from src import suppression_audit as sa


@pytest.fixture(autouse=True)
def _gross_edge_defaults(monkeypatch):
    # These assert the gross geometry→R mapping; the cost model (now live by
    # default) is covered in test_trade_costs.py / test_edge_reconciliation.py.
    monkeypatch.setattr(config, "EDGE_COST_MODEL_ENABLED", False, raising=False)


def _rec(side="LONG", entry=100.0, sl=99.0, tp1=102.0, gate="quiet_scalp_block",
         vfm=0.0, ts=1000.0):
    return {
        "gate_name": gate, "setup_class": "SR_FLIP_RETEST", "symbol": "BTCUSDT",
        "channel": "360_SCALP", "side": side, "entry": entry, "stop_loss": sl,
        "tp1": tp1, "sl_distance": abs(entry - sl), "confidence": 60.0,
        "context_key": "OVERLAP/RANGE/NORMAL/BTC_NEUTRAL", "regime": "RANGING",
        "valid_for_minutes": vfm, "suppress_timestamp": ts,
        "classification": None,
    }


# --------------------------------------------------------------- pure classifier
def test_long_would_win_tp_before_sl():
    r = _rec(side="LONG", entry=100, sl=99, tp1=102)
    assert sa.classify_suppressed_record(r, post_high=102.5, post_low=99.5) == sa.WOULD_WIN


def test_long_would_lose_sl_hit():
    r = _rec(side="LONG", entry=100, sl=99, tp1=102)
    assert sa.classify_suppressed_record(r, post_high=101.0, post_low=98.9) == sa.WOULD_LOSE


def test_both_breached_is_conservative_lose():
    r = _rec(side="LONG", entry=100, sl=99, tp1=102)
    # Both TP1 and SL touched in the window -> SL-first assumption.
    assert sa.classify_suppressed_record(r, post_high=102.5, post_low=98.5) == sa.WOULD_LOSE


def test_would_expire_neither_touched():
    r = _rec(side="LONG", entry=100, sl=99, tp1=102)
    assert sa.classify_suppressed_record(r, post_high=101.0, post_low=99.5) == sa.WOULD_EXPIRE


def test_short_mirror():
    r = _rec(side="SHORT", entry=100, sl=101, tp1=98)
    assert sa.classify_suppressed_record(r, post_high=100.5, post_low=97.5) == sa.WOULD_WIN
    assert sa.classify_suppressed_record(r, post_high=101.5, post_low=99.0) == sa.WOULD_LOSE


def test_insufficient_geometry():
    r = _rec(entry=0, sl=0, tp1=0)
    assert sa.classify_suppressed_record(r, 1, 1) == sa.INSUFFICIENT


# ------------------------------------------------------------------- R math / EV
def test_suppression_value_delta_signs():
    win = _rec(); win["classification"] = sa.WOULD_WIN
    lose = _rec(); lose["classification"] = sa.WOULD_LOSE
    exp = _rec(); exp["classification"] = sa.WOULD_EXPIRE
    assert sa.suppression_value_delta_r(lose) == 1.0            # saved a stop
    assert sa.suppression_value_delta_r(win) == -2.0           # R_to_tp1 = 2/1
    assert sa.suppression_value_delta_r(exp) == 0.0
    assert sa.suppression_value_delta_r(_rec()) is None        # unclassified


def test_candidate_outcome_maps_to_edge_fields():
    win = _rec(); win["classification"] = sa.WOULD_WIN
    out = sa.candidate_outcome(win)
    assert out["won"] is True and out["r_multiple"] == 2.0


# ---------------------------------------------------------- gate ablation verdicts
def test_gate_metrics_keep_when_suppressing_losers():
    recs = []
    for _ in range(25):
        r = _rec(); r["classification"] = sa.WOULD_LOSE
        recs.append(r)
    m = sa.compute_gate_suppression_metrics(recs)
    g = m["quiet_scalp_block"]
    assert g["verdict"] == sa.VERDICT_KEEP
    assert g["ev_per_suppression_r"] > 0


def test_gate_metrics_drop_when_killing_winners():
    recs = []
    for _ in range(25):
        r = _rec(); r["classification"] = sa.WOULD_WIN
        recs.append(r)
    m = sa.compute_gate_suppression_metrics(recs)
    g = m["quiet_scalp_block"]
    assert g["verdict"] == sa.VERDICT_DROP
    assert g["would_win_pct"] == 100.0


def test_gate_metrics_insufficient_below_floor():
    recs = [dict(_rec(), classification=sa.WOULD_LOSE) for _ in range(3)]
    m = sa.compute_gate_suppression_metrics(recs)
    assert m["quiet_scalp_block"]["verdict"] == sa.VERDICT_INSUFFICIENT


# ---------------------------------------------------------------- store behaviour
def test_stamp_scopes_to_geometry_and_is_o1(tmp_path):
    store = sa.SuppressedCandidateStore(persist_path="")
    # No geometry -> not stamped.
    assert sa.stamp_candidate(
        gate_name="g", symbol="X", channel="c", setup_class="S", side="LONG",
        entry=0, stop_loss=0, tp1=0, store=store,
    ) is None
    # Valid geometry -> stamped.
    rec = sa.stamp_candidate(
        gate_name="dispatch_cooldown", symbol="ETHUSDT", channel="360_SCALP",
        setup_class="MOVER_TREND_PULLBACK", side="LONG",
        entry=100, stop_loss=99, tp1=103, store=store,
    )
    assert rec is not None
    assert store.pending_count() == 1


def test_stamp_never_writes_on_hot_path(tmp_path, monkeypatch):
    # With persist disabled, stamping must do zero file I/O.
    store = sa.SuppressedCandidateStore(persist_path="")

    def _boom(*a, **k):
        raise AssertionError("stamp must not open files")

    monkeypatch.setattr("builtins.open", _boom)
    rec = sa.stamp_candidate(
        gate_name="g", symbol="X", channel="c", setup_class="S", side="LONG",
        entry=100, stop_loss=99, tp1=102, store=store,
    )
    assert rec is not None and store.pending_count() == 1


def test_classify_pending_matures_and_hooks_edge(tmp_path):
    store = sa.SuppressedCandidateStore(persist_path=str(tmp_path / "s.json"))
    sa.stamp_candidate(
        gate_name="level_still_in_play", symbol="BTCUSDT", channel="360_SCALP",
        setup_class="SR_FLIP_RETEST", side="LONG",
        entry=100, stop_loss=99, tp1=102, store=store,
    )
    seen = []

    def ohlc(symbol, since):
        return {"high": [102.5], "low": [99.5], "close": [102.1]}

    # now well past the window so the record matures.
    counters = store.classify_pending(
        fetch_ohlc_since=ohlc, now_ts=1e12,
        on_classified=lambda r: seen.append(sa.candidate_outcome(r)),
    )
    assert counters.get(sa.WOULD_WIN) == 1
    assert seen and seen[0]["won"] is True
    assert store.pending_count() == 0


def test_classify_pending_waits_inside_window(tmp_path):
    store = sa.SuppressedCandidateStore(persist_path="")
    sa.stamp_candidate(
        gate_name="g", symbol="BTCUSDT", channel="c", setup_class="S", side="LONG",
        entry=100, stop_loss=99, tp1=102, store=store,
    )
    # now_ts only 10s after stamp -> still inside the 3600s window.
    import time as _t
    counters = store.classify_pending(
        fetch_ohlc_since=lambda s, t: {"high": [103], "low": [98], "close": [100]},
        now_ts=_t.time() + 10,
    )
    assert counters == {}
    assert store.pending_count() == 1


def test_insufficient_when_no_ohlc(tmp_path):
    store = sa.SuppressedCandidateStore(persist_path="")
    sa.stamp_candidate(
        gate_name="g", symbol="BTCUSDT", channel="c", setup_class="S", side="LONG",
        entry=100, stop_loss=99, tp1=102, store=store,
    )
    counters = store.classify_pending(
        fetch_ohlc_since=lambda s, t: None, now_ts=1e12,
    )
    assert counters.get(sa.INSUFFICIENT) == 1


# ------------------------------------------------- limit-entry (fill-aware) arms
def _limit_rec(side="LONG", entry=100.0, sl=98.0, tp1=103.0):
    r = _rec(side=side, entry=entry, sl=sl, tp1=tp1, gate="tuned_variant:MTP")
    r["entry_type"] = sa.ENTRY_LIMIT
    return r


def test_limit_long_fill_then_win():
    # Candle 1 dips to the limit (no stop breach), candle 2 reaches TP1.
    label = sa.classify_limit_record(
        _limit_rec(), highs=[100.5, 103.5], lows=[99.8, 100.2]
    )
    assert label == sa.WOULD_WIN


def test_limit_long_never_filled_is_not_fill():
    # Price runs to TP without ever touching the resting limit — the immediate
    # classifier would flatter this as a WIN; the limit walk must not.
    label = sa.classify_limit_record(
        _limit_rec(), highs=[104.0, 105.0], lows=[100.5, 103.0]
    )
    assert label == sa.WOULD_NOT_FILL


def test_limit_long_fill_candle_stop_breach_is_lose():
    # The candle that touches the limit also trades through the stop —
    # conservative fill-then-stop, even though a later candle reaches TP.
    label = sa.classify_limit_record(
        _limit_rec(), highs=[100.5, 104.0], lows=[97.5, 100.0]
    )
    assert label == sa.WOULD_LOSE


def test_limit_long_fill_candle_spans_tp_with_stop_intact_is_win():
    label = sa.classify_limit_record(
        _limit_rec(), highs=[103.5], lows=[99.9]
    )
    assert label == sa.WOULD_WIN


def test_limit_long_filled_then_neither_is_expire():
    label = sa.classify_limit_record(
        _limit_rec(), highs=[100.4, 101.0], lows=[99.9, 99.5]
    )
    assert label == sa.WOULD_EXPIRE


def test_limit_short_mirror():
    # SHORT limit above market: entry 100, SL 102, TP1 97.
    rec = _limit_rec(side="SHORT", entry=100.0, sl=102.0, tp1=97.0)
    # Candle 1 pops to the limit, candle 2 drops to target.
    assert sa.classify_limit_record(rec, highs=[100.2, 99.0], lows=[99.0, 96.8]) == sa.WOULD_WIN
    # Never touches the limit from below → no fill.
    assert sa.classify_limit_record(rec, highs=[99.5, 98.0], lows=[97.0, 96.5]) == sa.WOULD_NOT_FILL
    # Fill candle also breaches the stop → conservative lose.
    assert sa.classify_limit_record(rec, highs=[102.5, 96.0], lows=[99.9, 95.0]) == sa.WOULD_LOSE


def test_limit_degenerate_geometry_insufficient():
    rec = _limit_rec()
    rec["stop_loss"] = 0.0
    rec["sl_distance"] = 0.0
    assert sa.classify_limit_record(rec, highs=[100.0], lows=[99.0]) == sa.INSUFFICIENT
    assert sa.classify_limit_record(_limit_rec(), highs=[], lows=[]) == sa.INSUFFICIENT


def test_would_not_fill_outcome_is_flat_zero():
    rec = _limit_rec()
    rec["classification"] = sa.WOULD_NOT_FILL
    out = sa.candidate_outcome(rec)
    assert out is not None
    assert out["r_multiple"] == 0.0
    assert out["net_r_multiple"] == 0.0
    assert out["pnl_pct"] == 0.0
    assert out["won"] is False


def test_classify_pending_routes_limit_records(tmp_path):
    store = sa.SuppressedCandidateStore(persist_path="")
    sa.stamp_candidate(
        gate_name="tuned_variant:MOVER_TREND_PULLBACK", symbol="BTCUSDT",
        channel="c", setup_class="MOVER_TREND_PULLBACK@TUNED", side="LONG",
        entry=100, stop_loss=98, tp1=103, entry_type=sa.ENTRY_LIMIT, store=store,
    )
    # Window extremes span TP with the limit never touched (lows stay above
    # entry): the immediate classifier would say WIN, the limit walk NOT_FILL.
    counters = store.classify_pending(
        fetch_ohlc_since=lambda s, t: {
            "high": [104.0, 105.0], "low": [100.5, 103.0], "close": [104.5, 104.8],
        },
        now_ts=1e12,
    )
    assert counters.get(sa.WOULD_NOT_FILL) == 1


def test_stamp_defaults_to_immediate_entry_type(tmp_path):
    store = sa.SuppressedCandidateStore(persist_path="")
    rec = sa.stamp_candidate(
        gate_name="g", symbol="BTCUSDT", channel="c", setup_class="S", side="LONG",
        entry=100, stop_loss=99, tp1=102, store=store,
    )
    assert rec is not None and rec.entry_type == sa.ENTRY_IMMEDIATE
