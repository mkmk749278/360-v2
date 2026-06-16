"""Tests for the generation-gated OPEN-positions cache in
``pretp_dispatcher`` (Firestore-read cost fix).

The pre-TP dispatcher used to run a Firestore collection-group query on
every mark-price tick (~1/sec/symbol, 24/7), which made Firestore reads
the dominant cloud cost.  The cache removes Firestore from the hot path
while preserving real-money correctness: it re-queries whenever the
position-write generation moves, so ``should_fire_pretp`` never sees a
stale ``state`` / ``pretp_fired`` / ``pretp_order_id``.
"""
from __future__ import annotations

import pytest

from src.execution import position_state as _ps
from src.execution import pretp_dispatcher as _pd


@pytest.fixture(autouse=True)
def _clean_state():
    _ps.reset_for_test()
    _pd.reset_positions_cache_for_test()
    yield
    _ps.reset_for_test()
    _pd.reset_positions_cache_for_test()


@pytest.fixture
def _counting_query(monkeypatch):
    """Replace the raw Firestore query with a call-counting stub.

    Returns a dict mapping each symbol to the number of underlying
    queries actually issued, so tests can assert cache hits avoid them.
    """
    calls: dict[str, int] = {}

    def _fake(symbol: str):
        calls[symbol] = calls.get(symbol, 0) + 1
        return []  # position payload is irrelevant to cache behaviour

    monkeypatch.setattr(_pd, "_query_open_positions", _fake)
    return calls


def test_second_call_same_generation_is_cached(_counting_query, monkeypatch):
    monkeypatch.setattr(_ps, "get_write_generation", lambda: 7)
    _pd._default_positions_for_symbol("BTCUSDT")
    _pd._default_positions_for_symbol("BTCUSDT")
    _pd._default_positions_for_symbol("BTCUSDT")
    # Only the first (cold) call hits Firestore.
    assert _counting_query["BTCUSDT"] == 1


def test_generation_bump_forces_requery(_counting_query, monkeypatch):
    gen = {"v": 1}
    monkeypatch.setattr(_ps, "get_write_generation", lambda: gen["v"])
    _pd._default_positions_for_symbol("ETHUSDT")
    _pd._default_positions_for_symbol("ETHUSDT")
    assert _counting_query["ETHUSDT"] == 1
    # A position write moved the generation → next tick must re-query so a
    # freshly-OPEN / freshly-fired position is reflected immediately.
    gen["v"] = 2
    _pd._default_positions_for_symbol("ETHUSDT")
    assert _counting_query["ETHUSDT"] == 2


def test_ttl_expiry_forces_requery(_counting_query, monkeypatch):
    monkeypatch.setattr(_ps, "get_write_generation", lambda: 1)
    clock = {"t": 1000.0}
    monkeypatch.setattr(_pd, "_clock", lambda: clock["t"])
    _pd._default_positions_for_symbol("SOLUSDT")
    # Within the TTL window → cached even though generation is unchanged.
    clock["t"] += _pd._QUERY_CACHE_MAX_TTL_S / 2
    _pd._default_positions_for_symbol("SOLUSDT")
    assert _counting_query["SOLUSDT"] == 1
    # Past the defensive TTL bound → re-query.
    clock["t"] += _pd._QUERY_CACHE_MAX_TTL_S + 1.0
    _pd._default_positions_for_symbol("SOLUSDT")
    assert _counting_query["SOLUSDT"] == 2


def test_symbols_cache_independently(_counting_query, monkeypatch):
    monkeypatch.setattr(_ps, "get_write_generation", lambda: 3)
    _pd._default_positions_for_symbol("BTCUSDT")
    _pd._default_positions_for_symbol("ETHUSDT")
    _pd._default_positions_for_symbol("BTCUSDT")
    assert _counting_query["BTCUSDT"] == 1
    assert _counting_query["ETHUSDT"] == 1


def test_write_generation_increments_on_put_and_delete(monkeypatch):
    """The cache's correctness rests on put/delete bumping the counter."""
    captured = {}

    class _FakeDoc:
        def set(self, *a, **k):
            captured["set"] = True

        def delete(self, *a, **k):
            captured["delete"] = True

    monkeypatch.setattr(_ps, "_doc_ref", lambda *a, **k: _FakeDoc())

    start = _ps.get_write_generation()
    pos = _make_open_position()
    _ps.put_position(pos)
    assert _ps.get_write_generation() == start + 1
    _ps.delete_position(pos.firebase_uid, pos.signal_id)
    assert _ps.get_write_generation() == start + 2


def _make_open_position() -> _ps.Position:
    return _ps.Position(
        signal_id="sig-1",
        firebase_uid="uid-1",
        symbol="BTCUSDT",
        side="LONG",
        state=_ps.PositionState.OPEN,
        entry_price_target=100.0,
        entry_price_filled=100.0,
        sl_price=95.0,
        tp1_price=101.0,
        tp2_price=102.0,
        tp3_price=103.0,
        total_qty=1.0,
        tp1_qty=0.3,
        tp2_qty=0.3,
        tp3_qty=0.4,
    )
