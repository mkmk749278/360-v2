# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `862` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 40 | 40 | 40 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6210 | 6210 | 5388 | 16 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 70940 | 70969 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 64686 | 64688 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 64272 | 62871 | 1811 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 64726 | 63976 | 828 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 64340 | 64186 | 191 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 54023 | 54043 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 64806 | 64854 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 64857 | 63585 | 1892 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 75018 | 82322 | 770 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 70989 | 63452 | 11511 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 64020 | 64022 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 64694 | 64713 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 64248 | 64248 | 22 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 65491 | 64382 | 1424 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 63898 | 64064 | 142 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 53423 | 49874 | 3938 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 53818 | 53523 | 384 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 70894 | 70893 | 42 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 54050 | 54074 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2469 | 2469 | 2150 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 580 | 580 | 203 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 9 | 9 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15581 | 15581 | 15309 | 9 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 4135 | 4135 | 2325 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1623 | 1623 | 276 | 41 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 24104 | 24104 | 11676 | 363 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 17 | 17 | 0 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 192 | 192 | 58 | 17 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2694 | 2694 | 1270 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 468 | 468 | 117 | 10 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1383 | 1383 | 1001 | 40 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 131 | 131 | 67 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=70969): breakout_not_found=41669, basic_filters_failed=15917, move_not_fresh=9255, breakout_stale=2908, retest_proximity_failed=1030, volume_spike_missing=173, move_exhausted=14, missing_fvg_or_orderblock=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=64688): cls_disabled_merged_into_lsr=64688
- **EVAL::DIVERGENCE_CONTINUATION** (total=62871): cvd_divergence_failed=24787, h1_trend_not_aligned=18941, basic_filters_failed=12211, ema_alignment_reject=5614, retest_proximity_failed=1141, missing_fvg_or_orderblock=177
- **EVAL::FAILED_AUCTION_RECLAIM** (total=63976): auction_not_detected=44601, basic_filters_failed=11513, regime_blocked=3438, reclaim_hold_failed=2446, tail_too_small=1976, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=64186): funding_not_extreme=45442, basic_filters_failed=10580, missing_funding_rate=5905, ema_alignment_reject=1292, rsi_reject=704, cvd_divergence_failed=161, momentum_reject=87, missing_fvg_or_orderblock=15
- **EVAL::LIQUIDATION_REVERSAL** (total=54043): cascade_threshold_not_met=41239, basic_filters_failed=12041, cvd_divergence_failed=380, rsi_reject=363, missing_fvg_or_orderblock=16, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=64854): no_ma_cross=52160, basic_filters_failed=12231, ma_cross_htf_misaligned=354, ma_cross_cooldown=109
- **EVAL::MEAN_REVERT** (total=63585): no_extension=52197, basic_filters_failed=11388
- **EVAL::MOVER_AVWAP_SCALP** (total=82322): no_avwap_tag=31772, no_mover_leg=20192, basic_filters_failed=16095, avwap_slope_against=9543, avwap_reclaim_no_volume=2772, no_avwap_reclaim=1868, anchor_too_recent=80
- **EVAL::MOVER_TREND_PULLBACK** (total=63452): mover_run_too_small=28879, no_reclaim=16672, basic_filters_failed=16014, no_pullback_tag=1887
- **EVAL::OPENING_RANGE_BREAKOUT** (total=64022): feature_disabled=64022
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=64713): regime_blocked=39438, breakout_not_found=20345, basic_filters_failed=3456, adx_reject=1413, ema_alignment_reject=61
- **EVAL::QUIET_COMPRESSION_BREAK** (total=64248): regime_blocked=28557, compression_not_detected=25911, basic_filters_failed=8040, breakout_not_detected=1568, volume_confirmation_failed=163, rsi_reject=6, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=64382): no_range_edge=52988, basic_filters_failed=11394
- **EVAL::SR_FLIP_RETEST** (total=64064): flip_close_not_confirmed=44722, basic_filters_failed=11486, regime_blocked=3413, h1_break_not_confirmed=1311, long_break_volume_thin=1261, retest_out_of_zone=1256, reclaim_hold_failed=444, long_acceptance_not_held=58, whipsaw_flip=47, ema_alignment_reject=28, wick_quality_failed=19, missing_fvg_or_orderblock=19
- **EVAL::STANDARD** (total=49874): momentum_reject=13760, adx_reject=12174, basic_filters_failed=7897, ema_alignment_reject=5846, sweeps_not_detected=4941, macd_reject=4321, htf_poi_unanchored=851, rsi_reject=49, invalid_sl_geometry=20, mtf_reject=15
- **EVAL::TREND_PULLBACK** (total=53523): h1_trend_not_aligned=18517, ema_alignment_reject=9916, basic_filters_failed=6776, h1_pullback_not_confirmed=6242, ema_not_tested_prev=3926, no_ema_reclaim_close=3079, body_conviction_fail=1995, rsi_reject=1725, prev_already_below_emas=568, no_prev_low_break=370, prev_already_above_emas=148, no_prev_high_break=84, momentum_flat=76, missing_fvg_or_orderblock=48, ema21_not_tagged=45, momentum_reject=8
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=70893): breakout_not_found=39588, basic_filters_failed=15913, move_not_fresh=9813, breakout_stale=3748, retest_proximity_failed=1553, volume_spike_missing=251, move_exhausted=15, missing_fvg_or_orderblock=12
- **EVAL::WHALE_MOMENTUM** (total=54074): momentum_reject=44800, recent_ticks_insufficient=8321, basic_filters_failed=953

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=14): execution:overextended=14
- **DIVERGENCE_CONTINUATION** (total=395): setup_compat:regime_VOLATILE_UNSUITABLE=386, setup_compat:regime_BREAKOUT_EXPANSION=9
- **FAILED_AUCTION_RECLAIM** (total=1099): execution:overextended=683, setup_compat:regime_STRONG_TREND=331, context_floor=71, setup_compat:regime_VOLATILE_UNSUITABLE=14
- **FUNDING_EXTREME_SIGNAL** (total=473): execution:trigger_not_confirmed=457, context_floor=16
- **LIQUIDATION_REVERSAL** (total=12): execution:trigger_not_confirmed=9, context_floor=3
- **LIQUIDITY_SWEEP_REVERSAL** (total=4199): setup_compat:regime_STRONG_TREND=1676, execution:trigger_not_confirmed=1275, execution:overextended=1248
- **MA_CROSS_TREND_SHIFT** (total=2): setup_compat:regime_CLEAN_RANGE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=3058): setup_compat:regime_WEAK_TREND=1499, setup_compat:regime_STRONG_TREND=1255, execution:overextended=304
- **MOVER_AVWAP_SCALP** (total=965): execution:overextended=646, entry_quality=161, execution:trigger_not_confirmed=158
- **MOVER_TREND_PULLBACK** (total=12272): execution:trigger_not_confirmed=7587, execution:overextended=2783, entry_quality=1902
- **QUIET_COMPRESSION_BREAK** (total=18): execution:trigger_not_confirmed=18
- **RANGE_FADE** (total=2390): setup_compat:regime_STRONG_TREND=1199, setup_compat:regime_WEAK_TREND=720, execution:overextended=339, context_edge=81, setup_compat:regime_VOLATILE_UNSUITABLE=40, setup_compat:regime_BREAKOUT_EXPANSION=11
- **TREND_PULLBACK_EMA** (total=1289): setup_compat:regime_CLEAN_RANGE=920, setup_compat:regime_DIRTY_RANGE=273, entry_quality=76, setup_compat:regime_VOLATILE_UNSUITABLE=20
- **VOLUME_SURGE_BREAKOUT** (total=4): execution:overextended=4

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 126787 | 38.8% |
| TRENDING_UP | 70640 | 21.6% |
| TRENDING_DOWN | 59541 | 18.2% |
| QUIET | 54910 | 16.8% |
| VOLATILE | 14729 | 4.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **97**
- Average confidence gap to threshold: **16.59** (samples=97) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ONDOUSDT=16, XMRUSDT=15, AVAXUSDT=14, JCTUSDT=11, ETHUSDT=10, XRPUSDT=8, HYPEUSDT=6, TAOUSDT=5, LTCUSDT=5, ARBUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 116 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 72 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 82 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 14 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 9 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 74 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 71 |
| MEAN_REVERT | filtered | min_confidence | 7 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 515 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 304 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2144 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 42 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3793 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 17 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 28 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 18 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 66 |
| SR_FLIP_RETEST | filtered | min_confidence | 47 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 84 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 46 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 163 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 51 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 13 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 116 | 53.58 | 64.57 | 10.99 | 19.64 | 19.38 | 18.23 | 2.04 | 15.90 |
| DIVERGENCE_CONTINUATION | kept | 72 | 67.30 | 65.00 | -2.30 | 20.42 | 19.85 | 18.02 | 1.08 | -0.92 |
| FAILED_AUCTION_RECLAIM | filtered | 96 | 41.27 | 62.29 | 21.02 | 22.49 | 18.78 | 20.00 | 1.70 | 16.00 |
| FAILED_AUCTION_RECLAIM | kept | 9 | 67.56 | 65.00 | -2.56 | 20.84 | 18.39 | 20.00 | 4.56 | 4.19 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 46.36 | 61.00 | 14.64 | 16.98 | 13.76 | 19.40 | 4.60 | 15.96 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 64.50 | 65.00 | 0.50 | 19.90 | 13.65 | 15.85 | 3.50 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 81 | 45.95 | 64.36 | 18.41 | 19.84 | 19.38 | 18.43 | 1.31 | 9.36 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 71 | 70.77 | 65.00 | -5.77 | 21.57 | 19.33 | 19.11 | 1.64 | 0.36 |
| MEAN_REVERT | filtered | 7 | 56.83 | 65.00 | 8.17 | 21.03 | 15.71 | 15.91 | 0.00 | 9.73 |
| MEAN_REVERT | kept | 1 | 68.70 | 65.00 | -3.70 | 19.20 | 17.10 | 20.00 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 516 | 54.19 | 64.28 | 10.09 | 20.51 | 16.21 | 15.80 | 3.59 | 9.65 |
| MOVER_AVWAP_SCALP | kept | 304 | 76.29 | 65.00 | -11.29 | 20.78 | 15.94 | 15.80 | 4.40 | 5.39 |
| MOVER_TREND_PULLBACK | filtered | 2186 | 56.43 | 64.37 | 7.94 | 19.71 | 18.75 | 15.80 | 3.95 | 18.97 |
| MOVER_TREND_PULLBACK | kept | 3793 | 77.31 | 65.00 | -12.31 | 20.25 | 18.55 | 15.80 | 4.28 | 1.26 |
| POST_DISPLACEMENT_CONTINUATION | kept | 17 | 88.96 | 65.00 | -23.96 | 20.55 | 20.00 | 18.40 | 5.65 | 3.80 |
| QUIET_COMPRESSION_BREAK | filtered | 46 | 44.37 | 64.91 | 20.54 | 21.63 | 19.46 | 20.00 | 0.00 | 13.84 |
| QUIET_COMPRESSION_BREAK | kept | 66 | 73.95 | 65.00 | -8.95 | 22.13 | 19.67 | 20.00 | 0.00 | 2.60 |
| SR_FLIP_RETEST | filtered | 47 | 58.77 | 64.32 | 5.55 | 20.70 | 20.00 | 16.31 | 1.46 | 7.42 |
| SR_FLIP_RETEST | kept | 84 | 68.79 | 65.00 | -3.79 | 20.33 | 20.00 | 15.88 | 1.85 | 0.59 |
| TREND_PULLBACK_EMA | filtered | 51 | 57.44 | 65.00 | 7.56 | 20.59 | 19.99 | 18.93 | 4.99 | 13.89 |
| TREND_PULLBACK_EMA | kept | 163 | 79.82 | 65.00 | -14.82 | 21.13 | 19.33 | 18.16 | 4.75 | -0.47 |
| VOLUME_SURGE_BREAKOUT | filtered | 51 | 59.59 | 63.14 | 3.55 | 20.78 | 18.27 | 20.00 | 4.74 | 14.02 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 75.65 | 65.00 | -10.65 | 20.59 | 16.71 | 20.00 | 5.04 | 3.09 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 116 | 53.58 | 21.76 | 11.79 | 6.16 | 13.69 | 5.07 | 8.96 | 2.04 |
| DIVERGENCE_CONTINUATION | kept | 72 | 67.30 | 22.44 | 13.69 | 4.50 | 12.22 | 5.40 | 8.79 | 1.08 |
| FAILED_AUCTION_RECLAIM | filtered | 96 | 41.27 | 19.33 | 17.42 | 6.97 | 15.42 | 6.56 | 4.07 | 1.70 |
| FAILED_AUCTION_RECLAIM | kept | 9 | 67.56 | 24.11 | 14.89 | 3.33 | 14.22 | 6.89 | 5.40 | 4.56 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 46.36 | 25.00 | 8.00 | 6.60 | 12.60 | 8.50 | 3.02 | 4.60 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 64.50 | 21.00 | 19.00 | 4.50 | 10.50 | 7.50 | 4.50 | 3.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 81 | 45.95 | 20.58 | 16.37 | 7.33 | 12.31 | 5.99 | 4.58 | 1.31 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 71 | 70.77 | 19.90 | 15.75 | 7.99 | 12.79 | 5.06 | 8.00 | 1.64 |
| MEAN_REVERT | filtered | 7 | 56.83 | 20.43 | 14.00 | 6.43 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 1 | 68.70 | 25.00 | 14.00 | 6.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 516 | 54.19 | 18.08 | 18.10 | 11.25 | 14.19 | 6.16 | 4.84 | 3.59 |
| MOVER_AVWAP_SCALP | kept | 304 | 76.29 | 19.01 | 18.02 | 11.99 | 14.10 | 6.91 | 7.68 | 4.40 |
| MOVER_TREND_PULLBACK | filtered | 2186 | 56.43 | 18.61 | 18.00 | 7.88 | 13.21 | 5.80 | 8.64 | 3.95 |
| MOVER_TREND_PULLBACK | kept | 3793 | 77.31 | 19.53 | 18.03 | 7.90 | 13.37 | 6.49 | 9.11 | 4.28 |
| POST_DISPLACEMENT_CONTINUATION | kept | 17 | 88.96 | 23.12 | 18.00 | 15.00 | 14.00 | 9.00 | 8.00 | 5.65 |
| QUIET_COMPRESSION_BREAK | filtered | 46 | 44.37 | 21.00 | 16.43 | 9.78 | 14.00 | 7.09 | 3.93 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 66 | 73.95 | 17.48 | 17.58 | 10.82 | 14.00 | 8.05 | 8.79 | 0.00 |
| SR_FLIP_RETEST | filtered | 47 | 58.77 | 15.85 | 18.00 | 5.04 | 12.60 | 5.22 | 8.03 | 1.46 |
| SR_FLIP_RETEST | kept | 84 | 68.79 | 21.05 | 14.55 | 5.14 | 12.85 | 5.80 | 8.26 | 1.85 |
| TREND_PULLBACK_EMA | filtered | 51 | 57.44 | 9.51 | 18.00 | 7.65 | 14.29 | 8.10 | 8.79 | 4.99 |
| TREND_PULLBACK_EMA | kept | 163 | 79.82 | 18.96 | 18.00 | 7.75 | 15.28 | 6.75 | 9.32 | 4.75 |
| VOLUME_SURGE_BREAKOUT | filtered | 51 | 59.59 | 22.02 | 15.02 | 12.00 | 13.76 | 4.71 | 6.40 | 4.74 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 75.65 | 23.15 | 14.92 | 12.23 | 14.00 | 4.42 | 7.28 | 5.04 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 116 | 53.58 | 0.00 | 0.00 | 1.10 | 0.00 | 0.41 | 0.47 | 0.00 | 0.00 | **1.98** |
| DIVERGENCE_CONTINUATION | kept | 72 | 67.30 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.07** |
| FAILED_AUCTION_RECLAIM | filtered | 96 | 41.27 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.83** |
| FAILED_AUCTION_RECLAIM | kept | 9 | 67.56 | 0.00 | 0.00 | 4.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.09** |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 46.36 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 64.50 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 81 | 45.95 | 0.00 | 0.00 | 1.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.26** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 71 | 70.77 | 0.00 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.32** |
| MEAN_REVERT | filtered | 7 | 56.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 1 | 68.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 516 | 54.19 | 0.00 | 0.00 | 0.60 | 0.00 | 1.04 | 0.00 | 0.00 | 1.71 | **3.35** |
| MOVER_AVWAP_SCALP | kept | 304 | 76.29 | 1.04 | 0.00 | 0.25 | 0.00 | 0.85 | 0.00 | 0.00 | 0.85 | **2.99** |
| MOVER_TREND_PULLBACK | filtered | 2186 | 56.43 | 0.00 | 0.00 | 1.07 | 0.00 | 0.61 | 0.00 | 0.00 | 0.00 | **1.68** |
| MOVER_TREND_PULLBACK | kept | 3793 | 77.31 | 0.00 | 0.00 | 0.30 | 0.00 | 0.12 | 0.01 | 0.00 | 0.00 | **0.43** |
| POST_DISPLACEMENT_CONTINUATION | kept | 17 | 88.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 46 | 44.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.56 | 0.00 | 0.00 | 6.65 | **7.21** |
| QUIET_COMPRESSION_BREAK | kept | 66 | 73.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | **0.33** |
| SR_FLIP_RETEST | filtered | 47 | 58.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 84 | 68.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 51 | 57.44 | 0.00 | 0.00 | 0.00 | 0.00 | 2.12 | 0.00 | 0.00 | 0.00 | **2.12** |
| TREND_PULLBACK_EMA | kept | 163 | 79.82 | 0.00 | 0.00 | 0.37 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.50** |
| VOLUME_SURGE_BREAKOUT | filtered | 51 | 59.59 | 0.00 | 0.00 | 2.98 | 0.00 | 0.00 | 0.00 | 0.00 | 1.39 | **4.37** |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 75.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.55 | **0.55** |

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
- Outcomes recorded: **168231 held of 675213 seen** across 21 strategies; 3788 cells past the sample floor; **1986 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46765 | 700/46065/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.40R) |
| MOVER_AVWAP_SCALP | 22233 | 200/22033/0 | 42% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12565 | 151/12414/0 | 48% | -0.08 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12364 | 144/12220/0 | 38% | -0.28 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 10667 | 53/10614/0 | 40% | -0.25 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9249 | 109/9140/0 | 35% | -0.47 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 7781 | 0/0/7781 | 42% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.59R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.22R) |
| SHADOW_RANGE_FADE | 7328 | 0/0/7328 | 36% | -0.12 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.37R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| QUIET_COMPRESSION_BREAK | 7203 | 422/6781/0 | 50% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_FUNDING_FADE | 6595 | 0/0/6595 | 35% | -0.40 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 4890 | 18/4872/0 | 47% | -0.23 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4795 | 58/4737/0 | 37% | -0.34 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3670 | 2/3668/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3487 | 0/3487/0 | 31% | -0.35 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2062 | 6/2056/0 | 38% | -0.27 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1539 | 0/0/1539 | 52% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 472 | 0/472/0 | 31% | -0.55 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 162 | 32/130/0 | 43% | -0.15 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 44 | 2/42/0 | 27% | -0.14 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.63R (n=26, NEGATIVE); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.63R (n=26, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 300 | 27% / -0.58R | 300 | 54% / -0.09R | +0.50 | **ATR** |
| LIQUIDATION_REVERSAL | 31 | 23% / -0.71R | 31 | 45% / -0.37R | +0.34 | **ATR** |
| TREND_PULLBACK_EMA | 952 | 38% / -0.35R | 952 | 51% / -0.07R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1437 | 42% / -0.37R | 1437 | 56% / -0.13R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 184 | 35% / -0.21R | 184 | 46% / -0.07R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 2206 | 43% / -0.19R | 2206 | 50% / -0.06R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 462 | 44% / -0.29R | 462 | 48% / -0.17R | +0.13 | **ATR** |
| MOVER_TREND_PULLBACK | 8403 | 49% / -0.12R | 8403 | 54% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1265 | 41% / -0.22R | 1265 | 43% / -0.12R | +0.10 | **ATR** |
| MA_CROSS_TREND_SHIFT | 49 | 41% / -0.17R | 49 | 45% / -0.07R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 107 | 37% / -0.16R | 107 | 44% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1435 | 48% / -0.11R | 1435 | 54% / -0.05R | +0.07 | **ATR** |
| MEAN_REVERT | 350 | 45% / -0.21R | 350 | 44% / -0.22R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1268 | 48% / -0.12R | 1268 | 48% / -0.13R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 10 | 50% / -0.22R | 10 | 50% / -0.17R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11323 | 28% | -0.22R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2206 | 48% | -0.05R | 232 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 117 | 48% | -0.06R | 66 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1652 | 39% / -0.15R | +0.86 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1262 | 33% / -0.25R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2724 | 34% / -0.17R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10308 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1659 | 37% / -0.11R | +0.17 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1230 | 37% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1063 | 32% / -0.24R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 267 | 31% / -0.34R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 403 | 33% / -0.12R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 296 | 46% / -0.11R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 80 | 44% / +0.03R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 423 | 33% / -0.31R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 78 | 29% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 39 | 46% / -0.19R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 18 | 44% / +0.72R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×195]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 135/6) (sustained 135 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.48R (bound 0.3) (streak 135/6) (sustained 135 cycles)
- **ALERT** `tuned_variants` — 170 non-stamps — atr_arm_uncomputable=170 (seen=5107 stamped=594 skipped=4343) (streak 112/6) (sustained 112 cycles)
- **ALERT** `auto_dispatch` — 35 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=38) (streak 131/3) (sustained 131 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 18191219 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 21 arms current, none stalled; covering 2050/2050 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 3/6) | 3 |
| atr_trail_live_arms | ok | 45 arms current, none stalled; covering 1051/1051 signals (100%) | 0 |
| auto_dispatch | violating | 35 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=38) (streak 131/3) | 131 |
| binance_ip_weight | ok | peak 470/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 77336.70 | 0 |
| candle_coverage | ok | 98/98 symbols with ≥20 15m candles, 98/98 updated within 45m [fresh=98; 73 Tier-1 futures + 25 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1169 dup bars, 0 undedupable; ws 0 out-of-order, 125 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +32 / upstream +21 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1479/1498 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 142 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1473/1492 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4509932 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.48R (bound 0.3) (streak 135/6) | 135 |
| emission_controller | ok | last cycle 766s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×195]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 135/6) | 135 |
| entry_quality_effective | ok | 5323 evaluated, 1843 suppressed, 2343 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,336 reads/day of 50,000 [engine 1,307, signing 29]; top site runtime_tunables.doc at 288/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +13 / upstream +275 | 0 |
| indicator_cache_key | ok | 41308 frozen value(s) avoided; 71987 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.35R over n=4737 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +15 / upstream +275 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 25 held, 25 with scan counts, 24 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2074 rows held, 3229600 evicted (sampled: execution:trigger_not_confirmed 281/1139420, execution:overextended 281/1014505, setup_compat:regime_STRONG_TREND 281/547180) | 0 |
| price_action_lane | ok | 270066 evaluated, 508 emitted; layer1 508 stamped / 0 blind; cooldown=41608, delta_opposed=21003, no_footprint=109941, no_opposing_target=1005, no_sweep=77545, rr_below_floor=18456 | 0 |
| promoted_pair_integrity | ok | 25/25 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.27R over n=2056 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +18 / upstream +275 | 0 |
| sar_alignment_crosscheck | ok | 418/9077 disagreed (4.6%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +275 | 0 |
| sar_hold_arm | ok | 1874 held arms settled, 128 unscored, 40 still walking (36 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 7/86 unfetchable (8%); top cause: gap or duplicate bar in the 15m window; symbols: BEATUSDT, PONSUSDT, USELESSUSDT | 0 |
| sar_live_arms | ok | 43 arms current, none stalled; covering 1050/1050 signals (100%) | 0 |
| sar_refresh_budget | ok | 8 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 12 resolved, 67 still mid-window | 0 |
| scan_cycle | ok | last 59.35s, worst 160.92s over 3068 lifetime cycles; lifetime 158 over 60s, 15 over 120s (plus 1/0 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 5.1s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 121583 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (2.41s to run, worst 124.73s), 491 overrun(s) of 3085 cycles, TTL 900s; slowest signals=0.52s, user_positions=0.5s, router_delivery=0.22s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +117 / upstream +275 | 0 |
| structural_snap | ok | 6000/6000 measured, 36 blind, 0 levels moved (refusals: redetect_cooldown=695) | 0 |
| structural_veto_lane | ok | 1141 stamped; 0 with no readable level book, 6 with clear air ahead, 675 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +275 / upstream +21 | 0 |
| tuned_variants | violating | 170 non-stamps — atr_arm_uncomputable=170 (seen=5107 stamped=594 skipped=4343) (streak 112/6) | 112 |
| unlock_shorts | ok | 15 open, 46 scheduled, calendar 1.8h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 11 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1773386`
- `Path funnel` emissions: `37`
- `Regime distribution` emissions: `37`
- `QUIET_SCALP_BLOCK` events: `97`
- `confidence_gate` events: `7797`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **5**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 2 | 32315 | 32315 | 35215 | 0 |
| futures_liq | 2 | 6637 | 6637 | 16572 | 0 |
| futures_mover | 1 | 32313 | 32313 | 32313 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=261304] state[populated=261304] buckets[many=261304] sources[none] quality[none]
- funding_rate: presence[absent=51839, present=209465] state[empty=51839, populated=209465] buckets[few=209465, none=51839] sources[none] quality[none]
- liquidation_clusters: presence[absent=155465, present=105839] state[empty=155465, populated=105839] buckets[few=87832, none=155465, some=18007] sources[none] quality[none]
- oi_snapshot: presence[absent=51184, present=210120] state[empty=51184, populated=210120] buckets[many=210120, none=51184] sources[none] quality[none]
- order_book: presence[absent=92328, present=168976] state[populated=168976, unavailable=92328] buckets[few=168976, none=92328] sources[book_ticker=168976, unavailable=92328] quality[none=92328, top_of_book_only=168976]
- orderblocks: presence[absent=261304] state[empty=261304] buckets[none=261304] sources[measured_dark=261304] quality[none]
- recent_ticks: presence[present=261304] state[populated=261304] buckets[many=261304] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.406306028366089` sec
- Median create→first breach: `3291.885146856308` sec
- Median create→terminal: `3292.5184619426727` sec
- Median first breach→terminal: `5.2928924560546875e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.3}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.3}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 2.989142857142849 | 3.0 | 0.9963809523809496 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.2764062257823 | 2.7954886348178127 | 0.8256730756970241 | 0 | 3 |
| MOVER_TREND_PULLBACK | 32 | 32 | 4.098575337649834 | 3.0 | 1.4134512325810884 | 24 | 7 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.5113473335399552 | 1.5113473355537022 | 0.9357197780147811 | 0 | 3 |
| TREND_PULLBACK_EMA | 2 | 2 | 2.6573969123283607 | 3.0 | 0.8857989707761204 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.9891 | 3734.5040390491486 | 3734.504101037979 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -1.4468 | 11429.721516132355 | 11429.721536159515 |
| MOVER_TREND_PULLBACK | 32 | 32 | 34.4 | 37.5 | 34.4 | 0.0 | 0.237 | 2939.4397000074387 | 2939.847874522209 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 20.0 | 40.0 | 20.0 | 0.0 | 0.0315 | 6165.628509044647 | 6165.628568887711 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2994 | 2536.662176966667 | 2536.6622265577316 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 468 | 10 | 117 | 0.0 | 0.0 | None | None | 351 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1383 | 40 | 1001 | 0.0 | 50.0 | 2536.662176966667 | 2536.6622265577316 | 382 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-130`
- Gating Δ: `7395`
- No-generation Δ: `553762`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.6462, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.6462, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.9603, "current_avg_pnl": -1.4468, "current_win_rate": 0.0, "previous_avg_pnl": 0.5135, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.1728, "current_avg_pnl": 0.237, "current_win_rate": 34.4, "previous_avg_pnl": 0.4098, "previous_win_rate": 25.9, "win_rate_delta": 8.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.5376, "current_avg_pnl": 0.0315, "current_win_rate": 20.0, "previous_avg_pnl": -0.5061, "previous_win_rate": 0.0, "win_rate_delta": 20.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 219, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 22, "geometry_changed_delta": 0, "geometry_preserved_delta": 220, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -5672.12, "median_terminal_delta_sec": -5672.12, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
