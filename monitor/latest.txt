# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, MOVER_AVWAP_SCALP
- Top promising signals/paths: MOVER_TREND_PULLBACK
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `2955` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 145 | 145 | 117 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 13645 | 13645 | 12975 | 4 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 101946 | 101947 | 12 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 89235 | 89235 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 88992 | 86264 | 2956 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 89250 | 88143 | 1152 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 94653 | 94302 | 366 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 86658 | 86656 | 3 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 89296 | 89309 | 14 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 89327 | 86705 | 3529 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 106087 | 108795 | 1314 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 101962 | 92015 | 14044 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 94161 | 94161 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 89237 | 89243 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 88969 | 88760 | 229 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 90240 | 87001 | 3950 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 88465 | 88780 | 169 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 81143 | 75318 | 5999 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 81318 | 80640 | 723 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 101929 | 101832 | 114 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 86665 | 86683 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5728 | 5728 | 4453 | 7 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1668 | 1668 | 1020 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 22 | 22 | 19 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 27971 | 27971 | 26733 | 40 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 22 | 22 | 17 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 11507 | 11507 | 9408 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3712 | 3712 | 2857 | 28 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 48400 | 48400 | 40611 | 176 | active-healthy (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2029 | 2029 | 1917 | 9 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 12148 | 12148 | 10176 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1172 | 1172 | 1098 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3389 | 3389 | 3202 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 356 | 356 | 208 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=101947): breakout_not_found=59871, basic_filters_failed=29154, move_not_fresh=8202, breakout_stale=3317, retest_proximity_failed=1188, volume_spike_missing=207, missing_fvg_or_orderblock=8
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=89235): cls_disabled_merged_into_lsr=89235
- **EVAL::DIVERGENCE_CONTINUATION** (total=86264): cvd_divergence_failed=28914, h1_trend_not_aligned=27849, basic_filters_failed=21046, ema_alignment_reject=7063, retest_proximity_failed=995, missing_fvg_or_orderblock=397
- **EVAL::FAILED_AUCTION_RECLAIM** (total=88143): auction_not_detected=54397, basic_filters_failed=19906, reclaim_hold_failed=5406, regime_blocked=4220, tail_too_small=4181, rsi_reject=33
- **EVAL::FUNDING_EXTREME** (total=94302): funding_not_extreme=64956, basic_filters_failed=23030, ema_alignment_reject=2670, missing_funding_rate=1764, rsi_reject=1276, momentum_reject=309, cvd_divergence_failed=281, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=86656): cascade_threshold_not_met=62145, basic_filters_failed=23474, cvd_divergence_failed=511, rsi_reject=506, missing_fvg_or_orderblock=16, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=89309): no_ma_cross=66598, basic_filters_failed=21053, ma_cross_cooldown=1340, ma_cross_htf_misaligned=318
- **EVAL::MEAN_REVERT** (total=86705): no_extension=74967, basic_filters_failed=11738
- **EVAL::MOVER_AVWAP_SCALP** (total=108795): no_avwap_tag=41166, basic_filters_failed=29260, no_mover_leg=27223, avwap_slope_against=6033, avwap_reclaim_no_volume=3130, no_avwap_reclaim=1880, anchor_too_recent=103
- **EVAL::MOVER_TREND_PULLBACK** (total=92015): mover_run_too_small=41707, basic_filters_failed=29199, no_reclaim=18956, no_pullback_tag=2153
- **EVAL::OPENING_RANGE_BREAKOUT** (total=94161): feature_disabled=94161
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=89243): regime_blocked=70227, breakout_not_found=11395, basic_filters_failed=5386, adx_reject=2215, ema_alignment_reject=20
- **EVAL::QUIET_COMPRESSION_BREAK** (total=88760): compression_not_detected=43942, regime_blocked=23176, basic_filters_failed=14513, breakout_not_detected=6542, volume_confirmation_failed=569, missing_fvg_or_orderblock=12, rsi_reject=6
- **EVAL::RANGE_FADE** (total=87001): no_range_edge=75259, basic_filters_failed=11742
- **EVAL::SR_FLIP_RETEST** (total=88780): flip_close_not_confirmed=55711, basic_filters_failed=19896, regime_blocked=4213, long_break_volume_thin=3725, retest_out_of_zone=2384, h1_break_not_confirmed=1675, reclaim_hold_failed=649, long_acceptance_not_held=236, ema_alignment_reject=96, wick_quality_failed=69, whipsaw_flip=67, missing_fvg_or_orderblock=59
- **EVAL::STANDARD** (total=75318): adx_reject=24266, momentum_reject=22065, macd_reject=9423, basic_filters_failed=7718, sweeps_not_detected=6662, ema_alignment_reject=3396, htf_poi_unanchored=1592, invalid_sl_geometry=125, rsi_reject=65, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=80640): h1_trend_not_aligned=32648, ema_alignment_reject=11610, basic_filters_failed=10904, h1_pullback_not_confirmed=8463, ema_not_tested_prev=5493, no_ema_reclaim_close=4894, body_conviction_fail=2667, rsi_reject=2080, prev_already_below_emas=749, no_prev_low_break=366, prev_already_above_emas=267, no_prev_high_break=206, momentum_flat=157, missing_fvg_or_orderblock=61, ema21_not_tagged=60, momentum_reject=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=101832): breakout_not_found=52220, basic_filters_failed=29154, move_not_fresh=12516, breakout_stale=5964, retest_proximity_failed=1534, volume_spike_missing=393, move_exhausted=42, missing_fvg_or_orderblock=9
- **EVAL::WHALE_MOMENTUM** (total=86683): momentum_reject=65543, recent_ticks_insufficient=14704, basic_filters_failed=6436

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=802): setup_compat:regime_VOLATILE_UNSUITABLE=707, setup_compat:regime_BREAKOUT_EXPANSION=77, execution:overextended=18
- **FAILED_AUCTION_RECLAIM** (total=1530): execution:overextended=925, setup_compat:regime_STRONG_TREND=304, context_floor=301
- **FUNDING_EXTREME_SIGNAL** (total=1406): execution:trigger_not_confirmed=1406
- **LIQUIDATION_REVERSAL** (total=23): execution:trigger_not_confirmed=22, context_floor=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=6739): execution:trigger_not_confirmed=2884, execution:overextended=2649, setup_compat:regime_STRONG_TREND=1206
- **MA_CROSS_TREND_SHIFT** (total=18): setup_compat:regime_DIRTY_RANGE=6, setup_compat:regime_CLEAN_RANGE=4, execution:trigger_not_confirmed=3, execution:overextended=3, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **MEAN_REVERT** (total=4178): setup_compat:regime_WEAK_TREND=1779, setup_compat:regime_STRONG_TREND=1771, execution:overextended=628
- **MOVER_AVWAP_SCALP** (total=1538): execution:overextended=1140, execution:trigger_not_confirmed=345, entry_quality=53
- **MOVER_TREND_PULLBACK** (total=17087): execution:trigger_not_confirmed=9914, execution:overextended=6129, entry_quality=1044
- **QUIET_COMPRESSION_BREAK** (total=34): execution:overextended=26, execution:trigger_not_confirmed=8
- **RANGE_FADE** (total=4057): setup_compat:regime_WEAK_TREND=1843, setup_compat:regime_STRONG_TREND=1029, setup_compat:regime_VOLATILE_UNSUITABLE=656, execution:overextended=292, context_edge=196, setup_compat:regime_BREAKOUT_EXPANSION=41
- **TREND_PULLBACK_EMA** (total=3104): setup_compat:regime_CLEAN_RANGE=2120, setup_compat:regime_DIRTY_RANGE=813, setup_compat:regime_VOLATILE_UNSUITABLE=111, entry_quality=60
- **VOLUME_SURGE_BREAKOUT** (total=11): execution:overextended=11

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 312603 | 53.2% |
| QUIET | 109075 | 18.6% |
| TRENDING_UP | 74255 | 12.6% |
| TRENDING_DOWN | 57617 | 9.8% |
| VOLATILE | 34207 | 5.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **91**
- Average confidence gap to threshold: **16.50** (samples=91) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=23, BTCUSDT=16, TRXUSDT=12, TAOUSDT=11, HYPEUSDT=7, ONDOUSDT=7, LTCUSDT=5, SUIUSDT=4, XPLUSDT=2, XLMUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 143 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 4 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 281 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 16 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 27 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 82 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 180 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 239 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 79 |
| MEAN_REVERT | kept | min_confidence_pass | 22 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 215 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 167 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1211 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 8 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1903 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 48 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 10 |
| SR_FLIP_RETEST | filtered | min_confidence | 10 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 6 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 27 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 42 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 68 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 96 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 48.50 | 61.00 | 12.50 | 21.20 | 19.60 | 20.00 | 4.50 | 20.00 |
| DIVERGENCE_CONTINUATION | filtered | 145 | 45.69 | 64.50 | 18.81 | 19.93 | 19.66 | 18.77 | 1.30 | 19.43 |
| DIVERGENCE_CONTINUATION | kept | 4 | 69.70 | 65.00 | -4.70 | 21.00 | 19.88 | 18.98 | 4.25 | 5.10 |
| FAILED_AUCTION_RECLAIM | filtered | 297 | 52.72 | 63.59 | 10.87 | 20.07 | 19.19 | 20.00 | 3.56 | 14.24 |
| FAILED_AUCTION_RECLAIM | kept | 27 | 65.01 | 65.00 | -0.01 | 19.10 | 19.61 | 20.00 | 4.65 | 3.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 82 | 41.06 | 64.29 | 23.23 | 20.10 | 15.61 | 16.78 | 3.10 | 11.31 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 189 | 58.48 | 65.00 | 6.52 | 19.65 | 18.19 | 18.36 | 2.77 | 10.64 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 239 | 69.93 | 65.00 | -4.93 | 20.23 | 18.58 | 18.14 | 3.70 | 2.62 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.50 | 61.00 | 2.50 | 20.60 | 20.00 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 68.10 | 65.00 | -3.10 | 18.83 | 17.73 | 15.80 | 0.00 | 4.00 |
| MEAN_REVERT | filtered | 79 | 54.87 | 65.00 | 10.13 | 19.10 | 14.56 | 15.19 | 0.00 | 13.13 |
| MEAN_REVERT | kept | 22 | 72.20 | 65.00 | -7.20 | 19.30 | 16.86 | 14.23 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 217 | 49.85 | 64.93 | 15.08 | 20.37 | 16.19 | 15.80 | 3.82 | 19.07 |
| MOVER_AVWAP_SCALP | kept | 167 | 76.49 | 65.00 | -11.49 | 20.28 | 15.73 | 15.80 | 4.22 | 1.55 |
| MOVER_TREND_PULLBACK | filtered | 1219 | 56.52 | 63.78 | 7.26 | 20.94 | 18.53 | 15.80 | 3.61 | 16.84 |
| MOVER_TREND_PULLBACK | kept | 1903 | 76.07 | 65.00 | -11.07 | 20.52 | 18.38 | 15.80 | 3.99 | 1.63 |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 44.16 | 65.00 | 20.84 | 22.93 | 19.66 | 20.00 | 0.00 | 13.04 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 71.73 | 65.00 | -6.73 | 21.92 | 19.91 | 20.00 | 0.00 | 1.19 |
| SR_FLIP_RETEST | filtered | 16 | 58.99 | 65.00 | 6.01 | 23.84 | 20.00 | 15.20 | 2.00 | 7.45 |
| SR_FLIP_RETEST | kept | 27 | 70.95 | 65.00 | -5.95 | 23.35 | 20.00 | 15.33 | 2.02 | 1.41 |
| TREND_PULLBACK_EMA | filtered | 42 | 57.69 | 62.62 | 4.93 | 19.48 | 19.92 | 16.61 | 4.90 | 8.90 |
| TREND_PULLBACK_EMA | kept | 68 | 78.85 | 65.00 | -13.85 | 20.79 | 19.74 | 18.08 | 4.52 | 1.08 |
| VOLUME_SURGE_BREAKOUT | filtered | 96 | 52.96 | 64.50 | 11.54 | 19.33 | 17.34 | 20.00 | 3.74 | 6.24 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 76.82 | 65.00 | -11.82 | 20.20 | 17.15 | 20.00 | 5.12 | 2.40 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 48.50 | 2.00 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 145 | 45.69 | 24.39 | 11.86 | 4.57 | 12.69 | 5.61 | 8.62 | 1.30 |
| DIVERGENCE_CONTINUATION | kept | 4 | 69.70 | 25.00 | 13.00 | 6.00 | 11.75 | 6.00 | 8.80 | 4.25 |
| FAILED_AUCTION_RECLAIM | filtered | 297 | 52.72 | 21.33 | 15.83 | 5.40 | 13.73 | 6.49 | 5.24 | 3.56 |
| FAILED_AUCTION_RECLAIM | kept | 27 | 65.01 | 23.74 | 17.85 | 4.33 | 7.15 | 5.35 | 5.85 | 4.65 |
| FUNDING_EXTREME_SIGNAL | filtered | 82 | 41.06 | 23.34 | 8.00 | 6.80 | 12.57 | 9.25 | 4.30 | 3.10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 189 | 58.48 | 24.62 | 14.00 | 3.86 | 13.72 | 5.95 | 4.21 | 2.77 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 239 | 69.93 | 24.50 | 14.00 | 6.25 | 12.64 | 6.28 | 5.17 | 3.70 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.50 | 25.00 | 14.00 | 15.00 | 14.00 | 2.50 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 68.10 | 21.67 | 14.67 | 9.00 | 13.00 | 5.00 | 8.77 | 0.00 |
| MEAN_REVERT | filtered | 79 | 54.87 | 23.48 | 17.59 | 11.70 | 12.32 | 5.00 | 6.27 | 0.00 |
| MEAN_REVERT | kept | 22 | 72.20 | 21.73 | 17.82 | 6.41 | 13.00 | 5.00 | 8.25 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 217 | 49.85 | 18.02 | 18.00 | 12.04 | 14.40 | 5.76 | 5.91 | 3.82 |
| MOVER_AVWAP_SCALP | kept | 167 | 76.49 | 19.48 | 18.01 | 11.00 | 13.62 | 7.98 | 7.51 | 4.22 |
| MOVER_TREND_PULLBACK | filtered | 1219 | 56.52 | 19.07 | 18.08 | 7.53 | 12.86 | 6.22 | 8.21 | 3.61 |
| MOVER_TREND_PULLBACK | kept | 1903 | 76.07 | 19.92 | 18.10 | 7.61 | 12.59 | 6.60 | 9.05 | 3.99 |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 44.16 | 19.35 | 16.56 | 12.28 | 14.00 | 5.49 | 4.34 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 71.73 | 17.80 | 17.60 | 11.40 | 14.00 | 6.15 | 6.87 | 0.00 |
| SR_FLIP_RETEST | filtered | 16 | 58.99 | 19.00 | 14.25 | 4.69 | 12.69 | 5.00 | 8.81 | 2.00 |
| SR_FLIP_RETEST | kept | 27 | 70.95 | 22.04 | 17.26 | 3.56 | 13.89 | 5.00 | 8.71 | 2.02 |
| TREND_PULLBACK_EMA | filtered | 42 | 57.69 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 7.47 | 4.90 |
| TREND_PULLBACK_EMA | kept | 68 | 78.85 | 20.01 | 18.03 | 7.57 | 14.62 | 6.57 | 9.18 | 4.52 |
| VOLUME_SURGE_BREAKOUT | filtered | 96 | 52.96 | 19.08 | 16.75 | 12.28 | 13.50 | 4.84 | 4.00 | 3.74 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 76.82 | 23.00 | 16.00 | 12.75 | 14.00 | 5.00 | 7.10 | 5.12 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 2 | 48.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 145 | 45.69 | 0.00 | 0.00 | 1.99 | 0.00 | 0.08 | 0.12 | 0.00 | 0.00 | **2.19** |
| DIVERGENCE_CONTINUATION | kept | 4 | 69.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 297 | 52.72 | 0.00 | 0.00 | 0.00 | 0.00 | 1.04 | 0.20 | 0.00 | 0.00 | **1.24** |
| FAILED_AUCTION_RECLAIM | kept | 27 | 65.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 82 | 41.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 189 | 58.48 | 0.00 | 0.00 | 1.61 | 0.00 | 0.32 | 0.16 | 0.00 | 0.00 | **2.09** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 239 | 69.93 | 0.00 | 0.00 | 0.00 | 0.00 | 1.81 | 0.08 | 0.00 | 0.00 | **1.89** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 58.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 68.10 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| MEAN_REVERT | filtered | 79 | 54.87 | 0.00 | 0.00 | 0.00 | 0.00 | 6.68 | 0.00 | 0.00 | 0.00 | **6.68** |
| MEAN_REVERT | kept | 22 | 72.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 217 | 49.85 | 0.07 | 0.00 | 0.04 | 0.00 | 3.04 | 0.18 | 0.00 | 1.58 | **4.91** |
| MOVER_AVWAP_SCALP | kept | 167 | 76.49 | 0.27 | 0.00 | 0.05 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | **0.75** |
| MOVER_TREND_PULLBACK | filtered | 1219 | 56.52 | 0.01 | 0.00 | 0.95 | 0.00 | 0.26 | 0.01 | 0.00 | 0.00 | **1.23** |
| MOVER_TREND_PULLBACK | kept | 1903 | 76.07 | 0.00 | 0.00 | 0.72 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.75** |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 44.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 8.53 | **9.33** |
| QUIET_COMPRESSION_BREAK | kept | 10 | 71.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **0.86** |
| SR_FLIP_RETEST | filtered | 16 | 58.99 | 0.00 | 0.00 | 0.00 | 0.00 | 4.05 | 0.00 | 0.00 | 0.00 | **4.05** |
| SR_FLIP_RETEST | kept | 27 | 70.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 42 | 57.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 68 | 78.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.18** |
| VOLUME_SURGE_BREAKOUT | filtered | 96 | 52.96 | 0.00 | 0.00 | 2.05 | 0.00 | 0.00 | 0.27 | 0.00 | 0.50 | **2.82** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 76.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.90 | **0.90** |

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
- Outcomes recorded: **100227 held of 252715 seen** across 21 strategies; 2297 cells past the sample floor; **1008 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 36219 | 541/35678/0 | 45% | -0.14 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.23R) | ASIA/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.13R) |
| MOVER_AVWAP_SCALP | 12436 | 152/12284/0 | 41% | -0.24 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 7774 | 90/7684/0 | 40% | -0.22 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6164 | 30/6134/0 | 50% | -0.02 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5384 | 0/0/5384 | 43% | -0.09 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.56R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (-0.86R) |
| TREND_PULLBACK_EMA | 4997 | 24/4973/0 | 45% | -0.15 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4445 | 0/0/4445 | 38% | -0.05 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | NY/QUIET/COMPRESSED/BTC_FALLING (-0.98R) |
| QUIET_COMPRESSION_BREAK | 4267 | 244/4023/0 | 43% | -0.15 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.72R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4115 | 0/0/4115 | 34% | -0.40 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.13R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2898 | 49/2849/0 | 38% | -0.36 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.29R) |
| MEAN_REVERT | 1847 | 20/1827/0 | 49% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1785 | 2/1783/0 | 34% | -0.39 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1592 | 0/1592/0 | 42% | +0.02 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1018 | 10/1008/0 | 49% | -0.19 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 709 | 0/0/709 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.47R) |
| RANGE_FADE | 586 | 0/586/0 | 38% | -0.36 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 352 | 29/323/0 | 41% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 210 | 0/210/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 58 | 6/52/0 | 41% | -0.11 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 142 | 28% / -0.54R | 142 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 403 | 45% / -0.20R | 403 | 54% / -0.04R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 974 | 44% / -0.19R | 974 | 50% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 688 | 42% / -0.20R | 688 | 44% / -0.11R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 118 | 49% / -0.25R | 118 | 51% / -0.17R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 5485 | 51% / -0.08R | 5485 | 55% / -0.00R | +0.08 | **ATR** |
| RANGE_FADE | 27 | 41% / -0.09R | 27 | 41% / -0.16R | -0.07 | **FIXED** |
| BREAKDOWN_SHORT | 30 | 33% / -0.18R | 30 | 37% / -0.12R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 568 | 50% / -0.21R | 568 | 54% / -0.15R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 93 | 40% / -0.09R | 93 | 47% / -0.06R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 584 | 51% / -0.06R | 584 | 57% / -0.04R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 724 | 45% / -0.16R | 724 | 45% / -0.16R | -0.01 | **FIXED** |
| MEAN_REVERT | 137 | 53% / -0.07R | 137 | 51% / -0.07R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8046 | 30% | -0.18R | 307 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 974 | 48% | -0.08R | 189 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 59 | 51% | -0.05R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 696 | 36% / -0.10R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7108 | 36% / -0.14R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1282 | 35% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 547 | 35% / -0.12R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 660 | 41% / +0.02R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 538 | 37% / -0.06R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 554 | 44% / -0.14R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 124 | 29% / -0.35R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 181 | 30% / -0.58R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 112 | 54% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 52 | 37% / -0.17R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 25 | 36% / -0.04R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 120 | 36% / -0.36R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 26 | 12% / -0.61R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **1** · boot grace active: False
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 5/3) (sustained 5 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1604925 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 5/3) | 5 |
| ai_governor_live_arms | ok | 34 arms current, none stalled; covering 447/447 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 67 arms current, none stalled; covering 1037/1037 signals (100%) | 0 |
| auto_dispatch | ok | placed=0 rejected=0 skipped=6 over 3 fan-out(s) to a keyed roster; top reasons: mode:off=3, mode:paper=3 (gaps: skip 3, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 76494.90 | 0 |
| candle_coverage | ok | 78/78 symbols with ≥20 15m candles, 78/78 updated within 45m [fresh=78; 75 Tier-1 futures + 3 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 469 dup bars, 0 undedupable; ws 0 out-of-order, 111 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +36 but output +0 (streak 5/72) | 5 |
| dark_atr_trail_arms | ok | no open arms; covering 1084/1101 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 4 of 112 open dark rows are not being advanced (worst: CVCUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 5/120) | 5 |
| dark_sar_arms | ok | no open arms; covering 1076/1093 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 272353 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.71R (bound 0.3) (streak 5/6) | 5 |
| emission_controller | ok | last cycle 1288s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×599]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 5/6) | 5 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/75 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=62, profile_reject=8. Held back in this window: session_quality=5. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 5/6) | 5 |
| footprint_bars | ok | 2399 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +200 but output +0 (streak 5/6) | 5 |
| indicator_cache_key | ok | 164 frozen value(s) avoided; 13795 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.17R over n=1827 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +37 / upstream +200 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 3 held, 3 with scan counts, 3 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 8 locked / 8 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3181 rows held, 1470164 evicted (sampled: execution:trigger_not_confirmed 400/537501, execution:overextended 400/482586, setup_compat:regime_STRONG_TREND 400/220369) | 0 |
| price_action_lane | ok | 33958 evaluated, 28 emitted; layer1 28 stamped / 0 blind; cooldown=4679, delta_opposed=2720, no_footprint=10287, no_sweep=13677, rr_below_floor=2567 | 0 |
| promoted_pair_integrity | ok | 3/3 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.36R over n=586 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +37 / upstream +200 | 0 |
| sar_alignment_crosscheck | ok | 10/518 disagreed (1.9%) | 0 |
| sar_exit_shadow | violating | upstream +200 but output +0 (streak 5/6) | 5 |
| sar_hold_arm | ok | 1811 held arms settled, 189 unscored, 67 still walking (61 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 7/51 unfetchable (14%); top cause: gap or duplicate bar in the 15m window; symbols: AVAXUSDT, COTIUSDT, DOGEUSDT, POLUSDT, SKYAIUSDT | 0 |
| sar_live_arms | ok | 67 arms current, none stalled; covering 1037/1037 signals (100%) | 0 |
| sar_refresh_budget | ok | 10 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 41 still mid-window | 0 |
| scan_cycle | ok | last 7.88s, worst 41.99s over 446 lifetime cycles; lifetime 0 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.05s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 16005 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 31s ago (0.18s to run, worst 27.63s), 4 overrun(s) of 217 cycles, TTL 900s; slowest position_marks=6.04s, signals=3.28s, dark_promotion=1.45s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +6 / upstream +200 | 0 |
| structural_snap | ok | 5202/5202 measured, 21 blind, 0 levels moved (refusals: none) | 0 |
| structural_veto_lane | ok | only 11 rows stamped yet | 0 |
| suppression_audit | ok | output +200 / upstream +36 | 0 |
| tuned_variants | ok | seen=194 stamped=8 skipped=186, residue 0 (none recorded) | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2873801`
- `Path funnel` emissions: `73`
- `Regime distribution` emissions: `73`
- `QUIET_SCALP_BLOCK` events: `91`
- `confidence_gate` events: `4934`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 2 | 5026 | 5026 | 18650 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| regime_shift | 6 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=448280] state[populated=448280] buckets[many=448280] sources[none] quality[none]
- funding_rate: presence[absent=37441, present=410839] state[empty=37441, populated=410839] buckets[few=410839, none=37441] sources[none] quality[none]
- liquidation_clusters: presence[absent=240185, present=208095] state[empty=240185, populated=208095] buckets[few=170782, none=240185, some=37313] sources[none] quality[none]
- oi_snapshot: presence[absent=34765, present=413515] state[empty=34765, populated=413515] buckets[few=100, many=412867, none=34765, some=548] sources[none] quality[none]
- order_book: presence[absent=126067, present=322213] state[populated=322213, unavailable=126067] buckets[few=322213, none=126067] sources[book_ticker=322213, unavailable=126067] quality[none=126067, top_of_book_only=322213]
- orderblocks: presence[absent=448280] state[empty=448280] buckets[none=448280] sources[measured_dark=448280] quality[none]
- recent_ticks: presence[present=448280] state[populated=448280] buckets[many=448280] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.059787034988403` sec
- Median create→first breach: `3455.8417818546295` sec
- Median create→terminal: `3456.2409658432007` sec
- Median first breach→terminal: `0.00010895729064941406` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 1.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 2.0050178038180295 | 2.335925349922239 | 0.8274576179247198 | 0 | 2 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.9463890808569435 | 1.1425544751616592 | 0.8233261706645132 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 1.232876272247251 | 1.5714818009026899 | 0.7966464006281716 | 0 | 6 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 1.049563262859205 | 1.2132560871510898 | 0.9007645563251889 | 0 | 3 |
| MOVER_AVWAP_SCALP | 4 | 4 | 3.1891202573751034 | 2.942587349938739 | 1.083042722931883 | 3 | 1 |
| MOVER_TREND_PULLBACK | 44 | 44 | 4.330065888707278 | 3.0 | 1.5104526472814948 | 33 | 11 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.1800830502448967 | 1.3241686115506306 | 0.8911879045848953 | 0 | 5 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 2.1062 | 33743.11816453934 | 33743.28461754322 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.1958 | 638.350399017334 | 638.4986358880997 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 16.7 | 50.0 | 16.7 | 0.0 | -0.1332 | 1952.4364819526672 | 1952.4365409612656 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -0.6083 | 11412.794150948524 | 11412.794221043587 |
| MOVER_AVWAP_SCALP | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2912 | 5100.138851523399 | 5100.1389285326 |
| MOVER_TREND_PULLBACK | 44 | 44 | 50.0 | 29.5 | 50.0 | 0.0 | 1.7021 | 2786.881584048271 | 2787.0360300540924 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 20.0 | 60.0 | 20.0 | 0.0 | -0.1464 | 18294.436002016068 | 18294.436110973358 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1172 | 5 | 1098 | 0.0 | 0.0 | None | None | 74 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3389 | 9 | 3202 | 0.0 | 0.0 | None | None | 187 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `52`
- Gating Δ: `-10871`
- No-generation Δ: `59847`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.4384, "current_avg_pnl": -0.1332, "current_win_rate": 16.7, "previous_avg_pnl": 0.3052, "previous_win_rate": 50.0, "win_rate_delta": -33.3}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -1.9369, "current_avg_pnl": -0.6083, "current_win_rate": 0.0, "previous_avg_pnl": 1.3286, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.2223, "current_avg_pnl": -1.2912, "current_win_rate": 0.0, "previous_avg_pnl": -0.0689, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0699, "current_avg_pnl": 1.7021, "current_win_rate": 50.0, "previous_avg_pnl": 1.6322, "previous_win_rate": 39.0, "win_rate_delta": 11.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.865, "current_avg_pnl": -0.1464, "current_win_rate": 20.0, "previous_avg_pnl": 0.7186, "previous_win_rate": 42.9, "win_rate_delta": -22.9}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 74, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 38, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
