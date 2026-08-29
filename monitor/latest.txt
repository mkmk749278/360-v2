# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `351` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 167 | 167 | 116 | 5 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12010 | 12010 | 10631 | 16 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 67552 | 67557 | 37 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 59269 | 59282 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 58795 | 55850 | 3409 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 59316 | 58579 | 829 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 59467 | 59293 | 216 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 50681 | 50694 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 59411 | 59448 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 59458 | 57917 | 2089 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 71265 | 76778 | 1022 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 67599 | 61567 | 9625 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 59198 | 59210 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 59290 | 59304 | 9 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 58763 | 58590 | 197 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 60013 | 59368 | 879 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 58461 | 58503 | 210 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 49542 | 47580 | 2232 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 49820 | 49534 | 396 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 67503 | 67530 | 14 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 50698 | 50723 | 20 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3393 | 3393 | 2592 | 17 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 643 | 643 | 164 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 12449 | 12449 | 11969 | 43 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 6 | 6 | 2 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5754 | 5754 | 4358 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2510 | 2510 | 302 | 101 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 25424 | 25424 | 11464 | 563 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 21 | 21 | 17 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1039 | 1039 | 534 | 60 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 2087 | 2087 | 1817 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 813 | 813 | 478 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1837 | 1837 | 1392 | 41 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 51 | 51 | 16 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1383 | 1383 | 71 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=67557): breakout_not_found=36116, basic_filters_failed=20601, move_not_fresh=6524, breakout_stale=2884, retest_proximity_failed=1136, volume_spike_missing=224, insufficient_candles=54, move_exhausted=16, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=59282): cls_disabled_merged_into_lsr=59282
- **EVAL::DIVERGENCE_CONTINUATION** (total=55850): cvd_divergence_failed=21794, basic_filters_failed=16587, h1_trend_not_aligned=10613, ema_alignment_reject=6085, retest_proximity_failed=510, missing_fvg_or_orderblock=257, regime_blocked=4
- **EVAL::FAILED_AUCTION_RECLAIM** (total=58579): auction_not_detected=35774, basic_filters_failed=16051, reclaim_hold_failed=2476, tail_too_small=2140, regime_blocked=1788, rsi_reject=350
- **EVAL::FUNDING_EXTREME** (total=59293): funding_not_extreme=39942, basic_filters_failed=16665, ema_alignment_reject=1257, missing_funding_rate=802, rsi_reject=274, momentum_reject=174, cvd_divergence_failed=153, missing_fvg_or_orderblock=20, insufficient_candles=6
- **EVAL::LIQUIDATION_REVERSAL** (total=50694): cascade_threshold_not_met=33362, basic_filters_failed=16649, cvd_divergence_failed=423, rsi_reject=199, insufficient_candles=44, missing_fvg_or_orderblock=11, volume_spike_missing=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=59448): no_ma_cross=41923, basic_filters_failed=16614, ma_cross_htf_misaligned=653, ma_cross_cooldown=244, ma_cross_htf_unconfirmed=14
- **EVAL::MEAN_REVERT** (total=57917): no_extension=43454, basic_filters_failed=14455, insufficient_candles=8
- **EVAL::MOVER_AVWAP_SCALP** (total=76778): no_avwap_tag=29625, basic_filters_failed=20896, no_mover_leg=12444, avwap_slope_against=9708, avwap_reclaim_no_volume=2193, no_avwap_reclaim=1746, insufficient_candles=109, anchor_too_recent=57
- **EVAL::MOVER_TREND_PULLBACK** (total=61567): mover_run_too_small=25197, basic_filters_failed=20752, no_reclaim=13706, no_pullback_tag=1803, insufficient_candles=109
- **EVAL::OPENING_RANGE_BREAKOUT** (total=59210): feature_disabled=59210
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=59304): regime_blocked=38513, breakout_not_found=13560, basic_filters_failed=4428, adx_reject=2735, ema_alignment_reject=68
- **EVAL::QUIET_COMPRESSION_BREAK** (total=58590): regime_blocked=22422, compression_not_detected=17930, basic_filters_failed=11604, breakout_not_detected=6004, volume_confirmation_failed=546, rsi_reject=84
- **EVAL::RANGE_FADE** (total=59368): no_range_edge=44898, basic_filters_failed=14462, insufficient_candles=8
- **EVAL::SR_FLIP_RETEST** (total=58503): flip_close_not_confirmed=36486, basic_filters_failed=16012, regime_blocked=1772, h1_break_not_confirmed=1446, retest_out_of_zone=1267, long_break_volume_thin=884, reclaim_hold_failed=442, ema_alignment_reject=61, wick_quality_failed=53, whipsaw_flip=45, missing_fvg_or_orderblock=16, long_acceptance_not_held=11, insufficient_candles=8
- **EVAL::STANDARD** (total=47580): momentum_reject=12734, basic_filters_failed=11357, adx_reject=10822, sweeps_not_detected=5235, macd_reject=3985, ema_alignment_reject=2599, htf_poi_unanchored=768, rsi_reject=44, invalid_sl_geometry=30, insufficient_candles=6
- **EVAL::TREND_PULLBACK** (total=49534): h1_trend_not_aligned=13813, h1_pullback_not_confirmed=8965, basic_filters_failed=8092, ema_alignment_reject=8026, ema_not_tested_prev=3294, no_ema_reclaim_close=3007, body_conviction_fail=1505, rsi_reject=1443, prev_already_below_emas=568, no_prev_low_break=371, prev_already_above_emas=194, momentum_flat=124, no_prev_high_break=64, ema21_not_tagged=32, missing_fvg_or_orderblock=16, momentum_reject=12, insufficient_candles=6, regime_blocked=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=67530): breakout_not_found=37677, basic_filters_failed=20597, move_not_fresh=5937, breakout_stale=2440, retest_proximity_failed=661, volume_spike_missing=126, insufficient_candles=54, missing_fvg_or_orderblock=33, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=50723): momentum_reject=34408, recent_ticks_insufficient=10508, basic_filters_failed=5807

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=9): execution:overextended=9
- **DIVERGENCE_CONTINUATION** (total=280): setup_compat:regime_VOLATILE_UNSUITABLE=254, setup_compat:regime_BREAKOUT_EXPANSION=25, execution:overextended=1
- **FAILED_AUCTION_RECLAIM** (total=1113): execution:overextended=629, setup_compat:regime_STRONG_TREND=408, context_floor=62, setup_compat:regime_VOLATILE_UNSUITABLE=14
- **FUNDING_EXTREME_SIGNAL** (total=471): execution:trigger_not_confirmed=468, context_floor=3
- **LIQUIDATION_REVERSAL** (total=7): execution:trigger_not_confirmed=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=3653): execution:trigger_not_confirmed=1409, execution:overextended=1317, setup_compat:regime_STRONG_TREND=927
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_DIRTY_RANGE=4, execution:overextended=2, setup_compat:regime_CLEAN_RANGE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=3663): setup_compat:regime_WEAK_TREND=1798, setup_compat:regime_STRONG_TREND=1479, execution:overextended=377, entry_quality=9
- **MOVER_AVWAP_SCALP** (total=1256): execution:overextended=1023, execution:trigger_not_confirmed=143, entry_quality=90
- **MOVER_TREND_PULLBACK** (total=11914): execution:trigger_not_confirmed=6364, execution:overextended=4143, entry_quality=1407
- **QUIET_COMPRESSION_BREAK** (total=28): execution:trigger_not_confirmed=28
- **RANGE_FADE** (total=1298): setup_compat:regime_WEAK_TREND=607, setup_compat:regime_STRONG_TREND=527, setup_compat:regime_VOLATILE_UNSUITABLE=82, execution:overextended=75, context_edge=7
- **TREND_PULLBACK_EMA** (total=1578): setup_compat:regime_CLEAN_RANGE=926, setup_compat:regime_DIRTY_RANGE=562, setup_compat:regime_VOLATILE_UNSUITABLE=59, entry_quality=31
- **VOLUME_SURGE_BREAKOUT** (total=6): execution:overextended=6
- **WHALE_MOMENTUM** (total=1122): execution:trigger_not_confirmed=1109, context_floor=13

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 141159 | 39.7% |
| QUIET | 79241 | 22.3% |
| TRENDING_DOWN | 71118 | 20.0% |
| TRENDING_UP | 50271 | 14.1% |
| VOLATILE | 14003 | 3.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **291**
- Average confidence gap to threshold: **10.29** (samples=291) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BCHUSDT=41, BTCUSDT=30, OPUSDT=29, SUIUSDT=21, 1000PEPEUSDT=19, AAVEUSDT=16, XRPUSDT=16, LTCUSDT=12, KMNOUSDT=12, XMRUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 1 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 25 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 194 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 17 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 270 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 215 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 12 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 115 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 13 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 8 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 221 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 79 |
| MEAN_REVERT | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 218 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 27 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 5 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1215 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 537 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 108 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5751 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 4 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 73 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 20 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 327 |
| SR_FLIP_RETEST | filtered | min_confidence | 28 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 100 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 54 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 216 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 22 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 13 |
| WHALE_MOMENTUM | filtered | min_confidence | 74 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 29 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 59.30 | 61.00 | 1.70 | 18.50 | 20.00 | 20.00 | 4.00 | 13.00 |
| BREAKDOWN_SHORT | kept | 25 | 74.81 | 65.00 | -9.81 | 19.42 | 18.53 | 20.00 | 4.36 | 1.94 |
| DIVERGENCE_CONTINUATION | filtered | 211 | 59.28 | 64.91 | 5.63 | 20.70 | 19.87 | 18.07 | 1.29 | 8.84 |
| DIVERGENCE_CONTINUATION | kept | 270 | 70.42 | 65.00 | -5.42 | 20.15 | 19.91 | 18.69 | 2.34 | 0.68 |
| FAILED_AUCTION_RECLAIM | filtered | 227 | 53.21 | 64.82 | 11.61 | 20.45 | 18.91 | 20.00 | 2.09 | 4.41 |
| FAILED_AUCTION_RECLAIM | kept | 115 | 73.55 | 65.00 | -8.55 | 20.35 | 18.68 | 20.00 | 3.63 | -0.75 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 43.67 | 63.25 | 19.58 | 21.10 | 15.76 | 17.00 | 2.38 | 8.03 |
| LIQUIDATION_REVERSAL | filtered | 5 | 60.32 | 10.00 | -50.32 | 21.32 | 8.00 | 18.64 | 4.80 | 5.28 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 56.36 | 65.00 | 8.64 | 20.78 | 18.37 | 17.50 | 2.17 | 17.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 221 | 70.46 | 65.00 | -5.46 | 21.23 | 19.33 | 17.67 | 1.86 | 0.19 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 73.25 | 65.00 | -8.25 | 22.85 | 16.90 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 79 | 60.15 | 64.49 | 4.34 | 20.50 | 14.66 | 15.89 | 0.00 | 10.66 |
| MEAN_REVERT | kept | 2 | 68.35 | 65.00 | -3.35 | 20.70 | 14.55 | 14.95 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 250 | 60.03 | 63.90 | 3.87 | 19.83 | 15.84 | 15.80 | 4.05 | 11.00 |
| MOVER_AVWAP_SCALP | kept | 1215 | 85.11 | 65.00 | -20.11 | 20.64 | 16.53 | 15.80 | 4.35 | 0.96 |
| MOVER_TREND_PULLBACK | filtered | 645 | 56.13 | 64.64 | 8.51 | 20.41 | 18.45 | 15.80 | 3.55 | 16.93 |
| MOVER_TREND_PULLBACK | kept | 5751 | 76.44 | 65.00 | -11.44 | 20.03 | 18.73 | 15.80 | 4.14 | 0.80 |
| POST_DISPLACEMENT_CONTINUATION | kept | 4 | 62.50 | 65.00 | 2.50 | 21.20 | 20.00 | 17.20 | 4.50 | 7.00 |
| QUIET_COMPRESSION_BREAK | filtered | 93 | 56.34 | 65.00 | 8.66 | 21.91 | 19.63 | 20.00 | 0.00 | 6.66 |
| QUIET_COMPRESSION_BREAK | kept | 327 | 75.72 | 65.00 | -10.72 | 21.65 | 19.61 | 20.00 | 0.00 | -0.97 |
| SR_FLIP_RETEST | filtered | 32 | 61.62 | 65.00 | 3.38 | 21.79 | 20.00 | 15.66 | 1.34 | 3.94 |
| SR_FLIP_RETEST | kept | 100 | 69.94 | 65.00 | -4.94 | 20.54 | 20.00 | 16.92 | 2.06 | 0.69 |
| TREND_PULLBACK_EMA | filtered | 64 | 59.10 | 64.56 | 5.46 | 20.08 | 19.43 | 16.76 | 4.56 | 13.23 |
| TREND_PULLBACK_EMA | kept | 216 | 78.39 | 65.00 | -13.39 | 20.62 | 19.84 | 19.39 | 4.97 | -1.04 |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 55.04 | 63.91 | 8.87 | 20.07 | 17.37 | 20.00 | 3.55 | 8.45 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 78.92 | 65.00 | -13.92 | 20.96 | 18.68 | 20.00 | 4.58 | 1.85 |
| WHALE_MOMENTUM | filtered | 103 | 55.95 | 64.57 | 8.62 | 23.73 | 15.30 | 17.00 | 0.00 | 12.26 |
| WHALE_MOMENTUM | kept | 2 | 64.85 | 65.00 | 0.15 | 22.75 | 17.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 59.30 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 6.30 | 4.00 |
| BREAKDOWN_SHORT | kept | 25 | 74.81 | 18.28 | 15.28 | 12.60 | 13.52 | 5.00 | 7.72 | 4.36 |
| DIVERGENCE_CONTINUATION | filtered | 211 | 59.28 | 22.88 | 13.97 | 5.06 | 12.26 | 4.96 | 7.91 | 1.29 |
| DIVERGENCE_CONTINUATION | kept | 270 | 70.42 | 22.48 | 17.01 | 4.31 | 12.61 | 5.02 | 8.60 | 2.34 |
| FAILED_AUCTION_RECLAIM | filtered | 227 | 53.21 | 20.31 | 16.84 | 6.99 | 13.50 | 6.61 | 4.75 | 2.09 |
| FAILED_AUCTION_RECLAIM | kept | 115 | 73.55 | 23.96 | 15.98 | 4.46 | 13.74 | 5.34 | 6.92 | 3.63 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 43.67 | 25.00 | 8.00 | 5.44 | 15.00 | 6.62 | 4.26 | 2.38 |
| LIQUIDATION_REVERSAL | filtered | 5 | 60.32 | 25.00 | 8.00 | 13.80 | 8.00 | 3.50 | 2.50 | 4.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 56.36 | 22.33 | 15.00 | 8.25 | 11.50 | 7.12 | 6.98 | 2.17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 221 | 70.46 | 22.79 | 15.52 | 4.63 | 12.59 | 5.64 | 7.67 | 1.86 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 73.25 | 17.00 | 14.00 | 9.00 | 15.50 | 8.75 | 9.00 | 0.00 |
| MEAN_REVERT | filtered | 79 | 60.15 | 16.57 | 16.89 | 11.66 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 2 | 68.35 | 24.00 | 14.00 | 9.00 | 12.50 | 5.00 | 3.85 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 250 | 60.03 | 19.01 | 18.13 | 10.57 | 14.20 | 5.27 | 6.96 | 4.05 |
| MOVER_AVWAP_SCALP | kept | 1215 | 85.11 | 21.14 | 18.04 | 12.96 | 14.00 | 6.93 | 8.86 | 4.35 |
| MOVER_TREND_PULLBACK | filtered | 645 | 56.13 | 18.78 | 18.00 | 7.83 | 12.60 | 5.81 | 9.00 | 3.55 |
| MOVER_TREND_PULLBACK | kept | 5751 | 76.44 | 19.25 | 18.01 | 7.74 | 12.54 | 6.41 | 9.23 | 4.14 |
| POST_DISPLACEMENT_CONTINUATION | kept | 4 | 62.50 | 0.00 | 18.00 | 15.00 | 14.00 | 10.00 | 8.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 93 | 56.34 | 19.06 | 17.14 | 11.68 | 14.00 | 7.15 | 3.96 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 327 | 75.72 | 18.74 | 17.72 | 11.01 | 14.15 | 6.40 | 8.49 | 0.00 |
| SR_FLIP_RETEST | filtered | 32 | 61.62 | 17.00 | 16.75 | 4.12 | 14.00 | 5.44 | 6.90 | 1.34 |
| SR_FLIP_RETEST | kept | 100 | 69.94 | 21.40 | 15.30 | 3.66 | 14.09 | 5.49 | 8.67 | 2.06 |
| TREND_PULLBACK_EMA | filtered | 64 | 59.10 | 13.75 | 18.00 | 7.66 | 14.80 | 7.93 | 8.67 | 4.56 |
| TREND_PULLBACK_EMA | kept | 216 | 78.39 | 18.36 | 18.00 | 7.51 | 13.96 | 6.91 | 8.99 | 4.97 |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 55.04 | 17.00 | 16.18 | 12.00 | 14.82 | 5.00 | 5.85 | 3.55 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 78.92 | 17.62 | 17.85 | 12.23 | 14.00 | 5.00 | 9.49 | 4.58 |
| WHALE_MOMENTUM | filtered | 103 | 55.95 | 21.82 | 14.89 | 5.68 | 13.27 | 6.30 | 6.26 | 0.00 |
| WHALE_MOMENTUM | kept | 2 | 64.85 | 25.00 | 18.00 | 3.00 | 13.50 | 9.50 | 5.85 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 59.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 10.00 | 0.00 | 0.00 | **10.00** |
| BREAKDOWN_SHORT | kept | 25 | 74.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.14 | **0.14** |
| DIVERGENCE_CONTINUATION | filtered | 211 | 59.28 | 0.00 | 0.00 | 1.70 | 0.00 | 1.29 | 0.00 | 0.00 | 0.00 | **2.99** |
| DIVERGENCE_CONTINUATION | kept | 270 | 70.42 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.67** |
| FAILED_AUCTION_RECLAIM | filtered | 227 | 53.21 | 0.00 | 0.00 | 1.56 | 0.00 | 0.85 | 0.10 | 0.00 | 0.00 | **2.51** |
| FAILED_AUCTION_RECLAIM | kept | 115 | 73.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | **0.09** |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 43.67 | 0.00 | 0.00 | 5.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.90** |
| LIQUIDATION_REVERSAL | filtered | 5 | 60.32 | 0.00 | 0.00 | 0.00 | 0.00 | 5.28 | 0.00 | 0.00 | 0.00 | **5.28** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 56.36 | 0.00 | 0.00 | 4.67 | 0.00 | 9.00 | 0.00 | 0.00 | 0.00 | **13.67** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 221 | 70.46 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | **0.23** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 73.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 79 | 60.15 | 0.00 | 0.00 | 0.00 | 0.00 | 10.66 | 0.00 | 0.00 | 0.00 | **10.66** |
| MEAN_REVERT | kept | 2 | 68.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 250 | 60.03 | 0.12 | 0.00 | 2.31 | 0.00 | 6.76 | 0.00 | 0.00 | 0.25 | **9.44** |
| MOVER_AVWAP_SCALP | kept | 1215 | 85.11 | 0.03 | 0.00 | 0.20 | 0.00 | 0.28 | 0.09 | 0.00 | 0.20 | **0.80** |
| MOVER_TREND_PULLBACK | filtered | 645 | 56.13 | 1.44 | 0.00 | 2.33 | 0.00 | 2.63 | 0.54 | 0.00 | 0.00 | **6.94** |
| MOVER_TREND_PULLBACK | kept | 5751 | 76.44 | 0.03 | 0.00 | 0.62 | 0.00 | 0.11 | 0.05 | 0.00 | 0.01 | **0.82** |
| POST_DISPLACEMENT_CONTINUATION | kept | 4 | 62.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 93 | 56.34 | 0.00 | 0.00 | 0.31 | 0.00 | 0.92 | 0.49 | 0.00 | 3.38 | **5.10** |
| QUIET_COMPRESSION_BREAK | kept | 327 | 75.72 | 0.00 | 0.00 | 0.41 | 0.00 | 0.32 | 0.14 | 0.00 | 0.08 | **0.95** |
| SR_FLIP_RETEST | filtered | 32 | 61.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 100 | 69.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 64 | 59.10 | 0.00 | 0.00 | 1.50 | 0.00 | 3.37 | 0.16 | 0.00 | 0.00 | **5.03** |
| TREND_PULLBACK_EMA | kept | 216 | 78.39 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | **0.34** |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 55.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 78.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 103 | 55.95 | 0.00 | 0.00 | 0.00 | 0.00 | 1.47 | 0.41 | 0.00 | 0.00 | **1.88** |
| WHALE_MOMENTUM | kept | 2 | 64.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **54735 held of 118937 seen** across 21 strategies; 1219 cells past the sample floor; **499 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 25852 | 127/25725/0 | 44% | -0.17 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.19R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.24R) |
| MOVER_AVWAP_SCALP | 6411 | 22/6389/0 | 43% | -0.24 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 4336 | 20/4316/0 | 38% | -0.25 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| DIVERGENCE_CONTINUATION | 2825 | 4/2821/0 | 50% | -0.05 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.05R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 2638 | 0/0/2638 | 42% | -0.10 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.49R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-0.90R) |
| TREND_PULLBACK_EMA | 2638 | 2/2636/0 | 42% | -0.22 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+0.72R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.31R) |
| SHADOW_RANGE_FADE | 2204 | 0/0/2204 | 36% | -0.07 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+0.32R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.88R) |
| QUIET_COMPRESSION_BREAK | 1790 | 33/1757/0 | 38% | -0.19 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.20R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 1478 | 0/0/1478 | 38% | -0.35 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | ASIA/MARKUP/NORMAL/BTC_RISING (-0.91R) |
| WHALE_MOMENTUM | 1422 | 0/1422/0 | 40% | -0.37 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| FUNDING_EXTREME_SIGNAL | 640 | 0/640/0 | 27% | -0.55 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| LIQUIDITY_SWEEP_REVERSAL | 580 | 6/574/0 | 44% | -0.18 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-0.06R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-0.45R) |
| MEAN_REVERT | 570 | 2/568/0 | 81% | +0.64 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| VOLUME_SURGE_BREAKOUT | 552 | 0/552/0 | 51% | +0.02 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SHADOW_CASCADE_REVERSAL | 269 | 0/0/269 | 56% | -0.03 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.22R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.32R) |
| SR_FLIP_RETEST | 226 | 0/226/0 | 65% | -0.08 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.72R) | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.25R) |
| BREAKDOWN_SHORT | 170 | 8/162/0 | 20% | -0.59 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 68 | 0/68/0 | 26% | -0.66 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 34 | 0/34/0 | 6% | -1.06 | — | — |
| MA_CROSS_TREND_SHIFT | 30 | 0/30/0 | 40% | -0.08 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 2 | 0/2/0 | 100% | +0.56 | — | — |

