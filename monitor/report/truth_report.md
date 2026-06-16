# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `15` sec (warning=False)
- Latest performance record age: `900` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2225 | 2225 | 2027 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 28128 | 28128 | 23882 | 32 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 225652 | 224949 | 728 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 203279 | 203299 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 202516 | 196291 | 6956 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 203347 | 193969 | 9973 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 226800 | 226467 | 395 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 225515 | 225518 | 16 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 203957 | 204015 | 13 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 225683 | 225692 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 203306 | 203330 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 202340 | 201206 | 1308 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 201169 | 194787 | 7464 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 200102 | 186423 | 14520 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 200951 | 200630 | 368 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 225576 | 225310 | 337 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 225535 | 225562 | 10 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 42912 | 42912 | 33615 | 115 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 1149 | 1149 | 1124 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 65 | 65 | 65 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 65290 | 65290 | 58271 | 82 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 15 | 15 | 14 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 83 | 83 | 82 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 9450 | 9450 | 9449 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 31682 | 31682 | 13600 | 165 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 571 | 571 | 505 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2746 | 2746 | 2153 | 3 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 188 | 188 | 92 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=224949): breakout_not_found=120738, basic_filters_failed=70022, retest_proximity_failed=24923, volume_spike_missing=4705, ema_alignment_reject=3290, insufficient_candles=1162, missing_fvg_or_orderblock=109
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=203299): cls_disabled_merged_into_lsr=203299
- **EVAL::DIVERGENCE_CONTINUATION** (total=196291): cvd_divergence_failed=66885, basic_filters_failed=61735, h1_trend_not_aligned=33368, retest_proximity_failed=20854, regime_blocked=10542, ema_alignment_reject=2290, missing_fvg_or_orderblock=521, cvd_insufficient=89, missing_cvd=7
- **EVAL::FAILED_AUCTION_RECLAIM** (total=193969): auction_not_detected=69485, basic_filters_failed=55614, reclaim_hold_failed=28028, regime_blocked=22658, tail_too_small=18181, rsi_reject=3
- **EVAL::FUNDING_EXTREME** (total=226467): funding_not_extreme=148088, basic_filters_failed=69792, missing_funding_rate=5728, ema_alignment_reject=1838, cvd_divergence_failed=500, rsi_reject=317, momentum_reject=81, insufficient_candles=70, missing_fvg_or_orderblock=53
- **EVAL::LIQUIDATION_REVERSAL** (total=225518): cascade_threshold_not_met=149503, basic_filters_failed=70074, cvd_divergence_failed=2920, rsi_reject=2177, insufficient_candles=753, volume_spike_missing=44, missing_fvg_or_orderblock=42, cvd_insufficient=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=204015): no_ma_cross=140061, basic_filters_failed=61749, ma_cross_cooldown=2205
- **EVAL::OPENING_RANGE_BREAKOUT** (total=225692): feature_disabled=225692
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=203330): regime_blocked=142749, breakout_not_found=32682, basic_filters_failed=23913, adx_reject=3963, ema_alignment_reject=13, rsi_reject=10
- **EVAL::QUIET_COMPRESSION_BREAK** (total=201206): regime_blocked=82991, compression_not_detected=76274, basic_filters_failed=31696, volume_confirmation_failed=7512, breakout_not_detected=1475, macd_reject=1199, missing_fvg_or_orderblock=59
- **EVAL::SR_FLIP_RETEST** (total=194787): basic_filters_failed=55593, retest_out_of_zone=41058, flip_close_not_confirmed=36046, reclaim_hold_failed=27673, regime_blocked=22592, ema_alignment_reject=7094, wick_quality_failed=4291, missing_fvg_or_orderblock=416, rsi_reject=24
- **EVAL::STANDARD** (total=186423): adx_reject=46491, momentum_reject=39244, basic_filters_failed=35823, sweeps_not_detected=26888, ema_alignment_reject=21137, macd_reject=9305, rsi_reject=6876, invalid_sl_geometry=659
- **EVAL::TREND_PULLBACK** (total=200630): h1_trend_not_aligned=46431, h1_pullback_not_confirmed=41617, ema_not_tested_prev=33301, basic_filters_failed=31301, ema_alignment_reject=20980, regime_blocked=15986, no_ema_reclaim_close=7278, body_conviction_fail=1505, rsi_reject=1215, prev_already_above_emas=446, prev_already_below_emas=172, momentum_flat=105, ema21_not_tagged=90, no_prev_low_break=87, momentum_reject=69, no_prev_high_break=47
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=225310): breakout_not_found=114071, basic_filters_failed=70019, retest_proximity_failed=31904, ema_alignment_reject=4021, volume_spike_missing=3902, insufficient_candles=1162, missing_fvg_or_orderblock=231
- **EVAL::WHALE_MOMENTUM** (total=225562): momentum_reject=160876, recent_ticks_insufficient=41945, basic_filters_failed=22736, insufficient_candles=5

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 418622 | 36.3% |
| RANGING | 325509 | 28.2% |
| TRENDING_UP | 159499 | 13.8% |
| TRENDING_DOWN | 156681 | 13.6% |
| VOLATILE | 93331 | 8.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **789**
- Average confidence gap to threshold: **12.10** (samples=789) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SNDKUSDT=81, LITEUSDT=81, XMRUSDT=61, TRXUSDT=57, LTCUSDT=50, SOLUSDT=44, MSTRUSDT=34, BZUSDT=34, AVAXUSDT=30, DOTUSDT=29

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 27 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 371 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 50 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 562 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 550 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 247 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2738 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 969 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 157 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1122 |
| POST_DISPLACEMENT_CONTINUATION | kept | min_confidence_pass | 1 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 1625 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 328 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3469 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 27 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 21 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 8 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 7 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 85 |
| WHALE_MOMENTUM | filtered | min_confidence | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 27 | 62.21 | 65.00 | 2.79 | 19.62 | 19.19 | 20.00 | 0.00 | 5.04 |
| BREAKDOWN_SHORT | kept | 1 | 77.70 | 65.00 | -12.70 | 17.80 | 19.90 | 20.00 | 0.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 421 | 59.09 | 65.00 | 5.91 | 20.39 | 19.42 | 18.73 | 1.34 | 8.65 |
| DIVERGENCE_CONTINUATION | kept | 562 | 70.81 | 65.00 | -5.81 | 19.37 | 19.62 | 18.31 | 3.06 | -0.13 |
| FAILED_AUCTION_RECLAIM | filtered | 797 | 56.01 | 65.00 | 8.99 | 20.74 | 19.06 | 20.00 | 3.10 | 10.38 |
| FAILED_AUCTION_RECLAIM | kept | 2738 | 70.67 | 65.00 | -5.67 | 21.44 | 19.39 | 20.00 | 3.27 | 0.40 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1126 | 53.73 | 65.00 | 11.27 | 20.88 | 19.61 | 18.27 | 1.46 | 8.25 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1122 | 68.84 | 65.00 | -3.84 | 21.33 | 19.59 | 17.84 | 1.85 | 0.66 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 73.00 | 65.00 | -8.00 | 22.50 | 20.00 | 17.80 | 1.50 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 70.00 | 65.00 | -5.00 | 21.10 | 17.20 | 20.00 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 1953 | 57.59 | 65.00 | 7.41 | 20.23 | 19.87 | 16.16 | 1.73 | 8.70 |
| SR_FLIP_RETEST | kept | 3469 | 72.09 | 65.00 | -7.09 | 20.31 | 19.93 | 16.69 | 2.30 | -0.52 |
| TREND_PULLBACK_EMA | filtered | 27 | 56.49 | 65.00 | 8.51 | 19.93 | 20.00 | 20.00 | 5.50 | 0.00 |
| TREND_PULLBACK_EMA | kept | 21 | 78.41 | 65.00 | -13.41 | 19.47 | 19.83 | 19.07 | 5.57 | 0.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 61.43 | 65.00 | 3.57 | 21.82 | 17.95 | 18.83 | 3.03 | 5.67 |
| VOLUME_SURGE_BREAKOUT | kept | 85 | 72.50 | 65.00 | -7.50 | 20.55 | 19.96 | 19.86 | 3.47 | 2.06 |
| WHALE_MOMENTUM | filtered | 1 | 61.20 | 65.00 | 3.80 | 24.40 | 20.00 | 17.00 | 0.00 | 10.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 27 | 62.21 | 24.19 | 18.00 | 3.00 | 10.00 | 5.89 | 6.17 | 0.00 |
| BREAKDOWN_SHORT | kept | 1 | 77.70 | 25.00 | 18.00 | 12.00 | 14.00 | 5.00 | 6.70 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 421 | 59.09 | 22.64 | 10.90 | 6.78 | 13.20 | 6.26 | 8.25 | 1.34 |
| DIVERGENCE_CONTINUATION | kept | 562 | 70.81 | 22.45 | 16.04 | 4.70 | 12.10 | 5.72 | 7.43 | 3.06 |
| FAILED_AUCTION_RECLAIM | filtered | 797 | 56.01 | 21.45 | 15.77 | 7.20 | 11.62 | 6.88 | 6.18 | 3.10 |
| FAILED_AUCTION_RECLAIM | kept | 2738 | 70.67 | 23.05 | 15.04 | 4.42 | 11.55 | 6.24 | 7.55 | 3.27 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1126 | 53.73 | 21.52 | 14.67 | 7.93 | 11.80 | 5.41 | 6.27 | 1.46 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1122 | 68.84 | 22.96 | 15.35 | 4.55 | 12.16 | 5.87 | 6.75 | 1.85 |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 73.00 | 17.00 | 18.00 | 6.00 | 14.00 | 8.50 | 8.00 | 1.50 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 70.00 | 17.00 | 18.00 | 3.00 | 17.00 | 8.00 | 7.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 1953 | 57.59 | 20.13 | 16.32 | 5.49 | 13.12 | 5.96 | 7.14 | 1.73 |
| SR_FLIP_RETEST | kept | 3469 | 72.09 | 22.70 | 16.35 | 3.93 | 13.55 | 5.90 | 8.36 | 2.30 |
| TREND_PULLBACK_EMA | filtered | 27 | 56.49 | 18.19 | 18.00 | 3.00 | 14.00 | 5.00 | 7.80 | 5.50 |
| TREND_PULLBACK_EMA | kept | 21 | 78.41 | 21.57 | 18.00 | 3.43 | 14.00 | 9.14 | 6.70 | 5.57 |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 61.43 | 25.00 | 8.00 | 6.20 | 13.47 | 5.00 | 6.40 | 3.03 |
| VOLUME_SURGE_BREAKOUT | kept | 85 | 72.50 | 23.96 | 17.88 | 5.08 | 13.67 | 4.35 | 6.14 | 3.47 |
| WHALE_MOMENTUM | filtered | 1 | 61.20 | 25.00 | 18.00 | 6.00 | 12.00 | 8.50 | 1.70 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 27 | 62.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 1 | 77.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 421 | 59.09 | 0.00 | 0.00 | 0.47 | 0.00 | 4.25 | 0.00 | 0.00 | 0.00 | **4.72** |
| DIVERGENCE_CONTINUATION | kept | 562 | 70.81 | 0.00 | 0.00 | 0.15 | 0.00 | 0.55 | 0.00 | 0.00 | 0.00 | **0.70** |
| FAILED_AUCTION_RECLAIM | filtered | 797 | 56.01 | 0.00 | 0.00 | 1.89 | 0.00 | 6.47 | 0.00 | 0.00 | 0.00 | **8.36** |
| FAILED_AUCTION_RECLAIM | kept | 2738 | 70.67 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.05** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1126 | 53.73 | 0.00 | 0.00 | 1.33 | 0.00 | 6.23 | 0.00 | 0.00 | 0.00 | **7.56** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1122 | 68.84 | 0.00 | 0.00 | 0.62 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.63** |
| POST_DISPLACEMENT_CONTINUATION | kept | 1 | 73.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 70.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 1953 | 57.59 | 0.06 | 0.00 | 1.95 | 0.00 | 2.59 | 0.00 | 0.00 | 0.11 | **4.71** |
| SR_FLIP_RETEST | kept | 3469 | 72.09 | 0.00 | 0.00 | 0.23 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.25** |
| TREND_PULLBACK_EMA | filtered | 27 | 56.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 21 | 78.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 15 | 61.43 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 85 | 72.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.05 | 0.00 | 0.00 | 0.00 | **0.05** |
| WHALE_MOMENTUM | filtered | 1 | 61.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=33 (80.5%) | PREMATURE=6 (14.6%) | NEUTRAL=2 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 27 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 9 | 1 | 0 | 0 |
| ema_crossover | 1 | 0 | 1 | 0 |
| momentum_loss | 21 | 3 | 1 | 0 |
| trailing_invalidation | 2 | 2 | 0 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 9 | 1 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 6 | 1 | 1 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 15 | 4 | 1 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 9 | 1 | 0 | 3.0 | 1.6 | +0.14 | **INSUFFICIENT_SAMPLE** — only 10 classified kills (need >= 20); let data accumulate before tuning |
| ema_crossover | 1 | 0 | 1 | 0.6 | 0.0 | +0.32 | **INSUFFICIENT_SAMPLE** — only 2 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 21 | 3 | 1 | 12.9 | 4.5 | +0.34 | **KEEP** — net-helping: avg +0.34R/kill across 25 kills (saved 12.9R vs missed 4.5R) |
| trailing_invalidation | 2 | 2 | 0 | 1.3 | 2.8 | -0.40 | **INSUFFICIENT_SAMPLE** — only 4 classified kills (need >= 20); let data accumulate before tuning |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4820650`
- `Path funnel` emissions: `163`
- `Regime distribution` emissions: `163`
- `QUIET_SCALP_BLOCK` events: `789`
- `confidence_gate` events: `12367`
- `free_channel_post` events: `95`
- `pre_tp_fire` events: `43`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **43**
- Avg resolved threshold: **0.419%** raw → avg net **+3.49%** @ 10x
- Avg time-to-fire from dispatch: **264s**
- By threshold source: stamped=43

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| FAILED_AUCTION_RECLAIM | 16 | 0.296% | +2.26% | 319 | stamped=16 |
| SR_FLIP_RETEST | 10 | 0.350% | +2.80% | 207 | stamped=10 |
| LIQUIDITY_SWEEP_REVERSAL | 9 | 0.659% | +5.89% | 196 | stamped=9 |
| DIVERGENCE_CONTINUATION | 8 | 0.483% | +4.13% | 300 | stamped=8 |
- Top symbols: MRVLUSDT=5, SNDKUSDT=5, MEGAUSDT=4, CHIPUSDT=4, BANANAS31USDT=3, RIFUSDT=3, COAIUSDT=2, BABYUSDT=2, 1000PEPEUSDT=2, JELLYJELLYUSDT=2

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **5**
- Total REST-fallback activations: **4**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 4 | 3544 | 4804 | 10542 | 0 |
| futures_liq | 1 | 2448 | 2448 | 2448 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 4 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **95**

| Source | Count |
|---|---:|
| signal_close | 46 |
| pre_tp | 43 |
| regime_shift | 6 |

- By severity: HIGH=95

## Dependency readiness
- cvd: presence[absent=4455, present=958626] state[empty=4455, populated=958626] buckets[few=426, many=954975, none=4455, some=3225] sources[none] quality[none]
- funding_rate: presence[absent=14975, present=948106] state[empty=14975, populated=948106] buckets[few=948106, none=14975] sources[none] quality[none]
- liquidation_clusters: presence[absent=446288, present=516793] state[empty=446288, populated=516793] buckets[few=400783, none=446288, some=116010] sources[none] quality[none]
- oi_snapshot: presence[absent=13686, present=949395] state[empty=13686, populated=949395] buckets[few=962, many=943165, none=13686, some=5268] sources[none] quality[none]
- order_book: presence[absent=241999, present=721082] state[populated=721082, unavailable=241999] buckets[few=721082, none=241999] sources[book_ticker=721082, unavailable=241999] quality[none=241999, top_of_book_only=721082]
- orderblocks: presence[absent=963081] state[empty=963081] buckets[none=963081] sources[not_implemented=963081] quality[none]
- recent_ticks: presence[absent=7822, present=955259] state[empty=7822, populated=955259] buckets[many=955259, none=7822] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.532710075378418` sec
- Median create→first breach: `382.9898910522461` sec
- Median create→terminal: `416.02227902412415` sec
- Median first breach→terminal: `1.228882908821106` sec
- Fast-failure buckets: `{"under_120s": {"count": 6, "pct": 13.0}, "under_180s": {"count": 8, "pct": 17.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 3, "pct": 6.5}}`
- ~3 minute terminal-close behavior: `{"count": 14, "pct": 16.3}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 18 | 18 | 0.0 | 5.6 | 0.0 | 44.4 | 0.3627 | 357.12242603302 | 242.1426421403885 |
| FAILED_AUCTION_RECLAIM | 25 | 25 | 0.0 | 0.0 | 0.0 | 64.0 | 0.1969 | 808.0845359563828 | 909.2586710453033 |
| LIQUIDITY_SWEEP_REVERSAL | 13 | 13 | 0.0 | 15.4 | 0.0 | 69.2 | 0.1267 | 289.1186611652374 | 515.396073102951 |
| SR_FLIP_RETEST | 31 | 31 | 0.0 | 16.1 | 0.0 | 32.3 | -0.1686 | 355.01948392391205 | 355.6982034444809 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 31682 | 165 | 13600 | 0.0 | 16.1 | 355.01948392391205 | 355.6982034444809 | 18082 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 571 | 0 | 505 | 0.0 | 0.0 | None | None | 66 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `70`
- Gating Δ: `7622`
- No-generation Δ: `485158`
- Fast failures Δ: `5`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.628, "current_avg_pnl": 0.3627, "current_win_rate": 0.0, "previous_avg_pnl": -0.2653, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0088, "current_avg_pnl": 0.1969, "current_win_rate": 0.0, "previous_avg_pnl": 0.2057, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.6252, "current_avg_pnl": 0.1267, "current_win_rate": 0.0, "previous_avg_pnl": 0.7519, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0782, "current_avg_pnl": -0.1686, "current_win_rate": 0.0, "previous_avg_pnl": -0.0904, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 21, "geometry_changed_delta": 0, "geometry_preserved_delta": 761, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 4.8, "median_terminal_delta_sec": -146.1, "sl_rate_delta": 7.8, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 66, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **BREAKDOWN_SHORT**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
