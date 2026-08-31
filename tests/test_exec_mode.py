"""``src/execution/exec_mode.py`` — what a mode MEANS, in one place.

These tests exist because ``both`` was accepted on the write path and
rejected or misread by everything downstream (#989). Each case below is a
site that was actually wrong, not a hypothetical:

* every response schema rejected ``both``, so a stored value could not be
  serialised back to the app;
* ``snapshot_writer`` deleted the Redis command key BEFORE validating, so
  an unsupported mode was consumed and dropped with only a log line;
* every paper surface tested ``active_mode == "paper"``, which ``both``
  fails — so ``both`` fired live orders and ran no paper book, the exact
  inverse of what it promises;
* switching paper → both ran ``prior_mode == "paper"`` → CLOSED the user's
  paper subscription window, truncating the history they may read because
  they asked for more.

The invariant these lock in: a mode's meaning is asked, never compared.
"""
from __future__ import annotations

import pytest

from src.execution import exec_mode as em


class TestBothIsNotHalfAMode:
    """``both`` must satisfy the live gate AND the paper gate."""

    def test_both_places_live_orders(self):
        assert em.places_live_orders("both") is True

    def test_both_runs_the_paper_book(self):
        """The regression. ``== "paper"`` said False here, which is how
        ``both`` came to mean "live only"."""
        assert em.runs_paper_book("both") is True

    def test_live_does_not_run_the_paper_book(self):
        assert em.runs_paper_book("live") is False

    def test_paper_does_not_place_live_orders(self):
        """The money-path direction. If this ever passes, paper mode is
        spending real funds."""
        assert em.places_live_orders("paper") is False


class TestFailClosed:
    """B12: capital preservation over signal volume. An unknown mode must
    never read as consent to trade."""

    @pytest.mark.parametrize("mode", [None, "", "  ", "LIVE_", "xxx", "on", "true"])
    def test_unknown_never_places_live_orders(self, mode):
        assert em.places_live_orders(mode) is False

    @pytest.mark.parametrize("mode", [None, "", "nonsense"])
    def test_unknown_normalises_to_none(self, mode):
        assert em.normalise(mode) is None

    def test_off_is_valid_but_enables_nothing(self):
        """``off`` is a real value meaning explicitly disabled — distinct
        from ``None`` meaning "no row". Valid, but never a green light."""
        assert em.is_valid("off") is True
        assert em.is_enabled("off") is False
        assert em.places_live_orders("off") is False
        assert em.runs_paper_book("off") is False

    def test_none_is_not_valid_input(self):
        assert em.is_valid(None) is False

    def test_non_string_input_is_refused_not_raised(self):
        """A gate that raises is a gate that 500s a page."""
        for bad in (0, 1, [], {}, object()):
            assert em.normalise(bad) is None
            assert em.places_live_orders(bad) is False


class TestCaseAndWhitespace:
    @pytest.mark.parametrize("raw", ["BOTH", "Both", " both ", "\tboth\n"])
    def test_mode_strings_are_normalised(self, raw):
        assert em.normalise(raw) == "both"
        assert em.places_live_orders(raw) is True
        assert em.runs_paper_book(raw) is True


class TestPaperSubscriptionWindow:
    """The data-integrity half of #989.

    The window governs what a user may READ about their own past paper
    trades. It must never narrow because they enabled something extra.
    """

    def test_both_keeps_the_window_open(self):
        assert em.paper_subscription_should_be_open("both") is True

    def test_paper_keeps_the_window_open(self):
        assert em.paper_subscription_should_be_open("paper") is True

    def test_live_only_does_not_hold_a_paper_window_open(self):
        assert em.paper_subscription_should_be_open("live") is False

    def test_off_closes_it(self):
        assert em.paper_subscription_should_be_open("off") is False

    def test_paper_to_both_is_not_a_close(self):
        """The exact reported defect: a user who ADDS live execution to
        paper must not lose their paper history. Both sides open ⇒ the
        transition is a no-op on the window."""
        assert em.paper_subscription_should_be_open("paper") is True
        assert em.paper_subscription_should_be_open("both") is True

    def test_both_to_live_does_close(self):
        """The converse must still work — dropping paper closes the
        window, or the window would never close at all."""
        assert em.paper_subscription_should_be_open("both") is True
        assert em.paper_subscription_should_be_open("live") is False


class TestValidModesIsTheSourceOfTruth:
    def test_the_four_modes(self):
        assert em.VALID_MODES == {"off", "paper", "live", "both"}

    def test_every_valid_mode_is_classifiable(self):
        """No mode may be valid yet unanswerable — that combination is
        how a value gets stored and then fails to serialise back."""
        for mode in em.VALID_MODES:
            assert isinstance(em.places_live_orders(mode), bool)
            assert isinstance(em.runs_paper_book(mode), bool)
            assert em.normalise(mode) == mode

    def test_the_api_schemas_accept_every_valid_mode(self):
        """The bug that made ``both`` unserialisable. Pydantic validates
        OUTBOUND too, so a response ``Literal`` narrower than the stored
        value set is a 500 waiting for the right row to exist."""
        pytest.importorskip("pydantic")
        import typing

        from src.api import schemas

        for model_name in (
            "PulseSnapshot",
            "UserAutoTradeSettingsRequest",
        ):
            model = getattr(schemas, model_name, None)
            if model is None:
                continue
            field = model.model_fields.get("mode")
            if field is None:
                continue
            allowed = set()
            for arg in typing.get_args(field.annotation):
                allowed.update(typing.get_args(arg) or ())
                if isinstance(arg, str):
                    allowed.add(arg)
            allowed.update(typing.get_args(field.annotation))
            allowed = {a for a in allowed if isinstance(a, str)}
            if not allowed:
                continue
            missing = em.VALID_MODES - allowed
            assert not missing, (
                f"{model_name}.mode cannot represent {sorted(missing)} — "
                f"a stored mode the schema rejects is a 500 on read"
            )
