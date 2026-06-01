# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, DIVERGENCE_CONTINUATION, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `65` sec (warning=False)
- Latest performance record age: `649` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 225 | 225 | 63 | 4 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2264 | 2264 | 1886 | 20 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 14258 | 14184 | 80 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 13841 | 13841 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 13776 | 12967 | 874 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 13844 | 13110 | 780 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 14381 | 14335 | 53 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 14243 | 14247 | 2 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 13890 | 13882 | 20 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 14264 | 14264 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 13843 | 13839 | 5 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 13770 | 13775 | 0 | 0 | 0 | 0 | non-generating (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 13645 | 12039 | 1723 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 13560 | 12346 | 1268 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 13614 | 13509 | 117 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 14255 | 14208 | 50 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 14249 | 14256 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 2135 | 2135 | 1385 | 46 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 184 | 184 | 142 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 3795 | 3795 | 3320 | 38 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 26 | 26 | 22 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 8 | 8 | 4 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 4671 | 4671 | 1545 | 130 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 351 | 351 | 302 | 6 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 153 | 153 | 80 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=14184): breakout_not_found=10933, retest_proximity_failed=2049, volume_spike_missing=471, basic_filters_failed=451, ema_alignment_reject=153, insufficient_candles=93, missing_fvg_or_orderblock=34
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=13841): cls_disabled_merged_into_lsr=13841
- **EVAL::DIVERGENCE_CONTINUATION** (total=12967): cvd_divergence_failed=5445, h1_trend_not_aligned=4981, ema_alignment_reject=1579, basic_filters_failed=453, retest_proximity_failed=324, missing_fvg_or_orderblock=93, regime_blocked=92
- **EVAL::FAILED_AUCTION_RECLAIM** (total=13110): auction_not_detected=7135, reclaim_hold_failed=3317, tail_too_small=2205, basic_filters_failed=453
- **EVAL::FUNDING_EXTREME** (total=14335): funding_not_extreme=12512, ema_alignment_reject=456, basic_filters_failed=448, missing_funding_rate=426, rsi_reject=361, cvd_divergence_failed=58, momentum_reject=46, insufficient_candles=20, missing_fvg_or_orderblock=8
- **EVAL::LIQUIDATION_REVERSAL** (total=14247): cascade_threshold_not_met=13395, basic_filters_failed=451, cvd_divergence_failed=161, rsi_reject=138, insufficient_candles=93, missing_fvg_or_orderblock=7, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=13882): no_ma_cross=13021, basic_filters_failed=453, ma_cross_cooldown=408
- **EVAL::OPENING_RANGE_BREAKOUT** (total=14264): feature_disabled=14264
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=13839): regime_blocked=8125, breakout_not_found=3256, ema_alignment_reject=1649, adx_reject=694, basic_filters_failed=115
- **EVAL::QUIET_COMPRESSION_BREAK** (total=13775): compression_not_detected=7745, regime_blocked=5693, basic_filters_failed=337
- **EVAL::SR_FLIP_RETEST** (total=12039): retest_out_of_zone=3814, reclaim_hold_failed=3439, flip_close_not_confirmed=3230, wick_quality_failed=792, basic_filters_failed=451, ema_alignment_reject=167, missing_fvg_or_orderblock=143, rsi_reject=3
- **EVAL::STANDARD** (total=12346): momentum_reject=4649, adx_reject=2636, sweeps_not_detected=1638, macd_reject=1586, ema_alignment_reject=1210, basic_filters_failed=409, invalid_sl_geometry=186, rsi_reject=32
- **EVAL::TREND_PULLBACK** (total=13509): h1_trend_not_aligned=5094, ema_alignment_reject=2503, h1_pullback_not_confirmed=1543, ema_not_tested_prev=1262, no_ema_reclaim_close=1018, body_conviction_fail=790, rsi_reject=493, prev_already_above_emas=241, basic_filters_failed=213, regime_blocked=92, prev_already_below_emas=79, no_prev_high_break=64, no_prev_low_break=54, momentum_flat=38, missing_fvg_or_orderblock=10, ema21_not_tagged=10, momentum_reject=5
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=14208): breakout_not_found=10263, retest_proximity_failed=2889, basic_filters_failed=451, volume_spike_missing=367, ema_alignment_reject=129, insufficient_candles=93, missing_fvg_or_orderblock=16
- **EVAL::WHALE_MOMENTUM** (total=14256): momentum_reject=10406, recent_ticks_insufficient=3797, basic_filters_failed=53

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 24130 | 56.6% |
| TRENDING_DOWN | 10265 | 24.1% |
| TRENDING_UP | 6991 | 16.4% |
| RANGING | 1237 | 2.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **584**
- Average confidence gap to threshold: **16.65** (samples=584) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XRPUSDT=46, PUMPUSDT=24, 1000PEPEUSDT=23, INJUSDT=22, BNBUSDT=19, GENIUSUSDT=18, UNIUSDT=18, NEARUSDT=17, HIVEUSDT=16, BTCUSDT=14

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 11 |
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 6 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 22 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 30 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 16 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 52 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 154 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 44 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 174 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| FUNDING_EXTREME_SIGNAL | kept | min_confidence_pass | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 122 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 14 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 95 |
| SR_FLIP_RETEST | filtered | min_confidence | 418 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 273 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 635 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 8 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 19 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 17 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 8 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 17 | 54.57 | 65.00 | 10.43 | 20.48 | 19.85 | 20.00 | 0.00 | 12.51 |
| BREAKDOWN_SHORT | kept | 22 | 71.72 | 65.00 | -6.72 | 20.50 | 19.55 | 19.54 | 0.00 | 0.68 |
| DIVERGENCE_CONTINUATION | filtered | 46 | 56.03 | 65.00 | 8.97 | 20.93 | 19.70 | 17.63 | 2.80 | 8.74 |
| DIVERGENCE_CONTINUATION | kept | 52 | 70.15 | 65.00 | -5.15 | 20.79 | 19.60 | 17.82 | 2.02 | 0.17 |
| FAILED_AUCTION_RECLAIM | filtered | 198 | 50.74 | 65.00 | 14.26 | 20.66 | 19.34 | 20.00 | 4.26 | 11.17 |
| FAILED_AUCTION_RECLAIM | kept | 174 | 70.36 | 65.00 | -5.36 | 20.56 | 19.39 | 20.00 | 4.38 | 0.27 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 41.10 | 65.00 | 23.90 | 21.00 | 20.00 | 20.00 | 2.33 | 12.27 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 67.70 | 65.00 | -2.70 | 20.60 | 19.70 | 17.00 | 0.50 | 0.35 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 136 | 50.75 | 65.00 | 14.25 | 20.90 | 19.44 | 17.73 | 2.92 | 12.09 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 69.95 | 65.00 | -4.95 | 20.93 | 19.20 | 17.53 | 2.20 | 0.20 |
| SR_FLIP_RETEST | filtered | 691 | 51.72 | 65.00 | 13.28 | 20.89 | 19.89 | 15.91 | 2.04 | 11.43 |
| SR_FLIP_RETEST | kept | 635 | 70.64 | 65.00 | -5.64 | 20.90 | 19.94 | 15.89 | 2.20 | 0.50 |
| TREND_PULLBACK_EMA | filtered | 8 | 58.89 | 65.00 | 6.11 | 20.62 | 19.96 | 17.40 | 5.50 | 1.80 |
| TREND_PULLBACK_EMA | kept | 19 | 78.01 | 65.00 | -13.01 | 20.66 | 19.71 | 19.28 | 5.53 | -1.64 |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 54.53 | 65.00 | 10.47 | 21.42 | 19.79 | 18.06 | 2.90 | 7.43 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 67.93 | 65.00 | -2.93 | 21.53 | 18.40 | 19.17 | 3.17 | 3.67 |
| WHALE_MOMENTUM | filtered | 1 | 46.90 | 65.00 | 18.10 | 20.60 | 20.00 | 17.00 | 0.00 | 21.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 17 | 54.57 | 22.53 | 13.88 | 7.06 | 12.65 | 5.35 | 5.61 | 0.00 |
| BREAKDOWN_SHORT | kept | 22 | 71.72 | 24.27 | 18.00 | 4.77 | 13.23 | 6.00 | 6.13 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 46 | 56.03 | 21.87 | 14.30 | 6.00 | 11.67 | 5.25 | 8.02 | 2.80 |
| DIVERGENCE_CONTINUATION | kept | 52 | 70.15 | 21.92 | 17.23 | 4.50 | 11.56 | 5.78 | 8.41 | 2.02 |
| FAILED_AUCTION_RECLAIM | filtered | 198 | 50.74 | 22.00 | 14.12 | 7.20 | 12.05 | 6.74 | 5.08 | 4.26 |
| FAILED_AUCTION_RECLAIM | kept | 174 | 70.36 | 22.44 | 14.16 | 5.43 | 11.47 | 6.50 | 6.29 | 4.38 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 41.10 | 25.00 | 8.00 | 3.00 | 14.00 | 7.33 | 8.70 | 2.33 |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 67.70 | 25.00 | 8.00 | 3.00 | 14.00 | 9.25 | 8.30 | 0.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 136 | 50.75 | 22.38 | 14.12 | 7.04 | 12.64 | 5.85 | 6.17 | 2.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 69.95 | 23.67 | 14.29 | 5.21 | 12.75 | 5.39 | 6.66 | 2.20 |
| SR_FLIP_RETEST | filtered | 691 | 51.72 | 21.64 | 14.05 | 7.09 | 13.53 | 5.94 | 5.94 | 2.04 |
| SR_FLIP_RETEST | kept | 635 | 70.64 | 22.72 | 15.37 | 4.80 | 13.66 | 6.22 | 7.40 | 2.20 |
| TREND_PULLBACK_EMA | filtered | 8 | 58.89 | 21.00 | 18.00 | 3.00 | 14.00 | 5.00 | 9.19 | 5.50 |
| TREND_PULLBACK_EMA | kept | 19 | 78.01 | 21.21 | 18.00 | 3.16 | 14.16 | 6.97 | 9.23 | 5.53 |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 54.53 | 20.96 | 13.60 | 6.36 | 13.68 | 5.56 | 6.10 | 2.90 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 67.93 | 25.00 | 14.67 | 5.00 | 12.33 | 5.00 | 6.43 | 3.17 |
| WHALE_MOMENTUM | filtered | 1 | 46.90 | 17.00 | 8.00 | 12.00 | 17.00 | 8.50 | 6.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 17 | 54.57 | 0.00 | 0.00 | 0.00 | 0.00 | 9.74 | 0.00 | 0.00 | 0.00 | **9.74** |
| BREAKDOWN_SHORT | kept | 22 | 71.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 46 | 56.03 | 0.00 | 0.00 | 1.77 | 0.00 | 5.17 | 0.00 | 0.00 | 0.00 | **6.94** |
| DIVERGENCE_CONTINUATION | kept | 52 | 70.15 | 0.00 | 0.00 | 0.28 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | **0.70** |
| FAILED_AUCTION_RECLAIM | filtered | 198 | 50.74 | 0.00 | 0.00 | 0.75 | 0.00 | 8.57 | 0.00 | 0.00 | 0.00 | **9.32** |
| FAILED_AUCTION_RECLAIM | kept | 174 | 70.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **0.04** |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 41.10 | 0.00 | 0.00 | 12.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.27** |
| FUNDING_EXTREME_SIGNAL | kept | 2 | 67.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 136 | 50.75 | 0.00 | 0.00 | 4.51 | 0.00 | 7.55 | 0.00 | 0.00 | 0.00 | **12.06** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 95 | 69.95 | 0.00 | 0.00 | 0.10 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.23** |
| SR_FLIP_RETEST | filtered | 691 | 51.72 | 0.09 | 0.00 | 1.35 | 0.00 | 5.81 | 0.00 | 0.00 | 0.42 | **7.67** |
| SR_FLIP_RETEST | kept | 635 | 70.64 | 0.00 | 0.00 | 0.21 | 0.00 | 0.26 | 0.00 | 0.00 | 0.02 | **0.49** |
| TREND_PULLBACK_EMA | filtered | 8 | 58.89 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| TREND_PULLBACK_EMA | kept | 19 | 78.01 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.25** |
| VOLUME_SURGE_BREAKOUT | filtered | 25 | 54.53 | 0.00 | 0.00 | 1.73 | 0.00 | 2.07 | 0.00 | 0.00 | 0.43 | **4.23** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 67.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 1 | 46.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=24 (75.0%) | PREMATURE=6 (18.8%) | NEUTRAL=2 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 18 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 8 | 0 | 0 | 0 |
| momentum_loss | 4 | 3 | 2 | 0 |
| regime_shift | 8 | 0 | 0 | 0 |
| trailing_invalidation | 4 | 3 | 0 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 0 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 2 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 1 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 9 | 2 | 2 | 0 |
| TREND_PULLBACK_EMA | 0 | 3 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 8 | 0 | 0 | 2.9 | 0.0 | +0.37 | **INSUFFICIENT_SAMPLE** — only 8 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 4 | 3 | 2 | 2.0 | 4.8 | -0.31 | **INSUFFICIENT_SAMPLE** — only 9 classified kills (need >= 20); let data accumulate before tuning |
| regime_shift | 8 | 0 | 0 | 4.1 | 0.0 | +0.52 | **INSUFFICIENT_SAMPLE** — only 8 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 4 | 3 | 0 | 3.0 | 4.2 | -0.18 | **INSUFFICIENT_SAMPLE** — only 7 classified kills (need >= 20); let data accumulate before tuning |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `12173`
- `Path funnel` emissions: `6`
- `Regime distribution` emissions: `6`
- `QUIET_SCALP_BLOCK` events: `584`
- `confidence_gate` events: `2130`
- `free_channel_post` events: `78`
- `pre_tp_fire` events: `34`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **34**
- Avg resolved threshold: **0.397%** raw → avg net **+3.27%** @ 10x
- Avg time-to-fire from dispatch: **320s**
- By threshold source: stamped=34

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 18 | 0.351% | +2.81% | 384 | stamped=18 |
| FAILED_AUCTION_RECLAIM | 7 | 0.328% | +2.58% | 304 | stamped=7 |
| LIQUIDITY_SWEEP_REVERSAL | 6 | 0.491% | +4.21% | 178 | stamped=6 |
| DIVERGENCE_CONTINUATION | 2 | 0.328% | +2.58% | 220 | stamped=2 |
| FUNDING_EXTREME_SIGNAL | 1 | 1.280% | +12.10% | 347 | stamped=1 |
- Top symbols: OPGUSDT=5, GENIUSUSDT=4, HOMEUSDT=3, VTHOUSDT=2, PUNDIXUSDT=2, 1000PEPEUSDT=2, HIVEUSDT=2, HUSDT=2, PRLUSDT=1, APRUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **78**

