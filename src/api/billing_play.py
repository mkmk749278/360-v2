"""Google Play Billing verification — server-side entitlement (B16).

The engine is the **source of truth** for subscription entitlement.  The
app can only *claim* a purchase; this module proves it against the Google
Play Developer API and decides what tier the user actually gets.

Flow
────
1. App buys a subscription via Play Billing → gets a ``purchaseToken``.
2. App ``POST /api/billing/play/verify`` (authed with the user JWT).
3. :meth:`PlayBillingVerifier.get_subscription` calls
   ``purchases.subscriptionsv2.get`` → we read state + expiry, decide
   entitlement, and :meth:`acknowledge` the purchase so Google doesn't
   auto-refund it after 3 days.
4. Renewals / cancellations / holds / expiries arrive later as RTDN
   (Real-Time Developer Notifications) on a Pub/Sub push; we re-run
   :meth:`get_subscription` for the token and re-apply entitlement.

Auth to Google
──────────────
A service account with Android Publisher access mints an OAuth2 access
token (RS256-signed assertion → token endpoint).  ``google-auth`` (a
transitive dependency via ``firebase-admin``) does the signing; we cache
the token until shortly before expiry.  Both the token provider and the
HTTP transport are injectable so unit tests never touch the network or
need a real key.

Security
────────
The service-account JSON is consumed from a path in config and held only
in memory.  It is never logged, never echoed in an error, never written
elsewhere (Hard Limits).  The purchase token is opaque and grants nothing
on its own — entitlement is always re-derived from Google.
"""

from __future__ import annotations

import base64
import binascii
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Optional

import httpx

from src.utils import get_logger

log = get_logger("api.billing_play")


_ANDROID_PUBLISHER_SCOPE = "https://www.googleapis.com/auth/androidpublisher"
_API_ROOT = "https://androidpublisher.googleapis.com/androidpublisher/v3"
_HTTP_TIMEOUT_S = 15.0

# Play subscriptionState values (subscriptionsv2).  Grouped by whether the
# user should currently have access.
_ENTITLED_STATES = frozenset({
    "SUBSCRIPTION_STATE_ACTIVE",
    "SUBSCRIPTION_STATE_IN_GRACE_PERIOD",
    # CANCELED = auto-renew off but still paid through ``expiryTime`` — the
    # user keeps access until then; the expiry check below enforces the cutoff.
    "SUBSCRIPTION_STATE_CANCELED",
})
_NOT_ENTITLED_STATES = frozenset({
    "SUBSCRIPTION_STATE_ON_HOLD",
    "SUBSCRIPTION_STATE_PAUSED",
    "SUBSCRIPTION_STATE_EXPIRED",
    "SUBSCRIPTION_STATE_PENDING",          # never paid yet (pending purchase)
    "SUBSCRIPTION_STATE_PENDING_PURCHASE_CANCELED",
})

# RTDN subscriptionNotification.notificationType → human label (logging only;
# entitlement is always re-derived from the live API, never from the type).
_RTDN_TYPES = {
    1: "RECOVERED", 2: "RENEWED", 3: "CANCELED", 4: "PURCHASED",
    5: "ON_HOLD", 6: "IN_GRACE_PERIOD", 7: "RESTARTED",
    8: "PRICE_CHANGE_CONFIRMED", 9: "DEFERRED", 10: "PAUSED",
    11: "PAUSE_SCHEDULE_CHANGED", 12: "REVOKED", 13: "EXPIRED",
    20: "PENDING_PURCHASE_CANCELED",
}


class PlayBillingError(Exception):
    """Raised when verification cannot complete.

    ``retryable`` distinguishes a transient Google-side failure (5xx /
    network — the caller may return 503 so the client retries) from a
    definitive rejection (4xx / bad token — return 4xx, don't retry).
    """

    def __init__(self, detail: str, *, retryable: bool = False) -> None:
        super().__init__(detail)
        self.detail = detail
        self.retryable = retryable


def is_entitled_snapshot(raw_state: str, expiry: Optional[datetime]) -> bool:
    """Whether a (state, expiry) snapshot means the user has paid access.

    Shared between the live :class:`PlaySubscriptionState` and the
    *stored* snapshots in ``play_purchases`` (referral-reward entitlement
    re-resolution consults the last observed state without a Google call).
    """
    if raw_state not in _ENTITLED_STATES:
        return False
    if expiry is None:
        # ACTIVE with no expiry shouldn't happen, but fail safe to
        # entitled only when the state is explicitly active.
        return raw_state == "SUBSCRIPTION_STATE_ACTIVE"
    return expiry > datetime.now(timezone.utc)


