"""CoinDCX venue core: signing, instrument parsing, symbol map, rounding,
stream frames, venue settings.

Public payloads are RECORDED from CoinDCX's live API (fixtures/coindcx), per
CLAUDE.md's rule that a fixture must come from the real producer.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from pathlib import Path

import pytest

from src.venues.coindcx import instruments as inst
from src.venues.coindcx import signing
from src.venues.coindcx import stream

FIX = Path(__file__).parent / "fixtures" / "coindcx"


def _load(name: str):
    return json.loads((FIX / name).read_text())


# ---------------------------------------------------------------- signing


def test_signature_covers_exact_body_text() -> None:
    text, headers = signing.signed_request("k", "s3cret", {"order": {"pair": "B-BTC_USDT"}}, now_ms=1700000000000)
    assert text == '{"order":{"pair":"B-BTC_USDT"},"timestamp":1700000000000}'
    expected = hmac.new(b"s3cret", text.encode(), hashlib.sha256).hexdigest()
    assert headers["X-AUTH-SIGNATURE"] == expected
    assert headers["X-AUTH-APIKEY"] == "k"


def test_caller_timestamp_is_overwritten_with_fresh_one() -> None:
    text = signing.canonical_body({"timestamp": 1}, now_ms=42)
    assert json.loads(text)["timestamp"] == 42


def test_stream_auth_is_hmac_of_constant_channel_body() -> None:
    expected = hmac.new(b"sec", b'{"channel":"coindcx"}', hashlib.sha256).hexdigest()
    assert signing.stream_auth_signature("sec") == expected


def test_allow_list_has_no_wallet_transfer_or_withdrawal() -> None:
    paths = set(signing.PRIVATE_ENDPOINTS)
    assert not any("transfer" in p or "withdraw" in p for p in paths)
    assert all(p.startswith("/exchange/v1/derivatives/futures/") for p in paths)
    assert signing.is_allowed("/exchange/v1/derivatives/futures/orders/create", "post")
    assert not signing.is_allowed("/exchange/v1/derivatives/futures/orders/create", "GET")
    assert not signing.is_allowed("/exchange/v1/derivatives/futures/wallets/transfer", "POST")


# ------------------------------------------------------------- instruments


def test_parse_recorded_btc_instrument() -> None:
    raw = _load("instrument_btc.json")["instrument"]
    i = inst.parse_instrument(raw, "BTCUSDT")
    assert i is not None and i.pair == "B-BTC_USDT"
    assert i.refusal() is None and i.tradable
    assert i.quantity_increment > 0 and i.price_increment > 0
    assert i.min_notional > 0 and i.max_leverage("LONG") >= 1


@pytest.mark.parametrize("patch,reason", [
    ({"status": "inactive"}, "instrument_inactive"),
    ({"exit_only": True}, "instrument_exit_only"),
    ({"unit_contract_value": 1000.0}, "contract_multiplier"),
    ({"is_quanto": True}, "instrument_not_linear"),
    ({"order_types": ["market_order", "limit_order"]}, "order_type_unsupported:stop_market"),
])
def test_instrument_refuses_shapes_our_orders_cannot_use(patch, reason) -> None:
    raw = dict(_load("instrument_btc.json")["instrument"], **patch)
    assert inst.parse_instrument(raw, "BTCUSDT").refusal() == reason


def test_symbol_map_uses_feed_twin_and_skips_rows_without_one() -> None:
    rows = _load("prices_rt_subset.json")["prices"]
    m = inst.build_symbol_map(rows)
    assert m["BTCUSDT"]["pair"] == "B-BTC_USDT"
    assert m["1000SHIBUSDT"]["pair"] == "B-1000SHIB_USDT"
    # rows the live feed publishes with no twin are never mapped
    for pair, row in rows.items():
        if not row.get("mkt"):
            assert all(v["pair"] != pair for v in m.values())


def test_symbol_claimed_by_two_pairs_is_dropped_not_guessed() -> None:
    rows = {"B-X_USDT": {"mkt": "XUSDT", "ls": 1}, "B-X2_USDT": {"mkt": "XUSDT", "ls": 2}}
    assert "XUSDT" not in inst.build_symbol_map(rows)


def test_inr_conversion_from_recorded_payload() -> None:
    assert inst.parse_inr_conversion(_load("conversions.json")) > 0
    assert inst.parse_inr_conversion({"bad": 1}) is None


def test_qty_rounds_down_never_up_and_formats_to_step() -> None:
    assert inst.round_qty_down(0.0019999, 0.001) == 0.001
    assert inst.round_qty_down(1.9, 1.0) == 1.0
    assert inst.format_number(0.30000000000000004, 0.1) == "0.3"
    assert inst.format_number(12.0, 1.0) == "12"
    assert inst.round_price(84351.06, 0.1) == pytest.approx(84351.1)


async def test_first_fetch_happens_even_on_a_freshly_booted_host(monkeypatch) -> None:
    """Regression (found by the live check): ``fetched_at = 0.0`` against
    ``time.monotonic()`` read as fresh on a host up for < TTL, so the first
    fetch never happened and BTC mapped to nothing."""
    monkeypatch.setattr(time, "monotonic", lambda: 5.0)  # "5s since boot"
    reg = inst.InstrumentRegistry()
    calls = []

    async def fake_get(url, params=None):
        calls.append(url)
        return _load("prices_rt_subset.json")

    reg._get_json = fake_get  # type: ignore[assignment]
    assert await reg.pair_for("BTCUSDT") == "B-BTC_USDT"
    assert calls, "the price feed must be fetched on first use"


async def test_fetch_failure_keeps_previous_cache_and_counts() -> None:
    reg = inst.InstrumentRegistry()

    async def ok(url, params=None):
        return _load("prices_rt_subset.json")

    reg._get_json = ok  # type: ignore[assignment]
    assert await reg.last_price("BTCUSDT")

    async def boom(url, params=None):
        raise RuntimeError("down")

    reg._get_json = boom  # type: ignore[assignment]
    assert await reg.pair_for("BTCUSDT") == "B-BTC_USDT"
    await reg.prices(max_age_s=-1)
    assert reg.stats["price_failures"] == 1
    assert await reg.pair_for("BTCUSDT") == "B-BTC_USDT"


# ------------------------------------------------------------------ stream


def test_parse_frame_live_price_and_documented_order_update() -> None:
    ex = _load("private_doc_examples.json")
    name, payload = stream.parse_frame(ex["stream_price_frame_live"])
    assert name == "price-change" and payload["data"]["p"] == "84351.1"
    name, payload = stream.parse_frame(ex["stream_order_update_frame"])
    assert name == "df-order-update"
    assert payload["data"][0]["stage"] == "tpsl_exit"


@pytest.mark.parametrize("frame", ["3", "40", "0{}", "42not json", "42{}"])
def test_parse_frame_ignores_non_events(frame) -> None:
    assert stream.parse_frame(frame) is None


# ---------------------------------------------------------- venue settings


@pytest.fixture()
def store(tmp_path):
    from src.api import user_overrides as uo

    st = uo.UserOverridesStore(tmp_path / "x.sqlite")
    st._conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY)")
    st._conn.execute("INSERT INTO users(user_id) VALUES (7)")
    return st


def test_venue_settings_round_trip_and_refuse_unknown_values(store) -> None:
    out = store.update_venue_settings(7, {"venue": "CoinDCX", "margin_currency": "inr", "leverage": 4})
    assert out["venue"] == "coindcx" and out["margin_currency"] == "INR" and out["leverage"] == 4.0
    for bad in ({"venue": "bybit"}, {"margin_currency": "EUR"}, {"leverage": 50}, {"leverage": 0.5}):
        with pytest.raises(ValueError):
            store.update_venue_settings(7, bad)
    assert store.get_venue_settings(7)["venue"] == "coindcx"


def test_every_unreadable_venue_resolves_to_binance(monkeypatch) -> None:
    from src.api import user_overrides as uo

    monkeypatch.setattr(uo, "_SINGLETON", None)
    r = uo.resolve_venue_settings_uid("u1")
    assert r["venue"] == "binance" and r["reason"] == uo.VENUE_REASON_STORE_COLD
    assert r["margin_currency"] == "INR"


def test_stored_choice_resolves(store, monkeypatch) -> None:
    from types import SimpleNamespace

    from src.api import user_overrides as uo
    from src.api import users as users_mod

    store.update_venue_settings(7, {"venue": "coindcx", "margin_currency": "USDT"})
    monkeypatch.setattr(uo, "_SINGLETON", store)
    fake_users = SimpleNamespace(get_by_firebase_uid=lambda uid: SimpleNamespace(user_id=7))
    monkeypatch.setattr(users_mod, "get_singleton", lambda: fake_users)
    r = uo.resolve_venue_settings_uid("fb7")
    assert (r["venue"], r["margin_currency"], r["reason"]) == ("coindcx", "USDT", "ok")
