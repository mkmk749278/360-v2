"""Dynamic mover retention — the scorer, its bounds, and its wiring.

The invariant these tests exist to hold is the module's first sentence:
**retention is scored on opportunity and liveness, never on outcomes.** A
future change that adds "just a win rate" to the window makes the gate an
absorbing state — dropped pair produces nothing, records nothing, can never
earn its way back — which is `cohort_edge`'s 23-day failure exactly. So the
first test derives the requirement from the dataclass rather than listing what
is allowed, and fails on the field that has not been invented yet.

The wiring tests parse the scanner's AST rather than mocking it. A mock of the
scanner would assert my assumption about where the counters fire back at me,
and the whole class of defect here is a call site that never runs.
"""
from __future__ import annotations

import ast
import dataclasses
import pathlib

import pytest

from src import mover_retention as mr


REPO = pathlib.Path(__file__).resolve().parents[1]
SCANNER = REPO / "src" / "scanner" / "__init__.py"


def _detector(**overrides):
    """The real detector with test-friendly thresholds — never a stand-in.

    `activity()` is the liveness half of every verdict, and a hand-written
    return shape would assert my assumption about it back at me.
    """
    from src.mover_ignition import MoverIgnitionDetector

    params = dict(
        enabled=True, window_sec=10.0, move_floor_pct=1.0, burst_mult=3.0,
        min_window_notional_usd=1_000.0, cooldown_sec=60.0,
        baseline_alpha=0.1, min_baseline_samples=5, max_gap_sec=30.0,
    )
    params.update(overrides)
    return MoverIgnitionDetector(**params)


@pytest.fixture(autouse=True)
def _fresh():
    mr.reset_for_test(mr.MoverRetention())
    yield
    mr.reset_for_test(None)


# --------------------------------------------------------------------------- #
# The invariant
# --------------------------------------------------------------------------- #

def test_no_outcome_field_can_enter_the_retention_window():
    """Derived from the dataclass, so tomorrow's field is covered.

    A list of *allowed* fields would pass the moment somebody adds `win_rate`
    beside them; this fails on any field whose name reads like an outcome,
    which is the direction the drift actually goes.
    """
    banned = (
        "pnl", "win", "loss", "profit", "r_multiple", "outcome",
        "hit_tp", "hit_sl", "edge", "expectancy", "return",
    )
    names = [f.name for f in dataclasses.fields(mr.PairWindow)]
    offenders = [n for n in names if any(b in n.lower() for b in banned)]
    assert offenders == [], (
        f"{offenders} looks like an outcome on the retention window. Scoring "
        "retention on outcomes makes it an absorbing state: a dropped pair "
        "produces no candidates, so it records no outcomes, so it can never "
        "earn its way back (cohort_edge, CLAUDE.md)."
    )


def test_the_module_never_imports_an_outcome_source():
    """The other half of the same invariant, one layer up.

    The window cannot hold an outcome; this stops the verdict reading one from
    the closed-signal record or the dark ledger at score time.
    """
    tree = ast.parse((REPO / "src" / "mover_retention.py").read_text())
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append(node.module)
        elif isinstance(node, ast.Import):
            imported.extend(a.name for a in node.names)
    forbidden = {
        "src.performance_tracker", "src.dark_emission", "src.strategy_edge",
        "src.suppression_audit", "src.trade_monitor",
    }
    assert not (set(imported) & forbidden), (
        f"mover_retention imports an outcome source: {set(imported) & forbidden}"
    )


# --------------------------------------------------------------------------- #
# Verdicts
# --------------------------------------------------------------------------- #

def test_a_young_pair_is_warmup_not_hold():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=1000.0)
    v = r.verdict("AAAUSDT", now=1000.0 + mr.MIN_HOLD_SEC - 1)
    assert v is not None
    assert v.verdict == mr.WARMUP
    assert v.reason == mr.REASON_WARMUP


