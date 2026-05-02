# Runtime Truth Report

## Executive summary
- Overall health/freshness: **stale**
- Top anomalies/concerns: QUIET_COMPRESSION_BREAK, EVAL::LIQUIDATION_REVERSAL, EVAL::WHALE_MOMENTUM
- Top promising signals/paths: none
- Recommended next investigation target: **QUIET_COMPRESSION_BREAK**

## Runtime health
- Engine running: `True` (status=running, health=healthy)
- Heartbeat age: `0` sec (warning=False)
- Latest performance record age: `10166` sec

## Path funnel truth
| Path/Setup | Attempts | No-signal | Generated | Scanner prep | Gated | Emitted | Classification |
|---|---:|---:|---:|---:|---:|---:|---|
| BREAKDOWN_SHORT | 0 | 0 | 1 | 1 | 1 | 0 | low-sample (none) |
| DIVERGENCE_CONTINUATION | 0 | 0 | 1421 | 1421 | 1406 | 3 | low-sample (none) |
| EVAL::BREAKDOWN_SHORT | 1769022 | 1769021 | 1 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::CONTINUATION_LIQUIDITY_SWEEP | 1769022 | 1769022 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::DIVERGENCE_CONTINUATION | 1769022 | 1767601 | 1421 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FAILED_AUCTION_RECLAIM | 1769022 | 1713163 | 55859 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::FUNDING_EXTREME | 1769022 | 1741547 | 27475 | 0 | 0 | 0 | low-sample (funding_not_extreme) |
| EVAL::LIQUIDATION_REVERSAL | 1769022 | 1769022 | 0 | 0 | 0 | 0 | non-generating (cascade_threshold_not_met) |
| EVAL::OPENING_RANGE_BREAKOUT | 1769022 | 1769022 | 0 | 0 | 0 | 0 | non-generating (feature_disabled) |
| EVAL::POST_DISPLACEMENT_CONTINUATION | 1769022 | 1769022 | 0 | 0 | 0 | 0 | non-generating (regime_blocked) |
| EVAL::QUIET_COMPRESSION_BREAK | 1769022 | 1764106 | 4916 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::SR_FLIP_RETEST | 1769022 | 1701471 | 67551 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::STANDARD | 1769022 | 1704948 | 64074 | 0 | 0 | 0 | low-sample (momentum_reject) |
| EVAL::TREND_PULLBACK | 1769022 | 1768684 | 338 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::VOLUME_SURGE_BREAKOUT | 1769022 | 1768375 | 647 | 0 | 0 | 0 | low-sample (regime_blocked) |
| EVAL::WHALE_MOMENTUM | 1769022 | 1769022 | 0 | 0 | 0 | 0 | non-generating (momentum_reject) |
| FAILED_AUCTION_RECLAIM | 0 | 0 | 55859 | 55859 | 50339 | 15 | low-sample (none) |
| FUNDING_EXTREME_SIGNAL | 0 | 0 | 27475 | 27475 | 27475 | 0 | low-sample (none) |
| LIQUIDITY_SWEEP_REVERSAL | 0 | 0 | 64074 | 64074 | 55317 | 8 | low-sample (none) |
| QUIET_COMPRESSION_BREAK | 0 | 0 | 4916 | 4916 | 1405 | 11 | active-low-quality (none) |
| SR_FLIP_RETEST | 0 | 0 | 67551 | 67551 | 36411 | 41 | low-sample (none) |
| TREND_PULLBACK_EMA | 0 | 0 | 338 | 338 | 338 | 0 | low-sample (none) |
| VOLUME_SURGE_BREAKOUT | 0 | 0 | 647 | 647 | 333 | 0 | low-sample (none) |

