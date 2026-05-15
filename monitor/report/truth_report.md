# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `10` sec (warning=False)
- Latest performance record age: `980` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 759 | 759 | 747 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 26712 | 26712 | 14105 | 7 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 45260 | 45260 | 29737 | 31 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 561620 | 560861 | 759 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 484527 | 457815 | 26712 | 0 | 0 | 0 | low-sample (sweeps_not_detected) |
| EVAL::DIVERGENCE_CONTINUATION | 484527 | 439267 | 45260 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 484527 | 442438 | 42089 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 561620 | 558723 | 2897 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 561620 | 561605 | 15 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 484527 | 484504 | 23 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 561620 | 561620 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 484527 | 484526 | 1 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 484527 | 481375 | 3152 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 484527 | 435255 | 49272 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 484527 | 469398 | 15129 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 484527 | 483851 | 676 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 561620 | 560492 | 1128 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 561620 | 561620 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 42089 | 42089 | 33448 | 111 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2897 | 2897 | 2888 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 15 | 15 | 15 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15129 | 15129 | 12434 | 91 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 23 | 23 | 19 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 3152 | 3152 | 2525 | 78 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 49272 | 49272 | 16827 | 151 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 676 | 676 | 622 | 5 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1128 | 1128 | 839 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=560861): breakout_not_found=300741, basic_filters_failed=145589, retest_proximity_failed=95146, volume_spike_missing=10208, ema_alignment_reject=7559, insufficient_candles=1224, missing_fvg_or_orderblock=294, rsi_reject=100
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=457815): sweeps_not_detected=128222, ema_alignment_reject=112790, basic_filters_failed=108945, regime_blocked=73456, adx_reject=18060, momentum_reject=12458, reclaim_confirmation_failed=3113, rsi_reject=771
- **EVAL::DIVERGENCE_CONTINUATION** (total=439267): cvd_divergence_failed=208123, basic_filters_failed=108945, regime_blocked=73456, ema_alignment_reject=23610, retest_proximity_failed=20684, missing_cvd=3594, missing_fvg_or_orderblock=855
- **EVAL::FAILED_AUCTION_RECLAIM** (total=442438): auction_not_detected=184132, basic_filters_failed=127008, reclaim_hold_failed=86606, tail_too_small=44655, regime_blocked=29, rsi_reject=8
- **EVAL::FUNDING_EXTREME** (total=558723): funding_not_extreme=398950, basic_filters_failed=141401, missing_funding_rate=14054, ema_alignment_reject=2148, rsi_reject=1789, momentum_reject=181, cvd_divergence_failed=128, insufficient_candles=61, missing_fvg_or_orderblock=11
- **EVAL::LIQUIDATION_REVERSAL** (total=561605): cascade_threshold_not_met=406826, basic_filters_failed=145715, cvd_divergence_failed=7030, rsi_reject=1101, insufficient_candles=852, missing_fvg_or_orderblock=51, volume_spike_missing=30
- **EVAL::MA_CROSS_TREND_SHIFT** (total=484504): no_ma_cross=354009, basic_filters_failed=127008, ma_cross_cooldown=3487
- **EVAL::OPENING_RANGE_BREAKOUT** (total=561620): feature_disabled=561620
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=484526): breakout_not_found=171275, ema_alignment_reject=112790, basic_filters_failed=108945, regime_blocked=73456, adx_reject=18060
- **EVAL::QUIET_COMPRESSION_BREAK** (total=481375): regime_blocked=411100, breakout_not_detected=36189, basic_filters_failed=18063, compression_not_detected=15658, rsi_reject=223, missing_fvg_or_orderblock=123, macd_reject=19
- **EVAL::SR_FLIP_RETEST** (total=435255): basic_filters_failed=127008, flip_close_not_confirmed=117297, retest_out_of_zone=112424, reclaim_hold_failed=56011, ema_alignment_reject=10086, wick_quality_failed=6262, rsi_reject=5765, missing_fvg_or_orderblock=373, regime_blocked=29
- **EVAL::STANDARD** (total=469398): momentum_reject=159948, basic_filters_failed=100800, ema_alignment_reject=69993, adx_reject=63091, sweeps_not_detected=58855, macd_reject=10167, rsi_reject=6186, invalid_sl_geometry=316, htf_ema_reject=27, mtf_reject=15
- **EVAL::TREND_PULLBACK** (total=483851): ema_alignment_reject=129889, basic_filters_failed=108945, ema_not_tested_prev=98104, regime_blocked=73456, no_ema_reclaim_close=37435, body_conviction_fail=19208, rsi_reject=14504, prev_already_above_emas=1129, no_prev_high_break=350, prev_already_below_emas=293, no_prev_low_break=253, momentum_flat=144, ema21_not_tagged=67, missing_fvg_or_orderblock=44, momentum_reject=30
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=560492): breakout_not_found=273705, basic_filters_failed=145589, retest_proximity_failed=103174, volume_spike_missing=34676, ema_alignment_reject=1743, insufficient_candles=1224, missing_fvg_or_orderblock=364, rsi_reject=17
- **EVAL::WHALE_MOMENTUM** (total=561620): momentum_reject=377246, recent_ticks_insufficient=141378, basic_filters_failed=42996

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 331563 | 48.7% |
| TRENDING_DOWN | 244622 | 35.9% |
| QUIET | 87845 | 12.9% |
| RANGING | 16474 | 2.4% |
| VOLATILE | 35 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **466**
- Average confidence gap to threshold: **13.72** (samples=466) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SUIUSDT=30, SOLUSDT=28, XRPUSDT=27, ZECUSDT=26, BTCUSDT=20, 1000SHIBUSDT=20, TRXUSDT=17, PENGUUSDT=15, SKYAIUSDT=13, SWARMSUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 8 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 514 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 7932 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 38 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 15672 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 281 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 92 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 708 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 198 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 990 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 103 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 20 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 329 |
| RANGE_FADE | filtered | min_confidence | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 390 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 73 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 7523 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 32 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 14 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 17 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 63.00 | 65.00 | 2.00 | 21.45 | 19.50 | 20.00 | 0.00 | 3.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 514 | 63.00 | 65.00 | 2.00 | 17.81 | 19.94 | 19.90 | 1.95 | 4.81 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 7932 | 68.71 | 65.00 | -3.71 | 18.66 | 19.83 | 18.71 | 1.25 | 2.56 |
| DIVERGENCE_CONTINUATION | filtered | 38 | 53.35 | 65.00 | 11.65 | 21.97 | 19.81 | 19.02 | 2.18 | 0.35 |
| DIVERGENCE_CONTINUATION | kept | 15672 | 68.23 | 65.00 | -3.23 | 19.87 | 20.00 | 18.87 | 5.01 | 0.15 |
| FAILED_AUCTION_RECLAIM | filtered | 373 | 54.66 | 65.00 | 10.34 | 19.96 | 19.54 | 14.00 | 4.48 | 6.74 |
| FAILED_AUCTION_RECLAIM | kept | 708 | 71.05 | 65.00 | -6.05 | 21.43 | 19.66 | 14.00 | 4.47 | 0.46 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 238 | 51.36 | 65.00 | 13.64 | 21.10 | 19.73 | 15.20 | 2.70 | 15.71 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 990 | 71.16 | 65.00 | -6.16 | 23.22 | 19.82 | 15.20 | 2.22 | 0.02 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 68.40 | 65.00 | -3.40 | 20.80 | 20.00 | 20.00 | 1.50 | 1.80 |
| QUIET_COMPRESSION_BREAK | filtered | 123 | 53.42 | 65.00 | 11.58 | 21.71 | 18.56 | 15.80 | 0.00 | 12.08 |
| QUIET_COMPRESSION_BREAK | kept | 329 | 73.18 | 65.00 | -8.18 | 21.85 | 19.07 | 15.80 | 0.00 | -0.09 |
| RANGE_FADE | filtered | 1 | 61.70 | 65.00 | 3.30 | 20.90 | 20.00 | 13.40 | 0.00 | 8.00 |
| SR_FLIP_RETEST | filtered | 463 | 56.51 | 65.00 | 8.49 | 20.65 | 19.86 | 15.59 | 1.64 | 8.84 |
| SR_FLIP_RETEST | kept | 7523 | 71.21 | 65.00 | -6.21 | 24.02 | 19.99 | 15.29 | 2.36 | 2.30 |
| TREND_PULLBACK_EMA | filtered | 1 | 62.00 | 65.00 | 3.00 | 23.60 | 20.00 | 15.20 | 4.00 | 9.00 |
| TREND_PULLBACK_EMA | kept | 32 | 77.35 | 65.00 | -12.35 | 19.86 | 19.44 | 19.03 | 5.56 | -0.39 |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 62.94 | 65.00 | 2.06 | 20.07 | 18.99 | 20.00 | 2.43 | 3.34 |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 71.99 | 65.00 | -6.99 | 21.49 | 19.82 | 19.93 | 3.06 | 1.62 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 63.00 | 25.00 | 8.00 | 3.00 | 17.00 | 5.00 | 8.00 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 514 | 63.00 | 17.02 | 18.00 | 3.06 | 13.98 | 5.00 | 8.89 | 1.95 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 7932 | 68.71 | 20.43 | 18.00 | 3.01 | 12.72 | 6.50 | 9.37 | 1.25 |
| DIVERGENCE_CONTINUATION | filtered | 38 | 53.35 | 23.74 | 18.00 | 4.18 | 10.63 | 4.80 | 3.98 | 2.18 |
| DIVERGENCE_CONTINUATION | kept | 15672 | 68.23 | 17.03 | 18.00 | 3.03 | 13.99 | 4.28 | 7.05 | 5.01 |
| FAILED_AUCTION_RECLAIM | filtered | 373 | 54.66 | 22.49 | 14.63 | 5.06 | 11.43 | 6.32 | 5.12 | 4.48 |
| FAILED_AUCTION_RECLAIM | kept | 708 | 71.05 | 23.13 | 14.49 | 4.93 | 11.65 | 6.03 | 6.85 | 4.47 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 238 | 51.36 | 22.28 | 14.25 | 6.79 | 12.79 | 5.23 | 6.54 | 2.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 990 | 71.16 | 24.48 | 14.15 | 3.84 | 13.34 | 7.23 | 5.92 | 2.22 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 68.40 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 8.70 | 1.50 |
| QUIET_COMPRESSION_BREAK | filtered | 123 | 53.42 | 18.30 | 16.37 | 11.07 | 13.76 | 7.16 | 4.56 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 329 | 73.18 | 19.19 | 17.51 | 8.02 | 14.33 | 7.25 | 7.57 | 0.00 |
| RANGE_FADE | filtered | 1 | 61.70 | 25.00 | 18.00 | 3.00 | 12.00 | 5.00 | 6.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 463 | 56.51 | 19.22 | 16.42 | 5.43 | 13.14 | 5.89 | 7.39 | 1.64 |
| SR_FLIP_RETEST | kept | 7523 | 71.21 | 23.86 | 17.90 | 3.47 | 11.56 | 5.25 | 9.44 | 2.36 |
| TREND_PULLBACK_EMA | filtered | 1 | 62.00 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 4.00 |
| TREND_PULLBACK_EMA | kept | 32 | 77.35 | 20.50 | 18.00 | 3.56 | 14.94 | 7.36 | 7.88 | 5.56 |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 62.94 | 22.71 | 11.57 | 3.00 | 13.93 | 5.29 | 8.43 | 2.43 |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 71.99 | 25.00 | 16.24 | 3.18 | 12.35 | 6.41 | 7.38 | 3.06 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 8 | 63.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 514 | 63.00 | 0.02 | 0.00 | 4.73 | 0.00 | 0.00 | 0.00 | **4.75** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 7932 | 68.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 38 | 53.35 | 0.71 | 0.00 | 0.38 | 0.00 | 0.76 | 0.00 | **1.85** |
| DIVERGENCE_CONTINUATION | kept | 15672 | 68.23 | 0.00 | 0.00 | 0.15 | 0.00 | 0.01 | 0.00 | **0.16** |
| FAILED_AUCTION_RECLAIM | filtered | 373 | 54.66 | 0.41 | 0.00 | 3.30 | 0.00 | 1.96 | 0.00 | **5.67** |
| FAILED_AUCTION_RECLAIM | kept | 708 | 71.05 | 0.02 | 0.00 | 0.25 | 0.00 | 0.02 | 0.00 | **0.29** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 238 | 51.36 | 2.72 | 0.00 | 5.32 | 0.00 | 7.71 | 0.00 | **15.75** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 990 | 71.16 | 0.00 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.02** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 68.40 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.80** |
| QUIET_COMPRESSION_BREAK | filtered | 123 | 53.42 | 6.37 | 0.00 | 0.88 | 0.00 | 3.10 | 0.00 | **10.35** |
| QUIET_COMPRESSION_BREAK | kept | 329 | 73.18 | 0.00 | 0.00 | 0.07 | 0.00 | 0.97 | 0.00 | **1.04** |
| RANGE_FADE | filtered | 1 | 61.70 | 0.00 | 0.00 | 8.00 | 0.00 | 0.00 | 0.00 | **8.00** |
| SR_FLIP_RETEST | filtered | 463 | 56.51 | 0.41 | 0.00 | 1.44 | 0.00 | 2.24 | 0.00 | **4.09** |
| SR_FLIP_RETEST | kept | 7523 | 71.21 | 0.00 | 0.00 | 0.02 | 0.00 | 0.01 | 0.00 | **0.03** |
| TREND_PULLBACK_EMA | filtered | 1 | 62.00 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| TREND_PULLBACK_EMA | kept | 32 | 77.35 | 0.28 | 0.00 | 0.45 | 0.00 | 0.00 | 0.00 | **0.73** |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 62.94 | 0.00 | 0.00 | 0.34 | 0.00 | 0.00 | 0.00 | **0.34** |
| VOLUME_SURGE_BREAKOUT | kept | 17 | 71.99 | 0.00 | 0.00 | 0.56 | 0.00 | 0.00 | 0.00 | **0.56** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=69 (64.5%) | PREMATURE=9 (8.4%) | NEUTRAL=29 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 60 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 1 | 0 | 0 | 0 |
| other | 39 | 4 | 14 | 0 |
| regime_shift | 29 | 5 | 15 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 2 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 2 | 2 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 12 | 1 | 5 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 11 | 2 | 4 | 0 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 10 | 0 | 9 | 0 |
| SR_FLIP_RETEST | 29 | 4 | 9 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4030822`
- `Path funnel` emissions: `90`
- `Regime distribution` emissions: `90`
- `QUIET_SCALP_BLOCK` events: `466`
- `confidence_gate` events: `34977`
- `free_channel_post` events: `256`
- `pre_tp_fire` events: `130`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **130**
- Avg resolved threshold: **0.365%** raw → avg net **+2.95%** @ 10x
- Avg time-to-fire from dispatch: **319s**
- By threshold source: stamped=130

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 49 | 0.315% | +2.45% | 343 | stamped=49 |
| LIQUIDITY_SWEEP_REVERSAL | 26 | 0.593% | +5.24% | 278 | stamped=26 |
| FAILED_AUCTION_RECLAIM | 24 | 0.304% | +2.34% | 288 | stamped=24 |
| QUIET_COMPRESSION_BREAK | 21 | 0.235% | +1.65% | 335 | stamped=21 |
| DIVERGENCE_CONTINUATION | 8 | 0.404% | +3.33% | 371 | stamped=8 |
| CONTINUATION_LIQUIDITY_SWEEP | 2 | 0.556% | +4.87% | 290 | stamped=2 |
- Top symbols: TAOUSDT=7, INJUSDT=5, RIVERUSDT=5, TIAUSDT=5, ENAUSDT=4, UNIUSDT=4, SAGAUSDT=4, NEARUSDT=4, HYPEUSDT=4, DASHUSDT=4

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **173**
- Total REST-fallback activations: **69**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 138 | 1854 | 3620 | 4564 | 0 |
| futures_liq | 35 | 1916 | 3293 | 26258 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 69 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **256**

| Source | Count |
|---|---:|
| pre_tp | 130 |
| signal_close | 120 |
| regime_shift | 5 |
| signal_highlight | 1 |

- By severity: HIGH=256

## Dependency readiness
- cvd: presence[absent=10169, present=551451] state[empty=10169, populated=551451] buckets[few=12, many=526992, none=10169, some=24447] sources[none] quality[none]
- funding_rate: presence[absent=14054, present=547566] state[empty=14054, populated=547566] buckets[few=547566, none=14054] sources[none] quality[none]
- liquidation_clusters: presence[absent=479418, present=82202] state[empty=479418, populated=82202] buckets[few=66473, none=479418, some=15729] sources[none] quality[none]
- oi_snapshot: presence[absent=4589, present=557031] state[empty=4589, populated=557031] buckets[few=126, many=555066, none=4589, some=1839] sources[none] quality[none]
- order_book: presence[absent=73921, present=487699] state[populated=487699, unavailable=73921] buckets[few=487699, none=73921] sources[book_ticker=487699, unavailable=73921] quality[none=73921, top_of_book_only=487699]
- orderblocks: presence[absent=561620] state[empty=561620] buckets[none=561620] sources[not_implemented=561620] quality[none]
- recent_ticks: presence[absent=9517, present=552103] state[empty=9517, populated=552103] buckets[many=552103, none=9517] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.973109006881714` sec
- Median create→first breach: `393.2091500759125` sec
- Median create→terminal: `672.3336389064789` sec
- Median first breach→terminal: `7.7337799072265625` sec
- Fast-failure buckets: `{"under_120s": {"count": 17, "pct": 14.0}, "under_180s": {"count": 25, "pct": 20.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 9, "pct": 7.4}}`
- ~3 minute terminal-close behavior: `{"count": 10, "pct": 3.8}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 7 | 7 | 0.0 | 14.3 | 0.0 | -0.1749 | 571.999498128891 | 737.1598074436188 |
| DIVERGENCE_CONTINUATION | 21 | 21 | 0.0 | 33.3 | 0.0 | -0.1716 | 259.2296998500824 | 521.8218309879303 |
| FAILED_AUCTION_RECLAIM | 46 | 46 | 0.0 | 6.5 | 0.0 | 0.0007 | 446.68852734565735 | 654.6265170574188 |
| LIQUIDITY_SWEEP_REVERSAL | 50 | 50 | 0.0 | 14.0 | 0.0 | -0.0143 | 383.9384375810623 | 661.8513414859772 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.4304 | None | 680.3762350082397 |
| QUIET_COMPRESSION_BREAK | 40 | 40 | 0.0 | 0.0 | 0.0 | -0.0457 | 273.1330270767212 | 669.9810310602188 |
| SR_FLIP_RETEST | 97 | 97 | 0.0 | 8.2 | 0.0 | 0.0056 | 451.6279580593109 | 705.8553184270859 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | -0.0786 | None | 766.0209629535675 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.9638 | None | None |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 49272 | 151 | 16827 | 0.0 | 8.2 | 451.6279580593109 | 705.8553184270859 | 32445 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 676 | 5 | 622 | 0.0 | 0.0 | None | 766.0209629535675 | 54 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `447`
- Gating Δ: `-139191`
- No-generation Δ: `-14164091`
- Fast failures Δ: `25`
- Quality changes: `{"CONTINUATION_LIQUIDITY_SWEEP": {"avg_pnl_delta": -0.1749, "current_avg_pnl": -0.1749, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.1716, "current_avg_pnl": -0.1716, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0007, "current_avg_pnl": 0.0007, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.0143, "current_avg_pnl": -0.0143, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.0457, "current_avg_pnl": -0.0457, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0056, "current_avg_pnl": 0.0056, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 133, "geometry_changed_delta": 0, "geometry_preserved_delta": -87402, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 451.63, "median_terminal_delta_sec": 705.86, "sl_rate_delta": 8.2, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 54, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 766.02, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