@dataclass(frozen=True)
class PlaySubscriptionState:
    """Normalised view of a ``purchases.subscriptionsv2.get`` response."""

    purchase_token: str
    product_id: str
    raw_state: str
    expiry: Optional[datetime]
    acknowledged: bool
    linked_purchase_token: Optional[str]
    # Play offer the purchase was made under (``lineItems[].offerDetails
    # .offerId``); None for a plain base-plan purchase.  Referral rewards
    # use this to tell a 50%-off first cycle from a full-price one — the
    # commission must be computed on what the referee actually paid.
    offer_id: Optional[str] = None

    @property
    def is_entitled(self) -> bool:
        """True when the user should currently have paid access."""
        return is_entitled_snapshot(self.raw_state, self.expiry)


@dataclass(frozen=True)
class RtdnNotification:
    """Parsed Real-Time Developer Notification (one Pub/Sub message)."""

    package_name: str
    is_test: bool
    is_voided: bool
    notification_type: Optional[int]
    notification_label: str
    purchase_token: Optional[str]
    subscription_id: Optional[str]


# Provider signatures (injectable for tests).
TokenProvider = Callable[[], Awaitable[str]]
HttpSend = Callable[..., Awaitable[httpx.Response]]


class PlayBillingVerifier:
    """Verifies Play purchases against the Google Play Developer API.

    Parameters
    ----------
    package_name:
        Android application id, e.g. ``org.luminapp.lumin``.
    service_account_info:
        Parsed service-account JSON dict, or ``None`` when unconfigured.
    product_tiers:
        Map of ``product_id → tier`` (e.g. ``{"lumin_auto_monthly": "auto",
        "lumin_assist_monthly": "assist"}``).  A purchase for a product not
        in this map is rejected.  Empty = accept any product the API
        confirms and grant ``default_tier`` (convenient for first wiring).
    default_tier:
        Tier granted when ``product_tiers`` is empty or doesn't list the
        product (kept for the empty-map convenience case).
    token_provider / http_send:
        Test seams — when provided, replace the real OAuth2 token mint and
        the real HTTP transport respectively.
    """

    def __init__(
        self,
        *,
        package_name: str,
        service_account_info: Optional[dict] = None,
        product_tiers: Optional[dict[str, str]] = None,
        default_tier: str = "auto",
        token_provider: Optional[TokenProvider] = None,
        http_send: Optional[HttpSend] = None,
    ) -> None:
        self._package = package_name
        self._sa_info = service_account_info
        self._product_tiers = dict(product_tiers or {})
        self._allowed = frozenset(self._product_tiers)
        self._default_tier = default_tier
        self._token_provider = token_provider
        self._http_send = http_send
        self._client: Optional[httpx.AsyncClient] = None
        # Cached OAuth2 token + unix expiry (only used by the default provider).
        self._cached_token: Optional[str] = None
        self._cached_token_exp: float = 0.0
        self._creds: Any = None  # lazily-built google-auth credentials

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def is_configured(self) -> bool:
        """True when this verifier can actually reach Google.

        Requires a package name and either an injected token provider
        (tests) or a service-account that ``google-auth`` can load.
        """
        if not self._package:
            return False
        if self._token_provider is not None:
            return True
        return bool(self._sa_info)

    @property
    def allowed_product_ids(self) -> frozenset[str]:
        return self._allowed

    def tier_for_product(self, product_id: str) -> str:
        """Tier a given product grants (assist / auto)."""
        return self._product_tiers.get(product_id, self._default_tier)

    def entitlement_for(
        self, state: PlaySubscriptionState
    ) -> tuple[str, Optional[datetime]]:
        """Map a subscription state to ``(tier, paid_until)`` for UserStore.

        Entitled → the product's tier (``assist`` / ``auto``), ``paid_until
        = expiry``.  Otherwise → free, ``paid_until = None``.  Single place
        the decision is made, used by both the verify endpoint and RTDN.
        """
        if state.is_entitled:
            return self.tier_for_product(state.product_id), state.expiry
        return "free", None

    # ------------------------------------------------------------------
    # Google Play Developer API
    # ------------------------------------------------------------------

    async def get_subscription(
        self, *, product_id: str, purchase_token: str
    ) -> PlaySubscriptionState:
        """Fetch + normalise a subscription via ``subscriptionsv2.get``."""
        if not self.is_configured():
            raise PlayBillingError("play billing not configured")

        url = (
            f"{_API_ROOT}/applications/{self._package}"
            f"/purchases/subscriptionsv2/tokens/{purchase_token}"
        )
        resp = await self._authed_get(url)

        if resp.status_code == 200:
            return self._parse_subscription(purchase_token, resp.json())
        if resp.status_code in (400, 404, 410):
            # Bad/unknown/expired-from-Google's-view token — definitive.
            raise PlayBillingError(
                f"play api rejected token (HTTP {resp.status_code})",
                retryable=False,
            )
        if resp.status_code in (401, 403):
            # Our service account lacks access / token expired — operator
            # config problem, not the user's fault.  Don't leak the body.
            raise PlayBillingError(
                f"play api auth error (HTTP {resp.status_code}) — check "
                "service-account Android Publisher access",
                retryable=True,
            )
        raise PlayBillingError(
            f"play api error (HTTP {resp.status_code})", retryable=True
        )

    def _parse_subscription(
        self, purchase_token: str, body: dict
    ) -> PlaySubscriptionState:
        raw_state = str(body.get("subscriptionState", ""))
        line_items = body.get("lineItems") or []

        product_id = ""
        expiry: Optional[datetime] = None
        offer_id: Optional[str] = None
        for item in line_items:
            pid = item.get("productId")
            if pid and not product_id:
                product_id = str(pid)
            exp = _parse_rfc3339(item.get("expiryTime"))
            if exp is not None and (expiry is None or exp > expiry):
                expiry = exp
            offer = item.get("offerDetails")
            if offer_id is None and isinstance(offer, dict) and offer.get("offerId"):
                offer_id = str(offer["offerId"])

        ack_state = str(body.get("acknowledgementState", ""))
        acknowledged = ack_state == "ACKNOWLEDGEMENT_STATE_ACKNOWLEDGED"
        linked = body.get("linkedPurchaseToken")

        return PlaySubscriptionState(
            purchase_token=purchase_token,
            product_id=product_id,
            raw_state=raw_state,
            expiry=expiry,
            acknowledged=acknowledged,
            linked_purchase_token=str(linked) if linked else None,
            offer_id=offer_id,
        )

    async def acknowledge(self, *, product_id: str, purchase_token: str) -> None:
        """Acknowledge a subscription purchase.

        Unacknowledged purchases are auto-refunded by Google after 3 days,
        so this must run after a successful grant.  Idempotent on Google's
        side; a 4xx here is logged but not raised — the grant already
        happened and a missed ack will be retried on the next RTDN.
        """
        if not self.is_configured():
            return
        url = (
            f"{_API_ROOT}/applications/{self._package}"
            f"/purchases/subscriptions/{product_id}/tokens/{purchase_token}"
            ":acknowledge"
        )
        try:
            resp = await self._authed_post(url, json_body={"developerPayload": ""})
        except Exception as exc:  # network — non-fatal, RTDN will retry
            log.warning("Play acknowledge failed (will retry on RTDN): {}", exc)
            return
        if resp.status_code not in (200, 204):
            log.warning(
                "Play acknowledge non-2xx (HTTP {}) — RTDN will retry",
                resp.status_code,
            )

    # ------------------------------------------------------------------
    # RTDN parsing (no network)
    # ------------------------------------------------------------------

    @staticmethod
    def parse_rtdn(envelope: dict) -> Optional[RtdnNotification]:
        """Decode a Pub/Sub push envelope into an :class:`RtdnNotification`.

        Returns ``None`` when the body carries no decodable developer
        notification (so the caller can ACK-and-ignore rather than 4xx,
        which would make Pub/Sub redeliver forever).
        """
        message = envelope.get("message")
        if not isinstance(message, dict):
            return None
        data_b64 = message.get("data")
        if not data_b64:
            return None
        try:
            decoded = base64.b64decode(data_b64)
            payload = json.loads(decoded)
        except (binascii.Error, ValueError, json.JSONDecodeError):
            return None
        if not isinstance(payload, dict):
            return None

        package_name = str(payload.get("packageName", ""))

        if "testNotification" in payload:
            return RtdnNotification(
                package_name=package_name, is_test=True, is_voided=False,
                notification_type=None, notification_label="TEST",
                purchase_token=None, subscription_id=None,
            )

        voided = payload.get("voidedPurchaseNotification")
        if isinstance(voided, dict):
            return RtdnNotification(
                package_name=package_name, is_test=False, is_voided=True,
                notification_type=None, notification_label="VOIDED",
                purchase_token=voided.get("purchaseToken"),
                subscription_id=None,
            )

        sub = payload.get("subscriptionNotification")
        if isinstance(sub, dict):
            ntype = sub.get("notificationType")
            try:
                ntype_int: Optional[int] = int(ntype)
            except (TypeError, ValueError):
                ntype_int = None
            return RtdnNotification(
                package_name=package_name, is_test=False, is_voided=False,
                notification_type=ntype_int,
                notification_label=_RTDN_TYPES.get(ntype_int or -1, "UNKNOWN"),
                purchase_token=sub.get("purchaseToken"),
                subscription_id=sub.get("subscriptionId"),
            )
        # One-time-product or unrecognised — nothing for us to do.
        return None

    # ------------------------------------------------------------------
    # HTTP + auth plumbing
    # ------------------------------------------------------------------

    async def _authed_get(self, url: str) -> httpx.Response:
        token = await self._access_token()
        headers = {"Authorization": f"Bearer {token}"}
        if self._http_send is not None:
            return await self._http_send("GET", url, headers=headers)
        client = await self._http_client()
        return await client.get(url, headers=headers)

    async def _authed_post(self, url: str, *, json_body: dict) -> httpx.Response:
        token = await self._access_token()
        headers = {"Authorization": f"Bearer {token}"}
        if self._http_send is not None:
            return await self._http_send("POST", url, headers=headers, json=json_body)
        client = await self._http_client()
        return await client.post(url, headers=headers, json=json_body)

    async def _http_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=_HTTP_TIMEOUT_S)
        return self._client

    async def _access_token(self) -> str:
        if self._token_provider is not None:
            return await self._token_provider()
        # Cache until ~60s before expiry to avoid re-minting per request
        # (Cost Discipline: the token endpoint is a network call).
        now = time.time()
        if self._cached_token and now < self._cached_token_exp - 60:
            return self._cached_token
        token, exp = await self._mint_token()
        self._cached_token = token
        self._cached_token_exp = exp
        return token

    async def _mint_token(self) -> tuple[str, float]:
        """Mint an OAuth2 access token from the service account.

        ``google-auth`` performs the RS256 assertion + token exchange.  It
        is synchronous, so run it off the event loop.
        """
        import asyncio

        if not self._sa_info:
            raise PlayBillingError("play billing not configured", retryable=True)

        def _refresh() -> tuple[str, float]:
            try:
                from google.auth.transport.requests import Request as _GReq
                from google.oauth2 import service_account as _sa
            except ImportError as exc:  # pragma: no cover — google-auth is a dep
                raise PlayBillingError(
                    f"google-auth unavailable: {exc}", retryable=True
                )
            if self._creds is None:
                self._creds = _sa.Credentials.from_service_account_info(
                    self._sa_info, scopes=[_ANDROID_PUBLISHER_SCOPE]
                )
            self._creds.refresh(_GReq())
            exp = self._creds.expiry
            # ``expiry`` is naive UTC; convert to a unix timestamp.
            exp_unix = (
                exp.replace(tzinfo=timezone.utc).timestamp()
                if exp is not None
                else time.time() + 1800
            )
            return self._creds.token, exp_unix

        try:
            return await asyncio.to_thread(_refresh)
        except PlayBillingError:
            raise
        except Exception as exc:
            # Never surface key material in the error.
            raise PlayBillingError(
                f"failed to mint Google access token: {type(exc).__name__}",
                retryable=True,
            )

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_rfc3339(raw: Optional[str]) -> Optional[datetime]:
    """Parse a Play RFC-3339 timestamp (``2026-07-23T10:00:00.000Z``)."""
    if not raw:
        return None
    s = str(raw).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_service_account_info(path: str) -> Optional[dict]:
    """Load + parse a service-account JSON file, or ``None`` on any failure.

    Failures (missing file, bad JSON) are logged WITHOUT the path contents
    and return ``None`` so the verifier reports ``is_configured() == False``
    and the endpoints fail closed rather than crashing boot.
    """
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            info = json.load(fh)
        if isinstance(info, dict) and info.get("client_email"):
            return info
        log.warning("Play service-account JSON missing client_email — ignoring")
        return None
    except FileNotFoundError:
        log.warning("Play service-account file not found at configured path")
        return None
    except (ValueError, OSError) as exc:
        log.warning("Play service-account load failed: {}", type(exc).__name__)
        return None
