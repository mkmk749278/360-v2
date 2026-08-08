# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::BREAKDOWN_SHORT
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `662` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4241 | 4241 | 3933 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 44877 | 44877 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 33956 | 33959 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 33897 | 33096 | 858 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 33964 | 33921 | 53 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 36703 | 36542 | 165 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 34003 | 34005 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 33975 | 33988 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MEAN_REVERT | 33990 | 33329 | 974 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 46600 | 47846 | 158 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 44878 | 39914 | 6676 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 36664 | 36665 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 33961 | 33965 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 33880 | 33739 | 157 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 34303 | 34111 | 300 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 33839 | 33871 | 3 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 31141 | 29760 | 1439 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 31201 | 31125 | 87 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 44867 | 44843 | 34 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 34006 | 34005 | 14 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 616 | 616 | 556 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 324 | 324 | 52 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8031 | 8031 | 8014 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 3104 | 3104 | 2405 | 7 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 336 | 336 | 35 | 6 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 19617 | 19617 | 13969 | 68 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1229 | 1229 | 769 | 3 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 1267 | 1267 | 970 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 38 | 38 | 38 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 886 | 886 | 824 | 9 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 91 | 91 | 22 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 3300 | 3300 | 102 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=44877): breakout_not_found=23147, basic_filters_failed=14279, move_not_fresh=3711, breakout_stale=1581, volume_spike_missing=1537, retest_proximity_failed=575, ema_alignment_reject=37, missing_fvg_or_orderblock=7, move_exhausted=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=33959): cls_disabled_merged_into_lsr=33959
- **EVAL::DIVERGENCE_CONTINUATION** (total=33096): cvd_divergence_failed=10294, basic_filters_failed=10146, h1_trend_not_aligned=8105, retest_proximity_failed=2227, ema_alignment_reject=2159, missing_fvg_or_orderblock=165
- **EVAL::FAILED_AUCTION_RECLAIM** (total=33921): auction_not_detected=21618, basic_filters_failed=9962, regime_blocked=1644, reclaim_hold_failed=409, tail_too_small=283, rsi_reject=5
- **EVAL::FUNDING_EXTREME** (total=36542): funding_not_extreme=20497, basic_filters_failed=8565, missing_funding_rate=5063, ema_alignment_reject=1189, rsi_reject=923, cvd_divergence_failed=178, momentum_reject=127
- **EVAL::LIQUIDATION_REVERSAL** (total=34005): cascade_threshold_not_met=23111, basic_filters_failed=10678, cvd_divergence_failed=121, rsi_reject=82, missing_fvg_or_orderblock=12, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=33988): no_ma_cross=23800, basic_filters_failed=10150, ma_cross_htf_misaligned=29, ma_cross_cooldown=9
- **EVAL::MEAN_REVERT** (total=33329): no_extension=27761, basic_filters_failed=5568
- **EVAL::MOVER_AVWAP_SCALP** (total=47846): no_mover_leg=15240, basic_filters_failed=14356, no_avwap_tag=14105, avwap_slope_against=2568, avwap_reclaim_no_volume=915, no_avwap_reclaim=662
- **EVAL::MOVER_TREND_PULLBACK** (total=39914): mover_run_too_small=17247, basic_filters_failed=14310, no_reclaim=7176, no_pullback_tag=1181
- **EVAL::OPENING_RANGE_BREAKOUT** (total=36665): feature_disabled=36665
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=33965): regime_blocked=25393, breakout_not_found=6084, basic_filters_failed=1956, adx_reject=519, ema_alignment_reject=13
- **EVAL::QUIET_COMPRESSION_BREAK** (total=33739): compression_not_detected=11010, regime_blocked=10208, basic_filters_failed=8003, breakout_not_detected=4003, volume_confirmation_failed=402, rsi_reject=73, volume_reject=33, missing_fvg_or_orderblock=7
- **EVAL::RANGE_FADE** (total=34111): no_range_edge=28541, basic_filters_failed=5570
- **EVAL::SR_FLIP_RETEST** (total=33871): flip_close_not_confirmed=20243, basic_filters_failed=9955, long_break_volume_thin=1664, regime_blocked=1639, retest_out_of_zone=236, h1_break_not_confirmed=95, reclaim_hold_failed=18, wick_quality_failed=14, long_acceptance_not_held=7
- **EVAL::STANDARD** (total=29760): momentum_reject=7785, adx_reject=5655, sweeps_not_detected=5476, basic_filters_failed=3894, macd_reject=2433, rsi_reject=1800, ema_alignment_reject=1684, htf_poi_unanchored=1023, invalid_sl_geometry=10
- **EVAL::TREND_PULLBACK** (total=31125): h1_trend_not_aligned=10164, h1_pullback_not_confirmed=7490, basic_filters_failed=4780, ema_alignment_reject=3075, no_ema_reclaim_close=2703, ema_not_tested_prev=1151, body_conviction_fail=834, rsi_reject=383, prev_already_below_emas=238, no_prev_low_break=128, prev_already_above_emas=95, momentum_flat=31, no_prev_high_break=27, ema21_not_tagged=11, momentum_reject=8, missing_fvg_or_orderblock=7
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=44843): breakout_not_found=21835, basic_filters_failed=14279, move_not_fresh=5019, volume_spike_missing=1697, breakout_stale=1225, retest_proximity_failed=760, ema_alignment_reject=21, missing_fvg_or_orderblock=7
- **EVAL::WHALE_MOMENTUM** (total=34005): momentum_reject=23264, recent_ticks_insufficient=7274, basic_filters_failed=3467

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **DIVERGENCE_CONTINUATION** (total=60): setup_compat:regime_VOLATILE_UNSUITABLE=52, setup_compat:regime_BREAKOUT_EXPANSION=8
- **FAILED_AUCTION_RECLAIM** (total=372): setup_compat:regime_STRONG_TREND=175, execution:overextended=167, context_floor=30
- **FUNDING_EXTREME_SIGNAL** (total=314): execution:trigger_not_confirmed=281, context_floor=33
- **LIQUIDITY_SWEEP_REVERSAL** (total=3206): execution:overextended=2389, setup_compat:regime_STRONG_TREND=492, execution:trigger_not_confirmed=325
- **MEAN_REVERT** (total=876): setup_compat:regime_STRONG_TREND=371, setup_compat:regime_WEAK_TREND=318, execution:overextended=169, entry_quality=18
- **MOVER_AVWAP_SCALP** (total=225): execution:overextended=162, entry_quality=54, execution:trigger_not_confirmed=9
- **MOVER_TREND_PULLBACK** (total=11812): execution:overextended=6205, execution:trigger_not_confirmed=4927, entry_quality=680
- **QUIET_COMPRESSION_BREAK** (total=230): context_floor=230
- **RANGE_FADE** (total=622): setup_compat:regime_VOLATILE_UNSUITABLE=280, setup_compat:regime_STRONG_TREND=210, context_edge=70, setup_compat:regime_WEAK_TREND=38, setup_compat:regime_BREAKOUT_EXPANSION=24
- **TREND_PULLBACK_EMA** (total=881): setup_compat:regime_CLEAN_RANGE=606, setup_compat:regime_DIRTY_RANGE=274, setup_compat:regime_VOLATILE_UNSUITABLE=1
- **VOLUME_SURGE_BREAKOUT** (total=66): execution:overextended=41, context_floor=25
- **WHALE_MOMENTUM** (total=3198): execution:trigger_not_confirmed=3198

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 113812 | 40.7% |
| QUIET | 85243 | 30.5% |
| TRENDING_UP | 34347 | 12.3% |
| TRENDING_DOWN | 31091 | 11.1% |
| VOLATILE | 15321 | 5.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **108**
- Average confidence gap to threshold: **11.73** (samples=108) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: 1000SHIBUSDT=16, ETHUSDT=14, DOTUSDT=11, ZECUSDT=10, 1000PEPEUSDT=9, ENAUSDT=7, XLMUSDT=7, LINKUSDT=7, BANKUSDT=5, NEARUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 45 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 99 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 16 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 26 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 9 |
| MEAN_REVERT | filtered | min_confidence | 10 |
| MEAN_REVERT | kept | min_confidence_pass | 11 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 147 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 123 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 1270 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1607 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 92 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 36 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 20 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 10 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 31 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 10 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 10 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 70.30 | 65.00 | -5.30 | 21.20 | 15.60 | 20.00 | 4.50 | 10.20 |
| DIVERGENCE_CONTINUATION | filtered | 45 | 50.78 | 64.56 | 13.78 | 20.33 | 19.83 | 16.66 | 1.36 | 21.67 |
| DIVERGENCE_CONTINUATION | kept | 99 | 69.65 | 65.00 | -4.65 | 19.58 | 19.88 | 18.76 | 0.31 | 0.00 |
| FAILED_AUCTION_RECLAIM | kept | 16 | 72.41 | 65.00 | -7.41 | 21.20 | 18.31 | 20.00 | 1.16 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 26 | 50.20 | 60.00 | 9.80 | 20.97 | 14.00 | 17.00 | 3.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 56.60 | 65.00 | 8.40 | 21.20 | 20.00 | 17.00 | 0.00 | 14.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.41 | 65.00 | -2.41 | 18.71 | 17.81 | 17.00 | 2.33 | 0.00 |
| MEAN_REVERT | filtered | 10 | 49.07 | 60.50 | 11.43 | 20.93 | 14.57 | 14.70 | 0.00 | 26.00 |
| MEAN_REVERT | kept | 11 | 71.27 | 65.00 | -6.27 | 20.65 | 16.31 | 18.75 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 147 | 59.84 | 65.00 | 5.16 | 19.79 | 15.74 | 15.80 | 3.96 | 6.92 |
| MOVER_AVWAP_SCALP | kept | 123 | 82.36 | 65.00 | -17.36 | 19.08 | 15.94 | 15.80 | 5.10 | -0.12 |
| MOVER_TREND_PULLBACK | filtered | 1275 | 55.35 | 63.64 | 8.29 | 19.82 | 18.36 | 15.80 | 4.47 | 18.02 |
| MOVER_TREND_PULLBACK | kept | 1607 | 76.36 | 65.00 | -11.36 | 20.24 | 18.40 | 15.80 | 4.54 | 1.15 |
| QUIET_COMPRESSION_BREAK | filtered | 128 | 50.47 | 63.59 | 13.12 | 21.72 | 19.53 | 20.00 | 0.00 | 9.89 |
| QUIET_COMPRESSION_BREAK | kept | 3 | 77.90 | 65.00 | -12.90 | 20.93 | 20.00 | 20.00 | 0.00 | -2.00 |
| TREND_PULLBACK_EMA | filtered | 20 | 58.23 | 65.00 | 6.77 | 19.88 | 20.00 | 18.59 | 4.50 | 17.15 |
| TREND_PULLBACK_EMA | kept | 10 | 73.51 | 65.00 | -8.51 | 20.86 | 19.60 | 18.13 | 4.60 | 5.30 |
| VOLUME_SURGE_BREAKOUT | filtered | 31 | 59.80 | 65.00 | 5.20 | 19.35 | 15.40 | 20.00 | 3.50 | 12.00 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 76.28 | 65.00 | -11.28 | 22.14 | 17.51 | 20.00 | 5.85 | 10.30 |
| WHALE_MOMENTUM | filtered | 10 | 52.21 | 65.00 | 12.79 | 21.38 | 14.00 | 17.00 | 0.00 | 18.64 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 70.30 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 7.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 45 | 50.78 | 23.93 | 15.51 | 3.27 | 12.93 | 6.56 | 8.89 | 1.36 |
| DIVERGENCE_CONTINUATION | kept | 99 | 69.65 | 22.82 | 15.68 | 3.06 | 13.06 | 5.64 | 9.09 | 0.31 |
| FAILED_AUCTION_RECLAIM | kept | 16 | 72.41 | 17.50 | 18.00 | 4.12 | 16.25 | 7.41 | 7.97 | 1.16 |
| FUNDING_EXTREME_SIGNAL | filtered | 26 | 50.20 | 25.00 | 8.00 | 9.00 | 9.00 | 8.50 | 2.70 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 56.60 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.41 | 19.67 | 14.44 | 5.67 | 12.78 | 5.00 | 7.52 | 2.33 |
| MEAN_REVERT | filtered | 10 | 49.07 | 20.80 | 18.00 | 8.70 | 12.00 | 9.50 | 6.07 | 0.00 |
| MEAN_REVERT | kept | 11 | 71.27 | 22.82 | 17.27 | 7.91 | 12.00 | 6.18 | 5.09 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 147 | 59.84 | 17.00 | 18.00 | 8.34 | 12.10 | 5.94 | 3.05 | 3.96 |
| MOVER_AVWAP_SCALP | kept | 123 | 82.36 | 21.62 | 18.16 | 9.54 | 14.72 | 5.32 | 7.98 | 5.10 |
| MOVER_TREND_PULLBACK | filtered | 1275 | 55.35 | 19.01 | 18.00 | 8.05 | 13.49 | 6.38 | 8.62 | 4.47 |
| MOVER_TREND_PULLBACK | kept | 1607 | 76.36 | 19.14 | 18.02 | 8.09 | 13.61 | 5.86 | 8.93 | 4.54 |
| QUIET_COMPRESSION_BREAK | filtered | 128 | 50.47 | 19.56 | 16.88 | 11.44 | 14.16 | 6.39 | 3.99 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 3 | 77.90 | 17.00 | 18.00 | 12.00 | 15.00 | 7.33 | 8.57 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 20 | 58.23 | 17.00 | 18.00 | 7.50 | 14.00 | 8.45 | 9.68 | 4.50 |
| TREND_PULLBACK_EMA | kept | 10 | 73.51 | 21.00 | 18.00 | 7.50 | 14.00 | 7.10 | 8.41 | 4.60 |
| VOLUME_SURGE_BREAKOUT | filtered | 31 | 59.80 | 17.00 | 18.00 | 15.00 | 11.00 | 5.00 | 2.30 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 76.28 | 25.00 | 16.80 | 12.00 | 14.00 | 5.00 | 7.93 | 5.85 |
| WHALE_MOMENTUM | filtered | 10 | 52.21 | 21.80 | 8.00 | 12.60 | 16.70 | 7.85 | 3.90 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 70.30 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| DIVERGENCE_CONTINUATION | filtered | 45 | 50.78 | 0.00 | 0.00 | 1.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.07** |
| DIVERGENCE_CONTINUATION | kept | 99 | 69.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 16 | 72.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 26 | 50.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 56.60 | 0.00 | 0.00 | 14.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **14.40** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 9 | 67.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 10 | 49.07 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| MEAN_REVERT | kept | 11 | 71.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 147 | 59.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 6.92 | **6.92** |
| MOVER_AVWAP_SCALP | kept | 123 | 82.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | **0.08** |
| MOVER_TREND_PULLBACK | filtered | 1275 | 55.35 | 0.00 | 0.00 | 4.00 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **4.28** |
| MOVER_TREND_PULLBACK | kept | 1607 | 76.36 | 0.00 | 0.00 | 0.36 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.54** |
| QUIET_COMPRESSION_BREAK | filtered | 128 | 50.47 | 0.00 | 0.00 | 0.45 | 0.00 | 0.64 | 0.00 | 0.00 | 5.82 | **6.91** |
| QUIET_COMPRESSION_BREAK | kept | 3 | 77.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 20 | 58.23 | 0.00 | 0.00 | 4.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.40** |
| TREND_PULLBACK_EMA | kept | 10 | 73.51 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.80** |
| VOLUME_SURGE_BREAKOUT | filtered | 31 | 59.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | **9.00** |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 76.28 | 0.00 | 0.00 | 10.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **10.00** |
| WHALE_MOMENTUM | filtered | 10 | 52.21 | 0.00 | 0.00 | 0.00 | 0.00 | 8.64 | 0.00 | 0.00 | 0.00 | **8.64** |

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
- Outcomes recorded: **126332 held of 185715 seen** across 21 strategies; 2842 cells past the sample floor; **760 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 29799 | 203/29596/0 | 52% | -0.01 | ASIA/MARKUP/CASCADE/BTC_RISING/MIDCAP (+1.24R) | ASIA/MARKDOWN/CASCADE/BTC_RISING (-1.20R) |
| FAILED_AUCTION_RECLAIM | 16983 | 24/16959/0 | 51% | -0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16544 | 1/16543/0 | 47% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 11342 | 4/11338/0 | 45% | -0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+1.37R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| QUIET_COMPRESSION_BREAK | 9089 | 0/9089/0 | 49% | -0.04 | NY/QUIET/EXPANDED/BTC_RISING/ALTCOIN (+1.37R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 7309 | 28/7281/0 | 31% | -0.40 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| SHADOW_MEAN_REVERT | 4552 | 0/0/4552 | 42% | -0.08 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-0.99R) |
| LIQUIDITY_SWEEP_REVERSAL | 4512 | 11/4501/0 | 46% | -0.20 | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+1.58R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| TREND_PULLBACK_EMA | 4390 | 2/4388/0 | 51% | -0.20 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-1.19R) |
| SHADOW_RANGE_FADE | 4185 | 0/0/4185 | 39% | +0.10 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+1.35R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.02R) |
| MEAN_REVERT | 3929 | 0/3929/0 | 74% | +0.47 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.44R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.35R) |
| SHADOW_FUNDING_FADE | 3846 | 0/0/3846 | 38% | -0.33 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (-0.96R) |
| RANGE_FADE | 3331 | 0/3331/0 | 28% | -0.48 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.87R) | NY/MARKUP/NORMAL/BTC_RISING (-1.31R) |
| VOLUME_SURGE_BREAKOUT | 2220 | 13/2207/0 | 42% | +0.02 | LONDON/MARKUP/COMPRESSED/BTC_NEUTRAL (+1.87R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 1985 | 4/1981/0 | 31% | -0.45 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (-1.61R) |
| WHALE_MOMENTUM | 1372 | 0/1372/0 | 44% | -0.25 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-0.76R) |
| SHADOW_CASCADE_REVERSAL | 432 | 0/0/432 | 47% | -0.18 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.02R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.81R) |
| BREAKDOWN_SHORT | 357 | 7/350/0 | 54% | +0.17 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 70 | 0/70/0 | 60% | -0.51 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) |
| POST_DISPLACEMENT_CONTINUATION | 67 | 0/67/0 | 90% | +0.75 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 18 | 1/17/0 | 28% | -0.46 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.87R (n=27, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.87R (n=27, STRONG); `RANGE_FADE @ ASIA/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` +1.87R (n=50, STRONG)
- **Weakest cells**: `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP` -1.61R (n=20, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 85 | 36% / -0.38R | 85 | 55% / -0.11R | +0.27 | **ATR** |
| TREND_PULLBACK_EMA | 138 | 43% / -0.28R | 138 | 48% / -0.11R | +0.17 | **ATR** |
| MOVER_AVWAP_SCALP | 419 | 38% / -0.24R | 419 | 42% / -0.13R | +0.11 | **ATR** |
| SR_FLIP_RETEST | 2762 | 46% / -0.20R | 2762 | 49% / -0.10R | +0.10 | **ATR** |
| DIVERGENCE_CONTINUATION | 796 | 47% / -0.12R | 796 | 52% / -0.06R | +0.06 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 658 | 50% / -0.18R | 658 | 54% / -0.12R | +0.06 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 70 | 41% / +0.01R | 70 | 49% / -0.05R | -0.05 | **FIXED** |
| MEAN_REVERT | 377 | 54% / +0.00R | 377 | 50% / +0.05R | +0.04 | **ATR** |
| MOVER_TREND_PULLBACK | 3543 | 52% / -0.05R | 3543 | 54% / -0.01R | +0.04 | **ATR** |
| RANGE_FADE | 213 | 16% / -0.72R | 213 | 18% / -0.68R | +0.04 | **ATR** |
| WHALE_MOMENTUM | 94 | 48% / -0.25R | 94 | 47% / -0.27R | -0.02 | **FIXED** |
| BREAKDOWN_SHORT | 17 | 29% / -0.24R | 17 | 29% / -0.23R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 1350 | 45% / -0.14R | 1350 | 44% / -0.15R | -0.01 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 2250 | 47% / -0.10R | 2250 | 47% / -0.10R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 9 | 33% / -0.27R | 9 | 33% / -0.27R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 7 | 71% / +0.23R | 7 | 71% / +0.04R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 6 | 33% / -0.86R | 6 | 33% / -0.51R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 4800 | 30% | -0.14R | 273 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 409 | 40% | -0.14R | 120 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 26 | 58% | +0.07R | 17 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1217 | 28% / -1.70R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 12 | 25% / -0.35R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 3678 | 38% / -0.22R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 948 | 33% / -0.58R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 66 | 23% / -0.89R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 601 | 30% / -1.84R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 781 | 34% / -0.15R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 291 | 42% / -1.23R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 97 | 30% / -1.25R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 140 | 26% / -1.00R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 385 | 31% / -0.21R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 10 | 20% / -0.43R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 110 | 36% / -0.34R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 50 | 42% / -0.14R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 4 | 0% / -1.16R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 6 | 17% / -1.54R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 23 | 43% / -0.35R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 42 · alerting: **5** · boot grace active: False
- **ALERT** `cohort_edge_gate` — all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 198/6) (sustained 198 cycles)
- **ALERT** `stale_tf_scoring` — scored on stale TF 8640x (gate reads 0x, withheld 0x — refusal dark); last XAIUSDT age=8924.1s (streak 73/6) (sustained 73 cycles)
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.40R (bound 0.3) (streak 198/6) (sustained 198 cycles)
- **ALERT** `tuned_variants` — 184 non-stamps — atr_arm_uncomputable=184 (seen=5497 stamped=369 skipped=4944) (streak 173/6) (sustained 173 cycles)
- **ALERT** `auto_dispatch` — 15 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: tier=16) (streak 112/3) (sustained 112 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 39 fed / 1 quiet / 0 never delivered of 40 subscribed; 21221232 accepted, 0 rejected | 0 |
| auto_dispatch | violating | 15 signals fanned out to keyed users with ZERO order attempts for anyone — every user is being silently skipped; check the fan-out summary log (cumulative skips: tier=16) (streak 112/3) | 112 |
| btc_reference | ok | BTC ref 64879.80 | 0 |
| candle_coverage | ok | 99/108 symbols with ≥20 15m candles, 86/108 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 943 dup bars, 0 undedupable; ws 0 out-of-order, 184 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 27 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 27 cohorts, 7 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 198/6) | 198 |
| context_emission_policy | ok | output +27 / upstream +34 | 0 |
| dark_resolution | violating | 1 of 59 open dark rows are not being advanced (worst: DODOXUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 7/120) | 7 |
| dark_sar_arms | ok | no open dark arms | 0 |
| depth_feed | ok | 39/40 books fresh (stale 1, never 0, thin 0); 5049033 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.40R (bound 0.3) (streak 198/6) | 198 |
| emission_controller | ok | last cycle 1644s ago; live_overrides=24 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=13 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4046 stamps (MEAN_REVERT=1126, MOVER_AVWAP_SCALP=106, MOVER_TREND_PULLBACK=2464, RANGE_FADE=246, TREND_PULLBACK_EMA=104), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 2/6) | 2 |
| footprint_bars | ok | 4754 sealed bars over 40 symbols; 202 incomplete, 4 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +1 / upstream +276 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 465 detections since last emission (emitted_total=12) — and the POST-SCORING blocked candidates measure +0.47R over n=3929, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 5/6) | 5 |
| mean_revert_path | ok | output +76 / upstream +276 | 0 |
| mover_admission_metadata | ok | 854 symbols known, 153 marked TRADIFI_PERPETUAL | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 254241 evicted (sampled: execution:overextended 400/90393, execution:trigger_not_confirmed 400/87796, setup_compat:regime_STRONG_TREND 400/32133) | 0 |
| price_action_lane | ok | 722324 evaluated, 338 emitted; layer1 338 stamped / 0 blind; cooldown=67064, delta_opposed=45580, no_footprint=239228, no_opposing_target=3843, no_sweep=328796, rr_below_floor=37475 | 0 |
| promoted_pair_integrity | ok | 12/12 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 4 detections since last progress | 0 |
| range_fade_path | violating | upstream +276 but output +0 (streak 1/72) | 1 |
| sar_alignment_crosscheck | ok | 153/11750 disagreed (1.3%) | 0 |
| sar_exit_shadow | ok | output +2 / upstream +276 | 0 |
| sar_ledger_candles | ok | 29/99 unfetchable (29%); top cause: gap or duplicate bar in the 15m window; symbols: ACEUSDT, ALLOUSDT, BANKUSDT, BICOUSDT, BSBUSDT +7 more | 0 |
| sar_live_arms | ok | 7 arms current, none stalled | 0 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 2 resolved, 68 still mid-window | 0 |
| setup_tf_resolver | ok | 226522 resolutions, 148979 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| stale_tf_scoring | violating | scored on stale TF 8640x (gate reads 0x, withheld 0x — refusal dark); last XAIUSDT age=8924.1s (streak 73/6) | 73 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +87 / upstream +276 | 0 |
| structural_snap | ok | 798/798 measured, 4 blind, 0 levels moved (refusals: redetect_cooldown=1403) | 0 |
| structural_veto_lane | ok | 1756 stamped; 0 with no readable level book, 198 with clear air ahead, 1002 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +276 / upstream +34 | 0 |
| tuned_variants | violating | 184 non-stamps — atr_arm_uncomputable=184 (seen=5497 stamped=369 skipped=4944) (streak 173/6) | 173 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `72526`
- `Path funnel` emissions: `33`
- `Regime distribution` emissions: `33`
- `QUIET_SCALP_BLOCK` events: `108`
- `confidence_gate` events: `3582`
- `free_channel_post` events: `9`
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
- Total posts in window: **9**

