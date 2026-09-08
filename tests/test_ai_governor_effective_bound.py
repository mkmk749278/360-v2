"""The staleness bound, derived from the loop rather than asserted about it.

The defect, live on 2026-09-08 and read off the ops page: bound **10.0s**,
measured floor **14.1s** (5.2s model round trip + 9.0s p50 sweep, worst tick
30.0s), headroom **-4.1s**. In that state no verdict can pass the bound at
all — 28 of 90 were recorded stale, including 13 of 26 ``ADJUST_SL``, which
is every actionable verdict this lane has ever produced.

Two things make it worth a file of its own rather than a line in the fix.

`verdict_age_floor` has published exactly that reading since #1015 and
**nothing consumed it**. The measurement that named the fault could not
correct it, because the enforced number stayed the config constant — a
reading with no reader, which is `flush()` with no caller one lane over.

And ops has rendered ``verdict_max_age_effective_sec`` and
``observed_tick_sec`` since its panel shipped, under a paragraph stating that
"the bound is derived from the loop, not configured: the floor above, the
slowest recent tick x1.5, and a hard 60s cap". The engine has never sent
either key. So the page described a derivation that did not exist, on the
panel an owner reads to decide whether the staleness rule is doing anything —
a docstring asserting a property the code beneath it does not have, arriving
one repo out and checkable in one grep.

Every test here fails against the pre-fix tree.
"""
from __future__ import annotations

from typing import Optional

import pytest

from src import ai_governor_ledger
from src.execution import ai_governor as gov

from tests.test_ai_governor_bounds import _menu_and_snapshot, _verdict  # noqa: F401


@pytest.fixture(autouse=True)
def _isolate():
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(ai_governor_ledger.GovernorLedger(path=""))
    yield
    gov.reset_state_for_test()
    gov.reset_health_for_test()
    ai_governor_ledger.reset_ledger(None)


def _ticks(*times: float) -> None:
    for t in times:
        gov._record_sweep_period(t)


# ── The derivation ──────────────────────────────────────────────────────────

def test_with_no_measured_tick_the_configured_floor_stands_and_says_so():
    """An unmeasured tick is not a fast one.

    Three states, not two: derived, configured-because-nothing-was-measured,
    and configured-because-the-loop-is-quick. The middle one has to name
    itself or a reader cannot tell a bound that was checked against the loop
    from one that never could be.
    """
    out = gov.effective_verdict_max_age()
    assert out["source"] == "configured"
    assert out["reason"] == "no_sweep_periods"
    assert out["observed_tick_sec"] is None, (
        "not 0.0 — an unmeasured period rendered as zero reads as an "
        "instantaneous loop, which is the flattering direction"
    )
    assert out["effective_sec"] == pytest.approx(out["configured_sec"])


def test_the_bound_widens_to_the_slowest_recent_tick():
    """The p50 is what the loop usually achieves; the bound has to survive the
    tick it actually hit. On the live reading those differ by more than 3x."""
    _ticks(0.0, 5.0, 10.0, 30.0)  # three periods: 5s, 5s, 20s
    out = gov.effective_verdict_max_age()
    assert out["observed_tick_sec"] == pytest.approx(20.0)
    assert out["effective_sec"] == pytest.approx(30.0), "20s slowest x 1.5"
    assert out["source"] == "derived"


def test_the_configured_number_is_a_FLOOR_not_a_target():
    """A quick loop must not shrink the bound below what the owner set."""
    _ticks(0.0, 1.0, 2.0)
    out = gov.effective_verdict_max_age()
    assert out["effective_sec"] == pytest.approx(out["configured_sec"])
    assert out["source"] == "configured"
    assert out["observed_tick_sec"] == pytest.approx(1.0), (
        "still published — the reader needs to see WHY it did not widen"
    )


def test_a_pathological_tick_cannot_switch_the_rule_off():
    """A monitor tick minutes long is a fault in its own right. Inheriting it
    here would silently turn the staleness rule into 'accept everything' at
    exactly the moment it matters."""
    _ticks(0.0, 300.0)
    out = gov.effective_verdict_max_age()
    assert out["effective_sec"] == pytest.approx(60.0)
    assert out["capped"] is True


# ── It is ENFORCED, not merely published ────────────────────────────────────

async def test_a_verdict_inside_the_derived_bound_is_no_longer_refused(monkeypatch):
    """The whole point, and the assertion that fails against the old tree.

    15s is stale against the 10.0s constant and fine against a loop whose
    slowest recent tick was 20s. Pre-fix this returned `stale_verdict`; the
    refusal was a fact about our own cadence rather than about the world.
    """
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    _ticks(0.0, 5.0, 10.0, 30.0)  # slowest 20s -> bound 30s
    m, sn = _menu_and_snapshot()
    out = await gov.apply_verdict(
        _verdict(gov.PANIC_CLOSE, None, issued_at=0.0), sn, m, now=15.0
    )
    assert out != gov.REFUSE_STALE_VERDICT, (
        "15s is inside a 30s derived bound; refusing it measures the loop, "
        "not the world"
    )


async def test_a_genuinely_old_verdict_is_still_refused(monkeypatch):
    """Widening is not switching off. The rule still has to bite."""
    monkeypatch.setattr(gov, "apply_enabled", lambda: True)
    _ticks(0.0, 5.0, 10.0, 30.0)
    m, sn = _menu_and_snapshot()
    out = await gov.apply_verdict(
        _verdict(gov.PANIC_CLOSE, None, issued_at=0.0), sn, m, now=120.0
    )
    assert out == gov.REFUSE_STALE_VERDICT


async def test_the_aged_out_COUNT_and_the_refusal_agree():
    """Two renderers of one fact, forty lines apart on the panel.

    `_record_verdict_age` stamps `stale` for every verdict including MAINTAIN,
    and `_apply_verdict` refuses on the same question. If one read the derived
    bound and the other the constant, the page would show verdicts "aged out"
    that were applied — the `/control` defect where a banner and the verdict
    under it described different worlds.
    """
    _ticks(0.0, 5.0, 10.0, 30.0)  # bound 30s
    m, sn = _menu_and_snapshot()
    await gov.apply_verdict(
        _verdict(gov.MAINTAIN, None, issued_at=0.0), sn, m, now=15.0
    )
    age = gov.health()["verdict_age"]
    assert age["n"] == 1
    assert age["stale_n"] == 0, "15s is not late against the bound being enforced"


# ── The cross-repo contract ─────────────────────────────────────────────────

def test_ops_receives_the_two_keys_it_has_always_rendered():
    """`ai_governor.html` reads `bounds.verdict_max_age_effective_sec` and
    `bounds.observed_tick_sec`. Neither has ever been sent, so the page fell
    to its "not measured yet" branch under a paragraph promising a derivation.
    A field one repo reads and no repo writes, pinned on the producing side."""
    _ticks(0.0, 5.0, 10.0, 30.0)
    bounds = gov.build_diag()["bounds"]
    assert bounds["verdict_max_age_effective_sec"] == pytest.approx(30.0)
    assert bounds["observed_tick_sec"] == pytest.approx(20.0)
    assert bounds["verdict_max_age_source"] == "derived"
    assert "verdict_max_age_sec" in bounds, (
        "the configured floor stays beside it — both numbers render because a "
        "reader needs to know which one binds"
    )
