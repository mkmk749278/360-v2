# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `542` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 213 | 213 | 213 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 26105 | 26105 | 25037 | 12 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 154075 | 153985 | 116 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 136745 | 136745 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 136412 | 130091 | 6635 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 136782 | 135624 | 1214 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 139362 | 139250 | 125 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 125849 | 125859 | 9 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 136844 | 136872 | 12 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 136884 | 131315 | 7439 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 160599 | 166970 | 1487 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 154107 | 139044 | 21517 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 138751 | 138751 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 136750 | 136690 | 85 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 136396 | 136174 | 235 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 138760 | 133188 | 7750 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 135770 | 136171 | 203 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 122833 | 114586 | 8465 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 123058 | 122254 | 859 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 154041 | 153926 | 147 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 125870 | 125885 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7434 | 7434 | 7051 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1600 | 1600 | 974 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 46 | 46 | 18 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 45299 | 45299 | 43821 | 18 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 7 | 3 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 24695 | 24695 | 22344 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4527 | 4527 | 2211 | 40 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 77658 | 77658 | 58755 | 187 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 431 | 431 | 404 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1321 | 1321 | 1245 | 21 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 29647 | 29647 | 28705 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1085 | 1085 | 562 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4297 | 4297 | 3977 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 418 | 418 | 212 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=153985): breakout_not_found=86254, basic_filters_failed=32754, move_not_fresh=28243, breakout_stale=5051, retest_proximity_failed=1456, volume_spike_missing=200, move_exhausted=17, missing_fvg_or_orderblock=10
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=136745): cls_disabled_merged_into_lsr=136745
- **EVAL::DIVERGENCE_CONTINUATION** (total=130091): cvd_divergence_failed=65993, h1_trend_not_aligned=29304, basic_filters_failed=22785, ema_alignment_reject=8997, retest_proximity_failed=2281, missing_fvg_or_orderblock=731
- **EVAL::FAILED_AUCTION_RECLAIM** (total=135624): auction_not_detected=98129, basic_filters_failed=21758, reclaim_hold_failed=7577, tail_too_small=4800, regime_blocked=3312, rsi_reject=48
- **EVAL::FUNDING_EXTREME** (total=139250): funding_not_extreme=111531, basic_filters_failed=23912, missing_funding_rate=1598, ema_alignment_reject=1341, rsi_reject=606, momentum_reject=124, cvd_divergence_failed=119, missing_fvg_or_orderblock=19
- **EVAL::LIQUIDATION_REVERSAL** (total=125859): cascade_threshold_not_met=100018, basic_filters_failed=24122, rsi_reject=824, cvd_divergence_failed=798, missing_fvg_or_orderblock=74, volume_spike_missing=23
- **EVAL::MA_CROSS_TREND_SHIFT** (total=136872): no_ma_cross=111008, basic_filters_failed=22795, ma_cross_cooldown=2134, ma_cross_htf_misaligned=935
- **EVAL::MEAN_REVERT** (total=131315): no_extension=116511, basic_filters_failed=14804
- **EVAL::MOVER_AVWAP_SCALP** (total=166970): no_avwap_tag=76596, no_mover_leg=44515, basic_filters_failed=32882, avwap_slope_against=6832, avwap_reclaim_no_volume=3479, no_avwap_reclaim=2638, anchor_too_recent=28
- **EVAL::MOVER_TREND_PULLBACK** (total=139044): mover_run_too_small=75083, basic_filters_failed=32824, no_reclaim=27307, no_pullback_tag=3830
- **EVAL::OPENING_RANGE_BREAKOUT** (total=138751): feature_disabled=138751
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=136690): regime_blocked=79124, breakout_not_found=46402, basic_filters_failed=7088, adx_reject=4004, ema_alignment_reject=46, rsi_reject=26
- **EVAL::QUIET_COMPRESSION_BREAK** (total=136174): regime_blocked=60824, compression_not_detected=48780, basic_filters_failed=14661, breakout_not_detected=10519, volume_confirmation_failed=1084, rsi_reject=262, macd_reject=27, missing_fvg_or_orderblock=17
- **EVAL::RANGE_FADE** (total=133188): no_range_edge=118382, basic_filters_failed=14806
- **EVAL::SR_FLIP_RETEST** (total=136171): flip_close_not_confirmed=96578, basic_filters_failed=21740, h1_break_not_confirmed=5113, retest_out_of_zone=4257, regime_blocked=3308, long_break_volume_thin=3168, reclaim_hold_failed=988, ema_alignment_reject=384, wick_quality_failed=268, long_acceptance_not_held=200, whipsaw_flip=142, missing_fvg_or_orderblock=25
- **EVAL::STANDARD** (total=114586): momentum_reject=43259, adx_reject=19861, sweeps_not_detected=14584, basic_filters_failed=12089, ema_alignment_reject=11611, macd_reject=10574, htf_poi_unanchored=2254, rsi_reject=183, invalid_sl_geometry=167, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=122254): h1_trend_not_aligned=33132, ema_alignment_reject=18246, h1_pullback_not_confirmed=17709, ema_not_tested_prev=14690, basic_filters_failed=11137, no_ema_reclaim_close=10442, body_conviction_fail=6793, rsi_reject=6482, prev_already_below_emas=1920, no_prev_low_break=1140, prev_already_above_emas=197, momentum_flat=123, missing_fvg_or_orderblock=94, ema21_not_tagged=70, no_prev_high_break=62, momentum_reject=17
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=153926): breakout_not_found=92247, basic_filters_failed=32751, move_not_fresh=20230, breakout_stale=5683, retest_proximity_failed=2656, volume_spike_missing=351, missing_fvg_or_orderblock=8
- **EVAL::WHALE_MOMENTUM** (total=125885): momentum_reject=92394, recent_ticks_insufficient=28298, basic_filters_failed=5193

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=6): execution:overextended=6
- **DIVERGENCE_CONTINUATION** (total=332): setup_compat:regime_VOLATILE_UNSUITABLE=292, setup_compat:regime_BREAKOUT_EXPANSION=34, execution:overextended=6
- **FAILED_AUCTION_RECLAIM** (total=3934): setup_compat:regime_STRONG_TREND=2306, execution:overextended=1498, context_floor=130
- **FUNDING_EXTREME_SIGNAL** (total=1423): execution:trigger_not_confirmed=1422, context_floor=1
- **LIQUIDATION_REVERSAL** (total=46): execution:trigger_not_confirmed=46
- **LIQUIDITY_SWEEP_REVERSAL** (total=12911): execution:trigger_not_confirmed=5750, setup_compat:regime_STRONG_TREND=4687, execution:overextended=2474
- **MA_CROSS_TREND_SHIFT** (total=10): setup_compat:regime_CLEAN_RANGE=4, execution:trigger_not_confirmed=2, execution:overextended=2, setup_compat:regime_DIRTY_RANGE=2
- **MEAN_REVERT** (total=16669): setup_compat:regime_STRONG_TREND=9584, setup_compat:regime_WEAK_TREND=5983, execution:overextended=1053, entry_quality=49
- **MOVER_AVWAP_SCALP** (total=2606): execution:overextended=1537, execution:trigger_not_confirmed=542, entry_quality=527
- **MOVER_TREND_PULLBACK** (total=28429): execution:overextended=13310, execution:trigger_not_confirmed=12920, entry_quality=2199
- **POST_DISPLACEMENT_CONTINUATION** (total=23): execution:overextended=23
- **QUIET_COMPRESSION_BREAK** (total=21): execution:trigger_not_confirmed=21
- **RANGE_FADE** (total=23246): setup_compat:regime_STRONG_TREND=10370, setup_compat:regime_WEAK_TREND=6685, execution:overextended=5982, setup_compat:regime_VOLATILE_UNSUITABLE=204, setup_compat:regime_BREAKOUT_EXPANSION=5
- **TREND_PULLBACK_EMA** (total=3864): setup_compat:regime_CLEAN_RANGE=2616, setup_compat:regime_DIRTY_RANGE=1093, setup_compat:regime_VOLATILE_UNSUITABLE=106, entry_quality=49
- **VOLUME_SURGE_BREAKOUT** (total=158): execution:overextended=158

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 268481 | 29.7% |
| TRENDING_DOWN | 206506 | 22.9% |
| QUIET | 202799 | 22.5% |
| TRENDING_UP | 194552 | 21.6% |
| VOLATILE | 30173 | 3.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **92**
- Average confidence gap to threshold: **19.34** (samples=92) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BATUSDT=18, BZUSDT=16, ETHUSDT=12, SPCXUSDT=7, HBARUSDT=7, PUMPUSDT=6, SUIUSDT=4, AAVEUSDT=4, ENAUSDT=3, SANDUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 287 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 78 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 105 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 7 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 26 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 18 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 409 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 95 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | min_confidence | 82 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 51 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 262 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 44 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1063 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3389 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 44 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3996 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 26 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 18 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 21 |
| SR_FLIP_RETEST | filtered | min_confidence | 39 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 8 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 171 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 36 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 131 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 36 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 288 | 55.52 | 64.48 | 8.96 | 19.44 | 19.75 | 17.36 | 0.67 | 11.88 |
| DIVERGENCE_CONTINUATION | kept | 78 | 67.09 | 65.00 | -2.09 | 19.01 | 19.68 | 18.72 | -0.10 | 1.02 |
| FAILED_AUCTION_RECLAIM | filtered | 112 | 50.66 | 64.30 | 13.64 | 21.26 | 18.06 | 20.00 | 1.51 | 6.59 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 68.95 | 65.00 | -3.95 | 20.05 | 20.00 | 20.00 | 3.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 47.21 | 63.34 | 16.13 | 19.85 | 14.00 | 17.00 | 3.34 | 13.11 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.80 | 65.00 | -6.80 | 17.10 | 14.00 | 17.00 | 5.00 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 18 | 72.87 | 10.00 | -62.87 | 21.20 | 8.30 | 15.60 | 6.67 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 419 | 49.81 | 64.12 | 14.31 | 19.96 | 18.98 | 18.24 | 1.71 | 6.30 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 70.60 | 65.00 | -5.60 | 20.77 | 19.60 | 18.89 | 1.73 | -0.28 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 54.50 | 61.00 | 6.50 | 21.20 | 17.70 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 67.83 | 65.00 | -2.83 | 21.15 | 17.00 | 15.80 | 0.00 | 2.25 |
| MEAN_REVERT | filtered | 83 | 61.94 | 64.42 | 2.48 | 22.19 | 14.76 | 16.57 | 0.00 | 7.94 |
| MEAN_REVERT | kept | 51 | 81.70 | 65.00 | -16.70 | 18.98 | 18.10 | 15.00 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 308 | 60.80 | 57.14 | -3.66 | 20.15 | 15.54 | 15.80 | 4.78 | 19.61 |
| MOVER_AVWAP_SCALP | kept | 1063 | 80.53 | 65.00 | -15.53 | 20.26 | 16.46 | 15.80 | 4.54 | 5.38 |
| MOVER_TREND_PULLBACK | filtered | 3433 | 56.29 | 64.16 | 7.87 | 20.19 | 18.68 | 15.80 | 4.13 | 18.76 |
| MOVER_TREND_PULLBACK | kept | 3996 | 76.52 | 65.00 | -11.52 | 20.30 | 18.68 | 15.80 | 4.44 | 1.85 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 26 | 55.16 | 63.31 | 8.15 | 17.30 | 20.00 | 18.90 | 3.90 | 9.60 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.20 | 65.00 | -6.20 | 24.10 | 20.00 | 19.30 | 3.50 | 6.00 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 52.73 | 63.24 | 10.51 | 21.04 | 14.90 | 20.00 | 0.00 | 0.82 |
| QUIET_COMPRESSION_BREAK | kept | 21 | 73.73 | 65.00 | -8.73 | 20.74 | 18.96 | 20.00 | 0.00 | 1.42 |
| SR_FLIP_RETEST | filtered | 47 | 34.91 | 60.85 | 25.94 | 20.78 | 20.00 | 19.22 | 2.50 | 25.03 |
| SR_FLIP_RETEST | kept | 3 | 64.17 | 65.00 | 0.83 | 21.30 | 20.00 | 15.57 | 2.17 | 0.40 |
| TREND_PULLBACK_EMA | filtered | 180 | 57.24 | 64.76 | 7.52 | 20.34 | 19.93 | 18.12 | 4.76 | 18.65 |
| TREND_PULLBACK_EMA | kept | 36 | 77.56 | 65.00 | -12.56 | 20.29 | 19.98 | 17.12 | 5.26 | 3.95 |
| VOLUME_SURGE_BREAKOUT | filtered | 131 | 45.52 | 64.42 | 18.90 | 18.44 | 16.18 | 20.00 | 3.46 | 10.69 |
| VOLUME_SURGE_BREAKOUT | kept | 36 | 74.40 | 65.00 | -9.40 | 16.16 | 15.46 | 20.00 | 4.53 | 0.21 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 288 | 55.52 | 23.19 | 14.77 | 5.09 | 11.92 | 5.04 | 7.96 | 0.67 |
| DIVERGENCE_CONTINUATION | kept | 78 | 67.09 | 19.26 | 17.36 | 3.50 | 13.51 | 4.97 | 9.73 | -0.10 |
| FAILED_AUCTION_RECLAIM | filtered | 112 | 50.66 | 19.71 | 17.75 | 4.88 | 13.87 | 9.08 | 4.79 | 1.51 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 68.95 | 25.00 | 16.00 | 6.00 | 14.00 | 6.75 | 5.70 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 47.21 | 25.00 | 8.00 | 3.21 | 12.83 | 9.64 | 5.02 | 3.34 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.80 | 25.00 | 18.00 | 3.00 | 9.00 | 8.50 | 8.30 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 18 | 72.87 | 25.00 | 8.00 | 15.00 | 8.00 | 2.50 | 7.70 | 6.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 419 | 49.81 | 23.95 | 15.71 | 4.53 | 10.96 | 5.83 | 5.77 | 1.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 70.60 | 24.28 | 14.34 | 4.48 | 11.73 | 6.21 | 7.83 | 1.73 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 54.50 | 25.00 | 14.00 | 6.00 | 11.00 | 8.50 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 67.83 | 21.00 | 14.00 | 3.75 | 14.75 | 6.75 | 9.82 | 0.00 |
| MEAN_REVERT | filtered | 83 | 61.94 | 21.14 | 16.12 | 8.75 | 11.45 | 5.00 | 7.63 | 0.00 |
| MEAN_REVERT | kept | 51 | 81.70 | 25.00 | 18.00 | 15.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 308 | 60.80 | 18.21 | 18.00 | 11.12 | 13.43 | 6.74 | 8.13 | 4.78 |
| MOVER_AVWAP_SCALP | kept | 1063 | 80.53 | 19.77 | 18.00 | 12.99 | 13.89 | 7.59 | 9.25 | 4.54 |
| MOVER_TREND_PULLBACK | filtered | 3433 | 56.29 | 17.88 | 18.00 | 7.67 | 12.26 | 6.40 | 8.87 | 4.13 |
| MOVER_TREND_PULLBACK | kept | 3996 | 76.52 | 19.53 | 18.01 | 7.97 | 12.79 | 6.71 | 8.98 | 4.44 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 26 | 55.16 | 19.15 | 18.00 | 15.00 | 14.00 | 5.00 | 4.70 | 3.90 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.20 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 4.70 | 3.50 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 52.73 | 17.96 | 15.12 | 9.48 | 12.40 | 9.42 | 5.37 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 21 | 73.73 | 19.29 | 16.48 | 12.29 | 14.14 | 6.57 | 7.91 | 0.00 |
| SR_FLIP_RETEST | filtered | 47 | 34.91 | 25.00 | 16.30 | 3.89 | 16.49 | 5.07 | 3.15 | 2.50 |
| SR_FLIP_RETEST | kept | 3 | 64.17 | 19.67 | 14.67 | 4.00 | 14.00 | 5.00 | 5.67 | 2.17 |
| TREND_PULLBACK_EMA | filtered | 180 | 57.24 | 18.07 | 18.00 | 7.53 | 14.55 | 6.32 | 9.08 | 4.76 |
| TREND_PULLBACK_EMA | kept | 36 | 77.56 | 22.78 | 18.06 | 7.50 | 14.00 | 5.50 | 8.67 | 5.26 |
| VOLUME_SURGE_BREAKOUT | filtered | 131 | 45.52 | 19.32 | 14.21 | 12.55 | 13.45 | 5.00 | 3.22 | 3.46 |
| VOLUME_SURGE_BREAKOUT | kept | 36 | 74.40 | 17.22 | 17.89 | 12.00 | 11.17 | 5.00 | 6.80 | 4.53 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 288 | 55.52 | 0.09 | 0.00 | 1.42 | 0.00 | 0.66 | 0.00 | 0.00 | 0.00 | **2.17** |
| DIVERGENCE_CONTINUATION | kept | 78 | 67.09 | 0.00 | 0.00 | 0.98 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **1.16** |
| FAILED_AUCTION_RECLAIM | filtered | 112 | 50.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **0.96** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 68.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 47.21 | 0.00 | 0.00 | 7.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.01** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 71.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 18 | 72.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 419 | 49.81 | 0.00 | 0.00 | 1.14 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | **1.74** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 70.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 54.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 67.83 | 2.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.25** |
| MEAN_REVERT | filtered | 83 | 61.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 51 | 81.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 308 | 60.80 | 0.00 | 0.00 | 0.00 | 0.00 | 4.54 | 0.48 | 0.00 | 0.77 | **5.79** |
| MOVER_AVWAP_SCALP | kept | 1063 | 80.53 | 0.00 | 0.00 | 0.08 | 0.00 | 1.57 | 0.17 | 0.00 | 0.57 | **2.39** |
| MOVER_TREND_PULLBACK | filtered | 3433 | 56.29 | 0.16 | 0.00 | 0.27 | 0.00 | 0.32 | 0.16 | 0.00 | 0.56 | **1.47** |
| MOVER_TREND_PULLBACK | kept | 3996 | 76.52 | 0.07 | 0.00 | 0.21 | 0.00 | 0.04 | 0.07 | 0.00 | 0.00 | **0.39** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 26 | 55.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 52.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.34 | 0.00 | 0.00 | 2.16 | **2.50** |
| QUIET_COMPRESSION_BREAK | kept | 21 | 73.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 47 | 34.91 | 0.00 | 0.00 | 0.00 | 0.00 | 3.22 | 0.00 | 0.00 | 0.00 | **3.22** |
| SR_FLIP_RETEST | kept | 3 | 64.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 180 | 57.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | **0.48** |
| TREND_PULLBACK_EMA | kept | 36 | 77.56 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.13** |
| VOLUME_SURGE_BREAKOUT | filtered | 131 | 45.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.68 | **5.68** |
| VOLUME_SURGE_BREAKOUT | kept | 36 | 74.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **150064 held of 549729 seen** across 21 strategies; 3410 cells past the sample floor; **1742 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44654 | 694/43960/0 | 43% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/RANGE/NORMAL/BTC_FALLING (-1.23R) |
| MOVER_AVWAP_SCALP | 19447 | 182/19265/0 | 42% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11497 | 126/11371/0 | 36% | -0.31 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10574 | 107/10467/0 | 48% | -0.06 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9043 | 41/9002/0 | 40% | -0.22 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 7838 | 87/7751/0 | 33% | -0.53 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7238 | 0/0/7238 | 42% | -0.12 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.48R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.07R) |
| SHADOW_RANGE_FADE | 6660 | 0/0/6660 | 36% | -0.14 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.60R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.20R) |
| QUIET_COMPRESSION_BREAK | 6217 | 405/5812/0 | 49% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5714 | 0/0/5714 | 34% | -0.41 | NY/RANGE/EXPANDED/BTC_FALLING (+0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 3895 | 47/3848/0 | 40% | -0.27 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| SR_FLIP_RETEST | 3686 | 15/3671/0 | 45% | -0.30 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+0.87R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 3028 | 0/3028/0 | 33% | -0.29 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2962 | 2/2960/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| RANGE_FADE | 1411 | 4/1407/0 | 38% | -0.36 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1334 | 0/0/1334 | 54% | -0.04 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.32R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.40R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 362 | 0/362/0 | 31% | -0.58 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 126 | 26/100/0 | 44% | -0.14 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_RISING/MIDCAP` -1.60R (n=48, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 224 | 28% / -0.58R | 224 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 20 | 30% / -0.54R | 20 | 55% / -0.24R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 769 | 40% / -0.30R | 769 | 53% / -0.06R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1259 | 43% / -0.35R | 1259 | 56% / -0.13R | +0.21 | **ATR** |
| RANGE_FADE | 71 | 30% / -0.45R | 71 | 37% / -0.31R | +0.14 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 152 | 35% / -0.22R | 152 | 45% / -0.08R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 315 | 44% / -0.28R | 315 | 47% / -0.17R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1850 | 43% / -0.19R | 1850 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1101 | 39% / -0.26R | 1101 | 42% / -0.15R | +0.11 | **ATR** |
| MA_CROSS_TREND_SHIFT | 39 | 41% / -0.19R | 39 | 44% / -0.09R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 7532 | 49% / -0.11R | 7532 | 54% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1153 | 49% / -0.09R | 1153 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1032 | 47% / -0.15R | 1032 | 47% / -0.15R | -0.00 | **FIXED** |
| MEAN_REVERT | 281 | 49% / -0.13R | 281 | 48% / -0.13R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10411 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1850 | 47% | -0.07R | 218 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 95 | 46% | -0.09R | 59 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1033 | 35% / -0.23R | +0.84 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1365 | 40% / -0.18R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2312 | 35% / -0.15R | +0.69 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9416 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1316 | 38% / -0.09R | +0.19 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1008 | 34% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 913 | 33% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 224 | 31% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 288 | 32% / -0.51R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 234 | 49% / -0.02R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 54 | 35% / -0.12R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 300 | 34% / -0.32R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 60 | 28% / -0.38R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 26 | 42% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×379]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 162/6) (sustained 162 cycles)
- **ALERT** `edge_reconciliation` — TREND_PULLBACK_EMA realized−counterfactual=+0.57R (bound 0.3) (streak 181/6) (sustained 181 cycles)
- **ALERT** `tuned_variants` — 298 non-stamps — atr_arm_uncomputable=298 (seen=5730 stamped=281 skipped=5151) (streak 181/6) (sustained 181 cycles)
- **ALERT** `auto_dispatch` — 21 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=21) (streak 141/3) (sustained 141 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 39935167 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 13 arms current, none stalled; covering 1700/1700 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 25 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 5/12) | 5 |
| auto_dispatch | violating | 21 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=21) (streak 141/3) | 141 |
| binance_ip_weight | ok | peak 241/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82521.90 | 0 |
| candle_coverage | ok | 82/82 symbols with ≥20 15m candles, 82/82 updated within 45m [fresh=82; 73 Tier-1 futures + 9 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1450 dup bars, 0 undedupable; ws 0 out-of-order, 308 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 57 cohorts, 35 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +199 / upstream +50 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1362/1380 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 4 promoted today, nothing refused | 0 |
| dark_resolution | ok | 129 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1349/1367 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 9455744 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | TREND_PULLBACK_EMA realized−counterfactual=+0.57R (bound 0.3) (streak 181/6) | 181 |
| emission_controller | ok | last cycle 0s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×379]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 162/6) | 162 |
| entry_quality_effective | ok | 6294 evaluated, 2233 suppressed, 4061 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,355 reads/day of 50,000 [engine 1,320, signing 35]; top site keystore.roster_doc at 288/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 940 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +19 / upstream +543 | 0 |
| indicator_cache_key | ok | 45597 frozen value(s) avoided; 277340 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.28R over n=3848 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +99 / upstream +543 | 0 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 9 held, 9 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2922581 evicted (sampled: execution:trigger_not_confirmed 400/1039274, execution:overextended 400/922105, setup_compat:regime_STRONG_TREND 400/493566) | 0 |
| price_action_lane | ok | 803955 evaluated, 502 emitted; layer1 502 stamped / 0 blind; cooldown=115996, delta_opposed=68269, no_footprint=273140, no_opposing_target=518, no_sweep=282064, rr_below_floor=63466 | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.36R over n=1407 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +10 / upstream +543 | 0 |
| sar_alignment_crosscheck | ok | 308/6429 disagreed (4.8%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +543 | 0 |
| sar_hold_arm | ok | 1875 held arms settled, 125 unscored, 25 still walking (21 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 6/26 unfetchable (23%); top cause: located bar does not contain the stamp; symbols: 1000PEPEUSDT, BATUSDT, CRVUSDT, STBLUSDT, STRKUSDT +1 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 24 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 5/12) | 5 |
| sar_refresh_budget | ok | 12 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 426 records await one (20 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 14.62s, worst 95.78s over 9631 lifetime cycles; lifetime 5 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.97s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 354812 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 36s ago (2.52s to run, worst 74.91s), 141 overrun(s) of 3979 cycles, TTL 900s; slowest engine_state=9.75s, positions_diag=4.06s, signals=2.51s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +133 / upstream +543 | 0 |
| structural_snap | ok | 6000/6000 measured, 23 blind, 0 levels moved (refusals: redetect_cooldown=698) | 0 |
| structural_veto_lane | ok | 904 stamped; 0 with no readable level book, 69 with clear air ahead, 541 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +543 / upstream +50 | 0 |
| tuned_variants | violating | 298 non-stamps — atr_arm_uncomputable=298 (seen=5730 stamped=281 skipped=5151) (streak 181/6) | 181 |
| unlock_shorts | ok | 15 open, 41 scheduled, calendar 13.4h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4161197`
- `Path funnel` emissions: `110`
- `Regime distribution` emissions: `110`
- `QUIET_SCALP_BLOCK` events: `92`
- `confidence_gate` events: `10487`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **12**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 3432 | 4063 | 6176 | 0 |
| futures_aggtrade | 2 | 2832 | 2832 | 3137 | 0 |
| futures_depth | 3 | 4611 | 4611 | 6881 | 0 |
| futures_liq | 3 | 2361 | 2361 | 5315 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=745545] state[populated=745545] buckets[many=745545] sources[none] quality[none]
- funding_rate: presence[absent=74056, present=671489] state[empty=74056, populated=671489] buckets[few=671489, none=74056] sources[none] quality[none]
- liquidation_clusters: presence[absent=395350, present=350195] state[empty=395350, populated=350195] buckets[few=293945, none=395350, some=56250] sources[none] quality[none]
- oi_snapshot: presence[absent=72848, present=672697] state[empty=72848, populated=672697] buckets[few=419, many=670176, none=72848, some=2102] sources[none] quality[none]
- order_book: presence[absent=203264, present=542281] state[populated=542281, unavailable=203264] buckets[few=542281, none=203264] sources[book_ticker=542281, unavailable=203264] quality[none=203264, top_of_book_only=542281]
- orderblocks: presence[absent=745545] state[empty=745545] buckets[none=745545] sources[measured_dark=745545] quality[none]
- recent_ticks: presence[present=745545] state[populated=745545] buckets[many=745545] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.4343069791793823` sec
- Median create→first breach: `4408.777466416359` sec
- Median create→terminal: `4408.9392240047455` sec
- Median first breach→terminal: `3.9577484130859375e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 3.1}, "under_180s": {"count": 1, "pct": 3.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 3.1}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 3.1}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 1.473178535441776 | 1.874773066526811 | 0.5811298667363437 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.0915331232028433 | 1.2062571507476239 | 0.9048925616949289 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.9639528043475265 | 2.0872405053855623 | 0.5820827257145337 | 0 | 2 |
| MOVER_AVWAP_SCALP | 2 | 2 | 1.6927651370381323 | 1.6330869319621724 | 1.0287560476070927 | 1 | 1 |
| MOVER_TREND_PULLBACK | 14 | 14 | 3.7573090931351008 | 3.0 | 1.252436364378367 | 12 | 2 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.8122533737590264 | 1.2386520168769042 | 0.6557559045574518 | 0 | 1 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.487208768754307 | 1.4872087684226492 | 0.9999991679896729 | 0 | 4 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.4589 | 3710.406497001648 | 3710.4065709114075 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0915 | 23664.162937879562 | 23664.162966012955 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 1.8278 | 2314.409772992134 | 2314.5325759649277 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.517 | 4143.859562039375 | 4143.859647989273 |
| MOVER_TREND_PULLBACK | 14 | 14 | 28.6 | 50.0 | 28.6 | 0.0 | -0.6863 | 2771.8979345560074 | 2772.0467694997787 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.5387 | 4180.860617876053 | 4181.184053897858 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 11.1 | 55.6 | 11.1 | 0.0 | -0.2779 | 23873.48088502884 | 23873.480907917023 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1085 | 3 | 562 | 0.0 | 0.0 | None | None | 523 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4297 | 9 | 3977 | 0.0 | 0.0 | None | None | 320 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `2`
- Gating Δ: `125128`
- No-generation Δ: `1497839`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0168, "current_avg_pnl": -0.4589, "current_win_rate": 0.0, "previous_avg_pnl": -0.4421, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.7962, "current_avg_pnl": -0.6863, "current_win_rate": 28.6, "previous_avg_pnl": 0.1099, "previous_win_rate": 34.4, "win_rate_delta": -5.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1777, "current_avg_pnl": -0.2779, "current_win_rate": 11.1, "previous_avg_pnl": -0.1002, "previous_win_rate": 25.0, "win_rate_delta": -13.9}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 459, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 265, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -65223.41, "median_terminal_delta_sec": -65226.82, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
