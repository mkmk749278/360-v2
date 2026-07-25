"""Web billing — the PWA's own payment rails (Phase 3, docs/WEB_BILLING_DESIGN.md).

The web channel (``app.luminapp.org``) sells the SAME two paid tiers as
Google Play (``assist`` / ``auto``) but through its own rails, because
Play/Apple billing is store-bound and the website is neither.  Launch rail:
**crypto via NOWPayments**, plus the always-available owner manual grant
(``admin_grant_route`` — not re-implemented here).

**The one invariant (design §2):** every rail converges on the single
entitlement write path — ``UserStore.aset_tier(user_id, tier, paid_until)``
— exactly like Play verify, ``/internal/billing/grant``, and the admin
grant already do.  This module invents **no** new tier, no parallel
entitlement store, no second "is-paid" flag.  Its only job is to *prove a
crypto payment happened* and call that one path.

**Dark-flag-first (production money-path doctrine).** Everything is gated on
``config.WEB_BILLING_ENABLED`` (master) + ``WEB_BILLING_CRYPTO_ENABLED``.
Both default **false**: checkout + webhook return 503, and
``/api/billing/web/config`` surfaces only the manual rail.  The owner
activates from Ops after a sandbox purchase verifies end-to-end.  Live keys
go in only when ``WEB_BILLING_TEST_MODE=false`` after sign-off.

Endpoints
─────────
* ``GET  /api/billing/web/config``          — public; which rails + prices to show.
* ``POST /api/billing/web/checkout``        — authed; engine creates a NOWPayments
                                              invoice server-side, returns the
                                              hosted-checkout handoff.
* ``POST /api/billing/web/crypto/webhook``  — NOWPayments IPN; HMAC-verified,
                                              deduped, mapped to tier, granted.

Security (design §7)
────────────────────
* **The client never holds a provider secret** and **never asserts a price** —
  it names a *tier*; the engine reads the amount from ``config.WEB_BILLING_TIER_USD``.
* **The webhook is authoritative**, the client success-redirect is UX only —
  a user cannot self-upgrade by faking a return URL.  Entitlement is granted
  only on a signature-verified ``finished`` IPN.
* **Idempotency:** the IPN is deduped on NOWPayments' ``payment_id`` so a
  retried callback never double-extends.  The store is injectable; the
  in-memory default mirrors the repo's "Redis optional, in-memory fallback"
  posture — a persistent store is swapped in before live activation.
* Secrets (API key, IPN secret) are engine-env only, first-chars-only in any
  log line, never surfaced in an error body (Hard Limits).

Wiring follows the ``push_topic_routes`` / ``binance_connect_routes``
``register()`` convention.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Awaitable, Callable, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from pydantic import BaseModel, Field

import config
from src.utils import get_logger

log = get_logger("api.billing_web")


#: NOWPayments signs each IPN with this header (lower-case hex HMAC-SHA512).
NOWPAYMENTS_SIG_HEADER = "x-nowpayments-sig"

#: IPN payment_status values that mean the money has actually landed.  We
#: grant only on a terminal, fully-credited status — never on ``waiting`` /
#: ``confirming`` / ``partially_paid`` (which can still fail or under-pay).
_GRANT_STATUSES = frozenset({"finished", "confirmed"})

#: Tiers this rail can sell.  ``free`` is not purchasable; owner/paid are not
#: web SKUs.  Kept in lock-step with ``config.WEB_BILLING_TIER_USD``.
_SELLABLE_TIERS = frozenset({"assist", "auto"})


# ---------------------------------------------------------------------------
# order_id — carries (user_id, tier) through NOWPayments and back on the IPN
# ---------------------------------------------------------------------------
#
# We set order_id at checkout; NOWPayments echoes it verbatim on the IPN.
# Because the IPN body is HMAC-verified with our secret, the echoed order_id
# cannot be tampered — so it is a trustworthy carrier of *which user bought
# which tier*.  A random suffix makes each order unique.

_ORDER_PREFIX = "luminweb"

#: order_id flag: this checkout was priced with the referee's one-time
#: referral discount.  Carried through the IPN so the webhook's
#: amount-match defence knows which expected price applies (eligibility
#: may have been consumed between checkout and IPN — the order itself is
#: the record of what was charged).
_ORDER_FLAG_REFERRAL_DISCOUNT = "d"


def encode_order_id(user_id: int, tier: str, *, discounted: bool = False) -> str:
    flags = _ORDER_FLAG_REFERRAL_DISCOUNT if discounted else "-"
    return f"{_ORDER_PREFIX}:{user_id}:{tier}:{flags}:{secrets.token_hex(6)}"


def decode_order_id(order_id: str) -> Optional[tuple[int, str, bool]]:
    """Return ``(user_id, tier, discounted)`` from an order_id we minted,
    else ``None``.  Accepts the pre-2026-07-21 4-part shape (no flags —
    an IPN can arrive for an invoice minted before a deploy)."""
    parts = (order_id or "").split(":")
    if len(parts) not in (4, 5) or parts[0] != _ORDER_PREFIX:
        return None
    try:
        user_id = int(parts[1])
    except (TypeError, ValueError):
        return None
    tier = parts[2]
    if tier not in _SELLABLE_TIERS:
        return None
    discounted = len(parts) == 5 and _ORDER_FLAG_REFERRAL_DISCOUNT in parts[3]
    return user_id, tier, discounted


# ---------------------------------------------------------------------------
# NOWPayments IPN verifier
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VerificationResult:
    ok: bool
    detail: str = ""


def _sorted_json_bytes(payload: Any) -> bytes:
    """Serialise ``payload`` with keys sorted recursively, compact separators.

    NOWPayments computes the IPN HMAC over the JSON of the payload **sorted
    by key** — not over the raw bytes we received — so we must re-serialise
    in that canonical form before signing.
    """

    def _canon(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: _canon(obj[k]) for k in sorted(obj)}
        if isinstance(obj, list):
            return [_canon(v) for v in obj]
        return obj

    return json.dumps(_canon(payload), separators=(",", ":")).encode("utf-8")


class NowPaymentsIpnVerifier:
    """HMAC-SHA512 verifier for NOWPayments IPN callbacks.

    Construct once at app build with the IPN secret; call :meth:`verify` per
    request.  Returns a result rather than raising so the caller owns the
    HTTP status.  Empty secret → fails closed (every request rejected), so a
    dropped config never silently accepts forged callbacks.
    """

    def __init__(self, secret: str) -> None:
        self._secret = secret.encode("utf-8") if secret else b""

    def is_configured(self) -> bool:
        return bool(self._secret)

    def verify(
        self, raw_body: bytes, presented_signature: Optional[str]
    ) -> VerificationResult:
        if not self._secret:
            return VerificationResult(
                ok=False, detail="IPN unconfigured (NOWPAYMENTS_IPN_SECRET unset)"
            )
        if not presented_signature:
            return VerificationResult(
                ok=False, detail=f"missing {NOWPAYMENTS_SIG_HEADER} header"
            )
        try:
            payload = json.loads(raw_body)
        except (ValueError, TypeError):
            return VerificationResult(ok=False, detail="body is not valid JSON")
        expected = hmac.new(
            self._secret, _sorted_json_bytes(payload), hashlib.sha512
        ).hexdigest()
        cleaned = presented_signature.strip().lower()
        if not hmac.compare_digest(expected, cleaned):
            log.warning("NOWPayments IPN HMAC mismatch")
            return VerificationResult(ok=False, detail="signature mismatch")
        return VerificationResult(ok=True)


# ---------------------------------------------------------------------------
# Idempotency store — dedup IPNs on payment_id
# ---------------------------------------------------------------------------


class InMemoryIdempotencyStore:
    """Thread-safe check-and-set on NOWPayments ``payment_id``.

    :meth:`mark_if_new` returns True the first time a payment_id is seen and
    False on every retry — so a redelivered IPN is processed exactly once.
    In-memory per process, matching the repo's "Redis optional → in-memory
    fallback" posture; a persistent implementation (same interface) is swapped
    in before live activation so dedup survives a restart.
    """

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self._lock = threading.Lock()

    def mark_if_new(self, payment_id: str) -> bool:
        with self._lock:
            if payment_id in self._seen:
                return False
            self._seen.add(payment_id)
            return True

    def reset(self) -> None:  # test hook
        with self._lock:
            self._seen.clear()


# ---------------------------------------------------------------------------
# NOWPayments invoice creation (server-side; API key never leaves the engine)
# ---------------------------------------------------------------------------


async def _create_invoice_http(payload: dict) -> dict:
    """Create a NOWPayments invoice.  Injectable — tests pass a fake."""
    headers = {"x-api-key": config.NOWPAYMENTS_API_KEY, "Content-Type": "application/json"}
    url = f"{config.NOWPAYMENTS_API_BASE.rstrip('/')}/invoice"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
    except httpx.RequestError as exc:
        # Network-level failure (DNS, connect, timeout) — previously escaped as
        # an unhandled 500 (which the browser then reported as a bare "failed
        # to fetch").  Return a clean, CORS-carrying 502 instead.
        log.warning("NOWPayments invoice create — provider unreachable: {}", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="payment provider is unreachable — please try again in a moment",
        )
    if resp.status_code >= 400:
        # Never echo the provider body verbatim (may carry request context), but
        # DO surface the status code — a 401/403 here is a deployment-side
        # key/environment/IP problem, not the user's, and a bare "retry later"
        # hid that.  The engine sets the price, so this is never a client fault.
        log.warning("NOWPayments invoice create failed: HTTP {}", resp.status_code)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"payment provider rejected the checkout (HTTP {resp.status_code}) "
                "— please try again later"
            ),
        )
    return resp.json()


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class WebCheckoutRequest(BaseModel):
    tier: str = Field(..., description="assist | auto — the tier to purchase")


class WebCheckoutResponse(BaseModel):
    ok: bool
    tier: str
    amount_usd: float
    invoice_url: str
    invoice_id: str
    order_id: str
    #: True when the referee's one-time referral discount priced this
    #: invoice (Phase 2, 2026-07-21) — the paywall shows the applied cut.
    discounted: bool = False
    discount_percent: int = 0


# ---------------------------------------------------------------------------
# Wiring
# ---------------------------------------------------------------------------


def register(
    app: FastAPI,
    *,
    user_store: Any,
    auth: Callable,
    identity_dep: Callable,
    verifier: Optional[NowPaymentsIpnVerifier] = None,
    idempotency: Optional[InMemoryIdempotencyStore] = None,
    invoice_creator: Callable[[dict], Awaitable[dict]] = _create_invoice_http,
    referral_rewards: Any = None,
    signup_trial: Any = None,
) -> None:
    """Wire the web-billing endpoints onto ``app``.

    ``verifier`` / ``idempotency`` / ``invoice_creator`` are injectable so
    unit tests never touch the network or a real IPN secret; production build
    passes the config-backed defaults.
    """

    ipn = verifier or NowPaymentsIpnVerifier(config.NOWPAYMENTS_IPN_SECRET)
    dedup = idempotency or InMemoryIdempotencyStore()

    def _crypto_live() -> bool:
        return bool(config.WEB_BILLING_ENABLED and config.WEB_BILLING_CRYPTO_ENABLED)

    # ---- GET /api/billing/web/config -------------------------------------

    @app.get("/api/billing/web/config", tags=["billing"])
    async def web_billing_config(request: Request) -> dict[str, Any]:
        """Public — the rails + prices the web paywall should render.

        Manual is always present (owner-fulfilled).  Crypto appears only when
        the rail is live *and* configured, so a half-provisioned deploy never
        offers a checkout that would 503.  Region is echoed for UX only.
        """
        country = (
            request.headers.get("CF-IPCountry")
            or request.headers.get("X-Country-Code")
            or "unknown"
        ).strip().upper() or "unknown"

        rails: list[dict[str, Any]] = []
        if _crypto_live() and config.NOWPAYMENTS_API_KEY:
            rails.append(
                {
                    "id": "crypto",
                    "provider": "nowpayments",
                    "currency": config.WEB_BILLING_PRICE_CURRENCY.upper(),
                    "period_days": config.WEB_BILLING_PERIOD_DAYS,
                    "tiers": {
                        tier: {
                            "amount": usd,
                            "display": f"${usd:g}/mo",
                        }
                        for tier, usd in config.WEB_BILLING_TIER_USD.items()
                    },
                }
            )
        rails.append({"id": "manual", "note": "contact the owner for manual activation"})

        return {
            "country_code": country,
            "enabled": bool(config.WEB_BILLING_ENABLED),
            "test_mode": bool(config.WEB_BILLING_TEST_MODE),
            "rails": rails,
        }

    # ---- POST /api/billing/web/checkout ----------------------------------

    @app.post(
        "/api/billing/web/checkout",
        response_model=WebCheckoutResponse,
        tags=["billing"],
        dependencies=[Depends(auth)],
    )
    async def web_billing_checkout(
        body: WebCheckoutRequest,
        identity: Optional[Any] = Depends(identity_dep),
    ) -> WebCheckoutResponse:
        if not _crypto_live():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="web billing is not enabled",
            )
        if not config.NOWPAYMENTS_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="crypto payments are not configured on this deployment",
            )
        tier = body.tier.strip().lower()
        if tier not in _SELLABLE_TIERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"unknown tier {body.tier!r} — sellable: {sorted(_SELLABLE_TIERS)}",
            )

        firebase_uid = _resolve_firebase_uid(identity)
        if firebase_uid is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="sign in first")
        user = await user_store.aget_by_firebase_uid(firebase_uid)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

        amount_usd = config.WEB_BILLING_TIER_USD[tier]  # engine sets the money
        # Referee's one-time referral discount (Phase 2) — the engine owns
        # the price on this rail, so the discount is applied right here and
        # stamped into the order_id for the webhook's amount check.
        discounted = False
        if referral_rewards is not None:
            discounted = await referral_rewards.discount_eligible(user.user_id)
            if discounted:
                amount_usd = round(
                    amount_usd
                    * (1.0 - float(config.REFERRAL_DISCOUNT_PERCENT) / 100.0),
                    2,
                )
        order_id = encode_order_id(user.user_id, tier, discounted=discounted)
        payload = {
            "price_amount": amount_usd,
            "price_currency": config.WEB_BILLING_PRICE_CURRENCY,
            "order_id": order_id,
            "order_description": f"Lumin {tier} — {config.WEB_BILLING_PERIOD_DAYS} days",
            "ipn_callback_url": (
                f"{config.WEB_BILLING_CALLBACK_BASE.rstrip('/')}"
                "/api/billing/web/crypto/webhook"
            ),
            "success_url": config.WEB_BILLING_SUCCESS_URL,
            "cancel_url": config.WEB_BILLING_CANCEL_URL,
        }
        invoice = await invoice_creator(payload)
        invoice_url = invoice.get("invoice_url") or invoice.get("pay_url") or ""
        invoice_id = str(invoice.get("id") or invoice.get("invoice_id") or "")
        if not invoice_url:
            log.warning("NOWPayments invoice missing invoice_url (id={})", invoice_id)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="payment provider returned no checkout URL — retry later",
            )
        log.info(
            "web billing checkout: user_id={} tier={} amount_usd={} invoice_id={}",
            user.user_id, tier, amount_usd, invoice_id,
        )
        return WebCheckoutResponse(
            ok=True,
            tier=tier,
            amount_usd=amount_usd,
            invoice_url=invoice_url,
            invoice_id=invoice_id,
            order_id=order_id,
            discounted=discounted,
            discount_percent=(
                int(config.REFERRAL_DISCOUNT_PERCENT) if discounted else 0
            ),
        )

    # ---- POST /api/billing/web/crypto/webhook ----------------------------

    @app.post("/api/billing/web/crypto/webhook", tags=["billing"])
    async def web_billing_crypto_webhook(request: Request) -> dict[str, Any]:
        # The webhook is reachable even when the rail is "off" only insofar as
        # the verifier must be configured; without the IPN secret it 503s.
        if not ipn.is_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="crypto webhook not configured",
            )
        raw = await request.body()
        presented = request.headers.get(NOWPAYMENTS_SIG_HEADER)
        result = ipn.verify(raw, presented)
        if not result.ok:
            log.warning("NOWPayments IPN rejected: {}", result.detail)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"signature verification failed: {result.detail}",
            )

        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="invalid IPN body")

        payment_status = str(payload.get("payment_status", "")).lower()
        payment_id = str(payload.get("payment_id") or payload.get("id") or "")
        order_id = str(payload.get("order_id") or "")

        # Non-terminal / non-crediting statuses are acknowledged (200) so
        # NOWPayments stops retrying, but grant nothing.
        if payment_status not in _GRANT_STATUSES:
            log.debug(
                "web billing IPN: non-grant status={} payment_id={}",
                payment_status, payment_id[:12],
            )
            return {"ok": True, "granted": False, "reason": f"status={payment_status}"}

        decoded = decode_order_id(order_id)
        if decoded is None:
            log.warning("web billing IPN: unrecognised order_id={!r}", order_id)
            raise HTTPException(status_code=422, detail="unrecognised order_id")
        user_id, tier, discounted = decoded

        # Defence: the amount actually invoiced must match the tier's price —
        # a signed IPN for a tampered-down amount never upgrades a user.  A
        # referral-discounted order (flagged in the order_id WE minted and
        # HMAC-echoed back) is checked against the discounted price.
        expected_usd = config.WEB_BILLING_TIER_USD.get(tier)
        if expected_usd is not None and discounted:
            expected_usd = round(
                expected_usd
                * (1.0 - float(config.REFERRAL_DISCOUNT_PERCENT) / 100.0),
                2,
            )
        price_amount = _as_float(payload.get("price_amount"))
        if expected_usd is None or price_amount is None or price_amount + 1e-6 < expected_usd:
            log.warning(
                "web billing IPN: amount mismatch tier={} expected={} got={} payment_id={}",
                tier, expected_usd, price_amount, payment_id[:12],
            )
            raise HTTPException(status_code=422, detail="amount does not match tier price")

        if not payment_id:
            raise HTTPException(status_code=422, detail="IPN missing payment_id")
        if not dedup.mark_if_new(payment_id):
            log.info("web billing IPN: duplicate payment_id={} — already granted", payment_id[:12])
            return {"ok": True, "granted": False, "reason": "duplicate"}

        # Grant: extend from the later of (now, current expiry) so an early
        # renewal stacks the remaining days instead of losing them.
        now = datetime.now(timezone.utc)
        current = _coerce_dt(getattr(await user_store.aget_by_id(user_id), "paid_until", None))
        base = max(now, current) if current else now
        paid_until = base + timedelta(days=config.WEB_BILLING_PERIOD_DAYS)
        write_tier, write_until = tier, paid_until
        if referral_rewards is not None:
            # Referral hooks (Phase 2): commission accrues from the ACTUAL
            # USD amount paid on this rail; the entitlement write composes
            # with the reward ledger like every other aset_tier site.
            await referral_rewards.on_paid_period(
                user_id,
                product_id=f"web_{tier}",
                purchase_token=f"npw:{payment_id}",
                period_expiry=paid_until,
                amount=price_amount,
                currency="USD",
            )
            write_tier, write_until = await referral_rewards.compose_entitlement(
                user_id, tier, paid_until,
            )
        if signup_trial is not None:
            # Trial → paid conversion, same as the Play rail.  Fail-open
            # inside the service — a funnel stamp never blocks a grant.
            await signup_trial.on_paid_period(user_id)
        try:
            updated = await user_store.aset_tier(
                user_id, tier=write_tier, paid_until=write_until,
            )
        except LookupError:
            raise HTTPException(status_code=404, detail="user not found for order")

        log.info(
            "web billing GRANT: user_id={} tier={} paid_until={} payment_id={}",
            user_id, write_tier,
            write_until.isoformat() if write_until else None, payment_id[:12],
        )
        return {
            "ok": True,
            "granted": True,
            "user_id": getattr(updated, "user_id", user_id),
            "tier": write_tier,
            "paid_until": write_until.isoformat() if write_until else None,
        }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_firebase_uid(identity: Any) -> Any:
    """Extract the Firebase uid from an identity-dep resolution.

    Mirrors ``account_routes._resolve_firebase_uid`` / the binance-connect
    helper — same identity shape from the same auth dep.
    """
    if identity is None:
        return None
    uid = getattr(identity, "firebase_uid", None)
    if uid is None and isinstance(identity, dict):
        uid = identity.get("firebase_uid")
    return uid


def _as_float(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_dt(value: Any) -> Optional[datetime]:
    """Best-effort parse of a stored paid_until into an aware UTC datetime."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(value))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return None
