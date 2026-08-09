"""The ATR-trail lane: four populations, four files, and the wiring that fills them.

Two kinds of test here, and the second kind is the one that matters.

**Behaviour** — an ATR arm opens, walks, closes on its own trail, and its
terminal state is named apart from a SAR flip.

**Seams** — the defect shape this repo keeps paying for is two halves that each
look complete: written but read by nothing, stamped but never flushed, flushed
but never loaded, built but never called. None of those crash and none leave an
empty screen. So the wiring tests parse the **call sites** rather than checking
that a function exists: ``atr_trail_live.sweep`` being importable says nothing
about whether anything calls it, and *defining a method is not calling it*.
"""
from __future__ import annotations

import ast
import json
import pathlib

import pytest

from src import atr_trail_live as atr
from src import sar_live_shadow as arms
from src import trail_mechanisms as tm

ROOT = pathlib.Path(__file__).resolve().parents[1]
BAR_MS = 900_000.0
PERIOD, MULT = 5, 2.0
PARAMS = {"period": float(PERIOD), "mult": MULT}


def _series(bars):
    return {
        "open": [b[0] for b in bars],
        "high": [b[1] for b in bars],
        "low": [b[2] for b in bars],
        "close": [b[3] for b in bars],
        "open_time": [1_700_000_000_000.0 + i * BAR_MS for i in range(len(bars))],
    }


def _rising(n, start=100.0, step_up=1.0):
    return [
        (start + i * step_up, start + i * step_up + 0.5,
         start + i * step_up - 0.5, start + i * step_up)
        for i in range(n)
    ]


def _now_at(bar_index, width_sec=BAR_MS / 1000.0):
    return (1_700_000_000_000.0 + bar_index * BAR_MS) / 1000.0 + width_sec


def _point(bars, side, state):
    s = _series(bars)
    ctx = tm.prepare(tm.MECH_CHANDELIER, s["high"], s["low"], s["close"], PARAMS)
    return tm.point(
        tm.MECH_CHANDELIER, ctx, s["high"], s["low"], s["close"],
        len(s["high"]) - 1, side=side, state=state, params=PARAMS,
        last_closed_ms=s["open_time"][-1],
    )


def _arm(bars, side="LONG", entry=None, sl=None, tp1=None):
    s = _series(bars)
    entry = s["close"][-1] if entry is None else entry
    state: dict = {}
    return arms.new_arm(
        signal_id="SIG-ATR",
        symbol="TESTUSDT",
        side=side,
        setup_class="MOVER_TREND_PULLBACK",
        timeframe="15m",
        entry=entry,
        stop_loss=entry * 0.97 if sl is None else sl,
        tp1=entry * 1.05 if tp1 is None else tp1,
        point=_point(bars, side, state),
        opened_ms=s["open_time"][-1],
        mechanism=tm.MECH_CHANDELIER,
        mech_params=PARAMS,
        mech_state=state,
        now_ts=_now_at(len(bars) - 1),
    )


# --------------------------------------------------------------------------- #
# The arm runs the chandelier, and says so
# --------------------------------------------------------------------------- #


def test_an_atr_arm_stamps_which_mechanism_produced_its_levels():
    arm = _arm(_rising(40))
    assert arm["mechanism"] == tm.MECH_CHANDELIER
    assert arm["mech_params"]["period"] == float(PERIOD)
    # The ratchet lives on the row, so it survives a restart with the arm rather
    # than being re-derived from whatever window the store happens to hold.
    assert arm["mech_state"]["trail_extreme"] > 0


def test_the_chandelier_governs_from_bar_one_when_its_level_is_not_breached():
    arm = _arm(_rising(40))
    assert arm["aligned_at_entry"] is True
    assert arm["governor"] == arms.GOV_SAR
    assert arm["sar_stop"] < arm["entry"]
    # No direction of its own — None, never False.
    assert arm["sar_up"] is None


def test_the_trail_exit_is_named_apart_from_a_sar_flip():
    """A SAR breach is a *reversal*; a chandelier stop is simply touched.

    Handing a reader the same word for two different events is how a page stops
    being able to say what happened, so the two mechanisms carry two terminal
    states — and the lanes never pool, so nothing is lost by naming them.
    """
    bars = _rising(40)
    arm = _arm(bars)
    parked = float(arm["sar_stop"])
    # One bar that trades straight through the parked stop.
    breach = (parked + 0.4, parked + 0.5, parked - 3.0, parked - 2.5)
    changed = arms.step_arm(arm, _series(bars + [breach]), now_ts=_now_at(len(bars)))
    assert changed is True
    assert arm["status"] == arms.STATUS_CLOSED_TRAIL_STOP
    assert arm["exit_reason"] == arms.EXIT_TRAIL_STOP
    assert arm["fill_level"] == pytest.approx(parked)


