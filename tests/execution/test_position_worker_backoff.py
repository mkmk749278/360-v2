"""Auth-failure / IP-ban backoff in the PositionWorker reconnect loop.

Regression guard for the 2026-07-24 incident: a user's dead Binance key
(``401 -2015``) was retried every 60s, and that steady stream of guaranteed
failures earned Binance a ``-1003`` IP ban of the whole VPS — which then blocked
all market-data REST and cycled the engine. A single user's bad key must never
be able to do that (blast-radius). These pin:

* the error classification (auth failure vs IP ban vs transient),
* that a dead key backs off HARD (does not hammer), and
* that an active IP ban is waited out (parsed from Binance's "banned until"),

without waiting real minutes — ``stop()`` releases the long sleep immediately.
"""
from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.execution import listen_key as listen_key_mod
from src.execution import position_worker
from src.execution.position_worker import (
    _AUTH_FAIL_BACKOFF_S,
    _BAN_BACKOFF_S,
    _MAX_BACKOFF_S,
    _ban_backoff_seconds,
)


# --------------------------------------------------------------------------- #
# Error classification
# --------------------------------------------------------------------------- #
def test_classify_auth_failure() -> None:
    # Reliable signal is the HTTP status; the numeric -2015 in the message is
    # the backstop (SignResponse.error_code is a string ERR_* constant).
    by_status = listen_key_mod.ListenKeyAcquireError("x", binance_status=401)
    by_msg = listen_key_mod.ListenKeyAcquireError(
        "x", error_message="Binance returned 401 (code=-2015 msg='Invalid API-key')"
    )
    assert by_status.is_auth_failure and not by_status.is_ip_ban
    assert by_msg.is_auth_failure and not by_msg.is_ip_ban


def test_classify_ip_ban() -> None:
    by_status = listen_key_mod.ListenKeyAcquireError("x", binance_status=418)
    by_msg = listen_key_mod.ListenKeyAcquireError(
        "x", error_message="Way too many requests; (code=-1003 …) banned"
    )
    assert by_status.is_ip_ban and not by_status.is_auth_failure
    assert by_msg.is_ip_ban and not by_msg.is_auth_failure


def test_classify_transient_plain_error() -> None:
    # A signing-service blip with no Binance status is neither — the worker
    # falls back to its normal exponential ladder.
    exc = listen_key_mod.ListenKeyAcquireError("signing socket timeout")
    assert not exc.is_auth_failure and not exc.is_ip_ban


# --------------------------------------------------------------------------- #
# Ban-window parsing
# --------------------------------------------------------------------------- #
def test_ban_backoff_parses_banned_until() -> None:
    future_ms = int((time.time() + 600.0) * 1000)
    exc = listen_key_mod.ListenKeyAcquireError(
        f"…banned until {future_ms}.",
        binance_status=418,
        error_message=f"Way too many requests; IP(1.2.3.4) banned until {future_ms}.",
    )
    secs = _ban_backoff_seconds(exc)
    assert 590.0 <= secs <= 610.0


def test_ban_backoff_floor_when_unparseable() -> None:
    exc = listen_key_mod.ListenKeyAcquireError(
        "banned, no timestamp", binance_status=418,
        error_message="code=-1003 too many requests, no deadline given",
    )
    assert _ban_backoff_seconds(exc) == _BAN_BACKOFF_S


# --------------------------------------------------------------------------- #
# _backoff_for_error selection + counter
# --------------------------------------------------------------------------- #
def test_backoff_selection_and_counter() -> None:
    w = position_worker.PositionWorker(firebase_uid="fb-1")
    # Transient → None (use exponential ladder), counter untouched.
    assert w._backoff_for_error(listen_key_mod.ListenKeyAcquireError("blip")) is None
    assert w._consecutive_auth_failures == 0
    # Auth failure → long fixed backoff, counter increments.
    auth = listen_key_mod.ListenKeyAcquireError("dead", binance_status=401)
    assert w._backoff_for_error(auth) == _AUTH_FAIL_BACKOFF_S
    assert w._backoff_for_error(auth) == _AUTH_FAIL_BACKOFF_S
    assert w._consecutive_auth_failures == 2
    # The dead-key backoff must be far slower than the transient ceiling —
    # that ratio is what makes an IP ban impossible.
    assert _AUTH_FAIL_BACKOFF_S > _MAX_BACKOFF_S * 5
    # IP ban → long wait, and it doesn't touch the auth counter.
    ban = listen_key_mod.ListenKeyAcquireError("banned", binance_status=418)
    assert w._backoff_for_error(ban) >= _BAN_BACKOFF_S
    assert w._consecutive_auth_failures == 2


# --------------------------------------------------------------------------- #
# The real anti-hammer guarantee, exercised through the loop
# --------------------------------------------------------------------------- #
def _handle() -> MagicMock:
    h = MagicMock()
    h.listen_key = "lk"
    h.close = AsyncMock(return_value=None)
    return h


@pytest.mark.asyncio
async def test_dead_key_does_not_hammer() -> None:
    """A dead key (-2015) must be attempted ONCE in a >1s window, not every
    60s. Contrast test_acquire_failure_retried_with_backoff, where a transient
    error retries ≥2× in the same window."""
    worker = position_worker.PositionWorker(firebase_uid="fb-1")
    dead = listen_key_mod.ListenKeyAcquireError(
        "invalid key", binance_status=401,
        error_message="Invalid API-key, IP, or permissions for action",
    )
    with patch.object(
        listen_key_mod, "acquire", new_callable=AsyncMock, side_effect=dead,
    ) as mock_acquire, patch(
        "src.execution.position_worker.user_data_stream.consume",
        new_callable=AsyncMock,
    ):
        run_task = asyncio.create_task(worker.run())
        await asyncio.sleep(1.2)
        await worker.stop()  # releases the long backoff sleep immediately
        await asyncio.wait_for(run_task, timeout=5.0)
    # 900s backoff → only the initial attempt fired inside 1.2s.
    assert mock_acquire.call_count == 1
    assert worker._consecutive_auth_failures == 1


@pytest.mark.asyncio
async def test_ip_ban_is_waited_out_not_retried() -> None:
    """An active IP ban (-1003) is waited out, not retried into (which would
    extend it) — so also a single attempt in the window."""
    worker = position_worker.PositionWorker(firebase_uid="fb-1")
    future_ms = int((time.time() + 600.0) * 1000)
    banned = listen_key_mod.ListenKeyAcquireError(
        "banned", binance_status=418,
        error_message=f"banned until {future_ms}",
    )
    with patch.object(
        listen_key_mod, "acquire", new_callable=AsyncMock, side_effect=banned,
    ) as mock_acquire, patch(
        "src.execution.position_worker.user_data_stream.consume",
        new_callable=AsyncMock,
    ):
        run_task = asyncio.create_task(worker.run())
        await asyncio.sleep(1.2)
        await worker.stop()
        await asyncio.wait_for(run_task, timeout=5.0)
    assert mock_acquire.call_count == 1
