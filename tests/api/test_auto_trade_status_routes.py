"""Tests for src.api.auto_trade_status_routes.

Same wiring pattern as test_binance_connect_routes (PR-2):
auth stub + identity stub + a FastAPI app that registers the route.
KillSwitchClient is mocked at the module boundary.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app(
    *,
    identity: object = None,
    allow_auth: bool = True,
    get_engine=None,
) -> FastAPI:
    from src.api import auto_trade_status_routes

    app = FastAPI()

    def _auth_stub() -> None:
        if not allow_auth:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="missing token")
        return None

    def _identity_stub() -> object:
        return identity

    auto_trade_status_routes.register(
        app, auth=_auth_stub, identity_dep=_identity_stub, get_engine=get_engine
    )
    return app


def _firebase_user(uid: str = "fb-uid-test") -> object:
    return SimpleNamespace(firebase_uid=uid, user_id=99)


def _user_row(user_id: int = 1, tier: str = "auto", paid_until=None):
    """A UserStore ``User``-shaped row for the runtime-status mocks.

    The endpoint reads ``.tier`` and ``.paid_until`` for the tier-gate
    verdict (2026-07-17), so the fakes must carry real values — a bare
    ``MagicMock(user_id=1)`` would leak a truthy MagicMock ``tier`` into
    the JSON payload.  Defaults model the fully-entitled AUTO user.
    """
    return MagicMock(user_id=user_id, tier=tier, paid_until=paid_until)


@pytest.fixture(autouse=True)
def _reset_kill_switch():
    from src.execution import kill_switch
    kill_switch.reset_for_test()
    yield
    kill_switch.reset_for_test()


@pytest.fixture(autouse=True)
def _reset_runtime_cache():
    """Clear the per-uid runtime-status TTL cache between tests.

    ``auto_trade_status_routes`` memoises each user's runtime-status payload
    for ``_RUNTIME_CACHE_TTL_S`` (PR #561).  The cache is module-global, so
    without a reset a payload built by one test leaks into the next when they
    share a firebase_uid — which made ``test_runtime_status_reads_symbol_
    allowlist_from_env`` pass alone but fail in-file (order-dependent), and is
    the same global-state hazard every other test in this module is exposed
    to.  Reset before and after so each test starts cold.
    """
    from src.api import auto_trade_status_routes
    auto_trade_status_routes._runtime_cache.clear()
    yield
    auto_trade_status_routes._runtime_cache.clear()


# ---------------------------------------------------------------------------
# Auth + identity
# ---------------------------------------------------------------------------


def test_no_auth_returns_401() -> None:
    app = _build_app(allow_auth=False)
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 401


def test_static_token_bypass_rejected_with_401() -> None:
    """The status endpoint requires a Firebase identity — static-
    token bypass (identity=None) should return 401 with a 'sign in'
    message rather than serving a default response."""
    app = _build_app(identity=None)
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 401
    assert "Firebase" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Kill switch not initialised (dev path) → safe default
# ---------------------------------------------------------------------------


def test_kill_switch_not_initialised_returns_safe_default() -> None:
    """When the server-side execution stack isn't wired (no GCP env
    vars), the endpoint returns a default-safe response rather than
    500 — keeps the Lumin app's banner UI functional in dev /
    pre-deploy contexts."""
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 200
    body = r.json()
    # Default state: globally NOT enabled, user not specifically
    # disabled.  Matches the doctrine default-deny on fresh deploy.
    assert body["auto_trade_globally_enabled"] is False
    assert body["auto_trade_user_disabled"] is False
    assert body["disabled_reason"] == ""
    assert body["disabled_at"] is None


# ---------------------------------------------------------------------------
# Kill switch initialised — reads from Firestore (mocked)
# ---------------------------------------------------------------------------


def _install_kill_switch_with_flags(
    *, enabled: bool, user_disabled: bool
) -> None:
    """Inject a KillSwitchClient that returns the given flags."""
    from src.execution import kill_switch

    fake = MagicMock()
    fake.is_globally_enabled = MagicMock(return_value=enabled)
    fake.is_user_disabled = MagicMock(return_value=user_disabled)
    kill_switch._client = fake


def test_returns_both_flags_when_initialised() -> None:
    _install_kill_switch_with_flags(enabled=True, user_disabled=False)
    app = _build_app(identity=_firebase_user(uid="fb-x"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 200
    body = r.json()
    assert body["auto_trade_globally_enabled"] is True
    assert body["auto_trade_user_disabled"] is False


def test_user_disabled_state_returned() -> None:
    """User-specific disable returns True on the response."""
    _install_kill_switch_with_flags(enabled=True, user_disabled=True)
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    body = r.json()
    assert body["auto_trade_user_disabled"] is True


def test_globally_disabled_state_returned() -> None:
    """Pre-flip global state returns enabled=False — the Lumin app
    surfaces "auto-trade globally paused" in this case."""
    _install_kill_switch_with_flags(enabled=False, user_disabled=False)
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    body = r.json()
    assert body["auto_trade_globally_enabled"] is False


def test_firestore_failure_returns_safe_default_with_reason() -> None:
    """A Firestore read failure (transient outage) returns the
    default-safe response with a diagnostic ``disabled_reason``
    rather than 500.  The Lumin app's banner UI keeps working;
    only the precision of the state is degraded."""
    from src.execution import kill_switch

    fake = MagicMock()
    fake.is_globally_enabled = MagicMock(
        side_effect=RuntimeError("Firestore unreachable")
    )
    fake.is_user_disabled = MagicMock(return_value=False)
    kill_switch._client = fake
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    r = client.get("/api/auto-trade/user-status")
    assert r.status_code == 200
    body = r.json()
    assert body["auto_trade_globally_enabled"] is False
    assert "RuntimeError" in body["disabled_reason"]


# ---------------------------------------------------------------------------
# runtime-status — composite for the Live-tab "Auto-trade armed" card
# ---------------------------------------------------------------------------


def test_runtime_status_requires_firebase_auth() -> None:
    """Static-token bypass returns 401 — the per-user state is keyed
    on Firebase uid so we cannot serve a meaningful response without."""
    app = _build_app(identity=None)
    client = TestClient(app)
    r = client.get("/api/auto-trade/runtime-status")
    assert r.status_code == 401


def test_runtime_status_default_safe_when_nothing_initialised(
    monkeypatch,
) -> None:
    """Engine boot without GCP env returns safe defaults across the
    board: every gate False, no allowed symbols (env unset), armed
    False.  The app renders all-red checks + "engine not configured
    for auto-trade" guidance."""
    monkeypatch.delenv("TRIPWIRE_SYMBOL_ALLOWLIST", raising=False)
    app = _build_app(identity=_firebase_user(uid="fb-y"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/runtime-status")
    assert r.status_code == 200
    body = r.json()
    assert body["auto_trade_globally_enabled"] is False
    assert body["auto_trade_user_disabled"] is False
    assert body["binance_key_connected"] is False
    assert body["user_mode"] is None
    assert body["allowed_symbols"] == []
    assert body["armed"] is False


def test_runtime_status_reads_symbol_allowlist_from_env(
    monkeypatch,
) -> None:
    """The allowed-symbols list reflects the engine's current
    ``TRIPWIRE_SYMBOL_ALLOWLIST`` — the user-facing card should
    display the same five symbols the FSM checks orders against."""
    monkeypatch.setenv(
        "TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT,SOLUSDT,XRPUSDT,BNBUSDT",
    )
    app = _build_app(identity=_firebase_user(uid="fb-y"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/runtime-status")
    body = r.json()
    assert body["allowed_symbols"] == [
        "BNBUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT",
    ]
    # Without a per-user preference set, effective = engine cap.
    assert body["effective_allowed_symbols"] == body["allowed_symbols"]


def test_runtime_status_effective_intersects_user_pref(
    monkeypatch,
) -> None:
    """When the user sets a symbol_preference, the runtime status
    surfaces the intersection so the app footnote shows the user's
    actual tradable set, not just the engine cap."""
    from src.api import user_overrides as _uo
    from src.api import users as _users_module

    monkeypatch.setenv(
        "TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT,ETHUSDT,SOLUSDT,XRPUSDT,BNBUSDT",
    )
    fake_user = _user_row(user_id=1)
    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=fake_user)
    # effective_allowed_symbols_for_user (run via to_thread) uses the
    # synchronous accessors, so mock both shapes.
    fake_user_store.get_by_firebase_uid = MagicMock(return_value=fake_user)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    fake_overrides_store = MagicMock()
    fake_overrides_store.aget_auto_trade = AsyncMock(
        return_value={"symbol_preference": ["BTCUSDT", "SOLUSDT"]}
    )
    fake_overrides_store.get_auto_trade = MagicMock(
        return_value={"symbol_preference": ["BTCUSDT", "SOLUSDT"]}
    )
    monkeypatch.setattr(
        _uo, "_SINGLETON", fake_overrides_store, raising=False,
    )

    app = _build_app(identity=_firebase_user(uid="fb-prefs"))
    client = TestClient(app)
    body = client.get("/api/auto-trade/runtime-status").json()
    assert body["allowed_symbols"] == [
        "BNBUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT",
    ]
    assert body["effective_allowed_symbols"] == ["BTCUSDT", "SOLUSDT"]


def _facade_stub(pairs: object):
    """RedisEngineFacade-shaped stub exposing ``published_pairs()``."""
    stub = MagicMock()
    stub.published_pairs = MagicMock(return_value=pairs)
    return stub


@pytest.fixture()
def _no_pair_manager(monkeypatch):
    """Model the isolated api container: no PairManager singleton in-process.

    Other test modules may leave a live singleton behind; the fallback tests
    must see the empty in-process resolution the api container really gets.
    """
    monkeypatch.setattr("src.pair_manager.get_singleton", lambda: None)


def test_runtime_status_allowlist_falls_back_to_pairs_snapshot(
    monkeypatch, _no_pair_manager,
) -> None:
    """Isolated api container (2026-07-18, same class as the KMS bug #736):
    no PairManager singleton lives in this process, so the in-process
    allowlist resolves to the block-all empty set and every user rendered
    "Watching 0 symbols" while the engine traded a full universe.  With
    the env unset, the route must substitute the engine-published pairs
    snapshot (regular + mover-promoted)."""
    monkeypatch.delenv("TRIPWIRE_SYMBOL_ALLOWLIST", raising=False)
    facade = _facade_stub({
        "regular": [
            {"symbol": "BTCUSDT", "tier": "T1"},
            {"symbol": "ETHUSDT", "tier": "T1"},
        ],
        "promoting": [{"symbol": "MOVERUSDT", "cycles_remaining": 3}],
    })
    app = _build_app(
        identity=_firebase_user(uid="fb-iso"), get_engine=lambda: facade
    )
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["allowed_symbols"] == ["BTCUSDT", "ETHUSDT", "MOVERUSDT"]
    # No per-user preference in this test → effective == engine list.
    assert body["effective_allowed_symbols"] == body["allowed_symbols"]


def test_runtime_status_snapshot_fallback_intersects_user_pref(
    monkeypatch, _no_pair_manager,
) -> None:
    """The per-user symbol_preference intersection must apply to the
    snapshot-sourced allowlist exactly as it does to the env-sourced one."""
    from src.api import user_overrides as _uo
    from src.api import users as _users_module

    monkeypatch.delenv("TRIPWIRE_SYMBOL_ALLOWLIST", raising=False)
    fake_user = _user_row(user_id=1)
    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=fake_user)
    fake_user_store.get_by_firebase_uid = MagicMock(return_value=fake_user)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    fake_overrides_store = MagicMock()
    fake_overrides_store.aget_auto_trade = AsyncMock(
        return_value={"symbol_preference": ["ETHUSDT"]}
    )
    fake_overrides_store.get_auto_trade = MagicMock(
        return_value={"symbol_preference": ["ETHUSDT"]}
    )
    monkeypatch.setattr(_uo, "_SINGLETON", fake_overrides_store, raising=False)

    facade = _facade_stub({
        "regular": [{"symbol": "BTCUSDT"}, {"symbol": "ETHUSDT"}],
        "promoting": [],
    })
    app = _build_app(
        identity=_firebase_user(uid="fb-iso-pref"), get_engine=lambda: facade
    )
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["allowed_symbols"] == ["BTCUSDT", "ETHUSDT"]
    assert body["effective_allowed_symbols"] == ["ETHUSDT"]


def test_runtime_status_env_allowlist_wins_over_snapshot(monkeypatch) -> None:
    """The operator hard-narrow env stays authoritative — the snapshot
    fallback fires only when the in-process resolution is empty."""
    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT")
    facade = _facade_stub({
        "regular": [{"symbol": "ETHUSDT"}], "promoting": [],
    })
    app = _build_app(
        identity=_firebase_user(uid="fb-envwin"), get_engine=lambda: facade
    )
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["allowed_symbols"] == ["BTCUSDT"]
    facade.published_pairs.assert_not_called()


def test_runtime_status_snapshot_fallback_survives_facade_error(
    monkeypatch, _no_pair_manager,
) -> None:
    """A facade read failure must degrade to the previous behaviour
    (empty list), never 500 the status endpoint."""
    monkeypatch.delenv("TRIPWIRE_SYMBOL_ALLOWLIST", raising=False)
    facade = MagicMock()
    facade.published_pairs = MagicMock(side_effect=RuntimeError("redis down"))
    app = _build_app(
        identity=_firebase_user(uid="fb-iso-err"), get_engine=lambda: facade
    )
    r = TestClient(app).get("/api/auto-trade/runtime-status")
    assert r.status_code == 200
    assert r.json()["allowed_symbols"] == []


def test_runtime_status_armed_when_all_gates_green(monkeypatch) -> None:
    """All four gates green AND user_mode=='live' → armed=True.
    Models the "auto-trade is firing now" UX state.

    2026-05-23: user_mode now resolves via firebase_uid → user_id →
    user_auto_trade_settings(user_id).mode (per-user), not the
    operator_auto_trade_override singleton.  Test mocks the
    user_store + override_store accordingly.
    """
    from src.api import user_overrides as _uo
    from src.api import users as _users_module
    from src.execution import kill_switch
    from src.security import firestore_keystore as _fk
    from src.security.firestore_keystore import UserKeyBlob
    from datetime import datetime, timezone

    # Globally enabled, user not disabled.
    ks = MagicMock()
    ks.is_globally_enabled = MagicMock(return_value=True)
    ks.is_user_disabled = MagicMock(return_value=False)
    kill_switch._client = ks

    # Binance key blob exists.
    _fk._db = MagicMock()
    def _fake_get_key_blob(uid: str) -> UserKeyBlob:
        return UserKeyBlob(
            uid=uid,
            encrypted_secret=b"\x00",
            encrypted_dek=b"\x00",
            api_key_full="ABCDEFGH...",
            key_public_id_first8="ABCDEFGH",
            ip_whitelist_ok=True,
            withdraw_disabled_ok=True,
            connected_at=datetime.now(timezone.utc),
            last_validated_at=datetime.now(timezone.utc),
        )
    monkeypatch.setattr(_fk, "get_key_blob", _fake_get_key_blob)

    # User mode = live — resolved per-user from
    # ``user_auto_trade_settings`` keyed by the calling user's
    # firebase_uid → user_id.  Both stores must mock the chained
    # lookup since the endpoint walks user_store → override_store.
    fake_user = _user_row(user_id=1)
    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=fake_user)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    fake_overrides_store = MagicMock()
    fake_overrides_store.aget_auto_trade = AsyncMock(return_value={"mode": "live"})
    monkeypatch.setattr(_uo, "_SINGLETON", fake_overrides_store, raising=False)

    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT")

    app = _build_app(identity=_firebase_user(uid="fb-armed"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/runtime-status")
    body = r.json()
    assert body["armed"] is True
    assert body["auto_trade_globally_enabled"] is True
    assert body["binance_key_connected"] is True
    assert body["user_mode"] == "live"


def test_runtime_status_armed_false_when_user_in_paper(monkeypatch) -> None:
    """Paper mode is *configured* auto-trade but does NOT place real
    orders.  ``armed`` reflects "real-money orders flowing" so paper
    keeps ``armed=False`` even when all other gates are green."""
    from src.api import user_overrides as _uo
    from src.api import users as _users_module
    from src.execution import kill_switch
    from src.security import firestore_keystore as _fk
    from src.security.firestore_keystore import UserKeyBlob
    from datetime import datetime, timezone

    ks = MagicMock()
    ks.is_globally_enabled = MagicMock(return_value=True)
    ks.is_user_disabled = MagicMock(return_value=False)
    kill_switch._client = ks

    _fk._db = MagicMock()
    def _fake_get_key_blob(uid: str) -> UserKeyBlob:
        return UserKeyBlob(
            uid=uid, encrypted_secret=b"\x00", encrypted_dek=b"\x00",
            api_key_full="ABCDEFGH...", key_public_id_first8="ABCDEFGH",
            ip_whitelist_ok=True, withdraw_disabled_ok=True,
            connected_at=datetime.now(timezone.utc),
            last_validated_at=datetime.now(timezone.utc),
        )
    monkeypatch.setattr(_fk, "get_key_blob", _fake_get_key_blob)

    # Same per-user resolution chain as the armed-live test above —
    # mode comes from the calling user's own row.
    fake_user = _user_row(user_id=2)
    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=fake_user)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    fake_overrides_store = MagicMock()
    fake_overrides_store.aget_auto_trade = AsyncMock(return_value={"mode": "paper"})
    monkeypatch.setattr(_uo, "_SINGLETON", fake_overrides_store, raising=False)

    app = _build_app(identity=_firebase_user(uid="fb-paper"))
    client = TestClient(app)
    body = client.get("/api/auto-trade/runtime-status").json()
    assert body["armed"] is False
    assert body["user_mode"] == "paper"


def test_runtime_status_no_mode_leak_across_users(monkeypatch) -> None:
    """**Per-user isolation pin.**  User A sets ``mode = "paper"`` via
    their own row; user B (different firebase_uid → different user_id
    → no row in user_auto_trade_settings) must see
    ``user_mode == None``, NOT user A's "paper".

    Owner-reported 2026-05-23: "many owner changes are applying to all
    users" — the pre-fix endpoint consulted
    ``operator_auto_trade_override()`` which returned the most-recently-
    updated row across the whole table, leaking the operator's mode
    onto every authenticated user's response.  This test is the
    regression pin: a per-user row for user A must NOT influence
    user B's response.
    """
    from src.api import user_overrides as _uo
    from src.api import users as _users_module

    # Two users registered: user_id=1 has mode=paper, user_id=2 has no row.
    user_a = _user_row(user_id=1)
    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=user_a)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    fake_overrides_store = MagicMock()
    # Real per-user resolution: user_id=1 → has paper, user_id=2 → empty.
    def _fake_get_auto_trade(user_id: int):
        return {"mode": "paper"} if user_id == 1 else {}
    fake_overrides_store.aget_auto_trade = AsyncMock(side_effect=_fake_get_auto_trade)
    monkeypatch.setattr(_uo, "_SINGLETON", fake_overrides_store, raising=False)

    # User A request — mode resolves to "paper".
    app_a = _build_app(identity=_firebase_user(uid="fb-A"))
    body = TestClient(app_a).get("/api/auto-trade/runtime-status").json()
    assert body["user_mode"] == "paper"

    # User B is a DISTINCT user — distinct firebase_uid (as every real user
    # is; firebase_uid is the stable per-user identity) resolving to
    # user_id=2 with no override row.  Must come back as None, NOT carried
    # over from user A.  Using a distinct uid is also what keeps the per-uid
    # runtime cache (PR #561) honest: the leak this pins is per-USER, and two
    # users never share a uid, so the cache key differs and cannot serve A's
    # payload to B.
    user_b = _user_row(user_id=2)
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=user_b)
    app_b = _build_app(identity=_firebase_user(uid="fb-B"))
    body = TestClient(app_b).get("/api/auto-trade/runtime-status").json()
    assert body["user_mode"] is None, (
        "Per-user isolation: user B without a row must NOT inherit "
        "user A's mode (regression pin for the operator-override leak)."
    )


