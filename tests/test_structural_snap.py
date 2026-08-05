"""Tests for the structural SL/TP1 snap (src/structural_snap.py).

The defect this lane exists to repair was invisible for the life of the code:
``build_channel_signal`` called a structural snap behind a guard on
``candle_highs is not None`` that **no caller ever satisfied**, under a comment
claiming every evaluator passed the arrays.  Nothing crashed and nothing was
empty; the geometry was simply never level-aware.

So the first test here is the one that matters: it asserts, by parsing the
scanner's own source, that the snap is reachable from the choke point — the
"verify a fix by reverting it" rule, applied to a defect whose whole nature was
unreachability.  A unit test of ``compute()`` would have passed against the
broken code exactly as it passes against this one.
"""
from __future__ import annotations

import ast
import json
import os
from pathlib import Path

import numpy as np
import pytest

from src import structural_snap as ss
from src.structural_levels import (
    find_round_numbers,
    find_structural_sl,
    find_structural_sl_detail,
    find_structural_tp,
    find_structural_tp_detail,
    find_swing_levels,
)

_REPO = Path(__file__).resolve().parents[1]

#: Captured before any fixture runs, so the one test that exercises the real
#: flag logic can reach past the autouse stub below.
_REAL_APPLY_ENABLED = ss.apply_enabled


# ---------------------------------------------------------------------------
# Reachability — the actual bug class
# ---------------------------------------------------------------------------

def test_snap_is_called_from_the_enqueue_chokepoint():
    """The snap must be invoked from ``_enqueue_signal``, not merely importable.

    ``_enqueue_signal`` is the single point every enqueued signal passes
    through, and the only one where sig.stop_loss / sig.tp1 are the numbers
    that will actually be parked.  Pinning the CALL SITE rather than the import
    is deliberate: the previous snap was imported, wired and dead.
    """
    src = (_REPO / "src" / "scanner" / "__init__.py").read_text()
    tree = ast.parse(src)
    enqueue = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "_enqueue_signal"
    )
    calls = {
        ast.unparse(n.func) for n in ast.walk(enqueue) if isinstance(n, ast.Call)
    }
    assert "_snap.stamp_and_apply" in calls, (
        "structural_snap.stamp_and_apply is not called from _enqueue_signal — "
        "the snap is unreachable, which is exactly the defect this module fixes"
    )


def test_build_channel_signal_no_longer_carries_a_dead_snap():
    """One snap, in one place.

    The old branch is gone rather than left beside the new one: a second
    implementation of the same selection is a mirror, and the fix for a
    drifting mirror is not a second mirror.
    """
    src = (_REPO / "src" / "channels" / "base.py").read_text()
    assert "find_structural_sl(" not in src
    assert "find_structural_tp(" not in src


def test_every_live_setup_class_has_a_declared_timeframe():
    """A setup absent from the map is refused, never defaulted — but the live
    ones must all be present, or the lane silently measures nothing on them.

    Derived from the evaluators' own ``setup_class=`` arguments rather than a
    hand-typed list, so a new evaluator fails this test instead of quietly
    landing in the ``tf_unknown`` bucket forever.
    """
    src = (_REPO / "src" / "channels" / "scalp.py").read_text()
    tree = ast.parse(src)
    declared = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg == "setup_class" and isinstance(kw.value, ast.Constant):
                if isinstance(kw.value.value, str) and kw.value.value:
                    declared.add(kw.value.value)
    missing = sorted(declared - set(ss.SNAP_TF_BY_SETUP))
    assert not missing, f"setup classes with no declared snap timeframe: {missing}"


# ---------------------------------------------------------------------------
# The detail/price pair must not drift
# ---------------------------------------------------------------------------

def _swings():
    return {"swing_highs": [105.0, 108.0], "swing_lows": [95.0, 92.0]}


def test_detail_and_price_views_agree_sl():
    rounds = find_round_numbers(100.0)
    detail = find_structural_sl_detail("LONG", 100.0, 93.0, _swings(), rounds, 7.0)
    price = find_structural_sl("LONG", 100.0, 93.0, _swings(), rounds, 7.0)
    assert detail.price == price


