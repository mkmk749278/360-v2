"""Dark → live promotion: the conditions, the fail-closed defaults, the wiring.

The tests that matter here are the ones about **refusing**. Promotion is the
one mechanism in this repo that deliberately moves rows from a lane that
reaches nobody into a feed paid subscribers read, so most of its surface area
is the set of circumstances under which it must decline — and every one of
those is a silent failure if it regresses, because a promoted signal looks
exactly like an ordinary one everywhere downstream.

Two things are pinned structurally rather than by value:

* the divert site's AST, so a refactor cannot drop the promotion branch or —
  much worse — reorder it so a marked candidate reaches ``signal_queue.put``
  without a decision (``test_divert_site_*``);
* the ledger's additive-schema declaration, because this change bumps
  ``LEDGER_SCHEMA`` and the last additive bump in this repo destroyed 371 rows
  by declaring nothing.
"""
from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from src import dark_emission, dark_promotion


class _Sig:
    """A candidate shaped like the real thing at the divert site."""

    def __init__(
        self,
        setup_class="LIQUIDITY_SWEEP_REVERSAL",
        side="SHORT",
        regime="TRENDING_DOWN",
        regime_15m="",
        session="NY",
        confidence=70.0,
        symbol="AAAUSDT",
    ):
        self.setup_class = setup_class
        self.direction = type("D", (), {"value": side})()
        self.entry_regime = regime
        self.entry_regime_15m = regime_15m
        self.mc_session = session
        self.mc_context_key = f"{session}/MARKDOWN/NORMAL/BTC_NEUTRAL"
        self.confidence = confidence
        self.symbol = symbol
        self.signal_id = f"SIG-{symbol}-{side}"
        self.channel = "360_SCALP"
        self.entry = 100.0
        self.stop_loss = 103.0
        self.tp1 = 97.0
        self.tp2 = 95.0
        self.tp3 = 92.0
        self.valid_for_minutes = 60.0
        self.pair_admission = "CORE"


@pytest.fixture(autouse=True)
def _isolated_registry(tmp_path, monkeypatch):
    dark_promotion.reset_for_test(str(tmp_path / "promotions.json"))
    monkeypatch.setattr(dark_promotion, "master_enabled", lambda: True)
    yield
    dark_promotion.reset_for_test("data/dark_promotions_v1.json")


def _lsr_rule(**over):
    kwargs = dict(
        setup_class="LIQUIDITY_SWEEP_REVERSAL",
        enabled=True,
        gates=["SETUP_COMPAT:REGIME_STRONG_TREND", "EXECUTION:OVEREXTENDED"],
        regimes=[dark_promotion.ANY],
        sessions=[dark_promotion.ANY],
        direction=dark_promotion.DIR_WITH_TREND,
        max_per_day=25,
    )
    kwargs.update(over)
    return dark_promotion.PromotionRule(**kwargs)


# --------------------------------------------------------------------------- #
# Fail-closed: every way this must decline
# --------------------------------------------------------------------------- #


def test_no_rule_means_no_promotion():
    d = dark_promotion.decide(_Sig(), "setup_compat:regime_STRONG_TREND")
    assert d.promote is False
    assert dark_promotion.DIM_NO_RULE in d.unmet


def test_master_switch_off_overrides_every_enabled_rule(monkeypatch):
    dark_promotion.set_rule(_lsr_rule())
    monkeypatch.setattr(dark_promotion, "master_enabled", lambda: False)
    d = dark_promotion.decide(_Sig(), "setup_compat:regime_STRONG_TREND")
    assert d.promote is False
    assert d.unmet == [dark_promotion.DIM_MASTER]


def test_rule_disabled_means_no_promotion():
    dark_promotion.set_rule(_lsr_rule(enabled=False))
    d = dark_promotion.decide(_Sig(), "setup_compat:regime_STRONG_TREND")
    assert d.promote is False
    assert dark_promotion.DIM_RULE in d.unmet


def test_empty_dimension_matches_nothing_rather_than_everything():
    """An unfilled allow-list is inert, not permissive.

    The single most dangerous plausible reading of this config. A rule saved
    with no gates chosen must promote nothing at all — the opposite convention
    would make a half-finished form a live promotion of the whole path.
    """
    rule = dark_promotion.set_rule(_lsr_rule(gates=[]))
    assert rule.inert is True
    d = dark_promotion.decide(_Sig(), "setup_compat:regime_STRONG_TREND")
    assert d.promote is False
    assert dark_promotion.DIM_GATE in d.unmet


def test_wildcard_is_explicit_and_does_match():
    dark_promotion.set_rule(_lsr_rule(gates=[dark_promotion.ANY]))
    d = dark_promotion.decide(_Sig(), "execution:trigger_not_confirmed")
    assert d.promote is True


def test_gate_not_in_the_allow_list_stays_dark():
    """The rule this repo's own LSR reading turns on.

    ``trigger_not_confirmed`` measured +0.192% on 8 rows with a CI straddling
    zero, against +1.354% on 20 for the STRONG_TREND gate. Promoting per gate
    rather than per path is the whole point of the gate dimension, so a rule
    naming two gates must leave the third exactly where it was.
    """
    dark_promotion.set_rule(_lsr_rule())
    assert dark_promotion.decide(
        _Sig(), "execution:trigger_not_confirmed"
    ).promote is False
    assert dark_promotion.decide(
        _Sig(), "setup_compat:regime_STRONG_TREND"
    ).promote is True


