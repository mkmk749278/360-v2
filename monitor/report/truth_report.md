# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `10500` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 41 | 41 | 26 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1912 | 1912 | 1734 | 2 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 54658 | 54668 | 22 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 48947 | 48957 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 48794 | 48110 | 833 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 48978 | 47814 | 1260 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 54808 | 54513 | 331 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 40685 | 40705 | 1 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 49075 | 49104 | 4 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 65024 | 67473 | 2649 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 54693 | 41475 | 23489 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 54359 | 54368 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 48954 | 48972 | 7 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 48772 | 48761 | 32 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 48300 | 48406 | 335 | 0 | 0 | 0 | low-sample (long_disabled) |
| EVAL::STANDARD | 35343 | 32819 | 2793 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 35620 | 35589 | 70 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 54607 | 54650 | 1 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 40708 | 40731 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3027 | 3027 | 2381 | 24 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 677 | 677 | 638 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 8 | 8 | 8 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14368 | 14368 | 14270 | 7 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 5 | 5 | 4 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4598 | 4598 | 4598 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 52539 | 52539 | 51085 | 5 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 20 | 20 | 20 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 118 | 118 | 70 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 794 | 794 | 623 | 6 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 195 | 195 | 187 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 11 | 11 | 11 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=54668): breakout_not_found=33161, basic_filters_failed=15294, move_not_fresh=3767, breakout_stale=1447, retest_proximity_failed=716, volume_spike_missing=263, ema_alignment_reject=19, move_exhausted=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=48958): cls_disabled_merged_into_lsr=48958
- **EVAL::DIVERGENCE_CONTINUATION** (total=48111): cvd_divergence_failed=19914, h1_trend_not_aligned=9459, basic_filters_failed=9278, retest_proximity_failed=6782, ema_alignment_reject=2488, missing_fvg_or_orderblock=190
- **EVAL::FAILED_AUCTION_RECLAIM** (total=47815): auction_not_detected=19202, basic_filters_failed=8472, reclaim_hold_failed=8466, tail_too_small=6856, regime_blocked=4819
- **EVAL::FUNDING_EXTREME** (total=54514): funding_not_extreme=39565, basic_filters_failed=11361, momentum_reject=1410, ema_alignment_reject=1336, rsi_reject=403, cvd_divergence_failed=260, missing_funding_rate=147, missing_fvg_or_orderblock=32
- **EVAL::LIQUIDATION_REVERSAL** (total=40705): cascade_threshold_not_met=28644, basic_filters_failed=11229, cvd_divergence_failed=422, rsi_reject=396, missing_fvg_or_orderblock=12, volume_spike_missing=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=49105): no_ma_cross=37995, basic_filters_failed=9295, ma_cross_htf_misaligned=1410, ma_cross_cooldown=405
- **EVAL::MOVER_AVWAP_SCALP** (total=67474): no_avwap_tag=37172, basic_filters_failed=15204, no_mover_leg=10063, avwap_slope_against=3471, avwap_reclaim_no_volume=1011, insufficient_candles=544, no_avwap_reclaim=9
- **EVAL::MOVER_TREND_PULLBACK** (total=41475): basic_filters_failed=15113, mover_run_too_small=12252, no_reclaim=12169, no_pullback_tag=1397, insufficient_candles=544
- **EVAL::OPENING_RANGE_BREAKOUT** (total=54369): feature_disabled=54369
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=48973): breakout_not_found=23283, regime_blocked=21737, basic_filters_failed=3750, adx_reject=198, ema_alignment_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=48762): regime_blocked=31955, compression_not_detected=10911, basic_filters_failed=4714, breakout_not_detected=653, macd_reject=462, volume_confirmation_failed=67
- **EVAL::SR_FLIP_RETEST** (total=48407): long_disabled=17380, basic_filters_failed=8454, flip_close_not_confirmed=7934, reclaim_hold_failed=4881, regime_blocked=4799, retest_out_of_zone=2305, ema_alignment_reject=2165, wick_quality_failed=466, missing_fvg_or_orderblock=13, rsi_reject=10
- **EVAL::STANDARD** (total=32819): momentum_reject=8426, adx_reject=6914, basic_filters_failed=6520, ema_alignment_reject=5048, sweeps_not_detected=4658, macd_reject=869, invalid_sl_geometry=252, rsi_reject=132
- **EVAL::TREND_PULLBACK** (total=35589): h1_pullback_not_confirmed=16818, h1_trend_not_aligned=9397, ema_not_tested_prev=2785, ema_alignment_reject=2575, basic_filters_failed=2377, no_ema_reclaim_close=793, body_conviction_fail=310, rsi_reject=187, prev_already_above_emas=157, no_prev_high_break=100, momentum_flat=41, ema21_not_tagged=23, no_prev_low_break=12, prev_already_below_emas=9, missing_fvg_or_orderblock=3, momentum_reject=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=54650): breakout_not_found=28198, basic_filters_failed=15292, move_not_fresh=7664, breakout_stale=2114, retest_proximity_failed=1106, volume_spike_missing=228, ema_alignment_reject=34, missing_fvg_or_orderblock=7, move_exhausted=7
- **EVAL::WHALE_MOMENTUM** (total=40731): momentum_reject=31928, recent_ticks_insufficient=6203, basic_filters_failed=2600

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 112765 | 45.4% |
| RANGING | 68264 | 27.5% |
| TRENDING_DOWN | 30764 | 12.4% |
| QUIET | 19919 | 8.0% |
| VOLATILE | 16841 | 6.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **19**
- Average confidence gap to threshold: **5.38** (samples=19) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: COINUSDT=6, ARMUSDT=5, RKLBUSDT=4, BZUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 7 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 40 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 14 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 268 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 37 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 17 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 39 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 2 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 376 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 3 |
| SR_FLIP_RETEST | filtered | min_confidence | 23 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 8 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 21 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 8 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 7 | 55.39 | 65.00 | 9.61 | 20.59 | 19.20 | 20.00 | 4.57 | 18.70 |
| BREAKDOWN_SHORT | kept | 1 | 71.80 | 65.00 | -6.80 | 20.70 | 18.80 | 20.00 | 3.50 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 40 | 56.61 | 65.00 | 8.39 | 20.36 | 19.37 | 17.85 | 1.18 | 10.66 |
| DIVERGENCE_CONTINUATION | kept | 14 | 74.99 | 65.00 | -9.99 | 19.47 | 17.41 | 18.67 | 0.14 | 0.32 |
| FAILED_AUCTION_RECLAIM | filtered | 276 | 52.23 | 65.00 | 12.77 | 20.83 | 19.09 | 20.00 | 3.31 | 9.07 |
| FAILED_AUCTION_RECLAIM | kept | 37 | 71.06 | 65.00 | -6.06 | 21.16 | 19.68 | 20.00 | 4.24 | 1.82 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 54.00 | 65.00 | 11.00 | 20.80 | 19.60 | 17.00 | 2.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 49.68 | 65.00 | 15.32 | 18.72 | 20.00 | 19.75 | 3.88 | 24.20 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 39 | 65.98 | 65.00 | -0.98 | 23.66 | 19.91 | 16.04 | 2.82 | 0.04 |
| MOVER_TREND_PULLBACK | filtered | 2 | 62.20 | 65.00 | 2.80 | 19.90 | 17.90 | 15.80 | 3.50 | 12.00 |
| MOVER_TREND_PULLBACK | kept | 376 | 76.70 | 65.00 | -11.70 | 20.47 | 18.71 | 15.80 | 4.82 | 2.31 |
| QUIET_COMPRESSION_BREAK | filtered | 3 | 64.10 | 65.00 | 0.90 | 21.53 | 20.00 | 20.00 | 0.00 | 13.70 |
| SR_FLIP_RETEST | filtered | 31 | 57.75 | 65.00 | 7.25 | 19.66 | 19.99 | 15.30 | 2.71 | 11.86 |
| SR_FLIP_RETEST | kept | 21 | 70.70 | 65.00 | -5.70 | 18.81 | 19.95 | 15.41 | 2.57 | -3.94 |
| TREND_PULLBACK_EMA | kept | 8 | 77.44 | 65.00 | -12.44 | 18.61 | 19.71 | 19.65 | 5.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 7 | 55.39 | 20.71 | 18.00 | 12.00 | 14.00 | 2.50 | 2.30 | 4.57 |
| BREAKDOWN_SHORT | kept | 1 | 71.80 | 17.00 | 18.00 | 12.00 | 14.00 | 5.00 | 5.30 | 3.50 |
| DIVERGENCE_CONTINUATION | filtered | 40 | 56.61 | 22.60 | 15.75 | 4.20 | 12.32 | 6.58 | 8.77 | 1.18 |
| DIVERGENCE_CONTINUATION | kept | 14 | 74.99 | 24.43 | 18.00 | 8.14 | 13.93 | 4.64 | 6.24 | 0.14 |
| FAILED_AUCTION_RECLAIM | filtered | 276 | 52.23 | 22.38 | 16.94 | 3.73 | 13.14 | 5.15 | 5.82 | 3.31 |
| FAILED_AUCTION_RECLAIM | kept | 37 | 71.06 | 22.73 | 15.84 | 5.92 | 12.16 | 6.07 | 5.91 | 4.24 |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 54.00 | 25.00 | 8.00 | 6.00 | 14.00 | 9.00 | 10.00 | 2.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 49.68 | 20.29 | 14.00 | 11.82 | 11.12 | 5.00 | 7.76 | 3.88 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 39 | 65.98 | 24.69 | 14.21 | 5.54 | 9.77 | 5.36 | 3.64 | 2.82 |
| MOVER_TREND_PULLBACK | filtered | 2 | 62.20 | 25.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.70 | 3.50 |
| MOVER_TREND_PULLBACK | kept | 376 | 76.70 | 20.26 | 18.00 | 8.15 | 12.76 | 5.59 | 9.48 | 4.82 |
| QUIET_COMPRESSION_BREAK | filtered | 3 | 64.10 | 17.00 | 18.00 | 9.00 | 17.00 | 9.00 | 7.80 | 0.00 |
| SR_FLIP_RETEST | filtered | 31 | 57.75 | 23.71 | 15.42 | 3.77 | 11.97 | 5.48 | 6.55 | 2.71 |
| SR_FLIP_RETEST | kept | 21 | 70.70 | 24.62 | 18.00 | 3.71 | 11.71 | 5.00 | 5.72 | 2.57 |
| TREND_PULLBACK_EMA | kept | 8 | 77.44 | 17.00 | 18.00 | 7.50 | 14.00 | 5.44 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 7 | 55.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |
| BREAKDOWN_SHORT | kept | 1 | 71.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 40 | 56.61 | 3.60 | 0.00 | 3.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **7.08** |
| DIVERGENCE_CONTINUATION | kept | 14 | 74.99 | 0.00 | 0.00 | 0.00 | 0.00 | 0.51 | 0.00 | 0.00 | 0.00 | **0.51** |
| FAILED_AUCTION_RECLAIM | filtered | 276 | 52.23 | 0.00 | 0.00 | 4.03 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | **4.26** |
| FAILED_AUCTION_RECLAIM | kept | 37 | 71.06 | 0.00 | 0.00 | 0.61 | 0.00 | 0.19 | 0.00 | 0.00 | 0.00 | **0.80** |
| FUNDING_EXTREME_SIGNAL | filtered | 2 | 54.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 17 | 49.68 | 0.00 | 0.00 | 0.00 | 0.00 | 4.94 | 0.00 | 0.00 | 0.00 | **4.94** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 39 | 65.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | filtered | 2 | 62.20 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| MOVER_TREND_PULLBACK | kept | 376 | 76.70 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **1.00** |
| QUIET_COMPRESSION_BREAK | filtered | 3 | 64.10 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | filtered | 31 | 57.75 | 2.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **2.61** |
| SR_FLIP_RETEST | kept | 21 | 70.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 8 | 77.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=81 (61.8%) | PREMATURE=21 (16.0%) | NEUTRAL=29 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 60 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 81 | 21 | 29 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 4 | 2 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 20 | 9 | 10 | 0 |
| FUNDING_EXTREME_SIGNAL | 0 | 1 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 2 | 3 | 0 |
| MOVER_AVWAP_SCALP | 8 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 18 | 2 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 19 | 5 | 10 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 81 | 21 | 29 | 56.3 | 44.7 | +0.09 | **TUNE** — marginal: avg +0.09R/kill across 131 kills — consider per-setup exemption or threshold adjustment, not full drop |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `82946`
- `Path funnel` emissions: `28`
- `Regime distribution` emissions: `28`
- `QUIET_SCALP_BLOCK` events: `19`
- `confidence_gate` events: `874`
- `free_channel_post` events: `12`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **12**