def test_detail_and_price_views_agree_tp():
    rounds = find_round_numbers(100.0)
    detail = find_structural_tp_detail("LONG", 100.0, 107.0, _swings(), rounds)
    price = find_structural_tp("LONG", 100.0, 107.0, _swings(), rounds, 0.0)
    assert detail.price == price


def test_source_is_reported_not_guessed():
    """An all-``none`` source column would be indistinguishable from a reader
    that cannot read, which is how ``smc_zone_dist_atr`` stayed broken."""
    swings = {"swing_highs": [], "swing_lows": [95.0]}
    pick = find_structural_sl_detail("LONG", 100.0, 93.0, swings, [], 7.0)
    assert pick.source == "swing"
    assert pick.level == 95.0
    # 0.1% buffer below the level
    assert pick.price == pytest.approx(95.0 * 0.999)


# ---------------------------------------------------------------------------
# compute() — bounds and refusals
# ---------------------------------------------------------------------------

def _series(n=60, base=100.0, seed=7):
    """A synthetic OHLC series with real swings.

    Noise is multiplicative so the fixture behaves identically at $100 and at
    $0.05 — an additive walk at sub-cent prices wanders through zero and the
    series stops being a price at all.
    """
    rng = np.random.default_rng(seed)
    closes = base * np.exp(np.cumsum(rng.normal(0, 0.003, n)))
    highs = closes * (1.0 + np.abs(rng.normal(0, 0.002, n)))
    lows = closes * (1.0 - np.abs(rng.normal(0, 0.002, n)))
    return highs, lows, closes


def test_tp1_only_ever_moves_nearer():
    """The direction is the safety property.

    Flooring TP1 *further* out is the change the 2026-08-01 dark-window
    simulation argues against — it took the book from -0.081R to as low as
    -0.836R.  A structural snap that could extend a target would reintroduce
    exactly that, so this is pinned rather than assumed.
    """
    highs, lows, closes = _series()
    entry = float(closes[-1])
    for direction, sl, tp1 in (
        ("LONG", entry * 0.98, entry * 1.02),
        ("SHORT", entry * 1.02, entry * 0.98),
    ):
        row = ss.compute(
            direction=direction, entry=entry, stop_loss=sl, tp1=tp1,
            highs=highs, lows=lows, closes=closes, tf="15m",
        )
        assert row["refused"] == ""
        assert row["tp1_shift_pct"] <= 0.0, (
            f"{direction}: TP1 moved further out — the snap must only tighten"
        )


def test_sl_snap_stays_inside_its_band():
    """At most +/-30% of the designed risk. This is what stops a 3% stop from
    becoming a 0.5% one."""
    highs, lows, closes = _series()
    entry = float(closes[-1])
    sl = entry * 0.97
    designed = abs(entry - sl)
    row = ss.compute(
        direction="LONG", entry=entry, stop_loss=sl, tp1=entry * 1.03,
        highs=highs, lows=lows, closes=closes, tf="15m",
    )
    assert row["refused"] == ""
    snapped = abs(entry - row["sl_snapped"])
    # The 0.1% buffer sits outside the band bound, so allow for it.
    assert 0.7 * designed * 0.99 <= snapped <= 1.3 * designed * 1.01


def test_shift_signs_are_toward_risk_and_reward_not_toward_price():
    """A SHORT whose stop widens must read POSITIVE, same as a LONG's.

    Storing these raw and splitting them with one "higher is better" rule is
    how ``cvd_slope`` and ``book_imbalance`` scored every SHORT backwards for a
    whole schema version while looking like noise.
    """
    highs, lows, closes = _series()
    entry = float(closes[-1])
    swings = find_swing_levels(highs, lows, closes, lookback=ss.SWING_LOOKBACK)
    assert swings["swing_highs"] or swings["swing_lows"], "fixture has no swings"

    long_row = ss.compute(
        direction="LONG", entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03,
        highs=highs, lows=lows, closes=closes, tf="15m",
    )
    short_row = ss.compute(
        direction="SHORT", entry=entry, stop_loss=entry * 1.03, tp1=entry * 0.97,
        highs=highs, lows=lows, closes=closes, tf="15m",
    )
    for row in (long_row, short_row):
        widened = abs(entry - row["sl_snapped"]) > abs(entry - row["sl_arith"])
        assert (row["sl_shift_pct"] > 0) == widened


