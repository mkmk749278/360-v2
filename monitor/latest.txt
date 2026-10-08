# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `423` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 151 | 151 | 151 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 25364 | 25364 | 24664 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 116593 | 116549 | 72 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 100874 | 100874 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 100333 | 95838 | 5012 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 100920 | 99998 | 986 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 103106 | 102953 | 188 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 87543 | 87543 | 16 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 100993 | 101037 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 101049 | 97884 | 4428 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 125329 | 132353 | 1596 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 116623 | 101237 | 24009 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 102553 | 102553 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 100881 | 100903 | 10 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 100313 | 100115 | 214 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 102320 | 100582 | 2475 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 99725 | 100144 | 123 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 84652 | 79845 | 5118 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 84972 | 84518 | 529 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 116542 | 116562 | 24 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 87562 | 87593 | 7 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6222 | 6222 | 5181 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1294 | 1294 | 663 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 21 | 21 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 37413 | 37413 | 35990 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 5 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 14040 | 14040 | 12617 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4951 | 4951 | 3379 | 41 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 81050 | 81050 | 68815 | 204 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 84 | 84 | 83 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2287 | 2287 | 2236 | 6 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 8044 | 8044 | 7771 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 910 | 910 | 785 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3487 | 3487 | 3351 | 11 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 86 | 86 | 41 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1374 | 1374 | 606 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=116549): breakout_not_found=62864, basic_filters_failed=31035, move_not_fresh=16648, breakout_stale=4450, retest_proximity_failed=1225, volume_spike_missing=309, missing_fvg_or_orderblock=17, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=100874): cls_disabled_merged_into_lsr=100874
- **EVAL::DIVERGENCE_CONTINUATION** (total=95838): cvd_divergence_failed=47863, basic_filters_failed=24025, h1_trend_not_aligned=15368, ema_alignment_reject=7275, retest_proximity_failed=779, missing_fvg_or_orderblock=528
- **EVAL::FAILED_AUCTION_RECLAIM** (total=99998): auction_not_detected=66374, basic_filters_failed=23641, reclaim_hold_failed=4579, tail_too_small=3022, regime_blocked=2251, rsi_reject=131
- **EVAL::FUNDING_EXTREME** (total=102953): funding_not_extreme=74797, basic_filters_failed=24644, ema_alignment_reject=1744, missing_funding_rate=744, rsi_reject=690, cvd_divergence_failed=165, momentum_reject=148, missing_fvg_or_orderblock=21
- **EVAL::LIQUIDATION_REVERSAL** (total=87543): cascade_threshold_not_met=62370, basic_filters_failed=24683, cvd_divergence_failed=270, rsi_reject=216, missing_fvg_or_orderblock=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=101037): no_ma_cross=75918, basic_filters_failed=24045, ma_cross_htf_misaligned=607, ma_cross_cooldown=467
- **EVAL::MEAN_REVERT** (total=97884): no_extension=78827, basic_filters_failed=19057
- **EVAL::MOVER_AVWAP_SCALP** (total=132353): no_avwap_tag=54724, basic_filters_failed=31312, no_mover_leg=27468, avwap_slope_against=13177, avwap_reclaim_no_volume=3506, no_avwap_reclaim=2164, anchor_too_recent=2
- **EVAL::MOVER_TREND_PULLBACK** (total=101237): mover_run_too_small=41634, basic_filters_failed=31173, no_reclaim=25698, no_pullback_tag=2732
- **EVAL::OPENING_RANGE_BREAKOUT** (total=102553): feature_disabled=102553
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=100903): regime_blocked=56854, breakout_not_found=31786, basic_filters_failed=9251, adx_reject=2937, ema_alignment_reject=63, rsi_reject=12
- **EVAL::QUIET_COMPRESSION_BREAK** (total=100115): regime_blocked=46062, compression_not_detected=33772, basic_filters_failed=14373, breakout_not_detected=5291, volume_confirmation_failed=545, rsi_reject=55, missing_fvg_or_orderblock=17
- **EVAL::RANGE_FADE** (total=100582): no_range_edge=81518, basic_filters_failed=19064
- **EVAL::SR_FLIP_RETEST** (total=100144): flip_close_not_confirmed=65949, basic_filters_failed=23612, retest_out_of_zone=2819, h1_break_not_confirmed=2451, regime_blocked=2220, long_break_volume_thin=1889, reclaim_hold_failed=634, long_acceptance_not_held=240, wick_quality_failed=124, ema_alignment_reject=98, whipsaw_flip=77, missing_fvg_or_orderblock=31
- **EVAL::STANDARD** (total=79845): momentum_reject=26068, adx_reject=15007, basic_filters_failed=14472, ema_alignment_reject=8022, macd_reject=7229, sweeps_not_detected=7215, htf_poi_unanchored=1698, invalid_sl_geometry=86, rsi_reject=47, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=84518): h1_pullback_not_confirmed=29036, h1_trend_not_aligned=14644, basic_filters_failed=11857, ema_alignment_reject=11442, ema_not_tested_prev=6268, no_ema_reclaim_close=4365, rsi_reject=2574, body_conviction_fail=2139, prev_already_below_emas=1029, no_prev_low_break=528, no_prev_high_break=189, prev_already_above_emas=187, momentum_flat=161, ema21_not_tagged=74, missing_fvg_or_orderblock=15, momentum_reject=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=116562): breakout_not_found=66770, basic_filters_failed=31032, move_not_fresh=13001, breakout_stale=4248, retest_proximity_failed=1228, volume_spike_missing=271, missing_fvg_or_orderblock=12
- **EVAL::WHALE_MOMENTUM** (total=87593): momentum_reject=68501, recent_ticks_insufficient=13594, basic_filters_failed=5498

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=336): setup_compat:regime_VOLATILE_UNSUITABLE=300, setup_compat:regime_BREAKOUT_EXPANSION=29, execution:overextended=7
- **FAILED_AUCTION_RECLAIM** (total=2280): setup_compat:regime_STRONG_TREND=1401, execution:overextended=722, context_floor=157
- **FUNDING_EXTREME_SIGNAL** (total=1217): execution:trigger_not_confirmed=1208, context_floor=9
- **LIQUIDATION_REVERSAL** (total=21): execution:trigger_not_confirmed=21
- **LIQUIDITY_SWEEP_REVERSAL** (total=9982): setup_compat:regime_STRONG_TREND=4138, execution:trigger_not_confirmed=3767, execution:overextended=2077
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=3, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=11197): setup_compat:regime_STRONG_TREND=6180, setup_compat:regime_WEAK_TREND=4148, execution:overextended=868, entry_quality=1
- **MOVER_AVWAP_SCALP** (total=2706): execution:overextended=2097, execution:trigger_not_confirmed=352, entry_quality=257
- **MOVER_TREND_PULLBACK** (total=22381): execution:trigger_not_confirmed=14518, execution:overextended=6228, entry_quality=1635
- **POST_DISPLACEMENT_CONTINUATION** (total=17): execution:overextended=17
- **QUIET_COMPRESSION_BREAK** (total=51): execution:trigger_not_confirmed=51
- **RANGE_FADE** (total=5787): setup_compat:regime_STRONG_TREND=3035, setup_compat:regime_WEAK_TREND=1970, setup_compat:regime_VOLATILE_UNSUITABLE=508, execution:overextended=261, context_edge=11, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=2897): setup_compat:regime_CLEAN_RANGE=1899, setup_compat:regime_DIRTY_RANGE=965, setup_compat:regime_VOLATILE_UNSUITABLE=27, entry_quality=6
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1
- **WHALE_MOMENTUM** (total=1155): execution:trigger_not_confirmed=1155

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 246907 | 34.3% |
| QUIET | 169131 | 23.5% |
| TRENDING_DOWN | 150376 | 20.9% |
| TRENDING_UP | 132160 | 18.3% |
| VOLATILE | 22030 | 3.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **174**
- Average confidence gap to threshold: **12.41** (samples=174) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=31, BNBUSDT=27, 1000SHIBUSDT=15, ASTERUSDT=14, XRPUSDT=11, LITUSDT=10, XLMUSDT=8, AAVEUSDT=7, DOGEUSDT=6, HYPEUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 127 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 78 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 385 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 15 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 83 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 105 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 6 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 381 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 29 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 95 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 74 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 15 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 503 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 19 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 524 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 942 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 45 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4659 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 38 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 5 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | filtered | min_confidence | 68 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 14 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 58 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 33 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 5 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 31 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 127 | 54.07 | 64.53 | 10.46 | 20.01 | 19.90 | 18.51 | 1.71 | 15.17 |
| DIVERGENCE_CONTINUATION | kept | 78 | 70.08 | 65.00 | -5.08 | 20.52 | 19.70 | 18.37 | 2.31 | -0.51 |
| FAILED_AUCTION_RECLAIM | filtered | 400 | 53.59 | 63.91 | 10.32 | 19.57 | 18.07 | 20.00 | 3.63 | 3.80 |
| FAILED_AUCTION_RECLAIM | kept | 83 | 73.98 | 65.00 | -8.98 | 19.63 | 17.33 | 20.00 | 4.45 | 0.17 |
| FUNDING_EXTREME_SIGNAL | filtered | 105 | 52.83 | 64.47 | 11.64 | 19.13 | 13.83 | 17.59 | 4.28 | 1.83 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 72.05 | 65.00 | -7.05 | 18.90 | 13.70 | 18.50 | 3.00 | 0.60 |
| LIQUIDATION_REVERSAL | filtered | 6 | 52.50 | 10.00 | -42.50 | 22.43 | 8.00 | 20.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 410 | 50.16 | 64.88 | 14.72 | 20.14 | 18.49 | 17.70 | 2.06 | 5.27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 71.06 | 65.00 | -6.06 | 19.73 | 17.84 | 18.10 | 1.77 | 0.23 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 69.15 | 65.00 | -4.15 | 20.75 | 19.65 | 15.80 | 0.00 | 2.60 |
| MEAN_REVERT | filtered | 89 | 49.98 | 65.00 | 15.02 | 19.12 | 16.69 | 15.51 | 0.00 | 17.69 |
| MEAN_REVERT | kept | 3 | 71.90 | 65.00 | -6.90 | 20.50 | 14.00 | 17.03 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 522 | 56.12 | 62.69 | 6.57 | 19.58 | 16.03 | 15.80 | 3.64 | 9.45 |
| MOVER_AVWAP_SCALP | kept | 524 | 83.38 | 65.00 | -18.38 | 20.59 | 14.65 | 15.80 | 4.52 | 0.12 |
| MOVER_TREND_PULLBACK | filtered | 987 | 56.73 | 63.42 | 6.69 | 20.06 | 19.13 | 15.80 | 4.08 | 16.12 |
| MOVER_TREND_PULLBACK | kept | 4659 | 77.03 | 65.00 | -12.03 | 20.45 | 18.91 | 15.80 | 4.28 | 0.78 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 66.00 | 65.00 | -1.00 | 19.40 | 19.10 | 15.20 | 4.50 | 6.00 |
| QUIET_COMPRESSION_BREAK | filtered | 43 | 50.73 | 64.53 | 13.80 | 21.96 | 19.61 | 20.00 | 0.00 | 5.24 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 75.75 | 65.00 | -10.75 | 21.50 | 17.73 | 20.00 | 0.00 | 1.22 |
| SR_FLIP_RETEST | filtered | 69 | 43.40 | 64.30 | 20.90 | 20.01 | 20.00 | 15.59 | 1.89 | 14.99 |
| SR_FLIP_RETEST | kept | 14 | 65.74 | 65.00 | -0.74 | 19.41 | 20.00 | 15.31 | 2.50 | 10.57 |
| TREND_PULLBACK_EMA | filtered | 5 | 57.00 | 65.00 | 8.00 | 21.20 | 20.00 | 17.40 | 4.50 | 20.00 |
| TREND_PULLBACK_EMA | kept | 58 | 74.25 | 65.00 | -9.25 | 22.00 | 19.82 | 17.10 | 4.42 | 1.03 |
| VOLUME_SURGE_BREAKOUT | filtered | 33 | 52.36 | 63.91 | 11.55 | 20.03 | 17.14 | 20.00 | 3.11 | 7.70 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 73.12 | 65.00 | -8.12 | 19.96 | 17.70 | 20.00 | 4.70 | 3.12 |
| WHALE_MOMENTUM | filtered | 31 | 53.76 | 65.00 | 11.24 | 22.47 | 13.97 | 17.00 | 0.00 | 13.23 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 127 | 54.07 | 22.48 | 13.92 | 4.75 | 11.92 | 5.93 | 8.53 | 1.71 |
| DIVERGENCE_CONTINUATION | kept | 78 | 70.08 | 19.87 | 16.33 | 6.69 | 11.67 | 5.22 | 9.14 | 2.31 |
| FAILED_AUCTION_RECLAIM | filtered | 400 | 53.59 | 23.00 | 15.11 | 5.21 | 13.20 | 7.11 | 5.11 | 3.63 |
| FAILED_AUCTION_RECLAIM | kept | 83 | 73.98 | 22.20 | 17.04 | 4.30 | 11.37 | 6.68 | 8.10 | 4.45 |
| FUNDING_EXTREME_SIGNAL | filtered | 105 | 52.83 | 23.32 | 16.48 | 3.69 | 11.77 | 6.24 | 3.88 | 4.28 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 72.05 | 25.00 | 18.00 | 3.00 | 9.00 | 7.50 | 7.15 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 6 | 52.50 | 25.00 | 8.00 | 15.00 | 8.00 | 5.50 | 2.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 410 | 50.16 | 22.87 | 15.54 | 5.40 | 12.52 | 5.41 | 4.86 | 2.06 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 71.06 | 22.89 | 16.27 | 5.15 | 11.89 | 5.19 | 8.12 | 1.77 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 69.15 | 17.00 | 14.00 | 9.00 | 15.50 | 7.25 | 9.00 | 0.00 |
| MEAN_REVERT | filtered | 89 | 49.98 | 18.89 | 14.67 | 8.49 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 3 | 71.90 | 22.33 | 14.00 | 11.00 | 13.00 | 5.00 | 6.57 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 522 | 56.12 | 19.76 | 18.00 | 11.09 | 13.89 | 6.99 | 4.96 | 3.64 |
| MOVER_AVWAP_SCALP | kept | 524 | 83.38 | 18.81 | 18.00 | 12.44 | 13.54 | 7.60 | 9.15 | 4.52 |
| MOVER_TREND_PULLBACK | filtered | 987 | 56.73 | 18.05 | 18.01 | 7.96 | 12.30 | 6.36 | 8.96 | 4.08 |
| MOVER_TREND_PULLBACK | kept | 4659 | 77.03 | 19.30 | 18.00 | 8.06 | 12.32 | 6.64 | 9.29 | 4.28 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 66.00 | 2.00 | 18.00 | 15.00 | 14.00 | 8.50 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 43 | 50.73 | 18.12 | 17.53 | 10.95 | 14.00 | 6.30 | 4.69 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 75.75 | 17.00 | 17.33 | 12.00 | 13.83 | 7.42 | 9.38 | 0.00 |
| SR_FLIP_RETEST | filtered | 69 | 43.40 | 21.75 | 17.86 | 3.00 | 14.22 | 6.59 | 5.04 | 1.89 |
| SR_FLIP_RETEST | kept | 14 | 65.74 | 24.86 | 18.00 | 3.00 | 13.71 | 5.21 | 9.02 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 5 | 57.00 | 17.00 | 18.00 | 7.50 | 14.00 | 9.00 | 7.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 58 | 74.25 | 14.62 | 18.00 | 7.50 | 14.62 | 7.96 | 9.40 | 4.42 |
| VOLUME_SURGE_BREAKOUT | filtered | 33 | 52.36 | 17.00 | 14.85 | 14.36 | 16.36 | 5.00 | 4.38 | 3.11 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 73.12 | 20.20 | 18.00 | 13.80 | 12.80 | 5.00 | 7.74 | 4.70 |
| WHALE_MOMENTUM | filtered | 31 | 53.76 | 22.10 | 8.00 | 8.32 | 12.87 | 6.74 | 8.96 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 127 | 54.07 | 0.00 | 0.00 | 3.28 | 0.00 | 1.04 | 0.00 | 0.00 | 0.00 | **4.32** |
| DIVERGENCE_CONTINUATION | kept | 78 | 70.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 400 | 53.59 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 83 | 73.98 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.10** |
| FUNDING_EXTREME_SIGNAL | filtered | 105 | 52.83 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 72.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 6 | 52.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 410 | 50.16 | 0.00 | 0.00 | 0.79 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | **0.84** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 71.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 69.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 89 | 49.98 | 0.00 | 0.00 | 0.00 | 0.00 | 3.64 | 0.00 | 0.00 | 0.00 | **3.64** |
| MEAN_REVERT | kept | 3 | 71.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 522 | 56.12 | 0.00 | 0.00 | 0.36 | 0.00 | 2.28 | 0.13 | 0.00 | 1.39 | **4.16** |
| MOVER_AVWAP_SCALP | kept | 524 | 83.38 | 0.00 | 0.00 | 0.24 | 0.00 | 0.04 | 0.05 | 0.00 | 0.01 | **0.34** |
| MOVER_TREND_PULLBACK | filtered | 987 | 56.73 | 0.26 | 0.00 | 1.35 | 0.00 | 0.76 | 0.67 | 0.00 | 0.00 | **3.04** |
| MOVER_TREND_PULLBACK | kept | 4659 | 77.03 | 0.31 | 0.00 | 0.18 | 0.00 | 0.08 | 0.05 | 0.00 | 0.00 | **0.62** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 66.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 43 | 50.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.70 | 0.00 | 0.00 | 4.66 | **5.36** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 75.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 69 | 43.40 | 0.00 | 0.00 | 1.51 | 0.00 | 0.00 | 0.00 | 0.00 | 1.67 | **3.18** |
| SR_FLIP_RETEST | kept | 14 | 65.74 | 0.00 | 0.00 | 7.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.43** |
| TREND_PULLBACK_EMA | filtered | 5 | 57.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 58 | 74.25 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.22** |
| VOLUME_SURGE_BREAKOUT | filtered | 33 | 52.36 | 0.00 | 0.00 | 6.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.76 | **7.06** |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 73.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.72 | **0.72** |
| WHALE_MOMENTUM | filtered | 31 | 53.76 | 0.87 | 0.00 | 0.00 | 0.00 | 1.39 | 0.00 | 0.00 | 0.00 | **2.26** |

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
- Outcomes recorded: **133016 held of 436850 seen** across 21 strategies; 3043 cells past the sample floor; **1477 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 42169 | 590/41579/0 | 42% | -0.20 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.17R) |
| MOVER_AVWAP_SCALP | 17546 | 189/17357/0 | 40% | -0.26 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10538 | 120/10418/0 | 38% | -0.26 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 8886 | 55/8831/0 | 49% | -0.06 | NY/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (+1.39R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.19R) |
| TREND_PULLBACK_EMA | 7526 | 32/7494/0 | 43% | -0.18 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_MEAN_REVERT | 6686 | 0/0/6686 | 43% | -0.09 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.92R) |
| LIQUIDITY_SWEEP_REVERSAL | 6070 | 74/5996/0 | 35% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_RANGE_FADE | 5909 | 0/0/5909 | 38% | -0.06 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.57R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| QUIET_COMPRESSION_BREAK | 5459 | 355/5104/0 | 48% | -0.10 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.59R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5296 | 0/0/5296 | 34% | -0.40 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3471 | 2/3469/0 | 45% | -0.32 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 3034 | 35/2999/0 | 46% | -0.14 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 2546 | 2/2544/0 | 30% | -0.49 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2456 | 0/2456/0 | 38% | -0.13 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 2224 | 11/2213/0 | 49% | -0.19 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| RANGE_FADE | 1142 | 4/1138/0 | 42% | -0.34 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1107 | 0/0/1107 | 54% | -0.04 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.12R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 288 | 0/288/0 | 30% | -0.60 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 86 | 12/74/0 | 47% | -0.07 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 10 | 0/10/0 | 60% | +0.21 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 179 | 26% / -0.60R | 179 | 50% / -0.16R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 16 | 31% / -0.48R | 16 | 56% / -0.22R | +0.26 | **ATR** |
| TREND_PULLBACK_EMA | 614 | 43% / -0.24R | 614 | 56% / -0.04R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1041 | 45% / -0.32R | 1041 | 54% / -0.15R | +0.17 | **ATR** |
| MOVER_AVWAP_SCALP | 1426 | 43% / -0.21R | 1426 | 49% / -0.08R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 391 | 45% / -0.32R | 391 | 47% / -0.21R | +0.11 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 125 | 37% / -0.17R | 125 | 46% / -0.07R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6655 | 48% / -0.13R | 6655 | 53% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1005 | 40% / -0.24R | 1005 | 43% / -0.14R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 203 | 48% / -0.23R | 203 | 51% / -0.16R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 901 | 48% / -0.12R | 901 | 54% / -0.05R | +0.07 | **ATR** |
| MA_CROSS_TREND_SHIFT | 26 | 46% / -0.13R | 26 | 46% / -0.07R | +0.05 | **ATR** |
| RANGE_FADE | 50 | 36% / -0.33R | 50 | 38% / -0.34R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 891 | 46% / -0.14R | 891 | 46% / -0.14R | -0.00 | **FIXED** |
| MEAN_REVERT | 226 | 53% / -0.05R | 226 | 51% / -0.05R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9485 | 29% | -0.25R | 310 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1426 | 46% | -0.08R | 212 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 77 | 49% | -0.06R | 51 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 823 | 37% / -0.15R | +0.92 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1042 | 39% / -0.27R | +0.74 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1844 | 34% / -0.11R | +0.73 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8495 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1006 | 39% / -0.04R | +0.24 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 148 | 36% / -0.31R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 869 | 35% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 817 | 33% / -0.19R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 184 | 29% / -0.41R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 237 | 30% / -0.62R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 187 | 55% / +0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 38 | 32% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 204 | 32% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 41 | 27% / -0.45R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 22 | 45% / -0.04R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 12 | 42% / +0.55R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×224]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 234/6) (sustained 234 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.53R (bound 0.3) (streak 549/6) (sustained 549 cycles)
- **ALERT** `tuned_variants` — 386 non-stamps — atr_arm_uncomputable=386 (seen=8982 stamped=749 skipped=7847) (streak 544/6) (sustained 544 cycles)
- **ALERT** `auto_dispatch` — 76 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=76) (streak 538/3) (sustained 538 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 51 fed / 0 quiet / 2 never delivered of 53 subscribed; 132291336 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 22 arms current, none stalled; covering 1274/1274 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 41 arms current, none stalled; covering 1110/1110 signals (100%) | 0 |
| auto_dispatch | violating | 76 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=76) (streak 538/3) | 538 |
| binance_ip_weight | ok | peak 263/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82663.30 | 0 |
| candle_coverage | ok | 96/96 symbols with ≥20 15m candles, 96/96 updated within 45m [fresh=96; 78 Tier-1 futures + 19 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 97 dup bars, 0 undedupable; ws 0 out-of-order, 603 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 48 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +100 / upstream +30 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1504/1522 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 103 open dark rows are not being advanced (worst: USELESSUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 8/120) | 8 |
| dark_sar_arms | ok | no open arms; covering 1499/1517 signals (99%) | 0 |
| depth_feed | ok | 51/53 books fresh (stale 0, never 2, thin 0); 57834436 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.53R (bound 0.3) (streak 549/6) | 549 |
| emission_controller | ok | last cycle 683s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×224]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 234/6) | 234 |
| entry_quality_effective | ok | 13550 evaluated, 4154 suppressed, 5623 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,365 reads/day of 50,000 [engine 1,326, signing 39]; top site keystore.roster_doc at 287/day (engine) | 0 |
| footprint_bars | ok | 6120 sealed bars over 51 symbols; 1124 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +29 / upstream +472 | 0 |
| indicator_cache_key | ok | 204846 frozen value(s) avoided; 1124569 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.15R over n=2999 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +472 but output +0 (streak 7/72) | 7 |
| mover_admission_metadata | ok | 924 symbols known, 217 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 19 held, 19 with scan counts, 18 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3128 rows held, 2460347 evicted (sampled: execution:trigger_not_confirmed 400/896061, execution:overextended 400/794592, setup_compat:regime_STRONG_TREND 400/383556) | 0 |
| price_action_lane | ok | 1832756 evaluated, 1226 emitted; layer1 1226 stamped / 0 blind; cooldown=220487, delta_opposed=145660, no_footprint=685783, no_opposing_target=1081, no_sweep=643697, rr_below_floor=134822 | 0 |
| promoted_pair_integrity | ok | 19/19 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.34R over n=1138 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +2 / upstream +472 | 0 |
| sar_alignment_crosscheck | ok | 432/16420 disagreed (2.6%) | 0 |
| sar_exit_shadow | ok | output +14 / upstream +472 | 0 |
| sar_hold_arm | ok | 1854 held arms settled, 146 unscored, 40 still walking (32 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 12/56 unfetchable (21%); top cause: located bar does not contain the stamp; symbols: BTWUSDT, ENAUSDT, FETUSDT, LYNUSDT, METUSDT +7 more | 0 |
| sar_live_arms | ok | 40 arms current, none stalled; covering 1109/1109 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 456 records await one (44 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 13.22s, worst 115.36s over 21520 lifetime cycles; lifetime 27 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.48s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 896985 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 3s ago (36.57s to run, worst 79.83s), 545 overrun(s) of 11640 cycles, TTL 900s; slowest user_positions=4.56s, dark_promotion=4.13s, position_marks=2.71s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=1, gate reads=0, withheld=1) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +28 / upstream +472 | 0 |
| structural_snap | ok | 5991/5991 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=746) | 0 |
| structural_veto_lane | ok | 1395 stamped; 0 with no readable level book, 45 with clear air ahead, 1076 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +472 / upstream +30 | 0 |
| tuned_variants | violating | 386 non-stamps — atr_arm_uncomputable=386 (seen=8982 stamped=749 skipped=7847) (streak 544/6) | 544 |
| unlock_shorts | ok | 12 open, 43 scheduled, calendar 11.5h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 12 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3448756`
- `Path funnel` emissions: `84`
- `Regime distribution` emissions: `84`
- `QUIET_SCALP_BLOCK` events: `174`
- `confidence_gate` events: `8357`
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
| futures_aggtrade | 7 | 14318 | 16487 | 18631 | 0 |
| futures_liq | 2 | 2375 | 2375 | 9497 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=621589] state[populated=621589] buckets[many=621589] sources[none] quality[none]
- funding_rate: presence[absent=70261, present=551328] state[empty=70261, populated=551328] buckets[few=551328, none=70261] sources[none] quality[none]
- liquidation_clusters: presence[absent=352358, present=269231] state[empty=352358, populated=269231] buckets[few=217678, none=352358, some=51553] sources[none] quality[none]
- oi_snapshot: presence[absent=70261, present=551328] state[empty=70261, populated=551328] buckets[few=319, many=548903, none=70261, some=2106] sources[none] quality[none]
- order_book: presence[absent=158714, present=462875] state[populated=462875, unavailable=158714] buckets[few=462875, none=158714] sources[book_ticker=462875, unavailable=158714] quality[none=158714, top_of_book_only=462875]
- orderblocks: presence[absent=621589] state[empty=621589] buckets[none=621589] sources[measured_dark=621589] quality[none]
- recent_ticks: presence[present=621589] state[populated=621589] buckets[many=621589] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.1022194623947144` sec
- Median create→first breach: `5420.375674962997` sec
- Median create→terminal: `5420.714751005173` sec
- Median first breach→terminal: `6.449222564697266e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.7999999999999945 | 1.4350707706133459 | 0.557463796477491 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.4608384393391702 | 3.0 | 0.8202794797797234 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.8945563787784256 | 2.99826191590347 | 0.6316071415751314 | 1 | 1 |
| MOVER_AVWAP_SCALP | 7 | 7 | 2.4420802672250423 | 2.5949205665722346 | 0.8652681568560193 | 0 | 6 |
| MOVER_TREND_PULLBACK | 16 | 16 | 4.193835010469518 | 2.9932500000000024 | 1.4700814324626887 | 13 | 3 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.0582208823596444 | 1.1661951807500741 | 0.961776153352327 | 0 | 2 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.1221353284396778 | 1.2746286073336048 | 0.880362579329733 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4351 | 1433.696230173111 | 1433.6967000961304 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 4.9217 | 1717.3084790706635 | 1725.04341506958 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 3.0693 | 6300.741458058357 | 6301.080514550209 |
| MOVER_AVWAP_SCALP | 7 | 7 | 14.3 | 71.4 | 14.3 | 0.0 | -1.1032 | 6386.674910783768 | 6386.674949884415 |
| MOVER_TREND_PULLBACK | 16 | 16 | 6.2 | 56.2 | 6.2 | 0.0 | -1.4524 | 3435.5460815429688 | 3435.5461300611496 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 75.0 | 25.0 | 75.0 | 0.0 | 1.7486 | 37131.879366874695 | 37132.326496481895 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.6832 | 4652.905375957489 | 4653.84694814682 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 910 | 1 | 785 | 0.0 | 0.0 | None | None | 125 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3487 | 11 | 3351 | 100.0 | 0.0 | 4652.905375957489 | 4653.84694814682 | 136 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `28`
- Gating Δ: `-20131`
- No-generation Δ: `-648481`
- Fast failures Δ: `-1`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": -2.2321, "current_avg_pnl": -1.1032, "current_win_rate": 14.3, "previous_avg_pnl": 1.1289, "previous_win_rate": 50.0, "win_rate_delta": -35.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.8082, "current_avg_pnl": -1.4524, "current_win_rate": 6.2, "previous_avg_pnl": 0.3558, "previous_win_rate": 36.4, "win_rate_delta": -30.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.8734, "current_avg_pnl": 1.7486, "current_win_rate": 75.0, "previous_avg_pnl": 0.8752, "previous_win_rate": 46.2, "win_rate_delta": 28.8}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -52, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -81, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 3825.19, "median_terminal_delta_sec": 3826.13, "sl_rate_delta": -100.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
