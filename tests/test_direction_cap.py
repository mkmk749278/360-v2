"""The same-direction cap: global budget vs per-path budget.

Owner, 2026-08-22: *"set cap per path 3 same direction and no cumulative max
cap anyways, so per path can individually produce 3 signals same direction —
so we can get max 6, 3 longs 3 shorts at same time"*.

Measured on the live box over one 10.5h boot: **545 dequeued, 17 delivered
(3.1%), and ``same_direction_throttle`` took 499 of the 500 drops — 91.6% of
everything the router dequeued.**  BTC had run +20.7% in three days, so every
candidate was long, and a global budget of three long slots is saturated
permanently.  MVRTP took 475 of those 499 because it submits roughly twenty
times anyone else's volume; the smaller paths' handful of candidates arrived
into a book whose slots were already held.

This raises blast radius, and the owner signed it off in writing.  These tests
pin what the cap does in each mode, that the counterfactual for the *other*
mode is measured on every candidate whatever the configured mode, and — the
one that matters most — that the budget key cannot drift between the moment a
signal is admitted and the moment it is counted.
"""
from __future__ import annotations

import asyncio
from typing import Optional

import pytest

import config
import src.signal_router as sr
from src.channels.base import Signal
from src.signal_router import SignalRouter
from src.smc import Direction


def _router() -> SignalRouter:
    async def _send(chat_id: str, text: str) -> bool:
        return True

    return SignalRouter(
        queue=asyncio.Queue(),
        send_telegram=_send,
        format_signal=lambda sig: f"Signal: {sig.symbol}",
    )


def _sig(
    symbol: str,
    direction: Direction = Direction.LONG,
    origin: str = "MOVER_TREND_PULLBACK",
    setup: Optional[str] = None,
) -> Signal:
    return Signal(
        channel="360_SCALP",
        symbol=symbol,
        direction=direction,
        entry=100.0,
        stop_loss=98.0,
        tp1=103.0,
        tp2=106.0,
        setup_class=origin if setup is None else setup,
        origin_setup_class=origin,
        signal_id=f"{symbol}-{direction.value}-{origin}",
    )


def _fill(router: SignalRouter, *signals: Signal) -> None:
    """Put signals in the active book the way the cap counts them."""
    for s in signals:
        router._active_signals[s.signal_id] = s


@pytest.fixture
def per_path(monkeypatch):
    monkeypatch.setattr(sr, "DIRECTION_CAP_MODE", "per_path")
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_PER_PATH", 3)
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_CUMULATIVE", 0)
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_GLOBAL", 3)


@pytest.fixture
def global_mode(monkeypatch):
    monkeypatch.setattr(sr, "DIRECTION_CAP_MODE", "global")
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_PER_PATH", 3)
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_CUMULATIVE", 0)
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_GLOBAL", 3)


# ---------------------------------------------------------------------------
# The budget key
# ---------------------------------------------------------------------------

def test_the_budget_is_keyed_on_the_immutable_origin_not_the_mutable_class():
    """``setup_class`` is rewritten downstream by arbitration and confluence.

    The count is recomputed from the live book on every candidate, so if the
    key can change between admission and counting, a signal decrements a
    budget it never incremented and the cap drifts silently.
    """
    rewritten = _sig("BTCUSDT", origin="MOVER_TREND_PULLBACK", setup="SOMETHING_ELSE")
    assert SignalRouter.direction_budget_key(rewritten) == "MOVER_TREND_PULLBACK"


def test_a_signal_with_no_origin_falls_back_to_its_current_class():
    s = _sig("BTCUSDT", origin="", setup="MEAN_REVERT")
    assert SignalRouter.direction_budget_key(s) == "MEAN_REVERT"


def test_a_signal_with_no_identity_at_all_gets_its_own_named_bucket():
    """A fallback is not a default.

    If a call site stops stamping, that must show up as an odd budget rather
    than hide inside whichever real path happens to be quiet.
    """
    s = _sig("BTCUSDT", origin="", setup="")
    assert SignalRouter.direction_budget_key(s) == "UNCLASSIFIED"


# ---------------------------------------------------------------------------
# Global mode — unchanged behaviour
# ---------------------------------------------------------------------------

