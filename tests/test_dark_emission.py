"""The dark emission lane — the silent paths emitting, owner-only.

The safety property is the point of these tests, not a side note. A dark signal
that reaches ``SignalRouter`` reaches the paid Telegram channel, the FCM
``signals`` topic, the free channel, the app feed, ``_position_lock`` (which
would block a *real* signal on that symbol), and
``signal_dispatch.dispatch_signal_to_active_users`` — **real orders on real
users' keys**.

That is why the design is structural rather than conditional: a dark candidate
is diverted at the single ``signal_queue.put`` site, and the queue is the only
route to any of the six. The tests below pin exactly that, including the
inverse — that a *live* candidate still enqueues, because a safety property that
also blocks the money path is a bug, not a guarantee.
"""
from __future__ import annotations

import pytest

from src import dark_emission as de


class _Sig:
    signal_id = "SIG-DARK-1"
    symbol = "MEANUSDT"
    channel = "360_SCALP"
    setup_class = "MEAN_REVERT"
    entry = 100.0
    stop_loss = 97.0
    tp1 = 106.0
    confidence = 71.5
    entry_regime = "TRENDING_UP"
    mc_context_key = "NY/MARKUP/NORMAL/BTC_NEUTRAL"
    valid_for_minutes = 60.0
    pair_admission = "CORE"

    class direction:
        value = "LONG"


@pytest.fixture(autouse=True)
def _on(monkeypatch):
    from src import runtime_tunables as rt

    monkeypatch.setattr(rt, "get", lambda key, *a, **k: True)
    de.reset_ledger(de.DarkLedger(path=""))
    yield
    de.reset_ledger(None)


# --------------------------------------------------------------------------- #
# Admission
# --------------------------------------------------------------------------- #


def test_a_loosened_gate_admits_an_enrolled_path():
    sig = _Sig()
    assert de.should_mark(sig, "setup_compat:regime_STRONG_TREND") is True
    assert de.should_mark(sig, "execution:overextended") is True


def test_a_gate_we_do_not_loosen_is_not_admitted():
    """min_confidence and the context floors stay live — they already carry
    KEEP/TUNE/DROP verdicts, and they are the last thing between a scored
    candidate and a feed."""
    assert de.should_mark(_Sig(), "min_confidence") is False
    assert de.should_mark(_Sig(), "context_floor:QUIET_COMPRESSION_BREAK") is False
    assert de.should_mark(_Sig(), "level_still_in_play") is False


def test_mover_trend_pullback_is_excluded():
    """Owner, 2026-07-31. It owns 64% of the delivered book and 24,327 of the
    37,782 pre-scoring rejects — admitting it makes the dark feed a second MTP
    feed, and is why no per-path budget was needed."""
    sig = _Sig()
    sig.setup_class = "MOVER_TREND_PULLBACK"
    assert de.should_mark(sig, "setup_compat:regime_STRONG_TREND") is False


def test_the_first_gate_to_catch_it_is_the_one_recorded():
    """A candidate can be caught by both loosened gates; the first is the one
    that would have killed it live, so the second must not overwrite it."""
    sig = _Sig()
    de.mark(sig, "setup_compat:regime_STRONG_TREND")
    assert de.should_mark(sig, "execution:overextended") is False
    assert getattr(sig, de.DARK_ATTR) == "setup_compat:regime_STRONG_TREND"


def test_nothing_is_admitted_while_the_lane_is_off(monkeypatch):
    from src import runtime_tunables as rt

    monkeypatch.setattr(rt, "get", lambda key, *a, **k: False)
    assert de.should_mark(_Sig(), "setup_compat:regime_STRONG_TREND") is False


# --------------------------------------------------------------------------- #
# The safety property — verified through the REAL scanner method
# --------------------------------------------------------------------------- #


def _scanner_source() -> str:
    import inspect

    import src.scanner as _scanner

    return inspect.getsource(_scanner)


def test_the_divert_sits_before_the_only_enqueue_site_in_the_real_scanner():
    """Asserted against the real source, not a re-implementation of it.

    A hand-written copy of this branch in a test would assert the author's
    assumption back at itself and go green over dead code (#798) — and the
    thing being asserted here is the one that keeps a dark signal away from
    real users' capital, so a test that could pass over a broken branch is
    worse than no test.

    ``signal_queue.put`` is the only route to ``SignalRouter``, and therefore
    the only route to the paid channel, FCM, the free channel, the app feed,
    ``_position_lock`` and ``signal_dispatch``. The divert must come first and
    must return.
    """
    src = _scanner_source()
    assert src.count("await self.signal_queue.put(sig)") == 1, (
        "a second enqueue site appeared — the dark divert now guards only one "
        "of them, and the other reaches real users"
    )
    divert = src.index("if dark_emission.is_dark(sig):")
    enqueue = src.index("await self.signal_queue.put(sig)")
    assert divert < enqueue, "the dark divert must precede the enqueue"
    branch = src[divert:enqueue]
    assert "return" in branch, "the dark branch must return, not fall through"
    assert "dark_emission.publish(sig)" in branch


