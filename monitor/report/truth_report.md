# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `12` sec (warning=False)
- Latest performance record age: `9060` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 72 | 72 | 72 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2938 | 2938 | 2578 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 23926 | 23938 | 23 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 20296 | 20300 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 20043 | 19189 | 1099 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 20325 | 20192 | 173 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 20602 | 20588 | 25 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 15482 | 15492 | 3 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 20370 | 20395 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 20401 | 19594 | 1101 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 27474 | 30232 | 433 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 23964 | 19301 | 8131 | 0 | 0 | 0 | low-sample (no_reclaim) |
| EVAL::OPENING_RANGE_BREAKOUT | 20499 | 20506 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 20300 | 20324 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 20032 | 20033 | 10 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 20698 | 20218 | 669 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 19922 | 19987 | 26 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 14786 | 13854 | 1103 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 14964 | 14861 | 162 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 23877 | 23903 | 19 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 15496 | 15489 | 32 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 437 | 437 | 413 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 60 | 60 | 12 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4416 | 4416 | 4373 | 6 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 3 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2091 | 2091 | 2063 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 888 | 888 | 135 | 60 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18444 | 18444 | 8539 | 571 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 53 | 53 | 26 | 6 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1380 | 1380 | 1350 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 82 | 82 | 69 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 507 | 507 | 367 | 28 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 49 | 49 | 17 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 908 | 908 | 12 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=23938): breakout_not_found=18027, basic_filters_failed=2626, move_not_fresh=1819, breakout_stale=930, retest_proximity_failed=342, volume_spike_missing=117, insufficient_candles=71, missing_fvg_or_orderblock=4, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=20300): cls_disabled_merged_into_lsr=20300
- **EVAL::DIVERGENCE_CONTINUATION** (total=19189): cvd_divergence_failed=12452, h1_trend_not_aligned=2321, basic_filters_failed=2145, ema_alignment_reject=1556, retest_proximity_failed=471, regime_blocked=141, missing_fvg_or_orderblock=103
- **EVAL::FAILED_AUCTION_RECLAIM** (total=20192): auction_not_detected=16211, basic_filters_failed=2052, regime_blocked=856, reclaim_hold_failed=606, tail_too_small=437, rsi_reject=30
- **EVAL::FUNDING_EXTREME** (total=20588): funding_not_extreme=17442, basic_filters_failed=2202, missing_funding_rate=394, ema_alignment_reject=285, rsi_reject=237, momentum_reject=12, cvd_divergence_failed=12, insufficient_candles=4
- **EVAL::LIQUIDATION_REVERSAL** (total=15492): cascade_threshold_not_met=12912, basic_filters_failed=2190, rsi_reject=167, cvd_divergence_failed=157, insufficient_candles=59, missing_fvg_or_orderblock=4, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=20395): no_ma_cross=17910, basic_filters_failed=2148, ma_cross_cooldown=326, ma_cross_htf_misaligned=11
- **EVAL::MEAN_REVERT** (total=19594): no_extension=17832, basic_filters_failed=1753, insufficient_candles=9
- **EVAL::MOVER_AVWAP_SCALP** (total=30232): no_avwap_tag=16050, no_mover_leg=5949, avwap_slope_against=3207, basic_filters_failed=2692, avwap_reclaim_no_volume=1311, no_avwap_reclaim=818, insufficient_candles=202, anchor_too_recent=3
- **EVAL::MOVER_TREND_PULLBACK** (total=19301): no_reclaim=8484, mover_run_too_small=6147, basic_filters_failed=2659, no_pullback_tag=1746, insufficient_candles=265
- **EVAL::OPENING_RANGE_BREAKOUT** (total=20506): feature_disabled=20506
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=20324): regime_blocked=10253, breakout_not_found=8342, basic_filters_failed=896, adx_reject=736, ema_alignment_reject=97
- **EVAL::QUIET_COMPRESSION_BREAK** (total=20033): regime_blocked=10786, compression_not_detected=7566, basic_filters_failed=1154, breakout_not_detected=490, volume_confirmation_failed=35, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=20218): no_range_edge=18384, basic_filters_failed=1754, insufficient_candles=80
- **EVAL::SR_FLIP_RETEST** (total=19987): flip_close_not_confirmed=15597, basic_filters_failed=2045, regime_blocked=839, long_break_volume_thin=572, retest_out_of_zone=508, h1_break_not_confirmed=239, reclaim_hold_failed=64, long_acceptance_not_held=49, ema_alignment_reject=37, whipsaw_flip=28, wick_quality_failed=9
- **EVAL::STANDARD** (total=13854): momentum_reject=4767, adx_reject=2707, ema_alignment_reject=1968, sweeps_not_detected=1812, basic_filters_failed=1290, macd_reject=1041, htf_poi_unanchored=227, rsi_reject=27, invalid_sl_geometry=15
- **EVAL::TREND_PULLBACK** (total=14861): h1_pullback_not_confirmed=3993, ema_alignment_reject=2364, ema_not_tested_prev=2162, h1_trend_not_aligned=2124, basic_filters_failed=1354, no_ema_reclaim_close=1138, body_conviction_fail=585, rsi_reject=571, prev_already_above_emas=198, no_prev_high_break=139, regime_blocked=115, momentum_flat=42, prev_already_below_emas=32, ema21_not_tagged=20, momentum_reject=11, missing_fvg_or_orderblock=7, no_prev_low_break=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=23903): breakout_not_found=13977, move_not_fresh=4750, basic_filters_failed=2626, breakout_stale=1597, retest_proximity_failed=754, volume_spike_missing=121, insufficient_candles=71, missing_fvg_or_orderblock=4, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=15489): momentum_reject=9272, recent_ticks_insufficient=5530, basic_filters_failed=686, insufficient_candles=1

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=14): execution:overextended=14
- **DIVERGENCE_CONTINUATION** (total=118): setup_compat:regime_VOLATILE_UNSUITABLE=109, setup_compat:regime_BREAKOUT_EXPANSION=8, execution:overextended=1
- **FAILED_AUCTION_RECLAIM** (total=170): setup_compat:regime_STRONG_TREND=90, execution:overextended=80
- **FUNDING_EXTREME_SIGNAL** (total=54): execution:trigger_not_confirmed=54
- **LIQUIDATION_REVERSAL** (total=7): execution:trigger_not_confirmed=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=1405): setup_compat:regime_STRONG_TREND=565, execution:overextended=506, execution:trigger_not_confirmed=334
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_DIRTY_RANGE=2, execution:trigger_not_confirmed=2, execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=1670): setup_compat:regime_STRONG_TREND=952, setup_compat:regime_WEAK_TREND=471, execution:overextended=247
- **MOVER_AVWAP_SCALP** (total=499): execution:overextended=394, execution:trigger_not_confirmed=83, entry_quality=22
- **MOVER_TREND_PULLBACK** (total=8372): execution:trigger_not_confirmed=3980, execution:overextended=2905, entry_quality=1487
- **RANGE_FADE** (total=947): setup_compat:regime_STRONG_TREND=584, setup_compat:regime_WEAK_TREND=343, setup_compat:regime_VOLATILE_UNSUITABLE=14, execution:overextended=6
- **TREND_PULLBACK_EMA** (total=359): setup_compat:regime_CLEAN_RANGE=226, setup_compat:regime_DIRTY_RANGE=110, setup_compat:regime_VOLATILE_UNSUITABLE=18, entry_quality=5
- **WHALE_MOMENTUM** (total=686): execution:trigger_not_confirmed=678, execution:overextended=8

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 37630 | 36.0% |
| TRENDING_UP | 32345 | 30.9% |
| TRENDING_DOWN | 20154 | 19.3% |
| QUIET | 10271 | 9.8% |
| VOLATILE | 4273 | 4.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **174**
- Average confidence gap to threshold: **7.64** (samples=174) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=51, DOTUSDT=38, BTCUSDT=20, ETCUSDT=10, ETHUSDT=7, LDOUSDT=6, BNBUSDT=6, LTCUSDT=5, AAVEUSDT=4, FILUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 55 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 137 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 3 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 9 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 86 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 501 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 237 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 146 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5712 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 24 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 14 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 127 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 35 |
| WHALE_MOMENTUM | filtered | min_confidence | 88 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 55 | 59.01 | 64.78 | 5.77 | 20.95 | 19.78 | 18.06 | 0.64 | 10.07 |
| DIVERGENCE_CONTINUATION | kept | 137 | 72.98 | 65.00 | -7.98 | 21.00 | 19.45 | 18.28 | 2.21 | -0.15 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 68.20 | 65.00 | -3.20 | 20.73 | 19.37 | 20.00 | 4.17 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 57.30 | 61.00 | 3.70 | 18.30 | 14.00 | 17.00 | 6.00 | 12.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 80.50 | 65.00 | -15.50 | 20.70 | 19.40 | 14.20 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 58.20 | 61.00 | 2.80 | 20.63 | 19.07 | 16.67 | 3.00 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.41 | 65.00 | -2.41 | 20.38 | 18.96 | 17.88 | 1.44 | 2.31 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.60 | 65.00 | -1.60 | 21.20 | 15.55 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 3 | 70.00 | 65.00 | -5.00 | 20.80 | 14.60 | 15.60 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 86 | 57.95 | 64.81 | 6.86 | 20.39 | 14.98 | 15.80 | 3.87 | 7.26 |
| MOVER_AVWAP_SCALP | kept | 501 | 78.91 | 65.00 | -13.91 | 20.83 | 16.37 | 15.80 | 4.67 | 0.68 |
| MOVER_TREND_PULLBACK | filtered | 383 | 56.86 | 64.60 | 7.74 | 20.31 | 19.19 | 15.80 | 4.55 | 15.85 |
| MOVER_TREND_PULLBACK | kept | 5712 | 77.73 | 65.00 | -12.73 | 20.60 | 18.83 | 15.80 | 4.68 | 1.22 |
| QUIET_COMPRESSION_BREAK | filtered | 7 | 60.66 | 65.00 | 4.34 | 21.06 | 19.53 | 20.00 | 0.00 | 12.09 |
| QUIET_COMPRESSION_BREAK | kept | 24 | 73.51 | 65.00 | -8.51 | 21.12 | 19.11 | 20.00 | 0.00 | 1.24 |
| SR_FLIP_RETEST | filtered | 1 | 44.00 | 65.00 | 21.00 | 21.20 | 20.00 | 15.20 | 2.50 | 23.80 |
| SR_FLIP_RETEST | kept | 1 | 69.50 | 65.00 | -4.50 | 20.60 | 20.00 | 16.90 | 2.50 | 3.00 |
| TREND_PULLBACK_EMA | filtered | 17 | 56.06 | 65.00 | 8.94 | 20.87 | 19.75 | 16.38 | 4.94 | 18.29 |
| TREND_PULLBACK_EMA | kept | 127 | 79.27 | 65.00 | -14.27 | 21.11 | 19.68 | 18.09 | 5.03 | 0.34 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 63.70 | 65.00 | 1.30 | 21.20 | 17.30 | 20.00 | 4.00 | 11.00 |
| VOLUME_SURGE_BREAKOUT | kept | 35 | 76.93 | 65.00 | -11.93 | 20.69 | 18.11 | 20.00 | 5.06 | 3.39 |
| WHALE_MOMENTUM | filtered | 105 | 56.42 | 64.24 | 7.82 | 23.89 | 16.42 | 17.00 | 0.00 | 11.95 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 55 | 59.01 | 23.55 | 16.00 | 3.93 | 11.40 | 4.67 | 8.90 | 0.64 |
| DIVERGENCE_CONTINUATION | kept | 137 | 72.98 | 23.31 | 17.34 | 5.15 | 11.88 | 5.43 | 8.81 | 2.21 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 68.20 | 25.00 | 16.67 | 5.00 | 11.67 | 6.33 | 4.37 | 4.17 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 57.30 | 17.00 | 20.00 | 3.00 | 9.00 | 5.00 | 9.30 | 6.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 80.50 | 25.00 | 20.00 | 9.00 | 14.00 | 2.50 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 58.20 | 17.00 | 14.00 | 7.00 | 12.33 | 5.00 | 7.87 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.41 | 20.78 | 14.44 | 6.00 | 14.44 | 6.67 | 5.94 | 1.44 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.60 | 21.00 | 14.00 | 7.50 | 11.50 | 3.75 | 8.85 | 0.00 |
| MEAN_REVERT | kept | 3 | 70.00 | 25.00 | 14.00 | 3.00 | 12.00 | 10.00 | 6.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 86 | 57.95 | 20.42 | 18.05 | 9.35 | 12.64 | 5.55 | 6.15 | 3.87 |
| MOVER_AVWAP_SCALP | kept | 501 | 78.91 | 19.32 | 18.01 | 9.69 | 13.14 | 6.04 | 9.32 | 4.67 |
| MOVER_TREND_PULLBACK | filtered | 383 | 56.86 | 18.33 | 18.07 | 8.06 | 13.71 | 5.81 | 8.84 | 4.55 |
| MOVER_TREND_PULLBACK | kept | 5712 | 77.73 | 19.40 | 18.02 | 8.23 | 13.27 | 5.86 | 9.60 | 4.68 |
| QUIET_COMPRESSION_BREAK | filtered | 7 | 60.66 | 18.14 | 18.00 | 12.43 | 14.00 | 6.50 | 3.67 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 24 | 73.51 | 17.33 | 17.00 | 10.62 | 14.00 | 6.92 | 9.75 | 0.00 |
| SR_FLIP_RETEST | filtered | 1 | 44.00 | 25.00 | 8.00 | 3.00 | 17.00 | 10.00 | 2.30 | 2.50 |
| SR_FLIP_RETEST | kept | 1 | 69.50 | 25.00 | 18.00 | 3.00 | 11.00 | 5.00 | 8.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 17 | 56.06 | 10.41 | 18.00 | 10.06 | 14.00 | 7.94 | 9.00 | 4.94 |
| TREND_PULLBACK_EMA | kept | 127 | 79.27 | 18.98 | 18.00 | 7.62 | 14.28 | 7.53 | 9.12 | 5.03 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 63.70 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 8.70 | 4.00 |
| VOLUME_SURGE_BREAKOUT | kept | 35 | 76.93 | 21.11 | 16.57 | 12.09 | 11.43 | 5.43 | 9.07 | 5.06 |
| WHALE_MOMENTUM | filtered | 105 | 56.42 | 24.92 | 16.00 | 7.83 | 12.56 | 6.48 | 0.58 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 55 | 59.01 | 0.00 | 0.00 | 2.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.56** |
| DIVERGENCE_CONTINUATION | kept | 137 | 72.98 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | **0.43** |
| FAILED_AUCTION_RECLAIM | kept | 3 | 68.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 57.30 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 80.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 58.20 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.41 | 0.00 | 0.00 | 2.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.31** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 3 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 86 | 57.95 | 0.70 | 0.00 | 0.28 | 0.00 | 0.00 | 0.12 | 0.00 | 0.25 | **1.35** |
| MOVER_AVWAP_SCALP | kept | 501 | 78.91 | 0.02 | 0.00 | 0.18 | 0.00 | 0.00 | 0.28 | 0.00 | 0.15 | **0.63** |
| MOVER_TREND_PULLBACK | filtered | 383 | 56.86 | 0.16 | 0.00 | 5.47 | 0.00 | 4.03 | 0.32 | 0.00 | 0.00 | **9.98** |
| MOVER_TREND_PULLBACK | kept | 5712 | 77.73 | 0.00 | 0.00 | 0.98 | 0.00 | 0.23 | 0.08 | 0.00 | 0.00 | **1.29** |
| QUIET_COMPRESSION_BREAK | filtered | 7 | 60.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | **10.80** |
| QUIET_COMPRESSION_BREAK | kept | 24 | 73.51 | 0.00 | 0.00 | 2.40 | 0.00 | 0.72 | 0.00 | 0.00 | 0.00 | **3.12** |
| SR_FLIP_RETEST | filtered | 1 | 44.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | **10.80** |
| SR_FLIP_RETEST | kept | 1 | 69.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 17 | 56.06 | 0.00 | 0.00 | 5.08 | 0.00 | 5.51 | 0.00 | 0.00 | 0.00 | **10.59** |
| TREND_PULLBACK_EMA | kept | 127 | 79.27 | 0.00 | 0.00 | 1.42 | 0.00 | 0.09 | 0.05 | 0.00 | 0.00 | **1.56** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 63.70 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| VOLUME_SURGE_BREAKOUT | kept | 35 | 76.93 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.69 | **0.83** |
| WHALE_MOMENTUM | filtered | 105 | 56.42 | 0.00 | 0.00 | 0.00 | 0.00 | 2.13 | 0.06 | 0.00 | 0.00 | **2.19** |

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
- Outcomes recorded: **11969 held of 20213 seen** across 19 strategies; 249 cells past the sample floor; **94 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 8693 | 8/8685/0 | 56% | +0.00 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.14R) |
| MOVER_AVWAP_SCALP | 600 | 0/600/0 | 41% | -0.25 | ASIA/MARKUP/EXPANDED/BTC_RISING (+0.07R) | ASIA/DISTRIBUTION/NORMAL/BTC_RISING/MIDCAP (-1.07R) |
| SHADOW_MEAN_REVERT | 487 | 0/0/487 | 31% | -0.41 | NY/MARKUP/CASCADE/BTC_RISING (-0.26R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.91R) |
| SHADOW_RANGE_FADE | 420 | 0/0/420 | 33% | -0.20 | NY/RANGE/NORMAL/BTC_RISING (+0.41R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.11R) |
| DIVERGENCE_CONTINUATION | 414 | 0/414/0 | 74% | +0.28 | LONDON/MARKUP/NORMAL/BTC_RISING/ALTCOIN (+0.71R) | OFF_HOURS/MARKUP/CASCADE/BTC_RISING (-0.26R) |
| WHALE_MOMENTUM | 310 | 0/310/0 | 7% | -0.74 | OFF_HOURS/MARKUP/EXPANDED/BTC_RISING (-0.22R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| TREND_PULLBACK_EMA | 286 | 0/286/0 | 46% | -0.12 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/DISTRIBUTION/EXPANDED/BTC_RISING/ALTCOIN (-0.71R) |
| SHADOW_FUNDING_FADE | 222 | 0/0/222 | 53% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.57R) | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.57R) |
| FAILED_AUCTION_RECLAIM | 158 | 2/156/0 | 32% | -0.48 | NY/MARKUP/COMPRESSED/BTC_RISING (-1.13R) | NY/MARKUP/COMPRESSED/BTC_RISING (-1.13R) |
| MEAN_REVERT | 154 | 0/154/0 | 100% | +1.13 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+0.94R) |
| QUIET_COMPRESSION_BREAK | 76 | 4/72/0 | 42% | -0.17 | — | — |
| FUNDING_EXTREME_SIGNAL | 48 | 0/48/0 | 21% | -0.21 | — | — |
| SHADOW_CASCADE_REVERSAL | 29 | 0/0/29 | 52% | -0.13 | — | — |
| VOLUME_SURGE_BREAKOUT | 28 | 0/28/0 | 43% | -0.16 | — | — |
| LIQUIDITY_SWEEP_REVERSAL | 28 | 2/26/0 | 43% | -0.25 | — | — |
| RANGE_FADE | 8 | 0/8/0 | 0% | -1.07 | — | — |
| BREAKDOWN_SHORT | 4 | 0/4/0 | 50% | -0.13 | — | — |
| SR_FLIP_RETEST | 2 | 0/2/0 | 0% | -1.30 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 0/2/0 | 0% | -0.21 | — | — |

