# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `3827` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 72 | 72 | 71 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 22410 | 22410 | 18705 | 60 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 146897 | 146916 | 4 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 127095 | 127114 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 126648 | 120974 | 6111 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 127148 | 121454 | 5962 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 130716 | 130240 | 527 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 118634 | 118639 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 127424 | 127474 | 10 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 127485 | 123472 | 5215 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 151189 | 156061 | 1503 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 146923 | 134832 | 16327 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 127141 | 127154 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 127118 | 127103 | 42 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 126597 | 126106 | 541 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 128694 | 126546 | 2819 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 122980 | 122639 | 3894 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 114232 | 109667 | 4958 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 114633 | 113813 | 884 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 146854 | 146813 | 79 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 118642 | 118653 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 23209 | 23209 | 18751 | 48 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2098 | 2098 | 1830 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 29369 | 29369 | 28652 | 36 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 14 | 14 | 11 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 13002 | 13002 | 12005 | 4 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3632 | 3632 | 2334 | 21 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 40428 | 40428 | 25412 | 349 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 67 | 67 | 65 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2621 | 2621 | 689 | 14 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 6838 | 6838 | 6715 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 14470 | 14470 | 2873 | 192 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3792 | 3792 | 3541 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 333 | 333 | 98 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=146916): breakout_not_found=80616, basic_filters_failed=41810, move_not_fresh=15735, breakout_stale=6004, retest_proximity_failed=2227, volume_spike_missing=343, insufficient_candles=67, move_exhausted=50, ema_alignment_reject=44, rsi_reject=19, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=127114): cls_disabled_merged_into_lsr=127114
- **EVAL::DIVERGENCE_CONTINUATION** (total=120974): cvd_divergence_failed=41056, basic_filters_failed=35057, h1_trend_not_aligned=27383, ema_alignment_reject=13103, retest_proximity_failed=2474, missing_fvg_or_orderblock=1901
- **EVAL::FAILED_AUCTION_RECLAIM** (total=121454): auction_not_detected=44089, basic_filters_failed=34089, reclaim_hold_failed=23379, tail_too_small=16026, regime_blocked=3839, rsi_reject=32
- **EVAL::FUNDING_EXTREME** (total=130240): funding_not_extreme=81817, basic_filters_failed=32248, missing_funding_rate=9129, ema_alignment_reject=4313, rsi_reject=1605, cvd_divergence_failed=564, momentum_reject=483, missing_fvg_or_orderblock=68, insufficient_candles=13
- **EVAL::LIQUIDATION_REVERSAL** (total=118639): cascade_threshold_not_met=81677, basic_filters_failed=35512, rsi_reject=657, cvd_divergence_failed=649, insufficient_candles=67, missing_fvg_or_orderblock=57, volume_spike_missing=20
- **EVAL::MA_CROSS_TREND_SHIFT** (total=127474): no_ma_cross=90667, basic_filters_failed=35083, ma_cross_cooldown=944, ma_cross_htf_misaligned=780
- **EVAL::MEAN_REVERT** (total=123472): no_extension=104780, basic_filters_failed=18692
- **EVAL::MOVER_AVWAP_SCALP** (total=156061): no_avwap_tag=52687, no_mover_leg=46203, basic_filters_failed=41972, avwap_slope_against=9240, avwap_reclaim_no_volume=3420, no_avwap_reclaim=2296, anchor_too_recent=176, insufficient_candles=67
- **EVAL::MOVER_TREND_PULLBACK** (total=134832): mover_run_too_small=62071, basic_filters_failed=41898, no_reclaim=26464, no_pullback_tag=4332, insufficient_candles=67
- **EVAL::OPENING_RANGE_BREAKOUT** (total=127154): feature_disabled=127154
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=127103): regime_blocked=67565, breakout_not_found=42578, basic_filters_failed=12307, adx_reject=4583, ema_alignment_reject=70
- **EVAL::QUIET_COMPRESSION_BREAK** (total=126106): regime_blocked=63215, compression_not_detected=30442, basic_filters_failed=21772, breakout_not_detected=9898, volume_confirmation_failed=732, rsi_reject=39, missing_fvg_or_orderblock=8
- **EVAL::RANGE_FADE** (total=126546): no_range_edge=107850, basic_filters_failed=18696
- **EVAL::SR_FLIP_RETEST** (total=122639): basic_filters_failed=34063, flip_close_not_confirmed=22658, long_break_volume_thin=15968, whipsaw_flip=15327, retest_out_of_zone=11058, reclaim_hold_failed=9476, long_disabled=7421, regime_blocked=3823, wick_quality_failed=1660, long_acceptance_not_held=578, missing_fvg_or_orderblock=299, ema_alignment_reject=297, rsi_reject=11
- **EVAL::STANDARD** (total=109667): momentum_reject=42153, adx_reject=22896, basic_filters_failed=15354, sweeps_not_detected=12584, ema_alignment_reject=8569, macd_reject=7776, rsi_reject=258, invalid_sl_geometry=76, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=113813): h1_trend_not_aligned=31471, basic_filters_failed=20663, h1_pullback_not_confirmed=19096, ema_alignment_reject=17523, ema_not_tested_prev=9026, no_ema_reclaim_close=7573, body_conviction_fail=3107, rsi_reject=3051, prev_already_below_emas=738, no_prev_low_break=645, prev_already_above_emas=267, momentum_flat=235, no_prev_high_break=211, ema21_not_tagged=142, momentum_reject=37, missing_fvg_or_orderblock=28
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=146813): breakout_not_found=80324, basic_filters_failed=41810, move_not_fresh=15687, breakout_stale=5689, retest_proximity_failed=2825, volume_spike_missing=313, insufficient_candles=67, ema_alignment_reject=40, move_exhausted=38, missing_fvg_or_orderblock=20
- **EVAL::WHALE_MOMENTUM** (total=118653): momentum_reject=91535, recent_ticks_insufficient=18668, basic_filters_failed=8450

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=17): execution:overextended=17
- **DIVERGENCE_CONTINUATION** (total=776): setup_compat:regime_VOLATILE_UNSUITABLE=717, execution:overextended=39, setup_compat:regime_BREAKOUT_EXPANSION=20
- **FAILED_AUCTION_RECLAIM** (total=7943): setup_compat:regime_STRONG_TREND=5101, execution:overextended=1407, context_floor=1407, setup_compat:regime_VOLATILE_UNSUITABLE=28
- **FUNDING_EXTREME_SIGNAL** (total=1718): execution:trigger_not_confirmed=1718
- **LIQUIDATION_REVERSAL** (total=2): execution:trigger_not_confirmed=2
- **LIQUIDITY_SWEEP_REVERSAL** (total=7677): setup_compat:regime_STRONG_TREND=3288, execution:trigger_not_confirmed=2253, execution:overextended=2136
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_CLEAN_RANGE=4, execution:trigger_not_confirmed=2, setup_compat:regime_DIRTY_RANGE=2
- **MEAN_REVERT** (total=9545): setup_compat:regime_STRONG_TREND=4878, setup_compat:regime_WEAK_TREND=4352, execution:overextended=315
- **MOVER_AVWAP_SCALP** (total=2567): execution:overextended=1841, execution:trigger_not_confirmed=418, context_floor=308
- **MOVER_TREND_PULLBACK** (total=24684): execution:overextended=13763, execution:trigger_not_confirmed=10921
- **QUIET_COMPRESSION_BREAK** (total=1309): context_floor=1292, execution:overextended=16, execution:trigger_not_confirmed=1
- **RANGE_FADE** (total=4556): setup_compat:regime_STRONG_TREND=2185, setup_compat:regime_WEAK_TREND=1191, setup_compat:regime_VOLATILE_UNSUITABLE=1100, setup_compat:regime_BREAKOUT_EXPANSION=56, execution:overextended=16, context_edge=8
- **TREND_PULLBACK_EMA** (total=3147): setup_compat:regime_CLEAN_RANGE=2563, setup_compat:regime_DIRTY_RANGE=431, setup_compat:regime_VOLATILE_UNSUITABLE=153
- **VOLUME_SURGE_BREAKOUT** (total=41): execution:overextended=25, context_floor=16

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 221352 | 28.6% |
| TRENDING_DOWN | 181047 | 23.4% |
| TRENDING_UP | 168654 | 21.8% |
| QUIET | 161066 | 20.8% |
| VOLATILE | 43191 | 5.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **363**
- Average confidence gap to threshold: **10.04** (samples=363) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SOLUSDT=55, TRXUSDT=49, BCHUSDT=21, DOTUSDT=20, XLMUSDT=20, XRPUSDT=18, BTCUSDT=17, BNBUSDT=16, AAVEUSDT=13, LINKUSDT=13

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 360 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 13 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1404 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 145 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 132 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 379 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 9 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 11 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 359 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 2 |
| MEAN_REVERT | filtered | min_confidence | 10 |
| MEAN_REVERT | kept | min_confidence_pass | 48 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 282 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 469 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1001 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 8289 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 92 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 69 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 348 |
| SR_FLIP_RETEST | filtered | min_confidence | 1842 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 103 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3932 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 209 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 155 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 68.80 | 65.00 | -3.80 | 17.90 | 15.70 | 20.00 | 3.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 373 | 57.81 | 64.16 | 6.35 | 19.83 | 19.83 | 18.00 | 0.99 | 11.12 |
| DIVERGENCE_CONTINUATION | kept | 1404 | 70.96 | 65.00 | -5.96 | 19.70 | 19.94 | 18.01 | 1.76 | 0.48 |
| FAILED_AUCTION_RECLAIM | filtered | 277 | 58.21 | 63.48 | 5.27 | 20.12 | 19.22 | 20.00 | 3.86 | 4.47 |
| FAILED_AUCTION_RECLAIM | kept | 379 | 70.56 | 65.00 | -5.56 | 21.10 | 19.45 | 20.00 | 4.47 | 0.47 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 58.47 | 65.00 | 6.53 | 21.13 | 19.80 | 17.00 | 0.67 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 16 | 53.64 | 61.56 | 7.92 | 20.60 | 19.80 | 19.06 | 0.00 | 15.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 359 | 68.57 | 65.00 | -3.57 | 21.16 | 19.55 | 17.76 | 2.20 | -0.04 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.50 | 65.00 | -1.50 | 21.20 | 15.80 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 10 | 55.89 | 61.50 | 5.61 | 19.97 | 14.09 | 16.36 | 0.00 | 15.44 |
| MEAN_REVERT | kept | 48 | 76.92 | 65.00 | -11.92 | 18.86 | 17.46 | 19.08 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 282 | 51.92 | 64.72 | 12.80 | 21.04 | 18.36 | 15.80 | 3.80 | 4.03 |
| MOVER_AVWAP_SCALP | kept | 469 | 79.26 | 65.00 | -14.26 | 20.13 | 18.95 | 15.80 | 4.71 | 0.17 |
| MOVER_TREND_PULLBACK | filtered | 1006 | 55.52 | 63.34 | 7.82 | 20.27 | 18.31 | 15.80 | 3.93 | 19.54 |
| MOVER_TREND_PULLBACK | kept | 8289 | 76.77 | 65.00 | -11.77 | 19.84 | 18.31 | 15.80 | 4.41 | 1.02 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 79.85 | 65.00 | -14.85 | 20.75 | 20.00 | 19.80 | 4.50 | 5.40 |
| QUIET_COMPRESSION_BREAK | filtered | 161 | 52.23 | 64.35 | 12.12 | 21.47 | 19.36 | 20.00 | 0.00 | 6.92 |
| QUIET_COMPRESSION_BREAK | kept | 348 | 77.70 | 65.00 | -12.70 | 21.65 | 19.74 | 20.00 | 0.00 | -0.69 |
| SR_FLIP_RETEST | filtered | 1945 | 58.48 | 64.63 | 6.15 | 20.02 | 19.87 | 15.83 | 1.21 | 9.32 |
| SR_FLIP_RETEST | kept | 3932 | 71.30 | 65.00 | -6.30 | 20.73 | 19.92 | 16.01 | 1.92 | 0.28 |
| TREND_PULLBACK_EMA | kept | 209 | 80.53 | 65.00 | -15.53 | 20.36 | 19.82 | 17.15 | 5.54 | -0.76 |
| VOLUME_SURGE_BREAKOUT | filtered | 155 | 54.29 | 63.87 | 9.58 | 19.78 | 18.19 | 19.18 | 4.35 | 5.98 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 70.20 | 65.00 | -5.20 | 20.10 | 18.20 | 20.00 | 4.50 | 4.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 68.80 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 5.30 | 3.50 |
| DIVERGENCE_CONTINUATION | filtered | 373 | 57.81 | 22.21 | 15.40 | 4.36 | 11.76 | 5.26 | 8.94 | 0.99 |
| DIVERGENCE_CONTINUATION | kept | 1404 | 70.96 | 23.23 | 17.46 | 4.34 | 11.34 | 5.48 | 8.94 | 1.76 |
| FAILED_AUCTION_RECLAIM | filtered | 277 | 58.21 | 20.91 | 15.76 | 4.16 | 11.88 | 6.91 | 6.67 | 3.86 |
| FAILED_AUCTION_RECLAIM | kept | 379 | 70.56 | 22.88 | 14.54 | 5.15 | 11.77 | 5.88 | 6.36 | 4.47 |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 58.47 | 25.00 | 18.00 | 3.00 | 17.00 | 8.50 | 1.30 | 0.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 16 | 53.64 | 19.50 | 14.00 | 7.88 | 14.38 | 5.00 | 7.89 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 359 | 68.57 | 23.87 | 14.12 | 4.18 | 12.18 | 6.02 | 6.03 | 2.20 |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.50 | 17.00 | 14.00 | 4.50 | 12.50 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 10 | 55.89 | 25.00 | 16.80 | 3.00 | 12.00 | 8.25 | 6.28 | 0.00 |
| MEAN_REVERT | kept | 48 | 76.92 | 17.50 | 18.00 | 11.56 | 13.83 | 8.47 | 7.55 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 282 | 51.92 | 17.97 | 18.06 | 8.01 | 12.33 | 5.04 | 4.48 | 3.80 |
| MOVER_AVWAP_SCALP | kept | 469 | 79.26 | 19.73 | 18.02 | 9.06 | 13.64 | 5.43 | 8.96 | 4.71 |
| MOVER_TREND_PULLBACK | filtered | 1006 | 55.52 | 17.87 | 18.31 | 7.67 | 13.06 | 5.96 | 8.82 | 3.93 |
| MOVER_TREND_PULLBACK | kept | 8289 | 76.77 | 19.34 | 18.03 | 8.15 | 13.22 | 5.74 | 9.14 | 4.41 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 79.85 | 17.00 | 18.00 | 15.00 | 14.00 | 6.75 | 10.00 | 4.50 |
| QUIET_COMPRESSION_BREAK | filtered | 161 | 52.23 | 20.48 | 16.29 | 11.96 | 14.06 | 7.02 | 4.32 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 348 | 77.70 | 17.94 | 17.97 | 11.42 | 14.04 | 8.42 | 8.49 | 0.00 |
| SR_FLIP_RETEST | filtered | 1945 | 58.48 | 17.59 | 17.47 | 4.04 | 12.00 | 6.15 | 9.36 | 1.21 |
| SR_FLIP_RETEST | kept | 3932 | 71.30 | 21.34 | 16.87 | 4.77 | 12.69 | 5.78 | 9.35 | 1.92 |
| TREND_PULLBACK_EMA | kept | 209 | 80.53 | 19.83 | 18.00 | 7.50 | 14.00 | 6.48 | 9.77 | 5.54 |
| VOLUME_SURGE_BREAKOUT | filtered | 155 | 54.29 | 20.51 | 15.16 | 12.00 | 13.08 | 4.60 | 5.00 | 4.35 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 70.20 | 21.00 | 16.00 | 13.50 | 15.50 | 5.00 | 6.20 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 68.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 373 | 57.81 | 0.08 | 0.00 | 1.03 | 0.00 | 1.36 | 0.00 | 0.00 | 0.00 | **2.47** |
| DIVERGENCE_CONTINUATION | kept | 1404 | 70.96 | 0.00 | 0.00 | 0.58 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.59** |
| FAILED_AUCTION_RECLAIM | filtered | 277 | 58.21 | 0.00 | 0.00 | 1.26 | 0.00 | 1.01 | 0.06 | 0.00 | 0.00 | **2.33** |
| FAILED_AUCTION_RECLAIM | kept | 379 | 70.56 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| FUNDING_EXTREME_SIGNAL | filtered | 9 | 58.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 16 | 53.64 | 0.00 | 0.00 | 0.00 | 0.00 | 15.00 | 0.00 | 0.00 | 0.00 | **15.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 359 | 68.57 | 0.00 | 0.00 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.03** |
| MA_CROSS_TREND_SHIFT | kept | 2 | 66.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 10 | 55.89 | 0.00 | 0.00 | 1.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.44** |
| MEAN_REVERT | kept | 48 | 76.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 282 | 51.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.26 | **1.26** |
| MOVER_AVWAP_SCALP | kept | 469 | 79.26 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.02 | **0.03** |
| MOVER_TREND_PULLBACK | filtered | 1006 | 55.52 | 1.73 | 0.00 | 1.88 | 0.00 | 0.42 | 0.01 | 0.00 | 0.00 | **4.04** |
| MOVER_TREND_PULLBACK | kept | 8289 | 76.77 | 0.07 | 0.00 | 0.58 | 0.00 | 0.21 | 0.01 | 0.00 | 0.00 | **0.87** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 79.85 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| QUIET_COMPRESSION_BREAK | filtered | 161 | 52.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0.11 | 0.00 | 5.93 | **6.39** |
| QUIET_COMPRESSION_BREAK | kept | 348 | 77.70 | 0.00 | 0.00 | 0.00 | 0.00 | 1.71 | 0.00 | 0.00 | 0.03 | **1.74** |
| SR_FLIP_RETEST | filtered | 1945 | 58.48 | 0.09 | 0.00 | 0.66 | 0.00 | 0.78 | 0.08 | 0.00 | 0.02 | **1.63** |
| SR_FLIP_RETEST | kept | 3932 | 71.30 | 0.00 | 0.00 | 0.16 | 0.00 | 0.01 | 0.01 | 0.00 | 0.00 | **0.18** |
| TREND_PULLBACK_EMA | kept | 209 | 80.53 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.80** |
| VOLUME_SURGE_BREAKOUT | filtered | 155 | 54.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.74 | **1.74** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 70.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=913 (19.1%) | WOULD_LOSE=1691 | WOULD_EXPIRE=2174 | pending (awaiting window)=222

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:FAILED_AUCTION_RECLAIM | 310 | 20.3% | 142.6 | 121.0 | +0.07 | **TUNE** |
| context_floor:MOVER_AVWAP_SCALP | 126 | 58.7% | 7.8 | 74.3 | -0.53 | **DROP** |
| context_floor:QUIET_COMPRESSION_BREAK | 805 | 0.0% | 332.7 | 0.0 | +0.41 | **KEEP** |
| dispatch_cooldown | 19 | 15.8% | 16.8 | 2.3 | +0.76 | **INSUFFICIENT_SAMPLE** |
| dispatch_staleness_v2 | 224 | 44.6% | 68.8 | 89.5 | -0.09 | **TUNE** |
| level_still_in_play | 1281 | 8.4% | 446.9 | 81.5 | +0.29 | **KEEP** |
| min_confidence | 1743 | 27.0% | 1138.2 | 545.8 | +0.34 | **KEEP** |
| quiet_scalp_block | 78 | 6.4% | 19.9 | 6.4 | +0.17 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 4 | 25.0% | 0.2 | 0.3 | -0.04 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 28 | 39.3% | 17.7 | 7.7 | +0.36 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 82 | 50.0% | 34.1 | 60.9 | -0.33 | **DROP** |
| shadow_unit:SHADOW_RANGE_FADE | 78 | 47.4% | 25.8 | 71.3 | -0.58 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 86870 across 20 strategies; 1967 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 20155 | 101/20054/0 | 59% | +0.11 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.27R) |
| FAILED_AUCTION_RECLAIM | 14461 | 27/14434/0 | 55% | +0.07 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 13846 | 2/13844/0 | 43% | -0.25 | OVERLAP/MARKDOWN/EXPANDED/BTC_RISING (+1.11R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.30R) |
| DIVERGENCE_CONTINUATION | 8466 | 7/8459/0 | 47% | -0.05 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (+1.61R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 5954 | 0/5954/0 | 45% | -0.10 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 3414 | 0/0/3414 | 40% | -0.01 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.04R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.03R) |
| LIQUIDITY_SWEEP_REVERSAL | 3243 | 9/3234/0 | 46% | -0.11 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.50R) |
| SHADOW_RANGE_FADE | 3219 | 0/0/3219 | 42% | +0.25 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.40R) | ASIA/QUIET/NORMAL/BTC_FALLING (-0.96R) |
| MEAN_REVERT | 3085 | 0/3085/0 | 80% | +0.58 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.14R) |
| SHADOW_FUNDING_FADE | 2527 | 0/0/2527 | 42% | -0.26 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.31R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-0.94R) |
| RANGE_FADE | 1985 | 0/1985/0 | 3% | -1.01 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.34R) |
| MOVER_AVWAP_SCALP | 1823 | 29/1794/0 | 39% | -0.28 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/MARKUP/CASCADE/BTC_NEUTRAL (-1.13R) |
| TREND_PULLBACK_EMA | 1591 | 2/1589/0 | 52% | -0.15 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.12R) |
| VOLUME_SURGE_BREAKOUT | 1588 | 12/1576/0 | 38% | -0.13 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.19R) |
| WHALE_MOMENTUM | 474 | 0/474/0 | 54% | -0.11 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 402 | 2/400/0 | 36% | -0.12 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.05R) |
| BREAKDOWN_SHORT | 299 | 7/292/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 265 | 0/0/265 | 46% | -0.24 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.01R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 6 | 1/5/0 | 50% | -0.24 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.50R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 43 | 49% / -0.22R | 43 | 53% / -0.03R | +0.18 | **ATR** |
| MEAN_REVERT | 257 | 60% / +0.16R | 257 | 56% / +0.27R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 31 | 42% / -0.16R | 31 | 39% / -0.26R | -0.10 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 444 | 50% / -0.15R | 444 | 55% / -0.06R | +0.09 | **ATR** |
| SR_FLIP_RETEST | 2137 | 46% / -0.18R | 2137 | 49% / -0.09R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 493 | 46% / -0.11R | 493 | 52% / -0.04R | +0.07 | **ATR** |
| MOVER_AVWAP_SCALP | 144 | 42% / -0.14R | 144 | 45% / -0.07R | +0.07 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 47 | 40% / -0.04R | 47 | 43% / -0.11R | -0.07 | **FIXED** |
| RANGE_FADE | 153 | 5% / -1.00R | 153 | 7% / -0.95R | +0.05 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1787 | 48% / -0.08R | 1787 | 47% / -0.06R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 868 | 45% / -0.10R | 868 | 44% / -0.12R | -0.02 | **FIXED** |
| MOVER_TREND_PULLBACK | 2262 | 56% / +0.03R | 2262 | 59% / +0.04R | +0.01 | **ATR** |
| BREAKDOWN_SHORT | 11 | 27% / -0.26R | 11 | 27% / -0.27R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 7 | 14% / -0.71R | 7 | 43% / -0.21R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 4 | 75% / +0.10R | 4 | 75% / -0.13R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 1841 | 31% | -0.11R | 172 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 134 | 43% | -0.09R | 62 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 12 | 42% | -0.04R | 11 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 525 | 29% / -3.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 2 | 0% / -2.41R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 854 | 40% / -0.73R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 423 | 37% / -0.98R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 15 | 13% / -4.31R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 205 | 25% / -4.98R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 153 | 45% / +0.47R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 91 | 38% / -3.47R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 9 | 11% / -9.42R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 24 | 29% / -3.23R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 34 | 29% / -0.17R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 3 | 0% / -0.88R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 6 | 33% / -0.33R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 5 | 20% / -0.61R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 1 | 0% / -2.10R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._