def test_both_loosened_gates_carry_instead_of_rejecting_in_the_real_scanner():
    src = _scanner_source()
    for token in ("setup_compat:{_compat_token}", "execution:{_exec_token}"):
        assert f'dark_emission.should_mark(sig, f"{token}")' in src
        assert f'dark_emission.mark(sig, f"{token}")' in src


def test_no_other_module_can_route_a_dark_signal():
    """The router, the dispatcher and the push path must not have learned
    about dark signals — if they had, the property would be conditional
    (six correct skips) rather than structural (one branch)."""
    import inspect

    from src import push_notifications, signal_router
    from src.execution import signal_dispatch

    for mod in (signal_router, signal_dispatch, push_notifications):
        assert "dark_emission" not in inspect.getsource(mod), (
            f"{mod.__name__} references the dark lane — the safety property is "
            "supposed to be that it never has to"
        )


def test_is_dark_is_false_for_an_ordinary_signal():
    assert de.is_dark(_Sig()) is False


# --------------------------------------------------------------------------- #
# The ledger
# --------------------------------------------------------------------------- #


def test_a_published_row_carries_the_gate_that_would_have_killed_it():
    sig = _Sig()
    de.mark(sig, "setup_compat:regime_STRONG_TREND")
    assert de.publish(sig) is True
    (row,) = de.get_ledger().rows()
    assert row["dark_gate"] == "setup_compat:regime_STRONG_TREND"
    assert row["setup_class"] == "MEAN_REVERT"
    assert row["status"] == de.STATUS_OPEN
    # Scored confidence — a dark signal has been through the scoring engine and
    # every gate but the loosened one, which is what makes it different in kind
    # from a suppression stamp.
    assert row["confidence"] == pytest.approx(71.5)


def test_geometry_that_cannot_be_measured_is_refused_not_stored():
    """Refuse, don't clamp: a row with no tradeable geometry can never resolve,
    and storing it would show as a permanently-open dark trade."""
    sig = _Sig()
    sig.tp1 = 0.0
    de.mark(sig, "execution:overextended")
    assert de.publish(sig) is False
    assert de.get_ledger().rows() == []


def test_one_loud_path_cannot_evict_another_paths_rows():
    """Same lesson the suppression store just paid for: a shared ring makes the
    loudest population the only readable one."""
    ledger = de.DarkLedger(path="", per_path_max=3)
    de.reset_ledger(ledger)
    quiet = _Sig()
    quiet.setup_class = "RANGE_FADE"
    de.mark(quiet, "setup_compat:regime_WEAK_TREND")
    de.publish(quiet)
    for _ in range(50):
        loud = _Sig()
        loud.setup_class = "LIQUIDITY_SWEEP_REVERSAL"
        de.mark(loud, "execution:trigger_not_confirmed")
        de.publish(loud)
    setups = [r["setup_class"] for r in ledger.rows()]
    assert "RANGE_FADE" in setups
    assert setups.count("LIQUIDITY_SWEEP_REVERSAL") == 3


def test_a_schema_bump_drops_rows_rather_than_reinterpreting_them(tmp_path):
    import json

    path = str(tmp_path / "dark.json")
    with open(path, "w") as fh:
        json.dump(
            {"schema": de.LEDGER_SCHEMA + 1, "rows": [{"setup_class": "X"}]}, fh
        )
    ledger = de.DarkLedger(path=path)
    ledger.load()
    assert ledger.rows() == []


def test_the_ledger_writes_even_with_nothing_to_say(tmp_path):
    """An idle engine that writes no file reads to ops as 'the lane is not
    running' — a fault that is not happening (#832, caught minutes after
    deploy)."""
    path = str(tmp_path / "dark.json")
    ledger = de.DarkLedger(path=path)
    assert ledger.flush(force=True) is True
    import json

    payload = json.load(open(path))
    assert payload["schema"] == de.LEDGER_SCHEMA
    assert payload["rows"] == []


def test_publish_never_raises_into_the_scan_loop(monkeypatch):
    monkeypatch.setattr(de, "get_ledger", lambda: (_ for _ in ()).throw(RuntimeError()))
    sig = _Sig()
    de.mark(sig, "execution:overextended")
    assert de.publish(sig) is False


# --------------------------------------------------------------------------- #
# What the gate was holding up
# --------------------------------------------------------------------------- #


