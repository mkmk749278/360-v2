# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `20` sec (warning=False)
- Latest performance record age: `14421` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 8455 | 8455 | 8001 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 37457 | 37462 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 34335 | 34339 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 34155 | 31827 | 2501 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 34343 | 32482 | 1975 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 34999 | 34810 | 209 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 31114 | 31119 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 34460 | 34472 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 34472 | 31877 | 2902 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 39015 | 40636 | 101 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 37462 | 33207 | 5800 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 34026 | 34030 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 34339 | 34343 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 34145 | 34011 | 140 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 34781 | 33129 | 2033 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 33157 | 32583 | 1537 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 30080 | 28337 | 1878 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 30219 | 30082 | 165 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 37441 | 37451 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 31119 | 31082 | 55 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7224 | 7224 | 5220 | 14 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 542 | 542 | 494 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8993 | 8993 | 8798 | 8 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6674 | 6674 | 4695 | 12 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 198 | 198 | 193 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 13118 | 13118 | 11479 | 12 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 693 | 693 | 466 | 5 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 4255 | 4255 | 377 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 5897 | 5897 | 1884 | 42 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1011 | 1011 | 1007 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 33 | 33 | 32 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2164 | 2164 | 1880 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=37462): breakout_not_found=17729, basic_filters_failed=12922, move_not_fresh=4894, breakout_stale=1596, retest_proximity_failed=274, ema_alignment_reject=24, volume_spike_missing=22, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=34339): cls_disabled_merged_into_lsr=34339
- **EVAL::DIVERGENCE_CONTINUATION** (total=31827): cvd_divergence_failed=11110, basic_filters_failed=10388, h1_trend_not_aligned=6754, ema_alignment_reject=2825, retest_proximity_failed=458, regime_blocked=199, missing_fvg_or_orderblock=93
- **EVAL::FAILED_AUCTION_RECLAIM** (total=32482): auction_not_detected=11631, basic_filters_failed=10350, tail_too_small=5249, reclaim_hold_failed=4947, regime_blocked=305
- **EVAL::FUNDING_EXTREME** (total=34810): funding_not_extreme=21425, basic_filters_failed=10371, ema_alignment_reject=1206, missing_funding_rate=1180, rsi_reject=426, cvd_divergence_failed=95, momentum_reject=89, missing_fvg_or_orderblock=18
- **EVAL::LIQUIDATION_REVERSAL** (total=31119): cascade_threshold_not_met=19914, basic_filters_failed=10971, cvd_divergence_failed=168, rsi_reject=64, volume_spike_missing=1, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=34472): no_ma_cross=23748, basic_filters_failed=10389, ma_cross_cooldown=247, ma_cross_htf_misaligned=88
- **EVAL::MEAN_REVERT** (total=31877): no_extension=25910, basic_filters_failed=5967
- **EVAL::MOVER_AVWAP_SCALP** (total=40636): no_avwap_tag=13338, basic_filters_failed=12343, no_mover_leg=10368, avwap_slope_against=2359, no_avwap_reclaim=1110, insufficient_candles=833, avwap_reclaim_no_volume=270, anchor_too_recent=15
- **EVAL::MOVER_TREND_PULLBACK** (total=33207): mover_run_too_small=13834, basic_filters_failed=12317, no_reclaim=5352, no_pullback_tag=871, insufficient_candles=833
- **EVAL::OPENING_RANGE_BREAKOUT** (total=34030): feature_disabled=34030
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=34343): regime_blocked=27182, breakout_not_found=4028, basic_filters_failed=1741, adx_reject=1381, ema_alignment_reject=11
- **EVAL::QUIET_COMPRESSION_BREAK** (total=34011): compression_not_detected=14767, basic_filters_failed=8606, regime_blocked=7441, breakout_not_detected=2829, volume_confirmation_failed=358, missing_fvg_or_orderblock=8, rsi_reject=2
- **EVAL::RANGE_FADE** (total=33129): no_range_edge=27160, basic_filters_failed=5969
- **EVAL::SR_FLIP_RETEST** (total=32583): basic_filters_failed=10346, flip_close_not_confirmed=5940, whipsaw_flip=4336, long_break_volume_thin=3309, reclaim_hold_failed=2987, long_disabled=2433, retest_out_of_zone=2255, wick_quality_failed=439, regime_blocked=302, long_acceptance_not_held=101, ema_alignment_reject=94, missing_fvg_or_orderblock=41
- **EVAL::STANDARD** (total=28337): momentum_reject=9123, adx_reject=7678, basic_filters_failed=4884, sweeps_not_detected=2995, macd_reject=2793, ema_alignment_reject=642, invalid_sl_geometry=192, rsi_reject=30
- **EVAL::TREND_PULLBACK** (total=30082): h1_trend_not_aligned=9419, h1_pullback_not_confirmed=7644, ema_alignment_reject=2730, basic_filters_failed=2423, no_ema_reclaim_close=2213, ema_not_tested_prev=1426, body_conviction_fail=1413, rsi_reject=1317, regime_blocked=832, no_prev_low_break=304, prev_already_below_emas=162, prev_already_above_emas=82, momentum_reject=41, no_prev_high_break=38, momentum_flat=24, ema21_not_tagged=8, missing_fvg_or_orderblock=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=37451): breakout_not_found=19880, basic_filters_failed=12922, move_not_fresh=3401, breakout_stale=905, retest_proximity_failed=243, volume_spike_missing=58, missing_fvg_or_orderblock=37, rsi_reject=5
- **EVAL::WHALE_MOMENTUM** (total=31082): momentum_reject=19718, recent_ticks_insufficient=8104, basic_filters_failed=3260

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=188): context_floor=113, setup_compat:regime_BREAKOUT_EXPANSION=63, setup_compat:regime_VOLATILE_UNSUITABLE=10, execution:overextended=2
- **FAILED_AUCTION_RECLAIM** (total=1494): context_floor=568, setup_compat:regime_STRONG_TREND=516, execution:overextended=402, setup_compat:regime_VOLATILE_UNSUITABLE=8
- **FUNDING_EXTREME_SIGNAL** (total=494): execution:trigger_not_confirmed=494
- **LIQUIDITY_SWEEP_REVERSAL** (total=2618): execution:overextended=1433, execution:trigger_not_confirmed=866, setup_compat:regime_STRONG_TREND=303, context_floor=16
- **MEAN_REVERT** (total=2143): setup_compat:regime_WEAK_TREND=987, execution:overextended=688, setup_compat:regime_STRONG_TREND=468
- **MOVER_AVWAP_SCALP** (total=193): execution:trigger_not_confirmed=114, execution:overextended=79
- **MOVER_TREND_PULLBACK** (total=11132): execution:trigger_not_confirmed=5791, execution:overextended=5341
- **QUIET_COMPRESSION_BREAK** (total=60): context_floor=60
- **RANGE_FADE** (total=1428): context_edge=1428
- **TREND_PULLBACK_EMA** (total=976): setup_compat:regime_CLEAN_RANGE=829, setup_compat:regime_DIRTY_RANGE=147
- **WHALE_MOMENTUM** (total=1776): execution:trigger_not_confirmed=1776

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 71891 | 37.9% |
| QUIET | 64488 | 34.0% |
| TRENDING_DOWN | 27545 | 14.5% |
| TRENDING_UP | 21192 | 11.2% |
| VOLATILE | 4451 | 2.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **591**
- Average confidence gap to threshold: **17.06** (samples=591) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AAVEUSDT=49, ARBUSDT=47, BTCUSDT=47, ENAUSDT=47, XLMUSDT=40, SOLUSDT=31, UNIUSDT=30, PENGUUSDT=27, ONDOUSDT=26, LITUSDT=26

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 13 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 6 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 223 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 31 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 367 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 14 |
| MEAN_REVERT | filtered | min_confidence | 76 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 59 |
| MEAN_REVERT | kept | min_confidence_pass | 1351 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 12 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 945 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 6 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 135 |
| RANGE_FADE | filtered | quiet_scalp_min_confidence | 46 |
| RANGE_FADE | kept | min_confidence_pass | 49 |
| SR_FLIP_RETEST | filtered | min_confidence | 278 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 221 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 993 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 2 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 53.17 | 65.00 | 11.83 | 21.90 | 20.00 | 17.13 | 1.05 | 15.74 |
| FAILED_AUCTION_RECLAIM | filtered | 254 | 50.52 | 64.39 | 13.87 | 20.91 | 19.77 | 20.00 | 4.31 | 6.54 |
| FAILED_AUCTION_RECLAIM | kept | 367 | 71.70 | 65.00 | -6.70 | 21.20 | 19.05 | 20.00 | 3.36 | 0.55 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 49.00 | 65.00 | 16.00 | 17.20 | 20.00 | 20.00 | 0.00 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 66.55 | 65.00 | -1.55 | 20.58 | 19.59 | 17.71 | 1.43 | 0.86 |
| MEAN_REVERT | filtered | 135 | 51.07 | 62.44 | 11.37 | 21.24 | 14.45 | 19.28 | 0.00 | 20.27 |
| MEAN_REVERT | kept | 1351 | 71.04 | 65.00 | -6.04 | 21.38 | 15.68 | 17.99 | 0.00 | 0.46 |
| MOVER_AVWAP_SCALP | kept | 1 | 83.50 | 65.00 | -18.50 | 18.20 | 17.80 | 15.80 | 5.00 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 12 | 62.67 | 65.00 | 2.33 | 20.14 | 19.35 | 15.80 | 4.33 | 12.00 |
| MOVER_TREND_PULLBACK | kept | 945 | 78.28 | 65.00 | -13.28 | 20.68 | 18.50 | 15.80 | 4.64 | 1.33 |
| QUIET_COMPRESSION_BREAK | filtered | 28 | 51.49 | 65.00 | 13.51 | 22.78 | 19.81 | 20.00 | 0.00 | 5.63 |
| QUIET_COMPRESSION_BREAK | kept | 135 | 79.13 | 65.00 | -14.13 | 20.24 | 20.00 | 20.00 | 0.00 | 1.13 |
| RANGE_FADE | filtered | 46 | 42.31 | 65.00 | 22.69 | 20.67 | 14.00 | 20.00 | 0.00 | 29.93 |
| RANGE_FADE | kept | 49 | 67.37 | 65.00 | -2.37 | 20.57 | 14.00 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 499 | 53.92 | 63.90 | 9.98 | 20.95 | 19.86 | 15.88 | 1.58 | 15.56 |
| SR_FLIP_RETEST | kept | 993 | 69.58 | 65.00 | -4.58 | 21.57 | 19.93 | 15.66 | 2.22 | 2.55 |
| TREND_PULLBACK_EMA | kept | 2 | 78.50 | 65.00 | -13.50 | 21.20 | 20.00 | 17.25 | 5.50 | 0.00 |
| WHALE_MOMENTUM | filtered | 7 | 21.60 | 65.00 | 43.40 | 23.90 | 20.00 | 17.00 | 0.00 | 31.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 53.17 | 19.95 | 11.16 | 8.53 | 12.74 | 7.39 | 8.09 | 1.05 |
| FAILED_AUCTION_RECLAIM | filtered | 254 | 50.52 | 23.46 | 14.49 | 5.21 | 11.88 | 6.43 | 4.39 | 4.31 |
| FAILED_AUCTION_RECLAIM | kept | 367 | 71.70 | 21.33 | 16.79 | 3.73 | 11.34 | 7.08 | 8.63 | 3.36 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 49.00 | 25.00 | 18.00 | 6.00 | 11.00 | 5.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 66.55 | 19.71 | 14.00 | 6.43 | 12.71 | 5.36 | 7.76 | 1.43 |
| MEAN_REVERT | filtered | 135 | 51.07 | 21.15 | 18.00 | 6.82 | 12.93 | 5.94 | 6.51 | 0.00 |
| MEAN_REVERT | kept | 1351 | 71.04 | 22.70 | 18.00 | 4.78 | 13.00 | 5.23 | 7.78 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 1 | 83.50 | 17.00 | 18.00 | 15.00 | 10.00 | 8.50 | 10.00 | 5.00 |
| MOVER_TREND_PULLBACK | filtered | 12 | 62.67 | 16.67 | 18.00 | 8.25 | 11.50 | 5.92 | 10.00 | 4.33 |
| MOVER_TREND_PULLBACK | kept | 945 | 78.28 | 19.74 | 18.00 | 8.14 | 13.20 | 6.03 | 9.85 | 4.64 |
| QUIET_COMPRESSION_BREAK | filtered | 28 | 51.49 | 17.29 | 17.14 | 11.79 | 14.00 | 8.05 | 4.28 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 135 | 79.13 | 22.93 | 17.97 | 11.29 | 14.00 | 7.89 | 7.65 | 0.00 |
| RANGE_FADE | filtered | 46 | 42.31 | 20.65 | 18.00 | 8.87 | 13.59 | 5.62 | 5.51 | 0.00 |
| RANGE_FADE | kept | 49 | 67.37 | 24.51 | 18.00 | 3.55 | 10.80 | 5.16 | 5.34 | 0.00 |
| SR_FLIP_RETEST | filtered | 499 | 53.92 | 19.11 | 13.57 | 8.59 | 13.24 | 5.99 | 7.40 | 1.58 |
| SR_FLIP_RETEST | kept | 993 | 69.58 | 22.16 | 16.05 | 5.61 | 13.09 | 6.03 | 7.87 | 2.22 |
| TREND_PULLBACK_EMA | kept | 2 | 78.50 | 21.00 | 18.00 | 7.50 | 12.00 | 6.50 | 8.00 | 5.50 |
| WHALE_MOMENTUM | filtered | 7 | 21.60 | 25.00 | 8.00 | 12.00 | 12.00 | 8.50 | 2.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 53.17 | 0.00 | 0.00 | 0.76 | 0.00 | 12.51 | 0.00 | 0.00 | 0.00 | **13.27** |
| FAILED_AUCTION_RECLAIM | filtered | 254 | 50.52 | 0.00 | 0.00 | 0.19 | 0.00 | 4.08 | 0.00 | 0.00 | 0.00 | **4.27** |
| FAILED_AUCTION_RECLAIM | kept | 367 | 71.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 49.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 66.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **0.86** |
| MEAN_REVERT | filtered | 135 | 51.07 | 9.78 | 0.00 | 1.49 | 0.00 | 9.00 | 0.00 | 0.00 | 0.00 | **20.27** |
| MEAN_REVERT | kept | 1351 | 71.04 | 0.01 | 0.00 | 0.00 | 0.00 | 0.44 | 0.00 | 0.00 | 0.00 | **0.45** |
| MOVER_AVWAP_SCALP | kept | 1 | 83.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 12 | 62.67 | 0.00 | 0.00 | 10.00 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_TREND_PULLBACK | kept | 945 | 78.28 | 0.00 | 0.00 | 0.65 | 0.00 | 0.68 | 0.00 | 0.00 | 0.00 | **1.33** |
| QUIET_COMPRESSION_BREAK | filtered | 28 | 51.49 | 0.00 | 0.00 | 0.00 | 0.00 | 1.38 | 0.00 | 0.00 | 4.24 | **5.62** |
| QUIET_COMPRESSION_BREAK | kept | 135 | 79.13 | 0.00 | 0.00 | 1.49 | 0.00 | 1.15 | 0.00 | 0.00 | 0.00 | **2.64** |
| RANGE_FADE | filtered | 46 | 42.31 | 18.20 | 0.00 | 0.00 | 0.00 | 11.74 | 0.00 | 0.00 | 0.00 | **29.94** |
| RANGE_FADE | kept | 49 | 67.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 499 | 53.92 | 0.00 | 0.00 | 1.16 | 0.00 | 7.77 | 0.12 | 0.00 | 0.08 | **9.13** |
| SR_FLIP_RETEST | kept | 993 | 69.58 | 0.00 | 0.00 | 0.45 | 0.00 | 0.30 | 0.00 | 0.00 | 0.00 | **0.75** |
| TREND_PULLBACK_EMA | kept | 2 | 78.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 7 | 21.60 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=248 (7.0%) | WOULD_LOSE=1464 | WOULD_EXPIRE=1834 | pending (awaiting window)=1454

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_edge:RANGE_FADE | 965 | 0.0% | 1153.6 | 0.0 | +1.20 | **KEEP** |
| context_floor:DIVERGENCE_CONTINUATION | 87 | 0.0% | 78.0 | 0.0 | +0.90 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 534 | 0.0% | 147.7 | 0.0 | +0.28 | **KEEP** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 24 | 16.7% | 12.8 | 18.0 | -0.22 | **DROP** |
| context_floor:QUIET_COMPRESSION_BREAK | 60 | 0.0% | 9.4 | 0.0 | +0.16 | **KEEP** |
| dispatch_staleness_v2 | 309 | 13.9% | 18.1 | 51.1 | -0.11 | **TUNE** |
| level_still_in_play | 644 | 11.3% | 53.4 | 50.7 | +0.00 | **TUNE** |
| min_confidence | 367 | 6.3% | 315.8 | 24.4 | +0.79 | **KEEP** |
| quiet_scalp_block | 485 | 15.1% | 190.9 | 85.5 | +0.22 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 8 | 37.5% | 1.4 | 2.1 | -0.09 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 50 | 58.0% | 22.2 | 49.6 | -0.55 | **DROP** |
| shadow_unit:SHADOW_RANGE_FADE | 13 | 0.0% | 15.4 | 0.0 | +1.18 | **INSUFFICIENT_SAMPLE** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 60397 across 20 strategies; 1375 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 14279 | 47/14232/0 | 59% | +0.16 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.13R) |
| FAILED_AUCTION_RECLAIM | 10937 | 22/10915/0 | 50% | +0.02 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 9544 | 2/9542/0 | 43% | -0.17 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.14R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (-1.30R) |
| DIVERGENCE_CONTINUATION | 5427 | 6/5421/0 | 47% | -0.04 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.19R) |
| QUIET_COMPRESSION_BREAK | 4082 | 0/4082/0 | 48% | +0.02 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MEAN_REVERT | 2954 | 0/2954/0 | 82% | +0.63 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_MEAN_REVERT | 2705 | 0/0/2705 | 37% | -0.08 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.82R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_RANGE_FADE | 2337 | 0/0/2337 | 34% | +0.08 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.30R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 2057 | 3/2054/0 | 39% | -0.23 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-1.07R) |
| RANGE_FADE | 1602 | 0/1602/0 | 4% | -0.94 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.21R) |
| SHADOW_FUNDING_FADE | 1460 | 0/0/1460 | 35% | -0.37 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 1041 | 10/1031/0 | 38% | -0.08 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| TREND_PULLBACK_EMA | 625 | 0/625/0 | 41% | -0.21 | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.36R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| WHALE_MOMENTUM | 446 | 0/446/0 | 51% | -0.12 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 239 | 5/234/0 | 54% | +0.31 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 236 | 0/236/0 | 42% | +0.12 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 217 | 16/201/0 | 19% | -0.63 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 196 | 0/0/196 | 46% | -0.12 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.03R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 11 | 0/11/0 | 36% | -0.62 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +1.95R (n=34, STRONG)
- **Weakest cells**: `SR_FLIP_RETEST @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.30R (n=22, NEGATIVE); `SR_FLIP_RETEST @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` -1.30R (n=22, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.28R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 29 | 45% / +0.19R | 29 | 34% / -0.15R | -0.34 | **FIXED** |
| TREND_PULLBACK_EMA | 23 | 52% / -0.16R | 23 | 57% / +0.05R | +0.21 | **ATR** |
| MOVER_AVWAP_SCALP | 46 | 41% / -0.09R | 46 | 52% / +0.05R | +0.14 | **ATR** |
| MEAN_REVERT | 211 | 57% / +0.11R | 211 | 55% / +0.23R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 29 | 38% / -0.18R | 29 | 34% / -0.29R | -0.12 | **FIXED** |
| SR_FLIP_RETEST | 1297 | 46% / -0.08R | 1297 | 50% / -0.03R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 215 | 48% / -0.07R | 215 | 55% / -0.03R | +0.04 | **ATR** |
| MOVER_TREND_PULLBACK | 1305 | 61% / +0.13R | 1305 | 64% / +0.10R | -0.03 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 590 | 45% / -0.01R | 590 | 44% / -0.03R | -0.02 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 1284 | 50% / -0.01R | 1284 | 49% / +0.00R | +0.01 | **ATR** |
| DIVERGENCE_CONTINUATION | 280 | 49% / -0.02R | 280 | 54% / -0.01R | +0.01 | **ATR** |
| RANGE_FADE | 100 | 3% / -0.99R | 100 | 3% / -0.99R | -0.00 | **FIXED** |
| BREAKDOWN_SHORT | 8 | 25% / -0.27R | 8 | 25% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 3 | 0% / -1.05R | 3 | 67% / -0.00R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 2 | 50% / -0.02R | 2 | 50% / -0.33R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 3 | 67% / +0.16R | 3 | 67% / +0.06R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 81 | 33% | -0.05R | 32 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 36 | 53% | +0.04R | 27 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 2 | 0% | -0.15R | 2 | MEASURING |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 18 · alerting: **2** · boot grace active: False
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=-0.37R (bound 0.3) (streak 198/6) (sustained 198 cycles)
- **ALERT** `mean_revert_emission` — 607 detections since last emission (emitted_total=17) — check gate rejections (streak 6/6) (sustained 6 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=13 fanouts=13 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 65418.60 | 0 |
| candle_coverage | ok | 93/105 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +39 / upstream +38 | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=-0.37R (bound 0.3) (streak 198/6) | 198 |
| emission_controller | ok | last cycle 1566s ago; live_overrides=14 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +2 / upstream +58 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 607 detections since last emission (emitted_total=17) — check gate rejections (streak 6/6) | 6 |
| mean_revert_path | ok | output +90 / upstream +58 | 0 |
| range_fade_emission | ok | emitted_total=3 context_blocked=3037 | 0 |
| range_fade_path | ok | output +70 / upstream +58 | 0 |
| shadow_units | ok | last shadow stamp 12m ago | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +178 / upstream +58 | 0 |
| suppression_audit | ok | output +58 / upstream +38 | 0 |
| tuned_variants | ok | seen=1450 stamped=87 skipped=1360 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `60269`
- `Path funnel` emissions: `23`
- `Regime distribution` emissions: `23`
- `QUIET_SCALP_BLOCK` events: `591`
- `confidence_gate` events: `4860`
- `free_channel_post` events: `3`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| signal_close | 2 |
| regime_shift | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[present=144758] state[populated=144758] buckets[many=144758] sources[none] quality[none]
- funding_rate: presence[absent=15589, present=129169] state[empty=15589, populated=129169] buckets[few=129169, none=15589] sources[none] quality[none]
- liquidation_clusters: presence[absent=82384, present=62374] state[empty=82384, populated=62374] buckets[few=50181, none=82384, some=12193] sources[none] quality[none]
- oi_snapshot: presence[absent=15589, present=129169] state[empty=15589, populated=129169] buckets[many=129169, none=15589] sources[none] quality[none]
- order_book: presence[absent=35208, present=109550] state[populated=109550, unavailable=35208] buckets[few=109550, none=35208] sources[book_ticker=109550, unavailable=35208] quality[none=35208, top_of_book_only=109550]
- orderblocks: presence[absent=144758] state[empty=144758] buckets[none=144758] sources[not_implemented=144758] quality[none]
- recent_ticks: presence[present=144758] state[populated=144758] buckets[many=144758] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.421531558036804` sec
- Median create→first breach: `2661.321725010872` sec
- Median create→terminal: `2663.723902463913` sec
- Median first breach→terminal: `2.1516915559768677` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4484.044064044952 | 4487.793117046356 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | -0.4667 | 2948.437092065811 | 2949.2663559913635 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.5552 | 1149.6313581466675 | 1531.760908126831 |
| MOVER_TREND_PULLBACK | 6 | 6 | 0.0 | 33.3 | 0.0 | 0.0 | -0.7794 | 3530.5306210517883 | 3530.968395471573 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4363 | 6286.339308977127 | 6310.499457120895 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 5897 | 42 | 1884 | 0.0 | 0.0 | None | None | 4013 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1011 | 2 | 1007 | 0.0 | 0.0 | None | None | 4 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-180`
- Gating Δ: `-164946`
- No-generation Δ: `-2226628`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.8268, "current_avg_pnl": -0.4667, "current_win_rate": 33.3, "previous_avg_pnl": -1.2935, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -5.0775, "current_avg_pnl": -0.5552, "current_win_rate": 0.0, "previous_avg_pnl": 4.5223, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.6879, "current_avg_pnl": -0.7794, "current_win_rate": 0.0, "previous_avg_pnl": -1.4673, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -12, "geometry_changed_delta": 0, "geometry_preserved_delta": -276, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -122, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **DIVERGENCE_CONTINUATION**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