def test_a_gap_through_the_trail_fills_at_the_open_never_better():
    bars = _rising(40)
    arm = _arm(bars)
    parked = float(arm["sar_stop"])
    gap = (parked - 1.5, parked - 1.0, parked - 4.0, parked - 3.5)
    arms.step_arm(arm, _series(bars + [gap]), now_ts=_now_at(len(bars)))
    assert arm["status"] == arms.STATUS_CLOSED_TRAIL_STOP
    assert arm["fill_level"] == pytest.approx(parked - 1.5)


def test_the_parked_stop_ratchets_toward_price_as_the_trade_runs():
    bars = _rising(40)
    arm = _arm(bars)
    first = float(arm["sar_stop"])
    grown = bars + _rising(6, start=bars[-1][0] + 1.0)
    arms.step_arm(arm, _series(grown), now_ts=_now_at(len(grown) - 1))
    assert arm["status"] == arms.STATUS_RUNNING
    assert float(arm["sar_stop"]) > first


def test_an_arm_that_cannot_read_its_mechanism_refuses_rather_than_inventing_one():
    """Fewer bars than the ATR seed. INSUFFICIENT is a state; a guessed level is
    a wrong answer with no signal."""
    bars = _rising(4)
    arm = _arm(bars)
    assert arm["status"] == arms.STATUS_INSUFFICIENT
    assert arm["governor"] is None
    assert arm["sar_stop"] is None


def test_the_held_arm_and_the_stop_rules_ride_the_chandelier_walk_too():
    """The second arm inherits the first's guards only if it rides the first's
    walk — and it must ride the CHANDELIER's walk on this lane, not SAR's."""
    arm = _arm(_rising(40))
    assert arm["hold_status"] == arms.HOLD_OPEN
    assert arm["strategies"], "the stop-management rules are not stamped"


# --------------------------------------------------------------------------- #
# Four populations, four files
# --------------------------------------------------------------------------- #


def test_every_lane_writes_its_own_file():
    """Never one file with a ``mechanism`` column.

    A consumer that has not heard of a second population cannot filter it out,
    whereas a consumer pointed at a file it does not open cannot see it at all.
    """
    paths = {
        arms.SarLiveLedger.DEFAULT_PATH,
        arms.DARK_PATH,
        atr.LIVE_PATH,
        atr.DARK_PATH,
    }
    assert len(paths) == 4, paths


def test_the_filenames_are_the_ones_ops_mounts():
    """Pinned on the PRODUCING side. #817's ``entry_regime`` was read by ops for
    months while nothing wrote it, and the page looked full the whole time."""
    assert atr.LIVE_PATH == "data/atr_trail_arms_v1.json"
    assert atr.DARK_PATH == "data/dark_atr_trail_arms_v1.json"


def test_each_lane_rolls_its_own_health_window():
    keys = {
        arms.lane_of(tm.MECH_SAR, dark=False),
        arms.lane_of(tm.MECH_SAR, dark=True),
        arms.lane_of(tm.MECH_CHANDELIER, dark=False),
        arms.lane_of(tm.MECH_CHANDELIER, dark=True),
    }
    assert len(keys) == 4, keys
    # SAR keeps the bare keys: main.py's probes and the ops surface read them,
    # and prefixing them would silently empty a probe that then reports a
    # healthy zero.
    assert arms.lane_of(tm.MECH_SAR, dark=False) == arms.LANE_LIVE
    assert arms.lane_of(tm.MECH_SAR, dark=True) == arms.LANE_DARK


def test_the_ledger_ships_the_mechanism_manifest_so_ops_keeps_no_copy(tmp_path):
    path = str(tmp_path / "atr.json")
    ledger = arms.SarLiveLedger(path=path, mechanism=tm.MECH_CHANDELIER)
    ledger.add(_arm(_rising(40)))
    assert ledger.flush(force=True) is True
    payload = json.loads(open(path).read())
    assert payload["mechanism"]["key"] == tm.MECH_CHANDELIER
    assert payload["mechanism"]["label"] == "ATR-trail (Chandelier)"
    assert payload["mechanism"]["has_direction"] is False


def test_an_atr_row_carries_every_field_ops_reads():
    from tests.test_sar_live_shadow import OPS_CONTRACT_KEYS

    arm = _arm(_rising(40))
    missing = OPS_CONTRACT_KEYS - set(arm)
    assert not missing, f"ops reads these and the ATR lane does not write them: {missing}"
    assert {"mechanism", "mech_params"} <= set(arm)


# --------------------------------------------------------------------------- #
# Additive schema: the older rows keep their standing
# --------------------------------------------------------------------------- #


def test_a_schema_2_ledger_survives_the_mechanism_bump(tmp_path):
    """The 1 -> 2 bump destroyed 371 rows because its loader compared ``!=``
    while its comment promised nothing would be purged. This asserts the
    promise rather than restating it."""
    path = str(tmp_path / "arms.json")
    with open(path, "w") as fh:
        json.dump(
            {
                "schema": 2,
                "open": [{"arm_id": "OLD:15m", "status": arms.STATUS_RUNNING,
                          "signal_id": "OLD", "timeframe": "15m"}],
                "resolved": [{"arm_id": "DONE:5m", "status": arms.STATUS_CLOSED_SL,
                              "signal_id": "DONE", "timeframe": "5m"}],
            },
            fh,
        )
    ledger = arms.SarLiveLedger(path=path)
    ledger.load()
    assert len(ledger.open_arms()) == 1
    assert len(ledger.resolved_arms()) == 1


