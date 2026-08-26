# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `10822` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 99 | 99 | 80 | 4 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10048 | 10048 | 9184 | 16 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 71586 | 71612 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 62345 | 62349 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 61952 | 59269 | 3063 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 62379 | 61583 | 876 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 61886 | 61799 | 128 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 50964 | 50987 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 62468 | 62502 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 62509 | 59756 | 3880 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 77225 | 83800 | 766 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 71644 | 62466 | 14704 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 61346 | 61355 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 62357 | 62359 | 13 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 61924 | 61876 | 74 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 63645 | 62867 | 1076 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 61349 | 61724 | 147 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 50412 | 46534 | 4302 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 50853 | 50487 | 464 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 71528 | 71564 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 50992 | 50963 | 76 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3007 | 3007 | 2604 | 8 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 457 | 457 | 48 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20920 | 20920 | 20713 | 17 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 3 | 2 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8845 | 8845 | 7908 | 7 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1984 | 1984 | 1242 | 52 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 36493 | 36493 | 26669 | 322 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 24 | 24 | 24 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 457 | 457 | 392 | 14 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 2719 | 2719 | 2684 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 418 | 418 | 337 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1876 | 1876 | 1551 | 28 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 68 | 68 | 28 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 2748 | 2748 | 180 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=71612): breakout_not_found=41840, basic_filters_failed=14566, move_not_fresh=10158, breakout_stale=3605, retest_proximity_failed=1111, volume_spike_missing=301, missing_fvg_or_orderblock=12, move_exhausted=10, insufficient_candles=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=62349): cls_disabled_merged_into_lsr=62349
- **EVAL::DIVERGENCE_CONTINUATION** (total=59269): cvd_divergence_failed=26897, h1_trend_not_aligned=16899, basic_filters_failed=10433, ema_alignment_reject=3839, retest_proximity_failed=917, missing_fvg_or_orderblock=284
- **EVAL::FAILED_AUCTION_RECLAIM** (total=61583): auction_not_detected=44137, basic_filters_failed=10295, reclaim_hold_failed=3022, tail_too_small=2598, regime_blocked=1514, rsi_reject=17
- **EVAL::FUNDING_EXTREME** (total=61799): funding_not_extreme=49059, basic_filters_failed=9468, missing_funding_rate=2129, ema_alignment_reject=669, rsi_reject=294, cvd_divergence_failed=95, momentum_reject=74, missing_fvg_or_orderblock=6, insufficient_candles=5
- **EVAL::LIQUIDATION_REVERSAL** (total=50987): cascade_threshold_not_met=40300, basic_filters_failed=10195, cvd_divergence_failed=267, rsi_reject=207, insufficient_candles=9, volume_spike_missing=6, missing_fvg_or_orderblock=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=62502): no_ma_cross=50596, basic_filters_failed=10454, ma_cross_htf_misaligned=1130, ma_cross_cooldown=322
- **EVAL::MEAN_REVERT** (total=59756): no_extension=51988, basic_filters_failed=7768
- **EVAL::MOVER_AVWAP_SCALP** (total=83800): no_avwap_tag=40851, no_mover_leg=17356, basic_filters_failed=14777, avwap_slope_against=6742, avwap_reclaim_no_volume=2319, no_avwap_reclaim=1726, anchor_too_recent=20, insufficient_candles=9
- **EVAL::MOVER_TREND_PULLBACK** (total=62466): mover_run_too_small=29349, no_reclaim=16086, basic_filters_failed=14672, no_pullback_tag=2350, insufficient_candles=9
- **EVAL::OPENING_RANGE_BREAKOUT** (total=61355): feature_disabled=61355
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=62359): regime_blocked=47566, breakout_not_found=11503, basic_filters_failed=2130, adx_reject=1117, ema_alignment_reject=43
- **EVAL::QUIET_COMPRESSION_BREAK** (total=61876): compression_not_detected=35116, regime_blocked=16210, basic_filters_failed=8150, breakout_not_detected=2140, volume_confirmation_failed=247, rsi_reject=13
- **EVAL::RANGE_FADE** (total=62867): no_range_edge=55096, basic_filters_failed=7771
- **EVAL::SR_FLIP_RETEST** (total=61724): flip_close_not_confirmed=43650, basic_filters_failed=10262, long_break_volume_thin=2121, h1_break_not_confirmed=1723, retest_out_of_zone=1588, regime_blocked=1489, reclaim_hold_failed=545, long_acceptance_not_held=127, ema_alignment_reject=96, whipsaw_flip=56, wick_quality_failed=48, missing_fvg_or_orderblock=19
- **EVAL::STANDARD** (total=46534): momentum_reject=13685, adx_reject=8345, macd_reject=7176, sweeps_not_detected=6868, basic_filters_failed=6317, ema_alignment_reject=2968, htf_poi_unanchored=935, invalid_sl_geometry=206, rsi_reject=34
- **EVAL::TREND_PULLBACK** (total=50487): h1_trend_not_aligned=16416, ema_alignment_reject=9547, basic_filters_failed=6095, h1_pullback_not_confirmed=5726, ema_not_tested_prev=4328, no_ema_reclaim_close=3648, body_conviction_fail=1863, rsi_reject=1395, prev_already_below_emas=456, prev_already_above_emas=380, no_prev_high_break=241, no_prev_low_break=220, momentum_flat=113, ema21_not_tagged=40, missing_fvg_or_orderblock=13, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=71564): breakout_not_found=47297, basic_filters_failed=14562, move_not_fresh=6487, breakout_stale=2070, retest_proximity_failed=871, volume_spike_missing=230, missing_fvg_or_orderblock=38, insufficient_candles=9
- **EVAL::WHALE_MOMENTUM** (total=50963): momentum_reject=34965, recent_ticks_insufficient=12945, basic_filters_failed=3053

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=6): execution:overextended=6
- **DIVERGENCE_CONTINUATION** (total=203): setup_compat:regime_VOLATILE_UNSUITABLE=202, setup_compat:regime_BREAKOUT_EXPANSION=1
- **FAILED_AUCTION_RECLAIM** (total=518): execution:overextended=285, setup_compat:regime_STRONG_TREND=194, context_floor=34, setup_compat:regime_VOLATILE_UNSUITABLE=5
- **FUNDING_EXTREME_SIGNAL** (total=329): execution:trigger_not_confirmed=329
- **LIQUIDATION_REVERSAL** (total=1): execution:trigger_not_confirmed=1
- **LIQUIDITY_SWEEP_REVERSAL** (total=4474): execution:overextended=1865, execution:trigger_not_confirmed=1638, setup_compat:regime_STRONG_TREND=971
- **MA_CROSS_TREND_SHIFT** (total=5): setup_compat:regime_DIRTY_RANGE=4, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=2689): setup_compat:regime_STRONG_TREND=1341, setup_compat:regime_WEAK_TREND=961, execution:overextended=386, entry_quality=1
- **MOVER_AVWAP_SCALP** (total=1003): execution:overextended=758, execution:trigger_not_confirmed=171, entry_quality=74
- **MOVER_TREND_PULLBACK** (total=13571): execution:trigger_not_confirmed=7598, execution:overextended=4962, entry_quality=1011
- **QUIET_COMPRESSION_BREAK** (total=2): execution:overextended=2
- **RANGE_FADE** (total=1448): setup_compat:regime_STRONG_TREND=867, setup_compat:regime_WEAK_TREND=426, execution:overextended=86, setup_compat:regime_VOLATILE_UNSUITABLE=69
- **SR_FLIP_RETEST** (total=6): setup_compat:regime_VOLATILE_UNSUITABLE=6
- **TREND_PULLBACK_EMA** (total=1631): setup_compat:regime_DIRTY_RANGE=801, setup_compat:regime_CLEAN_RANGE=731, setup_compat:regime_VOLATILE_UNSUITABLE=62, entry_quality=37
- **VOLUME_SURGE_BREAKOUT** (total=7): execution:overextended=7
- **WHALE_MOMENTUM** (total=2216): execution:trigger_not_confirmed=2216

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 212394 | 61.6% |
| TRENDING_DOWN | 48319 | 14.0% |
| QUIET | 38839 | 11.3% |
| TRENDING_UP | 36648 | 10.6% |
| VOLATILE | 8480 | 2.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **84**
- Average confidence gap to threshold: **13.14** (samples=84) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=63, XMRUSDT=9, SUIUSDT=9, SOLUSDT=2, 1000SHIBUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 19 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 121 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 121 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 123 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 50 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 19 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 77 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 3 |
| MEAN_REVERT | filtered | min_confidence | 33 |
| MEAN_REVERT | kept | min_confidence_pass | 30 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 92 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 7 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 413 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 679 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3648 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 9 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 31 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 15 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 13 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 32 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 135 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 25 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 15 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 57 |
| WHALE_MOMENTUM | filtered | min_confidence | 43 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 19 | 69.84 | 65.00 | -4.84 | 20.65 | 19.14 | 20.00 | 3.84 | 2.84 |
| DIVERGENCE_CONTINUATION | filtered | 121 | 56.75 | 64.40 | 7.65 | 20.36 | 19.65 | 17.95 | 2.03 | 11.90 |
| DIVERGENCE_CONTINUATION | kept | 121 | 71.67 | 65.00 | -6.67 | 20.80 | 19.83 | 18.50 | 1.04 | -0.31 |
| FAILED_AUCTION_RECLAIM | filtered | 123 | 51.05 | 62.23 | 11.18 | 20.83 | 18.46 | 20.00 | 2.09 | 7.73 |
| FAILED_AUCTION_RECLAIM | kept | 50 | 69.02 | 65.00 | -4.02 | 22.83 | 18.70 | 20.00 | 3.23 | 4.22 |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 42.92 | 62.89 | 19.97 | 20.84 | 14.20 | 17.00 | 3.58 | 8.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 59.80 | 65.00 | 5.20 | 19.99 | 20.00 | 20.00 | 0.57 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 77 | 69.96 | 65.00 | -4.96 | 20.86 | 19.07 | 17.99 | 1.39 | 0.31 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 69.20 | 65.00 | -4.20 | 20.60 | 18.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 33 | 44.21 | 65.00 | 20.79 | 20.93 | 14.34 | 15.08 | 0.00 | 25.95 |
| MEAN_REVERT | kept | 30 | 69.95 | 65.00 | -4.95 | 20.98 | 14.89 | 16.36 | 0.00 | 1.87 |
| MOVER_AVWAP_SCALP | filtered | 99 | 60.31 | 61.11 | 0.80 | 19.93 | 15.37 | 15.80 | 4.49 | 18.28 |
| MOVER_AVWAP_SCALP | kept | 413 | 80.05 | 65.00 | -15.05 | 19.83 | 16.71 | 15.80 | 4.27 | 3.06 |
| MOVER_TREND_PULLBACK | filtered | 682 | 57.32 | 64.00 | 6.68 | 20.38 | 18.70 | 15.80 | 3.97 | 16.41 |
| MOVER_TREND_PULLBACK | kept | 3648 | 76.37 | 65.00 | -11.37 | 19.84 | 18.62 | 15.80 | 4.15 | 1.05 |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 52.30 | 65.00 | 12.70 | 20.48 | 17.70 | 20.00 | 0.00 | 8.52 |
| QUIET_COMPRESSION_BREAK | kept | 31 | 73.12 | 65.00 | -8.12 | 21.98 | 18.50 | 20.00 | 0.00 | 1.16 |
| SR_FLIP_RETEST | filtered | 15 | 54.19 | 65.00 | 10.81 | 21.43 | 20.00 | 15.20 | 2.53 | 12.07 |
| SR_FLIP_RETEST | kept | 13 | 65.35 | 65.00 | -0.35 | 21.97 | 20.00 | 16.49 | 1.81 | 1.92 |
| TREND_PULLBACK_EMA | filtered | 32 | 61.71 | 65.00 | 3.29 | 20.55 | 19.63 | 18.07 | 4.00 | 9.42 |
| TREND_PULLBACK_EMA | kept | 135 | 74.97 | 65.00 | -9.97 | 20.52 | 19.67 | 17.55 | 4.77 | 1.12 |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 48.10 | 60.28 | 12.18 | 20.73 | 16.58 | 20.00 | 3.14 | 5.78 |
| VOLUME_SURGE_BREAKOUT | kept | 15 | 72.45 | 65.00 | -7.45 | 20.81 | 19.14 | 20.00 | 4.77 | 2.40 |
| WHALE_MOMENTUM | filtered | 100 | 51.82 | 64.36 | 12.54 | 23.81 | 14.55 | 17.00 | 0.00 | 15.87 |
| WHALE_MOMENTUM | kept | 1 | 62.00 | 65.00 | 3.00 | 24.90 | 20.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 19 | 69.84 | 18.26 | 14.21 | 12.16 | 12.79 | 5.00 | 6.42 | 3.84 |
| DIVERGENCE_CONTINUATION | filtered | 121 | 56.75 | 22.22 | 13.79 | 4.29 | 13.24 | 4.83 | 8.39 | 2.03 |
| DIVERGENCE_CONTINUATION | kept | 121 | 71.67 | 24.01 | 16.68 | 5.18 | 11.74 | 5.77 | 8.68 | 1.04 |
| FAILED_AUCTION_RECLAIM | filtered | 123 | 51.05 | 20.43 | 16.83 | 6.15 | 13.98 | 5.25 | 4.78 | 2.09 |
| FAILED_AUCTION_RECLAIM | kept | 50 | 69.02 | 23.12 | 17.92 | 5.22 | 12.82 | 5.27 | 5.96 | 3.23 |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 42.92 | 22.89 | 9.58 | 6.32 | 12.58 | 8.11 | 3.54 | 3.58 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 59.80 | 20.43 | 14.00 | 6.86 | 14.00 | 3.93 | 8.01 | 0.57 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 77 | 69.96 | 23.18 | 16.13 | 5.34 | 11.45 | 5.98 | 6.79 | 1.39 |
| MA_CROSS_TREND_SHIFT | kept | 3 | 69.20 | 22.33 | 14.00 | 5.00 | 15.33 | 5.00 | 7.53 | 0.00 |
| MEAN_REVERT | filtered | 33 | 44.21 | 19.67 | 14.24 | 12.00 | 11.55 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 30 | 69.95 | 18.27 | 16.40 | 13.00 | 13.00 | 5.00 | 6.15 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 99 | 60.31 | 17.51 | 18.02 | 10.95 | 14.48 | 7.96 | 6.98 | 4.49 |
| MOVER_AVWAP_SCALP | kept | 413 | 80.05 | 18.47 | 18.07 | 12.52 | 14.48 | 7.08 | 8.49 | 4.27 |
| MOVER_TREND_PULLBACK | filtered | 682 | 57.32 | 17.77 | 18.01 | 7.67 | 12.89 | 6.39 | 9.28 | 3.97 |
| MOVER_TREND_PULLBACK | kept | 3648 | 76.37 | 19.52 | 18.01 | 7.82 | 12.37 | 6.36 | 9.35 | 4.15 |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 52.30 | 18.03 | 15.16 | 12.77 | 14.00 | 5.68 | 3.40 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 31 | 73.12 | 19.58 | 15.94 | 10.65 | 14.10 | 7.18 | 6.94 | 0.00 |
| SR_FLIP_RETEST | filtered | 15 | 54.19 | 24.47 | 8.00 | 4.60 | 14.00 | 5.33 | 7.33 | 2.53 |
| SR_FLIP_RETEST | kept | 13 | 65.35 | 21.31 | 12.62 | 5.08 | 14.00 | 5.38 | 7.08 | 1.81 |
| TREND_PULLBACK_EMA | filtered | 32 | 61.71 | 18.28 | 18.00 | 7.50 | 14.38 | 7.62 | 8.38 | 4.00 |
| TREND_PULLBACK_EMA | kept | 135 | 74.97 | 17.59 | 18.00 | 7.58 | 14.56 | 7.17 | 9.18 | 4.77 |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 48.10 | 17.32 | 14.00 | 12.24 | 11.84 | 5.00 | 4.14 | 3.14 |
| VOLUME_SURGE_BREAKOUT | kept | 15 | 72.45 | 9.60 | 17.73 | 14.00 | 14.00 | 5.00 | 9.75 | 4.77 |
| WHALE_MOMENTUM | filtered | 100 | 51.82 | 22.50 | 8.00 | 9.42 | 13.67 | 7.51 | 6.60 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 62.00 | 25.00 | 8.00 | 12.00 | 14.00 | 5.00 | 8.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 19 | 69.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 121 | 56.75 | 0.00 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.00** |
| DIVERGENCE_CONTINUATION | kept | 121 | 71.67 | 0.00 | 0.00 | 1.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.47** |
| FAILED_AUCTION_RECLAIM | filtered | 123 | 51.05 | 0.00 | 0.00 | 4.01 | 0.00 | 1.66 | 0.00 | 0.00 | 0.00 | **5.67** |
| FAILED_AUCTION_RECLAIM | kept | 50 | 69.02 | 0.00 | 0.00 | 2.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.24** |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 42.92 | 0.00 | 0.00 | 3.83 | 0.00 | 0.63 | 0.00 | 0.00 | 0.00 | **4.46** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 7 | 59.80 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 77 | 69.96 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.31** |
| MA_CROSS_TREND_SHIFT | kept | 3 | 69.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 33 | 44.21 | 0.00 | 0.00 | 0.00 | 0.00 | 7.49 | 0.00 | 0.00 | 0.00 | **7.49** |
| MEAN_REVERT | kept | 30 | 69.95 | 0.00 | 0.00 | 1.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.87** |
| MOVER_AVWAP_SCALP | filtered | 99 | 60.31 | 2.20 | 0.00 | 0.29 | 0.00 | 4.85 | 0.00 | 0.00 | 3.06 | **10.40** |
| MOVER_AVWAP_SCALP | kept | 413 | 80.05 | 0.00 | 0.00 | 0.12 | 0.00 | 2.73 | 0.00 | 0.00 | 0.22 | **3.07** |
| MOVER_TREND_PULLBACK | filtered | 682 | 57.32 | 0.00 | 0.00 | 2.50 | 0.00 | 0.34 | 0.04 | 0.00 | 0.00 | **2.88** |
| MOVER_TREND_PULLBACK | kept | 3648 | 76.37 | 0.00 | 0.00 | 0.43 | 0.00 | 0.20 | 0.01 | 0.00 | 0.00 | **0.64** |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 52.30 | 0.00 | 0.00 | 0.00 | 0.00 | 1.70 | 0.00 | 0.00 | 4.10 | **5.80** |
| QUIET_COMPRESSION_BREAK | kept | 31 | 73.12 | 0.00 | 0.00 | 0.46 | 0.00 | 0.83 | 0.00 | 0.00 | 0.35 | **1.64** |
| SR_FLIP_RETEST | filtered | 15 | 54.19 | 0.00 | 0.00 | 8.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.64** |
| SR_FLIP_RETEST | kept | 13 | 65.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 32 | 61.71 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.75** |
| TREND_PULLBACK_EMA | kept | 135 | 74.97 | 0.00 | 0.00 | 1.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.91** |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 48.10 | 0.00 | 0.00 | 0.64 | 0.00 | 0.58 | 0.00 | 0.00 | 1.20 | **2.42** |
| VOLUME_SURGE_BREAKOUT | kept | 15 | 72.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 100 | 51.82 | 0.00 | 0.00 | 0.00 | 0.00 | 5.47 | 0.00 | 0.00 | 0.00 | **5.47** |
| WHALE_MOMENTUM | kept | 1 | 62.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **39269 held of 82065 seen** across 20 strategies; 880 cells past the sample floor; **355 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 21475 | 63/21412/0 | 44% | -0.18 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.14R) |
| MOVER_AVWAP_SCALP | 3991 | 13/3978/0 | 39% | -0.32 | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (+1.03R) | ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.36R) |
| FAILED_AUCTION_RECLAIM | 2092 | 15/2077/0 | 38% | -0.28 | ASIA/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.82R) | OVERLAP/MARKUP/NORMAL/BTC_RISING/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 1970 | 0/0/1970 | 42% | -0.10 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.72R) | NY/RANGE/EXPANDED/BTC_RISING (-0.89R) |
| TREND_PULLBACK_EMA | 1938 | 0/1938/0 | 42% | -0.18 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL (+0.72R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.31R) |
| DIVERGENCE_CONTINUATION | 1742 | 0/1742/0 | 54% | +0.02 | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.05R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_RANGE_FADE | 1642 | 0/0/1642 | 35% | -0.08 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+0.78R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.87R) |
| WHALE_MOMENTUM | 936 | 0/936/0 | 31% | -0.49 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.59R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.37R) |
| SHADOW_FUNDING_FADE | 903 | 0/0/903 | 43% | -0.25 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-0.93R) |
| QUIET_COMPRESSION_BREAK | 739 | 14/725/0 | 21% | -0.26 | ASIA/DISTRIBUTION/NORMAL/BTC_RISING (-0.06R) | OVERLAP/QUIET/EXPANDED/BTC_RISING (-0.41R) |
| FUNDING_EXTREME_SIGNAL | 442 | 0/442/0 | 29% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (-1.20R) |
| VOLUME_SURGE_BREAKOUT | 406 | 0/406/0 | 48% | +0.10 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| MEAN_REVERT | 312 | 2/310/0 | 74% | +0.56 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| LIQUIDITY_SWEEP_REVERSAL | 240 | 4/236/0 | 39% | -0.21 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-0.28R) | LONDON/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (-0.54R) |
| SHADOW_CASCADE_REVERSAL | 215 | 0/0/215 | 59% | -0.00 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) |
| BREAKDOWN_SHORT | 142 | 6/136/0 | 8% | -0.86 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| SR_FLIP_RETEST | 48 | 0/48/0 | 83% | +0.53 | — | — |
| RANGE_FADE | 18 | 0/18/0 | 22% | -0.40 | — | — |
| MA_CROSS_TREND_SHIFT | 14 | 0/14/0 | 29% | -0.14 | — | — |
| LIQUIDATION_REVERSAL | 4 | 0/4/0 | 0% | -1.16 | — | — |

