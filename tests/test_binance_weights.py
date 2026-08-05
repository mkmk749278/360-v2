"""Every Binance call must declare a weight the table can vouch for.

An under-declared weight makes ``rate_limiter`` optimistic: it keeps issuing
requests believing it has budget it has already spent. There is no warning
before the 429, so this cannot be a review-time convention — it has to fail CI.

``fetch_recent_trades`` declared ``weight=1`` for ``/fapi/v1/trades`` (actual 5)
and ``/api/v3/trades`` (actual 25) while fetching ``limit=1000``. It was recorded
as an open follow-up in ``ACTIVE_CONTEXT.md`` and shipped anyway, because nothing
enforced it. These tests are that enforcement.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from src.binance_weights import (
    BY_LIMIT,
    CARRIED,
    FIXED,
    VERIFIED,
    known_paths,
    weight_for,
)

SRC = pathlib.Path(__file__).resolve().parents[1] / "src"

#: Call methods that spend rate-limit budget.
_REQUEST_METHODS = {"_get", "_post", "_delete", "_signed_get"}


def _call_sites():
    """**Every** Binance request call in ``src/``, literal endpoint or not.

    Parsed from the AST rather than grepped, so a reformatted call site cannot
    slip past by wrapping its arguments differently.

    The endpoint is yielded as ``None`` when it is not a string literal, and
    those calls are still audited for their weight. The first cut of this
    helper required ``node.args[0]`` to be a constant — and the fix that
    centralised ``fetch_recent_trades``'s two branches into one call with a
    ``path`` variable therefore made **the very call site this module exists
    for** invisible to its own audit. Reverting the weight to 1 left the suite
    green. A check that stops seeing a call site the moment it is refactored is
    the shape of every defect in ``CLAUDE.md``: it looks like coverage and is
    not.
    """
    for path in sorted(SRC.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            name = getattr(fn, "attr", None) or getattr(fn, "id", None)
            if name not in _REQUEST_METHODS:
                continue
            if not node.args:
                continue
            first = node.args[0]
            endpoint = None
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                if not first.value.startswith(("/api", "/fapi")):
                    continue
                endpoint = first.value
            weight_expr = None
            for kw in node.keywords:
                if kw.arg == "weight":
                    weight_expr = ast.unparse(kw.value)
            yield str(path.relative_to(SRC)), node.lineno, endpoint, weight_expr


class TestEveryCallSiteIsPriced:
    def test_every_call_declares_a_weight(self):
        """A call with no ``weight=`` spends the limiter's default, silently."""
        missing = [
            f"{f}:{ln} {ep or '<dynamic path>'}"
            for f, ln, ep, w in _call_sites()
            if w is None
        ]
        assert not missing, (
            "Binance calls with no declared weight:\n  " + "\n  ".join(missing)
        )

    def test_no_call_site_hand_types_its_weight(self):
        """The number must come from the table, not from a literal.

        A hand-typed weight is how ``/fapi/v1/trades`` sat at 1 against an
        actual 5 for as long as it did: correct-looking, unchecked, and wrong.
        """
        literals = [
            f"{f}:{ln} {ep or '<dynamic path>'} weight={w}"
            for f, ln, ep, w in _call_sites()
            if w is not None and not w.startswith("weight_for(")
        ]
        assert not literals, (
            "Binance calls hand-typing a weight instead of using "
            "binance_weights.weight_for():\n  " + "\n  ".join(literals)
        )

    def test_the_audit_sees_calls_with_a_non_literal_path(self):
        """Pins the hole found while verifying this fix by reverting it.

        ``fetch_recent_trades`` resolves its endpoint into a ``path`` variable,
        so an audit keyed on literal first-arguments skipped it entirely — and
        restoring the original ``weight=1`` left every test green. At least one
        dynamic-path call must be visible here, or the audit has silently
        narrowed again."""
        dynamic = [(f, ln) for f, ln, ep, _w in _call_sites() if ep is None]
        assert dynamic, (
            "No dynamic-path Binance calls seen. Either they were all made "
            "literal (fine) or this audit stopped seeing them (not fine) — "
            "check src/historical_data.py fetch_recent_trades."
        )

    def test_every_called_endpoint_is_in_the_table(self):
        """``weight_for`` refuses an unknown path, so an undeclared endpoint
        would raise at runtime — on a live scan cycle. Catch it here."""
        unknown = sorted(
            {
                ep
                for _f, _ln, ep, _w in _call_sites()
                if ep is not None and ep not in known_paths()
            }
        )
        assert not unknown, (
            "Endpoints called but not declared in binance_weights:\n  "
            + "\n  ".join(unknown)
        )