def test_a_none_anchor_no_longer_raises_into_the_scan_loop():
    """Found by carrying a candidate past the gate that had always killed it.

    ``getattr(signal, "far_reclaim_level", signal.entry)`` looks defensive and
    is not: the attribute is declared on ``Signal`` and defaults to None, so
    the default never fires and the comparison raises. It was unreachable while
    ``setup_compat`` killed every FAILED_AUCTION_RECLAIM candidate in a VOLATILE
    regime before scoring — a gate holding a bug up. Loosening a gate exposes
    the code it was protecting, which is a cost of this lane worth naming.
    """
    from src.signal_quality import (
        MarketState,
        SetupClass,
        execution_quality_check,
    )
    from src.smc import Direction

    class _S:
        entry = 100.0
        stop_loss = 97.0
        tp1 = 106.0
        direction = Direction.LONG
        far_reclaim_level = None
        pdc_breakout_level = None

    for setup in (SetupClass.FAILED_AUCTION_RECLAIM,
                  SetupClass.POST_DISPLACEMENT_CONTINUATION):
        # Would raise TypeError on the None anchor before the fix.
        result = execution_quality_check(
            _S(), {}, {}, setup, MarketState.VOLATILE_UNSUITABLE
        )
        assert result is not None


# --------------------------------------------------------------------------- #
# Forward resolution
# --------------------------------------------------------------------------- #


def _published(side="LONG", entry=100.0, sl=97.0, tp1=106.0, ts=1_700_000_000.0):
    sig = _Sig()
    sig.entry, sig.stop_loss, sig.tp1 = entry, sl, tp1
    sig.direction = type("_D", (), {"value": side})
    de.mark(sig, "setup_compat:regime_STRONG_TREND")
    de.publish(sig, now_ts=ts)
    return de.get_ledger()


def test_a_dark_row_resolves_to_tp1_with_an_R():
    ledger = _published()
    ohlc = {"high": [101.0, 107.0], "low": [99.5, 100.0], "close": [100.5, 106.5]}
    de.resolve_open(lambda *_: ohlc, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_TP1
    assert row["r_multiple"] == pytest.approx(6.0 / 3.0)
    assert row["ambiguous_bar"] is False


def test_a_same_bar_touch_resolves_pessimistically_and_is_flagged():
    """OHLC cannot order two touches inside one bar — so the row says it is a
    judgement rather than being averaged in as a fact."""
    ledger = _published()
    ohlc = {"high": [107.0], "low": [96.0], "close": [100.0]}
    de.resolve_open(lambda *_: ohlc, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_SL
    assert row["ambiguous_bar"] is True


def test_a_row_past_the_horizon_expires_at_0R_not_as_a_loss():
    """An expiry is the mechanism doing nothing, not losing. Counting it as a
    loss is the #685 fabrication class."""
    ledger = _published()
    ohlc = {"high": [101.0], "low": [99.0], "close": [100.0]}
    de.resolve_open(
        lambda *_: ohlc, now_ts=1_700_000_000.0 + 7 * 3600.0, ledger=ledger
    )
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_EXPIRED
    assert row["r_multiple"] == 0.0


def test_a_row_with_no_candles_stays_open_and_is_counted():
    """An unresolved row must never be scored: a loss-selected sample is worse
    than no sample, because it looks like an answer (#832)."""
    ledger = _published()
    tally = de.resolve_open(lambda *_: None, now_ts=1_700_000_600.0, ledger=ledger)
    (row,) = ledger.rows()
    assert row["status"] == de.STATUS_OPEN
    assert row["r_multiple"] is None
    assert tally["no_candles"] == 1


def test_the_summary_reports_win_rate_over_decided_rows_only():
    ledger = de.DarkLedger(path="")
    de.reset_ledger(ledger)
    for tp in (True, True, False):
        sig = _Sig()
        sig.direction = type("_D", (), {"value": "LONG"})
        de.mark(sig, "setup_compat:regime_STRONG_TREND")
        de.publish(sig, now_ts=1_700_000_000.0)
    rows = ledger.rows()
    rows[0].update({"status": de.STATUS_TP1, "r_multiple": 2.0})
    rows[1].update({"status": de.STATUS_SL, "r_multiple": -1.0})
    rows[2].update({"status": de.STATUS_EXPIRED, "r_multiple": 0.0})
    agg = de.summary(ledger)["MEAN_REVERT"]
    assert agg["resolved"] == 3 and agg["expired"] == 1
    # 1 win of 2 DECIDED, not 1 of 3 — the expiry is neither.
    assert agg["win_rate"] == pytest.approx(0.5)
    assert agg["avg_r"] == pytest.approx((2.0 - 1.0 + 0.0) / 3.0)


def test_an_open_row_is_not_pooled_into_the_verdict():
    ledger = _published()
    agg = de.summary(ledger)["MEAN_REVERT"]
    assert agg["open"] == 1 and agg["resolved"] == 0
    assert agg["avg_r"] is None and agg["win_rate"] is None
