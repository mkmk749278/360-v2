# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `1426` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 538 | 538 | 533 | 4 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 19109 | 19109 | 18655 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 105941 | 105846 | 105 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 86428 | 86428 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 86296 | 82159 | 4265 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 86433 | 85230 | 1233 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 89310 | 88753 | 571 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 80823 | 80830 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 86463 | 86469 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 86477 | 83749 | 3418 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 110309 | 113600 | 1649 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 105952 | 94379 | 15913 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 88940 | 88940 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 86428 | 86432 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 86285 | 86139 | 155 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 87171 | 85937 | 1468 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 85902 | 86110 | 160 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 77862 | 73128 | 4885 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 78013 | 77224 | 835 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 105913 | 105929 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 80833 | 80827 | 9 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6658 | 6658 | 6169 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2367 | 2367 | 1161 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 12 | 12 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 27549 | 27549 | 27427 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 7 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 10954 | 10954 | 9653 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4873 | 4873 | 3961 | 82 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 52879 | 52879 | 48202 | 116 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1339 | 1339 | 1303 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4476 | 4476 | 4124 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1458 | 1458 | 1458 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3796 | 3796 | 3647 | 7 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 26 | 26 | 10 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 796 | 796 | 258 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=105846): breakout_not_found=56201, basic_filters_failed=29873, move_not_fresh=11469, breakout_stale=6271, retest_proximity_failed=1699, volume_spike_missing=313, missing_fvg_or_orderblock=17, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=86428): cls_disabled_merged_into_lsr=86428
- **EVAL::DIVERGENCE_CONTINUATION** (total=82159): cvd_divergence_failed=34518, basic_filters_failed=19820, h1_trend_not_aligned=19738, ema_alignment_reject=7090, retest_proximity_failed=564, missing_fvg_or_orderblock=237, missing_cvd=191, cvd_insufficient=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=85230): auction_not_detected=54467, basic_filters_failed=19386, reclaim_hold_failed=4815, tail_too_small=3652, regime_blocked=2896, rsi_reject=14
- **EVAL::FUNDING_EXTREME** (total=88753): funding_not_extreme=60012, basic_filters_failed=20584, ema_alignment_reject=3934, rsi_reject=1640, missing_funding_rate=1565, cvd_divergence_failed=500, momentum_reject=459, missing_fvg_or_orderblock=59
- **EVAL::LIQUIDATION_REVERSAL** (total=80830): cascade_threshold_not_met=59246, basic_filters_failed=20962, cvd_divergence_failed=316, rsi_reject=281, missing_fvg_or_orderblock=16, missing_cvd=6, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=86469): no_ma_cross=65067, basic_filters_failed=19821, ma_cross_htf_misaligned=901, ma_cross_cooldown=611, ma_cross_htf_unconfirmed=69
- **EVAL::MEAN_REVERT** (total=83749): no_extension=70061, basic_filters_failed=13688
- **EVAL::MOVER_AVWAP_SCALP** (total=113600): no_avwap_tag=47496, basic_filters_failed=29957, no_mover_leg=24017, avwap_slope_against=5946, avwap_reclaim_no_volume=3955, no_avwap_reclaim=2176, anchor_too_recent=53
- **EVAL::MOVER_TREND_PULLBACK** (total=94379): mover_run_too_small=43784, basic_filters_failed=29911, no_reclaim=18333, no_pullback_tag=2351
- **EVAL::OPENING_RANGE_BREAKOUT** (total=88940): feature_disabled=88940
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=86432): regime_blocked=58395, breakout_not_found=19834, basic_filters_failed=4544, adx_reject=3604, ema_alignment_reject=55
- **EVAL::QUIET_COMPRESSION_BREAK** (total=86139): compression_not_detected=35169, regime_blocked=30894, basic_filters_failed=14840, breakout_not_detected=4860, volume_confirmation_failed=363, rsi_reject=11, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=85937): no_range_edge=72249, basic_filters_failed=13688
- **EVAL::SR_FLIP_RETEST** (total=86110): flip_close_not_confirmed=54886, basic_filters_failed=19383, regime_blocked=2892, h1_break_not_confirmed=2850, long_break_volume_thin=2725, retest_out_of_zone=2115, reclaim_hold_failed=634, long_acceptance_not_held=454, ema_alignment_reject=62, wick_quality_failed=59, whipsaw_flip=38, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=73128): momentum_reject=23367, adx_reject=16301, basic_filters_failed=11427, sweeps_not_detected=8394, macd_reject=7333, ema_alignment_reject=4983, htf_poi_unanchored=1210, invalid_sl_geometry=44, rsi_reject=42, mtf_reject=27
- **EVAL::TREND_PULLBACK** (total=77224): h1_trend_not_aligned=23139, h1_pullback_not_confirmed=13016, ema_alignment_reject=12245, basic_filters_failed=10177, no_ema_reclaim_close=5779, ema_not_tested_prev=5429, body_conviction_fail=2837, rsi_reject=2077, prev_already_below_emas=1187, no_prev_low_break=613, prev_already_above_emas=224, no_prev_high_break=171, ema21_not_tagged=155, momentum_flat=126, missing_fvg_or_orderblock=36, momentum_reject=13
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=105929): breakout_not_found=62980, basic_filters_failed=29873, move_not_fresh=7499, breakout_stale=3995, retest_proximity_failed=1302, volume_spike_missing=265, missing_fvg_or_orderblock=11, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=80827): momentum_reject=59422, recent_ticks_insufficient=14900, basic_filters_failed=6505

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=20): execution:overextended=20
- **DIVERGENCE_CONTINUATION** (total=577): setup_compat:regime_VOLATILE_UNSUITABLE=498, setup_compat:regime_BREAKOUT_EXPANSION=79
- **FAILED_AUCTION_RECLAIM** (total=1878): setup_compat:regime_STRONG_TREND=962, execution:overextended=762, setup_compat:regime_VOLATILE_UNSUITABLE=106, context_floor=48
- **FUNDING_EXTREME_SIGNAL** (total=2120): execution:trigger_not_confirmed=2089, context_floor=31
- **LIQUIDATION_REVERSAL** (total=12): execution:trigger_not_confirmed=12
- **LIQUIDITY_SWEEP_REVERSAL** (total=6186): execution:trigger_not_confirmed=2686, execution:overextended=2026, setup_compat:regime_STRONG_TREND=1474
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=3, setup_compat:regime_CLEAN_RANGE=2
- **MEAN_REVERT** (total=7204): setup_compat:regime_STRONG_TREND=3956, setup_compat:regime_WEAK_TREND=2705, execution:overextended=530, entry_quality=13
- **MOVER_AVWAP_SCALP** (total=2427): execution:overextended=1682, execution:trigger_not_confirmed=612, entry_quality=133
- **MOVER_TREND_PULLBACK** (total=15598): execution:trigger_not_confirmed=9222, execution:overextended=5813, entry_quality=563
- **QUIET_COMPRESSION_BREAK** (total=31): execution:trigger_not_confirmed=31
- **RANGE_FADE** (total=3452): setup_compat:regime_WEAK_TREND=1602, setup_compat:regime_STRONG_TREND=1134, setup_compat:regime_VOLATILE_UNSUITABLE=558, execution:overextended=158
- **TREND_PULLBACK_EMA** (total=3061): setup_compat:regime_CLEAN_RANGE=1850, setup_compat:regime_DIRTY_RANGE=1119, setup_compat:regime_VOLATILE_UNSUITABLE=74, entry_quality=18
- **VOLUME_SURGE_BREAKOUT** (total=5): execution:overextended=5
- **WHALE_MOMENTUM** (total=788): execution:trigger_not_confirmed=788

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 298942 | 49.4% |
| TRENDING_DOWN | 109705 | 18.1% |
| QUIET | 98838 | 16.3% |
| TRENDING_UP | 68622 | 11.3% |
| VOLATILE | 29160 | 4.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **57**
- Average confidence gap to threshold: **19.09** (samples=57) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TUSDT=8, INJUSDT=8, AAVEUSDT=7, BCHUSDT=7, BNBUSDT=7, BTCUSDT=6, TRXUSDT=6, BTWUSDT=5, TAOUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 6 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 160 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 3 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 60 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 115 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 3 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 7 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 9 |
| MEAN_REVERT | filtered | min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 17 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 335 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 29 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 244 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 967 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 21 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1172 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 1 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 7 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 79 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 20 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 2 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | min_confidence | 74 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 75.15 | 65.00 | -10.15 | 20.18 | 17.25 | 20.00 | 4.75 | 4.67 |
| DIVERGENCE_CONTINUATION | filtered | 160 | 50.85 | 62.88 | 12.03 | 20.54 | 19.74 | 19.24 | 1.61 | 20.98 |
| DIVERGENCE_CONTINUATION | kept | 3 | 67.87 | 65.00 | -2.87 | 21.17 | 20.00 | 17.57 | 3.33 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 60 | 51.30 | 63.60 | 12.30 | 21.87 | 19.80 | 20.00 | 3.05 | 2.78 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.92 | 65.00 | -1.92 | 21.76 | 19.46 | 20.00 | 2.70 | 3.84 |
| FUNDING_EXTREME_SIGNAL | filtered | 115 | 48.05 | 63.68 | 15.63 | 20.03 | 14.48 | 16.93 | 3.05 | 11.19 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 65.17 | 65.00 | -0.17 | 19.10 | 13.80 | 17.13 | 3.00 | 4.93 |
| LIQUIDATION_REVERSAL | filtered | 7 | 32.20 | 10.00 | -22.20 | 20.29 | 8.00 | 20.00 | 4.00 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 56.11 | 64.38 | 8.27 | 20.67 | 19.45 | 17.28 | 2.49 | 11.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 69.71 | 65.00 | -4.71 | 21.26 | 17.28 | 17.50 | 2.89 | 2.39 |
| MEAN_REVERT | filtered | 2 | 61.50 | 65.00 | 3.50 | 21.20 | 14.00 | 16.80 | 0.00 | 7.20 |
| MEAN_REVERT | kept | 17 | 71.57 | 65.00 | -6.57 | 18.86 | 19.08 | 15.95 | 0.00 | 0.42 |
| MOVER_AVWAP_SCALP | filtered | 364 | 60.89 | 59.66 | -1.23 | 19.95 | 15.13 | 15.80 | 3.99 | 10.16 |
| MOVER_AVWAP_SCALP | kept | 244 | 79.82 | 65.00 | -14.82 | 19.85 | 15.14 | 15.80 | 4.15 | 3.09 |
| MOVER_TREND_PULLBACK | filtered | 988 | 55.30 | 63.43 | 8.13 | 20.19 | 19.11 | 15.80 | 4.07 | 16.23 |
| MOVER_TREND_PULLBACK | kept | 1172 | 76.56 | 65.00 | -11.56 | 19.66 | 18.55 | 15.80 | 4.32 | 1.65 |
| QUIET_COMPRESSION_BREAK | filtered | 28 | 46.65 | 64.86 | 18.21 | 21.70 | 19.92 | 20.00 | 0.00 | 9.64 |
| QUIET_COMPRESSION_BREAK | kept | 7 | 71.54 | 65.00 | -6.54 | 22.66 | 19.10 | 20.00 | 0.00 | 1.83 |
| TREND_PULLBACK_EMA | filtered | 79 | 58.55 | 63.84 | 5.29 | 22.58 | 19.68 | 17.02 | 4.84 | 19.09 |
| TREND_PULLBACK_EMA | kept | 20 | 68.57 | 65.00 | -3.57 | 20.22 | 19.91 | 16.80 | 5.17 | 1.03 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 47.70 | 61.00 | 13.30 | 18.40 | 14.00 | 20.00 | 3.00 | 9.00 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 70.70 | 65.00 | -5.70 | 22.10 | 16.67 | 20.00 | 4.50 | 2.00 |
| WHALE_MOMENTUM | filtered | 80 | 32.71 | 64.40 | 31.69 | 22.92 | 14.00 | 17.00 | 0.00 | 21.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 75.15 | 17.17 | 15.33 | 14.00 | 14.00 | 5.00 | 9.57 | 4.75 |
| DIVERGENCE_CONTINUATION | filtered | 160 | 50.85 | 22.95 | 14.88 | 4.88 | 13.96 | 5.87 | 8.48 | 1.61 |
| DIVERGENCE_CONTINUATION | kept | 3 | 67.87 | 19.67 | 14.67 | 5.00 | 12.67 | 5.00 | 8.53 | 3.33 |
| FAILED_AUCTION_RECLAIM | filtered | 60 | 51.30 | 18.63 | 18.00 | 8.25 | 12.97 | 5.06 | 3.67 | 3.05 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.92 | 20.20 | 15.60 | 8.40 | 14.20 | 6.60 | 6.06 | 2.70 |
| FUNDING_EXTREME_SIGNAL | filtered | 115 | 48.05 | 21.73 | 12.85 | 4.49 | 11.97 | 7.37 | 6.26 | 3.05 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 65.17 | 22.33 | 15.33 | 4.00 | 10.00 | 8.67 | 6.77 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 7 | 32.20 | 25.00 | 8.00 | 12.00 | 8.00 | 2.50 | 7.70 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 56.11 | 22.95 | 14.97 | 3.88 | 11.54 | 5.00 | 6.38 | 2.49 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 69.71 | 23.89 | 14.00 | 5.00 | 12.33 | 7.00 | 6.99 | 2.89 |
| MEAN_REVERT | filtered | 2 | 61.50 | 17.00 | 14.00 | 12.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 17 | 71.57 | 23.12 | 14.00 | 9.18 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 364 | 60.89 | 18.25 | 18.05 | 11.93 | 13.78 | 6.02 | 6.22 | 3.99 |
| MOVER_AVWAP_SCALP | kept | 244 | 79.82 | 20.21 | 18.06 | 13.33 | 13.91 | 6.76 | 8.69 | 4.15 |
| MOVER_TREND_PULLBACK | filtered | 988 | 55.30 | 18.53 | 18.09 | 7.58 | 12.85 | 6.13 | 8.95 | 4.07 |
| MOVER_TREND_PULLBACK | kept | 1172 | 76.56 | 19.46 | 18.07 | 8.02 | 13.29 | 6.71 | 8.76 | 4.32 |
| QUIET_COMPRESSION_BREAK | filtered | 28 | 46.65 | 19.29 | 17.86 | 10.61 | 14.00 | 5.34 | 4.20 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 7 | 71.54 | 17.00 | 17.43 | 10.71 | 14.86 | 6.64 | 7.16 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 79 | 58.55 | 18.62 | 18.00 | 7.50 | 14.42 | 6.51 | 8.89 | 4.84 |
| TREND_PULLBACK_EMA | kept | 20 | 68.57 | 10.30 | 18.00 | 7.80 | 14.60 | 8.22 | 8.36 | 5.17 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 47.70 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 3.70 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 70.70 | 22.33 | 15.33 | 13.00 | 12.00 | 5.00 | 5.53 | 4.50 |
| WHALE_MOMENTUM | filtered | 80 | 32.71 | 24.50 | 17.25 | 4.42 | 13.46 | 7.55 | 2.03 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 75.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.67 | 0.00 | 0.00 | **1.67** |
| DIVERGENCE_CONTINUATION | filtered | 160 | 50.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 3 | 67.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 60 | 51.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | **0.80** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.92 | 0.00 | 0.00 | 0.00 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | **1.44** |
| FUNDING_EXTREME_SIGNAL | filtered | 115 | 48.05 | 0.00 | 0.00 | 0.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.85** |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 65.17 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| LIQUIDATION_REVERSAL | filtered | 7 | 32.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 56.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | **0.83** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 69.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 2 | 61.50 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| MEAN_REVERT | kept | 17 | 71.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | **0.42** |
| MOVER_AVWAP_SCALP | filtered | 364 | 60.89 | 0.25 | 0.00 | 0.11 | 0.00 | 0.89 | 0.77 | 0.00 | 1.37 | **3.39** |
| MOVER_AVWAP_SCALP | kept | 244 | 79.82 | 0.53 | 0.00 | 0.10 | 0.00 | 0.18 | 0.92 | 0.00 | 0.10 | **1.83** |
| MOVER_TREND_PULLBACK | filtered | 988 | 55.30 | 0.00 | 0.00 | 1.48 | 0.00 | 0.31 | 0.05 | 0.00 | 0.00 | **1.84** |
| MOVER_TREND_PULLBACK | kept | 1172 | 76.56 | 0.00 | 0.00 | 0.24 | 0.00 | 0.19 | 0.05 | 0.00 | 0.00 | **0.48** |
| QUIET_COMPRESSION_BREAK | filtered | 28 | 46.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.93 | **7.93** |
| QUIET_COMPRESSION_BREAK | kept | 7 | 71.54 | 0.00 | 0.00 | 0.00 | 0.00 | 0.61 | 0.00 | 0.00 | 0.00 | **0.61** |
| TREND_PULLBACK_EMA | filtered | 79 | 58.55 | 0.00 | 0.00 | 1.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.11** |
| TREND_PULLBACK_EMA | kept | 20 | 68.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 47.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 70.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 80 | 32.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **97867 held of 242155 seen** across 21 strategies; 2229 cells past the sample floor; **981 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 36037 | 562/35475/0 | 44% | -0.13 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.25R) | ASIA/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.13R) |
| MOVER_AVWAP_SCALP | 12336 | 152/12184/0 | 40% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 7337 | 85/7252/0 | 41% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 5905 | 28/5877/0 | 51% | +0.01 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5325 | 0/0/5325 | 43% | -0.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.56R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL (-0.91R) |
| TREND_PULLBACK_EMA | 4843 | 24/4819/0 | 45% | -0.14 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4360 | 0/0/4360 | 38% | -0.06 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | NY/QUIET/COMPRESSED/BTC_FALLING (-0.98R) |
| QUIET_COMPRESSION_BREAK | 4241 | 239/4002/0 | 44% | -0.13 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.72R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 3974 | 0/0/3974 | 34% | -0.40 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-0.97R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2624 | 44/2580/0 | 37% | -0.34 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 1847 | 20/1827/0 | 49% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1621 | 2/1619/0 | 36% | -0.35 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1400 | 0/1400/0 | 45% | +0.08 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 928 | 10/918/0 | 46% | -0.26 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 684 | 0/0/684 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.47R) |
| RANGE_FADE | 424 | 0/424/0 | 42% | -0.23 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 344 | 25/319/0 | 41% | -0.15 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 210 | 0/210/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 56 | 6/50/0 | 39% | -0.13 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 132 | 30% / -0.51R | 132 | 48% / -0.17R | +0.34 | **ATR** |
| TREND_PULLBACK_EMA | 397 | 45% / -0.21R | 397 | 54% / -0.04R | +0.17 | **ATR** |
| MOVER_AVWAP_SCALP | 949 | 44% / -0.19R | 949 | 50% / -0.09R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 111 | 50% / -0.26R | 111 | 51% / -0.16R | +0.10 | **ATR** |
| RANGE_FADE | 22 | 45% / +0.07R | 22 | 45% / -0.02R | -0.09 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 650 | 43% / -0.18R | 650 | 45% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5433 | 51% / -0.09R | 5433 | 55% / -0.00R | +0.08 | **ATR** |
| BREAKDOWN_SHORT | 28 | 32% / -0.16R | 28 | 36% / -0.11R | +0.05 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 502 | 51% / -0.18R | 502 | 55% / -0.15R | +0.04 | **ATR** |
| DIVERGENCE_CONTINUATION | 573 | 52% / -0.05R | 573 | 57% / -0.03R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 713 | 45% / -0.15R | 713 | 45% / -0.16R | -0.01 | **FIXED** |
| MEAN_REVERT | 134 | 53% / -0.08R | 134 | 51% / -0.08R | -0.00 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 88 | 42% / -0.04R | 88 | 50% / -0.04R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7998 | 30% | -0.16R | 307 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 949 | 47% | -0.08R | 189 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 55 | 55% | -0.03R | 46 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 684 | 37% / -0.10R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7047 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1238 | 34% / -0.07R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 514 | 36% / -0.10R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 648 | 41% / +0.04R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 528 | 38% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 505 | 45% / -0.09R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 116 | 31% / -0.26R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 171 | 31% / -0.57R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 108 | 53% / +0.04R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 50 | 36% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 19 | 42% / +0.20R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 112 | 35% / -0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 26 | 12% / -0.61R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 18 | 39% / -0.13R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **5** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 32/67 unfetchable (48%); top cause: gap or duplicate bar in the 15m window; symbols: ASTRUSDT, AVAXUSDT, BRUSDT, BTWUSDT, CAPUSDT +10 more (streak 99/6) (sustained 99 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×207]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 47/6) (sustained 47 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.71R (bound 0.3) (streak 202/6) (sustained 202 cycles)
- **ALERT** `tuned_variants` — 203 non-stamps — atr_arm_uncomputable=203 (seen=2323 stamped=231 skipped=1889) (streak 200/6) (sustained 200 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 202/3) (sustained 202 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 46493099 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 202/3) | 202 |
| ai_governor_live_arms | ok | 27 arms current, none stalled; covering 376/376 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 52 arms current, none stalled; covering 1069/1069 signals (100%) | 0 |
| auto_dispatch | ok | 51 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:off=51, mode:paper=51. No user is on live. | 0 |
| btc_reference | ok | BTC ref 75687.10 | 0 |
| candle_coverage | ok | 91/91 symbols with ≥20 15m candles, 91/91 updated within 45m [fresh=91; 75 Tier-1 futures + 16 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 802 dup bars, 0 undedupable; ws 0 out-of-order, 247 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +63 / upstream +25 | 0 |
| dark_atr_trail_arms | violating | 1 dark ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 148 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/3) | 1 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 3 of 122 open dark rows are not being advanced (worst: TUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 12/120) | 12 |
| dark_sar_arms | violating | 1 dark SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 83 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/3) | 1 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 7415261 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.71R (bound 0.3) (streak 202/6) | 202 |
| emission_controller | ok | last cycle 990s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×207]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 47/6) | 47 |
| entry_quality_effective | ok | 1856 evaluated, 604 suppressed, 528 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| footprint_bars | ok | 4866 sealed bars over 41 symbols; 1265 incomplete, 15 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +13 / upstream +216 | 0 |
| indicator_cache_key | ok | 59776 frozen value(s) avoided; 314913 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.17R over n=1827 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +21 / upstream +216 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 16 held, 16 with scan counts, 14 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3075 rows held, 1430955 evicted (sampled: execution:trigger_not_confirmed 400/522695, execution:overextended 400/470615, setup_compat:regime_STRONG_TREND 400/216084) | 0 |
| price_action_lane | ok | 489694 evaluated, 551 emitted; layer1 551 stamped / 0 blind; cooldown=71150, delta_opposed=43006, no_footprint=192452, no_opposing_target=1248, no_sweep=143565, rr_below_floor=37722 | 0 |
| promoted_pair_integrity | ok | 16/16 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.23R over n=424 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +216 but output +0 (streak 4/72) | 4 |
| sar_alignment_crosscheck | ok | 146/6536 disagreed (2.2%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +216 | 0 |
| sar_hold_arm | ok | 1790 held arms settled, 211 unscored, 51 still walking (45 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 32/67 unfetchable (48%); top cause: gap or duplicate bar in the 15m window; symbols: ASTRUSDT, AVAXUSDT, BRUSDT, BTWUSDT, CAPUSDT +10 more (streak 99/6) | 99 |
| sar_live_arms | ok | 52 arms current, none stalled; covering 1068/1068 signals (100%) | 0 |
| sar_refresh_budget | ok | 4 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 467 records await one (35 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 25.31s, worst 73.84s over 5505 lifetime cycles; lifetime 3 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.29s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 235373 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (3.06s to run, worst 38.69s), 155 overrun(s) of 4091 cycles, TTL 900s; slowest signals=2.88s, agents=1.69s, activity=0.46s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=3, gate reads=0, withheld=3) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +2 / upstream +216 | 0 |
| structural_snap | ok | 5140/5140 measured, 19 blind, 0 levels moved (refusals: redetect_cooldown=270) | 0 |
| structural_veto_lane | ok | 512 stamped; 0 with no readable level book, 5 with clear air ahead, 434 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +216 / upstream +25 | 0 |
| tuned_variants | violating | 203 non-stamps — atr_arm_uncomputable=203 (seen=2323 stamped=231 skipped=1889) (streak 200/6) | 200 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2899669`
- `Path funnel` emissions: `69`
- `Regime distribution` emissions: `69`
- `QUIET_SCALP_BLOCK` events: `57`
- `confidence_gate` events: `3452`
- `free_channel_post` events: `11`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_mover | 1 | 4969 | 4969 | 4969 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **11**

| Source | Count |
|---|---:|
| signal_close | 11 |

- By severity: HIGH=11

## Dependency readiness
- cvd: presence[absent=483, present=477283] state[empty=483, populated=477283] buckets[few=4, many=477262, none=483, some=17] sources[none] quality[none]
- funding_rate: presence[absent=63863, present=413903] state[empty=63863, populated=413903] buckets[few=413903, none=63863] sources[none] quality[none]
- liquidation_clusters: presence[absent=274807, present=202959] state[empty=274807, populated=202959] buckets[few=160130, none=274807, some=42829] sources[none] quality[none]
- oi_snapshot: presence[absent=61494, present=416272] state[empty=61494, populated=416272] buckets[few=207, many=414798, none=61494, some=1267] sources[none] quality[none]
- order_book: presence[absent=138657, present=339109] state[populated=339109, unavailable=138657] buckets[few=339109, none=138657] sources[book_ticker=339109, unavailable=138657] quality[none=138657, top_of_book_only=339109]
- orderblocks: presence[absent=477766] state[empty=477766] buckets[none=477766] sources[measured_dark=477766] quality[none]
- recent_ticks: presence[present=477766] state[populated=477766] buckets[many=477766] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.7007755041122437` sec
- Median create→first breach: `3169.2462334632874` sec
- Median create→terminal: `3169.4340879917145` sec
- Median first breach→terminal: `0.2686864137649536` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 3.1}, "under_180s": {"count": 2, "pct": 3.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 1.6}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.8648344509951099 | 1.2205276823415245 | 0.7085742204027409 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.0993060180154806 | 1.2981311927756167 | 0.8468373798683511 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 1.2829386541082008 | 1.5735750544328146 | 0.8156162901901944 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.8781849666833885 | 2.0557455257717456 | 0.9169031053495167 | 0 | 1 |
| MOVER_AVWAP_SCALP | 10 | 10 | 2.1205915188990723 | 2.6304809425085853 | 0.8278618750909572 | 2 | 8 |
| MOVER_TREND_PULLBACK | 41 | 41 | 4.367094393743038 | 3.0 | 1.4556981312476793 | 37 | 4 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.2672703926188311 | 1.3759965797726357 | 0.8941390643269154 | 0 | 5 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 15473.714116811752 | 15473.714159965515 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0993 | 9047.736060857773 | 9047.736095905304 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.3052 | 4070.656046628952 | 4070.8083395957947 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.3286 | 1134.2734409570694 | 1134.4240609407425 |
| MOVER_AVWAP_SCALP | 10 | 10 | 20.0 | 40.0 | 20.0 | 0.0 | -0.0689 | 8785.615799546242 | 8785.615834116936 |
| MOVER_TREND_PULLBACK | 41 | 41 | 39.0 | 39.0 | 39.0 | 0.0 | 1.6322 | 2571.645031929016 | 2571.92121386528 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 42.9 | 28.6 | 42.9 | 0.0 | 0.7186 | 34551.87305998802 | 34551.87312412262 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1458 | 0 | 1458 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3796 | 7 | 3647 | 0.0 | 0.0 | None | None | 149 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-21`
- Gating Δ: `69764`
- No-generation Δ: `737609`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.6629, "current_avg_pnl": -0.0689, "current_win_rate": 20.0, "previous_avg_pnl": 0.594, "previous_win_rate": 50.0, "win_rate_delta": -30.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.6548, "current_avg_pnl": 1.6322, "current_win_rate": 39.0, "previous_avg_pnl": -0.0226, "previous_win_rate": 27.6, "win_rate_delta": 11.4}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.1428, "current_avg_pnl": 0.7186, "current_win_rate": 42.9, "previous_avg_pnl": -0.4242, "previous_win_rate": 22.2, "win_rate_delta": 20.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -64, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -9358.21, "median_terminal_delta_sec": -9360.76, "sl_rate_delta": -50.0, "win_rate_delta": -50.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": 68, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
