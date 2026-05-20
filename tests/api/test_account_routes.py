"""Tests for src.api.account_routes — Play Store in-app account deletion.

What we pin:

* 401 when no firebase_uid resolves from the identity (anonymous /
  malformed token).
* Happy path: Firestore blob deleted → user row deleted → cache reset
  → 204.
* Idempotent: deletion of an already-deleted user (no row in SQLite)
  still returns 204 (don't 404 a retry).
* Step-1 failure (Firestore blob delete raises) → 503 with
  ``key_blob_delete_failed`` tag; the user row is NOT deleted (we
  abort to avoid orphaned user row pointing at orphan blob).
* Step-2 failure (user row delete raises) → 503 with
  ``user_row_delete_failed`` tag.
* Step-3 failure (cache reset raises) does NOT fail the response —
  cache TTL expires naturally; this MUST be silent or production
  bugs in cache code would block legitimate deletions.
* Firestore-not-initialised path is OK (test/cold-deploy state) —
  skip step 1 + continue to step 2.

The Firestore keystore + UserStore + signal_dispatch are all mocked
at the module boundary, mirroring the test pattern in
``test_binance_connect_routes.py``.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _build_app(*, identity: object = None, allow_auth: bool = True) -> FastAPI:
    from src.api import account_routes

    app = FastAPI()

    def _auth_stub() -> None:
        if not allow_auth:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="missing token")
        return None

    def _identity_stub() -> object:
        return identity

    account_routes.register(
        app, auth=_auth_stub, identity_dep=_identity_stub
    )
    return app


def _firebase_user(uid: str = "fb-uid-test", user_id: int = 99) -> object:
    return SimpleNamespace(firebase_uid=uid, user_id=user_id)


# ---------------------------------------------------------------------------
# Auth + identity gating
# ---------------------------------------------------------------------------


def test_delete_returns_401_when_no_firebase_uid() -> None:
    """Anonymous device JWT (no firebase_uid attr) → 401."""
    app = _build_app(identity=SimpleNamespace())  # no firebase_uid attr
    client = TestClient(app)
    resp = client.delete("/api/account")
    assert resp.status_code == 401
    assert "Firebase sign-in" in resp.json()["detail"]


def test_delete_returns_401_when_identity_none() -> None:
    """``identity is None`` → 401."""
    app = _build_app(identity=None)
    client = TestClient(app)
    resp = client.delete("/api/account")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


@patch("src.execution.signal_dispatch.reset_cache_for_test")
@patch("src.api.users.get_singleton")
@patch("src.security.firestore_keystore.delete_key_blob")
@patch("src.security.firestore_keystore.is_initialised", return_value=True)
def test_delete_happy_path_returns_204(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
    mock_reset_cache: MagicMock,
) -> None:
    """All three steps succeed → 204; each underlying call fired once."""
    user_store = MagicMock()
    user_store.get_by_firebase_uid.return_value = SimpleNamespace(user_id=99)
    user_store.delete_by_id.return_value = True
    mock_get_user_store.return_value = user_store

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 204
    mock_delete_blob.assert_called_once_with("fb-uid-test")
    user_store.delete_by_id.assert_called_once_with(99)
    mock_reset_cache.assert_called_once()


# ---------------------------------------------------------------------------
# Idempotency — already-deleted user
# ---------------------------------------------------------------------------


@patch("src.execution.signal_dispatch.reset_cache_for_test")
@patch("src.api.users.get_singleton")
@patch("src.security.firestore_keystore.delete_key_blob")
@patch("src.security.firestore_keystore.is_initialised", return_value=True)
def test_delete_returns_204_when_user_already_deleted(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
    mock_reset_cache: MagicMock,
) -> None:
    """No SQLite row for the firebase_uid → treat as already-deleted,
    still return 204.  Retrying a successful delete must not 404."""
    user_store = MagicMock()
    user_store.get_by_firebase_uid.return_value = None  # no row
    mock_get_user_store.return_value = user_store

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 204
    mock_delete_blob.assert_called_once()
    user_store.delete_by_id.assert_not_called()  # no row to delete


# ---------------------------------------------------------------------------
# Step 1 failure — Firestore blob delete
# ---------------------------------------------------------------------------


@patch("src.execution.signal_dispatch.reset_cache_for_test")
@patch("src.api.users.get_singleton")
@patch("src.security.firestore_keystore.delete_key_blob",
       side_effect=RuntimeError("firestore down"))
@patch("src.security.firestore_keystore.is_initialised", return_value=True)
def test_delete_503_when_firestore_blob_delete_fails(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
    mock_reset_cache: MagicMock,
) -> None:
    """Step 1 failure → 503 with key_blob_delete_failed tag.  User row
    is NOT deleted (we abort to avoid orphaned user row → orphan blob)."""
    user_store = MagicMock()
    mock_get_user_store.return_value = user_store

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 503
    assert resp.json()["detail"] == "key_blob_delete_failed"
    user_store.delete_by_id.assert_not_called()
    mock_reset_cache.assert_not_called()


# ---------------------------------------------------------------------------
# Step 2 failure — user row delete
# ---------------------------------------------------------------------------


@patch("src.execution.signal_dispatch.reset_cache_for_test")
@patch("src.api.users.get_singleton")
@patch("src.security.firestore_keystore.delete_key_blob")
@patch("src.security.firestore_keystore.is_initialised", return_value=True)
def test_delete_503_when_user_row_delete_fails(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
    mock_reset_cache: MagicMock,
) -> None:
    """Step 2 failure → 503 with user_row_delete_failed tag.  Blob
    has already been deleted (step 1 succeeded) — orphan blob state
    is acceptable, the operator-side log surfaces it."""
    user_store = MagicMock()
    user_store.get_by_firebase_uid.return_value = SimpleNamespace(user_id=99)
    user_store.delete_by_id.side_effect = RuntimeError("sqlite locked")
    mock_get_user_store.return_value = user_store

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 503
    assert resp.json()["detail"] == "user_row_delete_failed"
    mock_delete_blob.assert_called_once()
    mock_reset_cache.assert_not_called()


# ---------------------------------------------------------------------------
# Step 3 failure — cache reset is best-effort
# ---------------------------------------------------------------------------


@patch("src.execution.signal_dispatch.reset_cache_for_test",
       side_effect=RuntimeError("cache module broken"))
@patch("src.api.users.get_singleton")
@patch("src.security.firestore_keystore.delete_key_blob")
@patch("src.security.firestore_keystore.is_initialised", return_value=True)
def test_delete_returns_204_even_when_cache_reset_fails(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
    mock_reset_cache: MagicMock,
) -> None:
    """Cache reset raising MUST NOT fail the response.  The cache TTL
    expires naturally within 30s; the user's deletion has already
    succeeded at the data layer."""
    user_store = MagicMock()
    user_store.get_by_firebase_uid.return_value = SimpleNamespace(user_id=99)
    mock_get_user_store.return_value = user_store

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 204


# ---------------------------------------------------------------------------
# Firestore-not-initialised path
# ---------------------------------------------------------------------------


@patch("src.execution.signal_dispatch.reset_cache_for_test")
@patch("src.api.users.get_singleton")
@patch("src.security.firestore_keystore.delete_key_blob")
@patch("src.security.firestore_keystore.is_initialised", return_value=False)
def test_delete_skips_blob_when_firestore_not_initialised(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
    mock_reset_cache: MagicMock,
) -> None:
    """Test paths + cold-deploy state where Firestore isn't wired —
    skip step 1, proceed to step 2.  Important so the endpoint
    remains callable in environments without Firestore (the
    in-process test harness)."""
    user_store = MagicMock()
    user_store.get_by_firebase_uid.return_value = SimpleNamespace(user_id=99)
    mock_get_user_store.return_value = user_store

    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 204
    mock_delete_blob.assert_not_called()
    user_store.delete_by_id.assert_called_once()


# ---------------------------------------------------------------------------
# UserStore singleton not registered (server misconfiguration)
# ---------------------------------------------------------------------------


@patch("src.api.users.get_singleton", return_value=None)
@patch("src.security.firestore_keystore.delete_key_blob")
@patch("src.security.firestore_keystore.is_initialised", return_value=True)
def test_delete_500_when_user_store_singleton_unset(
    mock_init: MagicMock,
    mock_delete_blob: MagicMock,
    mock_get_user_store: MagicMock,
) -> None:
    """UserStore singleton not registered = server misconfiguration.
    500 with server_misconfiguration_user_store tag — distinguishes
    from the 503 "transient failure" tags so the operator alerting
    can tell them apart."""
    app = _build_app(identity=_firebase_user())
    client = TestClient(app)
    resp = client.delete("/api/account")

    assert resp.status_code == 500
    assert resp.json()["detail"] == "server_misconfiguration_user_store"
