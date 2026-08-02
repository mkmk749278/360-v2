"""Entry quality — the consuming half of the entry-feature lane.

#849 and #851 stamped what every path could have looked at and applied none of
it.  This module is the part that can cost a candidate its emission, so the
properties worth pinning are the ones that decide whether a live gate is honest:

1. **Shadow and enforce are different facts.** ``would_reject_by`` and
   ``enforced_by`` must never collapse into one field, because the whole
   promotion argument rests on measuring what a rule *would* have done while it
   is not doing it.
2. **Unknown abstains, and abstaining is visible.** A feature that did not
   compute must not suppress — and must not read as a pass either, because an
   inert rule and a working one look identical on every count except this one.
3. **The blast-radius cap degrades, it does not filter.** Over budget, the gate
   keeps stamping and stops suppressing, and says so.
4. **The ops control plane cannot drift from the rule registry.** Adding a rule
   must surface its knobs with no second edit — the fix for a drifting mirror is
   not a second mirror.
"""
from __future__ import annotations

import pytest

from src import entry_features as ef
from src import entry_quality as eq


def _params(**over):
    """An explicit envelope — never the process-wide config.

    A test that reads ``from_config`` asserts today's defaults rather than the
    behaviour, and would go green the day someone flips a flag.
    """
    rules = over.pop("rules", None)
    if rules is None:
        rules = tuple(
            eq.RuleParams(rule=r, live=r.live_default, threshold=r.threshold_default)
            for r in eq.RULES
        )
    base = {
        "enabled": True,
        "live": True,
        "max_reject_frac": 1.0,      # cap disabled unless a test is about it
        "budget_window": 200,
        "rules": rules,
    }
    base.update(over)
    return eq.EntryQualityParams(rules=rules, **{k: v for k, v in base.items() if k != "rules"})


def _rule(key: str, live: bool, threshold: float = 0.0) -> eq.RuleParams:
    return eq.RuleParams(rule=eq.RULES_BY_KEY[key], live=live, threshold=threshold)


# --------------------------------------------------------------------------- #
# Rule reading — refuse, don't clamp, and don't re-read a refusal as a zero
# --------------------------------------------------------------------------- #


class TestRuleReading:
    def test_a_flag_rule_fires_on_true(self):
        out = eq.evaluate_rule(_rule("profile_reject", live=True), {"profile_would_reject": True})
        assert out.verdict == eq.VERDICT_REJECT

    def test_a_flag_rule_passes_on_false(self):
        out = eq.evaluate_rule(_rule("profile_reject", live=True), {"profile_would_reject": False})
        assert out.verdict == eq.VERDICT_PASS

    def test_a_none_feature_is_unknown_not_a_pass_and_not_a_reject(self):
        """``entry_features`` returns None as a deliberate refusal — a missing
        order book, an absent pair profile. Reading it as ``False`` here would
        undo that at the only place it can cost a trade."""
        out = eq.evaluate_rule(_rule("profile_reject", live=True), {"profile_would_reject": None})
        assert out.verdict == eq.VERDICT_UNKNOWN
        assert out.unknown_reason == "feature_none"

    def test_an_absent_feature_is_named_apart_from_a_none_one(self):
        """Different faults, different fixes: a path that never stamped the
        feature and an upstream that went dark are not the same event."""
        out = eq.evaluate_rule(_rule("profile_reject", live=True), {})
        assert out.verdict == eq.VERDICT_UNKNOWN
        assert out.unknown_reason == "feature_absent"

    def test_a_max_rule_fires_above_its_threshold(self):
        rp = _rule("tpe_smc_zone", live=True, threshold=1.5)
        assert eq.evaluate_rule(rp, {"smc_zone_dist_atr": 40.0}).verdict == eq.VERDICT_REJECT
        assert eq.evaluate_rule(rp, {"smc_zone_dist_atr": 0.4}).verdict == eq.VERDICT_PASS

    def test_a_boundary_value_passes(self):
        """Exactly at the threshold is inside the zone, not outside it — the
        comparison is stated once here so a later edit cannot flip it silently."""
        rp = _rule("tpe_smc_zone", live=True, threshold=1.5)
        assert eq.evaluate_rule(rp, {"smc_zone_dist_atr": 1.5}).verdict == eq.VERDICT_PASS

    def test_a_non_numeric_feature_is_unknown_rather_than_coerced(self):
        rp = _rule("tpe_smc_zone", live=True, threshold=1.5)
        out = eq.evaluate_rule(rp, {"smc_zone_dist_atr": "wide"})
        assert out.verdict == eq.VERDICT_UNKNOWN
        assert out.unknown_reason == "feature_not_numeric"


