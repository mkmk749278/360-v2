# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `13` sec (warning=False)
- Latest performance record age: `603` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 31 | 31 | 0 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 10741 | 10741 | 10449 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 50216 | 50193 | 31 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 42264 | 42266 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 42078 | 39198 | 3064 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 42273 | 40150 | 2212 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 47027 | 46921 | 119 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 42540 | 42543 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 42369 | 42390 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 52055 | 53200 | 605 | 0 | 0 | 0 | low-sample (no_mover_leg) |
| EVAL::MOVER_TREND_PULLBACK | 50224 | 44230 | 7814 | 0 | 0 | 0 | low-sample (mover_run_too_small) |
| EVAL::OPENING_RANGE_BREAKOUT | 45841 | 45842 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 42265 | 42222 | 51 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 42041 | 41705 | 372 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 40846 | 39659 | 2371 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 37488 | 34346 | 3309 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 37657 | 37460 | 211 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 50207 | 50216 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 42544 | 42546 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 8346 | 8346 | 6669 | 18 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 551 | 551 | 472 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 18867 | 18867 | 18815 | 1 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 9 | 9 | 8 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 1873 | 1873 | 1860 | 2 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 18950 | 18950 | 16059 | 18 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 131 | 131 | 131 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1392 | 1392 | 1258 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 8662 | 8662 | 5317 | 32 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 813 | 813 | 811 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=50193): breakout_not_found=22517, basic_filters_failed=12659, move_not_fresh=12268, breakout_stale=1916, retest_proximity_failed=759, volume_spike_missing=74
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=42266): cls_disabled_merged_into_lsr=42266
- **EVAL::DIVERGENCE_CONTINUATION** (total=39198): cvd_divergence_failed=15005, h1_trend_not_aligned=11817, basic_filters_failed=8440, ema_alignment_reject=2821, retest_proximity_failed=746, missing_fvg_or_orderblock=297, regime_blocked=72
- **EVAL::FAILED_AUCTION_RECLAIM** (total=40150): auction_not_detected=17831, basic_filters_failed=8394, reclaim_hold_failed=7728, tail_too_small=5819, regime_blocked=376, rsi_reject=2
- **EVAL::FUNDING_EXTREME** (total=46921): funding_not_extreme=31979, basic_filters_failed=8710, ema_alignment_reject=4029, missing_funding_rate=1738, rsi_reject=268, momentum_reject=98, cvd_divergence_failed=97, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=42543): cascade_threshold_not_met=33308, basic_filters_failed=8812, cvd_divergence_failed=251, rsi_reject=156, volume_spike_missing=15, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=42390): no_ma_cross=32755, basic_filters_failed=8445, ma_cross_cooldown=647, ma_cross_htf_misaligned=543
- **EVAL::MOVER_AVWAP_SCALP** (total=53200): no_mover_leg=19248, no_avwap_tag=14285, basic_filters_failed=12559, avwap_slope_against=4639, insufficient_candles=1996, avwap_reclaim_no_volume=308, no_avwap_reclaim=165
- **EVAL::MOVER_TREND_PULLBACK** (total=44230): mover_run_too_small=24747, basic_filters_failed=12537, no_reclaim=3881, insufficient_candles=1996, no_pullback_tag=1069
- **EVAL::OPENING_RANGE_BREAKOUT** (total=45842): feature_disabled=45842
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=42222): regime_blocked=26152, breakout_not_found=13498, basic_filters_failed=1982, adx_reject=583, ema_alignment_reject=7
- **EVAL::QUIET_COMPRESSION_BREAK** (total=41705): regime_blocked=16426, compression_not_detected=11424, basic_filters_failed=6408, breakout_not_detected=4442, macd_reject=2102, volume_confirmation_failed=851, rsi_reject=49, missing_fvg_or_orderblock=3
- **EVAL::SR_FLIP_RETEST** (total=39659): flip_close_not_confirmed=9915, basic_filters_failed=8387, retest_out_of_zone=5325, whipsaw_flip=4914, reclaim_hold_failed=3426, long_break_volume_thin=3094, long_disabled=2907, wick_quality_failed=777, regime_blocked=370, ema_alignment_reject=214, long_acceptance_not_held=201, missing_fvg_or_orderblock=90, rsi_reject=39
- **EVAL::STANDARD** (total=34346): momentum_reject=13982, sweeps_not_detected=7455, adx_reject=5536, macd_reject=2919, basic_filters_failed=2524, ema_alignment_reject=1635, invalid_sl_geometry=218, rsi_reject=77
- **EVAL::TREND_PULLBACK** (total=37460): h1_trend_not_aligned=12891, basic_filters_failed=5291, ema_not_tested_prev=5028, h1_pullback_not_confirmed=3875, no_ema_reclaim_close=3468, ema_alignment_reject=2947, rsi_reject=1566, body_conviction_fail=1517, prev_already_above_emas=235, momentum_flat=158, no_prev_high_break=143, prev_already_below_emas=142, no_prev_low_break=77, regime_blocked=63, missing_fvg_or_orderblock=35, momentum_reject=23, ema21_not_tagged=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=50216): breakout_not_found=32425, basic_filters_failed=12656, move_not_fresh=2456, breakout_stale=2130, retest_proximity_failed=438, volume_spike_missing=65, ema_alignment_reject=40, missing_fvg_or_orderblock=6
- **EVAL::WHALE_MOMENTUM** (total=42546): momentum_reject=30301, recent_ticks_insufficient=8639, basic_filters_failed=3606

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 77723 | 30.6% |
| QUIET | 76874 | 30.2% |
| TRENDING_DOWN | 68270 | 26.9% |
| TRENDING_UP | 23736 | 9.3% |
| VOLATILE | 7630 | 3.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **212**
- Average confidence gap to threshold: **15.91** (samples=212) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOTUSDT=26, BNBUSDT=25, BTCUSDT=25, SOXLUSDT=23, ETHUSDT=17, TRXUSDT=16, ASTERUSDT=12, LTCUSDT=11, AAVEUSDT=10, ZECUSDT=10

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 16 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 15 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 23 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 6 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 396 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 88 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 271 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 32 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 14 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 883 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1113 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 75 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 9 |
| SR_FLIP_RETEST | filtered | min_confidence | 834 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 45 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 404 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 16 | 60.30 | 65.00 | 4.70 | 20.80 | 17.40 | 20.00 | 4.50 | 17.20 |
| BREAKDOWN_SHORT | kept | 15 | 68.30 | 65.00 | -3.30 | 20.80 | 16.20 | 20.00 | 4.50 | 20.20 |
| DIVERGENCE_CONTINUATION | filtered | 26 | 57.98 | 65.00 | 7.02 | 20.76 | 19.80 | 17.96 | 2.88 | 8.08 |
| DIVERGENCE_CONTINUATION | kept | 6 | 67.23 | 65.00 | -2.23 | 20.95 | 18.70 | 17.70 | 0.83 | -0.37 |
| FAILED_AUCTION_RECLAIM | filtered | 484 | 53.72 | 65.00 | 11.28 | 18.47 | 19.19 | 20.00 | 4.56 | 5.21 |
| FAILED_AUCTION_RECLAIM | kept | 271 | 70.42 | 65.00 | -5.42 | 21.84 | 18.92 | 20.00 | 4.43 | 0.37 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 49.90 | 65.00 | 15.10 | 23.10 | 20.00 | 17.00 | 2.00 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 67.22 | 65.00 | -2.22 | 19.37 | 19.93 | 19.38 | 4.94 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 14 | 69.15 | 65.00 | -4.15 | 19.11 | 19.46 | 15.80 | 3.29 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 883 | 55.77 | 65.00 | 9.23 | 20.44 | 19.08 | 15.80 | 4.50 | 14.01 |
| MOVER_TREND_PULLBACK | kept | 1113 | 73.67 | 65.00 | -8.67 | 20.16 | 19.27 | 15.80 | 4.17 | 2.80 |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 51.04 | 65.00 | 13.96 | 21.19 | 19.89 | 20.00 | 0.00 | 17.64 |
| QUIET_COMPRESSION_BREAK | kept | 9 | 80.51 | 65.00 | -15.51 | 20.66 | 19.90 | 20.00 | 0.00 | 1.49 |
| SR_FLIP_RETEST | filtered | 879 | 57.51 | 65.00 | 7.49 | 20.67 | 19.83 | 15.48 | 1.47 | 11.58 |
| SR_FLIP_RETEST | kept | 404 | 70.24 | 65.00 | -5.24 | 20.37 | 19.89 | 16.53 | 2.11 | 0.74 |
| TREND_PULLBACK_EMA | kept | 2 | 77.15 | 65.00 | -12.15 | 21.15 | 19.90 | 18.90 | 5.50 | 6.35 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 16 | 60.30 | 17.00 | 18.00 | 12.00 | 11.00 | 5.00 | 10.00 | 4.50 |
| BREAKDOWN_SHORT | kept | 15 | 68.30 | 17.00 | 18.00 | 15.00 | 14.00 | 10.00 | 10.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 26 | 57.98 | 22.85 | 10.31 | 6.46 | 11.73 | 5.46 | 8.44 | 2.88 |
| DIVERGENCE_CONTINUATION | kept | 6 | 67.23 | 25.00 | 13.00 | 4.50 | 12.17 | 5.00 | 8.37 | 0.83 |
| FAILED_AUCTION_RECLAIM | filtered | 484 | 53.72 | 22.38 | 15.15 | 7.85 | 11.92 | 6.20 | 4.25 | 4.56 |
| FAILED_AUCTION_RECLAIM | kept | 271 | 70.42 | 23.80 | 14.24 | 4.69 | 12.30 | 5.87 | 5.46 | 4.43 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 49.90 | 23.00 | 14.00 | 15.00 | 11.00 | 2.50 | 4.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 67.22 | 25.00 | 14.00 | 3.09 | 12.00 | 5.11 | 3.08 | 4.94 |
| MOVER_AVWAP_SCALP | kept | 14 | 69.15 | 17.00 | 18.00 | 8.89 | 11.43 | 5.29 | 5.26 | 3.29 |
| MOVER_TREND_PULLBACK | filtered | 883 | 55.77 | 18.18 | 18.00 | 7.83 | 12.28 | 5.27 | 8.12 | 4.50 |
| MOVER_TREND_PULLBACK | kept | 1113 | 73.67 | 20.10 | 18.09 | 8.20 | 12.85 | 5.72 | 8.54 | 4.17 |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 51.04 | 17.96 | 18.00 | 12.00 | 14.00 | 6.99 | 2.73 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 9 | 80.51 | 21.44 | 18.00 | 12.67 | 16.00 | 8.17 | 6.06 | 0.00 |
| SR_FLIP_RETEST | filtered | 879 | 57.51 | 18.97 | 17.49 | 5.16 | 12.15 | 5.44 | 8.40 | 1.47 |
| SR_FLIP_RETEST | kept | 404 | 70.24 | 20.78 | 17.98 | 4.30 | 12.83 | 5.07 | 9.45 | 2.11 |
| TREND_PULLBACK_EMA | kept | 2 | 77.15 | 21.00 | 18.00 | 7.50 | 14.00 | 9.00 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 16 | 60.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 15 | 68.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 26 | 57.98 | 0.00 | 0.00 | 0.00 | 0.00 | 4.34 | 0.00 | 0.00 | 0.00 | **4.34** |
| DIVERGENCE_CONTINUATION | kept | 6 | 67.23 | 0.00 | 0.00 | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.80** |
| FAILED_AUCTION_RECLAIM | filtered | 484 | 53.72 | 0.00 | 0.00 | 0.28 | 0.00 | 3.94 | 0.00 | 0.00 | 0.00 | **4.22** |
| FAILED_AUCTION_RECLAIM | kept | 271 | 70.42 | 0.00 | 0.00 | 0.02 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **0.24** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1 | 49.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 32 | 67.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 14 | 69.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 883 | 55.77 | 0.00 | 0.00 | 1.07 | 0.00 | 1.02 | 0.07 | 0.00 | 0.00 | **2.16** |
| MOVER_TREND_PULLBACK | kept | 1113 | 73.67 | 0.00 | 0.00 | 0.75 | 0.00 | 1.50 | 0.00 | 0.00 | 0.00 | **2.25** |
| QUIET_COMPRESSION_BREAK | filtered | 75 | 51.04 | 0.00 | 0.00 | 0.00 | 0.00 | 2.52 | 0.00 | 0.00 | 10.80 | **13.32** |
| QUIET_COMPRESSION_BREAK | kept | 9 | 80.51 | 0.00 | 0.00 | 0.00 | 0.00 | 3.82 | 0.00 | 0.00 | 0.00 | **3.82** |
| SR_FLIP_RETEST | filtered | 879 | 57.51 | 0.00 | 0.00 | 0.19 | 0.00 | 2.35 | 0.03 | 0.00 | 0.06 | **2.63** |
| SR_FLIP_RETEST | kept | 404 | 70.24 | 0.00 | 0.00 | 0.02 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | **0.04** |
| TREND_PULLBACK_EMA | kept | 2 | 77.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=22 (71.0%) | PREMATURE=6 (19.4%) | NEUTRAL=3 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 16 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 22 | 6 | 3 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 0 | 2 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 3 | 1 | 2 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 6 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 9 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 4 | 2 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 22 | 6 | 3 | 18.2 | 6.4 | +0.38 | **KEEP** — net-helping: avg +0.38R/kill across 31 kills (saved 18.2R vs missed 6.4R) |

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=810 (34.2%) | WOULD_LOSE=570 | WOULD_EXPIRE=987 | pending (awaiting window)=1646

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| dispatch_cooldown | 43 | 0.0% | 0.0 | 0.0 | +0.00 | **TUNE** |
| dispatch_staleness | 410 | 66.1% | 70.0 | 180.1 | -0.27 | **DROP** |
| level_still_in_play | 372 | 29.8% | 122.0 | 37.3 | +0.23 | **KEEP** |
| min_confidence | 1178 | 30.8% | 237.0 | 482.7 | -0.21 | **DROP** |
| quiet_scalp_block | 221 | 8.1% | 60.0 | 27.7 | +0.15 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 4 | 50.0% | 1.0 | 1.5 | -0.12 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 43 | 16.3% | 35.0 | 5.2 | +0.69 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 67 | 29.9% | 38.0 | 46.7 | -0.13 | **TUNE** |
| shadow_unit:SHADOW_RANGE_FADE | 29 | 62.1% | 7.0 | 36.5 | -1.02 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 1412 across 14 strategies; 26 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| FAILED_AUCTION_RECLAIM | 433 | 0/433/0 | 22% | -0.36 | OFF_HOURS/DISTRIBUTION/NORMAL/BTC_NEUTRAL (+0.65R) | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| MOVER_TREND_PULLBACK | 428 | 2/426/0 | 60% | +0.19 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+1.08R) | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 223 | 0/223/0 | 84% | +0.74 | ASIA/MARKDOWN/EXPANDED/BTC_FALLING (+1.37R) | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.16R) |
| QUIET_COMPRESSION_BREAK | 81 | 0/81/0 | 79% | +0.45 | NY/QUIET/NORMAL/BTC_NEUTRAL (+0.52R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.50R) |
| SHADOW_MEAN_REVERT | 67 | 0/0/67 | 43% | +0.34 | — | — |
| DIVERGENCE_CONTINUATION | 44 | 0/44/0 | 86% | +0.40 | NY/MARKUP/EXPANDED/BTC_NEUTRAL (+0.15R) | NY/MARKUP/EXPANDED/BTC_NEUTRAL (+0.15R) |
| SHADOW_FUNDING_FADE | 43 | 0/0/43 | 16% | -0.71 | — | — |
| TREND_PULLBACK_EMA | 34 | 0/34/0 | 0% | -0.07 | NY/MARKUP/EXPANDED/BTC_NEUTRAL (-0.07R) | NY/MARKUP/EXPANDED/BTC_NEUTRAL (-0.07R) |
| SHADOW_RANGE_FADE | 29 | 0/0/29 | 76% | +1.09 | — | — |
| VOLUME_SURGE_BREAKOUT | 14 | 0/14/0 | 0% | -0.24 | — | — |
| FUNDING_EXTREME_SIGNAL | 10 | 0/10/0 | 70% | +0.27 | — | — |
| SHADOW_CASCADE_REVERSAL | 4 | 0/0/4 | 75% | +0.15 | — | — |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 0/1/0 | 100% | +1.52 | — | — |
| MOVER_AVWAP_SCALP | 1 | 1/0/0 | 0% | -0.08 | — | — |

