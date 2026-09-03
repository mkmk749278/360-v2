# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MEAN_REVERT, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: DIVERGENCE_CONTINUATION
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `737` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 62 | 62 | 60 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10305 | 10305 | 9025 | 17 | active-healthy (none) |
| EVAL::BREAKDOWN_SHORT | 70820 | 70844 | 13 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 67274 | 67274 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 66794 | 64163 | 3086 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 67322 | 66686 | 718 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 67615 | 67409 | 235 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 58060 | 58072 | 11 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 67414 | 67465 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 67481 | 65426 | 2956 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 75275 | 80202 | 779 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 70865 | 64379 | 10818 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 67119 | 67119 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 67284 | 67298 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 66745 | 66619 | 171 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 68388 | 67000 | 1994 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 66210 | 66577 | 115 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 56885 | 53532 | 3737 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 57267 | 56951 | 391 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 70754 | 70790 | 23 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 58088 | 58107 | 7 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2293 | 2293 | 2032 | 7 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 641 | 641 | 331 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 23 | 23 | 8 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 17561 | 17561 | 16898 | 34 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 7 | 7 | 5 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6980 | 6980 | 5198 | 7 | active-low-quality (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1765 | 1765 | 1051 | 43 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 25298 | 25298 | 16019 | 345 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 22 | 22 | 21 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 596 | 596 | 331 | 25 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5292 | 5292 | 4187 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 446 | 446 | 344 | 11 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1471 | 1471 | 1205 | 38 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 125 | 125 | 29 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 100 | 100 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=70844): breakout_not_found=41805, basic_filters_failed=19241, move_not_fresh=6337, breakout_stale=2455, retest_proximity_failed=795, volume_spike_missing=185, move_exhausted=13, missing_fvg_or_orderblock=13
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=67274): cls_disabled_merged_into_lsr=67274
- **EVAL::DIVERGENCE_CONTINUATION** (total=64163): cvd_divergence_failed=25031, basic_filters_failed=16385, h1_trend_not_aligned=16182, ema_alignment_reject=5567, retest_proximity_failed=706, missing_fvg_or_orderblock=292
- **EVAL::FAILED_AUCTION_RECLAIM** (total=66686): auction_not_detected=43457, basic_filters_failed=15790, reclaim_hold_failed=2672, regime_blocked=2462, tail_too_small=2296, rsi_reject=9
- **EVAL::FUNDING_EXTREME** (total=67409): funding_not_extreme=46461, basic_filters_failed=15999, missing_funding_rate=2475, ema_alignment_reject=1521, rsi_reject=545, cvd_divergence_failed=207, momentum_reject=169, missing_fvg_or_orderblock=32
- **EVAL::LIQUIDATION_REVERSAL** (total=58072): cascade_threshold_not_met=40878, basic_filters_failed=16408, cvd_divergence_failed=421, rsi_reject=344, missing_fvg_or_orderblock=16, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=67465): no_ma_cross=50030, basic_filters_failed=16407, ma_cross_cooldown=700, ma_cross_htf_misaligned=313, ma_cross_htf_unconfirmed=15
- **EVAL::MEAN_REVERT** (total=65426): no_extension=53417, basic_filters_failed=12009
- **EVAL::MOVER_AVWAP_SCALP** (total=80202): no_avwap_tag=28236, no_mover_leg=23408, basic_filters_failed=19519, avwap_slope_against=5251, avwap_reclaim_no_volume=2145, no_avwap_reclaim=1556, anchor_too_recent=87
- **EVAL::MOVER_TREND_PULLBACK** (total=64379): mover_run_too_small=30154, basic_filters_failed=19388, no_reclaim=12440, no_pullback_tag=2350, insufficient_candles=47
- **EVAL::OPENING_RANGE_BREAKOUT** (total=67119): feature_disabled=67119
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=67298): regime_blocked=48747, breakout_not_found=11656, basic_filters_failed=4552, adx_reject=2282, ema_alignment_reject=61
- **EVAL::QUIET_COMPRESSION_BREAK** (total=66619): compression_not_detected=27888, regime_blocked=20916, basic_filters_failed=11225, breakout_not_detected=6036, volume_confirmation_failed=504, rsi_reject=49, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=67000): no_range_edge=54856, basic_filters_failed=12019, shadow_mode=125
- **EVAL::SR_FLIP_RETEST** (total=66577): flip_close_not_confirmed=42723, basic_filters_failed=15760, regime_blocked=2448, long_break_volume_thin=2046, retest_out_of_zone=1602, h1_break_not_confirmed=1161, reclaim_hold_failed=429, ema_alignment_reject=127, long_acceptance_not_held=120, whipsaw_flip=94, wick_quality_failed=57, missing_fvg_or_orderblock=10
- **EVAL::STANDARD** (total=53532): momentum_reject=14636, adx_reject=13769, basic_filters_failed=9273, sweeps_not_detected=6103, macd_reject=5527, ema_alignment_reject=2914, htf_poi_unanchored=1221, invalid_sl_geometry=63, rsi_reject=25, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=56951): h1_trend_not_aligned=18304, basic_filters_failed=9845, ema_alignment_reject=9786, h1_pullback_not_confirmed=5450, ema_not_tested_prev=4734, no_ema_reclaim_close=3703, body_conviction_fail=1990, rsi_reject=1551, prev_already_below_emas=529, prev_already_above_emas=346, no_prev_low_break=232, no_prev_high_break=216, momentum_flat=166, missing_fvg_or_orderblock=39, ema21_not_tagged=34, momentum_reject=26
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=70790): breakout_not_found=37061, basic_filters_failed=19238, move_not_fresh=9751, breakout_stale=3165, retest_proximity_failed=1371, volume_spike_missing=176, missing_fvg_or_orderblock=17, move_exhausted=11
- **EVAL::WHALE_MOMENTUM** (total=58107): momentum_reject=48973, recent_ticks_insufficient=6400, basic_filters_failed=2734

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=39): execution:overextended=39
- **DIVERGENCE_CONTINUATION** (total=274): setup_compat:regime_VOLATILE_UNSUITABLE=217, setup_compat:regime_BREAKOUT_EXPANSION=57
- **FAILED_AUCTION_RECLAIM** (total=756): execution:overextended=353, setup_compat:regime_STRONG_TREND=309, setup_compat:regime_VOLATILE_UNSUITABLE=81, context_floor=13
- **FUNDING_EXTREME_SIGNAL** (total=524): execution:trigger_not_confirmed=518, context_floor=6
- **LIQUIDATION_REVERSAL** (total=23): execution:trigger_not_confirmed=23
- **LIQUIDITY_SWEEP_REVERSAL** (total=3854): execution:trigger_not_confirmed=1768, execution:overextended=1347, setup_compat:regime_STRONG_TREND=739
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_CLEAN_RANGE=3, execution:trigger_not_confirmed=3, setup_compat:regime_DIRTY_RANGE=1, execution:overextended=1
- **MEAN_REVERT** (total=2788): setup_compat:regime_STRONG_TREND=1441, setup_compat:regime_WEAK_TREND=866, execution:overextended=481
- **MOVER_AVWAP_SCALP** (total=1013): execution:overextended=852, execution:trigger_not_confirmed=104, entry_quality=57
- **MOVER_TREND_PULLBACK** (total=11547): execution:trigger_not_confirmed=6127, execution:overextended=4482, entry_quality=938
- **QUIET_COMPRESSION_BREAK** (total=47): execution:trigger_not_confirmed=42, execution:overextended=5
- **RANGE_FADE** (total=2681): setup_compat:regime_STRONG_TREND=1178, setup_compat:regime_WEAK_TREND=894, setup_compat:regime_VOLATILE_UNSUITABLE=377, execution:overextended=165, context_edge=65, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=1312): setup_compat:regime_CLEAN_RANGE=860, setup_compat:regime_DIRTY_RANGE=432, entry_quality=11, setup_compat:regime_VOLATILE_UNSUITABLE=9
- **VOLUME_SURGE_BREAKOUT** (total=51): context_floor=40, execution:overextended=11
- **WHALE_MOMENTUM** (total=83): execution:trigger_not_confirmed=83

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 179634 | 52.3% |
| QUIET | 53378 | 15.5% |
| TRENDING_UP | 49669 | 14.4% |
| TRENDING_DOWN | 43757 | 12.7% |
| VOLATILE | 17318 | 5.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **108**
- Average confidence gap to threshold: **11.59** (samples=108) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=33, TRXUSDT=14, DASHUSDT=10, LINKUSDT=9, DOTUSDT=6, WLDUSDT=6, INJUSDT=6, TAOUSDT=4, FETUSDT=4, AAVEUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 81 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 6 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 98 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 109 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 10 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 25 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 25 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 15 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 193 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 13 |
| MEAN_REVERT | kept | min_confidence_pass | 90 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 160 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 6 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 411 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 320 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 12 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 4600 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 63 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 46 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 88 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | filtered | min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 24 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 32 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 125 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 14 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 30 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 74.25 | 65.00 | -9.25 | 19.15 | 17.35 | 20.00 | 4.75 | 1.80 |
| DIVERGENCE_CONTINUATION | filtered | 87 | 53.28 | 63.83 | 10.55 | 21.63 | 19.82 | 17.91 | 1.90 | 13.40 |
| DIVERGENCE_CONTINUATION | kept | 98 | 68.51 | 65.00 | -3.51 | 20.86 | 19.39 | 18.26 | 1.58 | 0.26 |
| FAILED_AUCTION_RECLAIM | filtered | 119 | 52.72 | 63.64 | 10.92 | 21.13 | 19.66 | 20.00 | 2.87 | 7.96 |
| FAILED_AUCTION_RECLAIM | kept | 25 | 69.84 | 65.00 | -4.84 | 20.46 | 19.16 | 20.00 | 2.56 | 6.80 |
| FUNDING_EXTREME_SIGNAL | filtered | 25 | 53.17 | 62.92 | 9.75 | 20.00 | 13.94 | 16.98 | 3.32 | 1.60 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 64.47 | 65.00 | 0.53 | 20.55 | 13.38 | 17.00 | 3.00 | 4.25 |
| LIQUIDATION_REVERSAL | filtered | 15 | 65.50 | 10.00 | -55.50 | 18.01 | 8.00 | 20.00 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 83 | 54.42 | 64.81 | 10.39 | 19.08 | 17.92 | 18.28 | 1.71 | 17.38 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 193 | 70.84 | 65.00 | -5.84 | 21.81 | 18.93 | 17.25 | 2.39 | 0.02 |
| MEAN_REVERT | filtered | 13 | 57.50 | 65.00 | 7.50 | 24.53 | 18.25 | 16.34 | 0.00 | 17.82 |
| MEAN_REVERT | kept | 90 | 71.03 | 65.00 | -6.03 | 20.75 | 17.16 | 15.91 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 166 | 54.46 | 64.86 | 10.40 | 19.49 | 15.39 | 15.80 | 3.61 | 15.92 |
| MOVER_AVWAP_SCALP | kept | 411 | 79.66 | 65.00 | -14.66 | 19.96 | 16.78 | 15.80 | 4.31 | 2.04 |
| MOVER_TREND_PULLBACK | filtered | 332 | 59.41 | 65.00 | 5.59 | 20.69 | 18.80 | 15.80 | 4.12 | 13.26 |
| MOVER_TREND_PULLBACK | kept | 4600 | 77.30 | 65.00 | -12.30 | 20.04 | 18.58 | 15.80 | 4.21 | 0.76 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.20 | 65.00 | -19.20 | 18.50 | 20.00 | 20.00 | 4.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 109 | 51.11 | 63.86 | 12.75 | 22.14 | 19.12 | 20.00 | 0.00 | 10.31 |
| QUIET_COMPRESSION_BREAK | kept | 88 | 74.39 | 65.00 | -9.39 | 21.00 | 19.21 | 20.00 | 0.00 | -0.10 |
| SR_FLIP_RETEST | filtered | 7 | 54.54 | 65.00 | 10.46 | 20.71 | 20.00 | 17.40 | 2.29 | 15.34 |
| SR_FLIP_RETEST | kept | 24 | 73.16 | 65.00 | -8.16 | 20.76 | 20.00 | 15.66 | 2.21 | -0.61 |
| TREND_PULLBACK_EMA | filtered | 37 | 59.53 | 64.35 | 4.82 | 22.33 | 20.00 | 15.63 | 5.64 | 19.49 |
| TREND_PULLBACK_EMA | kept | 125 | 78.24 | 65.00 | -13.24 | 21.16 | 19.81 | 17.58 | 4.57 | 0.05 |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 50.47 | 62.71 | 12.24 | 19.61 | 17.60 | 20.00 | 3.86 | 15.00 |
| VOLUME_SURGE_BREAKOUT | kept | 30 | 78.91 | 65.00 | -13.91 | 20.54 | 18.00 | 20.00 | 4.92 | 3.06 |
| WHALE_MOMENTUM | filtered | 3 | 59.40 | 65.00 | 5.60 | 20.47 | 18.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 74.25 | 13.50 | 18.00 | 13.50 | 15.50 | 5.00 | 5.80 | 4.75 |
| DIVERGENCE_CONTINUATION | filtered | 87 | 53.28 | 22.79 | 10.07 | 5.62 | 13.93 | 5.99 | 7.58 | 1.90 |
| DIVERGENCE_CONTINUATION | kept | 98 | 68.51 | 23.04 | 12.49 | 6.28 | 12.97 | 5.31 | 8.48 | 1.58 |
| FAILED_AUCTION_RECLAIM | filtered | 119 | 52.72 | 23.89 | 17.29 | 5.12 | 13.58 | 6.53 | 3.24 | 2.87 |
| FAILED_AUCTION_RECLAIM | kept | 25 | 69.84 | 23.64 | 17.68 | 9.72 | 12.68 | 6.82 | 4.14 | 2.56 |
| FUNDING_EXTREME_SIGNAL | filtered | 25 | 53.17 | 23.40 | 10.00 | 8.16 | 12.68 | 9.10 | 2.51 | 3.32 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 64.47 | 25.00 | 8.00 | 3.75 | 11.25 | 9.75 | 7.98 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 15 | 65.50 | 25.00 | 8.00 | 12.00 | 8.00 | 2.50 | 4.00 | 6.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 83 | 54.42 | 22.54 | 14.10 | 8.42 | 13.36 | 5.72 | 5.95 | 1.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 193 | 70.84 | 23.65 | 14.10 | 5.24 | 12.77 | 6.25 | 6.46 | 2.39 |
| MEAN_REVERT | filtered | 13 | 57.50 | 20.08 | 18.00 | 11.54 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 90 | 71.03 | 19.93 | 18.00 | 7.53 | 12.99 | 4.97 | 7.60 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 166 | 54.46 | 19.14 | 18.08 | 12.36 | 14.00 | 7.31 | 5.72 | 3.61 |
| MOVER_AVWAP_SCALP | kept | 411 | 79.66 | 19.87 | 18.13 | 11.47 | 13.82 | 6.89 | 7.72 | 4.31 |
| MOVER_TREND_PULLBACK | filtered | 332 | 59.41 | 17.75 | 18.03 | 7.89 | 13.12 | 5.79 | 8.30 | 4.12 |
| MOVER_TREND_PULLBACK | kept | 4600 | 77.30 | 19.09 | 18.01 | 7.71 | 13.16 | 6.60 | 9.40 | 4.21 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.20 | 17.00 | 18.00 | 15.00 | 17.00 | 5.00 | 7.70 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 109 | 51.11 | 18.03 | 15.69 | 10.71 | 14.06 | 8.39 | 5.15 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 88 | 74.39 | 18.55 | 16.45 | 12.00 | 14.09 | 7.27 | 7.61 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 54.54 | 21.57 | 12.29 | 6.43 | 14.00 | 5.00 | 8.31 | 2.29 |
| SR_FLIP_RETEST | kept | 24 | 73.16 | 22.33 | 16.75 | 5.25 | 13.25 | 5.12 | 8.75 | 2.21 |
| TREND_PULLBACK_EMA | filtered | 37 | 59.53 | 16.19 | 18.00 | 8.07 | 14.41 | 7.65 | 9.07 | 5.64 |
| TREND_PULLBACK_EMA | kept | 125 | 78.24 | 18.74 | 18.00 | 7.55 | 14.33 | 7.36 | 9.05 | 4.57 |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 50.47 | 21.57 | 14.00 | 13.29 | 14.00 | 3.57 | 3.76 | 3.86 |
| VOLUME_SURGE_BREAKOUT | kept | 30 | 78.91 | 19.93 | 17.47 | 12.30 | 13.20 | 5.00 | 9.66 | 4.92 |
| WHALE_MOMENTUM | filtered | 3 | 59.40 | 25.00 | 8.00 | 9.00 | 13.67 | 6.50 | 7.23 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 74.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.80 | **1.80** |
| DIVERGENCE_CONTINUATION | filtered | 87 | 53.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.74 | 0.00 | 0.00 | 0.00 | **0.74** |
| DIVERGENCE_CONTINUATION | kept | 98 | 68.51 | 0.00 | 0.00 | 0.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.65** |
| FAILED_AUCTION_RECLAIM | filtered | 119 | 52.72 | 0.00 | 0.00 | 0.44 | 0.00 | 1.41 | 0.00 | 0.00 | 0.00 | **1.85** |
| FAILED_AUCTION_RECLAIM | kept | 25 | 69.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 25 | 53.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 64.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 15 | 65.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 83 | 54.42 | 0.00 | 0.00 | 0.50 | 0.00 | 3.38 | 0.00 | 0.00 | 0.00 | **3.88** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 193 | 70.84 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.02** |
| MEAN_REVERT | filtered | 13 | 57.50 | 0.00 | 0.00 | 0.00 | 0.00 | 1.66 | 0.00 | 0.00 | 0.00 | **1.66** |
| MEAN_REVERT | kept | 90 | 71.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 166 | 54.46 | 0.81 | 0.00 | 1.16 | 0.00 | 4.94 | 0.00 | 0.00 | 1.52 | **8.43** |
| MOVER_AVWAP_SCALP | kept | 411 | 79.66 | 0.04 | 0.00 | 0.07 | 0.00 | 1.16 | 0.00 | 0.00 | 0.63 | **1.90** |
| MOVER_TREND_PULLBACK | filtered | 332 | 59.41 | 0.66 | 0.00 | 3.46 | 0.00 | 0.78 | 0.03 | 0.00 | 0.00 | **4.93** |
| MOVER_TREND_PULLBACK | kept | 4600 | 77.30 | 0.00 | 0.00 | 0.51 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | **0.58** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 84.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 109 | 51.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.14 | 0.00 | 0.00 | 3.20 | **3.34** |
| QUIET_COMPRESSION_BREAK | kept | 88 | 74.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.39 | 0.00 | 0.00 | 0.07 | **0.46** |
| SR_FLIP_RETEST | filtered | 7 | 54.54 | 0.00 | 0.00 | 0.00 | 0.00 | 12.34 | 0.00 | 0.00 | 0.00 | **12.34** |
| SR_FLIP_RETEST | kept | 24 | 73.16 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.20** |
| TREND_PULLBACK_EMA | filtered | 37 | 59.53 | 0.00 | 0.00 | 0.00 | 0.00 | 2.92 | 0.00 | 0.00 | 0.00 | **2.92** |
| TREND_PULLBACK_EMA | kept | 125 | 78.24 | 0.00 | 0.00 | 1.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.25** |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 50.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.43 | **3.43** |
| VOLUME_SURGE_BREAKOUT | kept | 30 | 78.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 3 | 59.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **70930 held of 157295 seen** across 21 strategies; 1585 cells past the sample floor; **659 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 29695 | 218/29477/0 | 45% | -0.14 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.13R) |
| MOVER_AVWAP_SCALP | 8745 | 39/8706/0 | 38% | -0.29 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5652 | 29/5623/0 | 40% | -0.23 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 3841 | 24/3817/0 | 51% | -0.02 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.04R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 3569 | 0/0/3569 | 43% | -0.09 | ASIA/RANGE/NORMAL/BTC_RISING (+0.31R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.05R) |
| TREND_PULLBACK_EMA | 3420 | 6/3414/0 | 45% | -0.18 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| QUIET_COMPRESSION_BREAK | 3277 | 68/3209/0 | 45% | -0.15 | NY/DISTRIBUTION/NORMAL/BTC_RISING (+0.49R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 2953 | 0/0/2953 | 37% | -0.07 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.52R) | LONDON/RANGE/NORMAL/BTC_FALLING (-0.92R) |
| SHADOW_FUNDING_FADE | 2391 | 0/0/2391 | 35% | -0.40 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-0.98R) |
| WHALE_MOMENTUM | 2028 | 2/2026/0 | 40% | -0.39 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1472 | 8/1464/0 | 39% | -0.26 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | ASIA/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (-1.06R) |
| MEAN_REVERT | 932 | 12/920/0 | 70% | +0.37 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 878 | 2/876/0 | 30% | -0.49 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 848 | 0/848/0 | 51% | -0.04 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SHADOW_CASCADE_REVERSAL | 365 | 0/0/365 | 55% | -0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.31R) |
| SR_FLIP_RETEST | 328 | 0/328/0 | 56% | -0.20 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.25R) |
| RANGE_FADE | 232 | 0/232/0 | 50% | -0.32 | LONDON/ACCUMULATION/EXPANDED/BTC_FALLING (-0.08R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 188 | 12/176/0 | 21% | -0.58 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 70 | 0/70/0 | 3% | -1.19 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.34R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.34R) |
| MA_CROSS_TREND_SHIFT | 42 | 4/38/0 | 33% | -0.23 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING` +1.44R (n=23, STRONG)
- **Weakest cells**: `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL` -1.37R (n=16, NEGATIVE); `LIQUIDATION_REVERSAL @ ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP` -1.34R (n=15, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 90 | 31% / -0.47R | 90 | 49% / -0.13R | +0.34 | **ATR** |
| TREND_PULLBACK_EMA | 298 | 49% / -0.14R | 298 | 56% / -0.03R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 244 | 43% / -0.35R | 244 | 44% / -0.25R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 661 | 46% / -0.18R | 661 | 51% / -0.09R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 435 | 44% / -0.17R | 435 | 46% / -0.09R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 63 | 44% / -0.34R | 63 | 46% / -0.26R | +0.08 | **ATR** |
| RANGE_FADE | 17 | 47% / +0.02R | 17 | 47% / -0.06R | -0.08 | **FIXED** |
| MOVER_TREND_PULLBACK | 4540 | 51% / -0.08R | 4540 | 55% / +0.00R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 58 | 48% / -0.04R | 58 | 55% / +0.01R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 306 | 52% / -0.17R | 306 | 56% / -0.13R | +0.04 | **ATR** |
| BREAKDOWN_SHORT | 19 | 32% / -0.13R | 19 | 32% / -0.10R | +0.03 | **ATR** |
| MEAN_REVERT | 88 | 61% / +0.13R | 88 | 59% / +0.14R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 533 | 45% / -0.17R | 533 | 45% / -0.18R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 411 | 53% / -0.02R | 411 | 59% / -0.01R | +0.00 | **ATR** |
| MA_CROSS_TREND_SHIFT | 14 | 36% / -0.23R | 14 | 36% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 4 | 50% / -0.03R | 4 | 50% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 20% / -0.78R | 5 | 60% / -0.04R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6812 | 32% | -0.12R | 282 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 661 | 49% | -0.08R | 157 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 40 | 57% | -0.01R | 33 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 84 | 36% / -0.24R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 504 | 38% / -0.00R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5718 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 782 | 35% / -0.02R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 335 | 38% / -0.05R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 450 | 41% / +0.10R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 387 | 37% / -0.10R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 297 | 46% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 82 | 29% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 104 | 29% / -0.65R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 71 | 56% / +0.15R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 36 | 42% / -0.00R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 15 | 40% / +0.09R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 63 | 30% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 19 | 16% / -0.71R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 8 | 38% / +0.22R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 7 | 43% / +0.14R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×778]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 20/6) (sustained 20 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.41R (bound 0.3) (streak 26/6) (sustained 26 cycles)
- **ALERT** `mean_revert_emission` — 1513 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.36R over n=920, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 26/6) (sustained 26 cycles)
- **ALERT** `tuned_variants` — 35 non-stamps — atr_arm_uncomputable=35 (seen=370 stamped=57 skipped=278) (streak 26/6) (sustained 26 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 3354524 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | no verdicts yet | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 44 arms current, none stalled; covering 485/485 signals (100%) | 0 |
| auto_dispatch | ok | placed=5 rejected=0 skipped=5 over 5 fan-out(s) to a keyed roster; top reasons: mode=5 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77522.30 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 75 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 357 dup bars, 0 undedupable; ws 0 out-of-order, 73 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +46 / upstream +18 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1235/1252 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 9 of 152 open dark rows are not being advanced (worst: DOSUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 26/120) | 26 |
| dark_sar_arms | ok | no open arms; covering 1230/1247 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 840215 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.41R (bound 0.3) (streak 26/6) | 26 |
| emission_controller | ok | last cycle 353s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×778]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 20/6) | 20 |
| entry_quality_effective | ok | 669 evaluated, 276 suppressed, 393 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +10 / upstream +139 | 0 |
| indicator_cache_key | ok | 1193 frozen value(s) avoided; 0 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1513 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.36R over n=920, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 26/6) | 26 |
| mean_revert_path | ok | output +18 / upstream +139 | 0 |
| mover_admission_metadata | ok | 892 symbols known, 188 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 11 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2948 rows held, 964322 evicted (sampled: execution:trigger_not_confirmed 400/353138, execution:overextended 400/333497, setup_compat:regime_STRONG_TREND 400/130401) | 0 |
| price_action_lane | ok | 73445 evaluated, 87 emitted; layer1 87 stamped / 0 blind; cooldown=11038, delta_opposed=7031, no_footprint=28006, no_opposing_target=70, no_sweep=20294, rr_below_floor=6919 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.32R over n=232 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +4 / upstream +139 | 0 |
| sar_alignment_crosscheck | ok | 44/2211 disagreed (2.0%) | 0 |
| sar_exit_shadow | ok | output +14 / upstream +139 | 0 |
| sar_hold_arm | ok | 812 held arms settled, 135 unscored, 41 still walking (38 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 7/72 unfetchable (10%); top cause: located bar does not contain the stamp; symbols: CLOUSDT, CYSUSDT, EGLDUSDT, FARTCOINUSDT, OPUSDT +2 more | 0 |
| sar_live_arms | ok | 41 arms current, none stalled; covering 494/494 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 11 resolved, 54 still mid-window | 0 |
| scan_cycle | ok | last 15.99s, worst 149.61s over 888 lifetime cycles; lifetime 3 over 60s, 1 over 120s; recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.91s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 36086 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 2s ago (33.5s to run, worst 64.26s), 55 overrun(s) of 673 cycles, TTL 900s; slowest trail_governor=5.81s, router_delivery=5.15s, engine_state=3.71s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +109 / upstream +139 | 0 |
| structural_snap | ok | 4525/4525 measured, 11 blind, 0 levels moved (refusals: redetect_cooldown=87) | 0 |
| structural_veto_lane | ok | 141 stamped; 0 with no readable level book, 0 with clear air ahead, 100 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +139 / upstream +18 | 0 |
| tuned_variants | violating | 35 non-stamps — atr_arm_uncomputable=35 (seen=370 stamped=57 skipped=278) (streak 26/6) | 26 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 4 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1829091`
- `Path funnel` emissions: `41`
- `Regime distribution` emissions: `41`
- `QUIET_SCALP_BLOCK` events: `108`
- `confidence_gate` events: `6701`
- `free_channel_post` events: `49`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 4993 | 4993 | 16573 | 0 |
| futures_depth | 3 | 4809 | 4809 | 8349 | 0 |
| futures_liq | 2 | 2117 | 2117 | 41491 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **49**

