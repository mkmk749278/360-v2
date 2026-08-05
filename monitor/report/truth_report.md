# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1575` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 124 | 124 | 121 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 28373 | 28373 | 26137 | 17 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 151424 | 151426 | 16 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 135546 | 135555 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 135195 | 129415 | 6120 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 135576 | 135009 | 609 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 139063 | 138791 | 302 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 131511 | 131521 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 135623 | 135639 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 135652 | 131154 | 5907 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 155675 | 158917 | 1007 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 151442 | 142145 | 13506 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 138754 | 138766 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 135556 | 135548 | 23 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 135145 | 134388 | 803 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 137062 | 135053 | 2725 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 134818 | 134996 | 113 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 127702 | 123824 | 4032 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 127859 | 127165 | 750 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 151404 | 151404 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 131521 | 131534 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2448 | 2448 | 1246 | 7 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1447 | 1447 | 438 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 18168 | 18168 | 17921 | 7 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 14 | 14 | 5 | 4 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 16767 | 16767 | 14161 | 6 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2834 | 2834 | 448 | 52 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 44700 | 44700 | 26230 | 291 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 36 | 36 | 0 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 5070 | 5070 | 2879 | 38 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 9342 | 9342 | 8966 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 391 | 391 | 373 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4873 | 4873 | 4461 | 19 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 70 | 70 | 0 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=151426): breakout_not_found=74177, basic_filters_failed=50577, move_not_fresh=18243, breakout_stale=7026, retest_proximity_failed=1171, volume_spike_missing=201, move_exhausted=14, ema_alignment_reject=11, rsi_reject=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=135555): cls_disabled_merged_into_lsr=135555
- **EVAL::DIVERGENCE_CONTINUATION** (total=129415): cvd_divergence_failed=45665, basic_filters_failed=43283, h1_trend_not_aligned=27593, ema_alignment_reject=10993, retest_proximity_failed=1365, missing_fvg_or_orderblock=516
- **EVAL::FAILED_AUCTION_RECLAIM** (total=135009): auction_not_detected=85572, basic_filters_failed=41599, regime_blocked=4476, reclaim_hold_failed=2155, tail_too_small=1072, rsi_reject=135
- **EVAL::FUNDING_EXTREME** (total=138791): funding_not_extreme=86781, basic_filters_failed=44476, ema_alignment_reject=2791, missing_funding_rate=2467, rsi_reject=1737, momentum_reject=284, cvd_divergence_failed=221, missing_fvg_or_orderblock=34
- **EVAL::LIQUIDATION_REVERSAL** (total=131521): cascade_threshold_not_met=85422, basic_filters_failed=45058, cvd_divergence_failed=542, rsi_reject=391, missing_fvg_or_orderblock=58, volume_spike_missing=50
- **EVAL::MA_CROSS_TREND_SHIFT** (total=135639): no_ma_cross=89348, basic_filters_failed=43295, ma_cross_htf_misaligned=1941, ma_cross_cooldown=1055
- **EVAL::MEAN_REVERT** (total=131154): no_extension=109670, basic_filters_failed=21484
- **EVAL::MOVER_AVWAP_SCALP** (total=158917): no_mover_leg=63426, basic_filters_failed=50714, no_avwap_tag=34254, avwap_slope_against=6626, avwap_reclaim_no_volume=1979, no_avwap_reclaim=1747, anchor_too_recent=171
- **EVAL::MOVER_TREND_PULLBACK** (total=142145): mover_run_too_small=70163, basic_filters_failed=50640, no_reclaim=18029, no_pullback_tag=3313
- **EVAL::OPENING_RANGE_BREAKOUT** (total=138766): feature_disabled=138766
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=135548): regime_blocked=99554, breakout_not_found=22199, basic_filters_failed=9087, adx_reject=4669, ema_alignment_reject=39
- **EVAL::QUIET_COMPRESSION_BREAK** (total=134388): regime_blocked=40412, basic_filters_failed=32503, compression_not_detected=31817, breakout_not_detected=26724, volume_confirmation_failed=2423, rsi_reject=432, missing_fvg_or_orderblock=55, macd_reject=22
- **EVAL::RANGE_FADE** (total=135053): no_range_edge=113563, basic_filters_failed=21490
- **EVAL::SR_FLIP_RETEST** (total=134996): flip_close_not_confirmed=85456, basic_filters_failed=41576, regime_blocked=4460, long_break_volume_thin=1498, retest_out_of_zone=741, h1_break_not_confirmed=702, reclaim_hold_failed=201, whipsaw_flip=179, long_acceptance_not_held=97, ema_alignment_reject=54, wick_quality_failed=32
- **EVAL::STANDARD** (total=123824): momentum_reject=42882, adx_reject=30820, basic_filters_failed=17195, sweeps_not_detected=14310, macd_reject=10298, ema_alignment_reject=4520, htf_poi_unanchored=3644, rsi_reject=95, invalid_sl_geometry=54, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=127165): h1_trend_not_aligned=38331, basic_filters_failed=24694, ema_alignment_reject=22017, h1_pullback_not_confirmed=14497, no_ema_reclaim_close=7972, ema_not_tested_prev=6482, body_conviction_fail=5307, rsi_reject=4231, no_prev_high_break=1044, prev_already_above_emas=1001, prev_already_below_emas=819, no_prev_low_break=428, momentum_flat=224, ema21_not_tagged=50, momentum_reject=47, missing_fvg_or_orderblock=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=151404): breakout_not_found=81039, basic_filters_failed=50576, move_not_fresh=12249, breakout_stale=5271, retest_proximity_failed=1717, volume_spike_missing=315, move_exhausted=182, ema_alignment_reject=24, rsi_reject=20, missing_fvg_or_orderblock=11
- **EVAL::WHALE_MOMENTUM** (total=131534): momentum_reject=96351, recent_ticks_insufficient=27108, basic_filters_failed=8075

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=8): execution:overextended=8
- **DIVERGENCE_CONTINUATION** (total=1144): setup_compat:regime_VOLATILE_UNSUITABLE=1000, setup_compat:regime_BREAKOUT_EXPANSION=114, execution:overextended=30
- **FAILED_AUCTION_RECLAIM** (total=1321): setup_compat:regime_STRONG_TREND=600, execution:overextended=464, context_floor=227, setup_compat:regime_VOLATILE_UNSUITABLE=30
- **FUNDING_EXTREME_SIGNAL** (total=1320): execution:trigger_not_confirmed=1320
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=4875): execution:trigger_not_confirmed=2131, setup_compat:regime_STRONG_TREND=1444, execution:overextended=1300
- **MA_CROSS_TREND_SHIFT** (total=12): setup_compat:regime_CLEAN_RANGE=6, setup_compat:regime_DIRTY_RANGE=3, execution:overextended=3
- **MEAN_REVERT** (total=9339): setup_compat:regime_STRONG_TREND=4327, setup_compat:regime_WEAK_TREND=3872, execution:overextended=1136, entry_quality=4
- **MOVER_AVWAP_SCALP** (total=1692): execution:overextended=1102, execution:trigger_not_confirmed=381, entry_quality=209
- **MOVER_TREND_PULLBACK** (total=23469): execution:trigger_not_confirmed=11018, execution:overextended=10134, entry_quality=2317
- **QUIET_COMPRESSION_BREAK** (total=1855): context_floor=1535, execution:trigger_not_confirmed=320
- **RANGE_FADE** (total=4519): setup_compat:regime_STRONG_TREND=1645, setup_compat:regime_WEAK_TREND=1519, setup_compat:regime_VOLATILE_UNSUITABLE=747, execution:overextended=433, context_edge=129, setup_compat:regime_BREAKOUT_EXPANSION=46
- **TREND_PULLBACK_EMA** (total=4243): setup_compat:regime_CLEAN_RANGE=2981, setup_compat:regime_DIRTY_RANGE=1025, setup_compat:regime_VOLATILE_UNSUITABLE=218, entry_quality=19
- **VOLUME_SURGE_BREAKOUT** (total=35): context_floor=29, execution:overextended=6

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 290213 | 32.4% |
| QUIET | 274548 | 30.6% |
| TRENDING_UP | 157082 | 17.5% |
| TRENDING_DOWN | 119862 | 13.4% |
| VOLATILE | 54197 | 6.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **212**
- Average confidence gap to threshold: **12.07** (samples=212) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LINKUSDT=36, BTCUSDT=28, LTCUSDT=16, AVAXUSDT=13, XRPUSDT=13, TRXUSDT=12, ERAUSDT=11, UNIUSDT=9, TAOUSDT=9, ARBUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 314 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 24 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 397 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 140 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 105 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 84 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 29 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 37 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 55 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 5 |
| MEAN_REVERT | kept | min_confidence_pass | 94 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 253 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 983 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1913 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 23 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 7805 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 36 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 146 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 51 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 108 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 8 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 27 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 18 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 283 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 30 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 79.33 | 65.00 | -14.33 | 20.63 | 17.97 | 20.00 | 4.67 | 1.00 |
| DIVERGENCE_CONTINUATION | filtered | 338 | 59.22 | 63.86 | 4.64 | 21.72 | 19.78 | 17.83 | 0.78 | 12.11 |
| DIVERGENCE_CONTINUATION | kept | 397 | 69.75 | 65.00 | -4.75 | 20.84 | 19.81 | 18.11 | 2.55 | 1.67 |
| FAILED_AUCTION_RECLAIM | filtered | 141 | 52.07 | 62.62 | 10.55 | 19.23 | 19.47 | 20.00 | 1.75 | 8.66 |
| FAILED_AUCTION_RECLAIM | kept | 105 | 68.87 | 65.00 | -3.87 | 21.17 | 17.71 | 20.00 | 2.39 | 0.71 |
| FUNDING_EXTREME_SIGNAL | filtered | 84 | 55.63 | 65.00 | 9.37 | 19.50 | 16.71 | 17.13 | 3.12 | 7.37 |
| FUNDING_EXTREME_SIGNAL | kept | 29 | 74.70 | 65.00 | -9.70 | 19.16 | 13.93 | 17.00 | 4.76 | 0.41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 37 | 50.45 | 65.00 | 14.55 | 18.57 | 20.00 | 17.53 | 1.65 | 17.84 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 55 | 70.36 | 65.00 | -5.36 | 18.99 | 19.65 | 15.90 | 2.64 | -0.05 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 74.00 | 65.00 | -9.00 | 19.60 | 17.30 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 94 | 68.96 | 65.00 | -3.96 | 20.16 | 15.89 | 17.34 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 253 | 53.12 | 65.00 | 11.88 | 19.83 | 15.21 | 15.80 | 3.99 | 8.00 |
| MOVER_AVWAP_SCALP | kept | 983 | 76.73 | 65.00 | -11.73 | 20.80 | 16.71 | 15.80 | 4.28 | 0.57 |
| MOVER_TREND_PULLBACK | filtered | 1936 | 56.63 | 63.59 | 6.96 | 19.22 | 18.10 | 15.80 | 4.30 | 18.02 |
| MOVER_TREND_PULLBACK | kept | 7805 | 76.35 | 65.00 | -11.35 | 20.18 | 18.51 | 15.80 | 4.36 | 1.70 |
| POST_DISPLACEMENT_CONTINUATION | kept | 36 | 84.00 | 65.00 | -19.00 | 20.72 | 20.00 | 20.00 | 4.50 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 197 | 52.82 | 64.80 | 11.98 | 20.68 | 18.94 | 20.00 | 0.00 | 11.37 |
| QUIET_COMPRESSION_BREAK | kept | 108 | 74.21 | 65.00 | -9.21 | 21.46 | 17.99 | 20.00 | 0.00 | -0.99 |
| RANGE_FADE | kept | 1 | 65.30 | 65.00 | -0.30 | 20.20 | 14.00 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 8 | 62.50 | 65.00 | 2.50 | 21.20 | 20.00 | 18.80 | 1.00 | 4.80 |
| SR_FLIP_RETEST | kept | 1 | 74.70 | 65.00 | -9.70 | 20.60 | 20.00 | 17.00 | 2.50 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 45 | 59.90 | 65.00 | 5.10 | 19.98 | 19.68 | 18.72 | 4.51 | 19.11 |
| TREND_PULLBACK_EMA | kept | 283 | 79.70 | 65.00 | -14.70 | 21.27 | 19.89 | 17.70 | 5.09 | -0.66 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 47.94 | 65.00 | 17.06 | 20.40 | 17.29 | 20.00 | 3.38 | 7.18 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 61.40 | 65.00 | 3.60 | 21.10 | 20.00 | 20.00 | 5.00 | 6.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 79.33 | 22.33 | 16.67 | 12.00 | 13.00 | 5.00 | 6.67 | 4.67 |
| DIVERGENCE_CONTINUATION | filtered | 338 | 59.22 | 23.34 | 15.60 | 5.36 | 11.92 | 5.17 | 9.16 | 0.78 |
| DIVERGENCE_CONTINUATION | kept | 397 | 69.75 | 22.94 | 16.79 | 4.59 | 11.80 | 5.09 | 8.96 | 2.55 |
| FAILED_AUCTION_RECLAIM | filtered | 141 | 52.07 | 19.74 | 14.17 | 6.70 | 13.60 | 6.74 | 6.33 | 1.75 |
| FAILED_AUCTION_RECLAIM | kept | 105 | 68.87 | 18.60 | 14.65 | 4.09 | 13.63 | 7.83 | 8.40 | 2.39 |
| FUNDING_EXTREME_SIGNAL | filtered | 84 | 55.63 | 19.19 | 13.71 | 9.29 | 11.73 | 7.52 | 4.51 | 3.12 |
| FUNDING_EXTREME_SIGNAL | kept | 29 | 74.70 | 21.41 | 17.03 | 5.07 | 10.52 | 8.52 | 7.80 | 4.76 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 37 | 50.45 | 20.62 | 16.81 | 4.95 | 11.92 | 5.00 | 7.35 | 1.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 55 | 70.36 | 23.55 | 15.02 | 5.18 | 13.40 | 4.95 | 5.62 | 2.64 |
| MA_CROSS_TREND_SHIFT | kept | 5 | 74.00 | 18.20 | 14.00 | 13.80 | 12.60 | 7.00 | 8.40 | 0.00 |
| MEAN_REVERT | kept | 94 | 68.96 | 20.83 | 14.21 | 10.05 | 12.00 | 6.19 | 5.68 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 253 | 53.12 | 18.27 | 18.28 | 8.89 | 13.62 | 5.94 | 4.01 | 3.99 |
| MOVER_AVWAP_SCALP | kept | 983 | 76.73 | 19.02 | 18.09 | 9.21 | 12.72 | 5.69 | 8.42 | 4.28 |
| MOVER_TREND_PULLBACK | filtered | 1936 | 56.63 | 17.99 | 18.22 | 7.69 | 13.12 | 5.57 | 8.99 | 4.30 |
| MOVER_TREND_PULLBACK | kept | 7805 | 76.35 | 19.24 | 18.11 | 8.13 | 13.43 | 5.97 | 9.01 | 4.36 |
| POST_DISPLACEMENT_CONTINUATION | kept | 36 | 84.00 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 197 | 52.82 | 19.52 | 16.96 | 11.82 | 13.88 | 6.88 | 3.54 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 108 | 74.21 | 18.63 | 17.07 | 10.72 | 13.59 | 6.02 | 8.43 | 0.00 |
| RANGE_FADE | kept | 1 | 65.30 | 17.00 | 14.00 | 12.00 | 12.00 | 5.00 | 5.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 8 | 62.50 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 9.30 | 1.00 |
| SR_FLIP_RETEST | kept | 1 | 74.70 | 25.00 | 8.00 | 9.00 | 14.00 | 8.50 | 7.70 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 45 | 59.90 | 15.67 | 18.00 | 9.30 | 14.93 | 7.16 | 9.44 | 4.51 |
| TREND_PULLBACK_EMA | kept | 283 | 79.70 | 17.36 | 18.00 | 7.86 | 14.73 | 7.48 | 9.51 | 5.09 |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 47.94 | 17.80 | 15.87 | 12.00 | 12.60 | 5.00 | 3.47 | 3.38 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 61.40 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 4.00 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 79.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 338 | 59.22 | 0.00 | 0.00 | 0.88 | 0.00 | 1.28 | 0.00 | 0.00 | 0.00 | **2.16** |
| DIVERGENCE_CONTINUATION | kept | 397 | 69.75 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.01** |
| FAILED_AUCTION_RECLAIM | filtered | 141 | 52.07 | 0.00 | 0.00 | 0.00 | 0.00 | 1.70 | 0.00 | 0.00 | 0.00 | **1.70** |
| FAILED_AUCTION_RECLAIM | kept | 105 | 68.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 84 | 55.63 | 0.00 | 0.00 | 6.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.48** |
| FUNDING_EXTREME_SIGNAL | kept | 29 | 74.70 | 0.00 | 0.00 | 0.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.41** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 37 | 50.45 | 0.00 | 0.00 | 0.52 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.52** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 55 | 70.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 5 | 74.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 94 | 68.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 253 | 53.12 | 0.18 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 2.02 | **2.52** |
| MOVER_AVWAP_SCALP | kept | 983 | 76.73 | 0.08 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.12 | **0.56** |
| MOVER_TREND_PULLBACK | filtered | 1936 | 56.63 | 0.00 | 0.00 | 0.86 | 0.00 | 0.71 | 0.01 | 0.00 | 0.00 | **1.58** |
| MOVER_TREND_PULLBACK | kept | 7805 | 76.35 | 0.00 | 0.00 | 0.90 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **1.12** |
| POST_DISPLACEMENT_CONTINUATION | kept | 36 | 84.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 197 | 52.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.61 | 0.18 | 0.00 | 6.30 | **7.09** |
| QUIET_COMPRESSION_BREAK | kept | 108 | 74.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | 0.00 | 0.00 | 0.10 | **0.18** |
| RANGE_FADE | kept | 1 | 65.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 8 | 62.50 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| SR_FLIP_RETEST | kept | 1 | 74.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 45 | 59.90 | 0.00 | 0.00 | 3.41 | 0.00 | 8.64 | 0.00 | 0.00 | 0.00 | **12.05** |
| TREND_PULLBACK_EMA | kept | 283 | 79.70 | 0.00 | 0.00 | 0.06 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **0.21** |
| VOLUME_SURGE_BREAKOUT | filtered | 30 | 47.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.80 | **1.80** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 61.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |

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
- Outcomes recorded: **117801 held of 131771 seen** across 21 strategies; 2649 cells past the sample floor; **384 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 27695 | 168/27527/0 | 54% | +0.03 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| FAILED_AUCTION_RECLAIM | 16973 | 24/16949/0 | 51% | -0.00 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16538 | 1/16537/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 10882 | 4/10878/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.43R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 8517 | 0/8517/0 | 51% | -0.04 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+1.39R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 5688 | 27/5661/0 | 34% | -0.38 | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.01R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| LIQUIDITY_SWEEP_REVERSAL | 4272 | 9/4263/0 | 46% | -0.20 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 4259 | 0/0/4259 | 42% | -0.05 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.01R) |
| SHADOW_RANGE_FADE | 3878 | 0/0/3878 | 41% | +0.18 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.02R) |
| MEAN_REVERT | 3812 | 0/3812/0 | 75% | +0.49 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| TREND_PULLBACK_EMA | 3738 | 2/3736/0 | 52% | -0.19 | LONDON/QUIET/NORMAL/BTC_NEUTRAL (+0.74R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_FUNDING_FADE | 3432 | 0/0/3432 | 41% | -0.29 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.34R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (-0.90R) |
| RANGE_FADE | 2921 | 0/2921/0 | 25% | -0.56 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.34R) |
| VOLUME_SURGE_BREAKOUT | 1870 | 13/1857/0 | 40% | -0.06 | LONDON/MARKUP/COMPRESSED/BTC_NEUTRAL (+1.87R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1262 | 2/1260/0 | 33% | -0.35 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.07R) | OVERLAP/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.29R) |
| WHALE_MOMENTUM | 1226 | 0/1226/0 | 47% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 384 | 0/0/384 | 45% | -0.21 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.00R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.81R) |
| BREAKDOWN_SHORT | 305 | 7/298/0 | 58% | +0.32 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| LIQUIDATION_REVERSAL | 66 | 0/66/0 | 64% | -0.48 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| MA_CROSS_TREND_SHIFT | 16 | 1/15/0 | 31% | -0.48 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +1.87R (n=41, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 48 | 38% / -0.32R | 48 | 52% / -0.11R | +0.21 | **ATR** |
| TREND_PULLBACK_EMA | 114 | 45% / -0.26R | 114 | 49% / -0.11R | +0.15 | **ATR** |
| SR_FLIP_RETEST | 2759 | 46% / -0.20R | 2759 | 49% / -0.10R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 332 | 40% / -0.21R | 332 | 43% / -0.12R | +0.10 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 62 | 44% / +0.01R | 62 | 48% / -0.06R | -0.08 | **FIXED** |
| DIVERGENCE_CONTINUATION | 736 | 47% / -0.11R | 736 | 52% / -0.05R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 619 | 50% / -0.18R | 619 | 54% / -0.12R | +0.06 | **ATR** |
| RANGE_FADE | 196 | 14% / -0.76R | 196 | 17% / -0.71R | +0.05 | **ATR** |
| MEAN_REVERT | 343 | 55% / +0.04R | 343 | 51% / +0.09R | +0.05 | **ATR** |
| MOVER_TREND_PULLBACK | 3272 | 53% / -0.03R | 3272 | 55% / +0.00R | +0.03 | **ATR** |
| WHALE_MOMENTUM | 87 | 49% / -0.25R | 87 | 48% / -0.28R | -0.03 | **FIXED** |
| BREAKDOWN_SHORT | 16 | 25% / -0.32R | 16 | 25% / -0.30R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1237 | 46% / -0.12R | 1237 | 46% / -0.14R | -0.01 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2234 | 47% / -0.10R | 2234 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 8 | 38% / -0.27R | 8 | 38% / -0.23R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 40% / -0.81R | 5 | 40% / -0.40R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4002 | 31% | -0.13R | 269 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 322 | 42% | -0.12R | 107 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 20 | 60% | +0.07R | 15 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1211 | 28% / -1.71R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 9 | 11% / -0.97R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 2761 | 37% / -0.38R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 931 | 33% / -0.59R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 47 | 19% / -1.06R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 534 | 30% / -2.04R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 621 | 35% / -0.08R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 249 | 41% / -1.45R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 53 | 25% / -2.13R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 108 | 28% / -1.12R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 253 | 31% / -0.18R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 9 | 22% / -0.45R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 77 | 40% / -0.25R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 35 | 49% / +0.02R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 5 | 20% / -1.42R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 19 | 42% / -0.37R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 37 · alerting: **6** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 44/89 unfetchable (49%); top cause: gap or duplicate bar in the 15m window; symbols: 1000RATSUSDT, 1000SHIBUSDT, AVAXUSDT, BLESSUSDT, BTWUSDT +13 more (streak 27/6) (sustained 27 cycles)
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 5 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 186/6) (sustained 186 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 103x (gate reads 0x, withheld 0x — refusal dark); last ETHFIUSDT age=20773.2s (streak 127/6) (sustained 127 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.39R (bound 0.3) (streak 186/6) (sustained 186 cycles)
- **ALERT** `tuned_variants` — 125 non-stamps — atr_arm_uncomputable=125 (seen=5504 stamped=452 skipped=4927) (streak 124/6) (sustained 124 cycles)
- **ALERT** `auto_dispatch` — 14 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=14) (streak 117/3) (sustained 117 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 14 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=14) (streak 117/3) | 117 |
| btc_reference | ok | BTC ref 64110.60 | 0 |
| candle_coverage | ok | 93/104 symbols with ≥20 15m candles, 83/104 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 3617 dup bars, 0 undedupable; ws 140 out-of-order, 338 in-place; SAR refused 2 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 5 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 186/6) | 186 |
| context_emission_policy | ok | output +124 / upstream +46 | 0 |
| dark_resolution | ok | 3 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.39R (bound 0.3) (streak 186/6) | 186 |
| emission_controller | ok | last cycle 1622s ago; live_overrides=24 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=13 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4000 stamps (MEAN_REVERT=1067, MOVER_AVWAP_SCALP=363, MOVER_TREND_PULLBACK=1598, RANGE_FADE=758, TREND_PULLBACK_EMA=214), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 8830 evaluated, 2216 suppressed, 2566 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +4 / upstream +429 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 556 detections since last emission (emitted_total=4) — and the POST-SCORING blocked candidates measure +0.49R over n=3812, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 4/6) | 4 |
| mean_revert_path | ok | output +209 / upstream +429 | 0 |
| mover_admission_metadata | ok | 852 symbols known, 151 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 101312 evicted (sampled: execution:trigger_not_confirmed 400/36187, execution:overextended 400/29553, setup_compat:regime_STRONG_TREND 400/16218) | 0 |
| promoted_pair_integrity | ok | 9/9 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.56R over n=2921 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +93 / upstream +429 | 0 |
| sar_alignment_crosscheck | ok | 323/12289 disagreed (2.6%) | 0 |
| sar_exit_shadow | ok | output +6 / upstream +429 | 0 |
| sar_ledger_candles | violating | 44/89 unfetchable (49%); top cause: gap or duplicate bar in the 15m window; symbols: 1000RATSUSDT, 1000SHIBUSDT, AVAXUSDT, BLESSUSDT, BTWUSDT +13 more (streak 27/6) | 27 |
| sar_live_arms | ok | 6 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 4 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 489 records await one (45 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| setup_tf_resolver | ok | 195005 resolutions, 95945 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 103x (gate reads 0x, withheld 0x — refusal dark); last ETHFIUSDT age=20773.2s (streak 127/6) | 127 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +110 / upstream +429 | 0 |
| structural_snap | ok | 2216/2216 measured, 1 blind, 0 levels moved (refusals: none) | 0 |
| suppression_audit | ok | output +429 / upstream +46 | 0 |
| tuned_variants | violating | 125 non-stamps — atr_arm_uncomputable=125 (seen=5504 stamped=452 skipped=4927) (streak 124/6) | 124 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4027259`
- `Path funnel` emissions: `112`
- `Regime distribution` emissions: `112`
- `QUIET_SCALP_BLOCK` events: `212`
- `confidence_gate` events: `12975`
- `free_channel_post` events: `23`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **18**
- Total REST-fallback activations: **7**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 11 | 2624 | 23020 | 157618 | 0 |
| futures_liq | 3 | 3845 | 3845 | 3896 | 0 |
| futures_mover | 4 | 3200 | 8453 | 24834 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 7 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **23**

| Source | Count |
|---|---:|
| signal_close | 14 |
| regime_shift | 9 |

- By severity: HIGH=23

## Dependency readiness
- cvd: presence[present=653642] state[populated=653642] buckets[many=653642] sources[none] quality[none]
- funding_rate: presence[absent=47434, present=606208] state[empty=47434, populated=606208] buckets[few=606208, none=47434] sources[none] quality[none]
- liquidation_clusters: presence[absent=379946, present=273696] state[empty=379946, populated=273696] buckets[few=215340, none=379946, some=58356] sources[none] quality[none]
- oi_snapshot: presence[absent=45760, present=607882] state[empty=45760, populated=607882] buckets[few=226, many=606416, none=45760, some=1240] sources[none] quality[none]
- order_book: presence[absent=178329, present=475313] state[populated=475313, unavailable=178329] buckets[few=475313, none=178329] sources[book_ticker=475313, unavailable=178329] quality[none=178329, top_of_book_only=475313]
- orderblocks: presence[absent=653642] state[empty=653642] buckets[none=653642] sources[not_implemented=653642] quality[none]
- recent_ticks: presence[absent=10587, present=643055] state[empty=10587, populated=643055] buckets[many=643055, none=10587] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.47647750377655` sec
- Median create→first breach: `6072.496596455574` sec
- Median create→terminal: `6080.405788421631` sec
- Median first breach→terminal: `2.9731080532073975` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 14.3}, "under_180s": {"count": 2, "pct": 14.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 7.1}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 1.770405935096947 | 1.1401440580095643 | 1.5527914412742532 | 1 | 0 |
| MOVER_TREND_PULLBACK | 13 | 12 | 3.9752770960486394 | 3.0 | 1.3250923653495463 | 12 | 0 |

- **1 of 14 closed records carry no shipped-stop stamp** (written before 2026-08-04, or in flight across the deploy). They are excluded above. This shrinks on its own; it is not a fault.

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.1401 | 14145.912573814392 | 14147.315888881683 |
| MOVER_TREND_PULLBACK | 13 | 13 | 0.0 | 30.8 | 0.0 | 0.0 | -0.0564 | 5300.989166021347 | 5304.6125228405 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 391 | 1 | 373 | 0.0 | 0.0 | None | None | 18 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4873 | 19 | 4461 | 0.0 | 0.0 | None | None | 412 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-168`
- Gating Δ: `-20528`
- No-generation Δ: `9852`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.8145, "current_avg_pnl": -0.0564, "current_win_rate": 0.0, "previous_avg_pnl": 0.7581, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -56, "geometry_changed_delta": 0, "geometry_preserved_delta": -7682, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -83, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDATION_REVERSAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
