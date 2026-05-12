# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::WHALE_MOMENTUM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `None` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1241 | 1241 | 1241 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 2511 | 2511 | 3 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 4945 | 4945 | 4887 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1922193 | 1920952 | 1241 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1738828 | 1736317 | 2511 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::DIVERGENCE_CONTINUATION | 1738828 | 1733883 | 4945 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1738828 | 1677721 | 61107 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1922193 | 1907748 | 14445 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1922193 | 1922193 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1738828 | 1738826 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1922193 | 1922193 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1738828 | 1738828 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1738828 | 1723915 | 14913 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1738828 | 1573252 | 165576 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1738828 | 1717263 | 21565 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1738828 | 1738528 | 300 | 0 | 0 | 0 | low-sample (ema_not_tested_prev) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1922193 | 1922193 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1922193 | 1922193 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 61107 | 61107 | 22456 | 2 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 14445 | 14445 | 14181 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 21565 | 21565 | 2418 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 14913 | 14913 | 12763 | 2 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 165576 | 165576 | 5646 | 0 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 300 | 300 | 300 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1920952): breakout_not_found=1083568, basic_filters_failed=585934, retest_proximity_failed=223994, volume_spike_missing=26566, ema_alignment_reject=890
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1736317): basic_filters_failed=484297, sweeps_not_detected=462899, ema_alignment_reject=303573, regime_blocked=248854, rsi_reject=101840, adx_reject=77975, momentum_reject=55883, reclaim_confirmation_failed=996
- **EVAL::DIVERGENCE_CONTINUATION** (total=1733883): cvd_divergence_failed=748143, basic_filters_failed=484297, regime_blocked=248854, retest_proximity_failed=86299, ema_alignment_reject=79547, missing_cvd=63634, cvd_insufficient=22190, missing_fvg_or_orderblock=919
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1677721): auction_not_detected=673491, basic_filters_failed=537368, reclaim_hold_failed=278851, tail_too_small=188011
- **EVAL::FUNDING_EXTREME** (total=1907748): funding_not_extreme=1278198, basic_filters_failed=560629, missing_funding_rate=57639, ema_alignment_reject=8164, rsi_reject=3118
- **EVAL::LIQUIDATION_REVERSAL** (total=1922193): cascade_threshold_not_met=1315173, basic_filters_failed=585934, cvd_divergence_failed=19233, missing_cvd=1853
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1738826): no_ma_cross=1192957, basic_filters_failed=537368, ma_cross_cooldown=8501
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1922193): feature_disabled=1922193
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1738828): breakout_not_found=624129, basic_filters_failed=484297, ema_alignment_reject=303573, regime_blocked=248854, adx_reject=77975
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1723915): regime_blocked=1489974, compression_not_detected=104691, breakout_not_detected=53748, basic_filters_failed=53071, missing_fvg_or_orderblock=11935, macd_reject=10496
- **EVAL::SR_FLIP_RETEST** (total=1573252): basic_filters_failed=537368, flip_close_not_confirmed=340076, retest_out_of_zone=292694, reclaim_hold_failed=200330, wick_quality_failed=130422, rsi_reject=59037, ema_alignment_reject=13325
- **EVAL::STANDARD** (total=1717263): momentum_reject=623303, basic_filters_failed=398911, adx_reject=288062, sweeps_not_detected=174018, ema_alignment_reject=156456, macd_reject=31727, rsi_reject=30419, invalid_sl_geometry=14367
- **EVAL::TREND_PULLBACK** (total=1738528): ema_not_tested_prev=490967, basic_filters_failed=484297, ema_alignment_reject=361862, regime_blocked=248854, body_conviction_fail=51873, rsi_reject=50881, no_ema_reclaim_close=22618, no_prev_high_break=22321, prev_already_below_emas=2311, prev_already_above_emas=2105, momentum_flat=324, ema21_not_tagged=62, no_prev_low_break=53
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1922193): breakout_not_found=777418, basic_filters_failed=585934, retest_proximity_failed=526311, ema_alignment_reject=26609, volume_spike_missing=3351, rsi_reject=2570
- **EVAL::WHALE_MOMENTUM** (total=1922193): momentum_reject=1278692, recent_ticks_insufficient=466133, basic_filters_failed=177368

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1796043 | 83.3% |
| QUIET | 311660 | 14.5% |
| TRENDING_DOWN | 46170 | 2.1% |
| RANGING | 1501 | 0.1% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **381**
- Average confidence gap to threshold: **14.72** (samples=381) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SKYAIUSDT=231, LDOUSDT=150

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 2612 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 55 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 302 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 2374 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 231 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 150 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1973 |
| SR_FLIP_RETEST | filtered | min_confidence | 28403 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2159 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 2612 | 66.70 | 65.00 | -1.70 | 22.36 | 17.80 | 17.00 | 0.00 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 55 | 51.38 | 65.00 | 13.62 | 20.80 | 19.90 | 20.00 | 0.76 | 0.09 |
| FAILED_AUCTION_RECLAIM | filtered | 302 | 50.80 | 65.00 | 14.20 | 22.95 | 20.00 | 14.00 | 5.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | kept | 2374 | 69.28 | 65.00 | -4.28 | 22.51 | 20.00 | 14.00 | 4.98 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 231 | 49.76 | 65.00 | 15.24 | 20.40 | 20.00 | 15.20 | 3.16 | 21.60 |
| QUIET_COMPRESSION_BREAK | filtered | 150 | 51.06 | 65.00 | 13.94 | 21.10 | 17.00 | 15.80 | 0.00 | 8.24 |
| QUIET_COMPRESSION_BREAK | kept | 1973 | 66.70 | 65.00 | -1.70 | 19.89 | 20.00 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 28403 | 50.97 | 65.00 | 14.03 | 20.12 | 20.00 | 15.25 | 2.54 | 5.09 |
| SR_FLIP_RETEST | kept | 2159 | 72.73 | 65.00 | -7.73 | 21.42 | 20.00 | 15.20 | 2.65 | 3.61 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 2612 | 66.70 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 6.70 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 55 | 51.38 | 25.00 | 18.00 | 3.00 | 10.00 | 5.00 | 4.70 | 0.76 |
| FAILED_AUCTION_RECLAIM | filtered | 302 | 50.80 | 25.00 | 14.00 | 3.00 | 9.00 | 2.50 | 7.30 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 2374 | 69.28 | 24.01 | 14.00 | 3.37 | 11.21 | 5.43 | 6.27 | 4.98 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 231 | 49.76 | 25.00 | 14.00 | 6.00 | 12.00 | 2.50 | 8.70 | 3.16 |
| QUIET_COMPRESSION_BREAK | filtered | 150 | 51.06 | 17.00 | 18.00 | 15.00 | 14.00 | 5.00 | 5.30 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1973 | 66.70 | 17.00 | 18.00 | 3.00 | 14.00 | 10.00 | 4.70 | 0.00 |
| SR_FLIP_RETEST | filtered | 28403 | 50.97 | 22.99 | 18.00 | 3.00 | 16.82 | 5.00 | 2.35 | 2.54 |
| SR_FLIP_RETEST | kept | 2159 | 72.73 | 22.57 | 18.00 | 3.90 | 13.53 | 7.07 | 9.21 | 2.65 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 2612 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 55 | 51.38 | 0.00 | 0.00 | 0.09 | 0.00 | 0.00 | 0.00 | **0.09** |
| FAILED_AUCTION_RECLAIM | filtered | 302 | 50.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 2374 | 69.28 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 231 | 49.76 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | **21.60** |
| QUIET_COMPRESSION_BREAK | filtered | 150 | 51.06 | 0.00 | 0.00 | 3.94 | 0.00 | 4.30 | 0.00 | **8.24** |
| QUIET_COMPRESSION_BREAK | kept | 1973 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 28403 | 50.97 | 0.06 | 0.00 | 0.01 | 0.00 | 0.00 | 0.00 | **0.07** |
| SR_FLIP_RETEST | kept | 2159 | 72.73 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `10851187`
- `Path funnel` emissions: `288`
- `Regime distribution` emissions: `288`
- `QUIET_SCALP_BLOCK` events: `381`
- `confidence_gate` events: `38259`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **188**
- Total REST-fallback activations: **89**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 178 | 2471 | 4091 | 4317 | 0 |
| futures_liq | 10 | 2285 | 3377 | 3501 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 89 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| regime_shift | 6 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[absent=146202, present=1775991] state[empty=146202, populated=1775991] buckets[many=1591057, none=146202, some=184934] sources[none] quality[none]
- funding_rate: presence[absent=57639, present=1864554] state[empty=57639, populated=1864554] buckets[few=1864554, none=57639] sources[none] quality[none]
- liquidation_clusters: presence[absent=1922193] state[empty=1922193] buckets[none=1922193] sources[none] quality[none]
- oi_snapshot: presence[absent=47024, present=1875169] state[empty=47024, populated=1875169] buckets[many=1868102, none=47024, some=7067] sources[none] quality[none]
- order_book: presence[absent=71417, present=1850776] state[populated=1850776, unavailable=71417] buckets[few=1850776, none=71417] sources[book_ticker=1850776, unavailable=71417] quality[none=71417, top_of_book_only=1850776]
- orderblocks: presence[absent=1922193] state[empty=1922193] buckets[none=1922193] sources[not_implemented=1922193] quality[none]
- recent_ticks: presence[absent=88089, present=1834104] state[empty=88089, populated=1834104] buckets[many=1834104, none=88089] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `None` sec
- Median create→first breach: `None` sec
- Median create→terminal: `None` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 165576 | 0 | 5646 | 0.0 | 0.0 | None | None | 159930 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 300 | 0 | 300 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-114`
- Gating Δ: `-5716`
- No-generation Δ: `-1143629`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -15, "geometry_changed_delta": 0, "geometry_preserved_delta": 42894, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::WHALE_MOMENTUM**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **EVAL::WHALE_MOMENTUM**
