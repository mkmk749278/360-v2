# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `9` sec (warning=False)
- Latest performance record age: `1315` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 79 | 79 | 79 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 14025 | 14025 | 11521 | 29 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 82154 | 82156 | 31 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 69905 | 69905 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 69483 | 67569 | 2317 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 69945 | 68482 | 1521 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 70298 | 70191 | 132 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 59349 | 59361 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 70012 | 70032 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 70046 | 67730 | 3507 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 87690 | 93372 | 1129 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 82187 | 74731 | 12902 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 69863 | 69863 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 69913 | 69928 | 11 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 69460 | 69310 | 171 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 71245 | 70098 | 1628 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 68996 | 69223 | 200 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 58361 | 53569 | 5011 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 58582 | 58301 | 346 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 82114 | 82122 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 59364 | 59377 | 18 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5930 | 5930 | 5258 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 505 | 505 | 229 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 14 | 14 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 26407 | 26407 | 24953 | 14 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 6 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11070 | 11070 | 6610 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3231 | 3231 | 1319 | 92 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 43686 | 43686 | 27407 | 409 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 78 | 78 | 77 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 976 | 976 | 754 | 5 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 5324 | 5324 | 4126 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1101 | 1101 | 744 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2872 | 2872 | 2423 | 36 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 234 | 234 | 144 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 4171 | 4171 | 1100 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=82156): breakout_not_found=48814, basic_filters_failed=19072, move_not_fresh=9503, breakout_stale=2881, retest_proximity_failed=1625, volume_spike_missing=242, move_exhausted=17, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=69905): cls_disabled_merged_into_lsr=69905
- **EVAL::DIVERGENCE_CONTINUATION** (total=67569): cvd_divergence_failed=31190, h1_trend_not_aligned=14022, basic_filters_failed=12717, ema_alignment_reject=8067, retest_proximity_failed=1291, missing_fvg_or_orderblock=280, cvd_insufficient=2
- **EVAL::FAILED_AUCTION_RECLAIM** (total=68482): auction_not_detected=46032, basic_filters_failed=12352, reclaim_hold_failed=4623, regime_blocked=3027, tail_too_small=2404, rsi_reject=44
- **EVAL::FUNDING_EXTREME** (total=70191): funding_not_extreme=55911, basic_filters_failed=12997, ema_alignment_reject=729, rsi_reject=331, cvd_divergence_failed=117, momentum_reject=84, missing_fvg_or_orderblock=20, missing_funding_rate=2
- **EVAL::LIQUIDATION_REVERSAL** (total=59361): cascade_threshold_not_met=45813, basic_filters_failed=12791, cvd_divergence_failed=387, rsi_reject=344, missing_fvg_or_orderblock=26
- **EVAL::MA_CROSS_TREND_SHIFT** (total=70032): no_ma_cross=56189, basic_filters_failed=12728, ma_cross_cooldown=768, ma_cross_htf_misaligned=347
- **EVAL::MEAN_REVERT** (total=67730): no_extension=55339, basic_filters_failed=12391
- **EVAL::MOVER_AVWAP_SCALP** (total=93372): no_avwap_tag=35171, no_mover_leg=25278, basic_filters_failed=19282, avwap_slope_against=9648, avwap_reclaim_no_volume=2436, no_avwap_reclaim=1537, anchor_too_recent=20
- **EVAL::MOVER_TREND_PULLBACK** (total=74731): mover_run_too_small=32997, no_reclaim=19299, basic_filters_failed=19189, no_pullback_tag=3246
- **EVAL::OPENING_RANGE_BREAKOUT** (total=69863): feature_disabled=69863
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=69928): regime_blocked=40853, breakout_not_found=23060, basic_filters_failed=4944, adx_reject=1023, ema_alignment_reject=48
- **EVAL::QUIET_COMPRESSION_BREAK** (total=69310): regime_blocked=31930, compression_not_detected=26905, basic_filters_failed=7400, breakout_not_detected=2815, volume_confirmation_failed=250, missing_fvg_or_orderblock=9, rsi_reject=1
- **EVAL::RANGE_FADE** (total=70098): no_range_edge=57699, basic_filters_failed=12399
- **EVAL::SR_FLIP_RETEST** (total=69223): flip_close_not_confirmed=46715, basic_filters_failed=12335, regime_blocked=3006, long_break_volume_thin=2359, retest_out_of_zone=2230, h1_break_not_confirmed=1345, reclaim_hold_failed=711, ema_alignment_reject=248, wick_quality_failed=126, whipsaw_flip=70, long_acceptance_not_held=67, missing_fvg_or_orderblock=11
- **EVAL::STANDARD** (total=53569): momentum_reject=14449, adx_reject=9766, basic_filters_failed=9523, ema_alignment_reject=7312, sweeps_not_detected=6093, macd_reject=5486, htf_poi_unanchored=854, invalid_sl_geometry=44, rsi_reject=28, mtf_reject=14
- **EVAL::TREND_PULLBACK** (total=58301): h1_trend_not_aligned=14893, h1_pullback_not_confirmed=14173, ema_alignment_reject=12213, basic_filters_failed=5546, ema_not_tested_prev=4406, no_ema_reclaim_close=2892, body_conviction_fail=1621, rsi_reject=1448, prev_already_below_emas=413, no_prev_low_break=362, prev_already_above_emas=113, momentum_flat=105, no_prev_high_break=53, ema21_not_tagged=51, momentum_reject=7, missing_fvg_or_orderblock=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=82122): breakout_not_found=44079, basic_filters_failed=19072, move_not_fresh=13529, breakout_stale=3716, retest_proximity_failed=1456, volume_spike_missing=259, missing_fvg_or_orderblock=9, move_exhausted=2
- **EVAL::WHALE_MOMENTUM** (total=59377): momentum_reject=44353, recent_ticks_insufficient=10403, basic_filters_failed=4621

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=458): setup_compat:regime_VOLATILE_UNSUITABLE=426, setup_compat:regime_BREAKOUT_EXPANSION=29, execution:overextended=3
- **FAILED_AUCTION_RECLAIM** (total=1902): setup_compat:regime_STRONG_TREND=936, execution:overextended=772, context_floor=155, setup_compat:regime_VOLATILE_UNSUITABLE=39
- **FUNDING_EXTREME_SIGNAL** (total=384): execution:trigger_not_confirmed=367, context_floor=17
- **LIQUIDATION_REVERSAL** (total=14): execution:trigger_not_confirmed=14
- **LIQUIDITY_SWEEP_REVERSAL** (total=7922): setup_compat:regime_STRONG_TREND=3306, execution:trigger_not_confirmed=2659, execution:overextended=1957
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_DIRTY_RANGE=3, setup_compat:regime_CLEAN_RANGE=1, execution:trigger_not_confirmed=1, execution:overextended=1
- **MEAN_REVERT** (total=8205): setup_compat:regime_STRONG_TREND=4135, setup_compat:regime_WEAK_TREND=2982, execution:overextended=1088
- **MOVER_AVWAP_SCALP** (total=2073): execution:overextended=1798, entry_quality=200, execution:trigger_not_confirmed=75
- **MOVER_TREND_PULLBACK** (total=21827): execution:trigger_not_confirmed=12642, execution:overextended=6891, entry_quality=2294
- **RANGE_FADE** (total=3299): setup_compat:regime_STRONG_TREND=2057, setup_compat:regime_WEAK_TREND=836, execution:overextended=261, setup_compat:regime_VOLATILE_UNSUITABLE=128, context_edge=14, setup_compat:regime_BREAKOUT_EXPANSION=3
- **TREND_PULLBACK_EMA** (total=2579): setup_compat:regime_CLEAN_RANGE=1784, setup_compat:regime_DIRTY_RANGE=625, entry_quality=119, setup_compat:regime_VOLATILE_UNSUITABLE=51
- **VOLUME_SURGE_BREAKOUT** (total=73): execution:overextended=73
- **WHALE_MOMENTUM** (total=3619): execution:trigger_not_confirmed=3617, context_floor=2

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 189719 | 36.9% |
| TRENDING_UP | 116775 | 22.7% |
| QUIET | 94965 | 18.5% |
| TRENDING_DOWN | 93072 | 18.1% |
| VOLATILE | 19353 | 3.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **208**
- Average confidence gap to threshold: **12.37** (samples=208) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=73, ETHUSDT=26, CRVUSDT=23, LTCUSDT=12, ONUSDT=9, XLMUSDT=7, WLDUSDT=6, ZECUSDT=6, LINKUSDT=5, HBARUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 302 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 9 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 228 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 195 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 35 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 14 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 291 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 115 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 57 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 492 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 667 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1759 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 52 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5569 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 109 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 41 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 35 |
| SR_FLIP_RETEST | filtered | min_confidence | 77 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 12 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 29 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 74 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 137 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 85 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 73 |
| WHALE_MOMENTUM | filtered | min_confidence | 40 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 13 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 311 | 56.48 | 64.81 | 8.33 | 20.08 | 19.82 | 18.75 | 1.97 | 12.58 |
| DIVERGENCE_CONTINUATION | kept | 228 | 70.43 | 65.00 | -5.43 | 20.58 | 19.44 | 18.57 | 1.91 | -0.83 |
| FAILED_AUCTION_RECLAIM | filtered | 199 | 49.81 | 64.64 | 14.83 | 21.25 | 18.69 | 20.00 | 2.26 | 4.99 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.00 | 65.00 | -1.00 | 21.10 | 20.00 | 20.00 | 2.50 | 1.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 35 | 41.16 | 65.00 | 23.84 | 19.18 | 15.73 | 17.32 | 3.83 | 12.91 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 79.30 | 65.00 | -14.30 | 15.70 | 14.00 | 17.00 | 3.00 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 14 | 70.30 | 10.00 | -60.30 | 20.97 | 8.90 | 15.10 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 308 | 50.17 | 64.91 | 14.74 | 20.42 | 18.23 | 18.35 | 0.95 | 5.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 115 | 70.26 | 65.00 | -5.26 | 18.82 | 18.61 | 18.31 | 1.20 | 0.08 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 61.00 | 65.00 | 4.00 | 21.20 | 19.90 | 15.80 | 0.00 | 6.00 |
| MEAN_REVERT | filtered | 57 | 56.93 | 65.00 | 8.07 | 19.63 | 14.00 | 17.93 | 0.00 | 11.33 |
| MEAN_REVERT | kept | 1 | 69.50 | 65.00 | -4.50 | 20.90 | 14.00 | 20.00 | 0.00 | 7.20 |
| MOVER_AVWAP_SCALP | filtered | 492 | 55.72 | 64.15 | 8.43 | 20.73 | 16.96 | 15.80 | 4.24 | 10.51 |
| MOVER_AVWAP_SCALP | kept | 667 | 81.99 | 65.00 | -16.99 | 20.22 | 15.02 | 15.80 | 4.27 | 2.30 |
| MOVER_TREND_PULLBACK | filtered | 1811 | 57.12 | 63.92 | 6.80 | 20.13 | 18.39 | 15.80 | 3.85 | 15.31 |
| MOVER_TREND_PULLBACK | kept | 5569 | 77.25 | 65.00 | -12.25 | 20.31 | 18.30 | 15.80 | 4.36 | 1.71 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.20 | 65.00 | -19.20 | 21.20 | 20.00 | 19.10 | 4.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 150 | 49.45 | 64.44 | 14.99 | 22.26 | 18.82 | 20.00 | 0.00 | 10.94 |
| QUIET_COMPRESSION_BREAK | kept | 35 | 80.80 | 65.00 | -15.80 | 22.77 | 19.88 | 20.00 | 0.00 | -0.12 |
| SR_FLIP_RETEST | filtered | 89 | 53.34 | 63.17 | 9.83 | 20.59 | 20.00 | 17.19 | 1.84 | 16.85 |
| SR_FLIP_RETEST | kept | 29 | 68.62 | 65.00 | -3.62 | 21.31 | 20.00 | 19.25 | 1.24 | 2.72 |
| TREND_PULLBACK_EMA | filtered | 74 | 54.92 | 64.66 | 9.74 | 20.88 | 19.86 | 18.83 | 4.91 | 14.55 |
| TREND_PULLBACK_EMA | kept | 137 | 80.10 | 65.00 | -15.10 | 20.85 | 19.81 | 18.19 | 5.05 | -0.16 |
| VOLUME_SURGE_BREAKOUT | filtered | 85 | 47.51 | 63.06 | 15.55 | 19.20 | 17.21 | 20.00 | 4.77 | 15.18 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 77.50 | 65.00 | -12.50 | 20.70 | 15.80 | 20.00 | 4.50 | 3.00 |
| WHALE_MOMENTUM | filtered | 113 | 54.62 | 64.72 | 10.10 | 23.30 | 14.82 | 17.00 | 0.00 | 13.71 |
| WHALE_MOMENTUM | kept | 13 | 64.35 | 65.00 | 0.65 | 23.96 | 18.57 | 17.00 | 0.00 | 10.38 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 311 | 56.48 | 21.94 | 15.91 | 4.85 | 11.03 | 4.90 | 8.47 | 1.97 |
| DIVERGENCE_CONTINUATION | kept | 228 | 70.43 | 22.12 | 15.42 | 5.62 | 12.10 | 5.07 | 8.84 | 1.91 |
| FAILED_AUCTION_RECLAIM | filtered | 199 | 49.81 | 20.38 | 15.35 | 7.36 | 12.98 | 6.53 | 4.94 | 2.26 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.00 | 25.00 | 18.00 | 3.00 | 17.00 | 8.50 | 8.00 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 35 | 41.16 | 23.86 | 12.34 | 5.40 | 13.66 | 6.57 | 3.41 | 3.83 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 79.30 | 25.00 | 20.00 | 3.00 | 9.00 | 10.00 | 9.30 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 14 | 70.30 | 25.00 | 8.00 | 12.00 | 8.00 | 8.00 | 5.30 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 308 | 50.17 | 23.45 | 16.26 | 5.84 | 12.41 | 5.18 | 5.27 | 0.95 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 115 | 70.26 | 22.97 | 15.15 | 4.67 | 12.96 | 5.47 | 7.93 | 1.20 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 61.00 | 23.00 | 14.00 | 3.00 | 14.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 57 | 56.93 | 21.07 | 14.00 | 9.21 | 12.91 | 5.00 | 7.38 | 0.00 |
| MEAN_REVERT | kept | 1 | 69.50 | 25.00 | 14.00 | 12.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 492 | 55.72 | 17.96 | 18.02 | 10.70 | 14.47 | 6.07 | 5.93 | 4.24 |
| MOVER_AVWAP_SCALP | kept | 667 | 81.99 | 19.10 | 18.08 | 13.24 | 13.81 | 6.83 | 9.11 | 4.27 |
| MOVER_TREND_PULLBACK | filtered | 1811 | 57.12 | 17.69 | 18.09 | 7.70 | 12.45 | 6.59 | 8.69 | 3.85 |
| MOVER_TREND_PULLBACK | kept | 5569 | 77.25 | 19.79 | 18.02 | 7.94 | 12.86 | 6.81 | 9.28 | 4.36 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.20 | 17.00 | 18.00 | 15.00 | 17.00 | 5.00 | 7.70 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 150 | 49.45 | 19.35 | 15.09 | 12.32 | 14.06 | 7.96 | 4.23 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 35 | 80.80 | 22.49 | 17.89 | 11.83 | 14.09 | 5.53 | 9.04 | 0.00 |
| SR_FLIP_RETEST | filtered | 89 | 53.34 | 21.11 | 16.65 | 6.74 | 14.06 | 5.87 | 7.13 | 1.84 |
| SR_FLIP_RETEST | kept | 29 | 68.62 | 18.10 | 17.31 | 3.62 | 16.55 | 5.00 | 9.62 | 1.24 |
| TREND_PULLBACK_EMA | filtered | 74 | 54.92 | 12.54 | 18.00 | 7.50 | 14.00 | 8.57 | 8.82 | 4.91 |
| TREND_PULLBACK_EMA | kept | 137 | 80.10 | 18.55 | 18.00 | 7.83 | 15.00 | 6.47 | 9.58 | 5.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 85 | 47.51 | 20.11 | 16.45 | 12.00 | 13.36 | 4.76 | 6.24 | 4.77 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 77.50 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| WHALE_MOMENTUM | filtered | 113 | 54.62 | 20.70 | 11.54 | 7.96 | 13.15 | 6.78 | 8.18 | 0.00 |
| WHALE_MOMENTUM | kept | 13 | 64.35 | 24.23 | 18.00 | 3.92 | 12.85 | 5.73 | 10.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 311 | 56.48 | 0.00 | 0.00 | 0.69 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | **0.78** |
| DIVERGENCE_CONTINUATION | kept | 228 | 70.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.03 | 0.00 | 0.00 | **0.06** |
| FAILED_AUCTION_RECLAIM | filtered | 199 | 49.81 | 0.00 | 0.00 | 0.64 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | **1.15** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 35 | 41.16 | 0.00 | 0.00 | 2.33 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | **2.54** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 79.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 14 | 70.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 308 | 50.17 | 0.00 | 0.00 | 0.74 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | **1.22** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 115 | 70.26 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.08** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 61.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | 0.00 | 0.00 | **6.00** |
| MEAN_REVERT | filtered | 57 | 56.93 | 0.00 | 0.00 | 0.42 | 0.00 | 3.54 | 0.00 | 0.00 | 0.00 | **3.96** |
| MEAN_REVERT | kept | 1 | 69.50 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| MOVER_AVWAP_SCALP | filtered | 492 | 55.72 | 0.22 | 0.00 | 0.80 | 0.00 | 1.90 | 0.14 | 0.00 | 0.61 | **3.67** |
| MOVER_AVWAP_SCALP | kept | 667 | 81.99 | 0.62 | 0.00 | 0.08 | 0.00 | 0.65 | 0.25 | 0.00 | 0.08 | **1.68** |
| MOVER_TREND_PULLBACK | filtered | 1811 | 57.12 | 0.19 | 0.00 | 1.18 | 0.00 | 0.76 | 0.17 | 0.00 | 0.00 | **2.30** |
| MOVER_TREND_PULLBACK | kept | 5569 | 77.25 | 0.19 | 0.00 | 0.46 | 0.00 | 0.42 | 0.07 | 0.00 | 0.00 | **1.14** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 150 | 49.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | **7.00** |
| QUIET_COMPRESSION_BREAK | kept | 35 | 80.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 89 | 53.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.73 | 0.11 | 0.00 | 1.28 | **2.12** |
| SR_FLIP_RETEST | kept | 29 | 68.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 74 | 54.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.54 | 0.00 | 0.00 | **0.54** |
| TREND_PULLBACK_EMA | kept | 137 | 80.10 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.12** |
| VOLUME_SURGE_BREAKOUT | filtered | 85 | 47.51 | 0.00 | 0.00 | 2.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.42 | **2.79** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 77.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 113 | 54.62 | 0.00 | 0.00 | 0.00 | 0.00 | 3.44 | 0.00 | 0.00 | 0.00 | **3.44** |
| WHALE_MOMENTUM | kept | 13 | 64.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **136709 held of 453198 seen** across 21 strategies; 3119 cells past the sample floor; **1527 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 42847 | 600/42247/0 | 41% | -0.22 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.22R) |
| MOVER_AVWAP_SCALP | 17870 | 184/17686/0 | 40% | -0.24 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10725 | 122/10603/0 | 36% | -0.30 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 9342 | 62/9280/0 | 50% | -0.02 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.39R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.19R) |
| TREND_PULLBACK_EMA | 7827 | 34/7793/0 | 44% | -0.16 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| SHADOW_MEAN_REVERT | 6781 | 0/0/6781 | 43% | -0.09 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.95R) |
| LIQUIDITY_SWEEP_REVERSAL | 6497 | 79/6418/0 | 34% | -0.54 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | LONDON/MARKUP/EXPANDED/BTC_NEUTRAL (-1.66R) |
| SHADOW_RANGE_FADE | 6046 | 0/0/6046 | 38% | -0.06 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.53R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| QUIET_COMPRESSION_BREAK | 5607 | 349/5258/0 | 49% | -0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5373 | 0/0/5373 | 34% | -0.41 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3687 | 4/3683/0 | 44% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3143 | 35/3108/0 | 45% | -0.17 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 2643 | 2/2641/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2555 | 0/2555/0 | 36% | -0.21 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 2468 | 11/2457/0 | 47% | -0.22 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.27R) |
| RANGE_FADE | 1161 | 4/1157/0 | 44% | -0.32 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1154 | 0/0/1154 | 54% | -0.03 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.12R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 316 | 0/316/0 | 36% | -0.47 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 88 | 12/76/0 | 45% | -0.08 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.66R (n=42, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL` -1.66R (n=42, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 183 | 27% / -0.59R | 183 | 51% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 17 | 35% / -0.40R | 17 | 59% / -0.18R | +0.22 | **ATR** |
| TREND_PULLBACK_EMA | 640 | 42% / -0.25R | 640 | 55% / -0.04R | +0.21 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1068 | 44% / -0.33R | 1068 | 55% / -0.15R | +0.18 | **ATR** |
| MOVER_AVWAP_SCALP | 1466 | 43% / -0.20R | 1466 | 49% / -0.07R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 420 | 44% / -0.33R | 420 | 46% / -0.22R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1027 | 39% / -0.25R | 1027 | 42% / -0.15R | +0.11 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 127 | 36% / -0.19R | 127 | 46% / -0.08R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6746 | 48% / -0.13R | 6746 | 53% / -0.03R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 216 | 48% / -0.24R | 216 | 51% / -0.16R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 942 | 48% / -0.11R | 942 | 54% / -0.05R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 26 | 46% / -0.13R | 26 | 46% / -0.07R | +0.05 | **ATR** |
| RANGE_FADE | 51 | 37% / -0.31R | 51 | 39% / -0.33R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 901 | 46% / -0.14R | 901 | 46% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 229 | 52% / -0.05R | 229 | 51% / -0.05R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9674 | 29% | -0.26R | 310 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1466 | 46% | -0.08R | 212 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 79 | 48% | -0.09R | 51 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 857 | 37% / -0.17R | +0.90 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1081 | 38% / -0.27R | +0.74 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1919 | 34% / -0.11R | +0.73 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8706 | 35% / -0.18R | +0.35 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1058 | 38% / -0.05R | +0.23 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 156 | 35% / -0.34R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 877 | 34% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 834 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 188 | 29% / -0.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 245 | 31% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 190 | 54% / +0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 40 | 32% / -0.12R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 219 | 32% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 42 | 26% / -0.45R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 23 | 48% / +0.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **6** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×680]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 48/6) (sustained 48 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, profile_reject=2. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) (sustained 6 cycles)
- **ALERT** `dark_resolution` — 6 of 130 open dark rows are not being advanced (worst: BATUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 250/120) (sustained 250 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 791/6) (sustained 791 cycles)
- **ALERT** `tuned_variants` — 686 non-stamps — atr_arm_uncomputable=686 (seen=14764 stamped=1445 skipped=12633) (streak 786/6) (sustained 786 cycles)
- **ALERT** `auto_dispatch` — 125 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=125) (streak 780/3) (sustained 780 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 53 fed / 0 quiet / 2 never delivered of 55 subscribed; 301123285 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 15 arms current, none stalled; covering 1323/1323 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 34 arms current, none stalled; covering 1159/1159 signals (100%) | 0 |
| auto_dispatch | violating | 125 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=125) (streak 780/3) | 780 |
| binance_ip_weight | ok | peak 126/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82419.90 | 0 |
| candle_coverage | ok | 83/83 symbols with ≥20 15m candles, 83/83 updated within 45m [fresh=83; 77 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 243 dup bars, 0 undedupable; ws 0 out-of-order, 952 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 50 cohorts, 14 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +4 / upstream +29 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1930/1948 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | violating | 6 of 130 open dark rows are not being advanced (worst: BATUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 250/120) | 250 |
| dark_sar_arms | ok | no open arms; covering 1925/1943 signals (99%) | 0 |
| depth_feed | ok | 53/55 books fresh (stale 0, never 2, thin 0); 116487930 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 791/6) | 791 |
| emission_controller | ok | last cycle 1s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×680]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 48/6) | 48 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, profile_reject=2. Held back in this window: session_quality=129, profile_reject=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 6/6) | 6 |
| firestore_read_budget | ok | 1,367 reads/day of 50,000 [engine 1,328, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 6360 sealed bars over 53 symbols; 1485 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +230 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 323185 frozen value(s) avoided; 1728895 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.18R over n=3108 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +18 / upstream +230 | 0 |
| mover_admission_metadata | ok | 924 symbols known, 217 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 5 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3092 rows held, 2509812 evicted (sampled: execution:trigger_not_confirmed 400/915429, execution:overextended 400/807449, setup_compat:regime_STRONG_TREND 400/394022) | 0 |
| price_action_lane | ok | 2346721 evaluated, 1939 emitted; layer1 1939 stamped / 0 blind; cooldown=300181, delta_opposed=193011, no_footprint=894585, no_opposing_target=1211, no_sweep=774734, rr_below_floor=181060 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.32R over n=1157 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +28 / upstream +230 | 0 |
| sar_alignment_crosscheck | ok | 657/32311 disagreed (2.0%) | 0 |
| sar_exit_shadow | violating | upstream +230 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1856 held arms settled, 145 unscored, 31 still walking (22 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 5/53 unfetchable (9%); top cause: located bar does not contain the stamp; symbols: BTWUSDT, CRVUSDT, SKLUSDT, WUSDT, XMRUSDT | 0 |
| sar_live_arms | ok | 32 arms current, none stalled; covering 1158/1158 signals (100%) | 0 |
| sar_refresh_budget | ok | 15 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 453 records await one (48 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 104.55s, worst 172.99s over 27490 lifetime cycles; lifetime 125 over 60s, 8 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.52s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 1181322 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 3s ago (0.35s to run, worst 106.16s), 1083 overrun(s) of 16528 cycles, TTL 900s; slowest agents=0.39s, pair_context=0.19s, data_intake=0.09s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=7, gate reads=0, withheld=7) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +79 / upstream +230 | 0 |
| structural_snap | ok | 6000/6000 measured, 25 blind, 0 levels moved (refusals: redetect_cooldown=1359) | 0 |
| structural_veto_lane | ok | 2637 stamped; 0 with no readable level book, 66 with clear air ahead, 2097 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +230 / upstream +29 | 0 |
| tuned_variants | violating | 686 non-stamps — atr_arm_uncomputable=686 (seen=14764 stamped=1445 skipped=12633) (streak 786/6) | 786 |
| unlock_shorts | ok | 12 open, 43 scheduled, calendar 15.4h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 51 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2630650`
- `Path funnel` emissions: `59`
- `Regime distribution` emissions: `59`
- `QUIET_SCALP_BLOCK` events: `208`
- `confidence_gate` events: `10537`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **81**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 7694 | 16350 | 19716 | 0 |
| futures_aggtrade | 51 | 14090 | 34654 | 37667 | 0 |
| futures_depth | 10 | 8504 | 18595 | 41604 | 0 |
| futures_liq | 5 | 3169 | 4619 | 6256 | 0 |
| futures_mover | 11 | 6550 | 14450 | 32589 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1, present=436029] state[empty=1, populated=436029] buckets[few=3, many=435996, none=1, some=30] sources[none] quality[none]
- funding_rate: presence[absent=43569, present=392461] state[empty=43569, populated=392461] buckets[few=392461, none=43569] sources[none] quality[none]
- liquidation_clusters: presence[absent=232774, present=203256] state[empty=232774, populated=203256] buckets[few=164327, none=232774, some=38929] sources[none] quality[none]
- oi_snapshot: presence[absent=43569, present=392461] state[empty=43569, populated=392461] buckets[few=114, many=391783, none=43569, some=564] sources[none] quality[none]
- order_book: presence[absent=125139, present=310891] state[populated=310891, unavailable=125139] buckets[few=310891, none=125139] sources[book_ticker=310891, unavailable=125139] quality[none=125139, top_of_book_only=310891]
- orderblocks: presence[absent=436030] state[empty=436030] buckets[none=436030] sources[measured_dark=436030] quality[none]
- recent_ticks: presence[present=436030] state[populated=436030] buckets[many=436030] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.196947932243347` sec
- Median create→first breach: `3069.53173995018` sec
- Median create→terminal: `3069.531762480736` sec
- Median first breach→terminal: `4.9948692321777344e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 4.2}, "under_180s": {"count": 3, "pct": 6.2}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.1}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 4 | 1.6851202138990757 | 1.8315148470896672 | 0.919952336482814 | 0 | 4 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.0287876460073444 | 1.6930061689887002 | 0.6076691655659354 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 1.3542782155166218 | 3.0 | 0.4514260718388739 | 1 | 2 |
| MOVER_AVWAP_SCALP | 1 | 1 | 1.203736132002845 | 1.4243960545034258 | 0.8450852754029093 | 0 | 1 |
| MOVER_TREND_PULLBACK | 30 | 30 | 3.6110523544880575 | 3.0 | 1.272995765602177 | 22 | 8 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.3178800052304136 | 1.4621554056433514 | 0.8999500958922231 | 0 | 4 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.7837599702366957 | 1.8832478153036751 | 0.9345586539367146 | 0 | 2 |
| WHALE_MOMENTUM | 1 | 1 | 0.2119460124798263 | 0.824778265504969 | 0.256973324036446 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 4 | 0.0 | 75.0 | 0.0 | 0.0 | -1.4494 | 5624.597317576408 | 5624.597353935242 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.693 | 4048.184319972992 | 4048.1843378543854 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -2.0 | 1191.1033298969269 | 1191.1033508777618 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.2037 | 6895.603155136108 | 6895.603176116943 |
| MOVER_TREND_PULLBACK | 30 | 30 | 23.3 | 50.0 | 23.3 | 0.0 | -0.7725 | 2073.4580619335175 | 2073.4580949544907 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 50.0 | 33.3 | 50.0 | 0.0 | 1.3253 | 13447.951580405235 | 13448.427067041397 |
| TREND_PULLBACK_EMA | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 3.4869 | 2118.2799195051193 | 2121.4186894893646 |
| WHALE_MOMENTUM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8248 | 1541.0280067920685 | 1541.0280268192291 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1101 | 4 | 744 | 0.0 | 0.0 | None | None | 357 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2872 | 36 | 2423 | 100.0 | 0.0 | 2118.2799195051193 | 2121.4186894893646 | 449 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `298`
- Gating Δ: `-79595`
- No-generation Δ: `-583761`
- Fast failures Δ: `3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0143, "current_avg_pnl": -1.4494, "current_win_rate": 0.0, "previous_avg_pnl": -1.4351, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -5.0693, "current_avg_pnl": -2.0, "current_win_rate": 0.0, "previous_avg_pnl": 3.0693, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.1005, "current_avg_pnl": -1.2037, "current_win_rate": 0.0, "previous_avg_pnl": -1.1032, "previous_win_rate": 14.3, "win_rate_delta": -14.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.6799, "current_avg_pnl": -0.7725, "current_win_rate": 23.3, "previous_avg_pnl": -1.4524, "previous_win_rate": 6.2, "win_rate_delta": 17.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.4233, "current_avg_pnl": 1.3253, "current_win_rate": 50.0, "previous_avg_pnl": 1.7486, "previous_win_rate": 75.0, "win_rate_delta": -25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 232, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 25, "geometry_changed_delta": 0, "geometry_preserved_delta": 313, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2534.63, "median_terminal_delta_sec": -2532.43, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