@pytest.mark.parametrize("kwargs,expected", [
    (dict(highs=None, lows=None, closes=None), ss.REFUSE_NO_CANDLES),
    (dict(highs=[1.0], lows=[1.0], closes=[1.0]), ss.REFUSE_SHORT_SERIES),
])
def test_refuses_rather_than_clamping(kwargs, expected):
    """A series too short for +/-3-bar swing confirmation cannot support the
    work.  Reporting "no structural level nearby" for it would be a claim about
    the market made from a fact about the buffer."""
    row = ss.compute(
        direction="LONG", entry=100.0, stop_loss=97.0, tp1=103.0, tf="5m", **kwargs
    )
    assert row["refused"] == expected
    assert row["sl_snapped"] is None


def test_refuses_on_unusable_geometry():
    row = ss.compute(
        direction="LONG", entry=100.0, stop_loss=100.0, tp1=103.0,
        highs=[1.0] * 60, lows=[1.0] * 60, closes=[1.0] * 60, tf="5m",
    )
    assert row["refused"] == ss.REFUSE_NO_GEOMETRY


def test_numpy_arrays_are_never_boolean_tested():
    """The store holds numpy arrays; truthiness on one raises. Eight features
    died silently to this in 2026-07."""
    highs, lows, closes = _series()
    row = ss.compute(
        direction="LONG", entry=float(closes[-1]), stop_loss=float(closes[-1]) * 0.97,
        tp1=float(closes[-1]) * 1.03,
        highs=np.asarray(highs), lows=np.asarray(lows), closes=np.asarray(closes),
        tf="15m",
    )
    assert row["refused"] == ""


def test_round_step_pct_is_stamped():
    """Without it, an all-``swing`` source column reads as round numbers being
    unhelpful rather than as the absolute grid being 20% wide at this price and
    therefore contributing nothing."""
    highs, lows, closes = _series(base=0.05)
    entry = float(closes[-1])
    row = ss.compute(
        direction="LONG", entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03,
        highs=highs, lows=lows, closes=closes, tf="15m",
    )
    assert row["round_step_pct"] is not None
    assert row["round_step_pct"] > 10.0  # inert at this magnitude


# ---------------------------------------------------------------------------
# stamp_and_apply — the money-path half
# ---------------------------------------------------------------------------

class _Sig:
    def __init__(self, **kw):
        self.signal_id = kw.get("signal_id", "SNAP-1")
        self.symbol = "TESTUSDT"
        self.setup_class = kw.get("setup_class", "MOVER_TREND_PULLBACK")
        self.channel = "SCALP"
        self.direction = kw.get("direction", "LONG")
        self.entry = kw["entry"]
        self.stop_loss = kw["stop_loss"]
        self.tp1 = kw["tp1"]
        self.original_sl_distance = abs(kw["entry"] - kw["stop_loss"])
        self.sl_distance_pct_at_entry = self.original_sl_distance / kw["entry"] * 100.0


@pytest.fixture(autouse=True)
def _isolated_lane(monkeypatch):
    ss.reset_ledger(ss.SnapLedger(path=""))   # path="" = in memory, no disk
    ss.reset_counters()
    monkeypatch.setattr(ss, "measure_enabled", lambda: True)
    monkeypatch.setattr(ss, "apply_enabled", lambda _sc: False)
    yield
    ss.reset_ledger(None)
    ss.reset_counters()


def _candles():
    highs, lows, closes = _series()
    return {"high": highs, "low": lows, "close": closes}


def test_measure_only_does_not_touch_geometry():
    """The default posture. A subscriber sees exactly what they saw before."""
    c = _candles()
    entry = float(c["close"][-1])
    sig = _Sig(entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03)
    before = (sig.stop_loss, sig.tp1, sig.sl_distance_pct_at_entry)
    row = ss.stamp_and_apply(sig, candles=c, min_sl_distance=0.0)
    assert row is not None and row["refused"] == ""
    assert (sig.stop_loss, sig.tp1, sig.sl_distance_pct_at_entry) == before
    assert row["applied_sl"] is False and row["applied_tp1"] is False
    assert len(ss.get_ledger().rows()) == 1


