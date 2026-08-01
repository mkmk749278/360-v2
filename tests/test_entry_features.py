"""MVRTP entry-feature stamps: recorded, never applied.

Owner, 2026-08-01: *"taking entry is matter, how we are taking entry based on
only EMA or what, what if we add some more data to that"* — and *"we need to
know the difference as of now vs later"*.

Two properties matter and both are pinned here:

1. **The stamp changes nothing.** A signal emitted with this lane on must be
   identical to one emitted with it off. This is the whole safety argument, and
   it is the one a future edit is most likely to break.
2. **The now-vs-later split is honest.** ``split_by_feature`` reports the book as
   it shipped beside the book a candidate rule would have produced, and it must
   never quietly move the rows a rule could not have judged into the side that
   flatters it.

The feature helpers refuse rather than clamp: a missing order book is ``None``,
not ``0.0``. Zero is a *reading* — perfectly balanced depth — and reporting one
nobody took is the failure this repo keeps paying for.
"""
from __future__ import annotations

import pytest

from src import entry_features as ef


# --------------------------------------------------------------------------- #
# Feature helpers — each refuses on inputs that cannot support it
# --------------------------------------------------------------------------- #


class TestPullbackVolumeRatio:
    def test_a_quiet_pullback_reads_below_one(self):
        vols = [100.0] * 20 + [40.0] * 6
        assert ef.pullback_volume_ratio(vols) == pytest.approx(0.4)

    def test_a_sold_pullback_reads_above_one(self):
        vols = [100.0] * 20 + [250.0] * 6
        assert ef.pullback_volume_ratio(vols) == pytest.approx(2.5)

    def test_too_little_history_refuses(self):
        assert ef.pullback_volume_ratio([100.0] * 10) is None

    def test_a_zero_baseline_refuses_rather_than_dividing(self):
        """A ratio against no baseline is not a large number, it is not a
        number. Returning inf here would rank this candidate top of any sort."""
        assert ef.pullback_volume_ratio([0.0] * 20 + [50.0] * 6) is None

    def test_none_series_refuses(self):
        assert ef.pullback_volume_ratio(None) is None


class TestCvdSlope:
    def test_absorption_is_positive_selling_is_negative(self):
        rising = list(range(20))
        assert ef.cvd_slope(rising) == pytest.approx(6.0)
        assert ef.cvd_slope(list(reversed(rising))) == pytest.approx(-6.0)

    def test_short_or_absent_series_refuses(self):
        assert ef.cvd_slope(None) is None
        assert ef.cvd_slope([1.0, 2.0]) is None


class TestPullbackDepth:
    def test_depth_is_measured_in_atr_from_the_pre_pullback_close(self):
        closes = [100.0] * 7
        lows = [100.0, 100.0, 98.0, 97.0, 98.0, 99.0]
        assert ef.pullback_depth_atr(closes, lows, None, 1.0, True) == pytest.approx(3.0)

    def test_a_short_short_side_uses_highs(self):
        closes = [100.0] * 7
        highs = [100.0, 100.0, 102.0, 103.0, 102.0, 101.0]
        assert ef.pullback_depth_atr(closes, None, highs, 1.0, False) == pytest.approx(3.0)

    def test_absent_atr_refuses(self):
        assert ef.pullback_depth_atr([100.0] * 7, [99.0] * 6, None, None, True) is None
        assert ef.pullback_depth_atr([100.0] * 7, [99.0] * 6, None, 0.0, True) is None


