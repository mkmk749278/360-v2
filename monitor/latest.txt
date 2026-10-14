# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `972` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 136 | 136 | 136 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 16450 | 16450 | 14799 | 17 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 105648 | 105664 | 47 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 87271 | 87272 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 86784 | 83448 | 3809 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 87317 | 86695 | 710 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 88798 | 88672 | 160 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 77626 | 77643 | 11 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 87408 | 87453 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 87466 | 85463 | 2863 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 110810 | 117177 | 1006 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 105716 | 97399 | 13328 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 88289 | 88290 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 87278 | 87316 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 86746 | 86661 | 121 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 88331 | 87341 | 1292 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 86205 | 86467 | 234 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 75367 | 71069 | 4631 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 75707 | 75309 | 516 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 105579 | 105607 | 31 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 77660 | 77700 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2975 | 2975 | 2738 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 659 | 659 | 499 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 22 | 22 | 9 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 26896 | 26896 | 25709 | 18 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 4 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8724 | 8724 | 6595 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2946 | 2946 | 1937 | 29 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 40192 | 40192 | 26268 | 304 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1001 | 1001 | 938 | 21 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3403 | 3403 | 3053 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 891 | 891 | 502 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3184 | 3184 | 2410 | 36 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 169 | 169 | 104 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=105664): breakout_not_found=64641, basic_filters_failed=24433, move_not_fresh=11987, breakout_stale=3246, retest_proximity_failed=1205, volume_spike_missing=111, move_exhausted=30, missing_fvg_or_orderblock=11
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=87272): cls_disabled_merged_into_lsr=87272
- **EVAL::DIVERGENCE_CONTINUATION** (total=83448): cvd_divergence_failed=30656, h1_trend_not_aligned=26452, basic_filters_failed=18252, ema_alignment_reject=6798, retest_proximity_failed=854, missing_fvg_or_orderblock=436
- **EVAL::FAILED_AUCTION_RECLAIM** (total=86695): auction_not_detected=61310, basic_filters_failed=17884, reclaim_hold_failed=2678, regime_blocked=2655, tail_too_small=2162, rsi_reject=6
- **EVAL::FUNDING_EXTREME** (total=88672): funding_not_extreme=63370, basic_filters_failed=17570, missing_funding_rate=5780, ema_alignment_reject=1177, rsi_reject=424, cvd_divergence_failed=174, momentum_reject=148, missing_fvg_or_orderblock=29
- **EVAL::LIQUIDATION_REVERSAL** (total=77643): cascade_threshold_not_met=58167, basic_filters_failed=18839, cvd_divergence_failed=355, rsi_reject=247, missing_fvg_or_orderblock=28, volume_spike_missing=7
- **EVAL::MA_CROSS_TREND_SHIFT** (total=87453): no_ma_cross=67706, basic_filters_failed=18274, ma_cross_cooldown=1128, ma_cross_htf_misaligned=345
- **EVAL::MEAN_REVERT** (total=85463): no_extension=69609, basic_filters_failed=15854
- **EVAL::MOVER_AVWAP_SCALP** (total=117177): no_avwap_tag=43092, no_mover_leg=29545, basic_filters_failed=24717, avwap_slope_against=14660, avwap_reclaim_no_volume=3125, no_avwap_reclaim=2034, anchor_too_recent=4
- **EVAL::MOVER_TREND_PULLBACK** (total=97399): mover_run_too_small=52792, basic_filters_failed=24588, no_reclaim=17682, no_pullback_tag=2337
- **EVAL::OPENING_RANGE_BREAKOUT** (total=88290): feature_disabled=88290
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=87316): regime_blocked=52105, breakout_not_found=28069, basic_filters_failed=5640, adx_reject=1445, ema_alignment_reject=57
- **EVAL::QUIET_COMPRESSION_BREAK** (total=86661): regime_blocked=37693, compression_not_detected=30321, basic_filters_failed=12225, breakout_not_detected=5892, volume_confirmation_failed=507, rsi_reject=14, missing_fvg_or_orderblock=9
- **EVAL::RANGE_FADE** (total=87341): no_range_edge=71484, basic_filters_failed=15857
- **EVAL::SR_FLIP_RETEST** (total=86467): flip_close_not_confirmed=60079, basic_filters_failed=17845, regime_blocked=2642, retest_out_of_zone=1580, long_break_volume_thin=1578, h1_break_not_confirmed=1334, reclaim_hold_failed=814, ema_alignment_reject=261, wick_quality_failed=149, long_acceptance_not_held=99, whipsaw_flip=84, missing_fvg_or_orderblock=2
- **EVAL::STANDARD** (total=71069): momentum_reject=19189, adx_reject=16651, basic_filters_failed=12340, ema_alignment_reject=9199, sweeps_not_detected=6832, macd_reject=5663, htf_poi_unanchored=1114, rsi_reject=40, invalid_sl_geometry=35, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=75309): h1_trend_not_aligned=30221, ema_alignment_reject=11890, basic_filters_failed=9827, ema_not_tested_prev=6185, h1_pullback_not_confirmed=6150, no_ema_reclaim_close=4237, body_conviction_fail=2667, rsi_reject=2186, prev_already_below_emas=940, no_prev_low_break=413, prev_already_above_emas=179, momentum_flat=152, no_prev_high_break=127, ema21_not_tagged=74, missing_fvg_or_orderblock=32, momentum_reject=29
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=105607): breakout_not_found=56976, basic_filters_failed=24425, move_not_fresh=16865, breakout_stale=4962, retest_proximity_failed=2138, volume_spike_missing=182, move_exhausted=48, missing_fvg_or_orderblock=11
- **EVAL::WHALE_MOMENTUM** (total=77700): momentum_reject=56743, recent_ticks_insufficient=14943, basic_filters_failed=6014

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=5): execution:overextended=5
- **DIVERGENCE_CONTINUATION** (total=474): setup_compat:regime_VOLATILE_UNSUITABLE=407, setup_compat:regime_BREAKOUT_EXPANSION=67
- **FAILED_AUCTION_RECLAIM** (total=859): setup_compat:regime_STRONG_TREND=559, execution:overextended=202, context_floor=90, setup_compat:regime_VOLATILE_UNSUITABLE=8
- **FUNDING_EXTREME_SIGNAL** (total=563): execution:trigger_not_confirmed=549, context_floor=14
- **LIQUIDATION_REVERSAL** (total=22): execution:trigger_not_confirmed=22
- **LIQUIDITY_SWEEP_REVERSAL** (total=7471): setup_compat:regime_STRONG_TREND=3033, execution:trigger_not_confirmed=2837, execution:overextended=1601
- **MA_CROSS_TREND_SHIFT** (total=4): execution:trigger_not_confirmed=2, setup_compat:regime_CLEAN_RANGE=1, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=6897): setup_compat:regime_WEAK_TREND=3537, setup_compat:regime_STRONG_TREND=2823, execution:overextended=514, entry_quality=23
- **MOVER_AVWAP_SCALP** (total=1543): execution:overextended=924, execution:trigger_not_confirmed=573, entry_quality=46
- **MOVER_TREND_PULLBACK** (total=16433): execution:trigger_not_confirmed=8967, execution:overextended=5731, entry_quality=1735
- **QUIET_COMPRESSION_BREAK** (total=24): execution:trigger_not_confirmed=24
- **RANGE_FADE** (total=2659): setup_compat:regime_STRONG_TREND=1229, setup_compat:regime_WEAK_TREND=1185, execution:overextended=196, setup_compat:regime_VOLATILE_UNSUITABLE=33, setup_compat:regime_BREAKOUT_EXPANSION=16
- **TREND_PULLBACK_EMA** (total=2777): setup_compat:regime_CLEAN_RANGE=1805, setup_compat:regime_DIRTY_RANGE=735, entry_quality=194, setup_compat:regime_VOLATILE_UNSUITABLE=43

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 199698 | 34.9% |
| QUIET | 129046 | 22.6% |
| TRENDING_UP | 127445 | 22.3% |
| TRENDING_DOWN | 99388 | 17.4% |
| VOLATILE | 16039 | 2.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **165**
- Average confidence gap to threshold: **10.97** (samples=165) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: CAPUSDT=29, RLCUSDT=23, OGNUSDT=21, ETHUSDT=15, USUSDT=13, BTWUSDT=11, BNBUSDT=7, XLMUSDT=6, DASHUSDT=5, SOLUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 308 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 89 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 30 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 15 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 261 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 13 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 90 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 104 |
| MEAN_REVERT | kept | min_confidence_pass | 18 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 369 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 5 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 222 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2548 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 94 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4225 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 28 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 2 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 27 |
| SR_FLIP_RETEST | filtered | min_confidence | 34 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 309 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 135 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 23 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 152 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 63 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 315 | 55.33 | 64.10 | 8.77 | 20.44 | 19.83 | 17.30 | 2.10 | 13.14 |
| DIVERGENCE_CONTINUATION | kept | 89 | 66.68 | 65.00 | -1.68 | 20.63 | 19.88 | 18.64 | 1.52 | 3.95 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 46.72 | 60.00 | 13.28 | 22.01 | 20.00 | 20.00 | 2.92 | 5.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 53.04 | 61.80 | 8.76 | 20.28 | 17.86 | 17.00 | 2.20 | 7.00 |
| LIQUIDATION_REVERSAL | filtered | 4 | 69.00 | 10.00 | -59.00 | 20.80 | 8.00 | 18.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 274 | 50.36 | 64.57 | 14.21 | 20.72 | 19.57 | 17.86 | 0.72 | 4.35 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 90 | 73.37 | 65.00 | -8.37 | 19.86 | 18.14 | 17.14 | 3.31 | 0.13 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 49.40 | 61.00 | 11.60 | 17.50 | 19.80 | 15.80 | 0.00 | 4.80 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.50 | 65.00 | -1.50 | 20.90 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 104 | 59.12 | 64.30 | 5.18 | 21.04 | 14.15 | 16.51 | 0.00 | 10.00 |
| MEAN_REVERT | kept | 18 | 70.98 | 65.00 | -5.98 | 21.34 | 14.00 | 17.31 | 0.00 | 2.67 |
| MOVER_AVWAP_SCALP | filtered | 374 | 54.29 | 64.06 | 9.77 | 21.01 | 15.69 | 15.80 | 3.83 | 4.79 |
| MOVER_AVWAP_SCALP | kept | 222 | 79.56 | 65.00 | -14.56 | 20.06 | 15.45 | 15.80 | 4.54 | 0.46 |
| MOVER_TREND_PULLBACK | filtered | 2642 | 56.77 | 64.32 | 7.55 | 20.60 | 18.34 | 15.80 | 4.26 | 18.89 |
| MOVER_TREND_PULLBACK | kept | 4225 | 76.22 | 65.00 | -11.22 | 20.19 | 18.35 | 15.80 | 4.39 | 2.04 |
| QUIET_COMPRESSION_BREAK | filtered | 30 | 53.46 | 65.00 | 11.54 | 22.47 | 19.80 | 20.00 | 0.00 | 15.49 |
| QUIET_COMPRESSION_BREAK | kept | 27 | 72.04 | 65.00 | -7.04 | 21.59 | 19.86 | 20.00 | 0.00 | 3.92 |
| SR_FLIP_RETEST | filtered | 34 | 61.00 | 65.00 | 4.00 | 20.91 | 20.00 | 15.20 | 1.00 | 4.00 |
| SR_FLIP_RETEST | kept | 309 | 71.20 | 65.00 | -6.20 | 21.09 | 20.00 | 15.55 | 2.11 | 2.54 |
| TREND_PULLBACK_EMA | filtered | 158 | 58.70 | 64.11 | 5.41 | 20.87 | 19.16 | 19.12 | 4.48 | 19.64 |
| TREND_PULLBACK_EMA | kept | 152 | 78.79 | 65.00 | -13.79 | 20.20 | 19.32 | 18.07 | 5.03 | -1.10 |
| VOLUME_SURGE_BREAKOUT | filtered | 63 | 53.40 | 64.30 | 10.90 | 21.25 | 16.51 | 20.00 | 3.83 | 6.75 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 315 | 55.33 | 23.55 | 10.13 | 5.91 | 12.96 | 5.57 | 8.37 | 2.10 |
| DIVERGENCE_CONTINUATION | kept | 89 | 66.68 | 23.38 | 16.88 | 3.67 | 12.58 | 5.10 | 8.57 | 1.52 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 46.72 | 25.00 | 14.00 | 3.50 | 7.83 | 9.17 | 4.30 | 2.92 |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 53.04 | 25.00 | 16.67 | 3.00 | 13.53 | 5.67 | 6.97 | 2.20 |
| LIQUIDATION_REVERSAL | filtered | 4 | 69.00 | 25.00 | 8.00 | 15.00 | 8.00 | 5.00 | 4.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 274 | 50.36 | 23.62 | 16.55 | 6.11 | 11.61 | 5.06 | 4.93 | 0.72 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 90 | 73.37 | 23.22 | 14.53 | 6.47 | 10.60 | 7.47 | 8.06 | 3.31 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 49.40 | 25.00 | 14.00 | 3.00 | 12.00 | 8.50 | 6.70 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.50 | 17.00 | 14.00 | 3.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 104 | 59.12 | 20.15 | 17.23 | 9.98 | 13.05 | 5.00 | 6.59 | 0.00 |
| MEAN_REVERT | kept | 18 | 70.98 | 20.11 | 15.33 | 12.50 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 374 | 54.29 | 17.56 | 18.01 | 12.17 | 12.83 | 4.85 | 3.67 | 3.83 |
| MOVER_AVWAP_SCALP | kept | 222 | 79.56 | 19.24 | 18.27 | 12.20 | 14.13 | 6.89 | 7.96 | 4.54 |
| MOVER_TREND_PULLBACK | filtered | 2642 | 56.77 | 17.92 | 18.00 | 7.75 | 12.72 | 6.23 | 9.15 | 4.26 |
| MOVER_TREND_PULLBACK | kept | 4225 | 76.22 | 19.17 | 18.00 | 7.88 | 13.18 | 6.67 | 9.04 | 4.39 |
| QUIET_COMPRESSION_BREAK | filtered | 30 | 53.46 | 18.07 | 17.73 | 10.60 | 14.00 | 5.97 | 6.10 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 27 | 72.04 | 19.37 | 17.70 | 10.89 | 14.44 | 7.04 | 6.74 | 0.00 |
| SR_FLIP_RETEST | filtered | 34 | 61.00 | 17.00 | 18.00 | 3.00 | 11.00 | 5.00 | 10.00 | 1.00 |
| SR_FLIP_RETEST | kept | 309 | 71.20 | 21.87 | 17.94 | 3.99 | 12.42 | 5.92 | 9.50 | 2.11 |
| TREND_PULLBACK_EMA | filtered | 158 | 58.70 | 16.56 | 18.00 | 8.81 | 14.76 | 6.59 | 9.14 | 4.48 |
| TREND_PULLBACK_EMA | kept | 152 | 78.79 | 19.53 | 18.00 | 7.77 | 14.76 | 5.84 | 8.53 | 5.03 |
| VOLUME_SURGE_BREAKOUT | filtered | 63 | 53.40 | 18.78 | 18.00 | 12.00 | 14.00 | 5.00 | 3.54 | 3.83 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 315 | 55.33 | 0.00 | 0.00 | 1.85 | 0.00 | 1.56 | 0.04 | 0.00 | 0.00 | **3.45** |
| DIVERGENCE_CONTINUATION | kept | 89 | 66.68 | 0.00 | 0.00 | 1.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.65** |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 46.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 15 | 53.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 4 | 69.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 274 | 50.36 | 0.00 | 0.00 | 0.78 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.82** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 90 | 73.37 | 0.00 | 0.00 | 0.05 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.13** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 49.40 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 66.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 104 | 59.12 | 0.00 | 0.00 | 3.85 | 0.00 | 0.58 | 0.00 | 0.00 | 0.00 | **4.43** |
| MEAN_REVERT | kept | 18 | 70.98 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |
| MOVER_AVWAP_SCALP | filtered | 374 | 54.29 | 0.00 | 0.00 | 0.34 | 0.00 | 1.32 | 0.00 | 0.00 | 1.86 | **3.52** |
| MOVER_AVWAP_SCALP | kept | 222 | 79.56 | 0.00 | 0.00 | 0.10 | 0.00 | 0.22 | 0.00 | 0.00 | 0.05 | **0.37** |
| MOVER_TREND_PULLBACK | filtered | 2642 | 56.77 | 0.32 | 0.00 | 1.67 | 0.00 | 0.44 | 0.02 | 0.00 | 0.00 | **2.45** |
| MOVER_TREND_PULLBACK | kept | 4225 | 76.22 | 0.00 | 0.00 | 0.56 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.66** |
| QUIET_COMPRESSION_BREAK | filtered | 30 | 53.46 | 0.00 | 0.00 | 0.00 | 0.00 | 2.72 | 2.13 | 0.00 | 2.52 | **7.37** |
| QUIET_COMPRESSION_BREAK | kept | 27 | 72.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.64 | 0.00 | 0.00 | 0.00 | **0.64** |
| SR_FLIP_RETEST | filtered | 34 | 61.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 309 | 71.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 158 | 58.70 | 0.00 | 0.00 | 0.81 | 0.00 | 5.61 | 0.00 | 0.00 | 0.00 | **6.42** |
| TREND_PULLBACK_EMA | kept | 152 | 78.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.08** |
| VOLUME_SURGE_BREAKOUT | filtered | 63 | 53.40 | 0.00 | 0.00 | 1.14 | 0.00 | 0.00 | 0.00 | 0.00 | 2.11 | **3.25** |

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
- Outcomes recorded: **142671 held of 493511 seen** across 21 strategies; 3239 cells past the sample floor; **1634 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 43754 | 640/43114/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/MARKDOWN/EXPANDED/BTC_FALLING/ALTCOIN (-1.20R) |
| MOVER_AVWAP_SCALP | 18399 | 186/18213/0 | 41% | -0.24 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11008 | 120/10888/0 | 36% | -0.31 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 9870 | 70/9800/0 | 50% | -0.03 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.39R) | ASIA/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (-1.22R) |
| TREND_PULLBACK_EMA | 8176 | 40/8136/0 | 42% | -0.18 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| LIQUIDITY_SWEEP_REVERSAL | 7255 | 81/7174/0 | 33% | -0.52 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| SHADOW_MEAN_REVERT | 6976 | 0/0/6976 | 43% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.45R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.95R) |
| SHADOW_RANGE_FADE | 6324 | 0/0/6324 | 37% | -0.09 | NY/MARKDOWN/EXPANDED/BTC_FALLING (+0.55R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 5870 | 364/5506/0 | 52% | -0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5516 | 0/0/5516 | 34% | -0.41 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3659 | 43/3616/0 | 42% | -0.22 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| SR_FLIP_RETEST | 2954 | 15/2939/0 | 48% | -0.23 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+0.87R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| VOLUME_SURGE_BREAKOUT | 2842 | 0/2842/0 | 35% | -0.27 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2789 | 2/2787/0 | 30% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| RANGE_FADE | 1251 | 4/1247/0 | 43% | -0.27 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1228 | 0/0/1228 | 54% | -0.04 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.08R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 324 | 0/324/0 | 35% | -0.49 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 104 | 18/86/0 | 44% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 204 | 26% / -0.59R | 204 | 51% / -0.16R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 18 | 33% / -0.45R | 18 | 61% / -0.15R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 689 | 42% / -0.26R | 689 | 55% / -0.05R | +0.21 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1194 | 44% / -0.34R | 1194 | 55% / -0.14R | +0.19 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 135 | 35% / -0.23R | 135 | 44% / -0.09R | +0.14 | **ATR** |
| MOVER_AVWAP_SCALP | 1599 | 43% / -0.19R | 1599 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1067 | 40% / -0.25R | 1067 | 42% / -0.14R | +0.11 | **ATR** |
| RANGE_FADE | 59 | 34% / -0.36R | 59 | 41% / -0.26R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| MA_CROSS_TREND_SHIFT | 32 | 41% / -0.20R | 32 | 44% / -0.10R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 259 | 46% / -0.26R | 259 | 49% / -0.18R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 7153 | 50% / -0.09R | 7153 | 55% / -0.00R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1016 | 48% / -0.10R | 1016 | 54% / -0.04R | +0.06 | **ATR** |
| MEAN_REVERT | 257 | 51% / -0.08R | 257 | 50% / -0.08R | -0.00 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 972 | 46% / -0.16R | 972 | 46% / -0.16R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10003 | 28% | -0.25R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1599 | 47% | -0.07R | 214 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 84 | 46% | -0.10R | 53 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 925 | 36% / -0.18R | +0.88 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1249 | 40% / -0.18R | +0.83 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2063 | 34% / -0.13R | +0.71 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9040 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1152 | 37% / -0.07R | +0.21 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 945 | 34% / -0.19R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 870 | 33% / -0.22R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 204 | 29% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 267 | 31% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 214 | 51% / +0.03R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 45 | 36% / -0.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 257 | 33% / -0.36R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 49 | 27% / -0.41R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 24 | 46% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×510]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 185/6) (sustained 185 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 7/6) (sustained 7 cycles)
- **ALERT** `edge_reconciliation` — TREND_PULLBACK_EMA realized−counterfactual=+0.60R (bound 0.3) (streak 420/6) (sustained 420 cycles)
- **ALERT** `tuned_variants` — 344 non-stamps — atr_arm_uncomputable=344 (seen=12571 stamped=1348 skipped=10879) (streak 420/6) (sustained 420 cycles)
- **ALERT** `auto_dispatch` — 68 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=69) (streak 410/3) (sustained 410 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 43 fed / 0 quiet / 0 never delivered of 43 subscribed; 54445404 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 21 arms current, none stalled; covering 1509/1509 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 39 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 2/12) | 2 |
| auto_dispatch | violating | 68 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=69) (streak 410/3) | 410 |
| binance_ip_weight | ok | peak 212/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 83436.20 | 0 |
| candle_coverage | ok | 91/91 symbols with ≥20 15m candles, 91/91 updated within 45m [fresh=91; 75 Tier-1 futures + 18 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 3005 dup bars, 0 undedupable; ws 0 out-of-order, 449 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 55 cohorts, 19 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +103 / upstream +32 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1860/1878 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 3 promoted today, nothing refused | 0 |
| dark_resolution | ok | 129 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1857/1875 signals (99%) | 0 |
| depth_feed | ok | 43/43 books fresh (stale 0, never 0, thin 0); 20444270 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | TREND_PULLBACK_EMA realized−counterfactual=+0.60R (bound 0.3) (streak 420/6) | 420 |
| emission_controller | ok | last cycle 719s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×510]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 185/6) | 185 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 7/6) | 7 |
| firestore_read_budget | ok | 1,360 reads/day of 50,000 [engine 1,321, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5160 sealed bars over 43 symbols; 1365 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +15 / upstream +366 | 0 |
| indicator_cache_key | ok | 168022 frozen value(s) avoided; 519913 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.23R over n=3616 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +21 / upstream +366 | 0 |
| mover_admission_metadata | ok | 927 symbols known, 221 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 18 held, 18 with scan counts, 18 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2702569 evicted (sampled: execution:trigger_not_confirmed 400/974630, execution:overextended 400/861297, setup_compat:regime_STRONG_TREND 400/440967) | 0 |
| price_action_lane | ok | 1155145 evaluated, 1203 emitted; layer1 1203 stamped / 0 blind; cooldown=154456, delta_opposed=96792, no_footprint=499446, no_opposing_target=1652, no_sweep=304746, rr_below_floor=96850 | 0 |
| promoted_pair_integrity | ok | 18/18 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.27R over n=1247 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +13 / upstream +366 | 0 |
| sar_alignment_crosscheck | ok | 799/23757 disagreed (3.4%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +366 | 0 |
| sar_hold_arm | ok | 1846 held arms settled, 154 unscored, 40 still walking (35 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 6/35 unfetchable (17%); top cause: located bar does not contain the stamp; symbols: ASTERUSDT, BATUSDT, FILUSDT, GTCUSDT, MAGICUSDT +1 more | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 39 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 2/12) | 2 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 435 records await one (29 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 27.39s, worst 160.55s over 12643 lifetime cycles; lifetime 152 over 60s, 9 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.5s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 483619 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 59s ago (1.05s to run, worst 124.75s), 786 overrun(s) of 9138 cycles, TTL 900s; slowest engine_state=9.17s, positions_diag=9.1s, tickers=8.59s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=779, gate reads=0, withheld=779) | 0 |
| staleness_v2_shadow | ok | output +1 / upstream +1 | 0 |
| strategy_edge | ok | output +26 / upstream +366 | 0 |
| structural_snap | ok | 6000/6000 measured, 22 blind, 0 levels moved (refusals: redetect_cooldown=1162) | 0 |
| structural_veto_lane | ok | 2147 stamped; 0 with no readable level book, 79 with clear air ahead, 1509 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +366 / upstream +32 | 0 |
| tuned_variants | violating | 344 non-stamps — atr_arm_uncomputable=344 (seen=12571 stamped=1348 skipped=10879) (streak 420/6) | 420 |
| unlock_shorts | ok | 15 open, 42 scheduled, calendar 13.8h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 41 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2594006`
- `Path funnel` emissions: `64`
- `Regime distribution` emissions: `64`
- `QUIET_SCALP_BLOCK` events: `165`
- `confidence_gate` events: `9177`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **44**
- Total REST-fallback activations: **13**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 15 | 7689 | 17583 | 21660 | 0 |
| futures_depth | 18 | 3957 | 24657 | 38404 | 0 |
| futures_liq | 10 | 3585 | 6775 | 17576 | 0 |
| futures_mover | 1 | 2425 | 2425 | 2425 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 13 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=476836] state[populated=476836] buckets[many=476836] sources[none] quality[none]
- funding_rate: presence[absent=79187, present=397649] state[empty=79187, populated=397649] buckets[few=397649, none=79187] sources[none] quality[none]
- liquidation_clusters: presence[absent=278240, present=198596] state[empty=278240, populated=198596] buckets[few=167179, none=278240, some=31417] sources[none] quality[none]
- oi_snapshot: presence[absent=79187, present=397649] state[empty=79187, populated=397649] buckets[few=617, many=393580, none=79187, some=3452] sources[none] quality[none]
- order_book: presence[absent=141029, present=335807] state[populated=335807, unavailable=141029] buckets[few=335807, none=141029] sources[book_ticker=335807, unavailable=141029] quality[none=141029, top_of_book_only=335807]
- orderblocks: presence[absent=476836] state[empty=476836] buckets[none=476836] sources[measured_dark=476836] quality[none]
- recent_ticks: presence[present=476836] state[populated=476836] buckets[many=476836] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.826758623123169` sec
- Median create→first breach: `8735.71657049656` sec
- Median create→terminal: `8735.71679508686` sec
- Median first breach→terminal: `7.855892181396484e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MA_CROSS_TREND_SHIFT | 1 | 1 | 1.155785086867706 | 1.1131063946587587 | 1.0383419701959677 | 1 | 0 |
| MOVER_AVWAP_SCALP | 2 | 2 | 1.6263300091399941 | 2.34686645768598 | 0.7227580413776511 | 0 | 2 |
| MOVER_TREND_PULLBACK | 18 | 18 | 3.68284589506489 | 3.0 | 1.2519282943868806 | 15 | 3 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.4456484163757621 | 1.7335412311819545 | 0.9261258969029469 | 0 | 4 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1558 | 17201.764847040176 | 17201.764920949936 |
| MOVER_AVWAP_SCALP | 2 | 2 | 50.0 | 0.0 | 50.0 | 0.0 | 1.054 | 20305.400109529495 | 20307.415070056915 |
| MOVER_TREND_PULLBACK | 18 | 18 | 38.9 | 16.7 | 38.9 | 0.0 | 1.0703 | 6514.279232382774 | 6514.27930688858 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 0.0 | 40.0 | 0.0 | 0.0 | -0.655 | 13837.421021938324 | 13837.421042919159 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 891 | 8 | 502 | 0.0 | 0.0 | None | None | 389 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3184 | 36 | 2410 | 0.0 | 0.0 | None | None | 774 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-106`
- Gating Δ: `-30233`
- No-generation Δ: `-161018`
- Fast failures Δ: `-3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.8143, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -1.8143, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.7659, "current_avg_pnl": 1.0703, "current_win_rate": 38.9, "previous_avg_pnl": -0.6956, "previous_win_rate": 16.7, "win_rate_delta": 22.2}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.9709, "current_avg_pnl": -0.655, "current_win_rate": 0.0, "previous_avg_pnl": 0.3159, "previous_win_rate": 37.5, "win_rate_delta": -37.5}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 256, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 27, "geometry_changed_delta": 0, "geometry_preserved_delta": 649, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1709.65, "median_terminal_delta_sec": -1713.41, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
