# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `1222` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 171 | 171 | 171 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17508 | 17508 | 16461 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 158661 | 158660 | 37 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 130860 | 130860 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 130455 | 126769 | 4076 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 130902 | 129316 | 1672 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 137881 | 137601 | 313 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 124092 | 124100 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 130997 | 131032 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 131043 | 127554 | 4917 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 165724 | 171196 | 2345 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 158701 | 140319 | 25338 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 137011 | 137011 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 130868 | 130889 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 130419 | 129918 | 536 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 132485 | 129827 | 3423 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 129522 | 129821 | 548 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 116968 | 109421 | 7867 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 117296 | 116384 | 1002 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 158614 | 158580 | 73 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 124107 | 124136 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 8579 | 8579 | 7934 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1745 | 1745 | 1298 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 30 | 30 | 26 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 46720 | 46720 | 46203 | 9 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 17207 | 17207 | 15422 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 6903 | 6903 | 5531 | 26 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 74049 | 74049 | 63214 | 168 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2626 | 2626 | 2547 | 8 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 11081 | 11081 | 10829 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 2529 | 2529 | 2272 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 5051 | 5051 | 4750 | 15 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 248 | 248 | 198 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=158660): breakout_not_found=93604, basic_filters_failed=35204, move_not_fresh=20408, breakout_stale=7168, retest_proximity_failed=1850, volume_spike_missing=409, move_exhausted=17
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=130860): cls_disabled_merged_into_lsr=130860
- **EVAL::DIVERGENCE_CONTINUATION** (total=126769): cvd_divergence_failed=56793, h1_trend_not_aligned=33992, basic_filters_failed=23251, ema_alignment_reject=11171, retest_proximity_failed=1212, missing_fvg_or_orderblock=350
- **EVAL::FAILED_AUCTION_RECLAIM** (total=129316): auction_not_detected=93931, basic_filters_failed=22584, reclaim_hold_failed=5708, tail_too_small=4041, regime_blocked=2995, rsi_reject=57
- **EVAL::FUNDING_EXTREME** (total=137601): funding_not_extreme=108064, basic_filters_failed=24472, ema_alignment_reject=2374, missing_funding_rate=1119, rsi_reject=957, momentum_reject=302, cvd_divergence_failed=222, missing_fvg_or_orderblock=91
- **EVAL::LIQUIDATION_REVERSAL** (total=124100): cascade_threshold_not_met=98203, basic_filters_failed=24573, cvd_divergence_failed=700, rsi_reject=574, missing_fvg_or_orderblock=33, volume_spike_missing=17
- **EVAL::MA_CROSS_TREND_SHIFT** (total=131032): no_ma_cross=106478, basic_filters_failed=23269, ma_cross_htf_misaligned=903, ma_cross_cooldown=235, ma_cross_htf_unconfirmed=147
- **EVAL::MEAN_REVERT** (total=127554): no_extension=110278, basic_filters_failed=17276
- **EVAL::MOVER_AVWAP_SCALP** (total=171196): no_avwap_tag=66936, no_mover_leg=48228, basic_filters_failed=35423, avwap_slope_against=12453, avwap_reclaim_no_volume=5116, no_avwap_reclaim=2944, anchor_too_recent=96
- **EVAL::MOVER_TREND_PULLBACK** (total=140319): mover_run_too_small=65939, basic_filters_failed=35315, no_reclaim=33908, no_pullback_tag=5157
- **EVAL::OPENING_RANGE_BREAKOUT** (total=137011): feature_disabled=137011
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=130889): regime_blocked=92099, breakout_not_found=30592, basic_filters_failed=5934, adx_reject=2207, ema_alignment_reject=52, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=129918): compression_not_detected=60846, regime_blocked=41660, basic_filters_failed=16635, breakout_not_detected=9938, volume_confirmation_failed=792, missing_fvg_or_orderblock=22, rsi_reject=21, macd_reject=4
- **EVAL::RANGE_FADE** (total=129827): no_range_edge=112544, basic_filters_failed=17283
- **EVAL::SR_FLIP_RETEST** (total=129821): flip_close_not_confirmed=92728, basic_filters_failed=22557, long_break_volume_thin=4152, regime_blocked=2977, h1_break_not_confirmed=2896, retest_out_of_zone=2775, reclaim_hold_failed=942, long_acceptance_not_held=391, ema_alignment_reject=159, wick_quality_failed=132, whipsaw_flip=79, missing_fvg_or_orderblock=33
- **EVAL::STANDARD** (total=109421): momentum_reject=32570, adx_reject=23852, basic_filters_failed=13638, sweeps_not_detected=13500, macd_reject=13286, ema_alignment_reject=8608, htf_poi_unanchored=3591, invalid_sl_geometry=210, rsi_reject=90, mtf_reject=76
- **EVAL::TREND_PULLBACK** (total=116384): h1_trend_not_aligned=37570, ema_alignment_reject=24184, basic_filters_failed=12936, h1_pullback_not_confirmed=11981, ema_not_tested_prev=9582, no_ema_reclaim_close=8541, body_conviction_fail=4524, rsi_reject=3871, prev_already_above_emas=1114, prev_already_below_emas=715, no_prev_high_break=714, no_prev_low_break=398, momentum_flat=174, ema21_not_tagged=57, missing_fvg_or_orderblock=23
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=158580): breakout_not_found=96664, basic_filters_failed=35199, move_not_fresh=17150, breakout_stale=7018, retest_proximity_failed=2141, volume_spike_missing=383, missing_fvg_or_orderblock=14, move_exhausted=11
- **EVAL::WHALE_MOMENTUM** (total=124136): momentum_reject=80564, recent_ticks_insufficient=35066, basic_filters_failed=8506

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=345): setup_compat:regime_VOLATILE_UNSUITABLE=345
- **FAILED_AUCTION_RECLAIM** (total=1697): setup_compat:regime_STRONG_TREND=728, execution:overextended=714, context_floor=255
- **FUNDING_EXTREME_SIGNAL** (total=1464): execution:trigger_not_confirmed=1464
- **LIQUIDATION_REVERSAL** (total=30): execution:trigger_not_confirmed=30
- **LIQUIDITY_SWEEP_REVERSAL** (total=10409): execution:trigger_not_confirmed=4416, execution:overextended=3249, setup_compat:regime_STRONG_TREND=2744
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_DIRTY_RANGE=1, execution:overextended=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=9604): setup_compat:regime_STRONG_TREND=4480, setup_compat:regime_WEAK_TREND=2990, execution:overextended=2123, entry_quality=11
- **MOVER_AVWAP_SCALP** (total=3841): execution:overextended=2838, execution:trigger_not_confirmed=828, entry_quality=175
- **MOVER_TREND_PULLBACK** (total=30528): execution:trigger_not_confirmed=18105, execution:overextended=10777, entry_quality=1646
- **QUIET_COMPRESSION_BREAK** (total=32): execution:overextended=32
- **RANGE_FADE** (total=6158): setup_compat:regime_STRONG_TREND=3080, setup_compat:regime_WEAK_TREND=2057, execution:overextended=558, setup_compat:regime_VOLATILE_UNSUITABLE=444, setup_compat:regime_BREAKOUT_EXPANSION=16, context_edge=3
- **TREND_PULLBACK_EMA** (total=4440): setup_compat:regime_CLEAN_RANGE=2644, setup_compat:regime_DIRTY_RANGE=1615, setup_compat:regime_VOLATILE_UNSUITABLE=129, entry_quality=52
- **VOLUME_SURGE_BREAKOUT** (total=36): execution:overextended=36

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 411741 | 46.4% |
| QUIET | 198318 | 22.4% |
| TRENDING_DOWN | 129346 | 14.6% |
| TRENDING_UP | 122216 | 13.8% |
| VOLATILE | 24808 | 2.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **54**
- Average confidence gap to threshold: **10.11** (samples=54) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=9, FILUSDT=8, ETCUSDT=7, HYPEUSDT=7, DOTUSDT=7, XRPUSDT=4, BCHUSDT=4, MUBARAKUSDT=3, ZECUSDT=3, LYNUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 114 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 184 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 14 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 9 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 20 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 68 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 8 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 42 |
| MEAN_REVERT | filtered | min_confidence | 79 |
| MEAN_REVERT | kept | min_confidence_pass | 32 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 513 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 280 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1858 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 14 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2905 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 23 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 2 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 10 |
| SR_FLIP_RETEST | filtered | min_confidence | 40 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 90 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 29 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 121 | 45.28 | 65.00 | 19.72 | 20.72 | 19.80 | 17.52 | 1.13 | 23.80 |
| DIVERGENCE_CONTINUATION | kept | 184 | 66.62 | 65.00 | -1.62 | 20.13 | 19.88 | 18.21 | 2.07 | 4.52 |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 56.63 | 61.00 | 4.37 | 19.61 | 19.34 | 20.00 | 1.64 | 9.86 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 71.10 | 65.00 | -6.10 | 21.10 | 20.00 | 20.00 | 5.00 | 6.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 60.00 | 61.00 | 1.00 | 22.13 | 14.00 | 17.00 | 3.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 20 | 69.00 | 65.00 | -4.00 | 21.19 | 20.00 | 17.00 | 0.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 76 | 52.38 | 64.42 | 12.04 | 21.16 | 19.96 | 17.83 | 0.16 | 16.31 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 42 | 70.15 | 65.00 | -5.15 | 21.63 | 19.55 | 17.25 | 0.71 | 0.06 |
| MEAN_REVERT | filtered | 79 | 58.19 | 64.65 | 6.46 | 17.91 | 14.03 | 16.72 | 0.00 | 7.76 |
| MEAN_REVERT | kept | 32 | 66.49 | 65.00 | -1.49 | 21.36 | 15.07 | 15.07 | 0.00 | 1.74 |
| MOVER_AVWAP_SCALP | filtered | 515 | 53.87 | 63.79 | 9.92 | 20.42 | 16.93 | 15.80 | 3.96 | 21.40 |
| MOVER_AVWAP_SCALP | kept | 280 | 80.29 | 65.00 | -15.29 | 21.14 | 16.49 | 15.80 | 4.36 | 5.05 |
| MOVER_TREND_PULLBACK | filtered | 1872 | 56.86 | 63.71 | 6.85 | 19.85 | 18.16 | 15.80 | 4.23 | 17.06 |
| MOVER_TREND_PULLBACK | kept | 2905 | 77.05 | 65.00 | -12.05 | 19.96 | 18.89 | 15.80 | 4.29 | 1.67 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 53.75 | 65.00 | 11.25 | 21.85 | 19.70 | 20.00 | 0.00 | 6.12 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 74.87 | 65.00 | -9.87 | 22.24 | 19.33 | 20.00 | 0.00 | 1.78 |
| SR_FLIP_RETEST | filtered | 40 | 59.50 | 60.00 | 0.50 | 19.45 | 20.00 | 15.20 | 1.00 | 10.50 |
| TREND_PULLBACK_EMA | filtered | 4 | 64.10 | 65.00 | 0.90 | 21.20 | 18.60 | 16.20 | 4.50 | 15.90 |
| TREND_PULLBACK_EMA | kept | 90 | 71.83 | 65.00 | -6.83 | 21.60 | 19.95 | 18.52 | 4.80 | 0.71 |
| VOLUME_SURGE_BREAKOUT | filtered | 29 | 52.40 | 65.00 | 12.60 | 17.85 | 14.00 | 20.00 | 3.97 | 6.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 121 | 45.28 | 24.67 | 11.47 | 5.50 | 13.40 | 5.29 | 7.61 | 1.13 |
| DIVERGENCE_CONTINUATION | kept | 184 | 66.62 | 24.57 | 12.84 | 3.85 | 14.60 | 4.62 | 8.78 | 2.07 |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 56.63 | 17.00 | 18.00 | 5.57 | 12.07 | 8.36 | 3.84 | 1.64 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 71.10 | 25.00 | 18.00 | 6.00 | 9.00 | 8.50 | 6.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 60.00 | 25.00 | 8.00 | 3.00 | 12.00 | 9.00 | 5.00 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 20 | 69.00 | 17.00 | 20.00 | 6.00 | 10.00 | 9.00 | 7.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 76 | 52.38 | 22.55 | 16.47 | 5.17 | 11.70 | 5.81 | 6.80 | 0.16 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 42 | 70.15 | 24.76 | 14.00 | 4.14 | 13.90 | 5.17 | 7.58 | 0.71 |
| MEAN_REVERT | filtered | 79 | 58.19 | 17.00 | 14.30 | 9.00 | 13.00 | 5.00 | 7.65 | 0.00 |
| MEAN_REVERT | kept | 32 | 66.49 | 18.25 | 18.00 | 9.66 | 12.19 | 5.00 | 5.14 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 515 | 53.87 | 17.99 | 18.05 | 12.91 | 13.68 | 5.39 | 5.87 | 3.96 |
| MOVER_AVWAP_SCALP | kept | 280 | 80.29 | 20.94 | 18.44 | 12.78 | 14.00 | 6.53 | 8.32 | 4.36 |
| MOVER_TREND_PULLBACK | filtered | 1872 | 56.86 | 18.55 | 18.00 | 7.66 | 12.81 | 6.28 | 8.18 | 4.23 |
| MOVER_TREND_PULLBACK | kept | 2905 | 77.05 | 19.92 | 18.09 | 7.85 | 13.06 | 6.45 | 9.18 | 4.29 |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 53.75 | 18.28 | 17.68 | 11.16 | 14.72 | 5.10 | 3.42 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 74.87 | 18.60 | 18.00 | 11.70 | 14.00 | 7.45 | 6.90 | 0.00 |
| SR_FLIP_RETEST | filtered | 40 | 59.50 | 17.00 | 18.00 | 9.00 | 14.00 | 5.00 | 6.00 | 1.00 |
| TREND_PULLBACK_EMA | filtered | 4 | 64.10 | 17.00 | 18.00 | 7.50 | 14.00 | 9.00 | 10.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 90 | 71.83 | 12.80 | 18.02 | 7.53 | 13.49 | 6.58 | 9.53 | 4.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 29 | 52.40 | 19.48 | 18.00 | 12.00 | 13.38 | 4.48 | 2.69 | 3.97 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 121 | 45.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 184 | 66.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 14 | 56.63 | 0.00 | 0.00 | 0.00 | 0.00 | 1.71 | 0.00 | 0.00 | 0.00 | **1.71** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 71.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 60.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 20 | 69.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 76 | 52.38 | 0.00 | 0.00 | 2.40 | 0.00 | 1.14 | 0.00 | 0.00 | 0.00 | **3.54** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 42 | 70.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 79 | 58.19 | 0.00 | 0.00 | 0.00 | 0.00 | 6.77 | 0.00 | 0.00 | 0.00 | **6.77** |
| MEAN_REVERT | kept | 32 | 66.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 515 | 53.87 | 0.00 | 0.00 | 1.51 | 0.00 | 3.04 | 0.00 | 0.00 | 2.17 | **6.72** |
| MOVER_AVWAP_SCALP | kept | 280 | 80.29 | 0.00 | 0.00 | 0.06 | 0.00 | 4.19 | 0.00 | 0.00 | 0.13 | **4.38** |
| MOVER_TREND_PULLBACK | filtered | 1872 | 56.86 | 0.18 | 0.00 | 0.27 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **0.67** |
| MOVER_TREND_PULLBACK | kept | 2905 | 77.05 | 0.02 | 0.00 | 0.03 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **0.27** |
| QUIET_COMPRESSION_BREAK | filtered | 25 | 53.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.19 | 0.00 | 0.00 | 3.89 | **4.08** |
| QUIET_COMPRESSION_BREAK | kept | 10 | 74.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.08 | **1.08** |
| SR_FLIP_RETEST | filtered | 40 | 59.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 4 | 64.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 90 | 71.83 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.09** |
| VOLUME_SURGE_BREAKOUT | filtered | 29 | 52.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |

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
- Outcomes recorded: **113785 held of 332507 seen** across 21 strategies; 2595 cells past the sample floor; **1204 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 39218 | 586/38632/0 | 46% | -0.13 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.22R) |
| MOVER_AVWAP_SCALP | 14489 | 187/14302/0 | 40% | -0.28 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 8700 | 107/8593/0 | 43% | -0.14 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+1.74R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 7416 | 44/7372/0 | 51% | +0.02 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 6117 | 0/0/6117 | 43% | -0.09 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.87R) |
| TREND_PULLBACK_EMA | 5816 | 26/5790/0 | 46% | -0.09 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_RANGE_FADE | 5275 | 0/0/5275 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| QUIET_COMPRESSION_BREAK | 5035 | 305/4730/0 | 47% | -0.13 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4779 | 0/0/4779 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 3593 | 60/3533/0 | 40% | -0.34 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.93R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (-1.41R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2279 | 32/2247/0 | 48% | -0.11 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1973 | 2/1971/0 | 31% | -0.45 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1909 | 0/1909/0 | 35% | -0.17 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1274 | 12/1262/0 | 50% | -0.17 | ASIA/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.80R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 923 | 0/0/923 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 761 | 2/759/0 | 39% | -0.40 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 551 | 53/498/0 | 32% | -0.35 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 66 | 8/58/0 | 48% | -0.01 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ NY/MARKUP/NORMAL/BTC_RISING/MIDCAP` +2.03R (n=15, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP` -1.41R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 148 | 27% / -0.56R | 148 | 46% / -0.20R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 483 | 43% / -0.23R | 483 | 55% / -0.03R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 1159 | 43% / -0.21R | 1159 | 50% / -0.08R | +0.13 | **ATR** |
| BREAKDOWN_SHORT | 45 | 40% / -0.21R | 45 | 44% / -0.08R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 141 | 48% / -0.27R | 141 | 50% / -0.17R | +0.10 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 731 | 50% / -0.22R | 731 | 56% / -0.12R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 6088 | 50% / -0.10R | 6088 | 55% / -0.01R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 816 | 43% / -0.18R | 816 | 45% / -0.10R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 105 | 39% / -0.13R | 105 | 47% / -0.07R | +0.06 | **ATR** |
| DIVERGENCE_CONTINUATION | 688 | 51% / -0.05R | 688 | 57% / -0.03R | +0.02 | **ATR** |
| RANGE_FADE | 40 | 38% / -0.25R | 40 | 40% / -0.26R | -0.01 | **FIXED** |
| MEAN_REVERT | 171 | 54% / -0.05R | 171 | 52% / -0.05R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 812 | 46% / -0.16R | 812 | 46% / -0.16R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 21 | 43% / -0.12R | 21 | 43% / -0.12R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8706 | 29% | -0.25R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1159 | 48% | -0.08R | 196 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 65 | 49% | -0.07R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 786 | 35% / -0.13R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7788 | 36% / -0.16R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1525 | 35% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 660 | 35% / -0.14R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 776 | 40% / +0.02R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 640 | 39% / -0.03R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 729 | 42% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 151 | 28% / -0.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 196 | 30% / -0.61R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 139 | 57% / +0.15R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 78 | 42% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 31 | 35% / +0.11R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 144 | 35% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 31 | 23% / -0.36R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 10 | 40% / +0.02R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 60 · alerting: **4** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 41/58 unfetchable (71%); top cause: gap or duplicate bar in the 15m window; symbols: 2ZUSDT, ACEUSDT, AVAXUSDT, ETCUSDT, GRAMUSDT +7 more (streak 76/6) (sustained 76 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×726]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 76/6) (sustained 76 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.57R (bound 0.3) (streak 76/6) (sustained 76 cycles)
- **ALERT** `tuned_variants` — 67 non-stamps — atr_arm_uncomputable=67 (seen=1986 stamped=116 skipped=1803) (streak 71/6) (sustained 71 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 6495530 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 29 arms current, none stalled; covering 888/888 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 2 live ATR-trail arms could not be advanced this cycle (0 no candles, 2 bars behind; 60 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| auto_dispatch | ok | 12 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=12. No user is on live. | 0 |
| binance_ip_weight | ok | peak 136/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 84352.90 | 0 |
| candle_coverage | ok | 78/78 symbols with ≥20 15m candles, 78/78 updated within 45m [fresh=78; 74 Tier-1 futures + 4 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 595 dup bars, 0 undedupable; ws 0 out-of-order, 150 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 34 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 34 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +36 / upstream +52 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1096/1113 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 77 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1094/1111 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 2065977 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.57R (bound 0.3) (streak 76/6) | 76 |
| emission_controller | ok | last cycle 964s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×726]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 76/6) | 76 |
| entry_quality_effective | ok | 2252 evaluated, 811 suppressed, 1441 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,293 reads/day of 50,000 [engine 1,293, signing 0]; top site keystore.roster_doc at 290/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +339 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 3526 frozen value(s) avoided; 121280 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.12R over n=2247 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +2 / upstream +339 | 0 |
| mover_admission_metadata | ok | 907 symbols known, 201 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 4 held, 4 with scan counts, 3 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1975790 evicted (sampled: execution:trigger_not_confirmed 400/728220, execution:overextended 400/659942, setup_compat:regime_STRONG_TREND 400/290012) | 0 |
| price_action_lane | ok | 318478 evaluated, 197 emitted; layer1 197 stamped / 0 blind; cooldown=40348, delta_opposed=23898, no_footprint=116290, no_opposing_target=1272, no_sweep=114612, rr_below_floor=21861 | 0 |
| promoted_pair_integrity | ok | 4/4 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.41R over n=759 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +60 / upstream +339 | 0 |
| sar_alignment_crosscheck | ok | 114/2354 disagreed (4.8%) | 0 |
| sar_exit_shadow | violating | upstream +339 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1830 held arms settled, 170 unscored, 60 still walking (53 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 41/58 unfetchable (71%); top cause: gap or duplicate bar in the 15m window; symbols: 2ZUSDT, ACEUSDT, AVAXUSDT, ETCUSDT, GRAMUSDT +7 more (streak 76/6) | 76 |
| sar_live_arms | violating | 2 live SAR arms could not be advanced this cycle (0 no candles, 2 bars behind; 58 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| sar_refresh_budget | ok | 24 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 458 records await one (17 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 3/12) | 3 |
| scan_cycle | ok | last 21.74s, worst 68.19s over 3799 lifetime cycles; lifetime 1 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.47s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 105373 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (14.13s to run, worst 40.73s), 70 overrun(s) of 1745 cycles, TTL 900s; slowest router_delivery=4.97s, tickers=2.87s, dark_promotion=1.89s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +2 / upstream +339 | 0 |
| structural_snap | ok | 5624/5624 measured, 30 blind, 0 levels moved (refusals: redetect_cooldown=320) | 0 |
| structural_veto_lane | ok | 417 stamped; 0 with no readable level book, 9 with clear air ahead, 170 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +339 / upstream +52 | 0 |
| tuned_variants | violating | 67 non-stamps — atr_arm_uncomputable=67 (seen=1986 stamped=116 skipped=1803) (streak 71/6) | 71 |
| unlock_shorts | ok | 2 open, 45 scheduled, calendar 4.5h old | 0 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration
- `llm_client.google`: 1 — last: ClientOSError: [Errno 32] Broken pipe

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3949018`
- `Path funnel` emissions: `104`
- `Regime distribution` emissions: `104`
- `QUIET_SCALP_BLOCK` events: `54`
- `confidence_gate` events: `6348`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **11**
- Total REST-fallback activations: **3**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 3108 | 3498 | 6513 | 0 |
| futures_aggtrade | 2 | 1773 | 1773 | 2179 | 0 |
| futures_depth | 3 | 3068 | 3068 | 3321 | 0 |
| futures_liq | 2 | 3015 | 3015 | 3997 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 3 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=4, present=751033] state[empty=4, populated=751033] buckets[few=19, many=750822, none=4, some=192] sources[none] quality[none]
- funding_rate: presence[absent=80154, present=670883] state[empty=80154, populated=670883] buckets[few=670883, none=80154] sources[none] quality[none]
- liquidation_clusters: presence[absent=396755, present=354282] state[empty=396755, populated=354282] buckets[few=293930, none=396755, some=60352] sources[none] quality[none]
- oi_snapshot: presence[absent=77709, present=673328] state[empty=77709, populated=673328] buckets[few=180, many=672172, none=77709, some=976] sources[none] quality[none]
- order_book: presence[absent=184092, present=566945] state[populated=566945, unavailable=184092] buckets[few=566945, none=184092] sources[book_ticker=566945, unavailable=184092] quality[none=184092, top_of_book_only=566945]
- orderblocks: presence[absent=751037] state[empty=751037] buckets[none=751037] sources[measured_dark=751037] quality[none]
- recent_ticks: presence[present=751037] state[populated=751037] buckets[many=751037] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.8114506006240845` sec
- Median create→first breach: `4289.04060447216` sec
- Median create→terminal: `4289.040641546249` sec
- Median first breach→terminal: `9.059906005859375e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.8000000000000068 | 0.8816630378776006 | 0.9073761353609894 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 1.4177584185845031 | 1.5061739547827582 | 0.9415509743974313 | 0 | 2 |
| MEAN_REVERT | 1 | 1 | 1.0070065374805797 | 1.3023658057518124 | 0.7732132808103545 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.0106372663374845 | 2.2190441353632204 | 0.9080919360092425 | 0 | 2 |
| MOVER_TREND_PULLBACK | 36 | 36 | 3.13118258564438 | 2.9628302462607574 | 1.0683278716356188 | 20 | 16 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.9143666573237496 | 1.0579217402041514 | 0.879315603522753 | 0 | 3 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.5260276897021523 | 3.0 | 0.8420092299007175 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.5343 | 5631.590969800949 | 5631.778519868851 |
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.7012 | 17799.83472597599 | 17799.834745407104 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 11679.603925943375 | 11679.604652881622 |
| MOVER_AVWAP_SCALP | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 2.9414 | 3290.0481770038605 | 3290.50357401371 |
| MOVER_TREND_PULLBACK | 36 | 36 | 30.6 | 41.7 | 30.6 | 0.0 | -0.039 | 3607.173320055008 | 3607.173359513283 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9649 | 18801.635491847992 | 18801.63558292389 |
| TREND_PULLBACK_EMA | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 4.7086 | 1250.937950849533 | 1251.2113358974457 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 2529 | 0 | 2272 | 0.0 | 0.0 | None | None | 257 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 5051 | 15 | 4750 | 100.0 | 0.0 | 1250.937950849533 | 1251.2113358974457 | 301 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-11`
- Gating Δ: `-27738`
- No-generation Δ: `213045`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.1151, "current_avg_pnl": -0.7012, "current_win_rate": 0.0, "previous_avg_pnl": -1.8163, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.55, "current_avg_pnl": -0.039, "current_win_rate": 30.6, "previous_avg_pnl": 0.511, "previous_win_rate": 31.2, "win_rate_delta": -0.6}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.4557, "current_avg_pnl": -0.9649, "current_win_rate": 0.0, "previous_avg_pnl": -0.5092, "previous_win_rate": 16.7, "win_rate_delta": -16.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 212, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": -25, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1250.94, "median_terminal_delta_sec": 1251.21, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
