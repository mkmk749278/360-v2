# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: DIVERGENCE_CONTINUATION, CONTINUATION_LIQUIDITY_SWEEP, SR_FLIP_RETEST
- Top promising signals/paths: none
- Recommended next investigation target: **DIVERGENCE_CONTINUATION**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `4094` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 638 | 638 | 638 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 70811 | 70811 | 31981 | 2 | active-low-quality (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 136803 | 136803 | 102859 | 6 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 1612873 | 1612235 | 638 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1408369 | 1337558 | 70811 | 0 | 0 | 0 | low-sample (sweeps_not_detected) |
| EVAL::DIVERGENCE_CONTINUATION | 1408369 | 1271566 | 136803 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1408369 | 1310318 | 98051 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1612873 | 1587976 | 24897 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1612873 | 1612873 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1408369 | 1408367 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1612873 | 1612873 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1408369 | 1408369 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1408369 | 1408369 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1408369 | 1265906 | 142463 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1408369 | 1392489 | 15880 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1408369 | 1408367 | 2 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1612873 | 1612014 | 859 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1612873 | 1612873 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 98051 | 98051 | 73292 | 3 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 24897 | 24897 | 12744 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 15880 | 15880 | 1628 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 142463 | 142463 | 21639 | 20 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 859 | 859 | 60 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1612235): breakout_not_found=867987, basic_filters_failed=469740, retest_proximity_failed=231711, ema_alignment_reject=16687, missing_fvg_or_orderblock=15576, volume_spike_missing=10534
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1337558): sweeps_not_detected=425589, basic_filters_failed=351958, ema_alignment_reject=329361, regime_blocked=136716, adx_reject=29848, momentum_reject=28442, rsi_reject=24893, reclaim_confirmation_failed=10751
- **EVAL::DIVERGENCE_CONTINUATION** (total=1271566): cvd_divergence_failed=593941, basic_filters_failed=351958, regime_blocked=136716, ema_alignment_reject=95967, retest_proximity_failed=47777, missing_cvd=30330, cvd_insufficient=13852, missing_fvg_or_orderblock=1025
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1310318): auction_not_detected=511807, basic_filters_failed=401899, reclaim_hold_failed=285560, tail_too_small=111052
- **EVAL::FUNDING_EXTREME** (total=1587976): funding_not_extreme=1067168, basic_filters_failed=453406, missing_funding_rate=42375, rsi_reject=19404, ema_alignment_reject=4504, momentum_reject=1119
- **EVAL::LIQUIDATION_REVERSAL** (total=1612873): cascade_threshold_not_met=1122871, basic_filters_failed=469740, cvd_divergence_failed=20262
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1408367): no_ma_cross=1002143, basic_filters_failed=401899, ma_cross_cooldown=4325
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1612873): feature_disabled=1612873
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1408369): breakout_not_found=560486, basic_filters_failed=351958, ema_alignment_reject=329361, regime_blocked=136716, adx_reject=29848
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1408369): regime_blocked=1271653, basic_filters_failed=49941, compression_not_detected=44292, breakout_not_detected=30102, missing_fvg_or_orderblock=7200, macd_reject=5181
- **EVAL::SR_FLIP_RETEST** (total=1265906): basic_filters_failed=401899, retest_out_of_zone=340925, flip_close_not_confirmed=294596, reclaim_hold_failed=135650, rsi_reject=32473, ema_alignment_reject=31680, wick_quality_failed=28683
- **EVAL::STANDARD** (total=1392489): momentum_reject=564754, basic_filters_failed=305515, ema_alignment_reject=194861, sweeps_not_detected=161867, adx_reject=130903, rsi_reject=20171, macd_reject=14418
- **EVAL::TREND_PULLBACK** (total=1408367): ema_not_tested_prev=382592, basic_filters_failed=351958, ema_alignment_reject=348950, regime_blocked=136716, no_ema_reclaim_close=129462, rsi_reject=41000, body_conviction_fail=15357, prev_already_above_emas=1702, no_prev_high_break=628, prev_already_below_emas=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1612014): breakout_not_found=674071, basic_filters_failed=469740, retest_proximity_failed=373676, volume_spike_missing=85170, ema_alignment_reject=9357
- **EVAL::WHALE_MOMENTUM** (total=1612873): momentum_reject=1014789, recent_ticks_insufficient=463818, basic_filters_failed=134266

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1303525 | 70.8% |
| TRENDING_DOWN | 349108 | 18.9% |
| QUIET | 189791 | 10.3% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **196**
- Average confidence gap to threshold: **15.39** (samples=196) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SKYAIUSDT=196

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 14826 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 15125 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 903 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 32445 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 24 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 563 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 196 |
| SR_FLIP_RETEST | filtered | min_confidence | 1378 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 22936 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 14826 | 63.38 | 65.00 | 1.62 | 18.08 | 19.93 | 19.47 | 1.65 | 5.86 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 15125 | 69.20 | 65.00 | -4.20 | 19.44 | 19.74 | 18.06 | 0.89 | 4.36 |
| DIVERGENCE_CONTINUATION | filtered | 903 | 62.47 | 65.00 | 2.53 | 20.93 | 20.00 | 17.27 | 5.00 | 4.80 |
| DIVERGENCE_CONTINUATION | kept | 32445 | 67.11 | 65.00 | -2.11 | 19.40 | 20.00 | 19.27 | 5.18 | 1.93 |
| FAILED_AUCTION_RECLAIM | filtered | 24 | 61.54 | 65.00 | 3.46 | 20.50 | 20.00 | 14.00 | 5.04 | 4.80 |
| FAILED_AUCTION_RECLAIM | kept | 563 | 68.03 | 65.00 | -3.03 | 21.79 | 20.00 | 14.00 | 4.09 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 196 | 49.61 | 65.00 | 15.39 | 20.41 | 20.00 | 15.20 | 3.01 | 21.60 |
| SR_FLIP_RETEST | filtered | 1378 | 54.36 | 65.00 | 10.64 | 20.28 | 19.83 | 15.59 | 1.93 | 7.04 |
| SR_FLIP_RETEST | kept | 22936 | 71.15 | 65.00 | -6.15 | 23.44 | 20.00 | 15.21 | 2.38 | 3.03 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 14826 | 63.38 | 18.41 | 18.00 | 3.00 | 13.47 | 5.62 | 9.09 | 1.65 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 15125 | 69.20 | 23.38 | 18.00 | 3.00 | 12.06 | 6.89 | 9.37 | 0.89 |
| DIVERGENCE_CONTINUATION | filtered | 903 | 62.47 | 17.00 | 18.00 | 3.00 | 14.00 | 4.86 | 5.42 | 5.00 |
| DIVERGENCE_CONTINUATION | kept | 32445 | 67.11 | 17.00 | 18.00 | 3.00 | 14.00 | 4.31 | 7.55 | 5.18 |
| FAILED_AUCTION_RECLAIM | filtered | 24 | 61.54 | 25.00 | 14.00 | 3.00 | 8.00 | 5.00 | 6.30 | 5.04 |
| FAILED_AUCTION_RECLAIM | kept | 563 | 68.03 | 19.94 | 14.00 | 3.00 | 11.20 | 9.01 | 6.79 | 4.09 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 196 | 49.61 | 25.00 | 14.00 | 6.00 | 12.00 | 2.50 | 8.70 | 3.01 |
| SR_FLIP_RETEST | filtered | 1378 | 54.36 | 20.56 | 18.00 | 3.00 | 14.77 | 5.00 | 5.94 | 1.93 |
| SR_FLIP_RETEST | kept | 22936 | 71.15 | 23.43 | 18.00 | 3.62 | 11.58 | 5.84 | 9.80 | 2.38 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 14826 | 63.38 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.80** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 15125 | 69.20 | 0.00 | 0.00 | 0.92 | 0.00 | 0.00 | 0.00 | **0.92** |
| DIVERGENCE_CONTINUATION | filtered | 903 | 62.47 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.80** |
| DIVERGENCE_CONTINUATION | kept | 32445 | 67.11 | 0.00 | 0.00 | 1.93 | 0.00 | 0.00 | 0.00 | **1.93** |
| FAILED_AUCTION_RECLAIM | filtered | 24 | 61.54 | 0.00 | 0.00 | 4.80 | 0.00 | 0.00 | 0.00 | **4.80** |
| FAILED_AUCTION_RECLAIM | kept | 563 | 68.03 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 196 | 49.61 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | **21.60** |
| SR_FLIP_RETEST | filtered | 1378 | 54.36 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | **0.26** |
| SR_FLIP_RETEST | kept | 22936 | 71.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=9 (90.0%) | PREMATURE=1 (10.0%) | NEUTRAL=0 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 8 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| other | 3 | 1 | 0 | 0 |
| regime_shift | 6 | 0 | 0 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 0 | 0 | 0 |
| DIVERGENCE_CONTINUATION | 1 | 0 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 3 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 3 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `10762928`
- `Path funnel` emissions: `249`
- `Regime distribution` emissions: `249`
- `QUIET_SCALP_BLOCK` events: `196`
- `confidence_gate` events: `88396`
- `free_channel_post` events: `1`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **166**
- Total REST-fallback activations: **78**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 156 | 2592 | 4248 | 6853 | 0 |
| futures_liq | 10 | 2083 | 2841 | 2954 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 78 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **1**

