"""Phase 4 — the structural veto.

Drives the REAL `LevelBook` and the REAL `VolumeProfileResult` wherever a
collaborator is needed. A fixture whose keys the test author chose asserts that
author's assumption back at them and goes green over dead code — which is how
`zone_distance_atr` read `top`/`bottom`/`high`/`low`/`price` off a producer that
emits `gap_high`/`gap_low`, returned None on 57 of 57 rows for its whole life,
and passed two tests the whole time.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from src.level_book import Level
from src.structural_veto import (
    REFUSE_NO_LEVELS,
    REFUSE_NO_OPPOSING,
    ROW_METADATA_KEYS,
    build_row,
    nearest_opposing,
    should_suppress,
    would_reject,
)

REPO = Path(__file__).resolve().parents[1]


def _lvl(price, type_, **kw):
    """A real `Level`, not a dict shaped like one."""
    return Level(price=price, type=type_, source_tf=kw.pop("source_tf", "1h"), **kw)


def _row(**kw):
    base = dict(
        signal_id="s1", symbol="BTCUSDT", side="LONG",
        setup_class="MOVER_TREND_PULLBACK", entry=100.0, tp1=104.0,
        sl_dist_pct=2.0, atr=2.0, levels=[], value_area=None, now_ts=1_000.0,
    )
    base.update(kw)
    return build_row(**base)


# ── signed toward the trade ───────────────────────────────────────────────

def test_opposing_is_resistance_above_for_a_long():
    lvl, readable = nearest_opposing(
        [_lvl(102.0, "resistance"), _lvl(98.0, "support")], 100.0, is_long=True
    )
    assert lvl.price == 102.0
    assert readable == 2


def test_opposing_is_support_below_for_a_short():
    """A feature not signed toward the trade scores half the book backwards,
    and the book is ~50/50 by side — so the error would not show as an empty
    column, it would make the feature look like noise."""
    lvl, _ = nearest_opposing(
        [_lvl(102.0, "resistance"), _lvl(98.0, "support")], 100.0, is_long=False
    )
    assert lvl.price == 98.0


def test_a_level_behind_the_entry_is_not_an_obstacle():
    lvl, readable = nearest_opposing([_lvl(95.0, "resistance")], 100.0, is_long=True)
    assert lvl is None          # resistance below a long entry is already broken
    assert readable == 1        # ...but it WAS readable


def test_the_nearest_opposing_level_wins_not_the_highest_scoring():
    """`LevelBook.nearest_level` sorts by score; this lane wants the one price
    reaches FIRST, which is a different question."""
    lvl, _ = nearest_opposing(
        [_lvl(110.0, "resistance", score=9.0), _lvl(101.0, "resistance", score=0.1)],
        100.0, is_long=True,
    )
    assert lvl.price == 101.0


# ── the features ──────────────────────────────────────────────────────────

def test_distance_is_recorded_in_both_units():
    """ATR normalises across symbols, percent is what the money reads, and
    trusting one normaliser is #855's standing lesson."""
    r = _row(levels=[_lvl(103.0, "resistance")], entry=100.0, atr=2.0)
    assert r["opposing_dist_pct"] == pytest.approx(3.0)
    assert r["opposing_dist_atr"] == pytest.approx(1.5)


def test_target_behind_level_is_the_rule_that_needs_no_threshold():
    inside = _row(levels=[_lvl(102.0, "resistance")], entry=100.0, tp1=104.0)
    assert inside["opposing_inside_tp1"] is True
    assert would_reject(inside) is True

    beyond = _row(levels=[_lvl(108.0, "resistance")], entry=100.0, tp1=104.0)
    assert beyond["opposing_inside_tp1"] is False
    assert would_reject(beyond) is False


def test_target_behind_level_is_signed_for_a_short():
    r = _row(side="SHORT", levels=[_lvl(98.0, "support")], entry=100.0, tp1=96.0)
    assert r["opposing_inside_tp1"] is True
    assert would_reject(r) is True


