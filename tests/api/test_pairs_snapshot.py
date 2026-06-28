"""Tests for the pairs X-ray builder (regular universe + promoting movers)."""
from __future__ import annotations

import time

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


class _Scalp:
    """Stand-in for ScalpChannel exposing per-symbol mover reasons."""

    def __init__(self, reasons):
        self._reasons = reasons

    def mover_last_reasons(self):
        return self._reasons


# collect_pairs_live picks the channel by class name.
_Scalp.__name__ = "ScalpChannel"


class _Engine:
    def __init__(self, pairs, promoted, mover_reasons=None):
        self.pair_mgr = _PairMgr(pairs)
        self._scanner = _Scanner(promoted)
        if mover_reasons is not None:
            self._channels = [_Scalp(mover_reasons)]


def _engine(mover_reasons=None):
    pairs = {
        "BTCUSDT": _Info(_Tier("TIER1"), 5_000_000_000.0, 1.2),
        "ARXUSDT": _Info(_Tier("TIER3"), 8_000_000.0, 22.0),
        "GLWUSDT": _Info(_Tier("TIER2"), 60_000_000.0, 5.0),
    }
    # Values are monotonic EXPIRY times: ARX has ~5h left, GLW ~2h.
    now = time.monotonic()
    promoted = {"ARXUSDT": now + 5 * 3600, "GLWUSDT": now + 2 * 3600}
    return _Engine(pairs, promoted, mover_reasons=mover_reasons)


def test_collect_regular_pairs_excludes_promoted():
    out = collect_pairs_live(_engine())
    # ARX/GLW are promoted → shown only under Promoting, not Regular. BTC stays.
    syms = [r["symbol"] for r in out["regular"]]
    assert syms == ["BTCUSDT"]
    assert out["regular_count"] == 1
    btc = out["regular"][0]
    assert btc["tier"] == "TIER1"
    assert btc["volume_24h_usd"] == 5_000_000_000.0
    assert btc["change_24h_pct"] == 1.2


def test_promoting_pairs_carry_minutes_left_and_enriched_volume():
    out = collect_pairs_live(_engine())
    assert out["promoting_count"] == 2
    # Sorted by minutes_left desc → ARXUSDT (~5h) before GLWUSDT (~2h).
    assert [p["symbol"] for p in out["promoting"]] == ["ARXUSDT", "GLWUSDT"]
    arx = out["promoting"][0]
    assert 295 <= arx["minutes_left"] <= 300       # ~5h, minus test runtime
    assert arx["change_24h_pct"] == 22.0          # enriched from pair_mgr directly
    assert arx["volume_24h_usd"] == 8_000_000.0
    assert "updated_at" in out
    # No ScalpChannel wired → reject fields present but null (graceful).
    assert arx["reject_reason"] is None


def test_promoting_pairs_carry_mover_reject_reason():
    eng = _engine(mover_reasons={
        "ARXUSDT": {"reason": "no_reclaim", "path": "MOVER_TREND_PULLBACK", "age_sec": 4.0},
        "GLWUSDT": {"reason": "fired", "path": "MOVER_AVWAP_SCALP", "age_sec": 1.0},
    })
    out = collect_pairs_live(eng)
    by = {p["symbol"]: p for p in out["promoting"]}
    assert by["ARXUSDT"]["reject_reason"] == "no_reclaim"
    assert by["ARXUSDT"]["reject_path"] == "MOVER_TREND_PULLBACK"
    assert by["GLWUSDT"]["reject_reason"] == "fired"


def test_ignition_health_block_surfaced():
    from src.mover_ignition import MoverIgnitionDetector

    det = MoverIgnitionDetector(
        enabled=True, window_sec=30.0, move_floor_pct=1.0, burst_mult=3.0,
        min_window_notional_usd=1000.0, cooldown_sec=60.0, baseline_alpha=0.02,
        min_baseline_samples=5, max_gap_sec=30.0,
    )
    det.ingest([{"s": "ABCUSDT", "c": 1.0, "n": 10, "q": 1000.0, "E": 1}])

    class _WS:
        is_healthy = True
        stream_count = 1

    eng = _engine()
    eng._mover_ignition = det
    eng._ws_futures_mover = _WS()
    out = collect_pairs_live(eng)
    ig = out["ignition"]
    assert ig["enabled"] is True
    assert ig["frames_ingested"] == 1
    assert ig["ignitions_total"] == 0          # one frame can't ignite (warmup)
    assert ig["ws_connected"] is True
    assert ig["ws_streams"] == 1


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
