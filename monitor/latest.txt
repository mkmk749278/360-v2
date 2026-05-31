# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `26` sec (warning=False)
- Latest performance record age: `745` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Evaluator no-signal reasons
- _no reject-reason data parsed from logs in this window — see Log parse diagnostics below_

## Regime distribution
- _no regime data parsed — engine may need redeploy to start emitting `Regime distribution (last 100 cycles): ...` log lines_

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **130**
- Average confidence gap to threshold: **16.92** (samples=130) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: INJUSDT=16, 1000PEPEUSDT=12, ETHUSDT=8, DOGEUSDT=7, HEIUSDT=7, PENGUUSDT=6, ADAUSDT=6, ALGOUSDT=6, TAOUSDT=5, HIVEUSDT=5

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | quiet_scalp_min_confidence | 3 |
| BREAKDOWN_SHORT | kept | min_confidence_pass | 1 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 5 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 5 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 25 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 5 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 22 |
| FUNDING_EXTREME_SIGNAL | filtered | quiet_scalp_min_confidence | 4 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 2 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 15 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 1 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 14 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 78 |
| SR_FLIP_RETEST | filtered | min_confidence | 12 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 83 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 3 |
| VOLUME_SURGE_BREAKOUT | filtered | quiet_scalp_min_confidence | 3 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 41.70 | 65.00 | 23.30 | 21.20 | 19.70 | 20.00 | 0.00 | 24.60 |
| BREAKDOWN_SHORT | kept | 1 | 65.30 | 65.00 | -0.30 | 21.20 | 19.70 | 20.00 | 0.00 | 3.00 |
| DIVERGENCE_CONTINUATION | filtered | 6 | 62.77 | 65.00 | 2.23 | 20.75 | 19.08 | 18.10 | 4.33 | 3.00 |
| DIVERGENCE_CONTINUATION | kept | 5 | 70.92 | 65.00 | -5.92 | 20.44 | 19.74 | 17.74 | 3.00 | -0.22 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 49.90 | 65.00 | 15.10 | 20.26 | 19.38 | 20.00 | 4.30 | 10.49 |
| FAILED_AUCTION_RECLAIM | kept | 22 | 68.94 | 65.00 | -3.94 | 20.23 | 19.95 | 20.00 | 4.43 | 0.03 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 41.10 | 65.00 | 23.90 | 21.00 | 20.00 | 20.00 | 2.33 | 12.27 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 16 | 56.22 | 65.00 | 8.78 | 20.34 | 19.56 | 18.01 | 3.31 | 2.70 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 69.27 | 65.00 | -4.27 | 21.61 | 18.59 | 17.68 | 1.43 | 0.00 |
| SR_FLIP_RETEST | filtered | 90 | 48.19 | 65.00 | 16.81 | 20.94 | 19.97 | 15.65 | 2.37 | 11.89 |
| SR_FLIP_RETEST | kept | 83 | 70.93 | 65.00 | -5.93 | 20.57 | 19.98 | 15.64 | 2.37 | -0.24 |
| TREND_PULLBACK_EMA | kept | 1 | 71.20 | 65.00 | -6.20 | 21.00 | 19.90 | 20.00 | 5.50 | -3.00 |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 50.45 | 65.00 | 14.55 | 22.50 | 19.85 | 19.75 | 2.75 | 3.00 |
| WHALE_MOMENTUM | filtered | 1 | 46.90 | 65.00 | 18.10 | 20.60 | 20.00 | 17.00 | 0.00 | 21.60 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 41.70 | 25.00 | 8.00 | 6.00 | 17.00 | 5.00 | 5.30 | 0.00 |
| BREAKDOWN_SHORT | kept | 1 | 65.30 | 17.00 | 18.00 | 6.00 | 17.00 | 5.00 | 5.30 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 6 | 62.77 | 21.00 | 16.33 | 4.00 | 12.83 | 6.00 | 7.27 | 4.33 |
| DIVERGENCE_CONTINUATION | kept | 5 | 70.92 | 23.40 | 16.00 | 4.80 | 11.40 | 5.00 | 8.90 | 3.00 |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 49.90 | 20.33 | 14.27 | 7.10 | 11.10 | 7.60 | 6.19 | 4.30 |
| FAILED_AUCTION_RECLAIM | kept | 22 | 68.94 | 21.73 | 14.36 | 6.27 | 11.18 | 6.39 | 4.60 | 4.43 |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 41.10 | 25.00 | 8.00 | 3.00 | 14.00 | 7.33 | 8.70 | 2.33 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 16 | 56.22 | 24.00 | 14.00 | 6.56 | 12.94 | 6.06 | 5.17 | 3.31 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 69.27 | 23.86 | 14.00 | 4.71 | 14.00 | 4.43 | 6.84 | 1.43 |
| SR_FLIP_RETEST | filtered | 90 | 48.19 | 23.76 | 9.33 | 6.10 | 14.76 | 5.82 | 6.03 | 2.37 |
| SR_FLIP_RETEST | kept | 83 | 70.93 | 23.70 | 13.78 | 4.16 | 14.81 | 6.48 | 6.46 | 2.37 |
| TREND_PULLBACK_EMA | kept | 1 | 71.20 | 17.00 | 18.00 | 3.00 | 14.00 | 5.00 | 8.70 | 5.50 |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 50.45 | 25.00 | 8.00 | 3.00 | 14.00 | 9.00 | 6.70 | 2.75 |
| WHALE_MOMENTUM | filtered | 1 | 46.90 | 17.00 | 8.00 | 12.00 | 17.00 | 8.50 | 6.00 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 3 | 41.70 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |
| BREAKDOWN_SHORT | kept | 1 | 65.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 6 | 62.77 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 5 | 70.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 30 | 49.90 | 0.00 | 0.00 | 0.00 | 0.00 | 8.16 | 0.00 | 0.00 | 0.00 | **8.16** |
| FAILED_AUCTION_RECLAIM | kept | 22 | 68.94 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FUNDING_EXTREME_SIGNAL | filtered | 6 | 41.10 | 0.00 | 0.00 | 12.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **12.27** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 16 | 56.22 | 0.00 | 0.00 | 0.00 | 0.00 | 2.70 | 0.00 | 0.00 | 0.00 | **2.70** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 14 | 69.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 90 | 48.19 | 0.00 | 0.00 | 0.21 | 0.00 | 9.60 | 0.00 | 0.00 | 0.59 | **10.40** |
| SR_FLIP_RETEST | kept | 83 | 70.93 | 0.00 | 0.00 | 0.00 | 0.00 | 0.29 | 0.00 | 0.00 | 0.00 | **0.29** |
| TREND_PULLBACK_EMA | kept | 1 | 71.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 6 | 50.45 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 1 | 46.90 | 0.00 | 0.00 | 0.00 | 0.00 | 21.60 | 0.00 | 0.00 | 0.00 | **21.60** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=240 (71.0%) | PREMATURE=48 (14.2%) | NEUTRAL=50 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=1
- **Net-helping** — invalidation saved on 192 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| adverse_excursion | 28 | 5 | 1 | 0 |
| ema_crossover | 6 | 0 | 1 | 0 |
| momentum_loss | 102 | 22 | 17 | 0 |
| regime_shift | 64 | 10 | 28 | 0 |
| trailing_invalidation | 40 | 11 | 3 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 4 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 26 | 5 | 4 | 0 |
| FAILED_AUCTION_RECLAIM | 47 | 3 | 19 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 56 | 13 | 8 | 0 |
| SR_FLIP_RETEST | 96 | 26 | 16 | 0 |
| TREND_PULLBACK_EMA | 5 | 1 | 0 | 0 |
| VOLUME_SURGE_BREAKOUT | 5 | 0 | 1 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 1 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| adverse_excursion | 28 | 5 | 1 | 9.3 | 9.5 | -0.01 | **TUNE** — marginal: avg -0.01R/kill across 34 kills — consider per-setup exemption or threshold adjustment, not full drop |
| ema_crossover | 6 | 0 | 1 | 3.9 | 0.0 | +0.55 | **INSUFFICIENT_SAMPLE** — only 7 classified kills (need >= 20); let data accumulate before tuning |
| momentum_loss | 102 | 22 | 17 | 77.2 | 30.1 | +0.34 | **KEEP** — net-helping: avg +0.33R/kill across 141 kills (saved 77.2R vs missed 30.1R) |
| regime_shift | 64 | 10 | 28 | 44.5 | 14.6 | +0.29 | **KEEP** — net-helping: avg +0.29R/kill across 102 kills (saved 44.5R vs missed 14.6R) |
| trailing_invalidation | 40 | 11 | 3 | 34.4 | 16.9 | +0.32 | **KEEP** — net-helping: avg +0.32R/kill across 54 kills (saved 34.4R vs missed 16.9R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1762`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `130`
- `confidence_gate` events: `284`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `3`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- Total fires in window: **3**
- Avg resolved threshold: **0.301%** raw → avg net **+2.31%** @ 10x
- Avg time-to-fire from dispatch: **302s**
- By threshold source: stamped=3

| Setup | Fires | Avg threshold (raw) | Avg net @ 10x | Avg age (s) | Source mix |
|---|---:|---:|---:|---:|---|
| SR_FLIP_RETEST | 3 | 0.301% | +2.31% | 302 | stamped=3 |
- Top symbols: OPGUSDT=1, PRLUSDT=1, VTHOUSDT=1

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **0**
- Total REST-fallback activations: **0**

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| pre_tp | 3 |
| signal_close | 3 |

- By severity: HIGH=6

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `26.868343949317932` sec
- Median create→first breach: `338.9999829530716` sec
- Median create→terminal: `308.97185707092285` sec
- Median first breach→terminal: `6.125003933906555` sec
- Fast-failure buckets: `{"under_120s": {"count": 14, "pct": 25.9}, "under_180s": {"count": 17, "pct": 31.5}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 10, "pct": 18.5}}`
- ~3 minute terminal-close behavior: `{"count": 14, "pct": 11.9}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 8 | 8 | 0.0 | 25.0 | 0.0 | 0.0 | -0.0917 | 129.0734269618988 | 152.36802506446838 |
| FAILED_AUCTION_RECLAIM | 26 | 26 | 0.0 | 3.8 | 0.0 | 0.0 | 0.0843 | 217.65610599517822 | 195.07098042964935 |
| LIQUIDITY_SWEEP_REVERSAL | 25 | 25 | 0.0 | 24.0 | 0.0 | 0.0 | -0.1376 | 375.78646445274353 | 428.6507683992386 |
| POST_DISPLACEMENT_CONTINUATION | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.1076 | 49.208515882492065 | 51.54991579055786 |
| SR_FLIP_RETEST | 57 | 57 | 0.0 | 8.8 | 0.0 | 5.3 | -0.0444 | 660.1046800613403 | 440.1979138851166 |
| TREND_PULLBACK_EMA | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | -0.5383 | 823.9151701927185 | 854.0845869779587 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 8.8 | 660.1046800613403 | 440.1979138851166 | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 50.0 | 823.9151701927185 | 854.0845869779587 | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `7`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": -0.3987, "current_avg_pnl": -0.0917, "current_win_rate": 0.0, "previous_avg_pnl": 0.307, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1652, "current_avg_pnl": 0.0843, "current_win_rate": 0.0, "previous_avg_pnl": -0.0809, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "LIQUIDITY_SWEEP_REVERSAL": {"avg_pnl_delta": -0.387, "current_avg_pnl": -0.1376, "current_win_rate": 0.0, "previous_avg_pnl": 0.2494, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": -0.0568, "current_avg_pnl": -0.0444, "current_win_rate": 0.0, "previous_avg_pnl": 0.0124, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": 0.372, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.372, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 159.82, "median_terminal_delta_sec": -99.09, "sl_rate_delta": 0.2, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 720.1, "median_terminal_delta_sec": 319.3, "sl_rate_delta": 50.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
