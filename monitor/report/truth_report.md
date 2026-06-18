# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `354` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 6921 | 6921 | 6684 | 9 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 38114 | 38114 | 34105 | 33 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 163902 | 162736 | 1317 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 152470 | 152481 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 151572 | 143012 | 9447 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 152522 | 145529 | 7393 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 167690 | 167493 | 239 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 163692 | 163700 | 6 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 152931 | 152966 | 14 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 164054 | 164060 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 152489 | 152504 | 15 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 151524 | 151150 | 420 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 147852 | 140051 | 11416 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 146787 | 136559 | 10858 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 147426 | 146321 | 1184 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 163843 | 163527 | 373 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 163708 | 163470 | 371 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 29953 | 29953 | 23767 | 66 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1007 | 1007 | 933 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 44 | 44 | 44 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 51056 | 51056 | 46306 | 97 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 21 | 21 | 18 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 45 | 45 | 45 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 2134 | 2134 | 1994 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 54733 | 54733 | 33282 | 125 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 1 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 5049 | 5049 | 5003 | 9 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1713 | 1713 | 696 | 6 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 10867 | 10867 | 8463 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=162736): breakout_not_found=77067, basic_filters_failed=56637, retest_proximity_failed=21930, volume_spike_missing=4972, ema_alignment_reject=1157, insufficient_candles=494, missing_fvg_or_orderblock=479
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=152481): cls_disabled_merged_into_lsr=152481
- **EVAL::DIVERGENCE_CONTINUATION** (total=143012): basic_filters_failed=48566, cvd_divergence_failed=45850, h1_trend_not_aligned=29343, ema_alignment_reject=11434, regime_blocked=4164, retest_proximity_failed=2429, missing_fvg_or_orderblock=835, cvd_insufficient=203, insufficient_candles=188
- **EVAL::FAILED_AUCTION_RECLAIM** (total=145529): auction_not_detected=50913, basic_filters_failed=46468, reclaim_hold_failed=22961, tail_too_small=18561, regime_blocked=6437, insufficient_candles=188, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=167493): funding_not_extreme=106688, basic_filters_failed=55407, missing_funding_rate=2913, ema_alignment_reject=1625, rsi_reject=599, cvd_divergence_failed=158, momentum_reject=55, insufficient_candles=30, missing_fvg_or_orderblock=18
- **EVAL::LIQUIDATION_REVERSAL** (total=163700): cascade_threshold_not_met=104249, basic_filters_failed=56684, rsi_reject=1199, cvd_divergence_failed=1172, insufficient_candles=290, missing_fvg_or_orderblock=66, volume_spike_missing=34, cvd_insufficient=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=152966): no_ma_cross=101848, basic_filters_failed=48709, ma_cross_cooldown=2095, ma_cross_htf_misaligned=209, ma_cross_htf_unconfirmed=105
- **EVAL::OPENING_RANGE_BREAKOUT** (total=164060): feature_disabled=164060
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=152504): regime_blocked=102393, breakout_not_found=27371, basic_filters_failed=19692, adx_reject=3005, ema_alignment_reject=43
- **EVAL::QUIET_COMPRESSION_BREAK** (total=151150): regime_blocked=56207, compression_not_detected=54928, basic_filters_failed=26757, breakout_not_detected=11993, volume_confirmation_failed=870, insufficient_candles=203, rsi_reject=184, missing_fvg_or_orderblock=8
- **EVAL::SR_FLIP_RETEST** (total=140051): basic_filters_failed=45654, retest_out_of_zone=31058, reclaim_hold_failed=28846, flip_close_not_confirmed=18855, regime_blocked=6376, wick_quality_failed=4555, ema_alignment_reject=2530, insufficient_candles=1252, missing_fvg_or_orderblock=888, rsi_reject=37
- **EVAL::STANDARD** (total=136559): adx_reject=35417, momentum_reject=29374, basic_filters_failed=26901, sweeps_not_detected=19812, macd_reject=13700, ema_alignment_reject=8491, insufficient_candles=1240, invalid_sl_geometry=1155, rsi_reject=447, mtf_reject=22
- **EVAL::TREND_PULLBACK** (total=146321): h1_trend_not_aligned=41445, basic_filters_failed=25079, ema_alignment_reject=22161, h1_pullback_not_confirmed=15169, ema_not_tested_prev=11091, no_ema_reclaim_close=9039, regime_blocked=8934, body_conviction_fail=4786, rsi_reject=4085, insufficient_candles=1240, prev_already_below_emas=957, prev_already_above_emas=797, no_prev_low_break=742, no_prev_high_break=425, momentum_flat=166, ema21_not_tagged=131, missing_fvg_or_orderblock=52, momentum_reject=22
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=163527): breakout_not_found=81001, basic_filters_failed=56636, retest_proximity_failed=19400, volume_spike_missing=4275, ema_alignment_reject=1377, insufficient_candles=494, missing_fvg_or_orderblock=340, rsi_reject=4
- **EVAL::WHALE_MOMENTUM** (total=163470): momentum_reject=123473, recent_ticks_insufficient=25926, basic_filters_failed=14063, insufficient_candles=8

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 359079 | 40.1% |
| QUIET | 199112 | 22.2% |
| TRENDING_DOWN | 163540 | 18.3% |
| TRENDING_UP | 103003 | 11.5% |
| VOLATILE | 70540 | 7.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **602**
- Average confidence gap to threshold: **16.46** (samples=602) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: LITEUSDT=73, MRVLUSDT=55, LINKUSDT=46, SNDKUSDT=43, ETHUSDT=37, AAVEUSDT=37, BTCUSDT=35, BZUSDT=31, DOGEUSDT=30, MSTRUSDT=30

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 53 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 235 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 506 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 981 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 122 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1524 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 770 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 97 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 768 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 20 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 97 |
| SR_FLIP_RETEST | filtered | min_confidence | 4756 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 332 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2103 |
| TREND_PULLBACK_CONTINUATION | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 29 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 144 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 11 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 215 |
| WHALE_MOMENTUM | filtered | min_confidence | 357 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 17 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 29 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 53 | 69.89 | 65.00 | -4.89 | 20.90 | 19.56 | 19.98 | 0.00 | 2.57 |
| DIVERGENCE_CONTINUATION | filtered | 238 | 56.08 | 65.00 | 8.92 | 20.64 | 19.67 | 17.42 | 2.07 | 9.29 |
| DIVERGENCE_CONTINUATION | kept | 506 | 69.89 | 65.00 | -4.89 | 20.36 | 19.75 | 17.89 | 1.87 | -0.81 |
| FAILED_AUCTION_RECLAIM | filtered | 1103 | 53.71 | 65.00 | 11.29 | 21.34 | 18.61 | 20.00 | 4.00 | 3.16 |
| FAILED_AUCTION_RECLAIM | kept | 1524 | 72.75 | 65.00 | -7.75 | 21.47 | 19.27 | 20.00 | 3.91 | 0.17 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.80 | 65.00 | 18.20 | 21.20 | 20.00 | 20.00 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 867 | 52.83 | 65.00 | 12.17 | 20.97 | 19.57 | 17.85 | 2.34 | 4.10 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 768 | 69.80 | 65.00 | -4.80 | 21.32 | 19.58 | 18.19 | 1.93 | 0.30 |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 49.24 | 65.00 | 15.76 | 21.93 | 19.72 | 20.00 | 0.00 | 5.72 |
| QUIET_COMPRESSION_BREAK | kept | 97 | 73.10 | 65.00 | -8.10 | 21.51 | 19.84 | 20.00 | 0.00 | 0.78 |
| SR_FLIP_RETEST | filtered | 5088 | 53.74 | 65.00 | 11.26 | 21.64 | 19.89 | 15.77 | 1.98 | 3.99 |
| SR_FLIP_RETEST | kept | 2103 | 71.86 | 65.00 | -6.86 | 21.13 | 19.89 | 16.36 | 2.12 | -0.33 |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 65.00 | 65.00 | 0.00 | 21.00 | 15.80 | 16.40 | 0.00 | 0.00 |
| TREND_PULLBACK_EMA | kept | 29 | 79.52 | 65.00 | -14.52 | 21.56 | 19.45 | 17.27 | 5.86 | -0.62 |
| VOLUME_SURGE_BREAKOUT | filtered | 155 | 51.89 | 65.00 | 13.11 | 20.17 | 19.65 | 19.96 | 2.18 | 6.78 |
| VOLUME_SURGE_BREAKOUT | kept | 215 | 73.41 | 65.00 | -8.41 | 20.53 | 19.96 | 19.98 | 1.95 | 3.17 |
| WHALE_MOMENTUM | filtered | 374 | 59.18 | 65.00 | 5.82 | 23.70 | 19.35 | 17.00 | 0.00 | 10.07 |
| WHALE_MOMENTUM | kept | 29 | 68.14 | 65.00 | -3.14 | 23.24 | 19.90 | 17.00 | 0.00 | 10.17 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 53 | 69.89 | 22.28 | 14.94 | 13.02 | 12.34 | 5.07 | 4.82 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 238 | 56.08 | 22.55 | 11.36 | 7.30 | 13.08 | 5.07 | 8.00 | 2.07 |
| DIVERGENCE_CONTINUATION | kept | 506 | 69.89 | 23.55 | 13.61 | 5.56 | 11.96 | 6.46 | 7.57 | 1.87 |
| FAILED_AUCTION_RECLAIM | filtered | 1103 | 53.71 | 21.72 | 16.98 | 5.25 | 11.51 | 6.22 | 4.65 | 4.00 |
| FAILED_AUCTION_RECLAIM | kept | 1524 | 72.75 | 22.65 | 16.10 | 4.71 | 12.12 | 6.43 | 7.02 | 3.91 |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.80 | 25.00 | 8.00 | 3.00 | 14.00 | 8.50 | 8.30 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 867 | 52.83 | 22.38 | 14.40 | 6.28 | 12.83 | 5.92 | 5.08 | 2.34 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 768 | 69.80 | 22.77 | 14.72 | 4.89 | 13.01 | 5.89 | 6.89 | 1.93 |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 49.24 | 17.80 | 18.00 | 11.70 | 14.00 | 6.05 | 2.57 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 97 | 73.10 | 19.97 | 14.29 | 10.21 | 13.94 | 8.50 | 6.97 | 0.00 |
| SR_FLIP_RETEST | filtered | 5088 | 53.74 | 21.47 | 17.35 | 5.27 | 13.81 | 6.05 | 5.52 | 1.98 |
| SR_FLIP_RETEST | kept | 2103 | 71.86 | 22.15 | 16.54 | 4.66 | 14.11 | 5.81 | 7.68 | 2.12 |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 65.00 | 17.00 | 8.00 | 9.00 | 11.00 | 10.00 | 10.00 | 0.00 |
| TREND_PULLBACK_EMA | kept | 29 | 79.52 | 19.21 | 18.00 | 6.83 | 14.21 | 6.57 | 8.91 | 5.86 |
| VOLUME_SURGE_BREAKOUT | filtered | 155 | 51.89 | 22.57 | 15.70 | 9.00 | 13.54 | 5.96 | 4.42 | 2.18 |
| VOLUME_SURGE_BREAKOUT | kept | 215 | 73.41 | 21.54 | 13.40 | 12.17 | 13.91 | 6.38 | 7.38 | 1.95 |
| WHALE_MOMENTUM | filtered | 374 | 59.18 | 20.43 | 16.05 | 8.04 | 12.63 | 6.31 | 5.80 | 0.00 |
| WHALE_MOMENTUM | kept | 29 | 68.14 | 24.72 | 18.00 | 9.83 | 13.62 | 5.41 | 6.72 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 53 | 69.89 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 238 | 56.08 | 0.00 | 0.00 | 2.60 | 0.00 | 4.10 | 0.00 | 0.00 | 0.00 | **6.70** |
| DIVERGENCE_CONTINUATION | kept | 506 | 69.89 | 0.00 | 0.00 | 0.03 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.05** |
| FAILED_AUCTION_RECLAIM | filtered | 1103 | 53.71 | 0.00 | 0.00 | 0.60 | 0.00 | 1.62 | 0.00 | 0.00 | 0.00 | **2.22** |
| FAILED_AUCTION_RECLAIM | kept | 1524 | 72.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.01** |
| FUNDING_EXTREME_SIGNAL | filtered | 1 | 46.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 867 | 52.83 | 0.00 | 0.00 | 0.85 | 0.00 | 3.15 | 0.00 | 0.00 | 0.00 | **4.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 768 | 69.80 | 0.00 | 0.00 | 0.13 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **0.22** |
| QUIET_COMPRESSION_BREAK | filtered | 20 | 49.24 | 0.00 | 0.00 | 0.00 | 0.00 | 1.07 | 0.00 | 0.00 | 2.70 | **3.77** |
| QUIET_COMPRESSION_BREAK | kept | 97 | 73.10 | 0.00 | 0.00 | 0.00 | 0.00 | 2.57 | 0.00 | 0.00 | 0.00 | **2.57** |
| SR_FLIP_RETEST | filtered | 5088 | 53.74 | 0.00 | 0.00 | 1.27 | 0.00 | 1.63 | 0.00 | 0.00 | 0.46 | **3.36** |
| SR_FLIP_RETEST | kept | 2103 | 71.86 | 0.00 | 0.00 | 0.01 | 0.00 | 0.47 | 0.00 | 0.00 | 0.08 | **0.56** |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 29 | 79.52 | 0.00 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.17** |
| VOLUME_SURGE_BREAKOUT | filtered | 155 | 51.89 | 0.00 | 0.00 | 1.91 | 0.00 | 1.93 | 0.00 | 0.00 | 0.30 | **4.14** |
| VOLUME_SURGE_BREAKOUT | kept | 215 | 73.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.13** |
| WHALE_MOMENTUM | filtered | 374 | 59.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | kept | 29 | 68.14 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=82 (76.6%) | PREMATURE=15 (14.0%) | NEUTRAL=10 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 67 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 25 | 3 | 0 | 0 |
| ema_crossover | 2 | 1 | 1 | 0 |
| momentum_loss | 47 | 6 | 4 | 0 |
| trailing_invalidation | 8 | 5 | 5 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 0 | 3 | 0 |
| DIVERGENCE_CONTINUATION | 14 | 3 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 13 | 2 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 17 | 2 | 3 | 0 |
| SR_FLIP_RETEST | 32 | 8 | 3 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 25 | 3 | 0 | 8.8 | 5.6 | +0.12 | **KEEP** — net-helping: avg +0.12R/kill across 28 kills (saved 8.8R vs missed 5.6R) |
| ema_crossover | 2 | 1 | 1 | 1.1 | 2.0 | -0.21 | **INSUFFICIENT_SAMPLE** — only 4 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 47 | 6 | 4 | 31.0 | 9.3 | +0.38 | **KEEP** — net-helping: avg +0.38R/kill across 57 kills (saved 31.0R vs missed 9.3R) |
| trailing_invalidation | 8 | 5 | 5 | 7.9 | 7.2 | +0.04 | **INSUFFICIENT_SAMPLE** — only 18 classified kills (need >= 20); let data accumulate before tuning |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `3998320`
- `Path funnel` emissions: `125`
- `Regime distribution` emissions: `125`
- `QUIET_SCALP_BLOCK` events: `602`
- `confidence_gate` events: `13171`
- `free_channel_post` events: `113`
- `pre_tp_fire` events: `54`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **54**
- Avg resolved threshold: **0.495%** raw → avg net **+4.25%** @ 10x
- Avg time-to-fire from dispatch: **250s**
- By threshold source: stamped=54

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 21 | 0.499% | +4.29% | 292 | stamped=21 |
| LIQUIDITY_SWEEP_REVERSAL | 12 | 0.493% | +4.23% | 344 | stamped=12 |
| DIVERGENCE_CONTINUATION | 9 | 0.428% | +3.58% | 130 | stamped=9 |
| FAILED_AUCTION_RECLAIM | 8 | 0.335% | +2.65% | 111 | stamped=8 |
| TREND_PULLBACK_EMA | 3 | 0.626% | +5.55% | 366 | stamped=3 |
| TREND_PULLBACK_CONTINUATION | 1 | 1.926% | +18.56% | 125 | stamped=1 |
- Top symbols: AEROUSDT=8, XPLUSDT=6, SNDKUSDT=5, PORTALUSDT=4, TIAUSDT=4, EVAAUSDT=4, BRUSDT=3, STGUSDT=2, 1000PEPEUSDT=2, ALLOUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 4759 | 4759 | 4759 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **113**

