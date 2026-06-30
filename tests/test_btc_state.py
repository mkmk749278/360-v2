"""Unit tests for the graded BTC-State soft-confirmation (src/btc_state.py).

Deterministic + synthetic — no network, no indicator-engine dependency.  Covers the
three layers and the S38 acceptance thesis: a coupled counter-trend LONG in a hostile
BTC gets haircut, the SHORT in the same conditions does not, and a decoupled LONG
survives.
"""
from __future__ import annotations

import numpy as np

from src.btc_state import (
    DEFAULT_SEVERE_SETUPS,
    compute_btc_state,
    compute_downside_coupling,
    compute_haircut_factor,
    macro_direction,
)


def _candles(closes):
    """Build a candle dict (np arrays) from a close series; tight H/L band."""
    c = np.asarray(closes, dtype=np.float64)
    return {"close": c, "high": c * 1.001, "low": c * 0.999, "open": c, "volume": np.ones_like(c)}


def _trend(start, step, n=120):
    return [start + step * i for i in range(n)]


# ---------------------------------------------------------------------------
# compute_btc_state
# ---------------------------------------------------------------------------

class TestComputeBtcState:
    def test_strong_uptrend_positive_b(self):
        up = _candles(_trend(100.0, 0.5))  # steadily rising
        res = compute_btc_state({"5m": up, "15m": up, "1h": up})
        assert res["status"] == "ok"
        assert res["b"] > 0.5, res

    def test_strong_downtrend_negative_b(self):
        down = _candles(_trend(160.0, -0.5))
        res = compute_btc_state({"5m": down, "15m": down, "1h": down})
        assert res["status"] == "ok"
        assert res["b"] < -0.5, res

    def test_downtrend_is_hostile_to_longs(self):
        # The core S38 read: a falling BTC produces b<0 (longs at risk).
        down = _candles(_trend(160.0, -0.4))
        assert compute_btc_state({"1h": down})["b"] < 0.0

    def test_flat_chop_shrinks_toward_zero(self):
        flat = _candles([100.0 + (0.05 if i % 2 else -0.05) for i in range(120)])
        res = compute_btc_state({"5m": flat, "15m": flat, "1h": flat})
        assert abs(res["b"]) < 0.25, res  # tangled EMAs → damped conviction

    def test_insufficient_data_is_neutral_noop(self):
        short = _candles(_trend(100.0, 0.5, n=10))
        res = compute_btc_state({"1h": short})
        assert res["status"] == "insufficient_data"
        assert res["b"] == 0.0

    def test_empty_input_is_neutral(self):
        res = compute_btc_state({})
        assert res["b"] == 0.0 and res["status"] == "insufficient_data"

    def test_partial_tf_subset_still_scores(self):
        up = _candles(_trend(100.0, 0.5))
        res = compute_btc_state({"1h": up})  # only one TF warm
        assert res["status"] == "ok"
        assert "1h" in res["per_tf"] and res["b"] > 0.0


# ---------------------------------------------------------------------------
# compute_downside_coupling
# ---------------------------------------------------------------------------

class TestComputeDownsideCoupling:
    def _series_from_returns(self, rets, start=100.0):
        out = [start]
        for r in rets:
            out.append(out[-1] * (1.0 + r))
        return out

    def test_pair_that_follows_btc_down_is_coupled(self):
        rng = np.random.default_rng(0)
        btc_rets = rng.normal(0.0, 0.01, 250)
        pair_rets = btc_rets * 1.0  # perfectly tracks BTC
        btc = self._series_from_returns(btc_rets)
        pair = self._series_from_returns(pair_rets)
        res = compute_downside_coupling(pair, btc)
        assert res["status"] == "ok"
        assert res["w_pair"] > 0.7, res

    def test_decoupled_pair_is_exempt(self):
        rng = np.random.default_rng(1)
        btc_rets = rng.normal(0.0, 0.01, 250)
        pair_rets = rng.normal(0.0, 0.01, 250)  # independent
        res = compute_downside_coupling(
            self._series_from_returns(pair_rets), self._series_from_returns(btc_rets)
        )
        assert res["w_pair"] < 0.3, res

    def test_inverse_pair_is_not_coupled(self):
        # A pair that rises when BTC falls (hedge) has negative down-corr → w_pair 0.
        rng = np.random.default_rng(2)
        btc_rets = rng.normal(0.0, 0.01, 250)
        pair_rets = -btc_rets
        res = compute_downside_coupling(
            self._series_from_returns(pair_rets), self._series_from_returns(btc_rets)
        )
        assert res["w_pair"] == 0.0, res

    def test_insufficient_samples_is_noop(self):
        res = compute_downside_coupling([100, 101, 102], [100, 99, 98])
        assert res["w_pair"] == 0.0 and res["status"] == "insufficient_data"

    def test_high_beta_pair_scores_high(self):
        rng = np.random.default_rng(3)
        btc_rets = rng.normal(0.0, 0.01, 300)
        pair_rets = btc_rets * 1.8  # amplifies BTC moves
        res = compute_downside_coupling(
            self._series_from_returns(pair_rets), self._series_from_returns(btc_rets)
        )
        assert res["w_pair"] > 0.8, res


