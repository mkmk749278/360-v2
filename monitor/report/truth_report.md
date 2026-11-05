# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `941` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 237 | 237 | 237 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11232 | 11232 | 9712 | 15 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 81771 | 81757 | 43 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 76025 | 76025 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 75577 | 73141 | 2869 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 76052 | 75193 | 928 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 75515 | 75358 | 187 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 64364 | 64357 | 19 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 76129 | 76152 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 76168 | 74175 | 2700 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 85910 | 92960 | 869 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 81804 | 75784 | 10058 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 75009 | 75009 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 76030 | 76046 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 75547 | 75378 | 195 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 76880 | 76371 | 757 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 75019 | 75338 | 170 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 63875 | 60267 | 4011 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 64284 | 64055 | 306 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 81725 | 81747 | 18 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 64384 | 64391 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3521 | 3521 | 2750 | 6 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 550 | 550 | 60 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 64 | 64 | 63 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 22838 | 22838 | 22321 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 8 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6781 | 6781 | 5446 | 9 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2384 | 2384 | 572 | 53 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 29592 | 29592 | 14882 | 290 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 28 | 28 | 28 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 812 | 812 | 683 | 16 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2193 | 2193 | 1894 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 495 | 495 | 417 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1842 | 1842 | 1361 | 38 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 75 | 75 | 0 | 8 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=81757): breakout_not_found=47729, basic_filters_failed=22325, move_not_fresh=7430, breakout_stale=3195, retest_proximity_failed=899, volume_spike_missing=177, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=76025): cls_disabled_merged_into_lsr=76025
- **EVAL::DIVERGENCE_CONTINUATION** (total=73141): cvd_divergence_failed=27636, h1_trend_not_aligned=20462, basic_filters_failed=18054, ema_alignment_reject=5881, retest_proximity_failed=860, missing_fvg_or_orderblock=248
- **EVAL::FAILED_AUCTION_RECLAIM** (total=75193): auction_not_detected=48897, basic_filters_failed=17105, reclaim_hold_failed=4089, tail_too_small=2537, regime_blocked=2527, rsi_reject=38
- **EVAL::FUNDING_EXTREME** (total=75358): funding_not_extreme=53808, basic_filters_failed=17687, missing_funding_rate=1898, ema_alignment_reject=1212, rsi_reject=463, momentum_reject=144, cvd_divergence_failed=139, missing_fvg_or_orderblock=7
- **EVAL::LIQUIDATION_REVERSAL** (total=64357): cascade_threshold_not_met=45852, basic_filters_failed=17841, cvd_divergence_failed=384, rsi_reject=262, missing_fvg_or_orderblock=18
- **EVAL::MA_CROSS_TREND_SHIFT** (total=76152): no_ma_cross=56213, basic_filters_failed=18069, ma_cross_htf_misaligned=1352, ma_cross_cooldown=518
- **EVAL::MEAN_REVERT** (total=74175): no_extension=60678, basic_filters_failed=13497
- **EVAL::MOVER_AVWAP_SCALP** (total=92960): no_avwap_tag=38188, basic_filters_failed=22522, no_mover_leg=18550, avwap_slope_against=9853, avwap_reclaim_no_volume=2194, no_avwap_reclaim=1621, anchor_too_recent=32
- **EVAL::MOVER_TREND_PULLBACK** (total=75784): mover_run_too_small=37309, basic_filters_failed=22430, no_reclaim=13650, no_pullback_tag=2395
- **EVAL::OPENING_RANGE_BREAKOUT** (total=75009): feature_disabled=75009
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=76046): regime_blocked=47369, breakout_not_found=18780, basic_filters_failed=5674, adx_reject=4161, ema_alignment_reject=62
- **EVAL::QUIET_COMPRESSION_BREAK** (total=75378): regime_blocked=31057, compression_not_detected=29348, basic_filters_failed=11418, breakout_not_detected=3095, volume_confirmation_failed=349, rsi_reject=89, missing_fvg_or_orderblock=22
- **EVAL::RANGE_FADE** (total=76371): no_range_edge=62871, basic_filters_failed=13500
- **EVAL::SR_FLIP_RETEST** (total=75338): flip_close_not_confirmed=49606, basic_filters_failed=17082, regime_blocked=2513, long_break_volume_thin=2461, retest_out_of_zone=1508, h1_break_not_confirmed=1242, reclaim_hold_failed=541, long_acceptance_not_held=168, ema_alignment_reject=155, wick_quality_failed=48, whipsaw_flip=13, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=60267): momentum_reject=17557, adx_reject=14691, basic_filters_failed=10387, sweeps_not_detected=6165, macd_reject=5637, ema_alignment_reject=4462, htf_poi_unanchored=1256, rsi_reject=77, invalid_sl_geometry=26, mtf_reject=9
- **EVAL::TREND_PULLBACK** (total=64055): h1_trend_not_aligned=22484, basic_filters_failed=10404, ema_alignment_reject=10259, h1_pullback_not_confirmed=7535, ema_not_tested_prev=4599, no_ema_reclaim_close=3998, body_conviction_fail=1701, rsi_reject=1369, prev_already_above_emas=795, no_prev_high_break=404, momentum_flat=196, prev_already_below_emas=129, no_prev_low_break=94, ema21_not_tagged=57, missing_fvg_or_orderblock=25, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=81747): breakout_not_found=43266, basic_filters_failed=22324, move_not_fresh=10623, breakout_stale=3799, retest_proximity_failed=1495, volume_spike_missing=220, missing_fvg_or_orderblock=15, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=64391): momentum_reject=54240, recent_ticks_insufficient=7498, basic_filters_failed=2653

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=46): execution:overextended=46
- **DIVERGENCE_CONTINUATION** (total=221): setup_compat:regime_VOLATILE_UNSUITABLE=192, setup_compat:regime_BREAKOUT_EXPANSION=29
- **FAILED_AUCTION_RECLAIM** (total=1125): execution:overextended=573, setup_compat:regime_STRONG_TREND=273, context_floor=268, setup_compat:regime_VOLATILE_UNSUITABLE=11
- **FUNDING_EXTREME_SIGNAL** (total=481): execution:trigger_not_confirmed=472, context_floor=9
- **LIQUIDATION_REVERSAL** (total=61): execution:trigger_not_confirmed=61
- **LIQUIDITY_SWEEP_REVERSAL** (total=5470): execution:trigger_not_confirmed=1988, setup_compat:regime_STRONG_TREND=1897, execution:overextended=1585
- **MA_CROSS_TREND_SHIFT** (total=11): setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=3, execution:overextended=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=3453): setup_compat:regime_STRONG_TREND=1672, setup_compat:regime_WEAK_TREND=1237, execution:overextended=536, entry_quality=8
- **MOVER_AVWAP_SCALP** (total=1600): execution:overextended=972, execution:trigger_not_confirmed=329, entry_quality=299
- **MOVER_TREND_PULLBACK** (total=13794): execution:trigger_not_confirmed=7675, execution:overextended=4603, entry_quality=1516
- **POST_DISPLACEMENT_CONTINUATION** (total=25): execution:overextended=25
- **QUIET_COMPRESSION_BREAK** (total=57): execution:trigger_not_confirmed=57
- **RANGE_FADE** (total=1834): setup_compat:regime_STRONG_TREND=926, setup_compat:regime_WEAK_TREND=639, setup_compat:regime_VOLATILE_UNSUITABLE=156, execution:overextended=102, context_edge=6, setup_compat:regime_BREAKOUT_EXPANSION=5
- **TREND_PULLBACK_EMA** (total=1735): setup_compat:regime_CLEAN_RANGE=1152, setup_compat:regime_DIRTY_RANGE=434, entry_quality=107, setup_compat:regime_VOLATILE_UNSUITABLE=42
- **VOLUME_SURGE_BREAKOUT** (total=8): execution:overextended=8

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 192447 | 43.7% |
| TRENDING_UP | 88217 | 20.0% |
| QUIET | 74433 | 16.9% |
| TRENDING_DOWN | 72097 | 16.4% |
| VOLATILE | 13559 | 3.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **154**
- Average confidence gap to threshold: **10.30** (samples=154) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=28, XMRUSDT=23, ENAUSDT=16, BNBUSDT=12, ONDOUSDT=9, 1000PEPEUSDT=9, INJUSDT=8, SOLUSDT=6, ZROUSDT=6, LINKUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 284 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 151 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 71 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 26 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 9 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 112 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 21 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 131 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 346 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 3 |
| MEAN_REVERT | kept | min_confidence_pass | 37 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 339 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 8 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 636 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3455 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 38 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3813 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 44 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 36 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 49 |
| SR_FLIP_RETEST | filtered | min_confidence | 24 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 69 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 7 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 183 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 18 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 22 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 289 | 56.73 | 65.00 | 8.27 | 20.77 | 19.71 | 17.93 | 2.52 | 12.51 |
| DIVERGENCE_CONTINUATION | kept | 151 | 70.19 | 65.00 | -5.19 | 20.93 | 19.02 | 17.72 | 1.62 | 6.38 |
| FAILED_AUCTION_RECLAIM | filtered | 97 | 51.06 | 64.51 | 13.45 | 18.81 | 19.58 | 20.00 | 3.25 | 7.07 |
| FAILED_AUCTION_RECLAIM | kept | 9 | 68.90 | 65.00 | -3.90 | 21.03 | 19.08 | 20.00 | 4.00 | 1.33 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 51.74 | 61.00 | 9.26 | 21.06 | 14.98 | 17.36 | 2.80 | 10.38 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 65.55 | 65.00 | -0.55 | 21.70 | 13.65 | 15.55 | 3.00 | 2.10 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 133 | 53.21 | 64.76 | 11.55 | 20.32 | 19.38 | 17.92 | 1.69 | 15.38 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 131 | 72.77 | 65.00 | -7.77 | 22.14 | 18.55 | 18.16 | 2.76 | 0.26 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.30 | 65.00 | -10.30 | 20.30 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 349 | 52.98 | 64.89 | 11.91 | 19.97 | 16.85 | 16.62 | 0.00 | 13.70 |
| MEAN_REVERT | kept | 37 | 71.10 | 65.00 | -6.10 | 19.12 | 15.18 | 18.14 | 0.00 | 4.05 |
| MOVER_AVWAP_SCALP | filtered | 351 | 52.06 | 64.14 | 12.08 | 20.68 | 14.55 | 15.80 | 4.48 | 17.45 |
| MOVER_AVWAP_SCALP | kept | 636 | 81.10 | 65.00 | -16.10 | 20.19 | 15.67 | 15.80 | 4.36 | 2.97 |
| MOVER_TREND_PULLBACK | filtered | 3493 | 55.12 | 64.01 | 8.89 | 19.84 | 18.70 | 15.80 | 4.26 | 18.10 |
| MOVER_TREND_PULLBACK | kept | 3813 | 76.18 | 65.00 | -11.18 | 20.12 | 18.24 | 15.80 | 4.26 | 1.67 |
| QUIET_COMPRESSION_BREAK | filtered | 80 | 56.44 | 64.00 | 7.56 | 22.36 | 19.38 | 20.00 | 0.00 | 15.11 |
| QUIET_COMPRESSION_BREAK | kept | 49 | 75.64 | 65.00 | -10.64 | 22.35 | 19.88 | 20.00 | 0.00 | 4.04 |
| SR_FLIP_RETEST | filtered | 26 | 56.92 | 64.85 | 7.93 | 21.95 | 20.00 | 15.95 | 2.48 | 13.29 |
| SR_FLIP_RETEST | kept | 1 | 66.30 | 65.00 | -1.30 | 20.20 | 20.00 | 18.80 | 1.00 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 76 | 57.10 | 64.41 | 7.31 | 21.26 | 19.77 | 17.89 | 4.95 | 15.38 |
| TREND_PULLBACK_EMA | kept | 183 | 76.98 | 65.00 | -11.98 | 21.27 | 19.77 | 17.45 | 5.05 | 1.46 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 59.44 | 64.56 | 5.12 | 20.84 | 16.88 | 20.00 | 4.44 | 11.56 |
| VOLUME_SURGE_BREAKOUT | kept | 22 | 70.30 | 65.00 | -5.30 | 19.83 | 17.25 | 20.00 | 5.05 | 10.72 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 289 | 56.73 | 21.40 | 12.99 | 6.17 | 12.55 | 5.51 | 8.10 | 2.52 |
| DIVERGENCE_CONTINUATION | kept | 151 | 70.19 | 22.56 | 16.08 | 7.19 | 13.50 | 6.57 | 9.13 | 1.62 |
| FAILED_AUCTION_RECLAIM | filtered | 97 | 51.06 | 23.43 | 14.00 | 5.94 | 13.93 | 5.39 | 3.81 | 3.25 |
| FAILED_AUCTION_RECLAIM | kept | 9 | 68.90 | 24.11 | 14.44 | 5.00 | 11.67 | 5.56 | 5.46 | 4.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 51.74 | 21.80 | 10.00 | 7.80 | 13.00 | 7.00 | 5.74 | 2.80 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 65.55 | 21.00 | 8.00 | 9.00 | 12.00 | 7.50 | 7.15 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 133 | 53.21 | 21.03 | 16.50 | 6.34 | 11.57 | 5.80 | 7.80 | 1.69 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 131 | 72.77 | 22.08 | 14.96 | 6.78 | 12.16 | 6.48 | 7.83 | 2.76 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.30 | 25.00 | 14.00 | 12.00 | 11.00 | 5.00 | 8.30 | 0.00 |
| MEAN_REVERT | filtered | 349 | 52.98 | 20.68 | 17.30 | 10.74 | 12.68 | 5.00 | 5.78 | 0.00 |
| MEAN_REVERT | kept | 37 | 71.10 | 24.30 | 15.30 | 12.49 | 13.00 | 5.00 | 5.06 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 351 | 52.06 | 17.76 | 18.04 | 11.86 | 13.12 | 6.09 | 6.37 | 4.48 |
| MOVER_AVWAP_SCALP | kept | 636 | 81.10 | 20.58 | 18.08 | 12.74 | 13.54 | 6.66 | 8.67 | 4.36 |
| MOVER_TREND_PULLBACK | filtered | 3493 | 55.12 | 18.37 | 18.00 | 7.77 | 12.68 | 6.25 | 8.65 | 4.26 |
| MOVER_TREND_PULLBACK | kept | 3813 | 76.18 | 19.50 | 18.06 | 8.23 | 12.41 | 6.61 | 9.04 | 4.26 |
| QUIET_COMPRESSION_BREAK | filtered | 80 | 56.44 | 18.30 | 16.20 | 10.61 | 14.41 | 5.87 | 7.47 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 49 | 75.64 | 19.61 | 17.92 | 12.18 | 14.00 | 7.04 | 9.10 | 0.00 |
| SR_FLIP_RETEST | filtered | 26 | 56.92 | 24.69 | 17.23 | 3.46 | 14.00 | 5.00 | 3.34 | 2.48 |
| SR_FLIP_RETEST | kept | 1 | 66.30 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.30 | 1.00 |
| TREND_PULLBACK_EMA | filtered | 76 | 57.10 | 14.57 | 18.00 | 7.78 | 15.03 | 6.70 | 9.01 | 4.95 |
| TREND_PULLBACK_EMA | kept | 183 | 76.98 | 17.61 | 18.11 | 7.58 | 14.28 | 6.80 | 9.22 | 5.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 59.44 | 17.00 | 17.56 | 12.33 | 14.00 | 6.00 | 8.00 | 4.44 |
| VOLUME_SURGE_BREAKOUT | kept | 22 | 70.30 | 19.95 | 17.36 | 13.09 | 13.73 | 4.77 | 7.74 | 5.05 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 289 | 56.73 | 0.00 | 0.00 | 0.48 | 0.00 | 1.85 | 0.02 | 0.00 | 0.00 | **2.35** |
| DIVERGENCE_CONTINUATION | kept | 151 | 70.19 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.29** |
| FAILED_AUCTION_RECLAIM | filtered | 97 | 51.06 | 0.00 | 0.00 | 6.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.73** |
| FAILED_AUCTION_RECLAIM | kept | 9 | 68.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 51.74 | 0.00 | 0.00 | 3.52 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | **4.72** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 65.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 133 | 53.21 | 0.00 | 0.00 | 2.67 | 0.00 | 0.65 | 0.00 | 0.00 | 0.00 | **3.32** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 131 | 72.77 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 349 | 52.98 | 0.00 | 0.00 | 0.03 | 0.00 | 10.61 | 0.00 | 0.00 | 0.00 | **10.64** |
| MEAN_REVERT | kept | 37 | 71.10 | 0.00 | 0.00 | 0.00 | 0.00 | 3.96 | 0.00 | 0.00 | 0.00 | **3.96** |
| MOVER_AVWAP_SCALP | filtered | 351 | 52.06 | 0.21 | 0.00 | 0.86 | 0.00 | 2.48 | 0.71 | 0.00 | 0.82 | **5.08** |
| MOVER_AVWAP_SCALP | kept | 636 | 81.10 | 0.66 | 0.00 | 0.81 | 0.00 | 0.10 | 0.06 | 0.00 | 0.02 | **1.65** |
| MOVER_TREND_PULLBACK | filtered | 3493 | 55.12 | 0.16 | 0.00 | 1.65 | 0.00 | 0.19 | 0.03 | 0.00 | 0.07 | **2.10** |
| MOVER_TREND_PULLBACK | kept | 3813 | 76.18 | 0.32 | 0.00 | 0.65 | 0.00 | 0.08 | 0.03 | 0.00 | 0.00 | **1.08** |
| QUIET_COMPRESSION_BREAK | filtered | 80 | 56.44 | 0.00 | 0.00 | 3.42 | 0.00 | 0.27 | 0.00 | 0.00 | 1.20 | **4.89** |
| QUIET_COMPRESSION_BREAK | kept | 49 | 75.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.22 | **0.36** |
| SR_FLIP_RETEST | filtered | 26 | 56.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.31 | **5.31** |
| SR_FLIP_RETEST | kept | 1 | 66.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 76 | 57.10 | 0.00 | 0.00 | 4.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.06** |
| TREND_PULLBACK_EMA | kept | 183 | 76.98 | 0.00 | 0.00 | 0.29 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **0.36** |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 59.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 22 | 70.30 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.22** |

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
- Outcomes recorded: **175039 held of 738430 seen** across 21 strategies; 3954 cells past the sample floor; **2075 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47187 | 591/46596/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.40R) |
| MOVER_AVWAP_SCALP | 23104 | 173/22931/0 | 44% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 13545 | 163/13382/0 | 45% | -0.13 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13152 | 156/12996/0 | 39% | -0.26 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11587 | 57/11530/0 | 37% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9738 | 108/9630/0 | 37% | -0.44 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| SHADOW_MEAN_REVERT | 7927 | 0/0/7927 | 43% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (+0.79R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.92R) |
| QUIET_COMPRESSION_BREAK | 7892 | 426/7466/0 | 47% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_RANGE_FADE | 7447 | 0/0/7447 | 36% | -0.12 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.32R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_FUNDING_FADE | 6819 | 0/0/6819 | 35% | -0.40 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| SR_FLIP_RETEST | 5205 | 17/5188/0 | 46% | -0.27 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5015 | 66/4949/0 | 36% | -0.34 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| FUNDING_EXTREME_SIGNAL | 3810 | 2/3808/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3678 | 0/3678/0 | 31% | -0.35 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2194 | 6/2188/0 | 41% | -0.23 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1595 | 0/0/1595 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 182 | 32/150/0 | 43% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 56 | 2/54/0 | 43% | +0.14 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 332 | 27% / -0.58R | 332 | 53% / -0.09R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1065 | 37% / -0.38R | 1065 | 50% / -0.09R | +0.30 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1504 | 43% / -0.36R | 1504 | 57% / -0.12R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 522 | 42% / -0.33R | 522 | 47% / -0.18R | +0.15 | **ATR** |
| MOVER_AVWAP_SCALP | 2383 | 45% / -0.17R | 2383 | 51% / -0.05R | +0.12 | **ATR** |
| MA_CROSS_TREND_SHIFT | 57 | 42% / -0.20R | 57 | 46% / -0.08R | +0.12 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 198 | 37% / -0.17R | 198 | 48% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8611 | 49% / -0.13R | 8611 | 54% / -0.02R | +0.11 | **ATR** |
| RANGE_FADE | 117 | 38% / -0.14R | 117 | 46% / -0.04R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1369 | 41% / -0.21R | 1369 | 44% / -0.11R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1581 | 47% / -0.13R | 1581 | 53% / -0.06R | +0.07 | **ATR** |
| MEAN_REVERT | 403 | 47% / -0.14R | 403 | 46% / -0.16R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1380 | 46% / -0.13R | 1380 | 46% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11536 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2383 | 49% | -0.04R | 233 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 125 | 49% | -0.06R | 67 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1745 | 39% / -0.13R | +0.88 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1401 | 32% / -0.25R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2922 | 35% / -0.23R | +0.61 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10510 | 36% / -0.19R | +0.34 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1837 | 37% / -0.13R | +0.15 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1329 | 36% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1143 | 32% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 292 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 437 | 32% / -0.16R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 337 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 86 | 43% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 468 | 32% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 87 | 28% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×356]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 516/6) (sustained 516 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 516/6) (sustained 516 cycles)
- **ALERT** `tuned_variants` — 867 non-stamps — atr_arm_uncomputable=867 (seen=19257 stamped=1649 skipped=16741) (streak 508/6) (sustained 508 cycles)
- **ALERT** `auto_dispatch` — 110 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=110) (streak 496/3) (sustained 496 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 88840383 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | violating | 1 AI governor paired arms could not be advanced this cycle (0 no candles, 1 bars behind; 27 current): JUPUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 7/12) | 7 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 55 current): JUPUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 7/12) | 7 |
| auto_dispatch | violating | 110 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=110) (streak 496/3) | 496 |
| binance_ip_weight | ok | peak 132/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 80706.00 | 0 |
| candle_coverage | ok | 80/80 symbols with ≥20 15m candles, 80/80 updated within 45m [fresh=80; 75 Tier-1 futures + 5 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 629 dup bars, 0 undedupable; ws 0 out-of-order, 335 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +20 / upstream +28 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1780/1799 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | ok | 83 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1776/1795 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 33633546 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 516/6) | 516 |
| emission_controller | ok | last cycle 361s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×356]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 516/6) | 516 |
| entry_quality_effective | ok | 18747 evaluated, 5944 suppressed, 7506 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,317 reads/day of 50,000 [engine 1,292, signing 25]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4920 sealed bars over 41 symbols; 1215 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +321 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 217697 frozen value(s) avoided; 885202 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.35R over n=4949 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +21 / upstream +321 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 5 held, 5 with scan counts, 4 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 9 locked / 9 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2170 rows held, 3357709 evicted (sampled: execution:trigger_not_confirmed 293/1185480, execution:overextended 293/1052224, setup_compat:regime_STRONG_TREND 292/570721) | 0 |
| price_action_lane | ok | 1196046 evaluated, 1456 emitted; layer1 1456 stamped / 0 blind; cooldown=168220, delta_opposed=108137, no_footprint=440649, no_opposing_target=2168, no_sweep=377404, rr_below_floor=98012 | 0 |
| promoted_pair_integrity | ok | 5/5 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.23R over n=2188 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +26 / upstream +321 | 0 |
| sar_alignment_crosscheck | ok | 712/30750 disagreed (2.3%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +321 | 0 |
| sar_hold_arm | ok | 1860 held arms settled, 140 unscored, 56 still walking (51 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/41 unfetchable (10%); top cause: located bar does not contain the stamp; symbols: BIRBUSDT, BMTUSDT, CAPUSDT, ICNTUSDT | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 55 current): JUPUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 7/12) | 7 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 441 records await one (37 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 4.47s, worst 172.98s over 14837 lifetime cycles; lifetime 357 over 60s, 30 over 120s (plus 1/1 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.5s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 528921 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 4m ago | 0 |
| snapshot_writer | ok | last cycle 3s ago (33.38s to run, worst 148.28s), 1355 overrun(s) of 11212 cycles, TTL 900s; slowest tickers=10.61s, positions_diag=6.8s, signals=4.37s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=106, gate reads=0, withheld=106) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +5 / upstream +321 | 0 |
| structural_snap | ok | 6000/6000 measured, 35 blind, 0 levels moved (refusals: redetect_cooldown=3059) | 0 |
| structural_veto_lane | ok | 4288 stamped; 0 with no readable level book, 78 with clear air ahead, 3156 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +321 / upstream +28 | 0 |
| tuned_variants | violating | 867 non-stamps — atr_arm_uncomputable=867 (seen=19257 stamped=1649 skipped=16741) (streak 508/6) | 508 |
| unlock_shorts | ok | 12 open, 45 scheduled, calendar 2.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 91 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2060642`
- `Path funnel` emissions: `52`
- `Regime distribution` emissions: `52`
- `QUIET_SCALP_BLOCK` events: `154`
- `confidence_gate` events: `9952`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **20**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 9052 | 9234 | 9933 | 0 |
| futures_aggtrade | 3 | 13949 | 13949 | 33645 | 0 |
| futures_depth | 6 | 6543 | 12856 | 32655 | 0 |
| futures_liq | 6 | 3518 | 32432 | 34800 | 0 |
| futures_mover | 1 | 6953 | 6953 | 6953 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=343766] state[populated=343766] buckets[many=343766] sources[none] quality[none]
- funding_rate: presence[absent=35427, present=308339] state[empty=35427, populated=308339] buckets[few=308339, none=35427] sources[none] quality[none]
- liquidation_clusters: presence[absent=192157, present=151609] state[empty=192157, populated=151609] buckets[few=125757, none=192157, some=25852] sources[none] quality[none]
- oi_snapshot: presence[absent=35426, present=308340] state[empty=35426, populated=308340] buckets[few=211, many=307352, none=35426, some=777] sources[none] quality[none]
- order_book: presence[absent=108602, present=235164] state[populated=235164, unavailable=108602] buckets[few=235164, none=108602] sources[book_ticker=235164, unavailable=108602] quality[none=108602, top_of_book_only=235164]
- orderblocks: presence[absent=343766] state[empty=343766] buckets[none=343766] sources[measured_dark=343766] quality[none]
- recent_ticks: presence[present=343766] state[populated=343766] buckets[many=343766] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.13243556022644` sec
- Median create→first breach: `5561.704083442688` sec
- Median create→terminal: `5561.8531230688095` sec
- Median first breach→terminal: `7.605552673339844e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.3}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.494051823857475 | 1.8929700436549766 | 0.7892633213427593 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 0.9888170944365906 | 1.5932467614280128 | 0.6839748109030828 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 3.8973616469540793 | 3.0 | 1.299120548984693 | 1 | 0 |
| MEAN_REVERT | 1 | 1 | 1.3620028907876878 | 1.6686074368023167 | 0.8162512408537509 | 0 | 1 |
| MOVER_AVWAP_SCALP | 6 | 6 | 2.2639505452533943 | 1.9994011862080612 | 0.9040241669606885 | 2 | 4 |
| MOVER_TREND_PULLBACK | 21 | 21 | 3.353592898335346 | 3.0 | 1.1217904616370191 | 12 | 9 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.1220493411830723 | 1.2522105016008613 | 0.8952001617844557 | 0 | 6 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.588063374865419 | 3.0 | 0.8626877916218064 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.3182 | 2021.3002648353577 | 2022.72323679924 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 25.0 | 25.0 | 25.0 | 0.0 | 0.0346 | 9985.796907067299 | 9986.027635097504 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.8974 | 470.37092208862305 | 470.3709969520569 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 6275.165113925934 | 6275.165142059326 |
| MOVER_AVWAP_SCALP | 6 | 6 | 33.3 | 66.7 | 33.3 | 0.0 | -0.4579 | 5359.563955903053 | 5359.564080476761 |
| MOVER_TREND_PULLBACK | 21 | 21 | 33.3 | 38.1 | 33.3 | 0.0 | 0.3683 | 4762.995062828064 | 4765.083743810654 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 22.2 | 55.6 | 22.2 | 0.0 | 0.3178 | 8872.063804149628 | 8872.063882112503 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.8821 | 19656.343386888504 | 19656.99107503891 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 495 | 1 | 417 | 0.0 | 0.0 | None | None | 78 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1842 | 38 | 1361 | 100.0 | 0.0 | 19656.343386888504 | 19656.99107503891 | 481 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `52`
- Gating Δ: `-22410`
- No-generation Δ: `-345840`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 2.5977, "current_avg_pnl": 2.3182, "current_win_rate": 100.0, "previous_avg_pnl": -0.2795, "previous_win_rate": 33.3, "win_rate_delta": 66.7}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.8971, "current_avg_pnl": 0.0346, "current_win_rate": 25.0, "previous_avg_pnl": -0.8625, "previous_win_rate": 0.0, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -2.6056, "current_avg_pnl": -0.4579, "current_win_rate": 33.3, "previous_avg_pnl": 2.1477, "previous_win_rate": 66.7, "win_rate_delta": -33.4}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.2059, "current_avg_pnl": 0.3683, "current_win_rate": 33.3, "previous_avg_pnl": -0.8376, "previous_win_rate": 14.3, "win_rate_delta": 19.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.0279, "current_avg_pnl": 0.3178, "current_win_rate": 22.2, "previous_avg_pnl": 0.3457, "previous_win_rate": 36.4, "win_rate_delta": -14.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -133, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 11, "geometry_changed_delta": 0, "geometry_preserved_delta": 136, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 19656.34, "median_terminal_delta_sec": 19656.99, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
