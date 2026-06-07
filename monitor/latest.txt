# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `15` sec (warning=False)
- Latest performance record age: `502` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 670 | 670 | 586 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 17317 | 17317 | 15178 | 22 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 189644 | 189496 | 184 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 162845 | 162860 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 162336 | 156994 | 5834 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 162914 | 158374 | 4806 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 190938 | 190005 | 1040 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 189537 | 189546 | 9 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 163190 | 163262 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 189684 | 189691 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 162865 | 162886 | 24 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 162313 | 162250 | 84 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 160961 | 150828 | 11362 | 0 | 0 | 0 | low-sample (retest_out_of_zone) |
| EVAL::STANDARD | 160025 | 148131 | 12648 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 160784 | 160703 | 121 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 189573 | 188900 | 739 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 189556 | 189566 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 16205 | 16205 | 12057 | 67 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 4279 | 4279 | 4246 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 44 | 44 | 44 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 60436 | 60436 | 52394 | 110 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 8 | 8 | 7 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 128 | 128 | 128 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 176 | 176 | 141 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 48550 | 48550 | 35610 | 45 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 423 | 423 | 404 | 2 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 3955 | 3955 | 3127 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=189497): breakout_not_found=131987, basic_filters_failed=35607, retest_proximity_failed=14331, ema_alignment_reject=5687, volume_spike_missing=1725, missing_fvg_or_orderblock=111, rsi_reject=49
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=162861): cls_disabled_merged_into_lsr=162861
- **EVAL::DIVERGENCE_CONTINUATION** (total=156995): cvd_divergence_failed=55125, h1_trend_not_aligned=36988, basic_filters_failed=30075, ema_alignment_reject=20418, retest_proximity_failed=13095, regime_blocked=835, missing_fvg_or_orderblock=459
- **EVAL::FAILED_AUCTION_RECLAIM** (total=158375): auction_not_detected=65834, reclaim_hold_failed=29152, basic_filters_failed=27035, tail_too_small=24897, regime_blocked=11457
- **EVAL::FUNDING_EXTREME** (total=190006): funding_not_extreme=141820, basic_filters_failed=33919, ema_alignment_reject=6776, missing_funding_rate=4539, cvd_divergence_failed=1127, momentum_reject=1030, rsi_reject=746, missing_fvg_or_orderblock=49
- **EVAL::LIQUIDATION_REVERSAL** (total=189547): cascade_threshold_not_met=150429, basic_filters_failed=35604, cvd_divergence_failed=1857, rsi_reject=1518, missing_fvg_or_orderblock=102, volume_spike_missing=37
- **EVAL::MA_CROSS_TREND_SHIFT** (total=163263): no_ma_cross=131907, basic_filters_failed=30081, ma_cross_cooldown=1275
- **EVAL::OPENING_RANGE_BREAKOUT** (total=189692): feature_disabled=189692
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=162887): regime_blocked=80567, breakout_not_found=62824, basic_filters_failed=13542, adx_reject=5929, ema_alignment_reject=25
- **EVAL::QUIET_COMPRESSION_BREAK** (total=162251): regime_blocked=93435, compression_not_detected=50292, basic_filters_failed=13491, breakout_not_detected=4671, volume_confirmation_failed=272, rsi_reject=90
- **EVAL::SR_FLIP_RETEST** (total=150829): retest_out_of_zone=37725, reclaim_hold_failed=32637, flip_close_not_confirmed=30518, basic_filters_failed=27030, regime_blocked=11408, ema_alignment_reject=6153, wick_quality_failed=4973, missing_fvg_or_orderblock=359, rsi_reject=26
- **EVAL::STANDARD** (total=148131): momentum_reject=62404, basic_filters_failed=21010, ema_alignment_reject=18619, adx_reject=15862, sweeps_not_detected=15383, macd_reject=10377, invalid_sl_geometry=3559, rsi_reject=914, mtf_reject=3
- **EVAL::TREND_PULLBACK** (total=160704): h1_trend_not_aligned=44113, ema_alignment_reject=42700, h1_pullback_not_confirmed=34911, basic_filters_failed=14832, ema_not_tested_prev=12515, no_ema_reclaim_close=7250, rsi_reject=1323, regime_blocked=1179, body_conviction_fail=1165, prev_already_above_emas=353, prev_already_below_emas=116, no_prev_high_break=100, momentum_flat=42, momentum_reject=41, no_prev_low_break=35, ema21_not_tagged=23, missing_fvg_or_orderblock=6
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=188901): breakout_not_found=107453, basic_filters_failed=35607, retest_proximity_failed=35505, volume_spike_missing=7740, ema_alignment_reject=2271, missing_fvg_or_orderblock=316, rsi_reject=9
- **EVAL::WHALE_MOMENTUM** (total=189567): momentum_reject=168752, recent_ticks_insufficient=17337, basic_filters_failed=3478

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 388250 | 38.4% |
| TRENDING_UP | 347239 | 34.4% |
| TRENDING_DOWN | 98544 | 9.8% |
| QUIET | 88926 | 8.8% |
| VOLATILE | 86900 | 8.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **221**
- Average confidence gap to threshold: **16.26** (samples=221) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BZUSDT=120, SPYUSDT=50, TRXUSDT=20, BNBUSDT=13, UNIUSDT=11, QQQUSDT=4, BTCUSDT=2, MSTRUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 21 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 95 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 565 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 497 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 70 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1346 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1346 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 26 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 2151 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 22 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 2 |
| SR_FLIP_RETEST | filtered | min_confidence | 3387 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 103 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1171 |
| TREND_PULLBACK_CONTINUATION | filtered | min_confidence | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 5 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 10 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 123 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 21 | 54.30 | 65.00 | 10.70 | 19.85 | 20.00 | 20.00 | 0.00 | 12.00 |
| DIVERGENCE_CONTINUATION | filtered | 95 | 58.34 | 65.00 | 6.66 | 20.58 | 19.68 | 16.92 | 1.68 | 9.57 |
| DIVERGENCE_CONTINUATION | kept | 565 | 69.72 | 65.00 | -4.72 | 19.22 | 19.25 | 18.40 | 2.15 | -2.28 |
| FAILED_AUCTION_RECLAIM | filtered | 567 | 52.63 | 65.00 | 12.37 | 20.63 | 19.47 | 20.00 | 2.88 | 8.93 |
| FAILED_AUCTION_RECLAIM | kept | 1346 | 72.82 | 65.00 | -7.82 | 20.48 | 19.67 | 20.00 | 4.44 | 0.27 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1372 | 55.49 | 65.00 | 9.51 | 19.81 | 19.57 | 18.42 | 1.92 | 6.30 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2151 | 71.25 | 65.00 | -6.25 | 20.65 | 19.90 | 18.07 | 3.27 | 0.67 |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 52.25 | 65.00 | 12.75 | 20.32 | 20.00 | 20.00 | 0.00 | 7.50 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 80.10 | 65.00 | -15.10 | 22.50 | 20.00 | 20.00 | 0.00 | -1.50 |
| SR_FLIP_RETEST | filtered | 3490 | 51.45 | 65.00 | 13.55 | 20.38 | 19.87 | 16.01 | 1.99 | 7.08 |
| SR_FLIP_RETEST | kept | 1171 | 69.45 | 65.00 | -4.45 | 19.74 | 19.91 | 16.12 | 1.66 | -0.05 |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 59.30 | 65.00 | 5.70 | 20.70 | 20.00 | 16.40 | 0.00 | 9.00 |
| TREND_PULLBACK_EMA | filtered | 5 | 59.30 | 65.00 | 5.70 | 20.20 | 19.60 | 20.00 | 4.00 | 9.00 |
| TREND_PULLBACK_EMA | kept | 10 | 72.55 | 65.00 | -7.55 | 20.78 | 19.96 | 18.19 | 5.55 | -2.70 |
| VOLUME_SURGE_BREAKOUT | filtered | 123 | 55.30 | 65.00 | 9.70 | 20.39 | 19.12 | 20.00 | 2.98 | 8.56 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 68.40 | 65.00 | -3.40 | 19.80 | 19.20 | 20.00 | 4.50 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 21 | 54.30 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 9.30 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 95 | 58.34 | 23.48 | 9.68 | 5.31 | 11.23 | 7.83 | 8.70 | 1.68 |
| DIVERGENCE_CONTINUATION | kept | 565 | 69.72 | 20.00 | 17.88 | 3.91 | 11.92 | 5.17 | 8.78 | 2.15 |
| FAILED_AUCTION_RECLAIM | filtered | 567 | 52.63 | 21.94 | 16.90 | 4.74 | 12.43 | 6.50 | 5.37 | 2.88 |
| FAILED_AUCTION_RECLAIM | kept | 1346 | 72.82 | 22.49 | 16.06 | 4.39 | 11.53 | 5.94 | 8.25 | 4.44 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1372 | 55.49 | 21.79 | 14.01 | 7.47 | 13.84 | 5.30 | 5.08 | 1.92 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2151 | 71.25 | 22.23 | 14.05 | 4.93 | 13.13 | 5.83 | 8.46 | 3.27 |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 52.25 | 18.82 | 18.00 | 10.36 | 14.00 | 5.80 | 4.36 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 2 | 80.10 | 17.00 | 18.00 | 13.50 | 15.50 | 6.75 | 9.35 | 0.00 |
| SR_FLIP_RETEST | filtered | 3490 | 51.45 | 21.51 | 17.70 | 5.39 | 12.77 | 6.37 | 4.98 | 1.99 |
| SR_FLIP_RETEST | kept | 1171 | 69.45 | 19.45 | 17.77 | 3.89 | 13.54 | 6.06 | 8.66 | 1.66 |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 59.30 | 25.00 | 8.00 | 3.00 | 14.00 | 9.00 | 9.30 | 0.00 |
| TREND_PULLBACK_EMA | filtered | 5 | 59.30 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 7.30 | 4.00 |
| TREND_PULLBACK_EMA | kept | 10 | 72.55 | 17.00 | 18.00 | 3.30 | 14.00 | 5.00 | 9.70 | 5.55 |
| VOLUME_SURGE_BREAKOUT | filtered | 123 | 55.30 | 22.85 | 13.12 | 8.71 | 11.07 | 5.00 | 5.38 | 2.98 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 68.40 | 25.00 | 8.00 | 10.50 | 12.00 | 3.75 | 7.65 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 21 | 54.30 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| DIVERGENCE_CONTINUATION | filtered | 95 | 58.34 | 0.57 | 0.00 | 0.00 | 0.00 | 0.45 | 0.86 | 0.00 | 0.00 | **1.88** |
| DIVERGENCE_CONTINUATION | kept | 565 | 69.72 | 0.00 | 0.00 | 0.02 | 0.00 | 0.01 | 0.04 | 0.00 | 0.00 | **0.07** |
| FAILED_AUCTION_RECLAIM | filtered | 567 | 52.63 | 0.00 | 0.00 | 3.27 | 0.00 | 0.62 | 0.00 | 0.00 | 0.00 | **3.89** |
| FAILED_AUCTION_RECLAIM | kept | 1346 | 72.82 | 0.00 | 0.00 | 0.16 | 0.00 | 0.01 | 0.01 | 0.00 | 0.00 | **0.18** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1372 | 55.49 | 0.00 | 0.00 | 1.25 | 0.00 | 4.75 | 0.03 | 0.00 | 0.00 | **6.03** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2151 | 71.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.59 | 0.00 | 0.00 | 0.00 | **0.59** |
| QUIET_COMPRESSION_BREAK | filtered | 22 | 52.25 | 0.00 | 0.00 | 3.27 | 0.00 | 0.00 | 0.00 | 0.00 | 4.91 | **8.18** |
| QUIET_COMPRESSION_BREAK | kept | 2 | 80.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 3490 | 51.45 | 0.12 | 0.00 | 0.17 | 0.00 | 1.10 | 0.00 | 0.00 | 1.50 | **2.89** |
| SR_FLIP_RETEST | kept | 1171 | 69.45 | 0.00 | 0.00 | 0.01 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.03** |
| TREND_PULLBACK_CONTINUATION | filtered | 1 | 59.30 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| TREND_PULLBACK_EMA | filtered | 5 | 59.30 | 9.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **9.00** |
| TREND_PULLBACK_EMA | kept | 10 | 72.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 123 | 55.30 | 0.00 | 0.00 | 5.01 | 0.00 | 2.75 | 0.00 | 0.00 | 0.00 | **7.76** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 68.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=192 (79.7%) | PREMATURE=35 (14.5%) | NEUTRAL=14 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=2
- **Net-helping** — invalidation saved on 157 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 56 | 9 | 0 | 0 |
| ema_crossover | 3 | 1 | 1 | 0 |
| momentum_loss | 93 | 16 | 6 | 0 |
| regime_shift | 8 | 0 | 1 | 0 |
| trailing_invalidation | 32 | 9 | 6 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 9 | 2 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 33 | 5 | 2 | 0 |
| FAILED_AUCTION_RECLAIM | 20 | 0 | 2 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 0 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 51 | 8 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 68 | 18 | 5 | 0 |
| TREND_PULLBACK_EMA | 5 | 2 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 2 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 2 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 56 | 9 | 0 | 21.7 | 18.0 | +0.06 | **TUNE** — marginal: avg +0.06R/kill across 65 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 3 | 1 | 1 | 1.2 | 1.5 | -0.06 | **INSUFFICIENT_SAMPLE** — only 5 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 93 | 16 | 6 | 59.4 | 26.5 | +0.29 | **KEEP** — net-helping: avg +0.29R/kill across 115 kills (saved 59.4R vs missed 26.5R) |
| regime_shift | 8 | 0 | 1 | 4.9 | 0.0 | +0.55 | **INSUFFICIENT_SAMPLE** — only 9 classified kills (need >= 20); let data accumulate before tuning |
| trailing_invalidation | 32 | 9 | 6 | 28.2 | 13.2 | +0.32 | **KEEP** — net-helping: avg +0.32R/kill across 47 kills (saved 28.2R vs missed 13.2R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4249190`
- `Path funnel` emissions: `140`
- `Regime distribution` emissions: `140`
- `QUIET_SCALP_BLOCK` events: `221`
- `confidence_gate` events: `10943`
- `free_channel_post` events: `78`
- `pre_tp_fire` events: `36`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **36**
- Avg resolved threshold: **0.504%** raw → avg net **+4.34%** @ 10x
- Avg time-to-fire from dispatch: **249s**
- By threshold source: stamped=36

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| FAILED_AUCTION_RECLAIM | 11 | 0.446% | +3.76% | 423 | stamped=11 |
| SR_FLIP_RETEST | 11 | 0.503% | +4.33% | 191 | stamped=11 |
| LIQUIDITY_SWEEP_REVERSAL | 6 | 0.622% | +5.52% | 108 | stamped=6 |
| DIVERGENCE_CONTINUATION | 6 | 0.432% | +3.62% | 208 | stamped=6 |
| TREND_PULLBACK_EMA | 2 | 0.692% | +6.22% | 156 | stamped=2 |
- Top symbols: VELVETUSDT=7, BABYUSDT=6, APTUSDT=5, 龙虾USDT=3, 1000PEPEUSDT=2, 1000SHIBUSDT=2, TAUSDT=2, LAUSDT=2, WLFIUSDT=1, FILUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **78**

| Source | Count |
|---|---:|
| pre_tp | 36 |
| signal_close | 35 |
| regime_shift | 7 |

- By severity: HIGH=78

## Dependency readiness
- cvd: presence[present=800402] state[populated=800402] buckets[many=800319, some=83] sources[none] quality[none]
- funding_rate: presence[absent=13022, present=787380] state[empty=13022, populated=787380] buckets[few=787380, none=13022] sources[none] quality[none]
- liquidation_clusters: presence[absent=408009, present=392393] state[empty=408009, populated=392393] buckets[few=296367, none=408009, some=96026] sources[none] quality[none]
- oi_snapshot: presence[absent=9661, present=790741] state[empty=9661, populated=790741] buckets[few=289, many=788836, none=9661, some=1616] sources[none] quality[none]
- order_book: presence[absent=207014, present=593388] state[populated=593388, unavailable=207014] buckets[few=593388, none=207014] sources[book_ticker=593388, unavailable=207014] quality[none=207014, top_of_book_only=593388]
- orderblocks: presence[absent=800402] state[empty=800402] buckets[none=800402] sources[not_implemented=800402] quality[none]
- recent_ticks: presence[absent=26104, present=774298] state[empty=26104, populated=774298] buckets[many=774298, none=26104] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `8.231889009475708` sec
- Median create→first breach: `499.11686182022095` sec
- Median create→terminal: `407.6158368587494` sec
- Median first breach→terminal: `1.503105878829956` sec
- Fast-failure buckets: `{"under_120s": {"count": 7, "pct": 20.0}, "under_180s": {"count": 7, "pct": 20.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 5, "pct": 14.3}}`
- ~3 minute terminal-close behavior: `{"count": 4, "pct": 6.3}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 13 | 13 | 0.0 | 0.0 | 0.0 | 46.2 | 0.0289 | 343.39269948005676 | 160.3406159877777 |
| FAILED_AUCTION_RECLAIM | 16 | 16 | 0.0 | 6.2 | 0.0 | 68.8 | 0.0162 | 789.0573159456253 | 620.2821010351181 |
| LIQUIDITY_SWEEP_REVERSAL | 8 | 8 | 0.0 | 12.5 | 0.0 | 75.0 | -0.1615 | 410.49343943595886 | 440.73923790454865 |
| SR_FLIP_RETEST | 22 | 22 | 0.0 | 9.1 | 0.0 | 50.0 | -0.0753 | 443.38533210754395 | 445.07183361053467 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 100.0 | 0.346 | 515.7176184654236 | 519.593761920929 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1361 | None | 144.19307804107666 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 48550 | 45 | 35610 | 0.0 | 9.1 | 443.38533210754395 | 445.07183361053467 | 12940 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 423 | 2 | 404 | 0.0 | 0.0 | 515.7176184654236 | 519.593761920929 | 19 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-411`
- Gating Δ: `9368`
- No-generation Δ: `563872`
- Fast failures Δ: `-12`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -0.3347, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.3347, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0179, "current_avg_pnl": 0.0289, "current_win_rate": 0.0, "previous_avg_pnl": 0.0468, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.11, "current_avg_pnl": 0.0162, "current_win_rate": 0.0, "previous_avg_pnl": 0.1262, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.2451, "current_avg_pnl": -0.1615, "current_win_rate": 0.0, "previous_avg_pnl": 0.0836, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.1507, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.1507, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.224, "current_avg_pnl": -0.0753, "current_win_rate": 0.0, "previous_avg_pnl": 0.1487, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.6321, "current_avg_pnl": 0.346, "current_win_rate": 0.0, "previous_avg_pnl": -0.2861, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -237, "geometry_changed_delta": 0, "geometry_preserved_delta": -3443, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 48.8, "median_terminal_delta_sec": 95.5, "sl_rate_delta": 5.5, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -2, "geometry_changed_delta": 0, "geometry_preserved_delta": -260, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1541.04, "median_terminal_delta_sec": -323.55, "sl_rate_delta": -33.3, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
