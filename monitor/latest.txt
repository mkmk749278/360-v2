# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: FAILED_AUCTION_RECLAIM
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `2483` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 252 | 252 | 244 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5968 | 5968 | 5749 | 4 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 63479 | 63435 | 62 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 48989 | 48989 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 48803 | 47387 | 1590 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 49003 | 48488 | 552 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 53900 | 53788 | 130 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 46407 | 46414 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 49046 | 49067 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 49080 | 47307 | 2532 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 67445 | 70775 | 1055 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 63499 | 55418 | 11973 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 53530 | 53530 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 48992 | 48983 | 18 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 48785 | 48690 | 110 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 49848 | 48707 | 1449 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 48402 | 48647 | 121 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 41692 | 39441 | 2387 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 41832 | 41559 | 316 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 63444 | 63450 | 27 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 46419 | 46435 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3009 | 3009 | 2918 | 5 | active-healthy (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 807 | 807 | 770 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14759 | 14759 | 14648 | 9 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 10 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 7160 | 7160 | 6565 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2972 | 2972 | 2455 | 35 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 36353 | 36353 | 31398 | 222 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 24 | 24 | 24 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 679 | 679 | 586 | 9 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3772 | 3772 | 3678 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 573 | 573 | 484 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1822 | 1822 | 1746 | 11 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 174 | 174 | 141 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=63435): breakout_not_found=41188, basic_filters_failed=14456, move_not_fresh=4283, breakout_stale=2310, retest_proximity_failed=951, volume_spike_missing=166, move_exhausted=80, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=48989): cls_disabled_merged_into_lsr=48989
- **EVAL::DIVERGENCE_CONTINUATION** (total=47387): cvd_divergence_failed=19523, h1_trend_not_aligned=15170, basic_filters_failed=9350, ema_alignment_reject=2355, retest_proximity_failed=525, missing_cvd=338, missing_fvg_or_orderblock=126
- **EVAL::FAILED_AUCTION_RECLAIM** (total=48488): auction_not_detected=32543, basic_filters_failed=8763, regime_blocked=3075, reclaim_hold_failed=2576, tail_too_small=1473, rsi_reject=58
- **EVAL::FUNDING_EXTREME** (total=53788): funding_not_extreme=39738, basic_filters_failed=9106, missing_funding_rate=3637, ema_alignment_reject=837, rsi_reject=273, cvd_divergence_failed=104, momentum_reject=75, missing_fvg_or_orderblock=18
- **EVAL::LIQUIDATION_REVERSAL** (total=46414): cascade_threshold_not_met=35394, basic_filters_failed=10466, cvd_divergence_failed=234, rsi_reject=212, missing_cvd=91, missing_fvg_or_orderblock=16, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=49067): no_ma_cross=39044, basic_filters_failed=9362, ma_cross_htf_misaligned=329, ma_cross_cooldown=285, ma_cross_htf_unconfirmed=47
- **EVAL::MEAN_REVERT** (total=47307): no_extension=38810, basic_filters_failed=8497
- **EVAL::MOVER_AVWAP_SCALP** (total=70775): no_avwap_tag=30485, basic_filters_failed=14642, no_mover_leg=13230, avwap_slope_against=7128, avwap_reclaim_no_volume=3122, no_avwap_reclaim=2138, anchor_too_recent=30
- **EVAL::MOVER_TREND_PULLBACK** (total=55418): mover_run_too_small=22926, no_reclaim=15906, basic_filters_failed=14553, no_pullback_tag=2033
- **EVAL::OPENING_RANGE_BREAKOUT** (total=53530): feature_disabled=53530
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=48983): regime_blocked=35331, breakout_not_found=10981, basic_filters_failed=1602, adx_reject=1012, ema_alignment_reject=57
- **EVAL::QUIET_COMPRESSION_BREAK** (total=48690): compression_not_detected=21252, regime_blocked=16679, basic_filters_failed=7156, breakout_not_detected=3323, volume_confirmation_failed=273, missing_fvg_or_orderblock=4, rsi_reject=3
- **EVAL::RANGE_FADE** (total=48707): no_range_edge=40203, basic_filters_failed=8504
- **EVAL::SR_FLIP_RETEST** (total=48647): flip_close_not_confirmed=32667, basic_filters_failed=8751, regime_blocked=3054, long_break_volume_thin=1608, retest_out_of_zone=1292, h1_break_not_confirmed=735, reclaim_hold_failed=414, wick_quality_failed=52, whipsaw_flip=29, long_acceptance_not_held=21, ema_alignment_reject=17, missing_fvg_or_orderblock=7
- **EVAL::STANDARD** (total=39441): adx_reject=13172, momentum_reject=8042, basic_filters_failed=5217, sweeps_not_detected=4504, macd_reject=3720, ema_alignment_reject=3586, htf_poi_unanchored=1116, rsi_reject=51, invalid_sl_geometry=33
- **EVAL::TREND_PULLBACK** (total=41559): h1_trend_not_aligned=16518, ema_alignment_reject=6648, basic_filters_failed=4985, ema_not_tested_prev=3450, h1_pullback_not_confirmed=3381, no_ema_reclaim_close=2853, body_conviction_fail=1415, rsi_reject=910, prev_already_above_emas=636, no_prev_high_break=347, prev_already_below_emas=171, momentum_flat=106, no_prev_low_break=89, ema21_not_tagged=35, missing_fvg_or_orderblock=8, momentum_reject=7
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=63450): breakout_not_found=37029, basic_filters_failed=14453, move_not_fresh=7124, breakout_stale=3185, retest_proximity_failed=1329, volume_spike_missing=279, move_exhausted=38, missing_fvg_or_orderblock=13
- **EVAL::WHALE_MOMENTUM** (total=46435): momentum_reject=34456, recent_ticks_insufficient=8549, basic_filters_failed=3430

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=11): execution:overextended=11
- **DIVERGENCE_CONTINUATION** (total=135): setup_compat:regime_VOLATILE_UNSUITABLE=135
- **FAILED_AUCTION_RECLAIM** (total=1075): execution:overextended=593, setup_compat:regime_STRONG_TREND=445, context_floor=24, setup_compat:regime_VOLATILE_UNSUITABLE=13
- **FUNDING_EXTREME_SIGNAL** (total=577): execution:trigger_not_confirmed=577
- **LIQUIDATION_REVERSAL** (total=11): execution:trigger_not_confirmed=11
- **LIQUIDITY_SWEEP_REVERSAL** (total=4267): execution:overextended=1581, setup_compat:regime_STRONG_TREND=1436, execution:trigger_not_confirmed=1250
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_DIRTY_RANGE=4, execution:overextended=3, execution:trigger_not_confirmed=1, setup_compat:regime_CLEAN_RANGE=1
- **MEAN_REVERT** (total=5131): setup_compat:regime_STRONG_TREND=2335, setup_compat:regime_WEAK_TREND=2132, execution:overextended=663, entry_quality=1
- **MOVER_AVWAP_SCALP** (total=1572): execution:overextended=1043, execution:trigger_not_confirmed=467, entry_quality=62
- **MOVER_TREND_PULLBACK** (total=14339): execution:trigger_not_confirmed=8435, execution:overextended=5143, entry_quality=761
- **QUIET_COMPRESSION_BREAK** (total=13): execution:trigger_not_confirmed=13
- **RANGE_FADE** (total=2322): setup_compat:regime_WEAK_TREND=1054, setup_compat:regime_STRONG_TREND=943, execution:overextended=222, setup_compat:regime_VOLATILE_UNSUITABLE=85, setup_compat:regime_BREAKOUT_EXPANSION=18
- **TREND_PULLBACK_EMA** (total=1524): setup_compat:regime_CLEAN_RANGE=902, setup_compat:regime_DIRTY_RANGE=491, setup_compat:regime_VOLATILE_UNSUITABLE=110, entry_quality=21
- **VOLUME_SURGE_BREAKOUT** (total=12): execution:overextended=12

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 159276 | 46.7% |
| TRENDING_UP | 59491 | 17.4% |
| QUIET | 54564 | 16.0% |
| TRENDING_DOWN | 46236 | 13.6% |
| VOLATILE | 21638 | 6.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **90**
- Average confidence gap to threshold: **9.29** (samples=90) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITUSDT=15, XRPUSDT=13, LINKUSDT=9, ZILUSDT=8, UNIUSDT=6, ETHUSDT=6, FILUSDT=5, 1000SHIBUSDT=5, ASTERUSDT=5, 1000PEPEUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 8 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 14 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 13 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 23 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 8 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 21 |
| MEAN_REVERT | filtered | min_confidence | 3 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 3 |
| MEAN_REVERT | kept | min_confidence_pass | 8 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 99 |
| MOVER_AVWAP_SCALP | filtered | execution_component_floor | 29 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 117 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 483 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 49 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1494 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 53 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 29 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 10 |
| SR_FLIP_RETEST | filtered | min_confidence | 45 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 6 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 4 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 17 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 24 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 77.77 | 65.00 | -12.77 | 19.89 | 19.46 | 20.00 | 4.38 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 14 | 53.99 | 65.00 | 11.01 | 20.74 | 19.11 | 15.99 | 3.57 | 13.57 |
| DIVERGENCE_CONTINUATION | kept | 13 | 72.58 | 65.00 | -7.58 | 20.06 | 19.22 | 18.62 | 2.77 | -2.63 |
| FAILED_AUCTION_RECLAIM | filtered | 23 | 55.17 | 63.30 | 8.13 | 20.40 | 17.17 | 20.00 | 2.26 | 5.48 |
| FAILED_AUCTION_RECLAIM | kept | 8 | 64.89 | 65.00 | 0.11 | 21.02 | 19.20 | 20.00 | 1.69 | 2.62 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 43.16 | 62.18 | 19.02 | 18.69 | 17.35 | 17.00 | 3.24 | 12.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 61.90 | 65.00 | 3.10 | 21.20 | 19.70 | 17.00 | 0.00 | 3.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 67.94 | 65.00 | -2.94 | 20.87 | 19.80 | 17.60 | 1.29 | 0.00 |
| MEAN_REVERT | filtered | 6 | 53.30 | 65.00 | 11.70 | 22.63 | 17.10 | 14.45 | 0.00 | 22.35 |
| MEAN_REVERT | kept | 8 | 64.55 | 65.00 | 0.45 | 20.56 | 14.34 | 18.45 | 0.00 | 11.40 |
| MOVER_AVWAP_SCALP | filtered | 128 | 62.37 | 52.38 | -9.99 | 20.15 | 13.55 | 15.80 | 4.12 | 16.52 |
| MOVER_AVWAP_SCALP | kept | 117 | 81.06 | 65.00 | -16.06 | 19.53 | 15.29 | 15.80 | 4.08 | 2.12 |
| MOVER_TREND_PULLBACK | filtered | 532 | 55.87 | 64.24 | 8.37 | 20.42 | 18.64 | 15.80 | 3.85 | 19.98 |
| MOVER_TREND_PULLBACK | kept | 1494 | 75.50 | 65.00 | -10.50 | 20.46 | 18.55 | 15.80 | 4.22 | 1.64 |
| QUIET_COMPRESSION_BREAK | filtered | 82 | 55.31 | 65.00 | 9.69 | 20.85 | 19.34 | 20.00 | 0.00 | 5.63 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 75.75 | 65.00 | -10.75 | 20.25 | 19.32 | 20.00 | 0.00 | 3.41 |
| SR_FLIP_RETEST | filtered | 48 | 52.17 | 63.58 | 11.41 | 21.56 | 20.00 | 18.65 | 2.22 | 19.90 |
| SR_FLIP_RETEST | kept | 6 | 65.25 | 65.00 | -0.25 | 20.10 | 20.00 | 16.65 | 2.00 | 2.08 |
| TREND_PULLBACK_EMA | filtered | 10 | 60.98 | 65.00 | 4.02 | 20.57 | 19.20 | 18.12 | 5.20 | 10.14 |
| TREND_PULLBACK_EMA | kept | 17 | 77.22 | 65.00 | -12.22 | 21.11 | 19.62 | 18.44 | 4.88 | -1.79 |
| VOLUME_SURGE_BREAKOUT | filtered | 24 | 53.76 | 62.83 | 9.07 | 19.71 | 18.20 | 20.00 | 4.62 | 21.33 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.00 | 65.00 | -8.00 | 18.90 | 18.30 | 20.00 | 4.00 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 77.77 | 17.00 | 17.00 | 14.62 | 14.00 | 5.00 | 8.77 | 4.38 |
| DIVERGENCE_CONTINUATION | filtered | 14 | 53.99 | 19.29 | 15.14 | 3.86 | 12.29 | 5.00 | 8.41 | 3.57 |
| DIVERGENCE_CONTINUATION | kept | 13 | 72.58 | 19.46 | 14.92 | 8.31 | 13.92 | 5.00 | 8.34 | 2.77 |
| FAILED_AUCTION_RECLAIM | filtered | 23 | 55.17 | 19.09 | 18.00 | 3.78 | 12.91 | 5.96 | 5.83 | 2.26 |
| FAILED_AUCTION_RECLAIM | kept | 8 | 64.89 | 19.00 | 17.50 | 3.75 | 13.75 | 6.44 | 5.76 | 1.69 |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 43.16 | 18.41 | 18.12 | 4.76 | 15.12 | 6.44 | 4.07 | 3.24 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 61.90 | 17.00 | 14.00 | 9.00 | 14.00 | 5.00 | 6.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 67.94 | 21.95 | 15.71 | 5.43 | 12.33 | 5.33 | 6.04 | 1.29 |
| MEAN_REVERT | filtered | 6 | 53.30 | 17.00 | 18.00 | 15.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MEAN_REVERT | kept | 8 | 64.55 | 23.00 | 15.00 | 12.75 | 13.00 | 5.00 | 7.20 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 128 | 62.37 | 19.31 | 18.12 | 11.79 | 13.09 | 6.88 | 5.92 | 4.12 |
| MOVER_AVWAP_SCALP | kept | 117 | 81.06 | 18.15 | 18.10 | 13.51 | 14.07 | 7.29 | 8.39 | 4.08 |
| MOVER_TREND_PULLBACK | filtered | 532 | 55.87 | 18.33 | 18.00 | 7.65 | 12.59 | 6.82 | 8.64 | 3.85 |
| MOVER_TREND_PULLBACK | kept | 1494 | 75.50 | 19.05 | 18.02 | 7.98 | 13.01 | 6.36 | 8.59 | 4.22 |
| QUIET_COMPRESSION_BREAK | filtered | 82 | 55.31 | 21.00 | 15.41 | 10.54 | 14.15 | 6.01 | 5.39 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 75.75 | 20.20 | 16.80 | 13.20 | 14.00 | 6.15 | 9.11 | 0.00 |
| SR_FLIP_RETEST | filtered | 48 | 52.17 | 23.50 | 17.38 | 3.12 | 13.88 | 5.00 | 6.97 | 2.22 |
| SR_FLIP_RETEST | kept | 6 | 65.25 | 22.33 | 13.00 | 4.50 | 13.50 | 5.00 | 7.00 | 2.00 |
| TREND_PULLBACK_EMA | filtered | 10 | 60.98 | 12.60 | 18.00 | 7.50 | 14.00 | 6.40 | 7.42 | 5.20 |
| TREND_PULLBACK_EMA | kept | 17 | 77.22 | 16.71 | 18.00 | 7.68 | 14.18 | 7.68 | 9.14 | 4.88 |
| VOLUME_SURGE_BREAKOUT | filtered | 24 | 53.76 | 17.67 | 18.00 | 12.00 | 14.00 | 5.00 | 8.80 | 4.62 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 8 | 77.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 14 | 53.99 | 0.00 | 0.00 | 1.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.37** |
| DIVERGENCE_CONTINUATION | kept | 13 | 72.58 | 0.00 | 0.00 | 0.37 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.37** |
| FAILED_AUCTION_RECLAIM | filtered | 23 | 55.17 | 0.00 | 0.00 | 0.00 | 0.00 | 1.57 | 0.00 | 0.00 | 0.00 | **1.57** |
| FAILED_AUCTION_RECLAIM | kept | 8 | 64.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 17 | 43.16 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 61.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 67.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 6 | 53.30 | 0.00 | 0.00 | 4.00 | 0.00 | 16.80 | 0.00 | 0.00 | 0.00 | **20.80** |
| MEAN_REVERT | kept | 8 | 64.55 | 0.00 | 0.00 | 0.00 | 0.00 | 11.40 | 0.00 | 0.00 | 0.00 | **11.40** |
| MOVER_AVWAP_SCALP | filtered | 128 | 62.37 | 0.00 | 0.00 | 0.25 | 0.00 | 0.38 | 0.00 | 0.00 | 2.79 | **3.42** |
| MOVER_AVWAP_SCALP | kept | 117 | 81.06 | 0.00 | 0.00 | 1.01 | 0.00 | 0.10 | 0.09 | 0.00 | 0.57 | **1.77** |
| MOVER_TREND_PULLBACK | filtered | 532 | 55.87 | 0.00 | 0.00 | 1.57 | 0.00 | 0.98 | 0.00 | 0.00 | 0.00 | **2.55** |
| MOVER_TREND_PULLBACK | kept | 1494 | 75.50 | 0.00 | 0.00 | 0.46 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | **0.77** |
| QUIET_COMPRESSION_BREAK | filtered | 82 | 55.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 2.37 | **2.68** |
| QUIET_COMPRESSION_BREAK | kept | 10 | 75.75 | 0.00 | 0.00 | 1.44 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **2.30** |
| SR_FLIP_RETEST | filtered | 48 | 52.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 6 | 65.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 10 | 60.98 | 0.00 | 0.00 | 10.56 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **10.56** |
| TREND_PULLBACK_EMA | kept | 17 | 77.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 24 | 53.76 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 73.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **105535 held of 274679 seen** across 21 strategies; 2412 cells past the sample floor; **1068 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 37293 | 610/36683/0 | 44% | -0.16 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.16R) |
| MOVER_AVWAP_SCALP | 13098 | 181/12917/0 | 41% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | OVERLAP/MARKUP/EXPANDED/BTC_FALLING (-1.32R) |
| FAILED_AUCTION_RECLAIM | 8147 | 106/8041/0 | 41% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6468 | 34/6434/0 | 51% | -0.01 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5715 | 0/0/5715 | 42% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.84R) |
| TREND_PULLBACK_EMA | 5230 | 24/5206/0 | 45% | -0.16 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 4887 | 0/0/4887 | 37% | -0.10 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.70R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.21R) |
| QUIET_COMPRESSION_BREAK | 4648 | 284/4364/0 | 45% | -0.14 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4469 | 0/0/4469 | 34% | -0.40 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (-0.01R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3211 | 63/3148/0 | 36% | -0.38 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2169 | 24/2145/0 | 49% | -0.14 | LONDON/MARKDOWN/EXPANDED/BTC_RISING (+1.23R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1837 | 2/1835/0 | 34% | -0.40 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1650 | 0/1650/0 | 41% | -0.02 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1184 | 10/1174/0 | 48% | -0.22 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 807 | 0/0/807 | 54% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.15R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-0.51R) |
| RANGE_FADE | 717 | 0/717/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 362 | 35/327/0 | 41% | -0.14 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.03R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 60 | 6/54/0 | 43% | -0.09 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 142 | 28% / -0.54R | 142 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 422 | 45% / -0.21R | 422 | 54% / -0.04R | +0.17 | **ATR** |
| MOVER_AVWAP_SCALP | 1031 | 44% / -0.19R | 1031 | 50% / -0.08R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 131 | 50% / -0.26R | 131 | 51% / -0.17R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5721 | 50% / -0.09R | 5721 | 55% / -0.01R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 734 | 43% / -0.18R | 734 | 45% / -0.10R | +0.08 | **ATR** |
| BREAKDOWN_SHORT | 32 | 34% / -0.19R | 32 | 38% / -0.11R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 629 | 50% / -0.20R | 629 | 55% / -0.14R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 19 | 37% / -0.21R | 19 | 37% / -0.16R | +0.05 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 95 | 39% / -0.10R | 95 | 46% / -0.07R | +0.04 | **ATR** |
| RANGE_FADE | 35 | 40% / -0.19R | 35 | 43% / -0.22R | -0.03 | **FIXED** |
| DIVERGENCE_CONTINUATION | 619 | 51% / -0.08R | 619 | 56% / -0.05R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 770 | 46% / -0.15R | 770 | 46% / -0.16R | -0.01 | **FIXED** |
| MEAN_REVERT | 153 | 53% / -0.07R | 153 | 51% / -0.07R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8273 | 29% | -0.18R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1031 | 48% | -0.08R | 191 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 61 | 51% | -0.05R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 745 | 36% / -0.10R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7352 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1377 | 35% / -0.10R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 586 | 35% / -0.11R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 699 | 41% / +0.01R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 569 | 38% / -0.04R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 624 | 42% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 131 | 27% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 185 | 31% / -0.57R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 126 | 55% / +0.10R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 57 | 39% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 27 | 37% / +0.17R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 134 | 36% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 28 | 14% / -0.53R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×232]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 278/6) (sustained 278 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.58R (bound 0.3) (streak 1025/6) (sustained 1025 cycles)
- **ALERT** `tuned_variants` — 409 non-stamps — atr_arm_uncomputable=409 (seen=7743 stamped=1246 skipped=6088) (streak 971/6) (sustained 971 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 1025/3) (sustained 1025 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 45 fed / 0 quiet / 0 never delivered of 45 subscribed; 579835171 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 1025/3) | 1025 |
| ai_governor_live_arms | ok | 18 arms current, none stalled; covering 598/598 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +1 / upstream +1 | 0 |
| atr_trail_live_arms | ok | 40 arms current, none stalled; covering 1188/1188 signals (100%) | 0 |
| auto_dispatch | ok | 154 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=257, mode:off=51. No user is on live. | 0 |
| btc_reference | ok | BTC ref 81300.00 | 0 |
| candle_coverage | ok | 91/91 symbols with ≥20 15m candles, 91/91 updated within 45m [fresh=91; 78 Tier-1 futures + 14 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1355 dup bars, 0 undedupable; ws 0 out-of-order, 600 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +20 / upstream +14 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1530/1547 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 120 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1522/1539 signals (99%) | 0 |
| depth_feed | ok | 45/45 books fresh (stale 0, never 0, thin 0); 98214639 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.58R (bound 0.3) (streak 1025/6) | 1025 |
| emission_controller | ok | last cycle 334s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×232]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 278/6) | 278 |
| entry_quality_effective | ok | 8717 evaluated, 2946 suppressed, 4644 shadow-rejected; live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned | 0 |
| footprint_bars | ok | 5350 sealed bars over 45 symbols; 1797 incomplete, 7 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +2 / upstream +96 | 0 |
| indicator_cache_key | ok | 441864 frozen value(s) avoided; 1888629 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.14R over n=2145 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +9 / upstream +96 | 0 |
| mover_admission_metadata | ok | 905 symbols known, 199 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 14 held, 14 with scan counts, 14 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1621373 evicted (sampled: execution:trigger_not_confirmed 400/597606, execution:overextended 400/535242, setup_compat:regime_STRONG_TREND 400/239207) | 0 |
| price_action_lane | ok | 1763629 evaluated, 2642 emitted; layer1 2642 stamped / 0 blind; cooldown=235189, delta_opposed=149803, no_footprint=746680, no_levels=249, no_opposing_target=5941, no_sweep=489353, rr_below_floor=133772 | 0 |
| promoted_pair_integrity | ok | 14/14 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=717 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +11 / upstream +96 | 0 |
| sar_alignment_crosscheck | ok | 1024/33965 disagreed (3.0%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +96 | 0 |
| sar_hold_arm | ok | 1841 held arms settled, 160 unscored, 35 still walking (33 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/22 unfetchable (9%); top cause: located bar does not contain the stamp; symbols: B2USDT, FLOCKUSDT | 0 |
| sar_live_arms | ok | 36 arms current, none stalled; covering 1188/1188 signals (100%) | 0 |
| sar_refresh_budget | ok | 4 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 19 still mid-window | 0 |
| scan_cycle | ok | last 24.16s, worst 175.38s over 20048 lifetime cycles; lifetime 277 over 60s, 6 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 9.3s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 849912 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 2m ago | 0 |
| snapshot_writer | ok | last cycle 9s ago (1.14s to run, worst 90.86s), 1887 overrun(s) of 19845 cycles, TTL 900s; slowest activity=7.61s, signals=0.93s, alerts=0.55s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=687, gate reads=0, withheld=687) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +17 / upstream +96 | 0 |
| structural_snap | ok | 5351/5351 measured, 22 blind, 0 levels moved (refusals: redetect_cooldown=626) | 0 |
| structural_veto_lane | ok | 1679 stamped; 0 with no readable level book, 23 with clear air ahead, 1254 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +96 / upstream +14 | 0 |
| tuned_variants | violating | 409 non-stamps — atr_arm_uncomputable=409 (seen=7743 stamped=1246 skipped=6088) (streak 971/6) | 971 |

Fail-open exception counters (nonzero sites):
- `feature_liveness.probe.footprint_bars`: 1 — last: RuntimeError: deque mutated during iteration
- `llm_client.google`: 6 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1596046`
- `Path funnel` emissions: `38`
- `Regime distribution` emissions: `38`
- `QUIET_SCALP_BLOCK` events: `90`
- `confidence_gate` events: `2591`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **66**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_aggtrade | 58 | 7710 | 16739 | 23924 | 0 |
| futures_depth | 4 | 2444 | 3035 | 10764 | 0 |
| futures_liq | 3 | 2658 | 2658 | 12707 | 0 |
| futures_mover | 1 | 1991 | 1991 | 1991 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[absent=2043, present=282416] state[empty=2043, populated=282416] buckets[few=5, many=282385, none=2043, some=26] sources[none] quality[none]
- funding_rate: presence[absent=37813, present=246646] state[empty=37813, populated=246646] buckets[few=246646, none=37813] sources[none] quality[none]
- liquidation_clusters: presence[absent=154816, present=129643] state[empty=154816, populated=129643] buckets[few=103533, none=154816, some=26110] sources[none] quality[none]
- oi_snapshot: presence[absent=37813, present=246646] state[empty=37813, populated=246646] buckets[few=416, many=244066, none=37813, some=2164] sources[none] quality[none]
- order_book: presence[absent=101852, present=182607] state[populated=182607, unavailable=101852] buckets[few=182607, none=101852] sources[book_ticker=182607, unavailable=101852] quality[none=101852, top_of_book_only=182607]
- orderblocks: presence[absent=284459] state[empty=284459] buckets[none=284459] sources[measured_dark=284459] quality[none]
- recent_ticks: presence[present=284459] state[populated=284459] buckets[many=284459] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.4526050090789795` sec
- Median create→first breach: `3732.717454433441` sec
- Median create→terminal: `3732.868932366371` sec
- Median first breach→terminal: `6.29425048828125e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 1.8720032949967664 | 3.0 | 0.6240010983322555 | 0 | 2 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.800000000000005 | 1.5188349335869231 | 0.5267195152739229 | 0 | 1 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 1.3331801128489515 | 1.583220568335586 | 0.8680262166204843 | 0 | 3 |
| MEAN_REVERT | 2 | 2 | 1.732373227248066 | 1.6288681519695885 | 1.9960982439150377 | 1 | 1 |
| MOVER_AVWAP_SCALP | 3 | 3 | 2.2419368990242257 | 2.5575959332545817 | 0.9258187209548923 | 1 | 2 |
| MOVER_TREND_PULLBACK | 34 | 34 | 3.710975469471686 | 3.0 | 1.2703309251484876 | 25 | 8 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 1.2219382548353537 | 1.2219382548317115 | 0.8794723858452933 | 0 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 1.9293 | 4899.295313954353 | 4899.430755376816 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.0364 | 11640.15939617157 | 11640.4645819664 |
| FAILED_AUCTION_RECLAIM | 3 | 3 | 66.7 | 33.3 | 66.7 | 0.0 | 0.6672 | 6671.851008892059 | 6671.851029872894 |
| MEAN_REVERT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | -0.8913 | 10195.465359568596 | 10195.626262068748 |
| MOVER_AVWAP_SCALP | 3 | 3 | 33.3 | 33.3 | 33.3 | 0.0 | 0.5823 | 5514.906801939011 | 5515.200688838959 |
| MOVER_TREND_PULLBACK | 34 | 34 | 29.4 | 47.1 | 29.4 | 0.0 | -0.087 | 2743.1947840452194 | 2743.3446530103683 |
| QUIET_COMPRESSION_BREAK | 5 | 5 | 0.0 | 40.0 | 0.0 | 0.0 | -0.3304 | 17477.053722143173 | 17477.053746938705 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 573 | 4 | 484 | 0.0 | 0.0 | None | None | 89 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1822 | 11 | 1746 | 0.0 | 0.0 | None | None | 76 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `12`
- Gating Δ: `-17193`
- No-generation Δ: `-33840`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.4095, "current_avg_pnl": 0.6672, "current_win_rate": 66.7, "previous_avg_pnl": 2.0767, "previous_win_rate": 100.0, "win_rate_delta": -33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -1.7051, "current_avg_pnl": 0.5823, "current_win_rate": 33.3, "previous_avg_pnl": 2.2874, "previous_win_rate": 80.0, "win_rate_delta": -46.7}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.5971, "current_avg_pnl": -0.087, "current_win_rate": 29.4, "previous_avg_pnl": -0.6841, "previous_win_rate": 25.9, "win_rate_delta": 3.5}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.6445, "current_avg_pnl": -0.3304, "current_win_rate": 0.0, "previous_avg_pnl": -0.9749, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 24, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": 13, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **FAILED_AUCTION_RECLAIM**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
