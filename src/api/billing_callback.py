"""Billing webhook — HMAC verification for ``POST /internal/billing/grant``.

Topology: ``@LuminProBot`` (or any future billing platform — Paddle,
Lemon Squeezy, Coinbase Commerce — fronted by a tiny adapter) signs
webhook bodies with a shared secret; the engine verifies the signature
and updates the user's tier + ``paid_until``.  No JWT in the picture —
the bot is a server, not a user, so a shared HMAC secret is the right
authenticator.

The signature is HMAC-SHA256 over the raw request body, hex-encoded,
sent in the ``X-Lumin-Sig`` header.  Constant-time compare guards
against timing oracles.

The same shape works whether the bot runs on the same VPS (loopback)
or remote (TLS + IP allowlist) — security model is independent of
network topology.
"""

from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass
from typing import Optional

from src.utils import get_logger

log = get_logger("api.billing_callback")


SIGNATURE_HEADER = "X-Lumin-Sig"


# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    detail: str = ""


class BillingWebhookVerifier:
    """HMAC-SHA256 verifier for the billing webhook.

    Construct once at app build with the shared secret; call
    :meth:`verify` per request.  Returns a result object instead of
    raising so the caller controls the HTTP status (typically 401 on
    failure).
    """

    def __init__(self, secret: str) -> None:
        # Empty secret means the webhook is unconfigured — every
        # incoming request fails closed.  Tested explicitly so an
        # accidental config drop doesn't silently accept all bots.
        self._secret = secret.encode("utf-8") if secret else b""

    def is_configured(self) -> bool:
        return bool(self._secret)

    def verify(
        self,
        raw_body: bytes,
        presented_signature: Optional[str],
    ) -> VerificationResult:
        if not self._secret:
            return VerificationResult(
                ok=False,
                detail="webhook unconfigured (BILLING_WEBHOOK_SECRET unset)",
            )
        if not presented_signature:
            return VerificationResult(
                ok=False,
                detail=f"missing {SIGNATURE_HEADER} header",
            )
        expected = hmac.new(self._secret, raw_body, hashlib.sha256).hexdigest()
        # Strip whitespace/casing variations from the header.
        cleaned = presented_signature.strip().lower()
        if not hmac.compare_digest(expected, cleaned):
            log.warning("Billing webhook HMAC mismatch")
            return VerificationResult(ok=False, detail="signature mismatch")
        return VerificationResult(ok=True)
