# Runtime Truth Report

## Executive summary
- Overall health/freshness: **healthy**
- Top anomalies/concerns: FAILED_AUCTION_RECLAIM, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **FAILED_AUCTION_RECLAIM**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `3111` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 71 | 71 | 12 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 2644 | 2644 | 2400 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 25702 | 25702 | 17 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 22115 | 22114 | 0 | 0 | 0 | 0 | non-generating (cls_disabled_merged_into_lsr) |
| EVAL::DIVERGENCE_CONTINUATION | 22054 | 21075 | 1037 | 0 | 0 | 0 | low-sample (cvd_divergence_failed) |
| EVAL::FAILED_AUCTION_RECLAIM | 22124 | 20743 | 1427 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 24829 | 24771 | 67 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 18789 | 18796 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::MA_CROSS_TREND_SHIFT | 22173 | 22177 | 2 | 0 | 0 | 0 | low-sample (no_ma_cross) |
| EVAL::MOVER_AVWAP_SCALP | 30356 | 30547 | 1954 | 0 | 0 | 0 | low-sample (no_avwap_tag) |
| EVAL::MOVER_TREND_PULLBACK | 25719 | 18274 | 12071 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::OPENING_RANGE_BREAKOUT | 24433 | 24434 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 22115 | 22122 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 22051 | 22011 | 42 | 0 | 0 | 0 | low-sample (compression_not_detected) |
| EVAL::SR_FLIP_RETEST | 21652 | 20069 | 1975 | 0 | 0 | 0 | low-sample (flip_close_not_confirmed) |
| EVAL::STANDARD | 16548 | 15161 | 1471 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 16630 | 16572 | 69 | 0 | 0 | 0 | low-sample (h1_pullback_not_confirmed) |
| EVAL::VOLUME_SURGE_BREAKOUT | 25694 | 25701 | 0 | 0 | 0 | 0 | non-generating (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 18798 | 18810 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 3320 | 3320 | 2379 | 20 | active-low-quality (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 177 | 177 | 171 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 5150 | 5150 | 5082 | 0 | low-sample (none) |
| MA_CROSS_TREND_SHIFT | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| MOVER_AVWAP_SCALP | 0 | 0 | 4250 | 4250 | 4250 | 0 | low-sample (none) |
| MOVER_TREND_PULLBACK | 0 | 0 | 25574 | 25574 | 24146 | 2 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 68 | 68 | 31 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 5035 | 5035 | 4003 | 4 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 264 | 264 | 264 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 2 | 2 | 0 | 2 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=25702): breakout_not_found=11897, basic_filters_failed=6390, move_not_fresh=5223, breakout_stale=1573, retest_proximity_failed=585, volume_spike_missing=32, missing_fvg_or_orderblock=2
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=22115): cls_disabled_merged_into_lsr=22115
- **EVAL::DIVERGENCE_CONTINUATION** (total=21076): cvd_divergence_failed=8444, ema_alignment_reject=4864, h1_trend_not_aligned=3669, basic_filters_failed=3571, retest_proximity_failed=434, missing_fvg_or_orderblock=94
- **EVAL::FAILED_AUCTION_RECLAIM** (total=20744): auction_not_detected=8539, reclaim_hold_failed=4442, tail_too_small=3481, basic_filters_failed=3437, regime_blocked=845
- **EVAL::FUNDING_EXTREME** (total=24772): funding_not_extreme=19308, basic_filters_failed=4313, ema_alignment_reject=830, rsi_reject=119, momentum_reject=90, cvd_divergence_failed=89, missing_fvg_or_orderblock=15, missing_funding_rate=8
- **EVAL::LIQUIDATION_REVERSAL** (total=18796): cascade_threshold_not_met=14360, basic_filters_failed=4263, cvd_divergence_failed=93, rsi_reject=79, volume_spike_missing=1
- **EVAL::MA_CROSS_TREND_SHIFT** (total=22178): no_ma_cross=18343, basic_filters_failed=3573, ma_cross_cooldown=171, ma_cross_htf_misaligned=91
- **EVAL::MOVER_AVWAP_SCALP** (total=30548): no_avwap_tag=18646, basic_filters_failed=6440, no_mover_leg=2996, avwap_slope_against=1629, avwap_reclaim_no_volume=636, no_avwap_reclaim=201
- **EVAL::MOVER_TREND_PULLBACK** (total=18274): basic_filters_failed=6414, mover_run_too_small=5546, no_reclaim=4791, no_pullback_tag=1523
- **EVAL::OPENING_RANGE_BREAKOUT** (total=24435): feature_disabled=24435
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=22123): regime_blocked=16113, breakout_not_found=4568, basic_filters_failed=1046, adx_reject=374, ema_alignment_reject=22
- **EVAL::QUIET_COMPRESSION_BREAK** (total=22012): compression_not_detected=11940, regime_blocked=6831, basic_filters_failed=2390, breakout_not_detected=795, volume_confirmation_failed=45, rsi_reject=11
- **EVAL::SR_FLIP_RETEST** (total=20070): flip_close_not_confirmed=4425, basic_filters_failed=3434, reclaim_hold_failed=2853, whipsaw_flip=2588, long_break_volume_thin=2135, retest_out_of_zone=2042, long_disabled=864, regime_blocked=840, wick_quality_failed=593, long_acceptance_not_held=157, missing_fvg_or_orderblock=127, ema_alignment_reject=12
- **EVAL::STANDARD** (total=15161): momentum_reject=4911, sweeps_not_detected=2857, adx_reject=2745, basic_filters_failed=1802, macd_reject=1719, ema_alignment_reject=1015, invalid_sl_geometry=99, rsi_reject=13
- **EVAL::TREND_PULLBACK** (total=16572): h1_pullback_not_confirmed=6405, ema_alignment_reject=3261, h1_trend_not_aligned=3102, basic_filters_failed=1748, ema_not_tested_prev=837, no_ema_reclaim_close=508, rsi_reject=259, body_conviction_fail=245, prev_already_above_emas=119, no_prev_high_break=36, momentum_flat=26, no_prev_low_break=13, prev_already_below_emas=12, ema21_not_tagged=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=25701): breakout_not_found=15498, basic_filters_failed=6387, move_not_fresh=2005, breakout_stale=1147, retest_proximity_failed=612, volume_spike_missing=51, missing_fvg_or_orderblock=1
- **EVAL::WHALE_MOMENTUM** (total=18810): momentum_reject=12200, recent_ticks_insufficient=5469, basic_filters_failed=1141

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| RANGING | 49624 | 46.7% |
| QUIET | 21588 | 20.3% |
| TRENDING_DOWN | 17286 | 16.3% |
| TRENDING_UP | 12528 | 11.8% |
| VOLATILE | 5245 | 4.9% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **268**
- Average confidence gap to threshold: **10.84** (samples=268) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=154, DOGEUSDT=33, DOTUSDT=18, TRXUSDT=17, SOLUSDT=15, BTCUSDT=9, LINKUSDT=6, TAOUSDT=5, ETHUSDT=3, AAVEUSDT=3

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| BREAKDOWN_SHORT | filtered | min_confidence | 32 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 19 |
| DIVERGENCE_CONTINUATION | filtered | quiet_scalp_min_confidence | 1 |
| DIVERGENCE_CONTINUATION | kept | min_confidence_pass | 8 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 144 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 29 |
| FAILED_AUCTION_RECLAIM | kept | min_confidence_pass | 135 |
| MOVER_TREND_PULLBACK | filtered | quiet_scalp_min_confidence | 197 |
| MOVER_TREND_PULLBACK | filtered | min_confidence | 187 |
| MOVER_TREND_PULLBACK | kept | min_confidence_pass | 555 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 13 |
| SR_FLIP_RETEST | filtered | min_confidence | 105 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 28 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 23 |
| VOLUME_SURGE_BREAKOUT | kept | min_confidence_pass | 2 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 32 | 56.18 | 65.00 | 8.82 | 17.08 | 17.74 | 20.00 | 4.16 | 21.88 |
| DIVERGENCE_CONTINUATION | filtered | 20 | 54.99 | 65.00 | 10.01 | 19.48 | 19.43 | 18.45 | 2.95 | 11.09 |
| DIVERGENCE_CONTINUATION | kept | 8 | 70.76 | 65.00 | -5.76 | 20.63 | 19.96 | 17.31 | 0.88 | -0.75 |
| FAILED_AUCTION_RECLAIM | filtered | 173 | 54.83 | 65.00 | 10.17 | 20.47 | 19.66 | 20.00 | 4.43 | 4.51 |
| FAILED_AUCTION_RECLAIM | kept | 135 | 72.34 | 65.00 | -7.34 | 20.95 | 19.79 | 20.00 | 4.72 | 0.53 |
| MOVER_TREND_PULLBACK | filtered | 384 | 55.43 | 65.00 | 9.57 | 21.29 | 18.05 | 15.80 | 3.35 | 13.02 |
| MOVER_TREND_PULLBACK | kept | 555 | 72.81 | 65.00 | -7.81 | 20.25 | 17.24 | 15.80 | 3.88 | 4.77 |
| QUIET_COMPRESSION_BREAK | filtered | 13 | 62.36 | 65.00 | 2.64 | 18.00 | 20.00 | 20.00 | 0.00 | 7.32 |
| SR_FLIP_RETEST | filtered | 133 | 51.95 | 65.00 | 13.05 | 21.60 | 19.85 | 15.61 | 1.83 | 16.27 |
| SR_FLIP_RETEST | kept | 23 | 69.85 | 65.00 | -4.85 | 20.66 | 20.00 | 15.59 | 2.09 | 1.57 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 73.55 | 65.00 | -8.55 | 19.40 | 19.45 | 20.00 | 5.25 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 32 | 56.18 | 20.50 | 18.00 | 12.00 | 11.47 | 7.34 | 4.59 | 4.16 |
| DIVERGENCE_CONTINUATION | filtered | 20 | 54.99 | 24.60 | 8.50 | 7.05 | 10.95 | 5.70 | 7.83 | 2.95 |
| DIVERGENCE_CONTINUATION | kept | 8 | 70.76 | 24.00 | 16.75 | 3.38 | 10.88 | 5.62 | 9.26 | 0.88 |
| FAILED_AUCTION_RECLAIM | filtered | 173 | 54.83 | 22.34 | 17.17 | 4.79 | 12.58 | 5.75 | 5.13 | 4.43 |
| FAILED_AUCTION_RECLAIM | kept | 135 | 72.34 | 23.59 | 15.75 | 3.69 | 10.99 | 6.77 | 7.37 | 4.72 |
| MOVER_TREND_PULLBACK | filtered | 384 | 55.43 | 19.31 | 18.00 | 8.39 | 13.21 | 5.74 | 3.80 | 3.35 |
| MOVER_TREND_PULLBACK | kept | 555 | 72.81 | 20.92 | 18.00 | 7.81 | 12.61 | 7.57 | 6.79 | 3.88 |
| QUIET_COMPRESSION_BREAK | filtered | 13 | 62.36 | 17.00 | 18.00 | 12.23 | 14.00 | 7.15 | 1.30 | 0.00 |
| SR_FLIP_RETEST | filtered | 133 | 51.95 | 21.09 | 15.89 | 5.35 | 13.44 | 6.54 | 4.08 | 1.83 |
| SR_FLIP_RETEST | kept | 23 | 69.85 | 21.17 | 17.57 | 3.91 | 12.96 | 6.59 | 7.13 | 2.09 |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 73.55 | 25.00 | 16.00 | 12.00 | 14.00 | 5.00 | 6.80 | 5.25 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression; BTC_DIR = BTC 1H+4H counter-direction soft penalty (OWNER_BRIEF §2.1)._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | BTC_Dir | Sym_Dir | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BREAKDOWN_SHORT | filtered | 32 | 56.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 20 | 54.99 | 0.00 | 0.00 | 0.64 | 0.00 | 1.80 | 0.00 | 0.00 | 0.00 | **2.44** |
| DIVERGENCE_CONTINUATION | kept | 8 | 70.76 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| FAILED_AUCTION_RECLAIM | filtered | 173 | 54.83 | 0.00 | 0.00 | 1.20 | 0.00 | 1.54 | 0.00 | 0.00 | 0.00 | **2.74** |
| FAILED_AUCTION_RECLAIM | kept | 135 | 72.34 | 0.00 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.18** |
| MOVER_TREND_PULLBACK | filtered | 384 | 55.43 | 0.00 | 0.00 | 1.55 | 0.00 | 3.51 | 0.00 | 0.00 | 7.10 | **12.16** |
| MOVER_TREND_PULLBACK | kept | 555 | 72.81 | 0.00 | 0.00 | 0.61 | 0.00 | 0.09 | 0.00 | 0.00 | 4.05 | **4.75** |
| QUIET_COMPRESSION_BREAK | filtered | 13 | 62.36 | 0.00 | 0.00 | 0.00 | 0.00 | 1.32 | 0.00 | 0.00 | 0.00 | **1.32** |
| SR_FLIP_RETEST | filtered | 133 | 51.95 | 0.00 | 0.00 | 0.00 | 0.00 | 2.27 | 0.00 | 0.00 | 5.24 | **7.51** |
| SR_FLIP_RETEST | kept | 23 | 69.85 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| VOLUME_SURGE_BREAKOUT | kept | 2 | 73.55 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=100 (66.7%) | PREMATURE=18 (12.0%) | NEUTRAL=32 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 82 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| expired | 100 | 18 | 32 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 0 |
| DIVERGENCE_CONTINUATION | 6 | 1 | 0 | 0 |
| FAILED_AUCTION_RECLAIM | 26 | 6 | 12 | 0 |
| FUNDING_EXTREME_SIGNAL | 0 | 1 | 0 | 0 |
| LIQUIDITY_SWEEP_REVERSAL | 7 | 2 | 3 | 0 |
| MOVER_AVWAP_SCALP | 10 | 0 | 1 | 0 |
| MOVER_TREND_PULLBACK | 26 | 3 | 3 | 0 |
| QUIET_COMPRESSION_BREAK | 3 | 0 | 1 | 0 |
| SR_FLIP_RETEST | 20 | 5 | 11 | 0 |
| VOLUME_SURGE_BREAKOUT | 1 | 0 | 0 | 0 |
| WHALE_MOMENTUM | 1 | 0 | 0 | 0 |