# --------------------------------------------------------------------------- #
# Shadow vs enforce — the separation the whole promotion argument rests on
# --------------------------------------------------------------------------- #


class TestShadowAndEnforceAreDifferentFacts:
    def test_a_shadow_rule_records_what_it_would_have_killed_and_kills_nothing(self):
        params = _params(rules=(_rule("tpe_smc_zone", live=False, threshold=1.5),))
        d = eq.evaluate({"smc_zone_dist_atr": 40.0}, "TREND_PULLBACK_EMA", params)
        assert d.would_reject_by == ("tpe_smc_zone",)
        assert d.enforced_by is None
        assert d.suppressed is False

    def test_a_live_rule_suppresses(self):
        params = _params(rules=(_rule("profile_reject", live=True),))
        d = eq.evaluate({"profile_would_reject": True}, "MOVER_TREND_PULLBACK", params)
        assert d.enforced_by == "profile_reject"
        assert d.suppressed is True

    def test_the_master_switch_stops_every_rule_without_touching_per_rule_state(self):
        """One lever for the gate and one per rule. The rule stays live, so the
        shadow measurement it is being judged on keeps running."""
        params = _params(live=False, rules=(_rule("profile_reject", live=True),))
        d = eq.evaluate({"profile_would_reject": True}, "MOVER_TREND_PULLBACK", params)
        assert d.enforced_by is None
        assert d.would_reject_by == ("profile_reject",)

    def test_an_unknown_feature_never_suppresses(self):
        """The direction of the fail is deliberate. A fail-closed rule here
        would kill the entire feed the moment an upstream went dark, and the
        failure would be indistinguishable from a quiet market."""
        params = _params(rules=(_rule("profile_reject", live=True),))
        d = eq.evaluate({"profile_would_reject": None}, "MOVER_TREND_PULLBACK", params)
        assert d.enforced_by is None
        assert d.would_reject_by == ()

    def test_only_one_rule_is_credited_with_a_suppression(self):
        """Two rules firing on one candidate is one dead signal, not two — a
        gate table that double-counts cannot be ranked against its neighbours."""
        params = _params(
            rules=(_rule("profile_reject", live=True), _rule("tpe_smc_zone", live=True, threshold=1.5)),
        )
        d = eq.evaluate(
            {"profile_would_reject": True, "smc_zone_dist_atr": 40.0},
            "TREND_PULLBACK_EMA",
            params,
        )
        assert len(d.would_reject_by) == 2
        assert d.enforced_by == "profile_reject"

    def test_a_rule_scoped_to_a_path_does_not_judge_another(self):
        """The paths share no trigger, timeframe or stop geometry, so a
        threshold that is right on one is meaningless on another."""
        params = _params(rules=(_rule("tpe_smc_zone", live=True, threshold=1.5),))
        d = eq.evaluate({"smc_zone_dist_atr": 40.0}, "MOVER_TREND_PULLBACK", params)
        assert d.evaluated is False
        assert d.reason == "no_rules_for_path"


class TestInertIsNamedRatherThanSilent:
    def test_an_unstamped_candidate_reports_why_it_was_not_judged(self):
        """A live rule with zero decisions has two causes — nothing reached it,
        or nothing stamped it — and a panel that cannot tell them apart will
        report the wrong one."""
        d = eq.evaluate(None, "MOVER_TREND_PULLBACK", _params())
        assert d.evaluated is False
        assert d.reason == "no_stamp"

    def test_the_measurement_flag_off_is_its_own_reason(self):
        d = eq.evaluate({"profile_would_reject": True}, "X", _params(enabled=False))
        assert d.evaluated is False
        assert d.reason == "disabled"


# --------------------------------------------------------------------------- #
# The blast-radius cap
# --------------------------------------------------------------------------- #


