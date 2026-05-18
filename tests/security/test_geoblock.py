"""Tests for src.security.geoblock.

Pure-Python header-string parsing; no IO.  What we pin here:

* US is blocked (the B18 + owner-decision-1 contract).
* Other countries pass.
* Missing header is allowed-with-warning (CF outage / dev environment
  must not lock out the user base).
* ``XX`` (Cloudflare's "unknown" sentinel) is allowed-with-warning.
* Header lookup is case-insensitive (Starlette passes mixed case).
* The blocked list is the EXPECTED set — adding a country here without
  intent is now a test failure, not a silent prod change.
"""
from __future__ import annotations

import pytest

from src.security import geoblock


# ---------------------------------------------------------------------------
# Blocked list pinning — explicit constant test
# ---------------------------------------------------------------------------


def test_blocked_countries_is_us_only_today() -> None:
    """Pin the blocked-countries set so a future code change that adds
    a country also has to change this test — forces explicit owner
    intent for any expansion of the block."""
    assert geoblock._BLOCKED_COUNTRIES == frozenset({"US"})


# ---------------------------------------------------------------------------
# extract_country_code
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "header_name",
    ["CF-IPCountry", "cf-ipcountry", "Cf-Ipcountry"],
)
def test_extract_handles_case_insensitive_header(header_name: str) -> None:
    """Starlette passes headers as a case-insensitive map; emulate that
    via plain dicts in three common case spellings."""
    assert geoblock.extract_country_code({header_name: "US"}) == "US"


def test_extract_uppercases_and_strips() -> None:
    assert geoblock.extract_country_code({"CF-IPCountry": "  in  "}) == "IN"


def test_extract_returns_none_when_header_missing() -> None:
    assert geoblock.extract_country_code({}) is None


def test_extract_returns_none_when_header_empty_string() -> None:
    assert geoblock.extract_country_code({"CF-IPCountry": ""}) is None


# ---------------------------------------------------------------------------
# assert_country_allowed
# ---------------------------------------------------------------------------


def test_us_raises_geoblock_error() -> None:
    with pytest.raises(geoblock.GeoblockError):
        geoblock.assert_country_allowed({"CF-IPCountry": "US"})


def test_us_error_message_does_not_leak_country() -> None:
    """The user-facing message must NOT echo the country code — an
    attacker probing the geoblock shouldn't be able to enumerate
    blocked vs unblocked countries from the response body."""
    try:
        geoblock.assert_country_allowed({"CF-IPCountry": "US"})
    except geoblock.GeoblockError as exc:
        msg = exc.user_message.upper()
        assert "US" not in msg.split()  # 'US' as standalone word
        assert "UNITED STATES" not in msg


@pytest.mark.parametrize("country", ["IN", "GB", "DE", "SG", "AE", "AU"])
def test_non_blocked_countries_pass(country: str) -> None:
    """Spot-check a few common non-US countries — no exception."""
    geoblock.assert_country_allowed({"CF-IPCountry": country})


def test_missing_header_allowed_with_warning(caplog: pytest.LogCaptureFixture) -> None:
    """Dev / non-Cloudflare deployments must not lock out users —
    no exception, but the warning surfaces for operator visibility."""
    geoblock.assert_country_allowed({})
    # The warning fires via loguru → stdlib bridge; we don't assert on
    # exact log capture (loguru's bridge is sticky in pytest), but the
    # invariant is "no exception" which the line above pins.


def test_xx_unknown_country_allowed() -> None:
    """Cloudflare returns 'XX' when it can't determine the source
    country (e.g. Tor, certain enterprise proxies).  We allow rather
    than block — blocking would lock out legitimate users for a CF
    classification miss."""
    geoblock.assert_country_allowed({"CF-IPCountry": "XX"})