| Source | Count |
|---|---:|
| regime_shift | 1 |

- By severity: HIGH=1

## Dependency readiness
- cvd: presence[absent=56494, present=1556379] state[empty=56494, populated=1556379] buckets[many=1449122, none=56494, some=107257] sources[none] quality[none]
- funding_rate: presence[absent=42375, present=1570498] state[empty=42375, populated=1570498] buckets[few=1570498, none=42375] sources[none] quality[none]
- liquidation_clusters: presence[absent=1612873] state[empty=1612873] buckets[none=1612873] sources[none] quality[none]
- oi_snapshot: presence[absent=38924, present=1573949] state[empty=38924, populated=1573949] buckets[few=605, many=1570069, none=38924, some=3275] sources[none] quality[none]
- order_book: presence[absent=60149, present=1552724] state[populated=1552724, unavailable=60149] buckets[few=1552724, none=60149] sources[book_ticker=1552724, unavailable=60149] quality[none=60149, top_of_book_only=1552724]
- orderblocks: presence[absent=1612873] state[empty=1612873] buckets[none=1612873] sources[not_implemented=1612873] quality[none]
- recent_ticks: presence[absent=32325, present=1580548] state[empty=32325, populated=1580548] buckets[many=1580548, none=32325] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.2961679697036743` sec
- Median create→first breach: `None` sec
- Median create→terminal: `3217.2673984766006` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 3 | 3 | 0.0 | 0.0 | 0.0 | -0.0058 | None | 2832.8378698825836 |
| DIVERGENCE_CONTINUATION | 6 | 6 | 0.0 | 0.0 | 0.0 | 0.0803 | None | 3601.7528940439224 |
| SR_FLIP_RETEST | 12 | 12 | 0.0 | 0.0 | 0.0 | 0.0413 | None | 604.9274289608002 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 142463 | 20 | 21639 | 0.0 | 0.0 | None | 604.9274289608002 | 120824 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2 | 0 | 2 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-4`
- Gating Δ: `184064`
- No-generation Δ: `-4255456`
- Fast failures Δ: `0`
- Quality changes: `{"CONTINUATION_LIQUIDITY_SWEEP": {"avg_pnl_delta": -0.0058, "current_avg_pnl": -0.0058, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.0803, "current_avg_pnl": 0.0803, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.1844, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.1844, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1801, "current_avg_pnl": 0.0413, "current_win_rate": 0.0, "previous_avg_pnl": -0.1388, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": -41938, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -2133.88, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **DIVERGENCE_CONTINUATION**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **DIVERGENCE_CONTINUATION**
