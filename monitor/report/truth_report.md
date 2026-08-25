# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `5783` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 37 | 37 | 37 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3898 | 3898 | 3733 | 4 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 37462 | 37469 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 34417 | 34424 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 34275 | 33283 | 1125 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 34439 | 33930 | 534 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 34236 | 34177 | 82 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 28930 | 28942 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 34471 | 34487 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 34497 | 33633 | 1325 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 39834 | 42887 | 372 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 37473 | 33456 | 6349 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 34048 | 34050 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 34428 | 34435 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 34263 | 34249 | 23 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 34960 | 34397 | 760 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 34051 | 34108 | 127 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 28669 | 26334 | 2542 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 28888 | 28706 | 222 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 37431 | 37445 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 28945 | 28919 | 41 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1780 | 1780 | 1364 | 5 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 377 | 377 | 77 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 10543 | 10543 | 10531 | 1 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 6 | 6 | 2 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 3375 | 3375 | 2814 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1000 | 1000 | 781 | 11 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 15254 | 15254 | 10451 | 115 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 169 | 169 | 75 | 7 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1811 | 1811 | 1560 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 623 | 623 | 623 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 761 | 761 | 600 | 8 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 78 | 78 | 7 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1838 | 1838 | 17 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=37469): breakout_not_found=23794, basic_filters_failed=8650, move_not_fresh=2691, breakout_stale=1543, retest_proximity_failed=646, volume_spike_missing=143, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=34424): cls_disabled_merged_into_lsr=34424
- **EVAL::DIVERGENCE_CONTINUATION** (total=33283): cvd_divergence_failed=12999, h1_trend_not_aligned=10630, basic_filters_failed=6915, ema_alignment_reject=2383, retest_proximity_failed=279, missing_fvg_or_orderblock=77
- **EVAL::FAILED_AUCTION_RECLAIM** (total=33930): auction_not_detected=23288, basic_filters_failed=6882, reclaim_hold_failed=1753, tail_too_small=1508, regime_blocked=498, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=34177): funding_not_extreme=26090, basic_filters_failed=6842, ema_alignment_reject=484, missing_funding_rate=357, rsi_reject=243, momentum_reject=79, cvd_divergence_failed=71, missing_fvg_or_orderblock=11
- **EVAL::LIQUIDATION_REVERSAL** (total=28942): cascade_threshold_not_met=21990, basic_filters_failed=6796, cvd_divergence_failed=92, rsi_reject=64
- **EVAL::MA_CROSS_TREND_SHIFT** (total=34487): no_ma_cross=26426, basic_filters_failed=6928, ma_cross_htf_misaligned=828, ma_cross_cooldown=305
- **EVAL::MEAN_REVERT** (total=33633): no_extension=28650, basic_filters_failed=4983
- **EVAL::MOVER_AVWAP_SCALP** (total=42887): no_avwap_tag=17162, no_mover_leg=10443, basic_filters_failed=8758, avwap_slope_against=5376, avwap_reclaim_no_volume=593, no_avwap_reclaim=555
- **EVAL::MOVER_TREND_PULLBACK** (total=33456): mover_run_too_small=14875, no_reclaim=8964, basic_filters_failed=8704, no_pullback_tag=913
- **EVAL::OPENING_RANGE_BREAKOUT** (total=34050): feature_disabled=34050
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=34435): regime_blocked=24729, breakout_not_found=7359, basic_filters_failed=1935, adx_reject=399, ema_alignment_reject=13
- **EVAL::QUIET_COMPRESSION_BREAK** (total=34249): compression_not_detected=17737, regime_blocked=10176, basic_filters_failed=4936, breakout_not_detected=1235, volume_confirmation_failed=156, rsi_reject=9
- **EVAL::RANGE_FADE** (total=34397): no_range_edge=29413, basic_filters_failed=4984
- **EVAL::SR_FLIP_RETEST** (total=34108): flip_close_not_confirmed=23874, basic_filters_failed=6866, long_break_volume_thin=1067, h1_break_not_confirmed=753, retest_out_of_zone=628, regime_blocked=496, reclaim_hold_failed=215, long_acceptance_not_held=154, wick_quality_failed=23, missing_fvg_or_orderblock=15, ema_alignment_reject=10, whipsaw_flip=7
- **EVAL::STANDARD** (total=26334): momentum_reject=7537, adx_reject=5525, sweeps_not_detected=4813, basic_filters_failed=3676, macd_reject=2796, ema_alignment_reject=1559, htf_poi_unanchored=388, invalid_sl_geometry=27, rsi_reject=13
- **EVAL::TREND_PULLBACK** (total=28706): h1_trend_not_aligned=11478, ema_alignment_reject=5937, basic_filters_failed=2883, no_ema_reclaim_close=2131, ema_not_tested_prev=1958, h1_pullback_not_confirmed=1891, body_conviction_fail=876, rsi_reject=816, no_prev_high_break=219, prev_already_above_emas=208, prev_already_below_emas=132, no_prev_low_break=96, momentum_flat=40, ema21_not_tagged=21, missing_fvg_or_orderblock=14, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=37445): breakout_not_found=22116, basic_filters_failed=8648, move_not_fresh=5042, breakout_stale=1196, retest_proximity_failed=330, volume_spike_missing=113
- **EVAL::WHALE_MOMENTUM** (total=28919): momentum_reject=21289, recent_ticks_insufficient=4711, basic_filters_failed=2919

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=32): setup_compat:regime_VOLATILE_UNSUITABLE=32
- **FAILED_AUCTION_RECLAIM** (total=240): execution:overextended=172, setup_compat:regime_STRONG_TREND=50, context_floor=18
- **FUNDING_EXTREME_SIGNAL** (total=315): execution:trigger_not_confirmed=315
- **LIQUIDATION_REVERSAL** (total=4): execution:trigger_not_confirmed=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=2489): execution:overextended=901, execution:trigger_not_confirmed=840, setup_compat:regime_STRONG_TREND=748
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_DIRTY_RANGE=4, execution:overextended=2
- **MEAN_REVERT** (total=1056): setup_compat:regime_STRONG_TREND=499, setup_compat:regime_WEAK_TREND=373, execution:overextended=184
- **MOVER_AVWAP_SCALP** (total=656): execution:overextended=452, execution:trigger_not_confirmed=166, entry_quality=38
- **MOVER_TREND_PULLBACK** (total=6467): execution:trigger_not_confirmed=4229, execution:overextended=1622, entry_quality=616
- **RANGE_FADE** (total=829): setup_compat:regime_STRONG_TREND=490, setup_compat:regime_WEAK_TREND=273, execution:overextended=60, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **TREND_PULLBACK_EMA** (total=675): setup_compat:regime_CLEAN_RANGE=401, setup_compat:regime_DIRTY_RANGE=244, entry_quality=30
- **VOLUME_SURGE_BREAKOUT** (total=28): execution:overextended=28
- **WHALE_MOMENTUM** (total=1759): execution:trigger_not_confirmed=1759

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 108019 | 61.2% |
| QUIET | 27890 | 15.8% |
| TRENDING_DOWN | 22774 | 12.9% |
| TRENDING_UP | 14268 | 8.1% |
| VOLATILE | 3443 | 2.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **48**
- Average confidence gap to threshold: **16.14** (samples=48) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BCHUSDT=19, BTCUSDT=13, AVAXUSDT=6, WLFIUSDT=5, FILUSDT=2, DOTUSDT=2, LDOUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 25 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 12 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 114 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 73 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 31 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 93 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 384 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1925 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 35 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 26 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 112 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 42 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 13 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 25 | 61.91 | 65.00 | 3.09 | 21.18 | 19.78 | 18.69 | 4.08 | 5.12 |
| DIVERGENCE_CONTINUATION | kept | 12 | 66.85 | 65.00 | -1.85 | 20.61 | 19.27 | 16.82 | 0.50 | -0.85 |
| FAILED_AUCTION_RECLAIM | filtered | 137 | 54.18 | 64.28 | 10.10 | 21.03 | 19.05 | 20.00 | 1.71 | 4.46 |
| FAILED_AUCTION_RECLAIM | kept | 73 | 68.00 | 65.00 | -3.00 | 20.62 | 18.41 | 20.00 | 3.94 | 0.27 |
| FUNDING_EXTREME_SIGNAL | filtered | 31 | 47.88 | 63.06 | 15.18 | 21.10 | 13.12 | 16.54 | 3.74 | 3.55 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.80 | 65.00 | -1.80 | 20.80 | 14.00 | 17.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 67.30 | 65.00 | -2.30 | 20.80 | 20.00 | 17.00 | 0.00 | -3.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.70 | 61.00 | 10.30 | 19.90 | 17.40 | 15.80 | 0.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 75.25 | 65.00 | -10.25 | 20.75 | 15.80 | 15.80 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 93 | 78.25 | 65.00 | -13.25 | 20.96 | 17.19 | 15.80 | 4.52 | 2.88 |
| MOVER_TREND_PULLBACK | filtered | 385 | 58.33 | 64.72 | 6.39 | 20.82 | 18.58 | 15.80 | 4.32 | 14.79 |
| MOVER_TREND_PULLBACK | kept | 1925 | 76.02 | 65.00 | -11.02 | 20.05 | 18.57 | 15.80 | 4.03 | 1.64 |
| QUIET_COMPRESSION_BREAK | filtered | 42 | 53.70 | 64.33 | 10.63 | 20.07 | 18.11 | 20.00 | 0.00 | -0.64 |
| QUIET_COMPRESSION_BREAK | kept | 26 | 80.39 | 65.00 | -15.39 | 22.70 | 19.05 | 20.00 | 0.00 | -2.77 |
| TREND_PULLBACK_EMA | filtered | 4 | 60.60 | 65.00 | 4.40 | 18.60 | 20.00 | 20.00 | 4.50 | 18.60 |
| TREND_PULLBACK_EMA | kept | 112 | 73.88 | 65.00 | -8.88 | 21.56 | 19.85 | 17.97 | 4.95 | 1.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 46.00 | 63.00 | 17.00 | 20.32 | 18.58 | 20.00 | 3.00 | 7.43 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 72.00 | 65.00 | -7.00 | 20.60 | 16.40 | 20.00 | 4.50 | 4.50 |
| WHALE_MOMENTUM | filtered | 13 | 41.92 | 65.00 | 23.08 | 24.08 | 14.00 | 17.00 | 0.00 | 24.95 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 25 | 61.91 | 25.00 | 8.00 | 5.40 | 10.48 | 4.90 | 9.17 | 4.08 |
| DIVERGENCE_CONTINUATION | kept | 12 | 66.85 | 20.33 | 12.17 | 5.25 | 13.83 | 6.12 | 9.29 | 0.50 |
| FAILED_AUCTION_RECLAIM | filtered | 137 | 54.18 | 20.24 | 16.86 | 5.21 | 14.47 | 6.26 | 4.95 | 1.71 |
| FAILED_AUCTION_RECLAIM | kept | 73 | 68.00 | 19.41 | 17.07 | 3.74 | 11.44 | 6.34 | 6.33 | 3.94 |
| FUNDING_EXTREME_SIGNAL | filtered | 31 | 47.88 | 23.97 | 8.39 | 5.13 | 13.55 | 8.18 | 3.47 | 3.74 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.80 | 25.00 | 20.00 | 3.00 | 12.00 | 8.50 | 9.30 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 67.30 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 6.30 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.70 | 17.00 | 14.00 | 6.00 | 12.00 | 10.00 | 6.70 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 75.25 | 21.00 | 14.00 | 9.00 | 15.50 | 6.75 | 9.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 93 | 78.25 | 17.88 | 18.00 | 11.18 | 14.00 | 6.59 | 8.97 | 4.52 |
| MOVER_TREND_PULLBACK | filtered | 385 | 58.33 | 18.03 | 18.00 | 8.95 | 13.47 | 7.47 | 8.35 | 4.32 |
| MOVER_TREND_PULLBACK | kept | 1925 | 76.02 | 19.68 | 18.00 | 7.76 | 12.71 | 6.34 | 9.36 | 4.03 |
| QUIET_COMPRESSION_BREAK | filtered | 42 | 53.70 | 18.33 | 14.67 | 11.14 | 14.00 | 8.50 | 4.06 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 26 | 80.39 | 17.92 | 18.00 | 13.85 | 14.12 | 8.13 | 9.52 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 4 | 60.60 | 17.00 | 18.00 | 7.50 | 17.00 | 8.50 | 6.70 | 4.50 |
| TREND_PULLBACK_EMA | kept | 112 | 73.88 | 12.54 | 18.00 | 8.71 | 14.48 | 8.71 | 9.51 | 4.95 |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 46.00 | 17.00 | 14.00 | 12.57 | 14.57 | 5.00 | 2.28 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 72.00 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 9.00 | 4.50 |
| WHALE_MOMENTUM | filtered | 13 | 41.92 | 23.15 | 8.00 | 12.00 | 14.46 | 6.92 | 2.33 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 25 | 61.91 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| DIVERGENCE_CONTINUATION | kept | 12 | 66.85 | 0.00 | 0.00 | 0.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.40** |
| FAILED_AUCTION_RECLAIM | filtered | 137 | 54.18 | 0.00 | 0.00 | 0.53 | 0.00 | 0.95 | 0.00 | 0.00 | 0.00 | **1.48** |
| FAILED_AUCTION_RECLAIM | kept | 73 | 68.00 | 0.00 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.11** |
| FUNDING_EXTREME_SIGNAL | filtered | 31 | 47.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 66.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 67.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 50.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 75.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 93 | 78.25 | 0.00 | 0.00 | 0.00 | 0.00 | 1.81 | 0.00 | 0.00 | 0.00 | **1.81** |
| MOVER_TREND_PULLBACK | filtered | 385 | 58.33 | 0.00 | 0.00 | 1.81 | 0.00 | 6.66 | 0.00 | 0.00 | 0.00 | **8.47** |
| MOVER_TREND_PULLBACK | kept | 1925 | 76.02 | 0.00 | 0.00 | 0.49 | 0.00 | 0.71 | 0.00 | 0.00 | 0.00 | **1.20** |
| QUIET_COMPRESSION_BREAK | filtered | 42 | 53.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.29 | **1.29** |
| QUIET_COMPRESSION_BREAK | kept | 26 | 80.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 4 | 60.60 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| TREND_PULLBACK_EMA | kept | 112 | 73.88 | 0.00 | 0.00 | 0.00 | 0.00 | 3.47 | 0.00 | 0.00 | 0.00 | **3.47** |
| VOLUME_SURGE_BREAKOUT | filtered | 42 | 46.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 13 | 41.92 | 0.00 | 0.00 | 0.00 | 0.00 | 14.95 | 0.00 | 0.00 | 0.00 | **14.95** |

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
- Outcomes recorded: **35879 held of 72732 seen** across 20 strategies; 795 cells past the sample floor; **331 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 20660 | 58/20602/0 | 45% | -0.18 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.22R) |
| MOVER_AVWAP_SCALP | 3510 | 11/3499/0 | 38% | -0.32 | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (+1.03R) | ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.36R) |
| FAILED_AUCTION_RECLAIM | 1808 | 16/1792/0 | 37% | -0.34 | ASIA/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.82R) | OVERLAP/MARKUP/NORMAL/BTC_RISING/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 1689 | 0/0/1689 | 41% | -0.11 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.55R) | NY/RANGE/EXPANDED/BTC_RISING (-0.89R) |
| TREND_PULLBACK_EMA | 1634 | 0/1634/0 | 44% | -0.17 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL (+0.72R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 1452 | 0/1452/0 | 56% | +0.05 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.05R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_RANGE_FADE | 1440 | 0/0/1440 | 35% | -0.07 | ASIA/MARKUP/CASCADE/BTC_RISING (+0.28R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-0.91R) |
| SHADOW_FUNDING_FADE | 771 | 0/0/771 | 44% | -0.25 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-0.93R) |
| WHALE_MOMENTUM | 754 | 0/754/0 | 29% | -0.49 | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.00R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| QUIET_COMPRESSION_BREAK | 651 | 12/639/0 | 21% | -0.26 | ASIA/RANGE/NORMAL/BTC_RISING (-0.24R) | OVERLAP/QUIET/EXPANDED/BTC_RISING (-0.41R) |
| FUNDING_EXTREME_SIGNAL | 404 | 0/404/0 | 29% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| VOLUME_SURGE_BREAKOUT | 354 | 0/354/0 | 60% | +0.36 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| MEAN_REVERT | 238 | 2/236/0 | 81% | +0.70 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| SHADOW_CASCADE_REVERSAL | 168 | 0/0/168 | 53% | -0.07 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) |
| LIQUIDITY_SWEEP_REVERSAL | 160 | 4/156/0 | 41% | -0.22 | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL (-0.37R) | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-0.54R) |
| BREAKDOWN_SHORT | 136 | 6/130/0 | 7% | -0.86 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 18 | 0/18/0 | 22% | -0.40 | — | — |
| SR_FLIP_RETEST | 16 | 0/16/0 | 50% | -0.15 | — | — |
| MA_CROSS_TREND_SHIFT | 12 | 0/12/0 | 33% | -0.15 | — | — |
| LIQUIDATION_REVERSAL | 4 | 0/4/0 | 0% | -1.16 | — | — |

