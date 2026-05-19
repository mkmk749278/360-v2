"""Tests for src.api.auto_trade_status_routes.

Same wiring pattern as test_binance_connect_routes (PR-2):
auth stub + identity stub + a FastAPI app that registers the route.
KillSwitchClient is mocked at the module boundary.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app(*, identity: object = None, allow_auth: bool = True) -> FastAPI:
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
        app, auth=_auth_stub, identity_dep=_identity_stub
    )
    return app


def _firebase_user(uid: str = "fb-uid-test") -> object:
    return SimpleNamespace(firebase_uid=uid, user_id=99)


@pytest.fixture(autouse=True)
def _reset_kill_switch():
    from src.execution import kill_switch
    kill_switch.reset_for_test()
    yield
    kill_switch.reset_for_test()


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


def test_runtime_status_armed_when_all_gates_green(monkeypatch) -> None:
    """All four gates green AND user_mode=='live' → armed=True.
    Models the "auto-trade is firing now" UX state."""
    from src.api import user_overrides as _uo
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

    # User mode = live via per-user override.
    fake_store = MagicMock()
    fake_store.get_operator_auto_trade.return_value = {"mode": "live"}
    monkeypatch.setattr(_uo, "_SINGLETON", fake_store, raising=False)

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

    fake_store = MagicMock()
    fake_store.get_operator_auto_trade.return_value = {"mode": "paper"}
    monkeypatch.setattr(_uo, "_SINGLETON", fake_store, raising=False)

    app = _build_app(identity=_firebase_user(uid="fb-paper"))
    client = TestClient(app)
    body = client.get("/api/auto-trade/runtime-status").json()
    assert body["armed"] is False
    assert body["user_mode"] == "paper"


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
