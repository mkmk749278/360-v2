"""`candle_coverage` names its cause, and the re-seed sweep counts its shortfall.

On 2026-08-22 the probe had been violating for thirteen sustained cycles with:

    239/330 symbols with ≥20 15m candles, 139/330 updated within 45m

Every word true, sustained, and **unactionable** — three completely different
populations produce those two fractions and each has a different fix:

* 64 of the 330 had no bucket in the store at all (seeding never ran for them),
* some had a bucket with too few bars (a young admission, not a dead feed),
* and 101 scanned 15m series were stale, worst 46 hours.

For a **promoted mover** a stale series is the REST re-seed sweep falling
behind, because promoted pairs carry no WS kline subscription. For a **core**
pair it is a dead kline stream, which is a different and much worse fault — and
the two were pooled into one percentage.

Beside it, `_refresh_stale_mover_candles` used to `break` at its per-cycle
budget and count nothing it turned away, so an under-provisioned sweep was
indistinguishable from a sweep with nothing to do. A fail-open exit with no
counter is how the harm stays invisible.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any, Dict, List, Optional

import pytest

import src.scanner as scanner_mod


# ---------------------------------------------------------------------------
# The re-seed sweep's shortfall
# ---------------------------------------------------------------------------

class _Store:
    """Every symbol's 1m series is stale, so every one is eligible."""

    def last_kline_age_seconds(self, symbol: str, interval: str) -> Optional[float]:
        return 9999.0


def _sweeper(n_active: int, budget: int) -> tuple:
    from collections import defaultdict

    sc = scanner_mod.Scanner.__new__(scanner_mod.Scanner)
    sc.data_store = _Store()
    sc._mover_last_reseed = {}
    sc._suppression_counters = defaultdict(int)
    sc.pair_mgr = type("_PM", (), {"pairs": {}})()
    active = [f"SYM{i}USDT" for i in range(n_active)]
    return sc, active


async def test_the_budget_shortfall_is_counted_rather_than_broken_out_of(
    monkeypatch,
):
    """The number that says whether the sweep can keep pace at all."""
    import config

    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_MAX_PER_CYCLE", 8)
    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_SEC", 120.0)

    sc, active = _sweeper(30, 8)
    # No pair_mgr entries, so every `_reseed` no-ops; the accounting above it
    # is what is under test.
    await sc._refresh_stale_mover_candles(active)

    c = sc._suppression_counters
    assert c["mover_reseed:wanted"] == 30, (
        "the whole eligible list must be walked — 'however many were left when "
        "we stopped looking' is not the shortfall"
    )
    assert c["mover_reseed:refreshed"] == 8
    assert c["mover_reseed:deferred"] == 22


async def test_a_sweep_inside_its_budget_defers_nothing(monkeypatch):
    """Zero deferred and zero eligible must not read the same.

    `wanted` is what separates "nothing to do" from "everything done".
    """
    import config

    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_MAX_PER_CYCLE", 8)
    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_SEC", 120.0)

    sc, active = _sweeper(3, 8)
    await sc._refresh_stale_mover_candles(active)

    c = sc._suppression_counters
    assert c["mover_reseed:wanted"] == 3
    assert c["mover_reseed:deferred"] == 0
    assert c["mover_reseed:refreshed"] == 3


async def test_the_per_symbol_throttle_still_holds(monkeypatch):
    """A symbol refreshed this cycle is not eligible again immediately —
    otherwise the head of the list would starve the tail forever."""
    import config

    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_MAX_PER_CYCLE", 8)
    monkeypatch.setattr(config, "MOVER_CANDLE_REFRESH_SEC", 120.0)

    sc, active = _sweeper(30, 8)
    await sc._refresh_stale_mover_candles(active)
    first = set(sc._mover_last_reseed)
    assert len(first) == 8

    sc._suppression_counters.clear()
    await sc._refresh_stale_mover_candles(active)
    second = set(sc._mover_last_reseed)

    assert len(second) == 16, "the second cycle must take the NEXT eight"
    assert sc._suppression_counters["mover_reseed:deferred"] == 14


