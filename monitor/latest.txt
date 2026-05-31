# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `8` sec (warning=False)
- Latest performance record age: `828` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 209 | 209 | 128 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2994 | 2994 | 2590 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 21694 | 21578 | 118 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 20356 | 20357 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 20299 | 18949 | 1406 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 20364 | 19330 | 1067 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 21812 | 21739 | 82 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 21677 | 21677 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 20398 | 20399 | 9 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 21695 | 21698 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 20359 | 20361 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 20298 | 20295 | 5 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 20173 | 18218 | 2066 | 0 | 0 | 0 | low-sample (reclaim_hold_failed) |
| EVAL::STANDARD | 20077 | 17976 | 2162 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 20141 | 19893 | 259 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 21690 | 21619 | 75 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 21679 | 21600 | 89 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2381 | 2381 | 1455 | 67 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 199 | 199 | 171 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4865 | 4865 | 4213 | 67 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 13 | 13 | 12 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 4523 | 4523 | 1274 | 155 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 529 | 529 | 518 | 4 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 179 | 179 | 86 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 89 | 89 | 89 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=21578): breakout_not_found=15920, retest_proximity_failed=3557, volume_spike_missing=894, basic_filters_failed=690, ema_alignment_reject=355, insufficient_candles=87, missing_fvg_or_orderblock=75
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=20357): cls_disabled_merged_into_lsr=20357
- **EVAL::DIVERGENCE_CONTINUATION** (total=18949): cvd_divergence_failed=8843, h1_trend_not_aligned=6258, ema_alignment_reject=2480, basic_filters_failed=685, retest_proximity_failed=468, missing_fvg_or_orderblock=215
- **EVAL::FAILED_AUCTION_RECLAIM** (total=19330): auction_not_detected=11197, reclaim_hold_failed=3764, tail_too_small=3681, basic_filters_failed=685, rsi_reject=3
- **EVAL::FUNDING_EXTREME** (total=21739): funding_not_extreme=19205, missing_funding_rate=747, basic_filters_failed=676, ema_alignment_reject=574, rsi_reject=380, momentum_reject=72, cvd_divergence_failed=63, missing_fvg_or_orderblock=14, insufficient_candles=8
- **EVAL::LIQUIDATION_REVERSAL** (total=21677): cascade_threshold_not_met=20630, basic_filters_failed=690, cvd_divergence_failed=146, rsi_reject=135, insufficient_candles=69, missing_fvg_or_orderblock=7
- **EVAL::MA_CROSS_TREND_SHIFT** (total=20399): no_ma_cross=19413, basic_filters_failed=685, ma_cross_cooldown=301
- **EVAL::OPENING_RANGE_BREAKOUT** (total=21698): feature_disabled=21698
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=20361): regime_blocked=14213, breakout_not_found=2937, ema_alignment_reject=2082, adx_reject=1013, basic_filters_failed=116
- **EVAL::QUIET_COMPRESSION_BREAK** (total=20295): compression_not_detected=13478, regime_blocked=6133, basic_filters_failed=569, breakout_not_detected=108, volume_confirmation_failed=6, missing_fvg_or_orderblock=1
- **EVAL::SR_FLIP_RETEST** (total=18218): reclaim_hold_failed=5937, flip_close_not_confirmed=5546, retest_out_of_zone=4730, wick_quality_failed=766, basic_filters_failed=684, ema_alignment_reject=315, missing_fvg_or_orderblock=199, rsi_reject=41
- **EVAL::STANDARD** (total=17976): momentum_reject=5324, adx_reject=5051, sweeps_not_detected=2624, macd_reject=2396, ema_alignment_reject=1223, basic_filters_failed=1143, invalid_sl_geometry=179, rsi_reject=35, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=19893): h1_trend_not_aligned=6418, ema_alignment_reject=4190, h1_pullback_not_confirmed=2633, no_ema_reclaim_close=2205, ema_not_tested_prev=1487, body_conviction_fail=1071, rsi_reject=715, basic_filters_failed=383, prev_already_above_emas=333, no_prev_high_break=133, prev_already_below_emas=92, no_prev_low_break=91, momentum_flat=60, momentum_reject=36, missing_fvg_or_orderblock=31, ema21_not_tagged=15
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=21619): breakout_not_found=16646, retest_proximity_failed=3286, basic_filters_failed=690, volume_spike_missing=611, ema_alignment_reject=211, insufficient_candles=87, missing_fvg_or_orderblock=71, rsi_reject=17
- **EVAL::WHALE_MOMENTUM** (total=21600): momentum_reject=15021, recent_ticks_insufficient=6319, basic_filters_failed=258, insufficient_candles=2

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 35739 | 70.2% |
| TRENDING_DOWN | 7819 | 15.4% |
| TRENDING_UP | 5010 | 9.8% |
| RANGING | 2307 | 4.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1151**
- Average confidence gap to threshold: **14.75** (samples=1151) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: CRCLUSDT=48, SEIUSDT=43, PUMPUSDT=42, ADAUSDT=39, ALGOUSDT=39, 1000PEPEUSDT=37, LINKUSDT=32, MSTRUSDT=32, XLMUSDT=31, ENAUSDT=31

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 3 |
| BREAKDOWN_SHORT | filtered | min_confidence | 1 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 61 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 56 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 267 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 51 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 455 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 245 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 13 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 203 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 2 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 564 |
| SR_FLIP_RETEST | filtered | min_confidence | 231 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 992 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 14 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 9 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 4 | 46.00 | 65.00 | 19.00 | 20.50 | 17.70 | 20.00 | 0.00 | 22.20 |
| BREAKDOWN_SHORT | kept | 1 | 67.30 | 65.00 | -2.30 | 20.90 | 18.40 | 20.00 | 0.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 80 | 50.76 | 65.00 | 14.24 | 20.91 | 19.57 | 17.99 | 2.12 | 15.81 |
| DIVERGENCE_CONTINUATION | kept | 56 | 70.50 | 65.00 | -5.50 | 20.63 | 19.57 | 18.12 | 1.82 | 1.26 |
| FAILED_AUCTION_RECLAIM | filtered | 318 | 51.72 | 65.00 | 13.28 | 20.35 | 19.72 | 20.00 | 4.17 | 14.47 |
| FAILED_AUCTION_RECLAIM | kept | 455 | 70.51 | 65.00 | -5.51 | 20.69 | 19.82 | 20.00 | 4.41 | 0.40 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.70 | 65.00 | 19.30 | 21.20 | 20.00 | 17.00 | 0.00 | 5.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 67.00 | 65.00 | -2.00 | 20.10 | 20.00 | 17.00 | 2.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 258 | 48.52 | 65.00 | 16.48 | 21.12 | 19.62 | 18.02 | 3.08 | 15.83 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 203 | 69.88 | 65.00 | -4.88 | 21.18 | 19.60 | 17.54 | 2.44 | 0.31 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 81.50 | 65.00 | -16.50 | 20.75 | 20.00 | 18.10 | 4.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 795 | 52.86 | 65.00 | 12.14 | 20.69 | 19.91 | 15.92 | 2.00 | 13.52 |
| SR_FLIP_RETEST | kept | 992 | 70.47 | 65.00 | -5.47 | 20.83 | 19.96 | 15.54 | 2.25 | 0.19 |
| TREND_PULLBACK_EMA | filtered | 1 | 64.20 | 65.00 | 0.80 | 21.00 | 20.00 | 20.00 | 5.50 | 6.90 |
| TREND_PULLBACK_EMA | kept | 14 | 75.13 | 65.00 | -10.13 | 21.46 | 19.67 | 18.11 | 5.54 | 1.49 |
| VOLUME_SURGE_BREAKOUT | filtered | 13 | 59.87 | 65.00 | 5.13 | 21.02 | 18.37 | 20.00 | 3.81 | 8.34 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 67.90 | 65.00 | -2.90 | 21.00 | 19.20 | 20.00 | 2.75 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 4 | 46.00 | 25.00 | 8.00 | 12.00 | 14.00 | 2.50 | 6.70 | 0.00 |
| BREAKDOWN_SHORT | kept | 1 | 67.30 | 25.00 | 18.00 | 3.00 | 17.00 | 5.00 | 2.30 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 80 | 50.76 | 23.10 | 10.00 | 7.42 | 12.20 | 5.50 | 8.11 | 2.12 |
| DIVERGENCE_CONTINUATION | kept | 56 | 70.50 | 21.57 | 15.68 | 6.21 | 12.21 | 6.09 | 8.80 | 1.82 |
| FAILED_AUCTION_RECLAIM | filtered | 318 | 51.72 | 21.48 | 14.18 | 7.75 | 11.36 | 6.34 | 5.16 | 4.17 |
| FAILED_AUCTION_RECLAIM | kept | 455 | 70.51 | 23.86 | 14.20 | 4.57 | 12.11 | 5.94 | 5.83 | 4.41 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.70 | 17.00 | 8.00 | 6.00 | 17.00 | 9.00 | 8.70 | 0.00 |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 67.00 | 17.00 | 8.00 | 3.00 | 17.00 | 10.00 | 10.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 258 | 48.52 | 22.28 | 14.03 | 7.16 | 12.66 | 5.50 | 6.15 | 3.08 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 203 | 69.88 | 23.45 | 14.08 | 4.73 | 12.55 | 5.89 | 7.06 | 2.44 |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 81.50 | 17.00 | 18.00 | 12.00 | 14.00 | 8.50 | 8.00 | 4.00 |
| SR_FLIP_RETEST | filtered | 795 | 52.86 | 21.62 | 10.91 | 7.55 | 14.18 | 6.53 | 6.32 | 2.00 |
| SR_FLIP_RETEST | kept | 992 | 70.47 | 22.98 | 13.85 | 5.06 | 14.61 | 6.22 | 6.91 | 2.25 |
| TREND_PULLBACK_EMA | filtered | 1 | 64.20 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.70 | 5.50 |
| TREND_PULLBACK_EMA | kept | 14 | 75.13 | 19.86 | 18.00 | 3.86 | 14.43 | 7.54 | 8.94 | 5.54 |
| VOLUME_SURGE_BREAKOUT | filtered | 13 | 59.87 | 24.38 | 10.31 | 7.85 | 13.23 | 5.27 | 7.98 | 3.81 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 67.90 | 21.00 | 18.00 | 4.50 | 10.00 | 6.50 | 8.15 | 2.75 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 4 | 46.00 | 0.00 | 0.00 | 0.00 | 0.00 | 19.20 | 0.00 | 0.00 | **19.20** |
| BREAKDOWN_SHORT | kept | 1 | 67.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 80 | 50.76 | 0.00 | 0.00 | 2.56 | 0.00 | 9.51 | 0.00 | 0.00 | **12.07** |
| DIVERGENCE_CONTINUATION | kept | 56 | 70.50 | 0.00 | 0.00 | 0.43 | 0.00 | 0.13 | 0.00 | 0.00 | **0.56** |
| FAILED_AUCTION_RECLAIM | filtered | 318 | 51.72 | 0.00 | 0.00 | 1.17 | 0.00 | 10.54 | 0.00 | 0.00 | **11.71** |
| FAILED_AUCTION_RECLAIM | kept | 455 | 70.51 | 0.00 | 0.00 | 0.03 | 0.00 | 0.09 | 0.00 | 0.00 | **0.12** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 45.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 258 | 48.52 | 0.00 | 0.00 | 4.59 | 0.00 | 9.27 | 0.00 | 0.00 | **13.86** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 203 | 69.88 | 0.00 | 0.00 | 0.06 | 0.00 | 0.06 | 0.00 | 0.00 | **0.12** |
| POST_DISPLACEMENT_CONTINUATION | kept | 2 | 81.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 795 | 52.86 | 0.00 | 0.00 | 0.64 | 0.00 | 9.13 | 0.00 | 0.00 | **9.77** |
| SR_FLIP_RETEST | kept | 992 | 70.47 | 0.00 | 0.00 | 0.03 | 0.00 | 0.26 | 0.00 | 0.00 | **0.29** |
| TREND_PULLBACK_EMA | filtered | 1 | 64.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 14 | 75.13 | 0.00 | 0.00 | 1.37 | 0.00 | 0.00 | 0.00 | 0.00 | **1.37** |
| VOLUME_SURGE_BREAKOUT | filtered | 13 | 59.87 | 0.00 | 0.00 | 0.00 | 0.00 | 5.55 | 0.00 | 0.00 | **5.55** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 67.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=220 (70.1%) | PREMATURE=46 (14.6%) | NEUTRAL=48 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=5
- **Net-helping** — invalidation saved on 174 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 23 | 5 | 1 | 0 |
| ema_crossover | 5 | 0 | 1 | 0 |
| momentum_loss | 96 | 21 | 16 | 0 |
| regime_shift | 60 | 9 | 27 | 0 |
| trailing_invalidation | 36 | 11 | 3 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 24 | 5 | 4 | 0 |
| FAILED_AUCTION_RECLAIM | 44 | 2 | 19 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 50 | 13 | 8 | 0 |
| SR_FLIP_RETEST | 87 | 25 | 14 | 0 |
| TREND_PULLBACK_EMA | 5 | 1 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 5 | 0 | 1 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 23 | 5 | 1 | 7.6 | 9.5 | -0.06 | **TUNE** — marginal: avg -0.06R/kill across 29 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 5 | 0 | 1 | 3.5 | 0.0 | +0.59 | **INSUFFICIENT_SAMPLE** — only 6 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 96 | 21 | 16 | 74.3 | 28.7 | +0.34 | **KEEP** — net-helping: avg +0.34R/kill across 133 kills (saved 74.3R vs missed 28.7R) |
| regime_shift | 60 | 9 | 27 | 41.4 | 12.5 | +0.30 | **KEEP** — net-helping: avg +0.30R/kill across 96 kills (saved 41.4R vs missed 12.5R) |
| trailing_invalidation | 36 | 11 | 3 | 30.6 | 16.9 | +0.27 | **KEEP** — net-helping: avg +0.27R/kill across 50 kills (saved 30.6R vs missed 16.9R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `490494`
- `Path funnel` emissions: `7`
- `Regime distribution` emissions: `7`
- `QUIET_SCALP_BLOCK` events: `1151`
- `confidence_gate` events: `3198`
- `free_channel_post` events: `109`
- `pre_tp_fire` events: `45`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **45**
- Avg resolved threshold: **0.338%** raw → avg net **+2.68%** @ 10x
- Avg time-to-fire from dispatch: **349s**
- By threshold source: stamped=45

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 24 | 0.263% | +1.92% | 389 | stamped=24 |
| LIQUIDITY_SWEEP_REVERSAL | 9 | 0.533% | +4.63% | 312 | stamped=9 |
| FAILED_AUCTION_RECLAIM | 8 | 0.280% | +2.10% | 398 | stamped=8 |
| POST_DISPLACEMENT_CONTINUATION | 2 | 0.562% | +4.92% | 46 | stamped=2 |
| DIVERGENCE_CONTINUATION | 1 | 0.409% | +3.39% | 45 | stamped=1 |
| TREND_PULLBACK_EMA | 1 | 0.354% | +2.84% | 261 | stamped=1 |
- Top symbols: JTOUSDT=6, ENAUSDT=5, OPGUSDT=3, PUMPUSDT=3, APTUSDT=3, FILUSDT=3, XLMUSDT=3, GENIUSUSDT=2, NEARUSDT=2, NOMUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **4**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 4 | 15541 | 18813 | 24801 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **109**

| Source | Count |
|---|---:|
| signal_close | 47 |
| pre_tp | 45 |
| regime_shift | 14 |
| signal_highlight | 3 |

- By severity: HIGH=109

## Dependency readiness
- cvd: presence[present=47870] state[populated=47870] buckets[few=2, many=47852, some=16] sources[none] quality[none]
- funding_rate: presence[absent=1299, present=46571] state[empty=1299, populated=46571] buckets[few=46571, none=1299] sources[none] quality[none]
- liquidation_clusters: presence[absent=27725, present=20145] state[empty=27725, populated=20145] buckets[few=15760, none=27725, some=4385] sources[none] quality[none]
- oi_snapshot: presence[absent=334, present=47536] state[empty=334, populated=47536] buckets[few=95, many=46896, none=334, some=545] sources[none] quality[none]
- order_book: presence[absent=38781, present=9089] state[populated=9089, unavailable=38781] buckets[few=9089, none=38781] sources[book_ticker=9089, unavailable=38781] quality[none=38781, top_of_book_only=9089]
- orderblocks: presence[absent=47870] state[empty=47870] buckets[none=47870] sources[not_implemented=47870] quality[none]
- recent_ticks: presence[present=47870] state[populated=47870] buckets[many=47870] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `28.821603059768677` sec
- Median create→first breach: `532.8463459014893` sec
- Median create→terminal: `519.0226635932922` sec
- Median first breach→terminal: `6.263242959976196` sec
- Fast-failure buckets: `{"under_120s": {"count": 8, "pct": 17.0}, "under_180s": {"count": 11, "pct": 23.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 6, "pct": 12.8}}`
- ~3 minute terminal-close behavior: `{"count": 11, "pct": 10.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 2 | 0.0 | 50.0 | 0.0 | 50.0 | -0.2401 | 270.601665019989 | 220.67235100269318 |
| FAILED_AUCTION_RECLAIM | 27 | 27 | 0.0 | 3.7 | 0.0 | 29.6 | 0.0561 | 833.7787239551544 | 247.39436602592468 |
| LIQUIDITY_SWEEP_REVERSAL | 19 | 19 | 0.0 | 10.5 | 0.0 | 47.4 | 0.0026 | 479.71113193035126 | 534.3202831745148 |
| POST_DISPLACEMENT_CONTINUATION | 2 | 2 | 0.0 | 0.0 | 0.0 | 100.0 | 0.2812 | 63.311697483062744 | 64.61093437671661 |
| SR_FLIP_RETEST | 56 | 56 | 0.0 | 10.7 | 0.0 | 42.9 | -0.036 | 664.8780739307404 | 645.4128850698471 |
| TREND_PULLBACK_EMA | 3 | 3 | 0.0 | 33.3 | 0.0 | 33.3 | -0.3787 | 823.9151701927185 | 883.4844799041748 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1106 | None | 268.5658469200134 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 4523 | 155 | 1274 | 0.0 | 10.7 | 664.8780739307404 | 645.4128850698471 | 3249 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 529 | 4 | 518 | 0.0 | 33.3 | 823.9151701927185 | 883.4844799041748 | 11 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-13`
- Gating Δ: `-1932`
- No-generation Δ: `-370895`
- Fast failures Δ: `-3`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.4065, "current_avg_pnl": -0.2401, "current_win_rate": 0.0, "previous_avg_pnl": 0.1664, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1942, "current_avg_pnl": 0.0561, "current_win_rate": 0.0, "previous_avg_pnl": -0.1381, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0801, "current_avg_pnl": 0.0026, "current_win_rate": 0.0, "previous_avg_pnl": -0.0775, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0697, "current_avg_pnl": -0.036, "current_win_rate": 0.0, "previous_avg_pnl": 0.0337, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.4853, "current_avg_pnl": -0.3787, "current_win_rate": 0.0, "previous_avg_pnl": 0.1066, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": 0.2207, "current_avg_pnl": 0.1106, "current_win_rate": 0.0, "previous_avg_pnl": -0.1101, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": 1345, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 227.12, "median_terminal_delta_sec": 202.05, "sl_rate_delta": 4.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -25, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 227.78, "median_terminal_delta_sec": -40.54, "sl_rate_delta": 33.3, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
