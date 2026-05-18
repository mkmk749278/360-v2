"""Tests for src.security.signing_service.protocol.

The wire format is the stability contract between the engine main
process and the signing service.  These tests pin:

* Round-trip: ``SignRequest`` → ``to_json_line`` → ``from_json_line``
  recovers identical fields.
* JSON line is terminated with ``\\n`` (the line-delimited framing
  contract — the server reads via ``readline``).
* Defaults: ``firebase_uid``, ``path``, ``params`` default to empty;
  ``base`` defaults to ``futures``; ``recv_window_ms`` defaults to
  5000.  Defaults matter because a future schema addition with
  defaults is backward-compatible; without defaults the contract
  breaks across deploys.
* Required fields rejected with a clear ValueError — server maps
  this to ``ERR_BAD_REQUEST``.
* Helper constructors (``ok_reply`` / ``error_reply``) produce
  well-formed responses.
"""
from __future__ import annotations

import json

import pytest

from src.security.signing_service import protocol


# ---------------------------------------------------------------------------
# SignRequest
# ---------------------------------------------------------------------------


def test_request_round_trip_preserves_all_fields() -> None:
    """Encode then decode — every field must come back identical.
    This is the wire-format stability contract."""
    original = protocol.SignRequest(
        id="req-abc",
        verb="binance_signed_post",
        firebase_uid="fb-uid-1",
        base="futures",
        path="/fapi/v1/order",
        params={"symbol": "BTCUSDT", "side": "BUY", "type": "MARKET"},
        recv_window_ms=10_000,
    )
    raw = original.to_json_line()
    assert raw.endswith(b"\n")  # line-delimited framing contract
    recovered = protocol.SignRequest.from_json_line(raw)
    assert recovered == original


def test_request_defaults_match_documented_values() -> None:
    """If we change a default here, every existing caller silently
    gets the new behavior.  Pin the documented defaults."""
    req = protocol.SignRequest(id="x", verb="ping")
    assert req.firebase_uid == ""
    assert req.base == "futures"
    assert req.path == ""
    assert req.params == {}
    assert req.recv_window_ms == 5000


def test_request_from_json_rejects_non_object() -> None:
    """Wire format is a JSON object — arrays / strings / numbers
    at top level are bad requests."""
    with pytest.raises(ValueError, match="must be a JSON object"):
        protocol.SignRequest.from_json_line(b"[]\n")


def test_request_from_json_rejects_missing_required_fields() -> None:
    """``id`` and ``verb`` are required; missing them indicates a
    programming bug, not user state.  Server maps to ERR_BAD_REQUEST."""
    with pytest.raises(ValueError, match="missing required"):
        protocol.SignRequest.from_json_line(b'{"verb": "ping"}\n')
    with pytest.raises(ValueError, match="missing required"):
        protocol.SignRequest.from_json_line(b'{"id": "x"}\n')


def test_request_json_is_single_line() -> None:
    """The framing contract demands one JSON object per line.  Verify
    the encoded form contains no embedded newlines (the JSON encoder
    is configured with no indent / no extra whitespace)."""
    req = protocol.SignRequest(
        id="x", verb="ping", params={"k": "v with spaces"}
    )
    raw = req.to_json_line()
    # Strip trailing terminator and verify no other newlines.
    body = raw.rstrip(b"\n")
    assert b"\n" not in body


# ---------------------------------------------------------------------------
# SignResponse
# ---------------------------------------------------------------------------


def test_response_round_trip_success_path() -> None:
    original = protocol.SignResponse(
        id="resp-id",
        ok=True,
        binance_status=200,
        binance_body={"balances": [{"asset": "USDT", "balance": "100.0"}]},
    )
    raw = original.to_json_line()
    assert raw.endswith(b"\n")
    recovered = protocol.SignResponse.from_json_line(raw)
    assert recovered == original


def test_response_round_trip_error_path() -> None:
    original = protocol.SignResponse(
        id="resp-err",
        ok=False,
        error_code=protocol.ERR_BINANCE_HTTP_ERROR,
        error_message="Binance returned 401",
        binance_status=401,
        binance_body={"code": -2014, "msg": "invalid IP"},
    )
    recovered = protocol.SignResponse.from_json_line(original.to_json_line())
    assert recovered == original


def test_ok_reply_helper_sets_ok_true() -> None:
    resp = protocol.SignResponse.ok_reply(
        "req-1", binance_status=200, binance_body={"ok": True}
    )
    assert resp.ok is True
    assert resp.id == "req-1"
    assert resp.binance_status == 200
    assert resp.error_code == ""


def test_error_reply_helper_sets_ok_false() -> None:
    resp = protocol.SignResponse.error_reply(
        "req-2",
        code=protocol.ERR_KEY_BLOB_NOT_FOUND,
        message="no key for uid=foo",
    )
    assert resp.ok is False
    assert resp.error_code == protocol.ERR_KEY_BLOB_NOT_FOUND
    assert resp.error_message == "no key for uid=foo"
    assert resp.binance_status == 0
    assert resp.binance_body is None


# ---------------------------------------------------------------------------
# Error code constants — pin the public contract
# ---------------------------------------------------------------------------


def test_error_codes_are_stable_strings() -> None:
    """The exact string values of the error codes are part of the
    caller contract — engine workers switch on these.  A typo would
    silently break the worker's error-handling branch.  Pin them."""
    assert protocol.ERR_KEY_BLOB_NOT_FOUND == "KEY_BLOB_NOT_FOUND"
    assert protocol.ERR_KMS_DECRYPT_FAILED == "KMS_DECRYPT_FAILED"
    assert protocol.ERR_CRYPTO_DECRYPT_FAILED == "CRYPTO_DECRYPT_FAILED"
    assert protocol.ERR_BINANCE_HTTP_ERROR == "BINANCE_HTTP_ERROR"
    assert protocol.ERR_BINANCE_UNREACHABLE == "BINANCE_UNREACHABLE"
    assert protocol.ERR_BAD_REQUEST == "BAD_REQUEST"
    assert protocol.ERR_INTERNAL_ERROR == "INTERNAL_ERROR"
