"""Unit tests for snapshot_store encode/decode round-trips."""
import pytest
from src.api.snapshot_store import encode, decode, KEY_SIGNALS_ALL, KEY_ENGINE_STATE


def test_encode_decode_roundtrip_dict():
    data = {"mode": "paper", "count": 5, "pnl": 12.34}
    assert decode(encode(data)) == data


def test_encode_decode_roundtrip_list():
    data = [{"signal_id": "abc", "symbol": "BTCUSDT"}, {"signal_id": "def"}]
    assert decode(encode(data)) == data


def test_encode_coerces_non_json_types():
    from datetime import datetime, timezone
    dt = datetime(2026, 6, 2, 12, 0, 0, tzinfo=timezone.utc)
    result = decode(encode({"ts": dt}))
    assert result is not None
    assert isinstance(result["ts"], str)


def test_decode_none_returns_none():
    assert decode(None) is None


def test_decode_corrupt_json_returns_none():
    assert decode("{not valid json}") is None


def test_decode_empty_string_returns_none():
    assert decode("") is None


def test_key_constants_are_unique():
    from src.api import snapshot_store as ss
    keys = [
        ss.KEY_SIGNALS_ALL,
        ss.KEY_ACTIVITY_ALL,
        ss.KEY_AGENTS_ALL,
        ss.KEY_TICKERS,
        ss.KEY_ENGINE_STATE,
        ss.KEY_CMD_SET_MODE,
    ]
    assert len(keys) == len(set(keys)), "duplicate Redis key constant"


def test_ttls_are_positive():
    from src.api import snapshot_store as ss
    for attr in ("TTL_SIGNALS", "TTL_ACTIVITY", "TTL_AGENTS", "TTL_TICKERS",
                 "TTL_ENGINE_STATE", "TTL_CMD"):
        assert getattr(ss, attr) > 0, f"{attr} must be positive"


def test_ttls_are_at_least_double_write_interval():
    from src.api import snapshot_store as ss
    from src.api.snapshot_writer import _CYCLE_INTERVAL_S, _ACTIVITY_INTERVAL_S, _AGENTS_INTERVAL_S
    assert ss.TTL_SIGNALS      >= _CYCLE_INTERVAL_S    * 2
    assert ss.TTL_TICKERS      >= _CYCLE_INTERVAL_S    * 2
    assert ss.TTL_ENGINE_STATE >= _CYCLE_INTERVAL_S    * 2
    assert ss.TTL_ACTIVITY     >= _ACTIVITY_INTERVAL_S * 2
    assert ss.TTL_AGENTS       >= _AGENTS_INTERVAL_S   * 2
