# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, BREAKDOWN_SHORT
- Top promising signals/paths: LIQUIDITY_SWEEP_REVERSAL, QUIET_COMPRESSION_BREAK, FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `838` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 134 | 134 | 56 | 8 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9899 | 9899 | 7921 | 46 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 70028 | 70025 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 63942 | 63942 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 63619 | 60794 | 3136 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 63958 | 63410 | 616 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 63580 | 63442 | 153 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 52088 | 52099 | 6 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 64030 | 64061 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 64070 | 61657 | 3329 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 76228 | 82284 | 1165 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 70058 | 59742 | 16443 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 63333 | 63333 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 63945 | 63953 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 63601 | 63582 | 34 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 64993 | 62992 | 2502 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 63335 | 63358 | 219 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 51782 | 49331 | 2700 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 52036 | 51778 | 307 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 69980 | 70016 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 52108 | 52123 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2229 | 2229 | 1810 | 10 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 423 | 423 | 118 | 2 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 25 | 25 | 25 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 11621 | 11621 | 10593 | 69 | active-healthy (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 4 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8000 | 8000 | 7314 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2573 | 2573 | 198 | 119 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 40594 | 40594 | 14776 | 845 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 10 | 10 | 9 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 268 | 268 | 132 | 19 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 5698 | 5698 | 5631 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 586 | 586 | 452 | 8 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1337 | 1337 | 991 | 26 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 40 | 40 | 13 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=70025): breakout_not_found=30589, basic_filters_failed=21817, move_not_fresh=12618, breakout_stale=3077, retest_proximity_failed=1644, volume_spike_missing=249, move_exhausted=30, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=63942): cls_disabled_merged_into_lsr=63942
- **EVAL::DIVERGENCE_CONTINUATION** (total=60794): cvd_divergence_failed=30620, basic_filters_failed=18014, h1_trend_not_aligned=5504, ema_alignment_reject=5274, retest_proximity_failed=1113, missing_fvg_or_orderblock=269
- **EVAL::FAILED_AUCTION_RECLAIM** (total=63410): auction_not_detected=39999, basic_filters_failed=17257, reclaim_hold_failed=2483, regime_blocked=2295, tail_too_small=1369, rsi_reject=7
- **EVAL::FUNDING_EXTREME** (total=63442): funding_not_extreme=43182, basic_filters_failed=17775, ema_alignment_reject=1136, rsi_reject=589, missing_funding_rate=509, cvd_divergence_failed=139, momentum_reject=102, missing_fvg_or_orderblock=10
- **EVAL::LIQUIDATION_REVERSAL** (total=52099): cascade_threshold_not_met=33618, basic_filters_failed=17802, cvd_divergence_failed=356, rsi_reject=279, missing_fvg_or_orderblock=30, volume_spike_missing=14
- **EVAL::MA_CROSS_TREND_SHIFT** (total=64061): no_ma_cross=45599, basic_filters_failed=18031, ma_cross_cooldown=227, ma_cross_htf_misaligned=204
- **EVAL::MEAN_REVERT** (total=61657): no_extension=48274, basic_filters_failed=13383
- **EVAL::MOVER_AVWAP_SCALP** (total=82284): no_avwap_tag=38010, basic_filters_failed=22000, no_mover_leg=12359, avwap_slope_against=6751, avwap_reclaim_no_volume=1785, no_avwap_reclaim=1348, anchor_too_recent=31
- **EVAL::MOVER_TREND_PULLBACK** (total=59742): basic_filters_failed=21900, no_reclaim=17766, mover_run_too_small=15418, no_pullback_tag=4658
- **EVAL::OPENING_RANGE_BREAKOUT** (total=63333): feature_disabled=63333
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=63953): regime_blocked=36863, breakout_not_found=19111, basic_filters_failed=6070, adx_reject=1819, ema_alignment_reject=90
- **EVAL::QUIET_COMPRESSION_BREAK** (total=63582): regime_blocked=29253, compression_not_detected=22250, basic_filters_failed=11176, breakout_not_detected=784, volume_confirmation_failed=91, rsi_reject=28
- **EVAL::RANGE_FADE** (total=62992): no_range_edge=49605, basic_filters_failed=13387
- **EVAL::SR_FLIP_RETEST** (total=63358): flip_close_not_confirmed=39861, basic_filters_failed=17235, regime_blocked=2285, retest_out_of_zone=1365, h1_break_not_confirmed=1055, long_break_volume_thin=985, reclaim_hold_failed=344, ema_alignment_reject=60, wick_quality_failed=59, long_acceptance_not_held=59, whipsaw_flip=41, missing_fvg_or_orderblock=9
- **EVAL::STANDARD** (total=49331): momentum_reject=15485, basic_filters_failed=10085, adx_reject=9868, sweeps_not_detected=4333, ema_alignment_reject=4270, macd_reject=4004, htf_poi_unanchored=1110, rsi_reject=89, invalid_sl_geometry=76, mtf_reject=11
- **EVAL::TREND_PULLBACK** (total=51778): h1_pullback_not_confirmed=14538, basic_filters_failed=9226, h1_trend_not_aligned=7881, ema_not_tested_prev=6427, ema_alignment_reject=5611, no_ema_reclaim_close=3048, rsi_reject=2108, body_conviction_fail=1706, prev_already_below_emas=608, no_prev_low_break=305, momentum_flat=152, prev_already_above_emas=64, no_prev_high_break=45, ema21_not_tagged=31, missing_fvg_or_orderblock=24, momentum_reject=4
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=70016): breakout_not_found=41291, basic_filters_failed=21813, move_not_fresh=3859, breakout_stale=1965, retest_proximity_failed=914, volume_spike_missing=165, missing_fvg_or_orderblock=8, move_exhausted=1
- **EVAL::WHALE_MOMENTUM** (total=52123): momentum_reject=43280, recent_ticks_insufficient=6251, basic_filters_failed=2592

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=18): execution:overextended=18
- **DIVERGENCE_CONTINUATION** (total=72): setup_compat:regime_VOLATILE_UNSUITABLE=30, setup_compat:regime_BREAKOUT_EXPANSION=24, execution:overextended=18
- **FAILED_AUCTION_RECLAIM** (total=1109): execution:overextended=519, setup_compat:regime_STRONG_TREND=430, context_floor=109, setup_compat:regime_VOLATILE_UNSUITABLE=51
- **FUNDING_EXTREME_SIGNAL** (total=346): execution:trigger_not_confirmed=346
- **LIQUIDATION_REVERSAL** (total=25): execution:trigger_not_confirmed=25
- **LIQUIDITY_SWEEP_REVERSAL** (total=3213): setup_compat:regime_STRONG_TREND=1288, execution:overextended=1089, execution:trigger_not_confirmed=836
- **MA_CROSS_TREND_SHIFT** (total=10): setup_compat:regime_DIRTY_RANGE=4, execution:overextended=3, execution:trigger_not_confirmed=2, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=5712): setup_compat:regime_STRONG_TREND=2799, setup_compat:regime_WEAK_TREND=1671, execution:overextended=1226, entry_quality=16
- **MOVER_AVWAP_SCALP** (total=1871): execution:overextended=1348, entry_quality=374, execution:trigger_not_confirmed=149
- **MOVER_TREND_PULLBACK** (total=18019): execution:trigger_not_confirmed=7505, execution:overextended=6522, entry_quality=3992
- **QUIET_COMPRESSION_BREAK** (total=28): execution:trigger_not_confirmed=28
- **RANGE_FADE** (total=3609): setup_compat:regime_STRONG_TREND=2002, setup_compat:regime_WEAK_TREND=1338, setup_compat:regime_VOLATILE_UNSUITABLE=122, execution:overextended=81, setup_compat:regime_BREAKOUT_EXPANSION=54, context_edge=12
- **TREND_PULLBACK_EMA** (total=1144): setup_compat:regime_CLEAN_RANGE=630, setup_compat:regime_DIRTY_RANGE=369, entry_quality=110, setup_compat:regime_VOLATILE_UNSUITABLE=35

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 161588 | 44.1% |
| TRENDING_DOWN | 104855 | 28.6% |
| TRENDING_UP | 49374 | 13.5% |
| QUIET | 36753 | 10.0% |
| VOLATILE | 14181 | 3.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **173**
- Average confidence gap to threshold: **12.39** (samples=173) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ARBUSDT=35, AAVEUSDT=28, ETHUSDT=20, BNBUSDT=18, DOTUSDT=10, TAOUSDT=9, LINKUSDT=8, SUIUSDT=7, AVAXUSDT=5, INITUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 6 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 37 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 276 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 424 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 121 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 20 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 39 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 141 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 311 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 79 |
| MEAN_REVERT | kept | min_confidence_pass | 17 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 138 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 8 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1411 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 3168 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 120 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 10681 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 14 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 83 |
| SR_FLIP_RETEST | filtered | min_confidence | 17 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 5 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 46 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 27 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 13 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 100 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 3 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 12 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 6 | 58.92 | 65.00 | 6.08 | 17.53 | 14.03 | 20.00 | 3.25 | 11.67 |
| BREAKDOWN_SHORT | kept | 37 | 78.52 | 65.00 | -13.52 | 19.67 | 17.96 | 20.00 | 4.72 | 2.57 |
| DIVERGENCE_CONTINUATION | filtered | 277 | 54.11 | 63.54 | 9.43 | 20.67 | 19.79 | 18.26 | 1.16 | 15.76 |
| DIVERGENCE_CONTINUATION | kept | 424 | 69.56 | 65.00 | -4.56 | 20.53 | 19.76 | 18.07 | 1.11 | 0.05 |
| FAILED_AUCTION_RECLAIM | filtered | 121 | 49.99 | 60.17 | 10.18 | 19.51 | 19.33 | 20.00 | 2.22 | 9.52 |
| FAILED_AUCTION_RECLAIM | kept | 20 | 67.46 | 65.00 | -2.46 | 20.79 | 18.51 | 20.00 | 3.75 | 2.75 |
| FUNDING_EXTREME_SIGNAL | filtered | 39 | 46.31 | 62.95 | 16.64 | 20.66 | 15.67 | 17.71 | 4.21 | 6.94 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 66.53 | 65.00 | -1.53 | 20.98 | 17.00 | 17.00 | 2.00 | 1.75 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 161 | 57.77 | 64.98 | 7.21 | 20.08 | 18.94 | 17.83 | 2.07 | 12.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 311 | 69.89 | 65.00 | -4.89 | 21.11 | 19.33 | 18.03 | 1.60 | 0.43 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 65.90 | 65.00 | -0.90 | 19.00 | 20.00 | 15.80 | 0.00 | 0.50 |
| MEAN_REVERT | filtered | 79 | 58.57 | 65.00 | 6.43 | 21.75 | 16.83 | 14.70 | 0.00 | 17.27 |
| MEAN_REVERT | kept | 17 | 76.11 | 65.00 | -11.11 | 19.68 | 14.00 | 17.50 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 146 | 58.71 | 60.48 | 1.77 | 19.46 | 14.73 | 15.80 | 3.82 | 23.05 |
| MOVER_AVWAP_SCALP | kept | 1411 | 79.57 | 65.00 | -14.57 | 20.35 | 16.07 | 15.80 | 4.10 | 5.81 |
| MOVER_TREND_PULLBACK | filtered | 3288 | 56.44 | 64.15 | 7.71 | 20.04 | 18.42 | 15.80 | 4.21 | 18.31 |
| MOVER_TREND_PULLBACK | kept | 10681 | 76.06 | 65.00 | -11.06 | 20.73 | 18.36 | 15.80 | 4.36 | 2.55 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 61.50 | 65.00 | 3.50 | 20.70 | 20.00 | 17.80 | 4.50 | 4.80 |
| QUIET_COMPRESSION_BREAK | filtered | 36 | 47.61 | 65.00 | 17.39 | 20.96 | 18.65 | 20.00 | 0.00 | 15.76 |
| QUIET_COMPRESSION_BREAK | kept | 83 | 73.61 | 65.00 | -8.61 | 22.66 | 18.88 | 20.00 | 0.00 | -0.64 |
| SR_FLIP_RETEST | filtered | 22 | 58.62 | 65.00 | 6.38 | 20.01 | 20.00 | 15.61 | 1.48 | 11.16 |
| SR_FLIP_RETEST | kept | 46 | 72.87 | 65.00 | -7.87 | 21.13 | 20.00 | 15.30 | 2.57 | 0.15 |
| TREND_PULLBACK_EMA | filtered | 40 | 56.73 | 64.00 | 7.27 | 20.75 | 19.99 | 18.46 | 5.11 | 20.93 |
| TREND_PULLBACK_EMA | kept | 100 | 75.39 | 65.00 | -10.39 | 20.54 | 19.63 | 17.05 | 4.80 | 4.12 |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 31.00 | 65.00 | 34.00 | 20.60 | 20.00 | 20.00 | 3.00 | 22.00 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 81.46 | 65.00 | -16.46 | 18.73 | 17.63 | 20.00 | 4.54 | 0.25 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 6 | 58.92 | 17.00 | 14.67 | 12.00 | 14.00 | 5.00 | 4.75 | 3.25 |
| BREAKDOWN_SHORT | kept | 37 | 78.52 | 19.38 | 16.65 | 13.22 | 13.59 | 4.73 | 9.13 | 4.72 |
| DIVERGENCE_CONTINUATION | filtered | 277 | 54.11 | 21.82 | 16.23 | 4.02 | 12.31 | 5.26 | 9.12 | 1.16 |
| DIVERGENCE_CONTINUATION | kept | 424 | 69.56 | 22.40 | 15.92 | 4.81 | 12.61 | 5.24 | 9.16 | 1.11 |
| FAILED_AUCTION_RECLAIM | filtered | 121 | 49.99 | 22.16 | 17.34 | 4.21 | 14.45 | 6.71 | 4.82 | 2.22 |
| FAILED_AUCTION_RECLAIM | kept | 20 | 67.46 | 21.20 | 17.80 | 5.10 | 12.30 | 5.25 | 6.31 | 3.75 |
| FUNDING_EXTREME_SIGNAL | filtered | 39 | 46.31 | 22.13 | 9.13 | 5.92 | 13.00 | 7.42 | 5.67 | 4.21 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 66.53 | 23.00 | 11.00 | 3.75 | 11.50 | 7.88 | 9.15 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 161 | 57.77 | 23.15 | 14.97 | 4.66 | 11.92 | 5.09 | 7.98 | 2.07 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 311 | 69.89 | 22.76 | 14.95 | 4.77 | 12.74 | 5.35 | 8.31 | 1.60 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 65.90 | 17.00 | 14.00 | 6.00 | 14.00 | 6.75 | 8.65 | 0.00 |
| MEAN_REVERT | filtered | 79 | 58.57 | 23.48 | 17.85 | 11.47 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 17 | 76.11 | 24.41 | 14.00 | 12.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 146 | 58.71 | 18.11 | 18.22 | 13.32 | 13.76 | 5.54 | 9.30 | 3.82 |
| MOVER_AVWAP_SCALP | kept | 1411 | 79.57 | 19.89 | 18.02 | 13.13 | 13.95 | 6.54 | 9.76 | 4.10 |
| MOVER_TREND_PULLBACK | filtered | 3288 | 56.44 | 17.90 | 18.02 | 7.89 | 12.01 | 5.68 | 9.29 | 4.21 |
| MOVER_TREND_PULLBACK | kept | 10681 | 76.06 | 19.33 | 18.01 | 8.06 | 12.57 | 6.68 | 9.69 | 4.36 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 61.50 | 17.00 | 18.00 | 12.00 | 14.00 | 8.50 | 7.30 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 36 | 47.61 | 20.56 | 15.56 | 12.00 | 14.00 | 7.62 | 4.89 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 83 | 73.61 | 17.58 | 15.83 | 9.80 | 14.76 | 6.74 | 9.08 | 0.00 |
| SR_FLIP_RETEST | filtered | 22 | 58.62 | 18.91 | 15.73 | 5.05 | 14.68 | 5.80 | 8.22 | 1.48 |
| SR_FLIP_RETEST | kept | 46 | 72.87 | 22.91 | 16.70 | 3.39 | 12.76 | 5.23 | 9.60 | 2.57 |
| TREND_PULLBACK_EMA | filtered | 40 | 56.73 | 15.00 | 18.00 | 7.65 | 14.30 | 7.92 | 9.67 | 5.11 |
| TREND_PULLBACK_EMA | kept | 100 | 75.39 | 20.28 | 18.00 | 7.51 | 14.54 | 5.51 | 9.22 | 4.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 31.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 3.00 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 81.46 | 17.67 | 19.00 | 12.00 | 13.50 | 5.00 | 10.00 | 4.54 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 6 | 58.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.00 | **5.00** |
| BREAKDOWN_SHORT | kept | 37 | 78.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.32 | 0.00 | 0.00 | **0.32** |
| DIVERGENCE_CONTINUATION | filtered | 277 | 54.11 | 0.00 | 0.00 | 1.69 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | **1.78** |
| DIVERGENCE_CONTINUATION | kept | 424 | 69.56 | 0.00 | 0.00 | 0.75 | 0.00 | 0.03 | 0.06 | 0.00 | 0.00 | **0.84** |
| FAILED_AUCTION_RECLAIM | filtered | 121 | 49.99 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | **1.06** |
| FAILED_AUCTION_RECLAIM | kept | 20 | 67.46 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 39 | 46.31 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | **3.46** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 66.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 161 | 57.77 | 0.09 | 0.00 | 1.36 | 0.00 | 1.67 | 0.00 | 0.00 | 0.00 | **3.12** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 311 | 69.89 | 0.00 | 0.00 | 0.06 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **0.25** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 65.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 79 | 58.57 | 0.00 | 0.00 | 1.60 | 0.00 | 9.42 | 0.13 | 0.00 | 0.00 | **11.15** |
| MEAN_REVERT | kept | 17 | 76.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 146 | 58.71 | 4.11 | 0.00 | 3.29 | 0.00 | 1.89 | 1.41 | 0.00 | 0.00 | **10.70** |
| MOVER_AVWAP_SCALP | kept | 1411 | 79.57 | 2.06 | 0.00 | 0.53 | 0.00 | 0.85 | 0.38 | 0.00 | 0.03 | **3.85** |
| MOVER_TREND_PULLBACK | filtered | 3288 | 56.44 | 1.97 | 0.00 | 1.44 | 0.00 | 0.76 | 0.60 | 0.00 | 0.00 | **4.77** |
| MOVER_TREND_PULLBACK | kept | 10681 | 76.06 | 0.31 | 0.00 | 0.39 | 0.00 | 0.22 | 0.20 | 0.00 | 0.00 | **1.12** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 61.50 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 36 | 47.61 | 0.00 | 0.00 | 0.89 | 0.00 | 0.72 | 0.00 | 0.00 | 6.37 | **7.98** |
| QUIET_COMPRESSION_BREAK | kept | 83 | 73.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| SR_FLIP_RETEST | filtered | 22 | 58.62 | 0.00 | 0.00 | 0.00 | 0.00 | 4.91 | 0.00 | 0.00 | 0.00 | **4.91** |
| SR_FLIP_RETEST | kept | 46 | 72.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 40 | 56.73 | 0.00 | 0.00 | 6.20 | 0.00 | 2.16 | 0.00 | 0.00 | 0.00 | **8.36** |
| TREND_PULLBACK_EMA | kept | 100 | 75.39 | 0.00 | 0.00 | 0.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.72** |
| VOLUME_SURGE_BREAKOUT | filtered | 3 | 31.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 81.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **198718 held of 961115 seen** across 21 strategies; 4503 cells past the sample floor; **2443 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 49320 | 599/48721/0 | 44% | -0.18 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.26R) |
| MOVER_AVWAP_SCALP | 26442 | 187/26255/0 | 44% | -0.17 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 15877 | 277/15600/0 | 47% | -0.10 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+1.98R) | NY/MARKUP/CASCADE/BTC_FALLING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 14934 | 150/14784/0 | 36% | -0.33 | OVERLAP/RANGE/NORMAL/BTC_FALLING/MIDCAP (+1.66R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 14208 | 78/14130/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.38R) |
| LIQUIDITY_SWEEP_REVERSAL | 11415 | 124/11291/0 | 39% | -0.39 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.91R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 9724 | 501/9223/0 | 45% | -0.10 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8430 | 0/0/8430 | 42% | -0.10 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.99R) | OVERLAP/MARKDOWN/EXPANDED/BTC_FALLING (-0.96R) |
| SHADOW_RANGE_FADE | 7958 | 0/0/7958 | 35% | -0.14 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL (+0.43R) | OVERLAP/QUIET/NORMAL/BTC_FALLING (-1.36R) |
| SHADOW_FUNDING_FADE | 7562 | 0/0/7562 | 34% | -0.42 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.02R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 7498 | 30/7468/0 | 47% | -0.28 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.30R) |
| MEAN_REVERT | 5779 | 75/5704/0 | 37% | -0.31 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4578 | 4/4574/0 | 31% | -0.44 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.06R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.30R) |
| WHALE_MOMENTUM | 4395 | 4/4391/0 | 47% | -0.28 | NY/RANGE/EXPANDED/BTC_FALLING (+0.94R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 4153 | 0/4153/0 | 27% | -0.43 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/NORMAL/BTC_FALLING/ALTCOIN (-1.19R) |
| RANGE_FADE | 3181 | 6/3175/0 | 52% | +0.26 | OFF_HOURS/QUIET/NORMAL/BTC_FALLING (+3.08R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.78R) |
| SHADOW_CASCADE_REVERSAL | 1773 | 0/0/1773 | 52% | -0.09 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.54R) |
| BREAKDOWN_SHORT | 603 | 73/530/0 | 34% | -0.27 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 572 | 0/572/0 | 35% | -0.28 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 252 | 40/212/0 | 44% | -0.16 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 64 | 6/58/0 | 41% | +0.09 | — | — |

