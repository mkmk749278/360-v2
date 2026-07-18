"""Fan-out outcome telemetry + the ``auto_dispatch`` liveness predicate.

Why these pins exist (2026-07-18): every per-user gate in
``signal_dispatch._one_user`` skips silently by design — so when EVERY
user was being skipped (or the keyed-user roster resolved empty), the
engine emitted signals all day while placing zero orders for anyone,
with no counter, no summary and no page.  The owner's "auto trade not
happening to anyone" report was undiagnosable without VPS log access.

What we pin:

* The monotonic fan-out totals: placed / attempts / skip-reason
  breakdown, empty-roster counting, and that MANUAL takes never feed
  the auto-path totals.
* ``auto_dispatch_health_check`` — the pure predicate behind the
  feature-liveness probe: baseline capture, attempts-flowing reset,
  the silent-skip gap violation (with skip reasons in the detail),
  the empty-roster violation, and the restart watermark reset.
"""
from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.execution import signal_dispatch
from src.execution import symbol_filters


@pytest.fixture(autouse=True)
def _reset_cache(monkeypatch):
    signal_dispatch.reset_cache_for_test()
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT",
            step_size=0.001,
            tick_size=0.10,
            min_qty=0.001,
            min_notional=5.0,
        ),
    })
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: "live")
    monkeypatch.setattr(signal_dispatch, "_resolve_user_tier", lambda uid: "auto")
    yield
    signal_dispatch.reset_cache_for_test()
    symbol_filters.reset_for_test()


def _signal_kwargs(**overrides):
    kw = dict(
        signal_id="sig-1",
        symbol="BTCUSDT",
        direction="LONG",
        entry_price=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
    )
    kw.update(overrides)
    return kw


# ---------------------------------------------------------------------------
# Fan-out totals
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_placed_dispatch_counts_attempt_and_placed() -> None:
    with patch.object(signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B"]):
        from src.execution import position_fsm
        with patch.object(position_fsm, "place_signal", new_callable=AsyncMock):
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                **_signal_kwargs()
            )
    assert placed == 2
    t = signal_dispatch.dispatch_totals()
    assert t["fanouts_total"] == 1
    assert t["fanouts_with_users_total"] == 1
    assert t["attempts_total"] == 2
    assert t["placed_total"] == 2
    assert t.get("skipped_total", 0) == 0


@pytest.mark.asyncio
async def test_mode_skips_count_as_skips_not_attempts(monkeypatch) -> None:
    """The exact blackout signature: every user silently skipped at the
    mode gate → zero attempts, skip reason recorded."""
    from src.api import user_overrides as _uo
    monkeypatch.setattr(_uo, "resolve_user_mode_uid", lambda uid: "paper")
    with patch.object(signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B"]):
        from src.execution import position_fsm
        with patch.object(position_fsm, "place_signal", new_callable=AsyncMock) as mp:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                **_signal_kwargs()
            )
    assert placed == 0
    mp.assert_not_called()
    t = signal_dispatch.dispatch_totals()
    assert t["fanouts_with_users_total"] == 1
    assert t.get("attempts_total", 0) == 0
    assert t["skipped_total"] == 2
    assert t["skip:mode"] == 2


@pytest.mark.asyncio
async def test_tripwire_rejection_counts_as_attempt() -> None:
    """A rejection that writes a dispatch_log row IS an attempt — the
    probe must not confuse 'orders rejected' with 'nobody even tried'."""
    from src.execution import position_fsm, tripwires
    with patch.object(signal_dispatch, "_active_uids", return_value=["fb-A"]):
        with patch.object(
            position_fsm,
            "place_signal",
            new_callable=AsyncMock,
            side_effect=tripwires.SymbolNotAllowed("symbol 'X' is not on the tripwire allowlist"),
        ):
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                **_signal_kwargs()
            )
    assert placed == 0
    t = signal_dispatch.dispatch_totals()
    assert t["attempts_total"] == 1
    assert t.get("placed_total", 0) == 0
    assert t["rejected:SymbolNotAllowed"] == 1


@pytest.mark.asyncio
async def test_empty_roster_counts_separately() -> None:
    with patch.object(signal_dispatch, "_active_uids", return_value=[]):
        placed = await signal_dispatch.dispatch_signal_to_active_users(
            **_signal_kwargs()
        )
    assert placed == 0
    t = signal_dispatch.dispatch_totals()
    assert t["fanouts_total"] == 1
    assert t["fanouts_empty_roster_total"] == 1
    assert t.get("fanouts_with_users_total", 0) == 0


