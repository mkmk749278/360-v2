# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `26` sec (warning=False)
- Latest performance record age: `9266` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 43 | 43 | 33 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5645 | 5645 | 5252 | 13 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 38258 | 38267 | 6 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 34850 | 34853 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 34637 | 33268 | 1573 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 34871 | 34655 | 249 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 35034 | 34989 | 69 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 31221 | 31228 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 34909 | 34918 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 34927 | 34334 | 945 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 40459 | 42637 | 229 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 38274 | 34771 | 5646 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 34942 | 34946 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 34855 | 34868 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 34614 | 34528 | 107 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 35287 | 34495 | 1057 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 34500 | 34526 | 56 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 30696 | 29749 | 1064 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 30817 | 30586 | 273 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 38239 | 38253 | 1 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 31230 | 31239 | 10 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 834 | 834 | 542 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 282 | 282 | 105 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4446 | 4446 | 4301 | 16 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 5 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2734 | 2734 | 2182 | 5 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 538 | 538 | 217 | 30 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 14298 | 14298 | 8050 | 213 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 756 | 756 | 410 | 28 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 2372 | 2372 | 2049 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 212 | 212 | 111 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 980 | 980 | 860 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 11 | 11 | 0 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 599 | 599 | 32 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=38267): breakout_not_found=21301, basic_filters_failed=10640, move_not_fresh=4245, breakout_stale=1634, retest_proximity_failed=306, volume_spike_missing=93, move_exhausted=36, ema_alignment_reject=12
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=34853): cls_disabled_merged_into_lsr=34853
- **EVAL::DIVERGENCE_CONTINUATION** (total=33268): cvd_divergence_failed=14068, basic_filters_failed=9140, h1_trend_not_aligned=6208, ema_alignment_reject=2766, retest_proximity_failed=652, missing_fvg_or_orderblock=260, regime_blocked=174
- **EVAL::FAILED_AUCTION_RECLAIM** (total=34655): auction_not_detected=22544, basic_filters_failed=8954, regime_blocked=1316, reclaim_hold_failed=1038, tail_too_small=791, rsi_reject=12
- **EVAL::FUNDING_EXTREME** (total=34989): funding_not_extreme=24015, basic_filters_failed=9166, ema_alignment_reject=851, missing_funding_rate=514, rsi_reject=243, cvd_divergence_failed=99, momentum_reject=83, missing_fvg_or_orderblock=18
- **EVAL::LIQUIDATION_REVERSAL** (total=31228): cascade_threshold_not_met=21769, basic_filters_failed=9144, rsi_reject=158, cvd_divergence_failed=146, missing_fvg_or_orderblock=8, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=34918): no_ma_cross=25195, basic_filters_failed=9150, ma_cross_htf_misaligned=353, ma_cross_cooldown=220
- **EVAL::MEAN_REVERT** (total=34334): no_extension=28893, basic_filters_failed=5441
- **EVAL::MOVER_AVWAP_SCALP** (total=42637): no_avwap_tag=15853, no_mover_leg=12122, basic_filters_failed=10760, avwap_slope_against=2418, avwap_reclaim_no_volume=873, no_avwap_reclaim=598, anchor_too_recent=13
- **EVAL::MOVER_TREND_PULLBACK** (total=34771): mover_run_too_small=15609, basic_filters_failed=10683, no_reclaim=7407, no_pullback_tag=1002, insufficient_candles=70
- **EVAL::OPENING_RANGE_BREAKOUT** (total=34946): feature_disabled=34946
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=34868): regime_blocked=21723, breakout_not_found=8947, basic_filters_failed=2527, adx_reject=1617, ema_alignment_reject=54
- **EVAL::QUIET_COMPRESSION_BREAK** (total=34528): regime_blocked=14393, compression_not_detected=10139, basic_filters_failed=6420, breakout_not_detected=3285, volume_confirmation_failed=263, missing_fvg_or_orderblock=20, rsi_reject=8
- **EVAL::RANGE_FADE** (total=34495): no_range_edge=29049, basic_filters_failed=5446
- **EVAL::SR_FLIP_RETEST** (total=34526): flip_close_not_confirmed=22604, basic_filters_failed=8937, regime_blocked=1304, retest_out_of_zone=591, long_break_volume_thin=454, h1_break_not_confirmed=420, reclaim_hold_failed=162, wick_quality_failed=19, ema_alignment_reject=13, long_acceptance_not_held=11, whipsaw_flip=9, missing_fvg_or_orderblock=2
- **EVAL::STANDARD** (total=29749): momentum_reject=10092, adx_reject=6341, basic_filters_failed=4358, sweeps_not_detected=4109, macd_reject=2134, ema_alignment_reject=1900, htf_poi_unanchored=736, rsi_reject=42, invalid_sl_geometry=37
- **EVAL::TREND_PULLBACK** (total=30586): h1_trend_not_aligned=7947, ema_alignment_reject=4974, basic_filters_failed=4830, h1_pullback_not_confirmed=4282, no_ema_reclaim_close=2630, ema_not_tested_prev=2232, body_conviction_fail=1385, rsi_reject=1160, regime_blocked=316, prev_already_below_emas=296, no_prev_low_break=231, prev_already_above_emas=127, no_prev_high_break=82, momentum_flat=56, ema21_not_tagged=19, momentum_reject=13, missing_fvg_or_orderblock=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=38253): breakout_not_found=21958, basic_filters_failed=10636, move_not_fresh=3613, breakout_stale=1360, retest_proximity_failed=477, volume_spike_missing=165, move_exhausted=24, missing_fvg_or_orderblock=17, ema_alignment_reject=3
- **EVAL::WHALE_MOMENTUM** (total=31239): momentum_reject=20738, recent_ticks_insufficient=8950, basic_filters_failed=1551

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=23): execution:overextended=13, context_floor=10
- **DIVERGENCE_CONTINUATION** (total=145): setup_compat:regime_VOLATILE_UNSUITABLE=140, setup_compat:regime_BREAKOUT_EXPANSION=5
- **FAILED_AUCTION_RECLAIM** (total=348): execution:overextended=166, setup_compat:regime_STRONG_TREND=101, context_floor=52, setup_compat:regime_VOLATILE_UNSUITABLE=29
- **FUNDING_EXTREME_SIGNAL** (total=238): execution:trigger_not_confirmed=236, context_floor=2
- **LIQUIDITY_SWEEP_REVERSAL** (total=1153): execution:overextended=440, execution:trigger_not_confirmed=375, setup_compat:regime_STRONG_TREND=338
- **MA_CROSS_TREND_SHIFT** (total=13): setup_compat:regime_CLEAN_RANGE=6, setup_compat:regime_DIRTY_RANGE=4, execution:overextended=2, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=1664): setup_compat:regime_STRONG_TREND=785, setup_compat:regime_WEAK_TREND=717, execution:overextended=154, entry_quality=8
- **MOVER_AVWAP_SCALP** (total=413): execution:overextended=363, entry_quality=28, execution:trigger_not_confirmed=22
- **MOVER_TREND_PULLBACK** (total=7929): execution:overextended=4193, execution:trigger_not_confirmed=2954, entry_quality=782
- **QUIET_COMPRESSION_BREAK** (total=8): execution:trigger_not_confirmed=8
- **RANGE_FADE** (total=1737): setup_compat:regime_WEAK_TREND=584, setup_compat:regime_STRONG_TREND=510, execution:overextended=359, setup_compat:regime_VOLATILE_UNSUITABLE=219, context_edge=49, setup_compat:regime_BREAKOUT_EXPANSION=16
- **TREND_PULLBACK_EMA** (total=815): setup_compat:regime_CLEAN_RANGE=582, setup_compat:regime_DIRTY_RANGE=176, setup_compat:regime_VOLATILE_UNSUITABLE=30, entry_quality=27
- **WHALE_MOMENTUM** (total=484): execution:trigger_not_confirmed=484

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 62100 | 32.1% |
| QUIET | 47377 | 24.5% |
| TRENDING_DOWN | 37571 | 19.4% |
| TRENDING_UP | 35606 | 18.4% |
| VOLATILE | 10955 | 5.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **138**
- Average confidence gap to threshold: **10.89** (samples=138) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=20, SOLUSDT=19, DOTUSDT=14, TRXUSDT=11, BNBUSDT=11, DOGEUSDT=9, BCHUSDT=9, TRUMPUSDT=7, TAOUSDT=5, 1000PEPEUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 96 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 70 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 36 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 12 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 8 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 38 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MEAN_REVERT | filtered | min_confidence | 9 |
| MEAN_REVERT | kept | min_confidence_pass | 17 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 23 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 173 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 887 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 16 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2861 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 93 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 34 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 217 |
| SR_FLIP_RETEST | filtered | min_confidence | 7 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 20 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 23 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 57 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 11 |
| WHALE_MOMENTUM | filtered | min_confidence | 94 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 20 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 100 | 54.12 | 64.77 | 10.65 | 19.99 | 19.64 | 17.95 | 0.90 | 12.96 |
| DIVERGENCE_CONTINUATION | kept | 70 | 71.89 | 65.00 | -6.89 | 19.76 | 19.98 | 17.11 | 0.71 | -1.10 |
| FAILED_AUCTION_RECLAIM | filtered | 36 | 57.85 | 65.00 | 7.15 | 20.13 | 20.00 | 20.00 | 1.38 | 11.58 |
| FAILED_AUCTION_RECLAIM | kept | 4 | 68.45 | 65.00 | -3.45 | 20.95 | 19.70 | 20.00 | 2.75 | 3.30 |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 48.97 | 65.00 | 16.03 | 21.25 | 14.88 | 17.00 | 3.50 | 11.42 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.00 | 65.00 | 0.00 | 18.80 | 20.00 | 17.00 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 9 | 47.37 | 65.00 | 17.63 | 20.86 | 18.87 | 16.78 | 1.78 | 20.18 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 38 | 68.53 | 65.00 | -3.53 | 20.16 | 17.69 | 17.41 | 1.89 | 0.88 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 51.70 | 65.00 | 13.30 | 21.20 | 18.50 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 9 | 52.42 | 60.00 | 7.58 | 19.97 | 19.40 | 13.50 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 17 | 69.01 | 65.00 | -4.01 | 20.28 | 15.31 | 17.42 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 23 | 57.37 | 65.00 | 7.63 | 21.07 | 15.69 | 15.80 | 4.37 | -0.78 |
| MOVER_AVWAP_SCALP | kept | 173 | 76.94 | 65.00 | -11.94 | 20.54 | 16.02 | 15.80 | 4.07 | 0.17 |
| MOVER_TREND_PULLBACK | filtered | 903 | 53.22 | 63.78 | 10.56 | 19.71 | 18.36 | 15.80 | 4.45 | 21.86 |
| MOVER_TREND_PULLBACK | kept | 2861 | 76.82 | 65.00 | -11.82 | 20.38 | 18.52 | 15.80 | 4.40 | 1.31 |
| QUIET_COMPRESSION_BREAK | filtered | 127 | 54.45 | 65.00 | 10.55 | 20.83 | 19.71 | 20.00 | 0.00 | 7.73 |
| QUIET_COMPRESSION_BREAK | kept | 217 | 75.78 | 65.00 | -10.78 | 20.68 | 19.68 | 20.00 | 0.00 | -1.44 |
| SR_FLIP_RETEST | filtered | 11 | 58.07 | 65.00 | 6.93 | 20.95 | 20.00 | 15.20 | 1.55 | 8.09 |
| SR_FLIP_RETEST | kept | 20 | 70.66 | 65.00 | -5.66 | 21.31 | 20.00 | 16.64 | 1.82 | -0.80 |
| TREND_PULLBACK_EMA | filtered | 23 | 56.66 | 65.00 | 8.34 | 20.52 | 19.36 | 18.06 | 5.24 | 16.80 |
| TREND_PULLBACK_EMA | kept | 57 | 78.78 | 65.00 | -13.78 | 20.71 | 19.54 | 17.99 | 4.54 | 0.37 |
| VOLUME_SURGE_BREAKOUT | kept | 11 | 73.53 | 65.00 | -8.53 | 19.12 | 17.16 | 20.00 | 4.41 | 2.73 |
| WHALE_MOMENTUM | filtered | 114 | 56.16 | 65.00 | 8.84 | 23.29 | 15.98 | 17.00 | 0.00 | 12.39 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 100 | 54.12 | 23.80 | 10.80 | 5.58 | 11.59 | 6.21 | 8.19 | 0.90 |
| DIVERGENCE_CONTINUATION | kept | 70 | 71.89 | 23.74 | 16.43 | 4.03 | 13.49 | 5.56 | 9.11 | 0.71 |
| FAILED_AUCTION_RECLAIM | filtered | 36 | 57.85 | 19.00 | 16.00 | 6.00 | 15.17 | 4.42 | 9.13 | 1.38 |
| FAILED_AUCTION_RECLAIM | kept | 4 | 68.45 | 23.00 | 15.00 | 4.50 | 13.50 | 5.25 | 7.75 | 2.75 |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 48.97 | 23.00 | 8.00 | 8.50 | 12.58 | 7.67 | 5.13 | 3.50 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.00 | 25.00 | 8.00 | 6.00 | 14.00 | 5.00 | 7.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 9 | 47.37 | 17.00 | 17.56 | 4.67 | 12.00 | 5.00 | 9.54 | 1.78 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 38 | 68.53 | 22.53 | 15.68 | 4.34 | 11.95 | 6.08 | 6.94 | 1.89 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 51.70 | 25.00 | 14.00 | 3.00 | 11.00 | 5.00 | 8.70 | 0.00 |
| MEAN_REVERT | filtered | 9 | 52.42 | 17.67 | 18.00 | 11.33 | 12.00 | 4.72 | 3.70 | 0.00 |
| MEAN_REVERT | kept | 17 | 69.01 | 24.53 | 14.24 | 6.88 | 12.00 | 6.03 | 5.34 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 23 | 57.37 | 17.00 | 18.00 | 9.13 | 12.83 | 6.22 | 4.82 | 4.37 |
| MOVER_AVWAP_SCALP | kept | 173 | 76.94 | 19.12 | 18.00 | 9.68 | 13.39 | 6.54 | 6.98 | 4.07 |
| MOVER_TREND_PULLBACK | filtered | 903 | 53.22 | 18.27 | 18.06 | 7.71 | 13.35 | 5.52 | 9.30 | 4.45 |
| MOVER_TREND_PULLBACK | kept | 2861 | 76.82 | 19.46 | 18.02 | 8.22 | 13.17 | 5.80 | 9.17 | 4.40 |
| QUIET_COMPRESSION_BREAK | filtered | 127 | 54.45 | 17.69 | 16.93 | 12.61 | 14.12 | 7.16 | 3.95 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 217 | 75.78 | 18.33 | 17.52 | 13.02 | 14.26 | 5.80 | 7.48 | 0.00 |
| SR_FLIP_RETEST | filtered | 11 | 58.07 | 19.91 | 14.36 | 5.18 | 12.09 | 5.00 | 8.07 | 1.55 |
| SR_FLIP_RETEST | kept | 20 | 70.66 | 21.40 | 16.50 | 4.35 | 12.95 | 5.17 | 8.71 | 1.82 |
| TREND_PULLBACK_EMA | filtered | 23 | 56.66 | 17.70 | 18.00 | 7.50 | 14.78 | 7.50 | 7.96 | 5.24 |
| TREND_PULLBACK_EMA | kept | 57 | 78.78 | 18.02 | 18.00 | 8.76 | 14.63 | 7.06 | 9.29 | 4.54 |
| VOLUME_SURGE_BREAKOUT | kept | 11 | 73.53 | 17.00 | 18.00 | 12.27 | 11.55 | 5.00 | 9.39 | 4.41 |
| WHALE_MOMENTUM | filtered | 114 | 56.16 | 19.60 | 16.25 | 6.74 | 11.16 | 6.94 | 7.87 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 100 | 54.12 | 0.00 | 0.00 | 2.48 | 0.00 | 0.94 | 0.00 | 0.00 | 0.00 | **3.42** |
| DIVERGENCE_CONTINUATION | kept | 70 | 71.89 | 0.00 | 0.00 | 0.07 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.17** |
| FAILED_AUCTION_RECLAIM | filtered | 36 | 57.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | **0.80** |
| FAILED_AUCTION_RECLAIM | kept | 4 | 68.45 | 0.00 | 0.00 | 0.00 | 0.00 | 1.80 | 0.00 | 0.00 | 0.00 | **1.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 12 | 48.97 | 0.00 | 0.00 | 2.00 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 9 | 47.37 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | **2.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 38 | 68.53 | 0.00 | 0.00 | 0.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.88** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 51.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 9 | 52.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 17 | 69.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 23 | 57.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 173 | 76.94 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 0.21 | **0.33** |
| MOVER_TREND_PULLBACK | filtered | 903 | 53.22 | 0.00 | 0.00 | 4.48 | 0.00 | 0.72 | 0.00 | 0.00 | 0.08 | **5.28** |
| MOVER_TREND_PULLBACK | kept | 2861 | 76.82 | 0.00 | 0.00 | 0.73 | 0.00 | 0.16 | 0.01 | 0.00 | 0.05 | **0.95** |
| QUIET_COMPRESSION_BREAK | filtered | 127 | 54.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 5.52 | **5.89** |
| QUIET_COMPRESSION_BREAK | kept | 217 | 75.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.70 | **0.77** |
| SR_FLIP_RETEST | filtered | 11 | 58.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 20 | 70.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 23 | 56.66 | 0.00 | 0.00 | 3.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.76** |
| TREND_PULLBACK_EMA | kept | 57 | 78.78 | 0.00 | 0.00 | 0.42 | 0.00 | 0.84 | 0.00 | 0.00 | 0.00 | **1.26** |
| VOLUME_SURGE_BREAKOUT | kept | 11 | 73.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 114 | 56.16 | 0.00 | 0.00 | 0.00 | 0.00 | 2.21 | 0.00 | 0.00 | 0.00 | **2.21** |

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
- Outcomes recorded: **138340 held of 266302 seen** across 21 strategies; 3127 cells past the sample floor; **1166 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 32773 | 225/32548/0 | 51% | -0.04 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17229 | 24/17205/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16586 | 1/16585/0 | 48% | -0.17 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11991 | 4/11987/0 | 45% | -0.11 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9637 | 0/9637/0 | 47% | -0.07 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 9228 | 29/9199/0 | 35% | -0.30 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| TREND_PULLBACK_EMA | 5622 | 2/5620/0 | 48% | -0.22 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_MEAN_REVERT | 5106 | 0/0/5106 | 43% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.73R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL (-1.03R) |
| LIQUIDITY_SWEEP_REVERSAL | 5001 | 11/4990/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4655 | 0/0/4655 | 38% | +0.02 | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.78R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.28R) |
| MEAN_REVERT | 4387 | 0/4387/0 | 70% | +0.38 | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.32R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.29R) |
| SHADOW_FUNDING_FADE | 4195 | 0/0/4195 | 37% | -0.35 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 3916 | 0/3916/0 | 29% | -0.46 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.44R) |
| VOLUME_SURGE_BREAKOUT | 2553 | 19/2534/0 | 42% | +0.06 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2358 | 4/2354/0 | 32% | -0.45 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.33R) |
| WHALE_MOMENTUM | 1834 | 0/1834/0 | 46% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.86R) |
| SHADOW_CASCADE_REVERSAL | 539 | 0/0/539 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.76R) |
| BREAKDOWN_SHORT | 497 | 9/488/0 | 47% | +0.08 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 73 | 0/73/0 | 85% | +0.69 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 32 | 1/31/0 | 34% | -0.40 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `RANGE_FADE @ ASIA/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.44R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 111 | 35% / -0.40R | 111 | 57% / -0.08R | +0.32 | **ATR** |
| TREND_PULLBACK_EMA | 216 | 44% / -0.28R | 216 | 49% / -0.09R | +0.18 | **ATR** |
| MOVER_AVWAP_SCALP | 583 | 38% / -0.22R | 583 | 42% / -0.11R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 2780 | 46% / -0.20R | 2780 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 912 | 47% / -0.12R | 912 | 53% / -0.05R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 739 | 50% / -0.18R | 739 | 55% / -0.12R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4132 | 51% / -0.07R | 4132 | 54% / -0.01R | +0.06 | **ATR** |
| MEAN_REVERT | 456 | 54% / +0.01R | 456 | 50% / +0.04R | +0.03 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 84 | 40% / -0.02R | 84 | 50% / -0.06R | -0.03 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1517 | 45% / -0.13R | 1517 | 44% / -0.16R | -0.03 | **FIXED** |
| BREAKDOWN_SHORT | 20 | 30% / -0.27R | 20 | 30% / -0.25R | +0.02 | **ATR** |
| WHALE_MOMENTUM | 136 | 52% / -0.24R | 136 | 51% / -0.26R | -0.02 | **FIXED** |
| RANGE_FADE | 250 | 21% / -0.61R | 250 | 22% / -0.59R | +0.02 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2296 | 47% / -0.11R | 2296 | 47% / -0.11R | +0.00 | **ATR** |
| MA_CROSS_TREND_SHIFT | 14 | 29% / -0.27R | 14 | 29% / -0.24R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 9 | 56% / +0.07R | 9 | 56% / -0.01R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 5922 | 30% | -0.13R | 286 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 573 | 40% | -0.12R | 138 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 36 | 56% | -0.02R | 21 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1237 | 28% / -1.67R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 23 | 26% / -0.65R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4918 | 40% / -0.16R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1001 | 32% / -0.56R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 95 | 22% / -0.88R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 751 | 31% / -1.49R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1029 | 36% / -0.14R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 376 | 44% / -0.93R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 129 | 29% / -1.21R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 246 | 30% / -0.54R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 638 | 32% / -0.27R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 17 | 24% / -0.77R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 190 | 44% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 77 | 40% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 7 | 14% / -0.77R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 38 | 47% / -0.29R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 46 · alerting: **4** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 14 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 43/6) (sustained 43 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.40R (bound 0.3) (streak 43/6) (sustained 43 cycles)
- **ALERT** `mean_revert_emission` — 300 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.38R over n=4387, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 18/6) (sustained 18 cycles)
- **ALERT** `tuned_variants` — 20 non-stamps — atr_arm_uncomputable=20 (seen=1457 stamped=178 skipped=1259) (streak 16/6) (sustained 16 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 3774231 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 17 arms current, none stalled; covering 81/81 signals (100%) | 0 |
| auto_dispatch | ok | attempts=4 fanouts=4 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 63515.60 | 0 |
| candle_coverage | ok | 92/94 symbols with ≥20 15m candles, 88/94 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 570 dup bars, 0 undedupable; ws 0 out-of-order, 41 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 14 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 43/6) | 43 |
| context_emission_policy | ok | output +20 / upstream +23 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 255/255 signals (100%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today | 0 |
| dark_resolution | violating | 3 of 62 open dark rows are not being advanced (worst: INXUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 43/120) | 43 |
| dark_sar_arms | ok | no open arms; covering 273/273 signals (100%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 1311630 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.40R (bound 0.3) (streak 43/6) | 43 |
| emission_controller | ok | last cycle 783s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4165 stamps (MEAN_REVERT=328, MOVER_AVWAP_SCALP=133, MOVER_TREND_PULLBACK=3017, RANGE_FADE=364, TREND_PULLBACK_EMA=323), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +7 / upstream +119 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 300 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.38R over n=4387, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 18/6) | 18 |
| mean_revert_path | ok | output +28 / upstream +119 | 0 |
| mover_admission_metadata | ok | 859 symbols known, 157 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3077 rows held, 449511 evicted (sampled: execution:overextended 400/166801, execution:trigger_not_confirmed 400/151688, setup_compat:regime_STRONG_TREND 400/55530) | 0 |
| price_action_lane | ok | 72584 evaluated, 103 emitted; layer1 103 stamped / 0 blind; cooldown=8249, delta_opposed=5372, no_footprint=21464, no_opposing_target=720, no_sweep=32375, rr_below_floor=4301 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | ok | emitted_total=0 context_blocked=4 | 0 |
| range_fade_path | ok | output +12 / upstream +119 | 0 |
| sar_alignment_crosscheck | ok | 114/3990 disagreed (2.9%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +119 | 0 |
| sar_hold_arm | ok | 134 held arms settled, 29 unscored, 17 still walking (14 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 19/95 unfetchable (20%); top cause: gap or duplicate bar in the 15m window; symbols: ADAUSDT, AVAXUSDT, BCHUSDT, BTRUSDT, COTIUSDT +5 more | 0 |
| sar_live_arms | ok | 17 arms current, none stalled; covering 90/90 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 495 records await one (76 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| setup_tf_resolver | ok | 30460 resolutions, 16557 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +100 / upstream +119 | 0 |
| structural_snap | ok | 4038/4038 measured, 16 blind, 0 levels moved (refusals: redetect_cooldown=473) | 0 |
| structural_veto_lane | ok | 614 stamped; 0 with no readable level book, 49 with clear air ahead, 357 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +119 / upstream +23 | 0 |
| tuned_variants | violating | 20 non-stamps — atr_arm_uncomputable=20 (seen=1457 stamped=178 skipped=1259) (streak 16/6) | 16 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `78609`
- `Path funnel` emissions: `23`
- `Regime distribution` emissions: `23`
- `QUIET_SCALP_BLOCK` events: `138`
- `confidence_gate` events: `4837`
- `free_channel_post` events: `19`
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
| futures_liq | 4 | 4937 | 7528 | 7708 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **19**

| Source | Count |
|---|---:|
| signal_close | 16 |
| regime_shift | 2 |
| signal_highlight | 1 |

- By severity: HIGH=19

## Dependency readiness
- cvd: presence[present=156407] state[populated=156407] buckets[many=156356, some=51] sources[none] quality[none]
- funding_rate: presence[absent=19930, present=136477] state[empty=19930, populated=136477] buckets[few=136477, none=19930] sources[none] quality[none]
- liquidation_clusters: presence[absent=94601, present=61806] state[empty=94601, populated=61806] buckets[few=51763, none=94601, some=10043] sources[none] quality[none]
- oi_snapshot: presence[absent=18594, present=137813] state[empty=18594, populated=137813] buckets[few=114, many=137109, none=18594, some=590] sources[none] quality[none]
- order_book: presence[absent=60988, present=95419] state[populated=95419, unavailable=60988] buckets[few=95419, none=60988] sources[book_ticker=95419, unavailable=60988] quality[none=60988, top_of_book_only=95419]
- orderblocks: presence[absent=156407] state[empty=156407] buckets[none=156407] sources[measured_dark=156407] quality[none]
- recent_ticks: presence[present=156407] state[populated=156407] buckets[many=156407] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `24.98958396911621` sec
- Median create→first breach: `4348.582674980164` sec
- Median create→terminal: `4352.688835859299` sec
- Median first breach→terminal: `5.947223901748657` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 5.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 5.3}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 1.6644976287357875 | 2.390372506963784 | 0.6963339914120783 | 0 | 1 |
| MOVER_TREND_PULLBACK | 18 | 18 | 4.654278783188337 | 3.0 | 1.5514262610627791 | 17 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.6645 | 401.9680440425873 | 405.65953302383423 |
| MOVER_TREND_PULLBACK | 18 | 18 | 0.0 | 27.8 | 0.0 | 0.0 | 1.636 | 4351.506141901016 | 4355.072629451752 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 212 | 2 | 111 | 0.0 | 0.0 | None | None | 101 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 980 | 9 | 860 | 0.0 | 0.0 | None | None | 120 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-199`
- Gating Δ: `-21183`
- No-generation Δ: `-547200`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 3.7007, "current_avg_pnl": 1.636, "current_win_rate": 0.0, "previous_avg_pnl": -2.0647, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -8, "geometry_changed_delta": 0, "geometry_preserved_delta": -74, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
