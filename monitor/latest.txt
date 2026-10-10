# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `2634` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 177 | 177 | 177 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8688 | 8688 | 8381 | 12 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 72960 | 72953 | 37 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 65051 | 65051 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 64679 | 63118 | 1912 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 65083 | 64659 | 488 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 65349 | 65240 | 146 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 56555 | 56558 | 13 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 65152 | 65176 | 12 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 65200 | 63261 | 2771 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 77191 | 81806 | 1105 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 72996 | 66255 | 10882 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 64813 | 64813 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 65055 | 65076 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 64639 | 64573 | 97 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 66041 | 64912 | 1693 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 64068 | 64468 | 126 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 55601 | 51922 | 3896 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 55825 | 55505 | 388 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 72910 | 72906 | 48 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 56574 | 56605 | 6 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2540 | 2540 | 2323 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 769 | 769 | 586 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 36 | 36 | 22 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 17413 | 17413 | 17199 | 14 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 21 | 21 | 16 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8204 | 8204 | 6971 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2938 | 2938 | 2549 | 24 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 30936 | 30936 | 26276 | 150 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1210 | 1210 | 1127 | 17 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4947 | 4947 | 4066 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 366 | 366 | 296 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2016 | 2016 | 1963 | 7 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 237 | 237 | 207 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1559 | 1559 | 587 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=72953): breakout_not_found=42926, basic_filters_failed=18337, move_not_fresh=7767, breakout_stale=3347, retest_proximity_failed=437, volume_spike_missing=139
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=65051): cls_disabled_merged_into_lsr=65051
- **EVAL::DIVERGENCE_CONTINUATION** (total=63118): cvd_divergence_failed=23748, h1_trend_not_aligned=20587, basic_filters_failed=13769, ema_alignment_reject=4322, retest_proximity_failed=568, missing_fvg_or_orderblock=124
- **EVAL::FAILED_AUCTION_RECLAIM** (total=64659): auction_not_detected=44762, basic_filters_failed=13354, reclaim_hold_failed=2337, tail_too_small=2085, regime_blocked=2064, rsi_reject=57
- **EVAL::FUNDING_EXTREME** (total=65240): funding_not_extreme=45567, basic_filters_failed=12411, missing_funding_rate=5173, ema_alignment_reject=1203, rsi_reject=603, momentum_reject=138, cvd_divergence_failed=127, missing_fvg_or_orderblock=18
- **EVAL::LIQUIDATION_REVERSAL** (total=56558): cascade_threshold_not_met=42207, basic_filters_failed=13881, rsi_reject=239, cvd_divergence_failed=209, missing_fvg_or_orderblock=22
- **EVAL::MA_CROSS_TREND_SHIFT** (total=65176): no_ma_cross=49586, basic_filters_failed=13781, ma_cross_cooldown=1440, ma_cross_htf_misaligned=369
- **EVAL::MEAN_REVERT** (total=63261): no_extension=49914, basic_filters_failed=13347
- **EVAL::MOVER_AVWAP_SCALP** (total=81806): no_avwap_tag=32297, no_mover_leg=20287, basic_filters_failed=18556, avwap_slope_against=6898, avwap_reclaim_no_volume=2510, no_avwap_reclaim=1251, anchor_too_recent=7
- **EVAL::MOVER_TREND_PULLBACK** (total=66255): mover_run_too_small=33790, basic_filters_failed=18444, no_reclaim=11918, no_pullback_tag=2103
- **EVAL::OPENING_RANGE_BREAKOUT** (total=64813): feature_disabled=64813
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=65076): regime_blocked=39782, breakout_not_found=19150, basic_filters_failed=4539, adx_reject=1549, ema_alignment_reject=54, rsi_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=64573): regime_blocked=27206, compression_not_detected=24363, basic_filters_failed=8805, breakout_not_detected=3929, volume_confirmation_failed=243, rsi_reject=22, missing_fvg_or_orderblock=5
- **EVAL::RANGE_FADE** (total=64912): no_range_edge=51561, basic_filters_failed=13351
- **EVAL::SR_FLIP_RETEST** (total=64468): flip_close_not_confirmed=44316, basic_filters_failed=13333, regime_blocked=2043, retest_out_of_zone=1731, h1_break_not_confirmed=1170, long_break_volume_thin=1134, reclaim_hold_failed=505, long_acceptance_not_held=91, wick_quality_failed=85, whipsaw_flip=28, ema_alignment_reject=24, missing_fvg_or_orderblock=8
- **EVAL::STANDARD** (total=51922): momentum_reject=14357, basic_filters_failed=10053, adx_reject=9917, macd_reject=5534, sweeps_not_detected=5279, ema_alignment_reject=5197, htf_poi_unanchored=1440, invalid_sl_geometry=64, mtf_reject=56, rsi_reject=25
- **EVAL::TREND_PULLBACK** (total=55505): h1_trend_not_aligned=21525, ema_alignment_reject=8627, basic_filters_failed=7941, h1_pullback_not_confirmed=4675, ema_not_tested_prev=4515, no_ema_reclaim_close=3281, body_conviction_fail=1930, rsi_reject=1692, prev_already_below_emas=446, no_prev_low_break=295, prev_already_above_emas=198, momentum_flat=135, no_prev_high_break=131, ema21_not_tagged=47, momentum_reject=47, missing_fvg_or_orderblock=20
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=72906): breakout_not_found=38360, basic_filters_failed=18335, move_not_fresh=10966, breakout_stale=3943, retest_proximity_failed=1049, volume_spike_missing=237, missing_fvg_or_orderblock=11, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=56605): momentum_reject=40276, recent_ticks_insufficient=10784, basic_filters_failed=5545

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=38): execution:overextended=38
- **DIVERGENCE_CONTINUATION** (total=366): setup_compat:regime_VOLATILE_UNSUITABLE=350, setup_compat:regime_BREAKOUT_EXPANSION=16
- **FAILED_AUCTION_RECLAIM** (total=613): setup_compat:regime_STRONG_TREND=319, execution:overextended=233, context_floor=61
- **FUNDING_EXTREME_SIGNAL** (total=574): execution:trigger_not_confirmed=573, context_floor=1
- **LIQUIDATION_REVERSAL** (total=36): execution:trigger_not_confirmed=36
- **LIQUIDITY_SWEEP_REVERSAL** (total=4119): setup_compat:regime_STRONG_TREND=1575, execution:trigger_not_confirmed=1479, execution:overextended=1065
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=2, execution:overextended=2
- **MEAN_REVERT** (total=6748): setup_compat:regime_STRONG_TREND=3133, setup_compat:regime_WEAK_TREND=2954, execution:overextended=661
- **MOVER_AVWAP_SCALP** (total=1529): execution:overextended=995, execution:trigger_not_confirmed=477, entry_quality=57
- **MOVER_TREND_PULLBACK** (total=12824): execution:trigger_not_confirmed=6467, execution:overextended=5633, entry_quality=724
- **QUIET_COMPRESSION_BREAK** (total=25): execution:trigger_not_confirmed=25
- **RANGE_FADE** (total=3284): setup_compat:regime_STRONG_TREND=1701, setup_compat:regime_WEAK_TREND=1241, setup_compat:regime_VOLATILE_UNSUITABLE=166, execution:overextended=121, setup_compat:regime_BREAKOUT_EXPANSION=43, context_edge=12
- **TREND_PULLBACK_EMA** (total=1632): setup_compat:regime_CLEAN_RANGE=1035, setup_compat:regime_DIRTY_RANGE=507, setup_compat:regime_VOLATILE_UNSUITABLE=79, entry_quality=11
- **VOLUME_SURGE_BREAKOUT** (total=24): execution:overextended=24
- **WHALE_MOMENTUM** (total=1440): execution:trigger_not_confirmed=1434, context_floor=6

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 128911 | 30.9% |
| TRENDING_UP | 113714 | 27.3% |
| QUIET | 103002 | 24.7% |
| TRENDING_DOWN | 54113 | 13.0% |
| VOLATILE | 17308 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **94**
- Average confidence gap to threshold: **14.54** (samples=94) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=20, XRPUSDT=12, AVAXUSDT=8, HBARUSDT=6, AAVEUSDT=6, ZECUSDT=6, TRUMPUSDT=5, LINKUSDT=5, OPUSDT=4, SOLUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 132 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 41 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 22 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 17 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 53 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 21 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 78 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 113 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 378 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1404 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 36 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 16 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 18 |
| SR_FLIP_RETEST | filtered | min_confidence | 13 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 35 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 22 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 19 |
| WHALE_MOMENTUM | filtered | min_confidence | 11 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 132 | 54.05 | 63.84 | 9.79 | 20.52 | 19.81 | 19.46 | 2.45 | 16.85 |
| DIVERGENCE_CONTINUATION | kept | 41 | 71.06 | 65.00 | -6.06 | 22.41 | 19.70 | 17.61 | 0.24 | -0.40 |
| FAILED_AUCTION_RECLAIM | filtered | 39 | 44.74 | 64.56 | 19.82 | 20.97 | 19.97 | 20.00 | 2.15 | 9.08 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 63.00 | 65.00 | 2.00 | 20.50 | 19.35 | 20.00 | 2.50 | 3.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 49.37 | 61.00 | 11.63 | 21.20 | 14.00 | 17.00 | 3.67 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 62 | 47.68 | 64.48 | 16.80 | 19.47 | 19.29 | 18.07 | 1.55 | 7.42 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 69.08 | 65.00 | -4.08 | 20.64 | 19.36 | 17.17 | 1.48 | 0.55 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 72.30 | 65.00 | -7.30 | 20.40 | 19.70 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 1 | 74.30 | 65.00 | -9.30 | 20.50 | 14.00 | 16.10 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 82 | 46.64 | 65.00 | 18.36 | 19.62 | 16.11 | 15.80 | 3.76 | 19.53 |
| MOVER_AVWAP_SCALP | kept | 113 | 77.72 | 65.00 | -12.72 | 19.88 | 15.47 | 15.80 | 4.18 | 4.14 |
| MOVER_TREND_PULLBACK | filtered | 383 | 57.47 | 64.54 | 7.07 | 20.29 | 18.74 | 15.80 | 4.27 | 8.56 |
| MOVER_TREND_PULLBACK | kept | 1404 | 76.36 | 65.00 | -11.36 | 20.13 | 18.50 | 15.80 | 4.08 | 1.60 |
| QUIET_COMPRESSION_BREAK | filtered | 52 | 51.19 | 65.00 | 13.81 | 22.64 | 19.75 | 20.00 | 0.00 | 5.82 |
| QUIET_COMPRESSION_BREAK | kept | 18 | 71.49 | 65.00 | -6.49 | 21.48 | 19.62 | 20.00 | 0.00 | 1.57 |
| SR_FLIP_RETEST | filtered | 17 | 44.24 | 63.82 | 19.58 | 21.19 | 20.00 | 15.22 | 2.09 | 16.84 |
| SR_FLIP_RETEST | kept | 2 | 67.40 | 65.00 | -2.40 | 20.70 | 20.00 | 15.20 | 2.50 | 9.70 |
| TREND_PULLBACK_EMA | filtered | 6 | 55.00 | 61.00 | 6.00 | 21.20 | 19.80 | 20.00 | 4.50 | 5.00 |
| TREND_PULLBACK_EMA | kept | 35 | 74.43 | 65.00 | -9.43 | 20.89 | 19.91 | 17.58 | 5.09 | 0.21 |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 50.70 | 62.82 | 12.12 | 20.58 | 18.68 | 20.00 | 3.77 | 6.80 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 77.17 | 65.00 | -12.17 | 19.97 | 19.40 | 20.00 | 4.50 | 1.00 |
| WHALE_MOMENTUM | filtered | 30 | 55.23 | 63.17 | 7.94 | 22.84 | 14.60 | 17.00 | 0.00 | 11.61 |
| WHALE_MOMENTUM | kept | 1 | 62.20 | 65.00 | 2.80 | 24.00 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 132 | 54.05 | 22.82 | 17.47 | 3.11 | 12.15 | 5.39 | 7.42 | 2.45 |
| DIVERGENCE_CONTINUATION | kept | 41 | 71.06 | 19.34 | 17.02 | 8.12 | 13.02 | 5.23 | 9.06 | 0.24 |
| FAILED_AUCTION_RECLAIM | filtered | 39 | 44.74 | 19.46 | 14.31 | 8.38 | 12.79 | 6.54 | 5.18 | 2.15 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 63.00 | 25.00 | 16.00 | 7.50 | 15.50 | 8.50 | 6.00 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 49.37 | 25.00 | 8.00 | 12.00 | 9.00 | 10.00 | 4.70 | 3.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 62 | 47.68 | 24.13 | 15.10 | 5.37 | 12.02 | 5.00 | 5.25 | 1.55 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 69.08 | 22.52 | 15.52 | 4.14 | 12.19 | 5.36 | 8.41 | 1.48 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 72.30 | 25.00 | 14.00 | 3.00 | 17.00 | 5.00 | 8.30 | 0.00 |
| MEAN_REVERT | kept | 1 | 74.30 | 17.00 | 18.00 | 15.00 | 13.00 | 5.00 | 6.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 82 | 46.64 | 18.85 | 18.00 | 10.90 | 14.15 | 8.24 | 4.17 | 3.76 |
| MOVER_AVWAP_SCALP | kept | 113 | 77.72 | 19.19 | 18.00 | 12.16 | 14.36 | 6.75 | 7.49 | 4.18 |
| MOVER_TREND_PULLBACK | filtered | 383 | 57.47 | 18.02 | 18.00 | 7.55 | 12.06 | 5.89 | 7.53 | 4.27 |
| MOVER_TREND_PULLBACK | kept | 1404 | 76.36 | 19.61 | 18.00 | 7.63 | 12.95 | 6.98 | 8.83 | 4.08 |
| QUIET_COMPRESSION_BREAK | filtered | 52 | 51.19 | 19.00 | 16.77 | 10.15 | 14.35 | 7.50 | 4.47 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 18 | 71.49 | 19.22 | 17.56 | 11.50 | 14.50 | 5.47 | 6.23 | 0.00 |
| SR_FLIP_RETEST | filtered | 17 | 44.24 | 21.24 | 15.65 | 3.88 | 14.00 | 5.00 | 6.31 | 2.09 |
| SR_FLIP_RETEST | kept | 2 | 67.40 | 25.00 | 18.00 | 4.50 | 17.00 | 6.75 | 3.30 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 6 | 55.00 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 4.50 |
| TREND_PULLBACK_EMA | kept | 35 | 74.43 | 19.74 | 18.00 | 7.50 | 14.77 | 6.37 | 7.29 | 5.09 |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 50.70 | 12.91 | 16.18 | 12.14 | 11.95 | 5.82 | 5.65 | 3.77 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 77.17 | 17.00 | 18.00 | 13.00 | 12.00 | 5.00 | 8.67 | 4.50 |
| WHALE_MOMENTUM | filtered | 30 | 55.23 | 22.33 | 11.67 | 8.10 | 14.20 | 6.77 | 3.77 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 62.20 | 17.00 | 18.00 | 12.00 | 14.00 | 8.50 | 2.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 132 | 54.05 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.12** |
| DIVERGENCE_CONTINUATION | kept | 41 | 71.06 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.12** |
| FAILED_AUCTION_RECLAIM | filtered | 39 | 44.74 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 63.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 49.37 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 62 | 47.68 | 0.00 | 0.00 | 4.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.03** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 69.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 72.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 1 | 74.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 82 | 46.64 | 0.00 | 0.00 | 0.29 | 0.00 | 4.92 | 0.00 | 0.00 | 3.36 | **8.57** |
| MOVER_AVWAP_SCALP | kept | 113 | 77.72 | 0.00 | 0.00 | 0.55 | 0.00 | 1.54 | 0.00 | 0.00 | 1.16 | **3.25** |
| MOVER_TREND_PULLBACK | filtered | 383 | 57.47 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.80** |
| MOVER_TREND_PULLBACK | kept | 1404 | 76.36 | 0.03 | 0.00 | 0.53 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.60** |
| QUIET_COMPRESSION_BREAK | filtered | 52 | 51.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.74 | 0.35 | 0.00 | 2.72 | **3.81** |
| QUIET_COMPRESSION_BREAK | kept | 18 | 71.49 | 0.00 | 0.00 | 0.00 | 0.00 | 2.39 | 0.00 | 0.00 | 0.33 | **2.72** |
| SR_FLIP_RETEST | filtered | 17 | 44.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 2 | 67.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 6 | 55.00 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| TREND_PULLBACK_EMA | kept | 35 | 74.43 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.41** |
| VOLUME_SURGE_BREAKOUT | filtered | 22 | 50.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.73 | **2.73** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 77.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 30 | 55.23 | 0.00 | 0.00 | 0.00 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | **1.44** |
| WHALE_MOMENTUM | kept | 1 | 62.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **137320 held of 458655 seen** across 21 strategies; 3132 cells past the sample floor; **1541 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 42868 | 634/42234/0 | 41% | -0.21 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.22R) |
| MOVER_AVWAP_SCALP | 17904 | 184/17720/0 | 41% | -0.24 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10769 | 123/10646/0 | 37% | -0.30 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 9495 | 62/9433/0 | 51% | -0.00 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.39R) | OVERLAP/MARKDOWN/NORMAL/BTC_FALLING (-1.19R) |
| TREND_PULLBACK_EMA | 7836 | 34/7802/0 | 44% | -0.15 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OVERLAP/QUIET/COMPRESSED/BTC_FALLING (-1.29R) |
| SHADOW_MEAN_REVERT | 6819 | 0/0/6819 | 43% | -0.09 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.95R) |
| LIQUIDITY_SWEEP_REVERSAL | 6545 | 81/6464/0 | 34% | -0.52 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | LONDON/MARKUP/EXPANDED/BTC_NEUTRAL (-1.63R) |
| SHADOW_RANGE_FADE | 6087 | 0/0/6087 | 37% | -0.07 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+0.53R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-1.38R) |
| QUIET_COMPRESSION_BREAK | 5613 | 358/5255/0 | 50% | -0.09 | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (+0.57R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5402 | 0/0/5402 | 35% | -0.40 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.36R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3741 | 4/3737/0 | 44% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 3145 | 37/3108/0 | 45% | -0.17 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 2651 | 2/2649/0 | 31% | -0.47 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2601 | 0/2601/0 | 35% | -0.22 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 2508 | 13/2495/0 | 47% | -0.22 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.27R) |
| RANGE_FADE | 1189 | 4/1185/0 | 42% | -0.35 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1164 | 0/0/1164 | 54% | -0.03 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.12R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 316 | 0/316/0 | 36% | -0.47 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 88 | 12/76/0 | 45% | -0.08 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 12 | 0/12/0 | 50% | -0.00 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.63R (n=43, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/MARKUP/EXPANDED/BTC_NEUTRAL` -1.63R (n=43, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 186 | 26% / -0.60R | 186 | 52% / -0.15R | +0.44 | **ATR** |
| LIQUIDATION_REVERSAL | 17 | 35% / -0.40R | 17 | 59% / -0.18R | +0.22 | **ATR** |
| TREND_PULLBACK_EMA | 645 | 42% / -0.25R | 645 | 55% / -0.04R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1083 | 44% / -0.32R | 1083 | 54% / -0.15R | +0.18 | **ATR** |
| MOVER_AVWAP_SCALP | 1482 | 43% / -0.20R | 1482 | 49% / -0.07R | +0.13 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 131 | 35% / -0.22R | 131 | 45% / -0.09R | +0.13 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1035 | 40% / -0.25R | 1035 | 42% / -0.14R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 6782 | 48% / -0.13R | 6782 | 53% / -0.03R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 432 | 44% / -0.33R | 432 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 222 | 47% / -0.25R | 222 | 50% / -0.16R | +0.09 | **ATR** |
| RANGE_FADE | 56 | 34% / -0.40R | 56 | 39% / -0.32R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 953 | 48% / -0.11R | 953 | 54% / -0.05R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 26 | 46% / -0.13R | 26 | 46% / -0.07R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 909 | 46% / -0.15R | 909 | 46% / -0.15R | -0.01 | **FIXED** |
| MEAN_REVERT | 230 | 53% / -0.05R | 230 | 51% / -0.05R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 43% / -0.33R | 7 | 43% / -0.24R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9687 | 29% | -0.25R | 310 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1482 | 46% | -0.08R | 212 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 82 | 48% | -0.09R | 51 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 863 | 37% / -0.16R | +0.90 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1107 | 39% / -0.19R | +0.82 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1938 | 34% / -0.10R | +0.74 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8726 | 35% / -0.16R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1076 | 38% / -0.06R | +0.22 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 158 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 883 | 35% / -0.16R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 842 | 33% / -0.20R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 192 | 29% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 247 | 31% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 190 | 54% / +0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 42 | 31% / -0.16R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 226 | 33% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 42 | 26% / -0.45R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 23 | 48% / +0.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 13 | 38% / +0.45R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×541]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 285/6) (sustained 285 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.54R (bound 0.3) (streak 1028/6) (sustained 1028 cycles)
- **ALERT** `tuned_variants` — 735 non-stamps — atr_arm_uncomputable=735 (seen=16477 stamped=1697 skipped=14045) (streak 1023/6) (sustained 1023 cycles)
- **ALERT** `auto_dispatch` — 169 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=169) (streak 1017/3) (sustained 1017 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 53 fed / 0 quiet / 2 never delivered of 55 subscribed; 477411950 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 24 arms current, none stalled; covering 1367/1367 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 50 arms current, none stalled; covering 1203/1203 signals (100%) | 0 |
| auto_dispatch | violating | 169 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=169) (streak 1017/3) | 1017 |
| binance_ip_weight | ok | peak 164/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82749.50 | 0 |
| candle_coverage | ok | 85/85 symbols with ≥20 15m candles, 85/85 updated within 45m [fresh=85; 77 Tier-1 futures + 8 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 243 dup bars, 0 undedupable; ws 0 out-of-order, 1015 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 52 cohorts, 15 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +8 / upstream +29 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1999/2017 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 2 promoted today, nothing refused | 0 |
| dark_resolution | ok | 116 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1994/2012 signals (99%) | 0 |
| depth_feed | ok | 53/55 books fresh (stale 0, never 2, thin 0); 185809333 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.54R (bound 0.3) (streak 1028/6) | 1028 |
| emission_controller | ok | last cycle 1366s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×541]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 285/6) | 285 |
| entry_quality_effective | ok | 24870 evaluated, 7530 suppressed, 9375 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,368 reads/day of 50,000 [engine 1,329, signing 39]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 6360 sealed bars over 53 symbols; 1479 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +154 | 0 |
| indicator_cache_key | ok | 436228 frozen value(s) avoided; 2203438 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.18R over n=3108 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +29 / upstream +154 | 0 |
| mover_admission_metadata | ok | 924 symbols known, 217 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 8 held, 8 with scan counts, 8 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3075 rows held, 2541235 evicted (sampled: execution:trigger_not_confirmed 400/925593, execution:overextended 400/815976, setup_compat:regime_STRONG_TREND 400/400520) | 0 |
| price_action_lane | ok | 2756785 evaluated, 2609 emitted; layer1 2609 stamped / 0 blind; cooldown=359271, delta_opposed=222532, no_footprint=1056956, no_opposing_target=1521, no_sweep=905463, rr_below_floor=208433 | 0 |
| promoted_pair_integrity | ok | 8/8 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.35R over n=1185 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +41 / upstream +154 | 0 |
| sar_alignment_crosscheck | ok | 881/40313 disagreed (2.2%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +154 | 0 |
| sar_hold_arm | ok | 1855 held arms settled, 145 unscored, 47 still walking (38 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/31 unfetchable (6%); top cause: located bar does not contain the stamp; symbols: ASTERUSDT, OGNUSDT | 0 |
| sar_live_arms | ok | 47 arms current, none stalled; covering 1202/1202 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 431 records await one (29 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 5.06s, worst 192.9s over 32304 lifetime cycles; lifetime 263 over 60s, 22 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 6.1s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 1346093 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 5m ago | 0 |
| snapshot_writer | ok | last cycle 37s ago (3.37s to run, worst 179.91s), 1757 overrun(s) of 21199 cycles, TTL 900s; slowest tickers=9.44s, signals=3.32s, alerts=1.74s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=7, gate reads=0, withheld=7) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +3 / upstream +154 | 0 |
| structural_snap | ok | 6000/6000 measured, 25 blind, 0 levels moved (refusals: redetect_cooldown=1670) | 0 |
| structural_veto_lane | ok | 3199 stamped; 0 with no readable level book, 82 with clear air ahead, 2516 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +154 / upstream +29 | 0 |
| tuned_variants | violating | 735 non-stamps — atr_arm_uncomputable=735 (seen=16477 stamped=1697 skipped=14045) (streak 1023/6) | 1023 |
| unlock_shorts | ok | 14 open, 42 scheduled, calendar 19.1h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 92 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1962344`
- `Path funnel` emissions: `48`
- `Regime distribution` emissions: `48`
- `QUIET_SCALP_BLOCK` events: `94`
- `confidence_gate` events: `2470`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **26**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 9 | 8116 | 29007 | 33903 | 0 |
| futures_depth | 6 | 11893 | 17667 | 41604 | 0 |
| futures_liq | 4 | 6101 | 23290 | 82027 | 0 |
| futures_mover | 7 | 8758 | 11004 | 11032 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=351042] state[populated=351042] buckets[many=351042] sources[none] quality[none]
- funding_rate: presence[absent=42401, present=308641] state[empty=42401, populated=308641] buckets[few=308641, none=42401] sources[none] quality[none]
- liquidation_clusters: presence[absent=211681, present=139361] state[empty=211681, populated=139361] buckets[few=119969, none=211681, some=19392] sources[none] quality[none]
- oi_snapshot: presence[absent=42401, present=308641] state[empty=42401, populated=308641] buckets[many=308641, none=42401] sources[none] quality[none]
- order_book: presence[absent=105167, present=245875] state[populated=245875, unavailable=105167] buckets[few=245875, none=105167] sources[book_ticker=245875, unavailable=105167] quality[none=105167, top_of_book_only=245875]
- orderblocks: presence[absent=351042] state[empty=351042] buckets[none=351042] sources[measured_dark=351042] quality[none]
- recent_ticks: presence[present=351042] state[populated=351042] buckets[many=351042] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.5084985494613647` sec
- Median create→first breach: `6615.087132930756` sec
- Median create→terminal: `6616.362048506737` sec
- Median first breach→terminal: `6.902217864990234e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.0931112984822828 | 1.2638754826254832 | 0.8648884431332846 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.5421728869854077 | 3.0 | 0.8473909623284692 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 3.0492119738167083 | 3.0 | 1.016403991272236 | 1 | 0 |
| MEAN_REVERT | 1 | 1 | 2.1460924581206444 | 2.9836796318930183 | 0.7192771084337362 | 0 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.0109278547761544 | 2.4657812876052874 | 0.8587342659570962 | 0 | 3 |
| MOVER_TREND_PULLBACK | 28 | 28 | 3.7073015028395044 | 3.0 | 1.2816163973184291 | 19 | 9 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 0.9687798697905126 | 1.0624622893236808 | 0.9125175791052558 | 0 | 5 |
| SR_FLIP_RETEST | 1 | 1 | 0.7216783216783241 | 0.5000000000000003 | 1.4433566433566474 | 1 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0931 | 27568.519695043564 | 27568.519762039185 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.5422 | 4256.069025039673 | 4256.069047927856 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0492 | 1844.577882051468 | 1844.5779979228973 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 7980.474046945572 | 7980.474067926407 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -2.16 | 17395.067891836166 | 17395.067910909653 |
| MOVER_TREND_PULLBACK | 28 | 28 | 42.9 | 46.4 | 42.9 | 0.0 | 0.4087 | 5316.2616111040115 | 5316.441307544708 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 33.3 | 50.0 | 33.3 | 0.0 | 0.4169 | 10423.25353205204 | 10423.253582119942 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.0825 | 649398.8783700466 | 649399.5911550522 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 366 | 2 | 296 | 100.0 | 0.0 | 649398.8783700466 | 649399.5911550522 | 70 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2016 | 7 | 1963 | 0.0 | 0.0 | None | None | 53 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-355`
- Gating Δ: `-14529`
- No-generation Δ: `-99827`
- Fast failures Δ: `-3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.3563, "current_avg_pnl": -1.0931, "current_win_rate": 0.0, "previous_avg_pnl": -1.4494, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -1.0492, "current_avg_pnl": -3.0492, "current_win_rate": 0.0, "previous_avg_pnl": -2.0, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.9563, "current_avg_pnl": -2.16, "current_win_rate": 0.0, "previous_avg_pnl": -1.2037, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.3096, "current_avg_pnl": 0.4087, "current_win_rate": 42.9, "previous_avg_pnl": -0.9009, "previous_win_rate": 22.6, "win_rate_delta": 20.3}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.9084, "current_avg_pnl": 0.4169, "current_win_rate": 33.3, "previous_avg_pnl": 1.3253, "previous_win_rate": 50.0, "win_rate_delta": -16.7}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -2.8857, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 2.8857, "previous_win_rate": 100.0, "win_rate_delta": -100.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": -285, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 649398.88, "median_terminal_delta_sec": 649399.59, "sl_rate_delta": 0.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -29, "geometry_changed_delta": 0, "geometry_preserved_delta": -400, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3239.73, "median_terminal_delta_sec": -3242.3, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
