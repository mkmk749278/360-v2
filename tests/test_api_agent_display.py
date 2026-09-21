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


class TestRosterCoversWhatShipped:
    """``build_agents`` must not be a deny-list.

    It iterated ``_PATH_TO_SETUP`` alone — a hand-maintained map — so a
    setup class absent from it had no agent card at all, and the app's
    Agents page could not show its stats. Measured 2026-09-21 the map
    carried 19 of ``SetupClass``'s 29, and the ten missing included
    ``MULTI_STRATEGY_CONFLUENCE``, which ``Scanner`` assigns to signals it
    enqueues today. A subscriber looking up a strategy they had just been
    sent found nothing.

    A setup outside the map now earns a row by having lifecycle history —
    the population that would be harmed rather than the one that is
    convenient. One that has never shipped a signal stays out, because ten
    permanently empty cards are worse than the gap they would fill.
    """

    @staticmethod
    def _engine(setup_classes):
        """An engine whose history carries one signal per given setup."""
        from datetime import datetime, timedelta, timezone

        now = datetime.now(timezone.utc)

        class _Sig:
            def __init__(self, sc):
                self.setup_class = sc
                self.timestamp = now - timedelta(minutes=5)
                self.terminal_outcome_timestamp = now - timedelta(minutes=1)
                self.status = "TP1_HIT"

        class _Engine:
            _channels = []
            _signal_history = [_Sig(sc) for sc in setup_classes]
            router = None

        return _Engine()

    def test_a_shipped_setup_outside_the_map_gets_a_card(self):
        from src.api.snapshot import build_agents

        outside = "MULTI_STRATEGY_CONFLUENCE"
        assert outside not in set(_PATH_TO_SETUP.values()), (
            "This test is only meaningful while the setup sits outside the "
            "telemetry map; if it has been added there, pick another."
        )
        rows = build_agents(self._engine([outside]))
        classes = {r.setup_class for r in rows}
        assert outside in classes, (
            "A setup the engine has actually shipped signals for has no "
            "agent card, so the app cannot show its stats."
        )

    def test_a_setup_that_never_shipped_stays_out(self):
        from src.api.snapshot import build_agents

        rows = build_agents(self._engine([]))
        classes = {r.setup_class for r in rows}
        assert classes == {v for v in _PATH_TO_SETUP.values()}, (
            "With no history the roster must be exactly the telemetry map — "
            "empty cards for setups nobody has seen are worse than absent."
        )

    def test_every_mapped_setup_still_appears(self):
        """The union must never lose a member of the original map."""
        from src.api.snapshot import build_agents

        rows = build_agents(self._engine(["MULTI_STRATEGY_CONFLUENCE"]))
        classes = {r.setup_class for r in rows}
        missing = set(_PATH_TO_SETUP.values()) - classes
        assert not missing, f"roster dropped mapped setups: {missing}"
