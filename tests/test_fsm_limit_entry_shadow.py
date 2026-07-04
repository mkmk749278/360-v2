"""FSM LIMIT-entry stamp-and-shadow phase (S41, docs/FSM_LIMIT_ENTRY_DESIGN.md).

Owner-approved direction: LIMIT at zone + TTL. While FSM_LIMIT_ENTRY_ENABLED
is dark, every real dispatch logs the would-be order mode so activation is
decided on measured dispatch data. These tests pin: dark by default, shadow
line emitted with the correct mode, dispatch behaviour untouched.
"""
from __future__ import annotations

from unittest.mock import patch

from loguru import logger

from src.execution import signal_dispatch as sd


async def _capture_dispatch_shadow(**kwargs):
    lines: list = []
    sink = logger.add(lambda m: lines.append(str(m)), level="INFO")
    try:
        with patch.object(sd, "_active_uids", return_value=[]):
            n = await sd.dispatch_signal_to_active_users(
                signal_id="S-1", symbol="SOLUSDT", direction="LONG",
                entry_price=100.0, sl_price=99.0, tp1_price=102.0,
                tp2_price=103.0, tp3_price=104.0, **kwargs,
            )
    finally:
        logger.remove(sink)
    return n, [l for l in lines if "FSM_LIMIT_ENTRY" in l]


def test_flag_is_dark_by_default():
    from config import FSM_LIMIT_ENTRY_ENABLED

    assert FSM_LIMIT_ENTRY_ENABLED is False


async def test_shadow_in_zone_mode():
    n, shadows = await _capture_dispatch_shadow(
        entry_zone_low=99.9, entry_zone_high=100.1,
        valid_for_minutes=15, current_price=100.0,
    )
    assert n == 0  # no users — dispatch behaviour untouched
    assert len(shadows) == 1
    assert "mode=in_zone" in shadows[0]


async def test_shadow_would_rest_mode():
    _, shadows = await _capture_dispatch_shadow(
        entry_zone_low=99.9, entry_zone_high=100.1,
        valid_for_minutes=15, current_price=101.5,
    )
    assert len(shadows) == 1
    assert "mode=would_rest" in shadows[0]


async def test_shadow_market_semantics_when_no_zone():
    _, shadows = await _capture_dispatch_shadow(valid_for_minutes=15)
    assert len(shadows) == 1
    assert "mode=market_semantics" in shadows[0]