def test_warmup_protects_a_pair_that_has_produced_nothing_yet():
    """The bound that stops this measuring the clock instead of the pair.

    A pair promoted at minute zero of an ignition has produced nothing *by
    construction*, and releasing it for that would drop exactly the pairs the
    ignition path exists to catch.
    """
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    for _ in range(mr.MIN_SCANS_TO_JUDGE * 5):
        r.note_scan("AAAUSDT")
    v = r.verdict("AAAUSDT", now=mr.MIN_HOLD_SEC - 1)
    assert v.verdict == mr.WARMUP, "a young pair must not be released for silence"


def test_scanned_enough_and_produced_nothing_releases():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_TOP24H", now=0.0)
    for _ in range(mr.MIN_SCANS_TO_JUDGE):
        r.note_scan("AAAUSDT")
    v = r.verdict("AAAUSDT", now=mr.MIN_HOLD_SEC + 1)
    assert v.releases
    assert v.reason == mr.REASON_NO_CANDIDATES
    # A release with no numbers beside it is a counter, and a counter is not a
    # cause. The evidence is what the ops panel renders.
    assert v.evidence["scans"] == mr.MIN_SCANS_TO_JUDGE
    assert v.evidence["candidates"] == 0


def test_too_few_scans_is_not_evidence_of_a_dead_pair():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_TOP24H", now=0.0)
    for _ in range(mr.MIN_SCANS_TO_JUDGE - 1):
        r.note_scan("AAAUSDT")
    v = r.verdict("AAAUSDT", now=mr.MIN_HOLD_SEC + 1)
    assert not v.releases, (
        "'produced no candidates' must be a fact about the pair, not about "
        "how little we looked at it"
    )


def test_a_sustained_return_to_baseline_releases_the_slot():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    r.note_candidate("AAAUSDT", now=10.0)
    r.note_activity("AAAUSDT", 4.0, now=10.0)          # alive
    r.note_activity("AAAUSDT", 0.9, now=100.0)         # settled
    v = r.verdict("AAAUSDT", now=100.0 + mr.SPENT_FOR_SEC + mr.MIN_HOLD_SEC)
    assert v.releases
    assert v.reason == mr.REASON_MOVE_SPENT


def test_one_quiet_sample_inside_a_live_move_does_not_release():
    """`SPENT_FOR_SEC` is what separates a lull from exhaustion."""
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    alive_at = mr.MIN_HOLD_SEC + 100.0          # past warmup, still running
    r.note_candidate("AAAUSDT", now=alive_at)
    r.note_activity("AAAUSDT", 4.0, now=alive_at)
    r.note_activity("AAAUSDT", 0.5, now=alive_at + 10.0)
    v = r.verdict("AAAUSDT", now=alive_at + mr.SPENT_FOR_SEC - 60.0)
    assert not v.releases, "a single quiet window is noise, not exhaustion"


def test_an_unmeasurable_pair_is_held_never_dropped():
    """Absence of knowledge is not permission.

    `None` is what the detector returns on a reconnect, a thin symbol, or a
    window that has not re-warmed. Reading it as "spent" drops a pair mid-trend
    on a websocket hiccup — a fault wearing a verdict's clothes.
    """
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    r.note_candidate("AAAUSDT", now=10.0)
    for t in range(0, 6000, 60):
        r.note_activity("AAAUSDT", None, now=float(t))
    v = r.verdict("AAAUSDT", now=mr.MIN_HOLD_SEC + mr.SPENT_FOR_SEC * 4)
    assert not v.releases
    assert v.evidence.get("activity") == mr.REASON_NO_ACTIVITY_DATA, (
        "a lane that has gone blind must be visible, not merely harmless"
    )


def test_a_producing_pair_is_extended_past_the_flat_ttl():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    now = mr._flat_ttl() + 60.0
    r.note_scan("AAAUSDT")
    r.note_candidate("AAAUSDT", now=now - 10.0)
    r.note_activity("AAAUSDT", 3.0, now=now - 10.0)
    v = r.verdict("AAAUSDT", now=now)
    assert v.verdict == mr.EXTEND
    assert v.reason == mr.REASON_PRODUCING