def test_global_mode_blocks_the_fourth_long_whatever_path_it_came_from(global_mode):
    """The behaviour that took 91.6% of the drops."""
    r = _router()
    _fill(
        r,
        _sig("AUSDT", origin="MOVER_TREND_PULLBACK"),
        _sig("BUSDT", origin="MOVER_TREND_PULLBACK"),
        _sig("CUSDT", origin="MOVER_TREND_PULLBACK"),
    )
    # A completely different path, with an empty budget of its own.
    cap = r._direction_cap_decision(_sig("DUSDT", origin="MEAN_REVERT"))

    assert cap.blocked is True
    assert cap.mode == "global"
    assert cap.same_dir_path == 0, "MEAN_REVERT holds nothing and is blocked anyway"


def test_global_mode_leaves_the_opposite_direction_alone(global_mode):
    r = _router()
    _fill(r, *[_sig(f"{c}USDT") for c in "ABC"])
    cap = r._direction_cap_decision(_sig("DUSDT", direction=Direction.SHORT))
    assert cap.blocked is False


# ---------------------------------------------------------------------------
# Per-path mode — what the owner asked for
# ---------------------------------------------------------------------------

def test_per_path_mode_lets_a_starved_path_through_a_saturated_book(per_path):
    """The whole point: MEAN_REVERT is not starved by MVRTP's volume."""
    r = _router()
    _fill(r, *[_sig(f"{c}USDT", origin="MOVER_TREND_PULLBACK") for c in "ABC"])

    cap = r._direction_cap_decision(_sig("DUSDT", origin="MEAN_REVERT"))
    assert cap.blocked is False
    assert cap.would_block_global is True, "the global cap would have killed it"


def test_per_path_mode_still_caps_the_path_that_is_saturating(per_path):
    r = _router()
    _fill(r, *[_sig(f"{c}USDT", origin="MOVER_TREND_PULLBACK") for c in "ABC"])

    cap = r._direction_cap_decision(_sig("DUSDT", origin="MOVER_TREND_PULLBACK"))
    assert cap.blocked is True
    assert cap.count == 3 and cap.limit == 3
    assert "MOVER_TREND_PULLBACK" in cap.reason


def test_one_path_holds_three_longs_and_three_shorts_at_once(per_path):
    """"so we can get max 6, 3 longs 3 shorts at same time" — per path."""
    r = _router()
    _fill(
        r,
        *[_sig(f"L{c}USDT", Direction.LONG) for c in "ABC"],
        *[_sig(f"S{c}USDT", Direction.SHORT) for c in "ABC"],
    )
    assert len(r._active_signals) == 6

    assert r._direction_cap_decision(_sig("XUSDT", Direction.LONG)).blocked is True
    assert r._direction_cap_decision(_sig("YUSDT", Direction.SHORT)).blocked is True
    # …and a different path is untouched by either of those six.
    other = _sig("ZUSDT", Direction.LONG, origin="RANGE_FADE")
    assert r._direction_cap_decision(other).blocked is False


def test_the_cumulative_ceiling_is_off_and_that_is_a_decision_not_an_unset(per_path):
    """"no cumulative max cap" — six paths may each hold their three."""
    r = _router()
    for i, path in enumerate(["P1", "P2", "P3", "P4", "P5", "P6"]):
        _fill(r, *[_sig(f"{path}{c}USDT", origin=path) for c in "ABC"])
    assert len(r._active_signals) == 18

    cap = r._direction_cap_decision(_sig("NEWUSDT", origin="P7"))
    assert cap.blocked is False
    assert cap.same_dir_total == 18


def test_re_arming_the_cumulative_ceiling_works_without_a_redeploy(
    per_path, monkeypatch
):
    """It stays a tunable rather than being deleted.

    Deleting a cap costs a deploy to get it back, and the moment you want it
    back is the moment you cannot wait for one.
    """
    monkeypatch.setattr(sr, "MAX_SAME_DIRECTION_CUMULATIVE", 10)
    r = _router()
    for path in ["P1", "P2", "P3", "P4"]:
        _fill(r, *[_sig(f"{path}{c}USDT", origin=path) for c in "ABC"])
    assert len(r._active_signals) == 12

    cap = r._direction_cap_decision(_sig("NEWUSDT", origin="P5"))
    assert cap.blocked is True
    assert cap.reason == "cumulative ceiling", (
        "a path at its own bound and a book at a ceiling are different "
        "findings with different fixes, and must never pool"
    )


# ---------------------------------------------------------------------------
# The counterfactual — measured in BOTH modes, always
# ---------------------------------------------------------------------------

