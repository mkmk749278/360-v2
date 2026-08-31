"""Per-signal "why didn't my signal trade" visibility.

Owner, 2026-08-31, over screenshots of the Signals tab beside the Trade
tab: *"seems to be every signal is not trading in binance don't know why
some hit trading"*.  Nothing on either surface could answer it.

``_one_user`` has two classes of "did not trade" and only one of them was
ever written down:

* the order path was reached and something refused ⇒ ``record_rejected``,
  which the app's Recent Activity card has translated since it shipped;
* a per-user gate returned BEFORE the order path ⇒ nothing, anywhere.

The skip counters existed the whole time (``_FANOUT_TOTALS["skip:*"]``)
and ``dispatch_totals()`` had exactly one consumer — a fleet-blackout
probe whose healthy message printed ``attempts`` and ``fanouts`` and
neither the skips nor the placed count.  So the numbers were computed on
every fan-out and published in neither state.

What we pin here:

* the two PER-SIGNAL gates (path / regime preference) stamp a
  ``skipped`` dispatch_log row the app can render;
* the ACCOUNT-level gates (mode / tier / auto-pause) deliberately do
  NOT — one Firestore write per fan-out per non-live user, forever, to
  restate what ``/api/auto-trade/runtime-status`` already returns once
  per visit, is the unbounded hot-path write this repo's cost discipline
  exists to refuse.  They keep their in-memory counter;
* a user with no preference set can never produce a skipped row;
* the probe's healthy message publishes the funnel, so the answer is on
  the ops Overview page rather than only in a violating branch.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.execution import signal_dispatch
from src.execution import symbol_filters


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    signal_dispatch.reset_cache_for_test()
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT", step_size=0.001, tick_size=0.10,
            min_qty=0.001, min_notional=5.0,
        ),
    })
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: "live")
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "auto")
    yield
    signal_dispatch.reset_cache_for_test()
    symbol_filters.reset_for_test()


def _kwargs(**overrides):
    kw = dict(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        entry_price=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        setup_class="MOVER_TREND_PULLBACK",
        regime_label="TRENDING_UP",
    )
    kw.update(overrides)
    return kw


async def _dispatch(monkeypatch, *, prefs, mode="live", tier="auto"):
    """Run one fan-out to a single user with the given preferences, with
    ``dispatch_log.record_skipped`` captured rather than written."""
    from src.api import user_overrides as _uo
    from src.execution import dispatch_log as _dl
    from src.execution import position_fsm

    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: mode)
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: tier)
    monkeypatch.setattr(
        _uo, "resolve_auto_trade_preferences_uid", lambda uid: prefs
    )
    calls: list[dict] = []
    monkeypatch.setattr(
        _dl, "record_skipped", lambda **kw: calls.append(kw)
    )
    with patch.object(signal_dispatch, "_active_uids", return_value=["fb-A"]):
        with patch.object(position_fsm, "place_signal", new_callable=AsyncMock):
            await signal_dispatch.dispatch_signal_to_active_users(**_kwargs())
    return calls


# ---------------------------------------------------------------------------
# The two per-signal gates stamp
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_path_preference_skip_is_recorded(monkeypatch) -> None:
    calls = await _dispatch(
        monkeypatch, prefs=({"TREND_PULLBACK_EMA"}, None),
    )
    assert len(calls) == 1
    assert calls[0]["skip_reason"] == "path_preference"
    assert calls[0]["signal_id"] == "sig-1"
    assert calls[0]["symbol"] == "BTCUSDT"
    # The detail must name the setup the user's own list excluded — a
    # reason with no subject is "blank needs a cause before it gets a
    # caption" wearing a sentence.
    assert "MOVER_TREND_PULLBACK" in calls[0]["skip_detail"]
    assert signal_dispatch.dispatch_totals()["skip:path_pref"] == 1


@pytest.mark.asyncio
async def test_regime_preference_skip_is_recorded(monkeypatch) -> None:
    calls = await _dispatch(monkeypatch, prefs=(None, {"RANGING"}))
    assert len(calls) == 1
    assert calls[0]["skip_reason"] == "regime_preference"
    assert "TRENDING_UP" in calls[0]["skip_detail"]
    assert signal_dispatch.dispatch_totals()["skip:regime_pref"] == 1


@pytest.mark.asyncio
async def test_no_preference_set_never_stamps(monkeypatch) -> None:
    """The default account (no preference) is the overwhelming majority.
    It must not be able to write a row here at all — the population this
    lane bills for is bounded by users who opted into a filter."""
    calls = await _dispatch(monkeypatch, prefs=(None, None))
    assert calls == []


@pytest.mark.asyncio
async def test_preference_that_admits_the_signal_never_stamps(monkeypatch) -> None:
    calls = await _dispatch(
        monkeypatch,
        prefs=({"MOVER_TREND_PULLBACK"}, {"TRENDING_UP"}),
    )
    assert calls == []


# ---------------------------------------------------------------------------
# The account-level gates deliberately do NOT stamp
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "mode,tier,counter",
    [
        ("paper", "auto", "skip:mode"),
        ("off", "auto", "skip:mode"),
        ("live", "free", "skip:tier"),
    ],
)
@pytest.mark.asyncio
async def test_account_level_gates_count_but_do_not_write(
    monkeypatch, mode, tier, counter
) -> None:
    """A per-signal row here would be one Firestore write per fan-out per
    non-live user forever, to say something the runtime-status endpoint
    already answers once per visit.  Counted in memory, not persisted."""
    calls = await _dispatch(
        monkeypatch, prefs=(None, None), mode=mode, tier=tier,
    )
    assert calls == []
    assert signal_dispatch.dispatch_totals()[counter] == 1


# ---------------------------------------------------------------------------
# The probe publishes the funnel in its HEALTHY message
# ---------------------------------------------------------------------------


def test_healthy_probe_message_publishes_placed_rejected_skipped() -> None:
    """Pre-2026-08-31 this read ``attempts=41 fanouts=41`` and the owner
    could not tell 41 placed from 41 rejected.  Fails against that tree."""
    state: dict = {}
    totals = {
        "fanouts_with_users_total": 10.0,
        "fanouts_empty_roster_total": 0.0,
        "attempts_total": 8.0,
        "placed_total": 5.0,
        "skipped_total": 2.0,
        "skip:path_pref": 2.0,
        "rejected:OrderRejectedByBinance": 3.0,
    }
    signal_dispatch.auto_dispatch_health_check(state, totals)  # baseline
    ok, detail = signal_dispatch.auto_dispatch_health_check(state, totals)
    assert ok
    assert "placed=5" in detail
    assert "rejected=3" in detail
    assert "skipped=2" in detail
    assert "path_pref=2" in detail
    assert "OrderRejectedByBinance=3" in detail


def test_probe_message_never_calls_the_skip_gap_a_skip_count() -> None:
    """``skip {gap}`` is a gap since the last order attempt, and reading
    it as a count is how a fleet of silent skips looks like zero.  Both
    numbers appear, and the cumulative one is labelled ``skipped=``."""
    state: dict = {}
    totals = {
        "fanouts_with_users_total": 4.0,
        "attempts_total": 4.0,
        "placed_total": 4.0,
        "skipped_total": 17.0,
    }
    signal_dispatch.auto_dispatch_health_check(state, totals)
    _, detail = signal_dispatch.auto_dispatch_health_check(state, totals)
    assert "skipped=17" in detail
    assert "skip 0" in detail