- **Strongest cells**: `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR` +1.13R (n=27, STRONG); `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING` +1.08R (n=35, STRONG)
- **Weakest cells**: `WHALE_MOMENTUM @ LONDON/MARKUP/NORMAL/BTC_RISING/MAJOR` -1.16R (n=19, NEGATIVE); `WHALE_MOMENTUM @ LONDON/MARKUP/NORMAL/BTC_RISING` -1.16R (n=19, NEGATIVE); `MOVER_TREND_PULLBACK @ LONDON/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP` -1.14R (n=32, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 32 | 53% / -0.16R | 32 | 53% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 55 | 64% / +0.15R | 55 | 65% / +0.07R | -0.07 | **FIXED** |
| WHALE_MOMENTUM | 29 | 14% / -0.67R | 29 | 17% / -0.61R | +0.06 | **ATR** |
| MOVER_AVWAP_SCALP | 61 | 61% / +0.01R | 61 | 64% / -0.03R | -0.04 | **FIXED** |
| MOVER_TREND_PULLBACK | 1208 | 57% / +0.02R | 1208 | 61% / +0.05R | +0.03 | **ATR** |
| FAILED_AUCTION_RECLAIM | 24 | 29% / -0.43R | 24 | 29% / -0.45R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 17 | 59% / -0.03R | 17 | 59% / -0.04R | -0.01 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 10 | 40% / -0.20R | 10 | 40% / -0.34R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 6 | 17% / -0.56R | 6 | 50% / -0.07R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 10 | 40% / -0.19R | 10 | 40% / -0.12R | — | **MEASURING** |
| MEAN_REVERT | 10 | 100% / +1.04R | 10 | 100% / +1.24R | — | **MEASURING** |
| RANGE_FADE | 1 | 0% / -1.07R | 1 | 0% / -1.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 2 | 0% / -1.20R | 2 | 0% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.35R | 1 | 0% / -0.30R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 1624 | 32% | -0.04R | 111 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 61 | 59% | -0.02R | 30 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 6 | 67% | +0.05R | 6 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 17 | 18% / +0.33R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 36 | 75% / +2.80R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 1072 | 41% / +0.08R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 83 | 45% / +0.68R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 19 | 26% / -0.37R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 56 | 50% / +0.95R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 43 | 44% / +0.00R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 12 | 25% / -0.78R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 13 | 15% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 6 | 33% / -0.20R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 8 | 100% / +1.35R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 2 | 50% / -0.20R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 1 | 0% / -1.07R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 2 | 0% / -1.05R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 1 | 0% / -0.56R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 51 · alerting: **8** · boot grace active: False
- **ALERT** `scan_cycle` — last 350.21s, worst 350.21s over 1114 cycles; 387 over 60s, 91 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 163/2) (sustained 163 cycles)
- **ALERT** `dark_resolution` — 8 of 102 open dark rows are not being advanced (worst: BICOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 170/120) (sustained 170 cycles)
- **ALERT** `candle_coverage` — 105/155 symbols with ≥20 15m candles, 103/155 updated within 45m (streak 38/6) (sustained 38 cycles)
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 170/6) (sustained 170 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 376x (gate reads 0x, withheld 0x — refusal dark); last HOMEUSDT age=3538.3s (streak 116/6) (sustained 116 cycles)
- **ALERT** `mean_revert_emission` — 1010 detections since last emission (emitted_total=1) — and only 154 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 99/6) (sustained 99 cycles)
- **ALERT** `range_fade_emission` — 1420 detections since last emission (emitted_total=0) — and only 8 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 162/6) (sustained 162 cycles)
- **ALERT** `tuned_variants` — 94 non-stamps — atr_arm_uncomputable=94 (seen=4659 stamped=1185 skipped=3380) (streak 151/6) (sustained 151 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 28306562 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 10 arms current, none stalled; covering 170/170 signals (100%) | 0 |
| auto_dispatch | ok | attempts=8 fanouts=8 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 75103.30 | 0 |
| candle_coverage | violating | 105/155 symbols with ≥20 15m candles, 103/155 updated within 45m (streak 38/6) | 38 |
| candle_series_integrity | ok | merge dropped 639 dup bars, 0 undedupable; ws 0 out-of-order, 355 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 170/6) | 170 |
| context_emission_policy | ok | output +30 / upstream +3 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1279/1292 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 8 of 102 open dark rows are not being advanced (worst: BICOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 170/120) | 170 |
| dark_sar_arms | ok | no open arms; covering 1269/1282 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 6890167 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | no strategy past reconciliation sample floor yet | 0 |
| emission_controller | ok | last cycle 493s ago; live_overrides=27 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=15 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4245 stamps (MEAN_REVERT=366, MOVER_AVWAP_SCALP=229, MOVER_TREND_PULLBACK=3343, RANGE_FADE=169, TREND_PULLBACK_EMA=138), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | violating | 5040 sealed bars over 42 symbols; 2585 incomplete, 0 shape-capped (streak 1/6) | 1 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +29 / upstream +75 | 0 |
| indicator_cache_key | ok | 40405 frozen value(s) avoided; 3445 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1010 detections since last emission (emitted_total=1) — and only 154 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 99/6) | 99 |
| mean_revert_path | ok | output +16 / upstream +75 | 0 |
| mover_admission_metadata | ok | 872 symbols known, 170 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 31 held, 31 with scan counts, 29 with an activity reading (measuring only) | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s); 251 orphan(s) dropped at restore | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2911 rows held, 603264 evicted (sampled: execution:overextended 400/220363, execution:trigger_not_confirmed 400/209768, setup_compat:regime_STRONG_TREND 400/75110) | 0 |
| price_action_lane | ok | 110612 evaluated, 439 emitted; layer1 439 stamped / 0 blind; cooldown=12132, delta_opposed=9807, no_footprint=52676, no_levels=42, no_opposing_target=166, no_sweep=26303, rr_below_floor=9047 | 0 |
| promoted_pair_integrity | ok | 31/31 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 1420 detections since last emission (emitted_total=0) — and only 8 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 162/6) | 162 |
| range_fade_path | ok | output +4 / upstream +75 | 0 |
| sar_alignment_crosscheck | ok | 759/19644 disagreed (3.9%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +75 | 0 |
| sar_hold_arm | ok | 285 held arms settled, 63 unscored, 10 still walking (9 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 14/192 unfetchable (7%); top cause: gap or duplicate bar in the 15m window; symbols: FETUSDT, LINKUSDT, ONGUSDT, ORDIUSDT, PUMPUSDT +3 more | 0 |
| sar_live_arms | ok | 10 arms current, none stalled; covering 179/179 signals (100%) | 0 |
| sar_refresh_budget | ok | 8 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 174 still mid-window | 0 |
| scan_cycle | violating | last 350.21s, worst 350.21s over 1114 cycles; 387 over 60s, 91 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 163/2) | 163 |
| setup_tf_resolver | ok | 86278 resolutions, 67284 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 21s ago (33.05s to run, worst 170.94s), 1162 overrun(s) of 2753 cycles, TTL 900s; slowest engine_state=12.62s, agents=5.38s, signals=1.94s | 0 |
| stale_tf_scoring | violating | scored on stale TF 376x (gate reads 0x, withheld 0x — refusal dark); last HOMEUSDT age=3538.3s (streak 116/6) | 116 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +104 / upstream +75 | 0 |
| structural_snap | ok | 4224/4224 measured, 24 blind, 0 levels moved (refusals: redetect_cooldown=1772) | 0 |
| structural_veto_lane | ok | 2694 stamped; 0 with no readable level book, 53 with clear air ahead, 1875 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +75 / upstream +3 | 0 |
| tuned_variants | violating | 94 non-stamps — atr_arm_uncomputable=94 (seen=4659 stamped=1185 skipped=3380) (streak 151/6) | 151 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `79850`
- `Path funnel` emissions: `11`
- `Regime distribution` emissions: `11`
- `QUIET_SCALP_BLOCK` events: `174`
- `confidence_gate` events: `7215`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **11**
- Total REST-fallback activations: **4**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 21518 | 36582 | 40727 | 0 |
| futures_aggtrade | 5 | 5316 | 6143 | 8014 | 0 |
| futures_depth | 2 | 3776 | 3776 | 33158 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 4 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| signal_close | 6 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=87720] state[populated=87720] buckets[few=3, many=87649, some=68] sources[none] quality[none]
- funding_rate: presence[absent=23278, present=64442] state[empty=23278, populated=64442] buckets[few=64442, none=23278] sources[none] quality[none]
- liquidation_clusters: presence[absent=50536, present=37184] state[empty=50536, populated=37184] buckets[few=29498, none=50536, some=7686] sources[none] quality[none]
- oi_snapshot: presence[absent=22917, present=64803] state[empty=22917, populated=64803] buckets[few=134, many=63876, none=22917, some=793] sources[none] quality[none]
- order_book: presence[absent=58601, present=29119] state[populated=29119, unavailable=58601] buckets[few=29119, none=58601] sources[book_ticker=29119, unavailable=58601] quality[none=58601, top_of_book_only=29119]
- orderblocks: presence[absent=87720] state[empty=87720] buckets[none=87720] sources[measured_dark=87687, not_implemented=33] quality[none]
- recent_ticks: presence[present=87720] state[populated=87720] buckets[many=87720] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `12.909480094909668` sec
- Median create→first breach: `3052.323375940323` sec
- Median create→terminal: `3144.5976469516754` sec
- Median first breach→terminal: `5.417584180831909` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 9.1}, "under_180s": {"count": 1, "pct": 9.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.4980041198084901 | 1.7926936268644784 | 0.8356163581774891 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.77061559507523 | 1.9112761383623185 | 0.9264049079754568 | 0 | 1 |
| MOVER_TREND_PULLBACK | 7 | 7 | 2.575172686745102 | 2.5938473828446096 | 0.9422254150785926 | 3 | 4 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.7567404473988162 | 0.7999999999999922 | 0.9459255592485294 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.498 | 914.1690380573273 | 917.6355061531067 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.3223 | 93.85714077949524 | 109.00795388221741 |
| MOVER_TREND_PULLBACK | 7 | 7 | 0.0 | 71.4 | 0.0 | 0.0 | -0.6573 | 3052.323375940323 | 3144.5976469516754 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.6433 | 23612.21420586109 | 23623.26658141613 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 82 | 1 | 69 | 0.0 | 0.0 | None | None | 13 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 507 | 28 | 367 | 0.0 | 0.0 | None | None | 140 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `694`
- Gating Δ: `20036`
- No-generation Δ: `378396`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.1832, "current_avg_pnl": -0.6573, "current_win_rate": 0.0, "previous_avg_pnl": -2.8405, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 13, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 28, "geometry_changed_delta": 0, "geometry_preserved_delta": 140, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
