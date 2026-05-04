"""Tests for the 2026-05-04 kill-zone disable on 360_SCALP.

Background
----------
Truth-report soft-penalty breakdown (2026-05-04 04:16 UTC) showed the
KZ gate accounting for 80–100% of every filtered SCALP setup's
aggregate `gate=` penalty.  Kill Zone was inherited from session-traded
asset doctrine and is wrong for 24/7 crypto futures.  Per OWNER_BRIEF
§3.2 we are 24/7 scalpers — the gate is disabled on the main 360_SCALP
channel.  Other SCALP_* auxiliary channels keep KZ pending data on
their behaviour.

These tests assert:
* The doctrinal contract: 360_SCALP has kill_zone=False, other channels
  retain kill_zone=True.
* The runtime contract: when ``check_kill_zone_gate`` would fire,
  360_SCALP's gate-profile flag suppresses the penalty entirely;
  other SCALP channels continue to apply it.
"""
from __future__ import annotations

import pytest

from src.scanner import _CHANNEL_GATE_PROFILE


# ---------------------------------------------------------------------------
# Doctrinal contract — config dict assertions
# ---------------------------------------------------------------------------


def test_360_scalp_has_kill_zone_disabled():
    """The main paid channel must have kill_zone=False."""
    profile = _CHANNEL_GATE_PROFILE["360_SCALP"]
    assert profile["kill_zone"] is False, (
        "Kill Zone gate must be disabled for 360_SCALP — KZ deductions of "
        "5–13 confidence pts during 'low-liquidity' hours don't apply to "
        "24/7 crypto futures.  See ACTIVE_CONTEXT 2026-05-04 entry for the "
        "data-driven rationale."
    )


def test_360_scalp_other_gates_remain_active():
    """Other SCALP gates (mtf, vwap, oi, etc.) must remain on — only KZ is disabled."""
    profile = _CHANNEL_GATE_PROFILE["360_SCALP"]
    for gate in ("mtf", "vwap", "oi", "cross_asset", "spoof", "volume_div", "cluster"):
        assert profile[gate] is True, (
            f"360_SCALP gate {gate!r} must remain active; only KZ was disabled "
            "in the 2026-05-04 cleanup."
        )


@pytest.mark.parametrize(
    "channel",
    [
        "360_SCALP_FVG",
        "360_SCALP_CVD",
        "360_SCALP_VWAP",
        "360_SCALP_DIVERGENCE",
        "360_SCALP_SUPERTREND",
        "360_SCALP_ICHIMOKU",
        "360_SCALP_ORDERBLOCK",
    ],
)
def test_other_scalp_channels_retain_kill_zone(channel):
    """Auxiliary SCALP channels keep KZ pending data on their behaviour.

    The 2026-05-04 KZ disable was scoped to the main 360_SCALP channel
    only — auxiliary channels (FVG / CVD / VWAP / etc.) were NOT in the
    truth-report sample for the diagnosis, so we don't have data on
    whether KZ helps or hurts them.  Conservative scope: leave them
    alone until per-channel data justifies a change.
    """
    profile = _CHANNEL_GATE_PROFILE.get(channel, {})
    assert profile.get("kill_zone") is True, (
        f"{channel} should retain kill_zone=True until per-channel truth-report "
        "data justifies a separate change."
    )
