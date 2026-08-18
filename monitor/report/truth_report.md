# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `14` sec (warning=False)
- Latest performance record age: `1543` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 21 | 21 | 21 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2420 | 2420 | 2252 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 15595 | 15597 | 6 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 16067 | 16070 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 15902 | 15562 | 502 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 16091 | 15938 | 182 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 16369 | 16325 | 60 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 14039 | 14048 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 16122 | 16134 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 16140 | 15773 | 531 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 16674 | 17872 | 160 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 15606 | 14525 | 2128 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 16267 | 16273 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 16072 | 16086 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 15879 | 15812 | 85 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 16303 | 15913 | 572 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 15764 | 15813 | 44 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 13501 | 13206 | 371 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 13578 | 13549 | 77 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 15574 | 15587 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 14051 | 14056 | 17 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 561 | 561 | 487 | 6 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 247 | 247 | 45 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 1767 | 1767 | 1736 | 4 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 4 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 1118 | 1118 | 980 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 376 | 376 | 106 | 18 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 5968 | 5968 | 3788 | 138 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 400 | 400 | 202 | 34 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1210 | 1210 | 1098 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 159 | 159 | 153 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 327 | 327 | 307 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 24 | 24 | 18 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 473 | 473 | 7 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=15597): breakout_not_found=8883, basic_filters_failed=3277, move_not_fresh=2278, breakout_stale=844, retest_proximity_failed=236, volume_spike_missing=73, ema_alignment_reject=4, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=16070): cls_disabled_merged_into_lsr=16070
- **EVAL::DIVERGENCE_CONTINUATION** (total=15562): cvd_divergence_failed=6634, h1_trend_not_aligned=4086, basic_filters_failed=3051, ema_alignment_reject=1454, retest_proximity_failed=198, missing_fvg_or_orderblock=111, regime_blocked=28
- **EVAL::FAILED_AUCTION_RECLAIM** (total=15938): auction_not_detected=10978, basic_filters_failed=2943, regime_blocked=933, reclaim_hold_failed=550, tail_too_small=534
- **EVAL::FUNDING_EXTREME** (total=16325): funding_not_extreme=11825, basic_filters_failed=3068, missing_funding_rate=694, ema_alignment_reject=430, rsi_reject=203, momentum_reject=58, cvd_divergence_failed=38, missing_fvg_or_orderblock=9
- **EVAL::LIQUIDATION_REVERSAL** (total=14048): cascade_threshold_not_met=10761, basic_filters_failed=3139, cvd_divergence_failed=72, rsi_reject=72, missing_fvg_or_orderblock=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=16134): no_ma_cross=12581, basic_filters_failed=3063, ma_cross_cooldown=358, ma_cross_htf_misaligned=132
- **EVAL::MEAN_REVERT** (total=15773): no_extension=14004, basic_filters_failed=1769
- **EVAL::MOVER_AVWAP_SCALP** (total=17872): no_mover_leg=7587, no_avwap_tag=5086, basic_filters_failed=3352, avwap_slope_against=1210, avwap_reclaim_no_volume=349, no_avwap_reclaim=260, anchor_too_recent=28
- **EVAL::MOVER_TREND_PULLBACK** (total=14525): mover_run_too_small=8710, basic_filters_failed=3319, no_reclaim=2192, no_pullback_tag=304
- **EVAL::OPENING_RANGE_BREAKOUT** (total=16273): feature_disabled=16273
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=16086): regime_blocked=11164, breakout_not_found=3306, basic_filters_failed=922, adx_reject=668, ema_alignment_reject=26
- **EVAL::QUIET_COMPRESSION_BREAK** (total=15812): regime_blocked=5817, compression_not_detected=4413, breakout_not_detected=3312, basic_filters_failed=2016, volume_confirmation_failed=245, rsi_reject=8, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=15913): no_range_edge=14144, basic_filters_failed=1769
- **EVAL::SR_FLIP_RETEST** (total=15813): flip_close_not_confirmed=10982, basic_filters_failed=2930, regime_blocked=927, long_break_volume_thin=331, h1_break_not_confirmed=247, reclaim_hold_failed=183, retest_out_of_zone=147, long_acceptance_not_held=41, ema_alignment_reject=13, wick_quality_failed=8, missing_fvg_or_orderblock=4
- **EVAL::STANDARD** (total=13206): momentum_reject=4541, adx_reject=3924, sweeps_not_detected=1597, basic_filters_failed=1244, macd_reject=1026, ema_alignment_reject=523, htf_poi_unanchored=319, rsi_reject=13, mtf_reject=10, invalid_sl_geometry=9
- **EVAL::TREND_PULLBACK** (total=13549): h1_trend_not_aligned=4328, ema_alignment_reject=2797, h1_pullback_not_confirmed=2174, basic_filters_failed=1564, no_ema_reclaim_close=883, body_conviction_fail=515, ema_not_tested_prev=500, rsi_reject=431, prev_already_below_emas=128, prev_already_above_emas=66, momentum_flat=41, no_prev_low_break=39, no_prev_high_break=29, regime_blocked=23, momentum_reject=21, missing_fvg_or_orderblock=7, ema21_not_tagged=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=15587): breakout_not_found=10156, basic_filters_failed=3276, move_not_fresh=1465, breakout_stale=529, retest_proximity_failed=144, volume_spike_missing=11, move_exhausted=5, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=14056): momentum_reject=10431, recent_ticks_insufficient=2745, basic_filters_failed=880

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=5): execution:overextended=5
- **DIVERGENCE_CONTINUATION** (total=36): setup_compat:regime_VOLATILE_UNSUITABLE=36
- **FAILED_AUCTION_RECLAIM** (total=213): setup_compat:regime_STRONG_TREND=133, execution:overextended=80
- **FUNDING_EXTREME_SIGNAL** (total=202): execution:trigger_not_confirmed=196, context_floor=6
- **LIQUIDATION_REVERSAL** (total=3): execution:trigger_not_confirmed=3
- **LIQUIDITY_SWEEP_REVERSAL** (total=500): execution:trigger_not_confirmed=195, execution:overextended=156, setup_compat:regime_STRONG_TREND=149
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=2, execution:trigger_not_confirmed=2, execution:overextended=1, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=732): setup_compat:regime_STRONG_TREND=375, setup_compat:regime_WEAK_TREND=252, execution:overextended=105
- **MOVER_AVWAP_SCALP** (total=220): execution:overextended=130, execution:trigger_not_confirmed=84, entry_quality=6
- **MOVER_TREND_PULLBACK** (total=2957): execution:trigger_not_confirmed=1648, execution:overextended=1029, entry_quality=280
- **QUIET_COMPRESSION_BREAK** (total=7): execution:trigger_not_confirmed=7
- **RANGE_FADE** (total=767): setup_compat:regime_STRONG_TREND=378, setup_compat:regime_WEAK_TREND=223, execution:overextended=84, setup_compat:regime_VOLATILE_UNSUITABLE=59, context_edge=16, setup_compat:regime_BREAKOUT_EXPANSION=7
- **TREND_PULLBACK_EMA** (total=310): setup_compat:regime_CLEAN_RANGE=250, setup_compat:regime_DIRTY_RANGE=51, setup_compat:regime_VOLATILE_UNSUITABLE=7, entry_quality=2
- **VOLUME_SURGE_BREAKOUT** (total=4): execution:overextended=4
- **WHALE_MOMENTUM** (total=458): execution:trigger_not_confirmed=458

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 27081 | 34.2% |
| RANGING | 24276 | 30.7% |
| TRENDING_DOWN | 12858 | 16.3% |
| TRENDING_UP | 10466 | 13.2% |
| VOLATILE | 4439 | 5.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **148**
- Average confidence gap to threshold: **14.30** (samples=148) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HBARUSDT=26, BTCUSDT=15, 1000SHIBUSDT=11, ETHUSDT=10, FILUSDT=9, XLMUSDT=8, TRUMPUSDT=8, BNBUSDT=6, XMRUSDT=5, GRVTUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 30 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 48 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 9 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 27 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 23 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 13 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 9 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 34 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 16 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 162 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 255 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 32 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1349 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 93 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 11 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 181 |
| SR_FLIP_RETEST | filtered | min_confidence | 2 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 6 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 28 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 6 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 7 |
| WHALE_MOMENTUM | filtered | min_confidence | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 33 | 56.10 | 63.45 | 7.35 | 20.46 | 19.78 | 17.74 | 1.15 | 8.57 |
| DIVERGENCE_CONTINUATION | kept | 48 | 68.48 | 65.00 | -3.48 | 20.88 | 19.36 | 17.71 | 0.15 | 1.48 |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 52.40 | 63.05 | 10.65 | 20.96 | 19.59 | 20.00 | 3.61 | 6.75 |
| FAILED_AUCTION_RECLAIM | kept | 27 | 69.22 | 65.00 | -4.22 | 20.32 | 19.91 | 20.00 | 2.37 | 2.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 23 | 52.21 | 61.00 | 8.79 | 20.10 | 14.19 | 17.16 | 4.61 | 3.03 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.75 | 65.00 | -3.75 | 20.20 | 16.80 | 17.00 | 2.50 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 56.30 | 61.00 | 4.70 | 21.00 | 20.00 | 20.00 | 0.00 | 12.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 67.70 | 65.00 | -2.70 | 20.30 | 18.85 | 17.30 | 1.23 | 0.74 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.30 | 65.00 | -0.30 | 20.00 | 18.50 | 15.80 | 0.00 | -3.00 |
| MEAN_REVERT | kept | 9 | 71.93 | 65.00 | -6.93 | 21.11 | 16.26 | 17.33 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 50 | 55.03 | 45.24 | -9.79 | 21.06 | 12.07 | 15.80 | 2.68 | 9.89 |
| MOVER_AVWAP_SCALP | kept | 162 | 77.14 | 65.00 | -12.14 | 20.46 | 16.61 | 15.80 | 4.16 | 0.17 |
| MOVER_TREND_PULLBACK | filtered | 287 | 56.34 | 63.67 | 7.33 | 19.88 | 18.07 | 15.80 | 4.24 | 16.33 |
| MOVER_TREND_PULLBACK | kept | 1349 | 77.39 | 65.00 | -12.39 | 20.31 | 18.71 | 15.80 | 4.50 | 0.96 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 80.50 | 65.00 | -15.50 | 20.80 | 20.00 | 19.00 | 4.50 | 6.00 |
| QUIET_COMPRESSION_BREAK | filtered | 104 | 52.55 | 64.81 | 12.26 | 21.14 | 19.75 | 20.00 | 0.00 | 11.00 |
| QUIET_COMPRESSION_BREAK | kept | 181 | 76.27 | 65.00 | -11.27 | 20.93 | 19.66 | 20.00 | 0.00 | -0.84 |
| SR_FLIP_RETEST | filtered | 2 | 58.50 | 61.00 | 2.50 | 21.20 | 20.00 | 20.00 | 1.00 | 6.50 |
| SR_FLIP_RETEST | kept | 6 | 69.70 | 65.00 | -4.70 | 20.70 | 20.00 | 17.40 | 2.42 | 3.33 |
| TREND_PULLBACK_EMA | filtered | 6 | 47.35 | 63.00 | 15.65 | 21.00 | 20.00 | 16.00 | 4.00 | 15.55 |
| TREND_PULLBACK_EMA | kept | 28 | 79.98 | 65.00 | -14.98 | 21.32 | 19.59 | 18.42 | 4.62 | 0.01 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 47.30 | 61.00 | 13.70 | 20.10 | 14.70 | 20.00 | 3.00 | 8.00 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 75.18 | 65.00 | -10.18 | 19.22 | 16.53 | 20.00 | 4.75 | 3.93 |
| WHALE_MOMENTUM | filtered | 13 | 57.07 | 63.15 | 6.08 | 23.12 | 14.46 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 33 | 56.10 | 22.82 | 12.55 | 6.18 | 12.61 | 5.29 | 7.53 | 1.15 |
| DIVERGENCE_CONTINUATION | kept | 48 | 68.48 | 23.00 | 13.83 | 7.06 | 13.06 | 5.58 | 8.58 | 0.15 |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 52.40 | 21.95 | 15.05 | 7.89 | 13.74 | 5.24 | 4.31 | 3.61 |
| FAILED_AUCTION_RECLAIM | kept | 27 | 69.22 | 20.85 | 14.74 | 6.78 | 13.15 | 7.39 | 5.94 | 2.37 |
| FUNDING_EXTREME_SIGNAL | filtered | 23 | 52.21 | 25.00 | 11.04 | 3.65 | 13.78 | 6.35 | 5.15 | 4.61 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.75 | 25.00 | 13.00 | 6.00 | 13.00 | 6.25 | 5.50 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 56.30 | 25.00 | 14.00 | 6.00 | 14.00 | 5.00 | 4.30 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 67.70 | 22.54 | 16.15 | 3.69 | 11.85 | 5.73 | 7.25 | 1.23 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.30 | 25.00 | 14.00 | 3.00 | 11.00 | 5.00 | 7.30 | 0.00 |
| MEAN_REVERT | kept | 9 | 71.93 | 24.11 | 15.78 | 8.67 | 12.00 | 6.33 | 5.04 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 50 | 55.03 | 18.92 | 18.00 | 9.12 | 12.48 | 5.80 | 7.68 | 2.68 |
| MOVER_AVWAP_SCALP | kept | 162 | 77.14 | 18.70 | 18.04 | 9.31 | 13.64 | 5.52 | 8.44 | 4.16 |
| MOVER_TREND_PULLBACK | filtered | 287 | 56.34 | 18.18 | 18.07 | 7.95 | 12.78 | 5.37 | 8.85 | 4.24 |
| MOVER_TREND_PULLBACK | kept | 1349 | 77.39 | 19.19 | 18.04 | 8.24 | 13.61 | 5.84 | 9.04 | 4.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 80.50 | 17.00 | 18.00 | 15.00 | 14.00 | 10.00 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 104 | 52.55 | 18.54 | 17.58 | 10.73 | 14.12 | 7.10 | 3.54 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 181 | 76.27 | 19.39 | 17.43 | 11.62 | 14.05 | 6.67 | 7.94 | 0.00 |
| SR_FLIP_RETEST | filtered | 2 | 58.50 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 4.00 | 1.00 |
| SR_FLIP_RETEST | kept | 6 | 69.70 | 23.67 | 16.33 | 6.00 | 14.00 | 5.00 | 5.62 | 2.42 |
| TREND_PULLBACK_EMA | filtered | 6 | 47.35 | 9.50 | 18.00 | 8.25 | 17.00 | 7.50 | 6.15 | 4.00 |
| TREND_PULLBACK_EMA | kept | 28 | 79.98 | 20.75 | 18.00 | 8.09 | 14.21 | 6.18 | 8.99 | 4.62 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 47.30 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 2.30 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 75.18 | 21.00 | 15.33 | 12.00 | 14.00 | 5.08 | 6.95 | 4.75 |
| WHALE_MOMENTUM | filtered | 13 | 57.07 | 24.85 | 12.62 | 7.85 | 12.08 | 7.23 | 2.45 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 33 | 56.10 | 0.00 | 0.00 | 0.39 | 0.00 | 0.65 | 0.00 | 0.00 | 0.00 | **1.04** |
| DIVERGENCE_CONTINUATION | kept | 48 | 68.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 19 | 52.40 | 0.00 | 0.00 | 1.01 | 0.00 | 2.53 | 0.00 | 0.00 | 0.00 | **3.54** |
| FAILED_AUCTION_RECLAIM | kept | 27 | 69.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 23 | 52.21 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.42** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2 | 56.30 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 67.70 | 0.00 | 0.00 | 0.74 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.74** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 9 | 71.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 50 | 55.03 | 1.80 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.86 | **2.98** |
| MOVER_AVWAP_SCALP | kept | 162 | 77.14 | 0.06 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.32 | **0.43** |
| MOVER_TREND_PULLBACK | filtered | 287 | 56.34 | 6.66 | 0.00 | 1.35 | 0.00 | 1.46 | 0.00 | 0.00 | 0.06 | **9.53** |
| MOVER_TREND_PULLBACK | kept | 1349 | 77.39 | 0.04 | 0.00 | 0.45 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **0.77** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 80.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 104 | 52.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 7.57 | **8.32** |
| QUIET_COMPRESSION_BREAK | kept | 181 | 76.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.24 | 0.00 | 0.00 | 0.36 | **0.60** |
| SR_FLIP_RETEST | filtered | 2 | 58.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 6 | 69.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 6 | 47.35 | 0.00 | 0.00 | 0.00 | 0.00 | 10.80 | 0.00 | 0.00 | 0.00 | **10.80** |
| TREND_PULLBACK_EMA | kept | 28 | 79.98 | 0.00 | 0.00 | 0.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.97** |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 47.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 75.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.60 | **0.60** |
| WHALE_MOMENTUM | filtered | 13 | 57.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **144995 held of 312180 seen** across 21 strategies; 3251 cells past the sample floor; **1379 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 34155 | 193/33962/0 | 48% | -0.08 | NY/MARKDOWN/EXPANDED/BTC_RISING (+1.22R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.16R) |
| FAILED_AUCTION_RECLAIM | 17399 | 20/17379/0 | 52% | +0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16600 | 1/16599/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 12424 | 6/12418/0 | 45% | -0.10 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (+1.32R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 10191 | 30/10161/0 | 36% | -0.30 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| QUIET_COMPRESSION_BREAK | 9866 | 0/9866/0 | 46% | -0.09 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 6132 | 4/6128/0 | 46% | -0.26 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 5508 | 0/0/5508 | 43% | -0.11 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.56R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.93R) |
| LIQUIDITY_SWEEP_REVERSAL | 5198 | 11/5187/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 5033 | 0/0/5033 | 38% | -0.01 | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.55R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.41R) |
| MEAN_REVERT | 4892 | 4/4888/0 | 68% | +0.30 | NY/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.28R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-1.54R) |
| SHADOW_FUNDING_FADE | 4622 | 0/0/4622 | 36% | -0.37 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.20R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 4145 | 0/4145/0 | 33% | -0.36 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.60R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2669 | 19/2650/0 | 41% | +0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2621 | 4/2617/0 | 31% | -0.47 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.29R) |
| WHALE_MOMENTUM | 2132 | 0/2132/0 | 46% | -0.28 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.89R) |
| SHADOW_CASCADE_REVERSAL | 628 | 0/0/628 | 49% | -0.16 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.05R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-2.04R) |
| BREAKDOWN_SHORT | 533 | 11/522/0 | 45% | +0.04 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 75 | 0/75/0 | 83% | +0.64 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 44 | 1/43/0 | 34% | -0.41 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.60R (n=28, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.60R (n=28, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `SHADOW_CASCADE_REVERSAL @ OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL` -2.04R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 143 | 36% / -0.38R | 143 | 57% / -0.10R | +0.28 | **ATR** |
| TREND_PULLBACK_EMA | 288 | 42% / -0.32R | 288 | 48% / -0.12R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 728 | 39% / -0.22R | 728 | 43% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 2788 | 46% / -0.20R | 2788 | 49% / -0.10R | +0.11 | **ATR** |
| DIVERGENCE_CONTINUATION | 1039 | 47% / -0.12R | 1039 | 52% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 803 | 51% / -0.17R | 803 | 55% / -0.11R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4532 | 51% / -0.07R | 4532 | 54% / -0.01R | +0.05 | **ATR** |
| MA_CROSS_TREND_SHIFT | 17 | 35% / -0.25R | 17 | 35% / -0.20R | +0.05 | **ATR** |
| WHALE_MOMENTUM | 180 | 51% / -0.25R | 180 | 51% / -0.28R | -0.04 | **FIXED** |
| RANGE_FADE | 288 | 23% / -0.56R | 288 | 26% / -0.53R | +0.04 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 98 | 40% / -0.06R | 98 | 51% / -0.03R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1681 | 45% / -0.14R | 1681 | 45% / -0.16R | -0.03 | **FIXED** |
| MEAN_REVERT | 556 | 53% / -0.02R | 556 | 49% / -0.01R | +0.02 | **ATR** |
| BREAKDOWN_SHORT | 23 | 35% / -0.20R | 23 | 35% / -0.19R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2359 | 47% / -0.11R | 2359 | 47% / -0.11R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 11 | 55% / -0.01R | 11 | 55% / +0.01R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6685 | 30% | -0.18R | 294 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 718 | 42% | -0.10R | 147 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 47 | 57% | +0.03R | 26 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1248 | 29% / -1.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 34 | 29% / -0.36R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5684 | 39% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1072 | 32% / -0.54R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 121 | 24% / -0.82R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 911 | 34% / -1.21R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1246 | 37% / -0.14R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 466 | 45% / -0.72R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 176 | 30% / -1.00R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 348 | 31% / -0.56R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 849 | 32% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 23 | 17% / -0.70R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 287 | 45% / -0.09R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 108 | 39% / -0.12R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.50R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 64 | 41% / -0.27R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 47 · alerting: **3** · boot grace active: False
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 7/6) (sustained 7 cycles)
- **ALERT** `cohort_edge_gate` — all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 8/6) (sustained 8 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.53R (bound 0.3) (streak 8/6) (sustained 8 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1123160 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 6 arms current, none stalled; covering 145/145 signals (100%) | 0 |
| auto_dispatch | ok | attempts=2 fanouts=2 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64126.20 | 0 |
| candle_coverage | ok | 83/83 symbols with ≥20 15m candles, 81/83 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 935 dup bars, 0 undedupable; ws 0 out-of-order, 184 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 8/6) | 8 |
| context_emission_policy | ok | output +4 / upstream +7 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1141/1153 signals (99%) | 0 |
| dark_promotion_rules | ok | 2 rule(s) armed, 1 promoted today — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 11 of 87 open dark rows are not being advanced (worst: SOPHUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 8/120) | 8 |
| dark_sar_arms | ok | no open arms; covering 1128/1140 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 434055 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.53R (bound 0.3) (streak 8/6) | 8 |
| emission_controller | ok | last cycle 1396s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4225 stamps (MEAN_REVERT=519, MOVER_AVWAP_SCALP=117, MOVER_TREND_PULLBACK=3066, RANGE_FADE=352, TREND_PULLBACK_EMA=171), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 7/6) | 7 |
| footprint_bars | ok | 3920 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +10 / upstream +47 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | backlog 9 detections since last emission | 0 |
| mean_revert_path | ok | output +9 / upstream +47 | 0 |
| mover_admission_metadata | ok | 871 symbols known, 169 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 5 held, 5 with scan counts, 5 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2986 rows held, 560800 evicted (sampled: execution:overextended 400/206818, execution:trigger_not_confirmed 400/193019, setup_compat:regime_STRONG_TREND 400/67983) | 0 |
| price_action_lane | ok | 10928 evaluated, 33 emitted; layer1 33 stamped / 0 blind; cooldown=1245, delta_opposed=781, no_footprint=3009, no_sweep=5066, rr_below_floor=794 | 0 |
| promoted_pair_integrity | ok | 5/5 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 46 detections since last progress | 0 |
| range_fade_path | ok | output +7 / upstream +47 | 0 |
| sar_alignment_crosscheck | ok | 6/779 disagreed (0.8%) | 0 |
| sar_exit_shadow | ok | output +8 / upstream +47 | 0 |
| sar_hold_arm | ok | 252 held arms settled, 51 unscored, 5 still walking (3 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 28/80 unfetchable (35%); top cause: gap or duplicate bar in the 15m window; symbols: AKEUSDT, BSBUSDT, BTCUSDT, BTWUSDT, CHIPUSDT +8 more (streak 1/6) | 1 |
| sar_live_arms | ok | 5 arms current, none stalled; covering 154/154 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 480 records await one (52 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| setup_tf_resolver | ok | 6598 resolutions, 3630 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +81 / upstream +47 | 0 |
| structural_snap | ok | 4201/4201 measured, 30 blind, 0 levels moved (refusals: redetect_cooldown=111) | 0 |
| structural_veto_lane | ok | 150 stamped; 0 with no readable level book, 5 with clear air ahead, 106 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +47 / upstream +7 | 0 |
| tuned_variants | ok | seen=336 stamped=46 skipped=289, residue 1 (atr_arm_uncomputable=1) | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `48295`
- `Path funnel` emissions: `10`
- `Regime distribution` emissions: `10`
- `QUIET_SCALP_BLOCK` events: `148`
- `confidence_gate` events: `2376`
- `free_channel_post` events: `8`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **33**
- Total REST-fallback activations: **15**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 18 | 35230 | 62556 | 97684 | 0 |
| futures_aggtrade | 4 | 38934 | 59232 | 68282 | 0 |
| futures_depth | 6 | 23936 | 41971 | 53793 | 0 |
| futures_liq | 5 | 17417 | 18667 | 59232 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 15 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **8**

| Source | Count |
|---|---:|
| signal_close | 7 |
| regime_shift | 1 |

- By severity: HIGH=8

## Dependency readiness
- cvd: presence[present=67324] state[populated=67324] buckets[many=66789, some=535] sources[none] quality[none]
- funding_rate: presence[absent=6870, present=60454] state[empty=6870, populated=60454] buckets[few=60454, none=6870] sources[none] quality[none]
- liquidation_clusters: presence[absent=45423, present=21901] state[empty=45423, populated=21901] buckets[few=17976, none=45423, some=3925] sources[none] quality[none]
- oi_snapshot: presence[absent=5056, present=62268] state[empty=5056, populated=62268] buckets[few=490, many=59666, none=5056, some=2112] sources[none] quality[none]
- order_book: presence[absent=34151, present=33173] state[populated=33173, unavailable=34151] buckets[few=33173, none=34151] sources[book_ticker=33173, unavailable=34151] quality[none=34151, top_of_book_only=33173]
- orderblocks: presence[absent=67324] state[empty=67324] buckets[none=67324] sources[measured_dark=67324] quality[none]
- recent_ticks: presence[present=67324] state[populated=67324] buckets[many=67324] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `44.739755392074585` sec
- Median create→first breach: `1270.9598286151886` sec
- Median create→terminal: `1310.5003480911255` sec
- Median first breach→terminal: `16.33975899219513` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.7569152812966466 | 3.0 | 0.9189717604322155 | 0 | 1 |
| MEAN_REVERT | 1 | 1 | 1.5895353965083403 | 3.0 | 0.5298451321694467 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 3.7367524954488816 | 3.0 | 1.245584165149627 | 1 | 0 |
| MOVER_TREND_PULLBACK | 6 | 6 | 4.307522377690378 | 3.0 | 1.5605314713588534 | 5 | 1 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.616575849170468 | 3.0 | 0.8721919497234892 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1697.2399609088898 | 1720.1815030574799 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 5015.692355155945 | 5020.822237968445 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 3.451 | 1345.9991610050201 | 1407.3134469985962 |
| MOVER_TREND_PULLBACK | 6 | 6 | 0.0 | 50.0 | 0.0 | 0.0 | 0.1711 | 1106.8497881889343 | 1132.6747685670853 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 508.46697998046875 | 509.8073000907898 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 159 | 2 | 153 | 0.0 | 0.0 | None | None | 6 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 327 | 9 | 307 | 0.0 | 0.0 | 508.46697998046875 | 509.8073000907898 | 20 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `224`
- Gating Δ: `11207`
- No-generation Δ: `294139`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.2992, "current_avg_pnl": 0.1711, "current_win_rate": 0.0, "previous_avg_pnl": 0.4703, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 6, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": 20, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 508.47, "median_terminal_delta_sec": 509.81, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