class TestLevelDistance:
    def _lvl(self, price, type_):
        return {"price": price, "type": type_}

    def test_resistance_above_a_long_is_measured_in_r(self):
        levels = [self._lvl(104.0, "resistance"), self._lvl(90.0, "support")]
        # entry 100, risk 10 -> resistance at +4 is 0.4R away, inside TP1 (1.0R)
        assert ef.level_distance_r(levels, 100.0, 110.0, 10.0, True) == pytest.approx(0.4)

    def test_levels_already_behind_are_ignored(self):
        levels = [self._lvl(96.0, "resistance")]
        assert ef.level_distance_r(levels, 100.0, 110.0, 10.0, True) is None

    def test_an_empty_book_refuses_rather_than_reading_clear(self):
        """"We do not know what is overhead" must not render as "nothing is"."""
        assert ef.level_distance_r([], 100.0, 110.0, 10.0, True) is None
        assert ef.level_distance_r(None, 100.0, 110.0, 10.0, True) is None


class TestBookImbalance:
    def test_bid_heavy_is_positive(self):
        book = {"bids": [[1.0, 30.0]], "asks": [[1.1, 10.0]]}
        assert ef.book_imbalance(book) == pytest.approx(0.5)

    def test_a_missing_book_is_none_not_balanced(self):
        """0.0 means "measured, and balanced". An absent book means neither."""
        assert ef.book_imbalance(None) is None
        assert ef.book_imbalance({"bids": [], "asks": []}) is None
        assert ef.book_imbalance({"bids": [[1.0, 5.0]]}) is None


class TestExtension:
    def test_signed_distance_from_the_slow_ma(self):
        assert ef.extension_pct(110.0, 100.0) == pytest.approx(10.0)
        assert ef.extension_pct(90.0, 100.0) == pytest.approx(-10.0)

    def test_absent_ma_refuses(self):
        assert ef.extension_pct(110.0, None) is None


# --------------------------------------------------------------------------- #
# capture(): degrades per feature, never as a whole
# --------------------------------------------------------------------------- #


def _tf(n=40):
    return {
        "close": [100.0] * n,
        "high": [101.0] * n,
        "low": [99.0] * n,
        "volume": [100.0] * n,
    }


