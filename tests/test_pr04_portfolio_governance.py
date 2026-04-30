"""PR-04 — Portfolio-governance alignment tests.

Verifies that the active production defaults now match the canonical governance
doctrine defined in OWNER_BRIEF.md Part VI §6.2:

1. Auxiliary paid-channel paths (360_SCALP_FVG, 360_SCALP_DIVERGENCE,
   360_SCALP_ORDERBLOCK) are governed explicitly by rollout state, with
   360_SCALP_DIVERGENCE in limited-live pilot.
2. Core trusted 360_SCALP internal evaluators remain active.
3. Runtime routing / scanner initialization matches the governance doctrine.
4. Auxiliary channel code remains present and callable — the disable is a
   default-flag change only, so channels can be re-enabled via env var.
"""

from __future__ import annotations

import importlib
import os
import sys


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_config_with_env(env: dict[str, str]):
    """Re-import config with a specific set of env vars in effect.

    Returns the freshly-imported config module so tests can inspect its values
    without polluting the test session's cached module state.
    """
    original_env = {k: os.environ.get(k) for k in env}
    try:
        for k, v in env.items():
            os.environ[k] = v

        # Remove cached module so _safe_bool() re-reads the fresh env.
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config" or mod_name.startswith("config."):
                del sys.modules[mod_name]

        cfg = importlib.import_module("config")
        return cfg
    finally:
        # Restore original env
        for k, original_v in original_env.items():
            if original_v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = original_v
        # Reload canonical config back AND reload dependent modules that
        # captured `from config import X` references at their import time.
        # Without this, src.scanner / src.signal_quality / etc. retain
        # stale references to the test's overridden values, which
        # contaminates downstream tests in the same session.
        for mod_name in list(sys.modules.keys()):
            if mod_name == "config" or mod_name.startswith("config."):
                del sys.modules[mod_name]
        importlib.import_module("config")
        # Reload modules whose module-level constants come from `from config import …`
        for dependent in ("src.scanner", "src.signal_quality"):
            if dependent in sys.modules:
                importlib.reload(sys.modules[dependent])


# ---------------------------------------------------------------------------
# PR-04 Test Suite
# ---------------------------------------------------------------------------

class TestAuxiliaryChannelsDisabledByDefault:
    """Auxiliary paid-channel paths must not be active in production defaults."""

    def test_360_scalp_fvg_disabled_by_default(self):
        """360_SCALP_FVG must be disabled out of the box (no env override)."""
        cfg = _reload_config_with_env({"CHANNEL_SCALP_FVG_ENABLED": "false"})
        assert cfg.CHANNEL_SCALP_FVG_ENABLED is False, (
            "360_SCALP_FVG must default to disabled — it is under governance review "
            "and not yet trusted for redeploy (PR-04)."
        )

    def test_360_scalp_divergence_enabled_for_limited_live_by_default(self):
        """360_SCALP_DIVERGENCE must be enabled for controlled pilot rollout."""
        cfg = _reload_config_with_env({"CHANNEL_SCALP_DIVERGENCE_ENABLED": "true"})
        assert cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED is True, (
            "360_SCALP_DIVERGENCE is the PR-5 narrow pilot path and must remain "
            "enabled for limited-live rollout unless explicitly rolled back."
        )

    def test_360_scalp_orderblock_disabled_by_default(self):
        """360_SCALP_ORDERBLOCK must be disabled out of the box."""
        cfg = _reload_config_with_env({"CHANNEL_SCALP_ORDERBLOCK_ENABLED": "false"})
        assert cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED is False, (
            "360_SCALP_ORDERBLOCK must default to disabled — SMC_ORDERBLOCK path "
            "is under governance review and not yet trusted for redeploy (PR-04)."
        )

    def test_auxiliary_defaults_are_selective_not_blanket_enabled(self):
        """Only divergence pilot is enabled; other specialist channels remain disabled."""
        cfg = _reload_config_with_env({
            "CHANNEL_SCALP_FVG_ENABLED": "false",
            "CHANNEL_SCALP_DIVERGENCE_ENABLED": "true",
            "CHANNEL_SCALP_ORDERBLOCK_ENABLED": "false",
        })
        assert cfg.CHANNEL_SCALP_FVG_ENABLED is False
        assert cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED is True
        assert cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED is False


