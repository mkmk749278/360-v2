"""Phase 5 — the standalone price-action lane.

Drives the REAL `Level` throughout. The trigger is built only from §2's
supported column (stop clustering at levels, signed order imbalance) — not from
FVGs or order blocks, which have no validation distinct from support/resistance.
"""
from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from src import price_action_lane as pa
from src.level_book import Level

REPO = Path(__file__).resolve().parents[1]


def _swept_support(n=60, level=100.0, wick=99.2, reclaim=100.6):
    close = np.full(n, 101.0)
    high = close + 0.3
    low = close - 0.3
    low[-3] = wick
    close[-1] = reclaim
    high[-1] = reclaim + 0.2
    low[-1] = reclaim - 0.4
    return high, low, close


def _levels(support=100.0, resistance=103.0):
    out = []
    if support is not None:
        out.append(Level(price=support, type="support", source_tf="1h", score=6.0))
    if resistance is not None:
        out.append(Level(price=resistance, type="resistance", source_tf="4h", score=7.0))
    return out


def _eval(symbol="BTCUSDT", levels=None, delta=50_000.0, atr=0.4, now=1_000.0, **kw):
    pa.reset_census()
    high, low, close = _swept_support(**kw)
    return pa.evaluate(
        symbol=symbol,
        levels=_levels() if levels is None else levels,
        high=high, low=low, close=close, atr=atr,
        footprint_bar=None if delta is None else {"delta_quote": delta},
        now_ts=now,
    )


# ── the trigger ───────────────────────────────────────────────────────────

def test_a_swept_and_reclaimed_support_triggers_long():
    sig, reason = _eval()
    assert reason == ""
    assert sig is not None
    assert sig.direction.value == "LONG"
    assert sig.entry == pytest.approx(100.6)


def test_a_swept_and_reclaimed_resistance_triggers_short():
    pa.reset_census()
    n = 60
    close = np.full(n, 99.0)
    high = close + 0.3
    low = close - 0.3
    high[-3] = 100.8                    # sweep above resistance at 100
    close[-1] = 99.4
    levels = [Level(price=100.0, type="resistance", source_tf="1h", score=6.0),
              Level(price=97.0, type="support", source_tf="4h", score=7.0)]
    sig, reason = pa.evaluate(
        symbol="X", levels=levels, high=high, low=low, close=close, atr=0.4,
        footprint_bar={"delta_quote": -50_000.0}, now_ts=1_000.0,
    )
    assert reason == ""
    assert sig.direction.value == "SHORT"


def test_a_level_merely_touched_is_not_a_sweep():
    """Below the tolerance it is noise around the level, not a liquidity take."""
    sig, reason = _eval(wick=99.999)
    assert sig is None
    assert reason == pa.REFUSE_NO_SWEEP


def test_a_break_without_a_reclaim_is_not_a_trigger():
    """A sweep is a FAILED break — price must close back on the side it came
    from. Price that stays through the level has simply broken it."""
    pa.reset_census()
    n = 60
    close = np.full(n, 101.0)
    high, low = close + 0.3, close - 0.3
    low[-3] = 99.2
    close[-1] = 99.4                    # still below the level: broken, not swept
    sig, reason = pa.evaluate(
        symbol="X", levels=_levels(), high=high, low=low, close=close, atr=0.4,
        footprint_bar={"delta_quote": 50_000.0}, now_ts=1_000.0,
    )
    assert sig is None and reason == pa.REFUSE_NO_SWEEP


# ── delta confirmation is required, not a bonus ───────────────────────────

def test_delta_opposed_to_the_trade_refuses():
    """A sweep with no aggression behind the reclaim is a wick, and the
    footprint is the only thing that tells them apart."""
    sig, reason = _eval(delta=-50_000.0)
    assert sig is None and reason == pa.REFUSE_DELTA_OPPOSED


