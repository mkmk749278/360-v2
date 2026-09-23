"""Binance IP request-weight census (2026-09-23).

One whitelisted IP, 2,400 weight/min on USDⓈ-M futures, and the 2026-09-01
outage was that budget spent on per-user GETs. These tests pin the three
properties a reader of ``read.ip_weight`` relies on:

* the header crosses the signing-service wire intact and tri-state —
  ``None`` is "not reported", never zero usage;
* the census attributes it to the channel it arrived on and bounds
  "recent" by the wall clock, not by whichever buckets happen to exist;
* the probe pages on a real peak or a throttle, and clears on its own.
"""
from __future__ import annotations

import pytest

from src import ip_weight_census as ipw
from src.security.signing_service import client as sclient
from src.security.signing_service.protocol import SignRequest, SignResponse

T0 = 1_790_000_000.0  # fixed epoch, minute-aligned enough for arithmetic below


@pytest.fixture(autouse=True)
def _clean():
    ipw._reset_for_tests()
    yield
    ipw._reset_for_tests()


# --- wire protocol -----------------------------------------------------------


def test_used_weight_round_trips_the_wire():
    resp = SignResponse.ok_reply("r1", binance_status=200, binance_body={}, used_weight_1m=412)
    back = SignResponse.from_json_line(resp.to_json_line())
    assert back.used_weight_1m == 412


def test_zero_weight_stays_zero_and_absent_stays_none():
    zero = SignResponse.ok_reply("r1", binance_status=200, binance_body={}, used_weight_1m=0)
    assert SignResponse.from_json_line(zero.to_json_line()).used_weight_1m == 0
    # A reply from a signing service that predates the field.
    legacy = b'{"id":"r1","ok":true,"binance_status":200,"binance_body":{}}\n'
    assert SignResponse.from_json_line(legacy).used_weight_1m is None


def test_error_reply_carries_the_weight():
    err = SignResponse.error_reply("r1", code="BINANCE_HTTP_ERROR", message="x",
                                   binance_status=418, used_weight_1m=2400)
    back = SignResponse.from_json_line(err.to_json_line())
    assert back.used_weight_1m == 2400 and back.binance_status == 418


# --- the real client records into the census ----------------------------------


async def test_signing_client_records_every_signed_response(monkeypatch):
    """Drive the real SigningClient; only the socket conversation is stubbed."""

    async def _fake_send(self, request: SignRequest) -> SignResponse:
        return SignResponse.ok_reply(request.id, binance_status=200,
                                     binance_body=[], used_weight_1m=321)

    class _Conn:
        def __init__(self, path):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return None

        send_and_receive = _fake_send

    monkeypatch.setattr(sclient, "_SignClientConn", _Conn)
    c = sclient.SigningClient(socket_path="/nonexistent")
    await c.binance_signed_get(firebase_uid="u1", path="/fapi/v2/positionRisk")
    await c.binance_signed_get(firebase_uid="u2", path="/fapi/v2/positionRisk")
    await c.ping()  # a ping never reaches Binance and must not count

    snap = ipw.snapshot()
    assert snap["signed_calls_since_boot"] == {"/fapi/v2/positionRisk": 2}
    assert snap["distinct_uids_signed_this_hour"] == 2
    assert snap["last"]["signed"]["value"] == 321
    assert snap["peak_since_boot"] == 321
    assert snap["peak_since_boot_source"] == "signed"


# --- census semantics -----------------------------------------------------------


def test_missing_header_is_counted_apart_and_never_lowers_a_peak():
    ipw.record_signed(path="/fapi/v1/order", firebase_uid="u", base="futures",
                      used_weight_1m=900, now=T0)
    ipw.record_signed(path="/fapi/v1/order", firebase_uid="u", base="futures",
                      used_weight_1m=None, now=T0 + 1)
    snap = ipw.snapshot(now=T0 + 2)
    assert snap["signed_calls_without_header"] == 1
    assert snap["peak_last_5m"] == 900


def test_spot_calls_do_not_count_against_the_futures_budget():
    ipw.record_signed(path="/api/v3/account", firebase_uid="u", base="spot",
                      used_weight_1m=5000, now=T0)
    snap = ipw.snapshot(now=T0)
    assert snap["peak_since_boot"] is None
    assert snap["signed_calls_since_boot"] == {}


def test_public_and_signed_are_split_per_minute():
    ipw.record_public("700", now=T0)
    ipw.record_signed(path="/fapi/v2/positionRisk", firebase_uid="u", base="futures",
                      used_weight_1m=650, now=T0 + 1)
    row = ipw.snapshot(now=T0 + 2)["minutes"][-1]
    assert (row["public"], row["signed"], row["peak"]) == (700, 650, 700)


def test_recent_window_is_wall_clock_not_last_buckets():
    """After an idle hour, the newest bucket is old and must not read as recent."""
    ipw.record_public("2300", now=T0)
    snap = ipw.snapshot(now=T0 + 30 * 60)
    assert snap["peak_last_5m"] is None
    assert snap["peak_last_1h"] == 2300


def test_unparseable_header_is_ignored():
    ipw.record_public("not-a-number", now=T0)
    ipw.record_public(None, now=T0)
    assert ipw.snapshot(now=T0)["peak_since_boot"] is None


# --- probe --------------------------------------------------------------------


def test_probe_passes_with_no_reading():
    ok, detail = ipw.budget_health(now=T0)
    assert ok and "no futures weight reading" in detail


def test_probe_trips_above_eighty_percent():
    ipw.record_public("1900", now=T0)
    assert ipw.budget_health(now=T0)[0] is True
    ipw.record_public("1950", now=T0 + 1)
    ok, detail = ipw.budget_health(now=T0 + 2)
    assert not ok and "1950/2400" in detail


def test_throttle_pages_then_clears_after_an_hour():
    ipw.record_signed(path="/fapi/v2/positionRisk", firebase_uid="u", base="futures",
                      used_weight_1m=None, binance_status=418, now=T0)
    assert ipw.budget_health(now=T0 + 60)[0] is False
    # A since-boot latch would stay red until a restart; this must clear.
    assert ipw.budget_health(now=T0 + 3601)[0] is True
    assert ipw.snapshot(now=T0 + 3601)["throttled_responses"] == {418: 1}


# --- diagnostic catalog --------------------------------------------------------


def test_catalog_exposes_the_census():
    from src import diag_catalog

    entry = diag_catalog._REGISTRY["read.ip_weight"]
    ipw.record_public("42")
    out = entry.fn(None)
    assert out["peak_since_boot"] == 42 and out["limit_1m"] == 2400
