# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, DIVERGENCE_CONTINUATION, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: SR_FLIP_RETEST
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `5199` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 103 | 103 | 103 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 3845 | 3845 | 3468 | 2 | active-low-quality (none) |
| EVAL::BREAKDOWN_SHORT | 44636 | 44637 | 9 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 38884 | 38887 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 38846 | 37859 | 1023 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::FAILED_AUCTION_RECLAIM | 38887 | 37113 | 1810 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 44490 | 44454 | 47 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 34859 | 34862 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 38926 | 38928 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 50448 | 50300 | 3692 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 44645 | 35725 | 14711 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 43388 | 43390 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 38886 | 38886 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 38844 | 38819 | 27 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 37734 | 33760 | 5070 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 29648 | 26896 | 2868 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 29767 | 29750 | 26 | 0 | 0 | 0 | low-sample (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 44635 | 44633 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 34861 | 34868 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 4927 | 4927 | 4374 | 13 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 524 | 524 | 450 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 12899 | 12899 | 12800 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 8666 | 8666 | 8666 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 42156 | 42156 | 41173 | 0 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 47 | 47 | 47 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 15699 | 15699 | 14451 | 3 | active-healthy (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 313 | 313 | 305 | 1 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 28 | 28 | 28 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=44637): basic_filters_failed=16041, breakout_not_found=15140, move_not_fresh=10965, breakout_stale=1999, retest_proximity_failed=418, volume_spike_missing=65, move_exhausted=8, missing_fvg_or_orderblock=1
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=38889): cls_disabled_merged_into_lsr=38889
- **EVAL::DIVERGENCE_CONTINUATION** (total=37860): h1_trend_not_aligned=16915, basic_filters_failed=10311, cvd_divergence_failed=7187, ema_alignment_reject=3009, retest_proximity_failed=316, missing_fvg_or_orderblock=122
- **EVAL::FAILED_AUCTION_RECLAIM** (total=37115): auction_not_detected=10995, reclaim_hold_failed=10844, basic_filters_failed=10173, tail_too_small=4202, regime_blocked=901
- **EVAL::FUNDING_EXTREME** (total=44456): funding_not_extreme=31643, basic_filters_failed=12295, rsi_reject=267, ema_alignment_reject=190, momentum_reject=44, cvd_divergence_failed=17
- **EVAL::LIQUIDATION_REVERSAL** (total=34862): cascade_threshold_not_met=22463, basic_filters_failed=12230, cvd_divergence_failed=89, rsi_reject=77, volume_spike_missing=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=38930): no_ma_cross=27687, basic_filters_failed=10317, ma_cross_cooldown=926
- **EVAL::MOVER_AVWAP_SCALP** (total=50300): no_avwap_tag=25354, basic_filters_failed=15766, no_mover_leg=4539, avwap_slope_against=2693, avwap_reclaim_no_volume=809, no_avwap_reclaim=616, insufficient_candles=523
- **EVAL::MOVER_TREND_PULLBACK** (total=35725): basic_filters_failed=15742, mover_run_too_small=11713, no_reclaim=6529, no_pullback_tag=1218, insufficient_candles=523
- **EVAL::OPENING_RANGE_BREAKOUT** (total=43392): feature_disabled=43392
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=38888): regime_blocked=28208, breakout_not_found=7926, basic_filters_failed=2118, adx_reject=631, ema_alignment_reject=5
- **EVAL::QUIET_COMPRESSION_BREAK** (total=38821): compression_not_detected=17728, regime_blocked=11572, basic_filters_failed=8050, breakout_not_detected=1375, volume_confirmation_failed=96
- **EVAL::SR_FLIP_RETEST** (total=33761): basic_filters_failed=10163, flip_close_not_confirmed=5358, whipsaw_flip=4593, reclaim_hold_failed=4045, retest_out_of_zone=3346, long_break_volume_thin=2727, wick_quality_failed=1545, regime_blocked=900, long_disabled=811, missing_fvg_or_orderblock=175, long_acceptance_not_held=78, ema_alignment_reject=20
- **EVAL::STANDARD** (total=26896): momentum_reject=7799, basic_filters_failed=5095, adx_reject=4420, macd_reject=3847, sweeps_not_detected=3452, ema_alignment_reject=2078, invalid_sl_geometry=196, rsi_reject=9
- **EVAL::TREND_PULLBACK** (total=29750): h1_trend_not_aligned=14605, h1_pullback_not_confirmed=8768, basic_filters_failed=2790, ema_alignment_reject=2140, ema_not_tested_prev=553, no_ema_reclaim_close=345, rsi_reject=201, body_conviction_fail=200, prev_already_above_emas=46, prev_already_below_emas=30, no_prev_high_break=27, no_prev_low_break=18, momentum_flat=15, ema21_not_tagged=11, missing_fvg_or_orderblock=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=44633): breakout_not_found=24757, basic_filters_failed=16041, move_not_fresh=1671, breakout_stale=1419, retest_proximity_failed=691, volume_spike_missing=54
- **EVAL::WHALE_MOMENTUM** (total=34868): momentum_reject=29478, recent_ticks_insufficient=4547, basic_filters_failed=843

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 99829 | 44.8% |
| TRENDING_DOWN | 58997 | 26.5% |
| QUIET | 39509 | 17.7% |
| TRENDING_UP | 15753 | 7.1% |
| VOLATILE | 8883 | 4.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **56**
- Average confidence gap to threshold: **13.36** (samples=56) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: AMDUSDT=31, BZUSDT=14, SOLUSDT=11

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 19 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 19 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 204 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 56 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 50 |
| FUNDING_EXTREME_SIGNAL | filtered | min_confidence | 74 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 28 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 972 |
| SR_FLIP_RETEST | filtered | min_confidence | 181 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 3 |
| TREND_PULLBACK_EMA | kept | min_confidence_pass | 1 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 57.06 | 65.00 | 7.94 | 20.68 | 19.36 | 17.92 | 0.42 | 14.62 |
| DIVERGENCE_CONTINUATION | kept | 19 | 70.92 | 65.00 | -5.92 | 21.04 | 19.98 | 16.49 | 3.95 | -1.42 |
| FAILED_AUCTION_RECLAIM | filtered | 260 | 53.85 | 65.00 | 11.15 | 20.09 | 19.55 | 20.00 | 4.48 | 11.44 |
| FAILED_AUCTION_RECLAIM | kept | 50 | 70.58 | 65.00 | -5.58 | 21.37 | 19.78 | 20.00 | 4.68 | 0.26 |
| FUNDING_EXTREME_SIGNAL | filtered | 74 | 51.70 | 65.00 | 13.30 | 21.84 | 19.83 | 17.83 | 0.00 | 5.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 28 | 68.20 | 65.00 | -3.20 | 20.69 | 19.96 | 19.88 | 4.11 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 972 | 79.62 | 65.00 | -14.62 | 17.05 | 18.28 | 15.80 | 4.62 | -0.63 |
| SR_FLIP_RETEST | filtered | 181 | 57.92 | 65.00 | 7.08 | 23.76 | 19.98 | 15.28 | 2.05 | 11.15 |
| SR_FLIP_RETEST | kept | 3 | 74.00 | 65.00 | -9.00 | 21.87 | 19.77 | 17.00 | 2.50 | 3.67 |
| TREND_PULLBACK_EMA | kept | 1 | 77.00 | 65.00 | -12.00 | 22.60 | 20.00 | 15.20 | 5.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 57.06 | 19.95 | 12.74 | 13.42 | 12.37 | 5.95 | 6.79 | 0.42 |
| DIVERGENCE_CONTINUATION | kept | 19 | 70.92 | 21.21 | 16.42 | 3.47 | 12.95 | 4.11 | 9.13 | 3.95 |
| FAILED_AUCTION_RECLAIM | filtered | 260 | 53.85 | 21.37 | 15.97 | 4.68 | 11.71 | 5.86 | 6.75 | 4.48 |
| FAILED_AUCTION_RECLAIM | kept | 50 | 70.58 | 20.84 | 17.52 | 3.54 | 13.80 | 3.68 | 7.08 | 4.68 |
| FUNDING_EXTREME_SIGNAL | filtered | 74 | 51.70 | 20.68 | 18.00 | 3.00 | 15.01 | 8.31 | 6.70 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 28 | 68.20 | 22.43 | 14.00 | 3.96 | 12.07 | 6.12 | 5.50 | 4.11 |
| MOVER_TREND_PULLBACK | kept | 972 | 79.62 | 17.35 | 18.00 | 7.60 | 14.24 | 7.87 | 9.94 | 4.62 |
| SR_FLIP_RETEST | filtered | 181 | 57.92 | 22.26 | 18.00 | 3.83 | 12.03 | 6.18 | 4.73 | 2.05 |
| SR_FLIP_RETEST | kept | 3 | 74.00 | 24.33 | 18.00 | 5.00 | 14.00 | 7.17 | 6.67 | 2.50 |
| TREND_PULLBACK_EMA | kept | 1 | 77.00 | 17.00 | 18.00 | 7.50 | 14.00 | 5.00 | 10.00 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 19 | 57.06 | 0.00 | 0.00 | 0.00 | 0.00 | 3.41 | 0.00 | 0.00 | 0.00 | **3.41** |
| DIVERGENCE_CONTINUATION | kept | 19 | 70.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 260 | 53.85 | 0.00 | 0.00 | 4.98 | 0.00 | 1.50 | 0.00 | 0.00 | 0.00 | **6.48** |
| FAILED_AUCTION_RECLAIM | kept | 50 | 70.58 | 0.00 | 0.00 | 0.26 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.26** |
| FUNDING_EXTREME_SIGNAL | filtered | 74 | 51.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 28 | 68.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 972 | 79.62 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | filtered | 181 | 57.92 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| SR_FLIP_RETEST | kept | 3 | 74.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| TREND_PULLBACK_EMA | kept | 1 | 77.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=96 (67.6%) | PREMATURE=18 (12.7%) | NEUTRAL=28 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 78 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 96 | 18 | 28 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 5 | 1 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 19 | 7 | 10 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 4 | 3 | 3 | 0 |
| MOVER_AVWAP_SCALP | 16 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 28 | 2 | 2 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 20 | 5 | 10 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 96 | 18 | 28 | 70.0 | 30.5 | +0.28 | **KEEP** — net-helping: avg +0.28R/kill across 142 kills (saved 70.0R vs missed 30.5R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `76822`
- `Path funnel` emissions: `26`
- `Regime distribution` emissions: `26`
- `QUIET_SCALP_BLOCK` events: `56`
- `confidence_gate` events: `1607`
- `free_channel_post` events: `5`
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
- Total posts in window: **5**

| Source | Count |
|---|---:|
| regime_shift | 2 |
| signal_close | 2 |
| signal_highlight | 1 |

- By severity: HIGH=5

## Dependency readiness
- cvd: presence[present=177160] state[populated=177160] buckets[many=177160] sources[none] quality[none]
- funding_rate: presence[absent=17895, present=159265] state[empty=17895, populated=159265] buckets[few=159265, none=17895] sources[none] quality[none]
- liquidation_clusters: presence[absent=90319, present=86841] state[empty=90319, populated=86841] buckets[few=73591, none=90319, some=13250] sources[none] quality[none]
- oi_snapshot: presence[absent=17895, present=159265] state[empty=17895, populated=159265] buckets[many=159265, none=17895] sources[none] quality[none]
- order_book: presence[absent=46499, present=130661] state[populated=130661, unavailable=46499] buckets[few=130661, none=46499] sources[book_ticker=130661, unavailable=46499] quality[none=46499, top_of_book_only=130661]
- orderblocks: presence[absent=177160] state[empty=177160] buckets[none=177160] sources[not_implemented=177160] quality[none]
- recent_ticks: presence[absent=1492, present=175668] state[empty=1492, populated=175668] buckets[many=175668, none=1492] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `4.386069416999817` sec
- Median create→first breach: `1131.9427245855331` sec
- Median create→terminal: `2998.8313732147217` sec
- Median first breach→terminal: `2.323304057121277` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 3 | 3 | 0.0 | 33.3 | 0.0 | 0.0 | 1.5917 | 1334.6975479125977 | 2090.8269369602203 |
| DIVERGENCE_CONTINUATION | 7 | 7 | 28.6 | 28.6 | 28.6 | 0.0 | 0.4871 | 1599.3299934864044 | 2432.7327489852905 |
| FAILED_AUCTION_RECLAIM | 13 | 13 | 0.0 | 23.1 | 0.0 | 0.0 | 0.1516 | 1331.5010695457458 | 3600.1019570827484 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0 | 0.5642 | None | 3600.0730590820312 |
| MOVER_AVWAP_SCALP | 4 | 4 | 0.0 | 0.0 | 0.0 | 0.0 | -0.0461 | None | 3603.282956600189 |
| MOVER_TREND_PULLBACK | 13 | 13 | 7.7 | 23.1 | 7.7 | 0.0 | -0.4465 | 906.2018365859985 | 3604.27214884758 |
| SR_FLIP_RETEST | 12 | 12 | 50.0 | 8.3 | 50.0 | 0.0 | 0.7891 | 1422.1789613962173 | 1826.6313014030457 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 15699 | 3 | 14451 | 50.0 | 8.3 | 1422.1789613962173 | 1826.6313014030457 | 1248 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 313 | 1 | 305 | 0.0 | 0.0 | None | None | 8 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `21`
- Gating Δ: `85866`
- No-generation Δ: `653767`
- Fast failures Δ: `-2`
- Quality changes: `{"BREAKDOWN_SHORT": {"avg_pnl_delta": 1.6275, "current_avg_pnl": 1.5917, "current_win_rate": 0.0, "previous_avg_pnl": -0.0358, "previous_win_rate": 50.0, "win_rate_delta": -50.0}, "DIVERGENCE_CONTINUATION": {"avg_pnl_delta": 0.7063, "current_avg_pnl": 0.4871, "current_win_rate": 28.6, "previous_avg_pnl": -0.2192, "previous_win_rate": 22.2, "win_rate_delta": 6.4}, "FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": 0.1704, "current_avg_pnl": 0.1516, "current_win_rate": 0.0, "previous_avg_pnl": -0.0188, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_AVWAP_SCALP": {"avg_pnl_delta": -0.0704, "current_avg_pnl": -0.0461, "current_win_rate": 0.0, "previous_avg_pnl": 0.0243, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "MOVER_TREND_PULLBACK": {"avg_pnl_delta": 0.6137, "current_avg_pnl": -0.4465, "current_win_rate": 7.7, "previous_avg_pnl": -1.0602, "previous_win_rate": 0.0, "win_rate_delta": 7.7}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.3614, "current_avg_pnl": 0.7891, "current_win_rate": 50.0, "previous_avg_pnl": 0.4277, "previous_win_rate": 40.0, "win_rate_delta": 10.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 3, "geometry_changed_delta": 0, "geometry_preserved_delta": 1248, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1269.24, "median_terminal_delta_sec": -969.31, "sl_rate_delta": -11.7, "win_rate_delta": 10.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 1, "geometry_changed_delta": 0, "geometry_preserved_delta": 8, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -1476.93, "median_terminal_delta_sec": -1478.37, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **SR_FLIP_RETEST**
- Most likely bottleneck: **MOVER_TREND_PULLBACK**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