# ---------------------------------------------------------------------------
# runtime-status — the silent dispatch gates (tier / auto-pause / prefs)
#
# Regression pins for the 2026-07-17 owner report: "connected and ARMED
# but trading not happening", zero recent-activity rows.  Dispatch skips
# silently BEFORE any dispatch_log write on tier, auto-pause, and
# path/regime preferences — the armed card must evaluate the same gates
# or it lies green over a silent skip.
# ---------------------------------------------------------------------------


def _install_green_gates(monkeypatch, *, user, auto_trade_row) -> None:
    """All pre-2026-07-17 gates green: kill switch enabled + user not
    disabled, key blob present, per-user stores returning the given
    user row + auto-trade row.  Tests then vary tier/pause/prefs."""
    from datetime import datetime, timezone

    from src.api import user_overrides as _uo
    from src.api import users as _users_module
    from src.execution import kill_switch
    from src.security import firestore_keystore as _fk
    from src.security.firestore_keystore import UserKeyBlob

    ks = MagicMock()
    ks.is_globally_enabled = MagicMock(return_value=True)
    ks.is_user_disabled = MagicMock(return_value=False)
    kill_switch._client = ks

    _fk._db = MagicMock()

    def _fake_get_key_blob(uid: str) -> UserKeyBlob:
        return UserKeyBlob(
            uid=uid, encrypted_secret=b"\x00", encrypted_dek=b"\x00",
            api_key_full="ABCDEFGH...", key_public_id_first8="ABCDEFGH",
            ip_whitelist_ok=True, withdraw_disabled_ok=True,
            connected_at=datetime.now(timezone.utc),
            last_validated_at=datetime.now(timezone.utc),
        )

    monkeypatch.setattr(_fk, "get_key_blob", _fake_get_key_blob)

    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=user)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    fake_overrides_store = MagicMock()
    fake_overrides_store.aget_auto_trade = AsyncMock(return_value=auto_trade_row)
    monkeypatch.setattr(_uo, "_SINGLETON", fake_overrides_store, raising=False)

    monkeypatch.setenv("TRIPWIRE_SYMBOL_ALLOWLIST", "BTCUSDT")


