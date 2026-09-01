# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `11` sec (warning=False)
- Latest performance record age: `17023` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 59 | 59 | 53 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5398 | 5398 | 5028 | 17 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 33310 | 33321 | 28 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 34760 | 34760 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 34421 | 32915 | 1830 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 34799 | 34411 | 446 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 34665 | 34571 | 128 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 28279 | 28300 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 34861 | 34886 | 5 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 34899 | 33649 | 1762 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 36538 | 39689 | 346 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 33359 | 29739 | 6755 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 34398 | 34398 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 34767 | 34790 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 34389 | 34353 | 66 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 35420 | 34758 | 966 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 34087 | 34278 | 67 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 27765 | 26638 | 1355 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 28002 | 27876 | 225 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 33263 | 33296 | 9 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 28306 | 28273 | 72 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1190 | 1190 | 1067 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 414 | 414 | 217 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 7078 | 7078 | 6760 | 24 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 10 | 10 | 5 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 3509 | 3509 | 2871 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 820 | 820 | 392 | 35 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 15726 | 15726 | 11302 | 218 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 10 | 10 | 9 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 311 | 311 | 125 | 35 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 2011 | 2011 | 1669 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 132 | 132 | 101 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 802 | 802 | 702 | 23 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 48 | 48 | 0 | 6 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1871 | 1871 | 784 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=33321): breakout_not_found=19660, basic_filters_failed=8380, move_not_fresh=3510, breakout_stale=1291, retest_proximity_failed=375, volume_spike_missing=93, move_exhausted=8, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=34760): cls_disabled_merged_into_lsr=34760
- **EVAL::DIVERGENCE_CONTINUATION** (total=32915): cvd_divergence_failed=14014, h1_trend_not_aligned=7998, basic_filters_failed=7716, ema_alignment_reject=2277, regime_blocked=350, retest_proximity_failed=302, missing_fvg_or_orderblock=164, missing_cvd=89, cvd_insufficient=5
- **EVAL::FAILED_AUCTION_RECLAIM** (total=34411): auction_not_detected=22372, basic_filters_failed=7442, reclaim_hold_failed=1705, regime_blocked=1528, tail_too_small=1359, rsi_reject=5
- **EVAL::FUNDING_EXTREME** (total=34571): funding_not_extreme=23931, basic_filters_failed=6560, missing_funding_rate=2088, ema_alignment_reject=1341, rsi_reject=387, momentum_reject=125, cvd_divergence_failed=124, missing_fvg_or_orderblock=15
- **EVAL::LIQUIDATION_REVERSAL** (total=28300): cascade_threshold_not_met=20485, basic_filters_failed=7520, rsi_reject=158, cvd_divergence_failed=127, missing_fvg_or_orderblock=8, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=34886): no_ma_cross=26622, basic_filters_failed=7739, ma_cross_cooldown=393, ma_cross_htf_misaligned=122, ma_cross_htf_unconfirmed=10
- **EVAL::MEAN_REVERT** (total=33649): no_extension=28777, basic_filters_failed=4872
- **EVAL::MOVER_AVWAP_SCALP** (total=39689): no_avwap_tag=14892, no_mover_leg=11565, basic_filters_failed=8636, avwap_slope_against=3189, avwap_reclaim_no_volume=859, no_avwap_reclaim=543, anchor_too_recent=5
- **EVAL::MOVER_TREND_PULLBACK** (total=29739): mover_run_too_small=13516, basic_filters_failed=8473, no_reclaim=6572, no_pullback_tag=1102, insufficient_candles=76
- **EVAL::OPENING_RANGE_BREAKOUT** (total=34398): feature_disabled=34398
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=34790): regime_blocked=21576, breakout_not_found=9582, basic_filters_failed=2310, adx_reject=1242, ema_alignment_reject=80
- **EVAL::QUIET_COMPRESSION_BREAK** (total=34353): regime_blocked=14620, compression_not_detected=10808, basic_filters_failed=5115, breakout_not_detected=3550, volume_confirmation_failed=241, rsi_reject=17, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=34758): no_range_edge=29882, basic_filters_failed=4876
- **EVAL::SR_FLIP_RETEST** (total=34278): flip_close_not_confirmed=21764, basic_filters_failed=7414, long_break_volume_thin=1524, regime_blocked=1515, retest_out_of_zone=853, h1_break_not_confirmed=813, reclaim_hold_failed=258, long_acceptance_not_held=79, wick_quality_failed=22, ema_alignment_reject=14, whipsaw_flip=14, missing_fvg_or_orderblock=8
- **EVAL::STANDARD** (total=26638): momentum_reject=7912, adx_reject=6990, basic_filters_failed=3740, sweeps_not_detected=2852, macd_reject=2256, ema_alignment_reject=2106, htf_poi_unanchored=537, rsi_reject=234, invalid_sl_geometry=11
- **EVAL::TREND_PULLBACK** (total=27876): h1_trend_not_aligned=9073, h1_pullback_not_confirmed=4873, ema_alignment_reject=4191, basic_filters_failed=3313, ema_not_tested_prev=2003, no_ema_reclaim_close=1539, body_conviction_fail=917, rsi_reject=648, regime_blocked=502, prev_already_below_emas=358, no_prev_low_break=234, prev_already_above_emas=75, no_prev_high_break=72, momentum_flat=45, missing_fvg_or_orderblock=21, momentum_reject=6, ema21_not_tagged=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=33296): breakout_not_found=19188, basic_filters_failed=8373, move_not_fresh=3755, breakout_stale=1403, retest_proximity_failed=477, volume_spike_missing=84, missing_fvg_or_orderblock=13, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=28273): momentum_reject=19401, recent_ticks_insufficient=6418, basic_filters_failed=2454

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=3): execution:overextended=3
- **DIVERGENCE_CONTINUATION** (total=145): setup_compat:regime_VOLATILE_UNSUITABLE=141, setup_compat:regime_BREAKOUT_EXPANSION=4
- **FAILED_AUCTION_RECLAIM** (total=468): setup_compat:regime_STRONG_TREND=342, execution:overextended=117, context_floor=9
- **FUNDING_EXTREME_SIGNAL** (total=373): execution:trigger_not_confirmed=371, context_floor=2
- **LIQUIDATION_REVERSAL** (total=4): execution:trigger_not_confirmed=4
- **LIQUIDITY_SWEEP_REVERSAL** (total=1463): execution:trigger_not_confirmed=642, setup_compat:regime_STRONG_TREND=445, execution:overextended=376
- **MA_CROSS_TREND_SHIFT** (total=11): execution:trigger_not_confirmed=4, setup_compat:regime_DIRTY_RANGE=3, setup_compat:regime_CLEAN_RANGE=3, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=2097): setup_compat:regime_STRONG_TREND=1024, setup_compat:regime_WEAK_TREND=736, execution:overextended=337
- **MOVER_AVWAP_SCALP** (total=347): execution:overextended=259, execution:trigger_not_confirmed=80, entry_quality=8
- **MOVER_TREND_PULLBACK** (total=6725): execution:trigger_not_confirmed=3184, execution:overextended=3069, entry_quality=472
- **QUIET_COMPRESSION_BREAK** (total=2): execution:trigger_not_confirmed=2
- **RANGE_FADE** (total=1703): setup_compat:regime_STRONG_TREND=728, setup_compat:regime_WEAK_TREND=527, execution:overextended=323, setup_compat:regime_VOLATILE_UNSUITABLE=116, context_edge=9
- **TREND_PULLBACK_EMA** (total=678): setup_compat:regime_CLEAN_RANGE=421, setup_compat:regime_DIRTY_RANGE=244, setup_compat:regime_VOLATILE_UNSUITABLE=11, entry_quality=2
- **VOLUME_SURGE_BREAKOUT** (total=27): execution:overextended=27
- **WHALE_MOMENTUM** (total=1676): execution:trigger_not_confirmed=1676

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 63934 | 36.8% |
| QUIET | 39045 | 22.5% |
| TRENDING_DOWN | 31826 | 18.3% |
| TRENDING_UP | 30544 | 17.6% |
| VOLATILE | 8397 | 4.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **120**
- Average confidence gap to threshold: **14.32** (samples=120) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=34, TAOUSDT=9, ONGUSDT=9, ETHUSDT=8, AVAXUSDT=8, ADAUSDT=7, 1000SHIBUSDT=7, SOLUSDT=6, SUIUSDT=6, ASTERUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 6 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 45 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 40 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 24 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 2 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 29 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 8 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 142 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 3 |
| MEAN_REVERT | kept | min_confidence_pass | 6 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 85 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 235 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 119 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 11 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2254 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 73 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 4 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 79 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 71 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 8 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 12 |
| WHALE_MOMENTUM | filtered | min_confidence | 62 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 20 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 81.38 | 65.00 | -16.38 | 20.45 | 19.25 | 20.00 | 5.67 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 46 | 57.82 | 64.39 | 6.57 | 20.31 | 19.67 | 18.66 | 0.91 | 11.18 |
| DIVERGENCE_CONTINUATION | kept | 40 | 67.54 | 65.00 | -2.54 | 20.29 | 19.63 | 17.53 | 1.27 | 3.99 |
| FAILED_AUCTION_RECLAIM | filtered | 26 | 49.81 | 63.15 | 13.34 | 19.48 | 20.00 | 20.00 | 3.50 | 23.52 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 73.72 | 65.00 | -8.72 | 20.52 | 19.96 | 20.00 | 4.40 | 1.20 |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 49.77 | 63.07 | 13.30 | 20.24 | 13.99 | 16.95 | 3.48 | 6.13 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 69.48 | 65.00 | -4.48 | 19.95 | 14.00 | 16.32 | 3.00 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 3 | 63.03 | 10.00 | -53.03 | 18.07 | 8.00 | 20.00 | 7.33 | 4.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 8 | 51.31 | 65.00 | 13.69 | 19.68 | 19.46 | 17.00 | 3.00 | 21.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 142 | 70.31 | 65.00 | -5.31 | 20.80 | 18.96 | 17.30 | 1.90 | -0.32 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 67.00 | 65.00 | -2.00 | 20.70 | 16.80 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 3 | 59.70 | 63.67 | 3.97 | 20.80 | 14.00 | 20.00 | 0.00 | 12.00 |
| MEAN_REVERT | kept | 6 | 75.27 | 65.00 | -10.27 | 21.15 | 14.00 | 17.75 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 90 | 54.78 | 64.54 | 9.76 | 20.21 | 16.46 | 15.80 | 3.59 | 9.10 |
| MOVER_AVWAP_SCALP | kept | 235 | 81.01 | 65.00 | -16.01 | 20.39 | 17.37 | 15.80 | 4.61 | 1.13 |
| MOVER_TREND_PULLBACK | filtered | 130 | 57.40 | 63.72 | 6.32 | 20.77 | 18.58 | 15.80 | 3.77 | 10.87 |
| MOVER_TREND_PULLBACK | kept | 2254 | 76.57 | 65.00 | -11.57 | 20.08 | 18.54 | 15.80 | 4.38 | 0.90 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 82.80 | 65.00 | -17.80 | 21.20 | 20.00 | 19.10 | 3.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 77 | 54.50 | 64.95 | 10.45 | 21.41 | 19.51 | 20.00 | 0.00 | 6.84 |
| QUIET_COMPRESSION_BREAK | kept | 79 | 75.78 | 65.00 | -10.78 | 20.79 | 19.01 | 20.00 | 0.00 | -0.93 |
| SR_FLIP_RETEST | kept | 3 | 70.63 | 65.00 | -5.63 | 21.20 | 20.00 | 19.20 | 2.00 | -2.00 |
| TREND_PULLBACK_EMA | filtered | 5 | 60.60 | 64.20 | 3.60 | 19.58 | 19.98 | 16.44 | 5.60 | 11.20 |
| TREND_PULLBACK_EMA | kept | 71 | 79.55 | 65.00 | -14.55 | 20.65 | 19.72 | 17.97 | 4.84 | -0.78 |
| VOLUME_SURGE_BREAKOUT | filtered | 8 | 51.14 | 61.00 | 9.86 | 20.67 | 19.09 | 20.00 | 4.31 | 4.88 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 73.67 | 65.00 | -8.67 | 20.92 | 18.63 | 20.00 | 4.46 | 1.00 |
| WHALE_MOMENTUM | filtered | 82 | 38.53 | 61.61 | 23.08 | 23.90 | 14.14 | 17.00 | 0.00 | 30.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 81.38 | 23.67 | 17.33 | 12.00 | 12.50 | 5.00 | 8.22 | 5.67 |
| DIVERGENCE_CONTINUATION | filtered | 46 | 57.82 | 23.61 | 14.30 | 4.83 | 11.65 | 5.54 | 8.16 | 0.91 |
| DIVERGENCE_CONTINUATION | kept | 40 | 67.54 | 23.40 | 13.25 | 6.97 | 12.95 | 5.90 | 8.38 | 1.27 |
| FAILED_AUCTION_RECLAIM | filtered | 26 | 49.81 | 21.62 | 15.08 | 9.81 | 12.31 | 5.17 | 7.01 | 3.50 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 73.72 | 23.40 | 14.80 | 7.20 | 12.40 | 8.80 | 3.92 | 4.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 49.77 | 21.69 | 12.83 | 6.93 | 12.17 | 7.41 | 5.34 | 3.48 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 69.48 | 19.00 | 18.00 | 4.50 | 10.50 | 9.75 | 7.73 | 3.00 |
| LIQUIDATION_REVERSAL | filtered | 3 | 63.03 | 25.00 | 8.00 | 12.00 | 8.00 | 2.50 | 5.00 | 7.33 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 8 | 51.31 | 21.50 | 14.00 | 8.25 | 12.00 | 7.19 | 6.38 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 142 | 70.31 | 24.14 | 14.03 | 4.46 | 13.04 | 5.88 | 6.86 | 1.90 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 67.00 | 17.00 | 14.00 | 9.00 | 14.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 3 | 59.70 | 17.00 | 18.00 | 15.00 | 13.00 | 5.00 | 3.70 | 0.00 |
| MEAN_REVERT | kept | 6 | 75.27 | 20.00 | 16.00 | 15.00 | 13.00 | 5.00 | 6.27 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 90 | 54.78 | 19.47 | 18.00 | 12.50 | 13.51 | 6.85 | 4.63 | 3.59 |
| MOVER_AVWAP_SCALP | kept | 235 | 81.01 | 19.75 | 18.00 | 11.19 | 14.25 | 6.74 | 8.56 | 4.61 |
| MOVER_TREND_PULLBACK | filtered | 130 | 57.40 | 17.66 | 18.00 | 7.62 | 12.86 | 6.11 | 7.91 | 3.77 |
| MOVER_TREND_PULLBACK | kept | 2254 | 76.57 | 19.05 | 18.01 | 7.96 | 12.87 | 6.36 | 9.00 | 4.38 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 82.80 | 17.00 | 18.00 | 15.00 | 14.00 | 10.00 | 5.30 | 3.50 |
| QUIET_COMPRESSION_BREAK | filtered | 77 | 54.50 | 18.66 | 17.79 | 11.73 | 14.12 | 6.38 | 4.35 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 79 | 75.78 | 19.73 | 16.84 | 11.35 | 14.09 | 6.75 | 7.88 | 0.00 |
| SR_FLIP_RETEST | kept | 3 | 70.63 | 22.33 | 18.00 | 3.00 | 11.33 | 5.00 | 8.97 | 2.00 |
| TREND_PULLBACK_EMA | filtered | 5 | 60.60 | 14.00 | 18.00 | 8.40 | 14.00 | 6.00 | 8.80 | 5.60 |
| TREND_PULLBACK_EMA | kept | 71 | 79.55 | 19.75 | 18.00 | 7.56 | 14.68 | 6.36 | 9.07 | 4.84 |
| VOLUME_SURGE_BREAKOUT | filtered | 8 | 51.14 | 15.38 | 15.50 | 12.00 | 13.62 | 4.88 | 5.32 | 4.31 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 73.67 | 20.33 | 18.00 | 12.75 | 11.67 | 5.25 | 5.96 | 4.46 |
| WHALE_MOMENTUM | filtered | 82 | 38.53 | 20.51 | 14.22 | 8.56 | 13.38 | 7.71 | 4.64 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 6 | 81.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 46 | 57.82 | 0.00 | 0.00 | 3.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.10** |
| DIVERGENCE_CONTINUATION | kept | 40 | 67.54 | 0.00 | 0.00 | 0.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.36** |
| FAILED_AUCTION_RECLAIM | filtered | 26 | 49.81 | 0.00 | 0.00 | 0.00 | 0.00 | 6.37 | 0.00 | 0.00 | 0.00 | **6.37** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 73.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 29 | 49.77 | 0.00 | 0.00 | 3.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.89** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 69.48 | 0.00 | 0.00 | 3.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.00** |
| LIQUIDATION_REVERSAL | filtered | 3 | 63.03 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 8 | 51.31 | 0.00 | 0.00 | 0.00 | 0.00 | 13.50 | 0.00 | 0.00 | 0.00 | **13.50** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 142 | 70.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 3 | 59.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MEAN_REVERT | kept | 6 | 75.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 90 | 54.78 | 0.00 | 0.00 | 0.87 | 0.00 | 7.57 | 0.00 | 0.00 | 0.65 | **9.09** |
| MOVER_AVWAP_SCALP | kept | 235 | 81.01 | 0.00 | 0.00 | 0.06 | 0.00 | 1.48 | 0.00 | 0.00 | 0.11 | **1.65** |
| MOVER_TREND_PULLBACK | filtered | 130 | 57.40 | 0.00 | 0.00 | 4.13 | 0.00 | 3.01 | 0.05 | 0.00 | 0.00 | **7.19** |
| MOVER_TREND_PULLBACK | kept | 2254 | 76.57 | 0.00 | 0.00 | 0.45 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | **0.83** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 82.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 77 | 54.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 1.54 | **1.71** |
| QUIET_COMPRESSION_BREAK | kept | 79 | 75.78 | 0.00 | 0.00 | 0.18 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **0.33** |
| SR_FLIP_RETEST | kept | 3 | 70.63 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 5 | 60.60 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |
| TREND_PULLBACK_EMA | kept | 71 | 79.55 | 0.00 | 0.00 | 0.41 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | **0.58** |
| VOLUME_SURGE_BREAKOUT | filtered | 8 | 51.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.75 | **3.75** |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 73.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 82 | 38.53 | 0.00 | 0.00 | 0.00 | 0.00 | 2.02 | 0.00 | 0.00 | 0.00 | **2.02** |

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
- Outcomes recorded: **64760 held of 143613 seen** across 21 strategies; 1463 cells past the sample floor; **598 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 27906 | 151/27755/0 | 44% | -0.15 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.13R) |
| MOVER_AVWAP_SCALP | 8016 | 33/7983/0 | 40% | -0.26 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5323 | 25/5298/0 | 41% | -0.23 | ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP (+1.63R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 3466 | 12/3454/0 | 52% | +0.00 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.04R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 3257 | 0/0/3257 | 43% | -0.09 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.42R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.04R) |
| TREND_PULLBACK_EMA | 3202 | 2/3200/0 | 44% | -0.19 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| QUIET_COMPRESSION_BREAK | 2888 | 42/2846/0 | 45% | -0.14 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+0.77R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 2644 | 0/0/2644 | 37% | -0.07 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.39R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.88R) |
| SHADOW_FUNDING_FADE | 2008 | 0/0/2008 | 37% | -0.37 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | ASIA/MARKUP/NORMAL/BTC_RISING (-0.91R) |
| WHALE_MOMENTUM | 1908 | 2/1906/0 | 40% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 965 | 6/959/0 | 44% | -0.22 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+0.33R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.13R) |
| FUNDING_EXTREME_SIGNAL | 776 | 0/776/0 | 27% | -0.55 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.39R) |
| MEAN_REVERT | 748 | 2/746/0 | 74% | +0.44 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 706 | 0/706/0 | 48% | -0.10 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SHADOW_CASCADE_REVERSAL | 321 | 0/0/321 | 55% | -0.04 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.22R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.31R) |
| SR_FLIP_RETEST | 256 | 0/256/0 | 62% | -0.13 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.25R) |
| BREAKDOWN_SHORT | 176 | 10/166/0 | 19% | -0.58 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 114 | 0/114/0 | 30% | -0.37 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| LIQUIDATION_REVERSAL | 40 | 0/40/0 | 5% | -1.07 | — | — |
| MA_CROSS_TREND_SHIFT | 38 | 0/38/0 | 37% | -0.18 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 2 | 0/2/0 | 100% | +0.56 | — | — |

