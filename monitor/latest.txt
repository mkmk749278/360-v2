# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `2554` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 148 | 148 | 148 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10066 | 10066 | 8850 | 25 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 60161 | 60153 | 36 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 59972 | 59972 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 59500 | 57349 | 2604 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 60000 | 59372 | 729 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 59429 | 59360 | 103 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 52775 | 52787 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 60112 | 60142 | 12 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 60162 | 58230 | 2751 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 62742 | 66398 | 641 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 60194 | 57450 | 5244 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 59060 | 59060 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 59976 | 59995 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 59472 | 59389 | 108 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 60994 | 59773 | 1586 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 59064 | 59188 | 233 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 52403 | 49433 | 3264 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 52706 | 52226 | 546 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 60136 | 60142 | 16 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 52795 | 52818 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3868 | 3868 | 3350 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 571 | 571 | 232 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20979 | 20979 | 20857 | 4 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 19 | 19 | 7 | 6 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7694 | 7694 | 5856 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1501 | 1501 | 485 | 33 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 16563 | 16563 | 7886 | 248 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 27 | 27 | 27 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 614 | 614 | 308 | 36 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4465 | 4465 | 3594 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 931 | 931 | 405 | 17 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1914 | 1914 | 1583 | 29 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 61 | 61 | 50 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=60153): breakout_not_found=31178, basic_filters_failed=18033, move_not_fresh=7589, breakout_stale=2841, retest_proximity_failed=425, volume_spike_missing=60, move_exhausted=18, missing_fvg_or_orderblock=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=59972): cls_disabled_merged_into_lsr=59972
- **EVAL::DIVERGENCE_CONTINUATION** (total=57349): cvd_divergence_failed=22573, basic_filters_failed=16663, h1_trend_not_aligned=11954, ema_alignment_reject=5728, retest_proximity_failed=231, missing_fvg_or_orderblock=200
- **EVAL::FAILED_AUCTION_RECLAIM** (total=59372): auction_not_detected=35868, basic_filters_failed=16470, reclaim_hold_failed=3137, tail_too_small=2504, regime_blocked=1368, rsi_reject=25
- **EVAL::FUNDING_EXTREME** (total=59360): funding_not_extreme=39648, basic_filters_failed=15768, missing_funding_rate=2605, ema_alignment_reject=742, rsi_reject=426, cvd_divergence_failed=82, momentum_reject=78, missing_fvg_or_orderblock=11
- **EVAL::LIQUIDATION_REVERSAL** (total=52787): cascade_threshold_not_met=35952, basic_filters_failed=16413, rsi_reject=245, cvd_divergence_failed=172, missing_fvg_or_orderblock=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=60142): no_ma_cross=42358, basic_filters_failed=16690, ma_cross_cooldown=653, ma_cross_htf_misaligned=441
- **EVAL::MEAN_REVERT** (total=58230): no_extension=49874, basic_filters_failed=8356
- **EVAL::MOVER_AVWAP_SCALP** (total=66398): no_mover_leg=22115, no_avwap_tag=20212, basic_filters_failed=18242, avwap_slope_against=3318, avwap_reclaim_no_volume=1529, no_avwap_reclaim=968, anchor_too_recent=14
- **EVAL::MOVER_TREND_PULLBACK** (total=57450): mover_run_too_small=32248, basic_filters_failed=18138, no_reclaim=6007, no_pullback_tag=1057
- **EVAL::OPENING_RANGE_BREAKOUT** (total=59060): feature_disabled=59060
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=59995): regime_blocked=49731, breakout_not_found=5134, basic_filters_failed=3611, adx_reject=1486, ema_alignment_reject=33
- **EVAL::QUIET_COMPRESSION_BREAK** (total=59389): compression_not_detected=28915, basic_filters_failed=12838, regime_blocked=11574, breakout_not_detected=5576, volume_confirmation_failed=473, rsi_reject=10, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=59773): no_range_edge=51410, basic_filters_failed=8363
- **EVAL::SR_FLIP_RETEST** (total=59188): flip_close_not_confirmed=36370, basic_filters_failed=16429, retest_out_of_zone=1641, regime_blocked=1349, h1_break_not_confirmed=1191, long_break_volume_thin=925, reclaim_hold_failed=878, long_acceptance_not_held=153, ema_alignment_reject=133, wick_quality_failed=66, whipsaw_flip=31, missing_fvg_or_orderblock=22
- **EVAL::STANDARD** (total=49433): adx_reject=19890, momentum_reject=12489, macd_reject=5656, basic_filters_failed=5144, sweeps_not_detected=4186, ema_alignment_reject=1104, htf_poi_unanchored=809, invalid_sl_geometry=125, rsi_reject=30
- **EVAL::TREND_PULLBACK** (total=52226): h1_trend_not_aligned=14677, basic_filters_failed=10860, ema_alignment_reject=10171, no_ema_reclaim_close=4339, ema_not_tested_prev=3297, body_conviction_fail=2725, h1_pullback_not_confirmed=2012, rsi_reject=2001, prev_already_below_emas=1119, no_prev_low_break=535, momentum_flat=179, prev_already_above_emas=132, no_prev_high_break=84, momentum_reject=41, ema21_not_tagged=36, missing_fvg_or_orderblock=18
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=60142): breakout_not_found=33925, basic_filters_failed=18032, move_not_fresh=5142, breakout_stale=2106, retest_proximity_failed=778, volume_spike_missing=148, missing_fvg_or_orderblock=7, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=52818): momentum_reject=44598, recent_ticks_insufficient=5718, basic_filters_failed=2502

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=247): setup_compat:regime_VOLATILE_UNSUITABLE=233, setup_compat:regime_BREAKOUT_EXPANSION=14
- **FAILED_AUCTION_RECLAIM** (total=581): execution:overextended=283, context_floor=204, setup_compat:regime_STRONG_TREND=94
- **FUNDING_EXTREME_SIGNAL** (total=489): execution:trigger_not_confirmed=489
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=3297): execution:trigger_not_confirmed=2074, execution:overextended=871, setup_compat:regime_STRONG_TREND=352
- **MA_CROSS_TREND_SHIFT** (total=18): setup_compat:regime_DIRTY_RANGE=7, setup_compat:regime_CLEAN_RANGE=6, execution:trigger_not_confirmed=3, execution:overextended=2
- **MEAN_REVERT** (total=2696): setup_compat:regime_STRONG_TREND=1125, setup_compat:regime_WEAK_TREND=1044, execution:overextended=518, entry_quality=9
- **MOVER_AVWAP_SCALP** (total=916): execution:overextended=612, entry_quality=157, execution:trigger_not_confirmed=147
- **MOVER_TREND_PULLBACK** (total=7771): execution:trigger_not_confirmed=3834, execution:overextended=2498, entry_quality=1439
- **QUIET_COMPRESSION_BREAK** (total=7): execution:trigger_not_confirmed=6, execution:overextended=1
- **RANGE_FADE** (total=1455): setup_compat:regime_STRONG_TREND=673, setup_compat:regime_WEAK_TREND=595, setup_compat:regime_VOLATILE_UNSUITABLE=168, setup_compat:regime_BREAKOUT_EXPANSION=19
- **TREND_PULLBACK_EMA** (total=1842): setup_compat:regime_CLEAN_RANGE=1299, setup_compat:regime_DIRTY_RANGE=480, entry_quality=57, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **VOLUME_SURGE_BREAKOUT** (total=12): execution:overextended=12

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 226815 | 58.1% |
| QUIET | 71615 | 18.3% |
| TRENDING_UP | 42252 | 10.8% |
| TRENDING_DOWN | 32851 | 8.4% |
| VOLATILE | 16975 | 4.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **70**
- Average confidence gap to threshold: **13.79** (samples=70) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: GRAMUSDT=16, ARBUSDT=7, XMRUSDT=7, 1000SHIBUSDT=5, FILUSDT=5, ETHUSDT=5, WLDUSDT=4, AVAXUSDT=4, TAOUSDT=4, ASTERUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 129 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 133 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 73 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 5 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 24 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 32 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 12 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 8 |
| MEAN_REVERT | filtered | min_confidence | 28 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 288 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 14 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 274 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1584 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 22 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3093 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 95 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 11 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 144 |
| SR_FLIP_RETEST | filtered | min_confidence | 63 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 21 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 183 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 86 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 74 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 7 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 136 | 55.39 | 63.62 | 8.23 | 20.17 | 19.88 | 17.68 | 1.43 | 11.84 |
| DIVERGENCE_CONTINUATION | kept | 133 | 68.14 | 65.00 | -3.14 | 21.31 | 19.43 | 18.17 | 1.14 | 2.48 |
| FAILED_AUCTION_RECLAIM | filtered | 78 | 46.62 | 62.09 | 15.47 | 22.12 | 18.87 | 20.00 | 1.66 | 10.04 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 69.95 | 65.00 | -4.95 | 22.45 | 17.65 | 20.00 | 3.50 | 5.20 |
| FUNDING_EXTREME_SIGNAL | filtered | 24 | 50.01 | 63.83 | 13.82 | 20.69 | 13.92 | 17.23 | 3.29 | 6.72 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 67.00 | 65.00 | -2.00 | 20.00 | 20.00 | 17.00 | 2.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 32 | 44.19 | 64.00 | 19.81 | 19.96 | 18.88 | 17.27 | 1.69 | 11.44 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 69.56 | 65.00 | -4.56 | 21.02 | 17.33 | 18.35 | 1.42 | 0.23 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 47.85 | 63.00 | 15.15 | 19.25 | 17.00 | 15.80 | 0.00 | 13.90 |
| MA_CROSS_TREND_SHIFT | kept | 8 | 71.14 | 65.00 | -6.14 | 20.43 | 18.39 | 15.80 | 0.00 | 0.74 |
| MEAN_REVERT | filtered | 28 | 59.21 | 64.14 | 4.93 | 20.75 | 14.97 | 15.51 | 0.00 | 9.95 |
| MOVER_AVWAP_SCALP | filtered | 304 | 54.09 | 61.59 | 7.50 | 19.98 | 15.03 | 15.80 | 4.55 | 15.73 |
| MOVER_AVWAP_SCALP | kept | 274 | 78.27 | 65.00 | -13.27 | 20.38 | 16.97 | 15.80 | 4.55 | 4.25 |
| MOVER_TREND_PULLBACK | filtered | 1606 | 56.04 | 64.15 | 8.11 | 20.24 | 18.78 | 15.80 | 3.98 | 14.38 |
| MOVER_TREND_PULLBACK | kept | 3093 | 74.78 | 65.00 | -9.78 | 20.25 | 18.66 | 15.80 | 4.00 | 2.67 |
| QUIET_COMPRESSION_BREAK | filtered | 106 | 50.27 | 64.58 | 14.31 | 21.97 | 18.96 | 20.00 | 0.00 | 12.84 |
| QUIET_COMPRESSION_BREAK | kept | 144 | 76.19 | 65.00 | -11.19 | 22.43 | 19.35 | 20.00 | 0.00 | 0.94 |
| SR_FLIP_RETEST | filtered | 84 | 54.12 | 62.63 | 8.51 | 21.48 | 20.00 | 17.03 | 1.70 | 10.98 |
| SR_FLIP_RETEST | kept | 183 | 71.86 | 65.00 | -6.86 | 19.73 | 20.00 | 16.02 | 2.21 | 3.77 |
| TREND_PULLBACK_EMA | filtered | 87 | 57.14 | 64.14 | 7.00 | 20.40 | 19.98 | 17.08 | 5.01 | 17.01 |
| TREND_PULLBACK_EMA | kept | 74 | 75.60 | 65.00 | -10.60 | 21.04 | 19.94 | 17.81 | 4.67 | 4.85 |
| VOLUME_SURGE_BREAKOUT | filtered | 7 | 39.89 | 65.00 | 25.11 | 21.17 | 19.71 | 20.00 | 3.43 | 15.26 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 76.25 | 65.00 | -11.25 | 18.95 | 17.00 | 20.00 | 5.25 | 2.25 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 136 | 55.39 | 24.71 | 9.99 | 4.94 | 12.40 | 4.89 | 8.86 | 1.43 |
| DIVERGENCE_CONTINUATION | kept | 133 | 68.14 | 21.99 | 13.34 | 6.61 | 13.70 | 5.89 | 8.60 | 1.14 |
| FAILED_AUCTION_RECLAIM | filtered | 78 | 46.62 | 19.13 | 17.74 | 5.50 | 13.99 | 7.24 | 4.09 | 1.66 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 69.95 | 21.00 | 18.00 | 7.50 | 13.00 | 8.50 | 3.70 | 3.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 24 | 50.01 | 22.67 | 9.67 | 5.62 | 12.46 | 7.48 | 6.16 | 3.29 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 67.00 | 25.00 | 8.00 | 9.00 | 14.00 | 5.00 | 9.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 32 | 44.19 | 23.50 | 14.62 | 4.97 | 13.09 | 4.30 | 5.64 | 1.69 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 69.56 | 19.50 | 15.33 | 7.25 | 13.25 | 5.46 | 7.59 | 1.42 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 47.85 | 17.00 | 14.00 | 4.50 | 15.50 | 8.25 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 8 | 71.14 | 18.00 | 14.00 | 7.12 | 15.50 | 7.75 | 9.50 | 0.00 |
| MEAN_REVERT | filtered | 28 | 59.21 | 22.71 | 14.86 | 5.89 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 304 | 54.09 | 19.80 | 18.00 | 10.92 | 13.63 | 6.33 | 6.75 | 4.55 |
| MOVER_AVWAP_SCALP | kept | 274 | 78.27 | 18.96 | 18.01 | 11.48 | 13.88 | 7.71 | 8.54 | 4.55 |
| MOVER_TREND_PULLBACK | filtered | 1606 | 56.04 | 18.41 | 18.12 | 7.73 | 12.57 | 5.93 | 8.99 | 3.98 |
| MOVER_TREND_PULLBACK | kept | 3093 | 74.78 | 19.26 | 18.03 | 7.73 | 12.74 | 6.76 | 9.24 | 4.00 |
| QUIET_COMPRESSION_BREAK | filtered | 106 | 50.27 | 18.66 | 14.42 | 11.58 | 14.00 | 6.82 | 5.43 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 144 | 76.19 | 20.72 | 16.69 | 13.23 | 14.00 | 6.16 | 6.81 | 0.00 |
| SR_FLIP_RETEST | filtered | 84 | 54.12 | 20.71 | 15.50 | 3.50 | 14.25 | 5.27 | 6.85 | 1.70 |
| SR_FLIP_RETEST | kept | 183 | 71.86 | 22.91 | 17.84 | 4.89 | 12.97 | 5.62 | 9.22 | 2.21 |
| TREND_PULLBACK_EMA | filtered | 87 | 57.14 | 12.17 | 18.00 | 7.60 | 14.72 | 7.45 | 9.16 | 5.01 |
| TREND_PULLBACK_EMA | kept | 74 | 75.60 | 19.28 | 18.00 | 7.74 | 14.85 | 7.31 | 9.36 | 4.67 |
| VOLUME_SURGE_BREAKOUT | filtered | 7 | 39.89 | 18.14 | 14.57 | 12.00 | 13.57 | 5.00 | 3.43 | 3.43 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 76.25 | 23.00 | 16.00 | 12.75 | 13.25 | 5.00 | 7.00 | 5.25 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 136 | 55.39 | 0.00 | 0.00 | 1.31 | 0.00 | 0.48 | 0.18 | 0.00 | 0.00 | **1.97** |
| DIVERGENCE_CONTINUATION | kept | 133 | 68.14 | 0.00 | 0.00 | 0.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.82** |
| FAILED_AUCTION_RECLAIM | filtered | 78 | 46.62 | 0.00 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.51** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 69.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 24 | 50.01 | 0.00 | 0.00 | 2.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.47** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 32 | 44.19 | 0.00 | 0.00 | 4.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.88** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 69.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 47.85 | 0.00 | 0.00 | 9.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.60** |
| MA_CROSS_TREND_SHIFT | kept | 8 | 71.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 28 | 59.21 | 0.00 | 0.00 | 6.77 | 0.00 | 2.57 | 0.00 | 0.00 | 0.00 | **9.34** |
| MOVER_AVWAP_SCALP | filtered | 304 | 54.09 | 0.00 | 0.00 | 1.59 | 0.00 | 3.73 | 0.00 | 0.00 | 1.00 | **6.32** |
| MOVER_AVWAP_SCALP | kept | 274 | 78.27 | 0.00 | 0.00 | 0.97 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | **1.59** |
| MOVER_TREND_PULLBACK | filtered | 1606 | 56.04 | 0.00 | 0.00 | 3.14 | 0.00 | 0.85 | 0.00 | 0.00 | 0.00 | **3.99** |
| MOVER_TREND_PULLBACK | kept | 3093 | 74.78 | 0.06 | 0.00 | 1.13 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **1.23** |
| QUIET_COMPRESSION_BREAK | filtered | 106 | 50.27 | 0.00 | 0.00 | 0.15 | 0.00 | 0.04 | 0.00 | 0.00 | 4.47 | **4.66** |
| QUIET_COMPRESSION_BREAK | kept | 144 | 76.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.04 | **0.30** |
| SR_FLIP_RETEST | filtered | 84 | 54.12 | 0.00 | 0.00 | 2.06 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **3.09** |
| SR_FLIP_RETEST | kept | 183 | 71.86 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.03** |
| TREND_PULLBACK_EMA | filtered | 87 | 57.14 | 0.00 | 0.00 | 1.93 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | **2.34** |
| TREND_PULLBACK_EMA | kept | 74 | 75.60 | 0.00 | 0.00 | 2.79 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | **2.95** |
| VOLUME_SURGE_BREAKOUT | filtered | 7 | 39.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.14 | **5.14** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 76.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **195576 held of 925719 seen** across 21 strategies; 4426 cells past the sample floor; **2393 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49239 | 581/48658/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.26R) |
| MOVER_AVWAP_SCALP | 26176 | 193/25983/0 | 43% | -0.19 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15550 | 271/15279/0 | 45% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14771 | 141/14630/0 | 35% | -0.34 | OVERLAP/RANGE/NORMAL/BTC_FALLING/MIDCAP (+1.72R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 13822 | 78/13744/0 | 39% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 10783 | 113/10670/0 | 37% | -0.43 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9664 | 483/9181/0 | 45% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8384 | 0/0/8384 | 43% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.11R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7898 | 0/0/7898 | 35% | -0.15 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL (+0.34R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SHADOW_FUNDING_FADE | 7491 | 0/0/7491 | 33% | -0.42 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 7381 | 30/7351/0 | 46% | -0.30 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5726 | 71/5655/0 | 37% | -0.31 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4465 | 4/4461/0 | 31% | -0.44 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | LONDON/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.33R) |
| VOLUME_SURGE_BREAKOUT | 4122 | 0/4122/0 | 27% | -0.43 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 3115 | 6/3109/0 | 50% | +0.18 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1757 | 0/0/1757 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.56R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 552 | 0/552/0 | 36% | -0.25 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 242 | 40/202/0 | 44% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 414 | 27% / -0.57R | 414 | 52% / -0.09R | +0.47 | **ATR** |
| TREND_PULLBACK_EMA | 1424 | 39% / -0.37R | 1424 | 50% / -0.09R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1607 | 43% / -0.37R | 1607 | 57% / -0.11R | +0.25 | **ATR** |
| LIQUIDATION_REVERSAL | 34 | 26% / -0.56R | 34 | 47% / -0.32R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 238 | 37% / -0.17R | 238 | 48% / -0.04R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 74 | 45% / -0.17R | 74 | 50% / -0.03R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 805 | 47% / -0.25R | 805 | 52% / -0.13R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2880 | 46% / -0.14R | 2880 | 52% / -0.04R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1622 | 41% / -0.23R | 1622 | 44% / -0.13R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9153 | 48% / -0.13R | 9153 | 54% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 2050 | 47% / -0.12R | 2050 | 52% / -0.07R | +0.06 | **ATR** |
| RANGE_FADE | 165 | 43% / +0.03R | 165 | 50% / +0.08R | +0.05 | **ATR** |
| MEAN_REVERT | 486 | 46% / -0.15R | 486 | 45% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1691 | 48% / -0.09R | 1691 | 48% / -0.10R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12247 | 27% | -0.29R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2880 | 50% | -0.03R | 242 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 150 | 48% | -0.06R | 74 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1819 | 33% / -0.15R | +0.92 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1908 | 38% / -0.18R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3439 | 36% / -0.15R | +0.70 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11245 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2372 | 37% / -0.13R | +0.15 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1642 | 37% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1349 | 31% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 348 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 532 | 32% / -0.25R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 402 | 47% / -0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 115 | 46% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 692 | 35% / -0.28R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 119 | 30% / +0.11R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 45 | 44% / -0.22R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 25 | 48% / +0.53R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 948/6) (sustained 948 cycles)
- **ALERT** `range_fade_emission` — 10132 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.18R over n=3109, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 466/6) (sustained 466 cycles)
- **ALERT** `tuned_variants` — 1132 non-stamps — atr_arm_uncomputable=1132 (seen=26993 stamped=2648 skipped=23213) (streak 948/6) (sustained 948 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 375121931 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 24 arms current, none stalled; covering 2223/2223 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 47 arms current, none stalled; covering 1231/1231 signals (100%) | 0 |
| auto_dispatch | ok | 205 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=205. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 250/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 63594.90 | 0 |
| candle_coverage | ok | 92/92 symbols with ≥20 15m candles, 92/92 updated within 45m [fresh=92; 79 Tier-1 futures + 13 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 915 dup bars, 0 undedupable; ws 0 out-of-order, 690 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 62 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +53 / upstream +20 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 3023/3042 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 5 of 163 open dark rows are not being advanced (worst: SKYUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 27/120) | 27 |
| dark_sar_arms | ok | no open arms; covering 2984/3003 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 148901589 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 948/6) | 948 |
| emission_controller | ok | last cycle 818s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=714, MOVER_AVWAP_SCALP=544, MOVER_TREND_PULLBACK=4080, RANGE_FADE=549, TREND_PULLBACK_EMA=113), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=33, cvd_aligned=25, mover_stack_15m=12. Held back in this window: session_quality=54, cvd_aligned=18, mover_stack_15m=3. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,319 reads/day of 50,000 [engine 1,298, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1441 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +229 | 0 |
| indicator_cache_key | ok | 437318 frozen value(s) avoided; 2905515 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=5655 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +2 / upstream +229 | 0 |
| mover_admission_metadata | ok | 953 symbols known, 244 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 13 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2223 rows held, 3714708 evicted (sampled: execution:trigger_not_confirmed 278/1304136, execution:overextended 278/1141167, setup_compat:regime_STRONG_TREND 278/641595) | 0 |
| price_action_lane | ok | 2216950 evaluated, 2922 emitted; layer1 2922 stamped / 0 blind; cooldown=354015, delta_opposed=211783, no_footprint=805349, no_opposing_target=2933, no_sweep=653031, rr_below_floor=186917 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 10132 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.18R over n=3109, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 466/6) | 466 |
| range_fade_path | ok | output +20 / upstream +229 | 0 |
| sar_alignment_crosscheck | ok | 2106/52706 disagreed (4.0%) | 0 |
| sar_exit_shadow | violating | upstream +229 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1913 held arms settled, 87 unscored, 47 still walking (41 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 53/53 resolvable | 0 |
| sar_live_arms | ok | 47 arms current, none stalled; covering 1231/1231 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 453 records await one (53 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 149.92s, worst 213.0s over 28054 lifetime cycles; lifetime 710 over 60s, 56 over 120s (plus 1/0 during boot warm-up, not counted); recent 2/2 warn/kill breaches in 20/20 cycles; heartbeat age 3.38s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 869246 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (30.71s to run, worst 175.83s), 2315 overrun(s) of 19604 cycles, TTL 900s; slowest signals=0.29s, data_intake=0.24s, pair_context=0.16s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +19 / upstream +229 | 0 |
| structural_snap | ok | 6000/6000 measured, 44 blind, 0 levels moved (refusals: redetect_cooldown=3048) | 0 |
| structural_veto_lane | ok | 5118 stamped; 0 with no readable level book, 174 with clear air ahead, 3780 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +229 / upstream +20 | 0 |
| tuned_variants | violating | 1132 non-stamps — atr_arm_uncomputable=1132 (seen=26993 stamped=2648 skipped=23213) (streak 948/6) | 948 |
| unlock_shorts | ok | 17 open, 42 scheduled, calendar 18.3h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 69 — last: ServerDisconnectedError: Server disconnected

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1829645`
- `Path funnel` emissions: `49`
- `Regime distribution` emissions: `49`
- `QUIET_SCALP_BLOCK` events: `70`
- `confidence_gate` events: `6422`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 36905 | 36905 | 36905 | 0 |
| futures_aggtrade | 1 | 40240 | 40240 | 40240 | 0 |
| futures_depth | 1 | 42186 | 42186 | 42186 | 0 |
| futures_liq | 3 | 3660 | 3660 | 5562 | 0 |
| futures_mover | 1 | 40471 | 40471 | 40471 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=282813] state[populated=282813] buckets[many=282813] sources[none] quality[none]
- funding_rate: presence[absent=15270, present=267543] state[empty=15270, populated=267543] buckets[few=267543, none=15270] sources[none] quality[none]
- liquidation_clusters: presence[absent=166224, present=116589] state[empty=166224, populated=116589] buckets[few=98248, none=166224, some=18341] sources[none] quality[none]
- oi_snapshot: presence[absent=15270, present=267543] state[empty=15270, populated=267543] buckets[few=71, many=267093, none=15270, some=379] sources[none] quality[none]
- order_book: presence[absent=90308, present=192505] state[populated=192505, unavailable=90308] buckets[few=192505, none=90308] sources[book_ticker=192505, unavailable=90308] quality[none=90308, top_of_book_only=192505]
- orderblocks: presence[absent=282813] state[empty=282813] buckets[none=282813] sources[measured_dark=282813] quality[none]
- recent_ticks: presence[present=282813] state[populated=282813] buckets[many=282813] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.844781875610352` sec
- Median create→first breach: `4123.358715057373` sec
- Median create→terminal: `4124.144275903702` sec
- Median first breach→terminal: `7.200241088867188e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.4}, "under_180s": {"count": 1, "pct": 1.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 1.4}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 1.4}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 9 | 9 | 0.8422579472167637 | 1.3152804642166354 | 0.8542172772010572 | 0 | 8 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 2.064138275724995 | 3.0 | 0.6880460919083317 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 2.8457373723199733 | 3.0 | 0.9485791241066578 | 0 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.6017373808111968 | 2.864740354460911 | 0.9081930851987434 | 1 | 2 |
| MOVER_TREND_PULLBACK | 43 | 43 | 3.969680488338876 | 3.0 | 1.3255800155043174 | 35 | 8 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 1.4775426244804444 | 1.6096077811711629 | 0.9156775772011556 | 0 | 9 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.1606737633636284 | 2.6216773880325275 | 0.8241569970533769 | 0 | 1 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 9 | 1.70301986097318 | 1.70301986097318 | 0 | 0 | 0 | 4 | 0 | 5 |
| FUNDING_EXTREME_SIGNAL | 1 | 3.096201680672272 | 3.096201680672272 | 0 | 0 | 0 | 0 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 9.502259797816796 | 4.268606058479947 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 2.7735643846780755 | 3.9026060721921496 | 2 | 0 | 0 | 1 | 0 | 0 |
| MOVER_TREND_PULLBACK | 43 | 6.678458387637315 | 4.070429999999995 | 6 | 3 | 1 | 37 | 9 | 0 |
| QUIET_COMPRESSION_BREAK | 11 | 3.92033681647559 | 2.2163139367206726 | 0 | 0 | 0 | 8 | 0 | 3 |
| TREND_PULLBACK_EMA | 1 | 3.4834324553950626 | 3.4834324553950626 | 0 | 0 | 0 | 0 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 9 | 9 | 11.1 | 33.3 | 11.1 | 0.0 | -0.0739 | 5775.87864112854 | 5776.902459144592 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.0962 | 4614.473549127579 | 4614.741853952408 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.8457 | 1472.9066169261932 | 1472.9066650867462 |
| MOVER_AVWAP_SCALP | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | -0.0527 | 16901.58447909355 | 16901.58453798294 |
| MOVER_TREND_PULLBACK | 43 | 43 | 39.5 | 39.5 | 39.5 | 0.0 | 0.6159 | 2001.4015049934387 | 2001.4015729427338 |
| QUIET_COMPRESSION_BREAK | 11 | 11 | 27.3 | 45.5 | 27.3 | 0.0 | 0.0007 | 21954.479891061783 | 21954.479911088943 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3339.0447080135345 | 3339.0447289943695 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 931 | 17 | 405 | 0.0 | 0.0 | None | None | 526 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1914 | 29 | 1583 | 0.0 | 0.0 | 3339.0447080135345 | 3339.0447289943695 | 331 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `15`
- Gating Δ: `-2046`
- No-generation Δ: `-310469`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.2033, "current_avg_pnl": -0.0739, "current_win_rate": 11.1, "previous_avg_pnl": 0.1294, "previous_win_rate": 0.0, "win_rate_delta": 11.1}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.5256, "current_avg_pnl": -0.0527, "current_win_rate": 33.3, "previous_avg_pnl": 1.4729, "previous_win_rate": 33.3, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.2756, "current_avg_pnl": 0.6159, "current_win_rate": 39.5, "previous_avg_pnl": 0.3403, "previous_win_rate": 23.8, "win_rate_delta": 15.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.2764, "current_avg_pnl": 0.0007, "current_win_rate": 27.3, "previous_avg_pnl": -0.2757, "previous_win_rate": 20.0, "win_rate_delta": 7.3}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.3089, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.3089, "previous_win_rate": 25.0, "win_rate_delta": -25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -188, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -11548.35, "median_terminal_delta_sec": -11548.35, "sl_rate_delta": 0.0, "win_rate_delta": -25.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -11, "geometry_changed_delta": 0, "geometry_preserved_delta": -75, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3339.04, "median_terminal_delta_sec": 3339.04, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