| Source | Count |
|---|---:|
| signal_close | 40 |
| regime_shift | 9 |

- By severity: HIGH=49

## Dependency readiness
- cvd: presence[present=272619] state[populated=272619] buckets[many=272619] sources[none] quality[none]
- funding_rate: presence[absent=31765, present=240854] state[empty=31765, populated=240854] buckets[few=240854, none=31765] sources[none] quality[none]
- liquidation_clusters: presence[absent=143929, present=128690] state[empty=143929, populated=128690] buckets[few=104736, none=143929, some=23954] sources[none] quality[none]
- oi_snapshot: presence[absent=29312, present=243307] state[empty=29312, populated=243307] buckets[many=243307, none=29312] sources[none] quality[none]
- order_book: presence[absent=89048, present=183571] state[populated=183571, unavailable=89048] buckets[few=183571, none=89048] sources[book_ticker=183571, unavailable=89048] quality[none=89048, top_of_book_only=183571]
- orderblocks: presence[absent=272619] state[empty=272619] buckets[none=272619] sources[measured_dark=272619] quality[none]
- recent_ticks: presence[present=272619] state[populated=272619] buckets[many=272619] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `14.932374119758606` sec
- Median create→first breach: `5743.230039477348` sec
- Median create→terminal: `5756.086839914322` sec
- Median first breach→terminal: `3.7237340211868286` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.8259808516754357 | 0.9997583917220012 | 0.8925205273916232 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.8029543060640965 | 3.0 | 0.9343181020213654 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.8753965326447631 | 1.0020902496003947 | 0.8735705521472208 | 0 | 1 |
| MEAN_REVERT | 3 | 3 | 0.9120371698167382 | 1.0014692041045892 | 0.8093552465233852 | 0 | 2 |
| MOVER_AVWAP_SCALP | 2 | 2 | 1.7341208800937022 | 2.002931400630384 | 0.9041593360488113 | 1 | 1 |
| MOVER_TREND_PULLBACK | 23 | 23 | 3.690423439443675 | 3.0 | 1.2301411464812249 | 18 | 5 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 1.279559561593994 | 1.5412377395566232 | 0.8995696845962652 | 0 | 3 |
| TREND_PULLBACK_EMA | 1 | 1 | 2.961998213003333 | 3.0 | 0.9873327376677777 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 1.5601 | 2957.1477031707764 | 2964.8949930667877 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.803 | 35523.72069597244 | 35533.97168493271 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 11927.108732938766 | 11931.304018974304 |
| MEAN_REVERT | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 0.4456 | 8984.023422956467 | 9002.319705963135 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.7233 | 14265.171221137047 | 14265.786119103432 |
| MOVER_TREND_PULLBACK | 23 | 23 | 0.0 | 30.4 | 0.0 | 0.0 | -0.1893 | 3534.3616919517517 | 3534.6695079803467 |
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.0 | 75.0 | 0.0 | 0.0 | -0.9993 | 11200.476289868355 | 11221.449819922447 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 3928.3606808185577 | 3929.3681139945984 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 446 | 11 | 344 | 0.0 | 0.0 | None | None | 102 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1471 | 38 | 1205 | 0.0 | 100.0 | 3928.3606808185577 | 3929.3681139945984 | 266 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `170`
- Gating Δ: `38754`
- No-generation Δ: `861328`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.8024, "current_avg_pnl": 1.5601, "current_win_rate": 66.7, "previous_avg_pnl": 0.7577, "previous_win_rate": 33.3, "win_rate_delta": 33.4}, "MEAN_REVERT": {"avg_pnl_delta": -0.1484, "current_avg_pnl": 0.4456, "current_win_rate": 33.3, "previous_avg_pnl": 0.594, "previous_win_rate": 50.0, "win_rate_delta": -16.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.4165, "current_avg_pnl": -0.1893, "current_win_rate": 0.0, "previous_avg_pnl": -0.6058, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -2.4789, "current_avg_pnl": -0.9993, "current_win_rate": 0.0, "previous_avg_pnl": 1.4796, "previous_win_rate": 55.6, "win_rate_delta": -55.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": 68, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 11, "geometry_changed_delta": 0, "geometry_preserved_delta": 154, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2274.51, "median_terminal_delta_sec": 2260.44, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **DIVERGENCE_CONTINUATION**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