| Source | Count |
|---|---:|
| pre_tp | 54 |
| signal_close | 53 |
| regime_shift | 6 |

- By severity: HIGH=113

## Dependency readiness
- cvd: presence[absent=3, present=720304] state[empty=3, populated=720304] buckets[few=531, many=711817, none=3, some=7956] sources[none] quality[none]
- funding_rate: presence[absent=7502, present=712805] state[empty=7502, populated=712805] buckets[few=712805, none=7502] sources[none] quality[none]
- liquidation_clusters: presence[absent=343262, present=377045] state[empty=343262, populated=377045] buckets[few=286394, none=343262, some=90651] sources[none] quality[none]
- oi_snapshot: presence[absent=3019, present=717288] state[empty=3019, populated=717288] buckets[few=253, many=715927, none=3019, some=1108] sources[none] quality[none]
- order_book: presence[absent=185822, present=534485] state[populated=534485, unavailable=185822] buckets[few=534485, none=185822] sources[book_ticker=534485, unavailable=185822] quality[none=185822, top_of_book_only=534485]
- orderblocks: presence[absent=720307] state[empty=720307] buckets[none=720307] sources[not_implemented=720307] quality[none]
- recent_ticks: presence[absent=41021, present=679286] state[empty=41021, populated=679286] buckets[many=679286, none=41021] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.644605398178101` sec
- Median create→first breach: `419.5326979160309` sec
- Median create→terminal: `408.8865394592285` sec
- Median first breach→terminal: `1.2191030979156494` sec
- Fast-failure buckets: `{"under_120s": {"count": 14, "pct": 26.4}, "under_180s": {"count": 16, "pct": 30.2}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 8, "pct": 15.1}}`
- ~3 minute terminal-close behavior: `{"count": 8, "pct": 9.3}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 5 | 5 | 0.0 | 0.0 | 0.0 | 0.0 | -0.1497 | None | 665.3882739543915 |
| DIVERGENCE_CONTINUATION | 13 | 13 | 0.0 | 0.0 | 0.0 | 69.2 | 0.1319 | 224.79163193702698 | 226.01073503494263 |
| FAILED_AUCTION_RECLAIM | 12 | 12 | 0.0 | 8.3 | 0.0 | 66.7 | -0.0275 | 354.6084705591202 | 823.8494745492935 |
| LIQUIDITY_SWEEP_REVERSAL | 22 | 22 | 0.0 | 4.5 | 0.0 | 54.5 | 0.0031 | 682.9693419933319 | 366.574250459671 |
| SR_FLIP_RETEST | 29 | 29 | 0.0 | 10.3 | 0.0 | 72.4 | 0.0575 | 403.45189595222473 | 379.71659302711487 |
| TREND_PULLBACK_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 100.0 | 0.9632 | 604.4319219589233 | 604.9377450942993 |
| TREND_PULLBACK_EMA | 3 | 3 | 0.0 | 0.0 | 0.0 | 100.0 | -0.0965 | 1008.335265994072 | 653.6095759868622 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.9586 | 577.1213998794556 | 611.2133808135986 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 54733 | 125 | 33282 | 0.0 | 10.3 | 403.45189595222473 | 379.71659302711487 | 21451 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 5049 | 9 | 5003 | 0.0 | 0.0 | 1008.335265994072 | 653.6095759868622 | 46 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-87`
- Gating Δ: `27368`
- No-generation Δ: `-388258`
- Fast failures Δ: `9`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.5706, "current_avg_pnl": -0.1497, "current_win_rate": 0.0, "previous_avg_pnl": 0.4209, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.2111, "current_avg_pnl": 0.1319, "current_win_rate": 0.0, "previous_avg_pnl": -0.0792, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.3233, "current_avg_pnl": -0.0275, "current_win_rate": 0.0, "previous_avg_pnl": 0.2958, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0658, "current_avg_pnl": 0.0031, "current_win_rate": 0.0, "previous_avg_pnl": -0.0627, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0704, "current_avg_pnl": 0.0575, "current_win_rate": 0.0, "previous_avg_pnl": -0.0129, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.2678, "current_avg_pnl": -0.0965, "current_win_rate": 0.0, "previous_avg_pnl": -0.3643, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -74, "geometry_changed_delta": 0, "geometry_preserved_delta": -2356, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 44.72, "median_terminal_delta_sec": 22.22, "sl_rate_delta": -3.7, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": -329, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1008.34, "median_terminal_delta_sec": -240.26, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
