# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `34002` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 44 | 44 | 44 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4426 | 4426 | 4104 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 39530 | 39536 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 35848 | 35857 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 35666 | 34793 | 1049 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 35878 | 35250 | 693 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 35630 | 35506 | 134 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 30515 | 30523 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 35948 | 35970 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 35975 | 34616 | 1944 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 41160 | 44289 | 775 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 39558 | 37543 | 3584 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 35314 | 35323 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 35858 | 35873 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 35646 | 35495 | 172 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 36563 | 35747 | 1065 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 35326 | 35309 | 320 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 30278 | 28843 | 1611 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 30461 | 30347 | 168 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 39500 | 39528 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 30523 | 30507 | 38 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3027 | 3027 | 2641 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 479 | 479 | 60 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 9 | 9 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 9299 | 9299 | 9225 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 1 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5245 | 5245 | 4135 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1820 | 1820 | 647 | 44 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 10263 | 10263 | 6489 | 123 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 738 | 738 | 470 | 24 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 2486 | 2486 | 2028 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 922 | 922 | 810 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1125 | 1125 | 971 | 20 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 5 | 5 | 0 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2395 | 2395 | 19 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=39536): breakout_not_found=18904, basic_filters_failed=12939, move_not_fresh=4562, breakout_stale=2236, retest_proximity_failed=808, volume_spike_missing=87
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=35857): cls_disabled_merged_into_lsr=35857
- **EVAL::DIVERGENCE_CONTINUATION** (total=34793): cvd_divergence_failed=12720, basic_filters_failed=10439, h1_trend_not_aligned=8959, ema_alignment_reject=2309, retest_proximity_failed=230, missing_fvg_or_orderblock=136
- **EVAL::FAILED_AUCTION_RECLAIM** (total=35250): auction_not_detected=19525, basic_filters_failed=10012, reclaim_hold_failed=2542, tail_too_small=1937, regime_blocked=1221, rsi_reject=13
- **EVAL::FUNDING_EXTREME** (total=35506): funding_not_extreme=23166, basic_filters_failed=10017, ema_alignment_reject=909, missing_funding_rate=885, rsi_reject=283, cvd_divergence_failed=119, momentum_reject=118, missing_fvg_or_orderblock=9
- **EVAL::LIQUIDATION_REVERSAL** (total=30523): cascade_threshold_not_met=19988, basic_filters_failed=10248, rsi_reject=143, cvd_divergence_failed=130, volume_spike_missing=9, missing_fvg_or_orderblock=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=35970): no_ma_cross=24983, basic_filters_failed=10452, ma_cross_htf_misaligned=406, ma_cross_cooldown=115, ma_cross_htf_unconfirmed=14
- **EVAL::MEAN_REVERT** (total=34616): no_extension=26179, basic_filters_failed=8437
- **EVAL::MOVER_AVWAP_SCALP** (total=44289): no_avwap_tag=17132, basic_filters_failed=13118, no_mover_leg=9101, avwap_slope_against=2257, avwap_reclaim_no_volume=1594, no_avwap_reclaim=950, anchor_too_recent=137
- **EVAL::MOVER_TREND_PULLBACK** (total=37543): mover_run_too_small=18140, basic_filters_failed=13027, no_reclaim=5268, no_pullback_tag=1108
- **EVAL::OPENING_RANGE_BREAKOUT** (total=35323): feature_disabled=35323
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=35873): regime_blocked=24046, breakout_not_found=8385, basic_filters_failed=2423, adx_reject=986, ema_alignment_reject=33
- **EVAL::QUIET_COMPRESSION_BREAK** (total=35495): regime_blocked=12978, compression_not_detected=11735, basic_filters_failed=7580, breakout_not_detected=2856, volume_confirmation_failed=318, missing_fvg_or_orderblock=22, rsi_reject=6
- **EVAL::RANGE_FADE** (total=35747): no_range_edge=27309, basic_filters_failed=8438
- **EVAL::SR_FLIP_RETEST** (total=35309): flip_close_not_confirmed=19711, basic_filters_failed=9995, long_break_volume_thin=1534, regime_blocked=1216, h1_break_not_confirmed=1206, retest_out_of_zone=1108, reclaim_hold_failed=381, wick_quality_failed=55, ema_alignment_reject=42, long_acceptance_not_held=32, missing_fvg_or_orderblock=19, whipsaw_flip=10
- **EVAL::STANDARD** (total=28843): momentum_reject=8012, basic_filters_failed=6476, adx_reject=6100, macd_reject=3088, sweeps_not_detected=2898, ema_alignment_reject=1698, htf_poi_unanchored=476, rsi_reject=55, invalid_sl_geometry=40
- **EVAL::TREND_PULLBACK** (total=30347): h1_trend_not_aligned=10412, basic_filters_failed=5902, ema_alignment_reject=4954, ema_not_tested_prev=2840, h1_pullback_not_confirmed=2039, no_ema_reclaim_close=1728, rsi_reject=1016, body_conviction_fail=868, prev_already_above_emas=231, prev_already_below_emas=155, no_prev_low_break=78, no_prev_high_break=67, momentum_flat=47, ema21_not_tagged=4, momentum_reject=4, missing_fvg_or_orderblock=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=39528): breakout_not_found=19999, basic_filters_failed=12936, move_not_fresh=3891, breakout_stale=1839, retest_proximity_failed=719, volume_spike_missing=111, missing_fvg_or_orderblock=33
- **EVAL::WHALE_MOMENTUM** (total=30507): momentum_reject=23097, recent_ticks_insufficient=4654, basic_filters_failed=2756

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=197): setup_compat:regime_VOLATILE_UNSUITABLE=181, setup_compat:regime_BREAKOUT_EXPANSION=16
- **FAILED_AUCTION_RECLAIM** (total=1098): setup_compat:regime_STRONG_TREND=725, execution:overextended=369, context_floor=4
- **FUNDING_EXTREME_SIGNAL** (total=414): execution:trigger_not_confirmed=414
- **LIQUIDATION_REVERSAL** (total=9): execution:trigger_not_confirmed=9
- **LIQUIDITY_SWEEP_REVERSAL** (total=2375): execution:trigger_not_confirmed=1011, execution:overextended=906, setup_compat:regime_STRONG_TREND=458
- **MA_CROSS_TREND_SHIFT** (total=3): setup_compat:regime_DIRTY_RANGE=3
- **MEAN_REVERT** (total=2112): setup_compat:regime_WEAK_TREND=914, setup_compat:regime_STRONG_TREND=873, execution:overextended=319, entry_quality=6
- **MOVER_AVWAP_SCALP** (total=986): execution:overextended=629, execution:trigger_not_confirmed=187, entry_quality=170
- **MOVER_TREND_PULLBACK** (total=5216): execution:overextended=2379, execution:trigger_not_confirmed=2246, entry_quality=591
- **QUIET_COMPRESSION_BREAK** (total=20): execution:trigger_not_confirmed=20
- **RANGE_FADE** (total=1641): setup_compat:regime_STRONG_TREND=812, setup_compat:regime_WEAK_TREND=636, execution:overextended=132, setup_compat:regime_VOLATILE_UNSUITABLE=47, setup_compat:regime_BREAKOUT_EXPANSION=14
- **TREND_PULLBACK_EMA** (total=897): setup_compat:regime_CLEAN_RANGE=494, setup_compat:regime_DIRTY_RANGE=286, setup_compat:regime_VOLATILE_UNSUITABLE=93, entry_quality=24
- **WHALE_MOMENTUM** (total=2082): execution:trigger_not_confirmed=2051, context_floor=31

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 94384 | 45.0% |
| TRENDING_DOWN | 41582 | 19.8% |
| QUIET | 40531 | 19.3% |
| TRENDING_UP | 24351 | 11.6% |
| VOLATILE | 8985 | 4.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **65**
- Average confidence gap to threshold: **12.67** (samples=65) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=21, DOTUSDT=13, AAVEUSDT=9, SOLUSDT=6, APTUSDT=5, XRPUSDT=3, POLUSDT=2, VIRTUALUSDT=2, 1000PEPEUSDT=2, ZECUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 66 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 31 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 156 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 7 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 9 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 35 |
| MEAN_REVERT | filtered | min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 18 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 206 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 17 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 473 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 230 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1316 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 43 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 32 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 164 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 5 |
| SR_FLIP_RETEST | filtered | min_confidence | 2 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 36 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 91 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 5 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 21 |
| WHALE_MOMENTUM | filtered | min_confidence | 16 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 66 | 59.79 | 65.00 | 5.21 | 21.58 | 19.72 | 18.30 | 2.24 | 8.73 |
| DIVERGENCE_CONTINUATION | kept | 31 | 70.81 | 65.00 | -5.81 | 20.83 | 19.82 | 18.37 | 2.35 | 1.45 |
| FAILED_AUCTION_RECLAIM | filtered | 156 | 55.49 | 64.08 | 8.59 | 20.78 | 19.11 | 20.00 | 3.79 | 0.42 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.80 | 65.00 | -1.80 | 20.60 | 19.68 | 20.00 | 4.40 | 2.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 49.96 | 61.00 | 11.04 | 21.07 | 15.41 | 17.00 | 2.14 | 3.69 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 69.00 | 65.00 | -4.00 | 20.70 | 14.62 | 16.56 | 3.20 | 1.00 |
| LIQUIDATION_REVERSAL | filtered | 9 | 82.20 | 10.00 | -72.20 | 18.68 | 8.00 | 20.00 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 43.97 | 65.00 | 21.03 | 21.79 | 19.34 | 17.00 | 0.00 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 35 | 70.58 | 65.00 | -5.58 | 21.54 | 19.83 | 17.58 | 1.26 | 0.00 |
| MEAN_REVERT | filtered | 1 | 60.70 | 61.00 | 0.30 | 21.20 | 14.00 | 14.10 | 0.00 | 12.00 |
| MEAN_REVERT | kept | 18 | 67.14 | 65.00 | -2.14 | 17.44 | 14.70 | 14.50 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 223 | 54.78 | 60.81 | 6.03 | 21.04 | 15.92 | 15.80 | 3.36 | 11.37 |
| MOVER_AVWAP_SCALP | kept | 473 | 79.51 | 65.00 | -14.51 | 20.36 | 16.91 | 15.80 | 4.25 | 2.24 |
| MOVER_TREND_PULLBACK | filtered | 230 | 57.61 | 64.33 | 6.72 | 20.40 | 17.89 | 15.80 | 3.87 | 13.28 |
| MOVER_TREND_PULLBACK | kept | 1316 | 77.81 | 65.00 | -12.81 | 19.73 | 18.31 | 15.80 | 4.30 | 0.94 |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 58.49 | 64.20 | 5.71 | 21.51 | 19.40 | 20.00 | 0.00 | 2.78 |
| QUIET_COMPRESSION_BREAK | kept | 164 | 73.84 | 65.00 | -8.84 | 21.46 | 19.14 | 20.00 | 0.00 | -0.15 |
| SR_FLIP_RETEST | filtered | 7 | 60.57 | 65.00 | 4.43 | 19.89 | 20.00 | 16.26 | 2.21 | 8.57 |
| SR_FLIP_RETEST | kept | 36 | 70.93 | 65.00 | -5.93 | 21.13 | 20.00 | 15.62 | 2.04 | 0.08 |
| TREND_PULLBACK_EMA | filtered | 9 | 58.67 | 62.78 | 4.11 | 20.57 | 18.67 | 18.00 | 4.00 | 0.11 |
| TREND_PULLBACK_EMA | kept | 91 | 79.92 | 65.00 | -14.92 | 21.15 | 19.93 | 17.98 | 4.49 | -0.18 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 81.10 | 65.00 | -16.10 | 20.50 | 16.82 | 20.00 | 4.50 | 0.60 |
| WHALE_MOMENTUM | filtered | 37 | 49.61 | 63.81 | 14.20 | 23.08 | 14.16 | 17.00 | 0.00 | 18.26 |
| WHALE_MOMENTUM | kept | 1 | 63.70 | 65.00 | 1.30 | 24.30 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 66 | 59.79 | 22.70 | 9.52 | 7.05 | 14.45 | 5.00 | 8.74 | 2.24 |
| DIVERGENCE_CONTINUATION | kept | 31 | 70.81 | 23.97 | 13.48 | 6.68 | 12.26 | 5.26 | 8.84 | 2.35 |
| FAILED_AUCTION_RECLAIM | filtered | 156 | 55.49 | 23.67 | 16.31 | 4.15 | 13.04 | 5.20 | 4.82 | 3.79 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.80 | 23.40 | 16.40 | 4.20 | 13.00 | 6.40 | 4.40 | 4.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 49.96 | 23.86 | 9.43 | 4.29 | 14.71 | 7.21 | 4.86 | 2.14 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 69.00 | 21.80 | 14.00 | 6.60 | 11.20 | 6.40 | 6.80 | 3.20 |
| LIQUIDATION_REVERSAL | filtered | 9 | 82.20 | 25.00 | 18.00 | 15.00 | 8.00 | 2.50 | 7.70 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 43.97 | 17.00 | 14.00 | 6.00 | 11.00 | 8.50 | 9.07 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 35 | 70.58 | 22.54 | 15.94 | 4.54 | 11.94 | 5.31 | 9.04 | 1.26 |
| MEAN_REVERT | filtered | 1 | 60.70 | 25.00 | 18.00 | 9.00 | 10.00 | 5.00 | 5.70 | 0.00 |
| MEAN_REVERT | kept | 18 | 67.14 | 17.44 | 14.00 | 12.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 223 | 54.78 | 17.42 | 18.12 | 11.39 | 13.23 | 5.92 | 4.98 | 3.36 |
| MOVER_AVWAP_SCALP | kept | 473 | 79.51 | 20.02 | 18.22 | 11.56 | 13.62 | 6.98 | 8.40 | 4.25 |
| MOVER_TREND_PULLBACK | filtered | 230 | 57.61 | 16.96 | 18.37 | 7.50 | 12.98 | 6.56 | 8.97 | 3.87 |
| MOVER_TREND_PULLBACK | kept | 1316 | 77.81 | 19.48 | 18.03 | 8.11 | 13.21 | 6.40 | 9.32 | 4.30 |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 58.49 | 18.07 | 15.71 | 12.92 | 14.00 | 6.99 | 5.59 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 164 | 73.84 | 19.05 | 15.68 | 10.79 | 14.00 | 6.83 | 8.36 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 60.57 | 22.71 | 10.86 | 7.29 | 14.00 | 5.00 | 7.07 | 2.21 |
| SR_FLIP_RETEST | kept | 36 | 70.93 | 20.33 | 18.00 | 3.00 | 14.00 | 6.26 | 7.46 | 2.04 |
| TREND_PULLBACK_EMA | filtered | 9 | 58.67 | 13.67 | 18.00 | 7.83 | 14.00 | 6.11 | 8.50 | 4.00 |
| TREND_PULLBACK_EMA | kept | 91 | 79.92 | 21.04 | 18.00 | 7.58 | 14.09 | 7.40 | 9.35 | 4.49 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 81.10 | 17.00 | 18.00 | 12.60 | 14.60 | 5.00 | 10.00 | 4.50 |
| WHALE_MOMENTUM | filtered | 37 | 49.61 | 20.24 | 12.32 | 9.08 | 14.92 | 7.18 | 4.13 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 63.70 | 25.00 | 18.00 | 3.00 | 15.00 | 9.00 | 3.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 66 | 59.79 | 0.00 | 0.00 | 1.88 | 0.00 | 3.45 | 0.00 | 0.00 | 0.00 | **5.33** |
| DIVERGENCE_CONTINUATION | kept | 31 | 70.81 | 0.00 | 0.00 | 2.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.12** |
| FAILED_AUCTION_RECLAIM | filtered | 156 | 55.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | **0.23** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 49.96 | 0.00 | 0.00 | 2.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.97** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 69.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 9 | 82.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 43.97 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 35 | 70.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 1 | 60.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 18 | 67.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 223 | 54.78 | 0.00 | 0.00 | 0.00 | 0.00 | 7.60 | 0.00 | 0.00 | 1.61 | **9.21** |
| MOVER_AVWAP_SCALP | kept | 473 | 79.51 | 0.03 | 0.00 | 0.03 | 0.00 | 1.98 | 0.02 | 0.00 | 0.08 | **2.14** |
| MOVER_TREND_PULLBACK | filtered | 230 | 57.61 | 0.00 | 0.00 | 0.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.89** |
| MOVER_TREND_PULLBACK | kept | 1316 | 77.81 | 0.00 | 0.00 | 0.53 | 0.00 | 0.34 | 0.01 | 0.00 | 0.00 | **0.88** |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 58.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 2.16 | **2.62** |
| QUIET_COMPRESSION_BREAK | kept | 164 | 73.84 | 0.00 | 0.00 | 0.68 | 0.00 | 0.03 | 0.00 | 0.00 | 0.13 | **0.84** |
| SR_FLIP_RETEST | filtered | 7 | 60.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.71 | **7.71** |
| SR_FLIP_RETEST | kept | 36 | 70.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 9 | 58.67 | 0.00 | 0.00 | 1.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.78** |
| TREND_PULLBACK_EMA | kept | 91 | 79.92 | 0.00 | 0.00 | 1.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.64** |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 81.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 37 | 49.61 | 0.00 | 0.00 | 0.00 | 0.00 | 7.59 | 0.00 | 0.00 | 0.00 | **7.59** |
| WHALE_MOMENTUM | kept | 1 | 63.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **49100 held of 108869 seen** across 21 strategies; 1090 cells past the sample floor; **462 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 23581 | 91/23490/0 | 44% | -0.16 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.19R) | NY/MARKUP/NORMAL/BTC_RISING (-1.10R) |
| MOVER_AVWAP_SCALP | 5817 | 17/5800/0 | 45% | -0.20 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 3849 | 16/3833/0 | 39% | -0.24 | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (+1.42R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| DIVERGENCE_CONTINUATION | 2458 | 2/2456/0 | 50% | -0.04 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.05R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 2438 | 0/0/2438 | 43% | -0.08 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.72R) | NY/RANGE/EXPANDED/BTC_RISING (-0.89R) |
| TREND_PULLBACK_EMA | 2386 | 0/2386/0 | 43% | -0.22 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+0.72R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.31R) |
| SHADOW_RANGE_FADE | 2069 | 0/0/2069 | 36% | -0.06 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+0.32R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.88R) |
| QUIET_COMPRESSION_BREAK | 1491 | 25/1466/0 | 35% | -0.19 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.54R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 1320 | 0/0/1320 | 40% | -0.31 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | ASIA/MARKUP/NORMAL/BTC_RISING (-0.91R) |
| WHALE_MOMENTUM | 1208 | 0/1208/0 | 35% | -0.45 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| FUNDING_EXTREME_SIGNAL | 610 | 0/610/0 | 28% | -0.52 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| VOLUME_SURGE_BREAKOUT | 506 | 0/506/0 | 56% | +0.12 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| MEAN_REVERT | 410 | 2/408/0 | 74% | +0.54 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| LIQUIDITY_SWEEP_REVERSAL | 362 | 6/356/0 | 37% | -0.26 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-0.26R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-0.45R) |
| SHADOW_CASCADE_REVERSAL | 245 | 0/0/245 | 58% | +0.01 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.03R) |
| BREAKDOWN_SHORT | 144 | 6/138/0 | 8% | -0.85 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| SR_FLIP_RETEST | 96 | 0/96/0 | 69% | -0.01 | — | — |
| RANGE_FADE | 54 | 0/54/0 | 33% | -0.53 | — | — |
| MA_CROSS_TREND_SHIFT | 30 | 0/30/0 | 40% | -0.08 | — | — |
| LIQUIDATION_REVERSAL | 24 | 0/24/0 | 8% | -0.98 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 2 | 0/2/0 | 100% | +0.56 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` +1.54R (n=32, STRONG); `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +1.42R (n=34, STRONG); `MOVER_TREND_PULLBACK @ NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL` +1.19R (n=50, STRONG)
- **Weakest cells**: `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.31R (n=50, NEGATIVE); `TREND_PULLBACK_EMA @ ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.24R (n=17, NEGATIVE); `MOVER_AVWAP_SCALP @ ASIA/RANGE/NORMAL/BTC_RISING/MAJOR` -1.23R (n=27, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 51 | 31% / -0.48R | 51 | 51% / -0.08R | +0.39 | **ATR** |
| TREND_PULLBACK_EMA | 195 | 47% / -0.16R | 195 | 55% / -0.04R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 144 | 38% / -0.38R | 144 | 40% / -0.29R | +0.09 | **ATR** |
| MEAN_REVERT | 39 | 56% / +0.10R | 39 | 56% / +0.19R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 253 | 44% / -0.18R | 253 | 45% / -0.10R | +0.08 | **ATR** |
| MOVER_AVWAP_SCALP | 433 | 51% / -0.10R | 433 | 56% / -0.03R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 35 | 51% / +0.12R | 35 | 54% / +0.05R | -0.07 | **FIXED** |
| MOVER_TREND_PULLBACK | 3483 | 53% / -0.05R | 3483 | 58% / +0.02R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 95 | 47% / -0.20R | 95 | 51% / -0.14R | +0.06 | **ATR** |
| SR_FLIP_RETEST | 21 | 52% / -0.22R | 21 | 52% / -0.18R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 227 | 52% / -0.00R | 227 | 59% / -0.02R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 188 | 45% / -0.17R | 188 | 45% / -0.17R | +0.00 | **ATR** |
| RANGE_FADE | 6 | 50% / +0.16R | 6 | 50% / +0.02R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 10 | 30% / -0.23R | 10 | 30% / -0.17R | — | **MEASURING** |
| BREAKDOWN_SHORT | 9 | 11% / -0.57R | 9 | 11% / -0.34R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 100% / +0.56R | 1 | 100% / +0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 2 | 50% / -0.03R | 2 | 50% / -0.33R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 5175 | 32% | -0.09R | 225 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 433 | 54% | -0.02R | 114 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 24 | 62% | +0.08R | 23 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 56 | 32% / -0.10R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 197 | 44% / +0.32R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4314 | 38% / -0.10R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 512 | 39% / +0.16R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 183 | 38% / -0.02R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 250 | 40% / +0.22R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 255 | 37% / -0.18R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 102 | 41% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 55 | 33% / -0.25R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 56 | 30% / -0.57R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 36 | 58% / +0.18R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 23 | 30% / -0.28R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 6 | 50% / -0.04R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 21 | 33% / -0.42R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 12 | 17% / -0.62R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 4 | 25% / -1.36R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 1 | 100% / +1.90R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 52 · alerting: **7** · boot grace active: False
- **ALERT** `scan_cycle` — last 21.84s, worst 196.59s over 5237 cycles; 76 over 60s, 7 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 233/2) (sustained 233 cycles)
- **ALERT** `candle_coverage` — 119/133 symbols with ≥20 15m candles, 90/133 updated within 45m [no_bucket=13, short=1, stale=29, fresh=90; 16 promoted of 133]; 43 CORE pair(s) unusable (e.g. AGTUSDT, AIAUSDT, ARCUSDT, AVAAIUSDT, AVNTUSDT) (streak 27/6) (sustained 27 cycles)
- **ALERT** `cohort_edge_gate` — all 30 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 30 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 273/6) (sustained 273 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 2629x (gate reads 0x, withheld 0x — refusal dark); last BEATUSDT age=22485.8s (streak 210/6) (sustained 210 cycles)
- **ALERT** `mean_revert_emission` — 8727 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.53R over n=408, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 273/6) (sustained 273 cycles)
- **ALERT** `range_fade_emission` — 4444 detections since last emission (emitted_total=0) — and only 54 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 273/6) (sustained 273 cycles)
- **ALERT** `tuned_variants` — 140 non-stamps — atr_arm_uncomputable=140 (seen=4970 stamped=740 skipped=4090) (streak 273/6) (sustained 273 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 30413525 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 16 arms current, none stalled; covering 302/302 signals (100%) | 0 |
| auto_dispatch | ok | attempts=12 fanouts=12 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 79657.70 | 0 |
| candle_coverage | violating | 119/133 symbols with ≥20 15m candles, 90/133 updated within 45m [no_bucket=13, short=1, stale=29, fresh=90; 16 promoted of 133]; 43 CORE pair(s) unusable (e.g. AGTUSDT, AIAUSDT, ARCUSDT, AVAAIUSDT, AVNTUSDT) (streak 27/6) | 27 |
| candle_series_integrity | ok | merge dropped 4798 dup bars, 0 undedupable; ws 0 out-of-order, 278 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | violating | all 30 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 30 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 273/6) | 273 |
| context_emission_policy | ok | output +8 / upstream +17 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1275/1290 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 6 of 100 open dark rows are not being advanced (worst: CLOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 39/120) | 39 |
| dark_sar_arms | ok | no open arms; covering 1276/1291 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 9912989 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | max divergence MOVER_TREND_PULLBACK +0.28R (< 0.3) | 0 |
| emission_controller | ok | last cycle 1s ago; live_overrides=29 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=16 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4343 stamps (MEAN_REVERT=882, MOVER_AVWAP_SCALP=283, MOVER_TREND_PULLBACK=2584, RANGE_FADE=386, TREND_PULLBACK_EMA=208), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 7846 evaluated, 1399 suppressed, 3762 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1393 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +46 | 0 |
| indicator_cache_key | ok | 106014 frozen value(s) avoided; 461954 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 8727 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.53R over n=408, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 273/6) | 273 |
| mean_revert_path | violating | upstream +46 but output +0 (streak 1/72) | 1 |
| mover_admission_metadata | ok | 882 symbols known, 180 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 16 held, 16 with scan counts, 16 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3111 rows held, 841082 evicted (sampled: execution:trigger_not_confirmed 400/309121, execution:overextended 400/297109, setup_compat:regime_STRONG_TREND 400/108619) | 0 |
| price_action_lane | ok | 456988 evaluated, 665 emitted; layer1 665 stamped / 0 blind; cooldown=58154, delta_opposed=47080, no_footprint=178900, no_opposing_target=358, no_sweep=128570, rr_below_floor=43261 | 0 |
| promoted_pair_integrity | ok | 16/16 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 4444 detections since last emission (emitted_total=0) — and only 54 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 273/6) | 273 |
| range_fade_path | violating | upstream +46 but output +0 (streak 6/72) | 6 |
| sar_alignment_crosscheck | ok | 693/16460 disagreed (4.2%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +46 | 0 |
| sar_hold_arm | ok | 510 held arms settled, 96 unscored, 16 still walking (16 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 8/47 unfetchable (17%); top cause: gap or duplicate bar in the 15m window; symbols: BEAMXUSDT, BEATUSDT, ETHFIUSDT, OPUSDT, SKRUSDT +2 more | 0 |
| sar_live_arms | ok | 16 arms current, none stalled; covering 311/311 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 447 records await one (39 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | violating | last 21.84s, worst 196.59s over 5237 cycles; 76 over 60s, 7 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 233/2) | 233 |
| setup_tf_resolver | ok | 197464 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 33s ago (2.08s to run, worst 113.83s), 735 overrun(s) of 5630 cycles, TTL 900s; slowest tickers=3.29s, engine_state=3.23s, signals=2.58s | 0 |
| stale_tf_scoring | violating | scored on stale TF 2629x (gate reads 0x, withheld 0x — refusal dark); last BEATUSDT age=22485.8s (streak 210/6) | 210 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +59 / upstream +46 | 0 |
| structural_snap | ok | 4349/4349 measured, 16 blind, 0 levels moved (refusals: redetect_cooldown=1691) | 0 |
| structural_veto_lane | ok | 2371 stamped; 0 with no readable level book, 161 with clear air ahead, 1590 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +46 / upstream +17 | 0 |
| tuned_variants | violating | 140 non-stamps — atr_arm_uncomputable=140 (seen=4970 stamped=740 skipped=4090) (streak 273/6) | 273 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `64117`
- `Path funnel` emissions: `25`
- `Regime distribution` emissions: `25`
- `QUIET_SCALP_BLOCK` events: `65`
- `confidence_gate` events: `3007`
- `free_channel_post` events: `7`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **127**
- Total REST-fallback activations: **17**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 33 | 6474 | 10374 | 13874 | 0 |
| futures_aggtrade | 26 | 6720 | 12492 | 18287 | 0 |
| futures_depth | 35 | 6916 | 12644 | 19742 | 0 |
| futures_liq | 8 | 7686 | 13733 | 30970 | 0 |
| futures_mover | 25 | 6375 | 11857 | 15609 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 17 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **7**

| Source | Count |
|---|---:|
| signal_close | 4 |
| regime_shift | 3 |

- By severity: HIGH=7

## Dependency readiness
- cvd: presence[present=168755] state[populated=168755] buckets[many=168755] sources[none] quality[none]
- funding_rate: presence[absent=17132, present=151623] state[empty=17132, populated=151623] buckets[few=151623, none=17132] sources[none] quality[none]
- liquidation_clusters: presence[absent=98450, present=70305] state[empty=98450, populated=70305] buckets[few=55181, none=98450, some=15124] sources[none] quality[none]
- oi_snapshot: presence[absent=17132, present=151623] state[empty=17132, populated=151623] buckets[few=304, many=149734, none=17132, some=1585] sources[none] quality[none]
- order_book: presence[absent=52036, present=116719] state[populated=116719, unavailable=52036] buckets[few=116719, none=52036] sources[book_ticker=116719, unavailable=52036] quality[none=52036, top_of_book_only=116719]
- orderblocks: presence[absent=168755] state[empty=168755] buckets[none=168755] sources[measured_dark=168755] quality[none]
- recent_ticks: presence[present=168755] state[populated=168755] buckets[many=168755] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `17.148499011993408` sec
- Median create→first breach: `8539.285578846931` sec
- Median create→terminal: `8541.647826433182` sec
- Median first breach→terminal: `3.0542235374450684` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.7999999999999914 | 1.3245728432174377 | 0.6039682937004514 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.5665101963882644 | 1.761923240386571 | 0.8890910571362732 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.131495027610101 | 2.2566612946527 | 0.93473387452752 | 1 | 1 |
| MOVER_TREND_PULLBACK | 4 | 4 | 2.9327955862679875 | 2.839491157714812 | 1.0210317782388831 | 2 | 2 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 1.24418692265596 | 1.2441869220044917 | 1.0000000003858587 | 0 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3246 | 1722.3304901123047 | 1728.6432201862335 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.5665 | 25434.99946498871 | 25436.123683929443 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.8281 | 12700.986682415009 | 12704.679043531418 |
| MOVER_TREND_PULLBACK | 4 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 8278.909356951714 | 8281.281893968582 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 12996.103623986244 | 13006.648076415062 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 922 | 5 | 810 | 0.0 | 0.0 | None | None | 112 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1125 | 20 | 971 | 0.0 | 0.0 | None | None | 154 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-211`
- Gating Δ: `-31834`
- No-generation Δ: `-562581`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0717, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.0717, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": -25, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 12, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
