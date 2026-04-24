# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `70` sec (warning=False)
- Latest performance record age: `4943` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Evaluator no-signal reasons

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `2.6598360538482666` sec
- Median create→first breach: `36.95268201828003` sec
- Median create→terminal: `47.76076912879944` sec
- Median first breach→terminal: `9.476501941680908` sec
- Fast-failure buckets: `{"under_120s": {"count": 9, "pct": 100.0}, "under_180s": {"count": 9, "pct": 100.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 8, "pct": 88.9}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 0.0 | 50.0 | 0.0 | -0.331 | 34.50114858150482 | 47.256638526916504 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 100.0 | 0.0 | -1.3448 | 36.95268201828003 | 37.17920708656311 |
| SR_FLIP_RETEST | 4 | 4 | 0.0 | 100.0 | 0.0 | -0.4559 | 38.0536789894104 | 47.68157601356506 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 1.2465 | 49.31041097640991 | 62.35355806350708 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 100.0 | 38.0536789894104 | 47.68157601356506 | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 50.0 | 49.31041097640991 | 62.35355806350708 | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `9`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": -0.4559, "current_avg_pnl": -0.4559, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 38.05, "median_terminal_delta_sec": 47.68, "sl_rate_delta": 100.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 49.31, "median_terminal_delta_sec": 62.35, "sl_rate_delta": 50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