def test_the_documented_arithmetic_matches_the_shipped_defaults():
    """Pin the sustainability bound the sweep's comment states.

    supply = MAX_PER_CYCLE * (REFRESH_SEC / cycle_seconds); the sweep keeps
    pace while cycle_seconds <= MAX_PER_CYCLE * REFRESH_SEC / N. If either
    default moves, the sentence in the code moves with it or fails here.
    """
    import config

    per_cycle = config.MOVER_CANDLE_REFRESH_MAX_PER_CYCLE
    refresh_sec = config.MOVER_CANDLE_REFRESH_SEC
    cap = config.MOVER_PROMOTION_MAX_PAIRS

    assert per_cycle == 8
    assert refresh_sec == 120.0
    assert cap == 30
    sustainable_cycle_sec = per_cycle * refresh_sec / cap
    assert sustainable_cycle_sec == pytest.approx(32.0), (
        "the comment in _refresh_stale_mover_candles quotes 32s — update both"
    )


# ---------------------------------------------------------------------------
# The probe's cause bucketing
# ---------------------------------------------------------------------------

class _CoverageStore:
    def __init__(self, series: Dict[str, Any], ages: Dict[str, Optional[float]]):
        self._series = series
        self._ages = ages

    def get_candles(self, symbol: str, interval: str):
        return self._series.get(symbol)

    def last_kline_age_seconds(self, symbol: str, interval: str):
        return self._ages.get(symbol)


def _real_probe():
    """Pull the REAL ``candle_coverage`` closure out of the engine's registry.

    Not a reimplementation. A test that copies the probe's body asserts this
    file's assumptions back at itself and goes green over a probe that has
    since changed — the mock-shaped failure this repo has paid for twice
    (``classify_pending``'s ``exit_reason``, ``zone_distance_atr``'s zone
    keys). ``_build_feature_liveness`` only *builds* closures, so a bare engine
    is enough to register all 42 and hand back the one under test.
    """
    import src.main as main_mod

    eng = main_mod.CryptoSignalEngine.__new__(main_mod.CryptoSignalEngine)
    fl = eng._build_feature_liveness()
    probe = next(p for p in fl._predicate_probes if p.name == "candle_coverage")
    return eng, probe


def _coverage(symbols: List[str], series, ages, promoted=(), tiers=None):
    """Run the real probe against a store we control, and return what it says.

    The probe's output is a ``(healthy, detail)`` pair and the **detail string
    is the artifact the owner reads**, so that is what these tests assert on.
    """
    eng, probe = _real_probe()
    promoted_set = set(promoted)
    tiers = tiers or {}
    pairs = {
        s: SimpleNamespace(
            tier=tiers.get(s, "TIER2" if s in promoted_set else "TIER1"),
            market="futures",
        )
        for s in symbols
    }
    eng.pair_mgr = type("_PM", (), {"pairs": pairs})()
    eng.data_store = _CoverageStore(series, ages)
    eng._scanner = type(
        "_SC", (), {"_mover_promoted_pairs": {s: 0.0 for s in promoted}},
    )()
    return probe.fn()


def test_the_three_populations_are_counted_apart():
    """no_bucket / short / stale have three different fixes.

    The pre-fix probe said "2/4 symbols with ≥20 candles, 1/4 updated" and
    stopped there, which is true of this fixture and of three others that need
    three different repairs.
    """
    syms = ["AUSDT", "BUSDT", "CUSDT", "DUSDT"]
    series = {
        # AUSDT absent entirely — never seeded.
        "BUSDT": {"close": [1.0] * 5},     # seeded, not filled
        "CUSDT": {"close": [1.0] * 50},    # full and stale
        "DUSDT": {"close": [1.0] * 50},    # full and fresh
    }
    ages = {"CUSDT": 99999.0, "DUSDT": 10.0}
    healthy, detail = _coverage(syms, series, ages)

    assert healthy is False
    assert "no_bucket=1" in detail
    assert "short=1" in detail
    assert "stale=1" in detail
    assert "fresh=1" in detail
    assert "2/4 symbols" in detail and "1/4 updated" in detail


def test_a_stale_core_pair_is_named_apart_from_a_stale_mover():
    """The same symptom, two faults.

    A promoted pair has no WS kline subscription, so its bucket going stale is
    the re-seed sweep falling behind. A core pair going stale is a dead stream,
    and pooling them is what made 191 unusable symbols read as one percentage.
    """
    syms = ["COREUSDT", "MOVERUSDT"]
    series = {s: {"close": [1.0] * 50} for s in syms}
    ages = dict.fromkeys(syms, 99999.0)

    _, detail = _coverage(syms, series, ages, promoted=["MOVERUSDT"])
    assert "1 CORE pair(s) unusable" in detail
    assert "COREUSDT" in detail, "the next move is a symbol, not a percentage"
    assert "MOVERUSDT" not in detail, (
        "a promoted mover's frozen bucket is by design and must not be "
        "reported as a dead kline stream"
    )


