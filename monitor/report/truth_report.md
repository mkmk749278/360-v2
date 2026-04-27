# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `34` sec (warning=False)
- Latest performance record age: `7934` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 869 | 869 | 840 | 8 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 224236 | 224233 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 224236 | 223367 | 869 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 224236 | 224236 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 224236 | 203443 | 20793 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 224236 | 224236 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 224236 | 224236 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 224236 | 224236 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 224236 | 224235 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 224236 | 224060 | 176 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 224236 | 202138 | 22098 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 224236 | 219931 | 4305 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 224236 | 223965 | 271 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 224236 | 224223 | 13 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 224236 | 224236 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 20793 | 20793 | 16660 | 129 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4305 | 4305 | 3591 | 3 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 176 | 176 | 94 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 22098 | 22098 | 13066 | 182 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 271 | 271 | 247 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=174785, volume_spike_missing=35941, basic_filters_failed=11253
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=181607, sweeps_not_detected=14734, basic_filters_failed=10209
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=181607, cvd_divergence_failed=31392, basic_filters_failed=10209
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=86161, basic_filters_failed=55198, reclaim_hold_failed=36734
- EVAL::FUNDING_EXTREME: regime_blocked=174785, funding_not_extreme=35124, basic_filters_failed=10321
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=162120, basic_filters_failed=55625, cvd_divergence_failed=5686
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=224236
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=181607, breakout_not_found=19404, basic_filters_failed=10209
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=76421, regime_blocked=47112, compression_not_detected=45153
- EVAL::SR_FLIP_RETEST: basic_filters_failed=54771, reclaim_hold_failed=49764, flip_close_not_confirmed=45694
- EVAL::STANDARD: momentum_reject=106547, adx_reject=41369, basic_filters_failed=36598
- EVAL::TREND_PULLBACK: regime_blocked=181607, basic_filters_failed=10208, ema_not_tested_prev=9870
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=174785, volume_spike_missing=35869, basic_filters_failed=11253
- EVAL::WHALE_MOMENTUM: regime_blocked=174785, momentum_reject=49451

## Dependency readiness
- cvd: presence[absent=6133, present=218103] state[empty=6133, populated=218103] buckets[few=163, many=217015, none=6133, some=925] sources[none] quality[none]
- funding_rate: presence[absent=4179, present=220057] state[empty=4179, populated=220057] buckets[few=220057, none=4179] sources[none] quality[none]
- liquidation_clusters: presence[absent=131169, present=93067] state[empty=131169, populated=93067] buckets[few=72699, none=131169, some=20368] sources[none] quality[none]
- oi_snapshot: presence[absent=4178, present=220058] state[empty=4178, populated=220058] buckets[few=973, many=216131, none=4178, some=2954] sources[none] quality[none]
- order_book: presence[absent=83032, present=141204] state[populated=141204, unavailable=83032] buckets[few=141204, none=83032] sources[book_ticker=141204, unavailable=83032] quality[none=83032, top_of_book_only=141204]
- orderblocks: presence[absent=224236] state[empty=224236] buckets[none=224236] sources[not_implemented=224236] quality[none]
- recent_ticks: presence[absent=19000, present=205236] state[empty=19000, populated=205236] buckets[many=205236, none=19000] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.9334890842437744` sec
- Median create→first breach: `1615.4716620445251` sec
- Median create→terminal: `907.23046708107` sec
- Median first breach→terminal: `69.09665703773499` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0518 | None | 667.1410489082336 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.3787 | None | 725.657634973526 |
| SR_FLIP_RETEST | 9 | 9 | 0.0 | 11.1 | 0.0 | 0.0787 | 1615.4716620445251 | 1171.8955128192902 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 22098 | 182 | 13066 | 0.0 | 11.1 | 1615.4716620445251 | 1171.8955128192902 | 9032 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 271 | 1 | 247 | 0.0 | 0.0 | None | None | 24 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `259`
- Gating Δ: `27326`
- No-generation Δ: `2254167`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.1296, "current_avg_pnl": 0.0787, "current_win_rate": 0.0, "previous_avg_pnl": 0.2083, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 142, "geometry_changed_delta": 0, "geometry_preserved_delta": 7126, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1615.47, "median_terminal_delta_sec": 374.92, "sl_rate_delta": 11.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 23, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -629.84, "median_terminal_delta_sec": -631.06, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **VOLUME_SURGE_BREAKOUT**
- Suggested next investigation target: **SR_FLIP_RETEST**