class TestCoreTrustedChannelsRemainActive:
    """Core trusted 360_SCALP internal evaluators must remain enabled by default."""

    def test_360_scalp_core_channel_enabled_by_default(self):
        """360_SCALP (core internal evaluators) must remain active."""
        import config as cfg  # noqa: PLC0415
        assert cfg.CHANNEL_SCALP_ENABLED is True, (
            "360_SCALP (core internal evaluators) must remain active by default. "
            "Only the auxiliary paid-channel paths are disabled by PR-04."
        )

    def test_scanner_channel_flags_reflect_governance_defaults(self):
        """Scanner's _CHANNEL_ENABLED_FLAGS must match the governance defaults."""
        # Import scanner to trigger its module-level initialisation.
        import importlib as _il  # noqa: PLC0415

        # Remove cached scanner so it re-reads config defaults
        for mod_name in list(sys.modules.keys()):
            if "scanner" in mod_name:
                del sys.modules[mod_name]

        scanner = _il.import_module("src.scanner")

        flags = scanner._CHANNEL_ENABLED_FLAGS

        # Core channel must be on
        assert flags.get("360_SCALP") is True, (
            "360_SCALP must be enabled in the scanner's channel flag map."
        )

        # FVG/ORDERBLOCK remain disabled by default; DIVERGENCE is pilot-enabled.
        assert flags.get("360_SCALP_FVG") is False, (
            "360_SCALP_FVG must be disabled in scanner channel flags (PR-04)."
        )
        assert flags.get("360_SCALP_DIVERGENCE") is True, (
            "360_SCALP_DIVERGENCE must be enabled in scanner channel flags for PR-5 pilot."
        )
        assert flags.get("360_SCALP_ORDERBLOCK") is False, (
            "360_SCALP_ORDERBLOCK must be disabled in scanner channel flags (PR-04)."
        )


class TestAuxiliaryChannelCodeAvailable:
    """Auxiliary channel code must remain importable and callable for future rebuild."""

    def test_scalp_fvg_channel_class_importable(self):
        """ScalpFVGChannel evaluate() must still exist — disable is flag-only."""
        from src.channels.scalp_fvg import ScalpFVGChannel  # noqa: PLC0415
        assert hasattr(ScalpFVGChannel, "evaluate"), (
            "ScalpFVGChannel.evaluate() must remain present — code is preserved, "
            "only the default-enabled flag is changed (PR-04)."
        )

    def test_scalp_divergence_channel_class_importable(self):
        """ScalpDivergenceChannel evaluate() must still exist — disable is flag-only."""
        from src.channels.scalp_divergence import ScalpDivergenceChannel  # noqa: PLC0415
        assert hasattr(ScalpDivergenceChannel, "evaluate"), (
            "ScalpDivergenceChannel.evaluate() must remain present (PR-04)."
        )

    def test_scalp_orderblock_channel_class_importable(self):
        """ScalpOrderblockChannel evaluate() must still exist — disable is flag-only."""
        from src.channels.scalp_orderblock import ScalpOrderblockChannel  # noqa: PLC0415
        assert hasattr(ScalpOrderblockChannel, "evaluate"), (
            "ScalpOrderblockChannel.evaluate() must remain present (PR-04)."
        )

    def test_auxiliary_setup_classes_still_registered(self):
        """SetupClass enum must still include the auxiliary evaluator identities."""
        from src.signal_quality import SetupClass  # noqa: PLC0415
        assert hasattr(SetupClass, "FVG_RETEST"), (
            "SetupClass.FVG_RETEST must remain registered (PR-01 identity preservation)."
        )
        assert hasattr(SetupClass, "RSI_MACD_DIVERGENCE"), (
            "SetupClass.RSI_MACD_DIVERGENCE must remain registered."
        )
        assert hasattr(SetupClass, "SMC_ORDERBLOCK"), (
            "SetupClass.SMC_ORDERBLOCK must remain registered."
        )