@pytest.mark.asyncio
async def test_manual_take_never_feeds_auto_totals() -> None:
    """A manual take is user-initiated — it must neither mask a fleet
    blackout (by bumping attempts) nor trigger one (by bumping fanouts)."""
    from src.execution import position_fsm, position_state
    with patch.object(position_fsm, "place_signal", new_callable=AsyncMock):
        with patch.object(
            position_state,
            "get_position",
            side_effect=position_state.PositionNotFoundError("none"),
        ):
            result: dict = {}
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                **_signal_kwargs(),
                _only_uid="fb-A",
                _manual=True,
                _manual_result=result,
            )
    assert placed == 1
    assert signal_dispatch.dispatch_totals() == {}


# ---------------------------------------------------------------------------
# auto_dispatch_health_check — pure predicate
# ---------------------------------------------------------------------------


def test_health_first_cycle_captures_baseline() -> None:
    state: dict = {}
    ok, detail = signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 7.0, "attempts_total": 3.0},
    )
    assert ok
    assert "baseline" in detail
    assert state["attempts"] == 3.0
    assert state["fan_at_last_attempt"] == 7.0


def test_health_ok_while_attempts_flow() -> None:
    state: dict = {}
    signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 0.0, "attempts_total": 0.0},
    )
    # 10 fan-outs later, attempts also moved — healthy no matter the gap.
    ok, _ = signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 10.0, "attempts_total": 4.0},
    )
    assert ok
    assert state["fan_at_last_attempt"] == 10.0


def test_health_violates_on_silent_skip_gap_with_reasons() -> None:
    state: dict = {}
    signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 2.0, "attempts_total": 2.0},
    )
    totals = {
        "fanouts_with_users_total": 8.0,   # +6 fan-outs…
        "attempts_total": 2.0,             # …zero new attempts
        "skip:mode": 9.0,
        "skip:tier": 3.0,
    }
    ok, detail = signal_dispatch.auto_dispatch_health_check(
        state, totals, gap_threshold=5,
    )
    assert not ok
    assert "ZERO order attempts" in detail
    assert "mode=9" in detail
    assert "tier=3" in detail


def test_health_below_threshold_stays_ok() -> None:
    state: dict = {}
    signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 2.0, "attempts_total": 2.0},
    )
    ok, _ = signal_dispatch.auto_dispatch_health_check(
        state,
        {"fanouts_with_users_total": 4.0, "attempts_total": 2.0},
        gap_threshold=5,
    )
    assert ok


def test_health_violates_on_empty_roster_gap() -> None:
    state: dict = {}
    signal_dispatch.auto_dispatch_health_check(
        state,
        {
            "fanouts_with_users_total": 5.0,
            "fanouts_empty_roster_total": 0.0,
            "attempts_total": 5.0,
        },
    )
    ok, detail = signal_dispatch.auto_dispatch_health_check(
        state,
        {
            "fanouts_with_users_total": 5.0,   # roster never non-empty again
            "fanouts_empty_roster_total": 6.0,  # +6 empty-roster fan-outs
            "attempts_total": 5.0,
        },
        gap_threshold=5,
    )
    assert not ok
    assert "EMPTY" in detail


def test_health_empty_roster_watermark_advances_on_nonempty_fanout() -> None:
    """Empty-roster fan-outs interleaved with non-empty ones (e.g. a
    transient Firestore blip) must not accumulate toward a page."""
    state: dict = {}
    signal_dispatch.auto_dispatch_health_check(
        state,
        {
            "fanouts_with_users_total": 1.0,
            "fanouts_empty_roster_total": 3.0,
            "attempts_total": 1.0,
        },
    )
    ok, _ = signal_dispatch.auto_dispatch_health_check(
        state,
        {
            "fanouts_with_users_total": 2.0,   # a non-empty roster was seen
            "fanouts_empty_roster_total": 7.0,
            "attempts_total": 2.0,
        },
        gap_threshold=5,
    )
    assert ok
    assert state["empty_at_last_roster"] == 7.0


def test_health_restart_resets_watermarks() -> None:
    state: dict = {}
    signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 50.0, "attempts_total": 40.0},
    )
    # Engine restarted: counters reset to near-zero — must re-baseline,
    # not report a negative/false gap.
    ok, detail = signal_dispatch.auto_dispatch_health_check(
        state, {"fanouts_with_users_total": 1.0, "attempts_total": 0.0},
    )
    assert ok
    assert "baseline" in detail
    assert state["fan_at_last_attempt"] == 1.0
