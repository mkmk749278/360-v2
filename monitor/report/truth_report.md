# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `7030` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 50 | 50 | 40 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5071 | 5071 | 4677 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 37338 | 37332 | 19 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 31592 | 31598 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 31425 | 29826 | 1763 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 31611 | 31233 | 411 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 32488 | 32462 | 45 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 29119 | 29129 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 31645 | 31666 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 31671 | 30666 | 1427 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 39189 | 41084 | 267 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 37353 | 34192 | 4977 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 32353 | 32356 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 31599 | 31602 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 31409 | 31346 | 79 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 32097 | 31488 | 872 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 31258 | 31354 | 35 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 27927 | 27207 | 813 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 28025 | 27874 | 187 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 37321 | 37336 | 1 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 29132 | 29131 | 17 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1115 | 1115 | 852 | 6 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 244 | 244 | 74 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 12 | 12 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4374 | 4374 | 4224 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 5 | 5 | 0 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 3933 | 3933 | 2968 | 10 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 634 | 634 | 107 | 31 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 13456 | 13456 | 7242 | 191 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 18 | 18 | 17 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 516 | 516 | 293 | 34 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 2603 | 2603 | 2138 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 111 | 111 | 25 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 801 | 801 | 691 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 18 | 18 | 17 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 599 | 599 | 24 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=37332): breakout_not_found=19544, basic_filters_failed=11509, move_not_fresh=4324, breakout_stale=1134, retest_proximity_failed=600, insufficient_candles=106, volume_spike_missing=86, move_exhausted=19, ema_alignment_reject=6, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=31598): cls_disabled_merged_into_lsr=31598
- **EVAL::DIVERGENCE_CONTINUATION** (total=29826): cvd_divergence_failed=10978, basic_filters_failed=9560, h1_trend_not_aligned=5958, ema_alignment_reject=2660, retest_proximity_failed=307, missing_fvg_or_orderblock=191, regime_blocked=171, cvd_insufficient=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=31233): auction_not_detected=18875, basic_filters_failed=9124, regime_blocked=1414, reclaim_hold_failed=1125, tail_too_small=682, rsi_reject=13
- **EVAL::FUNDING_EXTREME** (total=32462): funding_not_extreme=21305, basic_filters_failed=10051, ema_alignment_reject=468, rsi_reject=335, missing_funding_rate=186, cvd_divergence_failed=58, momentum_reject=29, missing_fvg_or_orderblock=17, insufficient_candles=13
- **EVAL::LIQUIDATION_REVERSAL** (total=29129): cascade_threshold_not_met=18853, basic_filters_failed=9946, cvd_divergence_failed=134, rsi_reject=115, insufficient_candles=68, missing_fvg_or_orderblock=11, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=31666): no_ma_cross=21758, basic_filters_failed=9570, ma_cross_htf_misaligned=172, ma_cross_cooldown=159, ma_cross_htf_unconfirmed=7
- **EVAL::MEAN_REVERT** (total=30666): no_extension=23714, basic_filters_failed=6813, insufficient_candles=139
- **EVAL::MOVER_AVWAP_SCALP** (total=41084): no_avwap_tag=14465, basic_filters_failed=10948, no_mover_leg=10429, avwap_slope_against=2547, insufficient_candles=1500, avwap_reclaim_no_volume=715, no_avwap_reclaim=478, anchor_too_recent=2
- **EVAL::MOVER_TREND_PULLBACK** (total=34192): mover_run_too_small=14743, basic_filters_failed=10883, no_reclaim=6095, insufficient_candles=1500, no_pullback_tag=971
- **EVAL::OPENING_RANGE_BREAKOUT** (total=32356): feature_disabled=32356
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=31602): regime_blocked=21010, breakout_not_found=6220, basic_filters_failed=3103, adx_reject=1244, ema_alignment_reject=25
- **EVAL::QUIET_COMPRESSION_BREAK** (total=31346): regime_blocked=11960, compression_not_detected=9852, basic_filters_failed=6015, breakout_not_detected=3271, volume_confirmation_failed=219, rsi_reject=28, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=31488): no_range_edge=24269, basic_filters_failed=6569, insufficient_candles=650
- **EVAL::SR_FLIP_RETEST** (total=31354): flip_close_not_confirmed=19086, basic_filters_failed=9106, regime_blocked=1409, long_break_volume_thin=755, h1_break_not_confirmed=423, retest_out_of_zone=404, reclaim_hold_failed=96, long_acceptance_not_held=27, ema_alignment_reject=14, whipsaw_flip=14, wick_quality_failed=14, missing_fvg_or_orderblock=6
- **EVAL::STANDARD** (total=27207): momentum_reject=7692, adx_reject=6044, basic_filters_failed=5631, sweeps_not_detected=3885, macd_reject=1897, ema_alignment_reject=1224, htf_poi_unanchored=780, invalid_sl_geometry=29, rsi_reject=25
- **EVAL::TREND_PULLBACK** (total=27874): h1_trend_not_aligned=7391, h1_pullback_not_confirmed=5716, basic_filters_failed=5286, ema_alignment_reject=3279, no_ema_reclaim_close=1785, ema_not_tested_prev=1727, body_conviction_fail=956, rsi_reject=629, regime_blocked=451, prev_already_above_emas=166, prev_already_below_emas=140, no_prev_low_break=119, no_prev_high_break=106, momentum_flat=64, momentum_reject=43, ema21_not_tagged=12, missing_fvg_or_orderblock=4
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=37336): breakout_not_found=20242, basic_filters_failed=11508, move_not_fresh=3794, breakout_stale=1094, retest_proximity_failed=462, insufficient_candles=106, volume_spike_missing=104, ema_alignment_reject=22, rsi_reject=2, missing_fvg_or_orderblock=1, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=29131): momentum_reject=17970, recent_ticks_insufficient=7670, basic_filters_failed=3491

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=10): execution:overextended=10
- **DIVERGENCE_CONTINUATION** (total=69): setup_compat:regime_VOLATILE_UNSUITABLE=69
- **FAILED_AUCTION_RECLAIM** (total=717): execution:overextended=530, setup_compat:regime_STRONG_TREND=172, context_floor=15
- **FUNDING_EXTREME_SIGNAL** (total=202): execution:trigger_not_confirmed=202
- **LIQUIDATION_REVERSAL** (total=12): execution:trigger_not_confirmed=12
- **LIQUIDITY_SWEEP_REVERSAL** (total=1124): execution:overextended=492, execution:trigger_not_confirmed=395, setup_compat:regime_STRONG_TREND=237
- **MA_CROSS_TREND_SHIFT** (total=3): setup_compat:regime_CLEAN_RANGE=2, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=2170): setup_compat:regime_WEAK_TREND=1282, setup_compat:regime_STRONG_TREND=730, execution:overextended=151, entry_quality=7
- **MOVER_AVWAP_SCALP** (total=398): execution:overextended=309, execution:trigger_not_confirmed=58, entry_quality=31
- **MOVER_TREND_PULLBACK** (total=7504): execution:overextended=4413, execution:trigger_not_confirmed=2374, entry_quality=717
- **QUIET_COMPRESSION_BREAK** (total=6): execution:trigger_not_confirmed=6
- **RANGE_FADE** (total=2163): setup_compat:regime_WEAK_TREND=729, setup_compat:regime_STRONG_TREND=656, setup_compat:regime_VOLATILE_UNSUITABLE=390, execution:overextended=310, context_edge=77, entry_quality=1
- **TREND_PULLBACK_EMA** (total=718): setup_compat:regime_CLEAN_RANGE=484, setup_compat:regime_DIRTY_RANGE=219, setup_compat:regime_VOLATILE_UNSUITABLE=9, entry_quality=6
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1
- **WHALE_MOMENTUM** (total=575): execution:trigger_not_confirmed=575

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 71468 | 36.2% |
| QUIET | 45537 | 23.0% |
| TRENDING_DOWN | 40224 | 20.4% |
| TRENDING_UP | 26270 | 13.3% |
| VOLATILE | 14081 | 7.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **169**
- Average confidence gap to threshold: **13.92** (samples=169) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=26, AVAXUSDT=25, AAVEUSDT=17, SOLUSDT=12, ONDOUSDT=8, 1000PEPEUSDT=8, XRPUSDT=7, SUIUSDT=7, LINKUSDT=6, WLDUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 10 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 66 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 8 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 32 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 14 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 89 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 11 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 41 |
| MEAN_REVERT | filtered | min_confidence | 2 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 73 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 60 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 17 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 302 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 712 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 29 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2770 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 86 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 8 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 101 |
| RANGE_FADE | filtered | min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 15 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 9 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 55 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 10 | 81.45 | 65.00 | -16.45 | 19.65 | 16.61 | 20.00 | 4.65 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 74 | 57.41 | 64.24 | 6.83 | 20.42 | 19.53 | 18.10 | -0.16 | 9.32 |
| DIVERGENCE_CONTINUATION | kept | 32 | 68.21 | 65.00 | -3.21 | 20.98 | 19.79 | 17.62 | 1.47 | 2.12 |
| FAILED_AUCTION_RECLAIM | filtered | 18 | 52.50 | 63.67 | 11.17 | 20.67 | 20.00 | 20.00 | 1.00 | 8.00 |
| FAILED_AUCTION_RECLAIM | kept | 89 | 70.35 | 65.00 | -5.35 | 19.46 | 19.74 | 20.00 | 2.98 | 2.63 |
| LIQUIDATION_REVERSAL | filtered | 11 | 72.70 | 10.00 | -62.70 | 20.72 | 8.00 | 19.20 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11 | 55.13 | 65.00 | 9.87 | 20.78 | 19.96 | 18.09 | 2.91 | 13.82 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 41 | 69.75 | 65.00 | -4.75 | 20.34 | 19.79 | 17.98 | 1.24 | 0.00 |
| MEAN_REVERT | filtered | 4 | 58.83 | 65.00 | 6.17 | 21.10 | 16.40 | 16.55 | 0.00 | 12.20 |
| MEAN_REVERT | kept | 73 | 73.40 | 65.00 | -8.40 | 21.21 | 17.09 | 18.81 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 79 | 60.28 | 52.97 | -7.31 | 21.07 | 16.43 | 15.80 | 4.15 | 9.19 |
| MOVER_AVWAP_SCALP | kept | 302 | 75.94 | 65.00 | -10.94 | 20.98 | 16.11 | 15.80 | 4.10 | 0.33 |
| MOVER_TREND_PULLBACK | filtered | 741 | 54.76 | 64.04 | 9.28 | 20.41 | 18.56 | 15.80 | 4.51 | 18.83 |
| MOVER_TREND_PULLBACK | kept | 2770 | 76.99 | 65.00 | -11.99 | 20.28 | 18.42 | 15.80 | 4.41 | 0.39 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 70.70 | 65.00 | -5.70 | 20.30 | 20.00 | 17.80 | 4.50 | 10.80 |
| QUIET_COMPRESSION_BREAK | filtered | 94 | 51.18 | 65.00 | 13.82 | 20.99 | 19.82 | 20.00 | 0.00 | 8.22 |
| QUIET_COMPRESSION_BREAK | kept | 101 | 73.47 | 65.00 | -8.47 | 21.41 | 19.23 | 20.00 | 0.00 | -0.52 |
| RANGE_FADE | filtered | 4 | 63.03 | 65.00 | 1.97 | 20.97 | 14.00 | 18.60 | 0.00 | 4.80 |
| SR_FLIP_RETEST | kept | 15 | 66.53 | 65.00 | -1.53 | 19.60 | 20.00 | 16.88 | 1.10 | 6.00 |
| TREND_PULLBACK_EMA | filtered | 13 | 58.65 | 65.00 | 6.35 | 22.12 | 19.91 | 19.08 | 4.77 | 17.54 |
| TREND_PULLBACK_EMA | kept | 55 | 79.31 | 65.00 | -14.31 | 20.89 | 19.93 | 17.46 | 4.79 | -1.51 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 88.00 | 65.00 | -23.00 | 20.70 | 14.00 | 20.00 | 6.00 | 3.00 |
| WHALE_MOMENTUM | filtered | 19 | 35.45 | 65.00 | 29.55 | 22.70 | 14.00 | 17.00 | 0.00 | 16.82 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 10 | 81.45 | 17.80 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.65 |
| DIVERGENCE_CONTINUATION | filtered | 74 | 57.41 | 24.46 | 15.84 | 4.38 | 10.81 | 5.61 | 8.63 | -0.16 |
| DIVERGENCE_CONTINUATION | kept | 32 | 68.21 | 23.50 | 15.50 | 4.59 | 12.00 | 5.91 | 8.02 | 1.47 |
| FAILED_AUCTION_RECLAIM | filtered | 18 | 52.50 | 17.00 | 17.11 | 8.00 | 13.00 | 6.94 | 4.11 | 1.00 |
| FAILED_AUCTION_RECLAIM | kept | 89 | 70.35 | 23.83 | 14.49 | 4.96 | 12.12 | 5.29 | 9.30 | 2.98 |
| LIQUIDATION_REVERSAL | filtered | 11 | 72.70 | 25.00 | 8.00 | 12.00 | 8.00 | 8.00 | 7.70 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11 | 55.13 | 22.82 | 14.00 | 4.64 | 12.18 | 5.00 | 7.40 | 2.91 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 41 | 69.75 | 24.46 | 14.49 | 4.10 | 13.59 | 5.79 | 6.08 | 1.24 |
| MEAN_REVERT | filtered | 4 | 58.83 | 23.00 | 17.00 | 9.75 | 12.00 | 7.50 | 5.53 | 0.00 |
| MEAN_REVERT | kept | 73 | 73.40 | 23.90 | 16.08 | 7.44 | 12.00 | 7.53 | 6.44 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 79 | 60.28 | 17.23 | 18.00 | 8.94 | 13.65 | 5.94 | 8.02 | 4.15 |
| MOVER_AVWAP_SCALP | kept | 302 | 75.94 | 18.85 | 18.04 | 8.98 | 12.85 | 6.00 | 7.66 | 4.10 |
| MOVER_TREND_PULLBACK | filtered | 741 | 54.76 | 17.97 | 18.00 | 7.93 | 12.73 | 5.69 | 8.72 | 4.51 |
| MOVER_TREND_PULLBACK | kept | 2770 | 76.99 | 19.11 | 18.01 | 8.20 | 13.18 | 5.81 | 9.01 | 4.41 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 70.70 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 94 | 51.18 | 18.11 | 17.66 | 11.04 | 14.00 | 7.28 | 4.23 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 101 | 73.47 | 17.95 | 17.13 | 11.32 | 14.06 | 6.09 | 7.61 | 0.00 |
| RANGE_FADE | filtered | 4 | 63.03 | 25.00 | 14.00 | 3.00 | 15.00 | 5.00 | 5.83 | 0.00 |
| SR_FLIP_RETEST | kept | 15 | 66.53 | 17.53 | 18.00 | 14.60 | 14.00 | 5.00 | 2.30 | 1.10 |
| TREND_PULLBACK_EMA | filtered | 13 | 58.65 | 18.23 | 18.00 | 8.08 | 14.23 | 6.46 | 8.72 | 4.77 |
| TREND_PULLBACK_EMA | kept | 55 | 79.31 | 18.35 | 18.00 | 8.35 | 14.60 | 6.48 | 9.47 | 4.79 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 88.00 | 25.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.00 | 6.00 |
| WHALE_MOMENTUM | filtered | 19 | 35.45 | 25.00 | 8.00 | 8.53 | 14.47 | 6.68 | 4.59 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 10 | 81.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 74 | 57.41 | 0.00 | 0.00 | 0.52 | 0.00 | 1.46 | 0.00 | 0.00 | 0.00 | **1.98** |
| DIVERGENCE_CONTINUATION | kept | 32 | 68.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 18 | 52.50 | 0.00 | 0.00 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| FAILED_AUCTION_RECLAIM | kept | 89 | 70.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 11 | 72.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 11 | 55.13 | 0.00 | 0.00 | 13.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **13.82** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 41 | 69.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 4 | 58.83 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.20** |
| MEAN_REVERT | kept | 73 | 73.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 79 | 60.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.85 | **1.85** |
| MOVER_AVWAP_SCALP | kept | 302 | 75.94 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.28 | **0.44** |
| MOVER_TREND_PULLBACK | filtered | 741 | 54.76 | 0.86 | 0.00 | 2.12 | 0.00 | 0.57 | 0.01 | 0.00 | 0.00 | **3.56** |
| MOVER_TREND_PULLBACK | kept | 2770 | 76.99 | 0.01 | 0.00 | 0.10 | 0.00 | 0.24 | 0.00 | 0.00 | 0.01 | **0.36** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 70.70 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 94 | 51.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 7.01 | **7.42** |
| QUIET_COMPRESSION_BREAK | kept | 101 | 73.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.11 | **0.28** |
| RANGE_FADE | filtered | 4 | 63.03 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| SR_FLIP_RETEST | kept | 15 | 66.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 13 | 58.65 | 0.00 | 0.00 | 0.00 | 0.00 | 8.31 | 0.00 | 0.00 | 0.00 | **8.31** |
| TREND_PULLBACK_EMA | kept | 55 | 79.31 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.23** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 88.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 19 | 35.45 | 0.00 | 0.00 | 0.00 | 0.00 | 6.82 | 0.00 | 0.00 | 0.00 | **6.82** |

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
- Outcomes recorded: **135923 held of 253066 seen** across 21 strategies; 3066 cells past the sample floor; **1095 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 32267 | 203/32064/0 | 50% | -0.05 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17113 | 24/17089/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16578 | 1/16577/0 | 48% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11862 | 4/11858/0 | 45% | -0.11 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9498 | 0/9498/0 | 48% | -0.07 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 9096 | 27/9069/0 | 34% | -0.31 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| TREND_PULLBACK_EMA | 5407 | 2/5405/0 | 47% | -0.23 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_MEAN_REVERT | 4999 | 0/0/4999 | 43% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.73R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL (-0.97R) |
| LIQUIDITY_SWEEP_REVERSAL | 4910 | 11/4899/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4544 | 0/0/4544 | 38% | +0.05 | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.82R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.26R) |
| MEAN_REVERT | 4306 | 0/4306/0 | 72% | +0.42 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.29R) |
| SHADOW_FUNDING_FADE | 4103 | 0/0/4103 | 38% | -0.34 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.20R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 3684 | 0/3684/0 | 27% | -0.51 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2543 | 19/2524/0 | 42% | +0.05 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2326 | 4/2322/0 | 32% | -0.45 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.34R) |
| WHALE_MOMENTUM | 1484 | 0/1484/0 | 46% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.81R) |
| SHADOW_CASCADE_REVERSAL | 521 | 0/0/521 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.04R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.76R) |
| BREAKDOWN_SHORT | 451 | 9/442/0 | 48% | +0.01 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 73 | 0/73/0 | 85% | +0.69 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 30 | 1/29/0 | 37% | -0.40 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `RANGE_FADE @ ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP` -1.38R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 107 | 35% / -0.42R | 107 | 57% / -0.08R | +0.33 | **ATR** |
| TREND_PULLBACK_EMA | 198 | 43% / -0.29R | 198 | 46% / -0.13R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 547 | 39% / -0.21R | 547 | 42% / -0.11R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 2776 | 46% / -0.20R | 2776 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 878 | 47% / -0.12R | 878 | 53% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 717 | 50% / -0.19R | 717 | 54% / -0.13R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4045 | 51% / -0.06R | 4045 | 55% / -0.01R | +0.05 | **ATR** |
| WHALE_MOMENTUM | 112 | 51% / -0.25R | 112 | 50% / -0.30R | -0.05 | **FIXED** |
| MEAN_REVERT | 443 | 54% / +0.01R | 443 | 51% / +0.05R | +0.04 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 81 | 41% / -0.02R | 81 | 51% / -0.05R | -0.03 | **FIXED** |
| RANGE_FADE | 237 | 19% / -0.65R | 237 | 21% / -0.62R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1481 | 44% / -0.13R | 1481 | 44% / -0.16R | -0.03 | **FIXED** |
| BREAKDOWN_SHORT | 20 | 30% / -0.27R | 20 | 30% / -0.25R | +0.02 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2285 | 47% / -0.11R | 2285 | 47% / -0.11R | +0.00 | **ATR** |
| MA_CROSS_TREND_SHIFT | 13 | 31% / -0.26R | 13 | 31% / -0.24R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 9 | 56% / +0.07R | 9 | 56% / -0.01R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 5697 | 30% | -0.12R | 281 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 537 | 41% | -0.11R | 134 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 34 | 59% | +0.01R | 20 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1233 | 28% / -1.68R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 21 | 19% / -0.85R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4686 | 39% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 989 | 32% / -0.57R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 92 | 23% / -0.86R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 705 | 31% / -1.58R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 986 | 35% / -0.14R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 351 | 43% / -1.03R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 123 | 29% / -1.26R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 219 | 30% / -0.63R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 593 | 32% / -0.28R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 16 | 25% / -0.77R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 179 | 44% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 69 | 41% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 6 | 17% / -0.84R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 31 | 45% / -0.36R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 45 · alerting: **3** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 39/6) (sustained 39 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.45R (bound 0.3) (streak 39/6) (sustained 39 cycles)
- **ALERT** `tuned_variants` — 17 non-stamps — atr_arm_uncomputable=17 (seen=1465 stamped=200 skipped=1248) (streak 13/6) (sustained 13 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 2955296 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 6 arms current, none stalled; covering 55/55 signals (100%) | 0 |
| auto_dispatch | ok | attempts=1 fanouts=1 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 63722.60 | 0 |
| candle_coverage | ok | 88/91 symbols with ≥20 15m candles, 85/91 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 869 dup bars, 0 undedupable; ws 0 out-of-order, 113 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 39/6) | 39 |
| context_emission_policy | ok | output +8 / upstream +20 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 185/185 signals (100%) | 0 |
| dark_resolution | ok | 56 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 203/203 signals (100%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 1302611 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.45R (bound 0.3) (streak 39/6) | 39 |
| emission_controller | ok | last cycle 1467s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4139 stamps (MEAN_REVERT=753, MOVER_AVWAP_SCALP=158, MOVER_TREND_PULLBACK=2610, RANGE_FADE=460, TREND_PULLBACK_EMA=158), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 5/6) | 5 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +9 / upstream +107 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | backlog 6 detections since last emission | 0 |
| mean_revert_path | ok | output +1 / upstream +107 | 0 |
| mover_admission_metadata | ok | 859 symbols known, 157 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3101 rows held, 423252 evicted (sampled: execution:overextended 400/156506, execution:trigger_not_confirmed 400/143513, setup_compat:regime_STRONG_TREND 400/52783) | 0 |
| price_action_lane | ok | 53997 evaluated, 90 emitted; layer1 90 stamped / 0 blind; cooldown=5190, delta_opposed=3962, no_footprint=18351, no_opposing_target=15, no_sweep=22640, rr_below_floor=3749 | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | ok | emitted_total=0 context_blocked=66 | 0 |
| range_fade_path | ok | output +22 / upstream +107 | 0 |
| sar_alignment_crosscheck | ok | 172/4069 disagreed (4.2%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +107 | 0 |
| sar_hold_arm | ok | 105 held arms settled, 18 unscored, 5 still walking (5 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 13/130 unfetchable (10%); top cause: gap or duplicate bar in the 15m window; symbols: GRVTUSDT, HOLOUSDT, INJUSDT, LITUSDT, LUNA2USDT +1 more | 0 |
| sar_live_arms | ok | 6 arms current, none stalled; covering 64/64 signals (100%) | 0 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 7 resolved, 110 still mid-window | 0 |
| setup_tf_resolver | ok | 30076 resolutions, 21792 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +61 / upstream +107 | 0 |
| structural_snap | ok | 3326/3326 measured, 11 blind, 0 levels moved (refusals: redetect_cooldown=400) | 0 |
| structural_veto_lane | ok | 550 stamped; 0 with no readable level book, 2 with clear air ahead, 474 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +107 / upstream +20 | 0 |
| tuned_variants | violating | 17 non-stamps — atr_arm_uncomputable=17 (seen=1465 stamped=200 skipped=1248) (streak 13/6) | 13 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `69653`
- `Path funnel` emissions: `23`
- `Regime distribution` emissions: `23`
- `QUIET_SCALP_BLOCK` events: `169`
- `confidence_gate` events: `4558`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 5261 | 5261 | 5261 | 0 |
| futures_depth | 2 | 10626 | 10626 | 18221 | 0 |
| futures_liq | 1 | 14526 | 14526 | 14526 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| regime_shift | 3 |
| signal_close | 3 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=151911] state[populated=151911] buckets[few=6, many=151823, some=82] sources[none] quality[none]
- funding_rate: presence[absent=18631, present=133280] state[empty=18631, populated=133280] buckets[few=133280, none=18631] sources[none] quality[none]
- liquidation_clusters: presence[absent=89725, present=62186] state[empty=89725, populated=62186] buckets[few=50571, none=89725, some=11615] sources[none] quality[none]
- oi_snapshot: presence[absent=18182, present=133729] state[empty=18182, populated=133729] buckets[few=61, many=133147, none=18182, some=521] sources[none] quality[none]
- order_book: presence[absent=54911, present=97000] state[populated=97000, unavailable=54911] buckets[few=97000, none=54911] sources[book_ticker=97000, unavailable=54911] quality[none=54911, top_of_book_only=97000]
- orderblocks: presence[absent=151911] state[empty=151911] buckets[none=151911] sources[measured_dark=151859, not_implemented=52] quality[none]
- recent_ticks: presence[absent=1242, present=150669] state[empty=1242, populated=150669] buckets[many=150669, none=1242] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `20.610883951187134` sec
- Median create→first breach: `2034.649442076683` sec
- Median create→terminal: `2289.074370622635` sec
- Median first breach→terminal: `12.360995531082153` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 8 | 8 | 4.634062070434696 | 3.0 | 1.5446873568115655 | 6 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 8 | 8 | 0.0 | 75.0 | 0.0 | 0.0 | -2.0647 | 2034.649442076683 | 2289.074370622635 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 111 | 1 | 25 | 0.0 | 0.0 | None | None | 86 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 801 | 9 | 691 | 0.0 | 0.0 | None | None | 110 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-208`
- Gating Δ: `-30581`
- No-generation Δ: `-966557`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -3.2265, "current_avg_pnl": -2.0647, "current_win_rate": 0.0, "previous_avg_pnl": 1.1618, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 61, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -18, "geometry_changed_delta": 0, "geometry_preserved_delta": -377, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
