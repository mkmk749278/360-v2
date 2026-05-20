"""Tests for src.execution.signal_dispatch.

What we pin:

* Quantity computation: $500 notional / entry_price, with 30/40/30
  TP split that sums EXACTLY to total_qty (no orphan dust).
* Zero / negative entry price → zero qtys → dispatch no-ops.
* No active users → dispatch returns 0 without touching FSM.
* Per-user failures are isolated (one user's rejection doesn't
  block others).
* Cache TTL: list_active_uids is called at most once per 30s
  window.
"""
from __future__ import annotations

from typing import List
from unittest.mock import AsyncMock, patch

import pytest

from src.execution import signal_dispatch
from src.execution import symbol_filters


@pytest.fixture(autouse=True)
def _reset_cache():
    signal_dispatch.reset_cache_for_test()
    # Seed the symbol-filter cache so ``_compute_qty_split`` rounds
    # cleanly in tests.  BTCUSDT stepSize 0.001 + tickSize 0.10 matches
    # Binance's actual values closely enough for assertion math.
    symbol_filters._set_cache_for_test({
        "BTCUSDT": symbol_filters.SymbolFilters(
            symbol="BTCUSDT",
            step_size=0.001,
            tick_size=0.10,
            min_qty=0.001,
            min_notional=5.0,
        ),
    })
    yield
    signal_dispatch.reset_cache_for_test()
    symbol_filters.reset_for_test()


# ---------------------------------------------------------------------------
# Qty split math
# ---------------------------------------------------------------------------


def test_qty_split_sums_to_total_no_dust() -> None:
    """The three TP qtys must sum EXACTLY to total_qty — Binance
    rejects orders that don't reconcile, and dust orphan would
    block the residual from closing cleanly."""
    total, tp1, tp2, tp3 = signal_dispatch._compute_qty_split("BTCUSDT", 29000.0)
    assert tp1 + tp2 + tp3 == total


def test_qty_split_at_typical_btc_price() -> None:
    """$500 notional / $29000 entry ≈ 0.01724 BTC, then floored to
    BTCUSDT's stepSize=0.001 → 0.017 BTC.  The TP split is also
    floored to stepSize so each leg lands on a Binance-valid qty.
    The 30/40/30 ratio is approximate after rounding (especially on
    pairs with coarse stepSize like DOGEUSDT stepSize=1)."""
    total, tp1, tp2, tp3 = signal_dispatch._compute_qty_split("BTCUSDT", 29000.0)
    # 0.5 step-units of slack on the total — actual value depends
    # on stepSize floor behaviour.
    assert abs(total - 0.017) < 0.001
    # TP fractions in the right ballpark, allowing for stepSize floor.
    assert abs(tp1 / total - 0.30) < 0.05
    assert abs(tp2 / total - 0.40) < 0.05
    # Sums-to-total is the doctrine guarantee covered separately.


@pytest.mark.parametrize("bad_price", [0.0, -1.0, -29000.0])
def test_qty_split_defensive_on_invalid_price(bad_price: float) -> None:
    """Defensive: malformed signal with non-positive entry returns
    all zeros.  Caller (dispatcher) treats zero total_qty as
    'skip this signal' rather than placing a zero order."""
    total, tp1, tp2, tp3 = signal_dispatch._compute_qty_split("BTCUSDT", bad_price)
    assert total == 0.0
    assert tp1 == 0.0
    assert tp2 == 0.0
    assert tp3 == 0.0


# ---------------------------------------------------------------------------
# Dispatch fan-out
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dispatch_no_active_users_returns_zero() -> None:
    """Cold-deploy state (no users connected): returns 0 without
    invoking the FSM.  This is the safe default that lets the
    server-side stack ship alongside the legacy client-side path."""
    with patch.object(
        signal_dispatch, "_active_uids", return_value=[]
    ):
        from src.execution import position_fsm
        with patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock
        ) as mock_place:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=29000.0,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
            )
        assert placed == 0
        mock_place.assert_not_called()