def test_the_ceiling_beats_every_good_score():
    """A bound a good score can talk its way past is not a bound."""
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    now = mr.MAX_HOLD_SEC + 1
    for _ in range(500):
        r.note_scan("AAAUSDT")
        r.note_candidate("AAAUSDT", now=now - 1)
    r.note_activity("AAAUSDT", 50.0, now=now - 1)
    v = r.verdict("AAAUSDT", now=now)
    assert v.releases
    assert v.reason == mr.REASON_TTL


def test_re_promotion_keeps_the_original_window():
    """Otherwise a pair that keeps re-igniting is immortal.

    Its age would never reach any ceiling, which is the opposite of a
    retention policy — the pair with the most re-ignitions would be the one
    least able to be released.
    """
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=5000.0)
    assert r.promoted_at("AAAUSDT") == 0.0
    assert r.age_sec("AAAUSDT", now=mr.MAX_HOLD_SEC + 1) > mr.MAX_HOLD_SEC


# --------------------------------------------------------------------------- #
# Counters are no-ops for pairs we do not hold
# --------------------------------------------------------------------------- #

def test_every_counter_is_a_noop_for_an_unheld_symbol():
    """One predicate, here, rather than four in the scanner that can drift.

    The scan chain calls these on every symbol including the core 75; if any
    of them created a window, retention would score pairs it does not hold.
    """
    r = mr.get_retention()
    for fn in (r.note_scan, r.note_candidate, r.note_reached_enqueue,
               r.note_enqueued, r.note_dark):
        fn("BTCUSDT")
    r.note_activity("BTCUSDT", 3.0)
    assert r.held_symbols() == []
    assert r.verdict("BTCUSDT") is None


def test_held_symbols_is_what_lets_the_caller_reconcile():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION")
    r.on_promoted("BBBUSDT", "MOVER_TOP24H")
    assert sorted(r.held_symbols()) == ["AAAUSDT", "BBBUSDT"]
    r.on_released("AAAUSDT", "entered_scan")
    assert r.held_symbols() == ["BBBUSDT"]


# --------------------------------------------------------------------------- #
# Enforcement defaults, and the report
# --------------------------------------------------------------------------- #

def test_enforcement_is_off_by_default():
    """Measurement ON, effect OFF — the two-flag rule at this lane.

    The scorer runs from the moment it ships so a window of would-be releases
    accumulates in ops; acting on it changes which pairs are scanned, which
    changes which signals emit, and that needs owner sign-off on measured
    evidence.
    """
    from config import MOVER_RETENTION_ENFORCE

    assert MOVER_RETENTION_ENFORCE is False


def test_the_report_publishes_its_bounds_and_its_mode():
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    rep = r.report(now=100.0)
    assert rep["held"] == 1
    assert rep["enforcing"] is False
    # The reader cannot judge a verdict without the thresholds it was reached
    # against, so they render beside it rather than living in the source.
    for key in ("min_hold_sec", "max_hold_sec", "flat_ttl_sec",
                "min_scans_to_judge", "spent_burst_ratio", "spent_for_sec"):
        assert key in rep["bounds"]


def test_the_flat_ttl_is_read_from_config_not_copied():
    """A second constant here would drift from the promotion loop's own.

    The whole verdict is expressed relative to it, so a copy that fell behind
    would silently change what EXTEND means.
    """
    from config import MOVER_PROMOTION_TTL_SEC

    assert mr._flat_ttl() == float(MOVER_PROMOTION_TTL_SEC)


def test_a_sweep_never_lets_one_bad_pair_kill_the_rest():
    """A scorer that throws must not be able to change which pairs are scanned."""
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)
    r.on_promoted("BBBUSDT", "MOVER_IGNITION", now=0.0)
    r._windows["AAAUSDT"].promoted_at = None  # type: ignore[assignment]
    out = r.sweep(now=mr.MIN_HOLD_SEC + 1)
    assert [v.symbol for v in out] == ["BBBUSDT"]


# --------------------------------------------------------------------------- #
# The activity reading, driven through the REAL detector
# --------------------------------------------------------------------------- #