| Source | Count |
|---|---:|
| signal_close | 38 |
| pre_tp | 34 |
| regime_shift | 3 |
| signal_highlight | 3 |

- By severity: HIGH=78

## Dependency readiness
- cvd: presence[present=40010] state[populated=40010] buckets[few=6, many=39953, some=51] sources[none] quality[none]
- funding_rate: presence[absent=823, present=39187] state[empty=823, populated=39187] buckets[few=39187, none=823] sources[none] quality[none]
- liquidation_clusters: presence[absent=16920, present=23090] state[empty=16920, populated=23090] buckets[few=17952, none=16920, some=5138] sources[none] quality[none]
- oi_snapshot: presence[absent=653, present=39357] state[empty=653, populated=39357] buckets[few=121, many=39020, none=653, some=216] sources[none] quality[none]
- order_book: presence[absent=32674, present=7336] state[populated=7336, unavailable=32674] buckets[few=7336, none=32674] sources[book_ticker=7336, unavailable=32674] quality[none=32674, top_of_book_only=7336]
- orderblocks: presence[absent=40010] state[empty=40010] buckets[none=40010] sources[not_implemented=40010] quality[none]
- recent_ticks: presence[absent=78, present=39932] state[empty=78, populated=39932] buckets[many=39932, none=78] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `32.43958497047424` sec
- Median create→first breach: `490.20501017570496` sec
- Median create→terminal: `371.8051664829254` sec
- Median first breach→terminal: `6.681749105453491` sec
- Fast-failure buckets: `{"under_120s": {"count": 6, "pct": 20.7}, "under_180s": {"count": 7, "pct": 24.1}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 3, "pct": 10.3}}`
- ~3 minute terminal-close behavior: `{"count": 9, "pct": 13.2}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0169 | None | 768.2377109527588 |
| DIVERGENCE_CONTINUATION | 6 | 6 | 0.0 | 0.0 | 0.0 | 33.3 | 0.2873 | 358.65739917755127 | 276.34065306186676 |
| FAILED_AUCTION_RECLAIM | 12 | 12 | 0.0 | 8.3 | 0.0 | 58.3 | -0.2367 | 1021.011568069458 | 373.4962875843048 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 100.0 | 1.9786 | 773.282429933548 | 797.2904410362244 |
| LIQUIDITY_SWEEP_REVERSAL | 9 | 9 | 0.0 | 0.0 | 0.0 | 66.7 | -0.0726 | 271.52944684028625 | 171.78124499320984 |
| SR_FLIP_RETEST | 33 | 33 | 0.0 | 9.1 | 0.0 | 54.5 | -0.0025 | 528.5456235408783 | 494.3698060512543 |
| TREND_PULLBACK_EMA | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1104 | None | 473.8485689163208 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0893 | None | 200.92837595939636 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 4671 | 130 | 1545 | 0.0 | 9.1 | 528.5456235408783 | 494.3698060512543 | 3126 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 351 | 6 | 302 | 0.0 | 0.0 | None | 473.8485689163208 | 49 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `244`
- Gating Δ: `8753`
- No-generation Δ: `204802`
- Fast failures Δ: `7`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.0169, "current_avg_pnl": -0.0169, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.2873, "current_avg_pnl": 0.2873, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.2367, "current_avg_pnl": -0.2367, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.0726, "current_avg_pnl": -0.0726, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0025, "current_avg_pnl": -0.0025, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.1104, "current_avg_pnl": 0.1104, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 130, "geometry_changed_delta": 0, "geometry_preserved_delta": 3126, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 528.55, "median_terminal_delta_sec": 494.37, "sl_rate_delta": 9.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 49, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 473.85, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
