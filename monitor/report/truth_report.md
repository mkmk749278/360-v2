# Runtime Truth Report

## Executive summary
- Overall health/freshness: **unhealthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=unhealthy)
- Heartbeat age: `719` sec (warning=True)
- Latest performance record age: `646` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 44 | 44 | 33 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 19535 | 19535 | 18007 | 20 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 120211 | 120228 | 23 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 105640 | 105655 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 105298 | 98841 | 6793 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 105674 | 101339 | 4492 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 118481 | 117917 | 604 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 90055 | 90054 | 15 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 105832 | 105857 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 141880 | 145036 | 5753 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 120255 | 87793 | 54017 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 116487 | 116499 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 105661 | 105666 | 7 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 105279 | 105275 | 18 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 103265 | 101765 | 3470 | 0 | 0 | 0 | low-sample (long_disabled) |
| EVAL::STANDARD | 78986 | 73635 | 5696 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 79335 | 78861 | 528 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 120159 | 120155 | 51 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 90078 | 90026 | 84 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 10745 | 10745 | 8813 | 36 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1779 | 1779 | 1559 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 40 | 40 | 40 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 21392 | 21392 | 21011 | 13 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 7 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 11074 | 11074 | 10251 | 3 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 124135 | 124135 | 114007 | 33 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 27 | 27 | 25 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 82 | 82 | 63 | 4 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 8762 | 8762 | 6574 | 22 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2116 | 2116 | 2081 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 139 | 139 | 115 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 1796 | 1796 | 1770 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=120228): breakout_not_found=68419, basic_filters_failed=35143, move_not_fresh=11920, breakout_stale=2972, retest_proximity_failed=1432, volume_spike_missing=318, move_exhausted=17, missing_fvg_or_orderblock=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=105657): cls_disabled_merged_into_lsr=105657
- **EVAL::DIVERGENCE_CONTINUATION** (total=98842): cvd_divergence_failed=46982, basic_filters_failed=21138, h1_trend_not_aligned=14539, ema_alignment_reject=12339, retest_proximity_failed=2017, regime_blocked=1253, missing_fvg_or_orderblock=574
- **EVAL::FAILED_AUCTION_RECLAIM** (total=101341): auction_not_detected=42939, basic_filters_failed=19574, reclaim_hold_failed=17558, tail_too_small=14438, regime_blocked=6832
- **EVAL::FUNDING_EXTREME** (total=117919): funding_not_extreme=84839, basic_filters_failed=24135, ema_alignment_reject=4486, missing_funding_rate=2684, rsi_reject=844, cvd_divergence_failed=455, momentum_reject=402, missing_fvg_or_orderblock=74
- **EVAL::LIQUIDATION_REVERSAL** (total=90054): cascade_threshold_not_met=63802, basic_filters_failed=25206, cvd_divergence_failed=538, rsi_reject=480, missing_fvg_or_orderblock=27, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=105859): no_ma_cross=83677, basic_filters_failed=21156, ma_cross_cooldown=854, ma_cross_htf_misaligned=141, ma_cross_htf_unconfirmed=31
- **EVAL::MOVER_AVWAP_SCALP** (total=145039): no_avwap_tag=89293, basic_filters_failed=35315, no_mover_leg=10267, avwap_slope_against=7571, avwap_reclaim_no_volume=1815, no_avwap_reclaim=715, insufficient_candles=63
- **EVAL::MOVER_TREND_PULLBACK** (total=87793): basic_filters_failed=35238, no_reclaim=28495, mover_run_too_small=21472, no_pullback_tag=2525, insufficient_candles=63
- **EVAL::OPENING_RANGE_BREAKOUT** (total=116501): feature_disabled=116501
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=105668): regime_blocked=82167, breakout_not_found=17243, basic_filters_failed=4187, adx_reject=2038, ema_alignment_reject=33
- **EVAL::QUIET_COMPRESSION_BREAK** (total=105277): compression_not_detected=57865, regime_blocked=30246, basic_filters_failed=15373, breakout_not_detected=1605, volume_confirmation_failed=170, rsi_reject=18
- **EVAL::SR_FLIP_RETEST** (total=101767): long_disabled=19824, basic_filters_failed=19542, flip_close_not_confirmed=17382, long_break_volume_thin=11291, whipsaw_flip=10414, reclaim_hold_failed=7763, regime_blocked=6809, retest_out_of_zone=5958, wick_quality_failed=1379, long_acceptance_not_held=743, missing_fvg_or_orderblock=435, ema_alignment_reject=221, rsi_reject=6
- **EVAL::STANDARD** (total=73635): adx_reject=19823, momentum_reject=18546, basic_filters_failed=11908, sweeps_not_detected=11612, macd_reject=7587, ema_alignment_reject=3687, invalid_sl_geometry=368, rsi_reject=100, mtf_reject=4
- **EVAL::TREND_PULLBACK** (total=78861): h1_pullback_not_confirmed=22927, h1_trend_not_aligned=17178, basic_filters_failed=10403, ema_alignment_reject=10056, ema_not_tested_prev=4985, no_ema_reclaim_close=4282, body_conviction_fail=2944, rsi_reject=2505, regime_blocked=1546, prev_already_above_emas=848, no_prev_high_break=520, prev_already_below_emas=229, momentum_flat=142, no_prev_low_break=106, ema21_not_tagged=81, momentum_reject=59, missing_fvg_or_orderblock=50
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=120155): breakout_not_found=62604, basic_filters_failed=35140, move_not_fresh=14820, breakout_stale=4836, retest_proximity_failed=2360, volume_spike_missing=378, move_exhausted=13, missing_fvg_or_orderblock=4
- **EVAL::WHALE_MOMENTUM** (total=90026): momentum_reject=71666, recent_ticks_insufficient=12452, basic_filters_failed=5908

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 220798 | 41.4% |
| QUIET | 132825 | 24.9% |
| TRENDING_UP | 93323 | 17.5% |
| TRENDING_DOWN | 54577 | 10.2% |
| VOLATILE | 32449 | 6.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **343**
- Average confidence gap to threshold: **12.30** (samples=343) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=70, BZUSDT=37, XRPUSDT=28, NBISUSDT=27, AMDUSDT=26, ETHUSDT=25, TRXUSDT=20, DOTUSDT=14, BNBUSDT=13, AAVEUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 9 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 262 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 4 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 45 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 298 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 181 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 177 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 23 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 45 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 33 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 42 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 389 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 879 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 27 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 6056 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 15 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 14 |
| SR_FLIP_RETEST | filtered | min_confidence | 261 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 56 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 119 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 31 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 32 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 12 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 9 | 64.00 | 65.00 | 1.00 | 20.90 | 20.00 | 20.00 | 3.00 | 3.00 |
| BREAKDOWN_SHORT | kept | 2 | 70.05 | 65.00 | -5.05 | 20.85 | 18.35 | 20.00 | 4.50 | 9.60 |
| DIVERGENCE_CONTINUATION | filtered | 266 | 56.58 | 65.00 | 8.42 | 19.67 | 19.64 | 18.46 | 1.95 | 12.49 |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.11 | 65.00 | -3.11 | 20.71 | 19.87 | 17.71 | 2.24 | 1.28 |
| FAILED_AUCTION_RECLAIM | filtered | 479 | 54.81 | 65.00 | 10.19 | 21.26 | 19.42 | 20.00 | 4.40 | 11.09 |
| FAILED_AUCTION_RECLAIM | kept | 177 | 71.82 | 65.00 | -6.82 | 21.40 | 19.07 | 20.00 | 3.71 | 1.69 |
| FUNDING_EXTREME_SIGNAL | filtered | 26 | 53.02 | 65.00 | 11.98 | 20.28 | 19.96 | 17.82 | 0.92 | 8.97 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 50.63 | 65.00 | 14.37 | 20.98 | 19.65 | 17.12 | 1.41 | 19.64 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 42 | 67.74 | 65.00 | -2.74 | 21.37 | 19.90 | 17.13 | 3.21 | -0.64 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.00 | 65.00 | -3.00 | 20.70 | 17.20 | 15.80 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 389 | 82.55 | 65.00 | -17.55 | 18.23 | 16.34 | 15.80 | 4.36 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 906 | 59.75 | 65.00 | 5.25 | 20.90 | 17.46 | 15.80 | 3.81 | 8.92 |
| MOVER_TREND_PULLBACK | kept | 6056 | 79.47 | 65.00 | -14.47 | 19.45 | 17.97 | 15.80 | 4.69 | 1.36 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 80.85 | 65.00 | -15.85 | 23.55 | 20.00 | 19.45 | 5.25 | 5.40 |
| QUIET_COMPRESSION_BREAK | filtered | 15 | 62.82 | 65.00 | 2.18 | 18.86 | 20.00 | 20.00 | 0.00 | 8.58 |
| QUIET_COMPRESSION_BREAK | kept | 14 | 77.34 | 65.00 | -12.34 | 19.39 | 20.00 | 20.00 | 0.00 | -0.41 |
| SR_FLIP_RETEST | filtered | 317 | 56.08 | 65.00 | 8.92 | 20.75 | 19.88 | 16.22 | 2.01 | 13.19 |
| SR_FLIP_RETEST | kept | 119 | 69.76 | 65.00 | -4.76 | 20.30 | 19.80 | 16.23 | 2.37 | 1.95 |
| TREND_PULLBACK_EMA | filtered | 5 | 59.90 | 65.00 | 5.10 | 22.24 | 16.90 | 17.40 | 5.50 | 18.10 |
| TREND_PULLBACK_EMA | kept | 31 | 78.48 | 65.00 | -13.48 | 20.35 | 19.87 | 16.52 | 5.76 | -1.35 |
| VOLUME_SURGE_BREAKOUT | filtered | 32 | 58.27 | 65.00 | 6.73 | 20.85 | 18.19 | 20.00 | 5.36 | 8.75 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 78.58 | 65.00 | -13.58 | 22.05 | 18.25 | 20.00 | 4.75 | 5.85 |
| WHALE_MOMENTUM | filtered | 12 | 36.53 | 65.00 | 28.47 | 23.52 | 20.00 | 17.00 | 0.00 | 32.85 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 9 | 64.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 2.00 | 3.00 |
| BREAKDOWN_SHORT | kept | 2 | 70.05 | 21.00 | 16.00 | 13.50 | 14.00 | 5.00 | 5.65 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 266 | 56.58 | 22.29 | 15.11 | 4.79 | 11.51 | 6.11 | 7.70 | 1.95 |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.11 | 22.69 | 15.11 | 4.53 | 11.76 | 5.54 | 8.78 | 2.24 |
| FAILED_AUCTION_RECLAIM | filtered | 479 | 54.81 | 21.68 | 16.35 | 6.00 | 11.19 | 6.31 | 4.85 | 4.40 |
| FAILED_AUCTION_RECLAIM | kept | 177 | 71.82 | 21.07 | 15.67 | 7.69 | 12.21 | 6.47 | 6.68 | 3.71 |
| FUNDING_EXTREME_SIGNAL | filtered | 26 | 53.02 | 24.08 | 13.77 | 3.23 | 15.19 | 6.58 | 8.02 | 0.92 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 50.63 | 21.44 | 15.69 | 7.88 | 12.54 | 6.48 | 4.83 | 1.41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 42 | 67.74 | 24.43 | 14.19 | 3.93 | 12.10 | 6.18 | 3.71 | 3.21 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.00 | 17.00 | 14.00 | 12.00 | 11.00 | 8.00 | 6.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 389 | 82.55 | 18.15 | 18.00 | 14.26 | 14.00 | 5.00 | 8.78 | 4.36 |
| MOVER_TREND_PULLBACK | filtered | 906 | 59.75 | 18.75 | 18.00 | 8.05 | 12.67 | 6.56 | 8.42 | 3.81 |
| MOVER_TREND_PULLBACK | kept | 6056 | 79.47 | 19.35 | 18.08 | 9.37 | 13.91 | 6.43 | 9.02 | 4.69 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 80.85 | 21.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.00 | 5.25 |
| QUIET_COMPRESSION_BREAK | filtered | 15 | 62.82 | 17.00 | 18.00 | 12.60 | 14.00 | 8.50 | 1.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 14 | 77.34 | 19.29 | 18.00 | 12.64 | 13.79 | 8.00 | 7.57 | 0.00 |
| SR_FLIP_RETEST | filtered | 317 | 56.08 | 21.38 | 16.23 | 5.17 | 13.20 | 6.62 | 4.67 | 2.01 |
| SR_FLIP_RETEST | kept | 119 | 69.76 | 22.85 | 17.16 | 6.15 | 13.25 | 6.09 | 4.09 | 2.37 |
| TREND_PULLBACK_EMA | filtered | 5 | 59.90 | 17.00 | 18.00 | 7.50 | 17.00 | 5.00 | 8.00 | 5.50 |
| TREND_PULLBACK_EMA | kept | 31 | 78.48 | 17.35 | 18.00 | 7.50 | 14.10 | 6.48 | 9.87 | 5.76 |
| VOLUME_SURGE_BREAKOUT | filtered | 32 | 58.27 | 18.53 | 18.00 | 12.84 | 11.72 | 5.00 | 6.35 | 5.36 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 78.58 | 19.00 | 17.00 | 15.00 | 14.00 | 5.00 | 9.68 | 4.75 |
| WHALE_MOMENTUM | filtered | 12 | 36.53 | 18.83 | 8.00 | 13.00 | 14.00 | 8.33 | 7.22 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 9 | 64.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 2 | 70.05 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | 0.00 | 0.00 | 3.00 | **6.60** |
| DIVERGENCE_CONTINUATION | filtered | 266 | 56.58 | 0.00 | 0.00 | 0.58 | 0.00 | 0.86 | 0.00 | 0.00 | 0.00 | **1.44** |
| DIVERGENCE_CONTINUATION | kept | 45 | 68.11 | 0.00 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.21** |
| FAILED_AUCTION_RECLAIM | filtered | 479 | 54.81 | 0.00 | 0.00 | 2.72 | 0.00 | 3.24 | 0.00 | 0.00 | 0.00 | **5.96** |
| FAILED_AUCTION_RECLAIM | kept | 177 | 71.82 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.26** |
| FUNDING_EXTREME_SIGNAL | filtered | 26 | 53.02 | 0.00 | 0.00 | 5.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **5.08** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 78 | 50.63 | 0.00 | 0.00 | 0.55 | 0.00 | 10.92 | 0.00 | 0.00 | 0.00 | **11.47** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 42 | 67.74 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 389 | 82.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 906 | 59.75 | 0.00 | 0.00 | 2.24 | 0.00 | 1.04 | 0.00 | 0.00 | 0.00 | **3.28** |
| MOVER_TREND_PULLBACK | kept | 6056 | 79.47 | 0.00 | 0.00 | 0.27 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.31** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 80.85 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.40** |
| QUIET_COMPRESSION_BREAK | filtered | 15 | 62.82 | 0.00 | 0.00 | 0.00 | 0.00 | 2.58 | 0.00 | 0.00 | 0.00 | **2.58** |
| QUIET_COMPRESSION_BREAK | kept | 14 | 77.34 | 0.00 | 0.00 | 1.03 | 0.00 | 0.92 | 0.00 | 0.00 | 0.00 | **1.95** |
| SR_FLIP_RETEST | filtered | 317 | 56.08 | 0.00 | 0.00 | 0.00 | 0.00 | 2.85 | 0.00 | 0.00 | 2.35 | **5.20** |
| SR_FLIP_RETEST | kept | 119 | 69.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.19 | **0.19** |
| TREND_PULLBACK_EMA | filtered | 5 | 59.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 31 | 78.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 32 | 58.27 | 0.00 | 0.00 | 0.00 | 0.00 | 1.01 | 0.00 | 0.00 | 0.79 | **1.80** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 78.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 12 | 36.53 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=98 (63.2%) | PREMATURE=22 (14.2%) | NEUTRAL=35 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 76 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 98 | 22 | 35 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 5 | 2 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 23 | 9 | 11 | 0 |
| FUNDING_EXTREME_SIGNAL | 0 | 1 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 8 | 2 | 4 | 0 |
| MOVER_AVWAP_SCALP | 10 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 25 | 3 | 4 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 22 | 5 | 13 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 98 | 22 | 35 | 68.7 | 46.7 | +0.14 | **KEEP** — net-helping: avg +0.14R/kill across 155 kills (saved 68.7R vs missed 46.7R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2676972`
- `Path funnel` emissions: `58`
- `Regime distribution` emissions: `58`
- `QUIET_SCALP_BLOCK` events: `343`
- `confidence_gate` events: `9027`
- `free_channel_post` events: `31`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **5**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 5 | 3068 | 3579 | 7719 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **31**

| Source | Count |
|---|---:|
| signal_close | 27 |
| regime_shift | 2 |
| signal_highlight | 2 |

- By severity: HIGH=31

## Dependency readiness
- cvd: presence[present=411310] state[populated=411310] buckets[many=411309, some=1] sources[none] quality[none]
- funding_rate: presence[absent=70418, present=340892] state[empty=70418, populated=340892] buckets[few=340892, none=70418] sources[none] quality[none]
- liquidation_clusters: presence[absent=253986, present=157324] state[empty=253986, populated=157324] buckets[few=131491, none=253986, some=25833] sources[none] quality[none]
- oi_snapshot: presence[absent=67645, present=343665] state[empty=67645, populated=343665] buckets[few=139, many=342696, none=67645, some=830] sources[none] quality[none]
- order_book: presence[absent=124032, present=287278] state[populated=287278, unavailable=124032] buckets[few=287278, none=124032] sources[book_ticker=287278, unavailable=124032] quality[none=124032, top_of_book_only=287278]
- orderblocks: presence[absent=411310] state[empty=411310] buckets[none=411310] sources[not_implemented=411310] quality[none]
- recent_ticks: presence[present=411310] state[populated=411310] buckets[many=411310] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.440094470977783` sec
- Median create→first breach: `971.5904870033264` sec
- Median create→terminal: `3602.044068813324` sec
- Median first breach→terminal: `2.3377554416656494` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 7.7}, "under_180s": {"count": 2, "pct": 7.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 2, "pct": 7.7}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 1.8}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3191.0217940807343 | 3200.5387570858 |
| DIVERGENCE_CONTINUATION | 4 | 4 | 0.0 | 75.0 | 0.0 | 0.0 | -0.7254 | 2200.7188341617584 | 2364.2470470666885 |
| FAILED_AUCTION_RECLAIM | 11 | 11 | 18.2 | 36.4 | 18.2 | 0.0 | 0.3067 | 2020.3735439777374 | 2857.6944921016693 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.2584 | 1820.8129060268402 | 2716.402127981186 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | -0.1176 | None | 3612.2764575481415 |
| MOVER_TREND_PULLBACK | 25 | 25 | 0.0 | 12.0 | 0.0 | 0.0 | -0.079 | 702.2205259799957 | 3603.96977519989 |
| SR_FLIP_RETEST | 9 | 9 | 0.0 | 22.2 | 0.0 | 0.0 | 0.0364 | 446.5480999946594 | 3608.552031993866 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.1656 | 315.22571301460266 | 317.09239196777344 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 8762 | 22 | 6574 | 0.0 | 22.2 | 446.5480999946594 | 3608.552031993866 | 2188 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2116 | 2 | 2081 | 0.0 | 100.0 | 315.22571301460266 | 317.09239196777344 | 35 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `138`
- Gating Δ: `184356`
- No-generation Δ: `1764602`
- Fast failures Δ: `2`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.344, "current_avg_pnl": -0.7254, "current_win_rate": 0.0, "previous_avg_pnl": -0.3814, "previous_win_rate": 14.3, "win_rate_delta": -14.3}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.4128, "current_avg_pnl": 0.3067, "current_win_rate": 18.2, "previous_avg_pnl": -0.1061, "previous_win_rate": 15.4, "win_rate_delta": 2.8}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.6386, "current_avg_pnl": 0.2584, "current_win_rate": 0.0, "previous_avg_pnl": -0.3802, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.8954, "current_avg_pnl": -0.079, "current_win_rate": 0.0, "previous_avg_pnl": 0.8164, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0882, "current_avg_pnl": 0.0364, "current_win_rate": 0.0, "previous_avg_pnl": -0.0518, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 22, "geometry_changed_delta": 0, "geometry_preserved_delta": 2188, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1050.31, "median_terminal_delta_sec": 2099.25, "sl_rate_delta": -34.9, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 35, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -575.43, "median_terminal_delta_sec": -578.74, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
