"""Tests for src.execution.reconciler.

The signing client + Firestore queries are mocked.  What we pin:

* User register/unregister adds/removes from the active set.
* Reconciliation skips terminal positions (CLOSED) — no point
  reconciling a position already in its final state.
* Reconciliation skips users with no positions.
* When Binance shows flat (positionAmt = 0) for a symbol Lumin
  thinks is OPEN → transition to CLOSED with reason="MANUAL".
* When Binance shows the position still open → no state change.
* positionRisk fetch failure logs + skips reconciliation for that
  cycle.
* The loop respects ``stop()``.
"""
from __future__ import annotations

import asyncio
from typing import List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import position_state
from src.execution import reconciler
from src.security.signing_service import protocol as sig_protocol


def _make_position(
    *,
    signal_id: str = "sig-1",
    symbol: str = "BTCUSDT",
    state: position_state.PositionState = position_state.PositionState.OPEN,
) -> position_state.Position:
    return position_state.Position(
        signal_id=signal_id,
        firebase_uid="fb-x",
        symbol=symbol,
        side="LONG",
        state=state,
        entry_price_target=29000.0,
        entry_price_filled=29000.0,
        sl_price=28500.0,
        tp1_price=29500.0,
        tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.4,
        tp3_qty=0.3,
        filled_qty=1.0,
    )


def _signing_client_returning(position_risk_body):
    mock = MagicMock()
    mock.binance_signed_get = AsyncMock(
        return_value=sig_protocol.SignResponse.ok_reply(
            "req-x",
            binance_status=200,
            binance_body=position_risk_body,
        )
    )
    return mock


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_then_unregister_user() -> None:
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [],
        signing_client_factory=lambda: MagicMock(),
    )
    await r.register_user("fb-1")
    await r.register_user("fb-2")
    assert r._active_uids == {"fb-1", "fb-2"}
    await r.unregister_user("fb-1")
    assert r._active_uids == {"fb-2"}


# ---------------------------------------------------------------------------
# Skip terminal positions
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_terminal_positions_skipped() -> None:
    """A position in CLOSED state is already terminal — no point
    fetching Binance state to compare against it.  Skip entirely."""
    closed = _make_position(state=position_state.PositionState.CLOSED)
    signing = _signing_client_returning([])
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [closed],
        signing_client_factory=lambda: signing,
    )
    await r.reconcile_user("fb-x")
    # Since all positions filtered out, Binance fetch never happens.
    signing.binance_signed_get.assert_not_called()


@pytest.mark.asyncio
async def test_no_positions_skips_binance_fetch() -> None:
    signing = _signing_client_returning([])
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [],
        signing_client_factory=lambda: signing,
    )
    await r.reconcile_user("fb-x")
    signing.binance_signed_get.assert_not_called()


# ---------------------------------------------------------------------------
# Manual close detection
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_manual_close_detected_when_binance_flat() -> None:
    """The core reconciliation property: FSM says position is OPEN
    on BTCUSDT but Binance says positionAmt=0 → must transition to
    CLOSED with close_reason=MANUAL."""
    open_pos = _make_position(symbol="BTCUSDT")
    persisted: List = []
    signing = _signing_client_returning(
        [{"symbol": "BTCUSDT", "positionAmt": "0"}]
    )
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [open_pos],
        signing_client_factory=lambda: signing,
    )
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        await r.reconcile_user("fb-x")
    assert len(persisted) == 1
    assert persisted[0].state == position_state.PositionState.CLOSED
    assert persisted[0].close_reason == "MANUAL"
    assert persisted[0].closed_at is not None


@pytest.mark.asyncio
async def test_position_open_in_binance_no_state_change() -> None:
    """FSM says OPEN and Binance also shows the position open
    (positionAmt > 0).  No divergence → no state change → no
    persistence."""
    open_pos = _make_position(symbol="BTCUSDT")
    persisted: List = []
    signing = _signing_client_returning(
        [{"symbol": "BTCUSDT", "positionAmt": "1.0"}]
    )
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [open_pos],
        signing_client_factory=lambda: signing,
    )
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        await r.reconcile_user("fb-x")
    # No divergence → no write.
    assert len(persisted) == 0


