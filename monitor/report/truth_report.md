# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, DIVERGENCE_CONTINUATION, MOVER_AVWAP_SCALP
- Top promising signals/paths: MEAN_REVERT
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `1961` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 92 | 92 | 82 | 4 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 7307 | 7307 | 6877 | 8 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 58187 | 58188 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 42472 | 42472 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 42242 | 41026 | 1432 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 42484 | 42156 | 354 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 44857 | 44727 | 142 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 36943 | 36952 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 42515 | 42534 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MEAN_REVERT | 42537 | 41212 | 1929 | 0 | 0 | 0 | low-sample (no_extension) |
| EVAL::MOVER_AVWAP_SCALP | 62798 | 66746 | 1002 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 58208 | 49934 | 12832 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 44385 | 44385 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 42475 | 42480 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 42230 | 42182 | 57 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::RANGE_FADE | 43144 | 42443 | 1087 | 0 | 0 | 0 | low-sample (no_range_edge) |
| EVAL::SR_FLIP_RETEST | 41742 | 42055 | 157 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 34511 | 31400 | 3299 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 34706 | 34428 | 336 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 58155 | 58137 | 46 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 36955 | 36970 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2170 | 2170 | 2044 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 492 | 492 | 431 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 13 | 13 | 5 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20129 | 20129 | 19918 | 9 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 2 | 0 | low-sample (none) |
| MEAN_REVERT | 0 | 0 | 5914 | 5914 | 5471 | 3 | active-healthy (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 3303 | 3303 | 2897 | 28 | active-low-quality (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 41545 | 41545 | 36499 | 236 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 509 | 509 | 480 | 6 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 3851 | 3851 | 3788 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 650 | 650 | 643 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2067 | 2067 | 1878 | 23 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 277 | 277 | 257 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=58188): breakout_not_found=37967, basic_filters_failed=13148, move_not_fresh=3643, breakout_stale=2482, retest_proximity_failed=722, volume_spike_missing=205, missing_fvg_or_orderblock=14, move_exhausted=7
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=42472): cls_disabled_merged_into_lsr=42472
- **EVAL::DIVERGENCE_CONTINUATION** (total=41026): cvd_divergence_failed=19550, h1_trend_not_aligned=10499, basic_filters_failed=8027, ema_alignment_reject=2159, retest_proximity_failed=598, missing_fvg_or_orderblock=193
- **EVAL::FAILED_AUCTION_RECLAIM** (total=42156): auction_not_detected=29458, basic_filters_failed=7607, regime_blocked=2287, reclaim_hold_failed=1851, tail_too_small=952, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=44727): funding_not_extreme=34702, basic_filters_failed=8595, ema_alignment_reject=845, rsi_reject=321, momentum_reject=116, cvd_divergence_failed=103, missing_fvg_or_orderblock=27, missing_funding_rate=18
- **EVAL::LIQUIDATION_REVERSAL** (total=36952): cascade_threshold_not_met=27948, basic_filters_failed=8434, rsi_reject=316, cvd_divergence_failed=247, missing_fvg_or_orderblock=6, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=42534): no_ma_cross=34133, basic_filters_failed=8036, ma_cross_cooldown=185, ma_cross_htf_misaligned=180
- **EVAL::MEAN_REVERT** (total=41212): no_extension=33186, basic_filters_failed=8026
- **EVAL::MOVER_AVWAP_SCALP** (total=66746): no_avwap_tag=31507, basic_filters_failed=13311, no_mover_leg=13084, avwap_slope_against=4857, avwap_reclaim_no_volume=2563, no_avwap_reclaim=1383, anchor_too_recent=41
- **EVAL::MOVER_TREND_PULLBACK** (total=49934): mover_run_too_small=19536, no_reclaim=14935, basic_filters_failed=13231, no_pullback_tag=2232
- **EVAL::OPENING_RANGE_BREAKOUT** (total=44385): feature_disabled=44385
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=42480): regime_blocked=32784, breakout_not_found=7898, basic_filters_failed=1513, adx_reject=264, ema_alignment_reject=21
- **EVAL::QUIET_COMPRESSION_BREAK** (total=42182): compression_not_detected=23152, regime_blocked=11929, basic_filters_failed=6085, breakout_not_detected=920, volume_confirmation_failed=90, missing_fvg_or_orderblock=6
- **EVAL::RANGE_FADE** (total=42443): no_range_edge=34415, basic_filters_failed=8028
- **EVAL::SR_FLIP_RETEST** (total=42055): flip_close_not_confirmed=27567, basic_filters_failed=7593, regime_blocked=2279, retest_out_of_zone=1635, long_break_volume_thin=1453, h1_break_not_confirmed=693, reclaim_hold_failed=581, ema_alignment_reject=115, long_acceptance_not_held=55, wick_quality_failed=33, missing_fvg_or_orderblock=26, whipsaw_flip=25
- **EVAL::STANDARD** (total=31400): adx_reject=8191, momentum_reject=5640, basic_filters_failed=5622, macd_reject=4354, sweeps_not_detected=3378, ema_alignment_reject=3033, htf_poi_unanchored=1038, invalid_sl_geometry=106, rsi_reject=38
- **EVAL::TREND_PULLBACK** (total=34428): h1_trend_not_aligned=10806, ema_alignment_reject=5917, basic_filters_failed=4885, ema_not_tested_prev=3632, h1_pullback_not_confirmed=3050, no_ema_reclaim_close=3042, body_conviction_fail=1149, rsi_reject=836, prev_already_above_emas=513, no_prev_high_break=245, prev_already_below_emas=158, no_prev_low_break=75, momentum_flat=73, ema21_not_tagged=37, missing_fvg_or_orderblock=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=58137): breakout_not_found=31189, basic_filters_failed=13148, move_not_fresh=8389, breakout_stale=3530, retest_proximity_failed=1544, volume_spike_missing=298, missing_fvg_or_orderblock=34, move_exhausted=5
- **EVAL::WHALE_MOMENTUM** (total=36970): momentum_reject=27294, recent_ticks_insufficient=7707, basic_filters_failed=1969

