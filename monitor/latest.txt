# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: MOVER_TREND_PULLBACK
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1565` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 39 | 39 | 39 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 18099 | 18099 | 15115 | 16 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 57150 | 57169 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 61372 | 61372 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 60558 | 56177 | 5175 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 61406 | 60699 | 788 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 61230 | 61074 | 190 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 49207 | 49224 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 61504 | 61549 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 61568 | 59305 | 4196 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 63190 | 68807 | 952 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 57188 | 52216 | 10908 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 60872 | 60872 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 61375 | 61400 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 60531 | 60498 | 55 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 63509 | 61113 | 3344 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 60138 | 60402 | 74 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 48047 | 45450 | 3008 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 48462 | 48268 | 279 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 57085 | 57137 | 6 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 49228 | 49248 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2754 | 2754 | 2614 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1994 | 1994 | 80 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 8 | 8 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 16431 | 16431 | 16074 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 3 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8080 | 8080 | 6683 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1926 | 1926 | 374 | 61 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 26297 | 26297 | 15059 | 234 | active-healthy (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 267 | 267 | 29 | 27 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 6701 | 6701 | 5672 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 286 | 286 | 69 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1195 | 1195 | 860 | 31 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 31 | 31 | 2 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=57169): breakout_not_found=32071, basic_filters_failed=18056, move_not_fresh=4666, breakout_stale=1678, retest_proximity_failed=614, volume_spike_missing=73, move_exhausted=9, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=61372): cls_disabled_merged_into_lsr=61372
- **EVAL::DIVERGENCE_CONTINUATION** (total=56177): cvd_divergence_failed=22973, basic_filters_failed=16171, h1_trend_not_aligned=11847, ema_alignment_reject=3415, retest_proximity_failed=1277, missing_fvg_or_orderblock=494
- **EVAL::FAILED_AUCTION_RECLAIM** (total=60699): auction_not_detected=35400, basic_filters_failed=15907, regime_blocked=5238, reclaim_hold_failed=2385, tail_too_small=1743, rsi_reject=26
- **EVAL::FUNDING_EXTREME** (total=61074): funding_not_extreme=33018, missing_funding_rate=13967, basic_filters_failed=11043, rsi_reject=1487, ema_alignment_reject=1305, cvd_divergence_failed=148, momentum_reject=100, missing_fvg_or_orderblock=6
- **EVAL::LIQUIDATION_REVERSAL** (total=49224): cascade_threshold_not_met=32489, basic_filters_failed=15962, cvd_divergence_failed=532, rsi_reject=209, missing_fvg_or_orderblock=25, volume_spike_missing=7
- **EVAL::MA_CROSS_TREND_SHIFT** (total=61549): no_ma_cross=44731, basic_filters_failed=16212, ma_cross_cooldown=315, ma_cross_htf_misaligned=291
- **EVAL::MEAN_REVERT** (total=59305): no_extension=51212, basic_filters_failed=8093
- **EVAL::MOVER_AVWAP_SCALP** (total=68807): no_avwap_tag=23561, no_mover_leg=19822, basic_filters_failed=18340, avwap_slope_against=4339, avwap_reclaim_no_volume=1617, no_avwap_reclaim=1114, anchor_too_recent=14
- **EVAL::MOVER_TREND_PULLBACK** (total=52216): mover_run_too_small=21877, basic_filters_failed=18203, no_reclaim=10451, no_pullback_tag=1685
- **EVAL::OPENING_RANGE_BREAKOUT** (total=60872): feature_disabled=60872
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=61400): regime_blocked=44518, breakout_not_found=10931, basic_filters_failed=3740, adx_reject=2166, ema_alignment_reject=37, rsi_reject=8
- **EVAL::QUIET_COMPRESSION_BREAK** (total=60498): compression_not_detected=23458, regime_blocked=21675, basic_filters_failed=12145, breakout_not_detected=2935, volume_confirmation_failed=276, missing_fvg_or_orderblock=9
- **EVAL::RANGE_FADE** (total=61113): no_range_edge=53010, basic_filters_failed=8103
- **EVAL::SR_FLIP_RETEST** (total=60402): flip_close_not_confirmed=33489, basic_filters_failed=15861, regime_blocked=5127, retest_out_of_zone=2025, long_break_volume_thin=1772, h1_break_not_confirmed=1512, reclaim_hold_failed=341, long_acceptance_not_held=178, whipsaw_flip=49, wick_quality_failed=30, ema_alignment_reject=14, missing_fvg_or_orderblock=4
- **EVAL::STANDARD** (total=45450): adx_reject=13034, momentum_reject=11570, sweeps_not_detected=6635, basic_filters_failed=6491, macd_reject=4293, ema_alignment_reject=2127, invalid_sl_geometry=682, htf_poi_unanchored=560, rsi_reject=54, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=48268): h1_trend_not_aligned=15044, h1_pullback_not_confirmed=8516, basic_filters_failed=8041, ema_alignment_reject=5319, ema_not_tested_prev=4337, no_ema_reclaim_close=2969, body_conviction_fail=1660, rsi_reject=1319, prev_already_below_emas=524, no_prev_low_break=248, prev_already_above_emas=94, no_prev_high_break=75, momentum_flat=71, ema21_not_tagged=24, momentum_reject=21, missing_fvg_or_orderblock=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=57137): breakout_not_found=28469, basic_filters_failed=18052, move_not_fresh=6973, breakout_stale=2231, retest_proximity_failed=1069, volume_spike_missing=222, move_exhausted=107, missing_fvg_or_orderblock=14
- **EVAL::WHALE_MOMENTUM** (total=49248): momentum_reject=36417, recent_ticks_insufficient=7770, basic_filters_failed=5061

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=2745): setup_compat:regime_VOLATILE_UNSUITABLE=2696, setup_compat:regime_BREAKOUT_EXPANSION=26, execution:overextended=23
- **FAILED_AUCTION_RECLAIM** (total=570): execution:overextended=301, setup_compat:regime_STRONG_TREND=231, setup_compat:regime_VOLATILE_UNSUITABLE=38
- **FUNDING_EXTREME_SIGNAL** (total=2267): execution:trigger_not_confirmed=1906, context_floor=361
- **LIQUIDATION_REVERSAL** (total=8): execution:trigger_not_confirmed=8
- **LIQUIDITY_SWEEP_REVERSAL** (total=4735): execution:overextended=2965, execution:trigger_not_confirmed=1310, setup_compat:regime_STRONG_TREND=460
- **MA_CROSS_TREND_SHIFT** (total=7): execution:trigger_not_confirmed=2, setup_compat:regime_VOLATILE_UNSUITABLE=2, setup_compat:regime_DIRTY_RANGE=1, execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=4440): execution:overextended=2524, setup_compat:regime_WEAK_TREND=1155, setup_compat:regime_STRONG_TREND=740, entry_quality=21
- **MOVER_AVWAP_SCALP** (total=1044): execution:overextended=637, entry_quality=236, execution:trigger_not_confirmed=171
- **MOVER_TREND_PULLBACK** (total=15763): execution:overextended=8504, execution:trigger_not_confirmed=5704, entry_quality=1555
- **QUIET_COMPRESSION_BREAK** (total=8): execution:trigger_not_confirmed=8
- **RANGE_FADE** (total=4592): setup_compat:regime_WEAK_TREND=1619, setup_compat:regime_STRONG_TREND=1390, execution:overextended=851, setup_compat:regime_VOLATILE_UNSUITABLE=717, context_edge=14, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=1127): setup_compat:regime_CLEAN_RANGE=769, setup_compat:regime_DIRTY_RANGE=291, entry_quality=55, setup_compat:regime_VOLATILE_UNSUITABLE=12
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 204180 | 52.5% |
| TRENDING_UP | 58153 | 15.0% |
| TRENDING_DOWN | 53124 | 13.7% |
| QUIET | 41234 | 10.6% |
| VOLATILE | 31948 | 8.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **58**
- Average confidence gap to threshold: **10.67** (samples=58) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=11, ONDOUSDT=10, TUSDT=5, SUIUSDT=5, BTCUSDT=4, BNBUSDT=4, BCHUSDT=4, MAGMAUSDT=3, XMRUSDT=3, QNTUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 488 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 105 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 110 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 5 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 3 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 209 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 90 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 51 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 6 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 476 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 372 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1179 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4632 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 45 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 17 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 126 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 52 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 43 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 20 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 8 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 169 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 17 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 493 | 56.82 | 64.45 | 7.63 | 21.21 | 19.92 | 16.96 | 0.75 | 11.31 |
| DIVERGENCE_CONTINUATION | kept | 105 | 68.98 | 65.00 | -3.98 | 21.42 | 19.57 | 16.83 | 1.74 | 1.50 |
| FAILED_AUCTION_RECLAIM | filtered | 115 | 46.43 | 63.16 | 16.73 | 21.20 | 18.89 | 20.00 | 1.93 | 9.13 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 65.03 | 65.00 | -0.03 | 20.70 | 20.00 | 20.00 | 2.83 | 2.30 |
| FUNDING_EXTREME_SIGNAL | filtered | 210 | 33.76 | 64.53 | 30.77 | 20.98 | 14.20 | 17.00 | 3.03 | 17.51 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 62.77 | 65.00 | 2.23 | 19.77 | 13.80 | 18.00 | 3.67 | 8.33 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 99 | 52.99 | 64.88 | 11.89 | 19.89 | 18.72 | 18.13 | 0.70 | 9.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 51 | 68.65 | 65.00 | -3.65 | 19.62 | 19.30 | 17.97 | 1.43 | -0.06 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.50 | 62.33 | 5.83 | 19.43 | 19.57 | 15.80 | 0.00 | 14.93 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.70 | 65.00 | -5.70 | 16.20 | 18.40 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 6 | 71.87 | 65.00 | -6.87 | 19.28 | 14.22 | 14.45 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 483 | 55.13 | 64.75 | 9.62 | 20.33 | 17.31 | 15.80 | 3.88 | 15.41 |
| MOVER_AVWAP_SCALP | kept | 372 | 78.20 | 65.00 | -13.20 | 20.21 | 16.27 | 15.80 | 4.45 | 3.80 |
| MOVER_TREND_PULLBACK | filtered | 1183 | 55.96 | 64.36 | 8.40 | 19.49 | 17.95 | 15.80 | 4.20 | 15.59 |
| MOVER_TREND_PULLBACK | kept | 4632 | 76.20 | 65.00 | -11.20 | 18.80 | 18.30 | 15.80 | 4.29 | 2.36 |
| QUIET_COMPRESSION_BREAK | filtered | 62 | 49.50 | 64.35 | 14.85 | 20.40 | 19.08 | 20.00 | 0.00 | 11.67 |
| QUIET_COMPRESSION_BREAK | kept | 126 | 75.03 | 65.00 | -10.03 | 21.33 | 19.72 | 20.00 | 0.00 | -1.62 |
| RANGE_FADE | kept | 1 | 74.30 | 65.00 | -9.30 | 20.50 | 14.60 | 19.40 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 53 | 51.61 | 62.68 | 11.07 | 20.01 | 20.00 | 18.46 | 2.35 | 14.27 |
| SR_FLIP_RETEST | kept | 43 | 70.40 | 65.00 | -5.40 | 20.82 | 20.00 | 15.30 | 2.00 | -0.64 |
| TREND_PULLBACK_EMA | filtered | 28 | 58.26 | 64.29 | 6.03 | 20.44 | 19.82 | 16.39 | 4.77 | 13.98 |
| TREND_PULLBACK_EMA | kept | 169 | 80.74 | 65.00 | -15.74 | 21.71 | 19.85 | 17.50 | 5.02 | -1.02 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 46.61 | 62.18 | 15.57 | 20.62 | 18.50 | 20.00 | 3.62 | 9.00 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 72.63 | 65.00 | -7.63 | 19.97 | 16.97 | 20.00 | 5.17 | 4.67 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 493 | 56.82 | 23.67 | 16.64 | 3.78 | 10.79 | 5.12 | 7.74 | 0.75 |
| DIVERGENCE_CONTINUATION | kept | 105 | 68.98 | 24.24 | 13.62 | 4.74 | 13.22 | 5.55 | 8.61 | 1.74 |
| FAILED_AUCTION_RECLAIM | filtered | 115 | 46.43 | 19.78 | 17.83 | 5.03 | 13.70 | 7.21 | 5.07 | 1.93 |
| FAILED_AUCTION_RECLAIM | kept | 3 | 65.03 | 25.00 | 16.67 | 5.00 | 11.67 | 8.17 | 8.00 | 2.83 |
| FUNDING_EXTREME_SIGNAL | filtered | 210 | 33.76 | 17.72 | 17.05 | 3.13 | 12.02 | 5.38 | 7.01 | 3.03 |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 62.77 | 22.33 | 14.67 | 5.00 | 10.00 | 8.00 | 7.43 | 3.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 99 | 52.99 | 23.97 | 15.05 | 5.97 | 12.53 | 6.01 | 6.81 | 0.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 51 | 68.65 | 23.24 | 15.57 | 3.35 | 12.45 | 5.09 | 7.53 | 1.43 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.50 | 22.33 | 14.00 | 7.00 | 12.33 | 7.33 | 8.43 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.70 | 25.00 | 14.00 | 9.00 | 10.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 6 | 71.87 | 15.67 | 18.00 | 12.50 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 483 | 55.13 | 17.87 | 18.00 | 12.31 | 14.06 | 6.32 | 6.41 | 3.88 |
| MOVER_AVWAP_SCALP | kept | 372 | 78.20 | 19.90 | 18.04 | 11.81 | 14.06 | 7.77 | 8.10 | 4.45 |
| MOVER_TREND_PULLBACK | filtered | 1183 | 55.96 | 18.52 | 18.10 | 7.83 | 12.65 | 5.96 | 8.58 | 4.20 |
| MOVER_TREND_PULLBACK | kept | 4632 | 76.20 | 18.14 | 18.75 | 7.64 | 13.50 | 6.84 | 9.44 | 4.29 |
| QUIET_COMPRESSION_BREAK | filtered | 62 | 49.50 | 18.55 | 15.10 | 11.61 | 14.19 | 5.97 | 6.15 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 126 | 75.03 | 18.84 | 17.30 | 11.55 | 14.50 | 7.27 | 6.34 | 0.00 |
| RANGE_FADE | kept | 1 | 74.30 | 25.00 | 18.00 | 9.00 | 12.00 | 5.00 | 5.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 53 | 51.61 | 24.09 | 17.81 | 3.00 | 13.94 | 5.00 | 5.05 | 2.35 |
| SR_FLIP_RETEST | kept | 43 | 70.40 | 21.84 | 15.91 | 3.49 | 14.28 | 5.73 | 7.42 | 2.00 |
| TREND_PULLBACK_EMA | filtered | 28 | 58.26 | 14.86 | 18.00 | 7.55 | 14.00 | 5.75 | 8.37 | 4.77 |
| TREND_PULLBACK_EMA | kept | 169 | 80.74 | 20.98 | 18.00 | 7.61 | 14.07 | 7.38 | 8.69 | 5.02 |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 46.61 | 20.29 | 14.00 | 12.00 | 11.00 | 5.00 | 4.70 | 3.62 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 72.63 | 22.33 | 15.33 | 12.00 | 14.00 | 5.00 | 8.47 | 5.17 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 493 | 56.82 | 0.00 | 0.00 | 0.21 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.33** |
| DIVERGENCE_CONTINUATION | kept | 105 | 68.98 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| FAILED_AUCTION_RECLAIM | filtered | 115 | 46.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 3 | 65.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 210 | 33.76 | 0.00 | 0.00 | 10.93 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **11.03** |
| FUNDING_EXTREME_SIGNAL | kept | 3 | 62.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 99 | 52.99 | 0.00 | 0.00 | 1.13 | 0.00 | 0.87 | 0.00 | 0.00 | 0.00 | **2.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 51 | 68.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.50 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 70.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 6 | 71.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 483 | 55.13 | 0.00 | 0.00 | 1.16 | 0.00 | 2.16 | 0.00 | 0.00 | 0.73 | **4.05** |
| MOVER_AVWAP_SCALP | kept | 372 | 78.20 | 0.00 | 0.00 | 0.10 | 0.00 | 0.10 | 0.00 | 0.00 | 0.32 | **0.52** |
| MOVER_TREND_PULLBACK | filtered | 1183 | 55.96 | 0.00 | 0.00 | 1.71 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **2.07** |
| MOVER_TREND_PULLBACK | kept | 4632 | 76.20 | 0.00 | 0.00 | 2.02 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **2.09** |
| QUIET_COMPRESSION_BREAK | filtered | 62 | 49.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.93 | 0.74 | 0.00 | 2.59 | **4.26** |
| QUIET_COMPRESSION_BREAK | kept | 126 | 75.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | **0.14** |
| RANGE_FADE | kept | 1 | 74.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 53 | 51.61 | 0.00 | 0.00 | 2.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.48 | **2.74** |
| SR_FLIP_RETEST | kept | 43 | 70.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 28 | 58.26 | 0.00 | 0.00 | 0.94 | 0.00 | 5.49 | 0.00 | 0.00 | 0.00 | **6.43** |
| TREND_PULLBACK_EMA | kept | 169 | 80.74 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.18** |
| VOLUME_SURGE_BREAKOUT | filtered | 17 | 46.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 72.63 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |

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
- Outcomes recorded: **161626 held of 631562 seen** across 21 strategies; 3642 cells past the sample floor; **1898 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 46127 | 682/45445/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.27R) |
| MOVER_AVWAP_SCALP | 21029 | 185/20844/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 11828 | 129/11699/0 | 48% | -0.06 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 11806 | 129/11677/0 | 38% | -0.27 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| TREND_PULLBACK_EMA | 9934 | 45/9889/0 | 40% | -0.24 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/RANGE/NORMAL/BTC_FALLING (-1.32R) |
| LIQUIDITY_SWEEP_REVERSAL | 8828 | 99/8729/0 | 35% | -0.47 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7597 | 0/0/7597 | 42% | -0.10 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.48R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.11R) |
| SHADOW_RANGE_FADE | 7108 | 0/0/7108 | 36% | -0.14 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.54R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.21R) |
| QUIET_COMPRESSION_BREAK | 6844 | 407/6437/0 | 50% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 6401 | 0/0/6401 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| MEAN_REVERT | 4577 | 50/4527/0 | 38% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| SR_FLIP_RETEST | 4417 | 19/4398/0 | 44% | -0.27 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3589 | 2/3587/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3310 | 0/3310/0 | 31% | -0.34 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| RANGE_FADE | 1839 | 6/1833/0 | 34% | -0.50 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+2.15R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1474 | 0/0/1474 | 53% | -0.06 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 396 | 0/396/0 | 29% | -0.63 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 144 | 30/114/0 | 42% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 287 | 27% / -0.59R | 287 | 54% / -0.09R | +0.50 | **ATR** |
| LIQUIDATION_REVERSAL | 23 | 26% / -0.63R | 23 | 52% / -0.26R | +0.37 | **ATR** |
| TREND_PULLBACK_EMA | 861 | 39% / -0.33R | 861 | 52% / -0.07R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1374 | 43% / -0.35R | 1374 | 56% / -0.12R | +0.23 | **ATR** |
| RANGE_FADE | 92 | 33% / -0.35R | 92 | 40% / -0.20R | +0.15 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 167 | 34% / -0.22R | 167 | 46% / -0.07R | +0.15 | **ATR** |
| MOVER_AVWAP_SCALP | 2076 | 44% / -0.18R | 2076 | 50% / -0.05R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 412 | 43% / -0.29R | 412 | 46% / -0.17R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1159 | 40% / -0.24R | 1159 | 42% / -0.14R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8197 | 50% / -0.11R | 8197 | 55% / -0.01R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| MA_CROSS_TREND_SHIFT | 46 | 39% / -0.17R | 46 | 41% / -0.08R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 1314 | 48% / -0.10R | 1314 | 54% / -0.04R | +0.06 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1188 | 49% / -0.13R | 1188 | 49% / -0.13R | -0.01 | **FIXED** |
| MEAN_REVERT | 320 | 47% / -0.18R | 320 | 46% / -0.18R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11043 | 28% | -0.22R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2076 | 48% | -0.05R | 227 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 105 | 47% | -0.07R | 63 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1550 | 40% / -0.13R | +0.88 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1145 | 34% / -0.20R | +0.86 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2536 | 35% / -0.12R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10051 | 37% / -0.11R | +0.42 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1510 | 38% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1153 | 36% / -0.13R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 969 | 32% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 243 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 378 | 32% / -0.10R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 266 | 48% / -0.06R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 69 | 41% / -0.07R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 374 | 33% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 69 | 29% / -0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 29 | 41% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×1291]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 83/6) (sustained 83 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 140/6) (sustained 140 cycles)
- **ALERT** `tuned_variants` — 148 non-stamps — atr_arm_uncomputable=148 (seen=5129 stamped=295 skipped=4686) (streak 140/6) (sustained 140 cycles)
- **ALERT** `auto_dispatch` — 25 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=25) (streak 133/3) (sustained 133 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 46 fed / 0 quiet / 0 never delivered of 46 subscribed; 31673076 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 17 arms current, none stalled; covering 2013/2013 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 31 arms current, none stalled; covering 1049/1049 signals (100%) | 0 |
| auto_dispatch | violating | 25 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=25) (streak 133/3) | 133 |
| binance_ip_weight | ok | peak 198/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 79856.00 | 0 |
| candle_coverage | ok | 84/84 symbols with ≥20 15m candles, 84/84 updated within 45m [fresh=84; 75 Tier-1 futures + 9 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 2924 dup bars, 0 undedupable; ws 0 out-of-order, 267 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +12 / upstream +30 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1367/1386 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 78 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1360/1379 signals (99%) | 0 |
| depth_feed | ok | 46/46 books fresh (stale 0, never 0, thin 0); 5550901 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.56R (bound 0.3) (streak 140/6) | 140 |
| emission_controller | ok | last cycle 368s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×1291]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 83/6) | 83 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| firestore_read_budget | ok | 1,344 reads/day of 50,000 [engine 1,308, signing 36]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5520 sealed bars over 46 symbols; 1174 incomplete, 6 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +228 | 0 |
| indicator_cache_key | ok | 15070 frozen value(s) avoided; 118047 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=4527 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +228 but output +0 (streak 1/72) | 1 |
| mover_admission_metadata | ok | 936 symbols known, 229 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 9 held, 9 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2355 rows held, 3149980 evicted (sampled: execution:trigger_not_confirmed 315/1112942, execution:overextended 315/989219, setup_compat:regime_STRONG_TREND 315/531802) | 0 |
| price_action_lane | ok | 310733 evaluated, 261 emitted; layer1 261 stamped / 0 blind; cooldown=31852, delta_opposed=36212, no_footprint=123203, no_opposing_target=419, no_sweep=83732, rr_below_floor=35054 | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.50R over n=1833 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +40 / upstream +228 | 0 |
| sar_alignment_crosscheck | ok | 83/6806 disagreed (1.2%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +228 | 0 |
| sar_hold_arm | ok | 1861 held arms settled, 139 unscored, 31 still walking (26 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/40 unfetchable (10%); top cause: located bar does not contain the stamp; symbols: AINUSDT, ARIAUSDT, CHIPUSDT | 0 |
| sar_live_arms | ok | 31 arms current, none stalled; covering 1047/1047 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 440 records await one (36 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 17.13s, worst 186.64s over 7431 lifetime cycles; lifetime 96 over 60s, 15 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.11s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 134289 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 4s ago (38.38s to run, worst 178.9s), 370 overrun(s) of 3160 cycles, TTL 900s; slowest activity=12.16s, alerts=4.04s, user_positions=2.03s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=6959, gate reads=0, withheld=6959) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +44 / upstream +228 | 0 |
| structural_snap | ok | 6000/6000 measured, 36 blind, 0 levels moved (refusals: redetect_cooldown=2536) | 0 |
| structural_veto_lane | ok | 2793 stamped; 0 with no readable level book, 3 with clear air ahead, 2345 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +228 / upstream +30 | 0 |
| tuned_variants | violating | 148 non-stamps — atr_arm_uncomputable=148 (seen=5129 stamped=295 skipped=4686) (streak 140/6) | 140 |
| unlock_shorts | ok | 13 open, 46 scheduled, calendar 5.2h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 21 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1918278`
- `Path funnel` emissions: `83`
- `Regime distribution` emissions: `83`
- `QUIET_SCALP_BLOCK` events: `58`
- `confidence_gate` events: `8261`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **339**
- Total REST-fallback activations: **6**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 6 | 2691 | 13374 | 45572 | 0 |
| futures_aggtrade | 154 | 2512 | 13898 | 43531 | 0 |
| futures_depth | 153 | 2353 | 9544 | 27897 | 0 |
| futures_mover | 26 | 2421 | 5318 | 6517 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 6 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=271338] state[populated=271338] buckets[many=271338] sources[none] quality[none]
- funding_rate: presence[absent=56003, present=215335] state[empty=56003, populated=215335] buckets[few=215335, none=56003] sources[none] quality[none]
- liquidation_clusters: presence[absent=180687, present=90651] state[empty=180687, populated=90651] buckets[few=74151, none=180687, some=16500] sources[none] quality[none]
- oi_snapshot: presence[absent=55488, present=215850] state[empty=55488, populated=215850] buckets[few=214, many=214683, none=55488, some=953] sources[none] quality[none]
- order_book: presence[absent=102397, present=168941] state[populated=168941, unavailable=102397] buckets[few=168941, none=102397] sources[book_ticker=168941, unavailable=102397] quality[none=102397, top_of_book_only=168941]
- orderblocks: presence[absent=271338] state[empty=271338] buckets[none=271338] sources[measured_dark=271338] quality[none]
- recent_ticks: presence[present=271338] state[populated=271338] buckets[many=271338] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.1051729917526245` sec
- Median create→first breach: `6057.766492962837` sec
- Median create→terminal: `6059.05710208416` sec
- Median first breach→terminal: `6.496906280517578e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 4 | 0.9009615615077462 | 1.00415337015314 | 0.8991729171894421 | 0 | 4 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.2136665888940814 | 1.4321465985998652 | 0.8474457783027378 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 5.192049830124569 | 2.810681489241232 | 1.8472565639325458 | 1 | 0 |
| MEAN_REVERT | 1 | 1 | 1.2278500862474502 | 1.365846009095184 | 0.8989667049368542 | 0 | 1 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.4678773554995947 | 2.5232585714285727 | 0.9747434235208763 | 1 | 2 |
| MOVER_TREND_PULLBACK | 20 | 20 | 3.959071382043552 | 3.0 | 1.3196904606811841 | 16 | 4 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 0.9593070572642564 | 1.1095597360392695 | 0.8780119525137161 | 0 | 6 |
| RANGE_FADE | 1 | 1 | 0.9125679393410792 | 1.2614909749714842 | 0.7234042553191533 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 4 | 25.0 | 25.0 | 25.0 | 0.0 | 0.0807 | 8585.085761070251 | 8585.731326460838 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.2137 | 12977.931896924973 | 12977.931952953339 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 26249.759438037872 | 26249.759502887726 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1801.0410830974579 | 1801.0411450862885 |
| MOVER_AVWAP_SCALP | 4 | 4 | 25.0 | 25.0 | 25.0 | 0.0 | 0.2528 | 6384.0728640556335 | 6385.884707093239 |
| MOVER_TREND_PULLBACK | 20 | 20 | 45.0 | 35.0 | 45.0 | 0.0 | 1.0001 | 3425.1135100126266 | 3425.3268514871597 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 33.3 | 66.7 | 33.3 | 0.0 | -0.1457 | 14715.50031888485 | 14715.500359416008 |
| RANGE_FADE | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2868.4888129234314 | 2868.4888339042664 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 286 | 8 | 69 | 0.0 | 0.0 | None | None | 217 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1195 | 31 | 860 | 0.0 | 0.0 | None | None | 335 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-140`
- Gating Δ: `16960`
- No-generation Δ: `117142`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.6796, "current_avg_pnl": 0.0807, "current_win_rate": 25.0, "previous_avg_pnl": 0.7603, "previous_win_rate": 75.0, "win_rate_delta": -50.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.8458, "current_avg_pnl": 0.2528, "current_win_rate": 25.0, "previous_avg_pnl": 2.0986, "previous_win_rate": 66.7, "win_rate_delta": -41.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.1122, "current_avg_pnl": 1.0001, "current_win_rate": 45.0, "previous_avg_pnl": -1.1121, "previous_win_rate": 12.5, "win_rate_delta": 32.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.591, "current_avg_pnl": -0.1457, "current_win_rate": 33.3, "previous_avg_pnl": 0.4453, "previous_win_rate": 41.7, "win_rate_delta": -8.4}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 89, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -15, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -6312.05, "median_terminal_delta_sec": -6312.05, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **BREAKDOWN_SHORT**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
