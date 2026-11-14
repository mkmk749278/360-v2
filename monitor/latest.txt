# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `3353` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 160 | 160 | 160 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8984 | 8984 | 7861 | 23 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 68237 | 68231 | 27 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 61979 | 61981 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 61641 | 59687 | 2279 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 62013 | 61219 | 876 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 62249 | 62113 | 165 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 52265 | 52283 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 62099 | 62129 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 62137 | 60588 | 2318 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 71690 | 78763 | 509 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 68260 | 62892 | 8732 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 61930 | 61932 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 61984 | 62007 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 61623 | 61565 | 74 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 62909 | 62130 | 1113 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 61268 | 61410 | 171 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 51454 | 48326 | 3453 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 51783 | 51498 | 358 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 68186 | 68214 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 52288 | 52301 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3616 | 3616 | 3471 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 471 | 471 | 109 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 15 | 15 | 9 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 16723 | 16723 | 16522 | 5 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 1 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6165 | 6165 | 4387 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1516 | 1516 | 221 | 51 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 23031 | 23031 | 9376 | 331 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 2 | 2 | 0 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 299 | 299 | 67 | 13 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2928 | 2928 | 2525 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 463 | 463 | 216 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1620 | 1620 | 1033 | 60 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 80 | 80 | 42 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=68231): breakout_not_found=40884, basic_filters_failed=15098, move_not_fresh=8454, breakout_stale=2543, retest_proximity_failed=1024, volume_spike_missing=211, move_exhausted=6, missing_fvg_or_orderblock=6, ema_alignment_reject=5
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=61981): cls_disabled_merged_into_lsr=61981
- **EVAL::DIVERGENCE_CONTINUATION** (total=59687): cvd_divergence_failed=29411, h1_trend_not_aligned=11810, basic_filters_failed=11295, ema_alignment_reject=6183, retest_proximity_failed=718, missing_fvg_or_orderblock=270
- **EVAL::FAILED_AUCTION_RECLAIM** (total=61219): auction_not_detected=42464, basic_filters_failed=11014, reclaim_hold_failed=3061, tail_too_small=2431, regime_blocked=2205, rsi_reject=44
- **EVAL::FUNDING_EXTREME** (total=62113): funding_not_extreme=47118, basic_filters_failed=11314, ema_alignment_reject=2063, missing_funding_rate=757, rsi_reject=595, cvd_divergence_failed=136, momentum_reject=109, missing_fvg_or_orderblock=21
- **EVAL::LIQUIDATION_REVERSAL** (total=52283): cascade_threshold_not_met=40277, basic_filters_failed=11257, cvd_divergence_failed=358, rsi_reject=351, missing_fvg_or_orderblock=31, volume_spike_missing=9
- **EVAL::MA_CROSS_TREND_SHIFT** (total=62129): no_ma_cross=50043, basic_filters_failed=11315, ma_cross_cooldown=513, ma_cross_htf_misaligned=258
- **EVAL::MEAN_REVERT** (total=60588): no_extension=53124, basic_filters_failed=7464
- **EVAL::MOVER_AVWAP_SCALP** (total=78763): no_avwap_tag=33644, no_mover_leg=17857, basic_filters_failed=15322, avwap_slope_against=7704, avwap_reclaim_no_volume=2114, no_avwap_reclaim=2077, anchor_too_recent=45
- **EVAL::MOVER_TREND_PULLBACK** (total=62892): mover_run_too_small=35556, basic_filters_failed=15223, no_reclaim=10713, no_pullback_tag=1400
- **EVAL::OPENING_RANGE_BREAKOUT** (total=61932): feature_disabled=61932
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=62007): regime_blocked=33749, breakout_not_found=21331, basic_filters_failed=3753, adx_reject=3103, ema_alignment_reject=71
- **EVAL::QUIET_COMPRESSION_BREAK** (total=61565): regime_blocked=30311, compression_not_detected=22880, basic_filters_failed=7251, breakout_not_detected=957, volume_confirmation_failed=147, rsi_reject=19
- **EVAL::RANGE_FADE** (total=62130): no_range_edge=54662, basic_filters_failed=7468
- **EVAL::SR_FLIP_RETEST** (total=61410): flip_close_not_confirmed=42110, basic_filters_failed=10999, regime_blocked=2186, retest_out_of_zone=2067, h1_break_not_confirmed=1841, long_break_volume_thin=1373, reclaim_hold_failed=561, ema_alignment_reject=99, long_acceptance_not_held=69, wick_quality_failed=48, whipsaw_flip=38, missing_fvg_or_orderblock=19
- **EVAL::STANDARD** (total=48326): momentum_reject=15767, adx_reject=10844, sweeps_not_detected=7004, basic_filters_failed=5428, ema_alignment_reject=4399, macd_reject=4152, htf_poi_unanchored=638, invalid_sl_geometry=71, rsi_reject=22, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=51498): h1_trend_not_aligned=12107, ema_alignment_reject=11326, basic_filters_failed=7470, ema_not_tested_prev=5559, h1_pullback_not_confirmed=5179, no_ema_reclaim_close=3739, body_conviction_fail=2532, rsi_reject=1988, prev_already_below_emas=634, no_prev_low_break=356, prev_already_above_emas=226, no_prev_high_break=151, momentum_flat=136, ema21_not_tagged=65, momentum_reject=17, missing_fvg_or_orderblock=13
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=68214): breakout_not_found=42010, basic_filters_failed=15096, move_not_fresh=7469, breakout_stale=2468, retest_proximity_failed=978, volume_spike_missing=170, missing_fvg_or_orderblock=13, move_exhausted=10
- **EVAL::WHALE_MOMENTUM** (total=52301): momentum_reject=43936, recent_ticks_insufficient=5990, basic_filters_failed=2375

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=23): execution:overextended=23
- **DIVERGENCE_CONTINUATION** (total=292): setup_compat:regime_VOLATILE_UNSUITABLE=276, setup_compat:regime_BREAKOUT_EXPANSION=16
- **FAILED_AUCTION_RECLAIM** (total=1434): setup_compat:regime_STRONG_TREND=775, execution:overextended=491, setup_compat:regime_VOLATILE_UNSUITABLE=85, context_floor=83
- **FUNDING_EXTREME_SIGNAL** (total=453): execution:trigger_not_confirmed=418, context_floor=35
- **LIQUIDATION_REVERSAL** (total=15): execution:trigger_not_confirmed=15
- **LIQUIDITY_SWEEP_REVERSAL** (total=5586): setup_compat:regime_STRONG_TREND=2539, execution:trigger_not_confirmed=1653, execution:overextended=1394
- **MA_CROSS_TREND_SHIFT** (total=8): execution:overextended=2, setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_DIRTY_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=4235): setup_compat:regime_STRONG_TREND=2111, setup_compat:regime_WEAK_TREND=1801, execution:overextended=288, entry_quality=35
- **MOVER_AVWAP_SCALP** (total=1032): execution:overextended=697, entry_quality=204, execution:trigger_not_confirmed=131
- **MOVER_TREND_PULLBACK** (total=10319): execution:trigger_not_confirmed=5442, execution:overextended=3253, entry_quality=1624
- **QUIET_COMPRESSION_BREAK** (total=2): execution:overextended=2
- **RANGE_FADE** (total=2312): setup_compat:regime_STRONG_TREND=1287, setup_compat:regime_WEAK_TREND=721, setup_compat:regime_VOLATILE_UNSUITABLE=209, execution:overextended=94, setup_compat:regime_BREAKOUT_EXPANSION=1
- **TREND_PULLBACK_EMA** (total=1242): setup_compat:regime_CLEAN_RANGE=655, setup_compat:regime_DIRTY_RANGE=342, entry_quality=161, setup_compat:regime_VOLATILE_UNSUITABLE=84
- **VOLUME_SURGE_BREAKOUT** (total=4): execution:overextended=4

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 148399 | 37.1% |
| TRENDING_DOWN | 91871 | 23.0% |
| TRENDING_UP | 79808 | 19.9% |
| QUIET | 58364 | 14.6% |
| VOLATILE | 21710 | 5.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **115**
- Average confidence gap to threshold: **11.36** (samples=115) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=10, BTCUSDT=8, MAGMAUSDT=8, SUIUSDT=7, FILUSDT=7, ARBUSDT=7, INITUSDT=6, TRUMPUSDT=6, XMRUSDT=5, QNTUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 166 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 17 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 113 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 3 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 17 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 4 |
| LIQUIDATION_REVERSAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 6 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 2 |
| MA_CROSS_TREND_SHIFT | filtered | quiet_scalp_min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 22 |
| MEAN_REVERT | kept | min_confidence_pass | 8 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 268 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 10 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 8 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 417 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2715 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 25 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3753 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 91 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 34 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 72 |
| SR_FLIP_RETEST | filtered | min_confidence | 37 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 20 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 102 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 21 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 147 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 25 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 5 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 183 | 57.01 | 64.34 | 7.33 | 20.61 | 19.66 | 17.75 | 1.85 | 13.02 |
| DIVERGENCE_CONTINUATION | kept | 113 | 69.77 | 65.00 | -4.77 | 20.92 | 19.79 | 17.87 | 1.51 | 1.76 |
| FAILED_AUCTION_RECLAIM | filtered | 3 | 53.03 | 65.00 | 11.97 | 19.40 | 20.00 | 20.00 | 2.00 | 6.00 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.50 | 65.00 | 2.50 | 20.80 | 20.00 | 20.00 | 5.00 | 8.80 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 41.90 | 62.35 | 20.45 | 20.02 | 15.69 | 16.90 | 2.82 | 15.12 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.70 | 65.00 | 1.30 | 21.20 | 18.80 | 17.00 | 0.00 | 12.00 |
| LIQUIDATION_REVERSAL | filtered | 4 | 67.40 | 10.00 | -57.40 | 20.10 | 9.40 | 15.30 | 6.00 | 2.00 |
| LIQUIDATION_REVERSAL | kept | 1 | 70.70 | 65.00 | -5.70 | 20.30 | 10.40 | 17.50 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 45.65 | 65.00 | 19.35 | 22.75 | 19.89 | 18.66 | 0.41 | 4.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 70.73 | 65.00 | -5.73 | 20.82 | 19.45 | 16.93 | 1.67 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.00 | 62.33 | 6.33 | 20.57 | 16.80 | 15.80 | 0.00 | 13.17 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 64.73 | 65.00 | 0.27 | 20.63 | 16.93 | 15.80 | 0.00 | 1.93 |
| MEAN_REVERT | filtered | 22 | 63.29 | 65.00 | 1.71 | 18.96 | 14.27 | 17.00 | 0.00 | 4.80 |
| MEAN_REVERT | kept | 8 | 69.97 | 65.00 | -4.97 | 18.69 | 14.15 | 17.41 | 0.00 | 4.60 |
| MOVER_AVWAP_SCALP | filtered | 286 | 58.61 | 63.39 | 4.78 | 20.72 | 15.97 | 15.80 | 3.82 | 15.42 |
| MOVER_AVWAP_SCALP | kept | 417 | 75.99 | 65.00 | -10.99 | 20.77 | 16.22 | 15.80 | 4.43 | 6.61 |
| MOVER_TREND_PULLBACK | filtered | 2740 | 55.49 | 64.26 | 8.77 | 20.25 | 18.44 | 15.80 | 4.18 | 19.43 |
| MOVER_TREND_PULLBACK | kept | 3753 | 77.03 | 65.00 | -12.03 | 19.73 | 18.45 | 15.80 | 4.28 | 1.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 82.10 | 65.00 | -17.10 | 20.40 | 19.70 | 18.00 | 4.00 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 125 | 51.27 | 64.62 | 13.35 | 20.05 | 18.62 | 20.00 | 0.00 | 11.66 |
| QUIET_COMPRESSION_BREAK | kept | 72 | 75.18 | 65.00 | -10.18 | 22.81 | 18.85 | 20.00 | 0.00 | -0.19 |
| SR_FLIP_RETEST | filtered | 41 | 56.49 | 65.00 | 8.51 | 21.97 | 20.00 | 19.47 | 1.80 | 12.74 |
| SR_FLIP_RETEST | kept | 20 | 71.33 | 65.00 | -6.33 | 20.91 | 20.00 | 17.44 | 2.10 | 0.47 |
| TREND_PULLBACK_EMA | filtered | 123 | 56.94 | 64.80 | 7.86 | 21.13 | 19.60 | 18.58 | 5.21 | 19.53 |
| TREND_PULLBACK_EMA | kept | 147 | 77.71 | 65.00 | -12.71 | 20.49 | 19.90 | 17.68 | 5.04 | 0.88 |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 50.12 | 63.24 | 13.12 | 18.20 | 18.80 | 20.00 | 3.76 | 10.93 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 78.20 | 65.00 | -13.20 | 16.98 | 17.48 | 20.00 | 5.50 | 1.80 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 183 | 57.01 | 21.11 | 15.70 | 4.39 | 12.81 | 5.46 | 8.68 | 1.85 |
| DIVERGENCE_CONTINUATION | kept | 113 | 69.77 | 23.30 | 15.79 | 6.00 | 11.99 | 5.16 | 8.99 | 1.51 |
| FAILED_AUCTION_RECLAIM | filtered | 3 | 53.03 | 22.33 | 14.00 | 12.00 | 14.00 | 5.00 | 4.70 | 2.00 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.50 | 25.00 | 14.00 | 3.00 | 9.00 | 9.00 | 6.30 | 5.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 41.90 | 23.12 | 10.94 | 7.41 | 14.35 | 7.15 | 2.69 | 2.82 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.70 | 25.00 | 18.00 | 3.00 | 17.00 | 5.00 | 7.70 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 4 | 67.40 | 25.00 | 8.00 | 12.00 | 8.00 | 5.00 | 5.30 | 6.00 |
| LIQUIDATION_REVERSAL | kept | 1 | 70.70 | 25.00 | 8.00 | 12.00 | 8.00 | 5.00 | 6.70 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 45.65 | 24.88 | 14.24 | 3.00 | 13.47 | 5.18 | 4.15 | 0.41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 70.73 | 20.33 | 16.67 | 5.50 | 11.83 | 5.58 | 9.15 | 1.67 |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.00 | 19.67 | 14.00 | 4.00 | 14.33 | 7.83 | 9.33 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 64.73 | 16.33 | 14.00 | 4.00 | 15.00 | 7.33 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 22 | 63.29 | 18.82 | 14.00 | 10.64 | 13.00 | 5.00 | 6.63 | 0.00 |
| MEAN_REVERT | kept | 8 | 69.97 | 24.00 | 14.50 | 10.88 | 13.00 | 5.00 | 7.20 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 286 | 58.61 | 17.26 | 18.00 | 12.28 | 14.16 | 6.84 | 6.34 | 3.82 |
| MOVER_AVWAP_SCALP | kept | 417 | 75.99 | 19.87 | 18.02 | 11.48 | 14.00 | 7.23 | 8.30 | 4.43 |
| MOVER_TREND_PULLBACK | filtered | 2740 | 55.49 | 18.28 | 18.03 | 7.65 | 13.32 | 5.91 | 9.15 | 4.18 |
| MOVER_TREND_PULLBACK | kept | 3753 | 77.03 | 19.19 | 18.02 | 7.94 | 12.88 | 6.86 | 9.45 | 4.28 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 82.10 | 17.00 | 18.00 | 15.00 | 15.50 | 8.75 | 6.85 | 4.00 |
| QUIET_COMPRESSION_BREAK | filtered | 125 | 51.27 | 19.75 | 15.09 | 13.13 | 14.00 | 6.03 | 3.38 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 72 | 75.18 | 18.00 | 16.22 | 12.46 | 14.08 | 6.88 | 8.97 | 0.00 |
| SR_FLIP_RETEST | filtered | 41 | 56.49 | 21.29 | 17.02 | 3.00 | 14.29 | 5.17 | 6.65 | 1.80 |
| SR_FLIP_RETEST | kept | 20 | 71.33 | 22.60 | 16.00 | 4.95 | 13.35 | 5.50 | 7.90 | 2.10 |
| TREND_PULLBACK_EMA | filtered | 123 | 56.94 | 14.28 | 18.00 | 8.04 | 14.68 | 6.77 | 9.49 | 5.21 |
| TREND_PULLBACK_EMA | kept | 147 | 77.71 | 19.05 | 18.00 | 7.61 | 14.07 | 6.31 | 9.68 | 5.04 |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 50.12 | 13.20 | 15.44 | 13.68 | 13.76 | 6.48 | 5.53 | 3.76 |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 78.20 | 25.00 | 14.00 | 12.00 | 11.00 | 4.50 | 8.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 183 | 57.01 | 0.00 | 0.00 | 1.46 | 0.00 | 1.06 | 0.03 | 0.00 | 0.00 | **2.55** |
| DIVERGENCE_CONTINUATION | kept | 113 | 69.77 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.20** |
| FAILED_AUCTION_RECLAIM | filtered | 3 | 53.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 62.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 41.90 | 0.00 | 0.00 | 3.53 | 0.00 | 0.71 | 0.00 | 0.00 | 0.00 | **4.24** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 63.70 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDATION_REVERSAL | filtered | 4 | 67.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | kept | 1 | 70.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 45.65 | 0.00 | 0.00 | 0.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.47** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 6 | 70.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 3 | 56.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 64.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 22 | 63.29 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| MEAN_REVERT | kept | 8 | 69.97 | 0.00 | 0.00 | 4.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.60** |
| MOVER_AVWAP_SCALP | filtered | 286 | 58.61 | 0.00 | 0.00 | 0.70 | 0.00 | 4.66 | 0.00 | 0.00 | 1.17 | **6.53** |
| MOVER_AVWAP_SCALP | kept | 417 | 75.99 | 0.00 | 0.00 | 0.72 | 0.00 | 3.82 | 0.00 | 0.00 | 0.20 | **4.74** |
| MOVER_TREND_PULLBACK | filtered | 2740 | 55.49 | 0.25 | 0.00 | 2.24 | 0.00 | 0.08 | 0.05 | 0.00 | 0.01 | **2.63** |
| MOVER_TREND_PULLBACK | kept | 3753 | 77.03 | 0.00 | 0.00 | 0.59 | 0.00 | 0.16 | 0.03 | 0.00 | 0.00 | **0.78** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 82.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 125 | 51.27 | 0.00 | 0.00 | 0.46 | 0.00 | 0.00 | 0.29 | 0.00 | 2.58 | **3.33** |
| QUIET_COMPRESSION_BREAK | kept | 72 | 75.18 | 0.00 | 0.00 | 0.20 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | **0.32** |
| SR_FLIP_RETEST | filtered | 41 | 56.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 20 | 71.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 123 | 56.94 | 0.00 | 0.00 | 2.13 | 0.00 | 4.00 | 0.29 | 0.00 | 0.00 | **6.42** |
| TREND_PULLBACK_EMA | kept | 147 | 77.71 | 0.00 | 0.00 | 1.01 | 0.00 | 0.34 | 0.04 | 0.00 | 0.00 | **1.39** |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 50.12 | 0.00 | 0.00 | 1.73 | 0.00 | 0.00 | 0.00 | 0.00 | 2.16 | **3.89** |
| VOLUME_SURGE_BREAKOUT | kept | 5 | 78.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **188797 held of 852037 seen** across 21 strategies; 4270 cells past the sample floor; **2281 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 48768 | 632/48136/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 25241 | 207/25034/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 14846 | 249/14597/0 | 45% | -0.15 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14156 | 151/14005/0 | 36% | -0.32 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 13071 | 75/12996/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 10451 | 103/10348/0 | 38% | -0.42 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9250 | 438/8812/0 | 44% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8228 | 0/0/8228 | 43% | -0.08 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.18R) | ASIA/RANGE/NORMAL/BTC_FALLING (-0.92R) |
| SHADOW_RANGE_FADE | 7733 | 0/0/7733 | 36% | -0.14 | NY/MARKDOWN/CASCADE/BTC_FALLING (+0.37R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_FUNDING_FADE | 7230 | 0/0/7230 | 34% | -0.42 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6609 | 24/6585/0 | 47% | -0.25 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5524 | 69/5455/0 | 37% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4241 | 2/4239/0 | 31% | -0.46 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3983 | 0/3983/0 | 28% | -0.41 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 2552 | 6/2546/0 | 47% | +0.19 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1716 | 0/0/1716 | 52% | -0.08 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.60R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 542 | 0/542/0 | 37% | -0.23 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 220 | 34/186/0 | 44% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 62 | 4/58/0 | 42% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 382 | 27% / -0.58R | 382 | 53% / -0.09R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1305 | 38% / -0.38R | 1305 | 50% / -0.09R | +0.29 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1583 | 42% / -0.37R | 1583 | 57% / -0.12R | +0.25 | **ATR** |
| LIQUIDATION_REVERSAL | 34 | 26% / -0.56R | 34 | 47% / -0.32R | +0.24 | **ATR** |
| SR_FLIP_RETEST | 676 | 46% / -0.27R | 676 | 50% / -0.15R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 68 | 46% / -0.16R | 68 | 50% / -0.04R | +0.12 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 223 | 38% / -0.17R | 223 | 48% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 9000 | 48% / -0.14R | 9000 | 53% / -0.02R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 2710 | 45% / -0.16R | 2710 | 51% / -0.05R | +0.11 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1540 | 41% / -0.23R | 1540 | 44% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1890 | 48% / -0.12R | 1890 | 53% / -0.06R | +0.06 | **ATR** |
| RANGE_FADE | 138 | 41% / +0.03R | 138 | 47% / +0.08R | +0.05 | **ATR** |
| MEAN_REVERT | 454 | 47% / -0.15R | 454 | 46% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1605 | 47% / -0.11R | 1605 | 47% / -0.12R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12010 | 28% | -0.30R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2710 | 49% | -0.04R | 239 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 142 | 49% | -0.05R | 71 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1857 | 39% / -0.16R | +0.85 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1676 | 33% / -0.21R | +0.85 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3269 | 35% / -0.19R | +0.66 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11003 | 36% / -0.19R | +0.34 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2194 | 36% / -0.14R | +0.14 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1555 | 37% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1277 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 327 | 31% / -0.36R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 496 | 31% / -0.24R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 375 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 96 | 44% / -0.00R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 596 | 34% / -0.29R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 103 | 29% / -0.35R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 44 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 24 | 46% / +0.54R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 350/6) (sustained 350 cycles)
- **ALERT** `range_fade_emission` — 4612 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=2546, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 240/6) (sustained 240 cycles)
- **ALERT** `tuned_variants` — 396 non-stamps — atr_arm_uncomputable=396 (seen=10110 stamped=1197 skipped=8517) (streak 347/6) (sustained 347 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 116741540 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 20 arms current, none stalled; covering 2091/2091 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 40 arms current, none stalled; covering 1092/1092 signals (100%) | 0 |
| auto_dispatch | ok | 69 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=70. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 292/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 67328.30 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 75 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1203 dup bars, 0 undedupable; ws 0 out-of-order, 423 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 61 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +30 / upstream +23 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2019/2038 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 205 open dark rows are not being advanced (worst: JTOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 2/120) | 2 |
| dark_sar_arms | ok | no open arms; covering 2007/2026 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 29380410 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 350/6) | 350 |
| emission_controller | ok | last cycle 379s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=428, MOVER_AVWAP_SCALP=393, MOVER_TREND_PULLBACK=4422, RANGE_FADE=343, TREND_PULLBACK_EMA=414), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 2/6) | 2 |
| firestore_read_budget | ok | 1,309 reads/day of 50,000 [engine 1,288, signing 21]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 1479 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +11 / upstream +509 | 0 |
| indicator_cache_key | ok | 136167 frozen value(s) avoided; 335725 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.32R over n=5455 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +38 / upstream +509 | 0 |
| mover_admission_metadata | ok | 946 symbols known, 237 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 11 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2149 rows held, 3549657 evicted (sampled: execution:trigger_not_confirmed 288/1250399, execution:overextended 288/1102821, setup_compat:regime_STRONG_TREND 288/608681) | 0 |
| price_action_lane | ok | 744024 evaluated, 1261 emitted; layer1 1261 stamped / 0 blind; cooldown=121425, delta_opposed=68031, no_footprint=283427, no_opposing_target=336, no_sweep=207800, rr_below_floor=61744 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 4612 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.19R over n=2546, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 240/6) | 240 |
| range_fade_path | ok | output +11 / upstream +509 | 0 |
| sar_alignment_crosscheck | ok | 757/21898 disagreed (3.5%) | 0 |
| sar_exit_shadow | ok | output +10 / upstream +509 | 0 |
| sar_hold_arm | ok | 1877 held arms settled, 123 unscored, 40 still walking (33 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 15/73 unfetchable (21%); top cause: located bar does not contain the stamp; symbols: ADAUSDT, AGTUSDT, BARDUSDT, BNBUSDT, CAPUSDT +9 more | 0 |
| sar_live_arms | ok | 40 arms current, none stalled; covering 1091/1091 signals (100%) | 0 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 56 still mid-window | 0 |
| scan_cycle | ok | last 19.15s, worst 300.37s over 8912 lifetime cycles; lifetime 364 over 60s, 51 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.04s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 311810 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 17s ago (40.85s to run, worst 198.54s), 1130 overrun(s) of 7394 cycles, TTL 900s; slowest trail_governor=12.02s, router_delivery=10.74s, engine_state=7.48s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +81 / upstream +509 | 0 |
| structural_snap | ok | 6000/6000 measured, 32 blind, 0 levels moved (refusals: redetect_cooldown=925) | 0 |
| structural_veto_lane | ok | 1876 stamped; 0 with no readable level book, 75 with clear air ahead, 1501 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +509 / upstream +23 | 0 |
| tuned_variants | violating | 396 non-stamps — atr_arm_uncomputable=396 (seen=10110 stamped=1197 skipped=8517) (streak 347/6) | 347 |
| unlock_shorts | ok | 17 open, 42 scheduled, calendar 17.8h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 18 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1922070`
- `Path funnel` emissions: `47`
- `Regime distribution` emissions: `47`
- `QUIET_SCALP_BLOCK` events: `115`
- `confidence_gate` events: `8138`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **24**
- Total REST-fallback activations: **7**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 7 | 29566 | 57357 | 59686 | 0 |
| futures_aggtrade | 11 | 23358 | 50202 | 51835 | 0 |
| futures_depth | 1 | 23779 | 23779 | 23779 | 0 |
| futures_liq | 5 | 4839 | 7986 | 35766 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 7 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=309122] state[populated=309122] buckets[many=309122] sources[none] quality[none]
- funding_rate: presence[absent=32989, present=276133] state[empty=32989, populated=276133] buckets[few=276133, none=32989] sources[none] quality[none]
- liquidation_clusters: presence[absent=177409, present=131713] state[empty=177409, populated=131713] buckets[few=108217, none=177409, some=23496] sources[none] quality[none]
- oi_snapshot: presence[absent=32989, present=276133] state[empty=32989, populated=276133] buckets[few=157, many=274939, none=32989, some=1037] sources[none] quality[none]
- order_book: presence[absent=103819, present=205303] state[populated=205303, unavailable=103819] buckets[few=205303, none=103819] sources[book_ticker=205303, unavailable=103819] quality[none=103819, top_of_book_only=205303]
- orderblocks: presence[absent=309122] state[empty=309122] buckets[none=309122] sources[measured_dark=309122] quality[none]
- recent_ticks: presence[present=309122] state[populated=309122] buckets[many=309122] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.289531946182251` sec
- Median create→first breach: `3738.591637134552` sec
- Median create→terminal: `3738.5916860103607` sec
- Median first breach→terminal: `6.604194641113281e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.8789196625774893 | 1.0088208455845082 | 0.858343573114427 | 0 | 3 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.096283226130368 | 2.267745572523215 | 0.9222296750968324 | 0 | 2 |
| MOVER_TREND_PULLBACK | 32 | 32 | 3.9534856804357044 | 3.0 | 1.3381743889154127 | 24 | 8 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 1.7789082881798126 | 1.94256999282125 | 0.9157499059255276 | 0 | 1 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.5626969706430818 | 1.7092939682096193 | 0.8962053695432837 | 0 | 4 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.6175000000000019 | 1.209296542074067 | 0.5106274420837477 | 0 | 1 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 1.4659008426168403 | 1.3184291459663944 | 0 | 0 | 0 | 2 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2.31583970397469 | 2.9800801570713027 | 2 | 0 | 0 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 32 | 5.777727502067092 | 3.9731250000000014 | 8 | 2 | 0 | 24 | 5 | 0 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 2.488460766606458 | 2.6683724663857147 | 1 | 0 | 0 | 0 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 4 | 3.9222951839308084 | 2.3440431321543547 | 0 | 0 | 0 | 4 | 0 | 0 |
| TREND_PULLBACK_EMA | 1 | 1.6847304588570318 | 1.6847304588570318 | 0 | 0 | 0 | 0 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | -0.1462 | 3942.1524951457977 | 3942.1525661945343 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.1782 | 9016.349775075912 | 9016.34981906414 |
| MOVER_TREND_PULLBACK | 32 | 32 | 37.5 | 34.4 | 37.5 | 0.0 | 0.8048 | 2577.054681658745 | 2577.273337006569 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.7789 | 17094.15282201767 | 17094.15284180641 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 25.0 | 25.0 | 25.0 | 0.0 | 0.5591 | 27589.10893845558 | 27589.10899400711 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 10003.218584060669 | 10003.218652009964 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 463 | 8 | 216 | 0.0 | 0.0 | None | None | 247 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1620 | 60 | 1033 | 0.0 | 0.0 | 10003.218584060669 | 10003.218652009964 | 587 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-61`
- Gating Δ: `-14671`
- No-generation Δ: `-147483`
- Fast failures Δ: `-3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.5454, "current_avg_pnl": -0.1462, "current_win_rate": 33.3, "previous_avg_pnl": 0.3992, "previous_win_rate": 38.5, "win_rate_delta": -5.2}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.699, "current_avg_pnl": 0.8048, "current_win_rate": 37.5, "previous_avg_pnl": 0.1058, "previous_win_rate": 28.6, "win_rate_delta": 8.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1752, "current_avg_pnl": 0.5591, "current_win_rate": 25.0, "previous_avg_pnl": 0.7343, "previous_win_rate": 40.0, "win_rate_delta": -15.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": -31, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 31, "geometry_changed_delta": 0, "geometry_preserved_delta": 96, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 7737.34, "median_terminal_delta_sec": 7737.05, "sl_rate_delta": 0.0, "win_rate_delta": -50.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
