# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `4` sec (warning=False)
- Latest performance record age: `1725` sec
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
- Total blocks in window: **3**
- Average confidence gap to threshold: **16.80** (samples=3) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ZECUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 3 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 1 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 20 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3 | 48.20 | 65.00 | 16.80 | 24.00 | 19.20 | 20.00 | 2.50 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 50.30 | 61.00 | 10.70 | 20.80 | 20.00 | 20.00 | 5.00 | 20.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 68.30 | 65.00 | -3.30 | 21.10 | 20.00 | 20.00 | 3.00 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 20 | 80.26 | 65.00 | -15.26 | 19.48 | 18.95 | 15.80 | 4.60 | 0.00 |
| TREND_PULLBACK_EMA | kept | 1 | 81.00 | 65.00 | -16.00 | 20.90 | 19.90 | 20.00 | 4.50 | -3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3 | 48.20 | 23.00 | 14.00 | 3.00 | 14.00 | 5.00 | 6.70 | 2.50 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 50.30 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 6.30 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 68.30 | 25.00 | 14.00 | 3.00 | 12.00 | 5.00 | 6.30 | 3.00 |
| MOVER_TREND_PULLBACK | kept | 20 | 80.26 | 18.60 | 18.10 | 8.03 | 14.85 | 6.40 | 9.68 | 4.60 |
| TREND_PULLBACK_EMA | kept | 1 | 81.00 | 17.00 | 18.00 | 7.50 | 14.00 | 10.00 | 10.00 | 4.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 3 | 48.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 3 | 50.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 1 | 68.30 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 20 | 80.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 1 | 81.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- _no classified invalidation records yet — engine needs to run for ~30 min after a kill before the classifier can label it_

## Suppression Quality Audit
_Every post-scoring gate-suppressed candidate is stamped with its full geometry and forward-measured on real candles: **WOULD_WIN** (TP1 before SL — the gate cost us a winner), **WOULD_LOSE** (SL first — the gate saved us), **WOULD_EXPIRE** (neither in the window).  EV in R per suppression → per-gate **KEEP / TUNE / DROP**.  This is how a gate earns its place: measured, not assumed._
- _no classified suppressed candidates yet — candidates classify after their validity window (~1h) of real candles has accumulated_