class TestCapture:
    def test_one_dead_input_does_not_cost_the_others(self):
        """An absent order book must not take the volume reading with it —
        that is how a whole population arrives empty and nobody can tell which
        upstream died."""
        feats = ef.capture(
            symbol="BTCUSDT", direction_is_long=True, entry=100.0, sl_dist=3.0,
            tp1=103.0, trigger="fast_pullback", tf=_tf(), tf_name="15m",
            atr=1.0, ma_slow=95.0, stack_sep_pct=5.0,
            smc_data={"order_book": None, "cvd_15m": list(range(30))},
        )
        assert feats["book_imbalance_aligned"] is None
        assert feats["pullback_vol_ratio"] is not None
        assert feats["cvd_slope_aligned"] is not None
        assert "book_imbalance_aligned" in feats["missing"]
        assert "pullback_vol_ratio" not in feats["missing"]

    def test_missing_lists_exactly_the_none_features(self):
        feats = ef.capture(
            symbol="BTCUSDT", direction_is_long=True, entry=100.0, sl_dist=3.0,
            tp1=103.0, trigger="fast_pullback", tf=_tf(), tf_name="15m",
            atr=1.0, ma_slow=95.0, stack_sep_pct=5.0, smc_data={},
        )
        none_keys = {
            k for k, v in feats.items()
            if v is None and k not in ("missing", "profile_would_reject")
        }
        assert none_keys <= set(feats["missing"])

    def test_an_empty_smc_payload_still_produces_a_row(self):
        """Degrading to a row of Nones is correct; raising is not. The scan must
        not care whether order flow is up."""
        feats = ef.capture(
            symbol="BTCUSDT", direction_is_long=False, entry=100.0, sl_dist=3.0,
            tp1=97.0, trigger="deep_pullback", tf=None, tf_name="15m",
            atr=None, ma_slow=105.0, stack_sep_pct=5.0, smc_data=None,
        )
        assert feats["side"] == "SHORT"
        assert feats["entry_trigger"] == "deep_pullback"

    def test_the_series_timeframe_travels_with_the_row(self):
        """A 5m volume ratio and a 15m one are different measurements. Without
        ``tf_name`` on the row nothing downstream can refuse to pool them."""
        feats = ef.capture(
            symbol="BTCUSDT", direction_is_long=True, entry=100.0, sl_dist=3.0,
            tp1=103.0, trigger="ema21_tag_reclaim", tf=_tf(), tf_name="5m",
            atr=1.0, smc_data={}, entry_ref=99.0, entry_ref_name="ema21_5m",
        )
        assert feats["tf_name"] == "5m"
        assert feats["entry_ref_name"] == "ema21_5m"

    def test_a_directional_read_is_signed_toward_the_trade(self):
        """A falling CVD is the dip being sold: bad for a long, and exactly what
        a short wants. Stored raw and split with one "higher is better" rule, it
        scores every short backwards — which is what schema 1 did."""
        smc = {"cvd_15m": [float(i) for i in range(30)]}  # rising CVD
        long_row = ef.capture(
            symbol="X", direction_is_long=True, entry=100.0, sl_dist=3.0,
            tp1=103.0, trigger="t", tf=_tf(), tf_name="15m", atr=1.0, smc_data=smc,
        )
        short_row = ef.capture(
            symbol="X", direction_is_long=False, entry=100.0, sl_dist=3.0,
            tp1=97.0, trigger="t", tf=_tf(), tf_name="15m", atr=1.0, smc_data=smc,
        )
        assert long_row["cvd_slope_aligned"] > 0
        assert short_row["cvd_slope_aligned"] < 0
        assert long_row["cvd_slope_aligned"] == -short_row["cvd_slope_aligned"]

    def test_extras_merge_flat_and_share_the_missing_accounting(self):
        """A path-specific feature that stops computing must be as visible as a
        core one — otherwise the interesting half of the row fails silently."""
        feats = ef.capture(
            symbol="X", direction_is_long=True, entry=100.0, sl_dist=3.0,
            tp1=103.0, trigger="t", tf=_tf(), tf_name="5m", atr=1.0, smc_data={},
            extras={"h1_trend_sep_atr": 2.5, "rsi_at_entry": None},
        )
        assert feats["h1_trend_sep_atr"] == 2.5
        assert "rsi_at_entry" in feats["missing"]
        assert "h1_trend_sep_atr" not in feats["missing"]

    def test_designed_geometry_is_recorded_not_inferred(self):
        """The finding this lane exists to make legible: TP1 inside the stop.
        R divides by the distance the trade is *sized* for, the same denominator
        the closed-signal record carries, so the two are comparable."""
        tight = ef.capture(
            symbol="X", direction_is_long=True, entry=100.0, sl_dist=4.0,
            tp1=102.0, trigger="t", tf=_tf(), tf_name="5m", atr=1.0, smc_data={},
        )
        assert tight["tp1_r_multiple"] == pytest.approx(0.5)
        even = ef.capture(
            symbol="X", direction_is_long=False, entry=100.0, sl_dist=3.0,
            tp1=97.0, trigger="t", tf=_tf(), tf_name="15m", atr=1.0, smc_data={},
        )
        assert even["tp1_r_multiple"] == pytest.approx(1.0)