def test_decide_never_raises_and_answers_no_on_a_broken_signal():
    dark_promotion.set_rule(_lsr_rule())

    class _Exploding:
        setup_class = "LIQUIDITY_SWEEP_REVERSAL"

        @property
        def entry_regime(self):
            raise RuntimeError("boom")

    d = dark_promotion.decide(_Exploding(), "setup_compat:regime_STRONG_TREND")
    assert d.promote is False


# --------------------------------------------------------------------------- #
# Direction alignment — the condition this mechanism exists for
# --------------------------------------------------------------------------- #


def test_with_trend_admits_a_short_in_a_downtrend():
    dark_promotion.set_rule(_lsr_rule())
    d = dark_promotion.decide(
        _Sig(side="SHORT", regime="TRENDING_DOWN"),
        "setup_compat:regime_STRONG_TREND",
    )
    assert d.promote is True


def test_with_trend_refuses_the_counter_trend_case_the_doctrine_protects():
    """A sweep-reversal SHORT into an uptrend is the setup's known failure mode.

    `REGIME_SETUP_COMPATIBILITY` excludes LSR from STRONG_TREND for this case
    and cannot express the distinction, because it blocks the setup class and
    not the direction. This is the half of the gate that must survive the
    promotion — and there is no measured evidence for it either way, which is
    exactly why it stays refused.
    """
    dark_promotion.set_rule(_lsr_rule())
    d = dark_promotion.decide(
        _Sig(side="SHORT", regime="TRENDING_UP"),
        "setup_compat:regime_STRONG_TREND",
    )
    assert d.promote is False
    assert dark_promotion.DIM_DIRECTION in d.unmet


def test_unknown_trend_abstains_rather_than_assuming_alignment():
    dark_promotion.set_rule(_lsr_rule())
    d = dark_promotion.decide(
        _Sig(side="SHORT", regime="RANGING"),
        "setup_compat:regime_STRONG_TREND",
    )
    assert d.promote is False
    assert d.detail == "trend_unknown"


def test_15m_regime_is_a_fallback_for_a_range_label_not_an_override():
    dark_promotion.set_rule(_lsr_rule())
    # 5m says nothing about trend, 15m does → the fallback answers.
    assert dark_promotion.decide(
        _Sig(side="SHORT", regime="RANGING", regime_15m="TRENDING_DOWN"),
        "setup_compat:regime_STRONG_TREND",
    ).promote is True
    # 5m names a trend → the 15m read must not override it.
    assert dark_promotion.decide(
        _Sig(side="SHORT", regime="TRENDING_UP", regime_15m="TRENDING_DOWN"),
        "setup_compat:regime_STRONG_TREND",
    ).promote is False


def test_trend_of_survives_a_label_the_detector_has_not_taught_us():
    assert dark_promotion.trend_of("WYCKOFF_MARKDOWN") == "DOWN"
    assert dark_promotion.trend_of("STRONG_BULL_EXPANSION") == "UP"
    assert dark_promotion.trend_of("CLEAN_RANGE") is None
    assert dark_promotion.trend_of("") is None


def test_counter_trend_is_its_own_condition_not_the_absence_of_with_trend():
    dark_promotion.set_rule(_lsr_rule(direction=dark_promotion.DIR_COUNTER_TREND))
    assert dark_promotion.decide(
        _Sig(side="SHORT", regime="TRENDING_UP"), "execution:overextended"
    ).promote is True
    assert dark_promotion.decide(
        _Sig(side="SHORT", regime="TRENDING_DOWN"), "execution:overextended"
    ).promote is False
    # …and an unknown trend still abstains, on both conditions.
    assert dark_promotion.decide(
        _Sig(side="SHORT", regime="RANGING"), "execution:overextended"
    ).promote is False


# --------------------------------------------------------------------------- #
# The other dimensions
# --------------------------------------------------------------------------- #


def test_regime_and_session_narrow_the_rule():
    dark_promotion.set_rule(
        _lsr_rule(regimes=["TRENDING_DOWN"], sessions=["NY", "OVERLAP"])
    )
    assert dark_promotion.decide(
        _Sig(session="NY"), "execution:overextended"
    ).promote is True
    assert dark_promotion.decide(
        _Sig(session="ASIA"), "execution:overextended"
    ).promote is False


def test_unmet_lists_every_failed_dimension_not_just_the_first():
    """An owner debugging a rule needs the whole answer in one read."""
    dark_promotion.set_rule(
        _lsr_rule(regimes=["TRENDING_UP"], sessions=["ASIA"], min_confidence=90.0)
    )
    d = dark_promotion.decide(
        _Sig(session="NY", regime="TRENDING_DOWN", confidence=70.0),
        "execution:overextended",
    )
    assert d.promote is False
    assert set(d.unmet) >= {
        dark_promotion.DIM_REGIME,
        dark_promotion.DIM_SESSION,
        dark_promotion.DIM_CONFIDENCE,
    }
    assert dark_promotion.DIM_GATE in d.matched


def test_min_confidence_is_optional_and_absent_means_unfiltered():
    dark_promotion.set_rule(_lsr_rule(min_confidence=None))
    assert dark_promotion.decide(
        _Sig(confidence=1.0), "execution:overextended"
    ).promote is True


