# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `4678` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 286 | 286 | 266 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10221 | 10221 | 9637 | 8 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 122373 | 122349 | 50 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 105186 | 105186 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 104840 | 102870 | 2291 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 105227 | 104317 | 980 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 105853 | 105692 | 195 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 93929 | 93933 | 14 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 105303 | 105368 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 105385 | 102634 | 3725 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 127416 | 134058 | 1383 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 122401 | 112098 | 15232 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 105248 | 105248 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 105193 | 105207 | 19 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 104786 | 104484 | 349 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 106370 | 105353 | 1471 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 104148 | 104518 | 214 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 92643 | 87940 | 5118 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 93064 | 92745 | 397 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 122323 | 122341 | 29 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 93951 | 93972 | 6 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4327 | 4327 | 3842 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 861 | 861 | 414 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 125 | 125 | 35 | 1 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 28174 | 28174 | 27827 | 14 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 5 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 10569 | 10569 | 8940 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3688 | 3688 | 2798 | 70 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 45670 | 45670 | 34277 | 244 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 54 | 54 | 54 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2038 | 2038 | 1799 | 30 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4553 | 4553 | 4487 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1080 | 1080 | 876 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1960 | 1960 | 1813 | 16 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 122 | 122 | 86 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 198 | 198 | 108 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=122349): breakout_not_found=63981, basic_filters_failed=42262, move_not_fresh=9509, breakout_stale=4164, retest_proximity_failed=1891, volume_spike_missing=495, move_exhausted=38, missing_fvg_or_orderblock=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=105186): cls_disabled_merged_into_lsr=105186
- **EVAL::DIVERGENCE_CONTINUATION** (total=102870): h1_trend_not_aligned=34315, basic_filters_failed=32758, cvd_divergence_failed=31540, ema_alignment_reject=3445, retest_proximity_failed=620, missing_fvg_or_orderblock=192
- **EVAL::FAILED_AUCTION_RECLAIM** (total=104317): auction_not_detected=60643, basic_filters_failed=31481, regime_blocked=4895, reclaim_hold_failed=4193, tail_too_small=3049, rsi_reject=56
- **EVAL::FUNDING_EXTREME** (total=105692): funding_not_extreme=68063, basic_filters_failed=32452, ema_alignment_reject=2202, missing_funding_rate=1427, rsi_reject=1102, momentum_reject=238, cvd_divergence_failed=189, missing_fvg_or_orderblock=19
- **EVAL::LIQUIDATION_REVERSAL** (total=93933): cascade_threshold_not_met=60105, basic_filters_failed=32834, cvd_divergence_failed=473, rsi_reject=452, missing_fvg_or_orderblock=57, volume_spike_missing=12
- **EVAL::MA_CROSS_TREND_SHIFT** (total=105368): no_ma_cross=71096, basic_filters_failed=32793, ma_cross_htf_misaligned=871, ma_cross_cooldown=608
- **EVAL::MEAN_REVERT** (total=102634): no_extension=81763, basic_filters_failed=20871
- **EVAL::MOVER_AVWAP_SCALP** (total=134058): no_avwap_tag=43425, basic_filters_failed=42543, no_mover_leg=29090, avwap_slope_against=12447, avwap_reclaim_no_volume=3978, no_avwap_reclaim=2440, anchor_too_recent=135
- **EVAL::MOVER_TREND_PULLBACK** (total=112098): mover_run_too_small=46797, basic_filters_failed=42406, no_reclaim=19350, no_pullback_tag=3545
- **EVAL::OPENING_RANGE_BREAKOUT** (total=105248): feature_disabled=105248
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=105207): regime_blocked=70967, breakout_not_found=21452, basic_filters_failed=9276, adx_reject=3454, ema_alignment_reject=58
- **EVAL::QUIET_COMPRESSION_BREAK** (total=104484): regime_blocked=39030, compression_not_detected=32867, basic_filters_failed=22195, breakout_not_detected=9433, volume_confirmation_failed=859, rsi_reject=88, missing_fvg_or_orderblock=12
- **EVAL::RANGE_FADE** (total=105353): no_range_edge=84478, basic_filters_failed=20875
- **EVAL::SR_FLIP_RETEST** (total=104518): flip_close_not_confirmed=60017, basic_filters_failed=31450, regime_blocked=4880, retest_out_of_zone=3030, long_break_volume_thin=2012, h1_break_not_confirmed=1415, reclaim_hold_failed=1070, long_acceptance_not_held=223, whipsaw_flip=216, ema_alignment_reject=112, wick_quality_failed=79, missing_fvg_or_orderblock=14
- **EVAL::STANDARD** (total=87940): momentum_reject=23283, adx_reject=22063, basic_filters_failed=15301, sweeps_not_detected=11678, macd_reject=7426, ema_alignment_reject=5710, htf_poi_unanchored=2158, invalid_sl_geometry=193, rsi_reject=128
- **EVAL::TREND_PULLBACK** (total=92745): h1_trend_not_aligned=39491, basic_filters_failed=19076, ema_alignment_reject=10444, h1_pullback_not_confirmed=9418, ema_not_tested_prev=4934, no_ema_reclaim_close=4217, body_conviction_fail=2056, rsi_reject=1671, prev_already_above_emas=573, no_prev_high_break=334, prev_already_below_emas=293, momentum_flat=101, no_prev_low_break=80, missing_fvg_or_orderblock=26, momentum_reject=21, ema21_not_tagged=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=122341): breakout_not_found=61535, basic_filters_failed=42258, move_not_fresh=11255, breakout_stale=5154, retest_proximity_failed=1754, volume_spike_missing=349, move_exhausted=25, missing_fvg_or_orderblock=11
- **EVAL::WHALE_MOMENTUM** (total=93972): momentum_reject=67040, recent_ticks_insufficient=16370, basic_filters_failed=10562

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=4): execution:overextended=4
- **DIVERGENCE_CONTINUATION** (total=230): setup_compat:regime_VOLATILE_UNSUITABLE=187, setup_compat:regime_BREAKOUT_EXPANSION=23, execution:overextended=20
- **FAILED_AUCTION_RECLAIM** (total=2620): setup_compat:regime_STRONG_TREND=1278, execution:overextended=1158, context_floor=178, setup_compat:regime_VOLATILE_UNSUITABLE=6
- **FUNDING_EXTREME_SIGNAL** (total=728): execution:trigger_not_confirmed=718, context_floor=10
- **LIQUIDATION_REVERSAL** (total=125): execution:trigger_not_confirmed=125
- **LIQUIDITY_SWEEP_REVERSAL** (total=6866): setup_compat:regime_STRONG_TREND=2685, execution:trigger_not_confirmed=2573, execution:overextended=1608
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_DIRTY_RANGE=4, execution:overextended=2
- **MEAN_REVERT** (total=5149): setup_compat:regime_STRONG_TREND=2641, setup_compat:regime_WEAK_TREND=1901, execution:overextended=607
- **MOVER_AVWAP_SCALP** (total=2757): execution:overextended=2442, execution:trigger_not_confirmed=261, entry_quality=54
- **MOVER_TREND_PULLBACK** (total=19086): execution:trigger_not_confirmed=10224, execution:overextended=7626, entry_quality=1236
- **QUIET_COMPRESSION_BREAK** (total=186): execution:overextended=166, execution:trigger_not_confirmed=20
- **RANGE_FADE** (total=2462): setup_compat:regime_STRONG_TREND=1573, setup_compat:regime_WEAK_TREND=687, setup_compat:regime_VOLATILE_UNSUITABLE=120, execution:overextended=73, context_edge=9
- **TREND_PULLBACK_EMA** (total=1781): setup_compat:regime_CLEAN_RANGE=1081, setup_compat:regime_DIRTY_RANGE=553, setup_compat:regime_VOLATILE_UNSUITABLE=135, entry_quality=12
- **VOLUME_SURGE_BREAKOUT** (total=32): context_floor=17, execution:overextended=15
- **WHALE_MOMENTUM** (total=119): execution:trigger_not_confirmed=119

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 264183 | 40.6% |
| QUIET | 143175 | 22.0% |
| TRENDING_DOWN | 105247 | 16.2% |
| TRENDING_UP | 104212 | 16.0% |
| VOLATILE | 33951 | 5.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **115**
- Average confidence gap to threshold: **10.38** (samples=115) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=28, APRUSDT=12, ASTERUSDT=9, TRXUSDT=9, DOGEUSDT=9, AVAXUSDT=8, FILUSDT=8, XRPUSDT=6, SOLUSDT=6, PENGUUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 20 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 152 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 22 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 3 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 2 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 26 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 52 |
| LIQUIDATION_REVERSAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 82 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 40 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 469 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1537 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 16 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3143 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 79 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 57 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 74 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 9 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 4 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 28 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 93 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 20 | 79.65 | 65.00 | -14.65 | 20.61 | 18.19 | 20.00 | 4.55 | 0.90 |
| DIVERGENCE_CONTINUATION | filtered | 154 | 50.78 | 64.37 | 13.59 | 21.25 | 19.18 | 17.69 | 1.17 | 18.19 |
| DIVERGENCE_CONTINUATION | kept | 22 | 68.61 | 65.00 | -3.61 | 21.76 | 19.24 | 17.40 | 2.73 | 3.57 |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 54.60 | 63.20 | 8.60 | 20.50 | 19.46 | 20.00 | 3.00 | 2.40 |
| FAILED_AUCTION_RECLAIM | kept | 26 | 70.88 | 65.00 | -5.88 | 20.29 | 16.14 | 20.00 | 3.58 | 0.73 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 59.40 | 61.00 | 1.60 | 17.20 | 14.00 | 17.00 | 5.00 | 10.60 |
| LIQUIDATION_REVERSAL | filtered | 52 | 54.37 | 10.00 | -44.37 | 20.18 | 8.28 | 18.09 | 6.00 | 4.78 |
| LIQUIDATION_REVERSAL | kept | 1 | 61.70 | 65.00 | 3.30 | 23.90 | 10.50 | 14.40 | 6.50 | 17.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 46.70 | 65.00 | 18.30 | 20.10 | 20.00 | 15.90 | 3.00 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 82 | 69.41 | 65.00 | -4.41 | 20.85 | 19.55 | 17.75 | 1.85 | 0.15 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.50 | 65.00 | -3.50 | 16.90 | 18.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 1 | 68.70 | 65.00 | -3.70 | 21.20 | 14.00 | 20.00 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 43 | 60.01 | 61.16 | 1.15 | 20.16 | 14.04 | 15.80 | 4.21 | 9.54 |
| MOVER_AVWAP_SCALP | kept | 469 | 81.61 | 65.00 | -16.61 | 19.88 | 14.77 | 15.80 | 4.34 | 3.44 |
| MOVER_TREND_PULLBACK | filtered | 1553 | 56.97 | 63.76 | 6.79 | 21.30 | 18.45 | 15.80 | 4.08 | 16.59 |
| MOVER_TREND_PULLBACK | kept | 3143 | 77.00 | 65.00 | -12.00 | 20.55 | 18.59 | 15.80 | 4.30 | 2.05 |
| QUIET_COMPRESSION_BREAK | filtered | 136 | 55.40 | 64.59 | 9.19 | 20.41 | 19.41 | 20.00 | 0.00 | 3.97 |
| QUIET_COMPRESSION_BREAK | kept | 74 | 72.39 | 65.00 | -7.39 | 20.87 | 18.21 | 20.00 | 0.00 | 0.60 |
| SR_FLIP_RETEST | filtered | 9 | 54.44 | 65.00 | 10.56 | 20.66 | 20.00 | 16.53 | 1.78 | 12.42 |
| SR_FLIP_RETEST | kept | 4 | 70.70 | 65.00 | -5.70 | 20.88 | 20.00 | 17.30 | 2.50 | 2.38 |
| TREND_PULLBACK_EMA | filtered | 28 | 60.70 | 65.00 | 4.30 | 22.17 | 19.84 | 18.93 | 4.93 | 10.44 |
| TREND_PULLBACK_EMA | kept | 93 | 80.12 | 65.00 | -15.12 | 20.45 | 19.87 | 16.94 | 5.37 | 0.83 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 78.50 | 65.00 | -13.50 | 19.90 | 16.67 | 20.00 | 5.17 | 2.67 |
| WHALE_MOMENTUM | filtered | 3 | 38.80 | 65.00 | 26.20 | 24.30 | 14.00 | 17.00 | 0.00 | 27.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 20 | 79.65 | 17.40 | 17.80 | 12.90 | 14.70 | 5.15 | 8.05 | 4.55 |
| DIVERGENCE_CONTINUATION | filtered | 154 | 50.78 | 21.83 | 15.49 | 4.23 | 12.50 | 5.55 | 8.20 | 1.17 |
| DIVERGENCE_CONTINUATION | kept | 22 | 68.61 | 23.55 | 11.82 | 7.36 | 13.77 | 5.00 | 8.50 | 2.73 |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 54.60 | 23.40 | 14.80 | 4.80 | 14.00 | 8.10 | 3.90 | 3.00 |
| FAILED_AUCTION_RECLAIM | kept | 26 | 70.88 | 22.46 | 17.54 | 5.31 | 12.88 | 5.25 | 4.59 | 3.58 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 59.40 | 25.00 | 8.00 | 12.00 | 9.00 | 5.00 | 6.00 | 5.00 |
| LIQUIDATION_REVERSAL | filtered | 52 | 54.37 | 24.08 | 8.00 | 12.98 | 8.00 | 4.53 | 6.23 | 6.00 |
| LIQUIDATION_REVERSAL | kept | 1 | 61.70 | 25.00 | 8.00 | 15.00 | 8.00 | 8.00 | 8.70 | 6.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 46.70 | 25.00 | 14.00 | 6.00 | 12.00 | 5.00 | 3.30 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 82 | 69.41 | 24.76 | 14.05 | 5.30 | 13.39 | 4.68 | 5.53 | 1.85 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.50 | 15.00 | 14.00 | 9.00 | 14.00 | 8.50 | 8.00 | 0.00 |
| MEAN_REVERT | kept | 1 | 68.70 | 25.00 | 18.00 | 15.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 43 | 60.01 | 17.42 | 18.00 | 12.21 | 13.81 | 7.59 | 7.82 | 4.21 |
| MOVER_AVWAP_SCALP | kept | 469 | 81.61 | 20.10 | 18.06 | 13.07 | 14.15 | 7.43 | 8.35 | 4.34 |
| MOVER_TREND_PULLBACK | filtered | 1553 | 56.97 | 17.90 | 18.01 | 7.50 | 12.63 | 6.04 | 9.03 | 4.08 |
| MOVER_TREND_PULLBACK | kept | 3143 | 77.00 | 19.61 | 18.05 | 8.09 | 13.39 | 6.80 | 8.85 | 4.30 |
| QUIET_COMPRESSION_BREAK | filtered | 136 | 55.40 | 18.12 | 16.32 | 11.18 | 14.13 | 6.21 | 5.86 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 74 | 72.39 | 17.11 | 15.68 | 13.14 | 14.16 | 6.06 | 7.46 | 0.00 |
| SR_FLIP_RETEST | filtered | 9 | 54.44 | 20.56 | 8.00 | 4.67 | 15.67 | 8.28 | 7.92 | 1.78 |
| SR_FLIP_RETEST | kept | 4 | 70.70 | 25.00 | 15.50 | 3.75 | 14.00 | 5.00 | 7.33 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 28 | 60.70 | 10.57 | 18.00 | 7.50 | 14.00 | 7.00 | 9.14 | 4.93 |
| TREND_PULLBACK_EMA | kept | 93 | 80.12 | 20.44 | 18.00 | 7.50 | 14.74 | 6.81 | 9.02 | 5.37 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 78.50 | 22.33 | 15.33 | 13.00 | 13.00 | 5.00 | 8.33 | 5.17 |
| WHALE_MOMENTUM | filtered | 3 | 38.80 | 25.00 | 8.00 | 3.00 | 12.00 | 10.00 | 8.30 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 20 | 79.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 154 | 50.78 | 0.00 | 0.00 | 2.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.26** |
| DIVERGENCE_CONTINUATION | kept | 22 | 68.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 5 | 54.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 26 | 70.88 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.31** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 59.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 52 | 54.37 | 0.00 | 0.00 | 0.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.92** |
| LIQUIDATION_REVERSAL | kept | 1 | 61.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 46.70 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 82 | 69.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **0.15** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 1 | 68.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 43 | 60.01 | 0.00 | 0.00 | 0.00 | 0.00 | 1.53 | 0.00 | 0.00 | 1.31 | **2.84** |
| MOVER_AVWAP_SCALP | kept | 469 | 81.61 | 0.00 | 0.00 | 0.47 | 0.00 | 1.76 | 0.32 | 0.00 | 0.01 | **2.56** |
| MOVER_TREND_PULLBACK | filtered | 1553 | 56.97 | 0.00 | 0.00 | 0.67 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **0.86** |
| MOVER_TREND_PULLBACK | kept | 3143 | 77.00 | 0.00 | 0.00 | 0.32 | 0.00 | 0.35 | 0.03 | 0.00 | 0.00 | **0.70** |
| QUIET_COMPRESSION_BREAK | filtered | 136 | 55.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.13 | 0.00 | 1.59 | **1.72** |
| QUIET_COMPRESSION_BREAK | kept | 74 | 72.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.41 | 0.41 | 0.00 | 0.08 | **0.90** |
| SR_FLIP_RETEST | filtered | 9 | 54.44 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| SR_FLIP_RETEST | kept | 4 | 70.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 28 | 60.70 | 0.00 | 0.00 | 3.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.71** |
| TREND_PULLBACK_EMA | kept | 93 | 80.12 | 0.00 | 0.00 | 0.34 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.34** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 78.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 3 | 38.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **75208 held of 172647 seen** across 21 strategies; 1682 cells past the sample floor; **711 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 30603 | 281/30322/0 | 45% | -0.13 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.20R) |
| MOVER_AVWAP_SCALP | 9306 | 55/9251/0 | 41% | -0.26 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5939 | 31/5908/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 4157 | 24/4133/0 | 53% | +0.06 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 3859 | 0/0/3859 | 43% | -0.08 | ASIA/RANGE/NORMAL/BTC_RISING (+0.28R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.05R) |
| QUIET_COMPRESSION_BREAK | 3611 | 91/3520/0 | 47% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.84R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| TREND_PULLBACK_EMA | 3599 | 6/3593/0 | 46% | -0.19 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| SHADOW_RANGE_FADE | 3242 | 0/0/3242 | 37% | -0.08 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.24R) | LONDON/RANGE/NORMAL/BTC_FALLING (-0.92R) |
| SHADOW_FUNDING_FADE | 2722 | 0/0/2722 | 36% | -0.38 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-0.99R) |
| WHALE_MOMENTUM | 2064 | 2/2062/0 | 40% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1724 | 12/1712/0 | 36% | -0.32 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.62R) |
| MEAN_REVERT | 1046 | 14/1032/0 | 63% | +0.21 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 914 | 2/912/0 | 30% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 884 | 0/884/0 | 49% | -0.08 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 448 | 0/448/0 | 60% | -0.12 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-0.91R) |
| SHADOW_CASCADE_REVERSAL | 418 | 0/0/418 | 54% | -0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.23R) |
| RANGE_FADE | 256 | 0/256/0 | 52% | -0.11 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (+1.36R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 192 | 16/176/0 | 22% | -0.56 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 174 | 0/174/0 | 1% | -1.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 46 | 6/40/0 | 35% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +1.76R (n=34, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL` +1.62R (n=37, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.62R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.50R (n=20, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 95 | 34% / -0.43R | 95 | 51% / -0.12R | +0.31 | **ATR** |
| TREND_PULLBACK_EMA | 310 | 50% / -0.13R | 310 | 57% / -0.02R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 247 | 43% / -0.34R | 247 | 45% / -0.24R | +0.10 | **ATR** |
| RANGE_FADE | 19 | 47% / +0.11R | 19 | 47% / +0.01R | -0.10 | **FIXED** |
| MOVER_AVWAP_SCALP | 706 | 46% / -0.18R | 706 | 51% / -0.08R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 467 | 44% / -0.17R | 467 | 46% / -0.09R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 4648 | 51% / -0.09R | 4648 | 55% / -0.01R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 75 | 48% / -0.28R | 75 | 49% / -0.21R | +0.07 | **ATR** |
| MA_CROSS_TREND_SHIFT | 15 | 33% / -0.24R | 15 | 33% / -0.19R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 60 | 47% / -0.07R | 60 | 53% / -0.02R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 345 | 50% / -0.20R | 345 | 54% / -0.16R | +0.03 | **ATR** |
| BREAKDOWN_SHORT | 20 | 30% / -0.17R | 20 | 30% / -0.14R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 594 | 45% / -0.16R | 594 | 45% / -0.17R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 438 | 54% / -0.01R | 438 | 59% / -0.01R | -0.00 | **FIXED** |
| MEAN_REVERT | 97 | 57% / +0.04R | 97 | 55% / +0.04R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 9 | 11% / -0.99R | 9 | 33% / -0.54R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6961 | 31% | -0.12R | 283 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 706 | 49% | -0.08R | 162 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 41 | 56% | -0.04R | 34 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 86 | 36% / -0.24R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 554 | 37% / -0.07R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5926 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 839 | 36% / -0.03R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 360 | 37% / -0.05R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 484 | 42% / +0.10R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 405 | 38% / -0.10R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 336 | 44% / -0.15R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 84 | 29% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 110 | 31% / -0.59R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 77 | 53% / +0.08R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 38 | 42% / +0.01R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 17 | 41% / +0.18R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 76 | 32% / -0.35R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 13 | 23% / -0.46R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **8** · boot grace active: False
- **ALERT** `sar_alignment_crosscheck` — 506/7586 disagreed (6.7%) (streak 74/6) (sustained 74 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×340]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 47/6) (sustained 47 cycles)
- **ALERT** `entry_quality_effective` — entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) (sustained 13 cycles)
- **ALERT** `dark_resolution` — 9 of 101 open dark rows are not being advanced (worst: CAPUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 190/120) (sustained 190 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.46R (bound 0.3) (streak 190/6) (sustained 190 cycles)
- **ALERT** `mean_revert_emission` — 6451 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.21R over n=1032, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 171/6) (sustained 171 cycles)
- **ALERT** `tuned_variants` — 41 non-stamps — atr_arm_uncomputable=41 (seen=2313 stamped=255 skipped=2017) (streak 43/6) (sustained 43 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 190/3) (sustained 190 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 41 fed / 0 quiet / 0 never delivered of 41 subscribed; 29650569 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 190/3) | 190 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 44 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/12) | 1 |
| auto_dispatch | ok | placed=41 rejected=4 skipped=45 over 45 fan-out(s) to a keyed roster; top reasons: mode=45, NotionalTooSmall=4 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 79497.20 | 0 |
| candle_coverage | ok | 81/81 symbols with ≥20 15m candles, 81/81 updated within 45m [fresh=81; 74 Tier-1 futures + 7 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 954 dup bars, 0 undedupable; ws 0 out-of-order, 222 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +20 but output +0 (streak 2/72) | 2 |
| dark_atr_trail_arms | ok | no open arms; covering 1262/1279 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 9 of 101 open dark rows are not being advanced (worst: CAPUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 190/120) | 190 |
| dark_sar_arms | ok | no open arms; covering 1255/1272 signals (99%) | 0 |
| depth_feed | ok | 41/41 books fresh (stale 0, never 0, thin 0); 6676989 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.46R (bound 0.3) (streak 190/6) | 190 |
| emission_controller | ok | last cycle 1039s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×340]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 47/6) | 47 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 13/6) | 13 |
| footprint_bars | ok | 4817 sealed bars over 41 symbols; 1041 incomplete, 2 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +96 but output +0 (streak 5/6) | 5 |
| indicator_cache_key | ok | 51765 frozen value(s) avoided; 163936 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 6451 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.21R over n=1032, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 171/6) | 171 |
| mean_revert_path | ok | output +12 / upstream +96 | 0 |
| mover_admission_metadata | ok | 895 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 7 held, 7 with scan counts, 7 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2939 rows held, 1044437 evicted (sampled: execution:trigger_not_confirmed 400/381952, execution:overextended 400/360574, setup_compat:regime_STRONG_TREND 400/144216) | 0 |
| price_action_lane | ok | 481146 evaluated, 424 emitted; layer1 424 stamped / 0 blind; cooldown=56512, delta_opposed=44558, no_footprint=188382, no_opposing_target=1810, no_sweep=149746, rr_below_floor=39714 | 0 |
| promoted_pair_integrity | ok | 7/7 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.11R over n=256 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +42 / upstream +96 | 0 |
| sar_alignment_crosscheck | violating | 506/7586 disagreed (6.7%) (streak 74/6) | 74 |
| sar_exit_shadow | violating | upstream +96 but output +0 (streak 5/6) | 5 |
| sar_hold_arm | ok | 966 held arms settled, 164 unscored, 44 still walking (41 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 22/22 resolvable | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 43 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 1/12) | 1 |
| sar_refresh_budget | ok | 15 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 20 still mid-window | 0 |
| scan_cycle | ok | last 53.59s, worst 132.33s over 5412 lifetime cycles; lifetime 11 over 60s, 1 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.1s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 154620 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 11s ago (3.0s to run, worst 64.97s), 225 overrun(s) of 4110 cycles, TTL 900s; slowest dark_promotion=0.63s, data_intake=0.36s, signals=0.19s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=13, gate reads=0, withheld=13) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +72 / upstream +96 | 0 |
| structural_snap | ok | 4614/4614 measured, 10 blind, 0 levels moved (refusals: redetect_cooldown=264) | 0 |
| structural_veto_lane | ok | 557 stamped; 0 with no readable level book, 37 with clear air ahead, 431 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +96 / upstream +20 | 0 |
| tuned_variants | violating | 41 non-stamps — atr_arm_uncomputable=41 (seen=2313 stamped=255 skipped=2017) (streak 43/6) | 43 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 1 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2935296`
- `Path funnel` emissions: `74`
- `Regime distribution` emissions: `74`
- `QUIET_SCALP_BLOCK` events: `115`
- `confidence_gate` events: `5926`
- `free_channel_post` events: `59`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 4 | 15999 | 16021 | 21709 | 0 |
| futures_depth | 1 | 3416 | 3416 | 3416 | 0 |
| futures_liq | 1 | 4932 | 4932 | 4932 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **59**

| Source | Count |
|---|---:|
| signal_close | 53 |
| regime_shift | 4 |
| signal_highlight | 2 |

- By severity: HIGH=59

## Dependency readiness
- cvd: presence[present=525051] state[populated=525051] buckets[many=525051] sources[none] quality[none]
- funding_rate: presence[absent=60743, present=464308] state[empty=60743, populated=464308] buckets[few=464308, none=60743] sources[none] quality[none]
- liquidation_clusters: presence[absent=297442, present=227609] state[empty=297442, populated=227609] buckets[few=179890, none=297442, some=47719] sources[none] quality[none]
- oi_snapshot: presence[absent=59173, present=465878] state[empty=59173, populated=465878] buckets[few=126, many=464982, none=59173, some=770] sources[none] quality[none]
- order_book: presence[absent=135878, present=389173] state[populated=389173, unavailable=135878] buckets[few=389173, none=135878] sources[book_ticker=389173, unavailable=135878] quality[none=135878, top_of_book_only=389173]
- orderblocks: presence[absent=525051] state[empty=525051] buckets[none=525051] sources[measured_dark=525051] quality[none]
- recent_ticks: presence[present=525051] state[populated=525051] buckets[many=525051] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.113389015197754` sec
- Median create→first breach: `4354.129447937012` sec
- Median create→terminal: `4362.510717868805` sec
- Median first breach→terminal: `3.179225206375122` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.9}, "under_180s": {"count": 1, "pct": 1.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 1.9}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 1.9042561856896736 | 2.631437629399585 | 0.744562139955723 | 0 | 2 |
| MEAN_REVERT | 1 | 1 | 1.777432553892003 | 2.1161716201652614 | 0.8399283578678725 | 0 | 1 |
| MOVER_AVWAP_SCALP | 6 | 6 | 2.413176239784556 | 2.57252852533515 | 0.9753515898237572 | 2 | 3 |
| MOVER_TREND_PULLBACK | 36 | 36 | 4.209859459313188 | 3.0 | 1.4032864864377292 | 30 | 6 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 1.8453416076734048 | 1.9909984513621892 | 0.8941639782412039 | 0 | 7 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 1.0072 | 1526.47478890419 | 1530.3357660770416 |
| MEAN_REVERT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4913.2569370269775 | 4917.845261096954 |
| MOVER_AVWAP_SCALP | 6 | 6 | 0.0 | 50.0 | 0.0 | 0.0 | -0.1842 | 3753.5983934402466 | 3789.254798054695 |
| MOVER_TREND_PULLBACK | 36 | 36 | 0.0 | 41.7 | 0.0 | 0.0 | 0.2713 | 2968.0071049928665 | 2968.5502469539642 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 12.5 | 50.0 | 12.5 | 0.0 | -0.657 | 15648.518892526627 | 15651.63935494423 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1080 | 4 | 876 | 0.0 | 0.0 | None | None | 204 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1960 | 16 | 1813 | 0.0 | 0.0 | None | None | 147 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `147`
- Gating Δ: `4457`
- No-generation Δ: `516613`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.3807, "current_avg_pnl": -0.1842, "current_win_rate": 0.0, "previous_avg_pnl": 0.1965, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.3896, "current_avg_pnl": 0.2713, "current_win_rate": 0.0, "previous_avg_pnl": 0.6609, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.265, "current_avg_pnl": -0.657, "current_win_rate": 12.5, "previous_avg_pnl": 0.608, "previous_win_rate": 50.0, "win_rate_delta": -37.5}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 21, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 22, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
