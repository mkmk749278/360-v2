# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: SR_FLIP_RETEST, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **SR_FLIP_RETEST**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `33` sec (warning=False)
- Latest performance record age: `5832` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 584 | 584 | 557 | 7 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 218762 | 218759 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 218762 | 218178 | 584 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 218762 | 218762 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 218762 | 198368 | 20394 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 218762 | 218762 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 218762 | 218762 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 218762 | 218762 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 218762 | 218761 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 218762 | 218582 | 180 | 0 | 0 | 0 | low-sample (breakout_not_detected) |
| EVAL::SR_FLIP_RETEST | 218762 | 197623 | 21139 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 218762 | 214535 | 4227 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 218762 | 218556 | 206 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 218762 | 218749 | 13 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 218762 | 218762 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 20394 | 20394 | 16342 | 130 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 4227 | 4227 | 3501 | 2 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 180 | 180 | 94 | 3 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 21139 | 21139 | 12544 | 181 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 206 | 206 | 195 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 13 | 13 | 13 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=175758, volume_spike_missing=31818, basic_filters_failed=9195
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=182937, sweeps_not_detected=12434, ema_alignment_reject=8215
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=182937, cvd_divergence_failed=27054, basic_filters_failed=8015
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=84771, basic_filters_failed=53863, reclaim_hold_failed=35272
- EVAL::FUNDING_EXTREME: regime_blocked=175758, funding_not_extreme=31056, basic_filters_failed=8544
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=158122, basic_filters_failed=54290, cvd_divergence_failed=5545
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=218762
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=182937, breakout_not_found=15747, ema_alignment_reject=8215
- EVAL::QUIET_COMPRESSION_BREAK: breakout_not_detected=76747, basic_filters_failed=45752, compression_not_detected=45297
- EVAL::SR_FLIP_RETEST: basic_filters_failed=53436, reclaim_hold_failed=48922, flip_close_not_confirmed=44895
- EVAL::STANDARD: momentum_reject=103878, adx_reject=41133, basic_filters_failed=35949
- EVAL::TREND_PULLBACK: regime_blocked=182937, ema_alignment_reject=8188, basic_filters_failed=8014
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=175758, volume_spike_missing=31752, basic_filters_failed=9195
- EVAL::WHALE_MOMENTUM: regime_blocked=175758, momentum_reject=43004

## Dependency readiness
- cvd: presence[absent=5546, present=213216] state[empty=5546, populated=213216] buckets[few=163, many=212128, none=5546, some=925] sources[none] quality[none]
- funding_rate: presence[absent=3592, present=215170] state[empty=3592, populated=215170] buckets[few=215170, none=3592] sources[none] quality[none]
- liquidation_clusters: presence[absent=129759, present=89003] state[empty=129759, populated=89003] buckets[few=69502, none=129759, some=19501] sources[none] quality[none]
- oi_snapshot: presence[absent=3591, present=215171] state[empty=3591, populated=215171] buckets[few=973, many=211244, none=3591, some=2954] sources[none] quality[none]
- order_book: presence[absent=82161, present=136601] state[populated=136601, unavailable=82161] buckets[few=136601, none=82161] sources[book_ticker=136601, unavailable=82161] quality[none=82161, top_of_book_only=136601]
- orderblocks: presence[absent=218762] state[empty=218762] buckets[none=218762] sources[not_implemented=218762] quality[none]
- recent_ticks: presence[absent=17868, present=200894] state[empty=17868, populated=200894] buckets[many=200894, none=17868] sources[none] quality[none]

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
| SR_FLIP_RETEST | 0 | 21139 | 181 | 12544 | 0.0 | 11.1 | 1615.4716620445251 | 1171.8955128192902 | 8595 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 206 | 0 | 195 | 0.0 | 0.0 | None | None | 11 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `266`
- Gating Δ: `26496`
- No-generation Δ: `2255828`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.1296, "current_avg_pnl": 0.0787, "current_win_rate": 0.0, "previous_avg_pnl": 0.2083, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 147, "geometry_changed_delta": 0, "geometry_preserved_delta": 6843, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1615.47, "median_terminal_delta_sec": 374.92, "sl_rate_delta": 11.1, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 10, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -629.84, "median_terminal_delta_sec": -631.06, "sl_rate_delta": -100.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **SR_FLIP_RETEST**
- Most promising healthy path: **none**
- Most likely bottleneck: **TREND_PULLBACK_EMA**
- Suggested next investigation target: **SR_FLIP_RETEST**
