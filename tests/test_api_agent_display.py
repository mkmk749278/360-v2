"""Tests for the API agent-display + path-token maps.

When a new evaluator ships, both maps in ``src/api/snapshot.py`` must
be extended:
  - ``_AGENT_DISPLAY_NAMES``: setup_class → human-readable label shown
    in the Lumin app's per-agent drill-down.
  - ``_PATH_TO_SETUP``: telemetry path token → setup_class string,
    used to translate ScalpChannel's generation telemetry back into
    the canonical setup name.

The ``MA_CROSS_TREND_SHIFT`` evaluator (PR #318) was missing from
both maps when shipped, so the app showed it as "Engine" (the default
fallback) and the agent-stats lookup failed silently.
"""

from __future__ import annotations

from src.api.snapshot import (
    _AGENT_DISPLAY_NAMES,
    _PATH_TO_SETUP,
    _agent_name_for,
)
from src.signal_quality import SetupClass


class TestAgentDisplayNames:
    def test_ma_cross_has_display_name(self):
        """PR #318's 15th evaluator must appear in the agent map."""
        assert "MA_CROSS_TREND_SHIFT" in _AGENT_DISPLAY_NAMES
        assert _AGENT_DISPLAY_NAMES["MA_CROSS_TREND_SHIFT"]
        # Default fallback ("Engine") would mean the entry is missing.
        assert _AGENT_DISPLAY_NAMES["MA_CROSS_TREND_SHIFT"] != "Engine"

    def test_ma_cross_resolves_via_helper(self):
        assert _agent_name_for("MA_CROSS_TREND_SHIFT") == "The Trend Shifter"

    def test_unknown_setup_falls_back_to_engine(self):
        """Sanity: behaviour for unmapped class is still the safe fallback."""
        assert _agent_name_for("UNKNOWN_NEW_PATH") == "Engine"

    def test_every_active_evaluator_has_a_display_name(self):
        """Regression guard — if a new SetupClass enters
        ACTIVE_PATH_PORTFOLIO_ROLES it should also appear in
        _AGENT_DISPLAY_NAMES so the app doesn't silently render
        unknown setups as "Engine"."""
        from src.signal_quality import ACTIVE_PATH_PORTFOLIO_ROLES
        active_classes = {sc.value for sc in ACTIVE_PATH_PORTFOLIO_ROLES.keys()}
        missing = active_classes - set(_AGENT_DISPLAY_NAMES.keys())
        assert not missing, (
            f"Active evaluator setup_class without an _AGENT_DISPLAY_NAMES "
            f"entry: {missing}"
        )


class TestPathTokenToSetupClass:
    def test_ma_cross_path_token_resolves(self):
        """ScalpChannel telemetry uses path tokens (uppercased evaluator
        name minus '_evaluate_').  ``_evaluate_ma_cross_trend_shift`` →
        ``MA_CROSS_TREND_SHIFT``, which must map back to its setup_class."""
        assert "MA_CROSS_TREND_SHIFT" in _PATH_TO_SETUP
        assert _PATH_TO_SETUP["MA_CROSS_TREND_SHIFT"] == "MA_CROSS_TREND_SHIFT"

    def test_path_token_mapping_complete_for_ma_cross(self):
        """The setup_class on the right-hand side must match the enum."""
        target = _PATH_TO_SETUP["MA_CROSS_TREND_SHIFT"]
        assert target == SetupClass.MA_CROSS_TREND_SHIFT.value
