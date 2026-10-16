# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `6396` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 128 | 128 | 128 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10237 | 10237 | 8751 | 25 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 73862 | 73849 | 39 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 65237 | 65237 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 65011 | 62314 | 2912 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 65271 | 64425 | 904 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 66454 | 66381 | 82 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 55658 | 55676 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 65332 | 65347 | 16 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 65364 | 63524 | 2816 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 79930 | 85362 | 863 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 73890 | 64114 | 15748 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 66098 | 66098 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 65241 | 65261 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 65003 | 64901 | 109 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 66343 | 65150 | 1730 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 64636 | 64843 | 144 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 54050 | 50479 | 3815 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 54304 | 53954 | 401 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 73820 | 73814 | 48 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 55678 | 55699 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3936 | 3936 | 3703 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 324 | 324 | 224 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 23275 | 23275 | 22901 | 10 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 18 | 18 | 16 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7947 | 7947 | 5509 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2709 | 2709 | 1621 | 35 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 50172 | 50172 | 34542 | 397 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 32 | 32 | 32 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 767 | 767 | 518 | 31 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4905 | 4905 | 3145 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 519 | 519 | 329 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1893 | 1893 | 1432 | 45 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 178 | 178 | 132 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=73849): breakout_not_found=44073, basic_filters_failed=18252, move_not_fresh=6608, breakout_stale=3844, retest_proximity_failed=804, volume_spike_missing=240, move_exhausted=20, missing_fvg_or_orderblock=8
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=65237): cls_disabled_merged_into_lsr=65237
- **EVAL::DIVERGENCE_CONTINUATION** (total=62314): cvd_divergence_failed=23510, h1_trend_not_aligned=20138, basic_filters_failed=13533, ema_alignment_reject=4145, retest_proximity_failed=540, missing_fvg_or_orderblock=319, missing_cvd=129
- **EVAL::FAILED_AUCTION_RECLAIM** (total=64425): auction_not_detected=42196, basic_filters_failed=12750, reclaim_hold_failed=3828, tail_too_small=2859, regime_blocked=2758, rsi_reject=34
- **EVAL::FUNDING_EXTREME** (total=66381): funding_not_extreme=50085, basic_filters_failed=12756, missing_funding_rate=2558, ema_alignment_reject=585, rsi_reject=234, cvd_divergence_failed=76, momentum_reject=71, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=55676): cascade_threshold_not_met=41191, basic_filters_failed=13851, cvd_divergence_failed=314, rsi_reject=311, missing_cvd=7, missing_fvg_or_orderblock=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=65347): no_ma_cross=50265, basic_filters_failed=13544, ma_cross_cooldown=1330, ma_cross_htf_misaligned=208
- **EVAL::MEAN_REVERT** (total=63524): no_extension=51140, basic_filters_failed=12384
- **EVAL::MOVER_AVWAP_SCALP** (total=85362): no_avwap_tag=39938, basic_filters_failed=18419, no_mover_leg=12669, avwap_slope_against=10305, avwap_reclaim_no_volume=2565, no_avwap_reclaim=1466
- **EVAL::MOVER_TREND_PULLBACK** (total=64114): mover_run_too_small=22546, no_reclaim=20854, basic_filters_failed=18334, no_pullback_tag=2380
- **EVAL::OPENING_RANGE_BREAKOUT** (total=66098): feature_disabled=66098
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=65261): regime_blocked=43467, breakout_not_found=17514, basic_filters_failed=3213, adx_reject=1040, ema_alignment_reject=27
- **EVAL::QUIET_COMPRESSION_BREAK** (total=64901): compression_not_detected=26338, regime_blocked=24473, basic_filters_failed=9528, breakout_not_detected=4252, volume_confirmation_failed=276, rsi_reject=18, missing_fvg_or_orderblock=16
- **EVAL::RANGE_FADE** (total=65150): no_range_edge=52761, basic_filters_failed=12389
- **EVAL::SR_FLIP_RETEST** (total=64843): flip_close_not_confirmed=41603, basic_filters_failed=12736, long_break_volume_thin=2964, regime_blocked=2753, retest_out_of_zone=2437, h1_break_not_confirmed=1153, reclaim_hold_failed=691, long_acceptance_not_held=214, ema_alignment_reject=116, wick_quality_failed=108, whipsaw_flip=67, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=50479): adx_reject=14664, momentum_reject=11487, basic_filters_failed=8673, ema_alignment_reject=5402, sweeps_not_detected=5218, macd_reject=4447, htf_poi_unanchored=500, invalid_sl_geometry=37, rsi_reject=35, mtf_reject=16
- **EVAL::TREND_PULLBACK** (total=53954): h1_trend_not_aligned=22483, h1_pullback_not_confirmed=8674, ema_alignment_reject=7921, basic_filters_failed=5034, ema_not_tested_prev=3212, no_ema_reclaim_close=2964, body_conviction_fail=1343, rsi_reject=1000, prev_already_below_emas=591, no_prev_low_break=397, momentum_flat=123, prev_already_above_emas=95, ema21_not_tagged=63, no_prev_high_break=41, missing_fvg_or_orderblock=13
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=73814): breakout_not_found=43341, basic_filters_failed=18251, move_not_fresh=7631, breakout_stale=3132, retest_proximity_failed=1157, volume_spike_missing=291, missing_fvg_or_orderblock=10, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=55699): momentum_reject=35646, recent_ticks_insufficient=13066, basic_filters_failed=6987

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=188): setup_compat:regime_VOLATILE_UNSUITABLE=139, setup_compat:regime_BREAKOUT_EXPANSION=49
- **FAILED_AUCTION_RECLAIM** (total=1200): execution:overextended=687, setup_compat:regime_STRONG_TREND=455, context_floor=58
- **FUNDING_EXTREME_SIGNAL** (total=290): execution:trigger_not_confirmed=286, context_floor=4
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=5999): execution:trigger_not_confirmed=2191, setup_compat:regime_STRONG_TREND=2169, execution:overextended=1639
- **MA_CROSS_TREND_SHIFT** (total=14): execution:trigger_not_confirmed=5, setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_CLEAN_RANGE=3, execution:overextended=1, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=6043): setup_compat:regime_STRONG_TREND=2611, setup_compat:regime_WEAK_TREND=2329, execution:overextended=1069, entry_quality=34
- **MOVER_AVWAP_SCALP** (total=1109): execution:overextended=925, execution:trigger_not_confirmed=127, entry_quality=57
- **MOVER_TREND_PULLBACK** (total=21301): execution:trigger_not_confirmed=14121, execution:overextended=4880, entry_quality=2300
- **QUIET_COMPRESSION_BREAK** (total=28): execution:trigger_not_confirmed=28
- **RANGE_FADE** (total=3178): setup_compat:regime_STRONG_TREND=1975, setup_compat:regime_WEAK_TREND=1038, execution:overextended=76, setup_compat:regime_VOLATILE_UNSUITABLE=43, context_edge=29, setup_compat:regime_BREAKOUT_EXPANSION=17
- **TREND_PULLBACK_EMA** (total=1662): setup_compat:regime_CLEAN_RANGE=976, setup_compat:regime_DIRTY_RANGE=541, entry_quality=91, setup_compat:regime_VOLATILE_UNSUITABLE=54

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 186705 | 43.7% |
| QUIET | 89267 | 20.9% |
| TRENDING_UP | 74757 | 17.5% |
| TRENDING_DOWN | 60727 | 14.2% |
| VOLATILE | 16090 | 3.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **153**
- Average confidence gap to threshold: **12.79** (samples=153) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=24, AAVEUSDT=15, WLDUSDT=12, WUSDT=12, DOGEUSDT=10, RLCUSDT=9, LITUSDT=8, BTCUSDT=7, ESPUSDT=7, SUIUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 105 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 101 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 18 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 118 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 6 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 38 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 24 |
| MEAN_REVERT | kept | min_confidence_pass | 18 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 264 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 270 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1666 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 47 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4745 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 60 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 56 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 111 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 16 |
| SR_FLIP_RETEST | filtered | min_confidence | 15 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 29 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 86 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 18 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 144 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 15 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 9 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 108 | 58.22 | 64.95 | 6.73 | 20.94 | 19.82 | 17.16 | 1.75 | 9.27 |
| DIVERGENCE_CONTINUATION | kept | 101 | 70.60 | 65.00 | -5.60 | 20.59 | 19.54 | 18.85 | 1.44 | 0.16 |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 47.53 | 64.58 | 17.05 | 21.44 | 19.85 | 20.00 | 4.47 | 8.58 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.30 | 65.00 | 2.70 | 21.20 | 15.30 | 20.00 | 2.50 | 6.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 49.14 | 61.00 | 11.86 | 20.34 | 14.44 | 17.00 | 4.00 | 3.20 |
| LIQUIDATION_REVERSAL | filtered | 1 | 61.20 | 10.00 | -51.20 | 21.20 | 8.60 | 20.00 | 6.00 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 124 | 49.65 | 64.22 | 14.57 | 19.75 | 18.79 | 17.90 | 1.00 | 5.81 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 38 | 72.55 | 65.00 | -7.55 | 20.11 | 19.65 | 18.34 | 1.71 | 0.26 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.80 | 65.00 | -3.80 | 20.20 | 16.80 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 24 | 54.40 | 64.17 | 9.77 | 19.80 | 14.00 | 14.91 | 0.00 | 18.91 |
| MEAN_REVERT | kept | 18 | 70.19 | 65.00 | -5.19 | 21.43 | 14.68 | 14.93 | 0.00 | 1.38 |
| MOVER_AVWAP_SCALP | filtered | 270 | 54.70 | 64.63 | 9.93 | 20.75 | 15.65 | 15.80 | 3.69 | 14.41 |
| MOVER_AVWAP_SCALP | kept | 270 | 78.56 | 65.00 | -13.56 | 20.84 | 17.21 | 15.80 | 4.19 | 3.83 |
| MOVER_TREND_PULLBACK | filtered | 1713 | 56.72 | 63.95 | 7.23 | 20.76 | 18.77 | 15.80 | 3.85 | 18.92 |
| MOVER_TREND_PULLBACK | kept | 4745 | 76.62 | 65.00 | -11.62 | 20.31 | 18.50 | 15.80 | 4.01 | 1.43 |
| QUIET_COMPRESSION_BREAK | filtered | 116 | 50.28 | 63.96 | 13.68 | 21.35 | 19.05 | 20.00 | 0.00 | 15.36 |
| QUIET_COMPRESSION_BREAK | kept | 111 | 71.73 | 65.00 | -6.73 | 22.57 | 19.38 | 20.00 | 0.00 | 0.60 |
| SR_FLIP_RETEST | filtered | 31 | 51.59 | 64.87 | 13.28 | 20.16 | 20.00 | 15.28 | 2.23 | 21.12 |
| SR_FLIP_RETEST | kept | 29 | 70.16 | 65.00 | -5.16 | 20.06 | 20.00 | 16.26 | 1.72 | 0.60 |
| TREND_PULLBACK_EMA | filtered | 104 | 57.75 | 62.69 | 4.94 | 20.77 | 19.88 | 17.84 | 4.93 | 18.44 |
| TREND_PULLBACK_EMA | kept | 144 | 76.84 | 65.00 | -11.84 | 20.72 | 19.72 | 17.84 | 4.74 | 1.06 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 52.23 | 63.93 | 11.70 | 19.45 | 18.29 | 20.00 | 3.93 | 11.11 |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 64.01 | 65.00 | 0.99 | 20.09 | 19.46 | 20.00 | 5.22 | 18.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 108 | 58.22 | 24.04 | 10.78 | 4.33 | 12.20 | 6.00 | 8.38 | 1.75 |
| DIVERGENCE_CONTINUATION | kept | 101 | 70.60 | 23.57 | 13.64 | 5.58 | 12.49 | 6.11 | 8.82 | 1.44 |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 47.53 | 23.32 | 17.79 | 7.11 | 11.84 | 3.45 | 2.35 | 4.47 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.30 | 25.00 | 18.00 | 12.00 | 14.00 | 8.50 | 3.30 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 49.14 | 25.00 | 8.00 | 5.40 | 12.40 | 8.20 | 4.34 | 4.00 |
| LIQUIDATION_REVERSAL | filtered | 1 | 61.20 | 25.00 | 8.00 | 12.00 | 8.00 | 2.50 | 7.70 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 124 | 49.65 | 23.52 | 15.06 | 6.22 | 12.82 | 5.08 | 4.82 | 1.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 38 | 72.55 | 22.21 | 14.53 | 7.03 | 13.34 | 5.53 | 8.47 | 1.71 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.80 | 17.00 | 14.00 | 6.00 | 14.00 | 8.50 | 9.30 | 0.00 |
| MEAN_REVERT | filtered | 24 | 54.40 | 23.67 | 15.67 | 9.00 | 13.00 | 5.00 | 7.00 | 0.00 |
| MEAN_REVERT | kept | 18 | 70.19 | 21.00 | 16.11 | 10.17 | 12.28 | 5.00 | 7.19 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 270 | 54.70 | 18.53 | 18.00 | 11.37 | 13.67 | 6.27 | 5.26 | 3.69 |
| MOVER_AVWAP_SCALP | kept | 270 | 78.56 | 19.11 | 18.02 | 12.39 | 14.16 | 6.31 | 8.45 | 4.19 |
| MOVER_TREND_PULLBACK | filtered | 1713 | 56.72 | 18.08 | 18.02 | 7.74 | 12.85 | 6.00 | 9.51 | 3.85 |
| MOVER_TREND_PULLBACK | kept | 4745 | 76.62 | 19.73 | 18.02 | 7.72 | 12.66 | 6.75 | 9.25 | 4.01 |
| QUIET_COMPRESSION_BREAK | filtered | 116 | 50.28 | 18.79 | 15.93 | 10.71 | 14.08 | 7.11 | 4.57 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 111 | 71.73 | 19.09 | 17.06 | 10.68 | 14.09 | 7.14 | 5.14 | 0.00 |
| SR_FLIP_RETEST | filtered | 31 | 51.59 | 22.68 | 12.84 | 6.68 | 14.06 | 5.48 | 8.74 | 2.23 |
| SR_FLIP_RETEST | kept | 29 | 70.16 | 20.31 | 16.97 | 5.28 | 12.34 | 5.12 | 9.33 | 1.72 |
| TREND_PULLBACK_EMA | filtered | 104 | 57.75 | 16.57 | 18.00 | 7.59 | 12.93 | 7.55 | 8.63 | 4.93 |
| TREND_PULLBACK_EMA | kept | 144 | 76.84 | 17.99 | 18.00 | 7.52 | 14.00 | 7.24 | 9.34 | 4.74 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 52.23 | 20.20 | 16.13 | 14.00 | 14.93 | 5.00 | 3.14 | 3.93 |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 64.01 | 23.22 | 14.44 | 12.00 | 13.67 | 4.72 | 9.23 | 5.22 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 108 | 58.22 | 0.00 | 0.00 | 0.67 | 0.00 | 0.56 | 0.00 | 0.00 | 0.00 | **1.23** |
| DIVERGENCE_CONTINUATION | kept | 101 | 70.60 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.14** |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 47.53 | 0.00 | 0.00 | 0.00 | 0.00 | 1.14 | 0.00 | 0.00 | 0.00 | **1.14** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 49.14 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.20** |
| LIQUIDATION_REVERSAL | filtered | 1 | 61.20 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 124 | 49.65 | 0.00 | 0.00 | 1.15 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | **1.31** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 38 | 72.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 24 | 54.40 | 0.00 | 0.00 | 1.67 | 0.00 | 2.50 | 0.00 | 0.00 | 0.00 | **4.17** |
| MEAN_REVERT | kept | 18 | 70.19 | 0.00 | 0.00 | 0.00 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | **1.33** |
| MOVER_AVWAP_SCALP | filtered | 270 | 54.70 | 0.00 | 0.00 | 0.12 | 0.00 | 2.13 | 0.04 | 0.00 | 2.05 | **4.34** |
| MOVER_AVWAP_SCALP | kept | 270 | 78.56 | 0.00 | 0.00 | 0.24 | 0.00 | 1.96 | 0.28 | 0.00 | 0.42 | **2.90** |
| MOVER_TREND_PULLBACK | filtered | 1713 | 56.72 | 0.70 | 0.00 | 0.46 | 0.00 | 0.78 | 0.21 | 0.00 | 0.00 | **2.15** |
| MOVER_TREND_PULLBACK | kept | 4745 | 76.62 | 0.05 | 0.00 | 0.21 | 0.00 | 0.09 | 0.07 | 0.00 | 0.00 | **0.42** |
| QUIET_COMPRESSION_BREAK | filtered | 116 | 50.28 | 0.00 | 0.00 | 1.24 | 0.00 | 0.82 | 0.00 | 0.00 | 2.57 | **4.63** |
| QUIET_COMPRESSION_BREAK | kept | 111 | 71.73 | 0.00 | 0.00 | 0.26 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **0.48** |
| SR_FLIP_RETEST | filtered | 31 | 51.59 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| SR_FLIP_RETEST | kept | 29 | 70.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 104 | 57.75 | 0.00 | 0.00 | 0.00 | 0.00 | 1.25 | 0.63 | 0.00 | 0.00 | **1.88** |
| TREND_PULLBACK_EMA | kept | 144 | 76.84 | 0.00 | 0.00 | 0.63 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | **1.09** |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 52.23 | 0.00 | 0.00 | 4.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.96 | **5.44** |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 64.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **146597 held of 521414 seen** across 21 strategies; 3331 cells past the sample floor; **1691 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44375 | 653/43722/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/RANGE/NORMAL/BTC_FALLING (-1.23R) |
| MOVER_AVWAP_SCALP | 18851 | 188/18663/0 | 42% | -0.23 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11258 | 120/11138/0 | 36% | -0.31 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10274 | 90/10184/0 | 49% | -0.05 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKDOWN/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 8661 | 38/8623/0 | 40% | -0.22 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 7490 | 84/7406/0 | 34% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 7118 | 0/0/7118 | 42% | -0.11 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.48R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.99R) |
| SHADOW_RANGE_FADE | 6500 | 0/0/6500 | 37% | -0.10 | NY/MARKDOWN/EXPANDED/BTC_FALLING (+0.80R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 6051 | 387/5664/0 | 50% | -0.12 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5631 | 0/0/5631 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 3838 | 49/3789/0 | 41% | -0.24 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| SR_FLIP_RETEST | 3374 | 15/3359/0 | 47% | -0.26 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+0.87R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 2901 | 0/2901/0 | 35% | -0.27 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2866 | 2/2864/0 | 30% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| RANGE_FADE | 1321 | 4/1317/0 | 40% | -0.31 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1276 | 0/0/1276 | 53% | -0.05 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.10R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.38R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 326 | 0/326/0 | 35% | -0.49 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 114 | 24/90/0 | 42% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 214 | 27% / -0.58R | 214 | 52% / -0.15R | +0.44 | **ATR** |
| LIQUIDATION_REVERSAL | 19 | 32% / -0.50R | 19 | 58% / -0.20R | +0.31 | **ATR** |
| TREND_PULLBACK_EMA | 726 | 40% / -0.30R | 726 | 53% / -0.06R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1224 | 43% / -0.34R | 1224 | 55% / -0.14R | +0.20 | **ATR** |
| MA_CROSS_TREND_SHIFT | 35 | 37% / -0.28R | 35 | 40% / -0.12R | +0.16 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 141 | 34% / -0.23R | 141 | 45% / -0.08R | +0.14 | **ATR** |
| RANGE_FADE | 64 | 31% / -0.42R | 64 | 38% / -0.30R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1729 | 43% / -0.19R | 1729 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1082 | 40% / -0.25R | 1082 | 42% / -0.14R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 291 | 44% / -0.28R | 291 | 47% / -0.18R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 7426 | 50% / -0.10R | 7426 | 55% / -0.01R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1095 | 49% / -0.08R | 1095 | 55% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1002 | 47% / -0.16R | 1002 | 47% / -0.16R | -0.00 | **FIXED** |
| MEAN_REVERT | 274 | 50% / -0.10R | 274 | 49% / -0.10R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10289 | 28% | -0.25R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1729 | 47% | -0.07R | 216 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 90 | 48% | -0.08R | 55 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 984 | 35% / -0.20R | +0.86 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1308 | 40% / -0.19R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2204 | 34% / -0.14R | +0.70 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9295 | 36% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1245 | 38% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 980 | 34% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 891 | 33% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 212 | 29% / -0.46R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 279 | 32% / -0.53R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 229 | 49% / -0.01R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 50 | 34% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 283 | 34% / -0.35R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 54 | 28% / -0.42R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 25 | 44% / -0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×225]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 46/6) (sustained 46 cycles)
- **ALERT** `edge_reconciliation` — TREND_PULLBACK_EMA realized−counterfactual=+0.58R (bound 0.3) (streak 883/6) (sustained 883 cycles)
- **ALERT** `tuned_variants` — 670 non-stamps — atr_arm_uncomputable=670 (seen=24159 stamped=3030 skipped=20459) (streak 883/6) (sustained 883 cycles)
- **ALERT** `auto_dispatch` — 147 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=148) (streak 873/3) (sustained 873 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 46 fed / 0 quiet / 0 never delivered of 46 subscribed; 240560446 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 17 arms current, none stalled; covering 1588/1588 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 34 arms current, none stalled; covering 1165/1165 signals (100%) | 0 |
| auto_dispatch | violating | 147 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=148) (streak 873/3) | 873 |
| binance_ip_weight | ok | peak 179/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82017.10 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 77 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 4684 dup bars, 0 undedupable; ws 0 out-of-order, 891 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 55 cohorts, 30 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +3 / upstream +30 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2840/2858 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 4 of 134 open dark rows are not being advanced (worst: CHIPUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 41/120) | 41 |
| dark_sar_arms | ok | no open arms; covering 2837/2855 signals (99%) | 0 |
| depth_feed | ok | 46/46 books fresh (stale 0, never 0, thin 0); 90779394 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | TREND_PULLBACK_EMA realized−counterfactual=+0.58R (bound 0.3) (streak 883/6) | 883 |
| emission_controller | ok | last cycle 1420s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×225]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 46/6) | 46 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=64, profile_reject=6. Held back in this window: session_quality=109, profile_reject=21. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 5/6) | 5 |
| firestore_read_budget | ok | 1,361 reads/day of 50,000 [engine 1,322, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5520 sealed bars over 46 symbols; 1375 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +107 but output +0 (streak 2/6) | 2 |
| indicator_cache_key | ok | 394390 frozen value(s) avoided; 1397438 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.24R over n=3789 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +15 / upstream +107 | 0 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 11 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2777995 evicted (sampled: execution:trigger_not_confirmed 400/1001434, execution:overextended 400/881702, setup_compat:regime_STRONG_TREND 400/455104) | 0 |
| price_action_lane | ok | 2054693 evaluated, 2656 emitted; layer1 2656 stamped / 0 blind; cooldown=289726, delta_opposed=173166, no_footprint=845280, no_opposing_target=2958, no_sweep=573372, rr_below_floor=167535 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.32R over n=1317 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +23 / upstream +107 | 0 |
| sar_alignment_crosscheck | ok | 2294/56868 disagreed (4.0%) | 0 |
| sar_exit_shadow | violating | upstream +107 but output +0 (streak 2/6) | 2 |
| sar_hold_arm | ok | 1852 held arms settled, 148 unscored, 34 still walking (34 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 32/32 resolvable | 0 |
| sar_live_arms | ok | 34 arms current, none stalled; covering 1165/1165 signals (100%) | 0 |
| sar_refresh_budget | ok | 4 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 432 records await one (32 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 44.52s, worst 193.7s over 22776 lifetime cycles; lifetime 455 over 60s, 36 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.95s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 987475 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (0.31s to run, worst 154.4s), 1994 overrun(s) of 18503 cycles, TTL 900s; slowest signals=0.09s, data_intake=0.08s, pair_context=0.04s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=1687, gate reads=0, withheld=1687) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +114 / upstream +107 | 0 |
| structural_snap | ok | 6000/6000 measured, 19 blind, 0 levels moved (refusals: redetect_cooldown=1894) | 0 |
| structural_veto_lane | ok | 4196 stamped; 0 with no readable level book, 98 with clear air ahead, 3126 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +107 / upstream +30 | 0 |
| tuned_variants | violating | 670 non-stamps — atr_arm_uncomputable=670 (seen=24159 stamped=3030 skipped=20459) (streak 883/6) | 883 |
| unlock_shorts | ok | 14 open, 43 scheduled, calendar 1.2h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 85 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2166330`
- `Path funnel` emissions: `50`
- `Regime distribution` emissions: `50`
- `QUIET_SCALP_BLOCK` events: `153`
- `confidence_gate` events: `7997`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **30**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 3995 | 3995 | 3995 | 0 |
| futures_aggtrade | 7 | 5482 | 6691 | 7195 | 0 |
| futures_depth | 17 | 3775 | 7484 | 7525 | 0 |
| futures_liq | 4 | 3282 | 4665 | 17864 | 0 |
| futures_mover | 1 | 20091 | 20091 | 20091 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=1294, present=350644] state[empty=1294, populated=350644] buckets[many=350644, none=1294] sources[none] quality[none]
- funding_rate: presence[absent=36595, present=315343] state[empty=36595, populated=315343] buckets[few=315343, none=36595] sources[none] quality[none]
- liquidation_clusters: presence[absent=202084, present=149854] state[empty=202084, populated=149854] buckets[few=123496, none=202084, some=26358] sources[none] quality[none]
- oi_snapshot: presence[absent=36595, present=315343] state[empty=36595, populated=315343] buckets[few=48, many=314697, none=36595, some=598] sources[none] quality[none]
- order_book: presence[absent=110731, present=241207] state[populated=241207, unavailable=110731] buckets[few=241207, none=110731] sources[book_ticker=241207, unavailable=110731] quality[none=110731, top_of_book_only=241207]
- orderblocks: presence[absent=351938] state[empty=351938] buckets[none=351938] sources[measured_dark=351938] quality[none]
- recent_ticks: presence[present=351938] state[populated=351938] buckets[many=351938] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.146167993545532` sec
- Median create→first breach: `5381.669646024704` sec
- Median create→terminal: `5381.669667005539` sec
- Median first breach→terminal: `4.00543212890625e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.6911829517990777 | 0.8339158780305456 | 0.8288944812950585 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 2.7341774176202636 | 3.0 | 0.9113924725400879 | 1 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 4.444724193818807 | 1.2989743022410893 | 3.4217183405017564 | 1 | 0 |
| MEAN_REVERT | 1 | 1 | 1.883666681066141 | 3.0 | 0.6278888936887137 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 3.2823072050740394 | 2.9663999999999837 | 1.106495147341578 | 1 | 0 |
| MOVER_TREND_PULLBACK | 18 | 18 | 4.402746136232178 | 3.0 | 1.5369826068040409 | 14 | 4 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.0062836561682225 | 1.0481494084322764 | 0.8724506345049343 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.139 | 6534.979294419289 | 6535.210180044174 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.7755 | 3243.7990044355392 | 3243.7990584373474 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.299 | 38381.06138801575 | 38381.06141090393 |
| MEAN_REVERT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 1410.762622833252 | 1410.76265001297 |
| MOVER_AVWAP_SCALP | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.9877 | 14056.86601114273 | 14060.83975315094 |
| MOVER_TREND_PULLBACK | 18 | 18 | 5.6 | 50.0 | 5.6 | 0.0 | -1.4607 | 4078.867866873741 | 4078.8678889274597 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 25.0 | 25.0 | 25.0 | 0.0 | 0.1061 | 11893.1046615839 | 11894.080398440361 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 519 | 8 | 329 | 0.0 | 0.0 | None | None | 190 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1893 | 45 | 1432 | 0.0 | 0.0 | None | None | 461 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-125`
- Gating Δ: `-6963`
- No-generation Δ: `-92267`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0517, "current_avg_pnl": 0.139, "current_win_rate": 50.0, "previous_avg_pnl": 0.1907, "previous_win_rate": 25.0, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 4.4959, "current_avg_pnl": 3.9877, "current_win_rate": 100.0, "previous_avg_pnl": -0.5082, "previous_win_rate": 0.0, "win_rate_delta": 100.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.0814, "current_avg_pnl": -1.4607, "current_win_rate": 5.6, "previous_avg_pnl": -0.3793, "previous_win_rate": 24.0, "win_rate_delta": -18.4}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.1099, "current_avg_pnl": 0.1061, "current_win_rate": 25.0, "previous_avg_pnl": 1.216, "previous_win_rate": 55.6, "win_rate_delta": -30.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -244, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 19, "geometry_changed_delta": 0, "geometry_preserved_delta": 78, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
