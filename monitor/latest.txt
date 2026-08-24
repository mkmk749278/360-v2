# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `447` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 120 | 120 | 106 | 6 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6225 | 6225 | 5355 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 71041 | 71058 | 45 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 57068 | 57082 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 56716 | 55117 | 1931 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 57114 | 56351 | 839 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 57462 | 57356 | 135 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 47508 | 47521 | 7 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 57194 | 57225 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 57233 | 55539 | 2400 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 76062 | 82362 | 795 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 71106 | 62615 | 13365 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 56829 | 56843 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 57083 | 57103 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 56693 | 56563 | 152 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 57947 | 57093 | 1251 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 56046 | 56445 | 208 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 46239 | 43506 | 3139 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 46658 | 46372 | 382 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 70963 | 71021 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 47533 | 47556 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2873 | 2873 | 2452 | 14 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 553 | 553 | 68 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 15 | 15 | 13 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15677 | 15677 | 15566 | 10 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 14 | 14 | 9 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6389 | 6389 | 5340 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2168 | 2168 | 846 | 44 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 30381 | 30381 | 20624 | 368 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 409 | 409 | 173 | 22 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 3323 | 3323 | 3163 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 745 | 745 | 721 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1479 | 1479 | 997 | 52 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 49 | 49 | 6 | 6 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=71058): breakout_not_found=43221, basic_filters_failed=13220, move_not_fresh=9932, breakout_stale=3133, retest_proximity_failed=1350, volume_spike_missing=170, insufficient_candles=28, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=57082): cls_disabled_merged_into_lsr=57082
- **EVAL::DIVERGENCE_CONTINUATION** (total=55117): cvd_divergence_failed=24735, h1_trend_not_aligned=15682, basic_filters_failed=8950, ema_alignment_reject=5146, retest_proximity_failed=363, missing_fvg_or_orderblock=241
- **EVAL::FAILED_AUCTION_RECLAIM** (total=56351): auction_not_detected=39668, basic_filters_failed=8743, reclaim_hold_failed=3747, tail_too_small=2284, regime_blocked=1892, rsi_reject=17
- **EVAL::FUNDING_EXTREME** (total=57356): funding_not_extreme=43053, basic_filters_failed=7609, missing_funding_rate=4925, ema_alignment_reject=989, rsi_reject=498, cvd_divergence_failed=143, momentum_reject=100, missing_fvg_or_orderblock=36, insufficient_candles=3
- **EVAL::LIQUIDATION_REVERSAL** (total=47521): cascade_threshold_not_met=38121, basic_filters_failed=8779, rsi_reject=326, cvd_divergence_failed=256, insufficient_candles=20, missing_fvg_or_orderblock=17, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=57225): no_ma_cross=46607, basic_filters_failed=8978, ma_cross_cooldown=1340, ma_cross_htf_misaligned=272, ma_cross_htf_unconfirmed=28
- **EVAL::MEAN_REVERT** (total=55539): no_extension=47500, basic_filters_failed=8039
- **EVAL::MOVER_AVWAP_SCALP** (total=82362): no_avwap_tag=37586, no_mover_leg=16897, basic_filters_failed=13457, avwap_slope_against=9418, avwap_reclaim_no_volume=3014, no_avwap_reclaim=1847, insufficient_candles=116, anchor_too_recent=27
- **EVAL::MOVER_TREND_PULLBACK** (total=62615): mover_run_too_small=27046, no_reclaim=19915, basic_filters_failed=13357, no_pullback_tag=2181, insufficient_candles=116
- **EVAL::OPENING_RANGE_BREAKOUT** (total=56843): feature_disabled=56843
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=57103): regime_blocked=36456, breakout_not_found=15678, basic_filters_failed=3183, adx_reject=1725, ema_alignment_reject=61
- **EVAL::QUIET_COMPRESSION_BREAK** (total=56563): compression_not_detected=25976, regime_blocked=22400, basic_filters_failed=5544, breakout_not_detected=2393, volume_confirmation_failed=239, rsi_reject=11
- **EVAL::RANGE_FADE** (total=57093): no_range_edge=49048, basic_filters_failed=8045
- **EVAL::SR_FLIP_RETEST** (total=56445): flip_close_not_confirmed=39461, basic_filters_failed=8709, long_break_volume_thin=2187, regime_blocked=1876, retest_out_of_zone=1826, h1_break_not_confirmed=1078, reclaim_hold_failed=808, ema_alignment_reject=173, whipsaw_flip=131, wick_quality_failed=99, long_acceptance_not_held=88, missing_fvg_or_orderblock=9
- **EVAL::STANDARD** (total=43506): momentum_reject=13343, adx_reject=9000, basic_filters_failed=6016, sweeps_not_detected=4981, macd_reject=4753, ema_alignment_reject=4446, htf_poi_unanchored=823, invalid_sl_geometry=122, rsi_reject=21, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=46372): h1_trend_not_aligned=14270, ema_alignment_reject=8896, h1_pullback_not_confirmed=6223, basic_filters_failed=5536, ema_not_tested_prev=4105, no_ema_reclaim_close=3226, body_conviction_fail=1728, rsi_reject=1281, prev_already_above_emas=455, no_prev_high_break=223, prev_already_below_emas=126, no_prev_low_break=114, momentum_flat=80, ema21_not_tagged=45, missing_fvg_or_orderblock=43, momentum_reject=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=71021): breakout_not_found=42413, basic_filters_failed=13217, move_not_fresh=10764, breakout_stale=3421, retest_proximity_failed=962, volume_spike_missing=206, insufficient_candles=28, missing_fvg_or_orderblock=8, move_exhausted=2
- **EVAL::WHALE_MOMENTUM** (total=47556): momentum_reject=34131, recent_ticks_insufficient=10478, basic_filters_failed=2947

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=15): execution:overextended=15
- **DIVERGENCE_CONTINUATION** (total=100): setup_compat:regime_VOLATILE_UNSUITABLE=85, setup_compat:regime_BREAKOUT_EXPANSION=15
- **FAILED_AUCTION_RECLAIM** (total=1136): setup_compat:regime_STRONG_TREND=593, execution:overextended=543
- **FUNDING_EXTREME_SIGNAL** (total=461): execution:trigger_not_confirmed=455, context_floor=6
- **LIQUIDATION_REVERSAL** (total=15): execution:trigger_not_confirmed=15
- **LIQUIDITY_SWEEP_REVERSAL** (total=3999): execution:overextended=1747, execution:trigger_not_confirmed=1356, setup_compat:regime_STRONG_TREND=896
- **MA_CROSS_TREND_SHIFT** (total=17): setup_compat:regime_DIRTY_RANGE=8, execution:trigger_not_confirmed=4, execution:overextended=4, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=3230): setup_compat:regime_WEAK_TREND=1650, setup_compat:regime_STRONG_TREND=1272, execution:overextended=308
- **MOVER_AVWAP_SCALP** (total=1177): execution:overextended=521, entry_quality=373, execution:trigger_not_confirmed=283
- **MOVER_TREND_PULLBACK** (total=14188): execution:trigger_not_confirmed=8752, execution:overextended=3744, entry_quality=1692
- **QUIET_COMPRESSION_BREAK** (total=22): execution:overextended=22
- **RANGE_FADE** (total=1500): setup_compat:regime_STRONG_TREND=758, setup_compat:regime_WEAK_TREND=521, setup_compat:regime_VOLATILE_UNSUITABLE=158, setup_compat:regime_BREAKOUT_EXPANSION=59, execution:overextended=4
- **TREND_PULLBACK_EMA** (total=1405): setup_compat:regime_CLEAN_RANGE=647, setup_compat:regime_DIRTY_RANGE=618, entry_quality=128, setup_compat:regime_VOLATILE_UNSUITABLE=12

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 155272 | 46.5% |
| TRENDING_DOWN | 68583 | 20.6% |
| TRENDING_UP | 63040 | 18.9% |
| QUIET | 37346 | 11.2% |
| VOLATILE | 9398 | 2.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **54**
- Average confidence gap to threshold: **8.97** (samples=54) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: POLUSDT=20, LTCUSDT=8, FILUSDT=7, XLMUSDT=6, 1000SHIBUSDT=5, HYPEUSDT=4, 1000PEPEUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 3 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 9 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 112 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 78 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 136 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 5 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 88 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 83 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 15 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 12 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 80 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 22 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 528 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 566 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 20 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3392 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 56 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 21 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 103 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 54 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 165 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 5 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 13 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 58.20 | 61.00 | 2.80 | 20.60 | 18.00 | 20.00 | 3.50 | 14.60 |
| BREAKDOWN_SHORT | kept | 9 | 75.43 | 65.00 | -10.43 | 20.12 | 17.78 | 20.00 | 4.67 | 2.67 |
| DIVERGENCE_CONTINUATION | filtered | 116 | 52.86 | 65.00 | 12.14 | 20.75 | 19.39 | 18.18 | 2.78 | 12.26 |
| DIVERGENCE_CONTINUATION | kept | 78 | 71.29 | 65.00 | -6.29 | 20.73 | 19.37 | 18.28 | 0.49 | -0.31 |
| FAILED_AUCTION_RECLAIM | filtered | 141 | 53.65 | 65.00 | 11.35 | 19.84 | 19.22 | 20.00 | 1.88 | 6.82 |
| FAILED_AUCTION_RECLAIM | kept | 88 | 67.68 | 65.00 | -2.68 | 20.12 | 19.00 | 20.00 | 1.87 | 1.52 |
| FUNDING_EXTREME_SIGNAL | filtered | 83 | 47.29 | 65.00 | 17.71 | 20.90 | 14.58 | 17.00 | 3.41 | 10.60 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 72.00 | 65.00 | -7.00 | 21.90 | 20.00 | 17.00 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 57.70 | 61.00 | 3.30 | 20.30 | 20.00 | 15.40 | 5.00 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 15 | 69.15 | 65.00 | -4.15 | 20.39 | 18.45 | 17.97 | 2.60 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 36.50 | 61.00 | 24.50 | 21.20 | 18.70 | 15.80 | 0.00 | 27.20 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.95 | 65.00 | -1.95 | 20.60 | 15.90 | 15.80 | 0.00 | 2.40 |
| MEAN_REVERT | kept | 12 | 70.17 | 65.00 | -5.17 | 22.57 | 15.92 | 13.78 | 0.00 | 4.67 |
| MOVER_AVWAP_SCALP | filtered | 102 | 56.96 | 53.14 | -3.82 | 20.08 | 13.45 | 15.80 | 3.94 | 5.19 |
| MOVER_AVWAP_SCALP | kept | 528 | 76.98 | 65.00 | -11.98 | 20.61 | 16.46 | 15.80 | 4.60 | 4.50 |
| MOVER_TREND_PULLBACK | filtered | 586 | 55.92 | 64.36 | 8.44 | 20.25 | 18.02 | 15.80 | 4.35 | 12.70 |
| MOVER_TREND_PULLBACK | kept | 3392 | 77.66 | 65.00 | -12.66 | 20.16 | 18.37 | 15.80 | 4.41 | 1.07 |
| QUIET_COMPRESSION_BREAK | filtered | 77 | 57.06 | 64.74 | 7.68 | 20.21 | 18.79 | 20.00 | 0.00 | 3.03 |
| QUIET_COMPRESSION_BREAK | kept | 103 | 76.93 | 65.00 | -11.93 | 19.86 | 19.15 | 20.00 | 0.00 | -1.92 |
| SR_FLIP_RETEST | kept | 1 | 69.70 | 65.00 | -4.70 | 20.50 | 20.00 | 19.00 | 3.50 | 3.50 |
| TREND_PULLBACK_EMA | filtered | 58 | 60.91 | 63.88 | 2.97 | 20.92 | 19.28 | 18.63 | 4.66 | 11.41 |
| TREND_PULLBACK_EMA | kept | 165 | 78.33 | 65.00 | -13.33 | 20.62 | 19.90 | 17.66 | 4.78 | -0.02 |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 62.00 | 65.00 | 3.00 | 20.84 | 19.36 | 20.00 | 4.80 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 77.55 | 65.00 | -12.55 | 20.42 | 18.93 | 20.00 | 5.38 | 1.75 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 58.20 | 15.00 | 18.00 | 12.00 | 17.00 | 5.00 | 2.30 | 3.50 |
| BREAKDOWN_SHORT | kept | 9 | 75.43 | 18.89 | 17.56 | 12.33 | 13.67 | 5.00 | 6.32 | 4.67 |
| DIVERGENCE_CONTINUATION | filtered | 116 | 52.86 | 22.31 | 11.97 | 5.28 | 13.93 | 5.50 | 7.94 | 2.78 |
| DIVERGENCE_CONTINUATION | kept | 78 | 71.29 | 22.95 | 13.77 | 6.88 | 13.36 | 6.26 | 9.35 | 0.49 |
| FAILED_AUCTION_RECLAIM | filtered | 141 | 53.65 | 19.82 | 16.16 | 7.57 | 13.04 | 5.17 | 8.10 | 1.88 |
| FAILED_AUCTION_RECLAIM | kept | 88 | 67.68 | 18.27 | 15.23 | 6.92 | 13.49 | 5.96 | 7.64 | 1.87 |
| FUNDING_EXTREME_SIGNAL | filtered | 83 | 47.29 | 24.71 | 8.00 | 8.86 | 11.04 | 8.01 | 7.96 | 3.41 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 72.00 | 17.00 | 18.00 | 3.00 | 14.00 | 10.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 57.70 | 25.00 | 14.00 | 3.00 | 9.00 | 5.00 | 4.70 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 15 | 69.15 | 23.40 | 14.80 | 4.60 | 12.40 | 5.27 | 6.08 | 2.60 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 36.50 | 25.00 | 14.00 | 9.00 | 12.00 | 10.00 | 8.70 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.95 | 21.00 | 14.00 | 7.50 | 14.00 | 5.00 | 7.85 | 0.00 |
| MEAN_REVERT | kept | 12 | 70.17 | 22.33 | 14.67 | 12.25 | 13.00 | 5.00 | 7.58 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 102 | 56.96 | 18.08 | 18.00 | 11.96 | 12.03 | 6.67 | 5.30 | 3.94 |
| MOVER_AVWAP_SCALP | kept | 528 | 76.98 | 18.91 | 18.01 | 11.42 | 13.44 | 6.74 | 8.60 | 4.60 |
| MOVER_TREND_PULLBACK | filtered | 586 | 55.92 | 18.65 | 18.00 | 7.73 | 12.72 | 5.56 | 8.71 | 4.35 |
| MOVER_TREND_PULLBACK | kept | 3392 | 77.66 | 19.35 | 18.02 | 7.98 | 13.00 | 6.59 | 9.55 | 4.41 |
| QUIET_COMPRESSION_BREAK | filtered | 77 | 57.06 | 17.10 | 15.09 | 11.22 | 14.23 | 5.50 | 8.78 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 103 | 76.93 | 18.48 | 16.52 | 12.87 | 14.00 | 7.08 | 8.74 | 0.00 |
| SR_FLIP_RETEST | kept | 1 | 69.70 | 25.00 | 18.00 | 6.00 | 11.00 | 5.00 | 4.70 | 3.50 |
| TREND_PULLBACK_EMA | filtered | 58 | 60.91 | 16.67 | 18.00 | 7.63 | 14.41 | 6.59 | 8.76 | 4.66 |
| TREND_PULLBACK_EMA | kept | 165 | 78.33 | 18.55 | 18.01 | 7.59 | 14.51 | 6.84 | 9.42 | 4.78 |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 62.00 | 15.80 | 18.00 | 12.00 | 12.80 | 5.00 | 5.60 | 4.80 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 77.55 | 23.77 | 16.77 | 12.00 | 12.62 | 4.42 | 7.81 | 5.38 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 58.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| BREAKDOWN_SHORT | kept | 9 | 75.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | **1.00** |
| DIVERGENCE_CONTINUATION | filtered | 116 | 52.86 | 0.00 | 0.00 | 2.12 | 0.00 | 1.24 | 0.00 | 0.00 | 0.00 | **3.36** |
| DIVERGENCE_CONTINUATION | kept | 78 | 71.29 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| FAILED_AUCTION_RECLAIM | filtered | 141 | 53.65 | 0.00 | 0.00 | 0.28 | 0.00 | 0.77 | 0.48 | 0.00 | 0.00 | **1.53** |
| FAILED_AUCTION_RECLAIM | kept | 88 | 67.68 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.09** |
| FUNDING_EXTREME_SIGNAL | filtered | 83 | 47.29 | 0.00 | 0.00 | 5.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.78** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 57.70 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 15 | 69.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 36.50 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.95 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| MEAN_REVERT | kept | 12 | 70.17 | 0.00 | 0.00 | 4.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.67** |
| MOVER_AVWAP_SCALP | filtered | 102 | 56.96 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.20 | 0.00 | 0.56 | **1.07** |
| MOVER_AVWAP_SCALP | kept | 528 | 76.98 | 0.00 | 0.00 | 0.22 | 0.00 | 4.25 | 0.00 | 0.00 | 0.10 | **4.57** |
| MOVER_TREND_PULLBACK | filtered | 586 | 55.92 | 0.00 | 0.00 | 2.83 | 0.00 | 0.90 | 0.22 | 0.00 | 0.00 | **3.95** |
| MOVER_TREND_PULLBACK | kept | 3392 | 77.66 | 0.00 | 0.00 | 0.84 | 0.00 | 0.28 | 0.03 | 0.00 | 0.00 | **1.15** |
| QUIET_COMPRESSION_BREAK | filtered | 77 | 57.06 | 0.00 | 0.00 | 1.60 | 0.00 | 0.72 | 1.35 | 0.00 | 1.23 | **4.90** |
| QUIET_COMPRESSION_BREAK | kept | 103 | 76.93 | 0.00 | 0.00 | 0.30 | 0.00 | 0.28 | 0.19 | 0.00 | 0.16 | **0.93** |
| SR_FLIP_RETEST | kept | 1 | 69.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 58 | 60.91 | 0.00 | 0.00 | 2.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.68** |
| TREND_PULLBACK_EMA | kept | 165 | 78.33 | 0.00 | 0.00 | 1.25 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **1.40** |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 62.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 77.55 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.37** |

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
- Outcomes recorded: **30459 held of 60695 seen** across 20 strategies; 661 cells past the sample floor; **280 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 19190 | 60/19130/0 | 47% | -0.15 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | ASIA/MARKUP/EXPANDED/BTC_RISING/MIDCAP (-1.14R) |
| MOVER_AVWAP_SCALP | 2670 | 8/2662/0 | 32% | -0.41 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.85R) | ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.36R) |
| SHADOW_MEAN_REVERT | 1493 | 0/0/1493 | 38% | -0.17 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.46R) | NY/RANGE/EXPANDED/BTC_RISING (-0.89R) |
| TREND_PULLBACK_EMA | 1307 | 0/1307/0 | 41% | -0.23 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SHADOW_RANGE_FADE | 1229 | 0/0/1229 | 32% | -0.15 | ASIA/MARKUP/CASCADE/BTC_RISING (+0.23R) | LONDON/RANGE/NORMAL/BTC_RISING (-0.96R) |
| DIVERGENCE_CONTINUATION | 1060 | 0/1060/0 | 65% | +0.24 | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (+1.00R) | NY/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.13R) |
| WHALE_MOMENTUM | 692 | 0/692/0 | 30% | -0.47 | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.00R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| FAILED_AUCTION_RECLAIM | 685 | 10/675/0 | 24% | -0.52 | OFF_HOURS/DISTRIBUTION/NORMAL/BTC_RISING (-0.11R) | OVERLAP/MARKUP/NORMAL/BTC_RISING (-1.19R) |
| SHADOW_FUNDING_FADE | 616 | 0/0/616 | 45% | -0.22 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-0.62R) |
| QUIET_COMPRESSION_BREAK | 378 | 8/370/0 | 32% | -0.25 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (-0.25R) | NY/QUIET/NORMAL/BTC_RISING (-0.40R) |
| FUNDING_EXTREME_SIGNAL | 284 | 0/284/0 | 29% | -0.49 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| VOLUME_SURGE_BREAKOUT | 252 | 0/252/0 | 82% | +0.94 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.00R) |
| MEAN_REVERT | 222 | 2/220/0 | 80% | +0.70 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| SHADOW_CASCADE_REVERSAL | 151 | 0/0/151 | 55% | -0.05 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) |
| BREAKDOWN_SHORT | 130 | 4/126/0 | 6% | -0.90 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDITY_SWEEP_REVERSAL | 62 | 2/60/0 | 52% | -0.24 | — | — |
| RANGE_FADE | 18 | 0/18/0 | 22% | -0.40 | — | — |
| MA_CROSS_TREND_SHIFT | 12 | 0/12/0 | 33% | -0.15 | — | — |
| SR_FLIP_RETEST | 6 | 0/6/0 | 0% | -0.63 | — | — |
| LIQUIDATION_REVERSAL | 2 | 0/2/0 | 0% | -1.23 | — | — |

