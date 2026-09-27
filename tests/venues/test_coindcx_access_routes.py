"""Who may trade on CoinDCX, set from ops — no ``.env`` edit (owner, 2026-09-27).

Pinned:
* adding by PHONE resolves the Firebase uid the list stores;
* the list is edited against the store AT WRITE TIME (a second add keeps the
  first), and a list that could not be read is never overwritten;
* the switches reach the same live values the dispatch gate reads;
* a user with no Firebase sign-in yet is refused with a sentence, not stored
  as an empty uid.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from tests.venues.conftest import DCX


class _Snap:
    def __init__(self, d):
        self._d = d

    @property
    def exists(self):
        return self._d is not None

    def to_dict(self):
        return dict(self._d or {})


class _Doc:
    def __init__(self, db, path):
        self.db, self.path = db, path

    def get(self):
        if self.db.fail_reads:
            raise RuntimeError("firestore down")
        return _Snap(self.db.docs.get(self.path))

    def set(self, data, merge=False):
        cur = dict(self.db.docs.get(self.path) or {}) if merge else {}
        cur.update(data)
        self.db.docs[self.path] = cur


class _Coll:
    def __init__(self, db, name):
        self.db, self.name = db, name

    def document(self, name):
        return _Doc(self.db, (self.name, name))


class _DB:
    def __init__(self):
        self.docs: dict = {}
        self.fail_reads = False

    def collection(self, name):
        return _Coll(self, name)


_USERS = {
    "+919999999999": SimpleNamespace(firebase_uid="owner-uid", phone_e164="+919999999999",
                                     display_name="Owner"),
    "+918888888888": SimpleNamespace(firebase_uid="tester-uid", phone_e164="+918888888888",
                                     display_name="Tester"),
    "+917777777777": SimpleNamespace(firebase_uid=None, phone_e164="+917777777777",
                                     display_name="Legacy"),
}


class _Users:
    async def aget_by_phone(self, phone):
        return _USERS.get(phone)

    async def aget_by_firebase_uid(self, uid):
        return next((u for u in _USERS.values() if u.firebase_uid == uid), None)


@pytest.fixture()
def api(monkeypatch):
    from src import runtime_tunables as _rt
    from src.api import coindcx_routes
    from src.api import users as users_mod
    from src.venues.coindcx import keystore

    # The real store over a fake Firestore — so the gate reads what the
    # endpoint wrote, not a patched value.
    DCX.clear()
    _rt.reset_for_test()
    db = _DB()
    _rt.init_runtime_tunables(db)
    monkeypatch.setattr(_rt, "_bump", lambda: None)
    monkeypatch.setattr(users_mod, "get_singleton", lambda: _Users())
    monkeypatch.setattr(keystore, "get_status", lambda uid: None)
    app = FastAPI()
    coindcx_routes.register(app, auth=lambda: None, identity_dep=lambda: None,
                            owner_required=lambda: None, engine=None)
    yield TestClient(app), db
    _rt.reset_for_test()


def test_add_by_phone_stores_the_firebase_uid_and_the_gate_sees_it(api) -> None:
    from src.venues.coindcx import dispatch as dcx

    client, db = api
    r = client.post("/api/admin/coindcx/access", json={"action": "add", "phone": "+919999999999"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["changed_uid"] == "owner-uid"
    assert [row["uid"] for row in body["allowed"]] == ["owner-uid"]
    assert body["allowed"][0]["phone"] == "+919999999999"
    assert db.docs[("control", "runtime_tunables")]["coindcx_execution_allowed_uids"] == "owner-uid"
    assert dcx._allowed_uids() == {"owner-uid"}


def test_a_second_add_keeps_the_first_and_remove_takes_one(api) -> None:
    client, db = api
    client.post("/api/admin/coindcx/access", json={"action": "add", "phone": "+919999999999"})
    client.post("/api/admin/coindcx/access", json={"action": "add", "phone": "+918888888888"})
    assert db.docs[("control", "runtime_tunables")]["coindcx_execution_allowed_uids"] == \
        "owner-uid,tester-uid"
    r = client.post("/api/admin/coindcx/access",
                    json={"action": "remove", "firebase_uid": "owner-uid"})
    assert [row["uid"] for row in r.json()["allowed"]] == ["tester-uid"]


def test_an_unreadable_list_is_never_overwritten(api) -> None:
    client, db = api
    db.docs[("control", "runtime_tunables")] = {"coindcx_execution_allowed_uids": "owner-uid"}
    db.fail_reads = True
    r = client.post("/api/admin/coindcx/access", json={"action": "add", "phone": "+918888888888"})
    assert r.status_code == 503
    db.fail_reads = False
    assert db.docs[("control", "runtime_tunables")]["coindcx_execution_allowed_uids"] == "owner-uid"


def test_a_user_without_a_firebase_sign_in_is_refused_by_name(api) -> None:
    client, db = api
    r = client.post("/api/admin/coindcx/access", json={"action": "add", "phone": "+917777777777"})
    assert r.status_code == 409 and "sign in" in r.json()["detail"]
    assert ("control", "runtime_tunables") not in db.docs


def test_unknown_phone_is_a_404_not_an_empty_entry(api) -> None:
    client, _db = api
    r = client.post("/api/admin/coindcx/access", json={"action": "add", "phone": "+910000000000"})
    assert r.status_code == 404


def test_switches_reach_the_live_gate(api) -> None:
    from src.venues.coindcx import dispatch as dcx

    client, _db = api
    assert dcx.execution_enabled() is False
    r = client.post("/api/admin/coindcx/switch", json={"switch": "execution", "enabled": True})
    assert r.status_code == 200 and r.json()["execution_enabled"] is True
    assert dcx.execution_enabled() is True
    client.post("/api/admin/coindcx/switch", json={"switch": "open_to_all", "enabled": True})
    assert dcx._allowed_uids() is None
    r = client.post("/api/admin/coindcx/switch", json={"switch": "execution", "enabled": False})
    assert r.json()["execution_enabled"] is False


def test_access_view_says_unreadable_rather_than_empty(api) -> None:
    client, db = api
    db.fail_reads = True
    r = client.get("/api/admin/coindcx/access")
    assert r.status_code == 200 and r.json()["readable"] is False
    assert "allowed" not in r.json()
