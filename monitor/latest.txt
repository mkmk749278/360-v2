# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `3238` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 26933 | 26933 | 26933 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 969 | 969 | 969 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1881334 | 1881334 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1881334 | 1854401 | 26933 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::DIVERGENCE_CONTINUATION | 1881334 | 1880365 | 969 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1881334 | 1824358 | 56976 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1881334 | 1881334 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1881334 | 1881334 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1881334 | 1881334 | 0 | 0 | 0 | 0 | non-generating (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1881334 | 1881334 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1881334 | 1881334 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1881334 | 1864821 | 16513 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1881334 | 1773601 | 107733 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1881334 | 1837447 | 43887 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1881334 | 1881332 | 2 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1881334 | 1881334 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1881334 | 1881334 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 56976 | 56976 | 33307 | 54 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 43887 | 43887 | 30050 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 16513 | 16513 | 39 | 48 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 107733 | 107733 | 6484 | 16 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1881334): breakout_not_found=1161220, basic_filters_failed=576683, retest_proximity_failed=131639, ema_alignment_reject=11792
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1854401): basic_filters_failed=445760, ema_alignment_reject=403649, regime_blocked=366270, sweeps_not_detected=340218, rsi_reject=173255, adx_reject=71631, momentum_reject=53616, reclaim_confirmation_failed=2
- **EVAL::DIVERGENCE_CONTINUATION** (total=1880365): cvd_divergence_failed=829749, basic_filters_failed=445760, regime_blocked=366270, retest_proximity_failed=106660, missing_cvd=60077, cvd_insufficient=52499, ema_alignment_reject=19350
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1824358): auction_not_detected=756018, basic_filters_failed=576683, reclaim_hold_failed=338916, tail_too_small=152741
- **EVAL::FUNDING_EXTREME** (total=1881334): funding_not_extreme=1289394, basic_filters_failed=575298, rsi_reject=9399, missing_funding_rate=4587, momentum_reject=1541, ema_alignment_reject=1115
- **EVAL::LIQUIDATION_REVERSAL** (total=1881334): cascade_threshold_not_met=1266840, basic_filters_failed=576683, cvd_divergence_failed=35353, missing_cvd=2263, rsi_reject=195
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1881334): no_ma_cross=1304651, basic_filters_failed=576683
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1881334): feature_disabled=1881334
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1881334): breakout_not_found=594024, basic_filters_failed=445760, ema_alignment_reject=403649, regime_blocked=366270, adx_reject=71631
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1864821): regime_blocked=1515064, basic_filters_failed=130923, compression_not_detected=105690, breakout_not_detected=87075, macd_reject=25709, rsi_reject=360
- **EVAL::SR_FLIP_RETEST** (total=1773601): basic_filters_failed=576683, flip_close_not_confirmed=412745, retest_out_of_zone=338057, reclaim_hold_failed=263754, wick_quality_failed=119810, rsi_reject=62146, missing_fvg_or_orderblock=331, ema_alignment_reject=75
- **EVAL::STANDARD** (total=1837447): momentum_reject=830775, basic_filters_failed=400302, adx_reject=212086, sweeps_not_detected=148638, ema_alignment_reject=130438, rsi_reject=65935, macd_reject=49273
- **EVAL::TREND_PULLBACK** (total=1881332): ema_not_tested_prev=525391, basic_filters_failed=445760, ema_alignment_reject=403649, regime_blocked=366270, body_conviction_fail=55258, rsi_reject=35069, no_ema_reclaim_close=28089, no_prev_high_break=21844, prev_already_above_emas=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1881334): breakout_not_found=921438, basic_filters_failed=576683, retest_proximity_failed=332824, rsi_reject=30164, volume_spike_missing=20225
- **EVAL::WHALE_MOMENTUM** (total=1881334): momentum_reject=1879836, recent_ticks_insufficient=1498

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1568400 | 70.2% |
| QUIET | 431791 | 19.3% |
| TRENDING_DOWN | 233737 | 10.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **1392**
- Average confidence gap to threshold: **0.35** (samples=1392) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ZECUSDT=1373, DOGEUSDT=19

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 2130 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 1373 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 19364 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 16564 |
| SR_FLIP_RETEST | filtered | min_confidence | 21766 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 19 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 595 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3503 | 55.95 | 65.00 | 9.05 | 21.49 | 17.84 | 14.00 | 5.61 | 3.65 |
| FAILED_AUCTION_RECLAIM | kept | 19364 | 70.75 | 65.00 | -5.75 | 21.27 | 20.00 | 14.00 | 5.05 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 16564 | 66.70 | 65.00 | -1.70 | 19.89 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 21785 | 50.44 | 65.00 | 14.56 | 19.78 | 20.00 | 15.20 | 2.53 | 5.22 |
| SR_FLIP_RETEST | kept | 595 | 66.21 | 65.00 | -1.21 | 20.58 | 20.00 | 15.20 | 2.23 | 0.28 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3503 | 55.95 | 24.21 | 14.00 | 3.00 | 9.00 | 6.37 | 6.51 | 5.61 |
| FAILED_AUCTION_RECLAIM | kept | 19364 | 70.75 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 6.70 | 5.05 |
| QUIET_COMPRESSION_BREAK | kept | 16564 | 66.70 | 17.00 | 18.00 | 3.00 | 14.00 | 10.00 | 4.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 21785 | 50.44 | 23.15 | 17.99 | 3.00 | 16.55 | 5.00 | 2.43 | 2.53 |
| SR_FLIP_RETEST | kept | 595 | 66.21 | 20.75 | 13.34 | 3.00 | 15.40 | 6.63 | 6.71 | 2.23 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3503 | 55.95 | 0.00 | 0.00 | 1.69 | 0.00 | 0.00 | 0.00 | **1.69** |
| FAILED_AUCTION_RECLAIM | kept | 19364 | 70.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 16564 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 21785 | 50.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 595 | 66.21 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Total log lines in window: `11061233`
- `Path funnel` emissions: `299`
- `Regime distribution` emissions: `299`
- `QUIET_SCALP_BLOCK` events: `1392`
- `confidence_gate` events: `61811`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `2`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **2**
- Avg resolved threshold: **0.233%** raw → avg net **+1.62%** @ 10x
- Avg time-to-fire from dispatch: **964s**
- By threshold source: stamped=2

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 1 | 0.265% | +1.95% | 963 | stamped=1 |
| FAILED_AUCTION_RECLAIM | 1 | 0.200% | +1.30% | 964 | stamped=1 |
- Top symbols: TONUSDT=1, DOGEUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **186**
- Total REST-fallback activations: **88**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 175 | 2635 | 4190 | 12269 | 0 |
| futures_liq | 11 | 1924 | 2562 | 2779 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 88 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| regime_shift | 3 |
| pre_tp | 2 |
| signal_close | 1 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[absent=126979, present=1754355] state[empty=126979, populated=1754355] buckets[many=1601232, none=126979, some=153123] sources[none] quality[none]
- funding_rate: presence[absent=4587, present=1876747] state[empty=4587, populated=1876747] buckets[few=1876747, none=4587] sources[none] quality[none]
- liquidation_clusters: presence[absent=1881334] state[empty=1881334] buckets[none=1881334] sources[none] quality[none]
- oi_snapshot: presence[absent=602, present=1880732] state[empty=602, populated=1880732] buckets[few=946, many=1875810, none=602, some=3976] sources[none] quality[none]
- order_book: presence[absent=87146, present=1794188] state[populated=1794188, unavailable=87146] buckets[few=1794188, none=87146] sources[book_ticker=1794188, unavailable=87146] quality[none=87146, top_of_book_only=1794188]
- orderblocks: presence[absent=1881334] state[empty=1881334] buckets[none=1881334] sources[not_implemented=1881334] quality[none]
- recent_ticks: presence[absent=128880, present=1752454] state[empty=128880, populated=1752454] buckets[many=1752454, none=128880] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.2424428462982178` sec
- Median create→first breach: `2886.148158788681` sec
- Median create→terminal: `663.1577041149139` sec
- Median first breach→terminal: `1.9931271076202393` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.0866 | None | None |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1774 | None | None |
| SR_FLIP_RETEST | 14 | 14 | 0.0 | 0.0 | 0.0 | -0.0207 | 2886.148158788681 | 663.1577041149139 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 107733 | 16 | 6484 | 0.0 | 0.0 | 2886.148158788681 | 663.1577041149139 | 101249 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 2 | 0 | 2 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `19`
- Gating Δ: `78570`
- No-generation Δ: `-1400873`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.0898, "current_avg_pnl": 0.0866, "current_win_rate": 0.0, "previous_avg_pnl": -0.0032, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0317, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.0317, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.628, "current_avg_pnl": -0.1774, "current_win_rate": 0.0, "previous_avg_pnl": 0.4506, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.2319, "current_avg_pnl": -0.0207, "current_win_rate": 0.0, "previous_avg_pnl": 0.2112, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -5, "geometry_changed_delta": 0, "geometry_preserved_delta": 76604, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 2886.15, "median_terminal_delta_sec": -2590.11, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **SR_FLIP_RETEST**