- **Strongest cells**: `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR` +1.13R (n=27, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL` +1.07R (n=50, STRONG)
- **Weakest cells**: `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.36R (n=48, NEGATIVE); `MOVER_AVWAP_SCALP @ ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.36R (n=15, NEGATIVE); `MOVER_AVWAP_SCALP @ ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL` -1.36R (n=15, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 28 | 32% / -0.43R | 28 | 46% / -0.13R | +0.30 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 20 | 55% / +0.39R | 20 | 55% / +0.19R | -0.21 | **FIXED** |
| MEAN_REVERT | 21 | 67% / +0.31R | 21 | 67% / +0.45R | +0.14 | **ATR** |
| TREND_PULLBACK_EMA | 130 | 47% / -0.17R | 130 | 55% / -0.04R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 58 | 26% / -0.50R | 58 | 28% / -0.40R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 194 | 49% / -0.12R | 194 | 55% / -0.03R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 66 | 33% / -0.32R | 66 | 36% / -0.24R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 121 | 59% / +0.14R | 121 | 63% / +0.06R | -0.07 | **FIXED** |
| MOVER_TREND_PULLBACK | 2761 | 58% / +0.03R | 2761 | 62% / +0.07R | +0.04 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 27 | 44% / -0.19R | 27 | 52% / -0.16R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 63 | 51% / -0.11R | 63 | 51% / -0.10R | +0.01 | **ATR** |
| RANGE_FADE | 4 | 50% / +0.44R | 4 | 50% / +0.24R | — | **MEASURING** |
| SR_FLIP_RETEST | 3 | 0% / -0.97R | 3 | 0% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 4 | 25% / -0.40R | 4 | 25% / -0.36R | — | **MEASURING** |
| BREAKDOWN_SHORT | 4 | 0% / -0.66R | 4 | 0% / -0.44R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4032 | 32% | -0.04R | 195 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 194 | 53% | -0.04R | 69 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 13 | 69% | +0.25R | 12 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 29 | 24% / +0.13R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 75 | 49% / +1.21R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3209 | 43% / +0.03R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 270 | 39% / -0.04R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 51 | 31% / -0.15R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 134 | 47% / +0.50R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 169 | 42% / -0.17R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 29 | 38% / -0.48R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 30 | 43% / -0.06R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 20 | 30% / -0.28R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 20 | 65% / +0.43R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 13 | 15% / -0.88R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 4 | 50% / +0.21R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 5 | 0% / -0.69R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 7 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 1 | 0% / -1.23R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 51 · alerting: **10** · boot grace active: False
- **ALERT** `scan_cycle` — last 31.35s, worst 148.55s over 6036 cycles; 258 over 60s, 22 over the 120s healthcheck deadline; 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 306/2) (sustained 306 cycles)
- **ALERT** `sar_alignment_crosscheck` — 2655/31976 disagreed (8.3%) (streak 373/6) (sustained 373 cycles)
- **ALERT** `dark_resolution` — 7 of 82 open dark rows are not being advanced (worst: BSBUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 130/120) (sustained 130 cycles)
- **ALERT** `candle_coverage` — 104/141 symbols with ≥20 15m candles, 89/141 updated within 45m [no_bucket=37, stale=15, fresh=89; 14 promoted of 141]; 52 CORE pair(s) unusable (e.g. 1000000BOBUSDT, 1000CATUSDT, 1000RATSUSDT, ACHUSDT, AEVOUSDT) (streak 98/6) (sustained 98 cycles)
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 416/6) (sustained 416 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 7776x (gate reads 0x, withheld 0x — refusal dark); last MOVEUSDT age=64217.9s (streak 307/6) (sustained 307 cycles)
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=+0.36R (bound 0.3) (streak 416/6) (sustained 416 cycles)
- **ALERT** `mean_revert_emission` — 6016 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.69R over n=220, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 234/6) (sustained 234 cycles)
- **ALERT** `range_fade_emission` — 4038 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 338/6) (sustained 338 cycles)
- **ALERT** `tuned_variants` — 135 non-stamps — atr_arm_uncomputable=135 (seen=7547 stamped=1250 skipped=6162) (streak 306/6) (sustained 306 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 47823600 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 25 arms current, none stalled; covering 227/227 signals (100%) | 0 |
| auto_dispatch | ok | attempts=37 fanouts=37 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77057.60 | 0 |
| candle_coverage | violating | 104/141 symbols with ≥20 15m candles, 89/141 updated within 45m [no_bucket=37, stale=15, fresh=89; 14 promoted of 141]; 52 CORE pair(s) unusable (e.g. 1000000BOBUSDT, 1000CATUSDT, 1000RATSUSDT, ACHUSDT, AEVOUSDT) (streak 98/6) | 98 |
| candle_series_integrity | ok | merge dropped 10896 dup bars, 0 undedupable; ws 1 out-of-order, 435 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 416/6) | 416 |
| context_emission_policy | ok | output +30 / upstream +15 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1470/1484 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 7 of 82 open dark rows are not being advanced (worst: BSBUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 130/120) | 130 |
| dark_sar_arms | ok | no open arms; covering 1468/1482 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 14478994 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=+0.36R (bound 0.3) (streak 416/6) | 416 |
| emission_controller | ok | last cycle 1022s ago; live_overrides=27 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=15 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4291 stamps (MEAN_REVERT=1271, MOVER_AVWAP_SCALP=460, MOVER_TREND_PULLBACK=1831, RANGE_FADE=661, TREND_PULLBACK_EMA=68), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 11318 evaluated, 3982 suppressed, 7336 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 5040 sealed bars over 42 symbols; 1196 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +2 / upstream +188 | 0 |
| indicator_cache_key | ok | 154570 frozen value(s) avoided; 175594 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 6016 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.69R over n=220, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 234/6) | 234 |
| mean_revert_path | ok | output +163 / upstream +188 | 0 |
| mover_admission_metadata | ok | 872 symbols known, 170 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 14 held, 14 with scan counts, 14 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s); 2 orphan(s) dropped at restore | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3006 rows held, 707070 evicted (sampled: execution:overextended 400/256321, execution:trigger_not_confirmed 400/252013, setup_compat:regime_STRONG_TREND 400/91250) | 0 |
| price_action_lane | ok | 584806 evaluated, 1074 emitted; layer1 1074 stamped / 0 blind; cooldown=70304, delta_opposed=54520, no_footprint=272595, no_levels=81, no_opposing_target=217, no_sweep=134476, rr_below_floor=51539 | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 4038 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 338/6) | 338 |
| range_fade_path | ok | output +90 / upstream +188 | 0 |
| sar_alignment_crosscheck | violating | 2655/31976 disagreed (8.3%) (streak 373/6) | 373 |
| sar_exit_shadow | ok | output +2 / upstream +188 | 0 |
| sar_hold_arm | ok | 372 held arms settled, 75 unscored, 25 still walking (22 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 9/39 unfetchable (23%); top cause: gap or duplicate bar in the 15m window; symbols: BEATUSDT, ICPUSDT, MOVEUSDT, NEARUSDT, ONGUSDT +1 more | 0 |
| sar_live_arms | ok | 25 arms current, none stalled; covering 236/236 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 439 records await one (30 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | violating | last 31.35s, worst 148.55s over 6036 cycles; 258 over 60s, 22 over the 120s healthcheck deadline; 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 306/2) | 306 |
| setup_tf_resolver | ok | 228693 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 47s ago (2.52s to run, worst 94.56s), 1479 overrun(s) of 8132 cycles, TTL 900s; slowest tickers=8.94s, engine_state=8.55s, signals=5.78s | 0 |
| stale_tf_scoring | violating | scored on stale TF 7776x (gate reads 0x, withheld 0x — refusal dark); last MOVEUSDT age=64217.9s (streak 307/6) | 307 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +21 / upstream +188 | 0 |
| structural_snap | ok | 4278/4278 measured, 20 blind, 0 levels moved (refusals: redetect_cooldown=1523) | 0 |
| structural_veto_lane | ok | 2546 stamped; 0 with no readable level book, 14 with clear air ahead, 1862 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +188 / upstream +15 | 0 |
| tuned_variants | violating | 135 non-stamps — atr_arm_uncomputable=135 (seen=7547 stamped=1250 skipped=6162) (streak 306/6) | 306 |

Fail-open exception counters (nonzero sites):
- `trade_monitor.close_signal_manual`: 1 — last: AttributeError: 'str' object has no attribute 'timestamp'

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1635329`
- `Path funnel` emissions: `35`
- `Regime distribution` emissions: `35`
- `QUIET_SCALP_BLOCK` events: `54`
- `confidence_gate` events: `5580`
- `free_channel_post` events: `29`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **26**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 6 | 5986 | 9824 | 11359 | 0 |
| futures_aggtrade | 9 | 7139 | 9044 | 24145 | 0 |
| futures_depth | 4 | 2350 | 4124 | 15554 | 0 |
| futures_liq | 2 | 2604 | 2604 | 3793 | 0 |
| futures_mover | 5 | 7149 | 7303 | 13957 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **29**

| Source | Count |
|---|---:|
| signal_close | 24 |
| regime_shift | 5 |

- By severity: HIGH=29

## Dependency readiness
- cvd: presence[present=278047] state[populated=278047] buckets[few=2, many=278034, some=11] sources[none] quality[none]
- funding_rate: presence[absent=59680, present=218367] state[empty=59680, populated=218367] buckets[few=218367, none=59680] sources[none] quality[none]
- liquidation_clusters: presence[absent=168052, present=109995] state[empty=168052, populated=109995] buckets[few=87508, none=168052, some=22487] sources[none] quality[none]
- oi_snapshot: presence[absent=59679, present=218368] state[empty=59679, populated=218368] buckets[few=242, many=216725, none=59679, some=1401] sources[none] quality[none]
- order_book: presence[absent=110610, present=167437] state[populated=167437, unavailable=110610] buckets[few=167437, none=110610] sources[book_ticker=167437, unavailable=110610] quality[none=110610, top_of_book_only=167437]
- orderblocks: presence[absent=278047] state[empty=278047] buckets[none=278047] sources[measured_dark=278029, not_implemented=18] quality[none]
- recent_ticks: presence[absent=747, present=277300] state[empty=747, populated=277300] buckets[many=277300, none=747] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `15.523414015769958` sec
- Median create→first breach: `5288.474011540413` sec
- Median create→terminal: `5403.142702460289` sec
- Median first breach→terminal: `4.069926023483276` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 8.3}, "under_180s": {"count": 2, "pct": 8.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 4.2}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 1.5430501084051471 | 2.4762158324458645 | 0.6760174010282202 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.364364268768355 | 1.533797488384134 | 0.8895335134534103 | 0 | 3 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.9181957406404524 | 2.9528999999999934 | 0.9882473976905615 | 0 | 1 |
| MOVER_TREND_PULLBACK | 16 | 16 | 4.327128298994294 | 2.9944500000000027 | 1.650442809283359 | 13 | 3 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 1.385514636788229 | 1.5680290740317433 | 0.8843201654563253 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 2.6884 | 15999.330070495605 | 16002.052571892738 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 1.7007 | 6825.620313882828 | 6839.360140800476 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.9529 | 105.8209319114685 | 107.30961298942566 |
| MOVER_TREND_PULLBACK | 16 | 16 | 0.0 | 31.2 | 0.0 | 0.0 | 0.5655 | 4670.489443063736 | 4683.504101514816 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.4724 | 38397.19956994057 | 38400.16747391224 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 745 | 1 | 721 | 0.0 | 0.0 | None | None | 24 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1479 | 52 | 997 | 0.0 | 0.0 | None | None | 482 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-161`
- Gating Δ: `-24423`
- No-generation Δ: `-165505`
- Fast failures Δ: `2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.7007, "current_avg_pnl": 1.7007, "current_win_rate": 66.7, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.3232, "current_avg_pnl": 0.5655, "current_win_rate": 0.0, "previous_avg_pnl": 0.8887, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 24, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 24, "geometry_changed_delta": 0, "geometry_preserved_delta": 204, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **FAILED_AUCTION_RECLAIM**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
