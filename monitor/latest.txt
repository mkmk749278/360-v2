# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, MOVER_AVWAP_SCALP
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1761` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 46 | 46 | 46 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6832 | 6832 | 6765 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 55055 | 55070 | 12 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 48939 | 48939 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 48551 | 47226 | 1692 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 48980 | 48325 | 718 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 50090 | 50033 | 69 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 42253 | 42270 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 49046 | 49082 | 6 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 49093 | 46761 | 3168 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 59144 | 62768 | 954 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 55090 | 49177 | 9899 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 49705 | 49705 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 48945 | 48971 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 48517 | 48364 | 183 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::RANGE_FADE | 49940 | 48893 | 1448 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 48119 | 48384 | 104 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 40615 | 38470 | 2375 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 40851 | 40611 | 320 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 54989 | 55020 | 30 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 42273 | 42291 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2687 | 2687 | 2593 | 6 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 254 | 254 | 227 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 11 | 11 | 6 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 11510 | 11510 | 11432 | 11 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 17 | 17 | 16 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 8672 | 8672 | 8203 | 1 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 2272 | 2272 | 2114 | 20 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 28987 | 28987 | 27298 | 111 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1061 | 1061 | 1036 | 5 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 4268 | 4268 | 4236 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 315 | 315 | 271 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1728 | 1728 | 1675 | 8 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 90 | 90 | 89 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=55070): breakout_not_found=35571, basic_filters_failed=13820, move_not_fresh=3621, breakout_stale=1153, retest_proximity_failed=820, volume_spike_missing=79, move_exhausted=6
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=48939): cls_disabled_merged_into_lsr=48939
- **EVAL::DIVERGENCE_CONTINUATION** (total=47226): cvd_divergence_failed=22703, basic_filters_failed=10307, h1_trend_not_aligned=9696, ema_alignment_reject=3496, retest_proximity_failed=752, missing_fvg_or_orderblock=267, cvd_insufficient=5
- **EVAL::FAILED_AUCTION_RECLAIM** (total=48325): auction_not_detected=32038, basic_filters_failed=9863, reclaim_hold_failed=2598, tail_too_small=1948, regime_blocked=1866, rsi_reject=12
- **EVAL::FUNDING_EXTREME** (total=50033): funding_not_extreme=37849, basic_filters_failed=10912, ema_alignment_reject=560, rsi_reject=358, missing_funding_rate=246, momentum_reject=44, cvd_divergence_failed=40, missing_fvg_or_orderblock=24
- **EVAL::LIQUIDATION_REVERSAL** (total=42270): cascade_threshold_not_met=30901, basic_filters_failed=10743, cvd_divergence_failed=304, rsi_reject=297, missing_fvg_or_orderblock=21, volume_spike_missing=4
- **EVAL::MA_CROSS_TREND_SHIFT** (total=49082): no_ma_cross=37959, basic_filters_failed=10328, ma_cross_cooldown=707, ma_cross_htf_misaligned=88
- **EVAL::MEAN_REVERT** (total=46761): no_extension=40287, basic_filters_failed=6474
- **EVAL::MOVER_AVWAP_SCALP** (total=62768): no_avwap_tag=25599, no_mover_leg=14438, basic_filters_failed=14039, avwap_slope_against=5017, avwap_reclaim_no_volume=2035, no_avwap_reclaim=1580, anchor_too_recent=60
- **EVAL::MOVER_TREND_PULLBACK** (total=49177): mover_run_too_small=19733, basic_filters_failed=13950, no_reclaim=13480, no_pullback_tag=2014
- **EVAL::OPENING_RANGE_BREAKOUT** (total=49705): feature_disabled=49705
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=48971): regime_blocked=27243, breakout_not_found=14933, basic_filters_failed=4601, adx_reject=2127, ema_alignment_reject=67
- **EVAL::QUIET_COMPRESSION_BREAK** (total=48364): regime_blocked=23434, compression_not_detected=16233, basic_filters_failed=5246, breakout_not_detected=3077, volume_confirmation_failed=339, rsi_reject=30, missing_fvg_or_orderblock=5
- **EVAL::RANGE_FADE** (total=48893): no_range_edge=42417, basic_filters_failed=6476
- **EVAL::SR_FLIP_RETEST** (total=48384): flip_close_not_confirmed=32148, basic_filters_failed=9834, regime_blocked=1850, long_break_volume_thin=1358, retest_out_of_zone=1356, h1_break_not_confirmed=1119, reclaim_hold_failed=461, long_acceptance_not_held=91, whipsaw_flip=70, wick_quality_failed=37, ema_alignment_reject=36, missing_fvg_or_orderblock=24
- **EVAL::STANDARD** (total=38470): momentum_reject=12407, adx_reject=8372, sweeps_not_detected=5075, basic_filters_failed=4984, ema_alignment_reject=3506, macd_reject=3439, htf_poi_unanchored=582, rsi_reject=76, invalid_sl_geometry=26, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=40611): h1_trend_not_aligned=11024, ema_alignment_reject=7021, basic_filters_failed=6061, h1_pullback_not_confirmed=5493, ema_not_tested_prev=3934, no_ema_reclaim_close=3037, body_conviction_fail=1606, rsi_reject=1420, prev_already_above_emas=424, no_prev_high_break=312, prev_already_below_emas=83, momentum_flat=70, no_prev_low_break=45, ema21_not_tagged=38, missing_fvg_or_orderblock=35, momentum_reject=8
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=55020): breakout_not_found=28397, basic_filters_failed=13819, move_not_fresh=8667, breakout_stale=2824, retest_proximity_failed=1066, volume_spike_missing=170, move_exhausted=57, missing_fvg_or_orderblock=20
- **EVAL::WHALE_MOMENTUM** (total=42291): momentum_reject=32882, recent_ticks_insufficient=6462, basic_filters_failed=2947

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=2): execution:overextended=2
- **DIVERGENCE_CONTINUATION** (total=151): setup_compat:regime_VOLATILE_UNSUITABLE=145, execution:overextended=5, setup_compat:regime_BREAKOUT_EXPANSION=1
- **FAILED_AUCTION_RECLAIM** (total=1028): execution:overextended=592, setup_compat:regime_STRONG_TREND=414, setup_compat:regime_VOLATILE_UNSUITABLE=21, context_floor=1
- **FUNDING_EXTREME_SIGNAL** (total=166): execution:trigger_not_confirmed=166
- **LIQUIDATION_REVERSAL** (total=11): execution:trigger_not_confirmed=11
- **LIQUIDITY_SWEEP_REVERSAL** (total=2966): execution:trigger_not_confirmed=1037, setup_compat:regime_STRONG_TREND=1013, execution:overextended=916
- **MA_CROSS_TREND_SHIFT** (total=8): setup_compat:regime_DIRTY_RANGE=4, setup_compat:regime_CLEAN_RANGE=2, setup_compat:regime_VOLATILE_UNSUITABLE=1, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=5819): setup_compat:regime_STRONG_TREND=3029, setup_compat:regime_WEAK_TREND=2076, execution:overextended=714
- **MOVER_AVWAP_SCALP** (total=1384): execution:overextended=1246, execution:trigger_not_confirmed=114, entry_quality=24
- **MOVER_TREND_PULLBACK** (total=12233): execution:trigger_not_confirmed=6808, execution:overextended=5206, entry_quality=219
- **QUIET_COMPRESSION_BREAK** (total=10): execution:trigger_not_confirmed=10
- **RANGE_FADE** (total=2989): setup_compat:regime_WEAK_TREND=1287, setup_compat:regime_STRONG_TREND=1232, setup_compat:regime_VOLATILE_UNSUITABLE=261, execution:overextended=175, setup_compat:regime_BREAKOUT_EXPANSION=34
- **TREND_PULLBACK_EMA** (total=1429): setup_compat:regime_CLEAN_RANGE=892, setup_compat:regime_DIRTY_RANGE=420, setup_compat:regime_VOLATILE_UNSUITABLE=80, entry_quality=37
- **VOLUME_SURGE_BREAKOUT** (total=17): execution:overextended=17

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 95021 | 30.7% |
| TRENDING_UP | 78565 | 25.4% |
| QUIET | 69799 | 22.5% |
| TRENDING_DOWN | 49605 | 16.0% |
| VOLATILE | 16730 | 5.4% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **27**
- Average confidence gap to threshold: **10.15** (samples=27) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=11, XLMUSDT=7, BUSDT=4, 1000PEPEUSDT=3, XRPUSDT=1, BNBUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 5 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 4 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 2 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 6 |
| LIQUIDATION_REVERSAL | filtered | execution_component_floor | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 19 |
| MEAN_REVERT | kept | min_confidence_pass | 1 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 36 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 62 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 276 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 2 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 407 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 20 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 5 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 2 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 9 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 55.06 | 60.40 | 5.34 | 20.04 | 20.00 | 16.96 | -0.40 | 14.90 |
| DIVERGENCE_CONTINUATION | kept | 4 | 70.55 | 65.00 | -5.55 | 21.45 | 19.52 | 16.97 | 1.25 | -1.50 |
| FAILED_AUCTION_RECLAIM | filtered | 2 | 60.30 | 61.00 | 0.70 | 20.80 | 19.30 | 20.00 | 2.50 | 11.00 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 67.08 | 65.00 | -2.08 | 21.95 | 19.47 | 20.00 | 3.42 | 4.47 |
| LIQUIDATION_REVERSAL | filtered | 5 | 72.70 | 10.00 | -62.70 | 22.20 | 8.00 | 17.28 | 4.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 50.30 | 61.00 | 10.70 | 21.20 | 20.00 | 16.30 | 2.00 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 19 | 68.47 | 65.00 | -3.47 | 20.12 | 19.29 | 17.69 | 2.00 | 0.25 |
| MEAN_REVERT | kept | 1 | 69.70 | 65.00 | -4.70 | 21.20 | 14.00 | 17.40 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 36 | 59.16 | 64.44 | 5.28 | 22.03 | 19.91 | 15.80 | 5.82 | 19.54 |
| MOVER_AVWAP_SCALP | kept | 62 | 76.89 | 65.00 | -11.89 | 19.57 | 16.44 | 15.80 | 4.33 | 1.98 |
| MOVER_TREND_PULLBACK | filtered | 278 | 58.49 | 64.51 | 6.02 | 19.53 | 18.38 | 15.80 | 5.08 | 17.07 |
| MOVER_TREND_PULLBACK | kept | 407 | 76.93 | 65.00 | -11.93 | 20.02 | 18.25 | 15.80 | 4.26 | 2.30 |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 51.60 | 65.00 | 13.40 | 21.33 | 20.00 | 20.00 | 0.00 | 21.34 |
| QUIET_COMPRESSION_BREAK | kept | 5 | 74.58 | 65.00 | -9.58 | 22.02 | 20.00 | 20.00 | 0.00 | 1.56 |
| SR_FLIP_RETEST | filtered | 3 | 63.80 | 65.00 | 1.20 | 23.07 | 20.00 | 15.20 | 4.50 | 3.00 |
| SR_FLIP_RETEST | kept | 1 | 72.80 | 65.00 | -7.80 | 20.60 | 20.00 | 15.20 | 3.50 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 3 | 60.33 | 63.67 | 3.34 | 20.33 | 19.57 | 18.37 | 4.83 | 0.00 |
| TREND_PULLBACK_EMA | kept | 9 | 76.34 | 65.00 | -11.34 | 20.29 | 19.92 | 19.08 | 5.33 | 5.62 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 76.00 | 65.00 | -11.00 | 21.10 | 15.00 | 20.00 | 4.00 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 55.06 | 25.00 | 18.00 | 3.00 | 10.00 | 5.00 | 9.30 | -0.40 |
| DIVERGENCE_CONTINUATION | kept | 4 | 70.55 | 23.00 | 15.50 | 6.00 | 10.75 | 5.75 | 8.30 | 1.25 |
| FAILED_AUCTION_RECLAIM | filtered | 2 | 60.30 | 23.00 | 18.00 | 6.00 | 17.00 | 2.50 | 2.30 | 2.50 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 67.08 | 22.33 | 16.67 | 5.50 | 13.50 | 4.75 | 5.38 | 3.42 |
| LIQUIDATION_REVERSAL | filtered | 5 | 72.70 | 25.00 | 16.00 | 12.60 | 8.00 | 5.00 | 2.10 | 4.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 50.30 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 7.30 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 19 | 68.47 | 24.37 | 14.21 | 5.21 | 12.95 | 5.24 | 4.75 | 2.00 |
| MEAN_REVERT | kept | 1 | 69.70 | 25.00 | 18.00 | 3.00 | 13.00 | 5.00 | 5.70 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 36 | 59.16 | 17.00 | 18.00 | 8.88 | 14.00 | 8.01 | 7.41 | 5.82 |
| MOVER_AVWAP_SCALP | kept | 62 | 76.89 | 18.26 | 18.03 | 11.40 | 13.94 | 5.58 | 7.33 | 4.33 |
| MOVER_TREND_PULLBACK | filtered | 278 | 58.49 | 17.50 | 18.00 | 8.32 | 12.64 | 7.87 | 9.48 | 5.08 |
| MOVER_TREND_PULLBACK | kept | 407 | 76.93 | 18.96 | 18.02 | 8.10 | 13.86 | 6.83 | 9.54 | 4.26 |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 51.60 | 18.20 | 18.00 | 11.40 | 14.00 | 7.70 | 4.38 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 5 | 74.58 | 20.20 | 18.00 | 11.40 | 14.00 | 5.20 | 7.94 | 0.00 |
| SR_FLIP_RETEST | filtered | 3 | 63.80 | 25.00 | 8.00 | 3.00 | 14.00 | 8.00 | 4.30 | 4.50 |
| SR_FLIP_RETEST | kept | 1 | 72.80 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 4.30 | 3.50 |
| TREND_PULLBACK_EMA | filtered | 3 | 60.33 | 12.00 | 18.00 | 7.50 | 14.00 | 9.00 | 10.00 | 4.83 |
| TREND_PULLBACK_EMA | kept | 9 | 76.34 | 19.67 | 18.00 | 8.50 | 14.67 | 7.39 | 9.41 | 5.33 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 76.00 | 17.00 | 14.00 | 12.00 | 14.00 | 5.00 | 10.00 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 5 | 55.06 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| DIVERGENCE_CONTINUATION | kept | 4 | 70.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 2 | 60.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 6 | 67.08 | 0.00 | 0.00 | 3.47 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.47** |
| LIQUIDATION_REVERSAL | filtered | 5 | 72.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 50.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 19 | 68.47 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.25** |
| MEAN_REVERT | kept | 1 | 69.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 36 | 59.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | **0.10** |
| MOVER_AVWAP_SCALP | kept | 62 | 76.89 | 0.24 | 0.00 | 0.34 | 0.00 | 0.31 | 0.00 | 0.00 | 0.06 | **0.95** |
| MOVER_TREND_PULLBACK | filtered | 278 | 58.49 | 0.03 | 0.00 | 0.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.96** |
| MOVER_TREND_PULLBACK | kept | 407 | 76.93 | 0.07 | 0.00 | 1.09 | 0.00 | 0.07 | 0.03 | 0.00 | 0.00 | **1.26** |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 51.60 | 0.00 | 0.00 | 0.00 | 0.00 | 1.93 | 0.00 | 0.00 | 6.48 | **8.41** |
| QUIET_COMPRESSION_BREAK | kept | 5 | 74.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 2.16 | **2.16** |
| SR_FLIP_RETEST | filtered | 3 | 63.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 1 | 72.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 3 | 60.33 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 9 | 76.34 | 0.00 | 0.00 | 0.53 | 0.00 | 4.00 | 0.00 | 0.00 | 0.00 | **4.53** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 76.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **75774 held of 174944 seen** across 21 strategies; 1687 cells past the sample floor; **721 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 30675 | 312/30363/0 | 45% | -0.13 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.20R) |
| MOVER_AVWAP_SCALP | 9345 | 64/9281/0 | 41% | -0.25 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5952 | 39/5913/0 | 43% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 4175 | 24/4151/0 | 53% | +0.06 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.76R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 3983 | 0/0/3983 | 43% | -0.09 | ASIA/RANGE/NORMAL/BTC_RISING (+0.28R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.03R) |
| QUIET_COMPRESSION_BREAK | 3630 | 107/3523/0 | 47% | -0.11 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (+0.84R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| TREND_PULLBACK_EMA | 3611 | 10/3601/0 | 45% | -0.19 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| SHADOW_RANGE_FADE | 3366 | 0/0/3366 | 37% | -0.10 | ASIA/MARKUP/CASCADE/BTC_RISING (+0.23R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-0.94R) |
| SHADOW_FUNDING_FADE | 2811 | 0/0/2811 | 37% | -0.37 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.01R) |
| WHALE_MOMENTUM | 2064 | 2/2062/0 | 40% | -0.38 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1745 | 16/1729/0 | 36% | -0.31 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.66R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.62R) |
| MEAN_REVERT | 1048 | 16/1032/0 | 63% | +0.22 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 914 | 2/912/0 | 30% | -0.48 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| VOLUME_SURGE_BREAKOUT | 884 | 0/884/0 | 49% | -0.08 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SR_FLIP_RETEST | 456 | 0/456/0 | 59% | -0.13 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-0.91R) |
| SHADOW_CASCADE_REVERSAL | 433 | 0/0/433 | 53% | -0.03 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.23R) |
| RANGE_FADE | 256 | 0/256/0 | 52% | -0.11 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (+1.36R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| BREAKDOWN_SHORT | 192 | 16/176/0 | 22% | -0.56 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| LIQUIDATION_REVERSAL | 184 | 0/184/0 | 7% | -1.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 46 | 6/40/0 | 35% | -0.17 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +1.76R (n=34, STRONG); `LIQUIDITY_SWEEP_REVERSAL @ OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +1.66R (n=15, STRONG); `DIVERGENCE_CONTINUATION @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL` +1.62R (n=37, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.62R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.50R (n=20, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 95 | 34% / -0.43R | 95 | 51% / -0.12R | +0.31 | **ATR** |
| TREND_PULLBACK_EMA | 314 | 50% / -0.14R | 314 | 57% / -0.03R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 247 | 43% / -0.34R | 247 | 45% / -0.24R | +0.10 | **ATR** |
| RANGE_FADE | 19 | 47% / +0.11R | 19 | 47% / +0.01R | -0.10 | **FIXED** |
| MOVER_AVWAP_SCALP | 715 | 46% / -0.17R | 715 | 51% / -0.08R | +0.09 | **ATR** |
| FAILED_AUCTION_RECLAIM | 473 | 44% / -0.17R | 473 | 46% / -0.09R | +0.08 | **ATR** |
| MOVER_TREND_PULLBACK | 4694 | 51% / -0.08R | 4694 | 55% / -0.01R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 77 | 48% / -0.28R | 77 | 49% / -0.21R | +0.08 | **ATR** |
| MA_CROSS_TREND_SHIFT | 15 | 33% / -0.24R | 15 | 33% / -0.19R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 60 | 47% / -0.07R | 60 | 53% / -0.02R | +0.05 | **ATR** |
| BREAKDOWN_SHORT | 20 | 30% / -0.17R | 20 | 30% / -0.14R | +0.03 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 357 | 51% / -0.20R | 357 | 54% / -0.17R | +0.03 | **ATR** |
| QUIET_COMPRESSION_BREAK | 601 | 45% / -0.16R | 601 | 45% / -0.17R | -0.01 | **FIXED** |
| MEAN_REVERT | 98 | 57% / +0.05R | 98 | 55% / +0.06R | +0.01 | **ATR** |
| DIVERGENCE_CONTINUATION | 442 | 54% / -0.01R | 442 | 59% / -0.01R | -0.00 | **FIXED** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 11 | 27% / -0.51R | 11 | 45% / -0.35R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 7000 | 31% | -0.12R | 283 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 715 | 49% | -0.07R | 162 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 41 | 56% | -0.04R | 34 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 86 | 36% / -0.24R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 562 | 37% / -0.08R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5982 | 37% / -0.13R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 847 | 36% / -0.03R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 369 | 37% / -0.05R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 490 | 41% / +0.09R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 409 | 38% / -0.11R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 353 | 44% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 84 | 29% / -0.44R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 110 | 31% / -0.59R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 78 | 54% / +0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 38 | 42% / +0.01R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 17 | 41% / +0.18R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 78 | 31% / -0.37R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 21 | 14% / -0.68R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 15 | 33% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 8 | 38% / -0.01R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 55 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×319]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 19/6) (sustained 19 cycles)
- **ALERT** `mean_revert_emission` — 1460 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.21R over n=1032, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 19/6) (sustained 19 cycles)
- **ALERT** `tuned_variants` — 24 non-stamps — atr_arm_uncomputable=24 (seen=375 stamped=20 skipped=331) (streak 19/6) (sustained 19 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 19/3) (sustained 19 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 2887876 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 19/3) | 19 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | violating | 1 live ATR-trail arms could not be advanced this cycle (0 no candles, 1 bars behind; 44 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| auto_dispatch | ok | placed=6 rejected=0 skipped=6 over 6 fan-out(s) to a keyed roster; top reasons: mode=6 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 79881.00 | 0 |
| candle_coverage | ok | 86/86 symbols with ≥20 15m candles, 86/86 updated within 45m [fresh=86; 75 Tier-1 futures + 11 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 457 dup bars, 0 undedupable; ws 0 out-of-order, 101 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | violating | upstream +36 but output +0 (streak 1/72) | 1 |
| dark_atr_trail_arms | ok | no open arms; covering 1095/1112 signals (98%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 1 of 85 open dark rows are not being advanced (worst: TUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 19/120) | 19 |
| dark_sar_arms | ok | no open arms; covering 1091/1108 signals (98%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 615558 msgs, 0 rejected | 0 |
| edge_reconciliation | ok | max divergence FAILED_AUCTION_RECLAIM +0.23R (< 0.3) | 0 |
| emission_controller | ok | last cycle 2s ago; live_overrides=12 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×319]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 19/6) | 19 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | violating | upstream +299 but output +0 (streak 1/6) | 1 |
| indicator_cache_key | ok | 1087 frozen value(s) avoided; 9943 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 1460 detections since last emission (emitted_total=0) — and the POST-SCORING blocked candidates measure +0.21R over n=1032, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 19/6) | 19 |
| mean_revert_path | ok | output +41 / upstream +299 | 0 |
| mover_admission_metadata | ok | 895 symbols known, 191 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 11 held, 11 with scan counts, 11 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 5 locked / 5 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2959 rows held, 1073199 evicted (sampled: execution:trigger_not_confirmed 400/390476, execution:overextended 400/369705, setup_compat:regime_STRONG_TREND 400/149950) | 0 |
| price_action_lane | ok | 67233 evaluated, 62 emitted; layer1 62 stamped / 0 blind; cooldown=9911, delta_opposed=6532, no_footprint=27265, no_opposing_target=488, no_sweep=17389, rr_below_floor=5586 | 0 |
| promoted_pair_integrity | ok | 11/11 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.11R over n=256 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +5 / upstream +299 | 0 |
| sar_alignment_crosscheck | ok | 0/486 disagreed (0.0%) | 0 |
| sar_exit_shadow | violating | upstream +299 but output +0 (streak 1/6) | 1 |
| sar_hold_arm | ok | 1050 held arms settled, 172 unscored, 44 still walking (39 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 2/19 unfetchable (11%); top cause: located bar does not contain the stamp; symbols: ARBUSDT, NEARUSDT | 0 |
| sar_live_arms | violating | 1 live SAR arms could not be advanced this cycle (0 no candles, 1 bars behind; 43 current): . Their stops are frozen, so the mechanism is not being measured on those trades. (streak 4/12) | 4 |
| sar_refresh_budget | ok | 17 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 419 records await one (17 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 9.69s, worst 61.66s over 806 lifetime cycles; lifetime 1 over 60s, 0 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.22s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 21419 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 15s ago (5.64s to run, worst 49.64s), 6 overrun(s) of 521 cycles, TTL 900s; slowest positions_diag=3.57s, engine_state=1.6s, activity=0.33s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +1 / upstream +299 | 0 |
| structural_snap | ok | 4660/4660 measured, 10 blind, 0 levels moved (refusals: redetect_cooldown=77) | 0 |
| structural_veto_lane | ok | 100 stamped; 0 with no readable level book, 26 with clear air ahead, 12 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +299 / upstream +36 | 0 |
| tuned_variants | violating | 24 non-stamps — atr_arm_uncomputable=24 (seen=375 stamped=20 skipped=331) (streak 19/6) | 19 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1476664`
- `Path funnel` emissions: `36`
- `Regime distribution` emissions: `36`
- `QUIET_SCALP_BLOCK` events: `27`
- `confidence_gate` events: `868`
- `free_channel_post` events: `53`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **10**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 1 | 6884 | 6884 | 6884 | 0 |
| futures_aggtrade | 1 | 17743 | 17743 | 17743 | 0 |
| futures_depth | 8 | 9624 | 10443 | 11319 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **53**

| Source | Count |
|---|---:|
| signal_close | 48 |
| regime_shift | 4 |
| signal_highlight | 1 |

- By severity: HIGH=53

## Dependency readiness
- cvd: presence[present=249126] state[populated=249126] buckets[few=3, many=249110, some=13] sources[none] quality[none]
- funding_rate: presence[absent=23974, present=225152] state[empty=23974, populated=225152] buckets[few=225152, none=23974] sources[none] quality[none]
- liquidation_clusters: presence[absent=128260, present=120866] state[empty=128260, populated=120866] buckets[few=94713, none=128260, some=26153] sources[none] quality[none]
- oi_snapshot: presence[absent=23254, present=225872] state[empty=23254, populated=225872] buckets[few=211, many=224229, none=23254, some=1432] sources[none] quality[none]
- order_book: presence[absent=87614, present=161512] state[populated=161512, unavailable=87614] buckets[few=161512, none=87614] sources[book_ticker=161512, unavailable=87614] quality[none=87614, top_of_book_only=161512]
- orderblocks: presence[absent=249126] state[empty=249126] buckets[none=249126] sources[measured_dark=249126] quality[none]
- recent_ticks: presence[present=249126] state[populated=249126] buckets[many=249126] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `15.099544405937195` sec
- Median create→first breach: `5053.508672475815` sec
- Median create→terminal: `5057.121594071388` sec
- Median first breach→terminal: `5.018236517906189` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.1}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 4 | 4 | 1.2887027387530043 | 1.5128395347658783 | 0.8622391597911916 | 0 | 4 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 1.4805345250176851 | 1.6425404386722713 | 0.9052126687497655 | 0 | 1 |
| MEAN_REVERT | 1 | 1 | 1.9400005623190077 | 3.0 | 0.646666854106336 | 0 | 1 |
| MOVER_AVWAP_SCALP | 5 | 5 | 1.9607559513008872 | 2.880717264121169 | 0.8688553863421805 | 1 | 4 |
| MOVER_TREND_PULLBACK | 26 | 26 | 3.9540353213864643 | 3.0 | 1.4649430791453084 | 21 | 5 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 0.9446279907823398 | 1.1261043964558983 | 0.8879664138147676 | 0 | 7 |
| TREND_PULLBACK_EMA | 2 | 2 | 1.9116565697188987 | 2.442248350490463 | 0.7429168832101594 | 0 | 2 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 4 | 4 | 0.0 | 75.0 | 0.0 | 0.0 | -0.8473 | 8509.952380537987 | 8512.429481983185 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 33453.39265751839 | 33459.01263010502 |
| MEAN_REVERT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 3.1368 | 3579.950889110565 | 3585.718568086624 |
| MOVER_AVWAP_SCALP | 5 | 5 | 20.0 | 40.0 | 20.0 | 0.0 | 0.4586 | 8158.064147949219 | 8162.769848108292 |
| MOVER_TREND_PULLBACK | 26 | 26 | 7.7 | 42.3 | 7.7 | 0.0 | 0.6699 | 2457.6447930336 | 2464.130786061287 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 25.0 | 50.0 | 25.0 | 0.0 | -0.2338 | 36881.807512402534 | 36892.871913433075 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4299.99608194828 | 4302.377595424652 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 315 | 1 | 271 | 0.0 | 0.0 | None | None | 44 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1728 | 8 | 1675 | 0.0 | 0.0 | 4299.99608194828 | 4302.377595424652 | 53 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-227`
- Gating Δ: `-30410`
- No-generation Δ: `-1086112`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.8473, "current_avg_pnl": -0.8473, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.6428, "current_avg_pnl": 0.4586, "current_win_rate": 20.0, "previous_avg_pnl": -0.1842, "previous_win_rate": 0.0, "win_rate_delta": 20.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.3986, "current_avg_pnl": 0.6699, "current_win_rate": 7.7, "previous_avg_pnl": 0.2713, "previous_win_rate": 0.0, "win_rate_delta": 7.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.4232, "current_avg_pnl": -0.2338, "current_win_rate": 25.0, "previous_avg_pnl": -0.657, "previous_win_rate": 12.5, "win_rate_delta": 12.5}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": -160, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -8, "geometry_changed_delta": 0, "geometry_preserved_delta": -94, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 4300.0, "median_terminal_delta_sec": 4302.38, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
