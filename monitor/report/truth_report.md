# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `448` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 197 | 197 | 182 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9465 | 9465 | 9191 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 58630 | 58651 | 26 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 52705 | 52706 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 52192 | 50603 | 2085 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 52763 | 52177 | 651 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 54946 | 54940 | 43 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 47077 | 47102 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 52836 | 52881 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 52895 | 51502 | 2048 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 62363 | 66426 | 741 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 58681 | 54334 | 7974 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 54579 | 54580 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 52712 | 52747 | 6 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 52152 | 52085 | 97 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 53565 | 52637 | 1270 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 51748 | 51937 | 160 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 44456 | 41880 | 2825 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 44714 | 44438 | 382 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 58585 | 58603 | 15 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 47111 | 47086 | 70 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3166 | 3166 | 2842 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 240 | 240 | 185 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15065 | 15065 | 14944 | 12 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 3 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5685 | 5685 | 5037 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2001 | 2001 | 1278 | 49 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 25215 | 25215 | 20180 | 188 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 27 | 27 | 27 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 596 | 596 | 537 | 14 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3349 | 3349 | 3191 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 749 | 749 | 729 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2154 | 2154 | 2050 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 155 | 155 | 109 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 6819 | 6819 | 2008 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=58651): breakout_not_found=34219, basic_filters_failed=13321, move_not_fresh=7859, breakout_stale=2349, retest_proximity_failed=780, volume_spike_missing=120, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=52706): cls_disabled_merged_into_lsr=52706
- **EVAL::DIVERGENCE_CONTINUATION** (total=50603): cvd_divergence_failed=22239, h1_trend_not_aligned=13735, basic_filters_failed=10736, ema_alignment_reject=3337, retest_proximity_failed=358, missing_fvg_or_orderblock=198
- **EVAL::FAILED_AUCTION_RECLAIM** (total=52177): auction_not_detected=36278, basic_filters_failed=10654, reclaim_hold_failed=2452, tail_too_small=1953, regime_blocked=820, rsi_reject=20
- **EVAL::FUNDING_EXTREME** (total=54940): funding_not_extreme=42331, basic_filters_failed=11360, ema_alignment_reject=454, rsi_reject=350, missing_funding_rate=317, cvd_divergence_failed=78, momentum_reject=42, missing_fvg_or_orderblock=8
- **EVAL::LIQUIDATION_REVERSAL** (total=47102): cascade_threshold_not_met=35493, basic_filters_failed=11144, rsi_reject=241, cvd_divergence_failed=211, missing_fvg_or_orderblock=8, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=52881): no_ma_cross=41721, basic_filters_failed=10761, ma_cross_cooldown=227, ma_cross_htf_misaligned=172
- **EVAL::MEAN_REVERT** (total=51502): no_extension=43233, basic_filters_failed=8269
- **EVAL::MOVER_AVWAP_SCALP** (total=66426): no_avwap_tag=22314, no_mover_leg=20840, basic_filters_failed=13612, avwap_slope_against=6677, avwap_reclaim_no_volume=1614, no_avwap_reclaim=1199, anchor_too_recent=170
- **EVAL::MOVER_TREND_PULLBACK** (total=54334): mover_run_too_small=29631, basic_filters_failed=13465, no_reclaim=9587, no_pullback_tag=1651
- **EVAL::OPENING_RANGE_BREAKOUT** (total=54580): feature_disabled=54580
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=52747): regime_blocked=30992, breakout_not_found=16704, basic_filters_failed=3328, adx_reject=1669, ema_alignment_reject=54
- **EVAL::QUIET_COMPRESSION_BREAK** (total=52085): regime_blocked=22348, compression_not_detected=18437, basic_filters_failed=7306, breakout_not_detected=3764, volume_confirmation_failed=203, rsi_reject=26, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=52637): no_range_edge=44364, basic_filters_failed=8273
- **EVAL::SR_FLIP_RETEST** (total=51937): flip_close_not_confirmed=36337, basic_filters_failed=10617, long_break_volume_thin=1386, retest_out_of_zone=1276, h1_break_not_confirmed=985, regime_blocked=810, reclaim_hold_failed=334, long_acceptance_not_held=108, ema_alignment_reject=37, wick_quality_failed=24, whipsaw_flip=22, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=41880): momentum_reject=14824, basic_filters_failed=7005, adx_reject=6655, sweeps_not_detected=4744, ema_alignment_reject=3757, macd_reject=3669, htf_poi_unanchored=1107, rsi_reject=58, invalid_sl_geometry=47, mtf_reject=14
- **EVAL::TREND_PULLBACK** (total=44438): h1_trend_not_aligned=15541, ema_alignment_reject=7118, basic_filters_failed=5513, h1_pullback_not_confirmed=4489, ema_not_tested_prev=3985, no_ema_reclaim_close=3038, body_conviction_fail=1707, rsi_reject=1592, prev_already_below_emas=761, no_prev_low_break=346, ema21_not_tagged=92, missing_fvg_or_orderblock=87, prev_already_above_emas=48, no_prev_high_break=47, momentum_flat=41, momentum_reject=33
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=58603): breakout_not_found=33572, basic_filters_failed=13313, move_not_fresh=7800, breakout_stale=2651, retest_proximity_failed=1074, volume_spike_missing=177, missing_fvg_or_orderblock=16
- **EVAL::WHALE_MOMENTUM** (total=47086): momentum_reject=39024, recent_ticks_insufficient=6714, basic_filters_failed=1348

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=30): execution:overextended=30
- **DIVERGENCE_CONTINUATION** (total=93): setup_compat:regime_VOLATILE_UNSUITABLE=59, setup_compat:regime_BREAKOUT_EXPANSION=18, execution:overextended=16
- **FAILED_AUCTION_RECLAIM** (total=1407): execution:overextended=920, setup_compat:regime_STRONG_TREND=464, context_floor=23
- **FUNDING_EXTREME_SIGNAL** (total=140): execution:trigger_not_confirmed=139, context_floor=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=4664): setup_compat:regime_STRONG_TREND=1723, execution:trigger_not_confirmed=1619, execution:overextended=1322
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_DIRTY_RANGE=3, execution:overextended=2, setup_compat:regime_CLEAN_RANGE=2, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=3729): setup_compat:regime_STRONG_TREND=1773, setup_compat:regime_WEAK_TREND=1419, execution:overextended=520, entry_quality=17
- **MOVER_AVWAP_SCALP** (total=1436): execution:overextended=1279, entry_quality=87, execution:trigger_not_confirmed=70
- **MOVER_TREND_PULLBACK** (total=9540): execution:trigger_not_confirmed=5749, execution:overextended=3102, entry_quality=689
- **QUIET_COMPRESSION_BREAK** (total=4): execution:overextended=3, execution:trigger_not_confirmed=1
- **RANGE_FADE** (total=2166): setup_compat:regime_STRONG_TREND=1279, setup_compat:regime_WEAK_TREND=604, setup_compat:regime_VOLATILE_UNSUITABLE=134, execution:overextended=133, setup_compat:regime_BREAKOUT_EXPANSION=16
- **TREND_PULLBACK_EMA** (total=1805): setup_compat:regime_CLEAN_RANGE=1133, setup_compat:regime_DIRTY_RANGE=616, setup_compat:regime_VOLATILE_UNSUITABLE=42, entry_quality=14
- **VOLUME_SURGE_BREAKOUT** (total=15): execution:overextended=15
- **WHALE_MOMENTUM** (total=5960): execution:trigger_not_confirmed=5859, context_floor=66, execution:overextended=35

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 121018 | 34.5% |
| QUIET | 75291 | 21.5% |
| TRENDING_DOWN | 72741 | 20.7% |
| TRENDING_UP | 68573 | 19.6% |
| VOLATILE | 13083 | 3.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **110**
- Average confidence gap to threshold: **17.57** (samples=110) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=48, BTCUSDT=19, FFUSDT=12, XRPUSDT=11, TRXUSDT=10, ONDOUSDT=4, HYPEUSDT=3, ARBUSDT=2, SOLUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 78 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 8 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 129 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 13 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 11 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 15 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 12 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 10 |
| MEAN_REVERT | kept | min_confidence_pass | 6 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 261 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 198 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 717 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 12 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1406 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 32 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 14 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 49 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 2 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 18 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 30 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | min_confidence | 228 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 61 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 8 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 61.50 | 65.00 | 3.50 | 20.80 | 18.20 | 20.00 | 4.50 | 20.00 |
| DIVERGENCE_CONTINUATION | filtered | 81 | 57.97 | 64.12 | 6.15 | 19.70 | 19.79 | 18.69 | 0.63 | 11.87 |
| DIVERGENCE_CONTINUATION | kept | 8 | 78.45 | 65.00 | -13.45 | 20.06 | 19.12 | 19.85 | 0.00 | -1.40 |
| FAILED_AUCTION_RECLAIM | filtered | 129 | 47.23 | 61.67 | 14.44 | 19.48 | 18.03 | 20.00 | 2.86 | 14.28 |
| FAILED_AUCTION_RECLAIM | kept | 13 | 68.95 | 65.00 | -3.95 | 21.07 | 18.64 | 20.00 | 3.69 | 7.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 47.02 | 65.00 | 17.98 | 19.18 | 13.84 | 16.95 | 4.82 | 6.76 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.00 | 65.00 | -1.00 | 18.70 | 13.00 | 17.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 15 | 57.25 | 65.00 | 7.75 | 20.53 | 19.87 | 18.60 | 2.40 | 13.04 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.12 | 65.00 | -5.12 | 20.94 | 19.70 | 17.88 | 2.25 | 0.29 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 34.50 | 61.00 | 26.50 | 20.90 | 18.40 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 84.50 | 65.00 | -19.50 | 20.20 | 16.70 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 10 | 35.54 | 65.00 | 29.46 | 22.28 | 16.16 | 14.23 | 0.00 | 19.20 |
| MEAN_REVERT | kept | 6 | 68.97 | 65.00 | -3.97 | 19.35 | 14.00 | 14.50 | 0.00 | -0.50 |
| MOVER_AVWAP_SCALP | filtered | 261 | 54.89 | 63.27 | 8.38 | 21.04 | 14.35 | 15.80 | 3.81 | 12.98 |
| MOVER_AVWAP_SCALP | kept | 198 | 77.35 | 65.00 | -12.35 | 19.86 | 14.96 | 15.80 | 3.94 | 1.54 |
| MOVER_TREND_PULLBACK | filtered | 729 | 54.86 | 64.12 | 9.26 | 20.39 | 18.83 | 15.80 | 4.21 | 14.00 |
| MOVER_TREND_PULLBACK | kept | 1406 | 77.31 | 65.00 | -12.31 | 20.28 | 18.56 | 15.80 | 4.28 | 1.79 |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 54.07 | 65.00 | 10.93 | 21.22 | 19.76 | 20.00 | 0.00 | 5.32 |
| QUIET_COMPRESSION_BREAK | kept | 14 | 76.53 | 65.00 | -11.53 | 21.90 | 19.79 | 20.00 | 0.00 | 1.43 |
| TREND_PULLBACK_EMA | filtered | 51 | 57.17 | 64.53 | 7.36 | 21.74 | 19.97 | 19.37 | 4.87 | 18.24 |
| TREND_PULLBACK_EMA | kept | 18 | 77.08 | 65.00 | -12.08 | 20.40 | 19.83 | 18.43 | 4.56 | 0.98 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 45.95 | 63.93 | 17.98 | 18.41 | 17.38 | 20.00 | 3.48 | 11.40 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 90.00 | 65.00 | -25.00 | 20.40 | 14.30 | 20.00 | 6.00 | -3.00 |
| WHALE_MOMENTUM | filtered | 289 | 47.02 | 65.00 | 17.98 | 23.35 | 15.46 | 17.00 | 0.00 | 16.98 |
| WHALE_MOMENTUM | kept | 8 | 67.51 | 65.00 | -2.51 | 23.70 | 18.50 | 17.00 | 0.00 | 13.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 61.50 | 17.00 | 18.00 | 12.00 | 17.00 | 5.00 | 8.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 81 | 57.97 | 23.22 | 16.52 | 3.96 | 11.44 | 5.79 | 8.67 | 0.63 |
| DIVERGENCE_CONTINUATION | kept | 8 | 78.45 | 25.00 | 18.00 | 6.00 | 16.50 | 5.00 | 9.17 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 129 | 47.23 | 20.72 | 17.29 | 3.72 | 13.31 | 6.81 | 5.99 | 2.86 |
| FAILED_AUCTION_RECLAIM | kept | 13 | 68.95 | 23.77 | 17.38 | 4.38 | 13.38 | 7.00 | 7.57 | 3.69 |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 47.02 | 22.09 | 11.27 | 5.45 | 11.18 | 7.82 | 6.15 | 4.82 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.00 | 17.00 | 8.00 | 9.00 | 12.00 | 9.00 | 6.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 15 | 57.25 | 25.00 | 14.00 | 3.00 | 12.93 | 5.00 | 7.96 | 2.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.12 | 23.67 | 14.33 | 4.00 | 14.00 | 6.75 | 5.42 | 2.25 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 34.50 | 17.00 | 14.00 | 6.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 84.50 | 25.00 | 14.00 | 15.00 | 14.00 | 8.50 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 10 | 35.54 | 24.20 | 14.40 | 9.00 | 13.00 | 5.00 | 2.64 | 0.00 |
| MEAN_REVERT | kept | 6 | 68.97 | 19.67 | 14.00 | 11.50 | 12.50 | 5.00 | 6.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 261 | 54.89 | 18.59 | 18.00 | 13.48 | 13.12 | 6.29 | 5.85 | 3.81 |
| MOVER_AVWAP_SCALP | kept | 198 | 77.35 | 19.37 | 18.24 | 13.71 | 14.50 | 7.48 | 7.17 | 3.94 |
| MOVER_TREND_PULLBACK | filtered | 729 | 54.86 | 18.26 | 18.00 | 7.70 | 12.40 | 5.94 | 8.98 | 4.21 |
| MOVER_TREND_PULLBACK | kept | 1406 | 77.31 | 19.33 | 18.04 | 8.03 | 14.03 | 6.72 | 8.97 | 4.28 |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 54.07 | 19.00 | 18.00 | 9.84 | 13.94 | 7.12 | 5.53 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 14 | 76.53 | 18.71 | 18.00 | 13.07 | 14.00 | 6.86 | 8.18 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 51 | 57.17 | 15.82 | 18.00 | 7.50 | 13.65 | 6.99 | 8.58 | 4.87 |
| TREND_PULLBACK_EMA | kept | 18 | 77.08 | 17.94 | 18.00 | 7.50 | 15.50 | 6.22 | 9.65 | 4.56 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 45.95 | 17.00 | 17.87 | 13.20 | 12.00 | 5.00 | 3.80 | 3.48 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 90.00 | 25.00 | 18.00 | 15.00 | 11.00 | 5.00 | 10.00 | 6.00 |
| WHALE_MOMENTUM | filtered | 289 | 47.02 | 23.42 | 15.83 | 6.17 | 12.51 | 6.32 | 4.03 | 0.00 |
| WHALE_MOMENTUM | kept | 8 | 67.51 | 24.00 | 18.00 | 11.62 | 15.50 | 7.81 | 4.17 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 61.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 81 | 57.97 | 0.00 | 0.00 | 3.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.67** |
| DIVERGENCE_CONTINUATION | kept | 8 | 78.45 | 0.00 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.60** |
| FAILED_AUCTION_RECLAIM | filtered | 129 | 47.23 | 0.00 | 0.00 | 0.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.82** |
| FAILED_AUCTION_RECLAIM | kept | 13 | 68.95 | 0.00 | 0.00 | 5.54 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.54** |
| FUNDING_EXTREME_SIGNAL | filtered | 11 | 47.02 | 0.00 | 0.00 | 6.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.76** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 15 | 57.25 | 0.00 | 0.00 | 0.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.53** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 34.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 84.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 10 | 35.54 | 0.00 | 0.00 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | **1.20** |
| MEAN_REVERT | kept | 6 | 68.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 261 | 54.89 | 0.23 | 0.00 | 0.55 | 0.00 | 0.90 | 0.29 | 0.00 | 0.64 | **2.61** |
| MOVER_AVWAP_SCALP | kept | 198 | 77.35 | 0.38 | 0.00 | 0.70 | 0.00 | 0.15 | 0.00 | 0.00 | 0.09 | **1.32** |
| MOVER_TREND_PULLBACK | filtered | 729 | 54.86 | 0.00 | 0.00 | 1.62 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | **2.24** |
| MOVER_TREND_PULLBACK | kept | 1406 | 77.31 | 0.00 | 0.00 | 0.62 | 0.00 | 0.46 | 0.00 | 0.00 | 0.02 | **1.10** |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 54.07 | 0.00 | 0.00 | 1.35 | 0.00 | 0.13 | 0.00 | 0.00 | 3.71 | **5.19** |
| QUIET_COMPRESSION_BREAK | kept | 14 | 76.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.61 | 0.00 | 0.00 | 0.00 | **0.61** |
| TREND_PULLBACK_EMA | filtered | 51 | 57.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 18 | 77.08 | 0.00 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.27** |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 45.95 | 0.00 | 0.00 | 8.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.40** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 90.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 289 | 47.02 | 0.00 | 0.00 | 0.48 | 0.00 | 1.54 | 0.00 | 0.00 | 0.00 | **2.02** |
| WHALE_MOMENTUM | kept | 8 | 67.51 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | 0.00 | 0.00 | 0.00 | **3.60** |

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
- Outcomes recorded: **90459 held of 218772 seen** across 21 strategies; 2025 cells past the sample floor; **888 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 34788 | 469/34319/0 | 45% | -0.16 | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_FALLING/MAJOR (+1.18R) | LONDON/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.20R) |
| MOVER_AVWAP_SCALP | 11258 | 129/11129/0 | 39% | -0.28 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6769 | 76/6693/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 5350 | 26/5324/0 | 56% | +0.11 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | OVERLAP/MARKDOWN/CASCADE/BTC_RISING (-1.17R) |
| SHADOW_MEAN_REVERT | 4836 | 0/0/4836 | 44% | -0.07 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.52R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.09R) |
| TREND_PULLBACK_EMA | 4474 | 20/4454/0 | 48% | -0.11 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.28R) |
| QUIET_COMPRESSION_BREAK | 4036 | 188/3848/0 | 47% | -0.10 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+0.89R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 4027 | 0/0/4027 | 38% | -0.06 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.46R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.03R) |
| SHADOW_FUNDING_FADE | 3279 | 0/0/3279 | 35% | -0.39 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 3241 | 2/3239/0 | 42% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2315 | 34/2281/0 | 40% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1425 | 20/1405/0 | 60% | +0.09 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 1198 | 0/1198/0 | 45% | -0.01 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1112 | 2/1110/0 | 30% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| SR_FLIP_RETEST | 874 | 2/872/0 | 43% | -0.31 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.77R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 588 | 0/0/588 | 57% | +0.00 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (-0.33R) |
| BREAKDOWN_SHORT | 337 | 22/315/0 | 41% | -0.15 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 300 | 0/300/0 | 59% | +0.19 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 52 | 6/46/0 | 38% | -0.12 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.38R (n=17, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.36R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 108 | 32% / -0.44R | 108 | 49% / -0.15R | +0.29 | **ATR** |
| TREND_PULLBACK_EMA | 367 | 47% / -0.18R | 367 | 56% / -0.03R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 101 | 47% / -0.31R | 101 | 49% / -0.18R | +0.13 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| WHALE_MOMENTUM | 362 | 44% / -0.32R | 362 | 46% / -0.22R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 852 | 45% / -0.18R | 852 | 51% / -0.08R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 590 | 43% / -0.18R | 590 | 45% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5263 | 51% / -0.09R | 5263 | 55% / -0.01R | +0.09 | **ATR** |
| BREAKDOWN_SHORT | 25 | 32% / -0.15R | 25 | 36% / -0.10R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 74 | 43% / -0.05R | 74 | 51% / -0.01R | +0.04 | **ATR** |
| MA_CROSS_TREND_SHIFT | 17 | 35% / -0.20R | 17 | 35% / -0.16R | +0.04 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 469 | 52% / -0.18R | 469 | 56% / -0.15R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 672 | 47% / -0.14R | 672 | 47% / -0.14R | -0.01 | **FIXED** |
| MEAN_REVERT | 116 | 58% / +0.03R | 116 | 55% / +0.03R | -0.00 | **FIXED** |
| DIVERGENCE_CONTINUATION | 542 | 53% / -0.01R | 542 | 59% / -0.01R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7701 | 31% | -0.15R | 304 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 852 | 48% | -0.08R | 183 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 48 | 56% | -0.01R | 40 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 134 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 642 | 38% / -0.07R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6724 | 37% / -0.12R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1090 | 35% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 471 | 36% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 607 | 42% / +0.09R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 490 | 38% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 461 | 45% / -0.08R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 102 | 29% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 133 | 30% / -0.65R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 95 | 55% / +0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 46 | 39% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 102 | 32% / -0.42R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 24 | 12% / -0.63R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **7** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×268]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 420/6) (sustained 420 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.45R (bound 0.3) (streak 420/6) (sustained 420 cycles)
- **ALERT** `mean_revert_emission` — 766 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.08R over n=1405, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 42/6) (sustained 42 cycles)
- **ALERT** `range_fade_emission` — 5877 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 420/6) (sustained 420 cycles)
- **ALERT** `tuned_variants` — 478 non-stamps — atr_arm_uncomputable=478 (seen=6009 stamped=869 skipped=4662) (streak 420/6) (sustained 420 cycles)
- **ALERT** `auto_dispatch` — 99 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=198) (streak 410/3) (sustained 410 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 420/3) (sustained 420 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 43 fed / 0 quiet / 0 never delivered of 43 subscribed; 85640284 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 420/3) | 420 |
| ai_governor_live_arms | ok | 25 arms current, none stalled; covering 171/171 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 51 arms current, none stalled; covering 934/934 signals (100%) | 0 |
| auto_dispatch | violating | 99 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=198) (streak 410/3) | 410 |
| btc_reference | ok | BTC ref 77228.90 | 0 |
| candle_coverage | ok | 81/81 symbols with ≥20 15m candles, 81/81 updated within 45m [fresh=81; 73 Tier-1 futures + 8 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 863 dup bars, 0 undedupable; ws 0 out-of-order, 234 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 6 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +34 / upstream +19 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1664/1681 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 117 open dark rows are not being advanced (worst: BTRUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 58/120) | 58 |
| dark_sar_arms | ok | no open arms; covering 1658/1675 signals (99%) | 0 |
| depth_feed | ok | 43/43 books fresh (stale 0, never 0, thin 0); 26851118 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.45R (bound 0.3) (streak 420/6) | 420 |
| emission_controller | ok | last cycle 1416s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×268]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 420/6) | 420 |
| entry_quality_effective | ok | 6532 evaluated, 2157 suppressed, 2254 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| footprint_bars | ok | 5160 sealed bars over 43 symbols; 1453 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +224 | 0 |
| indicator_cache_key | ok | 155333 frozen value(s) avoided; 515656 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 766 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.08R over n=1405, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 42/6) | 42 |
| mean_revert_path | ok | output +28 / upstream +224 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 8 held, 8 with scan counts, 8 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2968 rows held, 1301218 evicted (sampled: execution:trigger_not_confirmed 400/478473, execution:overextended 400/435839, setup_compat:regime_STRONG_TREND 400/190368) | 0 |
| price_action_lane | ok | 679059 evaluated, 1079 emitted; layer1 1079 stamped / 0 blind; cooldown=89494, delta_opposed=56200, no_footprint=258625, no_opposing_target=547, no_sweep=220605, rr_below_floor=52509 | 0 |
| promoted_pair_integrity | ok | 8/8 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 5877 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 420/6) | 420 |
| range_fade_path | ok | output +17 / upstream +224 | 0 |
| sar_alignment_crosscheck | ok | 702/23689 disagreed (3.0%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +224 | 0 |
| sar_hold_arm | ok | 1628 held arms settled, 209 unscored, 49 still walking (38 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/48 unfetchable (8%); top cause: located bar does not contain the stamp; symbols: ETHFIUSDT, LITUSDT, THETAUSDT, TRXUSDT | 0 |
| sar_live_arms | ok | 49 arms current, none stalled; covering 943/943 signals (100%) | 0 |
| sar_refresh_budget | ok | 16 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 448 records await one (44 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 10.67s, worst 229.38s over 7866 lifetime cycles; lifetime 173 over 60s, 13 over 120s (plus 1/0 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.07s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 352545 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 53s ago (1.58s to run, worst 169.0s), 1163 overrun(s) of 8373 cycles, TTL 900s; slowest engine_state=8.72s, data_intake=7.56s, signals=6.91s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=1, gate reads=0, withheld=1) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +31 / upstream +224 | 0 |
| structural_snap | ok | 4953/4953 measured, 18 blind, 0 levels moved (refusals: redetect_cooldown=735) | 0 |
| structural_veto_lane | ok | 1494 stamped; 0 with no readable level book, 77 with clear air ahead, 1156 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +224 / upstream +19 | 0 |
| tuned_variants | violating | 478 non-stamps — atr_arm_uncomputable=478 (seen=6009 stamped=869 skipped=4662) (streak 420/6) | 420 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration
- `llm_client.google`: 5 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1613605`
- `Path funnel` emissions: `43`
- `Regime distribution` emissions: `43`
- `QUIET_SCALP_BLOCK` events: `110`
- `confidence_gate` events: `3326`
- `free_channel_post` events: `70`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **72**
- Total REST-fallback activations: **6**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 10 | 4943 | 10932 | 13234 | 0 |
| futures_aggtrade | 35 | 7175 | 33640 | 39067 | 0 |
| futures_depth | 15 | 3575 | 10298 | 10825 | 0 |
| futures_liq | 1 | 1738 | 1738 | 1738 | 0 |
| futures_mover | 11 | 5451 | 13266 | 24839 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 6 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **70**

| Source | Count |
|---|---:|
| signal_close | 65 |
| regime_shift | 5 |

- By severity: HIGH=70

## Dependency readiness
- cvd: presence[present=289664] state[populated=289664] buckets[many=289664] sources[none] quality[none]
- funding_rate: presence[absent=27540, present=262124] state[empty=27540, populated=262124] buckets[few=262124, none=27540] sources[none] quality[none]
- liquidation_clusters: presence[absent=168414, present=121250] state[empty=168414, populated=121250] buckets[few=94675, none=168414, some=26575] sources[none] quality[none]
- oi_snapshot: presence[absent=27540, present=262124] state[empty=27540, populated=262124] buckets[few=484, many=258861, none=27540, some=2779] sources[none] quality[none]
- order_book: presence[absent=95639, present=194025] state[populated=194025, unavailable=95639] buckets[few=194025, none=95639] sources[book_ticker=194025, unavailable=95639] quality[none=95639, top_of_book_only=194025]
- orderblocks: presence[absent=289664] state[empty=289664] buckets[none=289664] sources[measured_dark=289664] quality[none]
- recent_ticks: presence[present=289664] state[populated=289664] buckets[many=289664] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.938530921936035` sec
- Median create→first breach: `3427.3723385334015` sec
- Median create→terminal: `3430.156984567642` sec
- Median first breach→terminal: `3.2025126218795776` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 3.1}, "under_180s": {"count": 3, "pct": 4.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 3.1}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 3.1}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.735844285768104 | 0.8270251340211741 | 0.889748395179081 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 2.187609504473724 | 3.0 | 0.729203168157908 | 1 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.0381273036117307 | 2.267617967454394 | 0.9085865529231023 | 0 | 2 |
| MOVER_TREND_PULLBACK | 50 | 50 | 3.924171742582158 | 3.0 | 1.3186652083391315 | 36 | 14 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 0.9511524882500941 | 1.041414900845959 | 0.8958455167995276 | 0 | 7 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.7609993822499765 | 3.0 | 0.9203331274166588 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.1038 | 6418.171539068222 | 6423.194577217102 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.8056 | 4350.941335320473 | 4353.102557301521 |
| MOVER_AVWAP_SCALP | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.6034 | 33203.995478630066 | 33209.33674108982 |
| MOVER_TREND_PULLBACK | 50 | 50 | 38.0 | 36.0 | 38.0 | 0.0 | 0.6252 | 2874.6037806272507 | 2880.173663496971 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 50.0 | 50.0 | 50.0 | 0.0 | 0.6854 | 8862.61793935299 | 8866.281745433807 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.761 | 3037.7045769691467 | 3039.7148530483246 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 749 | 0 | 729 | 0.0 | 0.0 | None | None | 20 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2154 | 16 | 2050 | 0.0 | 100.0 | 3037.7045769691467 | 3039.7148530483246 | 104 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-200`
- Gating Δ: `-37370`
- No-generation Δ: `-412574`
- Fast failures Δ: `2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.4324, "current_avg_pnl": 1.1038, "current_win_rate": 100.0, "previous_avg_pnl": 1.5362, "previous_win_rate": 75.0, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.7891, "current_avg_pnl": 1.6034, "current_win_rate": 50.0, "previous_avg_pnl": -1.1857, "previous_win_rate": 12.5, "win_rate_delta": 37.5}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.2508, "current_avg_pnl": 0.6252, "current_win_rate": 38.0, "previous_avg_pnl": 0.876, "previous_win_rate": 45.5, "win_rate_delta": -7.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.9584, "current_avg_pnl": 0.6854, "current_win_rate": 50.0, "previous_avg_pnl": -0.273, "previous_win_rate": 28.6, "win_rate_delta": 21.4}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -128, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -235, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -4603.02, "median_terminal_delta_sec": -4602.63, "sl_rate_delta": 100.0, "win_rate_delta": -100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
