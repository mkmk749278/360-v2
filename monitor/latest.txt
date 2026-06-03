# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `18` sec (warning=False)
- Latest performance record age: `516` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 717 | 717 | 238 | 18 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 5627 | 5627 | 4453 | 78 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 28799 | 28547 | 269 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 25792 | 25794 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 25675 | 23818 | 1972 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 25801 | 24572 | 1265 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 28999 | 28885 | 121 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 28779 | 28781 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 25839 | 25846 | 8 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 28819 | 28822 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 25794 | 25793 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 25673 | 25674 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 25488 | 23528 | 2135 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 25350 | 23112 | 2312 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 25426 | 25171 | 274 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::VOLUME_SURGE_BREAKOUT | 28788 | 28740 | 59 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 28784 | 28787 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3403 | 3403 | 2813 | 53 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 315 | 315 | 270 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 6429 | 6429 | 5588 | 113 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 13 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 5854 | 5854 | 2371 | 306 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 866 | 866 | 758 | 22 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 173 | 173 | 71 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=28547): breakout_not_found=18755, retest_proximity_failed=5922, basic_filters_failed=2401, volume_spike_missing=1158, ema_alignment_reject=246, missing_fvg_or_orderblock=65
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=25794): cls_disabled_merged_into_lsr=25794
- **EVAL::DIVERGENCE_CONTINUATION** (total=23818): cvd_divergence_failed=13289, h1_trend_not_aligned=3835, ema_alignment_reject=3325, basic_filters_failed=2189, retest_proximity_failed=893, missing_fvg_or_orderblock=163, regime_blocked=124
- **EVAL::FAILED_AUCTION_RECLAIM** (total=24572): auction_not_detected=12020, reclaim_hold_failed=6024, tail_too_small=4314, basic_filters_failed=2189, regime_blocked=25
- **EVAL::FUNDING_EXTREME** (total=28885): funding_not_extreme=24096, basic_filters_failed=2346, missing_funding_rate=903, ema_alignment_reject=848, rsi_reject=441, cvd_divergence_failed=118, momentum_reject=113, missing_fvg_or_orderblock=20
- **EVAL::LIQUIDATION_REVERSAL** (total=28781): cascade_threshold_not_met=25604, basic_filters_failed=2400, cvd_divergence_failed=380, rsi_reject=373, missing_fvg_or_orderblock=17, volume_spike_missing=7
- **EVAL::MA_CROSS_TREND_SHIFT** (total=25846): no_ma_cross=23267, basic_filters_failed=2191, ma_cross_cooldown=388
- **EVAL::OPENING_RANGE_BREAKOUT** (total=28822): feature_disabled=28822
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=25793): regime_blocked=10912, breakout_not_found=7207, ema_alignment_reject=3959, adx_reject=2534, basic_filters_failed=1181
- **EVAL::QUIET_COMPRESSION_BREAK** (total=25674): regime_blocked=14845, compression_not_detected=9735, basic_filters_failed=1008, breakout_not_detected=84, volume_confirmation_failed=2
- **EVAL::SR_FLIP_RETEST** (total=23528): retest_out_of_zone=9401, reclaim_hold_failed=5562, flip_close_not_confirmed=5294, basic_filters_failed=2188, wick_quality_failed=669, ema_alignment_reject=260, missing_fvg_or_orderblock=129, regime_blocked=25
- **EVAL::STANDARD** (total=23112): adx_reject=6593, momentum_reject=5370, ema_alignment_reject=4043, sweeps_not_detected=2423, macd_reject=2416, basic_filters_failed=1871, invalid_sl_geometry=357, rsi_reject=39
- **EVAL::TREND_PULLBACK** (total=25171): ema_alignment_reject=5357, h1_pullback_not_confirmed=4727, h1_trend_not_aligned=4426, ema_not_tested_prev=3774, no_ema_reclaim_close=2172, body_conviction_fail=1250, rsi_reject=1117, basic_filters_failed=1102, prev_already_below_emas=415, prev_already_above_emas=204, no_prev_low_break=187, regime_blocked=125, no_prev_high_break=122, momentum_flat=99, ema21_not_tagged=41, missing_fvg_or_orderblock=30, momentum_reject=23
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=28740): breakout_not_found=22093, retest_proximity_failed=3275, basic_filters_failed=2400, volume_spike_missing=721, ema_alignment_reject=165, missing_fvg_or_orderblock=86
- **EVAL::WHALE_MOMENTUM** (total=28787): momentum_reject=21099, recent_ticks_insufficient=7094, basic_filters_failed=594

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_DOWN | 38830 | 41.4% |
| RANGING | 20491 | 21.9% |
| QUIET | 18452 | 19.7% |
| TRENDING_UP | 15856 | 16.9% |
| VOLATILE | 89 | 0.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **254**
- Average confidence gap to threshold: **15.88** (samples=254) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: PIEVERSEUSDT=14, STGUSDT=12, CLUSDT=10, MUUSDT=10, ASTERUSDT=10, SUIUSDT=9, HOMEUSDT=9, ALLOUSDT=9, 币安人生USDT=9, MSTRUSDT=9

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 35 |
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 5 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 266 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 132 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 16 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 426 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 91 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 35 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 241 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 5 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 104 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 61 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 303 |
| SR_FLIP_RETEST | filtered | min_confidence | 937 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 126 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1597 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 9 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 94 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 10 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 4 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 12 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 40 | 58.58 | 65.00 | 6.42 | 20.54 | 19.68 | 19.27 | 0.00 | 8.56 |
| BREAKDOWN_SHORT | kept | 266 | 67.92 | 65.00 | -2.92 | 20.70 | 19.92 | 19.13 | 0.00 | 0.35 |
| DIVERGENCE_CONTINUATION | filtered | 148 | 58.36 | 65.00 | 6.64 | 21.55 | 19.81 | 17.94 | 2.01 | 8.76 |
| DIVERGENCE_CONTINUATION | kept | 426 | 70.41 | 65.00 | -5.41 | 21.16 | 19.76 | 18.67 | 2.50 | -0.72 |
| FAILED_AUCTION_RECLAIM | filtered | 126 | 53.68 | 65.00 | 11.32 | 20.55 | 18.93 | 20.00 | 4.46 | 6.67 |
| FAILED_AUCTION_RECLAIM | kept | 241 | 72.45 | 65.00 | -7.45 | 20.78 | 19.26 | 20.00 | 4.33 | 1.10 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 61.27 | 65.00 | 3.73 | 21.93 | 20.00 | 17.50 | 1.67 | 6.40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 165 | 52.57 | 65.00 | 12.43 | 21.02 | 19.61 | 18.41 | 2.80 | 7.78 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 303 | 69.95 | 65.00 | -4.95 | 21.00 | 19.60 | 18.01 | 2.39 | 0.60 |
| SR_FLIP_RETEST | filtered | 1063 | 56.85 | 65.00 | 8.15 | 21.00 | 19.86 | 16.17 | 1.59 | 8.94 |
| SR_FLIP_RETEST | kept | 1597 | 71.57 | 65.00 | -6.57 | 21.36 | 19.92 | 16.25 | 1.81 | 0.86 |
| TREND_PULLBACK_EMA | filtered | 9 | 62.20 | 65.00 | 2.80 | 21.09 | 19.07 | 18.26 | 5.17 | -0.27 |
| TREND_PULLBACK_EMA | kept | 94 | 75.67 | 65.00 | -10.67 | 21.71 | 19.77 | 18.33 | 5.36 | -0.76 |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 46.13 | 65.00 | 18.87 | 20.89 | 19.96 | 19.97 | 3.39 | 16.39 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 71.43 | 65.00 | -6.43 | 19.71 | 19.43 | 20.00 | 2.92 | 3.70 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 40 | 58.58 | 20.55 | 15.00 | 5.55 | 13.07 | 4.76 | 8.20 | 0.00 |
| BREAKDOWN_SHORT | kept | 266 | 67.92 | 24.28 | 10.93 | 5.67 | 13.60 | 7.66 | 6.15 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 148 | 58.36 | 21.22 | 16.11 | 4.26 | 11.75 | 5.54 | 8.37 | 2.01 |
| DIVERGENCE_CONTINUATION | kept | 426 | 70.41 | 20.59 | 17.15 | 4.11 | 11.92 | 5.84 | 9.19 | 2.50 |
| FAILED_AUCTION_RECLAIM | filtered | 126 | 53.68 | 21.89 | 14.95 | 7.69 | 10.75 | 6.62 | 5.07 | 4.46 |
| FAILED_AUCTION_RECLAIM | kept | 241 | 72.45 | 22.46 | 15.79 | 5.12 | 11.56 | 6.74 | 7.79 | 4.33 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 61.27 | 25.00 | 8.00 | 8.50 | 10.67 | 5.00 | 8.83 | 1.67 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 165 | 52.57 | 22.72 | 14.24 | 6.00 | 12.64 | 5.31 | 5.54 | 2.80 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 303 | 69.95 | 22.99 | 14.69 | 5.12 | 12.54 | 5.34 | 7.51 | 2.39 |
| SR_FLIP_RETEST | filtered | 1063 | 56.85 | 18.95 | 16.81 | 5.10 | 12.95 | 5.79 | 8.14 | 1.59 |
| SR_FLIP_RETEST | kept | 1597 | 71.57 | 20.27 | 17.37 | 5.53 | 13.73 | 6.01 | 8.97 | 1.81 |
| TREND_PULLBACK_EMA | filtered | 9 | 62.20 | 23.22 | 18.00 | 3.00 | 14.00 | 5.00 | 6.54 | 5.17 |
| TREND_PULLBACK_EMA | kept | 94 | 75.67 | 19.30 | 18.00 | 3.45 | 14.13 | 6.80 | 9.25 | 5.36 |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 46.13 | 23.86 | 10.14 | 7.29 | 13.36 | 5.50 | 6.48 | 3.39 |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 71.43 | 23.67 | 13.00 | 3.75 | 14.75 | 7.71 | 9.33 | 2.92 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 40 | 58.58 | 0.00 | 0.00 | 1.08 | 0.00 | 3.00 | 0.15 | 0.00 | 0.00 | **4.23** |
| BREAKDOWN_SHORT | kept | 266 | 67.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 148 | 58.36 | 0.00 | 0.00 | 1.96 | 0.00 | 0.55 | 0.08 | 0.00 | 0.00 | **2.59** |
| DIVERGENCE_CONTINUATION | kept | 426 | 70.41 | 0.00 | 0.00 | 0.32 | 0.00 | 0.07 | 0.06 | 0.00 | 0.00 | **0.45** |
| FAILED_AUCTION_RECLAIM | filtered | 126 | 53.68 | 0.00 | 0.00 | 0.61 | 0.00 | 3.98 | 0.00 | 0.00 | 0.00 | **4.59** |
| FAILED_AUCTION_RECLAIM | kept | 241 | 72.45 | 0.00 | 0.00 | 0.23 | 0.00 | 0.55 | 0.02 | 0.00 | 0.00 | **0.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 61.27 | 0.00 | 0.00 | 6.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.40** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 165 | 52.57 | 0.09 | 0.00 | 2.27 | 0.00 | 4.81 | 0.12 | 0.00 | 0.00 | **7.29** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 303 | 69.95 | 0.00 | 0.00 | 0.23 | 0.00 | 0.26 | 0.04 | 0.00 | 0.00 | **0.53** |
| SR_FLIP_RETEST | filtered | 1063 | 56.85 | 0.00 | 0.00 | 0.80 | 0.00 | 2.03 | 0.01 | 0.00 | 0.39 | **3.23** |
| SR_FLIP_RETEST | kept | 1597 | 71.57 | 0.00 | 0.00 | 0.13 | 0.00 | 0.40 | 0.03 | 0.00 | 0.00 | **0.56** |
| TREND_PULLBACK_EMA | filtered | 9 | 62.20 | 0.00 | 0.00 | 1.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.07** |
| TREND_PULLBACK_EMA | kept | 94 | 75.67 | 0.00 | 0.00 | 0.71 | 0.00 | 0.08 | 0.00 | 0.00 | 0.00 | **0.79** |
| VOLUME_SURGE_BREAKOUT | filtered | 14 | 46.13 | 0.00 | 0.00 | 5.14 | 0.00 | 5.16 | 0.00 | 0.00 | 3.09 | **13.39** |
| VOLUME_SURGE_BREAKOUT | kept | 12 | 71.43 | 0.00 | 0.00 | 1.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.20** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=41 (77.4%) | PREMATURE=7 (13.2%) | NEUTRAL=5 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 34 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 11 | 3 | 0 | 0 |
| momentum_loss | 18 | 3 | 1 | 0 |
| regime_shift | 4 | 0 | 1 | 0 |
| trailing_invalidation | 8 | 1 | 3 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 3 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 0 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 14 | 3 | 1 | 0 |
| SR_FLIP_RETEST | 13 | 3 | 2 | 0 |
| TREND_PULLBACK_EMA | 2 | 1 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 11 | 3 | 0 | 3.8 | 5.9 | -0.15 | **INSUFFICIENT_SAMPLE** — only 14 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 18 | 3 | 1 | 11.4 | 4.8 | +0.30 | **KEEP** — net-helping: avg +0.30R/kill across 22 kills (saved 11.4R vs missed 4.8R) |
| regime_shift | 4 | 0 | 1 | 2.3 | 0.0 | +0.45 | **INSUFFICIENT_SAMPLE** — only 5 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 8 | 1 | 3 | 7.1 | 1.2 | +0.49 | **INSUFFICIENT_SAMPLE** — only 12 classified kills (need >= 20); let data accumulate before tuning |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `647274`
- `Path funnel` emissions: `13`
- `Regime distribution` emissions: `13`
- `QUIET_SCALP_BLOCK` events: `254`
- `confidence_gate` events: `4510`
- `free_channel_post` events: `162`
- `pre_tp_fire` events: `74`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **74**
- Avg resolved threshold: **0.529%** raw → avg net **+4.59%** @ 10x
- Avg time-to-fire from dispatch: **213s**
- By threshold source: stamped=74

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 35 | 0.481% | +4.11% | 219 | stamped=35 |
| LIQUIDITY_SWEEP_REVERSAL | 23 | 0.619% | +5.50% | 240 | stamped=23 |
| DIVERGENCE_CONTINUATION | 6 | 0.472% | +4.01% | 113 | stamped=6 |
| TREND_PULLBACK_EMA | 6 | 0.552% | +4.83% | 255 | stamped=6 |
| FAILED_AUCTION_RECLAIM | 4 | 0.474% | +4.04% | 86 | stamped=4 |
- Top symbols: FILUSDT=8, PUMPUSDT=7, RENDERUSDT=6, STGUSDT=5, OPGUSDT=5, ORDIUSDT=4, XPLUSDT=4, ALLOUSDT=4, VICUSDT=4, HOMEUSDT=4

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **162**

