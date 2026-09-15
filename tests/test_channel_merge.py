"""Tests for single-channel Telegram routing (config._build_channel_telegram_map)."""

from __future__ import annotations

import importlib
import os
from unittest import mock

_SCALP_CHANNELS = (
    "360_SCALP", "360_SCALP_FVG", "360_SCALP_CVD", "360_SCALP_VWAP",
    "360_SCALP_DIVERGENCE", "360_SCALP_SUPERTREND", "360_SCALP_ICHIMOKU", "360_SCALP_ORDERBLOCK",
)


def _build_map(**env_overrides):
    """Re-import config with specific env vars set and return CHANNEL_TELEGRAM_MAP.

    Restores the original config module state after the call so module-level
    constants seen by other tests don't leak across test boundaries.  Pre-fix
    this leaked: tests in `test_scanner.py`, `test_regime_soft_penalty.py`,
    and others would see whatever state this last call left behind.
    """
    env = {
        "TELEGRAM_ACTIVE_CHANNEL_ID": "",
        **env_overrides,
    }
    try:
        with mock.patch.dict(os.environ, env, clear=False):
            import config as cfg_module
            importlib.reload(cfg_module)
            return cfg_module._build_channel_telegram_map()
    finally:
        # Restore module to the env-clean default so later tests see the
        # config state they were imported with.
        import config as cfg_module
        importlib.reload(cfg_module)


class TestBuildChannelTelegramMap:
    def test_with_active_channel_routes_all_signals(self):
        """When ACTIVE is set AND broadcast channels are on, all scalp
        channels → active_id.

        The switch is named explicitly rather than inherited from the
        default: from 2026-09-15 `TELEGRAM_SIGNALS_ENABLED` blanks the
        channel id, so a test that did not say which world it is in would
        be measuring the default instead of the routing.
        """
        mapping = _build_map(
            TELEGRAM_SIGNALS_ENABLED="true", TELEGRAM_ACTIVE_CHANNEL_ID="active_id"
        )

        for ch in _SCALP_CHANNELS:
            assert mapping[ch] == "active_id", f"{ch} should route to active_id"

    def test_without_active_channel_all_empty(self):
        """When ACTIVE is not set, all channels resolve to an empty string."""
        mapping = _build_map(TELEGRAM_ACTIVE_CHANNEL_ID="")
        for ch in _SCALP_CHANNELS:
            assert mapping[ch] == "", f"{ch} should be empty when ACTIVE is unset"

    def test_active_set_routes_all_to_active(self):
        """ACTIVE set (and channels on) → all nine channels route to active_id."""
        mapping = _build_map(
            TELEGRAM_SIGNALS_ENABLED="true", TELEGRAM_ACTIVE_CHANNEL_ID="active_id"
        )
        for ch in _SCALP_CHANNELS:
            assert mapping[ch] == "active_id"

    def test_the_broadcast_switch_blanks_the_map_even_with_an_id_set(self):
        """The 2026-09-15 debloat, pinned where the map is built.

        The engine's `.env` keeps its channel id; the switch is what decides
        whether anything reads it. Every consumer of this map already
        handles an unconfigured channel, which is why the switch is applied
        here rather than at each of the ~14 posting sites.
        """
        mapping = _build_map(TELEGRAM_ACTIVE_CHANNEL_ID="active_id")
        for ch in _SCALP_CHANNELS:
            assert mapping[ch] == "", (
                f"{ch} still resolves to a chat id with broadcast channels off"
            )

    def test_all_nine_channels_present(self):
        """The map always contains exactly 9 scalp channel keys."""
        mapping = _build_map()
        expected_keys = set(_SCALP_CHANNELS)
        assert set(mapping.keys()) == expected_keys
