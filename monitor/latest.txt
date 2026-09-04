# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::OPENING_RANGE_BREAKOUT, EVAL::CONTINUATION_LIQUIDITY_SWEEP
- Top promising signals/paths: QUIET_COMPRESSION_BREAK
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1009` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 199 | 199 | 199 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9905 | 9905 | 9580 | 2 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 85474 | 85454 | 71 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 82848 | 82848 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 82420 | 79765 | 3061 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 82892 | 82169 | 822 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 83166 | 82834 | 374 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 69745 | 69772 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 82996 | 83049 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 83062 | 80207 | 3884 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 92313 | 97971 | 1513 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 85531 | 76554 | 15690 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 82626 | 82626 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 82854 | 82861 | 17 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 82380 | 82178 | 235 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 84100 | 82383 | 2394 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 81795 | 82224 | 85 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 68734 | 64707 | 4408 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 69124 | 68733 | 480 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 85407 | 85444 | 25 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 69786 | 69816 | 2 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3597 | 3597 | 3316 | 5 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1044 | 1044 | 909 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 22608 | 22608 | 22240 | 20 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 12 | 1 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 9225 | 9225 | 8239 | 2 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3499 | 3499 | 2555 | 28 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 43078 | 43078 | 38778 | 160 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 36 | 36 | 36 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1492 | 1492 | 1295 | 18 | active-healthy (none) |
| RANGE_FADE | 0 | 0 | 5611 | 5611 | 5266 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 287 | 287 | 104 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2026 | 2026 | 1901 | 13 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 116 | 116 | 116 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 97 | 97 | 88 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=85454): breakout_not_found=46230, basic_filters_failed=26146, move_not_fresh=8587, breakout_stale=3163, retest_proximity_failed=1139, volume_spike_missing=178, move_exhausted=9, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=82848): cls_disabled_merged_into_lsr=82848
- **EVAL::DIVERGENCE_CONTINUATION** (total=79765): cvd_divergence_failed=34989, basic_filters_failed=22025, h1_trend_not_aligned=16780, ema_alignment_reject=4617, retest_proximity_failed=1051, missing_fvg_or_orderblock=303
- **EVAL::FAILED_AUCTION_RECLAIM** (total=82169): auction_not_detected=51638, basic_filters_failed=21269, reclaim_hold_failed=3571, regime_blocked=3515, tail_too_small=2160, rsi_reject=16
- **EVAL::FUNDING_EXTREME** (total=82834): funding_not_extreme=53672, basic_filters_failed=21644, ema_alignment_reject=2952, missing_funding_rate=2213, rsi_reject=1729, cvd_divergence_failed=332, momentum_reject=242, missing_fvg_or_orderblock=50
- **EVAL::LIQUIDATION_REVERSAL** (total=69772): cascade_threshold_not_met=46773, basic_filters_failed=21904, cvd_divergence_failed=602, rsi_reject=475, missing_fvg_or_orderblock=14, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=83049): no_ma_cross=60086, basic_filters_failed=22049, ma_cross_cooldown=651, ma_cross_htf_misaligned=263
- **EVAL::MEAN_REVERT** (total=80207): no_extension=63624, basic_filters_failed=16583
- **EVAL::MOVER_AVWAP_SCALP** (total=97971): no_avwap_tag=36057, basic_filters_failed=26451, no_mover_leg=23714, avwap_slope_against=7816, avwap_reclaim_no_volume=2222, no_avwap_reclaim=1661, anchor_too_recent=50
- **EVAL::MOVER_TREND_PULLBACK** (total=76554): mover_run_too_small=30277, basic_filters_failed=26297, no_reclaim=17232, no_pullback_tag=2748
- **EVAL::OPENING_RANGE_BREAKOUT** (total=82626): feature_disabled=82626
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=82861): regime_blocked=59865, breakout_not_found=15289, basic_filters_failed=5560, adx_reject=2112, ema_alignment_reject=35
- **EVAL::QUIET_COMPRESSION_BREAK** (total=82178): compression_not_detected=34130, regime_blocked=26394, basic_filters_failed=15694, breakout_not_detected=5296, volume_confirmation_failed=620, rsi_reject=40, missing_fvg_or_orderblock=4
- **EVAL::RANGE_FADE** (total=82383): no_range_edge=65791, basic_filters_failed=16592
- **EVAL::SR_FLIP_RETEST** (total=82224): flip_close_not_confirmed=51852, basic_filters_failed=21240, regime_blocked=3492, long_break_volume_thin=2385, retest_out_of_zone=1451, h1_break_not_confirmed=1069, reclaim_hold_failed=345, ema_alignment_reject=156, long_acceptance_not_held=104, wick_quality_failed=90, whipsaw_flip=32, missing_fvg_or_orderblock=8
- **EVAL::STANDARD** (total=64707): adx_reject=17113, momentum_reject=16889, basic_filters_failed=12286, sweeps_not_detected=6556, macd_reject=6248, ema_alignment_reject=4252, htf_poi_unanchored=1202, invalid_sl_geometry=108, rsi_reject=50, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=68733): h1_trend_not_aligned=21246, h1_pullback_not_confirmed=13020, basic_filters_failed=11177, ema_alignment_reject=9529, ema_not_tested_prev=4465, no_ema_reclaim_close=3904, body_conviction_fail=2288, rsi_reject=1513, prev_already_above_emas=748, no_prev_high_break=398, no_prev_low_break=141, prev_already_below_emas=112, momentum_flat=93, momentum_reject=40, missing_fvg_or_orderblock=38, ema21_not_tagged=21
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=85444): breakout_not_found=44792, basic_filters_failed=26142, move_not_fresh=9666, breakout_stale=3043, retest_proximity_failed=1545, volume_spike_missing=226, missing_fvg_or_orderblock=18, move_exhausted=12
- **EVAL::WHALE_MOMENTUM** (total=69816): momentum_reject=50816, recent_ticks_insufficient=12228, basic_filters_failed=6772

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=50): execution:overextended=50
- **DIVERGENCE_CONTINUATION** (total=336): setup_compat:regime_VOLATILE_UNSUITABLE=297, setup_compat:regime_BREAKOUT_EXPANSION=28, execution:overextended=11
- **FAILED_AUCTION_RECLAIM** (total=867): execution:overextended=549, setup_compat:regime_STRONG_TREND=245, context_floor=73
- **FUNDING_EXTREME_SIGNAL** (total=922): execution:trigger_not_confirmed=921, context_floor=1
- **LIQUIDATION_REVERSAL** (total=12): execution:trigger_not_confirmed=12
- **LIQUIDITY_SWEEP_REVERSAL** (total=4853): execution:trigger_not_confirmed=2230, execution:overextended=1397, setup_compat:regime_STRONG_TREND=1226
- **MA_CROSS_TREND_SHIFT** (total=17): setup_compat:regime_DIRTY_RANGE=10, execution:trigger_not_confirmed=4, setup_compat:regime_CLEAN_RANGE=3
- **MEAN_REVERT** (total=5191): setup_compat:regime_STRONG_TREND=2244, setup_compat:regime_WEAK_TREND=1971, execution:overextended=976
- **MOVER_AVWAP_SCALP** (total=1742): execution:overextended=1447, entry_quality=160, execution:trigger_not_confirmed=135
- **MOVER_TREND_PULLBACK** (total=17826): execution:trigger_not_confirmed=10436, execution:overextended=6907, entry_quality=483
- **QUIET_COMPRESSION_BREAK** (total=8): execution:trigger_not_confirmed=6, execution:overextended=2
- **RANGE_FADE** (total=2242): setup_compat:regime_STRONG_TREND=1098, setup_compat:regime_WEAK_TREND=886, execution:overextended=135, setup_compat:regime_VOLATILE_UNSUITABLE=120, context_edge=3
- **TREND_PULLBACK_EMA** (total=1745): setup_compat:regime_CLEAN_RANGE=1188, setup_compat:regime_DIRTY_RANGE=483, setup_compat:regime_VOLATILE_UNSUITABLE=58, entry_quality=16
- **VOLUME_SURGE_BREAKOUT** (total=33): execution:overextended=33
- **WHALE_MOMENTUM** (total=81): execution:trigger_not_confirmed=81

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 197275 | 45.8% |
| QUIET | 92381 | 21.4% |
| TRENDING_UP | 64087 | 14.9% |
| TRENDING_DOWN | 51029 | 11.8% |
| VOLATILE | 25944 | 6.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **69**
- Average confidence gap to threshold: **13.70** (samples=69) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=23, 1000SHIBUSDT=9, SUIUSDT=7, TAOUSDT=6, HBARUSDT=6, ONDOUSDT=5, ETHUSDT=4, AAVEUSDT=3, ICPUSDT=2, LTCUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 45 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 48 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 29 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 12 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 11 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 49 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 5 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 93 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 4 |
| MEAN_REVERT | filtered | min_confidence | 51 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 18 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 321 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 391 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 277 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1580 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 49 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 39 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 49 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 4 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 87 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 2 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 28 |
| WHALE_MOMENTUM | filtered | min_confidence | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 48 | 55.77 | 62.46 | 6.69 | 20.64 | 19.81 | 16.74 | 1.02 | 11.13 |
| DIVERGENCE_CONTINUATION | kept | 48 | 68.44 | 65.00 | -3.44 | 20.79 | 19.72 | 18.24 | 1.83 | 4.81 |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 58.38 | 64.12 | 5.74 | 21.40 | 19.93 | 20.00 | 2.83 | 9.56 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 71.44 | 65.00 | -6.44 | 21.30 | 19.78 | 20.00 | 2.64 | 1.64 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 48.50 | 61.00 | 12.50 | 21.20 | 14.00 | 17.00 | 3.40 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 54 | 51.45 | 64.19 | 12.74 | 18.57 | 18.06 | 18.23 | 3.61 | 18.48 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 93 | 71.13 | 65.00 | -6.13 | 21.10 | 18.46 | 17.80 | 2.14 | 0.52 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.88 | 65.00 | -4.88 | 20.85 | 18.48 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 52 | 56.63 | 64.08 | 7.45 | 21.85 | 14.23 | 16.93 | 0.00 | 12.30 |
| MEAN_REVERT | kept | 18 | 66.06 | 65.00 | -1.06 | 22.14 | 17.68 | 14.76 | 0.00 | 0.67 |
| MOVER_AVWAP_SCALP | filtered | 321 | 59.37 | 64.99 | 5.62 | 20.62 | 17.62 | 15.80 | 4.23 | 9.84 |
| MOVER_AVWAP_SCALP | kept | 391 | 82.46 | 65.00 | -17.46 | 18.82 | 15.23 | 15.80 | 4.42 | 1.66 |
| MOVER_TREND_PULLBACK | filtered | 282 | 58.67 | 64.49 | 5.82 | 20.66 | 17.71 | 15.80 | 3.81 | 12.92 |
| MOVER_TREND_PULLBACK | kept | 1580 | 76.10 | 65.00 | -11.10 | 20.12 | 18.30 | 15.80 | 4.13 | 1.36 |
| QUIET_COMPRESSION_BREAK | filtered | 88 | 53.07 | 64.55 | 11.48 | 21.07 | 19.09 | 20.00 | 0.00 | 16.43 |
| QUIET_COMPRESSION_BREAK | kept | 49 | 72.10 | 65.00 | -7.10 | 22.27 | 19.36 | 20.00 | 0.00 | -0.53 |
| SR_FLIP_RETEST | filtered | 4 | 56.10 | 65.00 | 8.90 | 23.80 | 20.00 | 15.20 | 2.50 | 18.60 |
| SR_FLIP_RETEST | kept | 87 | 69.80 | 65.00 | -4.80 | 21.89 | 20.00 | 15.75 | 2.07 | 0.16 |
| TREND_PULLBACK_EMA | filtered | 2 | 56.50 | 65.00 | 8.50 | 22.60 | 20.00 | 15.30 | 6.00 | 20.00 |
| TREND_PULLBACK_EMA | kept | 28 | 81.31 | 65.00 | -16.31 | 21.21 | 19.70 | 18.38 | 5.05 | -1.18 |
| WHALE_MOMENTUM | filtered | 17 | 41.84 | 62.18 | 20.34 | 24.36 | 18.59 | 17.00 | 0.00 | 27.32 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 48 | 55.77 | 20.83 | 10.50 | 8.19 | 13.81 | 5.38 | 8.55 | 1.02 |
| DIVERGENCE_CONTINUATION | kept | 48 | 68.44 | 20.50 | 14.46 | 7.62 | 14.42 | 5.71 | 9.08 | 1.83 |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 58.38 | 20.41 | 16.83 | 5.78 | 12.24 | 5.94 | 3.90 | 2.83 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 71.44 | 23.55 | 15.82 | 7.91 | 13.00 | 5.50 | 4.66 | 2.64 |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 48.50 | 25.00 | 8.00 | 3.60 | 15.00 | 8.80 | 4.70 | 3.40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 54 | 51.45 | 24.19 | 14.00 | 5.44 | 12.26 | 6.49 | 3.94 | 3.61 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 93 | 71.13 | 21.30 | 14.30 | 8.87 | 12.97 | 6.68 | 5.38 | 2.14 |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.88 | 17.00 | 14.00 | 10.50 | 13.25 | 6.62 | 8.50 | 0.00 |
| MEAN_REVERT | filtered | 52 | 56.63 | 24.54 | 14.23 | 6.40 | 12.94 | 5.00 | 5.82 | 0.00 |
| MEAN_REVERT | kept | 18 | 66.06 | 23.56 | 14.89 | 6.83 | 12.67 | 5.00 | 3.78 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 321 | 59.37 | 16.77 | 18.00 | 12.33 | 14.00 | 6.43 | 5.78 | 4.23 |
| MOVER_AVWAP_SCALP | kept | 391 | 82.46 | 21.45 | 18.07 | 12.05 | 13.97 | 7.56 | 6.88 | 4.42 |
| MOVER_TREND_PULLBACK | filtered | 282 | 58.67 | 17.36 | 18.00 | 8.06 | 12.10 | 6.20 | 8.88 | 3.81 |
| MOVER_TREND_PULLBACK | kept | 1580 | 76.10 | 19.06 | 18.03 | 7.82 | 12.82 | 6.72 | 8.96 | 4.13 |
| QUIET_COMPRESSION_BREAK | filtered | 88 | 53.07 | 17.00 | 15.77 | 12.07 | 14.44 | 7.43 | 3.17 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 49 | 72.10 | 18.14 | 16.69 | 11.51 | 14.00 | 7.00 | 6.55 | 0.00 |
| SR_FLIP_RETEST | filtered | 4 | 56.10 | 25.00 | 8.00 | 6.00 | 17.00 | 8.50 | 7.70 | 2.50 |
| SR_FLIP_RETEST | kept | 87 | 69.80 | 22.43 | 12.94 | 4.34 | 16.24 | 6.76 | 6.65 | 2.07 |
| TREND_PULLBACK_EMA | filtered | 2 | 56.50 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 6.00 |
| TREND_PULLBACK_EMA | kept | 28 | 81.31 | 19.86 | 18.00 | 7.55 | 13.14 | 8.71 | 8.99 | 5.05 |
| WHALE_MOMENTUM | filtered | 17 | 41.84 | 25.00 | 18.00 | 4.24 | 15.12 | 6.65 | 0.16 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 48 | 55.77 | 0.00 | 0.00 | 2.53 | 0.00 | 3.50 | 0.00 | 0.00 | 0.00 | **6.03** |
| DIVERGENCE_CONTINUATION | kept | 48 | 68.44 | 0.00 | 0.00 | 3.60 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | **4.10** |
| FAILED_AUCTION_RECLAIM | filtered | 41 | 58.38 | 0.00 | 0.00 | 0.00 | 0.00 | 5.27 | 0.00 | 0.00 | 0.00 | **5.27** |
| FAILED_AUCTION_RECLAIM | kept | 11 | 71.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 5 | 48.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 54 | 51.45 | 0.00 | 0.00 | 0.00 | 0.00 | 2.00 | 0.00 | 0.00 | 0.00 | **2.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 93 | 71.13 | 0.00 | 0.00 | 0.26 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.52** |
| MA_CROSS_TREND_SHIFT | kept | 4 | 69.88 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 52 | 56.63 | 0.00 | 0.00 | 0.31 | 0.00 | 0.88 | 0.00 | 0.00 | 0.00 | **1.19** |
| MEAN_REVERT | kept | 18 | 66.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | **0.67** |
| MOVER_AVWAP_SCALP | filtered | 321 | 59.37 | 0.00 | 0.00 | 0.00 | 0.00 | 1.31 | 0.03 | 0.00 | 1.31 | **2.65** |
| MOVER_AVWAP_SCALP | kept | 391 | 82.46 | 0.04 | 0.00 | 0.16 | 0.00 | 0.53 | 0.05 | 0.00 | 0.06 | **0.84** |
| MOVER_TREND_PULLBACK | filtered | 282 | 58.67 | 1.31 | 0.00 | 0.12 | 0.00 | 2.94 | 0.11 | 0.00 | 0.26 | **4.74** |
| MOVER_TREND_PULLBACK | kept | 1580 | 76.10 | 0.00 | 0.00 | 1.00 | 0.00 | 0.11 | 0.02 | 0.00 | 0.01 | **1.14** |
| QUIET_COMPRESSION_BREAK | filtered | 88 | 53.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 5.17 | **5.46** |
| QUIET_COMPRESSION_BREAK | kept | 49 | 72.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.56 | **0.82** |
| SR_FLIP_RETEST | filtered | 4 | 56.10 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| SR_FLIP_RETEST | kept | 87 | 69.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 2 | 56.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 28 | 81.31 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 17 | 41.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **73107 held of 162746 seen** across 21 strategies; 1636 cells past the sample floor; **681 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 29974 | 258/29716/0 | 46% | -0.13 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/MARKUP/COMPRESSED/BTC_RISING/MIDCAP (-1.10R) |
| MOVER_AVWAP_SCALP | 9158 | 43/9115/0 | 42% | -0.24 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5803 | 31/5772/0 | 41% | -0.22 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 3922 | 24/3898/0 | 51% | -0.01 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.04R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 3720 | 0/0/3720 | 42% | -0.10 | ASIA/RANGE/NORMAL/BTC_RISING (+0.28R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.05R) |
| TREND_PULLBACK_EMA | 3492 | 6/3486/0 | 45% | -0.19 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| QUIET_COMPRESSION_BREAK | 3476 | 79/3397/0 | 46% | -0.15 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.72R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 3127 | 0/0/3127 | 37% | -0.09 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.34R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.98R) |
| SHADOW_FUNDING_FADE | 2568 | 0/0/2568 | 36% | -0.39 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-0.99R) |
| WHALE_MOMENTUM | 2058 | 2/2056/0 | 39% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1674 | 12/1662/0 | 35% | -0.33 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.62R) |
| MEAN_REVERT | 1042 | 12/1030/0 | 63% | +0.22 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 892 | 2/890/0 | 30% | -0.49 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 848 | 0/848/0 | 51% | -0.04 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 422 | 0/422/0 | 58% | -0.18 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-0.91R) |
| SHADOW_CASCADE_REVERSAL | 387 | 0/0/387 | 55% | -0.03 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.31R) |
| RANGE_FADE | 238 | 0/238/0 | 49% | -0.34 | LONDON/ACCUMULATION/EXPANDED/BTC_FALLING (-0.08R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 188 | 12/176/0 | 21% | -0.58 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 70 | 0/70/0 | 3% | -1.19 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.34R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.34R) |
| MA_CROSS_TREND_SHIFT | 44 | 6/38/0 | 32% | -0.23 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING` +1.44R (n=23, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.62R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.50R (n=20, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 94 | 33% / -0.44R | 94 | 50% / -0.12R | +0.32 | **ATR** |
| TREND_PULLBACK_EMA | 301 | 49% / -0.15R | 301 | 56% / -0.03R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 246 | 43% / -0.34R | 246 | 44% / -0.24R | +0.10 | **ATR** |
| MOVER_AVWAP_SCALP | 688 | 47% / -0.17R | 688 | 52% / -0.08R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 454 | 44% / -0.18R | 454 | 46% / -0.09R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4591 | 51% / -0.08R | 4591 | 55% / -0.00R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 69 | 46% / -0.33R | 69 | 48% / -0.24R | +0.08 | **ATR** |
| RANGE_FADE | 18 | 44% / -0.04R | 18 | 44% / -0.12R | -0.08 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 15 | 33% / -0.24R | 15 | 33% / -0.19R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 58 | 48% / -0.04R | 58 | 55% / +0.01R | +0.05 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 333 | 51% / -0.20R | 333 | 55% / -0.16R | +0.04 | **ATR** |
| BREAKDOWN_SHORT | 19 | 32% / -0.13R | 19 | 32% / -0.10R | +0.03 | **ATR** |
| MEAN_REVERT | 95 | 58% / +0.05R | 95 | 56% / +0.07R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 561 | 45% / -0.17R | 561 | 45% / -0.18R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 423 | 53% / -0.02R | 423 | 58% / -0.02R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 5 | 20% / -0.78R | 5 | 60% / -0.04R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6881 | 32% | -0.12R | 282 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 688 | 49% | -0.07R | 159 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 40 | 57% | -0.01R | 33 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 85 | 35% / -0.24R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 524 | 38% / -0.02R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5800 | 37% / -0.12R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 809 | 35% / -0.02R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 348 | 37% / -0.04R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 463 | 41% / +0.09R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 392 | 38% / -0.09R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 328 | 45% / -0.14R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 82 | 29% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 106 | 30% / -0.62R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 72 | 56% / +0.14R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 36 | 42% / -0.00R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 16 | 38% / +0.01R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 69 | 30% / -0.39R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 20 | 15% / -0.69R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 8 | 38% / +0.22R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **0** · boot grace active: False

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 785943 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 2/3) | 2 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 40 arms current, none stalled; covering 523/523 signals (100%) | 0 |
| auto_dispatch | ok | placed=2 rejected=0 skipped=2 over 2 fan-out(s) to a keyed roster; top reasons: mode=2 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 81012.70 | 0 |
| candle_coverage | ok | 83/83 symbols with ≥20 15m candles, 83/83 updated within 45m [fresh=83; 75 Tier-1 futures + 8 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 352 dup bars, 0 undedupable; ws 0 out-of-order, 72 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +6 / upstream +36 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1123/1140 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 115 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1117/1134 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 202114 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.51R (bound 0.3) (streak 2/6) | 2 |
| emission_controller | ok | last cycle 329s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×382]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 2/6) | 2 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/105 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | ok | 1760 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +253 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 186 frozen value(s) avoided; 0 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 507 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.21R over n=1030, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 2/6) | 2 |
| mean_revert_path | ok | output +72 / upstream +253 | 0 |
| mover_admission_metadata | ok | 893 symbols known, 189 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 8 held, 8 with scan counts, 8 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2928 rows held, 1003632 evicted (sampled: execution:trigger_not_confirmed 400/367842, execution:overextended 400/346787, setup_compat:regime_STRONG_TREND 400/135985) | 0 |
| price_action_lane | ok | 21393 evaluated, 19 emitted; layer1 19 stamped / 0 blind; cooldown=2910, delta_opposed=2434, no_footprint=6934, no_sweep=7017, rr_below_floor=2079 | 0 |
| promoted_pair_integrity | ok | 8/8 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.34R over n=238 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +63 / upstream +253 | 0 |
| sar_alignment_crosscheck | violating | 16/220 disagreed (7.3%) (streak 2/6) | 2 |
| sar_exit_shadow | violating | upstream +253 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 869 held arms settled, 155 unscored, 40 still walking (36 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 58/86 unfetchable (67%); top cause: gap or duplicate bar in the 15m window; symbols: 1000SHIBUSDT, AKEUSDT, APTUSDT, ASTERUSDT, AVAXUSDT +21 more (streak 2/6) | 2 |
| sar_live_arms | ok | 40 arms current, none stalled; covering 532/532 signals (100%) | 0 |
| sar_refresh_budget | ok | 0 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 486 records await one (28 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 2/12) | 2 |
| scan_cycle | ok | last 12.01s, worst 55.33s over 267 lifetime cycles; lifetime 0 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 0.62s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 8881 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| snapshot_writer | ok | last cycle 18s ago (0.6s to run, worst 30.68s), 7 overrun(s) of 166 cycles, TTL 900s; slowest signals=0.92s, activity=0.17s, engine_state=0.15s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +16 / upstream +253 | 0 |
| structural_snap | ok | 4562/4562 measured, 11 blind, 0 levels moved (refusals: redetect_cooldown=13) | 0 |
| structural_veto_lane | ok | 22 stamped; 0 with no readable level book, 0 with clear air ahead, 12 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +253 / upstream +36 | 0 |
| tuned_variants | violating | 32 non-stamps — atr_arm_uncomputable=32 (seen=109 stamped=9 skipped=68) (streak 2/6) | 2 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2174776`
- `Path funnel` emissions: `52`
- `Regime distribution` emissions: `52`
- `QUIET_SCALP_BLOCK` events: `69`
- `confidence_gate` events: `3223`
- `free_channel_post` events: `36`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **21**
- Total REST-fallback activations: **5**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 10 | 2956 | 4712 | 12742 | 0 |
| futures_aggtrade | 3 | 8713 | 8713 | 14578 | 0 |
| futures_depth | 5 | 4146 | 4376 | 9662 | 0 |
| futures_liq | 2 | 3080 | 3080 | 11342 | 0 |
| futures_mover | 1 | 2487 | 2487 | 2487 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 5 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **36**

| Source | Count |
|---|---:|
| signal_close | 34 |
| regime_shift | 2 |

- By severity: HIGH=36

## Dependency readiness
- cvd: presence[present=351026] state[populated=351026] buckets[many=351026] sources[none] quality[none]
- funding_rate: presence[absent=37818, present=313208] state[empty=37818, populated=313208] buckets[few=313208, none=37818] sources[none] quality[none]
- liquidation_clusters: presence[absent=184886, present=166140] state[empty=184886, populated=166140] buckets[few=130818, none=184886, some=35322] sources[none] quality[none]
- oi_snapshot: presence[absent=35160, present=315866] state[empty=35160, populated=315866] buckets[many=315866, none=35160] sources[none] quality[none]
- order_book: presence[absent=98642, present=252384] state[populated=252384, unavailable=98642] buckets[few=252384, none=98642] sources[book_ticker=252384, unavailable=98642] quality[none=98642, top_of_book_only=252384]
- orderblocks: presence[absent=351026] state[empty=351026] buckets[none=351026] sources[measured_dark=351026] quality[none]
- recent_ticks: presence[present=351026] state[populated=351026] buckets[many=351026] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `12.768896460533142` sec
- Median create→first breach: `4609.645058393478` sec
- Median create→terminal: `4616.164102435112` sec
- Median first breach→terminal: `5.96398651599884` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.887464154312634 | 1.1905898478922816 | 0.7453987247444824 | 0 | 1 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.679056532594348 | 1.9143162911590017 | 0.8780743342646722 | 0 | 2 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 10.568593749999987 | 2.978999999999998 | 3.5476984726418244 | 1 | 0 |
| MOVER_AVWAP_SCALP | 2 | 2 | 3.857201305766508 | 3.0 | 1.2857337685888361 | 2 | 0 |
| MOVER_TREND_PULLBACK | 22 | 22 | 3.3447728464680737 | 3.0 | 1.1149242821560246 | 14 | 8 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.1204712343400152 | 1.2685634448768193 | 0.8847991033792102 | 0 | 6 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.7749 | 7674.4671750068665 | 7678.099762201309 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.6791 | 10292.230268001556 | 10297.911130428314 |
| MA_CROSS_TREND_SHIFT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.979 | 26829.178332090378 | 26832.48781299591 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 0.1965 | 572.5460509061813 | 577.8442199230194 |
| MOVER_TREND_PULLBACK | 22 | 22 | 0.0 | 40.9 | 0.0 | 0.0 | 0.8402 | 3272.419129014015 | 3492.9452369213104 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 50.0 | 33.3 | 50.0 | 0.0 | 0.608 | 18909.618726968765 | 18915.59826898575 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 287 | 4 | 104 | 0.0 | 0.0 | None | None | 183 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2026 | 13 | 1901 | 0.0 | 0.0 | None | None | 125 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-283`
- Gating Δ: `37902`
- No-generation Δ: `275682`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -1.5601, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 1.5601, "previous_win_rate": 66.7, "win_rate_delta": -66.7}, "MEAN_REVERT": {"avg_pnl_delta": -0.4456, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.4456, "previous_win_rate": 33.3, "win_rate_delta": -33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.0272, "current_avg_pnl": 0.8402, "current_win_rate": 0.0, "previous_avg_pnl": -0.187, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 1.6073, "current_avg_pnl": 0.608, "current_win_rate": 50.0, "previous_avg_pnl": -0.9993, "previous_win_rate": 0.0, "win_rate_delta": 50.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -7, "geometry_changed_delta": 0, "geometry_preserved_delta": 81, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -25, "geometry_changed_delta": 0, "geometry_preserved_delta": -141, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -3928.36, "median_terminal_delta_sec": -3929.37, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **QUIET_COMPRESSION_BREAK**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
