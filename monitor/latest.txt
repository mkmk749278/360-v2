# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `5887` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 3498 | 3498 | 3322 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 15318 | 15318 | 13774 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 206616 | 205720 | 985 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 155812 | 155828 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 155233 | 151803 | 3989 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 155879 | 152061 | 4211 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 207904 | 207936 | 27 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 206487 | 206500 | 14 | 0 | 0 | 0 | low-sample (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 156279 | 156320 | 19 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 206709 | 206719 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 155830 | 155866 | 4 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 155077 | 153996 | 1227 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 153837 | 147386 | 7614 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 152284 | 140909 | 12675 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 153593 | 153556 | 73 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 206556 | 206460 | 151 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 206520 | 206551 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 21212 | 21212 | 15521 | 56 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 190 | 190 | 177 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 18 | 18 | 18 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 89287 | 89287 | 78819 | 133 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 37 | 37 | 35 | 0 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 36 | 36 | 36 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 7134 | 7134 | 7134 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 30693 | 30693 | 15110 | 122 | active-low-quality (none) |
| TREND_PULLBACK_CONTINUATION | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 364 | 364 | 364 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 1616 | 1616 | 1022 | 4 | active-low-quality (none) |
| WHALE_MOMENTUM | 0 | 0 | 0 | 0 | 0 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=205720): breakout_not_found=105433, basic_filters_failed=68984, retest_proximity_failed=21503, volume_spike_missing=3783, ema_alignment_reject=3695, insufficient_candles=1794, missing_fvg_or_orderblock=470, rsi_reject=58
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=155828): cls_disabled_merged_into_lsr=155828
- **EVAL::DIVERGENCE_CONTINUATION** (total=151803): basic_filters_failed=49124, cvd_divergence_failed=41149, h1_trend_not_aligned=38899, retest_proximity_failed=18898, ema_alignment_reject=1721, regime_blocked=1556, missing_fvg_or_orderblock=452, cvd_insufficient=3, missing_cvd=1
- **EVAL::FAILED_AUCTION_RECLAIM** (total=152061): auction_not_detected=56568, basic_filters_failed=48334, reclaim_hold_failed=23610, tail_too_small=18524, regime_blocked=5014, rsi_reject=11
- **EVAL::FUNDING_EXTREME** (total=207936): funding_not_extreme=134450, basic_filters_failed=69488, ema_alignment_reject=2912, rsi_reject=694, missing_funding_rate=189, insufficient_candles=155, cvd_divergence_failed=36, momentum_reject=7, missing_fvg_or_orderblock=5
- **EVAL::LIQUIDATION_REVERSAL** (total=206500): cascade_threshold_not_met=131996, basic_filters_failed=69189, cvd_divergence_failed=2115, rsi_reject=1943, insufficient_candles=1154, missing_fvg_or_orderblock=63, volume_spike_missing=38, cvd_insufficient=2
- **EVAL::MA_CROSS_TREND_SHIFT** (total=156321): no_ma_cross=103542, basic_filters_failed=49137, ma_cross_cooldown=3642
- **EVAL::OPENING_RANGE_BREAKOUT** (total=206719): feature_disabled=206719
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=155866): regime_blocked=104114, breakout_not_found=24549, basic_filters_failed=22601, adx_reject=4597, ema_alignment_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=153996): compression_not_detected=59312, regime_blocked=56494, basic_filters_failed=25724, macd_reject=6510, volume_confirmation_failed=5659, missing_fvg_or_orderblock=273, breakout_not_detected=24
- **EVAL::SR_FLIP_RETEST** (total=147386): basic_filters_failed=48313, reclaim_hold_failed=31990, flip_close_not_confirmed=26213, retest_out_of_zone=20802, ema_alignment_reject=8668, wick_quality_failed=5622, regime_blocked=4962, missing_fvg_or_orderblock=749, rsi_reject=67
- **EVAL::STANDARD** (total=140909): momentum_reject=56886, basic_filters_failed=27932, sweeps_not_detected=26453, adx_reject=23534, macd_reject=2220, ema_alignment_reject=1940, rsi_reject=1198, invalid_sl_geometry=746
- **EVAL::TREND_PULLBACK** (total=153556): h1_trend_not_aligned=53496, basic_filters_failed=24429, ema_alignment_reject=21053, h1_pullback_not_confirmed=21036, ema_not_tested_prev=19332, no_ema_reclaim_close=9652, regime_blocked=3184, rsi_reject=530, body_conviction_fail=492, prev_already_above_emas=178, momentum_flat=73, prev_already_below_emas=36, no_prev_high_break=26, ema21_not_tagged=18, no_prev_low_break=11, momentum_reject=9, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=206460): breakout_not_found=104955, basic_filters_failed=68980, retest_proximity_failed=24258, ema_alignment_reject=3279, volume_spike_missing=2844, insufficient_candles=1794, missing_fvg_or_orderblock=350
- **EVAL::WHALE_MOMENTUM** (total=206551): momentum_reject=129556, recent_ticks_insufficient=48592, basic_filters_failed=28381, insufficient_candles=22

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 476988 | 44.5% |
| QUIET | 229363 | 21.4% |
| TRENDING_UP | 181973 | 17.0% |
| TRENDING_DOWN | 136475 | 12.7% |
| VOLATILE | 47875 | 4.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **210**
- Average confidence gap to threshold: **16.99** (samples=210) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BZUSDT=43, ETHUSDT=38, LINKUSDT=32, SOLUSDT=19, 1000PEPEUSDT=17, LTCUSDT=16, TRXUSDT=16, WLFIUSDT=9, DOTUSDT=7, DOGEUSDT=7

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 21 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 7 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 330 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 7 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 84 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 602 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 56 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 1454 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 766 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 87 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 2079 |
| SR_FLIP_RETEST | filtered | min_confidence | 1792 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 60 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2342 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 102 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 50 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 21 | 63.95 | 65.00 | 1.05 | 20.87 | 19.15 | 20.00 | 0.00 | 3.38 |
| BREAKDOWN_SHORT | kept | 7 | 67.00 | 65.00 | -2.00 | 20.60 | 18.20 | 20.00 | 0.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 337 | 58.57 | 65.00 | 6.43 | 22.47 | 19.00 | 18.14 | 2.25 | 9.74 |
| DIVERGENCE_CONTINUATION | kept | 84 | 67.82 | 65.00 | -2.82 | 22.09 | 17.93 | 18.94 | 1.19 | 10.85 |
| FAILED_AUCTION_RECLAIM | filtered | 658 | 56.59 | 65.00 | 8.41 | 21.03 | 19.18 | 20.00 | 2.81 | 7.13 |
| FAILED_AUCTION_RECLAIM | kept | 1454 | 71.13 | 65.00 | -6.13 | 21.77 | 19.60 | 20.00 | 2.94 | 0.25 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 853 | 56.41 | 65.00 | 8.59 | 21.05 | 19.85 | 18.38 | 1.21 | 8.84 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2079 | 68.83 | 65.00 | -3.83 | 21.69 | 19.69 | 17.60 | 1.72 | 0.22 |
| SR_FLIP_RETEST | filtered | 1852 | 56.00 | 65.00 | 9.00 | 20.98 | 19.79 | 16.35 | 1.59 | 7.42 |
| SR_FLIP_RETEST | kept | 2342 | 71.77 | 65.00 | -6.77 | 21.81 | 19.90 | 15.76 | 1.94 | 0.87 |
| VOLUME_SURGE_BREAKOUT | filtered | 102 | 59.68 | 65.00 | 5.32 | 21.11 | 19.05 | 19.91 | 2.35 | 3.74 |
| VOLUME_SURGE_BREAKOUT | kept | 50 | 68.07 | 65.00 | -3.07 | 22.68 | 19.57 | 19.91 | 2.71 | 0.72 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 21 | 63.95 | 24.52 | 8.48 | 3.14 | 14.00 | 8.81 | 8.38 | 0.00 |
| BREAKDOWN_SHORT | kept | 7 | 67.00 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 10.00 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 337 | 58.57 | 18.54 | 14.50 | 6.25 | 13.39 | 5.25 | 8.13 | 2.25 |
| DIVERGENCE_CONTINUATION | kept | 84 | 67.82 | 24.90 | 17.76 | 7.43 | 13.95 | 5.15 | 8.27 | 1.19 |
| FAILED_AUCTION_RECLAIM | filtered | 658 | 56.59 | 21.37 | 17.28 | 6.12 | 13.14 | 5.99 | 5.23 | 2.81 |
| FAILED_AUCTION_RECLAIM | kept | 1454 | 71.13 | 22.45 | 15.57 | 5.02 | 11.40 | 6.45 | 7.55 | 2.94 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 853 | 56.41 | 21.78 | 14.38 | 8.73 | 12.89 | 5.45 | 5.75 | 1.21 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2079 | 68.83 | 23.69 | 14.07 | 4.85 | 11.63 | 5.98 | 7.10 | 1.72 |
| SR_FLIP_RETEST | filtered | 1852 | 56.00 | 19.54 | 17.68 | 4.58 | 13.40 | 5.73 | 6.83 | 1.59 |
| SR_FLIP_RETEST | kept | 2342 | 71.77 | 21.67 | 16.42 | 4.72 | 13.93 | 6.25 | 8.73 | 1.94 |
| VOLUME_SURGE_BREAKOUT | filtered | 102 | 59.68 | 21.71 | 12.12 | 4.09 | 12.94 | 5.00 | 7.42 | 2.35 |
| VOLUME_SURGE_BREAKOUT | kept | 50 | 68.07 | 24.68 | 8.60 | 5.94 | 13.86 | 4.95 | 8.05 | 2.71 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 21 | 63.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| BREAKDOWN_SHORT | kept | 7 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 337 | 58.57 | 0.00 | 0.00 | 0.00 | 0.00 | 1.03 | 0.00 | 0.00 | 0.00 | **1.03** |
| DIVERGENCE_CONTINUATION | kept | 84 | 67.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 658 | 56.59 | 0.00 | 0.00 | 0.53 | 0.00 | 3.02 | 0.00 | 0.00 | 0.00 | **3.55** |
| FAILED_AUCTION_RECLAIM | kept | 1454 | 71.13 | 0.00 | 0.00 | 0.00 | 0.00 | 0.13 | 0.00 | 0.00 | 0.00 | **0.13** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 853 | 56.41 | 0.94 | 0.00 | 0.76 | 0.00 | 6.73 | 0.00 | 0.00 | 0.00 | **8.43** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2079 | 68.83 | 0.01 | 0.00 | 0.05 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | **0.21** |
| SR_FLIP_RETEST | filtered | 1852 | 56.00 | 1.05 | 0.00 | 0.69 | 0.00 | 0.73 | 0.00 | 0.00 | 0.28 | **2.75** |
| SR_FLIP_RETEST | kept | 2342 | 71.77 | 0.05 | 0.00 | 0.09 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | **0.32** |
| VOLUME_SURGE_BREAKOUT | filtered | 102 | 59.68 | 0.00 | 0.00 | 0.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.71** |
| VOLUME_SURGE_BREAKOUT | kept | 50 | 68.07 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=178 (83.2%) | PREMATURE=20 (9.3%) | NEUTRAL=16 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 158 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 60 | 6 | 0 | 0 |
| ema_crossover | 4 | 0 | 1 | 0 |
| momentum_loss | 88 | 11 | 8 | 0 |
| trailing_invalidation | 26 | 3 | 7 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 1 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 22 | 2 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 24 | 0 | 5 | 0 |
| FUNDING_EXTREME_SIGNAL | 1 | 2 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 38 | 3 | 3 | 0 |
| SR_FLIP_RETEST | 77 | 12 | 6 | 0 |
| TREND_PULLBACK_EMA | 2 | 0 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 11 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 60 | 6 | 0 | 21.5 | 11.4 | +0.15 | **KEEP** — net-helping: avg +0.15R/kill across 66 kills (saved 21.5R vs missed 11.4R) |
| ema_crossover | 4 | 0 | 1 | 2.4 | 0.0 | +0.47 | **INSUFFICIENT_SAMPLE** — only 5 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 88 | 11 | 8 | 50.9 | 17.7 | +0.31 | **KEEP** — net-helping: avg +0.31R/kill across 107 kills (saved 50.9R vs missed 17.7R) |
| trailing_invalidation | 26 | 3 | 7 | 21.3 | 4.3 | +0.47 | **KEEP** — net-helping: avg +0.47R/kill across 36 kills (saved 21.3R vs missed 4.3R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4338987`
- `Path funnel` emissions: `149`
- `Regime distribution` emissions: `149`
- `QUIET_SCALP_BLOCK` events: `210`
- `confidence_gate` events: `9839`
- `free_channel_post` events: `40`
- `pre_tp_fire` events: `16`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **16**
- Avg resolved threshold: **0.427%** raw → avg net **+3.57%** @ 10x
- Avg time-to-fire from dispatch: **204s**
- By threshold source: stamped=16

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| FAILED_AUCTION_RECLAIM | 7 | 0.256% | +1.86% | 241 | stamped=7 |
| SR_FLIP_RETEST | 4 | 0.338% | +2.68% | 230 | stamped=4 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 0.823% | +7.53% | 136 | stamped=4 |
| DIVERGENCE_CONTINUATION | 1 | 0.395% | +3.25% | 115 | stamped=1 |
- Top symbols: OPUSDT=2, PLAYUSDT=2, OPGUSDT=2, ALLOUSDT=2, WLFIUSDT=2, CHIPUSDT=2, HMSTRUSDT=1, EPICUSDT=1, 1000PEPEUSDT=1, GWEIUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **40**

| Source | Count |
|---|---:|
| signal_close | 19 |
| pre_tp | 16 |
| regime_shift | 4 |
| signal_highlight | 1 |

- By severity: HIGH=40

## Dependency readiness
- cvd: presence[absent=6, present=868196] state[empty=6, populated=868196] buckets[few=84, many=867578, none=6, some=534] sources[none] quality[none]
- funding_rate: presence[absent=990, present=867212] state[empty=990, populated=867212] buckets[few=867212, none=990] sources[none] quality[none]
- liquidation_clusters: presence[absent=387363, present=480839] state[empty=387363, populated=480839] buckets[few=379121, none=387363, some=101718] sources[none] quality[none]
- oi_snapshot: presence[absent=990, present=867212] state[empty=990, populated=867212] buckets[few=316, many=865244, none=990, some=1652] sources[none] quality[none]
- order_book: presence[absent=227479, present=640723] state[populated=640723, unavailable=227479] buckets[few=640723, none=227479] sources[book_ticker=640723, unavailable=227479] quality[none=227479, top_of_book_only=640723]
- orderblocks: presence[absent=868202] state[empty=868202] buckets[none=868202] sources[not_implemented=868202] quality[none]
- recent_ticks: presence[absent=18760, present=849442] state[empty=18760, populated=849442] buckets[many=849442, none=18760] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.479691982269287` sec
- Median create→first breach: `440.91517198085785` sec
- Median create→terminal: `461.34105682373047` sec
- Median first breach→terminal: `0.9607044458389282` sec
- Fast-failure buckets: `{"under_120s": {"count": 5, "pct": 27.8}, "under_180s": {"count": 5, "pct": 27.8}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 5, "pct": 27.8}}`
- ~3 minute terminal-close behavior: `{"count": 2, "pct": 5.1}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 100.0 | 0.1974 | 241.86831498146057 | 242.84052801132202 |
| FAILED_AUCTION_RECLAIM | 13 | 13 | 0.0 | 0.0 | 0.0 | 53.8 | 0.0157 | 1075.253998041153 | 787.356663942337 |
| LIQUIDITY_SWEEP_REVERSAL | 9 | 9 | 0.0 | 22.2 | 0.0 | 44.4 | -0.1719 | 146.71193051338196 | 237.1335871219635 |
| SR_FLIP_RETEST | 13 | 13 | 0.0 | 7.7 | 0.0 | 30.8 | -0.2511 | 527.8808709383011 | 720.7482500076294 |
| VOLUME_SURGE_BREAKOUT | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0 | -0.3065 | None | 175.689954996109 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 30693 | 122 | 15110 | 0.0 | 7.7 | 527.8808709383011 | 720.7482500076294 | 15583 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 364 | 0 | 364 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `2`
- Gating Δ: `-3664`
- No-generation Δ: `-111189`
- Fast failures Δ: `-5`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.141, "current_avg_pnl": 0.1974, "current_win_rate": 0.0, "previous_avg_pnl": 0.0564, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -0.039, "current_avg_pnl": 0.0157, "current_win_rate": 0.0, "previous_avg_pnl": 0.0547, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0606, "current_avg_pnl": -0.1719, "current_win_rate": 0.0, "previous_avg_pnl": -0.2325, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.2168, "current_avg_pnl": -0.2511, "current_win_rate": 0.0, "previous_avg_pnl": -0.0343, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -0.253, "current_avg_pnl": -0.3065, "current_win_rate": 0.0, "previous_avg_pnl": -0.0535, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -24, "geometry_changed_delta": 0, "geometry_preserved_delta": -7074, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 110.43, "median_terminal_delta_sec": 79.65, "sl_rate_delta": 1.5, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **QUIET_COMPRESSION_BREAK**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