class TestTheTableItself:
    def test_the_trades_endpoints_carry_their_verified_weights(self):
        """The defect this module was written for. Fails against the old tree,
        where both of these were declared as 1."""
        assert weight_for("/fapi/v1/trades") == 5
        assert weight_for("/api/v3/trades") == 25
        assert FIXED["/fapi/v1/trades"].source == VERIFIED
        assert FIXED["/api/v3/trades"].source == VERIFIED

    def test_an_unknown_endpoint_refuses_rather_than_defaulting(self):
        """Absence of knowledge is not permission. A default of 1 on a new
        endpoint is invisible until the budget is already overspent."""
        with pytest.raises(KeyError) as exc:
            weight_for("/fapi/v1/somethingNew")
        assert "binance_weights" in str(exc.value)

    def test_a_by_limit_endpoint_refuses_without_a_limit(self):
        """Pricing a weight-by-limit endpoint at its cheapest tier by omission
        is an under-declaration wearing a default."""
        with pytest.raises(ValueError):
            weight_for("/fapi/v1/klines")

    def test_depth_tiers_match_the_published_table(self):
        """VERIFIED 2026-08-05: 5/10/20/50 -> 2, 100 -> 5, 500 -> 10, 1000 -> 20."""
        assert [weight_for("/fapi/v1/depth", limit=n) for n in (5, 20, 50)] == [2, 2, 2]
        assert weight_for("/fapi/v1/depth", limit=100) == 5
        assert weight_for("/fapi/v1/depth", limit=500) == 10
        assert weight_for("/fapi/v1/depth", limit=1000) == 20

    def test_the_all_symbol_and_single_symbol_forms_are_not_interchangeable(self):
        """A factor of 40 between them. It must never be implicit."""
        assert weight_for("/fapi/v1/ticker/24hr") == 40
        assert weight_for("/fapi/v1/ticker/24hr", single_symbol=True) == 1

    def test_every_entry_states_where_its_number_came_from(self):
        """An unlabelled constant reads exactly like a verified one."""
        for path, w in FIXED.items():
            assert w.source in (VERIFIED, CARRIED), f"{path} has no provenance"

    def test_carried_entries_are_visible_as_unconfirmed(self):
        """Not a failure — a standing note that these are the first things to
        re-check if the limiter starts disagreeing with the exchange."""
        carried = sorted(p for p, w in FIXED.items() if w.source == CARRIED)
        # Documented, not asserted empty: confirming them needs vendor pages
        # that did not render during the 2026-08-05 audit.
        assert isinstance(carried, list)


class TestTheDeadTrackerIsGone:
    def test_api_limits_module_is_removed(self):
        """It declared 1200 as the per-minute limit (the futures limit is
        2,400) and fed only itself: ``APIWeightTracker`` and ``BatchScheduler``
        were instantiated in the scanner and **never called**. Two weight
        systems, one of them dead and wrong, is worse than one."""
        assert not (SRC / "api_limits.py").exists()

    def test_nothing_imports_it(self):
        offenders = [
            str(p.relative_to(SRC))
            for p in SRC.rglob("*.py")
            if "api_limits" in p.read_text(encoding="utf-8")
        ]
        assert not offenders, f"api_limits still referenced in {offenders}"

    def test_rate_limiter_remains_the_single_budget_authority(self):
        """Its 2,200 futures budget is a *deliberate* margin under the 2,400
        limit, not drift — the reserve covers reconnects and ad-hoc calls. This
        pins that the margin exists so a future 'fix' cannot raise it to 2,400
        and remove the headroom."""
        from src.rate_limiter import _DEFAULT_FUTURES_BUDGET

        assert 2_000 <= _DEFAULT_FUTURES_BUDGET < 2_400