- **Strongest cells**: `SR_FLIP_RETEST @ ASIA/MARKDOWN/EXPANDED/BTC_FALLING` +1.37R (n=39, STRONG); `MOVER_TREND_PULLBACK @ ASIA/MARKDOWN/EXPANDED/BTC_FALLING` +1.08R (n=50, STRONG); `MOVER_TREND_PULLBACK @ ASIA/MARKUP/NORMAL/BTC_NEUTRAL` +0.98R (n=50, STRONG)
- **Weakest cells**: `MOVER_TREND_PULLBACK @ ASIA/ACCUMULATION/NORMAL/BTC_FALLING` -1.00R (n=27, NEGATIVE); `FAILED_AUCTION_RECLAIM @ ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` -1.00R (n=50, NEGATIVE); `MOVER_TREND_PULLBACK @ NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` -1.00R (n=34, NEGATIVE)

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `57567`
- `Path funnel` emissions: `32`
- `Regime distribution` emissions: `32`
- `QUIET_SCALP_BLOCK` events: `212`
- `confidence_gate` events: `4230`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **3**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 3 | 3506 | 3506 | 8166 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| signal_close | 3 |
| regime_shift | 2 |
| signal_highlight | 1 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=200946] state[populated=200946] buckets[many=200946] sources[none] quality[none]
- funding_rate: presence[absent=17088, present=183858] state[empty=17088, populated=183858] buckets[few=183858, none=17088] sources[none] quality[none]
- liquidation_clusters: presence[absent=102266, present=98680] state[empty=102266, populated=98680] buckets[few=81829, none=102266, some=16851] sources[none] quality[none]
- oi_snapshot: presence[absent=16305, present=184641] state[empty=16305, populated=184641] buckets[many=184641, none=16305] sources[none] quality[none]
- order_book: presence[absent=59289, present=141657] state[populated=141657, unavailable=59289] buckets[few=141657, none=59289] sources[book_ticker=141657, unavailable=59289] quality[none=59289, top_of_book_only=141657]
- orderblocks: presence[absent=200946] state[empty=200946] buckets[none=200946] sources[not_implemented=200946] quality[none]
- recent_ticks: presence[absent=5219, present=195727] state[empty=5219, populated=195727] buckets[many=195727, none=5219] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.2284220457077026` sec
- Median create→first breach: `6896.2327699661255` sec
- Median create→terminal: `6901.199159502983` sec
- Median first breach→terminal: `2.00370192527771` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.6344 | 21738.30770611763 | 21739.68806910515 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.15 | 2226.4532878398895 | 2226.777246952057 |
| MOVER_TREND_PULLBACK | 4 | 4 | 0.0 | 50.0 | 0.0 | 0.0 | 1.0829 | 6766.30008149147 | 6772.180171489716 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 8662 | 32 | 5317 | 0.0 | 0.0 | None | None | 3345 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 813 | 2 | 811 | 0.0 | 0.0 | None | None | 2 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `79`
- Gating Δ: `61849`
- No-generation Δ: `735087`
- Fast failures Δ: `0`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": 1.1202, "current_avg_pnl": 1.0829, "current_win_rate": 0.0, "previous_avg_pnl": -0.0373, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 32, "geometry_changed_delta": 0, "geometry_preserved_delta": 3345, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 2, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -8877.24, "median_terminal_delta_sec": -8879.41, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
