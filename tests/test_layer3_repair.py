"""Phase 3 — the order-block detector that never existed, and the 12-bar FVG.

The load-bearing test here is `test_the_live_fvg_list_is_byte_identical`: both
changes WIDEN a rejecting gate, so shipping either one live would change what
emits with nothing measured behind it. Dark means the detector runs for real and
the gates behave identically — not that the change is switched off.
"""
from __future__ import annotations

import numpy as np
import pytest

from src import layer3_repair as l3
from src.smc import Direction, detect_fvg


def _series(seed=0, n=200, drift=0.0):
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(drift, 0.8, n))
    high = close + rng.uniform(0.0, 1.2, n)
    low = close - rng.uniform(0.0, 1.2, n)
    open_ = close + rng.normal(0, 0.3, n)
    return high, low, close, open_


# ── the property the whole phase rests on ─────────────────────────────────

@pytest.mark.parametrize("seed", range(25))
def test_the_live_fvg_list_is_byte_identical(seed):
    """Detection runs once at the WIDE window and the live list is filtered out
    of it. If that filter is not exactly `detect_fvg(lookback=narrow)`, the
    gates silently change behaviour on deploy — which is the one thing dark
    forbids."""
    high, low, close, _ = _series(seed)
    n = len(close)
    direct = detect_fvg(high, low, close, lookback=10)
    derived = l3.narrow_from_wide(detect_fvg(high, low, close, lookback=60), n, 10)
    assert [(z.index, z.direction, z.gap_high, z.gap_low) for z in direct] == \
           [(z.index, z.direction, z.gap_high, z.gap_low) for z in derived]


def test_the_wide_window_finds_at_least_as_much_as_the_narrow_one():
    """A superset by construction — the narrow list is a filter of it."""
    high, low, close, _ = _series(3)
    narrow = detect_fvg(high, low, close, lookback=10)
    wide = detect_fvg(high, low, close, lookback=60)
    assert len(wide) >= len(narrow)


# ── the detector that never existed ───────────────────────────────────────

def test_the_detector_produces_real_output():
    """`orderblocks` had NO writer — 474,467 observations, 100% empty."""
    high, low, close, open_ = _series(1, n=300)
    obs = l3.detect_orderblocks(high, low, close, open_)
    assert isinstance(obs, list)
    assert obs, "the detector found nothing on a 300-bar random walk"


def test_an_orderblock_uses_the_same_vocabulary_the_consumer_reads():
    """`_funding_extreme_structure_tp1` prices `list(fvgs) + list(orderblocks)`
    through ONE reader that tries gap_high/top/level/price. A producer inventing
    its own field names there is the `zone_distance_atr` failure exactly — the
    reader skips every zone it cannot price, and skipping is indistinguishable
    from having none."""
    high, low, close, open_ = _series(1, n=300)
    obs = l3.detect_orderblocks(high, low, close, open_)
    for ob in obs:
        assert "gap_high" in ob and "gap_low" in ob
        assert ob["gap_high"] >= ob["gap_low"]
        assert ob["direction"] in (Direction.LONG, Direction.SHORT)


def test_the_real_consumer_can_price_a_real_orderblock():
    """Drives the real producer THROUGH the real consumer. A mock whose keys I
    chose would assert my assumption back at me and go green over dead code."""
    from src.channels.scalp import _funding_extreme_structure_tp1

    high, low, close, open_ = _series(1, n=300)
    obs = l3.detect_orderblocks(high, low, close, open_)
    assert obs
    tp1 = _funding_extreme_structure_tp1(
        [], obs, float(close[-1]), Direction.LONG, sl_dist=float(close[-1]) * 0.01,
    )
    assert tp1 > 0


def test_displacement_is_required():
    """Without it every second bar qualifies and the output is noise wearing a
    name. A flat series has no impulsive move and must yield nothing."""
    n = 100
    close = np.full(n, 100.0)
    high = close + 0.5
    low = close - 0.5
    open_ = close.copy()
    assert l3.detect_orderblocks(high, low, close, open_) == []


def test_a_short_series_refuses_rather_than_clamping():
    assert l3.detect_orderblocks(
        np.array([1.0, 2.0]), np.array([0.5, 1.0]),
        np.array([1.0, 1.5]), np.array([0.8, 1.2]),
    ) == []


# ── dark: the measurement runs, the effect does not ───────────────────────

def test_the_effect_flags_default_off_and_the_measurement_on():
    import config
    assert config.ORDERBLOCKS_MEASURE is True      # detector runs
    assert config.ORDERBLOCKS_LIVE is False        # gates do not see it
    assert config.FVG_WIDE_LIVE is False           # gates keep the narrow list
    assert config.FVG_LOOKBACK == 10
    assert config.FVG_LOOKBACK_WIDE > config.FVG_LOOKBACK


def test_the_detector_output_does_not_reach_the_gates():
    """The load-bearing assertion. Eight `bool(fvgs) or bool(orderblocks)`
    gates read `smc_data["orderblocks"]`; while dark it must stay empty however
    much the detector finds."""
    from src.detector import SMCDetector

    high, low, close, open_ = _series(1, n=300)
    cd = {"high": high, "low": low, "close": close, "open": open_,
          "volume": np.ones(len(close))}
    r = SMCDetector().detect(symbol="T", candles={"5m": cd}, ticks=[])

    assert r.orderblocks == [], "a dark detector reached the live gate key"
    assert r.orderblocks_measured, "the detector did not actually run"
    assert r.orderblocks_detector_status == "measured_dark"
    # ...and the same for FVG.
    assert len(r.fvg) == len(detect_fvg(high, low, close, lookback=10))
    assert len(r.fvg_wide) >= len(r.fvg)


def test_the_status_names_its_state_rather_than_a_boolean():
    """`not_implemented` was true for years, and a dead primitive behind a
    passing gate looks identical to a working one."""
    assert l3.detector_status() == "measured_dark"


def test_as_dict_carries_the_measured_keys():
    """A field one writer populates and one serializer drops is invisible at
    both ends (#842). The scan context is rebuilt from `as_dict()`."""
    from src.detector import SMCResult

    d = SMCResult().as_dict()
    for k in ("orderblocks_measured", "fvg_wide",
              "fvg_lookback_live", "fvg_lookback_wide"):
        assert k in d, f"{k} does not survive as_dict()"


# ── the census, and what it may not claim ─────────────────────────────────

def test_the_census_counts_gate_flips_not_zones():
    """The gate asks a yes/no question, so a rate over zones would move with
    how many gaps a volatile symbol carries rather than with how often the gate
    would change its answer."""
    l3.reset_census()
    z = detect_fvg(*_series(2)[:3], lookback=60)
    l3.observe(fvg_narrow=[], fvg_wide=z or [object()], orderblocks=[])
    l3.observe(fvg_narrow=[object()], fvg_wide=[object()], orderblocks=[])
    l3.observe(fvg_narrow=[], fvg_wide=[], orderblocks=[object()])
    c = l3.census()
    assert c["detections"] == 3
    assert c["fvg_narrow_empty_wide_found"] == 1   # gate would flip
    assert c["fvg_narrow_found"] == 1
    assert c["ob_found_when_fvg_empty"] == 1       # the OB gate would flip
    l3.reset_census()