def test_apply_moves_geometry_and_restamps_the_r_denominator(monkeypatch):
    """When the stop moves, ``sl_distance_pct_at_entry`` must move with it.

    #848 is the bill for a ratio whose denominator changed after it was
    recorded: ops divides pnl_pct by this field, so leaving the arithmetic stop
    in it would score every snapped trade against risk it never carried.
    """
    monkeypatch.setattr(ss, "apply_enabled", lambda _sc: True)
    c = _candles()
    entry = float(c["close"][-1])
    sig = _Sig(entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03)
    row = ss.stamp_and_apply(sig, candles=c, min_sl_distance=0.0)
    assert row["refused"] == ""
    # Asserted, not guarded on: a test whose body sits behind `if it fired`
    # goes green on a lane that never fires, which is the failure mode this
    # whole module exists to stop being invisible.
    assert row["applied_sl"] is True and row["applied_tp1"] is True

    assert sig.stop_loss == row["sl_snapped"]
    assert sig.tp1 == row["tp1_snapped"]
    assert sig.original_sl_distance == pytest.approx(abs(entry - sig.stop_loss))
    assert sig.sl_distance_pct_at_entry == pytest.approx(
        abs(entry - sig.stop_loss) / entry * 100.0
    )
    # ...and the restamped denominator is not the one it replaced.
    assert sig.sl_distance_pct_at_entry != pytest.approx(3.0)


def _series_with_swing_low_at(entry: float, frac_below: float, n: int = 60):
    """A flat series with one deliberate dip, so the swing low's distance from
    entry is exactly what the test says it is."""
    closes = np.full(n, entry, dtype=float)
    highs = closes * 1.0005
    lows = closes * 0.9995
    dip = n - 8               # inside the 20-bar lookback, clear of the +/-3-bar edge
    lows[dip] = entry * (1.0 - frac_below)
    closes[dip] = entry * (1.0 - frac_below * 0.5)
    return highs, lows, closes


def test_swing_levels_are_reachable_where_the_round_grid_is_inert():
    """Both level generators must be able to win.

    At $96 the round grid is ~1% wide and beats every swing, so a suite built
    only at that magnitude would pass with the swing detector entirely broken —
    an all-``round`` source column indistinguishable from a market with no
    swings.  Sub-cent prices make the grid 20% wide and therefore incapable of
    supplying a candidate, so a level found here is necessarily a swing.
    """
    entry = 0.05
    # 0.85x the 3% designed risk — inside the 0.7-1.3x band by construction.
    highs, lows, closes = _series_with_swing_low_at(entry, 0.03 * 0.85)
    row = ss.compute(
        direction="LONG", entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03,
        highs=highs, lows=lows, closes=closes, tf="15m",
    )
    assert row["refused"] == ""
    assert row["round_step_pct"] > 10.0, "round grid should be inert at this price"
    assert row["sl_source"] == "swing"
    assert row["sl_snapped"] == pytest.approx(entry * (1.0 - 0.03 * 0.85) * 0.999)


def test_a_swing_nearer_than_the_band_is_not_a_candidate():
    """The band is relative to the DESIGNED RISK, not to price.

    This is the property that decides how often the lane can say anything at
    all, and it is not obvious: a 3% stop puts the search band at 2.1-3.9%
    from entry, while a quiet 20-bar window's swings sit well inside 1%.  Such
    a swing is real structure and is still **not** a candidate — the snap will
    not reach past its own bound to find one, and the row reports ``none``
    rather than snapping to whatever is closest.

    Pinned because the tempting "fix" on seeing a book full of ``none`` is to
    widen the band, which would be a threshold invented to fit a window.
    """
    entry = 0.05
    highs, lows, closes = _series_with_swing_low_at(entry, 0.003)  # 0.3%, way inside
    row = ss.compute(
        direction="LONG", entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03,
        highs=highs, lows=lows, closes=closes, tf="15m",
    )
    assert row["refused"] == ""            # the measurement succeeded...
    assert row["n_swing_lows"] >= 1        # ...and it did see the swing...
    assert row["sl_source"] == "none"      # ...and correctly declined it.
    assert row["sl_snapped"] == row["sl_arith"]
    assert row["sl_shift_pct"] == pytest.approx(0.0)


