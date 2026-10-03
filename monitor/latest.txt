# Runtime Truth Report

## Executive summary
- Overall health/freshness: **halted_by_breaker**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `714` sec
- ⛔ **HALTED BY LOSS CIRCUIT BREAKER** — reason: 3 consecutive SL hits (max=3); cooldown remaining: 399.0s. This is a deliberate protective pause (not a crash); the stale heartbeat and zero-signal window are expected while halted.

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 533 | 533 | 533 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 19341 | 19341 | 18691 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 116041 | 115972 | 102 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 92479 | 92480 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 92233 | 88334 | 4137 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 92499 | 90875 | 1681 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 92877 | 92638 | 254 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 80586 | 80594 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 92561 | 92584 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 92600 | 90174 | 3405 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 122164 | 128972 | 1119 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 116076 | 103638 | 18482 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 92323 | 92324 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 92480 | 92493 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 92214 | 91986 | 246 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 93581 | 92214 | 1796 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 91642 | 91919 | 270 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 79642 | 73794 | 6189 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 79989 | 79449 | 602 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 116006 | 116024 | 14 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 80595 | 80615 | 7 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7124 | 7124 | 6252 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1034 | 1034 | 584 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 41541 | 41541 | 39966 | 26 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 13 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 12157 | 12157 | 9889 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4464 | 4464 | 3658 | 36 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 62404 | 62404 | 51533 | 203 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 23 | 23 | 23 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 827 | 827 | 751 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 6297 | 6297 | 6163 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1599 | 1599 | 1227 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3982 | 3982 | 3750 | 13 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 244 | 244 | 144 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1115 | 1115 | 1115 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=115972): breakout_not_found=65627, basic_filters_failed=29828, move_not_fresh=14789, breakout_stale=3906, retest_proximity_failed=1424, volume_spike_missing=386, move_exhausted=11, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=92480): cls_disabled_merged_into_lsr=92480
- **EVAL::DIVERGENCE_CONTINUATION** (total=88334): cvd_divergence_failed=32583, h1_trend_not_aligned=26711, basic_filters_failed=19649, ema_alignment_reject=8375, retest_proximity_failed=637, missing_fvg_or_orderblock=372, cvd_insufficient=7
- **EVAL::FAILED_AUCTION_RECLAIM** (total=90875): auction_not_detected=58112, basic_filters_failed=18927, reclaim_hold_failed=7558, tail_too_small=3755, regime_blocked=2517, rsi_reject=6
- **EVAL::FUNDING_EXTREME** (total=92638): funding_not_extreme=69748, basic_filters_failed=19739, ema_alignment_reject=1461, rsi_reject=655, missing_funding_rate=587, cvd_divergence_failed=231, momentum_reject=201, missing_fvg_or_orderblock=16
- **EVAL::LIQUIDATION_REVERSAL** (total=80594): cascade_threshold_not_met=60459, basic_filters_failed=19625, cvd_divergence_failed=277, rsi_reject=226, volume_spike_missing=5, missing_fvg_or_orderblock=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=92584): no_ma_cross=70595, basic_filters_failed=19669, ma_cross_htf_misaligned=1182, ma_cross_cooldown=1138
- **EVAL::MEAN_REVERT** (total=90174): no_extension=75333, basic_filters_failed=14841
- **EVAL::MOVER_AVWAP_SCALP** (total=128972): no_avwap_tag=55725, basic_filters_failed=29988, no_mover_leg=26462, avwap_slope_against=11175, avwap_reclaim_no_volume=3434, no_avwap_reclaim=2154, anchor_too_recent=34
- **EVAL::MOVER_TREND_PULLBACK** (total=103638): mover_run_too_small=40355, basic_filters_failed=29904, no_reclaim=29355, no_pullback_tag=4009, insufficient_candles=15
- **EVAL::OPENING_RANGE_BREAKOUT** (total=92324): feature_disabled=92324
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=92493): regime_blocked=57605, breakout_not_found=26147, basic_filters_failed=6786, adx_reject=1922, ema_alignment_reject=31, rsi_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=91986): regime_blocked=37324, compression_not_detected=36311, basic_filters_failed=12132, breakout_not_detected=5379, volume_confirmation_failed=835, missing_fvg_or_orderblock=5
- **EVAL::RANGE_FADE** (total=92214): no_range_edge=77368, basic_filters_failed=14846
- **EVAL::SR_FLIP_RETEST** (total=91919): flip_close_not_confirmed=60572, basic_filters_failed=18905, long_break_volume_thin=3670, regime_blocked=2510, h1_break_not_confirmed=2346, retest_out_of_zone=2038, reclaim_hold_failed=1231, ema_alignment_reject=299, wick_quality_failed=132, long_acceptance_not_held=88, whipsaw_flip=78, missing_fvg_or_orderblock=50
- **EVAL::STANDARD** (total=73794): momentum_reject=21815, adx_reject=14580, basic_filters_failed=11937, sweeps_not_detected=8591, macd_reject=7637, ema_alignment_reject=7635, htf_poi_unanchored=1433, invalid_sl_geometry=90, rsi_reject=62, mtf_reject=14
- **EVAL::TREND_PULLBACK** (total=79449): h1_trend_not_aligned=29684, ema_alignment_reject=12397, basic_filters_failed=10725, h1_pullback_not_confirmed=10223, ema_not_tested_prev=5452, no_ema_reclaim_close=4801, body_conviction_fail=2432, rsi_reject=1971, prev_already_below_emas=459, prev_already_above_emas=444, no_prev_low_break=355, no_prev_high_break=241, momentum_flat=183, momentum_reject=32, ema21_not_tagged=31, missing_fvg_or_orderblock=19
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=116024): breakout_not_found=66109, basic_filters_failed=29826, move_not_fresh=13634, breakout_stale=4493, retest_proximity_failed=1734, volume_spike_missing=179, missing_fvg_or_orderblock=38, ema_alignment_reject=10, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=80615): momentum_reject=61511, recent_ticks_insufficient=16816, basic_filters_failed=2288

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=86): execution:overextended=86
- **DIVERGENCE_CONTINUATION** (total=837): setup_compat:regime_VOLATILE_UNSUITABLE=721, setup_compat:regime_BREAKOUT_EXPANSION=76, execution:overextended=40
- **FAILED_AUCTION_RECLAIM** (total=2058): setup_compat:regime_STRONG_TREND=1282, execution:overextended=509, context_floor=267
- **FUNDING_EXTREME_SIGNAL** (total=934): execution:trigger_not_confirmed=871, context_floor=63
- **LIQUIDATION_REVERSAL** (total=6): execution:trigger_not_confirmed=6
- **LIQUIDITY_SWEEP_REVERSAL** (total=11647): setup_compat:regime_STRONG_TREND=4437, execution:trigger_not_confirmed=3614, execution:overextended=3596
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_DIRTY_RANGE=5, execution:trigger_not_confirmed=3, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=8345): setup_compat:regime_STRONG_TREND=4026, setup_compat:regime_WEAK_TREND=2531, execution:overextended=1710, entry_quality=78
- **MOVER_AVWAP_SCALP** (total=2394): execution:overextended=1626, execution:trigger_not_confirmed=574, entry_quality=194
- **MOVER_TREND_PULLBACK** (total=24669): execution:trigger_not_confirmed=14076, execution:overextended=9468, entry_quality=1125
- **RANGE_FADE** (total=3693): setup_compat:regime_STRONG_TREND=1545, setup_compat:regime_WEAK_TREND=1343, execution:overextended=567, setup_compat:regime_VOLATILE_UNSUITABLE=238
- **TREND_PULLBACK_EMA** (total=2976): setup_compat:regime_CLEAN_RANGE=2052, setup_compat:regime_DIRTY_RANGE=754, setup_compat:regime_VOLATILE_UNSUITABLE=103, entry_quality=67
- **VOLUME_SURGE_BREAKOUT** (total=79): execution:overextended=79
- **WHALE_MOMENTUM** (total=669): execution:trigger_not_confirmed=669

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 276302 | 39.4% |
| QUIET | 131475 | 18.7% |
| TRENDING_DOWN | 131004 | 18.7% |
| TRENDING_UP | 129549 | 18.5% |
| VOLATILE | 33305 | 4.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **114**
- Average confidence gap to threshold: **13.68** (samples=114) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: 1000SHIBUSDT=12, LTCUSDT=11, SOONUSDT=11, PENGUUSDT=11, DOTUSDT=10, MONUSDT=8, APTUSDT=7, ARKUSDT=6, LITUSDT=6, DASHUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 36 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 81 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 133 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 29 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 66 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 36 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 266 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 28 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 112 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 181 |
| MEAN_REVERT | kept | min_confidence_pass | 11 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 250 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 157 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1599 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 36 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2818 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 5 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | filtered | min_confidence | 64 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 12 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 32 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 9 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 94 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 34 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 36 | 49.07 | 63.33 | 14.26 | 19.06 | 19.54 | 17.08 | 3.39 | 11.68 |
| DIVERGENCE_CONTINUATION | kept | 81 | 75.04 | 65.00 | -10.04 | 20.81 | 19.76 | 17.85 | -0.10 | 0.24 |
| FAILED_AUCTION_RECLAIM | filtered | 162 | 52.00 | 64.21 | 12.21 | 20.36 | 19.17 | 20.00 | 1.93 | 14.75 |
| FAILED_AUCTION_RECLAIM | kept | 66 | 77.98 | 65.00 | -12.98 | 19.82 | 17.06 | 20.00 | 2.58 | 0.02 |
| FUNDING_EXTREME_SIGNAL | filtered | 36 | 45.06 | 63.44 | 18.38 | 20.73 | 14.24 | 17.02 | 2.86 | 7.12 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 294 | 52.16 | 64.19 | 12.03 | 20.36 | 19.20 | 17.89 | 2.04 | 7.57 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 112 | 70.12 | 65.00 | -5.12 | 21.36 | 18.63 | 17.73 | 0.89 | 0.83 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 53.00 | 61.00 | 8.00 | 20.60 | 18.80 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 71.15 | 65.00 | -6.15 | 20.60 | 16.70 | 15.80 | 0.00 | 0.70 |
| MEAN_REVERT | filtered | 181 | 59.07 | 65.00 | 5.93 | 22.69 | 14.21 | 19.15 | 0.00 | 11.62 |
| MEAN_REVERT | kept | 11 | 69.83 | 65.00 | -4.83 | 21.64 | 15.71 | 16.46 | 0.00 | 0.24 |
| MOVER_AVWAP_SCALP | filtered | 250 | 57.88 | 65.00 | 7.12 | 18.76 | 14.21 | 15.80 | 3.00 | 17.22 |
| MOVER_AVWAP_SCALP | kept | 157 | 80.81 | 65.00 | -15.81 | 19.39 | 15.76 | 15.80 | 4.03 | 5.96 |
| MOVER_TREND_PULLBACK | filtered | 1635 | 54.52 | 63.82 | 9.30 | 20.40 | 18.52 | 15.80 | 3.65 | 16.54 |
| MOVER_TREND_PULLBACK | kept | 2818 | 76.71 | 65.00 | -11.71 | 19.88 | 18.51 | 15.80 | 4.54 | 0.68 |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 51.01 | 63.75 | 12.74 | 19.08 | 19.36 | 20.00 | 0.00 | 22.34 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 70.33 | 65.00 | -5.33 | 22.17 | 19.47 | 20.00 | 0.00 | 2.87 |
| SR_FLIP_RETEST | filtered | 76 | 52.24 | 64.42 | 12.18 | 21.37 | 20.00 | 15.58 | 2.34 | 16.25 |
| SR_FLIP_RETEST | kept | 32 | 67.85 | 65.00 | -2.85 | 19.89 | 20.00 | 18.29 | 2.44 | 1.23 |
| TREND_PULLBACK_EMA | filtered | 13 | 54.01 | 65.00 | 10.99 | 20.97 | 20.00 | 17.70 | 4.62 | 4.98 |
| TREND_PULLBACK_EMA | kept | 94 | 78.79 | 65.00 | -13.79 | 20.50 | 19.71 | 16.90 | 4.72 | -1.04 |
| VOLUME_SURGE_BREAKOUT | filtered | 34 | 39.75 | 63.71 | 23.96 | 20.07 | 16.14 | 20.00 | 4.03 | 20.94 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.45 | 65.00 | -4.45 | 17.80 | 14.70 | 20.00 | 4.75 | 3.95 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 36 | 49.07 | 20.56 | 13.56 | 5.00 | 13.22 | 5.00 | 5.86 | 3.39 |
| DIVERGENCE_CONTINUATION | kept | 81 | 75.04 | 22.93 | 15.93 | 9.00 | 13.70 | 5.27 | 9.34 | -0.10 |
| FAILED_AUCTION_RECLAIM | filtered | 162 | 52.00 | 19.47 | 15.88 | 5.87 | 14.38 | 7.14 | 6.27 | 1.93 |
| FAILED_AUCTION_RECLAIM | kept | 66 | 77.98 | 24.39 | 17.94 | 3.09 | 14.02 | 6.08 | 9.91 | 2.58 |
| FUNDING_EXTREME_SIGNAL | filtered | 36 | 45.06 | 25.00 | 8.00 | 3.75 | 14.31 | 7.08 | 6.19 | 2.86 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 294 | 52.16 | 23.59 | 15.25 | 4.77 | 11.64 | 5.38 | 5.22 | 2.04 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 112 | 70.12 | 23.59 | 16.18 | 4.10 | 13.70 | 5.00 | 7.63 | 0.89 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 53.00 | 17.00 | 14.00 | 12.00 | 17.00 | 5.00 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 71.15 | 25.00 | 14.00 | 3.00 | 15.50 | 7.00 | 7.35 | 0.00 |
| MEAN_REVERT | filtered | 181 | 59.07 | 21.24 | 14.71 | 9.36 | 12.93 | 5.00 | 7.41 | 0.00 |
| MEAN_REVERT | kept | 11 | 69.83 | 24.27 | 14.73 | 7.36 | 12.45 | 5.00 | 6.25 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 250 | 57.88 | 18.83 | 18.06 | 14.34 | 14.00 | 5.58 | 4.90 | 3.00 |
| MOVER_AVWAP_SCALP | kept | 157 | 80.81 | 22.48 | 18.41 | 13.09 | 13.83 | 5.99 | 8.95 | 4.03 |
| MOVER_TREND_PULLBACK | filtered | 1635 | 54.52 | 18.32 | 18.00 | 8.30 | 12.55 | 6.23 | 8.22 | 3.65 |
| MOVER_TREND_PULLBACK | kept | 2818 | 76.71 | 19.56 | 18.05 | 7.89 | 13.12 | 6.20 | 8.88 | 4.54 |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 51.01 | 17.25 | 14.62 | 15.00 | 14.47 | 5.84 | 6.17 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 70.33 | 18.33 | 16.67 | 10.50 | 14.00 | 5.75 | 7.95 | 0.00 |
| SR_FLIP_RETEST | filtered | 76 | 52.24 | 22.05 | 16.42 | 5.96 | 13.68 | 5.00 | 5.19 | 2.34 |
| SR_FLIP_RETEST | kept | 32 | 67.85 | 24.50 | 14.25 | 5.53 | 10.53 | 5.25 | 7.61 | 2.44 |
| TREND_PULLBACK_EMA | filtered | 13 | 54.01 | 6.62 | 18.00 | 7.50 | 16.08 | 8.46 | 8.11 | 4.62 |
| TREND_PULLBACK_EMA | kept | 94 | 78.79 | 19.26 | 18.00 | 7.55 | 14.13 | 6.62 | 8.92 | 4.72 |
| VOLUME_SURGE_BREAKOUT | filtered | 34 | 39.75 | 9.74 | 17.88 | 12.00 | 14.09 | 3.82 | 6.63 | 4.03 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.45 | 21.00 | 19.00 | 12.00 | 12.50 | 5.00 | 6.65 | 4.75 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 36 | 49.07 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |
| DIVERGENCE_CONTINUATION | kept | 81 | 75.04 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| FAILED_AUCTION_RECLAIM | filtered | 162 | 52.00 | 0.00 | 0.00 | 3.03 | 0.00 | 0.53 | 0.00 | 0.00 | 0.00 | **3.56** |
| FAILED_AUCTION_RECLAIM | kept | 66 | 77.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 36 | 45.06 | 0.00 | 0.00 | 4.22 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | **4.55** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 294 | 52.16 | 0.00 | 0.00 | 1.00 | 0.00 | 0.37 | 0.07 | 0.00 | 0.00 | **1.44** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 112 | 70.12 | 0.00 | 0.00 | 0.70 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.81** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 53.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 71.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 181 | 59.07 | 0.00 | 0.00 | 1.35 | 0.00 | 5.34 | 0.00 | 0.00 | 0.00 | **6.69** |
| MEAN_REVERT | kept | 11 | 69.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 250 | 57.88 | 0.00 | 0.00 | 0.00 | 0.00 | 4.94 | 0.36 | 0.00 | 2.47 | **7.77** |
| MOVER_AVWAP_SCALP | kept | 157 | 80.81 | 0.00 | 0.00 | 0.18 | 0.00 | 1.15 | 0.10 | 0.00 | 0.25 | **1.68** |
| MOVER_TREND_PULLBACK | filtered | 1635 | 54.52 | 0.14 | 0.00 | 1.99 | 0.00 | 1.78 | 0.02 | 0.00 | 0.11 | **4.04** |
| MOVER_TREND_PULLBACK | kept | 2818 | 76.71 | 0.00 | 0.00 | 0.44 | 0.00 | 0.10 | 0.01 | 0.00 | 0.00 | **0.55** |
| QUIET_COMPRESSION_BREAK | filtered | 32 | 51.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.69 | **1.69** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 70.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 76 | 52.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.52 | **0.52** |
| SR_FLIP_RETEST | kept | 32 | 67.85 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| TREND_PULLBACK_EMA | filtered | 13 | 54.01 | 0.00 | 0.00 | 3.32 | 0.00 | 1.66 | 0.00 | 0.00 | 0.00 | **4.98** |
| TREND_PULLBACK_EMA | kept | 94 | 78.79 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| VOLUME_SURGE_BREAKOUT | filtered | 34 | 39.75 | 0.00 | 0.00 | 8.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.47** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 69.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **128121 held of 416030 seen** across 21 strategies; 2931 cells past the sample floor; **1414 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 41319 | 601/40718/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.16R) |
| MOVER_AVWAP_SCALP | 16569 | 176/16393/0 | 40% | -0.27 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10166 | 116/10050/0 | 40% | -0.24 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 8612 | 53/8559/0 | 50% | -0.04 | NY/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (+1.39R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 7331 | 26/7305/0 | 43% | -0.16 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6502 | 0/0/6502 | 44% | -0.08 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.86R) |
| SHADOW_RANGE_FADE | 5767 | 0/0/5767 | 37% | -0.07 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.63R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| QUIET_COMPRESSION_BREAK | 5390 | 318/5072/0 | 48% | -0.11 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.59R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| LIQUIDITY_SWEEP_REVERSAL | 5316 | 71/5245/0 | 37% | -0.47 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_FUNDING_FADE | 5058 | 0/0/5058 | 34% | -0.40 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2908 | 35/2873/0 | 43% | -0.21 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| VOLUME_SURGE_BREAKOUT | 2335 | 0/2335/0 | 40% | -0.08 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2311 | 2/2309/0 | 32% | -0.45 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| SR_FLIP_RETEST | 2062 | 11/2051/0 | 48% | -0.21 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| RANGE_FADE | 1142 | 4/1138/0 | 42% | -0.34 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1009 | 0/0/1009 | 55% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.19R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 82 | 12/70/0 | 46% | -0.08 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 168 | 27% / -0.57R | 168 | 49% / -0.16R | +0.40 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 594 | 43% / -0.24R | 594 | 56% / -0.03R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 980 | 46% / -0.30R | 980 | 56% / -0.14R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 1369 | 43% / -0.20R | 1369 | 49% / -0.07R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6456 | 49% / -0.12R | 6456 | 54% / -0.02R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 978 | 41% / -0.23R | 978 | 43% / -0.13R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 121 | 37% / -0.15R | 121 | 47% / -0.06R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 198 | 48% / -0.24R | 198 | 51% / -0.16R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 875 | 48% / -0.11R | 875 | 54% / -0.05R | +0.07 | **ATR** |
| MA_CROSS_TREND_SHIFT | 25 | 44% / -0.16R | 25 | 44% / -0.13R | +0.03 | **ATR** |
| RANGE_FADE | 50 | 36% / -0.33R | 50 | 38% / -0.34R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 873 | 46% / -0.15R | 873 | 46% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 217 | 52% / -0.07R | 217 | 51% / -0.07R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9225 | 30% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1369 | 47% | -0.08R | 206 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 75 | 51% | -0.06R | 50 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 850 | 35% / -0.18R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 8273 | 36% / -0.16R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1766 | 34% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 792 | 34% / -0.18R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 971 | 38% / -0.03R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 797 | 37% / -0.15R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 962 | 40% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 178 | 30% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 220 | 29% / -0.62R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 178 | 54% / +0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 38 | 32% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 197 | 31% / -0.49R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 39 | 26% / -0.48R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 11 | 45% / +0.67R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×298]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 51/6) (sustained 51 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 488/6) (sustained 488 cycles)
- **ALERT** `tuned_variants` — 369 non-stamps — atr_arm_uncomputable=369 (seen=8590 stamped=806 skipped=7415) (streak 475/6) (sustained 475 cycles)
- **ALERT** `auto_dispatch` — 89 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=89) (streak 469/3) (sustained 469 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 148092552 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 17 arms current, none stalled; covering 1192/1192 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 36 arms current, none stalled; covering 1124/1124 signals (100%) | 0 |
| auto_dispatch | violating | 89 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=89) (streak 469/3) | 469 |
| binance_ip_weight | ok | peak 12/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 84599.60 | 0 |
| candle_coverage | ok | 84/84 symbols with ≥20 15m candles, 84/84 updated within 45m [fresh=84; 75 Tier-1 futures + 9 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 15805 dup bars, 0 undedupable; ws 4 out-of-order, 823 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 42 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | violating | upstream +60 but output +0 (streak 1/72) | 1 |
| dark_atr_trail_arms | ok | no open arms; covering 1486/1504 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 5 promoted today, nothing refused | 0 |
| dark_resolution | violating | 14 of 139 open dark rows are not being advanced (worst: AGTUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 52/120) | 52 |
| dark_sar_arms | ok | no open arms; covering 1482/1500 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 41865930 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 488/6) | 488 |
| emission_controller | ok | last cycle 335s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×298]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 51/6) | 51 |
| entry_quality_effective | ok | 11721 evaluated, 3645 suppressed, 3739 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,381 reads/day of 50,000 [engine 1,343, signing 38]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5040 sealed bars over 42 symbols; 911 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +0 / upstream +0 | 0 |
| indicator_cache_key | ok | 162532 frozen value(s) avoided; 1456655 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.22R over n=2873 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +0 / upstream +0 | 0 |
| mover_admission_metadata | ok | 920 symbols known, 213 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 9 held, 9 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2317256 evicted (sampled: execution:trigger_not_confirmed 400/840506, execution:overextended 400/759113, setup_compat:regime_STRONG_TREND 400/356969) | 0 |
| price_action_lane | ok | 1468664 evaluated, 1243 emitted; layer1 1243 stamped / 0 blind; cooldown=191926, delta_opposed=122966, no_footprint=644057, no_opposing_target=2290, no_sweep=402225, rr_below_floor=103957 | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.34R over n=1138 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +0 / upstream +0 | 0 |
| sar_alignment_crosscheck | ok | 511/20564 disagreed (2.5%) | 0 |
| sar_exit_shadow | ok | output +0 / upstream +0 | 0 |
| sar_hold_arm | ok | 1855 held arms settled, 146 unscored, 35 still walking (30 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 67/67 resolvable | 0 |
| sar_live_arms | ok | 36 arms current, none stalled; covering 1124/1124 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 64 still mid-window | 0 |
| scan_cycle | ok | last 37.47s, worst 115.85s over 16482 lifetime cycles; lifetime 44 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.93s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 611434 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 9m ago | 0 |
| snapshot_writer | ok | last cycle 7s ago (0.15s to run, worst 89.85s), 610 overrun(s) of 10393 cycles, TTL 900s; slowest signals=0.05s, activity=0.05s, data_intake=0.04s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=31, gate reads=0, withheld=31) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +137 / upstream +0 | 0 |
| structural_snap | ok | 5911/5911 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=1484) | 0 |
| structural_veto_lane | ok | 2210 stamped; 0 with no readable level book, 63 with clear air ahead, 1775 would-reject, 0 enforced | 0 |
| suppression_audit | violating | upstream +60 but output +0 (streak 1/72) | 1 |
| tuned_variants | violating | 369 non-stamps — atr_arm_uncomputable=369 (seen=8590 stamped=806 skipped=7415) (streak 475/6) | 475 |
| unlock_shorts | ok | 10 open, 46 scheduled, calendar 8.2h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 12 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3146552`
- `Path funnel` emissions: `78`
- `Regime distribution` emissions: `78`
- `QUIET_SCALP_BLOCK` events: `114`
- `confidence_gate` events: `6131`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **650**
- Total REST-fallback activations: **85**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 121 | 3155 | 8447 | 26637 | 0 |
| futures_aggtrade | 175 | 3246 | 7715 | 35325 | 0 |
| futures_depth | 238 | 3036 | 8666 | 35340 | 0 |
| futures_liq | 10 | 3158 | 6344 | 35322 | 0 |
| futures_mover | 106 | 2881 | 8255 | 18176 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 85 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=595654] state[populated=595654] buckets[few=4, many=595604, some=46] sources[none] quality[none]
- funding_rate: presence[absent=80429, present=515225] state[empty=80429, populated=515225] buckets[few=515225, none=80429] sources[none] quality[none]
- liquidation_clusters: presence[absent=341686, present=253968] state[empty=341686, populated=253968] buckets[few=206558, none=341686, some=47410] sources[none] quality[none]
- oi_snapshot: presence[absent=80429, present=515225] state[empty=80429, populated=515225] buckets[few=322, many=512975, none=80429, some=1928] sources[none] quality[none]
- order_book: presence[absent=166191, present=429463] state[populated=429463, unavailable=166191] buckets[few=429463, none=166191] sources[book_ticker=429463, unavailable=166191] quality[none=166191, top_of_book_only=429463]
- orderblocks: presence[absent=595654] state[empty=595654] buckets[none=595654] sources[measured_dark=595654] quality[none]
- recent_ticks: presence[present=595654] state[populated=595654] buckets[many=595654] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.8123011589050293` sec
- Median create→first breach: `2455.6890301704407` sec
- Median create→terminal: `2455.6890830993652` sec
- Median first breach→terminal: `7.605552673339844e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 4, "pct": 9.3}, "under_180s": {"count": 4, "pct": 9.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 4, "pct": 9.3}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.2601784408852448 | 1.3344928452842126 | 0.9443126243339725 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 2.320042814588235 | 2.0363921241176097 | 1.0742385378298003 | 1 | 1 |
| MEAN_REVERT | 1 | 1 | 1.0866593767085855 | 1.81793329688354 | 0.5977443609022575 | 0 | 1 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.1614253790166282 | 2.5337214927505345 | 0.8684211472117671 | 0 | 4 |
| MOVER_TREND_PULLBACK | 32 | 32 | 4.1670195061593605 | 3.0 | 1.4004343150962844 | 28 | 4 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 1.5555678619508038 | 1.817244785276075 | 0.8560034809589412 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10652.605731010437 | 10652.605803012848 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.32 | 2019.9176423549652 | 2019.9176894426346 |
| MEAN_REVERT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.8179 | 1878.735510110855 | 1878.7355501651764 |
| MOVER_AVWAP_SCALP | 4 | 4 | 0.0 | 25.0 | 0.0 | 0.0 | -0.5243 | 29119.23399746418 | 29119.23404943943 |
| MOVER_TREND_PULLBACK | 32 | 32 | 37.5 | 50.0 | 37.5 | 0.0 | 0.1986 | 1645.3418600559235 | 1645.496405005455 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4468 | 15358.91007900238 | 15358.910101175308 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1599 | 6 | 1227 | 0.0 | 0.0 | None | None | 372 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3982 | 13 | 3750 | 0.0 | 0.0 | None | None | 232 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-46`
- Gating Δ: `954`
- No-generation Δ: `-283632`
- Fast failures Δ: `3`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.163, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -1.163, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.5243, "current_avg_pnl": -0.5243, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.8835, "current_avg_pnl": 0.1986, "current_win_rate": 37.5, "previous_avg_pnl": 1.0821, "previous_win_rate": 39.4, "win_rate_delta": -1.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.2998, "current_avg_pnl": -1.4468, "current_win_rate": 0.0, "previous_avg_pnl": -0.147, "previous_win_rate": 30.0, "win_rate_delta": -30.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": -109, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -252, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
