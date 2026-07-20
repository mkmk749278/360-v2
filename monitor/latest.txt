# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=starting)
- Heartbeat age: `20` sec (warning=False)
- Latest performance record age: `8668` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|

## Evaluator no-signal reasons
- _no reject-reason data parsed from logs in this window — see Log parse diagnostics below_

## Pre-scoring gate rejects (setup-compat / execution-quality)
- _no pre-scoring gate rejects recorded in this window (counters ship 2026-07-18 — a fresh window must accumulate first)_

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
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1966 (42.9%) | WOULD_LOSE=1316 | WOULD_EXPIRE=1301 | pending (awaiting window)=417

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 55 | 1.8% | 54.0 | 1.8 | +0.95 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 435 | 8.7% | 126.0 | 76.0 | +0.11 | **KEEP** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 61 | 0.0% | 61.0 | 0.0 | +1.00 | **KEEP** |
| context_floor:MOVER_TREND_PULLBACK | 1447 | 51.3% | 432.0 | 983.9 | -0.38 | **DROP** |
| context_floor:QUIET_COMPRESSION_BREAK | 24 | 0.0% | 0.0 | 0.0 | +0.00 | **TUNE** |
| context_floor:SR_FLIP_RETEST | 718 | 56.5% | 272.0 | 536.6 | -0.37 | **DROP** |
| context_floor:TREND_PULLBACK_EMA | 12 | 100.0% | 0.0 | 21.8 | -1.82 | **INSUFFICIENT_SAMPLE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 35 | 0.0% | 35.0 | 0.0 | +1.00 | **KEEP** |
| dispatch_staleness | 439 | 93.4% | 14.0 | 229.0 | -0.49 | **DROP** |
| level_still_in_play | 327 | 56.9% | 0.0 | 91.1 | -0.28 | **DROP** |
| min_confidence | 915 | 16.7% | 294.0 | 214.6 | +0.09 | **TUNE** |
| quiet_scalp_block | 74 | 5.4% | 8.0 | 4.8 | +0.04 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 1 | 0.0% | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_MEAN_REVERT | 16 | 37.5% | 9.0 | 8.7 | +0.02 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_RANGE_FADE | 24 | 29.2% | 11.0 | 19.5 | -0.35 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 35208 across 19 strategies; 785 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 8832 | 21/8811/0 | 64% | +0.24 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 6873 | 2/6871/0 | 44% | -0.05 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.29R) | LONDON/MARKDOWN/EXPANDED/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 5981 | 13/5968/0 | 49% | -0.07 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 3555 | 3/3552/0 | 43% | -0.01 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 2024 | 0/0/2024 | 33% | -0.13 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| QUIET_COMPRESSION_BREAK | 1913 | 0/1913/0 | 41% | +0.00 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 1772 | 0/0/1772 | 36% | +0.12 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.63R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 1415 | 1/1414/0 | 32% | -0.18 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 973 | 0/0/973 | 34% | -0.40 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | ASIA/MARKDOWN/NORMAL/BTC_FALLING (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 468 | 2/466/0 | 39% | -0.19 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 361 | 0/361/0 | 44% | -0.04 | NY/MARKDOWN/NORMAL/BTC_RISING (+0.32R) | OVERLAP/MARKUP/CASCADE/BTC_RISING (-0.51R) |
| WHALE_MOMENTUM | 222 | 0/222/0 | 57% | -0.04 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| MOVER_AVWAP_SCALP | 183 | 6/177/0 | 21% | -0.59 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 183 | 1/182/0 | 68% | +0.51 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| MEAN_REVERT | 172 | 0/172/0 | 18% | -0.78 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+0.15R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 144 | 0/0/144 | 46% | -0.11 | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| FUNDING_EXTREME_SIGNAL | 128 | 0/128/0 | 40% | +0.09 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG); `FAILED_AUCTION_RECLAIM @ LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL` +1.70R (n=45, STRONG); `SHADOW_RANGE_FADE @ OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL` +1.63R (n=16, STRONG)
- **Weakest cells**: `SR_FLIP_RETEST @ LONDON/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.00R (n=50, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ ASIA/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP` -1.00R (n=50, NEGATIVE); `FAILED_AUCTION_RECLAIM @ ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.00R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 15 | 47% / +0.10R | 15 | 40% / -0.08R | -0.17 | **FIXED** |
| MOVER_AVWAP_SCALP | 27 | 44% / -0.09R | 27 | 56% / +0.07R | +0.16 | **ATR** |
| WHALE_MOMENTUM | 16 | 31% / -0.22R | 16 | 25% / -0.29R | -0.07 | **FIXED** |
| SR_FLIP_RETEST | 961 | 45% / -0.06R | 961 | 49% / -0.00R | +0.06 | **ATR** |
| MEAN_REVERT | 26 | 12% / -0.83R | 26 | 8% / -0.88R | -0.05 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 145 | 46% / -0.05R | 145 | 51% / -0.02R | +0.02 | **ATR** |
| FAILED_AUCTION_RECLAIM | 751 | 47% / -0.05R | 751 | 45% / -0.03R | +0.01 | **ATR** |
| DIVERGENCE_CONTINUATION | 162 | 49% / -0.01R | 162 | 56% / -0.02R | -0.01 | **FIXED** |
| MOVER_TREND_PULLBACK | 651 | 63% / +0.15R | 651 | 68% / +0.14R | -0.01 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 391 | 43% / -0.02R | 391 | 42% / -0.01R | +0.01 | **ATR** |
| TREND_PULLBACK_EMA | 12 | 75% / +0.13R | 12 | 75% / +0.16R | — | **MEASURING** |
| BREAKDOWN_SHORT | 7 | 29% / -0.27R | 7 | 29% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 2 | 0% / -1.00R | 2 | 100% / +0.22R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 14 · alerting: **0** · boot grace active: True

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64200.00 | 0 |
| candle_coverage | ok | 83/83 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +53 / upstream +53 | 0 |
| geometry_ab | ok | boot grace (upstream +30 but output +0 (streak 1/6)) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | boot grace (172 detections since last emission (emitted_total=0) — check gate rejections (streak 1/6)) | 0 |
| mean_revert_path | ok | output +53 / upstream +30 | 0 |
| range_fade_emission | ok | emitted_total=0 context_blocked=12 | 0 |
| range_fade_path | ok | output +11 / upstream +30 | 0 |
| shadow_units | ok | last shadow stamp 12m ago | 0 |
| strategy_edge | ok | output +120 / upstream +30 | 0 |
| suppression_audit | ok | output +30 / upstream +53 | 0 |
| tuned_variants | ok | seen=0 stamped=0 skipped=0 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `0`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `0`
- `confidence_gate` events: `0`
- `free_channel_post` events: `0`
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
- _no free-channel posts in this window_

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `3.975419044494629` sec
- Median create→first breach: `7881.606021523476` sec
- Median create→terminal: `7882.704700112343` sec
- Median first breach→terminal: `1.3788315057754517` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.1525 | 9410.783209443092 | 9413.380096077919 |
| MOVER_TREND_PULLBACK | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | 0.1153 | 2212.8765959739685 | 2463.684786081314 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.0244 | 9530.649816036224 | 9532.028242111206 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 100.0 | 0.0 | 9530.649816036224 | 9532.028242111206 | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `-1`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.5782, "current_avg_pnl": 0.1525, "current_win_rate": 50.0, "previous_avg_pnl": -0.4257, "previous_win_rate": 0.0, "win_rate_delta": 50.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 4.5455, "current_avg_pnl": 0.1153, "current_win_rate": 0.0, "previous_avg_pnl": -4.4302, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 5583.42, "median_terminal_delta_sec": 5582.66, "sl_rate_delta": -100.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
