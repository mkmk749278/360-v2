# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `1662` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 57 | 57 | 11 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9714 | 9714 | 8397 | 19 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 46117 | 46115 | 11 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 39228 | 39234 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 38947 | 36465 | 2754 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 39252 | 37561 | 1850 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 40971 | 40911 | 71 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 36061 | 36067 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 39422 | 39439 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 39449 | 36533 | 5147 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 48034 | 50522 | 42 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 46125 | 41822 | 6192 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 39620 | 39624 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 39238 | 39245 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 38907 | 38656 | 289 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 37550 | 36726 | 2160 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 34449 | 32977 | 1623 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 34601 | 34390 | 232 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 46105 | 46114 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 36070 | 36082 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7193 | 7193 | 6032 | 18 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 214 | 214 | 172 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 32 | 32 | 32 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8428 | 8428 | 8169 | 12 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 9 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 15410 | 15410 | 15410 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 95 | 95 | 94 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 15257 | 15257 | 13420 | 13 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 20 | 20 | 20 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1015 | 1015 | 744 | 16 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 7794 | 7794 | 951 | 64 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 896 | 896 | 838 | 3 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 9 | 9 | 9 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=46115): breakout_not_found=21156, basic_filters_failed=14560, move_not_fresh=7812, breakout_stale=2047, retest_proximity_failed=449, volume_spike_missing=77, move_exhausted=13, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=39234): cls_disabled_merged_into_lsr=39234
- **EVAL::DIVERGENCE_CONTINUATION** (total=36465): cvd_divergence_failed=14776, basic_filters_failed=10947, h1_trend_not_aligned=6048, ema_alignment_reject=4093, retest_proximity_failed=415, missing_fvg_or_orderblock=186
- **EVAL::FAILED_AUCTION_RECLAIM** (total=37561): auction_not_detected=14037, basic_filters_failed=10566, reclaim_hold_failed=6851, tail_too_small=4832, regime_blocked=1273, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=40911): funding_not_extreme=27897, basic_filters_failed=10911, ema_alignment_reject=882, missing_funding_rate=785, rsi_reject=305, cvd_divergence_failed=65, momentum_reject=63, missing_fvg_or_orderblock=3
- **EVAL::LIQUIDATION_REVERSAL** (total=36067): cascade_threshold_not_met=24865, basic_filters_failed=10924, cvd_divergence_failed=171, rsi_reject=104, missing_fvg_or_orderblock=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=39439): no_ma_cross=27425, basic_filters_failed=10956, ma_cross_cooldown=697, ma_cross_htf_misaligned=361
- **EVAL::MEAN_REVERT** (total=36533): no_extension=28712, basic_filters_failed=7821
- **EVAL::MOVER_AVWAP_SCALP** (total=50522): no_avwap_tag=18859, basic_filters_failed=14658, no_mover_leg=12841, no_avwap_reclaim=1948, avwap_reclaim_no_volume=1104, avwap_slope_against=1069, anchor_too_recent=43
- **EVAL::MOVER_TREND_PULLBACK** (total=41822): mover_run_too_small=18734, basic_filters_failed=14581, no_reclaim=5559, no_pullback_tag=2651, insufficient_candles=297
- **EVAL::OPENING_RANGE_BREAKOUT** (total=39624): feature_disabled=39624
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=39245): regime_blocked=22487, breakout_not_found=10553, basic_filters_failed=4530, adx_reject=1649, ema_alignment_reject=26
- **EVAL::QUIET_COMPRESSION_BREAK** (total=38656): regime_blocked=17928, compression_not_detected=9884, basic_filters_failed=6035, breakout_not_detected=4240, volume_confirmation_failed=496, rsi_reject=63, missing_fvg_or_orderblock=10
- **EVAL::SR_FLIP_RETEST** (total=36726): basic_filters_failed=10556, flip_close_not_confirmed=6231, whipsaw_flip=4249, reclaim_hold_failed=4173, long_break_volume_thin=4172, retest_out_of_zone=2715, long_disabled=2208, regime_blocked=1269, wick_quality_failed=740, long_acceptance_not_held=180, missing_fvg_or_orderblock=145, ema_alignment_reject=77, rsi_reject=11
- **EVAL::STANDARD** (total=32977): momentum_reject=10816, adx_reject=7820, basic_filters_failed=6526, sweeps_not_detected=2694, macd_reject=2370, ema_alignment_reject=2220, invalid_sl_geometry=296, rsi_reject=228, mtf_reject=7
- **EVAL::TREND_PULLBACK** (total=34390): h1_pullback_not_confirmed=7861, h1_trend_not_aligned=7619, basic_filters_failed=5817, ema_alignment_reject=4844, no_ema_reclaim_close=2357, ema_not_tested_prev=2149, rsi_reject=1409, body_conviction_fail=1375, prev_already_below_emas=378, no_prev_low_break=238, momentum_flat=112, no_prev_high_break=104, prev_already_above_emas=94, ema21_not_tagged=15, missing_fvg_or_orderblock=11, momentum_reject=7
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=46114): breakout_not_found=26914, basic_filters_failed=14559, move_not_fresh=2407, breakout_stale=1773, retest_proximity_failed=330, volume_spike_missing=113, missing_fvg_or_orderblock=12, ema_alignment_reject=6
- **EVAL::WHALE_MOMENTUM** (total=36082): momentum_reject=23897, recent_ticks_insufficient=8417, basic_filters_failed=3768

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 65137 | 30.3% |
| TRENDING_DOWN | 61330 | 28.5% |
| QUIET | 49495 | 23.0% |
| TRENDING_UP | 29722 | 13.8% |
| VOLATILE | 9507 | 4.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **206**
- Average confidence gap to threshold: **14.34** (samples=206) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SPYUSDT=40, ETHUSDT=18, BTCUSDT=17, ORCLUSDT=17, TRXUSDT=16, CBRSUSDT=16, SUIUSDT=11, XRPUSDT=11, BNBUSDT=9, ENAUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 36 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 10 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 208 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 216 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 50 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 26 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 254 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 84 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 49 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 330 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 19 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1028 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 34 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 34 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 176 |
| SR_FLIP_RETEST | filtered | min_confidence | 1020 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 122 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1922 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 23 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 15 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 36 | 63.50 | 65.00 | 1.50 | 19.35 | 18.00 | 20.00 | 4.50 | 3.00 |
| BREAKDOWN_SHORT | kept | 10 | 67.98 | 65.00 | -2.98 | 20.93 | 17.90 | 20.00 | 4.20 | 7.00 |
| DIVERGENCE_CONTINUATION | filtered | 213 | 56.85 | 65.00 | 8.15 | 21.16 | 19.80 | 17.81 | 1.95 | 10.64 |
| DIVERGENCE_CONTINUATION | kept | 216 | 70.14 | 65.00 | -5.14 | 20.99 | 19.85 | 18.59 | 1.19 | 0.71 |
| FAILED_AUCTION_RECLAIM | filtered | 76 | 56.24 | 65.00 | 8.76 | 21.60 | 18.92 | 20.00 | 2.86 | 6.98 |
| FAILED_AUCTION_RECLAIM | kept | 254 | 70.82 | 65.00 | -5.82 | 20.94 | 19.66 | 20.00 | 4.20 | 0.56 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 37.00 | 65.00 | 28.00 | 19.80 | 19.80 | 20.00 | 0.00 | 13.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 84 | 62.00 | 65.00 | 3.00 | 20.73 | 19.49 | 18.27 | 2.67 | 7.90 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 49 | 69.06 | 65.00 | -4.06 | 21.49 | 19.83 | 17.75 | 2.71 | 0.52 |
| MOVER_AVWAP_SCALP | kept | 1 | 83.50 | 65.00 | -18.50 | 20.40 | 16.10 | 15.80 | 4.50 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 349 | 56.61 | 65.00 | 8.39 | 18.00 | 17.57 | 15.80 | 4.17 | 20.03 |
| MOVER_TREND_PULLBACK | kept | 1028 | 77.89 | 65.00 | -12.89 | 20.01 | 17.64 | 15.80 | 4.68 | -0.01 |
| QUIET_COMPRESSION_BREAK | filtered | 68 | 51.89 | 65.00 | 13.11 | 21.21 | 19.40 | 20.00 | 0.00 | 3.21 |
| QUIET_COMPRESSION_BREAK | kept | 176 | 74.61 | 65.00 | -9.61 | 20.29 | 19.63 | 20.00 | 0.00 | 3.16 |
| SR_FLIP_RETEST | filtered | 1142 | 58.51 | 65.00 | 6.49 | 20.60 | 19.84 | 15.69 | 1.46 | 11.12 |
| SR_FLIP_RETEST | kept | 1922 | 71.00 | 65.00 | -6.00 | 20.94 | 19.92 | 15.82 | 1.82 | 0.54 |
| TREND_PULLBACK_EMA | filtered | 23 | 59.30 | 65.00 | 5.70 | 19.83 | 19.50 | 20.00 | 6.00 | 17.20 |
| TREND_PULLBACK_EMA | kept | 15 | 81.88 | 65.00 | -16.88 | 21.03 | 19.99 | 16.94 | 5.40 | -0.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 36 | 63.50 | 2.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.00 | 4.50 |
| BREAKDOWN_SHORT | kept | 10 | 67.98 | 17.80 | 14.40 | 12.30 | 11.60 | 4.75 | 9.93 | 4.20 |
| DIVERGENCE_CONTINUATION | filtered | 213 | 56.85 | 19.78 | 16.45 | 3.89 | 12.55 | 4.85 | 8.49 | 1.95 |
| DIVERGENCE_CONTINUATION | kept | 216 | 70.14 | 20.70 | 16.01 | 5.79 | 13.12 | 6.12 | 8.39 | 1.19 |
| FAILED_AUCTION_RECLAIM | filtered | 76 | 56.24 | 20.34 | 16.63 | 4.82 | 13.55 | 5.69 | 6.44 | 2.86 |
| FAILED_AUCTION_RECLAIM | kept | 254 | 70.82 | 22.87 | 14.88 | 4.78 | 10.19 | 6.58 | 8.33 | 4.20 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 37.00 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 84 | 62.00 | 24.52 | 14.00 | 3.43 | 10.80 | 5.89 | 8.65 | 2.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 49 | 69.06 | 23.98 | 14.49 | 4.59 | 11.49 | 5.33 | 6.99 | 2.71 |
| MOVER_AVWAP_SCALP | kept | 1 | 83.50 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.50 |
| MOVER_TREND_PULLBACK | filtered | 349 | 56.61 | 19.18 | 18.00 | 8.03 | 12.65 | 6.03 | 8.57 | 4.17 |
| MOVER_TREND_PULLBACK | kept | 1028 | 77.89 | 19.76 | 18.00 | 8.43 | 12.54 | 5.77 | 9.31 | 4.68 |
| QUIET_COMPRESSION_BREAK | filtered | 68 | 51.89 | 17.59 | 16.00 | 11.78 | 14.49 | 7.15 | 3.06 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 176 | 74.61 | 18.41 | 17.14 | 12.41 | 14.00 | 8.15 | 8.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 1142 | 58.51 | 18.37 | 16.93 | 5.58 | 12.35 | 6.50 | 8.43 | 1.46 |
| SR_FLIP_RETEST | kept | 1922 | 71.00 | 20.16 | 16.70 | 5.48 | 13.34 | 6.27 | 8.83 | 1.82 |
| TREND_PULLBACK_EMA | filtered | 23 | 59.30 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 6.00 |
| TREND_PULLBACK_EMA | kept | 15 | 81.88 | 19.73 | 18.00 | 7.50 | 14.00 | 8.27 | 8.98 | 5.40 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 36 | 63.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 10 | 67.98 | 0.00 | 0.00 | 6.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.40** |
| DIVERGENCE_CONTINUATION | filtered | 213 | 56.85 | 0.00 | 0.00 | 1.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.10** |
| DIVERGENCE_CONTINUATION | kept | 216 | 70.14 | 0.00 | 0.00 | 0.58 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | **1.01** |
| FAILED_AUCTION_RECLAIM | filtered | 76 | 56.24 | 0.00 | 0.00 | 3.92 | 0.00 | 2.21 | 0.00 | 0.00 | 0.00 | **6.13** |
| FAILED_AUCTION_RECLAIM | kept | 254 | 70.82 | 0.00 | 0.00 | 0.77 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 37.00 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 84 | 62.00 | 0.00 | 0.00 | 3.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.43** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 49 | 69.06 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.39** |
| MOVER_AVWAP_SCALP | kept | 1 | 83.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 349 | 56.61 | 0.00 | 0.00 | 0.00 | 0.00 | 1.22 | 0.00 | 0.00 | 0.06 | **1.28** |
| MOVER_TREND_PULLBACK | kept | 1028 | 77.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | **0.36** |
| QUIET_COMPRESSION_BREAK | filtered | 68 | 51.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.65 | **3.65** |
| QUIET_COMPRESSION_BREAK | kept | 176 | 74.61 | 0.00 | 0.00 | 3.44 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **3.54** |
| SR_FLIP_RETEST | filtered | 1142 | 58.51 | 0.21 | 0.00 | 1.26 | 0.00 | 0.99 | 0.00 | 0.00 | 0.14 | **2.60** |
| SR_FLIP_RETEST | kept | 1922 | 71.00 | 0.00 | 0.00 | 0.02 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.10** |
| TREND_PULLBACK_EMA | filtered | 23 | 59.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 15 | 81.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=850 (19.7%) | WOULD_LOSE=1194 | WOULD_EXPIRE=2272 | pending (awaiting window)=684

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| dispatch_cooldown | 44 | 0.0% | 8.0 | 0.0 | +0.18 | **KEEP** |
| dispatch_staleness | 414 | 3.4% | 29.0 | 7.2 | +0.05 | **TUNE** |
| level_still_in_play | 1190 | 22.1% | 70.0 | 146.7 | -0.06 | **TUNE** |
| min_confidence | 2085 | 25.1% | 775.0 | 710.2 | +0.03 | **TUNE** |
| quiet_scalp_block | 270 | 3.3% | 56.0 | 12.6 | +0.16 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 4 | 0.0% | 2.0 | 0.0 | +0.50 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 21 | 9.5% | 19.0 | 1.5 | +0.83 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 156 | 14.1% | 130.0 | 31.5 | +0.63 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 132 | 12.1% | 105.0 | 30.0 | +0.57 | **KEEP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 18704 across 19 strategies; 412 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 5196 | 9/5187/0 | 47% | -0.06 | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (+1.25R) | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (-1.00R) |
| SR_FLIP_RETEST | 3715 | 0/3715/0 | 47% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.29R) | LONDON/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 2770 | 7/2763/0 | 45% | +0.01 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 1879 | 2/1877/0 | 40% | -0.02 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.22R) | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_MEAN_REVERT | 1337 | 0/0/1337 | 41% | +0.10 | NY/MARKUP/NORMAL/BTC_NEUTRAL (+0.46R) | NY/RANGE/EXPANDED/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 991 | 0/0/991 | 41% | +0.32 | ASIA/QUIET/NORMAL/BTC_NEUTRAL (+1.29R) | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (-0.81R) |
| QUIET_COMPRESSION_BREAK | 721 | 0/721/0 | 43% | -0.04 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | NY/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 625 | 0/0/625 | 36% | -0.37 | NY/MARKUP/NORMAL/BTC_NEUTRAL (+0.13R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-0.95R) |
| LIQUIDITY_SWEEP_REVERSAL | 517 | 0/517/0 | 32% | -0.32 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.06R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 280 | 0/280/0 | 32% | -0.25 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.21R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 164 | 5/159/0 | 19% | -0.62 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 153 | 1/152/0 | 36% | -0.39 | NY/MARKUP/EXPANDED/BTC_NEUTRAL (+0.33R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 106 | 0/0/106 | 37% | -0.25 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| FUNDING_EXTREME_SIGNAL | 105 | 0/105/0 | 45% | +0.23 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 70 | 0/70/0 | 20% | -0.14 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.44R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.44R) |
| BREAKDOWN_SHORT | 59 | 1/58/0 | 63% | +0.25 | ASIA/MARKDOWN/NORMAL/BTC_FALLING (+0.53R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MEAN_REVERT | 7 | 0/7/0 | 71% | +0.07 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.70R (n=45, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL` +1.65R (n=50, STRONG)
- **Weakest cells**: `QUIET_COMPRESSION_BREAK @ OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL` -1.00R (n=23, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.00R (n=16, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.00R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_TREND_PULLBACK | 278 | 56% / +0.02R | 278 | 59% / +0.07R | +0.06 | **ATR** |
| FAILED_AUCTION_RECLAIM | 341 | 49% / -0.02R | 341 | 49% / +0.04R | +0.05 | **ATR** |
| SR_FLIP_RETEST | 409 | 48% / -0.05R | 409 | 50% / -0.00R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 41 | 49% / -0.05R | 41 | 51% / -0.02R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 82 | 43% / -0.16R | 82 | 46% / -0.15R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 181 | 48% / +0.06R | 181 | 47% / +0.06R | -0.00 | **FIXED** |
| WHALE_MOMENTUM | 8 | 25% / -0.04R | 8 | 25% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 14 | 50% / -0.02R | 14 | 57% / +0.04R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 9 | 44% / -0.04R | 9 | 44% / +0.04R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 8 | 75% / +0.13R | 8 | 75% / +0.21R | — | **MEASURING** |
| BREAKDOWN_SHORT | 3 | 33% / +0.01R | 3 | 33% / +0.02R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 1 | 0% / -1.00R | 1 | 100% / +0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |
| MEAN_REVERT | 3 | 67% / +0.05R | 3 | 67% / +0.05R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 10 · alerting: **2** · boot grace active: False
- **ALERT** `mean_revert_emission` — 21492 detections since last emission (emitted_total=0) — check gate rejections (streak 119/6) (sustained 119 cycles)
- **ALERT** `tuned_variants` — 43 unexplained non-stamps (seen=44 stamped=1 skipped=0) (streak 119/6) (sustained 119 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| btc_reference | ok | BTC ref 63597.80 | 0 |
| candle_coverage | ok | 100/110 symbols with ≥20 15m candles | 0 |
| geometry_ab | ok | output +2 / upstream +63 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 21492 detections since last emission (emitted_total=0) — check gate rejections (streak 119/6) | 119 |
| mean_revert_path | ok | output +191 / upstream +63 | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| strategy_edge | ok | output +139 / upstream +63 | 0 |
| suppression_audit | ok | output +63 / upstream +38 | 0 |
| tuned_variants | violating | 43 unexplained non-stamps (seen=44 stamped=1 skipped=0) (streak 119/6) | 119 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `68445`
- `Path funnel` emissions: `25`
- `Regime distribution` emissions: `25`
- `QUIET_SCALP_BLOCK` events: `206`
- `confidence_gate` events: `5664`
- `free_channel_post` events: `5`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 6 | 5577 | 9352 | 11971 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **5**

| Source | Count |
|---|---:|
| signal_close | 5 |

- By severity: HIGH=5

## Dependency readiness
- cvd: presence[present=170122] state[populated=170122] buckets[many=170122] sources[none] quality[none]
- funding_rate: presence[absent=24458, present=145664] state[empty=24458, populated=145664] buckets[few=145664, none=24458] sources[none] quality[none]
- liquidation_clusters: presence[absent=99293, present=70829] state[empty=99293, populated=70829] buckets[few=62293, none=99293, some=8536] sources[none] quality[none]
- oi_snapshot: presence[absent=24458, present=145664] state[empty=24458, populated=145664] buckets[many=145664, none=24458] sources[none] quality[none]
- order_book: presence[absent=51446, present=118676] state[populated=118676, unavailable=51446] buckets[few=118676, none=51446] sources[book_ticker=118676, unavailable=51446] quality[none=51446, top_of_book_only=118676]
- orderblocks: presence[absent=170122] state[empty=170122] buckets[none=170122] sources[not_implemented=170122] quality[none]
- recent_ticks: presence[absent=1485, present=168637] state[empty=1485, populated=168637] buckets[many=168637, none=1485] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.8008220195770264` sec
- Median create→first breach: `5091.730411052704` sec
- Median create→terminal: `5147.871096134186` sec
- Median first breach→terminal: `3.3184971809387207` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | 0.612 | 6692.3450610637665 | 6693.615087032318 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 12.7132 | 6505.658519029617 | 6507.616126060486 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 1.8699 | 5091.730411052704 | 5147.871096134186 |
| MOVER_TREND_PULLBACK | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -4.1448 | 2979.3077179193497 | 2981.7740520238876 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 7794 | 64 | 951 | 0.0 | 0.0 | None | None | 6843 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 896 | 3 | 838 | 0.0 | 0.0 | None | None | 58 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `149`
- Gating Δ: `54308`
- No-generation Δ: `708483`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.3289, "current_avg_pnl": 0.612, "current_win_rate": 33.3, "previous_avg_pnl": 0.9409, "previous_win_rate": 33.3, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -7.5481, "current_avg_pnl": -4.1448, "current_win_rate": 0.0, "previous_avg_pnl": 3.4033, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 64, "geometry_changed_delta": 0, "geometry_preserved_delta": 6843, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 58, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
