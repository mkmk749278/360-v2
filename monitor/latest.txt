# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, EVAL::LIQUIDATION_REVERSAL, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=starting)
- Heartbeat age: `900` sec (warning=True)
- Latest performance record age: `48806` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 31 | 31 | 7 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2824 | 2824 | 2682 | 5 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 12104 | 12104 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 10868 | 10869 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 10849 | 10182 | 686 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 10870 | 10485 | 398 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 12522 | 12492 | 32 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 10499 | 10500 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 10883 | 10884 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 13024 | 13963 | 118 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 12109 | 11250 | 1774 | 0 | 0 | 0 | low-sample (no_reclaim) |
| EVAL::OPENING_RANGE_BREAKOUT | 12380 | 12380 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 10869 | 10869 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 10849 | 10849 | 0 | 0 | 0 | 0 | non-generating (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 10704 | 10492 | 354 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 8889 | 8347 | 581 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 8928 | 8867 | 65 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 12101 | 12104 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 10500 | 10473 | 31 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 1870 | 1870 | 1165 | 13 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 62 | 62 | 62 | 0 | low-sample (none) |
| LIQUIDATION_REVERSAL | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 3305 | 3305 | 3210 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 250 | 250 | 246 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 3365 | 3365 | 3201 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1632 | 1632 | 710 | 2 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 431 | 431 | 413 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 7 | 7 | 0 | 2 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 744 | 744 | 744 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=12104): breakout_not_found=6351, basic_filters_failed=3238, move_not_fresh=1546, breakout_stale=655, retest_proximity_failed=298, volume_spike_missing=12, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=10869): cls_disabled_merged_into_lsr=10869
- **EVAL::DIVERGENCE_CONTINUATION** (total=10182): cvd_divergence_failed=3885, basic_filters_failed=2535, h1_trend_not_aligned=2122, ema_alignment_reject=1476, retest_proximity_failed=64, missing_fvg_or_orderblock=61, regime_blocked=39
- **EVAL::FAILED_AUCTION_RECLAIM** (total=10485): auction_not_detected=4423, basic_filters_failed=2519, reclaim_hold_failed=1750, tail_too_small=1515, regime_blocked=278
- **EVAL::FUNDING_EXTREME** (total=12492): funding_not_extreme=9314, basic_filters_failed=2836, missing_funding_rate=194, ema_alignment_reject=103, rsi_reject=27, cvd_divergence_failed=15, momentum_reject=3
- **EVAL::LIQUIDATION_REVERSAL** (total=10500): cascade_threshold_not_met=7567, basic_filters_failed=2891, cvd_divergence_failed=32, rsi_reject=10
- **EVAL::MA_CROSS_TREND_SHIFT** (total=10884): no_ma_cross=8076, basic_filters_failed=2535, ma_cross_cooldown=256, ma_cross_htf_misaligned=17
- **EVAL::MOVER_AVWAP_SCALP** (total=13963): no_avwap_tag=7161, basic_filters_failed=3172, no_mover_leg=1610, avwap_slope_against=1179, insufficient_candles=736, avwap_reclaim_no_volume=68, no_avwap_reclaim=19, anchor_too_recent=18
- **EVAL::MOVER_TREND_PULLBACK** (total=11250): no_reclaim=3627, basic_filters_failed=3170, mover_run_too_small=2219, no_pullback_tag=1498, insufficient_candles=736
- **EVAL::OPENING_RANGE_BREAKOUT** (total=12380): feature_disabled=12380
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=10869): regime_blocked=8721, breakout_not_found=1176, basic_filters_failed=761, adx_reject=208, ema_alignment_reject=3
- **EVAL::QUIET_COMPRESSION_BREAK** (total=10849): compression_not_detected=6489, regime_blocked=2423, basic_filters_failed=1758, breakout_not_detected=174, volume_confirmation_failed=5
- **EVAL::SR_FLIP_RETEST** (total=10492): basic_filters_failed=2518, flip_close_not_confirmed=2010, long_break_volume_thin=1696, whipsaw_flip=1431, reclaim_hold_failed=1310, long_disabled=520, retest_out_of_zone=499, regime_blocked=277, wick_quality_failed=133, long_acceptance_not_held=30, missing_fvg_or_orderblock=25, rsi_reject=24, ema_alignment_reject=19
- **EVAL::STANDARD** (total=8347): momentum_reject=2821, adx_reject=2428, macd_reject=923, basic_filters_failed=916, sweeps_not_detected=898, ema_alignment_reject=290, invalid_sl_geometry=67, rsi_reject=4
- **EVAL::TREND_PULLBACK** (total=8867): h1_trend_not_aligned=2173, h1_pullback_not_confirmed=1718, basic_filters_failed=1492, ema_alignment_reject=1403, body_conviction_fail=472, no_ema_reclaim_close=445, ema_not_tested_prev=411, rsi_reject=252, prev_already_above_emas=235, regime_blocked=83, no_prev_high_break=71, prev_already_below_emas=55, no_prev_low_break=26, momentum_flat=17, momentum_reject=12, missing_fvg_or_orderblock=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=12104): breakout_not_found=7422, basic_filters_failed=3238, move_not_fresh=797, breakout_stale=590, retest_proximity_failed=40, missing_fvg_or_orderblock=10, volume_spike_missing=7
- **EVAL::WHALE_MOMENTUM** (total=10473): momentum_reject=7856, recent_ticks_insufficient=1851, basic_filters_failed=766

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 25337 | 38.4% |
| QUIET | 25203 | 38.2% |
| TRENDING_DOWN | 7376 | 11.2% |
| TRENDING_UP | 5861 | 8.9% |
| VOLATILE | 2183 | 3.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **48**
- Average confidence gap to threshold: **12.49** (samples=48) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: DOGEUSDT=11, NBISUSDT=8, AMDUSDT=6, BCHUSDT=6, BTCUSDT=5, AVAXUSDT=4, ETHUSDT=3, SUIUSDT=3, ADAUSDT=2

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 19 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 12 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 26 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 50 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 37 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 238 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 22 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 13 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 4 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 164 |
| SR_FLIP_RETEST | filtered | min_confidence | 114 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 7 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 25 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 7 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 19 | 63.00 | 65.00 | 2.00 | 17.08 | 16.30 | 20.00 | 6.00 | 20.00 |
| DIVERGENCE_CONTINUATION | filtered | 15 | 55.29 | 65.00 | 9.71 | 21.33 | 20.00 | 18.22 | 1.00 | 11.27 |
| DIVERGENCE_CONTINUATION | kept | 26 | 69.62 | 65.00 | -4.62 | 22.25 | 19.98 | 19.24 | 3.62 | -1.34 |
| FAILED_AUCTION_RECLAIM | filtered | 87 | 56.98 | 65.00 | 8.02 | 20.73 | 19.90 | 20.00 | 4.72 | 14.10 |
| FAILED_AUCTION_RECLAIM | kept | 238 | 68.58 | 65.00 | -3.58 | 20.57 | 19.96 | 20.00 | 3.89 | 0.16 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 23 | 59.71 | 65.00 | 5.29 | 18.64 | 17.42 | 17.00 | 0.35 | 12.42 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 67.35 | 65.00 | -2.35 | 20.22 | 20.00 | 17.23 | 2.77 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 4 | 54.20 | 65.00 | 10.80 | 19.60 | 17.80 | 15.80 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 164 | 76.86 | 65.00 | -11.86 | 19.83 | 19.25 | 15.80 | 4.51 | 0.12 |
| SR_FLIP_RETEST | filtered | 121 | 58.54 | 65.00 | 6.46 | 20.18 | 20.00 | 15.68 | 2.04 | 14.70 |
| SR_FLIP_RETEST | kept | 25 | 76.58 | 65.00 | -11.58 | 21.15 | 20.00 | 15.39 | 2.56 | -1.54 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 77.61 | 65.00 | -12.61 | 20.60 | 18.66 | 20.00 | 4.00 | 2.57 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 19 | 63.00 | 25.00 | 18.00 | 12.00 | 11.00 | 5.00 | 6.00 | 6.00 |
| DIVERGENCE_CONTINUATION | filtered | 15 | 55.29 | 17.00 | 12.00 | 4.80 | 14.33 | 7.70 | 9.72 | 1.00 |
| DIVERGENCE_CONTINUATION | kept | 26 | 69.62 | 22.85 | 11.85 | 5.65 | 11.65 | 5.10 | 9.19 | 3.62 |
| FAILED_AUCTION_RECLAIM | filtered | 87 | 56.98 | 23.90 | 16.30 | 5.34 | 10.79 | 6.06 | 3.96 | 4.72 |
| FAILED_AUCTION_RECLAIM | kept | 238 | 68.58 | 21.97 | 14.54 | 3.48 | 12.56 | 6.35 | 5.96 | 3.89 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 23 | 59.71 | 24.65 | 14.00 | 9.00 | 14.00 | 5.00 | 5.13 | 0.35 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 67.35 | 25.00 | 14.00 | 6.00 | 11.92 | 5.27 | 2.38 | 2.77 |
| MOVER_AVWAP_SCALP | filtered | 4 | 54.20 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 4.70 | 3.00 |
| MOVER_TREND_PULLBACK | kept | 164 | 76.86 | 19.59 | 18.00 | 7.77 | 12.63 | 5.59 | 8.89 | 4.51 |
| SR_FLIP_RETEST | filtered | 121 | 58.54 | 21.56 | 17.42 | 6.82 | 11.97 | 7.63 | 5.81 | 2.04 |
| SR_FLIP_RETEST | kept | 25 | 76.58 | 22.76 | 16.80 | 8.16 | 14.24 | 5.84 | 7.08 | 2.56 |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 77.61 | 17.00 | 14.00 | 14.14 | 16.14 | 5.00 | 9.90 | 4.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 19 | 63.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 15 | 55.29 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 26 | 69.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | **0.28** |
| FAILED_AUCTION_RECLAIM | filtered | 87 | 56.98 | 0.00 | 0.00 | 0.00 | 0.00 | 5.46 | 0.00 | 0.00 | 0.00 | **5.46** |
| FAILED_AUCTION_RECLAIM | kept | 238 | 68.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 23 | 59.71 | 0.00 | 0.00 | 0.00 | 0.00 | 12.42 | 0.00 | 0.00 | 0.00 | **12.42** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 13 | 67.35 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 4 | 54.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 164 | 76.86 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 121 | 58.54 | 0.00 | 0.00 | 0.00 | 0.00 | 2.98 | 0.00 | 0.00 | 0.10 | **3.08** |
| SR_FLIP_RETEST | kept | 25 | 76.58 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.48 | **0.48** |
| VOLUME_SURGE_BREAKOUT | kept | 7 | 77.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=41 (69.5%) | PREMATURE=10 (16.9%) | NEUTRAL=8 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 31 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 41 | 10 | 8 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 3 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 9 | 4 | 6 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 1 | 0 | 0 |
| MOVER_AVWAP_SCALP | 9 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 16 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 6 | 2 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 41 | 10 | 8 | 32.7 | 11.2 | +0.36 | **KEEP** — net-helping: avg +0.36R/kill across 59 kills (saved 32.7R vs missed 11.2R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `18406`
- `Path funnel` emissions: `8`
- `Regime distribution` emissions: `8`
- `QUIET_SCALP_BLOCK` events: `48`
- `confidence_gate` events: `742`
- `free_channel_post` events: `2`
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
- Total posts in window: **2**

| Source | Count |
|---|---:|
| regime_shift | 2 |

- By severity: HIGH=2

## Dependency readiness
- cvd: presence[present=51874] state[populated=51874] buckets[many=51874] sources[none] quality[none]
- funding_rate: presence[absent=3846, present=48028] state[empty=3846, populated=48028] buckets[few=48028, none=3846] sources[none] quality[none]
- liquidation_clusters: presence[absent=35965, present=15909] state[empty=35965, populated=15909] buckets[few=12316, none=35965, some=3593] sources[none] quality[none]
- oi_snapshot: presence[absent=3305, present=48569] state[empty=3305, populated=48569] buckets[many=48569, none=3305] sources[none] quality[none]
- order_book: presence[absent=13532, present=38342] state[populated=38342, unavailable=13532] buckets[few=38342, none=13532] sources[book_ticker=38342, unavailable=13532] quality[none=13532, top_of_book_only=38342]
- orderblocks: presence[absent=51874] state[empty=51874] buckets[none=51874] sources[not_implemented=51874] quality[none]
- recent_ticks: presence[absent=762, present=51112] state[empty=762, populated=51112] buckets[many=51112, none=762] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.3880789279937744` sec
- Median create→first breach: `2257.5094151496887` sec
- Median create→terminal: `2259.2421910762787` sec
- Median first breach→terminal: `2.946665048599243` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 4 | 4 | 25.0 | 75.0 | 25.0 | 0.0 | -0.5752 | 3131.808941960335 | 3136.2042734622955 |
| MOVER_TREND_PULLBACK | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 0.4182 | 6911.479415655136 | 6917.781600594521 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 2.9017 | 854.0935089588165 | 856.3273849487305 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 1632 | 2 | 710 | 0.0 | 0.0 | None | None | 922 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 431 | 0 | 413 | 0.0 | 0.0 | None | None | 18 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `25`
- Gating Δ: `12441`
- No-generation Δ: `187110`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.3696, "current_avg_pnl": -0.5752, "current_win_rate": 25.0, "previous_avg_pnl": -0.9448, "previous_win_rate": 20.0, "win_rate_delta": 5.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 2, "geometry_changed_delta": 0, "geometry_preserved_delta": 922, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 18, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
