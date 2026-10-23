"""The correlated exposure cap counts per path, not book-wide.

WHY (owner, 2026-10-23: "make per path same signals max 4"). The cap counted
every active same-direction scalp signal across all paths, so four MVRTP longs
blocked every other path's longs. In the 90 days to 2026-10-23 the delivered
book entered at that limit 1,139 times out of 2,804.

Driven through the real `_scan_symbol` with the harness `test_scanner.py`
uses, and asserted on the cap's own counter so no other gate can stand in
for it.
"""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import MAX_CORRELATED_SCALP_SIGNALS
from src.smc import Direction
from tests.test_scanner import (
    _execution_pass,
    _make_scan_ready_scanner,
    _make_signal,
    _risk_pass,
    _setup_pass,
)

_PATH = "MOVER_TREND_PULLBACK"
_OTHER = "LIQUIDITY_SWEEP_REVERSAL"


def _active(n: int, setup: str, direction: Direction = Direction.LONG) -> dict:
    out = {}
    for i in range(n):
        s = _make_signal(signal_id=f"ACT-{setup}-{i}", direction=direction)
        s.symbol = f"X{i}{setup[:3]}USDT"
        s.setup_class = setup
        s.origin_setup_class = setup
        out[s.signal_id] = s
    return out


async def _cap_fired(active: dict) -> bool:
    channel = MagicMock()
    channel.config = SimpleNamespace(name="360_SCALP", min_confidence=60.0)
    cand = _make_signal(signal_id="CAND")
    cand.setup_class = _PATH
    channel.evaluate.return_value = cand

    signal_queue = MagicMock()
    signal_queue.put = AsyncMock(return_value=True)
    scanner = _make_scan_ready_scanner(channel=channel, signal_queue=signal_queue)
    scanner.router.active_signals = active

    score = SimpleNamespace(
        total=87.0,
        quality_tier=SimpleNamespace(value="A"),
        components={"market": 20.0, "setup": 25.0, "execution": 20.0, "risk": 15.0, "context": 7.0},
    )
    with patch("src.scanner.compute_confidence", return_value=SimpleNamespace(total=55.0, blocked=False)), \
         patch("src.scanner.score_signal_components", return_value=score), \
         patch.object(scanner, "_evaluate_setup", return_value=_setup_pass()), \
         patch.object(scanner, "_evaluate_execution", return_value=_execution_pass()), \
         patch.object(scanner, "_evaluate_risk", return_value=_risk_pass()), \
         patch("src.scanner.check_vwap_extension", return_value=(True, "")), \
         patch("src.scanner.check_kill_zone_gate", return_value=(True, "")):
        await scanner._scan_symbol("BTCUSDT", 10_000_000)
    return any(k.startswith("correlated_scalp_cap:") for k in scanner._suppression_counters)


@pytest.mark.asyncio
async def test_a_full_path_blocks_its_own_next_signal():
    assert await _cap_fired(_active(MAX_CORRELATED_SCALP_SIGNALS, _PATH))


@pytest.mark.asyncio
async def test_another_path_being_full_does_not_block():
    # Fails on the book-wide cap: four LSR longs used to block an MVRTP long.
    assert not await _cap_fired(_active(MAX_CORRELATED_SCALP_SIGNALS, _OTHER))


@pytest.mark.asyncio
async def test_below_the_limit_on_its_own_path_does_not_block():
    active = _active(MAX_CORRELATED_SCALP_SIGNALS - 1, _PATH)
    active.update(_active(MAX_CORRELATED_SCALP_SIGNALS, _OTHER))
    assert not await _cap_fired(active)


@pytest.mark.asyncio
async def test_the_other_direction_does_not_count():
    assert not await _cap_fired(_active(MAX_CORRELATED_SCALP_SIGNALS, _PATH, Direction.SHORT))
