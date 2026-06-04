# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `60` sec (warning=False)
- Latest performance record age: `814` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 762 | 762 | 173 | 13 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6426 | 6426 | 5302 | 48 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 33797 | 33550 | 251 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 30889 | 30893 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 30805 | 28878 | 2009 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 30902 | 29583 | 1350 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 33925 | 33826 | 107 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 33775 | 33774 | 3 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 30934 | 30938 | 11 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 33803 | 33805 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 30894 | 30898 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 30800 | 30805 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 30672 | 28780 | 2012 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 30564 | 28243 | 2385 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 30628 | 30395 | 248 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 33784 | 33677 | 120 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 33777 | 33730 | 53 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4028 | 4028 | 2902 | 78 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 390 | 390 | 315 | 3 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 10 | 10 | 10 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 7140 | 7140 | 6056 | 137 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 11 | 0 | low-sample (none) |
| MOMENTUM_EXPANSION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 6 | 6 | 6 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 6942 | 6942 | 2969 | 244 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 885 | 885 | 838 | 10 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 369 | 369 | 116 | 10 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 545 | 545 | 510 | 4 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=33550): breakout_not_found=22910, retest_proximity_failed=4780, basic_filters_failed=4355, volume_spike_missing=1171, ema_alignment_reject=293, missing_fvg_or_orderblock=41
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=30893): cls_disabled_merged_into_lsr=30893
- **EVAL::DIVERGENCE_CONTINUATION** (total=28878): cvd_divergence_failed=12452, h1_trend_not_aligned=7352, basic_filters_failed=4031, ema_alignment_reject=3729, retest_proximity_failed=1009, regime_blocked=187, missing_fvg_or_orderblock=118
- **EVAL::FAILED_AUCTION_RECLAIM** (total=29583): auction_not_detected=13169, reclaim_hold_failed=5585, tail_too_small=4922, basic_filters_failed=3782, regime_blocked=2125
- **EVAL::FUNDING_EXTREME** (total=33826): funding_not_extreme=27559, basic_filters_failed=4225, missing_funding_rate=800, ema_alignment_reject=759, rsi_reject=246, cvd_divergence_failed=160, momentum_reject=75, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=33774): cascade_threshold_not_met=28660, basic_filters_failed=4355, cvd_divergence_failed=399, rsi_reject=332, missing_fvg_or_orderblock=22, volume_spike_missing=6
- **EVAL::MA_CROSS_TREND_SHIFT** (total=30938): no_ma_cross=26293, basic_filters_failed=4031, ma_cross_cooldown=614
- **EVAL::OPENING_RANGE_BREAKOUT** (total=33805): feature_disabled=33805
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=30898): regime_blocked=17705, breakout_not_found=7385, ema_alignment_reject=2304, adx_reject=1803, basic_filters_failed=1701
- **EVAL::QUIET_COMPRESSION_BREAK** (total=30805): regime_blocked=15275, compression_not_detected=13449, basic_filters_failed=2081
- **EVAL::SR_FLIP_RETEST** (total=28780): retest_out_of_zone=9942, reclaim_hold_failed=6502, flip_close_not_confirmed=5118, basic_filters_failed=3782, regime_blocked=2115, wick_quality_failed=927, ema_alignment_reject=259, missing_fvg_or_orderblock=135
- **EVAL::STANDARD** (total=28243): adx_reject=9333, momentum_reject=5553, ema_alignment_reject=4114, basic_filters_failed=3185, macd_reject=3156, sweeps_not_detected=2440, invalid_sl_geometry=408, rsi_reject=47, mtf_reject=7
- **EVAL::TREND_PULLBACK** (total=30395): h1_trend_not_aligned=8640, ema_alignment_reject=5862, h1_pullback_not_confirmed=5205, ema_not_tested_prev=3246, no_ema_reclaim_close=2196, basic_filters_failed=1954, body_conviction_fail=1083, rsi_reject=1069, prev_already_below_emas=332, regime_blocked=232, prev_already_above_emas=179, no_prev_low_break=163, momentum_flat=106, no_prev_high_break=92, ema21_not_tagged=23, missing_fvg_or_orderblock=10, momentum_reject=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=33677): breakout_not_found=22950, retest_proximity_failed=4593, basic_filters_failed=4355, volume_spike_missing=1309, ema_alignment_reject=356, missing_fvg_or_orderblock=108, rsi_reject=6
- **EVAL::WHALE_MOMENTUM** (total=33730): momentum_reject=24999, recent_ticks_insufficient=7427, basic_filters_failed=1304

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 41181 | 33.4% |
| TRENDING_DOWN | 31889 | 25.9% |
| TRENDING_UP | 22656 | 18.4% |
| QUIET | 19488 | 15.8% |
| VOLATILE | 8114 | 6.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **340**
- Average confidence gap to threshold: **14.86** (samples=340) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: CLUSDT=22, 1000PEPEUSDT=21, SUIUSDT=20, BZUSDT=19, INTCUSDT=18, TRXUSDT=17, AVAXUSDT=16, BNBUSDT=15, JTOUSDT=12, MUUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 110 |
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 6 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 164 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 181 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 12 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 300 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 218 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 58 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 476 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 222 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 116 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 461 |
| SR_FLIP_RETEST | filtered | min_confidence | 898 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 134 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2065 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 42 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 45 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 11 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 25 |
| WHALE_MOMENTUM | filtered | min_confidence | 19 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 2 |
| WHALE_MOMENTUM | kept | min_confidence_pass | 16 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 116 | 59.33 | 65.00 | 5.67 | 21.01 | 19.38 | 19.52 | 0.00 | 8.76 |
| BREAKDOWN_SHORT | kept | 164 | 68.30 | 65.00 | -3.30 | 21.34 | 19.61 | 19.34 | 0.00 | 1.79 |
| DIVERGENCE_CONTINUATION | filtered | 193 | 58.42 | 65.00 | 6.58 | 20.65 | 19.54 | 18.00 | 3.64 | 9.72 |
| DIVERGENCE_CONTINUATION | kept | 300 | 69.95 | 65.00 | -4.95 | 21.03 | 19.79 | 18.17 | 2.31 | -0.55 |
| FAILED_AUCTION_RECLAIM | filtered | 276 | 55.21 | 65.00 | 9.79 | 20.79 | 19.09 | 20.00 | 4.16 | 4.65 |
| FAILED_AUCTION_RECLAIM | kept | 476 | 71.47 | 65.00 | -6.47 | 21.52 | 19.22 | 20.00 | 4.08 | 0.73 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 52.23 | 65.00 | 12.77 | 20.07 | 19.93 | 17.00 | 0.67 | 2.07 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 71.70 | 65.00 | -6.70 | 22.46 | 19.76 | 17.00 | 0.80 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 338 | 55.13 | 65.00 | 9.87 | 21.25 | 19.43 | 18.20 | 2.59 | 10.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 461 | 70.30 | 65.00 | -5.30 | 21.13 | 19.54 | 17.84 | 2.38 | 0.67 |
| SR_FLIP_RETEST | filtered | 1032 | 55.06 | 65.00 | 9.94 | 20.97 | 19.88 | 15.95 | 1.83 | 8.44 |
| SR_FLIP_RETEST | kept | 2065 | 72.55 | 65.00 | -7.55 | 21.39 | 19.91 | 15.89 | 2.05 | -0.30 |
| TREND_PULLBACK_EMA | kept | 42 | 74.35 | 65.00 | -9.35 | 20.48 | 19.70 | 17.53 | 5.49 | -0.56 |
| VOLUME_SURGE_BREAKOUT | filtered | 56 | 52.81 | 65.00 | 12.19 | 20.66 | 18.64 | 19.78 | 3.23 | 7.50 |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 70.11 | 65.00 | -5.11 | 21.05 | 19.32 | 19.86 | 3.24 | 4.68 |
| WHALE_MOMENTUM | filtered | 21 | 61.22 | 65.00 | 3.78 | 24.30 | 20.00 | 17.00 | 0.00 | 10.55 |
| WHALE_MOMENTUM | kept | 16 | 69.81 | 65.00 | -4.81 | 23.30 | 19.69 | 17.00 | 0.00 | 8.01 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 116 | 59.33 | 21.53 | 14.22 | 6.72 | 13.18 | 5.23 | 7.18 | 0.00 |
| BREAKDOWN_SHORT | kept | 164 | 68.30 | 23.73 | 15.01 | 5.18 | 12.84 | 5.81 | 7.62 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 193 | 58.42 | 21.19 | 13.85 | 6.70 | 11.88 | 5.38 | 7.57 | 3.64 |
| DIVERGENCE_CONTINUATION | kept | 300 | 69.95 | 21.35 | 15.87 | 4.79 | 12.09 | 5.70 | 8.83 | 2.31 |
| FAILED_AUCTION_RECLAIM | filtered | 276 | 55.21 | 22.02 | 16.57 | 4.75 | 11.50 | 5.84 | 4.87 | 4.16 |
| FAILED_AUCTION_RECLAIM | kept | 476 | 71.47 | 22.20 | 15.63 | 4.76 | 11.79 | 6.32 | 7.42 | 4.08 |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 52.23 | 25.00 | 8.00 | 6.00 | 17.00 | 8.33 | 4.30 | 0.67 |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 71.70 | 21.80 | 16.00 | 4.20 | 15.80 | 7.90 | 5.20 | 0.80 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 338 | 55.13 | 21.70 | 14.15 | 7.53 | 12.84 | 5.52 | 6.49 | 2.59 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 461 | 70.30 | 22.91 | 14.81 | 4.99 | 12.81 | 5.46 | 7.65 | 2.38 |
| SR_FLIP_RETEST | filtered | 1032 | 55.06 | 20.15 | 16.70 | 5.05 | 13.82 | 5.89 | 6.59 | 1.83 |
| SR_FLIP_RETEST | kept | 2065 | 72.55 | 21.42 | 17.25 | 4.83 | 13.76 | 5.90 | 8.69 | 2.05 |
| TREND_PULLBACK_EMA | kept | 42 | 74.35 | 17.40 | 18.00 | 4.57 | 13.76 | 6.51 | 9.35 | 5.49 |
| VOLUME_SURGE_BREAKOUT | filtered | 56 | 52.81 | 21.29 | 13.00 | 8.62 | 14.50 | 5.07 | 4.78 | 3.23 |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 70.11 | 22.44 | 16.48 | 5.88 | 14.04 | 4.40 | 8.32 | 3.24 |
| WHALE_MOMENTUM | filtered | 21 | 61.22 | 24.24 | 17.05 | 3.71 | 14.00 | 5.50 | 7.27 | 0.00 |
| WHALE_MOMENTUM | kept | 16 | 69.81 | 23.38 | 17.38 | 10.50 | 13.38 | 5.97 | 7.23 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 116 | 59.33 | 0.00 | 0.00 | 0.83 | 0.00 | 2.52 | 0.00 | 0.00 | 0.76 | **4.11** |
| BREAKDOWN_SHORT | kept | 164 | 68.30 | 0.00 | 0.00 | 0.06 | 0.00 | 0.26 | 0.04 | 0.00 | 0.02 | **0.38** |
| DIVERGENCE_CONTINUATION | filtered | 193 | 58.42 | 0.00 | 0.00 | 0.51 | 0.00 | 2.57 | 0.00 | 0.00 | 0.00 | **3.08** |
| DIVERGENCE_CONTINUATION | kept | 300 | 69.95 | 0.00 | 0.00 | 0.19 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.37** |
| FAILED_AUCTION_RECLAIM | filtered | 276 | 55.21 | 0.00 | 0.00 | 1.31 | 0.00 | 1.57 | 0.00 | 0.00 | 0.00 | **2.88** |
| FAILED_AUCTION_RECLAIM | kept | 476 | 71.47 | 0.00 | 0.00 | 0.32 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.34** |
| FUNDING_EXTREME_SIGNAL | filtered | 3 | 52.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | kept | 5 | 71.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 338 | 55.13 | 0.04 | 0.00 | 1.87 | 0.00 | 6.94 | 0.09 | 0.00 | 0.00 | **8.94** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 461 | 70.30 | 0.00 | 0.00 | 0.20 | 0.00 | 0.27 | 0.03 | 0.00 | 0.00 | **0.50** |
| SR_FLIP_RETEST | filtered | 1032 | 55.06 | 0.00 | 0.00 | 0.62 | 0.00 | 2.03 | 0.05 | 0.00 | 0.56 | **3.26** |
| SR_FLIP_RETEST | kept | 2065 | 72.55 | 0.00 | 0.00 | 0.10 | 0.00 | 0.27 | 0.02 | 0.00 | 0.00 | **0.39** |
| TREND_PULLBACK_EMA | kept | 42 | 74.35 | 0.00 | 0.00 | 0.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.11** |
| VOLUME_SURGE_BREAKOUT | filtered | 56 | 52.81 | 0.00 | 0.00 | 1.09 | 0.00 | 2.16 | 0.00 | 0.00 | 1.22 | **4.47** |
| VOLUME_SURGE_BREAKOUT | kept | 25 | 70.11 | 0.00 | 0.00 | 2.02 | 0.00 | 0.34 | 0.00 | 0.00 | 0.00 | **2.36** |
| WHALE_MOMENTUM | filtered | 21 | 61.22 | 0.00 | 0.00 | 0.00 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **1.03** |
| WHALE_MOMENTUM | kept | 16 | 69.81 | 0.00 | 0.00 | 0.00 | 0.00 | 0.45 | 0.00 | 0.00 | 0.00 | **0.45** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=99 (81.8%) | PREMATURE=16 (13.2%) | NEUTRAL=6 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 83 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 32 | 6 | 0 | 0 |
| momentum_loss | 37 | 7 | 1 | 0 |
| regime_shift | 8 | 0 | 1 | 0 |
| trailing_invalidation | 22 | 3 | 4 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 6 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 9 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 11 | 0 | 1 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 31 | 5 | 2 | 0 |
| SR_FLIP_RETEST | 35 | 9 | 2 | 0 |
| TREND_PULLBACK_EMA | 3 | 2 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 32 | 6 | 0 | 12.2 | 11.4 | +0.02 | **TUNE** — marginal: avg +0.02R/kill across 38 kills — consider per-setup exemption or threshold adjustment, not full drop |
| momentum_loss | 37 | 7 | 1 | 24.2 | 11.0 | +0.29 | **KEEP** — net-helping: avg +0.29R/kill across 45 kills (saved 24.2R vs missed 11.0R) |
| regime_shift | 8 | 0 | 1 | 4.9 | 0.0 | +0.55 | **INSUFFICIENT_SAMPLE** — only 9 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 22 | 3 | 4 | 18.8 | 3.6 | +0.52 | **KEEP** — net-helping: avg +0.52R/kill across 29 kills (saved 18.8R vs missed 3.6R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `975257`
- `Path funnel` emissions: `17`
- `Regime distribution` emissions: `17`
- `QUIET_SCALP_BLOCK` events: `340`
- `confidence_gate` events: `5589`
- `free_channel_post` events: `121`
- `pre_tp_fire` events: `57`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **57**
- Avg resolved threshold: **0.561%** raw → avg net **+4.91%** @ 10x
- Avg time-to-fire from dispatch: **218s**
- By threshold source: stamped=57

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 24 | 0.477% | +4.07% | 247 | stamped=24 |
| LIQUIDITY_SWEEP_REVERSAL | 22 | 0.665% | +5.95% | 164 | stamped=22 |
| FAILED_AUCTION_RECLAIM | 4 | 0.494% | +4.24% | 374 | stamped=4 |
| DIVERGENCE_CONTINUATION | 4 | 0.505% | +4.36% | 130 | stamped=4 |
| TREND_PULLBACK_EMA | 3 | 0.642% | +5.72% | 298 | stamped=3 |
- Top symbols: FILUSDT=8, APTUSDT=4, HOMEUSDT=4, 1000PEPEUSDT=4, BIOUSDT=3, APRUSDT=3, PLAYUSDT=3, XPLUSDT=3, OPUSDT=2, EPICUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **121**

| Source | Count |
|---|---:|
| signal_close | 61 |
| pre_tp | 57 |
| regime_shift | 2 |
| signal_highlight | 1 |

- By severity: HIGH=121

## Dependency readiness
- cvd: presence[present=108178] state[populated=108178] buckets[many=108178] sources[none] quality[none]
- funding_rate: presence[absent=2497, present=105681] state[empty=2497, populated=105681] buckets[few=105681, none=2497] sources[none] quality[none]
- liquidation_clusters: presence[absent=40012, present=68166] state[empty=40012, populated=68166] buckets[few=51400, none=40012, some=16766] sources[none] quality[none]
- oi_snapshot: presence[absent=570, present=107608] state[empty=570, populated=107608] buckets[many=107608, none=570] sources[none] quality[none]
- order_book: presence[absent=54735, present=53443] state[populated=53443, unavailable=54735] buckets[few=53443, none=54735] sources[book_ticker=53443, unavailable=54735] quality[none=54735, top_of_book_only=53443]
- orderblocks: presence[absent=108178] state[empty=108178] buckets[none=108178] sources[not_implemented=108178] quality[none]
- recent_ticks: presence[absent=199, present=107979] state[empty=199, populated=107979] buckets[many=107979, none=199] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `22.27033495903015` sec
- Median create→first breach: `309.84516191482544` sec
- Median create→terminal: `266.81870102882385` sec
- Median first breach→terminal: `3.918915033340454` sec
- Fast-failure buckets: `{"under_120s": {"count": 16, "pct": 26.2}, "under_180s": {"count": 25, "pct": 41.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 9, "pct": 14.8}}`
- ~3 minute terminal-close behavior: `{"count": 13, "pct": 10.9}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 4 | 0.0 | 25.0 | 0.0 | 0.0 | -0.4946 | 272.99030208587646 | 321.91978204250336 |
| DIVERGENCE_CONTINUATION | 10 | 10 | 0.0 | 10.0 | 0.0 | 40.0 | 0.2492 | 380.6085685491562 | 168.09121811389923 |
| FAILED_AUCTION_RECLAIM | 7 | 7 | 0.0 | 0.0 | 0.0 | 57.1 | -0.0611 | 140.78558802604675 | 246.47686314582825 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -1.9058 | None | 133.67719101905823 |
| LIQUIDITY_SWEEP_REVERSAL | 36 | 36 | 0.0 | 0.0 | 0.0 | 61.1 | 0.0259 | 318.05364418029785 | 252.60304594039917 |
| SR_FLIP_RETEST | 54 | 54 | 0.0 | 14.8 | 0.0 | 44.4 | -0.1635 | 242.16693246364594 | 266.77277851104736 |
| TREND_PULLBACK_EMA | 6 | 6 | 0.0 | 16.7 | 0.0 | 50.0 | -0.1879 | 865.8979154825211 | 1059.017224431038 |
| WHALE_MOMENTUM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.3165 | None | 141.22114205360413 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 6942 | 244 | 2969 | 0.0 | 14.8 | 242.16693246364594 | 266.77277851104736 | 3973 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 885 | 10 | 838 | 0.0 | 16.7 | 865.8979154825211 | 1059.017224431038 | 47 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-101`
- Gating Δ: `1303`
- No-generation Δ: `44671`
- Fast failures Δ: `8`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.2643, "current_avg_pnl": -0.4946, "current_win_rate": 0.0, "previous_avg_pnl": -0.2303, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1963, "current_avg_pnl": 0.2492, "current_win_rate": 0.0, "previous_avg_pnl": 0.0529, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0024, "current_avg_pnl": -0.0611, "current_win_rate": 0.0, "previous_avg_pnl": -0.0635, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.013, "current_avg_pnl": 0.0259, "current_win_rate": 0.0, "previous_avg_pnl": 0.0389, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.1869, "current_avg_pnl": -0.1635, "current_win_rate": 0.0, "previous_avg_pnl": 0.0234, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.2624, "current_avg_pnl": -0.1879, "current_win_rate": 0.0, "previous_avg_pnl": 0.0745, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -87, "geometry_changed_delta": 0, "geometry_preserved_delta": 249, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -206.24, "median_terminal_delta_sec": -187.28, "sl_rate_delta": 5.4, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -13, "geometry_changed_delta": 0, "geometry_preserved_delta": -67, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 511.76, "median_terminal_delta_sec": 564.8, "sl_rate_delta": 16.7, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **MA_CROSS_TREND_SHIFT**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
