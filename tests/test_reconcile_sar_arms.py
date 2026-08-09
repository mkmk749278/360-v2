"""Tests for the SAR arm reconciliation diagnostic.

**Every arm in here is built by driving the real ``parabolic_sar_live``**, never
by hand-writing a level. A hand-written expectation asserts the author's
assumption back at them and goes green over dead code — the defect this repo
paid for twice (``classify_pending``'s ``exit_reason`` key, and
``entry_features.zone_distance_atr`` reading five key names that
``smc.FVGZone`` has never produced). Here the collaborator whose output matters
is the SAR projection itself, so the fixture calls it.

The load-bearing test is :func:`test_wrong_stop_is_caught`: a reconciliation
that cannot fail is not a reconciliation. It is the "verify a fix by reverting
it" rule expressed as a permanent test.
"""

from __future__ import annotations

import math
import random

import pytest

from scripts.reconcile_sar_arms import (
    MIN_SEED_WARMUP_BARS,
    R_BAR_MISSING,
    R_NO_BAR_MS,
    R_NO_STOP,
    R_SEED_SENSITIVE,
    R_SHORT_WARMUP,
    TOL_PCT,
    _Refusal,
    check_arm,
    load_arms,
    reconstruct,
)
from src.sar_exit_shadow import parabolic_sar_live

STEP, MAX_STEP = 0.02, 0.2
SEEDS = (0, 60, 120)


def _bars(n: int = 400) -> list[tuple[int, float, float, float, float]]:
    """A deterministic OHLC series with real trend reversals in it.

    Two overlaid sine waves of different periods, so SAR genuinely flips
    repeatedly rather than trending one way for the whole window — a series
    with no flips would let a broken projection pass.
    """
    out = []
    for i in range(n):
        base = 100.0 + 12.0 * math.sin(i / 23.0) + 4.0 * math.sin(i / 7.0)
        hi = base + 0.9
        lo = base - 0.9
        op = base - 0.3
        cl = base + 0.3
        out.append((1_700_000_000_000 + i * 900_000, op, hi, lo, cl))
    return out


def _arm_at(bars, idx: int, *, status: str = "RUNNING", side: str = "LONG") -> dict:
    """An arm carrying the stop ``step_arm`` would have parked after ``idx``."""
    live = parabolic_sar_live(
        [b[2] for b in bars[: idx + 1]], [b[3] for b in bars[: idx + 1]], STEP, MAX_STEP
    )
    assert live is not None
    return {
        "arm_id": f"sig-{idx}:15m",
        "symbol": "TESTUSDT",
        "timeframe": "15m",
        "status": status,
        "side": side,
        "entry": bars[idx][4],
        "last_bar_ms": bars[idx][0],
        "sar_stop": live.next_stop,
        "sar_up": live.up,
    }


# --------------------------------------------------------------------------- #
# The check agrees with a correctly-recorded arm
# --------------------------------------------------------------------------- #


def test_running_arm_reconciles_exactly():
    bars = _bars()
    arm = _arm_at(bars, 350)
    out = check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert out["match"] is True
    assert out["gap_pct"] <= TOL_PCT
    assert out["dir_match"] is True
    assert out["seeds"] >= 2, "at least two independent seeds must have agreed"


def test_closed_arm_reconciles_off_the_bar_before_the_breach():
    """A closed arm's parked stop comes from the bar *before* its last one.

    ``step_arm`` parks ``live(0..i).next_stop`` after a bar that does not
    breach; when bar *i* breaches it closes and leaves the earlier stop in
    place. Reconciling a closed arm against its own ``last_bar_ms`` would
    therefore report a mismatch on every correctly-recorded closed row — the
    bug this test exists to prevent.
    """
    bars = _bars()
    idx = 350
    prev = parabolic_sar_live(
        [b[2] for b in bars[:idx]], [b[3] for b in bars[:idx]], STEP, MAX_STEP
    )
    arm = {
        "arm_id": "sig-c:15m",
        "symbol": "TESTUSDT",
        "timeframe": "15m",
        "status": "CLOSED_SAR_FLIP",
        "side": "LONG",
        "entry": bars[idx][4],
        "last_bar_ms": bars[idx][0],
        "sar_stop": prev.next_stop,
        "sar_up": prev.up,
    }
    out = check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert out["match"] is True, "closed arms must reconcile off the prior bar"


def test_closed_arm_reconciled_against_its_own_bar_would_fail():
    """Pins the asymmetry above: the naive comparison really is wrong.

    Without this, a future 'simplification' that drops the closed-arm branch
    would still pass every other test in this file.
    """
    bars = _bars()
    idx = 350
    arm = _arm_at(bars, idx, status="CLOSED_SAR_FLIP")  # stop from bar idx, not idx-1
    out = check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert out["match"] is False


# --------------------------------------------------------------------------- #
# …and disagrees with an incorrectly-recorded one
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize("drift", [1.0005, 0.9995, 1.05])
def test_wrong_stop_is_caught(drift):
    """A reconciliation that cannot fail is not a reconciliation.

    0.05% is far below anything a human would notice on the ops page and far
    above float noise, so it is exactly the class of corruption this script
    exists for: an arithmetically perfect SAR computed over the wrong inputs.
    """
    bars = _bars()
    arm = _arm_at(bars, 350)
    arm["sar_stop"] = float(arm["sar_stop"]) * drift
    out = check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert out["match"] is False
    assert out["gap_pct"] > TOL_PCT


def test_wrong_direction_is_caught_without_touching_the_level():
    bars = _bars()
    arm = _arm_at(bars, 350)
    arm["sar_up"] = not bool(arm["sar_up"])
    out = check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert out["match"] is True, "the level itself is untouched"
    assert out["dir_match"] is False