class TestRejectBudget:
    def test_a_fresh_window_is_not_over_budget_on_its_first_rejection(self):
        """Measured against the window size, not against however many decisions
        have arrived — otherwise the first rejection after a boot reads as 100%
        and the gate suspends itself before it has done anything."""
        b = eq.RejectBudget(window=100, max_frac=0.35)
        b.record(True)
        assert b.allows() is True

    def test_it_stops_enforcing_once_the_cap_is_spent(self):
        b = eq.RejectBudget(window=10, max_frac=0.35)
        for _ in range(4):
            b.record(True)
        assert b.allows() is False

    def test_it_recovers_as_passing_decisions_push_rejections_out(self):
        b = eq.RejectBudget(window=10, max_frac=0.35)
        for _ in range(4):
            b.record(True)
        assert b.allows() is False
        for _ in range(10):
            b.record(False)
        assert b.allows() is True

    def test_over_budget_degrades_to_shadow_rather_than_passing_silently(self):
        """The candidate proceeds exactly as it would with the rule in shadow,
        the would-reject stamp is unchanged, and the suspension is its own
        state — a suspended gate must never read as a quiet market."""
        params = _params(rules=(_rule("profile_reject", live=True),))
        d = eq.evaluate(
            {"profile_would_reject": True},
            "MOVER_TREND_PULLBACK",
            params,
            budget_allows=False,
        )
        assert d.enforced_by is None
        assert d.budget_suspended is True
        assert d.would_reject_by == ("profile_reject",)
        assert d.reason == "budget_suspended"

    def test_the_budget_counts_passes_too_or_it_can_never_recover(self):
        """The denominator is every candidate the gate COULD have suppressed.

        Recorded only on rejections, the window is all-True, the fraction reads
        1.0, and the gate suspends itself permanently after ``cap × window``
        rejections with nothing able to push them out. Caught by asking what the
        ratio divides by before shipping it — the class this repo keeps paying
        for.
        """
        eq.reset_state()
        params = _params(
            max_reject_frac=0.35,
            budget_window=20,
            rules=(_rule("profile_reject", live=True),),
        )
        for _ in range(100):
            eq.decide({"profile_would_reject": False}, "MOVER_TREND_PULLBACK", params)
        snap = eq.get_budget().snapshot()
        assert snap["considered_total"] == 100
        assert snap["recent_reject_frac"] == pytest.approx(0.0)
        assert eq.get_budget().allows() is True
        eq.reset_state()

    def test_a_gate_that_spends_its_cap_recovers_on_later_passes(self):
        """End to end through ``decide``, not through the budget alone: the
        suspension must lift on its own, or a burst permanently disarms a rule
        the owner believes is enforcing."""
        eq.reset_state()
        params = _params(
            max_reject_frac=0.35,
            budget_window=20,
            rules=(_rule("profile_reject", live=True),),
        )
        suppressed = sum(
            1 for _ in range(20)
            if eq.decide(
                {"profile_would_reject": True}, "MOVER_TREND_PULLBACK", params
            ).suppressed
        )
        assert 0 < suppressed < 20, "the cap either never bit or never let anything through"
        assert eq.get_budget().allows() is False
        for _ in range(20):
            eq.decide({"profile_would_reject": False}, "MOVER_TREND_PULLBACK", params)
        assert eq.get_budget().allows() is True
        eq.reset_state()

    def test_a_shadow_only_window_does_not_consume_the_budget(self):
        """The cap exists to protect live output. Spending it on decisions that
        were never going to suppress would suspend a gate that had done
        nothing."""
        eq.reset_state()
        params = _params(
            max_reject_frac=0.35,
            budget_window=10,
            rules=(_rule("tpe_smc_zone", live=False, threshold=1.5),),
        )
        for _ in range(20):
            eq.decide({"smc_zone_dist_atr": 40.0}, "TREND_PULLBACK_EMA", params)
        assert eq.get_budget().snapshot()["considered_total"] == 0
        eq.reset_state()

    def test_a_disabled_cap_never_suspends(self):
        b = eq.RejectBudget(window=10, max_frac=1.0)
        for _ in range(10):
            b.record(True)
        assert b.allows() is True

    def test_reconfiguring_keeps_the_history_it_still_has_room_for(self):
        b = eq.RejectBudget(window=100, max_frac=0.35)
        for _ in range(50):
            b.record(False)
        b.reconfigure(window=20, max_frac=0.5)
        assert b.snapshot()["window"] == 20
        assert b.snapshot()["recent_decisions"] == 20


