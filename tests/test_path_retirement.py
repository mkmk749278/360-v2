"""Path retirement — the gate, its wiring, and the one thing that could go
silently wrong.

`MOVER_TREND_PULLBACK` is in `dark_emission.EXCLUDED_SETUPS`, so the obvious
failure mode of this feature is that a retired MVRTP SHORT is diverted *and
then refused by the ledger* — stopping delivery, which is wanted, while
destroying the measurement, which is the whole reason to divert rather than
return. That is checked here by driving the **real** `publish()`, not by
reading its source and concluding it is fine.
"""
from __future__ import annotations

import ast
import pathlib

from src import dark_emission, path_retirement as pr

REPO = pathlib.Path(__file__).resolve().parents[1]
SCANNER = REPO / "src" / "scanner" / "__init__.py"


class _Sig:
    """Minimal candidate with the fields the ledger row builder reads."""

    def __init__(self, setup="MOVER_TREND_PULLBACK", side="SHORT", sid="s1"):
        self.signal_id = sid
        self.symbol = "AAAUSDT"
        self.channel = "360_SCALP"
        self.setup_class = setup
        self.direction = side
        self.entry = 100.0
        self.stop_loss = 103.0 if side == "SHORT" else 97.0
        self.tp1 = 96.0 if side == "SHORT" else 104.0
        self.confidence = 75.0


# --------------------------------------------------------------------------- #
# The predicate
# --------------------------------------------------------------------------- #

def test_the_signed_off_retirements_match(monkeypatch):
    monkeypatch.setattr(pr, "_ENABLED_DEFAULT", True)
    assert pr.reason_for("MOVER_TREND_PULLBACK", "SHORT") == \
        "retired:MOVER_TREND_PULLBACK:SHORT"
    assert pr.reason_for("VOLUME_SURGE_BREAKOUT", "LONG") == \
        "retired:VOLUME_SURGE_BREAKOUT:*"
    assert pr.reason_for("VOLUME_SURGE_BREAKOUT", "SHORT") == \
        "retired:VOLUME_SURGE_BREAKOUT:*"


def test_the_side_that_earns_money_is_untouched():
    """MVRTP LONG measured +0.257%/trade with P(>0)=76%. Retiring the path
    rather than the (path, side) would have thrown that away — and MVRTP is
    76% of the delivered book."""
    assert pr.reason_for("MOVER_TREND_PULLBACK", "LONG") is None


def test_no_other_path_is_touched():
    for s in ("TREND_PULLBACK_EMA", "MOVER_AVWAP_SCALP", "MEAN_REVERT",
              "LIQUIDITY_SWEEP_REVERSAL", "FAILED_AUCTION_RECLAIM"):
        for side in ("LONG", "SHORT"):
            assert pr.reason_for(s, side) is None, f"{s}:{side}"


def test_an_unlabelled_candidate_is_not_retired():
    """Absence of a setup_class is not evidence about the path.

    Fail-closed here would silently retire every future evaluator that forgot
    its `setup_class=` argument — the opposite of a floor.
    """
    assert pr.reason_for("", "SHORT") is None
    assert pr.reason_for(None, "SHORT") is None


def test_a_Direction_enum_repr_still_matches():
    """`getattr(sig, "direction")` is a `Direction`, not a string, and its str
    is `Direction.SHORT`. A gate that only matched bare strings would abstain
    on every real candidate while every unit test passed."""
    assert pr.reason_for("MOVER_TREND_PULLBACK", "Direction.SHORT") is not None

    class _D:
        def __str__(self): return "Direction.SHORT"
    assert pr.reason_for("MOVER_TREND_PULLBACK", _D()) is not None


def test_the_master_switch_restores_prior_behaviour(monkeypatch):
    monkeypatch.setattr(pr, "enabled", lambda: False)
    assert pr.reason_for("MOVER_TREND_PULLBACK", "SHORT") is None


def test_an_empty_list_retires_nothing_and_is_a_real_value(monkeypatch):
    """The way the owner clears this from a form field.

    An empty string must mean "retire nothing", never "fall back to the
    default" — otherwise the control can be added to and never emptied, which
    is the one state a money-path switch must not be in.
    """
    monkeypatch.setattr(pr, "_configured", lambda: pr._parse(""))
    assert pr.reason_for("MOVER_TREND_PULLBACK", "SHORT") is None


def test_a_malformed_entry_is_skipped_not_obeyed():
    got = pr._parse("MOVER_TREND_PULLBACK:SIDEWAYS, MEAN_REVERT:SHORT")
    assert ("MEAN_REVERT", "SHORT") in got
    assert not any(s == "MOVER_TREND_PULLBACK" for s, _ in got)


def test_a_bare_setup_name_retires_both_sides():
    assert pr._parse("MEAN_REVERT") == [("MEAN_REVERT", pr.ANY_SIDE)]


# --------------------------------------------------------------------------- #
# THE check: a retired MVRTP SHORT must still be MEASURED
# --------------------------------------------------------------------------- #

