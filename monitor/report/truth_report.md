# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `1664` sec
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
- Total blocks in window: **4**
- Average confidence gap to threshold: **0.80** (samples=4) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HYPEUSDT=4

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 4 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 11 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 1 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 4 | 64.20 | 65.00 | 0.80 | 23.42 | 19.90 | 20.00 | 5.00 | 6.00 |
| MOVER_TREND_PULLBACK | kept | 11 | 72.91 | 65.00 | -7.91 | 21.15 | 19.79 | 15.80 | 4.41 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 75.70 | 65.00 | -10.70 | 21.60 | 20.00 | 20.00 | 0.00 | 4.30 |
| SR_FLIP_RETEST | kept | 2 | 70.20 | 65.00 | -5.20 | 18.35 | 19.40 | 15.20 | 2.50 | 4.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 4 | 64.20 | 25.00 | 14.00 | 3.00 | 12.00 | 8.50 | 2.70 | 5.00 |
| MOVER_TREND_PULLBACK | kept | 11 | 72.91 | 17.73 | 18.00 | 7.50 | 12.09 | 5.00 | 8.18 | 4.41 |
| QUIET_COMPRESSION_BREAK | kept | 1 | 75.70 | 25.00 | 18.00 | 9.00 | 14.00 | 5.00 | 9.00 | 0.00 |
| SR_FLIP_RETEST | kept | 2 | 70.20 | 25.00 | 18.00 | 3.00 | 11.00 | 9.00 | 5.70 | 2.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 4 | 64.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 11 | 72.91 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| QUIET_COMPRESSION_BREAK | kept | 1 | 75.70 | 0.00 | 0.00 | 0.00 | 0.00 | 4.30 | 0.00 | 0.00 | 0.00 | **4.30** |
| SR_FLIP_RETEST | kept | 2 | 70.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- Totals: WOULD_WIN=1582 (35.1%) | WOULD_LOSE=963 | WOULD_EXPIRE=1963 | pending (awaiting window)=492