def test_level_provenance_rides_on_the_row():
    """A 1d swing that has held four times and an untested round number are
    different obstacles; averaging them is how a real effect becomes noise."""
    r = _row(levels=[_lvl(102.0, "resistance", source_tf="1d", touches=4, score=7.5)])
    assert r["opposing_source_tf"] == "1d"
    assert r["opposing_score"] == pytest.approx(7.5)
    assert r["opposing_type"] == "resistance"


def test_recency_is_recorded_as_age_not_as_freshness():
    """A level swept minutes ago has had its liquidity taken and is WEAKER.
    The naive reading has this backwards."""
    r = _row(levels=[_lvl(102.0, "resistance", last_test_ts=940.0)], now_ts=1_000.0)
    assert r["opposing_age_s"] == pytest.approx(60.0)


def test_value_area_position_reads_the_real_producer():
    from src.volume_profile import VolumeProfileResult
    import dataclasses

    fields = {f.name for f in dataclasses.fields(VolumeProfileResult)}
    assert {"vah", "val"} <= fields, (
        "VolumeProfileResult no longer carries vah/val — this lane reads them "
        "by name and would silently return None"
    )


# ── refusals, each named ──────────────────────────────────────────────────

def test_an_empty_book_and_clear_air_are_different_findings():
    """`dict.get` makes absent and empty indistinguishable, which is exactly
    why `level_book_levels` went missing for four evaluators without anything
    being able to observe it. Pooling these would report a data fault when the
    finding is that the path ahead is clear."""
    empty = _row(levels=[])
    assert REFUSE_NO_LEVELS in empty["refusals"]

    clear = _row(levels=[_lvl(95.0, "resistance")], entry=100.0)
    assert REFUSE_NO_OPPOSING in clear["refusals"]
    assert REFUSE_NO_LEVELS not in clear["refusals"]


def test_a_missing_value_area_is_named_not_guessed():
    r = _row(value_area=None)
    assert r["value_area_pos"] is None
    assert "no_value_area" in r["refusals"]


def test_no_feature_degrades_to_zero():
    """A missing level book is not a clear path, and rendering it as one is how
    a broken measurement looks like agreement."""
    r = _row(levels=[], value_area=None)
    for k in ("opposing_dist_atr", "opposing_dist_pct", "opposing_inside_tp1",
              "opposing_score", "opposing_age_s", "value_area_pos"):
        assert r[k] is None, f"{k} degraded to a value instead of refusing"


def test_metadata_is_not_reclassified_by_line_order():
    """Whether a value counts as a feature must not depend on where its line
    sits in a function — `stack_sep_pct` could never be reported dark because
    it was assigned after the missing-accounting."""
    r = _row()
    features = set(r) - ROW_METADATA_KEYS
    # Pinned exactly. A path stamping twelve features invites twelve
    # thresholds, and twelve cells against a book this size guarantees a
    # spurious winner — so a new feature has to be a deliberate act that
    # updates this list, not something that appears by being assigned above
    # the accounting.
    assert features == {
        "opposing_dist_atr", "opposing_dist_pct", "opposing_inside_tp1",
        "opposing_score", "opposing_age_s", "value_area_pos",
    }, features
    # The level's identity describes the row; it does not measure the setup.
    for k in ("signal_id", "symbol", "side", "entry", "tp1", "opposing_price"):
        assert k in ROW_METADATA_KEYS
    # Written later — by `stamp` and by the retention ring — so they are
    # legitimately absent here and must not be mistaken for features.
    assert ROW_METADATA_KEYS - set(r) == {
        "delivered", "delivered_at", "veto_mode", "veto_would_reject",
    }


# ── the gate ──────────────────────────────────────────────────────────────

