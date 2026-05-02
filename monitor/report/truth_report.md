# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: QUIET_COMPRESSION_BREAK, EVAL::WHALE_MOMENTUM, EVAL::OPENING_RANGE_BREAKOUT
- Top promising signals/paths: none
- Recommended next investigation target: **QUIET_COMPRESSION_BREAK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `29799` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| CONTINUATION_LIQUIDITY_SWEEP | 0 | 0 | 3 | 3 | 3 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 138 | 138 | 123 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1736636 | 1736635 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1736636 | 1736633 | 3 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1736636 | 1736498 | 138 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1736636 | 1677456 | 59180 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1736636 | 1713407 | 23229 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1736636 | 1736636 | 0 | 0 | 0 | 0 | dependency-missing (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1736636 | 1736636 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1736636 | 1736636 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1736636 | 1731673 | 4963 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1736636 | 1664000 | 72636 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1736636 | 1667447 | 69189 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1736636 | 1736496 | 140 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1736636 | 1735975 | 661 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1736636 | 1736636 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 59180 | 59180 | 54780 | 10 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 23229 | 23229 | 23229 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 69189 | 69189 | 58723 | 6 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4963 | 4963 | 1456 | 6 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 72636 | 72636 | 35449 | 63 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 140 | 140 | 140 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 661 | 661 | 347 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1736635): regime_blocked=705358, breakout_not_found=610067, basic_filters_failed=235272, retest_proximity_failed=177797, volume_spike_missing=8138, ema_alignment_reject=3
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1736633): regime_blocked=1412959, ema_alignment_reject=124315, basic_filters_failed=88196, sweeps_not_detected=86567, adx_reject=21333, momentum_reject=3247, reclaim_confirmation_failed=15, rsi_reject=1
- **EVAL::DIVERGENCE_CONTINUATION** (total=1736498): regime_blocked=1412959, cvd_divergence_failed=152234, basic_filters_failed=88196, missing_cvd=34394, ema_alignment_reject=33142, retest_proximity_failed=15179, missing_fvg_or_orderblock=394
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1677456): regime_blocked=699911, auction_not_detected=491032, basic_filters_failed=295873, reclaim_hold_failed=111251, tail_too_small=78865, rsi_reject=524
- **EVAL::FUNDING_EXTREME** (total=1713407): funding_not_extreme=1213154, basic_filters_failed=427554, missing_funding_rate=50435, rsi_reject=21285, ema_alignment_reject=956, momentum_reject=20, cvd_divergence_failed=2, missing_fvg_or_orderblock=1
- **EVAL::LIQUIDATION_REVERSAL** (total=1736636): cascade_threshold_not_met=1269047, basic_filters_failed=441149, cvd_divergence_failed=25941, missing_cvd=499
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1736636): feature_disabled=1736636
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1736636): regime_blocked=1412959, ema_alignment_reject=124315, breakout_not_found=89833, basic_filters_failed=88196, adx_reject=21333
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1731673): regime_blocked=1023588, breakout_not_detected=301049, basic_filters_failed=207677, compression_not_detected=184184, rsi_reject=5904, missing_fvg_or_orderblock=4663, macd_reject=4593, htf_direction_veto=15
- **EVAL::SR_FLIP_RETEST** (total=1664000): regime_blocked=699911, retest_out_of_zone=318274, basic_filters_failed=290971, flip_close_not_confirmed=172433, reclaim_hold_failed=139590, wick_quality_failed=18509, missing_fvg_or_orderblock=11300, insufficient_candles=6784, htf_direction_veto=2998, ema_alignment_reject=1931, rsi_reject=1299
- **EVAL::STANDARD** (total=1667447): momentum_reject=586891, adx_reject=319162, basic_filters_failed=292046, sweeps_not_detected=225897, ema_alignment_reject=176630, insufficient_candles=24333, invalid_sl_geometry=21540, macd_reject=20891, rsi_reject=53, htf_ema_reject=4
- **EVAL::TREND_PULLBACK** (total=1736496): regime_blocked=1412959, ema_alignment_reject=124075, basic_filters_failed=87820, ema_not_tested_prev=84525, no_ema_reclaim_close=10936, prev_already_below_emas=7652, body_conviction_fail=5507, rsi_reject=2036, insufficient_candles=825, prev_already_above_emas=142, ema21_not_tagged=14, no_prev_low_break=2, momentum_reject=2, no_prev_high_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1735975): regime_blocked=705358, breakout_not_found=419323, retest_proximity_failed=347064, basic_filters_failed=235272, volume_spike_missing=28871, missing_fvg_or_orderblock=82, ema_alignment_reject=5
- **EVAL::WHALE_MOMENTUM** (total=1736636): momentum_reject=1031278, regime_blocked=705358

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| QUIET | 881933 | 40.1% |
| VOLATILE | 868512 | 39.5% |
| TRENDING_DOWN | 342536 | 15.6% |
| TRENDING_UP | 94075 | 4.3% |
| RANGING | 10744 | 0.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **3484**
- Average confidence gap to threshold: **16.61** (samples=3484) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=1137, ENSOUSDT=333, DOTUSDT=253, ZEREBROUSDT=253, RIVERUSDT=236, WIFUSDT=214, FILUSDT=204, WLFIUSDT=174, DOGEUSDT=94, BTCUSDT=88

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 12 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 3 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 1155 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 188 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 1595 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 9104 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1048 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 96 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 3393 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 121 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 3 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 3 |
| SR_FLIP_RETEST | filtered | min_confidence | 8749 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2127 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 6052 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 314 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 12 | 46.73 | 80.00 | 33.27 | 20.80 | 19.90 | 20.00 | 0.83 | 4.80 |
| DIVERGENCE_CONTINUATION | kept | 3 | 55.23 | 50.00 | -5.23 | 20.83 | 19.93 | 18.60 | 0.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 1343 | 48.54 | 77.90 | 29.36 | 22.65 | 18.49 | 14.00 | 1.83 | 4.89 |
| FAILED_AUCTION_RECLAIM | kept | 1595 | 61.69 | 50.00 | -11.69 | 22.88 | 20.00 | 14.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 10152 | 65.35 | 78.45 | 13.10 | 21.18 | 19.15 | 15.20 | 3.00 | 0.01 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 96 | 64.01 | 50.00 | -14.01 | 23.85 | 19.98 | 15.20 | 0.12 | 0.12 |
| QUIET_COMPRESSION_BREAK | filtered | 3514 | 68.23 | 79.48 | 11.25 | 20.90 | 18.61 | 15.80 | 0.00 | 0.31 |
| QUIET_COMPRESSION_BREAK | kept | 6 | 71.87 | 65.00 | -6.87 | 20.45 | 19.35 | 15.80 | 0.00 | 0.00 |
| SR_FLIP_RETEST | filtered | 10876 | 64.09 | 77.07 | 12.98 | 20.57 | 19.99 | 17.93 | 1.25 | 1.59 |
| SR_FLIP_RETEST | kept | 6052 | 58.43 | 50.00 | -8.43 | 21.23 | 19.98 | 15.20 | 1.01 | 7.63 |
| VOLUME_SURGE_BREAKOUT | filtered | 314 | 46.78 | 80.00 | 33.22 | 20.70 | 20.00 | 20.00 | 0.50 | 0.00 |