def test_runtime_status_not_armed_when_tier_free(monkeypatch) -> None:
    """THE bug this section pins: a free-tier user with every legacy
    gate green must NOT show armed — dispatch skips them silently at
    the entitlement gate with no activity row, so the card is the only
    place the user can learn why."""
    _install_green_gates(
        monkeypatch,
        user=_user_row(user_id=1, tier="free"),
        auto_trade_row={"mode": "live"},
    )
    app = _build_app(identity=_firebase_user(uid="fb-free"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["user_tier"] == "free"
    assert body["tier_allows_auto"] is False
    assert body["armed"] is False
    # The four legacy gates stay green — proving the card can explain
    # exactly which gate is the blocker instead of a mystery yellow.
    assert body["auto_trade_globally_enabled"] is True
    assert body["auto_trade_user_disabled"] is False
    assert body["binance_key_connected"] is True
    assert body["user_mode"] == "live"


def test_runtime_status_expired_paid_window_downgrades_tier(monkeypatch) -> None:
    """tier='auto' with a lapsed paid_until is downgraded to free at
    read time — the same defence-in-depth rule dispatch applies
    (signal_dispatch._resolve_user_tier), so the card matches what
    dispatch will actually do."""
    from datetime import datetime, timedelta, timezone

    _install_green_gates(
        monkeypatch,
        user=_user_row(
            user_id=1,
            tier="auto",
            paid_until=datetime.now(timezone.utc) - timedelta(days=3),
        ),
        auto_trade_row={"mode": "live"},
    )
    app = _build_app(identity=_firebase_user(uid="fb-lapsed"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["user_tier"] == "free"
    assert body["tier_allows_auto"] is False
    assert body["armed"] is False


def test_runtime_status_tier_gate_disabled_bypasses_tier(monkeypatch) -> None:
    """AUTO_TRADE_TIER_GATE_ENABLED=False (the reversible flag) means
    dispatch never checks tier — the card must mirror that too."""
    import config as _config

    monkeypatch.setattr(_config, "AUTO_TRADE_TIER_GATE_ENABLED", False)
    _install_green_gates(
        monkeypatch,
        user=_user_row(user_id=1, tier="free"),
        auto_trade_row={"mode": "live"},
    )
    app = _build_app(identity=_firebase_user(uid="fb-gate-off"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["tier_gate_enabled"] is False
    assert body["tier_allows_auto"] is True
    assert body["armed"] is True


def test_runtime_status_not_armed_when_auto_paused(monkeypatch) -> None:
    """A dispatcher auto-pause (paused_reason set after 3× -2019) skips
    every signal silently — the card must go yellow server-side, not
    rely on the client-side settings AND."""
    _install_green_gates(
        monkeypatch,
        user=_user_row(user_id=1, tier="auto"),
        auto_trade_row={"mode": "live", "paused_reason": "insufficient_margin"},
    )
    app = _build_app(identity=_firebase_user(uid="fb-paused"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["auto_paused"] is True
    assert body["armed"] is False


def test_runtime_status_block_all_path_pref_unarms(monkeypatch) -> None:
    """An explicit empty path_preference means NO signal ever matches
    (block-all) — guaranteed zero orders, so it unarms."""
    _install_green_gates(
        monkeypatch,
        user=_user_row(user_id=1, tier="auto"),
        auto_trade_row={"mode": "live", "path_preference": []},
    )
    app = _build_app(identity=_firebase_user(uid="fb-blockall"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["path_preference"] == []
    assert body["preferences_block_all"] is True
    assert body["armed"] is False


def test_runtime_status_restrictive_pref_stays_armed(monkeypatch) -> None:
    """A restrictive-but-non-empty preference is a per-signal filter —
    orders remain possible, so it must NOT unarm; the list is surfaced
    for the app to render as a footnote warning."""
    _install_green_gates(
        monkeypatch,
        user=_user_row(user_id=1, tier="auto"),
        auto_trade_row={
            "mode": "live",
            "path_preference": ["sr_flip_retest"],
            "regime_preference": ["TRENDING_UP", "TRENDING_DOWN"],
        },
    )
    app = _build_app(identity=_firebase_user(uid="fb-filtered"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["path_preference"] == ["SR_FLIP_RETEST"]  # uppercased tokens
    assert body["regime_preference"] == ["TRENDING_DOWN", "TRENDING_UP"]
    assert body["preferences_block_all"] is False
    assert body["armed"] is True


def test_runtime_status_unknown_user_fails_closed_on_tier(monkeypatch) -> None:
    """No user row resolvable → tier fails closed to free (never render
    a green tier gate for an account dispatch can't confirm)."""
    from src.api import users as _users_module

    fake_user_store = MagicMock()
    fake_user_store.aget_by_firebase_uid = AsyncMock(return_value=None)
    monkeypatch.setattr(_users_module, "_store", fake_user_store, raising=False)

    app = _build_app(identity=_firebase_user(uid="fb-unknown"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["user_tier"] == "free"
    assert body["tier_allows_auto"] is False
    assert body["armed"] is False


def test_runtime_status_armed_green_includes_new_fields(monkeypatch) -> None:
    """The fully-armed payload carries the new fields with their
    happy-path values — the app's gate rows read these directly."""
    _install_green_gates(
        monkeypatch,
        user=_user_row(user_id=1, tier="auto"),
        auto_trade_row={"mode": "live"},
    )
    app = _build_app(identity=_firebase_user(uid="fb-green"))
    body = TestClient(app).get("/api/auto-trade/runtime-status").json()
    assert body["armed"] is True
    assert body["user_tier"] == "auto"
    assert body["tier_gate_enabled"] is True
    assert body["tier_allows_auto"] is True
    assert body["auto_paused"] is False
    assert body["path_preference"] is None
    assert body["regime_preference"] is None
    assert body["preferences_block_all"] is False


# ---------------------------------------------------------------------------
# positions — Live-tab "your open positions" card backend
# ---------------------------------------------------------------------------


def test_positions_requires_firebase_auth() -> None:
    app = _build_app(identity=None)
    client = TestClient(app)
    assert client.get("/api/auto-trade/positions").status_code == 401


def test_positions_returns_empty_when_position_state_not_initialised() -> None:
    """Engine boot without server-side execution stack still answers
    with an empty list — the Live tab renders "no open positions"
    which is accurate (engine isn't tracking any)."""
    from src.execution import position_state
    position_state._db = None
    app = _build_app(identity=_firebase_user(uid="fb-z"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/positions")
    assert r.status_code == 200
    assert r.json() == {"positions": []}


def test_positions_returns_user_positions_from_firestore(
    monkeypatch,
) -> None:
    """End-to-end: a mocked Firestore that returns two open positions
    surfaces both in the response shape the app expects."""
    from datetime import datetime, timezone
    from src.execution import position_state

    now = datetime.now(timezone.utc)

    def _fake_list(firebase_uid: str, *, include_closed: bool = False):
        return [
            position_state.Position(
                signal_id="sig-a",
                firebase_uid=firebase_uid,
                symbol="BTCUSDT",
                side="LONG",
                state=position_state.PositionState.OPEN,
                entry_price_target=29000.0,
                entry_price_filled=29005.5,
                sl_price=28500.0,
                tp1_price=29500.0,
                tp2_price=30000.0,
                tp3_price=30500.0,
                total_qty=1.0,
                tp1_qty=0.3,
                tp2_qty=0.4,
                tp3_qty=0.3,
                filled_qty=1.0,
                created_at=now,
                pretp_fired=False,
                realized_pnl_total=0.0,
            )
        ]

    # Set _db to a truthy sentinel so the endpoint's "not initialised"
    # short-circuit doesn't fire; then patch list_positions_for_user.
    position_state._db = MagicMock()
    monkeypatch.setattr(position_state, "list_positions_for_user", _fake_list)

    app = _build_app(identity=_firebase_user(uid="fb-w"))
    client = TestClient(app)
    body = client.get("/api/auto-trade/positions").json()
    assert len(body["positions"]) == 1
    pos = body["positions"][0]
    assert pos["signal_id"] == "sig-a"
    assert pos["symbol"] == "BTCUSDT"
    assert pos["side"] == "LONG"
    assert pos["state"] == "OPEN"
    assert pos["entry_price_filled"] == 29005.5
    assert pos["pretp_fired"] is False
    assert pos["created_at"] == now.isoformat()


# ---------------------------------------------------------------------------
# recent-events endpoint — dispatch event log for the user-facing
# Recent Activity card
# ---------------------------------------------------------------------------


def test_recent_events_requires_firebase_auth() -> None:
    app = _build_app(identity=None)
    client = TestClient(app)
    assert client.get("/api/auto-trade/recent-events").status_code == 401


def test_recent_events_returns_empty_when_not_initialised() -> None:
    """No dispatch_log singleton wired (engine boot without GCP env)
    → returns ``{"events": []}`` not 5xx.  Matches the safe-default
    posture of every other server-side read endpoint."""
    from src.execution import dispatch_log
    dispatch_log.reset_for_test()
    app = _build_app(identity=_firebase_user(uid="fb-z"))
    client = TestClient(app)
    r = client.get("/api/auto-trade/recent-events")
    assert r.status_code == 200
    assert r.json() == {"events": []}


def test_recent_events_returns_user_events_from_firestore(
    monkeypatch,
) -> None:
    """End-to-end: a mocked dispatch_log returns one placed event +
    one rejected event with a Binance code; both surface in the
    response shape the app expects."""
    from datetime import datetime, timezone, timedelta
    from src.execution import dispatch_log

    now = datetime.now(timezone.utc)

    def _fake_list(firebase_uid: str, *, limit: int = 20):
        return [
            dispatch_log.DispatchEvent(
                event_id="evt-1",
                firebase_uid=firebase_uid,
                signal_id="sig-A",
                symbol="BTCUSDT",
                direction="LONG",
                outcome="placed",
                timestamp=now,
                entry_price=29000.0,
                total_qty=0.017,
            ),
            dispatch_log.DispatchEvent(
                event_id="evt-2",
                firebase_uid=firebase_uid,
                signal_id="sig-B",
                symbol="PROMUSDT",
                direction="SHORT",
                outcome="rejected",
                timestamp=now - timedelta(minutes=2),
                entry_price=0.1278,
                reject_class="OrderRejectedByBinance",
                reject_detail="full diagnostic",
                reject_binance_code=-2019,
                reject_binance_msg="Margin is insufficient.",
            ),
        ]

    dispatch_log._db = MagicMock()  # truthy so endpoint passes the init guard
    monkeypatch.setattr(dispatch_log, "list_recent_events", _fake_list)

    app = _build_app(identity=_firebase_user(uid="fb-w"))
    client = TestClient(app)
    body = client.get("/api/auto-trade/recent-events").json()
    assert len(body["events"]) == 2
    placed = body["events"][0]
    rejected = body["events"][1]
    assert placed["outcome"] == "placed"
    assert placed["symbol"] == "BTCUSDT"
    assert placed["reject_binance_code"] is None
    assert rejected["outcome"] == "rejected"
    assert rejected["symbol"] == "PROMUSDT"
    assert rejected["reject_class"] == "OrderRejectedByBinance"
    assert rejected["reject_binance_code"] == -2019
    assert rejected["reject_binance_msg"] == "Margin is insufficient."


# ---------------------------------------------------------------------------
# recent-events position join (#988 / #990)
#
# A DispatchEvent is an append-only record of the PLACEMENT MOMENT. It has
# an `outcome` of 'placed' | 'rejected' and NO close/exit field — and that
# immutability is correct, it is an audit log. The bug was that the app
# rendered "Position is open — Lumin manages it from here." from `isPlaced`
# alone, so a row that was placed and closed weeks ago still claimed to be
# open forever. Twenty rows asserted "open" directly underneath a correct
# open-position count of 0.
#
# The fix joins live position state server-side at read time. These tests
# pin the three things that matter: an open position reads open, a CLOSED
# one reads closed WITH its realised PnL, and a missing position degrades
# to null rather than inventing a state.
# ---------------------------------------------------------------------------


def _mk_position(signal_id: str, uid: str, state, **kw):
    """Minimal Position in a given FSM state. Only the fields the join
    reads are meaningful; the rest are structurally required."""
    from src.execution.position_state import Position
    defaults = dict(
        signal_id=signal_id, firebase_uid=uid, symbol="BTCUSDT",
        side="BUY", state=state,
        entry_price_target=29000.0, entry_price_filled=29012.5,
        sl_price=28500.0, tp1_price=29500.0, tp2_price=30000.0,
        tp3_price=30500.0,
        total_qty=0.017, tp1_qty=0.006, tp2_qty=0.006, tp3_qty=0.005,
    )
    defaults.update(kw)
    return Position(**defaults)


def _install_placed_event(monkeypatch, signal_id="sig-A"):
    """One 'placed' dispatch event, dispatch_log init guard satisfied."""
    from datetime import datetime, timezone
    from src.execution import dispatch_log

    def _fake_list(firebase_uid: str, *, limit: int = 20):
        return [dispatch_log.DispatchEvent(
            event_id="evt-1", firebase_uid=firebase_uid, signal_id=signal_id,
            symbol="BTCUSDT", direction="LONG", outcome="placed",
            timestamp=datetime.now(timezone.utc),
            entry_price=29000.0, total_qty=0.017,
        )]

    dispatch_log._db = MagicMock()
    monkeypatch.setattr(dispatch_log, "list_recent_events", _fake_list)


def test_recent_events_open_position_reports_open(monkeypatch) -> None:
    """OPEN is non-terminal → position_is_open True and the filled entry
    price is surfaced so the app can show what actually traded (#990)."""
    from src.execution import position_state as _ps
    _install_placed_event(monkeypatch)
    monkeypatch.setattr(
        _ps, "get_position",
        lambda uid, sid: _mk_position(sid, uid, _ps.PositionState.OPEN),
    )
    app = _build_app(identity=_firebase_user(uid="fb-1"))
    ev = TestClient(app).get("/api/auto-trade/recent-events").json()["events"][0]
    assert ev["position_state"] == "OPEN"
    assert ev["position_is_open"] is True
    assert ev["closed_at"] is None
    # The engine SIGNALLED 29000 but Binance FILLED at 29012.5. Both must
    # reach the app — that difference is the whole point of #990.
    assert ev["entry_price"] == 29000.0
    assert ev["entry_price_filled"] == 29012.5


def test_recent_events_closed_position_does_not_claim_open(
    monkeypatch,
) -> None:
    """THE #988 REGRESSION TEST. A placed-then-closed trade must not read
    as open, and must carry the realised PnL that replaces the bogus
    'Lumin manages it from here' present-tense claim."""
    from datetime import datetime, timezone
    from src.execution import position_state as _ps
    closed = datetime.now(timezone.utc)
    _install_placed_event(monkeypatch)
    monkeypatch.setattr(
        _ps, "get_position",
        lambda uid, sid: _mk_position(
            sid, uid, _ps.PositionState.CLOSED,
            closed_at=closed, realized_pnl_total=12.34,
        ),
    )
    app = _build_app(identity=_firebase_user(uid="fb-2"))
    ev = TestClient(app).get("/api/auto-trade/recent-events").json()["events"][0]
    # outcome stays 'placed' forever — it is a historical fact and the
    # audit log must not be rewritten. Present state lives beside it.
    assert ev["outcome"] == "placed"
    assert ev["position_state"] == "CLOSED"
    assert ev["position_is_open"] is False
    assert ev["realized_pnl_usd"] == 12.34
    assert ev["closed_at"] is not None


def test_recent_events_cancelled_no_fill_is_not_open(monkeypatch) -> None:
    """CANCELLED_NO_FILL is the other terminal state. It is easy to miss
    because it is not literally named 'closed' — a hand-rolled
    `state == "CLOSED"` check would call it open."""
    from src.execution import position_state as _ps
    _install_placed_event(monkeypatch)
    monkeypatch.setattr(
        _ps, "get_position",
        lambda uid, sid: _mk_position(
            sid, uid, _ps.PositionState.CANCELLED_NO_FILL),
    )
    app = _build_app(identity=_firebase_user(uid="fb-3"))
    ev = TestClient(app).get("/api/auto-trade/recent-events").json()["events"][0]
    assert ev["position_state"] == "CANCELLED_NO_FILL"
    assert ev["position_is_open"] is False


def test_recent_events_missing_position_yields_explicit_nulls(
    monkeypatch,
) -> None:
    """Store raises (no doc / offline). The keys must still be PRESENT and
    null: the app has to tell 'we looked, there is nothing' apart from
    'this server build does not send the field'. It must never fall back
    to asserting open."""
    from src.execution import position_state as _ps

    def _boom(uid, sid):
        raise _ps.PositionNotFoundError(sid)

    _install_placed_event(monkeypatch)
    monkeypatch.setattr(_ps, "get_position", _boom)
    app = _build_app(identity=_firebase_user(uid="fb-4"))
    ev = TestClient(app).get("/api/auto-trade/recent-events").json()["events"][0]
    for key in ("position_state", "position_is_open", "realized_pnl_usd",
                "entry_price_filled", "closed_at"):
        assert key in ev, f"{key} must always be present"
        assert ev[key] is None
    # The feed itself still renders.
    assert ev["outcome"] == "placed"


def test_recent_events_rejected_rows_skip_the_position_lookup(
    monkeypatch,
) -> None:
    """A rejected order never became a position, so looking one up would
    be a guaranteed-miss billed read. Cost discipline: only PLACED rows
    are joined."""
    from datetime import datetime, timezone
    from src.execution import dispatch_log
    from src.execution import position_state as _ps

    def _fake_list(firebase_uid: str, *, limit: int = 20):
        return [dispatch_log.DispatchEvent(
            event_id="evt-r", firebase_uid=firebase_uid, signal_id="sig-R",
            symbol="PROMUSDT", direction="SHORT", outcome="rejected",
            timestamp=datetime.now(timezone.utc),
            reject_class="OrderRejectedByBinance", reject_binance_code=-2019,
        )]

    dispatch_log._db = MagicMock()
    monkeypatch.setattr(dispatch_log, "list_recent_events", _fake_list)

    calls = []

    def _spy(uid, sid):
        calls.append(sid)
        raise AssertionError("must not look up a rejected order")

    monkeypatch.setattr(_ps, "get_position", _spy)
    app = _build_app(identity=_firebase_user(uid="fb-5"))
    ev = TestClient(app).get("/api/auto-trade/recent-events").json()["events"][0]
    assert calls == []
    assert ev["outcome"] == "rejected"
    assert ev["position_is_open"] is None


def test_recent_events_duplicate_signal_ids_looked_up_once(
    monkeypatch,
) -> None:
    """One signal can carry several dispatch events (retry, or a manual
    take after an auto reject). The join must de-duplicate — otherwise
    the read cost scales with retries, and both rows must still resolve
    to the SAME state."""
    from datetime import datetime, timezone, timedelta
    from src.execution import dispatch_log
    from src.execution import position_state as _ps

    now = datetime.now(timezone.utc)

    def _fake_list(firebase_uid: str, *, limit: int = 20):
        return [
            dispatch_log.DispatchEvent(
                event_id=f"evt-{i}", firebase_uid=firebase_uid,
                signal_id="sig-DUP", symbol="BTCUSDT", direction="LONG",
                outcome="placed", timestamp=now - timedelta(minutes=i),
                entry_price=29000.0, total_qty=0.017,
            ) for i in range(2)
        ]

    dispatch_log._db = MagicMock()
    monkeypatch.setattr(dispatch_log, "list_recent_events", _fake_list)

    calls = []

    def _spy(uid, sid):
        calls.append(sid)
        return _mk_position(sid, uid, _ps.PositionState.OPEN)

    monkeypatch.setattr(_ps, "get_position", _spy)
    app = _build_app(identity=_firebase_user(uid="fb-6"))
    body = TestClient(app).get("/api/auto-trade/recent-events").json()
    assert len(body["events"]) == 2
    assert calls == ["sig-DUP"], f"expected 1 lookup, got {calls}"
    assert all(e["position_is_open"] is True for e in body["events"])


def test_recent_events_never_streams_whole_position_history(
    monkeypatch,
) -> None:
    """Cost-discipline guard. ``list_positions_for_user`` streams the
    user's ENTIRE never-pruned history — one billed read per historical
    position on every tab visit. The join must fetch by explicit
    signal_id instead."""
    from src.execution import position_state as _ps
    _install_placed_event(monkeypatch)
    monkeypatch.setattr(
        _ps, "get_position",
        lambda uid, sid: _mk_position(sid, uid, _ps.PositionState.OPEN),
    )

    def _forbidden(*a, **k):
        raise AssertionError(
            "list_positions_for_user streams unbounded history; "
            "the join must fetch by signal_id"
        )

    monkeypatch.setattr(_ps, "list_positions_for_user", _forbidden)
    app = _build_app(identity=_firebase_user(uid="fb-7"))
    r = TestClient(app).get("/api/auto-trade/recent-events")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# resume-disabled-mine — self-serve breaker recovery (owner-approved
# 2026-07-18): the paused card's "Re-enable auto-trade" button
# ---------------------------------------------------------------------------


def _install_self_reenable_kill_switch(
    *, disabled: bool, last_self_reenable=None
):
    """Kill-switch double with a mutable disabled flag + cooldown stamp."""
    from src.execution import kill_switch

    state = {"disabled": disabled, "stamp": last_self_reenable}
    fake = MagicMock()
    fake.is_user_disabled = MagicMock(side_effect=lambda uid: state["disabled"])
    fake.enable_user = MagicMock(
        side_effect=lambda uid: state.__setitem__("disabled", False)
    )
    fake.last_self_reenable_at = MagicMock(side_effect=lambda uid: state["stamp"])
    fake.record_self_reenable = MagicMock(
        side_effect=lambda uid: state.__setitem__("stamp", "now")
    )
    kill_switch._client = fake
    return fake


def test_resume_disabled_mine_requires_firebase_identity() -> None:
    app = _build_app(identity=None)
    r = TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert r.status_code == 401


def test_resume_disabled_mine_503_when_kill_switch_uninitialised() -> None:
    app = _build_app(identity=_firebase_user(uid="fb-rdm-0"))
    r = TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert r.status_code == 503


def test_resume_disabled_mine_noop_when_not_disabled() -> None:
    fake = _install_self_reenable_kill_switch(disabled=False)
    app = _build_app(identity=_firebase_user(uid="fb-rdm-1"))
    body = TestClient(app).post("/api/auto-trade/resume-disabled-mine").json()
    assert body == {
        "ok": True, "auto_trade_disabled": False, "already_enabled": True,
    }
    fake.enable_user.assert_not_called()


def test_resume_disabled_mine_reenables_and_stamps_cooldown() -> None:
    fake = _install_self_reenable_kill_switch(disabled=True)
    app = _build_app(identity=_firebase_user(uid="fb-rdm-2"))
    r = TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["auto_trade_disabled"] is False
    assert body["already_enabled"] is False
    fake.enable_user.assert_called_once_with("fb-rdm-2")
    fake.record_self_reenable.assert_called_once_with("fb-rdm-2")


def test_resume_disabled_mine_rate_limited_inside_cooldown() -> None:
    from datetime import datetime, timedelta, timezone

    recent = datetime.now(timezone.utc) - timedelta(hours=1)
    fake = _install_self_reenable_kill_switch(
        disabled=True, last_self_reenable=recent
    )
    app = _build_app(identity=_firebase_user(uid="fb-rdm-3"))
    r = TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert r.status_code == 429
    assert "Try again in about" in r.json()["detail"]
    fake.enable_user.assert_not_called()


def test_resume_disabled_mine_allows_after_cooldown_expires() -> None:
    from datetime import datetime, timedelta, timezone

    stale = datetime.now(timezone.utc) - timedelta(hours=7)
    fake = _install_self_reenable_kill_switch(
        disabled=True, last_self_reenable=stale
    )
    app = _build_app(identity=_firebase_user(uid="fb-rdm-4"))
    r = TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert r.status_code == 200
    assert r.json()["auto_trade_disabled"] is False
    fake.enable_user.assert_called_once()


def test_resume_disabled_mine_malformed_stamp_fails_open() -> None:
    """A legacy/garbage cooldown stamp must not lock the user out."""
    fake = _install_self_reenable_kill_switch(
        disabled=True, last_self_reenable="not-a-datetime"
    )
    app = _build_app(identity=_firebase_user(uid="fb-rdm-5"))
    r = TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert r.status_code == 200
    assert r.json()["auto_trade_disabled"] is False
    fake.enable_user.assert_called_once()


def test_resume_disabled_mine_invalidates_runtime_cache() -> None:
    from src.api import auto_trade_status_routes as mod

    _install_self_reenable_kill_switch(disabled=True)
    mod._runtime_cache["fb-rdm-6"] = ({"armed": False}, 10.0**9)
    app = _build_app(identity=_firebase_user(uid="fb-rdm-6"))
    TestClient(app).post("/api/auto-trade/resume-disabled-mine")
    assert "fb-rdm-6" not in mod._runtime_cache
