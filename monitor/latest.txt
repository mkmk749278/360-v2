# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: none
- Top promising signals/paths: none
- Recommended next investigation target: **none**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `100` sec (warning=False)
- Latest performance record age: `27722` sec
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
- Total blocks in window: **30**
- Average confidence gap to threshold: **13.04** (samples=30) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: ETHUSDT=7, ADAUSDT=6, ZECUSDT=4, BTCUSDT=3, BNBUSDT=3, XLMUSDT=2, AAVEUSDT=1, XMRUSDT=1, DOTUSDT=1, ONDOUSDT=1

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 12 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 2 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 11 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 6 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 7 |
| MA_CROSS_TREND_SHIFT | filtered | min_confidence | 1 |
| MEAN_REVERT | filtered | min_confidence | 5 |
| MEAN_REVERT | filtered | quiet_scalp_min_confidence | 1 |
| MEAN_REVERT | kept | min_confidence_pass | 3 |
| MOVER_AVWAP_SCALP | filtered | min_confidence | 12 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 24 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 100 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 263 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 19 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 37 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 1 |
| TREND_PULLBACK_EMA | filtered | min_confidence | 2 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 7 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 5 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 1 |
| WHALE_MOMENTUM | filtered | quiet_scalp_min_confidence | 8 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 14 | 56.74 | 64.64 | 7.90 | 20.83 | 19.74 | 16.54 | 0.93 | 10.43 |
| DIVERGENCE_CONTINUATION | kept | 11 | 69.60 | 65.00 | -4.60 | 20.00 | 19.50 | 17.19 | 1.55 | -1.91 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 72.50 | 65.00 | -7.50 | 20.07 | 19.42 | 20.00 | 2.25 | -0.67 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 7 | 70.64 | 65.00 | -5.64 | 20.73 | 19.17 | 17.71 | 2.29 | 0.00 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.50 | 61.00 | 3.50 | 21.20 | 18.30 | 15.80 | 0.00 | 0.00 |
| MEAN_REVERT | filtered | 6 | 54.05 | 60.83 | 6.78 | 22.20 | 18.73 | 15.20 | 0.00 | 0.00 |
| MEAN_REVERT | kept | 3 | 69.90 | 65.00 | -4.90 | 21.07 | 17.93 | 16.63 | 0.00 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 12 | 57.96 | 62.00 | 4.04 | 20.40 | 17.30 | 15.80 | 3.96 | 13.25 |
| MOVER_AVWAP_SCALP | kept | 24 | 74.60 | 65.00 | -9.60 | 20.90 | 16.04 | 15.80 | 4.02 | 0.86 |
| MOVER_TREND_PULLBACK | filtered | 100 | 55.46 | 63.67 | 8.21 | 20.19 | 18.64 | 15.80 | 4.41 | 15.52 |
| MOVER_TREND_PULLBACK | kept | 263 | 76.42 | 65.00 | -11.42 | 20.66 | 18.91 | 15.80 | 4.35 | 1.15 |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 48.92 | 65.00 | 16.08 | 20.76 | 19.79 | 20.00 | 0.00 | 12.09 |
| QUIET_COMPRESSION_BREAK | kept | 37 | 76.39 | 65.00 | -11.39 | 20.46 | 19.86 | 20.00 | 0.00 | -0.74 |
| SR_FLIP_RETEST | kept | 1 | 76.50 | 65.00 | -11.50 | 21.20 | 20.00 | 15.20 | 2.50 | -3.00 |
| TREND_PULLBACK_EMA | filtered | 2 | 40.00 | 61.00 | 21.00 | 21.20 | 19.00 | 15.30 | 6.00 | 12.00 |
| TREND_PULLBACK_EMA | kept | 7 | 77.53 | 65.00 | -12.53 | 21.11 | 19.84 | 17.97 | 4.71 | 0.93 |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 55.60 | 62.60 | 7.00 | 21.20 | 16.66 | 20.00 | 3.30 | 2.40 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.50 | 65.00 | -14.50 | 21.20 | 17.20 | 20.00 | 5.50 | 3.00 |
| WHALE_MOMENTUM | filtered | 8 | 55.64 | 65.00 | 9.36 | 20.16 | 14.00 | 17.00 | 0.00 | 12.50 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 14 | 56.74 | 18.71 | 13.00 | 6.21 | 13.86 | 5.25 | 9.21 | 0.93 |
| DIVERGENCE_CONTINUATION | kept | 11 | 69.60 | 22.82 | 10.73 | 6.00 | 14.09 | 5.64 | 9.05 | 1.55 |
| FAILED_AUCTION_RECLAIM | kept | 6 | 72.50 | 20.67 | 18.00 | 6.50 | 11.50 | 4.58 | 9.83 | 2.25 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 7 | 70.64 | 21.86 | 15.14 | 5.57 | 12.43 | 6.50 | 6.86 | 2.29 |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.50 | 17.00 | 14.00 | 9.00 | 14.00 | 8.50 | 10.00 | 0.00 |
| MEAN_REVERT | filtered | 6 | 54.05 | 23.67 | 18.00 | 5.00 | 12.00 | 5.08 | 5.30 | 0.00 |
| MEAN_REVERT | kept | 3 | 69.90 | 22.33 | 15.33 | 7.00 | 12.00 | 6.67 | 6.57 | 0.00 |
| MOVER_AVWAP_SCALP | filtered | 12 | 57.96 | 18.33 | 18.00 | 9.62 | 12.17 | 6.88 | 7.25 | 3.96 |
| MOVER_AVWAP_SCALP | kept | 24 | 74.60 | 18.25 | 18.00 | 11.06 | 13.75 | 6.75 | 9.25 | 4.02 |
| MOVER_TREND_PULLBACK | filtered | 100 | 55.46 | 18.50 | 18.02 | 8.38 | 14.14 | 5.78 | 8.50 | 4.41 |
| MOVER_TREND_PULLBACK | kept | 263 | 76.42 | 19.27 | 18.04 | 7.96 | 13.39 | 5.70 | 9.20 | 4.35 |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 48.92 | 17.42 | 18.00 | 11.21 | 14.32 | 6.37 | 3.17 | 0.00 |
| QUIET_COMPRESSION_BREAK | kept | 37 | 76.39 | 18.51 | 17.68 | 11.59 | 14.41 | 6.74 | 8.18 | 0.00 |
| SR_FLIP_RETEST | kept | 1 | 76.50 | 25.00 | 8.00 | 9.00 | 17.00 | 5.00 | 10.00 | 2.50 |
| TREND_PULLBACK_EMA | filtered | 2 | 40.00 | 2.00 | 18.00 | 9.00 | 17.00 | 9.00 | 6.00 | 6.00 |
| TREND_PULLBACK_EMA | kept | 7 | 77.53 | 19.29 | 18.00 | 7.50 | 14.00 | 6.86 | 8.53 | 4.71 |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 55.60 | 18.60 | 14.00 | 12.00 | 13.40 | 7.00 | 4.70 | 3.30 |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.50 | 25.00 | 14.00 | 12.00 | 11.00 | 5.00 | 10.00 | 5.50 |
| WHALE_MOMENTUM | filtered | 8 | 55.64 | 18.00 | 8.00 | 11.25 | 13.75 | 8.31 | 8.82 | 0.00 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 14 | 56.74 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 11 | 69.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 6 | 72.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 7 | 70.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MA_CROSS_TREND_SHIFT | filtered | 1 | 57.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | filtered | 6 | 54.05 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MEAN_REVERT | kept | 3 | 69.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | filtered | 12 | 57.96 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 3.25 | **3.25** |
| MOVER_AVWAP_SCALP | kept | 24 | 74.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.25 | **0.25** |
| MOVER_TREND_PULLBACK | filtered | 100 | 55.46 | 0.00 | 0.00 | 1.04 | 0.00 | 1.32 | 0.00 | 0.00 | 0.00 | **2.36** |
| MOVER_TREND_PULLBACK | kept | 263 | 76.42 | 0.00 | 0.00 | 0.44 | 0.00 | 0.22 | 0.00 | 0.00 | 0.00 | **0.66** |
| QUIET_COMPRESSION_BREAK | filtered | 19 | 48.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.09 | **9.09** |
| QUIET_COMPRESSION_BREAK | kept | 37 | 76.39 | 0.00 | 0.00 | 0.00 | 0.00 | 0.35 | 0.00 | 0.00 | 0.29 | **0.64** |
| SR_FLIP_RETEST | kept | 1 | 76.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | filtered | 2 | 40.00 | 0.00 | 0.00 | 0.00 | 0.00 | 12.00 | 0.00 | 0.00 | 0.00 | **12.00** |
| TREND_PULLBACK_EMA | kept | 7 | 77.53 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | filtered | 5 | 55.60 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 1 | 79.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| WHALE_MOMENTUM | filtered | 8 | 55.64 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

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
- Outcomes recorded: **145630 held of 316961 seen** across 21 strategies; 3268 cells past the sample floor; **1393 cells have evicted** (saturated rings — their stats describe the most recent 50 only)