- **Strongest cells**: `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR` +1.13R (n=27, STRONG); `MEAN_REVERT @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL` +1.07R (n=50, STRONG)
- **Weakest cells**: `WHALE_MOMENTUM @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MAJOR` -1.37R (n=26, NEGATIVE); `WHALE_MOMENTUM @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL` -1.37R (n=26, NEGATIVE); `MOVER_AVWAP_SCALP @ ASIA/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.36R (n=15, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 37 | 30% / -0.51R | 37 | 49% / -0.10R | +0.40 | **ATR** |
| TREND_PULLBACK_EMA | 170 | 46% / -0.16R | 170 | 53% / -0.04R | +0.11 | **ATR** |
| MEAN_REVERT | 30 | 60% / +0.19R | 30 | 60% / +0.30R | +0.11 | **ATR** |
| MOVER_AVWAP_SCALP | 284 | 48% / -0.14R | 284 | 54% / -0.04R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 151 | 43% / -0.21R | 151 | 45% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 96 | 34% / -0.40R | 96 | 36% / -0.30R | +0.09 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 29 | 52% / +0.16R | 29 | 55% / +0.07R | -0.09 | **FIXED** |
| MOVER_TREND_PULLBACK | 3101 | 56% / -0.00R | 3101 | 60% / +0.05R | +0.05 | **ATR** |
| DIVERGENCE_CONTINUATION | 176 | 55% / +0.06R | 176 | 61% / +0.03R | -0.03 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 68 | 49% / -0.16R | 68 | 53% / -0.13R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 101 | 47% / -0.15R | 101 | 47% / -0.15R | +0.00 | **ATR** |
| RANGE_FADE | 4 | 50% / +0.44R | 4 | 50% / +0.24R | — | **MEASURING** |
| SR_FLIP_RETEST | 11 | 64% / +0.04R | 11 | 64% / +0.07R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 5 | 20% / -0.34R | 5 | 20% / -0.31R | — | **MEASURING** |
| BREAKDOWN_SHORT | 9 | 11% / -0.57R | 9 | 11% / -0.34R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4553 | 33% | -0.06R | 203 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 284 | 51% | -0.04R | 88 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 21 | 67% | +0.09R | 20 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 46 | 33% / +0.05R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 111 | 50% / +0.78R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3705 | 41% / -0.02R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 366 | 37% / -0.08R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 104 | 38% / -0.01R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 188 | 46% / +0.46R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 213 | 38% / -0.18R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 72 | 43% / -0.15R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 44 | 34% / -0.31R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 34 | 29% / -0.40R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 28 | 57% / +0.24R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 22 | 32% / -0.27R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 4 | 50% / +0.21R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 12 | 42% / -0.25R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 7 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 2 | 0% / -2.70R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 52 · alerting: **9** · boot grace active: False
- **ALERT** `close_accounting` — 2 close(s) failed to write a closed-signal record — those trades are missing from the track record until retried; check fail_open for the raising site (streak 130/2) (sustained 130 cycles)
- **ALERT** `scan_cycle` — last 24.49s, worst 154.87s over 2516 cycles; 70 over 60s, 4 over the 120s healthcheck deadline (plus 2/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 130/2) (sustained 130 cycles)
- **ALERT** `dark_resolution` — 10 of 133 open dark rows are not being advanced (worst: SUPERUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 130/120) (sustained 130 cycles)
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 130/6) (sustained 130 cycles)
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=+0.45R (bound 0.3) (streak 130/6) (sustained 130 cycles)
- **ALERT** `mean_revert_emission` — 466 detections since last emission (emitted_total=4) — and the POST-SCORING blocked candidates measure +0.56R over n=310, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 8/6) (sustained 8 cycles)
- **ALERT** `range_fade_emission` — 1802 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 130/6) (sustained 130 cycles)
- **ALERT** `tuned_variants` — 60 non-stamps — atr_arm_uncomputable=60 (seen=1906 stamped=302 skipped=1544) (streak 130/6) (sustained 130 cycles)
- **ALERT** `fail_open:trade_monitor._process_signal` — +126 fail-open(s) this cycle (total 12558); last: AttributeError: 'str' object has no attribute 'timestamp' (sustained 130 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 9246982 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 24 arms current, none stalled; covering 258/258 signals (100%) | 0 |
| auto_dispatch | ok | attempts=6 fanouts=6 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 78810.30 | 0 |
| candle_coverage | ok | 101/113 symbols with ≥20 15m candles, 86/113 updated within 45m [no_bucket=10, short=2, stale=15, fresh=86; 13 promoted of 113]; 27 CORE pair(s) unusable (e.g. ACHUSDT, AUSDT, AZTECUSDT, BARDUSDT, BASUSDT) | 0 |
| candle_series_integrity | ok | merge dropped 422 dup bars, 0 undedupable; ws 0 out-of-order, 68 in-place; SAR refused 0 series | 0 |
| close_accounting | violating | 2 close(s) failed to write a closed-signal record — those trades are missing from the track record until retried; check fail_open for the raising site (streak 130/2) | 130 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 10 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 130/6) | 130 |
| context_emission_policy | ok | output +52 / upstream +25 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1230/1244 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 10 of 133 open dark rows are not being advanced (worst: SUPERUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 130/120) | 130 |
| dark_sar_arms | ok | no open arms; covering 1225/1239 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 3606447 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=+0.45R (bound 0.3) (streak 130/6) | 130 |
| emission_controller | ok | last cycle 0s ago; live_overrides=28 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=15 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4309 stamps (MEAN_REVERT=661, MOVER_AVWAP_SCALP=86, MOVER_TREND_PULLBACK=3464, RANGE_FADE=15, TREND_PULLBACK_EMA=83), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 3023 evaluated, 477 suppressed, 1245 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4845 sealed bars over 41 symbols; 238 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +224 | 0 |
| indicator_cache_key | ok | 28657 frozen value(s) avoided; 71449 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 466 detections since last emission (emitted_total=4) — and the POST-SCORING blocked candidates measure +0.56R over n=310, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 8/6) | 8 |
| mean_revert_path | ok | output +34 / upstream +224 | 0 |
| mover_admission_metadata | ok | 877 symbols known, 175 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 13 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s); 2 orphan(s) dropped at restore | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3055 rows held, 772374 evicted (sampled: execution:trigger_not_confirmed 400/279051, execution:overextended 400/278295, setup_compat:regime_STRONG_TREND 400/99419) | 0 |
| price_action_lane | ok | 233624 evaluated, 364 emitted; layer1 364 stamped / 0 blind; cooldown=31744, delta_opposed=19692, no_footprint=98455, no_levels=182, no_sweep=63912, rr_below_floor=19275 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 1802 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 130/6) | 130 |
| range_fade_path | violating | upstream +224 but output +0 (streak 4/72) | 4 |
| sar_alignment_crosscheck | ok | 224/7002 disagreed (3.2%) | 0 |
| sar_exit_shadow | violating | upstream +224 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 428 held arms settled, 82 unscored, 24 still walking (22 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 11/49 unfetchable (22%); top cause: gap or duplicate bar in the 15m window; symbols: BMTUSDT, BRUSDT, ENAUSDT, HEMIUSDT, PEOPLEUSDT | 0 |
| sar_live_arms | ok | 24 arms current, none stalled; covering 267/267 signals (100%) | 0 |
| sar_refresh_budget | ok | 14 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 449 records await one (38 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | violating | last 24.49s, worst 154.87s over 2516 cycles; 70 over 60s, 4 over the 120s healthcheck deadline (plus 2/0 during boot warm-up, not counted); 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 130/2) | 130 |
| setup_tf_resolver | ok | 108868 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (9.75s to run, worst 92.74s), 377 overrun(s) of 2654 cycles, TTL 900s; slowest tickers=3.23s, engine_state=2.98s, signals=1.99s | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +25 / upstream +224 | 0 |
| structural_snap | ok | 4306/4306 measured, 16 blind, 0 levels moved (refusals: redetect_cooldown=785) | 0 |
| structural_veto_lane | ok | 1077 stamped; 0 with no readable level book, 0 with clear air ahead, 672 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +224 / upstream +25 | 0 |
| tuned_variants | violating | 60 non-stamps — atr_arm_uncomputable=60 (seen=1906 stamped=302 skipped=1544) (streak 130/6) | 130 |

Fail-open exception counters (nonzero sites):
- `main.finalise_restored_terminals`: 2 — last: AttributeError: 'str' object has no attribute 'timestamp'
- `trade_monitor._process_signal`: 12558 — last: AttributeError: 'str' object has no attribute 'timestamp'

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1726619`
- `Path funnel` emissions: `38`
- `Regime distribution` emissions: `38`
- `QUIET_SCALP_BLOCK` events: `84`
- `confidence_gate` events: `5843`
- `free_channel_post` events: `12`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 3282 | 3282 | 15950 | 0 |
| futures_aggtrade | 1 | 2887 | 2887 | 2887 | 0 |
| futures_depth | 1 | 1936 | 1936 | 1936 | 0 |
| futures_liq | 3 | 1942 | 1942 | 3361 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **12**

