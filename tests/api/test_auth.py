"""Smoke tests for the JWT auth module + auth endpoints."""
from __future__ import annotations

from datetime import timedelta

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api.auth import (  # noqa: E402
    ALL_ACCESS_TIER,
    AuthError,
    decode_token,
    mint_token,
    refresh_token,
)
from src.api.server import build_app  # noqa: E402

# Re-use the stub engine from the existing smoke tests
from tests.api.test_api_smoke import _StubEngine  # noqa: E402


_SECRET = "x" * 64


# ---------------------------------------------------------------------------
# Pure auth module
# ---------------------------------------------------------------------------


def test_mint_returns_decodable_token() -> None:
    t = mint_token(secret=_SECRET)
    c = decode_token(t, secret=_SECRET)
    assert c.tier == ALL_ACCESS_TIER
    assert c.sub.startswith("device-")
    assert c.is_paid is True


def test_mint_with_custom_sub_and_tier() -> None:
    t = mint_token(secret=_SECRET, sub="user-42", tier="paid")
    c = decode_token(t, secret=_SECRET)
    assert c.sub == "user-42"
    assert c.tier == "paid"


def test_decode_rejects_wrong_secret() -> None:
    t = mint_token(secret=_SECRET)
    with pytest.raises(AuthError):
        decode_token(t, secret="other" * 12)


def test_decode_rejects_garbage() -> None:
    with pytest.raises(AuthError):
        decode_token("not.a.jwt", secret=_SECRET)


@pytest.mark.parametrize("token", ["a.b.\u00e9", "\u00e9.b.c", "a.\u00e9.c"])
def test_decode_rejects_a_non_ascii_token_as_an_auth_error(token) -> None:
    """Regression (2026-09-26 audit): the signing input was ``.encode("ascii")``-ed
    and the signature compared as ``str``, so a non-ASCII character raised
    UnicodeEncodeError/TypeError — an unhandled 500 on every authenticated
    route instead of a 401."""
    with pytest.raises(AuthError):
        decode_token(token, secret=_SECRET)


def test_decode_rejects_expired_token() -> None:
    t = mint_token(secret=_SECRET, ttl=timedelta(seconds=-1))
    with pytest.raises(AuthError, match="expired"):
        decode_token(t, secret=_SECRET)


def test_refresh_preserves_sub_and_tier(monkeypatch) -> None:
    # A controlled clock instead of time.sleep(1), and a strict assertion:
    # the old ``exp >= exp`` was satisfied by a refresh that renewed nothing.
    from datetime import datetime, timezone

    from src.api import auth as auth_mod

    t0 = datetime.now(timezone.utc).replace(microsecond=0)
    monkeypatch.setattr(auth_mod, "_now", lambda: t0)
    t1 = mint_token(secret=_SECRET, sub="device-abc", tier="paid")
    monkeypatch.setattr(auth_mod, "_now", lambda: t0 + timedelta(minutes=10))
    t2 = refresh_token(t1, secret=_SECRET)
    c1 = decode_token(t1, secret=_SECRET)
    c2 = decode_token(t2, secret=_SECRET)
    assert c2.sub == c1.sub
    assert c2.tier == c1.tier
    assert c2.exp - c1.exp == timedelta(minutes=10)


def test_refresh_rejects_expired_token() -> None:
    t = mint_token(secret=_SECRET, ttl=timedelta(seconds=-1))
    with pytest.raises(AuthError):
        refresh_token(t, secret=_SECRET)


# ---------------------------------------------------------------------------
# /api/auth/* endpoints
# ---------------------------------------------------------------------------


@pytest.fixture
def client() -> TestClient:
    return TestClient(build_app(_StubEngine(), jwt_secret=_SECRET, allow_static=False))


def test_anonymous_endpoint_mints_token(client: TestClient) -> None:
    # Legacy JWT endpoint retired — returns 410 Gone since Firebase Phone Auth migration
    r = client.post("/api/auth/anonymous")
    assert r.status_code == 410


def test_refresh_endpoint_issues_new_token(client: TestClient) -> None:
    # Legacy JWT refresh endpoint retired — returns 410 Gone
    r = client.post("/api/auth/refresh", json={"token": "any.token.here"})
    assert r.status_code == 410


def test_refresh_endpoint_rejects_invalid_token(client: TestClient) -> None:
    # Legacy JWT refresh endpoint retired — returns 410 Gone regardless of token validity
    r = client.post("/api/auth/refresh", json={"token": "not.a.jwt"})
    assert r.status_code == 410


