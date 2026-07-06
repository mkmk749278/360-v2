# Runtime Truth Report

## Executive summary
- Overall health/freshness: **unhealthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=unhealthy)
- Heartbeat age: `21823` sec (warning=True)
- Latest performance record age: `21257` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Evaluator no-signal reasons
- _no reject-reason data parsed from logs in this window — see Log parse diagnostics below_

## Regime distribution
- _no regime data parsed — engine may need redeploy to start emitting `Regime distribution (last 100 cycles): ...` log lines_

## QUIET_SCALP_BLOCK gate
- _no QUIET_SCALP_BLOCK events in window_

## Confidence gate decisions
- _no confidence_gate decisions parsed in window_

## Confidence component breakdown
- _no confidence_gate component samples parsed in window — scoring telemetry may need a refresh after the next deploy_

## Scoring engine breakdown (per-dimension contribution)
- _no engine-component data parsed in window — log line predates the engine-breakdown instrumentation, will populate after redeploy_

## Soft-penalty per-type breakdown
- _no soft-penalty per-type data parsed in window — log line predates the LSR diagnosis instrumentation, will populate after redeploy_

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=95 (67.9%) | PREMATURE=15 (10.7%) | NEUTRAL=30 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 80 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 95 | 15 | 30 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 6 | 1 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 21 | 6 | 12 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 2 | 3 | 0 |
| MOVER_AVWAP_SCALP | 13 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 25 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 18 | 4 | 11 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 95 | 15 | 30 | 65.8 | 30.0 | +0.26 | **KEEP** — net-helping: avg +0.26R/kill across 140 kills (saved 65.8R vs missed 30.0R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4910`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `0`
- `confidence_gate` events: `0`
- `free_channel_post` events: `2`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **2**

| Source | Count |
|---|---:|
| regime_shift | 2 |

- By severity: HIGH=2

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `None` sec
- Median create→first breach: `None` sec
- Median create→terminal: `3600.667778968811` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | -0.1524 | None | 3600.667778968811 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Disabled

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
