# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `462` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 51 | 51 | 51 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11249 | 11249 | 10118 | 14 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 63855 | 63866 | 17 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 72503 | 72503 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 72044 | 69254 | 3234 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 72535 | 71493 | 1156 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 71970 | 71860 | 132 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 60371 | 60386 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 72652 | 72692 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 72707 | 70397 | 3436 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 68734 | 74533 | 615 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 63887 | 59228 | 9442 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 71407 | 71407 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 72507 | 72529 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 72003 | 71840 | 203 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 73841 | 70689 | 4137 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 71413 | 71886 | 71 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 59731 | 56602 | 3664 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 60274 | 59851 | 506 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 63818 | 63841 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 60392 | 60405 | 4 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3953 | 3953 | 3442 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 519 | 519 | 166 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20110 | 20110 | 19889 | 4 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 11 | 11 | 2 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7833 | 7833 | 6901 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1141 | 1141 | 166 | 31 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 24051 | 24051 | 11608 | 264 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 837 | 837 | 623 | 35 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 7441 | 7441 | 5601 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 238 | 238 | 65 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1843 | 1843 | 1499 | 21 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 32 | 32 | 4 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 66 | 66 | 7 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=63866): basic_filters_failed=27724, breakout_not_found=24318, move_not_fresh=8600, breakout_stale=2303, retest_proximity_failed=801, volume_spike_missing=94, move_exhausted=20, missing_fvg_or_orderblock=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=72503): cls_disabled_merged_into_lsr=72503
- **EVAL::DIVERGENCE_CONTINUATION** (total=69254): basic_filters_failed=27306, cvd_divergence_failed=25292, h1_trend_not_aligned=7561, ema_alignment_reject=6947, retest_proximity_failed=1406, missing_fvg_or_orderblock=742
- **EVAL::FAILED_AUCTION_RECLAIM** (total=71493): auction_not_detected=37088, basic_filters_failed=26810, reclaim_hold_failed=3527, tail_too_small=2556, regime_blocked=1489, rsi_reject=23
- **EVAL::FUNDING_EXTREME** (total=71860): funding_not_extreme=41250, basic_filters_failed=15920, missing_funding_rate=12291, ema_alignment_reject=1297, rsi_reject=903, cvd_divergence_failed=101, momentum_reject=88, missing_fvg_or_orderblock=10
- **EVAL::LIQUIDATION_REVERSAL** (total=60386): cascade_threshold_not_met=32934, basic_filters_failed=26835, cvd_divergence_failed=396, rsi_reject=176, volume_spike_missing=29, missing_fvg_or_orderblock=16
- **EVAL::MA_CROSS_TREND_SHIFT** (total=72692): no_ma_cross=44772, basic_filters_failed=27342, ma_cross_cooldown=336, ma_cross_htf_misaligned=242
- **EVAL::MEAN_REVERT** (total=70397): no_extension=60983, basic_filters_failed=9414
- **EVAL::MOVER_AVWAP_SCALP** (total=74533): basic_filters_failed=28106, no_avwap_tag=26951, no_mover_leg=13114, avwap_slope_against=3447, avwap_reclaim_no_volume=1811, no_avwap_reclaim=945, anchor_too_recent=159
- **EVAL::MOVER_TREND_PULLBACK** (total=59229): basic_filters_failed=27922, mover_run_too_small=21424, no_reclaim=8282, no_pullback_tag=1601
- **EVAL::OPENING_RANGE_BREAKOUT** (total=71407): feature_disabled=71407
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=72529): regime_blocked=54474, breakout_not_found=9685, basic_filters_failed=6997, adx_reject=1345, ema_alignment_reject=28
- **EVAL::QUIET_COMPRESSION_BREAK** (total=71840): compression_not_detected=25256, basic_filters_failed=19786, regime_blocked=19441, breakout_not_detected=6969, volume_confirmation_failed=385, rsi_reject=2, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=70689): no_range_edge=61269, basic_filters_failed=9420
- **EVAL::SR_FLIP_RETEST** (total=71886): flip_close_not_confirmed=37480, basic_filters_failed=26746, retest_out_of_zone=1914, long_break_volume_thin=1515, h1_break_not_confirmed=1477, regime_blocked=1476, reclaim_hold_failed=618, whipsaw_flip=272, ema_alignment_reject=180, long_acceptance_not_held=106, wick_quality_failed=92, missing_fvg_or_orderblock=10
- **EVAL::STANDARD** (total=56602): adx_reject=16372, momentum_reject=16351, macd_reject=7240, basic_filters_failed=6772, sweeps_not_detected=6182, ema_alignment_reject=2097, htf_poi_unanchored=1467, rsi_reject=66, invalid_sl_geometry=53, mtf_reject=2
- **EVAL::TREND_PULLBACK** (total=59851): basic_filters_failed=14105, h1_trend_not_aligned=12869, h1_pullback_not_confirmed=12564, ema_alignment_reject=6752, ema_not_tested_prev=3949, body_conviction_fail=3044, no_ema_reclaim_close=3020, rsi_reject=2030, prev_already_below_emas=813, no_prev_low_break=302, momentum_flat=173, prev_already_above_emas=99, no_prev_high_break=42, ema21_not_tagged=31, missing_fvg_or_orderblock=30, momentum_reject=28
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=63841): breakout_not_found=31103, basic_filters_failed=27720, move_not_fresh=2321, breakout_stale=1951, retest_proximity_failed=580, volume_spike_missing=111, move_exhausted=55
- **EVAL::WHALE_MOMENTUM** (total=60405): momentum_reject=48603, recent_ticks_insufficient=6305, basic_filters_failed=5497

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=2): execution:overextended=2
- **DIVERGENCE_CONTINUATION** (total=241): setup_compat:regime_VOLATILE_UNSUITABLE=231, setup_compat:regime_BREAKOUT_EXPANSION=10
- **FAILED_AUCTION_RECLAIM** (total=1349): setup_compat:regime_STRONG_TREND=936, execution:overextended=289, context_floor=96, setup_compat:regime_VOLATILE_UNSUITABLE=28
- **FUNDING_EXTREME_SIGNAL** (total=400): execution:trigger_not_confirmed=389, context_floor=11
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=5922): execution:trigger_not_confirmed=4561, execution:overextended=781, setup_compat:regime_STRONG_TREND=580
- **MA_CROSS_TREND_SHIFT** (total=11): setup_compat:regime_DIRTY_RANGE=6, execution:trigger_not_confirmed=3, setup_compat:regime_CLEAN_RANGE=1, execution:overextended=1
- **MEAN_REVERT** (total=5816): execution:overextended=2711, setup_compat:regime_STRONG_TREND=2246, setup_compat:regime_WEAK_TREND=834, entry_quality=25
- **MOVER_AVWAP_SCALP** (total=933): execution:overextended=607, entry_quality=222, execution:trigger_not_confirmed=104
- **MOVER_TREND_PULLBACK** (total=12639): execution:trigger_not_confirmed=6477, execution:overextended=4316, entry_quality=1846
- **QUIET_COMPRESSION_BREAK** (total=49): execution:trigger_not_confirmed=49
- **RANGE_FADE** (total=3137): setup_compat:regime_STRONG_TREND=1208, setup_compat:regime_WEAK_TREND=841, execution:overextended=641, setup_compat:regime_VOLATILE_UNSUITABLE=418, context_edge=29
- **TREND_PULLBACK_EMA** (total=1858): setup_compat:regime_CLEAN_RANGE=1147, setup_compat:regime_DIRTY_RANGE=596, entry_quality=104, setup_compat:regime_VOLATILE_UNSUITABLE=11
- **VOLUME_SURGE_BREAKOUT** (total=5): execution:overextended=5
- **WHALE_MOMENTUM** (total=59): execution:trigger_not_confirmed=59

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 231685 | 52.0% |
| TRENDING_DOWN | 80986 | 18.2% |
| QUIET | 71444 | 16.0% |
| TRENDING_UP | 52768 | 11.8% |
| VOLATILE | 8572 | 1.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **147**
- Average confidence gap to threshold: **15.41** (samples=147) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=26, INJUSDT=17, AAVEUSDT=17, ETHFIUSDT=12, LINKUSDT=10, TRXUSDT=9, XRPUSDT=9, BNBUSDT=9, BTCUSDT=7, TRUMPUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 110 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 14 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 64 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 75 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 22 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 62 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 32 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 102 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 128 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 8 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 316 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2352 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 39 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4085 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 50 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 5 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 124 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 7 |
| SR_FLIP_RETEST | filtered | min_confidence | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 23 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 71 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 54 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 21 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 8 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 124 | 49.99 | 64.47 | 14.48 | 21.29 | 19.33 | 17.70 | 0.35 | 17.38 |
| DIVERGENCE_CONTINUATION | kept | 64 | 68.07 | 65.00 | -3.07 | 21.67 | 19.62 | 18.12 | 0.44 | 0.42 |
| FAILED_AUCTION_RECLAIM | filtered | 98 | 48.71 | 64.54 | 15.83 | 20.93 | 19.96 | 20.00 | 2.19 | 6.79 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 70.40 | 65.00 | -5.40 | 20.40 | 17.60 | 20.00 | 2.50 | 4.80 |
| FUNDING_EXTREME_SIGNAL | filtered | 22 | 47.64 | 61.00 | 13.36 | 20.21 | 17.27 | 15.85 | 1.64 | 5.75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 66 | 50.68 | 63.73 | 13.05 | 21.23 | 19.63 | 17.50 | 2.11 | 10.79 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 68.79 | 65.00 | -3.79 | 20.01 | 19.05 | 17.05 | 2.34 | 2.09 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.33 | 65.00 | -7.33 | 20.63 | 19.37 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 102 | 52.26 | 64.02 | 11.76 | 21.92 | 16.67 | 13.99 | 0.00 | 16.38 |
| MOVER_AVWAP_SCALP | filtered | 139 | 51.49 | 59.57 | 8.08 | 20.09 | 14.77 | 15.80 | 3.99 | 18.74 |
| MOVER_AVWAP_SCALP | kept | 316 | 75.13 | 65.00 | -10.13 | 19.69 | 15.51 | 15.80 | 4.50 | 7.98 |
| MOVER_TREND_PULLBACK | filtered | 2391 | 51.84 | 64.24 | 12.40 | 19.93 | 18.58 | 15.80 | 4.18 | 21.13 |
| MOVER_TREND_PULLBACK | kept | 4085 | 76.18 | 65.00 | -11.18 | 20.45 | 18.51 | 15.80 | 4.21 | 1.45 |
| QUIET_COMPRESSION_BREAK | filtered | 55 | 46.73 | 64.64 | 17.91 | 20.86 | 19.64 | 20.00 | 0.00 | 15.75 |
| QUIET_COMPRESSION_BREAK | kept | 124 | 77.63 | 65.00 | -12.63 | 21.07 | 19.51 | 20.00 | 0.00 | -0.58 |
| SR_FLIP_RETEST | filtered | 8 | 48.56 | 65.00 | 16.44 | 20.95 | 20.00 | 15.20 | 2.50 | 22.52 |
| SR_FLIP_RETEST | kept | 23 | 69.28 | 65.00 | -4.28 | 20.67 | 20.00 | 15.49 | 2.83 | 0.67 |
| TREND_PULLBACK_EMA | filtered | 71 | 54.59 | 64.61 | 10.02 | 21.47 | 19.80 | 17.67 | 4.02 | 12.45 |
| TREND_PULLBACK_EMA | kept | 54 | 72.61 | 65.00 | -7.61 | 21.21 | 19.95 | 16.73 | 4.45 | 4.02 |
| VOLUME_SURGE_BREAKOUT | filtered | 21 | 55.32 | 65.00 | 9.68 | 20.62 | 18.56 | 20.00 | 3.71 | 7.84 |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 76.14 | 65.00 | -11.14 | 20.52 | 17.47 | 20.00 | 5.31 | 8.93 |
| WHALE_MOMENTUM | filtered | 7 | 50.50 | 65.00 | 14.50 | 24.37 | 14.00 | 17.00 | 0.00 | 14.70 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 124 | 49.99 | 20.81 | 12.44 | 7.50 | 12.95 | 5.65 | 8.64 | 0.35 |
| DIVERGENCE_CONTINUATION | kept | 64 | 68.07 | 20.75 | 15.50 | 4.55 | 13.36 | 5.54 | 9.26 | 0.44 |
| FAILED_AUCTION_RECLAIM | filtered | 98 | 48.71 | 21.41 | 16.86 | 4.10 | 13.67 | 7.41 | 4.10 | 2.19 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 70.40 | 25.00 | 14.00 | 6.00 | 14.00 | 5.00 | 8.70 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 22 | 47.64 | 22.09 | 8.00 | 8.05 | 14.45 | 9.05 | 5.12 | 1.64 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 66 | 50.68 | 21.97 | 14.55 | 6.55 | 12.24 | 6.82 | 6.07 | 2.11 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 68.79 | 22.00 | 15.62 | 5.34 | 12.00 | 6.44 | 7.32 | 2.34 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.33 | 22.33 | 14.00 | 3.00 | 17.00 | 7.33 | 8.67 | 0.00 |
| MEAN_REVERT | filtered | 102 | 52.26 | 23.43 | 18.00 | 4.18 | 10.59 | 5.00 | 7.43 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 139 | 51.49 | 17.85 | 18.09 | 12.76 | 14.00 | 5.94 | 4.21 | 3.99 |
| MOVER_AVWAP_SCALP | kept | 316 | 75.13 | 18.02 | 18.01 | 12.46 | 14.03 | 7.30 | 8.80 | 4.50 |
| MOVER_TREND_PULLBACK | filtered | 2391 | 51.84 | 18.14 | 18.00 | 7.98 | 12.38 | 6.07 | 8.80 | 4.18 |
| MOVER_TREND_PULLBACK | kept | 4085 | 76.18 | 18.96 | 18.02 | 7.86 | 12.62 | 6.68 | 9.36 | 4.21 |
| QUIET_COMPRESSION_BREAK | filtered | 55 | 46.73 | 18.60 | 17.64 | 10.80 | 14.00 | 7.03 | 5.06 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 124 | 77.63 | 19.32 | 15.48 | 12.97 | 14.02 | 6.98 | 9.69 | 0.00 |
| SR_FLIP_RETEST | filtered | 8 | 48.56 | 24.75 | 9.25 | 7.12 | 13.62 | 5.00 | 8.84 | 2.50 |
| SR_FLIP_RETEST | kept | 23 | 69.28 | 23.96 | 10.17 | 5.22 | 13.83 | 5.00 | 8.96 | 2.83 |
| TREND_PULLBACK_EMA | filtered | 71 | 54.59 | 12.42 | 18.00 | 7.50 | 14.00 | 7.68 | 8.06 | 4.02 |
| TREND_PULLBACK_EMA | kept | 54 | 72.61 | 16.39 | 18.00 | 7.58 | 13.28 | 7.73 | 9.85 | 4.45 |
| VOLUME_SURGE_BREAKOUT | filtered | 21 | 55.32 | 17.38 | 16.86 | 12.00 | 14.00 | 4.29 | 5.64 | 3.71 |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 76.14 | 23.00 | 15.00 | 13.12 | 15.12 | 5.00 | 8.50 | 5.31 |
| WHALE_MOMENTUM | filtered | 7 | 50.50 | 25.00 | 8.00 | 3.00 | 12.00 | 8.50 | 8.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 124 | 49.99 | 0.00 | 0.00 | 1.88 | 0.00 | 2.44 | 0.00 | 0.00 | 0.00 | **4.32** |
| DIVERGENCE_CONTINUATION | kept | 64 | 68.07 | 0.00 | 0.00 | 1.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.55** |
| FAILED_AUCTION_RECLAIM | filtered | 98 | 48.71 | 0.00 | 0.00 | 0.00 | 0.00 | 2.82 | 0.00 | 0.00 | 0.00 | **2.82** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 70.40 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 22 | 47.64 | 0.00 | 0.00 | 2.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.62** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 66 | 50.68 | 0.00 | 0.00 | 2.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.30** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 68.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 102 | 52.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 139 | 51.49 | 0.00 | 0.00 | 0.91 | 0.00 | 4.77 | 0.39 | 0.00 | 2.43 | **8.50** |
| MOVER_AVWAP_SCALP | kept | 316 | 75.13 | 0.00 | 0.00 | 0.27 | 0.00 | 1.31 | 0.07 | 0.00 | 0.02 | **1.67** |
| MOVER_TREND_PULLBACK | filtered | 2391 | 51.84 | 0.00 | 0.00 | 2.48 | 0.00 | 0.73 | 0.12 | 0.00 | 0.00 | **3.33** |
| MOVER_TREND_PULLBACK | kept | 4085 | 76.18 | 0.00 | 0.00 | 0.46 | 0.00 | 0.19 | 0.04 | 0.00 | 0.00 | **0.69** |
| QUIET_COMPRESSION_BREAK | filtered | 55 | 46.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.23 | 4.15 | 0.00 | 6.68 | **11.06** |
| QUIET_COMPRESSION_BREAK | kept | 124 | 77.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.23 | 0.00 | 0.00 | **0.33** |
| SR_FLIP_RETEST | filtered | 8 | 48.56 | 0.00 | 0.00 | 0.00 | 0.00 | 18.90 | 2.25 | 0.00 | 0.00 | **21.15** |
| SR_FLIP_RETEST | kept | 23 | 69.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 71 | 54.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 54 | 72.61 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.09** |
| VOLUME_SURGE_BREAKOUT | filtered | 21 | 55.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 76.14 | 0.00 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.60** |
| WHALE_MOMENTUM | filtered | 7 | 50.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **171471 held of 705653 seen** across 21 strategies; 3866 cells past the sample floor; **2026 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47004 | 730/46274/0 | 45% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.40R) |
| MOVER_AVWAP_SCALP | 22407 | 199/22208/0 | 43% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12896 | 160/12736/0 | 46% | -0.10 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12749 | 155/12594/0 | 36% | -0.30 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11149 | 55/11094/0 | 38% | -0.29 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9495 | 107/9388/0 | 35% | -0.47 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| SHADOW_MEAN_REVERT | 7848 | 0/0/7848 | 43% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (+0.76R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.91R) |
| QUIET_COMPRESSION_BREAK | 7575 | 418/7157/0 | 48% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_RANGE_FADE | 7379 | 0/0/7379 | 37% | -0.11 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.34R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_FUNDING_FADE | 6745 | 0/0/6745 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-0.99R) |
| SR_FLIP_RETEST | 5148 | 17/5131/0 | 46% | -0.25 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4951 | 64/4887/0 | 36% | -0.35 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3793 | 2/3791/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3548 | 0/3548/0 | 32% | -0.33 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2130 | 6/2124/0 | 42% | -0.20 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1576 | 0/0/1576 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 474 | 0/474/0 | 30% | -0.55 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 174 | 32/142/0 | 43% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 56 | 2/54/0 | 43% | +0.14 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 326 | 27% / -0.57R | 326 | 53% / -0.09R | +0.48 | **ATR** |
| LIQUIDATION_REVERSAL | 32 | 22% / -0.73R | 32 | 44% / -0.38R | +0.35 | **ATR** |
| TREND_PULLBACK_EMA | 1018 | 38% / -0.37R | 1018 | 51% / -0.08R | +0.29 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1476 | 42% / -0.37R | 1476 | 56% / -0.12R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 514 | 42% / -0.32R | 514 | 46% / -0.18R | +0.14 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 192 | 36% / -0.19R | 192 | 47% / -0.06R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2293 | 44% / -0.18R | 2293 | 51% / -0.05R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 54 | 41% / -0.20R | 54 | 44% / -0.07R | +0.13 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1323 | 41% / -0.22R | 1323 | 43% / -0.12R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 8519 | 50% / -0.11R | 8519 | 55% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 114 | 39% / -0.13R | 114 | 46% / -0.05R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1515 | 47% / -0.12R | 1515 | 53% / -0.05R | +0.07 | **ATR** |
| MEAN_REVERT | 372 | 45% / -0.20R | 372 | 44% / -0.22R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1338 | 47% / -0.14R | 1338 | 47% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11428 | 29% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2293 | 48% | -0.05R | 233 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 122 | 48% | -0.06R | 67 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1698 | 39% / -0.16R | +0.85 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1342 | 32% / -0.26R | +0.81 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2826 | 34% / -0.22R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10402 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1760 | 37% / -0.12R | +0.15 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1289 | 36% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1109 | 32% / -0.26R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 279 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 429 | 32% / -0.15R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 314 | 46% / -0.12R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 83 | 43% / +0.04R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 460 | 32% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 84 | 29% / -0.40R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 40 | 45% / -0.26R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×640]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 78/6) (sustained 78 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 78/6) (sustained 78 cycles)
- **ALERT** `tuned_variants` — 255 non-stamps — atr_arm_uncomputable=255 (seen=4070 stamped=352 skipped=3463) (streak 70/6) (sustained 70 cycles)
- **ALERT** `auto_dispatch` — 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=18) (streak 58/3) (sustained 58 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 6461188 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 12 arms current, none stalled; covering 2020/2020 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 30 arms current, none stalled; covering 1023/1023 signals (100%) | 0 |
| auto_dispatch | violating | 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=18) (streak 58/3) | 58 |
| binance_ip_weight | ok | peak 267/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 76478.90 | 0 |
| candle_coverage | ok | 89/89 symbols with ≥20 15m candles, 89/89 updated within 45m [fresh=89; 75 Tier-1 futures + 14 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 140 dup bars, 0 undedupable; ws 0 out-of-order, 169 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +76 / upstream +24 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1364/1383 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 194 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1360/1379 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 2524349 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 78/6) | 78 |
| emission_controller | ok | last cycle 783s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×640]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 78/6) | 78 |
| entry_quality_effective | ok | 4473 evaluated, 1564 suppressed, 2882 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,310 reads/day of 50,000 [engine 1,284, signing 26]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +19 / upstream +447 | 0 |
| indicator_cache_key | ok | 6397 frozen value(s) avoided; 22480 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.35R over n=4887 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +26 / upstream +447 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 14 held, 14 with scan counts, 14 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2199 rows held, 3298090 evicted (sampled: execution:trigger_not_confirmed 300/1163609, execution:overextended 300/1034221, setup_compat:regime_STRONG_TREND 300/559646) | 0 |
| price_action_lane | ok | 219068 evaluated, 260 emitted; layer1 260 stamped / 0 blind; cooldown=34303, delta_opposed=17708, no_footprint=69014, no_opposing_target=137, no_sweep=80690, rr_below_floor=16956 | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.20R over n=2124 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +42 / upstream +447 | 0 |
| sar_alignment_crosscheck | ok | 177/5312 disagreed (3.3%) | 0 |
| sar_exit_shadow | ok | output +10 / upstream +447 | 0 |
| sar_hold_arm | ok | 1859 held arms settled, 142 unscored, 26 still walking (22 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 21/122 unfetchable (17%); top cause: gap or duplicate bar in the 15m window; symbols: BNBUSDT, ESPORTSUSDT, ETHFIUSDT, OGNUSDT, RUNEUSDT +2 more | 0 |
| sar_live_arms | ok | 27 arms current, none stalled; covering 1022/1022 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 98 still mid-window | 0 |
| scan_cycle | ok | last 67.18s, worst 146.61s over 2815 lifetime cycles; lifetime 45 over 60s, 3 over 120s (plus 1/1 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 6.7s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 107415 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 22s ago (19.99s to run, worst 126.64s), 204 overrun(s) of 1845 cycles, TTL 900s; slowest pair_context=12.02s, trail_governor=7.74s, user_positions=3.53s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +226 / upstream +447 | 0 |
| structural_snap | ok | 6000/6000 measured, 32 blind, 0 levels moved (refusals: redetect_cooldown=333) | 0 |
| structural_veto_lane | ok | 591 stamped; 0 with no readable level book, 17 with clear air ahead, 441 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +447 / upstream +24 | 0 |
| tuned_variants | violating | 255 non-stamps — atr_arm_uncomputable=255 (seen=4070 stamped=352 skipped=3463) (streak 70/6) | 70 |
| unlock_shorts | ok | 13 open, 45 scheduled, calendar 14.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 21 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2154872`
- `Path funnel` emissions: `51`
- `Regime distribution` emissions: `51`
- `QUIET_SCALP_BLOCK` events: `147`
- `confidence_gate` events: `7814`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4712**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 2262 | 6175 | 62247 | 131441 | 0 |
| futures_depth | 2338 | 6070 | 63012 | 164582 | 0 |
| futures_liq | 111 | 8739 | 79900 | 125150 | 0 |
| futures_mover | 1 | 34151 | 34151 | 34151 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=272707] state[populated=272707] buckets[many=272707] sources[none] quality[none]
- funding_rate: presence[absent=49572, present=223135] state[empty=49572, populated=223135] buckets[few=223135, none=49572] sources[none] quality[none]
- liquidation_clusters: presence[absent=183607, present=89100] state[empty=183607, populated=89100] buckets[few=75576, none=183607, some=13524] sources[none] quality[none]
- oi_snapshot: presence[absent=48852, present=223855] state[empty=48852, populated=223855] buckets[many=223855, none=48852] sources[none] quality[none]
- order_book: presence[absent=94764, present=177943] state[populated=177943, unavailable=94764] buckets[few=177943, none=94764] sources[book_ticker=177943, unavailable=94764] quality[none=94764, top_of_book_only=177943]
- orderblocks: presence[absent=272707] state[empty=272707] buckets[none=272707] sources[measured_dark=272707] quality[none]
- recent_ticks: presence[present=272707] state[populated=272707] buckets[many=272707] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.228480935096741` sec
- Median create→first breach: `10183.2059019804` sec
- Median create→terminal: `10183.989207983017` sec
- Median first breach→terminal: `6.306171417236328e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 4.5}, "under_180s": {"count": 1, "pct": 4.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 4.5}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.8903925597393116 | 1.6438788682026062 | 0.6258125953088884 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.5612571932374782 | 0.8000000000000076 | 0.7015714915468412 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.243465447260349 | 2.384089920157765 | 0.9410154492460961 | 0 | 1 |
| MOVER_TREND_PULLBACK | 12 | 12 | 4.261778064202435 | 3.0 | 1.4205926880674782 | 8 | 4 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.0103731482751361 | 1.0883574594992602 | 0.9896444234781558 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.4904 | 4642.254252910614 | 4642.254274368286 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.5613 | 21133.64201593399 | 21133.642063856125 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 31395.685162067413 | 31395.68518805504 |
| MOVER_TREND_PULLBACK | 12 | 12 | 16.7 | 41.7 | 16.7 | 0.0 | 0.6067 | 5606.972452402115 | 5606.972496509552 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 83.3 | 0.0 | 83.3 | 0.0 | 1.9309 | 48646.39578843117 | 48647.086513996124 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 238 | 6 | 65 | 0.0 | 0.0 | None | None | 173 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1843 | 21 | 1499 | 0.0 | 0.0 | None | None | 344 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-26`
- Gating Δ: `27157`
- No-generation Δ: `432079`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.3308, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.3308, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.485, "current_avg_pnl": 0.6067, "current_win_rate": 16.7, "previous_avg_pnl": 0.1217, "previous_win_rate": 26.5, "win_rate_delta": -9.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 2.7414, "current_avg_pnl": 1.9309, "current_win_rate": 83.3, "previous_avg_pnl": -0.8105, "previous_win_rate": 9.1, "win_rate_delta": 74.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -241, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 63, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -4708.73, "median_terminal_delta_sec": -4708.73, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
