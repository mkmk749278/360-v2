"""CoinDCX key store + API routes.

* the roster: absent = nobody connected (``[]``), unreadable = ``None``;
* a connect stores the attestation WITH the key, and a roster failure
  removes the key again (never "connected" while invisible to dispatch);
* routes: every attestation box is required; CoinDCX can only be chosen with
  an attested key; a key cannot be removed while a CoinDCX position is live;
  status says ``readable: false`` rather than "not connected" on a failed read.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.venues.coindcx import keystore as K
from src.venues.coindcx import positions as P


# -------------------------------------------------------------- fake db


class _Snap:
    def __init__(self, data):
        self._d = data

    @property
    def exists(self):
        return self._d is not None

    def to_dict(self):
        return dict(self._d or {})


class _Doc:
    def __init__(self, db, path):
        self.db, self.path = db, path

    def collection(self, name):
        return _Coll(self.db, self.path + (name,))

    def get(self):
        if self.db.fail_reads:
            raise RuntimeError("firestore down")
        return _Snap(self.db.docs.get(self.path))

    def set(self, data, merge=False):
        if self.db.fail_roster and self.path[0] == "control":
            raise RuntimeError("roster write failed")
        cur = dict(self.db.docs.get(self.path) or {}) if merge else {}
        for k, v in data.items():
            name = type(v).__name__
            if name == "ArrayUnion":
                cur[k] = sorted(set(cur.get(k, [])) | set(v.values))
            elif name == "ArrayRemove":
                cur[k] = [x for x in cur.get(k, []) if x not in v.values]
            else:
                cur[k] = v
        self.db.docs[self.path] = cur

    def delete(self):
        self.db.docs.pop(self.path, None)


class _Coll:
    def __init__(self, db, path):
        self.db, self.path = db, path

    def document(self, name):
        return _Doc(self.db, self.path + (name,))


class FakeDB:
    def __init__(self):
        self.docs: Dict[tuple, Dict[str, Any]] = {}
        self.fail_reads = False
        self.fail_roster = False

    def collection(self, name):
        return _Coll(self, (name,))


@pytest.fixture()
def db(monkeypatch):
    fake = FakeDB()
    K.reset_for_test()
    K.set_db_for_test(fake)
    monkeypatch.setattr(K, "_bump", lambda doc: None)
    yield fake
    K.reset_for_test()


def _put(uid="u1"):
    K.put_key_blob(uid, encrypted_secret=b"c", encrypted_dek=b"d", api_key_full="PUBKEY12345",
                   attestation={"ip_bound": True, "no_withdraw": True, "version": 1})


def test_roster_absent_is_empty_and_unreadable_is_none(db) -> None:
    assert K.list_active_uids() == []
    K.invalidate_roster()
    db.fail_reads = True
    assert K.list_active_uids() is None


def test_connect_stores_attestation_with_key_and_lists_uid(db) -> None:
    _put()
    blob = K.get_key_blob("u1")
    assert blob.attested and blob.api_key_full == "PUBKEY12345"
    assert K.list_active_uids() == ["u1"]
    K.delete_key_blob("u1")
    K.invalidate_roster()
    assert K.list_active_uids() == []


def test_roster_failure_removes_the_key_again(db) -> None:
    db.fail_roster = True
    with pytest.raises(RuntimeError):
        _put()
    assert ("users", "u1", "coindcx_key", "current") not in db.docs


def test_attestation_requires_both_facts_and_a_version() -> None:
    b = K.CoinDCXKeyBlob(uid="u", encrypted_secret=b"", encrypted_dek=b"", api_key_full="k",
                         key_public_id_first8="k", attestation={"ip_bound": True, "version": 1})
    assert not b.attested


# ---------------------------------------------------------------- routes


def _app(identity):
    from src.api import coindcx_routes

    app = FastAPI()
    coindcx_routes.register(app, auth=lambda: None, identity_dep=lambda: identity,
                            owner_required=lambda: None, engine=None)
    return TestClient(app)


@pytest.fixture()
def pos_store():
    s = P.CoinDCXPositionStore(":memory:")
    P.set_store_for_test(s)
    yield s
    P.set_store_for_test(None)


_BODY = {"api_key": "PUBKEY12345", "api_secret": "SECRET123456",
         "attest_ip_bound": True, "attest_no_withdraw": True, "attest_trading_consent": True}


def test_connect_refuses_without_every_attestation(db, monkeypatch) -> None:
    monkeypatch.setenv("ENGINE_VPS_PUBLIC_IP", "203.0.113.9")
    c = _app(SimpleNamespace(firebase_uid="u1", user_id=1))
    r = c.post("/api/coindcx/connect", json={**_BODY, "attest_no_withdraw": False})
    assert r.status_code == 400
    assert r.headers["X-Connect-Error-Code"] == "ATTESTATION_REQUIRED"


def test_connect_validates_encrypts_and_stores(db, monkeypatch) -> None:
    from src.security import kms_client
    from src.venues.coindcx import connect_validator as cv

    monkeypatch.setenv("ENGINE_VPS_PUBLIC_IP", "203.0.113.9")
    kms = MagicMock()
    kms.encrypt.return_value = b"wrapped"
    kms_client._client = kms
    monkeypatch.setattr(cv, "validate_coindcx_key", AsyncMock(
        return_value=cv.CoinDCXValidation(futures_wallet_ok=True, balances={"USDT": 10.0})))
    try:
        r = _app(SimpleNamespace(firebase_uid="u1", user_id=1)).post("/api/coindcx/connect", json=_BODY)
    finally:
        kms_client.reset_for_test()
    assert r.status_code == 200 and r.json()["balances"] == {"USDT": 10.0}
    stored = db.docs[("users", "u1", "coindcx_key", "current")]
    assert stored["attestation"]["engine_ip"] == "203.0.113.9"
    assert "SECRET123456" not in str(stored)


def test_key_rejected_maps_to_400_with_code(db, monkeypatch) -> None:
    from src.security import kms_client
    from src.venues.coindcx import connect_validator as cv

    monkeypatch.setenv("ENGINE_VPS_PUBLIC_IP", "203.0.113.9")
    kms_client._client = MagicMock()
    monkeypatch.setattr(cv, "validate_coindcx_key", AsyncMock(side_effect=cv.KeyRejectedError("no")))
    try:
        r = _app(SimpleNamespace(firebase_uid="u1", user_id=1)).post("/api/coindcx/connect", json=_BODY)
    finally:
        kms_client.reset_for_test()
    assert r.status_code == 400 and r.headers["X-Connect-Error-Code"] == "KEY_REJECTED"


def test_status_says_unreadable_not_disconnected(db) -> None:
    db.fail_reads = True
    r = _app(SimpleNamespace(firebase_uid="u1", user_id=1)).get("/api/coindcx/connect/status")
    assert r.status_code == 200
    assert r.json()["readable"] is False and r.json()["connected"] is None


def test_choosing_coindcx_requires_an_attested_key(db, monkeypatch, tmp_path) -> None:
    from src.api import user_overrides as uo
    from src.api import users as users_mod

    st = uo.UserOverridesStore(tmp_path / "x.sqlite")
    st._conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY)")
    st._conn.execute("INSERT INTO users(user_id) VALUES (1)")
    monkeypatch.setattr(uo, "_SINGLETON", st)
    monkeypatch.setattr(users_mod, "get_singleton",
                        lambda: SimpleNamespace(get_by_firebase_uid=lambda u: SimpleNamespace(user_id=1)))
    import config
    c = _app(SimpleNamespace(firebase_uid="u1", user_id=1))
    assert c.put("/api/venue", json={"venue": "coindcx"}).status_code == 409
    _put()
    # key is fine, but CoinDCX execution is not open → still refused, so the
    # user is never taken off Binance onto an exchange that will not trade
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ENABLED", False)
    r = c.put("/api/venue", json={"venue": "coindcx"})
    assert r.status_code == 409 and r.headers["X-Venue-Error-Code"] == "COINDCX_NOT_OPEN"
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ENABLED", True)
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ALLOWED_UIDS", "someone-else")
    assert c.put("/api/venue", json={"venue": "coindcx"}).status_code == 409
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ALLOWED_UIDS", "u1")
    r = c.put("/api/venue", json={"venue": "coindcx", "margin_currency": "INR"})
    assert r.status_code == 200
    body = r.json()
    assert body["venue"] == "coindcx" and body["margin_currency"] == "INR"
    assert body["coindcx"]["attested"] is True
    assert c.put("/api/venue", json={"venue": "bybit"}).status_code == 400


def test_disconnect_refused_while_a_position_is_live(db, pos_store) -> None:
    _put()
    pos_store.put(P.CoinDCXPosition(uid="u1", signal_id="S", symbol="BTCUSDT", pair="B-BTC_USDT",
                                    side="LONG", state=P.OPEN, margin_currency="INR", leverage=5,
                                    qty=0.001, entry_target=1, sl_price=1, tp_price=2))
    c = _app(SimpleNamespace(firebase_uid="u1", user_id=1))
    assert c.delete("/api/coindcx/connect").status_code == 409
    closed = pos_store.get("u1", "S")
    closed.state = P.CLOSED
    pos_store.put(closed)
    assert c.delete("/api/coindcx/connect").status_code == 200


def test_positions_route_returns_only_the_callers(pos_store) -> None:
    for uid in ("u1", "u2"):
        pos_store.put(P.CoinDCXPosition(uid=uid, signal_id="S", symbol="BTCUSDT", pair="B-BTC_USDT",
                                        side="LONG", state=P.OPEN, margin_currency="INR", leverage=5,
                                        qty=0.001, entry_target=1, sl_price=1, tp_price=2,
                                        conversion_price=102.0, notional_usdt=10.0))
    r = _app(SimpleNamespace(firebase_uid="u1", user_id=1)).get("/api/coindcx/positions")
    rows = r.json()["positions"]
    assert r.json()["readable"] is True and [p["uid"] for p in rows] == ["u1"]
    assert rows[0]["venue"] == "coindcx" and rows[0]["notional_inr"] == 1020.0


def test_self_test_route_is_owner_gated_and_queues(monkeypatch) -> None:
    from fastapi import HTTPException

    from src.api import coindcx_routes

    def _deny():
        raise HTTPException(status_code=403)

    app = FastAPI()
    coindcx_routes.register(app, auth=lambda: None, identity_dep=lambda: None,
                            owner_required=_deny, engine=None)
    r = TestClient(app).post("/api/admin/coindcx/self-test", json={"uid": "owner-uid"})
    assert r.status_code == 403


# ------------------------------------------------- app contract vector
#
# `lumin-app/test/data/fixtures/coindcx_app_contract.json` is a byte-identical
# copy of the file below and the app parses it in its own CI.  This test
# pins that the file is what these routes REALLY return, so a renamed key
# fails here instead of silently emptying a field on the user's screen (the
# #817 class across a repo boundary).  Regenerate with
# `COINDCX_WRITE_APP_VECTOR=1 pytest tests/venues/test_coindcx_keystore_routes.py`
# and copy the file to the app.

_VECTOR = Path(__file__).parent / "fixtures" / "coindcx" / "app_contract.json"


def _live_responses(db, monkeypatch, tmp_path, pos_store) -> Dict[str, Any]:
    import config
    from src.api import user_overrides as uo
    from src.api import users as users_mod
    from src.venues.coindcx import instruments as I

    monkeypatch.setenv("ENGINE_VPS_PUBLIC_IP", "203.0.113.9")
    monkeypatch.setattr(I.get_registry(), "inr_per_usdt", AsyncMock(return_value=102.0))
    st = uo.UserOverridesStore(tmp_path / "x.sqlite")
    st._conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY)")
    st._conn.execute("INSERT INTO users(user_id) VALUES (1)")
    monkeypatch.setattr(uo, "_SINGLETON", st)
    monkeypatch.setattr(users_mod, "get_singleton",
                        lambda: SimpleNamespace(get_by_firebase_uid=lambda u: SimpleNamespace(user_id=1)))
    c = _app(SimpleNamespace(firebase_uid="u1", user_id=1))
    out: Dict[str, Any] = {"status_not_connected": c.get("/api/coindcx/connect/status").json()}
    _put()
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ENABLED", True)
    monkeypatch.setattr(config, "COINDCX_EXECUTION_ALLOWED_UIDS", "u1")
    out["info"] = c.get("/api/coindcx/info").json()
    out["venue_coindcx"] = c.put("/api/venue", json={"venue": "coindcx", "leverage": 3}).json()
    pos_store.put(P.CoinDCXPosition(
        uid="u1", signal_id="SIG-1", symbol="DOGEUSDT", pair="B-DOGE_USDT", side="LONG",
        state=P.CLOSED, margin_currency="INR", leverage=3, qty=100.0, entry_target=0.2,
        entry_filled=0.2001, sl_price=0.196, tp_price=0.205, conversion_price=102.0,
        notional_usdt=20.01, close_reason="TP1", exit_price=0.205,
        realized_pnl_usdt=0.49, fees_usdt=0.02))
    out["positions"] = c.get("/api/coindcx/positions").json()
    db.fail_reads = True
    K.invalidate_roster()
    out["status_unreadable"] = c.get("/api/coindcx/connect/status").json()
    return out


def _strip_volatile(o: Any) -> Any:
    """Timestamps differ per run; the contract is the keys and the types."""
    if isinstance(o, dict):
        return {k: ("<ts>" if k in ("connected_at", "last_validated_at", "created_at",
                                     "updated_at", "opened_at", "closed_at") and o[k] else
                    _strip_volatile(v)) for k, v in o.items()}
    if isinstance(o, list):
        return [_strip_volatile(v) for v in o]
    return o


def test_app_contract_vector_is_what_the_routes_return(db, monkeypatch, tmp_path, pos_store) -> None:
    import json
    import os

    live = _strip_volatile(_live_responses(db, monkeypatch, tmp_path, pos_store))
    text = json.dumps(live, indent=2, sort_keys=True) + "\n"
    if os.environ.get("COINDCX_WRITE_APP_VECTOR") == "1":
        _VECTOR.write_text(text)
    assert _VECTOR.read_text() == text, (
        "the CoinDCX routes no longer return the shape the app was built against — "
        "regenerate the vector and update lumin-app's copy + parser together")
