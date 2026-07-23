# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `7466` sec
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
- Totals: WOULD_WIN=1705 (42.7%) | WOULD_LOSE=713 | WOULD_EXPIRE=1578 | pending (awaiting window)=1004

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 295 | 18.0% | 217.1 | 72.9 | +0.49 | **KEEP** |
| context_floor:FAILED_AUCTION_RECLAIM | 143 | 2.8% | 100.9 | 7.4 | +0.65 | **KEEP** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 10 | 0.0% | 17.9 | 0.0 | +1.79 | **INSUFFICIENT_SAMPLE** |
| context_floor:QUIET_COMPRESSION_BREAK | 28 | 0.0% | 10.1 | 0.0 | +0.36 | **KEEP** |
| context_floor:TREND_PULLBACK_EMA | 2 | 0.0% | 2.3 | 0.0 | +1.17 | **INSUFFICIENT_SAMPLE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 9 | 0.0% | 10.1 | 0.0 | +1.13 | **INSUFFICIENT_SAMPLE** |
| data_stale | 6 | 0.0% | 6.1 | 0.0 | +1.02 | **INSUFFICIENT_SAMPLE** |
| dispatch_staleness | 1297 | 73.6% | 43.9 | 686.7 | -0.50 | **DROP** |
| level_still_in_play | 1014 | 46.7% | 97.3 | 197.5 | -0.10 | **TUNE** |
| min_confidence | 867 | 15.9% | 365.5 | 198.5 | +0.19 | **KEEP** |
| quiet_scalp_block | 101 | 4.0% | 31.6 | 3.8 | +0.28 | **KEEP** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 6 | 33.3% | 0.1 | 1.4 | -0.21 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 53 | 43.4% | 25.7 | 16.3 | +0.18 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 92 | 26.1% | 73.6 | 31.4 | +0.46 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 73 | 38.4% | 44.1 | 73.6 | -0.40 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 54428 across 20 strategies; 1243 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 14041 | 44/13997/0 | 62% | +0.20 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | OVERLAP/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.13R) |
| FAILED_AUCTION_RECLAIM | 10018 | 20/9998/0 | 50% | +0.03 | LONDON/MARKDOWN/EXPANDED/BTC_NEUTRAL (+1.70R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (-1.19R) |
| SR_FLIP_RETEST | 8450 | 2/8448/0 | 42% | -0.12 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN (+1.14R) | OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN (-1.20R) |
| DIVERGENCE_CONTINUATION | 4822 | 5/4817/0 | 45% | -0.01 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | OFF_HOURS/MARKUP/NORMAL/BTC_NEUTRAL (-1.19R) |
| QUIET_COMPRESSION_BREAK | 3895 | 0/3895/0 | 45% | +0.01 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+1.95R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| SHADOW_MEAN_REVERT | 2520 | 0/0/2520 | 34% | -0.14 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.61R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| SHADOW_RANGE_FADE | 2206 | 0/0/2206 | 35% | +0.15 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.61R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| MEAN_REVERT | 2153 | 0/2153/0 | 77% | +0.54 | OFF_HOURS/QUIET/COMPRESSED/BTC_NEUTRAL (+1.27R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-1.05R) |
| LIQUIDITY_SWEEP_REVERSAL | 1763 | 3/1760/0 | 37% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL/MIDCAP (-1.17R) |
| SHADOW_FUNDING_FADE | 1368 | 0/0/1368 | 33% | -0.41 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 943 | 8/935/0 | 39% | -0.10 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 593 | 0/593/0 | 42% | -0.16 | OFF_HOURS/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.36R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| RANGE_FADE | 546 | 0/546/0 | 11% | -0.39 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.21R) |
| WHALE_MOMENTUM | 242 | 0/242/0 | 55% | -0.04 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 239 | 5/234/0 | 54% | +0.31 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | NY/QUIET/COMPRESSED/BTC_RISING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 236 | 0/236/0 | 42% | +0.12 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 211 | 10/201/0 | 19% | -0.63 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| SHADOW_CASCADE_REVERSAL | 173 | 0/0/173 | 47% | -0.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.16R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +1.95R (n=34, STRONG)
- **Weakest cells**: `RANGE_FADE @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.21R (n=31, NEGATIVE); `RANGE_FADE @ LONDON/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.21R (n=31, NEGATIVE); `SR_FLIP_RETEST @ OVERLAP/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.20R (n=38, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| VOLUME_SURGE_BREAKOUT | 25 | 44% / +0.02R | 25 | 32% / -0.22R | -0.24 | **FIXED** |
| TREND_PULLBACK_EMA | 21 | 52% / -0.12R | 21 | 57% / +0.07R | +0.19 | **ATR** |
| MOVER_AVWAP_SCALP | 40 | 42% / -0.08R | 40 | 55% / +0.09R | +0.17 | **ATR** |
| RANGE_FADE | 19 | 16% / -0.10R | 19 | 16% / -0.25R | -0.15 | **FIXED** |
| MEAN_REVERT | 108 | 56% / +0.10R | 108 | 54% / +0.22R | +0.12 | **ATR** |
| WHALE_MOMENTUM | 20 | 35% / -0.16R | 20 | 30% / -0.26R | -0.10 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 191 | 44% / -0.13R | 191 | 52% / -0.05R | +0.08 | **ATR** |
| SR_FLIP_RETEST | 1116 | 45% / -0.07R | 1116 | 49% / -0.02R | +0.05 | **ATR** |
| MOVER_TREND_PULLBACK | 1207 | 63% / +0.17R | 1207 | 66% / +0.13R | -0.04 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 1169 | 50% / +0.01R | 1169 | 49% / +0.02R | +0.01 | **ATR** |
| QUIET_COMPRESSION_BREAK | 559 | 45% / -0.01R | 559 | 45% / -0.02R | -0.01 | **FIXED** |
| DIVERGENCE_CONTINUATION | 255 | 49% / -0.01R | 255 | 54% / -0.01R | +0.00 | **ATR** |
| BREAKDOWN_SHORT | 8 | 25% / -0.27R | 8 | 25% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 3 | 0% / -1.05R | 3 | 67% / -0.00R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0% / +0.00R | 1 | 0% / +0.00R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 16 · alerting: **3** · boot grace active: False
- **ALERT** `edge_reconciliation` — MOVER_TREND_PULLBACK realized−counterfactual=-0.35R (bound 0.3) (streak 110/6) (sustained 110 cycles)
- **ALERT** `mean_revert_emission` — 3084 detections since last emission (emitted_total=1) — check gate rejections (streak 28/6) (sustained 28 cycles)
- **ALERT** `tuned_variants` — 10 unexplained non-stamps (seen=154 stamped=1 skipped=143) (streak 66/6) (sustained 66 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=13 fanouts=13 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 65700.80 | 0 |
| candle_coverage | ok | 91/95 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +51 / upstream +33 | 0 |
| edge_reconciliation | violating | MOVER_TREND_PULLBACK realized−counterfactual=-0.35R (bound 0.3) (streak 110/6) | 110 |
| emission_controller | ok | last cycle 937s ago; live_overrides=11 | 0 |
| geometry_ab | ok | output +4 / upstream +51 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 3084 detections since last emission (emitted_total=1) — check gate rejections (streak 28/6) | 28 |
| mean_revert_path | ok | output +104 / upstream +51 | 0 |
| range_fade_emission | violating | 305 detections since last emission/context-block (emitted_total=0 context_blocked=135) — check gate rejections (streak 3/6) | 3 |
| range_fade_path | ok | output +100 / upstream +51 | 0 |
| shadow_units | ok | last shadow stamp 3m ago | 0 |
| strategy_edge | ok | output +189 / upstream +51 | 0 |
| suppression_audit | ok | output +51 / upstream +33 | 0 |
| tuned_variants | violating | 10 unexplained non-stamps (seen=154 stamped=1 skipped=143) (streak 66/6) | 66 |
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
- Median create→dispatch: `4.665199041366577` sec
- Median create→first breach: `2003.1093089580536` sec
- Median create→terminal: `2004.9683470726013` sec
- Median first breach→terminal: `1.3506219387054443` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 2.9}, "under_180s": {"count": 2, "pct": 5.7}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 2.9}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.9}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 2 | 2 | 100.0 | 0.0 | 100.0 | 0.0 | 7.4564 | 24048.455218553543 | 24052.408754587173 |
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0945 | 955.5695118904114 | 955.982095003128 |
| FAILED_AUCTION_RECLAIM | 5 | 5 | 20.0 | 40.0 | 20.0 | 0.0 | 0.1497 | 2712.8399591445923 | 2714.6704070568085 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 33.59271788597107 | 34.02080702781677 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 50.0 | 0.0 | 0.0 | 1.2237 | 4394.78203189373 | 4399.9005600214 |
| MOVER_TREND_PULLBACK | 20 | 20 | 0.0 | 55.0 | 0.0 | 0.0 | -1.3135 | 1619.785208582878 | 1620.7989770174026 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 1.0244 | 9530.649816036224 | 9532.028242111206 |
| VOLUME_SURGE_BREAKOUT | 3 | 3 | 0.0 | 66.7 | 0.0 | 0.0 | -1.0499 | 3698.725870847702 | 3700.213966846466 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 100.0 | 0.0 | 9530.649816036224 | 9532.028242111206 | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1627, "current_avg_pnl": 0.1497, "current_win_rate": 20.0, "previous_avg_pnl": -0.013, "previous_win_rate": 33.3, "win_rate_delta": -13.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.311, "current_avg_pnl": -1.3135, "current_win_rate": 0.0, "previous_avg_pnl": -1.6245, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": 0.2945, "current_avg_pnl": -1.0499, "current_win_rate": 0.0, "previous_avg_pnl": -1.3444, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 7360.4, "median_terminal_delta_sec": 7360.01, "sl_rate_delta": -100.0, "win_rate_delta": 100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