## Scoring engine breakdown (per-dimension contribution)
_These are the actual ``SignalScoringEngine`` dimensions whose sum reconstructs ``final`` (before the 100-cap).  Surfacing this answers the question the legacy ``components(market/execution/risk/thesis_adj)`` table couldn't: which scoring dimension is dragging a path under threshold._
| Setup | Decision | Samples | Avg final | SMC | Regime | Volume | Indicators | Patterns | MTF | Thesis adj |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FAILED_AUCTION_RECLAIM | filtered | 609 | 48.54 | 17.07 | 8.00 | 3.00 | 11.01 | 5.00 | 5.32 | 1.83 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 1120 | 65.35 | 24.99 | 8.00 | 3.04 | 12.00 | 8.26 | 6.68 | 3.00 |
| QUIET_COMPRESSION_BREAK | filtered | 8 | 68.23 | 20.00 | 18.00 | 5.25 | 14.00 | 5.94 | 5.08 | 0.00 |
| SR_FLIP_RETEST | filtered | 121 | 64.09 | 23.28 | 8.00 | 3.07 | 13.38 | 5.03 | 4.62 | 1.25 |
| SR_FLIP_RETEST | kept | 423 | 58.43 | 15.44 | 18.00 | 4.60 | 11.53 | 8.35 | 8.96 | 1.01 |