@pytest.mark.asyncio
async def test_short_position_open_recognised_via_negative_amt() -> None:
    """Binance encodes SHORT positions as negative positionAmt.
    Reconciler must NOT mark them manually-closed."""
    open_short = _make_position(symbol="BTCUSDT")
    open_short.side = "SHORT"
    persisted: List = []
    signing = _signing_client_returning(
        [{"symbol": "BTCUSDT", "positionAmt": "-1.0"}]
    )
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [open_short],
        signing_client_factory=lambda: signing,
    )
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        await r.reconcile_user("fb-x")
    assert len(persisted) == 0


# ---------------------------------------------------------------------------
# Binance fetch failure
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_binance_fetch_failure_skips_cycle() -> None:
    """positionRisk fetch error → reconciler skips the diff entirely.

    _fetch_binance_positions returns None on any error so the caller
    can distinguish "fetch failed" from "user has no open positions".
    Returning {} on error used to cause every non-terminal FSM position
    to be marked MANUAL CLOSE — fixed in PR #498.
    """
    open_pos = _make_position()
    persisted: List = []
    signing = MagicMock()
    signing.binance_signed_get = AsyncMock(
        return_value=sig_protocol.SignResponse.error_reply(
            "req-x",
            code=sig_protocol.ERR_BINANCE_UNREACHABLE,
            message="network",
        )
    )
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [open_pos],
        signing_client_factory=lambda: signing,
    )
    with patch.object(
        position_state, "put_position", side_effect=lambda p: persisted.append(p)
    ):
        await r.reconcile_user("fb-x")
    # Fetch failed → None returned → diff skipped → no state change.
    assert len(persisted) == 0


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stop_breaks_run_loop() -> None:
    r = reconciler.Reconciler(
        interval_s=0.05,
        positions_for_user=lambda uid: [],
        signing_client_factory=lambda: MagicMock(),
    )
    task = asyncio.create_task(r.run())
    await asyncio.sleep(0.02)
    await r.stop()
    await asyncio.wait_for(task, timeout=2.0)


# ---------------------------------------------------------------------------
# Module-level singleton (bootstrap wiring)
# ---------------------------------------------------------------------------


def test_set_and_get_instance() -> None:
    """set_instance / get_instance round-trip."""
    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [],
        signing_client_factory=lambda: MagicMock(),
    )
    original = reconciler.get_instance()
    try:
        reconciler.set_instance(r)
        assert reconciler.get_instance() is r
    finally:
        reconciler.set_instance(original)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_worker_manager_registers_user_with_reconciler() -> None:
    """start_user_worker calls reconciler.register_user when an instance is set."""
    from src.execution import worker_manager
    from unittest.mock import AsyncMock, patch

    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [],
        signing_client_factory=lambda: MagicMock(),
    )
    reconciler.set_instance(r)
    try:
        mock_worker = MagicMock()
        mock_worker.run = AsyncMock(return_value=None)
        mock_fsm = MagicMock()
        with (
            patch("src.execution.worker_manager.PositionWorker", return_value=mock_worker),
            patch("src.execution.worker_manager.PositionFSM", return_value=mock_fsm),
            patch.dict(worker_manager._workers, {}, clear=True),
        ):
            await worker_manager.start_user_worker("uid-reg-test")
        assert "uid-reg-test" in r._active_uids
    finally:
        reconciler.set_instance(None)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_stop_all_workers_unregisters_users() -> None:
    """stop_all_workers calls reconciler.unregister_user for every worker."""
    from src.execution import worker_manager
    from unittest.mock import AsyncMock, patch

    r = reconciler.Reconciler(
        positions_for_user=lambda uid: [],
        signing_client_factory=lambda: MagicMock(),
    )
    await r.register_user("uid-stop-test")
    reconciler.set_instance(r)
    try:
        mock_worker = MagicMock()
        mock_worker.stop = AsyncMock()
        mock_task = MagicMock()
        with patch.dict(
            worker_manager._workers,
            {"uid-stop-test": (mock_worker, mock_task)},
            clear=True,
        ):
            await worker_manager.stop_all_workers()
        assert "uid-stop-test" not in r._active_uids
    finally:
        reconciler.set_instance(None)  # type: ignore[arg-type]