## Strategy × Context Edge Matrix
_Every strategy — live evaluators AND shadow-only units — measured per market context (session/phase/volatility/rotation) on real data.  Sources: **emitted** = realised trades, **suppressed** = gate-blocked counterfactuals, **shadow** = shadow-only units.  Edge is Wilson-lower-bounded expectancy in R — thin cells cannot fake a positive edge.  This matrix is what the allocator routes on._
_**`suppressed` here means POST-SCORING suppressions only.** `suppression_audit.feeds_edge_matrix` returns False for every pre-scoring reject — `setup_compat:*` and `execution:*` fire ahead of the scoring engine and would swamp the matrix with a differently-measured population (~38k/window against ~4.5k) that Layer C's emission floor reads LIVE.  Those candidates are measured **in the dark lane instead** (`/signals/dark-live`), and the two populations are therefore **disjoint** — every dark row carries a `setup_compat:*` or `execution:*` gate, and none of them can appear here.  A path can read positive on this table and negative in the dark feed with no contradiction, because they are not measuring the same candidates.  Stated on the surface rather than in a docstring because reading one as a check on the other is a mistake this repo has now made (2026-08-04)._
_**Every cell is a 50-outcome ring** (`STRATEGY_EDGE_WINDOW`), so `n` is `min(seen, 50)` and `seen` is the denominator: a saturated cell is a rolling most-recent-50 window while a sparse cell beside it is all-time.  `sampled` counts cells that have evicted at least once._
- Outcomes recorded: **67329 held of 148564 seen** across 21 strategies; 1500 cells past the sample floor; **626 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 28638 | 189/28449/0 | 44% | -0.15 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_RISING/MAJOR (+1.17R) | LONDON/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL/MAJOR (-1.13R) |
| MOVER_AVWAP_SCALP | 8290 | 36/8254/0 | 40% | -0.26 | ASIA/RANGE/NORMAL/BTC_RISING (+1.13R) | ASIA/RANGE/NORMAL/BTC_RISING/MAJOR (-1.23R) |
| FAILED_AUCTION_RECLAIM | 5504 | 27/5477/0 | 41% | -0.23 | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN (+1.55R) | NY/MARKUP/EXPANDED/BTC_RISING (-1.21R) |
| DIVERGENCE_CONTINUATION | 3606 | 18/3588/0 | 52% | -0.00 | NY/MARKDOWN/NORMAL/BTC_NEUTRAL (+1.04R) | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL (-1.19R) |
| SHADOW_MEAN_REVERT | 3406 | 0/0/3406 | 43% | -0.09 | ASIA/RANGE/NORMAL/BTC_RISING (+0.31R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.04R) |
| TREND_PULLBACK_EMA | 3343 | 4/3339/0 | 45% | -0.18 | ASIA/QUIET/EXPANDED/BTC_RISING (+0.54R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.24R) |
| QUIET_COMPRESSION_BREAK | 3030 | 60/2970/0 | 45% | -0.14 | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+0.77R) | ASIA/RANGE/NORMAL/BTC_RISING/ALTCOIN (-1.09R) |
| SHADOW_RANGE_FADE | 2783 | 0/0/2783 | 37% | -0.07 | LONDON/RANGE/EXPANDED/BTC_NEUTRAL (+0.47R) | OFF_HOURS/MARKUP/NORMAL/BTC_RISING (-0.88R) |
| SHADOW_FUNDING_FADE | 2241 | 0/0/2241 | 36% | -0.40 | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_RISING (+0.18R) | ASIA/QUIET/COMPRESSED/BTC_NEUTRAL (-0.93R) |
| WHALE_MOMENTUM | 2022 | 2/2020/0 | 40% | -0.39 | NY/QUIET/COMPRESSED/BTC_NEUTRAL (+0.39R) | LONDON/MARKUP/NORMAL/BTC_RISING (-1.16R) |
| LIQUIDITY_SWEEP_REVERSAL | 1099 | 6/1093/0 | 46% | -0.21 | LONDON/QUIET/COMPRESSED/BTC_NEUTRAL/ALTCOIN (+0.33R) | OVERLAP/QUIET/NORMAL/BTC_NEUTRAL (-1.14R) |
| FUNDING_EXTREME_SIGNAL | 812 | 2/810/0 | 28% | -0.55 | NY/QUIET/COMPRESSED/BTC_RISING/ALTCOIN (+0.47R) | OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL (-1.37R) |
| MEAN_REVERT | 778 | 6/772/0 | 71% | +0.39 | OFF_HOURS/MARKUP/NORMAL/BTC_FALLING (+1.16R) | OVERLAP/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP (-1.19R) |
| VOLUME_SURGE_BREAKOUT | 740 | 0/740/0 | 48% | -0.08 | NY/DISTRIBUTION/NORMAL/BTC_NEUTRAL/MAJOR (+1.00R) | NY/QUIET/COMPRESSED/BTC_NEUTRAL (-1.19R) |
| SHADOW_CASCADE_REVERSAL | 335 | 0/0/335 | 56% | -0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_FALLING (+0.20R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (-0.31R) |
| SR_FLIP_RETEST | 298 | 0/298/0 | 59% | -0.15 | ASIA/MARKDOWN/NORMAL/BTC_FALLING/ALTCOIN (+0.72R) | ASIA/MARKDOWN/COMPRESSED/BTC_FALLING (+0.25R) |
| BREAKDOWN_SHORT | 186 | 12/174/0 | 20% | -0.59 | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) | NY/VOLATILE_EXPANSION/EXPANDED/BTC_NEUTRAL (-1.09R) |
| RANGE_FADE | 132 | 0/132/0 | 26% | -0.49 | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) | OVERLAP/RANGE/NORMAL/BTC_NEUTRAL (-1.10R) |
| MA_CROSS_TREND_SHIFT | 42 | 4/38/0 | 33% | -0.23 | — | — |
| LIQUIDATION_REVERSAL | 40 | 0/40/0 | 5% | -1.07 | — | — |
| POST_DISPLACEMENT_CONTINUATION | 4 | 0/4/0 | 50% | +0.17 | — | — |