# --------------------------------------------------------------------------- #
# Counters — the states that are indistinguishable on any other count
# --------------------------------------------------------------------------- #


class TestCounters:
    def test_unknown_is_counted_per_rule(self):
        """An enforcing rule whose feature never computes passes everything and
        reads exactly like a rule that is working. This count is the only thing
        that separates them, which is why the probe reads it."""
        eq.reset_state()
        params = _params(rules=(_rule("profile_reject", live=True),))
        for _ in range(5):
            eq.decide({"profile_would_reject": None}, "MOVER_TREND_PULLBACK", params)
        snap = eq.snapshot(params)
        stats = snap["rules"][0]["stats"]
        assert stats["unknown"] == 5
        assert stats["unknown_frac"] == pytest.approx(1.0)
        assert snap["totals"]["enforced_total"] == 0
        eq.reset_state()

    def test_shadow_rejections_and_suppressions_are_counted_apart(self):
        eq.reset_state()
        params = _params(
            rules=(_rule("profile_reject", live=False), _rule("tpe_smc_zone", live=True, threshold=1.5)),
        )
        eq.decide({"profile_would_reject": True, "smc_zone_dist_atr": 0.2}, "TREND_PULLBACK_EMA", params)
        eq.decide({"profile_would_reject": False, "smc_zone_dist_atr": 40.0}, "TREND_PULLBACK_EMA", params)
        totals = eq.snapshot(params)["totals"]
        assert totals["shadow_reject_total"] == 1
        assert totals["enforced_total"] == 1
        eq.reset_state()

    def test_unstamped_candidates_are_counted_apart_from_evaluated_ones(self):
        eq.reset_state()
        params = _params()
        eq.decide(None, "MOVER_TREND_PULLBACK", params)
        totals = eq.snapshot(params)["totals"]
        assert totals["no_stamp_total"] == 1
        assert totals["evaluated_total"] == 0
        eq.reset_state()


# --------------------------------------------------------------------------- #
# The annotation round trip — one artifact, not two
# --------------------------------------------------------------------------- #


class TestLedgerAnnotation:
    def test_the_verdict_lands_on_the_row_ops_reads(self):
        led = ef.EntryFeatureLedger(path="")
        led.add({"signal_id": "s1", "setup_class": "MOVER_TREND_PULLBACK",
                 "profile_would_reject": True})

        row = led.row_for("s1")
        d = eq.evaluate(row, "MOVER_TREND_PULLBACK",
                        _params(rules=(_rule("profile_reject", live=True),)))
        assert led.annotate("s1", d.as_row()) is True

        stored = led.rows()[0]
        assert stored["eq_enforced_by"] == "profile_reject"
        assert stored["eq_would_reject_by"] == ["profile_reject"]
        assert stored["eq_rules"][0]["verdict"] == "reject"

    def test_row_for_returns_the_live_row_not_a_copy(self):
        """The gate reads what was stamped and writes back what it decided. A
        copy would give it a private view and leave the ledger describing a
        decision that was never made."""
        led = ef.EntryFeatureLedger(path="")
        led.add({"signal_id": "s1", "x": 1})
        led.row_for("s1")["x"] = 2
        assert led.rows()[0]["x"] == 2

    def test_an_annotation_with_no_row_is_counted_not_swallowed(self):
        """A miss means the ring rotated or the stamp never happened. An
        annotation landing nowhere is how a panel comes to describe a
        population that does not exist."""
        led = ef.EntryFeatureLedger(path="")
        assert led.annotate("never-stamped", {"eq_enforced_by": "x"}) is False
        assert led.annotate_misses == 1

    def test_an_evicted_row_is_dropped_from_the_lookup_map(self):
        """The map must not outlive its deque — otherwise it leaks, and an
        annotation lands on a row that will never be flushed."""
        led = ef.EntryFeatureLedger(path="", max_rows=3)
        for i in range(5):
            led.add({"signal_id": f"s{i}"})
        assert led.row_for("s0") is None
        assert led.row_for("s4") is not None
        assert len(led.rows()) == 3

    def test_a_reloaded_row_is_annotatable(self, tmp_path):
        """A restart must not split the ledger into rows the gate can write to
        and rows it cannot, with nothing on screen saying which."""
        path = str(tmp_path / "ef.json")
        led = ef.EntryFeatureLedger(path=path)
        led.add({"signal_id": "s1", "setup_class": "MOVER_TREND_PULLBACK"})
        led.flush(force=True)

        reloaded = ef.EntryFeatureLedger(path=path)
        reloaded.load()
        assert reloaded.row_for("s1") is not None
        assert reloaded.annotate("s1", {"eq_enforced_by": "profile_reject"}) is True