- **Strongest cells**: `FAILED_AUCTION_RECLAIM @ ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP` +1.63R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING` +1.44R (n=23, STRONG)
- **Weakest cells**: `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.39R (n=15, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL` -1.39R (n=15, NEGATIVE); `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.24R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 79 | 28% / -0.52R | 79 | 44% / -0.16R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 268 | 48% / -0.16R | 268 | 55% / -0.04R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 214 | 43% / -0.34R | 214 | 44% / -0.24R | +0.10 | **ATR** |
| FAILED_AUCTION_RECLAIM | 380 | 44% / -0.18R | 380 | 46% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4162 | 51% / -0.08R | 4162 | 55% / -0.00R | +0.08 | **ATR** |
| MOVER_AVWAP_SCALP | 577 | 47% / -0.15R | 577 | 52% / -0.07R | +0.08 | **ATR** |
| MEAN_REVERT | 63 | 60% / +0.12R | 63 | 60% / +0.19R | +0.07 | **ATR** |
| BREAKDOWN_SHORT | 15 | 27% / -0.14R | 15 | 27% / -0.09R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 52 | 48% / -0.03R | 52 | 54% / +0.02R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 218 | 53% / -0.15R | 218 | 56% / -0.13R | +0.03 | **ATR** |
| SR_FLIP_RETEST | 41 | 46% / -0.28R | 41 | 46% / -0.26R | +0.02 | **ATR** |
| DIVERGENCE_CONTINUATION | 350 | 53% / -0.02R | 350 | 58% / -0.03R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 456 | 45% / -0.18R | 456 | 45% / -0.18R | -0.00 | **FIXED** |
| RANGE_FADE | 13 | 46% / +0.22R | 13 | 46% / +0.11R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 13 | 31% / -0.26R | 13 | 31% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 4 | 50% / -0.03R | 4 | 50% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 4 | 25% / -0.64R | 4 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6308 | 32% | -0.18R | 259 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 577 | 50% | -0.07R | 140 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 34 | 56% | +0.00R | 30 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 78 | 33% / -0.26R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 434 | 39% / +0.05R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5275 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 697 | 36% / +0.01R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 288 | 39% / +0.03R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 388 | 41% / +0.13R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 352 | 37% / -0.12R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 224 | 47% / -0.10R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 75 | 29% / -0.43R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 84 | 27% / -0.73R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 56 | 52% / +0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 30 | 40% / -0.11R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 12 | 50% / +0.36R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 42 | 29% / -0.38R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 17 | 18% / -0.53R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 7 | 29% / -0.44R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 5 | 60% / +0.24R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 53 · alerting: **7** · boot grace active: False
- **ALERT** `footprint_bars` — 5280 sealed bars over 44 symbols; 3829 incomplete, 0 shape-capped (streak 21/6) (sustained 21 cycles)
- **ALERT** `dark_resolution` — 90 of 92 open dark rows are not being advanced (worst: HEMIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 189/120) (sustained 189 cycles)
- **ALERT** `stale_tf_scoring` — new stale-TF events: scored 88x, gate reads 0x, withheld 88x (lifetime scored 1349x; refusal ARMED); last MAGICUSDT age=46185.8s (streak 24/6) (sustained 24 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.61R (bound 0.3) (streak 189/6) (sustained 189 cycles)
- **ALERT** `mean_revert_emission` — 902 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.44R over n=746, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 42/6) (sustained 42 cycles)
- **ALERT** `range_fade_emission` — 889 detections since last emission (emitted_total=0) — and only 114 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 81/6) (sustained 81 cycles)
- **ALERT** `tuned_variants` — 27 non-stamps — atr_arm_uncomputable=27 (seen=1351 stamped=356 skipped=968) (streak 44/6) (sustained 44 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 27314548 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 13 arms current, none stalled; covering 404/404 signals (100%) | 0 |
| auto_dispatch | ok | placed=21 rejected=1 skipped=22 over 22 fan-out(s) to a keyed roster; top reasons: mode=22, NotionalTooSmall=1 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 78376.50 | 0 |
| candle_coverage | ok | 3/3 symbols with ≥20 15m candles, 3/3 updated within 45m [fresh=3; 3 Tier-1 futures + 0 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 885 dup bars, 0 undedupable; ws 0 out-of-order, 292 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 32 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 32 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +15 / upstream +44 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1355/1372 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | violating | 90 of 92 open dark rows are not being advanced (worst: HEMIUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 189/120) | 189 |
| dark_sar_arms | ok | no open arms; covering 1353/1370 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 7720417 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.61R (bound 0.3) (streak 189/6) | 189 |
| emission_controller | ok | last cycle 1534s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4415 stamps (MEAN_REVERT=750, MOVER_AVWAP_SCALP=113, MOVER_TREND_PULLBACK=3247, RANGE_FADE=257, TREND_PULLBACK_EMA=48), no declared feature wholly absent; set aside 4 undeclared (extension_pct,funding_rate,pullback_depth_atr,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | violating | 5280 sealed bars over 44 symbols; 3829 incomplete, 0 shape-capped (streak 21/6) | 21 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +167 | 0 |
| indicator_cache_key | ok | 49859 frozen value(s) avoided; 126967 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 902 detections since last emission (emitted_total=1) — and the POST-SCORING blocked candidates measure +0.44R over n=746, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 42/6) | 42 |
| mean_revert_path | ok | output +22 / upstream +167 | 0 |
| mover_admission_metadata | ok | 883 symbols known, 180 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | no pairs held (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2909 rows held, 927442 evicted (sampled: execution:trigger_not_confirmed 400/339781, execution:overextended 400/321235, setup_compat:regime_STRONG_TREND 400/124827) | 0 |
| price_action_lane | ok | 175172 evaluated, 484 emitted; layer1 484 stamped / 0 blind; cooldown=22491, delta_opposed=16710, no_footprint=62730, no_opposing_target=307, no_sweep=55860, rr_below_floor=16590 | 0 |
| promoted_pair_integrity | ok | no pairs under promotion | 0 |
| range_fade_emission | violating | 889 detections since last emission (emitted_total=0) — and only 114 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 81/6) | 81 |
| range_fade_path | violating | upstream +167 but output +0 (streak 1/72) | 1 |
| sar_alignment_crosscheck | ok | 189/9765 disagreed (1.9%) | 0 |
| sar_exit_shadow | violating | upstream +167 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 687 held arms settled, 126 unscored, 13 still walking (13 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 28/28 resolvable | 0 |
| sar_live_arms | ok | 13 arms current, none stalled; covering 413/413 signals (100%) | 0 |
| sar_refresh_budget | ok | 39 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 26 still mid-window | 0 |
| scan_cycle | ok | last 17.6s, worst 270.39s over 2780 lifetime cycles; lifetime 235 over 60s, 42 over 120s (plus 1/0 during boot warm-up, not counted); recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.03s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 91715 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 24s ago (1.75s to run, worst 178.3s), 962 overrun(s) of 3532 cycles, TTL 900s; slowest agents=1.64s, signals=1.11s, tickers=0.18s | 0 |
| stale_tf_scoring | violating | new stale-TF events: scored 88x, gate reads 0x, withheld 88x (lifetime scored 1349x; refusal ARMED); last MAGICUSDT age=46185.8s (streak 24/6) | 24 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +19 / upstream +167 | 0 |
| structural_snap | ok | 4447/4447 measured, 9 blind, 0 levels moved (refusals: redetect_cooldown=471) | 0 |
| structural_veto_lane | ok | 901 stamped; 0 with no readable level book, 13 with clear air ahead, 724 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +167 / upstream +44 | 0 |
| tuned_variants | violating | 27 non-stamps — atr_arm_uncomputable=27 (seen=1351 stamped=356 skipped=968) (streak 44/6) | 44 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `88514`
- `Path funnel` emissions: `27`
- `Regime distribution` emissions: `27`
- `QUIET_SCALP_BLOCK` events: `120`
- `confidence_gate` events: `3366`
- `free_channel_post` events: `24`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **321**
- Total REST-fallback activations: **4**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 7 | 6919 | 9749 | 23815 | 0 |
| futures_aggtrade | 140 | 5272 | 20734 | 65880 | 0 |
| futures_depth | 141 | 6192 | 20561 | 64227 | 0 |
| futures_liq | 30 | 8118 | 35135 | 54933 | 0 |
| futures_mover | 3 | 4350 | 4350 | 9325 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 4 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **24**

| Source | Count |
|---|---:|
| signal_close | 20 |
| regime_shift | 4 |

- By severity: HIGH=24

## Dependency readiness
- cvd: presence[absent=603, present=141175] state[empty=603, populated=141175] buckets[few=8, many=141039, none=603, some=128] sources[none] quality[none]
- funding_rate: presence[absent=15972, present=125806] state[empty=15972, populated=125806] buckets[few=125806, none=15972] sources[none] quality[none]
- liquidation_clusters: presence[absent=86117, present=55661] state[empty=86117, populated=55661] buckets[few=44092, none=86117, some=11569] sources[none] quality[none]
- oi_snapshot: presence[absent=15453, present=126325] state[empty=15453, populated=126325] buckets[few=275, many=124599, none=15453, some=1451] sources[none] quality[none]
- order_book: presence[absent=59163, present=82615] state[populated=82615, unavailable=59163] buckets[few=82615, none=59163] sources[book_ticker=82615, unavailable=59163] quality[none=59163, top_of_book_only=82615]
- orderblocks: presence[absent=141778] state[empty=141778] buckets[none=141778] sources[measured_dark=141778] quality[none]
- recent_ticks: presence[absent=1650, present=140128] state[empty=1650, populated=140128] buckets[many=140128, none=1650] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `13.634038090705872` sec
- Median create→first breach: `2784.5839940309525` sec
- Median create→terminal: `2795.8674745559692` sec
- Median first breach→terminal: `3.572476029396057` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 7.1}, "under_180s": {"count": 2, "pct": 7.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 3.6}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.9876847012811206 | 1.1538611935795857 | 0.8583130907208151 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.9912476009330963 | 1.4220440134278294 | 0.6970583129446882 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 2.261979769175698 | 2.802292078589806 | 0.8071891529286952 | 0 | 1 |
| MOVER_TREND_PULLBACK | 21 | 21 | 3.838144907632326 | 3.0 | 1.3847953192984046 | 18 | 3 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 1.4511440948599095 | 1.6091543000178787 | 0.8887943525719335 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9877 | 20672.27379655838 | 20674.90639102459 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.422 | 13894.730149030685 | 13896.461147069931 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.262 | 12720.78887796402 | 12724.261204957962 |
| MOVER_TREND_PULLBACK | 21 | 21 | 0.0 | 42.9 | 0.0 | 0.0 | 0.3249 | 2026.5024218559265 | 2027.0618398189545 |
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.5762 | 19536.24225616455 | 19542.80100798607 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 132 | 1 | 101 | 0.0 | 0.0 | None | None | 31 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 802 | 23 | 702 | 0.0 | 0.0 | None | None | 100 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `368`
- Gating Δ: `31086`
- No-generation Δ: `624901`
- Fast failures Δ: `2`
- Quality changes: `{"MOVER_AVWAP_SCALP": {"avg_pnl_delta": -3.4962, "current_avg_pnl": -2.262, "current_win_rate": 0.0, "previous_avg_pnl": 1.2342, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.0292, "current_avg_pnl": 0.3249, "current_win_rate": 0.0, "previous_avg_pnl": -1.7043, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -1.7278, "current_avg_pnl": -1.5762, "current_win_rate": 0.0, "previous_avg_pnl": 0.1516, "previous_win_rate": 25.0, "win_rate_delta": -25.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 31, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 23, "geometry_changed_delta": 0, "geometry_preserved_delta": 100, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