class TestPathFeatureHelpers:
    """The per-path measurements, which are the point of the generalisation.

    A feature set is not portable just because the code that computes it is —
    these exist because TPE and MVAVW fail in different places than MVRTP.
    """

    def test_retrace_reads_the_giveback_not_the_depth(self):
        # Leg runs 100 -> 120; entry at 110 has given back half of it.
        highs = [100.0 + i for i in range(21)] + [120.0] * 3
        lows = [h - 1.0 for h in highs]
        got = ef.retrace_fraction(highs, lows, 110.0, True, leg_bars=24)
        assert got == pytest.approx((120.0 - 110.0) / (120.0 - 99.0), rel=1e-3)

    def test_retrace_refuses_a_flat_leg_rather_than_returning_zero(self):
        flat = [100.0] * 30
        assert ef.retrace_fraction(flat, flat, 100.0, True) is None

    def test_zone_distance_is_zero_inside_a_zone_not_the_gap_to_its_edge(self):
        """Inside the zone is the strongest reading there is; reporting the
        distance to the nearer edge would make it look like a near miss."""
        zones = [{"top": 105.0, "bottom": 95.0}]
        assert ef.zone_distance_atr(zones, 100.0, 2.0) == 0.0

    def test_zone_distance_measures_the_nearest_of_several(self):
        zones = [{"top": 130.0, "bottom": 125.0}, {"high": 104.0, "low": 103.0}]
        assert ef.zone_distance_atr(zones, 100.0, 1.5) == pytest.approx(3.0 / 1.5)

    def test_an_absent_zone_book_refuses(self):
        """The gate this replaces passes on *any* zone anywhere. Absent must not
        read as 'nothing overhead'."""
        assert ef.zone_distance_atr([], 100.0, 1.0) is None
        assert ef.zone_distance_atr(None, 100.0, 1.0) is None

    def test_anchor_touches_count_trigger_eligible_returns(self):
        """First return to the anchor is the reload; the fourth is a level that
        keeps failing. MOVER_AVWAP_SCALP cannot tell them apart today."""
        highs = [101.0, 110.0, 101.0, 112.0]
        lows = [99.0, 108.0, 99.0, 110.0]
        # band 2% of 100 -> [98, 102]; bars 0 and 2 intersect it.
        assert ef.anchor_touch_count(highs, lows, 100.0, band_pct=2.0) == 2

    def test_anchor_touches_refuse_without_an_anchor(self):
        assert ef.anchor_touch_count([1.0], [1.0], None, band_pct=2.0) is None


class TestFeatureRegistry:
    def test_each_path_gets_core_plus_its_own(self):
        tpe = ef.features_for("TREND_PULLBACK_EMA")
        mvavw = ef.features_for("MOVER_AVWAP_SCALP")
        assert set(ef.CORE_FEATURES) <= set(tpe)
        assert "retrace_frac_of_leg" in tpe
        assert "anchor_age_bars" in mvavw
        # The point of splitting: neither path's own features leak onto the other.
        assert "anchor_age_bars" not in tpe
        assert "h1_trend_sep_atr" not in mvavw

    def test_an_unknown_path_degrades_to_core_rather_than_raising(self):
        assert ef.features_for("NOT_A_SETUP") == ef.CORE_FEATURES

    def test_every_declared_feature_has_a_split_direction(self):
        """A feature with no entry in the keep-above set is silently treated as
        'lower is better'. That is a real choice and it must be a deliberate one
        for every feature, not a default nobody looked at."""
        undirected = {
            "uses_1h_trend",       # a flag, not a magnitude
            "funding_rate",        # deliberately unsigned — see capture()
            "liq_clusters_n",
        }
        for setup in ef.PATH_FEATURES:
            for feature in ef.features_for(setup):
                if feature in undirected:
                    continue
                assert (
                    feature in ef._KEEP_ABOVE
                    or feature in _LOWER_IS_BETTER
                ), f"{feature} has no deliberate split direction"


#: Features where keeping rows BELOW the threshold is the intended rule. Listed
#: explicitly so the assertion above cannot pass by defaulting.
_LOWER_IS_BETTER = {
    "entry_ref_dist_atr",
    "entry_bar_range_atr",
    "pullback_depth_atr",
    "extension_pct",
    "retrace_frac_of_leg",
    "smc_zone_dist_atr",
    "rsi_at_entry",
    "anchor_age_bars",
    "leg_move_pct",
    "avwap_touches_in_leg",
    "edge_touches",
}


# --------------------------------------------------------------------------- #
# The ledger
# --------------------------------------------------------------------------- #


