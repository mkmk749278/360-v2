# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `44` sec (warning=False)
- Latest performance record age: `3101` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 24 | 24 | 24 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2714 | 2714 | 2301 | 15 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 19704 | 19722 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 18056 | 18063 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 17849 | 17230 | 818 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 18076 | 17901 | 209 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 18281 | 18255 | 51 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 15648 | 15657 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 18116 | 18139 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 18142 | 17463 | 1039 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 21216 | 22640 | 170 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 19729 | 17670 | 3518 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 18179 | 18182 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 18065 | 18075 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 17821 | 17727 | 119 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 18509 | 18228 | 404 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 17699 | 17766 | 26 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 15155 | 14712 | 536 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 15257 | 15208 | 86 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 19681 | 19697 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 15661 | 15625 | 56 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 652 | 652 | 577 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 249 | 249 | 80 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 2411 | 2411 | 2322 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 2 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2318 | 2318 | 1996 | 12 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 400 | 400 | 52 | 34 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 8091 | 8091 | 4521 | 187 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 453 | 453 | 175 | 46 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 845 | 845 | 751 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 61 | 61 | 30 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 327 | 327 | 251 | 12 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 23 | 23 | 9 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1290 | 1290 | 12 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=19722): breakout_not_found=11409, basic_filters_failed=4200, move_not_fresh=2726, breakout_stale=1116, retest_proximity_failed=242, volume_spike_missing=22, ema_alignment_reject=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=18063): cls_disabled_merged_into_lsr=18063
- **EVAL::DIVERGENCE_CONTINUATION** (total=17230): cvd_divergence_failed=7510, h1_trend_not_aligned=3848, basic_filters_failed=3752, ema_alignment_reject=1634, retest_proximity_failed=211, missing_fvg_or_orderblock=157, regime_blocked=118
- **EVAL::FAILED_AUCTION_RECLAIM** (total=17901): auction_not_detected=12442, basic_filters_failed=3627, reclaim_hold_failed=727, regime_blocked=657, tail_too_small=448
- **EVAL::FUNDING_EXTREME** (total=18255): funding_not_extreme=12441, basic_filters_failed=3621, missing_funding_rate=1100, ema_alignment_reject=670, rsi_reject=290, momentum_reject=71, cvd_divergence_failed=48, missing_fvg_or_orderblock=14
- **EVAL::LIQUIDATION_REVERSAL** (total=15657): cascade_threshold_not_met=11755, basic_filters_failed=3761, cvd_divergence_failed=85, rsi_reject=48, missing_fvg_or_orderblock=7, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=18139): no_ma_cross=14133, basic_filters_failed=3758, ma_cross_cooldown=199, ma_cross_htf_misaligned=49
- **EVAL::MEAN_REVERT** (total=17463): no_extension=15177, basic_filters_failed=2286
- **EVAL::MOVER_AVWAP_SCALP** (total=22640): no_mover_leg=8279, no_avwap_tag=7746, basic_filters_failed=4279, avwap_slope_against=1329, avwap_reclaim_no_volume=600, no_avwap_reclaim=401, anchor_too_recent=6
- **EVAL::MOVER_TREND_PULLBACK** (total=17670): mover_run_too_small=9009, basic_filters_failed=3860, no_reclaim=3784, no_pullback_tag=578, insufficient_candles=439
- **EVAL::OPENING_RANGE_BREAKOUT** (total=18182): feature_disabled=18182
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=18075): regime_blocked=13571, breakout_not_found=3156, basic_filters_failed=678, adx_reject=638, ema_alignment_reject=32
- **EVAL::QUIET_COMPRESSION_BREAK** (total=17727): compression_not_detected=5868, regime_blocked=5100, breakout_not_detected=3478, basic_filters_failed=2944, volume_confirmation_failed=296, rsi_reject=37, missing_fvg_or_orderblock=4
- **EVAL::RANGE_FADE** (total=18228): no_range_edge=15928, basic_filters_failed=2207, insufficient_candles=93
- **EVAL::SR_FLIP_RETEST** (total=17766): flip_close_not_confirmed=12298, basic_filters_failed=3620, regime_blocked=652, long_break_volume_thin=514, retest_out_of_zone=298, h1_break_not_confirmed=219, reclaim_hold_failed=112, long_acceptance_not_held=36, whipsaw_flip=11, ema_alignment_reject=4, missing_fvg_or_orderblock=1, wick_quality_failed=1
- **EVAL::STANDARD** (total=14712): momentum_reject=5308, adx_reject=3245, sweeps_not_detected=2213, basic_filters_failed=1773, macd_reject=1285, ema_alignment_reject=488, htf_poi_unanchored=377, invalid_sl_geometry=13, rsi_reject=8, mtf_reject=2
- **EVAL::TREND_PULLBACK** (total=15208): h1_trend_not_aligned=4385, h1_pullback_not_confirmed=3049, ema_alignment_reject=2504, basic_filters_failed=1772, no_ema_reclaim_close=915, ema_not_tested_prev=903, body_conviction_fail=649, rsi_reject=466, prev_already_below_emas=142, no_prev_low_break=125, regime_blocked=94, prev_already_above_emas=90, no_prev_high_break=45, momentum_flat=30, missing_fvg_or_orderblock=18, momentum_reject=11, ema21_not_tagged=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=19697): breakout_not_found=12580, basic_filters_failed=4200, move_not_fresh=1747, breakout_stale=823, retest_proximity_failed=298, volume_spike_missing=39, ema_alignment_reject=6, missing_fvg_or_orderblock=3, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=15625): momentum_reject=11566, recent_ticks_insufficient=3251, basic_filters_failed=807, rsi_reject=1

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=6): execution:overextended=6
- **DIVERGENCE_CONTINUATION** (total=50): setup_compat:regime_VOLATILE_UNSUITABLE=50
- **FAILED_AUCTION_RECLAIM** (total=124): execution:overextended=59, setup_compat:regime_STRONG_TREND=44, context_floor=19, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **FUNDING_EXTREME_SIGNAL** (total=195): execution:trigger_not_confirmed=188, context_floor=7
- **LIQUIDITY_SWEEP_REVERSAL** (total=613): execution:overextended=325, execution:trigger_not_confirmed=191, setup_compat:regime_STRONG_TREND=97
- **MA_CROSS_TREND_SHIFT** (total=3): setup_compat:regime_DIRTY_RANGE=2, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=830): setup_compat:regime_STRONG_TREND=443, setup_compat:regime_WEAK_TREND=281, execution:overextended=78, entry_quality=28
- **MOVER_AVWAP_SCALP** (total=336): execution:overextended=178, execution:trigger_not_confirmed=87, entry_quality=71
- **MOVER_TREND_PULLBACK** (total=5137): execution:overextended=2491, execution:trigger_not_confirmed=1776, entry_quality=870
- **QUIET_COMPRESSION_BREAK** (total=33): execution:trigger_not_confirmed=33
- **RANGE_FADE** (total=299): setup_compat:regime_WEAK_TREND=128, setup_compat:regime_VOLATILE_UNSUITABLE=87, setup_compat:regime_STRONG_TREND=58, context_edge=13, execution:overextended=13
- **TREND_PULLBACK_EMA** (total=303): setup_compat:regime_CLEAN_RANGE=225, setup_compat:regime_DIRTY_RANGE=61, entry_quality=13, setup_compat:regime_VOLATILE_UNSUITABLE=4
- **VOLUME_SURGE_BREAKOUT** (total=31): execution:overextended=22, context_floor=9
- **WHALE_MOMENTUM** (total=1268): execution:trigger_not_confirmed=1268

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 37725 | 39.2% |
| QUIET | 27594 | 28.7% |
| TRENDING_DOWN | 15895 | 16.5% |
| TRENDING_UP | 10208 | 10.6% |
| VOLATILE | 4796 | 5.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **191**
- Average confidence gap to threshold: **13.53** (samples=191) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=14, SOLUSDT=13, ZECUSDT=12, DOTUSDT=12, ETHUSDT=9, BCHUSDT=9, BULLAUSDT=9, FILUSDT=8, WALUSDT=8, HYPEUSDT=8

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 28 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 6 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 128 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 12 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 15 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 8 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 34 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 4 |
| MEAN_REVERT | kept | min_confidence_pass | 32 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 112 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 181 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 441 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 31 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1637 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 117 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 255 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 7 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 7 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 12 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 50 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 11 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 75.50 | 65.00 | -10.50 | 20.80 | 18.20 | 20.00 | 4.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 34 | 55.32 | 64.85 | 9.53 | 20.24 | 19.81 | 17.01 | 0.32 | 12.18 |
| DIVERGENCE_CONTINUATION | kept | 128 | 70.13 | 65.00 | -5.13 | 20.25 | 19.70 | 17.83 | 0.49 | 0.56 |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 55.20 | 63.41 | 8.21 | 19.85 | 18.29 | 20.00 | 3.66 | 6.01 |
| FAILED_AUCTION_RECLAIM | kept | 15 | 70.83 | 65.00 | -5.83 | 19.68 | 19.91 | 20.00 | 1.93 | 2.80 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 50.64 | 63.67 | 13.03 | 20.80 | 14.06 | 18.00 | 3.22 | 3.46 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 51.57 | 65.00 | 13.43 | 20.67 | 17.87 | 17.00 | 0.67 | 18.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 69.85 | 65.00 | -4.85 | 20.91 | 18.61 | 18.12 | 1.76 | -0.18 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.30 | 65.00 | -3.30 | 21.20 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 4 | 53.42 | 60.75 | 7.33 | 20.82 | 16.65 | 13.53 | 0.00 | 1.78 |
| MEAN_REVERT | kept | 32 | 69.73 | 65.00 | -4.73 | 20.11 | 15.03 | 18.31 | 0.00 | 0.15 |
| MOVER_AVWAP_SCALP | filtered | 112 | 55.68 | 64.45 | 8.77 | 20.64 | 15.44 | 15.80 | 3.66 | 6.55 |
| MOVER_AVWAP_SCALP | kept | 181 | 76.49 | 65.00 | -11.49 | 20.08 | 16.08 | 15.80 | 4.09 | 1.39 |
| MOVER_TREND_PULLBACK | filtered | 472 | 57.84 | 64.15 | 6.31 | 19.94 | 18.88 | 15.80 | 4.50 | 12.06 |
| MOVER_TREND_PULLBACK | kept | 1637 | 76.75 | 65.00 | -11.75 | 20.30 | 18.71 | 15.80 | 4.55 | 0.78 |
| QUIET_COMPRESSION_BREAK | filtered | 124 | 50.14 | 64.87 | 14.73 | 20.25 | 19.92 | 20.00 | 0.00 | 9.26 |
| QUIET_COMPRESSION_BREAK | kept | 255 | 75.52 | 65.00 | -10.52 | 20.05 | 19.79 | 20.00 | 0.00 | -2.18 |
| RANGE_FADE | kept | 1 | 66.30 | 65.00 | -1.30 | 20.40 | 18.60 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 62.00 | 65.00 | 3.00 | 19.57 | 20.00 | 15.20 | 1.00 | 3.00 |
| SR_FLIP_RETEST | kept | 7 | 68.60 | 65.00 | -3.60 | 20.43 | 20.00 | 18.13 | 1.43 | 0.86 |
| TREND_PULLBACK_EMA | filtered | 17 | 57.14 | 65.00 | 7.86 | 20.85 | 19.41 | 18.62 | 4.68 | 7.65 |
| TREND_PULLBACK_EMA | kept | 50 | 79.82 | 65.00 | -14.82 | 20.54 | 19.76 | 17.55 | 4.83 | -1.22 |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 52.41 | 60.82 | 8.41 | 20.07 | 15.01 | 20.00 | 3.64 | 12.61 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 71.70 | 65.00 | -6.70 | 20.23 | 17.70 | 20.00 | 4.83 | 8.37 |
| WHALE_MOMENTUM | filtered | 19 | 50.21 | 65.00 | 14.79 | 21.00 | 14.95 | 17.00 | 0.00 | 13.41 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 75.50 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 8.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 34 | 55.32 | 23.35 | 13.59 | 5.56 | 12.21 | 5.76 | 7.76 | 0.32 |
| DIVERGENCE_CONTINUATION | kept | 128 | 70.13 | 23.06 | 15.27 | 7.48 | 12.72 | 5.25 | 8.58 | 0.49 |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 55.20 | 23.82 | 16.18 | 4.23 | 12.09 | 4.14 | 5.27 | 3.66 |
| FAILED_AUCTION_RECLAIM | kept | 15 | 70.83 | 21.27 | 15.87 | 7.20 | 14.00 | 5.87 | 7.49 | 1.93 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 50.64 | 25.00 | 8.00 | 4.00 | 14.22 | 8.00 | 3.32 | 3.22 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 51.57 | 22.33 | 14.00 | 7.00 | 15.00 | 7.33 | 3.63 | 0.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 69.85 | 22.06 | 14.71 | 6.09 | 13.09 | 6.12 | 6.03 | 1.76 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.30 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 7.30 | 0.00 |
| MEAN_REVERT | filtered | 4 | 53.42 | 16.50 | 18.00 | 8.25 | 12.00 | 8.75 | 5.20 | 0.00 |
| MEAN_REVERT | kept | 32 | 69.73 | 21.25 | 17.50 | 7.59 | 12.09 | 6.44 | 5.01 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 112 | 55.68 | 18.34 | 18.16 | 8.92 | 12.76 | 5.18 | 5.80 | 3.66 |
| MOVER_AVWAP_SCALP | kept | 181 | 76.49 | 19.19 | 18.07 | 9.70 | 13.24 | 5.90 | 8.42 | 4.09 |
| MOVER_TREND_PULLBACK | filtered | 472 | 57.84 | 17.77 | 18.06 | 7.91 | 13.48 | 5.73 | 8.12 | 4.50 |
| MOVER_TREND_PULLBACK | kept | 1637 | 76.75 | 19.20 | 18.04 | 8.14 | 13.28 | 5.67 | 8.94 | 4.55 |
| QUIET_COMPRESSION_BREAK | filtered | 124 | 50.14 | 17.90 | 17.77 | 11.42 | 14.07 | 6.29 | 4.32 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 255 | 75.52 | 18.54 | 17.70 | 11.42 | 14.13 | 5.76 | 8.05 | 0.00 |
| RANGE_FADE | kept | 1 | 66.30 | 17.00 | 14.00 | 12.00 | 15.00 | 5.00 | 3.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 62.00 | 17.00 | 18.00 | 3.00 | 11.00 | 5.00 | 10.00 | 1.00 |
| SR_FLIP_RETEST | kept | 7 | 68.60 | 19.29 | 18.00 | 4.29 | 13.43 | 5.00 | 8.46 | 1.43 |
| TREND_PULLBACK_EMA | filtered | 17 | 57.14 | 12.65 | 18.00 | 9.26 | 14.88 | 7.65 | 7.19 | 4.68 |
| TREND_PULLBACK_EMA | kept | 50 | 79.82 | 19.14 | 18.00 | 7.80 | 14.66 | 7.20 | 8.83 | 4.83 |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 52.41 | 17.00 | 16.91 | 14.45 | 13.18 | 5.00 | 5.75 | 3.64 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 71.70 | 19.67 | 16.67 | 14.00 | 11.00 | 5.00 | 8.90 | 4.83 |
| WHALE_MOMENTUM | filtered | 19 | 50.21 | 25.00 | 8.00 | 12.47 | 13.42 | 6.37 | 3.88 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 75.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 34 | 55.32 | 0.00 | 0.00 | 0.00 | 0.00 | 3.18 | 0.00 | 0.00 | 0.00 | **3.18** |
| DIVERGENCE_CONTINUATION | kept | 128 | 70.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **0.09** |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 55.20 | 0.00 | 0.00 | 0.00 | 0.00 | 1.96 | 0.00 | 0.00 | 0.00 | **1.96** |
| FAILED_AUCTION_RECLAIM | kept | 15 | 70.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 50.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 51.57 | 0.00 | 0.00 | 0.00 | 0.00 | 18.40 | 0.00 | 0.00 | 0.00 | **18.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 34 | 69.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 4 | 53.42 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 32 | 69.73 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.15** |
| MOVER_AVWAP_SCALP | filtered | 112 | 55.68 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.49 | **2.29** |
| MOVER_AVWAP_SCALP | kept | 181 | 76.49 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | **1.25** |
| MOVER_TREND_PULLBACK | filtered | 472 | 57.84 | 0.00 | 0.00 | 0.26 | 0.00 | 1.23 | 0.02 | 0.00 | 0.43 | **1.94** |
| MOVER_TREND_PULLBACK | kept | 1637 | 76.75 | 0.00 | 0.00 | 0.11 | 0.00 | 0.21 | 0.00 | 0.00 | 0.03 | **0.35** |
| QUIET_COMPRESSION_BREAK | filtered | 124 | 50.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.62 | 0.00 | 0.00 | 6.70 | **7.32** |
| QUIET_COMPRESSION_BREAK | kept | 255 | 75.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **0.22** |
| RANGE_FADE | kept | 1 | 66.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 7 | 62.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 7 | 68.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 17 | 57.14 | 0.00 | 0.00 | 0.00 | 0.00 | 6.35 | 0.00 | 0.00 | 0.00 | **6.35** |
| TREND_PULLBACK_EMA | kept | 50 | 79.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 11 | 52.41 | 0.00 | 0.00 | 2.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.62** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 71.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 19 | 50.21 | 0.00 | 0.00 | 0.00 | 0.00 | 3.41 | 0.00 | 0.00 | 0.00 | **3.41** |

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
- Outcomes recorded: **143358 held of 307463 seen** across 21 strategies; 3219 cells past the sample floor; **1342 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 33640 | 190/33450/0 | 49% | -0.07 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 17358 | 18/17340/0 | 52% | +0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16587 | 1/16586/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 12347 | 6/12341/0 | 45% | -0.10 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (+1.32R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 9992 | 29/9963/0 | 35% | -0.31 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| QUIET_COMPRESSION_BREAK | 9789 | 0/9789/0 | 47% | -0.08 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.21R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 6047 | 2/6045/0 | 47% | -0.26 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 5373 | 0/0/5373 | 43% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.56R) | LONDON/MARKUP/CASCADE/BTC_RISING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 5176 | 11/5165/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 4895 | 0/0/4895 | 38% | +0.00 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (+0.62R) | OVERLAP/QUIET/NORMAL/BTC_RISING (-1.28R) |
| MEAN_REVERT | 4876 | 4/4872/0 | 68% | +0.31 | NY/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.28R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-1.54R) |
| SHADOW_FUNDING_FADE | 4482 | 0/0/4482 | 36% | -0.37 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.20R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 4113 | 0/4113/0 | 33% | -0.36 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.60R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2648 | 19/2629/0 | 41% | +0.03 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2560 | 4/2556/0 | 31% | -0.47 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.29R) |
| WHALE_MOMENTUM | 2092 | 0/2092/0 | 46% | -0.27 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.89R) |
| SHADOW_CASCADE_REVERSAL | 611 | 0/0/611 | 48% | -0.17 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.03R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-2.04R) |
| BREAKDOWN_SHORT | 531 | 11/520/0 | 45% | +0.04 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 73 | 0/73/0 | 85% | +0.69 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 40 | 1/39/0 | 38% | -0.39 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.60R (n=28, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.60R (n=28, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `SHADOW_CASCADE_REVERSAL @ OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL` -2.04R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 136 | 35% / -0.41R | 136 | 57% / -0.11R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 276 | 42% / -0.32R | 276 | 48% / -0.12R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 705 | 39% / -0.21R | 705 | 43% / -0.09R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 2783 | 46% / -0.20R | 2783 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 1015 | 47% / -0.12R | 1015 | 52% / -0.06R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4396 | 51% / -0.07R | 4396 | 54% / -0.01R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 797 | 51% / -0.17R | 797 | 55% / -0.11R | +0.05 | **ATR** |
| MA_CROSS_TREND_SHIFT | 17 | 35% / -0.25R | 17 | 35% / -0.20R | +0.05 | **ATR** |
| WHALE_MOMENTUM | 171 | 51% / -0.24R | 171 | 50% / -0.28R | -0.04 | **FIXED** |
| RANGE_FADE | 282 | 23% / -0.56R | 282 | 26% / -0.53R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1623 | 45% / -0.13R | 1623 | 45% / -0.16R | -0.03 | **FIXED** |
| MEAN_REVERT | 550 | 53% / -0.03R | 550 | 49% / -0.00R | +0.02 | **ATR** |
| BREAKDOWN_SHORT | 23 | 35% / -0.20R | 23 | 35% / -0.19R | +0.01 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 94 | 40% / -0.05R | 94 | 51% / -0.05R | -0.01 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2338 | 47% / -0.11R | 2338 | 47% / -0.11R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 10 | 60% / +0.10R | 10 | 60% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6455 | 30% | -0.18R | 287 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 695 | 42% | -0.10R | 140 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 44 | 57% | +0.00R | 24 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1245 | 29% / -1.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 33 | 30% / -0.35R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5479 | 40% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1053 | 32% / -0.54R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 114 | 23% / -0.83R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 881 | 33% / -1.26R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1171 | 38% / -0.13R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 452 | 45% / -0.76R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 165 | 30% / -1.06R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 334 | 32% / -0.56R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 815 | 31% / -0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 19% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 275 | 44% / -0.12R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 103 | 40% / -0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 25% / -0.67R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 58 | 41% / -0.28R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 47 · alerting: **4** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 46/92 unfetchable (50%); top cause: gap or duplicate bar in the 15m window; symbols: BSBUSDT, CAPUSDT, COWUSDT, CYSUSDT, FETUSDT +12 more (streak 11/6) (sustained 11 cycles)
- **ALERT** `cohort_edge_gate` — all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 13 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 11/6) (sustained 11 cycles)
- **ALERT** `edge_reconciliation` — MOVER_AVWAP_SCALP realized−counterfactual=+0.44R (bound 0.3) (streak 11/6) (sustained 11 cycles)
- **ALERT** `mean_revert_emission` — 344 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.31R over n=4872, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 11/6) (sustained 11 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 1450241 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 6 arms current, none stalled; covering 133/133 signals (100%) | 0 |
| auto_dispatch | ok | attempts=3 fanouts=3 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 63084.00 | 0 |
| candle_coverage | ok | 87/90 symbols with ≥20 15m candles, 87/90 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 976 dup bars, 0 undedupable; ws 0 out-of-order, 222 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 13 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 11/6) | 11 |
| context_emission_policy | ok | output +13 / upstream +9 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1141/1153 signals (99%) | 0 |
| dark_promotion_rules | ok | 2 rule(s) armed, 0 promoted today | 0 |
| dark_resolution | violating | 2 of 97 open dark rows are not being advanced (worst: FARTCOINUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 11/120) | 11 |
| dark_sar_arms | ok | no open arms; covering 1138/1150 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 518089 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.44R (bound 0.3) (streak 11/6) | 11 |
| emission_controller | ok | last cycle 1s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4214 stamps (MEAN_REVERT=1300, MOVER_AVWAP_SCALP=157, MOVER_TREND_PULLBACK=2531, RANGE_FADE=95, TREND_PULLBACK_EMA=131), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +7 / upstream +127 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 344 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.31R over n=4872, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 11/6) | 11 |
| mean_revert_path | ok | output +39 / upstream +127 | 0 |
| mover_admission_metadata | ok | 865 symbols known, 163 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 12 held, 12 with scan counts, 12 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3010 rows held, 549623 evicted (sampled: execution:overextended 400/203022, execution:trigger_not_confirmed 400/189323, setup_compat:regime_STRONG_TREND 400/66067) | 0 |
| price_action_lane | ok | 10866 evaluated, 50 emitted; layer1 50 stamped / 0 blind; cooldown=1447, delta_opposed=1037, no_footprint=3267, no_opposing_target=32, no_sweep=4161, rr_below_floor=872 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 47 detections since last progress | 0 |
| range_fade_path | ok | output +9 / upstream +127 | 0 |
| sar_alignment_crosscheck | ok | 21/900 disagreed (2.3%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +127 | 0 |
| sar_hold_arm | ok | 231 held arms settled, 47 unscored, 6 still walking (2 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 46/92 unfetchable (50%); top cause: gap or duplicate bar in the 15m window; symbols: BSBUSDT, CAPUSDT, COWUSDT, CYSUSDT, FETUSDT +12 more (streak 11/6) | 11 |
| sar_live_arms | ok | 6 arms current, none stalled; covering 142/142 signals (100%) | 0 |
| sar_refresh_budget | ok | 8 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 45 still mid-window | 0 |
| setup_tf_resolver | ok | 5719 resolutions, 3520 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +34 / upstream +127 | 0 |
| structural_snap | ok | 4188/4188 measured, 23 blind, 0 levels moved (refusals: redetect_cooldown=16) | 0 |
| structural_veto_lane | ok | 68 stamped; 0 with no readable level book, 2 with clear air ahead, 40 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +127 / upstream +9 | 0 |
| tuned_variants | violating | 27 non-stamps — atr_arm_uncomputable=27 (seen=223 stamped=63 skipped=133) (streak 5/6) | 5 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `85955`
- `Path funnel` emissions: `11`
- `Regime distribution` emissions: `11`
- `QUIET_SCALP_BLOCK` events: `191`
- `confidence_gate` events: `3180`
- `free_channel_post` events: `19`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **45**
- Total REST-fallback activations: **12**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 15 | 47922 | 65820 | 80567 | 0 |
| futures_aggtrade | 6 | 42836 | 52131 | 53202 | 0 |
| futures_depth | 20 | 55492 | 78663 | 81567 | 0 |
| futures_liq | 4 | 14252 | 16969 | 24970 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 12 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **19**

| Source | Count |
|---|---:|
| signal_close | 11 |
| regime_shift | 8 |

- By severity: HIGH=19

## Dependency readiness
- cvd: presence[present=77503] state[populated=77503] buckets[many=77463, some=40] sources[none] quality[none]
- funding_rate: presence[absent=13506, present=63997] state[empty=13506, populated=63997] buckets[few=63997, none=13506] sources[none] quality[none]
- liquidation_clusters: presence[absent=50365, present=27138] state[empty=50365, populated=27138] buckets[few=22503, none=50365, some=4635] sources[none] quality[none]
- oi_snapshot: presence[absent=11726, present=65777] state[empty=11726, populated=65777] buckets[few=511, many=64079, none=11726, some=1187] sources[none] quality[none]
- order_book: presence[absent=42691, present=34812] state[populated=34812, unavailable=42691] buckets[few=34812, none=42691] sources[book_ticker=34812, unavailable=42691] quality[none=42691, top_of_book_only=34812]
- orderblocks: presence[absent=77503] state[empty=77503] buckets[none=77503] sources[measured_dark=77503] quality[none]
- recent_ticks: presence[present=77503] state[populated=77503] buckets[many=77503] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `23.842551946640015` sec
- Median create→first breach: `2780.1813929080963` sec
- Median create→terminal: `2786.3068010807037` sec
- Median first breach→terminal: `4.491970062255859` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 9.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 9.1}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MEAN_REVERT | 1 | 1 | 2.0207956600361725 | 3.0 | 0.6735985533453909 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.128910463861922 | 2.508010164622693 | 0.8488444320887341 | 0 | 1 |
| MOVER_TREND_PULLBACK | 9 | 9 | 5.01781248592655 | 3.0 | 1.6726041619755165 | 9 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2949.900181055069 | 2950.5716660022736 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 8398.27059006691 | 8398.522722005844 |
| MOVER_TREND_PULLBACK | 9 | 9 | 0.0 | 44.4 | 0.0 | 0.0 | 0.4703 | 2171.7263247966766 | 2172.3779718875885 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 61 | 2 | 30 | 0.0 | 0.0 | None | None | 31 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 327 | 12 | 251 | 0.0 | 0.0 | None | None | 76 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `282`
- Gating Δ: `11804`
- No-generation Δ: `308287`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.2211, "current_avg_pnl": 0.4703, "current_win_rate": 0.0, "previous_avg_pnl": 1.6914, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 31, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 11, "geometry_changed_delta": 0, "geometry_preserved_delta": 65, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
