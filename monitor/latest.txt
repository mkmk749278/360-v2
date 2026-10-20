# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `3044` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 445 | 445 | 445 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 21882 | 21882 | 20804 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 111431 | 111388 | 74 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 104980 | 104980 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 104391 | 99628 | 5329 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 105025 | 103657 | 1459 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 107616 | 107481 | 168 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 95483 | 95507 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 105127 | 105161 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 105178 | 102075 | 4383 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 116483 | 122332 | 1562 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 111463 | 104124 | 12297 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 106811 | 106811 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 104991 | 104985 | 35 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 104346 | 104042 | 340 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 106472 | 104570 | 2570 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 103507 | 103951 | 346 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 92117 | 86975 | 5436 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 92417 | 91650 | 894 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 111392 | 111351 | 76 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 95512 | 95535 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5918 | 5918 | 5583 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1099 | 1099 | 777 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 28823 | 28823 | 28107 | 10 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 21 | 21 | 17 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13926 | 13926 | 11782 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4398 | 4398 | 3753 | 26 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 42139 | 42139 | 35542 | 109 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 155 | 155 | 155 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2263 | 2263 | 2141 | 20 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 6698 | 6698 | 6443 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1643 | 1643 | 1228 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4317 | 4317 | 4126 | 13 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 365 | 365 | 271 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=111388): breakout_not_found=66268, basic_filters_failed=24841, move_not_fresh=12732, breakout_stale=6667, retest_proximity_failed=618, volume_spike_missing=258, move_exhausted=2, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=104980): cls_disabled_merged_into_lsr=104980
- **EVAL::DIVERGENCE_CONTINUATION** (total=99628): cvd_divergence_failed=43375, h1_trend_not_aligned=28805, basic_filters_failed=18644, ema_alignment_reject=7471, retest_proximity_failed=846, missing_fvg_or_orderblock=375, missing_cvd=112
- **EVAL::FAILED_AUCTION_RECLAIM** (total=103657): auction_not_detected=71142, basic_filters_failed=17910, reclaim_hold_failed=6761, tail_too_small=4947, regime_blocked=2853, rsi_reject=44
- **EVAL::FUNDING_EXTREME** (total=107481): funding_not_extreme=81294, basic_filters_failed=19701, missing_funding_rate=3995, ema_alignment_reject=1576, rsi_reject=690, momentum_reject=124, cvd_divergence_failed=91, missing_fvg_or_orderblock=10
- **EVAL::LIQUIDATION_REVERSAL** (total=95507): cascade_threshold_not_met=74911, basic_filters_failed=19918, rsi_reject=369, cvd_divergence_failed=283, missing_cvd=16, missing_fvg_or_orderblock=9, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=105161): no_ma_cross=82736, basic_filters_failed=18656, ma_cross_cooldown=2193, ma_cross_htf_misaligned=1576
- **EVAL::MEAN_REVERT** (total=102075): no_extension=89824, basic_filters_failed=12251
- **EVAL::MOVER_AVWAP_SCALP** (total=122332): no_avwap_tag=48006, no_mover_leg=33914, basic_filters_failed=25020, avwap_slope_against=9643, avwap_reclaim_no_volume=3306, no_avwap_reclaim=2313, anchor_too_recent=130
- **EVAL::MOVER_TREND_PULLBACK** (total=104124): mover_run_too_small=64037, basic_filters_failed=24938, no_reclaim=12943, no_pullback_tag=2206
- **EVAL::OPENING_RANGE_BREAKOUT** (total=106811): feature_disabled=106811
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=104985): regime_blocked=58195, breakout_not_found=36361, adx_reject=5977, basic_filters_failed=4380, ema_alignment_reject=72
- **EVAL::QUIET_COMPRESSION_BREAK** (total=104042): regime_blocked=49421, compression_not_detected=33769, basic_filters_failed=13520, breakout_not_detected=6725, volume_confirmation_failed=596, missing_fvg_or_orderblock=8, rsi_reject=3
- **EVAL::RANGE_FADE** (total=104570): no_range_edge=92317, basic_filters_failed=12253
- **EVAL::SR_FLIP_RETEST** (total=103951): flip_close_not_confirmed=71711, basic_filters_failed=17885, long_break_volume_thin=4191, retest_out_of_zone=3018, regime_blocked=2845, h1_break_not_confirmed=1967, reclaim_hold_failed=1311, long_acceptance_not_held=512, ema_alignment_reject=359, wick_quality_failed=116, missing_fvg_or_orderblock=33, whipsaw_flip=3
- **EVAL::STANDARD** (total=86975): momentum_reject=29209, adx_reject=24023, sweeps_not_detected=9637, basic_filters_failed=8608, ema_alignment_reject=8347, macd_reject=6314, htf_poi_unanchored=605, rsi_reject=178, invalid_sl_geometry=51, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=91650): h1_trend_not_aligned=31864, ema_alignment_reject=14910, h1_pullback_not_confirmed=12016, basic_filters_failed=9126, no_ema_reclaim_close=7193, ema_not_tested_prev=6552, body_conviction_fail=3963, rsi_reject=2708, prev_already_below_emas=1191, prev_already_above_emas=798, no_prev_low_break=584, no_prev_high_break=340, momentum_flat=236, ema21_not_tagged=91, missing_fvg_or_orderblock=50, momentum_reject=28
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=111351): breakout_not_found=64841, basic_filters_failed=24840, move_not_fresh=14206, breakout_stale=5302, retest_proximity_failed=1575, volume_spike_missing=542, missing_fvg_or_orderblock=40, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=95535): momentum_reject=65089, recent_ticks_insufficient=23197, basic_filters_failed=7249

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=32): execution:overextended=32
- **DIVERGENCE_CONTINUATION** (total=199): setup_compat:regime_VOLATILE_UNSUITABLE=188, setup_compat:regime_BREAKOUT_EXPANSION=11
- **FAILED_AUCTION_RECLAIM** (total=1637): setup_compat:regime_STRONG_TREND=700, execution:overextended=696, context_floor=241
- **FUNDING_EXTREME_SIGNAL** (total=1049): execution:trigger_not_confirmed=1011, context_floor=38
- **LIQUIDATION_REVERSAL** (total=11): execution:trigger_not_confirmed=11
- **LIQUIDITY_SWEEP_REVERSAL** (total=6736): execution:trigger_not_confirmed=2791, setup_compat:regime_STRONG_TREND=2100, execution:overextended=1845
- **MA_CROSS_TREND_SHIFT** (total=11): setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_CLEAN_RANGE=3, execution:overextended=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=11568): setup_compat:regime_WEAK_TREND=7391, setup_compat:regime_STRONG_TREND=3048, execution:overextended=1127, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=1953): execution:overextended=1243, execution:trigger_not_confirmed=627, entry_quality=83
- **MOVER_TREND_PULLBACK** (total=14888): execution:trigger_not_confirmed=8843, execution:overextended=5162, entry_quality=883
- **QUIET_COMPRESSION_BREAK** (total=2): execution:overextended=2
- **RANGE_FADE** (total=4918): setup_compat:regime_WEAK_TREND=2617, setup_compat:regime_STRONG_TREND=1593, setup_compat:regime_VOLATILE_UNSUITABLE=377, execution:overextended=300, context_edge=29, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=3618): setup_compat:regime_CLEAN_RANGE=2697, setup_compat:regime_DIRTY_RANGE=761, setup_compat:regime_VOLATILE_UNSUITABLE=98, entry_quality=62
- **VOLUME_SURGE_BREAKOUT** (total=3): execution:overextended=3

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 230055 | 33.6% |
| QUIET | 177416 | 25.9% |
| TRENDING_UP | 129701 | 18.9% |
| TRENDING_DOWN | 119818 | 17.5% |
| VOLATILE | 28715 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **52**
- Average confidence gap to threshold: **11.83** (samples=52) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ERAUSDT=24, STRKUSDT=7, INJUSDT=6, SOLUSDT=4, APTUSDT=3, XMRUSDT=3, SANDUSDT=3, FILUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 225 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 63 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 5 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 14 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 105 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 145 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 67 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 26 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 89 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 148 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1240 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 27 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1808 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 8 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 87 |
| SR_FLIP_RETEST | filtered | min_confidence | 17 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 9 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 33 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 55 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 85 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 225 | 54.01 | 64.43 | 10.42 | 19.61 | 19.86 | 16.35 | 4.02 | 14.33 |
| DIVERGENCE_CONTINUATION | kept | 63 | 70.60 | 65.00 | -5.60 | 20.21 | 19.97 | 17.33 | 4.76 | 3.76 |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 55.96 | 60.20 | 4.24 | 20.76 | 16.08 | 20.00 | 5.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.15 | 65.00 | -2.15 | 22.05 | 19.60 | 20.00 | 5.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 44.08 | 61.50 | 17.42 | 19.53 | 14.00 | 17.55 | 3.00 | 6.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 109 | 55.00 | 64.96 | 9.96 | 20.53 | 18.46 | 18.38 | 1.99 | 2.57 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 145 | 72.46 | 65.00 | -7.46 | 23.10 | 19.78 | 18.07 | 2.94 | 0.12 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 60.70 | 61.00 | 0.30 | 20.40 | 20.00 | 15.80 | 0.00 | 16.60 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 71.00 | 65.00 | -6.00 | 20.30 | 19.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 69 | 56.63 | 64.30 | 7.67 | 20.41 | 15.43 | 14.59 | 0.00 | 11.51 |
| MEAN_REVERT | kept | 26 | 73.06 | 65.00 | -8.06 | 20.68 | 14.82 | 15.37 | 0.00 | 4.43 |
| MOVER_AVWAP_SCALP | filtered | 89 | 59.14 | 65.00 | 5.86 | 19.85 | 15.11 | 15.80 | 4.67 | 15.99 |
| MOVER_AVWAP_SCALP | kept | 148 | 75.98 | 65.00 | -10.98 | 20.02 | 15.81 | 15.80 | 4.58 | 5.62 |
| MOVER_TREND_PULLBACK | filtered | 1267 | 57.47 | 63.85 | 6.38 | 19.80 | 18.68 | 15.80 | 3.78 | 16.58 |
| MOVER_TREND_PULLBACK | kept | 1808 | 78.03 | 65.00 | -13.03 | 19.82 | 18.53 | 15.80 | 4.53 | 2.16 |
| QUIET_COMPRESSION_BREAK | filtered | 35 | 56.64 | 65.00 | 8.36 | 19.93 | 18.23 | 20.00 | 0.00 | 16.32 |
| QUIET_COMPRESSION_BREAK | kept | 87 | 75.29 | 65.00 | -10.29 | 21.35 | 19.45 | 20.00 | 0.00 | -1.51 |
| SR_FLIP_RETEST | filtered | 26 | 48.93 | 63.31 | 14.38 | 19.83 | 20.00 | 17.18 | 2.54 | 12.34 |
| SR_FLIP_RETEST | kept | 33 | 75.12 | 65.00 | -10.12 | 19.84 | 20.00 | 15.34 | 2.14 | 2.30 |
| TREND_PULLBACK_EMA | kept | 55 | 76.23 | 65.00 | -11.23 | 20.55 | 19.82 | 18.61 | 5.24 | 0.35 |
| VOLUME_SURGE_BREAKOUT | filtered | 85 | 58.27 | 65.00 | 6.73 | 20.86 | 19.74 | 20.00 | 4.57 | 22.22 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.20 | 65.00 | -0.20 | 18.50 | 15.00 | 20.00 | 5.50 | 20.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 225 | 54.01 | 19.42 | 14.71 | 3.56 | 13.77 | 5.38 | 7.48 | 4.02 |
| DIVERGENCE_CONTINUATION | kept | 63 | 70.60 | 21.32 | 15.30 | 5.62 | 13.16 | 5.13 | 9.16 | 4.76 |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 55.96 | 25.00 | 18.00 | 3.00 | 12.00 | 5.00 | 2.96 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.15 | 25.00 | 16.00 | 7.50 | 10.50 | 5.00 | 5.65 | 5.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 44.08 | 24.00 | 9.50 | 3.38 | 12.00 | 8.75 | 4.95 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 109 | 55.00 | 21.79 | 15.58 | 6.55 | 13.44 | 6.21 | 4.67 | 1.99 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 145 | 72.46 | 24.52 | 14.06 | 6.56 | 12.14 | 6.33 | 6.04 | 2.94 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 60.70 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 7.30 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 71.00 | 17.00 | 14.00 | 3.00 | 17.00 | 10.00 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 69 | 56.63 | 17.58 | 17.59 | 8.61 | 13.00 | 5.00 | 6.37 | 0.00 |
| MEAN_REVERT | kept | 26 | 73.06 | 23.46 | 14.15 | 14.31 | 13.00 | 5.00 | 7.57 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 89 | 59.14 | 16.66 | 18.00 | 10.37 | 13.39 | 6.20 | 7.19 | 4.67 |
| MOVER_AVWAP_SCALP | kept | 148 | 75.98 | 20.92 | 18.01 | 11.43 | 12.82 | 6.82 | 7.13 | 4.58 |
| MOVER_TREND_PULLBACK | filtered | 1267 | 57.47 | 18.02 | 18.07 | 7.75 | 13.16 | 5.79 | 8.48 | 3.78 |
| MOVER_TREND_PULLBACK | kept | 1808 | 78.03 | 19.14 | 18.19 | 8.52 | 14.09 | 6.75 | 9.01 | 4.53 |
| QUIET_COMPRESSION_BREAK | filtered | 35 | 56.64 | 17.23 | 14.91 | 11.66 | 14.00 | 7.70 | 7.46 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 87 | 75.29 | 19.11 | 17.40 | 11.93 | 14.10 | 6.61 | 6.74 | 0.00 |
| SR_FLIP_RETEST | filtered | 26 | 48.93 | 25.00 | 14.54 | 3.69 | 14.69 | 5.40 | 4.05 | 2.54 |
| SR_FLIP_RETEST | kept | 33 | 75.12 | 23.06 | 18.00 | 4.73 | 13.55 | 7.70 | 8.71 | 2.14 |
| TREND_PULLBACK_EMA | kept | 55 | 76.23 | 18.05 | 18.00 | 7.53 | 14.22 | 5.41 | 8.30 | 5.24 |
| VOLUME_SURGE_BREAKOUT | filtered | 85 | 58.27 | 21.33 | 18.00 | 12.00 | 14.00 | 5.00 | 5.60 | 4.57 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.20 | 25.00 | 14.00 | 15.00 | 14.00 | 5.00 | 6.70 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 225 | 54.01 | 0.00 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.11** |
| DIVERGENCE_CONTINUATION | kept | 63 | 70.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 55.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 44.08 | 0.00 | 0.00 | 1.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.50** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 109 | 55.00 | 0.00 | 0.00 | 0.22 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | **0.55** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 145 | 72.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.08** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 60.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 71.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 69 | 56.63 | 0.00 | 0.00 | 0.00 | 0.00 | 11.06 | 0.00 | 0.00 | 0.00 | **11.06** |
| MEAN_REVERT | kept | 26 | 73.06 | 0.00 | 0.00 | 4.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.43** |
| MOVER_AVWAP_SCALP | filtered | 89 | 59.14 | 0.00 | 0.00 | 2.95 | 0.00 | 2.86 | 0.00 | 0.00 | 0.04 | **5.85** |
| MOVER_AVWAP_SCALP | kept | 148 | 75.98 | 0.00 | 0.00 | 0.26 | 0.00 | 3.68 | 0.00 | 0.00 | 0.75 | **4.69** |
| MOVER_TREND_PULLBACK | filtered | 1267 | 57.47 | 0.21 | 0.00 | 1.66 | 0.00 | 0.87 | 0.00 | 0.00 | 0.04 | **2.78** |
| MOVER_TREND_PULLBACK | kept | 1808 | 78.03 | 0.00 | 0.00 | 1.72 | 0.00 | 0.35 | 0.00 | 0.00 | 0.00 | **2.07** |
| QUIET_COMPRESSION_BREAK | filtered | 35 | 56.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.49 | 0.00 | 0.00 | 0.00 | **0.49** |
| QUIET_COMPRESSION_BREAK | kept | 87 | 75.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | **0.25** |
| SR_FLIP_RETEST | filtered | 26 | 48.93 | 0.00 | 0.00 | 1.66 | 0.00 | 2.49 | 0.00 | 0.00 | 2.49 | **6.64** |
| SR_FLIP_RETEST | kept | 33 | 75.12 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.48** |
| TREND_PULLBACK_EMA | kept | 55 | 76.23 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.26** |
| VOLUME_SURGE_BREAKOUT | filtered | 85 | 58.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **151493 held of 558515 seen** across 21 strategies; 3441 cells past the sample floor; **1764 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44714 | 663/44051/0 | 43% | -0.18 | LONDON/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (+1.20R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.28R) |
| MOVER_AVWAP_SCALP | 19559 | 193/19366/0 | 42% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11606 | 125/11481/0 | 37% | -0.28 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10806 | 105/10701/0 | 48% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9099 | 41/9058/0 | 41% | -0.20 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 8090 | 83/8007/0 | 35% | -0.49 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7288 | 0/0/7288 | 42% | -0.11 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.48R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.07R) |
| SHADOW_RANGE_FADE | 6683 | 0/0/6683 | 36% | -0.13 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.60R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.20R) |
| QUIET_COMPRESSION_BREAK | 6254 | 407/5847/0 | 49% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5779 | 0/0/5779 | 35% | -0.40 | NY/RANGE/EXPANDED/BTC_FALLING (-0.01R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 4085 | 46/4039/0 | 39% | -0.28 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/MARKDOWN/CASCADE/BTC_NEUTRAL (-1.32R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| SR_FLIP_RETEST | 3754 | 15/3739/0 | 45% | -0.29 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 3102 | 0/3102/0 | 31% | -0.34 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 3018 | 2/3016/0 | 31% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| RANGE_FADE | 1440 | 4/1436/0 | 35% | -0.40 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1348 | 0/0/1348 | 54% | -0.04 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.32R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.40R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 362 | 0/362/0 | 31% | -0.58 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 128 | 26/102/0 | 44% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 227 | 27% / -0.58R | 227 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 20 | 30% / -0.54R | 20 | 55% / -0.24R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 771 | 40% / -0.30R | 771 | 53% / -0.06R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1282 | 44% / -0.34R | 1282 | 56% / -0.13R | +0.21 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 154 | 34% / -0.23R | 154 | 45% / -0.08R | +0.16 | **ATR** |
| RANGE_FADE | 72 | 29% / -0.46R | 72 | 36% / -0.31R | +0.15 | **ATR** |
| MA_CROSS_TREND_SHIFT | 40 | 40% / -0.22R | 40 | 42% / -0.10R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1871 | 43% / -0.19R | 1871 | 49% / -0.07R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 327 | 44% / -0.28R | 327 | 47% / -0.17R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1112 | 40% / -0.25R | 1112 | 42% / -0.14R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 7556 | 49% / -0.12R | 7556 | 54% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1173 | 49% / -0.09R | 1173 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1043 | 47% / -0.15R | 1043 | 47% / -0.15R | -0.00 | **FIXED** |
| MEAN_REVERT | 287 | 49% / -0.13R | 287 | 48% / -0.13R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10431 | 28% | -0.25R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1871 | 46% | -0.07R | 218 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 97 | 46% | -0.08R | 60 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1036 | 35% / -0.22R | +0.85 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1389 | 40% / -0.16R | +0.85 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2335 | 35% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9440 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1337 | 37% / -0.09R | +0.19 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1020 | 33% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 919 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 227 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 293 | 32% / -0.52R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 240 | 50% / -0.02R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 55 | 35% / -0.14R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 310 | 34% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 61 | 28% / -0.38R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 26 | 42% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×545]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 408/6) (sustained 408 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 30/6) (sustained 30 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 427/6) (sustained 427 cycles)
- **ALERT** `tuned_variants` — 341 non-stamps — atr_arm_uncomputable=341 (seen=8287 stamped=488 skipped=7458) (streak 427/6) (sustained 427 cycles)
- **ALERT** `auto_dispatch` — 54 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=54) (streak 387/3) (sustained 387 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 169165307 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 15 arms current, none stalled; covering 1733/1733 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 30 arms current, none stalled; covering 1081/1081 signals (100%) | 0 |
| auto_dispatch | violating | 54 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=54) (streak 387/3) | 387 |
| binance_ip_weight | ok | peak 128/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82061.40 | 0 |
| candle_coverage | ok | 79/79 symbols with ≥20 15m candles, 79/79 updated within 45m [fresh=79; 75 Tier-1 futures + 5 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1498 dup bars, 0 undedupable; ws 0 out-of-order, 337 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 57 cohorts, 35 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +9 / upstream +21 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1466/1484 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 1 of 105 open dark rows are not being advanced (worst: WLFIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 2/120) | 2 |
| dark_sar_arms | ok | no open arms; covering 1453/1471 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 35567681 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 427/6) | 427 |
| emission_controller | ok | last cycle 1057s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×545]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 408/6) | 408 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 30/6) | 30 |
| firestore_read_budget | ok | 1,351 reads/day of 50,000 [engine 1,316, signing 35]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1310 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +125 | 0 |
| indicator_cache_key | ok | 144880 frozen value(s) avoided; 780590 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.29R over n=4039 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +125 but output +0 (streak 5/72) | 5 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 5 held, 5 with scan counts, 4 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3125 rows held, 2967401 evicted (sampled: execution:trigger_not_confirmed 400/1052326, execution:overextended 400/932410, setup_compat:regime_STRONG_TREND 400/500943) | 0 |
| price_action_lane | ok | 1485154 evaluated, 1147 emitted; layer1 1147 stamped / 0 blind; cooldown=222872, delta_opposed=135223, no_footprint=500813, no_opposing_target=1633, no_sweep=498341, rr_below_floor=125125 | 0 |
| promoted_pair_integrity | ok | 5/5 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.41R over n=1436 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +7 / upstream +125 | 0 |
| sar_alignment_crosscheck | ok | 512/13338 disagreed (3.8%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +125 | 0 |
| sar_hold_arm | ok | 1891 held arms settled, 109 unscored, 30 still walking (27 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/13 unfetchable (15%); top cause: located bar does not contain the stamp; symbols: LSKUSDT, ZROUSDT | 0 |
| sar_live_arms | ok | 30 arms current, none stalled; covering 1081/1081 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 413 records await one (11 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 5/12) | 5 |
| scan_cycle | ok | last 11.96s, worst 153.02s over 18331 lifetime cycles; lifetime 53 over 60s, 2 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.74s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 618443 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 44s ago (11.41s to run, worst 120.44s), 509 overrun(s) of 9126 cycles, TTL 900s; slowest trail_governor=10.59s, data_intake=8.22s, dark_promotion=7.76s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +1 / upstream +125 | 0 |
| structural_snap | ok | 6000/6000 measured, 23 blind, 0 levels moved (refusals: redetect_cooldown=946) | 0 |
| structural_veto_lane | ok | 1363 stamped; 0 with no readable level book, 70 with clear air ahead, 833 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +125 / upstream +21 | 0 |
| tuned_variants | violating | 341 non-stamps — atr_arm_uncomputable=341 (seen=8287 stamped=488 skipped=7458) (streak 427/6) | 427 |
| unlock_shorts | ok | 16 open, 41 scheduled, calendar 17.4h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 6 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2969466`
- `Path funnel` emissions: `88`
- `Regime distribution` emissions: `88`
- `QUIET_SCALP_BLOCK` events: `52`
- `confidence_gate` events: `4296`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **24**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 1835 | 1835 | 10367 | 0 |
| futures_depth | 3 | 5475 | 5475 | 11547 | 0 |
| futures_liq | 18 | 3613 | 9515 | 14710 | 0 |
| futures_mover | 1 | 10868 | 10868 | 10868 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=367, present=568315] state[empty=367, populated=568315] buckets[many=568315, none=367] sources[none] quality[none]
- funding_rate: presence[absent=42343, present=526339] state[empty=42343, populated=526339] buckets[few=526339, none=42343] sources[none] quality[none]
- liquidation_clusters: presence[absent=345647, present=223035] state[empty=345647, populated=223035] buckets[few=189247, none=345647, some=33788] sources[none] quality[none]
- oi_snapshot: presence[absent=42343, present=526339] state[empty=42343, populated=526339] buckets[few=64, many=525931, none=42343, some=344] sources[none] quality[none]
- order_book: presence[absent=149936, present=418746] state[populated=418746, unavailable=149936] buckets[few=418746, none=149936] sources[book_ticker=418746, unavailable=149936] quality[none=149936, top_of_book_only=418746]
- orderblocks: presence[absent=568682] state[empty=568682] buckets[none=568682] sources[measured_dark=568682] quality[none]
- recent_ticks: presence[present=568682] state[populated=568682] buckets[many=568682] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.788115978240967` sec
- Median create→first breach: `6472.196089982986` sec
- Median create→terminal: `6472.196166038513` sec
- Median first breach→terminal: `6.699562072753906e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.0752416989323004 | 1.1702038419595677 | 0.9188499134746915 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.4820114785771836 | 3.0 | 0.4940038261923945 | 0 | 1 |
| MOVER_AVWAP_SCALP | 7 | 7 | 1.7433990517363072 | 1.7466310741548599 | 0.8184142361232848 | 1 | 6 |
| MOVER_TREND_PULLBACK | 15 | 15 | 2.6775373111041803 | 2.988899999999992 | 0.8958269969233454 | 7 | 8 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.1319399187370898 | 1.3079154702081797 | 0.9172525873645045 | 0 | 5 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0752 | 3661.856670856476 | 3661.8567309379578 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.815 | 1255.380036830902 | 1257.664274930954 |
| MOVER_AVWAP_SCALP | 7 | 7 | 14.3 | 57.1 | 14.3 | 0.0 | -0.7163 | 5692.735996961594 | 5692.736022949219 |
| MOVER_TREND_PULLBACK | 15 | 15 | 20.0 | 73.3 | 20.0 | 0.0 | -1.0856 | 5552.594769001007 | 5552.5949149131775 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 0.0 | 42.9 | 0.0 | 0.0 | -0.4607 | 21356.850790977478 | 21356.850808143616 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1643 | 7 | 1228 | 0.0 | 0.0 | None | None | 415 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4317 | 13 | 4126 | 0.0 | 0.0 | None | None | 191 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-92`
- Gating Δ: `-73271`
- No-generation Δ: `-600014`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.6163, "current_avg_pnl": -1.0752, "current_win_rate": 0.0, "previous_avg_pnl": -0.4589, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.8007, "current_avg_pnl": -0.7163, "current_win_rate": 14.3, "previous_avg_pnl": -1.517, "previous_win_rate": 0.0, "win_rate_delta": 14.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.3993, "current_avg_pnl": -1.0856, "current_win_rate": 20.0, "previous_avg_pnl": -0.6863, "previous_win_rate": 28.6, "win_rate_delta": -8.6}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1828, "current_avg_pnl": -0.4607, "current_win_rate": 0.0, "previous_avg_pnl": -0.2779, "previous_win_rate": 11.1, "win_rate_delta": -11.1}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -100, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -129, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
