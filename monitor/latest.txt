# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `46` sec (warning=False)
- Latest performance record age: `2212` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 8 | 8 | 5 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3274 | 3274 | 2989 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 29183 | 29201 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 26014 | 26022 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 25844 | 25086 | 918 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 26038 | 25929 | 137 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 27058 | 26968 | 99 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 24129 | 24138 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 26069 | 26087 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 26094 | 25365 | 1056 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 30792 | 32358 | 152 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 29208 | 26630 | 4139 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 26939 | 26944 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 26026 | 26036 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 25809 | 25695 | 149 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 26426 | 25880 | 784 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 25686 | 25773 | 22 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 22864 | 22334 | 623 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 22964 | 22887 | 118 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 29155 | 29173 | 8 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 24146 | 24129 | 45 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 519 | 519 | 316 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 494 | 494 | 182 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 2835 | 2835 | 2783 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 5 | 5 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2566 | 2566 | 1976 | 8 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 399 | 399 | 36 | 24 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 10838 | 10838 | 5836 | 251 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 582 | 582 | 268 | 69 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1856 | 1856 | 1609 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 89 | 89 | 80 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 516 | 516 | 407 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 26 | 26 | 5 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1239 | 1239 | 3 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=29201): breakout_not_found=13853, basic_filters_failed=9027, move_not_fresh=4489, breakout_stale=1224, retest_proximity_failed=464, insufficient_candles=61, volume_spike_missing=57, ema_alignment_reject=21, move_exhausted=3, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=26022): cls_disabled_merged_into_lsr=26022
- **EVAL::DIVERGENCE_CONTINUATION** (total=25086): cvd_divergence_failed=9058, basic_filters_failed=7220, h1_trend_not_aligned=6458, ema_alignment_reject=1807, retest_proximity_failed=264, regime_blocked=136, missing_fvg_or_orderblock=93, insufficient_candles=47, cvd_insufficient=3
- **EVAL::FAILED_AUCTION_RECLAIM** (total=25929): auction_not_detected=16395, basic_filters_failed=7083, regime_blocked=1226, reclaim_hold_failed=669, tail_too_small=498, insufficient_candles=47, rsi_reject=11
- **EVAL::FUNDING_EXTREME** (total=26968): funding_not_extreme=17392, basic_filters_failed=7609, ema_alignment_reject=911, missing_funding_rate=644, rsi_reject=220, momentum_reject=102, cvd_divergence_failed=85, missing_fvg_or_orderblock=5
- **EVAL::LIQUIDATION_REVERSAL** (total=24138): cascade_threshold_not_met=16243, basic_filters_failed=7613, rsi_reject=120, cvd_divergence_failed=107, insufficient_candles=50, missing_fvg_or_orderblock=4, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=26087): no_ma_cross=18399, basic_filters_failed=7255, ma_cross_htf_misaligned=238, ma_cross_cooldown=195
- **EVAL::MEAN_REVERT** (total=25365): no_extension=21231, basic_filters_failed=3871, insufficient_candles=263
- **EVAL::MOVER_AVWAP_SCALP** (total=32358): no_mover_leg=10950, no_avwap_tag=9338, basic_filters_failed=8807, avwap_slope_against=1807, insufficient_candles=653, avwap_reclaim_no_volume=527, no_avwap_reclaim=271, anchor_too_recent=5
- **EVAL::MOVER_TREND_PULLBACK** (total=26630): mover_run_too_small=11347, basic_filters_failed=8646, no_reclaim=4909, insufficient_candles=897, no_pullback_tag=831
- **EVAL::OPENING_RANGE_BREAKOUT** (total=26944): feature_disabled=26944
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=26036): regime_blocked=18714, breakout_not_found=5303, basic_filters_failed=1342, adx_reject=639, ema_alignment_reject=38
- **EVAL::QUIET_COMPRESSION_BREAK** (total=25695): regime_blocked=8515, compression_not_detected=5856, basic_filters_failed=5733, breakout_not_detected=5007, volume_confirmation_failed=466, rsi_reject=60, insufficient_candles=47, missing_fvg_or_orderblock=9, macd_reject=2
- **EVAL::RANGE_FADE** (total=25880): no_range_edge=21460, basic_filters_failed=3592, insufficient_candles=828
- **EVAL::SR_FLIP_RETEST** (total=25773): flip_close_not_confirmed=16203, basic_filters_failed=7071, regime_blocked=1223, retest_out_of_zone=476, long_break_volume_thin=461, h1_break_not_confirmed=164, reclaim_hold_failed=76, insufficient_candles=47, wick_quality_failed=27, long_acceptance_not_held=25
- **EVAL::STANDARD** (total=22334): momentum_reject=8829, adx_reject=4573, basic_filters_failed=3067, sweeps_not_detected=2976, macd_reject=1444, ema_alignment_reject=930, htf_poi_unanchored=387, insufficient_candles=81, rsi_reject=25, invalid_sl_geometry=22
- **EVAL::TREND_PULLBACK** (total=22887): h1_trend_not_aligned=7823, basic_filters_failed=3845, ema_alignment_reject=3319, h1_pullback_not_confirmed=2791, ema_not_tested_prev=1295, no_ema_reclaim_close=1178, body_conviction_fail=969, rsi_reject=943, prev_already_below_emas=144, regime_blocked=133, no_prev_low_break=128, prev_already_above_emas=82, insufficient_candles=81, momentum_flat=48, momentum_reject=38, no_prev_high_break=36, missing_fvg_or_orderblock=28, ema21_not_tagged=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=29173): breakout_not_found=16830, basic_filters_failed=9026, move_not_fresh=1944, breakout_stale=814, retest_proximity_failed=418, volume_spike_missing=70, insufficient_candles=61, move_exhausted=4, missing_fvg_or_orderblock=3, ema_alignment_reject=2, rsi_reject=1
- **EVAL::WHALE_MOMENTUM** (total=24129): momentum_reject=15330, recent_ticks_insufficient=6385, basic_filters_failed=2414

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=94): setup_compat:regime_VOLATILE_UNSUITABLE=93, setup_compat:regime_BREAKOUT_EXPANSION=1
- **FAILED_AUCTION_RECLAIM** (total=120): execution:overextended=52, setup_compat:regime_STRONG_TREND=49, context_floor=19
- **FUNDING_EXTREME_SIGNAL** (total=381): execution:trigger_not_confirmed=373, context_floor=8
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=695): execution:overextended=320, setup_compat:regime_STRONG_TREND=202, execution:trigger_not_confirmed=173
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_DIRTY_RANGE=2, execution:overextended=2, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=1082): setup_compat:regime_WEAK_TREND=480, setup_compat:regime_STRONG_TREND=427, execution:overextended=143, entry_quality=32
- **MOVER_AVWAP_SCALP** (total=319): execution:overextended=188, entry_quality=87, execution:trigger_not_confirmed=44
- **MOVER_TREND_PULLBACK** (total=6520): execution:overextended=2908, execution:trigger_not_confirmed=2566, entry_quality=1046
- **QUIET_COMPRESSION_BREAK** (total=20): execution:trigger_not_confirmed=20
- **RANGE_FADE** (total=1119): setup_compat:regime_WEAK_TREND=379, setup_compat:regime_STRONG_TREND=374, execution:overextended=225, setup_compat:regime_VOLATILE_UNSUITABLE=101, context_edge=35, setup_compat:regime_BREAKOUT_EXPANSION=5
- **TREND_PULLBACK_EMA** (total=479): setup_compat:regime_CLEAN_RANGE=273, setup_compat:regime_DIRTY_RANGE=143, setup_compat:regime_VOLATILE_UNSUITABLE=38, entry_quality=25
- **WHALE_MOMENTUM** (total=1236): execution:trigger_not_confirmed=1236

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 48871 | 32.1% |
| RANGING | 47784 | 31.4% |
| TRENDING_DOWN | 29004 | 19.0% |
| TRENDING_UP | 17964 | 11.8% |
| VOLATILE | 8785 | 5.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **162**
- Average confidence gap to threshold: **9.24** (samples=162) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=22, HYPEUSDT=16, DOTUSDT=15, BTCUSDT=11, SUIUSDT=9, 1000PEPEUSDT=9, INJUSDT=8, TAOUSDT=8, XRPUSDT=8, SOLUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 53 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 16 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 9 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 14 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 6 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 21 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 54 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 103 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 58 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 364 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 9 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2075 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 119 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 1 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 236 |
| SR_FLIP_RETEST | filtered | min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 5 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 7 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 54 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 8 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 66.75 | 65.00 | -1.75 | 19.75 | 18.75 | 20.00 | 4.25 | 1.50 |
| DIVERGENCE_CONTINUATION | filtered | 7 | 51.46 | 63.14 | 11.68 | 20.24 | 19.51 | 17.67 | 0.00 | 13.34 |
| DIVERGENCE_CONTINUATION | kept | 53 | 68.81 | 65.00 | -3.81 | 20.66 | 19.76 | 17.37 | 1.38 | -2.29 |
| FAILED_AUCTION_RECLAIM | filtered | 16 | 52.00 | 65.00 | 13.00 | 20.14 | 20.00 | 20.00 | 1.00 | 15.14 |
| FAILED_AUCTION_RECLAIM | kept | 9 | 67.40 | 65.00 | -2.40 | 20.22 | 18.74 | 20.00 | 1.61 | 4.67 |
| FUNDING_EXTREME_SIGNAL | filtered | 14 | 46.29 | 61.00 | 14.71 | 17.66 | 17.89 | 17.01 | 0.93 | 8.07 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 67.00 | 65.00 | -2.00 | 20.10 | 14.00 | 17.00 | 3.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 55.21 | 65.00 | 9.79 | 19.40 | 19.89 | 17.03 | 1.71 | 19.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 69.20 | 65.00 | -4.20 | 20.35 | 17.38 | 18.11 | 1.43 | 0.70 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.50 | 65.00 | -13.50 | 19.80 | 16.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 54 | 67.82 | 65.00 | -2.82 | 20.23 | 18.61 | 17.01 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 103 | 55.09 | 64.46 | 9.37 | 20.54 | 15.45 | 15.80 | 3.43 | 5.17 |
| MOVER_AVWAP_SCALP | kept | 58 | 77.32 | 65.00 | -12.32 | 19.86 | 14.73 | 15.80 | 3.84 | 0.48 |
| MOVER_TREND_PULLBACK | filtered | 373 | 56.35 | 63.33 | 6.98 | 19.99 | 18.13 | 15.80 | 4.07 | 14.34 |
| MOVER_TREND_PULLBACK | kept | 2075 | 77.54 | 65.00 | -12.54 | 20.05 | 18.41 | 15.80 | 4.48 | 0.57 |
| QUIET_COMPRESSION_BREAK | filtered | 120 | 56.96 | 64.96 | 8.00 | 20.72 | 19.94 | 20.00 | 0.00 | 9.64 |
| QUIET_COMPRESSION_BREAK | kept | 236 | 75.31 | 65.00 | -10.31 | 20.27 | 19.76 | 20.00 | 0.00 | -0.63 |
| SR_FLIP_RETEST | filtered | 3 | 56.17 | 62.33 | 6.16 | 20.47 | 20.00 | 18.80 | 1.83 | 12.93 |
| SR_FLIP_RETEST | kept | 5 | 86.50 | 65.00 | -21.50 | 20.80 | 20.00 | 15.20 | 2.50 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 7 | 59.50 | 65.00 | 5.50 | 22.89 | 20.00 | 20.00 | 6.00 | 17.00 |
| TREND_PULLBACK_EMA | kept | 54 | 77.24 | 65.00 | -12.24 | 20.38 | 19.82 | 18.21 | 4.75 | -2.15 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 59.50 | 60.00 | 0.50 | 21.20 | 19.60 | 20.00 | 4.50 | 3.00 |
| WHALE_MOMENTUM | filtered | 8 | 45.43 | 65.00 | 19.57 | 19.93 | 14.00 | 17.00 | 0.00 | 20.80 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 66.75 | 9.50 | 16.00 | 13.50 | 12.00 | 5.00 | 8.00 | 4.25 |
| DIVERGENCE_CONTINUATION | filtered | 7 | 51.46 | 21.57 | 9.43 | 7.29 | 13.14 | 7.00 | 8.94 | 0.00 |
| DIVERGENCE_CONTINUATION | kept | 53 | 68.81 | 21.98 | 13.47 | 5.55 | 12.68 | 5.10 | 9.02 | 1.38 |
| FAILED_AUCTION_RECLAIM | filtered | 16 | 52.00 | 16.38 | 14.00 | 9.75 | 12.69 | 5.88 | 7.45 | 1.00 |
| FAILED_AUCTION_RECLAIM | kept | 9 | 67.40 | 19.67 | 15.78 | 9.00 | 13.67 | 6.22 | 6.12 | 1.61 |
| FUNDING_EXTREME_SIGNAL | filtered | 14 | 46.29 | 19.86 | 15.14 | 5.36 | 15.71 | 7.57 | 4.79 | 0.93 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 67.00 | 25.00 | 8.00 | 9.00 | 9.00 | 10.00 | 8.00 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 55.21 | 22.14 | 14.57 | 10.29 | 11.43 | 6.00 | 8.27 | 1.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 69.20 | 22.05 | 14.38 | 5.71 | 13.14 | 5.67 | 7.66 | 1.43 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.50 | 23.00 | 14.00 | 12.00 | 11.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | kept | 54 | 67.82 | 20.37 | 16.15 | 8.33 | 12.00 | 5.90 | 5.07 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 103 | 55.09 | 18.69 | 18.27 | 8.13 | 12.13 | 5.17 | 4.93 | 3.43 |
| MOVER_AVWAP_SCALP | kept | 58 | 77.32 | 18.66 | 18.07 | 9.49 | 13.76 | 5.57 | 8.74 | 3.84 |
| MOVER_TREND_PULLBACK | filtered | 373 | 56.35 | 17.90 | 18.15 | 8.04 | 13.48 | 5.71 | 6.71 | 4.07 |
| MOVER_TREND_PULLBACK | kept | 2075 | 77.54 | 18.95 | 18.03 | 8.33 | 13.28 | 5.88 | 9.25 | 4.48 |
| QUIET_COMPRESSION_BREAK | filtered | 120 | 56.96 | 18.20 | 17.97 | 11.60 | 14.00 | 6.91 | 4.05 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 236 | 75.31 | 18.06 | 17.93 | 11.75 | 14.18 | 6.63 | 7.64 | 0.00 |
| SR_FLIP_RETEST | filtered | 3 | 56.17 | 19.00 | 18.00 | 3.00 | 12.67 | 5.00 | 9.53 | 1.83 |
| SR_FLIP_RETEST | kept | 5 | 86.50 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 7 | 59.50 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 6.00 |
| TREND_PULLBACK_EMA | kept | 54 | 77.24 | 16.54 | 18.00 | 7.64 | 14.28 | 7.44 | 8.85 | 4.75 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 59.50 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 7.00 | 4.50 |
| WHALE_MOMENTUM | filtered | 8 | 45.43 | 25.00 | 8.00 | 13.50 | 9.50 | 5.00 | 5.22 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 66.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 7 | 51.46 | 0.00 | 0.00 | 2.29 | 0.00 | 12.34 | 0.00 | 0.00 | 0.00 | **14.63** |
| DIVERGENCE_CONTINUATION | kept | 53 | 68.81 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.33** |
| FAILED_AUCTION_RECLAIM | filtered | 16 | 52.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.45 | 0.00 | 0.00 | 0.00 | **9.45** |
| FAILED_AUCTION_RECLAIM | kept | 9 | 67.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 14 | 46.29 | 0.00 | 0.00 | 7.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.71** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 55.21 | 0.00 | 0.00 | 0.69 | 0.00 | 18.51 | 0.00 | 0.00 | 0.00 | **19.20** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 69.20 | 0.00 | 0.00 | 0.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.84** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 54 | 67.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 103 | 55.09 | 0.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.71 | **2.15** |
| MOVER_AVWAP_SCALP | kept | 58 | 77.32 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.26** |
| MOVER_TREND_PULLBACK | filtered | 373 | 56.35 | 0.00 | 0.00 | 0.62 | 0.00 | 0.75 | 0.00 | 0.00 | 0.00 | **1.37** |
| MOVER_TREND_PULLBACK | kept | 2075 | 77.54 | 0.00 | 0.00 | 0.33 | 0.00 | 0.15 | 0.02 | 0.00 | 0.00 | **0.50** |
| QUIET_COMPRESSION_BREAK | filtered | 120 | 56.96 | 0.00 | 0.00 | 0.24 | 0.00 | 0.25 | 0.00 | 0.00 | 7.25 | **7.74** |
| QUIET_COMPRESSION_BREAK | kept | 236 | 75.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.27 | 0.00 | 0.00 | 0.37 | **0.64** |
| SR_FLIP_RETEST | filtered | 3 | 56.17 | 0.00 | 0.00 | 6.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.93** |
| SR_FLIP_RETEST | kept | 5 | 86.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 7 | 59.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 54 | 77.24 | 0.00 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.30** |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 59.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 8 | 45.43 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **10.80** |

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
- Outcomes recorded: **142597 held of 299172 seen** across 21 strategies; 3210 cells past the sample floor; **1309 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 33607 | 205/33402/0 | 50% | -0.05 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17358 | 18/17340/0 | 52% | +0.00 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16586 | 1/16585/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 12285 | 6/12279/0 | 46% | -0.10 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (+1.32R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 9800 | 27/9773/0 | 36% | -0.31 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| QUIET_COMPRESSION_BREAK | 9777 | 0/9777/0 | 46% | -0.09 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 5989 | 2/5987/0 | 47% | -0.25 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 5321 | 0/0/5321 | 43% | -0.09 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.56R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL (-1.02R) |
| LIQUIDITY_SWEEP_REVERSAL | 5151 | 11/5140/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4866 | 0/0/4866 | 37% | +0.00 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (+0.62R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.28R) |
| MEAN_REVERT | 4760 | 2/4758/0 | 69% | +0.33 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.30R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-1.54R) |
| SHADOW_FUNDING_FADE | 4427 | 0/0/4427 | 36% | -0.37 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 4087 | 0/4087/0 | 33% | -0.36 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2630 | 19/2611/0 | 41% | +0.04 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2531 | 4/2527/0 | 31% | -0.46 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.29R) |
| WHALE_MOMENTUM | 2070 | 0/2070/0 | 46% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.89R) |
| SHADOW_CASCADE_REVERSAL | 582 | 0/0/582 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-2.17R) |
| BREAKDOWN_SHORT | 529 | 11/518/0 | 45% | +0.04 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 73 | 0/73/0 | 85% | +0.69 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 40 | 1/39/0 | 38% | -0.39 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `SHADOW_CASCADE_REVERSAL @ OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL` -2.17R (n=16, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 132 | 36% / -0.39R | 132 | 57% / -0.11R | +0.28 | **ATR** |
| TREND_PULLBACK_EMA | 262 | 42% / -0.33R | 262 | 47% / -0.12R | +0.21 | **ATR** |
| MOVER_AVWAP_SCALP | 663 | 38% / -0.22R | 663 | 42% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 2782 | 46% / -0.20R | 2782 | 49% / -0.10R | +0.11 | **ATR** |
| DIVERGENCE_CONTINUATION | 991 | 47% / -0.11R | 991 | 53% / -0.05R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4346 | 51% / -0.07R | 4346 | 54% / -0.01R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 784 | 51% / -0.17R | 784 | 55% / -0.11R | +0.05 | **ATR** |
| MA_CROSS_TREND_SHIFT | 17 | 35% / -0.25R | 17 | 35% / -0.20R | +0.05 | **ATR** |
| WHALE_MOMENTUM | 163 | 50% / -0.25R | 163 | 50% / -0.28R | -0.03 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1590 | 44% / -0.13R | 1590 | 44% / -0.16R | -0.03 | **FIXED** |
| RANGE_FADE | 272 | 23% / -0.56R | 272 | 25% / -0.53R | +0.03 | **ATR** |
| MEAN_REVERT | 510 | 53% / -0.02R | 510 | 49% / -0.00R | +0.02 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 91 | 41% / -0.03R | 91 | 52% / -0.05R | -0.01 | **FIXED** |
| BREAKDOWN_SHORT | 23 | 35% / -0.20R | 23 | 35% / -0.19R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2321 | 47% / -0.11R | 2321 | 47% / -0.11R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 10 | 60% / +0.10R | 10 | 60% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6361 | 30% | -0.15R | 287 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 653 | 41% | -0.10R | 140 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 42 | 57% | +0.01R | 23 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1241 | 29% / -1.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 32 | 31% / -0.32R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5399 | 40% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1038 | 32% / -0.55R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 107 | 22% / -0.86R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 851 | 34% / -1.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1132 | 37% / -0.12R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 435 | 45% / -0.80R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 155 | 30% / -1.21R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 317 | 31% / -0.57R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 751 | 31% / -0.35R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 19% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 243 | 45% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 97 | 40% / -0.09R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 25% / -0.67R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 55 | 42% / -0.27R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 47 · alerting: **2** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 13 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 27/6) (sustained 27 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.45R (bound 0.3) (streak 27/6) (sustained 27 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 2440597 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 10 arms current, none stalled; covering 116/116 signals (100%) | 0 |
| auto_dispatch | ok | attempts=4 fanouts=4 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 63051.30 | 0 |
| candle_coverage | ok | 93/94 symbols with ≥20 15m candles, 90/94 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 1011 dup bars, 0 undedupable; ws 0 out-of-order, 172 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 13 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 27/6) | 27 |
| context_emission_policy | ok | output +66 / upstream +10 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1165/1177 signals (99%) | 0 |
| dark_promotion_rules | ok | 2 rule(s) armed, 1 promoted today | 0 |
| dark_resolution | violating | 5 of 132 open dark rows are not being advanced (worst: GWEIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 27/120) | 27 |
| dark_sar_arms | ok | no open arms; covering 1183/1195 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 982143 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.45R (bound 0.3) (streak 27/6) | 27 |
| emission_controller | ok | last cycle 1209s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4198 stamps (MEAN_REVERT=808, MOVER_AVWAP_SCALP=75, MOVER_TREND_PULLBACK=2837, RANGE_FADE=322, TREND_PULLBACK_EMA=156), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 811 evaluated, 287 suppressed, 524 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +33 / upstream +179 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 114 detections since last emission (emitted_total=2) — and the POST-SCORING blocked candidates measure +0.33R over n=4758, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 4/6) | 4 |
| mean_revert_path | ok | output +14 / upstream +179 | 0 |
| mover_admission_metadata | ok | 865 symbols known, 163 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 15 held, 15 with scan counts, 15 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3038 rows held, 537750 evicted (sampled: execution:overextended 400/198644, execution:trigger_not_confirmed 400/184396, setup_compat:regime_STRONG_TREND 400/64908) | 0 |
| price_action_lane | ok | 26095 evaluated, 62 emitted; layer1 62 stamped / 0 blind; cooldown=2391, delta_opposed=2079, no_footprint=8407, no_opposing_target=78, no_sweep=11343, rr_below_floor=1735 | 0 |
| promoted_pair_integrity | ok | 15/15 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.36R over n=4087 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +16 / upstream +179 | 0 |
| sar_alignment_crosscheck | ok | 88/2844 disagreed (3.1%) | 0 |
| sar_exit_shadow | ok | output +20 / upstream +179 | 0 |
| sar_hold_arm | ok | 203 held arms settled, 38 unscored, 9 still walking (7 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 41/139 unfetchable (29%); top cause: gap or duplicate bar in the 15m window; symbols: AKEUSDT, ALICEUSDT, BLESSUSDT, BTCUSDT, COWUSDT +13 more | 0 |
| sar_live_arms | ok | 9 arms current, none stalled; covering 125/125 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 7 resolved, 91 still mid-window | 0 |
| setup_tf_resolver | ok | 14990 resolutions, 9757 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +60 / upstream +179 | 0 |
| structural_snap | ok | 4174/4174 measured, 25 blind, 0 levels moved (refusals: redetect_cooldown=135) | 0 |
| structural_veto_lane | ok | 290 stamped; 0 with no readable level book, 19 with clear air ahead, 147 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +179 / upstream +10 | 0 |
| tuned_variants | ok | seen=466 stamped=137 skipped=322, residue 7 (atr_arm_uncomputable=7) | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `56619`
- `Path funnel` emissions: `18`
- `Regime distribution` emissions: `18`
- `QUIET_SCALP_BLOCK` events: `162`
- `confidence_gate` events: `3232`
- `free_channel_post` events: `11`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **3**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 19638 | 19638 | 54753 | 0 |
| futures_aggtrade | 1 | 11457 | 11457 | 11457 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **11**

| Source | Count |
|---|---:|
| signal_close | 6 |
| regime_shift | 5 |

- By severity: HIGH=11

## Dependency readiness
- cvd: presence[present=118112] state[populated=118112] buckets[few=1, many=117960, some=151] sources[none] quality[none]
- funding_rate: presence[absent=14476, present=103636] state[empty=14476, populated=103636] buckets[few=103636, none=14476] sources[none] quality[none]
- liquidation_clusters: presence[absent=73905, present=44207] state[empty=73905, populated=44207] buckets[few=36040, none=73905, some=8167] sources[none] quality[none]
- oi_snapshot: presence[absent=12743, present=105369] state[empty=12743, populated=105369] buckets[few=250, many=103636, none=12743, some=1483] sources[none] quality[none]
- order_book: presence[absent=50212, present=67900] state[populated=67900, unavailable=50212] buckets[few=67900, none=50212] sources[book_ticker=67900, unavailable=50212] quality[none=50212, top_of_book_only=67900]
- orderblocks: presence[absent=118112] state[empty=118112] buckets[none=118112] sources[measured_dark=118112] quality[none]
- recent_ticks: presence[absent=320, present=117792] state[empty=320, populated=117792] buckets[many=117792, none=320] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `24.190620183944702` sec
- Median create→first breach: `1632.0760459899902` sec
- Median create→terminal: `1647.3844940662384` sec
- Median first breach→terminal: `10.472209930419922` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 1.265740021406461 | 3.0 | 0.4219133404688203 | 0 | 1 |
| MOVER_TREND_PULLBACK | 8 | 8 | 3.4864884405641474 | 3.0 | 1.1621628135213826 | 6 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.8788 | 6503.577991962433 | 6504.6938190460205 |
| MOVER_TREND_PULLBACK | 8 | 8 | 0.0 | 25.0 | 0.0 | 0.0 | 1.6914 | 1340.2449660301208 | 1353.135295033455 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 89 | 0 | 80 | 0.0 | 0.0 | None | None | 9 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 516 | 9 | 407 | 0.0 | 0.0 | None | None | 109 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `387`
- Gating Δ: `16500`
- No-generation Δ: `496635`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.2095, "current_avg_pnl": 1.6914, "current_win_rate": 0.0, "previous_avg_pnl": -0.5181, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 9, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": 109, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
