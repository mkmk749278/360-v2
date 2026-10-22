# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `2372` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 145 | 145 | 145 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 8253 | 8253 | 8047 | 4 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 54568 | 54554 | 58 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 50106 | 50107 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 49602 | 47733 | 2363 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50139 | 49424 | 816 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 51467 | 51290 | 221 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 40961 | 40982 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50243 | 50290 | 7 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 50303 | 48360 | 2826 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 59955 | 65944 | 1055 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 54616 | 48652 | 11244 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 50963 | 50964 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50109 | 50134 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 49563 | 49467 | 133 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 51198 | 49639 | 2259 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 49017 | 49410 | 103 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 38921 | 36472 | 2813 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 39292 | 38806 | 594 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 54519 | 54528 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 40988 | 41014 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2893 | 2893 | 2834 | 1 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 707 | 707 | 583 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14453 | 14453 | 14301 | 15 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 12 | 12 | 11 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 6544 | 6544 | 5911 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2320 | 2320 | 2048 | 19 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 28338 | 28338 | 24286 | 115 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 585 | 585 | 522 | 11 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 5368 | 5368 | 5341 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 319 | 319 | 281 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1903 | 1903 | 1847 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 95 | 95 | 95 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=54554): breakout_not_found=30746, move_not_fresh=9868, basic_filters_failed=9439, breakout_stale=3016, retest_proximity_failed=749, volume_spike_missing=693, missing_fvg_or_orderblock=27, move_exhausted=15, ema_alignment_reject=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=50107): cls_disabled_merged_into_lsr=50107
- **EVAL::DIVERGENCE_CONTINUATION** (total=47733): cvd_divergence_failed=24624, h1_trend_not_aligned=12185, basic_filters_failed=6885, ema_alignment_reject=3250, retest_proximity_failed=649, missing_fvg_or_orderblock=140
- **EVAL::FAILED_AUCTION_RECLAIM** (total=49424): auction_not_detected=35357, basic_filters_failed=6508, reclaim_hold_failed=3316, tail_too_small=2274, regime_blocked=1948, rsi_reject=21
- **EVAL::FUNDING_EXTREME** (total=51290): funding_not_extreme=39993, basic_filters_failed=6468, missing_funding_rate=2025, ema_alignment_reject=1860, rsi_reject=480, momentum_reject=228, cvd_divergence_failed=204, missing_fvg_or_orderblock=32
- **EVAL::LIQUIDATION_REVERSAL** (total=40982): cascade_threshold_not_met=33367, basic_filters_failed=7031, rsi_reject=277, cvd_divergence_failed=274, missing_fvg_or_orderblock=30, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50290): no_ma_cross=42511, basic_filters_failed=6897, ma_cross_cooldown=555, ma_cross_htf_misaligned=327
- **EVAL::MEAN_REVERT** (total=48360): no_extension=43082, basic_filters_failed=5278
- **EVAL::MOVER_AVWAP_SCALP** (total=65944): no_avwap_tag=28478, no_mover_leg=19347, basic_filters_failed=9571, avwap_slope_against=5339, avwap_reclaim_no_volume=1844, no_avwap_reclaim=1328, anchor_too_recent=37
- **EVAL::MOVER_TREND_PULLBACK** (total=48652): mover_run_too_small=25332, no_reclaim=12132, basic_filters_failed=9506, no_pullback_tag=1682
- **EVAL::OPENING_RANGE_BREAKOUT** (total=50964): feature_disabled=50964
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50134): regime_blocked=28214, breakout_not_found=17989, basic_filters_failed=2007, adx_reject=1836, ema_alignment_reject=88
- **EVAL::QUIET_COMPRESSION_BREAK** (total=49467): regime_blocked=23635, compression_not_detected=17482, basic_filters_failed=4493, breakout_not_detected=3057, macd_reject=432, volume_confirmation_failed=367, missing_fvg_or_orderblock=1
- **EVAL::RANGE_FADE** (total=49639): no_range_edge=44353, basic_filters_failed=5286
- **EVAL::SR_FLIP_RETEST** (total=49410): flip_close_not_confirmed=34847, basic_filters_failed=6491, long_break_volume_thin=2346, regime_blocked=1935, h1_break_not_confirmed=1854, retest_out_of_zone=1212, reclaim_hold_failed=355, long_acceptance_not_held=222, ema_alignment_reject=81, wick_quality_failed=35, whipsaw_flip=19, missing_fvg_or_orderblock=13
- **EVAL::STANDARD** (total=36472): momentum_reject=11938, adx_reject=8908, ema_alignment_reject=4476, sweeps_not_detected=3810, basic_filters_failed=3510, macd_reject=3068, htf_poi_unanchored=705, rsi_reject=27, invalid_sl_geometry=22, mtf_reject=8
- **EVAL::TREND_PULLBACK** (total=38806): h1_trend_not_aligned=10455, ema_alignment_reject=7947, h1_pullback_not_confirmed=4556, basic_filters_failed=4555, ema_not_tested_prev=3400, no_ema_reclaim_close=3257, body_conviction_fail=1856, rsi_reject=1495, prev_already_above_emas=591, no_prev_high_break=321, prev_already_below_emas=145, no_prev_low_break=121, momentum_flat=56, ema21_not_tagged=25, missing_fvg_or_orderblock=20, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=54528): breakout_not_found=34707, basic_filters_failed=9434, move_not_fresh=6277, breakout_stale=2509, retest_proximity_failed=890, volume_spike_missing=628, move_exhausted=80, missing_fvg_or_orderblock=3
- **EVAL::WHALE_MOMENTUM** (total=41014): momentum_reject=25446, recent_ticks_insufficient=13506, basic_filters_failed=2062

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=2): execution:overextended=2
- **DIVERGENCE_CONTINUATION** (total=190): setup_compat:regime_VOLATILE_UNSUITABLE=190
- **FAILED_AUCTION_RECLAIM** (total=938): setup_compat:regime_STRONG_TREND=574, execution:overextended=342, context_floor=20, setup_compat:regime_VOLATILE_UNSUITABLE=2
- **FUNDING_EXTREME_SIGNAL** (total=616): execution:trigger_not_confirmed=598, context_floor=18
- **LIQUIDATION_REVERSAL** (total=13): execution:trigger_not_confirmed=13
- **LIQUIDITY_SWEEP_REVERSAL** (total=3769): execution:trigger_not_confirmed=1495, setup_compat:regime_STRONG_TREND=1474, execution:overextended=800
- **MA_CROSS_TREND_SHIFT** (total=9): setup_compat:regime_DIRTY_RANGE=3, setup_compat:regime_CLEAN_RANGE=3, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:trigger_not_confirmed=1, execution:overextended=1
- **MEAN_REVERT** (total=5634): setup_compat:regime_STRONG_TREND=2825, setup_compat:regime_WEAK_TREND=2391, execution:overextended=418
- **MOVER_AVWAP_SCALP** (total=909): execution:overextended=698, execution:trigger_not_confirmed=180, entry_quality=31
- **MOVER_TREND_PULLBACK** (total=10184): execution:trigger_not_confirmed=6116, execution:overextended=3670, entry_quality=398
- **RANGE_FADE** (total=4088): setup_compat:regime_STRONG_TREND=2054, setup_compat:regime_WEAK_TREND=1398, execution:overextended=357, setup_compat:regime_VOLATILE_UNSUITABLE=270, setup_compat:regime_BREAKOUT_EXPANSION=9
- **TREND_PULLBACK_EMA** (total=1482): setup_compat:regime_CLEAN_RANGE=1033, setup_compat:regime_DIRTY_RANGE=414, setup_compat:regime_VOLATILE_UNSUITABLE=21, entry_quality=14
- **VOLUME_SURGE_BREAKOUT** (total=4): execution:overextended=4

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 88999 | 32.0% |
| TRENDING_DOWN | 63779 | 22.9% |
| QUIET | 58328 | 21.0% |
| TRENDING_UP | 56077 | 20.2% |
| VOLATILE | 10813 | 3.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **66**
- Average confidence gap to threshold: **8.45** (samples=66) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BATUSDT=22, QUSDT=11, BTCUSDT=10, XLMUSDT=8, XRPUSDT=5, DOGEUSDT=5, LTCUSDT=2, WLDUSDT=1, SUIUSDT=1, LINKUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 35 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 8 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 22 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 42 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 21 |
| MA_CROSS_TREND_SHIFT | kept | min_confidence_pass | 1 |
| MEAN_REVERT | filtered | min_confidence | 43 |
| MEAN_REVERT | kept | min_confidence_pass | 13 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 116 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 80 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1140 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 31 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 729 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 30 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 21 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 10 |
| SR_FLIP_RETEST | filtered | min_confidence | 7 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 14 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 25 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 35 | 52.81 | 63.74 | 10.93 | 20.12 | 19.81 | 17.23 | 2.94 | 17.49 |
| DIVERGENCE_CONTINUATION | kept | 8 | 70.91 | 65.00 | -5.91 | 20.30 | 19.64 | 18.94 | 2.75 | 2.25 |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 50.02 | 61.00 | 10.98 | 19.54 | 15.16 | 20.00 | 1.27 | 3.82 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.80 | 65.00 | -1.80 | 20.90 | 14.44 | 20.00 | 2.70 | 9.60 |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 53.30 | 61.00 | 7.70 | 20.05 | 13.60 | 17.00 | 3.00 | 12.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 44 | 54.91 | 63.20 | 8.29 | 21.94 | 18.03 | 16.73 | 2.84 | 13.96 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 71.89 | 65.00 | -6.89 | 20.92 | 19.52 | 18.60 | 1.81 | 0.21 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.00 | 65.00 | -13.00 | 20.40 | 20.00 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 43 | 44.52 | 65.00 | 20.48 | 23.07 | 15.00 | 17.70 | 0.00 | 28.32 |
| MEAN_REVERT | kept | 13 | 71.39 | 65.00 | -6.39 | 18.71 | 14.00 | 20.00 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 116 | 59.87 | 65.00 | 5.13 | 18.76 | 16.12 | 15.80 | 4.09 | 19.51 |
| MOVER_AVWAP_SCALP | kept | 80 | 74.83 | 65.00 | -9.83 | 19.57 | 15.80 | 15.80 | 4.17 | 5.87 |
| MOVER_TREND_PULLBACK | filtered | 1171 | 56.27 | 64.13 | 7.86 | 20.75 | 18.59 | 15.80 | 4.05 | 17.51 |
| MOVER_TREND_PULLBACK | kept | 729 | 74.43 | 65.00 | -9.43 | 20.74 | 18.54 | 15.80 | 4.08 | 3.96 |
| QUIET_COMPRESSION_BREAK | filtered | 51 | 52.82 | 65.00 | 12.18 | 20.37 | 19.60 | 20.00 | 0.00 | 16.56 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 70.21 | 65.00 | -5.21 | 21.60 | 19.75 | 20.00 | 0.00 | 5.98 |
| SR_FLIP_RETEST | filtered | 7 | 56.07 | 61.57 | 5.50 | 19.30 | 20.00 | 15.20 | 2.50 | 15.70 |
| SR_FLIP_RETEST | kept | 1 | 66.30 | 65.00 | -1.30 | 21.20 | 20.00 | 20.00 | 2.00 | 3.00 |
| TREND_PULLBACK_EMA | filtered | 17 | 58.24 | 65.00 | 6.76 | 21.58 | 20.00 | 18.16 | 4.76 | 10.52 |
| TREND_PULLBACK_EMA | kept | 25 | 78.14 | 65.00 | -13.14 | 19.64 | 19.82 | 19.40 | 5.60 | 3.89 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 35 | 52.81 | 24.31 | 11.71 | 4.71 | 13.43 | 5.26 | 7.93 | 2.94 |
| DIVERGENCE_CONTINUATION | kept | 8 | 70.91 | 23.00 | 16.75 | 3.75 | 13.25 | 5.44 | 8.60 | 2.75 |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 50.02 | 18.45 | 14.00 | 7.91 | 14.00 | 8.50 | 4.70 | 1.27 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.80 | 25.00 | 14.00 | 9.00 | 14.00 | 5.00 | 6.70 | 2.70 |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 53.30 | 17.00 | 18.00 | 3.00 | 12.00 | 5.00 | 7.30 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 44 | 54.91 | 24.45 | 14.27 | 4.64 | 12.34 | 4.94 | 6.75 | 2.84 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 71.89 | 20.81 | 15.90 | 8.71 | 11.90 | 5.24 | 7.91 | 1.81 |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.00 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 8.00 | 0.00 |
| MEAN_REVERT | filtered | 43 | 44.52 | 22.21 | 14.93 | 12.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MEAN_REVERT | kept | 13 | 71.39 | 25.00 | 17.69 | 3.00 | 13.00 | 5.00 | 7.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 116 | 59.87 | 20.59 | 18.00 | 12.36 | 13.48 | 6.21 | 4.66 | 4.09 |
| MOVER_AVWAP_SCALP | kept | 80 | 74.83 | 18.18 | 18.15 | 13.65 | 13.64 | 6.18 | 6.97 | 4.17 |
| MOVER_TREND_PULLBACK | filtered | 1171 | 56.27 | 18.64 | 18.00 | 7.63 | 11.88 | 6.38 | 8.24 | 4.05 |
| MOVER_TREND_PULLBACK | kept | 729 | 74.43 | 19.88 | 18.01 | 7.84 | 12.92 | 7.03 | 8.72 | 4.08 |
| QUIET_COMPRESSION_BREAK | filtered | 51 | 52.82 | 18.10 | 16.35 | 10.24 | 14.00 | 7.08 | 3.61 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 10 | 70.21 | 19.40 | 17.60 | 13.20 | 14.00 | 7.65 | 4.33 | 0.00 |
| SR_FLIP_RETEST | filtered | 7 | 56.07 | 25.00 | 18.00 | 3.00 | 10.57 | 5.00 | 7.79 | 2.50 |
| SR_FLIP_RETEST | kept | 1 | 66.30 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 7.30 | 2.00 |
| TREND_PULLBACK_EMA | filtered | 17 | 58.24 | 6.41 | 18.00 | 7.50 | 14.00 | 9.56 | 8.53 | 4.76 |
| TREND_PULLBACK_EMA | kept | 25 | 78.14 | 20.24 | 18.00 | 8.64 | 14.12 | 6.12 | 9.55 | 5.60 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 35 | 52.81 | 0.00 | 0.00 | 3.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.38** |
| DIVERGENCE_CONTINUATION | kept | 8 | 70.91 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.00** |
| FAILED_AUCTION_RECLAIM | filtered | 22 | 50.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 66.80 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 53.30 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 44 | 54.91 | 0.00 | 0.00 | 2.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.95** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 21 | 71.89 | 0.00 | 0.00 | 0.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.38** |
| MA_CROSS_TREND_SHIFT | kept | 1 | 78.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 43 | 44.52 | 0.00 | 0.00 | 0.00 | 0.00 | 8.32 | 0.00 | 0.00 | 0.00 | **8.32** |
| MEAN_REVERT | kept | 13 | 71.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 116 | 59.87 | 0.00 | 0.00 | 1.08 | 0.00 | 0.43 | 0.00 | 0.00 | 1.91 | **3.42** |
| MOVER_AVWAP_SCALP | kept | 80 | 74.83 | 0.19 | 0.00 | 0.00 | 0.00 | 3.09 | 0.00 | 0.00 | 0.62 | **3.90** |
| MOVER_TREND_PULLBACK | filtered | 1171 | 56.27 | 0.00 | 0.00 | 0.97 | 0.00 | 0.22 | 0.00 | 0.00 | 0.01 | **1.20** |
| MOVER_TREND_PULLBACK | kept | 729 | 74.43 | 0.01 | 0.00 | 1.20 | 0.00 | 0.21 | 0.00 | 0.00 | 0.00 | **1.42** |
| QUIET_COMPRESSION_BREAK | filtered | 51 | 52.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.93 | 0.00 | 0.00 | 4.59 | **5.52** |
| QUIET_COMPRESSION_BREAK | kept | 10 | 70.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.16 | **2.16** |
| SR_FLIP_RETEST | filtered | 7 | 56.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 1 | 66.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 17 | 58.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 25 | 78.14 | 0.00 | 0.00 | 6.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.08** |

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
- Outcomes recorded: **153027 held of 567744 seen** across 21 strategies; 3482 cells past the sample floor; **1776 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 44942 | 705/44237/0 | 45% | -0.16 | OVERLAP/QUIET/COMPRESSED/BTC_RISING/MAJOR (+1.19R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.28R) |
| MOVER_AVWAP_SCALP | 19759 | 193/19566/0 | 43% | -0.21 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL/MAJOR (+1.30R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 11617 | 123/11494/0 | 37% | -0.27 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (+1.77R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 10918 | 109/10809/0 | 48% | -0.07 | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (+2.35R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| TREND_PULLBACK_EMA | 9144 | 43/9101/0 | 41% | -0.20 | NY/MARKUP/NORMAL/BTC_NEUTRAL/MAJOR (+2.01R) | LONDON/ACCUMULATION/NORMAL/BTC_FALLING (-1.30R) |
| LIQUIDITY_SWEEP_REVERSAL | 8241 | 83/8158/0 | 35% | -0.50 | NY/MARKUP/COMPRESSED/BTC_FALLING (+2.27R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL (-1.64R) |
| SHADOW_MEAN_REVERT | 7359 | 0/0/7359 | 42% | -0.12 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.48R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.03R) |
| SHADOW_RANGE_FADE | 6805 | 0/0/6805 | 36% | -0.14 | LONDON/QUIET/COMPRESSED/BTC_FALLING (+0.53R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.20R) |
| QUIET_COMPRESSION_BREAK | 6389 | 424/5965/0 | 49% | -0.12 | NY/RANGE/NORMAL/BTC_FALLING/ALTCOIN (+1.96R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 5952 | 0/0/5952 | 34% | -0.41 | NY/RANGE/EXPANDED/BTC_FALLING (-0.01R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.99R) |
| MEAN_REVERT | 4223 | 46/4177/0 | 37% | -0.32 | LONDON/QUIET/NORMAL/BTC_FALLING (+1.68R) | OFF_HOURS/MARKDOWN/CASCADE/BTC_NEUTRAL (-1.32R) |
| SR_FLIP_RETEST | 3814 | 15/3799/0 | 45% | -0.29 | NY/RANGE/EXPANDED/BTC_NEUTRAL/MIDCAP (+1.18R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.30R) |
| WHALE_MOMENTUM | 3793 | 4/3789/0 | 45% | -0.34 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.61R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| VOLUME_SURGE_BREAKOUT | 3126 | 0/3126/0 | 31% | -0.34 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 3042 | 2/3040/0 | 31% | -0.49 | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+1.01R) | OFF_HOURS/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.35R) |
| RANGE_FADE | 1464 | 4/1460/0 | 36% | -0.37 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/MAJOR (-1.53R) |
| SHADOW_CASCADE_REVERSAL | 1360 | 0/0/1360 | 54% | -0.04 | OFF_HOURS/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.32R) | OVERLAP/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.40R) |
| BREAKDOWN_SHORT | 567 | 61/506/0 | 33% | -0.33 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.10R) |
| LIQUIDATION_REVERSAL | 362 | 0/362/0 | 31% | -0.58 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.80R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 132 | 28/104/0 | 42% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 18 | 2/16/0 | 56% | +0.19 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` +2.43R (n=33, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/MARKUP/COMPRESSED/BTC_NEUTRAL` -1.64R (n=18, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL` -1.57R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 229 | 28% / -0.58R | 229 | 52% / -0.15R | +0.43 | **ATR** |
| LIQUIDATION_REVERSAL | 20 | 30% / -0.54R | 20 | 55% / -0.24R | +0.30 | **ATR** |
| TREND_PULLBACK_EMA | 775 | 40% / -0.30R | 775 | 53% / -0.06R | +0.24 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 1308 | 44% / -0.34R | 1308 | 56% / -0.13R | +0.21 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 155 | 34% / -0.24R | 155 | 45% / -0.07R | +0.16 | **ATR** |
| RANGE_FADE | 73 | 30% / -0.42R | 73 | 37% / -0.28R | +0.14 | **ATR** |
| MA_CROSS_TREND_SHIFT | 42 | 38% / -0.22R | 42 | 40% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 337 | 44% / -0.29R | 337 | 47% / -0.18R | +0.12 | **ATR** |
| MOVER_AVWAP_SCALP | 1903 | 43% / -0.18R | 1903 | 49% / -0.07R | +0.12 | **ATR** |
| FAILED_AUCTION_RECLAIM | 1117 | 40% / -0.24R | 1117 | 42% / -0.14R | +0.11 | **ATR** |
| MOVER_TREND_PULLBACK | 7622 | 49% / -0.12R | 7622 | 54% / -0.01R | +0.10 | **ATR** |
| WHALE_MOMENTUM | 436 | 44% / -0.33R | 436 | 46% / -0.23R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 50 | 44% / -0.17R | 50 | 48% / -0.07R | +0.09 | **ATR** |
| DIVERGENCE_CONTINUATION | 1192 | 48% / -0.09R | 1192 | 54% / -0.04R | +0.05 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1067 | 48% / -0.14R | 1067 | 48% / -0.14R | -0.00 | **FIXED** |
| MEAN_REVERT | 296 | 47% / -0.16R | 296 | 46% / -0.16R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 8 | 50% / -0.24R | 8 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 10516 | 28% | -0.24R | 311 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1903 | 47% | -0.07R | 219 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 97 | 46% | -0.08R | 60 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| TREND_PULLBACK_EMA | 17 | 6% / -1.07R | 1046 | 35% / -0.20R | +0.86 | **SAR** |
| LIQUIDITY_SWEEP_REVERSAL | 58 | 7% / -1.01R | 1425 | 40% / -0.15R | +0.86 | **SAR** |
| MOVER_AVWAP_SCALP | 33 | 9% / -0.84R | 2365 | 35% / -0.16R | +0.68 | **SAR** |
| MOVER_TREND_PULLBACK | 223 | 24% / -0.53R | 9534 | 37% / -0.12R | +0.41 | **SAR** |
| DIVERGENCE_CONTINUATION | 15 | 40% / -0.28R | 1361 | 37% / -0.08R | +0.20 | **SAR** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 160 | 34% / -0.36R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 7 | 43% / +0.08R | 1046 | 33% / -0.18R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 12 | 25% / -0.40R | 930 | 33% / -0.21R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 4 | 0% / -1.13R | 228 | 31% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 11 | 9% / -0.95R | 298 | 32% / -0.49R | — | **MEASURING** |
| MEAN_REVERT | 10 | 20% / -0.57R | 245 | 49% / -0.03R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 86 | 42% / -0.16R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 56 | 36% / -0.10R | — | **MEASURING** |
| SR_FLIP_RETEST | 5 | 0% / -1.25R | 318 | 35% / -0.31R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -1.29R | 63 | 27% / -0.39R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 26 | 42% / -0.15R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 16 | 44% / +0.50R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 61 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×856]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 325/6) (sustained 325 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 325/6) (sustained 325 cycles)
- **ALERT** `tuned_variants` — 79 non-stamps — atr_arm_uncomputable=79 (seen=2627 stamped=343 skipped=2205) (streak 193/6) (sustained 193 cycles)
- **ALERT** `auto_dispatch` — 36 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=37) (streak 256/3) (sustained 256 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 42 fed / 0 quiet / 0 never delivered of 42 subscribed; 64644139 accepted, 0 rejected | 0 |
| ai_governor_blind | ok | blind 0% of last 50 | 0 |
| ai_governor_live_arms | ok | 15 arms current, none stalled; covering 1782/1782 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 29 arms current, none stalled; covering 1054/1054 signals (100%) | 0 |
| auto_dispatch | violating | 36 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (faults: venue:coindcx=37) (streak 256/3) | 256 |
| binance_ip_weight | ok | peak 253/2400 over the last 5 minutes | 0 |
| btc_reference | ok | BTC ref 82807.80 | 0 |
| candle_coverage | ok | 94/94 symbols with ≥20 15m candles, 94/94 updated within 45m [fresh=94; 77 Tier-1 futures + 17 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 1347 dup bars, 0 undedupable; ws 0 out-of-order, 308 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | 57 cohorts, 35 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE', 'RECOVERY'] | 0 |
| coindcx_positions | ok | no unprotected or unseen CoinDCX positions | 0 |
| context_emission_policy | violating | upstream +22 but output +0 (streak 1/72) | 1 |
| dark_atr_trail_arms | ok | no open arms; covering 1228/1246 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, 1 promoted today, nothing refused | 0 |
| dark_resolution | ok | 109 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1232/1250 signals (99%) | 0 |
| depth_feed | ok | 42/42 books fresh (stale 0, never 0, thin 0); 21918885 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.60R (bound 0.3) (streak 325/6) | 325 |
| emission_controller | ok | last cycle 1s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×856]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 325/6) | 325 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=68, profile_reject=2. Held back in this window: session_quality=126, profile_reject=4. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 4/6) | 4 |
| firestore_read_budget | ok | 1,317 reads/day of 50,000 [engine 1,284, signing 33]; top site runtime_tunables.doc at 287/day (engine) | 0 |
| footprint_bars | ok | 5040 sealed bars over 42 symbols; 1364 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +101 but output +0 (streak 2/6) | 2 |
| indicator_cache_key | ok | 143023 frozen value(s) avoided; 480396 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.33R over n=4177 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +22 / upstream +101 | 0 |
| mover_admission_metadata | ok | 931 symbols known, 225 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 17 held, 17 with scan counts, 17 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| pending_close | ok | 0 close(s) pending retry; outcomes since boot: {'closed': 0, 'already_flat': 0, 'failed': 0} | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3083 rows held, 3022007 evicted (sampled: execution:trigger_not_confirmed 400/1068359, execution:overextended 400/947320, setup_compat:regime_STRONG_TREND 400/513261) | 0 |
| price_action_lane | ok | 486099 evaluated, 950 emitted; layer1 950 stamped / 0 blind; cooldown=62775, delta_opposed=44901, no_footprint=188439, no_opposing_target=12, no_sweep=148746, rr_below_floor=40276 | 0 |
| promoted_pair_integrity | ok | 17/17 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=1460 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +13 / upstream +101 | 0 |
| sar_alignment_crosscheck | ok | 284/7392 disagreed (3.8%) | 0 |
| sar_exit_shadow | violating | upstream +101 but output +0 (streak 2/6) | 2 |
| sar_hold_arm | ok | 1894 held arms settled, 106 unscored, 29 still walking (26 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 27/27 resolvable | 0 |
| sar_live_arms | ok | 29 arms current, none stalled; covering 1054/1054 signals (100%) | 0 |
| sar_refresh_budget | ok | 12 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 1 resolved, 26 still mid-window | 0 |
| scan_cycle | ok | last 11.07s, worst 284.0s over 5705 lifetime cycles; lifetime 376 over 60s, 102 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 1.28s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 227212 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 28s ago (58.9s to run, worst 219.53s), 1392 overrun(s) of 6517 cycles, TTL 900s; slowest dark_promotion=7.42s, user_positions=7.1s, router_delivery=3.96s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=5, gate reads=0, withheld=5) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +41 / upstream +101 | 0 |
| structural_snap | ok | 5999/5999 measured, 25 blind, 0 levels moved (refusals: redetect_cooldown=110) | 0 |
| structural_veto_lane | ok | 365 stamped; 0 with no readable level book, 2 with clear air ahead, 271 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +101 / upstream +22 | 0 |
| tuned_variants | violating | 79 non-stamps — atr_arm_uncomputable=79 (seen=2627 stamped=343 skipped=2205) (streak 193/6) | 193 |
| unlock_shorts | ok | 15 open, 44 scheduled, calendar 5.3h old | 0 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 26 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1355278`
- `Path funnel` emissions: `32`
- `Regime distribution` emissions: `32`
- `QUIET_SCALP_BLOCK` events: `66`
- `confidence_gate` events: `2403`
- `free_channel_post` events: `0`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **38**
- Total REST-fallback activations: **10**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 13 | 6683 | 14821 | 14932 | 0 |
| futures_aggtrade | 7 | 9823 | 12934 | 13452 | 0 |
| futures_depth | 8 | 4547 | 17738 | 20196 | 0 |
| futures_liq | 2 | 2318 | 2318 | 4175 | 0 |
| futures_mover | 8 | 5284 | 7596 | 7785 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 10 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=236635] state[populated=236635] buckets[many=236635] sources[none] quality[none]
- funding_rate: presence[absent=36334, present=200301] state[empty=36334, populated=200301] buckets[few=200301, none=36334] sources[none] quality[none]
- liquidation_clusters: presence[absent=130396, present=106239] state[empty=130396, populated=106239] buckets[few=86544, none=130396, some=19695] sources[none] quality[none]
- oi_snapshot: presence[absent=36334, present=200301] state[empty=36334, populated=200301] buckets[few=510, many=197271, none=36334, some=2520] sources[none] quality[none]
- order_book: presence[absent=89683, present=146952] state[populated=146952, unavailable=89683] buckets[few=146952, none=89683] sources[book_ticker=146952, unavailable=89683] quality[none=89683, top_of_book_only=146952]
- orderblocks: presence[absent=236635] state[empty=236635] buckets[none=236635] sources[measured_dark=236635] quality[none]
- recent_ticks: presence[present=236635] state[populated=236635] buckets[many=236635] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.1721649169921875` sec
- Median create→first breach: `8193.756051778793` sec
- Median create→terminal: `8194.142790794373` sec
- Median first breach→terminal: `6.699562072753906e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 1.0805020193241701 | 1.2521415813071823 | 0.862923199304804 | 0 | 1 |
| MOVER_AVWAP_SCALP | 1 | 1 | 4.0440625014550555 | 3.0 | 1.348020833818352 | 1 | 0 |
| MOVER_TREND_PULLBACK | 19 | 19 | 2.82664999808072 | 2.5599279479007895 | 1.398054511807545 | 12 | 7 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 1.151538110053839 | 1.2830356076504397 | 0.8907061012633397 | 0 | 7 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.496414379861314 | 2.0231790356970927 | 0.7396351748700875 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.6208 | 8907.580099105835 | 8908.024976968765 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 529.9767050743103 | 529.9767580032349 |
| MOVER_TREND_PULLBACK | 19 | 19 | 42.1 | 36.8 | 42.1 | 0.0 | 0.356 | 5901.659461021423 | 5901.659511089325 |
| QUIET_COMPRESSION_BREAK | 7 | 7 | 42.9 | 28.6 | 42.9 | 0.0 | 0.1676 | 26256.291178941727 | 26258.642643928528 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 2905.1553111076355 | 2905.1554119586945 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 319 | 1 | 281 | 0.0 | 0.0 | None | None | 38 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1903 | 9 | 1847 | 0.0 | 0.0 | 2905.1553111076355 | 2905.1554119586945 | 56 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `27`
- Gating Δ: `42`
- No-generation Δ: `-180355`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.2214, "current_avg_pnl": 0.356, "current_win_rate": 42.1, "previous_avg_pnl": -0.8654, "previous_win_rate": 16.7, "win_rate_delta": 25.4}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.382, "current_avg_pnl": 0.1676, "current_win_rate": 42.9, "previous_avg_pnl": -0.2144, "previous_win_rate": 25.0, "win_rate_delta": 17.9}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -63, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 4, "geometry_changed_delta": 0, "geometry_preserved_delta": 25, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2905.16, "median_terminal_delta_sec": 2905.16, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
