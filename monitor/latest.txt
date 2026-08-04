# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `7334` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 94 | 94 | 66 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 23812 | 23812 | 21308 | 17 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 149175 | 149169 | 22 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 137148 | 137154 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 136870 | 131025 | 6118 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 137187 | 134490 | 2780 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 141421 | 140974 | 478 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 130535 | 130543 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 137274 | 137299 | 15 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 137317 | 132721 | 5728 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 153800 | 158099 | 1086 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 149192 | 135284 | 18497 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 139331 | 139338 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 137157 | 137177 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 136832 | 136317 | 550 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 138451 | 134588 | 4822 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 134714 | 133173 | 3617 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 126109 | 120399 | 5959 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 126359 | 125815 | 594 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 149157 | 149070 | 104 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 130545 | 130381 | 202 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 12691 | 12691 | 10263 | 30 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1255 | 1255 | 100 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 31169 | 31169 | 30639 | 21 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 22 | 22 | 6 | 3 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 15528 | 15528 | 12412 | 19 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2632 | 2632 | 526 | 43 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 47472 | 47472 | 26773 | 362 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 22 | 22 | 22 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3788 | 3788 | 2033 | 41 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 12482 | 12482 | 10628 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 13957 | 13957 | 6674 | 55 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3077 | 3077 | 2586 | 20 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 243 | 243 | 14 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 9918 | 9918 | 705 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=149169): breakout_not_found=77948, basic_filters_failed=49050, move_not_fresh=15820, breakout_stale=4588, retest_proximity_failed=1584, volume_spike_missing=124, ema_alignment_reject=29, move_exhausted=26
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=137155): cls_disabled_merged_into_lsr=137155
- **EVAL::DIVERGENCE_CONTINUATION** (total=131026): cvd_divergence_failed=46900, basic_filters_failed=42565, h1_trend_not_aligned=29170, ema_alignment_reject=9790, retest_proximity_failed=1865, missing_fvg_or_orderblock=725, cvd_insufficient=11
- **EVAL::FAILED_AUCTION_RECLAIM** (total=134491): auction_not_detected=69863, basic_filters_failed=42267, reclaim_hold_failed=12022, tail_too_small=7935, regime_blocked=2403, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=140975): funding_not_extreme=88562, basic_filters_failed=44019, ema_alignment_reject=3661, missing_funding_rate=2686, rsi_reject=1100, cvd_divergence_failed=448, momentum_reject=443, missing_fvg_or_orderblock=56
- **EVAL::LIQUIDATION_REVERSAL** (total=130543): cascade_threshold_not_met=84828, basic_filters_failed=44344, cvd_divergence_failed=717, rsi_reject=605, missing_fvg_or_orderblock=25, volume_spike_missing=24
- **EVAL::MA_CROSS_TREND_SHIFT** (total=137300): no_ma_cross=91008, basic_filters_failed=42581, ma_cross_cooldown=2840, ma_cross_htf_misaligned=871
- **EVAL::MEAN_REVERT** (total=132721): no_extension=112884, basic_filters_failed=19837
- **EVAL::MOVER_AVWAP_SCALP** (total=158099): no_avwap_tag=56987, basic_filters_failed=49168, no_mover_leg=40765, avwap_slope_against=6448, avwap_reclaim_no_volume=2631, no_avwap_reclaim=2071, anchor_too_recent=29
- **EVAL::MOVER_TREND_PULLBACK** (total=135284): mover_run_too_small=59644, basic_filters_failed=49105, no_reclaim=22649, no_pullback_tag=3886
- **EVAL::OPENING_RANGE_BREAKOUT** (total=139339): feature_disabled=139339
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=137178): regime_blocked=94176, breakout_not_found=27148, basic_filters_failed=12004, adx_reject=3786, ema_alignment_reject=53, rsi_reject=11
- **EVAL::QUIET_COMPRESSION_BREAK** (total=136318): regime_blocked=45334, compression_not_detected=41676, basic_filters_failed=30253, breakout_not_detected=17556, volume_confirmation_failed=1371, rsi_reject=111, missing_fvg_or_orderblock=17
- **EVAL::RANGE_FADE** (total=134588): no_range_edge=114745, basic_filters_failed=19843
- **EVAL::SR_FLIP_RETEST** (total=133174): flip_close_not_confirmed=57015, basic_filters_failed=42245, long_break_volume_thin=10026, whipsaw_flip=7022, retest_out_of_zone=6415, reclaim_hold_failed=5507, regime_blocked=2398, wick_quality_failed=1359, long_acceptance_not_held=610, h1_break_not_confirmed=264, missing_fvg_or_orderblock=189, ema_alignment_reject=82, rsi_reject=42
- **EVAL::STANDARD** (total=120399): momentum_reject=43963, adx_reject=27266, basic_filters_failed=15827, sweeps_not_detected=14388, macd_reject=10488, ema_alignment_reject=6116, htf_poi_unanchored=2028, rsi_reject=174, invalid_sl_geometry=142, mtf_reject=7
- **EVAL::TREND_PULLBACK** (total=125815): h1_trend_not_aligned=38324, h1_pullback_not_confirmed=23627, basic_filters_failed=22701, ema_alignment_reject=12609, ema_not_tested_prev=9650, no_ema_reclaim_close=6840, body_conviction_fail=4720, rsi_reject=4485, no_prev_high_break=1081, prev_already_above_emas=714, prev_already_below_emas=526, no_prev_low_break=266, momentum_flat=156, missing_fvg_or_orderblock=58, momentum_reject=38, ema21_not_tagged=20
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=149070): breakout_not_found=73640, basic_filters_failed=49050, move_not_fresh=17606, breakout_stale=6846, retest_proximity_failed=1494, volume_spike_missing=286, move_exhausted=73, ema_alignment_reject=66, missing_fvg_or_orderblock=9
- **EVAL::WHALE_MOMENTUM** (total=130381): momentum_reject=98946, recent_ticks_insufficient=23345, basic_filters_failed=8090

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=34): execution:overextended=34
- **DIVERGENCE_CONTINUATION** (total=570): setup_compat:regime_VOLATILE_UNSUITABLE=538, setup_compat:regime_BREAKOUT_EXPANSION=32
- **FAILED_AUCTION_RECLAIM** (total=3243): execution:overextended=1228, setup_compat:regime_STRONG_TREND=1191, context_floor=764, setup_compat:regime_VOLATILE_UNSUITABLE=60
- **FUNDING_EXTREME_SIGNAL** (total=1143): execution:trigger_not_confirmed=1098, context_floor=45
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=7150): execution:trigger_not_confirmed=3822, execution:overextended=1816, setup_compat:regime_STRONG_TREND=1512
- **MA_CROSS_TREND_SHIFT** (total=21): setup_compat:regime_CLEAN_RANGE=9, setup_compat:regime_DIRTY_RANGE=6, execution:trigger_not_confirmed=3, execution:overextended=2, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=8472): setup_compat:regime_WEAK_TREND=4046, setup_compat:regime_STRONG_TREND=3504, execution:overextended=922
- **MOVER_AVWAP_SCALP** (total=1364): execution:overextended=1120, execution:trigger_not_confirmed=244
- **MOVER_TREND_PULLBACK** (total=22100): execution:overextended=11311, execution:trigger_not_confirmed=10607, entry_quality=182
- **QUIET_COMPRESSION_BREAK** (total=1490): context_floor=1340, execution:trigger_not_confirmed=150
- **RANGE_FADE** (total=5789): setup_compat:regime_STRONG_TREND=2573, setup_compat:regime_WEAK_TREND=2211, setup_compat:regime_VOLATILE_UNSUITABLE=492, execution:overextended=363, context_edge=118, setup_compat:regime_BREAKOUT_EXPANSION=32
- **TREND_PULLBACK_EMA** (total=2609): setup_compat:regime_CLEAN_RANGE=1901, setup_compat:regime_DIRTY_RANGE=646, setup_compat:regime_VOLATILE_UNSUITABLE=62
- **VOLUME_SURGE_BREAKOUT** (total=22): context_floor=21, execution:overextended=1
- **WHALE_MOMENTUM** (total=9025): execution:trigger_not_confirmed=8590, context_floor=435

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 282824 | 33.6% |
| QUIET | 244279 | 29.0% |
| TRENDING_UP | 148365 | 17.6% |
| TRENDING_DOWN | 130151 | 15.5% |
| VOLATILE | 35342 | 4.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **449**
- Average confidence gap to threshold: **11.21** (samples=449) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=136, XRPUSDT=31, SOLUSDT=26, 1000PEPEUSDT=16, ONDOUSDT=16, XLMUSDT=14, BCHUSDT=14, DEXEUSDT=13, UNIUSDT=12, HYPEUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 17 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 267 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 17 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 433 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 118 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 33 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 381 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 47 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 21 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 206 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 6 |
| MEAN_REVERT | filtered | min_confidence | 50 |
| MEAN_REVERT | kept | min_confidence_pass | 139 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 275 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 27 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 1157 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2414 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 27 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 11180 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 94 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 36 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 206 |
| SR_FLIP_RETEST | filtered | min_confidence | 894 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 127 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1651 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 36 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 321 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 166 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 8 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 148 |
| WHALE_MOMENTUM | filtered | min_confidence | 77 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 22 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 17 | 76.16 | 65.00 | -11.16 | 20.79 | 18.02 | 20.00 | 4.76 | 1.59 |
| DIVERGENCE_CONTINUATION | filtered | 284 | 56.83 | 64.66 | 7.83 | 20.63 | 19.58 | 18.04 | 1.44 | 10.24 |
| DIVERGENCE_CONTINUATION | kept | 433 | 69.65 | 65.00 | -4.65 | 20.47 | 19.68 | 18.85 | 1.99 | 1.03 |
| FAILED_AUCTION_RECLAIM | filtered | 151 | 54.19 | 61.95 | 7.76 | 20.64 | 17.61 | 20.00 | 3.20 | 8.39 |
| FAILED_AUCTION_RECLAIM | kept | 381 | 74.55 | 65.00 | -9.55 | 20.96 | 17.42 | 20.00 | 3.72 | 0.22 |
| FUNDING_EXTREME_SIGNAL | filtered | 49 | 43.62 | 65.00 | 21.38 | 20.69 | 13.39 | 17.02 | 3.10 | 8.17 |
| LIQUIDATION_REVERSAL | filtered | 1 | 64.00 | 10.00 | -54.00 | 20.20 | 8.00 | 20.00 | 8.00 | 4.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 61.51 | 65.00 | 3.49 | 19.70 | 19.23 | 19.35 | 1.91 | 7.45 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 206 | 70.29 | 65.00 | -5.29 | 19.93 | 17.39 | 18.18 | 2.50 | 0.33 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 32.00 | 65.00 | 33.00 | 21.10 | 14.10 | 15.80 | 0.00 | 20.00 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.55 | 65.00 | -5.55 | 20.80 | 18.75 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 50 | 55.46 | 64.80 | 9.34 | 21.92 | 14.00 | 16.20 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 139 | 68.88 | 65.00 | -3.88 | 20.98 | 15.32 | 16.93 | 0.00 | 0.86 |
| MOVER_AVWAP_SCALP | filtered | 302 | 56.86 | 59.77 | 2.91 | 20.25 | 14.81 | 15.80 | 3.31 | 9.68 |
| MOVER_AVWAP_SCALP | kept | 1157 | 77.89 | 65.00 | -12.89 | 21.11 | 17.31 | 15.80 | 4.53 | 1.07 |
| MOVER_TREND_PULLBACK | filtered | 2441 | 52.46 | 62.70 | 10.24 | 19.58 | 18.00 | 15.80 | 4.23 | 16.51 |
| MOVER_TREND_PULLBACK | kept | 11180 | 76.59 | 65.00 | -11.59 | 20.29 | 18.55 | 15.80 | 4.53 | 1.13 |
| QUIET_COMPRESSION_BREAK | filtered | 130 | 52.73 | 63.89 | 11.16 | 20.62 | 19.44 | 20.00 | 0.00 | 5.85 |
| QUIET_COMPRESSION_BREAK | kept | 206 | 77.76 | 65.00 | -12.76 | 21.56 | 19.59 | 20.00 | 0.00 | -0.50 |
| SR_FLIP_RETEST | filtered | 1021 | 58.08 | 64.97 | 6.89 | 20.20 | 19.90 | 15.48 | 1.21 | 10.73 |
| SR_FLIP_RETEST | kept | 1651 | 70.87 | 65.00 | -5.87 | 20.97 | 19.94 | 15.70 | 2.10 | 0.51 |
| TREND_PULLBACK_EMA | filtered | 36 | 59.31 | 65.00 | 5.69 | 21.02 | 19.44 | 17.68 | 5.39 | 11.39 |
| TREND_PULLBACK_EMA | kept | 321 | 78.48 | 65.00 | -13.48 | 21.35 | 19.63 | 17.56 | 4.86 | -1.96 |
| VOLUME_SURGE_BREAKOUT | filtered | 166 | 51.32 | 65.00 | 13.68 | 20.75 | 18.21 | 20.00 | 3.87 | 5.50 |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 79.15 | 65.00 | -14.15 | 18.40 | 16.50 | 20.00 | 5.31 | 7.50 |
| WHALE_MOMENTUM | filtered | 225 | 55.12 | 64.59 | 9.47 | 22.37 | 15.09 | 17.00 | 0.00 | 11.74 |
| WHALE_MOMENTUM | kept | 22 | 67.33 | 65.00 | -2.33 | 22.75 | 14.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 17 | 76.16 | 21.24 | 18.00 | 13.41 | 11.00 | 3.82 | 5.51 | 4.76 |
| DIVERGENCE_CONTINUATION | filtered | 284 | 56.83 | 22.15 | 12.65 | 5.19 | 12.94 | 5.49 | 8.75 | 1.44 |
| DIVERGENCE_CONTINUATION | kept | 433 | 69.65 | 23.32 | 16.08 | 5.24 | 11.86 | 5.36 | 8.24 | 1.99 |
| FAILED_AUCTION_RECLAIM | filtered | 151 | 54.19 | 20.32 | 16.44 | 6.44 | 12.56 | 4.98 | 5.41 | 3.20 |
| FAILED_AUCTION_RECLAIM | kept | 381 | 74.55 | 22.13 | 16.05 | 5.29 | 13.46 | 6.81 | 7.35 | 3.72 |
| FUNDING_EXTREME_SIGNAL | filtered | 49 | 43.62 | 25.00 | 8.00 | 5.27 | 13.45 | 8.53 | 3.44 | 3.10 |
| LIQUIDATION_REVERSAL | filtered | 1 | 64.00 | 25.00 | 8.00 | 12.00 | 8.00 | 2.50 | 5.30 | 8.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 61.51 | 17.36 | 15.45 | 6.14 | 11.27 | 8.61 | 8.22 | 1.91 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 206 | 70.29 | 22.86 | 14.29 | 6.61 | 12.41 | 5.91 | 6.03 | 2.50 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 32.00 | 17.00 | 14.00 | 9.00 | 14.00 | 5.00 | 8.00 | 0.00 |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.55 | 19.67 | 14.00 | 10.00 | 12.17 | 6.67 | 8.05 | 0.00 |
| MEAN_REVERT | filtered | 50 | 55.46 | 25.00 | 14.16 | 9.00 | 12.00 | 5.00 | 5.30 | 0.00 |
| MEAN_REVERT | kept | 139 | 68.88 | 23.06 | 16.59 | 6.91 | 12.00 | 6.07 | 5.12 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 302 | 56.86 | 17.82 | 18.14 | 9.74 | 13.65 | 5.16 | 5.29 | 3.31 |
| MOVER_AVWAP_SCALP | kept | 1157 | 77.89 | 19.77 | 18.19 | 9.31 | 13.66 | 5.77 | 8.04 | 4.53 |
| MOVER_TREND_PULLBACK | filtered | 2441 | 52.46 | 17.84 | 18.10 | 7.93 | 13.55 | 5.61 | 8.18 | 4.23 |
| MOVER_TREND_PULLBACK | kept | 11180 | 76.59 | 19.29 | 18.05 | 7.96 | 13.17 | 5.85 | 9.11 | 4.53 |
| QUIET_COMPRESSION_BREAK | filtered | 130 | 52.73 | 17.49 | 16.89 | 11.72 | 14.12 | 5.95 | 4.53 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 206 | 77.76 | 18.99 | 17.36 | 12.17 | 14.42 | 6.23 | 8.79 | 0.00 |
| SR_FLIP_RETEST | filtered | 1021 | 58.08 | 17.24 | 16.76 | 5.37 | 12.59 | 6.62 | 9.03 | 1.21 |
| SR_FLIP_RETEST | kept | 1651 | 70.87 | 22.11 | 14.04 | 6.22 | 13.21 | 6.29 | 8.59 | 2.10 |
| TREND_PULLBACK_EMA | filtered | 36 | 59.31 | 13.67 | 18.00 | 7.50 | 15.25 | 8.28 | 8.17 | 5.39 |
| TREND_PULLBACK_EMA | kept | 321 | 78.48 | 19.70 | 18.00 | 7.61 | 14.24 | 6.18 | 9.13 | 4.86 |
| VOLUME_SURGE_BREAKOUT | filtered | 166 | 51.32 | 20.95 | 15.06 | 12.00 | 11.96 | 4.46 | 3.52 | 3.87 |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 79.15 | 23.00 | 16.50 | 13.88 | 13.62 | 5.00 | 9.34 | 5.31 |
| WHALE_MOMENTUM | filtered | 225 | 55.12 | 23.80 | 11.42 | 6.99 | 12.10 | 6.42 | 7.01 | 0.00 |
| WHALE_MOMENTUM | kept | 22 | 67.33 | 25.00 | 8.45 | 11.73 | 14.05 | 8.34 | 9.76 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 17 | 76.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 284 | 56.83 | 0.00 | 0.00 | 1.46 | 0.00 | 0.84 | 0.00 | 0.00 | 0.00 | **2.30** |
| DIVERGENCE_CONTINUATION | kept | 433 | 69.65 | 0.00 | 0.00 | 0.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.69** |
| FAILED_AUCTION_RECLAIM | filtered | 151 | 54.19 | 0.00 | 0.00 | 1.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.24** |
| FAILED_AUCTION_RECLAIM | kept | 381 | 74.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | **0.04** |
| FUNDING_EXTREME_SIGNAL | filtered | 49 | 43.62 | 0.00 | 0.00 | 2.84 | 0.00 | 0.73 | 0.00 | 0.00 | 0.00 | **3.57** |
| LIQUIDATION_REVERSAL | filtered | 1 | 64.00 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 22 | 61.51 | 0.00 | 0.00 | 6.47 | 0.00 | 0.98 | 0.00 | 0.00 | 0.00 | **7.45** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 206 | 70.29 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.33** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 32.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 6 | 70.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 50 | 55.46 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 139 | 68.88 | 0.00 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.86** |
| MOVER_AVWAP_SCALP | filtered | 302 | 56.86 | 3.10 | 0.00 | 0.81 | 0.00 | 0.00 | 0.00 | 0.00 | 2.37 | **6.28** |
| MOVER_AVWAP_SCALP | kept | 1157 | 77.89 | 0.32 | 0.00 | 0.33 | 0.00 | 0.00 | 0.02 | 0.00 | 0.42 | **1.09** |
| MOVER_TREND_PULLBACK | filtered | 2441 | 52.46 | 0.00 | 0.00 | 0.83 | 0.00 | 0.49 | 0.02 | 0.00 | 0.08 | **1.42** |
| MOVER_TREND_PULLBACK | kept | 11180 | 76.59 | 0.00 | 0.00 | 0.80 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | **0.91** |
| QUIET_COMPRESSION_BREAK | filtered | 130 | 52.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.53 | 0.69 | 0.00 | 4.24 | **5.46** |
| QUIET_COMPRESSION_BREAK | kept | 206 | 77.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.05 | **0.09** |
| SR_FLIP_RETEST | filtered | 1021 | 58.08 | 0.00 | 0.00 | 0.83 | 0.00 | 0.91 | 0.18 | 0.00 | 0.22 | **2.14** |
| SR_FLIP_RETEST | kept | 1651 | 70.87 | 0.00 | 0.00 | 0.19 | 0.00 | 0.01 | 0.00 | 0.00 | 0.06 | **0.26** |
| TREND_PULLBACK_EMA | filtered | 36 | 59.31 | 0.00 | 0.00 | 2.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.67** |
| TREND_PULLBACK_EMA | kept | 321 | 78.48 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.07** |
| VOLUME_SURGE_BREAKOUT | filtered | 166 | 51.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.08 | **4.08** |
| VOLUME_SURGE_BREAKOUT | kept | 8 | 79.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.75 | **0.75** |
| WHALE_MOMENTUM | filtered | 225 | 55.12 | 0.00 | 0.00 | 0.00 | 0.00 | 1.63 | 0.00 | 0.00 | 0.00 | **1.63** |
| WHALE_MOMENTUM | kept | 22 | 67.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- _no classified suppressed candidates yet — candidates classify after their validity window (~1h) of real candles has accumulated_

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 113113 across 21 strategies; 2541 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 26232 | 162/26070/0 | 55% | +0.03 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MAJOR (+1.27R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.21R) |
| FAILED_AUCTION_RECLAIM | 16856 | 24/16832/0 | 52% | +0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16530 | 1/16529/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 10471 | 4/10467/0 | 47% | -0.07 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.45R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 8052 | 0/8052/0 | 50% | -0.09 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+1.39R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 5205 | 27/5178/0 | 33% | -0.38 | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.01R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| LIQUIDITY_SWEEP_REVERSAL | 4123 | 9/4114/0 | 47% | -0.18 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (+1.78R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 4104 | 0/0/4104 | 42% | -0.04 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.00R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.06R) |
| SHADOW_RANGE_FADE | 3750 | 0/0/3750 | 41% | +0.18 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.37R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.02R) |
| MEAN_REVERT | 3649 | 0/3649/0 | 76% | +0.50 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| SHADOW_FUNDING_FADE | 3278 | 0/0/3278 | 40% | -0.30 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.33R) | NY/MARKUP/COMPRESSED/BTC_NEUTRAL (-0.89R) |
| TREND_PULLBACK_EMA | 3253 | 2/3251/0 | 52% | -0.20 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+0.73R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| RANGE_FADE | 2727 | 0/2727/0 | 21% | -0.68 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.34R) |
| VOLUME_SURGE_BREAKOUT | 1810 | 13/1797/0 | 40% | -0.06 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| WHALE_MOMENTUM | 1226 | 0/1226/0 | 47% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| FUNDING_EXTREME_SIGNAL | 1040 | 2/1038/0 | 34% | -0.32 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.07R) | OVERLAP/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.29R) |
| SHADOW_CASCADE_REVERSAL | 359 | 0/0/359 | 46% | -0.21 | LONDON/MARKUP/CASCADE/BTC_NEUTRAL (+0.15R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.83R) |
| BREAKDOWN_SHORT | 301 | 7/294/0 | 59% | +0.33 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| LIQUIDATION_REVERSAL | 66 | 0/66/0 | 64% | -0.48 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| MA_CROSS_TREND_SHIFT | 14 | 1/13/0 | 36% | -0.39 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` +1.78R (n=42, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.45R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 45 | 38% / -0.31R | 45 | 53% / -0.09R | +0.23 | **ATR** |
| TREND_PULLBACK_EMA | 95 | 44% / -0.27R | 95 | 48% / -0.11R | +0.16 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 60 | 45% / +0.05R | 60 | 48% / -0.06R | -0.11 | **FIXED** |
| MOVER_AVWAP_SCALP | 295 | 40% / -0.21R | 295 | 43% / -0.11R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 2759 | 46% / -0.20R | 2759 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 702 | 47% / -0.11R | 702 | 53% / -0.05R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 609 | 50% / -0.18R | 609 | 53% / -0.12R | +0.06 | **ATR** |
| RANGE_FADE | 192 | 13% / -0.80R | 192 | 16% / -0.74R | +0.05 | **ATR** |
| MEAN_REVERT | 336 | 55% / +0.04R | 336 | 51% / +0.09R | +0.05 | **ATR** |
| WHALE_MOMENTUM | 87 | 49% / -0.25R | 87 | 48% / -0.28R | -0.03 | **FIXED** |
| MOVER_TREND_PULLBACK | 3111 | 54% / -0.02R | 3111 | 56% / +0.00R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1171 | 47% / -0.11R | 1171 | 46% / -0.13R | -0.02 | **FIXED** |
| BREAKDOWN_SHORT | 15 | 27% / -0.30R | 15 | 27% / -0.29R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2221 | 47% / -0.10R | 2221 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 8 | 38% / -0.27R | 8 | 38% / -0.23R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 40% / -0.81R | 5 | 40% / -0.40R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 3639 | 32% | -0.13R | 256 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 285 | 41% | -0.12R | 99 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 18 | 61% | +0.10R | 14 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1209 | 28% / -1.71R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 7 | 14% / -0.93R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 2418 | 35% / -0.44R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 919 | 33% / -0.59R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 42 | 21% / -1.02R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 495 | 30% / -2.17R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 544 | 36% / -0.06R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 235 | 40% / -1.51R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 42 | 21% / -2.75R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 84 | 26% / -1.32R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 215 | 31% / -0.14R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 8 | 25% / -0.39R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 68 | 41% / -0.26R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 33 | 48% / -0.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 5 | 20% / -1.42R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 19 | 42% / -0.37R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 35 · alerting: **6** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 99/6) (sustained 99 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 1975x (gate reads 0x, withheld 0x — refusal dark); last RIFUSDT age=6837.8s (streak 33/6) (sustained 33 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.37R (bound 0.3) (streak 99/6) (sustained 99 cycles)
- **ALERT** `mean_revert_emission` — 4221 detections since last emission (emitted_total=5) — and the blocked candidates measure +0.50R over n=3649, so the gating is COSTING us. Check gate rejections. (streak 59/6) (sustained 59 cycles)
- **ALERT** `tuned_variants` — 55 non-stamps — atr_arm_uncomputable=55 (seen=2518 stamped=212 skipped=2251) (streak 99/6) (sustained 99 cycles)
- **ALERT** `auto_dispatch` — 7 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=8) (streak 30/3) (sustained 30 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | violating | 7 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: mode=8) (streak 30/3) | 30 |
| btc_reference | ok | BTC ref 63804.90 | 0 |
| candle_coverage | ok | 91/95 symbols with ≥20 15m candles, 86/95 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 592 dup bars, 0 undedupable; ws 0 out-of-order, 111 in-place; SAR refused 3 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 3 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 99/6) | 99 |
| context_emission_policy | ok | output +57 / upstream +47 | 0 |
| dark_resolution | ok | 7 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open dark arms | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.37R (bound 0.3) (streak 99/6) | 99 |
| emission_controller | ok | last cycle 649s ago; live_overrides=24 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=13 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4000 stamps (MEAN_REVERT=451, MOVER_AVWAP_SCALP=310, MOVER_TREND_PULLBACK=2031, RANGE_FADE=917, TREND_PULLBACK_EMA=291), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 4417 evaluated, 21 suppressed, 0 shadow-rejected; live rules: profile_reject | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +269 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 4221 detections since last emission (emitted_total=5) — and the blocked candidates measure +0.50R over n=3649, so the gating is COSTING us. Check gate rejections. (streak 59/6) | 59 |
| mean_revert_path | ok | output +60 / upstream +269 | 0 |
| mover_admission_metadata | ok | 852 symbols known, 151 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3041 rows held, 52034 evicted (sampled: execution:trigger_not_confirmed 400/20931, execution:overextended 400/15098, setup_compat:regime_STRONG_TREND 400/8164) | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE counterfactuals measure -0.68R over n=2727 — emitting them would lose money | 0 |
| range_fade_path | ok | output +91 / upstream +269 | 0 |
| sar_alignment_crosscheck | ok | 183/6468 disagreed (2.8%) | 0 |
| sar_exit_shadow | violating | upstream +269 but output +0 (streak 1/6) | 1 |
| sar_ledger_candles | ok | 17/78 unfetchable (22%); top cause: gap or duplicate bar in the 15m window; symbols: ACEUSDT, ATOMUSDT, BICOUSDT, LABUSDT, OPUSDT | 0 |
| sar_live_arms | ok | 2 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 3 resolved, 58 still mid-window | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 1975x (gate reads 0x, withheld 0x — refusal dark); last RIFUSDT age=6837.8s (streak 33/6) | 33 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +87 / upstream +269 | 0 |
| suppression_audit | ok | output +269 / upstream +47 | 0 |
| tuned_variants | violating | 55 non-stamps — atr_arm_uncomputable=55 (seen=2518 stamped=212 skipped=2251) (streak 99/6) | 99 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3958181`
- `Path funnel` emissions: `104`
- `Regime distribution` emissions: `104`
- `QUIET_SCALP_BLOCK` events: `449`
- `confidence_gate` events: `20606`
- `free_channel_post` events: `16`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **16**

