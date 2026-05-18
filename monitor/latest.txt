# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, DIVERGENCE_CONTINUATION, LIQUIDITY_SWEEP_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `40` sec (warning=False)
- Latest performance record age: `510` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 824 | 824 | 625 | 2 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 51 | 51 | 35 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 13674 | 13674 | 13127 | 49 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 297321 | 296497 | 824 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 278041 | 277990 | 51 | 0 | 0 | 0 | low-sample (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 278041 | 264367 | 13674 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 278041 | 263253 | 14788 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 297321 | 297167 | 154 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 297321 | 297295 | 26 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 278041 | 278026 | 15 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 297321 | 297321 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 278041 | 278012 | 29 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 278041 | 273972 | 4069 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 278041 | 247807 | 30234 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 278041 | 263789 | 14252 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 278041 | 276602 | 1439 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 297321 | 296595 | 726 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 297321 | 297321 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 14788 | 14788 | 10126 | 92 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 154 | 154 | 126 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 26 | 26 | 26 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14252 | 14252 | 11190 | 144 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 13 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 29 | 29 | 29 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4069 | 4069 | 2850 | 46 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 30234 | 30234 | 18212 | 191 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1439 | 1439 | 1365 | 12 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 726 | 726 | 705 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=296497): breakout_not_found=154836, basic_filters_failed=97209, retest_proximity_failed=35597, volume_spike_missing=6117, ema_alignment_reject=1209, insufficient_candles=1061, missing_fvg_or_orderblock=463, rsi_reject=5
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=277990): cls_disabled_merged_into_lsr=245843, regime_blocked=16611, sweeps_not_detected=6285, basic_filters_failed=3872, ema_alignment_reject=2268, adx_reject=2047, momentum_reject=530, reclaim_confirmation_failed=312, insufficient_candles=222
- **EVAL::DIVERGENCE_CONTINUATION** (total=264367): regime_blocked=86505, cvd_divergence_failed=75301, basic_filters_failed=57806, h1_trend_not_aligned=21328, ema_alignment_reject=19530, retest_proximity_failed=2027, missing_fvg_or_orderblock=1648, insufficient_candles=222
- **EVAL::FAILED_AUCTION_RECLAIM** (total=263253): auction_not_detected=99034, basic_filters_failed=88205, reclaim_hold_failed=47617, tail_too_small=27843, insufficient_candles=546, regime_blocked=8
- **EVAL::FUNDING_EXTREME** (total=297167): funding_not_extreme=189449, basic_filters_failed=93208, missing_funding_rate=10958, ema_alignment_reject=2020, rsi_reject=866, momentum_reject=224, insufficient_candles=187, cvd_divergence_failed=182, missing_fvg_or_orderblock=73
- **EVAL::LIQUIDATION_REVERSAL** (total=297295): cascade_threshold_not_met=196645, basic_filters_failed=97327, rsi_reject=1202, cvd_divergence_failed=1185, insufficient_candles=792, missing_fvg_or_orderblock=77, volume_spike_missing=67
- **EVAL::MA_CROSS_TREND_SHIFT** (total=278026): no_ma_cross=187193, basic_filters_failed=88299, ma_cross_cooldown=2534
- **EVAL::OPENING_RANGE_BREAKOUT** (total=297321): feature_disabled=297321
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=278012): regime_blocked=180930, breakout_not_found=45325, basic_filters_failed=22823, ema_alignment_reject=17091, adx_reject=11621, insufficient_candles=222
- **EVAL::QUIET_COMPRESSION_BREAK** (total=273972): regime_blocked=97119, compression_not_detected=66940, basic_filters_failed=65380, breakout_not_detected=42568, rsi_reject=897, volume_confirmation_failed=472, insufficient_candles=343, missing_fvg_or_orderblock=253
- **EVAL::SR_FLIP_RETEST** (total=247807): basic_filters_failed=87538, reclaim_hold_failed=57964, flip_close_not_confirmed=45759, retest_out_of_zone=38132, wick_quality_failed=12057, ema_alignment_reject=2592, insufficient_candles=1926, missing_fvg_or_orderblock=1782, rsi_reject=49, regime_blocked=8
- **EVAL::STANDARD** (total=263789): momentum_reject=68215, basic_filters_failed=57008, adx_reject=54453, sweeps_not_detected=44485, macd_reject=24220, ema_alignment_reject=12137, insufficient_candles=1755, invalid_sl_geometry=1038, rsi_reject=478
- **EVAL::TREND_PULLBACK** (total=276602): regime_blocked=85215, ema_alignment_reject=40847, basic_filters_failed=40089, h1_trend_not_aligned=32881, no_ema_reclaim_close=16362, h1_pullback_not_confirmed=16285, ema_not_tested_prev=15674, body_conviction_fail=13661, rsi_reject=9170, prev_already_below_emas=1652, prev_already_above_emas=1108, no_prev_low_break=1096, insufficient_candles=872, no_prev_high_break=676, momentum_flat=607, momentum_reject=187, missing_fvg_or_orderblock=163, ema21_not_tagged=57
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=296595): breakout_not_found=161149, basic_filters_failed=97209, retest_proximity_failed=29822, volume_spike_missing=4536, ema_alignment_reject=2164, insufficient_candles=1061, missing_fvg_or_orderblock=578, rsi_reject=76
- **EVAL::WHALE_MOMENTUM** (total=297321): momentum_reject=197431, recent_ticks_insufficient=76038, basic_filters_failed=23821, insufficient_candles=31

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 223717 | 59.1% |
| TRENDING_DOWN | 83728 | 22.1% |
| TRENDING_UP | 51476 | 13.6% |
| RANGING | 19546 | 5.2% |
| VOLATILE | 9 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1339**
- Average confidence gap to threshold: **13.33** (samples=1339) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: QUSDT=75, HYPEUSDT=69, PENGUUSDT=60, NMRUSDT=54, CLUSDT=53, ETHUSDT=51, ZECUSDT=49, SAHARAUSDT=48, RECALLUSDT=41, BNBUSDT=39

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 1 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 76 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 1 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 14 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 66 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 141 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 836 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 300 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1011 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 341 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 114 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 736 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 376 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 26 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 382 |
| SR_FLIP_RETEST | filtered | min_confidence | 1014 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 319 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1857 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 50 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 6 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 54.00 | 65.00 | 11.00 | 20.40 | 20.00 | 19.80 | 0.00 | 11.00 |
| BREAKDOWN_SHORT | kept | 76 | 69.78 | 65.00 | -4.78 | 20.41 | 20.00 | 17.47 | 0.00 | 0.04 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 1 | 53.70 | 65.00 | 11.30 | 19.90 | 19.90 | 17.00 | 4.00 | -3.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 14 | 66.68 | 65.00 | -1.68 | 19.41 | 17.03 | 17.00 | 0.00 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 66 | 57.37 | 65.00 | 7.63 | 19.57 | 19.82 | 17.82 | 0.15 | 1.49 |
| DIVERGENCE_CONTINUATION | kept | 141 | 71.23 | 65.00 | -6.23 | 20.65 | 19.89 | 18.07 | 1.74 | -0.66 |
| FAILED_AUCTION_RECLAIM | filtered | 1136 | 59.62 | 65.00 | 5.38 | 20.81 | 18.01 | 18.92 | 4.76 | 2.17 |
| FAILED_AUCTION_RECLAIM | kept | 1011 | 70.44 | 65.00 | -5.44 | 20.72 | 19.45 | 17.34 | 4.47 | 0.02 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.00 | 65.00 | 20.00 | 20.00 | 20.00 | 17.00 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 455 | 50.47 | 65.00 | 14.53 | 20.46 | 19.55 | 15.20 | 2.70 | 9.22 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 736 | 69.24 | 65.00 | -4.24 | 21.35 | 19.64 | 15.20 | 2.34 | 0.03 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.50 | 65.00 | -6.50 | 21.20 | 20.00 | 17.30 | 1.50 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 402 | 53.93 | 65.00 | 11.07 | 21.37 | 19.12 | 16.04 | 0.00 | 2.77 |
| QUIET_COMPRESSION_BREAK | kept | 382 | 72.00 | 65.00 | -7.00 | 20.72 | 19.04 | 15.83 | 0.00 | 0.11 |
| SR_FLIP_RETEST | filtered | 1333 | 53.05 | 65.00 | 11.95 | 20.47 | 19.91 | 15.97 | 1.73 | 8.28 |
| SR_FLIP_RETEST | kept | 1857 | 70.79 | 65.00 | -5.79 | 20.60 | 19.94 | 15.89 | 1.96 | -0.28 |
| TREND_PULLBACK_EMA | filtered | 3 | 52.60 | 65.00 | 12.40 | 21.20 | 19.83 | 17.37 | 5.00 | 3.20 |
| TREND_PULLBACK_EMA | kept | 50 | 74.73 | 65.00 | -9.73 | 19.61 | 19.86 | 18.65 | 5.36 | -2.18 |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 52.23 | 65.00 | 12.77 | 21.70 | 19.90 | 18.63 | 3.00 | 2.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 54.00 | 15.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| BREAKDOWN_SHORT | kept | 76 | 69.78 | 24.89 | 18.00 | 5.96 | 10.05 | 2.60 | 8.31 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 1 | 53.70 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 4.70 | 4.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 14 | 66.68 | 17.57 | 18.00 | 3.43 | 13.79 | 4.82 | 9.07 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 66 | 57.37 | 20.03 | 18.00 | 9.68 | 13.44 | 5.09 | 5.97 | 0.15 |
| DIVERGENCE_CONTINUATION | kept | 141 | 71.23 | 20.40 | 18.00 | 4.26 | 12.53 | 6.10 | 8.49 | 1.74 |
| FAILED_AUCTION_RECLAIM | filtered | 1136 | 59.62 | 24.11 | 14.10 | 6.04 | 9.77 | 8.96 | 7.83 | 4.76 |
| FAILED_AUCTION_RECLAIM | kept | 1011 | 70.44 | 23.59 | 14.52 | 4.32 | 11.04 | 6.06 | 7.09 | 4.47 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.00 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 455 | 50.47 | 22.65 | 14.21 | 6.08 | 12.80 | 5.53 | 6.24 | 2.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 736 | 69.24 | 23.41 | 14.09 | 4.07 | 12.37 | 5.80 | 7.19 | 2.34 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.50 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 10.00 | 1.50 |
| QUIET_COMPRESSION_BREAK | filtered | 402 | 53.93 | 18.69 | 17.35 | 9.73 | 14.16 | 6.71 | 4.28 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 382 | 72.00 | 19.12 | 18.00 | 7.58 | 14.02 | 6.69 | 7.81 | 0.00 |
| SR_FLIP_RETEST | filtered | 1333 | 53.05 | 20.03 | 15.61 | 6.28 | 13.79 | 6.24 | 6.31 | 1.73 |
| SR_FLIP_RETEST | kept | 1857 | 70.79 | 20.70 | 15.33 | 5.95 | 13.80 | 5.90 | 8.44 | 1.96 |
| TREND_PULLBACK_EMA | filtered | 3 | 52.60 | 17.00 | 18.00 | 3.00 | 15.00 | 5.00 | 7.80 | 5.00 |
| TREND_PULLBACK_EMA | kept | 50 | 74.73 | 18.48 | 18.00 | 4.14 | 14.36 | 5.72 | 9.31 | 5.36 |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 52.23 | 25.00 | 14.67 | 3.00 | 12.67 | 4.17 | 7.33 | 3.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 54.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 76 | 69.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 1 | 53.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 14 | 66.68 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 66 | 57.37 | 0.14 | 0.00 | 0.15 | 0.00 | 2.62 | 0.00 | **2.91** |
| DIVERGENCE_CONTINUATION | kept | 141 | 71.23 | 0.06 | 0.00 | 0.17 | 0.00 | 0.15 | 0.00 | **0.38** |
| FAILED_AUCTION_RECLAIM | filtered | 1136 | 59.62 | 0.00 | 0.00 | 0.36 | 0.00 | 1.62 | 0.00 | **1.98** |
| FAILED_AUCTION_RECLAIM | kept | 1011 | 70.44 | 0.00 | 0.00 | 0.02 | 0.00 | 0.01 | 0.00 | **0.03** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 455 | 50.47 | 0.00 | 0.00 | 1.96 | 0.00 | 7.26 | 0.00 | **9.22** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 736 | 69.24 | 0.00 | 0.00 | 0.01 | 0.00 | 0.02 | 0.00 | **0.03** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 402 | 53.93 | 0.00 | 0.00 | 0.11 | 0.00 | 2.47 | 0.00 | **2.58** |
| QUIET_COMPRESSION_BREAK | kept | 382 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.05 | 0.00 | **1.05** |
| SR_FLIP_RETEST | filtered | 1333 | 53.05 | 0.00 | 0.00 | 0.26 | 0.00 | 3.32 | 0.02 | **3.60** |
| SR_FLIP_RETEST | kept | 1857 | 70.79 | 0.00 | 0.00 | 0.03 | 0.00 | 0.08 | 0.01 | **0.12** |
| TREND_PULLBACK_EMA | filtered | 3 | 52.60 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.00 | **3.20** |
| TREND_PULLBACK_EMA | kept | 50 | 74.73 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 52.23 | 0.00 | 0.00 | 1.60 | 0.00 | 0.00 | 0.00 | **1.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=26 (72.2%) | PREMATURE=3 (8.3%) | NEUTRAL=7 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 23 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 1 | 0 | 0 | 0 |
| momentum_loss | 18 | 2 | 3 | 0 |
| regime_shift | 7 | 1 | 4 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 0 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 3 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 2 | 0 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 2 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 14 | 1 | 5 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2147544`
- `Path funnel` emissions: `52`
- `Regime distribution` emissions: `52`
- `QUIET_SCALP_BLOCK` events: `1339`
- `confidence_gate` events: `7674`
- `free_channel_post` events: `277`
- `pre_tp_fire` events: `127`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **127**
- Avg resolved threshold: **0.323%** raw → avg net **+2.53%** @ 10x
- Avg time-to-fire from dispatch: **383s**
- By threshold source: stamped=127

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 51 | 0.273% | +2.03% | 386 | stamped=51 |
| LIQUIDITY_SWEEP_REVERSAL | 31 | 0.408% | +3.38% | 329 | stamped=31 |
| FAILED_AUCTION_RECLAIM | 18 | 0.312% | +2.42% | 429 | stamped=18 |
| DIVERGENCE_CONTINUATION | 16 | 0.371% | +3.00% | 471 | stamped=16 |
| QUIET_COMPRESSION_BREAK | 6 | 0.230% | +1.60% | 306 | stamped=6 |
| TREND_PULLBACK_EMA | 5 | 0.313% | +2.43% | 337 | stamped=5 |
- Top symbols: SUIUSDT=5, ONDOUSDT=5, 1000LUNCUSDT=5, TAOUSDT=4, SKYAIUSDT=4, RECALLUSDT=4, IRYSUSDT=4, DOGEUSDT=4, PHBUSDT=4, AAVEUSDT=4

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **8**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 8 | 14665 | 23065 | 26575 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **277**

| Source | Count |
|---|---:|
| signal_close | 134 |
| pre_tp | 127 |
| regime_shift | 12 |
| signal_highlight | 4 |

- By severity: HIGH=277

## Dependency readiness
- cvd: presence[present=297321] state[populated=297321] buckets[few=18, many=296944, some=359] sources[none] quality[none]
- funding_rate: presence[absent=10958, present=286363] state[empty=10958, populated=286363] buckets[few=286363, none=10958] sources[none] quality[none]
- liquidation_clusters: presence[absent=161914, present=135407] state[empty=161914, populated=135407] buckets[few=112660, none=161914, some=22747] sources[none] quality[none]
- oi_snapshot: presence[absent=5097, present=292224] state[empty=5097, populated=292224] buckets[few=139, many=292017, none=5097, some=68] sources[none] quality[none]
- order_book: presence[absent=67261, present=230060] state[populated=230060, unavailable=67261] buckets[few=230060, none=67261] sources[book_ticker=230060, unavailable=67261] quality[none=67261, top_of_book_only=230060]
- orderblocks: presence[absent=297321] state[empty=297321] buckets[none=297321] sources[not_implemented=297321] quality[none]
- recent_ticks: presence[absent=6597, present=290724] state[empty=6597, populated=290724] buckets[many=290724, none=6597] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.654652118682861` sec
- Median create→first breach: `638.7757461071014` sec
- Median create→terminal: `793.4629790782928` sec
- Median first breach→terminal: `10.65035891532898` sec
- Fast-failure buckets: `{"under_120s": {"count": 11, "pct": 12.9}, "under_180s": {"count": 17, "pct": 20.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 7, "pct": 8.2}}`
- ~3 minute terminal-close behavior: `{"count": 3, "pct": 2.3}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.0 | 0.0 | 0.0 | -0.08 | None | 1177.3182401657104 |
| DIVERGENCE_CONTINUATION | 20 | 20 | 0.0 | 15.0 | 0.0 | 0.1847 | 564.966402053833 | 706.2022129297256 |
| FAILED_AUCTION_RECLAIM | 13 | 13 | 0.0 | 0.0 | 0.0 | 0.4127 | 1033.6360640525818 | 1162.0182495117188 |
| LIQUIDITY_SWEEP_REVERSAL | 28 | 28 | 0.0 | 25.0 | 0.0 | -0.1246 | 642.3266324996948 | 807.8082325458527 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1041 | None | 632.9987709522247 |
| SR_FLIP_RETEST | 64 | 64 | 0.0 | 9.4 | 0.0 | 0.0787 | 607.9799258708954 | 732.6573419570923 |
| TREND_PULLBACK_EMA | 6 | 6 | 0.0 | 16.7 | 0.0 | 0.0688 | 1054.2403820753098 | 1077.0306276082993 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 30234 | 191 | 18212 | 0.0 | 9.4 | 607.9799258708954 | 732.6573419570923 | 12022 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1439 | 12 | 1365 | 0.0 | 16.7 | 1054.2403820753098 | 1077.0306276082993 | 74 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `23`
- Gating Δ: `-7153`
- No-generation Δ: `94657`
- Fast failures Δ: `17`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1847, "current_avg_pnl": 0.1847, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.4127, "current_avg_pnl": 0.4127, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.1246, "current_avg_pnl": -0.1246, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0787, "current_avg_pnl": 0.0787, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.0688, "current_avg_pnl": 0.0688, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 93, "geometry_changed_delta": 0, "geometry_preserved_delta": 3394, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 607.98, "median_terminal_delta_sec": 732.66, "sl_rate_delta": 9.4, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 7, "geometry_changed_delta": 0, "geometry_preserved_delta": 56, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1054.24, "median_terminal_delta_sec": 1077.03, "sl_rate_delta": 16.7, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **VOLUME_SURGE_BREAKOUT**
- Suggested next investigation target: **SR_FLIP_RETEST**
