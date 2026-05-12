"""OTP delivery providers — WhatsApp Authentication template + SMS fallback.

Three concrete implementations:

* ``LogOnlyOtpProvider`` — writes the OTP to engine logs.  Default for
  the closed-beta window while Meta Business Verification is in flight;
  owner reads codes from logs and forwards via the existing chat
  channel.  Zero cost, zero external dependency.

* ``WhatsAppOtpProvider`` — Twilio Messages API with the approved
  Authentication template.  WhatsApp is the primary channel because it
  is dramatically cheaper than SMS in our highest-volume target markets
  (IN, LATAM, EU) and has reliable delivery (~95-98%) once the user has
  WhatsApp installed.  The template body is approved by Meta:
  ``"Your Lumin verification code is {{1}}. This code expires in 5
  minutes. Do not share it."``

* ``SnsSmsOtpProvider`` — AWS SNS ``publish``.  Triggered automatically
  when the WhatsApp send returns ``UNSUPPORTED_CHANNEL`` (recipient
  doesn't have WhatsApp).  No business verification, no DLT/short-code
  approval — pay-as-go SMS on the standard SNS pricing.

A ``ChainedOtpProvider`` wires primary → fallback: tries primary, on
``UNSUPPORTED_CHANNEL`` rolls forward to fallback and reports the channel
that actually delivered.  Other failure modes (network, auth) surface as
``PROVIDER_ERROR`` and short-circuit — we don't fall through to SMS just
because Twilio rate-limited us.

External SDKs (``twilio``, ``boto3``) are imported lazily inside each
provider's ``send`` so installs that never use them don't pay the import
cost.  Phase 2's closed beta uses LogOnly only — neither SDK is needed
to run the engine.
"""

from __future__ import annotations

import asyncio
import enum
from dataclasses import dataclass
from typing import Literal, Optional, Protocol, runtime_checkable

from typing import Any  # noqa: F401  (used by Telegram provider annotations)
from src.utils import get_logger

log = get_logger("api.otp_delivery")


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class DeliveryStatus(str, enum.Enum):
    OK = "ok"
    # The recipient cannot receive on this channel — caller should fall
    # through to the next provider (e.g. WhatsApp → SMS).
    UNSUPPORTED_CHANNEL = "unsupported_channel"
    # Provider-side error (network, auth, rate-limit) — caller surfaces
    # to the user, does NOT fall through.
    PROVIDER_ERROR = "provider_error"


_Channel = Literal["whatsapp", "sms", "log", "telegram"]


@dataclass(frozen=True)
class DeliveryResult:
    status: DeliveryStatus
    channel_used: _Channel
    detail: str = ""


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@runtime_checkable
class OtpDeliveryProvider(Protocol):
    """Send an OTP to a phone via a specific channel.

    Implementations must be coroutine-safe; multiple ``send`` calls may
    be in flight concurrently from FastAPI request handlers.
    """

    async def send(self, phone_e164: str, code: str) -> DeliveryResult: ...


# ---------------------------------------------------------------------------
# LogOnly — closed-beta default, zero cost
# ---------------------------------------------------------------------------


class LogOnlyOtpProvider:
    """Writes the OTP to engine logs at INFO level.

    Closed-beta default while Meta Business Verification is pending.
    Owner watches logs and forwards the code via the existing chat
    channel.  Never use in production once verified senders go live —
    putting OTPs in logs makes log access equivalent to account access.
    """

    async def send(self, phone_e164: str, code: str) -> DeliveryResult:
        log.info("[OTP] phone={} code={}", phone_e164, code)
        return DeliveryResult(
            status=DeliveryStatus.OK,
            channel_used="log",
            detail="logged for owner-mediated delivery",
        )


# ---------------------------------------------------------------------------
# WhatsApp — Twilio REST API
# ---------------------------------------------------------------------------