def test_apply_refuses_rather_than_widening_back_to_the_min_distance(monkeypatch):
    """The snap band bottoms out at 0.7x the designed risk, which can land
    inside the ``max(0.8%, 1xATR)`` floor the clamp above enforces.  Quietly
    widening back to the floor books a stop nobody chose — refuse and name it.
    """
    monkeypatch.setattr(ss, "apply_enabled", lambda _sc: True)
    c = _candles()
    entry = float(c["close"][-1])
    sig = _Sig(entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03)
    before_sl = sig.stop_loss
    # A floor larger than any level the band can offer.
    row = ss.stamp_and_apply(sig, candles=c, min_sl_distance=entry)
    assert row["applied_sl"] is False
    assert row["apply_refused"] == ss.REFUSE_MIN_DISTANCE
    assert sig.stop_loss == before_sl
    assert ss.get_counters().refused[ss.REFUSE_MIN_DISTANCE] == 1


def test_unknown_setup_is_refused_and_named_not_defaulted_to_5m():
    sig = _Sig(entry=100.0, stop_loss=97.0, tp1=103.0, setup_class="BRAND_NEW_PATH")
    row = ss.stamp_and_apply(sig, candles=_candles(), min_sl_distance=0.0)
    assert row["refused"] == ss.REFUSE_TF_UNKNOWN
    assert ss.get_counters().refused[ss.REFUSE_TF_UNKNOWN] == 1


def test_a_signal_is_stamped_exactly_once():
    c = _candles()
    entry = float(c["close"][-1])
    sig = _Sig(entry=entry, stop_loss=entry * 0.97, tp1=entry * 1.03)
    ss.stamp_and_apply(sig, candles=c, min_sl_distance=0.0)
    ss.stamp_and_apply(sig, candles=c, min_sl_distance=0.0)
    assert len(ss.get_ledger().rows()) == 1
    assert ss.get_ledger().duplicate_skips == 1


def test_measure_disabled_stamps_nothing(monkeypatch):
    monkeypatch.setattr(ss, "measure_enabled", lambda: False)
    sig = _Sig(entry=100.0, stop_loss=97.0, tp1=103.0)
    assert ss.stamp_and_apply(sig, candles=_candles(), min_sl_distance=0.0) is None
    assert ss.get_ledger().rows() == []


# ---------------------------------------------------------------------------
# Ledger
# ---------------------------------------------------------------------------

def test_in_memory_ledger_never_touches_disk(tmp_path, monkeypatch):
    """``path=""`` means in-memory.  A no-op that writes a stray .tmp into the
    repo root conflicted on every merge for two months and raised into
    fail_open on every test run."""
    monkeypatch.chdir(tmp_path)
    led = ss.SnapLedger(path="")
    led.add({"signal_id": "X"})
    assert led.flush(force=True) is False
    assert list(tmp_path.iterdir()) == []


def test_flush_writes_spec_and_the_ring_denominator(tmp_path):
    path = tmp_path / "snap.json"
    led = ss.SnapLedger(path=str(path), max_rows=2)
    for i in range(4):
        led.add({"signal_id": f"S{i}"})
    assert led.flush(force=True) is True
    payload = json.loads(path.read_text())
    assert payload["schema"] == ss.SCHEMA
    # The ring is capped, so every rate on it is a sample. Persist the
    # eviction count WITH the data — a reader in another process cannot see
    # the cap, and a verdict without its denominator reads as covering all.
    assert payload["max_rows"] == 2
    assert payload["evicted"] == 2
    assert payload["spec"]["tp1_direction"] == "nearer_only"
    assert "sl_band" in payload["spec"]


def test_flush_forced_writes_even_when_unchanged(tmp_path):
    """A heartbeat that only fires on change is not a heartbeat — an idle lane
    that stops writing renders as STALE, which is a fault that is not
    happening."""
    path = tmp_path / "snap.json"
    led = ss.SnapLedger(path=str(path))
    led.add({"signal_id": "S0"})
    assert led.flush() is True
    assert led.flush() is False          # unchanged, unforced
    assert led.flush(force=True) is True  # unchanged, forced


