"""Tests for src.api.region_routes — Play Store region detection.

What we pin:

* CF-IPCountry header takes precedence and is uppercased
* X-Country-Code header is used when CF header absent
* No header → "unknown" with is_blocked=false (soft-fail open)
* XX / T1 (Cloudflare's "unknown" + Tor markers) → "unknown"
* Malformed header value → "unknown"
* country_code IN BLOCKED_REGIONS → is_blocked=true
* country_code NOT in BLOCKED_REGIONS → is_blocked=false
* blocked_regions is echoed in the response
* Endpoint is public (no auth header required) — Play Store flow
  needs to call before user signs in
"""
from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app() -> FastAPI:
    from src.api import region_routes

    app = FastAPI()
    region_routes.register(app)
    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(_build_app())


# ---------------------------------------------------------------------------
# Header precedence + parsing
# ---------------------------------------------------------------------------


def test_cf_header_resolves_country(client: TestClient) -> None:
    """Cloudflare's CF-IPCountry is the primary source."""
    resp = client.get("/api/region", headers={"CF-IPCountry": "IN"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["country_code"] == "IN"
    assert body["source"] == "cf-header"


def test_cf_header_uppercased(client: TestClient) -> None:
    """Header values are normalised to uppercase."""
    resp = client.get("/api/region", headers={"CF-IPCountry": "in"})
    assert resp.json()["country_code"] == "IN"


def test_x_country_code_fallback(client: TestClient) -> None:
    """When CF header is absent, X-Country-Code is read."""
    resp = client.get("/api/region", headers={"X-Country-Code": "GB"})
    body = resp.json()
    assert body["country_code"] == "GB"
    assert body["source"] == "x-header"


def test_cf_header_precedence_over_x_header(client: TestClient) -> None:
    """When both headers are present, CF wins (it's more reliable)."""
    resp = client.get(
        "/api/region",
        headers={"CF-IPCountry": "DE", "X-Country-Code": "FR"},
    )
    body = resp.json()
    assert body["country_code"] == "DE"
    assert body["source"] == "cf-header"


# ---------------------------------------------------------------------------
# Soft-fail open
# ---------------------------------------------------------------------------


def test_no_headers_returns_unknown_not_blocked(client: TestClient) -> None:
    """No region headers at all → unknown country, NOT blocked.

    This is the soft-fail-open default: we'd rather show the UI to a
    user we can't identify than block a user in a permitted region.
    """
    resp = client.get("/api/region")
    assert resp.status_code == 200
    body = resp.json()
    assert body["country_code"] == "unknown"
    assert body["source"] == "unknown"
    assert body["is_blocked"] is False


@pytest.mark.parametrize("noisy", ["XX", "T1", "xx", "t1"])
def test_cf_unknown_or_tor_treated_as_unknown(
    client: TestClient, noisy: str,
) -> None:
    """Cloudflare uses ``XX`` for unrouted requests and ``T1`` for Tor.
    Both should map to ``unknown`` (and therefore NOT-blocked) so the
    UX doesn't say 'blocked in XX'."""
    resp = client.get("/api/region", headers={"CF-IPCountry": noisy})
    body = resp.json()
    assert body["country_code"] == "unknown"
    assert body["is_blocked"] is False


@pytest.mark.parametrize("bad", ["USA", "1A", "", "  ", "I"])
def test_malformed_header_treated_as_unknown(
    client: TestClient, bad: str,
) -> None:
    """Anything that isn't a clean 2-letter alpha → unknown."""
    resp = client.get("/api/region", headers={"CF-IPCountry": bad})
    body = resp.json()
    assert body["country_code"] == "unknown"


# ---------------------------------------------------------------------------
# Block-list semantics
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("blocked", ["US", "CN", "BD"])
def test_default_blocked_regions_are_blocked(
    client: TestClient, blocked: str,
) -> None:
    """Default block list (US, CN, BD) returns is_blocked=true."""
    resp = client.get("/api/region", headers={"CF-IPCountry": blocked})
    body = resp.json()
    assert body["country_code"] == blocked
    assert body["is_blocked"] is True


@pytest.mark.parametrize("permitted", ["IN", "GB", "DE", "FR", "JP", "AU"])
def test_permitted_regions_are_not_blocked(
    client: TestClient, permitted: str,
) -> None:
    """India, UK, EU member states, etc. return is_blocked=false."""
    resp = client.get("/api/region", headers={"CF-IPCountry": permitted})
    body = resp.json()
    assert body["country_code"] == permitted
    assert body["is_blocked"] is False


def test_blocked_regions_echoed_in_response(client: TestClient) -> None:
    """The response includes the sorted block list so the client can
    show 'not available in US/CN/BD' copy without hard-coding the
    list (env-overridable per config.BLOCKED_REGIONS)."""
    resp = client.get("/api/region", headers={"CF-IPCountry": "IN"})
    body = resp.json()
    assert "blocked_regions" in body
    assert isinstance(body["blocked_regions"], list)
    assert body["blocked_regions"] == sorted(body["blocked_regions"])
    # Default config should include US/CN/BD.
    assert "US" in body["blocked_regions"]
    assert "CN" in body["blocked_regions"]
    assert "BD" in body["blocked_regions"]


# ---------------------------------------------------------------------------
# Public access (no auth)
# ---------------------------------------------------------------------------


def test_endpoint_is_public_no_auth_required(client: TestClient) -> None:
    """Endpoint must be reachable without any auth header.  The Play
    Store launch flow needs to check region BEFORE the user signs in,
    so requiring Firebase auth here would block the welcome screen."""
    resp = client.get("/api/region")
    assert resp.status_code == 200  # NOT 401


# ---------------------------------------------------------------------------
# Env override
# ---------------------------------------------------------------------------


def test_env_override_of_blocked_regions(monkeypatch) -> None:
    """BLOCKED_REGIONS env var overrides the default list.

    Re-import config + region_routes after the env change so the
    frozenset is rebuilt.
    """
    import importlib
    import config
    import src.api.region_routes as region_routes

    monkeypatch.setenv("BLOCKED_REGIONS", "IR,KP,RU")
    importlib.reload(config)
    importlib.reload(region_routes)

    app = FastAPI()
    region_routes.register(app)
    c = TestClient(app)

    # IR is now blocked; US no longer is (under this override).
    resp_ir = c.get("/api/region", headers={"CF-IPCountry": "IR"})
    assert resp_ir.json()["is_blocked"] is True
    resp_us = c.get("/api/region", headers={"CF-IPCountry": "US"})
    assert resp_us.json()["is_blocked"] is False

    # Restore defaults for subsequent tests.
    monkeypatch.delenv("BLOCKED_REGIONS", raising=False)
    importlib.reload(config)
    importlib.reload(region_routes)
