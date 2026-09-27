"""Signing service — the CoinDCX branch.

Pins the three things that make custody of a CoinDCX key acceptable:

* the endpoint allow-list is enforced in THIS process (a wallet transfer is
  refused before the key is even read);
* a key without the owner-mandated attestation is refused before decryption;
* the signature covers exactly the body sent, and the secret never appears in
  any response field.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from src.security import envelope_crypto, kms_client
from src.security.signing_service import handler, protocol
from src.venues.coindcx import keystore as dcx_keys

SECRET = b"coindcx_secret_value_0123456789abcdef"


def _blob(attested: bool = True, api_key: str = "PUBKEY123456"):
    dek = envelope_crypto.generate_dek()
    enc = envelope_crypto.encrypt_secret(dek, SECRET)
    blob = dcx_keys.CoinDCXKeyBlob(
        uid="u1", encrypted_secret=enc.raw, encrypted_dek=b"wrapped",
        api_key_full=api_key, key_public_id_first8=api_key[:8],
        attestation={"ip_bound": attested, "no_withdraw": attested, "version": 1},
        connected_at=datetime.now(timezone.utc),
    )
    return blob, dek


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    kms_client.reset_for_test()
    dcx_keys.reset_for_test()
    yield
    kms_client.reset_for_test()
    dcx_keys.reset_for_test()


class _Resp:
    def __init__(self, status, body):
        self.status = status
        self._body = body

    async def json(self, content_type=None):
        return self._body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False


class _Session:
    def __init__(self, status=200, body=None):
        self.status, self.body = status, body if body is not None else [{"id": "o1"}]
        self.sent = []

    def request(self, method, url, data=None, headers=None):
        self.sent.append((method, url, data, headers))
        return _Resp(self.status, self.body)


def _wire(monkeypatch, blob, dek):
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms
    monkeypatch.setattr(dcx_keys, "get_key_blob_cached", lambda uid: blob)
    monkeypatch.setattr(dcx_keys, "get_key_blob", lambda uid: blob)


def _req(path="/exchange/v1/derivatives/futures/orders/create", verb="coindcx_signed_post", body=None):
    return protocol.SignRequest(id="r1", verb=verb, firebase_uid="u1", base="coindcx",
                                path=path, params=body or {"order": {"pair": "B-BTC_USDT"}})


async def test_happy_path_signs_exact_body_and_never_returns_secret(monkeypatch) -> None:
    blob, dek = _blob()
    _wire(monkeypatch, blob, dek)
    sess = _Session()
    resp = await handler.handle_request(_req(), session=sess)
    assert resp.ok and resp.binance_body == [{"id": "o1"}]
    method, url, data, headers = sess.sent[0]
    assert method == "POST" and url.endswith("/futures/orders/create")
    assert json.loads(data)["order"] == {"pair": "B-BTC_USDT"}
    assert headers["X-AUTH-SIGNATURE"] == hmac.new(SECRET, data.encode(), hashlib.sha256).hexdigest()
    assert SECRET.decode() not in json.dumps(resp.__dict__, default=str)


async def test_wallet_transfer_is_refused_before_the_key_is_read(monkeypatch) -> None:
    read = []
    monkeypatch.setattr(dcx_keys, "get_key_blob_cached", lambda uid: read.append(uid))
    resp = await handler.handle_request(
        _req(path="/exchange/v1/derivatives/futures/wallets/transfer"), session=_Session())
    assert resp.error_code == protocol.ERR_BAD_REQUEST and read == []


async def test_get_verb_cannot_reach_a_post_endpoint(monkeypatch) -> None:
    resp = await handler.handle_request(_req(verb="coindcx_signed_get"), session=_Session())
    assert resp.error_code == protocol.ERR_BAD_REQUEST


async def test_unattested_key_is_refused_before_decryption(monkeypatch) -> None:
    blob, dek = _blob(attested=False)
    _wire(monkeypatch, blob, dek)
    sess = _Session()
    resp = await handler.handle_request(_req(), session=sess)
    assert resp.error_code == protocol.ERR_KEY_NOT_ATTESTED
    assert kms_client._client.decrypt.call_count == 0 and sess.sent == []


async def test_stream_auth_returns_public_key_and_channel_signature(monkeypatch) -> None:
    blob, dek = _blob()
    _wire(monkeypatch, blob, dek)
    resp = await handler.handle_request(
        protocol.SignRequest(id="s", verb="coindcx_stream_auth", firebase_uid="u1", base="coindcx"))
    assert resp.ok
    assert resp.binance_body["api_key"] == "PUBKEY123456"
    assert resp.binance_body["auth_signature"] == hmac.new(
        SECRET, b'{"channel":"coindcx"}', hashlib.sha256).hexdigest()
    assert SECRET.decode() not in json.dumps(resp.binance_body)


async def test_http_error_is_typed_with_status_and_body(monkeypatch) -> None:
    blob, dek = _blob()
    _wire(monkeypatch, blob, dek)
    resp = await handler.handle_request(
        _req(), session=_Session(status=400, body={"message": "Insufficient funds"}))
    assert resp.error_code == protocol.ERR_BINANCE_HTTP_ERROR
    assert resp.binance_status == 400 and "Insufficient funds" in resp.error_message


async def test_rotated_key_rejected_401_is_retried_once_with_fresh_blob(monkeypatch) -> None:
    old, dek = _blob(api_key="OLDKEY000000")
    new, _ = _blob(api_key="NEWKEY000000")
    new = dcx_keys.CoinDCXKeyBlob(**{**new.__dict__, "encrypted_secret": old.encrypted_secret,
                                     "encrypted_dek": b"wrapped-new"})
    fake_kms = MagicMock()
    fake_kms.decrypt.return_value = dek
    kms_client._client = fake_kms
    monkeypatch.setattr(dcx_keys, "get_key_blob_cached", lambda uid: old)
    monkeypatch.setattr(dcx_keys, "get_key_blob", lambda uid: new)

    class _Rot(_Session):
        def request(self, method, url, data=None, headers=None):
            self.sent.append(headers["X-AUTH-APIKEY"])
            ok = headers["X-AUTH-APIKEY"] == "NEWKEY000000"
            return _Resp(200 if ok else 401, [{"id": "o"}] if ok else {"message": "Unauthorized"})

    sess = _Rot()
    resp = await handler.handle_request(_req(), session=sess)
    assert resp.ok and sess.sent == ["OLDKEY000000", "NEWKEY000000"]


async def test_binance_verbs_are_untouched_by_the_coindcx_branch() -> None:
    assert "binance_signed_post" not in handler._COINDCX_VERBS
    resp = await handler.handle_request(protocol.SignRequest(id="x", verb="ping"))
    assert resp.ok
