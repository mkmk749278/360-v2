# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **EVAL::LIQUIDATION_REVERSAL**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `2` sec (warning=False)
- Latest performance record age: `41215` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 86 | 86 | 51 | 2 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 6628 | 6628 | 5699 | 10 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1509932 | 1509929 | 3 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1509932 | 1509846 | 86 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1509932 | 1503304 | 6628 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1509932 | 1411080 | 98852 | 0 | 0 | 0 | low-sample (auction_not_detected) |
| EVAL::FUNDING_EXTREME | 1509932 | 1506442 | 3490 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1509932 | 1509932 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1509932 | 1509932 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1509932 | 1509932 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1509932 | 1504544 | 5388 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1509932 | 1451743 | 58189 | 0 | 0 | 0 | low-sample (basic_filters_failed) |
| EVAL::STANDARD | 1509932 | 1470146 | 39786 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1509932 | 1508967 | 965 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1509932 | 1509651 | 281 | 0 | 0 | 0 | low-sample (breakout_not_found) |
| EVAL::WHALE_MOMENTUM | 1509932 | 1509932 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 98852 | 98852 | 67457 | 52 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 3490 | 3490 | 3490 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 39786 | 39786 | 36889 | 5 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 5388 | 5388 | 5110 | 0 | low-sample (none) |
| SR_FLIP_RETEST | 0 | 0 | 58189 | 58189 | 24382 | 96 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 965 | 965 | 965 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 281 | 281 | 278 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1509929): breakout_not_found=673077, regime_blocked=383996, basic_filters_failed=293107, retest_proximity_failed=150708, volume_spike_missing=9037, missing_fvg_or_orderblock=4
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1509846): regime_blocked=689554, sweeps_not_detected=264507, basic_filters_failed=240436, ema_alignment_reject=238289, adx_reject=69116, momentum_reject=6913, reclaim_confirmation_failed=991, rsi_reject=40
- **EVAL::DIVERGENCE_CONTINUATION** (total=1503304): regime_blocked=689554, cvd_divergence_failed=470739, basic_filters_failed=240436, missing_cvd=65612, ema_alignment_reject=29508, retest_proximity_failed=7455
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1411080): auction_not_detected=504850, basic_filters_failed=403262, regime_blocked=300903, reclaim_hold_failed=114380, tail_too_small=87394, rsi_reject=291
- **EVAL::FUNDING_EXTREME** (total=1506442): funding_not_extreme=966098, basic_filters_failed=443232, ema_alignment_reject=60840, rsi_reject=19697, missing_funding_rate=13504, cvd_divergence_failed=1728, momentum_reject=1343
- **EVAL::LIQUIDATION_REVERSAL** (total=1509932): cascade_threshold_not_met=1018376, basic_filters_failed=454897, cvd_divergence_failed=36642, rsi_reject=17
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1509932): feature_disabled=1509932
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1509932): regime_blocked=689554, breakout_not_found=272537, basic_filters_failed=240436, ema_alignment_reject=238289, adx_reject=69116
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1504544): regime_blocked=1121281, basic_filters_failed=162826, breakout_not_detected=128565, compression_not_detected=84920, rsi_reject=5707, missing_fvg_or_orderblock=665, macd_reject=580
- **EVAL::SR_FLIP_RETEST** (total=1451743): basic_filters_failed=396291, retest_out_of_zone=352422, regime_blocked=300903, flip_close_not_confirmed=205926, reclaim_hold_failed=156888, wick_quality_failed=20219, insufficient_candles=9502, missing_fvg_or_orderblock=5192, rsi_reject=2825, ema_alignment_reject=1575
- **EVAL::STANDARD** (total=1470146): momentum_reject=455379, adx_reject=372913, basic_filters_failed=231393, sweeps_not_detected=204943, ema_alignment_reject=160608, insufficient_candles=21801, macd_reject=16185, invalid_sl_geometry=6794, rsi_reject=125, htf_ema_reject=5
- **EVAL::TREND_PULLBACK** (total=1508967): regime_blocked=689554, ema_alignment_reject=238289, basic_filters_failed=236779, ema_not_tested_prev=178123, body_conviction_fail=56839, rsi_reject=52446, no_ema_reclaim_close=45312, insufficient_candles=5468, prev_already_above_emas=3531, no_prev_high_break=1074, ema21_not_tagged=978, momentum_reject=291, missing_fvg_or_orderblock=271, momentum_flat=10, no_prev_low_break=1, prev_already_below_emas=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1509651): breakout_not_found=542356, regime_blocked=383996, basic_filters_failed=293107, retest_proximity_failed=267831, volume_spike_missing=22083, missing_fvg_or_orderblock=278
- **EVAL::WHALE_MOMENTUM** (total=1509932): momentum_reject=1125936, regime_blocked=383996

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| TRENDING_UP | 1069086 | 54.4% |
| QUIET | 501893 | 25.5% |
| VOLATILE | 389093 | 19.8% |
| RANGING | 5506 | 0.3% |
| TRENDING_DOWN | 902 | 0.0% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **4219**
- Average confidence gap to threshold: **26.39** (samples=4219) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=640, TRXUSDT=596, 币安人生USDT=516, XNYUSDT=422, ENAUSDT=305, VIRTUALUSDT=243, TRADOORUSDT=226, WLFIUSDT=191, ZEREBROUSDT=191, DASHUSDT=184

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | min_confidence | 33 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | watchlist_tier_keep | 2 |
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 718 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 211 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 20583 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 912 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 8647 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1833 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 289 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 281 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 278 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 3 |
| SR_FLIP_RETEST | filtered | min_confidence | 5900 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 1196 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 7113 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 2 |
| VOLUME_SURGE_BREAKOUT | kept | watchlist_tier_keep | 3 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 33 | 68.61 | 80.00 | 11.39 | 20.86 | 20.00 | 17.00 | 0.00 | 1.70 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 2 | 62.15 | 50.00 | -12.15 | 22.70 | 18.45 | 17.00 | 0.00 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 718 | 44.76 | 80.00 | 35.24 | 20.80 | 19.90 | 20.00 | 0.06 | 6.00 |
| DIVERGENCE_CONTINUATION | kept | 211 | 51.52 | 50.00 | -1.52 | 20.80 | 19.90 | 19.98 | 0.80 | 0.03 |
| FAILED_AUCTION_RECLAIM | filtered | 21495 | 55.01 | 79.36 | 24.35 | 21.30 | 18.93 | 14.00 | 2.85 | 7.98 |
| FAILED_AUCTION_RECLAIM | kept | 8647 | 59.25 | 50.00 | -9.25 | 22.75 | 19.53 | 14.00 | 4.04 | 6.41 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2122 | 49.42 | 67.04 | 17.62 | 21.61 | 19.44 | 15.20 | 2.36 | 16.43 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 281 | 58.32 | 50.00 | -8.32 | 20.19 | 18.89 | 15.20 | 0.80 | 8.28 |
| QUIET_COMPRESSION_BREAK | filtered | 281 | 46.29 | 65.16 | 18.87 | 20.19 | 18.30 | 15.80 | 0.00 | 18.71 |
| SR_FLIP_RETEST | filtered | 7096 | 50.48 | 77.47 | 26.99 | 20.84 | 19.99 | 15.28 | 1.14 | 9.98 |
| SR_FLIP_RETEST | kept | 7115 | 54.58 | 50.01 | -4.57 | 21.63 | 19.98 | 15.25 | 0.99 | 11.44 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 51.17 | 50.00 | -1.17 | 19.87 | 20.00 | 20.00 | 1.50 | 3.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 33 | 68.61 | 21.36 | 18.00 | 3.82 | 13.18 | 7.00 | 8.76 | 0.00 |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 2 | 62.15 | 21.00 | 18.00 | 4.50 | 12.00 | 5.00 | 9.15 | 0.00 |
| DIVERGENCE_CONTINUATION | filtered | 718 | 44.76 | 25.00 | 18.00 | 3.00 | 10.00 | 5.00 | 4.70 | 0.06 |
| DIVERGENCE_CONTINUATION | kept | 211 | 51.52 | 25.00 | 18.00 | 3.00 | 10.02 | 5.01 | 4.71 | 0.80 |
| FAILED_AUCTION_RECLAIM | filtered | 21495 | 55.01 | 20.36 | 14.05 | 3.06 | 10.52 | 6.60 | 6.57 | 2.85 |
| FAILED_AUCTION_RECLAIM | kept | 8647 | 59.25 | 23.05 | 14.12 | 3.08 | 9.53 | 5.29 | 6.54 | 4.04 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 2122 | 49.42 | 20.70 | 14.55 | 3.03 | 12.70 | 5.66 | 6.94 | 2.36 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 281 | 58.32 | 20.56 | 15.74 | 4.81 | 13.21 | 5.14 | 6.32 | 0.80 |
| QUIET_COMPRESSION_BREAK | filtered | 281 | 46.29 | 17.00 | 18.00 | 3.78 | 13.99 | 8.24 | 4.95 | 0.00 |
| SR_FLIP_RETEST | filtered | 7096 | 50.48 | 16.16 | 16.31 | 5.73 | 14.30 | 5.24 | 7.51 | 1.14 |
| SR_FLIP_RETEST | kept | 7115 | 54.58 | 15.26 | 18.00 | 3.83 | 11.63 | 7.29 | 9.64 | 0.99 |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 51.17 | 2.00 | 18.67 | 3.00 | 14.00 | 5.00 | 10.00 | 1.50 |

