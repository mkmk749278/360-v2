# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `18339` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 39 | 39 | 32 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 25127 | 25127 | 23194 | 14 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 132974 | 132995 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 135993 | 136009 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 135539 | 128550 | 7435 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 136025 | 129159 | 7171 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 136384 | 136048 | 386 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 120731 | 120731 | 16 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 136341 | 136365 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 136378 | 134235 | 2520 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 138481 | 142725 | 2397 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 133001 | 116680 | 21762 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 132114 | 132124 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 136011 | 136004 | 20 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 135476 | 134603 | 934 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 136760 | 133365 | 5192 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 131165 | 129745 | 5658 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 119868 | 114779 | 5461 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 120252 | 119456 | 870 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 132932 | 132934 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 120746 | 120780 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 23951 | 23951 | 15614 | 45 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1146 | 1146 | 997 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 74 | 74 | 74 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 24984 | 24984 | 24379 | 30 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 10 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5388 | 5388 | 5388 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 5719 | 5719 | 5718 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 51719 | 51719 | 44203 | 97 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 46 | 46 | 46 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3490 | 3490 | 2615 | 25 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 14356 | 14356 | 14356 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 18732 | 18732 | 4804 | 102 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3300 | 3300 | 3187 | 4 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 119 | 119 | 51 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=132995): breakout_not_found=76127, basic_filters_failed=35780, move_not_fresh=14867, breakout_stale=4159, retest_proximity_failed=1693, volume_spike_missing=253, ema_alignment_reject=46, missing_fvg_or_orderblock=36, move_exhausted=34
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=136009): cls_disabled_merged_into_lsr=136009
- **EVAL::DIVERGENCE_CONTINUATION** (total=128550): cvd_divergence_failed=41205, h1_trend_not_aligned=38089, basic_filters_failed=32724, ema_alignment_reject=13790, retest_proximity_failed=1948, missing_fvg_or_orderblock=794
- **EVAL::FAILED_AUCTION_RECLAIM** (total=129159): auction_not_detected=51040, basic_filters_failed=31635, reclaim_hold_failed=25572, tail_too_small=16931, regime_blocked=3977, rsi_reject=4
- **EVAL::FUNDING_EXTREME** (total=136048): funding_not_extreme=96775, basic_filters_failed=32126, ema_alignment_reject=3341, missing_funding_rate=2578, rsi_reject=713, momentum_reject=245, cvd_divergence_failed=220, missing_fvg_or_orderblock=50
- **EVAL::LIQUIDATION_REVERSAL** (total=120731): cascade_threshold_not_met=86888, basic_filters_failed=32570, cvd_divergence_failed=673, rsi_reject=556, missing_fvg_or_orderblock=29, volume_spike_missing=15
- **EVAL::MA_CROSS_TREND_SHIFT** (total=136365): no_ma_cross=100745, basic_filters_failed=32748, ma_cross_htf_misaligned=1468, ma_cross_cooldown=1384, ma_cross_htf_unconfirmed=20
- **EVAL::MEAN_REVERT** (total=134235): no_extension=118476, basic_filters_failed=15759
- **EVAL::MOVER_AVWAP_SCALP** (total=142725): no_mover_leg=54551, basic_filters_failed=35928, no_avwap_tag=33373, avwap_slope_against=9571, avwap_reclaim_no_volume=7285, no_avwap_reclaim=2017
- **EVAL::MOVER_TREND_PULLBACK** (total=116680): mover_run_too_small=60882, basic_filters_failed=35846, no_reclaim=18164, no_pullback_tag=1788
- **EVAL::OPENING_RANGE_BREAKOUT** (total=132124): feature_disabled=132124
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=136004): regime_blocked=99546, breakout_not_found=25745, basic_filters_failed=7253, adx_reject=3408, ema_alignment_reject=52
- **EVAL::QUIET_COMPRESSION_BREAK** (total=134603): compression_not_detected=45914, regime_blocked=40361, basic_filters_failed=24368, breakout_not_detected=21573, volume_confirmation_failed=1949, rsi_reject=395, missing_fvg_or_orderblock=43
- **EVAL::RANGE_FADE** (total=133365): no_range_edge=117603, basic_filters_failed=15762
- **EVAL::SR_FLIP_RETEST** (total=129745): basic_filters_failed=31610, flip_close_not_confirmed=23490, long_break_volume_thin=18435, whipsaw_flip=17185, long_disabled=12288, reclaim_hold_failed=10966, retest_out_of_zone=7878, regime_blocked=3961, wick_quality_failed=1901, long_acceptance_not_held=1260, missing_fvg_or_orderblock=524, ema_alignment_reject=213, rsi_reject=34
- **EVAL::STANDARD** (total=114779): momentum_reject=42881, adx_reject=28434, sweeps_not_detected=16938, basic_filters_failed=11672, macd_reject=8946, ema_alignment_reject=4929, invalid_sl_geometry=693, rsi_reject=222, mtf_reject=64
- **EVAL::TREND_PULLBACK** (total=119456): h1_trend_not_aligned=41432, h1_pullback_not_confirmed=18287, basic_filters_failed=17785, ema_alignment_reject=17215, no_ema_reclaim_close=6822, ema_not_tested_prev=5862, body_conviction_fail=5222, rsi_reject=4144, prev_already_below_emas=1015, no_prev_low_break=637, prev_already_above_emas=489, no_prev_high_break=252, momentum_flat=184, missing_fvg_or_orderblock=51, momentum_reject=36, ema21_not_tagged=23
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=132934): breakout_not_found=71480, basic_filters_failed=35776, move_not_fresh=17825, breakout_stale=5960, retest_proximity_failed=1565, volume_spike_missing=287, move_exhausted=25, ema_alignment_reject=9, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=120780): momentum_reject=88203, recent_ticks_insufficient=25626, basic_filters_failed=6951

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=27): execution:overextended=27
- **DIVERGENCE_CONTINUATION** (total=1297): setup_compat:regime_VOLATILE_UNSUITABLE=966, context_floor=169, setup_compat:regime_BREAKOUT_EXPANSION=162
- **FAILED_AUCTION_RECLAIM** (total=6361): context_floor=2492, execution:overextended=1915, setup_compat:regime_STRONG_TREND=1895, setup_compat:regime_VOLATILE_UNSUITABLE=59
- **FUNDING_EXTREME_SIGNAL** (total=968): execution:trigger_not_confirmed=959, context_floor=9
- **LIQUIDATION_REVERSAL** (total=74): execution:trigger_not_confirmed=74
- **LIQUIDITY_SWEEP_REVERSAL** (total=7901): execution:trigger_not_confirmed=3191, execution:overextended=2794, setup_compat:regime_STRONG_TREND=1916
- **MA_CROSS_TREND_SHIFT** (total=10): setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_CLEAN_RANGE=2, execution:overextended=2, execution:trigger_not_confirmed=1, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=5388): execution:overextended=3092, setup_compat:regime_WEAK_TREND=1564, setup_compat:regime_STRONG_TREND=732
- **MOVER_AVWAP_SCALP** (total=5718): execution:trigger_not_confirmed=4091, execution:overextended=1627
- **MOVER_TREND_PULLBACK** (total=43565): execution:trigger_not_confirmed=27084, execution:overextended=16481
- **POST_DISPLACEMENT_CONTINUATION** (total=10): execution:overextended=10
- **QUIET_COMPRESSION_BREAK** (total=530): context_floor=363, execution:trigger_not_confirmed=163, execution:overextended=4
- **RANGE_FADE** (total=5835): execution:overextended=4613, setup_compat:regime_VOLATILE_UNSUITABLE=495, setup_compat:regime_WEAK_TREND=453, setup_compat:regime_STRONG_TREND=196, setup_compat:regime_BREAKOUT_EXPANSION=78
- **TREND_PULLBACK_EMA** (total=2927): setup_compat:regime_CLEAN_RANGE=1885, setup_compat:regime_DIRTY_RANGE=927, setup_compat:regime_VOLATILE_UNSUITABLE=115
- **VOLUME_SURGE_BREAKOUT** (total=100): context_floor=53, execution:overextended=47

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 264691 | 38.5% |
| RANGING | 214785 | 31.3% |
| TRENDING_DOWN | 89587 | 13.0% |
| TRENDING_UP | 87486 | 12.7% |
| VOLATILE | 30201 | 4.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1041**
- Average confidence gap to threshold: **14.25** (samples=1041) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: WLFIUSDT=111, HYPEUSDT=95, FILUSDT=57, XRPUSDT=51, XLMUSDT=46, BTCUSDT=44, 1000PEPEUSDT=43, TRXUSDT=37, TAOUSDT=34, ASTERUSDT=34

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 288 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 18 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 79 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 351 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 206 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 822 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 9 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 183 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1346 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 111 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4323 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 171 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 56 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 143 |
| SR_FLIP_RETEST | filtered | min_confidence | 1707 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 349 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2209 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 75 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 36 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 18 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 78.75 | 65.00 | -13.75 | 20.57 | 18.00 | 20.00 | 4.00 | 2.25 |
| DIVERGENCE_CONTINUATION | filtered | 306 | 50.96 | 62.98 | 12.02 | 19.89 | 19.87 | 16.92 | 0.19 | 18.20 |
| DIVERGENCE_CONTINUATION | kept | 79 | 67.09 | 65.00 | -2.09 | 20.09 | 19.66 | 17.06 | 3.78 | 4.04 |
| FAILED_AUCTION_RECLAIM | filtered | 557 | 47.50 | 63.48 | 15.98 | 20.44 | 19.67 | 20.00 | 4.11 | 16.34 |
| FAILED_AUCTION_RECLAIM | kept | 822 | 70.94 | 65.00 | -5.94 | 21.32 | 19.72 | 20.00 | 4.35 | 0.56 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 49.23 | 65.00 | 15.77 | 21.10 | 19.94 | 18.40 | 1.78 | 1.11 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 70.20 | 65.00 | -5.20 | 20.68 | 19.96 | 17.00 | 0.80 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 58 | 54.98 | 64.40 | 9.42 | 20.72 | 19.95 | 17.53 | 2.48 | 18.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 183 | 70.84 | 65.00 | -5.84 | 21.32 | 19.62 | 17.29 | 3.10 | 0.67 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 67.00 | 65.00 | -2.00 | 20.40 | 20.00 | 15.80 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 82.50 | 65.00 | -17.50 | 17.30 | 20.00 | 15.80 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 1457 | 48.40 | 63.41 | 15.01 | 19.87 | 18.54 | 15.80 | 4.29 | 14.41 |
| MOVER_TREND_PULLBACK | kept | 4323 | 75.54 | 65.00 | -10.54 | 19.35 | 18.62 | 15.80 | 4.40 | 0.69 |
| QUIET_COMPRESSION_BREAK | filtered | 227 | 52.79 | 65.00 | 12.21 | 21.47 | 19.58 | 20.00 | 0.00 | 7.35 |
| QUIET_COMPRESSION_BREAK | kept | 143 | 74.47 | 65.00 | -9.47 | 20.78 | 19.92 | 20.00 | 0.00 | 0.37 |
| SR_FLIP_RETEST | filtered | 2056 | 56.40 | 64.28 | 7.88 | 20.03 | 19.89 | 15.81 | 1.46 | 12.64 |
| SR_FLIP_RETEST | kept | 2209 | 69.53 | 65.00 | -4.53 | 20.40 | 19.97 | 15.73 | 1.90 | 0.50 |
| TREND_PULLBACK_EMA | filtered | 75 | 59.66 | 65.00 | 5.34 | 20.87 | 19.36 | 18.98 | 5.84 | 17.74 |
| TREND_PULLBACK_EMA | kept | 36 | 75.57 | 65.00 | -10.57 | 18.89 | 19.96 | 17.37 | 5.51 | 1.12 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 47.52 | 62.22 | 14.70 | 19.77 | 16.93 | 20.00 | 3.53 | 7.20 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 68.50 | 65.00 | -3.50 | 19.25 | 17.75 | 20.00 | 4.00 | 9.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 78.75 | 17.00 | 14.00 | 15.00 | 14.75 | 7.25 | 9.00 | 4.00 |
| DIVERGENCE_CONTINUATION | filtered | 306 | 50.96 | 22.88 | 14.50 | 6.06 | 13.05 | 5.98 | 7.72 | 0.19 |
| DIVERGENCE_CONTINUATION | kept | 79 | 67.09 | 24.19 | 8.89 | 5.92 | 13.99 | 6.59 | 7.95 | 3.78 |
| FAILED_AUCTION_RECLAIM | filtered | 557 | 47.50 | 21.62 | 14.49 | 7.26 | 12.12 | 6.20 | 5.71 | 4.11 |
| FAILED_AUCTION_RECLAIM | kept | 822 | 70.94 | 22.45 | 15.27 | 4.79 | 11.46 | 6.79 | 6.42 | 4.35 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 49.23 | 25.00 | 8.00 | 3.33 | 14.33 | 7.33 | 5.57 | 1.78 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 70.20 | 23.40 | 12.40 | 3.60 | 15.20 | 8.00 | 8.80 | 0.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 58 | 54.98 | 20.21 | 14.00 | 11.22 | 12.19 | 6.08 | 6.89 | 2.48 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 183 | 70.84 | 24.80 | 14.02 | 4.02 | 12.63 | 6.22 | 6.73 | 3.10 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 67.00 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 6.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 82.50 | 25.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 3.00 |
| MOVER_TREND_PULLBACK | filtered | 1457 | 48.40 | 18.56 | 18.02 | 8.31 | 13.23 | 5.59 | 5.50 | 4.29 |
| MOVER_TREND_PULLBACK | kept | 4323 | 75.54 | 19.52 | 18.02 | 7.80 | 12.37 | 5.50 | 8.69 | 4.40 |
| QUIET_COMPRESSION_BREAK | filtered | 227 | 52.79 | 19.54 | 17.01 | 12.07 | 14.04 | 6.35 | 3.95 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 143 | 74.47 | 17.67 | 18.00 | 11.50 | 14.17 | 7.08 | 7.48 | 0.00 |
| SR_FLIP_RETEST | filtered | 2056 | 56.40 | 18.78 | 16.30 | 5.78 | 12.54 | 6.05 | 8.13 | 1.46 |
| SR_FLIP_RETEST | kept | 2209 | 69.53 | 21.19 | 14.89 | 5.24 | 13.65 | 6.02 | 8.29 | 1.90 |
| TREND_PULLBACK_EMA | filtered | 75 | 59.66 | 19.35 | 18.00 | 7.50 | 14.00 | 6.07 | 6.64 | 5.84 |
| TREND_PULLBACK_EMA | kept | 36 | 75.57 | 17.22 | 18.00 | 7.71 | 14.17 | 5.22 | 8.94 | 5.51 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 47.52 | 18.33 | 16.22 | 13.33 | 11.00 | 5.00 | 2.30 | 3.53 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 68.50 | 17.00 | 14.00 | 12.00 | 15.50 | 6.50 | 9.00 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 78.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 306 | 50.96 | 0.00 | 0.00 | 0.00 | 0.00 | 2.97 | 0.00 | 0.00 | 0.00 | **2.97** |
| DIVERGENCE_CONTINUATION | kept | 79 | 67.09 | 0.00 | 0.00 | 0.06 | 0.00 | 0.46 | 0.00 | 0.00 | 0.00 | **0.52** |
| FAILED_AUCTION_RECLAIM | filtered | 557 | 47.50 | 0.00 | 0.00 | 0.00 | 0.00 | 10.43 | 0.00 | 0.00 | 0.00 | **10.43** |
| FAILED_AUCTION_RECLAIM | kept | 822 | 70.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | **0.41** |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 49.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 70.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 58 | 54.98 | 0.00 | 0.00 | 1.38 | 0.00 | 16.72 | 0.00 | 0.00 | 0.00 | **18.10** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 183 | 70.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.66 | 0.00 | 0.00 | 0.00 | **0.66** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 1 | 82.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 1457 | 48.40 | 0.00 | 0.00 | 1.94 | 0.00 | 2.48 | 0.00 | 0.00 | 0.44 | **4.86** |
| MOVER_TREND_PULLBACK | kept | 4323 | 75.54 | 0.00 | 0.00 | 0.32 | 0.00 | 0.35 | 0.00 | 0.00 | 0.00 | **0.67** |
| QUIET_COMPRESSION_BREAK | filtered | 227 | 52.79 | 0.00 | 0.00 | 0.00 | 0.00 | 1.56 | 0.00 | 0.00 | 4.82 | **6.38** |
| QUIET_COMPRESSION_BREAK | kept | 143 | 74.47 | 0.00 | 0.00 | 0.00 | 0.00 | 1.50 | 0.00 | 0.00 | 0.00 | **1.50** |
| SR_FLIP_RETEST | filtered | 2056 | 56.40 | 0.00 | 0.00 | 0.09 | 0.00 | 3.71 | 0.00 | 0.00 | 0.27 | **4.07** |
| SR_FLIP_RETEST | kept | 2209 | 69.53 | 0.00 | 0.00 | 0.08 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | **0.33** |
| TREND_PULLBACK_EMA | filtered | 75 | 59.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 36 | 75.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **0.20** |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 47.52 | 0.00 | 0.00 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 2.67 | **5.87** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 68.50 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=513 (11.4%) | WOULD_LOSE=1300 | WOULD_EXPIRE=2687 | pending (awaiting window)=500

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:FAILED_AUCTION_RECLAIM | 1141 | 6.4% | 442.4 | 137.4 | +0.27 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 113 | 0.0% | 15.7 | 0.0 | +0.14 | **KEEP** |
| dispatch_cooldown | 37 | 97.3% | 0.1 | 45.7 | -1.23 | **DROP** |
| dispatch_staleness_v2 | 376 | 8.8% | 139.6 | 18.1 | +0.32 | **KEEP** |
| level_still_in_play | 686 | 16.0% | 101.5 | 59.9 | +0.06 | **TUNE** |
| min_confidence | 1621 | 12.0% | 1108.1 | 226.3 | +0.54 | **KEEP** |
| quiet_scalp_block | 439 | 5.7% | 134.4 | 33.3 | +0.23 | **KEEP** |
| shadow_unit:SHADOW_FUNDING_FADE | 15 | 66.7% | 5.2 | 7.3 | -0.14 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 20 | 15.0% | 2.8 | 5.6 | -0.14 | **TUNE** |
| shadow_unit:SHADOW_RANGE_FADE | 52 | 53.8% | 12.4 | 66.5 | -1.04 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 68752 across 20 strategies; 1553 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 15479 | 44/15435/0 | 64% | +0.22 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.14R) |
| FAILED_AUCTION_RECLAIM | 12403 | 22/12381/0 | 50% | -0.02 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 11518 | 2/11516/0 | 42% | -0.19 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.14R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.30R) |
| DIVERGENCE_CONTINUATION | 6173 | 6/6167/0 | 49% | -0.03 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.22R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| QUIET_COMPRESSION_BREAK | 4956 | 0/4956/0 | 47% | +0.02 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MEAN_REVERT | 2999 | 0/2999/0 | 80% | +0.60 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_MEAN_REVERT | 2854 | 0/0/2854 | 38% | -0.04 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.82R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 2591 | 9/2582/0 | 42% | -0.11 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| SHADOW_RANGE_FADE | 2558 | 0/0/2558 | 38% | +0.16 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.18R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_FUNDING_FADE | 1842 | 0/0/1842 | 39% | -0.32 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.38R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| RANGE_FADE | 1804 | 0/1804/0 | 3% | -0.98 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.21R) |
| VOLUME_SURGE_BREAKOUT | 1181 | 12/1169/0 | 33% | -0.17 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 839 | 0/839/0 | 45% | -0.21 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 326 | 2/324/0 | 34% | -0.14 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| MOVER_AVWAP_SCALP | 275 | 18/257/0 | 36% | -0.33 | NY/MARKUP/CASCADE/BTC_FALLING (+0.55R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 253 | 5/248/0 | 51% | +0.26 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 214 | 0/0/214 | 45% | -0.11 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.03R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 11 | 0/11/0 | 36% | -0.62 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.31R (n=16, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING` -1.30R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 34 | 38% / +0.05R | 34 | 32% / -0.17R | -0.22 | **FIXED** |
| TREND_PULLBACK_EMA | 25 | 52% / -0.15R | 25 | 56% / +0.06R | +0.21 | **ATR** |
| MOVER_AVWAP_SCALP | 48 | 42% / -0.10R | 48 | 52% / +0.04R | +0.13 | **ATR** |
| MEAN_REVERT | 235 | 58% / +0.15R | 235 | 56% / +0.28R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 308 | 49% / -0.13R | 308 | 54% / -0.04R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 1628 | 47% / -0.11R | 1628 | 50% / -0.04R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 316 | 49% / -0.03R | 316 | 55% / +0.00R | +0.03 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1470 | 47% / -0.06R | 1470 | 47% / -0.04R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 695 | 46% / -0.02R | 695 | 45% / -0.04R | -0.02 | **FIXED** |
| RANGE_FADE | 137 | 2% / -1.04R | 137 | 2% / -1.04R | +0.01 | **ATR** |
| MOVER_TREND_PULLBACK | 1528 | 58% / +0.06R | 1528 | 61% / +0.06R | -0.00 | **FIXED** |
| BREAKDOWN_SHORT | 10 | 20% / -0.31R | 10 | 20% / -0.31R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 5 | 20% / -0.62R | 5 | 60% / -0.13R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 2 | 50% / -0.02R | 2 | 50% / -0.33R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 3 | 67% / +0.16R | 3 | 67% / +0.06R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 321 | 31% | -0.14R | 82 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 38 | 53% | +0.02R | 28 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 3 | 0% | -0.14R | 3 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._
- _no SAR pairs classified yet — pairs stamp at every post-scoring emission/suppression once `sar_exit_shadow_enabled` is on, and each needs a 48h forward window before both arms resolve_

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| QUIET_COMPRESSION_BREAK | dispatch_cooldown | 24 | 95.8% | -1.81 | **DROP** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 52 | 53.8% | -1.04 | **DROP** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 21 | 81.0% | -0.30 | **DROP** |
| DIVERGENCE_CONTINUATION | min_confidence | 128 | 45.3% | -0.30 | **DROP** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 5 | 100.0% | -0.24 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | level_still_in_play | 126 | 42.1% | -0.18 | **TUNE** |
| MOVER_TREND_PULLBACK | dispatch_cooldown | 13 | 100.0% | -0.16 | **INSUFFICIENT_SAMPLE** |
| LIQUIDITY_SWEEP_REVERSAL | dispatch_staleness_v2 | 7 | 100.0% | -0.15 | **INSUFFICIENT_SAMPLE** |
| SHADOW_FUNDING_FADE | shadow_unit:SHADOW_FUNDING_FADE | 15 | 66.7% | -0.14 | **INSUFFICIENT_SAMPLE** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 20 | 15.0% | -0.14 | **TUNE** |
| MOVER_TREND_PULLBACK | quiet_scalp_block | 86 | 14.0% | -0.07 | **TUNE** |
| QUIET_COMPRESSION_BREAK | level_still_in_play | 26 | 0.0% | +0.10 | **KEEP** |
| SR_FLIP_RETEST | level_still_in_play | 337 | 10.4% | +0.13 | **KEEP** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 113 | 0.0% | +0.14 | **KEEP** |
| FAILED_AUCTION_RECLAIM | level_still_in_play | 171 | 0.0% | +0.15 | **KEEP** |
| QUIET_COMPRESSION_BREAK | quiet_scalp_block | 33 | 0.0% | +0.16 | **KEEP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 8 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 201 | 2.0% | +0.19 | **KEEP** |
| FAILED_AUCTION_RECLAIM | context_floor:FAILED_AUCTION_RECLAIM | 1141 | 6.4% | +0.27 | **KEEP** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 361 | 7.2% | +0.34 | **KEEP** |
| SR_FLIP_RETEST | min_confidence | 777 | 15.8% | +0.36 | **KEEP** |
| DIVERGENCE_CONTINUATION | quiet_scalp_block | 11 | 0.0% | +0.46 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | quiet_scalp_block | 92 | 6.5% | +0.49 | **KEEP** |
| FAILED_AUCTION_RECLAIM | min_confidence | 69 | 0.0% | +0.82 | **KEEP** |
| LIQUIDITY_SWEEP_REVERSAL | quiet_scalp_block | 16 | 18.8% | +0.85 | **INSUFFICIENT_SAMPLE** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 19 · alerting: **0** · boot grace active: True

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64518.80 | 0 |
| candle_coverage | ok | 77/77 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +27 / upstream +44 | 0 |
| edge_reconciliation | ok | boot grace (MOVER_TREND_PULLBACK realized−counterfactual=-0.43R (bound 0.3) (streak 1/6)) | 0 |
| emission_controller | ok | last cycle 316s ago; live_overrides=17 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | boot grace (upstream +29 but output +0 (streak 1/6)) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | backlog 44 detections since last emission | 0 |
| mean_revert_path | ok | output +44 / upstream +29 | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.98R over n=1804 — emitting them would lose money | 0 |
| range_fade_path | ok | output +94 / upstream +29 | 0 |
| sar_exit_shadow | ok | output +6 / upstream +29 | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +96 / upstream +29 | 0 |
| suppression_audit | ok | output +29 / upstream +44 | 0 |
| tuned_variants | ok | seen=48 stamped=1 skipped=47 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3573174`
- `Path funnel` emissions: `86`
- `Regime distribution` emissions: `86`
- `QUIET_SCALP_BLOCK` events: `1041`
- `confidence_gate` events: `12575`
- `free_channel_post` events: `10`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **5**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 4130 | 4130 | 4130 | 0 |
| futures_liq | 4 | 4308 | 4569 | 5693 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **10**

| Source | Count |
|---|---:|
| signal_close | 5 |
| signal_highlight | 3 |
| regime_shift | 2 |

- By severity: HIGH=10

## Dependency readiness
- cvd: presence[present=551984] state[populated=551984] buckets[many=551984] sources[none] quality[none]
- funding_rate: presence[absent=32338, present=519646] state[empty=32338, populated=519646] buckets[few=519646, none=32338] sources[none] quality[none]
- liquidation_clusters: presence[absent=338735, present=213249] state[empty=338735, populated=213249] buckets[few=163361, none=338735, some=49888] sources[none] quality[none]
- oi_snapshot: presence[absent=24431, present=527553] state[empty=24431, populated=527553] buckets[many=527553, none=24431] sources[none] quality[none]
- order_book: presence[absent=142640, present=409344] state[populated=409344, unavailable=142640] buckets[few=409344, none=142640] sources[book_ticker=409344, unavailable=142640] quality[none=142640, top_of_book_only=409344]
- orderblocks: presence[absent=551984] state[empty=551984] buckets[none=551984] sources[not_implemented=551984] quality[none]
- recent_ticks: presence[absent=1652, present=550332] state[empty=1652, populated=550332] buckets[many=550332, none=1652] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.5642409324646` sec
- Median create→first breach: `4861.2154269218445` sec
- Median create→terminal: `4862.437134981155` sec
- Median first breach→terminal: `1.4735970497131348` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 2.202 | 8658.908194422722 | 8661.835336446762 |
| MOVER_TREND_PULLBACK | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | 1.6609 | 333.4763309955597 | 340.3901779651642 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 18732 | 102 | 4804 | 0.0 | 0.0 | None | None | 13928 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3300 | 4 | 3187 | 0.0 | 0.0 | None | None | 113 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-25`
- Gating Δ: `51734`
- No-generation Δ: `903025`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -2.1903, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 2.1903, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 3.8246, "current_avg_pnl": 1.6609, "current_win_rate": 0.0, "previous_avg_pnl": -2.1637, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -45, "geometry_changed_delta": 0, "geometry_preserved_delta": 3896, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 97, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