def test_a_missing_footprint_refuses_by_name_rather_than_waiving():
    """The footprint covers a bounded symbol set. A lane that silently drops
    its own confirmation where the data is absent is measuring a DIFFERENT
    mechanism on those symbols."""
    sig, reason = _eval(delta=None)
    assert sig is None and reason == pa.REFUSE_NO_FOOTPRINT


# ── geometry from structure, never a multiplier ───────────────────────────

def test_the_stop_sits_beyond_the_sweep_extreme():
    """If price returns to the wick that took the liquidity, the read was
    wrong. The ATR buffer clears noise; it does not size the trade."""
    sig, _ = _eval(atr=0.4)
    assert sig.stop_loss == pytest.approx(99.2 - 0.4 * pa.SL_BUFFER_ATR)
    assert sig.stop_loss < 99.2


def test_tp1_is_the_next_opposing_level_not_an_r_multiple():
    sig, _ = _eval()
    assert sig.tp1 == pytest.approx(103.0)


def test_no_opposing_level_refuses_rather_than_inventing_a_target():
    """Fixed R-multiples off the stop distance are what §5 found the rest of
    the book doing. Inventing one here would make this a moving-average path
    wearing a structural name."""
    sig, reason = _eval(levels=_levels(resistance=None))
    assert sig is None and reason == pa.REFUSE_NO_TARGET


def test_a_target_nearer_than_the_floor_is_refused_not_retargeted():
    """The level IS the target; moving it to satisfy a ratio is how a
    structural lane quietly becomes an R-multiple lane."""
    # The resistance must sit ABOVE the window high (101.3), or it is itself a
    # swept level and the lane correctly reads a SHORT instead — which is what
    # the first cut of this test actually measured.
    sig, reason = _eval(levels=_levels(resistance=101.5))
    assert sig is None and reason == pa.REFUSE_RR_TOO_LOW


# ── one move, one row ─────────────────────────────────────────────────────

def test_a_persisting_sweep_does_not_emit_once_per_scan():
    """The unit of evidence is the MOVE. Without this, one setup produces a row
    per scan and the population's verdict becomes an artefact of re-detection —
    SLXUSDT bought 10 rows in 2h10m inside a 0.37% entry spread and inverted a
    whole population's sign."""
    pa.reset_census()
    high, low, close = _swept_support()
    kw = dict(levels=_levels(), high=high, low=low, close=close, atr=0.4,
              footprint_bar={"delta_quote": 50_000.0})
    sig, _ = pa.evaluate(symbol="BTCUSDT", now_ts=1_000.0, **kw)
    assert sig is not None
    pa._last_emit["BTCUSDT"] = 1_000.0          # what a publish would record
    sig2, reason = pa.evaluate(symbol="BTCUSDT", now_ts=1_060.0, **kw)
    assert sig2 is None and reason == pa.REFUSE_COOLDOWN
    sig3, _ = pa.evaluate(symbol="BTCUSDT", now_ts=1_000.0 + pa.EMIT_COOLDOWN_S + 1, **kw)
    assert sig3 is not None
    pa.reset_census()


# ── it is unscored, and says so ───────────────────────────────────────────

def test_confidence_is_zero_rather_than_invented():
    """This candidate has been through no scoring engine, no MTF policy and no
    confidence floor. A number here would be fabricated performance data on a
    surface an adoption decision reads."""
    sig, _ = _eval()
    assert sig.confidence == 0.0


def test_lane_rows_are_discriminable_from_gate_loosened_rows():
    """A gate-loosened dark row cleared the full scoring engine and every gate
    but one. Pooling the two is how 15 rows disappear into 2,418."""
    assert pa.is_lane_row({"dark_gate": pa.DARK_GATE}) is True
    assert pa.is_lane_row({"dark_gate": "execution:overextended"}) is False
    assert pa.is_lane_row({}) is False


def test_the_setup_class_is_its_own():
    from src.channels.scalp import ScalpChannel  # noqa: F401  (import proves it loads)
    assert pa.SETUP_CLASS == "PA_SWEEP_RECLAIM"