| Source | Count |
|---|---:|
| signal_close | 9 |
| regime_shift | 3 |

- By severity: HIGH=12

## Dependency readiness
- cvd: presence[present=282140] state[populated=282140] buckets[few=2, many=282107, some=31] sources[none] quality[none]
- funding_rate: presence[absent=54309, present=227831] state[empty=54309, populated=227831] buckets[few=227831, none=54309] sources[none] quality[none]
- liquidation_clusters: presence[absent=173316, present=108824] state[empty=173316, populated=108824] buckets[few=87552, none=173316, some=21272] sources[none] quality[none]
- oi_snapshot: presence[absent=53922, present=228218] state[empty=53922, populated=228218] buckets[few=312, many=226707, none=53922, some=1199] sources[none] quality[none]
- order_book: presence[absent=102050, present=180090] state[populated=180090, unavailable=102050] buckets[few=180090, none=102050] sources[book_ticker=180090, unavailable=102050] quality[none=102050, top_of_book_only=180090]
- orderblocks: presence[absent=282140] state[empty=282140] buckets[none=282140] sources[measured_dark=282102, not_implemented=38] quality[none]
- recent_ticks: presence[present=282140] state[populated=282140] buckets[many=282140] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `21.813966035842896` sec
- Median create→first breach: `6021.713062047958` sec
- Median create→terminal: `6031.611583948135` sec
- Median first breach→terminal: `3.210892915725708` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 3.3175632684664724 | 2.978400000000011 | 1.1138743179111135 | 1 | 0 |
| MOVER_TREND_PULLBACK | 7 | 7 | 3.2507320374314643 | 3.0 | 1.0924850918111195 | 5 | 2 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 1.0855072191543231 | 1.0855072191563044 | 0.9999999999981748 | 0 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3639.3751339912415 | 3641.0990850925446 |
| MOVER_TREND_PULLBACK | 7 | 7 | 0.0 | 28.6 | 0.0 | 0.0 | -0.6904 | 6021.713062047958 | 6031.611583948135 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 25612.325448036194 | 25613.775822162628 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 418 | 1 | 337 | 0.0 | 0.0 | None | None | 81 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1876 | 28 | 1551 | 0.0 | 0.0 | None | None | 325 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-25`
- Gating Δ: `-11702`
- No-generation Δ: `-526276`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -2.3658, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 2.3658, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -3.8412, "current_avg_pnl": -0.6904, "current_win_rate": 0.0, "previous_avg_pnl": 3.1508, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -4, "geometry_changed_delta": 0, "geometry_preserved_delta": 49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -8, "geometry_changed_delta": 0, "geometry_preserved_delta": -117, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
