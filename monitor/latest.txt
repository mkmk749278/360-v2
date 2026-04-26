# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `49` sec (warning=False)
- Latest performance record age: `3952` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 135 | 135 | 117 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 161013 | 161011 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 161013 | 160878 | 135 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 161013 | 161013 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 161013 | 146672 | 14341 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 161013 | 161011 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 161013 | 161013 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 161013 | 161013 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 161013 | 161011 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 161013 | 160876 | 137 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 161013 | 145630 | 15383 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 161013 | 157675 | 3338 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 161013 | 160915 | 98 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 161013 | 161011 | 2 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 161013 | 161013 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 14341 | 14341 | 11396 | 68 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 3338 | 3338 | 2660 | 2 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 137 | 137 | 78 | 2 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 15383 | 15383 | 9178 | 93 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 98 | 98 | 93 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2 | 2 | 2 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=138885, volume_spike_missing=16054, basic_filters_failed=5374
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=141606, ema_alignment_reject=5483, sweeps_not_detected=5228
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=141606, cvd_divergence_failed=14202, basic_filters_failed=4991
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=61213, basic_filters_failed=46877, reclaim_hold_failed=23193
- EVAL::FUNDING_EXTREME: regime_blocked=138885, funding_not_extreme=15064, basic_filters_failed=5367
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=109352, basic_filters_failed=46977, cvd_divergence_failed=4215
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=161013
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=141606, breakout_not_found=6348, ema_alignment_reject=5483
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=60627, basic_filters_failed=41886, compression_not_detected=30476
- EVAL::SR_FLIP_RETEST: basic_filters_failed=46532, reclaim_hold_failed=36662, flip_close_not_confirmed=33476
- EVAL::STANDARD: momentum_reject=68594, basic_filters_failed=34083, adx_reject=28867
- EVAL::TREND_PULLBACK: regime_blocked=141606, ema_alignment_reject=5437, basic_filters_failed=4976
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=138885, volume_spike_missing=16055, basic_filters_failed=5374
- EVAL::WHALE_MOMENTUM: regime_blocked=138885, momentum_reject=22128

## Dependency readiness
- cvd: presence[absent=12268, present=148745] state[empty=12268, populated=148745] buckets[few=659, many=142856, none=12268, some=5230] sources[none] quality[none]
- funding_rate: presence[absent=1715, present=159298] state[empty=1715, populated=159298] buckets[few=159298, none=1715] sources[none] quality[none]
- liquidation_clusters: presence[absent=101603, present=59410] state[empty=101603, populated=59410] buckets[few=45131, none=101603, some=14279] sources[none] quality[none]
- oi_snapshot: presence[absent=1051, present=159962] state[empty=1051, populated=159962] buckets[few=516, many=157622, none=1051, some=1824] sources[none] quality[none]
- order_book: presence[absent=49918, present=111095] state[populated=111095, unavailable=49918] buckets[few=111095, none=49918] sources[book_ticker=111095, unavailable=49918] quality[none=49918, top_of_book_only=111095]
- orderblocks: presence[absent=161013] state[empty=161013] buckets[none=161013] sources[not_implemented=161013] quality[none]
- recent_ticks: presence[absent=5752, present=155261] state[empty=5752, populated=155261] buckets[many=155261, none=5752] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `26.461432933807373` sec
- Median create→first breach: `None` sec
- Median create→terminal: `1171.8955128192902` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.1541 | None | 1171.8955128192902 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 15383 | 93 | 9178 | 0.0 | 0.0 | None | 1171.8955128192902 | 6205 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 98 | 0 | 93 | 0.0 | 0.0 | None | None | 5 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `168`
- Gating Δ: `23530`
- No-generation Δ: `2220742`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.2463, "current_avg_pnl": -0.1541, "current_win_rate": 0.0, "previous_avg_pnl": 0.0922, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 93, "geometry_changed_delta": 0, "geometry_preserved_delta": 6205, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 374.92, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 5, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -629.84, "median_terminal_delta_sec": -631.06, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **TREND_PULLBACK_EMA**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
