# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, MOVER_AVWAP_SCALP
- Top promising signals/paths: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `9` sec (warning=False)
- Latest performance record age: `1912` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 37 | 37 | 37 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4594 | 4594 | 4019 | 7 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 41025 | 41037 | 18 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 37476 | 37476 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 37219 | 35749 | 1714 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 37499 | 36858 | 728 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 37873 | 37865 | 19 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 32852 | 32869 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 37592 | 37611 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 37616 | 36785 | 1161 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 43119 | 46183 | 503 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 41057 | 37583 | 5499 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 37571 | 37571 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 37481 | 37497 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 37187 | 37098 | 118 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 37950 | 36802 | 1527 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 36872 | 37113 | 57 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 31973 | 29730 | 2481 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 32213 | 31979 | 277 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 40983 | 41003 | 18 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 32875 | 32884 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2121 | 2121 | 1767 | 7 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 80 | 80 | 23 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8974 | 8974 | 8816 | 15 | active-healthy (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2564 | 2564 | 1980 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 976 | 976 | 402 | 26 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 11693 | 11693 | 5414 | 229 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 2 | 2 | 0 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 477 | 477 | 247 | 38 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3093 | 3093 | 2503 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 178 | 178 | 80 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1016 | 1016 | 830 | 20 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 41 | 41 | 4 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=41037): breakout_not_found=27496, basic_filters_failed=8994, move_not_fresh=2672, breakout_stale=1317, retest_proximity_failed=466, volume_spike_missing=53, move_exhausted=30, missing_fvg_or_orderblock=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=37476): cls_disabled_merged_into_lsr=37476
- **EVAL::DIVERGENCE_CONTINUATION** (total=35749): cvd_divergence_failed=14896, h1_trend_not_aligned=9829, basic_filters_failed=7407, ema_alignment_reject=2877, retest_proximity_failed=589, missing_fvg_or_orderblock=151
- **EVAL::FAILED_AUCTION_RECLAIM** (total=36858): auction_not_detected=23483, basic_filters_failed=7002, reclaim_hold_failed=2850, regime_blocked=1817, tail_too_small=1704, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=37865): funding_not_extreme=26276, basic_filters_failed=6824, missing_funding_rate=4383, ema_alignment_reject=243, rsi_reject=88, cvd_divergence_failed=24, momentum_reject=16, missing_fvg_or_orderblock=11
- **EVAL::LIQUIDATION_REVERSAL** (total=32869): cascade_threshold_not_met=24934, basic_filters_failed=7408, rsi_reject=293, cvd_divergence_failed=224, missing_fvg_or_orderblock=10
- **EVAL::MA_CROSS_TREND_SHIFT** (total=37611): no_ma_cross=29527, basic_filters_failed=7417, ma_cross_htf_misaligned=530, ma_cross_cooldown=137
- **EVAL::MEAN_REVERT** (total=36785): no_extension=31263, basic_filters_failed=5522
- **EVAL::MOVER_AVWAP_SCALP** (total=46183): no_avwap_tag=17536, no_mover_leg=14102, basic_filters_failed=9107, avwap_slope_against=3352, avwap_reclaim_no_volume=1202, no_avwap_reclaim=882, anchor_too_recent=2
- **EVAL::MOVER_TREND_PULLBACK** (total=37583): mover_run_too_small=20215, basic_filters_failed=9054, no_reclaim=6785, no_pullback_tag=1529
- **EVAL::OPENING_RANGE_BREAKOUT** (total=37571): feature_disabled=37571
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=37497): regime_blocked=29355, breakout_not_found=5507, basic_filters_failed=1452, adx_reject=1140, ema_alignment_reject=43
- **EVAL::QUIET_COMPRESSION_BREAK** (total=37098): compression_not_detected=16493, regime_blocked=9890, basic_filters_failed=5542, breakout_not_detected=4891, volume_confirmation_failed=270, rsi_reject=7, missing_fvg_or_orderblock=5
- **EVAL::RANGE_FADE** (total=36802): no_range_edge=31279, basic_filters_failed=5523
- **EVAL::SR_FLIP_RETEST** (total=37113): flip_close_not_confirmed=24045, basic_filters_failed=6989, regime_blocked=1811, retest_out_of_zone=1181, long_break_volume_thin=1128, h1_break_not_confirmed=992, reclaim_hold_failed=399, ema_alignment_reject=250, long_acceptance_not_held=156, whipsaw_flip=104, wick_quality_failed=52, missing_fvg_or_orderblock=6
- **EVAL::STANDARD** (total=29730): adx_reject=8804, momentum_reject=7866, basic_filters_failed=4006, sweeps_not_detected=3614, macd_reject=3244, ema_alignment_reject=1504, htf_poi_unanchored=637, rsi_reject=31, invalid_sl_geometry=24
- **EVAL::TREND_PULLBACK** (total=31979): h1_trend_not_aligned=10895, ema_alignment_reject=6232, basic_filters_failed=4012, h1_pullback_not_confirmed=3086, no_ema_reclaim_close=2313, ema_not_tested_prev=2233, body_conviction_fail=1377, rsi_reject=819, prev_already_above_emas=293, prev_already_below_emas=286, no_prev_high_break=167, momentum_flat=130, no_prev_low_break=68, ema21_not_tagged=52, missing_fvg_or_orderblock=11, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=41003): breakout_not_found=22808, basic_filters_failed=8992, move_not_fresh=5406, breakout_stale=2771, retest_proximity_failed=775, volume_spike_missing=210, move_exhausted=39, missing_fvg_or_orderblock=2
- **EVAL::WHALE_MOMENTUM** (total=32884): momentum_reject=26462, recent_ticks_insufficient=4758, basic_filters_failed=1664

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=8): execution:overextended=8
- **DIVERGENCE_CONTINUATION** (total=110): setup_compat:regime_VOLATILE_UNSUITABLE=106, setup_compat:regime_BREAKOUT_EXPANSION=4
- **FAILED_AUCTION_RECLAIM** (total=606): execution:overextended=344, setup_compat:regime_STRONG_TREND=146, context_floor=69, setup_compat:regime_VOLATILE_UNSUITABLE=47
- **FUNDING_EXTREME_SIGNAL** (total=79): execution:trigger_not_confirmed=72, context_floor=7
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=1820): execution:trigger_not_confirmed=754, execution:overextended=729, setup_compat:regime_STRONG_TREND=337
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_DIRTY_RANGE=2, execution:overextended=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=1102): setup_compat:regime_STRONG_TREND=423, setup_compat:regime_WEAK_TREND=404, execution:overextended=275
- **MOVER_AVWAP_SCALP** (total=476): execution:overextended=315, entry_quality=93, execution:trigger_not_confirmed=68
- **MOVER_TREND_PULLBACK** (total=6013): execution:overextended=2789, execution:trigger_not_confirmed=2477, entry_quality=747
- **QUIET_COMPRESSION_BREAK** (total=4): execution:trigger_not_confirmed=4
- **RANGE_FADE** (total=1422): setup_compat:regime_STRONG_TREND=559, setup_compat:regime_VOLATILE_UNSUITABLE=371, setup_compat:regime_WEAK_TREND=278, execution:overextended=164, context_edge=49, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=967): setup_compat:regime_CLEAN_RANGE=628, setup_compat:regime_DIRTY_RANGE=220, entry_quality=82, setup_compat:regime_VOLATILE_UNSUITABLE=37
- **VOLUME_SURGE_BREAKOUT** (total=2): execution:overextended=2

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 87244 | 48.6% |
| QUIET | 42667 | 23.7% |
| TRENDING_UP | 25724 | 14.3% |
| TRENDING_DOWN | 14592 | 8.1% |
| VOLATILE | 9435 | 5.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **92**
- Average confidence gap to threshold: **10.76** (samples=92) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=14, AVAXUSDT=10, HBARUSDT=10, DOTUSDT=9, XLMUSDT=8, AAVEUSDT=5, ONDOUSDT=5, ZECUSDT=5, XMRUSDT=4, FILUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 72 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 114 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 56 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 30 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDATION_REVERSAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 54 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 23 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 8 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 3 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 267 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 130 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1272 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1573 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 46 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 35 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 139 |
| SR_FLIP_RETEST | filtered | min_confidence | 12 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 12 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 11 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 56 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 27 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 75 | 56.10 | 64.03 | 7.93 | 21.07 | 19.82 | 17.41 | 1.60 | 9.84 |
| DIVERGENCE_CONTINUATION | kept | 114 | 69.98 | 65.00 | -4.98 | 21.73 | 19.97 | 18.85 | 0.83 | 1.93 |
| FAILED_AUCTION_RECLAIM | filtered | 73 | 46.30 | 63.32 | 17.02 | 20.89 | 18.80 | 20.00 | 1.55 | 13.50 |
| FAILED_AUCTION_RECLAIM | kept | 30 | 67.54 | 65.00 | -2.54 | 21.11 | 19.79 | 20.00 | 2.38 | 4.09 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 52.00 | 61.00 | 9.00 | 21.20 | 13.60 | 17.00 | 5.00 | 0.00 |
| LIQUIDATION_REVERSAL | kept | 1 | 68.00 | 65.00 | -3.00 | 24.20 | 11.20 | 19.60 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 54 | 51.36 | 65.00 | 13.64 | 19.98 | 17.97 | 18.23 | 0.69 | 11.41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 23 | 68.07 | 65.00 | -3.07 | 21.82 | 18.90 | 18.14 | 1.96 | 0.13 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 52.50 | 61.00 | 8.50 | 20.90 | 19.80 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 65.00 | -1.00 | 21.20 | 18.10 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 11 | 51.61 | 65.00 | 13.39 | 21.15 | 15.75 | 15.07 | 0.00 | 17.90 |
| MEAN_REVERT | kept | 1 | 65.10 | 65.00 | -0.10 | 21.80 | 19.30 | 14.20 | 0.00 | 7.90 |
| MOVER_AVWAP_SCALP | filtered | 272 | 52.65 | 64.38 | 11.73 | 20.97 | 16.33 | 15.80 | 4.08 | 16.14 |
| MOVER_AVWAP_SCALP | kept | 130 | 76.53 | 65.00 | -11.53 | 18.89 | 16.93 | 15.80 | 4.87 | 6.24 |
| MOVER_TREND_PULLBACK | filtered | 1272 | 52.01 | 63.15 | 11.14 | 19.92 | 18.36 | 15.80 | 3.80 | 22.49 |
| MOVER_TREND_PULLBACK | kept | 1573 | 76.61 | 65.00 | -11.61 | 20.43 | 18.37 | 15.80 | 4.05 | 1.28 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 80.50 | 65.00 | -15.50 | 20.20 | 19.60 | 17.20 | 4.50 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 81 | 50.96 | 64.11 | 13.15 | 20.69 | 19.28 | 20.00 | 0.00 | 13.52 |
| QUIET_COMPRESSION_BREAK | kept | 139 | 73.98 | 65.00 | -8.98 | 20.72 | 19.40 | 20.00 | 0.00 | 1.56 |
| SR_FLIP_RETEST | filtered | 24 | 53.83 | 65.00 | 11.17 | 22.21 | 20.00 | 15.50 | 2.19 | 6.61 |
| SR_FLIP_RETEST | kept | 11 | 73.84 | 65.00 | -8.84 | 21.19 | 20.00 | 16.87 | 1.95 | 1.77 |
| TREND_PULLBACK_EMA | filtered | 12 | 59.52 | 65.00 | 5.48 | 21.53 | 19.95 | 16.61 | 5.00 | 14.82 |
| TREND_PULLBACK_EMA | kept | 56 | 77.95 | 65.00 | -12.95 | 20.93 | 19.97 | 17.86 | 4.65 | -0.85 |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 42.76 | 64.70 | 21.94 | 20.30 | 18.34 | 20.00 | 4.43 | 18.74 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 76.94 | 65.00 | -11.94 | 20.24 | 17.01 | 20.00 | 5.07 | 5.37 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 75 | 56.10 | 22.65 | 12.40 | 5.32 | 13.25 | 5.86 | 8.13 | 1.60 |
| DIVERGENCE_CONTINUATION | kept | 114 | 69.98 | 22.19 | 17.21 | 4.53 | 12.37 | 5.72 | 9.38 | 0.83 |
| FAILED_AUCTION_RECLAIM | filtered | 73 | 46.30 | 19.30 | 17.07 | 7.32 | 14.42 | 8.16 | 4.50 | 1.55 |
| FAILED_AUCTION_RECLAIM | kept | 30 | 67.54 | 23.67 | 17.33 | 4.80 | 12.70 | 5.15 | 6.10 | 2.38 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 52.00 | 25.00 | 8.00 | 3.00 | 15.00 | 5.00 | 6.00 | 5.00 |
| LIQUIDATION_REVERSAL | kept | 1 | 68.00 | 25.00 | 8.00 | 15.00 | 8.00 | 5.00 | 3.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 54 | 51.36 | 22.26 | 14.07 | 8.94 | 14.11 | 4.44 | 7.14 | 0.69 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 23 | 68.07 | 21.26 | 15.04 | 4.43 | 12.43 | 4.76 | 8.57 | 1.96 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 52.50 | 25.00 | 14.00 | 3.00 | 14.00 | 8.50 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 17.00 | 14.00 | 3.00 | 14.00 | 10.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 11 | 51.61 | 17.00 | 18.00 | 10.64 | 12.73 | 5.00 | 6.15 | 0.00 |
| MEAN_REVERT | kept | 1 | 65.10 | 25.00 | 14.00 | 15.00 | 12.00 | 5.00 | 2.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 272 | 52.65 | 19.30 | 18.00 | 11.60 | 13.25 | 5.66 | 6.21 | 4.08 |
| MOVER_AVWAP_SCALP | kept | 130 | 76.53 | 18.05 | 18.05 | 12.77 | 14.12 | 5.63 | 9.41 | 4.87 |
| MOVER_TREND_PULLBACK | filtered | 1272 | 52.01 | 18.00 | 18.02 | 7.83 | 12.40 | 6.55 | 8.55 | 3.80 |
| MOVER_TREND_PULLBACK | kept | 1573 | 76.61 | 19.50 | 18.08 | 7.83 | 12.62 | 6.77 | 9.12 | 4.05 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 80.50 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 81 | 50.96 | 19.27 | 16.27 | 12.85 | 14.15 | 7.09 | 3.92 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 139 | 73.98 | 20.28 | 16.53 | 10.64 | 14.05 | 6.38 | 8.35 | 0.00 |
| SR_FLIP_RETEST | filtered | 24 | 53.83 | 22.67 | 13.00 | 3.88 | 13.88 | 6.27 | 6.07 | 2.19 |
| SR_FLIP_RETEST | kept | 11 | 73.84 | 22.09 | 17.09 | 5.73 | 14.55 | 5.32 | 8.89 | 1.95 |
| TREND_PULLBACK_EMA | filtered | 12 | 59.52 | 13.25 | 18.00 | 7.50 | 14.50 | 6.92 | 9.17 | 5.00 |
| TREND_PULLBACK_EMA | kept | 56 | 77.95 | 19.43 | 18.04 | 7.74 | 13.93 | 6.44 | 9.09 | 4.65 |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 42.76 | 19.67 | 14.00 | 12.22 | 14.00 | 5.00 | 7.18 | 4.43 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 76.94 | 22.71 | 15.14 | 13.29 | 14.86 | 5.00 | 8.39 | 5.07 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 75 | 56.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.26** |
| DIVERGENCE_CONTINUATION | kept | 114 | 69.98 | 0.00 | 0.00 | 0.04 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.15** |
| FAILED_AUCTION_RECLAIM | filtered | 73 | 46.30 | 0.00 | 0.00 | 0.66 | 0.00 | 3.09 | 0.00 | 0.00 | 0.00 | **3.75** |
| FAILED_AUCTION_RECLAIM | kept | 30 | 67.54 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 52.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | kept | 1 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 54 | 51.36 | 0.17 | 0.00 | 1.93 | 0.00 | 2.67 | 0.56 | 0.00 | 0.00 | **5.33** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 23 | 68.07 | 0.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.39** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 52.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 11 | 51.61 | 0.00 | 0.00 | 0.00 | 0.00 | 14.62 | 0.91 | 0.00 | 0.00 | **15.53** |
| MEAN_REVERT | kept | 1 | 65.10 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| MOVER_AVWAP_SCALP | filtered | 272 | 52.65 | 0.00 | 0.00 | 0.26 | 0.00 | 4.46 | 0.15 | 0.00 | 0.87 | **5.74** |
| MOVER_AVWAP_SCALP | kept | 130 | 76.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.10 | **0.28** |
| MOVER_TREND_PULLBACK | filtered | 1272 | 52.01 | 0.00 | 0.00 | 3.63 | 0.00 | 0.47 | 0.02 | 0.00 | 0.02 | **4.14** |
| MOVER_TREND_PULLBACK | kept | 1573 | 76.61 | 0.00 | 0.00 | 0.32 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.43** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 80.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 81 | 50.96 | 0.00 | 0.00 | 0.18 | 0.00 | 0.42 | 1.83 | 0.00 | 5.11 | **7.54** |
| QUIET_COMPRESSION_BREAK | kept | 139 | 73.98 | 0.00 | 0.00 | 0.40 | 0.00 | 0.32 | 0.07 | 0.00 | 0.08 | **0.87** |
| SR_FLIP_RETEST | filtered | 24 | 53.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 11 | 73.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 12 | 59.52 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 0.00 | 0.00 | 0.00 | **5.40** |
| TREND_PULLBACK_EMA | kept | 56 | 77.95 | 0.00 | 0.00 | 0.09 | 0.00 | 0.64 | 0.00 | 0.00 | 0.00 | **0.73** |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 42.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 76.94 | 0.00 | 0.00 | 1.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.14** |

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
- Outcomes recorded: **163354 held of 642526 seen** across 21 strategies; 3674 cells past the sample floor; **1925 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46223 | 660/45563/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.27R) |
| MOVER_AVWAP_SCALP | 21189 | 189/21000/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 12057 | 138/11919/0 | 48% | -0.06 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12017 | 136/11881/0 | 38% | -0.28 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| TREND_PULLBACK_EMA | 10148 | 41/10107/0 | 40% | -0.24 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 8944 | 107/8837/0 | 35% | -0.46 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7645 | 0/0/7645 | 43% | -0.10 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.45R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.08R) |
| SHADOW_RANGE_FADE | 7161 | 0/0/7161 | 36% | -0.14 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.56R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.26R) |
| QUIET_COMPRESSION_BREAK | 6981 | 394/6587/0 | 49% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_FUNDING_FADE | 6448 | 0/0/6448 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 4640 | 18/4622/0 | 46% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4610 | 50/4560/0 | 38% | -0.31 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3627 | 2/3625/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3357 | 0/3357/0 | 31% | -0.34 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| RANGE_FADE | 1894 | 6/1888/0 | 33% | -0.52 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1491 | 0/0/1491 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 398 | 0/398/0 | 29% | -0.63 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 146 | 30/116/0 | 41% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 290 | 27% / -0.59R | 290 | 54% / -0.09R | +0.50 | **ATR** |
| LIQUIDATION_REVERSAL | 24 | 25% / -0.65R | 24 | 50% / -0.29R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 888 | 39% / -0.33R | 888 | 52% / -0.07R | +0.27 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1396 | 43% / -0.35R | 1396 | 56% / -0.12R | +0.23 | **ATR** |
| RANGE_FADE | 96 | 31% / -0.38R | 96 | 39% / -0.24R | +0.14 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 173 | 35% / -0.22R | 173 | 46% / -0.08R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 2110 | 43% / -0.19R | 2110 | 50% / -0.06R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 428 | 42% / -0.30R | 428 | 46% / -0.17R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 47 | 38% / -0.19R | 47 | 43% / -0.08R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1197 | 40% / -0.24R | 1197 | 42% / -0.14R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8228 | 50% / -0.11R | 8228 | 54% / -0.01R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1355 | 48% / -0.10R | 1355 | 54% / -0.04R | +0.06 | **ATR** |
| MEAN_REVERT | 330 | 47% / -0.17R | 330 | 46% / -0.18R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1222 | 46% / -0.15R | 1222 | 46% / -0.15R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11103 | 28% | -0.21R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2110 | 47% | -0.06R | 227 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 109 | 47% | -0.08R | 64 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1581 | 40% / -0.14R | +0.87 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1177 | 34% / -0.21R | +0.86 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2570 | 35% / -0.15R | +0.69 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10110 | 37% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1553 | 38% / -0.09R | +0.19 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1182 | 35% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1002 | 32% / -0.23R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 250 | 31% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 387 | 32% / -0.11R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 273 | 49% / -0.05R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 73 | 40% / -0.08R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 389 | 33% / -0.32R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 70 | 29% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 30 | 40% / -0.40R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **6** · boot grace active: False
- **ALERT** `ai_governor_verdicts` — upstream +2 but output +0 (streak 12/6) (sustained 12 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×935]; set aside 4 undeclared (extension_pct,funding_rate,pullback_depth_atr,stack_sep_pct) (streak 285/6) (sustained 285 cycles)
- **ALERT** `stale_tf_scoring` — new stale-TF events: scored 18x, gate reads 0x, withheld 18x (lifetime scored 7418x; refusal ARMED); last PONSUSDT age=16743.7s (streak 31/6) (sustained 31 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.55R (bound 0.3) (streak 342/6) (sustained 342 cycles)
- **ALERT** `tuned_variants` — 408 non-stamps — atr_arm_uncomputable=408 (seen=8849 stamped=886 skipped=7555) (streak 342/6) (sustained 342 cycles)
- **ALERT** `auto_dispatch` — 82 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=82) (streak 335/3) (sustained 335 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 46 fed / 0 quiet / 0 never delivered of 46 subscribed; 92183289 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 39 arms current, none stalled; covering 2070/2070 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 12/6) | 12 |
| atr_trail_live_arms | ok | 73 arms current, none stalled; covering 1106/1106 signals (100%) | 0 |
| auto_dispatch | violating | 82 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=82) (streak 335/3) | 335 |
| binance_ip_weight | ok | peak 146/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 80865.10 | 0 |
| candle_coverage | ok | 87/87 symbols with ≥20 15m candles, 87/87 updated within 45m [fresh=87; 77 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 2924 dup bars, 0 undedupable; ws 0 out-of-order, 396 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +17 / upstream +18 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1546/1565 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 4 promoted today, nothing refused | 0 |
| dark_resolution | violating | 8 of 129 open dark rows are not being advanced (worst: MAGMAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 41/120) | 41 |
| dark_sar_arms | ok | no open arms; covering 1539/1558 signals (99%) | 0 |
| depth_feed | ok | 46/46 books fresh (stale 0, never 0, thin 0); 18730215 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.55R (bound 0.3) (streak 342/6) | 342 |
| emission_controller | ok | last cycle 578s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×935]; set aside 4 undeclared (extension_pct,funding_rate,pullback_depth_atr,stack_sep_pct) (streak 285/6) | 285 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, profile_reject=2. Held back in this window: session_quality=127, profile_reject=3. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 2/6) | 2 |
| firestore_read_budget | ok | 1,358 reads/day of 50,000 [engine 1,323, signing 35]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5520 sealed bars over 46 symbols; 1507 incomplete, 9 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +217 | 0 |
| indicator_cache_key | ok | 109734 frozen value(s) avoided; 374062 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.31R over n=4560 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +217 but output +0 (streak 7/72) | 7 |
| mover_admission_metadata | ok | 936 symbols known, 229 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 13 locked / 13 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2177 rows held, 3166122 evicted (sampled: execution:trigger_not_confirmed 296/1117568, execution:overextended 296/995225, setup_compat:regime_STRONG_TREND 296/533816) | 0 |
| price_action_lane | ok | 583616 evaluated, 869 emitted; layer1 869 stamped / 0 blind; cooldown=67817, delta_opposed=67415, no_footprint=213521, no_opposing_target=1148, no_sweep=169528, rr_below_floor=63318 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.52R over n=1888 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +35 / upstream +217 | 0 |
| sar_alignment_crosscheck | ok | 499/20809 disagreed (2.4%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +217 | 0 |
| sar_hold_arm | ok | 1862 held arms settled, 138 unscored, 73 still walking (65 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 73/73 resolvable | 0 |
| sar_live_arms | ok | 73 arms current, none stalled; covering 1104/1104 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 6 resolved, 67 still mid-window | 0 |
| scan_cycle | ok | last 114.66s, worst 265.89s over 10761 lifetime cycles; lifetime 395 over 60s, 100 over 120s; recent 3/1 warn/kill breaches in 20/20 cycles; heartbeat age 64.21s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 253238 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 88s ago (141.17s to run, worst 178.9s), 1295 overrun(s) of 7113 cycles, TTL 900s; slowest trail_governor=29.06s, dark_promotion=26.41s, engine_state=12.07s | 0 |
| stale_tf_scoring | violating | new stale-TF events: scored 18x, gate reads 0x, withheld 18x (lifetime scored 7418x; refusal ARMED); last PONSUSDT age=16743.7s (streak 31/6) | 31 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +51 / upstream +217 | 0 |
| structural_snap | ok | 6000/6000 measured, 37 blind, 0 levels moved (refusals: redetect_cooldown=3089) | 0 |
| structural_veto_lane | ok | 3895 stamped; 0 with no readable level book, 23 with clear air ahead, 3180 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +217 / upstream +18 | 0 |
| tuned_variants | violating | 408 non-stamps — atr_arm_uncomputable=408 (seen=8849 stamped=886 skipped=7555) (streak 342/6) | 342 |
| unlock_shorts | ok | 12 open, 47 scheduled, calendar 9.8h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 69 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `73802`
- `Path funnel` emissions: `21`
- `Regime distribution` emissions: `21`
- `QUIET_SCALP_BLOCK` events: `92`
- `confidence_gate` events: `3991`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **9**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 2 | 3649 | 3649 | 25700 | 0 |
| futures_liq | 7 | 3844 | 19323 | 20541 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=138440] state[populated=138440] buckets[many=138440] sources[none] quality[none]
- funding_rate: presence[absent=22190, present=116250] state[empty=22190, populated=116250] buckets[few=116250, none=22190] sources[none] quality[none]
- liquidation_clusters: presence[absent=91960, present=46480] state[empty=91960, populated=46480] buckets[few=38366, none=91960, some=8114] sources[none] quality[none]
- oi_snapshot: presence[absent=22190, present=116250] state[empty=22190, populated=116250] buckets[many=116250, none=22190] sources[none] quality[none]
- order_book: presence[absent=54657, present=83783] state[populated=83783, unavailable=54657] buckets[few=83783, none=54657] sources[book_ticker=83783, unavailable=54657] quality[none=54657, top_of_book_only=83783]
- orderblocks: presence[absent=138440] state[empty=138440] buckets[none=138440] sources[measured_dark=138440] quality[none]
- recent_ticks: presence[present=138440] state[populated=138440] buckets[many=138440] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.809529066085815` sec
- Median create→first breach: `6240.85791683197` sec
- Median create→terminal: `6240.857936859131` sec
- Median first breach→terminal: `6.699562072753906e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 2.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 5 | 5 | 0.7999999999999977 | 0.9617918313570496 | 0.8508441072533248 | 0 | 5 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 0.973374726944634 | 1.2124439590908107 | 0.9022124837965324 | 0 | 6 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 1.298790954599565 | 3.0 | 0.701654901068853 | 1 | 3 |
| MOVER_AVWAP_SCALP | 4 | 4 | 1.7481433639640176 | 2.12016347396299 | 0.8528252108754368 | 1 | 3 |
| MOVER_TREND_PULLBACK | 24 | 24 | 4.717809345441313 | 3.0 | 1.5808940046639468 | 20 | 4 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 1.043811617530825 | 1.1516902722167455 | 0.9159143602920614 | 0 | 6 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 5 | 5 | 20.0 | 60.0 | 20.0 | 0.0 | -0.1571 | 11129.123703956604 | 11129.125212907791 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 50.0 | 33.3 | 50.0 | 0.0 | 0.5537 | 13777.528640985489 | 13778.25554406643 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 75.0 | 0.0 | 75.0 | 0.0 | 3.5468 | 4057.5667974948883 | 4058.063581585884 |
| MOVER_AVWAP_SCALP | 4 | 4 | 25.0 | 50.0 | 25.0 | 0.0 | 0.5052 | 6295.203679442406 | 6295.203719973564 |
| MOVER_TREND_PULLBACK | 24 | 24 | 29.2 | 41.7 | 29.2 | 0.0 | 0.1166 | 1757.8211045265198 | 1758.3049964904785 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 25.0 | 50.0 | 25.0 | 0.0 | 0.3952 | 29063.009157896042 | 29063.760007977486 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 178 | 4 | 80 | 0.0 | 0.0 | None | None | 98 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1016 | 20 | 830 | 0.0 | 0.0 | None | None | 186 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-43`
- Gating Δ: `-36634`
- No-generation Δ: `-392588`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.2378, "current_avg_pnl": -0.1571, "current_win_rate": 20.0, "previous_avg_pnl": 0.0807, "previous_win_rate": 25.0, "win_rate_delta": -5.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.7674, "current_avg_pnl": 0.5537, "current_win_rate": 50.0, "previous_avg_pnl": -1.2137, "previous_win_rate": 0.0, "win_rate_delta": 50.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 3.5468, "current_avg_pnl": 3.5468, "current_win_rate": 75.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 75.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.2524, "current_avg_pnl": 0.5052, "current_win_rate": 25.0, "previous_avg_pnl": 0.2528, "previous_win_rate": 25.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.627, "current_avg_pnl": 0.1166, "current_win_rate": 29.2, "previous_avg_pnl": 0.7436, "previous_win_rate": 44.4, "win_rate_delta": -15.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.5409, "current_avg_pnl": 0.3952, "current_win_rate": 25.0, "previous_avg_pnl": -0.1457, "previous_win_rate": 33.3, "win_rate_delta": -8.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -128, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -12, "geometry_changed_delta": 0, "geometry_preserved_delta": -139, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **LIQUIDITY_SWEEP_REVERSAL**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