## Evaluator no-signal reasons
- **EVAL::BREAKDOWN_SHORT** (total=1769021): regime_blocked=673865, breakout_not_found=653807, basic_filters_failed=235929, retest_proximity_failed=201011, volume_spike_missing=4409
- **EVAL::CONTINUATION_LIQUIDITY_SWEEP** (total=1769022): regime_blocked=1534484, ema_alignment_reject=86961, basic_filters_failed=65924, sweeps_not_detected=60628, adx_reject=18012, momentum_reject=1900, reclaim_confirmation_failed=1113
- **EVAL::DIVERGENCE_CONTINUATION** (total=1767601): regime_blocked=1534484, cvd_divergence_failed=112375, basic_filters_failed=65924, ema_alignment_reject=21570, missing_cvd=21489, retest_proximity_failed=11166, missing_fvg_or_orderblock=593
- **EVAL::FAILED_AUCTION_RECLAIM** (total=1713163): regime_blocked=852958, auction_not_detected=416854, basic_filters_failed=275690, reclaim_hold_failed=100382, tail_too_small=66619, rsi_reject=660
- **EVAL::FUNDING_EXTREME** (total=1741547): funding_not_extreme=1241869, basic_filters_failed=432583, missing_funding_rate=46166, rsi_reject=20854, ema_alignment_reject=75
- **EVAL::LIQUIDATION_REVERSAL** (total=1769022): cascade_threshold_not_met=1297019, basic_filters_failed=443900, cvd_divergence_failed=27028, rsi_reject=1075
- **EVAL::OPENING_RANGE_BREAKOUT** (total=1769022): feature_disabled=1769022
- **EVAL::POST_DISPLACEMENT_CONTINUATION** (total=1769022): regime_blocked=1534484, ema_alignment_reject=86961, basic_filters_failed=65924, breakout_not_found=63641, adx_reject=18012
- **EVAL::QUIET_COMPRESSION_BREAK** (total=1764106): regime_blocked=1087496, breakout_not_detected=281720, basic_filters_failed=209766, compression_not_detected=174460, rsi_reject=4928, missing_fvg_or_orderblock=3696, macd_reject=2025, htf_direction_veto=15
- **EVAL::SR_FLIP_RETEST** (total=1701471): regime_blocked=852958, basic_filters_failed=269346, retest_out_of_zone=255087, flip_close_not_confirmed=149407, reclaim_hold_failed=123861, wick_quality_failed=20914, missing_fvg_or_orderblock=10859, insufficient_candles=9025, htf_direction_veto=5700, ema_alignment_reject=2783, rsi_reject=1531
- **EVAL::STANDARD** (total=1704948): momentum_reject=600491, adx_reject=315548, basic_filters_failed=290252, sweeps_not_detected=237528, ema_alignment_reject=189920, insufficient_candles=25601, invalid_sl_geometry=23583, macd_reject=21990, rsi_reject=35
- **EVAL::TREND_PULLBACK** (total=1768684): regime_blocked=1534484, ema_alignment_reject=86621, basic_filters_failed=65151, ema_not_tested_prev=52221, no_ema_reclaim_close=12207, body_conviction_fail=7390, prev_already_below_emas=5466, rsi_reject=3404, insufficient_candles=1583, prev_already_above_emas=142, ema21_not_tagged=14, no_prev_low_break=1
- **EVAL::VOLUME_SURGE_BREAKOUT** (total=1768375): regime_blocked=673865, breakout_not_found=451155, retest_proximity_failed=382454, basic_filters_failed=235929, volume_spike_missing=24917, missing_fvg_or_orderblock=50, ema_alignment_reject=5
- **EVAL::WHALE_MOMENTUM** (total=1769022): momentum_reject=1095157, regime_blocked=673865

## Regime distribution
| Regime | Count | % of cycles |
|---|---:|---:|
| VOLATILE | 1063466 | 48.0% |
| QUIET | 830719 | 37.5% |
| TRENDING_DOWN | 240753 | 10.9% |
| TRENDING_UP | 69457 | 3.1% |
| RANGING | 10699 | 0.5% |

## QUIET_SCALP_BLOCK gate
- Total blocks in window: **3450**
- Average confidence gap to threshold: **15.80** (samples=3450) — small gap means candidates are *close* to clearing the gate.
- Top blocked symbols: BNBUSDT=911, ENSOUSDT=411, RIVERUSDT=263, WIFUSDT=223, FILUSDT=204, DOTUSDT=200, ZEREBROUSDT=176, WLFIUSDT=138, XAUUSDT=104, XAGUSDT=103