def test_rest_only_tiers_do_not_dilute_tier1_websocket_coverage():
    """Tier 2/3 are REST discovery populations, not continuous WS streams."""
    syms = ["COREUSDT", "DISCOVERYUSDT", "LIGHTUSDT"]
    series = {
        "COREUSDT": {"close": [1.0] * 50},
        "DISCOVERYUSDT": {"close": [1.0] * 50},
        "LIGHTUSDT": {"close": [1.0] * 50},
    }
    ages = {"COREUSDT": 10.0, "DISCOVERYUSDT": 99999.0, "LIGHTUSDT": 99999.0}
    healthy, detail = _coverage(
        syms,
        series,
        ages,
        tiers={
            "COREUSDT": "TIER1",
            "DISCOVERYUSDT": "TIER2",
            "LIGHTUSDT": "TIER3",
        },
    )

    assert healthy is True
    assert "1/1 symbols" in detail
    assert "1 Tier-1 futures" in detail
    assert "DISCOVERYUSDT" not in detail and "LIGHTUSDT" not in detail


def test_a_never_stamped_age_is_not_evidence_of_freshness():
    """``None`` means nothing recorded it, which is not "it is current"."""
    _, detail = _coverage(
        ["XUSDT"], {"XUSDT": {"close": [1.0] * 50}}, {"XUSDT": None}
    )
    assert "stale=1" in detail
    assert "0/1 updated" in detail


def test_the_pooled_healthy_thresholds_are_unchanged():
    """The pooled 0.7 bar must not move.

    A probe that starts passing on the same data as part of a 'clarity' change
    is a silenced detector, and the counters this repo keeps are exactly the
    ones that stop standing out when that happens.

    2026-08-29: the stale population here is PROMOTED MOVERS, deliberately —
    mover staleness is a budgeted re-seed shortfall and is exactly what the
    pooled ratio is for.  Core-pair staleness now pages on its own absolute
    rule (see test_dead_core_pairs_page_regardless_of_the_pooled_ratio) and
    would mask this test's subject if used here.
    """
    syms = [f"S{i}USDT" for i in range(10)]
    movers = syms[:4]
    series = {s: {"close": [1.0] * 50} for s in syms}
    ages = dict.fromkeys(syms, 10.0)
    for s in movers:
        ages[s] = 99999.0

    healthy, detail = _coverage(syms, series, ages, promoted=movers)
    assert healthy is False, "6/10 fresh must still fail the 0.7 bar"

    # …and the same data one symbol better must pass, so the bar has
    # not quietly moved with the wording.
    ages[movers[0]] = 10.0
    healthy_7, _ = _coverage(syms, series, ages, promoted=movers)
    assert healthy_7 is True, "7/10 is the bar and must pass"


def test_dead_core_pairs_page_regardless_of_the_pooled_ratio():
    """More than a handful of unusable CORE pairs is page-worthy on its own.

    2026-08-29: 18 dead Tier-1 streams — including BTCUSDT — sat inside a
    passing 70% pooled ratio for days while the probe NAMED them in its
    detail string and asserted healthy.  A core pair with no live kline
    stream is unusable for every evaluator; the pooled denominators, diluted
    with promoted movers whose staleness is a different budgeted fault, must
    not be able to vote that down.  Threshold: len(core_bad) >
    max(2, len(core_syms) // 15).
    """
    syms = [f"S{i}USDT" for i in range(30)]
    series = {s: {"close": [1.0] * 50} for s in syms}
    ages = dict.fromkeys(syms, 10.0)
    # 3 dead core pairs out of 30 — 90% pooled fresh, comfortably above the
    # 0.7 bar, and exactly the shape of the live incident in miniature.
    for s in syms[:3]:
        ages[s] = 99999.0

    healthy, detail = _coverage(syms, series, ages)
    assert healthy is False, (
        "3 unusable CORE pairs must page even at a 90% pooled fresh ratio"
    )
    assert "3 Tier-1 CORE pair(s) unusable" in detail

    # …while 2 dead core pairs (at or under the absolute floor) still pass:
    # a single flapping stream plus one late frame is not an incident.
    ages[syms[2]] = 10.0
    healthy_2, _ = _coverage(syms, series, ages)
    assert healthy_2 is True, "2 unusable CORE pairs is under the page bar"
