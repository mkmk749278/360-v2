# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `7998` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 62 | 62 | 61 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10773 | 10773 | 9663 | 6 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 96894 | 96892 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 82561 | 82568 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 82335 | 80163 | 2385 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 82585 | 82277 | 354 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 83785 | 83519 | 291 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 78447 | 78436 | 17 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 82637 | 82661 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 82679 | 80559 | 2791 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 99995 | 102743 | 612 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::MOVER_TREND_PULLBACK | 96909 | 89454 | 10518 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 83606 | 83615 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 82572 | 82585 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 82303 | 81944 | 389 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 83352 | 81514 | 2302 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 82106 | 82228 | 41 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 77078 | 74499 | 2703 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 77205 | 76753 | 493 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 96872 | 96864 | 27 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 78455 | 78474 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1357 | 1357 | 1194 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 848 | 848 | 118 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 42 | 42 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 11663 | 11663 | 11271 | 16 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 18 | 18 | 6 | 5 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8689 | 8689 | 6503 | 21 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1633 | 1633 | 148 | 42 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 31134 | 31134 | 17878 | 311 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 2 | 2 | 1 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1917 | 1917 | 1074 | 63 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 6215 | 6215 | 5742 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 137 | 137 | 112 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2385 | 2385 | 1892 | 25 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 107 | 107 | 12 | 5 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=96892): breakout_not_found=47699, basic_filters_failed=34830, move_not_fresh=9247, breakout_stale=3402, retest_proximity_failed=1383, volume_spike_missing=210, insufficient_candles=72, ema_alignment_reject=41, move_exhausted=5, missing_fvg_or_orderblock=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=82568): cls_disabled_merged_into_lsr=82568
- **EVAL::DIVERGENCE_CONTINUATION** (total=80163): basic_filters_failed=29572, cvd_divergence_failed=24706, h1_trend_not_aligned=18347, ema_alignment_reject=5551, retest_proximity_failed=1248, regime_blocked=391, missing_fvg_or_orderblock=346, cvd_insufficient=2
- **EVAL::FAILED_AUCTION_RECLAIM** (total=82277): auction_not_detected=47451, basic_filters_failed=28120, regime_blocked=3976, reclaim_hold_failed=1558, tail_too_small=1143, rsi_reject=29
- **EVAL::FUNDING_EXTREME** (total=83519): funding_not_extreme=49591, basic_filters_failed=29329, missing_funding_rate=2093, ema_alignment_reject=1597, rsi_reject=539, momentum_reject=182, cvd_divergence_failed=152, missing_fvg_or_orderblock=26, insufficient_candles=10
- **EVAL::LIQUIDATION_REVERSAL** (total=78436): cascade_threshold_not_met=47510, basic_filters_failed=29819, cvd_divergence_failed=549, rsi_reject=454, insufficient_candles=51, missing_fvg_or_orderblock=35, volume_spike_missing=18
- **EVAL::MA_CROSS_TREND_SHIFT** (total=82661): no_ma_cross=51460, basic_filters_failed=29601, ma_cross_cooldown=944, ma_cross_htf_misaligned=558, ma_cross_htf_unconfirmed=98
- **EVAL::MEAN_REVERT** (total=80559): no_extension=63463, basic_filters_failed=16721, insufficient_candles=375
- **EVAL::MOVER_AVWAP_SCALP** (total=102744): basic_filters_failed=34607, no_mover_leg=31897, no_avwap_tag=27045, avwap_slope_against=4862, avwap_reclaim_no_volume=1970, no_avwap_reclaim=1647, insufficient_candles=691, anchor_too_recent=25
- **EVAL::MOVER_TREND_PULLBACK** (total=89454): mover_run_too_small=36926, basic_filters_failed=34515, no_reclaim=15166, no_pullback_tag=2117, insufficient_candles=730
- **EVAL::OPENING_RANGE_BREAKOUT** (total=83615): feature_disabled=83615
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=82585): regime_blocked=59595, breakout_not_found=13469, basic_filters_failed=6980, adx_reject=2510, ema_alignment_reject=31
- **EVAL::QUIET_COMPRESSION_BREAK** (total=81944): regime_blocked=26901, compression_not_detected=21362, basic_filters_failed=21125, breakout_not_detected=11284, volume_confirmation_failed=1044, macd_reject=123, rsi_reject=101, missing_fvg_or_orderblock=4
- **EVAL::RANGE_FADE** (total=81514): no_range_edge=64237, basic_filters_failed=16675, insufficient_candles=602
- **EVAL::SR_FLIP_RETEST** (total=82228): flip_close_not_confirmed=46739, basic_filters_failed=27995, regime_blocked=3966, h1_break_not_confirmed=1154, long_break_volume_thin=1069, retest_out_of_zone=879, insufficient_candles=141, reclaim_hold_failed=120, whipsaw_flip=71, long_acceptance_not_held=46, wick_quality_failed=33, ema_alignment_reject=13, missing_fvg_or_orderblock=2
- **EVAL::STANDARD** (total=74499): momentum_reject=22030, adx_reject=20678, basic_filters_failed=12105, sweeps_not_detected=8412, macd_reject=5190, ema_alignment_reject=3917, htf_poi_unanchored=1838, invalid_sl_geometry=163, insufficient_candles=95, rsi_reject=71
- **EVAL::TREND_PULLBACK** (total=76753): h1_trend_not_aligned=25450, basic_filters_failed=16308, ema_alignment_reject=11007, h1_pullback_not_confirmed=8380, no_ema_reclaim_close=4968, ema_not_tested_prev=3762, body_conviction_fail=2681, rsi_reject=1696, regime_blocked=687, prev_already_below_emas=453, prev_already_above_emas=409, no_prev_low_break=354, no_prev_high_break=226, momentum_flat=210, insufficient_candles=95, missing_fvg_or_orderblock=31, momentum_reject=20, ema21_not_tagged=16
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=96864): breakout_not_found=47599, basic_filters_failed=34829, move_not_fresh=8629, breakout_stale=3868, retest_proximity_failed=1512, volume_spike_missing=262, insufficient_candles=72, ema_alignment_reject=70, missing_fvg_or_orderblock=19, move_exhausted=3, rsi_reject=1
- **EVAL::WHALE_MOMENTUM** (total=78474): momentum_reject=52261, recent_ticks_insufficient=17291, basic_filters_failed=8922

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=25): execution:overextended=25
- **DIVERGENCE_CONTINUATION** (total=422): setup_compat:regime_VOLATILE_UNSUITABLE=415, setup_compat:regime_BREAKOUT_EXPANSION=7
- **FAILED_AUCTION_RECLAIM** (total=662): execution:overextended=385, setup_compat:regime_STRONG_TREND=224, setup_compat:regime_VOLATILE_UNSUITABLE=31, context_floor=22
- **FUNDING_EXTREME_SIGNAL** (total=792): execution:trigger_not_confirmed=762, context_floor=30
- **LIQUIDATION_REVERSAL** (total=42): execution:trigger_not_confirmed=42
- **LIQUIDITY_SWEEP_REVERSAL** (total=3183): execution:overextended=1305, execution:trigger_not_confirmed=1085, setup_compat:regime_STRONG_TREND=793
- **MA_CROSS_TREND_SHIFT** (total=21): setup_compat:regime_CLEAN_RANGE=9, execution:trigger_not_confirmed=6, setup_compat:regime_DIRTY_RANGE=5, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=4293): setup_compat:regime_WEAK_TREND=1850, setup_compat:regime_STRONG_TREND=1621, execution:overextended=820, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=1177): execution:overextended=674, execution:trigger_not_confirmed=331, entry_quality=172
- **MOVER_TREND_PULLBACK** (total=18159): execution:overextended=8153, execution:trigger_not_confirmed=7889, entry_quality=2117
- **QUIET_COMPRESSION_BREAK** (total=28): execution:trigger_not_confirmed=28
- **RANGE_FADE** (total=4305): setup_compat:regime_STRONG_TREND=1305, setup_compat:regime_WEAK_TREND=1087, execution:overextended=940, setup_compat:regime_VOLATILE_UNSUITABLE=865, context_edge=79, setup_compat:regime_BREAKOUT_EXPANSION=29
- **TREND_PULLBACK_EMA** (total=2092): setup_compat:regime_CLEAN_RANGE=1419, setup_compat:regime_DIRTY_RANGE=524, setup_compat:regime_VOLATILE_UNSUITABLE=114, entry_quality=35
- **VOLUME_SURGE_BREAKOUT** (total=58): execution:overextended=31, context_floor=27

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 206680 | 36.8% |
| QUIET | 143796 | 25.6% |
| TRENDING_DOWN | 87431 | 15.6% |
| TRENDING_UP | 80019 | 14.3% |
| VOLATILE | 43372 | 7.7% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **259**
- Average confidence gap to threshold: **11.29** (samples=259) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LINKUSDT=32, DOTUSDT=24, SOLUSDT=22, 1000PEPEUSDT=21, ENAUSDT=20, XRPUSDT=19, BANKUSDT=15, XLMUSDT=15, HYPEUSDT=11, XMRUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 55 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 165 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 15 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 16 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 141 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 5 |
| MEAN_REVERT | filtered | min_confidence | 13 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 10 |
| MEAN_REVERT | kept | min_confidence_pass | 85 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 304 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 19 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 572 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 941 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 15 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 6478 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 209 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 61 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 465 |
| RANGE_FADE | kept | min_confidence_pass | 2 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 5 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 65 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 11 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 321 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 19 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 12 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 87.50 | 65.00 | -22.50 | 20.10 | 17.60 | 20.00 | 5.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 59 | 57.39 | 63.98 | 6.59 | 20.99 | 20.00 | 16.84 | 3.07 | 10.46 |
| DIVERGENCE_CONTINUATION | kept | 165 | 71.25 | 65.00 | -6.25 | 20.09 | 19.77 | 18.56 | 2.45 | -1.52 |
| FAILED_AUCTION_RECLAIM | filtered | 16 | 53.99 | 60.56 | 6.57 | 21.11 | 19.24 | 20.00 | 3.22 | 5.75 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 64.30 | 65.00 | 0.70 | 20.85 | 18.15 | 20.00 | 3.00 | 9.10 |
| LIQUIDATION_REVERSAL | filtered | 16 | 74.50 | 10.00 | -64.50 | 19.66 | 8.00 | 15.70 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 44.40 | 65.00 | 20.60 | 20.20 | 15.60 | 17.00 | 0.00 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 141 | 69.18 | 65.00 | -4.18 | 20.81 | 17.57 | 17.51 | 2.49 | -0.02 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 57.35 | 65.00 | 7.65 | 20.65 | 17.70 | 15.80 | 0.00 | 10.00 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.32 | 65.00 | -5.32 | 20.82 | 19.88 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 23 | 53.63 | 65.00 | 11.37 | 20.78 | 16.42 | 14.50 | 0.00 | 7.51 |
| MEAN_REVERT | kept | 85 | 71.77 | 65.00 | -6.77 | 20.20 | 16.17 | 19.14 | 0.00 | 0.35 |
| MOVER_AVWAP_SCALP | filtered | 330 | 54.67 | 60.57 | 5.90 | 20.19 | 15.58 | 15.80 | 3.55 | 11.24 |
| MOVER_AVWAP_SCALP | kept | 572 | 77.22 | 65.00 | -12.22 | 20.46 | 16.43 | 15.80 | 4.08 | 0.18 |
| MOVER_TREND_PULLBACK | filtered | 956 | 56.35 | 64.51 | 8.16 | 19.71 | 18.45 | 15.80 | 4.22 | 14.05 |
| MOVER_TREND_PULLBACK | kept | 6478 | 77.01 | 65.00 | -12.01 | 19.79 | 18.38 | 15.80 | 4.49 | 0.63 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 74.20 | 65.00 | -9.20 | 20.50 | 20.00 | 20.00 | 3.50 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 270 | 53.47 | 64.85 | 11.38 | 21.21 | 19.67 | 20.00 | 0.00 | 8.84 |
| QUIET_COMPRESSION_BREAK | kept | 465 | 76.91 | 65.00 | -11.91 | 21.80 | 19.79 | 20.00 | 0.00 | -0.96 |
| RANGE_FADE | kept | 2 | 69.50 | 65.00 | -4.50 | 20.80 | 14.65 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | kept | 5 | 69.76 | 65.00 | -4.76 | 21.20 | 20.00 | 15.20 | 1.30 | 1.00 |
| TREND_PULLBACK_EMA | filtered | 76 | 56.89 | 64.08 | 7.19 | 20.56 | 19.69 | 18.11 | 5.06 | 9.51 |
| TREND_PULLBACK_EMA | kept | 321 | 79.36 | 65.00 | -14.36 | 20.66 | 19.77 | 17.29 | 5.01 | -0.90 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.70 | 60.00 | 0.30 | 20.71 | 18.00 | 20.00 | 5.00 | 6.60 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 75.75 | 65.00 | -10.75 | 19.37 | 16.88 | 20.00 | 5.04 | 5.30 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 87.50 | 25.00 | 14.00 | 15.00 | 17.00 | 5.00 | 9.00 | 5.50 |
| DIVERGENCE_CONTINUATION | filtered | 59 | 57.39 | 23.24 | 8.34 | 5.75 | 12.92 | 6.03 | 8.51 | 3.07 |
| DIVERGENCE_CONTINUATION | kept | 165 | 71.25 | 23.06 | 13.58 | 5.55 | 12.00 | 5.98 | 8.70 | 2.45 |
| FAILED_AUCTION_RECLAIM | filtered | 16 | 53.99 | 23.50 | 15.00 | 6.56 | 13.81 | 6.97 | 5.68 | 3.22 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 64.30 | 24.00 | 16.00 | 10.50 | 15.50 | 6.75 | 5.15 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 16 | 74.50 | 19.50 | 18.00 | 15.00 | 8.00 | 8.00 | 2.00 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 44.40 | 17.00 | 14.00 | 9.00 | 11.00 | 5.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 141 | 69.18 | 22.90 | 14.11 | 4.19 | 12.72 | 5.57 | 7.19 | 2.49 |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 57.35 | 21.00 | 14.00 | 9.00 | 14.00 | 8.50 | 8.35 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.32 | 21.40 | 14.00 | 6.60 | 13.80 | 6.00 | 8.52 | 0.00 |
| MEAN_REVERT | filtered | 23 | 53.63 | 25.00 | 15.74 | 7.04 | 12.00 | 5.00 | 4.84 | 0.00 |
| MEAN_REVERT | kept | 85 | 71.77 | 22.39 | 17.01 | 9.42 | 11.54 | 6.82 | 4.93 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 330 | 54.67 | 17.95 | 18.55 | 9.57 | 13.22 | 6.84 | 5.32 | 3.55 |
| MOVER_AVWAP_SCALP | kept | 572 | 77.22 | 19.49 | 18.01 | 9.40 | 13.02 | 5.84 | 8.33 | 4.08 |
| MOVER_TREND_PULLBACK | filtered | 956 | 56.35 | 18.11 | 18.10 | 7.90 | 12.98 | 5.22 | 8.18 | 4.22 |
| MOVER_TREND_PULLBACK | kept | 6478 | 77.01 | 19.33 | 18.05 | 8.08 | 13.04 | 5.94 | 9.01 | 4.49 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 74.20 | 17.00 | 18.00 | 15.00 | 11.00 | 5.00 | 4.70 | 3.50 |
| QUIET_COMPRESSION_BREAK | filtered | 270 | 53.47 | 18.19 | 17.10 | 11.34 | 14.07 | 6.86 | 4.02 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 465 | 76.91 | 18.77 | 17.48 | 12.65 | 14.06 | 6.56 | 7.63 | 0.00 |
| RANGE_FADE | kept | 2 | 69.50 | 21.00 | 14.00 | 12.00 | 13.50 | 5.00 | 4.00 | 0.00 |
| SR_FLIP_RETEST | kept | 5 | 69.76 | 18.20 | 18.00 | 5.40 | 14.00 | 5.00 | 8.86 | 1.30 |
| TREND_PULLBACK_EMA | filtered | 76 | 56.89 | 14.86 | 18.00 | 8.74 | 14.99 | 6.30 | 8.92 | 5.06 |
| TREND_PULLBACK_EMA | kept | 321 | 79.36 | 19.17 | 18.00 | 7.55 | 13.96 | 6.94 | 8.96 | 5.01 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.70 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 2.30 | 5.00 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 75.75 | 20.33 | 17.33 | 12.25 | 13.75 | 4.58 | 9.01 | 5.04 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 87.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 59 | 57.39 | 0.00 | 0.00 | 0.00 | 0.00 | 3.25 | 0.00 | 0.00 | 0.00 | **3.25** |
| DIVERGENCE_CONTINUATION | kept | 165 | 71.25 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| FAILED_AUCTION_RECLAIM | filtered | 16 | 53.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 64.30 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | 0.00 | 0.00 | 0.00 | **3.60** |
| LIQUIDATION_REVERSAL | filtered | 16 | 74.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 44.40 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 141 | 69.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 2 | 57.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 5 | 70.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 23 | 53.63 | 0.00 | 0.00 | 0.00 | 0.00 | 5.63 | 0.00 | 0.00 | 1.88 | **7.51** |
| MEAN_REVERT | kept | 85 | 71.77 | 0.00 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | **0.35** |
| MOVER_AVWAP_SCALP | filtered | 330 | 54.67 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.96 | **3.14** |
| MOVER_AVWAP_SCALP | kept | 572 | 77.22 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | **0.15** |
| MOVER_TREND_PULLBACK | filtered | 956 | 56.35 | 0.00 | 0.00 | 1.26 | 0.00 | 0.91 | 0.02 | 0.00 | 0.08 | **2.27** |
| MOVER_TREND_PULLBACK | kept | 6478 | 77.01 | 0.00 | 0.00 | 0.40 | 0.00 | 0.18 | 0.00 | 0.00 | 0.01 | **0.59** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 74.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 270 | 53.47 | 0.00 | 0.00 | 0.29 | 0.00 | 0.52 | 0.07 | 0.00 | 5.94 | **6.82** |
| QUIET_COMPRESSION_BREAK | kept | 465 | 76.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.06 | **0.12** |
| RANGE_FADE | kept | 2 | 69.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 5 | 69.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 76 | 56.89 | 0.00 | 0.00 | 1.47 | 0.00 | 6.13 | 0.00 | 0.00 | 0.00 | **7.60** |
| TREND_PULLBACK_EMA | kept | 321 | 79.36 | 0.00 | 0.00 | 0.15 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **0.22** |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 75.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **134215 held of 238727 seen** across 21 strategies; 3025 cells past the sample floor; **1028 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 31851 | 207/31644/0 | 49% | -0.06 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17082 | 24/17058/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16550 | 1/16549/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11785 | 4/11781/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9444 | 0/9444/0 | 49% | -0.07 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 8839 | 27/8812/0 | 36% | -0.29 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| TREND_PULLBACK_EMA | 5282 | 2/5280/0 | 47% | -0.24 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_MEAN_REVERT | 4882 | 0/0/4882 | 42% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.73R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL (-1.07R) |
| LIQUIDITY_SWEEP_REVERSAL | 4830 | 11/4819/0 | 47% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4436 | 0/0/4436 | 38% | +0.06 | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.82R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.26R) |
| MEAN_REVERT | 4115 | 0/4115/0 | 73% | +0.44 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.29R) |
| SHADOW_FUNDING_FADE | 4053 | 0/0/4053 | 38% | -0.34 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.20R) | NY/MARKUP/NORMAL/BTC_RISING (-0.95R) |
| RANGE_FADE | 3645 | 0/3645/0 | 27% | -0.51 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2532 | 19/2513/0 | 41% | +0.03 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2316 | 4/2312/0 | 31% | -0.45 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.34R) |
| WHALE_MOMENTUM | 1458 | 0/1458/0 | 45% | -0.26 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.81R) |
| SHADOW_CASCADE_REVERSAL | 501 | 0/0/501 | 48% | -0.16 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.03R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.76R) |
| BREAKDOWN_SHORT | 411 | 9/402/0 | 47% | +0.01 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 106 | 0/106/0 | 40% | -0.74 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 71 | 0/71/0 | 87% | +0.72 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 26 | 1/25/0 | 35% | -0.42 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `RANGE_FADE @ ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP` -1.38R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 106 | 35% / -0.42R | 106 | 58% / -0.08R | +0.33 | **ATR** |
| TREND_PULLBACK_EMA | 177 | 39% / -0.33R | 177 | 42% / -0.16R | +0.17 | **ATR** |
| MOVER_AVWAP_SCALP | 521 | 38% / -0.23R | 521 | 41% / -0.12R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 2772 | 46% / -0.20R | 2772 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 854 | 47% / -0.13R | 854 | 52% / -0.06R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 699 | 50% / -0.18R | 699 | 54% / -0.13R | +0.06 | **ATR** |
| WHALE_MOMENTUM | 108 | 49% / -0.25R | 108 | 48% / -0.30R | -0.05 | **FIXED** |
| MOVER_TREND_PULLBACK | 3908 | 51% / -0.07R | 3908 | 54% / -0.01R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 80 | 41% / -0.01R | 80 | 51% / -0.04R | -0.04 | **FIXED** |
| MEAN_REVERT | 421 | 54% / +0.00R | 421 | 50% / +0.04R | +0.04 | **ATR** |
| RANGE_FADE | 232 | 19% / -0.64R | 232 | 21% / -0.61R | +0.03 | **ATR** |
| BREAKDOWN_SHORT | 19 | 26% / -0.34R | 19 | 26% / -0.31R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1453 | 45% / -0.13R | 1453 | 44% / -0.15R | -0.02 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2275 | 47% / -0.11R | 2275 | 47% / -0.11R | +0.00 | **ATR** |
| MA_CROSS_TREND_SHIFT | 11 | 36% / -0.25R | 11 | 36% / -0.24R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 62% / +0.14R | 8 | 62% / +0.00R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 7 | 29% / -0.91R | 7 | 43% / -0.40R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 5488 | 31% | -0.12R | 278 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 511 | 40% | -0.13R | 130 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 33 | 61% | +0.03R | 20 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1230 | 28% / -1.68R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 19 | 21% / -0.72R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 4491 | 39% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 978 | 32% / -0.57R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 90 | 22% / -0.90R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 680 | 31% / -1.63R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 939 | 34% / -0.16R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 333 | 42% / -1.09R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 122 | 30% / -1.26R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 199 | 27% / -0.73R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 546 | 32% / -0.25R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 13 | 31% / -0.86R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 154 | 42% / -0.21R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 65 | 43% / -0.10R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 6 | 17% / -0.84R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 8 | 12% / -1.44R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 30 | 47% / -0.36R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 45 · alerting: **5** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 33/92 unfetchable (36%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, ADAUSDT, DOGEUSDT, DOTUSDT, FILUSDT +6 more (streak 8/6) (sustained 8 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 76/6) (sustained 76 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 378x (gate reads 0x, withheld 0x — refusal dark); last LITUSDT age=25445.7s (streak 19/6) (sustained 19 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.43R (bound 0.3) (streak 76/6) (sustained 76 cycles)
- **ALERT** `tuned_variants` — 82 non-stamps — atr_arm_uncomputable=82 (seen=1868 stamped=206 skipped=1580) (streak 70/6) (sustained 70 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 5051112 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 15 arms current, none stalled; covering 43/43 signals (100%) | 0 |
| auto_dispatch | ok | attempts=2 fanouts=2 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64019.90 | 0 |
| candle_coverage | ok | 102/105 symbols with ≥20 15m candles, 96/105 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 496 dup bars, 0 undedupable; ws 0 out-of-order, 53 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 76/6) | 76 |
| context_emission_policy | ok | output +28 / upstream +18 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 93/93 signals (100%) | 0 |
| dark_resolution | ok | 64 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 111/111 signals (100%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 2056442 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.43R (bound 0.3) (streak 76/6) | 76 |
| emission_controller | ok | last cycle 1010s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4127 stamps (MEAN_REVERT=1394, MOVER_AVWAP_SCALP=302, MOVER_TREND_PULLBACK=1797, RANGE_FADE=420, TREND_PULLBACK_EMA=214), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +11 / upstream +196 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | emitted_total=9 | 0 |
| mean_revert_path | ok | output +63 / upstream +196 | 0 |
| mover_admission_metadata | ok | 858 symbols known, 157 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 394708 evicted (sampled: execution:overextended 400/145105, execution:trigger_not_confirmed 400/136485, setup_compat:regime_STRONG_TREND 400/48747) | 0 |
| price_action_lane | ok | 173682 evaluated, 133 emitted; layer1 133 stamped / 0 blind; cooldown=14940, delta_opposed=11020, no_footprint=58836, no_opposing_target=198, no_sweep=77916, rr_below_floor=10639 | 0 |
| promoted_pair_integrity | ok | 23/23 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.51R over n=3645 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +27 / upstream +196 | 0 |
| sar_alignment_crosscheck | ok | 134/5974 disagreed (2.2%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +196 | 0 |
| sar_hold_arm | ok | 77 held arms settled, 10 unscored, 17 still walking (17 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 33/92 unfetchable (36%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, ADAUSDT, DOGEUSDT, DOTUSDT, FILUSDT +6 more (streak 8/6) | 8 |
| sar_live_arms | ok | 17 arms current, none stalled; covering 52/52 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 8 resolved, 51 still mid-window | 0 |
| setup_tf_resolver | ok | 53228 resolutions, 30906 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 378x (gate reads 0x, withheld 0x — refusal dark); last LITUSDT age=25445.7s (streak 19/6) | 19 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +34 / upstream +196 | 0 |
| structural_snap | ok | 2593/2593 measured, 7 blind, 0 levels moved (refusals: redetect_cooldown=939) | 0 |
| structural_veto_lane | ok | 1165 stamped; 0 with no readable level book, 11 with clear air ahead, 667 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +196 / upstream +18 | 0 |
| tuned_variants | violating | 82 non-stamps — atr_arm_uncomputable=82 (seen=1868 stamped=206 skipped=1580) (streak 70/6) | 70 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2644130`
- `Path funnel` emissions: `65`
- `Regime distribution` emissions: `65`
- `QUIET_SCALP_BLOCK` events: `259`
- `confidence_gate` events: `10023`
- `free_channel_post` events: `20`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 1 | 3032 | 3032 | 3032 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **20**

| Source | Count |
|---|---:|
| signal_close | 16 |
| regime_shift | 4 |

- By severity: HIGH=20

## Dependency readiness
- cvd: presence[present=422550] state[populated=422550] buckets[few=4, many=422434, some=112] sources[none] quality[none]
- funding_rate: presence[absent=52215, present=370335] state[empty=52215, populated=370335] buckets[few=370335, none=52215] sources[none] quality[none]
- liquidation_clusters: presence[absent=253939, present=168611] state[empty=253939, populated=168611] buckets[few=133067, none=253939, some=35544] sources[none] quality[none]
- oi_snapshot: presence[absent=49064, present=373486] state[empty=49064, populated=373486] buckets[few=293, many=371677, none=49064, some=1516] sources[none] quality[none]
- order_book: presence[absent=123172, present=299378] state[populated=299378, unavailable=123172] buckets[few=299378, none=123172] sources[book_ticker=299378, unavailable=123172] quality[none=123172, top_of_book_only=299378]
- orderblocks: presence[absent=422550] state[empty=422550] buckets[none=422550] sources[measured_dark=422518, not_implemented=32] quality[none]
- recent_ticks: presence[absent=3827, present=418723] state[empty=3827, populated=418723] buckets[many=418723, none=3827] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.899714946746826` sec
- Median create→first breach: `2549.9958235025406` sec
- Median create→terminal: `2636.689390540123` sec
- Median first breach→terminal: `4.653218865394592` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 6.2}, "under_180s": {"count": 1, "pct": 6.2}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 14 | 14 | 4.8594178143344955 | 3.0 | 1.6198059381114986 | 11 | 3 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 2.57748583053186 | 3.0 | 0.85916194351062 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 14 | 14 | 0.0 | 35.7 | 0.0 | 0.0 | 1.1618 | 2549.9958235025406 | 2636.689390540123 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.5775 | 6453.565072417259 | 6456.420068979263 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 137 | 1 | 112 | 0.0 | 0.0 | None | None | 25 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2385 | 25 | 1892 | 0.0 | 0.0 | None | None | 493 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-8`
- Gating Δ: `-18711`
- No-generation Δ: `-214574`
- Fast failures Δ: `-5`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.587, "current_avg_pnl": 1.1618, "current_win_rate": 0.0, "previous_avg_pnl": 0.5748, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": -46, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 10, "geometry_changed_delta": 0, "geometry_preserved_delta": 341, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
