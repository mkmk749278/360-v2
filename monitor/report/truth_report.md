# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `8236` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 81 | 81 | 81 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 24075 | 24075 | 21451 | 20 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 118315 | 118327 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 115040 | 115050 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 114613 | 108247 | 6776 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 115063 | 109956 | 5378 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 116594 | 116155 | 487 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 104822 | 104831 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 115341 | 115375 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 115389 | 112078 | 4624 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 122391 | 126676 | 1145 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 118336 | 108571 | 13800 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 113275 | 113287 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 115053 | 115063 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 114561 | 113925 | 685 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 116710 | 114321 | 3057 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 111208 | 108937 | 5562 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 102289 | 96319 | 6446 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 102769 | 101852 | 992 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 118292 | 118212 | 98 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 104834 | 104836 | 11 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 18805 | 18805 | 14900 | 72 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1698 | 1698 | 504 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 27 | 27 | 19 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 33258 | 33258 | 32347 | 33 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 18 | 18 | 10 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11687 | 11687 | 8456 | 22 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2532 | 2532 | 585 | 27 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 34041 | 34041 | 18566 | 307 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 2 | 2 | 0 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2670 | 2670 | 1623 | 20 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 7285 | 7285 | 6557 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 19182 | 19182 | 10656 | 142 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4057 | 4057 | 3564 | 21 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 168 | 168 | 57 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 299 | 299 | 74 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=118327): breakout_not_found=64394, basic_filters_failed=34482, move_not_fresh=11921, breakout_stale=5951, retest_proximity_failed=1366, volume_spike_missing=138, move_exhausted=31, ema_alignment_reject=30, missing_fvg_or_orderblock=14
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=115050): cls_disabled_merged_into_lsr=115050
- **EVAL::DIVERGENCE_CONTINUATION** (total=108247): cvd_divergence_failed=39296, basic_filters_failed=30957, h1_trend_not_aligned=23490, ema_alignment_reject=11521, retest_proximity_failed=2202, missing_fvg_or_orderblock=781
- **EVAL::FAILED_AUCTION_RECLAIM** (total=109956): auction_not_detected=43621, basic_filters_failed=30073, reclaim_hold_failed=18434, tail_too_small=14184, regime_blocked=3644
- **EVAL::FUNDING_EXTREME** (total=116155): funding_not_extreme=73567, basic_filters_failed=30849, ema_alignment_reject=4485, missing_funding_rate=4215, rsi_reject=1819, momentum_reject=583, cvd_divergence_failed=508, missing_fvg_or_orderblock=129
- **EVAL::LIQUIDATION_REVERSAL** (total=104831): cascade_threshold_not_met=71621, basic_filters_failed=31754, cvd_divergence_failed=1044, rsi_reject=367, volume_spike_missing=32, missing_fvg_or_orderblock=13
- **EVAL::MA_CROSS_TREND_SHIFT** (total=115375): no_ma_cross=81814, basic_filters_failed=30982, ma_cross_cooldown=1585, ma_cross_htf_misaligned=994
- **EVAL::MEAN_REVERT** (total=112078): no_extension=95896, basic_filters_failed=16182
- **EVAL::MOVER_AVWAP_SCALP** (total=126676): no_mover_leg=43759, no_avwap_tag=38391, basic_filters_failed=34591, avwap_slope_against=5726, avwap_reclaim_no_volume=2238, no_avwap_reclaim=1692, insufficient_candles=231, anchor_too_recent=48
- **EVAL::MOVER_TREND_PULLBACK** (total=108571): mover_run_too_small=52978, basic_filters_failed=34494, no_reclaim=17924, no_pullback_tag=2944, insufficient_candles=231
- **EVAL::OPENING_RANGE_BREAKOUT** (total=113287): feature_disabled=113287
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=115063): regime_blocked=85262, breakout_not_found=19344, basic_filters_failed=5705, adx_reject=4699, ema_alignment_reject=53
- **EVAL::QUIET_COMPRESSION_BREAK** (total=113925): compression_not_detected=40141, regime_blocked=33364, basic_filters_failed=24353, breakout_not_detected=14762, volume_confirmation_failed=1162, missing_fvg_or_orderblock=77, rsi_reject=55, macd_reject=11
- **EVAL::RANGE_FADE** (total=114321): no_range_edge=98137, basic_filters_failed=16184
- **EVAL::SR_FLIP_RETEST** (total=108937): basic_filters_failed=30050, whipsaw_flip=17747, flip_close_not_confirmed=17407, long_break_volume_thin=14573, reclaim_hold_failed=10358, retest_out_of_zone=8518, regime_blocked=3634, long_disabled=3091, wick_quality_failed=2118, long_acceptance_not_held=564, missing_fvg_or_orderblock=477, ema_alignment_reject=369, rsi_reject=31
- **EVAL::STANDARD** (total=96319): momentum_reject=31639, adx_reject=29775, sweeps_not_detected=11922, basic_filters_failed=11480, macd_reject=7925, ema_alignment_reject=3181, rsi_reject=311, invalid_sl_geometry=86
- **EVAL::TREND_PULLBACK** (total=101852): h1_trend_not_aligned=28752, basic_filters_failed=18512, ema_alignment_reject=16782, h1_pullback_not_confirmed=12536, no_ema_reclaim_close=7552, ema_not_tested_prev=5848, body_conviction_fail=4826, rsi_reject=3696, prev_already_below_emas=931, prev_already_above_emas=721, no_prev_low_break=694, no_prev_high_break=451, momentum_flat=242, momentum_reject=151, ema21_not_tagged=79, missing_fvg_or_orderblock=79
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=118212): breakout_not_found=65929, basic_filters_failed=34476, move_not_fresh=11327, breakout_stale=3599, retest_proximity_failed=2486, volume_spike_missing=327, rsi_reject=41, missing_fvg_or_orderblock=21, move_exhausted=6
- **EVAL::WHALE_MOMENTUM** (total=104836): momentum_reject=75116, recent_ticks_insufficient=22529, basic_filters_failed=7191

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=475): setup_compat:regime_VOLATILE_UNSUITABLE=424, setup_compat:regime_BREAKOUT_EXPANSION=31, execution:overextended=20
- **FAILED_AUCTION_RECLAIM** (total=4165): execution:overextended=2189, setup_compat:regime_STRONG_TREND=1233, context_floor=743
- **FUNDING_EXTREME_SIGNAL** (total=1429): execution:trigger_not_confirmed=1421, context_floor=8
- **LIQUIDATION_REVERSAL** (total=27): execution:trigger_not_confirmed=27
- **LIQUIDITY_SWEEP_REVERSAL** (total=8004): execution:trigger_not_confirmed=4887, execution:overextended=2402, setup_compat:regime_STRONG_TREND=715
- **MA_CROSS_TREND_SHIFT** (total=18): setup_compat:regime_CLEAN_RANGE=7, setup_compat:regime_DIRTY_RANGE=5, execution:overextended=4, execution:trigger_not_confirmed=2
- **MEAN_REVERT** (total=5029): setup_compat:regime_WEAK_TREND=3326, setup_compat:regime_STRONG_TREND=1189, execution:overextended=514
- **MOVER_AVWAP_SCALP** (total=1492): execution:overextended=966, execution:trigger_not_confirmed=526
- **MOVER_TREND_PULLBACK** (total=15272): execution:trigger_not_confirmed=7880, execution:overextended=7392
- **QUIET_COMPRESSION_BREAK** (total=601): context_floor=461, execution:trigger_not_confirmed=140
- **RANGE_FADE** (total=3574): setup_compat:regime_WEAK_TREND=1396, setup_compat:regime_STRONG_TREND=1101, execution:overextended=523, setup_compat:regime_VOLATILE_UNSUITABLE=461, context_edge=93
- **TREND_PULLBACK_EMA** (total=3501): setup_compat:regime_CLEAN_RANGE=2610, setup_compat:regime_DIRTY_RANGE=795, setup_compat:regime_VOLATILE_UNSUITABLE=96
- **VOLUME_SURGE_BREAKOUT** (total=62): execution:overextended=45, context_floor=17
- **WHALE_MOMENTUM** (total=365): execution:trigger_not_confirmed=298, context_floor=67

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 247805 | 39.4% |
| QUIET | 183888 | 29.2% |
| TRENDING_UP | 84623 | 13.4% |
| TRENDING_DOWN | 81046 | 12.9% |
| VOLATILE | 32271 | 5.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **435**
- Average confidence gap to threshold: **12.09** (samples=435) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=44, LINKUSDT=30, BTCUSDT=30, ASTERUSDT=29, XRPUSDT=27, SUIUSDT=23, AAVEUSDT=23, ARBUSDT=20, AVAXUSDT=19, TAOUSDT=15

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 384 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 356 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 299 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 67 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1053 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 140 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 8 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 511 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 10 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 7 |
| MEAN_REVERT | kept | min_confidence_pass | 167 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 685 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 37 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 713 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1162 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 39 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 10197 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 130 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 75 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 315 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 1021 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 158 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2508 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 14 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 396 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 17 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 5 |
| WHALE_MOMENTUM | filtered | min_confidence | 33 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 403 | 57.10 | 64.73 | 7.63 | 20.20 | 19.60 | 18.12 | 2.59 | 7.53 |
| DIVERGENCE_CONTINUATION | kept | 356 | 71.12 | 65.00 | -6.12 | 19.33 | 19.73 | 18.15 | 2.96 | 2.00 |
| FAILED_AUCTION_RECLAIM | filtered | 366 | 54.39 | 64.09 | 9.70 | 20.71 | 17.65 | 20.00 | 3.30 | 6.97 |
| FAILED_AUCTION_RECLAIM | kept | 1053 | 70.64 | 65.00 | -5.64 | 20.52 | 18.59 | 20.00 | 3.27 | 0.49 |
| FUNDING_EXTREME_SIGNAL | filtered | 140 | 49.45 | 65.00 | 15.55 | 18.93 | 14.22 | 17.29 | 3.66 | 4.70 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.00 | 65.00 | -1.00 | 21.20 | 20.00 | 17.00 | 2.00 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 3 | 68.20 | 10.00 | -58.20 | 21.00 | 8.00 | 20.00 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 19 | 53.62 | 65.00 | 11.38 | 20.92 | 20.00 | 17.16 | 2.89 | 13.78 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 511 | 70.74 | 65.00 | -5.74 | 21.17 | 19.21 | 17.76 | 2.25 | 0.26 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.70 | 65.00 | 14.30 | 20.10 | 18.30 | 15.80 | 0.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 70.93 | 65.00 | -5.93 | 19.03 | 18.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 17 | 54.62 | 62.06 | 7.44 | 20.65 | 16.47 | 17.64 | 0.00 | 10.92 |
| MEAN_REVERT | kept | 167 | 71.37 | 65.00 | -6.37 | 19.76 | 17.23 | 18.80 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 724 | 55.09 | 62.19 | 7.10 | 19.68 | 15.56 | 15.80 | 3.53 | 8.10 |
| MOVER_AVWAP_SCALP | kept | 713 | 76.24 | 65.00 | -11.24 | 20.03 | 16.79 | 15.80 | 3.80 | 0.52 |
| MOVER_TREND_PULLBACK | filtered | 1201 | 53.38 | 63.71 | 10.33 | 20.07 | 19.21 | 15.80 | 4.21 | 14.78 |
| MOVER_TREND_PULLBACK | kept | 10197 | 76.98 | 65.00 | -11.98 | 19.95 | 18.86 | 15.80 | 4.48 | 1.31 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 77.35 | 65.00 | -12.35 | 20.70 | 20.00 | 17.75 | 4.50 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 205 | 50.43 | 65.00 | 14.57 | 20.32 | 19.65 | 20.00 | 0.00 | 6.67 |
| QUIET_COMPRESSION_BREAK | kept | 315 | 74.81 | 65.00 | -9.81 | 20.66 | 19.24 | 20.00 | 0.00 | -1.87 |
| RANGE_FADE | kept | 1 | 64.90 | 65.00 | 0.10 | 20.50 | 14.00 | 20.00 | 0.00 | 4.80 |
| SR_FLIP_RETEST | filtered | 1179 | 57.08 | 64.27 | 7.19 | 20.59 | 19.87 | 15.60 | 1.52 | 11.66 |
| SR_FLIP_RETEST | kept | 2508 | 71.82 | 65.00 | -6.82 | 20.17 | 19.94 | 16.23 | 1.90 | -0.42 |
| TREND_PULLBACK_EMA | filtered | 19 | 51.42 | 65.00 | 13.58 | 20.89 | 20.00 | 18.45 | 4.63 | 17.40 |
| TREND_PULLBACK_EMA | kept | 396 | 80.23 | 65.00 | -15.23 | 20.00 | 19.82 | 17.70 | 4.70 | -1.09 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 52.82 | 63.53 | 10.71 | 18.21 | 17.19 | 20.00 | 4.21 | 0.00 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 71.44 | 65.00 | -6.44 | 20.28 | 18.18 | 20.00 | 5.00 | 1.80 |
| WHALE_MOMENTUM | filtered | 33 | 51.59 | 65.00 | 13.41 | 24.49 | 17.75 | 17.00 | 0.00 | 15.73 |
| WHALE_MOMENTUM | kept | 1 | 67.00 | 65.00 | -2.00 | 24.70 | 19.20 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 403 | 57.10 | 22.53 | 11.75 | 5.89 | 11.81 | 5.73 | 8.40 | 2.59 |
| DIVERGENCE_CONTINUATION | kept | 356 | 71.12 | 21.90 | 15.89 | 5.88 | 12.50 | 6.24 | 8.43 | 2.96 |
| FAILED_AUCTION_RECLAIM | filtered | 366 | 54.39 | 20.85 | 16.72 | 5.91 | 13.23 | 5.99 | 4.95 | 3.30 |
| FAILED_AUCTION_RECLAIM | kept | 1053 | 70.64 | 20.68 | 15.88 | 5.53 | 12.79 | 6.14 | 6.83 | 3.27 |
| FUNDING_EXTREME_SIGNAL | filtered | 140 | 49.45 | 24.60 | 10.57 | 6.30 | 12.95 | 7.05 | 2.10 | 3.66 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.00 | 17.00 | 8.00 | 3.00 | 17.00 | 9.00 | 10.00 | 2.00 |
| LIQUIDATION_REVERSAL | filtered | 3 | 68.20 | 25.00 | 8.00 | 12.00 | 8.00 | 2.50 | 6.70 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 19 | 53.62 | 22.79 | 14.21 | 4.74 | 11.11 | 4.61 | 7.07 | 2.89 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 511 | 70.74 | 23.00 | 14.08 | 7.17 | 12.31 | 5.41 | 6.79 | 2.25 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.70 | 17.00 | 14.00 | 9.00 | 11.00 | 8.00 | 6.70 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 70.93 | 19.00 | 14.00 | 9.00 | 12.67 | 7.17 | 9.10 | 0.00 |
| MEAN_REVERT | filtered | 17 | 54.62 | 25.00 | 18.00 | 3.00 | 12.00 | 5.00 | 2.54 | 0.00 |
| MEAN_REVERT | kept | 167 | 71.37 | 23.23 | 16.40 | 8.82 | 12.00 | 6.16 | 4.76 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 724 | 55.09 | 19.98 | 18.10 | 8.24 | 13.29 | 6.18 | 4.49 | 3.53 |
| MOVER_AVWAP_SCALP | kept | 713 | 76.24 | 19.72 | 18.01 | 8.77 | 13.18 | 5.75 | 7.95 | 3.80 |
| MOVER_TREND_PULLBACK | filtered | 1201 | 53.38 | 17.85 | 18.21 | 7.95 | 12.82 | 5.46 | 8.72 | 4.21 |
| MOVER_TREND_PULLBACK | kept | 10197 | 76.98 | 19.49 | 18.07 | 8.06 | 13.29 | 5.76 | 9.34 | 4.48 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 77.35 | 17.00 | 18.00 | 13.50 | 14.00 | 5.00 | 8.35 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 205 | 50.43 | 17.62 | 16.54 | 12.01 | 14.06 | 6.98 | 4.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 315 | 74.81 | 18.45 | 15.24 | 12.37 | 14.17 | 6.59 | 8.03 | 0.00 |
| RANGE_FADE | kept | 1 | 64.90 | 23.00 | 14.00 | 3.00 | 15.00 | 10.00 | 4.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 1179 | 57.08 | 18.50 | 16.66 | 4.64 | 12.87 | 6.31 | 8.24 | 1.52 |
| SR_FLIP_RETEST | kept | 2508 | 71.82 | 20.88 | 16.60 | 5.26 | 13.48 | 5.92 | 8.94 | 1.90 |
| TREND_PULLBACK_EMA | filtered | 19 | 51.42 | 21.21 | 18.00 | 8.29 | 14.47 | 5.42 | 7.84 | 4.63 |
| TREND_PULLBACK_EMA | kept | 396 | 80.23 | 19.00 | 18.00 | 7.54 | 14.40 | 7.57 | 9.52 | 4.70 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 52.82 | 6.41 | 19.29 | 14.12 | 14.00 | 4.26 | 5.52 | 4.21 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 71.44 | 21.80 | 16.40 | 12.60 | 14.60 | 4.50 | 7.34 | 5.00 |
| WHALE_MOMENTUM | filtered | 33 | 51.59 | 18.21 | 9.52 | 11.55 | 12.94 | 5.11 | 10.00 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 67.00 | 25.00 | 8.00 | 15.00 | 14.00 | 5.00 | 10.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 403 | 57.10 | 0.00 | 0.00 | 1.54 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | **2.87** |
| DIVERGENCE_CONTINUATION | kept | 356 | 71.12 | 0.00 | 0.00 | 0.60 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | **0.65** |
| FAILED_AUCTION_RECLAIM | filtered | 366 | 54.39 | 0.00 | 0.00 | 0.56 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | **0.80** |
| FAILED_AUCTION_RECLAIM | kept | 1053 | 70.64 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | **0.06** |
| FUNDING_EXTREME_SIGNAL | filtered | 140 | 49.45 | 0.00 | 0.00 | 1.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.13** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 3 | 68.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 19 | 53.62 | 0.00 | 0.00 | 3.20 | 0.00 | 9.09 | 0.00 | 0.00 | 0.00 | **12.29** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 511 | 70.74 | 0.00 | 0.00 | 0.19 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | **0.25** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 70.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 17 | 54.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.45 | **4.45** |
| MEAN_REVERT | kept | 167 | 71.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 724 | 55.09 | 0.07 | 0.00 | 0.62 | 0.00 | 0.00 | 0.04 | 0.00 | 3.89 | **4.62** |
| MOVER_AVWAP_SCALP | kept | 713 | 76.24 | 0.02 | 0.00 | 0.26 | 0.00 | 0.00 | 0.03 | 0.00 | 0.01 | **0.32** |
| MOVER_TREND_PULLBACK | filtered | 1201 | 53.38 | 0.00 | 0.00 | 4.49 | 0.00 | 1.45 | 0.05 | 0.00 | 0.00 | **5.99** |
| MOVER_TREND_PULLBACK | kept | 10197 | 76.98 | 0.00 | 0.00 | 0.47 | 0.00 | 0.36 | 0.01 | 0.00 | 0.00 | **0.84** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 77.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 205 | 50.43 | 0.00 | 0.00 | 0.07 | 0.00 | 0.27 | 0.00 | 0.00 | 5.39 | **5.73** |
| QUIET_COMPRESSION_BREAK | kept | 315 | 74.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | **0.03** |
| RANGE_FADE | kept | 1 | 64.90 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| SR_FLIP_RETEST | filtered | 1179 | 57.08 | 0.02 | 0.00 | 1.11 | 0.00 | 1.39 | 0.07 | 0.00 | 0.16 | **2.75** |
| SR_FLIP_RETEST | kept | 2508 | 71.82 | 0.00 | 0.00 | 0.02 | 0.00 | 0.27 | 0.02 | 0.00 | 0.00 | **0.31** |
| TREND_PULLBACK_EMA | filtered | 19 | 51.42 | 0.00 | 0.00 | 5.89 | 0.00 | 5.68 | 0.00 | 0.00 | 0.00 | **11.57** |
| TREND_PULLBACK_EMA | kept | 396 | 80.23 | 0.00 | 0.00 | 0.39 | 0.00 | 0.05 | 0.05 | 0.00 | 0.00 | **0.49** |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 52.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 71.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 33 | 51.59 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | 0.91 | 0.00 | 0.00 | **1.64** |
| WHALE_MOMENTUM | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=872 (18.6%) | WOULD_LOSE=1745 | WOULD_EXPIRE=2075 | pending (awaiting window)=2378

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 180 | 3.9% | 89.1 | 11.5 | +0.43 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 400 | 11.2% | 139.8 | 83.3 | +0.14 | **KEEP** |
| context_floor:FUNDING_EXTREME_SIGNAL | 8 | 100.0% | 0.0 | 11.0 | -1.38 | **INSUFFICIENT_SAMPLE** |
| context_floor:QUIET_COMPRESSION_BREAK | 322 | 0.0% | 81.1 | 0.0 | +0.25 | **KEEP** |
| context_floor:RANGE_FADE | 22 | 0.0% | 31.7 | 0.0 | +1.44 | **KEEP** |
| context_floor:VOLUME_SURGE_BREAKOUT | 16 | 0.0% | 18.7 | 0.0 | +1.17 | **INSUFFICIENT_SAMPLE** |
| context_floor:WHALE_MOMENTUM | 67 | 0.0% | 23.1 | 0.0 | +0.34 | **KEEP** |
| dispatch_cooldown | 400 | 15.0% | 138.7 | 27.2 | +0.28 | **KEEP** |
| dispatch_staleness_v2 | 392 | 42.9% | 121.8 | 79.9 | +0.11 | **KEEP** |
| execution_component_floor | 3 | 0.0% | 3.9 | 0.0 | +1.29 | **INSUFFICIENT_SAMPLE** |
| level_still_in_play | 160 | 38.1% | 8.0 | 46.3 | -0.24 | **DROP** |
| min_confidence | 197 | 0.0% | 133.9 | 0.0 | +0.68 | **KEEP** |
| quiet_scalp_block | 364 | 6.6% | 114.1 | 26.7 | +0.24 | **KEEP** |
| setup_compat:regime_BREAKOUT_EXPANSION | 29 | 0.0% | 6.7 | 0.0 | +0.23 | **KEEP** |
| setup_compat:regime_CLEAN_RANGE | 364 | 36.0% | 300.3 | 18.3 | +0.77 | **KEEP** |
| setup_compat:regime_DIRTY_RANGE | 400 | 11.5% | 351.1 | 18.2 | +0.83 | **KEEP** |
| setup_compat:regime_STRONG_TREND | 116 | 4.3% | 84.2 | 3.1 | +0.70 | **KEEP** |
| setup_compat:regime_VOLATILE_UNSUITABLE | 348 | 13.8% | 187.1 | 82.1 | +0.30 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 34 | 41.2% | 6.7 | 9.1 | -0.07 | **TUNE** |
| shadow_unit:SHADOW_FUNDING_FADE | 312 | 34.6% | 171.8 | 76.2 | +0.31 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 308 | 29.9% | 187.8 | 123.9 | +0.21 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 250 | 22.0% | 174.2 | 134.7 | +0.16 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 99579 across 21 strategies; 2250 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 23462 | 149/23313/0 | 58% | +0.09 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.27R) |
| FAILED_AUCTION_RECLAIM | 15968 | 24/15944/0 | 55% | +0.06 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 15197 | 2/15195/0 | 46% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 9459 | 6/9453/0 | 44% | -0.12 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.45R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 7210 | 0/7210/0 | 49% | -0.10 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 3722 | 0/0/3722 | 41% | -0.03 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.03R) |
| LIQUIDITY_SWEEP_REVERSAL | 3524 | 9/3515/0 | 41% | -0.21 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| SHADOW_RANGE_FADE | 3469 | 0/0/3469 | 42% | +0.22 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.29R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.96R) |
| MOVER_AVWAP_SCALP | 3303 | 28/3275/0 | 33% | -0.39 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (+1.13R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| MEAN_REVERT | 3135 | 0/3135/0 | 80% | +0.58 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_FUNDING_FADE | 2960 | 0/0/2960 | 40% | -0.31 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.33R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.94R) |
| RANGE_FADE | 2310 | 0/2310/0 | 10% | -0.91 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| TREND_PULLBACK_EMA | 2187 | 2/2185/0 | 54% | -0.16 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.12R) |
| VOLUME_SURGE_BREAKOUT | 1638 | 11/1627/0 | 36% | -0.16 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 724 | 2/722/0 | 29% | -0.38 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.07R) | OVERLAP/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.29R) |
| WHALE_MOMENTUM | 623 | 0/623/0 | 48% | -0.18 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 306 | 0/0/306 | 46% | -0.21 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.15R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.80R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 10 | 1/9/0 | 30% | -0.43 | — | — |
| LIQUIDATION_REVERSAL | 6 | 0/6/0 | 0% | -1.29 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 20 | 25% / -0.53R | 20 | 40% / -0.28R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 61 | 49% / -0.22R | 61 | 52% / -0.08R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 2435 | 45% / -0.19R | 2435 | 48% / -0.10R | +0.09 | **ATR** |
| MOVER_AVWAP_SCALP | 210 | 40% / -0.18R | 210 | 42% / -0.09R | +0.09 | **ATR** |
| MEAN_REVERT | 278 | 59% / +0.14R | 278 | 55% / +0.22R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 514 | 51% / -0.16R | 514 | 54% / -0.08R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 589 | 46% / -0.13R | 589 | 51% / -0.06R | +0.07 | **ATR** |
| RANGE_FADE | 167 | 7% / -0.96R | 167 | 10% / -0.89R | +0.07 | **ATR** |
| WHALE_MOMENTUM | 36 | 42% / -0.17R | 36 | 39% / -0.24R | -0.07 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 50 | 40% / -0.06R | 50 | 42% / -0.11R | -0.05 | **FIXED** |
| MOVER_TREND_PULLBACK | 2661 | 56% / +0.01R | 2661 | 58% / +0.03R | +0.02 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2027 | 48% / -0.09R | 2027 | 47% / -0.08R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1006 | 45% / -0.12R | 1006 | 45% / -0.14R | -0.02 | **FIXED** |
| BREAKDOWN_SHORT | 12 | 25% / -0.32R | 12 | 25% / -0.29R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 7 | 43% / -0.18R | 7 | 43% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 1 | 0% / -1.29R | 1 | 0% / -0.36R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 2651 | 30% | -0.12R | 236 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 200 | 41% | -0.12R | 85 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 13 | 46% | +0.03R | 12 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 866 | 27% / -2.32R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 4 | 25% / -1.11R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 1457 | 37% / -0.55R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 678 | 33% / -0.74R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 22 | 18% / -1.88R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 341 | 27% / -3.09R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 313 | 34% / +0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 158 | 42% / -2.09R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 20 | 15% / -5.37R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 38 | 26% / -2.24R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 108 | 32% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 6 | 17% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 21 | 52% / +0.01R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 10 | 20% / -0.79R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| FUNDING_EXTREME_SIGNAL | context_floor:FUNDING_EXTREME_SIGNAL | 8 | 100.0% | -1.38 | **INSUFFICIENT_SAMPLE** |
| TREND_PULLBACK_EMA | quiet_scalp_block | 5 | 60.0% | -0.88 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 27 | 100.0% | -0.78 | **DROP** |
| DIVERGENCE_CONTINUATION | dispatch_staleness_v2 | 15 | 73.3% | -0.39 | **INSUFFICIENT_SAMPLE** |
| TREND_PULLBACK_EMA | dispatch_staleness_v2 | 24 | 87.5% | -0.27 | **DROP** |
| MOVER_TREND_PULLBACK | level_still_in_play | 88 | 38.6% | -0.25 | **DROP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 19 | 52.6% | -0.09 | **INSUFFICIENT_SAMPLE** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 34 | 41.2% | -0.07 | **TUNE** |
| MA_CROSS_TREND_SHIFT | setup_compat:regime_DIRTY_RANGE | 3 | 0.0% | +0.01 | **INSUFFICIENT_SAMPLE** |
| MOVER_AVWAP_SCALP | dispatch_cooldown | 62 | 9.7% | +0.03 | **TUNE** |
| TREND_PULLBACK_EMA | setup_compat:regime_VOLATILE_UNSUITABLE | 23 | 0.0% | +0.04 | **TUNE** |
| MEAN_REVERT | dispatch_staleness_v2 | 14 | 0.0% | +0.05 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | dispatch_cooldown | 8 | 0.0% | +0.09 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | level_still_in_play | 45 | 0.0% | +0.11 | **KEEP** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 299 | 41.8% | +0.11 | **KEEP** |
| SR_FLIP_RETEST | quiet_scalp_block | 140 | 15.0% | +0.13 | **KEEP** |
| FAILED_AUCTION_RECLAIM | context_floor:FAILED_AUCTION_RECLAIM | 400 | 11.2% | +0.14 | **KEEP** |
| MOVER_TREND_PULLBACK | dispatch_cooldown | 142 | 25.4% | +0.15 | **KEEP** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 250 | 22.0% | +0.16 | **KEEP** |
| DIVERGENCE_CONTINUATION | setup_compat:regime_VOLATILE_UNSUITABLE | 173 | 21.4% | +0.17 | **KEEP** |
| DIVERGENCE_CONTINUATION | dispatch_cooldown | 1 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 308 | 29.9% | +0.21 | **KEEP** |
| DIVERGENCE_CONTINUATION | min_confidence | 45 | 0.0% | +0.21 | **KEEP** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 61 | 0.0% | +0.21 | **KEEP** |
| DIVERGENCE_CONTINUATION | setup_compat:regime_BREAKOUT_EXPANSION | 29 | 0.0% | +0.23 | **KEEP** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 32 · alerting: **8** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 78/1417 disagreed (5.5%) (streak 121/6) (sustained 121 cycles)
- **ALERT** `sar_ledger_candles` — 377/379 unfetchable (99%); top cause: gap or duplicate bar in the 15m window; symbols: 1000BONKUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 1000XECUSDT +64 more (streak 126/6) (sustained 126 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 126/6) (sustained 126 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 2114x (gate reads 0x, withheld 0x — refusal dark); last MUSDT age=10220.9s (streak 23/6) (sustained 23 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.35R (bound 0.3) (streak 14/6) (sustained 14 cycles)
- **ALERT** `mean_revert_emission` — 593 detections since last emission (emitted_total=15) — and the blocked candidates measure +0.58R over n=3135, so the gating is COSTING us. Check gate rejections. (streak 11/6) (sustained 11 cycles)
- **ALERT** `tuned_variants` — 288 unexplained non-stamps (seen=3384 stamped=287 skipped=2809) (streak 14/6) (sustained 14 cycles)
- **ALERT** `auto_dispatch` — 12 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=12) (streak 99/3) (sustained 99 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 12 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=12) (streak 99/3) | 99 |
| btc_reference | ok | BTC ref 62970.50 | 0 |
| candle_coverage | ok | 90/97 symbols with ≥20 15m candles, 80/97 updated within 45m | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 126/6) | 126 |
| context_emission_policy | ok | output +140 / upstream +31 | 0 |
| dark_resolution | ok | 10 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.35R (bound 0.3) (streak 14/6) | 14 |
| emission_controller | ok | last cycle 1642s ago; live_overrides=21 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=10 wasted_promotions=0 pruned=0 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +295 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 593 detections since last emission (emitted_total=15) — and the blocked candidates measure +0.58R over n=3135, so the gating is COSTING us. Check gate rejections. (streak 11/6) | 11 |
| mean_revert_path | ok | output +44 / upstream +295 | 0 |
| mover_admission_metadata | ok | 851 symbols known, 150 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2829 rows held, 19654 evicted (sampled: execution:trigger_not_confirmed 400/7945, execution:overextended 400/7747, setup_compat:regime_WEAK_TREND 400/2125) | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | ok | emitted_total=1 context_blocked=81 | 0 |
| range_fade_path | ok | output +6 / upstream +295 | 0 |
| sar_alignment_crosscheck | violating | 78/1417 disagreed (5.5%) (streak 121/6) | 121 |
| sar_exit_shadow | ok | output +4 / upstream +295 | 0 |
| sar_ledger_candles | violating | 377/379 unfetchable (99%); top cause: gap or duplicate bar in the 15m window; symbols: 1000BONKUSDT, 1000PEPEUSDT, 1000RATSUSDT, 1000SHIBUSDT, 1000XECUSDT +64 more (streak 126/6) | 126 |
| sar_live_arms | ok | no open arms | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 779 records await one (2 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 3/12) | 3 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 2114x (gate reads 0x, withheld 0x — refusal dark); last MUSDT age=10220.9s (streak 23/6) | 23 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +113 / upstream +295 | 0 |
| suppression_audit | ok | output +295 / upstream +31 | 0 |
| tuned_variants | violating | 288 unexplained non-stamps (seen=3384 stamped=287 skipped=2809) (streak 14/6) | 14 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3418749`
- `Path funnel` emissions: `79`
- `Regime distribution` emissions: `79`
- `QUIET_SCALP_BLOCK` events: `435`
- `confidence_gate` events: `20556`
- `free_channel_post` events: `19`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **18**
- Total REST-fallback activations: **9**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 15 | 3330 | 6533 | 16086 | 0 |
| futures_liq | 2 | 2484 | 2484 | 6640 | 0 |
| futures_mover | 1 | 2637 | 2637 | 2637 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 9 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **19**

| Source | Count |
|---|---:|
| signal_close | 19 |

- By severity: HIGH=19

## Dependency readiness
- cvd: presence[present=469151] state[populated=469151] buckets[many=469151] sources[none] quality[none]
- funding_rate: presence[absent=37701, present=431450] state[empty=37701, populated=431450] buckets[few=431450, none=37701] sources[none] quality[none]
- liquidation_clusters: presence[absent=299015, present=170136] state[empty=299015, populated=170136] buckets[few=143057, none=299015, some=27079] sources[none] quality[none]
- oi_snapshot: presence[absent=33808, present=435343] state[empty=33808, populated=435343] buckets[few=252, many=435037, none=33808, some=54] sources[none] quality[none]
- order_book: presence[absent=126498, present=342653] state[populated=342653, unavailable=126498] buckets[few=342653, none=126498] sources[book_ticker=342653, unavailable=126498] quality[none=126498, top_of_book_only=342653]
- orderblocks: presence[absent=469151] state[empty=469151] buckets[none=469151] sources[not_implemented=469151] quality[none]
- recent_ticks: presence[present=469151] state[populated=469151] buckets[many=469151] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.5423312187194824` sec
- Median create→first breach: `3606.5111770629883` sec
- Median create→terminal: `3606.9588861465454` sec
- Median first breach→terminal: `1.4526948928833008` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 5.3}, "under_180s": {"count": 1, "pct": 5.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 19 | 19 | 0.0 | 42.1 | 0.0 | 0.0 | 0.1683 | 3606.5111770629883 | 3606.9588861465454 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 19182 | 142 | 10656 | 0.0 | 0.0 | None | None | 8526 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4057 | 21 | 3564 | 0.0 | 0.0 | None | None | 493 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `68`
- Gating Δ: `-37995`
- No-generation Δ: `-587102`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.8258, "current_avg_pnl": 0.1683, "current_win_rate": 0.0, "previous_avg_pnl": 0.9941, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 34, "geometry_changed_delta": 0, "geometry_preserved_delta": -1376, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 20, "geometry_changed_delta": 0, "geometry_preserved_delta": 396, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