## Pre-scoring gate rejects (setup-compat / execution-quality)
- **BREAKDOWN_SHORT** (total=11): execution:overextended=11
- **DIVERGENCE_CONTINUATION** (total=397): setup_compat:regime_VOLATILE_UNSUITABLE=387, setup_compat:regime_BREAKOUT_EXPANSION=10
- **FAILED_AUCTION_RECLAIM** (total=646): setup_compat:regime_STRONG_TREND=304, execution:overextended=290, context_floor=52
- **FUNDING_EXTREME_SIGNAL** (total=307): execution:trigger_not_confirmed=307
- **LIQUIDATION_REVERSAL** (total=13): execution:trigger_not_confirmed=13
- **LIQUIDITY_SWEEP_REVERSAL** (total=4980): execution:overextended=2128, setup_compat:regime_STRONG_TREND=1445, execution:trigger_not_confirmed=1407
- **MA_CROSS_TREND_SHIFT** (total=6): setup_compat:regime_DIRTY_RANGE=3, execution:overextended=2, execution:trigger_not_confirmed=1
- **MEAN_REVERT** (total=3216): setup_compat:regime_STRONG_TREND=1425, setup_compat:regime_WEAK_TREND=1043, execution:overextended=746, entry_quality=2
- **MOVER_AVWAP_SCALP** (total=2094): execution:overextended=1773, execution:trigger_not_confirmed=291, entry_quality=30
- **MOVER_TREND_PULLBACK** (total=16889): execution:trigger_not_confirmed=9485, execution:overextended=6718, entry_quality=686
- **QUIET_COMPRESSION_BREAK** (total=17): execution:trigger_not_confirmed=13, execution:overextended=4
- **RANGE_FADE** (total=1533): setup_compat:regime_STRONG_TREND=672, setup_compat:regime_WEAK_TREND=552, execution:overextended=283, setup_compat:regime_VOLATILE_UNSUITABLE=23, setup_compat:regime_BREAKOUT_EXPANSION=2, context_edge=1
- **TREND_PULLBACK_EMA** (total=1905): setup_compat:regime_CLEAN_RANGE=1058, setup_compat:regime_DIRTY_RANGE=721, setup_compat:regime_VOLATILE_UNSUITABLE=67, entry_quality=59
- **VOLUME_SURGE_BREAKOUT** (total=44): execution:overextended=44

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 213832 | 61.2% |
| TRENDING_UP | 46544 | 13.3% |
| QUIET | 36525 | 10.5% |
| TRENDING_DOWN | 34763 | 9.9% |
| VOLATILE | 17825 | 5.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **54**
- Average confidence gap to threshold: **12.71** (samples=54) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: INJUSDT=7, LSKUSDT=7, COTIUSDT=6, GPSUSDT=6, BTCUSDT=6, LITUSDT=5, ASTERUSDT=3, FILUSDT=3, ETHUSDT=3, ZETAUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 10 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 95 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 8 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 7 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 6 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 21 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 50 |
| MEAN_REVERT | kept | min_confidence_pass | 14 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 111 |
| MOVER_AVWAP_SCALP | filtered | quiet_scalp_min_confidence | 3 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 143 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 664 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 22 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1627 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 14 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 8 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 6 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 59 |
| TREND_PULLBACK_EMA | filtered | quiet_scalp_min_confidence | 6 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 43 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 18 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 10 | 69.22 | 65.00 | -4.22 | 20.10 | 19.41 | 20.00 | 3.70 | 5.58 |
| DIVERGENCE_CONTINUATION | filtered | 95 | 57.43 | 64.40 | 6.97 | 20.16 | 19.60 | 18.39 | 0.97 | 11.89 |
| DIVERGENCE_CONTINUATION | kept | 8 | 69.46 | 65.00 | -4.46 | 21.69 | 19.48 | 17.53 | 4.00 | 0.68 |
| FAILED_AUCTION_RECLAIM | filtered | 13 | 53.12 | 63.46 | 10.34 | 20.31 | 19.29 | 20.00 | 3.77 | 17.66 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 70.50 | 65.00 | -5.50 | 19.15 | 18.85 | 20.00 | 5.00 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 52.80 | 61.00 | 8.20 | 22.55 | 20.00 | 17.00 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 24 | 45.06 | 64.50 | 19.44 | 20.49 | 17.89 | 17.43 | 1.92 | 22.22 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 50 | 70.35 | 65.00 | -5.35 | 20.10 | 18.64 | 17.55 | 1.80 | 0.42 |
| MEAN_REVERT | kept | 14 | 67.91 | 65.00 | -2.91 | 21.45 | 15.04 | 16.29 | 0.00 | 1.71 |
| MOVER_AVWAP_SCALP | filtered | 114 | 56.03 | 63.86 | 7.83 | 19.06 | 16.82 | 15.80 | 5.03 | 13.21 |
| MOVER_AVWAP_SCALP | kept | 143 | 79.74 | 65.00 | -14.74 | 20.62 | 15.11 | 15.80 | 4.51 | 2.71 |
| MOVER_TREND_PULLBACK | filtered | 686 | 55.17 | 63.64 | 8.47 | 20.27 | 18.79 | 15.80 | 4.09 | 19.49 |
| MOVER_TREND_PULLBACK | kept | 1627 | 75.86 | 65.00 | -10.86 | 20.43 | 18.44 | 15.80 | 4.22 | 2.00 |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 54.04 | 63.64 | 9.60 | 21.50 | 19.62 | 20.00 | 0.00 | 13.65 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 77.92 | 65.00 | -12.92 | 21.55 | 19.72 | 20.00 | 0.00 | 2.67 |
| SR_FLIP_RETEST | kept | 1 | 65.00 | 65.00 | 0.00 | 20.90 | 20.00 | 20.00 | 1.00 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 65 | 58.09 | 65.00 | 6.91 | 20.74 | 19.35 | 18.38 | 3.93 | 18.94 |
| TREND_PULLBACK_EMA | kept | 43 | 75.77 | 65.00 | -10.77 | 20.83 | 19.71 | 17.68 | 4.92 | 1.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 49.00 | 65.00 | 16.00 | 19.14 | 16.70 | 20.00 | 3.50 | 7.80 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 75.85 | 65.00 | -10.85 | 18.30 | 16.95 | 20.00 | 5.50 | 1.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 10 | 69.22 | 17.80 | 17.60 | 12.30 | 13.70 | 5.00 | 4.70 | 3.70 |
| DIVERGENCE_CONTINUATION | filtered | 95 | 57.43 | 23.40 | 16.00 | 3.69 | 11.64 | 5.40 | 8.21 | 0.97 |
| DIVERGENCE_CONTINUATION | kept | 8 | 69.46 | 22.00 | 14.25 | 4.88 | 11.88 | 5.00 | 8.89 | 4.00 |
| FAILED_AUCTION_RECLAIM | filtered | 13 | 53.12 | 24.08 | 14.92 | 5.77 | 13.77 | 5.62 | 2.85 | 3.77 |
| FAILED_AUCTION_RECLAIM | kept | 2 | 70.50 | 25.00 | 14.00 | 3.00 | 12.00 | 7.00 | 4.50 | 5.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 52.80 | 25.00 | 18.00 | 3.00 | 14.00 | 8.50 | 4.30 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 24 | 45.06 | 21.67 | 15.50 | 5.00 | 11.71 | 3.65 | 7.85 | 1.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 50 | 70.35 | 24.68 | 15.04 | 4.02 | 11.58 | 7.25 | 6.40 | 1.80 |
| MEAN_REVERT | kept | 14 | 67.91 | 18.71 | 15.14 | 9.64 | 13.00 | 5.00 | 8.13 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 114 | 56.03 | 16.96 | 18.51 | 10.14 | 13.95 | 6.70 | 5.45 | 5.03 |
| MOVER_AVWAP_SCALP | kept | 143 | 79.74 | 20.47 | 18.03 | 11.07 | 13.66 | 6.57 | 8.17 | 4.51 |
| MOVER_TREND_PULLBACK | filtered | 686 | 55.17 | 17.62 | 18.02 | 8.11 | 13.39 | 5.89 | 8.41 | 4.09 |
| MOVER_TREND_PULLBACK | kept | 1627 | 75.86 | 19.47 | 18.06 | 7.80 | 13.09 | 6.66 | 8.62 | 4.22 |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 54.04 | 19.55 | 16.55 | 10.64 | 14.14 | 7.86 | 3.75 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 77.92 | 22.33 | 18.00 | 12.50 | 14.50 | 6.42 | 7.83 | 0.00 |
| SR_FLIP_RETEST | kept | 1 | 65.00 | 17.00 | 18.00 | 6.00 | 11.00 | 5.00 | 7.00 | 1.00 |
| TREND_PULLBACK_EMA | filtered | 65 | 58.09 | 17.40 | 18.00 | 8.19 | 14.46 | 6.20 | 8.85 | 3.93 |
| TREND_PULLBACK_EMA | kept | 43 | 75.77 | 18.51 | 18.00 | 7.81 | 14.26 | 6.24 | 9.56 | 4.92 |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 49.00 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 5.30 | 3.50 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 75.85 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 9.35 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 10 | 69.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.48 | **3.48** |
| DIVERGENCE_CONTINUATION | filtered | 95 | 57.43 | 0.00 | 0.00 | 1.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.67** |
| DIVERGENCE_CONTINUATION | kept | 8 | 69.46 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.20** |
| FAILED_AUCTION_RECLAIM | filtered | 13 | 53.12 | 0.00 | 0.00 | 0.00 | 0.00 | 1.66 | 0.00 | 0.00 | 0.00 | **1.66** |
| FAILED_AUCTION_RECLAIM | kept | 2 | 70.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 52.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 24 | 45.06 | 0.00 | 0.00 | 2.40 | 0.00 | 2.70 | 0.00 | 0.00 | 0.00 | **5.10** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 50 | 70.35 | 0.00 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.32** |
| MEAN_REVERT | kept | 14 | 67.91 | 0.00 | 0.00 | 0.00 | 0.00 | 1.71 | 0.00 | 0.00 | 0.00 | **1.71** |
| MOVER_AVWAP_SCALP | filtered | 114 | 56.03 | 0.00 | 0.00 | 3.02 | 0.00 | 2.67 | 0.25 | 0.00 | 0.21 | **6.15** |
| MOVER_AVWAP_SCALP | kept | 143 | 79.74 | 0.00 | 0.00 | 0.45 | 0.00 | 1.26 | 0.07 | 0.00 | 0.44 | **2.22** |
| MOVER_TREND_PULLBACK | filtered | 686 | 55.17 | 0.35 | 0.00 | 1.86 | 0.00 | 0.56 | 0.28 | 0.00 | 0.09 | **3.14** |
| MOVER_TREND_PULLBACK | kept | 1627 | 75.86 | 0.00 | 0.00 | 0.79 | 0.00 | 0.17 | 0.05 | 0.00 | 0.06 | **1.07** |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 54.04 | 0.00 | 0.00 | 2.84 | 0.00 | 0.39 | 0.82 | 0.00 | 6.44 | **10.49** |
| QUIET_COMPRESSION_BREAK | kept | 6 | 77.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.80 | **1.80** |
| SR_FLIP_RETEST | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 65 | 58.09 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.28 | 0.00 | 0.00 | **0.28** |
| TREND_PULLBACK_EMA | kept | 43 | 75.77 | 0.00 | 0.00 | 1.00 | 0.00 | 0.28 | 0.23 | 0.00 | 0.00 | **1.51** |
| VOLUME_SURGE_BREAKOUT | filtered | 18 | 49.00 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 75.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **107601 held of 282791 seen** across 21 strategies; 2459 cells past the sample floor; **1097 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 37664 | 641/37023/0 | 44% | -0.15 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | OVERLAP/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.16R) |
| MOVER_AVWAP_SCALP | 13417 | 200/13217/0 | 41% | -0.25 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL/MAJOR (+1.17R) | NY/MARKDOWN/NORMAL/BTC_RISING (-1.34R) |
| FAILED_AUCTION_RECLAIM | 8202 | 108/8094/0 | 42% | -0.18 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 6714 | 40/6674/0 | 51% | +0.00 | LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP (+1.68R) | NY/MARKDOWN/EXPANDED/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 5880 | 0/0/5880 | 43% | -0.11 | ASIA/MARKDOWN/CASCADE/BTC_FALLING (+0.50R) | OVERLAP/QUIET/EXPANDED/BTC_NEUTRAL (-0.84R) |
| TREND_PULLBACK_EMA | 5424 | 24/5400/0 | 44% | -0.18 | NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP (+2.19R) | OVERLAP/ACCUMULATION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.28R) |
| SHADOW_RANGE_FADE | 5035 | 0/0/5035 | 37% | -0.10 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.70R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.17R) |
| QUIET_COMPRESSION_BREAK | 4739 | 294/4445/0 | 46% | -0.13 | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_FUNDING_FADE | 4601 | 0/0/4601 | 34% | -0.40 | ASIA/MARKDOWN/CASCADE/BTC_NEUTRAL (-0.02R) | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_FALLING (-0.98R) |
| WHALE_MOMENTUM | 3365 | 2/3363/0 | 44% | -0.33 | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (+0.41R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 3310 | 63/3247/0 | 37% | -0.38 | NY/RANGE/NORMAL/BTC_FALLING (+1.64R) | NY/MARKDOWN/EXPANDED/BTC_FALLING (-1.23R) |
| MEAN_REVERT | 2183 | 30/2153/0 | 49% | -0.13 | LONDON/MARKDOWN/EXPANDED/BTC_RISING (+1.23R) | OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL (-1.53R) |
| FUNDING_EXTREME_SIGNAL | 1843 | 2/1841/0 | 33% | -0.41 | LONDON/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL/MIDCAP (+0.92R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP (-1.36R) |
| VOLUME_SURGE_BREAKOUT | 1690 | 0/1690/0 | 42% | +0.01 | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+2.46R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.19R) |
| SR_FLIP_RETEST | 1186 | 10/1176/0 | 48% | -0.23 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.79R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.25R) |
| SHADOW_CASCADE_REVERSAL | 846 | 0/0/846 | 53% | -0.04 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.14R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (-0.47R) |
| RANGE_FADE | 719 | 0/719/0 | 41% | -0.37 | LONDON/DISTRIBUTION/NORMAL/BTC_FALLING (+1.59R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.26R) |
| BREAKDOWN_SHORT | 503 | 43/460/0 | 31% | -0.38 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/MIDCAP (+1.00R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_RISING (-1.18R) |
| LIQUIDATION_REVERSAL | 212 | 0/212/0 | 10% | -1.02 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.25R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.38R) |
| MA_CROSS_TREND_SHIFT | 62 | 6/56/0 | 45% | -0.06 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 6 | 0/6/0 | 67% | +0.42 | — | — |

