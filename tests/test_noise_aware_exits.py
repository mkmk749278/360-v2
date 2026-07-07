"""Tests for the 2026-07-07 noise-aware exits + cohort-edge activation.

Covers the four owner-approved changes:
1. runtime_tunables — registry, env-default fallback, validation.
2. be_policy — noise-aware arm threshold + park tolerance.
3. CohortEdgeStore persistence — survives a restart (reload from JSON).
4. Scanner noise-floor helpers — ATR measurement + widen-only semantics.
"""
from __future__ import annotations


import pytest

from src import runtime_tunables as rt
from src.execution import be_policy
from src.stat_filter import CohortEdgeStore, SignalOutcome


@pytest.fixture(autouse=True)
def _reset_tunables():
    rt.reset_for_test()
    yield
    rt.reset_for_test()


# ---------------------------------------------------------------------------
# runtime_tunables
# ---------------------------------------------------------------------------

def test_tunables_default_when_uninitialised():
    # Firestore not wired → env boot defaults, never raises.
    assert rt.get("noise_floor_stops_enabled") is True
    assert rt.get("be_arm_r_mult") == pytest.approx(1.0)
    assert rt.get("cohort_edge_gate_enabled") is True


def test_tunables_unknown_key_raises():
    with pytest.raises(KeyError):
        rt.get("no_such_tunable")


def test_tunables_snapshot_covers_registry():
    snap = rt.snapshot()
    keys = {e["key"] for e in snap}
    assert "noise_floor_atr_mult" in keys
    assert "be_park_tolerance_pct" in keys
    assert "cohort_edge_suppress_below" in keys
    for e in snap:
        assert e["value"] == e["default"]  # uninitialised → defaults
        assert e["description"]


class _FakeDoc:
    def __init__(self, data):
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return self._data


class _FakeFirestore:
    def __init__(self):
        self.data = {}

    def collection(self, name):
        return self

    def document(self, name):
        return self

    def get(self):
        return _FakeDoc(dict(self.data))

    def set(self, payload, merge=False):
        self.data.update(payload)


def test_tunables_set_and_read_back():
    fs = _FakeFirestore()
    rt.init_runtime_tunables(fs)
    rt.set_values({"noise_floor_atr_mult": 1.5, "be_shift_enabled": False})
    assert rt.get("noise_floor_atr_mult") == pytest.approx(1.5)
    assert rt.get("be_shift_enabled") is False


def test_tunables_set_rejects_out_of_range():
    fs = _FakeFirestore()
    rt.init_runtime_tunables(fs)
    with pytest.raises(ValueError):
        rt.set_values({"noise_floor_atr_mult": 99.0})
    with pytest.raises(ValueError):
        rt.set_values({"bogus_key": 1})


# ---------------------------------------------------------------------------
# be_policy
# ---------------------------------------------------------------------------

def test_be_arm_uses_largest_of_flat_r_and_noise():
    # defaults: flat 1.0, r_mult 1.0, noise_mult 0.75
    assert be_policy.arm_threshold_pct(0.0, 0.0) == pytest.approx(1.0)
    # 2% stop → 1R = 2% dominates the flat 1%
    assert be_policy.arm_threshold_pct(2.0, 0.0) == pytest.approx(2.0)
    # 4% noise floor → 0.75 × 4 = 3% dominates
    assert be_policy.arm_threshold_pct(2.0, 4.0) == pytest.approx(3.0)


def test_be_park_is_on_loss_side_of_entry():
    entry = 100.0
    long_park = be_policy.park_price(entry, is_long=True)
    short_park = be_policy.park_price(entry, is_long=False)
    assert long_park < entry   # LONG: stop below entry
    assert short_park > entry  # SHORT: stop above entry
    # default tolerance 0.15%
    assert long_park == pytest.approx(entry * (1 - 0.0015))
    assert short_park == pytest.approx(entry * (1 + 0.0015))


def test_be_enabled_falls_back_to_default():
    assert be_policy.be_enabled(True) is True


# ---------------------------------------------------------------------------
# CohortEdgeStore persistence
# ---------------------------------------------------------------------------

def _outcome(won: bool, pnl: float) -> SignalOutcome:
    return SignalOutcome(
        signal_id="X",
        channel="360_SCALP",
        pair="TESTUSDT",
        regime="TRENDING_DOWN",
        setup_class="MOVER_TREND_PULLBACK",
        won=won,
        pnl_pct=pnl,
        side="SHORT",
        macro_dir="NEUTRAL",
    )


def test_cohort_store_survives_restart(tmp_path):
    path = str(tmp_path / "cohort.json")
    store = CohortEdgeStore(min_samples=3, persist_path=path)
    for _ in range(3):
        store.record(_outcome(False, -1.0))
    exp = store.expectancy("MOVER_TREND_PULLBACK", "SHORT", "TRENDING_DOWN", "NEUTRAL")
    assert exp is not None and exp < 0

    # Fresh instance (simulated restart) reloads the same measurements.
    reloaded = CohortEdgeStore(min_samples=3, persist_path=path)
    exp2 = reloaded.expectancy("MOVER_TREND_PULLBACK", "SHORT", "TRENDING_DOWN", "NEUTRAL")
    assert exp2 == pytest.approx(exp)
    assert reloaded.sample_count(
        "MOVER_TREND_PULLBACK", "SHORT", "TRENDING_DOWN", "NEUTRAL"
    ) == 3


def test_cohort_store_no_persist_path_is_memory_only(tmp_path):
    store = CohortEdgeStore(min_samples=3, persist_path="")
    store.record(_outcome(True, 1.0))
    assert store.sample_count(
        "MOVER_TREND_PULLBACK", "SHORT", "TRENDING_DOWN", "NEUTRAL"
    ) == 1


# ---------------------------------------------------------------------------
# Scanner noise-floor helpers (pure static pieces — no Scanner construction)
# ---------------------------------------------------------------------------

def test_atr_pct_from_candles():
    from src.scanner import Scanner

    n = 40
    highs = [101.0] * n
    lows = [99.0] * n
    closes = [100.0] * n
    cd = {"high": highs, "low": lows, "close": closes}
    pct = Scanner._atr_pct_from_candles(cd, entry=100.0)
    # TR = high-low = 2.0 every bar → ATR = 2.0 → 2% of entry
    assert pct == pytest.approx(2.0)


def test_atr_pct_insufficient_history_returns_zero():
    from src.scanner import Scanner

    cd = {"high": [1, 2], "low": [0.5, 1], "close": [0.9, 1.5]}
    assert Scanner._atr_pct_from_candles(cd, entry=1.0) == 0.0
    assert Scanner._atr_pct_from_candles(None, entry=1.0) == 0.0
    assert Scanner._atr_pct_from_candles({}, entry=0.0) == 0.0
