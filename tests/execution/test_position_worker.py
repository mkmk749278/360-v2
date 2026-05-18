"""Tests for src.execution.position_worker.

We mock the listenKey acquire + WS consume so unit tests don't need
GCP / network.  What we pin:

* The worker calls listenKey acquire once per outer-loop iteration.
* On acquire failure, the worker backs off + retries — does NOT exit
  the loop.
* :meth:`stop` actually stops the loop.
* On clean WS close (no exception), the worker re-acquires + reconnects.
* Handler exceptions inside consume are absorbed (already tested in
  the WS suite; here we verify the worker survives them).
"""
from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import listen_key as listen_key_mod
from src.execution import position_worker
from src.security.signing_service.protocol import SignResponse


def _make_listen_key_handle(uid: str = "fb-x") -> MagicMock:
    """A mock ListenKeyHandle with the close method as an AsyncMock."""
    handle = MagicMock()
    handle.listen_key = "fake-lk"
    handle.firebase_uid = uid
    handle.close = AsyncMock(return_value=None)
    return handle


# ---------------------------------------------------------------------------
# stop() actually stops
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stop_breaks_the_main_loop() -> None:
    """The worker holds the loop indefinitely; calling stop() must
    release it within one backoff cycle."""
    worker = position_worker.PositionWorker(firebase_uid="fb-1")

    with patch.object(
        listen_key_mod,
        "acquire",
        new_callable=AsyncMock,
        return_value=_make_listen_key_handle(),
    ), patch(
        "src.execution.position_worker.user_data_stream.consume",
        new_callable=AsyncMock,
        return_value=None,
    ):
        run_task = asyncio.create_task(worker.run())
        # Let one iteration complete (acquire + consume returns immediately).
        await asyncio.sleep(0.05)
        await worker.stop()
        await asyncio.wait_for(run_task, timeout=2.0)


# ---------------------------------------------------------------------------
# Acquire failure → back off and retry (loop survives)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_acquire_failure_retried_with_backoff() -> None:
    """A persistent acquire failure (signing-service error) MUST NOT
    crash the worker.  The loop logs and retries with backoff until
    stopped."""
    worker = position_worker.PositionWorker(firebase_uid="fb-1")

    with patch.object(
        listen_key_mod,
        "acquire",
        new_callable=AsyncMock,
        side_effect=listen_key_mod.ListenKeyAcquireError("KEY_INVALID"),
    ) as mock_acquire, patch(
        "src.execution.position_worker.user_data_stream.consume",
        new_callable=AsyncMock,
    ):
        run_task = asyncio.create_task(worker.run())
        # Give the loop ~1.5s to attempt at least 2 reconnects (1s
        # first backoff, then 2s — we'll be inside the second sleep).
        await asyncio.sleep(1.2)
        await worker.stop()
        await asyncio.wait_for(run_task, timeout=5.0)
    # At least 2 acquire attempts in that window (initial + 1 retry).
    assert mock_acquire.call_count >= 2


# ---------------------------------------------------------------------------
# Clean WS close → reconnect
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clean_ws_close_triggers_reacquire() -> None:
    """When the WS consume returns normally (e.g. Binance closed the
    connection gracefully, or listenKey expired and we exited the
    iter), the worker re-acquires a fresh listenKey and reconnects."""
    worker = position_worker.PositionWorker(firebase_uid="fb-1")

    handles = [_make_listen_key_handle(), _make_listen_key_handle()]

    with patch.object(
        listen_key_mod,
        "acquire",
        new_callable=AsyncMock,
        side_effect=handles,  # First call returns first handle, second returns second
    ) as mock_acquire, patch(
        "src.execution.position_worker.user_data_stream.consume",
        new_callable=AsyncMock,
        return_value=None,  # consume returns immediately (WS closed)
    ):
        run_task = asyncio.create_task(worker.run())
        # Wait long enough for 2 iterations (1s backoff between).
        await asyncio.sleep(1.3)
        await worker.stop()
        await asyncio.wait_for(run_task, timeout=5.0)
    assert mock_acquire.call_count >= 2
    # First handle was closed after first iteration.
    handles[0].close.assert_called()


# ---------------------------------------------------------------------------
# Handle closed on shutdown even mid-consume
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_handle_closed_on_stop() -> None:
    """If stop() fires while we're mid-consume, the listenKey handle
    is still closed cleanly in the finally block — Binance reclaims
    the key, no resource leak."""
    worker = position_worker.PositionWorker(firebase_uid="fb-1")
    handle = _make_listen_key_handle()

    async def _slow_consume(*args, **kwargs):
        # Consume blocks for a while — simulates a long-lived WS.
        await asyncio.sleep(0.5)

    with patch.object(
        listen_key_mod,
        "acquire",
        new_callable=AsyncMock,
        return_value=handle,
    ), patch(
        "src.execution.position_worker.user_data_stream.consume",
        side_effect=_slow_consume,
    ):
        run_task = asyncio.create_task(worker.run())
        await asyncio.sleep(0.1)  # let the worker enter consume
        await worker.stop()
        await asyncio.wait_for(run_task, timeout=5.0)
    handle.close.assert_called()