- **Strongest cells**: `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL` +2.46R (n=21, STRONG); `VOLUME_SURGE_BREAKOUT @ LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR` +2.46R (n=21, STRONG); `TREND_PULLBACK_EMA @ NY/ACCUMULATION/NORMAL/BTC_NEUTRAL/MIDCAP` +2.19R (n=27, STRONG)
- **Weakest cells**: `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.53R (n=15, NEGATIVE); `MEAN_REVERT @ OFF_HOURS/QUIET/NORMAL/BTC_NEUTRAL` -1.53R (n=15, NEGATIVE); `LIQUIDATION_REVERSAL @ OVERLAP/MARKDOWN/CASCADE/BTC_FALLING/MIDCAP` -1.38R (n=17, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 143 | 28% / -0.54R | 143 | 48% / -0.18R | +0.36 | **ATR** |
| TREND_PULLBACK_EMA | 447 | 44% / -0.23R | 447 | 54% / -0.04R | +0.19 | **ATR** |
| MOVER_AVWAP_SCALP | 1070 | 44% / -0.19R | 1070 | 50% / -0.08R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 367 | 44% / -0.32R | 367 | 46% / -0.22R | +0.10 | **ATR** |
| BREAKDOWN_SHORT | 38 | 37% / -0.20R | 38 | 39% / -0.10R | +0.10 | **ATR** |
| SR_FLIP_RETEST | 132 | 49% / -0.26R | 132 | 51% / -0.18R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 5831 | 50% / -0.09R | 5831 | 55% / -0.01R | +0.08 | **ATR** |
| FAILED_AUCTION_RECLAIM | 750 | 43% / -0.18R | 750 | 45% / -0.10R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 648 | 50% / -0.21R | 648 | 55% / -0.14R | +0.07 | **ATR** |
| RANGE_FADE | 36 | 39% / -0.21R | 36 | 42% / -0.24R | -0.03 | **FIXED** |
| VOLUME_SURGE_BREAKOUT | 96 | 40% / -0.09R | 96 | 47% / -0.06R | +0.02 | **ATR** |
| DIVERGENCE_CONTINUATION | 639 | 51% / -0.05R | 639 | 56% / -0.04R | +0.01 | **ATR** |
| MEAN_REVERT | 157 | 54% / -0.07R | 157 | 52% / -0.06R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 781 | 45% / -0.16R | 781 | 45% / -0.17R | -0.01 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 20 | 40% / -0.15R | 20 | 40% / -0.14R | +0.01 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 5 | 40% / -0.24R | 5 | 40% / -0.12R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 14 | 29% / -0.51R | 14 | 57% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 8367 | 29% | -0.24R | 309 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 1070 | 48% | -0.07R | 194 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 61 | 51% | -0.05R | 47 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 139 | 37% / -0.30R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 757 | 36% / -0.11R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 7465 | 37% / -0.14R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 1422 | 35% / -0.12R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 598 | 35% / -0.13R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 724 | 41% / +0.02R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 597 | 38% / -0.06R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 647 | 42% / -0.16R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 134 | 28% / -0.40R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 187 | 30% / -0.58R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 131 | 56% / +0.13R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 67 | 42% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 28 | 36% / +0.13R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 136 | 35% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 29 | 17% / -0.49R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 19 | 42% / -0.05R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.05R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 56 · alerting: **4** · boot grace active: False
- **ALERT** `entry_feature_inputs` — 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×374]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 390/6) (sustained 390 cycles)
- **ALERT** `edge_reconciliation` — MEAN_REVERT realized−counterfactual=+0.64R (bound 0.3) (streak 463/6) (sustained 463 cycles)
- **ALERT** `tuned_variants` — 133 non-stamps — atr_arm_uncomputable=133 (seen=2533 stamped=573 skipped=1827) (streak 463/6) (sustained 463 cycles)
- **ALERT** `ai_governor_blind` — 50/50 verdicts had no readable context (streak 463/3) (sustained 463 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 44 fed / 0 quiet / 0 never delivered of 44 subscribed; 181405792 accepted, 0 rejected | 0 |
| ai_governor_blind | violating | 50/50 verdicts had no readable context (streak 463/3) | 463 |
| ai_governor_live_arms | ok | 28 arms current, none stalled; covering 673/673 signals (100%) | 0 |
| ai_governor_verdicts | ok | output +0 / upstream +0 | 0 |
| atr_trail_live_arms | ok | 54 arms current, none stalled; covering 1092/1092 signals (100%) | 0 |
| auto_dispatch | ok | 71 signals fanned out to keyed users and none reached the order path — but every skip is a user setting, not a fault: mode:paper=142. No user is on live. | 0 |
| btc_reference | ok | BTC ref 87114.80 | 0 |
| candle_coverage | ok | 97/97 symbols with ≥20 15m candles, 97/97 updated within 45m [fresh=97; 77 Tier-1 futures + 20 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 620 dup bars, 0 undedupable; ws 0 out-of-order, 354 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +4 / upstream +19 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1294/1311 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | ok | 123 open rows, all advancing | 0 |
| dark_sar_arms | ok | no open arms; covering 1291/1308 signals (99%) | 0 |
| depth_feed | ok | 44/44 books fresh (stale 0, never 0, thin 0); 41441663 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MEAN_REVERT realized−counterfactual=+0.64R (bound 0.3) (streak 463/6) | 463 |
| emission_controller | ok | last cycle 1350s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | enforcing; dead_overrides=0 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | violating | 2 declared feature(s) absent on EVERY stamp of their path: RANGE_FADE.campaign_prev_age_h[cause unrecorded],RANGE_FADE.campaign_prev_won[first_leg×374]; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) (streak 390/6) | 390 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/200 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing. Window spent by: session_quality=70. Held back in this window: session_quality=130. Live rules: profile_reject,session_quality,mover_stack_15m,cvd_aligned (streak 1/6) | 1 |
| footprint_bars | ok | 5280 sealed bars over 44 symbols; 1979 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +144 | 0 |
| indicator_cache_key | ok | 193896 frozen value(s) avoided; 556091 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | fully gated, and correctly: MEAN_REVERT POST-SCORING counterfactuals measure -0.14R over n=2153 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| mean_revert_path | ok | output +5 / upstream +144 | 0 |
| mover_admission_metadata | ok | 906 symbols known, 200 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 20 held, 20 with scan counts, 16 with an activity reading (enforcing) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 4 locked / 4 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 3200 rows held, 1700495 evicted (sampled: execution:trigger_not_confirmed 400/623768, execution:overextended 400/563605, setup_compat:regime_STRONG_TREND 400/253249) | 0 |
| price_action_lane | ok | 730541 evaluated, 1261 emitted; layer1 1261 stamped / 0 blind; cooldown=96001, delta_opposed=63498, no_footprint=347437, no_opposing_target=1333, no_sweep=162206, rr_below_floor=58805 | 0 |
| promoted_pair_integrity | ok | 20/20 promoted pairs present in universe | 0 |
| range_fade_emission | ok | fully gated, and correctly: RANGE_FADE POST-SCORING counterfactuals measure -0.37R over n=719 — emitting them would lose money (pre-scoring rejects are measured in the dark lane, not here) | 0 |
| range_fade_path | ok | output +4 / upstream +144 | 0 |
| sar_alignment_crosscheck | ok | 699/15169 disagreed (4.6%) | 0 |
| sar_exit_shadow | violating | upstream +144 but output +0 (streak 4/6) | 4 |
| sar_hold_arm | ok | 1839 held arms settled, 161 unscored, 53 still walking (49 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | 37/37 resolvable | 0 |
| sar_live_arms | ok | 53 arms current, none stalled; covering 1090/1090 signals (100%) | 0 |
| sar_refresh_budget | ok | 9 refreshed, none turned away | 0 |
| sar_resolution_progress | violating | 0 verdicts produced while 437 records await one (37 had candles and still resolved nothing). The ledger is not advancing — check resolver candle freshness. (streak 1/12) | 1 |
| scan_cycle | ok | last 29.2s, worst 147.88s over 7588 lifetime cycles; lifetime 158 over 60s, 3 over 120s; recent 0/0 warn/kill breaches in 20/20 cycles; heartbeat age 3.34s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 344078 resolutions, 0 would move off 5m, 0 unmapped, correction LIVE | 0 |
| shadow_units | ok | last shadow stamp 0m ago | 0 |
| snapshot_writer | ok | last cycle 4s ago (32.43s to run, worst 87.37s), 997 overrun(s) of 9010 cycles, TTL 900s; slowest trail_governor=6.38s, dark_promotion=4.45s, exchange_positions=3.4s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=909, gate reads=0, withheld=909) | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +16 / upstream +144 | 0 |
| structural_snap | ok | 5424/5424 measured, 27 blind, 0 levels moved (refusals: redetect_cooldown=209) | 0 |
| structural_veto_lane | ok | 707 stamped; 0 with no readable level book, 11 with clear air ahead, 523 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +144 / upstream +19 | 0 |
| tuned_variants | violating | 133 non-stamps — atr_arm_uncomputable=133 (seen=2533 stamped=573 skipped=1827) (streak 463/6) | 463 |

Fail-open exception counters (nonzero sites):
- `llm_client.google`: 3 — last: TimeoutError: 

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1739254`
- `Path funnel` emissions: `37`
- `Regime distribution` emissions: `37`
- `QUIET_SCALP_BLOCK` events: `54`
- `confidence_gate` events: `2945`
- `free_channel_post` events: `0`
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
| futures_aggtrade | 4 | 5624 | 6373 | 8245 | 0 |
| futures_liq | 1 | 8898 | 8898 | 8898 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- _no free-channel posts in this window_

