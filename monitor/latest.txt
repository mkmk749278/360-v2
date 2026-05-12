# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: LIQUIDITY_SWEEP_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **LIQUIDITY_SWEEP_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `1917` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2152 | 2152 | 2152 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1809 | 1809 | 0 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 9536 | 9536 | 9536 | 0 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1943068 | 1940916 | 2152 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1751537 | 1749728 | 1809 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::DIVERGENCE_CONTINUATION | 1751537 | 1742001 | 9536 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1751537 | 1691352 | 60185 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1943068 | 1924781 | 18287 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1943068 | 1943068 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1751537 | 1751535 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::OPENING_RANGE_BREAKOUT | 1943068 | 1943068 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1751537 | 1751537 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::QUIET_COMPRESSION_BREAK | 1751537 | 1742725 | 8812 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1751537 | 1577854 | 173683 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1751537 | 1731194 | 20343 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1751537 | 1751237 | 300 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1943068 | 1943068 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1943068 | 1943068 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 60185 | 60185 | 24183 | 0 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 18287 | 18287 | 17063 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 20343 | 20343 | 1784 | 3 | active-low-quality (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 8812 | 8812 | 7988 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 173683 | 173683 | 2761 | 6 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 300 | 300 | 300 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1940916): breakout_not_found=1102803, basic_filters_failed=599615, retest_proximity_failed=204619, volume_spike_missing=32838, ema_alignment_reject=1041
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1749728): basic_filters_failed=490392, sweeps_not_detected=470447, ema_alignment_reject=310117, regime_blocked=226657, adx_reject=99250, rsi_reject=94621, momentum_reject=57248, reclaim_confirmation_failed=996
- **EVAL::DIVERGENCE_CONTINUATION** (total=1742001): cvd_divergence_failed=785052, basic_filters_failed=490392, regime_blocked=226657, ema_alignment_reject=78933, retest_proximity_failed=71449, missing_cvd=69692, cvd_insufficient=18907, missing_fvg_or_orderblock=919
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1691352): auction_not_detected=657665, basic_filters_failed=550896, reclaim_hold_failed=280034, tail_too_small=202757
- **EVAL::FUNDING_EXTREME** (total=1924781): funding_not_extreme=1284914, basic_filters_failed=575529, missing_funding_rate=53558, rsi_reject=6047, ema_alignment_reject=4733
- **EVAL::LIQUIDATION_REVERSAL** (total=1943068): cascade_threshold_not_met=1321105, basic_filters_failed=599615, cvd_divergence_failed=21788, missing_cvd=560
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1751535): no_ma_cross=1193758, basic_filters_failed=550896, ma_cross_cooldown=6881
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1943068): feature_disabled=1943068
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1751537): breakout_not_found=625121, basic_filters_failed=490392, ema_alignment_reject=310117, regime_blocked=226657, adx_reject=99250
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1742725): regime_blocked=1524880, compression_not_detected=85344, basic_filters_failed=60504, breakout_not_detected=47916, missing_fvg_or_orderblock=14313, macd_reject=9768
- **EVAL::SR_FLIP_RETEST** (total=1577854): basic_filters_failed=550896, flip_close_not_confirmed=333174, retest_out_of_zone=287393, reclaim_hold_failed=203740, wick_quality_failed=132854, rsi_reject=58868, ema_alignment_reject=10929
- **EVAL::STANDARD** (total=1731194): momentum_reject=617549, basic_filters_failed=394834, adx_reject=360308, ema_alignment_reject=150244, sweeps_not_detected=146510, macd_reject=28394, rsi_reject=19004, invalid_sl_geometry=14351
- **EVAL::TREND_PULLBACK** (total=1751237): basic_filters_failed=490392, ema_not_tested_prev=487498, ema_alignment_reject=390418, regime_blocked=226657, body_conviction_fail=57913, rsi_reject=39784, no_ema_reclaim_close=34705, no_prev_high_break=19564, prev_already_below_emas=2310, prev_already_above_emas=1793, momentum_flat=203
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1943068): breakout_not_found=759214, basic_filters_failed=599615, retest_proximity_failed=544929, ema_alignment_reject=32526, volume_spike_missing=6784
- **EVAL::WHALE_MOMENTUM** (total=1943068): momentum_reject=1259978, recent_ticks_insufficient=495171, basic_filters_failed=187919

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1797189 | 83.6% |
| QUIET | 274943 | 12.8% |
| TRENDING_DOWN | 58607 | 2.7% |
| RANGING | 18135 | 0.8% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **476**
- Average confidence gap to threshold: **12.75** (samples=476) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: SKYAIUSDT=232, LDOUSDT=150, SUIUSDT=94

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | min_confidence_pass | 1833 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 302 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 889 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 232 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 3675 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 244 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 306 |
| SR_FLIP_RETEST | filtered | min_confidence | 29666 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 8131 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1833 | 66.70 | 65.00 | -1.70 | 22.35 | 17.80 | 17.00 | 0.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 302 | 50.80 | 65.00 | 14.20 | 22.95 | 20.00 | 14.00 | 5.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | kept | 889 | 68.15 | 65.00 | -3.15 | 24.12 | 20.00 | 14.00 | 4.84 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 232 | 49.76 | 65.00 | 15.24 | 20.40 | 20.00 | 15.20 | 3.16 | 21.60 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 3675 | 67.80 | 65.00 | -2.80 | 20.28 | 20.00 | 15.20 | 3.00 | 0.00 |
| QUIET_COMPRESSION_BREAK | filtered | 244 | 54.62 | 65.00 | 10.38 | 21.46 | 16.96 | 15.80 | 0.00 | 7.37 |
| QUIET_COMPRESSION_BREAK | kept | 306 | 71.36 | 65.00 | -6.36 | 21.70 | 19.80 | 15.80 | 0.00 | 5.90 |
| SR_FLIP_RETEST | filtered | 29666 | 51.34 | 65.00 | 13.66 | 20.00 | 19.99 | 15.27 | 2.54 | 5.47 |
| SR_FLIP_RETEST | kept | 8131 | 69.93 | 65.00 | -4.93 | 20.28 | 20.00 | 15.20 | 2.70 | 5.64 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1833 | 66.70 | 17.00 | 18.00 | 6.00 | 14.00 | 5.00 | 6.70 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 302 | 50.80 | 25.00 | 14.00 | 3.00 | 9.00 | 2.50 | 7.30 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 889 | 68.15 | 22.35 | 14.00 | 3.99 | 11.00 | 6.16 | 5.80 | 4.84 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 232 | 49.76 | 25.00 | 14.00 | 6.00 | 12.00 | 2.50 | 8.70 | 3.16 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 3675 | 67.80 | 25.00 | 14.00 | 3.00 | 12.00 | 5.50 | 5.30 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 244 | 54.62 | 17.00 | 18.00 | 12.69 | 14.00 | 5.00 | 4.53 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 306 | 71.36 | 24.87 | 18.00 | 8.95 | 16.95 | 5.08 | 3.41 | 0.00 |
| SR_FLIP_RETEST | filtered | 29666 | 51.34 | 22.94 | 18.00 | 3.00 | 16.68 | 5.00 | 2.68 | 2.54 |
| SR_FLIP_RETEST | kept | 8131 | 69.93 | 22.30 | 17.99 | 4.01 | 12.44 | 6.84 | 9.79 | 2.70 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | kept | 1833 | 66.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 302 | 50.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 889 | 68.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 232 | 49.76 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | **21.60** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 3675 | 67.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | filtered | 244 | 54.62 | 0.00 | 0.00 | 2.42 | 0.00 | 2.64 | 0.00 | **5.06** |
| QUIET_COMPRESSION_BREAK | kept | 306 | 71.36 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 29666 | 51.34 | 0.00 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | **0.20** |
| SR_FLIP_RETEST | kept | 8131 | 69.93 | 0.00 | 0.00 | 0.68 | 0.00 | 0.00 | 0.00 | **0.68** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=1 (100.0%) | PREMATURE=0 (0.0%) | NEUTRAL=0 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 1 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| regime_shift | 1 | 0 | 0 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 1 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `10877322`
- `Path funnel` emissions: `287`
- `Regime distribution` emissions: `287`
- `QUIET_SCALP_BLOCK` events: `476`
- `confidence_gate` events: `45278`
- `free_channel_post` events: `5`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **192**
- Total REST-fallback activations: **90**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 180 | 2366 | 4039 | 4317 | 0 |
| futures_liq | 12 | 2285 | 3420 | 3501 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 90 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **5**

