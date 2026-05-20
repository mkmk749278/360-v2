"""``GET /api/region`` — client region detection for Play Store launch.

Returns the ISO 3166-1 alpha-2 country code we derived from the
incoming request, plus a ``is_blocked`` flag indicating whether the
auto-trade feature is available in that region.

**Why this exists:** the Play Store launch plan (``docs/PLAYSTORE_PLAN.md``)
calls for client-side region gating so users in restricted jurisdictions
(US / CN / BD by default) don't see the auto-trade UI at all. This
endpoint backs the client check (A6 in the plan).

**No authentication:** deliberately public so the client can call it
*before* the user signs in — the region-block needs to show on the
welcome screen, not after we've already collected a phone number.

**Detection strategy (soft-fail open):**

1. ``CF-IPCountry`` header — set automatically by Cloudflare on any
   plan (including free). This is the primary path; if the engine
   VPS is behind Cloudflare, every request carries a reliable
   2-letter country code.
2. ``X-Country-Code`` header — fallback for other CDNs (Cloud Run,
   App Engine, some load balancers set this).
3. If neither header is present → return ``country_code: "unknown"``
   and ``is_blocked: false``. This is the **soft-fail-open** default:
   we'd rather show the UI to a user we can't identify than block a
   user in a permitted region.

Server-side dispatch ALSO enforces region restrictions via the
per-user ``_active_uids`` allowlist + the connect-time validator —
this endpoint is the UX layer, not the security layer.

**Response shape::**

    {
      "country_code": "IN",        // ISO 3166-1 alpha-2 or "unknown"
      "source": "cf-header",       // "cf-header" | "x-header" | "unknown"
      "is_blocked": false,         // true iff country_code in BLOCKED_REGIONS
      "blocked_regions": ["US", "CN", "BD"]  // current block list
    }

``blocked_regions`` is echoed so the client can show "not available
in US/CN/BD" copy without hard-coding the list — env-overridable per
config.BLOCKED_REGIONS.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request

from config import BLOCKED_REGIONS
from src.utils import get_logger

log = get_logger("api.region_routes")


# Cloudflare's canonical header.  Per docs:
# https://developers.cloudflare.com/network/ip-geolocation/
# This header is always set when IP Geolocation is enabled on the
# zone (default ON for paid plans, opt-in but free on the free plan).
_CF_HEADER = "CF-IPCountry"

# Generic fallback used by some other CDNs and proxies.  Lowercase
# variants are also tried since some intermediaries normalise case.
_X_COUNTRY_HEADER = "X-Country-Code"


def _normalise_country_code(raw: str) -> str:
    """Trim + uppercase a header value, returning ``""`` on falsy input.

    Cloudflare returns ``"XX"`` for unknown / Tor / unrouted requests
    and ``"T1"`` for Tor specifically — we treat both as unknown so
    the soft-fail-open path engages rather than producing a confusing
    "blocked in XX" UX.
    """
    if not raw:
        return ""
    code = raw.strip().upper()
    if code in ("XX", "T1"):
        return ""
    # ISO 3166-1 alpha-2 is exactly two letters.  Anything else is
    # malformed; treat as unknown.
    if len(code) != 2 or not code.isalpha():
        return ""
    return code


def register(app: FastAPI) -> None:
    """Wire ``GET /api/region`` onto the given app.

    No auth dependency — endpoint is public (see module docstring).
    """

    @app.get("/api/region", tags=["region"])
    async def region(request: Request) -> dict[str, Any]:
        # Order matters: Cloudflare's header takes precedence because
        # we know its semantics; the generic X-Country-Code is a best-
        # effort fallback.
        cf_raw = request.headers.get(_CF_HEADER, "")
        x_raw = request.headers.get(_X_COUNTRY_HEADER, "")

        country = _normalise_country_code(cf_raw)
        source = "cf-header"
        if not country:
            country = _normalise_country_code(x_raw)
            source = "x-header" if country else "unknown"

        if not country:
            country = "unknown"

        is_blocked = country in BLOCKED_REGIONS

        # Lightweight access log — useful when investigating region
        # complaints ("I'm in India but the app says I'm blocked").
        # Avoid logging the full request to keep the line scannable.
        log.debug(
            "region: country={} source={} is_blocked={}",
            country, source, is_blocked,
        )

        return {
            "country_code": country,
            "source": source,
            "is_blocked": is_blocked,
            "blocked_regions": sorted(BLOCKED_REGIONS),
        }