def test_apply_paths_allowlist_is_per_path(monkeypatch):
    """One global flag would flip 19 paths at once on evidence gathered from
    the one path that is ~59% of the book."""
    calls = {"structural_snap_apply": True,
             "structural_snap_apply_paths": "SR_FLIP_RETEST"}
    import src.runtime_tunables as rt
    monkeypatch.setattr(rt, "get", lambda k: calls.get(k))
    monkeypatch.setattr(ss, "apply_enabled", _REAL_APPLY_ENABLED)
    assert ss.apply_enabled("SR_FLIP_RETEST") is True
    assert ss.apply_enabled("MOVER_TREND_PULLBACK") is False

    calls["structural_snap_apply"] = False
    assert ss.apply_enabled("SR_FLIP_RETEST") is False

    calls["structural_snap_apply"] = True
    calls["structural_snap_apply_paths"] = ""
    assert ss.apply_enabled("SR_FLIP_RETEST") is False


class TestRedetectThrottle:
    """One move, one row.

    A setup persists across many scans, so without this the ledger's verdict is
    an artefact of re-detection rather than of the mechanism. Owner export
    2026-08-05: 51 rows from 6 distinct setups, EPICUSDT SHORT alone 30 of them
    (59%), every one carrying the IDENTICAL shift_pct — one level and one
    geometry counted thirty times.

    The same shape had already filled this ledger with 211 re-detections of one
    RIFUSDT setup, and SLXUSDT's 10 rows in 2h10m inside a 0.37% spread inverted
    a whole population's sign: 32% win per row against 55% per move.
    """

    def _sig(self, symbol="EPICUSDT", direction="SHORT", sid="a"):
        from src.smc import Direction

        class _S:
            pass

        s = _S()
        s.signal_id = sid
        s.symbol = symbol
        s.setup_class = "MOVER_TREND_PULLBACK"
        s.direction = Direction.SHORT if direction == "SHORT" else Direction.LONG
        s.entry = 100.0
        s.stop_loss = 102.0
        s.tp1 = 97.0
        s.atr_val = 1.0
        return s

    def test_a_persisting_setup_stamps_once_not_once_per_scan(self):
        import src.structural_snap as snap

        snap.reset_redetect_state()
        first = snap.stamp_and_apply(self._sig(sid="a"), candles=None)
        second = snap.stamp_and_apply(self._sig(sid="b"), candles=None)
        assert first is not None, "the first detection must stamp"
        assert second is None, "a re-detection of the same setup stamped again"
        snap.reset_redetect_state()

    def test_the_throttle_is_counted_never_silent(self):
        """A suppressed re-detection and a setup that never fired are different
        facts, and the panel divides by this to show real concentration."""
        import src.structural_snap as snap

        snap.reset_redetect_state()
        before = dict(snap.get_counters().refused)
        snap.stamp_and_apply(self._sig(sid="a"), candles=None)
        snap.stamp_and_apply(self._sig(sid="b"), candles=None)
        after = snap.get_counters().refused
        assert after.get(snap.REFUSE_REDETECT, 0) > before.get(snap.REFUSE_REDETECT, 0)
        snap.reset_redetect_state()

    def test_a_different_setup_on_the_same_symbol_is_not_throttled(self):
        """A LONG and a SHORT on one symbol are genuinely different evidence."""
        import src.structural_snap as snap

        snap.reset_redetect_state()
        assert snap.stamp_and_apply(self._sig(direction="SHORT", sid="a"), candles=None) is not None
        assert snap.stamp_and_apply(self._sig(direction="LONG", sid="b"), candles=None) is not None
        snap.reset_redetect_state()

    def test_the_key_carries_nothing_that_can_oscillate(self):
        """A key that splits a budget multiplies it — the SAR cooldown carried
        provenance, so a candidate flipping across a gate boundary held two
        budgets and 21 of 21 sub-cooldown repeats were flips, not misses."""
        import src.structural_snap as snap

        key = snap._redetect_key("EPICUSDT", "SHORT", "MOVER_TREND_PULLBACK")
        assert key == "EPICUSDT|SHORT|MOVER_TREND_PULLBACK"
        for volatile in ("provenance", "apply_mode", "level_source", "shift"):
            assert volatile not in key