# ---------------------------------------------------------------------------
# compute_haircut_factor
# ---------------------------------------------------------------------------

class TestComputeHaircutFactor:
    def test_counter_trend_long_in_hostile_btc_is_cut(self):
        hc = compute_haircut_factor(-0.8, 0.9, "LONG", "SR_FLIP_RETEST")
        assert hc["applied"] is True
        assert hc["factor"] < 1.0

    def test_aligned_short_in_hostile_btc_not_cut(self):
        # BTC falling (b<0) + SHORT = aligned → no haircut.
        hc = compute_haircut_factor(-0.8, 0.9, "SHORT", "SR_FLIP_RETEST")
        assert hc["applied"] is False
        assert hc["factor"] == 1.0

    def test_aligned_long_in_supportive_btc_not_cut(self):
        hc = compute_haircut_factor(0.8, 0.9, "LONG", "SR_FLIP_RETEST")
        assert hc["applied"] is False and hc["factor"] == 1.0

    def test_counter_trend_short_in_supportive_btc_is_cut(self):
        # BTC rising (b>0) + SHORT = counter → haircut, but milder than the long side.
        hc = compute_haircut_factor(0.8, 0.9, "SHORT", "SR_FLIP_RETEST")
        assert hc["applied"] is True and hc["factor"] < 1.0

    def test_long_penalised_harder_than_short_asymmetry(self):
        long_hc = compute_haircut_factor(-0.8, 0.9, "LONG", "SR_FLIP_RETEST")
        short_hc = compute_haircut_factor(0.8, 0.9, "SHORT", "SR_FLIP_RETEST")
        # Same |b|, same coupling, same setup → the LONG cut is deeper (lower factor).
        assert long_hc["factor"] < short_hc["factor"]

    def test_severe_setup_cut_deeper_than_mild(self):
        severe = compute_haircut_factor(-0.8, 0.9, "LONG", "SR_FLIP_RETEST")
        mild = compute_haircut_factor(-0.8, 0.9, "LONG", "VOLUME_SURGE_BREAKOUT")
        assert severe["factor"] < mild["factor"]

    def test_decoupled_pair_not_cut_even_when_counter(self):
        hc = compute_haircut_factor(-0.9, 0.0, "LONG", "SR_FLIP_RETEST")
        assert hc["applied"] is False and hc["factor"] == 1.0

    def test_factor_floored(self):
        # Extreme inputs cannot drive the factor below the floor.
        hc = compute_haircut_factor(-1.0, 1.0, "LONG", "SR_FLIP_RETEST", k=5.0, floor=0.5)
        assert hc["factor"] == 0.5

    def test_neutral_btc_no_cut(self):
        hc = compute_haircut_factor(0.0, 0.9, "LONG", "SR_FLIP_RETEST")
        assert hc["applied"] is False and hc["factor"] == 1.0

    def test_severe_setups_catalog(self):
        assert {"SR_FLIP_RETEST", "LIQUIDITY_SWEEP_REVERSAL", "MOVER_TREND_PULLBACK"} == set(
            DEFAULT_SEVERE_SETUPS
        )


# ---------------------------------------------------------------------------
# macro_direction — the S39 directional gate ("direction, not a fence")
# ---------------------------------------------------------------------------

