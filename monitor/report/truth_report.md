# Runtime Truth Report

## Executive summary
- Overall health/freshness: **unhealthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=unhealthy)
- Heartbeat age: `16232` sec (warning=True)
- Latest performance record age: `15805` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 24 | 24 | 24 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3944 | 3944 | 3323 | 11 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 38595 | 38577 | 20 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 40969 | 40971 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 40929 | 39557 | 1413 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 40972 | 38307 | 2717 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 46113 | 45877 | 245 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 35454 | 35461 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 41021 | 41027 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 45539 | 46760 | 1812 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 38597 | 29219 | 16306 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 45019 | 45021 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 40971 | 40952 | 21 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 40926 | 40929 | 0 | 0 | 0 | 0 | non-generating (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 39826 | 39719 | 1198 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 32330 | 29761 | 2670 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 32431 | 32362 | 81 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 38583 | 38522 | 73 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 35462 | 35469 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 7787 | 7787 | 6384 | 20 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 675 | 675 | 662 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 10896 | 10896 | 10555 | 3 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4580 | 4580 | 4444 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 39100 | 39100 | 38072 | 2 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 48 | 48 | 48 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 2869 | 2869 | 2126 | 7 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 401 | 401 | 389 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 94 | 94 | 31 | 1 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=38577): breakout_not_found=22088, basic_filters_failed=12568, move_not_fresh=2029, breakout_stale=1570, retest_proximity_failed=290, volume_spike_missing=32
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=40971): cls_disabled_merged_into_lsr=40971
- **EVAL::DIVERGENCE_CONTINUATION** (total=39557): h1_trend_not_aligned=15825, basic_filters_failed=10492, cvd_divergence_failed=9522, ema_alignment_reject=3133, retest_proximity_failed=451, missing_fvg_or_orderblock=134
- **EVAL::FAILED_AUCTION_RECLAIM** (total=38307): auction_not_detected=13797, basic_filters_failed=10399, reclaim_hold_failed=7654, tail_too_small=5504, regime_blocked=952, rsi_reject=1
- **EVAL::FUNDING_EXTREME** (total=45877): funding_not_extreme=33151, basic_filters_failed=11585, ema_alignment_reject=605, rsi_reject=210, momentum_reject=175, cvd_divergence_failed=99, missing_funding_rate=46, missing_fvg_or_orderblock=6
- **EVAL::LIQUIDATION_REVERSAL** (total=35461): cascade_threshold_not_met=23643, basic_filters_failed=11568, cvd_divergence_failed=126, rsi_reject=120, volume_spike_missing=3, missing_fvg_or_orderblock=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=41027): no_ma_cross=30433, basic_filters_failed=10494, ma_cross_cooldown=95, ma_cross_htf_misaligned=5
- **EVAL::MOVER_AVWAP_SCALP** (total=46760): no_avwap_tag=28028, basic_filters_failed=12606, no_mover_leg=3053, avwap_slope_against=2263, avwap_reclaim_no_volume=801, no_avwap_reclaim=9
- **EVAL::MOVER_TREND_PULLBACK** (total=29219): basic_filters_failed=12589, no_reclaim=9009, mover_run_too_small=6562, no_pullback_tag=1059
- **EVAL::OPENING_RANGE_BREAKOUT** (total=45021): feature_disabled=45021
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=40952): regime_blocked=30738, breakout_not_found=7718, basic_filters_failed=1744, adx_reject=743, ema_alignment_reject=9
- **EVAL::QUIET_COMPRESSION_BREAK** (total=40929): compression_not_detected=20585, regime_blocked=11179, basic_filters_failed=8654, breakout_not_detected=502, volume_confirmation_failed=9
- **EVAL::SR_FLIP_RETEST** (total=39719): basic_filters_failed=10395, flip_close_not_confirmed=6677, long_break_volume_thin=5959, whipsaw_flip=5374, long_disabled=4567, reclaim_hold_failed=2804, retest_out_of_zone=2134, regime_blocked=948, wick_quality_failed=443, long_acceptance_not_held=227, missing_fvg_or_orderblock=108, ema_alignment_reject=83
- **EVAL::STANDARD** (total=29761): adx_reject=8079, momentum_reject=7380, basic_filters_failed=4813, sweeps_not_detected=3713, macd_reject=3706, ema_alignment_reject=1851, invalid_sl_geometry=134, rsi_reject=85
- **EVAL::TREND_PULLBACK** (total=32362): h1_trend_not_aligned=16087, h1_pullback_not_confirmed=5340, basic_filters_failed=4489, ema_alignment_reject=3346, ema_not_tested_prev=996, no_ema_reclaim_close=861, body_conviction_fail=502, rsi_reject=372, prev_already_above_emas=183, no_prev_high_break=87, no_prev_low_break=40, prev_already_below_emas=28, momentum_flat=13, momentum_reject=12, missing_fvg_or_orderblock=3, ema21_not_tagged=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=38522): breakout_not_found=16821, basic_filters_failed=12568, move_not_fresh=6938, breakout_stale=1837, retest_proximity_failed=273, volume_spike_missing=84, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=35469): momentum_reject=23417, recent_ticks_insufficient=10095, basic_filters_failed=1957

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 82797 | 44.1% |
| QUIET | 49318 | 26.3% |
| TRENDING_UP | 30584 | 16.3% |
| TRENDING_DOWN | 19145 | 10.2% |
| VOLATILE | 6023 | 3.2% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **92**
- Average confidence gap to threshold: **13.49** (samples=92) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BTCUSDT=25, 1000BONKUSDT=11, SOLUSDT=10, AAVEUSDT=9, ETHUSDT=9, ZECUSDT=7, FETUSDT=6, DOTUSDT=5, AVAXUSDT=4, PLAYUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 60 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 71 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 221 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 49 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 289 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 49 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 16 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 58 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 153 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 213 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 5 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 801 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | filtered | min_confidence | 46 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 19 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 17 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 12 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 62 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 63 | 56.31 | 65.00 | 8.69 | 20.93 | 20.00 | 16.21 | 4.76 | -1.97 |
| DIVERGENCE_CONTINUATION | kept | 71 | 69.78 | 65.00 | -4.78 | 19.69 | 19.73 | 19.27 | 1.30 | -1.42 |
| FAILED_AUCTION_RECLAIM | filtered | 270 | 54.23 | 65.00 | 10.77 | 20.79 | 18.89 | 20.00 | 3.04 | 14.71 |
| FAILED_AUCTION_RECLAIM | kept | 289 | 70.66 | 65.00 | -5.66 | 20.79 | 19.33 | 20.00 | 3.37 | 1.56 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 65 | 60.83 | 65.00 | 4.17 | 22.92 | 19.81 | 16.67 | 2.40 | 14.36 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 58 | 69.12 | 65.00 | -4.12 | 21.59 | 20.00 | 18.28 | 2.43 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 153 | 76.38 | 65.00 | -11.38 | 17.98 | 18.16 | 15.80 | 3.68 | 0.00 |
| MOVER_TREND_PULLBACK | filtered | 218 | 56.03 | 65.00 | 8.97 | 18.96 | 18.91 | 15.80 | 3.40 | 0.50 |
| MOVER_TREND_PULLBACK | kept | 801 | 77.83 | 65.00 | -12.83 | 19.25 | 17.57 | 15.80 | 4.67 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 78.20 | 65.00 | -13.20 | 18.50 | 20.00 | 20.00 | 0.00 | 1.30 |
| SR_FLIP_RETEST | filtered | 65 | 53.74 | 65.00 | 11.26 | 20.54 | 20.00 | 15.23 | 1.50 | 14.43 |
| SR_FLIP_RETEST | kept | 17 | 72.21 | 65.00 | -7.21 | 20.52 | 19.96 | 15.33 | 2.41 | -0.76 |
| TREND_PULLBACK_EMA | kept | 12 | 83.28 | 65.00 | -18.28 | 18.63 | 19.94 | 17.15 | 5.96 | 1.80 |
| VOLUME_SURGE_BREAKOUT | filtered | 62 | 54.12 | 65.00 | 10.88 | 23.02 | 17.98 | 20.00 | 3.65 | 4.70 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.50 | 65.00 | -0.50 | 20.70 | 17.40 | 20.00 | 4.50 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 63 | 56.31 | 21.19 | 8.00 | 12.14 | 14.00 | 5.00 | 6.39 | 4.76 |
| DIVERGENCE_CONTINUATION | kept | 71 | 69.78 | 21.51 | 16.87 | 4.69 | 11.35 | 6.06 | 8.48 | 1.30 |
| FAILED_AUCTION_RECLAIM | filtered | 270 | 54.23 | 19.78 | 17.14 | 8.00 | 12.56 | 5.71 | 7.05 | 3.04 |
| FAILED_AUCTION_RECLAIM | kept | 289 | 70.66 | 21.57 | 14.65 | 6.03 | 13.21 | 5.63 | 7.80 | 3.37 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 65 | 60.83 | 24.17 | 14.00 | 14.45 | 12.63 | 5.32 | 2.22 | 2.40 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 58 | 69.12 | 22.34 | 15.17 | 4.66 | 12.78 | 6.33 | 5.41 | 2.43 |
| MOVER_AVWAP_SCALP | kept | 153 | 76.38 | 17.00 | 18.00 | 15.00 | 15.24 | 5.00 | 8.64 | 3.68 |
| MOVER_TREND_PULLBACK | filtered | 218 | 56.03 | 17.65 | 18.00 | 8.50 | 12.61 | 5.77 | 5.25 | 3.40 |
| MOVER_TREND_PULLBACK | kept | 801 | 77.83 | 18.44 | 18.05 | 8.97 | 13.64 | 5.43 | 8.73 | 4.67 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 78.20 | 17.00 | 18.00 | 12.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 65 | 53.74 | 19.03 | 15.08 | 4.62 | 13.82 | 7.15 | 6.97 | 1.50 |
| SR_FLIP_RETEST | kept | 17 | 72.21 | 23.47 | 12.12 | 7.76 | 15.41 | 5.44 | 6.94 | 2.41 |
| TREND_PULLBACK_EMA | kept | 12 | 83.28 | 22.33 | 18.00 | 7.50 | 14.00 | 8.21 | 9.08 | 5.96 |
| VOLUME_SURGE_BREAKOUT | filtered | 62 | 54.12 | 17.77 | 18.00 | 12.00 | 12.35 | 6.65 | 3.30 | 3.65 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.50 | 2.00 | 18.00 | 15.00 | 14.00 | 5.00 | 10.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 63 | 56.31 | 0.00 | 0.00 | 0.00 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **1.03** |
| DIVERGENCE_CONTINUATION | kept | 71 | 69.78 | 0.00 | 0.00 | 1.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.28** |
| FAILED_AUCTION_RECLAIM | filtered | 270 | 54.23 | 0.00 | 0.00 | 4.34 | 0.00 | 2.72 | 0.00 | 0.00 | 0.00 | **7.06** |
| FAILED_AUCTION_RECLAIM | kept | 289 | 70.66 | 0.00 | 0.00 | 1.22 | 0.00 | 0.04 | 0.00 | 0.00 | 0.00 | **1.26** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 65 | 60.83 | 0.00 | 0.00 | 0.00 | 0.00 | 14.36 | 0.00 | 0.00 | 0.00 | **14.36** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 58 | 69.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 153 | 76.38 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 218 | 56.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | 0.00 | 0.00 | 0.00 | **0.50** |
| MOVER_TREND_PULLBACK | kept | 801 | 77.83 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 78.20 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | filtered | 65 | 53.74 | 0.00 | 0.00 | 0.00 | 0.00 | 3.32 | 0.00 | 0.00 | 0.00 | **3.32** |
| SR_FLIP_RETEST | kept | 17 | 72.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.42 | 0.00 | 0.00 | 0.00 | **0.42** |
| TREND_PULLBACK_EMA | kept | 12 | 83.28 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **4.80** |
| VOLUME_SURGE_BREAKOUT | filtered | 62 | 54.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 65.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=96 (68.1%) | PREMATURE=15 (10.6%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 81 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 96 | 15 | 30 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 6 | 1 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 22 | 6 | 12 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 2 | 3 | 0 |
| MOVER_AVWAP_SCALP | 13 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 25 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 18 | 4 | 11 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 96 | 15 | 30 | 67.1 | 30.0 | +0.26 | **KEEP** — net-helping: avg +0.26R/kill across 141 kills (saved 67.1R vs missed 30.0R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `75247`
- `Path funnel` emissions: `24`
- `Regime distribution` emissions: `24`
- `QUIET_SCALP_BLOCK` events: `92`
- `confidence_gate` events: `2146`
- `free_channel_post` events: `13`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 3135 | 3135 | 3135 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **13**

| Source | Count |
|---|---:|
| signal_close | 13 |

- By severity: HIGH=13

## Dependency readiness
- cvd: presence[present=148247] state[populated=148247] buckets[many=148247] sources[none] quality[none]
- funding_rate: presence[absent=6862, present=141385] state[empty=6862, populated=141385] buckets[few=141385, none=6862] sources[none] quality[none]
- liquidation_clusters: presence[absent=86015, present=62232] state[empty=86015, populated=62232] buckets[few=53366, none=86015, some=8866] sources[none] quality[none]
- oi_snapshot: presence[absent=6862, present=141385] state[empty=6862, populated=141385] buckets[few=215, many=140063, none=6862, some=1107] sources[none] quality[none]
- order_book: presence[absent=37476, present=110771] state[populated=110771, unavailable=37476] buckets[few=110771, none=37476] sources[book_ticker=110771, unavailable=37476] quality[none=37476, top_of_book_only=110771]
- orderblocks: presence[absent=148247] state[empty=148247] buckets[none=148247] sources[not_implemented=148247] quality[none]
- recent_ticks: presence[present=148247] state[populated=148247] buckets[many=148247] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.2102179527282715` sec
- Median create→first breach: `944.6768381595612` sec
- Median create→terminal: `2128.1670928001404` sec
- Median first breach→terminal: `1.7603118419647217` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 2, "pct": 7.4}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.2}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | -0.0358 | 1293.680440068245 | 1295.3281754255295 |
| DIVERGENCE_CONTINUATION | 8 | 8 | 12.5 | 75.0 | 12.5 | 0.0 | -0.4198 | 1345.0725650787354 | 1354.8047415018082 |
| FAILED_AUCTION_RECLAIM | 13 | 13 | 0.0 | 15.4 | 0.0 | 0.0 | -0.0188 | 1064.3249921798706 | 3602.528175830841 |
| LIQUIDITY_SWEEP_REVERSAL | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -1.194 | 228.43679344654083 | 230.94888591766357 |
| MOVER_AVWAP_SCALP | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0243 | None | 3603.0535221099854 |
| MOVER_TREND_PULLBACK | 9 | 9 | 0.0 | 44.4 | 0.0 | 0.0 | -1.0602 | 444.03329050540924 | 524.3557159900665 |
| SR_FLIP_RETEST | 5 | 5 | 40.0 | 20.0 | 40.0 | 0.0 | 0.4277 | 2691.4139721393585 | 2795.9429080486298 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1476.9315971136093 | 1478.3650945425034 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.6329 | 1964.0596549510956 | 1964.6024980545044 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 2869 | 7 | 2126 | 40.0 | 20.0 | 2691.4139721393585 | 2795.9429080486298 | 743 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 401 | 1 | 389 | 0.0 | 0.0 | 1476.9315971136093 | 1478.3650945425034 | 12 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-96`
- Gating Δ: `-142462`
- No-generation Δ: `-1211844`
- Fast failures Δ: `0`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.5444, "current_avg_pnl": -0.4198, "current_win_rate": 12.5, "previous_avg_pnl": 0.1246, "previous_win_rate": 33.3, "win_rate_delta": -20.8}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.138, "current_avg_pnl": -0.0188, "current_win_rate": 0.0, "previous_avg_pnl": 1.1192, "previous_win_rate": 20.0, "win_rate_delta": -20.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.2116, "current_avg_pnl": -1.194, "current_win_rate": 0.0, "previous_avg_pnl": -0.9824, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": 0.0243, "current_avg_pnl": 0.0243, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.0077, "current_avg_pnl": -1.0602, "current_win_rate": 0.0, "previous_avg_pnl": -0.0525, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.33, "current_avg_pnl": 0.4277, "current_win_rate": 40.0, "previous_avg_pnl": 0.0977, "previous_win_rate": 50.0, "win_rate_delta": -10.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -0.0561, "current_avg_pnl": -0.6329, "current_win_rate": 0.0, "previous_avg_pnl": -0.5768, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -7, "geometry_changed_delta": 0, "geometry_preserved_delta": -2503, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2295.37, "median_terminal_delta_sec": 2372.76, "sl_rate_delta": -13.3, "win_rate_delta": -10.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1476.93, "median_terminal_delta_sec": 1478.37, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
