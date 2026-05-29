# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `36` sec (warning=False)
- Latest performance record age: `1300` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 267 | 267 | 73 | 8 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2915 | 2915 | 2525 | 36 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 46799 | 46532 | 267 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 42084 | 42084 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 42084 | 39169 | 2915 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 42084 | 39718 | 2366 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 46799 | 46765 | 34 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 46799 | 46795 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 42084 | 42070 | 14 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 46799 | 46799 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 42084 | 42084 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 42084 | 41988 | 96 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 42084 | 37317 | 4767 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 42084 | 37316 | 4768 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 42084 | 41619 | 465 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 46799 | 46670 | 129 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 46799 | 46799 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2366 | 2366 | 1620 | 74 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 34 | 34 | 30 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4768 | 4768 | 4098 | 101 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 14 | 14 | 9 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 96 | 96 | 96 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 4767 | 4767 | 2477 | 187 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 465 | 465 | 430 | 3 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 129 | 129 | 63 | 1 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=46532): breakout_not_found=37541, retest_proximity_failed=5843, volume_spike_missing=1845, basic_filters_failed=715, ema_alignment_reject=478, missing_fvg_or_orderblock=110
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=42084): cls_disabled_merged_into_lsr=42084
- **EVAL::DIVERGENCE_CONTINUATION** (total=39169): cvd_divergence_failed=17853, h1_trend_not_aligned=13756, ema_alignment_reject=5959, retest_proximity_failed=712, basic_filters_failed=680, missing_fvg_or_orderblock=209
- **EVAL::FAILED_AUCTION_RECLAIM** (total=39718): auction_not_detected=21855, reclaim_hold_failed=9721, tail_too_small=7462, basic_filters_failed=680
- **EVAL::FUNDING_EXTREME** (total=46765): funding_not_extreme=43950, missing_funding_rate=1492, basic_filters_failed=710, ema_alignment_reject=325, rsi_reject=215, cvd_divergence_failed=46, momentum_reject=23, missing_fvg_or_orderblock=4
- **EVAL::LIQUIDATION_REVERSAL** (total=46795): cascade_threshold_not_met=45382, basic_filters_failed=715, cvd_divergence_failed=354, rsi_reject=317, missing_fvg_or_orderblock=20, volume_spike_missing=7
- **EVAL::MA_CROSS_TREND_SHIFT** (total=42070): no_ma_cross=40309, ma_cross_cooldown=1081, basic_filters_failed=680
- **EVAL::OPENING_RANGE_BREAKOUT** (total=46799): feature_disabled=46799
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=42084): regime_blocked=25503, breakout_not_found=9204, ema_alignment_reject=3882, adx_reject=3285, basic_filters_failed=210
- **EVAL::QUIET_COMPRESSION_BREAK** (total=41988): compression_not_detected=24937, regime_blocked=16581, basic_filters_failed=470
- **EVAL::SR_FLIP_RETEST** (total=37317): flip_close_not_confirmed=11831, retest_out_of_zone=11295, reclaim_hold_failed=10679, wick_quality_failed=1788, ema_alignment_reject=864, basic_filters_failed=680, missing_fvg_or_orderblock=172, rsi_reject=8
- **EVAL::STANDARD** (total=37316): momentum_reject=11047, adx_reject=10455, macd_reject=6209, ema_alignment_reject=3886, sweeps_not_detected=3722, basic_filters_failed=1666, invalid_sl_geometry=278, rsi_reject=47, mtf_reject=6
- **EVAL::TREND_PULLBACK** (total=41619): h1_trend_not_aligned=14090, h1_pullback_not_confirmed=9388, ema_alignment_reject=7557, no_ema_reclaim_close=3523, ema_not_tested_prev=2819, body_conviction_fail=1743, rsi_reject=1225, prev_already_below_emas=451, no_prev_low_break=324, prev_already_above_emas=144, basic_filters_failed=140, momentum_flat=81, no_prev_high_break=73, missing_fvg_or_orderblock=31, ema21_not_tagged=24, momentum_reject=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=46670): breakout_not_found=35178, retest_proximity_failed=8733, volume_spike_missing=1464, basic_filters_failed=715, ema_alignment_reject=441, missing_fvg_or_orderblock=135, rsi_reject=4
- **EVAL::WHALE_MOMENTUM** (total=46799): momentum_reject=29430, recent_ticks_insufficient=17344, basic_filters_failed=25

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 23399 | 46.2% |
| TRENDING_UP | 11371 | 22.5% |
| TRENDING_DOWN | 8502 | 16.8% |
| RANGING | 7349 | 14.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **391**
- Average confidence gap to threshold: **14.44** (samples=391) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ICPUSDT=27, BEATUSDT=19, UBUSDT=18, BNBUSDT=18, TRXUSDT=16, AAVEUSDT=14, RENDERUSDT=14, CRCLUSDT=13, GENIUSUSDT=12, SEIUSDT=12

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 4 |
| BREAKDOWN_SHORT | filtered | min_confidence | 1 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 24 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 37 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 15 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 84 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 85 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 76 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 216 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 131 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 35 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 184 |
| SR_FLIP_RETEST | filtered | min_confidence | 289 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 156 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 556 |
| TREND_PULLBACK_CONTINUATION | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 24 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 1 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 57.44 | 65.00 | 7.56 | 20.96 | 20.00 | 16.86 | 0.00 | 10.50 |
| BREAKDOWN_SHORT | kept | 24 | 71.17 | 65.00 | -6.17 | 21.11 | 19.97 | 18.13 | 0.00 | 1.38 |
| DIVERGENCE_CONTINUATION | filtered | 52 | 55.66 | 65.00 | 9.34 | 20.59 | 19.79 | 17.49 | 1.50 | 13.54 |
| DIVERGENCE_CONTINUATION | kept | 84 | 69.86 | 65.00 | -4.86 | 20.98 | 19.75 | 17.23 | 2.18 | 0.45 |
| FAILED_AUCTION_RECLAIM | filtered | 161 | 53.72 | 65.00 | 11.28 | 20.94 | 19.31 | 20.00 | 3.51 | 8.91 |
| FAILED_AUCTION_RECLAIM | kept | 216 | 71.44 | 65.00 | -6.44 | 21.22 | 19.58 | 20.00 | 4.68 | 0.41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 166 | 50.26 | 65.00 | 14.74 | 20.91 | 19.56 | 18.02 | 2.86 | 11.25 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 184 | 70.09 | 65.00 | -5.09 | 21.10 | 19.71 | 17.79 | 2.85 | 0.20 |
| SR_FLIP_RETEST | filtered | 445 | 53.13 | 65.00 | 11.87 | 21.00 | 19.90 | 15.89 | 1.97 | 10.21 |
| SR_FLIP_RETEST | kept | 556 | 71.29 | 65.00 | -6.29 | 21.07 | 19.95 | 15.67 | 2.19 | -0.66 |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 68.50 | 65.00 | -3.50 | 20.80 | 19.80 | 16.40 | 0.00 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 1 | 62.10 | 65.00 | 2.90 | 20.90 | 20.00 | 20.00 | 5.50 | 8.40 |
| TREND_PULLBACK_EMA | kept | 24 | 78.59 | 65.00 | -13.59 | 21.39 | 19.66 | 17.41 | 5.58 | -1.10 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 62.00 | 65.00 | 3.00 | 21.10 | 20.00 | 17.60 | 1.50 | 4.80 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 71.50 | 65.00 | -6.50 | 21.10 | 20.00 | 17.60 | 3.00 | 4.80 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 57.44 | 24.60 | 10.00 | 4.80 | 12.40 | 7.20 | 8.94 | 0.00 |
| BREAKDOWN_SHORT | kept | 24 | 71.17 | 22.67 | 16.33 | 5.00 | 13.46 | 5.88 | 9.22 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 52 | 55.66 | 22.23 | 13.19 | 7.04 | 12.25 | 5.48 | 7.79 | 1.50 |
| DIVERGENCE_CONTINUATION | kept | 84 | 69.86 | 22.43 | 15.38 | 4.61 | 12.24 | 5.98 | 8.82 | 2.18 |
| FAILED_AUCTION_RECLAIM | filtered | 161 | 53.72 | 21.67 | 14.97 | 6.06 | 13.14 | 6.60 | 5.35 | 3.51 |
| FAILED_AUCTION_RECLAIM | kept | 216 | 71.44 | 23.96 | 14.41 | 4.07 | 11.43 | 6.19 | 7.22 | 4.68 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 166 | 50.26 | 23.13 | 14.10 | 6.22 | 12.78 | 5.47 | 5.56 | 2.86 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 184 | 70.09 | 23.33 | 14.37 | 4.22 | 12.44 | 5.84 | 7.33 | 2.85 |
| SR_FLIP_RETEST | filtered | 445 | 53.13 | 20.89 | 14.49 | 6.48 | 13.83 | 6.22 | 6.27 | 1.97 |
| SR_FLIP_RETEST | kept | 556 | 71.29 | 22.06 | 15.55 | 4.58 | 13.66 | 5.87 | 8.46 | 2.19 |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 68.50 | 25.00 | 8.00 | 9.00 | 14.00 | 2.50 | 10.00 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 1 | 62.10 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.00 | 5.50 |
| TREND_PULLBACK_EMA | kept | 24 | 78.59 | 21.67 | 18.00 | 3.88 | 13.50 | 7.00 | 9.70 | 5.58 |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 62.00 | 17.00 | 18.00 | 6.00 | 10.00 | 5.00 | 9.30 | 1.50 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 71.50 | 25.00 | 18.00 | 6.00 | 10.00 | 5.00 | 9.30 | 3.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 5 | 57.44 | 0.00 | 0.00 | 0.96 | 0.00 | 4.32 | 0.00 | 0.00 | **5.28** |
| BREAKDOWN_SHORT | kept | 24 | 71.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 52 | 55.66 | 0.00 | 0.00 | 1.38 | 0.00 | 5.22 | 0.00 | 0.00 | **6.60** |
| DIVERGENCE_CONTINUATION | kept | 84 | 69.86 | 0.00 | 0.00 | 0.29 | 0.00 | 0.09 | 0.00 | 0.00 | **0.38** |
| FAILED_AUCTION_RECLAIM | filtered | 161 | 53.72 | 0.00 | 0.00 | 2.08 | 0.00 | 6.02 | 0.00 | 0.00 | **8.10** |
| FAILED_AUCTION_RECLAIM | kept | 216 | 71.44 | 0.00 | 0.00 | 0.21 | 0.00 | 0.07 | 0.00 | 0.00 | **0.28** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 166 | 50.26 | 0.00 | 0.00 | 2.81 | 0.00 | 7.84 | 0.00 | 0.00 | **10.65** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 184 | 70.09 | 0.00 | 0.00 | 0.03 | 0.00 | 0.07 | 0.00 | 0.00 | **0.10** |
| SR_FLIP_RETEST | filtered | 445 | 53.13 | 0.00 | 0.00 | 0.90 | 0.00 | 6.05 | 0.00 | 0.00 | **6.95** |
| SR_FLIP_RETEST | kept | 556 | 71.29 | 0.00 | 0.00 | 0.15 | 0.00 | 0.15 | 0.00 | 0.00 | **0.30** |
| TREND_PULLBACK_CONTINUATION | kept | 1 | 68.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 1 | 62.10 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| TREND_PULLBACK_EMA | kept | 24 | 78.59 | 0.00 | 0.00 | 0.60 | 0.00 | 0.00 | 0.00 | 0.00 | **0.60** |
| VOLUME_SURGE_BREAKOUT | filtered | 1 | 62.00 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 71.50 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=131 (70.8%) | PREMATURE=28 (15.1%) | NEUTRAL=26 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 103 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 10 | 2 | 0 | 0 |
| ema_crossover | 1 | 0 | 0 | 0 |
| momentum_loss | 63 | 16 | 10 | 0 |
| regime_shift | 39 | 4 | 13 | 0 |
| trailing_invalidation | 18 | 6 | 3 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 18 | 2 | 3 | 0 |
| FAILED_AUCTION_RECLAIM | 23 | 1 | 12 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 36 | 10 | 5 | 0 |
| SR_FLIP_RETEST | 47 | 15 | 5 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 10 | 2 | 0 | 2.9 | 4.1 | -0.10 | **INSUFFICIENT_SAMPLE** — only 12 classified kills (need >= 20); let data accumulate before tuning |
| ema_crossover | 1 | 0 | 0 | 0.6 | 0.0 | +0.58 | **INSUFFICIENT_SAMPLE** — only 1 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 63 | 16 | 10 | 50.5 | 21.6 | +0.33 | **KEEP** — net-helping: avg +0.33R/kill across 89 kills (saved 50.5R vs missed 21.6R) |
| regime_shift | 39 | 4 | 13 | 27.7 | 4.9 | +0.41 | **KEEP** — net-helping: avg +0.41R/kill across 56 kills (saved 27.7R vs missed 4.9R) |
| trailing_invalidation | 18 | 6 | 3 | 15.0 | 8.6 | +0.24 | **KEEP** — net-helping: avg +0.24R/kill across 27 kills (saved 15.0R vs missed 8.6R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `21272`
- `Path funnel` emissions: `7`
- `Regime distribution` emissions: `7`
- `QUIET_SCALP_BLOCK` events: `391`
- `confidence_gate` events: `1921`
- `free_channel_post` events: `95`
- `pre_tp_fire` events: `46`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **46**
- Avg resolved threshold: **0.376%** raw → avg net **+3.06%** @ 10x
- Avg time-to-fire from dispatch: **376s**
- By threshold source: stamped=46

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 19 | 0.337% | +2.67% | 310 | stamped=19 |
| LIQUIDITY_SWEEP_REVERSAL | 16 | 0.440% | +3.70% | 468 | stamped=16 |
| FAILED_AUCTION_RECLAIM | 6 | 0.333% | +2.63% | 119 | stamped=6 |
| DIVERGENCE_CONTINUATION | 5 | 0.369% | +2.99% | 636 | stamped=5 |
- Top symbols: HUSDT=6, JTOUSDT=4, XPLUSDT=4, PLAYUSDT=4, RENDERUSDT=3, 1000PEPEUSDT=2, SEIUSDT=2, FETUSDT=2, HBARUSDT=2, APTUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 44327 | 44327 | 44327 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **95**

| Source | Count |
|---|---:|
| pre_tp | 46 |
| signal_close | 45 |
| regime_shift | 4 |

- By severity: HIGH=95

## Dependency readiness
- cvd: presence[present=46799] state[populated=46799] buckets[many=46799] sources[none] quality[none]
- funding_rate: presence[absent=1492, present=45307] state[empty=1492, populated=45307] buckets[few=45307, none=1492] sources[none] quality[none]
- liquidation_clusters: presence[absent=25653, present=21146] state[empty=25653, populated=21146] buckets[few=17465, none=25653, some=3681] sources[none] quality[none]
- oi_snapshot: presence[absent=1160, present=45639] state[empty=1160, populated=45639] buckets[many=45639, none=1160] sources[none] quality[none]
- order_book: presence[absent=39207, present=7592] state[populated=7592, unavailable=39207] buckets[few=7592, none=39207] sources[book_ticker=7592, unavailable=39207] quality[none=39207, top_of_book_only=7592]
- orderblocks: presence[absent=46799] state[empty=46799] buckets[none=46799] sources[not_implemented=46799] quality[none]
- recent_ticks: presence[present=46799] state[populated=46799] buckets[many=46799] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `40.41783308982849` sec
- Median create→first breach: `695.7423751354218` sec
- Median create→terminal: `689.7301390171051` sec
- Median first breach→terminal: `16.06648588180542` sec
- Fast-failure buckets: `{"under_120s": {"count": 4, "pct": 8.9}, "under_180s": {"count": 5, "pct": 11.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 11, "pct": 11.1}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0054 | None | 402.36929655075073 |
| DIVERGENCE_CONTINUATION | 11 | 11 | 0.0 | 9.1 | 0.0 | 45.5 | 0.036 | 644.4490364789963 | 733.052482843399 |
| FAILED_AUCTION_RECLAIM | 22 | 22 | 0.0 | 4.5 | 0.0 | 27.3 | -0.0924 | 369.60321402549744 | 268.42776000499725 |
| LIQUIDITY_SWEEP_REVERSAL | 26 | 26 | 0.0 | 11.5 | 0.0 | 61.5 | 0.0508 | 654.9900060892105 | 757.2970910072327 |
| SR_FLIP_RETEST | 36 | 36 | 0.0 | 0.0 | 0.0 | 52.8 | 0.1161 | 720.8160084486008 | 735.2998689413071 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | -0.2463 | None | 871.5735919475555 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 4767 | 187 | 2477 | 0.0 | 0.0 | 720.8160084486008 | 735.2998689413071 | 2290 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 465 | 3 | 430 | 0.0 | 0.0 | None | 871.5735919475555 | 35 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `410`
- Gating Δ: `11425`
- No-generation Δ: `643725`
- Fast failures Δ: `-2`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.2437, "current_avg_pnl": 0.036, "current_win_rate": 0.0, "previous_avg_pnl": -0.2077, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.4494, "current_avg_pnl": -0.0924, "current_win_rate": 0.0, "previous_avg_pnl": 0.357, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.1987, "current_avg_pnl": 0.0508, "current_win_rate": 0.0, "previous_avg_pnl": -0.1479, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1533, "current_avg_pnl": 0.1161, "current_win_rate": 0.0, "previous_avg_pnl": -0.0372, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 187, "geometry_changed_delta": 0, "geometry_preserved_delta": 2290, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 390.51, "median_terminal_delta_sec": 376.18, "sl_rate_delta": -25.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 35, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 871.57, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **QUIET_COMPRESSION_BREAK**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