- **Strongest cells**: `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING` +1.44R (n=23, STRONG); `FAILED_AUCTION_RECLAIM @ NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +1.42R (n=34, STRONG)
- **Weakest cells**: `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.31R (n=50, NEGATIVE); `TREND_PULLBACK_EMA @ ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.24R (n=17, NEGATIVE); `MOVER_TREND_PULLBACK @ OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.24R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 58 | 28% / -0.55R | 58 | 47% / -0.15R | +0.40 | **ATR** |
| TREND_PULLBACK_EMA | 217 | 47% / -0.16R | 217 | 55% / -0.04R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 293 | 44% / -0.18R | 293 | 45% / -0.09R | +0.09 | **ATR** |
| WHALE_MOMENTUM | 161 | 41% / -0.34R | 161 | 42% / -0.26R | +0.09 | **ATR** |
| MEAN_REVERT | 43 | 60% / +0.17R | 43 | 60% / +0.25R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 3779 | 53% / -0.06R | 3779 | 57% / +0.01R | +0.07 | **ATR** |
| MOVER_AVWAP_SCALP | 479 | 49% / -0.13R | 479 | 53% / -0.06R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 139 | 50% / -0.15R | 139 | 53% / -0.10R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 37 | 51% / +0.10R | 37 | 54% / +0.06R | -0.04 | **FIXED** |
| SR_FLIP_RETEST | 31 | 52% / -0.26R | 31 | 52% / -0.23R | +0.02 | **ATR** |
| DIVERGENCE_CONTINUATION | 263 | 50% / -0.06R | 263 | 56% / -0.05R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 253 | 38% / -0.24R | 253 | 38% / -0.25R | -0.01 | **FIXED** |
| RANGE_FADE | 7 | 43% / -0.03R | 7 | 43% / -0.15R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 10 | 30% / -0.23R | 10 | 30% / -0.17R | — | **MEASURING** |
| BREAKDOWN_SHORT | 14 | 29% / -0.15R | 14 | 29% / -0.09R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 100% / +0.56R | 1 | 100% / +0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 4 | 25% / -0.64R | 4 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 5648 | 32% | -0.17R | 251 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 479 | 51% | -0.06R | 123 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 26 | 62% | +0.09R | 25 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 63 | 33% / -0.17R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 248 | 38% / +0.13R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4675 | 38% / -0.10R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 556 | 38% / +0.13R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 218 | 39% / -0.00R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 285 | 39% / +0.15R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 284 | 38% / -0.16R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 143 | 48% / -0.14R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 57 | 33% / -0.25R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 61 | 28% / -0.63R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 38 | 61% / +0.21R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 28 | 43% / -0.08R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 7 | 43% / -0.20R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 30 | 30% / -0.32R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 12 | 17% / -0.62R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 5 | 20% / -1.53R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 1 | 100% / +1.90R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 52 · alerting: **0** · boot grace active: True

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 136627 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 31 arms current, none stalled; covering 335/335 signals (100%) | 0 |
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77412.70 | 0 |
| candle_coverage | ok | 77/78 symbols with ≥20 15m candles, 60/78 updated within 45m [short=1, stale=17, fresh=60; 75 Tier-1 futures + 3 promoted movers monitored]; 18 Tier-1 CORE pair(s) unusable (e.g. AAVEUSDT, ADAUSDT, AVAXUSDT, BTCUSDT, BTWUSDT) | 0 |
| candle_series_integrity | ok | merge dropped 356 dup bars, 0 undedupable; ws 0 out-of-order, 75 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 30 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 30 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +60 / upstream +37 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1293/1308 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | boot grace (7 of 119 open dark rows are not being advanced (worst: HEIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 1/120)) | 0 |
| dark_sar_arms | ok | no open arms; covering 1292/1307 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 49666 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | boot grace (FAILED_AUCTION_RECLAIM realized−counterfactual=+0.77R (bound 0.3) (streak 1/6)) | 0 |
| emission_controller | ok | last cycle 333s ago; live_overrides=28 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=16 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4368 stamps (MEAN_REVERT=938, MOVER_AVWAP_SCALP=189, MOVER_TREND_PULLBACK=2704, RANGE_FADE=309, TREND_PULLBACK_EMA=228), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | boot grace (entry-quality gate is over its blast-radius cap (70/73 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 1/6)) | 0 |
| footprint_bars | ok | 440 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +237 | 0 |
| indicator_cache_key | ok | 129 frozen value(s) avoided; 4014 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | backlog 31 detections since last emission | 0 |
| mean_revert_path | ok | output +31 / upstream +237 | 0 |
| mover_admission_metadata | ok | 882 symbols known, 180 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 3 held, 3 with scan counts, 3 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3114 rows held, 860709 evicted (sampled: execution:trigger_not_confirmed 400/316863, execution:overextended 400/302879, setup_compat:regime_STRONG_TREND 400/111452) | 0 |
| price_action_lane | ok | 5860 evaluated, 7 emitted; layer1 7 stamped / 0 blind; cooldown=707, delta_opposed=711, no_footprint=2012, no_sweep=1853, rr_below_floor=570 | 0 |
| promoted_pair_integrity | ok | 3/3 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 43 detections since last progress | 0 |
| range_fade_path | ok | output +43 / upstream +237 | 0 |
| sar_alignment_crosscheck | ok | boot grace (13/155 disagreed (8.4%) (streak 1/6)) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +237 | 0 |
| sar_hold_arm | ok | 554 held arms settled, 104 unscored, 30 still walking (27 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 4/78 unfetchable (5%); top cause: gap or duplicate bar in the 15m window; symbols: HBARUSDT | 0 |
| sar_live_arms | ok | 31 arms current, none stalled; covering 344/344 signals (100%) | 0 |
| sar_refresh_budget | ok | boot grace (12 due symbols turned away by the per-cycle cap (40); 94 symbols await a verdict. Their records cannot resolve — raise SAR_EXIT_SHADOW_CANDLE_REFRESH_MAX_PER_CYCLE. (streak 1/6)) | 0 |
| sar_resolution_progress | ok | 2 resolved, 72 still mid-window | 0 |
| scan_cycle | ok | last 18.21s, worst 41.79s over 77 lifetime cycles; lifetime 0 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 7.08s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 1717 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 7s ago (3.99s to run, worst 13.18s), 0 overrun(s) of 43 cycles, TTL 900s; slowest signals=0.87s, tickers=0.71s, engine_state=0.69s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +85 / upstream +237 | 0 |
| structural_snap | ok | 4381/4381 measured, 13 blind, 0 levels moved (refusals: redetect_cooldown=24) | 0 |
| structural_veto_lane | ok | 29 stamped; 0 with no readable level book, 0 with clear air ahead, 6 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +237 / upstream +37 | 0 |
| tuned_variants | ok | boot grace (23 non-stamps — atr_arm_uncomputable=23 (seen=72 stamped=4 skipped=45) (streak 1/6)) | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1762206`
- `Path funnel` emissions: `41`
- `Regime distribution` emissions: `41`
- `QUIET_SCALP_BLOCK` events: `291`
- `confidence_gate` events: `10023`
- `free_channel_post` events: `38`
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
| futures_aggtrade | 2 | 11506 | 11506 | 14156 | 0 |
| futures_depth | 2 | 3741 | 3741 | 10857 | 0 |
| futures_liq | 5 | 6393 | 6514 | 13386 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **38**

| Source | Count |
|---|---:|
| signal_close | 34 |
| regime_shift | 2 |
| signal_highlight | 2 |

- By severity: HIGH=38

## Dependency readiness
- cvd: presence[present=285673] state[populated=285673] buckets[few=8, many=285525, some=140] sources[none] quality[none]
- funding_rate: presence[absent=36321, present=249352] state[empty=36321, populated=249352] buckets[few=249352, none=36321] sources[none] quality[none]
- liquidation_clusters: presence[absent=183513, present=102160] state[empty=183513, populated=102160] buckets[few=81527, none=183513, some=20633] sources[none] quality[none]
- oi_snapshot: presence[absent=35625, present=250048] state[empty=35625, populated=250048] buckets[few=228, many=248510, none=35625, some=1310] sources[none] quality[none]
- order_book: presence[absent=100660, present=185013] state[populated=185013, unavailable=100660] buckets[few=185013, none=100660] sources[book_ticker=185013, unavailable=100660] quality[none=100660, top_of_book_only=185013]
- orderblocks: presence[absent=285673] state[empty=285673] buckets[none=285673] sources[measured_dark=285641, not_implemented=32] quality[none]
- recent_ticks: presence[present=285673] state[populated=285673] buckets[many=285673] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `14.50803005695343` sec
- Median create→first breach: `4447.796108484268` sec
- Median create→terminal: `4448.610790967941` sec
- Median first breach→terminal: `7.208625435829163` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.8000000000000038 | 1.3624575373488685 | 0.5871742627345876 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.0489850322574537 | 1.1753580345139787 | 0.892481270773989 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 1.5961187388556781 | 2.374917428861787 | 0.7082109296259785 | 0 | 2 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.353367322546091 | 2.799641913929782 | 0.8650790684002447 | 1 | 2 |
| MOVER_TREND_PULLBACK | 21 | 21 | 4.053227399953116 | 3.0 | 1.3510757999843719 | 19 | 2 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.0361225655799662 | 1.0361225654018096 | 0.9267746850692656 | 0 | 3 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.8549524145223837 | 2.016769638128863 | 0.9197641512708354 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2277.512948989868 | 2281.8357179164886 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.5735 | 1732.6651339530945 | 1738.3870768547058 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.7398 | 7187.171722531319 | 7188.096830487251 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | 0.513 | 43834.732453107834 | 43841.74997806549 |
| MOVER_TREND_PULLBACK | 21 | 21 | 0.0 | 23.8 | 0.0 | 0.0 | 1.8929 | 2126.4144871234894 | 2129.1995100975037 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 60.0 | 20.0 | 60.0 | 0.0 | 1.2931 | 40782.33577108383 | 40784.02781510353 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.7824 | 4943.169278860092 | 4975.347000837326 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 813 | 7 | 478 | 0.0 | 0.0 | None | None | 335 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1837 | 41 | 1392 | 100.0 | 0.0 | 4943.169278860092 | 4975.347000837326 | 445 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `332`
- Gating Δ: `-12192`
- No-generation Δ: `-262680`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.3411, "current_avg_pnl": 0.513, "current_win_rate": 0.0, "previous_avg_pnl": -0.8281, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.7133, "current_avg_pnl": 1.8929, "current_win_rate": 0.0, "previous_avg_pnl": 0.1796, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.2931, "current_avg_pnl": 1.2931, "current_win_rate": 60.0, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 60.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 222, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 118, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 4943.17, "median_terminal_delta_sec": 4975.35, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