# --------------------------------------------------------------------------- #
# Blast radius
# --------------------------------------------------------------------------- #


def test_daily_cap_bounds_a_rule_and_is_counted_apart_from_a_miss():
    dark_promotion.set_rule(_lsr_rule(max_per_day=2))
    for _ in range(2):
        d = dark_promotion.decide(_Sig(), "execution:overextended")
        assert d.promote is True
        dark_promotion.note_promoted("LIQUIDITY_SWEEP_REVERSAL")
    d = dark_promotion.decide(_Sig(), "execution:overextended")
    assert d.promote is False
    # Named apart from a condition miss: this candidate MATCHED the rule, which
    # is a different finding from one that did not, and pooling them hides a
    # rule running at its bound behind a rule that never fires.
    assert d.unmet == [dark_promotion.DIM_CAP]
    assert dark_promotion.DIM_GATE in d.matched


def test_cap_is_charged_by_the_caller_not_by_deciding():
    """A decision the caller does not act on must not spend budget."""
    dark_promotion.set_rule(_lsr_rule(max_per_day=1))
    for _ in range(5):
        assert dark_promotion.decide(_Sig(), "execution:overextended").promote is True
    assert dark_promotion.promoted_today("LIQUIDITY_SWEEP_REVERSAL") == 0


# --------------------------------------------------------------------------- #
# Storage
# --------------------------------------------------------------------------- #


def test_set_rule_returns_what_is_stored_not_what_was_asked_for():
    stored = dark_promotion.set_rule(
        _lsr_rule(direction="nonsense", gates=["execution:overextended"], max_per_day=-4)
    )
    assert stored.direction == dark_promotion.DIR_ANY
    assert stored.gates == ["EXECUTION:OVEREXTENDED"]
    assert stored.max_per_day == 0


def test_rules_round_trip_through_disk(tmp_path):
    dark_promotion.set_rule(_lsr_rule(note="promoted on the 43-row window"))
    path = Path(dark_promotion.REGISTRY_PATH)
    assert path.exists()
    payload = json.loads(path.read_text())
    assert payload["schema"] == dark_promotion.REGISTRY_SCHEMA

    dark_promotion.reset_for_test(str(path))
    reloaded = dark_promotion.get_rule("LIQUIDITY_SWEEP_REVERSAL")
    assert reloaded is not None
    assert reloaded.enabled is True
    assert reloaded.note == "promoted on the 43-row window"
    assert reloaded.direction == dark_promotion.DIR_WITH_TREND


def test_a_newer_registry_schema_is_refused_rather_than_guessed(tmp_path):
    path = tmp_path / "future.json"
    path.write_text(json.dumps({
        "schema": dark_promotion.REGISTRY_SCHEMA + 1,
        "rules": [_lsr_rule().normalised().to_dict()],
    }))
    dark_promotion.reset_for_test(str(path))
    assert dark_promotion.all_rules() == []


def test_generation_bumps_on_every_write():
    before = dark_promotion.generation()
    dark_promotion.set_rule(_lsr_rule())
    assert dark_promotion.generation() > before


def test_delete_removes_the_rule():
    dark_promotion.set_rule(_lsr_rule())
    assert dark_promotion.delete_rule("liquidity_sweep_reversal") is True
    assert dark_promotion.get_rule("LIQUIDITY_SWEEP_REVERSAL") is None
    assert dark_promotion.delete_rule("LIQUIDITY_SWEEP_REVERSAL") is False


# --------------------------------------------------------------------------- #
# The ledger side: measurement continues, and delivery is not enqueue
# --------------------------------------------------------------------------- #


@pytest.fixture
def ledger():
    led = dark_emission.DarkLedger(path="")
    dark_emission.reset_ledger(led)
    yield led
    dark_emission.reset_ledger(None)


def test_a_promoted_row_is_still_written_to_the_dark_ledger(ledger):
    """The measurement does not stop when the rule goes live.

    The whole design rests on this: if promotion ended the stamping, the
    evidence for the decision would freeze at the moment it was taken and
    could never be re-read on fresh rows.
    """
    dark_promotion.set_rule(_lsr_rule())
    sig = _Sig()
    decision = dark_promotion.decide(sig, "execution:overextended")
    sig.dark_gate = "execution:overextended"
    assert dark_emission.publish(sig, promotion=decision) is True

    row = ledger.rows()[0]
    assert row["promoted"] is True
    assert row["delivery"] == dark_emission.DELIVERY_ENQUEUED
    # It is still a fully-formed measurement row, walked by the same resolver.
    assert row["status"] == dark_emission.STATUS_OPEN
    assert row["sl_distance_pct"] == pytest.approx(3.0)


def test_an_ordinary_dark_row_is_unchanged_and_says_so(ledger):
    sig = _Sig()
    sig.dark_gate = "execution:overextended"
    dark_emission.publish(sig)
    row = ledger.rows()[0]
    assert row["promoted"] is False
    assert row["delivery"] == dark_emission.DELIVERY_DARK
    assert row["delivered_at"] is None


def test_enqueued_is_not_delivered_until_the_router_says_so(ledger):
    dark_promotion.set_rule(_lsr_rule())
    sig = _Sig()
    sig.dark_gate = "execution:overextended"
    dark_emission.publish(
        sig, promotion=dark_promotion.decide(sig, "execution:overextended")
    )
    assert ledger.rows()[0]["delivery"] == dark_emission.DELIVERY_ENQUEUED

    assert dark_emission.mark_delivered(sig.signal_id) is True
    row = ledger.rows()[0]
    assert row["delivery"] == dark_emission.DELIVERY_DELIVERED
    assert row["delivered_at"] is not None


