"""Billing webhook HMAC verification tests."""
from __future__ import annotations

import hashlib
import hmac

import pytest

from src.api.billing_callback import (
    SIGNATURE_HEADER,
    BillingWebhookVerifier,
)


SECRET = "shared-bot-secret-x" * 4


def _sign(body: bytes, secret: str = SECRET) -> str:
    return hmac.new(
        secret.encode("utf-8"), body, hashlib.sha256,
    ).hexdigest()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def test_unconfigured_verifier_rejects_everything() -> None:
    v = BillingWebhookVerifier(secret="")
    assert v.is_configured() is False
    body = b'{"phone":"+1","tier":"paid","paid_until_iso":null}'
    assert v.verify(body, _sign(body)).ok is False


def test_configured_verifier_reports_configured() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    assert v.is_configured() is True


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------


def test_valid_signature_passes() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    body = b'{"phone":"+15551110000","tier":"paid","paid_until_iso":"2026-06-01T00:00:00+00:00"}'
    res = v.verify(body, _sign(body))
    assert res.ok is True


def test_missing_signature_header_rejected() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    body = b'{"phone":"+1","tier":"paid","paid_until_iso":null}'
    assert v.verify(body, None).ok is False
    assert v.verify(body, "").ok is False


def test_signature_mismatch_rejected() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    body = b'{"phone":"+1","tier":"paid","paid_until_iso":null}'
    assert v.verify(body, "deadbeef" * 8).ok is False


def test_signature_signed_with_wrong_secret_rejected() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    body = b'{"phone":"+1","tier":"paid","paid_until_iso":null}'
    bad_sig = _sign(body, secret="wrong" * 12)
    assert v.verify(body, bad_sig).ok is False


def test_body_tampering_rejected() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    original = b'{"phone":"+1","tier":"free","paid_until_iso":null}'
    sig = _sign(original)
    tampered = b'{"phone":"+1","tier":"paid","paid_until_iso":null}'
    assert v.verify(tampered, sig).ok is False


def test_signature_case_and_whitespace_tolerated() -> None:
    v = BillingWebhookVerifier(secret=SECRET)
    body = b'{"phone":"+1","tier":"paid","paid_until_iso":null}'
    sig = _sign(body)
    assert v.verify(body, "  " + sig.upper() + "\n").ok is True


# Re-export so the constant is part of the public API and a typo'd
# import surfaces in tests.
def test_signature_header_constant_exposed() -> None:
    assert SIGNATURE_HEADER == "X-Lumin-Sig"


pytest.importorskip("fastapi")  # smoke tests for the endpoint live in test_api_smoke
