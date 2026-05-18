"""Tests for src.execution.listen_key.

The signing-service client is mocked so unit tests don't need a live
Unix socket.  What we pin:

* ``acquire`` sends a signed POST to ``/fapi/v1/listenKey`` with the
  user's firebase_uid + returns a handle carrying the listenKey.
* Acquire failure (signing service error, malformed response) raises
  :class:`ListenKeyAcquireError` with a useful message.
* The keepalive task fires the configured PUT every interval; we
  test with a short interval so the task fires within test time.
* ``close`` cancels the keepalive task AND sends DELETE.  Idempotent:
  calling close twice is safe.
* Errors in keepalive PUT are logged but don't tear down the task —
  worker's reconnect loop handles a real expiry via the
  ``listenKeyExpired`` event from the WS.
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.execution import listen_key
from src.security.signing_service.protocol import SignResponse


def _ok_resp(body: dict = None) -> SignResponse:
    # Note: ``body or {...}`` would mask an explicit empty-dict caller
    # (which is what test_acquire_raises_when_response_missing_listen_key_field
    # passes to simulate a malformed Binance response).
    if body is None:
        body = {"listenKey": "abc123def"}
    return SignResponse.ok_reply("req-x", binance_status=200, binance_body=body)


def _err_resp(code: str = "KEY_INVALID") -> SignResponse:
    return SignResponse.error_reply("req-x", code=code, message="bad key")


def _make_mock_client() -> MagicMock:
    """Build a mock signing client with async methods that return
    success by default.  Individual tests override per-method."""
    mock = MagicMock()
    mock.binance_signed_post = AsyncMock(return_value=_ok_resp())
    mock.binance_signed_delete = AsyncMock(
        return_value=SignResponse.ok_reply(
            "req-d", binance_status=200, binance_body={}
        )
    )
    return mock


# ---------------------------------------------------------------------------
# acquire
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_acquire_returns_handle_with_listen_key() -> None:
    mock = _make_mock_client()
    handle = await listen_key.acquire(
        "fb-uid-1", client=mock, keepalive_interval_s=3600
    )
    try:
        assert handle.listen_key == "abc123def"
        assert handle.firebase_uid == "fb-uid-1"
        # POST issued to the listenKey path with the right uid.
        mock.binance_signed_post.assert_called_once()
        kwargs = mock.binance_signed_post.call_args.kwargs
        assert kwargs["firebase_uid"] == "fb-uid-1"
        assert kwargs["base"] == "futures"
        assert kwargs["path"] == "/fapi/v1/listenKey"
    finally:
        await handle.close()


@pytest.mark.asyncio
async def test_acquire_raises_on_signing_error() -> None:
    mock = _make_mock_client()
    mock.binance_signed_post = AsyncMock(return_value=_err_resp())
    with pytest.raises(listen_key.ListenKeyAcquireError):
        await listen_key.acquire("fb-uid-1", client=mock, keepalive_interval_s=3600)


@pytest.mark.asyncio
async def test_acquire_raises_when_response_missing_listen_key_field() -> None:
    """Binance might return 200 but with a malformed body — defensive
    check that the field is present and is a non-empty string."""
    mock = _make_mock_client()
    mock.binance_signed_post = AsyncMock(return_value=_ok_resp(body={}))
    with pytest.raises(listen_key.ListenKeyAcquireError):
        await listen_key.acquire("fb-uid-1", client=mock, keepalive_interval_s=3600)


# ---------------------------------------------------------------------------
# keepalive
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_keepalive_task_fires_periodic_put() -> None:
    """With a tight 0.05s interval, the keepalive task should fire at
    least once before we close.  Validates the loop is actually
    scheduling PUTs."""
    mock = _make_mock_client()
    handle = await listen_key.acquire(
        "fb-uid-1", client=mock, keepalive_interval_s=0.05
    )
    try:
        await asyncio.sleep(0.15)  # gives ~2-3 keepalive ticks
    finally:
        await handle.close()
    # First call was the initial acquire; subsequent ones are keepalives.
    assert mock.binance_signed_post.call_count >= 2


@pytest.mark.asyncio
async def test_keepalive_failure_does_not_kill_task(caplog) -> None:
    """A PUT returning an error must NOT cancel the keepalive task —
    the worker's reconnect loop handles real expiry via the
    listenKeyExpired event.  Caller-side log captures the warning."""
    mock = _make_mock_client()
    # First call (acquire) succeeds; subsequent keepalive PUTs return error.
    mock.binance_signed_post = AsyncMock(
        side_effect=[
            _ok_resp(),  # acquire
            _err_resp(code="BINANCE_HTTP_ERROR"),  # keepalive 1
            _err_resp(code="BINANCE_HTTP_ERROR"),  # keepalive 2
        ]
    )
    handle = await listen_key.acquire(
        "fb-uid-1", client=mock, keepalive_interval_s=0.05
    )
    try:
        await asyncio.sleep(0.15)
        # Task should still be alive (the failed PUTs didn't propagate).
        assert handle._keepalive_task is not None
        assert not handle._keepalive_task.done()
    finally:
        await handle.close()


# ---------------------------------------------------------------------------
# close
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_close_cancels_keepalive_and_sends_delete() -> None:
    mock = _make_mock_client()
    handle = await listen_key.acquire(
        "fb-uid-1", client=mock, keepalive_interval_s=3600
    )
    # Pre-close, the keepalive task is running.
    assert handle._keepalive_task is not None
    assert not handle._keepalive_task.done()
    await handle.close()
    # Post-close, the task is no longer running + DELETE was issued.
    mock.binance_signed_delete.assert_called_once()
    delete_kwargs = mock.binance_signed_delete.call_args.kwargs
    assert delete_kwargs["firebase_uid"] == "fb-uid-1"
    assert delete_kwargs["path"] == "/fapi/v1/listenKey"


@pytest.mark.asyncio
async def test_close_is_idempotent() -> None:
    """Calling close twice should not raise; the second call is a
    no-op once the task is already cancelled."""
    mock = _make_mock_client()
    handle = await listen_key.acquire(
        "fb-uid-1", client=mock, keepalive_interval_s=3600
    )
    await handle.close()
    await handle.close()  # second close — must not raise
    # DELETE fires once (from the first close); the second close
    # short-circuits because _client is still set but no keepalive
    # task to cancel.  We tolerate either 1 or 2 DELETEs; the
    # important invariant is "no exception".


@pytest.mark.asyncio
async def test_close_swallows_delete_errors() -> None:
    """DELETE failing during shutdown must NOT propagate — Binance
    will reap the listenKey after 60min anyway, so a failed DELETE
    is operator-noise, not user-visible breakage."""
    mock = _make_mock_client()
    mock.binance_signed_delete = AsyncMock(side_effect=RuntimeError("network down"))
    handle = await listen_key.acquire(
        "fb-uid-1", client=mock, keepalive_interval_s=3600
    )
    # Must not raise.
    await handle.close()
