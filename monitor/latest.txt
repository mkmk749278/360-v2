# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `537` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 67 | 67 | 46 | 3 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2793 | 2793 | 2320 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 38989 | 38991 | 25 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 30150 | 30162 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 29981 | 29188 | 953 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 30182 | 29974 | 254 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 30066 | 29997 | 95 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 25178 | 25185 | 5 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 30228 | 30259 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 30264 | 29582 | 1066 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 42366 | 45211 | 352 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 39021 | 32559 | 9773 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 29890 | 29897 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 30164 | 30183 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 29963 | 29952 | 25 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 30649 | 30531 | 214 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 29771 | 29887 | 51 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 24766 | 22597 | 2409 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 25010 | 24871 | 182 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 38935 | 38964 | 21 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 25196 | 25207 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 770 | 770 | 656 | 4 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 265 | 265 | 72 | 4 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 8 | 8 | 0 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 9063 | 9063 | 9044 | 1 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 6 | 6 | 4 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 2598 | 2598 | 1981 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 715 | 715 | 339 | 16 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 21041 | 21041 | 13836 | 287 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 104 | 104 | 87 | 2 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 553 | 553 | 522 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 134 | 134 | 134 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 759 | 759 | 548 | 18 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 51 | 51 | 0 | 3 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=38991): breakout_not_found=24927, basic_filters_failed=7540, move_not_fresh=3968, breakout_stale=1782, retest_proximity_failed=641, volume_spike_missing=126, missing_fvg_or_orderblock=5, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=30163): cls_disabled_merged_into_lsr=30163
- **EVAL::DIVERGENCE_CONTINUATION** (total=29189): h1_trend_not_aligned=13580, cvd_divergence_failed=9391, basic_filters_failed=4920, ema_alignment_reject=1074, retest_proximity_failed=173, missing_fvg_or_orderblock=51
- **EVAL::FAILED_AUCTION_RECLAIM** (total=29975): auction_not_detected=22574, basic_filters_failed=4739, regime_blocked=1217, tail_too_small=735, reclaim_hold_failed=709, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=29998): funding_not_extreme=23007, basic_filters_failed=4483, missing_funding_rate=1564, ema_alignment_reject=531, rsi_reject=219, momentum_reject=116, cvd_divergence_failed=75, missing_fvg_or_orderblock=3
- **EVAL::LIQUIDATION_REVERSAL** (total=25185): cascade_threshold_not_met=20194, basic_filters_failed=4798, cvd_divergence_failed=103, rsi_reject=84, missing_fvg_or_orderblock=5, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=30260): no_ma_cross=24677, basic_filters_failed=4940, ma_cross_cooldown=402, ma_cross_htf_misaligned=196, ma_cross_htf_unconfirmed=45
- **EVAL::MEAN_REVERT** (total=29583): no_extension=24263, basic_filters_failed=5320
- **EVAL::MOVER_AVWAP_SCALP** (total=45212): no_avwap_tag=17473, no_mover_leg=13861, basic_filters_failed=7676, avwap_slope_against=4472, avwap_reclaim_no_volume=905, no_avwap_reclaim=809, anchor_too_recent=16
- **EVAL::MOVER_TREND_PULLBACK** (total=32559): mover_run_too_small=11819, no_reclaim=11695, basic_filters_failed=7605, no_pullback_tag=1440
- **EVAL::OPENING_RANGE_BREAKOUT** (total=29898): feature_disabled=29898
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=30184): regime_blocked=20903, breakout_not_found=7867, basic_filters_failed=1344, adx_reject=36, ema_alignment_reject=34
- **EVAL::QUIET_COMPRESSION_BREAK** (total=29953): compression_not_detected=15594, regime_blocked=10425, basic_filters_failed=3386, breakout_not_detected=505, volume_confirmation_failed=36, rsi_reject=5, missing_fvg_or_orderblock=2
- **EVAL::RANGE_FADE** (total=30532): no_range_edge=25208, basic_filters_failed=5324
- **EVAL::SR_FLIP_RETEST** (total=29888): flip_close_not_confirmed=22135, basic_filters_failed=4720, regime_blocked=1203, long_break_volume_thin=906, retest_out_of_zone=479, reclaim_hold_failed=209, h1_break_not_confirmed=85, whipsaw_flip=73, long_acceptance_not_held=53, wick_quality_failed=13, ema_alignment_reject=10, missing_fvg_or_orderblock=2
- **EVAL::STANDARD** (total=22597): momentum_reject=5289, adx_reject=4499, basic_filters_failed=3826, sweeps_not_detected=3319, macd_reject=2743, ema_alignment_reject=2378, htf_poi_unanchored=513, invalid_sl_geometry=17, rsi_reject=13
- **EVAL::TREND_PULLBACK** (total=24871): h1_trend_not_aligned=13538, ema_alignment_reject=3311, basic_filters_failed=2363, ema_not_tested_prev=1783, no_ema_reclaim_close=1495, h1_pullback_not_confirmed=738, body_conviction_fail=711, rsi_reject=447, prev_already_above_emas=168, no_prev_high_break=143, no_prev_low_break=49, momentum_flat=45, prev_already_below_emas=45, ema21_not_tagged=23, missing_fvg_or_orderblock=12
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=38964): breakout_not_found=25064, basic_filters_failed=7537, move_not_fresh=3887, breakout_stale=1391, retest_proximity_failed=882, volume_spike_missing=192, missing_fvg_or_orderblock=11
- **EVAL::WHALE_MOMENTUM** (total=25207): momentum_reject=20022, recent_ticks_insufficient=4084, basic_filters_failed=1101

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=17): execution:overextended=17
- **DIVERGENCE_CONTINUATION** (total=215): setup_compat:regime_VOLATILE_UNSUITABLE=151, setup_compat:regime_BREAKOUT_EXPANSION=64
- **FAILED_AUCTION_RECLAIM** (total=119): execution:overextended=69, setup_compat:regime_STRONG_TREND=31, setup_compat:regime_VOLATILE_UNSUITABLE=19
- **FUNDING_EXTREME_SIGNAL** (total=228): execution:trigger_not_confirmed=228
- **LIQUIDATION_REVERSAL** (total=8): execution:trigger_not_confirmed=8
- **LIQUIDITY_SWEEP_REVERSAL** (total=1948): execution:overextended=842, setup_compat:regime_STRONG_TREND=556, execution:trigger_not_confirmed=550
- **MA_CROSS_TREND_SHIFT** (total=4): setup_compat:regime_DIRTY_RANGE=2, execution:trigger_not_confirmed=2
- **MEAN_REVERT** (total=1509): setup_compat:regime_STRONG_TREND=825, setup_compat:regime_WEAK_TREND=487, execution:overextended=194, entry_quality=3
- **MOVER_AVWAP_SCALP** (total=281): execution:overextended=158, execution:trigger_not_confirmed=63, entry_quality=60
- **MOVER_TREND_PULLBACK** (total=9541): execution:trigger_not_confirmed=5590, execution:overextended=2612, entry_quality=1339
- **QUIET_COMPRESSION_BREAK** (total=6): execution:trigger_not_confirmed=6
- **RANGE_FADE** (total=398): setup_compat:regime_STRONG_TREND=173, setup_compat:regime_WEAK_TREND=140, execution:overextended=68, setup_compat:regime_VOLATILE_UNSUITABLE=15, setup_compat:regime_BREAKOUT_EXPANSION=2
- **TREND_PULLBACK_EMA** (total=756): setup_compat:regime_CLEAN_RANGE=475, setup_compat:regime_DIRTY_RANGE=204, entry_quality=57, setup_compat:regime_VOLATILE_UNSUITABLE=20

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 90749 | 53.3% |
| TRENDING_DOWN | 30885 | 18.1% |
| TRENDING_UP | 26635 | 15.6% |
| QUIET | 16393 | 9.6% |
| VOLATILE | 5727 | 3.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **18**
- Average confidence gap to threshold: **12.45** (samples=18) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XPLUSDT=8, APTUSDT=3, TRXUSDT=3, SWARMSUSDT=2, SOLUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 3 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 35 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 24 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 3 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 77 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 16 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 12 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 12 |
| MEAN_REVERT | filtered | min_confidence | 16 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 2 |
| MEAN_REVERT | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 121 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 96 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 480 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 10 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 2469 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 17 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 11 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 65 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 19 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 21 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 58.70 | 61.00 | 2.30 | 18.10 | 17.20 | 20.00 | 3.00 | 11.00 |
| BREAKDOWN_SHORT | kept | 3 | 73.17 | 65.00 | -8.17 | 19.70 | 15.10 | 20.00 | 4.50 | 5.67 |
| DIVERGENCE_CONTINUATION | filtered | 38 | 55.93 | 63.74 | 7.81 | 21.00 | 19.96 | 18.34 | 1.95 | 5.79 |
| DIVERGENCE_CONTINUATION | kept | 24 | 67.40 | 65.00 | -2.40 | 21.43 | 19.85 | 16.64 | 2.67 | -2.54 |
| FAILED_AUCTION_RECLAIM | filtered | 3 | 64.30 | 65.00 | 0.70 | 20.77 | 19.70 | 20.00 | 1.00 | 6.00 |
| FAILED_AUCTION_RECLAIM | kept | 77 | 71.83 | 65.00 | -6.83 | 19.83 | 17.76 | 20.00 | 3.81 | 1.95 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 57.71 | 61.50 | 3.79 | 20.54 | 13.88 | 17.00 | 3.62 | 1.38 |
| FUNDING_EXTREME_SIGNAL | kept | 12 | 67.94 | 65.00 | -2.94 | 20.60 | 13.90 | 16.14 | 3.67 | 0.83 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.22 | 65.00 | -5.22 | 20.49 | 15.50 | 19.03 | 0.17 | 0.50 |
| MEAN_REVERT | filtered | 18 | 53.86 | 63.22 | 9.36 | 20.11 | 17.16 | 14.33 | 0.00 | 13.07 |
| MEAN_REVERT | kept | 2 | 68.70 | 65.00 | -3.70 | 20.70 | 17.30 | 14.75 | 0.00 | 12.00 |
| MOVER_AVWAP_SCALP | filtered | 121 | 59.32 | 64.80 | 5.48 | 21.12 | 15.81 | 15.80 | 4.48 | 8.32 |
| MOVER_AVWAP_SCALP | kept | 96 | 79.28 | 65.00 | -14.28 | 20.32 | 16.91 | 15.80 | 4.87 | 2.50 |
| MOVER_TREND_PULLBACK | filtered | 490 | 56.03 | 64.80 | 8.77 | 19.88 | 18.87 | 15.80 | 3.86 | 15.61 |
| MOVER_TREND_PULLBACK | kept | 2469 | 77.07 | 65.00 | -12.07 | 20.24 | 18.49 | 15.80 | 4.25 | 0.47 |
| QUIET_COMPRESSION_BREAK | kept | 17 | 76.66 | 65.00 | -11.66 | 20.39 | 19.88 | 20.00 | 0.00 | -2.29 |
| TREND_PULLBACK_EMA | filtered | 14 | 56.41 | 65.00 | 8.59 | 20.95 | 19.41 | 17.55 | 4.36 | 8.49 |
| TREND_PULLBACK_EMA | kept | 65 | 80.57 | 65.00 | -15.57 | 20.42 | 19.59 | 18.49 | 4.64 | -0.17 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 48.83 | 61.63 | 12.80 | 20.83 | 19.52 | 20.00 | 3.32 | 6.47 |
| VOLUME_SURGE_BREAKOUT | kept | 21 | 67.73 | 65.00 | -2.73 | 19.02 | 18.22 | 20.00 | 4.79 | 7.10 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 58.70 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 4.70 | 3.00 |
| BREAKDOWN_SHORT | kept | 3 | 73.17 | 22.33 | 15.33 | 13.00 | 13.00 | 5.00 | 5.67 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 38 | 55.93 | 23.11 | 10.37 | 5.53 | 12.26 | 5.66 | 7.74 | 1.95 |
| DIVERGENCE_CONTINUATION | kept | 24 | 67.40 | 21.00 | 8.83 | 6.25 | 12.42 | 7.33 | 9.11 | 2.67 |
| FAILED_AUCTION_RECLAIM | filtered | 3 | 64.30 | 17.00 | 18.00 | 9.00 | 17.00 | 5.00 | 3.30 | 1.00 |
| FAILED_AUCTION_RECLAIM | kept | 77 | 71.83 | 24.06 | 17.95 | 4.05 | 13.84 | 4.83 | 5.23 | 3.81 |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 57.71 | 22.50 | 11.75 | 4.12 | 12.75 | 7.12 | 5.84 | 3.62 |
| FUNDING_EXTREME_SIGNAL | kept | 12 | 67.94 | 24.33 | 11.33 | 3.25 | 13.25 | 6.25 | 6.69 | 3.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.22 | 24.33 | 16.00 | 5.25 | 13.50 | 5.00 | 6.47 | 0.17 |
| MEAN_REVERT | filtered | 18 | 53.86 | 20.56 | 18.00 | 12.00 | 13.00 | 5.00 | 5.03 | 0.00 |
| MEAN_REVERT | kept | 2 | 68.70 | 25.00 | 18.00 | 12.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 121 | 59.32 | 17.00 | 18.00 | 10.86 | 13.98 | 6.67 | 6.70 | 4.48 |
| MOVER_AVWAP_SCALP | kept | 96 | 79.28 | 20.71 | 18.00 | 11.28 | 14.53 | 6.24 | 8.49 | 4.87 |
| MOVER_TREND_PULLBACK | filtered | 490 | 56.03 | 18.30 | 18.00 | 7.55 | 13.68 | 5.86 | 8.34 | 3.86 |
| MOVER_TREND_PULLBACK | kept | 2469 | 77.07 | 19.28 | 18.02 | 7.71 | 13.07 | 6.36 | 9.01 | 4.25 |
| QUIET_COMPRESSION_BREAK | kept | 17 | 76.66 | 17.00 | 18.00 | 9.71 | 14.00 | 8.50 | 9.46 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 14 | 56.41 | 11.64 | 18.00 | 9.11 | 14.43 | 8.93 | 8.29 | 4.36 |
| TREND_PULLBACK_EMA | kept | 65 | 80.57 | 20.18 | 18.06 | 7.57 | 14.06 | 7.75 | 9.66 | 4.64 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 48.83 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 4.98 | 3.32 |
| VOLUME_SURGE_BREAKOUT | kept | 21 | 67.73 | 17.71 | 16.67 | 12.00 | 14.00 | 5.00 | 8.95 | 4.79 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 58.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.00 | **6.00** |
| BREAKDOWN_SHORT | kept | 3 | 73.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 | **2.00** |
| DIVERGENCE_CONTINUATION | filtered | 38 | 55.93 | 0.00 | 0.00 | 3.45 | 0.00 | 1.71 | 0.00 | 0.00 | 0.00 | **5.16** |
| DIVERGENCE_CONTINUATION | kept | 24 | 67.40 | 0.00 | 0.00 | 0.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.33** |
| FAILED_AUCTION_RECLAIM | filtered | 3 | 64.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 77 | 71.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 16 | 57.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 12 | 67.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 70.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | **0.50** |
| MEAN_REVERT | filtered | 18 | 53.86 | 0.00 | 0.00 | 0.00 | 0.00 | 13.07 | 0.00 | 0.00 | 0.00 | **13.07** |
| MEAN_REVERT | kept | 2 | 68.70 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_AVWAP_SCALP | filtered | 121 | 59.32 | 0.00 | 0.00 | 2.75 | 0.00 | 4.38 | 0.00 | 0.00 | 1.19 | **8.32** |
| MOVER_AVWAP_SCALP | kept | 96 | 79.28 | 0.00 | 0.00 | 1.18 | 0.00 | 1.12 | 0.00 | 0.00 | 0.00 | **2.30** |
| MOVER_TREND_PULLBACK | filtered | 490 | 56.03 | 0.00 | 0.00 | 1.83 | 0.00 | 0.49 | 0.03 | 0.00 | 0.00 | **2.35** |
| MOVER_TREND_PULLBACK | kept | 2469 | 77.07 | 0.00 | 0.00 | 0.30 | 0.00 | 0.11 | 0.02 | 0.00 | 0.00 | **0.43** |
| QUIET_COMPRESSION_BREAK | kept | 17 | 76.66 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 14 | 56.41 | 0.00 | 0.00 | 3.43 | 0.00 | 8.06 | 0.00 | 0.00 | 0.00 | **11.49** |
| TREND_PULLBACK_EMA | kept | 65 | 80.57 | 0.00 | 0.00 | 1.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.35** |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 48.83 | 0.00 | 0.00 | 2.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.95 | **3.48** |
| VOLUME_SURGE_BREAKOUT | kept | 21 | 67.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **25335 held of 50255 seen** across 20 strategies; 547 cells past the sample floor; **230 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 17113 | 45/17068/0 | 50% | -0.10 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | ASIA/MARKUP/EXPANDED/BTC_RISING/MIDCAP (-1.21R) |
| MOVER_AVWAP_SCALP | 1673 | 6/1667/0 | 40% | -0.27 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (+0.85R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (-1.05R) |
| SHADOW_MEAN_REVERT | 1262 | 0/0/1262 | 37% | -0.21 | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.46R) | NY/RANGE/EXPANDED/BTC_RISING (-0.88R) |
| SHADOW_RANGE_FADE | 987 | 0/0/987 | 31% | -0.18 | ASIA/MARKUP/CASCADE/BTC_RISING (+0.23R) | LONDON/RANGE/NORMAL/BTC_RISING (-0.96R) |
| TREND_PULLBACK_EMA | 868 | 0/868/0 | 42% | -0.20 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.33R) |
| DIVERGENCE_CONTINUATION | 846 | 0/846/0 | 65% | +0.16 | OFF_HOURS/QUIET/COMPRESSED/BTC_RISING (+1.34R) | NY/MARKDOWN/COMPRESSED/BTC_RISING/MIDCAP (-1.13R) |
| WHALE_MOMENTUM | 692 | 0/692/0 | 30% | -0.47 | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.00R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| SHADOW_FUNDING_FADE | 509 | 0/0/509 | 45% | -0.21 | NY/MARKDOWN/COMPRESSED/BTC_RISING (+0.58R) | ASIA/RANGE/NORMAL/BTC_RISING (-0.58R) |
| FAILED_AUCTION_RECLAIM | 326 | 4/322/0 | 34% | -0.46 | OFF_HOURS/DISTRIBUTION/NORMAL/BTC_RISING (-0.11R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 230 | 0/230/0 | 86% | +1.06 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.00R) | ASIA/ACCUMULATION/NORMAL/BTC_NEUTRAL (+1.00R) |
| MEAN_REVERT | 220 | 2/218/0 | 80% | +0.70 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MAJOR (+1.13R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.18R) |
| QUIET_COMPRESSION_BREAK | 140 | 4/136/0 | 47% | -0.16 | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.36R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.36R) |
| FUNDING_EXTREME_SIGNAL | 138 | 0/138/0 | 32% | -0.32 | — | — |
| SHADOW_CASCADE_REVERSAL | 133 | 0/0/133 | 54% | -0.06 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.00R) | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) |
| BREAKDOWN_SHORT | 116 | 0/116/0 | 2% | -1.05 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDITY_SWEEP_REVERSAL | 50 | 2/48/0 | 52% | -0.23 | — | — |
| RANGE_FADE | 18 | 0/18/0 | 22% | -0.40 | — | — |
| MA_CROSS_TREND_SHIFT | 8 | 0/8/0 | 25% | +0.00 | — | — |
| SR_FLIP_RETEST | 4 | 0/4/0 | 0% | -0.88 | — | — |
| LIQUIDATION_REVERSAL | 2 | 0/2/0 | 0% | -1.23 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ OFF_HOURS/QUIET/COMPRESSED/BTC_RISING` +1.34R (n=25, STRONG); `DIVERGENCE_CONTINUATION @ OFF_HOURS/QUIET/COMPRESSED/BTC_RISING/MIDCAP` +1.34R (n=25, STRONG); `MOVER_TREND_PULLBACK @ ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR` +1.17R (n=32, STRONG)
- **Weakest cells**: `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.33R (n=34, NEGATIVE); `MOVER_TREND_PULLBACK @ ASIA/MARKUP/EXPANDED/BTC_RISING/MIDCAP` -1.21R (n=50, NEGATIVE); `FAILED_AUCTION_RECLAIM @ ASIA/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.19R (n=18, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 19 | 37% / -0.30R | 19 | 58% / +0.02R | +0.32 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 18 | 56% / +0.45R | 18 | 56% / +0.20R | -0.25 | **FIXED** |
| TREND_PULLBACK_EMA | 94 | 48% / -0.18R | 94 | 57% / -0.02R | +0.16 | **ATR** |
| MEAN_REVERT | 20 | 65% / +0.31R | 20 | 65% / +0.45R | +0.14 | **ATR** |
| WHALE_MOMENTUM | 58 | 26% / -0.50R | 58 | 28% / -0.40R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 93 | 61% / +0.16R | 93 | 63% / +0.07R | -0.09 | **FIXED** |
| MOVER_AVWAP_SCALP | 135 | 57% / +0.01R | 135 | 63% / +0.06R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 17 | 41% / -0.20R | 17 | 47% / -0.25R | -0.05 | **FIXED** |
| MOVER_TREND_PULLBACK | 2437 | 59% / +0.06R | 2437 | 64% / +0.09R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 34 | 62% / -0.03R | 34 | 62% / -0.02R | +0.01 | **ATR** |
| FAILED_AUCTION_RECLAIM | 40 | 32% / -0.37R | 40 | 35% / -0.36R | +0.01 | **ATR** |
| RANGE_FADE | 4 | 50% / +0.44R | 4 | 50% / +0.24R | — | **MEASURING** |
| SR_FLIP_RETEST | 3 | 0% / -0.97R | 3 | 0% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 2 | 0% / -0.28R | 2 | 0% / -0.20R | — | **MEASURING** |
| BREAKDOWN_SHORT | 2 | 0% / -0.70R | 2 | 0% / -0.67R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 3631 | 33% | -0.01R | 178 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 135 | 61% | +0.05R | 54 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 12 | 75% | +0.31R | 11 | MEASURING |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 29 | 24% / +0.13R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 47 | 72% / +2.27R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 2789 | 44% / +0.07R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 198 | 43% / +0.23R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 35 | 29% / -0.37R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 106 | 48% / +0.64R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 129 | 43% / -0.21R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 23 | 35% / -0.61R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 22 | 32% / -0.32R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 16 | 25% / -0.48R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 18 | 61% / +0.37R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 8 | 12% / -1.31R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 4 | 50% / +0.21R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 4 | 0% / -0.77R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 5 | 0% / -0.76R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 1 | 0% / -1.23R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 51 · alerting: **9** · boot grace active: False
- **ALERT** `scan_cycle` — last 43.33s, worst 137.82s over 2480 cycles; 90 over 60s, 5 over the 120s healthcheck deadline; 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 54/2) (sustained 54 cycles)
- **ALERT** `sar_alignment_crosscheck` — 2000/14782 disagreed (13.5%) (streak 121/6) (sustained 121 cycles)
- **ALERT** `dark_resolution` — 20 of 167 open dark rows are not being advanced (worst: ONEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 164/120) (sustained 164 cycles)
- **ALERT** `cohort_edge_gate` — all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 164/6) (sustained 164 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 1221x (gate reads 0x, withheld 0x — refusal dark); last MUBARAKUSDT age=21249.7s (streak 55/6) (sustained 55 cycles)
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=+0.61R (bound 0.3) (streak 164/6) (sustained 164 cycles)
- **ALERT** `mean_revert_emission` — 1245 detections since last emission (emitted_total=2) — and the POST-SCORING blocked candidates measure +0.70R over n=218, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 49/6) (sustained 49 cycles)
- **ALERT** `range_fade_emission` — 557 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 86/6) (sustained 86 cycles)
- **ALERT** `tuned_variants` — 50 non-stamps — atr_arm_uncomputable=50 (seen=3657 stamped=608 skipped=2999) (streak 54/6) (sustained 54 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 14479490 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 24 arms current, none stalled; covering 203/203 signals (100%) | 0 |
| auto_dispatch | ok | attempts=13 fanouts=13 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77143.90 | 0 |
| candle_coverage | ok | 105/123 symbols with ≥20 15m candles, 99/123 updated within 45m [no_bucket=18, stale=6, fresh=99; 29 promoted of 123]; 24 CORE pair(s) unusable (e.g. 1000000BOBUSDT, 1000CATUSDT, AEVOUSDT, BLUAIUSDT, BTRUSDT) | 0 |
| candle_series_integrity | ok | merge dropped 10455 dup bars, 0 undedupable; ws 1 out-of-order, 289 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 29 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 29 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 164/6) | 164 |
| context_emission_policy | ok | output +34 / upstream +6 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1264/1278 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 20 of 167 open dark rows are not being advanced (worst: ONEUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 164/120) | 164 |
| dark_sar_arms | ok | no open arms; covering 1262/1276 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 4206970 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=+0.61R (bound 0.3) (streak 164/6) | 164 |
| emission_controller | ok | last cycle 700s ago; live_overrides=27 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=15 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4274 stamps (MEAN_REVERT=226, MOVER_AVWAP_SCALP=240, MOVER_TREND_PULLBACK=3498, RANGE_FADE=174, TREND_PULLBACK_EMA=136), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 507 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | counter reset | 0 |
| geometry_ab | ok | output +15 / upstream +46 | 0 |
| indicator_cache_key | ok | 47314 frozen value(s) avoided; 37836 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1245 detections since last emission (emitted_total=2) — and the POST-SCORING blocked candidates measure +0.70R over n=218, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 49/6) | 49 |
| mean_revert_path | ok | output +8 / upstream +46 | 0 |
| mover_admission_metadata | ok | 872 symbols known, 170 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 29 held, 29 with scan counts, 29 with an activity reading (enforcing) | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s); 2 orphan(s) dropped at restore | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2941 rows held, 681925 evicted (sampled: execution:overextended 400/249457, execution:trigger_not_confirmed 400/241133, setup_compat:regime_STRONG_TREND 400/87577) | 0 |
| price_action_lane | ok | 251087 evaluated, 431 emitted; layer1 431 stamped / 0 blind; cooldown=28267, delta_opposed=24264, no_footprint=125490, no_opposing_target=140, no_sweep=49866, rr_below_floor=22629 | 0 |
| promoted_pair_integrity | ok | 29/29 promoted pairs present in universe | 0 |
| range_fade_emission | violating | 557 detections since last emission (emitted_total=0) — and only 18 POST-SCORING suppressed samples measured (need 200), so we cannot tell a dead path from a correctly-gated one. Pre-scoring rejects (setup_compat:* / execution:*) are NOT in this population — check the dark lane and the gate-reject counters for those. (streak 86/6) | 86 |
| range_fade_path | ok | output +4 / upstream +46 | 0 |
| sar_alignment_crosscheck | violating | 2000/14782 disagreed (13.5%) (streak 121/6) | 121 |
| sar_exit_shadow | ok | output +12 / upstream +46 | 0 |
| sar_hold_arm | ok | 330 held arms settled, 71 unscored, 23 still walking (18 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 5/84 unfetchable (6%); top cause: gap or duplicate bar in the 15m window; symbols: BEATUSDT, ETCUSDT, HYPEUSDT, ONDOUSDT, SANDUSDT | 0 |
| sar_live_arms | ok | 23 arms current, none stalled; covering 212/212 signals (100%) | 0 |
| sar_refresh_budget | ok | 9 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 77 still mid-window | 0 |
| scan_cycle | violating | last 43.33s, worst 137.82s over 2480 cycles; 90 over 60s, 5 over the 120s healthcheck deadline; 8 executor workers — a cycle past the deadline leaves the scanner heartbeat stale, and three consecutive failed healthchecks restart this container (streak 54/2) | 54 |
| setup_tf_resolver | ok | 97230 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 31s ago (3.74s to run, worst 94.53s), 544 overrun(s) of 3302 cycles, TTL 900s; slowest signals=7.36s, data_intake=7.27s, activity=1.27s | 0 |
| stale_tf_scoring | violating | scored on stale TF 1221x (gate reads 0x, withheld 0x — refusal dark); last MUBARAKUSDT age=21249.7s (streak 55/6) | 55 |
| staleness_v2_shadow | ok | counter reset | 0 |
| strategy_edge | ok | output +82 / upstream +46 | 0 |
| structural_snap | ok | 4255/4255 measured, 17 blind, 0 levels moved (refusals: redetect_cooldown=719) | 0 |
| structural_veto_lane | ok | 1163 stamped; 0 with no readable level book, 4 with clear air ahead, 853 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +46 / upstream +6 | 0 |
| tuned_variants | violating | 50 non-stamps — atr_arm_uncomputable=50 (seen=3657 stamped=608 skipped=2999) (streak 54/6) | 54 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `73222`
- `Path funnel` emissions: `17`
- `Regime distribution` emissions: `17`
- `QUIET_SCALP_BLOCK` events: `18`
- `confidence_gate` events: `3520`
- `free_channel_post` events: `13`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **128**
- Total REST-fallback activations: **25**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 47 | 4812 | 13532 | 57799 | 0 |
| futures_aggtrade | 16 | 5205 | 32844 | 307994 | 1 |
| futures_depth | 30 | 5041 | 11760 | 18618 | 0 |
| futures_liq | 10 | 4176 | 25169 | 33275 | 0 |
| futures_mover | 25 | 5538 | 17198 | 44604 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 25 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **13**

| Source | Count |
|---|---:|
| signal_close | 11 |
| regime_shift | 2 |

- By severity: HIGH=13

## Dependency readiness
- cvd: presence[present=139969] state[populated=139969] buckets[many=139969] sources[none] quality[none]
- funding_rate: presence[absent=38408, present=101561] state[empty=38408, populated=101561] buckets[few=101561, none=38408] sources[none] quality[none]
- liquidation_clusters: presence[absent=87740, present=52229] state[empty=87740, populated=52229] buckets[few=42255, none=87740, some=9974] sources[none] quality[none]
- oi_snapshot: presence[absent=38408, present=101561] state[empty=38408, populated=101561] buckets[many=101561, none=38408] sources[none] quality[none]
- order_book: presence[absent=63743, present=76226] state[populated=76226, unavailable=63743] buckets[few=76226, none=63743] sources[book_ticker=76226, unavailable=63743] quality[none=63743, top_of_book_only=76226]
- orderblocks: presence[absent=139969] state[empty=139969] buckets[none=139969] sources[measured_dark=139969] quality[none]
- recent_ticks: presence[present=139969] state[populated=139969] buckets[many=139969] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.530374526977539` sec
- Median create→first breach: `4585.8058425188065` sec
- Median create→terminal: `4618.114715576172` sec
- Median first breach→terminal: `5.548508405685425` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 2.42484517187897 | 3.0 | 0.8082817239596567 | 0 | 1 |
| MOVER_AVWAP_SCALP | 2 | 2 | 1.9479183862471392 | 2.0373663571225733 | 0.9549157353018407 | 1 | 1 |
| MOVER_TREND_PULLBACK | 17 | 17 | 2.946054734948386 | 3.0 | 1.0287256768081665 | 9 | 8 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 35810.92026901245 | 35812.33377599716 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9145 | 5457.103504538536 | 5459.14493560791 |
| MOVER_TREND_PULLBACK | 17 | 17 | 0.0 | 29.4 | 0.0 | 0.0 | 0.8887 | 4336.075269937515 | 4338.442328929901 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 134 | 0 | 134 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 759 | 18 | 548 | 0.0 | 0.0 | None | None | 211 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `345`
- Gating Δ: `29589`
- No-generation Δ: `583197`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.3946, "current_avg_pnl": 0.8887, "current_win_rate": 0.0, "previous_avg_pnl": 2.2833, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 18, "geometry_changed_delta": 0, "geometry_preserved_delta": 211, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
