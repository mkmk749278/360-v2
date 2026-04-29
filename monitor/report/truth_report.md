# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::TREND_PULLBACK, EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::TREND_PULLBACK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `3` sec (warning=False)
- Latest performance record age: `53065` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| EVAL::BREAKDOWN_SHORT | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 409322 | 409322 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 409322 | 366289 | 43033 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 409322 | 409322 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 409322 | 409322 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 409322 | 396948 | 12374 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::SR_FLIP_RETEST | 409322 | 382189 | 27133 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 409322 | 401891 | 7431 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 409322 | 409322 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 43033 | 43033 | 40845 | 2 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 7431 | 7431 | 7269 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 12374 | 12374 | 36 | 12 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 27133 | 27133 | 22539 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=407934, volume_spike_missing=817, basic_filters_failed=397
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=409265, sweeps_not_detected=29, adx_reject=14
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=409265, missing_cvd=44, cvd_divergence_failed=7
- EVAL::FAILED_AUCTION_RECLAIM: basic_filters_failed=166532, auction_not_detected=101953, reclaim_hold_failed=52759
- EVAL::FUNDING_EXTREME: funding_not_extreme=240903, basic_filters_failed=166493, ema_alignment_reject=1220
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=240967, basic_filters_failed=166532, missing_cvd=1812
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=409322
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=409265, breakout_not_found=30, adx_reject=14
- EVAL::QUIET_COMPRESSION_BREAK: basic_filters_failed=166526, breakout_not_detected=163250, compression_not_detected=33550
- EVAL::SR_FLIP_RETEST: basic_filters_failed=161297, reclaim_hold_failed=92368, retest_out_of_zone=46281
- EVAL::STANDARD: momentum_reject=147694, basic_filters_failed=110679, adx_reject=85482
- EVAL::TREND_PULLBACK: regime_blocked=409265, rsi_reject=16, body_conviction_fail=13
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=407934, volume_spike_missing=817, basic_filters_failed=397
- EVAL::WHALE_MOMENTUM: regime_blocked=407934, momentum_reject=1388

## Dependency readiness
- cvd: presence[absent=344748, present=64574] state[empty=344748, populated=64574] buckets[many=64574, none=344748] sources[none] quality[none]
- funding_rate: presence[absent=107, present=409215] state[empty=107, populated=409215] buckets[few=409215, none=107] sources[none] quality[none]
- liquidation_clusters: presence[absent=409322] state[empty=409322] buckets[none=409322] sources[none] quality[none]
- oi_snapshot: presence[absent=107, present=409215] state[empty=107, populated=409215] buckets[few=190, many=407880, none=107, some=1145] sources[none] quality[none]
- order_book: presence[absent=23801, present=385521] state[populated=385521, unavailable=23801] buckets[few=385521, none=23801] sources[book_ticker=385521, unavailable=23801] quality[none=23801, top_of_book_only=385521]
- orderblocks: presence[absent=409322] state[empty=409322] buckets[none=409322] sources[not_implemented=409322] quality[none]
- recent_ticks: presence[absent=26580, present=382742] state[empty=26580, populated=382742] buckets[many=382742, none=26580] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.4005110263824463` sec
- Median create→first breach: `None` sec
- Median create→terminal: `1510.1236500740051` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0861 | None | 1510.1236500740051 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 27133 | 0 | 22539 | 0.0 | 0.0 | None | None | 4594 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `14`
- Gating Δ: `70689`
- No-generation Δ: `5640537`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 4594, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -768.49, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::TREND_PULLBACK**
- Most promising healthy path: **none**
- Most likely bottleneck: **SR_FLIP_RETEST**
- Suggested next investigation target: **EVAL::TREND_PULLBACK**
