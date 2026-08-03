# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `2468` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 54 | 54 | 33 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 20614 | 20614 | 18512 | 33 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 121825 | 121830 | 9 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 117110 | 117122 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 116803 | 110726 | 6375 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 117137 | 112402 | 4961 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 118081 | 117815 | 296 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 106562 | 106536 | 34 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 117368 | 117385 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 117401 | 113818 | 4669 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 125694 | 129823 | 852 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 121840 | 113046 | 12612 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 114517 | 114523 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 117124 | 117132 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 116762 | 116112 | 690 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 118491 | 115424 | 3795 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 113168 | 109416 | 7299 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 104946 | 99645 | 5631 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 105276 | 104663 | 667 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 121807 | 121812 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 106570 | 106325 | 305 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 17894 | 17894 | 13795 | 69 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 835 | 835 | 156 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 60 | 60 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 28169 | 28169 | 27670 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 6 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11757 | 11757 | 9145 | 16 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1858 | 1858 | 261 | 49 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 31093 | 31093 | 18167 | 311 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 65 | 65 | 65 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3055 | 3055 | 1822 | 43 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 9657 | 9657 | 8854 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 28234 | 28234 | 17072 | 95 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2274 | 2274 | 2034 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 43 | 43 | 0 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 9878 | 9878 | 321 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=121830): breakout_not_found=60532, basic_filters_failed=39253, move_not_fresh=15912, breakout_stale=3423, retest_proximity_failed=1810, insufficient_candles=708, volume_spike_missing=97, ema_alignment_reject=73, move_exhausted=22
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=117122): cls_disabled_merged_into_lsr=117122
- **EVAL::DIVERGENCE_CONTINUATION** (total=110726): cvd_divergence_failed=38042, basic_filters_failed=34466, h1_trend_not_aligned=22825, ema_alignment_reject=11028, retest_proximity_failed=1950, regime_blocked=1226, missing_fvg_or_orderblock=897, insufficient_candles=267, cvd_insufficient=25
- **EVAL::FAILED_AUCTION_RECLAIM** (total=112402): auction_not_detected=39904, basic_filters_failed=33845, reclaim_hold_failed=20060, tail_too_small=15201, regime_blocked=3080, insufficient_candles=267, rsi_reject=45
- **EVAL::FUNDING_EXTREME** (total=117815): funding_not_extreme=76690, basic_filters_failed=34386, missing_funding_rate=2826, ema_alignment_reject=2621, rsi_reject=569, momentum_reject=345, cvd_divergence_failed=256, insufficient_candles=88, missing_fvg_or_orderblock=34
- **EVAL::LIQUIDATION_REVERSAL** (total=106536): cascade_threshold_not_met=69989, basic_filters_failed=35048, cvd_divergence_failed=528, insufficient_candles=508, rsi_reject=417, missing_fvg_or_orderblock=35, volume_spike_missing=11
- **EVAL::MA_CROSS_TREND_SHIFT** (total=117385): no_ma_cross=80088, basic_filters_failed=34513, ma_cross_htf_misaligned=1567, ma_cross_cooldown=1217
- **EVAL::MEAN_REVERT** (total=113818): no_extension=92310, basic_filters_failed=20106, insufficient_candles=1402
- **EVAL::MOVER_AVWAP_SCALP** (total=129823): no_mover_leg=40207, basic_filters_failed=39186, no_avwap_tag=39144, avwap_slope_against=4859, avwap_reclaim_no_volume=2176, no_avwap_reclaim=2139, insufficient_candles=1898, anchor_too_recent=214
- **EVAL::MOVER_TREND_PULLBACK** (total=113046): mover_run_too_small=51866, basic_filters_failed=39059, no_reclaim=16756, no_pullback_tag=3253, insufficient_candles=2112
- **EVAL::OPENING_RANGE_BREAKOUT** (total=114523): feature_disabled=114523
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=117132): regime_blocked=84116, breakout_not_found=22801, basic_filters_failed=8000, adx_reject=2175, ema_alignment_reject=40
- **EVAL::QUIET_COMPRESSION_BREAK** (total=116112): regime_blocked=36026, compression_not_detected=30556, basic_filters_failed=25821, breakout_not_detected=21213, volume_confirmation_failed=2021, insufficient_candles=302, rsi_reject=116, missing_fvg_or_orderblock=35, macd_reject=22
- **EVAL::RANGE_FADE** (total=115424): no_range_edge=93426, basic_filters_failed=20072, insufficient_candles=1926
- **EVAL::SR_FLIP_RETEST** (total=109416): basic_filters_failed=33677, flip_close_not_confirmed=18412, whipsaw_flip=14999, long_break_volume_thin=13754, retest_out_of_zone=10053, reclaim_hold_failed=9931, regime_blocked=3069, wick_quality_failed=2579, insufficient_candles=1076, long_acceptance_not_held=925, missing_fvg_or_orderblock=598, ema_alignment_reject=290, rsi_reject=53
- **EVAL::STANDARD** (total=99645): momentum_reject=33670, adx_reject=23754, basic_filters_failed=15558, sweeps_not_detected=11558, macd_reject=7769, ema_alignment_reject=6034, insufficient_candles=1006, invalid_sl_geometry=140, rsi_reject=139, mtf_reject=17
- **EVAL::TREND_PULLBACK** (total=104663): h1_trend_not_aligned=31019, h1_pullback_not_confirmed=20876, basic_filters_failed=15711, ema_alignment_reject=13805, ema_not_tested_prev=6211, no_ema_reclaim_close=5759, body_conviction_fail=3573, rsi_reject=3091, regime_blocked=1301, insufficient_candles=1006, prev_already_above_emas=838, no_prev_high_break=601, momentum_flat=228, prev_already_below_emas=222, no_prev_low_break=209, momentum_reject=97, missing_fvg_or_orderblock=83, ema21_not_tagged=33
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=121812): breakout_not_found=63254, basic_filters_failed=39249, move_not_fresh=11409, breakout_stale=4680, retest_proximity_failed=2034, insufficient_candles=708, volume_spike_missing=424, ema_alignment_reject=24, missing_fvg_or_orderblock=21, move_exhausted=9
- **EVAL::WHALE_MOMENTUM** (total=106325): momentum_reject=83112, recent_ticks_insufficient=17134, basic_filters_failed=6035, insufficient_candles=44

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=12): execution:overextended=12
- **DIVERGENCE_CONTINUATION** (total=470): setup_compat:regime_VOLATILE_UNSUITABLE=414, setup_compat:regime_BREAKOUT_EXPANSION=56
- **FAILED_AUCTION_RECLAIM** (total=3393): execution:overextended=1332, setup_compat:regime_STRONG_TREND=1313, context_floor=748
- **FUNDING_EXTREME_SIGNAL** (total=699): execution:trigger_not_confirmed=693, context_floor=6
- **LIQUIDATION_REVERSAL** (total=60): execution:trigger_not_confirmed=60
- **LIQUIDITY_SWEEP_REVERSAL** (total=6673): execution:trigger_not_confirmed=3916, execution:overextended=1721, setup_compat:regime_STRONG_TREND=1036
- **MA_CROSS_TREND_SHIFT** (total=14): setup_compat:regime_CLEAN_RANGE=8, setup_compat:regime_DIRTY_RANGE=3, execution:trigger_not_confirmed=3
- **MEAN_REVERT** (total=4965): setup_compat:regime_WEAK_TREND=2360, setup_compat:regime_STRONG_TREND=2239, execution:overextended=366
- **MOVER_AVWAP_SCALP** (total=1136): execution:overextended=756, execution:trigger_not_confirmed=377, entry_quality=3
- **MOVER_TREND_PULLBACK** (total=14132): execution:overextended=8149, execution:trigger_not_confirmed=5835, entry_quality=148
- **POST_DISPLACEMENT_CONTINUATION** (total=22): execution:overextended=22
- **QUIET_COMPRESSION_BREAK** (total=884): context_floor=738, execution:trigger_not_confirmed=146
- **RANGE_FADE** (total=6049): setup_compat:regime_STRONG_TREND=2161, setup_compat:regime_WEAK_TREND=1607, setup_compat:regime_VOLATILE_UNSUITABLE=1109, execution:overextended=1022, context_edge=72, setup_compat:regime_BREAKOUT_EXPANSION=47, context_floor=31
- **TREND_PULLBACK_EMA** (total=1967): setup_compat:regime_CLEAN_RANGE=1402, setup_compat:regime_DIRTY_RANGE=477, setup_compat:regime_VOLATILE_UNSUITABLE=88
- **VOLUME_SURGE_BREAKOUT** (total=36): execution:overextended=31, context_floor=5
- **WHALE_MOMENTUM** (total=9418): execution:trigger_not_confirmed=9418

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 234728 | 34.9% |
| RANGING | 195869 | 29.1% |
| TRENDING_UP | 112924 | 16.8% |
| TRENDING_DOWN | 102967 | 15.3% |
| VOLATILE | 26261 | 3.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **582**
- Average confidence gap to threshold: **11.23** (samples=582) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ARBUSDT=58, SOLUSDT=46, BTCUSDT=38, TRXUSDT=37, HYPEUSDT=27, ETCUSDT=26, AAVEUSDT=25, BNBUSDT=25, 1000PEPEUSDT=25, ETHUSDT=21

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 21 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 261 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 14 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 410 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 127 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 85 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 604 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 25 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 29 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 15 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 163 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 60 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 12 |
| MEAN_REVERT | kept | min_confidence_pass | 106 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 326 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 110 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 743 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1253 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 90 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 7110 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 81 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 26 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 308 |
| RANGE_FADE | filtered | quiet_scalp_min_confidence | 15 |
| RANGE_FADE | filtered | min_confidence | 6 |
| SR_FLIP_RETEST | filtered | min_confidence | 708 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 148 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 967 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 34 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 168 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 16 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 74 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 10 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 21 | 71.27 | 65.00 | -6.27 | 17.85 | 15.60 | 20.00 | 4.21 | 4.65 |
| DIVERGENCE_CONTINUATION | filtered | 275 | 57.71 | 64.53 | 6.82 | 20.10 | 19.74 | 17.15 | 1.07 | 10.07 |
| DIVERGENCE_CONTINUATION | kept | 410 | 70.74 | 65.00 | -5.74 | 19.87 | 19.88 | 17.72 | 1.81 | 1.92 |
| FAILED_AUCTION_RECLAIM | filtered | 212 | 55.68 | 63.68 | 8.00 | 20.71 | 19.28 | 20.00 | 4.33 | 8.73 |
| FAILED_AUCTION_RECLAIM | kept | 604 | 72.49 | 65.00 | -7.49 | 20.62 | 19.54 | 20.00 | 3.69 | 0.23 |
| FUNDING_EXTREME_SIGNAL | filtered | 30 | 44.56 | 64.00 | 19.44 | 19.20 | 14.00 | 17.01 | 3.37 | 10.92 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 65.80 | 65.00 | -0.80 | 20.30 | 13.85 | 17.00 | 3.50 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 29 | 63.41 | 10.00 | -53.41 | 20.77 | 8.00 | 20.00 | 4.83 | 0.69 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 51.23 | 65.00 | 13.77 | 20.98 | 18.31 | 17.26 | 1.73 | 17.96 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 163 | 69.94 | 65.00 | -4.94 | 20.40 | 18.90 | 17.18 | 1.48 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 68.15 | 65.00 | -3.15 | 21.95 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 72 | 52.16 | 64.93 | 12.77 | 20.59 | 15.41 | 16.69 | 0.00 | 5.33 |
| MEAN_REVERT | kept | 106 | 70.60 | 65.00 | -5.60 | 19.83 | 15.40 | 18.18 | 0.00 | -0.03 |
| MOVER_AVWAP_SCALP | filtered | 439 | 59.20 | 50.85 | -8.35 | 20.30 | 13.90 | 15.80 | 3.43 | 5.81 |
| MOVER_AVWAP_SCALP | kept | 743 | 77.40 | 65.00 | -12.40 | 20.28 | 16.34 | 15.80 | 4.23 | 0.31 |
| MOVER_TREND_PULLBACK | filtered | 1343 | 55.96 | 63.02 | 7.06 | 19.27 | 18.54 | 15.80 | 4.21 | 14.37 |
| MOVER_TREND_PULLBACK | kept | 7110 | 76.54 | 65.00 | -11.54 | 20.34 | 18.62 | 15.80 | 4.56 | 1.03 |
| QUIET_COMPRESSION_BREAK | filtered | 107 | 57.96 | 65.00 | 7.04 | 20.91 | 19.48 | 20.00 | 0.00 | 7.78 |
| QUIET_COMPRESSION_BREAK | kept | 308 | 77.48 | 65.00 | -12.48 | 21.75 | 19.85 | 20.00 | 0.00 | -1.16 |
| RANGE_FADE | filtered | 21 | 53.69 | 63.57 | 9.88 | 21.42 | 15.36 | 19.98 | 0.00 | 15.09 |
| SR_FLIP_RETEST | filtered | 856 | 57.07 | 64.23 | 7.16 | 20.75 | 19.88 | 15.88 | 1.62 | 12.20 |
| SR_FLIP_RETEST | kept | 967 | 69.64 | 65.00 | -4.64 | 20.59 | 19.92 | 15.68 | 1.96 | 1.02 |
| TREND_PULLBACK_EMA | filtered | 40 | 53.73 | 65.00 | 11.27 | 19.96 | 19.15 | 18.06 | 4.50 | 17.59 |
| TREND_PULLBACK_EMA | kept | 168 | 75.37 | 65.00 | -10.37 | 20.27 | 19.61 | 17.05 | 4.37 | -1.77 |
| VOLUME_SURGE_BREAKOUT | filtered | 16 | 58.80 | 63.12 | 4.32 | 19.45 | 17.58 | 20.00 | 3.50 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 75.20 | 65.00 | -10.20 | 18.90 | 17.80 | 20.00 | 5.00 | 8.53 |
| WHALE_MOMENTUM | filtered | 74 | 52.81 | 65.00 | 12.19 | 20.12 | 14.64 | 17.00 | 0.00 | 15.58 |
| WHALE_MOMENTUM | kept | 10 | 65.05 | 65.00 | -0.05 | 19.23 | 13.82 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 21 | 71.27 | 17.00 | 15.71 | 13.86 | 10.71 | 4.52 | 9.90 | 4.21 |
| DIVERGENCE_CONTINUATION | filtered | 275 | 57.71 | 22.24 | 15.64 | 5.04 | 11.09 | 5.16 | 8.53 | 1.07 |
| DIVERGENCE_CONTINUATION | kept | 410 | 70.74 | 22.68 | 16.27 | 5.43 | 11.58 | 6.57 | 9.17 | 1.81 |
| FAILED_AUCTION_RECLAIM | filtered | 212 | 55.68 | 21.94 | 14.83 | 6.01 | 11.63 | 6.11 | 5.35 | 4.33 |
| FAILED_AUCTION_RECLAIM | kept | 604 | 72.49 | 23.16 | 15.11 | 5.24 | 12.17 | 6.16 | 7.27 | 3.69 |
| FUNDING_EXTREME_SIGNAL | filtered | 30 | 44.56 | 25.00 | 8.33 | 3.80 | 13.20 | 8.38 | 4.90 | 3.37 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 65.80 | 17.00 | 20.00 | 3.00 | 9.00 | 5.00 | 8.30 | 3.50 |
| LIQUIDATION_REVERSAL | filtered | 29 | 63.41 | 25.00 | 8.00 | 13.76 | 8.00 | 3.53 | 7.18 | 4.83 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 51.23 | 19.55 | 15.64 | 5.05 | 14.36 | 5.52 | 7.35 | 1.73 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 163 | 69.94 | 20.69 | 15.28 | 6.61 | 13.15 | 6.02 | 6.71 | 1.48 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 68.15 | 25.00 | 14.00 | 4.50 | 10.50 | 5.00 | 9.15 | 0.00 |
| MEAN_REVERT | filtered | 72 | 52.16 | 23.44 | 17.72 | 5.00 | 12.00 | 6.37 | 5.04 | 0.00 |
| MEAN_REVERT | kept | 106 | 70.60 | 20.72 | 16.64 | 8.38 | 12.00 | 7.68 | 5.18 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 439 | 59.20 | 19.00 | 18.14 | 8.34 | 13.16 | 5.75 | 6.08 | 3.43 |
| MOVER_AVWAP_SCALP | kept | 743 | 77.40 | 19.51 | 18.01 | 9.76 | 12.90 | 5.75 | 8.20 | 4.23 |
| MOVER_TREND_PULLBACK | filtered | 1343 | 55.96 | 17.34 | 18.02 | 7.81 | 12.74 | 5.40 | 8.64 | 4.21 |
| MOVER_TREND_PULLBACK | kept | 7110 | 76.54 | 19.12 | 18.05 | 8.02 | 13.05 | 5.89 | 9.05 | 4.56 |
| QUIET_COMPRESSION_BREAK | filtered | 107 | 57.96 | 17.52 | 17.03 | 12.36 | 14.08 | 5.52 | 3.84 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 308 | 77.48 | 19.26 | 17.78 | 12.59 | 14.03 | 7.22 | 6.87 | 0.00 |
| RANGE_FADE | filtered | 21 | 53.69 | 23.57 | 16.86 | 9.29 | 13.71 | 5.64 | 3.99 | 0.00 |
| SR_FLIP_RETEST | filtered | 856 | 57.07 | 19.49 | 16.27 | 6.40 | 12.51 | 6.46 | 6.53 | 1.62 |
| SR_FLIP_RETEST | kept | 967 | 69.64 | 21.28 | 15.63 | 6.07 | 13.29 | 6.30 | 7.43 | 1.96 |
| TREND_PULLBACK_EMA | filtered | 40 | 53.73 | 8.78 | 18.00 | 7.72 | 14.45 | 7.88 | 10.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 168 | 75.37 | 14.42 | 18.00 | 7.54 | 14.50 | 7.32 | 9.26 | 4.37 |
| VOLUME_SURGE_BREAKOUT | filtered | 16 | 58.80 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 4.30 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 75.20 | 21.00 | 16.00 | 12.75 | 13.25 | 5.75 | 10.00 | 5.00 |
| WHALE_MOMENTUM | filtered | 74 | 52.81 | 20.97 | 8.00 | 12.61 | 13.65 | 7.16 | 6.00 | 0.00 |
| WHALE_MOMENTUM | kept | 10 | 65.05 | 25.00 | 8.00 | 14.70 | 14.00 | 5.35 | 8.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 21 | 71.27 | 0.00 | 0.00 | 2.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.17** |
| DIVERGENCE_CONTINUATION | filtered | 275 | 57.71 | 0.00 | 0.00 | 1.11 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **1.97** |
| DIVERGENCE_CONTINUATION | kept | 410 | 70.74 | 0.00 | 0.00 | 0.54 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.56** |
| FAILED_AUCTION_RECLAIM | filtered | 212 | 55.68 | 0.00 | 0.00 | 1.22 | 0.00 | 3.36 | 0.00 | 0.00 | 0.00 | **4.58** |
| FAILED_AUCTION_RECLAIM | kept | 604 | 72.49 | 0.00 | 0.00 | 0.03 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.05** |
| FUNDING_EXTREME_SIGNAL | filtered | 30 | 44.56 | 0.00 | 0.00 | 3.04 | 0.00 | 2.88 | 0.00 | 0.00 | 0.00 | **5.92** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 65.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 29 | 63.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 51.23 | 0.00 | 0.00 | 0.00 | 0.00 | 6.87 | 0.00 | 0.00 | 0.00 | **6.87** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 163 | 69.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 68.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 72 | 52.16 | 0.00 | 0.00 | 5.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.33** |
| MEAN_REVERT | kept | 106 | 70.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 439 | 59.20 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.05 | **1.19** |
| MOVER_AVWAP_SCALP | kept | 743 | 77.40 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | **0.28** |
| MOVER_TREND_PULLBACK | filtered | 1343 | 55.96 | 1.44 | 0.00 | 1.03 | 0.00 | 1.18 | 0.00 | 0.00 | 0.27 | **3.92** |
| MOVER_TREND_PULLBACK | kept | 7110 | 76.54 | 0.19 | 0.00 | 0.38 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | **0.71** |
| QUIET_COMPRESSION_BREAK | filtered | 107 | 57.96 | 0.00 | 0.00 | 0.81 | 0.00 | 0.44 | 0.00 | 0.00 | 2.52 | **3.77** |
| QUIET_COMPRESSION_BREAK | kept | 308 | 77.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.18** |
| RANGE_FADE | filtered | 21 | 53.69 | 0.00 | 0.00 | 2.74 | 0.00 | 12.34 | 0.00 | 0.00 | 0.00 | **15.08** |
| SR_FLIP_RETEST | filtered | 856 | 57.07 | 0.00 | 0.00 | 0.21 | 0.00 | 2.16 | 0.15 | 0.00 | 0.28 | **2.80** |
| SR_FLIP_RETEST | kept | 967 | 69.64 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.03** |
| TREND_PULLBACK_EMA | filtered | 40 | 53.73 | 0.00 | 0.00 | 3.30 | 0.00 | 3.24 | 0.00 | 0.00 | 0.00 | **6.54** |
| TREND_PULLBACK_EMA | kept | 168 | 75.37 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| VOLUME_SURGE_BREAKOUT | filtered | 16 | 58.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 75.20 | 0.00 | 0.00 | 3.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.00** |
| WHALE_MOMENTUM | filtered | 74 | 52.81 | 0.00 | 0.00 | 0.00 | 0.00 | 4.96 | 0.49 | 0.00 | 0.00 | **5.45** |
| WHALE_MOMENTUM | kept | 10 | 65.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1084 (18.8%) | WOULD_LOSE=1908 | WOULD_EXPIRE=2786 | pending (awaiting window)=2429

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 330 | 8.2% | 173.0 | 53.3 | +0.36 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 390 | 0.0% | 101.2 | 0.0 | +0.26 | **KEEP** |
| context_floor:FUNDING_EXTREME_SIGNAL | 21 | 38.1% | 2.2 | 11.0 | -0.42 | **DROP** |
| context_floor:QUIET_COMPRESSION_BREAK | 298 | 0.0% | 48.7 | 0.0 | +0.16 | **KEEP** |
| context_floor:RANGE_FADE | 53 | 0.0% | 39.3 | 0.0 | +0.74 | **KEEP** |
| context_floor:VOLUME_SURGE_BREAKOUT | 56 | 0.0% | 25.7 | 0.0 | +0.46 | **KEEP** |
| context_floor:WHALE_MOMENTUM | 67 | 0.0% | 23.1 | 0.0 | +0.34 | **KEEP** |
| data_stale | 17 | 0.0% | 17.9 | 0.0 | +1.05 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 400 | 18.8% | 96.5 | 52.6 | +0.11 | **KEEP** |
| dispatch_staleness_v2 | 392 | 32.9% | 158.0 | 67.7 | +0.23 | **KEEP** |
| entry_quality:profile_reject | 140 | 4.3% | 138.8 | 8.1 | +0.93 | **KEEP** |
| execution:overextended | 143 | 0.0% | 34.7 | 0.0 | +0.24 | **KEEP** |
| execution_component_floor | 185 | 0.0% | 168.2 | 0.0 | +0.91 | **KEEP** |
| level_still_in_play | 350 | 14.6% | 85.5 | 36.3 | +0.14 | **KEEP** |
| min_confidence | 279 | 13.6% | 96.3 | 42.5 | +0.19 | **KEEP** |
| quiet_scalp_block | 362 | 13.0% | 141.1 | 51.3 | +0.25 | **KEEP** |
| router:correlation_lock | 245 | 18.8% | 69.5 | 31.9 | +0.15 | **KEEP** |
| router:per_channel_cap | 5 | 60.0% | 1.1 | 2.4 | -0.25 | **INSUFFICIENT_SAMPLE** |
| setup_compat:regime_BREAKOUT_EXPANSION | 154 | 16.9% | 84.8 | 24.3 | +0.39 | **KEEP** |
| setup_compat:regime_CLEAN_RANGE | 325 | 60.0% | 184.3 | 19.6 | +0.51 | **KEEP** |
| setup_compat:regime_DIRTY_RANGE | 385 | 30.6% | 227.8 | 52.3 | +0.46 | **KEEP** |
| setup_compat:regime_STRONG_TREND | 37 | 0.0% | 28.9 | 0.0 | +0.78 | **KEEP** |
| setup_compat:regime_VOLATILE_UNSUITABLE | 21 | 0.0% | 21.9 | 0.0 | +1.04 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 67 | 29.9% | 19.0 | 12.4 | +0.10 | **TUNE** |
| shadow_unit:SHADOW_FUNDING_FADE | 353 | 39.1% | 171.0 | 95.9 | +0.21 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 368 | 26.1% | 265.6 | 136.6 | +0.35 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 335 | 18.2% | 245.7 | 140.4 | +0.31 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 107482 across 21 strategies; 2418 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 24919 | 163/24756/0 | 55% | +0.04 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.21R) |
| FAILED_AUCTION_RECLAIM | 16433 | 24/16409/0 | 53% | +0.03 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 16020 | 1/16019/0 | 48% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 10134 | 4/10130/0 | 46% | -0.09 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.45R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 7635 | 0/7635/0 | 45% | -0.12 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+1.42R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 4533 | 27/4506/0 | 31% | -0.39 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.98R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| LIQUIDITY_SWEEP_REVERSAL | 4004 | 9/3995/0 | 46% | -0.18 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 3953 | 0/0/3953 | 42% | -0.04 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.16R) |
| SHADOW_RANGE_FADE | 3619 | 0/0/3619 | 41% | +0.20 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.35R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.96R) |
| MEAN_REVERT | 3361 | 0/3361/0 | 79% | +0.55 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| SHADOW_FUNDING_FADE | 3174 | 0/0/3174 | 40% | -0.30 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.33R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-0.88R) |
| TREND_PULLBACK_EMA | 2940 | 2/2938/0 | 51% | -0.21 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| RANGE_FADE | 2555 | 0/2555/0 | 19% | -0.72 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.34R) |
| VOLUME_SURGE_BREAKOUT | 1754 | 13/1741/0 | 40% | -0.09 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 902 | 2/900/0 | 30% | -0.35 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.07R) | OVERLAP/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.29R) |
| WHALE_MOMENTUM | 765 | 0/765/0 | 50% | -0.19 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 339 | 0/0/339 | 46% | -0.22 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.15R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.82R) |
| BREAKDOWN_SHORT | 301 | 7/294/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| LIQUIDATION_REVERSAL | 64 | 0/64/0 | 66% | -0.45 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| MA_CROSS_TREND_SHIFT | 10 | 1/9/0 | 30% | -0.43 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 83 | 46% / -0.26R | 83 | 49% / -0.12R | +0.15 | **ATR** |
| FUNDING_EXTREME_SIGNAL | 33 | 36% / -0.28R | 33 | 45% / -0.17R | +0.12 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 56 | 46% / +0.04R | 56 | 48% / -0.07R | -0.11 | **FIXED** |
| SR_FLIP_RETEST | 2652 | 46% / -0.20R | 2652 | 48% / -0.10R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 265 | 38% / -0.22R | 265 | 41% / -0.13R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 49 | 45% / -0.22R | 49 | 43% / -0.29R | -0.07 | **FIXED** |
| RANGE_FADE | 186 | 12% / -0.82R | 186 | 15% / -0.76R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 662 | 47% / -0.12R | 662 | 52% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 587 | 50% / -0.17R | 587 | 54% / -0.11R | +0.06 | **ATR** |
| MEAN_REVERT | 323 | 56% / +0.06R | 323 | 52% / +0.12R | +0.05 | **ATR** |
| MOVER_TREND_PULLBACK | 2918 | 54% / -0.01R | 2918 | 56% / +0.01R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1100 | 46% / -0.12R | 1100 | 45% / -0.14R | -0.02 | **FIXED** |
| BREAKDOWN_SHORT | 15 | 27% / -0.30R | 15 | 27% / -0.29R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2162 | 47% / -0.10R | 2162 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 7 | 43% / -0.18R | 7 | 43% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 40% / -0.81R | 5 | 40% / -0.40R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 3212 | 31% | -0.11R | 246 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 255 | 39% | -0.14R | 96 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 17 | 59% | +0.10R | 13 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1114 | 28% / -1.82R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 6 | 17% / -1.07R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 2049 | 35% / -0.49R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 861 | 32% / -0.63R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 36 | 17% / -1.26R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 449 | 29% / -2.40R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 450 | 34% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 214 | 40% / -1.62R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 32 | 12% / -3.65R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 67 | 25% / -1.57R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 177 | 31% / -0.23R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 6 | 17% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 57 | 42% / -0.24R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 27 | 56% / +0.10R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 4 | 25% / -0.90R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 7 | 43% / -0.06R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| FUNDING_EXTREME_SIGNAL | quiet_scalp_block | 5 | 80.0% | -0.96 | **INSUFFICIENT_SAMPLE** |
| MEAN_REVERT | dispatch_staleness_v2 | 5 | 100.0% | -0.81 | **INSUFFICIENT_SAMPLE** |
| TREND_PULLBACK_EMA | router:correlation_lock | 1 | 100.0% | -0.70 | **INSUFFICIENT_SAMPLE** |
| FUNDING_EXTREME_SIGNAL | context_floor:FUNDING_EXTREME_SIGNAL | 21 | 38.1% | -0.42 | **DROP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 16 | 93.8% | -0.32 | **INSUFFICIENT_SAMPLE** |
| LIQUIDITY_SWEEP_REVERSAL | dispatch_staleness_v2 | 16 | 87.5% | -0.29 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | quiet_scalp_block | 33 | 60.6% | -0.29 | **DROP** |
| TREND_PULLBACK_EMA | dispatch_staleness_v2 | 5 | 100.0% | -0.26 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | router:per_channel_cap | 5 | 60.0% | -0.25 | **INSUFFICIENT_SAMPLE** |
| MA_CROSS_TREND_SHIFT | setup_compat:regime_DIRTY_RANGE | 2 | 0.0% | +0.01 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | execution:overextended | 27 | 0.0% | +0.01 | **TUNE** |
| DIVERGENCE_CONTINUATION | setup_compat:regime_BREAKOUT_EXPANSION | 87 | 29.9% | +0.04 | **TUNE** |
| MOVER_TREND_PULLBACK | dispatch_cooldown | 336 | 22.0% | +0.06 | **TUNE** |
| MOVER_AVWAP_SCALP | min_confidence | 5 | 0.0% | +0.06 | **INSUFFICIENT_SAMPLE** |
| BREAKDOWN_SHORT | router:correlation_lock | 1 | 0.0% | +0.07 | **INSUFFICIENT_SAMPLE** |
| MA_CROSS_TREND_SHIFT | setup_compat:regime_CLEAN_RANGE | 3 | 0.0% | +0.07 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | router:correlation_lock | 14 | 35.7% | +0.07 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | min_confidence | 61 | 37.7% | +0.08 | **TUNE** |
| FAILED_AUCTION_RECLAIM | dispatch_staleness_v2 | 1 | 0.0% | +0.08 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | router:correlation_lock | 37 | 10.8% | +0.08 | **TUNE** |
| MOVER_TREND_PULLBACK | level_still_in_play | 246 | 16.3% | +0.09 | **TUNE** |
| TREND_PULLBACK_EMA | level_still_in_play | 17 | 64.7% | +0.10 | **INSUFFICIENT_SAMPLE** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 67 | 29.9% | +0.10 | **TUNE** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 17 | 0.0% | +0.10 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | dispatch_cooldown | 11 | 9.1% | +0.11 | **INSUFFICIENT_SAMPLE** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 35 · alerting: **6** · boot grace active: False
- **ALERT** `candle_series_integrity` — merge dropped 1443 dup bars, 0 undedupable; ws 0 out-of-order, 121 in-place; SAR refused 12301 series (streak 118/6) (sustained 118 cycles)
- **ALERT** `entry_feature_inputs` — 8 feature(s) absent on EVERY stamp of their path: MEAN_REVERT.extension_pct,MEAN_REVERT.level_dist_r,MOVER_AVWAP_SCALP.extension_pct,MOVER_AVWAP_SCALP.level_dist_r,MOVER_TREND_PULLBACK.level_dist_r,RANGE_FADE.extension_pct,RANGE_FADE.level_dist_r,TREND_PULLBACK_EMA.level_dist_r — upstream is dark, and the panel cannot tell that from 'unused' (streak 118/6) (sustained 118 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 2 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 118/6) (sustained 118 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.39R (bound 0.3) (streak 118/6) (sustained 118 cycles)
- **ALERT** `mean_revert_emission` — 721 detections since last emission (emitted_total=6) — and the blocked candidates measure +0.55R over n=3361, so the gating is COSTING us. Check gate rejections. (streak 20/6) (sustained 20 cycles)
- **ALERT** `tuned_variants` — 78 unexplained non-stamps (seen=1784 stamped=215 skipped=1491) (streak 38/6) (sustained 38 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=0 fanouts=4 (gaps: skip 3, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 62839.70 | 0 |
| candle_coverage | ok | 92/96 symbols with ≥20 15m candles, 85/96 updated within 45m | 0 |
| candle_series_integrity | violating | merge dropped 1443 dup bars, 0 undedupable; ws 0 out-of-order, 121 in-place; SAR refused 12301 series (streak 118/6) | 118 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 2 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 118/6) | 118 |
| context_emission_policy | ok | output +70 / upstream +30 | 0 |
| dark_resolution | ok | 6 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.39R (bound 0.3) (streak 118/6) | 118 |
| emission_controller | ok | last cycle 969s ago; live_overrides=22 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=11 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 8 feature(s) absent on EVERY stamp of their path: MEAN_REVERT.extension_pct,MEAN_REVERT.level_dist_r,MOVER_AVWAP_SCALP.extension_pct,MOVER_AVWAP_SCALP.level_dist_r,MOVER_TREND_PULLBACK.level_dist_r,RANGE_FADE.extension_pct,RANGE_FADE.level_dist_r,TREND_PULLBACK_EMA.level_dist_r — upstream is dark, and the panel cannot tell that from 'unused' (streak 118/6) | 118 |
| entry_quality_effective | ok | 3466 evaluated, 153 suppressed, 0 shadow-rejected; live rules: profile_reject | 0 |
| gate_override_shadow | ok | output +1 / upstream +1 | 0 |
| geometry_ab | ok | output +13 / upstream +226 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 721 detections since last emission (emitted_total=6) — and the blocked candidates measure +0.55R over n=3361, so the gating is COSTING us. Check gate rejections. (streak 20/6) | 20 |
| mean_revert_path | ok | output +13 / upstream +226 | 0 |
| mover_admission_metadata | ok | 851 symbols known, 150 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2977 rows held, 28628 evicted (sampled: execution:trigger_not_confirmed 400/13736, execution:overextended 400/7586, setup_compat:regime_STRONG_TREND 400/4062) | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.72R over n=2555 — emitting them would lose money | 0 |
| range_fade_path | ok | output +20 / upstream +226 | 0 |
| sar_alignment_crosscheck | ok | 380/11000 disagreed (3.5%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +226 | 0 |
| sar_ledger_candles | ok | 13/104 unfetchable (12%); top cause: 15m history rolled off before the stamp; symbols: BEATUSDT, DEXEUSDT, HBARUSDT, KAITOUSDT, TRUMPUSDT +1 more | 0 |
| sar_live_arms | ok | 2 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 19 resolved, 72 still mid-window | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +1 / upstream +0 | 0 |
| strategy_edge | ok | output +74 / upstream +226 | 0 |
| suppression_audit | ok | output +226 / upstream +30 | 0 |
| tuned_variants | violating | 78 unexplained non-stamps (seen=1784 stamped=215 skipped=1491) (streak 38/6) | 38 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3412995`
- `Path funnel` emissions: `85`
- `Regime distribution` emissions: `85`
- `QUIET_SCALP_BLOCK` events: `582`
- `confidence_gate` events: `14156`
- `free_channel_post` events: `15`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 4607 | 4607 | 5908 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **15**

| Source | Count |
|---|---:|
| signal_close | 8 |
| regime_shift | 7 |

- By severity: HIGH=15

## Dependency readiness
- cvd: presence[present=498103] state[populated=498103] buckets[few=25, many=497348, some=730] sources[none] quality[none]
- funding_rate: presence[absent=38579, present=459524] state[empty=38579, populated=459524] buckets[few=459524, none=38579] sources[none] quality[none]
- liquidation_clusters: presence[absent=303605, present=194498] state[empty=303605, populated=194498] buckets[few=152453, none=303605, some=42045] sources[none] quality[none]
- oi_snapshot: presence[absent=34501, present=463602] state[empty=34501, populated=463602] buckets[few=388, many=461532, none=34501, some=1682] sources[none] quality[none]
- order_book: presence[absent=133633, present=364470] state[populated=364470, unavailable=133633] buckets[few=364470, none=133633] sources[book_ticker=364470, unavailable=133633] quality[none=133633, top_of_book_only=364470]
- orderblocks: presence[absent=498103] state[empty=498103] buckets[none=498103] sources[not_implemented=498103] quality[none]
- recent_ticks: presence[absent=539, present=497564] state[empty=539, populated=497564] buckets[many=497564, none=539] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.0807594060897827` sec
- Median create→first breach: `2747.268809080124` sec
- Median create→terminal: `2748.7357300519943` sec
- Median first breach→terminal: `2.143582582473755` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 12.5}, "under_180s": {"count": 1, "pct": 12.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 12.5}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.8845 | 2741.664834022522 | 2743.247225046158 |
| MOVER_TREND_PULLBACK | 7 | 7 | 0.0 | 57.1 | 0.0 | 0.0 | -0.4977 | 2752.872784137726 | 2754.224235057831 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 28234 | 95 | 17072 | 0.0 | 0.0 | None | None | 11162 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2274 | 16 | 2034 | 0.0 | 0.0 | None | None | 240 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-32`
- Gating Δ: `14698`
- No-generation Δ: `42007`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9717, "current_avg_pnl": -0.4977, "current_win_rate": 0.0, "previous_avg_pnl": -1.4694, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -25, "geometry_changed_delta": 0, "geometry_preserved_delta": -529, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -11, "geometry_changed_delta": 0, "geometry_preserved_delta": -209, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