class TestExplicitReenableWorks:
    """Auxiliary channels must be re-enable-able via env var without code changes."""

    def test_fvg_channel_can_be_reenabled_via_env(self):
        """Setting CHANNEL_SCALP_FVG_ENABLED=true must re-enable the channel."""
        cfg = _reload_config_with_env({"CHANNEL_SCALP_FVG_ENABLED": "true"})
        assert cfg.CHANNEL_SCALP_FVG_ENABLED is True, (
            "Setting CHANNEL_SCALP_FVG_ENABLED=true in the environment must "
            "re-enable 360_SCALP_FVG without any code change."
        )

    def test_divergence_channel_can_be_reenabled_via_env(self):
        """Setting CHANNEL_SCALP_DIVERGENCE_ENABLED=true must re-enable the channel."""
        cfg = _reload_config_with_env({"CHANNEL_SCALP_DIVERGENCE_ENABLED": "true"})
        assert cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED is True

    def test_orderblock_channel_can_be_reenabled_via_env(self):
        """Setting CHANNEL_SCALP_ORDERBLOCK_ENABLED=true must re-enable the channel."""
        cfg = _reload_config_with_env({"CHANNEL_SCALP_ORDERBLOCK_ENABLED": "true"})
        assert cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED is True


class TestGovernanceDoctrineRuntimeAlignment:
    """Runtime behavior must match the brief's governance doctrine (end-to-end check)."""

    # Channels that should be live by default under the current governance doctrine
    TRUSTED_DEFAULT_ON: frozenset[str] = frozenset({"360_SCALP"})

    # Auxiliary channels that remain off by default (under governance review)
    GOVERNANCE_REVIEW_OFF: frozenset[str] = frozenset({
        "360_SCALP_FVG",
        "360_SCALP_ORDERBLOCK",
    })

    def test_trusted_channels_are_enabled_in_scanner_flags(self):
        """Every trusted-default-on channel must be active in scanner flags."""
        import importlib as _il  # noqa: PLC0415

        for mod_name in list(sys.modules.keys()):
            if "scanner" in mod_name:
                del sys.modules[mod_name]

        scanner = _il.import_module("src.scanner")
        flags = scanner._CHANNEL_ENABLED_FLAGS

        for channel in self.TRUSTED_DEFAULT_ON:
            assert flags.get(channel) is True, (
                f"Trusted channel '{channel}' must be enabled in scanner flags."
            )

    def test_governance_review_channels_are_disabled_in_scanner_flags(self):
        """Every governance-review channel must be inactive in scanner flags."""
        import importlib as _il  # noqa: PLC0415

        for mod_name in list(sys.modules.keys()):
            if "scanner" in mod_name:
                del sys.modules[mod_name]

        scanner = _il.import_module("src.scanner")
        flags = scanner._CHANNEL_ENABLED_FLAGS

        for channel in self.GOVERNANCE_REVIEW_OFF:
            assert flags.get(channel) is False, (
                f"Governance-review channel '{channel}' must be disabled in scanner "
                f"flags until governance rebuild/re-enable decision (PR-04)."
            )

    def test_no_mismatch_between_config_defaults_and_scanner_flags(self):
        """Config default booleans and scanner flag map must agree for aux channels."""
        import importlib as _il  # noqa: PLC0415

        cfg = _il.import_module("config")

        for mod_name in list(sys.modules.keys()):
            if "scanner" in mod_name:
                del sys.modules[mod_name]

        scanner = _il.import_module("src.scanner")
        flags = scanner._CHANNEL_ENABLED_FLAGS

        assert flags.get("360_SCALP_FVG") == cfg.CHANNEL_SCALP_FVG_ENABLED
        assert flags.get("360_SCALP_DIVERGENCE") == cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED
        assert flags.get("360_SCALP_ORDERBLOCK") == cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED
