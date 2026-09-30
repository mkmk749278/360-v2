# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_AVWAP_SCALP, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_AVWAP_SCALP**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1460` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 221 | 221 | 183 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 14381 | 14381 | 13145 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 105251 | 105211 | 64 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 79026 | 79026 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 78660 | 76838 | 2172 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 79065 | 78148 | 969 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 84780 | 84469 | 328 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 74414 | 74428 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 79121 | 79166 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 79182 | 77035 | 3234 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 109731 | 115906 | 1017 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 105280 | 95799 | 13879 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 84223 | 84223 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 79036 | 79041 | 17 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 78626 | 78532 | 123 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 80285 | 78966 | 1958 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 78052 | 78420 | 176 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 68610 | 63527 | 5331 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 68859 | 68470 | 450 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 105203 | 105217 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 74429 | 74453 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4132 | 4132 | 3577 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 678 | 678 | 459 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 31291 | 31291 | 30288 | 26 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 7 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11100 | 11100 | 9192 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2969 | 2969 | 1565 | 38 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 46006 | 46006 | 30822 | 271 | active-healthy (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 28 | 28 | 28 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1069 | 1069 | 927 | 20 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 7435 | 7435 | 6367 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1016 | 1016 | 650 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2589 | 2589 | 2059 | 25 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 326 | 326 | 149 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=105211): breakout_not_found=64077, basic_filters_failed=24519, move_not_fresh=10314, breakout_stale=4430, retest_proximity_failed=1581, volume_spike_missing=290
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=79026): cls_disabled_merged_into_lsr=79026
- **EVAL::DIVERGENCE_CONTINUATION** (total=76838): cvd_divergence_failed=29997, h1_trend_not_aligned=25358, basic_filters_failed=14790, ema_alignment_reject=5700, retest_proximity_failed=797, missing_fvg_or_orderblock=196
- **EVAL::FAILED_AUCTION_RECLAIM** (total=78148): auction_not_detected=55255, basic_filters_failed=14276, reclaim_hold_failed=3151, regime_blocked=2964, tail_too_small=2468, rsi_reject=34
- **EVAL::FUNDING_EXTREME** (total=84469): funding_not_extreme=65030, basic_filters_failed=16437, ema_alignment_reject=1440, rsi_reject=603, cvd_divergence_failed=363, missing_funding_rate=355, momentum_reject=184, missing_fvg_or_orderblock=57
- **EVAL::LIQUIDATION_REVERSAL** (total=74428): cascade_threshold_not_met=57281, basic_filters_failed=16267, cvd_divergence_failed=472, rsi_reject=385, missing_fvg_or_orderblock=17, volume_spike_missing=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=79166): no_ma_cross=63100, basic_filters_failed=14803, ma_cross_htf_misaligned=629, ma_cross_cooldown=609, ma_cross_htf_unconfirmed=25
- **EVAL::MEAN_REVERT** (total=77035): no_extension=62933, basic_filters_failed=14102
- **EVAL::MOVER_AVWAP_SCALP** (total=115906): no_avwap_tag=46682, no_mover_leg=26157, basic_filters_failed=24707, avwap_slope_against=11650, avwap_reclaim_no_volume=3475, no_avwap_reclaim=3167, anchor_too_recent=68
- **EVAL::MOVER_TREND_PULLBACK** (total=95799): mover_run_too_small=48349, basic_filters_failed=24613, no_reclaim=20420, no_pullback_tag=2417
- **EVAL::OPENING_RANGE_BREAKOUT** (total=84223): feature_disabled=84223
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=79041): regime_blocked=47134, breakout_not_found=24645, basic_filters_failed=5653, adx_reject=1568, ema_alignment_reject=41
- **EVAL::QUIET_COMPRESSION_BREAK** (total=78532): regime_blocked=34724, compression_not_detected=32730, basic_filters_failed=8609, breakout_not_detected=2281, volume_confirmation_failed=185, rsi_reject=3
- **EVAL::RANGE_FADE** (total=78966): no_range_edge=64860, basic_filters_failed=14106
- **EVAL::SR_FLIP_RETEST** (total=78420): flip_close_not_confirmed=51924, basic_filters_failed=14240, retest_out_of_zone=3423, long_break_volume_thin=3049, regime_blocked=2950, h1_break_not_confirmed=1385, reclaim_hold_failed=896, ema_alignment_reject=245, long_acceptance_not_held=128, wick_quality_failed=94, whipsaw_flip=81, missing_fvg_or_orderblock=5
- **EVAL::STANDARD** (total=63527): momentum_reject=16169, adx_reject=15306, basic_filters_failed=10776, ema_alignment_reject=7997, sweeps_not_detected=6660, macd_reject=5857, htf_poi_unanchored=689, invalid_sl_geometry=38, rsi_reject=35
- **EVAL::TREND_PULLBACK** (total=68470): h1_trend_not_aligned=25438, ema_alignment_reject=14236, basic_filters_failed=8799, h1_pullback_not_confirmed=6073, ema_not_tested_prev=4671, no_ema_reclaim_close=4191, body_conviction_fail=2035, rsi_reject=1689, prev_already_below_emas=404, no_prev_low_break=381, prev_already_above_emas=301, momentum_flat=134, no_prev_high_break=70, ema21_not_tagged=42, missing_fvg_or_orderblock=4, momentum_reject=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=105217): breakout_not_found=59334, basic_filters_failed=24518, move_not_fresh=13708, breakout_stale=5255, retest_proximity_failed=1929, volume_spike_missing=444, move_exhausted=20, missing_fvg_or_orderblock=9
- **EVAL::WHALE_MOMENTUM** (total=74453): momentum_reject=65971, recent_ticks_insufficient=6927, basic_filters_failed=1555

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=359): setup_compat:regime_VOLATILE_UNSUITABLE=311, execution:overextended=28, setup_compat:regime_BREAKOUT_EXPANSION=20
- **FAILED_AUCTION_RECLAIM** (total=1613): execution:overextended=854, setup_compat:regime_STRONG_TREND=581, context_floor=178
- **FUNDING_EXTREME_SIGNAL** (total=627): execution:trigger_not_confirmed=591, context_floor=36
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=7822): setup_compat:regime_STRONG_TREND=3289, execution:trigger_not_confirmed=2540, execution:overextended=1993
- **MA_CROSS_TREND_SHIFT** (total=13): setup_compat:regime_DIRTY_RANGE=5, execution:overextended=3, setup_compat:regime_CLEAN_RANGE=3, execution:trigger_not_confirmed=2
- **MEAN_REVERT** (total=8026): setup_compat:regime_STRONG_TREND=3520, setup_compat:regime_WEAK_TREND=3448, execution:overextended=1035, entry_quality=23
- **MOVER_AVWAP_SCALP** (total=1611): execution:overextended=1123, execution:trigger_not_confirmed=285, entry_quality=203
- **MOVER_TREND_PULLBACK** (total=20026): execution:trigger_not_confirmed=11752, execution:overextended=6350, entry_quality=1924
- **QUIET_COMPRESSION_BREAK** (total=63): execution:trigger_not_confirmed=63
- **RANGE_FADE** (total=6023): setup_compat:regime_STRONG_TREND=3252, setup_compat:regime_WEAK_TREND=2297, setup_compat:regime_VOLATILE_UNSUITABLE=287, execution:overextended=105, context_edge=73, setup_compat:regime_BREAKOUT_EXPANSION=9
- **TREND_PULLBACK_EMA** (total=2399): setup_compat:regime_CLEAN_RANGE=1222, setup_compat:regime_DIRTY_RANGE=867, setup_compat:regime_VOLATILE_UNSUITABLE=194, entry_quality=116
- **VOLUME_SURGE_BREAKOUT** (total=13): execution:overextended=13

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 269671 | 41.0% |
| TRENDING_UP | 148010 | 22.5% |
| TRENDING_DOWN | 115927 | 17.6% |
| QUIET | 99932 | 15.2% |
| VOLATILE | 24383 | 3.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **146**
- Average confidence gap to threshold: **12.69** (samples=146) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=21, XLMUSDT=18, SUIUSDT=18, BNBUSDT=13, ETHUSDT=12, DASHUSDT=12, ADAUSDT=11, AVAXUSDT=8, DOTUSDT=5, INJUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 31 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 129 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 51 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 28 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 84 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 108 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 68 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 156 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 6 |
| MEAN_REVERT | filtered | min_confidence | 87 |
| MEAN_REVERT | kept | min_confidence_pass | 21 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 455 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 469 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3002 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 13 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3939 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 52 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 35 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 41 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 18 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 99 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 92 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 110 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 96 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 31 | 72.49 | 65.00 | -7.49 | 20.21 | 18.33 | 20.00 | 4.48 | 2.90 |
| DIVERGENCE_CONTINUATION | filtered | 131 | 53.48 | 64.40 | 10.92 | 20.65 | 19.74 | 17.87 | 1.50 | 16.69 |
| DIVERGENCE_CONTINUATION | kept | 51 | 75.43 | 65.00 | -10.43 | 20.80 | 19.46 | 19.49 | 1.90 | -1.70 |
| FAILED_AUCTION_RECLAIM | filtered | 28 | 57.40 | 64.71 | 7.31 | 21.04 | 20.00 | 20.00 | 3.23 | 6.96 |
| FAILED_AUCTION_RECLAIM | kept | 84 | 73.17 | 65.00 | -8.17 | 21.14 | 19.55 | 20.00 | 1.82 | 0.21 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 176 | 53.87 | 64.20 | 10.33 | 20.80 | 18.06 | 18.45 | 2.09 | 16.09 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 156 | 69.80 | 65.00 | -4.80 | 22.01 | 19.54 | 18.21 | 2.19 | 0.04 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.80 | 65.00 | 7.20 | 24.00 | 20.00 | 15.80 | 0.00 | 7.50 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.43 | 65.00 | -5.43 | 21.15 | 17.70 | 15.80 | 0.00 | 0.95 |
| MEAN_REVERT | filtered | 87 | 51.57 | 64.26 | 12.69 | 22.37 | 15.98 | 16.11 | 0.00 | 19.42 |
| MEAN_REVERT | kept | 21 | 63.89 | 65.00 | 1.11 | 18.34 | 14.19 | 16.72 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 462 | 56.00 | 63.61 | 7.61 | 19.88 | 15.69 | 15.80 | 3.68 | 15.18 |
| MOVER_AVWAP_SCALP | kept | 469 | 75.49 | 65.00 | -10.49 | 20.68 | 16.39 | 15.80 | 4.29 | 7.45 |
| MOVER_TREND_PULLBACK | filtered | 3015 | 57.18 | 64.17 | 6.99 | 19.94 | 18.62 | 15.80 | 3.92 | 14.22 |
| MOVER_TREND_PULLBACK | kept | 3939 | 75.91 | 65.00 | -10.91 | 20.28 | 18.57 | 15.80 | 4.14 | 1.25 |
| QUIET_COMPRESSION_BREAK | filtered | 87 | 55.89 | 65.00 | 9.11 | 22.81 | 19.38 | 20.00 | 0.00 | 8.01 |
| QUIET_COMPRESSION_BREAK | kept | 41 | 74.85 | 65.00 | -9.85 | 22.20 | 19.64 | 20.00 | 0.00 | -0.62 |
| SR_FLIP_RETEST | filtered | 18 | 42.93 | 65.00 | 22.07 | 21.69 | 20.00 | 15.20 | 2.42 | 25.62 |
| SR_FLIP_RETEST | kept | 99 | 71.30 | 65.00 | -6.30 | 21.35 | 20.00 | 15.29 | 1.86 | -0.89 |
| TREND_PULLBACK_EMA | filtered | 97 | 59.11 | 63.60 | 4.49 | 20.22 | 19.68 | 18.54 | 4.86 | 14.97 |
| TREND_PULLBACK_EMA | kept | 110 | 77.44 | 65.00 | -12.44 | 21.11 | 19.94 | 18.81 | 4.80 | -0.11 |
| VOLUME_SURGE_BREAKOUT | filtered | 96 | 53.31 | 64.67 | 11.36 | 19.63 | 16.96 | 20.00 | 3.80 | 9.01 |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 77.47 | 65.00 | -12.47 | 19.57 | 17.70 | 20.00 | 4.68 | 3.31 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 31 | 72.49 | 17.00 | 17.87 | 12.00 | 11.10 | 4.92 | 8.02 | 4.48 |
| DIVERGENCE_CONTINUATION | filtered | 131 | 53.48 | 22.01 | 13.95 | 6.02 | 13.08 | 6.24 | 8.60 | 1.50 |
| DIVERGENCE_CONTINUATION | kept | 51 | 75.43 | 24.22 | 17.41 | 9.71 | 10.67 | 5.70 | 6.72 | 1.90 |
| FAILED_AUCTION_RECLAIM | filtered | 28 | 57.40 | 22.21 | 14.00 | 6.21 | 14.46 | 8.50 | 3.77 | 3.23 |
| FAILED_AUCTION_RECLAIM | kept | 84 | 73.17 | 21.00 | 17.95 | 5.61 | 14.00 | 6.51 | 6.67 | 1.82 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 176 | 53.87 | 22.64 | 14.00 | 5.62 | 13.30 | 5.68 | 6.62 | 2.09 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 156 | 69.80 | 23.08 | 14.97 | 6.00 | 11.47 | 5.25 | 7.13 | 2.19 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.80 | 17.00 | 14.00 | 9.00 | 14.00 | 5.00 | 6.30 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.43 | 19.67 | 14.00 | 6.50 | 15.00 | 7.50 | 8.72 | 0.00 |
| MEAN_REVERT | filtered | 87 | 51.57 | 24.26 | 17.26 | 7.28 | 13.00 | 5.00 | 7.29 | 0.00 |
| MEAN_REVERT | kept | 21 | 63.89 | 24.24 | 14.00 | 14.71 | 13.00 | 5.00 | 5.80 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 462 | 56.00 | 19.19 | 18.00 | 11.68 | 13.64 | 5.69 | 6.42 | 3.68 |
| MOVER_AVWAP_SCALP | kept | 469 | 75.49 | 19.58 | 18.10 | 12.53 | 13.92 | 5.84 | 8.81 | 4.29 |
| MOVER_TREND_PULLBACK | filtered | 3015 | 57.18 | 18.52 | 18.07 | 7.87 | 12.40 | 5.95 | 8.63 | 3.92 |
| MOVER_TREND_PULLBACK | kept | 3939 | 75.91 | 19.25 | 18.05 | 7.70 | 12.94 | 6.57 | 8.78 | 4.14 |
| QUIET_COMPRESSION_BREAK | filtered | 87 | 55.89 | 19.02 | 15.61 | 11.55 | 14.14 | 6.98 | 4.87 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 41 | 74.85 | 19.73 | 17.71 | 10.10 | 13.95 | 6.01 | 8.71 | 0.00 |
| SR_FLIP_RETEST | filtered | 18 | 42.93 | 23.67 | 8.00 | 5.83 | 15.17 | 5.58 | 7.88 | 2.42 |
| SR_FLIP_RETEST | kept | 99 | 71.30 | 21.12 | 12.34 | 7.55 | 14.12 | 5.39 | 9.33 | 1.86 |
| TREND_PULLBACK_EMA | filtered | 97 | 59.11 | 17.00 | 18.00 | 7.50 | 14.00 | 6.01 | 9.11 | 4.86 |
| TREND_PULLBACK_EMA | kept | 110 | 77.44 | 19.73 | 18.00 | 7.51 | 14.54 | 5.86 | 8.75 | 4.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 96 | 53.31 | 15.84 | 16.33 | 12.19 | 13.41 | 4.90 | 6.17 | 3.80 |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 77.47 | 17.94 | 18.00 | 12.00 | 14.18 | 5.00 | 9.86 | 4.68 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 31 | 72.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 131 | 53.48 | 0.00 | 0.00 | 0.67 | 0.00 | 0.77 | 0.00 | 0.00 | 0.00 | **1.44** |
| DIVERGENCE_CONTINUATION | kept | 51 | 75.43 | 0.00 | 0.00 | 0.25 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **0.53** |
| FAILED_AUCTION_RECLAIM | filtered | 28 | 57.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 84 | 73.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 176 | 53.87 | 0.00 | 0.00 | 0.00 | 0.00 | 1.47 | 0.00 | 0.00 | 0.00 | **1.47** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 156 | 69.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.43 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.80** |
| MEAN_REVERT | filtered | 87 | 51.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 21 | 63.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 462 | 56.00 | 0.00 | 0.00 | 0.37 | 0.00 | 1.70 | 0.00 | 0.00 | 0.28 | **2.35** |
| MOVER_AVWAP_SCALP | kept | 469 | 75.49 | 0.00 | 0.00 | 0.03 | 0.00 | 4.17 | 0.00 | 0.00 | 0.54 | **4.74** |
| MOVER_TREND_PULLBACK | filtered | 3015 | 57.18 | 0.00 | 0.00 | 0.53 | 0.00 | 0.23 | 0.00 | 0.00 | 0.12 | **0.88** |
| MOVER_TREND_PULLBACK | kept | 3939 | 75.91 | 0.00 | 0.00 | 0.62 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.73** |
| QUIET_COMPRESSION_BREAK | filtered | 87 | 55.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 1.97 | **2.19** |
| QUIET_COMPRESSION_BREAK | kept | 41 | 74.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | **0.21** |
| SR_FLIP_RETEST | filtered | 18 | 42.93 | 0.00 | 0.00 | 5.60 | 0.00 | 8.40 | 0.00 | 0.00 | 0.00 | **14.00** |
| SR_FLIP_RETEST | kept | 99 | 71.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 97 | 59.11 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.41** |
| TREND_PULLBACK_EMA | kept | 110 | 77.44 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| VOLUME_SURGE_BREAKOUT | filtered | 96 | 53.31 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.27 | **0.42** |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 77.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **120560 held of 378250 seen** across 21 strategies; 2749 cells past the sample floor; **1309 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 40136 | 568/39568/0 | 44% | -0.17 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.20R) |
| MOVER_AVWAP_SCALP | 15768 | 187/15581/0 | 39% | -0.28 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 9293 | 110/9183/0 | 42% | -0.19 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 7958 | 48/7910/0 | 50% | -0.01 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.65R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 6824 | 26/6798/0 | 44% | -0.14 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6329 | 0/0/6329 | 43% | -0.08 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | LONDON/QUIET/NORMAL/BTC_RISING (-0.83R) |
| SHADOW_RANGE_FADE | 5555 | 0/0/5555 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.70R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| QUIET_COMPRESSION_BREAK | 5140 | 317/4823/0 | 47% | -0.11 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4925 | 0/0/4925 | 35% | -0.39 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 4205 | 66/4139/0 | 39% | -0.44 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.55R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2440 | 31/2409/0 | 49% | -0.11 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 2196 | 0/2196/0 | 41% | -0.04 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2118 | 2/2116/0 | 31% | -0.48 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SR_FLIP_RETEST | 1534 | 12/1522/0 | 52% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| SHADOW_CASCADE_REVERSAL | 972 | 0/0/972 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 861 | 2/859/0 | 34% | -0.49 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 555 | 55/500/0 | 32% | -0.35 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 76 | 10/66/0 | 50% | -0.00 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP` -1.54R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/RANGE/NORMAL/BTC_NEUTRAL` -1.54R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 158 | 27% / -0.58R | 158 | 47% / -0.18R | +0.40 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 540 | 44% / -0.20R | 540 | 56% / -0.02R | +0.18 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 848 | 48% / -0.26R | 848 | 57% / -0.11R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 1266 | 43% / -0.21R | 1266 | 49% / -0.08R | +0.13 | **ATR** |
| BREAKDOWN_SHORT | 47 | 43% / -0.19R | 47 | 47% / -0.08R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 159 | 48% / -0.27R | 159 | 50% / -0.16R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6273 | 49% / -0.11R | 6273 | 54% / -0.01R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 888 | 42% / -0.21R | 888 | 44% / -0.12R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 777 | 49% / -0.10R | 777 | 55% / -0.04R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 117 | 38% / -0.12R | 117 | 47% / -0.06R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 23 | 48% / -0.07R | 23 | 48% / -0.10R | -0.03 | **FIXED** |
| MEAN_REVERT | 192 | 55% / -0.03R | 192 | 53% / -0.02R | +0.01 | **ATR** |
| RANGE_FADE | 43 | 35% / -0.31R | 43 | 37% / -0.32R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 841 | 47% / -0.14R | 841 | 47% / -0.15R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8983 | 29% | -0.25R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1266 | 47% | -0.08R | 201 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 72 | 50% | -0.07R | 49 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 818 | 36% / -0.16R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 8060 | 36% / -0.16R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1649 | 35% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 727 | 35% / -0.14R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 872 | 39% / -0.03R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 726 | 37% / -0.09R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 837 | 42% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 170 | 29% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 209 | 29% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 159 | 57% / +0.13R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 81 | 42% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 33 | 33% / +0.03R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 160 | 33% / -0.45R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 36 | 28% / -0.35R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 11 | 45% / +0.67R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 60 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×57]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 38/6) (sustained 38 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.59R (bound 0.3) (streak 490/6) (sustained 490 cycles)
- **ALERT** `tuned_variants` — 628 non-stamps — atr_arm_uncomputable=628 (seen=12798 stamped=1198 skipped=10972) (streak 470/6) (sustained 470 cycles)
- **ALERT** `auto_dispatch` — 90 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=90) (streak 459/3) (sustained 459 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 143998079 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 31 arms current, none stalled; covering 1053/1053 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 3/6) | 3 |
| atr_trail_live_arms | ok | 61 arms current, none stalled; covering 1122/1122 signals (100%) | 0 |
| auto_dispatch | violating | 90 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=90) (streak 459/3) | 459 |
| binance_ip_weight | ok | peak 312/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83430.90 | 0 |
| candle_coverage | ok | 93/93 symbols with ≥20 15m candles, 93/93 updated within 45m [fresh=93; 75 Tier-1 futures + 18 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1755 dup bars, 0 undedupable; ws 0 out-of-order, 426 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 34 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 34 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +9 / upstream +32 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1721/1739 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | violating | 5 of 167 open dark rows are not being advanced (worst: WUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 24/120) | 24 |
| dark_sar_arms | ok | no open arms; covering 1715/1733 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 41562685 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.59R (bound 0.3) (streak 490/6) | 490 |
| emission_controller | ok | last cycle 1013s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×57]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 38/6) | 38 |
| entry_quality_effective | ok | 17573 evaluated, 5360 suppressed, 5905 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,383 reads/day of 50,000 [engine 1,342, signing 41]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4920 sealed bars over 41 symbols; 1082 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +248 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 197568 frozen value(s) avoided; 1331277 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.12R over n=2409 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +42 / upstream +248 | 0 |
| mover_admission_metadata | ok | 919 symbols known, 213 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 18 held, 18 with scan counts, 18 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2165994 evicted (sampled: execution:trigger_not_confirmed 400/797674, execution:overextended 400/717327, setup_compat:regime_STRONG_TREND 400/323530) | 0 |
| price_action_lane | ok | 1397106 evaluated, 1293 emitted; layer1 1293 stamped / 0 blind; cooldown=189255, delta_opposed=125325, no_footprint=609899, no_opposing_target=1410, no_sweep=353756, rr_below_floor=116168 | 0 |
| promoted_pair_integrity | ok | 18/18 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.49R over n=859 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +3 / upstream +248 | 0 |
| sar_alignment_crosscheck | ok | 949/27527 disagreed (3.4%) | 0 |
| sar_exit_shadow | violating | upstream +248 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1835 held arms settled, 165 unscored, 61 still walking (53 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 64/64 resolvable | 0 |
| sar_live_arms | ok | 61 arms current, none stalled; covering 1120/1120 signals (100%) | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 8 resolved, 56 still mid-window | 0 |
| scan_cycle | ok | last 7.82s, worst 117.68s over 15622 lifetime cycles; lifetime 45 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 6.06s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 660822 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 29s ago (6.18s to run, worst 78.41s), 635 overrun(s) of 10400 cycles, TTL 900s; slowest signals=6.63s, positions_diag=5.03s, tickers=2.51s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +39 / upstream +248 | 0 |
| structural_snap | ok | 5784/5784 measured, 26 blind, 0 levels moved (refusals: redetect_cooldown=1237) | 0 |
| structural_veto_lane | ok | 2260 stamped; 0 with no readable level book, 14 with clear air ahead, 1518 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +248 / upstream +32 | 0 |
| tuned_variants | violating | 628 non-stamps — atr_arm_uncomputable=628 (seen=12798 stamped=1198 skipped=10972) (streak 470/6) | 470 |
| unlock_shorts | ok | 5 open, 45 scheduled, calendar 16.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 3 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2988924`
- `Path funnel` emissions: `74`
- `Regime distribution` emissions: `74`
- `QUIET_SCALP_BLOCK` events: `146`
- `confidence_gate` events: `9222`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **12**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 3820 | 3820 | 4912 | 0 |
| futures_aggtrade | 4 | 3675 | 3886 | 4634 | 0 |
| futures_depth | 5 | 5201 | 5668 | 5690 | 0 |
| futures_mover | 1 | 6281 | 6281 | 6281 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=553593] state[populated=553593] buckets[many=553593] sources[none] quality[none]
- funding_rate: presence[absent=59843, present=493750] state[empty=59843, populated=493750] buckets[few=493750, none=59843] sources[none] quality[none]
- liquidation_clusters: presence[absent=307063, present=246530] state[empty=307063, populated=246530] buckets[few=200269, none=307063, some=46261] sources[none] quality[none]
- oi_snapshot: presence[absent=59843, present=493750] state[empty=59843, populated=493750] buckets[few=103, many=493178, none=59843, some=469] sources[none] quality[none]
- order_book: presence[absent=150910, present=402683] state[populated=402683, unavailable=150910] buckets[few=402683, none=150910] sources[book_ticker=402683, unavailable=150910] quality[none=150910, top_of_book_only=402683]
- orderblocks: presence[absent=553593] state[empty=553593] buckets[none=553593] sources[measured_dark=553593] quality[none]
- recent_ticks: presence[present=553593] state[populated=553593] buckets[many=553593] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.053357005119324` sec
- Median create→first breach: `5525.94880259037` sec
- Median create→terminal: `5526.05112862587` sec
- Median first breach→terminal: `5.745887756347656e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 2.129890910526707 | 2.2269398904165225 | 0.9627283559443173 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 4.871685417114685 | 2.969233463716504 | 1.6407215790357343 | 1 | 0 |
| MOVER_AVWAP_SCALP | 4 | 4 | 1.9429796448957959 | 2.6342289734279545 | 0.9445486991715755 | 2 | 2 |
| MOVER_TREND_PULLBACK | 27 | 27 | 3.382966360016953 | 3.0 | 1.2772559407254462 | 18 | 9 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.0205870069400726 | 1.1331321166219235 | 0.8996106465849483 | 0 | 5 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2049 | 7737.942256569862 | 7737.94227707386 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 6347.385276079178 | 6347.385300159454 |
| MOVER_AVWAP_SCALP | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -1.1567 | 1120.9200484752655 | 1120.9200714826584 |
| MOVER_TREND_PULLBACK | 27 | 27 | 48.1 | 25.9 | 48.1 | 0.0 | 1.0588 | 5099.618986129761 | 5099.619029045105 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 50.0 | 33.3 | 50.0 | 0.0 | 0.8521 | 15490.007770061493 | 15490.007794499397 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1016 | 5 | 650 | 0.0 | 0.0 | None | None | 366 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2589 | 25 | 2059 | 0.0 | 0.0 | None | None | 530 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-168`
- Gating Δ: `-74276`
- No-generation Δ: `-404496`
- Fast failures Δ: `-2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.5186, "current_avg_pnl": -1.2049, "current_win_rate": 0.0, "previous_avg_pnl": 0.3137, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.8245, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.8245, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.3962, "current_avg_pnl": -1.1567, "current_win_rate": 0.0, "previous_avg_pnl": -1.5529, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.1232, "current_avg_pnl": 1.0588, "current_win_rate": 48.1, "previous_avg_pnl": -0.0644, "previous_win_rate": 33.3, "win_rate_delta": 14.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.8415, "current_avg_pnl": 0.8521, "current_win_rate": 50.0, "previous_avg_pnl": -0.9894, "previous_win_rate": 0.0, "win_rate_delta": 50.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 152, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -18, "geometry_changed_delta": 0, "geometry_preserved_delta": -284, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_AVWAP_SCALP**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_AVWAP_SCALP**
