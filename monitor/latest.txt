# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, SR_FLIP_RETEST, TREND_PULLBACK_EMA
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `5` sec (warning=False)
- Latest performance record age: `4944` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 9 | 9 | 0 | 1 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 1892 | 1892 | 1805 | 11 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 262507 | 262498 | 9 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 262507 | 260615 | 1892 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 262507 | 262507 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 262507 | 241900 | 20607 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 262507 | 262507 | 0 | 0 | 0 | 0 | dependency-missing (regime_blocked) |
| EVAL::LIQUIDATION_REVERSAL | 262507 | 262507 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 262507 | 262507 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 262507 | 262506 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 262507 | 262436 | 71 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 262507 | 253316 | 9191 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 262507 | 256202 | 6305 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 262507 | 261707 | 800 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 262507 | 262497 | 10 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 262507 | 262507 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 20607 | 20607 | 16669 | 193 | active-low-quality (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 6305 | 6305 | 5270 | 40 | low-sample (none) |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0 | 1 | 1 | 0 | 1 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 71 | 71 | 23 | 21 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 9191 | 9191 | 3644 | 156 | active-low-quality (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 800 | 800 | 663 | 24 | active-low-quality (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 10 | 10 | 10 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- EVAL::BREAKDOWN_SHORT: regime_blocked=128133, volume_spike_missing=98811, basic_filters_failed=30355
- EVAL::CONTINUATION_LIQUIDITY_SWEEP: regime_blocked=169250, sweeps_not_detected=29653, basic_filters_failed=20174
- EVAL::DIVERGENCE_CONTINUATION: regime_blocked=169250, cvd_divergence_failed=70637, basic_filters_failed=20174
- EVAL::FAILED_AUCTION_RECLAIM: auction_not_detected=99435, basic_filters_failed=72863, reclaim_hold_failed=35422
- EVAL::FUNDING_EXTREME: regime_blocked=128133, funding_not_extreme=100107, basic_filters_failed=30350
- EVAL::LIQUIDATION_REVERSAL: cascade_threshold_not_met=181584, basic_filters_failed=73991, cvd_divergence_failed=6643
- EVAL::OPENING_RANGE_BREAKOUT: regime_blocked=262507
- EVAL::POST_DISPLACEMENT_CONTINUATION: regime_blocked=169250, breakout_not_found=40810, basic_filters_failed=20174
- EVAL::QUIET_COMPRESSION_BREAK: regime_blocked=101115, breakout_not_detected=56067, basic_filters_failed=52688
- EVAL::SR_FLIP_RETEST: flip_close_not_confirmed=131249, basic_filters_failed=72616, retest_out_of_zone=18710
- EVAL::STANDARD: momentum_reject=111840, adx_reject=61599, basic_filters_failed=51649
- EVAL::TREND_PULLBACK: regime_blocked=169250, basic_filters_failed=20137, ema_alignment_reject=19177
- EVAL::VOLUME_SURGE_BREAKOUT: regime_blocked=128133, volume_spike_missing=98831, basic_filters_failed=30355
- EVAL::WHALE_MOMENTUM: momentum_reject=134374, regime_blocked=128133

## Dependency readiness
- cvd: presence[present=262507] state[empty=2031, populated=260476] buckets[few=694, many=254257, none=2031, some=5525] sources[none] quality[none]
- funding_rate: presence[present=262507] state[empty=2481, populated=260026] buckets[few=260026, none=2481] sources[none] quality[none]
- liquidation_clusters: presence[present=262507] state[empty=130697, populated=131810] buckets[few=105697, none=130697, some=26113] sources[none] quality[none]
- oi_snapshot: presence[present=262507] state[empty=2472, populated=260035] buckets[few=4175, many=230404, none=2472, some=25456] sources[none] quality[none]
- order_book: presence[absent=60795, present=201712] state[populated=201712, unavailable=60795] buckets[few=201712, none=60795] sources[book_ticker=201712, unavailable=60795] quality[none=60795, top_of_book_only=201712]
- orderblocks: presence[present=262507] state[empty=262507] buckets[none=262507] sources[not_implemented=262507] quality[none]
- recent_ticks: presence[present=262507] state[empty=12329, populated=250178] buckets[many=250178, none=12329] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.475738048553467` sec
- Median create→first breach: `184.9289734363556` sec
- Median create→terminal: `217.66476106643677` sec
- Median first breach→terminal: `10.827589988708496` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 19, "pct": 51.4}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | 1 | 1 | 0.0 | 100.0 | 0.0 | -1.1325 | 185.00471901893616 | 186.09579491615295 |
| FAILED_AUCTION_RECLAIM | 9 | 9 | 0.0 | 0.0 | 0.0 | 1.5372 | 185.23825109004974 | 631.5399980545044 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 4.6377 | 185.57982683181763 | 203.14849281311035 |
| SR_FLIP_RETEST | 7 | 7 | 0.0 | 28.6 | 0.0 | 0.1104 | 183.57221055030823 | 651.2669088840485 |
| TREND_PULLBACK_EMA | 19 | 19 | 0.0 | 78.9 | 0.0 | -0.1511 | 184.9443188905716 | 196.06612396240234 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 9191 | 156 | 3644 | 0.0 | 28.6 | 183.57221055030823 | 651.2669088840485 | 5547 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 800 | 24 | 663 | 0.0 | 78.9 | 184.9443188905716 | 196.06612396240234 | 137 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `447`
- Gating Δ: `28084`
- No-generation Δ: `3636212`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 1.5372, "current_avg_pnl": 1.5372, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.1104, "current_avg_pnl": 0.1104, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.1511, "current_avg_pnl": -0.1511, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 156, "geometry_changed_delta": 0, "geometry_preserved_delta": 5547, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 183.57, "median_terminal_delta_sec": 651.27, "sl_rate_delta": 28.6, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 24, "geometry_changed_delta": 0, "geometry_preserved_delta": 137, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 184.94, "median_terminal_delta_sec": 196.07, "sl_rate_delta": 78.9, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **VOLUME_SURGE_BREAKOUT**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