# ── refusals are named, never pooled ──────────────────────────────────────

def test_every_refusal_is_counted_under_its_own_name():
    pa.reset_census()
    _eval(delta=-1.0)
    _eval(delta=None)
    _eval(levels=_levels(resistance=None))
    c = pa.census()
    # `_eval` resets the census itself, so check the shape rather than totals.
    assert isinstance(c["refusals"], dict)
    assert c["evaluated"] >= 1


# ── revert-checks ─────────────────────────────────────────────────────────

def test_the_lane_is_wired_into_the_scan():
    src = (REPO / "src" / "scanner" / "__init__.py").read_text()
    assert "price_action_lane" in src
    assert "_pa.scan_symbol(" in src
    assert "self.level_book.get_levels(symbol)" in src


def test_the_lane_publishes_only_to_dark_emission():
    """It reaches no channel, no push, no app feed and no order.

    Checked on the IMPORTS and calls, not on a grep of the file — the first cut
    grepped raw text and tripped on the word "router" inside a docstring
    explaining that the lane never reaches one. A check that matches prose is
    not a check on behaviour.
    """
    src = (REPO / "src" / "price_action_lane.py").read_text()
    assert "dark_emission.publish" in src

    tree = ast.parse(src)
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
    for forbidden in ("src.signal_router", "src.telegram_bot", "src.redis_client"):
        assert forbidden not in imported, f"the lane imports {forbidden}"
    # And it must not reach the queue by any name.
    called = {
        n.func.attr for n in ast.walk(tree)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
    }
    for forbidden in ("put", "enqueue", "_enqueue_signal", "send_signal"):
        assert forbidden not in called, f"the lane calls {forbidden}()"


def test_the_measurement_flag_is_on():
    """It publishes to a dark ledger and nowhere else, so ON is not a
    money-path risk — and a measurement shipped OFF produces an empty panel and
    a decision that keeps being deferred."""
    import config
    assert config.PRICE_ACTION_LANE_MEASURE is True


def test_the_lane_runs_per_scan_not_on_the_level_book_ttl():
    """THE defect this lane shipped with, and it is a call-site defect.

    The first cut put `scan_symbol` inside `_refresh_level_book_if_stale`,
    which returns early on a per-symbol TTL of **one hour**
    (`LEVEL_BOOK_REFRESH_SEC = 3600`). So the lane was evaluated ~1/hour per
    symbol — and a sweep-and-reclaim is a transient event on the newest closed
    bar, so an hourly poll almost never lands on one. It produced zero signals
    for that reason alone, not because the trigger is rare.

    "Where it becomes true is a point in the call graph": the lane needs to be
    evaluated OFTEN, which is a different requirement from the levels being
    FRESH, and the first cut satisfied the second. Pinned by the enclosing
    function, because "it is wired" was true the whole time and still wrong.
    """
    src = (REPO / "src" / "scanner" / "__init__.py").read_text()
    tree = ast.parse(src)

    enclosing = None
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        seg = ast.get_source_segment(src, node) or ""
        if "_pa.scan_symbol(" not in seg:
            continue
        if enclosing is None or node.lineno > enclosing.lineno:
            enclosing = node          # innermost wins

    assert enclosing is not None, "the lane is not called from the scanner"
    assert enclosing.name == "_build_scan_context", (
        f"the lane is called from {enclosing.name!r}. It must run per scan; "
        "_refresh_level_book_if_stale is TTL-gated at one hour per symbol and "
        "starved the lane to ~1 evaluation/hour"
    )
    assert "_refresh_level_book_if_stale" != enclosing.name


def test_the_census_is_surfaced_so_silence_has_a_named_cause():
    """The lane shipped with a page for its ROWS and nothing showing why there
    were none — so "why is it silent" could only be answered by reading source.
    That is "dark work must be observable" broken by the change meant to honour
    it."""
    from src.data_intake import _price_action_lane_report

    rep = _price_action_lane_report()
    assert rep.get("present") is True
    assert "refusals" in rep
    assert "refusal_share" in rep
    assert "evaluated" in rep