def test_a_router_drop_records_the_reason_not_just_the_fact(ledger):
    dark_promotion.set_rule(_lsr_rule())
    sig = _Sig()
    sig.dark_gate = "execution:overextended"
    dark_emission.publish(
        sig, promotion=dark_promotion.decide(sig, "execution:overextended")
    )
    assert dark_emission.mark_router_dropped(sig.signal_id, "correlation_lock") is True
    row = ledger.rows()[0]
    assert row["delivery"] == dark_emission.DELIVERY_DROPPED
    assert row["router_drop_reason"] == "correlation_lock"


def test_delivery_stamps_refuse_a_row_that_was_never_promoted(ledger):
    """`delivery` must be a fact about this row, not a coincidence of ids."""
    sig = _Sig()
    sig.dark_gate = "execution:overextended"
    dark_emission.publish(sig)
    assert dark_emission.mark_delivered(sig.signal_id) is False
    assert ledger.rows()[0]["delivery"] == dark_emission.DELIVERY_DARK


def test_delivery_stamp_on_an_unknown_id_is_a_no_op(ledger):
    assert dark_emission.mark_delivered("SIG-NOT-HERE") is False
    assert dark_emission.mark_delivered("") is False


# --------------------------------------------------------------------------- #
# The schema bump — declared additive, and it had better be
# --------------------------------------------------------------------------- #


def test_every_earlier_schema_is_declared_additive():
    """The bump that added the promotion block must not destroy the window.

    Every row that argues FOR a promotion was written under schema 1. Dropping
    them on the first flush after deploy — which is what a bare `!=` loader
    does, and what cost this repo 371 SAR arms on 2026-08-09 — would delete the
    evidence at exactly the moment it starts being used.

    This pins the PROPERTY, not the number. The first cut asserted
    ``LEDGER_SCHEMA == 2``, which is an assertion about today rather than about
    the invariant, and it failed on the next additive bump for a reason that
    had nothing to do with what it protects — the reader's cheapest response
    being to bump the literal and move on, which is how a guard becomes a
    formality.

    Every bump so far has been additive, so every earlier schema must be
    listed. A bump that genuinely REDEFINES a field is the one case where
    dropping old rows is right — old and new rows would then disagree about
    what a column *is* — and it must edit this test deliberately, with the
    reasoning written down, rather than being waved through.
    """
    assert dark_emission.ADDITIVE_FROM_SCHEMAS == frozenset(
        range(1, dark_emission.LEDGER_SCHEMA)
    ), (
        "every schema before the current one is additive and must be readable; "
        "if a bump redefined a field, change this test and say which field and "
        "why the old rows no longer mean what they say"
    )


def test_a_schema_one_ledger_still_loads_and_keeps_its_rows(tmp_path, monkeypatch):
    """A real schema-1 file, written by the real serializer, must survive.

    Deliberately NOT a hand-built envelope. The first cut of this test wrote
    ``{"schema": 1, "paths": {...}}`` — a shape nothing has ever produced, and
    it failed for that reason rather than for the reason it was testing. A
    fixture chooses a shape and then agrees with you about it; the only way to
    know a schema-1 ledger loads is to make one the way the engine makes one.
    """
    path = tmp_path / "dark_v1.json"

    monkeypatch.setattr(dark_emission, "LEDGER_SCHEMA", 1)
    writer = dark_emission.DarkLedger(path=str(path))
    old = _Sig(symbol="OLDUSDT")
    old.dark_gate = "execution:overextended"
    dark_emission.reset_ledger(writer)
    assert dark_emission.publish(old) is True
    assert writer.flush() is True
    monkeypatch.undo()
    dark_emission.reset_ledger(None)

    payload = json.loads(path.read_text())
    assert payload["schema"] == 1

    # Today's builder still writes the block, so strip it to get the row an
    # older BUILD would have produced. Derived from PROMOTION_FIELDS rather
    # than typed out, so the next field added is covered without editing this.
    for key in dark_emission.PROMOTION_FIELDS:
        payload["rows"][0].pop(key, None)
    path.write_text(json.dumps(payload))

    reader = dark_emission.DarkLedger(path=str(path))
    reader.load()
    rows = reader.rows()
    assert [r["signal_id"] for r in rows] == [old.signal_id], (
        "an additive bump dropped its own window — the 2026-08-09 defect"
    )
    # A pre-promotion row carries no block at all, which readers render as its
    # own bucket. `.get` returning None is the point: absent is not `False`,
    # because "this row was not promoted" and "this row predates promotion"
    # are different populations.
    assert rows[0].get("delivery") is None
    assert rows[0].get("promoted") is None


def test_promotion_fields_are_named_once():
    """The row builder and every reader agree by construction, not by memory."""
    sig = _Sig()
    sig.dark_gate = "execution:overextended"
    row = dark_emission._row_from_signal(sig, 1_786_000_000.0)
    for key in dark_emission.PROMOTION_FIELDS:
        assert key in row, f"{key} declared in PROMOTION_FIELDS but not written"