| Strategy | n | emit/supp/shadow | Win% | Avg R | Best context (edge) | Worst context (edge) |
|---|---:|---|---:|---:|---|---|
| MOVER_TREND_PULLBACK | 34226 | 184/34042/0 | 49% | -0.06 | NY/MARKDOWN/EXPANDED/BTC_RISING (+1.22R) | LONDON/QUIET/EXPANDED/BTC_NEUTRAL/ALTCOIN (-1.16R) |
| FAILED_AUCTION_RECLAIM | 17408 | 20/17388/0 | 52% | +0.01 | ASIA/MARKUP/EXPANDED/BTC_FALLING/MIDCAP (+1.73R) | ASIA/MARKUP/COMPRESSED/BTC_NEUTRAL/ALTCOIN (-1.19R) |
| SR_FLIP_RETEST | 16600 | 1/16599/0 | 48% | -0.18 | NY/MARKDOWN/NORMAL/BTC_RISING/MIDCAP (+1.20R) | OFF_HOURS/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/MIDCAP (-1.30R) |
| DIVERGENCE_CONTINUATION | 12454 | 6/12448/0 | 45% | -0.10 | OVERLAP/MARKUP/COMPRESSED/BTC_NEUTRAL/MIDCAP (+1.32R) | OVERLAP/RANGE/EXPANDED/BTC_FALLING/MIDCAP (-1.19R) |
| MOVER_AVWAP_SCALP | 10327 | 30/10297/0 | 36% | -0.31 | LONDON/DISTRIBUTION/EXPANDED/BTC_RISING (+1.12R) | LONDON/MARKUP/CASCADE/BTC_FALLING (-1.22R) |
| QUIET_COMPRESSION_BREAK | 9882 | 0/9882/0 | 46% | -0.09 | ASIA/RANGE/NORMAL/BTC_RISING (+1.16R) | NY/RANGE/NORMAL/BTC_NEUTRAL/MIDCAP (-1.19R) |
| TREND_PULLBACK_EMA | 6164 | 4/6160/0 | 46% | -0.26 | NY/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+1.07R) | OFF_HOURS/MARKUP/COMPRESSED/BTC_FALLING/ALTCOIN (-1.19R) |
| SHADOW_MEAN_REVERT | 5562 | 0/0/5562 | 43% | -0.11 | NY/MARKDOWN/COMPRESSED/BTC_NEUTRAL (+0.56R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL (-0.96R) |
| LIQUIDITY_SWEEP_REVERSAL | 5220 | 11/5209/0 | 46% | -0.20 | ASIA/ACCUMULATION/NORMAL/BTC_FALLING (+1.53R) | OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL (-1.64R) |
| SHADOW_RANGE_FADE | 5120 | 0/0/5120 | 38% | -0.01 | ASIA/MARKUP/CASCADE/BTC_NEUTRAL (+0.57R) | LONDON/QUIET/NORMAL/BTC_RISING (-1.41R) |
| MEAN_REVERT | 4928 | 6/4922/0 | 68% | +0.30 | NY/DISTRIBUTION/EXPANDED/BTC_NEUTRAL/ALTCOIN (+1.28R) | LONDON/QUIET/NORMAL/BTC_NEUTRAL/MAJOR (-1.54R) |
| SHADOW_FUNDING_FADE | 4686 | 0/0/4686 | 37% | -0.36 | ASIA/VOLATILE_EXPANSION/COMPRESSED/BTC_NEUTRAL (+0.22R) | OFF_HOURS/QUIET/COMPRESSED/BTC_FALLING (-1.02R) |
| RANGE_FADE | 4147 | 0/4147/0 | 33% | -0.36 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+3.60R) | ASIA/RANGE/NORMAL/BTC_NEUTRAL (-1.38R) |
| VOLUME_SURGE_BREAKOUT | 2681 | 19/2662/0 | 41% | +0.02 | NY/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+2.68R) | OFF_HOURS/ACCUMULATION/NORMAL/BTC_NEUTRAL (-1.19R) |
| FUNDING_EXTREME_SIGNAL | 2642 | 4/2638/0 | 32% | -0.46 | ASIA/MARKDOWN/NORMAL/BTC_NEUTRAL/ALTCOIN (+1.16R) | OVERLAP/VOLATILE_EXPANSION/COMPRESSED/BTC_FALLING (-1.29R) |
| WHALE_MOMENTUM | 2154 | 0/2154/0 | 46% | -0.28 | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MIDCAP (+0.52R) | OVERLAP/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/MAJOR (-0.89R) |
| SHADOW_CASCADE_REVERSAL | 643 | 0/0/643 | 49% | -0.16 | LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.05R) | OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL (-2.04R) |
| BREAKDOWN_SHORT | 537 | 11/526/0 | 45% | +0.04 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.67R) | LONDON/RANGE/NORMAL/BTC_NEUTRAL (-1.08R) |
| LIQUIDATION_REVERSAL | 128 | 0/128/0 | 33% | -0.81 | ASIA/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL (+0.02R) | NY/VOLATILE_EXPANSION/NORMAL/BTC_FALLING (-1.17R) |
| POST_DISPLACEMENT_CONTINUATION | 75 | 0/75/0 | 83% | +0.64 | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) | OFF_HOURS/MARKUP/EXPANDED/BTC_NEUTRAL (+0.89R) |
| MA_CROSS_TREND_SHIFT | 46 | 1/45/0 | 37% | -0.36 | — | — |

