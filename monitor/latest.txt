# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `15` sec (warning=False)
- Latest performance record age: `665` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 151 | 151 | 151 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9468 | 9468 | 7979 | 13 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 90318 | 90316 | 39 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 78723 | 78723 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 78224 | 76312 | 2388 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 78764 | 77800 | 1065 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 80725 | 80442 | 343 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 70017 | 70039 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 78872 | 78912 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 78929 | 76816 | 3058 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 95400 | 101262 | 937 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 90363 | 80492 | 14826 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 80324 | 80324 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 78732 | 78750 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 78185 | 77926 | 290 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 79893 | 78238 | 2222 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 77722 | 77961 | 145 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 66996 | 62262 | 5120 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 67392 | 67079 | 419 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 90253 | 90277 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 70040 | 70077 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4246 | 4246 | 3905 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1570 | 1570 | 379 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 24823 | 24823 | 24454 | 9 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 18 | 18 | 5 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8528 | 8528 | 6005 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2105 | 2105 | 104 | 60 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 38369 | 38369 | 15262 | 531 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1410 | 1410 | 678 | 48 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 5265 | 5265 | 3660 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 848 | 848 | 262 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1998 | 1998 | 1722 | 26 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 101 | 101 | 15 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=90316): breakout_not_found=46479, basic_filters_failed=23687, move_not_fresh=14813, breakout_stale=3555, retest_proximity_failed=1466, volume_spike_missing=263, move_exhausted=38, ema_alignment_reject=8, missing_fvg_or_orderblock=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=78723): cls_disabled_merged_into_lsr=78723
- **EVAL::DIVERGENCE_CONTINUATION** (total=76312): cvd_divergence_failed=35685, basic_filters_failed=18289, h1_trend_not_aligned=15438, ema_alignment_reject=5875, retest_proximity_failed=765, missing_fvg_or_orderblock=260
- **EVAL::FAILED_AUCTION_RECLAIM** (total=77800): auction_not_detected=51211, basic_filters_failed=17700, reclaim_hold_failed=3699, regime_blocked=2888, tail_too_small=2288, rsi_reject=14
- **EVAL::FUNDING_EXTREME** (total=80442): funding_not_extreme=56762, basic_filters_failed=18561, ema_alignment_reject=2521, rsi_reject=1069, missing_funding_rate=914, cvd_divergence_failed=280, momentum_reject=271, missing_fvg_or_orderblock=64
- **EVAL::LIQUIDATION_REVERSAL** (total=70039): cascade_threshold_not_met=50428, basic_filters_failed=18556, cvd_divergence_failed=546, rsi_reject=482, missing_fvg_or_orderblock=19, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=78912): no_ma_cross=59271, basic_filters_failed=18318, ma_cross_cooldown=1190, ma_cross_htf_misaligned=133
- **EVAL::MEAN_REVERT** (total=76816): no_extension=63445, basic_filters_failed=13371
- **EVAL::MOVER_AVWAP_SCALP** (total=101262): no_avwap_tag=44011, no_mover_leg=24108, basic_filters_failed=23943, avwap_slope_against=6350, avwap_reclaim_no_volume=1730, no_avwap_reclaim=1103, anchor_too_recent=17
- **EVAL::MOVER_TREND_PULLBACK** (total=80492): mover_run_too_small=34756, basic_filters_failed=23826, no_reclaim=18547, no_pullback_tag=3363
- **EVAL::OPENING_RANGE_BREAKOUT** (total=80324): feature_disabled=80324
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=78750): regime_blocked=61421, breakout_not_found=12462, basic_filters_failed=3307, adx_reject=1525, ema_alignment_reject=35
- **EVAL::QUIET_COMPRESSION_BREAK** (total=77926): compression_not_detected=34044, regime_blocked=20133, basic_filters_failed=14370, breakout_not_detected=8504, volume_confirmation_failed=819, rsi_reject=47, missing_fvg_or_orderblock=9
- **EVAL::RANGE_FADE** (total=78238): no_range_edge=64860, basic_filters_failed=13378
- **EVAL::SR_FLIP_RETEST** (total=77961): flip_close_not_confirmed=50363, basic_filters_failed=17667, regime_blocked=2871, h1_break_not_confirmed=2200, long_break_volume_thin=1954, retest_out_of_zone=1750, reclaim_hold_failed=863, ema_alignment_reject=93, long_acceptance_not_held=71, wick_quality_failed=69, whipsaw_flip=53, missing_fvg_or_orderblock=7
- **EVAL::STANDARD** (total=62262): momentum_reject=19492, basic_filters_failed=10985, adx_reject=10799, macd_reject=8149, sweeps_not_detected=7617, ema_alignment_reject=3479, htf_poi_unanchored=1552, invalid_sl_geometry=112, rsi_reject=76, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=67079): h1_trend_not_aligned=18173, h1_pullback_not_confirmed=12934, ema_alignment_reject=10999, basic_filters_failed=9248, ema_not_tested_prev=4613, no_ema_reclaim_close=3827, body_conviction_fail=3062, rsi_reject=2700, prev_already_below_emas=696, no_prev_low_break=481, momentum_flat=99, prev_already_above_emas=89, no_prev_high_break=84, missing_fvg_or_orderblock=41, ema21_not_tagged=27, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=90277): breakout_not_found=51617, basic_filters_failed=23685, move_not_fresh=10211, breakout_stale=3402, retest_proximity_failed=1090, volume_spike_missing=204, move_exhausted=39, missing_fvg_or_orderblock=29
- **EVAL::WHALE_MOMENTUM** (total=70077): momentum_reject=57633, recent_ticks_insufficient=8084, basic_filters_failed=4360

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=13): execution:overextended=13
- **DIVERGENCE_CONTINUATION** (total=82): setup_compat:regime_VOLATILE_UNSUITABLE=76, setup_compat:regime_BREAKOUT_EXPANSION=6
- **FAILED_AUCTION_RECLAIM** (total=1164): setup_compat:regime_STRONG_TREND=641, execution:overextended=427, context_floor=83, setup_compat:regime_VOLATILE_UNSUITABLE=13
- **FUNDING_EXTREME_SIGNAL** (total=1451): execution:trigger_not_confirmed=1361, context_floor=90
- **LIQUIDITY_SWEEP_REVERSAL** (total=5346): execution:trigger_not_confirmed=3044, execution:overextended=1428, setup_compat:regime_STRONG_TREND=874
- **MA_CROSS_TREND_SHIFT** (total=21): setup_compat:regime_CLEAN_RANGE=7, setup_compat:regime_DIRTY_RANGE=6, execution:trigger_not_confirmed=4, setup_compat:regime_VOLATILE_UNSUITABLE=2, execution:overextended=2
- **MEAN_REVERT** (total=2459): setup_compat:regime_STRONG_TREND=1355, setup_compat:regime_WEAK_TREND=789, execution:overextended=293, entry_quality=22
- **MOVER_AVWAP_SCALP** (total=1217): execution:overextended=585, entry_quality=319, execution:trigger_not_confirmed=313
- **MOVER_TREND_PULLBACK** (total=17099): execution:trigger_not_confirmed=8387, execution:overextended=4429, entry_quality=4283
- **POST_DISPLACEMENT_CONTINUATION** (total=7): execution:overextended=7
- **QUIET_COMPRESSION_BREAK** (total=2): execution:trigger_not_confirmed=2
- **RANGE_FADE** (total=2557): setup_compat:regime_STRONG_TREND=1048, setup_compat:regime_WEAK_TREND=744, execution:overextended=438, setup_compat:regime_VOLATILE_UNSUITABLE=206, context_edge=110, setup_compat:regime_BREAKOUT_EXPANSION=11
- **TREND_PULLBACK_EMA** (total=1869): setup_compat:regime_CLEAN_RANGE=1153, setup_compat:regime_DIRTY_RANGE=617, entry_quality=66, setup_compat:regime_VOLATILE_UNSUITABLE=33
- **VOLUME_SURGE_BREAKOUT** (total=5): execution:overextended=5

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 222514 | 45.8% |
| QUIET | 134008 | 27.6% |
| TRENDING_DOWN | 53605 | 11.0% |
| TRENDING_UP | 47012 | 9.7% |
| VOLATILE | 28507 | 5.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **491**
- Average confidence gap to threshold: **11.28** (samples=491) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: WLDUSDT=46, ONDOUSDT=45, ARBUSDT=42, ENAUSDT=32, SOLUSDT=31, DOTUSDT=22, LITUSDT=20, APTUSDT=19, HYPEUSDT=18, STRKUSDT=14

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 198 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 9 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 114 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 96 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 15 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 16 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 7 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 138 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 35 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 7 |
| MEAN_REVERT | filtered | min_confidence | 111 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 5 |
| MEAN_REVERT | kept | min_confidence_pass | 21 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 399 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 46 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 20 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 718 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2974 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 242 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 8015 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 162 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 159 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 269 |
| SR_FLIP_RETEST | filtered | min_confidence | 48 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 27 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 100 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 22 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 11 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 108 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 68 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 9 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 207 | 54.30 | 64.04 | 9.74 | 19.81 | 19.73 | 17.74 | 1.61 | 14.37 |
| DIVERGENCE_CONTINUATION | kept | 114 | 68.31 | 65.00 | -3.31 | 20.50 | 19.77 | 18.10 | 1.31 | 0.88 |
| FAILED_AUCTION_RECLAIM | filtered | 111 | 51.49 | 64.58 | 13.09 | 21.13 | 19.03 | 20.00 | 1.93 | 4.73 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.35 | 65.00 | -2.35 | 19.65 | 17.80 | 20.00 | 2.25 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 40.22 | 61.84 | 21.62 | 20.44 | 14.06 | 17.00 | 2.95 | 16.11 |
| FUNDING_EXTREME_SIGNAL | kept | 7 | 67.47 | 65.00 | -2.47 | 15.96 | 10.91 | 19.83 | 4.71 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 138 | 51.62 | 64.97 | 13.35 | 20.23 | 18.92 | 17.81 | 2.41 | 8.02 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 35 | 71.45 | 65.00 | -6.45 | 20.06 | 18.94 | 19.16 | 1.46 | 3.42 |
| MA_CROSS_TREND_SHIFT | kept | 7 | 69.89 | 65.00 | -4.89 | 20.76 | 19.66 | 15.80 | 0.00 | 0.30 |
| MEAN_REVERT | filtered | 116 | 40.38 | 64.66 | 24.28 | 20.15 | 14.77 | 15.44 | 0.00 | 22.74 |
| MEAN_REVERT | kept | 21 | 73.44 | 65.00 | -8.44 | 18.64 | 14.71 | 14.54 | 0.00 | -2.14 |
| MOVER_AVWAP_SCALP | filtered | 465 | 56.98 | 59.10 | 2.12 | 20.51 | 15.85 | 15.80 | 4.18 | 14.63 |
| MOVER_AVWAP_SCALP | kept | 718 | 81.21 | 65.00 | -16.21 | 20.28 | 16.71 | 15.80 | 4.23 | 2.99 |
| MOVER_TREND_PULLBACK | filtered | 3216 | 54.59 | 63.92 | 9.33 | 19.88 | 19.07 | 15.80 | 3.99 | 17.31 |
| MOVER_TREND_PULLBACK | kept | 8015 | 76.96 | 65.00 | -11.96 | 20.61 | 18.85 | 15.80 | 4.25 | 2.08 |
| QUIET_COMPRESSION_BREAK | filtered | 321 | 49.55 | 65.00 | 15.45 | 21.35 | 19.19 | 20.00 | 0.00 | 12.61 |
| QUIET_COMPRESSION_BREAK | kept | 269 | 75.05 | 65.00 | -10.05 | 21.93 | 19.55 | 20.00 | 0.00 | 1.84 |
| SR_FLIP_RETEST | filtered | 75 | 58.98 | 64.47 | 5.49 | 22.03 | 20.00 | 15.61 | 1.41 | 8.54 |
| SR_FLIP_RETEST | kept | 100 | 71.96 | 65.00 | -6.96 | 20.85 | 20.00 | 16.07 | 1.86 | 1.24 |
| TREND_PULLBACK_EMA | filtered | 33 | 57.47 | 64.39 | 6.92 | 20.92 | 20.00 | 18.31 | 4.68 | 17.56 |
| TREND_PULLBACK_EMA | kept | 108 | 76.35 | 65.00 | -11.35 | 21.20 | 19.87 | 16.98 | 4.38 | -0.47 |
| VOLUME_SURGE_BREAKOUT | filtered | 68 | 52.60 | 64.35 | 11.75 | 19.82 | 19.19 | 20.00 | 3.96 | 9.34 |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 75.86 | 65.00 | -10.86 | 19.62 | 16.60 | 20.00 | 5.67 | 5.78 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 207 | 54.30 | 22.18 | 14.28 | 4.70 | 11.79 | 5.23 | 9.10 | 1.61 |
| DIVERGENCE_CONTINUATION | kept | 114 | 68.31 | 20.30 | 14.75 | 6.50 | 13.25 | 5.26 | 9.35 | 1.31 |
| FAILED_AUCTION_RECLAIM | filtered | 111 | 51.49 | 19.59 | 17.35 | 5.46 | 14.80 | 5.80 | 6.28 | 1.93 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.35 | 21.00 | 18.00 | 6.00 | 15.50 | 6.75 | 8.35 | 2.25 |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 40.22 | 22.89 | 10.11 | 6.79 | 12.42 | 8.63 | 5.17 | 2.95 |
| FUNDING_EXTREME_SIGNAL | kept | 7 | 67.47 | 25.00 | 9.43 | 3.00 | 11.57 | 7.57 | 6.19 | 4.71 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 138 | 51.62 | 23.26 | 15.33 | 5.07 | 13.18 | 5.59 | 5.66 | 2.41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 35 | 71.45 | 20.37 | 15.03 | 10.46 | 13.37 | 5.74 | 8.86 | 1.46 |
| MA_CROSS_TREND_SHIFT | kept | 7 | 69.89 | 23.86 | 14.00 | 3.86 | 14.00 | 6.57 | 7.90 | 0.00 |
| MEAN_REVERT | filtered | 116 | 40.38 | 16.78 | 16.31 | 13.14 | 11.66 | 6.27 | 5.95 | 0.00 |
| MEAN_REVERT | kept | 21 | 73.44 | 25.00 | 15.14 | 10.71 | 10.86 | 5.00 | 6.73 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 465 | 56.98 | 19.52 | 18.02 | 11.16 | 12.98 | 6.64 | 6.73 | 4.18 |
| MOVER_AVWAP_SCALP | kept | 718 | 81.21 | 19.18 | 18.00 | 13.09 | 13.85 | 7.10 | 8.92 | 4.23 |
| MOVER_TREND_PULLBACK | filtered | 3216 | 54.59 | 17.97 | 18.00 | 7.85 | 12.50 | 6.52 | 8.70 | 3.99 |
| MOVER_TREND_PULLBACK | kept | 8015 | 76.96 | 19.16 | 18.01 | 8.33 | 12.96 | 6.90 | 9.50 | 4.25 |
| QUIET_COMPRESSION_BREAK | filtered | 321 | 49.55 | 18.76 | 15.98 | 11.93 | 14.03 | 6.93 | 5.39 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 269 | 75.05 | 17.81 | 17.26 | 11.89 | 14.03 | 7.10 | 9.28 | 0.00 |
| SR_FLIP_RETEST | filtered | 75 | 58.98 | 19.13 | 14.40 | 4.36 | 14.25 | 6.11 | 7.91 | 1.41 |
| SR_FLIP_RETEST | kept | 100 | 71.96 | 21.56 | 13.80 | 6.45 | 14.29 | 6.48 | 9.30 | 1.86 |
| TREND_PULLBACK_EMA | filtered | 33 | 57.47 | 15.18 | 18.00 | 7.50 | 14.64 | 5.61 | 9.42 | 4.68 |
| TREND_PULLBACK_EMA | kept | 108 | 76.35 | 15.85 | 18.00 | 8.22 | 15.25 | 6.90 | 8.52 | 4.38 |
| VOLUME_SURGE_BREAKOUT | filtered | 68 | 52.60 | 19.59 | 14.06 | 12.40 | 13.15 | 5.00 | 5.25 | 3.96 |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 75.86 | 25.00 | 16.22 | 12.00 | 12.00 | 5.00 | 9.08 | 5.67 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 207 | 54.30 | 0.00 | 0.00 | 2.67 | 0.00 | 1.17 | 0.13 | 0.00 | 0.00 | **3.97** |
| DIVERGENCE_CONTINUATION | kept | 114 | 68.31 | 0.00 | 0.00 | 0.38 | 0.00 | 0.44 | 0.16 | 0.00 | 0.00 | **0.98** |
| FAILED_AUCTION_RECLAIM | filtered | 111 | 51.49 | 0.00 | 0.00 | 1.59 | 0.00 | 0.58 | 0.00 | 0.00 | 0.00 | **2.17** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 67.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 40.22 | 0.00 | 0.00 | 5.85 | 0.00 | 3.41 | 0.00 | 0.00 | 0.00 | **9.26** |
| FUNDING_EXTREME_SIGNAL | kept | 7 | 67.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 138 | 51.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | **0.07** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 35 | 71.45 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.14** |
| MA_CROSS_TREND_SHIFT | kept | 7 | 69.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 116 | 40.38 | 0.00 | 0.00 | 4.45 | 0.00 | 7.60 | 0.00 | 0.00 | 0.00 | **12.05** |
| MEAN_REVERT | kept | 21 | 73.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 465 | 56.98 | 0.12 | 0.00 | 0.00 | 0.00 | 4.13 | 0.34 | 0.00 | 1.11 | **5.70** |
| MOVER_AVWAP_SCALP | kept | 718 | 81.21 | 0.03 | 0.00 | 0.00 | 0.00 | 1.71 | 0.57 | 0.00 | 0.10 | **2.41** |
| MOVER_TREND_PULLBACK | filtered | 3216 | 54.59 | 1.93 | 0.00 | 1.78 | 0.00 | 1.17 | 0.33 | 0.00 | 0.00 | **5.21** |
| MOVER_TREND_PULLBACK | kept | 8015 | 76.96 | 0.08 | 0.00 | 0.60 | 0.00 | 0.22 | 0.20 | 0.00 | 0.00 | **1.10** |
| QUIET_COMPRESSION_BREAK | filtered | 321 | 49.55 | 0.00 | 0.00 | 1.57 | 0.00 | 0.49 | 0.00 | 0.00 | 4.22 | **6.28** |
| QUIET_COMPRESSION_BREAK | kept | 269 | 75.05 | 0.00 | 0.00 | 0.17 | 0.00 | 0.05 | 0.28 | 0.00 | 0.00 | **0.50** |
| SR_FLIP_RETEST | filtered | 75 | 58.98 | 0.00 | 0.00 | 0.00 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | **1.44** |
| SR_FLIP_RETEST | kept | 100 | 71.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.40 | 0.00 | 0.00 | **0.40** |
| TREND_PULLBACK_EMA | filtered | 33 | 57.47 | 0.00 | 0.00 | 4.36 | 0.00 | 0.65 | 1.52 | 0.00 | 0.00 | **6.53** |
| TREND_PULLBACK_EMA | kept | 108 | 76.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.11 | 0.43 | 0.00 | 0.00 | **0.54** |
| VOLUME_SURGE_BREAKOUT | filtered | 68 | 52.60 | 0.00 | 0.00 | 0.47 | 0.00 | 0.00 | 0.15 | 0.00 | 1.59 | **2.21** |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 75.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **158625 held of 606722 seen** across 21 strategies; 3592 cells past the sample floor; **1853 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 45817 | 749/45068/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.27R) |
| MOVER_AVWAP_SCALP | 20661 | 183/20478/0 | 43% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11756 | 125/11631/0 | 38% | -0.26 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 11480 | 113/11367/0 | 48% | -0.05 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9559 | 43/9516/0 | 40% | -0.22 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 8605 | 99/8506/0 | 34% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7550 | 0/0/7550 | 43% | -0.09 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.24R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_RANGE_FADE | 7022 | 0/0/7022 | 35% | -0.15 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.38R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.21R) |
| QUIET_COMPRESSION_BREAK | 6637 | 404/6233/0 | 51% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 6247 | 0/0/6247 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 4375 | 46/4329/0 | 39% | -0.28 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/MARKDOWN/CASCADE/BTC_NEUTRAL (-1.32R) |
| SR_FLIP_RETEST | 4211 | 19/4192/0 | 43% | -0.30 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3301 | 2/3299/0 | 33% | -0.45 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3250 | 0/3250/0 | 31% | -0.33 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| RANGE_FADE | 1791 | 4/1787/0 | 33% | -0.53 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1453 | 0/0/1453 | 53% | -0.06 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.51R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 396 | 0/396/0 | 29% | -0.63 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 136 | 28/108/0 | 43% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 253 | 28% / -0.57R | 253 | 53% / -0.13R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 23 | 26% / -0.63R | 23 | 52% / -0.26R | +0.37 | **ATR** |
| TREND_PULLBACK_EMA | 827 | 40% / -0.31R | 827 | 53% / -0.06R | +0.25 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1344 | 43% / -0.35R | 1344 | 56% / -0.13R | +0.22 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 162 | 35% / -0.24R | 162 | 46% / -0.07R | +0.17 | **ATR** |
| RANGE_FADE | 88 | 32% / -0.37R | 88 | 39% / -0.23R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 389 | 42% / -0.31R | 389 | 45% / -0.18R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2016 | 44% / -0.17R | 2016 | 50% / -0.05R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1144 | 40% / -0.24R | 1144 | 42% / -0.14R | +0.11 | **ATR** |
| MA_CROSS_TREND_SHIFT | 43 | 40% / -0.19R | 43 | 42% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8099 | 50% / -0.10R | 8099 | 55% / -0.00R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1260 | 48% / -0.10R | 1260 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1147 | 49% / -0.11R | 1147 | 49% / -0.12R | -0.01 | **FIXED** |
| MEAN_REVERT | 306 | 48% / -0.15R | 306 | 47% / -0.15R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10893 | 28% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2016 | 48% | -0.05R | 226 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 103 | 48% | -0.07R | 62 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1497 | 40% / -0.17R | +0.84 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1107 | 34% / -0.24R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2479 | 35% / -0.12R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9906 | 37% / -0.11R | +0.42 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1447 | 38% / -0.07R | +0.21 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1115 | 37% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 953 | 33% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 239 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 336 | 33% / +0.05R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 254 | 49% / -0.03R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 65 | 38% / -0.08R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 355 | 32% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 65 | 28% / -0.41R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 29 | 41% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **6** · boot grace active: False
- **ALERT** `ai_governor_verdicts` — upstream +1 but output +0 (streak 7/6) (sustained 7 cycles)
- **ALERT** `sar_alignment_crosscheck` — 1147/20037 disagreed (5.7%) (streak 212/6) (sustained 212 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×247]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 211/6) (sustained 211 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 249/6) (sustained 249 cycles)
- **ALERT** `tuned_variants` — 353 non-stamps — atr_arm_uncomputable=353 (seen=10892 stamped=1233 skipped=9306) (streak 242/6) (sustained 242 cycles)
- **ALERT** `auto_dispatch` — 67 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=67) (streak 236/3) (sustained 236 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 41704358 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 10 arms current, none stalled; covering 1927/1927 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 7/6) | 7 |
| atr_trail_live_arms | ok | 23 arms current, none stalled; covering 1079/1079 signals (100%) | 0 |
| auto_dispatch | violating | 67 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=67) (streak 236/3) | 236 |
| binance_ip_weight | ok | peak 115/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 80894.20 | 0 |
| candle_coverage | ok | 78/78 symbols with ≥20 15m candles, 78/78 updated within 45m [fresh=78; 72 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 210 dup bars, 0 undedupable; ws 0 out-of-order, 479 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 58 cohorts, 36 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +23 / upstream +18 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1761/1779 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 129 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1756/1774 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 10933325 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 249/6) | 249 |
| emission_controller | ok | last cycle 1646s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×247]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 211/6) | 211 |
| entry_quality_effective | ok | 15084 evaluated, 5259 suppressed, 9825 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,397 reads/day of 50,000 [engine 1,359, signing 38]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4920 sealed bars over 41 symbols; 1313 incomplete, 3 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +196 | 0 |
| indicator_cache_key | ok | 84897 frozen value(s) avoided; 227718 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.29R over n=4329 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +196 but output +0 (streak 2/72) | 2 |
| mover_admission_metadata | ok | 931 symbols known, 225 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 5 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2976 rows held, 3096395 evicted (sampled: execution:trigger_not_confirmed 400/1096771, execution:overextended 400/968752, setup_compat:regime_STRONG_TREND 400/526028) | 0 |
| price_action_lane | ok | 583671 evaluated, 755 emitted; layer1 755 stamped / 0 blind; cooldown=81897, delta_opposed=49343, no_footprint=217147, no_opposing_target=978, no_sweep=186821, rr_below_floor=46730 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.53R over n=1787 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +196 but output +0 (streak 5/72) | 5 |
| sar_alignment_crosscheck | violating | 1147/20037 disagreed (5.7%) (streak 212/6) | 212 |
| sar_exit_shadow | ok | output +6 / upstream +196 | 0 |
| sar_hold_arm | ok | 1897 held arms settled, 103 unscored, 23 still walking (16 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/54 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: QUSDT | 0 |
| sar_live_arms | ok | 23 arms current, none stalled; covering 1077/1077 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 5 resolved, 48 still mid-window | 0 |
| scan_cycle | ok | last 32.66s, worst 213.02s over 6754 lifetime cycles; lifetime 176 over 60s, 15 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.94s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 275765 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 164s ago (3.21s to run, worst 135.69s), 626 overrun(s) of 5455 cycles, TTL 900s; slowest data_intake=33.47s, user_positions=29.75s, pair_context=12.29s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +142 / upstream +196 | 0 |
| structural_snap | ok | 6000/6000 measured, 31 blind, 0 levels moved (refusals: redetect_cooldown=952) | 0 |
| structural_veto_lane | ok | 1784 stamped; 0 with no readable level book, 159 with clear air ahead, 1372 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +196 / upstream +18 | 0 |
| tuned_variants | violating | 353 non-stamps — atr_arm_uncomputable=353 (seen=10892 stamped=1233 skipped=9306) (streak 242/6) | 242 |
| unlock_shorts | ok | 14 open, 44 scheduled, calendar 17.1h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 16 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2438018`
- `Path funnel` emissions: `55`
- `Regime distribution` emissions: `55`
- `QUIET_SCALP_BLOCK` events: `491`
- `confidence_gate` events: `14174`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **3**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 16547 | 16547 | 16547 | 0 |
| futures_aggtrade | 1 | 2859 | 2859 | 2859 | 0 |
| futures_liq | 1 | 21641 | 21641 | 21641 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=368466] state[populated=368466] buckets[many=368466] sources[none] quality[none]
- funding_rate: presence[absent=44728, present=323738] state[empty=44728, populated=323738] buckets[few=323738, none=44728] sources[none] quality[none]
- liquidation_clusters: presence[absent=227527, present=140939] state[empty=227527, populated=140939] buckets[few=113775, none=227527, some=27164] sources[none] quality[none]
- oi_snapshot: presence[absent=44727, present=323739] state[empty=44727, populated=323739] buckets[few=363, many=321219, none=44727, some=2157] sources[none] quality[none]
- order_book: presence[absent=116305, present=252161] state[populated=252161, unavailable=116305] buckets[few=252161, none=116305] sources[book_ticker=252161, unavailable=116305] quality[none=116305, top_of_book_only=252161]
- orderblocks: presence[absent=368466] state[empty=368466] buckets[none=368466] sources[measured_dark=368466] quality[none]
- recent_ticks: presence[present=368466] state[populated=368466] buckets[many=368466] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.5835405588150024` sec
- Median create→first breach: `2018.1803350448608` sec
- Median create→terminal: `2018.1803909540176` sec
- Median first breach→terminal: `6.461143493652344e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 3.6}, "under_180s": {"count": 3, "pct": 5.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 1.8}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 3.6}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.8000000000000005 | 1.1480099266864936 | 0.6968580858085833 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 2.105925022293919 | 3.0 | 0.9292906490264932 | 1 | 3 |
| MOVER_AVWAP_SCALP | 2 | 2 | 7.383572970614655 | 3.0 | 2.461190990204885 | 2 | 0 |
| MOVER_TREND_PULLBACK | 43 | 43 | 4.219561034472815 | 3.0 | 1.4065203448242718 | 35 | 8 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.1035020144047447 | 1.2117736889831883 | 0.9497731068768327 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5664 | 4430.521574020386 | 4431.164305925369 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | -0.767 | 5056.135946393013 | 5056.135991930962 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -2.9322 | 488.6044269800186 | 488.60445749759674 |
| MOVER_TREND_PULLBACK | 43 | 43 | 25.6 | 48.8 | 25.6 | 0.0 | -0.6633 | 1810.1834468841553 | 1810.1834700107574 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 50.0 | 25.0 | 50.0 | 0.0 | 1.3541 | 39191.05382657051 | 39191.69179558754 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 848 | 7 | 262 | 0.0 | 0.0 | None | None | 586 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1998 | 26 | 1722 | 0.0 | 0.0 | None | None | 276 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `350`
- Gating Δ: `13713`
- No-generation Δ: `412152`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.6919, "current_avg_pnl": 0.5664, "current_win_rate": 0.0, "previous_avg_pnl": 1.2583, "previous_win_rate": 100.0, "win_rate_delta": -100.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -1.4499, "current_avg_pnl": -0.767, "current_win_rate": 25.0, "previous_avg_pnl": 0.6829, "previous_win_rate": 50.0, "win_rate_delta": -25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -5.7569, "current_avg_pnl": -2.9322, "current_win_rate": 0.0, "previous_avg_pnl": 2.8247, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.5985, "current_avg_pnl": -0.6633, "current_win_rate": 25.6, "previous_avg_pnl": 0.9352, "previous_win_rate": 38.7, "win_rate_delta": -13.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0278, "current_avg_pnl": 1.3541, "current_win_rate": 50.0, "previous_avg_pnl": 1.3263, "previous_win_rate": 66.7, "win_rate_delta": -16.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": 211, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2442.75, "median_terminal_delta_sec": -2442.75, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": -76, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