# --------------------------------------------------------------------------- #
# Wiring — pin the call site, not the import
# --------------------------------------------------------------------------- #


def _enqueue_ast():
    src = Path("src/scanner/__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_enqueue_signal":
            return node
    raise AssertionError("Scanner._enqueue_signal not found")


def test_divert_site_consults_the_promotion_decision():
    """A rule the scanner never asks about is a control panel wired to nothing.

    Pins the CALL, not the import: `src/dark_promotion.py` imported and never
    consulted is the shape this repo has paid for repeatedly (a dead parameter
    under a docstring claiming it is shared, a flush with no caller).
    """
    calls = [
        n for n in ast.walk(_enqueue_ast())
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "decide"
        and isinstance(n.func.value, ast.Name)
        and n.func.value.id == "dark_promotion"
    ]
    assert calls, "the divert site does not call dark_promotion.decide"


def test_divert_site_still_publishes_every_diverted_candidate():
    """Both branches write a ledger row — promoted and not.

    If a refactor kept the promotion branch and dropped the row it writes, the
    lane would keep working and silently stop measuring exactly the population
    an ongoing promotion decision reads.
    """
    publishes = [
        n for n in ast.walk(_enqueue_ast())
        if isinstance(n, ast.Call)
        and isinstance(n.func, ast.Attribute)
        and n.func.attr == "publish"
        and isinstance(n.func.value, ast.Name)
        and n.func.value.id == "dark_emission"
    ]
    assert len(publishes) == 2, (
        "expected exactly two dark_emission.publish calls at the divert site — "
        "one for the promoted branch, one for the diverted branch"
    )
    assert any(
        any(kw.arg == "promotion" for kw in call.keywords) for call in publishes
    ), "the promoted branch must pass its decision to publish()"


def test_router_stamps_both_halves_of_the_delivery_verdict():
    """Enqueue is not dispatch, and only the router closes that gap."""
    src = Path("src/signal_router.py").read_text(encoding="utf-8")
    assert "mark_delivered" in src, "the router never confirms a promoted delivery"
    assert "mark_router_dropped" in src, "the router never records a promoted drop"


# --------------------------------------------------------------------------- #
# The refusal census — which condition is actually saying no
#
# Added 2026-08-17, after the owner asked why no LSR row had ever reached a
# subscriber.  Two armed rules, master switch on, dark lane on, neither inert,
# 610 diverted LIQUIDITY_SWEEP_REVERSAL candidates in the truth-report window —
# and `0 promoted today` was the entire diagnostic available, in the engine and
# on the ops page alike.  `decide` had computed the full `unmet` list the whole
# time, exactly as this module's docstring promised, and every caller discarded
# it.
# --------------------------------------------------------------------------- #


def test_a_refusal_names_its_dimension_rather_than_incrementing_one_total():
    """The property the module docstring has always claimed.

    Fails against the pre-2026-08-17 tree, where the only counter was
    `unmet:{setup_class}` — one integer over five dimensions.
    """
    dark_promotion.set_rule(_lsr_rule(regimes=["TRENDING_UP"]))
    dark_promotion.decide(_Sig(regime="TRENDING_DOWN"), "execution:overextended")

    cell = dark_promotion.runtime_report()["refusals"]["LIQUIDITY_SWEEP_REVERSAL"]
    assert cell["total"] == 1
    assert cell["by_dimension"] == {dark_promotion.DIM_REGIME: 1}, (
        "the census must name the dimension that refused, not just count refusals"
    )


def test_sole_blocker_is_counted_apart_from_the_marginal_count():
    """A rule is a conjunction, so the two numbers answer different questions.

    `by_dimension` says how often a condition failed at all and deliberately
    sums past the refusal count; `sole_blocker` says how often it was the only
    thing in the way — the number that says what one edit would unlock. The ops
    panel offers its evidence one dimension at a time while the rule it builds
    is an intersection, which is exactly how a well-evidenced-looking rule ends
    up selecting nothing.
    """
    # `direction=any` so the only conditions in play are the two under test —
    # a with_trend rule would ALSO refuse the TRENDING_UP/SHORT candidate below
    # and there would be no sole blocker to observe. (That is not a hypothetical:
    # the first cut of this test asserted one and was wrong.)
    dark_promotion.set_rule(
        _lsr_rule(
            regimes=["TRENDING_UP"],
            sessions=["LONDON"],
            direction=dark_promotion.DIR_ANY,
        )
    )
    # Fails regime AND session — no single edit fixes it.
    dark_promotion.decide(
        _Sig(regime="TRENDING_DOWN", session="NY"), "execution:overextended"
    )
    # Fails session only.
    dark_promotion.decide(
        _Sig(regime="TRENDING_UP", session="NY"), "execution:overextended"
    )

    cell = dark_promotion.runtime_report()["refusals"]["LIQUIDITY_SWEEP_REVERSAL"]
    assert cell["total"] == 2
    assert cell["by_dimension"][dark_promotion.DIM_SESSION] == 2
    assert cell["by_dimension"][dark_promotion.DIM_REGIME] == 1
    assert cell["sole_blocker"] == {dark_promotion.DIM_SESSION: 1}, (
        "only the second candidate had a single condition standing in its way"
    )


def test_the_cap_is_a_refusal_dimension_and_never_pooled_with_a_miss():
    """A rule at its bound is working and throttled; a rule that never matches
    is misconfigured. The cap check is last precisely so the two stay apart."""
    dark_promotion.set_rule(_lsr_rule(max_per_day=1))
    assert dark_promotion.decide(_Sig(), "execution:overextended").promote
    dark_promotion.note_promoted("LIQUIDITY_SWEEP_REVERSAL")
    d = dark_promotion.decide(_Sig(), "execution:overextended")
    assert not d.promote

    cell = dark_promotion.runtime_report()["refusals"]["LIQUIDITY_SWEEP_REVERSAL"]
    assert cell["sole_blocker"] == {dark_promotion.DIM_CAP: 1}
    assert dark_promotion.DIM_REGIME not in cell["by_dimension"]


def test_a_near_miss_records_the_observed_values_not_the_rule():
    """The owner is comparing what he asked for against what the engine
    stamped, and only one of those is already on his screen."""
    dark_promotion.set_rule(_lsr_rule(direction=dark_promotion.DIR_WITH_TREND))
    dark_promotion.decide(
        _Sig(side="SHORT", regime="RANGING", session="ASIA", symbol="ZZZUSDT"),
        "execution:overextended",
    )
    sample = dark_promotion.runtime_report()["near_misses"][-1]
    assert sample["symbol"] == "ZZZUSDT"
    assert sample["regime"] == "RANGING"
    assert sample["session"] == "ASIA"
    assert sample["side"] == "SHORT"
    assert dark_promotion.DIM_DIRECTION in sample["unmet"]
    assert "trend_unknown" in sample["detail"], (
        "a with_trend rule against a range label abstains, and the row says so"
    )


def test_the_near_miss_ring_publishes_its_own_denominator():
    """A capped buffer feeding a statistic must say what it is a sample of."""
    dark_promotion.set_rule(_lsr_rule(regimes=["TRENDING_UP"]))
    for i in range(dark_promotion.NEAR_MISS_RING + 7):
        dark_promotion.decide(
            _Sig(regime="TRENDING_DOWN", symbol=f"S{i}USDT"),
            "execution:overextended",
        )
    report = dark_promotion.runtime_report()
    assert len(report["near_misses"]) == dark_promotion.NEAR_MISS_RING
    assert report["near_miss_seen"] == dark_promotion.NEAR_MISS_RING + 7, (
        "the unbounded count must sit beside the ring, or the newest few read "
        "as the whole population"
    )


def test_top_blocker_distinguishes_no_candidates_from_every_candidate_refused():
    """Two states, one of which is benign, and they must not share a caption.

    This is the sentence the liveness probe prints. Before the census it read
    `0 promoted today` for both, and the probe's own docstring called that
    'the market has not offered a candidate matching it' — a claim nobody
    could check.
    """
    dark_promotion.set_rule(_lsr_rule(regimes=["TRENDING_UP"]))
    assert dark_promotion.top_blocker(["LIQUIDITY_SWEEP_REVERSAL"]) == "", (
        "nothing has been refused yet — that is not the same as being blocked"
    )
    dark_promotion.decide(_Sig(regime="TRENDING_DOWN"), "execution:overextended")
    msg = dark_promotion.top_blocker(["LIQUIDITY_SWEEP_REVERSAL"])
    assert dark_promotion.DIM_REGIME in msg and "1 candidate(s) refused" in msg


def test_top_blocker_says_so_when_no_single_edit_would_help():
    dark_promotion.set_rule(
        _lsr_rule(
            regimes=["TRENDING_UP"],
            sessions=["LONDON"],
            direction=dark_promotion.DIR_ANY,
        )
    )
    dark_promotion.decide(
        _Sig(regime="TRENDING_DOWN", session="NY"), "execution:overextended"
    )
    assert "none on one condition alone" in dark_promotion.top_blocker(
        ["LIQUIDITY_SWEEP_REVERSAL"]
    )


def test_a_promotion_is_never_recorded_as_a_refusal():
    dark_promotion.set_rule(_lsr_rule())
    assert dark_promotion.decide(_Sig(), "execution:overextended").promote
    assert dark_promotion.runtime_report()["refusals"] == {}


def test_the_census_covers_every_dimension_decide_can_refuse_on():
    """Derived from the DIM_* constants, so a dimension added to the rule
    cannot be silently absent from the census that explains it."""
    import re

    src = Path("src/dark_promotion.py").read_text(encoding="utf-8")
    declared = {
        name for name in re.findall(r"^(DIM_[A-Z_]+) = ", src, re.MULTILINE)
    }
    # The three that are not conditions on a candidate: they describe the
    # absence of a rule to evaluate, so there is nothing to attribute.
    not_conditions = {"DIM_MASTER", "DIM_RULE", "DIM_NO_RULE"}
    expected = {
        getattr(dark_promotion, name) for name in declared - not_conditions
    }
    assert set(dark_promotion.REFUSAL_DIMENSIONS) == expected


# --------------------------------------------------------------------------- #
# Which process holds the state
# --------------------------------------------------------------------------- #


def test_runtime_block_is_separable_so_the_api_container_can_be_overlaid():
    """`decide` runs in the engine container; the ops panel is served by the
    API one. A snapshot built there loads the rules correctly off the shared
    volume and reports every runtime number as zero — which is also what a
    correctly-armed rule reads before it fires, so the wrong answer and the
    right one are the same number until the rule works.
    """
    dark_promotion.set_rule(_lsr_rule())
    dark_promotion.note_promoted("LIQUIDITY_SWEEP_REVERSAL")

    engine_runtime = dark_promotion.runtime_report()
    assert engine_runtime["promoted_today"]["LIQUIDITY_SWEEP_REVERSAL"] == 1
    assert engine_runtime["source"] == "engine"

    # A second process: same registry file, no decisions ever evaluated.
    dark_promotion.reset_for_test()
    dark_promotion.set_rule(_lsr_rule())
    cold = dark_promotion.snapshot()
    assert cold["rules"][0]["promoted_today"] == 0

    warm = dark_promotion.apply_runtime(cold, engine_runtime)
    assert warm["rules"][0]["promoted_today"] == 1
    assert warm["runtime"]["source"] == "engine"


def test_a_missing_published_block_leaves_the_snapshot_alone():
    """"The engine has not published" and "nothing has been promoted" are
    different states, and blanking the snapshot would merge them."""
    dark_promotion.set_rule(_lsr_rule())
    snap = dark_promotion.snapshot()
    assert dark_promotion.apply_runtime(snap, None)["runtime"]["source"] == "engine"
    assert dark_promotion.apply_runtime(snap, {})["runtime"]["source"] == "engine"


def test_the_api_route_prefers_the_engines_published_runtime_block():
    """Pin the call site, not the method. The handler must consult the facade
    — a local build in the API container is the `INDEX COLD` defect again.
    """
    src = Path("src/api/dark_promotion_routes.py").read_text(encoding="utf-8")
    assert "published_dark_promotion" in src, (
        "the read handler must consult the engine's published runtime block"
    )
    assert "apply_runtime" in src


def test_the_engine_publishes_the_runtime_block_every_cycle():
    """Defining a writer is not calling it — pin the caller."""
    writer = Path("src/api/snapshot_writer.py").read_text(encoding="utf-8")
    assert "_write_dark_promotion" in writer
    tree = ast.parse(writer)
    cycle = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "_write_cycle"
    )
    called = {
        n.func.attr for n in ast.walk(cycle)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    assert "_write_dark_promotion" in called, (
        "the runtime block is built and never published — the API container "
        "would keep reading its own zeros"
    )


def test_runtime_report_is_safe_against_the_writer_it_reads_from():
    """`decide` runs on the scanner's event loop; `runtime_report` is called
    from the snapshot writer's THREAD POOL.

    The reader iterates dicts the writer is inserting into, so an unguarded
    implementation raises "dictionary changed size during iteration" — and the
    only symptom in production would be the block quietly failing to publish,
    which is precisely the silence this census exists to end.

    Each candidate carries a DIFFERENT setup_class, because that is what makes
    `_refusals` grow while it is being read. Pinning the race needs the
    dictionary to resize mid-iteration; a single-key churn cannot fail however
    long it runs, which is what the first cut of this test got wrong.
    """
    import threading

    for i in range(200):
        dark_promotion.set_rule(
            _lsr_rule(setup_class=f"PATH_{i}", regimes=["TRENDING_UP"])
        )

    errors = []
    stop = threading.Event()

    def _read():
        try:
            while not stop.is_set():
                report = dark_promotion.runtime_report()
                for cell in report["refusals"].values():
                    dict(cell["by_dimension"])
                    dict(cell["sole_blocker"])
                for sample in report["near_misses"]:
                    list(sample["unmet"])
                dark_promotion.top_blocker([f"PATH_{i}" for i in range(200)])
        except Exception as exc:  # pragma: no cover - the failure being pinned
            errors.append(exc)

    reader = threading.Thread(target=_read, daemon=True)
    reader.start()
    try:
        for round_ in range(20):
            dark_promotion.reset_refusals_for_test()
            for i in range(200):
                dark_promotion.decide(
                    _Sig(
                        setup_class=f"PATH_{i}",
                        regime="TRENDING_DOWN",
                        symbol=f"R{i}USDT",
                    ),
                    "execution:overextended",
                )
    finally:
        stop.set()
        reader.join(timeout=10)

    assert not errors, f"reader raced the writer: {errors[0]!r}"


def test_an_unpublished_runtime_block_is_not_served_as_the_engines_own():
    """The API container must not hand ops zeros under `source: "engine"`.

    In isolated mode `snapshot()` builds a runtime block from THIS process,
    which has never run `decide` — so every counter is zero and the refusal
    census is empty. Ops reads `source` to decide between *not reported* and
    *reporting, nothing refused*; serving the local block would give it the
    second, i.e. "the engine is reporting and has refused nothing for this
    path, so the rule is not what is stopping it" — a benign caption for a
    state nobody observed, which is the defect this census exists to remove.

    Fails against the first cut of this change, which called `apply_runtime`
    unconditionally and left the local block in place on a `None`.
    """
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from src.api import dark_promotion_routes

    dark_promotion.set_rule(_lsr_rule())

    class _FacadeWithNothingPublished:
        def published_dark_promotion(self):
            return None

    app = FastAPI()
    dark_promotion_routes.register(
        app, owner_required=lambda: None, engine=_FacadeWithNothingPublished()
    )
    with TestClient(app) as client:
        body = client.get("/api/admin/dark-promotions").json()

    assert body["runtime"]["source"] is None, (
        "an unpublished block must not claim the engine as its source"
    )
    assert body["runtime"]["unavailable"], "and it must say why"
    assert body["counters"] == {}


def test_a_published_runtime_block_is_preferred_over_the_local_one():
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from src.api import dark_promotion_routes

    dark_promotion.set_rule(_lsr_rule())
    engine_block = {
        "source": "engine",
        "counters": {"promoted:LIQUIDITY_SWEEP_REVERSAL": 4},
        "promoted_today": {"LIQUIDITY_SWEEP_REVERSAL": 4},
        "refusals": {"LIQUIDITY_SWEEP_REVERSAL": {
            "total": 610, "by_dimension": {"gate": 513}, "sole_blocker": {},
        }},
        "near_misses": [],
    }

    class _Facade:
        def published_dark_promotion(self):
            return engine_block

    app = FastAPI()
    dark_promotion_routes.register(
        app, owner_required=lambda: None, engine=_Facade()
    )
    with TestClient(app) as client:
        body = client.get("/api/admin/dark-promotions").json()

    assert body["runtime"]["refusals"]["LIQUIDITY_SWEEP_REVERSAL"]["total"] == 610
    assert body["rules"][0]["promoted_today"] == 4, (
        "the cap's tally belongs to the process that charges it"
    )


# --------------------------------------------------------------------------- #
# The probe's sentence must not contradict the number beside it
#
# The first post-deploy read (2026-08-18) printed:
#   "2 rule(s) armed, 1 promoted today — no candidate has reached the decision
#    yet"
# `top_blocker` is empty when NOTHING WAS REFUSED, which is a different fact
# from nothing having reached the decision — and a promotion is a candidate
# reaching the decision. The sentence contradicted its own number.
# --------------------------------------------------------------------------- #


def _probe_detail():
    """Drive the REAL liveness predicate, lifted out of `main.py` by AST.

    Not a re-implementation: importing `src.main` drags the whole engine in, so
    the nested `_dark_promotion_rules` closure is compiled straight out of the
    shipping source. A copy of the sentence written here would assert my own
    assumption back at me, which is the failure mode that let the contradictory
    copy ship in the first place.
    """
    import ast
    from typing import Tuple as _Tuple

    tree = ast.parse(Path("src/main.py").read_text(encoding="utf-8"))
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "_dark_promotion_rules"
    )
    fn.col_offset = 0
    module = ast.Module(body=[fn], type_ignores=[])
    ast.fix_missing_locations(module)
    ns = {"Tuple": _Tuple}
    exec(compile(module, "<probe>", "exec"), ns)
    return ns["_dark_promotion_rules"]()