## Dependency readiness
- cvd: presence[present=303968] state[populated=303968] buckets[few=5, many=303943, some=20] sources[none] quality[none]
- funding_rate: presence[absent=51739, present=252229] state[empty=51739, populated=252229] buckets[few=252229, none=51739] sources[none] quality[none]
- liquidation_clusters: presence[absent=160670, present=143298] state[empty=160670, populated=143298] buckets[few=115392, none=160670, some=27906] sources[none] quality[none]
- oi_snapshot: presence[absent=51739, present=252229] state[empty=51739, populated=252229] buckets[few=217, many=250616, none=51739, some=1396] sources[none] quality[none]
- order_book: presence[absent=112562, present=191406] state[populated=191406, unavailable=112562] buckets[few=191406, none=112562] sources[book_ticker=191406, unavailable=112562] quality[none=112562, top_of_book_only=191406]
- orderblocks: presence[absent=303968] state[empty=303968] buckets[none=303968] sources[measured_dark=303968] quality[none]
- recent_ticks: presence[present=303968] state[populated=303968] buckets[many=303968] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.889811992645264` sec
- Median create→first breach: `4739.714052200317` sec
- Median create→terminal: `4740.0018610954285` sec
- Median first breach→terminal: `5.2928924560546875e-05` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 1.8781725888324872 | 3.0 | 0.9315104722091887 | 0 | 3 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 2.264471623287907 | 2.4530184600033293 | 0.9166722684480854 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.3663024957285173 | 1.5800125498210544 | 0.864741546441045 | 0 | 1 |
| MEAN_REVERT | 3 | 3 | 1.3214611146265902 | 1.4461877236443696 | 0.9167029616724771 | 0 | 3 |
| MOVER_AVWAP_SCALP | 6 | 6 | 2.3826859322851766 | 2.3649394124812018 | 0.9452802773730504 | 2 | 3 |
| MOVER_TREND_PULLBACK | 21 | 21 | 3.8235923754372236 | 3.0 | 1.29354591678921 | 13 | 8 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 1.247693309931388 | 1.4191161987366026 | 0.8962399215659407 | 0 | 4 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 1.4431 | 16629.653561115265 | 16629.65358519554 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 1.8998 | 8646.781446933746 | 8647.138933897018 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.3663 | 17396.03853201866 | 17396.038562059402 |
| MEAN_REVERT | 3 | 3 | 66.7 | 0.0 | 66.7 | 0.0 | 0.9938 | 3042.1682291030884 | 3042.4417021274567 |
| MOVER_AVWAP_SCALP | 6 | 6 | 16.7 | 33.3 | 16.7 | 0.0 | -0.1797 | 17836.07189643383 | 17836.071932911873 |
| MOVER_TREND_PULLBACK | 21 | 21 | 38.1 | 33.3 | 38.1 | 0.0 | 0.4702 | 2918.3905708789825 | 2918.390589952469 |
| QUIET_COMPRESSION_BREAK | 6 | 6 | 16.7 | 50.0 | 16.7 | 0.0 | 0.0491 | 15462.130000472069 | 15462.33257651329 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 650 | 1 | 643 | 0.0 | 0.0 | None | None | 7 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2067 | 23 | 1878 | 0.0 | 0.0 | None | None | 189 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `158`
- Gating Δ: `-36883`
- No-generation Δ: `-264061`
- Fast failures Δ: `-1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -2.7064, "current_avg_pnl": 1.4431, "current_win_rate": 33.3, "previous_avg_pnl": 4.1495, "previous_win_rate": 100.0, "win_rate_delta": -66.7}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.8998, "current_avg_pnl": 1.8998, "current_win_rate": 33.3, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 33.3}, "MEAN_REVERT": {"avg_pnl_delta": 0.9938, "current_avg_pnl": 0.9938, "current_win_rate": 66.7, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 66.7}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 1.5129, "current_avg_pnl": -0.1797, "current_win_rate": 16.7, "previous_avg_pnl": -1.6926, "previous_win_rate": 25.0, "win_rate_delta": -8.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.527, "current_avg_pnl": 0.4702, "current_win_rate": 38.1, "previous_avg_pnl": 0.9972, "previous_win_rate": 45.8, "win_rate_delta": -7.7}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -2.3204, "current_avg_pnl": 0.0491, "current_win_rate": 16.7, "previous_avg_pnl": 2.3695, "previous_win_rate": 33.3, "win_rate_delta": -16.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": -12, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 15, "geometry_changed_delta": 0, "geometry_preserved_delta": 133, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **MEAN_REVERT**
- Most likely bottleneck: **RANGE_FADE**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
