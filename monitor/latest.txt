# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `2353` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 633 | 633 | 598 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 21573 | 21573 | 20250 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 148381 | 148272 | 143 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 120298 | 120299 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 119999 | 115970 | 4317 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 120320 | 118951 | 1417 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 127254 | 127152 | 122 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 112108 | 112106 | 18 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 120370 | 120394 | 15 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 120414 | 116740 | 5038 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 155991 | 163218 | 1525 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 148419 | 130792 | 25147 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 126299 | 126299 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 120304 | 120314 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 119975 | 119905 | 89 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 121787 | 119654 | 2763 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 119001 | 119722 | 221 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 104873 | 95802 | 9470 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 105280 | 104570 | 762 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 148337 | 148357 | 21 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 112127 | 112141 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6794 | 6794 | 5385 | 9 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 770 | 770 | 405 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 71 | 71 | 42 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 53285 | 53285 | 51506 | 43 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 26 | 26 | 22 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 16630 | 16630 | 11641 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 5099 | 5099 | 4137 | 47 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 78187 | 78187 | 54710 | 349 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 885 | 885 | 785 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 10106 | 10106 | 7874 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 814 | 814 | 714 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2912 | 2912 | 2496 | 30 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 128 | 128 | 65 | 6 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=148272): breakout_not_found=85170, basic_filters_failed=38705, move_not_fresh=16067, breakout_stale=6140, retest_proximity_failed=1691, volume_spike_missing=444, missing_fvg_or_orderblock=38, move_exhausted=17
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=120299): cls_disabled_merged_into_lsr=120299
- **EVAL::DIVERGENCE_CONTINUATION** (total=115970): cvd_divergence_failed=44466, h1_trend_not_aligned=35547, basic_filters_failed=25587, ema_alignment_reject=8531, retest_proximity_failed=1509, missing_fvg_or_orderblock=330
- **EVAL::FAILED_AUCTION_RECLAIM** (total=118951): auction_not_detected=77704, basic_filters_failed=24464, reclaim_hold_failed=5601, tail_too_small=5578, regime_blocked=5404, rsi_reject=200
- **EVAL::FUNDING_EXTREME** (total=127152): funding_not_extreme=96719, basic_filters_failed=26487, missing_funding_rate=2353, ema_alignment_reject=757, rsi_reject=569, momentum_reject=142, cvd_divergence_failed=97, missing_fvg_or_orderblock=28
- **EVAL::LIQUIDATION_REVERSAL** (total=112106): cascade_threshold_not_met=83845, basic_filters_failed=27083, cvd_divergence_failed=588, rsi_reject=572, missing_fvg_or_orderblock=15, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=120394): no_ma_cross=92144, basic_filters_failed=25596, ma_cross_cooldown=2089, ma_cross_htf_misaligned=565
- **EVAL::MEAN_REVERT** (total=116740): no_extension=92367, basic_filters_failed=24373
- **EVAL::MOVER_AVWAP_SCALP** (total=163218): no_avwap_tag=66257, basic_filters_failed=38862, no_mover_leg=35042, avwap_slope_against=14741, avwap_reclaim_no_volume=5069, no_avwap_reclaim=3208, anchor_too_recent=39
- **EVAL::MOVER_TREND_PULLBACK** (total=130792): mover_run_too_small=55346, basic_filters_failed=38781, no_reclaim=31886, no_pullback_tag=4779
- **EVAL::OPENING_RANGE_BREAKOUT** (total=126299): feature_disabled=126299
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=120314): regime_blocked=94955, breakout_not_found=19603, basic_filters_failed=4931, adx_reject=801, ema_alignment_reject=24
- **EVAL::QUIET_COMPRESSION_BREAK** (total=119905): compression_not_detected=62643, regime_blocked=30698, basic_filters_failed=19525, breakout_not_detected=6228, volume_confirmation_failed=692, rsi_reject=84, macd_reject=32, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=119654): no_range_edge=95278, basic_filters_failed=24376
- **EVAL::SR_FLIP_RETEST** (total=119722): flip_close_not_confirmed=77855, basic_filters_failed=24443, regime_blocked=5382, long_break_volume_thin=4925, retest_out_of_zone=2777, h1_break_not_confirmed=2314, reclaim_hold_failed=1317, ema_alignment_reject=254, whipsaw_flip=185, wick_quality_failed=121, long_acceptance_not_held=100, missing_fvg_or_orderblock=49
- **EVAL::STANDARD** (total=95802): adx_reject=21841, momentum_reject=19643, basic_filters_failed=19153, macd_reject=13819, sweeps_not_detected=12162, ema_alignment_reject=6687, htf_poi_unanchored=2175, invalid_sl_geometry=258, rsi_reject=64
- **EVAL::TREND_PULLBACK** (total=104570): h1_trend_not_aligned=39031, ema_alignment_reject=18336, basic_filters_failed=13615, h1_pullback_not_confirmed=11790, ema_not_tested_prev=8135, no_ema_reclaim_close=5845, body_conviction_fail=3344, rsi_reject=2203, prev_already_above_emas=637, prev_already_below_emas=588, no_prev_low_break=420, no_prev_high_break=366, momentum_flat=149, ema21_not_tagged=71, missing_fvg_or_orderblock=25, momentum_reject=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=148357): breakout_not_found=84610, basic_filters_failed=38703, move_not_fresh=15302, breakout_stale=6801, retest_proximity_failed=2420, volume_spike_missing=457, missing_fvg_or_orderblock=53, move_exhausted=11
- **EVAL::WHALE_MOMENTUM** (total=112141): momentum_reject=80414, recent_ticks_insufficient=25797, basic_filters_failed=5930

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=233): execution:overextended=233
- **DIVERGENCE_CONTINUATION** (total=1326): setup_compat:regime_VOLATILE_UNSUITABLE=1118, setup_compat:regime_BREAKOUT_EXPANSION=208
- **FAILED_AUCTION_RECLAIM** (total=2407): execution:overextended=1092, setup_compat:regime_STRONG_TREND=799, context_floor=423, setup_compat:regime_VOLATILE_UNSUITABLE=93
- **FUNDING_EXTREME_SIGNAL** (total=592): execution:trigger_not_confirmed=567, context_floor=25
- **LIQUIDATION_REVERSAL** (total=71): execution:trigger_not_confirmed=71
- **LIQUIDITY_SWEEP_REVERSAL** (total=13467): execution:overextended=5566, execution:trigger_not_confirmed=4525, setup_compat:regime_STRONG_TREND=3376
- **MA_CROSS_TREND_SHIFT** (total=33): setup_compat:regime_DIRTY_RANGE=13, execution:trigger_not_confirmed=8, setup_compat:regime_CLEAN_RANGE=6, execution:overextended=5, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=7624): setup_compat:regime_STRONG_TREND=4083, setup_compat:regime_WEAK_TREND=2024, execution:overextended=1492, entry_quality=25
- **MOVER_AVWAP_SCALP** (total=2884): execution:overextended=2290, execution:trigger_not_confirmed=366, entry_quality=228
- **MOVER_TREND_PULLBACK** (total=35983): execution:trigger_not_confirmed=18538, execution:overextended=14083, entry_quality=3362
- **RANGE_FADE** (total=6108): setup_compat:regime_STRONG_TREND=2259, setup_compat:regime_WEAK_TREND=1583, setup_compat:regime_VOLATILE_UNSUITABLE=1219, execution:overextended=917, setup_compat:regime_BREAKOUT_EXPANSION=113, context_edge=17
- **TREND_PULLBACK_EMA** (total=2790): setup_compat:regime_CLEAN_RANGE=1707, setup_compat:regime_DIRTY_RANGE=789, setup_compat:regime_VOLATILE_UNSUITABLE=148, entry_quality=146
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 510013 | 59.5% |
| QUIET | 109724 | 12.8% |
| TRENDING_UP | 96624 | 11.3% |
| TRENDING_DOWN | 94980 | 11.1% |
| VOLATILE | 46026 | 5.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **138**
- Average confidence gap to threshold: **9.83** (samples=138) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=32, TRUMPUSDT=23, ZROUSDT=16, FILUSDT=12, SOLUSDT=7, BNBUSDT=7, 1000PEPEUSDT=6, ETHUSDT=6, APTUSDT=5, COTIUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 230 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 21 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 311 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 42 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 379 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 14 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 191 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 20 |
| MEAN_REVERT | kept | min_confidence_pass | 29 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 108 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 330 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3229 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 74 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 7080 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 21 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | filtered | min_confidence | 34 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 44 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 8 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 79 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 57 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 65.00 | 65.00 | 0.00 | 20.05 | 17.80 | 20.00 | 3.50 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 232 | 56.06 | 64.46 | 8.40 | 21.12 | 19.49 | 17.88 | 2.28 | 9.50 |
| DIVERGENCE_CONTINUATION | kept | 21 | 66.76 | 65.00 | -1.76 | 20.75 | 19.39 | 18.53 | 1.90 | 4.83 |
| FAILED_AUCTION_RECLAIM | filtered | 324 | 52.67 | 64.37 | 11.70 | 21.06 | 18.76 | 20.00 | 2.40 | 16.71 |
| FAILED_AUCTION_RECLAIM | kept | 42 | 70.47 | 65.00 | -5.47 | 22.18 | 19.54 | 20.00 | 4.58 | 2.31 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 51.30 | 61.00 | 9.70 | 17.58 | 20.00 | 18.20 | 0.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 63.35 | 65.00 | 1.65 | 20.60 | 13.70 | 18.50 | 3.00 | 8.40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 393 | 56.52 | 64.30 | 7.78 | 20.18 | 18.32 | 18.58 | 3.13 | 12.77 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 191 | 70.49 | 65.00 | -5.49 | 20.95 | 17.61 | 17.78 | 2.58 | 0.80 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.00 | 65.00 | -5.00 | 21.05 | 19.20 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 20 | 58.60 | 65.00 | 6.40 | 19.56 | 18.85 | 13.40 | 0.00 | 15.90 |
| MEAN_REVERT | kept | 29 | 72.86 | 65.00 | -7.86 | 21.46 | 15.92 | 14.39 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 108 | 60.26 | 64.70 | 4.44 | 20.44 | 17.75 | 15.80 | 4.51 | 6.31 |
| MOVER_AVWAP_SCALP | kept | 330 | 76.90 | 65.00 | -11.90 | 20.29 | 15.03 | 15.80 | 4.07 | 2.39 |
| MOVER_TREND_PULLBACK | filtered | 3303 | 57.75 | 64.18 | 6.43 | 20.13 | 18.29 | 15.80 | 3.82 | 15.64 |
| MOVER_TREND_PULLBACK | kept | 7080 | 76.21 | 65.00 | -11.21 | 20.31 | 18.73 | 15.80 | 3.98 | 1.57 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.00 | 65.00 | -19.00 | 21.30 | 20.00 | 16.90 | 4.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 48 | 55.16 | 65.00 | 9.84 | 21.83 | 19.45 | 20.00 | 0.00 | 11.45 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 73.57 | 65.00 | -8.57 | 20.63 | 18.93 | 20.00 | 0.00 | 1.45 |
| SR_FLIP_RETEST | filtered | 34 | 56.36 | 63.35 | 6.99 | 20.64 | 20.00 | 15.20 | 1.00 | 12.76 |
| SR_FLIP_RETEST | kept | 3 | 69.87 | 65.00 | -4.87 | 21.47 | 20.00 | 16.80 | 2.33 | 4.00 |
| TREND_PULLBACK_EMA | filtered | 52 | 59.53 | 65.00 | 5.47 | 19.68 | 19.57 | 17.39 | 4.59 | 16.45 |
| TREND_PULLBACK_EMA | kept | 79 | 81.98 | 65.00 | -16.98 | 21.85 | 19.75 | 16.93 | 4.68 | -1.17 |
| VOLUME_SURGE_BREAKOUT | filtered | 57 | 47.55 | 65.00 | 17.45 | 20.80 | 18.80 | 20.00 | 3.92 | 11.81 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 73.63 | 65.00 | -8.63 | 19.50 | 17.20 | 20.00 | 4.25 | 2.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 65.00 | 17.00 | 14.00 | 12.00 | 12.50 | 5.00 | 5.50 | 3.50 |
| DIVERGENCE_CONTINUATION | filtered | 232 | 56.06 | 23.00 | 9.72 | 6.54 | 12.07 | 5.91 | 9.01 | 2.28 |
| DIVERGENCE_CONTINUATION | kept | 21 | 66.76 | 25.00 | 12.76 | 7.14 | 10.33 | 5.52 | 9.20 | 1.90 |
| FAILED_AUCTION_RECLAIM | filtered | 324 | 52.67 | 20.26 | 16.74 | 7.02 | 13.98 | 6.63 | 4.10 | 2.40 |
| FAILED_AUCTION_RECLAIM | kept | 42 | 70.47 | 24.24 | 15.62 | 5.00 | 12.45 | 5.32 | 5.57 | 4.58 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 51.30 | 17.00 | 20.00 | 3.00 | 14.00 | 10.00 | 2.30 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 63.35 | 25.00 | 14.00 | 4.50 | 10.50 | 8.75 | 6.00 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 393 | 56.52 | 24.41 | 14.00 | 5.73 | 11.88 | 5.69 | 4.46 | 3.13 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 191 | 70.49 | 24.50 | 14.44 | 5.61 | 13.24 | 5.91 | 5.09 | 2.58 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.00 | 21.00 | 14.00 | 7.50 | 12.50 | 5.00 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 20 | 58.60 | 23.20 | 16.00 | 15.00 | 12.00 | 5.00 | 3.30 | 0.00 |
| MEAN_REVERT | kept | 29 | 72.86 | 18.93 | 18.00 | 10.14 | 13.14 | 5.00 | 7.65 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 108 | 60.26 | 16.93 | 18.00 | 10.88 | 14.38 | 6.38 | 6.48 | 4.51 |
| MOVER_AVWAP_SCALP | kept | 330 | 76.90 | 18.78 | 18.01 | 12.47 | 13.55 | 7.30 | 7.75 | 4.07 |
| MOVER_TREND_PULLBACK | filtered | 3303 | 57.75 | 17.47 | 18.01 | 7.87 | 12.32 | 6.38 | 8.45 | 3.82 |
| MOVER_TREND_PULLBACK | kept | 7080 | 76.21 | 19.75 | 18.02 | 7.75 | 12.74 | 6.55 | 9.15 | 3.98 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.00 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 7.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 48 | 55.16 | 18.67 | 16.25 | 9.12 | 14.38 | 7.70 | 3.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 73.57 | 18.33 | 16.67 | 12.00 | 14.50 | 8.50 | 7.62 | 0.00 |
| SR_FLIP_RETEST | filtered | 34 | 56.36 | 17.00 | 18.00 | 8.82 | 17.00 | 5.00 | 2.30 | 1.00 |
| SR_FLIP_RETEST | kept | 3 | 69.87 | 22.33 | 18.00 | 5.00 | 16.00 | 5.00 | 5.20 | 2.33 |
| TREND_PULLBACK_EMA | filtered | 52 | 59.53 | 16.13 | 18.00 | 7.76 | 12.71 | 7.06 | 9.77 | 4.59 |
| TREND_PULLBACK_EMA | kept | 79 | 81.98 | 20.24 | 18.00 | 7.61 | 15.75 | 7.89 | 8.88 | 4.68 |
| VOLUME_SURGE_BREAKOUT | filtered | 57 | 47.55 | 18.54 | 15.40 | 12.00 | 15.05 | 5.00 | 4.44 | 3.92 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 73.63 | 14.50 | 16.33 | 13.00 | 13.00 | 5.50 | 9.55 | 4.25 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.00 | **3.00** |
| DIVERGENCE_CONTINUATION | filtered | 232 | 56.06 | 0.00 | 0.00 | 2.86 | 0.00 | 0.83 | 0.00 | 0.00 | 0.00 | **3.69** |
| DIVERGENCE_CONTINUATION | kept | 21 | 66.76 | 0.00 | 0.00 | 2.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.29** |
| FAILED_AUCTION_RECLAIM | filtered | 324 | 52.67 | 0.00 | 0.00 | 0.00 | 0.00 | 2.25 | 0.00 | 0.00 | 0.00 | **2.25** |
| FAILED_AUCTION_RECLAIM | kept | 42 | 70.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 51.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 63.35 | 0.00 | 0.00 | 8.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.40** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 393 | 56.52 | 0.00 | 0.00 | 1.38 | 0.00 | 1.29 | 0.00 | 0.00 | 0.00 | **2.67** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 191 | 70.49 | 0.00 | 0.00 | 0.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.84** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 20 | 58.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 29 | 72.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 108 | 60.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.44 | 0.00 | 0.00 | 0.50 | **0.94** |
| MOVER_AVWAP_SCALP | kept | 330 | 76.90 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.85 | **0.86** |
| MOVER_TREND_PULLBACK | filtered | 3303 | 57.75 | 0.02 | 0.00 | 2.10 | 0.00 | 0.26 | 0.00 | 0.00 | 0.01 | **2.39** |
| MOVER_TREND_PULLBACK | kept | 7080 | 76.21 | 0.00 | 0.00 | 0.50 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.60** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 48 | 55.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.55 | **5.55** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 73.57 | 0.00 | 0.00 | 0.00 | 0.00 | 1.83 | 0.00 | 0.00 | 0.00 | **1.83** |
| SR_FLIP_RETEST | filtered | 34 | 56.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 3 | 69.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 52 | 59.53 | 0.00 | 0.00 | 0.83 | 0.00 | 2.08 | 0.00 | 0.00 | 0.00 | **2.91** |
| TREND_PULLBACK_EMA | kept | 79 | 81.98 | 0.00 | 0.00 | 0.28 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | **0.71** |
| VOLUME_SURGE_BREAKOUT | filtered | 57 | 47.55 | 0.00 | 0.00 | 3.65 | 0.00 | 1.51 | 0.00 | 0.00 | 1.16 | **6.32** |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 73.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **111403 held of 312602 seen** across 21 strategies; 2539 cells past the sample floor; **1160 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 38689 | 564/38125/0 | 45% | -0.15 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+1.20R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.22R) |
| MOVER_AVWAP_SCALP | 14001 | 200/13801/0 | 41% | -0.26 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 8487 | 107/8380/0 | 44% | -0.14 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+1.75R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 7120 | 40/7080/0 | 51% | +0.03 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 6044 | 0/0/6044 | 43% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.84R) |
| TREND_PULLBACK_EMA | 5541 | 24/5517/0 | 45% | -0.15 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 5187 | 0/0/5187 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.17R) |
| QUIET_COMPRESSION_BREAK | 4985 | 292/4693/0 | 47% | -0.12 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4714 | 0/0/4714 | 34% | -0.41 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 3505 | 64/3441/0 | 39% | -0.34 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.93R) | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.24R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2233 | 30/2203/0 | 49% | -0.11 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1919 | 2/1917/0 | 32% | -0.44 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1856 | 0/1856/0 | 39% | -0.09 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1262 | 12/1250/0 | 50% | -0.17 | ASIA/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.80R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 895 | 0/0/895 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.16R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 753 | 0/753/0 | 39% | -0.40 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 537 | 49/488/0 | 33% | -0.32 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 64 | 8/56/0 | 47% | -0.02 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 145 | 28% / -0.55R | 145 | 47% / -0.19R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 466 | 43% / -0.24R | 466 | 55% / -0.04R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 1114 | 44% / -0.20R | 1114 | 50% / -0.08R | +0.12 | **ATR** |
| BREAKDOWN_SHORT | 42 | 38% / -0.20R | 42 | 43% / -0.09R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 139 | 48% / -0.27R | 139 | 50% / -0.17R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 5999 | 50% / -0.10R | 5999 | 55% / -0.01R | +0.09 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 714 | 49% / -0.22R | 714 | 56% / -0.13R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 787 | 43% / -0.18R | 787 | 46% / -0.10R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 102 | 39% / -0.11R | 102 | 47% / -0.05R | +0.06 | **ATR** |
| RANGE_FADE | 38 | 37% / -0.26R | 38 | 39% / -0.29R | -0.02 | **FIXED** |
| DIVERGENCE_CONTINUATION | 657 | 51% / -0.05R | 657 | 57% / -0.03R | +0.02 | **ATR** |
| MEAN_REVERT | 162 | 54% / -0.05R | 162 | 52% / -0.04R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 797 | 45% / -0.16R | 797 | 45% / -0.17R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 20 | 40% / -0.15R | 20 | 40% / -0.14R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8597 | 29% | -0.25R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1114 | 48% | -0.07R | 195 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 63 | 51% | -0.04R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 771 | 36% / -0.12R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7686 | 36% / -0.17R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1485 | 35% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 634 | 35% / -0.14R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 747 | 41% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 619 | 38% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 714 | 42% / -0.14R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 145 | 28% / -0.45R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 191 | 30% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 134 | 56% / +0.14R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 75 | 43% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 30 | 33% / +0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 143 | 36% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 30 | 20% / -0.38R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 10 | 40% / +0.02R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 59 · alerting: **1** · boot grace active: False
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 116/6) (sustained 116 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 12146733 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | violating | 1 AI governor paired arms could not be advanced this cycle (0 no candles, 1 bars behind; 22 current): CFGUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 3/12) | 3 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 36 current): CFGUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 3/12) | 3 |
| auto_dispatch | ok | 28 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=56. No user is on live. | 0 |
| binance_ip_weight | ok | peak 421/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 84184.30 | 0 |
| candle_coverage | ok | 92/92 symbols with ≥20 15m candles, 92/92 updated within 45m [fresh=92; 72 Tier-1 futures + 20 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 464 dup bars, 0 undedupable; ws 0 out-of-order, 63 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +119 / upstream +44 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1172/1189 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 115 open dark rows are not being advanced (worst: STABLEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 46/120) | 46 |
| dark_sar_arms | ok | no open arms; covering 1170/1187 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3209109 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 116/6) | 116 |
| emission_controller | ok | last cycle 647s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 5265 stamps (MEAN_REVERT=297, MOVER_AVWAP_SCALP=175, MOVER_TREND_PULLBACK=4527, TREND_PULLBACK_EMA=266), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,362 reads/day of 50,000 [engine 1,362, signing 0]; top site keystore.roster_doc at 288/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +12 / upstream +302 | 0 |
| indicator_cache_key | ok | 23256 frozen value(s) avoided; 244928 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.11R over n=2203 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +21 / upstream +302 | 0 |
| mover_admission_metadata | ok | 907 symbols known, 201 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 20 held, 20 with scan counts, 19 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1835154 evicted (sampled: execution:trigger_not_confirmed 400/676766, execution:overextended 400/613393, setup_compat:regime_STRONG_TREND 400/269891) | 0 |
| price_action_lane | ok | 403700 evaluated, 317 emitted; layer1 317 stamped / 0 blind; cooldown=55318, delta_opposed=39755, no_footprint=165413, no_opposing_target=28, no_sweep=106670, rr_below_floor=36199 | 0 |
| promoted_pair_integrity | ok | 20/20 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.40R over n=753 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | violating | upstream +302 but output +0 (streak 13/72) | 13 |
| sar_alignment_crosscheck | ok | 137/9299 disagreed (1.5%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +302 | 0 |
| sar_hold_arm | ok | 1830 held arms settled, 170 unscored, 37 still walking (31 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 10/56 unfetchable (18%); top cause: gap or duplicate bar in the 15m window; symbols: 1000PEPEUSDT, BRUSDT, HBARUSDT, MARSCOINUSDT, MUBARAKUSDT +1 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 36 current): CFGUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 3/12) | 3 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 456 records await one (46 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 11.32s, worst 74.27s over 4548 lifetime cycles; lifetime 4 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.56s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 190331 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 30s ago (0.38s to run, worst 66.1s), 121 overrun(s) of 2623 cycles, TTL 900s; slowest engine_state=6.22s, positions_diag=2.01s, signals=1.33s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +46 / upstream +302 | 0 |
| structural_snap | ok | 5536/5536 measured, 25 blind, 0 levels moved (refusals: redetect_cooldown=740) | 0 |
| structural_veto_lane | ok | 1040 stamped; 0 with no readable level book, 9 with clear air ahead, 696 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +302 / upstream +44 | 0 |
| tuned_variants | ok | seen=5598 stamped=426 skipped=5172, residue 0 (none recorded) | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 2 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4238390`
- `Path funnel` emissions: `99`
- `Regime distribution` emissions: `99`
- `QUIET_SCALP_BLOCK` events: `138`
- `confidence_gate` events: `12370`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=700834] state[populated=700834] buckets[many=700834] sources[none] quality[none]
- funding_rate: presence[absent=95313, present=605521] state[empty=95313, populated=605521] buckets[few=605521, none=95313] sources[none] quality[none]
- liquidation_clusters: presence[absent=367874, present=332960] state[empty=367874, populated=332960] buckets[few=257628, none=367874, some=75332] sources[none] quality[none]
- oi_snapshot: presence[absent=91936, present=608898] state[empty=91936, populated=608898] buckets[many=608898, none=91936] sources[none] quality[none]
- order_book: presence[absent=180800, present=520034] state[populated=520034, unavailable=180800] buckets[few=520034, none=180800] sources[book_ticker=520034, unavailable=180800] quality[none=180800, top_of_book_only=520034]
- orderblocks: presence[absent=700834] state[empty=700834] buckets[none=700834] sources[measured_dark=700834] quality[none]
- recent_ticks: presence[present=700834] state[populated=700834] buckets[many=700834] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.869873046875` sec
- Median create→first breach: `4643.196774959564` sec
- Median create→terminal: `4643.539532184601` sec
- Median first breach→terminal: `7.295608520507812e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 1.2634413939823677 | 1.4278466333260857 | 0.8848579143540468 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 1.5828163251079195 | 2.231550174373089 | 0.8402092732257727 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 8 | 8 | 1.1362423236378745 | 1.5166438201612777 | 0.7042940236656616 | 0 | 8 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 2.8817465070196553 | 2.7880935907030646 | 1.0335903058020999 | 1 | 0 |
| MOVER_AVWAP_SCALP | 6 | 6 | 2.094311661823364 | 2.566783916610854 | 0.8632162422279153 | 0 | 6 |
| MOVER_TREND_PULLBACK | 36 | 36 | 4.270811524164783 | 3.0 | 1.5241184871199494 | 28 | 8 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 1.3939913715296175 | 1.5162830160846121 | 0.8806052580029526 | 0 | 6 |
| SR_FLIP_RETEST | 1 | 1 | 1.8688138908366407 | 2.1591149413133155 | 0.8655462731872465 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 7570.595968008041 | 7570.595992088318 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 0.0 | 75.0 | 0.0 | 0.0 | -1.674 | 6643.169344425201 | 6643.169371366501 |
| LIQUIDITY_SWEEP_REVERSAL | 8 | 8 | 0.0 | 62.5 | 0.0 | 0.0 | -1.0441 | 1666.7156480550766 | 1666.7156945466995 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.5903 | 3515.4164209365845 | 3516.3101320266724 |
| MOVER_AVWAP_SCALP | 6 | 6 | 16.7 | 66.7 | 16.7 | 0.0 | -0.9484 | 14237.468179941177 | 14237.468256354332 |
| MOVER_TREND_PULLBACK | 36 | 36 | 44.4 | 33.3 | 44.4 | 0.0 | 0.8007 | 3593.081761598587 | 3593.0818390846252 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 12.5 | 62.5 | 12.5 | 0.0 | -0.6021 | 13901.690144062042 | 13901.690173983574 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.8688 | 4665.448423862457 | 4665.448725938797 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 814 | 3 | 714 | 0.0 | 100.0 | 4665.448423862457 | 4665.448725938797 | 100 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2912 | 30 | 2496 | 0.0 | 0.0 | None | None | 416 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `237`
- Gating Δ: `-27575`
- No-generation Δ: `321571`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.674, "current_avg_pnl": -1.674, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -1.0441, "current_avg_pnl": -1.0441, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -3.5467, "current_avg_pnl": -0.9484, "current_win_rate": 16.7, "previous_avg_pnl": 2.5983, "previous_win_rate": 80.0, "win_rate_delta": -63.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9963, "current_avg_pnl": 0.8007, "current_win_rate": 44.4, "previous_avg_pnl": -0.1956, "previous_win_rate": 30.2, "win_rate_delta": 14.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.7448, "current_avg_pnl": -0.6021, "current_win_rate": 12.5, "previous_avg_pnl": 0.1427, "previous_win_rate": 25.0, "win_rate_delta": -12.5}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 74, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 4665.45, "median_terminal_delta_sec": 4665.45, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 25, "geometry_changed_delta": 0, "geometry_preserved_delta": 352, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
