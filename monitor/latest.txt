# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `8` sec (warning=False)
- Latest performance record age: `3306` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 50 | 50 | 32 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 7182 | 7182 | 6594 | 19 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 52856 | 52878 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 50030 | 50043 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 49625 | 48022 | 1997 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50087 | 49851 | 297 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 50323 | 50198 | 157 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 44466 | 44488 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50153 | 50190 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 50203 | 48846 | 2052 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 55871 | 59017 | 414 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 52891 | 49010 | 6814 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 50128 | 50135 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50052 | 50078 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 49571 | 49431 | 194 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 50904 | 50021 | 1352 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 49348 | 49496 | 30 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 43607 | 42729 | 1015 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 43750 | 43518 | 315 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 52808 | 52848 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 44497 | 44485 | 76 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1178 | 1178 | 962 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 513 | 513 | 149 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 15 | 15 | 15 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4568 | 4568 | 4439 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 2 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5307 | 5307 | 3952 | 18 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1050 | 1050 | 285 | 35 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 19174 | 19174 | 12332 | 272 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1213 | 1213 | 739 | 44 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 3623 | 3623 | 3175 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 178 | 178 | 108 | 3 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1159 | 1159 | 873 | 30 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 49 | 49 | 21 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2282 | 2282 | 68 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=52878): breakout_not_found=28232, basic_filters_failed=15967, move_not_fresh=5707, breakout_stale=2231, retest_proximity_failed=611, volume_spike_missing=107, ema_alignment_reject=12, missing_fvg_or_orderblock=6, move_exhausted=5
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=50044): cls_disabled_merged_into_lsr=50044
- **EVAL::DIVERGENCE_CONTINUATION** (total=48023): cvd_divergence_failed=18521, basic_filters_failed=13999, h1_trend_not_aligned=10860, ema_alignment_reject=3787, retest_proximity_failed=561, missing_fvg_or_orderblock=295
- **EVAL::FAILED_AUCTION_RECLAIM** (total=49852): auction_not_detected=32106, basic_filters_failed=13772, regime_blocked=1744, reclaim_hold_failed=1400, tail_too_small=795, rsi_reject=35
- **EVAL::FUNDING_EXTREME** (total=50199): funding_not_extreme=32472, basic_filters_failed=13805, missing_funding_rate=1721, ema_alignment_reject=1139, rsi_reject=803, cvd_divergence_failed=131, momentum_reject=114, missing_fvg_or_orderblock=14
- **EVAL::LIQUIDATION_REVERSAL** (total=44488): cascade_threshold_not_met=29920, basic_filters_failed=14121, cvd_divergence_failed=229, rsi_reject=188, missing_fvg_or_orderblock=26, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50191): no_ma_cross=35249, basic_filters_failed=14019, ma_cross_cooldown=590, ma_cross_htf_misaligned=333
- **EVAL::MEAN_REVERT** (total=48847): no_extension=40178, basic_filters_failed=8669
- **EVAL::MOVER_AVWAP_SCALP** (total=59018): no_mover_leg=19738, no_avwap_tag=17868, basic_filters_failed=16170, avwap_slope_against=3573, avwap_reclaim_no_volume=915, no_avwap_reclaim=705, anchor_too_recent=49
- **EVAL::MOVER_TREND_PULLBACK** (total=49010): mover_run_too_small=23757, basic_filters_failed=16085, no_reclaim=7760, no_pullback_tag=1408
- **EVAL::OPENING_RANGE_BREAKOUT** (total=50136): feature_disabled=50136
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50079): regime_blocked=32652, breakout_not_found=11368, basic_filters_failed=4236, adx_reject=1779, ema_alignment_reject=44
- **EVAL::QUIET_COMPRESSION_BREAK** (total=49432): regime_blocked=19054, compression_not_detected=13123, basic_filters_failed=9521, breakout_not_detected=7086, volume_confirmation_failed=610, rsi_reject=18, missing_fvg_or_orderblock=11, macd_reject=9
- **EVAL::RANGE_FADE** (total=50022): no_range_edge=41346, basic_filters_failed=8676
- **EVAL::SR_FLIP_RETEST** (total=49497): flip_close_not_confirmed=31835, basic_filters_failed=13746, regime_blocked=1726, long_break_volume_thin=731, h1_break_not_confirmed=712, retest_out_of_zone=535, reclaim_hold_failed=111, long_acceptance_not_held=51, whipsaw_flip=27, wick_quality_failed=19, ema_alignment_reject=3, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=42729): momentum_reject=14681, adx_reject=10823, basic_filters_failed=6318, sweeps_not_detected=4770, macd_reject=2935, ema_alignment_reject=1921, htf_poi_unanchored=1233, rsi_reject=35, invalid_sl_geometry=10, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=43518): h1_trend_not_aligned=14794, basic_filters_failed=6696, ema_alignment_reject=6326, h1_pullback_not_confirmed=6104, ema_not_tested_prev=2770, no_ema_reclaim_close=2708, body_conviction_fail=1545, rsi_reject=1432, prev_already_below_emas=407, no_prev_low_break=209, prev_already_above_emas=167, momentum_flat=148, no_prev_high_break=128, momentum_reject=51, missing_fvg_or_orderblock=17, ema21_not_tagged=16
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=52848): breakout_not_found=27050, basic_filters_failed=15962, move_not_fresh=6826, breakout_stale=2016, retest_proximity_failed=845, volume_spike_missing=110, rsi_reject=20, move_exhausted=12, ema_alignment_reject=4, missing_fvg_or_orderblock=3
- **EVAL::WHALE_MOMENTUM** (total=44485): momentum_reject=29458, recent_ticks_insufficient=11495, basic_filters_failed=3532

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=7): context_floor=7
- **DIVERGENCE_CONTINUATION** (total=339): setup_compat:regime_VOLATILE_UNSUITABLE=328, setup_compat:regime_BREAKOUT_EXPANSION=11
- **FAILED_AUCTION_RECLAIM** (total=693): execution:overextended=363, setup_compat:regime_STRONG_TREND=286, context_floor=38, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **FUNDING_EXTREME_SIGNAL** (total=465): execution:trigger_not_confirmed=462, context_floor=3
- **LIQUIDATION_REVERSAL** (total=15): execution:trigger_not_confirmed=15
- **LIQUIDITY_SWEEP_REVERSAL** (total=1440): execution:overextended=640, setup_compat:regime_STRONG_TREND=403, execution:trigger_not_confirmed=397
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_DIRTY_RANGE=2, execution:overextended=1, execution:trigger_not_confirmed=1, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=3280): setup_compat:regime_STRONG_TREND=1538, setup_compat:regime_WEAK_TREND=1515, execution:overextended=209, entry_quality=18
- **MOVER_AVWAP_SCALP** (total=736): execution:overextended=482, execution:trigger_not_confirmed=167, entry_quality=87
- **MOVER_TREND_PULLBACK** (total=10996): execution:overextended=6288, execution:trigger_not_confirmed=3641, entry_quality=1067
- **QUIET_COMPRESSION_BREAK** (total=40): execution:trigger_not_confirmed=40
- **RANGE_FADE** (total=2929): setup_compat:regime_WEAK_TREND=1038, setup_compat:regime_STRONG_TREND=683, execution:overextended=591, setup_compat:regime_VOLATILE_UNSUITABLE=550, context_edge=42, setup_compat:regime_BREAKOUT_EXPANSION=25
- **TREND_PULLBACK_EMA** (total=1065): setup_compat:regime_CLEAN_RANGE=738, setup_compat:regime_DIRTY_RANGE=242, setup_compat:regime_VOLATILE_UNSUITABLE=48, entry_quality=37
- **VOLUME_SURGE_BREAKOUT** (total=31): context_floor=22, execution:overextended=9
- **WHALE_MOMENTUM** (total=2179): execution:trigger_not_confirmed=2172, context_floor=7

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 88812 | 32.2% |
| RANGING | 85439 | 30.9% |
| TRENDING_DOWN | 44459 | 16.1% |
| TRENDING_UP | 41884 | 15.2% |
| VOLATILE | 15617 | 5.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **351**
- Average confidence gap to threshold: **13.07** (samples=351) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=48, BNBUSDT=30, ETHUSDT=24, ATOMUSDT=19, ADAUSDT=18, XRPUSDT=17, TRXUSDT=15, LINKUSDT=15, TAOUSDT=14, ETCUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 4 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 7 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 85 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 80 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 29 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 17 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 33 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | min_confidence | 22 |
| MEAN_REVERT | kept | min_confidence_pass | 46 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 189 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 336 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 980 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 42 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2870 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 254 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 12 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 235 |
| RANGE_FADE | kept | min_confidence_pass | 17 |
| SR_FLIP_RETEST | filtered | min_confidence | 30 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 7 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 25 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 142 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 38 |
| WHALE_MOMENTUM | filtered | min_confidence | 36 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 4 | 59.80 | 65.00 | 5.20 | 17.82 | 16.50 | 20.00 | 3.50 | 12.00 |
| BREAKDOWN_SHORT | kept | 7 | 81.67 | 65.00 | -16.67 | 21.20 | 19.40 | 20.00 | 5.29 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 87 | 54.15 | 64.59 | 10.44 | 20.34 | 19.81 | 17.92 | 1.07 | 16.21 |
| DIVERGENCE_CONTINUATION | kept | 80 | 70.36 | 65.00 | -5.36 | 20.85 | 19.77 | 17.03 | 1.16 | 0.26 |
| FAILED_AUCTION_RECLAIM | filtered | 33 | 51.72 | 62.18 | 10.46 | 20.82 | 19.58 | 20.00 | 3.52 | 11.52 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 65.94 | 65.00 | -0.94 | 20.88 | 19.50 | 20.00 | 2.10 | 1.80 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 55.58 | 65.00 | 9.42 | 21.14 | 12.85 | 18.38 | 4.76 | 2.61 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.30 | 65.00 | -1.30 | 20.90 | 13.90 | 17.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 49.91 | 65.00 | 15.09 | 20.02 | 15.50 | 18.50 | 1.08 | 20.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 33 | 68.82 | 65.00 | -3.82 | 19.37 | 19.80 | 17.98 | 1.06 | 0.27 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 56.00 | 65.00 | 9.00 | 20.10 | 18.00 | 15.80 | 0.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.30 | 65.00 | -4.30 | 20.73 | 19.15 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 22 | 60.71 | 65.00 | 4.29 | 19.94 | 15.04 | 19.07 | 0.00 | 5.67 |
| MEAN_REVERT | kept | 46 | 73.52 | 65.00 | -8.52 | 20.62 | 16.97 | 15.67 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 192 | 52.80 | 64.98 | 12.18 | 20.15 | 15.71 | 15.80 | 3.83 | 14.51 |
| MOVER_AVWAP_SCALP | kept | 336 | 79.31 | 65.00 | -14.31 | 20.49 | 16.48 | 15.80 | 4.41 | 0.57 |
| MOVER_TREND_PULLBACK | filtered | 1022 | 56.02 | 63.81 | 7.79 | 19.72 | 18.65 | 15.80 | 4.53 | 19.35 |
| MOVER_TREND_PULLBACK | kept | 2870 | 76.30 | 65.00 | -11.30 | 20.04 | 18.52 | 15.80 | 4.52 | 2.03 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 65.20 | 65.00 | -0.20 | 21.20 | 20.00 | 18.30 | 4.50 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 266 | 53.88 | 64.94 | 11.06 | 20.75 | 19.73 | 20.00 | 0.00 | 8.06 |
| QUIET_COMPRESSION_BREAK | kept | 235 | 75.37 | 65.00 | -10.37 | 21.49 | 19.18 | 20.00 | 0.00 | -0.57 |
| RANGE_FADE | kept | 17 | 65.30 | 65.00 | -0.30 | 22.07 | 17.00 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 30 | 58.40 | 65.00 | 6.60 | 20.57 | 20.00 | 15.20 | 1.00 | 9.10 |
| SR_FLIP_RETEST | kept | 7 | 69.79 | 65.00 | -4.79 | 20.89 | 20.00 | 15.31 | 2.50 | 0.43 |
| TREND_PULLBACK_EMA | filtered | 30 | 51.98 | 65.00 | 13.02 | 20.00 | 19.43 | 18.65 | 4.55 | 20.33 |
| TREND_PULLBACK_EMA | kept | 142 | 80.38 | 65.00 | -15.38 | 20.96 | 19.94 | 16.80 | 5.13 | -1.33 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 56.80 | 60.00 | 3.20 | 21.20 | 19.40 | 20.00 | 3.50 | 0.00 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 68.53 | 65.00 | -3.53 | 21.13 | 19.10 | 20.00 | 4.00 | 4.67 |
| WHALE_MOMENTUM | filtered | 74 | 39.39 | 65.00 | 25.61 | 23.47 | 14.79 | 17.00 | 0.00 | 16.96 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 4 | 59.80 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 2.30 | 3.50 |
| BREAKDOWN_SHORT | kept | 7 | 81.67 | 22.71 | 16.86 | 12.00 | 13.57 | 5.00 | 9.24 | 5.29 |
| DIVERGENCE_CONTINUATION | filtered | 87 | 54.15 | 22.43 | 14.44 | 6.62 | 12.37 | 5.32 | 8.12 | 1.07 |
| DIVERGENCE_CONTINUATION | kept | 80 | 70.36 | 22.50 | 13.25 | 5.51 | 14.16 | 6.97 | 8.90 | 1.16 |
| FAILED_AUCTION_RECLAIM | filtered | 33 | 51.72 | 23.42 | 16.67 | 4.36 | 12.33 | 5.26 | 4.94 | 3.52 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 65.94 | 20.20 | 18.00 | 6.60 | 13.00 | 7.10 | 3.74 | 2.10 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 55.58 | 24.53 | 8.71 | 3.18 | 13.59 | 8.29 | 6.60 | 4.76 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.30 | 25.00 | 8.00 | 6.00 | 9.00 | 5.00 | 8.30 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 49.91 | 23.67 | 14.00 | 5.25 | 13.50 | 5.00 | 7.81 | 1.08 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 33 | 68.82 | 22.76 | 16.06 | 4.73 | 11.27 | 5.27 | 8.03 | 1.06 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 56.00 | 25.00 | 14.00 | 6.00 | 11.00 | 5.00 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.30 | 23.00 | 14.00 | 4.50 | 13.25 | 5.88 | 8.68 | 0.00 |
| MEAN_REVERT | filtered | 22 | 60.71 | 25.00 | 15.09 | 3.00 | 12.00 | 4.32 | 6.97 | 0.00 |
| MEAN_REVERT | kept | 46 | 73.52 | 23.22 | 17.22 | 6.91 | 12.13 | 7.50 | 6.54 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 192 | 52.80 | 18.11 | 18.07 | 10.23 | 13.66 | 5.84 | 6.04 | 3.83 |
| MOVER_AVWAP_SCALP | kept | 336 | 79.31 | 20.18 | 18.11 | 9.57 | 13.37 | 5.91 | 8.71 | 4.41 |
| MOVER_TREND_PULLBACK | filtered | 1022 | 56.02 | 18.35 | 18.09 | 7.75 | 13.31 | 5.62 | 8.60 | 4.53 |
| MOVER_TREND_PULLBACK | kept | 2870 | 76.30 | 19.67 | 18.06 | 8.15 | 13.24 | 5.70 | 9.27 | 4.52 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 65.20 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 6.70 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 266 | 53.88 | 18.53 | 17.82 | 11.44 | 14.12 | 6.70 | 4.68 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 235 | 75.37 | 19.14 | 17.98 | 11.14 | 13.95 | 6.13 | 7.82 | 0.00 |
| RANGE_FADE | kept | 17 | 65.30 | 17.00 | 14.00 | 12.00 | 12.00 | 5.00 | 5.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 30 | 58.40 | 17.00 | 18.00 | 3.00 | 14.00 | 8.50 | 6.00 | 1.00 |
| SR_FLIP_RETEST | kept | 7 | 69.79 | 25.00 | 12.29 | 3.86 | 13.86 | 5.00 | 8.14 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 30 | 51.98 | 14.77 | 18.00 | 8.60 | 14.37 | 6.00 | 9.63 | 4.55 |
| TREND_PULLBACK_EMA | kept | 142 | 80.38 | 19.39 | 18.03 | 7.66 | 14.68 | 6.83 | 9.08 | 5.13 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 56.80 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 2.30 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 68.53 | 19.67 | 15.33 | 13.00 | 15.00 | 6.00 | 5.20 | 4.00 |
| WHALE_MOMENTUM | filtered | 74 | 39.39 | 23.03 | 12.86 | 8.11 | 13.55 | 8.23 | 2.53 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 4 | 59.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | **9.00** |
| BREAKDOWN_SHORT | kept | 7 | 81.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 87 | 54.15 | 0.00 | 0.00 | 0.18 | 0.00 | 0.77 | 0.00 | 0.00 | 0.00 | **0.95** |
| DIVERGENCE_CONTINUATION | kept | 80 | 70.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 33 | 51.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 65.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 55.58 | 0.00 | 0.00 | 4.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.38** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 12 | 49.91 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 0.00 | 0.00 | 0.00 | **5.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 33 | 68.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **0.36** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 56.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 22 | 60.71 | 0.00 | 0.00 | 5.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.67** |
| MEAN_REVERT | kept | 46 | 73.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 192 | 52.80 | 0.94 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | **2.15** |
| MOVER_AVWAP_SCALP | kept | 336 | 79.31 | 0.18 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | **0.58** |
| MOVER_TREND_PULLBACK | filtered | 1022 | 56.02 | 0.58 | 0.00 | 2.93 | 0.00 | 0.88 | 0.03 | 0.00 | 0.00 | **4.42** |
| MOVER_TREND_PULLBACK | kept | 2870 | 76.30 | 0.06 | 0.00 | 1.25 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **1.42** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 65.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 266 | 53.88 | 0.00 | 0.00 | 0.22 | 0.00 | 0.34 | 0.00 | 0.00 | 6.20 | **6.76** |
| QUIET_COMPRESSION_BREAK | kept | 235 | 75.37 | 0.00 | 0.00 | 0.18 | 0.00 | 0.28 | 0.00 | 0.00 | 0.18 | **0.64** |
| RANGE_FADE | kept | 17 | 65.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 30 | 58.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 7 | 69.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 30 | 51.98 | 0.00 | 0.00 | 2.93 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | **4.93** |
| TREND_PULLBACK_EMA | kept | 142 | 80.38 | 0.00 | 0.00 | 0.06 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.14** |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 56.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 68.53 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |
| WHALE_MOMENTUM | filtered | 74 | 39.39 | 0.00 | 0.00 | 0.00 | 0.00 | 6.42 | 0.00 | 0.00 | 0.00 | **6.42** |

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
- Outcomes recorded: **139595 held of 275617 seen** across 21 strategies; 3151 cells past the sample floor; **1201 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 32963 | 225/32738/0 | 52% | -0.03 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17258 | 24/17234/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16586 | 1/16585/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 12123 | 4/12119/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9642 | 0/9642/0 | 46% | -0.07 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 9343 | 29/9314/0 | 35% | -0.30 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| TREND_PULLBACK_EMA | 5760 | 2/5758/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 5167 | 0/0/5167 | 43% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.73R) | LONDON/MARKUP/CASCADE/BTC_RISING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 5044 | 11/5033/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4714 | 0/0/4714 | 37% | +0.01 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.61R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.28R) |
| MEAN_REVERT | 4500 | 2/4498/0 | 69% | +0.35 | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.32R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-1.54R) |
| SHADOW_FUNDING_FADE | 4257 | 0/0/4257 | 38% | -0.35 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 3974 | 0/3974/0 | 30% | -0.45 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.44R) |
| VOLUME_SURGE_BREAKOUT | 2575 | 19/2556/0 | 43% | +0.07 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2397 | 4/2393/0 | 32% | -0.45 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.32R) |
| WHALE_MOMENTUM | 1975 | 0/1975/0 | 46% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.89R) |
| SHADOW_CASCADE_REVERSAL | 555 | 0/0/555 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-2.17R) |
| BREAKDOWN_SHORT | 523 | 9/514/0 | 45% | +0.04 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 73 | 0/73/0 | 85% | +0.69 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 38 | 1/37/0 | 34% | -0.40 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `SHADOW_CASCADE_REVERSAL @ OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL` -2.17R (n=16, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 115 | 35% / -0.41R | 115 | 57% / -0.09R | +0.32 | **ATR** |
| TREND_PULLBACK_EMA | 236 | 42% / -0.31R | 236 | 47% / -0.11R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 614 | 38% / -0.22R | 614 | 42% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 2781 | 46% / -0.20R | 2781 | 49% / -0.10R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 4175 | 50% / -0.08R | 4175 | 54% / -0.01R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 941 | 47% / -0.12R | 941 | 53% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 752 | 51% / -0.17R | 752 | 55% / -0.11R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 16 | 31% / -0.25R | 16 | 31% / -0.21R | +0.04 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 88 | 42% / -0.00R | 88 | 52% / -0.04R | -0.04 | **FIXED** |
| RANGE_FADE | 256 | 21% / -0.61R | 256 | 23% / -0.58R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1526 | 44% / -0.13R | 1526 | 43% / -0.16R | -0.03 | **FIXED** |
| MEAN_REVERT | 470 | 54% / -0.01R | 470 | 50% / +0.02R | +0.02 | **ATR** |
| WHALE_MOMENTUM | 152 | 51% / -0.25R | 152 | 51% / -0.26R | -0.01 | **FIXED** |
| BREAKDOWN_SHORT | 21 | 33% / -0.21R | 21 | 33% / -0.20R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2300 | 47% / -0.11R | 2300 | 47% / -0.11R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 10 | 60% / +0.10R | 10 | 60% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6036 | 30% | -0.13R | 286 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 604 | 40% | -0.11R | 139 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 40 | 60% | +0.02R | 22 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1239 | 29% / -1.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 28 | 32% / -0.36R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5049 | 39% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1016 | 32% / -0.56R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 100 | 22% / -0.86R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 795 | 32% / -1.41R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1058 | 36% / -0.13R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 396 | 44% / -0.89R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 135 | 29% / -1.20R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 272 | 30% / -0.57R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 673 | 32% / -0.31R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 20 | 20% / -0.70R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 204 | 46% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 83 | 41% / -0.14R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 7 | 14% / -0.77R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 46 | 48% / -0.25R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 47 · alerting: **4** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 14 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 86/6) (sustained 86 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 1155x (gate reads 0x, withheld 0x — refusal dark); last GPSUSDT age=5051.0s (streak 30/6) (sustained 30 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.40R (bound 0.3) (streak 86/6) (sustained 86 cycles)
- **ALERT** `tuned_variants` — 14 non-stamps — atr_arm_uncomputable=14 (seen=1704 stamped=297 skipped=1393) (streak 63/6) (sustained 63 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 9832055 accepted, 0 rejected | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 9 current): EDENUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 7/12) | 7 |
| auto_dispatch | ok | attempts=7 fanouts=7 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 63407.90 | 0 |
| candle_coverage | ok | 94/97 symbols with ≥20 15m candles, 83/97 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 653 dup bars, 0 undedupable; ws 0 out-of-order, 182 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 14 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 86/6) | 86 |
| context_emission_policy | ok | output +90 / upstream +27 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 482/482 signals (100%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 0 promoted today | 0 |
| dark_resolution | violating | 6 of 103 open dark rows are not being advanced (worst: BABYUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 16/120) | 16 |
| dark_sar_arms | ok | no open arms; covering 500/500 signals (100%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 2596631 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.40R (bound 0.3) (streak 86/6) | 86 |
| emission_controller | ok | last cycle 1421s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4178 stamps (MEAN_REVERT=563, MOVER_AVWAP_SCALP=156, MOVER_TREND_PULLBACK=2873, RANGE_FADE=358, TREND_PULLBACK_EMA=228), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +22 / upstream +382 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 113 detections since last emission (emitted_total=8) — and the POST-SCORING blocked candidates measure +0.35R over n=4498, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 1/6) | 1 |
| mean_revert_path | ok | output +101 / upstream +382 | 0 |
| mover_admission_metadata | ok | 865 symbols known, 163 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 12 held, 12 with scan counts, 12 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3072 rows held, 474211 evicted (sampled: execution:overextended 400/175932, execution:trigger_not_confirmed 400/159272, setup_compat:regime_STRONG_TREND 400/58653) | 0 |
| price_action_lane | ok | 134965 evaluated, 178 emitted; layer1 178 stamped / 0 blind; cooldown=13093, delta_opposed=7454, no_footprint=40742, no_opposing_target=278, no_sweep=66603, rr_below_floor=6617 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.45R over n=3974 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +37 / upstream +382 | 0 |
| sar_alignment_crosscheck | ok | 275/6623 disagreed (4.2%) | 0 |
| sar_exit_shadow | ok | output +18 / upstream +382 | 0 |
| sar_hold_arm | ok | 163 held arms settled, 34 unscored, 9 still walking (9 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 23/98 unfetchable (23%); top cause: located bar does not contain the stamp; symbols: 1000PEPEUSDT, AAVEUSDT, ADAUSDT, ATOMUSDT, AVAXUSDT +7 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 9 current): EDENUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 7/12) | 7 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 498 records await one (75 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| setup_tf_resolver | ok | 55133 resolutions, 35610 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 1155x (gate reads 0x, withheld 0x — refusal dark); last GPSUSDT age=5051.0s (streak 30/6) | 30 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +102 / upstream +382 | 0 |
| structural_snap | ok | 4153/4153 measured, 15 blind, 0 levels moved (refusals: redetect_cooldown=308) | 0 |
| structural_veto_lane | ok | 581 stamped; 0 with no readable level book, 28 with clear air ahead, 377 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +382 / upstream +27 | 0 |
| tuned_variants | violating | 14 non-stamps — atr_arm_uncomputable=14 (seen=1704 stamped=297 skipped=1393) (streak 63/6) | 63 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1409999`
- `Path funnel` emissions: `34`
- `Regime distribution` emissions: `34`
- `QUIET_SCALP_BLOCK` events: `351`
- `confidence_gate` events: `5581`
- `free_channel_post` events: `23`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **9**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 42046 | 42046 | 42046 | 0 |
| futures_aggtrade | 2 | 6432 | 6432 | 50622 | 0 |
| futures_liq | 6 | 8426 | 23067 | 24544 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **23**

| Source | Count |
|---|---:|
| signal_close | 12 |
| regime_shift | 11 |

- By severity: HIGH=23

## Dependency readiness
- cvd: presence[present=226761] state[populated=226761] buckets[many=226761] sources[none] quality[none]
- funding_rate: presence[absent=27248, present=199513] state[empty=27248, populated=199513] buckets[few=199513, none=27248] sources[none] quality[none]
- liquidation_clusters: presence[absent=146465, present=80296] state[empty=146465, populated=80296] buckets[few=64574, none=146465, some=15722] sources[none] quality[none]
- oi_snapshot: presence[absent=23996, present=202765] state[empty=23996, populated=202765] buckets[few=18, many=202562, none=23996, some=185] sources[none] quality[none]
- order_book: presence[absent=84646, present=142115] state[populated=142115, unavailable=84646] buckets[few=142115, none=84646] sources[book_ticker=142115, unavailable=84646] quality[none=84646, top_of_book_only=142115]
- orderblocks: presence[absent=226761] state[empty=226761] buckets[none=226761] sources[measured_dark=226761] quality[none]
- recent_ticks: presence[present=226761] state[populated=226761] buckets[many=226761] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `21.491196513175964` sec
- Median create→first breach: `3326.055041074753` sec
- Median create→terminal: `3337.179092526436` sec
- Median first breach→terminal: `4.410865545272827` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 8.3}, "under_180s": {"count": 1, "pct": 8.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 8.3}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MEAN_REVERT | 1 | 1 | 1.3850174216027824 | 3.0 | 0.46167247386759414 | 0 | 1 |
| MOVER_TREND_PULLBACK | 11 | 11 | 3.6847588719157747 | 3.0 | 1.2282529573052583 | 8 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 14820.685477018356 | 14823.965536117554 |
| MOVER_TREND_PULLBACK | 11 | 11 | 0.0 | 27.3 | 0.0 | 0.0 | 0.0205 | 2593.3652300834656 | 2614.9305469989777 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 178 | 3 | 108 | 0.0 | 0.0 | None | None | 70 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1159 | 30 | 873 | 0.0 | 0.0 | None | None | 286 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-45`
- Gating Δ: `-5405`
- No-generation Δ: `-106096`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.6155, "current_avg_pnl": 0.0205, "current_win_rate": 0.0, "previous_avg_pnl": 1.636, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -57, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 15, "geometry_changed_delta": 0, "geometry_preserved_delta": 80, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