| Source | Count |
|---|---:|
| signal_close | 84 |
| pre_tp | 74 |
| signal_highlight | 3 |
| regime_shift | 1 |

- By severity: HIGH=162

## Dependency readiness
- cvd: presence[present=83997] state[populated=83997] buckets[many=83997] sources[none] quality[none]
- funding_rate: presence[absent=2225, present=81772] state[empty=2225, populated=81772] buckets[few=81772, none=2225] sources[none] quality[none]
- liquidation_clusters: presence[absent=27330, present=56667] state[empty=27330, populated=56667] buckets[few=37646, none=27330, some=19021] sources[none] quality[none]
- oi_snapshot: presence[absent=1003, present=82994] state[empty=1003, populated=82994] buckets[many=82994, none=1003] sources[none] quality[none]
- order_book: presence[absent=55669, present=28328] state[populated=28328, unavailable=55669] buckets[few=28328, none=55669] sources[book_ticker=28328, unavailable=55669] quality[none=55669, top_of_book_only=28328]
- orderblocks: presence[absent=83997] state[empty=83997] buckets[none=83997] sources[not_implemented=83997] quality[none]
- recent_ticks: presence[present=83997] state[populated=83997] buckets[many=83997] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `20.163264989852905` sec
- Median create→first breach: `383.50218510627747` sec
- Median create→terminal: `386.91967391967773` sec
- Median first breach→terminal: `4.740437984466553` sec
- Fast-failure buckets: `{"under_120s": {"count": 13, "pct": 18.3}, "under_180s": {"count": 17, "pct": 23.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 6, "pct": 8.5}}`
- ~3 minute terminal-close behavior: `{"count": 8, "pct": 6.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 5 | 5 | 0.0 | 20.0 | 0.0 | 0.0 | -0.2303 | 69.87745904922485 | 440.94749879837036 |
| DIVERGENCE_CONTINUATION | 11 | 11 | 0.0 | 9.1 | 0.0 | 54.5 | 0.1096 | 271.32361006736755 | 135.97357416152954 |
| FAILED_AUCTION_RECLAIM | 13 | 13 | 0.0 | 7.7 | 0.0 | 30.8 | -0.0635 | 126.99853992462158 | 333.8202531337738 |
| LIQUIDITY_SWEEP_REVERSAL | 44 | 44 | 0.0 | 4.5 | 0.0 | 52.3 | 0.0577 | 376.1481090784073 | 357.83321738243103 |
| SR_FLIP_RETEST | 52 | 52 | 0.0 | 9.6 | 0.0 | 67.3 | 0.03 | 448.4033844470978 | 462.0863894224167 |
| TREND_PULLBACK_EMA | 8 | 8 | 0.0 | 0.0 | 0.0 | 75.0 | 0.0745 | 354.13648200035095 | 494.2131019830704 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 5854 | 306 | 2371 | 0.0 | 9.6 | 448.4033844470978 | 462.0863894224167 | 3483 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 866 | 22 | 758 | 0.0 | 0.0 | 354.13648200035095 | 494.2131019830704 | 108 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `74`
- Gating Δ: `4300`
- No-generation Δ: `109910`
- Fast failures Δ: `17`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.2303, "current_avg_pnl": -0.2303, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.1096, "current_avg_pnl": 0.1096, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0635, "current_avg_pnl": -0.0635, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0577, "current_avg_pnl": 0.0577, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.03, "current_avg_pnl": 0.03, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.0745, "current_avg_pnl": 0.0745, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 9, "geometry_changed_delta": 0, "geometry_preserved_delta": -281, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 448.4, "median_terminal_delta_sec": 462.09, "sl_rate_delta": 9.6, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 29, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 354.14, "median_terminal_delta_sec": 494.21, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
