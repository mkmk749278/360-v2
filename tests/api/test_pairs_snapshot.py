"""Tests for the pairs X-ray builder (regular universe + promoting movers)."""
from __future__ import annotations

from src.api.snapshot import build_pairs, collect_pairs_live


class _Info:
    def __init__(self, tier, vol, change):
        self.tier = tier
        self.volume_24h_usd = vol
        self.volatility_24h = change


class _Tier:
    def __init__(self, value):
        self.value = value


class _PairMgr:
    def __init__(self, pairs):
        self.pairs = pairs


class _Scanner:
    def __init__(self, promoted):
        self._mover_promoted_pairs = promoted


class _Engine:
    def __init__(self, pairs, promoted):
        self.pair_mgr = _PairMgr(pairs)
        self._scanner = _Scanner(promoted)


def _engine():
    pairs = {
        "BTCUSDT": _Info(_Tier("TIER1"), 5_000_000_000.0, 1.2),
        "ARXUSDT": _Info(_Tier("TIER3"), 8_000_000.0, 22.0),
        "GLWUSDT": _Info(_Tier("TIER2"), 60_000_000.0, 5.0),
    }
    promoted = {"ARXUSDT": 5, "GLWUSDT": 2}
    return _Engine(pairs, promoted)


def test_collect_regular_pairs_sorted_with_tier_and_volume():
    out = collect_pairs_live(_engine())
    assert out["regular_count"] == 3
    syms = [r["symbol"] for r in out["regular"]]
    # TIER1 first (sort by tier string), then TIER2, then TIER3.
    assert syms[0] == "BTCUSDT"
    btc = out["regular"][0]
    assert btc["tier"] == "TIER1"
    assert btc["volume_24h_usd"] == 5_000_000_000.0
    assert btc["change_24h_pct"] == 1.2


def test_promoting_pairs_carry_cycles_and_enriched_volume():
    out = collect_pairs_live(_engine())
    assert out["promoting_count"] == 2
    # Sorted by cycles_left desc → ARXUSDT (5) before GLWUSDT (2).
    assert [p["symbol"] for p in out["promoting"]] == ["ARXUSDT", "GLWUSDT"]
    arx = out["promoting"][0]
    assert arx["cycles_left"] == 5
    assert arx["change_24h_pct"] == 22.0          # enriched from the regular row
    assert arx["volume_24h_usd"] == 8_000_000.0
    assert "updated_at" in out


def test_empty_engine_is_safe():
    class _Empty:
        pair_mgr = None
        _scanner = None
    out = collect_pairs_live(_Empty())
    assert out["regular"] == [] and out["promoting"] == []
    assert out["regular_count"] == 0 and out["promoting_count"] == 0


def test_build_pairs_prefers_facade_published_payload():
    # Isolated mode: facade exposes published_pairs() replayed from engine_state.
    published = {"regular": [], "promoting": [{"symbol": "XUSDT", "cycles_left": 3}],
                 "regular_count": 0, "promoting_count": 1, "updated_at": "t"}

    class _Facade:
        def published_pairs(self):
            return published

    out = build_pairs(_Facade())
    assert out is published
    assert out["promoting"][0]["symbol"] == "XUSDT"


def test_build_pairs_falls_back_to_live_when_facade_empty():
    class _Facade:
        pair_mgr = None
        _scanner = None
        def published_pairs(self):
            return None

    out = build_pairs(_Facade())
    assert out["regular_count"] == 0  # live build on the (empty) facade engine