| Setup | Gate | n | WOULD_WIN% | EV/suppression (R) | Verdict |
|---|---|---:|---:|---:|---|
| FAILED_AUCTION_RECLAIM | min_confidence | 45 | 93.3% | -1.75 | **DROP** |
| MEAN_REVERT | min_confidence | 3 | 100.0% | -1.55 | **INSUFFICIENT_SAMPLE** |
| LIQUIDITY_SWEEP_REVERSAL | level_still_in_play | 19 | 89.5% | -1.20 | **INSUFFICIENT_SAMPLE** |
| MOVER_TREND_PULLBACK | dispatch_staleness_v2 | 92 | 68.5% | -0.69 | **DROP** |
| SHADOW_RANGE_FADE | shadow_unit:SHADOW_RANGE_FADE | 78 | 47.4% | -0.58 | **DROP** |
| MOVER_AVWAP_SCALP | context_floor:MOVER_AVWAP_SCALP | 126 | 58.7% | -0.53 | **DROP** |
| SR_FLIP_RETEST | dispatch_staleness_v2 | 55 | 58.2% | -0.37 | **DROP** |
| SHADOW_MEAN_REVERT | shadow_unit:SHADOW_MEAN_REVERT | 82 | 50.0% | -0.33 | **DROP** |
| SR_FLIP_RETEST | quiet_scalp_block | 14 | 35.7% | -0.27 | **INSUFFICIENT_SAMPLE** |
| SHADOW_CASCADE_REVERSAL | shadow_unit:SHADOW_CASCADE_REVERSAL | 4 | 25.0% | -0.04 | **INSUFFICIENT_SAMPLE** |
| DIVERGENCE_CONTINUATION | dispatch_staleness_v2 | 17 | 5.9% | +0.04 | **INSUFFICIENT_SAMPLE** |
| MOVER_AVWAP_SCALP | level_still_in_play | 53 | 0.0% | +0.06 | **TUNE** |
| FAILED_AUCTION_RECLAIM | context_floor:FAILED_AUCTION_RECLAIM | 310 | 20.3% | +0.07 | **TUNE** |
| QUIET_COMPRESSION_BREAK | min_confidence | 48 | 0.0% | +0.11 | **KEEP** |
| FAILED_AUCTION_RECLAIM | level_still_in_play | 21 | 0.0% | +0.15 | **KEEP** |
| QUIET_COMPRESSION_BREAK | level_still_in_play | 124 | 0.0% | +0.18 | **KEEP** |
| DIVERGENCE_CONTINUATION | level_still_in_play | 291 | 18.2% | +0.18 | **KEEP** |
| DIVERGENCE_CONTINUATION | quiet_scalp_block | 6 | 0.0% | +0.19 | **INSUFFICIENT_SAMPLE** |
| QUIET_COMPRESSION_BREAK | quiet_scalp_block | 40 | 0.0% | +0.23 | **KEEP** |
| MOVER_TREND_PULLBACK | level_still_in_play | 493 | 0.0% | +0.26 | **KEEP** |
| FAILED_AUCTION_RECLAIM | quiet_scalp_block | 16 | 0.0% | +0.29 | **INSUFFICIENT_SAMPLE** |
| SR_FLIP_RETEST | min_confidence | 863 | 33.6% | +0.35 | **KEEP** |
| SHADOW_FUNDING_FADE | shadow_unit:SHADOW_FUNDING_FADE | 28 | 39.3% | +0.36 | **KEEP** |
| MOVER_TREND_PULLBACK | min_confidence | 389 | 17.2% | +0.38 | **KEEP** |
| QUIET_COMPRESSION_BREAK | context_floor:QUIET_COMPRESSION_BREAK | 805 | 0.0% | +0.41 | **KEEP** |