def test_activity_reads_none_before_a_baseline_exists():
    """Driven through the real detector, not a hand-written return shape.

    A mock whose keys I chose cannot verify a contract I got wrong — and the
    direction of this particular fail decides whether a pair is dropped
    mid-trend on a feed blink.
    """
    det = _detector()
    assert det.activity("AAAUSDT") is None
    assert det.activity("") is None


def test_activity_returns_a_multiple_of_the_pairs_own_baseline():
    """Fed through `ingest`, the path production actually uses."""
    det = _detector()
    base_ms = 1_700_000_000_000
    for i in range(12):
        det.ingest(
            [{"s": "AAAUSDT", "E": base_ms + i * 5_000, "c": "1.0",
              "n": 100 * (i + 1), "q": "1000000", "P": "1.0"}],
            now=float(i * 5),
        )
    val = det.activity("AAAUSDT")
    assert val is not None, "a steady stream must produce a readable baseline"
    # A constant trade rate is the pair trading at its own baseline — ~1x,
    # which is precisely the reading that calls a move spent.
    assert 0.5 <= val <= 2.0


# --------------------------------------------------------------------------- #
# Wiring — parsed from the scanner's tree, because a call site that never runs
# is exactly the defect here and no mock can see it.
# --------------------------------------------------------------------------- #

def _scanner_tree() -> ast.Module:
    return ast.parse(SCANNER.read_text())


def _retention_calls() -> set[str]:
    """Every `mover_retention.get_retention().<method>(...)` in the scanner."""
    found: set[str] = set()
    for node in ast.walk(_scanner_tree()):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        if not isinstance(f, ast.Attribute):
            continue
        inner = f.value
        # `<something>.get_retention().method()` or `_retention.method()`
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) \
                and inner.func.attr == "get_retention":
            found.add(f.attr)
        elif isinstance(inner, ast.Name) and inner.id == "_retention":
            found.add(f.attr)
    return found


@pytest.mark.parametrize("method", [
    "note_scan", "note_candidate", "note_reached_enqueue",
    "note_enqueued", "note_dark", "note_activity",
    "on_promoted", "on_released", "sweep",
])
def test_the_scanner_actually_calls_each_counter(method):
    """Defining a method is not calling it — pin the call site.

    Every previous version of this defect in the repo was a half that looked
    complete: stamped but never flushed, flushed but never loaded, written but
    read by nothing. A counter with no call site scores every pair on an empty
    window and then releases it for producing nothing.
    """
    assert method in _retention_calls(), (
        f"mover_retention.{method} has no call site in the scanner — the "
        "verdict would be reached on a window nothing fills"
    )


def test_the_promotion_loop_reconciles_instead_of_remembering():
    """Three sites drop a symbol from `_mover_promoted_pairs`; a fourth added
    later must not leak a retention window. The reconcile derives the
    requirement from the two sets rather than from a list of call sites."""
    src = SCANNER.read_text()
    assert "held_symbols()" in src, (
        "the promotion loop must reconcile retention's held set against its "
        "own, or a future drop site leaves a window scoring a pair we no "
        "longer promote"
    )


def test_enforcement_gates_the_ACTION_and_never_the_MEASUREMENT():
    """The two-flag rule, pinned in the tree.

    `sweep()` must not sit behind `enforce_enabled()`: a measurement that
    stamps nothing until somebody flips a switch produces an empty ops panel
    and a decision that keeps getting deferred (CLAUDE.md § Project Phase).
    """
    tree = _scanner_tree()
    fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef))
        and n.name == "_update_movers_promotion"
    )
    sweep_calls = [
        n for n in ast.walk(fn)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "sweep"
    ]
    assert sweep_calls, "_update_movers_promotion must sweep every cycle"

    # No `sweep()` may be nested inside a test of `enforce_enabled`.
    for node in ast.walk(fn):
        if not isinstance(node, ast.If):
            continue
        guards_enforcement = any(
            isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
            and c.func.attr == "enforce_enabled"
            for c in ast.walk(node.test)
        ) or any(
            isinstance(c, ast.Name) and c.id == "_enforcing"
            for c in ast.walk(node.test)
        )
        if not guards_enforcement:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute) \
                    and inner.func.attr == "sweep":
                raise AssertionError(
                    "sweep() sits behind the enforcement flag — the "
                    "measurement must run whether or not it is acted on"
                )


