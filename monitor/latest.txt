# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `821` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 574 | 574 | 478 | 12 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6644 | 6644 | 6308 | 44 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 120521 | 119947 | 574 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 102177 | 102177 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 102177 | 95533 | 6644 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 102177 | 97650 | 4527 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 120521 | 120327 | 194 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 120521 | 120497 | 24 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 102177 | 102147 | 30 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 120521 | 120521 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 102177 | 102160 | 17 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 102177 | 102155 | 22 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 102177 | 91912 | 10265 | 0 | 0 | 0 | low-sample (reclaim_hold_failed) |
| EVAL::STANDARD | 102177 | 93900 | 8277 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 102177 | 101405 | 772 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 120521 | 120300 | 221 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 120521 | 120521 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4527 | 4527 | 3081 | 63 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 194 | 194 | 183 | 1 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 24 | 24 | 24 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 8277 | 8277 | 6270 | 140 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 30 | 30 | 14 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 17 | 17 | 5 | 3 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 22 | 22 | 20 | 1 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 10265 | 10265 | 3644 | 271 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 772 | 772 | 709 | 12 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 221 | 221 | 191 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=119947): breakout_not_found=75664, basic_filters_failed=19632, retest_proximity_failed=18475, volume_spike_missing=3983, ema_alignment_reject=1186, insufficient_candles=753, missing_fvg_or_orderblock=254
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=102177): cls_disabled_merged_into_lsr=102177
- **EVAL::DIVERGENCE_CONTINUATION** (total=95533): cvd_divergence_failed=34317, h1_trend_not_aligned=28369, basic_filters_failed=16359, ema_alignment_reject=10767, regime_blocked=3525, retest_proximity_failed=1352, missing_fvg_or_orderblock=844
- **EVAL::FAILED_AUCTION_RECLAIM** (total=97650): auction_not_detected=44240, reclaim_hold_failed=22139, basic_filters_failed=16359, tail_too_small=14912
- **EVAL::FUNDING_EXTREME** (total=120327): funding_not_extreme=96784, basic_filters_failed=19162, ema_alignment_reject=2079, missing_funding_rate=1437, rsi_reject=588, cvd_divergence_failed=127, momentum_reject=79, insufficient_candles=69, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=120497): cascade_threshold_not_met=98396, basic_filters_failed=19660, cvd_divergence_failed=961, rsi_reject=893, insufficient_candles=516, missing_fvg_or_orderblock=41, volume_spike_missing=30
- **EVAL::MA_CROSS_TREND_SHIFT** (total=102147): no_ma_cross=83161, basic_filters_failed=16359, ma_cross_cooldown=2627
- **EVAL::OPENING_RANGE_BREAKOUT** (total=120521): feature_disabled=120521
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=102160): regime_blocked=60442, breakout_not_found=21687, ema_alignment_reject=10920, adx_reject=4816, basic_filters_failed=4293, rsi_reject=2
- **EVAL::QUIET_COMPRESSION_BREAK** (total=102155): compression_not_detected=47408, regime_blocked=41735, basic_filters_failed=12066, breakout_not_detected=897, volume_confirmation_failed=47, rsi_reject=2
- **EVAL::SR_FLIP_RETEST** (total=91912): reclaim_hold_failed=25211, flip_close_not_confirmed=23120, retest_out_of_zone=20713, basic_filters_failed=16359, wick_quality_failed=4309, ema_alignment_reject=1500, missing_fvg_or_orderblock=671, rsi_reject=29
- **EVAL::STANDARD** (total=93900): momentum_reject=28450, adx_reject=17572, basic_filters_failed=15559, macd_reject=11527, sweeps_not_detected=10241, ema_alignment_reject=9837, invalid_sl_geometry=501, rsi_reject=146, mtf_reject=67
- **EVAL::TREND_PULLBACK** (total=101405): h1_trend_not_aligned=33503, ema_alignment_reject=17097, h1_pullback_not_confirmed=10343, no_ema_reclaim_close=8619, basic_filters_failed=7168, ema_not_tested_prev=7001, regime_blocked=5978, body_conviction_fail=4855, rsi_reject=4113, prev_already_above_emas=917, no_prev_high_break=642, prev_already_below_emas=535, no_prev_low_break=290, momentum_flat=200, missing_fvg_or_orderblock=85, momentum_reject=31, ema21_not_tagged=28
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=120300): breakout_not_found=80764, basic_filters_failed=19632, retest_proximity_failed=14412, volume_spike_missing=3088, ema_alignment_reject=1325, insufficient_candles=753, missing_fvg_or_orderblock=284, rsi_reject=42
- **EVAL::WHALE_MOMENTUM** (total=120521): momentum_reject=78953, recent_ticks_insufficient=36052, basic_filters_failed=5508, insufficient_candles=8

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 75733 | 56.3% |
| TRENDING_DOWN | 32639 | 24.3% |
| TRENDING_UP | 22771 | 16.9% |
| RANGING | 3348 | 2.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1008**
- Average confidence gap to threshold: **13.95** (samples=1008) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AVAXUSDT=53, LITUSDT=53, CRCLUSDT=52, MUUSDT=49, 1000PEPEUSDT=44, BCHUSDT=30, ASTERUSDT=30, TAOUSDT=30, EWYUSDT=28, DOGEUSDT=26

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 28 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 13 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 48 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 127 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 199 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 106 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 355 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 374 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 23 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 400 |
| POST_DISPLACEMENT_CONTINUATION | filtered | min_confidence | 4 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 3 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 1 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 725 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 435 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1302 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 55 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 2 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 9 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 28 | 64.02 | 65.00 | 0.98 | 21.02 | 19.44 | 19.42 | 0.00 | 3.86 |
| BREAKDOWN_SHORT | kept | 13 | 69.03 | 65.00 | -4.03 | 21.38 | 19.52 | 18.97 | 0.00 | 1.62 |
| DIVERGENCE_CONTINUATION | filtered | 48 | 61.88 | 65.00 | 3.12 | 20.74 | 19.75 | 17.60 | 1.04 | 6.01 |
| DIVERGENCE_CONTINUATION | kept | 127 | 71.45 | 65.00 | -6.45 | 20.99 | 19.80 | 17.77 | 2.24 | 1.50 |
| FAILED_AUCTION_RECLAIM | filtered | 305 | 53.47 | 65.00 | 11.53 | 20.76 | 19.56 | 20.00 | 4.50 | 9.77 |
| FAILED_AUCTION_RECLAIM | kept | 355 | 69.68 | 65.00 | -4.68 | 21.16 | 19.64 | 20.00 | 4.66 | 0.78 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.00 | 65.00 | 0.00 | 21.20 | 20.00 | 17.00 | 2.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 397 | 51.32 | 65.00 | 13.68 | 20.85 | 19.51 | 15.20 | 2.82 | 15.48 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 400 | 69.03 | 65.00 | -4.03 | 21.19 | 19.58 | 15.20 | 2.17 | 0.58 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 4 | 61.65 | 65.00 | 3.35 | 21.58 | 20.00 | 17.50 | 2.50 | 9.18 |
| POST_DISPLACEMENT_CONTINUATION | kept | 3 | 69.87 | 65.00 | -4.87 | 21.97 | 20.00 | 19.10 | 2.67 | 4.97 |
| QUIET_COMPRESSION_BREAK | filtered | 1 | 62.80 | 65.00 | 2.20 | 18.80 | 20.00 | 20.00 | 0.00 | 2.40 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 70.90 | 65.00 | -5.90 | 18.80 | 20.00 | 20.00 | 0.00 | 4.30 |
| SR_FLIP_RETEST | filtered | 1160 | 55.16 | 65.00 | 9.84 | 20.97 | 19.89 | 15.90 | 1.80 | 11.17 |
| SR_FLIP_RETEST | kept | 1302 | 70.48 | 65.00 | -5.48 | 21.02 | 19.94 | 15.77 | 2.16 | 0.99 |
| TREND_PULLBACK_EMA | kept | 55 | 74.52 | 65.00 | -9.52 | 20.76 | 19.63 | 18.04 | 5.21 | -0.33 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 64.70 | 65.00 | 0.30 | 20.60 | 20.00 | 18.00 | 3.00 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 68.02 | 65.00 | -3.02 | 20.99 | 19.34 | 17.48 | 2.56 | 2.67 |
| WHALE_MOMENTUM | kept | 2 | 68.95 | 65.00 | -3.95 | 20.40 | 20.00 | 17.00 | 0.00 | 1.55 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 28 | 64.02 | 21.00 | 18.00 | 3.32 | 11.57 | 5.52 | 8.43 | 0.00 |
| BREAKDOWN_SHORT | kept | 13 | 69.03 | 21.92 | 18.00 | 5.08 | 11.46 | 5.58 | 8.61 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 48 | 61.88 | 20.17 | 18.00 | 4.75 | 11.00 | 5.35 | 7.55 | 1.04 |
| DIVERGENCE_CONTINUATION | kept | 127 | 71.45 | 22.35 | 18.00 | 5.53 | 12.06 | 5.56 | 7.82 | 2.24 |
| FAILED_AUCTION_RECLAIM | filtered | 305 | 53.47 | 22.55 | 14.30 | 5.84 | 11.82 | 6.70 | 4.42 | 4.50 |
| FAILED_AUCTION_RECLAIM | kept | 355 | 69.68 | 23.85 | 14.17 | 4.60 | 11.83 | 5.67 | 5.69 | 4.66 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.00 | 25.00 | 8.00 | 3.00 | 17.00 | 5.00 | 10.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 397 | 51.32 | 23.01 | 14.04 | 6.21 | 12.43 | 5.63 | 5.88 | 2.82 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 400 | 69.03 | 23.97 | 14.35 | 4.60 | 12.34 | 5.63 | 6.57 | 2.17 |
| POST_DISPLACEMENT_CONTINUATION | filtered | 4 | 61.65 | 16.50 | 18.00 | 6.00 | 14.00 | 7.25 | 6.57 | 2.50 |
| POST_DISPLACEMENT_CONTINUATION | kept | 3 | 69.87 | 19.00 | 18.00 | 5.00 | 14.00 | 7.83 | 9.33 | 2.67 |
| QUIET_COMPRESSION_BREAK | filtered | 1 | 62.80 | 17.00 | 8.00 | 15.00 | 14.00 | 8.50 | 2.70 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 70.90 | 17.00 | 18.00 | 15.00 | 14.00 | 8.50 | 2.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 1160 | 55.16 | 20.30 | 14.25 | 6.05 | 13.37 | 6.39 | 6.98 | 1.80 |
| SR_FLIP_RETEST | kept | 1302 | 70.48 | 22.00 | 15.78 | 5.22 | 13.69 | 6.13 | 7.58 | 2.16 |
| TREND_PULLBACK_EMA | kept | 55 | 74.52 | 19.18 | 18.00 | 3.60 | 14.58 | 6.25 | 8.13 | 5.21 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 64.70 | 25.00 | 8.00 | 3.00 | 17.00 | 5.00 | 6.70 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 68.02 | 19.67 | 15.78 | 5.00 | 12.33 | 6.83 | 8.52 | 2.56 |
| WHALE_MOMENTUM | kept | 2 | 68.95 | 25.00 | 18.00 | 3.00 | 10.50 | 5.00 | 9.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 28 | 64.02 | 0.00 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | **0.51** |
| BREAKDOWN_SHORT | kept | 13 | 69.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 48 | 61.88 | 0.00 | 0.00 | 0.70 | 0.00 | 0.60 | 0.00 | 0.00 | **1.30** |
| DIVERGENCE_CONTINUATION | kept | 127 | 71.45 | 0.00 | 0.00 | 0.45 | 0.00 | 0.74 | 0.00 | 0.00 | **1.19** |
| FAILED_AUCTION_RECLAIM | filtered | 305 | 53.47 | 0.00 | 0.00 | 2.19 | 0.00 | 5.26 | 0.00 | 0.00 | **7.45** |
| FAILED_AUCTION_RECLAIM | kept | 355 | 69.68 | 0.00 | 0.00 | 0.03 | 0.00 | 0.18 | 0.00 | 0.00 | **0.21** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 65.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 397 | 51.32 | 0.00 | 0.00 | 5.74 | 0.00 | 8.74 | 0.00 | 0.00 | **14.48** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 400 | 69.03 | 0.00 | 0.00 | 0.10 | 0.00 | 0.12 | 0.00 | 0.00 | **0.22** |
| POST_DISPLACEMENT_CONTINUATION | filtered | 4 | 61.65 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| POST_DISPLACEMENT_CONTINUATION | kept | 3 | 69.87 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 1 | 62.80 | 0.00 | 0.00 | 0.00 | 0.00 | 2.40 | 0.00 | 0.00 | **2.40** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 70.90 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | filtered | 1160 | 55.16 | 0.14 | 0.00 | 1.59 | 0.00 | 4.48 | 0.00 | 0.00 | **6.21** |
| SR_FLIP_RETEST | kept | 1302 | 70.48 | 0.00 | 0.00 | 0.29 | 0.00 | 0.41 | 0.00 | 0.00 | **0.70** |
| TREND_PULLBACK_EMA | kept | 55 | 74.52 | 0.00 | 0.00 | 0.44 | 0.00 | 0.00 | 0.00 | 0.00 | **0.44** |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 64.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 9 | 68.02 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | kept | 2 | 68.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=259 (68.7%) | PREMATURE=32 (8.5%) | NEUTRAL=86 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 227 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 5 | 2 | 0 | 0 |
| ema_crossover | 7 | 0 | 1 | 0 |
| momentum_loss | 175 | 17 | 43 | 0 |
| regime_shift | 72 | 13 | 42 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 6 | 0 | 2 | 0 |
| DIVERGENCE_CONTINUATION | 18 | 1 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 42 | 4 | 12 | 0 |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 69 | 14 | 35 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 116 | 12 | 33 | 0 |
| TREND_PULLBACK_EMA | 4 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 1 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 5 | 2 | 0 | 1.3 | 4.5 | -0.46 | **INSUFFICIENT_SAMPLE** — only 7 classified kills (need >= 20); let data accumulate before tuning |
| ema_crossover | 7 | 0 | 1 | 4.3 | 0.0 | +0.54 | **INSUFFICIENT_SAMPLE** — only 8 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 175 | 17 | 43 | 93.8 | 25.8 | +0.29 | **KEEP** — net-helping: avg +0.29R/kill across 235 kills (saved 93.8R vs missed 25.8R) |
| regime_shift | 72 | 13 | 42 | 42.4 | 17.1 | +0.20 | **KEEP** — net-helping: avg +0.20R/kill across 127 kills (saved 42.4R vs missed 17.1R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `732964`
- `Path funnel` emissions: `19`
- `Regime distribution` emissions: `19`
- `QUIET_SCALP_BLOCK` events: `1008`
- `confidence_gate` events: `4213`
- `free_channel_post` events: `101`
- `pre_tp_fire` events: `40`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **40**
- Avg resolved threshold: **0.355%** raw → avg net **+2.85%** @ 10x
- Avg time-to-fire from dispatch: **357s**
- By threshold source: stamped=40

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 15 | 0.258% | +1.88% | 412 | stamped=15 |
| LIQUIDITY_SWEEP_REVERSAL | 10 | 0.532% | +4.62% | 325 | stamped=10 |
| FAILED_AUCTION_RECLAIM | 9 | 0.270% | +2.00% | 368 | stamped=9 |
| TREND_PULLBACK_EMA | 3 | 0.492% | +4.22% | 90 | stamped=3 |
| DIVERGENCE_CONTINUATION | 3 | 0.372% | +3.02% | 424 | stamped=3 |
- Top symbols: PLAYUSDT=5, ENAUSDT=5, FARTCOINUSDT=4, JTOUSDT=4, PUMPUSDT=3, SOLUSDT=3, FILUSDT=2, USELESSUSDT=2, SAHARAUSDT=2, XLMUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **101**

| Source | Count |
|---|---:|
| signal_close | 53 |
| pre_tp | 40 |
| regime_shift | 4 |
| signal_highlight | 4 |

- By severity: HIGH=101

## Dependency readiness
- cvd: presence[present=120522] state[populated=120522] buckets[few=7, many=120243, some=272] sources[none] quality[none]
- funding_rate: presence[absent=1438, present=119084] state[empty=1438, populated=119084] buckets[few=119084, none=1438] sources[none] quality[none]
- liquidation_clusters: presence[absent=63639, present=56883] state[empty=63639, populated=56883] buckets[few=41969, none=63639, some=14914] sources[none] quality[none]
- oi_snapshot: presence[absent=642, present=119880] state[empty=642, populated=119880] buckets[few=226, many=118472, none=642, some=1182] sources[none] quality[none]
- order_book: presence[absent=67577, present=52945] state[populated=52945, unavailable=67577] buckets[few=52945, none=67577] sources[book_ticker=52945, unavailable=67577] quality[none=67577, top_of_book_only=52945]
- orderblocks: presence[absent=120522] state[empty=120522] buckets[none=120522] sources[not_implemented=120522] quality[none]
- recent_ticks: presence[absent=4230, present=116292] state[empty=4230, populated=116292] buckets[many=116292, none=4230] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `15.942397832870483` sec
- Median create→first breach: `487.56981587409973` sec
- Median create→terminal: `757.6131818294525` sec
- Median first breach→terminal: `17.92982506752014` sec
- Fast-failure buckets: `{"under_120s": {"count": 4, "pct": 7.8}, "under_180s": {"count": 9, "pct": 17.6}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.0}}`
- ~3 minute terminal-close behavior: `{"count": 5, "pct": 4.4}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | -0.3485 | 716.4990365505219 | 950.3171745538712 |
| DIVERGENCE_CONTINUATION | 12 | 12 | 0.0 | 8.3 | 0.0 | 25.0 | 0.2322 | 698.6042500734329 | 855.9753019809723 |
| FAILED_AUCTION_RECLAIM | 17 | 17 | 0.0 | 0.0 | 0.0 | 52.9 | 0.2958 | 2062.348834991455 | 785.1080790758133 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.199 | None | 935.4448728561401 |
| LIQUIDITY_SWEEP_REVERSAL | 24 | 24 | 0.0 | 8.3 | 0.0 | 41.7 | -0.0142 | 403.52557241916656 | 792.5972925424576 |
| SR_FLIP_RETEST | 51 | 51 | 0.0 | 15.7 | 0.0 | 29.4 | 0.0612 | 457.9260754585266 | 706.8998908996582 |
| TREND_PULLBACK_EMA | 4 | 4 | 0.0 | 0.0 | 0.0 | 75.0 | 0.2932 | 164.21394300460815 | 535.4624304771423 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9582 | 251.68797290325165 | 264.91750490665436 |
| WHALE_MOMENTUM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.3264 | None | 844.8096349239349 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 10265 | 271 | 3644 | 0.0 | 15.7 | 457.9260754585266 | 706.8998908996582 | 6621 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 772 | 12 | 709 | 0.0 | 0.0 | 164.21394300460815 | 535.4624304771423 | 63 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-28`
- Gating Δ: `-1375`
- No-generation Δ: `186449`
- Fast failures Δ: `-5`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.9946, "current_avg_pnl": -0.3485, "current_win_rate": 0.0, "previous_avg_pnl": 0.6461, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.1822, "current_avg_pnl": 0.2322, "current_win_rate": 0.0, "previous_avg_pnl": 0.4144, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.4093, "current_avg_pnl": 0.2958, "current_win_rate": 0.0, "previous_avg_pnl": -0.1135, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.1386, "current_avg_pnl": -0.0142, "current_win_rate": 0.0, "previous_avg_pnl": 0.1244, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0156, "current_avg_pnl": 0.0612, "current_win_rate": 0.0, "previous_avg_pnl": 0.0768, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 1.2545, "current_avg_pnl": 0.2932, "current_win_rate": 0.0, "previous_avg_pnl": -0.9613, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -0.7111, "current_avg_pnl": -0.9582, "current_win_rate": 0.0, "previous_avg_pnl": -0.2471, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 18, "geometry_changed_delta": 0, "geometry_preserved_delta": 910, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -97.62, "median_terminal_delta_sec": -17.19, "sl_rate_delta": 7.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 20, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -342.42, "median_terminal_delta_sec": 22.84, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDATION_REVERSAL**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