## Soft-penalty per-type breakdown
_Average per-type contribution to the aggregate ``gate`` penalty.  When one column dominates a setup's filtered row, that gate is the bottleneck — investigate its trigger conditions before tuning the overall threshold.  Sums to the aggregate ``gate`` penalty shown in the 'Confidence component breakdown' table above (modulo rounding).  VWAP = VWAP overextension; KZ = kill zone / session filter; OI = open-interest flip; SPOOF = order-book spoofing; VOL_DIV = volume-CVD divergence; CLUSTER = symbol cluster suppression._
| Setup | Decision | Samples | Avg final | VWAP | KZ | OI | Spoof | Vol_Div | Cluster | Sum |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTINUATION_LIQUIDITY_SWEEP | filtered | 29 | 68.61 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| CONTINUATION_LIQUIDITY_SWEEP | kept | 2 | 62.15 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |
| DIVERGENCE_CONTINUATION | filtered | 718 | 44.76 | 0.00 | 6.00 | 0.00 | 0.00 | 0.00 | 0.00 | **6.00** |
| DIVERGENCE_CONTINUATION | kept | 211 | 51.52 | 0.00 | 0.03 | 0.00 | 0.00 | 0.00 | 0.00 | **0.03** |
| FAILED_AUCTION_RECLAIM | filtered | 21004 | 55.01 | 0.00 | 4.91 | 0.00 | 0.00 | 0.00 | 0.00 | **4.91** |
| FAILED_AUCTION_RECLAIM | kept | 8646 | 59.25 | 0.00 | 4.75 | 0.27 | 0.00 | 0.00 | 0.00 | **5.02** |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 945 | 49.42 | 0.00 | 13.16 | 0.50 | 0.00 | 0.00 | 0.00 | **13.66** |
| LIQUIDITY_SWEEP_REVERSAL | kept | 281 | 58.32 | 0.00 | 8.24 | 0.04 | 0.00 | 0.00 | 0.00 | **8.28** |
| QUIET_COMPRESSION_BREAK | filtered | 31 | 46.29 | 1.74 | 16.26 | 1.39 | 0.00 | 0.84 | 0.00 | **20.23** |
| SR_FLIP_RETEST | filtered | 6367 | 50.48 | 0.02 | 6.28 | 0.02 | 0.00 | 0.34 | 0.00 | **6.66** |
| SR_FLIP_RETEST | kept | 7112 | 54.58 | 0.07 | 5.88 | 0.00 | 0.00 | 0.00 | 0.00 | **5.95** |
| VOLUME_SURGE_BREAKOUT | kept | 3 | 51.17 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | **0.00** |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=3 (60.0%) | PREMATURE=0 (0.0%) | NEUTRAL=2 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 3 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 3 | 0 | 2 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 2 | 0 | 2 | 0 |
| SR_FLIP_RETEST | 1 | 0 | 0 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `7954326`
- `Path funnel` emissions: `267`
- `Regime distribution` emissions: `267`
- `QUIET_SCALP_BLOCK` events: `4219`
- `confidence_gate` events: `48004`
- `free_channel_post` events: `5`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **5**