def test_the_probe_never_says_nothing_reached_the_decision_beside_a_promotion():
    dark_promotion.set_rule(_lsr_rule())
    dark_promotion.note_promoted("LIQUIDITY_SWEEP_REVERSAL")

    ok, detail = _probe_detail()
    assert ok
    assert "1 promoted today" in detail
    assert "no candidate has reached the decision" not in detail, (
        "a promotion IS a candidate reaching the decision — the sentence must "
        "not contradict the number standing beside it"
    )
    assert "nothing refused" in detail


def test_the_probe_still_says_so_when_genuinely_nothing_reached_the_decision():
    dark_promotion.set_rule(_lsr_rule())
    ok, detail = _probe_detail()
    assert ok
    assert "no candidate has reached the decision" in detail


def test_the_probe_names_the_blocker_once_something_is_refused():
    dark_promotion.set_rule(_lsr_rule(regimes=["TRENDING_UP"]))
    dark_promotion.decide(_Sig(regime="TRENDING_DOWN"), "execution:overextended")
    ok, detail = _probe_detail()
    assert ok
    assert dark_promotion.DIM_REGIME in detail
    assert "no candidate has reached the decision" not in detail


def test_an_erroring_candidate_is_counted_rather_than_reading_as_nothing_refused():
    """Otherwise "nothing was refused" is true while every candidate errors,
    and the probe's sentence names the benign cause for a fault."""
    dark_promotion.set_rule(_lsr_rule())

    class _Exploding:
        setup_class = "LIQUIDITY_SWEEP_REVERSAL"

        @property
        def entry_regime(self):
            raise RuntimeError("boom")

    d = dark_promotion.decide(_Exploding(), "execution:overextended")
    assert d.promote is False
    assert d.unmet == [dark_promotion.DIM_ERROR]

    cell = dark_promotion.runtime_report()["refusals"]["LIQUIDITY_SWEEP_REVERSAL"]
    assert cell["total"] == 1
    assert cell["sole_blocker"] == {dark_promotion.DIM_ERROR: 1}
    assert dark_promotion.top_blocker(["LIQUIDITY_SWEEP_REVERSAL"]) != ""


def test_the_census_survives_a_candidate_whose_own_attributes_raise():
    """The counters are written before the sample, because the sample reads the
    candidate and the candidate is the thing that is broken."""
    dark_promotion.set_rule(_lsr_rule())

    class _AllExploding:
        setup_class = "LIQUIDITY_SWEEP_REVERSAL"

        def __getattr__(self, name):
            raise RuntimeError("boom")

    dark_promotion.decide(_AllExploding(), "execution:overextended")
    cell = dark_promotion.runtime_report()["refusals"]["LIQUIDITY_SWEEP_REVERSAL"]
    assert cell["total"] == 1, "the count must land even when the sample cannot"