### Per-rule ablation (R-units per kill)
_DROP candidate: avg EV < -0.20R/kill across >= 20 kills. KEEP: avg EV > +0.10R/kill. TUNE: in between. EV model: counterfactual exit at TP1 (PREMATURE) or at worst post-kill excursion floored at -1R (PROTECTIVE)._

| Rule | PROT | PREM | NEUT | Saved R | Missed R | EV/kill (R) | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| expired | 100 | 18 | 32 | 72.0 | 32.8 | +0.26 | **KEEP** — net-helping: avg +0.26R/kill across 150 kills (saved 72.0R vs missed 32.8R) |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `501756`
- `Path funnel` emissions: `11`
- `Regime distribution` emissions: `11`
- `QUIET_SCALP_BLOCK` events: `268`
- `confidence_gate` events: `1478`
- `free_channel_post` events: `6`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## WebSocket outage stats
_Drop → restored durations and REST-fallback activations parsed from engine logs.  Each reconnect emits a `ws_reconnect_duration_ms` marker; each REST-fallback start emits `ws_rest_fallback_activated`. The 180s grace column shows how many reconnects exceeded ``WS_REST_FALLBACK_ALERT_GRACE_SEC`` (i.e. fired an admin alert) — if `exceeds_grace` >> 0 we should bump the grace, shard further, or both._
- Total reconnects in window: **1**
- Total REST-fallback activations: **0**