## Invalidation Quality Audit
_Each trade-monitor kill is classified after a 30-min window: **PROTECTIVE** (price moved further against position by >0.3R — kill saved money), **PREMATURE** (price would have hit TP1 — kill destroyed value), **NEUTRAL** (price stayed within ±0.3R), **INSUFFICIENT_DATA** (no usable post-kill OHLC).  This is the only honest answer to 'is invalidation net-helping or net-hurting?'_
- Totals: PROTECTIVE=2 (66.7%) | PREMATURE=0 (0.0%) | NEUTRAL=1 | INSUFFICIENT_DATA=0 | stale (awaiting classification)=0
- **Net-helping** — invalidation saved on 2 more signals than it killed prematurely.  Tightening would lose that protection.

| Kill reason | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| momentum_loss | 2 | 0 | 1 | 0 |

| Setup | PROTECTIVE | PREMATURE | NEUTRAL | INSUFFICIENT |
|---|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 2 | 0 | 1 | 0 |

## Log parse diagnostics
_If a section above is empty but the matching diagnostic count is also 0, the engine isn't emitting that log line in the window (cadence/retention) rather than the parser being broken._
- Total log lines in window: `8708453`
- `Path funnel` emissions: `297`
- `Regime distribution` emissions: `297`
- `QUIET_SCALP_BLOCK` events: `3519`
- `confidence_gate` events: `33963`
- `free_channel_post` events: `2`
- `pre_tp_fire` events: `0`

## Pre-TP grab fire stats
_Each row is a pre-TP fire — signal moved favourably by the resolved threshold within 30 min, in a non-trending regime, on a non-breakout setup.  Threshold source ``atr`` means the ATR-adaptive term won; ``atr_floored`` means ATR×0.5 was below the 0.20% fee floor (B11) so the floor was used; ``static`` means ATR was unavailable and the 0.35% fallback fired._
- _no pre-TP fires in this window (either PRE_TP_ENABLED=false on the engine, or no signals matched all gates yet)_

## Free-channel post attribution
_Counts every successful post to the free subscriber channel by source.  Verifies the Phase-5 close-storytelling, Phase-2a BTC big-move, Phase-2b regime-shift, and Phase-1 macro-alert pipelines are firing in production.  Zero counts on a freshly-shipped instrumentation rollout are the expected baseline._
- Total posts in window: **2**

| Source | Count |
|---|---:|
| regime_shift | 2 |

- By severity: HIGH=2

## Dependency readiness
- cvd: presence[absent=232908, present=1503728] state[empty=232908, populated=1503728] buckets[few=4, many=556190, none=232908, some=947534] sources[none] quality[none]
- funding_rate: presence[absent=50435, present=1686201] state[empty=50435, populated=1686201] buckets[few=1686201, none=50435] sources[none] quality[none]
- liquidation_clusters: presence[absent=1736636] state[empty=1736636] buckets[none=1736636] sources[none] quality[none]
- oi_snapshot: presence[absent=40597, present=1696039] state[empty=40597, populated=1696039] buckets[many=1696039, none=40597] sources[none] quality[none]
- order_book: presence[absent=63070, present=1673566] state[populated=1673566, unavailable=63070] buckets[few=1673566, none=63070] sources[book_ticker=1673566, unavailable=63070] quality[none=63070, top_of_book_only=1673566]
- orderblocks: presence[absent=1736636] state[empty=1736636] buckets[none=1736636] sources[not_implemented=1736636] quality[none]
- recent_ticks: presence[absent=159442, present=1577194] state[empty=159442, populated=1577194] buckets[many=1577194, none=159442] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.6369240283966064` sec
- Median create→first breach: `None` sec
- Median create→terminal: `1780.343369960785` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 3 | 3 | 0.0 | 0.0 | 0.0 | -0.1078 | None | 1780.343369960785 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 72636 | 63 | 35449 | 0.0 | 0.0 | None | None | 37187 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 140 | 0 | 140 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-17`
- Gating Δ: `29427`
- No-generation Δ: `-1112068`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.0636, "current_avg_pnl": -0.1078, "current_win_rate": 0.0, "previous_avg_pnl": -0.0442, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0265, "current_avg_pnl": null, "current_win_rate": null, "previous_avg_pnl": -0.0265, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -9, "geometry_changed_delta": 0, "geometry_preserved_delta": 8121, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": -607.57, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **QUIET_COMPRESSION_BREAK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **QUIET_COMPRESSION_BREAK**