| Gate | n | WOULD_WIN% | Saved R | Missed R | EV/suppression (R) | Verdict |
|---|---:|---:|---:|---:|---:|---|
| context_floor:DIVERGENCE_CONTINUATION | 63 | 54.0% | 6.0 | 48.6 | -0.68 | **DROP** |
| context_floor:FAILED_AUCTION_RECLAIM | 730 | 9.2% | 6.0 | 134.0 | -0.18 | **TUNE** |
| context_floor:LIQUIDITY_SWEEP_REVERSAL | 9 | 0.0% | 0.0 | 0.0 | +0.00 | **INSUFFICIENT_SAMPLE** |
| context_floor:MEAN_REVERT | 13 | 0.0% | 13.0 | 0.0 | +1.00 | **INSUFFICIENT_SAMPLE** |
| context_floor:MOVER_TREND_PULLBACK | 744 | 24.3% | 400.0 | 237.9 | +0.22 | **KEEP** |
| context_floor:QUIET_COMPRESSION_BREAK | 446 | 6.1% | 4.0 | 67.5 | -0.14 | **TUNE** |
| context_floor:SR_FLIP_RETEST | 114 | 38.6% | 69.0 | 57.6 | +0.10 | **TUNE** |
| context_floor:VOLUME_SURGE_BREAKOUT | 1 | 0.0% | 1.0 | 0.0 | +1.00 | **INSUFFICIENT_SAMPLE** |
| dispatch_cooldown | 32 | 31.2% | 0.0 | 3.5 | -0.11 | **TUNE** |
| dispatch_staleness | 1035 | 90.0% | 98.0 | 618.9 | -0.50 | **DROP** |
| level_still_in_play | 363 | 22.6% | 3.0 | 54.0 | -0.14 | **TUNE** |
| min_confidence | 589 | 18.7% | 218.0 | 218.0 | -0.00 | **TUNE** |
| quiet_scalp_block | 139 | 12.9% | 18.0 | 32.0 | -0.10 | **TUNE** |
| shadow_unit:SHADOW_CASCADE_REVERSAL | 10 | 40.0% | 3.0 | 3.1 | -0.01 | **INSUFFICIENT_SAMPLE** |
| shadow_unit:SHADOW_FUNDING_FADE | 52 | 19.2% | 42.0 | 7.5 | +0.66 | **KEEP** |
| shadow_unit:SHADOW_MEAN_REVERT | 89 | 18.0% | 63.0 | 26.3 | +0.41 | **KEEP** |
| shadow_unit:SHADOW_RANGE_FADE | 79 | 59.5% | 19.0 | 160.1 | -1.79 | **DROP** |

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
- Outcomes recorded: 39020 across 20 strategies; 880 cells past the sample floor

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 9898 | 25/9873/0 | 63% | +0.22 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (+1.27R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SR_FLIP_RETEST | 7173 | 2/7171/0 | 43% | -0.06 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.28R) | LONDON/MARKDOWN/EXPANDED/BTC_FALLING (-1.00R) |
| FAILED_AUCTION_RECLAIM | 6558 | 14/6544/0 | 52% | +0.04 | NY/RANGE/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.86R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| DIVERGENCE_CONTINUATION | 3770 | 5/3765/0 | 45% | +0.03 | OVERLAP/MARKUP/EXPANDED/BTC_NEUTRAL (+1.46R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-1.00R) |
| QUIET_COMPRESSION_BREAK | 2720 | 0/2720/0 | 47% | +0.08 | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (+2.21R) | OFF_HOURS/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_MEAN_REVERT | 2095 | 0/0/2095 | 33% | -0.14 | OVERLAP/MARKDOWN/NORMAL/BTC_NEUTRAL (+0.91R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| SHADOW_RANGE_FADE | 1872 | 0/0/1872 | 37% | +0.21 | OVERLAP/MARKUP/NORMAL/BTC_NEUTRAL (+1.78R) | ASIA/QUIET/NORMAL/BTC_FALLING (-1.00R) |
| LIQUIDITY_SWEEP_REVERSAL | 1473 | 1/1472/0 | 32% | -0.18 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | ASIA/QUIET/NORMAL/BTC_NEUTRAL (-1.00R) |
| SHADOW_FUNDING_FADE | 1080 | 0/0/1080 | 33% | -0.41 | ASIA/MARKUP/EXPANDED/BTC_NEUTRAL (+0.60R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL (-1.00R) |
| VOLUME_SURGE_BREAKOUT | 550 | 6/544/0 | 33% | -0.24 | OVERLAP/MARKUP/CASCADE/BTC_FALLING (+1.22R) | ASIA/DISTRIBUTION/NORMAL/BTC_NEUTRAL (-1.00R) |
| TREND_PULLBACK_EMA | 421 | 0/421/0 | 38% | -0.14 | ASIA/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.27R) | OFF_HOURS/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.89R) |
| MEAN_REVERT | 372 | 0/372/0 | 8% | -0.90 | ASIA/RANGE/NORMAL/BTC_NEUTRAL (+0.15R) | NY/RANGE/NORMAL/BTC_NEUTRAL (-1.00R) |
| WHALE_MOMENTUM | 232 | 0/232/0 | 54% | -0.06 | NY/MARKUP/CASCADE/BTC_NEUTRAL (+0.34R) | OVERLAP/MARKDOWN/CASCADE/BTC_FALLING (-1.00R) |
| FUNDING_EXTREME_SIGNAL | 208 | 0/208/0 | 39% | -0.03 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.24R) | ASIA/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.00R) |
| MOVER_AVWAP_SCALP | 191 | 6/185/0 | 20% | -0.61 | LONDON/MARKUP/CASCADE/BTC_FALLING (-0.91R) | ASIA/MARKUP/CASCADE/BTC_FALLING (-1.00R) |
| BREAKDOWN_SHORT | 183 | 1/182/0 | 68% | +0.51 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+1.58R) | LONDON/MARKDOWN/NORMAL/BTC_NEUTRAL (-0.34R) |
| SHADOW_CASCADE_REVERSAL | 155 | 0/0/155 | 46% | -0.10 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.20R) | ASIA/MARKUP/NORMAL/BTC_NEUTRAL (-0.87R) |
| RANGE_FADE | 60 | 0/60/0 | 100% | +4.76 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+4.10R) |
| POST_DISPLACEMENT_CONTINUATION | 7 | 0/7/0 | 0% | -1.00 | — | — |
| MA_CROSS_TREND_SHIFT | 2 | 1/1/0 | 50% | +0.35 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +4.10R (n=24, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +4.10R (n=24, STRONG); `QUIET_COMPRESSION_BREAK @ OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL` +2.21R (n=29, STRONG)
- **Weakest cells**: `MEAN_REVERT @ NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/ALTCOIN` -1.00R (n=42, NEGATIVE); `MEAN_REVERT @ NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL` -1.00R (n=42, NEGATIVE); `MOVER_TREND_PULLBACK @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN` -1.00R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| MOVER_AVWAP_SCALP | 32 | 38% / -0.19R | 32 | 47% / -0.03R | +0.16 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 18 | 44% / +0.02R | 18 | 39% / -0.10R | -0.12 | **FIXED** |
| WHALE_MOMENTUM | 17 | 29% / -0.23R | 17 | 24% / -0.31R | -0.08 | **FIXED** |
| SR_FLIP_RETEST | 983 | 45% / -0.06R | 983 | 49% / -0.01R | +0.05 | **ATR** |
| MEAN_REVERT | 33 | 9% / -0.87R | 33 | 6% / -0.90R | -0.04 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 819 | 50% / +0.01R | 819 | 48% / +0.05R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 177 | 50% / +0.01R | 177 | 56% / -0.02R | -0.02 | **FIXED** |
| LIQUIDITY_SWEEP_REVERSAL | 153 | 44% / -0.07R | 153 | 50% / -0.05R | +0.02 | **ATR** |
| QUIET_COMPRESSION_BREAK | 438 | 44% / +0.00R | 438 | 44% / +0.01R | +0.01 | **ATR** |
| MOVER_TREND_PULLBACK | 745 | 62% / +0.14R | 745 | 67% / +0.14R | +0.00 | **ATR** |
| TREND_PULLBACK_EMA | 14 | 64% / +0.06R | 14 | 64% / +0.12R | — | **MEASURING** |
| BREAKDOWN_SHORT | 7 | 29% / -0.27R | 7 | 29% / -0.18R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 2 | 0% / -1.00R | 2 | 100% / +0.22R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 1 | 0% / -0.64R | 1 | 0% / -1.00R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 1 | 0% / +0.00R | 1 | 0% / +0.00R | — | **MEASURING** |
| RANGE_FADE | 3 | 100% / +4.79R | 3 | 100% / +3.83R | — | **MEASURING** |

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 14 · alerting: **2** · boot grace active: False
- **ALERT** `mean_revert_emission` — 7409 detections since last emission (emitted_total=1) — check gate rejections (streak 115/6) (sustained 115 cycles)
- **ALERT** `range_fade_emission` — 339 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 146/6) (sustained 146 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| auto_dispatch | ok | attempts=6 fanouts=6 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 65538.90 | 0 |
| candle_coverage | ok | 84/85 symbols with ≥20 15m candles | 0 |
| context_emission_policy | ok | output +61 / upstream +35 | 0 |
| geometry_ab | ok | output +6 / upstream +62 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 7409 detections since last emission (emitted_total=1) — check gate rejections (streak 115/6) | 115 |
| mean_revert_path | ok | output +70 / upstream +62 | 0 |
| range_fade_emission | violating | 339 detections since last emission/context-block (emitted_total=0 context_blocked=0) — check gate rejections (streak 146/6) | 146 |
| range_fade_path | violating | upstream +62 but output +0 (streak 1/72) | 1 |
| shadow_units | ok | last shadow stamp 1m ago | 0 |
| strategy_edge | ok | output +21 / upstream +62 | 0 |
| suppression_audit | ok | output +62 / upstream +35 | 0 |
| tuned_variants | ok | seen=67 stamped=6 skipped=61 | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `1570`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `4`
- `confidence_gate` events: `18`
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
- Median create→dispatch: `5.2495951652526855` sec
- Median create→first breach: `3296.384621143341` sec
- Median create→terminal: `3298.547014951706` sec
- Median first breach→terminal: `1.3792369365692139` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.0945 | 955.5695118904114 | 955.982095003128 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 50.0 | 50.0 | 50.0 | 0.0 | 0.4137 | 4764.473424077034 | 4765.964086532593 |
| MOVER_TREND_PULLBACK | 7 | 7 | 0.0 | 85.7 | 0.0 | 0.0 | -2.3005 | 1737.139463186264 | 1740.7229549884796 |
| SR_FLIP_RETEST | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | -0.2872 | 6738.941568493843 | 6740.6963675022125 |
| VOLUME_SURGE_BREAKOUT | 3 | 3 | 0.0 | 100.0 | 0.0 | 0.0 | -1.498 | 3434.54390501976 | 3435.939390897751 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 50.0 | 50.0 | 6738.941568493843 | 6740.6963675022125 | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `-2`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.013, "current_avg_pnl": 0.4137, "current_win_rate": 50.0, "previous_avg_pnl": 0.4007, "previous_win_rate": 25.0, "win_rate_delta": 25.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.1254, "current_avg_pnl": -2.3005, "current_win_rate": 0.0, "previous_avg_pnl": -1.1751, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "VOLUME_SURGE_BREAKOUT": {"avg_pnl_delta": -1.498, "current_avg_pnl": -1.498, "current_win_rate": 0.0, "previous_avg_pnl": null, "previous_win_rate": null, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 6345.67, "median_terminal_delta_sec": 6346.03, "sl_rate_delta": -50.0, "win_rate_delta": 50.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