class TestSchemaIsNotBumpedForTheVerdict:
    def test_a_row_stamped_before_the_gate_carries_no_verdict_rather_than_a_pass(self):
        """Bumping the schema would drop the population this lane finally has;
        a pre-gate row simply has no ``eq_*`` keys, and a reader must render
        that as 'not evaluated'. A missing stamp is not a pass."""
        old_row = {"signal_id": "s1", "setup_class": "MOVER_TREND_PULLBACK"}
        assert "eq_enforced_by" not in old_row
        assert ef.SCHEMA == 2


# --------------------------------------------------------------------------- #
# The control plane cannot drift from the rule registry
# --------------------------------------------------------------------------- #


class TestOpsControlsComeFromTheRegistry:
    def test_every_rule_surfaces_its_live_switch_as_a_tunable(self):
        from src import runtime_tunables as rt

        reg = rt._build_registry()
        for rule in eq.RULES:
            assert rule.live_key in reg, (
                f"{rule.key} has no ops control — a rule that can only be "
                "flipped by a deploy is not on the control plane"
            )

    def test_a_thresholded_rule_surfaces_its_threshold_and_a_flag_rule_does_not(self):
        """A knob in ops that changes nothing is worse than no knob."""
        from src import runtime_tunables as rt

        reg = rt._build_registry()
        for rule in eq.RULES:
            if rule.compare == eq.CMP_FLAG:
                assert rule.threshold_key not in reg
            else:
                assert rule.threshold_key in reg

    def test_the_snapshot_ships_the_registry_so_ops_holds_no_mirror(self):
        """``MEASUREMENT_SUFFIXES`` drifted for a week. One writer, one reader."""
        snap = eq.snapshot(_params())
        assert {r["key"] for r in snap["rules"]} == {r.key for r in eq.RULES}
        for row in snap["rules"]:
            assert row["rationale"]
            assert row["feature"]
            assert row["compare"] in (eq.CMP_FLAG, eq.CMP_MAX, eq.CMP_MIN)

    def test_a_flag_rule_advertises_no_threshold_key_to_ops(self):
        snap = eq.snapshot(_params())
        by_key = {r["key"]: r for r in snap["rules"]}
        assert by_key["profile_reject"]["threshold_key"] == ""
        assert by_key["tpe_smc_zone"]["threshold_key"] == "entry_quality_tpe_smc_zone_threshold"


class TestOnlyRepairsShipEnforcing:
    """The rule set's defaults are an argument, so they are pinned as one.

    #849 tested nineteen cells on 46 closed signals against a ~62% familywise
    chance of a spurious hit; that window cannot choose a threshold. A rule
    ships live only when enforcing it invents no number — ``profile_reject``
    applies thresholds ``_pass_basic_filters`` already computes. ``tpe_smc_zone``
    knows the repair and not the number, so it ships in shadow.
    """

    def test_profile_reject_ships_live_and_needs_no_threshold(self):
        rule = eq.RULES_BY_KEY["profile_reject"]
        assert rule.live_default is True
        assert rule.compare == eq.CMP_FLAG

    def test_the_rule_whose_threshold_is_a_judgement_ships_in_shadow(self):
        assert eq.RULES_BY_KEY["tpe_smc_zone"].live_default is False

    def test_the_rule_set_stays_small(self):
        """Twelve rules is twelve thresholds against a book this size, which
        guarantees a spurious winner. The ops now-vs-later page is where
        thresholds are explored; a rule arrives here to be enforced."""
        assert len(eq.RULES) <= 4

    def test_every_rule_names_a_defect_in_code_rather_than_a_measured_delta(self):
        for rule in eq.RULES:
            assert rule.rationale.strip(), f"{rule.key} has no rationale"
            assert rule.feature, f"{rule.key} names no feature"


