# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: MOVER_TREND_PULLBACK, FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION
- Top promising signals/paths: SR_FLIP_RETEST
- Recommended next investigation target: **MOVER_TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `633` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 24 | 24 | 23 | 1 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4027 | 4027 | 3326 | 7 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 53331 | 53335 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 46320 | 46324 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 46275 | 44999 | 1319 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 46331 | 44039 | 2352 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 52646 | 52586 | 66 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 40954 | 40957 | 6 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 46393 | 46396 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 60661 | 61686 | 2854 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 53336 | 41403 | 19255 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 51204 | 51206 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 46324 | 46331 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 46273 | 46236 | 39 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 44831 | 44104 | 2163 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 35000 | 32160 | 2982 | 0 | 0 | 0 | low-sample (adx_reject) |
| EVAL::TREND_PULLBACK | 35148 | 35067 | 95 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 53322 | 53331 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 40961 | 40968 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 6199 | 6199 | 5473 | 11 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 586 | 586 | 422 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 7 | 7 | 7 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 13194 | 13194 | 12988 | 8 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 6401 | 6401 | 6339 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 49397 | 49397 | 48911 | 4 | active-low-quality (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 87 | 87 | 47 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 6899 | 6899 | 5937 | 14 | active-healthy (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 610 | 610 | 602 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2 | 2 | 0 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=53335): breakout_not_found=26665, basic_filters_failed=18474, move_not_fresh=5611, breakout_stale=1880, retest_proximity_failed=618, volume_spike_missing=87
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=46326): cls_disabled_merged_into_lsr=46326
- **EVAL::DIVERGENCE_CONTINUATION** (total=45000): h1_trend_not_aligned=17586, basic_filters_failed=11776, cvd_divergence_failed=10152, ema_alignment_reject=4913, retest_proximity_failed=438, missing_fvg_or_orderblock=135
- **EVAL::FAILED_AUCTION_RECLAIM** (total=44041): auction_not_detected=16832, basic_filters_failed=11706, reclaim_hold_failed=8096, tail_too_small=5870, regime_blocked=1537
- **EVAL::FUNDING_EXTREME** (total=52588): funding_not_extreme=37912, basic_filters_failed=13985, ema_alignment_reject=278, rsi_reject=270, momentum_reject=69, cvd_divergence_failed=64, missing_funding_rate=7, missing_fvg_or_orderblock=3
- **EVAL::LIQUIDATION_REVERSAL** (total=40957): cascade_threshold_not_met=26740, basic_filters_failed=13943, cvd_divergence_failed=172, rsi_reject=83, missing_fvg_or_orderblock=14, volume_spike_missing=5
- **EVAL::MA_CROSS_TREND_SHIFT** (total=46398): no_ma_cross=33122, basic_filters_failed=11781, ma_cross_cooldown=1495
- **EVAL::MOVER_AVWAP_SCALP** (total=61686): no_avwap_tag=33452, basic_filters_failed=18234, no_mover_leg=5329, avwap_slope_against=3030, insufficient_candles=596, no_avwap_reclaim=561, avwap_reclaim_no_volume=484
- **EVAL::MOVER_TREND_PULLBACK** (total=41403): basic_filters_failed=18208, mover_run_too_small=12310, no_reclaim=7720, no_pullback_tag=2569, insufficient_candles=596
- **EVAL::OPENING_RANGE_BREAKOUT** (total=51207): feature_disabled=51207
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=46333): regime_blocked=36151, breakout_not_found=7189, basic_filters_failed=1811, adx_reject=1175, ema_alignment_reject=7
- **EVAL::QUIET_COMPRESSION_BREAK** (total=46238): compression_not_detected=23438, regime_blocked=11695, basic_filters_failed=9892, breakout_not_detected=1139, volume_confirmation_failed=74
- **EVAL::SR_FLIP_RETEST** (total=44106): basic_filters_failed=11703, flip_close_not_confirmed=7329, whipsaw_flip=7154, long_break_volume_thin=4790, long_disabled=4226, reclaim_hold_failed=3200, retest_out_of_zone=2960, regime_blocked=1531, wick_quality_failed=821, long_acceptance_not_held=251, missing_fvg_or_orderblock=97, ema_alignment_reject=44
- **EVAL::STANDARD** (total=32160): adx_reject=8214, momentum_reject=8206, basic_filters_failed=5251, sweeps_not_detected=4321, macd_reject=4233, ema_alignment_reject=1728, invalid_sl_geometry=179, rsi_reject=28
- **EVAL::TREND_PULLBACK** (total=35067): h1_trend_not_aligned=13280, h1_pullback_not_confirmed=9397, ema_alignment_reject=4699, basic_filters_failed=4389, ema_not_tested_prev=1149, no_ema_reclaim_close=925, body_conviction_fail=481, rsi_reject=295, prev_already_below_emas=99, no_prev_high_break=96, no_prev_low_break=93, prev_already_above_emas=79, momentum_flat=70, momentum_reject=10, ema21_not_tagged=4, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=53331): breakout_not_found=26804, basic_filters_failed=18474, move_not_fresh=5161, breakout_stale=2431, retest_proximity_failed=429, volume_spike_missing=31, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=40968): momentum_reject=33572, recent_ticks_insufficient=6133, basic_filters_failed=1263

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 120125 | 46.9% |
| QUIET | 52661 | 20.6% |
| TRENDING_UP | 43011 | 16.8% |
| TRENDING_DOWN | 30478 | 11.9% |
| VOLATILE | 9640 | 3.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **57**
- Average confidence gap to threshold: **12.26** (samples=57) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BZUSDT=14, LINKUSDT=11, SOLUSDT=11, AMDUSDT=6, ZECUSDT=4, LTCUSDT=4, BTCUSDT=4, ETHUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 72 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 41 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 427 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 31 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 60 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 4 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 123 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 62 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 496 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 40 |
| SR_FLIP_RETEST | filtered | min_confidence | 158 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 22 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 76 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 77.80 | 65.00 | -12.80 | 22.80 | 15.80 | 20.00 | 6.00 | 7.20 |
| DIVERGENCE_CONTINUATION | filtered | 72 | 54.20 | 65.00 | 10.80 | 21.22 | 19.13 | 18.38 | 1.18 | 10.28 |
| DIVERGENCE_CONTINUATION | kept | 41 | 72.48 | 65.00 | -7.48 | 20.38 | 19.96 | 17.32 | 2.02 | -2.81 |
| FAILED_AUCTION_RECLAIM | filtered | 458 | 53.56 | 65.00 | 11.44 | 20.68 | 19.01 | 20.00 | 4.69 | 9.62 |
| FAILED_AUCTION_RECLAIM | kept | 60 | 71.76 | 65.00 | -6.76 | 22.94 | 19.84 | 20.00 | 4.89 | 0.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 4 | 54.70 | 65.00 | 10.30 | 21.95 | 19.10 | 17.00 | 3.00 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 123 | 68.26 | 65.00 | -3.26 | 20.80 | 19.42 | 17.07 | 3.20 | 0.17 |
| MOVER_AVWAP_SCALP | kept | 62 | 86.50 | 65.00 | -21.50 | 17.70 | 18.30 | 15.80 | 3.50 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 496 | 79.18 | 65.00 | -14.18 | 18.06 | 18.17 | 15.80 | 4.60 | -0.75 |
| QUIET_COMPRESSION_BREAK | kept | 40 | 81.30 | 65.00 | -16.30 | 20.22 | 20.00 | 20.00 | 0.00 | 1.30 |
| SR_FLIP_RETEST | filtered | 180 | 52.53 | 65.00 | 12.47 | 20.47 | 19.73 | 16.57 | 1.53 | 16.95 |
| SR_FLIP_RETEST | kept | 76 | 67.41 | 65.00 | -2.41 | 19.94 | 19.98 | 15.65 | 2.49 | 2.61 |
| TREND_PULLBACK_EMA | kept | 1 | 77.00 | 65.00 | -12.00 | 22.60 | 20.00 | 15.20 | 5.50 | 0.00 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.90 | 65.00 | -13.90 | 20.70 | 19.30 | 20.00 | 5.00 | 5.10 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 77.80 | 25.00 | 18.00 | 12.00 | 11.00 | 5.00 | 8.00 | 6.00 |
| DIVERGENCE_CONTINUATION | filtered | 72 | 54.20 | 23.00 | 9.25 | 11.42 | 12.33 | 5.07 | 7.22 | 1.18 |
| DIVERGENCE_CONTINUATION | kept | 41 | 72.48 | 21.29 | 16.78 | 6.29 | 12.22 | 4.68 | 9.38 | 2.02 |
| FAILED_AUCTION_RECLAIM | filtered | 458 | 53.56 | 21.53 | 17.53 | 5.85 | 11.47 | 5.18 | 4.88 | 4.69 |
| FAILED_AUCTION_RECLAIM | kept | 60 | 71.76 | 24.33 | 17.80 | 3.40 | 9.45 | 5.28 | 7.11 | 4.89 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 4 | 54.70 | 23.00 | 14.00 | 12.00 | 12.00 | 5.00 | 7.30 | 3.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 123 | 68.26 | 24.33 | 14.03 | 5.59 | 12.02 | 4.41 | 4.85 | 3.20 |
| MOVER_AVWAP_SCALP | kept | 62 | 86.50 | 23.00 | 18.00 | 15.00 | 14.00 | 5.00 | 8.00 | 3.50 |
| MOVER_TREND_PULLBACK | kept | 496 | 79.18 | 17.69 | 18.00 | 7.90 | 14.34 | 6.98 | 9.69 | 4.60 |
| QUIET_COMPRESSION_BREAK | kept | 40 | 81.30 | 23.60 | 18.00 | 12.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 180 | 52.53 | 19.71 | 16.78 | 6.75 | 13.43 | 7.46 | 3.82 | 1.53 |
| SR_FLIP_RETEST | kept | 76 | 67.41 | 23.50 | 17.61 | 4.34 | 11.55 | 5.80 | 4.86 | 2.49 |
| TREND_PULLBACK_EMA | kept | 1 | 77.00 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 5.50 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.90 | 21.00 | 16.00 | 13.50 | 15.50 | 5.00 | 8.00 | 5.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 1 | 77.80 | 0.00 | 0.00 | 0.00 | 0.00 | 7.20 | 0.00 | 0.00 | 0.00 | **7.20** |
| DIVERGENCE_CONTINUATION | filtered | 72 | 54.20 | 0.00 | 0.00 | 0.00 | 0.00 | 5.40 | 0.00 | 0.00 | 0.00 | **5.40** |
| DIVERGENCE_CONTINUATION | kept | 41 | 72.48 | 0.00 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.12** |
| FAILED_AUCTION_RECLAIM | filtered | 458 | 53.56 | 0.00 | 0.00 | 1.55 | 0.00 | 2.34 | 0.00 | 0.00 | 0.00 | **3.89** |
| FAILED_AUCTION_RECLAIM | kept | 60 | 71.76 | 0.00 | 0.00 | 0.48 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.48** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 4 | 54.70 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 123 | 68.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 0.00 | **0.10** |
| MOVER_AVWAP_SCALP | kept | 62 | 86.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 496 | 79.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 40 | 81.30 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | filtered | 180 | 52.53 | 0.00 | 0.00 | 0.00 | 0.00 | 4.49 | 0.00 | 0.00 | 3.03 | **7.52** |
| SR_FLIP_RETEST | kept | 76 | 67.41 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.08 | **0.08** |
| TREND_PULLBACK_EMA | kept | 1 | 77.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 78.90 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | 0.00 | 0.00 | 0.00 | **3.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=97 (68.3%) | PREMATURE=16 (11.3%) | NEUTRAL=29 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 81 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 97 | 16 | 29 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 5 | 1 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 19 | 6 | 11 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 2 | 3 | 0 |
| MOVER_AVWAP_SCALP | 16 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 29 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 20 | 5 | 10 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 97 | 16 | 29 | 71.0 | 28.6 | +0.30 | **KEEP** — net-helping: avg +0.30R/kill across 142 kills (saved 71.0R vs missed 28.6R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `89676`
- `Path funnel` emissions: `30`
- `Regime distribution` emissions: `30`
- `QUIET_SCALP_BLOCK` events: `57`
- `confidence_gate` events: `1616`
- `free_channel_post` events: `11`
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
| futures_liq | 1 | 1706 | 1706 | 1706 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **11**

| Source | Count |
|---|---:|
| signal_close | 9 |
| signal_highlight | 2 |

- By severity: HIGH=11

## Dependency readiness
- cvd: presence[present=202858] state[populated=202858] buckets[many=202858] sources[none] quality[none]
- funding_rate: presence[absent=27816, present=175042] state[empty=27816, populated=175042] buckets[few=175042, none=27816] sources[none] quality[none]
- liquidation_clusters: presence[absent=128046, present=74812] state[empty=128046, populated=74812] buckets[few=63024, none=128046, some=11788] sources[none] quality[none]
- oi_snapshot: presence[absent=27816, present=175042] state[empty=27816, populated=175042] buckets[few=52, many=174839, none=27816, some=151] sources[none] quality[none]
- order_book: presence[absent=53803, present=149055] state[populated=149055, unavailable=53803] buckets[few=149055, none=53803] sources[book_ticker=149055, unavailable=53803] quality[none=53803, top_of_book_only=149055]
- orderblocks: presence[absent=202858] state[empty=202858] buckets[none=202858] sources[not_implemented=202858] quality[none]
- recent_ticks: presence[absent=1858, present=201000] state[empty=1858, populated=201000] buckets[many=201000, none=1858] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.386069416999817` sec
- Median create→first breach: `1131.9427245855331` sec
- Median create→terminal: `2538.51921749115` sec
- Median first breach→terminal: `2.323304057121277` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | 1.5917 | 1334.6975479125977 | 2090.8269369602203 |
| DIVERGENCE_CONTINUATION | 7 | 7 | 28.6 | 28.6 | 28.6 | 0.0 | 0.4871 | 1599.3299934864044 | 2432.7327489852905 |
| FAILED_AUCTION_RECLAIM | 10 | 10 | 0.0 | 30.0 | 0.0 | 0.0 | -0.1407 | 1331.5010695457458 | 2787.443999528885 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5642 | None | 3600.0730590820312 |
| MOVER_AVWAP_SCALP | 4 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0461 | None | 3603.282956600189 |
| MOVER_TREND_PULLBACK | 13 | 13 | 7.7 | 23.1 | 7.7 | 0.0 | -0.4465 | 906.2018365859985 | 3604.27214884758 |
| SR_FLIP_RETEST | 12 | 12 | 50.0 | 8.3 | 50.0 | 0.0 | 0.7891 | 1422.1789613962173 | 1826.6313014030457 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 6899 | 14 | 5937 | 50.0 | 8.3 | 1422.1789613962173 | 1826.6313014030457 | 962 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 610 | 1 | 602 | 0.0 | 0.0 | None | None | 8 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `49`
- Gating Δ: `84077`
- No-generation Δ: `781128`
- Fast failures Δ: `-2`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 1.6275, "current_avg_pnl": 1.5917, "current_win_rate": 0.0, "previous_avg_pnl": -0.0358, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.6844, "current_avg_pnl": 0.4871, "current_win_rate": 28.6, "previous_avg_pnl": -0.1973, "previous_win_rate": 20.0, "win_rate_delta": 8.6}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1693, "current_avg_pnl": -0.1407, "current_win_rate": 0.0, "previous_avg_pnl": 0.0286, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 1.3602, "current_avg_pnl": 0.5642, "current_win_rate": 0.0, "previous_avg_pnl": -0.796, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.0704, "current_avg_pnl": -0.0461, "current_win_rate": 0.0, "previous_avg_pnl": 0.0243, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.1541, "current_avg_pnl": -0.4465, "current_win_rate": 7.7, "previous_avg_pnl": -0.6006, "previous_win_rate": 0.0, "win_rate_delta": 7.7}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.2365, "current_avg_pnl": 0.7891, "current_win_rate": 50.0, "previous_avg_pnl": 0.5526, "previous_win_rate": 50.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 14, "geometry_changed_delta": 0, "geometry_preserved_delta": 962, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -878.12, "median_terminal_delta_sec": -918.7, "sl_rate_delta": -8.4, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 8, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1476.93, "median_terminal_delta_sec": -1478.37, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **MOVER_TREND_PULLBACK**
- Most promising healthy path: **SR_FLIP_RETEST**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **MOVER_TREND_PULLBACK**