class WhatsAppOtpProvider:
    """Send an OTP via Twilio's WhatsApp Authentication template.

    Configuration (passed in constructor; sourced from env in
    :func:`build_provider_from_env`):

    * ``account_sid`` — Twilio Account SID (``AC...``).
    * ``auth_token`` — Twilio Auth Token (corresponds to ``account_sid``).
    * ``from_number`` — verified WhatsApp Business sender, E.164,
      including ``whatsapp:`` prefix on the wire.
    * ``content_sid`` — the approved Authentication-template SID
      (``HX...``).  Created in the Twilio Console; the body must contain
      one variable for the OTP itself.

    Failure modes:

    * Recipient is on a number not registered with WhatsApp → Twilio
      returns ``code=63003`` (channel not reachable) → we map this to
      ``UNSUPPORTED_CHANNEL`` so the chain falls through to SMS.
    * Auth / config problems (bad SID, expired token, template
      unapproved) → ``PROVIDER_ERROR``; caller shows a generic
      "verification failed, try again later" message.
    """

    _TWILIO_BASE = "https://api.twilio.com/2010-04-01"
    # Twilio errors that mean "recipient unreachable on this channel" —
    # treat as fall-through to the next provider rather than surfacing.
    _UNREACHABLE_CODES = frozenset({63003, 63016, 63024})

    def __init__(
        self,
        *,
        account_sid: str,
        auth_token: str,
        from_number: str,
        content_sid: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        if not all([account_sid, auth_token, from_number, content_sid]):
            raise ValueError(
                "WhatsAppOtpProvider requires account_sid, auth_token, "
                "from_number, content_sid"
            )
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self._content_sid = content_sid
        self._timeout = timeout_seconds

    async def send(self, phone_e164: str, code: str) -> DeliveryResult:
        # Lazy-imported so installs that never use WhatsApp don't pay
        # aiohttp's connection-manager allocation cost on startup.
        import json as _json

        import aiohttp

        url = f"{self._TWILIO_BASE}/Accounts/{self._account_sid}/Messages.json"
        # Twilio REST requires both From and To prefixed with "whatsapp:".
        from_addr = f"whatsapp:{self._from_number}"
        to_addr = f"whatsapp:{phone_e164}"
        # ContentVariables is a JSON-encoded string of {position: value}.
        # Position "1" maps to the {{1}} placeholder in the approved
        # Authentication template body.
        content_vars = _json.dumps({"1": code})
        form = {
            "From": from_addr,
            "To": to_addr,
            "ContentSid": self._content_sid,
            "ContentVariables": content_vars,
        }
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self._timeout),
                auth=aiohttp.BasicAuth(self._account_sid, self._auth_token),
            ) as session:
                async with session.post(url, data=form) as response:
                    body = await response.json(content_type=None)
                    if response.status >= 400:
                        twilio_code = int(body.get("code", 0) or 0)
                        if twilio_code in self._UNREACHABLE_CODES:
                            log.info(
                                "WhatsApp unreachable for {} (code={}), falling through",
                                phone_e164, twilio_code,
                            )
                            return DeliveryResult(
                                status=DeliveryStatus.UNSUPPORTED_CHANNEL,
                                channel_used="whatsapp",
                                detail=f"twilio code={twilio_code}",
                            )
                        log.warning(
                            "Twilio WhatsApp send failed: status={} body={}",
                            response.status, body,
                        )
                        return DeliveryResult(
                            status=DeliveryStatus.PROVIDER_ERROR,
                            channel_used="whatsapp",
                            detail=f"twilio status={response.status}",
                        )
        except asyncio.TimeoutError:
            log.warning("Twilio WhatsApp send timed out for {}", phone_e164)
            return DeliveryResult(
                status=DeliveryStatus.PROVIDER_ERROR,
                channel_used="whatsapp",
                detail="timeout",
            )
        except Exception as exc:
            log.warning("Twilio WhatsApp send raised: {}", exc)
            return DeliveryResult(
                status=DeliveryStatus.PROVIDER_ERROR,
                channel_used="whatsapp",
                detail=str(exc),
            )
        return DeliveryResult(
            status=DeliveryStatus.OK,
            channel_used="whatsapp",
        )


# ---------------------------------------------------------------------------
# SMS — AWS SNS
# ---------------------------------------------------------------------------