- _sorted most-costly first: the top rows are gates whose suppressions lose more than they save on that specific path_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 25 · alerting: **5** · boot grace active: False
- **ALERT** `sar_ledger_candles` — 618/628 unfetchable (98%); top cause: 15m history rolled off before the stamp; symbols: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ADAUSDT +57 more (streak 211/6) (sustained 211 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 4684x (gate reads 0x, withheld 0x — refusal dark); last ACHUSDT age=43694.9s (streak 143/6) (sustained 143 cycles)
- **ALERT** `mean_revert_emission` — 2400 detections since last emission (emitted_total=4) — and the blocked candidates measure +0.58R over n=3085, so the gating is COSTING us. Check gate rejections. (streak 34/6) (sustained 34 cycles)
- **ALERT** `tuned_variants` — 38 unexplained non-stamps (seen=2884 stamped=403 skipped=2443) (streak 134/6) (sustained 134 cycles)
- **ALERT** `auto_dispatch` — 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=18) (streak 165/3) (sustained 165 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 18 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=18) (streak 165/3) | 165 |
| btc_reference | ok | BTC ref 64176.60 | 0 |
| candle_coverage | ok | 79/80 symbols with ≥20 15m candles, 78/80 updated within 45m | 0 |
| context_emission_policy | ok | output +129 / upstream +34 | 0 |
| edge_reconciliation | ok | max divergence MOVER_AVWAP_SCALP +0.24R (< 0.3) | 0 |
| emission_controller | ok | last cycle 0s ago; live_overrides=20 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=9 wasted_promotions=0 pruned=0 | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +5 / upstream +35 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 2400 detections since last emission (emitted_total=4) — and the blocked candidates measure +0.58R over n=3085, so the gating is COSTING us. Check gate rejections. (streak 34/6) | 34 |
| mean_revert_path | ok | output +5 / upstream +35 | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -1.01R over n=1985 — emitting them would lose money | 0 |
| range_fade_path | ok | output +33 / upstream +35 | 0 |
| sar_alignment_crosscheck | ok | 33/1785 disagreed (1.8%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +35 | 0 |
| sar_ledger_candles | violating | 618/628 unfetchable (98%); top cause: 15m history rolled off before the stamp; symbols: 1000BONKUSDT, 1000PEPEUSDT, 1000SHIBUSDT, AAVEUSDT, ADAUSDT +57 more (streak 211/6) | 211 |
| sar_refresh_budget | ok | 16 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 1392 records await one (10 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 7/12) | 7 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 4684x (gate reads 0x, withheld 0x — refusal dark); last ACHUSDT age=43694.9s (streak 143/6) | 143 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +47 / upstream +35 | 0 |
| suppression_audit | ok | output +35 / upstream +34 | 0 |
| tuned_variants | violating | 38 unexplained non-stamps (seen=2884 stamped=403 skipped=2443) (streak 134/6) | 134 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3644346`
- `Path funnel` emissions: `88`
- `Regime distribution` emissions: `88`
- `QUIET_SCALP_BLOCK` events: `363`
- `confidence_gate` events: `19678`
- `free_channel_post` events: `31`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **2**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 2 | 2547 | 2547 | 4440 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **31**

| Source | Count |
|---|---:|
| signal_close | 24 |
| regime_shift | 7 |

- By severity: HIGH=31

## Dependency readiness
- cvd: presence[present=568146] state[populated=568146] buckets[few=6, many=568113, some=27] sources[none] quality[none]
- funding_rate: presence[absent=83849, present=484297] state[empty=83849, populated=484297] buckets[few=484297, none=83849] sources[none] quality[none]
- liquidation_clusters: presence[absent=344650, present=223496] state[empty=344650, populated=223496] buckets[few=175918, none=344650, some=47578] sources[none] quality[none]
- oi_snapshot: presence[absent=81939, present=486207] state[empty=81939, populated=486207] buckets[few=506, many=483831, none=81939, some=1870] sources[none] quality[none]
- order_book: presence[absent=161683, present=406463] state[populated=406463, unavailable=161683] buckets[few=406463, none=161683] sources[book_ticker=406463, unavailable=161683] quality[none=161683, top_of_book_only=406463]
- orderblocks: presence[absent=568146] state[empty=568146] buckets[none=568146] sources[not_implemented=568146] quality[none]
- recent_ticks: presence[present=568146] state[populated=568146] buckets[many=568146] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.4687780141830444` sec
- Median create→first breach: `3357.1162519454956` sec
- Median create→terminal: `3360.694149851799` sec
- Median first breach→terminal: `1.384371042251587` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 4.2}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.3071 | 8304.978282570839 | 8305.383709549904 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7007 | 2371.2331759929657 | 2372.695293903351 |
| MOVER_TREND_PULLBACK | 19 | 19 | 0.0 | 73.7 | 0.0 | 0.0 | -0.3999 | 3516.3190820217133 | 3520.3892228603363 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 14470 | 192 | 2873 | 0.0 | 0.0 | None | None | 11597 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3792 | 5 | 3541 | 0.0 | 0.0 | None | None | 251 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-19`
- Gating Δ: `25270`
- No-generation Δ: `459108`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.7028, "current_avg_pnl": -0.7007, "current_win_rate": 0.0, "previous_avg_pnl": -1.4035, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.2189, "current_avg_pnl": -0.3999, "current_win_rate": 0.0, "previous_avg_pnl": -0.6188, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 61, "geometry_changed_delta": 0, "geometry_preserved_delta": 3397, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 6, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