def test_the_counterfactual_is_measured_while_the_effect_is_off(global_mode):
    """The number the switch decision is read from, gathered before switching."""
    r = _router()
    _fill(r, *[_sig(f"{c}USDT", origin="MOVER_TREND_PULLBACK") for c in "ABC"])

    for sym in ["DUSDT", "EUSDT"]:
        r._record_direction_cap_counterfactual(
            r._direction_cap_decision(_sig(sym, origin="MEAN_REVERT"))
        )
    report = r.direction_cap_report()

    assert report["mode"] == "global"
    assert report["counterfactual"]["global_only"] == 2, (
        "two candidates the global cap kills that per-path would pass"
    )
    assert report["would_gain"] == 2
    assert report["would_gain_share"] == pytest.approx(1.0)
    assert report["counterfactual_by_path"]["global_only:MEAN_REVERT"] == 2


def test_agreement_between_the_modes_is_counted_apart_from_disagreement(global_mode):
    r = _router()
    _fill(r, *[_sig(f"{c}USDT", origin="MOVER_TREND_PULLBACK") for c in "ABC"])

    # Same path as the three holders: both modes block it.
    r._record_direction_cap_counterfactual(
        r._direction_cap_decision(_sig("DUSDT", origin="MOVER_TREND_PULLBACK"))
    )
    # Empty book in the other direction: neither blocks.
    r._record_direction_cap_counterfactual(
        r._direction_cap_decision(_sig("EUSDT", Direction.SHORT))
    )
    cf = r.direction_cap_report()["counterfactual"]

    assert cf["both_block"] == 1
    assert cf["neither_blocks"] == 1
    assert cf["global_only"] == 0
    assert cf["evaluated"] == 2


def test_the_gate_and_the_counterfactual_cannot_disagree(per_path):
    """One evaluation, two readings — never two implementations.

    A panel built on a second implementation of "would this have been blocked"
    ends up disagreeing with the gate that would perform the switch.
    """
    r = _router()
    _fill(r, *[_sig(f"{c}USDT", origin="MOVER_TREND_PULLBACK") for c in "ABC"])

    cap = r._direction_cap_decision(_sig("DUSDT", origin="MOVER_TREND_PULLBACK"))
    assert cap.blocked is cap.would_block_per_path, (
        "in per_path mode the applied verdict IS the per-path counterfactual"
    )


def test_budgets_held_makes_saturation_legible_as_saturation(per_path):
    """A saturated cap and an absence of candidates read identically without
    this."""
    r = _router()
    _fill(r, *[_sig(f"{c}USDT", origin="MOVER_TREND_PULLBACK") for c in "ABC"])
    _fill(r, _sig("XUSDT", Direction.SHORT, origin="RANGE_FADE"))

    held = r.direction_cap_report()["budgets_held"]
    assert held["MOVER_TREND_PULLBACK|LONG"] == 3
    assert held["RANGE_FADE|SHORT"] == 1
    assert r.direction_cap_report()["budgets_held_total"] == 4


def test_the_report_rides_the_delivery_stats_ops_already_reads():
    """Dark work must be observable, and the last hop is a surface that
    renders it."""
    r = _router()
    stats = r.delivery_stats()
    assert "direction_cap" in stats
    assert stats["direction_cap"]["mode"] in ("global", "per_path")


# ---------------------------------------------------------------------------
# The flag
# ---------------------------------------------------------------------------

def test_the_mode_ships_global_and_the_switch_is_one_tunable():
    """A money-path blast-radius change ships dark; the measurement does not."""
    assert config.DIRECTION_CAP_MODE == "global"
    assert config.MAX_SAME_DIRECTION_PER_PATH == 3
    assert config.MAX_SAME_DIRECTION_CUMULATIVE == 0


def test_an_invalid_mode_fails_closed_to_global(monkeypatch):
    """The trail-governor timeframe lesson: a setting with two legal values
    must be unselectable-wrong, not merely validated."""
    import importlib

    monkeypatch.setenv("DIRECTION_CAP_MODE", "per-path")  # hyphen, not underscore
    reloaded = importlib.reload(config)
    try:
        assert reloaded.DIRECTION_CAP_MODE == "global"
    finally:
        monkeypatch.delenv("DIRECTION_CAP_MODE", raising=False)
        importlib.reload(config)
