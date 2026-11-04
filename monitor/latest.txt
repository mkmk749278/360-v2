# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: MOVER_AVWAP_SCALP
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1188` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 241 | 241 | 241 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10877 | 10877 | 9553 | 14 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 99293 | 99307 | 30 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 96998 | 96999 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 96530 | 94085 | 2899 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 97030 | 95684 | 1487 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 96435 | 96310 | 153 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 84408 | 84394 | 25 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 97181 | 97225 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 97239 | 93974 | 4752 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 103672 | 110575 | 1426 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 99347 | 92523 | 11082 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 95783 | 95783 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 97010 | 97028 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 96471 | 96307 | 215 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 98734 | 95819 | 4177 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 95790 | 96178 | 252 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 83740 | 78000 | 6306 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 84310 | 83883 | 519 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 99254 | 99267 | 21 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 84421 | 84439 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 5723 | 5723 | 4765 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 479 | 479 | 34 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 31 | 31 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 32673 | 32673 | 32370 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 14 | 14 | 3 | 5 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13088 | 13088 | 9665 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3330 | 3330 | 449 | 51 | active-healthy (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 28753 | 28753 | 14496 | 275 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1377 | 1377 | 741 | 29 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 11896 | 11896 | 10123 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 726 | 726 | 485 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2072 | 2072 | 1703 | 28 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 122 | 122 | 2 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=99307): breakout_not_found=51807, basic_filters_failed=31007, move_not_fresh=10677, breakout_stale=4402, retest_proximity_failed=1119, volume_spike_missing=279, missing_fvg_or_orderblock=10, move_exhausted=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=96999): cls_disabled_merged_into_lsr=96999
- **EVAL::DIVERGENCE_CONTINUATION** (total=94085): cvd_divergence_failed=33212, basic_filters_failed=27409, h1_trend_not_aligned=24795, ema_alignment_reject=7575, retest_proximity_failed=829, missing_fvg_or_orderblock=265
- **EVAL::FAILED_AUCTION_RECLAIM** (total=95684): auction_not_detected=58025, basic_filters_failed=26731, reclaim_hold_failed=4834, tail_too_small=3638, regime_blocked=2379, rsi_reject=77
- **EVAL::FUNDING_EXTREME** (total=96310): funding_not_extreme=64555, basic_filters_failed=26506, missing_funding_rate=2238, ema_alignment_reject=1678, rsi_reject=1009, momentum_reject=184, cvd_divergence_failed=118, missing_fvg_or_orderblock=22
- **EVAL::LIQUIDATION_REVERSAL** (total=84394): cascade_threshold_not_met=56615, basic_filters_failed=27091, cvd_divergence_failed=358, rsi_reject=291, missing_fvg_or_orderblock=36, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=97225): no_ma_cross=68131, basic_filters_failed=27430, ma_cross_cooldown=1108, ma_cross_htf_misaligned=556
- **EVAL::MEAN_REVERT** (total=93974): no_extension=76004, basic_filters_failed=17970
- **EVAL::MOVER_AVWAP_SCALP** (total=110575): no_avwap_tag=35886, basic_filters_failed=31280, no_mover_leg=31029, avwap_slope_against=7617, avwap_reclaim_no_volume=2704, no_avwap_reclaim=2058, anchor_too_recent=1
- **EVAL::MOVER_TREND_PULLBACK** (total=92523): mover_run_too_small=44139, basic_filters_failed=31144, no_reclaim=14819, no_pullback_tag=2421
- **EVAL::OPENING_RANGE_BREAKOUT** (total=95783): feature_disabled=95783
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=97028): regime_blocked=69374, breakout_not_found=16314, basic_filters_failed=8790, adx_reject=2500, ema_alignment_reject=50
- **EVAL::QUIET_COMPRESSION_BREAK** (total=96307): compression_not_detected=39188, regime_blocked=29923, basic_filters_failed=17926, breakout_not_detected=8523, volume_confirmation_failed=661, rsi_reject=86
- **EVAL::RANGE_FADE** (total=95819): no_range_edge=77848, basic_filters_failed=17971
- **EVAL::SR_FLIP_RETEST** (total=96178): flip_close_not_confirmed=57754, basic_filters_failed=26698, retest_out_of_zone=2662, h1_break_not_confirmed=2380, regime_blocked=2361, long_break_volume_thin=2223, reclaim_hold_failed=1189, long_acceptance_not_held=492, ema_alignment_reject=164, wick_quality_failed=121, whipsaw_flip=99, missing_fvg_or_orderblock=35
- **EVAL::STANDARD** (total=78000): momentum_reject=23505, adx_reject=17405, basic_filters_failed=14396, macd_reject=10219, sweeps_not_detected=6529, ema_alignment_reject=3617, htf_poi_unanchored=2007, invalid_sl_geometry=178, rsi_reject=107, mtf_reject=37
- **EVAL::TREND_PULLBACK** (total=83883): h1_trend_not_aligned=28316, basic_filters_failed=14144, h1_pullback_not_confirmed=14106, ema_alignment_reject=12305, ema_not_tested_prev=5230, no_ema_reclaim_close=4140, body_conviction_fail=2346, rsi_reject=1580, prev_already_below_emas=723, no_prev_low_break=429, prev_already_above_emas=187, no_prev_high_break=145, momentum_flat=101, missing_fvg_or_orderblock=56, ema21_not_tagged=55, momentum_reject=20
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=99267): breakout_not_found=48500, basic_filters_failed=31001, move_not_fresh=14368, breakout_stale=3617, retest_proximity_failed=1375, volume_spike_missing=389, missing_fvg_or_orderblock=9, move_exhausted=8
- **EVAL::WHALE_MOMENTUM** (total=84439): momentum_reject=70459, recent_ticks_insufficient=9238, basic_filters_failed=4742

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=44): execution:overextended=44
- **DIVERGENCE_CONTINUATION** (total=237): setup_compat:regime_VOLATILE_UNSUITABLE=204, execution:overextended=21, setup_compat:regime_BREAKOUT_EXPANSION=12
- **FAILED_AUCTION_RECLAIM** (total=1461): execution:overextended=625, setup_compat:regime_STRONG_TREND=497, context_floor=339
- **FUNDING_EXTREME_SIGNAL** (total=380): execution:trigger_not_confirmed=379, context_floor=1
- **LIQUIDATION_REVERSAL** (total=31): execution:trigger_not_confirmed=31
- **LIQUIDITY_SWEEP_REVERSAL** (total=7151): execution:trigger_not_confirmed=3583, execution:overextended=1857, setup_compat:regime_STRONG_TREND=1711
- **MA_CROSS_TREND_SHIFT** (total=11): setup_compat:regime_DIRTY_RANGE=6, execution:trigger_not_confirmed=2, setup_compat:regime_CLEAN_RANGE=2, execution:overextended=1
- **MEAN_REVERT** (total=4410): setup_compat:regime_STRONG_TREND=2501, setup_compat:regime_WEAK_TREND=1242, execution:overextended=661, entry_quality=6
- **MOVER_AVWAP_SCALP** (total=1842): execution:overextended=1113, entry_quality=387, execution:trigger_not_confirmed=342
- **MOVER_TREND_PULLBACK** (total=14159): execution:trigger_not_confirmed=7054, execution:overextended=5037, entry_quality=2068
- **RANGE_FADE** (total=4141): setup_compat:regime_STRONG_TREND=1787, setup_compat:regime_WEAK_TREND=1520, execution:overextended=407, setup_compat:regime_VOLATILE_UNSUITABLE=393, context_edge=34
- **TREND_PULLBACK_EMA** (total=1740): setup_compat:regime_CLEAN_RANGE=1113, setup_compat:regime_DIRTY_RANGE=503, entry_quality=83, setup_compat:regime_VOLATILE_UNSUITABLE=41
- **VOLUME_SURGE_BREAKOUT** (total=3): execution:overextended=3

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 272085 | 49.8% |
| QUIET | 103453 | 19.0% |
| TRENDING_UP | 78650 | 14.4% |
| TRENDING_DOWN | 77487 | 14.2% |
| VOLATILE | 14215 | 2.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **231**
- Average confidence gap to threshold: **14.37** (samples=231) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=46, DOTUSDT=29, TAOUSDT=18, SOLUSDT=11, XLMUSDT=10, BCHUSDT=10, PIEVERSEUSDT=9, QNTUSDT=8, ERAUSDT=8, UAIUSDT=8

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 280 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 16 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 54 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 215 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 16 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 29 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 23 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 72 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 7 |
| MEAN_REVERT | filtered | min_confidence | 216 |
| MEAN_REVERT | kept | min_confidence_pass | 48 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 1152 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 20 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 784 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2765 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 18 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4262 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 180 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 160 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 170 |
| SR_FLIP_RETEST | filtered | min_confidence | 16 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 38 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 86 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 175 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 94 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 20 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 296 | 52.85 | 63.85 | 11.00 | 19.88 | 19.51 | 18.57 | 1.17 | 15.50 |
| DIVERGENCE_CONTINUATION | kept | 54 | 68.23 | 65.00 | -3.23 | 20.85 | 19.88 | 17.92 | 1.56 | 4.46 |
| FAILED_AUCTION_RECLAIM | filtered | 231 | 47.95 | 62.79 | 14.84 | 20.75 | 19.46 | 20.00 | 2.10 | 7.17 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.50 | 65.00 | -1.50 | 20.90 | 19.40 | 20.00 | 3.50 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 6.40 | 65.00 | 58.60 | 21.20 | 14.00 | 17.00 | 5.00 | 46.60 |
| LIQUIDATION_REVERSAL | filtered | 29 | 66.73 | 10.00 | -56.73 | 21.76 | 8.00 | 19.09 | 5.31 | 1.66 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 23 | 52.73 | 65.00 | 12.27 | 19.73 | 19.95 | 17.00 | 2.78 | 9.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 72 | 68.75 | 65.00 | -3.75 | 22.13 | 17.40 | 18.13 | 1.89 | 0.50 |
| MA_CROSS_TREND_SHIFT | kept | 7 | 68.54 | 65.00 | -3.54 | 20.30 | 18.44 | 15.80 | 0.00 | 1.47 |
| MEAN_REVERT | filtered | 216 | 50.09 | 65.00 | 14.91 | 19.63 | 14.20 | 14.60 | 0.00 | 19.64 |
| MEAN_REVERT | kept | 48 | 67.30 | 65.00 | -2.30 | 20.55 | 14.00 | 15.10 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 1176 | 53.28 | 64.37 | 11.09 | 21.12 | 17.20 | 15.80 | 3.57 | 13.21 |
| MOVER_AVWAP_SCALP | kept | 784 | 78.79 | 65.00 | -13.79 | 20.69 | 16.39 | 15.80 | 4.40 | 3.69 |
| MOVER_TREND_PULLBACK | filtered | 2783 | 55.70 | 63.85 | 8.15 | 19.74 | 18.42 | 15.80 | 4.17 | 18.22 |
| MOVER_TREND_PULLBACK | kept | 4262 | 76.19 | 65.00 | -11.19 | 20.06 | 18.52 | 15.80 | 4.39 | 1.90 |
| QUIET_COMPRESSION_BREAK | filtered | 340 | 51.19 | 64.76 | 13.57 | 21.70 | 19.42 | 20.00 | 0.00 | 7.81 |
| QUIET_COMPRESSION_BREAK | kept | 170 | 72.24 | 65.00 | -7.24 | 22.30 | 19.46 | 20.00 | 0.00 | 0.97 |
| SR_FLIP_RETEST | filtered | 16 | 58.56 | 65.00 | 6.44 | 20.40 | 20.00 | 18.58 | 2.41 | 12.06 |
| SR_FLIP_RETEST | kept | 38 | 68.90 | 65.00 | -3.90 | 20.31 | 20.00 | 15.20 | 2.64 | 1.05 |
| TREND_PULLBACK_EMA | filtered | 86 | 56.95 | 64.77 | 7.82 | 19.47 | 19.81 | 17.81 | 5.20 | 19.71 |
| TREND_PULLBACK_EMA | kept | 175 | 77.12 | 65.00 | -12.12 | 21.22 | 19.57 | 18.03 | 4.95 | 3.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 94 | 49.09 | 63.67 | 14.58 | 19.34 | 17.80 | 20.00 | 4.31 | 16.75 |
| VOLUME_SURGE_BREAKOUT | kept | 20 | 76.15 | 65.00 | -11.15 | 22.09 | 17.57 | 20.00 | 5.05 | 2.85 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 296 | 52.85 | 21.35 | 15.47 | 5.10 | 12.86 | 5.13 | 8.10 | 1.17 |
| DIVERGENCE_CONTINUATION | kept | 54 | 68.23 | 24.26 | 15.04 | 6.39 | 12.80 | 5.12 | 8.14 | 1.56 |
| FAILED_AUCTION_RECLAIM | filtered | 231 | 47.95 | 22.51 | 17.72 | 4.66 | 12.86 | 6.10 | 4.16 | 2.10 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.50 | 17.00 | 18.00 | 9.00 | 9.00 | 5.00 | 5.00 | 3.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 6.40 | 25.00 | 8.00 | 6.00 | 9.00 | 10.00 | 5.00 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 29 | 66.73 | 25.00 | 8.00 | 12.62 | 8.00 | 5.62 | 6.93 | 5.31 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 23 | 52.73 | 23.09 | 15.74 | 3.91 | 13.13 | 4.91 | 7.34 | 2.78 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 72 | 68.75 | 22.83 | 14.89 | 4.50 | 11.50 | 6.85 | 6.83 | 1.89 |
| MA_CROSS_TREND_SHIFT | kept | 7 | 68.54 | 19.29 | 14.00 | 7.29 | 14.00 | 7.07 | 8.37 | 0.00 |
| MEAN_REVERT | filtered | 216 | 50.09 | 17.49 | 15.61 | 13.21 | 10.72 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 48 | 67.30 | 17.00 | 14.00 | 12.00 | 13.00 | 5.00 | 6.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 1176 | 53.28 | 19.16 | 18.03 | 11.54 | 13.41 | 6.90 | 5.36 | 3.57 |
| MOVER_AVWAP_SCALP | kept | 784 | 78.79 | 19.83 | 18.05 | 12.38 | 14.51 | 6.37 | 7.95 | 4.40 |
| MOVER_TREND_PULLBACK | filtered | 2783 | 55.70 | 18.32 | 18.06 | 7.87 | 12.88 | 6.37 | 8.70 | 4.17 |
| MOVER_TREND_PULLBACK | kept | 4262 | 76.19 | 19.22 | 18.01 | 8.03 | 12.96 | 6.47 | 9.16 | 4.39 |
| QUIET_COMPRESSION_BREAK | filtered | 340 | 51.19 | 19.80 | 15.88 | 12.12 | 14.13 | 6.73 | 4.76 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 170 | 72.24 | 17.61 | 16.56 | 12.02 | 14.09 | 5.43 | 8.10 | 0.00 |
| SR_FLIP_RETEST | filtered | 16 | 58.56 | 24.50 | 18.00 | 3.75 | 13.81 | 5.00 | 3.16 | 2.41 |
| SR_FLIP_RETEST | kept | 38 | 68.90 | 22.68 | 11.42 | 8.53 | 13.13 | 5.09 | 6.45 | 2.64 |
| TREND_PULLBACK_EMA | filtered | 86 | 56.95 | 17.94 | 18.00 | 7.50 | 14.24 | 5.41 | 9.07 | 5.20 |
| TREND_PULLBACK_EMA | kept | 175 | 77.12 | 18.79 | 18.00 | 7.54 | 14.58 | 7.02 | 9.44 | 4.95 |
| VOLUME_SURGE_BREAKOUT | filtered | 94 | 49.09 | 19.13 | 16.94 | 12.41 | 13.52 | 5.67 | 6.31 | 4.31 |
| VOLUME_SURGE_BREAKOUT | kept | 20 | 76.15 | 20.20 | 17.60 | 12.00 | 11.15 | 5.00 | 8.00 | 5.05 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 296 | 52.85 | 0.00 | 0.00 | 2.45 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | **3.18** |
| DIVERGENCE_CONTINUATION | kept | 54 | 68.23 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| FAILED_AUCTION_RECLAIM | filtered | 231 | 47.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 66.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 6.40 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| LIQUIDATION_REVERSAL | filtered | 29 | 66.73 | 0.00 | 0.00 | 1.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.66** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 23 | 52.73 | 0.00 | 0.00 | 1.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.04** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 72 | 68.75 | 0.00 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.51** |
| MA_CROSS_TREND_SHIFT | kept | 7 | 68.54 | 0.00 | 0.00 | 0.00 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **1.03** |
| MEAN_REVERT | filtered | 216 | 50.09 | 0.00 | 0.00 | 2.87 | 0.00 | 4.83 | 0.00 | 0.00 | 0.00 | **7.70** |
| MEAN_REVERT | kept | 48 | 67.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 1176 | 53.28 | 0.26 | 0.00 | 0.62 | 0.00 | 3.36 | 0.00 | 0.00 | 2.20 | **6.44** |
| MOVER_AVWAP_SCALP | kept | 784 | 78.79 | 0.00 | 0.00 | 0.21 | 0.00 | 0.71 | 0.04 | 0.00 | 1.11 | **2.07** |
| MOVER_TREND_PULLBACK | filtered | 2783 | 55.70 | 0.00 | 0.00 | 2.35 | 0.00 | 0.29 | 0.03 | 0.00 | 0.06 | **2.73** |
| MOVER_TREND_PULLBACK | kept | 4262 | 76.19 | 0.00 | 0.00 | 0.25 | 0.00 | 0.28 | 0.01 | 0.00 | 0.00 | **0.54** |
| QUIET_COMPRESSION_BREAK | filtered | 340 | 51.19 | 0.00 | 0.00 | 0.04 | 0.00 | 0.85 | 0.26 | 0.00 | 2.94 | **4.09** |
| QUIET_COMPRESSION_BREAK | kept | 170 | 72.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.03** |
| SR_FLIP_RETEST | filtered | 16 | 58.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.62 | 0.00 | 5.62 | **6.24** |
| SR_FLIP_RETEST | kept | 38 | 68.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 86 | 56.95 | 0.00 | 0.00 | 2.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.66** |
| TREND_PULLBACK_EMA | kept | 175 | 77.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **0.07** |
| VOLUME_SURGE_BREAKOUT | filtered | 94 | 49.09 | 0.00 | 0.00 | 1.82 | 0.00 | 0.00 | 0.00 | 0.00 | 1.56 | **3.38** |
| VOLUME_SURGE_BREAKOUT | kept | 20 | 76.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **172866 held of 722508 seen** across 21 strategies; 3903 cells past the sample floor; **2045 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47044 | 696/46348/0 | 45% | -0.15 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.40R) |
| MOVER_AVWAP_SCALP | 22675 | 187/22488/0 | 43% | -0.22 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 13076 | 164/12912/0 | 45% | -0.12 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 12899 | 153/12746/0 | 38% | -0.27 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11275 | 55/11220/0 | 37% | -0.31 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 9536 | 107/9429/0 | 36% | -0.46 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| SHADOW_MEAN_REVERT | 7865 | 0/0/7865 | 43% | -0.08 | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (+0.79R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.92R) |
| QUIET_COMPRESSION_BREAK | 7800 | 417/7383/0 | 48% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_RANGE_FADE | 7407 | 0/0/7407 | 36% | -0.12 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.32R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_FUNDING_FADE | 6783 | 0/0/6783 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| SR_FLIP_RETEST | 5201 | 17/5184/0 | 47% | -0.25 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 4983 | 64/4919/0 | 35% | -0.35 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| FUNDING_EXTREME_SIGNAL | 3796 | 2/3794/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3619 | 0/3619/0 | 32% | -0.33 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2182 | 6/2176/0 | 40% | -0.24 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1583 | 0/0/1583 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 180 | 32/148/0 | 42% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 56 | 2/54/0 | 43% | +0.14 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 328 | 27% / -0.58R | 328 | 53% / -0.09R | +0.49 | **ATR** |
| TREND_PULLBACK_EMA | 1037 | 37% / -0.38R | 1037 | 50% / -0.09R | +0.29 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1483 | 42% / -0.37R | 1483 | 57% / -0.12R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 518 | 42% / -0.33R | 518 | 47% / -0.18R | +0.15 | **ATR** |
| MOVER_AVWAP_SCALP | 2340 | 44% / -0.17R | 2340 | 51% / -0.05R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 56 | 41% / -0.20R | 56 | 45% / -0.08R | +0.13 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 195 | 37% / -0.18R | 195 | 47% / -0.06R | +0.12 | **ATR** |
| RANGE_FADE | 116 | 38% / -0.15R | 116 | 46% / -0.04R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1348 | 41% / -0.21R | 1348 | 43% / -0.11R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 8550 | 49% / -0.12R | 8550 | 54% / -0.02R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1542 | 47% / -0.12R | 1542 | 53% / -0.06R | +0.06 | **ATR** |
| MEAN_REVERT | 379 | 45% / -0.22R | 379 | 43% / -0.24R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1364 | 47% / -0.13R | 1364 | 47% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11461 | 28% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2340 | 48% | -0.05R | 233 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 124 | 48% | -0.06R | 67 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1715 | 39% / -0.16R | +0.85 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1365 | 32% / -0.27R | +0.80 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2876 | 35% / -0.23R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10437 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1791 | 37% / -0.12R | +0.16 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1313 | 37% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1124 | 32% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 285 | 31% / -0.35R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 431 | 32% / -0.15R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 318 | 45% / -0.14R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 85 | 42% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 465 | 32% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 86 | 28% / -0.40R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×524]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 296/6) (sustained 296 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 296/6) (sustained 296 cycles)
- **ALERT** `tuned_variants` — 689 non-stamps — atr_arm_uncomputable=689 (seen=12151 stamped=966 skipped=10496) (streak 288/6) (sustained 288 cycles)
- **ALERT** `auto_dispatch` — 61 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=61) (streak 276/3) (sustained 276 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 34580448 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 16 arms current, none stalled; covering 2063/2063 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +2 / upstream +3 | 0 |
| atr_trail_live_arms | ok | 32 arms current, none stalled; covering 1066/1066 signals (100%) | 0 |
| auto_dispatch | violating | 61 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=61) (streak 276/3) | 276 |
| binance_ip_weight | ok | peak 252/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 77959.90 | 0 |
| candle_coverage | ok | 84/84 symbols with ≥20 15m candles, 84/84 updated within 45m [fresh=84; 75 Tier-1 futures + 9 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 336 dup bars, 0 undedupable; ws 0 out-of-order, 237 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 38 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +48 / upstream +33 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1600/1619 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | ok | 104 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1596/1615 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 13011042 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 296/6) | 296 |
| emission_controller | ok | last cycle 1s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×524]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 296/6) | 296 |
| entry_quality_effective | ok | 12147 evaluated, 4013 suppressed, 6015 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,317 reads/day of 50,000 [engine 1,291, signing 26]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1354 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +8 / upstream +418 | 0 |
| indicator_cache_key | ok | 105983 frozen value(s) avoided; 425195 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.36R over n=4919 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +28 / upstream +418 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 9 held, 9 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2178 rows held, 3329855 evicted (sampled: execution:trigger_not_confirmed 298/1174838, execution:overextended 298/1043734, setup_compat:regime_STRONG_TREND 297/565926) | 0 |
| price_action_lane | ok | 752516 evaluated, 877 emitted; layer1 877 stamped / 0 blind; cooldown=111534, delta_opposed=65947, no_footprint=266663, no_opposing_target=853, no_sweep=246208, rr_below_floor=60434 | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.24R over n=2176 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +63 / upstream +418 | 0 |
| sar_alignment_crosscheck | ok | 605/18125 disagreed (3.3%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +418 | 0 |
| sar_hold_arm | ok | 1861 held arms settled, 139 unscored, 32 still walking (27 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 10/50 unfetchable (20%); top cause: gap or duplicate bar in the 15m window; symbols: ARIAUSDT, BMTUSDT, LSKUSDT, WLFIUSDT, XMRUSDT | 0 |
| sar_live_arms | ok | 32 arms current, none stalled; covering 1065/1065 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 37 still mid-window | 0 |
| scan_cycle | ok | last 6.39s, worst 146.61s over 9507 lifetime cycles; lifetime 168 over 60s, 8 over 120s (plus 1/1 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 11.76s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 338331 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 48s ago (3.28s to run, worst 126.64s), 716 overrun(s) of 6619 cycles, TTL 900s; slowest signals=8.61s, user_positions=3.95s, tickers=3.2s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=52, gate reads=0, withheld=52) | 0 |
| staleness_v2_shadow | ok | output +1 / upstream +1 | 0 |
| strategy_edge | ok | output +68 / upstream +418 | 0 |
| structural_snap | ok | 6000/6000 measured, 33 blind, 0 levels moved (refusals: redetect_cooldown=1911) | 0 |
| structural_veto_lane | ok | 2629 stamped; 0 with no readable level book, 55 with clear air ahead, 2111 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +418 / upstream +33 | 0 |
| tuned_variants | violating | 689 non-stamps — atr_arm_uncomputable=689 (seen=12151 stamped=966 skipped=10496) (streak 288/6) | 288 |
| unlock_shorts | ok | 13 open, 45 scheduled, calendar 18.3h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 67 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2499866`
- `Path funnel` emissions: `70`
- `Regime distribution` emissions: `70`
- `QUIET_SCALP_BLOCK` events: `231`
- `confidence_gate` events: `10922`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **11**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 8616 | 8616 | 8616 | 0 |
| futures_liq | 10 | 3648 | 9059 | 18739 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=424805] state[populated=424805] buckets[many=424805] sources[none] quality[none]
- funding_rate: presence[absent=38136, present=386669] state[empty=38136, populated=386669] buckets[few=386669, none=38136] sources[none] quality[none]
- liquidation_clusters: presence[absent=224653, present=200152] state[empty=224653, populated=200152] buckets[few=161436, none=224653, some=38716] sources[none] quality[none]
- oi_snapshot: presence[absent=38136, present=386669] state[empty=38136, populated=386669] buckets[few=236, many=385007, none=38136, some=1426] sources[none] quality[none]
- order_book: presence[absent=119993, present=304812] state[populated=304812, unavailable=119993] buckets[few=304812, none=119993] sources[book_ticker=304812, unavailable=119993] quality[none=119993, top_of_book_only=304812]
- orderblocks: presence[absent=424805] state[empty=424805] buckets[none=424805] sources[measured_dark=424805] quality[none]
- recent_ticks: presence[present=424805] state[populated=424805] buckets[many=424805] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.4636740684509277` sec
- Median create→first breach: `6286.901384949684` sec
- Median create→terminal: `6286.901427030563` sec
- Median first breach→terminal: `6.54458999633789e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.799999999999996 | 0.9962177293304122 | 0.8981968792829025 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.8624992057608765 | 1.0301913521513906 | 0.8372223315209201 | 0 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.4489579934975647 | 2.5546893635019816 | 0.8525221792709236 | 0 | 3 |
| MOVER_TREND_PULLBACK | 27 | 27 | 3.1537720404387746 | 3.0 | 1.0958115294232904 | 16 | 10 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 1.2412751773725241 | 1.3842301454919752 | 0.8819936530033072 | 0 | 10 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | -0.2795 | 19368.482418060303 | 19369.56485891342 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.8625 | 6236.326898097992 | 6236.326922178268 |
| MOVER_AVWAP_SCALP | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 2.1477 | 42486.085063934326 | 42486.08513402939 |
| MOVER_TREND_PULLBACK | 27 | 27 | 14.8 | 55.6 | 14.8 | 0.0 | -0.7211 | 3585.186898946762 | 3585.186948776245 |
| QUIET_COMPRESSION_BREAK | 12 | 12 | 41.7 | 25.0 | 41.7 | 0.0 | 0.4257 | 22094.56889653206 | 22096.659853100777 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 726 | 2 | 485 | 0.0 | 0.0 | None | None | 241 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2072 | 28 | 1703 | 0.0 | 0.0 | None | None | 369 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `58`
- Gating Δ: `26275`
- No-generation Δ: `530954`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.2109, "current_avg_pnl": -0.2795, "current_win_rate": 33.3, "previous_avg_pnl": -0.4904, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.1477, "current_avg_pnl": 2.1477, "current_win_rate": 66.7, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.3278, "current_avg_pnl": -0.7211, "current_win_rate": 14.8, "previous_avg_pnl": 0.6067, "previous_win_rate": 16.7, "win_rate_delta": -1.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.6302, "current_avg_pnl": 0.4257, "current_win_rate": 41.7, "previous_avg_pnl": 2.0559, "previous_win_rate": 80.0, "win_rate_delta": -38.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 98, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MOVER_AVWAP_SCALP**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