| Source | Count |
|---|---:|
| signal_close | 8 |
| regime_shift | 1 |

- By severity: HIGH=9

## Dependency readiness
- cvd: presence[present=217932] state[populated=217932] buckets[many=217932] sources[none] quality[none]
- funding_rate: presence[absent=34223, present=183709] state[empty=34223, populated=183709] buckets[few=183709, none=34223] sources[none] quality[none]
- liquidation_clusters: presence[absent=147660, present=70272] state[empty=147660, populated=70272] buckets[few=55129, none=147660, some=15143] sources[none] quality[none]
- oi_snapshot: presence[absent=34223, present=183709] state[empty=34223, populated=183709] buckets[few=361, many=182497, none=34223, some=851] sources[none] quality[none]
- order_book: presence[absent=64919, present=153013] state[populated=153013, unavailable=64919] buckets[few=153013, none=64919] sources[book_ticker=153013, unavailable=64919] quality[none=64919, top_of_book_only=153013]
- orderblocks: presence[absent=217932] state[empty=217932] buckets[none=217932] sources[measured_dark=217932] quality[none]
- recent_ticks: presence[absent=853, present=217079] state[empty=853, populated=217079] buckets[many=217079, none=853] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.160770893096924` sec
- Median create→first breach: `2700.527729034424` sec
- Median create→terminal: `2702.9244360923767` sec
- Median first breach→terminal: `6.293399810791016` sec
- Fast-failure buckets: `{"under_120s": {"count": 2, "pct": 8.7}, "under_180s": {"count": 2, "pct": 8.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 4.3}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 4.3}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 2.2839517423607103 | 2.595457854018842 | 0.8799802851062323 | 0 | 1 |
| MOVER_TREND_PULLBACK | 22 | 22 | 4.684092799038726 | 3.0 | 1.5613642663462421 | 19 | 3 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.284 | 16409.91902089119 | 16411.268497943878 |
| MOVER_TREND_PULLBACK | 22 | 22 | 0.0 | 36.4 | 0.0 | 0.0 | 1.5179 | 2653.6918395757675 | 2656.2413705587387 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 38 | 0 | 38 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 886 | 9 | 824 | 0.0 | 0.0 | None | None | 62 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-307`
- Gating Δ: `-61637`
- No-generation Δ: `-1504247`
- Fast failures Δ: `2`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 2.1295, "current_avg_pnl": 1.5179, "current_win_rate": 0.0, "previous_avg_pnl": -0.6116, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -76, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -8, "geometry_changed_delta": 0, "geometry_preserved_delta": -168, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