# --------------------------------------------------------------------------- #
# The promotion-age stamp
# --------------------------------------------------------------------------- #

def test_promotion_age_uses_minus_one_for_not_a_mover_never_zero():
    """`0.0` is a real reading — a signal that fired at the top of a hold.

    Sharing a sentinel with "this pair was never promoted" would make every
    core pair read as the freshest possible ignition, which is the exact
    reading the owner's question turns on.
    """
    from src.channels.base import Signal

    assert dataclasses.fields(Signal)  # sanity: it is a dataclass
    default = next(
        f.default for f in dataclasses.fields(Signal)
        if f.name == "promotion_age_sec"
    )
    assert default == -1.0

    from src.performance_tracker import SignalRecord

    rec_default = next(
        f.default for f in dataclasses.fields(SignalRecord)
        if f.name == "promotion_age_sec"
    )
    assert rec_default == -1.0


def test_the_closed_signal_record_carries_promotion_age(tmp_path):
    """A cross-repo field name is a contract, pinned on the PRODUCING side.

    Ops splits the mover book by where in the hold a signal fired; renaming
    this must fail here rather than quietly emptying that page (#817).
    """
    from src.performance_tracker import PerformanceTracker

    tracker = PerformanceTracker(storage_path=str(tmp_path / "perf.json"))
    tracker.record_outcome(
        signal_id="sig-1", channel="360_SCALP", symbol="AAAUSDT",
        direction="LONG", entry=1.0, hit_tp=0, hit_sl=1, pnl_pct=-1.0,
        pair_admission="MOVER_IGNITION", promotion_age_sec=42.5,
    )
    rec = tracker._records[-1]
    assert rec.promotion_age_sec == 42.5
    assert rec.pair_admission == "MOVER_IGNITION"


def test_the_dark_ledger_row_carries_promotion_age():
    """Driven through the real row builder — a fixture would choose the key's
    location and then agree with me about it."""
    from src import dark_emission

    class _Sig:
        signal_id = "s1"
        symbol = "AAAUSDT"
        channel = "360_SCALP"
        setup_class = "MOVER_TREND_PULLBACK"
        direction = "LONG"
        entry = 1.0
        stop_loss = 0.9
        tp1 = 1.1
        confidence = 70.0
        pair_admission = "MOVER_IGNITION"
        promotion_age_sec = 123.0

    row = dark_emission._row_from_signal(_Sig(), 1_700_000_000.0)
    assert row["promotion_age_sec"] == 123.0
    assert row["pair_admission"] == "MOVER_IGNITION"


def test_a_row_with_no_stamp_reads_absent_not_zero():
    """Absent and "not a held mover" are different facts, and pooling them
    reports core pairs as unstamped movers."""
    from src import dark_emission

    class _Old:
        signal_id = "s2"
        symbol = "BBBUSDT"
        channel = "360_SCALP"
        setup_class = "MEAN_REVERT"
        direction = "SHORT"
        entry = 1.0
        stop_loss = 1.1
        tp1 = 0.9
        confidence = 60.0
        promotion_age_sec = None

    row = dark_emission._row_from_signal(_Old(), 1_700_000_000.0)
    assert row["promotion_age_sec"] is None


def test_the_dark_ledger_schema_bump_is_declared_additive():
    """The bump adds a field and redefines nothing, so every older row keeps
    its full standing — dropping them would delete the evidence at the moment
    it starts being used (the 371 SAR rows, 2026-08-09).

    Pins the PROPERTY, not the number. The first cut asserted
    `LEDGER_SCHEMA == 3`, and the very next additive bump failed it for a
    reason unrelated to what it protects — whose cheapest fix is to edit the
    literal and move on, which is how a guard becomes a formality. Every bump
    so far is additive, so every earlier schema must be readable; a bump that
    REDEFINES a field is the one case where dropping old rows is right, and it
    has to edit this test deliberately and say which field changed meaning.
    """
    from src import dark_emission

    assert dark_emission.ADDITIVE_FROM_SCHEMAS == frozenset(
        range(1, dark_emission.LEDGER_SCHEMA)
    ), (
        "every schema before the current one is additive and must stay "
        "readable; if a bump redefined a field, change this test and say which"
    )