| Label | Reconnects | p50 (ms) | p95 (ms) | Max (ms) | Exceeds 180s grace |
|---|---:|---:|---:|---:|---:|
| futures_liq | 1 | 2049 | 2049 | 2049 | 0 |

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **6**

| Source | Count |
|---|---:|
| signal_close | 5 |
| regime_shift | 1 |

- By severity: HIGH=6

## Dependency readiness
- cvd: presence[present=84864] state[populated=84864] buckets[many=84864] sources[none] quality[none]
- funding_rate: presence[absent=16743, present=68121] state[empty=16743, populated=68121] buckets[few=68121, none=16743] sources[none] quality[none]
- liquidation_clusters: presence[absent=54446, present=30418] state[empty=54446, populated=30418] buckets[few=26096, none=54446, some=4322] sources[none] quality[none]
- oi_snapshot: presence[absent=16743, present=68121] state[empty=16743, populated=68121] buckets[few=56, many=67660, none=16743, some=405] sources[none] quality[none]
- order_book: presence[absent=31082, present=53782] state[populated=53782, unavailable=31082] buckets[few=53782, none=31082] sources[book_ticker=53782, unavailable=31082] quality[none=31082, top_of_book_only=53782]
- orderblocks: presence[absent=84864] state[empty=84864] buckets[none=84864] sources[not_implemented=84864] quality[none]
- recent_ticks: presence[present=84864] state[populated=84864] buckets[many=84864] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `9.513532996177673` sec
- Median create→first breach: `492.3451180458069` sec
- Median create→terminal: `1751.1076259613037` sec
- Median first breach→terminal: `1.6055219173431396` sec
- Fast-failure buckets: `{"under_120s": {"count": 1, "pct": 25.0}, "under_180s": {"count": 2, "pct": 50.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
_``Win rate`` / ``TP rate`` count only TP1/TP2/TP3 hits — they MISS the pre-TP partial-close fires that bank real subscriber value per OWNER_BRIEF §3.2a.  ``Pre-TP win%`` is the rate at which signals hit their pre-TP threshold (typically ~+0.32% raw → ~+2.5% net @ 10×) before terminal close.  The composite truth: a setup with Win=0 + Pre-TP=60% is doctrinally healthy (banking + BE residual), while Win=0 + Pre-TP=0 is the actual quality problem._
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Pre-TP win% | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -0.7999 | 841.1757040023804 | 842.094584941864 |
| FAILED_AUCTION_RECLAIM | 4 | 4 | 0.0 | 25.0 | 0.0 | 0.0 | 0.5267 | 1749.2244100570679 | 3632.6496584415436 |
| SR_FLIP_RETEST | 1 | 1 | 100.0 | 0.0 | 100.0 | 0.0 | 0.96 | 100.77561497688293 | 104.39647006988525 |
| VOLUME_SURGE_BREAKOUT | 1 | 1 | 0.0 | 100.0 | 0.0 | 0.0 | -1.2993 | 143.5145320892334 | 144.84236001968384 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 5035 | 4 | 4003 | 100.0 | 0.0 | 100.77561497688293 | 104.39647006988525 | 1032 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 264 | 0 | 264 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Disabled

## Recommended operator focus
- Most suspicious degradation: **FAILED_AUCTION_RECLAIM**
- Most promising healthy path: **none**
- Most likely bottleneck: **LIQUIDITY_SWEEP_REVERSAL**
- Suggested next investigation target: **FAILED_AUCTION_RECLAIM**
