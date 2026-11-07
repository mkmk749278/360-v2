# Runtime Truth Report

## Executive summary
- Overall health/freshness: **halted_by_breaker**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `967` sec
- ⛔ **HALTED BY LOSS CIRCUIT BREAKER** — reason: Daily drawdown 11.22% exceeded threshold 10.0%; cooldown remaining: 169.3s. This is a deliberate protective pause (not a crash); the stale heartbeat and zero-signal window are expected while halted.

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 54 | 54 | 54 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 7852 | 7852 | 6954 | 24 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 64853 | 64842 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 60064 | 60065 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 59570 | 57716 | 2332 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 60101 | 59308 | 896 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 59474 | 59425 | 85 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 51815 | 51835 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 60212 | 60267 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 60271 | 58513 | 2510 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 67755 | 72882 | 605 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 64885 | 60026 | 7669 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 59109 | 59110 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 60072 | 60075 | 21 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 59519 | 59334 | 231 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 61034 | 60011 | 1460 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 59110 | 59267 | 198 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 51425 | 48938 | 2757 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 51703 | 51366 | 442 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 64810 | 64847 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 51841 | 51853 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2896 | 2896 | 2351 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 319 | 319 | 36 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 11976 | 11976 | 11679 | 4 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 6 | 6 | 1 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6119 | 6119 | 3643 | 5 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1307 | 1307 | 285 | 45 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 17111 | 17111 | 8322 | 255 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 95 | 95 | 95 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 879 | 879 | 421 | 27 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3441 | 3441 | 2092 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 503 | 503 | 235 | 7 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1656 | 1656 | 1264 | 40 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 18 | 18 | 5 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=64842): breakout_not_found=35736, basic_filters_failed=18974, move_not_fresh=6491, breakout_stale=2958, retest_proximity_failed=548, volume_spike_missing=121, move_exhausted=13, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=60065): cls_disabled_merged_into_lsr=60065
- **EVAL::DIVERGENCE_CONTINUATION** (total=57716): cvd_divergence_failed=20815, basic_filters_failed=15938, h1_trend_not_aligned=15005, ema_alignment_reject=5075, retest_proximity_failed=718, missing_fvg_or_orderblock=165
- **EVAL::FAILED_AUCTION_RECLAIM** (total=59308): auction_not_detected=35777, basic_filters_failed=15304, reclaim_hold_failed=3178, regime_blocked=3003, tail_too_small=2034, rsi_reject=12
- **EVAL::FUNDING_EXTREME** (total=59425): funding_not_extreme=40398, basic_filters_failed=15692, missing_funding_rate=1520, ema_alignment_reject=977, rsi_reject=626, momentum_reject=117, cvd_divergence_failed=92, missing_fvg_or_orderblock=3
- **EVAL::LIQUIDATION_REVERSAL** (total=51835): cascade_threshold_not_met=35534, basic_filters_failed=15708, rsi_reject=289, cvd_divergence_failed=286, missing_fvg_or_orderblock=10, volume_spike_missing=8
- **EVAL::MA_CROSS_TREND_SHIFT** (total=60267): no_ma_cross=43668, basic_filters_failed=15963, ma_cross_htf_misaligned=326, ma_cross_cooldown=310
- **EVAL::MEAN_REVERT** (total=58513): no_extension=48587, basic_filters_failed=9926
- **EVAL::MOVER_AVWAP_SCALP** (total=72882): no_avwap_tag=26071, no_mover_leg=19296, basic_filters_failed=19170, avwap_slope_against=5076, avwap_reclaim_no_volume=1973, no_avwap_reclaim=1283, anchor_too_recent=13
- **EVAL::MOVER_TREND_PULLBACK** (total=60026): mover_run_too_small=29096, basic_filters_failed=19069, no_reclaim=10387, no_pullback_tag=1474
- **EVAL::OPENING_RANGE_BREAKOUT** (total=59110): feature_disabled=59110
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=60075): regime_blocked=43044, breakout_not_found=10416, basic_filters_failed=3296, adx_reject=3252, ema_alignment_reject=67
- **EVAL::QUIET_COMPRESSION_BREAK** (total=59334): compression_not_detected=20046, regime_blocked=19939, basic_filters_failed=11991, breakout_not_detected=6794, volume_confirmation_failed=554, rsi_reject=6, missing_fvg_or_orderblock=3, macd_reject=1
- **EVAL::RANGE_FADE** (total=60011): no_range_edge=50080, basic_filters_failed=9931
- **EVAL::SR_FLIP_RETEST** (total=59267): flip_close_not_confirmed=35488, basic_filters_failed=15271, regime_blocked=2982, retest_out_of_zone=1964, long_break_volume_thin=1491, h1_break_not_confirmed=1107, reclaim_hold_failed=624, ema_alignment_reject=171, wick_quality_failed=72, whipsaw_flip=46, long_acceptance_not_held=46, missing_fvg_or_orderblock=5
- **EVAL::STANDARD** (total=48938): adx_reject=19159, momentum_reject=12052, basic_filters_failed=7083, macd_reject=4093, sweeps_not_detected=3494, ema_alignment_reject=2379, htf_poi_unanchored=637, invalid_sl_geometry=22, rsi_reject=18, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=51366): h1_trend_not_aligned=15581, basic_filters_failed=11200, ema_alignment_reject=9330, h1_pullback_not_confirmed=3929, no_ema_reclaim_close=3381, ema_not_tested_prev=2760, body_conviction_fail=2113, rsi_reject=1704, prev_already_below_emas=543, no_prev_low_break=275, prev_already_above_emas=266, momentum_flat=120, no_prev_high_break=115, missing_fvg_or_orderblock=35, momentum_reject=14
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=64847): breakout_not_found=34899, basic_filters_failed=18972, move_not_fresh=6639, breakout_stale=3305, retest_proximity_failed=827, volume_spike_missing=144, move_exhausted=41, missing_fvg_or_orderblock=20
- **EVAL::WHALE_MOMENTUM** (total=51853): momentum_reject=44009, recent_ticks_insufficient=4315, basic_filters_failed=3529

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=239): setup_compat:regime_VOLATILE_UNSUITABLE=233, setup_compat:regime_BREAKOUT_EXPANSION=6
- **FAILED_AUCTION_RECLAIM** (total=633): setup_compat:regime_STRONG_TREND=255, execution:overextended=210, context_floor=132, setup_compat:regime_VOLATILE_UNSUITABLE=36
- **FUNDING_EXTREME_SIGNAL** (total=212): execution:trigger_not_confirmed=211, context_floor=1
- **LIQUIDATION_REVERSAL** (total=7): execution:trigger_not_confirmed=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=2284): execution:trigger_not_confirmed=883, execution:overextended=805, setup_compat:regime_STRONG_TREND=596
- **MA_CROSS_TREND_SHIFT** (total=2): setup_compat:regime_DIRTY_RANGE=2
- **MEAN_REVERT** (total=4010): setup_compat:regime_WEAK_TREND=2285, setup_compat:regime_STRONG_TREND=1468, execution:overextended=206, entry_quality=51
- **MOVER_AVWAP_SCALP** (total=721): execution:overextended=423, execution:trigger_not_confirmed=206, entry_quality=92
- **MOVER_TREND_PULLBACK** (total=9010): execution:trigger_not_confirmed=5220, execution:overextended=2662, entry_quality=1128
- **QUIET_COMPRESSION_BREAK** (total=34): execution:trigger_not_confirmed=22, execution:overextended=12
- **RANGE_FADE** (total=1669): setup_compat:regime_WEAK_TREND=1013, setup_compat:regime_STRONG_TREND=521, setup_compat:regime_VOLATILE_UNSUITABLE=104, execution:overextended=30, context_edge=1
- **TREND_PULLBACK_EMA** (total=1554): setup_compat:regime_CLEAN_RANGE=1084, setup_compat:regime_DIRTY_RANGE=308, entry_quality=107, setup_compat:regime_VOLATILE_UNSUITABLE=55
- **VOLUME_SURGE_BREAKOUT** (total=1): execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 124239 | 38.4% |
| QUIET | 89175 | 27.6% |
| TRENDING_UP | 49427 | 15.3% |
| TRENDING_DOWN | 44300 | 13.7% |
| VOLATILE | 16170 | 5.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **263**
- Average confidence gap to threshold: **15.87** (samples=263) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XMRUSDT=38, ARBUSDT=27, SOLUSDT=26, BTCUSDT=17, BNBUSDT=15, ASTERUSDT=11, FILUSDT=11, ENAUSDT=11, WLFIUSDT=11, LTCUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 50 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 157 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 104 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 3 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 6 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 92 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 17 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 87 |
| MEAN_REVERT | kept | min_confidence_pass | 50 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 426 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 7 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 208 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1075 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 26 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2430 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 196 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 91 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 107 |
| SR_FLIP_RETEST | filtered | min_confidence | 78 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 7 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 26 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 49 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 15 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 160 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 13 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 53 | 54.14 | 64.92 | 10.78 | 20.98 | 19.91 | 16.99 | 2.60 | 15.62 |
| DIVERGENCE_CONTINUATION | kept | 157 | 72.78 | 65.00 | -7.78 | 20.94 | 19.24 | 17.91 | 1.23 | 0.07 |
| FAILED_AUCTION_RECLAIM | filtered | 107 | 49.65 | 61.74 | 12.09 | 21.79 | 17.42 | 20.00 | 1.69 | 8.40 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 68.75 | 65.00 | -3.75 | 20.95 | 19.55 | 20.00 | 2.50 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 38.77 | 60.50 | 21.73 | 18.97 | 14.40 | 17.00 | 3.50 | 21.90 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.50 | 65.00 | -0.50 | 20.10 | 10.90 | 17.00 | 7.00 | 7.20 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 101 | 44.12 | 65.00 | 20.88 | 20.44 | 19.57 | 18.63 | 1.50 | 15.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 71.75 | 65.00 | -6.75 | 22.10 | 19.55 | 17.04 | 1.29 | 0.05 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.00 | 61.00 | 4.00 | 20.60 | 16.50 | 15.80 | 0.00 | 9.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.85 | 65.00 | -5.85 | 21.05 | 18.95 | 15.80 | 0.00 | 0.40 |
| MEAN_REVERT | filtered | 87 | 51.60 | 62.87 | 11.27 | 20.33 | 15.92 | 14.05 | 0.00 | 19.15 |
| MEAN_REVERT | kept | 50 | 69.45 | 65.00 | -4.45 | 19.83 | 15.99 | 14.48 | 0.00 | 1.51 |
| MOVER_AVWAP_SCALP | filtered | 437 | 55.56 | 64.04 | 8.48 | 19.92 | 15.87 | 15.80 | 4.11 | 9.53 |
| MOVER_AVWAP_SCALP | kept | 208 | 78.65 | 65.00 | -13.65 | 20.48 | 16.01 | 15.80 | 4.47 | 2.85 |
| MOVER_TREND_PULLBACK | filtered | 1101 | 56.81 | 63.97 | 7.16 | 19.74 | 18.55 | 15.80 | 4.10 | 16.14 |
| MOVER_TREND_PULLBACK | kept | 2430 | 76.89 | 65.00 | -11.89 | 20.26 | 18.79 | 15.80 | 4.33 | 1.72 |
| QUIET_COMPRESSION_BREAK | filtered | 287 | 47.31 | 64.85 | 17.54 | 21.33 | 19.24 | 20.00 | 0.00 | 10.77 |
| QUIET_COMPRESSION_BREAK | kept | 107 | 75.24 | 65.00 | -10.24 | 20.15 | 19.78 | 20.00 | 0.00 | -1.60 |
| SR_FLIP_RETEST | filtered | 85 | 56.25 | 63.16 | 6.91 | 20.64 | 20.00 | 15.48 | 2.12 | 14.64 |
| SR_FLIP_RETEST | kept | 26 | 69.40 | 65.00 | -4.40 | 20.77 | 20.00 | 16.76 | 2.12 | 1.94 |
| TREND_PULLBACK_EMA | filtered | 64 | 58.59 | 63.91 | 5.32 | 20.94 | 19.46 | 18.01 | 4.52 | 16.19 |
| TREND_PULLBACK_EMA | kept | 160 | 81.06 | 65.00 | -16.06 | 21.23 | 19.67 | 17.93 | 4.86 | -0.69 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 72.09 | 65.00 | -7.09 | 20.45 | 17.14 | 20.00 | 4.04 | 2.77 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 53 | 54.14 | 20.62 | 11.81 | 8.32 | 12.58 | 5.33 | 8.50 | 2.60 |
| DIVERGENCE_CONTINUATION | kept | 157 | 72.78 | 22.25 | 15.91 | 6.13 | 13.45 | 5.74 | 9.12 | 1.23 |
| FAILED_AUCTION_RECLAIM | filtered | 107 | 49.65 | 20.48 | 17.66 | 6.95 | 15.29 | 6.93 | 4.05 | 1.69 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 68.75 | 25.00 | 18.00 | 3.00 | 14.00 | 8.25 | 5.50 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 38.77 | 18.33 | 12.00 | 7.50 | 14.33 | 6.67 | 5.83 | 3.50 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.50 | 25.00 | 8.00 | 12.00 | 15.00 | 5.00 | 0.70 | 7.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 101 | 44.12 | 20.49 | 16.02 | 6.21 | 13.35 | 5.16 | 6.57 | 1.50 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 71.75 | 23.24 | 16.35 | 4.06 | 13.00 | 5.88 | 8.15 | 1.29 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.00 | 17.00 | 14.00 | 6.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.85 | 19.00 | 14.00 | 7.50 | 14.00 | 9.25 | 7.50 | 0.00 |
| MEAN_REVERT | filtered | 87 | 51.60 | 20.31 | 16.94 | 10.34 | 11.89 | 5.00 | 6.27 | 0.00 |
| MEAN_REVERT | kept | 50 | 69.45 | 24.68 | 14.08 | 7.68 | 12.40 | 5.00 | 7.19 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 437 | 55.56 | 19.09 | 18.23 | 11.28 | 13.70 | 5.54 | 4.71 | 4.11 |
| MOVER_AVWAP_SCALP | kept | 208 | 78.65 | 20.84 | 18.01 | 12.19 | 13.17 | 6.25 | 8.10 | 4.47 |
| MOVER_TREND_PULLBACK | filtered | 1101 | 56.81 | 18.82 | 18.19 | 7.64 | 12.97 | 6.01 | 7.68 | 4.10 |
| MOVER_TREND_PULLBACK | kept | 2430 | 76.89 | 19.45 | 18.02 | 7.81 | 13.39 | 6.53 | 9.31 | 4.33 |
| QUIET_COMPRESSION_BREAK | filtered | 287 | 47.31 | 18.81 | 16.73 | 10.85 | 14.06 | 7.22 | 4.31 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 107 | 75.24 | 18.64 | 17.81 | 11.61 | 14.06 | 5.69 | 8.49 | 0.00 |
| SR_FLIP_RETEST | filtered | 85 | 56.25 | 21.85 | 17.18 | 4.06 | 13.81 | 5.00 | 7.22 | 2.12 |
| SR_FLIP_RETEST | kept | 26 | 69.40 | 20.54 | 16.85 | 4.85 | 14.00 | 5.27 | 8.19 | 2.12 |
| TREND_PULLBACK_EMA | filtered | 64 | 58.59 | 14.59 | 18.00 | 7.83 | 14.09 | 6.42 | 9.32 | 4.52 |
| TREND_PULLBACK_EMA | kept | 160 | 81.06 | 19.87 | 18.01 | 7.66 | 14.61 | 7.34 | 9.48 | 4.86 |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 72.09 | 17.62 | 14.00 | 12.00 | 13.77 | 5.00 | 9.59 | 4.04 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 53 | 54.14 | 0.00 | 0.00 | 2.49 | 0.00 | 2.35 | 0.00 | 0.00 | 0.00 | **4.84** |
| DIVERGENCE_CONTINUATION | kept | 157 | 72.78 | 0.00 | 0.00 | 1.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.46** |
| FAILED_AUCTION_RECLAIM | filtered | 107 | 49.65 | 0.00 | 0.00 | 4.79 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.79** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 68.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 38.77 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.50 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 101 | 44.12 | 0.00 | 0.00 | 2.90 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | **3.11** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 17 | 71.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.00 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 70.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 87 | 51.60 | 0.00 | 0.00 | 2.30 | 0.00 | 1.10 | 0.00 | 0.00 | 0.00 | **3.40** |
| MEAN_REVERT | kept | 50 | 69.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 437 | 55.56 | 0.00 | 0.00 | 0.00 | 0.00 | 2.95 | 0.00 | 0.00 | 1.88 | **4.83** |
| MOVER_AVWAP_SCALP | kept | 208 | 78.65 | 0.00 | 0.00 | 0.66 | 0.00 | 0.91 | 0.00 | 0.00 | 0.25 | **1.82** |
| MOVER_TREND_PULLBACK | filtered | 1101 | 56.81 | 0.85 | 0.00 | 1.25 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | **2.24** |
| MOVER_TREND_PULLBACK | kept | 2430 | 76.89 | 0.00 | 0.00 | 0.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.47** |
| QUIET_COMPRESSION_BREAK | filtered | 287 | 47.31 | 0.00 | 0.00 | 0.10 | 0.00 | 0.34 | 0.00 | 0.00 | 6.08 | **6.52** |
| QUIET_COMPRESSION_BREAK | kept | 107 | 75.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.12** |
| SR_FLIP_RETEST | filtered | 85 | 56.25 | 0.00 | 0.00 | 0.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.85** |
| SR_FLIP_RETEST | kept | 26 | 69.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 64 | 58.59 | 0.00 | 0.00 | 3.45 | 0.00 | 2.89 | 0.00 | 0.00 | 0.00 | **6.34** |
| TREND_PULLBACK_EMA | kept | 160 | 81.06 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.18** |
| VOLUME_SURGE_BREAKOUT | kept | 13 | 72.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **177785 held of 762957 seen** across 21 strategies; 4024 cells past the sample floor; **2126 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 47579 | 603/46976/0 | 43% | -0.19 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING/MIDCAP (-1.35R) |
| MOVER_AVWAP_SCALP | 23584 | 181/23403/0 | 44% | -0.20 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 13747 | 175/13572/0 | 45% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13304 | 153/13151/0 | 38% | -0.27 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 11845 | 63/11782/0 | 37% | -0.32 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 9906 | 108/9798/0 | 37% | -0.45 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 8081 | 435/7646/0 | 46% | -0.13 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8015 | 0/0/8015 | 43% | -0.07 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.68R) | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.90R) |
| SHADOW_RANGE_FADE | 7522 | 0/0/7522 | 36% | -0.13 | NY/RANGE/NORMAL/BTC_NEUTRAL (+0.41R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| SHADOW_FUNDING_FADE | 6900 | 0/0/6900 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 5446 | 17/5429/0 | 46% | -0.27 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+2.10R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5271 | 69/5202/0 | 36% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.42R) |
| FUNDING_EXTREME_SIGNAL | 3853 | 2/3851/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3747 | 0/3747/0 | 30% | -0.36 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| RANGE_FADE | 2214 | 6/2208/0 | 41% | -0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1613 | 0/0/1613 | 53% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 194 | 32/162/0 | 42% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 340 | 27% / -0.58R | 340 | 52% / -0.10R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1119 | 37% / -0.39R | 1119 | 49% / -0.09R | +0.30 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1528 | 42% / -0.37R | 1528 | 56% / -0.12R | +0.25 | **ATR** |
| SR_FLIP_RETEST | 552 | 43% / -0.32R | 552 | 48% / -0.17R | +0.15 | **ATR** |
| MA_CROSS_TREND_SHIFT | 57 | 42% / -0.20R | 57 | 46% / -0.08R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2462 | 44% / -0.17R | 2462 | 51% / -0.05R | +0.12 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 201 | 37% / -0.18R | 201 | 48% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8717 | 48% / -0.14R | 8717 | 53% / -0.03R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1410 | 41% / -0.21R | 1410 | 43% / -0.11R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 119 | 39% / -0.08R | 119 | 47% / +0.01R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1640 | 48% / -0.12R | 1640 | 53% / -0.06R | +0.06 | **ATR** |
| MEAN_REVERT | 420 | 48% / -0.13R | 420 | 46% / -0.15R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1412 | 45% / -0.15R | 1412 | 45% / -0.15R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11660 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2462 | 48% | -0.05R | 235 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 126 | 49% | -0.05R | 67 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1780 | 39% / -0.14R | +0.87 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1459 | 32% / -0.27R | +0.80 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3011 | 35% / -0.22R | +0.62 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10656 | 36% / -0.21R | +0.33 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1917 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1357 | 36% / -0.14R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1175 | 32% / -0.25R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 296 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 448 | 32% / -0.18R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 348 | 48% / -0.06R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 88 | 44% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 492 | 33% / -0.34R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 93 | 27% / -0.40R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **5** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×458]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 323/6) (sustained 323 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 7/6) (sustained 7 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 323/6) (sustained 323 cycles)
- **ALERT** `tuned_variants` — 295 non-stamps — atr_arm_uncomputable=295 (seen=10203 stamped=1473 skipped=8435) (streak 323/6) (sustained 323 cycles)
- **ALERT** `auto_dispatch` — 70 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=70) (streak 313/3) (sustained 313 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 59291117 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 26 arms current, none stalled; covering 2081/2081 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +1 but output +0 (streak 1/6) | 1 |
| atr_trail_live_arms | ok | 54 arms current, none stalled; covering 1085/1085 signals (100%) | 0 |
| auto_dispatch | violating | 70 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=70) (streak 313/3) | 313 |
| binance_ip_weight | ok | peak 99/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 76009.30 | 0 |
| candle_coverage | ok | 78/78 symbols with ≥20 15m candles, 78/78 updated within 45m [fresh=78; 74 Tier-1 futures + 4 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 957 dup bars, 0 undedupable; ws 0 out-of-order, 276 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 39 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +3 / upstream +57 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1848/1867 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 4 of 76 open dark rows are not being advanced (worst: ESPORTSUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 20/120) | 20 |
| dark_sar_arms | ok | no open arms; covering 1843/1862 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 22154030 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 323/6) | 323 |
| emission_controller | ok | last cycle 808s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×458]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 323/6) | 323 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 7/6) | 7 |
| firestore_read_budget | ok | 1,316 reads/day of 50,000 [engine 1,291, signing 25]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1136 incomplete, 2 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +3 | 0 |
| indicator_cache_key | ok | 145369 frozen value(s) avoided; 637685 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=5202 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +0 / upstream +3 | 0 |
| mover_admission_metadata | ok | 942 symbols known, 235 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 4 held, 4 with scan counts, 4 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2153 rows held, 3408749 evicted (sampled: execution:trigger_not_confirmed 290/1203956, execution:overextended 291/1064762, setup_compat:regime_STRONG_TREND 291/581859) | 0 |
| price_action_lane | ok | 604233 evaluated, 1036 emitted; layer1 1036 stamped / 0 blind; cooldown=84704, delta_opposed=49441, no_footprint=236829, no_opposing_target=516, no_sweep=186657, rr_below_floor=45050 | 0 |
| promoted_pair_integrity | ok | 4/4 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.19R over n=2208 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +0 / upstream +3 | 0 |
| sar_alignment_crosscheck | ok | 835/22914 disagreed (3.6%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +3 | 0 |
| sar_hold_arm | ok | 1868 held arms settled, 135 unscored, 48 still walking (44 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/35 unfetchable (3%); top cause: located bar does not contain the stamp; symbols: TIAUSDT | 0 |
| sar_live_arms | ok | 51 arms current, none stalled; covering 1084/1084 signals (100%) | 0 |
| sar_refresh_budget | ok | 9 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 435 records await one (34 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 206.36s, worst 258.77s over 7072 lifetime cycles; lifetime 365 over 60s, 83 over 120s (plus 2/1 during boot warm-up, not counted); recent 1/1 warn/kill breaches in 20/20 cycles; heartbeat age 2.11s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 300796 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (6.05s to run, worst 198.24s), 1139 overrun(s) of 6843 cycles, TTL 900s; slowest signals=5.28s, tickers=0.51s, pair_context=0.13s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=35, gate reads=0, withheld=35) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +26 / upstream +3 | 0 |
| structural_snap | ok | 6000/6000 measured, 31 blind, 0 levels moved (refusals: redetect_cooldown=1244) | 0 |
| structural_veto_lane | ok | 2347 stamped; 0 with no readable level book, 130 with clear air ahead, 1747 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +3 / upstream +57 | 0 |
| tuned_variants | violating | 295 non-stamps — atr_arm_uncomputable=295 (seen=10203 stamped=1473 skipped=8435) (streak 323/6) | 323 |
| unlock_shorts | ok | 14 open, 43 scheduled, calendar 9.7h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 25 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1599263`
- `Path funnel` emissions: `38`
- `Regime distribution` emissions: `38`
- `QUIET_SCALP_BLOCK` events: `263`
- `confidence_gate` events: `5502`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **15**
- Total REST-fallback activations: **10**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 10 | 7920 | 20497 | 39439 | 0 |
| futures_aggtrade | 2 | 5509 | 5509 | 10056 | 0 |
| futures_depth | 1 | 44907 | 44907 | 44907 | 0 |
| futures_liq | 2 | 4435 | 4435 | 5134 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 10 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=248994] state[populated=248994] buckets[many=248994] sources[none] quality[none]
- funding_rate: presence[absent=24263, present=224731] state[empty=24263, populated=224731] buckets[few=224731, none=24263] sources[none] quality[none]
- liquidation_clusters: presence[absent=170098, present=78896] state[empty=170098, populated=78896] buckets[few=64589, none=170098, some=14307] sources[none] quality[none]
- oi_snapshot: presence[absent=24263, present=224731] state[empty=24263, populated=224731] buckets[few=292, many=222261, none=24263, some=2178] sources[none] quality[none]
- order_book: presence[absent=85446, present=163548] state[populated=163548, unavailable=85446] buckets[few=163548, none=85446] sources[book_ticker=163548, unavailable=85446] quality[none=85446, top_of_book_only=163548]
- orderblocks: presence[absent=248994] state[empty=248994] buckets[none=248994] sources[measured_dark=248994] quality[none]
- recent_ticks: presence[present=248994] state[populated=248994] buckets[many=248994] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.23708963394165` sec
- Median create→first breach: `4880.210694074631` sec
- Median create→terminal: `4880.210743546486` sec
- Median first breach→terminal: `6.639957427978516e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 2.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.1}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 6 | 6 | 0.9552572497427048 | 1.0127630036396198 | 0.9069690325126538 | 0 | 4 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.531270507288174 | 3.0 | 0.8437568357627246 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1.3544366692389096 | 3.0 | 0.4514788897463032 | 0 | 1 |
| MEAN_REVERT | 1 | 1 | 1.0139866757513791 | 1.115085673909204 | 0.9093352192362064 | 0 | 1 |
| MOVER_AVWAP_SCALP | 5 | 5 | 1.6634694640861636 | 1.9805999477137781 | 0.8206192264923133 | 0 | 5 |
| MOVER_TREND_PULLBACK | 27 | 27 | 4.436627737540041 | 3.0 | 1.659636549435312 | 22 | 5 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.2988383414928242 | 1.4814316753249355 | 0.8584614148600933 | 0 | 6 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.6957785662930798 | 3.0 | 0.5652595220976933 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 6 | 6 | 33.3 | 33.3 | 33.3 | 0.0 | 0.2513 | 5831.62455701828 | 5833.5012085437775 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.5313 | 2207.0499460697174 | 2207.050043106079 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 164.33546495437622 | 164.33551216125488 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.1348 | 1137.8766169548035 | 1143.0771179199219 |
| MOVER_AVWAP_SCALP | 5 | 5 | 20.0 | 60.0 | 20.0 | 0.0 | -0.5592 | 25839.478691101074 | 25839.47871017456 |
| MOVER_TREND_PULLBACK | 27 | 27 | 25.9 | 59.3 | 25.9 | 0.0 | -1.0665 | 2785.7076420783997 | 2787.536164999008 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 0.0 | 66.7 | 0.0 | 0.0 | -0.9243 | 25877.000730991364 | 25877.000824451447 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1025.563206911087 | 1025.563225030899 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 503 | 7 | 235 | 0.0 | 0.0 | None | None | 268 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1656 | 40 | 1264 | 0.0 | 0.0 | 1025.563206911087 | 1025.563225030899 | 392 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-289`
- Gating Δ: `-16450`
- No-generation Δ: `-163191`
- Fast failures Δ: `1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.4169, "current_avg_pnl": 0.2513, "current_win_rate": 33.3, "previous_avg_pnl": -1.1656, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 2.4182, "current_avg_pnl": -0.5592, "current_win_rate": 20.0, "previous_avg_pnl": -2.9774, "previous_win_rate": 0.0, "win_rate_delta": 20.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.6527, "current_avg_pnl": -1.0665, "current_win_rate": 25.9, "previous_avg_pnl": 0.5862, "previous_win_rate": 44.0, "win_rate_delta": -18.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.39, "current_avg_pnl": -0.9243, "current_win_rate": 0.0, "previous_avg_pnl": 0.4657, "previous_win_rate": 28.6, "win_rate_delta": -28.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": -14, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 45, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2213.47, "median_terminal_delta_sec": -2214.25, "sl_rate_delta": 0.0, "win_rate_delta": -50.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
