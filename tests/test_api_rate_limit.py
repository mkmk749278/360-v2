"""Tests for the API rate-limit layer (src/api/rate_limit.py, audit F-14)."""

from __future__ import annotations

import pytest

from src.api.rate_limit import (
    DEFAULT_LIMIT_PER_MIN,
    EXEMPT_PATH_PREFIXES,
    SlidingWindowLimiter,
    client_key,
    install_rate_limiting,
)


# ---------------------------------------------------------------------------
# SlidingWindowLimiter unit behaviour
# ---------------------------------------------------------------------------


class TestSlidingWindowLimiter:
    def test_allows_up_to_limit(self):
        lim = SlidingWindowLimiter(limit_per_min=5)
        for i in range(5):
            allowed, _ = lim.check("k", now=100.0 + i)
            assert allowed, f"hit {i} should be allowed"

    def test_blocks_over_limit_with_retry_after(self):
        lim = SlidingWindowLimiter(limit_per_min=3)
        for i in range(3):
            assert lim.check("k", now=100.0 + i)[0]
        allowed, retry_after = lim.check("k", now=103.0)
        assert not allowed
        # Oldest hit at t=100 ages out at t=160 → retry_after ≈ 57s.
        assert retry_after == pytest.approx(57.0, abs=0.01)

    def test_window_slides(self):
        lim = SlidingWindowLimiter(limit_per_min=2)
        assert lim.check("k", now=100.0)[0]
        assert lim.check("k", now=101.0)[0]
        assert not lim.check("k", now=102.0)[0]
        # 61s after the first hit, one slot has freed.
        assert lim.check("k", now=161.0)[0]

    def test_clients_are_independent(self):
        lim = SlidingWindowLimiter(limit_per_min=1)
        assert lim.check("a", now=100.0)[0]
        assert not lim.check("a", now=100.5)[0]
        assert lim.check("b", now=100.5)[0]

    def test_max_clients_evicts_stalest(self):
        lim = SlidingWindowLimiter(limit_per_min=10, max_clients=2)
        lim.check("old", now=100.0)
        lim.check("new", now=200.0)
        lim.check("third", now=300.0)  # evicts "old"
        assert lim.tracked_clients == 2
        # "old" starts fresh — its history was evicted, not blocked.
        assert lim.check("old", now=300.5)[0]

    def test_limit_floor_is_one(self):
        lim = SlidingWindowLimiter(limit_per_min=0)
        assert lim.limit == 1


# ---------------------------------------------------------------------------
# client_key derivation
# ---------------------------------------------------------------------------


class TestClientKey:
    def test_bearer_token_wins_and_is_hashed(self):
        key = client_key(
            authorization="Bearer sekret-token",
            client_host="1.2.3.4",
            forwarded_for="",
        )
        assert key.startswith("tok:")
        assert "sekret" not in key  # raw token never appears in the key

    def test_same_token_same_key(self):
        a = client_key(authorization="Bearer t1", client_host="1.1.1.1", forwarded_for="")
        b = client_key(authorization="Bearer t1", client_host="2.2.2.2", forwarded_for="")
        assert a == b  # token-keyed, not IP-keyed

    def test_forwarded_for_first_hop(self):
        key = client_key(
            authorization="",
            client_host="10.0.0.1",  # the proxy
            forwarded_for="203.0.113.9, 172.16.0.1",
        )
        assert key == "ip:203.0.113.9"

    def test_falls_back_to_client_host(self):
        assert client_key(authorization="", client_host="9.9.9.9", forwarded_for="") == "ip:9.9.9.9"

    def test_no_client_at_all(self):
        assert client_key(authorization="", client_host="", forwarded_for="") == "ip:unknown"

    def test_non_bearer_scheme_ignored(self):
        key = client_key(authorization="Basic abc", client_host="5.5.5.5", forwarded_for="")
        assert key == "ip:5.5.5.5"


# ---------------------------------------------------------------------------
# Middleware integration (FastAPI TestClient)
# ---------------------------------------------------------------------------


@pytest.fixture()
def make_app(monkeypatch):
    """Build a minimal FastAPI app with the middleware installed."""

    def _make(limit: int):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        monkeypatch.setenv("API_RATE_LIMIT_ENABLED", "true")
        monkeypatch.setenv("API_RATE_LIMIT_PER_MIN", str(limit))
        app = FastAPI()

        @app.get("/api/thing")
        async def thing():
            return {"ok": True}

        @app.get("/api/health")
        async def health():
            return {"ok": True}

        limiter = install_rate_limiting(app)
        assert limiter is not None
        return TestClient(app)

    return _make


class TestMiddleware:
    def test_429_after_limit(self, make_app):
        client = make_app(3)
        for _ in range(3):
            assert client.get("/api/thing").status_code == 200
        resp = client.get("/api/thing")
        assert resp.status_code == 429
        assert int(resp.headers["Retry-After"]) >= 1
        assert resp.json() == {"detail": "rate limit exceeded"}

    def test_health_exempt(self, make_app):
        client = make_app(1)
        for _ in range(10):
            assert client.get("/api/health").status_code == 200

    def test_tokens_partition_budgets(self, make_app):
        client = make_app(1)
        assert client.get("/api/thing", headers={"Authorization": "Bearer a"}).status_code == 200
        assert client.get("/api/thing", headers={"Authorization": "Bearer a"}).status_code == 429
        assert client.get("/api/thing", headers={"Authorization": "Bearer b"}).status_code == 200

    def test_disabled_via_env(self, monkeypatch):
        from fastapi import FastAPI

        monkeypatch.setenv("API_RATE_LIMIT_ENABLED", "false")
        app = FastAPI()
        assert install_rate_limiting(app) is None

    def test_default_limit_generous(self):
        # Guard against someone tightening the default under the app's
        # legitimate polling cadence (~15s poll + dashboards ≪ 240/min).
        assert DEFAULT_LIMIT_PER_MIN >= 120

    def test_exempt_prefixes_cover_healthchecks(self):
        assert any(p.startswith("/api/health") for p in EXEMPT_PATH_PREFIXES)
