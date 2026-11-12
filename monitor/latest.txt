# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, MOVER_AVWAP_SCALP, QUIET_COMPRESSION_BREAK
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `2781` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 7841 | 7841 | 6809 | 21 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 48471 | 48498 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 50096 | 50097 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 49672 | 47569 | 2509 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50116 | 49443 | 759 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 49607 | 49582 | 54 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 41638 | 41651 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50210 | 50244 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 50261 | 49233 | 1661 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 51705 | 56556 | 357 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 48500 | 45372 | 6288 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 49265 | 49266 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50099 | 50106 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 49643 | 49590 | 72 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 50901 | 49546 | 1895 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 49270 | 49493 | 106 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 41233 | 38643 | 2892 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 41541 | 41196 | 438 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 48427 | 48462 | 6 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 41653 | 41694 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2839 | 2839 | 2532 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 343 | 343 | 149 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 5 | 5 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13059 | 13059 | 12999 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 19 | 19 | 6 | 7 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 3923 | 3923 | 3103 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 817 | 817 | 151 | 52 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18536 | 18536 | 6987 | 353 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 377 | 377 | 127 | 37 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4676 | 4676 | 3926 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 450 | 450 | 174 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1814 | 1814 | 1472 | 45 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 15 | 15 | 2 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=48498): breakout_not_found=26053, basic_filters_failed=12419, move_not_fresh=7329, breakout_stale=2182, retest_proximity_failed=422, volume_spike_missing=88, move_exhausted=4, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=50097): cls_disabled_merged_into_lsr=50097
- **EVAL::DIVERGENCE_CONTINUATION** (total=47569): cvd_divergence_failed=19854, h1_trend_not_aligned=12728, basic_filters_failed=10651, ema_alignment_reject=3802, retest_proximity_failed=300, missing_fvg_or_orderblock=234
- **EVAL::FAILED_AUCTION_RECLAIM** (total=49443): auction_not_detected=32856, basic_filters_failed=10459, reclaim_hold_failed=3007, tail_too_small=2058, regime_blocked=1054, rsi_reject=9
- **EVAL::FUNDING_EXTREME** (total=49582): funding_not_extreme=37627, basic_filters_failed=10630, ema_alignment_reject=803, rsi_reject=366, cvd_divergence_failed=63, momentum_reject=63, missing_funding_rate=22, missing_fvg_or_orderblock=8
- **EVAL::LIQUIDATION_REVERSAL** (total=41651): cascade_threshold_not_met=31003, basic_filters_failed=10441, rsi_reject=106, cvd_divergence_failed=87, missing_fvg_or_orderblock=8, volume_spike_missing=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50244): no_ma_cross=38454, basic_filters_failed=10665, ma_cross_htf_misaligned=622, ma_cross_cooldown=503
- **EVAL::MEAN_REVERT** (total=49233): no_extension=42977, basic_filters_failed=6256
- **EVAL::MOVER_AVWAP_SCALP** (total=56556): no_avwap_tag=24492, no_mover_leg=14299, basic_filters_failed=12600, avwap_slope_against=2688, avwap_reclaim_no_volume=1549, no_avwap_reclaim=921, anchor_too_recent=7
- **EVAL::MOVER_TREND_PULLBACK** (total=45372): mover_run_too_small=25995, basic_filters_failed=12516, no_reclaim=5794, no_pullback_tag=1067
- **EVAL::OPENING_RANGE_BREAKOUT** (total=49266): feature_disabled=49266
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50106): regime_blocked=40670, breakout_not_found=6679, basic_filters_failed=1391, adx_reject=1332, ema_alignment_reject=34
- **EVAL::QUIET_COMPRESSION_BREAK** (total=49590): compression_not_detected=25638, regime_blocked=10427, basic_filters_failed=9053, breakout_not_detected=4002, volume_confirmation_failed=462, rsi_reject=5, missing_fvg_or_orderblock=3
- **EVAL::RANGE_FADE** (total=49546): no_range_edge=43284, basic_filters_failed=6262
- **EVAL::SR_FLIP_RETEST** (total=49493): flip_close_not_confirmed=33622, basic_filters_failed=10436, h1_break_not_confirmed=1408, long_break_volume_thin=1355, regime_blocked=1040, retest_out_of_zone=970, reclaim_hold_failed=462, ema_alignment_reject=69, wick_quality_failed=69, long_acceptance_not_held=48, missing_fvg_or_orderblock=14
- **EVAL::STANDARD** (total=38643): adx_reject=12615, momentum_reject=11687, basic_filters_failed=4202, macd_reject=4068, sweeps_not_detected=3947, ema_alignment_reject=1367, htf_poi_unanchored=634, rsi_reject=63, invalid_sl_geometry=60
- **EVAL::TREND_PULLBACK** (total=41196): h1_trend_not_aligned=13143, basic_filters_failed=7051, ema_alignment_reject=6491, h1_pullback_not_confirmed=4107, no_ema_reclaim_close=3228, ema_not_tested_prev=2582, body_conviction_fail=1878, rsi_reject=1399, prev_already_below_emas=493, no_prev_low_break=285, prev_already_above_emas=199, no_prev_high_break=160, momentum_flat=117, momentum_reject=22, ema21_not_tagged=21, missing_fvg_or_orderblock=20
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=48462): breakout_not_found=29447, basic_filters_failed=12414, move_not_fresh=4178, breakout_stale=1948, retest_proximity_failed=379, volume_spike_missing=65, missing_fvg_or_orderblock=28, move_exhausted=3
- **EVAL::WHALE_MOMENTUM** (total=41694): momentum_reject=23998, recent_ticks_insufficient=13803, basic_filters_failed=3893

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=163): setup_compat:regime_VOLATILE_UNSUITABLE=163
- **FAILED_AUCTION_RECLAIM** (total=667): execution:overextended=319, setup_compat:regime_STRONG_TREND=185, context_floor=141, setup_compat:regime_VOLATILE_UNSUITABLE=22
- **FUNDING_EXTREME_SIGNAL** (total=295): execution:trigger_not_confirmed=258, context_floor=37
- **LIQUIDATION_REVERSAL** (total=5): execution:trigger_not_confirmed=5
- **LIQUIDITY_SWEEP_REVERSAL** (total=2577): execution:trigger_not_confirmed=1193, execution:overextended=803, setup_compat:regime_STRONG_TREND=581
- **MA_CROSS_TREND_SHIFT** (total=19): setup_compat:regime_DIRTY_RANGE=10, setup_compat:regime_CLEAN_RANGE=3, execution:overextended=3, execution:trigger_not_confirmed=2, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **MEAN_REVERT** (total=1606): setup_compat:regime_WEAK_TREND=724, setup_compat:regime_STRONG_TREND=625, execution:overextended=231, entry_quality=26
- **MOVER_AVWAP_SCALP** (total=403): execution:overextended=239, execution:trigger_not_confirmed=85, entry_quality=79
- **MOVER_TREND_PULLBACK** (total=7542): execution:trigger_not_confirmed=3604, execution:overextended=2409, entry_quality=1529
- **RANGE_FADE** (total=2388): setup_compat:regime_WEAK_TREND=809, setup_compat:regime_STRONG_TREND=728, execution:overextended=586, setup_compat:regime_VOLATILE_UNSUITABLE=224, context_edge=25, setup_compat:regime_BREAKOUT_EXPANSION=16
- **TREND_PULLBACK_EMA** (total=1811): setup_compat:regime_CLEAN_RANGE=1155, setup_compat:regime_DIRTY_RANGE=494, entry_quality=96, setup_compat:regime_VOLATILE_UNSUITABLE=66
- **VOLUME_SURGE_BREAKOUT** (total=3): execution:overextended=3

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 145646 | 52.4% |
| QUIET | 60274 | 21.7% |
| TRENDING_DOWN | 36426 | 13.1% |
| TRENDING_UP | 23050 | 8.3% |
| VOLATILE | 12308 | 4.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **171**
- Average confidence gap to threshold: **15.08** (samples=171) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ARBUSDT=33, INJUSDT=20, CYBERUSDT=16, ONEUSDT=16, AAVEUSDT=14, ETHUSDT=8, SUIUSDT=7, XMRUSDT=6, ASTERUSDT=6, SOLUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 132 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 51 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 19 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 19 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 2 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 7 |
| MEAN_REVERT | filtered | min_confidence | 6 |
| MEAN_REVERT | kept | min_confidence_pass | 8 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 255 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 199 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2175 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 103 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3086 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 53 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 29 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 120 |
| SR_FLIP_RETEST | filtered | min_confidence | 53 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 10 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 9 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 32 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 10 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 84 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 10 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 137 | 54.21 | 64.62 | 10.41 | 20.64 | 19.73 | 16.92 | 1.08 | 14.81 |
| DIVERGENCE_CONTINUATION | kept | 51 | 68.19 | 65.00 | -3.19 | 20.63 | 19.75 | 18.35 | 1.53 | 0.92 |
| FAILED_AUCTION_RECLAIM | filtered | 32 | 40.15 | 62.03 | 21.88 | 20.38 | 17.92 | 20.00 | 2.52 | 17.42 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 69.85 | 65.00 | -4.85 | 20.80 | 17.95 | 20.00 | 4.25 | 13.00 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 65.88 | 65.00 | -0.88 | 20.25 | 16.65 | 17.75 | 2.50 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 20 | 42.95 | 64.60 | 21.65 | 19.86 | 18.20 | 18.58 | 1.15 | 17.77 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 70.80 | 65.00 | -5.80 | 20.15 | 19.70 | 18.90 | 1.00 | 4.00 |
| MA_CROSS_TREND_SHIFT | kept | 7 | 71.76 | 65.00 | -6.76 | 20.63 | 18.51 | 15.80 | 0.00 | 1.97 |
| MEAN_REVERT | filtered | 6 | 47.97 | 65.00 | 17.03 | 21.90 | 14.00 | 15.60 | 0.00 | 20.00 |
| MEAN_REVERT | kept | 8 | 74.55 | 65.00 | -9.55 | 17.34 | 14.00 | 15.64 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 255 | 52.84 | 64.46 | 11.62 | 20.26 | 16.16 | 15.80 | 3.92 | 21.10 |
| MOVER_AVWAP_SCALP | kept | 199 | 78.61 | 65.00 | -13.61 | 20.89 | 17.77 | 15.80 | 4.32 | 2.38 |
| MOVER_TREND_PULLBACK | filtered | 2278 | 55.40 | 64.12 | 8.72 | 20.55 | 18.65 | 15.80 | 3.86 | 20.26 |
| MOVER_TREND_PULLBACK | kept | 3086 | 75.99 | 65.00 | -10.99 | 20.59 | 18.49 | 15.80 | 4.18 | 2.11 |
| QUIET_COMPRESSION_BREAK | filtered | 82 | 49.54 | 64.70 | 15.16 | 20.69 | 18.82 | 20.00 | 0.00 | 11.21 |
| QUIET_COMPRESSION_BREAK | kept | 120 | 75.65 | 65.00 | -10.65 | 21.34 | 19.64 | 20.00 | 0.00 | 0.32 |
| SR_FLIP_RETEST | filtered | 63 | 59.58 | 65.00 | 5.42 | 20.74 | 20.00 | 15.53 | 2.17 | 15.76 |
| SR_FLIP_RETEST | kept | 9 | 71.60 | 65.00 | -6.60 | 20.64 | 20.00 | 17.81 | 2.28 | 6.79 |
| TREND_PULLBACK_EMA | filtered | 42 | 55.71 | 64.43 | 8.72 | 20.69 | 19.96 | 18.41 | 4.94 | 19.87 |
| TREND_PULLBACK_EMA | kept | 84 | 77.02 | 65.00 | -12.02 | 20.87 | 19.91 | 18.01 | 4.97 | 0.66 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 45.75 | 62.60 | 16.85 | 19.51 | 16.80 | 20.00 | 3.05 | 22.74 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 69.67 | 65.00 | -4.67 | 19.00 | 18.37 | 19.10 | 4.50 | 10.27 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 137 | 54.21 | 21.61 | 13.62 | 5.34 | 12.66 | 5.94 | 8.77 | 1.08 |
| DIVERGENCE_CONTINUATION | kept | 51 | 68.19 | 23.12 | 13.10 | 4.94 | 12.25 | 6.31 | 9.12 | 1.53 |
| FAILED_AUCTION_RECLAIM | filtered | 32 | 40.15 | 21.50 | 16.38 | 5.06 | 13.50 | 6.78 | 4.49 | 2.52 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 69.85 | 25.00 | 18.00 | 6.00 | 13.00 | 8.75 | 7.85 | 4.25 |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 65.88 | 19.00 | 11.00 | 6.75 | 13.00 | 8.38 | 7.75 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 20 | 42.95 | 20.70 | 14.00 | 8.40 | 14.75 | 5.38 | 6.10 | 1.15 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 70.80 | 21.00 | 16.00 | 10.50 | 12.00 | 5.00 | 9.30 | 1.00 |
| MA_CROSS_TREND_SHIFT | kept | 7 | 71.76 | 21.57 | 14.00 | 8.57 | 13.71 | 6.93 | 8.94 | 0.00 |
| MEAN_REVERT | filtered | 6 | 47.97 | 19.67 | 18.00 | 9.00 | 10.00 | 5.00 | 6.30 | 0.00 |
| MEAN_REVERT | kept | 8 | 74.55 | 21.25 | 14.00 | 15.00 | 13.00 | 5.00 | 6.30 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 255 | 52.84 | 17.89 | 18.01 | 12.80 | 13.54 | 5.66 | 7.01 | 3.92 |
| MOVER_AVWAP_SCALP | kept | 199 | 78.61 | 18.70 | 18.02 | 11.98 | 14.80 | 6.34 | 7.89 | 4.32 |
| MOVER_TREND_PULLBACK | filtered | 2278 | 55.40 | 18.34 | 18.01 | 7.83 | 12.04 | 6.23 | 9.35 | 3.86 |
| MOVER_TREND_PULLBACK | kept | 3086 | 75.99 | 19.36 | 18.04 | 7.83 | 13.04 | 6.46 | 9.24 | 4.18 |
| QUIET_COMPRESSION_BREAK | filtered | 82 | 49.54 | 20.22 | 15.41 | 11.05 | 14.18 | 7.20 | 4.21 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 120 | 75.65 | 19.80 | 17.13 | 11.85 | 14.12 | 6.37 | 8.14 | 0.00 |
| SR_FLIP_RETEST | filtered | 63 | 59.58 | 22.84 | 16.41 | 4.67 | 14.86 | 5.29 | 9.10 | 2.17 |
| SR_FLIP_RETEST | kept | 9 | 71.60 | 23.22 | 15.78 | 9.00 | 14.89 | 5.00 | 8.54 | 2.28 |
| TREND_PULLBACK_EMA | filtered | 42 | 55.71 | 18.17 | 18.05 | 7.61 | 14.07 | 5.96 | 8.93 | 4.94 |
| TREND_PULLBACK_EMA | kept | 84 | 77.02 | 18.83 | 18.02 | 7.77 | 14.43 | 6.14 | 8.61 | 4.97 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 45.75 | 17.00 | 14.40 | 12.00 | 14.00 | 5.00 | 4.54 | 3.05 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 69.67 | 19.67 | 16.67 | 13.00 | 14.00 | 5.00 | 7.10 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 137 | 54.21 | 0.00 | 0.00 | 1.44 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | **2.44** |
| DIVERGENCE_CONTINUATION | kept | 51 | 68.19 | 0.00 | 0.00 | 0.75 | 0.00 | 0.24 | 0.00 | 0.00 | 0.00 | **0.99** |
| FAILED_AUCTION_RECLAIM | filtered | 32 | 40.15 | 0.00 | 0.00 | 0.00 | 0.00 | 3.38 | 0.00 | 0.00 | 0.00 | **3.38** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 69.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 4 | 65.88 | 0.00 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 20 | 42.95 | 0.00 | 0.00 | 2.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | **3.20** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 70.80 | 0.00 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.00** |
| MA_CROSS_TREND_SHIFT | kept | 7 | 71.76 | 0.00 | 0.00 | 0.69 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.69** |
| MEAN_REVERT | filtered | 6 | 47.97 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 8 | 74.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 255 | 52.84 | 0.00 | 0.00 | 1.10 | 0.00 | 5.14 | 1.04 | 0.00 | 0.70 | **7.98** |
| MOVER_AVWAP_SCALP | kept | 199 | 78.61 | 0.08 | 0.00 | 0.59 | 0.00 | 0.24 | 0.21 | 0.00 | 0.08 | **1.20** |
| MOVER_TREND_PULLBACK | filtered | 2278 | 55.40 | 1.05 | 0.00 | 1.37 | 0.00 | 0.94 | 0.01 | 0.00 | 0.00 | **3.37** |
| MOVER_TREND_PULLBACK | kept | 3086 | 75.99 | 0.21 | 0.00 | 1.02 | 0.00 | 0.24 | 0.01 | 0.00 | 0.00 | **1.48** |
| QUIET_COMPRESSION_BREAK | filtered | 82 | 49.54 | 0.00 | 0.00 | 0.00 | 0.00 | 0.36 | 0.95 | 0.00 | 4.13 | **5.44** |
| QUIET_COMPRESSION_BREAK | kept | 120 | 75.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| SR_FLIP_RETEST | filtered | 63 | 59.58 | 0.00 | 0.00 | 3.53 | 0.00 | 0.76 | 0.00 | 0.00 | 0.34 | **4.63** |
| SR_FLIP_RETEST | kept | 9 | 71.60 | 0.00 | 0.00 | 0.53 | 0.00 | 5.33 | 0.00 | 0.00 | 0.00 | **5.86** |
| TREND_PULLBACK_EMA | filtered | 42 | 55.71 | 0.00 | 0.00 | 0.34 | 0.00 | 2.86 | 0.00 | 0.00 | 0.00 | **3.20** |
| TREND_PULLBACK_EMA | kept | 84 | 77.02 | 0.00 | 0.00 | 0.34 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.60** |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 45.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | **5.40** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 69.67 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.60** |

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
- Outcomes recorded: **184368 held of 824106 seen** across 21 strategies; 4174 cells past the sample floor; **2224 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 48203 | 630/47573/0 | 44% | -0.17 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | NY/QUIET/EXPANDED/BTC_FALLING/MAJOR (-1.26R) |
| MOVER_AVWAP_SCALP | 24556 | 209/24347/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| DIVERGENCE_CONTINUATION | 14376 | 221/14155/0 | 45% | -0.14 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP (+2.35R) | LONDON/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.19R) |
| FAILED_AUCTION_RECLAIM | 13919 | 153/13766/0 | 35% | -0.33 | OVERLAP/MARKDOWN/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.50R) | NY/MARKUP/EXPANDED/BTC_RISING/ALTCOIN (-1.21R) |
| TREND_PULLBACK_EMA | 12478 | 70/12408/0 | 38% | -0.30 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | NY/ACCUMULATION/EXPANDED/BTC_FALLING/MAJOR (-1.35R) |
| LIQUIDITY_SWEEP_REVERSAL | 10321 | 103/10218/0 | 37% | -0.43 | NY/MARKUP/COMPRESSED/BTC_FALLING (+1.99R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING (-1.81R) |
| QUIET_COMPRESSION_BREAK | 8745 | 423/8322/0 | 45% | -0.14 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.09R) |
| SHADOW_MEAN_REVERT | 8121 | 0/0/8121 | 44% | -0.07 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+1.28R) | LONDON/QUIET/COMPRESSED/BTC_RISING (-0.82R) |
| SHADOW_RANGE_FADE | 7609 | 0/0/7609 | 36% | -0.13 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.27R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_FUNDING_FADE | 7110 | 0/0/7110 | 34% | -0.41 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+0.00R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.97R) |
| SR_FLIP_RETEST | 6286 | 24/6262/0 | 47% | -0.25 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.68R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.30R) |
| MEAN_REVERT | 5479 | 67/5412/0 | 37% | -0.33 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.37R) |
| FUNDING_EXTREME_SIGNAL | 4089 | 2/4087/0 | 31% | -0.46 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| VOLUME_SURGE_BREAKOUT | 3873 | 0/3873/0 | 28% | -0.42 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL/MIDCAP (-1.19R) |
| WHALE_MOMENTUM | 3807 | 4/3803/0 | 45% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| RANGE_FADE | 2336 | 6/2330/0 | 42% | -0.11 | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL (+3.25R) | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.82R) |
| SHADOW_CASCADE_REVERSAL | 1693 | 0/0/1693 | 52% | -0.08 | ASIA/RANGE/EXPANDED/BTC_NEUTRAL (+0.17R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.66R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 532 | 0/532/0 | 36% | -0.24 | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL (+2.71R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 210 | 32/178/0 | 43% | -0.19 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 58 | 2/56/0 | 45% | +0.15 | — | — |

- **Strongest cells**: `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL` +3.25R (n=50, STRONG); `RANGE_FADE @ ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` +3.25R (n=50, STRONG); `LIQUIDATION_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL` +2.71R (n=23, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.82R (n=46, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING/MIDCAP` -1.81R (n=19, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_FALLING` -1.81R (n=19, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 371 | 27% / -0.57R | 371 | 53% / -0.09R | +0.48 | **ATR** |
| TREND_PULLBACK_EMA | 1230 | 38% / -0.38R | 1230 | 50% / -0.08R | +0.29 | **ATR** |
| LIQUIDATION_REVERSAL | 33 | 24% / -0.61R | 33 | 45% / -0.35R | +0.26 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1570 | 42% / -0.37R | 1570 | 57% / -0.12R | +0.25 | **ATR** |
| MA_CROSS_TREND_SHIFT | 64 | 42% / -0.22R | 64 | 47% / -0.06R | +0.15 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 215 | 38% / -0.18R | 215 | 48% / -0.04R | +0.14 | **ATR** |
| SR_FLIP_RETEST | 642 | 45% / -0.28R | 642 | 50% / -0.16R | +0.13 | **ATR** |
| MOVER_AVWAP_SCALP | 2616 | 44% / -0.17R | 2616 | 50% / -0.05R | +0.12 | **ATR** |
| MOVER_TREND_PULLBACK | 8896 | 48% / -0.14R | 8896 | 53% / -0.02R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1513 | 41% / -0.23R | 1513 | 43% / -0.12R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 437 | 44% / -0.32R | 437 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| RANGE_FADE | 131 | 39% / -0.08R | 131 | 46% / -0.00R | +0.07 | **ATR** |
| DIVERGENCE_CONTINUATION | 1800 | 48% / -0.12R | 1800 | 53% / -0.06R | +0.06 | **ATR** |
| MEAN_REVERT | 441 | 47% / -0.14R | 441 | 46% / -0.16R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1533 | 46% / -0.13R | 1533 | 46% / -0.14R | -0.01 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 13 | 62% / -0.06R | 13 | 62% / -0.08R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 11833 | 28% | -0.25R | 313 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 2616 | 48% | -0.05R | 239 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 138 | 50% | -0.04R | 68 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1836 | 39% / -0.15R | +0.86 | **SAR** |
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1591 | 33% / -0.22R | +0.84 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 3177 | 35% / -0.20R | +0.64 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 10834 | 36% / -0.20R | +0.33 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 2096 | 36% / -0.15R | +0.13 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 161 | 35% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1471 | 35% / -0.15R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 1260 | 32% / -0.28R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 318 | 31% / -0.37R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 481 | 32% / -0.22R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 366 | 48% / -0.07R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 94 | 45% / +0.02R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 564 | 34% / -0.31R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 101 | 28% / -0.37R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 42 | 45% / -0.20R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 22 | 45% / +0.62R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **3** · boot grace active: False
- **ALERT** `dark_resolution` — 3 of 142 open dark rows are not being advanced (worst: CLOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 151/120) (sustained 151 cycles)
- **ALERT** `edge_reconciliation` — BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 402/6) (sustained 402 cycles)
- **ALERT** `tuned_variants` — 416 non-stamps — atr_arm_uncomputable=416 (seen=9957 stamped=1320 skipped=8221) (streak 402/6) (sustained 402 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 187457216 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 22 arms current, none stalled; covering 2118/2118 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 45 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 7/12) | 7 |
| auto_dispatch | ok | 97 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: venue:coindcx=97. No user is on live on this (Binance) order path. | 0 |
| binance_ip_weight | ok | peak 104/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 73578.90 | 0 |
| candle_coverage | ok | 82/82 symbols with ≥20 15m candles, 82/82 updated within 45m [fresh=82; 76 Tier-1 futures + 6 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1497 dup bars, 0 undedupable; ws 0 out-of-order, 449 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 60 cohorts, 40 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | ok | output +21 / upstream +17 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1854/1873 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 3 of 142 open dark rows are not being advanced (worst: CLOUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 151/120) | 151 |
| dark_sar_arms | ok | no open arms; covering 1848/1867 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 58034908 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | BREAKDOWN_SHORT realized−counterfactual=+0.46R (bound 0.3) (streak 402/6) | 402 |
| emission_controller | ok | last cycle 1262s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 6000 stamps (MEAN_REVERT=494, MOVER_AVWAP_SCALP=309, MOVER_TREND_PULLBACK=4446, RANGE_FADE=434, TREND_PULLBACK_EMA=317), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct); 2 absent on every stamp for an ordinary reason — no previous leg (RANGE_FADE.campaign_prev_age_h,RANGE_FADE.campaign_prev_won) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=37, cvd_aligned=23, mover_stack_15m=10. Held back in this window: session_quality=24, cvd_aligned=4, mover_stack_15m=3. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 2/6) | 2 |
| firestore_read_budget | ok | 1,316 reads/day of 50,000 [engine 1,295, signing 21]; top site runtime_tunables.doc at 286/day (engine) | 0 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1959 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +6 / upstream +193 | 0 |
| indicator_cache_key | ok | 147176 frozen value(s) avoided; 360826 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.34R over n=5412 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +9 / upstream +193 | 0 |
| mover_admission_metadata | ok | 946 symbols known, 237 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 6 held, 6 with scan counts, 5 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 7 locked / 7 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2153 rows held, 3499789 evicted (sampled: execution:trigger_not_confirmed 290/1233164, execution:overextended 290/1089700, setup_compat:regime_STRONG_TREND 291/597669) | 0 |
| price_action_lane | ok | 679039 evaluated, 1408 emitted; layer1 1408 stamped / 0 blind; cooldown=114826, delta_opposed=63293, no_footprint=235806, no_opposing_target=1360, no_sweep=208569, rr_below_floor=53777 | 0 |
| promoted_pair_integrity | ok | 6/6 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.11R over n=2330 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +2 / upstream +193 | 0 |
| sar_alignment_crosscheck | ok | 557/25122 disagreed (2.2%) | 0 |
| sar_exit_shadow | ok | output +4 / upstream +193 | 0 |
| sar_hold_arm | ok | 1870 held arms settled, 130 unscored, 44 still walking (40 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/92 unfetchable (2%); top cause: located bar does not contain the stamp; symbols: HUMAUSDT, MAGMAUSDT | 0 |
| sar_live_arms | ok | 44 arms current, none stalled; covering 1119/1119 signals (100%) | 0 |
| sar_refresh_budget | ok | 10 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 5 resolved, 85 still mid-window | 0 |
| scan_cycle | ok | last 76.94s, worst 263.84s over 8695 lifetime cycles; lifetime 469 over 60s, 140 over 120s (plus 1/0 during boot warm-up, not counted); recent 1/0 warn/kill breaches in 20/20 cycles; heartbeat age 21.81s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 300908 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 22s ago (0.92s to run, worst 228.23s), 1513 overrun(s) of 7993 cycles, TTL 900s; slowest data_intake=0.22s, tickers=0.18s, signals=0.16s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +116 / upstream +193 | 0 |
| structural_snap | ok | 6000/6000 measured, 25 blind, 0 levels moved (refusals: redetect_cooldown=920) | 0 |
| structural_veto_lane | ok | 1977 stamped; 0 with no readable level book, 64 with clear air ahead, 1518 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +193 / upstream +17 | 0 |
| tuned_variants | violating | 416 non-stamps — atr_arm_uncomputable=416 (seen=9957 stamped=1320 skipped=8221) (streak 402/6) | 402 |
| unlock_shorts | ok | 17 open, 43 scheduled, calendar 10.5h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 52 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1420115`
- `Path funnel` emissions: `35`
- `Regime distribution` emissions: `35`
- `QUIET_SCALP_BLOCK` events: `171`
- `confidence_gate` events: `6500`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **39**
- Total REST-fallback activations: **7**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 7 | 36549 | 48038 | 61082 | 0 |
| futures_aggtrade | 14 | 11830 | 34509 | 41884 | 0 |
| futures_depth | 12 | 17562 | 54614 | 58179 | 0 |
| futures_liq | 1 | 12472 | 12472 | 12472 | 0 |
| futures_mover | 5 | 13569 | 13772 | 30104 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 7 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=209673] state[populated=209673] buckets[many=209673] sources[none] quality[none]
- funding_rate: presence[absent=13935, present=195738] state[empty=13935, populated=195738] buckets[few=195738, none=13935] sources[none] quality[none]
- liquidation_clusters: presence[absent=129673, present=80000] state[empty=129673, populated=80000] buckets[few=65026, none=129673, some=14974] sources[none] quality[none]
- oi_snapshot: presence[absent=13935, present=195738] state[empty=13935, populated=195738] buckets[few=232, many=194282, none=13935, some=1224] sources[none] quality[none]
- order_book: presence[absent=73115, present=136558] state[populated=136558, unavailable=73115] buckets[few=136558, none=73115] sources[book_ticker=136558, unavailable=73115] quality[none=73115, top_of_book_only=136558]
- orderblocks: presence[absent=209673] state[empty=209673] buckets[none=209673] sources[measured_dark=209673] quality[none]
- recent_ticks: presence[present=209673] state[populated=209673] buckets[many=209673] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.864422082901001` sec
- Median create→first breach: `4286.9353120327` sec
- Median create→terminal: `4286.935449838638` sec
- Median first breach→terminal: `8.106231689453125e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 2, "pct": 4.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.4}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Three stages then move it before it reaches the wire: ``build_risk_plan`` **replaces** stop and TP ladder with generic 5m structure geometry (1.3 / 2.3 / 3.4 R) **unless the setup is in ``STRUCTURAL_SLTP_PROTECTED_SETUPS`` — the two mover paths are not**; ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``; and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band without moving the targets.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 1.0012791150100504 | 1.1831644194871072 | 0.8513814158409185 | 0 | 2 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.0294710515510122 | 1.162295300226335 | 0.8857224591293987 | 0 | 1 |
| MOVER_AVWAP_SCALP | 9 | 9 | 1.5507158168697495 | 1.833430694466208 | 0.8422726425897874 | 2 | 6 |
| MOVER_TREND_PULLBACK | 22 | 22 | 4.547100290921321 | 3.0 | 1.515700096973774 | 19 | 3 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.3888292456341393 | 1.6396317023370564 | 0.8602135391571141 | 0 | 6 |

### TP1 — authored vs shipped
_The same comparison for the first target.  ``Nearer`` = the evaluator's TP1 sat closer than the one that shipped; of those, ``Reached`` had MFE ≥ the authored distance and ``Rescued`` cleared the authored target but **not** the shipped one — trades that would have banked TP1 and did not.  ``Farther / undecidable`` rows closed at the shipped TP1 before the authored one, so the record cannot say whether they would have gone on; no figure is drawn from them.  MFE is tick-sampled, so ``Reached`` under-counts and never invents a touch.  This counts touches, **not PnL**: the authored stop differs too, and that half is not decidable here.  Rows closed before 2026-11-10 carry no authored-TP1 stamp and are excluded, not averaged in._
| Path/Setup | Stamped | Authored TP1 % | Shipped TP1 % | Nearer | Reached | Rescued | Farther | Farther / undecidable | Same |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 1.9510289004558716 | 1.5019176500201823 | 0 | 0 | 0 | 2 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 1 | 1.8551084400313507 | 1.544215909515098 | 0 | 0 | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 9 | 2.2085339375058988 | 2.2665419648666227 | 4 | 3 | 2 | 3 | 0 | 2 |
| MOVER_TREND_PULLBACK | 22 | 5.208817160512224 | 4.007835000000004 | 7 | 1 | 1 | 15 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 7 | 4.335721066914396 | 2.0832438684512007 | 0 | 0 | 0 | 6 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0013 | 3208.1658425331116 | 3208.1659449338913 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.5442 | 1825.922914981842 | 1831.4747250080109 |
| MOVER_AVWAP_SCALP | 9 | 9 | 11.1 | 22.2 | 11.1 | 0.0 | -0.0658 | 9834.73752784729 | 9834.737608909607 |
| MOVER_TREND_PULLBACK | 22 | 22 | 27.3 | 36.4 | 27.3 | 0.0 | 0.8571 | 2823.9066029787064 | 2828.9389219284058 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 14.3 | 28.6 | 14.3 | 0.0 | 0.3029 | 31347.99897313118 | 31347.99908399582 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 450 | 4 | 174 | 0.0 | 0.0 | None | None | 276 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1814 | 45 | 1472 | 0.0 | 0.0 | None | None | 342 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `75`
- Gating Δ: `-14199`
- No-generation Δ: `-432952`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.9497, "current_avg_pnl": -1.0013, "current_win_rate": 0.0, "previous_avg_pnl": -0.0516, "previous_win_rate": 25.0, "win_rate_delta": -25.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 2.3481, "current_avg_pnl": 1.5442, "current_win_rate": 100.0, "previous_avg_pnl": -0.8039, "previous_win_rate": 0.0, "win_rate_delta": 100.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.1114, "current_avg_pnl": -0.0658, "current_win_rate": 11.1, "previous_avg_pnl": 0.0456, "previous_win_rate": 16.7, "win_rate_delta": -5.6}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.7452, "current_avg_pnl": 0.8571, "current_win_rate": 27.3, "previous_avg_pnl": 0.1119, "previous_win_rate": 27.6, "win_rate_delta": -0.3}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.6981, "current_avg_pnl": 0.3029, "current_win_rate": 14.3, "previous_avg_pnl": -0.3952, "previous_win_rate": 11.1, "win_rate_delta": 3.2}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": -227, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2907.5, "median_terminal_delta_sec": -2907.5, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": -82, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -991.12, "median_terminal_delta_sec": -991.12, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