## Confidence gate decisions
| Setup | Decision | Reason | Count |
|---|---|---|---:|
| DIVERGENCE_CONTINUATION | filtered | min_confidence | 12 |
| DIVERGENCE_CONTINUATION | kept | watchlist_tier_keep | 3 |
| FAILED_AUCTION_RECLAIM | filtered | min_confidence | 1806 |
| FAILED_AUCTION_RECLAIM | filtered | quiet_scalp_min_confidence | 205 |
| FAILED_AUCTION_RECLAIM | kept | watchlist_tier_keep | 2086 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | min_confidence | 7244 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | quiet_scalp_min_confidence | 1053 |
| LIQUIDITY_SWEEP_REVERSAL | kept | watchlist_tier_keep | 98 |
| QUIET_COMPRESSION_BREAK | filtered | min_confidence | 3125 |
| QUIET_COMPRESSION_BREAK | filtered | quiet_scalp_min_confidence | 110 |
| QUIET_COMPRESSION_BREAK | kept | watchlist_tier_keep | 207 |
| QUIET_COMPRESSION_BREAK | kept | min_confidence_pass | 89 |
| SR_FLIP_RETEST | filtered | min_confidence | 7539 |
| SR_FLIP_RETEST | filtered | quiet_scalp_min_confidence | 2082 |
| SR_FLIP_RETEST | kept | watchlist_tier_keep | 3034 |
| SR_FLIP_RETEST | kept | min_confidence_pass | 100 |
| VOLUME_SURGE_BREAKOUT | filtered | min_confidence | 314 |

## Confidence component breakdown
| Setup | Decision | Samples | Avg final | Avg threshold | Gap | Market | Execution | Risk | Thesis adj | Avg penalty |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DIVERGENCE_CONTINUATION | filtered | 12 | 46.73 | 80.00 | 33.27 | 20.80 | 19.90 | 20.00 | 0.83 | 4.80 |
| DIVERGENCE_CONTINUATION | kept | 3 | 55.23 | 50.00 | -5.23 | 20.83 | 19.93 | 18.60 | 0.00 | 0.00 |
| FAILED_AUCTION_RECLAIM | filtered | 2011 | 47.08 | 78.47 | 31.39 | 22.74 | 18.35 | 14.00 | 1.58 | 5.50 |
| FAILED_AUCTION_RECLAIM | kept | 2086 | 61.70 | 50.00 | -11.70 | 22.88 | 20.00 | 14.00 | 5.00 | 0.00 |
| LIQUIDITY_SWEEP_REVERSAL | filtered | 8297 | 64.94 | 78.10 | 13.16 | 21.17 | 19.18 | 15.20 | 3.01 | 0.02 |
| LIQUIDITY_SWEEP_REVERSAL | kept | 98 | 64.01 | 50.00 | -14.01 | 23.86 | 19.98 | 15.20 | 0.12 | 0.12 |
| QUIET_COMPRESSION_BREAK | filtered | 3235 | 68.52 | 79.49 | 10.97 | 21.34 | 18.49 | 15.80 | 0.00 | 0.32 |
| QUIET_COMPRESSION_BREAK | kept | 296 | 67.76 | 59.02 | -8.74 | 20.74 | 19.98 | 15.80 | 0.00 | 9.05 |
| SR_FLIP_RETEST | filtered | 9621 | 63.12 | 76.75 | 13.63 | 20.61 | 19.99 | 17.82 | 1.32 | 2.17 |
| SR_FLIP_RETEST | kept | 3134 | 59.43 | 50.96 | -8.47 | 20.85 | 19.95 | 15.21 | 1.07 | 7.32 |
| VOLUME_SURGE_BREAKOUT | filtered | 314 | 46.78 | 80.00 | 33.22 | 20.70 | 20.00 | 20.00 | 0.50 | 0.00 |

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
- Total log lines in window: `8471803`
- `Path funnel` emissions: `302`
- `Regime distribution` emissions: `302`
- `QUIET_SCALP_BLOCK` events: `3801`
- `confidence_gate` events: `29107`