class TestMacroDirection:
    def test_clean_uptrend_allows_longs(self):
        rising = [100.0 + i for i in range(70)]
        res = macro_direction(rising, fast_period=50)
        assert res["longs_suppressed"] is False
        assert res["regime"] in ("BULL", "RECOVERY") and res["direction"] == "up"

    def test_clean_downtrend_suppresses_longs(self):
        falling = [200.0 - i for i in range(70)]
        res = macro_direction(falling, fast_period=50)
        assert res["longs_suppressed"] is True and res["regime"] == "DECLINE"

    def test_fall_from_top_suppresses_on_losing_the_fast_ma(self):
        # 60 rising weeks then a sharp drop that loses the fast MA — the owner's
        # "falling from top to MA" case.  The static 200-line would still read the
        # price as above it (no suppression); the directional gate de-risks here.
        series = [100.0 + i for i in range(60)] + [159.0 - 11.0 * j for j in range(1, 9)]
        res = macro_direction(series, fast_period=50)
        assert res["price"] < res["fast_ma"]          # price lost the fast MA
        assert res["longs_suppressed"] is True        # …so we de-risk on the way down
        assert res["regime"] == "DECLINE"

    def test_v_recovery_restores_longs_with_higher_low(self):
        # Deep decline then a strong reclaim with a higher low — longs come back.
        series = [200.0 - 3.0 * i for i in range(40)] + [80.0 + 4.0 * j for j in range(1, 25)]
        res = macro_direction(series, fast_period=50)
        assert res["higher_low"] is True
        assert res["longs_suppressed"] is False
        assert res["regime"] in ("RECOVERY", "BULL") and res["direction"] == "up"

    def test_insufficient_data_fails_open_not_suppressed(self):
        res = macro_direction([100.0, 101.0, 102.0], fast_period=50)
        assert res["longs_suppressed"] is False and res["status"] == "insufficient_data"

    def test_accepts_numpy_array(self):
        falling = np.asarray([200.0 - i for i in range(70)], dtype=np.float64)
        res = macro_direction(falling, fast_period=50)
        assert res["longs_suppressed"] is True  # no ambiguous-truth crash on np input

    def test_buffer_deadband_holds_neutral_at_the_line(self):
        # Price sitting basically on a flat fast MA → no suppression (neutral).
        flat = [100.0 + (0.1 if i % 2 else -0.1) for i in range(70)]
        res = macro_direction(flat, fast_period=50, buffer_pct=0.02)
        assert res["longs_suppressed"] is False


# ---------------------------------------------------------------------------
# Acceptance: the S38 thesis, end to end through the three layers
# ---------------------------------------------------------------------------

class TestS38Acceptance:
    def _coupled_pair_vs_falling_btc(self, beta):
        rng = np.random.default_rng(7)
        btc_rets = rng.normal(-0.002, 0.012, 300)  # net downtrend
        pair_rets = btc_rets * beta
        btc = [100.0]
        for r in btc_rets:
            btc.append(btc[-1] * (1.0 + r))
        pair = [100.0]
        for r in pair_rets:
            pair.append(pair[-1] * (1.0 + r))
        return pair, btc

    def test_coupled_counter_long_cut_but_short_survives(self):
        pair, btc = self._coupled_pair_vs_falling_btc(beta=1.2)
        b = compute_btc_state({"1h": _candles(btc)})["b"]
        assert b < 0.0  # BTC hostile
        w = compute_downside_coupling(pair, btc)["w_pair"]
        assert w > 0.5  # pair is BTC-led on the downside
        long_cut = compute_haircut_factor(b, w, "LONG", "SR_FLIP_RETEST")
        short = compute_haircut_factor(b, w, "SHORT", "SR_FLIP_RETEST")
        assert long_cut["applied"] and long_cut["factor"] < 1.0
        assert short["applied"] is False and short["factor"] == 1.0

    def test_decoupled_long_survives_hostile_btc(self):
        rng = np.random.default_rng(11)
        btc_rets = rng.normal(-0.002, 0.012, 300)
        pair_rets = rng.normal(0.0, 0.02, 300)  # own catalyst, ignores BTC
        btc = [100.0]
        for r in btc_rets:
            btc.append(btc[-1] * (1.0 + r))
        pair = [100.0]
        for r in pair_rets:
            pair.append(pair[-1] * (1.0 + r))
        b = compute_btc_state({"1h": _candles(btc)})["b"]
        w = compute_downside_coupling(pair, btc)["w_pair"]
        hc = compute_haircut_factor(b, w, "LONG", "SR_FLIP_RETEST")
        # Decoupled ⇒ w_pair small ⇒ minimal-to-no cut.
        assert hc["factor"] > 0.85, (b, w, hc)
