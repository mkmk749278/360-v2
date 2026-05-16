# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM, LIQUIDITY_SWEEP_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `626` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1513 | 1513 | 1418 | 1 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1504 | 1504 | 1454 | 13 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6716 | 6716 | 6343 | 27 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 265843 | 264330 | 1513 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 247588 | 246084 | 1504 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 247588 | 240872 | 6716 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 247588 | 226869 | 20719 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 265843 | 265554 | 289 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 265843 | 265826 | 17 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 247588 | 247567 | 21 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 265843 | 265843 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 247588 | 247576 | 12 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 247588 | 239628 | 7960 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 247588 | 223687 | 23901 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 247588 | 231969 | 15619 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 247588 | 246641 | 947 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 265843 | 264991 | 852 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 265843 | 265843 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 20719 | 20719 | 16854 | 107 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 289 | 289 | 253 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15619 | 15619 | 13306 | 101 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 21 | 21 | 17 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 12 | 12 | 12 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 7960 | 7960 | 6049 | 76 | active-low-quality (none) |
| RANGE_FADE | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 23901 | 23901 | 17080 | 135 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 947 | 947 | 896 | 8 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 852 | 852 | 824 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=264330): breakout_not_found=144213, basic_filters_failed=74752, retest_proximity_failed=34950, volume_spike_missing=7641, ema_alignment_reject=1890, missing_fvg_or_orderblock=807, insufficient_candles=77
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=246084): regime_blocked=164816, sweeps_not_detected=29443, basic_filters_failed=16686, ema_alignment_reject=15344, adx_reject=12303, momentum_reject=5952, reclaim_confirmation_failed=1540
- **EVAL::DIVERGENCE_CONTINUATION** (total=240872): regime_blocked=164816, cvd_divergence_failed=50516, basic_filters_failed=16686, ema_alignment_reject=6489, retest_proximity_failed=1608, missing_fvg_or_orderblock=757
- **EVAL::FAILED_AUCTION_RECLAIM** (total=226869): auction_not_detected=97442, basic_filters_failed=68112, reclaim_hold_failed=37249, tail_too_small=24059, rsi_reject=7
- **EVAL::FUNDING_EXTREME** (total=265554): funding_not_extreme=183684, basic_filters_failed=72850, missing_funding_rate=5353, ema_alignment_reject=2118, rsi_reject=944, cvd_divergence_failed=298, momentum_reject=271, missing_fvg_or_orderblock=36
- **EVAL::LIQUIDATION_REVERSAL** (total=265826): cascade_threshold_not_met=189094, basic_filters_failed=74752, rsi_reject=926, cvd_divergence_failed=908, missing_fvg_or_orderblock=65, insufficient_candles=63, volume_spike_missing=18
- **EVAL::MA_CROSS_TREND_SHIFT** (total=247567): no_ma_cross=175411, basic_filters_failed=68112, ma_cross_cooldown=4044
- **EVAL::OPENING_RANGE_BREAKOUT** (total=265843): feature_disabled=265843
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=247576): regime_blocked=164816, breakout_not_found=38427, basic_filters_failed=16686, ema_alignment_reject=15344, adx_reject=12303
- **EVAL::QUIET_COMPRESSION_BREAK** (total=239628): breakout_not_detected=85629, regime_blocked=82772, basic_filters_failed=51426, compression_not_detected=18654, missing_fvg_or_orderblock=803, rsi_reject=344
- **EVAL::SR_FLIP_RETEST** (total=223687): basic_filters_failed=68095, reclaim_hold_failed=58667, flip_close_not_confirmed=46947, retest_out_of_zone=33534, wick_quality_failed=9914, ema_alignment_reject=4056, missing_fvg_or_orderblock=2368, insufficient_candles=62, rsi_reject=44
- **EVAL::STANDARD** (total=231969): basic_filters_failed=52897, adx_reject=51995, momentum_reject=48502, sweeps_not_detected=44048, macd_reject=22232, ema_alignment_reject=11808, invalid_sl_geometry=318, rsi_reject=85, htf_ema_reject=54, insufficient_candles=29, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=246641): regime_blocked=164816, ema_alignment_reject=25699, basic_filters_failed=16686, no_ema_reclaim_close=12750, ema_not_tested_prev=11051, body_conviction_fail=6722, rsi_reject=5655, prev_already_below_emas=1450, no_prev_low_break=859, no_prev_high_break=264, momentum_flat=239, prev_already_above_emas=221, missing_fvg_or_orderblock=97, ema21_not_tagged=89, momentum_reject=36, insufficient_candles=7
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=264991): breakout_not_found=165951, basic_filters_failed=74752, retest_proximity_failed=17324, volume_spike_missing=4555, ema_alignment_reject=1676, missing_fvg_or_orderblock=644, insufficient_candles=77, rsi_reject=12
- **EVAL::WHALE_MOMENTUM** (total=265843): momentum_reject=193695, recent_ticks_insufficient=54154, basic_filters_failed=17994

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 201350 | 64.0% |
| TRENDING_DOWN | 77559 | 24.6% |
| TRENDING_UP | 29909 | 9.5% |
| RANGING | 6008 | 1.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1719**
- Average confidence gap to threshold: **16.34** (samples=1719) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=83, SUIUSDT=81, DOGEUSDT=77, HYPEUSDT=70, 1000PEPEUSDT=48, POLYXUSDT=48, INJUSDT=47, PENGUUSDT=46, AVAXUSDT=46, BNBUSDT=45

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 3 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 11 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 38 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 58 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 75 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 299 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 188 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 680 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 397 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 41 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 467 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 778 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 1 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 362 |
| SR_FLIP_RETEST | filtered | min_confidence | 533 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 242 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 785 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 31 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 10 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 4 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 72.90 | 65.00 | -7.90 | 20.53 | 17.53 | 20.00 | 0.00 | 5.20 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 11 | 55.69 | 65.00 | 9.31 | 21.49 | 18.89 | 17.00 | 0.36 | 3.33 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 38 | 71.41 | 65.00 | -6.41 | 21.26 | 19.35 | 17.00 | 0.68 | -0.15 |
| DIVERGENCE_CONTINUATION | filtered | 58 | 57.29 | 65.00 | 7.71 | 20.56 | 19.62 | 18.30 | 2.03 | -1.88 |
| DIVERGENCE_CONTINUATION | kept | 75 | 69.63 | 65.00 | -4.63 | 20.19 | 19.83 | 17.95 | 2.87 | -0.39 |
| FAILED_AUCTION_RECLAIM | filtered | 487 | 52.39 | 65.00 | 12.61 | 20.61 | 19.48 | 14.00 | 4.61 | 7.61 |
| FAILED_AUCTION_RECLAIM | kept | 680 | 70.83 | 65.00 | -5.83 | 21.22 | 19.80 | 14.00 | 4.63 | 0.39 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 46.97 | 65.00 | 18.03 | 20.36 | 20.00 | 17.00 | 2.00 | 10.49 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 438 | 48.44 | 65.00 | 16.56 | 21.07 | 19.61 | 15.20 | 2.66 | 12.19 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 467 | 69.68 | 65.00 | -4.68 | 21.33 | 19.75 | 15.20 | 2.51 | 0.02 |
| QUIET_COMPRESSION_BREAK | filtered | 779 | 49.77 | 65.00 | 15.23 | 21.12 | 19.25 | 15.80 | 0.00 | 7.84 |
| QUIET_COMPRESSION_BREAK | kept | 362 | 73.07 | 65.00 | -8.07 | 22.32 | 19.13 | 15.80 | 0.00 | -0.22 |
| SR_FLIP_RETEST | filtered | 775 | 51.89 | 65.00 | 13.11 | 20.87 | 19.87 | 15.65 | 2.12 | 7.77 |
| SR_FLIP_RETEST | kept | 785 | 70.76 | 65.00 | -5.76 | 21.00 | 19.92 | 15.72 | 2.13 | -0.78 |
| TREND_PULLBACK_EMA | kept | 31 | 71.93 | 65.00 | -6.93 | 20.02 | 19.56 | 17.49 | 4.74 | -0.37 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 53.91 | 65.00 | 11.09 | 19.43 | 19.46 | 20.00 | 3.00 | 3.96 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 67.55 | 65.00 | -2.55 | 21.17 | 19.88 | 19.07 | 3.62 | 2.25 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 72.90 | 22.33 | 18.00 | 11.00 | 12.67 | 5.00 | 9.10 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 11 | 55.69 | 21.55 | 18.00 | 3.00 | 13.45 | 6.18 | 6.02 | 0.36 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 38 | 71.41 | 20.58 | 18.00 | 4.89 | 13.03 | 6.88 | 8.77 | 0.68 |
| DIVERGENCE_CONTINUATION | filtered | 58 | 57.29 | 21.14 | 18.00 | 3.98 | 12.40 | 4.81 | 7.48 | 2.03 |
| DIVERGENCE_CONTINUATION | kept | 75 | 69.63 | 19.88 | 18.00 | 3.68 | 12.40 | 5.78 | 7.28 | 2.87 |
| FAILED_AUCTION_RECLAIM | filtered | 487 | 52.39 | 22.89 | 14.06 | 5.77 | 11.52 | 6.57 | 5.13 | 4.61 |
| FAILED_AUCTION_RECLAIM | kept | 680 | 70.83 | 23.13 | 14.24 | 4.47 | 10.98 | 6.54 | 7.27 | 4.63 |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 46.97 | 25.00 | 8.00 | 3.00 | 15.71 | 5.00 | 7.31 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 438 | 48.44 | 22.89 | 14.34 | 6.05 | 12.48 | 5.60 | 6.20 | 2.66 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 467 | 69.68 | 23.24 | 14.21 | 4.66 | 12.25 | 5.50 | 7.34 | 2.51 |
| QUIET_COMPRESSION_BREAK | filtered | 779 | 49.77 | 19.04 | 17.99 | 8.88 | 14.55 | 7.11 | 3.46 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 362 | 73.07 | 20.60 | 17.92 | 6.54 | 14.12 | 6.68 | 8.21 | 0.00 |
| SR_FLIP_RETEST | filtered | 775 | 51.89 | 21.61 | 14.88 | 5.93 | 13.89 | 6.24 | 5.76 | 2.12 |
| SR_FLIP_RETEST | kept | 785 | 70.76 | 21.98 | 15.46 | 4.23 | 13.57 | 6.11 | 8.58 | 2.13 |
| TREND_PULLBACK_EMA | kept | 31 | 71.93 | 18.55 | 18.00 | 3.29 | 14.10 | 7.63 | 6.22 | 4.74 |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 53.91 | 21.80 | 12.00 | 6.30 | 12.50 | 5.70 | 7.07 | 3.00 |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 67.55 | 23.00 | 10.50 | 6.00 | 13.25 | 5.25 | 8.18 | 3.62 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 3 | 72.90 | 0.00 | 0.00 | 3.20 | 0.00 | 0.00 | 0.00 | **3.20** |
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 11 | 55.69 | 0.00 | 0.00 | 0.87 | 0.00 | 0.00 | 0.00 | **0.87** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 38 | 71.41 | 0.00 | 0.00 | 0.38 | 0.00 | 0.28 | 0.00 | **0.66** |
| DIVERGENCE_CONTINUATION | filtered | 58 | 57.29 | 0.00 | 0.00 | 0.91 | 0.00 | 0.00 | 0.00 | **0.91** |
| DIVERGENCE_CONTINUATION | kept | 75 | 69.63 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.13** |
| FAILED_AUCTION_RECLAIM | filtered | 487 | 52.39 | 0.00 | 0.00 | 2.41 | 0.00 | 3.71 | 0.00 | **6.12** |
| FAILED_AUCTION_RECLAIM | kept | 680 | 70.83 | 0.00 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **0.15** |
| FUNDING_EXTREME_SIGNAL | filtered | 7 | 46.97 | 0.00 | 0.00 | 5.49 | 0.00 | 0.00 | 0.00 | **5.49** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 438 | 48.44 | 0.00 | 0.00 | 5.73 | 0.00 | 6.46 | 0.00 | **12.19** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 467 | 69.68 | 0.00 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | **0.03** |
| QUIET_COMPRESSION_BREAK | filtered | 779 | 49.77 | 0.00 | 0.00 | 2.40 | 0.00 | 2.16 | 0.00 | **4.56** |
| QUIET_COMPRESSION_BREAK | kept | 362 | 73.07 | 0.00 | 0.00 | 0.16 | 0.00 | 1.22 | 0.00 | **1.38** |
| SR_FLIP_RETEST | filtered | 775 | 51.89 | 0.00 | 0.00 | 1.86 | 0.00 | 3.11 | 0.00 | **4.97** |
| SR_FLIP_RETEST | kept | 785 | 70.76 | 0.00 | 0.00 | 0.13 | 0.00 | 0.01 | 0.00 | **0.14** |
| TREND_PULLBACK_EMA | kept | 31 | 71.93 | 0.00 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | **0.31** |
| VOLUME_SURGE_BREAKOUT | filtered | 10 | 53.91 | 0.00 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **0.96** |
| VOLUME_SURGE_BREAKOUT | kept | 4 | 67.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=136 (62.7%) | PREMATURE=21 (9.7%) | NEUTRAL=60 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=3
- **Net-helping** — invalidation saved on 115 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 2 | 0 | 0 | 0 |
| other | 90 | 8 | 35 | 0 |
| regime_shift | 44 | 13 | 25 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 6 | 0 | 3 | 0 |
| DIVERGENCE_CONTINUATION | 3 | 4 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 31 | 2 | 13 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 20 | 7 | 8 | 0 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0 | 0 | 0 |
| QUIET_COMPRESSION_BREAK | 19 | 0 | 17 | 0 |
| SR_FLIP_RETEST | 51 | 8 | 18 | 0 |
| TREND_PULLBACK_EMA | 4 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1725485`
- `Path funnel` emissions: `43`
- `Regime distribution` emissions: `43`
- `QUIET_SCALP_BLOCK` events: `1719`
- `confidence_gate` events: `5010`
- `free_channel_post` events: `296`
- `pre_tp_fire` events: `157`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **157**
- Avg resolved threshold: **0.370%** raw → avg net **+3.00%** @ 10x
- Avg time-to-fire from dispatch: **393s**
- By threshold source: stamped=157

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 48 | 0.304% | +2.34% | 484 | stamped=48 |
| LIQUIDITY_SWEEP_REVERSAL | 41 | 0.519% | +4.49% | 344 | stamped=41 |
| QUIET_COMPRESSION_BREAK | 24 | 0.310% | +2.40% | 320 | stamped=24 |
| FAILED_AUCTION_RECLAIM | 24 | 0.266% | +1.96% | 500 | stamped=24 |
| DIVERGENCE_CONTINUATION | 13 | 0.418% | +3.48% | 237 | stamped=13 |
| TREND_PULLBACK_EMA | 4 | 0.503% | +4.33% | 260 | stamped=4 |
| CONTINUATION_LIQUIDITY_SWEEP | 3 | 0.316% | +2.46% | 209 | stamped=3 |
- Top symbols: TONUSDT=7, RIVERUSDT=7, SAHARAUSDT=7, UBUSDT=7, VVVUSDT=7, ICPUSDT=6, INJUSDT=6, SIRENUSDT=5, DASHUSDT=5, UNIUSDT=5

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **7**
- Total REST-fallback activations: **1**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 2 | 1706 | 1706 | 1829 | 0 |
| futures_liq | 5 | 3163 | 5022 | 23896 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 1 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **296**

| Source | Count |
|---|---:|
| pre_tp | 157 |
| signal_close | 137 |
| regime_shift | 2 |

- By severity: HIGH=296

## Dependency readiness
- cvd: presence[present=265843] state[populated=265843] buckets[many=265741, some=102] sources[none] quality[none]
- funding_rate: presence[absent=5353, present=260490] state[empty=5353, populated=260490] buckets[few=260490, none=5353] sources[none] quality[none]
- liquidation_clusters: presence[absent=153767, present=112076] state[empty=153767, populated=112076] buckets[few=93942, none=153767, some=18134] sources[none] quality[none]
- oi_snapshot: presence[absent=3142, present=262701] state[empty=3142, populated=262701] buckets[many=262701, none=3142] sources[none] quality[none]
- order_book: presence[absent=69936, present=195907] state[populated=195907, unavailable=69936] buckets[few=195907, none=69936] sources[book_ticker=195907, unavailable=69936] quality[none=69936, top_of_book_only=195907]
- orderblocks: presence[absent=265843] state[empty=265843] buckets[none=265843] sources[not_implemented=265843] quality[none]
- recent_ticks: presence[absent=853, present=264990] state[empty=853, populated=264990] buckets[many=264990, none=853] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.75274908542633` sec
- Median create→first breach: `483.57860493659973` sec
- Median create→terminal: `706.2080994844437` sec
- Median first breach→terminal: `7.917820930480957` sec
- Fast-failure buckets: `{"under_120s": {"count": 21, "pct": 15.3}, "under_180s": {"count": 26, "pct": 19.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 12, "pct": 8.8}}`
- ~3 minute terminal-close behavior: `{"count": 11, "pct": 4.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 7 | 7 | 0.0 | 0.0 | 0.0 | 0.0459 | 183.2548635005951 | 641.5623559951782 |
| DIVERGENCE_CONTINUATION | 18 | 18 | 0.0 | 11.1 | 0.0 | -0.0834 | 280.9264588356018 | 476.32869935035706 |
| FAILED_AUCTION_RECLAIM | 52 | 52 | 0.0 | 9.6 | 0.0 | -0.0949 | 693.4609169960022 | 801.5948675870895 |
| LIQUIDITY_SWEEP_REVERSAL | 65 | 65 | 0.0 | 10.8 | 0.0 | 0.1209 | 409.8961880207062 | 661.6236741542816 |
| QUIET_COMPRESSION_BREAK | 42 | 42 | 0.0 | 0.0 | 0.0 | -0.0051 | 329.17774510383606 | 683.8752400875092 |
| SR_FLIP_RETEST | 87 | 87 | 0.0 | 10.3 | 0.0 | -0.0142 | 581.9508863687515 | 750.1874399185181 |
| TREND_PULLBACK_EMA | 8 | 8 | 0.0 | 12.5 | 0.0 | -0.6728 | 315.40183997154236 | 436.99711894989014 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1132 | None | 796.588063955307 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 23901 | 135 | 17080 | 0.0 | 10.3 | 581.9508863687515 | 750.1874399185181 | 6821 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 947 | 8 | 896 | 0.0 | 12.5 | 315.40183997154236 | 436.99711894989014 | 51 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-7`
- Gating Δ: `-45345`
- No-generation Δ: `-3550486`
- Fast failures Δ: `0`
- Quality changes: `{"CONTINUATION_LIQUIDITY_SWEEP": {"avg_pnl_delta": 0.2208, "current_avg_pnl": 0.0459, "current_win_rate": 0.0, "previous_avg_pnl": -0.1749, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0882, "current_avg_pnl": -0.0834, "current_win_rate": 0.0, "previous_avg_pnl": -0.1716, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0935, "current_avg_pnl": -0.0949, "current_win_rate": 0.0, "previous_avg_pnl": -0.0014, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.1349, "current_avg_pnl": 0.1209, "current_win_rate": 0.0, "previous_avg_pnl": -0.014, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0406, "current_avg_pnl": -0.0051, "current_win_rate": 0.0, "previous_avg_pnl": -0.0457, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0198, "current_avg_pnl": -0.0142, "current_win_rate": 0.0, "previous_avg_pnl": 0.0056, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.5942, "current_avg_pnl": -0.6728, "current_win_rate": 0.0, "previous_avg_pnl": -0.0786, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -16, "geometry_changed_delta": 0, "geometry_preserved_delta": -24091, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 130.32, "median_terminal_delta_sec": 44.33, "sl_rate_delta": 2.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": -3, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 315.4, "median_terminal_delta_sec": -329.02, "sl_rate_delta": 12.5, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
