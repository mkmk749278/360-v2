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

Deliberately reload-free (2026-07-14): this file used to
``importlib.reload(config)`` and delete/re-import ``src.scanner`` mid-suite,
which orphaned every previously-imported reference and contaminated 28
downstream tests into permanent class-level xfails (soft-penalty + MTF-gate
suites).  Default assertions now read the LIVE config module (strictly
stronger — the old reload version set the env var to the expected value first,
which only tested the parser), and env-overridability is tested through
``config._safe_bool`` — the exact parser each flag is defined with — under
``monkeypatch.setenv``, touching no module state.
"""

from __future__ import annotations

import config as cfg
from config import _safe_bool


# ---------------------------------------------------------------------------
# PR-04 Test Suite
# ---------------------------------------------------------------------------

class TestAuxiliaryChannelsDisabledByDefault:
    """Auxiliary paid-channel paths must not be active in production defaults."""

    def test_360_scalp_fvg_disabled_by_default(self):
        """360_SCALP_FVG must be disabled out of the box."""
        assert cfg.CHANNEL_SCALP_FVG_ENABLED is False, (
            "360_SCALP_FVG must default to disabled — it is under governance review "
            "and not yet trusted for redeploy (PR-04)."
        )

    def test_360_scalp_divergence_enabled_for_limited_live_by_default(self):
        """360_SCALP_DIVERGENCE must be enabled for controlled pilot rollout."""
        assert cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED is True, (
            "360_SCALP_DIVERGENCE is the PR-5 narrow pilot path and must remain "
            "enabled for limited-live rollout unless explicitly rolled back."
        )

    def test_360_scalp_orderblock_disabled_by_default(self):
        """360_SCALP_ORDERBLOCK must be disabled out of the box."""
        assert cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED is False, (
            "360_SCALP_ORDERBLOCK must default to disabled — SMC_ORDERBLOCK path "
            "is under governance review and not yet trusted for redeploy (PR-04)."
        )

    def test_auxiliary_defaults_are_selective_not_blanket_enabled(self):
        """Only divergence pilot is enabled; other specialist channels remain disabled."""
        assert cfg.CHANNEL_SCALP_FVG_ENABLED is False
        assert cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED is True
        assert cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED is False


class TestCoreTrustedChannelsRemainActive:
    """Core trusted 360_SCALP internal evaluators must remain enabled by default."""

    def test_360_scalp_core_channel_enabled_by_default(self):
        """360_SCALP (core internal evaluators) must remain active."""
        assert cfg.CHANNEL_SCALP_ENABLED is True, (
            "360_SCALP (core internal evaluators) must remain active by default. "
            "Only the auxiliary paid-channel paths are disabled by PR-04."
        )

    def test_scanner_channel_flags_reflect_governance_defaults(self):
        """Scanner's _CHANNEL_ENABLED_FLAGS must match the governance defaults."""
        import src.scanner as scanner

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
    """Auxiliary channels must be re-enable-able via env var without code changes.

    Each flag is defined as ``_safe_bool("<NAME>", "<default>")`` in config —
    overridability is proven by driving that exact parser with the env var set
    to the opposite of the shipped default (no module reloads).
    """

    def test_fvg_channel_can_be_reenabled_via_env(self, monkeypatch):
        """Setting CHANNEL_SCALP_FVG_ENABLED=true must re-enable the channel."""
        monkeypatch.setenv("CHANNEL_SCALP_FVG_ENABLED", "true")
        assert _safe_bool("CHANNEL_SCALP_FVG_ENABLED", "false") is True, (
            "Setting CHANNEL_SCALP_FVG_ENABLED=true in the environment must "
            "re-enable 360_SCALP_FVG without any code change."
        )

    def test_divergence_channel_can_be_disabled_via_env(self, monkeypatch):
        """Setting CHANNEL_SCALP_DIVERGENCE_ENABLED=false must disable the pilot."""
        monkeypatch.setenv("CHANNEL_SCALP_DIVERGENCE_ENABLED", "false")
        assert _safe_bool("CHANNEL_SCALP_DIVERGENCE_ENABLED", "true") is False

    def test_orderblock_channel_can_be_reenabled_via_env(self, monkeypatch):
        """Setting CHANNEL_SCALP_ORDERBLOCK_ENABLED=true must re-enable the channel."""
        monkeypatch.setenv("CHANNEL_SCALP_ORDERBLOCK_ENABLED", "true")
        assert _safe_bool("CHANNEL_SCALP_ORDERBLOCK_ENABLED", "false") is True


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
        import src.scanner as scanner

        flags = scanner._CHANNEL_ENABLED_FLAGS
        for channel in self.TRUSTED_DEFAULT_ON:
            assert flags.get(channel) is True, (
                f"Trusted channel '{channel}' must be enabled in scanner flags."
            )

    def test_governance_review_channels_are_disabled_in_scanner_flags(self):
        """Every governance-review channel must be inactive in scanner flags."""
        import src.scanner as scanner

        flags = scanner._CHANNEL_ENABLED_FLAGS
        for channel in self.GOVERNANCE_REVIEW_OFF:
            assert flags.get(channel) is False, (
                f"Governance-review channel '{channel}' must be disabled in scanner "
                f"flags until governance rebuild/re-enable decision (PR-04)."
            )

    def test_no_mismatch_between_config_defaults_and_scanner_flags(self):
        """Config default booleans and scanner flag map must agree for aux channels."""
        import src.scanner as scanner

        flags = scanner._CHANNEL_ENABLED_FLAGS
        assert flags.get("360_SCALP_FVG") == cfg.CHANNEL_SCALP_FVG_ENABLED
        assert flags.get("360_SCALP_DIVERGENCE") == cfg.CHANNEL_SCALP_DIVERGENCE_ENABLED
        assert flags.get("360_SCALP_ORDERBLOCK") == cfg.CHANNEL_SCALP_ORDERBLOCK_ENABLED
