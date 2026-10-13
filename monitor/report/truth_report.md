# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `3718` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 256 | 256 | 256 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11096 | 11096 | 9879 | 8 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 128630 | 128625 | 39 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 102348 | 102349 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 102029 | 98729 | 3605 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 102386 | 101226 | 1230 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 103727 | 103674 | 81 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 88171 | 88182 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 102460 | 102502 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 102517 | 100289 | 3161 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 137463 | 145355 | 820 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 128674 | 111299 | 26105 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 103356 | 103357 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 102350 | 102380 | 5 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 102016 | 101996 | 32 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 103456 | 100552 | 3878 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 101611 | 101879 | 96 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 86206 | 82262 | 4232 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 86503 | 86224 | 328 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 128555 | 128602 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 88190 | 88207 | 2 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4940 | 4940 | 4559 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 385 | 385 | 190 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 10 | 10 | 10 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 25519 | 25519 | 24075 | 20 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 4 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8755 | 8755 | 8304 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2094 | 2094 | 983 | 51 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 75981 | 75981 | 57344 | 429 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 73 | 73 | 73 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 346 | 346 | 332 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 11075 | 11075 | 10611 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 479 | 479 | 346 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1463 | 1463 | 1285 | 10 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 124 | 124 | 34 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 272 | 272 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=128625): breakout_not_found=59354, move_not_fresh=29749, basic_filters_failed=29338, breakout_stale=7296, retest_proximity_failed=2474, volume_spike_missing=384, move_exhausted=18, missing_fvg_or_orderblock=12
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=102349): cls_disabled_merged_into_lsr=102349
- **EVAL::DIVERGENCE_CONTINUATION** (total=98729): cvd_divergence_failed=38063, h1_trend_not_aligned=34974, basic_filters_failed=16938, ema_alignment_reject=7401, retest_proximity_failed=857, missing_fvg_or_orderblock=496
- **EVAL::FAILED_AUCTION_RECLAIM** (total=101226): auction_not_detected=73102, basic_filters_failed=16344, reclaim_hold_failed=5120, tail_too_small=3871, regime_blocked=2782, rsi_reject=7
- **EVAL::FUNDING_EXTREME** (total=103674): funding_not_extreme=78923, basic_filters_failed=16084, missing_funding_rate=7503, ema_alignment_reject=727, rsi_reject=232, momentum_reject=109, cvd_divergence_failed=74, missing_fvg_or_orderblock=22
- **EVAL::LIQUIDATION_REVERSAL** (total=88182): cascade_threshold_not_met=69662, basic_filters_failed=17899, cvd_divergence_failed=314, rsi_reject=289, missing_fvg_or_orderblock=13, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=102502): no_ma_cross=82088, basic_filters_failed=16957, ma_cross_htf_misaligned=2278, ma_cross_cooldown=1179
- **EVAL::MEAN_REVERT** (total=100289): no_extension=86509, basic_filters_failed=13780
- **EVAL::MOVER_AVWAP_SCALP** (total=145356): no_avwap_tag=81737, basic_filters_failed=29550, no_mover_leg=25178, avwap_slope_against=4928, avwap_reclaim_no_volume=2194, no_avwap_reclaim=1699, anchor_too_recent=70
- **EVAL::MOVER_TREND_PULLBACK** (total=111299): mover_run_too_small=41185, no_reclaim=34226, basic_filters_failed=29451, no_pullback_tag=6437
- **EVAL::OPENING_RANGE_BREAKOUT** (total=103357): feature_disabled=103357
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=102380): breakout_not_found=53280, regime_blocked=39727, basic_filters_failed=7442, adx_reject=1855, ema_alignment_reject=76
- **EVAL::QUIET_COMPRESSION_BREAK** (total=101996): regime_blocked=65239, compression_not_detected=26517, basic_filters_failed=8891, breakout_not_detected=1199, volume_confirmation_failed=146, rsi_reject=4
- **EVAL::RANGE_FADE** (total=100552): no_range_edge=86770, basic_filters_failed=13782
- **EVAL::SR_FLIP_RETEST** (total=101879): flip_close_not_confirmed=70893, basic_filters_failed=16321, h1_break_not_confirmed=4985, retest_out_of_zone=3011, regime_blocked=2780, long_break_volume_thin=2699, reclaim_hold_failed=642, long_acceptance_not_held=227, ema_alignment_reject=140, wick_quality_failed=98, whipsaw_flip=70, missing_fvg_or_orderblock=13
- **EVAL::STANDARD** (total=82262): momentum_reject=32321, ema_alignment_reject=14180, basic_filters_failed=11556, sweeps_not_detected=9808, adx_reject=8020, macd_reject=4815, htf_poi_unanchored=1394, rsi_reject=93, invalid_sl_geometry=38, mtf_reject=37
- **EVAL::TREND_PULLBACK** (total=86224): h1_trend_not_aligned=34324, h1_pullback_not_confirmed=16618, ema_alignment_reject=11880, ema_not_tested_prev=8084, basic_filters_failed=6677, no_ema_reclaim_close=3883, rsi_reject=1918, body_conviction_fail=1753, no_prev_low_break=333, prev_already_below_emas=321, prev_already_above_emas=152, no_prev_high_break=105, ema21_not_tagged=79, momentum_flat=66, missing_fvg_or_orderblock=16, momentum_reject=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=128602): breakout_not_found=80264, basic_filters_failed=29334, move_not_fresh=13714, breakout_stale=3218, retest_proximity_failed=1834, volume_spike_missing=203, move_exhausted=22, missing_fvg_or_orderblock=13
- **EVAL::WHALE_MOMENTUM** (total=88207): momentum_reject=63020, recent_ticks_insufficient=19963, basic_filters_failed=5224

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=52): execution:overextended=52
- **DIVERGENCE_CONTINUATION** (total=260): setup_compat:regime_VOLATILE_UNSUITABLE=216, execution:overextended=44
- **FAILED_AUCTION_RECLAIM** (total=2949): setup_compat:regime_STRONG_TREND=2029, execution:overextended=795, context_floor=125
- **FUNDING_EXTREME_SIGNAL** (total=300): execution:trigger_not_confirmed=289, context_floor=11
- **LIQUIDATION_REVERSAL** (total=10): execution:trigger_not_confirmed=10
- **LIQUIDITY_SWEEP_REVERSAL** (total=10422): setup_compat:regime_STRONG_TREND=5092, execution:trigger_not_confirmed=3751, execution:overextended=1579
- **MA_CROSS_TREND_SHIFT** (total=3): setup_compat:regime_CLEAN_RANGE=1, setup_compat:regime_DIRTY_RANGE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=7375): setup_compat:regime_STRONG_TREND=4548, setup_compat:regime_WEAK_TREND=1806, execution:overextended=1015, entry_quality=6
- **MOVER_AVWAP_SCALP** (total=1438): execution:overextended=885, execution:trigger_not_confirmed=320, entry_quality=233
- **MOVER_TREND_PULLBACK** (total=31560): execution:overextended=14941, execution:trigger_not_confirmed=12416, entry_quality=4203
- **RANGE_FADE** (total=9148): setup_compat:regime_STRONG_TREND=6177, setup_compat:regime_WEAK_TREND=1921, execution:overextended=787, setup_compat:regime_VOLATILE_UNSUITABLE=162, setup_compat:regime_BREAKOUT_EXPANSION=101
- **TREND_PULLBACK_EMA** (total=1047): setup_compat:regime_CLEAN_RANGE=714, setup_compat:regime_DIRTY_RANGE=314, entry_quality=17, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **WHALE_MOMENTUM** (total=252): execution:trigger_not_confirmed=252

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 234090 | 34.8% |
| RANGING | 189816 | 28.2% |
| TRENDING_UP | 136139 | 20.3% |
| QUIET | 88273 | 13.1% |
| VOLATILE | 23744 | 3.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **97**
- Average confidence gap to threshold: **11.88** (samples=97) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HYPEUSDT=28, BNBUSDT=13, SUIUSDT=11, BATUSDT=11, XLMUSDT=10, WLDUSDT=5, LTCUSDT=5, ETHUSDT=3, KAIAUSDT=3, ENAUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 310 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 107 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 60 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 6 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 420 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 109 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 5 |
| MEAN_REVERT | filtered | min_confidence | 35 |
| MEAN_REVERT | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 127 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 7 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 475 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1777 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 40 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 8239 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 2 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 12 |
| SR_FLIP_RETEST | filtered | min_confidence | 48 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 4 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 52 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 74 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 310 | 51.25 | 64.56 | 13.31 | 20.71 | 19.70 | 18.38 | 1.65 | 17.30 |
| DIVERGENCE_CONTINUATION | kept | 107 | 70.11 | 65.00 | -5.11 | 21.24 | 19.73 | 17.34 | 3.17 | 4.44 |
| FAILED_AUCTION_RECLAIM | filtered | 66 | 46.99 | 60.86 | 13.87 | 20.45 | 18.01 | 20.00 | 3.42 | 8.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 52.67 | 61.00 | 8.33 | 21.20 | 14.00 | 17.60 | 3.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 461 | 51.34 | 64.43 | 13.09 | 19.92 | 18.74 | 17.92 | 1.87 | 7.98 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 109 | 72.54 | 65.00 | -7.54 | 20.19 | 16.02 | 17.10 | 1.15 | 0.94 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 54.65 | 61.00 | 6.35 | 21.20 | 17.80 | 15.80 | 0.00 | 6.20 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.30 | 65.00 | -5.30 | 20.50 | 18.50 | 15.80 | 0.00 | 2.26 |
| MEAN_REVERT | filtered | 35 | 51.24 | 65.00 | 13.76 | 19.93 | 14.00 | 15.55 | 0.00 | 12.57 |
| MEAN_REVERT | kept | 2 | 69.50 | 65.00 | -4.50 | 18.60 | 14.00 | 16.65 | 0.00 | 6.00 |
| MOVER_AVWAP_SCALP | filtered | 138 | 56.49 | 60.96 | 4.47 | 20.79 | 14.56 | 15.80 | 3.55 | 22.34 |
| MOVER_AVWAP_SCALP | kept | 475 | 77.96 | 65.00 | -12.96 | 20.23 | 16.61 | 15.80 | 4.49 | 4.52 |
| MOVER_TREND_PULLBACK | filtered | 1817 | 57.95 | 64.31 | 6.36 | 20.06 | 18.34 | 15.80 | 4.38 | 18.04 |
| MOVER_TREND_PULLBACK | kept | 8239 | 77.83 | 65.00 | -12.83 | 20.25 | 17.89 | 15.80 | 4.79 | 1.98 |
| QUIET_COMPRESSION_BREAK | filtered | 2 | 61.30 | 65.00 | 3.70 | 22.80 | 19.70 | 20.00 | 0.00 | 11.05 |
| QUIET_COMPRESSION_BREAK | kept | 12 | 72.52 | 65.00 | -7.52 | 22.69 | 19.74 | 20.00 | 0.00 | 1.21 |
| SR_FLIP_RETEST | filtered | 48 | 46.39 | 63.90 | 17.51 | 21.43 | 20.00 | 15.33 | 1.91 | 10.30 |
| SR_FLIP_RETEST | kept | 4 | 63.38 | 65.00 | 1.62 | 19.95 | 20.00 | 15.20 | 2.38 | 6.58 |
| TREND_PULLBACK_EMA | filtered | 8 | 59.59 | 65.00 | 5.41 | 20.79 | 20.00 | 18.14 | 4.19 | 16.06 |
| TREND_PULLBACK_EMA | kept | 52 | 76.87 | 65.00 | -11.87 | 20.64 | 19.74 | 17.87 | 4.76 | -0.35 |
| VOLUME_SURGE_BREAKOUT | filtered | 74 | 48.82 | 63.81 | 14.99 | 21.61 | 16.55 | 20.00 | 4.01 | 11.01 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 70.40 | 65.00 | -5.40 | 20.47 | 17.38 | 20.00 | 4.50 | 5.92 |
| WHALE_MOMENTUM | filtered | 1 | 55.30 | 65.00 | 9.70 | 23.60 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 310 | 51.25 | 22.34 | 17.32 | 3.62 | 11.61 | 4.68 | 8.54 | 1.65 |
| DIVERGENCE_CONTINUATION | kept | 107 | 70.11 | 20.59 | 17.72 | 4.23 | 13.50 | 6.22 | 9.23 | 3.17 |
| FAILED_AUCTION_RECLAIM | filtered | 66 | 46.99 | 24.27 | 15.21 | 4.36 | 10.97 | 7.37 | 4.73 | 3.42 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 52.67 | 25.00 | 8.00 | 4.00 | 12.00 | 9.67 | 6.00 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 461 | 51.34 | 23.49 | 15.54 | 5.68 | 12.02 | 5.39 | 5.75 | 1.87 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 109 | 72.54 | 23.26 | 15.25 | 5.26 | 13.99 | 5.31 | 9.33 | 1.15 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 54.65 | 21.00 | 14.00 | 4.50 | 13.00 | 8.50 | 7.35 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.30 | 18.60 | 14.00 | 9.00 | 14.00 | 7.90 | 9.06 | 0.00 |
| MEAN_REVERT | filtered | 35 | 51.24 | 20.89 | 16.06 | 13.46 | 12.00 | 5.00 | 3.70 | 0.00 |
| MEAN_REVERT | kept | 2 | 69.50 | 21.00 | 18.00 | 13.50 | 12.50 | 5.00 | 5.50 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 138 | 56.49 | 17.90 | 18.19 | 14.07 | 13.43 | 7.00 | 7.74 | 3.55 |
| MOVER_AVWAP_SCALP | kept | 475 | 77.96 | 19.14 | 18.00 | 12.29 | 13.56 | 6.08 | 8.91 | 4.49 |
| MOVER_TREND_PULLBACK | filtered | 1817 | 57.95 | 18.04 | 18.00 | 8.30 | 12.53 | 5.96 | 9.30 | 4.38 |
| MOVER_TREND_PULLBACK | kept | 8239 | 77.83 | 18.67 | 18.01 | 9.20 | 13.25 | 6.87 | 9.11 | 4.79 |
| QUIET_COMPRESSION_BREAK | filtered | 2 | 61.30 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 6.35 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 12 | 72.52 | 20.33 | 18.00 | 9.50 | 14.00 | 7.62 | 5.02 | 0.00 |
| SR_FLIP_RETEST | filtered | 48 | 46.39 | 20.50 | 18.00 | 3.06 | 13.56 | 7.67 | 4.50 | 1.91 |
| SR_FLIP_RETEST | kept | 4 | 63.38 | 23.00 | 18.00 | 4.50 | 11.75 | 5.00 | 5.33 | 2.38 |
| TREND_PULLBACK_EMA | filtered | 8 | 59.59 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 4.19 |
| TREND_PULLBACK_EMA | kept | 52 | 76.87 | 18.56 | 18.00 | 7.50 | 14.06 | 5.36 | 8.92 | 4.76 |
| VOLUME_SURGE_BREAKOUT | filtered | 74 | 48.82 | 20.68 | 16.59 | 12.00 | 13.43 | 5.00 | 3.14 | 4.01 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 70.40 | 19.00 | 17.00 | 12.00 | 14.00 | 5.00 | 8.57 | 4.50 |
| WHALE_MOMENTUM | filtered | 1 | 55.30 | 25.00 | 8.00 | 15.00 | 10.00 | 5.00 | 2.30 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 310 | 51.25 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | **0.50** |
| DIVERGENCE_CONTINUATION | kept | 107 | 70.11 | 0.00 | 0.00 | 0.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.99** |
| FAILED_AUCTION_RECLAIM | filtered | 66 | 46.99 | 0.00 | 0.00 | 2.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.42** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 52.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 461 | 51.34 | 0.00 | 0.00 | 3.06 | 0.00 | 0.61 | 0.07 | 0.00 | 0.00 | **3.74** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 109 | 72.54 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.00** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 54.65 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 35 | 51.24 | 0.00 | 0.00 | 2.33 | 0.00 | 9.67 | 0.57 | 0.00 | 0.00 | **12.57** |
| MEAN_REVERT | kept | 2 | 69.50 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | 0.00 | **6.00** |
| MOVER_AVWAP_SCALP | filtered | 138 | 56.49 | 2.52 | 0.00 | 0.09 | 0.00 | 3.90 | 1.49 | 0.00 | 0.98 | **8.98** |
| MOVER_AVWAP_SCALP | kept | 475 | 77.96 | 0.92 | 0.00 | 0.00 | 0.00 | 1.82 | 0.13 | 0.00 | 0.16 | **3.03** |
| MOVER_TREND_PULLBACK | filtered | 1817 | 57.95 | 0.11 | 0.00 | 0.62 | 0.00 | 0.82 | 0.90 | 0.00 | 0.00 | **2.45** |
| MOVER_TREND_PULLBACK | kept | 8239 | 77.83 | 0.02 | 0.00 | 0.25 | 0.00 | 0.29 | 0.21 | 0.00 | 0.01 | **0.78** |
| QUIET_COMPRESSION_BREAK | filtered | 2 | 61.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 12 | 72.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 48 | 46.39 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 2.52 | **3.32** |
| SR_FLIP_RETEST | kept | 4 | 63.38 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | 0.00 | 1.50 | **2.70** |
| TREND_PULLBACK_EMA | filtered | 8 | 59.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | 0.00 | 0.00 | **9.00** |
| TREND_PULLBACK_EMA | kept | 52 | 76.87 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | **0.58** |
| VOLUME_SURGE_BREAKOUT | filtered | 74 | 48.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.05 | **4.05** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 70.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 1 | 55.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **141331 held of 480725 seen** across 21 strategies; 3214 cells past the sample floor; **1602 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 43658 | 643/43015/0 | 43% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.22R) |
| MOVER_AVWAP_SCALP | 18232 | 187/18045/0 | 40% | -0.25 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10962 | 120/10842/0 | 36% | -0.31 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 9733 | 71/9662/0 | 50% | -0.02 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.39R) | ASIA/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (-1.22R) |
| TREND_PULLBACK_EMA | 8000 | 40/7960/0 | 44% | -0.15 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| LIQUIDITY_SWEEP_REVERSAL | 7088 | 85/7003/0 | 34% | -0.51 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 6949 | 0/0/6949 | 43% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.45R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.95R) |
| SHADOW_RANGE_FADE | 6313 | 0/0/6313 | 37% | -0.10 | NY/MARKDOWN/EXPANDED/BTC_FALLING (+0.55R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 5855 | 356/5499/0 | 52% | -0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5497 | 0/0/5497 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3503 | 45/3458/0 | 43% | -0.21 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| SR_FLIP_RETEST | 2843 | 15/2828/0 | 50% | -0.19 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+0.87R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| FUNDING_EXTREME_SIGNAL | 2733 | 2/2731/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2720 | 0/2720/0 | 37% | -0.23 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| RANGE_FADE | 1251 | 4/1247/0 | 43% | -0.27 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1206 | 0/0/1206 | 53% | -0.04 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.08R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 316 | 0/316/0 | 36% | -0.47 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 100 | 16/84/0 | 46% | -0.12 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.56R (n=45, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL` -1.56R (n=45, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 196 | 27% / -0.59R | 196 | 52% / -0.15R | +0.44 | **ATR** |
| LIQUIDATION_REVERSAL | 17 | 35% / -0.40R | 17 | 59% / -0.18R | +0.22 | **ATR** |
| TREND_PULLBACK_EMA | 664 | 43% / -0.24R | 664 | 55% / -0.04R | +0.19 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1162 | 44% / -0.33R | 1162 | 54% / -0.15R | +0.18 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 133 | 35% / -0.21R | 133 | 45% / -0.09R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 1571 | 43% / -0.19R | 1571 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1065 | 40% / -0.25R | 1065 | 42% / -0.14R | +0.11 | **ATR** |
| RANGE_FADE | 59 | 34% / -0.36R | 59 | 41% / -0.26R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| MA_CROSS_TREND_SHIFT | 31 | 42% / -0.19R | 31 | 45% / -0.10R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 248 | 47% / -0.24R | 248 | 50% / -0.16R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 7130 | 50% / -0.09R | 7130 | 55% / -0.01R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 983 | 49% / -0.10R | 983 | 54% / -0.04R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 967 | 46% / -0.15R | 967 | 46% / -0.16R | -0.00 | **FIXED** |
| MEAN_REVERT | 246 | 52% / -0.07R | 246 | 50% / -0.07R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9971 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1571 | 47% | -0.07R | 214 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 83 | 47% | -0.10R | 52 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 889 | 37% / -0.17R | +0.90 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1205 | 40% / -0.17R | +0.84 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2040 | 34% / -0.13R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9012 | 37% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1114 | 38% / -0.06R | +0.22 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 934 | 34% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 866 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 202 | 30% / -0.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 259 | 32% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 207 | 53% / +0.05R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 45 | 36% / -0.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 249 | 34% / -0.35R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 46 | 26% / -0.43R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 23 | 48% / +0.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×305]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 85/6) (sustained 85 cycles)
- **ALERT** `edge_reconciliation` — TREND_PULLBACK_EMA realized−counterfactual=+0.57R (bound 0.3) (streak 206/6) (sustained 206 cycles)
- **ALERT** `tuned_variants` — 255 non-stamps — atr_arm_uncomputable=255 (seen=7396 stamped=808 skipped=6333) (streak 206/6) (sustained 206 cycles)
- **ALERT** `auto_dispatch` — 39 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=40) (streak 196/3) (sustained 196 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 17877385 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 12 arms current, none stalled; covering 1480/1480 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 22 arms current, none stalled; covering 1057/1057 signals (100%) | 0 |
| auto_dispatch | violating | 39 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=40) (streak 196/3) | 196 |
| binance_ip_weight | ok | peak 320/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83738.70 | 0 |
| candle_coverage | ok | 85/85 symbols with ≥20 15m candles, 85/85 updated within 45m [fresh=85; 72 Tier-1 futures + 13 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 747 dup bars, 0 undedupable; ws 0 out-of-order, 275 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 55 cohorts, 18 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +22 / upstream +35 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1549/1567 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | violating | 6 of 130 open dark rows are not being advanced (worst: DOSUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 92/120) | 92 |
| dark_sar_arms | ok | no open arms; covering 1546/1564 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 5736066 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | TREND_PULLBACK_EMA realized−counterfactual=+0.57R (bound 0.3) (streak 206/6) | 206 |
| emission_controller | ok | last cycle 1442s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×305]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 85/6) | 85 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=59, profile_reject=11. Held back in this window: session_quality=100, profile_reject=30. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 2/6) | 2 |
| firestore_read_budget | ok | 1,380 reads/day of 50,000 [engine 1,341, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +228 | 0 |
| indicator_cache_key | ok | 67983 frozen value(s) avoided; 212576 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.22R over n=3458 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +228 but output +0 (streak 1/72) | 1 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 11 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 2 locked / 2 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2669024 evicted (sampled: execution:trigger_not_confirmed 400/964076, execution:overextended 400/852642, setup_compat:regime_STRONG_TREND 400/434334) | 0 |
| price_action_lane | ok | 646869 evaluated, 568 emitted; layer1 568 stamped / 0 blind; cooldown=84070, delta_opposed=57503, no_footprint=294922, no_opposing_target=271, no_sweep=149109, rr_below_floor=60426 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.27R over n=1247 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +9 / upstream +228 | 0 |
| sar_alignment_crosscheck | ok | 190/12145 disagreed (1.6%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +228 | 0 |
| sar_hold_arm | ok | 1846 held arms settled, 154 unscored, 22 still walking (19 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/24 unfetchable (17%); top cause: located bar does not contain the stamp; symbols: BATUSDT, ENAUSDT, LUMIAUSDT | 0 |
| sar_live_arms | ok | 22 arms current, none stalled; covering 1057/1057 signals (100%) | 0 |
| sar_refresh_budget | ok | 22 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 424 records await one (20 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 55.57s, worst 99.48s over 6973 lifetime cycles; lifetime 34 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.86s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 255166 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 6s ago (48.38s to run, worst 56.64s), 275 overrun(s) of 4612 cycles, TTL 900s; slowest user_positions=1.56s, signals=1.34s, engine_state=1.01s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=779, gate reads=0, withheld=779) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +29 / upstream +228 | 0 |
| structural_snap | ok | 5999/5999 measured, 19 blind, 0 levels moved (refusals: redetect_cooldown=671) | 0 |
| structural_veto_lane | ok | 1213 stamped; 0 with no readable level book, 12 with clear air ahead, 1013 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +228 / upstream +35 | 0 |
| tuned_variants | violating | 255 non-stamps — atr_arm_uncomputable=255 (seen=7396 stamped=808 skipped=6333) (streak 206/6) | 206 |
| unlock_shorts | ok | 14 open, 42 scheduled, calendar 11.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 19 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3186946`
- `Path funnel` emissions: `73`
- `Regime distribution` emissions: `73`
- `QUIET_SCALP_BLOCK` events: `97`
- `confidence_gate` events: `11974`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 7424 | 7424 | 7424 | 0 |
| futures_liq | 3 | 3871 | 3871 | 7953 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=553084] state[populated=553084] buckets[many=553084] sources[none] quality[none]
- funding_rate: presence[absent=112496, present=440588] state[empty=112496, populated=440588] buckets[few=440588, none=112496] sources[none] quality[none]
- liquidation_clusters: presence[absent=300297, present=252787] state[empty=300297, populated=252787] buckets[few=196486, none=300297, some=56301] sources[none] quality[none]
- oi_snapshot: presence[absent=111659, present=441425] state[empty=111659, populated=441425] buckets[few=53, many=441372, none=111659] sources[none] quality[none]
- order_book: presence[absent=159133, present=393951] state[populated=393951, unavailable=159133] buckets[few=393951, none=159133] sources[book_ticker=393951, unavailable=159133] quality[none=159133, top_of_book_only=393951]
- orderblocks: presence[absent=553084] state[empty=553084] buckets[none=553084] sources[measured_dark=553084] quality[none]
- recent_ticks: presence[present=553084] state[populated=553084] buckets[many=553084] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.657827615737915` sec
- Median create→first breach: `4642.402600646019` sec
- Median create→terminal: `4642.5548775196075` sec
- Median first breach→terminal: `9.131431579589844e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 3, "pct": 7.1}, "under_180s": {"count": 3, "pct": 7.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.4}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.4}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.7999999999999985 | 1.870211807120326 | 0.6242999999999969 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.677069946759692 | 0.7579974460561227 | 0.8932351293299229 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 4.809677639415267 | 1.5546549592002603 | 3.0614552308662395 | 2 | 0 |
| MEAN_REVERT | 2 | 2 | 2.473527905126219 | 3.0 | 0.8245093017087397 | 0 | 2 |
| MOVER_TREND_PULLBACK | 24 | 24 | 3.6727404372298764 | 3.0 | 1.2242468124099588 | 18 | 6 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 1.321407592139396 | 1.4326730085876271 | 0.8892282226426174 | 0 | 5 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.1814481072270935 | 1.9538991014755576 | 0.6934269324506513 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.8143 | 4842.06348490715 | 4842.063569068909 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.6771 | 900.945573091507 | 900.9456000328064 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 2.0574 | 13691.044392466545 | 13691.598445057869 |
| MEAN_REVERT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.5587 | 2821.4359641075134 | 2821.436045050621 |
| MOVER_TREND_PULLBACK | 24 | 24 | 16.7 | 54.2 | 16.7 | 0.0 | -0.5961 | 3327.1351615190506 | 3327.135246038437 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 37.5 | 50.0 | 37.5 | 0.0 | 0.3159 | 20219.47814142704 | 20220.094450473785 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.7429 | 1709.6543245315552 | 1713.4069879055023 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 479 | 3 | 346 | 0.0 | 0.0 | None | None | 133 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1463 | 10 | 1285 | 0.0 | 0.0 | 1709.6543245315552 | 1713.4069879055023 | 178 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `296`
- Gating Δ: `50511`
- No-generation Δ: `935795`
- Fast failures Δ: `3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.1243, "current_avg_pnl": -1.8143, "current_win_rate": 0.0, "previous_avg_pnl": -1.69, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.8593, "current_avg_pnl": -0.5961, "current_win_rate": 16.7, "previous_avg_pnl": 0.2632, "previous_win_rate": 34.8, "win_rate_delta": -18.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.0202, "current_avg_pnl": 0.3159, "current_win_rate": 37.5, "previous_avg_pnl": -0.7043, "previous_win_rate": 18.2, "win_rate_delta": 19.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": 49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -27973.52, "median_terminal_delta_sec": -27973.52, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -13, "geometry_changed_delta": 0, "geometry_preserved_delta": 49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 296.61, "median_terminal_delta_sec": 299.81, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
