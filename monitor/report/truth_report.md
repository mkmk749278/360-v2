# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `1236` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 434 | 434 | 434 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 27183 | 27183 | 26278 | 8 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 163742 | 163688 | 76 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 131249 | 131249 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 130870 | 126182 | 5058 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 131272 | 129786 | 1566 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 135413 | 135229 | 217 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 123117 | 123102 | 27 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 131358 | 131387 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 131399 | 126663 | 6670 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 169106 | 175522 | 2661 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 163766 | 149675 | 19389 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 134806 | 134806 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 131255 | 131246 | 20 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 130821 | 130423 | 445 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 133337 | 130887 | 3026 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 130178 | 130428 | 343 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 118312 | 110185 | 8462 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 118658 | 117834 | 912 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 163707 | 163717 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 123131 | 123098 | 61 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 8112 | 8112 | 7748 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1147 | 1147 | 906 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 152 | 152 | 152 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 47099 | 47099 | 46469 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 9 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 21199 | 21199 | 20744 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 8409 | 8409 | 7717 | 43 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 61643 | 61643 | 51726 | 177 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 74 | 74 | 74 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3442 | 3442 | 3402 | 10 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 9533 | 9533 | 8997 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1744 | 1744 | 1567 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 5773 | 5773 | 5556 | 10 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 134 | 134 | 133 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 8701 | 8701 | 6731 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=163688): breakout_not_found=88555, basic_filters_failed=42906, move_not_fresh=22707, breakout_stale=6284, retest_proximity_failed=1981, volume_spike_missing=1254, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=131249): cls_disabled_merged_into_lsr=131249
- **EVAL::DIVERGENCE_CONTINUATION** (total=126182): cvd_divergence_failed=51550, basic_filters_failed=31578, h1_trend_not_aligned=30733, ema_alignment_reject=10766, retest_proximity_failed=1078, missing_fvg_or_orderblock=477
- **EVAL::FAILED_AUCTION_RECLAIM** (total=129786): auction_not_detected=83598, basic_filters_failed=30689, reclaim_hold_failed=7207, tail_too_small=4862, regime_blocked=3342, rsi_reject=88
- **EVAL::FUNDING_EXTREME** (total=135229): funding_not_extreme=96050, basic_filters_failed=33670, ema_alignment_reject=2487, rsi_reject=1228, missing_funding_rate=1099, cvd_divergence_failed=341, momentum_reject=264, missing_fvg_or_orderblock=90
- **EVAL::LIQUIDATION_REVERSAL** (total=123102): cascade_threshold_not_met=88362, basic_filters_failed=33482, cvd_divergence_failed=651, rsi_reject=543, missing_fvg_or_orderblock=54, volume_spike_missing=10
- **EVAL::MA_CROSS_TREND_SHIFT** (total=131387): no_ma_cross=97718, basic_filters_failed=31595, ma_cross_htf_misaligned=1260, ma_cross_cooldown=814
- **EVAL::MEAN_REVERT** (total=126663): no_extension=100879, basic_filters_failed=25784
- **EVAL::MOVER_AVWAP_SCALP** (total=175522): no_avwap_tag=63049, no_mover_leg=50700, basic_filters_failed=43103, avwap_slope_against=11223, avwap_reclaim_no_volume=4332, no_avwap_reclaim=3071, anchor_too_recent=44
- **EVAL::MOVER_TREND_PULLBACK** (total=149675): mover_run_too_small=73697, basic_filters_failed=43017, no_reclaim=27823, no_pullback_tag=4791, no_ma_stack=347
- **EVAL::OPENING_RANGE_BREAKOUT** (total=134806): feature_disabled=134806
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=131246): regime_blocked=95739, breakout_not_found=26817, basic_filters_failed=5643, adx_reject=3004, ema_alignment_reject=43
- **EVAL::QUIET_COMPRESSION_BREAK** (total=130423): compression_not_detected=51304, regime_blocked=38784, basic_filters_failed=25036, breakout_not_detected=12996, volume_confirmation_failed=1145, macd_reject=994, rsi_reject=117, volume_reject=28, missing_fvg_or_orderblock=19
- **EVAL::RANGE_FADE** (total=130887): no_range_edge=105094, basic_filters_failed=25793
- **EVAL::SR_FLIP_RETEST** (total=130428): flip_close_not_confirmed=84628, basic_filters_failed=30664, long_break_volume_thin=4947, regime_blocked=3337, retest_out_of_zone=2861, h1_break_not_confirmed=2611, reclaim_hold_failed=736, long_acceptance_not_held=352, wick_quality_failed=141, ema_alignment_reject=119, missing_fvg_or_orderblock=23, whipsaw_flip=9
- **EVAL::STANDARD** (total=110185): momentum_reject=29955, adx_reject=22972, basic_filters_failed=20642, sweeps_not_detected=13977, macd_reject=12867, ema_alignment_reject=7236, htf_poi_unanchored=2196, invalid_sl_geometry=256, rsi_reject=78, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=117834): h1_trend_not_aligned=34776, ema_alignment_reject=20932, basic_filters_failed=19744, h1_pullback_not_confirmed=14881, no_ema_reclaim_close=8286, ema_not_tested_prev=8188, body_conviction_fail=4176, rsi_reject=3900, prev_already_below_emas=955, prev_already_above_emas=734, no_prev_high_break=414, no_prev_low_break=377, momentum_flat=223, ema21_not_tagged=93, momentum_reject=88, missing_fvg_or_orderblock=67
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=163717): breakout_not_found=94666, basic_filters_failed=42905, move_not_fresh=15499, breakout_stale=7202, retest_proximity_failed=2042, volume_spike_missing=1383, missing_fvg_or_orderblock=14, move_exhausted=6
- **EVAL::WHALE_MOMENTUM** (total=123098): momentum_reject=83085, recent_ticks_insufficient=25729, basic_filters_failed=14284

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=31): execution:overextended=31
- **DIVERGENCE_CONTINUATION** (total=380): setup_compat:regime_VOLATILE_UNSUITABLE=354, execution:overextended=15, setup_compat:regime_BREAKOUT_EXPANSION=11
- **FAILED_AUCTION_RECLAIM** (total=1695): setup_compat:regime_STRONG_TREND=945, execution:overextended=687, setup_compat:regime_VOLATILE_UNSUITABLE=39, context_floor=24
- **FUNDING_EXTREME_SIGNAL** (total=1010): execution:trigger_not_confirmed=984, context_floor=26
- **LIQUIDATION_REVERSAL** (total=152): execution:trigger_not_confirmed=152
- **LIQUIDITY_SWEEP_REVERSAL** (total=9952): execution:trigger_not_confirmed=4434, setup_compat:regime_STRONG_TREND=2791, execution:overextended=2727
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_CLEAN_RANGE=3, execution:overextended=3, execution:trigger_not_confirmed=2, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=10653): setup_compat:regime_STRONG_TREND=4982, setup_compat:regime_WEAK_TREND=3781, execution:overextended=1886, entry_quality=4
- **MOVER_AVWAP_SCALP** (total=5060): execution:overextended=4482, execution:trigger_not_confirmed=448, entry_quality=130
- **MOVER_TREND_PULLBACK** (total=22029): execution:trigger_not_confirmed=11749, execution:overextended=8699, entry_quality=1581
- **QUIET_COMPRESSION_BREAK** (total=101): execution:trigger_not_confirmed=94, execution:overextended=7
- **RANGE_FADE** (total=4420): setup_compat:regime_WEAK_TREND=2173, setup_compat:regime_STRONG_TREND=1272, execution:overextended=495, setup_compat:regime_VOLATILE_UNSUITABLE=362, setup_compat:regime_BREAKOUT_EXPANSION=118
- **TREND_PULLBACK_EMA** (total=5141): setup_compat:regime_CLEAN_RANGE=3381, setup_compat:regime_DIRTY_RANGE=1699, entry_quality=40, setup_compat:regime_VOLATILE_UNSUITABLE=21
- **VOLUME_SURGE_BREAKOUT** (total=38): execution:overextended=38
- **WHALE_MOMENTUM** (total=8522): execution:trigger_not_confirmed=8521, execution:overextended=1

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 354580 | 38.1% |
| QUIET | 253247 | 27.2% |
| TRENDING_DOWN | 157801 | 17.0% |
| TRENDING_UP | 128437 | 13.8% |
| VOLATILE | 36473 | 3.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **194**
- Average confidence gap to threshold: **14.50** (samples=194) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=33, ETHUSDT=29, XRPUSDT=17, DASHUSDT=16, WLDUSDT=15, UNIUSDT=13, ZROUSDT=10, 1000SHIBUSDT=8, BNBUSDT=7, HYPEUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 144 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 135 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 25 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 8 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 137 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 7 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 64 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 11 |
| MEAN_REVERT | kept | min_confidence_pass | 9 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 132 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 263 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1854 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 80 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3170 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 29 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 1 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 10 |
| SR_FLIP_RETEST | filtered | min_confidence | 30 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 78 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 16 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 41 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 33 |
| WHALE_MOMENTUM | filtered | min_confidence | 2 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 144 | 44.04 | 64.86 | 20.82 | 19.63 | 19.99 | 17.51 | 0.59 | 24.40 |
| DIVERGENCE_CONTINUATION | kept | 135 | 67.96 | 65.00 | -2.96 | 21.39 | 19.96 | 18.10 | 2.59 | 3.93 |
| FAILED_AUCTION_RECLAIM | filtered | 33 | 41.71 | 64.03 | 22.32 | 20.82 | 19.73 | 20.00 | 3.59 | 11.29 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 74.50 | 65.00 | -9.50 | 24.00 | 20.00 | 20.00 | 2.50 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 51.30 | 61.00 | 9.70 | 19.64 | 13.60 | 17.00 | 3.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 70.80 | 65.00 | -5.80 | 20.90 | 14.00 | 17.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 144 | 54.04 | 63.50 | 9.46 | 20.31 | 19.39 | 17.95 | 2.58 | 6.56 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 64 | 70.95 | 65.00 | -5.95 | 22.02 | 19.50 | 19.36 | 2.14 | 0.31 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.00 | 65.00 | -10.00 | 20.60 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 11 | 53.23 | 65.00 | 11.77 | 20.00 | 15.27 | 14.71 | 0.00 | 15.89 |
| MEAN_REVERT | kept | 9 | 64.39 | 65.00 | 0.61 | 20.57 | 14.34 | 14.23 | 0.00 | 2.40 |
| MOVER_AVWAP_SCALP | filtered | 133 | 48.35 | 62.44 | 14.09 | 19.75 | 18.17 | 15.80 | 4.27 | 20.79 |
| MOVER_AVWAP_SCALP | kept | 263 | 76.08 | 65.00 | -11.08 | 20.48 | 15.10 | 15.80 | 3.96 | 6.59 |
| MOVER_TREND_PULLBACK | filtered | 1934 | 54.42 | 64.19 | 9.77 | 19.67 | 18.14 | 15.80 | 4.28 | 19.44 |
| MOVER_TREND_PULLBACK | kept | 3170 | 74.70 | 65.00 | -9.70 | 20.37 | 18.87 | 15.80 | 4.01 | 1.51 |
| QUIET_COMPRESSION_BREAK | filtered | 30 | 55.99 | 64.87 | 8.88 | 22.40 | 19.98 | 20.00 | 0.00 | 6.43 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 72.84 | 65.00 | -7.84 | 21.58 | 19.20 | 20.00 | 0.00 | 1.16 |
| SR_FLIP_RETEST | filtered | 33 | 52.56 | 63.55 | 10.99 | 19.56 | 20.00 | 15.20 | 3.86 | 9.33 |
| SR_FLIP_RETEST | kept | 1 | 65.80 | 65.00 | -0.80 | 20.80 | 20.00 | 15.20 | 3.50 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 94 | 56.34 | 62.11 | 5.77 | 20.23 | 19.76 | 17.06 | 5.06 | 16.52 |
| TREND_PULLBACK_EMA | kept | 41 | 74.95 | 65.00 | -9.95 | 21.75 | 19.96 | 18.67 | 5.32 | -0.51 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 73.00 | 65.00 | -8.00 | 18.50 | 14.10 | 20.00 | 4.00 | 3.00 |
| WHALE_MOMENTUM | filtered | 35 | 53.79 | 64.77 | 10.98 | 23.16 | 14.00 | 17.00 | 0.00 | 14.13 |
| WHALE_MOMENTUM | kept | 1 | 66.30 | 65.00 | -1.30 | 20.40 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 144 | 44.04 | 23.11 | 17.44 | 3.44 | 12.36 | 5.09 | 6.90 | 0.59 |
| DIVERGENCE_CONTINUATION | kept | 135 | 67.96 | 22.81 | 16.07 | 4.93 | 12.04 | 5.00 | 8.49 | 2.59 |
| FAILED_AUCTION_RECLAIM | filtered | 33 | 41.71 | 22.58 | 14.00 | 5.27 | 12.91 | 6.58 | 3.11 | 3.59 |
| FAILED_AUCTION_RECLAIM | kept | 1 | 74.50 | 25.00 | 14.00 | 3.00 | 14.00 | 8.00 | 8.00 | 2.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 51.30 | 17.00 | 20.00 | 3.00 | 12.00 | 10.00 | 6.30 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 70.80 | 21.00 | 20.00 | 3.00 | 9.00 | 5.00 | 8.80 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 144 | 54.04 | 23.82 | 15.47 | 6.27 | 11.05 | 5.59 | 6.34 | 2.58 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 64 | 70.95 | 24.22 | 14.19 | 5.16 | 13.17 | 5.38 | 7.24 | 2.14 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.00 | 25.00 | 14.00 | 6.00 | 17.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 11 | 53.23 | 17.00 | 16.55 | 12.00 | 13.00 | 5.00 | 5.57 | 0.00 |
| MEAN_REVERT | kept | 9 | 64.39 | 17.89 | 14.44 | 12.00 | 13.00 | 5.00 | 4.46 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 133 | 48.35 | 20.64 | 18.00 | 10.76 | 12.15 | 5.79 | 5.88 | 4.27 |
| MOVER_AVWAP_SCALP | kept | 263 | 76.08 | 19.90 | 18.00 | 13.89 | 13.97 | 7.18 | 8.17 | 3.96 |
| MOVER_TREND_PULLBACK | filtered | 1934 | 54.42 | 18.31 | 18.04 | 7.75 | 12.82 | 6.26 | 8.35 | 4.28 |
| MOVER_TREND_PULLBACK | kept | 3170 | 74.70 | 19.49 | 18.02 | 7.56 | 11.95 | 6.30 | 9.13 | 4.01 |
| QUIET_COMPRESSION_BREAK | filtered | 30 | 55.99 | 17.00 | 17.87 | 11.30 | 14.00 | 6.55 | 6.20 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 72.84 | 19.40 | 16.80 | 12.30 | 14.00 | 7.05 | 8.04 | 0.00 |
| SR_FLIP_RETEST | filtered | 33 | 52.56 | 25.00 | 17.09 | 8.73 | 11.27 | 5.00 | 4.57 | 3.86 |
| SR_FLIP_RETEST | kept | 1 | 65.80 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 7.30 | 3.50 |
| TREND_PULLBACK_EMA | filtered | 94 | 56.34 | 17.34 | 18.00 | 7.50 | 14.00 | 6.28 | 8.40 | 5.06 |
| TREND_PULLBACK_EMA | kept | 41 | 74.95 | 13.93 | 18.00 | 7.50 | 14.05 | 8.99 | 8.41 | 5.32 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 73.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.00 |
| WHALE_MOMENTUM | filtered | 35 | 53.79 | 21.11 | 8.57 | 10.37 | 12.89 | 7.29 | 7.69 | 0.00 |
| WHALE_MOMENTUM | kept | 1 | 66.30 | 25.00 | 18.00 | 9.00 | 12.00 | 5.00 | 7.30 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 144 | 44.04 | 0.00 | 0.00 | 0.23 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | **0.31** |
| DIVERGENCE_CONTINUATION | kept | 135 | 67.96 | 0.00 | 0.00 | 2.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.10** |
| FAILED_AUCTION_RECLAIM | filtered | 33 | 41.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | **0.36** |
| FAILED_AUCTION_RECLAIM | kept | 1 | 74.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 8 | 51.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 70.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 144 | 54.04 | 0.00 | 0.00 | 0.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.27** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 64 | 70.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 75.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 11 | 53.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.73 | 0.00 | 0.00 | **2.73** |
| MEAN_REVERT | kept | 9 | 64.39 | 0.00 | 0.00 | 0.00 | 0.00 | 1.33 | 0.00 | 0.00 | 0.00 | **1.33** |
| MOVER_AVWAP_SCALP | filtered | 133 | 48.35 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 1.35 | 0.00 | 0.18 | **1.64** |
| MOVER_AVWAP_SCALP | kept | 263 | 76.08 | 1.46 | 0.00 | 0.05 | 0.00 | 2.86 | 1.30 | 0.00 | 0.02 | **5.69** |
| MOVER_TREND_PULLBACK | filtered | 1934 | 54.42 | 0.50 | 0.00 | 0.83 | 0.00 | 0.60 | 0.25 | 0.00 | 0.00 | **2.18** |
| MOVER_TREND_PULLBACK | kept | 3170 | 74.70 | 0.07 | 0.00 | 0.83 | 0.00 | 0.01 | 0.05 | 0.00 | 0.00 | **0.96** |
| QUIET_COMPRESSION_BREAK | filtered | 30 | 55.99 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | **1.00** |
| QUIET_COMPRESSION_BREAK | kept | 10 | 72.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.43 | 0.00 | 0.00 | 0.00 | **0.43** |
| SR_FLIP_RETEST | filtered | 33 | 52.56 | 0.00 | 0.00 | 4.36 | 0.00 | 1.96 | 0.00 | 0.00 | 0.00 | **6.32** |
| SR_FLIP_RETEST | kept | 1 | 65.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 94 | 56.34 | 0.00 | 0.00 | 2.04 | 0.00 | 0.00 | 0.38 | 0.00 | 0.00 | **2.42** |
| TREND_PULLBACK_EMA | kept | 41 | 74.95 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.68 | 0.00 | 0.00 | **0.88** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 73.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 35 | 53.79 | 0.00 | 0.00 | 0.00 | 0.00 | 3.70 | 0.00 | 0.00 | 0.00 | **3.70** |
| WHALE_MOMENTUM | kept | 1 | 66.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **129443 held of 425525 seen** across 21 strategies; 2962 cells past the sample floor; **1433 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 41665 | 613/41052/0 | 43% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.17R) |
| MOVER_AVWAP_SCALP | 16771 | 180/16591/0 | 41% | -0.25 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 10184 | 118/10066/0 | 40% | -0.24 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 8635 | 53/8582/0 | 50% | -0.04 | NY/QUIET/COMPRESSED/BTC_FALLING/MIDCAP (+1.39R) | OVERLAP/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 7438 | 30/7408/0 | 43% | -0.17 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_MEAN_REVERT | 6590 | 0/0/6590 | 43% | -0.09 | OFF_HOURS/MARKDOWN/NORMAL/BTC_FALLING (+0.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.85R) |
| SHADOW_RANGE_FADE | 5808 | 0/0/5808 | 37% | -0.06 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.57R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.33R) |
| LIQUIDITY_SWEEP_REVERSAL | 5431 | 70/5361/0 | 36% | -0.50 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-1.57R) |
| QUIET_COMPRESSION_BREAK | 5424 | 347/5077/0 | 48% | -0.11 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.59R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5131 | 0/0/5131 | 34% | -0.40 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.00R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3421 | 2/3419/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2936 | 35/2901/0 | 43% | -0.21 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 2386 | 2/2384/0 | 31% | -0.47 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 2385 | 0/2385/0 | 39% | -0.10 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 2072 | 11/2061/0 | 48% | -0.20 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.86R) | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.27R) |
| RANGE_FADE | 1142 | 4/1138/0 | 42% | -0.34 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1089 | 0/0/1089 | 54% | -0.03 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.12R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.36R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 276 | 0/276/0 | 31% | -0.57 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 84 | 12/72/0 | 48% | -0.06 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MAJOR` -1.55R (n=16, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR` -1.53R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 172 | 27% / -0.58R | 172 | 49% / -0.18R | +0.41 | **ATR** |
| LIQUIDATION_REVERSAL | 15 | 33% / -0.42R | 15 | 60% / -0.16R | +0.25 | **ATR** |
| TREND_PULLBACK_EMA | 610 | 43% / -0.23R | 610 | 56% / -0.03R | +0.20 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1008 | 45% / -0.31R | 1008 | 55% / -0.14R | +0.16 | **ATR** |
| MOVER_AVWAP_SCALP | 1395 | 43% / -0.20R | 1395 | 49% / -0.07R | +0.13 | **ATR** |
| WHALE_MOMENTUM | 379 | 44% / -0.32R | 379 | 46% / -0.22R | +0.10 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 122 | 37% / -0.16R | 122 | 47% / -0.06R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 6519 | 49% / -0.12R | 6519 | 54% / -0.02R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 990 | 41% / -0.23R | 990 | 43% / -0.14R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 200 | 48% / -0.24R | 200 | 50% / -0.16R | +0.08 | **ATR** |
| DIVERGENCE_CONTINUATION | 884 | 48% / -0.11R | 884 | 54% / -0.05R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 26 | 46% / -0.13R | 26 | 46% / -0.07R | +0.05 | **ATR** |
| RANGE_FADE | 50 | 36% / -0.33R | 50 | 38% / -0.34R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 883 | 46% / -0.14R | 883 | 46% / -0.14R | -0.01 | **FIXED** |
| MEAN_REVERT | 221 | 52% / -0.09R | 221 | 50% / -0.09R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 9346 | 29% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1395 | 47% | -0.08R | 207 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 76 | 50% | -0.06R | 50 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 816 | 37% / -0.14R | +0.92 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 994 | 39% / -0.27R | +0.74 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 1813 | 34% / -0.11R | +0.73 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 8343 | 36% / -0.16R | +0.37 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 981 | 39% / -0.04R | +0.24 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 145 | 36% / -0.31R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 861 | 35% / -0.17R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 805 | 34% / -0.19R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 180 | 30% / -0.39R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 228 | 28% / -0.67R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 184 | 54% / +0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 38 | 32% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 201 | 32% / -0.41R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 40 | 28% / -0.45R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 21 | 48% / +0.11R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 11 | 45% / +0.67R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×180]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 35/6) (sustained 35 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 292/6) (sustained 292 cycles)
- **ALERT** `tuned_variants` — 91 non-stamps — atr_arm_uncomputable=91 (seen=4987 stamped=382 skipped=4514) (streak 287/6) (sustained 287 cycles)
- **ALERT** `auto_dispatch` — 45 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=45) (streak 281/3) (sustained 281 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 48 fed / 0 quiet / 2 never delivered of 50 subscribed; 46752988 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 13 arms current, none stalled; covering 1243/1243 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +2 / upstream +2 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 27 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| auto_dispatch | violating | 45 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=45) (streak 281/3) | 281 |
| binance_ip_weight | ok | peak 123/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 84255.50 | 0 |
| candle_coverage | ok | 78/78 symbols with ≥20 15m candles, 78/78 updated within 45m [fresh=78; 72 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 97 dup bars, 0 undedupable; ws 0 out-of-order, 518 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 46 cohorts, 12 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +50 / upstream +42 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1299/1317 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 21 of 190 open dark rows are not being advanced (worst: CCUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 36/120) | 36 |
| dark_sar_arms | ok | no open arms; covering 1294/1312 signals (99%) | 0 |
| depth_feed | ok | 48/50 books fresh (stale 0, never 2, thin 0); 20379315 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 292/6) | 292 |
| emission_controller | ok | last cycle 1027s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×180]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 35/6) | 35 |
| entry_quality_effective | ok | 6333 evaluated, 2205 suppressed, 3682 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,378 reads/day of 50,000 [engine 1,335, signing 43]; top site keystore.roster_doc at 288/day (engine) | 0 |
| footprint_bars | ok | 5760 sealed bars over 48 symbols; 1235 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +320 | 0 |
| indicator_cache_key | ok | 87549 frozen value(s) avoided; 454284 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.22R over n=2901 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | violating | upstream +320 but output +0 (streak 3/72) | 3 |
| mover_admission_metadata | ok | 924 symbols known, 217 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 6 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3194 rows held, 2401715 evicted (sampled: execution:trigger_not_confirmed 400/874603, execution:overextended 400/782196, setup_compat:regime_STRONG_TREND 400/368754) | 0 |
| price_action_lane | ok | 1106316 evaluated, 606 emitted; layer1 606 stamped / 0 blind; cooldown=124765, delta_opposed=82510, no_footprint=410763, no_opposing_target=962, no_sweep=412192, rr_below_floor=74518 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.34R over n=1138 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +17 / upstream +320 | 0 |
| sar_alignment_crosscheck | ok | 105/7620 disagreed (1.4%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +320 | 0 |
| sar_hold_arm | ok | 1860 held arms settled, 141 unscored, 26 still walking (23 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 1/64 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: LITUSDT | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 26 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| sar_refresh_budget | ok | 8 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 61 still mid-window | 0 |
| scan_cycle | ok | last 25.53s, worst 115.36s over 12971 lifetime cycles; lifetime 5 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 2.94s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 475737 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 13s ago (37.92s to run, worst 79.83s), 230 overrun(s) of 6274 cycles, TTL 900s; slowest exchange_positions=10.05s, router_delivery=6.18s, user_positions=4.69s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=1, gate reads=0, withheld=1) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +51 / upstream +320 | 0 |
| structural_snap | ok | 5961/5961 measured, 28 blind, 0 levels moved (refusals: redetect_cooldown=403) | 0 |
| structural_veto_lane | ok | 734 stamped; 0 with no readable level book, 16 with clear air ahead, 521 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +320 / upstream +42 | 0 |
| tuned_variants | violating | 91 non-stamps — atr_arm_uncomputable=91 (seen=4987 stamped=382 skipped=4514) (streak 287/6) | 287 |
| unlock_shorts | ok | 12 open, 43 scheduled, calendar 7.3h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 2 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4122586`
- `Path funnel` emissions: `109`
- `Regime distribution` emissions: `109`
- `QUIET_SCALP_BLOCK` events: `194`
- `confidence_gate` events: `6298`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **12**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 1881 | 1881 | 1881 | 0 |
| futures_aggtrade | 8 | 2130 | 6451 | 7798 | 0 |
| futures_depth | 1 | 2566 | 2566 | 2566 | 0 |
| futures_liq | 2 | 2023 | 2023 | 2926 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=779548] state[populated=779548] buckets[many=779548] sources[none] quality[none]
- funding_rate: presence[absent=116181, present=663367] state[empty=116181, populated=663367] buckets[few=663367, none=116181] sources[none] quality[none]
- liquidation_clusters: presence[absent=459791, present=319757] state[empty=459791, populated=319757] buckets[few=264104, none=459791, some=55653] sources[none] quality[none]
- oi_snapshot: presence[absent=107724, present=671824] state[empty=107724, populated=671824] buckets[few=737, many=667635, none=107724, some=3452] sources[none] quality[none]
- order_book: presence[absent=208763, present=570785] state[populated=570785, unavailable=208763] buckets[few=570785, none=208763] sources[book_ticker=570785, unavailable=208763] quality[none=208763, top_of_book_only=570785]
- orderblocks: presence[absent=779548] state[empty=779548] buckets[none=779548] sources[measured_dark=779548] quality[none]
- recent_ticks: presence[present=779548] state[populated=779548] buckets[many=779548] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.281632900238037` sec
- Median create→first breach: `4766.2204258441925` sec
- Median create→terminal: `4766.8841960430145` sec
- Median first breach→terminal: `8.392333984375e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.4}, "under_180s": {"count": 1, "pct": 2.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.4}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.4}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.6991800910752024 | 0.7999999999999995 | 0.8739751138440036 | 0 | 1 |
| MOVER_AVWAP_SCALP | 4 | 4 | 2.4066073715073886 | 2.918222231768646 | 0.8247416953538476 | 1 | 3 |
| MOVER_TREND_PULLBACK | 22 | 22 | 4.150815391293408 | 3.0 | 1.4829947286301752 | 18 | 4 |
| QUIET_COMPRESSION_BREAK | 13 | 13 | 1.2076048715054404 | 1.3061726483599065 | 0.8973598468751681 | 0 | 10 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.775267883000308 | 3.0 | 0.925089294333436 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.6992 | 17015.6888589859 | 17015.68892598152 |
| MOVER_AVWAP_SCALP | 4 | 4 | 50.0 | 50.0 | 50.0 | 0.0 | 1.1289 | 7888.272914528847 | 7889.476610422134 |
| MOVER_TREND_PULLBACK | 22 | 22 | 36.4 | 40.9 | 36.4 | 0.0 | 0.3558 | 2421.266609787941 | 2421.2666543722153 |
| QUIET_COMPRESSION_BREAK | 13 | 13 | 46.2 | 38.5 | 46.2 | 0.0 | 0.8752 | 25392.24870109558 | 25392.24880194664 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.7753 | 827.7136569023132 | 827.7136769294739 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1744 | 1 | 1567 | 0.0 | 0.0 | None | None | 177 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 5773 | 10 | 5556 | 0.0 | 100.0 | 827.7136569023132 | 827.7136769294739 | 217 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `240`
- Gating Δ: `156866`
- No-generation Δ: `2044020`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.1289, "current_avg_pnl": 1.1289, "current_win_rate": 50.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.3111, "current_avg_pnl": 0.3558, "current_win_rate": 36.4, "previous_avg_pnl": -0.9553, "previous_win_rate": 25.0, "win_rate_delta": 11.4}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 2.2642, "current_avg_pnl": 0.8752, "current_win_rate": 46.2, "previous_avg_pnl": -1.389, "previous_win_rate": 0.0, "win_rate_delta": 46.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 22, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 10, "geometry_changed_delta": 0, "geometry_preserved_delta": 217, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 827.71, "median_terminal_delta_sec": 827.71, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