def test_pre_mechanism_rows_are_labelled_not_left_blank(tmp_path):
    """A blank ``mechanism`` beside rows that carry one reads as the engine
    having stopped stamping. Every row written before schema 3 was SAR — that
    is a fact, not a guess, because SAR was the only mechanism there was."""
    path = str(tmp_path / "arms.json")
    with open(path, "w") as fh:
        json.dump({"schema": 2, "open": [], "resolved": [
            {"arm_id": "OLD:15m", "signal_id": "OLD", "timeframe": "15m",
             "status": arms.STATUS_CLOSED_SAR_FLIP},
        ]}, fh)
    ledger = arms.SarLiveLedger(path=path)
    ledger.load()
    assert ledger.resolved_arms()[0]["mechanism"] == tm.MECH_SAR


def test_a_chandelier_ledger_does_not_label_old_rows_sar(tmp_path):
    """The label comes from the FILE's mechanism, not from a constant."""
    path = str(tmp_path / "atr.json")
    with open(path, "w") as fh:
        json.dump({"schema": 2, "open": [], "resolved": [
            {"arm_id": "OLD:15m", "signal_id": "OLD", "timeframe": "15m",
             "status": arms.STATUS_CLOSED_SL},
        ]}, fh)
    ledger = arms.SarLiveLedger(path=path, mechanism=tm.MECH_CHANDELIER)
    ledger.load()
    assert ledger.resolved_arms()[0]["mechanism"] == tm.MECH_CHANDELIER


def test_get_ledger_calls_load_rather_than_merely_having_one(tmp_path, monkeypatch):
    """Flush without load actively DELETES a window on every deploy while the
    page reports a healthy ledger. Defining a method is not calling it."""
    path = tmp_path / "atr.json"
    path.write_text(json.dumps({
        "schema": arms.LEDGER_SCHEMA, "open": [], "resolved": [
            {"arm_id": "R:15m", "signal_id": "R", "timeframe": "15m",
             "status": arms.STATUS_CLOSED_TRAIL_STOP},
        ],
    }))
    monkeypatch.setattr(atr, "LIVE_PATH", str(path))
    atr.reset_ledgers()
    try:
        assert len(atr.get_ledger().resolved_arms()) == 1
    finally:
        atr.reset_ledgers()


# --------------------------------------------------------------------------- #
# The seams — parse the call site, never the import
# --------------------------------------------------------------------------- #


def _calls(path: str):
    """Every ``a.b(...)`` attribute call in a module, as ``"a.b"`` strings."""
    tree = ast.parse((ROOT / path).read_text())
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            val = node.func.value
            if isinstance(val, ast.Name):
                out.add(f"{val.id}.{node.func.attr}")
    return out


def test_the_monitor_loop_opens_and_sweeps_the_live_atr_lane():
    calls = _calls("src/trade_monitor.py")
    assert "atr_trail_live.observe_signal" in calls, (
        "nothing opens an ATR arm on a delivered signal — the lane would be "
        "empty and the page would render a quiet market"
    )
    assert "atr_trail_live.sweep" in calls, (
        "arms are opened and never advanced: every stop freezes at its anchor "
        "and the rows render as live trades forever (#835)"
    )


def test_the_scanner_opens_an_atr_arm_on_every_dark_row():
    src = (ROOT / "src/scanner/__init__.py").read_text()
    assert "_atr.observe_signal(sig, self.data_store, dark=True)" in src, (
        "the dark feed is the population the owner asked the question about — "
        "the delivered book is ~59% one path"
    )


def test_the_maintenance_loop_sweeps_the_dark_atr_lane():
    src = (ROOT / "src/main.py").read_text()
    assert "_atr_dark.sweep" in src
    assert "_atr_dark.get_dark_ledger().flush(force=True)" in src, (
        "a ledger nobody flushes is data that exists only in memory, and a "
        "flush that is not forced stops writing when the lane goes idle — "
        "which ops renders as STALE, a fault that is not happening"
    )


def test_both_atr_lanes_have_a_liveness_probe():
    src = (ROOT / "src/main.py").read_text()
    assert 'name="atr_trail_live_arms"' in src
    assert 'name="dark_atr_trail_arms"' in src


def test_the_measurement_flag_ships_ON():
    """§ Project Phase: a dark measurement shipped OFF produces an empty ops
    panel and a decision that keeps getting deferred. These arms place no
    orders and change no exit, so there is nothing for an OFF default to
    protect."""
    from config import ATR_TRAIL_LIVE_ENABLED

    assert ATR_TRAIL_LIVE_ENABLED is True
