# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION
- Top promising signals/paths: none
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1548` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 8 | 8 | 6 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4692 | 4692 | 4327 | 11 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 41221 | 41222 | 2 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 34951 | 34953 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 34918 | 33442 | 1505 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 34953 | 33222 | 1766 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 38993 | 38974 | 21 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 31765 | 31764 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 34988 | 34989 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 46257 | 45489 | 3439 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 41224 | 34111 | 12134 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 38598 | 38598 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 34952 | 34950 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 34913 | 34829 | 88 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 34516 | 34163 | 748 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 27986 | 25619 | 2451 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::TREND_PULLBACK | 28071 | 28065 | 11 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 41216 | 41214 | 5 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::WHALE_MOMENTUM | 31768 | 31771 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6353 | 6353 | 5818 | 5 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 117 | 117 | 115 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 10941 | 10941 | 10400 | 15 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 8137 | 8137 | 6762 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 34635 | 34635 | 33237 | 2 | active-low-quality (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 275 | 275 | 226 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 3709 | 3709 | 2274 | 11 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 78 | 78 | 27 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 47 | 47 | 28 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=41222): basic_filters_failed=17920, breakout_not_found=16148, move_not_fresh=4673, breakout_stale=1254, retest_proximity_failed=804, insufficient_candles=362, ema_alignment_reject=47, volume_spike_missing=12, move_exhausted=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=34954): cls_disabled_merged_into_lsr=34954
- **EVAL::DIVERGENCE_CONTINUATION** (total=33443): basic_filters_failed=13316, cvd_divergence_failed=8793, h1_trend_not_aligned=7896, ema_alignment_reject=1946, retest_proximity_failed=1296, missing_fvg_or_orderblock=196
- **EVAL::FAILED_AUCTION_RECLAIM** (total=33223): basic_filters_failed=12894, auction_not_detected=10841, reclaim_hold_failed=4146, tail_too_small=3792, regime_blocked=1539, rsi_reject=11
- **EVAL::FUNDING_EXTREME** (total=38975): funding_not_extreme=23467, basic_filters_failed=14557, ema_alignment_reject=655, rsi_reject=172, missing_funding_rate=79, cvd_divergence_failed=25, insufficient_candles=10, momentum_reject=8, missing_fvg_or_orderblock=2
- **EVAL::LIQUIDATION_REVERSAL** (total=31764): cascade_threshold_not_met=16443, basic_filters_failed=14433, cvd_divergence_failed=371, rsi_reject=265, insufficient_candles=208, missing_fvg_or_orderblock=25, volume_spike_missing=19
- **EVAL::MA_CROSS_TREND_SHIFT** (total=34990): no_ma_cross=21437, basic_filters_failed=13321, ma_cross_htf_misaligned=128, ma_cross_cooldown=104
- **EVAL::MOVER_AVWAP_SCALP** (total=45490): no_avwap_tag=22579, basic_filters_failed=17947, no_mover_leg=3503, avwap_slope_against=491, insufficient_candles=420, no_avwap_reclaim=381, avwap_reclaim_no_volume=132, anchor_too_recent=37
- **EVAL::MOVER_TREND_PULLBACK** (total=34111): basic_filters_failed=17934, mover_run_too_small=9859, no_reclaim=5331, no_pullback_tag=567, insufficient_candles=420
- **EVAL::OPENING_RANGE_BREAKOUT** (total=38599): feature_disabled=38599
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=34951): regime_blocked=23845, basic_filters_failed=6330, breakout_not_found=4288, adx_reject=487, ema_alignment_reject=1
- **EVAL::QUIET_COMPRESSION_BREAK** (total=34830): compression_not_detected=14921, regime_blocked=12631, basic_filters_failed=6562, breakout_not_detected=428, volume_confirmation_failed=288
- **EVAL::SR_FLIP_RETEST** (total=34164): basic_filters_failed=12890, flip_close_not_confirmed=4582, retest_out_of_zone=3569, whipsaw_flip=3522, long_break_volume_thin=3316, reclaim_hold_failed=2256, regime_blocked=1538, long_disabled=1205, ema_alignment_reject=636, wick_quality_failed=561, long_acceptance_not_held=58, missing_fvg_or_orderblock=31
- **EVAL::STANDARD** (total=25619): basic_filters_failed=7669, momentum_reject=6057, adx_reject=5178, sweeps_not_detected=3267, macd_reject=2247, ema_alignment_reject=961, rsi_reject=170, invalid_sl_geometry=69, mtf_reject=1
- **EVAL::TREND_PULLBACK** (total=28065): h1_pullback_not_confirmed=11883, h1_trend_not_aligned=8206, basic_filters_failed=3251, ema_alignment_reject=1895, ema_not_tested_prev=1528, no_ema_reclaim_close=559, rsi_reject=254, body_conviction_fail=248, prev_already_below_emas=102, ema21_not_tagged=43, prev_already_above_emas=39, no_prev_low_break=28, no_prev_high_break=23, momentum_flat=3, momentum_reject=3
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=41214): basic_filters_failed=17919, breakout_not_found=17830, breakout_stale=2893, move_not_fresh=1744, insufficient_candles=362, retest_proximity_failed=357, volume_spike_missing=93, ema_alignment_reject=14, move_exhausted=2
- **EVAL::WHALE_MOMENTUM** (total=31771): momentum_reject=26436, recent_ticks_insufficient=3070, basic_filters_failed=2265

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 72240 | 33.5% |
| QUIET | 57433 | 26.7% |
| TRENDING_DOWN | 36303 | 16.9% |
| TRENDING_UP | 35806 | 16.6% |
| VOLATILE | 13603 | 6.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **138**
- Average confidence gap to threshold: **10.79** (samples=138) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: XLMUSDT=50, TRXUSDT=38, LTCUSDT=12, BZUSDT=9, XRPUSDT=7, ETHUSDT=6, BTCUSDT=5, 1000BONKUSDT=4, DOGEUSDT=4, SOLUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 143 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 42 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 59 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 171 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 5 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 87 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 25 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 704 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 28 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 1044 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 49 |
| SR_FLIP_RETEST | filtered | min_confidence | 111 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 68 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 129 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 13 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 38 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 71.50 | 65.00 | -6.50 | 20.75 | 19.90 | 20.00 | 4.50 | 6.00 |
| DIVERGENCE_CONTINUATION | filtered | 185 | 53.54 | 65.00 | 11.46 | 20.36 | 19.82 | 17.32 | 0.89 | 12.26 |
| DIVERGENCE_CONTINUATION | kept | 59 | 69.24 | 65.00 | -4.24 | 20.46 | 19.70 | 17.85 | 0.34 | -1.82 |
| FAILED_AUCTION_RECLAIM | filtered | 171 | 51.01 | 65.00 | 13.99 | 20.67 | 18.57 | 20.00 | 3.46 | 9.55 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 69.08 | 65.00 | -4.08 | 22.26 | 19.44 | 20.00 | 4.90 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 87 | 57.80 | 65.00 | 7.20 | 19.75 | 20.00 | 16.76 | 2.32 | 10.88 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 25 | 69.05 | 65.00 | -4.05 | 19.87 | 19.62 | 16.75 | 1.72 | 0.98 |
| MOVER_AVWAP_SCALP | kept | 704 | 74.51 | 65.00 | -9.51 | 17.97 | 18.53 | 15.80 | 3.42 | 0.35 |
| MOVER_TREND_PULLBACK | filtered | 28 | 60.54 | 65.00 | 4.46 | 22.58 | 16.60 | 15.80 | 3.61 | 21.60 |
| MOVER_TREND_PULLBACK | kept | 1044 | 79.73 | 65.00 | -14.73 | 20.47 | 17.13 | 15.80 | 3.70 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 49 | 73.33 | 65.00 | -8.33 | 19.57 | 20.00 | 20.00 | 0.00 | 1.30 |
| SR_FLIP_RETEST | filtered | 179 | 56.61 | 65.00 | 8.39 | 20.97 | 19.92 | 15.73 | 1.79 | 13.16 |
| SR_FLIP_RETEST | kept | 129 | 67.87 | 65.00 | -2.87 | 21.44 | 19.94 | 17.27 | 2.63 | 3.51 |
| TREND_PULLBACK_EMA | filtered | 13 | 42.92 | 65.00 | 22.08 | 20.37 | 18.90 | 15.70 | 4.00 | 17.20 |
| TREND_PULLBACK_EMA | kept | 38 | 81.00 | 65.00 | -16.00 | 20.05 | 20.00 | 17.00 | 5.50 | 0.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.55 | 65.00 | 5.45 | 21.12 | 18.03 | 20.00 | 4.76 | 6.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 71.50 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 3.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 185 | 53.54 | 22.66 | 14.00 | 6.41 | 11.81 | 4.82 | 8.10 | 0.89 |
| DIVERGENCE_CONTINUATION | kept | 59 | 69.24 | 19.17 | 16.64 | 6.56 | 12.29 | 5.49 | 9.16 | 0.34 |
| FAILED_AUCTION_RECLAIM | filtered | 171 | 51.01 | 19.71 | 17.98 | 6.58 | 14.26 | 5.04 | 4.68 | 3.46 |
| FAILED_AUCTION_RECLAIM | kept | 5 | 69.08 | 23.40 | 15.60 | 4.80 | 10.80 | 7.50 | 5.08 | 4.90 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 87 | 57.80 | 24.98 | 14.00 | 3.00 | 11.05 | 5.00 | 8.34 | 2.32 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 25 | 69.05 | 22.36 | 14.96 | 4.32 | 12.48 | 6.04 | 8.15 | 1.72 |
| MOVER_AVWAP_SCALP | kept | 704 | 74.51 | 18.77 | 18.00 | 7.50 | 12.33 | 7.02 | 7.82 | 3.42 |
| MOVER_TREND_PULLBACK | filtered | 28 | 60.54 | 18.14 | 18.00 | 12.27 | 14.00 | 6.12 | 10.00 | 3.61 |
| MOVER_TREND_PULLBACK | kept | 1044 | 79.73 | 19.44 | 18.02 | 7.95 | 13.87 | 6.81 | 9.94 | 3.70 |
| QUIET_COMPRESSION_BREAK | kept | 49 | 73.33 | 18.63 | 18.00 | 9.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 179 | 56.61 | 20.05 | 14.20 | 4.89 | 13.46 | 7.51 | 7.86 | 1.79 |
| SR_FLIP_RETEST | kept | 129 | 67.87 | 22.27 | 14.36 | 4.70 | 14.14 | 5.56 | 7.75 | 2.63 |
| TREND_PULLBACK_EMA | filtered | 13 | 42.92 | 17.62 | 18.00 | 7.50 | 14.00 | 5.00 | 9.00 | 4.00 |
| TREND_PULLBACK_EMA | kept | 38 | 81.00 | 25.00 | 18.00 | 7.50 | 14.00 | 5.00 | 6.00 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.55 | 23.74 | 18.00 | 12.00 | 14.00 | 3.95 | 4.70 | 4.76 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 71.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.00 | **3.00** |
| DIVERGENCE_CONTINUATION | filtered | 185 | 53.54 | 0.00 | 0.00 | 1.82 | 0.00 | 4.90 | 0.00 | 0.00 | 0.00 | **6.72** |
| DIVERGENCE_CONTINUATION | kept | 59 | 69.24 | 0.00 | 0.00 | 0.16 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.16** |
| FAILED_AUCTION_RECLAIM | filtered | 171 | 51.01 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 5 | 69.08 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 87 | 57.80 | 0.00 | 0.00 | 3.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **3.95** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 25 | 69.05 | 0.00 | 0.00 | 0.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.32** |
| MOVER_AVWAP_SCALP | kept | 704 | 74.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | **0.35** |
| MOVER_TREND_PULLBACK | filtered | 28 | 60.54 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| MOVER_TREND_PULLBACK | kept | 1044 | 79.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 49 | 73.33 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | filtered | 179 | 56.61 | 2.26 | 0.00 | 0.00 | 0.00 | 4.22 | 0.00 | 0.00 | 0.00 | **6.48** |
| SR_FLIP_RETEST | kept | 129 | 67.87 | 0.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.04** |
| TREND_PULLBACK_EMA | filtered | 13 | 42.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 38 | 81.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=77 (66.4%) | PREMATURE=18 (15.5%) | NEUTRAL=21 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 59 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 77 | 18 | 21 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 3 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 16 | 5 | 7 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 2 | 2 | 0 |
| MOVER_AVWAP_SCALP | 13 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 27 | 2 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 13 | 6 | 8 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 77 | 18 | 21 | 57.7 | 28.7 | +0.25 | **KEEP** — net-helping: avg +0.25R/kill across 116 kills (saved 57.7R vs missed 28.7R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `63555`
- `Path funnel` emissions: `24`
- `Regime distribution` emissions: `24`
- `QUIET_SCALP_BLOCK` events: `138`
- `confidence_gate` events: `2737`
- `free_channel_post` events: `3`
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
- Total posts in window: **3**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[present=156510] state[populated=156510] buckets[few=3, many=156472, some=35] sources[none] quality[none]
- funding_rate: presence[absent=20170, present=136340] state[empty=20170, populated=136340] buckets[few=136340, none=20170] sources[none] quality[none]
- liquidation_clusters: presence[absent=79099, present=77411] state[empty=79099, populated=77411] buckets[few=59517, none=79099, some=17894] sources[none] quality[none]
- oi_snapshot: presence[absent=20169, present=136341] state[empty=20169, populated=136341] buckets[few=286, many=134477, none=20169, some=1578] sources[none] quality[none]
- order_book: presence[absent=41557, present=114953] state[populated=114953, unavailable=41557] buckets[few=114953, none=41557] sources[book_ticker=114953, unavailable=41557] quality[none=41557, top_of_book_only=114953]
- orderblocks: presence[absent=156510] state[empty=156510] buckets[none=156510] sources[not_implemented=156510] quality[none]
- recent_ticks: presence[present=156510] state[populated=156510] buckets[many=156510] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.885936975479126` sec
- Median create→first breach: `885.2688648700714` sec
- Median create→terminal: `1907.8463099002838` sec
- Median first breach→terminal: `1.586216926574707` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 6.7}, "under_180s": {"count": 1, "pct": 6.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 6.7}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 4.2}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 402.69567012786865 | 404.5148289203644 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | 0.4856 | 219.80720686912537 | 3604.1055607795715 |
| FAILED_AUCTION_RECLAIM | 6 | 6 | 33.3 | 16.7 | 33.3 | 0.0 | 1.3063 | 2027.094804406166 | 2185.6771174669266 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.4295 | 685.4990639686584 | 686.1017279624939 |
| MOVER_AVWAP_SCALP | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.3423 | None | 3603.41846203804 |
| MOVER_TREND_PULLBACK | 5 | 5 | 0.0 | 40.0 | 0.0 | 0.0 | -0.5106 | 706.1916620731354 | 823.3716139793396 |
| SR_FLIP_RETEST | 7 | 7 | 14.3 | 57.1 | 14.3 | 0.0 | -0.2421 | 953.9457581043243 | 1271.6504340171814 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 3709 | 11 | 2274 | 14.3 | 57.1 | 953.9457581043243 | 1271.6504340171814 | 1435 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 78 | 0 | 27 | 0.0 | 0.0 | None | None | 51 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `46`
- Gating Δ: `63252`
- No-generation Δ: `597375`
- Fast failures Δ: `1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": -4.5917, "current_avg_pnl": -3.0, "current_win_rate": 0.0, "previous_avg_pnl": 1.5917, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.0015, "current_avg_pnl": 0.4856, "current_win_rate": 0.0, "previous_avg_pnl": 0.4871, "previous_win_rate": 28.6, "win_rate_delta": -28.6}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.1547, "current_avg_pnl": 1.3063, "current_win_rate": 33.3, "previous_avg_pnl": 0.1516, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.2962, "current_avg_pnl": -0.3423, "current_win_rate": 0.0, "previous_avg_pnl": -0.0461, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.0641, "current_avg_pnl": -0.5106, "current_win_rate": 0.0, "previous_avg_pnl": -0.4465, "previous_win_rate": 7.7, "win_rate_delta": -7.7}, "SR_FLIP_RETEST": {"avg_pnl_delta": -1.0312, "current_avg_pnl": -0.2421, "current_win_rate": 14.3, "previous_avg_pnl": 0.7891, "previous_win_rate": 50.0, "win_rate_delta": -35.7}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 11, "geometry_changed_delta": 0, "geometry_preserved_delta": 1435, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -468.23, "median_terminal_delta_sec": -554.98, "sl_rate_delta": 48.8, "win_rate_delta": -35.7}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 51, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **MOVER_AVWAP_SCALP**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