def test_protected_endpoint_requires_valid_jwt(client: TestClient) -> None:
    r = client.get("/api/pulse")
    assert r.status_code == 401

    r = client.get("/api/pulse", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401


def test_protected_endpoint_accepts_minted_jwt(client: TestClient) -> None:
    # Anonymous endpoint is retired (410); use a directly minted token instead
    token = mint_token(secret=_SECRET)
    r = client.get("/api/pulse", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Static admin token escape hatch
# ---------------------------------------------------------------------------


def test_static_token_accepted_when_allow_flag_true() -> None:
    app = build_app(
        _StubEngine(),
        jwt_secret=_SECRET,
        static_token="admin-token",
        allow_static=True,
    )
    c = TestClient(app)
    r = c.get("/api/pulse", headers={"Authorization": "Bearer admin-token"})
    assert r.status_code == 200


def test_static_token_rejected_when_allow_flag_false() -> None:
    app = build_app(
        _StubEngine(),
        jwt_secret=_SECRET,
        static_token="admin-token",
        allow_static=False,
    )
    c = TestClient(app)
    r = c.get("/api/pulse", headers={"Authorization": "Bearer admin-token"})
    assert r.status_code == 401


def test_health_does_not_require_auth() -> None:
    app = build_app(_StubEngine(), jwt_secret=_SECRET, allow_static=False)
    c = TestClient(app)
    assert c.get("/api/health").status_code == 200


def test_anonymous_endpoint_503_when_secret_missing() -> None:
    # Legacy JWT endpoint is retired — always returns 410 regardless of jwt_secret config
    app = build_app(_StubEngine(), jwt_secret="", allow_static=False)
    c = TestClient(app)
    r = c.post("/api/auth/anonymous")
    assert r.status_code == 410


# ---------------------------------------------------------------------------
# effective_tier — read-time expiry downgrade (shared with dispatch)
# ---------------------------------------------------------------------------
#
# Pure-function twin of the dispatch money-path rule in
# ``signal_dispatch._resolve_user_tier`` (the two must stay in lockstep);
# consumed by /api/auto-trade/runtime-status so the armed card renders the
# same tier verdict dispatch will apply.


def test_effective_tier_active_paid_window_keeps_tier() -> None:
    from datetime import datetime, timezone

    from src.api.auth import effective_tier

    future = datetime.now(timezone.utc) + timedelta(days=30)
    assert effective_tier("auto", future) == "auto"
    assert effective_tier("assist", future) == "assist"


def test_effective_tier_lapsed_paid_window_downgrades_to_free() -> None:
    from datetime import datetime, timezone

    from src.api.auth import effective_tier

    past = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert effective_tier("auto", past) == "free"
    assert effective_tier("assist", past) == "free"


def test_effective_tier_none_paid_until_never_downgrades() -> None:
    from src.api.auth import effective_tier

    assert effective_tier("auto", None) == "auto"
    assert effective_tier("owner", None) == "owner"


def test_effective_tier_free_tier_ignores_paid_until() -> None:
    """The downgrade only applies to assist-or-higher — a free row with
    a stale paid_until stays free (no can_assist match, no-op)."""
    from datetime import datetime, timezone

    from src.api.auth import effective_tier

    past = datetime.now(timezone.utc) - timedelta(days=9)
    assert effective_tier("free", past) == "free"


def test_effective_tier_missing_tier_is_free_and_unknown_ranks_free() -> None:
    from src.api.auth import can_auto, effective_tier

    assert effective_tier(None, None) == "free"
    assert effective_tier("", None) == "free"
    # Unknown strings pass through normalised (lowercase) but rank 0,
    # so every capability check downstream treats them as free.
    assert effective_tier("GARBAGE", None) == "garbage"
    assert can_auto(effective_tier("GARBAGE", None)) is False


def test_effective_tier_injectable_now_is_deterministic() -> None:
    from datetime import datetime, timezone

    from src.api.auth import effective_tier

    paid_until = datetime(2026, 7, 1, tzinfo=timezone.utc)
    before = datetime(2026, 6, 30, tzinfo=timezone.utc)
    after = datetime(2026, 7, 2, tzinfo=timezone.utc)
    assert effective_tier("auto", paid_until, now=before) == "auto"
    assert effective_tier("auto", paid_until, now=after) == "free"
