# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `930` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 193 | 193 | 177 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12464 | 12464 | 12140 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 79926 | 79931 | 43 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 76450 | 76451 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 75963 | 73280 | 3142 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 76508 | 75276 | 1341 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 78623 | 78405 | 259 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 70172 | 70193 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 76630 | 76687 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 76702 | 73185 | 4991 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 84040 | 87276 | 1481 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 79980 | 73561 | 10389 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 78385 | 78386 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 76459 | 76479 | 18 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 75924 | 75729 | 226 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 78188 | 76773 | 1917 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 75652 | 75648 | 219 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 67964 | 64686 | 3502 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 68200 | 67901 | 362 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 79876 | 79854 | 64 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 70204 | 70229 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5165 | 5165 | 4689 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 970 | 970 | 611 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15870 | 15870 | 15784 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 8 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13560 | 13560 | 12591 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3591 | 3591 | 2810 | 26 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 29707 | 29707 | 24778 | 163 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 58 | 58 | 58 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 972 | 972 | 904 | 10 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 5414 | 5414 | 5262 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 859 | 859 | 818 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1576 | 1576 | 1453 | 11 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 230 | 230 | 160 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=79931): breakout_not_found=43611, basic_filters_failed=21275, move_not_fresh=10259, breakout_stale=3239, retest_proximity_failed=1356, volume_spike_missing=161, move_exhausted=20, missing_fvg_or_orderblock=10
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=76451): cls_disabled_merged_into_lsr=76451
- **EVAL::DIVERGENCE_CONTINUATION** (total=73280): cvd_divergence_failed=25525, h1_trend_not_aligned=22672, basic_filters_failed=18915, ema_alignment_reject=5166, retest_proximity_failed=512, missing_cvd=256, missing_fvg_or_orderblock=227, cvd_insufficient=7
- **EVAL::FAILED_AUCTION_RECLAIM** (total=75276): auction_not_detected=46733, basic_filters_failed=18267, reclaim_hold_failed=4366, tail_too_small=3182, regime_blocked=2699, rsi_reject=29
- **EVAL::FUNDING_EXTREME** (total=78405): funding_not_extreme=55121, basic_filters_failed=19484, ema_alignment_reject=1930, rsi_reject=738, missing_funding_rate=704, momentum_reject=200, cvd_divergence_failed=182, missing_fvg_or_orderblock=46
- **EVAL::LIQUIDATION_REVERSAL** (total=70193): cascade_threshold_not_met=50243, basic_filters_failed=19161, cvd_divergence_failed=385, rsi_reject=362, missing_cvd=36, missing_fvg_or_orderblock=4, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=76687): no_ma_cross=55274, basic_filters_failed=18953, ma_cross_cooldown=1488, ma_cross_htf_misaligned=761, ma_cross_htf_unconfirmed=211
- **EVAL::MEAN_REVERT** (total=73185): no_extension=61008, basic_filters_failed=12177
- **EVAL::MOVER_AVWAP_SCALP** (total=87276): no_mover_leg=31167, no_avwap_tag=27510, basic_filters_failed=21720, avwap_slope_against=4221, avwap_reclaim_no_volume=1614, no_avwap_reclaim=1012, anchor_too_recent=32
- **EVAL::MOVER_TREND_PULLBACK** (total=73561): mover_run_too_small=37816, basic_filters_failed=21527, no_reclaim=12055, no_pullback_tag=2163
- **EVAL::OPENING_RANGE_BREAKOUT** (total=78386): feature_disabled=78386
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=76479): regime_blocked=47962, breakout_not_found=21444, basic_filters_failed=5283, adx_reject=1722, ema_alignment_reject=68
- **EVAL::QUIET_COMPRESSION_BREAK** (total=75729): regime_blocked=31058, compression_not_detected=26441, basic_filters_failed=12957, breakout_not_detected=4592, volume_confirmation_failed=593, rsi_reject=76, missing_fvg_or_orderblock=12
- **EVAL::RANGE_FADE** (total=76773): no_range_edge=64584, basic_filters_failed=12189
- **EVAL::SR_FLIP_RETEST** (total=75648): flip_close_not_confirmed=48401, basic_filters_failed=18226, regime_blocked=2683, long_break_volume_thin=1858, h1_break_not_confirmed=1764, retest_out_of_zone=1578, reclaim_hold_failed=653, long_acceptance_not_held=277, ema_alignment_reject=86, wick_quality_failed=59, whipsaw_flip=52, missing_fvg_or_orderblock=11
- **EVAL::STANDARD** (total=64686): momentum_reject=22536, basic_filters_failed=10346, adx_reject=9859, sweeps_not_detected=8972, macd_reject=6387, ema_alignment_reject=4825, htf_poi_unanchored=1560, rsi_reject=140, invalid_sl_geometry=55, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=67901): h1_trend_not_aligned=28447, ema_alignment_reject=10691, h1_pullback_not_confirmed=8151, basic_filters_failed=7993, ema_not_tested_prev=3962, no_ema_reclaim_close=3806, body_conviction_fail=1971, rsi_reject=1749, prev_already_below_emas=349, no_prev_low_break=275, prev_already_above_emas=208, momentum_flat=126, no_prev_high_break=78, ema21_not_tagged=46, momentum_reject=28, missing_fvg_or_orderblock=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=79854): breakout_not_found=44973, basic_filters_failed=21269, move_not_fresh=9406, breakout_stale=3364, retest_proximity_failed=696, volume_spike_missing=108, move_exhausted=22, missing_fvg_or_orderblock=16
- **EVAL::WHALE_MOMENTUM** (total=70229): momentum_reject=52082, recent_ticks_insufficient=12392, basic_filters_failed=5755

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=71): execution:overextended=71
- **DIVERGENCE_CONTINUATION** (total=281): setup_compat:regime_VOLATILE_UNSUITABLE=237, setup_compat:regime_BREAKOUT_EXPANSION=34, execution:overextended=10
- **FAILED_AUCTION_RECLAIM** (total=1807): setup_compat:regime_STRONG_TREND=1163, execution:overextended=432, context_floor=162, setup_compat:regime_VOLATILE_UNSUITABLE=50
- **FUNDING_EXTREME_SIGNAL** (total=827): execution:trigger_not_confirmed=806, context_floor=21
- **LIQUIDATION_REVERSAL** (total=12): execution:trigger_not_confirmed=12
- **LIQUIDITY_SWEEP_REVERSAL** (total=4590): execution:overextended=1686, execution:trigger_not_confirmed=1679, setup_compat:regime_STRONG_TREND=1225
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=2, setup_compat:regime_CLEAN_RANGE=1, execution:overextended=1
- **MEAN_REVERT** (total=8180): setup_compat:regime_STRONG_TREND=4474, setup_compat:regime_WEAK_TREND=3018, execution:overextended=670, entry_quality=18
- **MOVER_AVWAP_SCALP** (total=2183): execution:overextended=1936, execution:trigger_not_confirmed=172, entry_quality=75
- **MOVER_TREND_PULLBACK** (total=12395): execution:trigger_not_confirmed=6114, execution:overextended=5501, entry_quality=780
- **RANGE_FADE** (total=3715): setup_compat:regime_STRONG_TREND=2183, setup_compat:regime_WEAK_TREND=929, execution:overextended=360, setup_compat:regime_VOLATILE_UNSUITABLE=233, setup_compat:regime_BREAKOUT_EXPANSION=10
- **TREND_PULLBACK_EMA** (total=1329): setup_compat:regime_CLEAN_RANGE=784, setup_compat:regime_DIRTY_RANGE=448, setup_compat:regime_VOLATILE_UNSUITABLE=60, entry_quality=37
- **VOLUME_SURGE_BREAKOUT** (total=2): execution:overextended=2

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 155159 | 34.6% |
| QUIET | 100951 | 22.5% |
| TRENDING_DOWN | 89541 | 20.0% |
| TRENDING_UP | 72546 | 16.2% |
| VOLATILE | 29630 | 6.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **56**
- Average confidence gap to threshold: **17.07** (samples=56) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=13, TRXUSDT=7, ETHFIUSDT=7, DOGEUSDT=6, TRUMPUSDT=3, WLDUSDT=3, 牛来USDT=3, ADAUSDT=2, RIVERUSDT=2, AVAXUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 91 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 12 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 57 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 3 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 55 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 48 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 8 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 186 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 17 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 256 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 230 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 695 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 12 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1403 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 19 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 4 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 36 |
| SR_FLIP_RETEST | filtered | min_confidence | 14 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 31 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 43 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 57 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 14 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 72.90 | 65.00 | -7.90 | 19.30 | 19.80 | 20.00 | 4.50 | 5.40 |
| DIVERGENCE_CONTINUATION | filtered | 91 | 50.75 | 64.47 | 13.72 | 20.09 | 19.66 | 17.37 | 1.53 | 16.38 |
| DIVERGENCE_CONTINUATION | kept | 12 | 68.17 | 65.00 | -3.17 | 20.50 | 19.73 | 19.38 | 1.50 | 4.08 |
| FAILED_AUCTION_RECLAIM | filtered | 60 | 49.91 | 63.38 | 13.47 | 21.51 | 19.22 | 20.00 | 2.22 | 6.43 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 68.36 | 65.00 | -3.36 | 21.46 | 19.54 | 20.00 | 4.40 | 1.20 |
| FUNDING_EXTREME_SIGNAL | filtered | 55 | 45.82 | 63.33 | 17.51 | 19.42 | 14.18 | 17.79 | 3.02 | 10.76 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.20 | 65.00 | -4.20 | 21.20 | 13.40 | 18.80 | 7.00 | 4.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 57.56 | 64.00 | 6.44 | 19.55 | 18.22 | 17.00 | 0.71 | 11.76 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 8 | 70.75 | 65.00 | -5.75 | 21.50 | 19.46 | 17.31 | 3.38 | 0.89 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 64.70 | 65.00 | 0.30 | 20.80 | 19.70 | 15.80 | 0.00 | 8.20 |
| MEAN_REVERT | filtered | 203 | 47.47 | 64.71 | 17.24 | 20.92 | 17.21 | 19.38 | 0.00 | 8.40 |
| MOVER_AVWAP_SCALP | filtered | 258 | 47.45 | 64.29 | 16.84 | 19.78 | 14.94 | 15.80 | 4.74 | 19.72 |
| MOVER_AVWAP_SCALP | kept | 230 | 79.09 | 65.00 | -14.09 | 19.78 | 15.45 | 15.80 | 4.26 | 3.70 |
| MOVER_TREND_PULLBACK | filtered | 707 | 57.83 | 64.61 | 6.78 | 19.03 | 18.71 | 15.80 | 4.39 | 16.35 |
| MOVER_TREND_PULLBACK | kept | 1403 | 77.00 | 65.00 | -12.00 | 20.01 | 18.70 | 15.80 | 4.13 | 1.03 |
| QUIET_COMPRESSION_BREAK | filtered | 23 | 51.52 | 64.30 | 12.78 | 19.95 | 19.72 | 20.00 | 0.00 | 12.26 |
| QUIET_COMPRESSION_BREAK | kept | 36 | 75.31 | 65.00 | -10.31 | 22.81 | 19.01 | 20.00 | 0.00 | 0.71 |
| SR_FLIP_RETEST | filtered | 17 | 45.14 | 65.00 | 19.86 | 21.12 | 20.00 | 15.20 | 1.26 | 21.48 |
| SR_FLIP_RETEST | kept | 2 | 70.75 | 65.00 | -5.75 | 21.20 | 20.00 | 15.20 | 1.75 | -3.00 |
| TREND_PULLBACK_EMA | filtered | 31 | 58.81 | 65.00 | 6.19 | 19.32 | 19.69 | 16.73 | 4.69 | 15.53 |
| TREND_PULLBACK_EMA | kept | 43 | 79.32 | 65.00 | -14.32 | 20.73 | 19.89 | 17.30 | 5.50 | 2.14 |
| VOLUME_SURGE_BREAKOUT | filtered | 57 | 52.47 | 64.16 | 11.69 | 20.13 | 18.97 | 20.00 | 3.95 | 12.56 |
| VOLUME_SURGE_BREAKOUT | kept | 14 | 64.11 | 65.00 | 0.89 | 20.42 | 16.18 | 20.00 | 4.46 | 3.73 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 72.90 | 17.00 | 18.00 | 13.50 | 12.00 | 5.00 | 8.30 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 91 | 50.75 | 22.10 | 12.18 | 5.93 | 12.45 | 6.04 | 7.56 | 1.53 |
| DIVERGENCE_CONTINUATION | kept | 12 | 68.17 | 20.33 | 15.67 | 10.50 | 12.75 | 5.42 | 8.34 | 1.50 |
| FAILED_AUCTION_RECLAIM | filtered | 60 | 49.91 | 19.90 | 17.33 | 5.75 | 14.80 | 7.32 | 3.78 | 2.22 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 68.36 | 23.40 | 14.80 | 4.80 | 10.00 | 6.70 | 5.46 | 4.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 55 | 45.82 | 22.96 | 10.76 | 5.73 | 12.07 | 7.12 | 6.38 | 3.02 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.20 | 25.00 | 8.00 | 3.00 | 15.00 | 10.00 | 6.00 | 7.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 57.56 | 22.50 | 15.42 | 3.12 | 13.65 | 5.00 | 8.97 | 0.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 8 | 70.75 | 23.75 | 14.00 | 6.38 | 11.50 | 6.69 | 5.95 | 3.38 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 64.70 | 17.00 | 14.00 | 9.00 | 17.00 | 8.50 | 7.30 | 0.00 |
| MEAN_REVERT | filtered | 203 | 47.47 | 18.37 | 15.18 | 14.51 | 12.93 | 5.00 | 4.51 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 258 | 47.45 | 18.64 | 18.00 | 10.57 | 13.67 | 6.68 | 4.94 | 4.74 |
| MOVER_AVWAP_SCALP | kept | 230 | 79.09 | 19.40 | 18.30 | 11.84 | 13.19 | 7.47 | 8.41 | 4.26 |
| MOVER_TREND_PULLBACK | filtered | 707 | 57.83 | 17.52 | 18.06 | 7.80 | 11.80 | 6.75 | 8.56 | 4.39 |
| MOVER_TREND_PULLBACK | kept | 1403 | 77.00 | 19.47 | 18.02 | 8.02 | 12.95 | 6.79 | 8.82 | 4.13 |
| QUIET_COMPRESSION_BREAK | filtered | 23 | 51.52 | 18.39 | 17.30 | 10.43 | 14.00 | 7.13 | 4.34 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 36 | 75.31 | 20.78 | 15.56 | 12.42 | 14.00 | 6.11 | 7.90 | 0.00 |
| SR_FLIP_RETEST | filtered | 17 | 45.14 | 18.41 | 16.24 | 3.35 | 12.76 | 5.00 | 9.59 | 1.26 |
| SR_FLIP_RETEST | kept | 2 | 70.75 | 21.00 | 18.00 | 3.00 | 11.00 | 6.50 | 9.50 | 1.75 |
| TREND_PULLBACK_EMA | filtered | 31 | 58.81 | 18.03 | 18.00 | 7.50 | 14.00 | 7.82 | 7.19 | 4.69 |
| TREND_PULLBACK_EMA | kept | 43 | 79.32 | 21.86 | 18.00 | 8.27 | 14.07 | 5.73 | 8.45 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 57 | 52.47 | 21.07 | 14.49 | 13.11 | 14.00 | 4.25 | 3.64 | 3.95 |
| VOLUME_SURGE_BREAKOUT | kept | 14 | 64.11 | 9.07 | 17.43 | 14.57 | 12.71 | 5.00 | 7.81 | 4.46 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 72.90 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| DIVERGENCE_CONTINUATION | filtered | 91 | 50.75 | 0.00 | 0.00 | 1.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.67** |
| DIVERGENCE_CONTINUATION | kept | 12 | 68.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 60 | 49.91 | 0.00 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.33** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 68.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 55 | 45.82 | 0.00 | 0.00 | 7.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.49** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.20 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 57.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | **0.25** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 8 | 70.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 64.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 203 | 47.47 | 0.00 | 0.00 | 0.00 | 0.00 | 7.47 | 0.00 | 0.00 | 0.00 | **7.47** |
| MOVER_AVWAP_SCALP | filtered | 258 | 47.45 | 0.00 | 0.00 | 1.13 | 0.00 | 1.10 | 0.16 | 0.00 | 0.72 | **3.11** |
| MOVER_AVWAP_SCALP | kept | 230 | 79.09 | 0.00 | 0.00 | 0.16 | 0.00 | 2.09 | 0.08 | 0.00 | 0.00 | **2.33** |
| MOVER_TREND_PULLBACK | filtered | 707 | 57.83 | 0.00 | 0.00 | 1.30 | 0.00 | 0.19 | 0.04 | 0.00 | 0.03 | **1.56** |
| MOVER_TREND_PULLBACK | kept | 1403 | 77.00 | 0.00 | 0.00 | 0.29 | 0.00 | 0.36 | 0.04 | 0.00 | 0.01 | **0.70** |
| QUIET_COMPRESSION_BREAK | filtered | 23 | 51.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.13 | 0.00 | 8.09 | **11.22** |
| QUIET_COMPRESSION_BREAK | kept | 36 | 75.31 | 0.00 | 0.00 | 0.40 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | **1.00** |
| SR_FLIP_RETEST | filtered | 17 | 45.14 | 0.00 | 0.00 | 0.00 | 0.00 | 2.54 | 0.00 | 0.00 | 0.00 | **2.54** |
| SR_FLIP_RETEST | kept | 2 | 70.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 31 | 58.81 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.93** |
| TREND_PULLBACK_EMA | kept | 43 | 79.32 | 0.00 | 0.00 | 0.37 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **0.65** |
| VOLUME_SURGE_BREAKOUT | filtered | 57 | 52.47 | 0.00 | 0.00 | 0.98 | 0.00 | 0.00 | 0.00 | 0.00 | 2.76 | **3.74** |
| VOLUME_SURGE_BREAKOUT | kept | 14 | 64.11 | 0.00 | 0.00 | 0.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | **0.95** |

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
- Outcomes recorded: **93423 held of 228680 seen** across 21 strategies; 2097 cells past the sample floor; **919 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 35285 | 535/34750/0 | 44% | -0.15 | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_FALLING/MAJOR (+1.18R) | ASIA/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.16R) |
| MOVER_AVWAP_SCALP | 11634 | 139/11495/0 | 40% | -0.24 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 6908 | 80/6828/0 | 41% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 5537 | 26/5511/0 | 55% | +0.06 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | OVERLAP/MARKDOWN/CASCADE/BTC_RISING (-1.17R) |
| SHADOW_MEAN_REVERT | 5102 | 0/0/5102 | 43% | -0.09 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (+0.52R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (-0.91R) |
| TREND_PULLBACK_EMA | 4609 | 24/4585/0 | 47% | -0.11 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4189 | 0/0/4189 | 38% | -0.05 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.04R) |
| QUIET_COMPRESSION_BREAK | 4149 | 208/3941/0 | 45% | -0.12 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.83R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 3508 | 0/0/3508 | 35% | -0.39 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.03R) |
| WHALE_MOMENTUM | 3253 | 2/3251/0 | 42% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 2441 | 38/2403/0 | 39% | -0.28 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| MEAN_REVERT | 1819 | 20/1799/0 | 48% | -0.18 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 1302 | 0/1302/0 | 44% | +0.02 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1244 | 2/1242/0 | 31% | -0.45 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| SR_FLIP_RETEST | 922 | 6/916/0 | 46% | -0.26 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 623 | 0/0/623 | 56% | -0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.49R) |
| BREAKDOWN_SHORT | 340 | 23/317/0 | 41% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 300 | 0/300/0 | 59% | +0.19 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 196 | 0/196/0 | 11% | -1.00 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 56 | 6/50/0 | 39% | -0.13 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 114 | 32% / -0.46R | 114 | 48% / -0.17R | +0.29 | **ATR** |
| TREND_PULLBACK_EMA | 384 | 46% / -0.19R | 384 | 55% / -0.03R | +0.16 | **ATR** |
| RANGE_FADE | 20 | 50% / +0.20R | 20 | 50% / +0.10R | -0.11 | **FIXED** |
| MOVER_AVWAP_SCALP | 883 | 45% / -0.19R | 883 | 50% / -0.09R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 364 | 43% / -0.33R | 364 | 45% / -0.23R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 109 | 49% / -0.27R | 109 | 50% / -0.17R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 619 | 43% / -0.18R | 619 | 45% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5340 | 51% / -0.09R | 5340 | 55% / -0.00R | +0.09 | **ATR** |
| BREAKDOWN_SHORT | 26 | 31% / -0.18R | 26 | 35% / -0.12R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 484 | 52% / -0.18R | 484 | 55% / -0.15R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 695 | 46% / -0.15R | 695 | 46% / -0.16R | -0.01 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 81 | 43% / -0.01R | 81 | 52% / -0.00R | +0.01 | **ATR** |
| DIVERGENCE_CONTINUATION | 552 | 53% / -0.02R | 552 | 58% / -0.02R | +0.01 | **ATR** |
| MEAN_REVERT | 132 | 52% / -0.10R | 132 | 50% / -0.10R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 13 | 31% / -0.46R | 13 | 54% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7815 | 30% | -0.15R | 304 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 883 | 48% | -0.08R | 187 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 54 | 56% | -0.02R | 45 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 137 | 36% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 666 | 38% / -0.08R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 6856 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1133 | 35% / -0.04R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 491 | 36% / -0.13R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 622 | 42% / +0.08R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 511 | 38% / -0.02R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 482 | 45% / -0.09R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 109 | 31% / -0.24R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 143 | 31% / -0.62R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 107 | 52% / +0.03R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 48 | 38% / -0.14R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 18 | 44% / +0.28R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 109 | 35% / -0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 26 | 12% / -0.61R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 17 | 41% / -0.06R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **7** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×683]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 314/6) (sustained 314 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) (sustained 13 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.72R (bound 0.3) (streak 314/6) (sustained 314 cycles)
- **ALERT** `range_fade_emission` — 6917 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 314/6) (sustained 314 cycles)
- **ALERT** `tuned_variants` — 205 non-stamps — atr_arm_uncomputable=205 (seen=2684 stamped=314 skipped=2165) (streak 314/6) (sustained 314 cycles)
- **ALERT** `auto_dispatch` — 72 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode:off=72, mode:paper=72) (streak 298/3) (sustained 298 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 314/3) (sustained 314 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 43 fed / 0 quiet / 0 never delivered of 43 subscribed; 96230662 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 314/3) | 314 |
| ai_governor_live_arms | ok | 10 arms current, none stalled; covering 263/263 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 22 arms current, none stalled; covering 1026/1026 signals (100%) | 0 |
| auto_dispatch | violating | 72 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode:off=72, mode:paper=72) (streak 298/3) | 298 |
| btc_reference | ok | BTC ref 77539.10 | 0 |
| candle_coverage | ok | 82/82 symbols with ≥20 15m candles, 82/82 updated within 45m [fresh=82; 76 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1252 dup bars, 0 undedupable; ws 0 out-of-order, 303 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +17 / upstream +25 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1193/1210 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 3 of 129 open dark rows are not being advanced (worst: 我踏马来了USDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 40/120) | 40 |
| dark_sar_arms | ok | no open arms; covering 1194/1211 signals (99%) | 0 |
| depth_feed | ok | 43/43 books fresh (stale 0, never 0, thin 0); 17894465 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.72R (bound 0.3) (streak 314/6) | 314 |
| emission_controller | ok | last cycle 1407s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×683]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 314/6) | 314 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) | 13 |
| footprint_bars | ok | 5061 sealed bars over 43 symbols; 849 incomplete, 9 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +56 | 0 |
| indicator_cache_key | ok | 92525 frozen value(s) avoided; 499089 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.19R over n=1799 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +23 / upstream +56 | 0 |
| mover_admission_metadata | ok | 897 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 1 locked / 1 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2986 rows held, 1363438 evicted (sampled: execution:trigger_not_confirmed 400/498809, execution:overextended 400/453015, setup_compat:regime_STRONG_TREND 400/203612) | 0 |
| price_action_lane | ok | 594537 evaluated, 709 emitted; layer1 709 stamped / 0 blind; cooldown=75197, delta_opposed=54467, no_footprint=204059, no_opposing_target=584, no_sweep=208592, rr_below_floor=50929 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 6917 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=300, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 314/6) | 314 |
| range_fade_path | ok | output +2 / upstream +56 | 0 |
| sar_alignment_crosscheck | ok | 361/7973 disagreed (4.5%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +56 | 0 |
| sar_hold_arm | ok | 1760 held arms settled, 241 unscored, 21 still walking (20 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/30 unfetchable (7%); top cause: located bar does not contain the stamp; symbols: FLOCKUSDT, UAIUSDT | 0 |
| sar_live_arms | ok | 22 arms current, none stalled; covering 1035/1035 signals (100%) | 0 |
| sar_refresh_budget | ok | 11 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 4 resolved, 24 still mid-window | 0 |
| scan_cycle | ok | last 17.76s, worst 132.02s over 7408 lifetime cycles; lifetime 52 over 60s, 2 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 6.86s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 193877 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 7s ago (8.34s to run, worst 115.02s), 594 overrun(s) of 6247 cycles, TTL 900s; slowest activity=1.14s, alerts=1.12s, signals=0.46s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +57 / upstream +56 | 0 |
| structural_snap | ok | 5037/5037 measured, 19 blind, 0 levels moved (refusals: redetect_cooldown=456) | 0 |
| structural_veto_lane | ok | 752 stamped; 0 with no readable level book, 7 with clear air ahead, 593 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +56 / upstream +25 | 0 |
| tuned_variants | violating | 205 non-stamps — atr_arm_uncomputable=205 (seen=2684 stamped=314 skipped=2165) (streak 314/6) | 314 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration
- `llm_client.google`: 2 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1977042`
- `Path funnel` emissions: `56`
- `Regime distribution` emissions: `56`
- `QUIET_SCALP_BLOCK` events: `56`
- `confidence_gate` events: `3307`
- `free_channel_post` events: `73`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **16**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 1804 | 3853 | 24410 | 0 |
| futures_aggtrade | 2 | 4694 | 4694 | 4739 | 0 |
| futures_depth | 6 | 2009 | 6034 | 6291 | 0 |
| futures_mover | 4 | 1610 | 1651 | 3176 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **73**

| Source | Count |
|---|---:|
| signal_close | 67 |
| regime_shift | 6 |

- By severity: HIGH=73

## Dependency readiness
- cvd: presence[absent=1519, present=347922] state[empty=1519, populated=347922] buckets[many=347769, none=1519, some=153] sources[none] quality[none]
- funding_rate: presence[absent=20857, present=328584] state[empty=20857, populated=328584] buckets[few=328584, none=20857] sources[none] quality[none]
- liquidation_clusters: presence[absent=192881, present=156560] state[empty=192881, populated=156560] buckets[few=126711, none=192881, some=29849] sources[none] quality[none]
- oi_snapshot: presence[absent=20857, present=328584] state[empty=20857, populated=328584] buckets[few=330, many=326964, none=20857, some=1290] sources[none] quality[none]
- order_book: presence[absent=102283, present=247158] state[populated=247158, unavailable=102283] buckets[few=247158, none=102283] sources[book_ticker=247158, unavailable=102283] quality[none=102283, top_of_book_only=247158]
- orderblocks: presence[absent=349441] state[empty=349441] buckets[none=349441] sources[measured_dark=349441] quality[none]
- recent_ticks: presence[present=349441] state[populated=349441] buckets[many=349441] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.412846088409424` sec
- Median create→first breach: `3945.4100580215454` sec
- Median create→terminal: `3947.3929359912872` sec
- Median first breach→terminal: `2.3592379093170166` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 1.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 1.5}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.7341935483870943 | 3.0 | 0.9113978494623648 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 1.1522398181965257 | 1.6434309643533238 | 0.7054178788948304 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.8790521191294368 | 0.9657904434344718 | 0.9101892911710923 | 0 | 1 |
| MOVER_AVWAP_SCALP | 8 | 8 | 2.039481841791987 | 2.400204998051949 | 0.8697937376291536 | 2 | 6 |
| MOVER_TREND_PULLBACK | 41 | 41 | 4.084746719096262 | 3.0 | 1.382843004947569 | 33 | 7 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 1.085621662773267 | 1.3205112337901137 | 0.8982819480307331 | 0 | 8 |
| SR_FLIP_RETEST | 2 | 2 | 1.0964431321005357 | 1.0609937157603293 | 1.0964741436902705 | 1 | 1 |
| TREND_PULLBACK_EMA | 2 | 2 | 2.681059322668 | 3.0 | 0.8936864408893332 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.7342 | 4485.425049066544 | 4490.254686117172 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 2.3045 | 9879.899419546127 | 9884.407941579819 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.3186 | 4436.9929139614105 | 4440.545922994614 |
| MOVER_AVWAP_SCALP | 8 | 8 | 25.0 | 75.0 | 25.0 | 0.0 | -0.6018 | 5399.25307559967 | 5401.981388092041 |
| MOVER_TREND_PULLBACK | 41 | 41 | 26.8 | 56.1 | 26.8 | 0.0 | -0.1472 | 1722.4344260692596 | 1725.9224290847778 |
| QUIET_COMPRESSION_BREAK | 10 | 10 | 50.0 | 40.0 | 50.0 | 0.0 | 0.5508 | 26571.533769011497 | 26574.84758245945 |
| SR_FLIP_RETEST | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 1.4218 | 16040.472906470299 | 16042.860148072243 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.3097 | 2419.1924570798874 | 2421.756229519844 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 859 | 2 | 818 | 100.0 | 0.0 | 16040.472906470299 | 16042.860148072243 | 41 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1576 | 11 | 1453 | 0.0 | 50.0 | 2419.1924570798874 | 2421.756229519844 | 123 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `117`
- Gating Δ: `14943`
- No-generation Δ: `206422`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.6018, "current_avg_pnl": -0.6018, "current_win_rate": 25.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 25.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.5264, "current_avg_pnl": -0.1472, "current_win_rate": 26.8, "previous_avg_pnl": 1.3792, "previous_win_rate": 43.5, "win_rate_delta": -16.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.7955, "current_avg_pnl": 0.5508, "current_win_rate": 50.0, "previous_avg_pnl": -0.2447, "previous_win_rate": 0.0, "win_rate_delta": 50.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -9, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 16040.47, "median_terminal_delta_sec": 16042.86, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 75, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2419.19, "median_terminal_delta_sec": 2421.76, "sl_rate_delta": 50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