| Source | Count |
|---|---:|
| signal_close | 13 |
| regime_shift | 3 |

- By severity: HIGH=16

## Dependency readiness
- cvd: presence[present=626120] state[populated=626120] buckets[few=1, many=626044, some=75] sources[none] quality[none]
- funding_rate: presence[absent=48540, present=577580] state[empty=48540, populated=577580] buckets[few=577580, none=48540] sources[none] quality[none]
- liquidation_clusters: presence[absent=371897, present=254223] state[empty=371897, populated=254223] buckets[few=203196, none=371897, some=51027] sources[none] quality[none]
- oi_snapshot: presence[absent=46133, present=579987] state[empty=46133, populated=579987] buckets[many=579987, none=46133] sources[none] quality[none]
- order_book: presence[absent=165893, present=460227] state[populated=460227, unavailable=165893] buckets[few=460227, none=165893] sources[book_ticker=460227, unavailable=165893] quality[none=165893, top_of_book_only=460227]
- orderblocks: presence[absent=626120] state[empty=626120] buckets[none=626120] sources[not_implemented=626120] quality[none]
- recent_ticks: presence[absent=5319, present=620801] state[empty=5319, populated=620801] buckets[many=620801, none=5319] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.718038082122803` sec
- Median create→first breach: `1497.428200006485` sec
- Median create→terminal: `1499.044589996338` sec
- Median first breach→terminal: `3.5070600509643555` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 15.4}, "under_180s": {"count": 2, "pct": 15.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 7.7}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 13 | 13 | 0.0 | 46.2 | 0.0 | 0.0 | 0.7581 | 1497.428200006485 | 1499.044589996338 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 13957 | 55 | 6674 | 0.0 | 0.0 | None | None | 7283 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3077 | 20 | 2586 | 0.0 | 0.0 | None | None | 491 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-36`
- Gating Δ: `7377`
- No-generation Δ: `421987`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.2558, "current_avg_pnl": 0.7581, "current_win_rate": 0.0, "previous_avg_pnl": -0.4977, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -40, "geometry_changed_delta": 0, "geometry_preserved_delta": -3792, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 258, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
