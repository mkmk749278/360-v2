# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, DIVERGENCE_CONTINUATION, LIQUIDITY_SWEEP_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `15` sec (warning=False)
- Latest performance record age: `644` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 863 | 863 | 734 | 2 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 192 | 192 | 169 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 12233 | 12233 | 11739 | 38 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 300096 | 299233 | 863 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 276724 | 276532 | 192 | 0 | 0 | 0 | low-sample (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 276724 | 264491 | 12233 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 276724 | 261071 | 15653 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 300096 | 299938 | 158 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 300096 | 300069 | 27 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 276724 | 276711 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 300096 | 300096 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 276724 | 276695 | 29 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 276724 | 271272 | 5452 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 276724 | 245899 | 30825 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 276724 | 262409 | 14315 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 276724 | 275474 | 1250 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 300096 | 299419 | 677 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 300096 | 300096 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 15653 | 15653 | 11007 | 89 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 158 | 158 | 135 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 27 | 27 | 27 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14315 | 14315 | 11273 | 140 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 11 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 29 | 29 | 29 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 5452 | 5452 | 4149 | 49 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 30825 | 30825 | 19072 | 180 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 1250 | 1250 | 1179 | 10 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 677 | 677 | 658 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=299233): breakout_not_found=146024, basic_filters_failed=98648, retest_proximity_failed=42233, volume_spike_missing=7926, insufficient_candles=2157, ema_alignment_reject=1565, missing_fvg_or_orderblock=675, rsi_reject=5
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=276532): cls_disabled_merged_into_lsr=215155, regime_blocked=36352, sweeps_not_detected=10907, basic_filters_failed=6238, ema_alignment_reject=3146, adx_reject=2919, momentum_reject=1175, reclaim_confirmation_failed=418, insufficient_candles=222
- **EVAL::DIVERGENCE_CONTINUATION** (total=264491): regime_blocked=105917, cvd_divergence_failed=69758, basic_filters_failed=50951, h1_trend_not_aligned=18912, ema_alignment_reject=15405, retest_proximity_failed=1757, missing_fvg_or_orderblock=1569, insufficient_candles=222
- **EVAL::FAILED_AUCTION_RECLAIM** (total=261071): auction_not_detected=95587, basic_filters_failed=88070, reclaim_hold_failed=50249, tail_too_small=26611, insufficient_candles=546, regime_blocked=8
- **EVAL::FUNDING_EXTREME** (total=299938): funding_not_extreme=191150, basic_filters_failed=95836, missing_funding_rate=9219, ema_alignment_reject=2222, rsi_reject=837, momentum_reject=217, cvd_divergence_failed=190, insufficient_candles=187, missing_fvg_or_orderblock=80
- **EVAL::LIQUIDATION_REVERSAL** (total=300069): cascade_threshold_not_met=197160, basic_filters_failed=99021, insufficient_candles=1371, rsi_reject=1206, cvd_divergence_failed=1153, missing_fvg_or_orderblock=86, volume_spike_missing=72
- **EVAL::MA_CROSS_TREND_SHIFT** (total=276711): no_ma_cross=186124, basic_filters_failed=88164, ma_cross_cooldown=2423
- **EVAL::OPENING_RANGE_BREAKOUT** (total=300096): feature_disabled=300096
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=276695): regime_blocked=184374, breakout_not_found=45738, basic_filters_failed=21725, ema_alignment_reject=14219, adx_reject=10417, insufficient_candles=222
- **EVAL::QUIET_COMPRESSION_BREAK** (total=271272): regime_blocked=92358, basic_filters_failed=66343, compression_not_detected=60113, breakout_not_detected=50470, rsi_reject=848, volume_confirmation_failed=446, missing_fvg_or_orderblock=351, insufficient_candles=343
- **EVAL::SR_FLIP_RETEST** (total=245899): basic_filters_failed=87403, reclaim_hold_failed=55395, flip_close_not_confirmed=46924, retest_out_of_zone=37686, wick_quality_failed=12220, ema_alignment_reject=2501, insufficient_candles=1926, missing_fvg_or_orderblock=1786, rsi_reject=50, regime_blocked=8
- **EVAL::STANDARD** (total=262409): momentum_reject=67152, basic_filters_failed=58358, adx_reject=50335, sweeps_not_detected=45530, macd_reject=25895, ema_alignment_reject=11887, insufficient_candles=1755, invalid_sl_geometry=1021, rsi_reject=476
- **EVAL::TREND_PULLBACK** (total=275474): regime_blocked=103739, basic_filters_failed=36413, ema_alignment_reject=34237, h1_trend_not_aligned=28971, ema_not_tested_prev=15887, no_ema_reclaim_close=14943, h1_pullback_not_confirmed=13596, body_conviction_fail=13172, rsi_reject=9264, no_prev_low_break=1034, prev_already_above_emas=1011, prev_already_below_emas=995, insufficient_candles=872, no_prev_high_break=520, momentum_flat=447, momentum_reject=180, missing_fvg_or_orderblock=165, ema21_not_tagged=28
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=299419): breakout_not_found=161322, basic_filters_failed=98648, retest_proximity_failed=30112, volume_spike_missing=4395, ema_alignment_reject=2204, insufficient_candles=2157, missing_fvg_or_orderblock=510, rsi_reject=71
- **EVAL::WHALE_MOMENTUM** (total=300096): momentum_reject=202533, recent_ticks_insufficient=73511, basic_filters_failed=24021, insufficient_candles=31

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 233662 | 61.5% |
| TRENDING_DOWN | 90196 | 23.8% |
| TRENDING_UP | 39346 | 10.4% |
| RANGING | 16463 | 4.3% |
| VOLATILE | 9 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1325**
- Average confidence gap to threshold: **14.09** (samples=1325) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HYPEUSDT=76, PENGUUSDT=57, ETHUSDT=56, NMRUSDT=54, CLUSDT=52, SAHARAUSDT=51, ZECUSDT=49, BNBUSDT=44, RECALLUSDT=39, BTCUSDT=38

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 1 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 69 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 3 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 16 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 50 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 123 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 630 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 274 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 912 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 341 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 72 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 649 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 403 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 27 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 387 |
| SR_FLIP_RETEST | filtered | min_confidence | 944 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 304 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1789 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 50 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 54.00 | 65.00 | 11.00 | 20.40 | 20.00 | 19.80 | 0.00 | 11.00 |
| BREAKDOWN_SHORT | kept | 69 | 69.78 | 65.00 | -4.78 | 20.41 | 20.00 | 17.47 | 0.00 | 0.04 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 3 | 59.90 | 65.00 | 5.10 | 20.50 | 19.97 | 17.00 | 2.67 | 1.67 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 16 | 66.84 | 65.00 | -1.84 | 19.44 | 17.40 | 17.00 | 0.12 | -0.19 |
| DIVERGENCE_CONTINUATION | filtered | 50 | 57.02 | 65.00 | 7.98 | 19.58 | 19.77 | 17.21 | 0.30 | 0.44 |
| DIVERGENCE_CONTINUATION | kept | 123 | 71.45 | 65.00 | -6.45 | 20.52 | 19.86 | 18.29 | 1.46 | -0.57 |
| FAILED_AUCTION_RECLAIM | filtered | 904 | 58.06 | 65.00 | 6.94 | 20.75 | 18.16 | 18.33 | 4.67 | 3.20 |
| FAILED_AUCTION_RECLAIM | kept | 912 | 70.40 | 65.00 | -5.40 | 20.71 | 19.49 | 16.75 | 4.36 | 0.02 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.00 | 65.00 | 20.00 | 20.00 | 20.00 | 17.00 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 413 | 51.05 | 65.00 | 13.95 | 20.57 | 19.52 | 15.20 | 2.62 | 9.27 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 649 | 69.03 | 65.00 | -4.03 | 21.16 | 19.79 | 15.20 | 2.30 | 0.02 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.50 | 65.00 | -6.50 | 21.20 | 20.00 | 17.30 | 1.50 | -3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 430 | 53.51 | 65.00 | 11.49 | 21.41 | 19.05 | 16.02 | 0.00 | 3.17 |
| QUIET_COMPRESSION_BREAK | kept | 387 | 72.00 | 65.00 | -7.00 | 20.72 | 19.04 | 15.83 | 0.00 | 0.11 |
| SR_FLIP_RETEST | filtered | 1248 | 53.02 | 65.00 | 11.98 | 20.39 | 19.90 | 16.02 | 1.66 | 8.22 |
| SR_FLIP_RETEST | kept | 1789 | 70.85 | 65.00 | -5.85 | 20.51 | 19.94 | 15.80 | 1.96 | -0.34 |
| TREND_PULLBACK_EMA | filtered | 3 | 52.60 | 65.00 | 12.40 | 21.20 | 19.83 | 17.37 | 5.00 | 3.20 |
| TREND_PULLBACK_EMA | kept | 50 | 75.26 | 65.00 | -10.26 | 19.65 | 19.88 | 18.61 | 5.39 | -1.94 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 51.75 | 65.00 | 13.25 | 21.95 | 19.85 | 17.95 | 3.00 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 54.00 | 15.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| BREAKDOWN_SHORT | kept | 69 | 69.78 | 24.88 | 18.00 | 5.96 | 10.06 | 2.61 | 8.31 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 3 | 59.90 | 16.33 | 18.00 | 6.00 | 12.00 | 5.00 | 7.57 | 2.67 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 16 | 66.84 | 17.50 | 18.00 | 3.38 | 14.00 | 4.84 | 9.00 | 0.12 |
| DIVERGENCE_CONTINUATION | filtered | 50 | 57.02 | 20.36 | 18.00 | 8.10 | 13.26 | 5.12 | 5.64 | 0.30 |
| DIVERGENCE_CONTINUATION | kept | 123 | 71.45 | 20.58 | 18.00 | 4.34 | 12.49 | 6.21 | 8.58 | 1.46 |
| FAILED_AUCTION_RECLAIM | filtered | 904 | 58.06 | 23.75 | 14.13 | 6.05 | 10.06 | 8.56 | 7.47 | 4.67 |
| FAILED_AUCTION_RECLAIM | kept | 912 | 70.40 | 23.36 | 14.21 | 4.39 | 11.27 | 5.94 | 7.13 | 4.36 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.00 | 25.00 | 8.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 413 | 51.05 | 23.05 | 14.23 | 6.41 | 12.47 | 5.66 | 6.01 | 2.62 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 649 | 69.03 | 23.38 | 14.10 | 4.11 | 12.36 | 5.71 | 7.09 | 2.30 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.50 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 10.00 | 1.50 |
| QUIET_COMPRESSION_BREAK | filtered | 430 | 53.51 | 18.71 | 17.37 | 9.73 | 14.16 | 6.76 | 4.23 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 387 | 72.00 | 19.15 | 18.00 | 7.54 | 14.02 | 6.69 | 7.80 | 0.00 |
| SR_FLIP_RETEST | filtered | 1248 | 53.02 | 19.79 | 15.56 | 6.55 | 13.79 | 6.20 | 6.37 | 1.66 |
| SR_FLIP_RETEST | kept | 1789 | 70.85 | 20.76 | 15.45 | 5.88 | 13.70 | 5.92 | 8.47 | 1.96 |
| TREND_PULLBACK_EMA | filtered | 3 | 52.60 | 17.00 | 18.00 | 3.00 | 15.00 | 5.00 | 7.80 | 5.00 |
| TREND_PULLBACK_EMA | kept | 50 | 75.26 | 18.94 | 18.00 | 4.32 | 14.30 | 5.62 | 9.33 | 5.39 |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 51.75 | 25.00 | 13.00 | 3.00 | 14.00 | 3.75 | 8.00 | 3.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 1 | 54.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 69 | 69.78 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 3 | 59.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 16 | 66.84 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 50 | 57.02 | 0.00 | 0.00 | 0.19 | 0.00 | 1.15 | 0.00 | **1.34** |
| DIVERGENCE_CONTINUATION | kept | 123 | 71.45 | 0.00 | 0.00 | 0.20 | 0.00 | 0.12 | 0.00 | **0.32** |
| FAILED_AUCTION_RECLAIM | filtered | 904 | 58.06 | 0.00 | 0.00 | 0.63 | 0.00 | 2.33 | 0.00 | **2.96** |
| FAILED_AUCTION_RECLAIM | kept | 912 | 70.40 | 0.00 | 0.00 | 0.02 | 0.00 | 0.02 | 0.00 | **0.04** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 413 | 51.05 | 0.00 | 0.00 | 1.12 | 0.00 | 8.16 | 0.00 | **9.28** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 649 | 69.03 | 0.00 | 0.00 | 0.01 | 0.00 | 0.02 | 0.00 | **0.03** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 71.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 430 | 53.51 | 0.00 | 0.00 | 0.33 | 0.00 | 2.48 | 0.00 | **2.81** |
| QUIET_COMPRESSION_BREAK | kept | 387 | 72.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.04 | 0.00 | **1.04** |
| SR_FLIP_RETEST | filtered | 1248 | 53.02 | 0.00 | 0.00 | 0.19 | 0.00 | 3.56 | 0.02 | **3.77** |
| SR_FLIP_RETEST | kept | 1789 | 70.85 | 0.00 | 0.00 | 0.03 | 0.00 | 0.08 | 0.01 | **0.12** |
| TREND_PULLBACK_EMA | filtered | 3 | 52.60 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.00 | **3.20** |
| TREND_PULLBACK_EMA | kept | 50 | 75.26 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| VOLUME_SURGE_BREAKOUT | filtered | 4 | 51.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=24 (72.7%) | PREMATURE=2 (6.1%) | NEUTRAL=7 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 22 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 1 | 0 | 0 | 0 |
| momentum_loss | 17 | 2 | 3 | 0 |
| regime_shift | 6 | 0 | 4 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 0 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 2 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 2 | 0 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 1 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 13 | 1 | 5 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2138738`
- `Path funnel` emissions: `52`
- `Regime distribution` emissions: `52`
- `QUIET_SCALP_BLOCK` events: `1325`
- `confidence_gate` events: `7055`
- `free_channel_post` events: `266`
- `pre_tp_fire` events: `123`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **123**
- Avg resolved threshold: **0.326%** raw → avg net **+2.56%** @ 10x
- Avg time-to-fire from dispatch: **378s**
- By threshold source: stamped=123

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 49 | 0.275% | +2.05% | 384 | stamped=49 |
| LIQUIDITY_SWEEP_REVERSAL | 33 | 0.412% | +3.42% | 318 | stamped=33 |
| FAILED_AUCTION_RECLAIM | 16 | 0.323% | +2.53% | 465 | stamped=16 |
| DIVERGENCE_CONTINUATION | 12 | 0.379% | +3.09% | 415 | stamped=12 |
| QUIET_COMPRESSION_BREAK | 9 | 0.240% | +1.70% | 369 | stamped=9 |
| TREND_PULLBACK_EMA | 4 | 0.280% | +2.10% | 372 | stamped=4 |
- Top symbols: GUAUSDT=5, TAOUSDT=5, SUIUSDT=5, 1000LUNCUSDT=5, RIVERUSDT=4, IRYSUSDT=4, ONDOUSDT=4, PHBUSDT=4, LINKUSDT=4, APEUSDT=4

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **6**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 6 | 14665 | 23065 | 26575 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **266**

| Source | Count |
|---|---:|
| signal_close | 127 |
| pre_tp | 123 |
| regime_shift | 13 |
| signal_highlight | 3 |

- By severity: HIGH=266

## Dependency readiness
- cvd: presence[present=300096] state[populated=300096] buckets[few=18, many=299719, some=359] sources[none] quality[none]
- funding_rate: presence[absent=9219, present=290877] state[empty=9219, populated=290877] buckets[few=290877, none=9219] sources[none] quality[none]
- liquidation_clusters: presence[absent=161162, present=138934] state[empty=161162, populated=138934] buckets[few=115398, none=161162, some=23536] sources[none] quality[none]
- oi_snapshot: presence[absent=3358, present=296738] state[empty=3358, populated=296738] buckets[few=139, many=296129, none=3358, some=470] sources[none] quality[none]
- order_book: presence[absent=68094, present=232002] state[populated=232002, unavailable=68094] buckets[few=232002, none=68094] sources[book_ticker=232002, unavailable=68094] quality[none=68094, top_of_book_only=232002]
- orderblocks: presence[absent=300096] state[empty=300096] buckets[none=300096] sources[not_implemented=300096] quality[none]
- recent_ticks: presence[absent=7311, present=292785] state[empty=7311, populated=292785] buckets[many=292785, none=7311] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `6.654652118682861` sec
- Median create→first breach: `638.1869665384293` sec
- Median create→terminal: `822.1534860134125` sec
- Median first breach→terminal: `11.89597201347351` sec
- Fast-failure buckets: `{"under_120s": {"count": 9, "pct": 13.2}, "under_180s": {"count": 14, "pct": 20.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 5, "pct": 7.4}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 1.9}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.0 | 0.0 | 0.0 | -0.08 | None | 1177.3182401657104 |
| DIVERGENCE_CONTINUATION | 12 | 12 | 0.0 | 8.3 | 0.0 | 0.1848 | 443.78123903274536 | 608.2265884876251 |
| FAILED_AUCTION_RECLAIM | 10 | 10 | 0.0 | 0.0 | 0.0 | 0.4545 | 1197.4665582180023 | 1204.534749031067 |
| LIQUIDITY_SWEEP_REVERSAL | 25 | 25 | 0.0 | 24.0 | 0.0 | -0.103 | 550.8404929637909 | 822.1534860134125 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1041 | None | 632.9987709522247 |
| SR_FLIP_RETEST | 54 | 54 | 0.0 | 7.4 | 0.0 | 0.0314 | 622.7890564203262 | 741.0450685024261 |
| TREND_PULLBACK_EMA | 5 | 5 | 0.0 | 20.0 | 0.0 | 0.0382 | 1060.1407511234283 | 1105.3304431438446 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 30825 | 180 | 19072 | 0.0 | 7.4 | 622.7890564203262 | 741.0450685024261 | 11753 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 1250 | 10 | 1179 | 0.0 | 20.0 | 1060.1407511234283 | 1105.3304431438446 | 71 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-10`
- Gating Δ: `-5387`
- No-generation Δ: `-40162`
- Fast failures Δ: `14`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1848, "current_avg_pnl": 0.1848, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.4545, "current_avg_pnl": 0.4545, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.103, "current_avg_pnl": -0.103, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0314, "current_avg_pnl": 0.0314, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.0382, "current_avg_pnl": 0.0382, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 78, "geometry_changed_delta": 0, "geometry_preserved_delta": 1899, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 622.79, "median_terminal_delta_sec": 741.05, "sl_rate_delta": 7.4, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 57, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1060.14, "median_terminal_delta_sec": 1105.33, "sl_rate_delta": 20.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **VOLUME_SURGE_BREAKOUT**
- Suggested next investigation target: **SR_FLIP_RETEST**