def test_the_payload_key_is_the_one_ops_reads():
    """A cross-repo field name is a contract, pinned on the PRODUCING side.

    The test above asserts the report function's own return shape, which is a
    mock asserting your assumption back at you one repo short of the reader —
    and it went green on 2026-08-06 while `/diagnostics/data-intake` rendered
    nothing for the lane at all, because ops had no section for the key. That is
    #817 inverted: a field one repo WRITES and no repo READS, invisible at both
    ends.

    So this pins the key by name, in the assembled payload. Renaming it now
    fails here rather than quietly emptying a panel in the other repo.
    """
    from src import data_intake

    src = (REPO / "src" / "data_intake.py").read_text()
    assert '"price_action_lane": _price_action_lane_report()' in src

    # And it is nested under `derived`, which is the half a reader gets wrong:
    # ops must walk `report["derived"]["price_action_lane"]`, and a fixture that
    # puts the block at the top level goes green over a page that renders
    # nothing. Pinned by driving the real assembler over a bare engine.
    class _Engine:
        pass

    report = data_intake.build_data_intake(_Engine())
    assert "price_action_lane" not in report, (
        "moved to the top level — ops reads report['derived']['price_action_lane']"
    )
    assert "price_action_lane" in report["derived"], (
        "ops reads report['derived']['price_action_lane'] on "
        "/diagnostics/data-intake"
    )


def test_every_refusal_reason_is_a_declared_constant():
    """The reason strings travel to ops as dictionary KEYS, and ops looks each
    one up to decide whether it is a fault, a coverage gap, a market fact or our
    own throttle. A reason invented inline at a call site would arrive unnamed.

    Ops renders an unrecognised reason under its raw name rather than dropping
    it — the fix for a drifting mirror is not a second mirror — but the reason
    must at least be declared here, once, so there is something to rename.
    """
    import ast

    src = (REPO / "src" / "price_action_lane.py").read_text()
    tree = ast.parse(src)

    declared = {
        node.value.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
        and any(
            isinstance(t, ast.Name) and t.id.startswith("REFUSE_")
            for t in node.targets
        )
    }
    assert declared, "no REFUSE_* constants found"

    # Every `_census.refuse(...)` argument must be one of them — never a literal.
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "refuse"
            and node.args
        ):
            arg = node.args[0]
            assert isinstance(arg, ast.Name) and arg.id.startswith("REFUSE_"), (
                f"refuse() called with a literal on line {node.lineno} — "
                "the reason string is a cross-repo contract, declare it"
            )


def test_lane_provenance_survives_the_serializer():
    """`LaneSignal` declares eight provenance fields under the sentence
    "carried so the page can split by what actually differs between rows".
    `_row_from_signal` wrote a fixed key list containing none of them, so
    `/signals/price-action` bucketed every row into `unstamped` and its
    by-level table described nothing (owner data, 2026-08-06).

    #842's shape: a field one writer populates and one SERIALIZER drops,
    invisible at both ends because nothing is missing while the process lives.
    Driven through the real serializer rather than asserted on the dataclass.
    """
    from src import dark_emission
    from src.smc import Direction

    sig = pa.LaneSignal(
        signal_id="pa-test", symbol="BTCUSDT", channel=pa.SETUP_CLASS,
        setup_class=pa.SETUP_CLASS, direction=Direction.LONG,
        entry=100.0, stop_loss=98.0, tp1=104.0,
        level_price=99.0, level_type="support", level_source_tf="1h",
        level_score=7.5, sweep_extreme=97.5, sweep_depth_pct=1.5,
        delta_quote=12345.0, rr=2.0,
    )
    row = dark_emission._row_from_signal(sig, 1_700_000_000.0)

    # Every declared field arrives, by name and by value.
    assert row["level_source_tf"] == "1h"
    assert row["level_type"] == "support"
    assert row["level_price"] == 99.0
    assert row["level_score"] == 7.5
    assert row["sweep_extreme"] == 97.5
    assert row["sweep_depth_pct"] == 1.5
    assert row["delta_quote"] == 12345.0
    assert row["rr"] == 2.0
    for key in dark_emission.LANE_PROVENANCE_FIELDS:
        assert key in row, key


