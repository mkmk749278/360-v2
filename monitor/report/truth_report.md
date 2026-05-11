# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `6186` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 26748 | 26748 | 26748 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 368 | 368 | 367 | 1 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1890909 | 1890909 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1890909 | 1864161 | 26748 | 0 | 0 | 0 | low-sample (ema_alignment_reject) |
| EVAL::DIVERGENCE_CONTINUATION | 1890909 | 1890541 | 368 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1890909 | 1846425 | 44484 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1890909 | 1890909 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1890909 | 1890909 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1890909 | 1890909 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1890909 | 1890909 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1890909 | 1890909 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1890909 | 1873585 | 17324 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1890909 | 1769740 | 121169 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1890909 | 1845418 | 45491 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1890909 | 1890907 | 2 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1890909 | 1890909 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1890909 | 1890909 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 44484 | 44484 | 21303 | 51 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 45491 | 45491 | 19991 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 17324 | 17324 | 659 | 49 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 121169 | 121169 | 5114 | 13 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1890909): breakout_not_found=1189926, basic_filters_failed=527945, retest_proximity_failed=162751, ema_alignment_reject=10287
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1864161): ema_alignment_reject=424936, basic_filters_failed=417582, sweeps_not_detected=376685, regime_blocked=357304, rsi_reject=146586, adx_reject=80157, momentum_reject=60908, reclaim_confirmation_failed=3
- **EVAL::DIVERGENCE_CONTINUATION** (total=1890541): cvd_divergence_failed=861745, basic_filters_failed=417582, regime_blocked=357304, retest_proximity_failed=104753, missing_cvd=72350, cvd_insufficient=51961, ema_alignment_reject=24846
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1846425): auction_not_detected=851801, basic_filters_failed=527945, reclaim_hold_failed=320201, tail_too_small=146478
- **EVAL::FUNDING_EXTREME** (total=1890909): funding_not_extreme=1328389, basic_filters_failed=504312, missing_funding_rate=41943, rsi_reject=8207, ema_alignment_reject=8058
- **EVAL::LIQUIDATION_REVERSAL** (total=1890909): cascade_threshold_not_met=1323652, basic_filters_failed=527945, cvd_divergence_failed=33924, missing_cvd=5388
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1890909): no_ma_cross=1362964, basic_filters_failed=527945
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1890909): feature_disabled=1890909
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1890909): breakout_not_found=610930, ema_alignment_reject=424936, basic_filters_failed=417582, regime_blocked=357304, adx_reject=80157
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1873585): regime_blocked=1533605, compression_not_detected=125660, basic_filters_failed=110363, breakout_not_detected=81481, macd_reject=22476
- **EVAL::SR_FLIP_RETEST** (total=1769740): basic_filters_failed=527945, flip_close_not_confirmed=418379, retest_out_of_zone=405142, reclaim_hold_failed=252241, wick_quality_failed=103924, rsi_reject=61379, missing_fvg_or_orderblock=655, ema_alignment_reject=75
- **EVAL::STANDARD** (total=1845418): momentum_reject=813211, basic_filters_failed=372993, adx_reject=216965, sweeps_not_detected=194042, ema_alignment_reject=141582, rsi_reject=61441, macd_reject=45184
- **EVAL::TREND_PULLBACK** (total=1890907): ema_not_tested_prev=530948, ema_alignment_reject=424936, basic_filters_failed=417582, regime_blocked=357304, body_conviction_fail=63633, rsi_reject=38461, no_ema_reclaim_close=31133, no_prev_high_break=26909, prev_already_above_emas=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1890909): breakout_not_found=998371, basic_filters_failed=527945, retest_proximity_failed=315318, rsi_reject=29907, volume_spike_missing=19368
- **EVAL::WHALE_MOMENTUM** (total=1890909): momentum_reject=1889403, recent_ticks_insufficient=1506

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1513200 | 68.7% |
| QUIET | 400435 | 18.2% |
| TRENDING_DOWN | 289610 | 13.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **820**
- Average confidence gap to threshold: **1.70** (samples=820) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ZECUSDT=801, DOGEUSDT=19

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 1 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 3918 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 753 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 18230 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 48 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 97 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 16744 |
| SR_FLIP_RETEST | filtered | min_confidence | 29691 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 19 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 307 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 1 | 67.00 | 65.00 | -2.00 | 24.20 | 18.80 | 18.80 | 5.00 | -3.00 |
| FAILED_AUCTION_RECLAIM | filtered | 4671 | 52.04 | 65.00 | 12.96 | 20.49 | 17.70 | 14.00 | 5.84 | 3.67 |
| FAILED_AUCTION_RECLAIM | kept | 18230 | 70.82 | 65.00 | -5.82 | 21.60 | 20.00 | 14.00 | 5.13 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 43.47 | 65.00 | 21.53 | 23.51 | 19.50 | 15.20 | 1.65 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 97 | 68.00 | 65.00 | -3.00 | 23.40 | 20.00 | 15.20 | 0.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 16744 | 66.71 | 65.00 | -1.71 | 19.94 | 19.99 | 15.80 | 0.00 | -0.02 |
| SR_FLIP_RETEST | filtered | 29710 | 50.49 | 65.00 | 14.51 | 19.95 | 20.00 | 15.20 | 2.56 | 5.20 |
| SR_FLIP_RETEST | kept | 307 | 65.80 | 65.00 | -0.80 | 19.65 | 20.00 | 15.21 | 2.00 | -2.95 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 1 | 67.00 | 17.00 | 18.00 | 3.00 | 13.00 | 5.00 | 6.00 | 5.00 |
| FAILED_AUCTION_RECLAIM | filtered | 4671 | 52.04 | 24.68 | 14.00 | 3.00 | 9.00 | 5.56 | 6.21 | 5.84 |
| FAILED_AUCTION_RECLAIM | kept | 18230 | 70.82 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 6.70 | 5.13 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 43.47 | 22.17 | 14.00 | 6.00 | 13.29 | 6.24 | 6.11 | 1.65 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 97 | 68.00 | 25.00 | 14.00 | 3.00 | 14.00 | 5.00 | 7.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 16744 | 66.71 | 17.00 | 18.00 | 3.02 | 14.00 | 9.99 | 4.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 29710 | 50.49 | 23.14 | 17.99 | 3.00 | 16.58 | 5.00 | 2.42 | 2.56 |
| SR_FLIP_RETEST | kept | 307 | 65.80 | 17.05 | 18.00 | 3.00 | 14.02 | 5.01 | 6.73 | 2.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | kept | 1 | 67.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 4671 | 52.04 | 0.00 | 0.00 | 2.86 | 0.00 | 0.00 | 0.00 | **2.86** |
| FAILED_AUCTION_RECLAIM | kept | 18230 | 70.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 48 | 43.47 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 97 | 68.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 16744 | 66.71 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 29710 | 50.49 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 307 | 65.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=20 (38.5%) | PREMATURE=2 (3.8%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 18 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| ema_crossover | 6 | 1 | 28 | 0 |
| other | 5 | 0 | 1 | 0 |
| regime_shift | 9 | 1 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 6 | 0 | 27 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 1 | 0 | 0 | 0 |
| SR_FLIP_RETEST | 12 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `11187766`
- `Path funnel` emissions: `295`
- `Regime distribution` emissions: `295`
- `QUIET_SCALP_BLOCK` events: `820`
- `confidence_gate` events: `69808`
- `free_channel_post` events: `7`
- `pre_tp_fire` events: `1`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **1**
- Avg resolved threshold: **0.200%** raw → avg net **+1.30%** @ 10x
- Avg time-to-fire from dispatch: **964s**
- By threshold source: stamped=1

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| FAILED_AUCTION_RECLAIM | 1 | 0.200% | +1.30% | 964 | stamped=1 |
- Top symbols: DOGEUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **191**
- Total REST-fallback activations: **90**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 179 | 2517 | 4114 | 5275 | 0 |
| futures_liq | 12 | 1927 | 2682 | 2779 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 90 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **7**

| Source | Count |
|---|---:|
| regime_shift | 6 |
| pre_tp | 1 |

- By severity: HIGH=7

## Dependency readiness
- cvd: presence[absent=120800, present=1770109] state[empty=120800, populated=1770109] buckets[many=1599735, none=120800, some=170374] sources[none] quality[none]
- funding_rate: presence[absent=41943, present=1848966] state[empty=41943, populated=1848966] buckets[few=1848966, none=41943] sources[none] quality[none]
- liquidation_clusters: presence[absent=1890909] state[empty=1890909] buckets[none=1890909] sources[none] quality[none]
- oi_snapshot: presence[absent=38316, present=1852593] state[empty=38316, populated=1852593] buckets[few=502, many=1850606, none=38316, some=1485] sources[none] quality[none]
- order_book: presence[absent=94664, present=1796245] state[populated=1796245, unavailable=94664] buckets[few=1796245, none=94664] sources[book_ticker=1796245, unavailable=94664] quality[none=94664, top_of_book_only=1796245]
- orderblocks: presence[absent=1890909] state[empty=1890909] buckets[none=1890909] sources[not_implemented=1890909] quality[none]
- recent_ticks: presence[absent=141140, present=1749769] state[empty=141140, populated=1749769] buckets[many=1749769, none=141140] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.2424428462982178` sec
- Median create→first breach: `None` sec
- Median create→terminal: `656.3956081867218` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.3496 | None | None |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1774 | None | None |
| SR_FLIP_RETEST | 11 | 11 | 0.0 | 0.0 | 0.0 | -0.0904 | None | 656.3956081867218 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 121169 | 13 | 5114 | 0.0 | 0.0 | None | 656.3956081867218 | 116055 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2 | 0 | 2 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `8`
- Gating Δ: `22764`
- No-generation Δ: `-1116260`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.1572, "current_avg_pnl": -0.0904, "current_win_rate": 0.0, "previous_avg_pnl": 0.0668, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -3, "geometry_changed_delta": 0, "geometry_preserved_delta": 45328, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -2886.15, "median_terminal_delta_sec": -1652.37, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **CONTINUATION_LIQUIDITY_SWEEP**
- Suggested next investigation target: **SR_FLIP_RETEST**
