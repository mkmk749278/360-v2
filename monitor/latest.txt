# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `989` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 72 | 72 | 72 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3718 | 3718 | 3017 | 26 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 40470 | 40470 | 27 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 34922 | 34923 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 34670 | 33808 | 1102 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 34946 | 34406 | 617 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 34865 | 34837 | 45 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 26712 | 26706 | 25 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 35025 | 35038 | 16 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 35055 | 33855 | 1763 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 44005 | 49723 | 808 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 40501 | 35322 | 8636 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 34582 | 34583 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 34926 | 34924 | 19 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 34655 | 34641 | 28 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 35623 | 34985 | 950 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 34354 | 34525 | 107 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 26236 | 24653 | 1793 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 26457 | 26379 | 127 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 40433 | 40451 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 26733 | 26748 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2353 | 2353 | 2045 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 181 | 181 | 66 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 75 | 75 | 46 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 9870 | 9870 | 9622 | 6 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 27 | 27 | 12 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 4258 | 4258 | 3393 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1874 | 1874 | 517 | 107 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 20092 | 20092 | 10600 | 459 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 52 | 52 | 39 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 184 | 184 | 125 | 1 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 2599 | 2599 | 2352 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 361 | 361 | 229 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 503 | 503 | 341 | 18 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 41 | 41 | 17 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=40470): breakout_not_found=25996, basic_filters_failed=6606, move_not_fresh=5371, breakout_stale=1338, retest_proximity_failed=992, volume_spike_missing=166, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=34923): cls_disabled_merged_into_lsr=34923
- **EVAL::DIVERGENCE_CONTINUATION** (total=33808): cvd_divergence_failed=15336, h1_trend_not_aligned=8651, basic_filters_failed=4644, ema_alignment_reject=4115, retest_proximity_failed=862, missing_fvg_or_orderblock=200
- **EVAL::FAILED_AUCTION_RECLAIM** (total=34406): auction_not_detected=23773, basic_filters_failed=4224, reclaim_hold_failed=2412, regime_blocked=2206, tail_too_small=1741, rsi_reject=50
- **EVAL::FUNDING_EXTREME** (total=34837): funding_not_extreme=27896, basic_filters_failed=4269, missing_funding_rate=2018, ema_alignment_reject=395, rsi_reject=173, cvd_divergence_failed=56, momentum_reject=23, missing_fvg_or_orderblock=7
- **EVAL::LIQUIDATION_REVERSAL** (total=26706): cascade_threshold_not_met=21695, basic_filters_failed=4572, cvd_divergence_failed=219, rsi_reject=194, missing_fvg_or_orderblock=21, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=35038): no_ma_cross=29093, basic_filters_failed=4651, ma_cross_cooldown=785, ma_cross_htf_misaligned=509
- **EVAL::MEAN_REVERT** (total=33855): no_extension=29747, basic_filters_failed=4108
- **EVAL::MOVER_AVWAP_SCALP** (total=49723): no_avwap_tag=27113, no_mover_leg=8447, basic_filters_failed=6739, avwap_slope_against=5102, avwap_reclaim_no_volume=1435, no_avwap_reclaim=852, anchor_too_recent=35
- **EVAL::MOVER_TREND_PULLBACK** (total=35322): mover_run_too_small=14418, no_reclaim=12396, basic_filters_failed=6672, no_pullback_tag=1836
- **EVAL::OPENING_RANGE_BREAKOUT** (total=34583): feature_disabled=34583
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=34924): breakout_not_found=16867, regime_blocked=15131, basic_filters_failed=2018, adx_reject=809, ema_alignment_reject=99
- **EVAL::QUIET_COMPRESSION_BREAK** (total=34641): regime_blocked=21847, compression_not_detected=9992, basic_filters_failed=2201, breakout_not_detected=552, volume_confirmation_failed=49
- **EVAL::RANGE_FADE** (total=34985): no_range_edge=30875, basic_filters_failed=4110
- **EVAL::SR_FLIP_RETEST** (total=34525): flip_close_not_confirmed=24068, basic_filters_failed=4212, regime_blocked=2189, h1_break_not_confirmed=1342, retest_out_of_zone=1244, long_break_volume_thin=1007, reclaim_hold_failed=338, ema_alignment_reject=56, whipsaw_flip=22, wick_quality_failed=21, long_acceptance_not_held=17, missing_fvg_or_orderblock=9
- **EVAL::STANDARD** (total=24653): momentum_reject=8424, ema_alignment_reject=3859, sweeps_not_detected=3786, adx_reject=3247, basic_filters_failed=3138, macd_reject=1883, htf_poi_unanchored=215, rsi_reject=57, invalid_sl_geometry=44
- **EVAL::TREND_PULLBACK** (total=26379): h1_trend_not_aligned=8111, h1_pullback_not_confirmed=6155, ema_alignment_reject=5003, ema_not_tested_prev=2339, basic_filters_failed=2026, no_ema_reclaim_close=1238, body_conviction_fail=652, rsi_reject=454, prev_already_below_emas=133, prev_already_above_emas=86, no_prev_low_break=74, no_prev_high_break=53, momentum_flat=32, ema21_not_tagged=11, momentum_reject=10, missing_fvg_or_orderblock=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=40451): breakout_not_found=24540, basic_filters_failed=6606, move_not_fresh=6401, breakout_stale=1984, retest_proximity_failed=716, volume_spike_missing=188, missing_fvg_or_orderblock=15, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=26748): momentum_reject=22441, recent_ticks_insufficient=3568, basic_filters_failed=739

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=10): execution:overextended=10
- **DIVERGENCE_CONTINUATION** (total=234): setup_compat:regime_VOLATILE_UNSUITABLE=211, execution:overextended=13, setup_compat:regime_BREAKOUT_EXPANSION=10
- **FAILED_AUCTION_RECLAIM** (total=1410): setup_compat:regime_STRONG_TREND=874, execution:overextended=479, context_floor=57
- **FUNDING_EXTREME_SIGNAL** (total=127): execution:trigger_not_confirmed=115, context_floor=12
- **LIQUIDATION_REVERSAL** (total=75): execution:trigger_not_confirmed=75
- **LIQUIDITY_SWEEP_REVERSAL** (total=3813): setup_compat:regime_STRONG_TREND=2005, execution:trigger_not_confirmed=940, execution:overextended=868
- **MA_CROSS_TREND_SHIFT** (total=28): execution:overextended=10, execution:trigger_not_confirmed=7, setup_compat:regime_DIRTY_RANGE=6, setup_compat:regime_CLEAN_RANGE=5
- **MEAN_REVERT** (total=3728): setup_compat:regime_STRONG_TREND=1927, execution:overextended=916, setup_compat:regime_WEAK_TREND=883, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=1650): execution:overextended=1353, entry_quality=185, execution:trigger_not_confirmed=112
- **MOVER_TREND_PULLBACK** (total=10375): execution:trigger_not_confirmed=4555, execution:overextended=4458, entry_quality=1362
- **QUIET_COMPRESSION_BREAK** (total=16): execution:trigger_not_confirmed=16
- **RANGE_FADE** (total=2280): setup_compat:regime_STRONG_TREND=1119, setup_compat:regime_WEAK_TREND=756, execution:overextended=278, setup_compat:regime_VOLATILE_UNSUITABLE=123, setup_compat:regime_BREAKOUT_EXPANSION=4
- **TREND_PULLBACK_EMA** (total=389): setup_compat:regime_CLEAN_RANGE=206, setup_compat:regime_DIRTY_RANGE=110, setup_compat:regime_VOLATILE_UNSUITABLE=51, entry_quality=22
- **VOLUME_SURGE_BREAKOUT** (total=2): execution:overextended=2

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 65360 | 30.5% |
| TRENDING_DOWN | 59962 | 28.0% |
| TRENDING_UP | 57685 | 26.9% |
| QUIET | 20047 | 9.4% |
| VOLATILE | 11148 | 5.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **122**
- Average confidence gap to threshold: **11.84** (samples=122) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BCHUSDT=19, XLMUSDT=16, SOLUSDT=13, XMRUSDT=12, ASTERUSDT=10, XPINUSDT=7, BNBUSDT=7, BTCUSDT=6, ONDOUSDT=5, LTCUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 74 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 89 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 30 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 28 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 11 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 7 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 14 |
| LIQUIDATION_REVERSAL | filtered | min_confidence | 6 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 31 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 5 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 268 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 18 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 532 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1047 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 15 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2732 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 12 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 41 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 16 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 2 |
| SR_FLIP_RETEST | filtered | min_confidence | 24 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 41 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 40 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 50 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 12 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 78 | 53.21 | 63.45 | 10.24 | 20.65 | 19.80 | 18.41 | 2.37 | 14.63 |
| DIVERGENCE_CONTINUATION | kept | 89 | 69.27 | 65.00 | -4.27 | 21.48 | 19.69 | 18.04 | 1.44 | 1.87 |
| FAILED_AUCTION_RECLAIM | filtered | 58 | 50.32 | 62.90 | 12.58 | 20.98 | 18.73 | 20.00 | 2.02 | 5.52 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 65.25 | 65.00 | -0.25 | 22.49 | 20.00 | 20.00 | 2.59 | 5.60 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 43.36 | 61.89 | 18.53 | 20.78 | 14.60 | 17.20 | 2.56 | 8.73 |
| LIQUIDATION_REVERSAL | filtered | 20 | 43.75 | 26.50 | -17.25 | 19.95 | 8.90 | 15.38 | 5.60 | 11.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 76 | 50.52 | 64.11 | 13.59 | 20.44 | 19.01 | 18.97 | 2.09 | 13.57 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 31 | 69.26 | 65.00 | -4.26 | 21.28 | 19.44 | 16.90 | 3.16 | 0.38 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.00 | 62.33 | 6.33 | 20.80 | 17.07 | 15.80 | 0.00 | 19.17 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 71.15 | 65.00 | -6.15 | 21.75 | 14.65 | 15.80 | 0.00 | 3.60 |
| MEAN_REVERT | filtered | 5 | 46.10 | 65.00 | 18.90 | 21.20 | 17.70 | 17.40 | 0.00 | 21.60 |
| MEAN_REVERT | kept | 3 | 70.77 | 65.00 | -5.77 | 20.80 | 14.00 | 16.07 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 286 | 54.54 | 64.41 | 9.87 | 20.09 | 15.26 | 15.80 | 3.96 | 18.87 |
| MOVER_AVWAP_SCALP | kept | 532 | 79.79 | 65.00 | -14.79 | 19.90 | 14.25 | 15.80 | 4.19 | 5.48 |
| MOVER_TREND_PULLBACK | filtered | 1062 | 55.01 | 63.99 | 8.98 | 20.00 | 18.19 | 15.80 | 4.15 | 19.74 |
| MOVER_TREND_PULLBACK | kept | 2732 | 76.07 | 65.00 | -11.07 | 20.21 | 18.37 | 15.80 | 4.15 | 1.40 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 12 | 56.30 | 61.33 | 5.03 | 19.66 | 20.00 | 15.90 | 3.50 | 6.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 76.00 | 65.00 | -11.00 | 24.10 | 20.00 | 17.70 | 3.50 | 1.80 |
| QUIET_COMPRESSION_BREAK | filtered | 57 | 49.67 | 65.00 | 15.33 | 21.12 | 19.46 | 20.00 | 0.00 | 8.92 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 77.00 | 65.00 | -12.00 | 20.65 | 19.80 | 20.00 | 0.00 | 1.50 |
| SR_FLIP_RETEST | filtered | 24 | 55.29 | 65.00 | 9.71 | 21.00 | 20.00 | 15.60 | 1.50 | 14.82 |
| SR_FLIP_RETEST | kept | 41 | 71.30 | 65.00 | -6.30 | 19.83 | 20.00 | 15.92 | 1.61 | 1.14 |
| TREND_PULLBACK_EMA | filtered | 45 | 56.36 | 64.64 | 8.28 | 19.72 | 19.65 | 17.09 | 4.57 | 15.67 |
| TREND_PULLBACK_EMA | kept | 50 | 79.76 | 65.00 | -14.76 | 21.12 | 19.82 | 18.26 | 5.09 | 0.06 |
| VOLUME_SURGE_BREAKOUT | filtered | 12 | 43.44 | 65.00 | 21.56 | 19.83 | 18.60 | 20.00 | 3.50 | 12.55 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.75 | 65.00 | -8.75 | 19.50 | 17.52 | 20.00 | 4.50 | 6.65 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 78 | 53.21 | 21.62 | 13.77 | 4.35 | 12.35 | 5.35 | 8.02 | 2.37 |
| DIVERGENCE_CONTINUATION | kept | 89 | 69.27 | 23.02 | 15.87 | 4.01 | 12.92 | 5.44 | 9.35 | 1.44 |
| FAILED_AUCTION_RECLAIM | filtered | 58 | 50.32 | 21.10 | 15.31 | 6.16 | 14.00 | 6.57 | 4.66 | 2.02 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 65.25 | 24.27 | 15.09 | 4.09 | 13.55 | 4.59 | 8.03 | 2.59 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 43.36 | 25.00 | 8.00 | 3.00 | 14.78 | 8.61 | 5.14 | 2.56 |
| LIQUIDATION_REVERSAL | filtered | 20 | 43.75 | 25.00 | 8.00 | 14.85 | 8.00 | 4.00 | 1.80 | 5.60 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 76 | 50.52 | 22.79 | 17.26 | 5.68 | 12.93 | 5.04 | 5.80 | 2.09 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 31 | 69.26 | 22.68 | 16.06 | 5.13 | 11.03 | 4.94 | 7.13 | 3.16 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.00 | 21.67 | 14.00 | 8.00 | 14.00 | 9.50 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 71.15 | 20.50 | 14.00 | 10.50 | 14.00 | 6.75 | 9.00 | 0.00 |
| MEAN_REVERT | filtered | 5 | 46.10 | 17.00 | 18.00 | 9.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MEAN_REVERT | kept | 3 | 70.77 | 22.33 | 16.67 | 7.00 | 13.00 | 5.00 | 6.77 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 286 | 54.54 | 18.24 | 18.06 | 12.07 | 14.13 | 6.67 | 5.89 | 3.96 |
| MOVER_AVWAP_SCALP | kept | 532 | 79.79 | 19.02 | 18.00 | 14.22 | 13.88 | 7.63 | 8.49 | 4.19 |
| MOVER_TREND_PULLBACK | filtered | 1062 | 55.01 | 18.24 | 18.06 | 7.69 | 12.51 | 6.27 | 9.01 | 4.15 |
| MOVER_TREND_PULLBACK | kept | 2732 | 76.07 | 19.43 | 18.01 | 7.73 | 12.19 | 6.81 | 9.28 | 4.15 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 12 | 56.30 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 5.30 | 3.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 76.00 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 5.30 | 3.50 |
| QUIET_COMPRESSION_BREAK | filtered | 57 | 49.67 | 19.25 | 16.88 | 11.79 | 14.26 | 6.46 | 4.01 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 77.00 | 21.00 | 18.00 | 13.50 | 14.00 | 5.00 | 7.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 24 | 55.29 | 19.67 | 18.00 | 4.00 | 13.00 | 5.00 | 8.94 | 1.50 |
| SR_FLIP_RETEST | kept | 41 | 71.30 | 20.07 | 17.27 | 7.68 | 12.80 | 5.07 | 8.22 | 1.61 |
| TREND_PULLBACK_EMA | filtered | 45 | 56.36 | 16.87 | 18.09 | 7.50 | 14.40 | 7.29 | 7.98 | 4.57 |
| TREND_PULLBACK_EMA | kept | 50 | 79.76 | 18.54 | 18.00 | 7.65 | 14.80 | 8.14 | 9.34 | 5.09 |
| VOLUME_SURGE_BREAKOUT | filtered | 12 | 43.44 | 19.67 | 14.00 | 15.00 | 11.00 | 3.12 | 4.70 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.75 | 19.00 | 17.00 | 13.50 | 13.25 | 5.00 | 8.15 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 78 | 53.21 | 0.00 | 0.00 | 2.11 | 0.00 | 0.15 | 0.41 | 0.00 | 0.00 | **2.67** |
| DIVERGENCE_CONTINUATION | kept | 89 | 69.27 | 0.00 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.38** |
| FAILED_AUCTION_RECLAIM | filtered | 58 | 50.32 | 0.00 | 0.00 | 1.10 | 0.00 | 1.16 | 0.00 | 0.00 | 0.00 | **2.26** |
| FAILED_AUCTION_RECLAIM | kept | 11 | 65.25 | 0.00 | 0.00 | 4.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.51** |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 43.36 | 0.00 | 0.00 | 3.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.73** |
| LIQUIDATION_REVERSAL | filtered | 20 | 43.75 | 0.00 | 0.00 | 0.24 | 0.00 | 6.84 | 0.00 | 0.00 | 0.00 | **7.08** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 76 | 50.52 | 0.00 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.51** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 31 | 69.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.00 | 0.00 | 0.00 | 6.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.40** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 71.15 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | 0.00 | 0.00 | 0.00 | **3.60** |
| MEAN_REVERT | filtered | 5 | 46.10 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MEAN_REVERT | kept | 3 | 70.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 286 | 54.54 | 0.58 | 0.00 | 1.51 | 0.00 | 4.23 | 0.56 | 0.00 | 0.39 | **7.27** |
| MOVER_AVWAP_SCALP | kept | 532 | 79.79 | 2.45 | 0.00 | 0.05 | 0.00 | 1.31 | 0.29 | 0.00 | 0.08 | **4.18** |
| MOVER_TREND_PULLBACK | filtered | 1062 | 55.01 | 0.36 | 0.00 | 2.47 | 0.00 | 0.57 | 0.27 | 0.00 | 0.00 | **3.67** |
| MOVER_TREND_PULLBACK | kept | 2732 | 76.07 | 0.04 | 0.00 | 0.21 | 0.00 | 0.13 | 0.18 | 0.00 | 0.00 | **0.56** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 12 | 56.30 | 0.00 | 0.00 | 4.80 | 0.00 | 4.70 | 0.00 | 0.00 | 0.00 | **9.50** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 76.00 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 57 | 49.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.96 | **3.96** |
| QUIET_COMPRESSION_BREAK | kept | 2 | 77.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 24 | 55.29 | 0.00 | 0.00 | 5.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.07** |
| SR_FLIP_RETEST | kept | 41 | 71.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 45 | 56.36 | 0.00 | 0.00 | 4.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.14** |
| TREND_PULLBACK_EMA | kept | 50 | 79.76 | 0.00 | 0.00 | 0.19 | 0.00 | 0.43 | 0.40 | 0.00 | 0.00 | **1.02** |
| VOLUME_SURGE_BREAKOUT | filtered | 12 | 43.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.75 | 0.00 | 0.00 | 4.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.40** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- _no classified suppressed candidates yet — candidates classify after their validity window (~1h) of real candles has accumulated_

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
_**`suppressed` here means POST-SCORING suppressions only.** `suppression_audit.feeds_edge_matrix` returns False for every pre-scoring reject — `setup_compat:*` and `execution:*` fire ahead of the scoring engine and would swamp the matrix with a differently-measured population (~38k/window against ~4.5k) that Layer C's emission floor reads LIVE.  Those candidates are measured **in the dark lane instead** (`/signals/dark-live`), and the two populations are therefore **disjoint** — every dark row carries a `setup_compat:*` or `execution:*` gate, and none of them can appear here.  A path can read positive on this table and negative in the dark feed with no contradiction, because they are not measuring the same candidates.  Stated on the surface rather than in a docstring because reading one as a check on the other is a mistake this repo has now made (2026-08-04)._
_**Every cell is a 50-outcome ring** (`STRATEGY_EDGE_WINDOW`), so `n` is `min(seen, 50)` and `seen` is the denominator: a saturated cell is a rolling most-recent-50 window while a sparse cell beside it is all-time.  `sampled` counts cells that have evicted at least once._
- Outcomes recorded: **166383 held of 661788 seen** across 21 strategies; 3752 cells past the sample floor; **1962 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46607 | 715/45892/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | LONDON/DISTRIBUTION/NORMAL/BTC_RISING (-1.29R) |
| MOVER_AVWAP_SCALP | 21621 | 203/21418/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12410 | 151/12259/0 | 48% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12279 | 145/12134/0 | 39% | -0.26 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 10528 | 49/10479/0 | 40% | -0.24 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9166 | 108/9058/0 | 35% | -0.46 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7721 | 0/0/7721 | 42% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.59R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.22R) |
| SHADOW_RANGE_FADE | 7260 | 0/0/7260 | 36% | -0.13 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.39R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| QUIET_COMPRESSION_BREAK | 7125 | 415/6710/0 | 50% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_FUNDING_FADE | 6518 | 0/0/6518 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 4796 | 18/4778/0 | 46% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4795 | 58/4737/0 | 37% | -0.34 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3660 | 2/3658/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3435 | 0/3435/0 | 31% | -0.35 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| RANGE_FADE | 1896 | 6/1890/0 | 33% | -0.52 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1528 | 0/0/1528 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 472 | 0/472/0 | 31% | -0.55 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 162 | 32/130/0 | 43% | -0.15 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 44 | 2/42/0 | 27% | -0.14 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 300 | 27% / -0.58R | 300 | 54% / -0.09R | +0.50 | **ATR** |
| LIQUIDATION_REVERSAL | 31 | 23% / -0.71R | 31 | 45% / -0.37R | +0.34 | **ATR** |
| TREND_PULLBACK_EMA | 935 | 38% / -0.35R | 935 | 51% / -0.07R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1425 | 43% / -0.36R | 1425 | 56% / -0.13R | +0.24 | **ATR** |
| RANGE_FADE | 97 | 32% / -0.36R | 97 | 39% / -0.22R | +0.14 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 180 | 35% / -0.21R | 180 | 46% / -0.07R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 2163 | 44% / -0.19R | 2163 | 50% / -0.06R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 448 | 43% / -0.30R | 448 | 47% / -0.17R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8334 | 49% / -0.11R | 8334 | 54% / -0.01R | +0.10 | **ATR** |
| MA_CROSS_TREND_SHIFT | 49 | 41% / -0.17R | 49 | 45% / -0.07R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1253 | 41% / -0.22R | 1253 | 43% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1408 | 48% / -0.11R | 1408 | 54% / -0.04R | +0.06 | **ATR** |
| MEAN_REVERT | 348 | 46% / -0.20R | 348 | 44% / -0.22R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1254 | 47% / -0.13R | 1254 | 47% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 10 | 50% / -0.22R | 10 | 50% / -0.17R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11237 | 28% | -0.21R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2163 | 48% | -0.06R | 229 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 114 | 47% | -0.07R | 66 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1629 | 39% / -0.16R | +0.84 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1238 | 34% / -0.23R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2679 | 35% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10228 | 37% / -0.14R | +0.39 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1633 | 38% / -0.10R | +0.18 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1217 | 37% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1051 | 32% / -0.23R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 260 | 31% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 396 | 33% / -0.10R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 294 | 47% / -0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 73 | 40% / -0.08R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 411 | 33% / -0.30R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 78 | 29% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 38 | 45% / -0.30R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 18 | 44% / +0.72R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) (sustained 6 cycles)
- **ALERT** `dark_resolution` — 38 of 179 open dark rows are not being advanced (worst: CELOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 384/120) (sustained 384 cycles)
- **ALERT** `edge_reconciliation` — LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.51R (bound 0.3) (streak 733/6) (sustained 733 cycles)
- **ALERT** `tuned_variants` — 975 non-stamps — atr_arm_uncomputable=975 (seen=16331 stamped=2334 skipped=13022) (streak 733/6) (sustained 733 cycles)
- **ALERT** `auto_dispatch` — 180 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=180) (streak 726/3) (sustained 726 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 47 fed / 0 quiet / 0 never delivered of 47 subscribed; 246011077 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 9 arms current, none stalled; covering 2168/2168 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 19 arms current, none stalled; covering 1204/1204 signals (100%) | 0 |
| auto_dispatch | violating | 180 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=180) (streak 726/3) | 726 |
| binance_ip_weight | ok | peak 361/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 78590.10 | 0 |
| candle_coverage | ok | 132/132 symbols with ≥20 15m candles, 128/132 updated within 45m [stale=4, fresh=128; 73 Tier-1 futures + 61 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 5955 dup bars, 0 undedupable; ws 0 out-of-order, 913 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +20 / upstream +17 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2324/2343 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 38 of 179 open dark rows are not being advanced (worst: CELOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 384/120) | 384 |
| dark_sar_arms | ok | no open arms; covering 2317/2336 signals (99%) | 0 |
| depth_feed | ok | 47/47 books fresh (stale 0, never 0, thin 0); 61271481 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | LIQUIDITY_SWEEP_REVERSAL realized−counterfactual=+0.51R (bound 0.3) (streak 733/6) | 733 |
| emission_controller | ok | last cycle 438s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=301, MOVER_AVWAP_SCALP=381, MOVER_TREND_PULLBACK=5215, RANGE_FADE=3, TREND_PULLBACK_EMA=100), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) | 6 |
| firestore_read_budget | ok | 1,337 reads/day of 50,000 [engine 1,307, signing 30]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5640 sealed bars over 47 symbols; 2330 incomplete, 10 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +385 | 0 |
| indicator_cache_key | ok | 298900 frozen value(s) avoided; 814434 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.35R over n=4737 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +385 but output +0 (streak 4/72) | 4 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 61 held, 61 with scan counts, 61 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 2 locked / 2 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2081 rows held, 3205251 evicted (sampled: execution:trigger_not_confirmed 281/1129728, execution:overextended 281/1008341, setup_compat:regime_STRONG_TREND 281/542763) | 0 |
| price_action_lane | ok | 1033868 evaluated, 2068 emitted; layer1 2068 stamped / 0 blind; cooldown=127982, delta_opposed=117675, no_footprint=391342, no_opposing_target=1174, no_sweep=283673, rr_below_floor=109954 | 0 |
| promoted_pair_integrity | ok | 61/61 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.52R over n=1890 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +385 but output +0 (streak 35/72) | 35 |
| sar_alignment_crosscheck | ok | 1127/45334 disagreed (2.5%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +385 | 0 |
| sar_hold_arm | ok | 1872 held arms settled, 128 unscored, 18 still walking (13 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/47 unfetchable (9%); top cause: located bar does not contain the stamp; symbols: AINUSDT, BTWUSDT, CHIPUSDT, MAGMAUSDT | 0 |
| sar_live_arms | ok | 18 arms current, none stalled; covering 1202/1202 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 447 records await one (43 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 35.01s, worst 281.8s over 16051 lifetime cycles; lifetime 1049 over 60s, 332 over 120s; recent 2/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.87s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 459798 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 4s ago (10.79s to run, worst 209.82s), 3197 overrun(s) of 14380 cycles, TTL 900s; slowest signals=6.57s, tickers=2.13s, engine_state=1.11s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=7563, gate reads=0, withheld=7563) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +34 / upstream +385 | 0 |
| structural_snap | ok | 6000/6000 measured, 37 blind, 0 levels moved (refusals: redetect_cooldown=3907) | 0 |
| structural_veto_lane | ok | 5913 stamped; 0 with no readable level book, 43 with clear air ahead, 4751 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +385 / upstream +17 | 0 |
| tuned_variants | violating | 975 non-stamps — atr_arm_uncomputable=975 (seen=16331 stamped=2334 skipped=13022) (streak 733/6) | 733 |
| unlock_shorts | ok | 12 open, 46 scheduled, calendar 17.9h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 141 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1156870`
- `Path funnel` emissions: `24`
- `Regime distribution` emissions: `24`
- `QUIET_SCALP_BLOCK` events: `122`
- `confidence_gate` events: `5247`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **148**
- Total REST-fallback activations: **10**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 15 | 18741 | 35764 | 57743 | 0 |
| futures_aggtrade | 100 | 9897 | 46721 | 56007 | 0 |
| futures_depth | 3 | 16013 | 16013 | 57802 | 0 |
| futures_mover | 30 | 8227 | 21201 | 37670 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 10 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=180013] state[populated=180013] buckets[many=180013] sources[none] quality[none]
- funding_rate: presence[absent=23880, present=156133] state[empty=23880, populated=156133] buckets[few=156133, none=23880] sources[none] quality[none]
- liquidation_clusters: presence[absent=98791, present=81222] state[empty=98791, populated=81222] buckets[few=62171, none=98791, some=19051] sources[none] quality[none]
- oi_snapshot: presence[absent=23880, present=156133] state[empty=23880, populated=156133] buckets[few=163, many=155147, none=23880, some=823] sources[none] quality[none]
- order_book: presence[absent=78585, present=101428] state[populated=101428, unavailable=78585] buckets[few=101428, none=78585] sources[book_ticker=101428, unavailable=78585] quality[none=78585, top_of_book_only=101428]
- orderblocks: presence[absent=180013] state[empty=180013] buckets[none=180013] sources[measured_dark=180013] quality[none]
- recent_ticks: presence[present=180013] state[populated=180013] buckets[many=180013] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.338767051696777` sec
- Median create→first breach: `2909.0446190834045` sec
- Median create→terminal: `2909.0446450710297` sec
- Median first breach→terminal: `6.103515625e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.3}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 6 | 6 | 1.0728040965210106 | 2.0811576640571574 | 0.7573417823850339 | 0 | 6 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.3507193460490385 | 1.5652916957974043 | 0.8629186174535626 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 4.568122913806818 | 3.0 | 1.522707637935606 | 1 | 0 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.617499733560698 | 2.978399999999998 | 1.1050577010642082 | 2 | 1 |
| MOVER_TREND_PULLBACK | 27 | 27 | 3.208197599483088 | 3.0 | 1.0900224161778038 | 22 | 4 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.8 | 0.7999999999999997 | 0.999999908097898 | 0 | 1 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.6502493816957284 | 2.037105195583325 | 0.8308761478351196 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 6 | 6 | 0.0 | 33.3 | 0.0 | 0.0 | 0.6462 | 4887.345064997673 | 4887.589451551437 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5365.718384027481 | 5365.718407154083 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2659.449313879013 | 2659.449364900589 |
| MOVER_AVWAP_SCALP | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 0.5135 | 5877.448091030121 | 5877.4481410980225 |
| MOVER_TREND_PULLBACK | 27 | 27 | 25.9 | 33.3 | 25.9 | 0.0 | 0.4098 | 2793.61376285553 | 2794.1997389793396 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.5061 | 48808.57674407959 | 48808.57676696777 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.4699 | 8208.779059886932 | 8208.779275894165 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 361 | 5 | 229 | 0.0 | 0.0 | None | None | 132 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 503 | 18 | 341 | 0.0 | 50.0 | 8208.779059886932 | 8208.779275894165 | 162 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `198`
- Gating Δ: `-6898`
- No-generation Δ: `-226008`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.4046, "current_avg_pnl": 0.6462, "current_win_rate": 0.0, "previous_avg_pnl": 1.0508, "previous_win_rate": 100.0, "win_rate_delta": -100.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1765, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": 0.1765, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MEAN_REVERT": {"avg_pnl_delta": -0.0503, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.0503, "previous_win_rate": 25.0, "win_rate_delta": -25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.0875, "current_avg_pnl": 0.5135, "current_win_rate": 33.3, "previous_avg_pnl": -0.574, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.3378, "current_avg_pnl": 0.4098, "current_win_rate": 25.9, "previous_avg_pnl": -0.928, "previous_win_rate": 28.1, "win_rate_delta": -2.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.933, "current_avg_pnl": -0.5061, "current_win_rate": 0.0, "previous_avg_pnl": 0.4269, "previous_win_rate": 35.7, "win_rate_delta": -35.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -118, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -20, "geometry_changed_delta": 0, "geometry_preserved_delta": -129, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 6485.78, "median_terminal_delta_sec": 6485.78, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
