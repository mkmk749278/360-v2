"""Tests for the depth endpoint circuit breaker in BinanceClient.

Validates that once the breaker trips, concurrent in-flight requests
bail out on their next retry instead of continuing to time out and
inflating the consecutive-timeout counter.
"""

from __future__ import annotations

import asyncio
import time
import unittest.mock as mock

import pytest

from src.binance import BinanceClient, DEPTH_CIRCUIT_BREAKER_THRESHOLD


class _TimeoutContextManager:
    """Async context manager that raises TimeoutError on __aenter__."""

    async def __aenter__(self):
        raise asyncio.TimeoutError()

    async def __aexit__(self, *args):
        pass  # pragma: no cover


class _FakeSession:
    """Minimal stand-in for aiohttp.ClientSession."""

    def get(self, *args, **kwargs):
        return _TimeoutContextManager()

    @property
    def closed(self):
        return False


@pytest.fixture()
def client():
    c = BinanceClient(market="futures")
    # Bypass real session creation and rate-limiter waits.
    c._ensure_session = _make_fake_ensure()
    c._rate_limiter.acquire = lambda w: asyncio.sleep(0)
    return c


def _make_fake_ensure():
    session = _FakeSession()

    async def _ensure():
        return session

    return _ensure


class TestDepthCircuitBreakerConcurrency:
    """Concurrent requests must respect the breaker opened by another request."""

    async def test_concurrent_requests_stop_after_breaker_opens(self, client):
        """Simulate multiple concurrent depth calls where all time out.

        Once the threshold is reached by one coroutine, other coroutines
        that are in their retry loop must see the breaker is open and
        bail out — the consecutive-timeout counter must NOT exceed the
        threshold by more than the concurrency level of requests that
        were mid-flight when the breaker tripped.
        """
        # Pre-set the counter just below the threshold so the very first
        # timeout from any coroutine will trip the breaker.
        client._depth_consecutive_timeouts = DEPTH_CIRCUIT_BREAKER_THRESHOLD - 1

        # Patch asyncio.sleep to avoid real waits.
        with mock.patch("asyncio.sleep", return_value=asyncio.sleep(0)):
            tasks = [
                asyncio.create_task(
                    client._get("/fapi/v1/depth", params={"symbol": "BTCUSDT", "limit": 20})
                )
                for _ in range(10)
            ]
            await asyncio.gather(*tasks)

        # The first timeout trips the breaker (threshold reached).  All other
        # coroutines should detect the open breaker on their next retry
        # attempt and return immediately.  Before the fix, the counter would
        # climb to threshold + number_of_concurrent_requests.
        assert client._depth_consecutive_timeouts <= DEPTH_CIRCUIT_BREAKER_THRESHOLD + 1
        assert client._depth_circuit_open_until > time.monotonic()

    async def test_retry_loop_checks_breaker_each_attempt(self, client):
        """A single request that enters the retry loop must re-check the
        breaker before each attempt, not just at _get() entry."""
        attempt_count = 0
        original_get = _FakeSession.get

        def counting_get(self_sess, *args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            # After the first attempt triggers a timeout, open the
            # breaker as if another coroutine tripped it.
            if attempt_count == 1:
                client._depth_circuit_open_until = time.monotonic() + 60
            return original_get(self_sess, *args, **kwargs)

        with mock.patch.object(_FakeSession, "get", counting_get):
            with mock.patch("asyncio.sleep", return_value=asyncio.sleep(0)):
                result = await client._get(
                    "/fapi/v1/depth", params={"symbol": "ETHUSDT"}
                )

        assert result is None
        # Only one attempt should have been made; the second attempt sees
        # the open breaker and returns immediately.
        assert attempt_count == 1
        assert client._depth_consecutive_timeouts == 1