- **Strongest cells**: `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING/ALTCOIN` +1.55R (n=22, STRONG); `FAILED_AUCTION_RECLAIM @ OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING` +1.44R (n=23, STRONG); `FAILED_AUCTION_RECLAIM @ ASIA/RANGE/NORMAL/BTC_FALLING/MIDCAP` +1.44R (n=31, STRONG)
- **Weakest cells**: `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL/MIDCAP` -1.37R (n=16, NEGATIVE); `FUNDING_EXTREME_SIGNAL @ OVERLAP/VOLATILE_EXPANSION/NORMAL/BTC_NEUTRAL` -1.37R (n=16, NEGATIVE); `TREND_PULLBACK_EMA @ NY/QUIET/COMPRESSED/BTC_NEUTRAL/MIDCAP` -1.24R (n=50, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 84 | 29% / -0.52R | 84 | 45% / -0.17R | +0.35 | **ATR** |
| TREND_PULLBACK_EMA | 287 | 49% / -0.14R | 287 | 56% / -0.03R | +0.11 | **ATR** |
| WHALE_MOMENTUM | 242 | 43% / -0.35R | 242 | 45% / -0.24R | +0.10 | **ATR** |
| RANGE_FADE | 15 | 40% / +0.03R | 15 | 40% / -0.06R | -0.10 | **FIXED** |
| FAILED_AUCTION_RECLAIM | 414 | 44% / -0.18R | 414 | 46% / -0.09R | +0.09 | **ATR** |
| MOVER_AVWAP_SCALP | 625 | 47% / -0.16R | 625 | 52% / -0.08R | +0.09 | **ATR** |
| MOVER_TREND_PULLBACK | 4359 | 51% / -0.08R | 4359 | 55% / -0.01R | +0.08 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 255 | 53% / -0.15R | 255 | 58% / -0.10R | +0.05 | **ATR** |
| SR_FLIP_RETEST | 53 | 47% / -0.29R | 53 | 47% / -0.25R | +0.04 | **ATR** |
| MEAN_REVERT | 69 | 58% / +0.07R | 69 | 57% / +0.10R | +0.04 | **ATR** |
| BREAKDOWN_SHORT | 18 | 28% / -0.15R | 18 | 28% / -0.11R | +0.03 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 53 | 49% / -0.00R | 53 | 55% / +0.03R | +0.03 | **ATR** |
| DIVERGENCE_CONTINUATION | 373 | 54% / -0.01R | 373 | 59% / -0.03R | -0.02 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 495 | 45% / -0.17R | 495 | 45% / -0.18R | -0.00 | **FIXED** |
| MA_CROSS_TREND_SHIFT | 14 | 36% / -0.23R | 14 | 36% / -0.18R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 4 | 50% / -0.03R | 4 | 50% / +0.02R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 4 | 25% / -0.64R | 4 | 50% / -0.20R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6561 | 32% | -0.18R | 276 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 625 | 49% | -0.07R | 153 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 35 | 57% | +0.01R | 31 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 83 | 36% / -0.22R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 467 | 38% / +0.02R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5461 | 37% / -0.11R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 740 | 36% / +0.03R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 318 | 37% / -0.04R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 413 | 41% / +0.11R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 370 | 37% / -0.13R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 257 | 46% / -0.13R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 76 | 29% / -0.43R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 95 | 28% / -0.72R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 60 | 53% / +0.09R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 34 | 38% / -0.15R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 14 | 43% / +0.13R | — | **MEASURING** |
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 48 | 29% / -0.40R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 19 | 16% / -0.71R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 7 | 29% / -0.44R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 7 | 43% / +0.14R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 53 · alerting: **1** · boot grace active: False
- **ALERT** `edge_reconciliation` — FAILED_AUCTION_RECLAIM realized−counterfactual=+0.50R (bound 0.3) (streak 16/6) (sustained 16 cycles)

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 3214218 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | 36 arms current, none stalled; covering 446/446 signals (100%) | 0 |
| auto_dispatch | ok | placed=0 rejected=0 skipped=0 over 0 fan-out(s) to a keyed roster (gaps: skip 0, empty-roster 2; threshold 5) | 0 |
| btc_reference | ok | BTC ref 77552.90 | 0 |
| candle_coverage | ok | 88/88 symbols with ≥20 15m candles, 88/88 updated within 45m [fresh=88; 75 Tier-1 futures + 13 promoted movers monitored] | 0 |
| candle_series_integrity | ok | merge dropped 937 dup bars, 0 undedupable; ws 0 out-of-order, 84 in-place; SAR refused 0 series | 0 |
| close_accounting | ok | no unrecorded closes | 0 |
| cohort_edge_gate | ok | all 33 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once (informational); 33 cohorts, 8 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] | 0 |
| context_emission_policy | ok | output +11 / upstream +8 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1249/1266 signals (99%) | 0 |
| dark_promotion_rules | ok | master switch off — nothing is promoted | 0 |
| dark_resolution | violating | 5 of 144 open dark rows are not being advanced (worst: NOTUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 16/120) | 16 |
| dark_sar_arms | ok | no open arms; covering 1242/1259 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 615994 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | FAILED_AUCTION_RECLAIM realized−counterfactual=+0.50R (bound 0.3) (streak 16/6) | 16 |
| emission_controller | ok | last cycle 5s ago; live_overrides=13 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=1 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4442 stamps (MEAN_REVERT=673, MOVER_AVWAP_SCALP=286, MOVER_TREND_PULLBACK=3203, RANGE_FADE=122, TREND_PULLBACK_EMA=158), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | ok | 167 evaluated, 0 suppressed, 167 shadow-rejected; live rules: profile_reject | 0 |
| footprint_bars | ok | 4800 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +14 / upstream +68 | 0 |
| indicator_cache_key | ok | 837 frozen value(s) avoided; 0 hit(s) on buckets at the 1000-bar cap; 0 undatable (0 of them at the cap) | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | violating | 63 detections since last emission (emitted_total=3) — and the POST-SCORING blocked candidates measure +0.38R over n=772, so that gating is COSTING us. Check gate rejections — but confirm the output is actually being stopped post-scoring before loosening anything: pre-scoring rejects are a different, disjoint population measured in the dark lane. (streak 1/6) | 1 |
| mean_revert_path | ok | output +7 / upstream +68 | 0 |
| mover_admission_metadata | ok | 885 symbols known, 181 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 13 held, 13 with scan counts, 13 with an activity reading (measuring only) | 0 |
| paper_dispatch | ok | opened=0 of 0 considered, skipped=0 over 0 fan-out(s) to a paper roster (0 with no paper users); reasons: none recorded | 0 |
| position_lock_integrity | ok | 3 locked / 3 active symbol(s) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2912 rows held, 939287 evicted (sampled: execution:trigger_not_confirmed 400/343991, execution:overextended 400/325338, setup_compat:regime_STRONG_TREND 400/126714) | 0 |
| price_action_lane | ok | 12727 evaluated, 68 emitted; layer1 68 stamped / 0 blind; cooldown=2167, delta_opposed=1508, no_footprint=5094, no_opposing_target=136, no_sweep=2466, rr_below_floor=1288 | 0 |
| promoted_pair_integrity | ok | 13/13 promoted pairs present in universe | 0 |
| range_fade_emission | ok | disabled by tunable | 0 |
| range_fade_path | unknown | counter unavailable | 0 |
| sar_alignment_crosscheck | ok | disabled by tunable | 0 |
| sar_exit_shadow | unknown | counter unavailable | 0 |
| sar_hold_arm | ok | 746 held arms settled, 130 unscored, 34 still walking (32 awaiting the second arm) | 0 |
| sar_ledger_candles | ok | disabled by tunable | 0 |
| sar_live_arms | ok | 35 arms current, none stalled; covering 455/455 signals (100%) | 0 |
| sar_refresh_budget | ok | disabled by tunable | 0 |
| sar_resolution_progress | ok | disabled by tunable | 0 |
| scan_cycle | ok | last 19.16s, worst 238.97s over 152 lifetime cycles; lifetime 44 over 60s, 8 over 120s (plus 2/0 during boot warm-up, not counted); recent 9/3 warn/kill breaches in 20/20 cycles; heartbeat age 0.25s; 8 executor workers | 0 |
| setup_tf_resolver | ok | 7784 resolutions, 5018 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 6m ago | 0 |
| snapshot_writer | ok | last cycle 3s ago (122.45s to run, worst 186.77s), 147 overrun(s) of 323 cycles, TTL 900s; slowest agents=18.62s, alerts=13.42s, activity=11.05s | 0 |
| stale_tf_scoring | ok | no new known-stale timeframe reached scoring (lifetime scored=0, gate reads=0, withheld=0) | 0 |
| staleness_v2_shadow | ok | counter reset | 0 |
| strategy_edge | ok | output +43 / upstream +68 | 0 |
| structural_snap | ok | 4487/4487 measured, 10 blind, 0 levels moved (refusals: redetect_cooldown=35) | 0 |
| structural_veto_lane | ok | 92 stamped; 0 with no readable level book, 4 with clear air ahead, 72 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +68 / upstream +8 | 0 |
| tuned_variants | ok | seen=352 stamped=69 skipped=281, residue 2 (atr_arm_uncomputable=2) | 0 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `199054`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `3`
- `confidence_gate` events: `28`
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
- Median create→dispatch: `26.07864201068878` sec
- Median create→first breach: `4398.302906870842` sec
- Median create→terminal: `4486.891098499298` sec
- Median first breach→terminal: `7.504577994346619` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 1, "pct": 2.3}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 1, "pct": 2.3}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.8218178374932741 | 2.805967560065922 | 0.29288215914868476 | 0 | 1 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 0.9407657759284316 | 2.003913894324852 | 0.4276335427968836 | 0 | 3 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 1.4451539264283912 | 1.657329598506068 | 0.8719773832139763 | 0 | 1 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 2.1004807780953287 | 3.0 | 0.7001602593651096 | 0 | 1 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 6.412488157243262 | 2.9015186378103075 | 2.223310349998406 | 2 | 0 |
| MEAN_REVERT | 2 | 2 | 1.3005401382458435 | 1.4500587998081444 | 0.898418570140052 | 0 | 2 |
| MOVER_AVWAP_SCALP | 2 | 2 | 2.099013543000913 | 2.0928571381881316 | 1.020594234493043 | 1 | 1 |
| MOVER_TREND_PULLBACK | 22 | 22 | 3.889360553659072 | 2.99558679306963 | 1.5565604959815682 | 17 | 5 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 1.2003523273934569 | 1.3995926680244346 | 0.8672055114397222 | 0 | 7 |
| TREND_PULLBACK_EMA | 1 | 1 | 1.7914714869196584 | 2.359859484777518 | 0.7591432873337177 | 0 | 1 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -2.806 | 6433.605622053146 | 6434.844428062439 |
| DIVERGENCE_CONTINUATION | 3 | 3 | 33.3 | 0.0 | 33.3 | 0.0 | 0.7577 | 14689.432482004166 | 14694.795946836472 |
| FAILED_AUCTION_RECLAIM | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.4452 | 2636.649889945984 | 2645.1426799297333 |
| FUNDING_EXTREME_SIGNAL | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -3.0 | 154.92280292510986 | 163.05007004737854 |
| MA_CROSS_TREND_SHIFT | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -4.1503 | 13500.121307015419 | 13504.579006552696 |
| MEAN_REVERT | 2 | 2 | 50.0 | 50.0 | 50.0 | 0.0 | 0.594 | 5229.149108052254 | 5233.393733024597 |
| MOVER_AVWAP_SCALP | 2 | 2 | 0.0 | 100.0 | 0.0 | 0.0 | -2.0929 | 2121.5367670059204 | 2134.791955590248 |
| MOVER_TREND_PULLBACK | 22 | 22 | 0.0 | 54.5 | 0.0 | 0.0 | -0.6058 | 3585.8692005872726 | 3592.148777484894 |
| QUIET_COMPRESSION_BREAK | 9 | 9 | 55.6 | 11.1 | 55.6 | 0.0 | 1.4796 | 19727.404280900955 | 19732.56434392929 |
| TREND_PULLBACK_EMA | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 3.413 | 1653.8505549430847 | 1668.9301080703735 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | 1653.8505549430847 | 1668.9301080703735 | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `-1`
- Quality changes: `{"DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 1.7454, "current_avg_pnl": 0.7577, "current_win_rate": 33.3, "previous_avg_pnl": -0.9877, "previous_win_rate": 0.0, "win_rate_delta": 33.3}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": -1.0905, "current_avg_pnl": -0.6058, "current_win_rate": 0.0, "previous_avg_pnl": 0.4847, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": 3.0558, "current_avg_pnl": 1.4796, "current_win_rate": 55.6, "previous_avg_pnl": -1.5762, "previous_win_rate": 0.0, "win_rate_delta": 55.6}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 1653.85, "median_terminal_delta_sec": 1668.93, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