- **Strongest cells**: `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR` +1.13R (n=27, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL` +1.07R (n=50, STRONG)
- **Weakest cells**: `MOVER_AVWAP_SCALP @ ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.36R (n=15, NEGATIVE); `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.30R (n=50, NEGATIVE); `MOVER_TREND_PULLBACK @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.22R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 33 | 30% / -0.48R | 33 | 52% / -0.07R | +0.40 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 25 | 56% / +0.27R | 25 | 60% / +0.15R | -0.12 | **FIXED** |
| MEAN_REVERT | 23 | 65% / +0.28R | 23 | 65% / +0.40R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 127 | 44% / -0.21R | 127 | 46% / -0.11R | +0.11 | **ATR** |
| TREND_PULLBACK_EMA | 148 | 48% / -0.13R | 148 | 55% / -0.03R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 250 | 48% / -0.13R | 250 | 54% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 67 | 27% / -0.49R | 67 | 28% / -0.40R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 2937 | 56% / +0.01R | 2937 | 61% / +0.06R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 51 | 49% / -0.15R | 51 | 53% / -0.12R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 148 | 56% / +0.06R | 148 | 62% / +0.05R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 84 | 48% / -0.12R | 84 | 48% / -0.13R | -0.01 | **FIXED** |
| RANGE_FADE | 4 | 50% / +0.44R | 4 | 50% / +0.24R | — | **MEASURING** |
| SR_FLIP_RETEST | 8 | 50% / -0.28R | 8 | 50% / -0.05R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 4 | 25% / -0.40R | 4 | 25% / -0.36R | — | **MEASURING** |
| BREAKDOWN_SHORT | 6 | 0% / -0.58R | 6 | 0% / -0.42R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4292 | 32% | -0.05R | 199 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 250 | 52% | -0.04R | 81 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 18 | 72% | +0.19R | 17 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 34 | 29% / +0.16R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 88 | 45% / +0.98R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3466 | 42% / +0.01R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 330 | 37% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 82 | 34% / -0.10R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 159 | 47% / +0.38R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 188 | 40% / -0.22R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 52 | 42% / -0.36R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 38 | 37% / -0.34R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 28 | 32% / -0.29R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 23 | 65% / +0.41R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 18 | 28% / -0.28R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 4 | 50% / +0.21R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 9 | 22% / -0.47R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 7 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 2 | 0% / -2.70R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 52 · alerting: **9** · boot grace active: False
- **ALERT** `close_accounting` — 1 close(s) failed to write a closed-signal record — those trades are missing from the track record until retried; check fail_open for the raising site (streak 119/2) (sustained 119 cycles)
- **ALERT** `sar_ledger_candles` — 53/105 unfetchable (50%); top cause: gap or duplicate bar in the 15m window; symbols: 1000BONKUSDT, APTUSDT, AVAXUSDT, DASHUSDT, ETCUSDT +10 more (streak 119/6) (sustained 119 cycles)
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 119/6) (sustained 119 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 840x (gate reads 0x, withheld 0x — refusal dark); last HEMIUSDT age=15039.2s (streak 37/6) (sustained 37 cycles)
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=+0.48R (bound 0.3) (streak 119/6) (sustained 119 cycles)
- **ALERT** `mean_revert_emission` — 3881 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.69R over n=236, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 115/6) (sustained 115 cycles)
- **ALERT** `range_fade_emission` — 3296 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 119/6) (sustained 119 cycles)
- **ALERT** `tuned_variants` — 19 non-stamps — atr_arm_uncomputable=19 (seen=2330 stamped=245 skipped=2066) (streak 23/6) (sustained 23 cycles)
- **ALERT** `fail_open:trade_monitor._process_signal` — +92 fail-open(s) this cycle (total 9214); last: AttributeError: 'str' object has no attribute 'timestamp' (sustained 116 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 10070533 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 31 arms current, none stalled; covering 245/245 signals (100%) | 0 |
| auto_dispatch | ok | attempts=9 fanouts=9 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 79806.10 | 0 |
| candle_coverage | ok | 95/107 symbols with ≥20 15m candles, 84/107 updated within 45m [no_bucket=12, stale=11, fresh=84; 12 promoted of 107]; 23 CORE pair(s) unusable (e.g. ACTUSDT, AIOTUSDT, BARDUSDT, BMTUSDT, CELOUSDT) | 0 |
| candle_series_integrity | ok | merge dropped 990 dup bars, 0 undedupable; ws 0 out-of-order, 231 in-place; SAR refused 0 series | 0 |
| close_accounting | violating | 1 close(s) failed to write a closed-signal record — those trades are missing from the track record until retried; check fail_open for the raising site (streak 119/2) | 119 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 119/6) | 119 |
| context_emission_policy | ok | output +31 / upstream +23 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1196/1210 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 90 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1192/1206 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3119383 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=+0.48R (bound 0.3) (streak 119/6) | 119 |
| emission_controller | ok | last cycle 1376s ago; live_overrides=28 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=15 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4300 stamps (MEAN_REVERT=1415, MOVER_AVWAP_SCALP=260, MOVER_TREND_PULLBACK=2292, RANGE_FADE=232, TREND_PULLBACK_EMA=101), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 4025 evaluated, 872 suppressed, 1805 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | counter reset | 0 |
| geometry_ab | ok | output +12 / upstream +159 | 0 |
| indicator_cache_key | ok | 18317 frozen value(s) avoided; 40684 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 3881 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.69R over n=236, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 115/6) | 115 |
| mean_revert_path | ok | output +1 / upstream +159 | 0 |
| mover_admission_metadata | ok | 872 symbols known, 170 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 12 held, 12 with scan counts, 11 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s); 1 orphan(s) dropped at restore | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3054 rows held, 745089 evicted (sampled: execution:overextended 400/269874, execution:trigger_not_confirmed 400/266904, setup_compat:regime_STRONG_TREND 400/96019) | 0 |
| price_action_lane | ok | 249081 evaluated, 264 emitted; layer1 264 stamped / 0 blind; cooldown=31624, delta_opposed=28925, no_footprint=100792, no_opposing_target=766, no_sweep=59210, rr_below_floor=27500 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 3296 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 119/6) | 119 |
| range_fade_path | ok | output +45 / upstream +159 | 0 |
| sar_alignment_crosscheck | ok | 194/5104 disagreed (3.8%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +159 | 0 |
| sar_hold_arm | ok | 400 held arms settled, 77 unscored, 31 still walking (29 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 53/105 unfetchable (50%); top cause: gap or duplicate bar in the 15m window; symbols: 1000BONKUSDT, APTUSDT, AVAXUSDT, DASHUSDT, ETCUSDT +10 more (streak 119/6) | 119 |
| sar_live_arms | ok | 31 arms current, none stalled; covering 254/254 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 5 resolved, 47 still mid-window | 0 |
| scan_cycle | ok | last 67.77s, worst 87.29s over 2990 cycles; 9 over 60s, 0 over the 120s healthcheck deadline (plus 1/0 during boot warm-up, not counted); 8 executor workers | 0 |
| setup_tf_resolver | ok | 118030 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 12s ago (3.28s to run, worst 61.35s), 206 overrun(s) of 2560 cycles, TTL 900s; slowest activity=6.17s, alerts=4.03s, agents=2.16s | 0 |
| stale_tf_scoring | violating | scored on stale TF 840x (gate reads 0x, withheld 0x — refusal dark); last HEMIUSDT age=15039.2s (streak 37/6) | 37 |
| staleness_v2_shadow | ok | counter reset | 0 |
| strategy_edge | ok | output +145 / upstream +159 | 0 |
| structural_snap | ok | 4295/4295 measured, 17 blind, 0 levels moved (refusals: redetect_cooldown=963) | 0 |
| structural_veto_lane | ok | 1210 stamped; 0 with no readable level book, 0 with clear air ahead, 1037 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +159 / upstream +23 | 0 |
| tuned_variants | violating | 19 non-stamps — atr_arm_uncomputable=19 (seen=2330 stamped=245 skipped=2066) (streak 23/6) | 23 |

Fail-open exception counters (nonzero sites):
- `main.finalise_restored_terminals`: 1 — last: AttributeError: 'str' object has no attribute 'timestamp'
- `trade_monitor._process_signal`: 9214 — last: AttributeError: 'str' object has no attribute 'timestamp'

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `59904`
- `Path funnel` emissions: `21`
- `Regime distribution` emissions: `21`
- `QUIET_SCALP_BLOCK` events: `48`
- `confidence_gate` events: `2926`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **9**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 7099 | 7099 | 7338 | 0 |
| futures_aggtrade | 1 | 7489 | 7489 | 7489 | 0 |
| futures_depth | 1 | 7146 | 7146 | 7146 | 0 |
| futures_liq | 4 | 2202 | 2536 | 2830 | 0 |
| futures_mover | 1 | 7448 | 7448 | 7448 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| signal_close | 6 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=144465] state[populated=144465] buckets[many=144465] sources[none] quality[none]
- funding_rate: presence[absent=16577, present=127888] state[empty=16577, populated=127888] buckets[few=127888, none=16577] sources[none] quality[none]
- liquidation_clusters: presence[absent=89990, present=54475] state[empty=89990, populated=54475] buckets[few=46917, none=89990, some=7558] sources[none] quality[none]
- oi_snapshot: presence[absent=16577, present=127888] state[empty=16577, populated=127888] buckets[many=127888, none=16577] sources[none] quality[none]
- order_book: presence[absent=41059, present=103406] state[populated=103406, unavailable=41059] buckets[few=103406, none=41059] sources[book_ticker=103406, unavailable=41059] quality[none=41059, top_of_book_only=103406]
- orderblocks: presence[absent=144465] state[empty=144465] buckets[none=144465] sources[measured_dark=144465] quality[none]
- recent_ticks: presence[present=144465] state[populated=144465] buckets[many=144465] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `10.741796374320984` sec
- Median create→first breach: `7145.220597982407` sec
- Median create→terminal: `7148.213230013847` sec
- Median first breach→terminal: `4.035419464111328` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 2.4380353688864416 | 2.835843075094113 | 0.8597215375909087 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 2.0453722698202026 | 2.2675051396783155 | 0.902036442620974 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.8184059335237608 | 2.1100725446428545 | 0.8617741310081543 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 3.5897664160555967 | 2.76105988674625 | 1.2882080170501706 | 2 | 0 |
| MOVER_TREND_PULLBACK | 7 | 7 | 3.3920860560194983 | 2.9798999999999913 | 1.1306953520064995 | 5 | 2 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.9034237525994765 | 1.0507152406175575 | 0.8514631624685962 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.438 | 2737.222095012665 | 2740.840276002884 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 66.7 | 0.0 | 66.7 | 0.0 | 2.3658 | 13864.088130950928 | 13868.540788888931 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.7276 | 26001.613589048386 | 26003.791087150574 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2813 | 5240.605011343956 | 5244.689873933792 |
| MOVER_TREND_PULLBACK | 7 | 7 | 0.0 | 14.3 | 0.0 | 0.0 | 3.1508 | 4516.485013961792 | 4645.130663871765 |
| QUIET_COMPRESSION_BREAK | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9034 | 22019.441865086555 | 22022.52286696434 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 623 | 0 | 623 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 761 | 8 | 600 | 0.0 | 0.0 | None | None | 161 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `155`
- Gating Δ: `32672`
- No-generation Δ: `639331`
- Fast failures Δ: `-2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.6651, "current_avg_pnl": 2.3658, "current_win_rate": 66.7, "previous_avg_pnl": 1.7007, "previous_win_rate": 66.7, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.5853, "current_avg_pnl": 3.1508, "current_win_rate": 0.0, "previous_avg_pnl": 0.5655, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 161, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **FAILED_AUCTION_RECLAIM**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