class _Sig:
    def __init__(self, sid="MVRTP-1"):
        self.signal_id = sid
        self.setup_class = "MOVER_TREND_PULLBACK"
        self.confidence = 75.0
        self.entry_regime = "TRENDING_UP"


class TestLedger:
    def test_a_signal_is_stamped_once(self):
        """A second stamp for one signal_id means the evaluator ran twice on the
        same signal — a fault to count, not to silently overwrite."""
        led = ef.EntryFeatureLedger(path="")
        ef.reset_ledger(led)
        assert ef.stamp(_Sig(), {"a": 1}) is True
        assert ef.stamp(_Sig(), {"a": 2}) is False
        assert len(led.rows()) == 1
        assert led.duplicate_skips == 1
        ef.reset_ledger(None)

    def test_an_in_memory_ledger_never_touches_the_disk(self, tmp_path, monkeypatch):
        """``path=""`` means "do not persist" — and a no-op that writes a .tmp
        into the process cwd is how a stray file got committed on every branch
        for two months, with its failure raising into fail_open every test run.
        Return before the side effect."""
        monkeypatch.chdir(tmp_path)
        led = ef.EntryFeatureLedger(path="")
        led.add({"signal_id": "x"})
        assert led.flush(force=True) is False
        assert list(tmp_path.iterdir()) == []

    def test_it_round_trips_through_the_real_serializer(self, tmp_path):
        """A field that survives in memory and vanishes on disk fixes nothing —
        pin the round trip with the real writer and reader, not a mock."""
        path = str(tmp_path / "ef.json")
        led = ef.EntryFeatureLedger(path=path)
        led.add({"signal_id": "s1", "pullback_vol_ratio": 0.42, "schema": ef.SCHEMA})
        assert led.flush(force=True) is True

        back = ef.EntryFeatureLedger(path=path)
        back.load()
        assert len(back.rows()) == 1
        assert back.rows()[0]["pullback_vol_ratio"] == pytest.approx(0.42)

    def test_a_foreign_schema_is_ignored_not_merged(self, tmp_path):
        path = tmp_path / "ef.json"
        path.write_text('{"schema": 999, "rows": [{"signal_id": "old"}]}')
        led = ef.EntryFeatureLedger(path=str(path))
        led.load()
        assert led.rows() == []

    def test_force_writes_even_when_nothing_changed(self, tmp_path):
        """An idle lane must still refresh the file, or ops cannot tell "no
        signals fired" from "the engine stopped stamping"."""
        path = str(tmp_path / "ef.json")
        led = ef.EntryFeatureLedger(path=path)
        led.add({"signal_id": "s1"})
        led.flush(force=True)
        assert led.flush() is False          # nothing changed, no forced write
        assert led.flush(force=True) is True  # heartbeat


# --------------------------------------------------------------------------- #
# "As of now" vs "later" — the comparison the owner asked for
# --------------------------------------------------------------------------- #


def _row(sid, r, feat=None, pnl=None):
    row = {"signal_id": sid, "r": r, "pnl_pct": pnl if pnl is not None else (r or 0) * 3.0}
    if feat is not None:
        row["pullback_vol_ratio"] = feat
    return row