| Source | Count |
|---|---:|
| signal_close | 11 |
| regime_shift | 1 |

- By severity: HIGH=12

## Dependency readiness
- cvd: presence[present=199039] state[populated=199039] buckets[many=199039] sources[none] quality[none]
- funding_rate: presence[absent=24503, present=174536] state[empty=24503, populated=174536] buckets[few=174536, none=24503] sources[none] quality[none]
- liquidation_clusters: presence[absent=135546, present=63493] state[empty=135546, populated=63493] buckets[few=50202, none=135546, some=13291] sources[none] quality[none]
- oi_snapshot: presence[absent=24503, present=174536] state[empty=24503, populated=174536] buckets[few=3, many=174533, none=24503] sources[none] quality[none]
- order_book: presence[absent=56786, present=142253] state[populated=142253, unavailable=56786] buckets[few=142253, none=56786] sources[book_ticker=142253, unavailable=56786] quality[none=56786, top_of_book_only=142253]
- orderblocks: presence[absent=199039] state[empty=199039] buckets[none=199039] sources[not_implemented=199039] quality[none]
- recent_ticks: presence[absent=2700, present=196339] state[empty=2700, populated=196339] buckets[many=196339, none=2700] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `5.125618934631348` sec
- Median create→first breach: `1298.8330688476562` sec
- Median create→terminal: `1299.5652568340302` sec
- Median first breach→terminal: `2.2475080490112305` sec
- Fast-failure buckets: `{"under_120s": {"count": 3, "pct": 3.0}, "under_180s": {"count": 4, "pct": 4.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 2.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 5 | 5 | 0.0 | 100.0 | 0.0 | 0.0 | -0.9743 | 1829.9636969566345 | 1831.3038408756256 |
| DIVERGENCE_CONTINUATION | 27 | 27 | 14.8 | 51.9 | 14.8 | 0.0 | -0.1385 | 1548.6697750091553 | 1550.715229511261 |
| FAILED_AUCTION_RECLAIM | 35 | 35 | 11.4 | 25.7 | 11.4 | 0.0 | -0.0124 | 1974.8452285528183 | 1979.277447104454 |
| LIQUIDITY_SWEEP_REVERSAL | 16 | 16 | 6.2 | 37.5 | 6.2 | 0.0 | -0.2931 | 697.7688074111938 | 718.5067644119263 |
| MOVER_AVWAP_SCALP | 8 | 8 | 0.0 | 0.0 | 0.0 | 0.0 | -0.1374 | None | None |
| MOVER_TREND_PULLBACK | 27 | 27 | 11.1 | 22.2 | 11.1 | 0.0 | 0.4583 | 1123.6636544466019 | 1124.3975645303726 |
| QUIET_COMPRESSION_BREAK | 8 | 8 | 37.5 | 12.5 | 37.5 | 0.0 | 0.6881 | 1090.6442325115204 | 1092.8921700716019 |
| SR_FLIP_RETEST | 48 | 48 | 16.7 | 25.0 | 16.7 | 0.0 | 0.0813 | 1496.8537340164185 | 1509.3041241168976 |
| TREND_PULLBACK_EMA | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 631.3398430347443 | 633.4154031276703 |
| VOLUME_SURGE_BREAKOUT | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.803 | 1006.1522319316864 | 1008.2386289834976 |
| WHALE_MOMENTUM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.7923 | None | None |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 794 | 6 | 623 | 16.7 | 25.0 | 1496.8537340164185 | 1509.3041241168976 | 171 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 195 | 1 | 187 | 0.0 | 0.0 | 631.3398430347443 | 633.4154031276703 | 8 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `46`
- Gating Δ: `75655`
- No-generation Δ: `817115`
- Fast failures Δ: `-4`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -1.3793, "current_avg_pnl": -0.9743, "current_win_rate": 0.0, "previous_avg_pnl": 0.405, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.176, "current_avg_pnl": -0.1385, "current_win_rate": 14.8, "previous_avg_pnl": 0.0375, "previous_win_rate": 5.6, "win_rate_delta": 9.2}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.0686, "current_avg_pnl": -0.0124, "current_win_rate": 11.4, "previous_avg_pnl": 0.0562, "previous_win_rate": 2.1, "win_rate_delta": 9.3}, "FUNDING_EXTREME_SIGNAL": {"avg_pnl_delta": -0.0842, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": 0.0842, "previous_win_rate": 14.3, "win_rate_delta": -14.3}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0974, "current_avg_pnl": -0.2931, "current_win_rate": 6.2, "previous_avg_pnl": -0.3905, "previous_win_rate": 5.7, "win_rate_delta": 0.5}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.1374, "current_avg_pnl": -0.1374, "current_win_rate": 0.0, "previous_avg_pnl": 0.0, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.9987, "current_avg_pnl": 0.4583, "current_win_rate": 11.1, "previous_avg_pnl": -0.5404, "previous_win_rate": 0.0, "win_rate_delta": 11.1}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 0.0383, "current_avg_pnl": 0.6881, "current_win_rate": 37.5, "previous_avg_pnl": 0.6498, "previous_win_rate": 0.0, "win_rate_delta": 37.5}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.3134, "current_avg_pnl": 0.0813, "current_win_rate": 16.7, "previous_avg_pnl": -0.2321, "previous_win_rate": 4.5, "win_rate_delta": 12.2}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.103, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.103, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -0.6139, "current_avg_pnl": -0.803, "current_win_rate": 0.0, "previous_avg_pnl": -0.1891, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 6, "geometry_changed_delta": 0, "geometry_preserved_delta": 171, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 719.71, "median_terminal_delta_sec": 646.04, "sl_rate_delta": -24.3, "win_rate_delta": 12.2}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 8, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1929.47, "median_terminal_delta_sec": -1928.44, "sl_rate_delta": -25.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MOVER_AVWAP_SCALP**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
