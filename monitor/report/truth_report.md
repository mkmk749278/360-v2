# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `709` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1612 | 1612 | 695 | 8 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 41444 | 41444 | 37459 | 29 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 195944 | 195585 | 392 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 189608 | 189631 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 189008 | 181956 | 7636 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 189683 | 183578 | 6421 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 201500 | 201361 | 178 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 195854 | 195862 | 11 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 190007 | 190062 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_TREND_PULLBACK | 195982 | 178991 | 18079 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 197092 | 197101 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 189635 | 189661 | 14 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 188948 | 188260 | 742 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 184512 | 173588 | 15309 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 182741 | 171596 | 11672 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 183273 | 182759 | 559 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 195900 | 195132 | 810 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 195877 | 195899 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 27399 | 27399 | 18884 | 81 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1531 | 1531 | 1483 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 47 | 47 | 47 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 59110 | 59110 | 54197 | 84 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 7 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 71624 | 71624 | 70444 | 4 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 350 | 350 | 350 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4721 | 4721 | 3419 | 13 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 62272 | 62272 | 39478 | 116 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2605 | 2605 | 2559 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 3708 | 3708 | 3009 | 4 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=195585): breakout_not_found=109970, basic_filters_failed=52684, retest_proximity_failed=23767, ema_alignment_reject=5001, volume_spike_missing=3902, missing_fvg_or_orderblock=261
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=189631): cls_disabled_merged_into_lsr=189631
- **EVAL::DIVERGENCE_CONTINUATION** (total=181956): cvd_divergence_failed=60058, h1_trend_not_aligned=48249, basic_filters_failed=47974, ema_alignment_reject=16517, retest_proximity_failed=6290, cvd_insufficient=1322, regime_blocked=780, missing_fvg_or_orderblock=599, missing_cvd=167
- **EVAL::FAILED_AUCTION_RECLAIM** (total=183578): auction_not_detected=73562, basic_filters_failed=46351, reclaim_hold_failed=33155, tail_too_small=25029, regime_blocked=5472, rsi_reject=9
- **EVAL::FUNDING_EXTREME** (total=201361): funding_not_extreme=139362, basic_filters_failed=47907, missing_funding_rate=10225, ema_alignment_reject=2445, rsi_reject=942, momentum_reject=274, cvd_divergence_failed=192, missing_fvg_or_orderblock=14
- **EVAL::LIQUIDATION_REVERSAL** (total=195862): cascade_threshold_not_met=140193, basic_filters_failed=52678, cvd_divergence_failed=1602, rsi_reject=1303, missing_fvg_or_orderblock=59, cvd_insufficient=18, volume_spike_missing=9
- **EVAL::MA_CROSS_TREND_SHIFT** (total=190062): no_ma_cross=140156, basic_filters_failed=47987, ma_cross_cooldown=1246, ma_cross_htf_misaligned=673
- **EVAL::MOVER_TREND_PULLBACK** (total=178991): mover_run_too_small=80979, basic_filters_failed=52647, no_reclaim=34238, no_pullback_tag=9654, no_ma_stack=1004, insufficient_candles=469
- **EVAL::OPENING_RANGE_BREAKOUT** (total=197101): feature_disabled=197101
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=189661): regime_blocked=126595, breakout_not_found=38672, basic_filters_failed=16272, adx_reject=8105, ema_alignment_reject=17
- **EVAL::QUIET_COMPRESSION_BREAK** (total=188260): compression_not_detected=80031, regime_blocked=68326, basic_filters_failed=30070, breakout_not_detected=6154, volume_confirmation_failed=3053, macd_reject=471, rsi_reject=141, missing_fvg_or_orderblock=14
- **EVAL::SR_FLIP_RETEST** (total=173588): basic_filters_failed=46329, reclaim_hold_failed=43328, retest_out_of_zone=34138, flip_close_not_confirmed=29371, ema_alignment_reject=7388, wick_quality_failed=6546, regime_blocked=5442, missing_fvg_or_orderblock=1000, rsi_reject=46
- **EVAL::STANDARD** (total=171596): momentum_reject=64459, adx_reject=38216, sweeps_not_detected=25162, basic_filters_failed=24463, macd_reject=9852, ema_alignment_reject=6665, invalid_sl_geometry=1441, rsi_reject=1321, mtf_reject=17
- **EVAL::TREND_PULLBACK** (total=182759): h1_trend_not_aligned=61883, ema_alignment_reject=40940, basic_filters_failed=27766, h1_pullback_not_confirmed=15897, ema_not_tested_prev=14412, no_ema_reclaim_close=10581, body_conviction_fail=3854, rsi_reject=3217, regime_blocked=1648, prev_already_below_emas=815, prev_already_above_emas=584, no_prev_low_break=400, momentum_flat=345, no_prev_high_break=205, ema21_not_tagged=133, momentum_reject=51, missing_fvg_or_orderblock=28
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=195132): breakout_not_found=112063, basic_filters_failed=52680, retest_proximity_failed=23176, volume_spike_missing=5547, ema_alignment_reject=1180, missing_fvg_or_orderblock=438, rsi_reject=48
- **EVAL::WHALE_MOMENTUM** (total=195899): momentum_reject=129796, recent_ticks_insufficient=41659, basic_filters_failed=24444

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 370549 | 34.1% |
| QUIET | 314480 | 29.0% |
| TRENDING_UP | 227174 | 20.9% |
| TRENDING_DOWN | 92695 | 8.5% |
| VOLATILE | 81348 | 7.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **904**
- Average confidence gap to threshold: **13.05** (samples=904) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=159, TRXUSDT=155, ETHUSDT=140, ASTERUSDT=78, MRVLUSDT=51, LTCUSDT=45, LINKUSDT=33, NEARUSDT=32, 1000PEPEUSDT=32, ONDOUSDT=30

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 321 |
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 4 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 191 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 837 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 247 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 476 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 171 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2090 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 6 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1129 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 133 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 941 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 603 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 559 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 193 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 787 |
| SR_FLIP_RETEST | filtered | min_confidence | 4741 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 369 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2964 |
| TREND_PULLBACK_CONTINUATION | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 46 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 245 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 15 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 58 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 325 | 59.08 | 65.00 | 5.92 | 21.49 | 19.40 | 19.32 | 0.00 | 8.63 |
| BREAKDOWN_SHORT | kept | 191 | 71.14 | 65.00 | -6.14 | 20.83 | 19.40 | 18.38 | 0.00 | 2.59 |
| DIVERGENCE_CONTINUATION | filtered | 856 | 57.17 | 65.00 | 7.83 | 20.94 | 19.52 | 18.34 | 1.90 | 9.80 |
| DIVERGENCE_CONTINUATION | kept | 247 | 68.96 | 65.00 | -3.96 | 20.13 | 19.75 | 17.38 | 1.66 | -0.28 |
| FAILED_AUCTION_RECLAIM | filtered | 647 | 55.42 | 65.00 | 9.58 | 21.43 | 19.45 | 20.00 | 2.94 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 2090 | 71.99 | 65.00 | -6.99 | 20.73 | 19.35 | 20.00 | 3.49 | 0.65 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 55.20 | 65.00 | 9.80 | 20.80 | 20.00 | 17.00 | 2.00 | 9.80 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 69.56 | 65.00 | -4.56 | 19.88 | 19.98 | 17.00 | 1.60 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1262 | 54.86 | 65.00 | 10.14 | 20.44 | 19.75 | 18.34 | 1.89 | 8.49 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 941 | 69.35 | 65.00 | -4.35 | 20.77 | 19.65 | 18.36 | 1.33 | 0.98 |
| MOVER_TREND_PULLBACK | filtered | 603 | 53.20 | 65.00 | 11.80 | 19.61 | 18.19 | 15.80 | 4.36 | 22.38 |
| MOVER_TREND_PULLBACK | kept | 559 | 72.45 | 65.00 | -7.45 | 20.53 | 18.09 | 15.80 | 4.98 | 5.24 |
| QUIET_COMPRESSION_BREAK | filtered | 193 | 54.28 | 65.00 | 10.72 | 22.57 | 19.29 | 20.00 | 0.00 | 4.34 |
| QUIET_COMPRESSION_BREAK | kept | 787 | 77.90 | 65.00 | -12.90 | 20.03 | 19.45 | 20.00 | 0.00 | 1.75 |
| SR_FLIP_RETEST | filtered | 5110 | 55.40 | 65.00 | 9.60 | 21.22 | 19.89 | 15.81 | 1.57 | 6.54 |
| SR_FLIP_RETEST | kept | 2964 | 70.50 | 65.00 | -5.50 | 20.72 | 19.95 | 15.59 | 2.14 | 1.24 |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 54.00 | 65.00 | 11.00 | 24.00 | 18.60 | 16.40 | 0.00 | 0.00 |
| TREND_PULLBACK_EMA | kept | 46 | 78.72 | 65.00 | -13.72 | 19.99 | 19.96 | 19.00 | 5.51 | -2.66 |
| VOLUME_SURGE_BREAKOUT | filtered | 260 | 51.78 | 65.00 | 13.22 | 21.43 | 19.89 | 19.15 | 1.66 | 6.04 |
| VOLUME_SURGE_BREAKOUT | kept | 58 | 69.41 | 65.00 | -4.41 | 20.68 | 19.95 | 20.00 | 2.13 | 2.58 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 325 | 59.08 | 16.90 | 14.71 | 12.49 | 12.94 | 4.99 | 5.67 | 0.00 |
| BREAKDOWN_SHORT | kept | 191 | 71.14 | 21.02 | 14.52 | 12.06 | 14.24 | 5.60 | 6.28 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 856 | 57.17 | 20.15 | 11.28 | 7.95 | 14.66 | 5.43 | 8.54 | 1.90 |
| DIVERGENCE_CONTINUATION | kept | 247 | 68.96 | 20.66 | 16.18 | 4.85 | 11.40 | 6.18 | 9.21 | 1.66 |
| FAILED_AUCTION_RECLAIM | filtered | 647 | 55.42 | 21.78 | 16.33 | 4.91 | 12.56 | 6.62 | 5.76 | 2.94 |
| FAILED_AUCTION_RECLAIM | kept | 2090 | 71.99 | 23.39 | 15.62 | 4.46 | 12.95 | 6.21 | 6.54 | 3.49 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 55.20 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 8.00 | 2.00 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 69.56 | 25.00 | 10.00 | 3.00 | 14.60 | 5.70 | 9.66 | 1.60 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1262 | 54.86 | 21.31 | 15.13 | 7.40 | 13.02 | 5.13 | 6.24 | 1.89 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 941 | 69.35 | 22.81 | 14.20 | 6.02 | 14.01 | 5.58 | 6.40 | 1.33 |
| MOVER_TREND_PULLBACK | filtered | 603 | 53.20 | 18.40 | 18.18 | 7.95 | 12.84 | 5.35 | 8.70 | 4.36 |
| MOVER_TREND_PULLBACK | kept | 559 | 72.45 | 18.31 | 18.00 | 8.03 | 13.66 | 5.53 | 9.18 | 4.98 |
| QUIET_COMPRESSION_BREAK | filtered | 193 | 54.28 | 18.08 | 18.00 | 6.75 | 16.77 | 5.70 | 5.64 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 787 | 77.90 | 20.15 | 18.00 | 10.68 | 16.62 | 6.54 | 8.44 | 0.00 |
| SR_FLIP_RETEST | filtered | 5110 | 55.40 | 19.34 | 17.28 | 4.94 | 13.02 | 6.18 | 7.49 | 1.57 |
| SR_FLIP_RETEST | kept | 2964 | 70.50 | 22.34 | 15.16 | 5.01 | 13.93 | 5.87 | 8.19 | 2.14 |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 54.00 | 17.00 | 8.00 | 15.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| TREND_PULLBACK_EMA | kept | 46 | 78.72 | 18.74 | 18.00 | 7.50 | 14.00 | 5.25 | 9.86 | 5.51 |
| VOLUME_SURGE_BREAKOUT | filtered | 260 | 51.78 | 18.91 | 16.82 | 12.78 | 11.85 | 5.30 | 4.11 | 1.66 |
| VOLUME_SURGE_BREAKOUT | kept | 58 | 69.41 | 22.24 | 17.93 | 13.86 | 14.00 | 5.10 | 6.55 | 2.13 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 325 | 59.08 | 0.00 | 0.00 | 3.11 | 0.00 | 1.22 | 0.00 | 0.00 | 2.01 | **6.34** |
| BREAKDOWN_SHORT | kept | 191 | 71.14 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.29** |
| DIVERGENCE_CONTINUATION | filtered | 856 | 57.17 | 0.00 | 0.00 | 0.17 | 0.00 | 3.93 | 0.00 | 0.00 | 0.00 | **4.10** |
| DIVERGENCE_CONTINUATION | kept | 247 | 68.96 | 0.00 | 0.00 | 0.04 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.15** |
| FAILED_AUCTION_RECLAIM | filtered | 647 | 55.42 | 0.00 | 0.00 | 0.33 | 0.00 | 2.54 | 0.00 | 0.00 | 0.00 | **2.87** |
| FAILED_AUCTION_RECLAIM | kept | 2090 | 71.99 | 0.00 | 0.00 | 0.02 | 0.00 | 0.35 | 0.00 | 0.00 | 0.00 | **0.37** |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 55.20 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 69.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1262 | 54.86 | 0.00 | 0.00 | 1.62 | 0.00 | 4.48 | 0.00 | 0.00 | 0.00 | **6.10** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 941 | 69.35 | 0.00 | 0.00 | 0.07 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | **0.55** |
| MOVER_TREND_PULLBACK | filtered | 603 | 53.20 | 0.00 | 0.00 | 8.32 | 0.00 | 0.58 | 0.00 | 0.00 | 0.05 | **8.95** |
| MOVER_TREND_PULLBACK | kept | 559 | 72.45 | 0.00 | 0.00 | 4.72 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | **5.09** |
| QUIET_COMPRESSION_BREAK | filtered | 193 | 54.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.47 | 0.00 | 0.00 | 2.91 | **3.38** |
| QUIET_COMPRESSION_BREAK | kept | 787 | 77.90 | 0.00 | 0.00 | 0.00 | 0.00 | 2.90 | 0.00 | 0.00 | 1.26 | **4.16** |
| SR_FLIP_RETEST | filtered | 5110 | 55.40 | 0.00 | 0.00 | 0.49 | 0.00 | 1.15 | 0.01 | 0.00 | 0.48 | **2.13** |
| SR_FLIP_RETEST | kept | 2964 | 70.50 | 0.00 | 0.00 | 0.25 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | **0.48** |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 54.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 46 | 78.72 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.21** |
| VOLUME_SURGE_BREAKOUT | filtered | 260 | 51.78 | 0.00 | 0.00 | 1.11 | 0.00 | 1.11 | 0.00 | 0.00 | 1.36 | **3.58** |
| VOLUME_SURGE_BREAKOUT | kept | 58 | 69.41 | 0.00 | 0.00 | 1.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.49** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=141 (71.9%) | PREMATURE=29 (14.8%) | NEUTRAL=26 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 112 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 39 | 7 | 0 | 0 |
| ema_crossover | 4 | 1 | 2 | 0 |
| momentum_loss | 88 | 14 | 17 | 0 |
| trailing_invalidation | 10 | 7 | 7 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 7 | 2 | 8 | 0 |
| DIVERGENCE_CONTINUATION | 20 | 8 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 27 | 3 | 3 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 30 | 4 | 6 | 0 |
| SR_FLIP_RETEST | 50 | 12 | 7 | 0 |
| TREND_PULLBACK_EMA | 3 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 4 | 0 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 39 | 7 | 0 | 14.6 | 14.7 | -0.00 | **TUNE** — marginal: avg -0.00R/kill across 46 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 4 | 1 | 2 | 2.8 | 2.0 | +0.11 | **INSUFFICIENT_SAMPLE** — only 7 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 88 | 14 | 17 | 56.5 | 23.5 | +0.28 | **KEEP** — net-helping: avg +0.28R/kill across 119 kills (saved 56.5R vs missed 23.5R) |
| trailing_invalidation | 10 | 7 | 7 | 10.1 | 10.1 | -0.00 | **TUNE** — marginal: avg -0.00R/kill across 24 kills — consider per-setup exemption or threshold adjustment, not full drop |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4871910`
- `Path funnel` emissions: `154`
- `Regime distribution` emissions: `154`
- `QUIET_SCALP_BLOCK` events: `904`
- `confidence_gate` events: `17151`
- `free_channel_post` events: `105`
- `pre_tp_fire` events: `49`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **49**
- Avg resolved threshold: **0.577%** raw → avg net **+5.07%** @ 10x
- Avg time-to-fire from dispatch: **278s**
- By threshold source: stamped=49

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 22 | 0.395% | +3.25% | 229 | stamped=22 |
| LIQUIDITY_SWEEP_REVERSAL | 13 | 0.675% | +6.05% | 232 | stamped=13 |
| FAILED_AUCTION_RECLAIM | 6 | 0.405% | +3.35% | 396 | stamped=6 |
| DIVERGENCE_CONTINUATION | 3 | 0.513% | +4.43% | 142 | stamped=3 |
| TREND_PULLBACK_EMA | 2 | 1.206% | +11.37% | 442 | stamped=2 |
| MOVER_TREND_PULLBACK | 2 | 1.597% | +15.27% | 651 | stamped=2 |
| FUNDING_EXTREME_SIGNAL | 1 | 1.261% | +11.91% | 596 | stamped=1 |
- Top symbols: HOMEUSDT=6, BASEDUSDT=5, CLOUSDT=5, BELUSDT=4, ORDIUSDT=4, METUSDT=3, APTUSDT=3, AGTUSDT=2, SYNUSDT=2, HUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **105**

| Source | Count |
|---|---:|
| signal_close | 53 |
| pre_tp | 49 |
| regime_shift | 3 |

- By severity: HIGH=105

## Dependency readiness
- cvd: presence[absent=5907, present=877020] state[empty=5907, populated=877020] buckets[few=149, many=870401, none=5907, some=6470] sources[none] quality[none]
- funding_rate: presence[absent=21766, present=861161] state[empty=21766, populated=861161] buckets[few=861161, none=21766] sources[none] quality[none]
- liquidation_clusters: presence[absent=485788, present=397139] state[empty=485788, populated=397139] buckets[few=316086, none=485788, some=81053] sources[none] quality[none]
- oi_snapshot: presence[absent=19122, present=863805] state[empty=19122, populated=863805] buckets[many=863805, none=19122] sources[none] quality[none]
- order_book: presence[absent=226847, present=656080] state[populated=656080, unavailable=226847] buckets[few=656080, none=226847] sources[book_ticker=656080, unavailable=226847] quality[none=226847, top_of_book_only=656080]
- orderblocks: presence[absent=882927] state[empty=882927] buckets[none=882927] sources[not_implemented=882927] quality[none]
- recent_ticks: presence[absent=5191, present=877736] state[empty=5191, populated=877736] buckets[many=877736, none=5191] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.523131489753723` sec
- Median create→first breach: `404.3333568572998` sec
- Median create→terminal: `350.59652602672577` sec
- Median first breach→terminal: `1.0951979160308838` sec
- Fast-failure buckets: `{"under_120s": {"count": 16, "pct": 30.2}, "under_180s": {"count": 17, "pct": 32.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 11, "pct": 20.8}}`
- ~3 minute terminal-close behavior: `{"count": 6, "pct": 6.8}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0374 | None | 179.4174768924713 |
| DIVERGENCE_CONTINUATION | 12 | 12 | 0.0 | 16.7 | 0.0 | 25.0 | 0.0477 | 449.37098693847656 | 292.66267108917236 |
| FAILED_AUCTION_RECLAIM | 16 | 16 | 0.0 | 6.2 | 0.0 | 37.5 | -0.0452 | 716.674281835556 | 719.1988849639893 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 100.0 | 1.6057 | 654.6598389148712 | 663.398768901825 |
| LIQUIDITY_SWEEP_REVERSAL | 16 | 16 | 0.0 | 6.2 | 0.0 | 81.2 | -0.0426 | 235.43707942962646 | 345.7936325073242 |
| MOVER_TREND_PULLBACK | 3 | 3 | 0.0 | 33.3 | 0.0 | 66.7 | 0.0553 | 909.3740990161896 | 940.5434855222702 |
| SR_FLIP_RETEST | 38 | 38 | 0.0 | 7.9 | 0.0 | 57.9 | -0.0285 | 404.3333568572998 | 350.59652602672577 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 100.0 | 0.0871 | 1370.2900149822235 | 1006.9548870325089 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 62272 | 116 | 39478 | 0.0 | 7.9 | 404.3333568572998 | 350.59652602672577 | 22794 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2605 | 5 | 2559 | 0.0 | 0.0 | 1370.2900149822235 | 1006.9548870325089 | 46 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-94`
- Gating Δ: `-8483`
- No-generation Δ: `2034`
- Fast failures Δ: `7`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.5226, "current_avg_pnl": -0.0374, "current_win_rate": 0.0, "previous_avg_pnl": 0.4852, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1391, "current_avg_pnl": 0.0477, "current_win_rate": 0.0, "previous_avg_pnl": -0.0914, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1651, "current_avg_pnl": -0.0452, "current_win_rate": 0.0, "previous_avg_pnl": 0.1199, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.049, "current_avg_pnl": -0.0426, "current_win_rate": 0.0, "previous_avg_pnl": -0.0916, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.0553, "current_avg_pnl": 0.0553, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0948, "current_avg_pnl": -0.0285, "current_win_rate": 0.0, "previous_avg_pnl": 0.0663, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -49, "geometry_changed_delta": 0, "geometry_preserved_delta": -7763, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -149.77, "median_terminal_delta_sec": -124.59, "sl_rate_delta": 3.4, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -95, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1370.29, "median_terminal_delta_sec": 1006.95, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **POST_DISPLACEMENT_CONTINUATION**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