class TestNowVsLater:
    def test_now_is_the_whole_book_and_keep_is_the_subset(self):
        rows = [_row("a", 1.0, 2.0), _row("b", -1.0, 0.3), _row("c", 2.0, 1.5)]
        out = ef.split_by_feature(rows, "pullback_vol_ratio", 1.0)
        assert out["now"]["n"] == 3
        assert out["keep"]["n"] == 2 and out["drop"]["n"] == 1
        assert out["now"]["avg_r"] == pytest.approx(2.0 / 3.0)
        assert out["keep"]["avg_r"] == pytest.approx(1.5)
        assert out["delta_avg_r"] == pytest.approx(1.5 - 2.0 / 3.0)

    def test_rows_the_rule_could_not_judge_are_their_own_bucket(self):
        """The failure mode this prevents: binning unknowns with ``keep`` lets a
        rule take credit for rows it never filtered."""
        rows = [_row("a", 1.0, 2.0), _row("b", -1.0, None), _row("c", 3.0, None)]
        out = ef.split_by_feature(rows, "pullback_vol_ratio", 1.0)
        assert out["unknown"]["n"] == 2
        assert out["keep"]["n"] == 1
        assert out["keep"]["n"] + out["drop"]["n"] + out["unknown"]["n"] == out["now"]["n"]

    def test_direction_flips_for_features_where_low_is_the_problem(self):
        """``extension_pct`` keeps rows BELOW the threshold — a filter that kept
        the most extended entries would be backwards."""
        rows = [
            {"signal_id": "a", "r": 1.0, "pnl_pct": 3.0, "extension_pct": 2.0},
            {"signal_id": "b", "r": -1.0, "pnl_pct": -3.0, "extension_pct": 25.0},
        ]
        out = ef.split_by_feature(rows, "extension_pct", 10.0)
        assert out["direction"] == "keep <= threshold"
        assert out["keep"]["n"] == 1 and out["drop"]["n"] == 1

    def test_kept_fraction_exposes_a_rule_this_window_never_tested(self):
        rows = [_row(str(i), 1.0, 5.0) for i in range(10)]
        out = ef.split_by_feature(rows, "pullback_vol_ratio", 0.1)
        assert out["kept_fraction"] == pytest.approx(1.0)

    def test_pnl_is_reported_beside_r_because_the_r_subset_is_selected(self):
        """Rows closed before #848 carry no entry-risk denominator, so the
        R-scored population is not a random sample of the book."""
        rows = [_row("a", 1.0, 2.0), {"signal_id": "b", "r": None,
                                      "pnl_pct": -4.0, "pullback_vol_ratio": 2.0}]
        out = ef.split_by_feature(rows, "pullback_vol_ratio", 1.0)
        assert out["keep"]["n"] == 2 and out["keep"]["scored"] == 1
        # Both rows carry a pnl (+3.0 and -4.0); only one carries an R. The R
        # average describes one row, the pnl average describes two — which is
        # exactly why both are published.
        assert out["keep"]["avg_r"] == pytest.approx(1.0)
        assert out["keep"]["avg_pnl_pct"] == pytest.approx(-0.5)

    def test_an_empty_book_yields_none_not_zero(self):
        out = ef.split_by_feature([], "pullback_vol_ratio", 1.0)
        assert out["now"]["avg_r"] is None and out["delta_avg_r"] is None


class TestJoinOutcomes:
    def test_it_joins_on_signal_id_and_divides_by_the_entry_risk(self):
        stamps = [{"signal_id": "s1", "pullback_vol_ratio": 1.4}]
        records = [{"signal_id": "s1", "pnl_pct": -0.1,
                    "sl_distance_pct_at_entry": 3.0, "outcome_label": "SL_HIT"}]
        joined, cov = ef.join_outcomes(stamps, records)
        # The #848 denominator: a BE-shifted scratch is -0.03R, not -1.00R.
        assert joined[0]["r"] == pytest.approx(-0.1 / 3.0)
        assert cov["joined"] == 1 and cov["scored"] == 1

    def test_a_record_without_the_engine_stamp_gets_no_r(self):
        stamps = [{"signal_id": "s1"}]
        records = [{"signal_id": "s1", "pnl_pct": -3.0}]
        joined, cov = ef.join_outcomes(stamps, records)
        assert joined[0]["r"] is None
        assert joined[0]["pnl_pct"] == pytest.approx(-3.0)
        assert cov["scored"] == 0

    def test_stamps_with_no_record_are_counted_not_dropped_silently(self):
        """A stamp with no record is a signal the router dropped, or one still
        open. A join that keeps only what matched reports a book that is not the
        book."""
        stamps = [{"signal_id": "s1"}, {"signal_id": "never-delivered"}]
        records = [{"signal_id": "s1", "pnl_pct": 1.0, "sl_distance_pct_at_entry": 2.0}]
        joined, cov = ef.join_outcomes(stamps, records)
        assert len(joined) == 1
        assert cov["stamped_not_closed"] == 1
        assert cov["stamps"] == 2


