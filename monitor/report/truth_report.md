# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `3125` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 98 | 98 | 98 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11314 | 11314 | 9791 | 39 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 74742 | 74721 | 45 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 70017 | 70018 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 69552 | 66823 | 3175 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 70053 | 69349 | 760 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 69487 | 69306 | 208 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 58012 | 58025 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 70113 | 70135 | 22 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 70163 | 68769 | 2078 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 80455 | 87045 | 438 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 74770 | 64654 | 15736 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 69221 | 69222 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 70020 | 70044 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 69515 | 69462 | 81 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 70853 | 69592 | 1743 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 69226 | 69359 | 119 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 57563 | 54584 | 3336 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 57927 | 57601 | 405 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 74712 | 74730 | 10 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 58028 | 58037 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3103 | 3103 | 2871 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 625 | 625 | 229 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15975 | 15975 | 15738 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 37 | 37 | 5 | 7 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5170 | 5170 | 3788 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 956 | 956 | 260 | 28 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 38968 | 38968 | 16146 | 570 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 45 | 45 | 45 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 474 | 474 | 313 | 20 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4026 | 4026 | 3694 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 551 | 551 | 252 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1541 | 1541 | 1153 | 33 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 76 | 76 | 6 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=74721): breakout_not_found=40708, basic_filters_failed=21394, move_not_fresh=8200, breakout_stale=3240, retest_proximity_failed=946, volume_spike_missing=215, move_exhausted=11, missing_fvg_or_orderblock=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=70018): cls_disabled_merged_into_lsr=70018
- **EVAL::DIVERGENCE_CONTINUATION** (total=66823): cvd_divergence_failed=28285, basic_filters_failed=16267, h1_trend_not_aligned=13392, ema_alignment_reject=7937, retest_proximity_failed=653, missing_fvg_or_orderblock=289
- **EVAL::FAILED_AUCTION_RECLAIM** (total=69349): auction_not_detected=44636, basic_filters_failed=15697, reclaim_hold_failed=3493, tail_too_small=3210, regime_blocked=2293, rsi_reject=20
- **EVAL::FUNDING_EXTREME** (total=69306): funding_not_extreme=49621, basic_filters_failed=15982, missing_funding_rate=1674, ema_alignment_reject=1174, rsi_reject=310, cvd_divergence_failed=246, momentum_reject=242, missing_fvg_or_orderblock=57
- **EVAL::LIQUIDATION_REVERSAL** (total=58025): cascade_threshold_not_met=41199, basic_filters_failed=16079, cvd_divergence_failed=392, rsi_reject=340, missing_fvg_or_orderblock=12, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=70135): no_ma_cross=50948, basic_filters_failed=16279, ma_cross_cooldown=2113, ma_cross_htf_misaligned=795
- **EVAL::MEAN_REVERT** (total=68769): no_extension=58123, basic_filters_failed=10646
- **EVAL::MOVER_AVWAP_SCALP** (total=87045): no_avwap_tag=41059, basic_filters_failed=21565, no_mover_leg=14783, avwap_slope_against=6445, avwap_reclaim_no_volume=1964, no_avwap_reclaim=1215, anchor_too_recent=14
- **EVAL::MOVER_TREND_PULLBACK** (total=64654): basic_filters_failed=21481, no_reclaim=21342, mover_run_too_small=18957, no_pullback_tag=2874
- **EVAL::OPENING_RANGE_BREAKOUT** (total=69222): feature_disabled=69222
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=70044): regime_blocked=35887, breakout_not_found=24333, basic_filters_failed=6275, adx_reject=3461, ema_alignment_reject=88
- **EVAL::QUIET_COMPRESSION_BREAK** (total=69462): regime_blocked=36298, compression_not_detected=20395, basic_filters_failed=9416, breakout_not_detected=3144, volume_confirmation_failed=205, missing_fvg_or_orderblock=3, rsi_reject=1
- **EVAL::RANGE_FADE** (total=69592): no_range_edge=58943, basic_filters_failed=10649
- **EVAL::SR_FLIP_RETEST** (total=69359): flip_close_not_confirmed=44842, basic_filters_failed=15685, retest_out_of_zone=2408, regime_blocked=2282, h1_break_not_confirmed=1752, long_break_volume_thin=1404, reclaim_hold_failed=677, long_acceptance_not_held=97, ema_alignment_reject=74, wick_quality_failed=62, whipsaw_flip=46, missing_fvg_or_orderblock=30
- **EVAL::STANDARD** (total=54584): momentum_reject=16233, adx_reject=14310, basic_filters_failed=8162, sweeps_not_detected=6528, ema_alignment_reject=5229, macd_reject=3415, htf_poi_unanchored=531, rsi_reject=86, invalid_sl_geometry=52, mtf_reject=38
- **EVAL::TREND_PULLBACK** (total=57601): h1_trend_not_aligned=14848, h1_pullback_not_confirmed=14818, ema_alignment_reject=9099, basic_filters_failed=7373, ema_not_tested_prev=3866, no_ema_reclaim_close=3655, body_conviction_fail=1568, rsi_reject=1093, prev_already_below_emas=510, no_prev_low_break=248, no_prev_high_break=217, prev_already_above_emas=192, momentum_flat=67, ema21_not_tagged=40, missing_fvg_or_orderblock=6, momentum_reject=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=74730): breakout_not_found=42251, basic_filters_failed=21392, move_not_fresh=6793, breakout_stale=2683, retest_proximity_failed=1322, volume_spike_missing=257, missing_fvg_or_orderblock=20, move_exhausted=12
- **EVAL::WHALE_MOMENTUM** (total=58037): momentum_reject=47450, recent_ticks_insufficient=6740, basic_filters_failed=3847

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=37): execution:overextended=37
- **DIVERGENCE_CONTINUATION** (total=105): setup_compat:regime_VOLATILE_UNSUITABLE=75, setup_compat:regime_BREAKOUT_EXPANSION=30
- **FAILED_AUCTION_RECLAIM** (total=1687): setup_compat:regime_STRONG_TREND=1184, execution:overextended=378, context_floor=112, setup_compat:regime_VOLATILE_UNSUITABLE=13
- **FUNDING_EXTREME_SIGNAL** (total=506): execution:trigger_not_confirmed=493, context_floor=13
- **LIQUIDATION_REVERSAL** (total=7): execution:trigger_not_confirmed=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=5706): setup_compat:regime_STRONG_TREND=3011, execution:overextended=1419, execution:trigger_not_confirmed=1276
- **MA_CROSS_TREND_SHIFT** (total=23): execution:overextended=11, setup_compat:regime_CLEAN_RANGE=5, execution:trigger_not_confirmed=3, setup_compat:regime_DIRTY_RANGE=3, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=4166): setup_compat:regime_STRONG_TREND=2157, setup_compat:regime_WEAK_TREND=1441, execution:overextended=552, entry_quality=16
- **MOVER_AVWAP_SCALP** (total=812): execution:overextended=363, execution:trigger_not_confirmed=276, entry_quality=173
- **MOVER_TREND_PULLBACK** (total=18111): execution:trigger_not_confirmed=10099, execution:overextended=4303, entry_quality=3709
- **RANGE_FADE** (total=3310): setup_compat:regime_STRONG_TREND=1554, setup_compat:regime_WEAK_TREND=1018, execution:overextended=461, setup_compat:regime_VOLATILE_UNSUITABLE=267, context_edge=9, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=1304): setup_compat:regime_CLEAN_RANGE=886, setup_compat:regime_DIRTY_RANGE=296, entry_quality=100, setup_compat:regime_VOLATILE_UNSUITABLE=22
- **VOLUME_SURGE_BREAKOUT** (total=8): execution:overextended=8

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 130410 | 34.2% |
| TRENDING_DOWN | 106519 | 27.9% |
| TRENDING_UP | 74912 | 19.6% |
| QUIET | 55405 | 14.5% |
| VOLATILE | 14566 | 3.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **277**
- Average confidence gap to threshold: **8.97** (samples=277) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XLMUSDT=41, XMRUSDT=40, BTCUSDT=31, BNBUSDT=28, TAOUSDT=24, ENAUSDT=16, 1000PEPEUSDT=12, ONDOUSDT=12, SUIUSDT=10, WLDUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 166 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 358 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 9 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 14 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 92 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 17 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 16 |
| MEAN_REVERT | filtered | min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 43 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 125 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 13 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 267 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1972 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 156 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 8212 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 65 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 21 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 63 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 25 |
| SR_FLIP_RETEST | filtered | min_confidence | 14 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 71 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 7 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 185 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 28 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 42 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 171 | 55.26 | 62.99 | 7.73 | 20.98 | 19.62 | 18.20 | 1.00 | 14.36 |
| DIVERGENCE_CONTINUATION | kept | 358 | 69.13 | 65.00 | -4.13 | 21.12 | 19.84 | 18.19 | 1.49 | 2.06 |
| FAILED_AUCTION_RECLAIM | filtered | 9 | 52.86 | 65.00 | 12.14 | 21.97 | 20.00 | 20.00 | 2.33 | 2.67 |
| FUNDING_EXTREME_SIGNAL | filtered | 14 | 40.68 | 63.57 | 22.89 | 20.94 | 15.24 | 16.45 | 3.36 | 14.92 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 101 | 46.69 | 64.60 | 17.91 | 19.98 | 18.62 | 19.34 | 1.10 | 14.55 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 69.43 | 65.00 | -4.43 | 21.36 | 18.04 | 17.49 | 2.29 | 3.04 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 56.05 | 61.00 | 4.95 | 20.35 | 17.90 | 15.80 | 0.00 | 15.95 |
| MA_CROSS_TREND_SHIFT | kept | 16 | 71.37 | 65.00 | -6.37 | 20.52 | 16.39 | 15.80 | 0.00 | 1.22 |
| MEAN_REVERT | filtered | 2 | 64.50 | 65.00 | 0.50 | 19.50 | 15.80 | 14.20 | 0.00 | 2.10 |
| MEAN_REVERT | kept | 43 | 69.34 | 65.00 | -4.34 | 20.25 | 15.90 | 14.46 | 0.00 | 1.61 |
| MOVER_AVWAP_SCALP | filtered | 139 | 58.74 | 59.23 | 0.49 | 20.18 | 14.51 | 15.80 | 4.86 | 14.97 |
| MOVER_AVWAP_SCALP | kept | 267 | 82.19 | 65.00 | -17.19 | 20.40 | 14.81 | 15.80 | 4.55 | 4.10 |
| MOVER_TREND_PULLBACK | filtered | 2128 | 58.02 | 64.10 | 6.08 | 20.53 | 18.66 | 15.80 | 3.85 | 16.82 |
| MOVER_TREND_PULLBACK | kept | 8212 | 76.12 | 65.00 | -11.12 | 20.52 | 18.61 | 15.80 | 4.16 | 2.14 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 1 | 52.50 | 61.00 | 8.50 | 20.90 | 20.00 | 18.40 | 4.50 | 26.00 |
| QUIET_COMPRESSION_BREAK | filtered | 86 | 51.12 | 65.00 | 13.88 | 21.45 | 19.40 | 20.00 | 0.00 | 14.94 |
| QUIET_COMPRESSION_BREAK | kept | 63 | 71.49 | 65.00 | -6.49 | 21.32 | 19.80 | 20.00 | 0.00 | 5.64 |
| SR_FLIP_RETEST | filtered | 39 | 55.13 | 63.31 | 8.18 | 22.28 | 20.00 | 16.24 | 2.36 | 12.05 |
| SR_FLIP_RETEST | kept | 71 | 71.68 | 65.00 | -6.68 | 21.43 | 20.00 | 18.63 | 2.35 | 1.44 |
| TREND_PULLBACK_EMA | filtered | 12 | 59.73 | 65.00 | 5.27 | 20.82 | 19.62 | 16.96 | 4.58 | 18.15 |
| TREND_PULLBACK_EMA | kept | 185 | 80.04 | 65.00 | -15.04 | 20.80 | 19.86 | 18.47 | 4.82 | -0.47 |
| VOLUME_SURGE_BREAKOUT | filtered | 28 | 54.31 | 61.00 | 6.69 | 20.58 | 17.15 | 20.00 | 3.50 | 5.21 |
| VOLUME_SURGE_BREAKOUT | kept | 42 | 70.71 | 65.00 | -5.71 | 23.51 | 18.74 | 20.00 | 3.55 | 2.86 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 171 | 55.26 | 21.07 | 16.60 | 5.19 | 12.18 | 5.28 | 8.28 | 1.00 |
| DIVERGENCE_CONTINUATION | kept | 358 | 69.13 | 22.92 | 17.13 | 4.59 | 12.30 | 4.80 | 8.79 | 1.49 |
| FAILED_AUCTION_RECLAIM | filtered | 9 | 52.86 | 24.11 | 14.00 | 5.67 | 15.33 | 5.00 | 4.08 | 2.33 |
| FUNDING_EXTREME_SIGNAL | filtered | 14 | 40.68 | 25.00 | 15.71 | 3.21 | 10.71 | 8.39 | 3.14 | 3.36 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 101 | 46.69 | 20.86 | 15.27 | 9.27 | 13.86 | 5.17 | 5.37 | 1.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 69.43 | 24.88 | 15.65 | 5.29 | 11.12 | 6.12 | 7.11 | 2.29 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 56.05 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 16 | 71.37 | 18.50 | 14.00 | 10.88 | 14.19 | 5.66 | 9.38 | 0.00 |
| MEAN_REVERT | filtered | 2 | 64.50 | 17.00 | 18.00 | 6.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 43 | 69.34 | 24.81 | 14.74 | 6.14 | 13.00 | 5.00 | 7.33 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 139 | 58.74 | 18.77 | 18.00 | 11.28 | 13.47 | 5.40 | 6.35 | 4.86 |
| MOVER_AVWAP_SCALP | kept | 267 | 82.19 | 20.15 | 18.00 | 14.11 | 13.81 | 7.58 | 8.16 | 4.55 |
| MOVER_TREND_PULLBACK | filtered | 2128 | 58.02 | 17.92 | 18.06 | 7.82 | 12.17 | 6.15 | 9.27 | 3.85 |
| MOVER_TREND_PULLBACK | kept | 8212 | 76.12 | 19.84 | 18.01 | 7.84 | 12.24 | 6.78 | 9.45 | 4.16 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 1 | 52.50 | 17.00 | 18.00 | 15.00 | 11.00 | 5.00 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 86 | 51.12 | 18.86 | 17.02 | 10.43 | 14.00 | 7.55 | 3.96 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 63 | 71.49 | 18.52 | 17.81 | 10.90 | 14.05 | 8.13 | 7.85 | 0.00 |
| SR_FLIP_RETEST | filtered | 39 | 55.13 | 23.77 | 11.59 | 4.15 | 12.49 | 5.36 | 7.46 | 2.36 |
| SR_FLIP_RETEST | kept | 71 | 71.68 | 23.76 | 18.00 | 4.18 | 12.31 | 5.04 | 8.04 | 2.35 |
| TREND_PULLBACK_EMA | filtered | 12 | 59.73 | 17.00 | 18.00 | 9.00 | 15.25 | 5.00 | 9.04 | 4.58 |
| TREND_PULLBACK_EMA | kept | 185 | 80.04 | 19.84 | 18.00 | 7.61 | 14.25 | 7.42 | 9.08 | 4.82 |
| VOLUME_SURGE_BREAKOUT | filtered | 28 | 54.31 | 17.00 | 18.00 | 14.14 | 12.93 | 5.00 | 3.94 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 42 | 70.71 | 17.19 | 17.90 | 13.29 | 13.86 | 3.69 | 4.45 | 3.55 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 171 | 55.26 | 0.00 | 0.00 | 0.53 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | **0.78** |
| DIVERGENCE_CONTINUATION | kept | 358 | 69.13 | 0.00 | 0.00 | 0.89 | 0.00 | 0.44 | 0.02 | 0.00 | 0.00 | **1.35** |
| FAILED_AUCTION_RECLAIM | filtered | 9 | 52.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 14 | 40.68 | 0.00 | 0.00 | 9.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.77** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 101 | 46.69 | 0.00 | 0.00 | 2.39 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **2.75** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 69.43 | 0.00 | 0.00 | 4.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.52** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 56.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 16 | 71.37 | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.30** |
| MEAN_REVERT | filtered | 2 | 64.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 43 | 69.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 139 | 58.74 | 0.00 | 0.00 | 0.33 | 0.00 | 2.43 | 0.17 | 0.00 | 1.15 | **4.08** |
| MOVER_AVWAP_SCALP | kept | 267 | 82.19 | 0.56 | 0.00 | 0.32 | 0.00 | 0.75 | 0.25 | 0.00 | 0.04 | **1.92** |
| MOVER_TREND_PULLBACK | filtered | 2128 | 58.02 | 0.27 | 0.00 | 1.00 | 0.00 | 1.01 | 0.82 | 0.00 | 0.01 | **3.11** |
| MOVER_TREND_PULLBACK | kept | 8212 | 76.12 | 0.01 | 0.00 | 0.65 | 0.00 | 0.47 | 0.12 | 0.00 | 0.00 | **1.25** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 1 | 52.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 86 | 51.12 | 0.00 | 0.00 | 0.00 | 0.00 | 1.25 | 0.42 | 0.00 | 3.71 | **5.38** |
| QUIET_COMPRESSION_BREAK | kept | 63 | 71.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.65 | 0.00 | 0.00 | 0.00 | **0.65** |
| SR_FLIP_RETEST | filtered | 39 | 55.13 | 0.00 | 0.00 | 5.54 | 0.00 | 0.00 | 0.00 | 0.00 | 1.54 | **7.08** |
| SR_FLIP_RETEST | kept | 71 | 71.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 12 | 59.73 | 0.00 | 0.00 | 3.60 | 0.00 | 8.20 | 0.00 | 0.00 | 0.00 | **11.80** |
| TREND_PULLBACK_EMA | kept | 185 | 80.04 | 0.00 | 0.00 | 0.27 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **0.63** |
| VOLUME_SURGE_BREAKOUT | filtered | 28 | 54.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| VOLUME_SURGE_BREAKOUT | kept | 42 | 70.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **176370 held of 752719 seen** across 21 strategies; 3990 cells past the sample floor; **2103 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47536 | 613/46923/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.35R) |
| MOVER_AVWAP_SCALP | 23276 | 178/23098/0 | 44% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 13687 | 163/13524/0 | 45% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13210 | 156/13054/0 | 39% | -0.26 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11685 | 61/11624/0 | 37% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9832 | 110/9722/0 | 37% | -0.44 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| SHADOW_MEAN_REVERT | 7979 | 0/0/7979 | 43% | -0.08 | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (+0.67R) | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.90R) |
| QUIET_COMPRESSION_BREAK | 7915 | 438/7477/0 | 47% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_RANGE_FADE | 7486 | 0/0/7486 | 36% | -0.13 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.32R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_FUNDING_FADE | 6876 | 0/0/6876 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.00R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 5253 | 17/5236/0 | 46% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5073 | 68/5005/0 | 35% | -0.35 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| FUNDING_EXTREME_SIGNAL | 3841 | 2/3839/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3747 | 0/3747/0 | 30% | -0.36 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2212 | 6/2206/0 | 41% | -0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1606 | 0/0/1606 | 53% | -0.08 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.56R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 192 | 32/160/0 | 43% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 339 | 27% / -0.57R | 339 | 53% / -0.09R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1086 | 37% / -0.39R | 1086 | 50% / -0.09R | +0.30 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1517 | 42% / -0.37R | 1517 | 56% / -0.12R | +0.25 | **ATR** |
| SR_FLIP_RETEST | 533 | 43% / -0.33R | 533 | 47% / -0.18R | +0.15 | **ATR** |
| MA_CROSS_TREND_SHIFT | 57 | 42% / -0.20R | 57 | 46% / -0.08R | +0.12 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 201 | 37% / -0.18R | 201 | 48% / -0.05R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2411 | 45% / -0.17R | 2411 | 51% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8684 | 49% / -0.13R | 8684 | 54% / -0.02R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1380 | 42% / -0.21R | 1380 | 44% / -0.11R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 118 | 39% / -0.10R | 118 | 47% / -0.00R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1615 | 47% / -0.13R | 1615 | 53% / -0.06R | +0.07 | **ATR** |
| MEAN_REVERT | 406 | 47% / -0.14R | 406 | 46% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1391 | 47% / -0.13R | 1391 | 47% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11619 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2411 | 49% | -0.04R | 233 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 126 | 49% | -0.05R | 67 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1762 | 39% / -0.14R | +0.87 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1426 | 32% / -0.26R | +0.80 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2962 | 35% / -0.23R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10617 | 36% / -0.19R | +0.34 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1886 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1337 | 36% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1150 | 32% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 296 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 444 | 32% / -0.17R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 338 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 87 | 44% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 475 | 32% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 92 | 27% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×183]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 128/6) (sustained 128 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 128/6) (sustained 128 cycles)
- **ALERT** `tuned_variants` — 152 non-stamps — atr_arm_uncomputable=152 (seen=6811 stamped=956 skipped=5703) (streak 128/6) (sustained 128 cycles)
- **ALERT** `auto_dispatch` — 21 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=21) (streak 118/3) (sustained 118 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 14551750 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 16 arms current, none stalled; covering 2032/2032 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 4/6) | 4 |
| atr_trail_live_arms | ok | 32 arms current, none stalled; covering 1036/1036 signals (100%) | 0 |
| auto_dispatch | violating | 21 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=21) (streak 118/3) | 118 |
| binance_ip_weight | ok | peak 260/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 75437.70 | 0 |
| candle_coverage | ok | 89/89 symbols with ≥20 15m candles, 89/89 updated within 45m [fresh=89; 74 Tier-1 futures + 15 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 521 dup bars, 0 undedupable; ws 0 out-of-order, 124 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +44 / upstream +29 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1640/1659 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 4 of 172 open dark rows are not being advanced (worst: MARSCOINUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 47/120) | 47 |
| dark_sar_arms | ok | no open arms; covering 1635/1654 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4112084 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 128/6) | 128 |
| emission_controller | ok | last cycle 786s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×183]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 128/6) | 128 |
| entry_quality_effective | ok | 11831 evaluated, 3757 suppressed, 4585 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,312 reads/day of 50,000 [engine 1,287, signing 25]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 2 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +598 | 0 |
| indicator_cache_key | ok | 46311 frozen value(s) avoided; 270792 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.36R over n=5005 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +58 / upstream +598 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 15 held, 15 with scan counts, 15 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2142 rows held, 3391349 evicted (sampled: execution:trigger_not_confirmed 286/1197811, execution:overextended 286/1060713, setup_compat:regime_STRONG_TREND 286/579339) | 0 |
| price_action_lane | ok | 297117 evaluated, 414 emitted; layer1 414 stamped / 0 blind; cooldown=41795, delta_opposed=27291, no_footprint=126323, no_opposing_target=516, no_sweep=76098, rr_below_floor=24680 | 0 |
| promoted_pair_integrity | ok | 15/15 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.19R over n=2206 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +58 / upstream +598 | 0 |
| sar_alignment_crosscheck | ok | 521/11504 disagreed (4.5%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +598 | 0 |
| sar_hold_arm | ok | 1863 held arms settled, 137 unscored, 31 still walking (29 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 10/77 unfetchable (13%); top cause: gap or duplicate bar in the 15m window; symbols: BEAMXUSDT, ENAUSDT | 0 |
| sar_live_arms | ok | 31 arms current, none stalled; covering 1035/1035 signals (100%) | 0 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 477 records await one (67 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 54.95s, worst 168.66s over 3392 lifetime cycles; lifetime 126 over 60s, 14 over 120s (plus 2/1 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.75s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 177469 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 12s ago (0.87s to run, worst 147.21s), 404 overrun(s) of 2894 cycles, TTL 900s; slowest signals=0.27s, data_intake=0.26s, engine_state=0.07s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +39 / upstream +598 | 0 |
| structural_snap | ok | 6000/6000 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=671) | 0 |
| structural_veto_lane | ok | 1321 stamped; 0 with no readable level book, 28 with clear air ahead, 1050 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +598 / upstream +29 | 0 |
| tuned_variants | violating | 152 non-stamps — atr_arm_uncomputable=152 (seen=6811 stamped=956 skipped=5703) (streak 128/6) | 128 |
| unlock_shorts | ok | 14 open, 43 scheduled, calendar 6.5h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 7 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2137508`
- `Path funnel` emissions: `44`
- `Regime distribution` emissions: `44`
- `QUIET_SCALP_BLOCK` events: `277`
- `confidence_gate` events: `12006`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **196**
- Total REST-fallback activations: **28**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 34 | 13219 | 35143 | 42324 | 0 |
| futures_aggtrade | 83 | 17005 | 64965 | 85968 | 0 |
| futures_depth | 9 | 11594 | 21171 | 26310 | 0 |
| futures_liq | 7 | 5179 | 11574 | 23610 | 0 |
| futures_mover | 63 | 20435 | 49215 | 106856 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 28 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=286709] state[populated=286709] buckets[many=286585, some=124] sources[none] quality[none]
- funding_rate: presence[absent=38414, present=248295] state[empty=38414, populated=248295] buckets[few=248295, none=38414] sources[none] quality[none]
- liquidation_clusters: presence[absent=168912, present=117797] state[empty=168912, populated=117797] buckets[few=100441, none=168912, some=17356] sources[none] quality[none]
- oi_snapshot: presence[absent=37840, present=248869] state[empty=37840, populated=248869] buckets[many=248869, none=37840] sources[none] quality[none]
- order_book: presence[absent=93930, present=192779] state[populated=192779, unavailable=93930] buckets[few=192779, none=93930] sources[book_ticker=192779, unavailable=93930] quality[none=93930, top_of_book_only=192779]
- orderblocks: presence[absent=286709] state[empty=286709] buckets[none=286709] sources[measured_dark=286709] quality[none]
- recent_ticks: presence[present=286709] state[populated=286709] buckets[many=286709] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.8756959438323975` sec
- Median create→first breach: `7581.755737066269` sec
- Median create→terminal: `7581.954890966415` sec
- Median first breach→terminal: `6.29425048828125e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.8375341243513422 | 1.2472234371592852 | 0.700771349841453 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 3.4008594769268132 | 3.0 | 1.1336198256422712 | 1 | 0 |
| MEAN_REVERT | 1 | 1 | 1.5281820587456991 | 2.139643896722489 | 0.7142226148409889 | 0 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 4.2100818337589985 | 3.0 | 1.4033606112529995 | 2 | 1 |
| MOVER_TREND_PULLBACK | 25 | 25 | 3.908250215177612 | 3.0 | 1.367881896263346 | 19 | 5 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.067400198458145 | 1.0806112398609444 | 0.9167056683643423 | 0 | 4 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.4007524156023488 | 1.5720100042238672 | 0.88498245674343 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1656 | 7151.217169523239 | 7151.217213869095 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 6.0261 | 11873.013236045837 | 11875.560389995575 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.1953 | 9145.127572059631 | 9146.86015510559 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -2.9774 | 11113.693280935287 | 11113.69335103035 |
| MOVER_TREND_PULLBACK | 25 | 25 | 44.0 | 32.0 | 44.0 | 0.0 | 0.5862 | 2425.3354148864746 | 2425.3354358673096 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 28.6 | 28.6 | 28.6 | 0.0 | 0.4657 | 28863.927053928375 | 28863.927068948746 |
| TREND_PULLBACK_EMA | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 0.7959 | 3239.037038564682 | 3239.8122034072876 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 551 | 5 | 252 | 0.0 | 0.0 | None | None | 299 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1541 | 33 | 1153 | 50.0 | 0.0 | 3239.037038564682 | 3239.8122034072876 | 388 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `259`
- Gating Δ: `-6038`
- No-generation Δ: `-122028`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0346, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.0346, "previous_win_rate": 25.0, "win_rate_delta": -25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -2.5195, "current_avg_pnl": -2.9774, "current_win_rate": 0.0, "previous_avg_pnl": -0.4579, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.2179, "current_avg_pnl": 0.5862, "current_win_rate": 44.0, "previous_avg_pnl": 0.3683, "previous_win_rate": 33.3, "win_rate_delta": 10.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.1479, "current_avg_pnl": 0.4657, "current_win_rate": 28.6, "previous_avg_pnl": 0.3178, "previous_win_rate": 22.2, "win_rate_delta": 6.4}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 221, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": -93, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -16417.31, "median_terminal_delta_sec": -16417.18, "sl_rate_delta": 0.0, "win_rate_delta": -50.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
