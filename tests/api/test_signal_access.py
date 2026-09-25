"""Guest access + the live-signal paywall (owner, 2026-09-25).

Two changes, pinned together because they meet on every feed route:

* a **guest** — a Firebase anonymous sign-in — may read, gets a free-tier
  identity with no user row, and never sees an ACTIVE signal;
* the **paywall** (``signals_paywall_start``) hides ACTIVE signals from a
  phone account once its 3 free days are over, unless it holds the Signals
  plan or any automation tier.

The route tests drive the real ``build_app`` with the Firebase path wired and
only ``verify_id_token`` faked, because that is the seam the app actually
crosses: an anonymous token and a phone token differ only in the claims
Firebase returns.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

from src.api import firebase_auth, signal_access  # noqa: E402
from src.api import server as server_mod  # noqa: E402
from src.api.auth import FREE_TIER, TokenClaims, tier_rank, effective_tier  # noqa: E402
from src.api.server import build_app  # noqa: E402
from src.api.users import User, UserStore  # noqa: E402

from tests.api.test_api_smoke import _StubEngine  # noqa: E402

NOW = datetime(2026, 10, 10, 12, 0, tzinfo=timezone.utc)
START = "2026-10-05T00:00:00"


def _user(*, created: datetime, tier: str = "free", paid_until=None) -> User:
    return User(
        user_id=7, phone_e164="+919999999999", tier=tier, paid_until=paid_until,
        telegram_chat_id=None, created_at=created, updated_at=created,
    )


def _guest() -> TokenClaims:
    return TokenClaims(sub="guest-abc", tier=FREE_TIER, iat=NOW, exp=NOW)


# ---------------------------------------------------------------------------
# The rule itself
# ---------------------------------------------------------------------------


def test_guest_never_sees_live_signals_even_with_the_paywall_off() -> None:
    a = signal_access.live_access(_guest(), now=NOW, start="")
    assert (a.allowed, a.reason) == (False, "guest")


def test_owner_static_token_always_sees_them() -> None:
    assert signal_access.live_access(None, now=NOW, start=START).allowed


def test_paywall_off_keeps_todays_behaviour_for_phone_users() -> None:
    a = signal_access.live_access(_user(created=NOW - timedelta(days=90)), now=NOW, start="")
    assert (a.allowed, a.reason) == (True, "paywall_off")


def test_a_future_start_is_scheduled_not_active() -> None:
    a = signal_access.live_access(
        _user(created=NOW - timedelta(days=90)), now=NOW, start="2026-12-01",
    )
    assert (a.allowed, a.reason) == (True, "paywall_off")


def test_an_unparseable_start_is_reported_and_never_locks_anyone() -> None:
    a = signal_access.live_access(
        _user(created=NOW - timedelta(days=90)), now=NOW, start="1st October",
    )
    assert (a.allowed, a.reason) == (True, "misconfigured")


def test_new_signup_gets_three_days_from_signup() -> None:
    created = NOW - timedelta(days=2)
    a = signal_access.live_access(_user(created=created), now=NOW, start=START, free_days=3)
    assert (a.allowed, a.reason) == (True, "free_window")
    assert a.until == created + timedelta(days=3)


def test_new_signup_is_locked_after_three_days() -> None:
    a = signal_access.live_access(
        _user(created=NOW - timedelta(days=3, seconds=1)), now=NOW, start=START, free_days=3,
    )
    assert (a.allowed, a.reason) == (False, "locked")


def test_existing_account_gets_three_days_counted_from_the_launch() -> None:
    """Owner: existing users get 3 days from launch, then lock."""
    old = _user(created=NOW - timedelta(days=200))
    start = datetime(2026, 10, 8, tzinfo=timezone.utc)
    inside = signal_access.live_access(old, now=start + timedelta(days=2), start=start.isoformat(), free_days=3)
    after = signal_access.live_access(old, now=start + timedelta(days=3, seconds=1), start=start.isoformat(), free_days=3)
    assert (inside.allowed, inside.reason) == (True, "free_window")
    assert inside.until == start + timedelta(days=3)
    assert (after.allowed, after.reason) == (False, "locked")


@pytest.mark.parametrize("tier", ["signals", "assist", "auto", "paid", "all-access", "owner"])
def test_every_tier_from_signals_up_includes_live_signals(tier: str) -> None:
    u = _user(created=NOW - timedelta(days=200), tier=tier, paid_until=NOW + timedelta(days=10))
    a = signal_access.live_access(u, now=NOW, start=START, free_days=3)
    assert (a.allowed, a.reason) == (True, "plan")


def test_a_lapsed_signals_plan_locks_again() -> None:
    u = _user(created=NOW - timedelta(days=200), tier="signals", paid_until=NOW - timedelta(seconds=1))
    a = signal_access.live_access(u, now=NOW, start=START, free_days=3)
    assert (a.allowed, a.reason) == (False, "locked")


def test_signals_tier_sits_between_free_and_assist() -> None:
    assert tier_rank("free") < tier_rank("signals") < tier_rank("assist") < tier_rank("auto")
    # and it expires at read time like every paid tier
    assert effective_tier("signals", NOW - timedelta(days=1), now=NOW) == "free"


# ---------------------------------------------------------------------------
# Guest identity
# ---------------------------------------------------------------------------


def _anon_claims(uid: str = "anon-1") -> dict:
    return {"uid": uid, "iat": 1, "exp": 2, "firebase": {"sign_in_provider": "anonymous"}}


def _phone_claims(uid: str = "phone-1") -> dict:
    return {"uid": uid, "phone_number": "+919876543210", "iat": 1, "exp": 2,
            "firebase": {"sign_in_provider": "phone"}}


def test_anonymous_token_maps_to_a_free_guest(monkeypatch) -> None:
    monkeypatch.delenv("GUEST_ACCESS_ENABLED", raising=False)
    g = server_mod._guest_claims(_anon_claims("u9"))
    assert g is not None and g.sub == "guest-u9" and g.tier == "free"
    assert signal_access.is_guest(g)


def test_a_phone_token_is_never_a_guest() -> None:
    assert server_mod._guest_claims(_phone_claims()) is None


def test_a_token_missing_its_phone_is_not_silently_made_a_guest() -> None:
    """Guest is keyed on the provider, never on a missing phone claim."""
    claims = {"uid": "x", "firebase": {"sign_in_provider": "phone"}}
    assert server_mod._guest_claims(claims) is None


def test_guest_access_switch_turns_guests_off(monkeypatch) -> None:
    monkeypatch.setenv("GUEST_ACCESS_ENABLED", "false")
    assert server_mod._guest_claims(_anon_claims()) is None


# ---------------------------------------------------------------------------
# Routes, through the real app
# ---------------------------------------------------------------------------


TOKENS = {"anon": _anon_claims(), "phone": _phone_claims()}


@pytest.fixture
def app_client(tmp_path, monkeypatch):
    monkeypatch.setenv("FIREBASE_AUTH_ENABLED", "true")
    monkeypatch.delenv("GUEST_ACCESS_ENABLED", raising=False)
    monkeypatch.setattr(firebase_auth, "is_initialised", lambda: True)

    def _verify(token: str) -> dict:
        if token not in TOKENS:
            from src.api.auth import AuthError

            raise AuthError("bad token")
        return dict(TOKENS[token])

    monkeypatch.setattr(firebase_auth, "verify_id_token", _verify)
    # The API's snapshot cache is a module singleton another test may have
    # left warm with its own engine's signals; force it cold so these routes
    # read this test's stub engine.
    from src.api.snapshot_cache import snapshot_cache

    monkeypatch.setattr(snapshot_cache, "filter_signals", lambda **_k: None)
    monkeypatch.setattr(snapshot_cache, "filter_activity", lambda **_k: None)
    store = UserStore(tmp_path / "lumin.sqlite")
    app = build_app(_StubEngine(), jwt_secret="x" * 40, allow_static=False, user_store=store)
    yield TestClient(app), store
    store.close()


def _get(client: TestClient, path: str, who: str):
    return client.get(path, headers={"Authorization": f"Bearer {who}"})


def _paywall(monkeypatch, start: str) -> None:
    monkeypatch.setattr(signal_access, "_configured_start", lambda: signal_access.parse_start(start))


def test_guest_reads_closed_signals_only_and_is_told_how_many_are_locked(app_client) -> None:
    client, _ = app_client
    r = _get(client, "/api/signals?status=all", "anon")
    assert r.status_code == 200
    body = r.json()
    ids = {it["signal_id"] for it in body["items"]}
    assert ids == {"sig-002"}  # the closed one; sig-001 is active
    assert body["live_locked"] is True
    assert body["locked_open_count"] == 1
    assert body["live_access"]["reason"] == "guest"
    assert "private" in r.headers["cache-control"]


def test_guest_asking_for_open_gets_nothing_open(app_client) -> None:
    client, _ = app_client
    body = _get(client, "/api/signals?status=open", "anon").json()
    assert all(not it["is_open"] for it in body["items"])


def test_guest_cannot_open_a_live_signal_by_id_but_can_open_a_closed_one(app_client) -> None:
    client, _ = app_client
    r = _get(client, "/api/signals/sig-001", "anon")
    assert r.status_code == 403 and r.json()["detail"] == "live_signal_locked"
    assert _get(client, "/api/signals/sig-002", "anon").status_code == 200


def test_guest_activity_hides_events_of_live_signals(app_client) -> None:
    client, _ = app_client
    phone = _get(client, "/api/activity", "phone").json()["items"]
    guest = _get(client, "/api/activity", "anon").json()["items"]
    assert any(e["signal_open"] for e in phone)
    assert not any(e["signal_open"] for e in guest)
    assert not any("ETHUSDT" in e["title"] and e["kind"] == "OPEN" for e in guest)


def test_guest_gets_no_engine_wide_positions(app_client) -> None:
    client, _ = app_client
    assert _get(client, "/api/positions", "anon").json()["items"] == []


def test_guest_creates_no_user_row(app_client) -> None:
    client, store = app_client
    _get(client, "/api/signals", "anon")
    _get(client, "/api/pulse", "anon")
    assert store.get_by_firebase_uid("anon-1") is None


def test_guest_is_refused_per_user_endpoints(app_client) -> None:
    client, _ = app_client
    assert _get(client, "/api/profile", "anon").status_code in (401, 403, 404)
    assert _get(client, "/api/binance/connect/status", "anon").status_code in (401, 403, 404, 503)


def test_guest_reads_pulse(app_client) -> None:
    client, _ = app_client
    assert _get(client, "/api/pulse", "anon").status_code == 200


def test_phone_user_sees_live_signals_while_the_paywall_is_off(app_client) -> None:
    client, _ = app_client
    body = _get(client, "/api/signals?status=all", "phone").json()
    assert {it["signal_id"] for it in body["items"]} == {"sig-001", "sig-002"}
    assert body["live_locked"] is False


def test_phone_user_inside_free_days_sees_live_signals(app_client, monkeypatch) -> None:
    client, _ = app_client
    _paywall(monkeypatch, (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat())
    body = _get(client, "/api/signals?status=all", "phone").json()
    assert body["live_locked"] is False
    assert body["live_access"]["reason"] == "free_window"
    profile = _get(client, "/api/profile", "phone").json()
    assert profile["live_access"]["reason"] == "free_window"


def test_phone_user_after_free_days_is_locked_and_a_plan_unlocks(app_client, monkeypatch) -> None:
    client, store = app_client
    _paywall(monkeypatch, (datetime.now(timezone.utc) - timedelta(days=10)).isoformat())
    _get(client, "/api/profile", "phone")  # materialise the row
    user = store.get_by_firebase_uid("phone-1")
    # Pretend the account is old so its free days are over.
    monkeypatch.setattr(
        signal_access, "_free_days", lambda: 0,
    )
    locked = _get(client, "/api/signals?status=all", "phone").json()
    assert locked["live_locked"] is True
    assert {it["signal_id"] for it in locked["items"]} == {"sig-002"}
    assert _get(client, "/api/signals/sig-001", "phone").status_code == 403

    store.set_tier(user.user_id, tier="signals", paid_until=datetime.now(timezone.utc) + timedelta(days=30))
    unlocked = _get(client, "/api/signals?status=all", "phone").json()
    assert unlocked["live_locked"] is False
    assert unlocked["live_access"]["reason"] == "plan"
    assert _get(client, "/api/signals/sig-001", "phone").status_code == 200


# ---------------------------------------------------------------------------
# Push: once the paywall is on, the new-signal push is a teaser for everyone
# ---------------------------------------------------------------------------


class _Dir:
    value = "LONG"


class _Sig:
    signal_id = "s1"
    symbol = "BTCUSDT"
    direction = _Dir()
    entry = 64000.0
    stop_loss = 63200.0
    tp1 = 65000.0
    confidence = 80.0


def _capture_push(monkeypatch):
    import src.push_notifications as pn

    sent = []
    monkeypatch.setattr(pn, "FCM_PUSH_SIGNALS_ENABLED", True)
    monkeypatch.setattr(pn, "_dispatch", lambda topic, title, body, data, ch: sent.append((title, body, data)))
    return pn, sent


def test_push_is_a_teaser_once_the_paywall_is_active(monkeypatch) -> None:
    pn, sent = _capture_push(monkeypatch)
    monkeypatch.setattr(signal_access, "paywall_active", lambda now=None: True)
    pn.push_signal_published(_Sig())
    title, body, data = sent[0]
    for leak in ("64000", "63200", "65000", "LONG"):
        assert leak not in title and leak not in body and leak not in str(data)
    assert "BTCUSDT" in title and data["teaser"] == "1"


def test_push_keeps_its_levels_while_the_paywall_is_off(monkeypatch) -> None:
    pn, sent = _capture_push(monkeypatch)
    monkeypatch.setattr(signal_access, "paywall_active", lambda now=None: False)
    pn.push_signal_published(_Sig())
    title, body, data = sent[0]
    assert "LONG" in title and "64000" in body and data["direction"] == "LONG"
