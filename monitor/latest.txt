# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: MOVER_AVWAP_SCALP, POST_DISPLACEMENT_CONTINUATION
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1552` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 90 | 90 | 54 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 11292 | 11292 | 10352 | 10 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 100839 | 100845 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 97142 | 97142 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 96718 | 93908 | 3219 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 97202 | 96124 | 1191 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 98007 | 97716 | 316 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 88296 | 88309 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 97321 | 97361 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 97372 | 94411 | 4014 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 104853 | 110074 | 937 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 100860 | 94380 | 10385 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 97542 | 97542 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 97156 | 97157 | 32 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 96693 | 96579 | 134 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 98432 | 96693 | 2379 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 96195 | 96522 | 124 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 86769 | 83037 | 4078 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 87128 | 86464 | 740 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 100795 | 100823 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 88309 | 88338 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3970 | 3970 | 2730 | 6 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1095 | 1095 | 263 | 4 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 18932 | 18932 | 17831 | 21 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 6 | 6 | 1 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 9555 | 9555 | 7686 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2375 | 2375 | 358 | 58 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 28321 | 28321 | 13598 | 247 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 88 | 88 | 56 | 10 | active-healthy (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 516 | 516 | 185 | 33 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 6276 | 6276 | 5960 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 395 | 395 | 153 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2803 | 2803 | 2255 | 38 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 69 | 69 | 14 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=100845): breakout_not_found=55189, basic_filters_failed=33896, move_not_fresh=7943, breakout_stale=2606, retest_proximity_failed=1070, volume_spike_missing=138, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=97142): cls_disabled_merged_into_lsr=97142
- **EVAL::DIVERGENCE_CONTINUATION** (total=93908): cvd_divergence_failed=42927, basic_filters_failed=30704, h1_trend_not_aligned=14264, ema_alignment_reject=4998, retest_proximity_failed=772, missing_fvg_or_orderblock=243
- **EVAL::FAILED_AUCTION_RECLAIM** (total=96124): auction_not_detected=56629, basic_filters_failed=30245, reclaim_hold_failed=3885, tail_too_small=2966, regime_blocked=2281, rsi_reject=118
- **EVAL::FUNDING_EXTREME** (total=97716): funding_not_extreme=58587, basic_filters_failed=28471, missing_funding_rate=6613, ema_alignment_reject=1913, rsi_reject=1504, cvd_divergence_failed=297, momentum_reject=294, missing_fvg_or_orderblock=37
- **EVAL::LIQUIDATION_REVERSAL** (total=88309): cascade_threshold_not_met=56733, basic_filters_failed=30773, cvd_divergence_failed=527, rsi_reject=262, missing_fvg_or_orderblock=13, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=97361): no_ma_cross=65655, basic_filters_failed=30740, ma_cross_htf_misaligned=617, ma_cross_cooldown=349
- **EVAL::MEAN_REVERT** (total=94411): no_extension=75790, basic_filters_failed=18621
- **EVAL::MOVER_AVWAP_SCALP** (total=110074): no_avwap_tag=34396, basic_filters_failed=34207, no_mover_leg=32371, avwap_slope_against=5946, avwap_reclaim_no_volume=1898, no_avwap_reclaim=1201, anchor_too_recent=55
- **EVAL::MOVER_TREND_PULLBACK** (total=94380): mover_run_too_small=43545, basic_filters_failed=34049, no_reclaim=14343, no_pullback_tag=2443
- **EVAL::OPENING_RANGE_BREAKOUT** (total=97542): feature_disabled=97542
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=97157): regime_blocked=53807, breakout_not_found=31465, basic_filters_failed=7938, adx_reject=3854, ema_alignment_reject=86, rsi_reject=7
- **EVAL::QUIET_COMPRESSION_BREAK** (total=96579): regime_blocked=45458, compression_not_detected=23472, basic_filters_failed=22279, breakout_not_detected=4994, volume_confirmation_failed=369, rsi_reject=5, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=96693): no_range_edge=78064, basic_filters_failed=18629
- **EVAL::SR_FLIP_RETEST** (total=96522): flip_close_not_confirmed=56387, basic_filters_failed=30197, retest_out_of_zone=2797, long_break_volume_thin=2575, regime_blocked=2274, h1_break_not_confirmed=1011, reclaim_hold_failed=527, long_acceptance_not_held=265, ema_alignment_reject=206, whipsaw_flip=177, wick_quality_failed=97, missing_fvg_or_orderblock=9
- **EVAL::STANDARD** (total=83037): momentum_reject=28768, adx_reject=16911, basic_filters_failed=15163, sweeps_not_detected=9304, ema_alignment_reject=6318, macd_reject=5259, htf_poi_unanchored=1187, rsi_reject=86, invalid_sl_geometry=41
- **EVAL::TREND_PULLBACK** (total=86464): basic_filters_failed=20595, h1_trend_not_aligned=17224, h1_pullback_not_confirmed=12364, ema_alignment_reject=11951, ema_not_tested_prev=6941, no_ema_reclaim_close=6524, body_conviction_fail=4279, rsi_reject=4128, prev_already_above_emas=1292, no_prev_high_break=639, momentum_flat=182, prev_already_below_emas=92, ema21_not_tagged=91, momentum_reject=63, no_prev_low_break=56, missing_fvg_or_orderblock=43
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=100823): breakout_not_found=46917, basic_filters_failed=33894, move_not_fresh=14413, breakout_stale=4020, retest_proximity_failed=1343, volume_spike_missing=203, missing_fvg_or_orderblock=17, move_exhausted=14, rsi_reject=2
- **EVAL::WHALE_MOMENTUM** (total=88338): momentum_reject=62162, recent_ticks_insufficient=15825, basic_filters_failed=10351

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=20): execution:overextended=20
- **DIVERGENCE_CONTINUATION** (total=283): setup_compat:regime_VOLATILE_UNSUITABLE=281, setup_compat:regime_BREAKOUT_EXPANSION=2
- **FAILED_AUCTION_RECLAIM** (total=1336): setup_compat:regime_STRONG_TREND=922, execution:overextended=409, setup_compat:regime_VOLATILE_UNSUITABLE=5
- **FUNDING_EXTREME_SIGNAL** (total=927): execution:trigger_not_confirmed=927
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=6021): setup_compat:regime_STRONG_TREND=2713, execution:trigger_not_confirmed=1961, execution:overextended=1347
- **MA_CROSS_TREND_SHIFT** (total=3): execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=7787): setup_compat:regime_STRONG_TREND=4230, setup_compat:regime_WEAK_TREND=2988, execution:overextended=553, entry_quality=16
- **MOVER_AVWAP_SCALP** (total=1692): execution:overextended=927, entry_quality=394, execution:trigger_not_confirmed=371
- **MOVER_TREND_PULLBACK** (total=13477): execution:trigger_not_confirmed=7058, execution:overextended=4527, entry_quality=1892
- **POST_DISPLACEMENT_CONTINUATION** (total=16): execution:overextended=16
- **QUIET_COMPRESSION_BREAK** (total=1): execution:trigger_not_confirmed=1
- **RANGE_FADE** (total=5680): setup_compat:regime_STRONG_TREND=2661, setup_compat:regime_WEAK_TREND=1408, execution:overextended=874, setup_compat:regime_VOLATILE_UNSUITABLE=678, setup_compat:regime_BREAKOUT_EXPANSION=54, context_edge=5
- **TREND_PULLBACK_EMA** (total=2226): setup_compat:regime_CLEAN_RANGE=1413, setup_compat:regime_DIRTY_RANGE=573, entry_quality=162, setup_compat:regime_VOLATILE_UNSUITABLE=78
- **VOLUME_SURGE_BREAKOUT** (total=17): execution:overextended=17

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 169350 | 30.9% |
| TRENDING_UP | 136629 | 24.9% |
| QUIET | 133864 | 24.4% |
| TRENDING_DOWN | 90752 | 16.6% |
| VOLATILE | 17317 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **229**
- Average confidence gap to threshold: **9.48** (samples=229) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: 1000PEPEUSDT=43, TAOUSDT=18, PENGUUSDT=17, PUMPUSDT=16, BTWUSDT=16, AAVEUSDT=14, 1000SHIBUSDT=13, XRPUSDT=11, XLMUSDT=9, ELSAUSDT=8

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 8 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 93 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 14 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 55 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 242 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 64 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 177 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 150 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 8 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 285 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 15 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 114 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 35 |
| MEAN_REVERT | kept | min_confidence_pass | 55 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 359 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 617 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1904 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 56 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4480 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 32 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 47 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 31 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 174 |
| SR_FLIP_RETEST | filtered | min_confidence | 22 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 5 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 39 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 22 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 188 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 48 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 40.70 | 61.00 | 20.30 | 21.03 | 18.00 | 20.00 | 3.00 | 29.00 |
| BREAKDOWN_SHORT | kept | 8 | 76.40 | 65.00 | -11.40 | 17.59 | 17.05 | 20.00 | 4.50 | 3.38 |
| DIVERGENCE_CONTINUATION | filtered | 107 | 57.70 | 65.00 | 7.30 | 22.54 | 19.98 | 17.90 | 0.79 | 9.08 |
| DIVERGENCE_CONTINUATION | kept | 55 | 67.94 | 65.00 | -2.94 | 21.45 | 19.61 | 17.49 | 2.29 | 0.83 |
| FAILED_AUCTION_RECLAIM | filtered | 306 | 48.34 | 63.95 | 15.61 | 21.22 | 19.33 | 20.00 | 2.31 | 18.01 |
| FAILED_AUCTION_RECLAIM | kept | 177 | 71.67 | 65.00 | -6.67 | 21.06 | 19.27 | 20.00 | 2.36 | 1.03 |
| FUNDING_EXTREME_SIGNAL | filtered | 155 | 41.25 | 64.06 | 22.81 | 19.41 | 14.90 | 17.24 | 3.84 | 11.93 |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 65.08 | 65.00 | -0.08 | 20.03 | 13.70 | 17.38 | 3.62 | 2.12 |
| LIQUIDATION_REVERSAL | filtered | 1 | 70.20 | 10.00 | -60.20 | 17.00 | 8.00 | 20.00 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 300 | 50.91 | 64.96 | 14.05 | 21.18 | 18.58 | 17.79 | 1.05 | 17.36 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 114 | 69.89 | 65.00 | -4.89 | 22.08 | 19.08 | 17.59 | 0.73 | 0.49 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 73.70 | 65.00 | -8.70 | 20.60 | 20.00 | 15.80 | 0.00 | 6.80 |
| MEAN_REVERT | filtered | 35 | 57.13 | 65.00 | 7.87 | 20.91 | 14.41 | 18.26 | 0.00 | 18.57 |
| MEAN_REVERT | kept | 55 | 75.05 | 65.00 | -10.05 | 21.25 | 17.40 | 14.70 | 0.00 | 0.36 |
| MOVER_AVWAP_SCALP | filtered | 365 | 56.27 | 64.62 | 8.35 | 19.88 | 15.10 | 15.80 | 3.80 | 20.22 |
| MOVER_AVWAP_SCALP | kept | 617 | 78.65 | 65.00 | -13.65 | 21.33 | 15.96 | 15.80 | 4.40 | 4.33 |
| MOVER_TREND_PULLBACK | filtered | 1960 | 56.15 | 64.02 | 7.87 | 20.00 | 18.63 | 15.80 | 4.07 | 16.91 |
| MOVER_TREND_PULLBACK | kept | 4480 | 76.91 | 65.00 | -11.91 | 20.34 | 18.78 | 15.80 | 4.41 | 1.08 |
| POST_DISPLACEMENT_CONTINUATION | kept | 32 | 77.39 | 65.00 | -12.39 | 20.84 | 19.98 | 16.55 | 4.83 | 7.09 |
| QUIET_COMPRESSION_BREAK | filtered | 78 | 54.45 | 64.69 | 10.24 | 21.31 | 19.54 | 20.00 | 0.00 | 15.30 |
| QUIET_COMPRESSION_BREAK | kept | 174 | 73.31 | 65.00 | -8.31 | 22.11 | 19.69 | 20.00 | 0.00 | 1.64 |
| SR_FLIP_RETEST | filtered | 22 | 60.70 | 63.36 | 2.66 | 19.02 | 20.00 | 15.20 | 2.50 | 11.50 |
| SR_FLIP_RETEST | kept | 5 | 65.66 | 65.00 | -0.66 | 20.36 | 20.00 | 17.16 | 2.20 | 3.54 |
| TREND_PULLBACK_EMA | filtered | 61 | 55.01 | 65.00 | 9.99 | 20.87 | 19.94 | 19.08 | 4.78 | 14.41 |
| TREND_PULLBACK_EMA | kept | 188 | 78.70 | 65.00 | -13.70 | 21.51 | 19.82 | 17.93 | 4.98 | 1.32 |
| VOLUME_SURGE_BREAKOUT | filtered | 48 | 45.63 | 64.50 | 18.87 | 21.13 | 16.76 | 20.00 | 3.53 | 11.39 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 73.80 | 65.00 | -8.80 | 19.64 | 19.06 | 20.00 | 5.21 | 5.61 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 40.70 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 4.70 | 3.00 |
| BREAKDOWN_SHORT | kept | 8 | 76.40 | 18.00 | 17.50 | 14.62 | 14.00 | 3.12 | 8.03 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 107 | 57.70 | 23.13 | 13.42 | 4.49 | 12.36 | 4.97 | 9.29 | 0.79 |
| DIVERGENCE_CONTINUATION | kept | 55 | 67.94 | 20.93 | 10.91 | 5.07 | 14.20 | 6.73 | 9.57 | 2.29 |
| FAILED_AUCTION_RECLAIM | filtered | 306 | 48.34 | 20.57 | 15.37 | 6.32 | 13.16 | 7.25 | 4.72 | 2.31 |
| FAILED_AUCTION_RECLAIM | kept | 177 | 71.67 | 22.15 | 14.43 | 5.68 | 13.38 | 7.29 | 7.51 | 2.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 155 | 41.25 | 24.54 | 9.23 | 4.35 | 12.19 | 7.76 | 5.79 | 3.84 |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 65.08 | 20.00 | 11.75 | 6.38 | 11.62 | 8.88 | 6.82 | 3.62 |
| LIQUIDATION_REVERSAL | filtered | 1 | 70.20 | 25.00 | 8.00 | 15.00 | 8.00 | 2.50 | 5.70 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 300 | 50.91 | 21.93 | 15.31 | 5.33 | 13.17 | 5.60 | 5.89 | 1.05 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 114 | 69.89 | 24.14 | 15.86 | 6.08 | 12.72 | 6.41 | 4.47 | 0.73 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 73.70 | 25.00 | 14.00 | 6.00 | 17.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 35 | 57.13 | 23.86 | 14.57 | 11.57 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 55 | 75.05 | 22.82 | 16.11 | 10.47 | 13.00 | 5.00 | 8.02 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 365 | 56.27 | 18.91 | 18.00 | 13.30 | 13.80 | 6.08 | 6.88 | 3.80 |
| MOVER_AVWAP_SCALP | kept | 617 | 78.65 | 20.02 | 18.00 | 12.74 | 13.82 | 6.75 | 7.29 | 4.40 |
| MOVER_TREND_PULLBACK | filtered | 1960 | 56.15 | 18.23 | 18.05 | 7.84 | 12.00 | 5.84 | 8.53 | 4.07 |
| MOVER_TREND_PULLBACK | kept | 4480 | 76.91 | 19.05 | 18.01 | 7.91 | 13.16 | 6.43 | 9.11 | 4.41 |
| POST_DISPLACEMENT_CONTINUATION | kept | 32 | 77.39 | 16.81 | 18.00 | 15.00 | 14.00 | 6.77 | 9.08 | 4.83 |
| QUIET_COMPRESSION_BREAK | filtered | 78 | 54.45 | 17.82 | 16.41 | 10.69 | 14.12 | 7.94 | 3.53 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 174 | 73.31 | 19.48 | 17.91 | 11.48 | 14.01 | 7.39 | 5.34 | 0.00 |
| SR_FLIP_RETEST | filtered | 22 | 60.70 | 25.00 | 18.00 | 6.00 | 11.00 | 5.00 | 4.70 | 2.50 |
| SR_FLIP_RETEST | kept | 5 | 65.66 | 23.40 | 18.00 | 4.20 | 11.80 | 5.00 | 4.62 | 2.20 |
| TREND_PULLBACK_EMA | filtered | 61 | 55.01 | 14.66 | 18.00 | 7.57 | 14.30 | 7.67 | 8.10 | 4.78 |
| TREND_PULLBACK_EMA | kept | 188 | 78.70 | 18.47 | 18.00 | 7.59 | 14.41 | 8.28 | 9.18 | 4.98 |
| VOLUME_SURGE_BREAKOUT | filtered | 48 | 45.63 | 17.17 | 18.00 | 12.69 | 12.31 | 4.57 | 3.75 | 3.53 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 73.80 | 23.86 | 16.86 | 13.71 | 13.14 | 6.71 | 6.34 | 5.21 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 40.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| BREAKDOWN_SHORT | kept | 8 | 76.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.75 | **0.75** |
| DIVERGENCE_CONTINUATION | filtered | 107 | 57.70 | 0.00 | 0.00 | 2.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.02** |
| DIVERGENCE_CONTINUATION | kept | 55 | 67.94 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.09** |
| FAILED_AUCTION_RECLAIM | filtered | 306 | 48.34 | 0.00 | 0.00 | 1.94 | 0.00 | 0.99 | 0.02 | 0.00 | 0.00 | **2.95** |
| FAILED_AUCTION_RECLAIM | kept | 177 | 71.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 155 | 41.25 | 0.00 | 0.00 | 5.96 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **6.04** |
| FUNDING_EXTREME_SIGNAL | kept | 8 | 65.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 1 | 70.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 300 | 50.91 | 0.00 | 0.00 | 1.37 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **1.59** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 114 | 69.89 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.07** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 73.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 35 | 57.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.43 | 0.00 | 0.00 | **1.43** |
| MEAN_REVERT | kept | 55 | 75.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | **0.36** |
| MOVER_AVWAP_SCALP | filtered | 365 | 56.27 | 0.00 | 0.00 | 3.02 | 0.00 | 1.60 | 0.32 | 0.00 | 0.48 | **5.42** |
| MOVER_AVWAP_SCALP | kept | 617 | 78.65 | 0.04 | 0.00 | 0.40 | 0.00 | 1.57 | 0.07 | 0.00 | 0.29 | **2.37** |
| MOVER_TREND_PULLBACK | filtered | 1960 | 56.15 | 0.72 | 0.00 | 0.91 | 0.00 | 0.53 | 0.02 | 0.00 | 0.00 | **2.18** |
| MOVER_TREND_PULLBACK | kept | 4480 | 76.91 | 0.07 | 0.00 | 0.37 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.55** |
| POST_DISPLACEMENT_CONTINUATION | kept | 32 | 77.39 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 1.12 | 0.00 | 0.00 | **1.35** |
| QUIET_COMPRESSION_BREAK | filtered | 78 | 54.45 | 0.00 | 0.00 | 0.00 | 0.00 | 1.10 | 0.23 | 0.00 | 1.11 | **2.44** |
| QUIET_COMPRESSION_BREAK | kept | 174 | 73.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | **0.25** |
| SR_FLIP_RETEST | filtered | 22 | 60.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 5 | 65.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 61 | 55.01 | 0.00 | 0.00 | 5.80 | 0.00 | 2.48 | 0.00 | 0.00 | 0.00 | **8.28** |
| TREND_PULLBACK_EMA | kept | 188 | 78.70 | 0.00 | 0.00 | 1.41 | 0.00 | 0.34 | 0.00 | 0.00 | 0.00 | **1.75** |
| VOLUME_SURGE_BREAKOUT | filtered | 48 | 45.63 | 0.00 | 0.00 | 5.35 | 0.00 | 0.00 | 0.00 | 0.00 | 1.72 | **7.07** |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 73.80 | 0.00 | 0.00 | 0.69 | 0.00 | 0.00 | 0.00 | 0.00 | 1.54 | **2.23** |

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
- Outcomes recorded: **207226 held of 1042944 seen** across 21 strategies; 4695 cells past the sample floor; **2575 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49632 | 547/49085/0 | 43% | -0.20 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 27052 | 190/26862/0 | 43% | -0.19 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 16855 | 288/16567/0 | 48% | -0.10 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.86R) | LONDON/MARKUP/EXPANDED/BTC_FALLING (-1.19R) |
| FAILED_AUCTION_RECLAIM | 16044 | 220/15824/0 | 37% | -0.30 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.69R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 15181 | 86/15095/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 12491 | 157/12334/0 | 38% | -0.43 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 10012 | 536/9476/0 | 45% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8578 | 0/0/8578 | 42% | -0.12 | OVERLAP/MARKUP/CASCADE/BTC_RISING (+1.58R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.95R) |
| SHADOW_RANGE_FADE | 8135 | 0/0/8135 | 35% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+1.00R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.33R) |
| SR_FLIP_RETEST | 7880 | 31/7849/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| SHADOW_FUNDING_FADE | 7782 | 0/0/7782 | 35% | -0.39 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (-0.01R) | OFF_HOURS/RANGE/NORMAL/BTC_RISING (-0.95R) |
| MEAN_REVERT | 6215 | 83/6132/0 | 37% | -0.31 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.60R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 5048 | 4/5044/0 | 33% | -0.39 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.95R) | LONDON/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.47R) |
| VOLUME_SURGE_BREAKOUT | 4568 | 0/4568/0 | 32% | -0.32 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| WHALE_MOMENTUM | 4500 | 4/4496/0 | 47% | -0.27 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 3525 | 6/3519/0 | 51% | +0.25 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1851 | 0/0/1851 | 52% | -0.08 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.53R) |
| BREAKDOWN_SHORT | 859 | 84/775/0 | 35% | -0.25 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 590 | 0/590/0 | 34% | -0.30 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 268 | 44/224/0 | 45% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 160 | 14/146/0 | 57% | +0.17 | ASIA/MARKUP/NORMAL/BTC_RISING (-0.02R) | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-0.14R) |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 513 | 28% / -0.54R | 513 | 52% / -0.09R | +0.44 | **ATR** |
| TREND_PULLBACK_EMA | 1576 | 39% / -0.37R | 1576 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDATION_REVERSAL | 36 | 28% / -0.55R | 36 | 47% / -0.30R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 2002 | 44% / -0.35R | 2002 | 56% / -0.11R | +0.24 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 261 | 37% / -0.17R | 261 | 49% / -0.03R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 892 | 48% / -0.26R | 892 | 52% / -0.13R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 83 | 48% / -0.13R | 83 | 53% / -0.01R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 9459 | 47% / -0.15R | 9459 | 53% / -0.04R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 491 | 47% / -0.29R | 491 | 49% / -0.19R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 3121 | 47% / -0.12R | 3121 | 53% / -0.03R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1822 | 41% / -0.22R | 1822 | 43% / -0.13R | +0.09 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 28 | 68% / +0.09R | 28 | 68% / +0.00R | -0.09 | **FIXED** |
| BREAKDOWN_SHORT | 65 | 42% / -0.15R | 65 | 46% / -0.08R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 2303 | 47% / -0.12R | 2303 | 52% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 201 | 43% / +0.04R | 201 | 50% / +0.09R | +0.05 | **ATR** |
| MEAN_REVERT | 566 | 45% / -0.19R | 566 | 44% / -0.20R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1791 | 49% / -0.08R | 1791 | 49% / -0.08R | +0.00 | **ATR** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12513 | 27% | -0.21R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 3121 | 51% | -0.02R | 247 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 165 | 48% | -0.04R | 78 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 2012 | 33% / -0.16R | +0.91 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2321 | 40% / -0.15R | +0.86 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3725 | 36% / -0.14R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11526 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2644 | 36% / -0.13R | +0.15 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 176 | 34% / -0.38R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1740 | 37% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1527 | 31% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 390 | 33% / -0.21R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 621 | 31% / -0.28R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 463 | 47% / -0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 113 | 44% / +0.12R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 144 | 45% / -0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 767 | 36% / -0.24R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 131 | 32% / +0.10R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 49 | 41% / -0.36R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 44 | 48% / +0.36R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.51R (bound 0.3) (streak 6/6) (sustained 6 cycles)
- **ALERT** `range_fade_emission` — 357 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3519, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) (sustained 6 cycles)
- **ALERT** `tuned_variants` — 35 non-stamps — atr_arm_uncomputable=35 (seen=253 stamped=36 skipped=182) (streak 6/6) (sustained 6 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1089321 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 21 arms current, none stalled; covering 2031/2031 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 19m ago | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 42 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 6/12) | 6 |
| auto_dispatch | ok | placed=0 rejected=0 skipped=4 over 4 fan-out(s) to a keyed roster; top reasons: venue:coindcx=4 (gaps: skip 4, empty-roster 0; threshold 5) | 0 |
| binance_ip_weight | ok | peak 118/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 61700.00 | 0 |
| candle_coverage | ok | 80/80 symbols with ≥20 15m candles, 80/80 updated within 45m [fresh=80; 75 Tier-1 futures + 5 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 276 dup bars, 0 undedupable; ws 0 out-of-order, 83 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 65 cohorts, 21 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +53 / upstream +34 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1068/1087 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 4 of 100 open dark rows are not being advanced (worst: 2ZUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 6/120) | 6 |
| dark_sar_arms | ok | no open arms; covering 1066/1085 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 330562 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 75 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.51R (bound 0.3) (streak 6/6) | 6 |
| emission_controller | ok | last cycle 4s ago; live_overrides=14 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=364, MOVER_AVWAP_SCALP=323, MOVER_TREND_PULLBACK=4150, RANGE_FADE=722, TREND_PULLBACK_EMA=441), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 442 evaluated, 147 suppressed, 120 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,414 reads/day of 50,000 [engine 1,395, signing 19]; top site keystore.roster_doc at 314/day (engine) | 0 |
| footprint_bars | ok | 2920 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +1 / upstream +1 | 0 |
| geometry_ab | ok | output +10 / upstream +462 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 257 frozen value(s) avoided; 13192 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=6132 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +34 / upstream +462 | 0 |
| mover_admission_metadata | ok | 958 symbols known, 249 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 5 held, 5 with scan counts, 5 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 9 locked / 9 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2258 rows held, 3953118 evicted (sampled: execution:trigger_not_confirmed 286/1379257, execution:overextended 285/1199696, setup_compat:regime_STRONG_TREND 285/696871) | 0 |
| price_action_lane | ok | 29722 evaluated, 30 emitted; layer1 30 stamped / 0 blind; cooldown=4634, delta_opposed=2716, no_footprint=9915, no_sweep=9897, rr_below_floor=2530 | 0 |
| promoted_pair_integrity | ok | 5/5 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 357 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.25R over n=3519, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 6/6) | 6 |
| range_fade_path | ok | output +67 / upstream +462 | 0 |
| sar_alignment_crosscheck | ok | 11/616 disagreed (1.8%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +462 | 0 |
| sar_hold_arm | ok | 1856 held arms settled, 145 unscored, 42 still walking (33 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/64 unfetchable (6%); top cause: located bar does not contain the stamp; symbols: COLLECTUSDT, EVAAUSDT, INITUSDT, LISTAUSDT | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 42 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 6/12) | 6 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 464 records await one (60 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 47.07s, worst 65.68s over 389 lifetime cycles; lifetime 3 over 60s, 0 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.36s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 16064 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 9m ago | 0 |
| snapshot_writer | ok | last cycle 10s ago (40.37s to run, worst 58.98s), 33 overrun(s) of 243 cycles, TTL 900s; slowest trail_governor=10.65s, desk=8.09s, engine_state=4.9s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +1 / upstream +1 | 0 |
| strategy_edge | ok | output +97 / upstream +462 | 0 |
| structural_snap | ok | 6000/6000 measured, 41 blind, 0 levels moved (refusals: redetect_cooldown=117) | 0 |
| structural_veto_lane | ok | 147 stamped; 0 with no readable level book, 0 with clear air ahead, 81 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +462 / upstream +34 | 0 |
| tuned_variants | violating | 35 non-stamps — atr_arm_uncomputable=35 (seen=253 stamped=36 skipped=182) (streak 6/6) | 6 |
| unlock_shorts | ok | 14 open, 49 scheduled, calendar 11.1h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2528415`
- `Path funnel` emissions: `70`
- `Regime distribution` emissions: `70`
- `QUIET_SCALP_BLOCK` events: `229`
- `confidence_gate` events: `9367`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 4 | 4229 | 8178 | 11823 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=386080] state[populated=386080] buckets[many=386080] sources[none] quality[none]
- funding_rate: presence[absent=39695, present=346385] state[empty=39695, populated=346385] buckets[few=346385, none=39695] sources[none] quality[none]
- liquidation_clusters: presence[absent=238816, present=147264] state[empty=238816, populated=147264] buckets[few=116219, none=238816, some=31045] sources[none] quality[none]
- oi_snapshot: presence[absent=39105, present=346975] state[empty=39105, populated=346975] buckets[few=487, many=343788, none=39105, some=2700] sources[none] quality[none]
- order_book: presence[absent=117574, present=268506] state[populated=268506, unavailable=117574] buckets[few=268506, none=117574] sources[book_ticker=268506, unavailable=117574] quality[none=117574, top_of_book_only=268506]
- orderblocks: presence[absent=386080] state[empty=386080] buckets[none=386080] sources[measured_dark=386080] quality[none]
- recent_ticks: presence[present=386080] state[populated=386080] buckets[many=386080] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.762510061264038` sec
- Median create→first breach: `10867.679181814194` sec
- Median create→terminal: `10870.805274963379` sec
- Median first breach→terminal: `8.702278137207031e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 3.8}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.9962913852881752 | 1.0251838644974407 | 0.8961529156521758 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 0.8000000000000016 | 1.127201565557731 | 0.8913710030661399 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.7127465868492722 | 1.8354222016864972 | 0.6498879816364138 | 1 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 1.333525798308052 | 1.3320789695474926 | 1.0010861433846154 | 0 | 0 |
| MOVER_AVWAP_SCALP | 5 | 5 | 1.4960706570195017 | 1.428526762531698 | 1.0619692446402276 | 4 | 1 |
| MOVER_TREND_PULLBACK | 21 | 21 | 2.7192697740112974 | 3.0 | 1.0181775500712538 | 11 | 10 |
| POST_DISPLACEMENT_CONTINUATION | 3 | 3 | 0.8000000000000068 | 0.8631914982988212 | 0.926793187347938 | 0 | 2 |
| QUIET_COMPRESSION_BREAK | 15 | 15 | 1.1371046552949509 | 1.2530419160869344 | 0.8972060714570181 | 0 | 14 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 1.494438260869576 | 1.494438260869576 | 1 | 0 | 0 | 0 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 3 | 1.6890056942619354 | 1.6000000000000032 | 1 | 0 | 0 | 1 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 3.2074063322138695 | 2.8327689885083207 | 0 | 0 | 0 | 1 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 1 | 7.035765601544068 | 1.7508028415183408 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 5 | 1.4960706577456333 | 1.8803962593481747 | 3 | 2 | 1 | 2 | 0 | 0 |
| MOVER_TREND_PULLBACK | 21 | 4.355269003145443 | 3.7314259700642234 | 6 | 3 | 1 | 15 | 0 | 0 |
| POST_DISPLACEMENT_CONTINUATION | 3 | 1.30843869450162 | 1.30843869450162 | 0 | 0 | 0 | 0 | 0 | 3 |
| QUIET_COMPRESSION_BREAK | 15 | 3.2099370232122753 | 1.7492384059320478 | 0 | 0 | 0 | 13 | 1 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.597 | 3555.2951810359955 | 3558.6542150974274 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.2377 | 22500.180109024048 | 22500.180199861526 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 1.9421 | 6191.269033074379 | 6192.212190032005 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3335 | 7260.562597036362 | 7260.562676906586 |
| MOVER_AVWAP_SCALP | 5 | 5 | 80.0 | 20.0 | 80.0 | 0.0 | 1.0969 | 10315.627609014511 | 10316.02661395073 |
| MOVER_TREND_PULLBACK | 21 | 21 | 33.3 | 42.9 | 33.3 | 0.0 | 0.1797 | 8628.533243894577 | 8628.533336877823 |
| POST_DISPLACEMENT_CONTINUATION | 3 | 3 | 100.0 | 0.0 | 100.0 | 0.0 | 1.4701 | 11157.894745111465 | 11159.20186305046 |
| QUIET_COMPRESSION_BREAK | 15 | 15 | 33.3 | 53.3 | 33.3 | 0.0 | 0.1256 | 16550.811986207962 | 16551.07709503174 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 395 | 3 | 153 | 0.0 | 0.0 | None | None | 242 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2803 | 38 | 2255 | 0.0 | 0.0 | None | None | 548 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `438`
- Gating Δ: `61496`
- No-generation Δ: `1813425`
- Fast failures Δ: `-6`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.2592, "current_avg_pnl": -0.597, "current_win_rate": 0.0, "previous_avg_pnl": -0.3378, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.1966, "current_avg_pnl": -0.2377, "current_win_rate": 0.0, "previous_avg_pnl": -1.4343, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 2.1584, "current_avg_pnl": 1.9421, "current_win_rate": 50.0, "previous_avg_pnl": -0.2163, "previous_win_rate": 42.9, "win_rate_delta": 7.1}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.6229, "current_avg_pnl": 1.0969, "current_win_rate": 80.0, "previous_avg_pnl": -0.526, "previous_win_rate": 0.0, "win_rate_delta": 80.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.001, "current_avg_pnl": 0.1797, "current_win_rate": 33.3, "previous_avg_pnl": 0.1807, "previous_win_rate": 35.5, "win_rate_delta": -2.2}, "POST_DISPLACEMENT_CONTINUATION": {"avg_pnl_delta": 1.4701, "current_avg_pnl": 1.4701, "current_win_rate": 100.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 100.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.4603, "current_avg_pnl": 0.1256, "current_win_rate": 33.3, "previous_avg_pnl": 0.5859, "previous_win_rate": 33.3, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 242, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2704.9, "median_terminal_delta_sec": -2704.9, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 38, "geometry_changed_delta": 0, "geometry_preserved_delta": 548, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2328.91, "median_terminal_delta_sec": -2328.91, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