def test_the_gate_abstains_while_measuring():
    r = _row(levels=[_lvl(102.0, "resistance")], entry=100.0, tp1=104.0)
    r["veto_mode"] = "measure"
    r["veto_would_reject"] = True
    assert should_suppress(r) is False, "a measuring lane suppressed a candidate"


def test_the_gate_rejects_only_when_enforcing():
    r = _row(levels=[_lvl(102.0, "resistance")], entry=100.0, tp1=104.0)
    r["veto_mode"] = "enforce"
    r["veto_would_reject"] = True
    assert should_suppress(r) is True


def test_unknown_abstains():
    """Fail-open is deliberate: the input is a measurement lane, and a
    fail-closed rule would kill the feed the moment the LevelBook went dark —
    indistinguishable from a quiet market."""
    r = _row(levels=[])
    assert r["opposing_inside_tp1"] is None
    assert would_reject(r) is False


def test_enforcement_is_gated_per_path(monkeypatch):
    """One flip must not move nineteen paths on evidence from the one that is
    59% of the book."""
    import config
    from src.structural_veto import enforcing_for

    monkeypatch.setattr(config, "STRUCTURAL_VETO_ENFORCE", True, raising=False)
    monkeypatch.setattr(config, "STRUCTURAL_VETO_ENFORCE_PATHS", "", raising=False)
    assert enforcing_for("MOVER_TREND_PULLBACK") is False, (
        "an empty allow-list enforced everywhere"
    )

    monkeypatch.setattr(
        config, "STRUCTURAL_VETO_ENFORCE_PATHS", "MOVER_TREND_PULLBACK", raising=False,
    )
    assert enforcing_for("MOVER_TREND_PULLBACK") is True
    assert enforcing_for("TREND_PULLBACK_EMA") is False


# ── retention comes from Phase 6, not a third copy ────────────────────────

def test_the_ledger_retains_by_delivery():
    from src.structural_veto import VetoLedger

    led = VetoLedger(path="", max_rows=3)
    led.add({"signal_id": "keep", "stamped_at": 1.0})
    assert led.mark_delivered("keep") is True
    for i in range(30):
        led.add({"signal_id": f"x{i}", "stamped_at": float(i + 2)})
    assert "keep" in {r["signal_id"] for r in led.rows()}
    assert led.retention()["n_delivered"] == 1


# ── revert-checks: these fail against the pre-fix tree ────────────────────

def test_the_lane_is_stamped_at_the_enqueue_choke_point():
    """Pins the CALL SITE, not the import. `opposing_inside_tp1` asks about
    `sig.tp1`, which is rewritten four times between the evaluator and here."""
    src = (REPO / "src" / "scanner" / "__init__.py").read_text()
    assert "structural_veto" in src
    assert "_veto.stamp(" in src
    assert "self.level_book.get_levels(sig.symbol)" in src

    tree = ast.parse(src)
    fn = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != "_enqueue_signal":
            continue
        for inner in ast.walk(node):
            if (
                isinstance(inner, ast.Call)
                and isinstance(inner.func, ast.Attribute)
                and inner.func.attr == "stamp"
                and getattr(inner.func.value, "id", None) == "_veto"
            ):
                fn = node
    assert fn is not None, "the veto is not stamped inside _enqueue_signal"


def test_the_consuming_half_ships_in_the_same_change():
    """A setting the engine stores but does not consume is a scaffold, and
    scaffolds are banned. The gate is real and suppression-stamped."""
    src = (REPO / "src" / "scanner" / "__init__.py").read_text()
    assert "_veto.should_suppress(" in src
    assert 'structural_veto:target_behind_level' in src


def test_both_flags_exist_and_default_dark():
    import config
    assert config.STRUCTURAL_VETO_MEASURE is True     # measurement ON
    assert config.STRUCTURAL_VETO_ENFORCE is False    # effect OFF
    assert config.STRUCTURAL_VETO_ENFORCE_PATHS == ""  # and nowhere