- **Strongest cells**: `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING` +3.08R (n=37, STRONG); `RANGE_FADE @ OFF_HOURS/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.08R (n=37, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_FALLING/ALTCOIN` +3.00R (n=32, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE); `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.78R (n=47, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 440 | 28% / -0.55R | 440 | 52% / -0.09R | +0.46 | **ATR** |
| TREND_PULLBACK_EMA | 1461 | 39% / -0.36R | 1461 | 50% / -0.08R | +0.28 | **ATR** |
| LIQUIDATION_REVERSAL | 35 | 26% / -0.58R | 35 | 46% / -0.34R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1764 | 44% / -0.33R | 1764 | 58% / -0.10R | +0.23 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 241 | 37% / -0.18R | 241 | 48% / -0.04R | +0.14 | **ATR** |
| BREAKDOWN_SHORT | 56 | 41% / -0.23R | 56 | 46% / -0.10R | +0.13 | **ATR** |
| MA_CROSS_TREND_SHIFT | 76 | 45% / -0.16R | 76 | 50% / -0.03R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 834 | 48% / -0.25R | 834 | 52% / -0.13R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 473 | 46% / -0.30R | 473 | 48% / -0.20R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1653 | 41% / -0.23R | 1653 | 44% / -0.13R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 2969 | 47% / -0.13R | 2969 | 53% / -0.03R | +0.10 | **ATR** |
| MOVER_TREND_PULLBACK | 9246 | 49% / -0.12R | 9246 | 54% / -0.02R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 2136 | 48% / -0.11R | 2136 | 53% / -0.06R | +0.05 | **ATR** |
| RANGE_FADE | 170 | 44% / +0.08R | 170 | 51% / +0.13R | +0.04 | **ATR** |
| MEAN_REVERT | 504 | 46% / -0.15R | 504 | 45% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1714 | 48% / -0.09R | 1714 | 48% / -0.09R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 14 | 57% / -0.06R | 14 | 57% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 12351 | 27% | -0.22R | 314 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2969 | 51% | -0.02R | 243 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 153 | 47% | -0.07R | 74 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1875 | 33% / -0.11R | +0.95 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 2108 | 41% / -0.10R | +0.90 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3532 | 37% / -0.12R | +0.72 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 11336 | 36% / -0.17R | +0.36 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2479 | 37% / -0.11R | +0.17 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 172 | 34% / -0.39R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1665 | 37% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1386 | 32% / -0.27R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 353 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 555 | 32% / -0.25R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 418 | 48% / -0.06R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 97 | 43% / -0.03R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 120 | 47% / +0.06R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 722 | 37% / -0.24R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 124 | 31% / +0.13R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 46 | 43% / -0.26R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 26 | 46% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 64 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.56R (bound 0.3) (streak 230/6) (sustained 230 cycles)
- **ALERT** `range_fade_emission` — 5398 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.26R over n=3175, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 188/6) (sustained 188 cycles)
- **ALERT** `tuned_variants` — 356 non-stamps — atr_arm_uncomputable=356 (seen=12134 stamped=1821 skipped=9957) (streak 230/6) (sustained 230 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 62112717 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 37 arms current, none stalled; covering 2086/2086 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| analyst_plan_cadence | ok | last plan 56m ago | 0 |
| atr_trail_live_arms | ok | 88 arms current, none stalled; covering 1092/1092 signals (100%) | 0 |
| auto_dispatch | ok | 67 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=67. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 373/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 58131.20 | 0 |
| candle_coverage | ok | 117/117 symbols with ≥20 15m candles, 112/117 updated within 45m [stale=5, fresh=112; 73 Tier-1 futures + 44 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 2861 dup bars, 0 undedupable; ws 0 out-of-order, 279 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 63 cohorts, 27 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +8 / upstream +14 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 2252/2271 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 6 promoted today, nothing refused | 0 |
| dark_resolution | violating | 27 of 175 open dark rows are not being advanced (worst: TRBUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 32/120) | 32 |
| dark_sar_arms | ok | no open arms; covering 2246/2265 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 15440636 msgs, 0 rejected | 0 |
| deriv_recorder | ok | hour recorded, 73 rows | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.56R (bound 0.3) (streak 230/6) | 230 |
| emission_controller | ok | last cycle 473s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=145, MOVER_AVWAP_SCALP=302, MOVER_TREND_PULLBACK=5046, RANGE_FADE=457, TREND_PULLBACK_EMA=50), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 4 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won,TREND_PULLBACK_EMA.campaign_prev_age_h,TREND_PULLBACK_EMA.campaign_prev_won) | 0 |
| entry_quality_effective | ok | 19928 evaluated, 5611 suppressed, 5502 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| firestore_read_budget | ok | 1,330 reads/day of 50,000 [engine 1,308, signing 22]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 2499 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +496 | 0 |
| htf_candles | ok | BTCUSDT 1d/1w current | 0 |
| indicator_cache_key | ok | 87554 frozen value(s) avoided; 132126 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.31R over n=5704 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +14 / upstream +496 | 0 |
| mover_admission_metadata | ok | 956 symbols known, 247 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 44 held, 44 with scan counts, 44 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 6 locked / 6 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2217 rows held, 3774039 evicted (sampled: execution:trigger_not_confirmed 278/1325078, execution:overextended 278/1159835, setup_compat:regime_STRONG_TREND 277/652356) | 0 |
| price_action_lane | ok | 464297 evaluated, 709 emitted; layer1 709 stamped / 0 blind; cooldown=60080, delta_opposed=43653, no_footprint=183541, no_opposing_target=1481, no_sweep=135826, rr_below_floor=39007 | 0 |
| promoted_pair_integrity | ok | 44/44 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 5398 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.26R over n=3175, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 188/6) | 188 |
| range_fade_path | ok | output +10 / upstream +496 | 0 |
| sar_alignment_crosscheck | ok | 571/28018 disagreed (2.0%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +496 | 0 |
| sar_hold_arm | ok | 1878 held arms settled, 124 unscored, 84 still walking (70 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 6/42 unfetchable (14%); top cause: gap or duplicate bar in the 15m window; symbols: HUMAUSDT, WLFIUSDT, XPLUSDT | 0 |
| sar_live_arms | ok | 86 arms current, none stalled; covering 1092/1092 signals (100%) | 0 |
| sar_refresh_budget | ok | 6 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 34 still mid-window | 0 |
| scan_cycle | ok | last 145.35s, worst 207.59s over 5261 lifetime cycles; lifetime 265 over 60s, 53 over 120s; recent 2/2 warn/kill breaches in 20/20 cycles; heartbeat age 15.59s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 253346 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| snapshot_writer | ok | last cycle 13s ago (11.85s to run, worst 162.63s), 889 overrun(s) of 5028 cycles, TTL 900s; slowest tickers=8.57s, router_delivery=1.58s, dark_promotion=1.57s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=28, gate reads=0, withheld=28) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +175 / upstream +496 | 0 |
| structural_snap | ok | 6000/6000 measured, 35 blind, 0 levels moved (refusals: redetect_cooldown=1656) | 0 |
| structural_veto_lane | ok | 3032 stamped; 0 with no readable level book, 326 with clear air ahead, 2007 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +496 / upstream +14 | 0 |
| tuned_variants | violating | 356 non-stamps — atr_arm_uncomputable=356 (seen=12134 stamped=1821 skipped=9957) (streak 230/6) | 230 |
| unlock_shorts | ok | 17 open, 44 scheduled, calendar 6.0h old | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2082176`
- `Path funnel` emissions: `41`
- `Regime distribution` emissions: `41`
- `QUIET_SCALP_BLOCK` events: `173`
- `confidence_gate` events: `17367`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **119**
- Total REST-fallback activations: **27**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 34 | 8119 | 35623 | 49303 | 0 |
| futures_aggtrade | 72 | 8629 | 33688 | 46959 | 0 |
| futures_depth | 8 | 7181 | 19960 | 50983 | 0 |
| futures_liq | 3 | 5226 | 5226 | 22754 | 0 |
| futures_mover | 2 | 10005 | 10005 | 17137 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 27 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=266222] state[populated=266222] buckets[many=266222] sources[none] quality[none]
- funding_rate: presence[absent=39916, present=226306] state[empty=39916, populated=226306] buckets[few=226306, none=39916] sources[none] quality[none]
- liquidation_clusters: presence[absent=139997, present=126225] state[empty=139997, populated=126225] buckets[few=97436, none=139997, some=28789] sources[none] quality[none]
- oi_snapshot: presence[absent=39916, present=226306] state[empty=39916, populated=226306] buckets[few=149, many=224105, none=39916, some=2052] sources[none] quality[none]
- order_book: presence[absent=101926, present=164296] state[populated=164296, unavailable=101926] buckets[few=164296, none=101926] sources[book_ticker=164296, unavailable=101926] quality[none=101926, top_of_book_only=164296]
- orderblocks: presence[absent=266222] state[empty=266222] buckets[none=266222] sources[measured_dark=266222] quality[none]
- recent_ticks: presence[present=266222] state[populated=266222] buckets[many=266222] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.533981084823608` sec
- Median create→first breach: `2901.7250690460205` sec
- Median create→terminal: `2902.1350910663605` sec
- Median first breach→terminal: `0.00011491775512695312` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 3.5}, "under_180s": {"count": 2, "pct": 3.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 3.5}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 1.9282694327731122 | 2.142857142857148 | 0.8998590686274501 | 0 | 3 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.8691201286691655 | 1.5068704052961739 | 0.5309016602809754 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 1.815426709462151 | 3.0 | 0.7766848323398149 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 1.252667413399267 | 1.4552077898136848 | 0.8608168690188569 | 0 | 3 |
| MOVER_AVWAP_SCALP | 2 | 2 | 3.1955760929832238 | 3.0 | 1.065192030994408 | 1 | 1 |
| MOVER_TREND_PULLBACK | 36 | 36 | 4.136314297197659 | 3.0 | 1.4282249005675167 | 28 | 8 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.5823634240767988 | 1.6002666149092921 | 0.9207791351794035 | 0 | 5 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 4.017857142857152 | 2.8924107142857154 | 0 | 0 | 0 | 3 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 3 | 2.2615535889872085 | 2.2615535889872085 | 0 | 0 | 0 | 1 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 4 | 3.6308525431473084 | 3.6308525431473084 | 1 | 0 | 0 | 1 | 0 | 2 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 2.331506849315068 | 1.8790011202140424 | 0 | 0 | 0 | 2 | 1 | 1 |
| MOVER_AVWAP_SCALP | 2 | 3.7206827312189414 | 3.798369892862773 | 1 | 0 | 0 | 0 | 0 | 1 |
| MOVER_TREND_PULLBACK | 36 | 4.777109081408734 | 3.9374336856928354 | 10 | 1 | 1 | 25 | 3 | 1 |
| QUIET_COMPRESSION_BREAK | 6 | 3.588705783842907 | 2.955131923165215 | 0 | 0 | 0 | 4 | 3 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 33.3 | 66.7 | 33.3 | 0.0 | 0.3521 | 3678.653288125992 | 3678.653336048126 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 0.8262 | 2901.7250690460205 | 2902.1350910663605 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 75.0 | 0.0 | 75.0 | 0.0 | 2.8145 | 2851.413873076439 | 2851.5854300260544 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 100.0 | 0.0 | 100.0 | 0.0 | 1.8887 | 1302.4904899597168 | 1302.9046580791473 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -1.2096 | 704.3360840082169 | 704.3361431360245 |
| MOVER_TREND_PULLBACK | 36 | 36 | 27.8 | 30.6 | 27.8 | 0.0 | 0.7803 | 2417.3496963977814 | 2417.3497170209885 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 100.0 | 0.0 | 100.0 | 0.0 | 2.7754 | 19667.708415031433 | 19669.634239554405 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 586 | 8 | 452 | 0.0 | 0.0 | None | None | 134 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1337 | 26 | 991 | 0.0 | 0.0 | None | None | 346 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `465`
- Gating Δ: `-16588`
- No-generation Δ: `-514414`
- Fast failures Δ: `2`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -3.2726, "current_avg_pnl": 0.3521, "current_win_rate": 33.3, "previous_avg_pnl": 3.6247, "previous_win_rate": 100.0, "win_rate_delta": -66.7}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.1738, "current_avg_pnl": 0.8262, "current_win_rate": 33.3, "previous_avg_pnl": 1.0, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.4688, "current_avg_pnl": 2.8145, "current_win_rate": 75.0, "previous_avg_pnl": 1.3457, "previous_win_rate": 42.9, "win_rate_delta": 32.1}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 1.005, "current_avg_pnl": 1.8887, "current_win_rate": 100.0, "previous_avg_pnl": 0.8837, "previous_win_rate": 57.1, "win_rate_delta": 42.9}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.1628, "current_avg_pnl": -1.2096, "current_win_rate": 0.0, "previous_avg_pnl": -1.3724, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.5811, "current_avg_pnl": 0.7803, "current_win_rate": 27.8, "previous_avg_pnl": 0.1992, "previous_win_rate": 35.7, "win_rate_delta": -7.9}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 2.7612, "current_avg_pnl": 2.7754, "current_win_rate": 100.0, "previous_avg_pnl": 0.0142, "previous_win_rate": 28.6, "win_rate_delta": 71.4}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": -159, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -14, "geometry_changed_delta": 0, "geometry_preserved_delta": -241, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **LIQUIDITY_SWEEP_REVERSAL**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