def test_absent_direction_is_not_scored_as_agreement():
    """A blank ``sar_up`` means the arm never advanced — an absence.

    Scoring it as a pass is how "the check stopped running" becomes
    indistinguishable from "the check passed".
    """
    bars = _bars()
    arm = _arm_at(bars, 350)
    arm["sar_up"] = None
    out = check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert out["dir_match"] is None


# --------------------------------------------------------------------------- #
# Refusals are named, and are neither a pass nor a failure
# --------------------------------------------------------------------------- #


def test_bar_outside_the_window_is_refused_by_name():
    bars = _bars()
    arm = _arm_at(bars, 350)
    arm["last_bar_ms"] = 1
    with pytest.raises(_Refusal) as exc:
        check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert exc.value.reason == R_BAR_MISSING


def test_arm_without_a_parked_stop_is_refused():
    bars = _bars()
    arm = _arm_at(bars, 350)
    arm["sar_stop"] = None
    with pytest.raises(_Refusal) as exc:
        check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert exc.value.reason == R_NO_STOP


def test_arm_without_a_bar_timestamp_is_refused():
    bars = _bars()
    arm = _arm_at(bars, 350)
    arm["last_bar_ms"] = None
    with pytest.raises(_Refusal) as exc:
        check_arm(arm, bars, seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert exc.value.reason == R_NO_BAR_MS


def test_bar_too_close_to_the_window_start_is_refused_not_guessed():
    """Refuse the claim rather than answer it off an unseeded walk."""
    bars = _bars()
    arm = _arm_at(bars, 5)
    with pytest.raises(_Refusal) as exc:
        reconstruct(bars, arm["last_bar_ms"], seeds=SEEDS, step=STEP, max_step=MAX_STEP)
    assert exc.value.reason == R_SHORT_WARMUP


def _noisy_bars(n: int = 300) -> list[tuple[int, float, float, float, float]]:
    """A seeded random walk — the series where seeds actually can disagree.

    Smooth series converge so fast that no seed depth produces a disagreement
    at all, which is why the sine fixture above cannot exercise this path.
    """
    rng = random.Random(11)
    px = 100.0
    out = []
    for i in range(n):
        px *= 1 + rng.gauss(0, 0.012)
        out.append(
            (1_700_000_000_000 + i * 900_000, px * 0.999, px * 1.006, px * 0.994, px * 1.001)
        )
    return out


def test_seed_disagreement_is_refused_rather_than_reported_as_a_mismatch():
    """The premise of the whole script, made falsifiable with real SAR output.

    Below convergence the reconstructions genuinely differ, and the right answer
    is to decline: neither reconstruction is the engine's, so a diff against
    either would be an artefact of the seed rather than a finding about the arm.

    Driven at ``min_warmup=3``, where the convergence sweep behind
    :data:`MIN_SEED_WARMUP_BARS` measured 13 disagreeing target bars out of 177.
    Nothing is mocked — this is the real projection on both seeds.
    """
    bars = _noisy_bars()
    refused = 0
    for idx in range(6, 200):
        try:
            reconstruct(
                bars, bars[idx][0], seeds=(0, 20, 30), step=STEP, max_step=MAX_STEP,
                min_warmup=3,
            )
        except _Refusal as exc:
            if exc.reason == R_SEED_SENSITIVE:
                refused += 1
    assert refused > 0, "no seed disagreement below convergence — the guard is untestable"


def test_seeds_agree_at_the_configured_warmup_on_the_same_noisy_series():
    """…and the constant is not merely large: at 30 bars the same series agrees.

    This is the other half of the measurement. Without it, ``MIN_SEED_WARMUP_BARS``
    could be any number at all and the test above would still pass.
    """
    bars = _noisy_bars()
    disagreements = 0
    checked = 0
    for idx in range(MIN_SEED_WARMUP_BARS + 2, 200):
        try:
            reconstruct(bars, bars[idx][0], seeds=(0, 20, 30), step=STEP, max_step=MAX_STEP)
            checked += 1
        except _Refusal as exc:
            if exc.reason == R_SEED_SENSITIVE:
                disagreements += 1
    assert checked > 100, "the sweep must actually have run"
    assert disagreements == 0, f"{disagreements} seed disagreements at the configured warmup"


def test_converged_seeds_agree_which_is_what_makes_the_check_meaningful():
    bars = _bars()
    up, level, n = reconstruct(
        bars, bars[350][0], seeds=(0, 60, 120, 200), step=STEP, max_step=MAX_STEP
    )
    assert n == 4
    assert level > 0
    assert isinstance(up, bool)


# --------------------------------------------------------------------------- #
# Ledger shapes
# --------------------------------------------------------------------------- #


def test_load_arms_accepts_both_ledger_shapes(tmp_path):
    """Bare list and schema envelope both read.

    A schema bump made for one consumer silently changed another consumer's
    file on 2026-08-02 and two ops pages read UNAVAILABLE for four days. This
    reader takes both shapes for exactly that reason.
    """
    import json

    flat = tmp_path / "flat.json"
    flat.write_text(json.dumps([{"arm_id": "a"}, {"arm_id": "b"}]))
    assert len(load_arms(str(flat))) == 2

    env = tmp_path / "env.json"
    env.write_text(
        json.dumps({"schema": 2, "open": [{"arm_id": "a"}], "resolved": [{"arm_id": "b"}]})
    )
    assert {a["arm_id"] for a in load_arms(str(env))} == {"a", "b"}
