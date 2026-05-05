"""Tests for the kill-zone disable across the SCALP channel family.

Background
----------
Truth-report soft-penalty breakdown (2026-05-04 04:16 UTC) showed the KZ
gate accounting for 80–100% of every filtered SCALP setup's aggregate
``gate=`` penalty.  Kill Zone was inherited from session-traded asset
doctrine and is wrong for 24/7 crypto futures.  Per OWNER_BRIEF §3.2 we
are 24/7 scalpers; penalising signals for time-of-day is structurally
wrong regardless of which scalp variant produced the signal.

Initial scope (PR #289, 2026-05-04) disabled KZ on the main 360_SCALP
channel only, with auxiliary 360_SCALP_* channels held back pending
per-channel truth-report data.  Subsequent truth reports showed those
auxiliary channels are too low-volume to ever generate the per-channel
sample, so the doctrinal call is applied uniformly across all scalp
variants — the §3.2 argument doesn't depend on volume.

These tests assert:
* The doctrinal contract — every SCALP-family channel has
  ``kill_zone=False``.
* The non-regression contract — other gates (mtf / vwap / oi /
  cross_asset / spoof / volume_div / cluster) remain on for every
  channel; only KZ was flipped.
"""
from __future__ import annotations

import pytest

from src.scanner import _CHANNEL_GATE_PROFILE


_SCALP_CHANNELS = (
    "360_SCALP",
    "360_SCALP_FVG",
    "360_SCALP_CVD",
    "360_SCALP_VWAP",
    "360_SCALP_DIVERGENCE",
    "360_SCALP_SUPERTREND",
    "360_SCALP_ICHIMOKU",
    "360_SCALP_ORDERBLOCK",
)

_OTHER_GATES = ("mtf", "vwap", "oi", "cross_asset", "spoof", "volume_div", "cluster")


# ---------------------------------------------------------------------------
# Doctrinal contract — KZ disabled on every SCALP channel
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("channel", _SCALP_CHANNELS)
def test_scalp_channel_has_kill_zone_disabled(channel):
    """Every SCALP channel must have ``kill_zone=False``.

    Kill Zone deductions of 5–13 confidence points during 'low-liquidity'
    hours don't apply to 24/7 crypto futures — see ACTIVE_CONTEXT for
    the data-driven rationale.  Reversing this requires a fresh truth-
    report case for the specific channel.
    """
    profile = _CHANNEL_GATE_PROFILE.get(channel, {})
    assert profile.get("kill_zone") is False, (
        f"{channel} must have kill_zone=False per OWNER_BRIEF §3.2 "
        "(24/7 scalpers — no session-time gating).  Reversing requires "
        "channel-specific truth-report evidence that KZ helps."
    )


# ---------------------------------------------------------------------------
# Non-regression contract — other gates stay on
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("channel", _SCALP_CHANNELS)
@pytest.mark.parametrize("gate", _OTHER_GATES)
def test_scalp_channel_other_gates_remain_active(channel, gate):
    """Only KZ was disabled; every other gate stays on for every channel.

    Defensive — if a future edit accidentally flips one of these to
    False, this test catches it before deploy.
    """
    profile = _CHANNEL_GATE_PROFILE.get(channel, {})
    assert profile.get(gate) is True, (
        f"{channel} gate {gate!r} must remain active.  Only KZ was "
        "disabled in the 2026-05-04 / aux-channel cleanup."
    )