- **Strongest cells**: `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL` +3.60R (n=28, STRONG); `RANGE_FADE @ LONDON/VOLATILE_EXPANSION/CASCADE/BTC_NEUTRAL/ALTCOIN` +3.60R (n=28, STRONG); `RANGE_FADE @ LONDON/MARKUP/NORMAL/BTC_NEUTRAL/MIDCAP` +3.19R (n=19, STRONG)
- **Weakest cells**: `SHADOW_CASCADE_REVERSAL @ OVERLAP/MARKUP/CASCADE/BTC_NEUTRAL` -2.04R (n=17, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL/MIDCAP` -1.64R (n=24, NEGATIVE); `LIQUIDITY_SWEEP_REVERSAL @ OFF_HOURS/ACCUMULATION/EXPANDED/BTC_NEUTRAL` -1.64R (n=24, NEGATIVE)

## Stop-Geometry A/B (fixed-% vs ATR/structure stops)
_Every post-scoring candidate (emitted AND suppressed) is stamped as a counterfactual pair — its live fixed-% stop vs an ATR/structure stop beyond the liquidity pool — and both arms are forward-measured identically.  R-units normalise per-arm risk, so constant-dollar-risk sizing is inherent.  Observe-only: a leader here changes nothing live until the geometry ships dark-first with owner sign-off._

| Strategy | n fixed | Win%/R fixed | n ATR | Win%/R ATR | ΔR (ATR−fixed) | Leader |
|---|---:|---|---:|---|---:|---|
| FUNDING_EXTREME_SIGNAL | 146 | 37% / -0.36R | 146 | 58% / -0.09R | +0.27 | **ATR** |
| TREND_PULLBACK_EMA | 298 | 42% / -0.31R | 298 | 49% / -0.11R | +0.20 | **ATR** |
| MOVER_AVWAP_SCALP | 751 | 39% / -0.22R | 751 | 43% / -0.10R | +0.12 | **ATR** |
| SR_FLIP_RETEST | 2788 | 46% / -0.20R | 2788 | 49% / -0.10R | +0.11 | **ATR** |
| DIVERGENCE_CONTINUATION | 1062 | 47% / -0.12R | 1062 | 52% / -0.06R | +0.07 | **ATR** |
| LIQUIDITY_SWEEP_REVERSAL | 817 | 51% / -0.17R | 817 | 55% / -0.12R | +0.06 | **ATR** |
| MOVER_TREND_PULLBACK | 4576 | 51% / -0.07R | 4576 | 54% / -0.01R | +0.06 | **ATR** |
| MA_CROSS_TREND_SHIFT | 18 | 39% / -0.20R | 18 | 39% / -0.16R | +0.03 | **ATR** |
| RANGE_FADE | 290 | 23% / -0.56R | 290 | 26% / -0.52R | +0.03 | **ATR** |
| WHALE_MOMENTUM | 191 | 51% / -0.25R | 191 | 51% / -0.28R | -0.03 | **FIXED** |
| QUIET_COMPRESSION_BREAK | 1694 | 45% / -0.13R | 1694 | 45% / -0.16R | -0.03 | **FIXED** |
| MEAN_REVERT | 566 | 52% / -0.04R | 566 | 48% / -0.02R | +0.02 | **ATR** |
| VOLUME_SURGE_BREAKOUT | 100 | 41% / -0.04R | 100 | 52% / -0.03R | +0.02 | **ATR** |
| BREAKDOWN_SHORT | 24 | 38% / -0.17R | 24 | 38% / -0.17R | +0.00 | **ATR** |
| FAILED_AUCTION_RECLAIM | 2365 | 47% / -0.11R | 2365 | 47% / -0.11R | +0.00 | **ATR** |
| POST_DISPLACEMENT_CONTINUATION | 11 | 55% / -0.01R | 11 | 55% / +0.01R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 8 | 25% / -0.94R | 8 | 50% / -0.27R | — | **MEASURING** |

## Recipe & rescue shadow arms (@TUNED / @DSV2 / @GOV)
_Dark-first evidence rows for pending live flips: **@TUNED** = tuned recipes for measured losers incl. the MOVER_TREND_PULLBACK perfect-entry study (limit at the pulled-back fast MA, fill-aware — a retest that never comes scores 0R, never a fantasy win); **@DSV2** = dispatch-staleness V2 rescues (V1 blocked, geometry-aware V2 would pass; entry re-anchored at dispatch-time price); **@GOV** = STRONG-cell overrides of the two audited-negative gates.  Compare each arm's avg R against its base strategy row in the edge matrix above; a MEASURED arm sustaining positive net R is the sign-off evidence for its flag (`dispatch_staleness_v2_live` / `context_emission_gate_override_live`)._

| Strategy | Arm | n | Win% | Avg R | Cells | Status |
|---|---|---:|---:|---:|---:|---|
| MOVER_TREND_PULLBACK | @TUNED | 6788 | 29% | -0.18R | 294 | MEASURED |
| MOVER_AVWAP_SCALP | @TUNED | 741 | 43% | -0.10R | 148 | MEASURED |
| VOLUME_SURGE_BREAKOUT | @TUNED | 47 | 57% | +0.03R | 26 | MEASURED |

## SAR exit A/B (live geometry vs a trailing 15m Parabolic SAR)
_The 102,496-entry exit-method bake-off ranked SAR-on-15m the only profitable trailing exit (PF 1.60 vs SuperTrend 0.93 / ATR 0.72).  A backtest verdict is not a promotion, so every post-scoring candidate now stamps a pair — **@SARBASE** (the live evaluator geometry) and **@SAREXIT** (the same entry exited by the trail) — forward-measured over the SAME 192-bar (48h) window and divided by the same live stop distance, so the comparison carries no hold-time confound.  Observe-only and default-OFF; adopting a SAR exit stays a separate dark-first, owner-signed change._

| Strategy | n live | Win%/R live | n SAR | Win%/R SAR | ΔR (SAR−live) | Leader |
|---|---:|---|---:|---|---:|---|
| SR_FLIP_RETEST | 0 | 0% / +0.00R | 1250 | 29% / -1.66R | — | **MEASURING** |
| BREAKDOWN_SHORT | 0 | 0% / +0.00R | 36 | 31% / -0.30R | — | **MEASURING** |
| MOVER_TREND_PULLBACK | 0 | 0% / +0.00R | 5779 | 39% / -0.11R | — | **MEASURING** |
| FAILED_AUCTION_RECLAIM | 0 | 0% / +0.00R | 1081 | 32% / -0.52R | — | **MEASURING** |
| VOLUME_SURGE_BREAKOUT | 0 | 0% / +0.00R | 128 | 24% / -0.82R | — | **MEASURING** |
| DIVERGENCE_CONTINUATION | 0 | 0% / +0.00R | 935 | 33% / -1.20R | — | **MEASURING** |
| QUIET_COMPRESSION_BREAK | 0 | 0% / +0.00R | 1260 | 35% / -0.16R | — | **MEASURING** |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0% / +0.00R | 480 | 44% / -0.71R | — | **MEASURING** |
| FUNDING_EXTREME_SIGNAL | 0 | 0% / +0.00R | 180 | 32% / -0.94R | — | **MEASURING** |
| TREND_PULLBACK_EMA | 0 | 0% / +0.00R | 357 | 31% / -0.56R | — | **MEASURING** |
| MOVER_AVWAP_SCALP | 0 | 0% / +0.00R | 860 | 32% / -0.36R | — | **MEASURING** |
| MA_CROSS_TREND_SHIFT | 0 | 0% / +0.00R | 23 | 17% / -0.70R | — | **MEASURING** |
| MEAN_REVERT | 0 | 0% / +0.00R | 295 | 45% / -0.11R | — | **MEASURING** |
| RANGE_FADE | 0 | 0% / +0.00R | 111 | 39% / -0.13R | — | **MEASURING** |
| POST_DISPLACEMENT_CONTINUATION | 0 | 0% / +0.00R | 9 | 33% / -0.50R | — | **MEASURING** |
| LIQUIDATION_REVERSAL | 0 | 0% / +0.00R | 9 | 22% / -1.09R | — | **MEASURING** |
| WHALE_MOMENTUM | 0 | 0% / +0.00R | 68 | 41% / -0.28R | — | **MEASURING** |

## Gate rejections by setup (why a path never emits)
_The per-gate table above pools every setup into one row, so it cannot answer the question the emission probes tell you to ask: *this path emits nothing — which gate is stopping it, and is that gate right?*  Both fields were always on the stamped records; this cross-tabs them.  EV is from the **suppression's** perspective: positive = the gate saved money on this path, negative = it is destroying value here._
- _no classified suppressions yet_

## Feature Liveness & Fail-Open Telemetry
_Every measurement pipeline's output rate is compared against its upstream driver each 5-min audit cycle (the systemic answer to the 2026-07-14 eight-features-dead-silently incident).  Sustained violations and growing fail-open exception counters page via the monitor's INVARIANT_WARN path — this section is the same manifest, rendered for the session-start read._
- Probes: 48 · alerting: **0** · boot grace active: False

| Feature | Status | Detail | Streak |
|---|---|---|---:|
| aggtrade_feed | ok | 40 fed / 0 quiet / 0 never delivered of 40 subscribed; 988181 accepted, 0 rejected | 0 |
| atr_trail_live_arms | ok | no open arms; covering 149/149 signals (100%) | 0 |
| auto_dispatch | ok | attempts=0 fanouts=0 (gaps: skip 0, empty-roster 0; threshold 5) | 0 |
| btc_reference | ok | BTC ref 64380.50 | 0 |
| candle_coverage | ok | 81/81 symbols with ≥20 15m candles, 79/81 updated within 45m | 0 |
| candle_series_integrity | ok | merge dropped 1568 dup bars, 0 undedupable; ws 0 out-of-order, 184 in-place; SAR refused 0 series | 0 |
| cohort_edge_gate | violating | all 28 cohorts share macro_dir=DECLINE — a macro flip resets every cohort at once; 28 cohorts, 11 holding stale-only evidence, expiry=14d, macro_dirs=['DECLINE'] (streak 3/6) | 3 |
| context_emission_policy | ok | output +14 / upstream +5 | 0 |
| dark_atr_trail_arms | ok | no open arms; covering 1101/1114 signals (99%) | 0 |
| dark_promotion_rules | ok | 1 rule(s) armed, nothing promoted and nothing refused — no candidate has reached the decision yet | 0 |
| dark_resolution | violating | 2 of 63 open dark rows are not being advanced (worst: PROMUSDT 0 missed cycles, no fresh bars) — their outcomes on the ops page describe bars that stopped arriving (streak 3/120) | 3 |
| dark_sar_arms | ok | no open arms; covering 1093/1106 signals (99%) | 0 |
| depth_feed | ok | 40/40 books fresh (stale 0, never 0, thin 0); 274647 msgs, 0 rejected | 0 |
| edge_reconciliation | violating | MOVER_AVWAP_SCALP realized−counterfactual=+0.53R (bound 0.3) (streak 3/6) | 3 |
| emission_controller | ok | last cycle 1215s ago; live_overrides=26 | 0 |
| emission_controller_routability | ok | measuring; dead_overrides=14 wasted_promotions=0 pruned=0 | 0 |
| entry_feature_inputs | ok | 4228 stamps (MEAN_REVERT=617, MOVER_AVWAP_SCALP=142, MOVER_TREND_PULLBACK=2873, RANGE_FADE=416, TREND_PULLBACK_EMA=180), no declared feature wholly absent; set aside 3 undeclared (extension_pct,funding_rate,stack_sep_pct) | 0 |
| entry_quality_effective | violating | entry-quality gate is over its blast-radius cap (70/92 recent decisions rejected, cap 0.35) — suppression is held back and the rule reads as passing (streak 3/6) | 3 |
| footprint_bars | ok | 2560 sealed bars over 40 symbols; 0 incomplete, 0 shape-capped | 0 |
| gate_override_shadow | ok | output +0 / upstream +0 | 0 |
| geometry_ab | ok | output +3 / upstream +37 | 0 |
| market_context | ok | publishing with ATR percentile | 0 |
| mean_revert_emission | ok | emitted_total=2 | 0 |
| mean_revert_path | ok | output +6 / upstream +37 | 0 |
| mover_admission_metadata | ok | 871 symbols known, 169 marked TRADIFI_PERPETUAL | 0 |
| mover_retention | ok | 4 held, 4 with scan counts, 4 with an activity reading (measuring only) | 0 |
| prescoring_audit | ok | 8 pre-scoring gates measured, 2965 rows held, 567122 evicted (sampled: execution:overextended 400/208692, execution:trigger_not_confirmed 400/195518, setup_compat:regime_STRONG_TREND 400/68792) | 0 |
| price_action_lane | ok | 3673 evaluated, 13 emitted; layer1 13 stamped / 0 blind; cooldown=261, delta_opposed=258, no_footprint=1179, no_opposing_target=27, no_sweep=1721, rr_below_floor=214 | 0 |
| promoted_pair_integrity | ok | 4/4 promoted pairs present in universe | 0 |
| range_fade_emission | ok | backlog 3 detections since last progress | 0 |
| range_fade_path | violating | upstream +37 but output +0 (streak 1/72) | 1 |
| sar_alignment_crosscheck | violating | 25/364 disagreed (6.9%) (streak 3/6) | 3 |
| sar_exit_shadow | ok | output +2 / upstream +37 | 0 |
| sar_hold_arm | ok | 261 held arms settled, 55 unscored, 0 still walking (0 awaiting the second arm) | 0 |
| sar_ledger_candles | violating | 61/114 unfetchable (54%); top cause: gap or duplicate bar in the 15m window; symbols: 1000RATSUSDT, ADAUSDT, AIOUSDT, ALPINEUSDT, APRUSDT +12 more (streak 3/6) | 3 |
| sar_live_arms | ok | no open arms; covering 158/158 signals (100%) | 0 |
| sar_refresh_budget | ok | 3 refreshed, none turned away | 0 |
| sar_resolution_progress | ok | 12 resolved, 41 still mid-window | 0 |
| setup_tf_resolver | ok | 1599 resolutions, 830 would move off 5m, 0 unmapped, correction dark | 0 |
| shadow_units | ok | last shadow stamp 8m ago | 0 |
| snapshot_writer | ok | last cycle 36s ago (11.57s to run, worst 134.53s), 63 overrun(s) of 113 cycles, TTL 900s; slowest positions_diag=6.33s, engine_state=5.98s, signals=5.25s | 0 |
| stale_tf_scoring | ok | no known-stale timeframe reached scoring | 0 |
| staleness_v2_shadow | ok | output +0 / upstream +0 | 0 |
| strategy_edge | ok | output +100 / upstream +37 | 0 |
| structural_snap | ok | 4205/4205 measured, 29 blind, 0 levels moved (refusals: redetect_cooldown=3) | 0 |
| structural_veto_lane | ok | 21 stamped; 0 with no readable level book, 1 with clear air ahead, 13 would-reject, 0 enforced | 0 |
| suppression_audit | ok | output +37 / upstream +5 | 0 |
| tuned_variants | violating | 25 non-stamps — atr_arm_uncomputable=25 (seen=85 stamped=17 skipped=43) (streak 3/6) | 3 |
- Fail-open exception counters: none recorded 🎉

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `31589`
- `Path funnel` emissions: `0`
- `Regime distribution` emissions: `0`
- `QUIET_SCALP_BLOCK` events: `30`
- `confidence_gate` events: `527`
- `free_channel_post` events: `2`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **34**
- Total REST-fallback activations: **14**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures | 15 | 67594 | 84408 | 85688 | 0 |
| futures_depth | 16 | 63913 | 84374 | 103198 | 0 |
| futures_liq | 3 | 24121 | 24121 | 100647 | 0 |

| Label | REST-fallback activations |
|---|---:|
| futures | 14 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **2**

| Source | Count |
|---|---:|
| regime_shift | 1 |
| signal_close | 1 |

- By severity: HIGH=2

## Dependency readiness

## Lifecycle truth summary
- Median create→dispatch: `40.49185109138489` sec
- Median create→first breach: `43.677319049835205` sec
- Median create→terminal: `45.28540802001953` sec
- Median first breach→terminal: `1.6080889701843262` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 100.0}, "under_180s": {"count": 1, "pct": 100.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 1, "pct": 100.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Stop geometry — designed vs shipped
_The evaluator authors a structural stop (for the mover paths: beyond the mid/slow MA plus an ATR buffer — where the thesis is dead).  Two stages then move it before it reaches the wire: ``predictive_ai.adjust_tp_sl`` scales the distance by a model multiplier **unless the setup is in ``_PREDICTIVE_SLTP_BYPASS_SETUPS``**, and ``_apply_noise_floor_stop`` widens it to the pair's 1h noise band.  Nothing had ever compared the two ends, so a systematic override was invisible.  ``Ratio`` = designed ÷ shipped; **>1 means the stop that was actually in the market was TIGHTER than the one the TP ladder was built from**, so the R on every other surface divides by a stop the trade never had.  ``Stamped`` leads the row and 0.0 means unknown, not 'no override' — records written before 2026-08-04 cannot be recovered and are excluded from every figure here rather than averaged in._
| Path/Setup | Rows | Stamped | Designed % | Shipped % | Ratio | Tightened | Widened |
|---|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 1 | 1 | 4.207556565926573 | 3.0 | 1.4025188553088574 | 1 | 0 |

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MOVER_TREND_PULLBACK | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -4.2076 | 43.677319049835205 | 45.28540802001953 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `0`
- Gating Δ: `0`
- No-generation Δ: `0`
- Fast failures Δ: `1`
- Quality changes: `{"MOVER_TREND_PULLBACK": {"avg_pnl_delta": -4.3787, "current_avg_pnl": -4.2076, "current_win_rate": 0.0, "previous_avg_pnl": 0.1711, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -508.47, "median_terminal_delta_sec": -509.81, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **none**
- Most promising healthy path: **none**
- Most likely bottleneck: **none**
- Suggested next investigation target: **none**
