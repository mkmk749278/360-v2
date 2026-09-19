# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1201` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 49 | 49 | 48 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10209 | 10209 | 9928 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 75171 | 75184 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 56002 | 56002 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 55835 | 53659 | 2331 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 56013 | 55681 | 349 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 60428 | 60351 | 85 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 48530 | 48539 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 56032 | 56036 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 56042 | 54274 | 2386 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 84316 | 88628 | 1017 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 75190 | 61270 | 23018 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 60143 | 60143 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 56004 | 56005 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 55825 | 55745 | 89 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 56663 | 54585 | 2600 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 55532 | 55784 | 31 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 43856 | 40422 | 3628 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 44051 | 43752 | 339 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 75141 | 75124 | 43 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 48540 | 48548 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1920 | 1920 | 1859 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 610 | 610 | 564 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 24444 | 24444 | 24195 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8358 | 8358 | 8179 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3340 | 3340 | 3049 | 11 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 83270 | 83270 | 80471 | 133 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 31 | 31 | 31 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 652 | 652 | 616 | 2 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 8174 | 8174 | 8123 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 186 | 186 | 163 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2733 | 2733 | 2712 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 223 | 223 | 223 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=75184): breakout_not_found=44956, basic_filters_failed=22845, move_not_fresh=4056, breakout_stale=2250, retest_proximity_failed=722, volume_spike_missing=237, insufficient_candles=99, missing_fvg_or_orderblock=11, move_exhausted=8
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=56002): cls_disabled_merged_into_lsr=56002
- **EVAL::DIVERGENCE_CONTINUATION** (total=53659): cvd_divergence_failed=32446, basic_filters_failed=13350, h1_trend_not_aligned=4632, ema_alignment_reject=2572, retest_proximity_failed=424, missing_fvg_or_orderblock=232, cvd_insufficient=3
- **EVAL::FAILED_AUCTION_RECLAIM** (total=55681): auction_not_detected=38124, basic_filters_failed=13097, regime_blocked=1852, reclaim_hold_failed=1795, tail_too_small=811, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=60351): funding_not_extreme=43381, basic_filters_failed=15141, ema_alignment_reject=814, missing_funding_rate=633, rsi_reject=222, cvd_divergence_failed=70, momentum_reject=70, missing_fvg_or_orderblock=15, insufficient_candles=5
- **EVAL::LIQUIDATION_REVERSAL** (total=48539): cascade_threshold_not_met=32713, basic_filters_failed=15267, cvd_divergence_failed=246, rsi_reject=209, insufficient_candles=64, missing_fvg_or_orderblock=36, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=56036): no_ma_cross=42191, basic_filters_failed=13361, ma_cross_cooldown=450, ma_cross_htf_misaligned=34
- **EVAL::MEAN_REVERT** (total=54274): no_extension=44248, basic_filters_failed=10026
- **EVAL::MOVER_AVWAP_SCALP** (total=88628): no_avwap_tag=42364, basic_filters_failed=22571, no_mover_leg=9713, avwap_slope_against=7704, avwap_reclaim_no_volume=3177, no_avwap_reclaim=2245, insufficient_candles=816, anchor_too_recent=38
- **EVAL::MOVER_TREND_PULLBACK** (total=61270): basic_filters_failed=22529, no_reclaim=21754, mover_run_too_small=13099, no_pullback_tag=3072, insufficient_candles=816
- **EVAL::OPENING_RANGE_BREAKOUT** (total=60143): feature_disabled=60143
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=56005): regime_blocked=41868, breakout_not_found=10183, basic_filters_failed=2899, adx_reject=1015, ema_alignment_reject=39, rsi_reject=1
- **EVAL::QUIET_COMPRESSION_BREAK** (total=55745): compression_not_detected=27273, regime_blocked=15943, basic_filters_failed=10189, breakout_not_detected=2042, volume_confirmation_failed=251, rsi_reject=39, missing_fvg_or_orderblock=8
- **EVAL::RANGE_FADE** (total=54585): no_range_edge=44556, basic_filters_failed=10029
- **EVAL::SR_FLIP_RETEST** (total=55784): flip_close_not_confirmed=38004, basic_filters_failed=13082, regime_blocked=1844, long_break_volume_thin=1478, retest_out_of_zone=496, h1_break_not_confirmed=451, reclaim_hold_failed=205, long_acceptance_not_held=103, wick_quality_failed=65, ema_alignment_reject=41, missing_fvg_or_orderblock=8, whipsaw_flip=7
- **EVAL::STANDARD** (total=40422): momentum_reject=10944, adx_reject=9648, basic_filters_failed=7273, macd_reject=4726, sweeps_not_detected=4609, ema_alignment_reject=2293, htf_poi_unanchored=779, rsi_reject=81, invalid_sl_geometry=69
- **EVAL::TREND_PULLBACK** (total=43752): h1_pullback_not_confirmed=16822, basic_filters_failed=5793, ema_alignment_reject=5757, h1_trend_not_aligned=5470, ema_not_tested_prev=3031, no_ema_reclaim_close=2761, body_conviction_fail=1665, rsi_reject=1413, prev_already_above_emas=582, no_prev_high_break=308, momentum_flat=43, prev_already_below_emas=35, no_prev_low_break=25, missing_fvg_or_orderblock=23, ema21_not_tagged=17, momentum_reject=7
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=75124): breakout_not_found=34862, basic_filters_failed=22845, move_not_fresh=10661, breakout_stale=4552, retest_proximity_failed=1624, volume_spike_missing=455, insufficient_candles=99, missing_fvg_or_orderblock=26
- **EVAL::WHALE_MOMENTUM** (total=48548): momentum_reject=30940, recent_ticks_insufficient=10418, basic_filters_failed=7190

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=155): setup_compat:regime_VOLATILE_UNSUITABLE=86, setup_compat:regime_BREAKOUT_EXPANSION=62, execution:overextended=7
- **FAILED_AUCTION_RECLAIM** (total=579): execution:overextended=327, setup_compat:regime_STRONG_TREND=252
- **FUNDING_EXTREME_SIGNAL** (total=478): execution:trigger_not_confirmed=478
- **LIQUIDATION_REVERSAL** (total=7): execution:trigger_not_confirmed=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=6140): execution:overextended=2886, execution:trigger_not_confirmed=2251, setup_compat:regime_STRONG_TREND=1003
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_DIRTY_RANGE=3, execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=3071): setup_compat:regime_STRONG_TREND=1618, execution:overextended=767, setup_compat:regime_WEAK_TREND=667, entry_quality=19
- **MOVER_AVWAP_SCALP** (total=1655): execution:overextended=1251, execution:trigger_not_confirmed=385, entry_quality=19
- **MOVER_TREND_PULLBACK** (total=26223): execution:trigger_not_confirmed=15820, execution:overextended=10129, entry_quality=274
- **POST_DISPLACEMENT_CONTINUATION** (total=10): execution:overextended=10
- **QUIET_COMPRESSION_BREAK** (total=22): execution:trigger_not_confirmed=22
- **RANGE_FADE** (total=2632): setup_compat:regime_STRONG_TREND=1071, setup_compat:regime_WEAK_TREND=905, execution:overextended=451, setup_compat:regime_VOLATILE_UNSUITABLE=201, setup_compat:regime_BREAKOUT_EXPANSION=4
- **TREND_PULLBACK_EMA** (total=2366): setup_compat:regime_CLEAN_RANGE=1211, setup_compat:regime_DIRTY_RANGE=1031, setup_compat:regime_VOLATILE_UNSUITABLE=113, entry_quality=11
- **VOLUME_SURGE_BREAKOUT** (total=44): execution:overextended=44

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 241534 | 53.8% |
| TRENDING_UP | 82624 | 18.4% |
| QUIET | 61622 | 13.7% |
| TRENDING_DOWN | 41978 | 9.4% |
| VOLATILE | 21073 | 4.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **31**
- Average confidence gap to threshold: **14.54** (samples=31) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: FILUSDT=6, HBARUSDT=6, SOLUSDT=6, DOTUSDT=5, XLMUSDT=2, SUIUSDT=2, 1000SHIBUSDT=1, XRPUSDT=1, DOGEUSDT=1, HYPEUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 69 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 12 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 18 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 23 |
| MEAN_REVERT | filtered | min_confidence | 19 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 167 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 6 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 22 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 489 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 10 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 608 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 17 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 14 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 2 |
| SR_FLIP_RETEST | filtered | min_confidence | 18 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 8 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 79.70 | 65.00 | -14.70 | 16.50 | 18.90 | 20.00 | 5.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 76 | 60.07 | 64.74 | 4.67 | 21.47 | 19.89 | 17.98 | 0.72 | 6.87 |
| DIVERGENCE_CONTINUATION | kept | 12 | 75.30 | 65.00 | -10.30 | 21.00 | 19.27 | 18.65 | 0.42 | 2.90 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 64.30 | 65.00 | 0.70 | 21.20 | 13.60 | 17.00 | 4.00 | 12.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 18 | 53.73 | 64.33 | 10.60 | 19.17 | 19.33 | 16.24 | 0.67 | 12.23 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 23 | 69.05 | 65.00 | -4.05 | 19.96 | 19.36 | 18.83 | 2.57 | 0.47 |
| MEAN_REVERT | filtered | 19 | 63.70 | 65.00 | 1.30 | 21.02 | 14.00 | 20.00 | 0.00 | 12.00 |
| MEAN_REVERT | kept | 1 | 69.70 | 65.00 | -4.70 | 19.50 | 14.00 | 20.00 | 0.00 | 12.00 |
| MOVER_AVWAP_SCALP | filtered | 173 | 53.23 | 63.06 | 9.83 | 21.25 | 15.53 | 15.80 | 3.38 | 23.86 |
| MOVER_AVWAP_SCALP | kept | 22 | 75.13 | 65.00 | -10.13 | 21.00 | 15.29 | 15.80 | 3.91 | 10.00 |
| MOVER_TREND_PULLBACK | filtered | 499 | 56.00 | 64.50 | 8.50 | 20.29 | 18.06 | 15.80 | 3.80 | 19.56 |
| MOVER_TREND_PULLBACK | kept | 608 | 76.37 | 65.00 | -11.37 | 20.07 | 18.49 | 15.80 | 4.09 | 2.35 |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 51.40 | 63.45 | 12.05 | 21.53 | 18.26 | 20.00 | 0.00 | 18.10 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 66.70 | 65.00 | -1.70 | 20.70 | 19.95 | 20.00 | 0.00 | 11.40 |
| SR_FLIP_RETEST | filtered | 18 | 51.36 | 62.33 | 10.97 | 20.02 | 20.00 | 17.08 | 2.50 | 18.89 |
| TREND_PULLBACK_EMA | filtered | 3 | 62.90 | 65.00 | 2.10 | 20.07 | 20.00 | 18.30 | 6.00 | 23.10 |
| TREND_PULLBACK_EMA | kept | 8 | 81.75 | 65.00 | -16.75 | 20.36 | 19.89 | 18.88 | 5.00 | 0.40 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 79.70 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 3.70 | 5.00 |
| DIVERGENCE_CONTINUATION | filtered | 76 | 60.07 | 22.05 | 13.92 | 5.33 | 11.75 | 4.59 | 8.57 | 0.72 |
| DIVERGENCE_CONTINUATION | kept | 12 | 75.30 | 24.33 | 18.00 | 3.75 | 15.00 | 7.12 | 9.58 | 0.42 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 64.30 | 17.00 | 18.00 | 6.00 | 12.00 | 10.00 | 9.30 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 18 | 53.73 | 24.78 | 14.00 | 3.00 | 14.00 | 5.00 | 4.52 | 0.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 23 | 69.05 | 24.91 | 14.00 | 6.13 | 12.65 | 5.33 | 3.93 | 2.57 |
| MEAN_REVERT | filtered | 19 | 63.70 | 17.00 | 18.00 | 15.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 1 | 69.70 | 25.00 | 18.00 | 15.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 173 | 53.23 | 19.28 | 18.00 | 11.15 | 14.87 | 6.29 | 4.13 | 3.38 |
| MOVER_AVWAP_SCALP | kept | 22 | 75.13 | 22.45 | 18.00 | 13.09 | 14.00 | 6.50 | 7.16 | 3.91 |
| MOVER_TREND_PULLBACK | filtered | 499 | 56.00 | 18.66 | 18.00 | 7.97 | 12.61 | 6.35 | 8.20 | 3.80 |
| MOVER_TREND_PULLBACK | kept | 608 | 76.37 | 20.31 | 18.00 | 7.64 | 13.12 | 6.78 | 8.79 | 4.09 |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 51.40 | 18.81 | 15.81 | 9.00 | 14.00 | 8.10 | 3.79 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 66.70 | 17.00 | 18.00 | 15.00 | 14.00 | 6.75 | 7.35 | 0.00 |
| SR_FLIP_RETEST | filtered | 18 | 51.36 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 2.74 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 3 | 62.90 | 25.00 | 18.00 | 9.00 | 14.00 | 5.00 | 9.00 | 6.00 |
| TREND_PULLBACK_EMA | kept | 8 | 81.75 | 22.00 | 18.00 | 7.50 | 14.38 | 6.88 | 9.38 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 79.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 76 | 60.07 | 0.00 | 0.00 | 0.00 | 0.00 | 1.71 | 0.00 | 0.00 | 0.00 | **1.71** |
| DIVERGENCE_CONTINUATION | kept | 12 | 75.30 | 0.00 | 0.00 | 0.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.40** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 64.30 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 18 | 53.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 23 | 69.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 19 | 63.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 1 | 69.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_AVWAP_SCALP | filtered | 173 | 53.23 | 0.00 | 0.00 | 0.00 | 0.00 | 5.86 | 0.00 | 0.00 | 5.22 | **11.08** |
| MOVER_AVWAP_SCALP | kept | 22 | 75.13 | 4.77 | 0.00 | 0.36 | 0.00 | 1.15 | 0.91 | 0.00 | 1.12 | **8.31** |
| MOVER_TREND_PULLBACK | filtered | 499 | 56.00 | 0.06 | 0.00 | 0.38 | 0.00 | 0.50 | 0.18 | 0.00 | 0.11 | **1.23** |
| MOVER_TREND_PULLBACK | kept | 608 | 76.37 | 0.08 | 0.00 | 0.09 | 0.00 | 0.04 | 0.20 | 0.00 | 0.31 | **0.72** |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 51.40 | 0.00 | 0.00 | 5.32 | 0.00 | 0.00 | 0.58 | 0.00 | 7.82 | **13.72** |
| QUIET_COMPRESSION_BREAK | kept | 2 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | 0.00 | 5.40 | **14.40** |
| SR_FLIP_RETEST | filtered | 18 | 51.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| TREND_PULLBACK_EMA | filtered | 3 | 62.90 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| TREND_PULLBACK_EMA | kept | 8 | 81.75 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | **1.75** |

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
- Outcomes recorded: **103214 held of 263341 seen** across 21 strategies; 2362 cells past the sample floor; **1042 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 36792 | 565/36227/0 | 44% | -0.14 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.23R) | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.15R) |
| MOVER_AVWAP_SCALP | 12734 | 168/12566/0 | 41% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 8014 | 96/7918/0 | 41% | -0.19 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6418 | 32/6386/0 | 51% | -0.00 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5528 | 0/0/5528 | 42% | -0.11 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.83R) |
| TREND_PULLBACK_EMA | 5150 | 24/5126/0 | 45% | -0.15 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4703 | 0/0/4703 | 37% | -0.10 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.66R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.16R) |
| QUIET_COMPRESSION_BREAK | 4335 | 266/4069/0 | 43% | -0.16 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4310 | 0/0/4310 | 35% | -0.39 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.01R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3182 | 59/3123/0 | 36% | -0.38 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2133 | 20/2113/0 | 48% | -0.15 | LONDON/MARKDOWN/EXPANDED/BTC_RISING (+1.23R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1797 | 2/1795/0 | 34% | -0.40 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1600 | 0/1600/0 | 42% | +0.01 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1058 | 10/1048/0 | 48% | -0.20 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.22R) |
| SHADOW_CASCADE_REVERSAL | 748 | 0/0/748 | 53% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.16R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.47R) |
| RANGE_FADE | 717 | 0/717/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 354 | 31/323/0 | 40% | -0.16 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 58 | 6/52/0 | 41% | -0.11 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 142 | 28% / -0.54R | 142 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 411 | 45% / -0.20R | 411 | 55% / -0.04R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 991 | 44% / -0.19R | 991 | 50% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 121 | 48% / -0.27R | 121 | 50% / -0.18R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5598 | 50% / -0.09R | 5598 | 55% / -0.01R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 707 | 43% / -0.17R | 707 | 45% / -0.10R | +0.08 | **ATR** |
| BREAKDOWN_SHORT | 31 | 32% / -0.20R | 31 | 35% / -0.13R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 611 | 49% / -0.21R | 611 | 55% / -0.15R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 94 | 39% / -0.09R | 94 | 47% / -0.06R | +0.03 | **ATR** |
| RANGE_FADE | 35 | 40% / -0.19R | 35 | 43% / -0.22R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 607 | 51% / -0.06R | 607 | 56% / -0.04R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 738 | 45% / -0.16R | 738 | 45% / -0.17R | -0.01 | **FIXED** |
| MEAN_REVERT | 146 | 51% / -0.10R | 146 | 49% / -0.10R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8154 | 29% | -0.18R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 991 | 48% | -0.08R | 190 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 60 | 50% | -0.06R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 712 | 36% / -0.09R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7221 | 37% / -0.14R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1310 | 35% / -0.08R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 562 | 36% / -0.10R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 684 | 41% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 555 | 38% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 601 | 42% / -0.18R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 127 | 28% / -0.38R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 182 | 31% / -0.57R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 118 | 53% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 52 | 37% / -0.17R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 27 | 37% / +0.17R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 123 | 35% / -0.41R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 27 | 15% / -0.50R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **6** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×335]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 519/6) (sustained 519 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 8/6) (sustained 8 cycles)
- **ALERT** `sar_live_arms` — 2 live SAR arms could not be advanced this cycle (0 no candles, 2 bars behind; 64 current): ZROUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 14/12) (sustained 14 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.69R (bound 0.3) (streak 519/6) (sustained 519 cycles)
- **ALERT** `tuned_variants` — 179 non-stamps — atr_arm_uncomputable=179 (seen=3552 stamped=491 skipped=2882) (streak 465/6) (sustained 465 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 519/3) (sustained 519 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 158715262 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 519/3) | 519 |
| ai_governor_live_arms | ok | 32 arms current, none stalled; covering 504/504 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 2 live ATR-trail arms could not be advanced this cycle (0 no candles, 2 bars behind; 64 current): ZROUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/12) | 1 |
| auto_dispatch | ok | 60 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=69, mode:off=51. No user is on live. | 0 |
| btc_reference | ok | BTC ref 80949.10 | 0 |
| candle_coverage | ok | 95/95 symbols with ≥20 15m candles, 95/95 updated within 45m [fresh=95; 76 Tier-1 futures + 20 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 469 dup bars, 0 undedupable; ws 0 out-of-order, 239 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +46 but output +0 (streak 2/72) | 2 |
| dark_atr_trail_arms | ok | no open arms; covering 1214/1231 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 7 of 78 open dark rows are not being advanced (worst: BULLAUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 3/120) | 3 |
| dark_sar_arms | ok | no open arms; covering 1206/1223 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 28764219 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.69R (bound 0.3) (streak 519/6) | 519 |
| emission_controller | ok | last cycle 663s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×335]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 519/6) | 519 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 8/6) | 8 |
| footprint_bars | ok | 5204 sealed bars over 44 symbols; 1718 incomplete, 2 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +0 / upstream +0 | 0 |
| indicator_cache_key | ok | 202250 frozen value(s) avoided; 880444 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.16R over n=2113 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +0 / upstream +0 | 0 |
| mover_admission_metadata | ok | 905 symbols known, 199 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 20 held, 20 with scan counts, 17 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1554718 evicted (sampled: execution:trigger_not_confirmed 400/572220, execution:overextended 400/513809, setup_compat:regime_STRONG_TREND 400/228947) | 0 |
| price_action_lane | ok | 1041197 evaluated, 1274 emitted; layer1 1274 stamped / 0 blind; cooldown=135835, delta_opposed=85368, no_footprint=427557, no_levels=249, no_opposing_target=4323, no_sweep=313130, rr_below_floor=73461 | 0 |
| promoted_pair_integrity | ok | 20/20 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=717 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +0 / upstream +0 | 0 |
| sar_alignment_crosscheck | ok | 251/15223 disagreed (1.6%) | 0 |
| sar_exit_shadow | ok | output +0 / upstream +0 | 0 |
| sar_hold_arm | ok | 1822 held arms settled, 178 unscored, 66 still walking (65 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 9/32 unfetchable (28%); top cause: gap or duplicate bar in the 15m window; symbols: EVAAUSDT, STGUSDT | 0 |
| sar_live_arms | violating | 2 live SAR arms could not be advanced this cycle (0 no candles, 2 bars behind; 64 current): ZROUSDT. Their stops are frozen, so the mechanism is not being measured on those trades. (streak 14/12) | 14 |
| sar_refresh_budget | ok | 23 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 22 still mid-window | 0 |
| scan_cycle | ok | last 17.75s, worst 120.46s over 11944 lifetime cycles; lifetime 55 over 60s, 1 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 11.5s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 542768 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 18m ago | 0 |
| snapshot_writer | ok | last cycle 6s ago (0.58s to run, worst 68.28s), 678 overrun(s) of 10239 cycles, TTL 900s; slowest data_intake=0.2s, dark_promotion=0.08s, signals=0.06s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +46 / upstream +0 | 0 |
| structural_snap | ok | 5260/5260 measured, 21 blind, 0 levels moved (refusals: redetect_cooldown=376) | 0 |
| structural_veto_lane | ok | 780 stamped; 0 with no readable level book, 8 with clear air ahead, 565 would-reject, 0 enforced | 0 |
| suppression_audit | violating | upstream +46 but output +0 (streak 2/72) | 2 |
| tuned_variants | violating | 179 non-stamps — atr_arm_uncomputable=179 (seen=3552 stamped=491 skipped=2882) (streak 465/6) | 465 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 4 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2243720`
- `Path funnel` emissions: `47`
- `Regime distribution` emissions: `47`
- `QUIET_SCALP_BLOCK` events: `31`
- `confidence_gate` events: `1515`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **9**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 4 | 4516 | 5679 | 6853 | 0 |
| futures_depth | 3 | 7680 | 7680 | 8104 | 0 |
| futures_mover | 2 | 3098 | 3098 | 9414 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=371712] state[populated=371712] buckets[few=11, many=371662, some=39] sources[none] quality[none]
- funding_rate: presence[absent=61453, present=310259] state[empty=61453, populated=310259] buckets[few=310259, none=61453] sources[none] quality[none]
- liquidation_clusters: presence[absent=188677, present=183035] state[empty=188677, populated=183035] buckets[few=143173, none=188677, some=39862] sources[none] quality[none]
- oi_snapshot: presence[absent=61452, present=310260] state[empty=61452, populated=310260] buckets[few=139, many=308679, none=61452, some=1442] sources[none] quality[none]
- order_book: presence[absent=132517, present=239195] state[populated=239195, unavailable=132517] buckets[few=239195, none=132517] sources[book_ticker=239195, unavailable=132517] quality[none=132517, top_of_book_only=239195]
- orderblocks: presence[absent=371712] state[empty=371712] buckets[none=371712] sources[measured_dark=371675, not_implemented=37] quality[none]
- recent_ticks: presence[present=371712] state[populated=371712] buckets[many=371712] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.2723469734191895` sec
- Median create→first breach: `7253.415802001953` sec
- Median create→terminal: `7253.415828943253` sec
- Median first breach→terminal: `5.507469177246094e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 1.328826530612245 | 1.5591179653679645 | 0.8522937713046179 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.1992302806112998 | 1.3430442335961488 | 0.892919421872077 | 0 | 1 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.3580101230253505 | 2.4894188695323427 | 0.9553605319167302 | 2 | 2 |
| MOVER_TREND_PULLBACK | 15 | 15 | 3.4272327279343684 | 2.551861625615757 | 1.5666179045053132 | 12 | 3 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.0306251143398768 | 1.167161011474613 | 0.8841149638256416 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3288 | 4004.575047969818 | 4004.575164794922 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1992 | 19880.633625984192 | 19880.633653879166 |
| MOVER_AVWAP_SCALP | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | -1.3549 | 5369.100010514259 | 5369.100061535835 |
| MOVER_TREND_PULLBACK | 15 | 15 | 40.0 | 20.0 | 40.0 | 0.0 | 1.0357 | 6864.8511600494385 | 6865.133728027344 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 25.0 | 50.0 | 25.0 | 0.0 | 0.4466 | 43531.50671553612 | 43531.72643494606 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 186 | 0 | 163 | 0.0 | 0.0 | None | None | 23 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2733 | 5 | 2712 | 0.0 | 0.0 | None | None | 21 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-39`
- Gating Δ: `2214`
- No-generation Δ: `-627585`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1764, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.1764, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.7922, "current_avg_pnl": -1.1992, "current_win_rate": 0.0, "previous_avg_pnl": -0.407, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.2086, "current_avg_pnl": -1.3549, "current_win_rate": 25.0, "previous_avg_pnl": -0.1463, "previous_win_rate": 25.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.0704, "current_avg_pnl": 1.0357, "current_win_rate": 40.0, "previous_avg_pnl": 1.1061, "previous_win_rate": 53.8, "win_rate_delta": -13.8}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.7806, "current_avg_pnl": 0.4466, "current_win_rate": 25.0, "previous_avg_pnl": -0.334, "previous_win_rate": 22.2, "win_rate_delta": 2.8}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": -3, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -6, "geometry_changed_delta": 0, "geometry_preserved_delta": -112, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MEAN_REVERT**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
