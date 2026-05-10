"""OTP delivery tests — LogOnly + Chained fall-through.

WhatsApp / SNS providers are exercised with stubbed transports — we
don't make real HTTP calls in unit tests.  The chained provider's
fall-through logic is the most subtle part and gets dedicated coverage.
"""
from __future__ import annotations

import pytest

from src.api.otp_delivery import (
    ChainedOtpProvider,
    DeliveryResult,
    DeliveryStatus,
    LogOnlyOtpProvider,
)


pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# LogOnly
# ---------------------------------------------------------------------------


async def test_log_only_returns_ok() -> None:
    provider = LogOnlyOtpProvider()
    res = await provider.send("+15551110000", "123456")
    assert res.status is DeliveryStatus.OK
    assert res.channel_used == "log"


# ---------------------------------------------------------------------------
# Stub providers for chain tests
# ---------------------------------------------------------------------------


class _StubProvider:
    """Records calls + returns a configured result."""

    def __init__(self, result: DeliveryResult) -> None:
        self._result = result
        self.calls: list[tuple[str, str]] = []

    async def send(self, phone_e164: str, code: str) -> DeliveryResult:
        self.calls.append((phone_e164, code))
        return self._result


# ---------------------------------------------------------------------------
# Chain — happy path
# ---------------------------------------------------------------------------


async def test_chain_uses_primary_when_ok() -> None:
    primary = _StubProvider(
        DeliveryResult(status=DeliveryStatus.OK, channel_used="whatsapp"),
    )
    fallback = _StubProvider(
        DeliveryResult(status=DeliveryStatus.OK, channel_used="sms"),
    )
    chain = ChainedOtpProvider(primary, fallback)
    res = await chain.send("+15551110000", "123456")
    assert res.channel_used == "whatsapp"
    assert len(primary.calls) == 1
    assert len(fallback.calls) == 0


async def test_chain_falls_through_on_unsupported_channel() -> None:
    primary = _StubProvider(
        DeliveryResult(
            status=DeliveryStatus.UNSUPPORTED_CHANNEL,
            channel_used="whatsapp",
            detail="recipient lacks WhatsApp",
        ),
    )
    fallback = _StubProvider(
        DeliveryResult(status=DeliveryStatus.OK, channel_used="sms"),
    )
    chain = ChainedOtpProvider(primary, fallback)
    res = await chain.send("+15551110000", "123456")
    assert res.channel_used == "sms"
    assert res.status is DeliveryStatus.OK
    assert len(primary.calls) == 1
    assert len(fallback.calls) == 1


async def test_chain_does_not_fall_through_on_provider_error() -> None:
    """Don't burn an SMS just because Twilio rate-limited us."""
    primary = _StubProvider(
        DeliveryResult(
            status=DeliveryStatus.PROVIDER_ERROR,
            channel_used="whatsapp",
            detail="rate limited",
        ),
    )
    fallback = _StubProvider(
        DeliveryResult(status=DeliveryStatus.OK, channel_used="sms"),
    )
    chain = ChainedOtpProvider(primary, fallback)
    res = await chain.send("+15551110000", "123456")
    assert res.status is DeliveryStatus.PROVIDER_ERROR
    assert len(fallback.calls) == 0


async def test_chain_with_no_fallback_surfaces_unsupported() -> None:
    primary = _StubProvider(
        DeliveryResult(
            status=DeliveryStatus.UNSUPPORTED_CHANNEL,
            channel_used="whatsapp",
        ),
    )
    chain = ChainedOtpProvider(primary, fallback=None)
    res = await chain.send("+15551110000", "123456")
    assert res.status is DeliveryStatus.UNSUPPORTED_CHANNEL
