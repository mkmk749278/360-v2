# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `4406` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 51 | 51 | 51 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6880 | 6880 | 6411 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 47172 | 47206 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 49997 | 49997 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 49611 | 47786 | 2188 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50036 | 49475 | 667 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 50581 | 50434 | 180 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 39444 | 39460 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50143 | 50170 | 18 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 50193 | 48881 | 1945 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 52630 | 58537 | 561 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 47219 | 40007 | 12553 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 50322 | 50322 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50004 | 50025 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 49566 | 49480 | 124 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 50833 | 49051 | 2332 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 49271 | 49395 | 127 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 38325 | 35974 | 2695 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 38676 | 38560 | 188 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 47119 | 47147 | 19 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 39465 | 39495 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2989 | 2989 | 2784 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 566 | 566 | 276 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 20 | 20 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14524 | 14524 | 14274 | 6 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 33 | 33 | 25 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 4968 | 4968 | 3114 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1354 | 1354 | 827 | 22 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 33121 | 33121 | 21962 | 392 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 666 | 666 | 552 | 13 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5424 | 5424 | 5024 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 477 | 477 | 293 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1038 | 1038 | 893 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 39 | 39 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=47206): breakout_not_found=24967, basic_filters_failed=10892, move_not_fresh=8024, breakout_stale=2595, retest_proximity_failed=579, volume_spike_missing=130, move_exhausted=19
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=49997): cls_disabled_merged_into_lsr=49997
- **EVAL::DIVERGENCE_CONTINUATION** (total=47786): cvd_divergence_failed=20494, h1_trend_not_aligned=14375, basic_filters_failed=9103, ema_alignment_reject=3259, missing_fvg_or_orderblock=285, retest_proximity_failed=270
- **EVAL::FAILED_AUCTION_RECLAIM** (total=49475): auction_not_detected=33856, basic_filters_failed=8525, reclaim_hold_failed=2875, regime_blocked=2316, tail_too_small=1888, rsi_reject=15
- **EVAL::FUNDING_EXTREME** (total=50434): funding_not_extreme=38977, basic_filters_failed=9260, ema_alignment_reject=1264, rsi_reject=516, cvd_divergence_failed=161, momentum_reject=151, missing_funding_rate=95, missing_fvg_or_orderblock=10
- **EVAL::LIQUIDATION_REVERSAL** (total=39460): cascade_threshold_not_met=30009, basic_filters_failed=9072, cvd_divergence_failed=213, rsi_reject=154, missing_fvg_or_orderblock=9, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50170): no_ma_cross=39051, basic_filters_failed=9114, ma_cross_cooldown=1148, ma_cross_htf_misaligned=857
- **EVAL::MEAN_REVERT** (total=48881): no_extension=42565, basic_filters_failed=6316
- **EVAL::MOVER_AVWAP_SCALP** (total=58537): no_avwap_tag=31947, basic_filters_failed=11074, no_mover_leg=10156, avwap_slope_against=2659, avwap_reclaim_no_volume=1636, no_avwap_reclaim=1009, anchor_too_recent=56
- **EVAL::MOVER_TREND_PULLBACK** (total=40007): mover_run_too_small=15576, no_reclaim=12238, basic_filters_failed=10990, no_pullback_tag=1203
- **EVAL::OPENING_RANGE_BREAKOUT** (total=50322): feature_disabled=50322
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50025): regime_blocked=28898, breakout_not_found=16809, basic_filters_failed=2868, adx_reject=1372, ema_alignment_reject=73, rsi_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=49480): regime_blocked=23310, compression_not_detected=15550, basic_filters_failed=5650, breakout_not_detected=4512, volume_confirmation_failed=420, missing_fvg_or_orderblock=24, rsi_reject=14
- **EVAL::RANGE_FADE** (total=49051): no_range_edge=42732, basic_filters_failed=6319
- **EVAL::SR_FLIP_RETEST** (total=49395): flip_close_not_confirmed=34072, basic_filters_failed=8507, regime_blocked=2308, h1_break_not_confirmed=1894, long_break_volume_thin=1330, retest_out_of_zone=677, reclaim_hold_failed=295, long_acceptance_not_held=132, ema_alignment_reject=81, whipsaw_flip=63, wick_quality_failed=24, missing_fvg_or_orderblock=12
- **EVAL::STANDARD** (total=35974): momentum_reject=13688, adx_reject=6942, basic_filters_failed=4330, sweeps_not_detected=3723, macd_reject=3332, ema_alignment_reject=3282, htf_poi_unanchored=608, invalid_sl_geometry=40, rsi_reject=29
- **EVAL::TREND_PULLBACK** (total=38560): h1_trend_not_aligned=13591, h1_pullback_not_confirmed=11949, basic_filters_failed=3488, ema_alignment_reject=3393, no_ema_reclaim_close=1880, ema_not_tested_prev=1792, body_conviction_fail=1040, rsi_reject=671, prev_already_below_emas=333, no_prev_low_break=224, momentum_flat=72, prev_already_above_emas=46, ema21_not_tagged=40, missing_fvg_or_orderblock=36, no_prev_high_break=4, momentum_reject=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=47147): breakout_not_found=29590, basic_filters_failed=10890, move_not_fresh=3980, breakout_stale=1866, retest_proximity_failed=634, volume_spike_missing=157, move_exhausted=18, missing_fvg_or_orderblock=12
- **EVAL::WHALE_MOMENTUM** (total=39495): momentum_reject=24301, recent_ticks_insufficient=12055, basic_filters_failed=3139

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=9): execution:overextended=9
- **DIVERGENCE_CONTINUATION** (total=233): setup_compat:regime_VOLATILE_UNSUITABLE=227, setup_compat:regime_BREAKOUT_EXPANSION=6
- **FAILED_AUCTION_RECLAIM** (total=1079): setup_compat:regime_STRONG_TREND=602, execution:overextended=461, context_floor=15, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **FUNDING_EXTREME_SIGNAL** (total=494): execution:trigger_not_confirmed=487, context_floor=7
- **LIQUIDATION_REVERSAL** (total=20): execution:trigger_not_confirmed=20
- **LIQUIDITY_SWEEP_REVERSAL** (total=3675): setup_compat:regime_STRONG_TREND=1505, execution:trigger_not_confirmed=1459, execution:overextended=711
- **MA_CROSS_TREND_SHIFT** (total=25): setup_compat:regime_CLEAN_RANGE=13, execution:trigger_not_confirmed=6, setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:overextended=1
- **MEAN_REVERT** (total=3920): setup_compat:regime_WEAK_TREND=1899, setup_compat:regime_STRONG_TREND=1618, execution:overextended=401, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=777): execution:overextended=671, execution:trigger_not_confirmed=58, entry_quality=48
- **MOVER_TREND_PULLBACK** (total=9349): execution:trigger_not_confirmed=5432, execution:overextended=2489, entry_quality=1428
- **QUIET_COMPRESSION_BREAK** (total=30): execution:trigger_not_confirmed=30
- **RANGE_FADE** (total=3852): setup_compat:regime_STRONG_TREND=2053, setup_compat:regime_WEAK_TREND=1347, execution:overextended=295, setup_compat:regime_VOLATILE_UNSUITABLE=125, context_edge=30, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=821): setup_compat:regime_CLEAN_RANGE=520, setup_compat:regime_DIRTY_RANGE=259, entry_quality=22, setup_compat:regime_VOLATILE_UNSUITABLE=20

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 78143 | 28.6% |
| RANGING | 73728 | 27.0% |
| TRENDING_DOWN | 63648 | 23.3% |
| TRENDING_UP | 43868 | 16.1% |
| VOLATILE | 13862 | 5.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **298**
- Average confidence gap to threshold: **12.88** (samples=298) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AAVEUSDT=39, BULLAUSDT=22, TAOUSDT=21, TIAUSDT=18, ONDOUSDT=17, HYPEUSDT=16, DOGEUSDT=16, AVAXUSDT=15, SOLUSDT=15, LINKUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 64 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 51 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 43 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 29 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 17 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 85 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 10 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 9 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 136 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 123 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2099 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 172 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3509 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 72 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 7 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 20 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 33 |
| SR_FLIP_RETEST | filtered | min_confidence | 15 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 37 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 41 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 53 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 31 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 69 | 57.48 | 64.10 | 6.62 | 20.42 | 19.83 | 17.47 | 2.54 | 10.51 |
| DIVERGENCE_CONTINUATION | kept | 51 | 70.25 | 65.00 | -5.25 | 19.97 | 19.95 | 18.54 | 0.20 | 0.33 |
| FAILED_AUCTION_RECLAIM | filtered | 47 | 47.49 | 63.13 | 15.64 | 20.07 | 18.06 | 20.00 | 1.38 | 7.60 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 61.80 | 65.00 | 3.20 | 20.40 | 15.40 | 20.00 | 2.50 | 8.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 49.61 | 61.00 | 11.39 | 19.52 | 14.80 | 16.76 | 3.17 | 8.21 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.30 | 65.00 | 1.70 | 21.10 | 14.00 | 14.50 | 3.00 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 17 | 46.47 | 10.00 | -36.47 | 19.05 | 8.00 | 17.76 | 6.00 | 11.61 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 85 | 50.78 | 64.39 | 13.61 | 20.09 | 19.34 | 18.41 | 1.74 | 6.94 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 69.92 | 65.00 | -4.92 | 20.46 | 19.24 | 19.91 | 0.70 | 2.48 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.00 | 65.00 | -7.00 | 21.77 | 19.40 | 15.80 | 0.00 | 1.67 |
| MEAN_REVERT | filtered | 1 | 64.50 | 65.00 | 0.50 | 20.50 | 14.00 | 17.50 | 0.00 | 4.80 |
| MEAN_REVERT | kept | 9 | 67.43 | 65.00 | -2.43 | 20.86 | 15.87 | 16.31 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 138 | 53.15 | 64.97 | 11.82 | 19.30 | 16.06 | 15.80 | 4.11 | 25.17 |
| MOVER_AVWAP_SCALP | kept | 123 | 77.86 | 65.00 | -12.86 | 20.37 | 17.06 | 15.80 | 4.54 | 4.00 |
| MOVER_TREND_PULLBACK | filtered | 2271 | 54.51 | 64.20 | 9.69 | 20.14 | 19.24 | 15.80 | 4.02 | 17.38 |
| MOVER_TREND_PULLBACK | kept | 3509 | 75.98 | 65.00 | -10.98 | 20.59 | 19.18 | 15.80 | 4.10 | 1.77 |
| QUIET_COMPRESSION_BREAK | filtered | 79 | 41.84 | 65.00 | 23.16 | 21.02 | 19.36 | 20.00 | 0.00 | 15.29 |
| QUIET_COMPRESSION_BREAK | kept | 20 | 77.94 | 65.00 | -12.94 | 20.66 | 19.69 | 20.00 | 0.00 | 2.49 |
| SR_FLIP_RETEST | filtered | 48 | 55.37 | 65.00 | 9.63 | 20.79 | 20.00 | 15.40 | 2.24 | 14.09 |
| SR_FLIP_RETEST | kept | 37 | 70.78 | 65.00 | -5.78 | 20.70 | 20.00 | 19.14 | 2.61 | 1.39 |
| TREND_PULLBACK_EMA | filtered | 51 | 55.30 | 65.00 | 9.70 | 19.45 | 19.96 | 18.49 | 4.99 | 19.98 |
| TREND_PULLBACK_EMA | kept | 53 | 81.32 | 65.00 | -16.32 | 20.73 | 19.80 | 17.65 | 4.93 | 1.39 |
| VOLUME_SURGE_BREAKOUT | filtered | 31 | 46.30 | 65.00 | 18.70 | 20.45 | 17.95 | 20.00 | 5.00 | 20.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 69 | 57.48 | 22.91 | 13.36 | 3.78 | 12.26 | 5.29 | 7.83 | 2.54 |
| DIVERGENCE_CONTINUATION | kept | 51 | 70.25 | 22.65 | 17.61 | 4.35 | 11.98 | 5.24 | 9.15 | 0.20 |
| FAILED_AUCTION_RECLAIM | filtered | 47 | 47.49 | 19.04 | 14.77 | 8.04 | 15.02 | 6.00 | 5.83 | 1.38 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 61.80 | 25.00 | 18.00 | 3.00 | 11.00 | 5.00 | 5.30 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 49.61 | 22.52 | 16.28 | 3.10 | 11.72 | 6.79 | 4.58 | 3.17 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.30 | 17.00 | 18.00 | 3.00 | 9.00 | 10.00 | 8.30 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 17 | 46.47 | 25.00 | 8.00 | 14.65 | 8.00 | 6.32 | 3.34 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 85 | 50.78 | 22.46 | 16.16 | 6.46 | 12.74 | 5.25 | 5.61 | 1.74 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 69.92 | 20.20 | 18.00 | 10.20 | 12.50 | 5.00 | 8.80 | 0.70 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.00 | 25.00 | 14.00 | 5.00 | 12.00 | 9.00 | 8.67 | 0.00 |
| MEAN_REVERT | filtered | 1 | 64.50 | 25.00 | 14.00 | 6.00 | 13.00 | 5.00 | 6.30 | 0.00 |
| MEAN_REVERT | kept | 9 | 67.43 | 24.11 | 14.00 | 4.00 | 13.00 | 5.00 | 7.32 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 138 | 53.15 | 17.57 | 18.00 | 12.52 | 13.41 | 6.19 | 6.99 | 4.11 |
| MOVER_AVWAP_SCALP | kept | 123 | 77.86 | 18.37 | 18.07 | 12.02 | 13.81 | 7.16 | 8.52 | 4.54 |
| MOVER_TREND_PULLBACK | filtered | 2271 | 54.51 | 18.22 | 18.03 | 7.76 | 12.09 | 5.91 | 8.92 | 4.02 |
| MOVER_TREND_PULLBACK | kept | 3509 | 75.98 | 19.72 | 18.02 | 7.91 | 12.55 | 6.69 | 9.00 | 4.10 |
| QUIET_COMPRESSION_BREAK | filtered | 79 | 41.84 | 19.33 | 17.65 | 11.39 | 13.92 | 5.01 | 4.19 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 20 | 77.94 | 20.60 | 17.60 | 12.45 | 14.15 | 7.40 | 9.13 | 0.00 |
| SR_FLIP_RETEST | filtered | 48 | 55.37 | 22.50 | 11.12 | 4.88 | 14.98 | 5.45 | 8.29 | 2.24 |
| SR_FLIP_RETEST | kept | 37 | 70.78 | 23.70 | 17.19 | 3.81 | 12.38 | 5.14 | 7.34 | 2.61 |
| TREND_PULLBACK_EMA | filtered | 51 | 55.30 | 18.43 | 18.00 | 8.00 | 14.14 | 5.59 | 8.54 | 4.99 |
| TREND_PULLBACK_EMA | kept | 53 | 81.32 | 20.77 | 18.00 | 7.58 | 14.23 | 8.12 | 9.07 | 4.93 |
| VOLUME_SURGE_BREAKOUT | filtered | 31 | 46.30 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 2.30 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 69 | 57.48 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | **0.38** |
| DIVERGENCE_CONTINUATION | kept | 51 | 70.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.24 | 0.12 | 0.00 | 0.00 | **0.36** |
| FAILED_AUCTION_RECLAIM | filtered | 47 | 47.49 | 0.00 | 0.00 | 4.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.49** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 61.80 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 49.61 | 0.00 | 0.00 | 3.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.72** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 17 | 46.47 | 0.00 | 0.00 | 2.26 | 0.00 | 3.39 | 0.00 | 0.00 | 0.00 | **5.65** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 85 | 50.78 | 0.00 | 0.00 | 2.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.39** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 10 | 69.92 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.48** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 72.00 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| MEAN_REVERT | filtered | 1 | 64.50 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| MEAN_REVERT | kept | 9 | 67.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 138 | 53.15 | 0.00 | 0.00 | 2.84 | 0.00 | 5.10 | 0.28 | 0.00 | 0.43 | **8.65** |
| MOVER_AVWAP_SCALP | kept | 123 | 77.86 | 0.00 | 0.00 | 1.38 | 0.00 | 0.49 | 0.08 | 0.00 | 0.05 | **2.00** |
| MOVER_TREND_PULLBACK | filtered | 2271 | 54.51 | 0.00 | 0.00 | 1.82 | 0.00 | 0.99 | 0.21 | 0.00 | 0.00 | **3.02** |
| MOVER_TREND_PULLBACK | kept | 3509 | 75.98 | 0.00 | 0.00 | 0.51 | 0.00 | 0.20 | 0.12 | 0.00 | 0.00 | **0.83** |
| QUIET_COMPRESSION_BREAK | filtered | 79 | 41.84 | 0.00 | 0.00 | 0.95 | 0.00 | 0.05 | 0.00 | 0.00 | 9.10 | **10.10** |
| QUIET_COMPRESSION_BREAK | kept | 20 | 77.94 | 0.00 | 0.00 | 0.00 | 0.00 | 1.29 | 0.00 | 0.00 | 0.00 | **1.29** |
| SR_FLIP_RETEST | filtered | 48 | 55.37 | 0.00 | 0.00 | 0.90 | 0.00 | 0.45 | 0.00 | 0.00 | 0.00 | **1.35** |
| SR_FLIP_RETEST | kept | 37 | 70.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | **0.16** |
| TREND_PULLBACK_EMA | filtered | 51 | 55.30 | 0.00 | 0.00 | 2.54 | 0.00 | 3.39 | 0.00 | 0.00 | 0.00 | **5.93** |
| TREND_PULLBACK_EMA | kept | 53 | 81.32 | 0.00 | 0.00 | 0.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.91** |
| VOLUME_SURGE_BREAKOUT | filtered | 31 | 46.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **154994 held of 578648 seen** across 21 strategies; 3521 cells past the sample floor; **1796 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 45461 | 713/44748/0 | 44% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING/ALTCOIN (-1.33R) |
| MOVER_AVWAP_SCALP | 20087 | 192/19895/0 | 42% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11686 | 123/11563/0 | 37% | -0.28 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 11038 | 111/10927/0 | 48% | -0.06 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9329 | 43/9286/0 | 40% | -0.22 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 8374 | 91/8283/0 | 34% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7427 | 0/0/7427 | 42% | -0.12 | NY/MARKDOWN/CASCADE/BTC_FALLING (+0.46R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.03R) |
| SHADOW_RANGE_FADE | 6913 | 0/0/6913 | 35% | -0.16 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.43R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.23R) |
| QUIET_COMPRESSION_BREAK | 6488 | 435/6053/0 | 49% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 6058 | 0/0/6058 | 35% | -0.40 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.04R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 4239 | 46/4193/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/MARKDOWN/CASCADE/BTC_NEUTRAL (-1.32R) |
| SR_FLIP_RETEST | 3896 | 17/3879/0 | 45% | -0.30 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3130 | 0/3130/0 | 32% | -0.32 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 3112 | 2/3110/0 | 31% | -0.48 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| RANGE_FADE | 1480 | 4/1476/0 | 37% | -0.35 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1370 | 0/0/1370 | 54% | -0.04 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.32R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.40R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 396 | 0/396/0 | 29% | -0.63 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 132 | 28/104/0 | 42% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 234 | 28% / -0.58R | 234 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 23 | 26% / -0.63R | 23 | 52% / -0.26R | +0.37 | **ATR** |
| TREND_PULLBACK_EMA | 792 | 40% / -0.31R | 792 | 53% / -0.06R | +0.25 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1324 | 43% / -0.35R | 1324 | 56% / -0.13R | +0.22 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 157 | 35% / -0.23R | 157 | 46% / -0.07R | +0.16 | **ATR** |
| RANGE_FADE | 74 | 31% / -0.40R | 74 | 38% / -0.26R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 42 | 38% / -0.22R | 42 | 40% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 354 | 42% / -0.31R | 354 | 46% / -0.19R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1919 | 43% / -0.18R | 1919 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1126 | 40% / -0.24R | 1126 | 42% / -0.14R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 7811 | 49% / -0.12R | 7811 | 54% / -0.02R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1206 | 48% / -0.09R | 1206 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1091 | 48% / -0.14R | 1091 | 48% / -0.14R | -0.00 | **FIXED** |
| MEAN_REVERT | 298 | 47% / -0.16R | 298 | 46% / -0.16R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10684 | 28% | -0.23R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1919 | 46% | -0.07R | 222 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 99 | 47% | -0.07R | 61 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1458 | 40% / -0.16R | +0.85 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1064 | 34% / -0.22R | +0.84 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2385 | 34% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9690 | 37% / -0.13R | +0.40 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1378 | 37% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1065 | 34% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 938 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 229 | 31% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 309 | 33% / -0.44R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 247 | 49% / -0.03R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 57 | 37% / -0.08R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 330 | 34% / -0.33R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 63 | 27% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 29 | 41% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×633]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 535/6) (sustained 535 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 535/6) (sustained 535 cycles)
- **ALERT** `tuned_variants` — 168 non-stamps — atr_arm_uncomputable=168 (seen=7235 stamped=1086 skipped=5981) (streak 403/6) (sustained 403 cycles)
- **ALERT** `auto_dispatch` — 82 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=83) (streak 466/3) (sustained 466 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 43 fed / 0 quiet / 0 never delivered of 43 subscribed; 173187647 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 18 arms current, none stalled; covering 1828/1828 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 36 arms current, none stalled; covering 1100/1100 signals (100%) | 0 |
| auto_dispatch | violating | 82 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=83) (streak 466/3) | 466 |
| binance_ip_weight | ok | peak 120/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 81787.80 | 0 |
| candle_coverage | ok | 82/82 symbols with ≥20 15m candles, 82/82 updated within 45m [fresh=82; 78 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 4476 dup bars, 0 undedupable; ws 0 out-of-order, 574 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 57 cohorts, 36 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +2 / upstream +19 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1590/1608 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | violating | 6 of 149 open dark rows are not being advanced (worst: APRUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 16/120) | 16 |
| dark_sar_arms | ok | no open arms; covering 1594/1612 signals (99%) | 0 |
| depth_feed | ok | 43/43 books fresh (stale 0, never 0, thin 0); 61729199 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.61R (bound 0.3) (streak 535/6) | 535 |
| emission_controller | ok | last cycle 728s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×633]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 535/6) | 535 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 4/6) | 4 |
| firestore_read_budget | ok | 1,335 reads/day of 50,000 [engine 1,301, signing 34]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5160 sealed bars over 43 symbols; 1413 incomplete, 1 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +107 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 242462 frozen value(s) avoided; 796989 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.33R over n=4193 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +107 but output +0 (streak 2/72) | 2 |
| mover_admission_metadata | ok | 931 symbols known, 225 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3025 rows held, 3044330 evicted (sampled: execution:trigger_not_confirmed 400/1075681, execution:overextended 400/952332, setup_compat:regime_STRONG_TREND 400/518985) | 0 |
| price_action_lane | ok | 752919 evaluated, 1652 emitted; layer1 1652 stamped / 0 blind; cooldown=105057, delta_opposed=65282, no_footprint=276795, no_opposing_target=82, no_sweep=244453, rr_below_floor=59598 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 59 detections since last progress | 0 |
| range_fade_path | violating | upstream +107 but output +0 (streak 2/72) | 2 |
| sar_alignment_crosscheck | ok | 474/18441 disagreed (2.6%) | 0 |
| sar_exit_shadow | violating | upstream +107 but output +0 (streak 3/6) | 3 |
| sar_hold_arm | ok | 1903 held arms settled, 97 unscored, 36 still walking (33 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 7/36 unfetchable (19%); top cause: gap or duplicate bar in the 15m window; symbols: BNBUSDT, ETHUSDT, MUSDT | 0 |
| sar_live_arms | ok | 36 arms current, none stalled; covering 1100/1100 signals (100%) | 0 |
| sar_refresh_budget | ok | 2 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 436 records await one (29 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 9.05s, worst 301.52s over 9028 lifetime cycles; lifetime 645 over 60s, 176 over 120s; recent 2/0 warn/kill breaches in 20/20 cycles; heartbeat age 4.08s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 379806 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 5m ago | 0 |
| snapshot_writer | ok | last cycle 28s ago (4.99s to run, worst 277.68s), 2317 overrun(s) of 10361 cycles, TTL 900s; slowest trail_governor=3.56s, tickers=3.12s, signals=1.96s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=8, gate reads=0, withheld=8) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | violating | upstream +107 but output +0 (streak 1/36) | 1 |
| structural_snap | ok | 6000/6000 measured, 28 blind, 0 levels moved (refusals: redetect_cooldown=406) | 0 |
| structural_veto_lane | ok | 1161 stamped; 0 with no readable level book, 5 with clear air ahead, 894 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +107 / upstream +19 | 0 |
| tuned_variants | violating | 168 non-stamps — atr_arm_uncomputable=168 (seen=7235 stamped=1086 skipped=5981) (streak 403/6) | 403 |
| unlock_shorts | ok | 14 open, 44 scheduled, calendar 9.3h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 68 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1366552`
- `Path funnel` emissions: `35`
- `Regime distribution` emissions: `35`
- `QUIET_SCALP_BLOCK` events: `298`
- `confidence_gate` events: `6683`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **109**
- Total REST-fallback activations: **17**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 21 | 6564 | 39218 | 55971 | 0 |
| futures_aggtrade | 8 | 11462 | 54006 | 54877 | 0 |
| futures_depth | 63 | 11004 | 31871 | 85590 | 0 |
| futures_liq | 5 | 7178 | 9873 | 11466 | 0 |
| futures_mover | 12 | 6591 | 14361 | 14481 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 17 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=228541] state[populated=228541] buckets[many=228541] sources[none] quality[none]
- funding_rate: presence[absent=14039, present=214502] state[empty=14039, populated=214502] buckets[few=214502, none=14039] sources[none] quality[none]
- liquidation_clusters: presence[absent=126637, present=101904] state[empty=126637, populated=101904] buckets[few=85459, none=126637, some=16445] sources[none] quality[none]
- oi_snapshot: presence[absent=14039, present=214502] state[empty=14039, populated=214502] buckets[few=192, many=213252, none=14039, some=1058] sources[none] quality[none]
- order_book: presence[absent=76556, present=151985] state[populated=151985, unavailable=76556] buckets[few=151985, none=76556] sources[book_ticker=151985, unavailable=76556] quality[none=76556, top_of_book_only=151985]
- orderblocks: presence[absent=228541] state[empty=228541] buckets[none=228541] sources[measured_dark=228541] quality[none]
- recent_ticks: presence[present=228541] state[populated=228541] buckets[many=228541] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.052716016769409` sec
- Median create→first breach: `2599.496882557869` sec
- Median create→terminal: `2599.626524567604` sec
- Median first breach→terminal: `5.888938903808594e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.3}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.3}}`
- ~3 minute terminal-close behavior: `{"count": 3, "pct": 6.8}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.1155250329626354 | 1.1759834368530022 | 0.9485890685228042 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 1.1563298297126974 | 3.0 | 0.38544327657089916 | 1 | 3 |
| MOVER_TREND_PULLBACK | 32 | 32 | 3.88917234576145 | 3.0 | 1.324364197802485 | 26 | 6 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.0652572505690885 | 1.1597319528160406 | 0.867243885239474 | 0 | 5 |
| SR_FLIP_RETEST | 1 | 1 | 2.1207421703132034 | 2.432123370110331 | 0.871971461800064 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5217 | 333.1301779747009 | 333.57040095329285 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 50.0 | 50.0 | 50.0 | 0.0 | 0.6779 | 933.6186779737473 | 933.8665980100632 |
| MOVER_TREND_PULLBACK | 32 | 32 | 18.8 | 56.2 | 18.8 | 0.0 | -1.1778 | 2295.8226445913315 | 2295.9522886276245 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 33.3 | 50.0 | 33.3 | 0.0 | -0.0759 | 26542.783496379852 | 26542.783571481705 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.1811 | 17434.853188037872 | 17435.292807102203 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 477 | 6 | 293 | 100.0 | 0.0 | 17434.853188037872 | 17435.292807102203 | 184 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1038 | 16 | 893 | 0.0 | 0.0 | None | None | 145 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `287`
- Gating Δ: `-9774`
- No-generation Δ: `-36368`
- Fast failures Δ: `1`
- Quality changes: `{"LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.6779, "current_avg_pnl": 0.6779, "current_win_rate": 50.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.5338, "current_avg_pnl": -1.1778, "current_win_rate": 18.8, "previous_avg_pnl": 0.356, "previous_win_rate": 42.1, "win_rate_delta": -23.3}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.2435, "current_avg_pnl": -0.0759, "current_win_rate": 33.3, "previous_avg_pnl": 0.1676, "previous_win_rate": 42.9, "win_rate_delta": -9.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 146, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 17434.85, "median_terminal_delta_sec": 17435.29, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 7, "geometry_changed_delta": 0, "geometry_preserved_delta": 89, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2905.16, "median_terminal_delta_sec": -2905.16, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