@pytest.mark.asyncio
async def test_dispatch_fans_out_to_all_active_users() -> None:
    """Multiple users with connected keys: each gets a separate
    place_signal call, all in parallel."""
    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B", "fb-C"]
    ):
        from src.execution import position_fsm
        with patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock
        ) as mock_place:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=29000.0,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
            )
        assert placed == 3
        assert mock_place.await_count == 3
        # Verify each call carried the right per-user uid.
        called_uids = {
            call.kwargs["firebase_uid"] for call in mock_place.await_args_list
        }
        assert called_uids == {"fb-A", "fb-B", "fb-C"}


@pytest.mark.asyncio
async def test_dispatch_isolates_per_user_failures() -> None:
    """The doctrine canary: one user's tripwire rejection (or
    KMS outage, or Binance key revoked) must NOT block other
    users' orders from landing.  This is what makes the server-
    side stack robust under partial failures."""
    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B", "fb-C"]
    ):
        async def _per_user(firebase_uid, **kwargs):
            if firebase_uid == "fb-B":
                raise RuntimeError("user fb-B's circuit breaker tripped")
            return None  # success

        from src.execution import position_fsm
        with patch.object(
            position_fsm, "place_signal", side_effect=_per_user
        ):
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=29000.0,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
            )
        # fb-A + fb-C succeeded; fb-B rejected.
        assert placed == 2


@pytest.mark.asyncio
async def test_dispatch_skips_zero_qty_signal() -> None:
    """Defensive: malformed signal with entry=0 returns 0 without
    attempting any per-user placement."""
    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A"]
    ):
        from src.execution import position_fsm
        with patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock
        ) as mock_place:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=0.0,  # malformed
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
            )
        assert placed == 0
        mock_place.assert_not_called()


# ---------------------------------------------------------------------------
# Cache TTL
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Per-user notional override (2026-05-20)
# ---------------------------------------------------------------------------


def test_qty_split_honours_user_notional_override() -> None:
    """When ``notional_usd`` is passed, qty math uses that value
    instead of the engine default ($500).  Half-default ($250) →
    roughly half the qty."""
    total_default, _, _, _ = signal_dispatch._compute_qty_split(
        "BTCUSDT", 29000.0,
    )
    total_half, _, _, _ = signal_dispatch._compute_qty_split(
        "BTCUSDT", 29000.0, notional_usd=250.0,
    )
    # 250/500 = 0.5; both floored to stepSize so we allow one step of
    # slack ($0.001 BTC ≈ $0.029 of notional).
    assert abs(total_half - total_default / 2) < 0.002


def test_qty_split_user_notional_below_min_returns_zero() -> None:
    """User sets notional so low that the rounded qty fails
    Binance MIN_NOTIONAL → returns all zeros so dispatch skips
    cleanly rather than firing a -4164-doomed order."""
    # $1 notional / $29000 entry = ~0.00003 BTC → floored to step
    # 0.001 → 0 → fails MIN_NOTIONAL=5.
    total, _, _, _ = signal_dispatch._compute_qty_split(
        "BTCUSDT", 29000.0, notional_usd=1.0,
    )
    assert total == 0.0


def test_qty_split_user_notional_zero_falls_back_to_default() -> None:
    """Zero / None notional → use engine default (preserves prior
    behaviour for users without an override row)."""
    total_default, _, _, _ = signal_dispatch._compute_qty_split(
        "BTCUSDT", 29000.0,
    )
    total_zero, _, _, _ = signal_dispatch._compute_qty_split(
        "BTCUSDT", 29000.0, notional_usd=0.0,
    )
    total_none, _, _, _ = signal_dispatch._compute_qty_split(
        "BTCUSDT", 29000.0, notional_usd=None,
    )
    assert total_zero == total_default
    assert total_none == total_default