def test_a_retired_row_is_still_written_to_the_dark_ledger(tmp_path, monkeypatch):
    """Driving the REAL ledger, because MVRTP is in `EXCLUDED_SETUPS`.

    If `publish` honoured that exclusion the retirement would stop delivery AND
    stop the measurement — a verdict that can never be revisited, which is
    `cohort_edge`'s absorbing state and the exact thing diverting instead of
    returning is meant to avoid. Reading `publish`'s source and concluding it
    does not check is not the same as running it.
    """
    assert "MOVER_TREND_PULLBACK" in dark_emission.EXCLUDED_SETUPS, (
        "premise of this test: the path is barred from the lane by should_mark"
    )
    ledger = dark_emission.DarkLedger(path=str(tmp_path / "dark.json"))
    dark_emission.reset_ledger(ledger)
    monkeypatch.setattr(dark_emission, "enabled", lambda: True)

    sig = _Sig()
    dark_emission.mark(sig, pr.reason_for(sig.setup_class, sig.direction))
    assert dark_emission.is_dark(sig) is True

    assert dark_emission.publish(sig) is True, (
        "a retired candidate was diverted and then refused by the ledger — "
        "delivery stopped and the measurement destroyed"
    )
    rows = ledger.rows()
    assert len(rows) == 1
    assert rows[0]["dark_gate"] == "retired:MOVER_TREND_PULLBACK:SHORT"
    assert rows[0]["setup_class"] == "MOVER_TREND_PULLBACK"
    dark_emission.reset_ledger(None)


def test_should_mark_still_refuses_the_excluded_path(monkeypatch):
    """The retirement bypasses `should_mark` deliberately; that bypass must not
    quietly re-admit MVRTP to the LOOSENED-GATE lane, which is a different
    population with a different reason for existing."""
    monkeypatch.setattr(dark_emission, "enabled", lambda: True)
    assert dark_emission.should_mark(_Sig(), "setup_compat:regime_CLEAN_RANGE") is False


# --------------------------------------------------------------------------- #
# Wiring — parsed from the scanner's tree
# --------------------------------------------------------------------------- #

def _enqueue_fn() -> ast.AsyncFunctionDef:
    tree = ast.parse(SCANNER.read_text())
    for n in ast.walk(tree):
        if isinstance(n, (ast.AsyncFunctionDef, ast.FunctionDef)) and n.name == "_enqueue_signal":
            return n
    raise AssertionError("_enqueue_signal not found")


def test_the_retirement_marks_and_never_returns():
    """A bare `return False` would stop delivery AND the measurement.

    Pinned by AST rather than by substring: the property is that the retirement
    branch reaches `dark_emission.mark` and contains no `return`, and a
    substring assertion on the word "mark" would go green over a branch that
    also returned.
    """
    fn = _enqueue_fn()
    branch = None
    for node in ast.walk(fn):
        if not isinstance(node, ast.Try):
            continue
        src = ast.dump(node)
        if "path_retirement" in src and "reason_for" in src:
            branch = node
            break
    assert branch is not None, "no path_retirement block in _enqueue_signal"

    marks = [
        n for n in ast.walk(branch)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
        and n.func.attr == "mark"
    ]
    assert marks, "the retirement must MARK the candidate dark"
    returns = [n for n in ast.walk(branch) if isinstance(n, ast.Return)]
    assert not returns, (
        "the retirement branch returns — that stops the measurement too, and a "
        "path that never emits can never earn its way back"
    )


def test_the_retirement_runs_before_the_dark_divergence():
    """Marking after the `is_dark` branch would divert nothing at all."""
    src = SCANNER.read_text()
    i_retire = src.index("path_retirement.reason_for")
    i_divert = src.index("if dark_emission.is_dark(sig):", src.index("async def _enqueue_signal"))
    assert i_retire < i_divert, (
        "path retirement must mark before the divergence point, or the mark "
        "arrives after the only branch that reads it"
    )


def test_it_stamps_suppressed_like_every_other_live_gate():
    """A gate that cannot be measured cannot earn its place — and this one has
    to keep earning it, since it is designed to be reversible."""
    fn = _enqueue_fn()
    for node in ast.walk(fn):
        if isinstance(node, ast.Try) and "path_retirement" in ast.dump(node):
            assert "_stamp_suppressed" in ast.dump(node)
            return
    raise AssertionError("no path_retirement block found")


def test_an_already_dark_candidate_keeps_its_original_gate():
    """Overwriting `dark_gate` would relabel the row and lose which gate
    actually caught it — the loosened gate is the reason it never delivers."""
    fn = _enqueue_fn()
    for node in ast.walk(fn):
        if isinstance(node, ast.Try) and "path_retirement" in ast.dump(node):
            assert "is_dark" in ast.dump(node), (
                "the retirement must skip candidates already marked dark"
            )
            return
    raise AssertionError("no path_retirement block found")


# --------------------------------------------------------------------------- #
# The two switches are separate, and the panel must be able to say which
# --------------------------------------------------------------------------- #

def test_snapshot_reports_both_the_mode_and_the_list():
    snap = pr.snapshot()
    assert set(snap) >= {"enabled", "retired", "count", "is_default"}
    assert {"setup_class": "MOVER_TREND_PULLBACK", "side": "SHORT"} in snap["retired"]


def test_the_tunables_are_registered_and_typed():
    from src import runtime_tunables as rt

    keys = rt.registry()
    assert keys["path_retirement_enabled"].type == "bool"
    assert keys["retired_paths"].type == "str"
    assert keys["retired_paths"].category == keys["path_retirement_enabled"].category
