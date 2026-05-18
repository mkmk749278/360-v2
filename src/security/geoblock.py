"""US-user geoblock — connect-flow defence per B18 + owner-decision 1 (2026-05-18).

Solo-scale implementation: the engine VPS sits behind Cloudflare, which
adds a ``CF-IPCountry`` header to every request based on the client's
source IP.  We check that header against the blocked-country list at
the connect endpoint (and any other write endpoint that touches
auto-trade enablement).

This is **defence-in-depth**, not the only US block.  The primary
block lives at Firebase Auth signup (block US account creation
entirely via Firebase Phone Auth's country allowlist).  This server-
side check catches:

* Users who signed up before the Firebase block was wired.
* Users who travel to the US after signing up elsewhere (we block
  them at connect time so a stolen-phone-in-US scenario can't trigger
  trades).
* Defence against Cloudflare misconfig — if the country header is
  missing entirely we log a warning but don't block, so a temporary
  CF outage doesn't lock out non-US users.

When the engine isn't deployed behind Cloudflare (e.g. local dev),
``CF-IPCountry`` is absent.  In that case the check no-ops with a
warning — the deployment-side responsibility is to ensure the
production VPS sits behind Cloudflare (or an equivalent that injects
the country header) before going live with auto-trade.

This module is intentionally minimal — adding a paid GeoIP service
(MaxMind GeoLite2, ipinfo.io, etc.) is a follow-up if we ever leave
Cloudflare.
"""

from __future__ import annotations

from typing import Optional

from src.utils import get_logger

log = get_logger("security.geoblock")


# Countries blocked from auto-trade enablement.  Per OWNER_BRIEF B18
# + owner-decision 1 (2026-05-18) — defends against the 3Commas N.D.
# Cal. litigation vector.  Add more ISO-3166-1 alpha-2 codes here as
# legal posture dictates; keep this list explicit (not a regex) so
# the blocked surface is obvious to anyone reading.
_BLOCKED_COUNTRIES = frozenset({"US"})


class GeoblockError(Exception):
    """Raised by :func:`assert_country_allowed` when the request's
    country is on the blocked list.

    The route handler maps this to HTTP 403 with a generic message;
    we deliberately don't echo the country back so an attacker
    probing the geoblock can't enumerate blocked countries.
    """

    user_message = (
        "Lumin auto-trade is not available in your region. "
        "You can continue using read-only features."
    )


def extract_country_code(headers: dict) -> Optional[str]:
    """Pull the ``CF-IPCountry`` header (case-insensitive).

    Returns ``None`` if the header is missing.  Headers from
    Cloudflare are ISO-3166-1 alpha-2 (e.g. ``US``, ``IN``, ``GB``);
    ``XX`` is Cloudflare's sentinel for "couldn't determine country."
    """
    # FastAPI passes a Starlette ``Headers`` instance that is
    # case-insensitive; calling code may pass a plain dict in tests
    # so we handle both.
    raw = (
        headers.get("CF-IPCountry")
        or headers.get("cf-ipcountry")
        or headers.get("Cf-Ipcountry")
    )
    if not raw:
        return None
    code = str(raw).strip().upper()
    return code or None


def assert_country_allowed(headers: dict) -> None:
    """Reject if the request originated from a blocked country.

    Raises :class:`GeoblockError` when ``CF-IPCountry`` is on the
    blocked list.  No-ops with a debug log when the header is missing
    (dev / non-Cloudflare deployment) or when Cloudflare couldn't
    determine the country (``XX``) — in production behind Cloudflare
    these cases are rare, and missing-country defaulting to allow is
    intentional so a CF outage doesn't lock out our entire user base.
    """
    code = extract_country_code(headers)
    if code is None:
        log.warning(
            "geoblock: CF-IPCountry header missing — request allowed by default "
            "(ensure engine VPS is behind Cloudflare in production)"
        )
        return
    if code == "XX":
        log.warning(
            "geoblock: Cloudflare returned XX (country unknown) — request allowed"
        )
        return
    if code in _BLOCKED_COUNTRIES:
        # Log the country at info level (operator needs visibility of
        # blocked-request volume); do NOT include any user-identifying
        # information.
        log.info("geoblock: rejected request from country={}", code)
        raise GeoblockError(GeoblockError.user_message)