@pytest.mark.asyncio
async def test_dispatch_uses_per_user_notional_override() -> None:
    """The doctrine: each user's qty is computed from their own
    ``notional_usd`` override, not a single value broadcast to all.

    Setup: user fb-A overrides to $100; user fb-B has no override
    (default $500).  After dispatch, fb-A's place_signal call must
    carry ~5× smaller total_qty than fb-B's.
    """
    def _resolve(uid: str, default: float) -> float:
        # fb-A: small wallet, $100 override.  fb-B: default.
        return 100.0 if uid == "fb-A" else default

    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B"]
    ):
        from src.execution import position_fsm
        from src.api import user_overrides
        with patch.object(
            user_overrides, "resolve_notional_usd", side_effect=_resolve,
        ), patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock,
        ) as mock_place:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=29000.0,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
            )
        assert placed == 2

        # Pull per-uid total_qty from the recorded calls.
        per_uid_qty = {
            call.kwargs["firebase_uid"]: call.kwargs["total_qty"]
            for call in mock_place.await_args_list
        }
        # $100 / $29000 ≈ 0.00345 BTC, floored to step 0.001 → 0.003.
        # $500 / $29000 ≈ 0.01724 BTC, floored to step 0.001 → 0.017.
        # Ratio ~5.67×; allow stepSize-rounding slack.
        assert per_uid_qty["fb-A"] < per_uid_qty["fb-B"]
        assert per_uid_qty["fb-A"] / per_uid_qty["fb-B"] < 0.25  # < 1/4


@pytest.mark.asyncio
async def test_dispatch_skips_user_when_their_notional_too_low() -> None:
    """If a user's override makes the qty fail MIN_NOTIONAL, that
    user is skipped but other users still get their orders placed."""
    def _resolve(uid: str, default: float) -> float:
        # fb-A: $1 (below MIN_NOTIONAL).  fb-B: default $500 (succeeds).
        return 1.0 if uid == "fb-A" else default

    with patch.object(
        signal_dispatch, "_active_uids", return_value=["fb-A", "fb-B"]
    ):
        from src.execution import position_fsm
        from src.api import user_overrides
        with patch.object(
            user_overrides, "resolve_notional_usd", side_effect=_resolve,
        ), patch.object(
            position_fsm, "place_signal", new_callable=AsyncMock,
        ) as mock_place:
            placed = await signal_dispatch.dispatch_signal_to_active_users(
                signal_id="sig-1",
                symbol="BTCUSDT",
                direction="LONG",
                entry_price=29000.0,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
            )
        assert placed == 1  # only fb-B
        called_uids = {
            call.kwargs["firebase_uid"] for call in mock_place.await_args_list
        }
        assert called_uids == {"fb-B"}


def test_active_uids_cached_within_ttl() -> None:
    """The user-roster cache reduces Firestore load.  Verify the
    underlying ``list_active_uids`` call is amortised across
    multiple dispatch attempts within the TTL window."""
    from src.security import firestore_keystore

    with patch.object(
        firestore_keystore, "list_active_uids", return_value=["fb-A"]
    ) as mock_list:
        # Two calls back-to-back.
        signal_dispatch._active_uids()
        signal_dispatch._active_uids()
        # Cache absorbed the second call.
        assert mock_list.call_count == 1


def test_active_uids_refreshes_after_ttl() -> None:
    """After 30s + 0.1s buffer, the cache expires and we re-query."""
    from src.security import firestore_keystore

    with patch.object(
        firestore_keystore, "list_active_uids", return_value=["fb-A"]
    ) as mock_list:
        signal_dispatch._active_uids()
        # Force the cache stamp into the past.
        signal_dispatch._cache.fetched_at_monotonic -= (
            signal_dispatch._ACTIVE_UIDS_TTL_S + 1
        )
        signal_dispatch._active_uids()
        assert mock_list.call_count == 2
