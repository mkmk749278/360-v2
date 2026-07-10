# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, EVAL::TREND_PULLBACK, EVAL::LIQUIDATION_REVERSAL
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `9` sec (warning=False)
- Latest performance record age: `11124` sec
- Circuit breaker: healthy (not halted)

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| DIVERGENCE_CONTINUATION | 0 | 0 | 270 | 270 | 220 | 1 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1680 | 1680 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1752 | 1752 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 1748 | 1647 | 105 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 1752 | 1684 | 68 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1938 | 1938 | 0 | 0 | 0 | 0 | dependency-missing (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1546 | 1546 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 1752 | 1751 | 1 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 1909 | 1906 | 149 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 1680 | 1416 | 492 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 1908 | 1908 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1752 | 1752 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1748 | 1748 | 0 | 0 | 0 | 0 | non-generating (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 1718 | 1715 | 33 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1386 | 1351 | 36 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1387 | 1388 | 0 | 0 | 0 | 0 | non-generating (h1_trend_not_aligned) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1680 | 1680 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1546 | 1544 | 3 | 0 | 0 | 0 | low-sample (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 200 | 200 | 77 | 3 | active-low-quality (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 200 | 200 | 192 | 2 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 263 | 263 | 197 | 1 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 1106 | 1106 | 1100 | 1 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 66 | 66 | 52 | 0 | low-sample (none) |
| WHALE_MOMENTUM | 0 | 0 | 99 | 99 | 99 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1680): breakout_not_found=987, basic_filters_failed=640, breakout_stale=34, move_not_fresh=17, volume_spike_missing=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1752): cls_disabled_merged_into_lsr=1752
- **EVAL::DIVERGENCE_CONTINUATION** (total=1647): basic_filters_failed=529, h1_trend_not_aligned=524, cvd_divergence_failed=499, ema_alignment_reject=71, retest_proximity_failed=11, missing_fvg_or_orderblock=9, regime_blocked=4
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1684): auction_not_detected=673, basic_filters_failed=510, tail_too_small=282, reclaim_hold_failed=147, regime_blocked=72
- **EVAL::FUNDING_EXTREME** (total=1938): funding_not_extreme=1096, basic_filters_failed=509, missing_funding_rate=264, ema_alignment_reject=60, rsi_reject=9
- **EVAL::LIQUIDATION_REVERSAL** (total=1546): cascade_threshold_not_met=920, basic_filters_failed=593, rsi_reject=16, cvd_divergence_failed=14, missing_fvg_or_orderblock=3
- **EVAL::MA_CROSS_TREND_SHIFT** (total=1751): no_ma_cross=1165, basic_filters_failed=529, ma_cross_cooldown=57
- **EVAL::MOVER_AVWAP_SCALP** (total=1906): no_avwap_tag=968, basic_filters_failed=640, no_mover_leg=241, avwap_slope_against=54, avwap_reclaim_no_volume=3
- **EVAL::MOVER_TREND_PULLBACK** (total=1416): basic_filters_failed=640, mover_run_too_small=477, no_reclaim=260, no_pullback_tag=39
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1908): feature_disabled=1908
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1752): regime_blocked=1381, breakout_not_found=192, basic_filters_failed=129, adx_reject=50
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1748): compression_not_detected=842, regime_blocked=443, basic_filters_failed=381, breakout_not_detected=82
- **EVAL::SR_FLIP_RETEST** (total=1715): basic_filters_failed=510, flip_close_not_confirmed=447, long_break_volume_thin=346, whipsaw_flip=172, long_disabled=103, regime_blocked=72, retest_out_of_zone=36, reclaim_hold_failed=15, wick_quality_failed=8, long_acceptance_not_held=3, ema_alignment_reject=2, missing_fvg_or_orderblock=1
- **EVAL::STANDARD** (total=1351): momentum_reject=326, basic_filters_failed=291, adx_reject=279, macd_reject=259, sweeps_not_detected=135, ema_alignment_reject=48, invalid_sl_geometry=10, rsi_reject=3
- **EVAL::TREND_PULLBACK** (total=1388): h1_trend_not_aligned=470, basic_filters_failed=276, h1_pullback_not_confirmed=223, no_ema_reclaim_close=187, ema_alignment_reject=133, body_conviction_fail=34, regime_blocked=28, ema_not_tested_prev=13, momentum_flat=10, rsi_reject=7, no_prev_high_break=3, prev_already_above_emas=2, momentum_reject=2
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1680): breakout_not_found=859, basic_filters_failed=640, move_not_fresh=115, breakout_stale=55, volume_spike_missing=7, retest_proximity_failed=4
- **EVAL::WHALE_MOMENTUM** (total=1544): momentum_reject=958, recent_ticks_insufficient=387, basic_filters_failed=199

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 3122 | 39.5% |
| RANGING | 2585 | 32.7% |
| TRENDING_UP | 1043 | 13.2% |
| TRENDING_DOWN | 602 | 7.6% |
| VOLATILE | 544 | 6.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **8**
- Average confidence gap to threshold: **3.49** (samples=8) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: HYPEUSDT=5, DOGEUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 3 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 2 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 8 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 11 |
| LIQUIDITY_SWEEP_REVERSAL | kept | min_confidence_pass | 2 |
| MOVER_AVWAP_SCALP | kept | min_confidence_pass | 65 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 3 | 60.70 | 65.00 | 4.30 | 21.20 | 20.00 | 18.97 | 3.33 | 6.73 |
| DIVERGENCE_CONTINUATION | kept | 2 | 67.95 | 65.00 | -2.95 | 20.70 | 20.00 | 17.05 | 0.00 | 3.60 |
| FAILED_AUCTION_RECLAIM | filtered | 8 | 61.51 | 65.00 | 3.49 | 22.81 | 20.00 | 20.00 | 4.81 | 5.00 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 69.27 | 65.00 | -4.27 | 20.89 | 18.59 | 20.00 | 5.09 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 67.20 | 65.00 | -2.20 | 21.90 | 19.45 | 17.00 | 4.00 | 0.00 |
| MOVER_AVWAP_SCALP | kept | 65 | 75.23 | 65.00 | -10.23 | 19.04 | 19.94 | 15.80 | 4.58 | 0.00 |
| MOVER_TREND_PULLBACK | kept | 3 | 78.90 | 65.00 | -13.90 | 19.73 | 19.00 | 15.80 | 5.50 | 6.80 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 3 | 60.70 | 17.00 | 14.67 | 6.00 | 11.33 | 6.67 | 8.43 | 3.33 |
| DIVERGENCE_CONTINUATION | kept | 2 | 67.95 | 25.00 | 8.00 | 7.50 | 14.00 | 9.25 | 9.30 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 8 | 61.51 | 20.00 | 14.00 | 3.00 | 13.12 | 6.88 | 4.70 | 4.81 |
| FAILED_AUCTION_RECLAIM | kept | 11 | 69.27 | 24.27 | 14.00 | 3.00 | 10.27 | 5.45 | 7.18 | 5.09 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 67.20 | 25.00 | 14.00 | 3.00 | 12.00 | 5.50 | 3.70 | 4.00 |
| MOVER_AVWAP_SCALP | kept | 65 | 75.23 | 17.98 | 18.00 | 10.68 | 14.00 | 6.62 | 3.36 | 4.58 |
| MOVER_TREND_PULLBACK | kept | 3 | 78.90 | 19.67 | 18.00 | 10.50 | 13.00 | 9.50 | 9.53 | 5.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 3 | 60.70 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | kept | 2 | 67.95 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 8 | 61.51 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | kept | 11 | 69.27 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 2 | 67.20 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_AVWAP_SCALP | kept | 65 | 75.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| MOVER_TREND_PULLBACK | kept | 3 | 78.90 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=55 (68.8%) | PREMATURE=11 (13.8%) | NEUTRAL=14 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 44 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 55 | 11 | 14 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 2 | 3 | 1 | 0 |
| FAILED_AUCTION_RECLAIM | 12 | 4 | 7 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 1 | 1 | 1 | 0 |
| MOVER_AVWAP_SCALP | 11 | 0 | 0 | 0 |
| MOVER_TREND_PULLBACK | 22 | 1 | 1 | 0 |
| SR_FLIP_RETEST | 7 | 2 | 4 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 55 | 11 | 14 | 42.3 | 13.2 | +0.36 | **KEEP** — net-helping: avg +0.36R/kill across 80 kills (saved 42.3R vs missed 13.2R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `4012`
- `Path funnel` emissions: `1`
- `Regime distribution` emissions: `1`
- `QUIET_SCALP_BLOCK` events: `8`
- `confidence_gate` events: `94`
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
- cvd: presence[present=6284] state[populated=6284] buckets[many=6236, some=48] sources[none] quality[none]
- funding_rate: presence[absent=921, present=5363] state[empty=921, populated=5363] buckets[few=5363, none=921] sources[none] quality[none]
- liquidation_clusters: presence[absent=5282, present=1002] state[empty=5282, populated=1002] buckets[few=936, none=5282, some=66] sources[none] quality[none]
- oi_snapshot: presence[absent=325, present=5959] state[empty=325, populated=5959] buckets[many=5959, none=325] sources[none] quality[none]
- order_book: presence[absent=1067, present=5217] state[populated=5217, unavailable=1067] buckets[few=5217, none=1067] sources[book_ticker=5217, unavailable=1067] quality[none=1067, top_of_book_only=5217]
- orderblocks: presence[absent=6284] state[empty=6284] buckets[none=6284] sources[not_implemented=6284] quality[none]
- recent_ticks: presence[present=6284] state[populated=6284] buckets[many=6284] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `3.3606069087982178` sec
- Median create→first breach: `9337.02173936367` sec
- Median create→terminal: `9339.30735194683` sec
- Median first breach→terminal: `2.567630887031555` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | 5 | 5 | 20.0 | 80.0 | 20.0 | 0.0 | -0.9448 | 10001.968668937683 | 10003.613761901855 |
| MOVER_TREND_PULLBACK | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.7871 | 8672.074809789658 | 8675.000941991806 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 66 | 0 | 52 | 0.0 | 0.0 | None | None | 14 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 0 | 0 | 0 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `8`
- Gating Δ: `1938`
- No-generation Δ: `28406`
- Fast failures Δ: `0`
- Quality changes: `{"FAILED_AUCTION_RECLAIM": {"avg_pnl_delta": -1.6902, "current_avg_pnl": -0.9448, "current_win_rate": 20.0, "previous_avg_pnl": 0.7454, "previous_win_rate": 0.0, "win_rate_delta": 20.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 14, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": -725.34, "median_terminal_delta_sec": -725.81, "sl_rate_delta": 0.0, "win_rate_delta": -100.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": 0, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **WHALE_MOMENTUM**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
