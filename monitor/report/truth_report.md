# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, SR_FLIP_RETEST, FAILED_AUCTION_RECLAIM
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `648` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2 | 2 | 0 | 2 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9737 | 9737 | 9408 | 1 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 61227 | 61228 | 2 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 50325 | 50328 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 50225 | 47092 | 3234 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 50332 | 47695 | 2688 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 57000 | 56919 | 89 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 46411 | 46411 | 4 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 50381 | 50383 | 3 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 68997 | 68669 | 3631 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 61232 | 47940 | 21046 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 56508 | 56511 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 50329 | 50331 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 50222 | 50196 | 29 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 49722 | 47128 | 3085 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 40012 | 36698 | 3452 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 40151 | 40017 | 140 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 61221 | 61220 | 5 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 46415 | 46417 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 8350 | 8350 | 7449 | 8 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 403 | 403 | 311 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 17 | 17 | 17 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 14572 | 14572 | 14313 | 7 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 4 | 4 | 4 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 7928 | 7928 | 7600 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 54717 | 54717 | 53919 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 87 | 87 | 0 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 9247 | 9247 | 8639 | 5 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 643 | 643 | 643 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 47 | 47 | 28 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=61228): breakout_not_found=26220, basic_filters_failed=23166, move_not_fresh=8475, breakout_stale=2768, retest_proximity_failed=430, volume_spike_missing=123, insufficient_candles=37, missing_fvg_or_orderblock=9
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=50328): cls_disabled_merged_into_lsr=50328
- **EVAL::DIVERGENCE_CONTINUATION** (total=47092): basic_filters_failed=16216, cvd_divergence_failed=14710, h1_trend_not_aligned=12335, ema_alignment_reject=2942, retest_proximity_failed=523, missing_fvg_or_orderblock=366
- **EVAL::FAILED_AUCTION_RECLAIM** (total=47695): auction_not_detected=19091, basic_filters_failed=15399, tail_too_small=5760, reclaim_hold_failed=5477, regime_blocked=1957, rsi_reject=11
- **EVAL::FUNDING_EXTREME** (total=56919): funding_not_extreme=36794, basic_filters_failed=18337, missing_funding_rate=717, ema_alignment_reject=535, rsi_reject=355, momentum_reject=89, cvd_divergence_failed=78, insufficient_candles=10, missing_fvg_or_orderblock=4
- **EVAL::LIQUIDATION_REVERSAL** (total=46411): cascade_threshold_not_met=27004, basic_filters_failed=18792, cvd_divergence_failed=370, rsi_reject=166, insufficient_candles=37, missing_fvg_or_orderblock=23, volume_spike_missing=19
- **EVAL::MA_CROSS_TREND_SHIFT** (total=50383): no_ma_cross=33533, basic_filters_failed=16221, ma_cross_cooldown=617, ma_cross_htf_misaligned=12
- **EVAL::MOVER_AVWAP_SCALP** (total=68669): no_avwap_tag=35403, basic_filters_failed=23203, no_mover_leg=8812, no_avwap_reclaim=448, avwap_reclaim_no_volume=389, avwap_slope_against=283, anchor_too_recent=94, insufficient_candles=37
- **EVAL::MOVER_TREND_PULLBACK** (total=47940): basic_filters_failed=23180, mover_run_too_small=15807, no_reclaim=7703, no_pullback_tag=1213, insufficient_candles=37
- **EVAL::OPENING_RANGE_BREAKOUT** (total=56511): feature_disabled=56511
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=50331): regime_blocked=32884, breakout_not_found=10756, basic_filters_failed=5622, adx_reject=1065, ema_alignment_reject=4
- **EVAL::QUIET_COMPRESSION_BREAK** (total=50196): compression_not_detected=20387, regime_blocked=19354, basic_filters_failed=9772, breakout_not_detected=664, volume_confirmation_failed=18, missing_fvg_or_orderblock=1
- **EVAL::SR_FLIP_RETEST** (total=47128): basic_filters_failed=15391, flip_close_not_confirmed=9536, reclaim_hold_failed=5582, whipsaw_flip=4687, retest_out_of_zone=4082, long_break_volume_thin=3969, regime_blocked=1955, long_disabled=1026, wick_quality_failed=751, long_acceptance_not_held=89, missing_fvg_or_orderblock=49, ema_alignment_reject=11
- **EVAL::STANDARD** (total=36698): momentum_reject=9742, basic_filters_failed=9714, adx_reject=6169, sweeps_not_detected=4669, macd_reject=3665, ema_alignment_reject=1913, rsi_reject=765, invalid_sl_geometry=61
- **EVAL::TREND_PULLBACK** (total=40017): h1_trend_not_aligned=13704, h1_pullback_not_confirmed=12648, basic_filters_failed=4316, ema_alignment_reject=2675, ema_not_tested_prev=2443, no_ema_reclaim_close=2108, rsi_reject=950, body_conviction_fail=677, prev_already_below_emas=195, no_prev_low_break=186, prev_already_above_emas=47, missing_fvg_or_orderblock=18, momentum_reject=18, no_prev_high_break=11, ema21_not_tagged=11, momentum_flat=10
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=61220): breakout_not_found=35365, basic_filters_failed=23166, move_not_fresh=1486, breakout_stale=779, retest_proximity_failed=353, insufficient_candles=37, volume_spike_missing=28, rsi_reject=6
- **EVAL::WHALE_MOMENTUM** (total=46417): momentum_reject=37143, recent_ticks_insufficient=5976, basic_filters_failed=3298

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 111714 | 37.4% |
| TRENDING_DOWN | 90437 | 30.2% |
| QUIET | 58848 | 19.7% |
| TRENDING_UP | 21395 | 7.2% |
| VOLATILE | 16706 | 5.6% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **71**
- Average confidence gap to threshold: **12.79** (samples=71) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: TRXUSDT=38, BTCUSDT=16, ETHUSDT=9, AAVEUSDT=5, 1000BONKUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | kept | min_confidence_pass | 2 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 38 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 22 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 312 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 13 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 74 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 21 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 169 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 12 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 289 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 724 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 87 |
| SR_FLIP_RETEST | filtered | min_confidence | 77 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 20 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 4 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 19 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 71.50 | 65.00 | -6.50 | 20.75 | 19.90 | 20.00 | 4.50 | 6.00 |
| DIVERGENCE_CONTINUATION | filtered | 41 | 50.83 | 65.00 | 14.17 | 19.64 | 19.99 | 17.06 | 1.34 | 18.04 |
| DIVERGENCE_CONTINUATION | kept | 22 | 67.07 | 65.00 | -2.07 | 19.92 | 20.00 | 15.48 | 0.36 | 0.22 |
| FAILED_AUCTION_RECLAIM | filtered | 325 | 53.75 | 65.00 | 11.25 | 20.85 | 19.22 | 20.00 | 4.10 | 4.21 |
| FAILED_AUCTION_RECLAIM | kept | 74 | 75.98 | 65.00 | -10.98 | 23.19 | 18.99 | 20.00 | 4.79 | 0.00 |
| FUNDING_EXTREME_SIGNAL | filtered | 21 | 47.11 | 65.00 | 17.89 | 20.25 | 20.00 | 17.00 | 1.05 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 169 | 50.94 | 65.00 | 14.06 | 18.14 | 18.92 | 18.88 | 3.53 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 68.96 | 65.00 | -3.96 | 19.17 | 19.20 | 17.33 | 1.42 | 1.53 |
| MOVER_AVWAP_SCALP | kept | 289 | 72.06 | 65.00 | -7.06 | 19.39 | 19.58 | 15.80 | 2.86 | 0.85 |
| MOVER_TREND_PULLBACK | kept | 724 | 81.75 | 65.00 | -16.75 | 20.60 | 17.60 | 15.80 | 4.12 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 87 | 77.34 | 65.00 | -12.34 | 19.63 | 20.00 | 20.00 | 0.00 | -0.58 |
| SR_FLIP_RETEST | filtered | 97 | 58.79 | 65.00 | 6.21 | 22.18 | 19.96 | 15.54 | 1.56 | 10.56 |
| SR_FLIP_RETEST | kept | 4 | 67.92 | 65.00 | -2.92 | 21.85 | 19.85 | 16.65 | 2.50 | 6.83 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.55 | 65.00 | 5.45 | 21.12 | 18.03 | 20.00 | 4.76 | 6.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 71.50 | 25.00 | 14.00 | 12.00 | 14.00 | 5.00 | 3.00 | 4.50 |
| DIVERGENCE_CONTINUATION | filtered | 41 | 50.83 | 19.54 | 8.00 | 11.34 | 13.71 | 5.29 | 9.66 | 1.34 |
| DIVERGENCE_CONTINUATION | kept | 22 | 67.07 | 23.55 | 8.45 | 6.68 | 13.82 | 5.00 | 9.43 | 0.36 |
| FAILED_AUCTION_RECLAIM | filtered | 325 | 53.75 | 21.50 | 17.22 | 5.66 | 12.59 | 6.38 | 4.51 | 4.10 |
| FAILED_AUCTION_RECLAIM | kept | 74 | 75.98 | 22.51 | 17.78 | 5.80 | 11.88 | 6.49 | 7.13 | 4.79 |
| FUNDING_EXTREME_SIGNAL | filtered | 21 | 47.11 | 25.00 | 8.00 | 3.00 | 16.29 | 10.00 | 3.78 | 1.05 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 169 | 50.94 | 22.87 | 14.00 | 6.37 | 12.00 | 5.47 | 6.70 | 3.53 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 68.96 | 21.00 | 16.00 | 5.50 | 13.08 | 5.50 | 7.98 | 1.42 |
| MOVER_AVWAP_SCALP | kept | 289 | 72.06 | 20.43 | 18.00 | 7.50 | 11.93 | 5.49 | 6.70 | 2.86 |
| MOVER_TREND_PULLBACK | kept | 724 | 81.75 | 17.01 | 18.00 | 13.48 | 12.46 | 6.97 | 9.72 | 4.12 |
| QUIET_COMPRESSION_BREAK | kept | 87 | 77.34 | 17.92 | 18.00 | 11.62 | 14.00 | 6.53 | 10.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 97 | 58.79 | 19.97 | 15.94 | 5.81 | 12.86 | 5.79 | 7.42 | 1.56 |
| SR_FLIP_RETEST | kept | 4 | 67.92 | 25.00 | 18.00 | 6.00 | 12.25 | 5.00 | 6.00 | 2.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.55 | 23.74 | 18.00 | 12.00 | 14.00 | 3.95 | 4.70 | 4.76 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | kept | 2 | 71.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.00 | **3.00** |
| DIVERGENCE_CONTINUATION | filtered | 41 | 50.83 | 0.00 | 0.00 | 0.00 | 0.00 | 20.02 | 0.00 | 0.00 | 0.00 | **20.02** |
| DIVERGENCE_CONTINUATION | kept | 22 | 67.07 | 0.00 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.22** |
| FAILED_AUCTION_RECLAIM | filtered | 325 | 53.75 | 0.00 | 0.00 | 0.34 | 0.00 | 0.96 | 0.00 | 0.00 | 0.00 | **1.30** |
| FAILED_AUCTION_RECLAIM | kept | 74 | 75.98 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 21 | 47.11 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 169 | 50.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 12 | 68.96 | 0.00 | 0.00 | 0.67 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.67** |
| MOVER_AVWAP_SCALP | kept | 289 | 72.06 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.85 | **0.85** |
| MOVER_TREND_PULLBACK | kept | 724 | 81.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 87 | 77.34 | 0.00 | 0.00 | 0.00 | 0.00 | 2.42 | 0.00 | 0.00 | 0.00 | **2.42** |
| SR_FLIP_RETEST | filtered | 97 | 58.79 | 0.00 | 0.00 | 0.00 | 0.00 | 2.45 | 0.00 | 0.00 | 0.00 | **2.45** |
| SR_FLIP_RETEST | kept | 4 | 67.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 19 | 59.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.60 | **3.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=81 (67.5%) | PREMATURE=17 (14.2%) | NEUTRAL=22 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 64 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 81 | 17 | 22 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 4 | 2 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 16 | 5 | 7 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 2 | 2 | 0 |
| MOVER_AVWAP_SCALP | 14 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 28 | 2 | 1 | 0 |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 15 | 6 | 9 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 81 | 17 | 22 | 60.2 | 27.1 | +0.28 | **KEEP** — net-helping: avg +0.28R/kill across 120 kills (saved 60.2R vs missed 27.1R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `81903`
- `Path funnel` emissions: `34`
- `Regime distribution` emissions: `34`
- `QUIET_SCALP_BLOCK` events: `71`
- `confidence_gate` events: `1886`
- `free_channel_post` events: `3`
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
| futures_liq | 1 | 3640 | 3640 | 3640 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **3**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 1 |

- By severity: HIGH=3

## Dependency readiness
- cvd: presence[present=231257] state[populated=231257] buckets[few=3, many=231219, some=35] sources[none] quality[none]
- funding_rate: presence[absent=31930, present=199327] state[empty=31930, populated=199327] buckets[few=199327, none=31930] sources[none] quality[none]
- liquidation_clusters: presence[absent=146022, present=85235] state[empty=146022, populated=85235] buckets[few=71450, none=146022, some=13785] sources[none] quality[none]
- oi_snapshot: presence[absent=31929, present=199328] state[empty=31929, populated=199328] buckets[few=286, many=197464, none=31929, some=1578] sources[none] quality[none]
- order_book: presence[absent=62796, present=168461] state[populated=168461, unavailable=62796] buckets[few=168461, none=62796] sources[book_ticker=168461, unavailable=62796] quality[none=62796, top_of_book_only=168461]
- orderblocks: presence[absent=231257] state[empty=231257] buckets[none=231257] sources[not_implemented=231257] quality[none]
- recent_ticks: presence[present=231257] state[populated=231257] buckets[many=231257] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.234135031700134` sec
- Median create→first breach: `1002.3900294303894` sec
- Median create→terminal: `2237.078251004219` sec
- Median first breach→terminal: `1.9496474266052246` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 1.3}, "under_180s": {"count": 3, "pct": 3.9}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 1.3}}`
- ~3 minute terminal-close behavior: `{"count": 4, "pct": 3.1}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 6 | 6 | 16.7 | 50.0 | 16.7 | 0.0 | 0.2839 | 579.3527920246124 | 1336.687539935112 |
| DIVERGENCE_CONTINUATION | 19 | 19 | 21.1 | 47.4 | 21.1 | 0.0 | 0.0384 | 1181.8171454668045 | 1362.483321905136 |
| FAILED_AUCTION_RECLAIM | 32 | 32 | 6.2 | 18.8 | 6.2 | 0.0 | 0.3312 | 1457.7069475650787 | 3600.5548290014267 |
| LIQUIDITY_SWEEP_REVERSAL | 5 | 5 | 20.0 | 40.0 | 20.0 | 0.0 | -0.0789 | 484.9011824131012 | 686.1017279624939 |
| MOVER_AVWAP_SCALP | 8 | 8 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0567 | None | 3603.2359920740128 |
| MOVER_TREND_PULLBACK | 30 | 30 | 3.3 | 30.0 | 3.3 | 0.0 | -0.5188 | 522.8061990737915 | 2553.1079790592194 |
| SR_FLIP_RETEST | 25 | 25 | 40.0 | 24.0 | 40.0 | 0.0 | 0.4436 | 1310.9793899059296 | 1916.3324840068817 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1476.9315971136093 | 1478.3650945425034 |
| VOLUME_SURGE_BREAKOUT | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -0.5469 | 1964.0596549510956 | 1964.6024980545044 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 9247 | 5 | 8639 | 40.0 | 24.0 | 1310.9793899059296 | 1916.3324840068817 | 608 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 643 | 0 | 643 | 0.0 | 0.0 | 1476.9315971136093 | 1478.3650945425034 | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `24`
- Gating Δ: `102331`
- No-generation Δ: `865183`
- Fast failures Δ: `-1`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 0.785, "current_avg_pnl": 0.2839, "current_win_rate": 16.7, "previous_avg_pnl": -0.5011, "previous_win_rate": 0.0, "win_rate_delta": 16.7}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.3122, "current_avg_pnl": 0.0384, "current_win_rate": 21.1, "previous_avg_pnl": -0.2738, "previous_win_rate": 15.8, "win_rate_delta": 5.3}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.1512, "current_avg_pnl": 0.3312, "current_win_rate": 6.2, "previous_avg_pnl": 0.4824, "previous_win_rate": 17.1, "win_rate_delta": -10.9}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.2998, "current_avg_pnl": -0.0789, "current_win_rate": 20.0, "previous_avg_pnl": -0.3787, "previous_win_rate": 0.0, "win_rate_delta": 20.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.0042, "current_avg_pnl": -0.0567, "current_win_rate": 0.0, "previous_avg_pnl": -0.0525, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -0.3414, "current_avg_pnl": -0.5188, "current_win_rate": 3.3, "previous_avg_pnl": -0.1774, "previous_win_rate": 2.6, "win_rate_delta": 0.7}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.4443, "current_avg_pnl": 0.4436, "current_win_rate": 40.0, "previous_avg_pnl": -0.0007, "previous_win_rate": 9.1, "win_rate_delta": 30.9}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": 0.7219, "current_avg_pnl": 0.0, "current_win_rate": 0.0, "previous_avg_pnl": -0.7219, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -0.1138, "current_avg_pnl": -0.5469, "current_win_rate": 0.0, "previous_avg_pnl": -0.4331, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 608, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 82.26, "median_terminal_delta_sec": -355.82, "sl_rate_delta": -12.4, "win_rate_delta": 30.9}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 926.32, "median_terminal_delta_sec": 921.6, "sl_rate_delta": -33.3, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **MOVER_AVWAP_SCALP**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