class SnsSmsOtpProvider:
    """Send an OTP via AWS SNS ``publish``.

    Used as a fallback when WhatsApp returns ``UNSUPPORTED_CHANNEL``.
    SNS has no DLT/short-code restrictions — pay-as-go in every
    region we ship to.

    ``boto3`` is imported lazily so the engine's startup path doesn't
    drag in the ~30MB of AWS SDK if SMS is not configured.  The
    underlying call is sync; we offload to a thread executor to keep
    the event loop responsive.
    """

    _SMS_BODY_TEMPLATE = (
        "Your Lumin verification code is {code}. "
        "Expires in 5 minutes. Do not share it."
    )

    def __init__(
        self,
        *,
        region_name: str,
        access_key_id: str,
        secret_access_key: str,
        sender_id: Optional[str] = None,
    ) -> None:
        if not all([region_name, access_key_id, secret_access_key]):
            raise ValueError(
                "SnsSmsOtpProvider requires region_name, access_key_id, "
                "secret_access_key"
            )
        self._region = region_name
        self._access_key_id = access_key_id
        self._secret_access_key = secret_access_key
        self._sender_id = sender_id

    def _publish_sync(self, phone_e164: str, code: str) -> DeliveryResult:
        import boto3  # type: ignore[import-not-found]
        from botocore.exceptions import BotoCoreError, ClientError  # type: ignore[import-not-found]

        client = boto3.client(
            "sns",
            region_name=self._region,
            aws_access_key_id=self._access_key_id,
            aws_secret_access_key=self._secret_access_key,
        )
        attributes = {
            "AWS.SNS.SMS.SMSType": {
                "DataType": "String",
                "StringValue": "Transactional",
            },
        }
        if self._sender_id:
            attributes["AWS.SNS.SMS.SenderID"] = {
                "DataType": "String",
                "StringValue": self._sender_id,
            }
        try:
            client.publish(
                PhoneNumber=phone_e164,
                Message=self._SMS_BODY_TEMPLATE.format(code=code),
                MessageAttributes=attributes,
            )
        except (BotoCoreError, ClientError) as exc:
            log.warning("SNS SMS publish failed for {}: {}", phone_e164, exc)
            return DeliveryResult(
                status=DeliveryStatus.PROVIDER_ERROR,
                channel_used="sms",
                detail=str(exc),
            )
        return DeliveryResult(
            status=DeliveryStatus.OK,
            channel_used="sms",
        )

    async def send(self, phone_e164: str, code: str) -> DeliveryResult:
        # boto3 is sync — push to thread pool so the event loop keeps
        # serving other requests while SNS-API latency (typ. ~200ms)
        # ticks down.
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self._publish_sync, phone_e164, code,
        )


# ---------------------------------------------------------------------------
# Telegram bot DM — aligns with OWNER_BRIEF B13 (Telegram is the identity primitive)
# ---------------------------------------------------------------------------


class TelegramOtpProvider:
    """Send the OTP as a Telegram bot DM to the user's stored chat_id.

    OWNER_BRIEF B13 declares Telegram user ID the identity primitive — this
    provider is the doctrinally-aligned delivery channel.  No Meta business
    verification, no Twilio sender approval, no DLT/short-code registration
    required.  Works against the existing ``@LuminProBot`` infrastructure
    already wired for the billing webhook (PR #356).

    Flow per OTP send:

    1. Look up the user by ``phone_e164`` in ``UserStore``.
    2. If the user has no ``telegram_chat_id`` yet (i.e. hasn't completed
       the ``/start`` bind step in the bot), return
       ``UNSUPPORTED_CHANNEL`` so the chain falls through to fallback —
       typically ``LogOnlyOtpProvider`` for owner-mediated delivery during
       onboarding.
    3. Otherwise send the OTP as a Markdown-formatted DM via the engine's
       existing :class:`TelegramBot` instance.  ``send_message`` returns
       ``False`` on Telegram-side error (chat blocked, rate limited, etc.);
       we surface that as ``PROVIDER_ERROR`` (no fallthrough — the user's
       Telegram is broken in some way, SMS won't help).
    """

    def __init__(self, telegram_bot: Any, user_store: Any) -> None:
        self._bot = telegram_bot
        self._users = user_store

    async def send(self, phone_e164: str, code: str) -> DeliveryResult:
        user = self._users.get_by_phone(phone_e164) if self._users else None
        chat_id = getattr(user, "telegram_chat_id", None) if user else None
        if not chat_id:
            log.info(
                "Telegram OTP unsupported for {} — no telegram_chat_id linked",
                phone_e164,
            )
            return DeliveryResult(
                status=DeliveryStatus.UNSUPPORTED_CHANNEL,
                channel_used="telegram",
                detail="phone not linked to a Telegram chat_id (user needs /start in @LuminProBot)",
            )

        text = (
            "\U0001F510 *Lumin verification*\n\n"
            f"Your code is: `{code}`\n\n"
            "_Valid for 5 minutes. Do not share this code with anyone._"
        )
        try:
            ok = await self._bot.send_message(str(chat_id), text)
        except Exception as exc:
            log.warning(
                "Telegram OTP send raised for {} chat_id={}: {}",
                phone_e164, chat_id, exc,
            )
            return DeliveryResult(
                status=DeliveryStatus.PROVIDER_ERROR,
                channel_used="telegram",
                detail=f"send_message raised: {exc}",
            )
        if not ok:
            return DeliveryResult(
                status=DeliveryStatus.PROVIDER_ERROR,
                channel_used="telegram",
                detail="send_message returned False (chat blocked, rate-limited, or 4xx)",
            )
        return DeliveryResult(
            status=DeliveryStatus.OK,
            channel_used="telegram",
            detail=f"sent to chat_id={str(chat_id)[:6]}…",
        )


