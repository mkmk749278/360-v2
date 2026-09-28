# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `814` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 497 | 497 | 497 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 26331 | 26331 | 25182 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 170211 | 170175 | 58 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 147251 | 147251 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 146927 | 141675 | 5568 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 147281 | 144590 | 2778 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 158109 | 157844 | 290 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 141535 | 141544 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 147374 | 147402 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 147411 | 142934 | 5991 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 178019 | 183498 | 3196 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 170241 | 154383 | 23595 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 156840 | 156840 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 147255 | 147224 | 50 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 146901 | 146699 | 224 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 148934 | 144962 | 5004 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 145608 | 146502 | 364 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 131336 | 122251 | 9399 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 131658 | 130767 | 960 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 170168 | 170106 | 102 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 141547 | 141568 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 11963 | 11963 | 11099 | 4 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1363 | 1363 | 1037 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 51 | 51 | 50 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 50580 | 50580 | 49729 | 13 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 19840 | 19840 | 18325 | 3 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 10078 | 10078 | 9023 | 41 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 81868 | 81868 | 67820 | 248 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 82 | 82 | 82 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1595 | 1595 | 1551 | 11 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 14238 | 14238 | 13677 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1150 | 1150 | 1000 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 4997 | 4997 | 4603 | 17 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 430 | 430 | 343 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=170175): breakout_not_found=97958, basic_filters_failed=34096, move_not_fresh=26714, breakout_stale=8490, retest_proximity_failed=2491, volume_spike_missing=414, missing_fvg_or_orderblock=10, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=147251): cls_disabled_merged_into_lsr=147251
- **EVAL::DIVERGENCE_CONTINUATION** (total=141675): cvd_divergence_failed=59866, h1_trend_not_aligned=47751, basic_filters_failed=23206, ema_alignment_reject=9244, retest_proximity_failed=1133, missing_fvg_or_orderblock=475
- **EVAL::FAILED_AUCTION_RECLAIM** (total=144590): auction_not_detected=101377, basic_filters_failed=22018, reclaim_hold_failed=9787, tail_too_small=7605, regime_blocked=3785, rsi_reject=18
- **EVAL::FUNDING_EXTREME** (total=157844): funding_not_extreme=126282, basic_filters_failed=24068, missing_funding_rate=2931, ema_alignment_reject=2805, rsi_reject=752, cvd_divergence_failed=497, momentum_reject=456, missing_fvg_or_orderblock=53
- **EVAL::LIQUIDATION_REVERSAL** (total=141544): cascade_threshold_not_met=114914, basic_filters_failed=25260, cvd_divergence_failed=727, rsi_reject=498, missing_fvg_or_orderblock=120, volume_spike_missing=25
- **EVAL::MA_CROSS_TREND_SHIFT** (total=147402): no_ma_cross=121241, basic_filters_failed=23215, ma_cross_htf_misaligned=1908, ma_cross_cooldown=1011, ma_cross_htf_unconfirmed=27
- **EVAL::MEAN_REVERT** (total=142934): no_extension=124117, basic_filters_failed=18817
- **EVAL::MOVER_AVWAP_SCALP** (total=183498): no_avwap_tag=69616, no_mover_leg=59392, basic_filters_failed=34185, avwap_slope_against=11303, avwap_reclaim_no_volume=5034, no_avwap_reclaim=3860, anchor_too_recent=108
- **EVAL::MOVER_TREND_PULLBACK** (total=154383): mover_run_too_small=90354, basic_filters_failed=34141, no_reclaim=24596, no_pullback_tag=5292
- **EVAL::OPENING_RANGE_BREAKOUT** (total=156840): feature_disabled=156840
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=147224): regime_blocked=93160, breakout_not_found=41417, adx_reject=6948, basic_filters_failed=5628, ema_alignment_reject=71
- **EVAL::QUIET_COMPRESSION_BREAK** (total=146699): compression_not_detected=66038, regime_blocked=57811, basic_filters_failed=16385, breakout_not_detected=5777, volume_confirmation_failed=646, rsi_reject=25, missing_fvg_or_orderblock=17
- **EVAL::RANGE_FADE** (total=144962): no_range_edge=126140, basic_filters_failed=18822
- **EVAL::SR_FLIP_RETEST** (total=146502): flip_close_not_confirmed=104235, basic_filters_failed=22007, long_break_volume_thin=5562, h1_break_not_confirmed=4420, retest_out_of_zone=4055, regime_blocked=3782, reclaim_hold_failed=1195, long_acceptance_not_held=795, ema_alignment_reject=187, whipsaw_flip=180, wick_quality_failed=74, missing_fvg_or_orderblock=10
- **EVAL::STANDARD** (total=122251): momentum_reject=38243, adx_reject=31522, basic_filters_failed=13854, macd_reject=12543, sweeps_not_detected=12525, ema_alignment_reject=10435, htf_poi_unanchored=2787, rsi_reject=229, invalid_sl_geometry=105, mtf_reject=8
- **EVAL::TREND_PULLBACK** (total=130767): h1_trend_not_aligned=51909, ema_alignment_reject=21328, ema_not_tested_prev=13070, basic_filters_failed=11463, h1_pullback_not_confirmed=10348, no_ema_reclaim_close=9141, body_conviction_fail=5287, rsi_reject=4494, prev_already_above_emas=1268, prev_already_below_emas=839, no_prev_high_break=573, no_prev_low_break=427, momentum_flat=344, ema21_not_tagged=156, missing_fvg_or_orderblock=119, momentum_reject=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=170106): breakout_not_found=104908, basic_filters_failed=34096, move_not_fresh=21236, breakout_stale=7491, retest_proximity_failed=2016, volume_spike_missing=304, missing_fvg_or_orderblock=51, move_exhausted=4
- **EVAL::WHALE_MOMENTUM** (total=141568): momentum_reject=90175, recent_ticks_insufficient=41110, basic_filters_failed=10283

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=41): execution:overextended=41
- **DIVERGENCE_CONTINUATION** (total=491): setup_compat:regime_VOLATILE_UNSUITABLE=369, setup_compat:regime_BREAKOUT_EXPANSION=122
- **FAILED_AUCTION_RECLAIM** (total=2663): setup_compat:regime_STRONG_TREND=1202, execution:overextended=1009, context_floor=452
- **FUNDING_EXTREME_SIGNAL** (total=1156): execution:trigger_not_confirmed=1155, context_floor=1
- **LIQUIDATION_REVERSAL** (total=51): execution:trigger_not_confirmed=51
- **LIQUIDITY_SWEEP_REVERSAL** (total=14132): execution:overextended=5391, execution:trigger_not_confirmed=5293, setup_compat:regime_STRONG_TREND=3448
- **MA_CROSS_TREND_SHIFT** (total=5): execution:trigger_not_confirmed=2, execution:overextended=1, setup_compat:regime_CLEAN_RANGE=1, setup_compat:regime_DIRTY_RANGE=1
- **MEAN_REVERT** (total=12821): setup_compat:regime_STRONG_TREND=6160, setup_compat:regime_WEAK_TREND=4856, execution:overextended=1776, entry_quality=29
- **MOVER_AVWAP_SCALP** (total=4386): execution:overextended=3105, execution:trigger_not_confirmed=919, entry_quality=362
- **MOVER_TREND_PULLBACK** (total=30302): execution:trigger_not_confirmed=14633, execution:overextended=12769, entry_quality=2900
- **QUIET_COMPRESSION_BREAK** (total=52): execution:trigger_not_confirmed=52
- **RANGE_FADE** (total=6749): setup_compat:regime_WEAK_TREND=3423, setup_compat:regime_STRONG_TREND=2308, setup_compat:regime_VOLATILE_UNSUITABLE=746, execution:overextended=272
- **TREND_PULLBACK_EMA** (total=4223): setup_compat:regime_CLEAN_RANGE=2847, setup_compat:regime_DIRTY_RANGE=1319, entry_quality=55, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **VOLUME_SURGE_BREAKOUT** (total=10): execution:overextended=10

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 431687 | 45.6% |
| TRENDING_DOWN | 173100 | 18.3% |
| QUIET | 157989 | 16.7% |
| TRENDING_UP | 155529 | 16.4% |
| VOLATILE | 27817 | 2.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **48**
- Average confidence gap to threshold: **12.66** (samples=48) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: MUBARAKUSDT=12, BNBUSDT=11, ETHUSDT=7, XLMUSDT=4, ZECUSDT=3, AAVEUSDT=3, BCHUSDT=3, FILUSDT=2, LTCUSDT=2, AEROUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 81 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 75 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 173 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 9 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 19 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 78 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 109 |
| MEAN_REVERT | kept | min_confidence_pass | 34 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 106 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 425 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 845 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 17 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 5515 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 19 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 25 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 15 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 192 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 93 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 82 | 57.09 | 63.33 | 6.24 | 19.77 | 19.84 | 17.48 | 1.83 | 12.70 |
| DIVERGENCE_CONTINUATION | kept | 75 | 71.11 | 65.00 | -6.11 | 19.70 | 19.85 | 18.88 | 1.73 | 1.56 |
| FAILED_AUCTION_RECLAIM | filtered | 182 | 50.95 | 61.97 | 11.02 | 20.20 | 19.37 | 20.00 | 3.79 | 5.25 |
| FAILED_AUCTION_RECLAIM | kept | 4 | 69.80 | 65.00 | -4.80 | 20.20 | 19.23 | 20.00 | 2.62 | 1.50 |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 47.94 | 61.42 | 13.48 | 20.38 | 14.00 | 17.00 | 3.00 | 9.14 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.70 | 65.00 | -3.70 | 18.45 | 14.00 | 15.60 | 3.00 | 0.00 |
| LIQUIDATION_REVERSAL | filtered | 1 | 79.30 | 10.00 | -69.30 | 21.20 | 8.00 | 20.00 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 53.08 | 64.64 | 11.56 | 20.38 | 18.39 | 16.95 | 1.81 | 18.51 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 109 | 67.51 | 65.00 | -2.51 | 20.87 | 18.62 | 17.37 | 2.69 | 0.11 |
| MEAN_REVERT | kept | 34 | 73.10 | 65.00 | -8.10 | 18.91 | 16.02 | 14.79 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 108 | 56.40 | 64.59 | 8.19 | 20.83 | 16.12 | 15.80 | 4.22 | 20.28 |
| MOVER_AVWAP_SCALP | kept | 425 | 77.89 | 65.00 | -12.89 | 20.50 | 16.13 | 15.80 | 4.86 | 2.60 |
| MOVER_TREND_PULLBACK | filtered | 862 | 58.58 | 63.93 | 5.35 | 19.45 | 18.57 | 15.80 | 4.33 | 16.15 |
| MOVER_TREND_PULLBACK | kept | 5515 | 75.73 | 65.00 | -10.73 | 20.07 | 18.71 | 15.80 | 4.14 | 1.34 |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 53.04 | 65.00 | 11.96 | 22.69 | 20.00 | 20.00 | 0.00 | 12.63 |
| QUIET_COMPRESSION_BREAK | kept | 25 | 74.10 | 65.00 | -9.10 | 21.14 | 19.29 | 20.00 | 0.00 | 1.39 |
| SR_FLIP_RETEST | kept | 15 | 69.95 | 65.00 | -4.95 | 19.79 | 20.00 | 19.68 | 3.43 | 3.29 |
| TREND_PULLBACK_EMA | filtered | 192 | 59.20 | 64.77 | 5.57 | 21.57 | 20.00 | 18.60 | 4.80 | 17.49 |
| TREND_PULLBACK_EMA | kept | 93 | 80.14 | 65.00 | -15.14 | 19.74 | 19.27 | 17.53 | 4.11 | 0.49 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 76.55 | 65.00 | -11.55 | 20.70 | 18.07 | 20.00 | 4.33 | 2.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 82 | 57.09 | 24.51 | 13.85 | 4.13 | 11.63 | 7.14 | 7.60 | 1.83 |
| DIVERGENCE_CONTINUATION | kept | 75 | 71.11 | 24.89 | 15.60 | 6.36 | 10.59 | 5.04 | 8.46 | 1.73 |
| FAILED_AUCTION_RECLAIM | filtered | 182 | 50.95 | 22.45 | 16.22 | 4.52 | 12.29 | 5.71 | 4.74 | 3.79 |
| FAILED_AUCTION_RECLAIM | kept | 4 | 69.80 | 21.00 | 17.00 | 5.25 | 12.00 | 6.75 | 6.67 | 2.62 |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 47.94 | 25.00 | 8.00 | 4.11 | 13.89 | 6.89 | 5.66 | 3.00 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.70 | 25.00 | 18.00 | 3.00 | 12.00 | 6.00 | 1.70 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 1 | 79.30 | 25.00 | 20.00 | 15.00 | 8.00 | 5.00 | 2.30 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 53.08 | 21.31 | 14.15 | 8.08 | 13.15 | 6.44 | 6.66 | 1.81 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 109 | 67.51 | 24.25 | 14.04 | 3.83 | 11.55 | 5.10 | 6.17 | 2.69 |
| MEAN_REVERT | kept | 34 | 73.10 | 21.94 | 17.88 | 9.00 | 12.91 | 5.00 | 6.36 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 108 | 56.40 | 16.85 | 18.00 | 9.42 | 13.97 | 6.45 | 9.30 | 4.22 |
| MOVER_AVWAP_SCALP | kept | 425 | 77.89 | 20.07 | 18.25 | 10.51 | 13.24 | 6.21 | 7.35 | 4.86 |
| MOVER_TREND_PULLBACK | filtered | 862 | 58.58 | 17.31 | 18.00 | 7.64 | 12.16 | 6.88 | 8.51 | 4.33 |
| MOVER_TREND_PULLBACK | kept | 5515 | 75.73 | 19.22 | 18.00 | 7.77 | 12.59 | 6.55 | 8.89 | 4.14 |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 53.04 | 19.53 | 18.00 | 10.42 | 14.00 | 6.47 | 3.72 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 25 | 74.10 | 18.92 | 15.76 | 13.80 | 14.24 | 5.54 | 8.07 | 0.00 |
| SR_FLIP_RETEST | kept | 15 | 69.95 | 25.00 | 18.00 | 3.40 | 10.27 | 5.00 | 8.15 | 3.43 |
| TREND_PULLBACK_EMA | filtered | 192 | 59.20 | 17.00 | 18.00 | 7.50 | 14.00 | 5.96 | 9.42 | 4.80 |
| TREND_PULLBACK_EMA | kept | 93 | 80.14 | 21.99 | 18.00 | 7.50 | 13.96 | 6.75 | 8.78 | 4.11 |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 76.55 | 18.33 | 15.00 | 13.00 | 13.50 | 5.00 | 9.88 | 4.33 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 82 | 57.09 | 0.00 | 0.00 | 0.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.49** |
| DIVERGENCE_CONTINUATION | kept | 75 | 71.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 182 | 50.95 | 0.00 | 0.00 | 0.79 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | **1.99** |
| FAILED_AUCTION_RECLAIM | kept | 4 | 69.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 19 | 47.94 | 0.00 | 0.00 | 5.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.98** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 68.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDATION_REVERSAL | filtered | 1 | 79.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 53.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 109 | 67.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 34 | 73.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 108 | 56.40 | 0.00 | 0.00 | 1.07 | 0.00 | 2.01 | 0.74 | 0.00 | 0.00 | **3.82** |
| MOVER_AVWAP_SCALP | kept | 425 | 77.89 | 0.02 | 0.00 | 0.00 | 0.00 | 0.05 | 0.02 | 0.00 | 0.38 | **0.47** |
| MOVER_TREND_PULLBACK | filtered | 862 | 58.58 | 0.00 | 0.00 | 0.05 | 0.00 | 1.65 | 0.07 | 0.00 | 0.00 | **1.77** |
| MOVER_TREND_PULLBACK | kept | 5515 | 75.73 | 0.00 | 0.00 | 0.01 | 0.00 | 0.27 | 0.04 | 0.00 | 0.00 | **0.32** |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 53.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.25 | **6.25** |
| QUIET_COMPRESSION_BREAK | kept | 25 | 74.10 | 0.00 | 0.00 | 0.00 | 0.00 | 1.04 | 0.00 | 0.00 | 0.00 | **1.04** |
| SR_FLIP_RETEST | kept | 15 | 69.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 192 | 59.20 | 0.00 | 0.00 | 0.00 | 0.00 | 2.44 | 0.00 | 0.00 | 0.00 | **2.44** |
| TREND_PULLBACK_EMA | kept | 93 | 80.14 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.26** |
| VOLUME_SURGE_BREAKOUT | kept | 6 | 76.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **115618 held of 345398 seen** across 21 strategies; 2633 cells past the sample floor; **1233 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 39500 | 618/38882/0 | 46% | -0.13 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.22R) |
| MOVER_AVWAP_SCALP | 14862 | 196/14666/0 | 40% | -0.28 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 9040 | 109/8931/0 | 42% | -0.19 | LONDON/RANGE/NORMAL/BTC_NEUTRAL (+1.74R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 7488 | 44/7444/0 | 51% | +0.02 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 6198 | 0/0/6198 | 43% | -0.09 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | LONDON/QUIET/NORMAL/BTC_RISING (-0.83R) |
| TREND_PULLBACK_EMA | 6026 | 26/6000/0 | 46% | -0.08 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/QUIET/COMPRESSED/BTC_FALLING (-1.33R) |
| SHADOW_RANGE_FADE | 5348 | 0/0/5348 | 37% | -0.09 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.34R) |
| QUIET_COMPRESSION_BREAK | 5089 | 316/4773/0 | 46% | -0.13 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+0.88R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4848 | 0/0/4848 | 34% | -0.41 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| LIQUIDITY_SWEEP_REVERSAL | 3731 | 64/3667/0 | 42% | -0.31 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.93R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (-1.41R) |
| WHALE_MOMENTUM | 3391 | 2/3389/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| MEAN_REVERT | 2348 | 31/2317/0 | 50% | -0.08 | OVERLAP/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.62R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 2015 | 2/2013/0 | 32% | -0.44 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1917 | 0/1917/0 | 35% | -0.17 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1276 | 12/1264/0 | 50% | -0.17 | ASIA/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+0.80R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 941 | 0/0/941 | 54% | -0.03 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.42R) |
| RANGE_FADE | 761 | 2/759/0 | 39% | -0.40 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 551 | 53/498/0 | 32% | -0.35 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 214 | 0/214/0 | 11% | -0.99 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 66 | 8/58/0 | 48% | -0.01 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 8 | 0/8/0 | 75% | +0.30 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ NY/MARKUP/NORMAL/BTC_RISING/MIDCAP` +2.03R (n=15, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP` -1.41R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 149 | 28% / -0.55R | 149 | 46% / -0.20R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 490 | 44% / -0.22R | 490 | 56% / -0.03R | +0.19 | **ATR** |
| BREAKDOWN_SHORT | 45 | 40% / -0.21R | 45 | 44% / -0.08R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 1191 | 44% / -0.20R | 1191 | 50% / -0.08R | +0.13 | **ATR** |
| SR_FLIP_RETEST | 142 | 47% / -0.28R | 142 | 49% / -0.17R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 368 | 44% / -0.33R | 368 | 46% / -0.22R | +0.10 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 751 | 49% / -0.22R | 751 | 56% / -0.13R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 6153 | 50% / -0.09R | 6153 | 55% / -0.00R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 843 | 42% / -0.20R | 843 | 45% / -0.11R | +0.08 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 106 | 39% / -0.14R | 106 | 46% / -0.07R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 695 | 51% / -0.05R | 695 | 57% / -0.03R | +0.02 | **ATR** |
| RANGE_FADE | 40 | 38% / -0.25R | 40 | 40% / -0.26R | -0.01 | **FIXED** |
| MEAN_REVERT | 176 | 54% / -0.05R | 176 | 52% / -0.04R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 827 | 46% / -0.15R | 827 | 46% / -0.16R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 21 | 43% / -0.12R | 21 | 43% / -0.12R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 6 | 50% / -0.21R | 6 | 50% / -0.10R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8789 | 29% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1191 | 48% | -0.07R | 198 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 66 | 48% | -0.07R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 141 | 36% / -0.32R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 804 | 35% / -0.14R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7862 | 36% / -0.14R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1554 | 35% / -0.09R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 685 | 35% / -0.16R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 789 | 40% / +0.02R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 656 | 39% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 749 | 42% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 153 | 28% / -0.42R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 200 | 30% / -0.60R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 146 | 55% / +0.11R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 78 | 42% / -0.13R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 32 | 34% / +0.07R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 146 | 36% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 31 | 23% / -0.36R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 20 | 45% / +0.07R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 10 | 40% / +0.02R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 60 · alerting: **6** · boot grace active: False
- **ALERT** `ai_governor_verdicts` — upstream +3 but output +0 (streak 8/6) (sustained 8 cycles)
- **ALERT** `sar_ledger_candles` — 38/89 unfetchable (43%); top cause: gap or duplicate bar in the 15m window; symbols: APTUSDT, ARKUSDT, DOTUSDT, ETHUSDT, FETUSDT +9 more (streak 47/6) (sustained 47 cycles)
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×913]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 140/6) (sustained 140 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.57R (bound 0.3) (streak 140/6) (sustained 140 cycles)
- **ALERT** `mean_revert_emission` — 8809 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure -0.09R over n=2317, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 21/6) (sustained 21 cycles)
- **ALERT** `tuned_variants` — 70 non-stamps — atr_arm_uncomputable=70 (seen=4387 stamped=317 skipped=4000) (streak 87/6) (sustained 87 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 16209752 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 28 arms current, none stalled; covering 958/958 signals (100%) | 0 |
| ai_governor_verdicts | violating | upstream +3 but output +0 (streak 8/6) | 8 |
| atr_trail_live_arms | ok | 55 arms current, none stalled; covering 1065/1065 signals (100%) | 0 |
| auto_dispatch | ok | placed=0 rejected=1 skipped=42 over 43 fan-out(s) to a keyed roster; top reasons: venue:coindcx=42, NotionalTooSmall=1 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| binance_ip_weight | ok | peak 260/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82730.20 | 0 |
| candle_coverage | ok | 85/85 symbols with ≥20 15m candles, 85/85 updated within 45m [fresh=85; 75 Tier-1 futures + 10 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 903 dup bars, 0 undedupable; ws 0 out-of-order, 191 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 34 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 34 cohorts, 9 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +361 / upstream +33 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1208/1225 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 4 promoted today, nothing refused | 0 |
| dark_resolution | violating | 1 of 101 open dark rows are not being advanced (worst: 1000BONKUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 1/120) | 1 |
| dark_sar_arms | ok | no open arms; covering 1208/1225 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 3733208 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.57R (bound 0.3) (streak 140/6) | 140 |
| emission_controller | ok | last cycle 350s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×913]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 140/6) | 140 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=62, profile_reject=8. Held back in this window: session_quality=119, profile_reject=11. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 2/6) | 2 |
| firestore_read_budget | ok | 1,384 reads/day of 50,000 [engine 1,369, signing 15]; top site keystore.roster_doc at 289/day (engine) | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +16 / upstream +507 | 0 |
| indicator_cache_key | ok | 27981 frozen value(s) avoided; 330060 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 8809 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure -0.09R over n=2317, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 21/6) | 21 |
| mean_revert_path | ok | output +41 / upstream +507 | 0 |
| mover_admission_metadata | ok | 907 symbols known, 201 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 10 held, 10 with scan counts, 9 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 2049812 evicted (sampled: execution:trigger_not_confirmed 400/750444, execution:overextended 400/684558, setup_compat:regime_STRONG_TREND 400/303322) | 0 |
| price_action_lane | ok | 512110 evaluated, 345 emitted; layer1 345 stamped / 0 blind; cooldown=70627, delta_opposed=48268, no_footprint=204685, no_opposing_target=496, no_sweep=140984, rr_below_floor=46705 | 0 |
| promoted_pair_integrity | ok | 10/10 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.41R over n=759 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +319 / upstream +507 | 0 |
| sar_alignment_crosscheck | ok | 68/6596 disagreed (1.0%) | 0 |
| sar_exit_shadow | ok | output +12 / upstream +507 | 0 |
| sar_hold_arm | ok | 1826 held arms settled, 174 unscored, 53 still walking (42 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 38/89 unfetchable (43%); top cause: gap or duplicate bar in the 15m window; symbols: APTUSDT, ARKUSDT, DOTUSDT, ETHUSDT, FETUSDT +9 more (streak 47/6) | 47 |
| sar_live_arms | ok | 53 arms current, none stalled; covering 1065/1065 signals (100%) | 0 |
| sar_refresh_budget | ok | 5 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 489 records await one (51 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 43.31s, worst 64.27s over 6206 lifetime cycles; lifetime 1 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.98s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 232371 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 1s ago (0.28s to run, worst 45.24s), 114 overrun(s) of 3120 cycles, TTL 900s; slowest signals=0.08s, data_intake=0.05s, activity=0.03s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +132 / upstream +507 | 0 |
| structural_snap | ok | 5693/5693 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=1020) | 0 |
| structural_veto_lane | ok | 1299 stamped; 0 with no readable level book, 18 with clear air ahead, 858 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +507 / upstream +33 | 0 |
| tuned_variants | violating | 70 non-stamps — atr_arm_uncomputable=70 (seen=4387 stamped=317 skipped=4000) (streak 87/6) | 87 |
| unlock_shorts | ok | 2 open, 46 scheduled, calendar 8.6h old | 0 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4321586`
- `Path funnel` emissions: `113`
- `Regime distribution` emissions: `113`
- `QUIET_SCALP_BLOCK` events: `48`
- `confidence_gate` events: `7846`
- `free_channel_post` events: `0`
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
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=792390] state[populated=792390] buckets[many=792390] sources[none] quality[none]
- funding_rate: presence[absent=70513, present=721877] state[empty=70513, populated=721877] buckets[few=721877, none=70513] sources[none] quality[none]
- liquidation_clusters: presence[absent=392265, present=400125] state[empty=392265, populated=400125] buckets[few=329784, none=392265, some=70341] sources[none] quality[none]
- oi_snapshot: presence[absent=66148, present=726242] state[empty=66148, populated=726242] buckets[many=726242, none=66148] sources[none] quality[none]
- order_book: presence[absent=203672, present=588718] state[populated=588718, unavailable=203672] buckets[few=588718, none=203672] sources[book_ticker=588718, unavailable=203672] quality[none=203672, top_of_book_only=588718]
- orderblocks: presence[absent=792390] state[empty=792390] buckets[none=792390] sources[measured_dark=792390] quality[none]
- recent_ticks: presence[present=792390] state[populated=792390] buckets[many=792390] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.294750213623047` sec
- Median create→first breach: `4038.571449995041` sec
- Median create→terminal: `4038.9881591796875` sec
- Median first breach→terminal: `6.604194641113281e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 2.7}, "under_180s": {"count": 2, "pct": 2.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 2.7}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.3312486763148534 | 1.438667339727409 | 0.8279218560605635 | 0 | 3 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 1.4583343141150218 | 1.6553894562192555 | 0.8541447531515134 | 0 | 4 |
| MOVER_AVWAP_SCALP | 5 | 5 | 2.0019539688616685 | 2.083586237188887 | 1.0163628564721048 | 3 | 2 |
| MOVER_TREND_PULLBACK | 55 | 55 | 3.8937908342101903 | 3.0 | 1.3733401833780896 | 39 | 16 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 0.8568724361573854 | 0.9414983739837397 | 0.9077657410422139 | 0 | 6 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 0.8085 | 7639.120023965836 | 7639.120046854019 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 4 | 25.0 | 25.0 | 25.0 | 0.0 | 0.3902 | 7972.5587195158005 | 7972.746447563171 |
| MOVER_AVWAP_SCALP | 5 | 5 | 40.0 | 40.0 | 40.0 | 0.0 | 1.1744 | 3534.5203800201416 | 3541.7890758514404 |
| MOVER_TREND_PULLBACK | 55 | 55 | 34.5 | 40.0 | 34.5 | 0.0 | 0.2296 | 3232.6036779880524 | 3232.603703022003 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 33.3 | 66.7 | 33.3 | 0.0 | -0.1103 | 16551.49539554119 | 16552.03334748745 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1150 | 1 | 1000 | 0.0 | 0.0 | None | None | 150 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 4997 | 17 | 4603 | 0.0 | 0.0 | None | None | 394 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `106`
- Gating Δ: `27166`
- No-generation Δ: `294821`
- Fast failures Δ: `2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.5097, "current_avg_pnl": 0.8085, "current_win_rate": 33.3, "previous_avg_pnl": -0.7012, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.3902, "current_avg_pnl": 0.3902, "current_win_rate": 25.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 25.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.767, "current_avg_pnl": 1.1744, "current_win_rate": 40.0, "previous_avg_pnl": 2.9414, "previous_win_rate": 100.0, "win_rate_delta": -60.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.2697, "current_avg_pnl": 0.2296, "current_win_rate": 34.5, "previous_avg_pnl": -0.0401, "previous_win_rate": 31.4, "win_rate_delta": 3.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.8546, "current_avg_pnl": -0.1103, "current_win_rate": 33.3, "previous_avg_pnl": -0.9649, "previous_win_rate": 0.0, "win_rate_delta": 33.3}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -107, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 93, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1250.94, "median_terminal_delta_sec": -1251.21, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