| Source | Count |
|---|---:|
| regime_shift | 5 |

- By severity: HIGH=5

## Dependency readiness
- cvd: presence[absent=169975, present=1773093] state[empty=169975, populated=1773093] buckets[many=1595640, none=169975, some=177453] sources[none] quality[none]
- funding_rate: presence[absent=53558, present=1889510] state[empty=53558, populated=1889510] buckets[few=1889510, none=53558] sources[none] quality[none]
- liquidation_clusters: presence[absent=1943068] state[empty=1943068] buckets[none=1943068] sources[none] quality[none]
- oi_snapshot: presence[absent=46298, present=1896770] state[empty=46298, populated=1896770] buckets[few=317, many=1895494, none=46298, some=959] sources[none] quality[none]
- order_book: presence[absent=64938, present=1878130] state[populated=1878130, unavailable=64938] buckets[few=1878130, none=64938] sources[book_ticker=1878130, unavailable=64938] quality[none=64938, top_of_book_only=1878130]
- orderblocks: presence[absent=1943068] state[empty=1943068] buckets[none=1943068] sources[not_implemented=1943068] quality[none]
- recent_ticks: presence[absent=103637, present=1839431] state[empty=103637, populated=1839431] buckets[many=1839431, none=103637] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.6903350353240967` sec
- Median create→first breach: `None` sec
- Median create→terminal: `2190.973512172699` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| LIQUIDITY_SWEEP_REVERSAL | 3 | 3 | 0.0 | 0.0 | 0.0 | 0.0208 | None | 2190.973512172699 |
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.1115 | None | None |
| SR_FLIP_RETEST | 2 | 2 | 0.0 | 0.0 | 0.0 | 0.1115 | None | None |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 173683 | 6 | 2761 | 0.0 | 0.0 | None | None | 170922 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 300 | 0 | 300 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-70`
- Gating Δ: `11430`
- No-generation Δ: `-531424`
- Fast failures Δ: `0`
- Quality changes: `{"LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": 0.0208, "current_avg_pnl": 0.0208, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 44392, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **LIQUIDITY_SWEEP_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **FAILED_AUCTION_RECLAIM**
- Suggested next investigation target: **LIQUIDITY_SWEEP_REVERSAL**