# --------------------------------------------------------------------------- #
# The promotion SIGN — top gainer vs top loser
# --------------------------------------------------------------------------- #

def test_the_signed_move_survives_promotion():
    """`_ensure_mover_pair` stores `abs(change_pct)`, so this is the only
    carrier of the sign. A top gainer and a top loser are the same number to
    every other consumer, and on the delivered book they are not the same
    trade."""
    r = mr.get_retention()
    r.on_promoted("UPUSDT", "MOVER_TOP24H", now=0.0, change_pct=+31.4)
    r.on_promoted("DOWNUSDT", "MOVER_TOP24H", now=0.0, change_pct=-27.9)
    assert r.change_pct_at_promotion("UPUSDT") == 31.4
    assert r.change_pct_at_promotion("DOWNUSDT") == -27.9


def test_unknown_is_None_and_never_zero():
    """"We could not read which kind of mover this was" and "it moved 0%" are
    different facts, and only one of them can be filtered on."""
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0)          # no reading
    assert r.change_pct_at_promotion("AAAUSDT") is None
    r.on_promoted("BBBUSDT", "MOVER_IGNITION", now=0.0, change_pct=0.0)
    assert r.change_pct_at_promotion("BBBUSDT") == 0.0           # a real reading
    assert r.change_pct_at_promotion("NEVERPROMOTED") is None


def test_the_report_says_gainer_or_loser_and_abstains_when_unknown():
    r = mr.get_retention()
    r.on_promoted("UPUSDT", "MOVER_TOP24H", now=0.0, change_pct=+20.0)
    r.on_promoted("DOWNUSDT", "MOVER_TOP24H", now=0.0, change_pct=-20.0)
    r.on_promoted("QQQUSDT", "MOVER_TOP24H", now=0.0)
    rows = {x["symbol"]: x for x in r.report(now=10.0)["pairs"]}
    assert rows["UPUSDT"]["gainer"] is True
    assert rows["DOWNUSDT"]["gainer"] is False
    assert rows["QQQUSDT"]["gainer"] is None, (
        "no reading must abstain — False would call every unmeasurable pair a loser"
    )


def test_re_promotion_keeps_the_ORIGINAL_move_too():
    """The window is not reset on re-promotion (a re-igniting pair would become
    immortal), so the move it was ADMITTED on is what stays recorded."""
    r = mr.get_retention()
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=0.0, change_pct=+18.0)
    r.on_promoted("AAAUSDT", "MOVER_IGNITION", now=5000.0, change_pct=-4.0)
    assert r.change_pct_at_promotion("AAAUSDT") == 18.0


def test_the_detector_reports_the_sign_and_None_when_it_cannot():
    """Driven through the real detector — `meta_change_pct` is the only reader
    of the sign, so a hand-written return shape would assert my assumption."""
    det = _detector()
    assert det.meta_change_pct("NOPEUSDT") is None
    base = 1_700_000_000_000
    for i in range(6):
        det.ingest([{"s": "DOWNUSDT", "E": base + i * 5_000, "c": "1.0",
                     "n": 100 * (i + 1), "q": "1000000", "P": "-27.5"}],
                   now=float(i * 5))
    assert det.meta_change_pct("DOWNUSDT") == -27.5, "the SIGN must survive"


def test_the_scanner_passes_the_signed_move_to_on_promoted():
    """Pinned in the tree: `on_promoted` must be called WITH `change_pct`.

    Dropping the argument leaves every window reading None while the report
    still renders — a full-looking column describing nothing, which is the
    defect shape this repo keeps paying for.
    """
    tree = ast.parse(SCANNER.read_text())
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "on_promoted"):
            if any(k.arg == "change_pct" for k in node.keywords):
                return
    raise AssertionError(
        "the scanner calls on_promoted without change_pct — the sign is lost "
        "at the only point that still has it"
    )
