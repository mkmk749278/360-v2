# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `700` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2482 | 2482 | 2230 | 4 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 20337 | 20337 | 19902 | 42 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 278655 | 276173 | 2482 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 261791 | 261791 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 261791 | 241454 | 20337 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 261791 | 251480 | 10311 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 278655 | 278413 | 242 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 278655 | 278642 | 13 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 261791 | 261775 | 16 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 278655 | 278655 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 261791 | 261764 | 27 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 261791 | 261678 | 113 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 261791 | 238331 | 23460 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 261791 | 243094 | 18697 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 261791 | 258744 | 3047 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 278655 | 277683 | 972 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 278655 | 278655 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 10311 | 10311 | 6923 | 110 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 242 | 242 | 224 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 18697 | 18697 | 14507 | 195 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 16 | 16 | 10 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 27 | 27 | 27 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 113 | 113 | 95 | 0 | low-sample (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 23460 | 23460 | 12153 | 249 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 3047 | 3047 | 2952 | 16 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 972 | 972 | 941 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=276173): breakout_not_found=149667, basic_filters_failed=81762, retest_proximity_failed=31756, volume_spike_missing=8977, ema_alignment_reject=2459, insufficient_candles=980, missing_fvg_or_orderblock=555, rsi_reject=17
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=261791): cls_disabled_merged_into_lsr=261791
- **EVAL::DIVERGENCE_CONTINUATION** (total=241454): cvd_divergence_failed=85708, basic_filters_failed=75616, h1_trend_not_aligned=44952, ema_alignment_reject=29842, retest_proximity_failed=2920, missing_fvg_or_orderblock=1783, regime_blocked=633
- **EVAL::FAILED_AUCTION_RECLAIM** (total=251480): auction_not_detected=95639, basic_filters_failed=75616, reclaim_hold_failed=40266, tail_too_small=39867, rsi_reject=92
- **EVAL::FUNDING_EXTREME** (total=278413): funding_not_extreme=186523, basic_filters_failed=77693, missing_funding_rate=10988, ema_alignment_reject=1956, rsi_reject=702, cvd_divergence_failed=248, momentum_reject=200, missing_fvg_or_orderblock=59, insufficient_candles=44
- **EVAL::LIQUIDATION_REVERSAL** (total=278642): cascade_threshold_not_met=193505, basic_filters_failed=81937, cvd_divergence_failed=1419, rsi_reject=1021, insufficient_candles=681, volume_spike_missing=46, missing_fvg_or_orderblock=33
- **EVAL::MA_CROSS_TREND_SHIFT** (total=261775): no_ma_cross=180649, basic_filters_failed=75616, ma_cross_cooldown=5510
- **EVAL::OPENING_RANGE_BREAKOUT** (total=278655): feature_disabled=278655
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=261764): regime_blocked=200499, breakout_not_found=22066, adx_reject=14756, ema_alignment_reject=13401, basic_filters_failed=11042
- **EVAL::QUIET_COMPRESSION_BREAK** (total=261678): compression_not_detected=132764, basic_filters_failed=64574, regime_blocked=61292, breakout_not_detected=2877, volume_confirmation_failed=164, rsi_reject=7
- **EVAL::SR_FLIP_RETEST** (total=238331): basic_filters_failed=75616, reclaim_hold_failed=69884, flip_close_not_confirmed=40406, retest_out_of_zone=38559, wick_quality_failed=9356, ema_alignment_reject=2843, missing_fvg_or_orderblock=1641, rsi_reject=26
- **EVAL::STANDARD** (total=243094): adx_reject=84835, basic_filters_failed=53418, momentum_reject=51480, macd_reject=26805, sweeps_not_detected=16796, ema_alignment_reject=8405, invalid_sl_geometry=1024, rsi_reject=331
- **EVAL::TREND_PULLBACK** (total=258744): h1_trend_not_aligned=67332, ema_alignment_reject=44529, basic_filters_failed=38464, h1_pullback_not_confirmed=30336, no_ema_reclaim_close=25679, body_conviction_fail=15703, ema_not_tested_prev=14923, rsi_reject=9183, regime_blocked=3603, prev_already_below_emas=3366, no_prev_low_break=2052, prev_already_above_emas=1784, no_prev_high_break=768, momentum_flat=546, ema21_not_tagged=185, missing_fvg_or_orderblock=163, momentum_reject=128
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=277683): breakout_not_found=159260, basic_filters_failed=81762, retest_proximity_failed=23205, volume_spike_missing=6628, ema_alignment_reject=5280, insufficient_candles=980, missing_fvg_or_orderblock=435, rsi_reject=133
- **EVAL::WHALE_MOMENTUM** (total=278655): momentum_reject=206354, recent_ticks_insufficient=47463, basic_filters_failed=24838

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 246680 | 69.6% |
| TRENDING_DOWN | 61756 | 17.4% |
| TRENDING_UP | 24899 | 7.0% |
| RANGING | 21038 | 5.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1535**
- Average confidence gap to threshold: **14.02** (samples=1535) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: PENGUUSDT=68, BTCUSDT=60, BZUSDT=56, TRXUSDT=53, APRUSDT=45, LABUSDT=43, SOLUSDT=42, NEARUSDT=42, BSBUSDT=37, 币安人生USDT=37

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 70 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 87 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 13 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 257 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 313 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 139 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1578 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 672 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 89 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1335 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 18 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 2 |
| RANGE_FADE | filtered | quiet_scalp_min_confidence | 1 |
| RANGE_FADE | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 709 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 529 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2957 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 109 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 2 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 10 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 70 | 62.91 | 65.00 | 2.09 | 19.79 | 19.99 | 19.09 | 0.00 | 3.36 |
| BREAKDOWN_SHORT | kept | 87 | 69.84 | 65.00 | -4.84 | 20.67 | 19.92 | 18.09 | 0.00 | 1.86 |
| DIVERGENCE_CONTINUATION | filtered | 13 | 61.48 | 65.00 | 3.52 | 20.88 | 20.00 | 19.22 | 0.77 | 5.16 |
| DIVERGENCE_CONTINUATION | kept | 257 | 72.11 | 65.00 | -7.11 | 20.26 | 19.73 | 18.60 | 1.60 | -1.16 |
| FAILED_AUCTION_RECLAIM | filtered | 452 | 54.22 | 65.00 | 10.78 | 20.78 | 19.54 | 20.00 | 4.05 | 13.71 |
| FAILED_AUCTION_RECLAIM | kept | 1578 | 70.57 | 65.00 | -5.57 | 21.09 | 19.81 | 20.00 | 4.07 | 0.86 |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 56.90 | 65.00 | 8.10 | 20.65 | 19.90 | 17.00 | 0.50 | 14.60 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 761 | 50.98 | 65.00 | 14.02 | 20.90 | 19.62 | 15.20 | 2.74 | 14.21 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1335 | 69.41 | 65.00 | -4.41 | 21.45 | 19.60 | 15.20 | 2.26 | 0.43 |
| QUIET_COMPRESSION_BREAK | filtered | 18 | 58.24 | 65.00 | 6.76 | 19.83 | 20.00 | 20.00 | 0.00 | -0.16 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 66.20 | 65.00 | -1.20 | 18.75 | 20.00 | 20.00 | 0.00 | 0.00 |
| RANGE_FADE | filtered | 1 | 62.50 | 65.00 | 2.50 | 20.60 | 18.60 | 13.40 | 0.00 | 2.80 |
| RANGE_FADE | kept | 1 | 73.20 | 65.00 | -8.20 | 21.20 | 19.40 | 13.40 | 0.00 | 1.80 |
| SR_FLIP_RETEST | filtered | 1238 | 54.18 | 65.00 | 10.82 | 20.96 | 19.92 | 15.84 | 1.85 | 10.43 |
| SR_FLIP_RETEST | kept | 2957 | 70.77 | 65.00 | -5.77 | 21.15 | 19.94 | 15.47 | 2.14 | -0.98 |
| TREND_PULLBACK_EMA | kept | 109 | 76.83 | 65.00 | -11.83 | 20.13 | 19.66 | 18.14 | 5.52 | -1.01 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 60.70 | 65.00 | 4.30 | 21.10 | 19.90 | 20.00 | 1.50 | 7.80 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 68.05 | 65.00 | -3.05 | 20.66 | 19.89 | 20.00 | 3.20 | 3.18 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 70 | 62.91 | 20.06 | 18.00 | 3.86 | 12.40 | 5.05 | 6.90 | 0.00 |
| BREAKDOWN_SHORT | kept | 87 | 69.84 | 23.44 | 18.00 | 3.48 | 12.79 | 5.03 | 8.91 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 13 | 61.48 | 20.08 | 18.00 | 3.69 | 12.15 | 5.77 | 8.95 | 0.77 |
| DIVERGENCE_CONTINUATION | kept | 257 | 72.11 | 21.79 | 18.00 | 4.80 | 11.51 | 5.63 | 9.07 | 1.60 |
| FAILED_AUCTION_RECLAIM | filtered | 452 | 54.22 | 20.53 | 14.56 | 8.40 | 10.96 | 6.10 | 6.72 | 4.05 |
| FAILED_AUCTION_RECLAIM | kept | 1578 | 70.57 | 22.38 | 14.36 | 4.69 | 11.76 | 6.58 | 7.59 | 4.07 |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 56.90 | 21.00 | 8.00 | 9.00 | 15.50 | 7.50 | 10.00 | 0.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 761 | 50.98 | 22.57 | 14.04 | 6.61 | 12.29 | 5.64 | 6.50 | 2.74 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1335 | 69.41 | 23.84 | 14.15 | 3.97 | 12.37 | 5.83 | 7.46 | 2.26 |
| QUIET_COMPRESSION_BREAK | filtered | 18 | 58.24 | 17.89 | 18.00 | 7.17 | 14.83 | 6.75 | 4.44 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 66.20 | 17.00 | 18.00 | 6.00 | 14.00 | 8.50 | 2.70 | 0.00 |
| RANGE_FADE | filtered | 1 | 62.50 | 17.00 | 18.00 | 3.00 | 17.00 | 5.00 | 5.30 | 0.00 |
| RANGE_FADE | kept | 1 | 73.20 | 25.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 1238 | 54.18 | 20.63 | 13.73 | 6.46 | 13.77 | 6.13 | 7.37 | 1.85 |
| SR_FLIP_RETEST | kept | 2957 | 70.77 | 22.11 | 15.23 | 4.35 | 13.49 | 5.91 | 8.45 | 2.14 |
| TREND_PULLBACK_EMA | kept | 109 | 76.83 | 19.80 | 18.00 | 3.94 | 15.38 | 5.34 | 9.36 | 5.52 |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 60.70 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 10.00 | 1.50 |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 68.05 | 25.00 | 9.00 | 3.60 | 15.20 | 5.50 | 9.73 | 3.20 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 70 | 62.91 | 0.00 | 0.00 | 0.07 | 0.00 | 0.00 | 0.00 | 0.00 | **0.07** |
| BREAKDOWN_SHORT | kept | 87 | 69.84 | 0.00 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 0.00 | **0.06** |
| DIVERGENCE_CONTINUATION | filtered | 13 | 61.48 | 0.00 | 0.00 | 3.69 | 0.00 | 0.55 | 0.00 | 0.00 | **4.24** |
| DIVERGENCE_CONTINUATION | kept | 257 | 72.11 | 0.00 | 0.00 | 0.15 | 0.00 | 0.11 | 0.00 | 0.00 | **0.26** |
| FAILED_AUCTION_RECLAIM | filtered | 452 | 54.22 | 0.00 | 0.00 | 0.93 | 0.00 | 11.10 | 0.12 | 0.00 | **12.15** |
| FAILED_AUCTION_RECLAIM | kept | 1578 | 70.57 | 0.00 | 0.00 | 0.01 | 0.00 | 0.22 | 0.00 | 0.00 | **0.23** |
| FUNDING_EXTREME_SIGNAL | filtered | 4 | 56.90 | 0.00 | 0.00 | 9.60 | 0.00 | 0.00 | 0.00 | 0.00 | **9.60** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 761 | 50.98 | 0.00 | 0.00 | 4.26 | 0.00 | 8.30 | 0.00 | 0.00 | **12.56** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1335 | 69.41 | 0.00 | 0.00 | 0.03 | 0.00 | 0.04 | 0.00 | 0.00 | **0.07** |
| QUIET_COMPRESSION_BREAK | filtered | 18 | 58.24 | 0.00 | 0.00 | 0.00 | 0.00 | 1.67 | 0.00 | 0.00 | **1.67** |
| QUIET_COMPRESSION_BREAK | kept | 2 | 66.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| RANGE_FADE | filtered | 1 | 62.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| RANGE_FADE | kept | 1 | 73.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 1238 | 54.18 | 0.03 | 0.00 | 0.84 | 0.00 | 6.26 | 0.05 | 0.00 | **7.18** |
| SR_FLIP_RETEST | kept | 2957 | 70.77 | 0.00 | 0.00 | 0.06 | 0.00 | 0.15 | 0.00 | 0.00 | **0.21** |
| TREND_PULLBACK_EMA | kept | 109 | 76.83 | 0.00 | 0.00 | 0.04 | 0.00 | 0.13 | 0.00 | 0.00 | **0.17** |
| VOLUME_SURGE_BREAKOUT | filtered | 2 | 60.70 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| VOLUME_SURGE_BREAKOUT | kept | 10 | 68.05 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | **0.48** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=145 (68.7%) | PREMATURE=17 (8.1%) | NEUTRAL=49 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=3
- **Net-helping** — invalidation saved on 128 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 5 | 0 | 1 | 0 |
| momentum_loss | 105 | 9 | 29 | 0 |
| regime_shift | 35 | 8 | 19 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 9 | 0 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 26 | 3 | 7 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 40 | 8 | 17 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 63 | 6 | 22 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| ema_crossover | 5 | 0 | 1 | 3.1 | 0.0 | +0.52 | **INSUFFICIENT_SAMPLE** — only 6 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 105 | 9 | 29 | 54.5 | 13.7 | +0.28 | **KEEP** — net-helping: avg +0.28R/kill across 143 kills (saved 54.5R vs missed 13.7R) |
| regime_shift | 35 | 8 | 19 | 22.1 | 10.5 | +0.19 | **KEEP** — net-helping: avg +0.19R/kill across 62 kills (saved 22.1R vs missed 10.5R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `2159412`
- `Path funnel` emissions: `49`
- `Regime distribution` emissions: `49`
- `QUIET_SCALP_BLOCK` events: `1535`
- `confidence_gate` events: `8895`
- `free_channel_post` events: `243`
- `pre_tp_fire` events: `115`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **115**
- Avg resolved threshold: **0.345%** raw → avg net **+2.75%** @ 10x
- Avg time-to-fire from dispatch: **336s**
- By threshold source: stamped=115

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 50 | 0.332% | +2.62% | 340 | stamped=50 |
| LIQUIDITY_SWEEP_REVERSAL | 40 | 0.388% | +3.18% | 294 | stamped=40 |
| FAILED_AUCTION_RECLAIM | 16 | 0.280% | +2.10% | 495 | stamped=16 |
| DIVERGENCE_CONTINUATION | 5 | 0.332% | +2.62% | 294 | stamped=5 |
| TREND_PULLBACK_EMA | 4 | 0.349% | +2.79% | 129 | stamped=4 |
- Top symbols: EWYUSDT=7, KITEUSDT=6, GOATUSDT=6, ATUSDT=6, ONDOUSDT=5, CHZUSDT=5, PLAYUSDT=5, AIAUSDT=5, 币安人生USDT=4, NEARUSDT=4

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **8**
- Total REST-fallback activations: **2**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 3 | 3702 | 3702 | 35798 | 0 |
| futures_liq | 5 | 2486 | 2573 | 3128 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 2 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **243**

| Source | Count |
|---|---:|
| pre_tp | 115 |
| signal_close | 115 |
| regime_shift | 11 |
| signal_highlight | 2 |

- By severity: HIGH=243

## Dependency readiness
- cvd: presence[present=278657] state[populated=278657] buckets[few=14, many=278599, some=44] sources[none] quality[none]
- funding_rate: presence[absent=10990, present=267667] state[empty=10990, populated=267667] buckets[few=267667, none=10990] sources[none] quality[none]
- liquidation_clusters: presence[absent=155422, present=123235] state[empty=155422, populated=123235] buckets[few=103224, none=155422, some=20011] sources[none] quality[none]
- oi_snapshot: presence[absent=6406, present=272251] state[empty=6406, populated=272251] buckets[few=191, many=270290, none=6406, some=1770] sources[none] quality[none]
- order_book: presence[absent=69020, present=209637] state[populated=209637, unavailable=69020] buckets[few=209637, none=69020] sources[book_ticker=209637, unavailable=69020] quality[none=69020, top_of_book_only=209637]
- orderblocks: presence[absent=278657] state[empty=278657] buckets[none=278657] sources[not_implemented=278657] quality[none]
- recent_ticks: presence[absent=980, present=277677] state[empty=980, populated=277677] buckets[many=277677, none=980] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `12.352458953857422` sec
- Median create→first breach: `464.99050211906433` sec
- Median create→terminal: `671.9911289215088` sec
- Median first breach→terminal: `12.820456981658936` sec
- Fast-failure buckets: `{"under_120s": {"count": 18, "pct": 15.7}, "under_180s": {"count": 24, "pct": 20.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 11, "pct": 9.6}}`
- ~3 minute terminal-close behavior: `{"count": 10, "pct": 5.3}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.2366 | None | 609.244234085083 |
| DIVERGENCE_CONTINUATION | 10 | 10 | 0.0 | 30.0 | 0.0 | 50.0 | -0.0626 | 174.90172696113586 | 348.1752370595932 |
| FAILED_AUCTION_RECLAIM | 27 | 27 | 0.0 | 0.0 | 0.0 | 59.3 | 0.0423 | 958.8133804798126 | 920.0869140625 |
| LIQUIDITY_SWEEP_REVERSAL | 62 | 62 | 0.0 | 4.8 | 0.0 | 64.5 | 0.0342 | 567.6710430383682 | 708.4697771072388 |
| SR_FLIP_RETEST | 83 | 83 | 0.0 | 8.4 | 0.0 | 60.2 | 0.0152 | 486.97021996974945 | 656.1840269565582 |
| TREND_PULLBACK_EMA | 6 | 6 | 0.0 | 16.7 | 0.0 | 66.7 | -0.1195 | 159.597501039505 | 240.96404659748077 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 23460 | 249 | 12153 | 0.0 | 8.4 | 486.97021996974945 | 656.1840269565582 | 11307 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 3047 | 16 | 2952 | 0.0 | 16.7 | 159.597501039505 | 240.96404659748077 | 95 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `126`
- Gating Δ: `-4809`
- No-generation Δ: `-108130`
- Fast failures Δ: `-10`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.296, "current_avg_pnl": -0.2366, "current_win_rate": 0.0, "previous_avg_pnl": 0.0594, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.2955, "current_avg_pnl": -0.0626, "current_win_rate": 0.0, "previous_avg_pnl": 0.2329, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0685, "current_avg_pnl": 0.0423, "current_win_rate": 0.0, "previous_avg_pnl": -0.0262, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0135, "current_avg_pnl": 0.0342, "current_win_rate": 0.0, "previous_avg_pnl": 0.0207, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0267, "current_avg_pnl": 0.0152, "current_win_rate": 0.0, "previous_avg_pnl": -0.0115, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.1541, "current_avg_pnl": -0.1195, "current_win_rate": 0.0, "previous_avg_pnl": -0.2736, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 48, "geometry_changed_delta": 0, "geometry_preserved_delta": 2913, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 39.98, "median_terminal_delta_sec": -2.06, "sl_rate_delta": 0.2, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 8, "geometry_changed_delta": 0, "geometry_preserved_delta": 38, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -666.23, "median_terminal_delta_sec": -585.47, "sl_rate_delta": -33.3, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
