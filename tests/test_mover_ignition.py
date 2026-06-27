"""Tests for the real-time mover-ignition detector (`src/mover_ignition.py`).

The detector folds successive `!ticker@arr` frames and returns pairs that are
igniting *now* — a short-window price move + a sustained trade-rate burst vs the
pair's own EWMA baseline + a min traded notional. These tests drive it with
synthetic frames (no network) and assert the fire / no-fire boundaries.
"""
from __future__ import annotations

from typing import List, Tuple

from src.mover_ignition import LONG, SHORT, MoverIgnitionDetector


def _make_detector(**overrides) -> MoverIgnitionDetector:
    """Detector with small, test-friendly thresholds; override per case."""
    params = dict(
        enabled=True,
        window_sec=10.0,
        move_floor_pct=1.0,
        burst_mult=3.0,
        min_window_notional_usd=1_000.0,
        cooldown_sec=60.0,
        baseline_alpha=0.1,
        min_baseline_samples=5,
        max_gap_sec=30.0,
    )
    params.update(overrides)
    return MoverIgnitionDetector(**params)


def _frame(symbol: str, *, price: float, trades: int, quote: float, evt_ms: int) -> List[dict]:
    """One `!ticker@arr` array carrying a single symbol's ticker."""
    return [{"s": symbol, "c": price, "n": trades, "q": quote, "E": evt_ms}]


def _warm_then_burst(
    det: MoverIgnitionDetector,
    symbol: str = "ABCUSDT",
    *,
    warm_frames: int = 8,
    base_rate: int = 10,
    base_notional: float = 5_000.0,
    burst_frames: int = 5,
    burst_rate: int = 100,
    burst_notional: float = 20_000.0,
    price_step_pct: float = 0.6,
    now: float = 1000.0,
) -> List[Tuple[str, str]]:
    """Feed a steady baseline then a sustained burst; return all ignitions seen.

    Frames are 1 s apart. During warmup price is flat; during the burst price
    steps up ``price_step_pct`` % per frame so the windowed move clears the floor.
    """
    price = 100.0
    trades = 1_000
    quote = 1_000_000.0
    evt = 1_700_000_000_000
    ignitions: List[Tuple[str, str]] = []

    for _ in range(warm_frames):
        det.ingest(_frame(symbol, price=price, trades=trades, quote=quote, evt_ms=evt), now=now)
        trades += base_rate
        quote += base_notional
        evt += 1_000
        now += 1.0

    for _ in range(burst_frames):
        price *= 1.0 + price_step_pct / 100.0
        trades += burst_rate
        quote += burst_notional
        evt += 1_000
        now += 1.0
        ignitions += det.ingest(
            _frame(symbol, price=price, trades=trades, quote=quote, evt_ms=evt), now=now
        )
    return ignitions


def test_sustained_burst_with_move_ignites_long():
    det = _make_detector()
    ignitions = _warm_then_burst(det)
    assert ignitions, "a sustained burst + >1% move should ignite"
    sym, direction = ignitions[0]
    assert sym == "ABCUSDT"
    assert direction == LONG


def test_downward_move_ignites_short():
    det = _make_detector()
    ignitions = _warm_then_burst(det, price_step_pct=-0.6)
    assert ignitions
    assert ignitions[0][1] == SHORT


def test_burst_without_move_does_not_ignite():
    # Big trade-rate burst but price stays flat ⇒ no directional move ⇒ no fire.
    det = _make_detector()
    ignitions = _warm_then_burst(det, price_step_pct=0.0)
    assert ignitions == []


def test_move_without_burst_does_not_ignite():
    # Price moves but trade-rate stays at baseline ⇒ no RVOL surge ⇒ no fire.
    det = _make_detector()
    ignitions = _warm_then_burst(det, burst_rate=10, burst_notional=5_000.0)
    assert ignitions == []


def test_micro_cap_notional_floor_blocks_ignition():
    # Move + burst present, but windowed notional below the floor ⇒ no fire.
    det = _make_detector(min_window_notional_usd=10_000_000.0)
    ignitions = _warm_then_burst(det)
    assert ignitions == []


def test_warmup_gate_blocks_early_ignition():
    # Before the baseline has enough samples, even a burst+move cannot fire.
    det = _make_detector(min_baseline_samples=1_000)
    ignitions = _warm_then_burst(det, warm_frames=8, burst_frames=5)
    assert ignitions == []


def test_disabled_detector_never_ignites():
    det = _make_detector(enabled=False)
    ignitions = _warm_then_burst(det)
    assert ignitions == []


def test_cooldown_suppresses_reignition():
    det = _make_detector(cooldown_sec=10_000.0)
    first = _warm_then_burst(det)
    assert first
    # Immediately feed another burst within the cooldown window — no re-fire.
    second = _warm_then_burst(det, warm_frames=2, now=2_000.0)
    assert second == []


def test_non_usdt_symbol_is_ignored():
    det = _make_detector()
    ignitions = _warm_then_burst(det, symbol="ABCBUSD")
    assert ignitions == []


def test_large_time_gap_resets_state_no_cross_hole_fire():
    det = _make_detector(max_gap_sec=5.0)
    symbol = "GAPUSDT"
    # Warm the baseline.
    price, trades, quote = 100.0, 1_000, 1_000_000.0
    evt, now = 1_700_000_000_000, 1000.0
    for _ in range(8):
        det.ingest(_frame(symbol, price=price, trades=trades, quote=quote, evt_ms=evt), now=now)
        trades += 10
        quote += 5_000.0
        evt += 1_000
        now += 1.0
    # A single frame after a 60 s hole with a huge price jump must NOT fire —
    # the gap exceeds max_gap_sec, so state resets instead of measuring across it.
    evt += 60_000
    now += 60.0
    out = det.ingest(
        _frame(symbol, price=price * 1.2, trades=trades + 5_000, quote=quote + 5_000_000.0, evt_ms=evt),
        now=now,
    )
    assert out == []


def test_duplicate_event_time_is_ignored():
    det = _make_detector()
    symbol = "DUPUSDT"
    evt = 1_700_000_000_000
    out1 = det.ingest(_frame(symbol, price=100.0, trades=1_000, quote=1_000_000.0, evt_ms=evt), now=1.0)
    # Same E (dt <= 0) — must be a no-op, not a divide-by-zero.
    out2 = det.ingest(_frame(symbol, price=200.0, trades=9_999, quote=9_999_999.0, evt_ms=evt), now=2.0)
    assert out1 == [] and out2 == []


def test_empty_and_malformed_frames_are_safe():
    det = _make_detector()
    assert det.ingest([], now=1.0) == []
    # Missing keys / bad types must be skipped, not raise.
    assert det.ingest([{"s": "XUSDT"}], now=1.0) == []
    assert det.ingest([{"s": "XUSDT", "c": "n/a", "n": 1, "q": 1, "E": 1}], now=1.0) == []