class TestSummary:
    def test_it_counts_which_inputs_are_absent(self):
        led = ef.EntryFeatureLedger(path="")
        for i in range(3):
            led.add({"signal_id": f"s{i}", "stamped_at": 1000.0 + i,
                     "missing": ["book_imbalance"]})
        s = ef.summary(led)
        assert s["rows"] == 3
        assert s["missing_by_feature"]["book_imbalance"] == 3
        assert s["schema"] == ef.SCHEMA


class TestPerPathLiveness:
    """A dead input on a rare path must not hide behind a busy one.

    MVRTP alone is ~94% of the delivered book. A TPE-only feature that has gone
    dark contributes a handful of Nones against a ledger-wide row count and can
    never reach it, so a probe dividing by the total reports healthy forever.
    #815's rule: key on the population that would be harmed.
    """

    def test_missing_is_counted_against_each_path_s_own_rows(self):
        led = ef.EntryFeatureLedger(path="")
        for i in range(50):
            led.add({
                "signal_id": f"mv-{i}",
                "setup_class": "MOVER_TREND_PULLBACK",
                "missing": [],
            })
        for i in range(12):
            led.add({
                "signal_id": f"tpe-{i}",
                "setup_class": "TREND_PULLBACK_EMA",
                "missing": ["h1_trend_sep_atr"],   # dead on every TPE row
            })

        per_setup = ef.missing_by_setup(led)
        tpe_rows, tpe_missing = per_setup["TREND_PULLBACK_EMA"]
        assert tpe_rows == 12
        assert tpe_missing["h1_trend_sep_atr"] == 12
        # Reachable per path...
        assert tpe_missing["h1_trend_sep_atr"] >= tpe_rows
        # ...and unreachable against the ledger total, which is the bug.
        assert tpe_missing["h1_trend_sep_atr"] < len(led.rows())

    def test_summary_reports_rows_per_path(self):
        led = ef.EntryFeatureLedger(path="")
        led.add({"signal_id": "a", "setup_class": "MOVER_AVWAP_SCALP", "missing": []})
        led.add({"signal_id": "b", "setup_class": "MOVER_AVWAP_SCALP", "missing": []})
        led.add({"signal_id": "c", "setup_class": "TREND_PULLBACK_EMA", "missing": []})

        got = ef.summary(led)["rows_by_setup"]

        assert got == {"MOVER_AVWAP_SCALP": 2, "TREND_PULLBACK_EMA": 1}


class TestSelect:
    def test_it_splits_the_book_by_path(self):
        rows = [
            {"setup_class": "TREND_PULLBACK_EMA", "r": 1.0},
            {"setup_class": "MOVER_AVWAP_SCALP", "r": -1.0},
            {"setup_class": "TREND_PULLBACK_EMA", "r": 0.5},
        ]
        assert len(ef.select(rows, "TREND_PULLBACK_EMA")) == 2
        assert len(ef.select(rows, "")) == 3

    def test_a_split_reports_the_timeframes_it_pooled(self):
        """A threshold applied across 5m and 15m rows is being applied to two
        scales at once, and the surface has to be able to say so."""
        rows = [
            {"tf_name": "5m", "pullback_vol_ratio": 1.2, "r": 1.0},
            {"tf_name": "15m", "pullback_vol_ratio": 0.8, "r": -1.0},
        ]
        out = ef.split_by_feature(rows, "pullback_vol_ratio", 1.0)
        assert out["timeframes"] == ["15m", "5m"]
