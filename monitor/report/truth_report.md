# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1216` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 96 | 96 | 86 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9632 | 9632 | 8762 | 10 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 92234 | 92252 | 22 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 96271 | 96272 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 95810 | 93197 | 3056 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 96324 | 95391 | 1074 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 95726 | 95392 | 389 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 86379 | 86392 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 96476 | 96515 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 96523 | 94118 | 3360 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 95255 | 100702 | 827 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 92282 | 87615 | 7574 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 95210 | 95211 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 96283 | 96291 | 16 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 95785 | 95666 | 139 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 97495 | 94925 | 3433 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 95218 | 95480 | 233 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 85978 | 83885 | 2382 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 86279 | 85937 | 433 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 92199 | 92219 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 86397 | 86414 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3566 | 3566 | 2728 | 14 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1194 | 1194 | 328 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 12109 | 12109 | 11603 | 11 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 3 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7378 | 7378 | 4779 | 11 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1617 | 1617 | 857 | 39 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18395 | 18395 | 9250 | 187 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 105 | 105 | 97 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 554 | 554 | 305 | 36 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 7443 | 7443 | 5343 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1040 | 1040 | 671 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1544 | 1544 | 1308 | 20 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 71 | 71 | 2 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=92252): breakout_not_found=47273, basic_filters_failed=32749, move_not_fresh=7850, breakout_stale=3787, retest_proximity_failed=456, volume_spike_missing=113, move_exhausted=20, rsi_reject=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=96272): cls_disabled_merged_into_lsr=96272
- **EVAL::DIVERGENCE_CONTINUATION** (total=93197): basic_filters_failed=31308, cvd_divergence_failed=30902, h1_trend_not_aligned=25119, ema_alignment_reject=4932, retest_proximity_failed=516, missing_fvg_or_orderblock=420
- **EVAL::FAILED_AUCTION_RECLAIM** (total=95391): auction_not_detected=53277, basic_filters_failed=30781, reclaim_hold_failed=5350, tail_too_small=3528, regime_blocked=2449, rsi_reject=6
- **EVAL::FUNDING_EXTREME** (total=95392): funding_not_extreme=58604, basic_filters_failed=30164, ema_alignment_reject=2825, missing_funding_rate=2040, rsi_reject=850, cvd_divergence_failed=446, momentum_reject=410, missing_fvg_or_orderblock=53
- **EVAL::LIQUIDATION_REVERSAL** (total=86392): cascade_threshold_not_met=54884, basic_filters_failed=30925, cvd_divergence_failed=308, rsi_reject=248, missing_fvg_or_orderblock=27
- **EVAL::MA_CROSS_TREND_SHIFT** (total=96515): no_ma_cross=63745, basic_filters_failed=31341, ma_cross_htf_misaligned=1171, ma_cross_cooldown=258
- **EVAL::MEAN_REVERT** (total=94118): no_extension=75741, basic_filters_failed=18377
- **EVAL::MOVER_AVWAP_SCALP** (total=100702): basic_filters_failed=33071, no_mover_leg=29299, no_avwap_tag=28789, avwap_slope_against=5527, avwap_reclaim_no_volume=2620, no_avwap_reclaim=1373, anchor_too_recent=23
- **EVAL::MOVER_TREND_PULLBACK** (total=87615): mover_run_too_small=43777, basic_filters_failed=32918, no_reclaim=9594, no_pullback_tag=1326
- **EVAL::OPENING_RANGE_BREAKOUT** (total=95211): feature_disabled=95211
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=96291): regime_blocked=54819, breakout_not_found=25474, basic_filters_failed=9909, adx_reject=5996, ema_alignment_reject=93
- **EVAL::QUIET_COMPRESSION_BREAK** (total=95666): regime_blocked=43704, basic_filters_failed=20852, compression_not_detected=20314, breakout_not_detected=9901, volume_confirmation_failed=877, missing_fvg_or_orderblock=16, rsi_reject=2
- **EVAL::RANGE_FADE** (total=94925): no_range_edge=76535, basic_filters_failed=18390
- **EVAL::SR_FLIP_RETEST** (total=95480): flip_close_not_confirmed=55313, basic_filters_failed=30743, regime_blocked=2412, retest_out_of_zone=2104, long_break_volume_thin=1984, h1_break_not_confirmed=1205, reclaim_hold_failed=1128, long_acceptance_not_held=212, ema_alignment_reject=177, wick_quality_failed=97, whipsaw_flip=77, missing_fvg_or_orderblock=28
- **EVAL::STANDARD** (total=83885): adx_reject=27799, momentum_reject=27221, basic_filters_failed=12501, sweeps_not_detected=7849, ema_alignment_reject=3904, macd_reject=3526, htf_poi_unanchored=927, rsi_reject=116, invalid_sl_geometry=38, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=85937): h1_trend_not_aligned=33924, basic_filters_failed=14948, ema_alignment_reject=11500, h1_pullback_not_confirmed=8018, no_ema_reclaim_close=5062, ema_not_tested_prev=4549, body_conviction_fail=3151, rsi_reject=2845, prev_already_above_emas=581, no_prev_high_break=416, prev_already_below_emas=376, no_prev_low_break=235, momentum_flat=162, ema21_not_tagged=107, missing_fvg_or_orderblock=40, momentum_reject=23
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=92219): breakout_not_found=42936, basic_filters_failed=32744, move_not_fresh=10692, breakout_stale=4434, retest_proximity_failed=1097, volume_spike_missing=281, move_exhausted=21, missing_fvg_or_orderblock=14
- **EVAL::WHALE_MOMENTUM** (total=86414): momentum_reject=60937, recent_ticks_insufficient=16129, basic_filters_failed=9348

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=8): execution:overextended=8
- **DIVERGENCE_CONTINUATION** (total=604): setup_compat:regime_VOLATILE_UNSUITABLE=602, setup_compat:regime_BREAKOUT_EXPANSION=2
- **FAILED_AUCTION_RECLAIM** (total=1618): setup_compat:regime_STRONG_TREND=897, execution:overextended=456, context_floor=166, setup_compat:regime_VOLATILE_UNSUITABLE=99
- **FUNDING_EXTREME_SIGNAL** (total=916): execution:trigger_not_confirmed=916
- **LIQUIDATION_REVERSAL** (total=4): execution:trigger_not_confirmed=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=3219): execution:overextended=1168, setup_compat:regime_STRONG_TREND=1114, execution:trigger_not_confirmed=937
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_DIRTY_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:overextended=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=5857): setup_compat:regime_WEAK_TREND=3242, setup_compat:regime_STRONG_TREND=2274, execution:overextended=321, entry_quality=20
- **MOVER_AVWAP_SCALP** (total=874): execution:overextended=601, execution:trigger_not_confirmed=158, entry_quality=115
- **MOVER_TREND_PULLBACK** (total=8733): execution:trigger_not_confirmed=4579, execution:overextended=2659, entry_quality=1495
- **QUIET_COMPRESSION_BREAK** (total=3): execution:overextended=2, execution:trigger_not_confirmed=1
- **RANGE_FADE** (total=5652): setup_compat:regime_WEAK_TREND=2399, setup_compat:regime_STRONG_TREND=2079, setup_compat:regime_VOLATILE_UNSUITABLE=758, execution:overextended=304, context_edge=84, setup_compat:regime_BREAKOUT_EXPANSION=28
- **SR_FLIP_RETEST** (total=10): setup_compat:regime_VOLATILE_UNSUITABLE=10
- **TREND_PULLBACK_EMA** (total=1265): setup_compat:regime_CLEAN_RANGE=836, setup_compat:regime_DIRTY_RANGE=277, setup_compat:regime_VOLATILE_UNSUITABLE=85, entry_quality=67

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 146817 | 29.8% |
| QUIET | 128702 | 26.1% |
| TRENDING_UP | 118029 | 23.9% |
| TRENDING_DOWN | 78977 | 16.0% |
| VOLATILE | 20557 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **108**
- Average confidence gap to threshold: **13.31** (samples=108) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DODOXUSDT=16, AAVEUSDT=13, DOTUSDT=11, TRXUSDT=11, DOGEUSDT=9, TAOUSDT=9, BCHUSDT=6, NEARUSDT=4, ASTERUSDT=4, 1000SHIBUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 8 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 416 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 71 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 78 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 45 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 102 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 80 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 43 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 12 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 89 |
| MEAN_REVERT | filtered | min_confidence | 140 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 7 |
| MEAN_REVERT | kept | min_confidence_pass | 79 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 137 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 282 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1398 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 16 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2652 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 7 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 18 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 215 |
| SR_FLIP_RETEST | filtered | min_confidence | 30 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 33 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 36 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 106 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 73 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 53.70 | 61.00 | 7.30 | 21.10 | 14.00 | 20.00 | 4.00 | 23.00 |
| BREAKDOWN_SHORT | kept | 2 | 69.25 | 65.00 | -4.25 | 17.50 | 18.00 | 20.00 | 5.25 | 13.00 |
| DIVERGENCE_CONTINUATION | filtered | 418 | 54.64 | 64.40 | 9.76 | 18.73 | 19.79 | 18.13 | 1.45 | 14.93 |
| DIVERGENCE_CONTINUATION | kept | 71 | 69.43 | 65.00 | -4.43 | 19.94 | 19.62 | 18.11 | 2.14 | -0.15 |
| FAILED_AUCTION_RECLAIM | filtered | 123 | 48.98 | 63.13 | 14.15 | 20.60 | 19.61 | 20.00 | 2.23 | 11.87 |
| FAILED_AUCTION_RECLAIM | kept | 102 | 68.23 | 65.00 | -3.23 | 21.37 | 19.53 | 20.00 | 3.11 | 1.65 |
| FUNDING_EXTREME_SIGNAL | filtered | 81 | 45.17 | 63.88 | 18.71 | 19.45 | 14.85 | 17.71 | 3.63 | 8.36 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 66.15 | 65.00 | -1.15 | 18.40 | 17.00 | 17.00 | 3.50 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 55 | 56.26 | 65.00 | 8.74 | 21.07 | 19.92 | 17.77 | 2.29 | 11.22 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 89 | 70.03 | 65.00 | -5.03 | 20.98 | 17.92 | 18.02 | 1.48 | 0.06 |
| MEAN_REVERT | filtered | 147 | 53.29 | 64.67 | 11.38 | 19.51 | 16.38 | 16.35 | 0.00 | 16.28 |
| MEAN_REVERT | kept | 79 | 69.52 | 65.00 | -4.52 | 20.72 | 17.39 | 16.43 | 0.00 | 0.45 |
| MOVER_AVWAP_SCALP | filtered | 137 | 57.77 | 64.82 | 7.05 | 19.77 | 16.08 | 15.80 | 4.18 | 15.56 |
| MOVER_AVWAP_SCALP | kept | 282 | 80.08 | 65.00 | -15.08 | 19.74 | 17.12 | 15.80 | 4.69 | 2.78 |
| MOVER_TREND_PULLBACK | filtered | 1414 | 56.33 | 64.25 | 7.92 | 19.35 | 18.43 | 15.80 | 3.88 | 16.96 |
| MOVER_TREND_PULLBACK | kept | 2652 | 76.16 | 65.00 | -11.16 | 19.74 | 18.52 | 15.80 | 4.28 | 1.88 |
| POST_DISPLACEMENT_CONTINUATION | kept | 7 | 70.60 | 65.00 | -5.60 | 21.20 | 20.00 | 15.23 | 4.50 | 1.86 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 49.72 | 64.36 | 14.64 | 20.83 | 19.05 | 20.00 | 0.00 | 11.22 |
| QUIET_COMPRESSION_BREAK | kept | 215 | 73.55 | 65.00 | -8.55 | 20.38 | 19.83 | 20.00 | 0.00 | -0.89 |
| SR_FLIP_RETEST | filtered | 32 | 54.86 | 63.75 | 8.89 | 20.84 | 20.00 | 16.51 | 2.02 | 19.34 |
| SR_FLIP_RETEST | kept | 33 | 70.11 | 65.00 | -5.11 | 20.69 | 20.00 | 16.14 | 2.20 | 2.33 |
| TREND_PULLBACK_EMA | filtered | 41 | 53.32 | 64.46 | 11.14 | 20.80 | 20.00 | 19.30 | 5.61 | 5.80 |
| TREND_PULLBACK_EMA | kept | 106 | 72.08 | 65.00 | -7.08 | 20.75 | 19.96 | 18.21 | 5.16 | 6.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 73 | 55.99 | 63.85 | 7.86 | 20.34 | 18.40 | 20.00 | 3.71 | 9.15 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.60 | 65.00 | -4.60 | 21.05 | 18.30 | 20.00 | 4.75 | 1.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 53.70 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 7.70 | 4.00 |
| BREAKDOWN_SHORT | kept | 2 | 69.25 | 25.00 | 16.00 | 12.00 | 12.00 | 5.00 | 7.00 | 5.25 |
| DIVERGENCE_CONTINUATION | filtered | 418 | 54.64 | 22.07 | 17.04 | 4.91 | 11.76 | 5.02 | 8.13 | 1.45 |
| DIVERGENCE_CONTINUATION | kept | 71 | 69.43 | 20.83 | 17.72 | 6.46 | 12.18 | 3.96 | 7.92 | 2.14 |
| FAILED_AUCTION_RECLAIM | filtered | 123 | 48.98 | 21.21 | 14.78 | 6.32 | 12.54 | 5.70 | 6.48 | 2.23 |
| FAILED_AUCTION_RECLAIM | kept | 102 | 68.23 | 23.12 | 14.86 | 4.15 | 13.25 | 6.23 | 5.40 | 3.11 |
| FUNDING_EXTREME_SIGNAL | filtered | 81 | 45.17 | 24.60 | 8.15 | 5.11 | 14.10 | 8.42 | 3.77 | 3.63 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 66.15 | 25.00 | 13.00 | 3.00 | 13.00 | 7.00 | 4.15 | 3.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 55 | 56.26 | 24.71 | 14.00 | 4.42 | 12.53 | 5.32 | 4.21 | 2.29 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 89 | 70.03 | 24.80 | 14.13 | 4.25 | 13.71 | 6.75 | 4.98 | 1.48 |
| MEAN_REVERT | filtered | 147 | 53.29 | 17.93 | 14.24 | 12.96 | 11.69 | 5.00 | 7.79 | 0.00 |
| MEAN_REVERT | kept | 79 | 69.52 | 19.73 | 14.15 | 12.38 | 12.75 | 5.00 | 6.68 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 137 | 57.77 | 19.07 | 18.10 | 12.12 | 13.48 | 6.26 | 6.25 | 4.18 |
| MOVER_AVWAP_SCALP | kept | 282 | 80.08 | 19.23 | 18.01 | 13.10 | 13.66 | 6.76 | 8.46 | 4.69 |
| MOVER_TREND_PULLBACK | filtered | 1414 | 56.33 | 18.47 | 18.12 | 7.55 | 13.07 | 6.17 | 8.64 | 3.88 |
| MOVER_TREND_PULLBACK | kept | 2652 | 76.16 | 19.59 | 18.06 | 7.87 | 12.43 | 6.52 | 9.35 | 4.28 |
| POST_DISPLACEMENT_CONTINUATION | kept | 7 | 70.60 | 3.86 | 18.00 | 15.00 | 14.00 | 9.29 | 7.81 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 49.72 | 17.00 | 16.88 | 12.12 | 14.24 | 5.56 | 4.14 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 215 | 73.55 | 18.30 | 17.70 | 11.62 | 14.06 | 6.65 | 5.65 | 0.00 |
| SR_FLIP_RETEST | filtered | 32 | 54.86 | 21.25 | 17.38 | 4.03 | 14.94 | 5.75 | 8.81 | 2.02 |
| SR_FLIP_RETEST | kept | 33 | 70.11 | 22.45 | 15.58 | 6.09 | 15.52 | 7.33 | 4.46 | 2.20 |
| TREND_PULLBACK_EMA | filtered | 41 | 53.32 | 9.22 | 18.00 | 8.34 | 14.07 | 8.22 | 8.90 | 5.61 |
| TREND_PULLBACK_EMA | kept | 106 | 72.08 | 18.83 | 18.00 | 8.17 | 14.23 | 5.74 | 8.33 | 5.16 |
| VOLUME_SURGE_BREAKOUT | filtered | 73 | 55.99 | 18.32 | 17.67 | 12.00 | 12.23 | 5.00 | 4.00 | 3.71 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.60 | 21.00 | 18.00 | 12.00 | 11.00 | 5.00 | 6.85 | 4.75 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 53.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 2 | 69.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 418 | 54.64 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.37** |
| DIVERGENCE_CONTINUATION | kept | 71 | 69.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 123 | 48.98 | 0.00 | 0.00 | 0.94 | 0.00 | 5.68 | 0.00 | 0.00 | 0.00 | **6.62** |
| FAILED_AUCTION_RECLAIM | kept | 102 | 68.23 | 0.00 | 0.00 | 0.71 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.83** |
| FUNDING_EXTREME_SIGNAL | filtered | 81 | 45.17 | 0.00 | 0.00 | 4.92 | 0.00 | 0.77 | 0.00 | 0.00 | 0.00 | **5.69** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 66.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 55 | 56.26 | 0.00 | 0.00 | 0.00 | 0.00 | 1.18 | 0.00 | 0.00 | 0.00 | **1.18** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 89 | 70.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 147 | 53.29 | 0.00 | 0.00 | 0.26 | 0.00 | 7.56 | 0.00 | 0.00 | 0.00 | **7.82** |
| MEAN_REVERT | kept | 79 | 69.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.82 | 0.00 | 0.00 | 0.00 | **0.82** |
| MOVER_AVWAP_SCALP | filtered | 137 | 57.77 | 1.20 | 0.00 | 0.59 | 0.00 | 0.96 | 0.00 | 0.00 | 1.27 | **4.02** |
| MOVER_AVWAP_SCALP | kept | 282 | 80.08 | 0.11 | 0.00 | 0.12 | 0.00 | 1.05 | 0.00 | 0.00 | 0.03 | **1.31** |
| MOVER_TREND_PULLBACK | filtered | 1414 | 56.33 | 0.00 | 0.00 | 2.60 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **2.80** |
| MOVER_TREND_PULLBACK | kept | 2652 | 76.16 | 0.00 | 0.00 | 0.28 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | **0.57** |
| POST_DISPLACEMENT_CONTINUATION | kept | 7 | 70.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 49.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.46 | **4.46** |
| QUIET_COMPRESSION_BREAK | kept | 215 | 73.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.03** |
| SR_FLIP_RETEST | filtered | 32 | 54.86 | 0.00 | 0.00 | 0.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.90** |
| SR_FLIP_RETEST | kept | 33 | 70.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 41 | 53.32 | 0.00 | 0.00 | 1.13 | 0.00 | 2.63 | 0.00 | 0.00 | 0.00 | **3.76** |
| TREND_PULLBACK_EMA | kept | 106 | 72.08 | 0.00 | 0.00 | 0.14 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | **0.41** |
| VOLUME_SURGE_BREAKOUT | filtered | 73 | 55.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.30 | **3.30** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **201304 held of 985807 seen** across 21 strategies; 4562 cells past the sample floor; **2480 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49426 | 615/48811/0 | 42% | -0.21 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 26620 | 188/26432/0 | 44% | -0.17 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 16056 | 280/15776/0 | 47% | -0.10 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 15344 | 172/15172/0 | 35% | -0.33 | OVERLAP/RANGE/NORMAL/BTC_FALLING/MIDCAP (+1.66R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14452 | 78/14374/0 | 39% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 11616 | 130/11486/0 | 39% | -0.39 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9781 | 505/9276/0 | 45% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8481 | 0/0/8481 | 41% | -0.13 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.99R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-0.99R) |
| SHADOW_RANGE_FADE | 8006 | 0/0/8006 | 36% | -0.13 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.80R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SHADOW_FUNDING_FADE | 7640 | 0/0/7640 | 35% | -0.40 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.01R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 7630 | 30/7600/0 | 47% | -0.27 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 6098 | 79/6019/0 | 36% | -0.32 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.60R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4783 | 4/4779/0 | 33% | -0.39 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.30R) |
| WHALE_MOMENTUM | 4395 | 4/4391/0 | 47% | -0.28 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 4324 | 0/4324/0 | 29% | -0.39 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| RANGE_FADE | 3315 | 6/3309/0 | 55% | +0.33 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1805 | 0/0/1805 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 624 | 75/549/0 | 36% | -0.11 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 572 | 0/572/0 | 35% | -0.28 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 254 | 40/214/0 | 44% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 82 | 6/76/0 | 34% | +0.03 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 478 | 28% / -0.53R | 478 | 52% / -0.09R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 1501 | 39% / -0.36R | 1501 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDATION_REVERSAL | 35 | 26% / -0.58R | 35 | 46% / -0.34R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1829 | 44% / -0.34R | 1829 | 58% / -0.10R | +0.23 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 250 | 37% / -0.17R | 250 | 49% / -0.03R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 76 | 45% / -0.16R | 76 | 50% / -0.03R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 857 | 47% / -0.25R | 857 | 52% / -0.13R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 9314 | 48% / -0.13R | 9314 | 54% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 473 | 46% / -0.30R | 473 | 48% / -0.20R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 3018 | 47% / -0.12R | 3018 | 53% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1729 | 41% / -0.22R | 1729 | 43% / -0.13R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 2183 | 48% / -0.11R | 2183 | 53% / -0.06R | +0.05 | **ATR** |
| BREAKDOWN_SHORT | 58 | 41% / -0.13R | 58 | 47% / -0.08R | +0.05 | **ATR** |
| RANGE_FADE | 188 | 46% / +0.10R | 188 | 52% / +0.13R | +0.03 | **ATR** |
| MEAN_REVERT | 535 | 45% / -0.18R | 535 | 44% / -0.19R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 16 | 50% / -0.08R | 16 | 50% / -0.08R | -0.00 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1749 | 49% / -0.08R | 1749 | 49% / -0.08R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12396 | 27% | -0.22R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 3018 | 51% | -0.02R | 246 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 159 | 48% | -0.04R | 75 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1914 | 33% / -0.13R | +0.93 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2175 | 40% / -0.12R | +0.89 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3581 | 37% / -0.13R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11397 | 36% / -0.16R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2525 | 37% / -0.12R | +0.16 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 172 | 34% / -0.39R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1690 | 37% / -0.08R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1441 | 32% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 361 | 32% / -0.32R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 582 | 32% / -0.25R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 440 | 47% / -0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 101 | 44% / +0.02R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 132 | 46% / +0.05R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 743 | 36% / -0.25R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 125 | 31% / +0.11R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 46 | 43% / -0.26R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 30 | 47% / +0.43R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — SR_FLIP_RETEST realized−counterfactual=+0.42R (bound 0.3) (streak 117/6) (sustained 117 cycles)
- **ALERT** `range_fade_emission` — 5033 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.33R over n=3309, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 117/6) (sustained 117 cycles)
- **ALERT** `tuned_variants` — 41 non-stamps — atr_arm_uncomputable=41 (seen=3082 stamped=246 skipped=2795) (streak 117/6) (sustained 117 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 11890721 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 37 arms current, none stalled; covering 2065/2065 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 19m ago | 0 |
| atr_trail_live_arms | ok | 76 arms current, none stalled; covering 1067/1067 signals (100%) | 0 |
| auto_dispatch | ok | 32 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=32. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 45/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 61476.00 | 0 |
| candle_coverage | ok | 81/81 symbols with ≥20 15m candles, 81/81 updated within 45m [fresh=81; 74 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 917 dup bars, 0 undedupable; ws 0 out-of-order, 258 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 63 cohorts, 25 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | violating | upstream +61 but output +0 (streak 1/72) | 1 |
| dark_atr_trail_arms | ok | no open arms; covering 1199/1218 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 103 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1189/1208 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3688976 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 74 rows | 0 |
| edge_reconciliation | violating | SR_FLIP_RETEST realized−counterfactual=+0.42R (bound 0.3) (streak 117/6) | 117 |
| emission_controller | ok | last cycle 782s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=322, MOVER_AVWAP_SCALP=244, MOVER_TREND_PULLBACK=3397, RANGE_FADE=1789, TREND_PULLBACK_EMA=248), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 3279 evaluated, 1171 suppressed, 2027 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,344 reads/day of 50,000 [engine 1,320, signing 24]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +0 / upstream +0 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 21526 frozen value(s) avoided; 87757 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=6019 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +0 / upstream +0 | 0 |
| mover_admission_metadata | ok | 956 symbols known, 247 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 9 locked / 9 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2243 rows held, 3819351 evicted (sampled: execution:trigger_not_confirmed 281/1339997, execution:overextended 281/1168103, setup_compat:regime_STRONG_TREND 281/663141) | 0 |
| price_action_lane | ok | 329534 evaluated, 362 emitted; layer1 362 stamped / 0 blind; cooldown=51197, delta_opposed=32455, no_footprint=101021, no_opposing_target=125, no_sweep=113484, rr_below_floor=30890 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 5033 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.33R over n=3309, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 117/6) | 117 |
| range_fade_path | ok | output +0 / upstream +0 | 0 |
| sar_alignment_crosscheck | ok | 154/6064 disagreed (2.5%) | 0 |
| sar_exit_shadow | ok | output +0 / upstream +0 | 0 |
| sar_hold_arm | ok | 1881 held arms settled, 122 unscored, 70 still walking (60 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 18/77 unfetchable (23%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, ACEUSDT, BARDUSDT, KAVAUSDT, LTCUSDT +1 more | 0 |
| sar_live_arms | ok | 73 arms current, none stalled; covering 1066/1066 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 477 records await one (59 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 55.85s, worst 147.82s over 4383 lifetime cycles; lifetime 58 over 60s, 2 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 5.91s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 93882 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 10m ago | 0 |
| snapshot_writer | ok | last cycle 3s ago (0.57s to run, worst 122.86s), 304 overrun(s) of 2777 cycles, TTL 900s; slowest data_intake=0.15s, signals=0.14s, activity=0.1s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +153 / upstream +0 | 0 |
| structural_snap | ok | 5999/5999 measured, 32 blind, 0 levels moved (refusals: redetect_cooldown=1058) | 0 |
| structural_veto_lane | ok | 1286 stamped; 0 with no readable level book, 2 with clear air ahead, 899 would-reject, 0 enforced | 0 |
| suppression_audit | violating | upstream +61 but output +0 (streak 1/72) | 1 |
| tuned_variants | violating | 41 non-stamps — atr_arm_uncomputable=41 (seen=3082 stamped=246 skipped=2795) (streak 117/6) | 117 |
| unlock_shorts | ok | 15 open, 45 scheduled, calendar 14.3h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2216660`
- `Path funnel` emissions: `66`
- `Regime distribution` emissions: `66`
- `QUIET_SCALP_BLOCK` events: `108`
- `confidence_gate` events: `6196`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **16**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 10 | 5354 | 21571 | 29905 | 0 |
| futures_liq | 4 | 3330 | 3750 | 24298 | 0 |
| futures_mover | 2 | 3106 | 3106 | 4793 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=349094] state[populated=349094] buckets[many=349094] sources[none] quality[none]
- funding_rate: presence[absent=15859, present=333235] state[empty=15859, populated=333235] buckets[few=333235, none=15859] sources[none] quality[none]
- liquidation_clusters: presence[absent=226698, present=122396] state[empty=226698, populated=122396] buckets[few=100671, none=226698, some=21725] sources[none] quality[none]
- oi_snapshot: presence[absent=14522, present=334572] state[empty=14522, populated=334572] buckets[many=334572, none=14522] sources[none] quality[none]
- order_book: presence[absent=104330, present=244764] state[populated=244764, unavailable=104330] buckets[few=244764, none=104330] sources[book_ticker=244764, unavailable=104330] quality[none=104330, top_of_book_only=244764]
- orderblocks: presence[absent=349094] state[empty=349094] buckets[none=349094] sources[measured_dark=349094] quality[none]
- recent_ticks: presence[present=349094] state[populated=349094] buckets[many=349094] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.5434720516204834` sec
- Median create→first breach: `5151.092185020447` sec
- Median create→terminal: `5151.092276096344` sec
- Median first breach→terminal: `6.699562072753906e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 10 | 10 | 0.8211668515876827 | 0.9334655613095455 | 0.8941978881432986 | 0 | 8 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 1.1867214581016556 | 1.3543304783663956 | 0.8762421558533399 | 0 | 3 |
| MEAN_REVERT | 2 | 2 | 0.7542679370017493 | 0.6659568585367754 | 1.1370242678790752 | 2 | 0 |
| MOVER_AVWAP_SCALP | 5 | 5 | 1.7639776632160258 | 1.7925379171728788 | 0.8391800615219844 | 1 | 4 |
| MOVER_TREND_PULLBACK | 33 | 33 | 4.401231326809513 | 3.0 | 1.5547214801148481 | 23 | 9 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 1.2424636394333217 | 1.4551619637971442 | 0.8782246773267604 | 0 | 8 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 10 | 1.7008005483190178 | 1.599999999999992 | 2 | 0 | 0 | 4 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 2.151035645472056 | 1.7800821857269105 | 0 | 0 | 0 | 1 | 0 | 2 |
| MEAN_REVERT | 2 | 0.8959136478316432 | 1.0820345577662982 | 2 | 0 | 0 | 0 | 0 | 0 |
| MOVER_AVWAP_SCALP | 5 | 2.1194420350291896 | 2.4106788248639783 | 3 | 2 | 2 | 2 | 0 | 0 |
| MOVER_TREND_PULLBACK | 33 | 5.3689828380075335 | 3.944070000000001 | 11 | 3 | 1 | 21 | 4 | 1 |
| QUIET_COMPRESSION_BREAK | 10 | 3.7251499007740607 | 1.9955421188630518 | 0 | 0 | 0 | 7 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 10 | 10 | 20.0 | 70.0 | 20.0 | 0.0 | -0.2699 | 5889.4761555194855 | 5889.476216077805 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.7248 | 6713.215542078018 | 6713.216562986374 |
| MEAN_REVERT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7543 | 2588.747285962105 | 2588.7473080158234 |
| MOVER_AVWAP_SCALP | 5 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 29355.01682114601 | 29355.01684308052 |
| MOVER_TREND_PULLBACK | 33 | 33 | 36.4 | 42.4 | 36.4 | 0.0 | 0.3062 | 3573.470541000366 | 3573.470582962036 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 30.0 | 50.0 | 30.0 | 0.0 | 0.2633 | 30937.525773525238 | 30938.155591845512 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1040 | 8 | 671 | 0.0 | 0.0 | None | None | 369 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1544 | 20 | 1308 | 0.0 | 0.0 | None | None | 236 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-206`
- Gating Δ: `19736`
- No-generation Δ: `1019188`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.3831, "current_avg_pnl": -0.2699, "current_win_rate": 20.0, "previous_avg_pnl": 1.1132, "previous_win_rate": 50.0, "win_rate_delta": -30.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 2.2752, "current_avg_pnl": -0.7248, "current_win_rate": 0.0, "previous_avg_pnl": -3.0, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.0, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.4345, "current_avg_pnl": 0.3062, "current_win_rate": 36.4, "previous_avg_pnl": 0.7407, "previous_win_rate": 39.3, "win_rate_delta": -2.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.7215, "current_avg_pnl": 0.2633, "current_win_rate": 30.0, "previous_avg_pnl": -0.4582, "previous_win_rate": 16.7, "win_rate_delta": 13.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 323, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 32, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
