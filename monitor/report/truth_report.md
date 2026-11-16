# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: MOVER_TREND_PULLBACK
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `3409` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 125 | 125 | 125 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9511 | 9511 | 8562 | 15 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 95543 | 95564 | 5 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 90779 | 90779 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 90447 | 88693 | 2067 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 90807 | 90047 | 822 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 90388 | 89990 | 428 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 79802 | 79811 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 90875 | 90909 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 90914 | 88660 | 3179 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 100083 | 106071 | 551 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 95576 | 88225 | 11819 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 89754 | 89754 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 90785 | 90793 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 90429 | 90393 | 51 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 91844 | 89611 | 3273 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 89757 | 90245 | 137 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 79442 | 75650 | 4065 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 79723 | 79197 | 600 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 95503 | 95524 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 79815 | 79828 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4663 | 4663 | 4043 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1104 | 1104 | 358 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 23085 | 23085 | 22864 | 5 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 5 | 5 | 0 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 9886 | 9886 | 6788 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2011 | 2011 | 560 | 28 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 38072 | 38072 | 16980 | 405 | active-healthy (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 26 | 26 | 26 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 375 | 375 | 142 | 24 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 10404 | 10404 | 5129 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 975 | 975 | 337 | 16 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2765 | 2765 | 2119 | 38 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 120 | 120 | 85 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=95564): breakout_not_found=45708, basic_filters_failed=34492, move_not_fresh=9858, breakout_stale=3593, retest_proximity_failed=1457, volume_spike_missing=360, move_exhausted=83, missing_fvg_or_orderblock=13
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=90779): cls_disabled_merged_into_lsr=90779
- **EVAL::DIVERGENCE_CONTINUATION** (total=88693): cvd_divergence_failed=31329, basic_filters_failed=29311, h1_trend_not_aligned=22903, ema_alignment_reject=4342, retest_proximity_failed=561, missing_fvg_or_orderblock=247
- **EVAL::FAILED_AUCTION_RECLAIM** (total=90047): auction_not_detected=53103, basic_filters_failed=28899, reclaim_hold_failed=3433, regime_blocked=2633, tail_too_small=1920, rsi_reject=59
- **EVAL::FUNDING_EXTREME** (total=89990): funding_not_extreme=56207, basic_filters_failed=28921, ema_alignment_reject=3072, missing_funding_rate=624, rsi_reject=592, cvd_divergence_failed=293, momentum_reject=236, missing_fvg_or_orderblock=45
- **EVAL::LIQUIDATION_REVERSAL** (total=79811): cascade_threshold_not_met=50019, basic_filters_failed=29093, rsi_reject=347, cvd_divergence_failed=331, missing_fvg_or_orderblock=21
- **EVAL::MA_CROSS_TREND_SHIFT** (total=90909): no_ma_cross=61075, basic_filters_failed=29328, ma_cross_cooldown=413, ma_cross_htf_misaligned=93
- **EVAL::MEAN_REVERT** (total=88660): no_extension=71780, basic_filters_failed=16880
- **EVAL::MOVER_AVWAP_SCALP** (total=106071): no_avwap_tag=35012, basic_filters_failed=34669, no_mover_leg=23424, avwap_slope_against=9441, avwap_reclaim_no_volume=1945, no_avwap_reclaim=1476, anchor_too_recent=104
- **EVAL::MOVER_TREND_PULLBACK** (total=88225): mover_run_too_small=35254, basic_filters_failed=34578, no_reclaim=17157, no_pullback_tag=1236
- **EVAL::OPENING_RANGE_BREAKOUT** (total=89754): feature_disabled=89754
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=90793): regime_blocked=52731, breakout_not_found=21161, basic_filters_failed=12394, adx_reject=4461, ema_alignment_reject=46
- **EVAL::QUIET_COMPRESSION_BREAK** (total=90393): regime_blocked=40589, compression_not_detected=31052, basic_filters_failed=16494, breakout_not_detected=1904, volume_confirmation_failed=324, rsi_reject=28, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=89611): no_range_edge=72724, basic_filters_failed=16887
- **EVAL::SR_FLIP_RETEST** (total=90245): flip_close_not_confirmed=52428, basic_filters_failed=28867, regime_blocked=2622, retest_out_of_zone=2348, long_break_volume_thin=1476, h1_break_not_confirmed=1286, reclaim_hold_failed=742, long_acceptance_not_held=235, wick_quality_failed=113, ema_alignment_reject=103, whipsaw_flip=13, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=75650): adx_reject=26782, momentum_reject=19654, basic_filters_failed=11319, sweeps_not_detected=7131, ema_alignment_reject=5077, macd_reject=4797, htf_poi_unanchored=826, rsi_reject=29, invalid_sl_geometry=23, mtf_reject=12
- **EVAL::TREND_PULLBACK** (total=79197): h1_trend_not_aligned=28664, basic_filters_failed=16870, ema_alignment_reject=10836, h1_pullback_not_confirmed=6598, ema_not_tested_prev=5833, no_ema_reclaim_close=4420, body_conviction_fail=2465, rsi_reject=1509, prev_already_below_emas=863, no_prev_low_break=634, momentum_flat=168, prev_already_above_emas=134, no_prev_high_break=78, ema21_not_tagged=67, missing_fvg_or_orderblock=42, momentum_reject=16
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=95524): breakout_not_found=49296, basic_filters_failed=34491, move_not_fresh=7163, breakout_stale=3302, retest_proximity_failed=1028, volume_spike_missing=233, missing_fvg_or_orderblock=10, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=79828): momentum_reject=70372, recent_ticks_insufficient=5361, basic_filters_failed=4095

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=2): execution:overextended=2
- **DIVERGENCE_CONTINUATION** (total=146): setup_compat:regime_VOLATILE_UNSUITABLE=127, setup_compat:regime_BREAKOUT_EXPANSION=19
- **FAILED_AUCTION_RECLAIM** (total=1130): execution:overextended=443, setup_compat:regime_STRONG_TREND=387, context_floor=208, setup_compat:regime_VOLATILE_UNSUITABLE=92
- **FUNDING_EXTREME_SIGNAL** (total=891): execution:trigger_not_confirmed=844, context_floor=47
- **LIQUIDATION_REVERSAL** (total=12): execution:trigger_not_confirmed=12
- **LIQUIDITY_SWEEP_REVERSAL** (total=5025): execution:trigger_not_confirmed=1956, setup_compat:regime_STRONG_TREND=1553, execution:overextended=1516
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:overextended=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=7660): setup_compat:regime_WEAK_TREND=4659, setup_compat:regime_STRONG_TREND=2078, execution:overextended=914, entry_quality=9
- **MOVER_AVWAP_SCALP** (total=1104): execution:overextended=613, execution:trigger_not_confirmed=330, entry_quality=161
- **MOVER_TREND_PULLBACK** (total=17897): execution:trigger_not_confirmed=11077, execution:overextended=3492, entry_quality=3328
- **POST_DISPLACEMENT_CONTINUATION** (total=24): execution:overextended=24
- **QUIET_COMPRESSION_BREAK** (total=20): execution:trigger_not_confirmed=17, execution:overextended=3
- **RANGE_FADE** (total=8933): setup_compat:regime_WEAK_TREND=4324, setup_compat:regime_STRONG_TREND=2990, setup_compat:regime_VOLATILE_UNSUITABLE=744, execution:overextended=483, context_edge=347, setup_compat:regime_BREAKOUT_EXPANSION=45
- **TREND_PULLBACK_EMA** (total=2457): setup_compat:regime_CLEAN_RANGE=1851, setup_compat:regime_DIRTY_RANGE=484, entry_quality=106, setup_compat:regime_VOLATILE_UNSUITABLE=16

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 236394 | 39.1% |
| TRENDING_UP | 127386 | 21.1% |
| TRENDING_DOWN | 114303 | 18.9% |
| QUIET | 98872 | 16.3% |
| VOLATILE | 27770 | 4.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **237**
- Average confidence gap to threshold: **13.28** (samples=237) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BULLAUSDT=55, AAVEUSDT=38, FILUSDT=23, 1000PEPEUSDT=21, BTCUSDT=18, HYPEUSDT=11, PUMPUSDT=8, 1000SHIBUSDT=7, XMRUSDT=6, DOTUSDT=6

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 42 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 232 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 75 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 15 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 97 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 32 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 117 |
| MEAN_REVERT | kept | min_confidence_pass | 6 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 614 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 33 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 320 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3891 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 178 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 6287 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 32 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 29 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 119 |
| SR_FLIP_RETEST | filtered | min_confidence | 18 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 12 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 219 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 141 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 168 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 27 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 42 | 60.51 | 64.00 | 3.49 | 20.25 | 19.54 | 17.83 | 0.24 | 4.85 |
| DIVERGENCE_CONTINUATION | kept | 232 | 75.38 | 65.00 | -10.38 | 20.90 | 19.23 | 17.89 | 0.55 | -2.03 |
| FAILED_AUCTION_RECLAIM | filtered | 79 | 47.89 | 60.28 | 12.39 | 21.06 | 18.18 | 20.00 | 2.27 | 21.40 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 68.20 | 65.00 | -3.20 | 21.20 | 19.40 | 20.00 | 3.50 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 44.88 | 61.00 | 16.12 | 20.74 | 13.97 | 16.72 | 3.80 | 13.63 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 61.00 | 65.00 | 4.00 | 21.20 | 14.00 | 17.00 | 5.00 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 100 | 49.37 | 64.92 | 15.55 | 20.06 | 18.24 | 17.61 | 2.26 | 15.45 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 69.86 | 65.00 | -4.86 | 20.34 | 15.96 | 19.05 | 0.81 | 0.54 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.80 | 61.00 | 10.20 | 19.90 | 14.10 | 15.80 | 0.00 | 7.20 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.00 | 65.00 | 0.00 | 18.70 | 20.00 | 15.80 | 0.00 | 2.00 |
| MEAN_REVERT | filtered | 117 | 52.15 | 64.91 | 12.76 | 21.12 | 15.82 | 15.10 | 0.00 | 10.41 |
| MEAN_REVERT | kept | 6 | 67.50 | 65.00 | -2.50 | 21.70 | 15.08 | 14.27 | 0.00 | 3.70 |
| MOVER_AVWAP_SCALP | filtered | 649 | 53.84 | 62.12 | 8.28 | 20.13 | 15.45 | 15.80 | 4.11 | 14.94 |
| MOVER_AVWAP_SCALP | kept | 320 | 77.60 | 65.00 | -12.60 | 20.13 | 17.02 | 15.80 | 4.66 | 4.43 |
| MOVER_TREND_PULLBACK | filtered | 4069 | 55.65 | 64.13 | 8.48 | 19.73 | 18.69 | 15.80 | 3.93 | 16.49 |
| MOVER_TREND_PULLBACK | kept | 6287 | 76.35 | 65.00 | -11.35 | 20.22 | 18.81 | 15.80 | 4.31 | 2.47 |
| QUIET_COMPRESSION_BREAK | filtered | 61 | 46.64 | 64.93 | 18.29 | 22.95 | 19.48 | 20.00 | 0.00 | 11.69 |
| QUIET_COMPRESSION_BREAK | kept | 119 | 75.67 | 65.00 | -10.67 | 21.84 | 18.84 | 20.00 | 0.00 | 0.84 |
| SR_FLIP_RETEST | filtered | 30 | 60.02 | 64.83 | 4.81 | 21.30 | 20.00 | 15.23 | 2.02 | 7.32 |
| SR_FLIP_RETEST | kept | 219 | 71.77 | 65.00 | -6.77 | 21.38 | 20.00 | 15.40 | 2.28 | 2.18 |
| TREND_PULLBACK_EMA | filtered | 150 | 55.65 | 64.35 | 8.70 | 21.01 | 19.63 | 17.99 | 4.77 | 19.30 |
| TREND_PULLBACK_EMA | kept | 168 | 77.78 | 65.00 | -12.78 | 21.27 | 19.94 | 17.04 | 4.99 | 0.65 |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 51.90 | 63.22 | 11.32 | 19.82 | 20.00 | 20.00 | 3.50 | 6.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 42 | 60.51 | 19.48 | 14.19 | 5.07 | 13.83 | 4.52 | 9.45 | 0.24 |
| DIVERGENCE_CONTINUATION | kept | 232 | 75.38 | 23.17 | 17.05 | 6.32 | 13.50 | 6.00 | 9.11 | 0.55 |
| FAILED_AUCTION_RECLAIM | filtered | 79 | 47.89 | 20.44 | 17.80 | 5.13 | 13.15 | 6.04 | 8.07 | 2.27 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 68.20 | 25.00 | 18.00 | 9.00 | 17.00 | 5.00 | 5.70 | 3.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 44.88 | 25.00 | 10.00 | 5.40 | 11.80 | 7.57 | 3.94 | 3.80 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 61.00 | 17.00 | 8.00 | 15.00 | 12.00 | 5.00 | 7.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 100 | 49.37 | 23.24 | 14.84 | 5.01 | 12.33 | 6.15 | 7.14 | 2.26 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 69.86 | 20.25 | 15.12 | 8.34 | 13.16 | 4.92 | 7.79 | 0.81 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.80 | 17.00 | 14.00 | 15.00 | 14.00 | 5.00 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.00 | 17.00 | 14.00 | 3.00 | 14.00 | 10.00 | 9.00 | 0.00 |
| MEAN_REVERT | filtered | 117 | 52.15 | 21.74 | 16.67 | 11.28 | 11.71 | 5.00 | 4.39 | 0.00 |
| MEAN_REVERT | kept | 6 | 67.50 | 25.00 | 14.00 | 6.50 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 649 | 53.84 | 19.08 | 18.02 | 11.19 | 13.06 | 6.04 | 5.71 | 4.11 |
| MOVER_AVWAP_SCALP | kept | 320 | 77.60 | 19.97 | 18.00 | 10.75 | 13.97 | 6.55 | 8.50 | 4.66 |
| MOVER_TREND_PULLBACK | filtered | 4069 | 55.65 | 18.31 | 18.10 | 7.81 | 12.45 | 5.87 | 8.52 | 3.93 |
| MOVER_TREND_PULLBACK | kept | 6287 | 76.35 | 19.79 | 18.00 | 7.89 | 13.63 | 6.52 | 9.23 | 4.31 |
| QUIET_COMPRESSION_BREAK | filtered | 61 | 46.64 | 22.11 | 15.90 | 11.56 | 14.25 | 4.83 | 3.94 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 119 | 75.67 | 20.24 | 15.41 | 12.88 | 14.05 | 6.61 | 7.78 | 0.00 |
| SR_FLIP_RETEST | filtered | 30 | 60.02 | 19.40 | 14.00 | 3.60 | 13.10 | 8.02 | 7.21 | 2.02 |
| SR_FLIP_RETEST | kept | 219 | 71.77 | 22.54 | 17.41 | 4.53 | 13.03 | 6.14 | 8.71 | 2.28 |
| TREND_PULLBACK_EMA | filtered | 150 | 55.65 | 13.82 | 18.00 | 9.24 | 14.96 | 5.53 | 9.03 | 4.77 |
| TREND_PULLBACK_EMA | kept | 168 | 77.78 | 18.07 | 18.00 | 7.54 | 15.30 | 7.00 | 8.87 | 4.99 |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 51.90 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 4.00 | 3.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 42 | 60.51 | 0.00 | 0.00 | 1.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.52** |
| DIVERGENCE_CONTINUATION | kept | 232 | 75.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 79 | 47.89 | 0.00 | 0.00 | 5.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.37** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 68.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 44.88 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.96** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 61.00 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 100 | 49.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 69.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.80 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 117 | 52.15 | 0.00 | 0.00 | 0.00 | 0.00 | 7.12 | 0.00 | 0.00 | 0.00 | **7.12** |
| MEAN_REVERT | kept | 6 | 67.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 649 | 53.84 | 0.00 | 0.00 | 2.23 | 0.00 | 1.96 | 0.11 | 0.00 | 1.80 | **6.10** |
| MOVER_AVWAP_SCALP | kept | 320 | 77.60 | 0.00 | 0.00 | 0.14 | 0.00 | 1.73 | 0.00 | 0.00 | 0.13 | **2.00** |
| MOVER_TREND_PULLBACK | filtered | 4069 | 55.65 | 0.00 | 0.00 | 2.24 | 0.00 | 0.71 | 0.40 | 0.00 | 0.04 | **3.39** |
| MOVER_TREND_PULLBACK | kept | 6287 | 76.35 | 0.00 | 0.00 | 0.62 | 0.00 | 0.30 | 0.17 | 0.00 | 0.00 | **1.09** |
| QUIET_COMPRESSION_BREAK | filtered | 61 | 46.64 | 0.00 | 0.00 | 0.24 | 0.00 | 0.14 | 0.75 | 0.00 | 7.83 | **8.96** |
| QUIET_COMPRESSION_BREAK | kept | 119 | 75.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.24 | 0.08 | 0.00 | 0.00 | **0.32** |
| SR_FLIP_RETEST | filtered | 30 | 60.02 | 0.00 | 0.00 | 0.00 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | **1.44** |
| SR_FLIP_RETEST | kept | 219 | 71.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 150 | 55.65 | 0.00 | 0.00 | 3.73 | 0.00 | 0.72 | 0.24 | 0.00 | 0.00 | **4.69** |
| TREND_PULLBACK_EMA | kept | 168 | 77.78 | 0.00 | 0.00 | 0.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.70** |
| VOLUME_SURGE_BREAKOUT | filtered | 27 | 51.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |

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
- Outcomes recorded: **191298 held of 887125 seen** across 21 strategies; 4318 cells past the sample floor; **2330 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49015 | 588/48427/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.26R) |
| MOVER_AVWAP_SCALP | 25664 | 199/25465/0 | 43% | -0.19 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15031 | 247/14784/0 | 46% | -0.13 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14244 | 148/14096/0 | 35% | -0.34 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 13317 | 77/13240/0 | 40% | -0.27 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.42R) |
| LIQUIDITY_SWEEP_REVERSAL | 10564 | 108/10456/0 | 38% | -0.42 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9330 | 454/8876/0 | 45% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8301 | 0/0/8301 | 43% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.11R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7814 | 0/0/7814 | 35% | -0.15 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.33R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.39R) |
| SHADOW_FUNDING_FADE | 7349 | 0/0/7349 | 33% | -0.43 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6725 | 24/6701/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5660 | 71/5589/0 | 37% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4373 | 2/4371/0 | 31% | -0.45 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 4021 | 0/4021/0 | 28% | -0.41 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 2941 | 6/2935/0 | 50% | +0.19 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1741 | 0/0/1741 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.57R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 542 | 0/542/0 | 37% | -0.23 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 228 | 34/194/0 | 45% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 392 | 27% / -0.57R | 392 | 53% / -0.09R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1357 | 39% / -0.35R | 1357 | 50% / -0.08R | +0.27 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1593 | 43% / -0.36R | 1593 | 57% / -0.11R | +0.25 | **ATR** |
| LIQUIDATION_REVERSAL | 34 | 26% / -0.56R | 34 | 47% / -0.32R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 713 | 48% / -0.25R | 713 | 52% / -0.13R | +0.12 | **ATR** |
| MA_CROSS_TREND_SHIFT | 69 | 46% / -0.15R | 69 | 51% / -0.04R | +0.11 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 228 | 38% / -0.16R | 228 | 48% / -0.05R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 2805 | 46% / -0.14R | 2805 | 52% / -0.04R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1562 | 41% / -0.23R | 1562 | 44% / -0.13R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9071 | 48% / -0.13R | 9071 | 54% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1961 | 48% / -0.11R | 1961 | 53% / -0.06R | +0.05 | **ATR** |
| RANGE_FADE | 160 | 42% / +0.02R | 160 | 49% / +0.07R | +0.05 | **ATR** |
| MEAN_REVERT | 474 | 46% / -0.16R | 474 | 45% / -0.17R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1630 | 48% / -0.11R | 1630 | 48% / -0.11R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12112 | 27% | -0.27R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2805 | 50% | -0.03R | 241 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 145 | 49% | -0.05R | 73 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1740 | 34% / -0.21R | +0.85 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1878 | 38% / -0.18R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3352 | 36% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11099 | 36% / -0.15R | +0.38 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2275 | 37% / -0.11R | +0.17 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1580 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1296 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 332 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 509 | 32% / -0.23R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 392 | 47% / -0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 110 | 45% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 618 | 35% / -0.27R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 111 | 31% / -0.35R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 44 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 25 | 48% / +0.53R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 1130/17405 disagreed (6.5%) (streak 106/6) (sustained 106 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 266/6) (sustained 266 cycles)
- **ALERT** `range_fade_emission` — 2050 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=2935, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 31/6) (sustained 31 cycles)
- **ALERT** `tuned_variants` — 452 non-stamps — atr_arm_uncomputable=452 (seen=10471 stamped=973 skipped=9046) (streak 266/6) (sustained 266 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 63107138 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 14 arms current, none stalled; covering 2062/2062 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 2/6) | 2 |
| atr_trail_live_arms | ok | 34 arms current, none stalled; covering 1070/1070 signals (100%) | 0 |
| auto_dispatch | ok | 44 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=44. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 100/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 64681.60 | 0 |
| candle_coverage | ok | 75/75 symbols with ≥20 15m candles, 75/75 updated within 45m [fresh=75; 72 Tier-1 futures + 3 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 326 dup bars, 0 undedupable; ws 0 out-of-order, 256 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 61 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +60 / upstream +37 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2295/2314 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 5 of 133 open dark rows are not being advanced (worst: HUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 36/120) | 36 |
| dark_sar_arms | ok | no open arms; covering 2256/2275 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 21397406 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 266/6) | 266 |
| emission_controller | ok | last cycle 1521s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=143, MOVER_AVWAP_SCALP=358, MOVER_TREND_PULLBACK=3564, RANGE_FADE=1382, TREND_PULLBACK_EMA=553), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=126, cvd_aligned=1. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 3/6) | 3 |
| firestore_read_budget | ok | 1,313 reads/day of 50,000 [engine 1,292, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4920 sealed bars over 41 symbols; 1058 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +15 / upstream +387 | 0 |
| indicator_cache_key | ok | 107550 frozen value(s) avoided; 859574 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=5589 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +10 / upstream +387 | 0 |
| mover_admission_metadata | ok | 946 symbols known, 237 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 3 held, 3 with scan counts, 3 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2170 rows held, 3635695 evicted (sampled: execution:trigger_not_confirmed 281/1280597, execution:overextended 281/1121935, setup_compat:regime_STRONG_TREND 281/626600) | 0 |
| price_action_lane | ok | 751309 evaluated, 787 emitted; layer1 787 stamped / 0 blind; cooldown=108631, delta_opposed=71785, no_footprint=262407, no_opposing_target=1136, no_sweep=240576, rr_below_floor=65987 | 0 |
| promoted_pair_integrity | ok | 3/3 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 2050 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=2935, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 31/6) | 31 |
| range_fade_path | ok | output +27 / upstream +387 | 0 |
| sar_alignment_crosscheck | violating | 1130/17405 disagreed (6.5%) (streak 106/6) | 106 |
| sar_exit_shadow | ok | output +10 / upstream +387 | 0 |
| sar_hold_arm | ok | 1872 held arms settled, 128 unscored, 33 still walking (27 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 5/64 unfetchable (8%); top cause: located bar does not contain the stamp; symbols: 1000PEPEUSDT, BTWUSDT, NIGHTUSDT, PUMPUSDT, XPLUSDT | 0 |
| sar_live_arms | ok | 33 arms current, none stalled; covering 1070/1070 signals (100%) | 0 |
| sar_refresh_budget | ok | 7 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 9 resolved, 50 still mid-window | 0 |
| scan_cycle | ok | last 16.63s, worst 133.59s over 9262 lifetime cycles; lifetime 156 over 60s, 7 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.11s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 316318 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 18s ago (52.85s to run, worst 115.43s), 538 overrun(s) of 5835 cycles, TTL 900s; slowest trail_governor=12.16s, activity=7.28s, pair_context=4.0s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +172 / upstream +387 | 0 |
| structural_snap | ok | 6000/6000 measured, 35 blind, 0 levels moved (refusals: redetect_cooldown=891) | 0 |
| structural_veto_lane | ok | 1578 stamped; 0 with no readable level book, 31 with clear air ahead, 1104 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +387 / upstream +37 | 0 |
| tuned_variants | violating | 452 non-stamps — atr_arm_uncomputable=452 (seen=10471 stamped=973 skipped=9046) (streak 266/6) | 266 |
| unlock_shorts | ok | 18 open, 42 scheduled, calendar 5.8h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 10 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2881941`
- `Path funnel` emissions: `74`
- `Regime distribution` emissions: `74`
- `QUIET_SCALP_BLOCK` events: `237`
- `confidence_gate` events: `12726`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 7 | 4652 | 29384 | 33400 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=465667] state[populated=465667] buckets[many=465667] sources[none] quality[none]
- funding_rate: presence[absent=32435, present=433232] state[empty=32435, populated=433232] buckets[few=433232, none=32435] sources[none] quality[none]
- liquidation_clusters: presence[absent=263171, present=202496] state[empty=263171, populated=202496] buckets[few=169481, none=263171, some=33015] sources[none] quality[none]
- oi_snapshot: presence[absent=32435, present=433232] state[empty=32435, populated=433232] buckets[few=196, many=431970, none=32435, some=1066] sources[none] quality[none]
- order_book: presence[absent=128037, present=337630] state[populated=337630, unavailable=128037] buckets[few=337630, none=128037] sources[book_ticker=337630, unavailable=128037] quality[none=128037, top_of_book_only=337630]
- orderblocks: presence[absent=465667] state[empty=465667] buckets[none=465667] sources[measured_dark=465667] quality[none]
- recent_ticks: presence[present=465667] state[populated=465667] buckets[many=465667] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.4709185361862183` sec
- Median create→first breach: `4155.954847574234` sec
- Median create→terminal: `4157.961230516434` sec
- Median first breach→terminal: `7.462501525878906e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 5.6}, "under_180s": {"count": 2, "pct": 5.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.8}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.8340512673507288 | 3.0 | 0.611350422450243 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 1.1502680241013974 | 3.0 | 0.3834226747004658 | 1 | 2 |
| MEAN_REVERT | 1 | 1 | 2.5833606646988074 | 3.0 | 0.8611202215662691 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.105958816477221 | 2.533789285714278 | 0.8311499414536158 | 0 | 1 |
| MOVER_TREND_PULLBACK | 23 | 23 | 3.9288062447265606 | 3.0 | 1.3096020815755203 | 16 | 5 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.5161185647425812 | 1.6747374999999918 | 0.884674006997359 | 0 | 6 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 3.6676328502415534 | 3.6676328502415534 | 0 | 0 | 0 | 0 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 4.598035072892461 | 4.70378987956899 | 3 | 0 | 0 | 0 | 0 | 0 |
| MEAN_REVERT | 1 | 3.4123209795561382 | 3.875040997048212 | 1 | 0 | 0 | 0 | 0 | 0 |
| MOVER_AVWAP_SCALP | 1 | 2.535540006850711 | 3.1589382231300185 | 1 | 0 | 0 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 23 | 6.001134410450317 | 4.109753681560745 | 6 | 2 | 0 | 17 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 7 | 3.794861986829197 | 2.2741778471138896 | 0 | 0 | 0 | 5 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.6676 | 1503.5865581035614 | 1504.6322259902954 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -3.1022 | 999.556617975235 | 999.5566720962524 |
| MEAN_REVERT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.5834 | 23281.96378493309 | 23281.963805913925 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.106 | 13473.157701015472 | 13473.157753944397 |
| MOVER_TREND_PULLBACK | 23 | 23 | 47.8 | 34.8 | 47.8 | 0.0 | 1.5732 | 3328.0079638957977 | 3328.0080308914185 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 0.0 | 71.4 | 0.0 | 0.0 | -1.2569 | 8350.08316898346 | 8350.083187818527 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 975 | 16 | 337 | 0.0 | 0.0 | None | None | 638 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2765 | 38 | 2119 | 0.0 | 0.0 | None | None | 646 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-637`
- Gating Δ: `4935`
- No-generation Δ: `440654`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.4419, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.4419, "previous_win_rate": 10.0, "win_rate_delta": -10.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -3.1022, "current_avg_pnl": -3.1022, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.8402, "current_avg_pnl": 1.5732, "current_win_rate": 47.8, "previous_avg_pnl": -1.267, "previous_win_rate": 14.3, "win_rate_delta": 33.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -4.111, "current_avg_pnl": -1.2569, "current_win_rate": 0.0, "previous_avg_pnl": 2.8541, "previous_win_rate": 100.0, "win_rate_delta": -100.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 11, "geometry_changed_delta": 0, "geometry_preserved_delta": 375, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -19, "geometry_changed_delta": 0, "geometry_preserved_delta": -14, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3756.68, "median_terminal_delta_sec": -3756.68, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **MOVER_TREND_PULLBACK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
