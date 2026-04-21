# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::WHALE_MOMENTUM, EVAL::VOLUME_SURGE_BREAKOUT, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::WHALE_MOMENTUM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `6` sec (warning=False)
- Latest performance record age: `None` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 14 | 14 | 11 | 1 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 53995 | 53994 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 53995 | 53981 | 14 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 53995 | 53995 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 53995 | 44718 | 9277 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FUNDING_EXTREME | 53995 | 53995 | 0 | 0 | 0 | 0 | dependency-missing (none) |
| EVAL::LIQUIDATION_REVERSAL | 53995 | 53995 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 53995 | 53995 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 53995 | 53995 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 53995 | 53852 | 143 | 0 | 0 | 0 | low-sample (none) |
| EVAL::SR_FLIP_RETEST | 53995 | 52080 | 1915 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 53995 | 52436 | 1559 | 0 | 0 | 0 | low-sample (none) |
| EVAL::TREND_PULLBACK | 53995 | 53987 | 8 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 53995 | 53995 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 53995 | 53995 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 9277 | 9277 | 9277 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 1559 | 1559 | 1284 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 143 | 143 | 143 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 1915 | 1915 | 1726 | 5 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 8 | 8 | 6 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=41102, volume_spike_missing=8706, basic_filters_failed=3655
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=53002, ema_alignment_reject=465, sweeps_not_detected=226
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=53002, cvd_divergence_failed=681, cvd_insufficient=268
- EVAL::FAILED_AUCTION_RECLAIM: basic_filters_failed=17965, auction_not_detected=12022, regime_blocked=8068
- EVAL::FUNDING_EXTREME: none=41102, funding_not_extreme=8915, basic_filters_failed=3636
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=32924, basic_filters_failed=19807, cvd_divergence_failed=1224
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=53995
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=53002, ema_alignment_reject=465, breakout_not_found=303
- EVAL::QUIET_COMPRESSION_BREAK: none=53852
- EVAL::SR_FLIP_RETEST: flip_close_not_confirmed=20275, basic_filters_failed=17748, regime_blocked=8068
- EVAL::STANDARD: none=52436
- EVAL::TREND_PULLBACK: regime_blocked=53002, ema_alignment_reject=464, retest_proximity_failed=209
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=41102, volume_spike_missing=8653, basic_filters_failed=3655
- EVAL::WHALE_MOMENTUM: regime_blocked=41102, momentum_reject=12893

## Dependency readiness
- cvd: presence[present=53995] state[empty=23, populated=53972] buckets[few=1881, many=44393, none=23, some=7698] sources[none] quality[none]
- funding_rate: presence[present=53995] state[empty=509, populated=53486] buckets[few=53486, none=509] sources[none] quality[none]
- liquidation_clusters: presence[present=53995] state[empty=31091, populated=22904] buckets[few=17681, none=31091, some=5223] sources[none] quality[none]
- oi_snapshot: presence[present=53995] state[empty=502, populated=53493] buckets[few=5549, many=22248, none=502, some=25696] sources[none] quality[none]
- order_book: presence[absent=7302, present=46693] state[populated=46693, unavailable=7302] buckets[few=46693, none=7302] sources[book_ticker=46693, unavailable=7302] quality[none=7302, top_of_book_only=46693]
- orderblocks: presence[absent=53995] state[unavailable=53995] buckets[none=53995] sources[none] quality[none]
- recent_ticks: presence[present=53995] state[empty=1967, populated=52028] buckets[many=52028, none=1967] sources[none] quality[none]

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
| SR_FLIP_RETEST | 0 | 1915 | 5 | 1726 | 0.0 | 0.0 | None | None | 189 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 8 | 0 | 6 | 0.0 | 0.0 | None | None | 2 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `8`
- Gating Δ: `12448`
- No-generation Δ: `743013`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 5, "geometry_changed_delta": 0, "geometry_preserved_delta": 189, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 2, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::WHALE_MOMENTUM**
- Most promising healthy path: **none**
- Most likely bottleneck: **FAILED_AUCTION_RECLAIM**
- Suggested next investigation target: **EVAL::WHALE_MOMENTUM**