| Source | Count |
|---|---:|
| regime_shift | 5 |

- By severity: HIGH=5

## Dependency readiness
- cvd: presence[absent=237145, present=1272787] state[empty=237145, populated=1272787] buckets[many=557489, none=237145, some=715298] sources[none] quality[none]
- funding_rate: presence[absent=13504, present=1496428] state[empty=13504, populated=1496428] buckets[few=1496428, none=13504] sources[none] quality[none]
- liquidation_clusters: presence[absent=1509932] state[empty=1509932] buckets[none=1509932] sources[none] quality[none]
- oi_snapshot: presence[absent=12998, present=1496934] state[empty=12998, populated=1496934] buckets[few=974, many=1491041, none=12998, some=4919] sources[none] quality[none]
- order_book: presence[absent=86626, present=1423306] state[populated=1423306, unavailable=86626] buckets[few=1423306, none=86626] sources[book_ticker=1423306, unavailable=86626] quality[none=86626, top_of_book_only=1423306]
- orderblocks: presence[absent=1509932] state[empty=1509932] buckets[none=1509932] sources[not_implemented=1509932] quality[none]
- recent_ticks: presence[absent=146694, present=1363238] state[empty=146694, populated=1363238] buckets[many=1363238, none=146694] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `1.409101963043213` sec
- Median create→first breach: `None` sec
- Median create→terminal: `607.0336439609528` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 0.0 | 0.0 | 0.0361 | None | 607.0336439609528 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 58189 | 96 | 24382 | 0.0 | 0.0 | None | 607.0336439609528 | 33807 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 965 | 0 | 965 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `52`
- Gating Δ: `21909`
- No-generation Δ: `-945556`
- Fast failures Δ: `0`
- Quality changes: `{}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -9, "geometry_changed_delta": 0, "geometry_preserved_delta": -6906, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 607.03, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": 0, "geometry_changed_delta": 0, "geometry_preserved_delta": -138, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **EVAL::LIQUIDATION_REVERSAL**
- Most promising healthy path: **none**
- Most likely bottleneck: **QUIET_COMPRESSION_BREAK**
- Suggested next investigation target: **EVAL::LIQUIDATION_REVERSAL**