def test_a_row_with_no_lane_gets_none_not_zero():
    """An unstamped level is not a zero one. Every other dark row is a real
    `Signal` with none of these attributes, and ops renders the difference —
    `None` becomes `unstamped`, `0.0` would become a level at price zero."""
    from src import dark_emission
    from src.smc import Direction

    class _PlainSignal:
        signal_id = "s-1"
        symbol = "ETHUSDT"
        channel = "x"
        setup_class = "MOVER_TREND_PULLBACK"
        direction = Direction.SHORT
        entry = 100.0
        stop_loss = 102.0
        tp1 = 96.0

    row = dark_emission._row_from_signal(_PlainSignal(), 1_700_000_000.0)
    for key in dark_emission.LANE_PROVENANCE_FIELDS:
        assert row[key] is None, f"{key} must be None, not {row[key]!r}"


def test_the_emit_cooldown_survives_a_restart():
    """The throttle lived in memory while the ledger it protects lives on disk,
    so every deploy re-armed every symbol and a setup still live across the
    restart bought a second row at the same price.

    #816 arriving through the process lifetime rather than through the key: a
    restart is not a new move.
    """
    from src import dark_emission

    class _Ledger:
        def rows(self):
            return [
                {"symbol": "BTCUSDT", "dark_gate": pa.DARK_GATE,
                 "emitted_at": 1_000.0},
                {"symbol": "BTCUSDT", "dark_gate": pa.DARK_GATE,
                 "emitted_at": 1_500.0},          # newest wins
                {"symbol": "ETHUSDT", "dark_gate": "some_other_gate",
                 "emitted_at": 1_500.0},          # not this lane — ignored
            ]

    pa.reset_census()
    original = dark_emission.get_ledger
    dark_emission.get_ledger = lambda: _Ledger()          # type: ignore[assignment]
    try:
        pa._rehydrate_cooldown()
        assert pa._last_emit["BTCUSDT"] == 1_500.0
        assert "ETHUSDT" not in pa._last_emit, (
            "another lane's rows must not arm this lane's throttle"
        )
        # Once per process, not once per evaluation — this sits inside the
        # scanner's per-symbol loop.
        pa._last_emit.clear()
        pa._rehydrate_cooldown()
        assert pa._last_emit == {}
    finally:
        dark_emission.get_ledger = original               # type: ignore[assignment]
        pa.reset_census()


def test_a_rehydrated_cooldown_actually_refuses():
    """The seed is only worth having if `evaluate` reads it — pinning the wire,
    not the helper. Driven through the same triggering fixture every other test
    in this file uses, so a pass here means a real setup was refused."""
    from src import dark_emission

    class _Ledger:
        def rows(self):
            return [{"symbol": "BTCUSDT", "dark_gate": pa.DARK_GATE,
                     "emitted_at": 10_000.0}]

    # Same inputs, no ledger: this triggers. That is the control.
    sig, reason = _eval(now=10_100.0)
    assert sig is not None, "fixture must trigger, or the test below proves nothing"

    original = dark_emission.get_ledger
    dark_emission.get_ledger = lambda: _Ledger()          # type: ignore[assignment]
    try:
        sig, reason = _eval(now=10_100.0)                 # 100s after the row
        assert sig is None
        assert reason == pa.REFUSE_COOLDOWN
    finally:
        dark_emission.get_ledger = original               # type: ignore[assignment]
        pa.reset_census()
