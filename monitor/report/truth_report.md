# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `1` sec (warning=False)
- Latest performance record age: `1044` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Lifecycle truth summary
- Median create→dispatch: `1.557157039642334` sec
- Median create→first breach: `183.88034391403198` sec
- Median create→terminal: `187.31129384040833` sec
- Median first breach→terminal: `0.9470198154449463` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 5, "pct": 100.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | -0.7362 | 186.36427402496338 | 187.31129384040833 |
| SR_FLIP_RETEST | 10 | 10 | 0.0 | 80.0 | 0.0 | -0.2145 | 182.4664249420166 | 188.1073089838028 |
| TREND_PULLBACK_EMA | 14 | 14 | 0.0 | 71.4 | 0.0 | 0.0308 | 183.5238515138626 | 186.9035724401474 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `0`
- Quality changes: `{"SR_FLIP_RETEST": {"avg_pnl_delta": 0.0763, "current_avg_pnl": -0.2145, "current_win_rate": 0.0, "previous_avg_pnl": -0.2908, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"avg_pnl_delta": -0.1975, "current_avg_pnl": 0.0308, "current_win_rate": 0.0, "previous_avg_pnl": 0.2283, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