# --------------------------------------------------------------------------- #
# The seam the scanner actually drives
# --------------------------------------------------------------------------- #


class TestTheScannerSeam:
    """Driven with the real collaborators, in the real order.

    A mock whose keys we chose cannot verify a contract we got wrong — it
    asserts our assumption back at us and goes green over dead code
    (``CLAUDE.md``, #798). So this drives ``entry_features.stamp`` →
    ``row_for`` → ``decide`` → ``annotate`` exactly as the gate does, against a
    signal object of the shape the evaluator returns.
    """

    class _Sig:
        def __init__(self, sid: str, setup: str) -> None:
            self.signal_id = sid
            self.setup_class = setup
            self.confidence = 71.0
            self.entry_regime = ""

    def test_a_stamp_made_in_the_evaluator_is_found_by_the_gate_later(self):
        led = ef.EntryFeatureLedger(path="")
        ef.reset_ledger(led)
        try:
            sig = self._Sig("sig-1", "MOVER_TREND_PULLBACK")
            assert ef.stamp(sig, {"profile_would_reject": True}, regime="TRENDING_UP")

            # Exactly what the scanner does, one line at a time.
            row = ef.get_ledger().row_for(sig.signal_id)
            assert row is not None
            decision = eq.evaluate(
                row, sig.setup_class, _params(rules=(_rule("profile_reject", live=True),))
            )
            assert decision.enforced_by == "profile_reject"
            assert ef.get_ledger().annotate(sig.signal_id, decision.as_row())

            stored = ef.get_ledger().rows()[0]
            assert stored["eq_enforced_by"] == "profile_reject"
            assert stored["eq_rules"][0]["feature"] == "profile_would_reject"
        finally:
            ef.reset_ledger(None)

    def test_a_signal_the_lane_never_stamped_leaves_the_gate_inert(self):
        """Not a crash and not a rejection — the gate has nothing to read, says
        so, and the candidate proceeds."""
        led = ef.EntryFeatureLedger(path="")
        ef.reset_ledger(led)
        try:
            row = ef.get_ledger().row_for("never-stamped")
            d = eq.evaluate(row, "MOVER_TREND_PULLBACK", _params())
            assert d.evaluated is False and d.reason == "no_stamp"
            assert d.suppressed is False
        finally:
            ef.reset_ledger(None)


class TestTheGateIsWiredWhereItClaimsToBe:
    """Placement is part of the claim, so it is pinned rather than commented.

    The gate's counter only means "signals this gate cost us" if it runs after
    the confidence floor. Run it earlier and it starts killing candidates that
    were dying anyway, and the shadow population stops being the emitting book —
    which is the only population a promotion may read.
    """

    @staticmethod
    def _scanner_source() -> str:
        import inspect

        from src.scanner import Scanner

        return inspect.getsource(Scanner._prepare_signal)

    def test_it_runs_after_the_confidence_floor(self):
        src = self._scanner_source()
        assert "ENTRY QUALITY" in src, "the gate is not in _prepare_signal at all"
        assert src.index("_stamp_suppressed(sig, _reason)") < src.index("ENTRY QUALITY"), (
            "entry_quality runs before the confidence floor — its rejections "
            "would no longer be candidates that would otherwise have emitted"
        )

    def test_a_live_rejection_stamps_the_suppression_audit(self):
        """Every live gate stamps, no exceptions — and this one needs it most,
        because an enforcing entry rule starves its own evidence."""
        src = self._scanner_source()
        tail = src[src.index("ENTRY QUALITY"):]
        assert 'self._stamp_suppressed(sig, f"entry_quality:' in tail
        assert "REASON_ENTRY_QUALITY" in tail

    def test_the_gate_cannot_kill_a_scan(self):
        """A measurement lane must never be the reason a scan dies, and the
        failure is counted rather than swallowed."""
        src = self._scanner_source()
        tail = src[src.index("ENTRY QUALITY"):]
        assert 'fail_open.record("scanner.entry_quality"' in tail

    def test_it_has_its_own_suppression_reason(self):
        """Folded into another gate's bucket it could not be ranked apart from
        it in the audit — which is the only way it earns or loses its place."""
        from src.suppression_telemetry import REASON_ENTRY_QUALITY

        assert REASON_ENTRY_QUALITY == "entry_quality"