# ---------------------------------------------------------------------------
# Chain — primary then fallback
# ---------------------------------------------------------------------------


class ChainedOtpProvider:
    """Try ``primary``, fall through to ``fallback`` on UNSUPPORTED_CHANNEL.

    Other failure modes (PROVIDER_ERROR) short-circuit the chain — we
    don't burn an SMS just because Twilio rate-limited us; that almost
    certainly means SNS is rate-limited too.

    A chain with no fallback is degenerate but legal: only the primary
    is consulted, UNSUPPORTED_CHANNEL surfaces as-is to the caller.
    """

    def __init__(
        self,
        primary: OtpDeliveryProvider,
        fallback: Optional[OtpDeliveryProvider] = None,
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    async def send(self, phone_e164: str, code: str) -> DeliveryResult:
        result = await self._primary.send(phone_e164, code)
        if result.status != DeliveryStatus.UNSUPPORTED_CHANNEL:
            return result
        if self._fallback is None:
            return result
        log.info(
            "Falling through {} -> fallback for {}",
            result.channel_used, phone_e164,
        )
        return await self._fallback.send(phone_e164, code)


# ---------------------------------------------------------------------------
# Env-driven factory
# ---------------------------------------------------------------------------


def build_provider_from_env(
    telegram_bot: Optional[Any] = None,
    user_store: Optional[Any] = None,
) -> OtpDeliveryProvider:
    """Construct the configured delivery provider from env vars.

    Driven by ``OTP_PRIMARY_CHANNEL`` and ``OTP_FALLBACK_CHANNEL`` (each
    one of ``log`` / ``whatsapp`` / ``sms`` / ``telegram``).  Returns a
    single provider when no fallback is configured, or a
    :class:`ChainedOtpProvider` when both are set.

    The ``telegram`` channel requires the engine's ``TelegramBot`` and
    ``UserStore`` instances — these are injected by ``bootstrap.py`` after
    both have been constructed.  Selecting ``telegram`` without injecting
    these is a configuration error and raises ``ValueError`` early (better
    a boot-time crash than silent OTP failures in production).

    Lazy import of :mod:`config` keeps this file pure and importable in
    unit tests that don't want the engine's full env load.
    """
    from config import (
        OTP_PRIMARY_CHANNEL,
        OTP_FALLBACK_CHANNEL,
        TWILIO_ACCOUNT_SID,
        TWILIO_AUTH_TOKEN,
        TWILIO_WHATSAPP_FROM,
        TWILIO_WHATSAPP_CONTENT_SID,
        AWS_SNS_REGION,
        AWS_SNS_ACCESS_KEY_ID,
        AWS_SNS_SECRET_ACCESS_KEY,
        AWS_SNS_SENDER_ID,
    )

    def _build(name: str) -> Optional[OtpDeliveryProvider]:
        if name == "log":
            return LogOnlyOtpProvider()
        if name == "whatsapp":
            return WhatsAppOtpProvider(
                account_sid=TWILIO_ACCOUNT_SID,
                auth_token=TWILIO_AUTH_TOKEN,
                from_number=TWILIO_WHATSAPP_FROM,
                content_sid=TWILIO_WHATSAPP_CONTENT_SID,
            )
        if name == "sms":
            return SnsSmsOtpProvider(
                region_name=AWS_SNS_REGION,
                access_key_id=AWS_SNS_ACCESS_KEY_ID,
                secret_access_key=AWS_SNS_SECRET_ACCESS_KEY,
                sender_id=AWS_SNS_SENDER_ID or None,
            )
        if name == "telegram":
            if telegram_bot is None or user_store is None:
                raise ValueError(
                    "OTP channel 'telegram' selected but telegram_bot / "
                    "user_store not injected. bootstrap.py must pass both "
                    "into build_provider_from_env()."
                )
            return TelegramOtpProvider(
                telegram_bot=telegram_bot,
                user_store=user_store,
            )
        if name == "":
            return None
        raise ValueError(
            f"unknown OTP delivery channel: {name!r} "
            f"(expected one of: log, whatsapp, sms, telegram)"
        )

    primary = _build(OTP_PRIMARY_CHANNEL)
    if primary is None:
        # Defensive — config layer enforces a non-empty primary; if we
        # somehow get here, fall back to LogOnly so the engine still
        # boots and verifies don't 500.
        log.warning("OTP_PRIMARY_CHANNEL empty; defaulting to LogOnly")
        primary = LogOnlyOtpProvider()
    fallback = _build(OTP_FALLBACK_CHANNEL)
    if fallback is None:
        return primary
    return ChainedOtpProvider(primary, fallback)
