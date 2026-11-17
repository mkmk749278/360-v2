# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `5453` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 111 | 111 | 111 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12635 | 12635 | 11636 | 19 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 88163 | 88155 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 91062 | 91062 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 90698 | 88413 | 2627 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 91094 | 89546 | 1633 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 90645 | 90255 | 414 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 82189 | 82199 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 91186 | 91215 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 91225 | 88471 | 3593 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 91570 | 95336 | 1050 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 88190 | 83533 | 7993 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 89956 | 89956 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 91068 | 91091 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 90675 | 90600 | 93 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 92068 | 90283 | 2387 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 89960 | 90266 | 376 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 81861 | 77884 | 4213 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 82108 | 81697 | 488 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 88128 | 88107 | 50 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 82206 | 82217 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6129 | 6129 | 5288 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 999 | 999 | 167 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 18 | 18 | 18 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 22403 | 22403 | 22174 | 4 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 4 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 10044 | 10044 | 4894 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2895 | 2895 | 1167 | 53 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 26201 | 26201 | 11141 | 269 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 578 | 578 | 139 | 20 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 7850 | 7850 | 6101 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1104 | 1104 | 559 | 13 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2689 | 2689 | 2304 | 33 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 143 | 143 | 35 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=88155): breakout_not_found=44761, basic_filters_failed=30038, move_not_fresh=8987, breakout_stale=3419, retest_proximity_failed=821, volume_spike_missing=128, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=91062): cls_disabled_merged_into_lsr=91062
- **EVAL::DIVERGENCE_CONTINUATION** (total=88413): cvd_divergence_failed=32278, basic_filters_failed=28566, h1_trend_not_aligned=22919, ema_alignment_reject=3779, retest_proximity_failed=629, missing_fvg_or_orderblock=242
- **EVAL::FAILED_AUCTION_RECLAIM** (total=89546): auction_not_detected=47781, basic_filters_failed=27903, reclaim_hold_failed=6483, tail_too_small=5247, regime_blocked=2110, rsi_reject=22
- **EVAL::FUNDING_EXTREME** (total=90255): funding_not_extreme=55474, basic_filters_failed=27455, ema_alignment_reject=3049, missing_funding_rate=2693, rsi_reject=858, cvd_divergence_failed=371, momentum_reject=292, missing_fvg_or_orderblock=63
- **EVAL::LIQUIDATION_REVERSAL** (total=82199): cascade_threshold_not_met=53369, basic_filters_failed=28286, cvd_divergence_failed=306, rsi_reject=187, missing_fvg_or_orderblock=41, volume_spike_missing=10
- **EVAL::MA_CROSS_TREND_SHIFT** (total=91215): no_ma_cross=61840, basic_filters_failed=28580, ma_cross_cooldown=424, ma_cross_htf_misaligned=371
- **EVAL::MEAN_REVERT** (total=88471): no_extension=72617, basic_filters_failed=15854
- **EVAL::MOVER_AVWAP_SCALP** (total=95336): no_mover_leg=30471, basic_filters_failed=30283, no_avwap_tag=26049, avwap_slope_against=4538, avwap_reclaim_no_volume=2640, no_avwap_reclaim=1199, anchor_too_recent=156
- **EVAL::MOVER_TREND_PULLBACK** (total=83533): mover_run_too_small=41896, basic_filters_failed=30149, no_reclaim=10187, no_pullback_tag=1301
- **EVAL::OPENING_RANGE_BREAKOUT** (total=89956): feature_disabled=89956
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=91091): regime_blocked=54843, breakout_not_found=21902, basic_filters_failed=8441, adx_reject=5843, ema_alignment_reject=62
- **EVAL::QUIET_COMPRESSION_BREAK** (total=90600): regime_blocked=38206, compression_not_detected=26665, basic_filters_failed=19451, breakout_not_detected=5842, volume_confirmation_failed=430, rsi_reject=4, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=90283): no_range_edge=74429, basic_filters_failed=15854
- **EVAL::SR_FLIP_RETEST** (total=90266): flip_close_not_confirmed=49745, basic_filters_failed=27875, retest_out_of_zone=3848, h1_break_not_confirmed=2126, regime_blocked=2092, reclaim_hold_failed=1968, long_break_volume_thin=1708, ema_alignment_reject=323, long_acceptance_not_held=296, wick_quality_failed=184, whipsaw_flip=78, missing_fvg_or_orderblock=23
- **EVAL::STANDARD** (total=77884): adx_reject=28922, momentum_reject=22032, basic_filters_failed=10489, sweeps_not_detected=6221, ema_alignment_reject=4737, macd_reject=4566, htf_poi_unanchored=846, rsi_reject=40, invalid_sl_geometry=24, mtf_reject=7
- **EVAL::TREND_PULLBACK** (total=81697): h1_trend_not_aligned=29934, basic_filters_failed=15719, ema_alignment_reject=11725, h1_pullback_not_confirmed=6392, no_ema_reclaim_close=5102, ema_not_tested_prev=4615, body_conviction_fail=3125, rsi_reject=2494, prev_already_below_emas=1245, no_prev_low_break=665, prev_already_above_emas=237, momentum_flat=199, no_prev_high_break=115, ema21_not_tagged=70, missing_fvg_or_orderblock=51, momentum_reject=9
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=88107): breakout_not_found=46164, basic_filters_failed=30035, move_not_fresh=7160, breakout_stale=3594, retest_proximity_failed=800, volume_spike_missing=321, missing_fvg_or_orderblock=22, move_exhausted=11
- **EVAL::WHALE_MOMENTUM** (total=82217): momentum_reject=72944, recent_ticks_insufficient=5774, basic_filters_failed=3499

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=15): execution:overextended=15
- **DIVERGENCE_CONTINUATION** (total=575): setup_compat:regime_VOLATILE_UNSUITABLE=532, setup_compat:regime_BREAKOUT_EXPANSION=43
- **FAILED_AUCTION_RECLAIM** (total=1846): execution:overextended=822, setup_compat:regime_STRONG_TREND=793, context_floor=231
- **FUNDING_EXTREME_SIGNAL** (total=873): execution:trigger_not_confirmed=867, context_floor=6
- **LIQUIDATION_REVERSAL** (total=18): execution:trigger_not_confirmed=18
- **LIQUIDITY_SWEEP_REVERSAL** (total=5808): setup_compat:regime_STRONG_TREND=2212, execution:trigger_not_confirmed=1825, execution:overextended=1771
- **MA_CROSS_TREND_SHIFT** (total=8): execution:trigger_not_confirmed=4, setup_compat:regime_DIRTY_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:overextended=1
- **MEAN_REVERT** (total=7416): setup_compat:regime_WEAK_TREND=4093, setup_compat:regime_STRONG_TREND=2718, execution:overextended=599, entry_quality=6
- **MOVER_AVWAP_SCALP** (total=1475): execution:overextended=1039, entry_quality=229, execution:trigger_not_confirmed=207
- **MOVER_TREND_PULLBACK** (total=11743): execution:trigger_not_confirmed=5994, execution:overextended=3647, entry_quality=2102
- **RANGE_FADE** (total=6062): setup_compat:regime_WEAK_TREND=2972, setup_compat:regime_STRONG_TREND=1562, execution:overextended=693, setup_compat:regime_VOLATILE_UNSUITABLE=681, context_edge=105, setup_compat:regime_BREAKOUT_EXPANSION=49
- **TREND_PULLBACK_EMA** (total=2430): setup_compat:regime_CLEAN_RANGE=1516, setup_compat:regime_DIRTY_RANGE=714, setup_compat:regime_VOLATILE_UNSUITABLE=108, entry_quality=92
- **VOLUME_SURGE_BREAKOUT** (total=12): execution:overextended=12

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 223652 | 40.6% |
| TRENDING_UP | 103795 | 18.9% |
| TRENDING_DOWN | 96965 | 17.6% |
| QUIET | 93425 | 17.0% |
| VOLATILE | 32793 | 6.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **118**
- Average confidence gap to threshold: **12.67** (samples=118) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ASTERUSDT=22, INITUSDT=11, BNBUSDT=10, WLFIUSDT=8, LTCUSDT=8, TRXUSDT=7, SOLUSDT=6, XRPUSDT=6, XMRUSDT=5, KAVAUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 82 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 147 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 132 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 15 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 12 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 16 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 123 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 5 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 102 |
| MEAN_REVERT | kept | min_confidence_pass | 15 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 364 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 745 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 4030 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 38 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4285 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 256 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 49 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 67 |
| SR_FLIP_RETEST | filtered | min_confidence | 175 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 188 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 71 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 137 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 72 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 89 | 54.51 | 62.75 | 8.24 | 21.50 | 19.24 | 17.71 | 1.53 | 14.20 |
| DIVERGENCE_CONTINUATION | kept | 147 | 72.05 | 65.00 | -7.05 | 20.37 | 19.24 | 17.49 | 0.72 | -1.48 |
| FAILED_AUCTION_RECLAIM | filtered | 147 | 45.50 | 60.96 | 15.46 | 23.01 | 18.01 | 20.00 | 1.99 | 9.20 |
| FAILED_AUCTION_RECLAIM | kept | 12 | 71.88 | 65.00 | -6.88 | 20.61 | 18.81 | 20.00 | 2.12 | 2.19 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 44.77 | 62.19 | 17.42 | 21.14 | 13.58 | 16.98 | 3.12 | 10.49 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.00 | 65.00 | -4.00 | 20.90 | 14.00 | 17.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 128 | 53.70 | 64.03 | 10.33 | 21.71 | 19.54 | 17.99 | 1.60 | 3.97 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 5 | 67.34 | 65.00 | -2.34 | 20.66 | 17.60 | 17.62 | 0.80 | 0.72 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 53.80 | 61.00 | 7.20 | 21.20 | 18.80 | 15.80 | 0.00 | 16.20 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.15 | 65.00 | -5.15 | 21.15 | 17.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 102 | 51.24 | 64.53 | 13.29 | 20.04 | 15.03 | 15.73 | 0.00 | 14.93 |
| MEAN_REVERT | kept | 15 | 66.98 | 65.00 | -1.98 | 18.47 | 14.01 | 15.31 | 0.00 | 0.32 |
| MOVER_AVWAP_SCALP | filtered | 365 | 50.52 | 64.36 | 13.84 | 20.00 | 16.26 | 15.80 | 3.86 | 18.49 |
| MOVER_AVWAP_SCALP | kept | 745 | 78.70 | 65.00 | -13.70 | 20.16 | 16.92 | 15.80 | 4.86 | 4.00 |
| MOVER_TREND_PULLBACK | filtered | 4068 | 56.05 | 64.42 | 8.37 | 19.70 | 18.57 | 15.80 | 3.84 | 17.05 |
| MOVER_TREND_PULLBACK | kept | 4285 | 76.53 | 65.00 | -11.53 | 19.90 | 18.62 | 15.80 | 4.37 | 2.44 |
| QUIET_COMPRESSION_BREAK | filtered | 305 | 50.70 | 63.96 | 13.26 | 21.02 | 18.60 | 20.00 | 0.00 | 7.76 |
| QUIET_COMPRESSION_BREAK | kept | 67 | 73.90 | 65.00 | -8.90 | 22.54 | 19.57 | 20.00 | 0.00 | 0.45 |
| SR_FLIP_RETEST | filtered | 178 | 57.99 | 64.10 | 6.11 | 21.91 | 20.00 | 16.43 | 1.83 | 11.87 |
| SR_FLIP_RETEST | kept | 188 | 69.75 | 65.00 | -4.75 | 21.46 | 20.00 | 15.82 | 1.89 | 0.47 |
| TREND_PULLBACK_EMA | filtered | 71 | 56.03 | 64.01 | 7.98 | 21.16 | 19.51 | 17.84 | 4.32 | 17.95 |
| TREND_PULLBACK_EMA | kept | 137 | 77.95 | 65.00 | -12.95 | 20.98 | 19.93 | 17.49 | 4.69 | 1.97 |
| VOLUME_SURGE_BREAKOUT | filtered | 72 | 46.84 | 64.50 | 17.66 | 20.75 | 19.01 | 20.00 | 3.47 | 11.03 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 77.36 | 65.00 | -12.36 | 16.20 | 16.70 | 20.00 | 4.50 | 1.71 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 89 | 54.51 | 23.65 | 8.94 | 6.94 | 13.04 | 5.56 | 9.04 | 1.53 |
| DIVERGENCE_CONTINUATION | kept | 147 | 72.05 | 23.26 | 15.58 | 7.12 | 12.27 | 5.18 | 8.51 | 0.72 |
| FAILED_AUCTION_RECLAIM | filtered | 147 | 45.50 | 20.63 | 16.23 | 7.43 | 14.07 | 5.90 | 3.15 | 1.99 |
| FAILED_AUCTION_RECLAIM | kept | 12 | 71.88 | 23.00 | 18.00 | 8.75 | 11.50 | 5.58 | 6.37 | 2.12 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 44.77 | 24.50 | 15.75 | 3.94 | 11.81 | 6.41 | 3.79 | 3.12 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.00 | 17.00 | 18.00 | 6.00 | 12.00 | 5.00 | 6.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 128 | 53.70 | 22.28 | 15.47 | 5.88 | 12.99 | 5.23 | 4.99 | 1.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 5 | 67.34 | 18.20 | 15.60 | 6.60 | 13.40 | 5.00 | 8.46 | 0.80 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 53.80 | 23.00 | 14.00 | 3.00 | 17.00 | 5.00 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.15 | 21.00 | 14.00 | 6.00 | 15.50 | 5.00 | 8.65 | 0.00 |
| MEAN_REVERT | filtered | 102 | 51.24 | 17.47 | 14.00 | 9.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 15 | 66.98 | 23.27 | 14.00 | 6.40 | 12.80 | 5.00 | 5.83 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 365 | 50.52 | 18.42 | 18.00 | 11.25 | 14.22 | 6.62 | 6.30 | 3.86 |
| MOVER_AVWAP_SCALP | kept | 745 | 78.70 | 19.62 | 18.04 | 10.61 | 14.01 | 7.19 | 9.08 | 4.86 |
| MOVER_TREND_PULLBACK | filtered | 4068 | 56.05 | 18.62 | 18.00 | 7.66 | 12.24 | 6.12 | 8.52 | 3.84 |
| MOVER_TREND_PULLBACK | kept | 4285 | 76.53 | 19.62 | 18.01 | 7.77 | 13.32 | 6.73 | 9.25 | 4.37 |
| QUIET_COMPRESSION_BREAK | filtered | 305 | 50.70 | 17.79 | 14.64 | 10.27 | 14.06 | 7.98 | 5.97 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 67 | 73.90 | 21.66 | 16.63 | 10.93 | 14.04 | 5.92 | 6.59 | 0.00 |
| SR_FLIP_RETEST | filtered | 178 | 57.99 | 20.69 | 17.83 | 4.99 | 12.54 | 5.10 | 6.87 | 1.83 |
| SR_FLIP_RETEST | kept | 188 | 69.75 | 20.83 | 17.84 | 3.93 | 13.52 | 5.10 | 8.15 | 1.89 |
| TREND_PULLBACK_EMA | filtered | 71 | 56.03 | 16.23 | 18.00 | 7.50 | 13.68 | 6.90 | 8.21 | 4.32 |
| TREND_PULLBACK_EMA | kept | 137 | 77.95 | 19.46 | 18.00 | 7.54 | 14.65 | 7.30 | 9.31 | 4.69 |
| VOLUME_SURGE_BREAKOUT | filtered | 72 | 46.84 | 17.00 | 17.67 | 12.38 | 14.00 | 4.97 | 3.39 | 3.47 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 77.36 | 17.00 | 18.00 | 12.00 | 14.00 | 3.57 | 10.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 89 | 54.51 | 0.00 | 0.00 | 4.26 | 0.00 | 0.00 | 0.34 | 0.00 | 0.00 | **4.60** |
| DIVERGENCE_CONTINUATION | kept | 147 | 72.05 | 0.00 | 0.00 | 0.70 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.80** |
| FAILED_AUCTION_RECLAIM | filtered | 147 | 45.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | **0.73** |
| FAILED_AUCTION_RECLAIM | kept | 12 | 71.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 44.77 | 0.00 | 0.00 | 4.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.55** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 69.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 128 | 53.70 | 0.00 | 0.00 | 0.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.85** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 5 | 67.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 53.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 102 | 51.24 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| MEAN_REVERT | kept | 15 | 66.98 | 0.00 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.32** |
| MOVER_AVWAP_SCALP | filtered | 365 | 50.52 | 0.00 | 0.00 | 1.05 | 0.00 | 5.29 | 0.03 | 0.00 | 1.17 | **7.54** |
| MOVER_AVWAP_SCALP | kept | 745 | 78.70 | 0.00 | 0.00 | 1.01 | 0.00 | 0.28 | 0.01 | 0.00 | 0.11 | **1.41** |
| MOVER_TREND_PULLBACK | filtered | 4068 | 56.05 | 0.23 | 0.00 | 2.26 | 0.00 | 0.49 | 0.02 | 0.00 | 0.01 | **3.01** |
| MOVER_TREND_PULLBACK | kept | 4285 | 76.53 | 0.00 | 0.00 | 1.04 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | **1.07** |
| QUIET_COMPRESSION_BREAK | filtered | 305 | 50.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 2.03 | **2.11** |
| QUIET_COMPRESSION_BREAK | kept | 67 | 73.90 | 0.00 | 0.00 | 0.12 | 0.00 | 0.52 | 0.00 | 0.00 | 0.00 | **0.64** |
| SR_FLIP_RETEST | filtered | 178 | 57.99 | 0.00 | 0.00 | 1.73 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **2.09** |
| SR_FLIP_RETEST | kept | 188 | 69.75 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.75** |
| TREND_PULLBACK_EMA | filtered | 71 | 56.03 | 0.00 | 0.00 | 2.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.70** |
| TREND_PULLBACK_EMA | kept | 137 | 77.95 | 0.00 | 0.00 | 3.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.32** |
| VOLUME_SURGE_BREAKOUT | filtered | 72 | 46.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.45 | **2.45** |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 77.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **192723 held of 903021 seen** across 21 strategies; 4361 cells past the sample floor; **2351 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49071 | 584/48487/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.26R) |
| MOVER_AVWAP_SCALP | 26007 | 194/25813/0 | 43% | -0.19 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15131 | 251/14880/0 | 45% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14323 | 148/14175/0 | 36% | -0.32 | OVERLAP/RANGE/NORMAL/BTC_FALLING (+1.72R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 13535 | 77/13458/0 | 39% | -0.29 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-1.37R) |
| LIQUIDITY_SWEEP_REVERSAL | 10663 | 112/10551/0 | 37% | -0.43 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9377 | 453/8924/0 | 44% | -0.11 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8330 | 0/0/8330 | 43% | -0.08 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.11R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7853 | 0/0/7853 | 35% | -0.15 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.33R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.37R) |
| SHADOW_FUNDING_FADE | 7387 | 0/0/7387 | 33% | -0.42 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6864 | 22/6842/0 | 46% | -0.29 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5660 | 71/5589/0 | 37% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4405 | 2/4403/0 | 31% | -0.44 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 4054 | 0/4054/0 | 28% | -0.42 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 3107 | 6/3101/0 | 50% | +0.17 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1744 | 0/0/1744 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.57R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 542 | 0/542/0 | 37% | -0.23 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 232 | 36/196/0 | 44% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 402 | 27% / -0.57R | 402 | 52% / -0.10R | +0.47 | **ATR** |
| TREND_PULLBACK_EMA | 1386 | 39% / -0.36R | 1386 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1600 | 42% / -0.37R | 1600 | 57% / -0.11R | +0.25 | **ATR** |
| LIQUIDATION_REVERSAL | 34 | 26% / -0.56R | 34 | 47% / -0.32R | +0.24 | **ATR** |
| MA_CROSS_TREND_SHIFT | 71 | 45% / -0.17R | 71 | 51% / -0.04R | +0.13 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 231 | 37% / -0.17R | 231 | 48% / -0.04R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 739 | 47% / -0.26R | 739 | 51% / -0.14R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2848 | 46% / -0.14R | 2848 | 52% / -0.04R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1580 | 41% / -0.23R | 1580 | 44% / -0.12R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9096 | 48% / -0.13R | 9096 | 54% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1990 | 48% / -0.12R | 1990 | 53% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 164 | 43% / +0.02R | 164 | 49% / +0.07R | +0.05 | **ATR** |
| MEAN_REVERT | 478 | 46% / -0.15R | 478 | 45% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1642 | 48% / -0.10R | 1642 | 48% / -0.11R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12149 | 27% | -0.29R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2848 | 50% | -0.03R | 242 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 147 | 48% | -0.05R | 73 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1777 | 33% / -0.13R | +0.94 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1892 | 38% / -0.19R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3394 | 36% / -0.14R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11142 | 36% / -0.14R | +0.39 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2308 | 37% / -0.12R | +0.16 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1590 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1313 | 31% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 338 | 32% / -0.35R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 519 | 32% / -0.23R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 395 | 47% / -0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 115 | 46% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 640 | 34% / -0.28R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 114 | 31% / +0.14R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 44 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 25 | 48% / +0.53R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 1722/31181 disagreed (5.5%) (streak 346/6) (sustained 346 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 506/6) (sustained 506 cycles)
- **ALERT** `range_fade_emission` — 815 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.17R over n=3101, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 24/6) (sustained 24 cycles)
- **ALERT** `tuned_variants` — 619 non-stamps — atr_arm_uncomputable=619 (seen=18744 stamped=1607 skipped=16518) (streak 506/6) (sustained 506 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 171157886 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 27 arms current, none stalled; covering 2112/2112 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +2 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 52 arms current, none stalled; covering 1120/1120 signals (100%) | 0 |
| auto_dispatch | ok | 94 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=94. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 106/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 64580.10 | 0 |
| candle_coverage | ok | 80/80 symbols with ≥20 15m candles, 80/80 updated within 45m [fresh=80; 77 Tier-1 futures + 3 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 620 dup bars, 0 undedupable; ws 0 out-of-order, 365 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 61 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +54 / upstream +36 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2577/2596 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 95 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 2538/2557 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 56756805 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 506/6) | 506 |
| emission_controller | ok | last cycle 1506s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=237, MOVER_AVWAP_SCALP=328, MOVER_TREND_PULLBACK=4406, RANGE_FADE=826, TREND_PULLBACK_EMA=203), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 20369 evaluated, 6842 suppressed, 10533 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,314 reads/day of 50,000 [engine 1,293, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5040 sealed bars over 42 symbols; 1159 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +338 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 224650 frozen value(s) avoided; 1698039 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=5589 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +338 but output +0 (streak 5/72) | 5 |
| mover_admission_metadata | ok | 946 symbols known, 237 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 3 held, 3 with scan counts, 3 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2211 rows held, 3673207 evicted (sampled: execution:trigger_not_confirmed 277/1290237, execution:overextended 278/1130917, setup_compat:regime_STRONG_TREND 277/634042) | 0 |
| price_action_lane | ok | 1332373 evaluated, 1505 emitted; layer1 1505 stamped / 0 blind; cooldown=205485, delta_opposed=132769, no_footprint=473503, no_opposing_target=2473, no_sweep=398330, rr_below_floor=118308 | 0 |
| promoted_pair_integrity | ok | 3/3 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 815 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.17R over n=3101, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 24/6) | 24 |
| range_fade_path | ok | output +80 / upstream +338 | 0 |
| sar_alignment_crosscheck | violating | 1722/31181 disagreed (5.5%) (streak 346/6) | 346 |
| sar_exit_shadow | ok | output +2 / upstream +338 | 0 |
| sar_hold_arm | ok | 1872 held arms settled, 128 unscored, 52 still walking (47 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 34/34 resolvable | 0 |
| sar_live_arms | ok | 52 arms current, none stalled; covering 1120/1120 signals (100%) | 0 |
| sar_refresh_budget | ok | 1 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 6 resolved, 28 still mid-window | 0 |
| scan_cycle | ok | last 42.78s, worst 166.37s over 16807 lifetime cycles; lifetime 317 over 60s, 12 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.22s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 557634 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 16s ago (86.09s to run, worst 175.83s), 1064 overrun(s) of 10772 cycles, TTL 900s; slowest router_delivery=22.03s, user_positions=18.06s, exchange_positions=9.13s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +63 / upstream +338 | 0 |
| structural_snap | ok | 6000/6000 measured, 36 blind, 0 levels moved (refusals: redetect_cooldown=1803) | 0 |
| structural_veto_lane | ok | 2988 stamped; 0 with no readable level book, 64 with clear air ahead, 2185 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +338 / upstream +36 | 0 |
| tuned_variants | violating | 619 non-stamps — atr_arm_uncomputable=619 (seen=18744 stamped=1607 skipped=16518) (streak 506/6) | 506 |
| unlock_shorts | ok | 18 open, 41 scheduled, calendar 10.9h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 28 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2588825`
- `Path funnel` emissions: `72`
- `Regime distribution` emissions: `72`
- `QUIET_SCALP_BLOCK` events: `118`
- `confidence_gate` events: `11153`
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
| futures | 1 | 4501 | 4501 | 4501 | 0 |
| futures_aggtrade | 3 | 6020 | 6020 | 7228 | 0 |
| futures_depth | 3 | 3582 | 3582 | 15004 | 0 |
| futures_liq | 4 | 2865 | 3428 | 10621 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=411441] state[populated=411441] buckets[many=411441] sources[none] quality[none]
- funding_rate: presence[absent=23259, present=388182] state[empty=23259, populated=388182] buckets[few=388182, none=23259] sources[none] quality[none]
- liquidation_clusters: presence[absent=234071, present=177370] state[empty=234071, populated=177370] buckets[few=149555, none=234071, some=27815] sources[none] quality[none]
- oi_snapshot: presence[absent=23259, present=388182] state[empty=23259, populated=388182] buckets[few=359, many=385947, none=23259, some=1876] sources[none] quality[none]
- order_book: presence[absent=116385, present=295056] state[populated=295056, unavailable=116385] buckets[few=295056, none=116385] sources[book_ticker=295056, unavailable=116385] quality[none=116385, top_of_book_only=295056]
- orderblocks: presence[absent=411441] state[empty=411441] buckets[none=411441] sources[measured_dark=411441] quality[none]
- recent_ticks: presence[present=411441] state[populated=411441] buckets[many=411441] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.7840731143951416` sec
- Median create→first breach: `6111.3530740737915` sec
- Median create→terminal: `6111.353135108948` sec
- Median first breach→terminal: `7.200241088867188e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.1}, "under_180s": {"count": 1, "pct": 2.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.1}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.915935587868109 | 1.1223904903960316 | 0.8134989779259547 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 3.264674832666136 | 3.0 | 1.0882249442220453 | 1 | 0 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 4.777917650144243 | 1.584803866471846 | 3.014832151300233 | 1 | 0 |
| MOVER_AVWAP_SCALP | 3 | 3 | 1.4832454027354744 | 1.6459404517810619 | 0.950741929507487 | 1 | 2 |
| MOVER_TREND_PULLBACK | 31 | 31 | 4.271728431265083 | 3.0 | 1.4776976418064012 | 28 | 3 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.1283804314797894 | 1.353488837721493 | 0.8955491860623906 | 0 | 7 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 1.8239236777858738 | 1.3739033818021502 | 0 | 0 | 0 | 2 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 4.484366428963241 | 4.957103675260555 | 1 | 0 | 0 | 0 | 0 | 0 |
| MA_CROSS_TREND_SHIFT | 1 | 7.166876475216374 | 1.92112008064516 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 3 | 1.9181162303664918 | 1.9673219422892445 | 2 | 1 | 1 | 1 | 0 | 0 |
| MOVER_TREND_PULLBACK | 31 | 7.155497863247861 | 4.721256309590571 | 4 | 0 | 0 | 27 | 7 | 0 |
| QUIET_COMPRESSION_BREAK | 9 | 2.729060265577103 | 1.791314972401098 | 0 | 0 | 0 | 6 | 1 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9159 | 13289.690127015114 | 13289.690147042274 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.2647 | 353.43161511421204 | 353.43167996406555 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 13949.445584058762 | 13949.445606946945 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | -0.4372 | 10831.919634103775 | 10831.919652223587 |
| MOVER_TREND_PULLBACK | 31 | 31 | 38.7 | 29.0 | 38.7 | 0.0 | 1.0146 | 2260.9898841381073 | 2261.288682937622 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 22.2 | 22.2 | 22.2 | 0.0 | 0.0658 | 15513.570061922073 | 15513.5701379776 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1104 | 13 | 559 | 0.0 | 0.0 | None | None | 545 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2689 | 33 | 2304 | 0.0 | 0.0 | None | None | 385 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-83`
- Gating Δ: `-3143`
- No-generation Δ: `-13040`
- Fast failures Δ: `-2`
- Quality changes: `{"LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.188, "current_avg_pnl": -3.2647, "current_win_rate": 0.0, "previous_avg_pnl": -3.0767, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.6688, "current_avg_pnl": -0.4372, "current_win_rate": 0.0, "previous_avg_pnl": -2.106, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.8823, "current_avg_pnl": 1.0146, "current_win_rate": 38.7, "previous_avg_pnl": 1.8969, "previous_win_rate": 52.4, "win_rate_delta": -13.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.3227, "current_avg_pnl": 0.0658, "current_win_rate": 22.2, "previous_avg_pnl": -1.2569, "previous_win_rate": 0.0, "win_rate_delta": 22.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -91, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -9, "geometry_changed_delta": 0, "geometry_preserved_delta": -341, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