## Dependency readiness
- cvd: presence[absent=227815, present=1541207] state[empty=227815, populated=1541207] buckets[many=543131, none=227815, some=998076] sources[none] quality[none]
- funding_rate: presence[absent=46166, present=1722856] state[empty=46166, populated=1722856] buckets[few=1722856, none=46166] sources[none] quality[none]
- liquidation_clusters: presence[absent=1769022] state[empty=1769022] buckets[none=1769022] sources[none] quality[none]
- oi_snapshot: presence[absent=39650, present=1729372] state[empty=39650, populated=1729372] buckets[many=1729372, none=39650] sources[none] quality[none]
- order_book: presence[absent=67147, present=1701875] state[populated=1701875, unavailable=67147] buckets[few=1701875, none=67147] sources[book_ticker=1701875, unavailable=67147] quality[none=67147, top_of_book_only=1701875]
- orderblocks: presence[absent=1769022] state[empty=1769022] buckets[none=1769022] sources[not_implemented=1769022] quality[none]
- recent_ticks: presence[absent=156950, present=1612072] state[empty=156950, populated=1612072] buckets[many=1612072, none=156950] sources[none] quality[none]

## Lifecycle truth summary
- Median create→dispatch: `2.5541791915893555` sec
- Median create→first breach: `None` sec
- Median create→terminal: `607.6894590854645` sec
- Median first breach→terminal: `None` sec
- Fast-failure buckets: `{"under_120s": {"count": 0, "pct": 0.0}, "under_180s": {"count": 0, "pct": 0.0}, "under_30s": {"count": 0, "pct": 0.0}, "under_60s": {"count": 0, "pct": 0.0}}`
- ~3 minute terminal-close behavior: `{"count": 0, "pct": 0.0}`

## Quality-by-path/setup summary
| Path/Setup | Emitted | Closed | Win rate | SL rate | TP rate | Avg PnL% | Median first breach (s) | Median terminal (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| QUIET_COMPRESSION_BREAK | 4 | 4 | 0.0 | 0.0 | 0.0 | -0.0992 | None | 1193.6449509859085 |
| SR_FLIP_RETEST | 1 | 1 | 0.0 | 0.0 | 0.0 | -0.0134 | None | 607.6894590854645 |

## Post-correction focus (target setups)
| Setup | Attempts | Generated | Emitted | Gated | Win rate | SL rate | Median first breach (s) | Median terminal (s) | Geometry preserved | Geometry changed | Geometry rejected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SR_FLIP_RETEST | 0 | 67551 | 41 | 36411 | 0.0 | 0.0 | None | 607.6894590854645 | 31140 | 0 | 0 |
| TREND_PULLBACK_EMA | 0 | 338 | 0 | 338 | 0.0 | 0.0 | None | None | 0 | 0 | 0 |

## Window-over-window comparison
- Path emissions Δ: `-11`
- Gating Δ: `59121`
- No-generation Δ: `-784793`
- Fast failures Δ: `0`
- Quality changes: `{"QUIET_COMPRESSION_BREAK": {"avg_pnl_delta": -0.0697, "current_avg_pnl": -0.0992, "current_win_rate": 0.0, "previous_avg_pnl": -0.0295, "previous_win_rate": 0.0, "win_rate_delta": 0.0}, "SR_FLIP_RETEST": {"avg_pnl_delta": 0.0164, "current_avg_pnl": -0.0134, "current_win_rate": 0.0, "previous_avg_pnl": -0.0298, "previous_win_rate": 0.0, "win_rate_delta": 0.0}}`
- Post-correction setup deltas: `{"SR_FLIP_RETEST": {"emitted_delta": -27, "geometry_changed_delta": 0, "geometry_preserved_delta": 9197, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.78, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}, "TREND_PULLBACK_EMA": {"emitted_delta": -1, "geometry_changed_delta": 0, "geometry_preserved_delta": -1, "geometry_rejected_delta": 0, "median_first_breach_delta_sec": 0.0, "median_terminal_delta_sec": 0.0, "sl_rate_delta": 0.0, "win_rate_delta": 0.0}}`

## Recommended operator focus
- Most suspicious degradation: **QUIET_COMPRESSION_BREAK**
- Most promising healthy path: **none**
- Most likely bottleneck: **FUNDING_EXTREME_SIGNAL**
- Suggested next investigation target: **QUIET_COMPRESSION_BREAK**
